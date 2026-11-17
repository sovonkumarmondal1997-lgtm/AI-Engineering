# Classes and Objects from First Principles

> **Audience:** Stage 1 learners who know Python functions, collections, exceptions, mutability, pytest, type hints, and basic object-oriented design.
>
> **Runtime target:** Python 3.12+. Examples use the standard library; tests use `pytest`.
>
> **Purpose:** Build a precise mental model of classes and instances, then use that model to make small, testable design decisions. This is a mechanics-and-practice lesson, not a full treatment of inheritance, object construction internals, descriptors, or metaclasses.

## Learning objectives

By the end, you should be able to:

- Explain what the `class` statement creates and what calling a class does at a high level.
- Distinguish an object's identity, type, value, attributes, and methods.
- Explain `self`, bound methods, and the basic instance/class/base-class lookup path.
- Diagnose class attributes accidentally shared by instances and fix mutable-state bugs.
- Choose between instance methods, `@classmethod`, `@staticmethod`, module functions, and dataclasses.
- Protect invariants without pretending underscore conventions are security boundaries.
- Decide when equality should mean identity or value equality, and understand the consequences for hashing.
- Use introspection tools carefully and annotate classes with `ClassVar`, `Final`, `Self`, generics, and protocols at an introductory level.
- Test class behavior, invalid states, state transitions, and representations.
- Explain when a class is justified—and when a function or simple data model is clearer.

## Prerequisites and roadmap boundaries

This lesson assumes familiarity with functions and parameters, scope, exceptions, mutability and aliasing, pytest, type hints, and basic design concepts. In the Stage 1 tree, it consolidates:

- **Module 1.8 — Object-Oriented Design, Data Modelling and Functional Style:** encapsulation, composition, dataclasses, class/instance attributes, protocols, dependency boundaries, and the functional core/imperative shell distinction.
- **Module 1.9 — Advanced Production-Oriented Python Foundations:** typing, context-manager awareness, object-model vocabulary, and production habits.
- **Module 1.7 — Testing and Systematic Debugging:** small tests, fixtures, invalid-input cases, and test doubles.

The companion roadmap explicitly assigns this lesson the first-principles mechanics and basic design heuristics. It assigns detailed construction behavior (`__new__` and `__init__`) to Lesson 09; inheritance and `super()` chaining to Lesson 10; advanced `__repr__`, `__str__`, equality/hash, properties, descriptors, `__slots__`, MRO, copying/pickling, and metaclasses to later Stage 1 modules. We will preview only what is needed to build a sound mental model.

## 1. The minimum mental model

### 1.1 A class is an object; an instance is an object too

A class describes attributes and behavior that its instances can use. The `class` statement executes a class body and, in the ordinary case, creates a class object. The class itself is a value in Python: it can be assigned to a variable, passed to a function, inspected, and called.

Calling a class normally produces an instance of that class. The details of construction are covered in Lesson 09; for now, think of `Account("Mina", 100)` as asking Python to create and initialize an `Account` instance.

```python
class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"

person = Greeter()
print(type(Greeter).__name__)
print(type(person).__name__)
print(isinstance(person, Greeter))
print(person.greet("Mina"))
```

Expected output:

```text
type
Greeter
True
Hello, Mina!
```

Interpretation:

- `Greeter` is a class object. In ordinary Python, its type is `type`.
- `person` is an instance whose type is `Greeter`.
- `isinstance(person, Greeter)` asks whether the object is an instance of `Greeter` or a compatible subclass.
- `person.greet("Mina")` calls a method available through the class.

`type(obj)` reports an object's type. `isinstance(obj, SomeType)` is usually the more flexible behavioral/type-family check. Use `type(obj) is SomeType` only when exact type identity is specifically required; it excludes subclasses.

### 1.2 Identity, type, and value are different questions

Every object has an identity during its lifetime, a type, and a value or state. These concepts overlap but are not interchangeable.

```python
left = [1, 2]
right = [1, 2]
alias = left

print(left == right)       # equal values
print(left is right)       # different objects
print(left is alias)       # same object
print(type(left).__name__) # list
```

Expected output:

```text
True
False
True
list
```

- `==` asks for equality according to the type's equality behavior.
- `is` checks identity: whether both references point to the same object.
- `id(obj)` exposes an identity token during the object's lifetime. Do not treat it as a durable identifier or business key.
- `type(obj)` reports the object's type.

A custom class gets identity-based equality by default through the ordinary `object` behavior. A value type may instead define equality by its meaningful data. Make that decision deliberately.

## 2. A first useful class: `Account`

Begin with a class that owns a small amount of state and provides behavior that protects it.

```python
from math import isfinite

class Account:
    """A simple account with a non-negative, finite balance.

    This first version intentionally exposes state so the next section can
    demonstrate why public attributes can bypass invariants.
    """

    def __init__(self, owner: str, opening_balance: float = 0.0) -> None:
        if not isinstance(owner, str):
            raise TypeError("owner must be a string")
        if not owner.strip():
            raise ValueError("owner must not be empty")
        if isinstance(opening_balance, bool) or not isinstance(opening_balance, (int, float)):
            raise TypeError("opening_balance must be a finite number")
        if isinstance(opening_balance, float) and not isfinite(opening_balance):
            raise ValueError("opening_balance must be finite")
        if opening_balance < 0:
            raise ValueError("opening_balance must be non-negative")
        self.owner = owner
        self.balance = opening_balance

    def deposit(self, amount: float) -> None:
        """Add a positive, finite amount to the account."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("amount must be a finite number")
        if isinstance(amount, float) and not isfinite(amount):
            raise ValueError("amount must be finite")
        if amount <= 0:
            raise ValueError("deposit amount must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        """Withdraw a positive, finite amount if funds are available."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("amount must be a finite number")
        if isinstance(amount, float) and not isfinite(amount):
            raise ValueError("amount must be finite")
        if amount <= 0:
            raise ValueError("withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount

    def __repr__(self) -> str:
        return f"Account(owner={self.owner!r}, balance={self.balance!r})"


account = Account("Mina", 100.0)
account.deposit(25.0)
account.withdraw(10.0)
print(account)
print(account.balance)
```

Expected output:

```text
Account(owner='Mina', balance=115.0)
115.0
```

Line-by-line design notes:

1. `class Account:` creates the class object and begins its class namespace.
2. `__init__` initializes an instance after the construction machinery has obtained it. The exact `__new__`/`__init__` protocol belongs to Lesson 09.
3. `self` is the instance on which a method is operating. It is a conventional parameter name, not a keyword.
4. `self.owner` and `self.balance` are instance attributes. Each account normally has its own values.
5. Methods validate their inputs before changing state. This protects the invariant that the balance remains non-negative, assuming the public state is not bypassed.
6. `__repr__` gives a useful developer-facing representation. The `!r` conversion uses `repr()` on the values, which helps strings appear unambiguously quoted.

### 2.1 Deliberate mistake: public state can bypass an invariant

The preceding example exposes `balance`, so callers can write `account.balance = -900`. Its invariant is therefore only protected when callers use the methods correctly. For a small teaching example, this makes the limitation visible; a production domain model should design a smaller public surface.

A property can validate assignment, but properties and their full mechanics are covered in Module 1.11. For now, use a private-by-convention attribute and read-only property:

```python
from math import isfinite

class Account:
    """Account with read-only owner and balance properties."""

    def __init__(self, owner: str, opening_balance: float = 0.0) -> None:
        if not isinstance(owner, str):
            raise TypeError("owner must be a string")
        if not owner.strip():
            raise ValueError("owner must not be empty")
        if isinstance(opening_balance, bool) or not isinstance(opening_balance, (int, float)):
            raise TypeError("opening_balance must be a finite number")
        if isinstance(opening_balance, float) and not isfinite(opening_balance):
            raise ValueError("opening_balance must be finite")
        if opening_balance < 0:
            raise ValueError("opening_balance must be non-negative")
        self._owner = owner
        self._balance = opening_balance

    @property
    def owner(self) -> str:
        """Account owner; assignment is not part of the public API."""
        return self._owner

    @property
    def balance(self) -> float:
        """Current balance; callers cannot assign through this property."""
        return self._balance

    def deposit(self, amount: float) -> None:
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("amount must be a finite number")
        if isinstance(amount, float) and not isfinite(amount):
            raise ValueError("amount must be finite")
        if amount <= 0:
            raise ValueError("deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("amount must be a finite number")
        if isinstance(amount, float) and not isfinite(amount):
            raise ValueError("amount must be finite")
        if amount <= 0:
            raise ValueError("withdrawal amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
```

The leading underscore communicates “internal implementation detail.” It does not enforce access control: a determined caller can still reach `account._balance`. Name-mangled double-underscore names can help avoid accidental subclass name collisions, but they are not a security boundary either.

## 3. `self`, functions, and bound methods

A function defined in a class body is stored as an attribute on the class. When accessed through an instance, an ordinary function is bound to that instance. The bound method remembers both the function and the instance.

```python
class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"

greeter = Greeter()
print(greeter.greet("Ada"))
print(Greeter.greet(greeter, "Ada"))
print(greeter.greet.__self__ is greeter)
print(greeter.greet.__func__ is Greeter.greet)
```

Expected output:

```text
Hello, Ada!
Hello, Ada!
True
True
```

For an ordinary instance method, `greeter.greet("Ada")` is conceptually equivalent to `Greeter.greet(greeter, "Ada")`. The first form is idiomatic. The second is useful for understanding binding, not as a preferred everyday style.

### 3.1 Method categories

| Form | First parameter | Typical purpose | Choose it when |
|---|---|---|---|
| Instance method: `def deposit(self, ...)` | Instance | Read or update instance state | Behavior belongs to one instance |
| Class method: `@classmethod def from_record(cls, ...)` | Class | Alternative constructor or class-level behavior | The implementation should use the actual class, including subclasses |
| Static method: `@staticmethod def is_valid_code(...)` | None is injected | A related helper grouped with a class | The helper is conceptually related but needs neither instance nor class state |
| Module function: `def parse_code(...)` | None is injected | General reusable behavior | The function does not need a class namespace or state |

Prefer a module-level function when it is simply a helper. Do not make every function a `staticmethod` merely to place it near a class.

```python
from __future__ import annotations

class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @classmethod
    def from_fahrenheit(cls, fahrenheit: float) -> Temperature:
        return cls((fahrenheit - 32) * 5 / 9)

    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        return celsius * 9 / 5 + 32

    def as_fahrenheit(self) -> float:
        return self.celsius_to_fahrenheit(self.celsius)


temp = Temperature.from_fahrenheit(68)
print(round(temp.celsius, 1))
print(round(temp.as_fahrenheit(), 1))
```

Expected output:

```text
20.0
68.0
```

`cls` is a conventional name for the class argument. `return cls(...)` lets a subclass inherit the alternative constructor and receive an instance of that subclass. Do not confuse a classmethod with the class-construction protocol; the latter is the focus of Lesson 09.

## 4. Instance attributes, class attributes, and lookup

### 4.1 Instance attributes belong to one object

Attributes assigned through `self` are commonly stored in the instance namespace:

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name

first = User("Asha")
second = User("Ben")
first.name = "Asha K."
print(first.name, second.name)
print(vars(first))
```

Expected output:

```text
Asha K. Ben
{'name': 'Asha K.'}
```

### 4.2 Class attributes are looked up through the class

An attribute assigned directly in the class body is a class attribute:

```python
class Job:
    queue_name = "default"

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id

one = Job("J-1")
two = Job("J-2")
print(one.queue_name, two.queue_name)
one.queue_name = "urgent"
print(one.queue_name, two.queue_name, Job.queue_name)
```

Expected output:

```text
default default
urgent default default
```

Before `one.queue_name` is assigned, the attribute is found on the class. Assigning `one.queue_name = "urgent"` normally creates an instance attribute that shadows the class attribute. It does not change `Job.queue_name`.

### 4.3 The shared mutable class-attribute bug

This is a common source of state leakage:

```python
class BadJobQueue:
    jobs: list[str] = []  # one list shared by all instances

    def add(self, job_id: str) -> None:
        self.jobs.append(job_id)

first = BadJobQueue()
second = BadJobQueue()
first.add("J-1")
print(second.jobs)
```

Expected output (the bug):

```text
['J-1']
```

The instances both resolve `jobs` to the same class-level list. Fix it by creating a new list per instance:

```python
class JobQueue:
    def __init__(self) -> None:
        self._jobs: list[str] = []

    def add(self, job_id: str) -> None:
        if not isinstance(job_id, str):
            raise TypeError("job_id must be a string")
        if not job_id.strip():
            raise ValueError("job_id must not be empty")
        self._jobs.append(job_id)

    def pending(self) -> tuple[str, ...]:
        """Return a snapshot so callers cannot mutate the internal list."""
        return tuple(self._jobs)

    def __len__(self) -> int:
        return len(self._jobs)

    def __repr__(self) -> str:
        return f"JobQueue(pending={self.pending()!r})"


first = JobQueue()
second = JobQueue()
first.add("J-1")
print(first.pending(), second.pending(), len(first), len(second))
```

Expected output:

```text
('J-1',) () 1 0
```

Use `ClassVar` for an intentionally class-owned variable when it helps communicate the intent to type checkers. Do not use it to silence a shared-state bug.

```python
from typing import ClassVar

class ConnectionPool:
    # A conceptual class-wide setting; this is not a real connection pool.
    default_timeout_seconds: ClassVar[float] = 5.0
```

Class-level mutable state is sometimes intentional—registries and shared caches are examples—but it needs explicit ownership, lifecycle, and concurrency reasoning.

### 4.4 Simplified attribute lookup model

For ordinary attributes, a useful introductory model is:

1. Look for an attribute on the instance.
2. If it is not found there, look on its class.
3. If not found on that class, continue through base classes according to the method resolution order (MRO).

This is a **simplification**, not the full rule: descriptors such as properties can take precedence over the instance dictionary. Descriptor precedence and MRO mechanics are covered later in Module 1.11. The practical lesson here is that a method or class attribute can be inherited, shadowed, or overridden, and a property can intercept ordinary attribute access.

## 5. Namespaces and safe introspection

Introspection is useful while debugging, exploring unfamiliar code, or writing tooling. Prefer simple inspection over code that depends on private implementation details.

| Tool | What it tells you | Caution |
|---|---|---|
| `type(obj)` | The object's type | Exact-type checks can reject valid subclasses |
| `isinstance(obj, T)` | Whether an object belongs to a type family | Usually better for API boundaries than exact type identity |
| `vars(obj)` | The object's `__dict__`, when present | Raises `TypeError` for objects without an instance dictionary, including some slotted objects |
| `obj.__dict__` | Common instance namespace | Not every object has one; direct access is introspection, not a universal API |
| `Class.__dict__` | Class namespace mapping | It is a read-only mapping proxy, not an ordinary mutable dict |
| `dir(obj)` | A helpful list of names | Includes inherited and dynamic names; not a complete contract |
| `getattr(obj, name, default)` | Retrieves a named attribute, optionally with a default | Dynamic names should be validated when driven by untrusted input |
| `hasattr(obj, name)` | Tests whether attribute access succeeds | It can execute descriptors or properties and may have side effects |

```python
class Sample:
    category = "demo"

    def __init__(self, value: int) -> None:
        self.value = value

    def doubled(self) -> int:
        return self.value * 2

sample = Sample(7)
print(vars(sample))
print("category" in dir(sample))
print(getattr(sample, "value"))
print(hasattr(sample, "missing"))
print(type(Sample.__dict__).__name__)
```

Expected output:

```text
{'value': 7}
True
7
False
mappingproxy
```

Do not use `getattr` to turn arbitrary user-supplied strings into unrestricted method calls. Introspection is a tool, not an authorization system. The advanced `inspect` APIs and dynamic attribute access belong to the metaprogramming modules.

## 6. Encapsulation, invariants, and mutable state

### 6.1 Encapsulation is about maintaining a contract

Python relies largely on conventions rather than enforced `public`/`private` access modifiers:

- `name`: public API; callers may reasonably depend on it.
- `_name`: internal implementation detail; callers should not depend on it.
- `__name`: name-mangled to reduce accidental collisions in subclasses. It is not encrypted or access-controlled.

A class's **invariant** is a condition that should remain true for every valid instance. Examples include a non-negative account balance, a currency code with a fixed format, or a job queue containing only valid job identifiers. Validate at construction and at every state-changing operation that could violate the invariant.

Avoid setters that let callers bypass rules. Keep state changes behind meaningful methods such as `deposit`, `withdraw`, `enqueue`, or `mark_complete` rather than exposing arbitrary mutation.

### 6.2 Mutable defaults and aliasing

Bad:

```python
class BadLabels:
    def __init__(self, labels: list[str] = []) -> None:
        self.labels = labels
```

Every call that uses the default receives the same list. Also, if a caller passes a list, both caller and instance hold references to that same mutable object.

Safer when a mutable list is needed:

```python
class Labels:
    def __init__(self, labels: list[str] | None = None) -> None:
        self._labels = list(labels) if labels is not None else []

    def labels(self) -> tuple[str, ...]:
        return tuple(self._labels)

    def add(self, label: str) -> None:
        if not label.strip():
            raise ValueError("label must not be empty")
        self._labels.append(label)
```

`list(labels)` makes a **shallow copy**. It separates the outer list, but nested mutable objects inside it remain shared. Use a deep copy only when the data model and copying semantics justify it; deep copying can be expensive and can be incorrect for resources such as sockets, locks, or clients.

### 6.3 Public read-only views are not always enough

Returning `self._items` directly exposes internal state. Returning a tuple snapshot is often enough for a list of immutable values. If the values inside the container are themselves mutable, a tuple only protects the outer container. Choose a defensive-copy strategy that matches the nested data and performance needs.

### 6.4 Mutability, fluent methods, and immutable values

A mutating method typically returns `None` to make the side effect explicit. A method on an immutable value object can return a **new object** representing the result. Some fluent APIs return `self` after mutation, but that can obscure mutation and should be chosen deliberately.

For immutable values, `@dataclass(frozen=True)` can prevent ordinary field reassignment. It is shallow immutability: a frozen object that contains a list can still have that list mutated. Prefer immutable field values such as `tuple`, `str`, `int`, and other appropriately immutable value objects.

## 7. Equality, representation, and value objects

### 7.1 Identity equality versus value equality

Two separate objects can represent the same domain value. Decide whether they should compare equal.

- **Entity:** identity and continuity often matter. Two accounts with the same owner and balance are not necessarily the same account.
- **Value object:** its value defines its meaning. Two amounts of the same currency and amount can be equal.
- **Service:** equality is rarely meaningful; identity/default equality is often adequate.

The default equality for a normal user-defined class is identity-based. A dataclass defaults to field-based equality (`eq=True`). Do not automatically use dataclasses for entities if comparing all fields would give the wrong domain semantics.

### 7.2 `__repr__` and `__str__`

- `repr(obj)` should help a developer understand which object/value is present, ideally with an unambiguous representation.
- `str(obj)` is a more user-facing string. If you do not define `__str__`, Python generally falls back to `__repr__`.
- Start by making `__repr__` useful. Avoid including secrets, tokens, personal data, or huge payloads in logs or representations.

Full data-model rules for `__repr__`, `__str__`, equality, ordering, and hashing are assigned to Module 1.11. This lesson focuses on basic semantics and safe choices.

### 7.3 A handwritten immutable `Money` value object

For financial applications, binary `float` is often not the right representation for decimal amounts. This introductory model stores integer minor units (for example, cents) to avoid floating-point rounding in simple arithmetic.

```python
from __future__ import annotations
from types import NotImplementedType

class Money:
    """A non-negative immutable amount represented in minor units."""

    __slots__ = ("_minor_units", "_currency")

    def __init__(self, minor_units: int, currency: str) -> None:
        if isinstance(minor_units, bool) or not isinstance(minor_units, int):
            raise TypeError("minor_units must be an int")
        if minor_units < 0:
            raise ValueError("minor_units must be non-negative")
        if not isinstance(currency, str):
            raise TypeError("currency must be a string")
        if len(currency) != 3 or not currency.isalpha() or not currency.isascii():
            raise ValueError("currency must be a three-letter ASCII code")
        object.__setattr__(self, "_minor_units", minor_units)
        object.__setattr__(self, "_currency", currency.upper())

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Money instances are immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("Money instances are immutable")

    @property
    def minor_units(self) -> int:
        return self._minor_units

    @property
    def currency(self) -> str:
        return self._currency

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Money):
            return NotImplemented
        return (self.minor_units, self.currency) == (other.minor_units, other.currency)

    def __hash__(self) -> int:
        return hash((self.minor_units, self.currency))

    def __repr__(self) -> str:
        return f"Money(minor_units={self.minor_units}, currency={self.currency!r})"

    def __add__(self, other: object) -> Money | NotImplementedType:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("cannot add Money values with different currencies")
        return Money(self.minor_units + other.minor_units, self.currency)


subtotal = Money(1250, "usd")
tax = Money(100, "USD")
print(subtotal + tax)
print(subtotal == Money(1250, "USD"))
print(len({subtotal, Money(1250, "USD")}))
```

Expected output:

```text
Money(minor_units=1350, currency='USD')
True
1
```

Key decisions:

- Currency is normalized once during construction.
- Values are represented as integer minor units, not floats.
- Equality and hashing use the same immutable value components. Equal objects must have equal hashes.
- Addition returns a new value and refuses mixed currencies.
- `__slots__` is shown as an awareness example, not a memory-optimization recommendation. It prevents automatic instance `__dict__` storage for these slots but has further implications covered in Module 1.11.
- This is not a complete financial type: real systems need currency metadata, minor-unit rules, rounding policy, overflow/domain constraints, and carefully specified multiplication/division semantics.

### 7.4 Why equality and hashing must agree

If an object is used as a key in a dictionary or as an element of a set, its hash and equality behavior matter. The fundamental rule is: if `a == b`, then `hash(a) == hash(b)` must hold. The reverse is not required; hash collisions are possible.

Mutable objects that define equality by mutable fields should generally not be hashable, because changing the fields after insertion can make lookup unreliable. Python disables generated hashing for many mutable dataclass configurations for this reason. Do not write `__hash__` casually. The complete contract is covered later in Module 1.11.

### 7.5 The dataclass version

A dataclass can remove repetitive code when the class is primarily a data model:

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class MoneyRecord:
    """Simple immutable amount; validation is included for the exercise."""

    minor_units: int
    currency: str

    def __post_init__(self) -> None:
        if isinstance(self.minor_units, bool) or not isinstance(self.minor_units, int):
            raise TypeError("minor_units must be an int")
        if self.minor_units < 0:
            raise ValueError("minor_units must be non-negative")
        if not isinstance(self.currency, str):
            raise TypeError("currency must be a string")
        if len(self.currency) != 3 or not self.currency.isalpha() or not self.currency.isascii():
            raise ValueError("currency must be a three-letter ASCII code")
        object.__setattr__(self, "currency", self.currency.upper())


print(MoneyRecord(1250, "usd"))
print(MoneyRecord(1250, "usd") == MoneyRecord(1250, "USD"))
print(hash(MoneyRecord(1250, "usd")) == hash(MoneyRecord(1250, "USD")))
```

Expected output:

```text
MoneyRecord(minor_units=1250, currency='USD')
True
True
```

The dataclass generates representation, field-based equality, and—because this is frozen and equality is enabled—hashing based on its fields. `object.__setattr__` is used in `__post_init__` to normalize a frozen field during initialization. The explicit currency type check runs before string operations, so invalid runtime inputs fail with a clear `TypeError` rather than an incidental error from `len()` or `.isalpha()`. Every field used by the generated hash must itself be hashable. A dataclass does not automatically make validation or domain rules correct; those remain your responsibility.

Choose a handwritten class when its semantics need custom equality, arithmetic, representation, state transitions, or a carefully constrained public API. Choose a dataclass when generated field-oriented behavior accurately expresses the model.

## 8. State, services, and composition

### 8.1 Entity, value object, service, or function?

| Abstraction | Typical role | Example | Main design question |
|---|---|---|---|
| Entity | Mutable identity over time | `Account`, `Job` | What identifies this entity independently of its current fields? |
| Value object | Value-based meaning | `Money`, date range | Which fields define equality, and can the value be immutable? |
| Service | Orchestrates behavior using collaborators | `InvoiceService` | Which dependencies does it need, and can they be injected? |
| Stateful component | Owns a meaningful state machine or resource | `Stopwatch`, `JobQueue` | Who owns its state and lifecycle? |
| Data model | Carries structured data | `@dataclass` record | Are field-based equality and generated methods appropriate? |
| Namespace | Groups names | Module, occasionally a small namespace object | Would a module or function be simpler? |

Avoid both extremes:

- **Anemic class:** a bag of data with all domain behavior scattered in unrelated functions. This can be fine for a transport/data-transfer object, but is a poor fit if the class owns important invariants.
- **Oversized or “god” class:** one class manages parsing, persistence, business rules, logging, retries, and presentation. Split cohesive responsibilities and compose collaborators.
- **Unnecessary class:** a class with one stateless method that has no meaningful identity, configuration, or lifecycle may be better as a function.

### 8.2 Tell, don't ask

Instead of reading internal state, deciding externally what should happen, and then mutating the object, prefer asking the object to perform an operation that protects its invariant.

Less cohesive:

```text
if queue.pending_count < 100:
    queue.jobs.append(job_id)
```

Better API:

```text
queue.enqueue(job_id)
```

The queue can validate the identifier, enforce capacity, and keep its representation consistent. Do not interpret “tell, don't ask” as a ban on read-only accessors; use them when the caller genuinely needs to observe state.

### 8.3 A `Stopwatch` with injected time

A clock dependency makes time-dependent behavior deterministic in tests. `time.monotonic()` is appropriate for elapsed time because it is not intended to move backward with wall-clock adjustments.

```python
from collections.abc import Callable
from math import isfinite
from time import monotonic
from types import TracebackType
from typing import Self

class Stopwatch:
    """Measure elapsed time using an injectable monotonic clock."""

    def __init__(self, clock: Callable[[], float] = monotonic) -> None:
        self._clock = clock
        self._started_at: float | None = None
        self._elapsed = 0.0

    def start(self) -> None:
        if self._started_at is not None:
            raise RuntimeError("stopwatch is already running")
        self._started_at = self._clock()

    def stop(self) -> float:
        if self._started_at is None:
            raise RuntimeError("stopwatch is not running")
        self._elapsed += self._clock() - self._started_at
        self._started_at = None
        return self._elapsed

    def elapsed(self) -> float:
        if self._started_at is None:
            return self._elapsed
        return self._elapsed + (self._clock() - self._started_at)

    def __enter__(self) -> Self:
        """Start timing and return this stopwatch for a ``with`` block."""
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """Stop timing and never suppress an exception from the block."""
        if self._started_at is not None:
            self.stop()
        return False


class FakeClock:
    def __init__(self, now: float = 0.0) -> None:
        if isinstance(now, bool) or not isinstance(now, (int, float)):
            raise TypeError("now must be a finite number")
        if isinstance(now, float) and not isfinite(now):
            raise ValueError("now must be finite")
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
            raise TypeError("seconds must be a finite non-negative number")
        if isinstance(seconds, float) and not isfinite(seconds):
            raise ValueError("seconds must be finite")
        if seconds < 0:
            raise ValueError("seconds must be non-negative")
        self.now += seconds


clock = FakeClock()
watch = Stopwatch(clock=clock)
watch.start()
clock.advance(2.5)
print(watch.elapsed())
print(watch.stop())
```

Expected output:

```text
2.5
2.5
```

The `FakeClock` is a callable object because it implements `__call__`. The example uses it as a dependency that matches `Callable[[], float]`. In a production application, keep the injected clock monotonic and define how negative or invalid clock values should be handled. A stopwatch is stateful by design; it should not be shared between unrelated measurements.

### 8.4 Lifecycle and resource ownership

An object can own a resource, but ownership should be explicit. Files, locks, database connections, and network clients often have lifecycle requirements. Use context managers (`with`) or explicit `close()` protocols when appropriate; do not rely on garbage collection timing or `__del__` to release important resources. Detailed context-manager mechanics belong to Module 1.9, and lifecycle hooks/copying belong to Module 1.11.

## 9. Introductory type annotations for classes

Annotations document intent and support static analysis; they do not generally enforce runtime types by themselves.

### 9.1 `ClassVar` and `Final`

```python
from typing import ClassVar, Final

class BatchConfig:
    DEFAULT_BATCH_SIZE: ClassVar[int] = 500
    DEFAULT_TIMEOUT: Final[float] = 3.0

    def __init__(self, batch_size: int = DEFAULT_BATCH_SIZE) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        self.batch_size = batch_size
```

`ClassVar` marks a name as class-level for type checkers; it is not a runtime access-control mechanism. `Final` tells type checkers that reassignment is not intended. Neither keyword makes an object deeply immutable at runtime. Keep the runtime model simple: class constants are conventionally uppercase, and annotations communicate intended usage.

### 9.2 `Self`

`Self` (available from `typing` in Python 3.11+) indicates that a method returns the same concrete type as its receiver, which is useful for fluent immutable methods and subclasses.

```python
from typing import Self

class QueryOptions:
    def __init__(self, limit: int = 100) -> None:
        self.limit = limit

    def with_limit(self, limit: int) -> Self:
        if limit <= 0:
            raise ValueError("limit must be positive")
        return type(self)(limit)


options = QueryOptions().with_limit(20)
print(options.limit)
```

Expected output:

```text
20
```

This method returns a new instance rather than mutating the original. `Self` expresses the intended return type, but `type(self)(limit)` is only appropriate if subclasses support that constructor shape. Otherwise use a named factory or another design that respects subclass constructors.

### 9.3 Generics and protocols

Python 3.12 supports the modern type-parameter syntax:

```python
class Box[T]:
    """A minimal container for one value."""

    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value


number_box = Box(42)
text_box = Box("ready")
print(number_box.get(), text_box.get())
```

Expected output:

```text
42 ready
```

A generic class preserves a relationship between the input and output types. It is more useful than `Any` when the class should work for many types while keeping the type relationship intact.

A `Protocol` describes the operations an object must provide without requiring it to inherit from a particular base class:

```python
from typing import Protocol

class HasPending(Protocol):
    def pending(self) -> tuple[str, ...]: ...

def report_pending(queue: HasPending) -> str:
    return ", ".join(queue.pending())
```

Any suitable object with a compatible `pending()` method can be passed. Protocols help dependency inversion: code depends on the needed behavior, not a specific concrete implementation. Module 1.8 lesson 05 gives the broader interface-design treatment.

## 10. The object model, at a safe introductory level

Python is object-oriented at runtime in the sense that classes, functions, integers, modules, and many other values are objects.

- `object` is the root base class of ordinary new-style class hierarchies.
- `type` is the default metaclass; ordinary class objects are instances of `type`.
- An instance's type is commonly the class from which it was created.
- `isinstance` is often more robust than exact `type(...) is ...` checks.
- A class body creates a namespace that becomes the class's attribute namespace; it does not execute once per instance.

```python
class Record:
    kind = "event"

record = Record()
print(isinstance(record, object))
print(isinstance(Record, type))
print(type(record) is Record)
print(type(Record) is type)
```

Expected output:

```text
True
True
True
True
```

This is enough for this lesson. Do not infer that all attribute access is a simple dictionary lookup: descriptors, MRO rules, custom metaclasses, and dynamic class creation add complexity. Those are explicitly assigned to later modules. Construction itself is treated in Lesson 09.

## 11. Serialization and object boundaries

An in-memory object is not automatically a stable interchange format. Before persisting or sending it, decide which fields are part of the data contract and how the schema evolves.

A common explicit pattern is `to_dict()`/`from_dict()` or a dataclass converted into a schema-shaped record. Validate untrusted data at the boundary. Avoid treating Python pickle as a safe general interchange format: unpickling untrusted bytes can execute code, and pickle compatibility across code versions is not a durable schema contract. The advanced copying/pickling lesson and security module cover these risks in depth.

For example:

```python
from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class JobRecord:
    job_id: str
    priority: int

    def __post_init__(self) -> None:
        if not isinstance(self.job_id, str):
            raise TypeError("job_id must be a string")
        if not self.job_id.strip():
            raise ValueError("job_id must not be empty")
        if isinstance(self.priority, bool) or not isinstance(self.priority, int):
            raise TypeError("priority must be an int")
        if self.priority < 0:
            raise ValueError("priority must be non-negative")


job = JobRecord("J-42", 3)
print(asdict(job))
```

Expected output:

```text
{'job_id': 'J-42', 'priority': 3}
```

`asdict()` is convenient for simple dataclass models, but it is not a universal serializer. Nested types, timestamps, decimals, enums, custom objects, schema versions, and privacy rules may require explicit conversion logic.

## 12. Testing classes with pytest

Test public behavior and invariants, not private implementation details unless a focused implementation test is necessary. A good class test suite usually includes:

1. Valid construction and initial state.
2. Invalid construction and invalid method arguments.
3. State transitions and invariants after sequences of operations.
4. Isolation between instances.
5. Equality, hashing, and representation when they are part of the contract.
6. Defensive-copy behavior for mutable state.
7. Repeatability: tests should not depend on order, wall-clock timing, network services, or shared global state.

The fenced examples in this lesson are separate teaching snippets; do not concatenate every code block into one module because some snippets deliberately redefine a class to demonstrate a later design. For a runnable practice project, place the read-only `Account` from §2.1, `Money` from §7.3, `JobQueue` from §4.3, `Stopwatch`/`FakeClock` from §8.3, and the handwritten `Point` plus `PointRecord` from Solution 3 in `classes_first_principles.py`. Consolidate imports at the top of that module; any `from __future__ import annotations` must be at the very beginning of the file. Then save the following as `test_classes_first_principles.py` beside it. The test imports are explicit so the file can be run with `pytest -q`.

```python
import pytest
from classes_first_principles import (
    Account, FakeClock, JobQueue, Money, Point, PointRecord, Stopwatch,
)

# Account is the read-only-balance version from §2.1; the other classes are
# the specific implementations named above, not similarly named demo snippets.

def test_account_deposit_and_withdraw_preserve_balance() -> None:
    account = Account("Mina", 100.0)
    account.deposit(25.0)
    account.withdraw(10.0)
    assert account.balance == 115.0

@pytest.mark.parametrize("owner", ["", "   "])
def test_account_rejects_blank_owner(owner: str) -> None:
    with pytest.raises(ValueError, match="owner must not be empty"):
        Account(owner)

def test_account_rejects_invalid_deposit_without_mutation() -> None:
    account = Account("Mina", 100.0)
    with pytest.raises(ValueError, match="deposit amount must be positive"):
        account.deposit(0)
    assert account.balance == 100.0

@pytest.mark.parametrize("amount", [float("nan"), float("inf"), float("-inf")])
def test_account_rejects_non_finite_deposit_without_mutation(amount: float) -> None:
    account = Account("Mina", 100.0)
    with pytest.raises(ValueError, match="must be finite"):
        account.deposit(amount)
    assert account.balance == 100.0

def test_account_rejects_overdraft_without_mutation() -> None:
    account = Account("Mina", 100.0)
    with pytest.raises(ValueError, match="insufficient funds"):
        account.withdraw(101.0)
    assert account.balance == 100.0

@pytest.mark.parametrize("opening_balance", [float("nan"), float("inf"), float("-inf")])
def test_account_rejects_non_finite_opening_balance(opening_balance: float) -> None:
    with pytest.raises(ValueError, match="must be finite"):
        Account("Mina", opening_balance)

def test_account_owner_and_balance_are_read_only() -> None:
    account = Account("Mina", 100.0)
    with pytest.raises(AttributeError):
        setattr(account, "owner", "Other")
    with pytest.raises(AttributeError):
        setattr(account, "balance", -1.0)
    assert account.owner == "Mina"
    assert account.balance == 100.0

def test_job_queues_have_independent_state() -> None:
    first = JobQueue()
    second = JobQueue()
    first.add("J-1")
    assert first.pending() == ("J-1",)
    assert second.pending() == ()

def test_job_queue_rejects_blank_id() -> None:
    queue = JobQueue()
    with pytest.raises(ValueError, match="job_id must not be empty"):
        queue.add("  ")
    assert queue.pending() == ()

def test_money_equality_and_hashing_are_consistent() -> None:
    one = Money(1250, "usd")
    two = Money(1250, "USD")
    assert one == two
    assert hash(one) == hash(two)
    assert len({one, two}) == 1

def test_money_rejects_mixed_currency_addition() -> None:
    with pytest.raises(ValueError, match="different currencies"):
        Money(100, "USD") + Money(100, "EUR")

def test_money_is_immutable() -> None:
    money = Money(100, "USD")
    with pytest.raises(AttributeError, match="immutable"):
        money._minor_units = 200
    with pytest.raises(AttributeError, match="immutable"):
        del money._minor_units
    assert money.minor_units == 100

def test_money_rejects_bool_minor_units() -> None:
    with pytest.raises(TypeError, match="must be an int"):
        Money(True, "USD")

def test_money_rejects_non_string_currency() -> None:
    with pytest.raises(TypeError, match="currency must be a string"):
        Money(100, 123)  # type: ignore[arg-type]

def test_money_addition_returns_new_value() -> None:
    original = Money(100, "USD")
    result = original + Money(50, "USD")
    assert result == Money(150, "USD")
    assert original == Money(100, "USD")
```

These tests demonstrate expected behavior, but they need the class definitions in scope. A realistic repository would put production classes in a module and import them into the test file. Keep tests independent of private fields where public behavior can prove the same property.

### 12.1 Testing a fake-clock `Stopwatch`

```python
def test_stopwatch_measures_elapsed_time_without_sleeping() -> None:
    clock = FakeClock()
    watch = Stopwatch(clock=clock)

    watch.start()
    clock.advance(2.5)
    assert watch.elapsed() == 2.5
    assert watch.stop() == 2.5
    assert watch.elapsed() == 2.5

def test_stopwatch_rejects_double_start() -> None:
    watch = Stopwatch(clock=FakeClock())
    watch.start()
    with pytest.raises(RuntimeError, match="already running"):
        watch.start()

def test_stopwatch_rejects_stop_when_not_running() -> None:
    watch = Stopwatch(clock=FakeClock())
    with pytest.raises(RuntimeError, match="not running"):
        watch.stop()

def test_stopwatch_context_manager_stops_on_exit() -> None:
    clock = FakeClock()
    with Stopwatch(clock=clock) as watch:
        clock.advance(1.5)
        assert watch.elapsed() == 1.5
    assert watch.elapsed() == 1.5

def test_stopwatch_context_manager_does_not_suppress_exceptions() -> None:
    clock = FakeClock()
    watch = Stopwatch(clock=clock)
    with pytest.raises(RuntimeError, match="inside block"):
        with watch:
            clock.advance(2.0)
            raise RuntimeError("inside block")
    assert watch.elapsed() == 2.0

def test_handwritten_point_has_stable_value_equality_and_hash() -> None:
    first = Point(2, 3)
    second = Point(2, 3)
    assert first == second
    assert hash(first) == hash(second)
    assert len({first, second}) == 1

def test_handwritten_point_rejects_assignment_and_deletion() -> None:
    point = Point(2, 3)
    with pytest.raises(AttributeError, match="immutable"):
        setattr(point, "x", 4)
    with pytest.raises(AttributeError, match="immutable"):
        delattr(point, "_x")


def test_point_dataclass_uses_value_equality_and_hashing() -> None:
    first = PointRecord(2, 3)
    second = PointRecord(2, 3)
    assert first == second
    assert hash(first) == hash(second)
```

The fake clock avoids flaky sleeps and makes the time dependency explicit. Do not test elapsed time by asserting that a real sleep took an exact number of milliseconds.

## 13. Design trade-offs: should this be a class?

Use this decision table as a guide, not a rigid rule.

| Need | Likely simplest fit | Why |
|---|---|---|
| Transform input to output without retained state | Function | Small surface, easy to test and compose |
| Bundle related data with generated equality/representation | Dataclass | Avoids repetitive field plumbing |
| Maintain state across operations and protect invariants | Class | State and allowed transitions live together |
| Orchestrate work using a repository/client/clock | Service class or function with injected dependencies | Choose based on whether orchestration needs persistent state/configuration |
| Group a few unrelated helpers | Module | A class would imply a false stateful relationship |
| Model a domain value with custom equality/arithmetic | Handwritten value class or carefully configured dataclass | Semantics matter more than code reduction |
| One-off mutable container with no domain behavior | Built-in collection or small dataclass | Avoid unnecessary abstraction |

### 13.1 Refactor a procedural sequence into cohesive objects

Suppose a procedural pipeline validates a job identifier, computes a priority, and queues the job. Keep pure calculation in a function and stateful queue operations in a class:

```python
def normalize_job_id(raw_id: str) -> str:
    """Normalize an external identifier without performing I/O."""
    job_id = raw_id.strip()
    if not job_id:
        raise ValueError("job id must not be empty")
    return job_id.upper()

class PipelineJobQueue:
    """Own normalized pending job IDs in this separate pipeline example."""

    def __init__(self) -> None:
        self._jobs: list[str] = []

    def enqueue(self, raw_id: str) -> None:
        self._jobs.append(normalize_job_id(raw_id))

    def pending(self) -> tuple[str, ...]:
        return tuple(self._jobs)
```

This separation makes normalization independently testable and keeps queue state with the queue. Do not split every line into a function or every concept into a class; separate responsibilities when it makes contracts clearer, reuse real, or tests more focused.

## 14. Common mistakes and how to correct them

| Mistake | Why it is a problem | Better approach |
|---|---|---|
| Putting a mutable list/dict in the class body unintentionally | Instances share one object | Create it in `__init__`; use `ClassVar` only for intentional class state |
| Using mutable default arguments in `__init__` | Calls can share the same default object | Use `None` or an immutable default, then create a new mutable value |
| Treating `_private` as inaccessible | Underscores are conventions, not security controls | Keep a small documented API and validate at boundaries |
| Using `is` to compare strings, numbers, or value objects | Identity is not value equality | Use `==`; reserve `is` for identity/singletons such as `None` |
| Defining equality without considering hashing | Equal objects may violate hash contracts | Use dataclasses where suitable; make hashability an explicit design decision |
| Returning internal lists or dicts | Callers can mutate internal state behind the class's back | Return immutable snapshots or well-defined copies/views |
| Writing a class for one stateless helper | Adds ceremony and an artificial abstraction | Prefer a module-level function |
| Using a dataclass for every class | Generated field equality may be wrong for entities/services | Choose semantics first; use dataclasses when field-based behavior fits |
| Making every helper a static method | Hides simple reusable functions inside classes | Use a module function unless class grouping has a real benefit |
| Doing network or database work in `__init__` | Construction becomes slow, fragile, and hard to test | Inject dependencies; make explicit operations perform I/O |
| Testing implementation details only | Refactoring breaks tests without changing behavior | Assert public contracts and invariants |
| Treating `frozen=True` as deep immutability | Nested mutable values remain mutable | Prefer immutable fields and defensive boundaries |
| Assuming `vars(obj)` works for all objects | Slotted and built-in objects may lack `__dict__` | Use it when supported; use documented public behavior first |
| Using `__slots__` solely because it sounds faster | Can complicate inheritance, weakrefs, and introspection | Measure memory/performance and understand trade-offs first |

## 15. Practical exercises

Try each exercise before reading its solution. Keep each class small and write tests before expanding it.

### Exercise 1 — Build an `Account`

Implement an account with a non-empty owner, a non-negative opening balance, positive deposits, and withdrawals that cannot overdraw. Expose balance read-only. Write tests for valid operations and invalid transitions.

### Exercise 2 — Build an immutable `Money`

Implement `Money(minor_units, currency)` using integer minor units. Normalize currency to uppercase, reject invalid values, compare by value, hash consistently, and support addition only for matching currencies. Explain why `Money(100, "USD")` and `Money(100, "EUR")` must not compare equal.

### Exercise 3 — Compare a handwritten value object with a dataclass

Implement a small immutable `Point(x, y)` twice: once by hand, and once with `@dataclass(frozen=True, slots=True)`. Compare line count, representation, equality, hashing, and validation. Which version is easier to maintain if the requirements are simple field equality? When would custom behavior justify the handwritten version?

### Exercise 4 — Build a `JobQueue`

Implement a queue with independent state per instance, an `enqueue` method that rejects blank identifiers, and a `pending()` method that does not expose the internal list. Test empty state, insertion, invalid input, and independence of two queues.

### Exercise 5 — Function or class?

For each task, choose a function, dataclass, entity, service, or stateful class and justify the decision:

1. Convert Celsius to Fahrenheit.
2. Store a validated immutable date range.
3. Track elapsed time across `start()` and `stop()` calls.
4. Coordinate a repository and a notifier to publish a report.
5. Group ten unrelated string helpers.

### Exercise 6 — Inspect a class

Create two instances with one class attribute and one instance attribute. Use `vars`, `dir`, `getattr`, `type`, and `isinstance` to explain which values are per-instance and which are class-level. Then create an instance attribute with the same name as the class attribute and describe the shadowing behavior.

## 16. Exercise solutions

### Solution 1 — `Account`

Use the read-only-balance implementation in §2.1. The key tests are: blank owner raises `ValueError`; negative opening balance raises; zero/negative deposits raise without changing balance; an overdraft raises without changing balance; valid deposits and withdrawals preserve the invariant.

### Solution 2 — `Money`

The handwritten implementation in §7.3 is a complete introductory solution. Integer minor units avoid binary floating-point representation for the stored amount. Currency is part of the value, so mixed currencies represent different units and cannot be added without an explicit exchange-rate conversion policy. `__eq__` and `__hash__` use the same fields.

### Solution 3 — `Point`

A handwritten version must make the fields stable if it defines `__hash__`; public mutable fields would make dictionary/set membership unreliable after mutation. This version uses read-only properties and rejects ordinary assignment and deletion:

```python
from types import NotImplementedType

class Point:
    __slots__ = ("_x", "_y")

    def __init__(self, x: int, y: int) -> None:
        for name, value in (("x", x), ("y", y)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int")
        object.__setattr__(self, "_x", x)
        object.__setattr__(self, "_y", y)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Point instances are immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("Point instances are immutable")

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"Point(x={self.x!r}, y={self.y!r})"
```

For this immutable field model, a dataclass is usually clearer:

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class PointRecord:
    x: int
    y: int
```

The dataclass supplies representation, field equality, and hashing for the frozen value. Neither version validates that values are truly integers at runtime unless you add checks; annotations alone do not enforce them. A handwritten version is justified when equality, normalization, arithmetic, or construction rules are meaningfully different from field-based defaults.

### Solution 4 — `JobQueue`

Use the implementation in §4.3. State is created in `__init__`, `pending()` returns a tuple snapshot, and `add()` rejects blank IDs before mutation. The critical regression test constructs two queues, adds a job to one, and confirms the other remains empty.

### Solution 5 — Abstraction choices

1. **Function:** pure conversion with no retained state.
2. **Frozen dataclass or handwritten value object:** fields define the value; validation may be needed.
3. **Stateful class:** the object owns timing state across calls and uses an injected clock.
4. **Service or function with injected dependencies:** choose a service if configuration/state or multiple related operations persist; keep I/O boundaries explicit.
5. **Module:** a class would imply a relationship that does not exist.

### Solution 6 — Inspection

Expected principle: `vars(instance)` shows its instance dictionary, not every attribute it can read. Class attributes are visible through normal access and appear in the class namespace. If an instance attribute is assigned with the same name as a class attribute, the instance value normally shadows the class value for that instance only.

## 17. Self-check

Answer without running the code:

1. What is the difference between `Account`, `Account("Mina")`, and `type(Account("Mina"))`?
2. Why is `self` not a keyword, and what does method binding do?
3. What is the difference between `a == b` and `a is b`?
4. Why can `queue.jobs = []` in the class body cause two queues to share state?
5. Why does assigning `one.queue_name = "urgent"` not normally change `Job.queue_name`?
6. Why is `_balance` not a security boundary?
7. When should you use a dataclass rather than a handwritten class?
8. What must be true of `__eq__` and `__hash__` for objects used as set members?
9. Why can a frozen dataclass still contain mutable state?
10. Why should a `Stopwatch` accept an injected clock in tests?
11. What is the introductory attribute lookup model, and what important caveat does it omit?
12. Why is `vars(obj)` not guaranteed to work for every object?

## Summary

Classes are objects that define a namespace and behavior available to their instances. Instances combine identity, type, and state; methods operate on instances through binding. Instance attributes typically hold per-object state, while class attributes are shared lookup targets unless shadowed. Mutable class attributes are a common accidental-sharing bug.

Good class design is less about using every OOP feature and more about keeping related state and behavior cohesive, making invariants hard to violate, choosing equality semantics that match the domain, and keeping the public API small. Use functions for stateless transformations, dataclasses for straightforward data models, and handwritten classes when behavior, invariants, or equality semantics justify them. Use tests to prove behavior and isolation rather than relying on visual inspection.

## Completion checklist

- [ ] I can explain the difference between a class object and an instance.
- [ ] I can use `self`, `type`, `isinstance`, `==`, and `is` correctly.
- [ ] I can explain instance/class attributes and identify accidental shared mutable state.
- [ ] I understand basic method binding and the roles of instance, class, and static methods.
- [ ] I can use `vars`, `dir`, `getattr`, and `hasattr` without treating them as universal or security-safe APIs.
- [ ] I can define and preserve class invariants through construction and methods.
- [ ] I can decide between identity equality, value equality, a handwritten class, and a dataclass.
- [ ] I understand the basic equality/hash contract and avoid hashing mutable value state.
- [ ] I can explain the limitations of underscore conventions and shallow immutability.
- [ ] I can introduce `ClassVar`, `Final`, `Self`, generics, and protocols at a basic level.
- [ ] I can test valid behavior, invalid states, transitions, representation, and per-instance isolation.
- [ ] I can explain when a function or module is simpler than a class.
- [ ] I can identify which advanced topics belong to Lessons 09–10 and Modules 1.11–1.12 rather than trying to learn them all here.
