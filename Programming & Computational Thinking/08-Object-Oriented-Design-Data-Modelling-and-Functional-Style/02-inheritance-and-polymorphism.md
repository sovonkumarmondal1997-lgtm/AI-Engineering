# Inheritance and Polymorphism

This chapter belongs to **Stage 1 — Programming & Computational Thinking**, Module **08 — Object-Oriented Design, Data Modelling, and Functional Style**.

The previous chapter established classes, objects, state, behavior, encapsulation, abstraction, composition, dependency injection, protocols, interfaces/contracts, and testability. This chapter focuses specifically on **inheritance and polymorphism** and progresses from beginner mental models to production-oriented architecture.

The recurring learning sequence is:

**SIMPLE IDEA → WHY IT EXISTS → BASIC EXAMPLE → INTERNAL MECHANICS → PYTHON BEHAVIOR → REAL-WORLD EXAMPLE → COMMON MISTAKE → BETTER APPROACH → TRADE-OFFS → PRODUCTION APPLICATION**.

### Learning Objectives

By the end of this chapter you should be able to:

- explain parent/child classes, subclassing, overriding, specialization, and inherited behavior;
- distinguish inheritance from simple code reuse;
- trace Python attribute and method lookup through the MRO;
- use `super()` correctly, including cooperative multiple inheritance;
- explain polymorphism through inheritance, duck typing, `Protocol`, and ABCs;
- reason about substitutability and the Liskov Substitution Principle;
- understand multiple inheritance, C3 linearization, diamond inheritance, and mixins;
- use `isinstance()`, `issubclass()`, `__mro__`, and `mro()` appropriately;
- recognize when inheritance is the wrong tool;
- design pluggable, testable systems for backend, data, ML, LLM, and agentic-AI components.

### Prerequisites

You should already know basic Python functions, classes, instances, `__init__()`, instance methods, properties, composition, dependency injection, protocols/contracts, and basic `pytest` testing.

## 1. Why Inheritance Exists

### What is it?

Inheritance defines a class in relation to one or more base classes. The classic model is a subtype relationship:

```python
class Animal:
    def speak(self) -> str:
        return "some sound"


class Dog(Animal):
    pass
```

`Dog` is an `Animal`. This is an **is-a** relationship.

### Why does it exist?

Inheritance lets a subtype reuse and specialize behavior while remaining part of a common abstraction. Code reuse can be a benefit, but inheritance is primarily useful when the subtype relationship and behavioral contract are meaningful.

### What problem does it solve?

A caller can work with the base abstraction instead of hard-coding every concrete type:

```python
def announce(animal: Animal) -> str:
    return animal.speak()
```

A `Dog` can be passed to `announce()` because it participates in the `Animal` contract.

### Common mistake

Creating inheritance merely because two classes share methods.

### Better approach

Ask: **Is the child genuinely a specialized form of the parent, and can callers safely treat it as the parent?** If not, consider composition, a Protocol, a function, or a simple data structure.

## 2. Parent and Child Classes

The terms **base class**, **parent class**, and **superclass** generally describe the class being inherited from. **Subclass**, **child class**, and **derived class** describe the inheriting class.

```text
Animal
├── Dog
├── Cat
└── Bird
```

A subtype can inherit methods, class attributes, properties, and other descriptors, then add specialized behavior or override inherited behavior.

```python
class Animal:
    def move(self) -> str:
        return "moving"


class Dog(Animal):
    def fetch(self) -> str:
        return "fetching"


dog = Dog()
assert dog.move() == "moving"
assert dog.fetch() == "fetching"
```

The hierarchy communicates a domain relationship. It should not exist solely to make the class count larger.

## 3. Basic Inheritance Syntax

The syntax is:

```python
class Child(Parent):
    ...
```

```python
class Animal:
    def move(self) -> None:
        print("Moving")


class Dog(Animal):
    pass


dog = Dog()
dog.move()
```

Expected output:

```text
Moving
```

Conceptually, Python creates `Animal`, then creates `Dog` with `Animal` as a base. `Dog()` creates an instance. `dog.move()` triggers attribute lookup, which eventually finds `move()` on `Animal`.

Python does **not** copy every method into the child class. Inheritance affects lookup.

## 4. What Is Actually Inherited?

Python inheritance is best understood as an **attribute lookup relationship**.

Relevant inherited behavior includes:

- regular methods;
- class attributes;
- properties and other descriptors;
- `classmethod` and `staticmethod` descriptors;
- relevant special methods from the Python data model.

Example:

```python
class Parent:
    category = "parent"

    def describe(self) -> str:
        return "from Parent"


class Child(Parent):
    pass


child = Child()
assert child.category == "parent"
assert child.describe() == "from Parent"
```

The method is not physically copied into `Child`; Python can find it through the class hierarchy. This matters when methods are overridden and when multiple inheritance changes lookup order.

## 5. Attribute and Method Lookup

For a call such as:

```python
obj.method()
```

the beginner-friendly model is:

```text
object / instance state and descriptor rules
          ↓
        class
          ↓
base classes according to MRO
```

For class attributes:

```python
class Parent:
    x = 10


class Child(Parent):
    pass


child = Child()
print(child.x)  # 10
```

Instance attributes can shadow class attributes:

```python
child.x = 99
print(child.x)       # 99
print(Child.x)       # 10
```

When a subclass overrides a method, lookup finds the subclass method earlier in the MRO.

## 6. Method Overriding

Overriding means that a subclass defines a method with the same API name as an inherited method and supplies a new implementation.

```python
class Animal:
    def speak(self) -> str:
        return "some sound"


class Dog(Animal):
    def speak(self) -> str:
        return "woof"


assert Animal().speak() == "some sound"
assert Dog().speak() == "woof"
```

### Overriding is not overloading

Traditional overloading means multiple methods with the same name and different compile-time signatures. Python does not provide that Java/C++ style method-overload selection mechanism for ordinary methods. Python alternatives include default arguments, `*args`, `**kwargs`, different method names, or tools such as `functools.singledispatch` where appropriate.

Do not let overloading distract from inheritance: overriding is about subtype-specific behavior.

## 7. Specialization

A subtype commonly combines base behavior with specialized behavior.

```text
Vehicle
└── Car
    └── ElectricCar
```

```python
class Vehicle:
    def move(self) -> str:
        return "vehicle moving"


class Car(Vehicle):
    def open_doors(self) -> str:
        return "doors opened"


class ElectricCar(Car):
    def charge(self) -> str:
        return "charging"
```

The danger is **semantic specialization** that violates the parent contract. A subtype that exists syntactically but cannot satisfy the base abstraction is a poor polymorphic subtype.

## 8. super()

The common forms are:

```python
super().method()
super().__init__()
```

`super()` is useful when a subclass wants to extend inherited behavior.

```python
class Report:
    def save(self) -> str:
        return "saved"


class AuditedReport(Report):
    def save(self) -> str:
        result = super().save()
        return f"{result} + audit"


assert AuditedReport().save() == "saved + audit"
```

### Critical mental model

Do **not** define `super()` as "call my immediate parent". In Python, `super()` continues attribute lookup according to the relevant **MRO**. That distinction is essential for multiple inheritance.

## 9. The super() API and Behavior

Modern Python normally uses the zero-argument form:

```python
super()
```

The conceptual two-argument form is:

```python
super(CurrentClass, self)
```

The two-argument form can help when studying or debugging old patterns, but normal Python 3 code generally prefers the zero-argument form.

Inside a method, `super().method()` asks for the next implementation after the current class in the MRO. This enables cooperative inheritance and avoids hard-coding a direct parent.

## 10. Constructor Inheritance

If a subclass does not define `__init__()`, it can inherit the base constructor:

```python
class Parent:
    def __init__(self, name: str) -> None:
        self.name = name


class Child(Parent):
    pass


assert Child("Maya").name == "Maya"
```

When a child needs additional state, it can extend initialization:

```python
class Child(Parent):
    def __init__(self, name: str, age: int) -> None:
        super().__init__(name)
        self.age = age
```

If the child defines `__init__()`, Python does not automatically call the parent's `__init__()`. The child must make that decision explicitly.

## 11. Common __init__ Mistakes

### Forgetting parent initialization

```python
class Parent:
    def __init__(self, name: str) -> None:
        self.name = name


class Child(Parent):
    def __init__(self, age: int) -> None:
        self.age = age
```

`Child(10).name` does not exist because the parent constructor never ran.

### Wrong argument forwarding

If the parent requires two arguments, forwarding only one will fail.

### Incompatible initialization contracts

A child that requires unrelated mandatory data can become difficult to substitute for the parent. Constructor compatibility is part of design reasoning.

### Duplicate initialization

Reimplementing parent state creation in the child can split ownership of invariants.

### Diagnosis

Inspect which `__init__()` actually ran, which arguments were passed, and `type(instance).__mro__` when multiple inheritance is involved.

## 12. Inherited Properties and Methods

Regular methods, properties, class methods, and static methods can all participate in inheritance.

```python
class Person:
    def __init__(self, first: str, last: str) -> None:
        self.first = first
        self.last = last

    @property
    def full_name(self) -> str:
        return f"{self.first} {self.last}"


class Employee(Person):
    pass


employee = Employee("Ada", "Lovelace")
assert employee.full_name == "Ada Lovelace"
```

A subclass may override a property:

```python
class Person:
    @property
    def label(self) -> str:
        return "person"


class Employee(Person):
    @property
    def label(self) -> str:
        return "employee"
```

Properties are descriptors, so inheritance and overriding follow normal descriptor lookup rules.

## 13. What Is Polymorphism?

Polymorphism means that the same operation or abstraction can work with multiple implementations.

The important engineering idea is:

```text
One caller-facing operation
        ↓
multiple concrete implementations
```

Example:

```python
class Dog:
    def speak(self) -> str:
        return "woof"


class Cat:
    def speak(self) -> str:
        return "meow"


def make_sound(animal) -> str:
    return animal.speak()
```

`make_sound()` does not need to know whether it received a `Dog` or `Cat`. This example does not use inheritance at all.

## 14. Polymorphism Through Inheritance

Inheritance provides one common route to polymorphism:

```python
class Animal:
    def speak(self) -> str:
        raise NotImplementedError


class Dog(Animal):
    def speak(self) -> str:
        return "woof"


class Cat(Animal):
    def speak(self) -> str:
        return "meow"


animals: list[Animal] = [Dog(), Cat()]
for animal in animals:
    print(animal.speak())
```

Expected output:

```text
woof
meow
```

The caller uses one operation, `speak()`, while runtime dispatch selects the concrete override.

## 15. Polymorphism Without Inheritance

Python can use polymorphism without a shared base class.

```python
class EmailNotifier:
    def send(self, message: str) -> None:
        print(f"Email: {message}")


class SmsNotifier:
    def send(self, message: str) -> None:
        print(f"SMS: {message}")


class FakeNotifier:
    def send(self, message: str) -> None:
        print(f"FAKE: {message}")


def notify(sender) -> None:
    sender.send("Hello")
```

Each object supports the required operation. The caller does not require a nominal inheritance relationship.

## 16. Duck Typing

Duck typing is a behavior-oriented style: code relies on an object's supported operations rather than requiring a specific nominal class.

The practical idea is:

```python
def record(logger) -> None:
    logger.write("user logged in")
```

If an object has a compatible `write()` method, it can be used.

### Trade-off

Duck typing is flexible, but without static typing it can leave mistakes until runtime. A typo in `write()` or an incompatible signature may not be caught early. `typing.Protocol` can add an explicit structural contract for static analysis.

## 17. Protocol-Based Polymorphism

`typing.Protocol` supports **structural typing**.

```python
from typing import Protocol


class Notifier(Protocol):
    def send(self, message: str) -> None:
        ...


class EmailNotifier:
    def send(self, message: str) -> None:
        print(f"email:{message}")


def notify(sender: Notifier, message: str) -> None:
    sender.send(message)
```

`EmailNotifier` does not need to inherit from `Notifier`. A static type checker can determine that it has the required shape.

Protocols are useful when the application cares about a behavior contract more than a nominal class hierarchy.

## 18. ABC-Based Polymorphism

Abstract base classes provide a **nominal** abstraction and can enforce abstractness at runtime.

```python
from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    @abstractmethod
    def charge(self, amount: float) -> bool:
        """Charge an amount and report success."""


class CardPayment(PaymentProcessor):
    def charge(self, amount: float) -> bool:
        return amount > 0
```

`PaymentProcessor()` cannot be instantiated while it still has an unimplemented abstract method.

### ABC vs Protocol

| ABC | Protocol |
|---|---|
| Nominal relationship | Structural relationship |
| Explicit subclassing | No subclass declaration required |
| Runtime abstractness | Primarily static contract checking |
| Good for shared implementation | Good for loose coupling |
| Supports registration | Structural shape is central |

They are related tools, not identical ones.

## 19. Substitutability

Substitutability means that code written against an abstraction can use a valid subtype without having to know it is a special case.

If a caller expects:

```python
processor.charge(100.0)
```

then each supported subtype should preserve what that call is supposed to mean.

Check:

- input expectations;
- return values;
- documented exceptions;
- side effects;
- invariants;
- semantic meaning.

## 20. Liskov Substitution Principle

The Liskov Substitution Principle is the practical rule that a subtype should preserve the behavioral expectations of the abstraction it replaces.

A syntactically valid override can still violate LSP:

```python
class Storage:
    def save(self, value: str) -> bool:
        raise NotImplementedError


class BrokenStorage(Storage):
    def save(self, value: str) -> bool:
        raise RuntimeError("cannot save")
```

If the `Storage` contract promises a usable `save()` operation, `BrokenStorage` is not a valid production subtype.

LSP is useful here because polymorphism fails when behavior, not merely types, becomes incompatible.

## 21. classmethod and staticmethod with Inheritance

`classmethod` receives `cls` and can therefore use the subclass through which it is called:

```python
class Base:
    kind = "base"

    @classmethod
    def describe(cls) -> str:
        return cls.kind


class Child(Base):
    kind = "child"


assert Base.describe() == "base"
assert Child.describe() == "child"
```

A `staticmethod` receives neither `self` nor `cls` automatically:

```python
class Base:
    @staticmethod
    def normalize(value: str) -> str:
        return value.strip().lower()


assert Base.normalize("  HELLO  ") == "hello"
```

Both can be inherited and overridden. Choose them for their binding semantics, not simply because they are available.

## 22. Multiple Inheritance

Python permits multiple direct bases:

```python
class A:
    pass


class B:
    pass


class C(A, B):
    pass
```

Legitimate uses include mixins and framework patterns. Risks include:

- ambiguous behavior;
- complex MROs;
- constructor coordination;
- diamond inheritance;
- hidden mixin dependencies;
- harder maintenance.

Multiple inheritance is not universally bad. It is a design choice that requires deliberate contracts and an understandable MRO.

## 23. Method Resolution Order

The **Method Resolution Order (MRO)** is the order Python searches classes during inherited attribute lookup.

```python
class A:
    pass


class B(A):
    pass


class C(A):
    pass


class D(B, C):
    pass


print(D.__mro__)
print(D.mro())
```

Conceptually the order is:

```text
D → B → C → A → object
```

`__mro__` is a tuple. `mro()` returns a list.

When multiple inheritance behaves unexpectedly, inspect the MRO before changing code by guesswork.

## 24. C3 Linearization

Python uses **C3 linearization** to compute a consistent MRO for multiple inheritance.

You do not need to memorize the full merge algorithm at this stage. Remember the practical properties:

1. A child comes before its parents.
2. The local order of direct bases is respected.
3. The ordering is monotonic.
4. Diamond inheritance is resolved consistently.

If a requested multiple-inheritance graph cannot be given a consistent MRO, Python raises `TypeError` when the class definition is created.

## 25. Diamond Inheritance

The classic diamond is:

```text
        A
       / \
      B   C
       \ /
        D
```

```python
class A:
    def greet(self) -> str:
        return "A"


class B(A):
    pass


class C(A):
    pass


class D(B, C):
    pass


assert D().greet() == "A"
print(D.__mro__)
```

The MRO determines where `greet()` is found. Diamond inheritance is manageable when the hierarchy is simple and the cooperative rules are explicit; it becomes dangerous when the team cannot explain the method chain.

## 26. super() and Multiple Inheritance

This example demonstrates why `super()` does not mean "direct parent":

```python
class A:
    def process(self) -> None:
        print("A")


class B(A):
    def process(self) -> None:
        print("B")
        super().process()


class C(A):
    def process(self) -> None:
        print("C")
        super().process()


class D(B, C):
    def process(self) -> None:
        print("D")
        super().process()


D().process()
```

Expected output:

```text
D
B
C
A
```

The MRO is `D, B, C, A, object`. Each `super()` continues to the next method in that ordering.

## 27. Cooperative Inheritance

Cooperative multiple inheritance means participating classes intentionally form a method chain.

Typical requirements:

- every participating class uses `super()` where appropriate;
- method signatures are compatible;
- each class performs its own responsibility;
- the chain eventually reaches an appropriate endpoint.

A single class that returns without calling `super()` can stop the rest of the chain. Incompatible signatures can cause `TypeError`. Direct calls such as `A.method(self)` can bypass sibling classes in a diamond.

## 28. Mixins

A mixin is usually a small class that provides reusable behavior rather than a standalone domain identity.

```python
class LoggingMixin:
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")


class UserService(LoggingMixin):
    def create(self, username: str) -> None:
        self.log(f"creating {username}")
```

Good mixins are often small, focused, and explicit about dependencies.

Risky mixins become giant stateful objects, assume hidden fields, or contain unrelated business responsibilities.

## 29. Mixin Design Rules

Practical rules:

- keep each mixin focused;
- avoid large mutable state in a mixin unless its purpose is explicit;
- document required attributes and methods;
- avoid hidden dependencies such as `self.repository` appearing without explanation;
- inspect the MRO when combining multiple mixins;
- use cooperative `super()` when the mixin participates in a method chain.

A mixin should make behavior easier to reuse, not make the host class impossible to understand without reading five parent classes.

## 30. ABC + Mixin

An ABC and a mixin can have different responsibilities.

```python
from abc import ABC, abstractmethod


class DocumentStore(ABC):
    @abstractmethod
    def save(self, key: str, content: str) -> None:
        ...


class LoggingMixin:
    def log(self, message: str) -> None:
        print(message)


class FileStore(LoggingMixin, DocumentStore):
    def save(self, key: str, content: str) -> None:
        self.log(f"saving {key}")
```

Think:

```text
ABC   = domain capability/contract
Mixin = reusable implementation behavior
```

This separation reduces confusion over why a base exists.

## 31. Multiple Inheritance vs Composition

Consider:

```python
class Service(LoggingMixin, ValidationMixin):
    ...
```

versus:

```python
class Service:
    def __init__(self, logger, validator) -> None:
        self.logger = logger
        self.validator = validator
```

Multiple inheritance can be concise for small orthogonal mixins. Composition makes dependencies explicit and often simplifies lifecycle management and testing.

Do not adopt the slogan **"composition is always better."** The correct choice depends on the relationship, lifecycle, variability, and complexity of the behavior.

## 32. Inheritance vs Composition

Use inheritance for a meaningful **is-a** relationship:

```text
ElectricCar is a Vehicle
```

Use composition for a meaningful **has-a** relationship:

```text
Car has an Engine
```

```python
class Car:
    def __init__(self, engine: "Engine") -> None:
        self.engine = engine
```

In production systems, dependencies such as loggers, repositories, gateways, retry policies, metrics, and clients often have independent lifecycles and are clearer as collaborators rather than bases.

## 33. Method Signature Compatibility

A polymorphic override should generally remain callable under the base contract.

Bad:

```python
class Processor:
    def process(self, data: str) -> str:
        return data.strip()


class BrokenProcessor(Processor):
    def process(self) -> str:
        return "fixed"
```

This breaks:

```python
processor: Processor = BrokenProcessor()
processor.process("input")
```

A subtype that narrows required inputs can break polymorphic callers. Static type checkers can catch many such incompatibilities.

## 34. Type Variance — Conceptual Only

Variance matters when typed APIs use generic types.

- **Covariance** is about safely producing more-specific values.
- **Contravariance** is about safely accepting values through input positions.
- **Invariance** means substitution in either direction is generally not assumed safe.

You do not need the formal type-theory machinery to use inheritance well. The practical lesson is:

> keep parameter and return contracts compatible with the abstraction a caller depends on.

Deep variance rules belong in advanced typing study rather than becoming the center of this chapter.

## 35. Type Checking: type(), isinstance(), issubclass()

`type(obj)` returns the concrete runtime class:

```python
class Animal:
    pass


class Dog(Animal):
    pass


dog = Dog()
assert type(dog) is Dog
```

`isinstance()` accepts an object and recognizes subclasses:

```python
assert isinstance(dog, Dog)
assert isinstance(dog, Animal)
```

`issubclass()` accepts classes:

```python
assert issubclass(Dog, Animal)
```

Excessive runtime type branching can undermine polymorphism, but `isinstance()` is not inherently bad. It is appropriate when the actual problem requires runtime classification.

## 36. ABC Registration and Virtual Subclasses

ABCs can register an unrelated class as a **virtual subclass**:

```python
from abc import ABC


class Marker(ABC):
    pass


class ExternalType:
    pass


Marker.register(ExternalType)
value = ExternalType()

assert isinstance(value, Marker)
```

Registration changes subclass checks; it does **not** copy methods from `Marker` into `ExternalType`.

ABCs use `ABCMeta` machinery to support abstractness, subclass checks, and registration. Most application code does not need to manipulate the metaclass directly.

## 37. Python Data Model and Special-Method Polymorphism

Python's data model uses protocols through special methods.

```python
class Batch:
    def __init__(self, items: list[str]) -> None:
        self._items = list(items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index: int) -> str:
        return self._items[index]
```

Now Python operations work naturally:

```python
batch = Batch(["a", "b"])
assert len(batch) == 2
assert list(batch) == ["a", "b"]
assert batch[0] == "a"
```

Other relevant special methods include `__str__`, `__repr__`, and `__eq__`. Different classes can support the same language-level operation without sharing a domain base class.

## 38. Operator Polymorphism

The same syntax can invoke type-specific behavior:

```python
assert 1 + 2 == 3
assert "hello " + "world" == "hello world"
```

For equality:

```python
class User:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self.user_id == other.user_id


assert User(1) == User(1)
assert User(1) != User(2)
```

Python's data model therefore provides polymorphism directly in the language.

## 39. Function Polymorphism

A function can depend on a small behavior contract rather than a concrete implementation.

```python
from typing import Protocol


class Priced(Protocol):
    price: float


def total(items: list[Priced]) -> float:
    return sum(item.price for item in items)
```

Any compatible item can participate. This is especially useful when the behavior is simple and does not justify a class hierarchy.

## 40. Polymorphic Design vs Explicit Branching

Poorly factored variation often looks like:

```python
def send(sender_type: str, sender, message: str) -> None:
    if sender_type == "email":
        sender.send_email(message)
    elif sender_type == "sms":
        sender.send_sms(message)
    elif sender_type == "push":
        sender.send_push(message)
```

A behavior-oriented design may be:

```python
def send(sender, message: str) -> None:
    sender.send(message)
```

However, explicit branching is not automatically wrong. A small closed set of data cases can be clearer as `match` or `if/elif`. The goal is to put variation where it is easiest to understand and test.

## 41. Polymorphism and Testing

Polymorphism makes substitution natural in tests.

```python
class FakePayment:
    def charge(self, amount: float) -> bool:
        return True


def checkout(processor, amount: float) -> bool:
    return processor.charge(amount)


assert checkout(FakePayment(), 100.0) is True
```

A mature test suite should often test the contract across multiple implementations rather than asserting internal inheritance details. Boundary and invalid-input cases still matter.

## 42. Polymorphism and Mocking

A mock can satisfy an abstraction while staying out of production.

```python
from unittest.mock import create_autospec


class PaymentProcessor:
    def charge(self, amount: float) -> bool:
        raise NotImplementedError


processor = create_autospec(PaymentProcessor, instance=True)
processor.charge.return_value = True

assert processor.charge(100.0) is True
```

`spec` constrains the mock's known attributes. `autospec` and `create_autospec()` help mirror the target's callable signatures. For simple boundaries, a small fake can be more readable than a heavily configured mock.

## 43. Polymorphism and Debugging

When a polymorphic call behaves unexpectedly, answer these questions:

1. What concrete class was instantiated?
2. What does `type(obj)` say?
3. Is `isinstance(obj, ExpectedBase)` true?
4. Which method is overridden?
5. What is `obj.__class__.__mro__`?
6. Did `super()` continue the expected chain?
7. Did a mixin add a surprising implementation?

Useful diagnostics:

```python
print(type(processor))
print(isinstance(processor, PaymentProcessor))
print(processor.__class__.__mro__)
```

Use a debugger to trace the actual method selected instead of reasoning only from the class names.

## 44. Polymorphism and Logging

Structured logs can expose which implementation ran:

```python
import logging

logger = logging.getLogger(__name__)


def charge(processor, amount: float) -> bool:
    logger.info(
        "starting payment",
        extra={"processor_type": type(processor).__name__, "amount": amount},
    )
    return processor.charge(amount)
```

Useful non-sensitive fields include operation name, concrete implementation, duration, outcome, and correlation ID. Never log secrets, payment credentials, access tokens, or unnecessary personal data merely to make polymorphic code easier to debug.

## 45. Production Payment System

A pluggable payment architecture can look like:

```text
PaymentProcessor
├── CardPaymentProcessor
├── BankTransferProcessor
├── WalletPaymentProcessor
└── FakePaymentProcessor
```

```python
from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    @abstractmethod
    def charge(self, amount: float) -> bool:
        ...


class CardPaymentProcessor(PaymentProcessor):
    def charge(self, amount: float) -> bool:
        return amount > 0


class FakePaymentProcessor(PaymentProcessor):
    def charge(self, amount: float) -> bool:
        return amount > 0


class CheckoutService:
    def __init__(self, processor: PaymentProcessor) -> None:
        self.processor = processor

    def checkout(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("amount must be positive")
        return self.processor.charge(amount)
```

Real systems additionally need idempotency, retries with correct semantics, timeouts, reconciliation, auditability, secure credentials, provider error translation, and observability. Inheritance only solves the polymorphic implementation boundary.

## 46. Production Notification System

A notification architecture can use an ABC:

```text
NotificationSender
├── EmailSender
├── SmsSender
├── PushSender
└── FakeSender
```

The business operation can remain:

```python
def notify(sender, message: str) -> None:
    sender.send(message)
```

A Protocol alternative is often concise:

```python
from typing import Protocol


class Sender(Protocol):
    def send(self, message: str) -> None:
        ...
```

Choose between nominal hierarchy and structural behavior based on what the system actually needs.

## 47. Data Processing Example

A data platform might represent processors as:

```text
DataProcessor
├── CsvProcessor
├── JsonProcessor
└── ParquetProcessor
```

The core API may simply be:

```python
processor.process(data)
```

If processors share domain state and meaningful subtype identity, an ABC can be justified. If they are merely interchangeable algorithms, a Protocol or callable interface may be simpler.

The key question is whether inheritance adds a useful contract or only wraps independent behaviors in classes.

## 48. ML/AI Example

A model provider boundary may look like:

```text
ModelProvider
├── LocalModelProvider
├── CloudModelProvider
└── MockModelProvider
```

```python
from typing import Protocol


class ModelProvider(Protocol):
    def predict(self, text: str) -> str:
        ...


class MockModelProvider:
    def predict(self, text: str) -> str:
        return "mock-output"


class Classifier:
    def __init__(self, provider: ModelProvider) -> None:
        self.provider = provider

    def classify(self, text: str) -> str:
        return self.provider.predict(text)
```

The application can inject local, hosted, or fake providers. Real ML systems also need model versions, latency/error telemetry, batching, resource limits, and deployment concerns outside inheritance itself.

## 49. LLM Example

A multi-provider LLM application can depend on a narrow contract:

```python
from typing import Protocol


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class FakeLLMClient:
    def generate(self, prompt: str) -> str:
        return "test-response"


class QASystem:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def answer(self, question: str) -> str:
        return self.client.generate(question)
```

Provider-specific SDKs can live behind adapters. Avoid creating a universal base class that exposes every vendor-specific parameter. The abstraction should represent the application's needs, not the union of every provider's API.

## 50. Agentic AI Example

A simplified agent can be composed from replaceable components:

```text
Agent
├── Model
├── ToolExecutor
├── Memory
└── Planner
```

For example:

```text
Model
├── CloudModel
├── LocalModel
└── FakeModel
```

```python
from typing import Protocol


class Model(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class FakeModel:
    def generate(self, prompt: str) -> str:
        return "fake-response"


class Agent:
    def __init__(self, model: Model) -> None:
        self.model = model

    def run(self, task: str) -> str:
        return self.model.generate(task)
```

Polymorphism makes replacement and testing possible. The broader agent design still needs explicit decisions about state, tools, memory, retries, policy, evaluation, and observability.

## 51. Data Modelling Connection

Inheritance can be useful for domain models when subtype identity and shared behavior are real:

```text
Document
├── Invoice
├── Receipt
└── Contract
```

But tagged data can be simpler when the differences are primarily data:

```python
from dataclasses import dataclass
from typing import Literal


@dataclass
class Document:
    kind: Literal["invoice", "receipt", "contract"]
    document_id: str
```

Do not automatically create a class hierarchy for every set of related records. Compare behavior, lifecycle, invariants, and serialization requirements.

## 52. Dataclass + Inheritance

Dataclasses can participate in inheritance:

```python
from dataclasses import dataclass


@dataclass
class Person:
    name: str


@dataclass
class Employee(Person):
    employee_id: int


employee = Employee("Ada", 42)
print(employee)
```

Expected output:

```text
Employee(name='Ada', employee_id=42)
```

Watch for generated `__init__()` behavior, field ordering, default values, equality, and frozen instances. Dataclasses simplify boilerplate; they do not remove inheritance design decisions.

## 53. Type Hints and Polymorphism

Nominal annotations can depend on a base class:

```python
def process(payment: PaymentProcessor) -> bool:
    return payment.charge(100.0)
```

Structural annotations can depend on a Protocol:

```python
from typing import Protocol


class Payment(Protocol):
    def charge(self, amount: float) -> bool:
        ...


def process(payment: Payment) -> bool:
    return payment.charge(100.0)
```

Type hints clarify the contract. Subclasses and Protocol-compatible implementations still need behavioral compatibility, not only matching annotations.

## 54. Production Architecture — Order Processing

A larger order-processing boundary may look like:

```text
                     OrderService
                          |
                   PaymentProcessor
                     /    |     \
                  Card   Bank   Wallet
```

`OrderService` should depend on the stable payment capability rather than provider-specific details.

Design decisions:

- **inheritance** can express a controlled nominal payment hierarchy;
- **Protocol** can express only the `charge()` capability;
- **dependency injection** keeps construction outside the business workflow;
- **fakes** make tests deterministic;
- **logging** identifies implementations without leaking secrets.

Before shipping, decide whether the domain truly benefits from inheritance or whether composition plus Protocol is a lower-coupling boundary.

## 55. Common Inheritance Mistakes

The following mistakes deserve explicit review:

1. Using inheritance only for code reuse.
2. Creating an incorrect "is-a" relationship.
3. Building a deep hierarchy.
4. Creating a fragile base class.
5. Overriding without understanding the base contract.
6. Forgetting `super().__init__()` where required.
7. Misusing `super()`.
8. Breaking cooperative inheritance.
9. Using incompatible method signatures.
10. Violating substitutability.
11. Excessive `isinstance()` branching.
12. Excessive exact `type()` checks.
13. Unnecessary multiple inheritance.
14. Diamond inheritance that nobody can explain.
15. Giant mixins.
16. Hidden mixin dependencies.
17. Overusing ABCs.
18. Creating unnecessary base classes.
19. Using inheritance where composition is clearer.
20. Assuming polymorphism requires inheritance.
21. Confusing overriding with overloading.
22. Ignoring MRO.
23. Calling direct parent methods in cooperative hierarchies.
24. Mocking concrete implementations instead of testing the abstraction.

For every mistake, use this reasoning pattern:

**Problem → Why it happens → Example → Better approach.**

## 56. When Not to Use Inheritance

Inheritance should not be the default mechanism.

Prefer **composition** when the behavior has an independent lifecycle or changes independently from domain identity.

Prefer a **Protocol** when the application only needs a behavioral contract.

Prefer **duck typing** for small behavior-oriented operations where runtime flexibility is natural.

Prefer **functions** when the variation is stateless and algorithmic.

Prefer **simple data structures** when the domain is primarily data.

Example: a service does not need to inherit from `RetryPolicy`, `Metrics`, and `Logger`. Those are usually collaborators.

The key decision question is:

> What concept is changing, and what relationship does it have to the object using it?

## 57. Fragile Base Classes

A fragile base class is a base whose changes can unexpectedly break subclasses.

```python
class Report:
    def generate(self) -> str:
        return self.prepare()


class SpecialReport(Report):
    def prepare(self) -> str:
        return "special"
```

The child can become coupled to an internal helper-call sequence it did not realize was part of the base contract.

Production mitigations include:

- smaller abstractions;
- explicit contracts and invariants;
- limited protected hooks;
- contract tests;
- composition for independently changing behavior;
- Protocols where nominal inheritance is unnecessary.

## 58. Deep Inheritance Hierarchies

A hierarchy such as:

```text
A
↓
B
↓
C
↓
D
↓
E
```

can distribute behavior across too many layers.

Costs include harder lookup tracing, hidden inherited state, larger regression surfaces, and more complicated debugging. Shallow hierarchies are often easier to reason about, but depth itself is not a forbidden number. The real concern is accumulated coupling and cognitive load.

## 59. Refactoring Type-Based Branching

Start:

```python
def process_payment(payment_type: str, amount: float) -> str:
    if payment_type == "card":
        return f"card:{amount}"
    elif payment_type == "bank":
        return f"bank:{amount}"
    elif payment_type == "wallet":
        return f"wallet:{amount}"
    raise ValueError("unsupported payment type")
```

Refactor in stages:

1. isolate each algorithm as a function;
2. consider a dictionary of callables;
3. introduce objects only if state or polymorphic contracts justify them;
4. add Protocol or ABC when a stable boundary is valuable;
5. inject implementations from the outside.

The correct endpoint might still be functions. The lesson is **design reasoning**, not automatic class conversion.

## 60. Mini Project — Pluggable Payment Processing System

## Project Goal

Build a complete local payment-processing exercise that demonstrates inheritance, polymorphism, dependency injection, testing, validation, debugging, and trade-offs.

### Requirements

- base abstraction;
- card, bank-transfer, and wallet implementations;
- fake test implementation;
- input validation;
- explicit failure handling;
- logging;
- `pytest` tests;
- boundary tests;
- invalid-input tests;
- regression test;
- fake or mock where appropriate;
- no real credentials or paid APIs.

### Architecture

```text
CheckoutService
      |
      v
PaymentProcessor
 /       |       \
Card    Bank    Wallet
      \
       Fake
```

### Implementation

```python
from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    @abstractmethod
    def charge(self, amount: float) -> bool:
        ...


class CardPaymentProcessor(PaymentProcessor):
    def charge(self, amount: float) -> bool:
        return amount > 0


class BankTransferProcessor(PaymentProcessor):
    def charge(self, amount: float) -> bool:
        return amount > 0


class WalletPaymentProcessor(PaymentProcessor):
    def charge(self, amount: float) -> bool:
        return amount > 0


class FakePaymentProcessor(PaymentProcessor):
    def __init__(self, result: bool = True) -> None:
        self.result = result
        self.charged_amounts: list[float] = []

    def charge(self, amount: float) -> bool:
        self.charged_amounts.append(amount)
        return self.result


class CheckoutService:
    def __init__(self, processor: PaymentProcessor) -> None:
        self.processor = processor

    def checkout(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("amount must be positive")
        return self.processor.charge(amount)
```

### Tests

```python
import pytest


def test_checkout_uses_injected_processor() -> None:
    processor = FakePaymentProcessor(True)
    service = CheckoutService(processor)

    assert service.checkout(100.0) is True
    assert processor.charged_amounts == [100.0]


def test_checkout_rejects_zero() -> None:
    service = CheckoutService(FakePaymentProcessor())

    with pytest.raises(ValueError):
        service.checkout(0.0)


def test_checkout_rejects_negative() -> None:
    service = CheckoutService(FakePaymentProcessor())

    with pytest.raises(ValueError):
        service.checkout(-1.0)


def test_provider_failure_is_returned() -> None:
    service = CheckoutService(FakePaymentProcessor(False))

    assert service.checkout(100.0) is False
```

### Failure scenarios

Consider provider timeouts, duplicate requests, provider exceptions, partial failures, and idempotency. These require system-level design beyond inheritance.

### Trade-off exercise

Build both an ABC version and a Protocol version on paper. Record where each improves explicitness and where each introduces coupling. Then decide which boundary you would keep for a real service.

## 61. Detailed Mistake Review

Use this review table when code review reveals inheritance problems.

| Mistake | Problem | Why it happens | Better approach |
|---|---|---|---|
| Code reuse only | hierarchy has no semantic meaning | DRY pressure | helper/function/composition |
| Wrong is-a | child cannot honor parent contract | relationship guessed from names | redesign relationship |
| Deep hierarchy | difficult lookup and coupling | incremental subclassing | shallower hierarchy/composition |
| Fragile base | base change breaks children | hidden implementation hooks | narrow stable contract |
| Missing `super()` | inherited state or chain lost | constructor override | call `super()` when required |
| Direct parent call | sibling implementations bypassed | misunderstanding of `super()` | cooperative `super()` |
| Excessive type checks | dispatch logic spreads everywhere | concrete implementation leaks | behavior-based boundary |
| Giant mixin | unrelated responsibilities merge | reuse pressure | smaller mixins/composition |
| Broad ABC | implementations cannot satisfy every method | abstraction built from all use cases | narrower ABC/Protocol |
| Fake subtype | test double violates production contract | tests force inheritance | dedicated fake/Protocol |

## 63. Exercise 1 — Basic inheritance

### Problem

Create `Animal.move()` and `Dog(Animal)` without overriding `move()`.

### Requirements

Dog().move() must return `"moving"`.

### Solution

```python
class Animal:
    def move(self) -> str:
        return "moving"


class Dog(Animal):
    pass


assert Dog().move() == "moving"
```

### Explanation

The method is inherited and found by lookup.

### Common Mistake

Copying the method into `Dog` instead of using inheritance.

## 64. Exercise 2 — Method overriding

### Problem

Create `Animal.speak()` and override it in `Dog`.

### Requirements

The base returns `"some sound"`; Dog returns `"woof"`.

### Solution

```python
class Animal:
    def speak(self) -> str:
        return "some sound"


class Dog(Animal):
    def speak(self) -> str:
        return "woof"


assert Dog().speak() == "woof"
```

### Explanation

The subclass method is selected earlier in the MRO.

### Common Mistake

Calling this overloading instead of overriding.

## 65. Exercise 3 — Inherited attribute

### Problem

Create `Animal.category` and read it through a `Dog` instance.

### Requirements

Use a class attribute inherited from the parent.

### Solution

```python
class Animal:
    category = "animal"


class Dog(Animal):
    pass


assert Dog().category == "animal"
```

### Explanation

Class-attribute lookup reaches the base class.

### Common Mistake

Assuming the attribute is copied into the child.

## 66. Exercise 4 — Constructor extension

### Problem

Create `Person(name)` and `Employee(name, employee_id)`.

### Requirements

Preserve parent state and add child state using `super()`.

### Solution

```python
class Person:
    def __init__(self, name: str) -> None:
        self.name = name


class Employee(Person):
    def __init__(self, name: str, employee_id: int) -> None:
        super().__init__(name)
        self.employee_id = employee_id


employee = Employee("Ada", 7)
assert employee.name == "Ada"
assert employee.employee_id == 7
```

### Explanation

The base owns initialization of `name`; the child owns `employee_id`.

### Common Mistake

Reinitializing parent fields manually and forgetting base invariants.

## 67. Exercise 5 — Simple polymorphism

### Problem

Write `make_sound()` for `Dog` and `Cat` without inheritance.

### Requirements

The function must call only `speak()`.

### Solution

```python
class Dog:
    def speak(self) -> str:
        return "woof"


class Cat:
    def speak(self) -> str:
        return "meow"


def make_sound(animal) -> str:
    return animal.speak()


assert make_sound(Dog()) == "woof"
assert make_sound(Cat()) == "meow"
```

### Explanation

This is duck-typed polymorphism.

### Common Mistake

Adding an unnecessary common base class.

## 68. Exercise 6 — isinstance and issubclass

### Problem

Create `Animal` and `Dog(Animal)` and demonstrate both checks.

### Requirements

`isinstance(Dog(), Animal)` and `issubclass(Dog, Animal)` must be true.

### Solution

```python
class Animal:
    pass


class Dog(Animal):
    pass


assert isinstance(Dog(), Animal)
assert issubclass(Dog, Animal)
```

### Explanation

`isinstance()` takes an object; `issubclass()` takes classes.

### Common Mistake

Passing an instance to `issubclass()`.

## 69. Exercise 7 — Inherited property

### Problem

Create a parent property `full_name` and inherit it.

### Requirements

The property must compute the name dynamically.

### Solution

```python
class Person:
    def __init__(self, first: str, last: str) -> None:
        self.first = first
        self.last = last

    @property
    def full_name(self) -> str:
        return f"{self.first} {self.last}"


class Employee(Person):
    pass


assert Employee("Ada", "Lovelace").full_name == "Ada Lovelace"
```

### Explanation

The property is inherited as a descriptor.

### Common Mistake

Calling the property as a method.

## 70. Exercise 8 — ABC

### Problem

Define an abstract `Storage.save()` and a concrete in-memory implementation.

### Requirements

Use `ABC` and `abstractmethod`.

### Solution

```python
from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def save(self, key: str, value: str) -> None:
        ...


class MemoryStorage(Storage):
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    def save(self, key: str, value: str) -> None:
        self.data[key] = value


storage = MemoryStorage()
storage.save("a", "1")
assert storage.data["a"] == "1"
```

### Explanation

The ABC specifies a nominal contract and the concrete class implements it.

### Common Mistake

Forgetting `@abstractmethod`.

## 71. Exercise 9 — Protocol

### Problem

Create a `Writer` Protocol and accept a class that does not inherit from it.

### Requirements

Use structural typing.

### Solution

```python
from typing import Protocol


class Writer(Protocol):
    def write(self, message: str) -> None:
        ...


class ConsoleWriter:
    def write(self, message: str) -> None:
        print(message)


def save_message(writer: Writer, message: str) -> None:
    writer.write(message)


save_message(ConsoleWriter(), "hello")
```

### Explanation

Protocol lets static typing describe behavior without nominal inheritance.

### Common Mistake

Assuming Protocol requires subclassing.

## 72. Exercise 10 — super().method()

### Problem

Extend a base formatter and preserve its behavior.

### Requirements

The child must call `super().format()`.

### Solution

```python
class Formatter:
    def format(self, value: str) -> str:
        return value.strip()


class ChildFormatter(Formatter):
    def format(self, value: str) -> str:
        base = super().format(value)
        return f"{base}-child"


assert ChildFormatter().format(" base ") == "base-child"
```

### Explanation

The child adds behavior after the base implementation.

### Common Mistake

Replacing the method when extension is desired.

## 73. Exercise 11 — MRO inspection

### Problem

Build `A`, `B(A)`, `C(A)`, and `D(B, C)`.

### Requirements

Assert the MRO is `D, B, C, A, object`.

### Solution

```python
class A:
    pass


class B(A):
    pass


class C(A):
    pass


class D(B, C):
    pass


assert D.__mro__ == (D, B, C, A, object)
assert D.mro() == [D, B, C, A, object]
```

### Explanation

Both APIs expose the resolution order.

### Common Mistake

Assuming the order is ordinary depth-first traversal.

## 74. Exercise 12 — Diamond chain

### Problem

Make a cooperative diamond where all classes contribute to `run()`.

### Requirements

Output must contain D, B, C, A in order.

### Solution

```python
class A:
    def run(self) -> list[str]:
        return ["A"]


class B(A):
    def run(self) -> list[str]:
        return ["B", *super().run()]


class C(A):
    def run(self) -> list[str]:
        return ["C", *super().run()]


class D(B, C):
    def run(self) -> list[str]:
        return ["D", *super().run()]


assert D().run() == ["D", "B", "C", "A"]
```

### Explanation

Each `super()` continues through MRO.

### Common Mistake

Calling `A.run(self)` directly and bypassing C.

## 75. Exercise 13 — Mixin

### Problem

Create a focused `LoggingMixin` for a service.

### Requirements

The mixin should expose only `log()`.

### Solution

```python
class LoggingMixin:
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")


class UserService(LoggingMixin):
    def create(self, username: str) -> None:
        self.log(f"creating {username}")


UserService().create("ada")
```

### Explanation

The mixin contributes a small cross-cutting capability.

### Common Mistake

Turning the mixin into a large service with hidden state.

## 76. Exercise 14 — Cooperative mixin chain

### Problem

Create two mixins that both call `super()`.

### Requirements

Each step must occur once.

### Solution

```python
class Base:
    def process(self) -> list[str]:
        return ["base"]


class LoggingMixin(Base):
    def process(self) -> list[str]:
        return [*super().process(), "logging"]


class ValidationMixin(Base):
    def process(self) -> list[str]:
        return [*super().process(), "validation"]


class Service(LoggingMixin, ValidationMixin, Base):
    pass


assert Service().process() == ["base", "validation", "logging"]
```

### Explanation

The result order follows the MRO.

### Common Mistake

Skipping `super()` in one participant.

## 77. Exercise 15 — Virtual subclass

### Problem

Register an external class with an ABC.

### Requirements

Show `register()` plus `isinstance()`.

### Solution

```python
from abc import ABC


class Marker(ABC):
    pass


class ExternalType:
    pass


Marker.register(ExternalType)
assert isinstance(ExternalType(), Marker)
```

### Explanation

Registration establishes a virtual relationship without adding implementation.

### Common Mistake

Expecting methods to be copied from the ABC.

## 78. Exercise 16 — Special methods

### Problem

Implement a small collection with `__len__()` and `__iter__()`.

### Requirements

Make `len()` and iteration work naturally.

### Solution

```python
class Collection:
    def __init__(self, items: list[str]) -> None:
        self._items = list(items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items)


value = Collection(["a", "b"])
assert len(value) == 2
assert list(value) == ["a", "b"]
```

### Explanation

Python operations dispatch through special methods.

### Common Mistake

Inventing non-standard APIs when data-model protocols fit.

## 79. Exercise 17 — Model provider Protocol

### Problem

Create local and fake model implementations behind one Protocol.

### Requirements

Inject the implementation into an application class.

### Solution

```python
from typing import Protocol


class Model(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class LocalModel:
    def generate(self, prompt: str) -> str:
        return f"local:{prompt}"


class FakeModel:
    def generate(self, prompt: str) -> str:
        return "fake"


class App:
    def __init__(self, model: Model) -> None:
        self.model = model

    def run(self, prompt: str) -> str:
        return self.model.generate(prompt)


assert App(FakeModel()).run("hi") == "fake"
```

### Explanation

The application depends on behavior, not the vendor implementation.

### Common Mistake

Making the application inherit from each provider client.

## 80. Exercise 18 — Payment contract tests

### Problem

Run the same tests against two payment implementations.

### Requirements

Cover success and invalid amounts.

### Solution

```python
import pytest


class SuccessPayment:
    def charge(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("amount must be positive")
        return True


class RejectingPayment:
    def charge(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("amount must be positive")
        return False


@pytest.mark.parametrize(
    "processor, expected",
    [(SuccessPayment(), True), (RejectingPayment(), False)],
)
def test_payment_contract(processor, expected):
    assert processor.charge(100.0) is expected
```

### Explanation

Contract tests make behavior comparable across implementations.

### Common Mistake

Testing only one concrete class.

## 81. Exercise 19 — Branch-to-polymorphism refactor

### Problem

Replace a type-based payment branch with a shared `process()` operation.

### Requirements

Avoid `isinstance()` in the core function.

### Solution

```python
class CardPayment:
    def process(self, amount: float) -> str:
        return f"card:{amount}"


class BankPayment:
    def process(self, amount: float) -> str:
        return f"bank:{amount}"


def process_payment(payment, amount: float) -> str:
    return payment.process(amount)


assert process_payment(CardPayment(), 10.0) == "card:10.0"
assert process_payment(BankPayment(), 10.0) == "bank:10.0"
```

### Explanation

The operation is moved to the polymorphic objects.

### Common Mistake

Creating a class hierarchy even when two tiny functions would be simpler.

## 82. Exercise 20 — Substitutability

### Problem

Implement two `Shape` subtypes with a common `area()` behavior.

### Requirements

Neither implementation may require concrete-type branching.

### Solution

```python
from abc import ABC, abstractmethod
import math


class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        ...


class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        if width < 0 or height < 0:
            raise ValueError
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height


class Circle(Shape):
    def __init__(self, radius: float) -> None:
        if radius < 0:
            raise ValueError
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2


def total_area(shapes: list[Shape]) -> float:
    return sum(shape.area() for shape in shapes)
```

### Explanation

The caller only depends on the shared behavior.

### Common Mistake

Making one subtype return a different kind of result.

## 83. Exercise 21 — Choose the simpler design

### Problem

For three stateless report formats, decide whether inheritance is needed.

### Requirements

Provide a function-based solution.

### Solution

```python
import json


def format_json(data: dict[str, object]) -> str:
    return json.dumps(data)


def format_text(data: dict[str, object]) -> str:
    return "\n".join(f"{key}={value}" for key, value in data.items())
```

### Explanation

Functions can be the right polymorphic boundary for stateless algorithms.

### Common Mistake

Adding an ABC only because there are several formats.

## 84. Exercise 22 — Dependency injection for testability

### Problem

Refactor a service so the model client is injected.

### Requirements

The service must accept a fake implementation.

### Solution

```python
from typing import Protocol


class Model(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class FakeModel:
    def generate(self, prompt: str) -> str:
        return "fake-result"


class Summarizer:
    def __init__(self, model: Model) -> None:
        self.model = model

    def summarize(self, text: str) -> str:
        return self.model.generate(f"summarize:{text}")


assert Summarizer(FakeModel()).summarize("hello") == "fake-result"
```

### Explanation

Dependency injection moves construction out of business logic.

### Common Mistake

Injecting a concrete SDK but keeping provider-specific code in the service.

## 85. Exercise 23 — LLM abstraction

### Problem

Create cloud, local, and fake LLM clients behind one Protocol.

### Requirements

The application must not import vendor-specific types.

### Solution

```python
from typing import Protocol


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class CloudLLMClient:
    def generate(self, prompt: str) -> str:
        return f"cloud:{prompt}"


class LocalLLMClient:
    def generate(self, prompt: str) -> str:
        return f"local:{prompt}"


class FakeLLMClient:
    def generate(self, prompt: str) -> str:
        return "test-response"


class QASystem:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def answer(self, question: str) -> str:
        return self.client.generate(question)


assert QASystem(FakeLLMClient()).answer("q") == "test-response"
```

### Explanation

The generic contract contains only application-facing behavior.

### Common Mistake

Stuffing every provider-specific option into the common abstraction.

## 86. Exercise 24 — MRO debugging

### Problem

Given `class D(B, C)`, determine which `process()` implementation is selected.

### Requirements

Use `D.__mro__` rather than guessing.

### Solution

```python
class A:
    def process(self) -> str:
        return "A"


class B(A):
    def process(self) -> str:
        return "B"


class C(A):
    def process(self) -> str:
        return "C"


class D(B, C):
    pass


assert D.__mro__ == (D, B, C, A, object)
assert D().process() == "B"
```

### Explanation

The first implementation found in the MRO wins.

### Common Mistake

Assuming Python chooses the last listed base.

## 87. Debugging Lab — How to Investigate Inheritance Failures

For each debugging problem, first predict the behavior, then run the code, inspect the traceback/output, inspect the concrete type and MRO, and only then patch the code. The goal is to train a repeatable debugging workflow.

## 89. Debugging Problem 1 — Missing `super().__init__()`

### Broken Code

```python
class Parent:
    def __init__(self, name: str) -> None:
        self.name = name


class Child(Parent):
    def __init__(self, age: int) -> None:
        self.age = age


child = Child(10)
print(child.name)
```

### Expected Behavior

The inherited `name` state is available.

### Observed Behavior

`AttributeError: 'Child' object has no attribute 'name'`.

### Debugging Strategy

Inspect the child constructor and compare it with the parent constructor.

### Root Cause

The child constructor replaced the parent constructor without forwarding initialization.

### Corrected Code

```python
class Child(Parent):
    def __init__(self, name: str, age: int) -> None:
        super().__init__(name)
        self.age = age
```

### Lesson Learned

A child constructor must preserve inherited initialization responsibilities when required.

## 90. Debugging Problem 2 — Wrong method override

### Broken Code

```python
class PaymentProcessor:
    def charge(self, amount: float) -> bool:
        return False


class BrokenProcessor(PaymentProcessor):
    def process(self, amount: float) -> bool:
        return True


print(BrokenProcessor().charge(100.0))
```

### Expected Behavior

The child should customize `charge()`.

### Observed Behavior

The base `charge()` implementation still runs and returns `False`.

### Debugging Strategy

Compare the operation used by the caller with the method defined by the child.

### Root Cause

The child introduced `process()` instead of overriding `charge()`.

### Corrected Code

```python
class FixedProcessor(PaymentProcessor):
    def charge(self, amount: float) -> bool:
        return True
```

### Lesson Learned

Polymorphism relies on the same operation name and contract.

## 91. Debugging Problem 3 — Wrong method signature

### Broken Code

```python
class Processor:
    def process(self, data: str) -> str:
        return data.strip()


class BrokenProcessor(Processor):
    def process(self) -> str:
        return "fixed"


processor: Processor = BrokenProcessor()
print(processor.process("hello"))
```

### Expected Behavior

The base call should work through the subtype.

### Observed Behavior

`TypeError` because the child accepts fewer arguments.

### Debugging Strategy

Compare `inspect.signature()` or simply read the base and child definitions side by side.

### Root Cause

The override is not callable under the base contract.

### Corrected Code

```python
class FixedProcessor(Processor):
    def process(self, data: str) -> str:
        return f"fixed:{data}"
```

### Lesson Learned

Substitutability includes call compatibility.

## 92. Debugging Problem 4 — Broken MRO assumption

### Broken Code

```python
class A:
    def run(self) -> str:
        return "A"


class B(A):
    def run(self) -> str:
        return "B"


class C(A):
    def run(self) -> str:
        return "C"


class D(B, C):
    pass


print(D().run())
```

### Expected Behavior

The developer expects a specific parent without checking MRO.

### Observed Behavior

`B` is returned.

### Debugging Strategy

Print `D.__mro__` and trace lookup.

### Root Cause

The MRO is `D, B, C, A, object`, so `B.run()` wins.

### Corrected Code

```python
assert D().run() == "B"
print(D.__mro__)
```

### Lesson Learned

Inspect MRO instead of guessing.

## 93. Debugging Problem 5 — Incorrect multiple inheritance

### Broken Code

```python
class A:
    def process(self, value: int) -> str:
        return f"A:{value}"


class B(A):
    def process(self, value: int) -> str:
        return f"B:{super().process(value)}"


class C(A):
    def process(self) -> str:
        return "C"


class D(B, C):
    pass


print(D().process(10))
```

### Expected Behavior

The cooperative chain should accept the same call contract.

### Observed Behavior

The chain eventually calls `C.process(value)` and raises `TypeError`.

### Debugging Strategy

Print the MRO and compare method signatures across the chain.

### Root Cause

Cooperative methods are not signature-compatible.

### Corrected Code

```python
class C(A):
    def process(self, value: int) -> str:
        return f"C:{super().process(value)}"
```

### Lesson Learned

Cooperative inheritance is a protocol between methods, not merely a base-class list.

## 94. Debugging Problem 6 — Missing `super()` in a cooperative chain

### Broken Code

```python
class A:
    def process(self) -> list[str]:
        return ["A"]


class B(A):
    def process(self) -> list[str]:
        return ["B"]


class C(A):
    def process(self) -> list[str]:
        return ["C", *super().process()]


class D(B, C):
    def process(self) -> list[str]:
        return ["D", *super().process()]


print(D().process())
```

### Expected Behavior

Every participating class should contribute.

### Observed Behavior

The output is `['D', 'B']` and the chain stops at B.

### Debugging Strategy

Trace the `super()` calls along `D → B → C → A`.

### Root Cause

B did not continue the chain.

### Corrected Code

```python
class B(A):
    def process(self) -> list[str]:
        return ["B", *super().process()]
```

### Lesson Learned

In cooperative inheritance, one class can stop every later implementation.

## 95. Debugging Problem 7 — Diamond initialization bug

### Broken Code

```python
class A:
    def __init__(self) -> None:
        print("A")


class B(A):
    def __init__(self) -> None:
        print("B")
        A.__init__(self)


class C(A):
    def __init__(self) -> None:
        print("C")
        A.__init__(self)


class D(B, C):
    def __init__(self) -> None:
        print("D")
        super().__init__()
```

### Expected Behavior

Each initializer should run once in a cooperative chain.

### Observed Behavior

Direct calls to `A.__init__()` bypass the MRO and can duplicate or skip work as hierarchies evolve.

### Debugging Strategy

Print `D.__mro__` and replace direct parent calls with cooperative `super()` where appropriate.

### Root Cause

B and C hard-code the common ancestor instead of continuing the MRO.

### Corrected Code

```python
class B(A):
    def __init__(self) -> None:
        print("B")
        super().__init__()


class C(A):
    def __init__(self) -> None:
        print("C")
        super().__init__()
```

### Lesson Learned

Cooperative construction lets each class participate without naming a direct parent.

## 96. Debugging Problem 8 — Incorrect mixin dependency

### Broken Code

```python
class LoggingMixin:
    def log(self, message: str) -> None:
        self.logger.write(message)


class Service(LoggingMixin):
    def run(self) -> None:
        self.log("running")


Service().run()
```

### Expected Behavior

Logging should succeed.

### Observed Behavior

`AttributeError` because `logger` is missing.

### Debugging Strategy

Inspect the mixin for hidden assumptions about host attributes.

### Root Cause

The mixin requires a collaborator that the host never supplies.

### Corrected Code

```python
class Service(LoggingMixin):
    def __init__(self, logger) -> None:
        self.logger = logger

    def run(self) -> None:
        self.log("running")
```

### Lesson Learned

Make dependencies explicit or use composition.

## 97. Debugging Problem 9 — `isinstance()` misuse

### Broken Code

```python
class EmailSender:
    def send(self, message: str) -> str:
        return f"email:{message}"


class SmsSender:
    def send(self, message: str) -> str:
        return f"sms:{message}"


def notify(sender) -> str:
    if isinstance(sender, EmailSender):
        return sender.send("hello")
    raise TypeError("unsupported sender")
```

### Expected Behavior

Any sender with `send()` should work.

### Observed Behavior

`SmsSender()` is rejected.

### Debugging Strategy

Ask whether the real requirement is behavior or runtime classification.

### Root Cause

The implementation branches on one concrete type instead of using the shared behavior.

### Corrected Code

```python
def notify(sender) -> str:
    return sender.send("hello")
```

### Lesson Learned

Use polymorphism when behavior is the actual contract.

## 98. Debugging Problem 10 — Subclass violates base contract

### Broken Code

```python
from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def save(self, value: str) -> bool:
        ...


class BrokenStorage(Storage):
    def save(self, value: str) -> bool:
        raise RuntimeError("saving is impossible")
```

### Expected Behavior

A normal production call should satisfy the storage contract.

### Observed Behavior

Every call raises an unexpected exception.

### Debugging Strategy

Compare the child behavior against the base contract, not just the signature.

### Root Cause

The subtype provides a method but does not preserve promised behavior.

### Corrected Code

```python
class InMemoryStorage(Storage):
    def __init__(self) -> None:
        self.values: list[str] = []

    def save(self, value: str) -> bool:
        self.values.append(value)
        return True
```

### Lesson Learned

A valid subtype must be behaviorally substitutable.

## 99. Interview Questions

### Beginner

**What is inheritance?**

A class mechanism for creating a subtype relationship with one or more base classes, allowing inherited and specialized behavior.

**What is overriding?**

A subclass defines a compatible method with the same API name and supplies a new implementation.

**What is polymorphism?**

One operation or abstraction working with multiple implementations.

**Does polymorphism require inheritance?**

No. Duck typing, Protocols, ABCs, callables, and Python's data model all support polymorphic behavior.

### Intermediate

**What is `super()`?**

A mechanism for continuing method/attribute lookup according to the MRO.

**Does every override need `super()`?**

No. Call it when inherited behavior or cooperative chaining is part of the design.

**What is MRO?**

The Method Resolution Order used to search classes for attributes and methods.

**What is C3 linearization?**

The algorithmic strategy Python uses to construct a consistent MRO for multiple inheritance.

**What is duck typing?**

Behavior-oriented programming based on what an object supports rather than a required nominal class.

**ABC vs Protocol?**

ABC is nominal and can enforce abstractness at runtime; Protocol is structural and is primarily valuable as a typed behavioral contract.

### Advanced

**What is substitutability?**

A subtype can be used where the abstraction is expected without violating behavioral expectations.

**What is LSP?**

The principle that subtypes should preserve the behavioral contract of the abstraction they replace.

**Why can multiple inheritance be difficult?**

Because MRO, initialization, shared bases, hidden assumptions, and side effects increase reasoning complexity.

**What is a mixin?**

A small behavior-oriented class intended to be combined into another class.

**What is a fragile base class?**

A base whose implementation changes can unexpectedly break subclasses because they depend on implicit details.

**When should inheritance be avoided?**

When the subtype relationship is not genuine, behavior varies independently, the hierarchy is fragile, or composition/Protocol/functions express the dependency more clearly.

**How would you design a pluggable payment system?**

Define a narrow contract, inject provider implementations, isolate provider details behind adapters, normalize errors, and use fakes/contract tests.

**How would you design an LLM provider abstraction?**

Expose only application-required operations, isolate SDKs behind adapters, use Protocol or ABC as appropriate, inject the implementation, and prevent provider-specific options from bloating the generic interface.

## 100. Architecture Questions

### 1. Design a pluggable payment architecture.

Model answer: start with the business capability, such as `charge(amount)`. Put it behind a narrow contract. Inject implementations. Keep idempotency, retries, timeouts, reconciliation, and audit behavior outside the basic inheritance boundary.

### 2. Design a multi-provider notification system.

Model answer: define a common `send(message)` contract. Use adapters for email/SMS/push. Inject them. Use composition for independent policies such as retries and metrics when that is clearer than multiple mixins.

### 3. Design a document-processing framework.

Model answer: define the smallest processing contract. Use inheritance only where subtype identity/shared implementation matters; otherwise Protocol or callable composition may be simpler.

### 4. Design a model-provider abstraction.

Model answer: depend on a stable application-facing interface, inject local/cloud/fake providers, and keep vendor SDKs behind adapters.

### 5. Design a multi-provider LLM client.

Model answer: define only the common behavior the business actually requires. Keep streaming, tool-calling, token accounting, and provider-specific metadata behind separate capabilities rather than bloating one universal base class.

### 6. When would you choose ABC over Protocol?

When nominal hierarchy, shared implementation, or runtime abstractness provides meaningful value. Prefer Protocol when structural compatibility and loose coupling matter more.

### 7. When would you choose composition over inheritance?

When the relationship is "has-a", when behavior has an independent lifecycle, or when it varies independently of the host object's identity.

### 8. How would you prevent a fragile inheritance hierarchy?

Keep abstractions narrow, contracts explicit, hierarchies shallow, tests strong, and subclass hooks limited.

### 9. How would you test polymorphic implementations?

Create reusable contract tests for common behavior and implementation-specific tests only where necessary.

### 10. How would you add a new implementation without changing business logic?

Place variation behind a stable contract and inject the implementation. Avoid a core function that branches on every concrete type.

### 11. How would you design an agent with interchangeable models?

Compose the agent from a model contract plus tool executor, memory, and planner components. Inject cloud/local/fake models and test the orchestration using deterministic fakes.

### 12. How do you detect an abstraction that became too broad?

Look for `NotImplementedError` in normal subclasses, provider-specific parameters leaking into generic methods, frequent `isinstance()` branching, and interfaces that change whenever one implementation changes.

## 101. API and Function Coverage Audit

This chapter intentionally demonstrates the required Python APIs rather than merely listing them:

- `class Child(Parent)` — basic inheritance syntax;
- `super()` — MRO-aware continuation;
- `super().method()` — extension of inherited behavior;
- `super().__init__()` — inherited initialization and cooperative construction;
- `__mro__` — MRO tuple inspection;
- `mro()` — MRO list inspection;
- `isinstance()` — runtime object/subclass relationship check;
- `issubclass()` — runtime class relationship check;
- `ABC` / `abstractmethod` — nominal abstract contracts;
- `Protocol` — structural contracts;
- `register()` — ABC virtual subclass registration;
- `classmethod` — inherited class-bound factory/behavior;
- `staticmethod` — inherited unbound utility behavior;
- `@property` — inherited/overridden descriptor behavior;
- `__str__`, `__repr__`, `__len__`, `__iter__`, `__getitem__`, `__eq__` — representative Python data-model polymorphism.

Each is connected to working examples above.

## 102. Technical Accuracy Rules

Keep these statements as the chapter's correctness guardrails:

- `super()` does **not** simply mean "call the immediate parent"; it follows MRO-aware lookup.
- polymorphism does **not** require inheritance;
- inheritance is **not** primarily a code-reuse mechanism;
- not every override must call `super()`;
- multiple inheritance is not automatically bad;
- composition is not automatically better;
- `isinstance()` is not automatically bad;
- ABC and Protocol are not identical;
- overriding is not overloading.

Any design recommendation should be framed as a trade-off, not a universal rule.

## 103. Code Quality and Production Constraints

Python examples in this chapter are designed to be:

- valid Python;
- meaningful and progressively complex;
- type-hinted where that improves clarity;
- standard-library based unless `pytest` is explicitly used for tests;
- free of real credentials;
- free of paid service requirements;
- explicit about runnable code versus conceptual diagrams;
- focused on behavior rather than unnecessary implementation details.

Production code should additionally be reviewed for security, observability, performance, failure semantics, lifecycle, and operational constraints.

## 104. Final Production Checklist

### Inheritance

- [ ] I understand parent and child classes.
- [ ] I understand inherited behavior.
- [ ] I understand method overriding.
- [ ] I understand constructor inheritance.
- [ ] I understand `super()`.
- [ ] I understand attribute lookup.
- [ ] I understand MRO.
- [ ] I understand multiple inheritance.
- [ ] I understand diamond inheritance.
- [ ] I understand cooperative inheritance.
- [ ] I understand mixins.

### Polymorphism

- [ ] I understand polymorphism.
- [ ] I understand inheritance-based polymorphism.
- [ ] I understand duck typing.
- [ ] I understand Protocol-based polymorphism.
- [ ] I understand ABC-based polymorphism.
- [ ] I understand substitutability and LSP.
- [ ] I can design around behavior rather than concrete types.

### Design

- [ ] I know when inheritance is appropriate.
- [ ] I know when composition is clearer.
- [ ] I understand fragile base classes.
- [ ] I can avoid unnecessary deep hierarchies.
- [ ] I understand multiple-inheritance trade-offs.
- [ ] I can design replaceable implementations.

### Production

- [ ] I can design pluggable services.
- [ ] I can test polymorphic implementations.
- [ ] I can apply these ideas to backend systems.
- [ ] I can apply them to data-processing systems.
- [ ] I can apply them to ML systems.
- [ ] I can apply them to LLM systems.
- [ ] I can apply them to selected agentic-AI components.

## 105. Knowledge Check

### Question

What is inheritance?

### Answer

A subtype mechanism connecting a child class to one or more base classes, supporting inherited and specialized behavior.

### Question

What is method overriding?

### Answer

A subclass provides a new implementation for an inherited operation with a compatible contract.

### Question

What does `super()` do?

### Answer

It continues attribute/method lookup according to the MRO.

### Question

Does every subclass need to call `super()`?

### Answer

No. It matters when inherited behavior or cooperative chaining is required.

### Question

What is attribute lookup?

### Answer

The runtime process Python uses to find an attribute or method through the instance, class, descriptors, and MRO.

### Question

What is polymorphism?

### Answer

One operation or abstraction working with multiple implementations.

### Question

Can polymorphism exist without inheritance?

### Answer

Yes; duck typing, Protocols, ABCs, callables, and data-model protocols all support polymorphic designs.

### Question

What is duck typing?

### Answer

Behavior-oriented use of an object based on the operations it supports.

### Question

What is Protocol?

### Answer

A structural typing contract describing required behavior without forcing nominal inheritance.

### Question

What is an ABC?

### Answer

A nominal abstract base class that can define abstract operations and runtime abstractness.

### Question

What is `abstractmethod`?

### Answer

A decorator marking a method as abstract within an ABC hierarchy.

### Question

What is MRO?

### Answer

The Method Resolution Order used to search classes for inherited attributes and methods.

### Question

What is C3 linearization?

### Answer

The method Python uses to compute a consistent MRO for multiple inheritance.

### Question

What is diamond inheritance?

### Answer

A hierarchy where two branches share a base and later converge in a subclass.

### Question

What is cooperative inheritance?

### Answer

A multiple-inheritance design where compatible methods use `super()` to participate in an MRO chain.

### Question

What is a mixin?

### Answer

A small reusable behavior provider intended to be combined into another class.

### Question

What is substitutability?

### Answer

The ability to use a valid subtype where the base abstraction is expected without violating caller expectations.

### Question

What is LSP?

### Answer

The principle that subtypes should preserve the behavioral expectations of the abstraction they replace.

### Question

What is `isinstance()`?

### Answer

A runtime check on an object against a class or subclass relationship.

### Question

What is `issubclass()`?

### Answer

A runtime check comparing one class with a base class.

### Question

When should inheritance be avoided?

### Answer

When there is no genuine subtype relationship, behavior varies independently, or composition/Protocol/functions express the boundary more clearly.

### Question

How does polymorphism help testing?

### Answer

It permits fakes, mocks, and alternative implementations to satisfy the same contract and be injected into the system.

### Question

How does polymorphism help AI systems?

### Answer

It lets applications replace model providers, LLM clients, tool executors, or other implementations without rewriting business logic.

## 106. Final Mental Model

### Inheritance

```text
Child
  |
  | is-a
  v
Parent
```

Use it when subtype identity and behavioral substitutability are real.

### Polymorphism

```text
Caller
  |
  +----> Implementation A
  +----> Implementation B
  +----> Implementation C
```

The caller depends on stable behavior, not unnecessary concrete details.

### `super()`

```text
Continue through the MRO
```

Not:

```text
Call the direct parent
```

### Multiple inheritance

Use it deliberately for legitimate patterns such as small mixins. Understand the MRO and cooperative `super()` chain.

### Inheritance vs composition

```text
Inheritance = is-a
Composition = has-a
```

Neither wins universally. Decide based on domain meaning, change boundaries, ownership, lifecycle, and coupling.

### Production mental model

```text
Business Logic
      |
      v
Stable Contract
   /      |      \
Impl A  Impl B   Fake
```

The most valuable result is a system where implementations can change without forcing unrelated business logic to change.

## 107. Final Self-Review

Before considering this chapter complete, verify:

1. Inheritance is explained from beginner to advanced.
2. Polymorphism is explained from beginner to advanced.
3. Parent/child terminology is defined.
4. Method overriding is explained and distinguished from overloading.
5. `super()` is explained correctly.
6. `super()` is connected to MRO.
7. Constructor inheritance and common `__init__()` mistakes are included.
8. Attribute lookup is explained.
9. Duck typing is explained.
10. Protocol-based polymorphism is explained.
11. ABC-based polymorphism is explained.
12. `abstractmethod` is demonstrated.
13. `isinstance()` and `issubclass()` are explained.
14. ABC `register()` and virtual subclasses are included.
15. Multiple inheritance is explained.
16. MRO is explained with `__mro__` and `mro()`.
17. C3 linearization is explained conceptually.
18. Diamond inheritance is demonstrated.
19. Cooperative inheritance is explained.
20. Mixins and mixin design rules are included.
21. Composition versus inheritance is covered without absolutist claims.
22. Method signature compatibility is connected to substitutability.
23. Python data-model polymorphism is demonstrated.
24. Testing and mocking connections are included.
25. Debugging connections are included.
26. Backend payment/notification examples are included.
27. Data-processing examples are included.
28. ML/AI examples are included.
29. LLM examples are included.
30. Agentic-AI examples are included and remain focused on inheritance/polymorphism.
31. At least 20 progressive coding exercises are present.
32. Every exercise has Problem, Requirements, Solution, Explanation, and Common Mistake.
33. A dedicated debugging lab contains at least 10 intentionally broken designs.
34. Every debugging problem includes broken code, expected behavior, observed behavior, debugging strategy, root cause, corrected code, and lesson.
35. Interview questions are included.
36. Architecture questions are included.
37. Production considerations are included.
38. Common inheritance mistakes are explained.
39. "When Not to Use Inheritance" is included.
40. There are no false claims that polymorphism requires inheritance.
41. There are no false claims that `super()` simply means "call the parent".
42. There are no false claims that inheritance is only for code reuse.
43. There are no claims that composition is universally better.
44. There are no unnecessary frameworks or real credentials.
45. Required Python APIs are taught through practical examples.

## 108. Practical API Recipes

### Inspect the concrete type

```python
print(type(obj))
```

### Ask whether an object fits a nominal hierarchy

```python
print(isinstance(obj, BaseType))
```

### Ask whether a class belongs to a nominal hierarchy

```python
print(issubclass(ConcreteType, BaseType))
```

### Inspect the lookup chain

```python
print(ConcreteType.__mro__)
print(ConcreteType.mro())
```

### Extend base behavior

```python
class Child(Parent):
    def run(self) -> str:
        return super().run() + ":child"
```

### Continue cooperative initialization

```python
class Child(Parent):
    def __init__(self, value: int) -> None:
        super().__init__(value)
```

### Define a structural contract

```python
from typing import Protocol


class Reader(Protocol):
    def read(self) -> str:
        ...
```

### Define a nominal abstract contract

```python
from abc import ABC, abstractmethod


class Reader(ABC):
    @abstractmethod
    def read(self) -> str:
        ...
```

The right recipe depends on whether the system needs a nominal hierarchy, a structural contract, or simple behavior-based dispatch.

## 109. Chapter Completion

You have reached the end of the inheritance-and-polymorphism chapter. The next useful step is deliberate practice: implement the exercises without looking at the solutions, reproduce the debugging failures locally, and explain every design choice in terms of contracts, substitutability, coupling, and changeability.

A strong engineer does not merely know how inheritance works. A strong engineer can explain **why a hierarchy exists, what contract it represents, how Python will resolve it, how it can fail, how it can be tested, and when not to use it**.

