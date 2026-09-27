# Encapsulation, Abstraction, and Composition

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain why object-oriented design exists beyond simply writing `class` definitions.
- Distinguish **encapsulation**, **abstraction**, and **composition**.
- Design objects around state, behavior, responsibilities, boundaries, and invariants.
- Use Python's attribute conventions, name mangling, and properties correctly.
- Build abstractions with functions, duck typing, Abstract Base Classes (ABCs), and `typing.Protocol`.
- Apply dependency injection without requiring a framework.
- Build systems through composition and delegation.
- Reason about dependency ownership and lifecycle.
- Design code that is replaceable, testable, debuggable, and maintainable.
- Connect OOP design to backend systems, data systems, APIs, ML/AI systems, LLM applications, and agentic AI.
- Recognize when OOP or additional abstraction would make a design worse rather than better.

## Prerequisites

This chapter assumes familiarity with:

- Python variables and data types
- functions and scope
- collections and mutable state
- classes at a basic level
- exceptions and validation
- modules, packages, and imports
- testing, mocking, debugging, and logging

The earlier topics are used here as building blocks rather than repeated as separate chapters.

---

# 1. Why Object-Oriented Design Exists

## The problem before the solution

Imagine a small order-processing program:

```python
order_items = [
    {"name": "Keyboard", "price": 2500, "quantity": 2},
    {"name": "Mouse", "price": 1200, "quantity": 1},
]

total = 0
for item in order_items:
    total += item["price"] * item["quantity"]

if total < 0:
    raise ValueError("invalid total")
```

This is perfectly valid Python.

The problem appears when the program grows.

More code may need to:

- change order state;
- validate quantities;
- calculate totals;
- process payments;
- save orders;
- send notifications;
- apply discounts;
- enforce business rules.

Soon, unrelated code can mutate the same data directly.

```text
Many functions
     |
     +--> shared state
     |
     +--> shared rules
     |
     +--> hidden assumptions
     |
     v
harder maintenance
```

Object-oriented design is one way to create meaningful boundaries around related state and behavior.

## The central idea

A useful mental model is:

```text
Data
 +
Behavior
 +
Responsibilities
 +
Boundaries
 =
Object-oriented design
```

OOP is therefore not merely:

```text
class + object
```

A class is a Python mechanism. The engineering question is whether the resulting object model makes the system easier to understand, change, test, and operate.

## Three ideas in this chapter

```text
Encapsulation
    -> controls/bounds access to state and behavior

Abstraction
    -> exposes what clients need and hides unnecessary detail

Composition
    -> builds larger objects/systems from smaller collaborating objects
```

They overlap, but they are not interchangeable.

---

# 2. Objects, State, and Behavior

## What is an object?

An object combines data with operations that work on that data.

For example:

```python
class BankAccount:
    def __init__(self, owner: str, balance: float) -> None:
        self.owner = owner
        self.balance = balance

    def deposit(self, amount: float) -> None:
        self.balance += amount
```

An instance contains:

```text
State:
    owner
    balance

Behavior:
    deposit()
```

## Why this matters

When state and behavior are related, keeping them near each other can make the model easier to reason about.

Instead of:

```text
external code
    |
    +--> modifies balance
    |
    +--> checks rules
    |
    +--> performs deposit
```

the object can own the operation:

```text
BankAccount
    |
    +--> balance
    |
    +--> deposit()
    |
    +--> account rules
```

## Object boundary

A useful object boundary answers:

> Which state and behavior naturally belong together, and which responsibilities belong somewhere else?

A boundary that is too broad can produce a **God object**. A boundary that is too narrow can create excessive indirection.

---

# 3. Encapsulation

## What is it?

Encapsulation means organizing state and behavior behind an intentional boundary and controlling how that state is manipulated.

It often includes:

- grouping related state and behavior;
- exposing intentional operations;
- validating changes;
- preserving invariants;
- reducing unnecessary access to representation details.

## Real-world analogy

Think about a bank ATM.

You do not normally manipulate the bank's ledger directly.

You ask for an operation:

```text
withdraw money
deposit money
check balance
```

The system decides how the internal state changes.

That boundary is the useful part of the analogy.

## Basic example

```python
class BankAccount:
    def __init__(self, balance: float = 0.0) -> None:
        if balance < 0:
            raise ValueError("balance cannot be negative")
        self._balance = balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self._balance:
            raise ValueError("insufficient balance")
        self._balance -= amount

    @property
    def balance(self) -> float:
        return self._balance
```

The caller uses:

```python
account = BankAccount(1000)
account.withdraw(200)
print(account.balance)
```

The caller does not need to know the representation or internal validation logic.

## Important Python nuance

Python does **not** provide strict private instance fields in the same sense as languages with enforced access modifiers.

Encapsulation in Python is usually supported through:

- naming conventions;
- properties;
- deliberate public APIs;
- module/class design;
- validation;
- documentation;
- composition and dependency boundaries.

---

# 4. Python Attribute Access

## Public attributes

A public attribute is normal attribute access:

```python
class BankAccount:
    def __init__(self, balance: float) -> None:
        self.balance = balance
```

The caller can do:

```python
account = BankAccount(1000)
account.balance = -100000
```

The language permits that assignment.

The engineering issue is whether the design should permit arbitrary mutation.

## Why unrestricted mutation is risky

Suppose the invariant is:

```text
balance >= 0
```

Then:

```python
account.balance = -100000
```

can create an invalid object state.

The problem is not that direct attributes are always bad.

The problem is that a public mutable representation may expose more freedom than the domain model can safely allow.

## Internal convention: one underscore

Python convention:

```python
self._balance
```

means approximately:

> This is an internal implementation detail; consumers should normally not depend on it.

It is a convention, not an enforcement mechanism.

This is useful because a codebase can communicate intent without pretending the runtime has absolute privacy.

## Example

```python
class InventoryItem:
    def __init__(self, quantity: int) -> None:
        self._quantity = quantity

    def restock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("restock amount must be positive")
        self._quantity += amount

    @property
    def quantity(self) -> int:
        return self._quantity
```

---

# 5. Double Underscore and Name Mangling

## What happens with `__name`?

Consider:

```python
class Account:
    def __init__(self) -> None:
        self.__balance = 0
```

Python applies **name mangling** to the attribute.

Conceptually, inside the class, the attribute becomes:

```text
_Account__balance
```

You can observe this:

```python
account = Account()
account._Account__balance = 100
print(account._Account__balance)
```

Name mangling is therefore not a security boundary.

## Why does name mangling exist?

One important purpose is reducing accidental name collisions in subclasses.

Example:

```python
class Parent:
    def __init__(self) -> None:
        self.__value = "parent"


class Child(Parent):
    def __init__(self) -> None:
        super().__init__()
        self.__value = "child"
```

The two `__value` names are mangled differently:

```text
_Parent__value
_Child__value
```

This reduces accidental collision between implementation details.

## What it does not mean

Name mangling is not:

- encryption;
- authentication;
- authorization;
- secret storage;
- protection against a determined caller.

For secrets, use proper security mechanisms rather than relying on leading underscores or name mangling.

## Practical rule

Use:

```text
public_name
```

for intentionally public API.

Use:

```text
_internal_name
```

for internal-by-convention implementation.

Use:

```text
__name
```

when name collision avoidance through mangling is genuinely useful.

Do not use `__name` merely because "private" sounds safer.

---

# 6. Properties

## What is a property?

A property lets attribute-style access invoke behavior.

Example:

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius
```

Usage:

```python
temperature = Temperature(25)
print(temperature.celsius)
```

It looks like ordinary attribute access, but Python is executing the property getter.

## Why use properties?

Properties are useful when you want:

- validation;
- computed values;
- controlled mutation;
- compatibility with attribute-style APIs;
- a future behavior boundary.

## Getter

```python
class User:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name
```

## Setter

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("temperature cannot be below absolute zero")
        self._celsius = value
```

Usage:

```python
temperature = Temperature(20)
temperature.celsius = 25
```

The caller sees a simple assignment, while the setter enforces the rule.

## Deleter

A property can also define deletion behavior:

```python
class Session:
    def __init__(self, token: str) -> None:
        self._token = token

    @property
    def token(self) -> str:
        return self._token

    @token.deleter
    def token(self) -> None:
        self._token = ""
```

Then:

```python
session = Session("abc")
del session.token
```

A deleter is useful only when deletion has meaningful domain semantics. It is not required for ordinary properties.

## Computed property

Properties can represent derived values:

```python
class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    @property
    def area(self) -> float:
        return self.width * self.height
```

The caller uses:

```python
rectangle.area
```

instead of:

```python
rectangle.get_area()
```

Neither style is universally correct. Choose the API that communicates the domain clearly.

---

# 7. The `property()` API

The decorator syntax:

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        self._celsius = value
```

is built on Python's `property()` object.

Conceptually:

```python
def get_celsius(self: "Temperature") -> float:
    return self._celsius


def set_celsius(self: "Temperature", value: float) -> None:
    self._celsius = value


Temperature.celsius = property(
    fget=get_celsius,
    fset=set_celsius,
)
```

The important roles are:

| Argument | Role |
|---|---|
| `fget` | function called when reading the property |
| `fset` | function called when assigning |
| `fdel` | function called when deleting |
| `doc` | property documentation |

A read-only property can omit `fset`.

Decorator syntax is normally easier to read because the property and its related operations remain visually grouped with the class.

---

# 8. Invariants and Controlled Mutation

## What is an invariant?

An invariant is a condition that should remain true for a valid object state.

Examples:

```text
Bank account balance >= 0
Inventory quantity >= 0
Order contains at least one item
Discount percentage between 0 and 100
User age satisfies the domain rule
```

## Why invariants matter

Without invariants, every caller may need to remember every rule.

That creates duplicated reasoning:

```text
caller A checks rule
caller B checks rule
caller C forgets rule
```

A better boundary moves the rule near the state it protects.

## Example: inventory

Poor design:

```python
class Inventory:
    def __init__(self) -> None:
        self.quantity = 10


inventory = Inventory()
inventory.quantity = -500
```

Better design:

```python
class Inventory:
    def __init__(self, quantity: int = 0) -> None:
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        self._quantity = quantity

    def remove(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self._quantity:
            raise ValueError("insufficient inventory")
        self._quantity -= amount

    def add(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._quantity += amount

    @property
    def quantity(self) -> int:
        return self._quantity
```

The design turns arbitrary mutation into domain operations.

## Connection to testing

A previous testing chapter gives the natural strategy:

```text
valid input
invalid input
boundary value
exception behavior
regression case
```

For `Inventory.remove()` you might test:

```text
quantity = 10, remove 1  -> 9
quantity = 10, remove 10 -> 0
quantity = 10, remove 11 -> error
quantity = 10, remove 0  -> error
```

The object boundary and the test boundary reinforce each other.

---

# 9. Encapsulation and Mutability

## The danger of exposed mutable collections

Suppose:

```python
class ShoppingCart:
    def __init__(self) -> None:
        self.items: list[str] = []
```

A caller can do:

```python
cart.items.append("Keyboard")
```

That may bypass rules such as:

- quantity limits;
- product validation;
- duplicate handling;
- inventory checks.

## Controlled mutation

A stronger design may be:

```python
class ShoppingCart:
    def __init__(self) -> None:
        self._items: list[str] = []

    def add(self, item: str) -> None:
        if not item:
            raise ValueError("item cannot be empty")
        self._items.append(item)

    @property
    def items(self) -> tuple[str, ...]:
        return tuple(self._items)
```

Now callers can inspect the contents but cannot mutate the internal list through the returned tuple.

## Why not always copy?

Returning a copy has a cost.

For a very large structure, copying every time may be expensive. In another design, a read-only view or explicit query operation may be more appropriate.

The rule is not:

> Always copy.

The rule is:

> Choose the exposure mechanism based on the ownership, size, mutation semantics, and required performance.

## Immutability as a reasoning tool

Immutable values can make state transitions easier to reason about because the value does not change in place.

But immutability is a design option, not a universal requirement.

---

# 10. Abstraction

## What is abstraction?

Abstraction focuses the public interface on what clients need while hiding unnecessary implementation detail.

The key question is:

> What can the client do?

rather than:

> Which internal steps does the implementation perform?

## Examples

When you use:

```python
sorted(values)
```

you do not need to implement sorting yourself.

When you call:

```python
save_user(user)
```

you may not need to know whether the implementation uses:

```text
SQL
connection pooling
transactions
serialization
retries
```

The function boundary provides an abstraction.

## Real-world analogy

A car's driver interface includes:

```text
steering
brake
accelerator
gear selection
```

The driver does not need to control:

```text
fuel injection timing
sensor firmware
engine control logic
```

Abstraction reduces unnecessary knowledge.

---

# 11. Encapsulation vs Abstraction

| Concept | Main question | Main purpose | Example |
|---|---|---|---|
| Encapsulation | How do we bound and control state/behavior? | Protect boundaries and invariants | `BankAccount.withdraw()` |
| Abstraction | What does the client need to know? | Hide unnecessary implementation detail | `PaymentProcessor.charge()` |
| Composition | How do we build the larger system? | Combine collaborating components | `OrderService(repository, payment)` |

A single design can use all three.

Example:

```text
Order object
    |
    +--> encapsulates order state

PaymentProcessor
    |
    +--> abstracts payment behavior

OrderService
    |
    +--> composes order, payment, repository, notifier
```

Do not collapse the three concepts into one definition.

---

# 12. Functions as Abstractions

Abstraction does not require classes.

A function is often the right abstraction.

```python
def save_user(user: dict[str, object]) -> None:
    ...
```

The caller might simply do:

```python
save_user(user)
```

The implementation can hide:

```text
database connection
serialization
SQL
transactions
```

This is useful because a common beginner misconception is:

```text
abstraction == abstract class
```

That is false.

A well-designed function, module, class, or dependency contract can all create useful abstraction boundaries.

## When a function is enough

A function is often sufficient when:

- there is no meaningful object identity;
- state does not need to persist across calls;
- the behavior is simple;
- the dependency structure is small.

Do not create a class solely because the word "abstraction" appears in the requirement.

---

# 13. Duck Typing

## The Python idea

Python commonly follows a behavioral approach:

> If an object supports the required operation, it can often be used.

Example:

```python
def send_notification(sender: object, message: str) -> None:
    sender.send(message)
```

Objects with a compatible `send()` behavior may work:

```python
class EmailSender:
    def send(self, message: str) -> None:
        print(f"email: {message}")


class SmsSender:
    def send(self, message: str) -> None:
        print(f"sms: {message}")


class MockSender:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send(self, message: str) -> None:
        self.messages.append(message)
```

The caller depends on behavior, not a concrete class hierarchy.

## Benefits

Duck typing can provide:

- flexibility;
- low coupling;
- easy replacement;
- lightweight tests;
- simple adapters.

## Risks

Without a clearly understood contract, failures may occur at runtime:

```text
expected send()
actual object has deliver()
```

or:

```text
expected send(message)
actual send() takes no arguments
```

This is one reason explicit contracts can become valuable as systems grow.

---

# 14. Abstract Base Classes

Python's `abc` module provides Abstract Base Classes.

```python
from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    @abstractmethod
    def charge(self, amount: float) -> bool:
        raise NotImplementedError
```

A concrete implementation can be:

```python
class StripePaymentProcessor(PaymentProcessor):
    def charge(self, amount: float) -> bool:
        return amount > 0
```

The abstract base class expresses an expected operation.

## Instantiation restriction

This cannot be directly instantiated:

```python
processor = PaymentProcessor()
```

because the abstract method has not been implemented.

The concrete class can:

```python
processor = StripePaymentProcessor()
```

## Why use an ABC?

An ABC can be useful when:

- a nominal type relationship is meaningful;
- implementations share an explicit contract;
- you want Python to prevent incomplete concrete subclasses from being instantiated;
- the abstraction is stable enough to justify the mechanism.

An ABC is not automatically better than duck typing or `Protocol`.

---

# 15. ABC API Details

## `ABC`

`ABC` is the common base used for classes that define abstract behavior:

```python
from abc import ABC


class Repository(ABC):
    ...
```

## `abstractmethod`

The usual modern mechanism is:

```python
from abc import ABC, abstractmethod


class Repository(ABC):
    @abstractmethod
    def get(self, key: str) -> object:
        raise NotImplementedError
```

Subclasses must implement the abstract operation before normal instantiation is allowed.

## Modern combinations

For a class method:

```python
from abc import ABC, abstractmethod


class Factory(ABC):
    @classmethod
    @abstractmethod
    def create(cls) -> "Factory":
        raise NotImplementedError
```

For a static method:

```python
from abc import ABC, abstractmethod


class Encoder(ABC):
    @staticmethod
    @abstractmethod
    def encode(value: object) -> bytes:
        raise NotImplementedError
```

For a property:

```python
from abc import ABC, abstractmethod


class Shape(ABC):
    @property
    @abstractmethod
    def area(self) -> float:
        raise NotImplementedError
```

Python historically exposed specialized names such as:

```text
abstractproperty
abstractclassmethod
abstractstaticmethod
```

Modern Python style uses the normal descriptor/decorator plus `@abstractmethod`. The specialized aliases are legacy/deprecated patterns and should not be introduced into new designs merely for historical completeness.

---

# 16. ABC vs Interface vs Protocol

Python does not have a separate `interface` keyword equivalent to some other languages.

In Python, interface-like contracts can be expressed through:

```text
duck typing
ABC
Protocol
```

## ABC

An ABC is a nominal mechanism.

The implementation normally declares a relationship:

```python
class StripePaymentProcessor(PaymentProcessor):
    ...
```

## Protocol

A `Protocol` is primarily a structural typing mechanism.

A class may satisfy the protocol based on its shape without explicitly inheriting from it.

## Duck typing

Duck typing relies directly on runtime behavior:

```text
object has the required method
    -> try to use it
```

## Choosing between them

A useful heuristic:

```text
Need runtime-enforced abstract instantiation rules?
    -> consider ABC

Need static structural contract across unrelated implementations?
    -> consider Protocol

Need a tiny dynamic boundary?
    -> duck typing may be enough
```

These are heuristics, not laws.

---

# 17. Protocols and Structural Abstraction

Python typing provides `Protocol`.

```python
from typing import Protocol


class PaymentProcessor(Protocol):
    def charge(self, amount: float) -> bool:
        ...
```

A class can satisfy the expected shape without inheriting:

```python
class StripePaymentProcessor:
    def charge(self, amount: float) -> bool:
        return amount > 0


class FakePaymentProcessor:
    def __init__(self) -> None:
        self.calls: list[float] = []

    def charge(self, amount: float) -> bool:
        self.calls.append(amount)
        return True
```

The important idea is structural compatibility:

```text
required behavior
      ^
      |
implementation shape
```

## Why Protocol helps architecture

A `Protocol` can make a dependency boundary explicit:

```python
class OrderService:
    def __init__(self, payment: PaymentProcessor) -> None:
        self.payment = payment
```

Now the service does not need to know the exact provider class.

This can support:

- dependency injection;
- testing;
- replacement;
- maintainability;
- loose coupling.

This chapter does not attempt to replace a complete typing chapter. The focus is the architecture benefit of a structural contract.

---

# 18. Dependency Injection

## Poorly coupled design

```python
class OrderService:
    def __init__(self) -> None:
        self.payment = StripePaymentProcessor()
```

The service chooses its own infrastructure.

That can make tests harder:

```text
OrderService
    |
    +--> Stripe
          |
          +--> external behavior
```

## Dependency injection

Instead:

```python
class OrderService:
    def __init__(self, payment: PaymentProcessor) -> None:
        self.payment = payment
```

Then the caller decides:

```python
production_payment = StripePaymentProcessor()
service = OrderService(production_payment)
```

A test can inject:

```python
fake_payment = FakePaymentProcessor()
service = OrderService(fake_payment)
```

## The important idea

Dependency injection is not a framework.

At its simplest:

```text
dependency exists
     ↓
caller provides dependency
     ↓
object uses dependency
```

The technique can be implemented with plain Python constructor arguments, function arguments, or other explicit boundaries.

---

# 19. Composition

## What is composition?

Composition means building a larger object/system from smaller collaborating objects.

The common phrase is:

```text
has-a
```

Example:

```text
Car
├── Engine
├── Transmission
└── BrakeSystem
```

Python:

```python
class Engine:
    def start(self) -> None:
        print("engine started")


class Car:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def start(self) -> None:
        self.engine.start()
```

The car **has an engine**.

## Why composition matters

Composition lets each component own a focused responsibility.

Instead of:

```text
one giant class
    |
    +--> engine logic
    +--> braking logic
    +--> transmission logic
```

you can have:

```text
Car
 |------> Engine
 |------> BrakeSystem
 |------> Transmission
```

The larger object orchestrates collaborators.

---

# 20. Composition vs Inheritance

## The basic distinction

Composition:

```text
Car has an Engine
```

Inheritance:

```text
Dog is an Animal
```

The conceptual relationship is:

```text
has-a
vs
is-a
```

## Composition example

```python
class Car:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
```

## Inheritance example

```python
class Animal:
    def speak(self) -> str:
        return "sound"


class Dog(Animal):
    def speak(self) -> str:
        return "woof"
```

## Why composition can be flexible

Suppose behavior needs to vary independently:

```text
OrderService
    |
    +--> PaymentProcessor
```

You can replace the payment implementation without changing the service's main algorithm.

Inheritance can be appropriate when the subtype relationship is genuine, stable, and behaviorally substitutable.

Do not replace one slogan with another:

```text
"composition is always better"
```

is just as simplistic as:

```text
"inheritance is always better"
```

---

# 21. Delegation

Composition often uses **delegation**.

Delegation means one object asks another object to perform work that belongs to the collaborator.

```python
class OrderRepository:
    def get(self, order_id: str) -> dict[str, object]:
        return {"id": order_id}


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self.repository = repository

    def get_order(self, order_id: str) -> dict[str, object]:
        return self.repository.get(order_id)
```

The service delegates persistence retrieval to the repository.

This gives:

```text
OrderService
    |
    +--> business orchestration
    |
    +--> delegates storage to repository
```

## Benefits

Delegation can reduce:

- duplicated persistence logic;
- knowledge of infrastructure;
- tight coupling;
- testing difficulty.

But delegation can become meaningless indirection when layers add no useful responsibility.

---

# 22. Composition Root

A **composition root** is a place where the application assembles its concrete dependencies.

Small example:

```python
engine = Engine()
car = Car(engine)
```

More realistic:

```python
repository = PostgresRepository(...)
payment = StripePaymentProcessor(...)
notifier = EmailNotificationService(...)

service = OrderService(
    repository=repository,
    payment=payment,
    notifier=notifier,
)
```

The key distinction is:

```text
construction
    !=
business logic
```

Application wiring decides which concrete implementations to use. The domain/service code consumes the injected abstractions.

## Why it helps

Without a composition boundary, object creation can leak everywhere:

```text
controller creates repository
repository creates client
service creates provider
provider creates logger
```

That makes replacement and testing harder.

A composition root centralizes wiring.

---

# 23. Dependency Ownership and Lifecycle

When an object receives a dependency, ask:

> Who owns it?

Possible models include:

### Externally managed dependency

```python
client = DatabaseClient()
service = Service(client)
```

The caller owns the client lifecycle.

### Object-created dependency

```python
class Service:
    def __init__(self) -> None:
        self.client = DatabaseClient()
```

The service is responsible for creating the dependency.

### Shared dependency

```text
Application
   |
   +--> Service A
   |
   +--> Service B
   |
   +--> shared database client
```

The application may own the shared resource.

Lifecycle questions include:

- when is it created?
- when is it closed?
- can it be shared?
- can it be reused?
- who performs cleanup?

Dependency injection clarifies **where the object comes from**. It does not automatically solve lifecycle management.

---

# 24. Composition and Resource Management

Consider:

```text
OrderService
    |
    v
OrderRepository
    |
    v
Database Connection
```

The composition relationship is useful, but resources such as database connections, file handles, or HTTP clients also have lifecycle requirements.

Context managers can express resource lifetimes:

```python
class FileRepository:
    def save(self, path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
```

The larger lesson is:

```text
composition
+
explicit lifecycle ownership
=
more understandable resource management
```

Composition by itself does not automatically close resources or prevent leaks.

---

# 25. Composition and Testability

Suppose production code uses:

```text
OrderService
    |
    v
StripePaymentProcessor
```

A focused unit test may use:

```text
OrderService
    |
    v
FakePaymentProcessor
```

or:

```text
OrderService
    |
    v
MockPaymentProcessor
```

The object boundary makes the dependency replaceable.

Example fake:

```python
class FakePaymentProcessor:
    def __init__(self, should_succeed: bool = True) -> None:
        self.should_succeed = should_succeed
        self.charges: list[float] = []

    def charge(self, amount: float) -> bool:
        self.charges.append(amount)
        return self.should_succeed
```

The test can then assert behavior:

```python
def test_order_service_charges_payment() -> None:
    payment = FakePaymentProcessor()
    service = OrderService(payment=payment)

    service.checkout(amount=100.0)

    assert payment.charges == [100.0]
```

This connects directly to test doubles:

```text
Dummy -> supplied but not meaningfully used
Stub  -> supplies controlled answers
Fake  -> lightweight working implementation
Mock  -> interaction-focused verification
Spy   -> records real or wrapped behavior for observation
```

Do not mock merely because mocking exists. A simple fake can communicate the boundary more clearly.

---

# 26. Loose Coupling

## Tight coupling

```python
class ReportService:
    def __init__(self) -> None:
        self.client = SpecificCloudClient(...)
```

The service knows a concrete infrastructure class.

## Looser coupling

```python
class ReportService:
    def __init__(self, client) -> None:
        self.client = client
```

or:

```python
class ReportClient(Protocol):
    def upload(self, content: bytes) -> str:
        ...
```

The service knows what it needs rather than everything about how the dependency is implemented.

## Why coupling matters

Lower coupling can improve:

- replacement;
- testing;
- refactoring;
- maintainability;
- team ownership boundaries.

But "loose coupling" does not mean "zero coupling." Components must still communicate through meaningful contracts.

---

# 27. Single Responsibility and Composition

Consider a large class:

```text
HugeOrderService
    ├── validation
    ├── pricing
    ├── persistence
    ├── payment
    ├── notification
    └── reporting
```

It may become difficult to change because many unrelated concerns move together.

Composition can separate responsibilities:

```text
OrderValidator
OrderRepository
PaymentProcessor
NotificationService
PricingService
        |
        v
   OrderService
```

The service can orchestrate rather than implement every detail.

## Avoid the opposite extreme

This is not automatically better:

```text
OrderIdValidator
OrderItemValidator
OrderPriceValidator
OrderQuantityValidator
OrderNameValidator
...
```

Creating dozens of tiny classes can make the system harder to understand.

The design target is meaningful responsibility boundaries, not maximum class count.

---

# 28. Integrated Example: E-Commerce Order System

## Architecture

```text
                         Application
                             |
                             v
                       OrderService
                    /       |       \
                   v        v        v
              Repository  Payment  Notifier
                   |         |        |
                   v         v        v
               Database   Provider  Email/SMS
```

The `Order` object owns order state.

## Encapsulation

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderItem:
    name: str
    price: float
    quantity: int
```

The order itself can control valid transitions:

```python
class Order:
    def __init__(self, items: list[OrderItem]) -> None:
        if not items:
            raise ValueError("order must contain at least one item")

        for item in items:
            if item.price < 0:
                raise ValueError("price cannot be negative")
            if item.quantity <= 0:
                raise ValueError("quantity must be positive")

        self._items = tuple(items)
        self._status = "pending"

    @property
    def status(self) -> str:
        return self._status

    @property
    def items(self) -> tuple[OrderItem, ...]:
        return self._items

    def mark_paid(self) -> None:
        if self._status != "pending":
            raise ValueError("only pending orders can be paid")
        self._status = "paid"
```

## Abstraction

The payment dependency can be described with a protocol:

```python
from typing import Protocol


class PaymentProcessor(Protocol):
    def charge(self, amount: float) -> bool:
        ...
```

## Composition

```python
class OrderService:
    def __init__(
        self,
        payment: PaymentProcessor,
        repository: "OrderRepository",
    ) -> None:
        self.payment = payment
        self.repository = repository
```

The service composes collaborators.

## The three ideas together

```text
Order
  |
  +--> encapsulation: controls valid state transitions

PaymentProcessor
  |
  +--> abstraction: defines required behavior

OrderService
  |
  +--> composition: combines order workflow dependencies
```

---

# 29. Banking Example

A simple banking design may contain:

```text
BankAccount
TransactionRepository
PaymentProcessor
NotificationService
BankingService
```

## Encapsulation

`BankAccount` owns balance transitions.

```python
class BankAccount:
    def __init__(self, account_id: str, balance: float = 0.0) -> None:
        if balance < 0:
            raise ValueError("balance cannot be negative")
        self.account_id = account_id
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient balance")
        self._balance -= amount
```

## Abstraction

A repository contract:

```python
from typing import Protocol


class TransactionRepository(Protocol):
    def save(self, account_id: str, amount: float) -> None:
        ...
```

## Composition

```python
class BankingService:
    def __init__(
        self,
        repository: TransactionRepository,
    ) -> None:
        self.repository = repository
```

A real implementation can write to a database. A test fake can store transactions in memory.

---

# 30. Applied AI Example

Consider:

```text
DocumentProcessingService
├── Parser
├── Validator
├── EmbeddingProvider
├── VectorStore
└── Logger
```

## Encapsulation

A `Document` can protect its valid internal state:

```python
class Document:
    def __init__(self, text: str) -> None:
        if not text.strip():
            raise ValueError("document text cannot be empty")
        self._text = text

    @property
    def text(self) -> str:
        return self._text
```

## Abstraction

```python
from typing import Protocol


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]:
        ...
```

Different providers can implement the same operation.

## Composition

```python
class DocumentProcessingService:
    def __init__(
        self,
        parser,
        validator,
        embedder: EmbeddingProvider,
        vector_store,
        logger,
    ) -> None:
        self.parser = parser
        self.validator = validator
        self.embedder = embedder
        self.vector_store = vector_store
        self.logger = logger
```

In tests:

```text
real parser       -> fake parser
real embedding    -> deterministic fake
real vector store -> in-memory fake
real logger       -> test logger
```

The architecture is intentionally replaceable.

---

# 31. LLM Application Example

A question-answering system might be:

```text
QuestionAnsweringService
├── LLMClient
├── Retriever
├── PromptBuilder
└── ResponseValidator
```

An abstraction can represent the model client:

```python
from typing import Protocol


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...
```

Implementations might include:

```text
HostedProviderClient
AlternativeProviderClient
LocalModelClient
FakeLLMClient
```

The service can depend on the behavior it needs:

```python
class QuestionAnsweringService:
    def __init__(
        self,
        llm: LLMClient,
        retriever,
        prompt_builder,
        validator,
    ) -> None:
        self.llm = llm
        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.validator = validator
```

## Why this matters

The service does not need to know:

- provider-specific SDK calls;
- transport details;
- credential handling;
- exact request serialization.

Those concerns can live behind the provider implementation.

No real API credential is needed to unit-test the orchestration.

---

# 32. Agentic AI Example

A simplified agent architecture might be:

```text
Agent
├── Model
├── ToolRegistry
├── Memory
├── Planner
└── Executor
```

## Encapsulation

Each component can protect its internal state:

```text
Memory
    -> controls storage/retrieval behavior

ToolRegistry
    -> controls registered tool state

Agent
    -> controls state transitions
```

## Abstraction

The agent can depend on contracts:

```text
Model
Tool execution
Memory
Planning
```

rather than concrete providers.

## Composition

The agent is built from components:

```python
class Agent:
    def __init__(self, model, tools, memory, planner, executor) -> None:
        self.model = model
        self.tools = tools
        self.memory = memory
        self.planner = planner
        self.executor = executor
```

This can support:

- unit testing;
- provider replacement;
- debugging;
- incremental scaling;
- clearer responsibility boundaries.

The point is architectural application of OOP principles, not a complete agent framework.

---

# 33. Abstract Data Types and Information Hiding

An **Abstract Data Type (ADT)** describes what operations are available and what behavior they provide without requiring clients to know the internal representation.

Examples:

```text
Stack
Queue
BankAccount
```

A stack may expose:

```text
push()
pop()
peek()
```

without exposing whether it uses:

```text
list
deque
custom linked structure
```

That is information hiding.

## Information hiding is not security

Information hiding says:

> Clients should not need unnecessary implementation knowledge.

Security asks questions such as:

> Who is authorized to access this information?

These are different concerns.

A repository can hide SQL details without making the database secure.

---

# 34. Public API vs Internal Implementation

Imagine:

```python
class UserRepository:
    def get_user(self, user_id: str) -> dict[str, object]:
        ...

    def _build_query(self, user_id: str) -> str:
        ...
```

A reasonable public API is:

```text
get_user()
```

The caller should not generally depend on:

```text
_build_query()
```

because changing the SQL generation should not require every consumer to change.

## Why this supports refactoring

Suppose version 1 uses SQL:

```text
SELECT ...
```

and version 2 uses another persistence mechanism.

If callers only depend on:

```python
repository.get_user(user_id)
```

the implementation can change while the public contract remains stable.

This is one practical benefit of encapsulation and abstraction boundaries.

---

# 35. Immutability and Design

## Mutable object

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name
```

The state can change:

```python
user.name = "Bob"
```

## Controlled mutation

```python
class User:
    def __init__(self, name: str) -> None:
        if not name:
            raise ValueError("name is required")
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def rename(self, new_name: str) -> None:
        if not new_name:
            raise ValueError("name is required")
        self._name = new_name
```

## Immutable value

A value can instead be represented so that callers receive a stable snapshot.

For example, immutable tuples:

```python
coordinates = (10.0, 20.0)
```

The design trade-off is:

```text
mutation
    -> convenient for some stateful workflows

immutability
    -> simpler reasoning for some values
```

Use the semantics that match the domain.

---

# 36. Dataclass Connection

When a codebase already uses dataclasses, they can be useful for modeling data without automatically turning every data record into a behavior-heavy class.

Example:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str
```

This gives a concise data model.

The relevant connection here is:

```text
dataclass
    -> data representation

frozen=True
    -> one option for immutability

composition
    -> data objects can be combined into larger domain objects
```

Do not infer that every dataclass needs properties, private fields, or an ABC.

---

# 37. Functional Style Connection

OOP and functional-style programming can coexist.

Object-oriented style:

```python
order_service.process(order)
```

Functional style:

```python
total = calculate_total(items)
```

A production Python system may combine:

```text
objects
+
functions
+
composition
+
immutable values
+
pure transformations
```

For example:

```python
def calculate_total(items: tuple[OrderItem, ...]) -> float:
    return sum(
        item.price * item.quantity
        for item in items
    )
```

The service object may coordinate I/O, while pure functions calculate values.

This can reduce complexity because not every behavior needs mutable object state.

---

# 38. Composition Over Inheritance — Nuanced View

The phrase:

> Favor composition over inheritance.

is useful as a design heuristic.

It often applies when:

- behavior varies independently;
- dependencies need replacement;
- testing needs flexibility;
- responsibilities should remain separate.

Inheritance may still be appropriate when:

- there is a genuine subtype relationship;
- substitutability is meaningful;
- shared behavior is stable;
- the hierarchy is simple and intentional.

The important engineering skill is deciding based on the domain and change patterns.

---

# 39. Liskov/Substitutability Connection

A simplified substitutability idea is:

> If code expects an abstraction, an implementation should honor the abstraction's behavioral contract.

Suppose:

```python
class PaymentProcessor(Protocol):
    def charge(self, amount: float) -> bool:
        ...
```

A fake that always returns `True` can be useful for certain tests.

But the fake should still respect important observable expectations of the contract.

For example, if production code expects:

```text
charge(amount <= 0)
    -> invalid request
```

a fake that silently accepts invalid amounts could make tests misleading.

This connects:

```text
abstraction
+
substitutability
+
test doubles
```

A test double should be useful without violating the behavior the production code relies on.

---

# 40. Common Design Mistakes

## 40.1 Public mutable state everywhere

**Problem**

```python
order.status = "shipped"
```

from any part of the application.

**Why it happens**

Direct assignment is simple.

**Better approach**

Provide explicit transitions when the domain has rules:

```python
order.mark_shipped()
```

---

## 40.2 Treating underscores as security

**Problem**

Assuming:

```python
self._password
```

protects a secret.

**Why it happens**

The word "private" is incorrectly mapped to the underscore convention.

**Better approach**

Use real security controls and secret-management mechanisms.

---

## 40.3 Overusing `__name`

**Problem**

Every attribute becomes:

```python
self.__value
```

**Why it happens**

The developer wants "maximum privacy."

**Better approach**

Use a single underscore for ordinary internal-by-convention state. Use name mangling when collision avoidance is the real need.

---

## 40.4 Getter/setter everywhere

**Problem**

Every field gets:

```text
get_x()
set_x()
```

even when no rule exists.

**Better approach**

Use direct attributes when they are a suitable public data model. Use properties or methods when behavior exists.

---

## 40.5 Giant classes / God objects

**Problem**

One class owns:

```text
validation
database
network
payments
notifications
reporting
```

**Better approach**

Separate meaningful responsibilities and compose them.

---

## 40.6 Deep inheritance hierarchies

**Problem**

A change high in a hierarchy affects many subclasses.

**Better approach**

Use shallow, intentional hierarchies or composition where behavior truly varies independently.

---

## 40.7 Too many composition dependencies

**Problem**

```text
Service(
    A,
    B,
    C,
    D,
    E,
    F,
    G,
    H,
    ...
)
```

**Better approach**

Question whether the object has too many responsibilities or whether a collaborator should itself own a cohesive group.

---

## 40.8 Premature interfaces

**Problem**

Creating five abstractions before there is a second implementation.

**Better approach**

Introduce a contract when it creates a real boundary, replacement point, or useful type/design constraint.

---

## 40.9 Abstract classes without a real need

**Problem**

Using an ABC because "professional architecture requires one."

**Better approach**

Choose the simplest contract that expresses the required behavior.

---

## 40.10 Hidden dependencies

**Problem**

```python
class Service:
    def __init__(self) -> None:
        self.database = create_database()
```

The object silently decides what infrastructure exists.

**Better approach**

Inject meaningful dependencies explicitly when replaceability matters.

---

## 40.11 Poor ownership

**Problem**

No one is clearly responsible for closing a client.

**Better approach**

Define lifecycle ownership at the composition boundary.

---

## 40.12 Business logic mixed with infrastructure

**Problem**

The payment algorithm directly knows how to create HTTP clients, parse provider responses, and log network details.

**Better approach**

Keep provider-specific concerns behind a dependency boundary.

---

## 40.13 Objects that expose too much internal state

**Problem**

Consumers mutate nested dictionaries and lists.

**Better approach**

Expose stable views, queries, or operations appropriate to the domain.

---

## 40.14 Objects that do too little

A wrapper such as:

```python
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b
```

may add no useful abstraction if a function already expresses the idea better.

Use classes when object identity, state, collaboration, or lifecycle justifies them.

---

## 40.15 Mocking architecture instead of designing good boundaries

A large quantity of mocks can hide a poor design.

Better question:

> Can I make the dependency boundary clear enough that a simple fake or focused mock communicates the real behavior?

---

# 41. When Not to Use OOP

Not every Python problem needs classes.

Functions may be simpler for:

- pure transformations;
- small scripts;
- straightforward utilities;
- simple data processing.

Example:

```python
def normalize_name(name: str) -> str:
    return " ".join(name.split()).title()
```

A class would not improve the design merely because the project is "production."

## Use the simplest design that models the problem clearly

A useful decision flow is:

```text
Does the problem have meaningful persistent state?
        |
       yes
        v
Do state + behavior naturally belong together?
        |
       yes
        v
Use an object boundary.

Otherwise:
        |
        v
Can a function/module provide a clearer abstraction?
        |
       yes
        v
Use the simpler abstraction.
```

---

# 42. Refactoring Procedural Code

Start with a simple function:

```python
def process_order(items: list[dict[str, float]]) -> float:
    total = 0.0

    for item in items:
        price = item["price"]
        quantity = item["quantity"]

        if price < 0:
            raise ValueError("price cannot be negative")
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        total += price * quantity

    return total
```

## Step 1: identify the data model

An item has:

```text
name
price
quantity
```

A focused data model can help:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderItem:
    name: str
    price: float
    quantity: int
```

## Step 2: identify invariants

The `OrderItem` invariant is:

```text
price >= 0
quantity > 0
```

## Step 3: identify object behavior

The order can own:

```text
items
total
state transitions
```

## Step 4: isolate external dependencies

Persistence and payment do not need to live inside the order model.

## Step 5: compose

```text
Order
  |
  +--> OrderService
         |
         +--> Repository
         +--> PaymentProcessor
         +--> NotificationService
```

The refactoring is not about adding classes for ceremony. Each step should solve a concrete problem.

---

# 43. Production-Oriented Order Processing Example

## Architecture

```text
Application
   |
   v
OrderService
   |
   +------------------+
   |                  |
   v                  v
Order             PaymentProcessor
                       |
                       v
                 Provider Adapter

OrderService
   |
   +--> OrderRepository
   |
   +--> NotificationService
```

## Contracts

```python
from typing import Protocol


class PaymentProcessor(Protocol):
    def charge(self, amount: float) -> bool:
        ...


class OrderRepository(Protocol):
    def save(self, order: "Order") -> None:
        ...


class NotificationService(Protocol):
    def send(self, message: str) -> None:
        ...
```

## Domain model

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderItem:
    name: str
    price: float
    quantity: int
```

```python
class Order:
    def __init__(self, items: list[OrderItem]) -> None:
        if not items:
            raise ValueError("order must contain at least one item")

        for item in items:
            if item.price < 0:
                raise ValueError("price cannot be negative")
            if item.quantity <= 0:
                raise ValueError("quantity must be positive")

        self._items = tuple(items)
        self._status = "pending"

    @property
    def status(self) -> str:
        return self._status

    @property
    def items(self) -> tuple[OrderItem, ...]:
        return self._items

    @property
    def total(self) -> float:
        return sum(
            item.price * item.quantity
            for item in self._items
        )

    def mark_paid(self) -> None:
        if self._status != "pending":
            raise ValueError("order is not pending")
        self._status = "paid"
```

## Service

```python
class OrderService:
    def __init__(
        self,
        payment: PaymentProcessor,
        repository: OrderRepository,
        notifier: NotificationService,
    ) -> None:
        self.payment = payment
        self.repository = repository
        self.notifier = notifier

    def checkout(self, order: Order) -> None:
        if not self.payment.charge(order.total):
            raise RuntimeError("payment failed")

        order.mark_paid()
        self.repository.save(order)
        self.notifier.send(
            f"Order paid: {order.total:.2f}"
        )
```

## Design analysis

### Encapsulation

`Order` controls:

- valid items;
- status;
- status transition;
- total calculation.

### Abstraction

The service depends on behavior:

```text
PaymentProcessor
OrderRepository
NotificationService
```

rather than concrete infrastructure.

### Composition

`OrderService` combines those collaborators.

### Testability

Each dependency can be replaced with a fake.

### Production caution

The example is deliberately simplified. Real payment systems require additional concerns such as transaction semantics, idempotency, durable state, provider error handling, and operational diagnostics. Those are system concerns layered on top of the OOP principles shown here.

---

# 44. Testing OOP Designs

The previous testing material gives a useful rule:

> Test public behavior and observable contracts rather than private implementation details whenever practical.

## Test invariants

```python
def test_order_rejects_empty_items() -> None:
    try:
        Order([])
    except ValueError as exc:
        assert str(exc) == "order must contain at least one item"
```

A pytest-style version is clearer:

```python
import pytest


def test_order_rejects_empty_items() -> None:
    with pytest.raises(ValueError, match="order must contain at least one item"):
        Order([])
```

## Test public behavior

```python
def test_order_total() -> None:
    items = [
        OrderItem(name="Keyboard", price=100.0, quantity=2),
        OrderItem(name="Mouse", price=50.0, quantity=1),
    ]

    order = Order(items)

    assert order.total == 250.0
```

## Test composed dependencies

```python
class FakePayment:
    def __init__(self) -> None:
        self.charges: list[float] = []

    def charge(self, amount: float) -> bool:
        self.charges.append(amount)
        return True


class FakeRepository:
    def __init__(self) -> None:
        self.saved: list[Order] = []

    def save(self, order: Order) -> None:
        self.saved.append(order)


class FakeNotifier:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send(self, message: str) -> None:
        self.messages.append(message)
```

```python
def test_checkout_composes_dependencies() -> None:
    payment = FakePayment()
    repository = FakeRepository()
    notifier = FakeNotifier()

    service = OrderService(
        payment=payment,
        repository=repository,
        notifier=notifier,
    )

    order = Order([
        OrderItem(name="Keyboard", price=100.0, quantity=2),
    ])

    service.checkout(order)

    assert payment.charges == [200.0]
    assert repository.saved == [order]
    assert notifier.messages == ["Order paid: 200.00"]
    assert order.status == "paid"
```

The test verifies observable behavior and interactions with dependencies.

---

# 45. Debugging OOP Designs

When an OOP system fails, inspect:

```text
object state
method arguments
dependency identity
call order
exception
traceback
logs
call stack
```

Example symptom:

```text
checkout() reports payment success
but order remains pending
```

A systematic debugging process is:

```text
1. Reproduce
2. Identify failing behavior
3. Inspect traceback/logs
4. Locate object/state transition
5. Inspect injected dependency
6. Step through the call stack
7. Compare expected and actual state
8. Identify root cause
9. Fix
10. Add regression test
```

A poor object boundary can make this harder because the state transition is spread across many unrelated components.

A useful object boundary makes the debugging question narrower:

```text
Which collaborator owns this state?
Which method changed it?
Which dependency returned the unexpected result?
```

---

# 46. Progressive Coding Exercises

The exercises below progress from basic syntax/application to production-oriented design. Attempt the problem before reading the solution.

## Exercise 1 — Encapsulated Counter

### Problem

Create a `Counter` class whose value cannot be changed directly through a public `value` attribute.

### Requirements

- Store the internal count using an internal naming convention.
- Provide an `increment()` method.
- Provide a read-only `value` property.

### Solution

```python
class Counter:
    def __init__(self) -> None:
        self._value = 0

    def increment(self) -> None:
        self._value += 1

    @property
    def value(self) -> int:
        return self._value
```

### Explanation

The `_value` attribute is internal by convention. The `value` property provides controlled read access.

### Common Mistake

Thinking `_value` is enforced as private. It is not.

---

## Exercise 2 — Validated Temperature

### Problem

Create a `Temperature` class that rejects temperatures below absolute zero.

### Requirements

- Use a property.
- Validate assignments.
- Allow valid assignments.

### Solution

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("temperature below absolute zero")
        self._celsius = value
```

### Explanation

The setter protects the invariant every time the property changes.

### Common Mistake

Validating only in `__init__` and forgetting later assignments.

---

## Exercise 3 — Bank Account Invariant

### Problem

Implement a bank account that rejects negative balances.

### Requirements

- Support deposit and withdrawal.
- Reject invalid amounts.
- Prevent overdrawing.

### Solution

```python
class BankAccount:
    def __init__(self, balance: float = 0.0) -> None:
        if balance < 0:
            raise ValueError("balance cannot be negative")
        self._balance = balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient balance")
        self._balance -= amount

    @property
    def balance(self) -> float:
        return self._balance
```

### Explanation

The object owns the state transitions, so the invariant is enforced at the boundary.

### Common Mistake

Allowing direct mutation such as `account._balance = -1` and pretending the underscore prevents it.

---

## Exercise 4 — Safe Shopping Cart

### Problem

Store cart items internally but expose them without allowing callers to mutate the internal list directly.

### Requirements

- Add items through a method.
- Reject empty item names.
- Expose a tuple.

### Solution

```python
class ShoppingCart:
    def __init__(self) -> None:
        self._items: list[str] = []

    def add(self, item: str) -> None:
        if not item.strip():
            raise ValueError("item is required")
        self._items.append(item)

    @property
    def items(self) -> tuple[str, ...]:
        return tuple(self._items)
```

### Explanation

The tuple provides a read-oriented snapshot.

### Common Mistake

Returning `self._items` directly when arbitrary mutation would violate the intended boundary.

---

## Exercise 5 — Computed Property

### Problem

Create a `Rectangle` with `width`, `height`, and computed `area`.

### Requirements

- Reject non-positive dimensions.
- Make `area` computed rather than stored independently.

### Solution

```python
class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("dimensions must be positive")
        self.width = width
        self.height = height

    @property
    def area(self) -> float:
        return self.width * self.height
```

### Explanation

The area is derived from current state, so storing a second mutable `area` value would create another invariant to maintain.

### Common Mistake

Allowing `area` and the dimensions to become inconsistent.

---

## Exercise 6 — Function as an Abstraction

### Problem

Write `calculate_total()` so callers do not need to know the internal calculation.

### Requirements

- Accept item dictionaries.
- Return the total.
- Keep the abstraction as a function.

### Solution

```python
def calculate_total(items: list[dict[str, float]]) -> float:
    return sum(
        item["price"] * item["quantity"]
        for item in items
    )
```

### Explanation

The abstraction boundary is the function itself. No class is needed.

### Common Mistake

Creating an unnecessary class with one stateless method.

---

## Exercise 7 — Duck-Typed Sender

### Problem

Create a `send_notification()` function that works with any object providing `send(message)`.

### Requirements

- Do not require a common base class.
- Demonstrate two implementations.

### Solution

```python
def send_notification(sender, message: str) -> None:
    sender.send(message)


class EmailSender:
    def send(self, message: str) -> None:
        print(f"email: {message}")


class SmsSender:
    def send(self, message: str) -> None:
        print(f"sms: {message}")
```

### Explanation

The function depends on behavior rather than inheritance.

### Common Mistake

Assuming duck typing means "anything works." The required behavior still has to match.

---

## Exercise 8 — Basic ABC

### Problem

Define an abstract `Storage` contract with a `save()` method.

### Requirements

- Use `ABC`.
- Use `abstractmethod`.
- Implement one concrete storage class.

### Solution

```python
from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def save(self, key: str, value: str) -> None:
        raise NotImplementedError


class MemoryStorage(Storage):
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    def save(self, key: str, value: str) -> None:
        self.data[key] = value
```

### Explanation

`Storage` states the required behavior. `MemoryStorage` supplies the concrete implementation.

### Common Mistake

Instantiating the abstract base directly.

---

## Exercise 9 — Protocol Boundary

### Problem

Define a `Notifier` protocol and create a concrete implementation without inheriting from the protocol.

### Requirements

- Use `typing.Protocol`.
- Define `send(message)`.
- Provide a compatible concrete class.

### Solution

```python
from typing import Protocol


class Notifier(Protocol):
    def send(self, message: str) -> None:
        ...


class ConsoleNotifier:
    def send(self, message: str) -> None:
        print(message)
```

### Explanation

`ConsoleNotifier` structurally matches the protocol.

### Common Mistake

Assuming a protocol must be inherited explicitly for structural compatibility.

---

## Exercise 10 — Dependency Injection

### Problem

Refactor a service that directly creates its payment provider.

### Requirements

- Remove concrete construction from the service.
- Inject a dependency through the constructor.
- Allow a fake to be used in tests.

### Solution

```python
from typing import Protocol


class PaymentProcessor(Protocol):
    def charge(self, amount: float) -> bool:
        ...


class OrderService:
    def __init__(self, payment: PaymentProcessor) -> None:
        self.payment = payment

    def checkout(self, amount: float) -> bool:
        return self.payment.charge(amount)
```

### Explanation

The caller now controls the dependency, making the service easier to test and replace.

### Common Mistake

Adding a service locator or framework when a constructor argument is sufficient.

---

## Exercise 11 — Composition

### Problem

Create a `Car` that receives an `Engine`.

### Requirements

- Use a constructor dependency.
- Delegate `start()` to the engine.

### Solution

```python
class Engine:
    def start(self) -> str:
        return "engine started"


class Car:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def start(self) -> str:
        return self.engine.start()
```

### Explanation

The car has an engine and delegates engine-specific work.

### Common Mistake

Copying engine logic into `Car` rather than composing the engine object.

---

## Exercise 12 — Composition Root

### Problem

Assemble a small application from concrete dependencies.

### Requirements

- Create repository, payment, and notifier instances.
- Inject them into `OrderService`.
- Keep wiring outside the service.

### Solution

```python
class Repository:
    def save(self, value: str) -> None:
        print(f"saved: {value}")


class Payment:
    def charge(self, amount: float) -> bool:
        return amount > 0


class Notifier:
    def send(self, message: str) -> None:
        print(message)


class OrderService:
    def __init__(self, repository, payment, notifier) -> None:
        self.repository = repository
        self.payment = payment
        self.notifier = notifier


repository = Repository()
payment = Payment()
notifier = Notifier()

service = OrderService(
    repository=repository,
    payment=payment,
    notifier=notifier,
)
```

### Explanation

The bottom part is application wiring: a simple composition root.

### Common Mistake

Moving construction back into `OrderService`.

---

## Exercise 13 — Delegation

### Problem

Create an `OrderService.get_order()` method that delegates retrieval to an injected repository.

### Requirements

- Repository owns storage access.
- Service owns orchestration.
- Service does not implement storage logic.

### Solution

```python
class Repository:
    def get(self, order_id: str) -> dict[str, object]:
        return {"id": order_id}


class OrderService:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def get_order(self, order_id: str) -> dict[str, object]:
        return self.repository.get(order_id)
```

### Explanation

The service delegates persistence behavior to the repository.

### Common Mistake

Putting SQL/query construction inside every service method.

---

## Exercise 14 — Test Double Selection

### Problem

A service depends on an external payment provider. Decide whether to use a stub, fake, mock, or real implementation for a focused unit test.

### Requirements

- The test needs deterministic success.
- It should not perform a real network call.
- The test should inspect the amount requested.

### Solution

A small fake is often the clearest choice:

```python
class FakePayment:
    def __init__(self) -> None:
        self.amounts: list[float] = []

    def charge(self, amount: float) -> bool:
        self.amounts.append(amount)
        return True
```

Then:

```python
payment = FakePayment()
service = OrderService(payment=payment)

service.checkout(100.0)

assert payment.amounts == [100.0]
```

### Explanation

The fake provides controlled behavior and records state. A mock could also verify interaction, but choosing the smallest clear test double is often better.

### Common Mistake

Assuming every external dependency must be mocked with a large set of call assertions.

---

## Exercise 15 — Refactor Public Mutable State

### Problem

Refactor:

```python
class Inventory:
    def __init__(self) -> None:
        self.quantity = 10
```

so callers cannot arbitrarily set a negative quantity.

### Requirements

- Use internal state.
- Provide controlled add/remove methods.
- Expose read access.

### Solution

```python
class Inventory:
    def __init__(self, quantity: int = 0) -> None:
        if quantity < 0:
            raise ValueError("quantity cannot be negative")
        self._quantity = quantity

    @property
    def quantity(self) -> int:
        return self._quantity

    def add(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._quantity += amount

    def remove(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self._quantity:
            raise ValueError("insufficient inventory")
        self._quantity -= amount
```

### Explanation

The state transition rules are now centralized.

### Common Mistake

Adding a setter that simply assigns `_quantity` and recreates the original design problem.

---

## Exercise 16 — Replace Inheritance with Composition

### Problem

A report service inherits from `EmailSender` only so it can send email.

Refactor so the service composes an injected sender.

### Requirements

- Remove inheritance.
- Inject the sender.
- Keep report logic separate from notification logic.

### Solution

```python
class EmailSender:
    def send(self, message: str) -> None:
        print(f"email: {message}")


class ReportService:
    def __init__(self, sender: EmailSender) -> None:
        self.sender = sender

    def publish(self, report: str) -> None:
        self.sender.send(report)
```

### Explanation

`ReportService` does not become a specialized kind of `EmailSender`. It uses a sender.

### Common Mistake

Creating an inheritance relationship for code reuse when the domain relationship is not `is-a`.

---

## Exercise 17 — Regression Test for a Refactor

### Problem

You refactor order total calculation from a function into an `Order` property. Preserve the old observable behavior.

### Requirements

- Write a behavior-focused test.
- The test should not care whether the implementation uses a property or a helper function.

### Solution

```python
def test_order_total_is_preserved() -> None:
    order = Order([
        OrderItem(name="Keyboard", price=100.0, quantity=2),
        OrderItem(name="Mouse", price=50.0, quantity=1),
    ])

    assert order.total == 250.0
```

### Explanation

The regression test protects the behavior that mattered during the refactor.

### Common Mistake

Testing the internal private field or helper function instead of the public result.

---

## Exercise 18 — Property-Based Boundary Thinking

### Problem

For a temperature property, identify the boundary cases around absolute zero.

### Requirements

Test:

```text
below minimum
exact minimum
just above minimum
```

### Solution

```python
import pytest


@pytest.mark.parametrize(
    "value,should_fail",
    [
        (-273.16, True),
        (-273.15, False),
        (-273.14, False),
    ],
)
def test_temperature_boundary(value: float, should_fail: bool) -> None:
    if should_fail:
        with pytest.raises(ValueError):
            Temperature(value)
    else:
        temperature = Temperature(value)
        assert temperature.celsius == value
```

### Explanation

The test connects encapsulated validation to boundary-value analysis.

### Common Mistake

Testing only an ordinary valid value and assuming the setter is correct.

---

## Exercise 19 — OOP Design for an API Client

### Problem

Design a service that uses an HTTP client abstraction without making real network calls in unit tests.

### Requirements

- Define the required client behavior.
- Inject the client.
- Use a fake client for tests.

### Solution

```python
from typing import Protocol


class UserClient(Protocol):
    def fetch_user(self, user_id: str) -> dict[str, object]:
        ...


class UserService:
    def __init__(self, client: UserClient) -> None:
        self.client = client

    def get_display_name(self, user_id: str) -> str:
        user = self.client.fetch_user(user_id)
        return str(user["name"])


class FakeUserClient:
    def __init__(self, user: dict[str, object]) -> None:
        self.user = user

    def fetch_user(self, user_id: str) -> dict[str, object]:
        return self.user
```

Test:

```python
def test_user_service_uses_client() -> None:
    client = FakeUserClient({"name": "Alice"})
    service = UserService(client)

    assert service.get_display_name("123") == "Alice"
```

### Explanation

The service depends on an abstraction and remains independent of network transport.

### Common Mistake

Instantiating a real HTTP client inside `UserService`.

---

## Exercise 20 — LLM Client Abstraction

### Problem

Create a simple question-answering service that can use a fake LLM client.

### Requirements

- Define the `generate(prompt)` contract.
- Inject the client.
- Write a deterministic fake.

### Solution

```python
from typing import Protocol


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class FakeLLM:
    def generate(self, prompt: str) -> str:
        return f"answer for: {prompt}"


class QuestionAnsweringService:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def answer(self, question: str) -> str:
        prompt = f"Question: {question}"
        return self.llm.generate(prompt)
```

### Explanation

The orchestration can be tested deterministically without a real model provider.

### Common Mistake

Trying to make the unit test reproduce probabilistic production model behavior exactly.

---

## Exercise 21 — Diagnose Over-Abstraction

### Problem

You find a class hierarchy:

```text
BaseRepository
    -> UserRepository
        -> CachedUserRepository
            -> LoggedCachedUserRepository
```

Each class changes one small behavior.

Explain whether the hierarchy should automatically be replaced with composition.

### Requirements

- Identify evidence you would inspect.
- Explain trade-offs.
- Suggest a refactoring only if justified.

### Solution

Do not refactor merely because the hierarchy is long.

Inspect:

```text
Are these genuine subtypes?
Is substitutability stable?
Are behaviors varying independently?
Do tests become harder?
Does construction become difficult?
Would collaborators express the design more clearly?
```

If caching and logging vary independently, composition may be clearer:

```text
UserRepository
   |
   +--> cache
   |
   +--> logger
```

But if the hierarchy models a stable domain subtype and remains simple, inheritance may still be appropriate.

### Explanation

Difficulty comes from design reasoning, not from memorizing "composition good, inheritance bad."

### Common Mistake

Replacing every inheritance hierarchy with five injected dependencies without understanding the domain.

---

## Exercise 22 — Production Architecture Review

### Problem

Review this service:

```python
class CustomerService:
    def __init__(self) -> None:
        self.database = Postgres(...)
        self.redis = Redis(...)
        self.payment = Stripe(...)
        self.email = EmailClient(...)
        self.logger = create_logger(...)
```

Explain the architectural concerns.

### Requirements

Identify:

- coupling;
- dependency ownership;
- testability;
- composition root;
- lifecycle.

### Solution

The service currently chooses and constructs all infrastructure itself.

A more replaceable design would inject meaningful dependencies:

```python
class CustomerService:
    def __init__(
        self,
        database,
        cache,
        payment,
        email,
        logger,
    ) -> None:
        self.database = database
        self.cache = cache
        self.payment = payment
        self.email = email
        self.logger = logger
```

The composition root can construct concrete implementations.

### Explanation

The important improvement is not "more interfaces." It is moving infrastructure construction to the application boundary and making dependencies explicit.

### Common Mistake

Assuming constructor injection alone fixes an object that still has too many unrelated responsibilities.

---

# 47. Debugging Lab

Each lab presents a deliberately flawed design. Use the debugging workflow:

```text
Observe symptom
    ↓
Collect evidence
    ↓
Locate boundary/state
    ↓
Identify root cause
    ↓
Correct design
    ↓
Add regression protection
```

## Lab 1 — Public Mutable State Breaks an Invariant

### Broken code

```python
class Account:
    def __init__(self) -> None:
        self.balance = 100


account = Account()
account.balance = -500
```

### Observed problem

The account contains an invalid balance.

### Debugging approach

Ask:

```text
Who can change balance?
Where is the invariant enforced?
Can any caller bypass the rule?
```

### Root cause

The representation is publicly mutable.

### Corrected design

```python
class Account:
    def __init__(self, balance: float = 0.0) -> None:
        if balance < 0:
            raise ValueError("balance cannot be negative")
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient balance")
        self._balance -= amount
```

### Lesson

Encapsulation protects an invariant by moving state transitions behind meaningful operations.

---

## Lab 2 — Incorrect Property Setter

### Broken code

```python
class User:
    def __init__(self, age: int) -> None:
        self.age = age

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        self.age = value
```

### Observed problem

Assigning `age` recursively calls the setter.

### Debugging approach

Inspect the stack:

```text
age setter
    -> self.age = value
        -> age setter
            -> self.age = value
                ...
```

### Root cause

The setter writes through the property instead of the backing attribute.

### Corrected design

```python
class User:
    def __init__(self, age: int) -> None:
        self.age = age

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if value < 0:
            raise ValueError("age cannot be negative")
        self._age = value
```

### Lesson

A property setter usually writes to an internal representation, not back through the same property.

---

## Lab 3 — Wrong Abstraction Boundary

### Broken code

```python
class OrderService:
    def checkout(self, order) -> None:
        connection = create_postgres_connection()
        connection.execute(
            "INSERT INTO orders ...",
            order,
        )

        stripe_client = create_stripe_client()
        stripe_client.charge(order.total)
```

### Observed problem

Unit tests require database and payment infrastructure.

### Debugging approach

Trace responsibilities:

```text
OrderService
    -> database construction
    -> SQL details
    -> payment construction
    -> payment provider details
    -> business workflow
```

### Root cause

Infrastructure concerns are mixed into the service's orchestration.

### Corrected design

```python
class OrderService:
    def __init__(self, repository, payment) -> None:
        self.repository = repository
        self.payment = payment

    def checkout(self, order) -> None:
        if not self.payment.charge(order.total):
            raise RuntimeError("payment failed")
        self.repository.save(order)
```

### Lesson

A good abstraction hides infrastructure details from higher-level workflow code.

---

## Lab 4 — Tight Coupling Makes Testing Difficult

### Broken code

```python
class ReportService:
    def __init__(self) -> None:
        self.client = RealCloudStorageClient()

    def publish(self, report: bytes) -> None:
        self.client.upload(report)
```

### Observed problem

Every unit test attempts to use cloud infrastructure.

### Root cause

Concrete dependency construction occurs inside the service.

### Corrected design

```python
from typing import Protocol


class Storage(Protocol):
    def upload(self, data: bytes) -> None:
        ...


class ReportService:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def publish(self, report: bytes) -> None:
        self.storage.upload(report)
```

### Lesson

Dependency injection creates a replaceable seam.

---

## Lab 5 — Incorrect Dependency Injection

### Broken code

```python
class OrderService:
    def __init__(self, payment=None) -> None:
        self.payment = payment or StripePaymentProcessor()
```

### Observed symptom

A test passes a fake object, but the service still uses the real provider.

### Root cause

The injected fake is treated as falsey and replaced.

### Corrected design

```python
class OrderService:
    def __init__(self, payment=None) -> None:
        if payment is None:
            payment = StripePaymentProcessor()
        self.payment = payment
```

An even clearer design is to require the dependency at the boundary:

```python
class OrderService:
    def __init__(self, payment) -> None:
        self.payment = payment
```

### Lesson

Be precise about optional dependencies. Do not use truthiness when identity with `None` expresses the actual condition.

---

## Lab 6 — Circular Composition Dependency

### Broken code

```python
class Service:
    def __init__(self) -> None:
        self.repository = Repository(self)


class Repository:
    def __init__(self, service: Service) -> None:
        self.service = service
```

### Observed problem

Construction creates a circular dependency.

### Root cause

Both objects require the other during construction.

### Better direction

Usually the repository should not need the whole service:

```python
class Repository:
    def save(self, value: str) -> None:
        ...


class Service:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
```

### Lesson

Dependency direction matters. A lower-level persistence component depending on the higher-level service can create unnecessary cycles.

---

## Lab 7 — Test Double Does Not Match the Contract

### Broken code

```python
class PaymentProcessor:
    def charge(self, amount: float) -> bool:
        ...


class FakePayment:
    def charge(self) -> bool:
        return True
```

### Observed problem

The service calls:

```python
payment.charge(100)
```

but the fake accepts no argument.

### Root cause

The test double does not satisfy the dependency contract.

### Correction

```python
class FakePayment:
    def charge(self, amount: float) -> bool:
        return True
```

If static typing is used, a `Protocol` can make the intended contract clearer.

### Lesson

A fake is valuable only if it models the observable contract the production code relies upon.

---

## Lab 8 — Over-Engineered Hierarchy

### Broken design

```text
BaseNotification
    -> AbstractNotification
        -> EmailNotification
            -> LoggedEmailNotification
                -> RetryingLoggedEmailNotification
```

### Observed symptom

Small behavior changes require hierarchy changes.

### Debugging approach

Map independent dimensions:

```text
channel
logging
retry
formatting
```

### Root cause

Multiple independent behaviors were encoded as inheritance levels.

### Corrected direction

Use composition:

```text
NotificationService
   |
   +--> Sender
   +--> RetryPolicy
   +--> Logger
```

### Lesson

Composition is particularly useful when behaviors need to vary independently.

---

# 48. Complete Mini Project — Production-Oriented Order Processing System

## 48.1 Requirements

Build a small Python order-processing system with:

- encapsulated order state;
- input validation;
- invariants;
- payment abstraction;
- repository abstraction;
- notification abstraction;
- composition;
- dependency injection;
- test doubles;
- pytest tests;
- error handling;
- logging.

## 48.2 Architecture

```text
                         Application
                             |
                             v
                       Composition Root
                             |
                             v
                       OrderService
                  /          |          \
                 v           v           v
               Order      Payment      Repository
                            |
                            v
                         Provider

                         OrderService
                              |
                              v
                           Notifier
```

## 48.3 Domain model

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderItem:
    name: str
    price: float
    quantity: int
```

```python
class Order:
    def __init__(self, items: list[OrderItem]) -> None:
        if not items:
            raise ValueError("order cannot be empty")

        for item in items:
            if item.price < 0:
                raise ValueError("price cannot be negative")
            if item.quantity <= 0:
                raise ValueError("quantity must be positive")

        self._items = tuple(items)
        self._status = "pending"

    @property
    def items(self) -> tuple[OrderItem, ...]:
        return self._items

    @property
    def total(self) -> float:
        return sum(
            item.price * item.quantity
            for item in self._items
        )

    @property
    def status(self) -> str:
        return self._status

    def mark_paid(self) -> None:
        if self._status != "pending":
            raise ValueError("order is not pending")
        self._status = "paid"
```

## 48.4 Contracts

```python
from typing import Protocol


class PaymentProcessor(Protocol):
    def charge(self, amount: float) -> bool:
        ...


class OrderRepository(Protocol):
    def save(self, order: Order) -> None:
        ...


class NotificationService(Protocol):
    def send(self, message: str) -> None:
        ...
```

## 48.5 Service

```python
import logging


class OrderService:
    def __init__(
        self,
        payment: PaymentProcessor,
        repository: OrderRepository,
        notifier: NotificationService,
    ) -> None:
        self.payment = payment
        self.repository = repository
        self.notifier = notifier
        self.logger = logging.getLogger(__name__)

    def checkout(self, order: Order) -> None:
        self.logger.info(
            "starting checkout for order total %.2f",
            order.total,
        )

        if not self.payment.charge(order.total):
            self.logger.warning("payment declined")
            raise RuntimeError("payment failed")

        order.mark_paid()
        self.repository.save(order)
        self.notifier.send(
            f"Order paid: {order.total:.2f}"
        )

        self.logger.info("checkout completed")
```

## 48.6 Test doubles

```python
class FakePayment:
    def __init__(self, success: bool = True) -> None:
        self.success = success
        self.charges: list[float] = []

    def charge(self, amount: float) -> bool:
        self.charges.append(amount)
        return self.success


class FakeRepository:
    def __init__(self) -> None:
        self.orders: list[Order] = []

    def save(self, order: Order) -> None:
        self.orders.append(order)


class FakeNotifier:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send(self, message: str) -> None:
        self.messages.append(message)
```

## 48.7 Tests

```python
import pytest


def make_order() -> Order:
    return Order([
        OrderItem(
            name="Keyboard",
            price=100.0,
            quantity=2,
        )
    ])


def test_order_rejects_empty_items() -> None:
    with pytest.raises(ValueError, match="order cannot be empty"):
        Order([])


def test_order_total() -> None:
    order = make_order()
    assert order.total == 200.0


def test_checkout_marks_order_paid() -> None:
    payment = FakePayment()
    repository = FakeRepository()
    notifier = FakeNotifier()

    service = OrderService(
        payment=payment,
        repository=repository,
        notifier=notifier,
    )

    order = make_order()
    service.checkout(order)

    assert order.status == "paid"
    assert payment.charges == [200.0]
    assert repository.orders == [order]
    assert notifier.messages == ["Order paid: 200.00"]


def test_failed_payment_does_not_mark_order_paid() -> None:
    payment = FakePayment(success=False)
    repository = FakeRepository()
    notifier = FakeNotifier()

    service = OrderService(
        payment=payment,
        repository=repository,
        notifier=notifier,
    )

    order = make_order()

    with pytest.raises(RuntimeError, match="payment failed"):
        service.checkout(order)

    assert order.status == "pending"
    assert repository.orders == []
    assert notifier.messages == []
```

## 48.8 What this project demonstrates

```text
Encapsulation
    Order owns valid state and transitions.

Abstraction
    PaymentProcessor, OrderRepository, NotificationService
    define required behavior.

Composition
    OrderService combines collaborators.

Dependency Injection
    dependencies are supplied from outside.

Test Doubles
    fakes replace external systems.

Testing
    invariants, behavior, and failure paths are protected.

Debugging
    logs and object state give useful evidence.

Production direction
    concrete infrastructure belongs at the application boundary.
```

## 48.9 Refactoring opportunities

As the system grows, consider:

- a dedicated domain error type;
- stronger money modeling;
- explicit lifecycle management;
- a logging configuration at the application boundary;
- persistence integration tests;
- provider contract tests;
- transaction/idempotency handling for real payment workflows.

Do not add these merely for theoretical completeness. Add them when the real system requirements justify them.

---

# 49. Interview Questions

## Beginner

### What is encapsulation?

Encapsulation is organizing state and behavior behind an intentional boundary and controlling how the state can be accessed or changed.

### What is abstraction?

Abstraction exposes the behavior clients need while hiding unnecessary implementation detail.

### What is composition?

Composition builds a larger object/system from smaller collaborating objects.

### Is Python truly private?

Not in the strict field-access sense found in some languages. Python primarily uses conventions, properties, and deliberate APIs. Double-underscore names use name mangling, which is not security.

### Why use properties?

Properties allow attribute-style access to behavior such as validation, computed values, and controlled mutation.

## Intermediate

### Encapsulation vs abstraction?

Encapsulation focuses on the boundary and control of state/behavior. Abstraction focuses on simplifying what clients need to know.

### What is an invariant?

A condition that should remain true for a valid object state.

### What is duck typing?

Using an object based on the behavior it provides rather than requiring a specific declared class relationship.

### What is an ABC?

An Abstract Base Class is a class mechanism for expressing abstract behavior and restricting instantiation of incomplete subclasses.

### What is a Protocol?

A structural typing mechanism that expresses the operations an object should provide without requiring explicit inheritance.

### ABC vs Protocol?

ABC is commonly used for nominal relationships and runtime abstract-method restrictions. `Protocol` is primarily a structural typing contract. Neither is universally required.

### What is dependency injection?

Providing a dependency to an object or function from outside instead of forcing that code to construct the dependency itself.

### What is delegation?

One component asks another component to perform work that belongs to the collaborator's responsibility.

### What is a composition root?

A boundary where concrete dependencies are assembled and injected into application components.

## Advanced

### Why does composition often improve testability?

Dependencies can be replaced with fakes, stubs, or mocks without rewriting the service's core logic.

### Why can excessive abstraction be harmful?

Each abstraction has a cognitive and maintenance cost. Too many interfaces or wrappers can obscure simple behavior and make changes harder.

### When should inheritance be preferred?

When there is a genuine subtype relationship, substitutability is meaningful, shared behavior is stable, and the hierarchy remains simple and intentional.

### Why can public mutable state be dangerous?

Any caller can change it, potentially bypassing validation and breaking invariants.

### How would you design an extensible payment system?

Define the behavior the order workflow needs, inject a provider implementation, keep provider-specific details behind the boundary, use test doubles for unit tests, and use integration/contract coverage at the real provider boundary where appropriate.

### How do these concepts apply to AI systems?

Model clients, retrievers, vector stores, tool registries, memory components, and validators can be composed behind explicit contracts. Domain state can be encapsulated, and external providers can be replaced with deterministic test implementations.

---

# 50. Architecture Questions

## 1. Design a payment-processing system using abstraction and composition

### Model reasoning

Use a payment contract such as:

```text
PaymentProcessor
```

Then compose:

```text
OrderService
    |
    +--> PaymentProcessor
    +--> OrderRepository
    +--> NotificationService
```

Concrete provider selection belongs in the composition root.

---

## 2. Design a repository layer for a banking system

### Model reasoning

The banking service should depend on a repository behavior boundary rather than database-specific code.

```text
BankingService
    |
    v
TransactionRepository
    |
    +--> PostgreSQL implementation
    +--> Test fake
```

The domain object protects account invariants.

---

## 3. Design an LLM provider abstraction

### Model reasoning

Define only the behavior required by the application:

```python
class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...
```

Provider implementations can translate this to provider-specific APIs.

The test suite can inject a fake.

---

## 4. Design a document-processing pipeline

### Model reasoning

A useful composition might be:

```text
DocumentProcessingService
    |
    +--> Parser
    +--> Validator
    +--> EmbeddingProvider
    +--> VectorStore
```

The `Document` domain object can protect valid state.

The service orchestrates. Infrastructure implementations remain replaceable.

---

## 5. Design an agent architecture using composition

### Model reasoning

Use:

```text
Agent
├── Model
├── Planner
├── ToolRegistry
├── Memory
└── Executor
```

Each collaborator owns a meaningful responsibility. The composition root decides which implementations are used.

---

## 6. How would you make external services replaceable?

### Model reasoning

Identify the minimum behavior the application needs, express the contract with a function, protocol, or ABC where justified, inject the dependency, and test against a fake or mock.

---

## 7. How would you design for unit-testability?

### Model reasoning

Keep business logic separate from:

```text
database
network
external APIs
cloud clients
```

Inject those dependencies at boundaries and keep domain calculations deterministic where practical.

---

## 8. Where would you use Protocol vs ABC?

### Model reasoning

Use `Protocol` when structural compatibility is useful, especially across unrelated implementations.

Use ABC when the runtime abstraction itself should enforce incomplete subclasses and a nominal relationship is meaningful.

---

## 9. How would you avoid over-abstraction?

### Model reasoning

Start with the simplest design that satisfies today's requirements.

Introduce another abstraction when it creates a genuine:

```text
replacement point
dependency boundary
behavioral contract
responsibility boundary
```

Avoid interfaces whose only purpose is to satisfy a style rule.

---

## 10. How would you prevent a service from becoming a God object?

### Model reasoning

Identify independent responsibilities, move cohesive behavior behind focused boundaries, then compose the collaborators.

Validate the result by asking whether the final service primarily coordinates rather than owning every detail.

---

# 51. Production Checklist

## Encapsulation

- [ ] I understand state and behavior.
- [ ] I understand object boundaries.
- [ ] I distinguish public attributes from internal-by-convention attributes.
- [ ] I understand `_single_leading_underscore`.
- [ ] I understand name mangling.
- [ ] I know name mangling is not security.
- [ ] I can use properties for meaningful behavior.
- [ ] I understand invariants.
- [ ] I can control mutation where the domain requires it.
- [ ] I do not expose mutable internal collections without considering the consequences.

## Abstraction

- [ ] I can explain abstraction without saying "abstract class."
- [ ] I can create abstractions with functions.
- [ ] I understand duck typing.
- [ ] I understand ABCs.
- [ ] I understand `abstractmethod`.
- [ ] I understand modern combinations such as `@classmethod` + `@abstractmethod`.
- [ ] I understand `Protocol`.
- [ ] I can distinguish nominal and structural contracts.
- [ ] I know that no one abstraction mechanism is universally required.
- [ ] I can identify what a client actually needs to know.

## Composition

- [ ] I understand has-a relationships.
- [ ] I can compose objects from collaborators.
- [ ] I understand delegation.
- [ ] I understand a composition root.
- [ ] I understand dependency ownership.
- [ ] I understand lifecycle responsibility.
- [ ] I can use dependency injection without a framework.
- [ ] I can replace external dependencies in tests.
- [ ] I understand the trade-off between composition and inheritance.

## Testing and Debugging

- [ ] I test public behavior and invariants.
- [ ] I use boundary and invalid-input tests around encapsulated state.
- [ ] I choose test doubles intentionally.
- [ ] I can debug object-state problems with a traceback and call stack.
- [ ] I can inspect injected dependencies during debugging.
- [ ] I add regression tests for discovered defects.
- [ ] I avoid tests that depend unnecessarily on private implementation details.

## Production

- [ ] Infrastructure construction is separated from business orchestration where appropriate.
- [ ] Dependencies are explicit when replaceability matters.
- [ ] Resource ownership is clear.
- [ ] Logging configuration is not scattered arbitrarily across every object.
- [ ] External API clients have clear boundaries.
- [ ] Database access is behind a deliberate boundary where useful.
- [ ] AI/LLM providers can be replaced without rewriting application logic where the architecture requires it.
- [ ] Agent components have meaningful boundaries.
- [ ] I know when not to use OOP.
- [ ] I avoid creating abstractions merely for appearance.

---

# 52. Final Knowledge Check

## 1. A class has `self._balance`. Is the field private?

**Answer:** No. The leading underscore communicates internal intent by convention. It does not enforce access control.

## 2. What problem does `__balance` solve?

**Answer:** Python name mangling primarily reduces accidental name collisions, especially across inheritance hierarchies. It is not security.

## 3. Why might a property be better than a public writable attribute?

**Answer:** When reads/writes need validation, computation, controlled mutation, or a stable behavior boundary.

## 4. What is an invariant?

**Answer:** A condition that should remain true for a valid object state.

## 5. Does abstraction require ABC?

**Answer:** No. Functions, modules, duck typing, `Protocol`, ABCs, and other boundaries can provide abstraction.

## 6. What is duck typing?

**Answer:** Using an object based on the behavior it provides rather than requiring a particular nominal type relationship.

## 7. What is the main architectural value of dependency injection?

**Answer:** It makes dependencies explicit and replaceable by allowing them to be supplied from outside.

## 8. What is composition?

**Answer:** Building a larger object/system from smaller collaborating objects.

## 9. Why does a composition root exist?

**Answer:** To assemble concrete implementations at an application boundary rather than scattering object construction throughout the business logic.

## 10. A `Service` creates a real database client inside `__init__`. What concern should you investigate?

**Answer:** Coupling and dependency ownership. The service may be harder to test and replace because infrastructure construction is embedded inside it.

## 11. When can inheritance be appropriate?

**Answer:** When there is a genuine subtype relationship, the implementation is behaviorally substitutable, shared behavior is stable, and the hierarchy remains simple and intentional.

## 12. Can composition be over-engineered?

**Answer:** Yes. Too many tiny collaborators or deeply nested object graphs can increase cognitive and construction complexity.

## 13. Why should a fake respect the abstraction contract?

**Answer:** Otherwise tests can pass against behavior that production implementations would not provide, creating false confidence.

## 14. What is the difference between information hiding and security?

**Answer:** Information hiding reduces unnecessary implementation knowledge and coupling. Security controls access and protects assets. Information hiding does not replace security.

## 15. When might a function be better than a class?

**Answer:** When the behavior is stateless, straightforward, and does not benefit from an object identity, lifecycle, persistent state, or collaboration boundary.

## 16. What is the relationship among encapsulation, abstraction, and composition?

**Answer:**

```text
Encapsulation -> boundary and controlled state/behavior
Abstraction   -> simplified contract / reduced unnecessary knowledge
Composition   -> collaboration among components
```

A production system can use all three at once.

---

# 53. Glossary

| Term | Meaning |
|---|---|
| **Abstraction** | A simplified contract exposing needed behavior while hiding unnecessary implementation detail. |
| **Abstract Base Class (ABC)** | A Python class mechanism for expressing abstract behavior and restricting instantiation of incomplete subclasses. |
| **Abstract method** | A method declared as required for a concrete subclass, commonly using `@abstractmethod`. |
| **Behavior** | What an object or function does. |
| **Boundary** | A deliberate point separating responsibilities, state, or dependencies. |
| **Composition** | Building a larger object/system from smaller collaborating objects. |
| **Composition root** | Application boundary where concrete dependencies are assembled. |
| **Contract** | The behavior or interface that consumers can rely on. |
| **Delegation** | Giving a collaborator responsibility for work that belongs to its domain. |
| **Dependency injection** | Supplying dependencies from outside a component instead of forcing the component to construct them. |
| **Duck typing** | Using objects according to the behavior they support rather than a required nominal class relationship. |
| **Encapsulation** | Bounding state/behavior and controlling how that state is accessed or changed. |
| **Information hiding** | Reducing unnecessary knowledge of implementation details to limit coupling. |
| **Invariant** | A condition that must remain true for a valid object state. |
| **Name mangling** | Python's transformation of double-leading-underscore attribute names within classes. |
| **Object** | A runtime entity combining state and behavior. |
| **Ownership** | Responsibility for a dependency or resource's existence and lifecycle. |
| **Property** | Attribute-style access backed by getter/setter/deleter behavior. |
| **Protocol** | A structural typing contract describing required operations. |
| **Public API** | The supported interface consumers are expected to use. |
| **State** | Data representing an object's current condition. |
| **Test double** | A replacement for a real dependency used for controlled testing. |
| **Visibility convention** | Python naming style communicating public or internal intent without strict access enforcement. |
| **`_internal`** | A Python convention meaning an attribute or method is intended for internal use. |
| **`__name`** | A name subject to class-based name mangling. |

---

# 54. Final Mental Model

Remember the chapter as a sequence of engineering questions:

```text
1. WHAT STATE EXISTS?
        |
        v
2. WHO OWNS THAT STATE?
        |
        v
3. WHAT BEHAVIOR SHOULD CONTROL IT?
        |
        v
4. WHAT INVARIANTS MUST HOLD?
        |
        v
5. WHAT SHOULD CLIENTS KNOW?
        |
        v
6. WHAT SHOULD THEY NOT NEED TO KNOW?
        |
        v
7. WHAT DEPENDENCIES DOES THE COMPONENT NEED?
        |
        v
8. WHO ASSEMBLES THOSE DEPENDENCIES?
        |
        v
9. CAN COLLABORATORS BE REPLACED WHEN NEEDED?
        |
        v
10. CAN THE DESIGN BE TESTED AND DEBUGGED?
```

And the three core concepts:

```text
                 OBJECT
                   |
          +--------+--------+
          |                 |
        STATE             BEHAVIOR
          |                 |
          +--------+--------+
                   |
                BOUNDARY
                   |
        +----------+----------+
        |          |          |
        v          v          v
   ENCAPSULATION ABSTRACTION COMPOSITION
        |          |          |
        |          |          |
        v          v          v
 control state   expose    combine
 and behavior   required   collaborators
 protect        contract
 invariants     hide detail
```

A production-oriented mental model is:

```text
Domain state
   |
   v
Encapsulation
   |
   v
Valid behavior + invariants
   |
   v
Abstraction boundaries
   |
   v
Explicit dependencies
   |
   v
Composition root
   |
   v
Collaborating components
   |
   v
Tests + debugging + observability
```

The deepest lesson is not:

```text
Use classes.
```

It is:

```text
Create clear boundaries around responsibility,
state, behavior, and dependencies.
```

---

# 55. Final Self-Review

Before considering this chapter complete, verify:

1. Encapsulation is explained from beginner to advanced.
2. Abstraction is explained from beginner to advanced.
3. Composition is explained from beginner to advanced.
4. The differences among all three are explicit.
5. Python does not get incorrectly described as having strict private fields.
6. Name mangling is described accurately.
7. Properties, getters, setters, and deleters are explained.
8. The `property()` API and its main arguments are explained.
9. Invariants are tied to controlled mutation.
10. Mutable collection exposure is discussed with trade-offs.
11. Encapsulation is distinguished from security.
12. Functions are presented as valid abstractions.
13. Duck typing is explained.
14. ABC and `abstractmethod` are explained.
15. Modern decorator combinations are shown.
16. Legacy abstract decorator aliases are contextualized without recommending outdated patterns.
17. ABC is distinguished from Protocol and duck typing.
18. `Protocol` is connected to architecture and testing.
19. Dependency injection is explained without requiring a framework.
20. Composition and delegation are explained.
21. Composition root is explained.
22. Dependency ownership and lifecycle are explained.
23. Resource management is connected to composition.
24. Loose coupling is explained without claiming zero coupling is possible.
25. Single Responsibility is connected to composition without forcing excessive class decomposition.
26. E-commerce, banking, and Applied AI examples are included.
27. LLM application architecture is included without requiring credentials.
28. Agentic AI is connected to OOP without becoming a separate agent-engineering chapter.
29. Abstract data types and information hiding are explained.
30. Public API vs internal implementation is explained.
31. Immutability is discussed as a trade-off.
32. Dataclass use is connected only at a minimal level.
33. Functional-style programming is connected without replacing the chapter's OOP focus.
34. Composition vs inheritance is treated as a nuanced engineering decision.
35. Substitutability/Liskov connection is explained without turning into a complete SOLID chapter.
36. At least 20 progressive exercises are included.
37. Every exercise contains the required problem, requirements, solution, explanation, and common mistake.
38. A dedicated debugging lab is included.
39. The debugging lab covers flawed encapsulation, properties, abstraction, dependency injection, composition, test doubles, and over-engineering.
40. A complete mini-project is included.
41. Testing connections are demonstrated with pytest-compatible examples.
42. Debugging connections are demonstrated.
43. Production architecture questions are included.
44. Interview questions progress from beginner to advanced.
45. A production checklist is included.
46. A final knowledge check includes immediate answers.
47. A glossary is included.
48. The final mental model ties the concepts together.
49. No unnecessary third-party dependencies are introduced.
50. No real credentials or secrets are included.
51. Code examples are written as valid Python where presented as runnable code.
52. Illustrative architecture diagrams are clearly conceptual.
53. "Composition is always better" is not taught.
54. "More classes mean better architecture" is not taught.
55. "Dependency injection requires a framework" is not taught.
56. "Every field needs a getter and setter" is not taught.
57. "Abstraction means abstract classes" is not taught.
58. "Name mangling provides security" is not taught.
59. "Encapsulation means hiding everything" is not taught.
60. The chapter emphasizes simplicity, boundaries, replaceability, testability, and engineering judgment.

## Completion Criteria

You are ready to move forward when you can independently:

```text
model meaningful state
        ↓
define invariants
        ↓
encapsulate state transitions
        ↓
identify the behavior clients actually need
        ↓
choose a suitable abstraction mechanism
        ↓
inject external dependencies where useful
        ↓
compose focused components
        ↓
define ownership and lifecycle
        ↓
write tests around behavior and boundaries
        ↓
debug object interactions
        ↓
refactor without unnecessary architecture
```

The goal is not to use more OOP.

The goal is to use encapsulation, abstraction, and composition when they make the system clearer, safer to change, easier to test, and easier to operate.
