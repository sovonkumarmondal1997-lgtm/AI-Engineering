# Protocols, Interfaces, and Dependency Inversion

## 1. Learning Objectives

By the end of this chapter you should be able to explain and apply:

- abstractions, interfaces, contracts, implementations, dependencies, and coupling;
- tight versus loose coupling;
- duck typing, structural typing, and nominal typing;
- `typing.Protocol`, `@runtime_checkable`, protocol inheritance, generic protocols, callable protocols, method protocols, attribute protocols, and property protocols;
- abstract base classes with `ABC` and `abstractmethod`;
- interface segregation and consumer-focused contracts;
- Dependency Inversion Principle (DIP);
- Dependency Injection (DI), constructor injection, function/parameter injection, method injection, factory injection, and configuration injection;
- Inversion of Control (IoC), composition roots, dependency graphs, and adapters;
- ports-and-adapters / hexagonal architecture and its connection to Clean Architecture;
- testability using fakes, stubs, mocks, and spies;
- production boundaries for repositories, gateways, clients, adapters, data sources, model providers, LLMs, tools, and memory;
- when Protocol is useful and when it is unnecessary.

The final skill is not merely writing a Protocol. It is deciding:

> **Why does this abstraction exist, who should depend on whom, and where should concrete implementation details live?**

---

## 2. Prerequisites

You should already understand:

- variables and functions;
- classes, objects, `self`, and `__init__`;
- instance and class attributes;
- encapsulation and properties;
- inheritance and polymorphism;
- dataclasses and basic data modelling;
- basic testing with `pytest`.

A quick refresh:

```python
class UserService:
    def save(self, repository, user) -> None:
        repository.save(user)
```

The service depends on a `repository` capability. This chapter explains how to make that relationship explicit, flexible, and maintainable.

---

# BASIC

## 3. Start With a Real Problem: Tight Coupling

Start with the problem, not with `Protocol`.

```python
class EmailSender:
    def send(self, message: str) -> None:
        print(f"Sending email: {message}")


class OrderService:
    def __init__(self) -> None:
        self.sender = EmailSender()

    def place_order(self) -> None:
        self.sender.send("Order placed")
```

### What happens?

Creating `OrderService` creates `EmailSender`.

```text
OrderService
    |
    +---- creates ----> EmailSender
```

### Why is this tightly coupled?

The high-level order logic knows:

- the concrete sender class;
- how that sender is constructed;
- that email is the chosen delivery mechanism.

Suppose tomorrow the application needs:

```text
Email
SMS
Push
Webhook
Fake test sender
```

The service must change whenever that implementation decision changes.

### Testing problem

A unit test for order placement now constructs the sender automatically. If the sender eventually calls an external service, the test has unintentionally acquired an infrastructure dependency.

### Architectural question

Ask:

> Does `OrderService` need an `EmailSender`, or does it need a capability such as `send(message)`?

That distinction motivates the rest of this chapter.

---

## 4. What Is a Dependency?

A **dependency** is something a component needs in order to perform its work.

Examples:

- another object;
- a function;
- a database;
- an API client;
- a file system;
- a queue publisher;
- a clock;
- configuration;
- a repository;
- a model client;
- an embedding service;
- a vector store;
- a tool executor.

Example:

```python
class OrderService:
    def __init__(self, repository) -> None:
        self.repository = repository
```

Here `repository` is a dependency.

### Dependency ownership

Ask:

```text
Who creates it?
Who owns it?
How long does it live?
Who closes it?
Can it be replaced?
Can it be shared safely?
```

These questions matter because construction and lifetime are architectural responsibilities.

---

## 5. What Is Coupling?

**Coupling** describes how one component depends on another.

Some coupling is normal and necessary.

A system cannot work without dependencies:

```text
service -> repository
service -> clock
service -> model client
```

### Tight coupling

```python
class OrderService:
    def __init__(self) -> None:
        self.repository = PostgresOrderRepository()
```

The service directly controls a concrete infrastructure choice.

### Loose coupling

```python
class OrderService:
    def __init__(self, repository) -> None:
        self.repository = repository
```

The service still depends on something that provides repository behavior, but the concrete choice is supplied from outside.

### What loose coupling does not mean

It does not mean:

> no dependencies.

It means:

> **dependencies are controlled around useful boundaries.**

### Why it matters

Controlled coupling can improve:

- changeability;
- testability;
- maintainability;
- extensibility;
- integration isolation;
- deployment flexibility.

---

## 6. What Is an Interface?

A simple analogy is a power socket.

The socket defines how a device connects. The device does not need to know how the power station is implemented.

In software:

> An **interface** describes what a component promises to provide to a consumer.

An interface may describe:

- operations;
- inputs;
- outputs;
- expected errors;
- side effects;
- invariants;
- semantic behavior.

Python has no single mandatory `interface` keyword.

Python can express interface-like contracts through:

- duck typing;
- `Protocol`;
- abstract base classes;
- callable types;
- ordinary functions;
- documentation;
- type annotations.

---

## 7. Interface vs Implementation

Think:

```text
INTERFACE
    = what capability is promised

IMPLEMENTATION
    = how that capability is provided
```

Example:

```python
class EmailSender:
    def send(self, message: str) -> None:
        print(f"Email: {message}")
```

The useful application-level capability may simply be:

```text
send(message)
```

Possible implementations:

```python
class EmailSender:
    def send(self, message: str) -> None:
        print(f"Email: {message}")


class SmsSender:
    def send(self, message: str) -> None:
        print(f"SMS: {message}")


class PushSender:
    def send(self, message: str) -> None:
        print(f"Push: {message}")
```

The business caller should not need to understand SMTP, carrier APIs, push gateways, or SDK internals if all it needs is the sending capability.

---

## 8. What Is a Contract?

A **contract** is the set of expectations between a consumer and an implementation.

For example:

```python
def send(message: str) -> bool:
    ...
```

communicates:

- method name: `send`;
- parameter: `message`;
- expected parameter type: `str`;
- expected return type: `bool`.

But a production contract may also specify:

```text
input:
    non-empty message

output:
    True means accepted

errors:
    ValueError for invalid message

side effects:
    one notification is attempted

reliability:
    retries may occur according to documented policy
```

### Important

Python type annotations describe part of a contract. They do not automatically enforce all runtime behavior or semantics.

---

## 9. Duck Typing

Duck typing is behavior-oriented programming.

The informal idea is:

> **If an object provides the operation I need, I can often use it without requiring a particular nominal class.**

Example:

```python
class EmailSender:
    def send(self, message: str) -> None:
        print(f"Email: {message}")


class SmsSender:
    def send(self, message: str) -> None:
        print(f"SMS: {message}")


def notify(sender, message: str) -> None:
    sender.send(message)


notify(EmailSender(), "Hello")
notify(SmsSender(), "Hello")
```

### Step-by-step

1. `notify()` receives an object.
2. It attempts `sender.send(...)`.
3. Python performs ordinary attribute lookup.
4. The concrete method is called.

No inheritance relationship is required.

### Benefits

- simple;
- flexible;
- natural for Python;
- minimal nominal coupling.

### Risks

The contract can be less visible, and errors may appear only at runtime without static typing.

---

## 10. Structural Typing vs Nominal Typing

### Nominal typing

Compatibility is based on explicit type relationships such as inheritance.

```python
class Animal:
    pass


class Dog(Animal):
    pass
```

`Dog` is nominally related to `Animal`.

### Structural typing

Compatibility is based on whether the required structure is present.

```text
required capability
       ↑
class A

required capability
       ↑
class B
```

The classes need not share a base class.

### Protocol connection

`typing.Protocol` lets static type checkers express structural subtyping.

### Important distinction

Structural compatibility is not semantic correctness.

A class can have the right method name and still:

- return the wrong result;
- perform the wrong side effect;
- violate an invariant;
- be unsafe under concurrency.

---

## 11. Introduce `Protocol`

Now the problem has enough context to introduce the solution.

```python
from typing import Protocol


class MessageSender(Protocol):
    def send(self, message: str) -> None:
        ...
```

Implementations:

```python
class EmailSender:
    def send(self, message: str) -> None:
        print(f"Email: {message}")


class SmsSender:
    def send(self, message: str) -> None:
        print(f"SMS: {message}")
```

Consumer:

```python
def notify(sender: MessageSender, message: str) -> None:
    sender.send(message)
```

### Why does this help?

The type annotation communicates:

> `notify()` needs anything compatible with `MessageSender`.

The concrete classes do not have to inherit from the Protocol.

### Core mental model

```text
Protocol
   ↓
required shape/behavior
   ↑
+--+---------+---------+
|            |         |
Email       SMS       Fake
```

---

## 12. Protocol Internal Mental Model

A Protocol is mainly a **typing/design contract**.

Think in three layers:

```text
Protocol compatibility
        ↓
Does the type have the required members?

Runtime behavior
        ↓
Will the actual call execute?

Semantic correctness
        ↓
Does the implementation satisfy the intended contract?
```

A Protocol helps with the first layer, especially during static analysis.

A normal call exercises the second layer.

Tests, documentation, validation, and integration behavior address the third.

### What Protocol does not mean

It does not mean:

- runtime enforcement for every call;
- automatic validation of return values;
- automatic verification of side effects;
- proof of reliability or correctness.

---

## 13. Protocol Methods

A method Protocol:

```python
from typing import Protocol


class Logger(Protocol):
    def log(self, message: str) -> None:
        ...
```

Implementations:

```python
class ConsoleLogger:
    def log(self, message: str) -> None:
        print(message)


class MemoryLogger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def log(self, message: str) -> None:
        self.messages.append(message)
```

Consumer:

```python
def record(logger: Logger, message: str) -> None:
    logger.log(message)
```

### Static checking

A type checker can verify that the implementation provides a compatible `log` method.

### Runtime

Python simply executes the concrete method.

### Behavioral contract

A type checker cannot prove that the logger:

- actually writes to a durable destination;
- never drops records;
- is thread-safe;
- preserves message order.

Those are separate requirements.

---

## 14. Protocol Attributes

Protocols can describe attributes.

```python
from typing import Protocol


class HasName(Protocol):
    name: str
```

Implementation:

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name
```

Consumer:

```python
def greet(user: HasName) -> str:
    return f"Hello, {user.name}"
```

### Attribute mutability matters

A protocol attribute:

```python
name: str
```

can express a writable attribute requirement.

If a consumer only needs read access, a property contract can be clearer:

```python
class Identifiable(Protocol):
    @property
    def identifier(self) -> str:
        ...
```

---

## 15. Protocols With Properties

```python
from typing import Protocol


class Identifiable(Protocol):
    @property
    def identifier(self) -> str:
        ...
```

Implementation:

```python
class User:
    def __init__(self, user_id: str) -> None:
        self._user_id = user_id

    @property
    def identifier(self) -> str:
        return self._user_id
```

A different class can expose a normal attribute if it satisfies the static contract:

```python
class Record:
    def __init__(self, record_id: str) -> None:
        self.identifier = record_id
```

### Why this matters

The consumer gets a stable read interface while implementation details remain private to the implementation.

---

## 16. Protocol Inheritance

Small capabilities can be combined.

```python
from typing import Protocol


class Reader(Protocol):
    def read(self) -> str:
        ...


class Writer(Protocol):
    def write(self, data: str) -> None:
        ...


class ReaderWriter(Reader, Writer, Protocol):
    pass
```

A consumer can still depend on only `Reader` or only `Writer`.

### Why this is useful

It supports interface segregation:

```text
Reader capability
Writer capability
       ↓
combined capability where needed
```

Avoid giant contracts when consumers need only small capabilities.

---

## 17. Protocol Composition

You do not always need protocol inheritance.

A function can require separate capabilities:

```python
from typing import Protocol


class Identifiable(Protocol):
    @property
    def identifier(self) -> str:
        ...


class Logger(Protocol):
    def log(self, message: str) -> None:
        ...


def process(item: Identifiable, logger: Logger) -> None:
    logger.log(item.identifier)
```

This communicates two independent dependencies.

### Why useful?

It avoids inventing a large combined interface when the consumer can explicitly accept two small capabilities.

---

## 18. Generic Protocols

A generic Protocol can preserve type relationships.

```python
from typing import Protocol, TypeVar


T = TypeVar("T")


class Repository(Protocol[T]):
    def get(self, key: str) -> T | None:
        ...

    def save(self, item: T) -> None:
        ...
```

A repository for `User` can conceptually be treated as:

```text
Repository[User]
```

### Why generics?

Without a type parameter, the relationship between `get()` and `save()` is less precise.

With `Repository[T]`:

```text
get() -> T | None
save(item: T)
```

The type checker can preserve that relationship.

### Modern versus legacy syntax

Modern Python releases support newer generic syntax. For broad compatibility, the `TypeVar` form above also remains useful.

Use the syntax supported by the project's minimum Python version.

---

## 19. Callable Protocols

Sometimes the dependency is simply something callable.

```python
from typing import Protocol


class Predictor(Protocol):
    def __call__(self, text: str) -> float:
        ...
```

A function can satisfy the behavior:

```python
def score_text(text: str) -> float:
    return len(text) / 100.0
```

A callable object can also satisfy it:

```python
class LengthPredictor:
    def __call__(self, text: str) -> float:
        return len(text) / 100.0
```

Consumer:

```python
def classify(predictor: Predictor, text: str) -> float:
    return predictor(text)
```

### Why useful in AI systems?

Inference may be represented by:

- a function;
- a local model wrapper;
- a remote prediction client;
- a deterministic test implementation.

Do not create a class when a callable is the better abstraction.

---

## 20. `@runtime_checkable`

Most Protocol value comes from static typing.

Sometimes you also need a runtime capability check.

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Closable(Protocol):
    def close(self) -> None:
        ...


class Resource:
    def close(self) -> None:
        print("closed")


resource = Resource()
print(isinstance(resource, Closable))
```

Expected output:

```text
True
```

### What does `@runtime_checkable` do?

It allows runtime use of supported structural checks through:

```python
isinstance(obj, Closable)
```

and supported `issubclass()` checks.

### What does it NOT do?

It does not fully validate:

- signatures;
- annotations;
- return types;
- semantics;
- side effects;
- correctness.

A runtime check is not a replacement for a type checker or tests.

---

## 21. Runtime Protocol Limitations

Consider:

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Sender(Protocol):
    def send(self, message: str) -> None:
        ...


class WrongSender:
    def send(self, message: int) -> list[int]:
        return [message]
```

A runtime structural check focuses on the presence of `send`, not complete signature/type correctness.

### Correct diagnostic strategy

Use:

```text
static type checker
      +
unit/contract tests
      +
integration tests
```

rather than:

```text
runtime_checkable alone
```

### Performance note

Runtime Protocol checks can be more expensive than ordinary class checks. Avoid placing them in a hot loop without a reason and measurement.

---

## 22. `isinstance()` and `issubclass()` With Protocol

A runtime-checkable method protocol can be used in a runtime check:

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Closable(Protocol):
    def close(self) -> None:
        ...


class Resource:
    def close(self) -> None:
        pass


assert isinstance(Resource(), Closable)
```

`issubclass()` asks a class-level question:

```python
issubclass(Resource, Closable)
```

Runtime structural checks have limitations, especially for protocols with non-method members because an instance attribute may not be represented as a class attribute.

### Practical rule

Use `isinstance()` only when a runtime capability check is genuinely needed.

Use static Protocol typing for normal application contracts.

---

## 23. Protocol Introspection APIs

Modern Python provides public typing introspection helpers in recent versions, including APIs such as:

```python
from typing import Protocol, get_protocol_members, is_protocol


class Named(Protocol):
    name: str


print(is_protocol(Named))
print(get_protocol_members(Named))
```

### Why use these?

They are useful for tooling, diagnostics, schema/introspection utilities, and framework code.

You may also encounter internal attributes such as:

```text
_is_protocol
__protocol_attrs__
```

Do not make application architecture depend on private/internal names. Prefer documented public APIs when available.

---

## 24. Abstract Base Classes

Python also supports nominal abstract classes.

```python
from abc import ABC, abstractmethod


class MessageSender(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        ...
```

Implementation:

```python
class EmailSender(MessageSender):
    def send(self, message: str) -> None:
        print(f"Email: {message}")
```

### Why use an ABC?

An ABC is useful when:

- the nominal hierarchy matters;
- runtime abstractness is useful;
- shared implementation belongs in the base;
- the family of types has meaningful common identity.

### `abstractmethod`

It marks a method as abstract. A normal subclass must implement all required abstract members before it can be instantiated.

---

## 25. ABC With Shared Implementation

ABCs can contain concrete methods as well as abstract ones.

```python
from abc import ABC, abstractmethod


class BaseExporter(ABC):
    @abstractmethod
    def export(self, data: str) -> str:
        ...

    def add_header(self, data: str) -> str:
        return f"HEADER\n{data}"
```

Implementation:

```python
class CsvExporter(BaseExporter):
    def export(self, data: str) -> str:
        return self.add_header(data)
```

### Trade-off

Shared implementation can remove duplication.

It also creates coupling to the base class.

Use it when the common behavior genuinely belongs to the abstraction.

---

## 26. Abstract Methods May Have Implementations

This is valid:

```python
from abc import ABC, abstractmethod


class Processor(ABC):
    @abstractmethod
    def process(self, value: str) -> str:
        return value.strip()
```

Subclass:

```python
class LowerProcessor(Processor):
    def process(self, value: str) -> str:
        cleaned = super().process(value)
        return cleaned.lower()
```

The abstract status means a concrete implementation is still required; it does not mean the method body must be empty.

This can be useful in cooperative designs.

---

## 27. ABC Decorator Combinations

Modern Python supports combinations such as:

```python
from abc import ABC, abstractmethod


class Factory(ABC):
    @classmethod
    @abstractmethod
    def create(cls):
        ...
```

Static method:

```python
class Utility(ABC):
    @staticmethod
    @abstractmethod
    def normalize(value: str) -> str:
        ...
```

Property:

```python
class Entity(ABC):
    @property
    @abstractmethod
    def identifier(self) -> str:
        ...
```

When combining `abstractmethod` with another descriptor, it should be the innermost decorator.

Legacy aliases such as `abstractclassmethod`, `abstractstaticmethod`, and `abstractproperty` are deprecated/redundant for new code because the ordinary descriptors now support `abstractmethod` correctly.

---

## 28. Protocol vs ABC — Detailed Comparison

| Concern | Protocol | ABC |
|---|---|---|
| Main relationship | Structural | Nominal |
| Inheritance required | No for structural compatibility | Usually yes for ordinary subclassing |
| Static typing | Strong | Strong |
| Runtime abstractness | No by itself | Yes |
| Shared implementation | Not its primary purpose | Strong use case |
| Third-party compatibility | Very convenient | Often needs subclassing or registration |
| Runtime checking | With `@runtime_checkable`, limited | Normal class checks |
| Signature validation at runtime | No | No full validation |
| Domain hierarchy | Less focused on it | Strong fit |
| Test doubles | Excellent | Excellent |
| Coupling | Often lower | Can be higher |

Neither mechanism is universally better.

Ask what the system actually needs.

---

## 29. Duck Typing vs Protocol vs ABC

| Dimension | Duck typing | Protocol | ABC |
|---|---|---|---|
| Main idea | Behavior at runtime | Structural contract for typing | Nominal abstract family |
| Explicit contract | Often implicit | Explicit | Explicit |
| Inheritance | Not needed | Not needed | Usually used |
| Static checking | Optional | Strong | Strong |
| Runtime check | Actual calls | Optional limited check | Nominal runtime behavior |
| Shared implementation | No requirement | Not primary | Strong fit |
| Flexibility | High | High | Moderate to high |
| Best fit | Small/simple behavior | Typed boundaries | Controlled class family |

### Same consumer, three styles

Duck typing:

```python
def notify(sender, message: str) -> None:
    sender.send(message)
```

Protocol:

```python
class Sender(Protocol):
    def send(self, message: str) -> None:
        ...


def notify(sender: Sender, message: str) -> None:
    sender.send(message)
```

ABC:

```python
class Sender(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        ...


def notify(sender: Sender, message: str) -> None:
    sender.send(message)
```

The runtime call looks similar, but the design and typing model are different.

---

## 30. Interface Segregation

A giant interface creates unnecessary dependency surface.

Bad:

```python
class Storage(Protocol):
    def read(self, key: str) -> str:
        ...

    def write(self, key: str, value: str) -> None:
        ...

    def delete(self, key: str) -> None:
        ...

    def backup(self) -> None:
        ...

    def replicate(self) -> None:
        ...

    def encrypt(self) -> None:
        ...
```

A reader only needs:

```python
class Reader(Protocol):
    def read(self, key: str) -> str:
        ...
```

A writer only needs:

```python
class Writer(Protocol):
    def write(self, key: str, value: str) -> None:
        ...
```

### Why this helps

Consumers depend only on capabilities they actually use.

That can improve:

- testing;
- implementation flexibility;
- change isolation;
- readability.

### Important nuance

Interface size is not judged by a magic number. It is judged by consumer needs and semantic cohesion.

# DEPENDENCY INVERSION AND INJECTION

## 31. Dependency Inversion Principle

The **Dependency Inversion Principle (DIP)** says, in practical terms:

> High-level policy should not depend directly on low-level implementation details. Both should depend on abstractions where an abstraction is useful.

A related formulation is:

> Details should depend on abstractions rather than forcing abstractions to depend on details.

### Bad direction

```text
High-Level Business Logic
          |
          v
   Concrete Database
```

Example:

```python
class OrderService:
    def __init__(self) -> None:
        self.repository = PostgresOrderRepository()
```

### Better direction

```text
High-Level Business Logic
          |
          v
      Abstraction
          ^
          |
 Concrete Implementation
```

Example:

```python
class OrderService:
    def __init__(self, repository) -> None:
        self.repository = repository
```

with an abstraction:

```python
from typing import Protocol


class OrderRepository(Protocol):
    def save(self, order) -> None:
        ...
```

### What does "inversion" mean?

The important change is the dependency direction:

```text
Before:
policy → detail

After:
policy → abstraction ← detail
```

The concrete implementation still exists. Its knowledge is simply moved to an appropriate outer layer.

### Do not reduce DIP to

> "Always use interfaces."

DIP is about dependency direction and stable abstractions, not about creating maximum numbers of interfaces.

---

## 32. Dependency Direction

Consider:

```python
class PostgresRepository:
    def save(self, order) -> None:
        print("save to database")


class OrderService:
    def __init__(self) -> None:
        self.repository = PostgresRepository()
```

The service directly depends on PostgreSQL implementation details.

A more decoupled design is:

```python
from typing import Protocol


class OrderRepository(Protocol):
    def save(self, order) -> None:
        ...


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self.repository = repository
```

Concrete infrastructure:

```python
class PostgresOrderRepository:
    def save(self, order) -> None:
        print("save to PostgreSQL")
```

### Dependency picture

```text
OrderService
     |
     v
OrderRepository Protocol
     ^
     |
PostgresOrderRepository
```

### What improved?

The service now needs only the repository capability.

It does not need to know:

- which database is used;
- which driver is used;
- how SQL is executed;
- how connections are configured.

---

## 33. Dependency Injection

**Dependency Injection (DI)** means supplying a component with dependencies rather than making that component construct them internally.

### Constructor injection

```python
class OrderService:
    def __init__(self, repository) -> None:
        self.repository = repository
```

### Function/parameter injection

```python
def generate_report(data, formatter):
    return formatter(data)
```

### Method injection

```python
class ReportService:
    def generate(self, data, formatter):
        return formatter(data)
```

### Factory injection

```python
class ClientFactory(Protocol):
    def create(self):
        ...
```

### Configuration injection

```python
class APIClient:
    def __init__(self, base_url: str, timeout: int) -> None:
        self.base_url = base_url
        self.timeout = timeout
```

### Critical distinction

```text
DIP = architectural principle
DI  = implementation technique
```

A dependency injection framework is optional.

---

## 34. Constructor Injection

Constructor injection is often the simplest DI form.

```python
class OrderService:
    def __init__(self, repository) -> None:
        self.repository = repository
```

Wiring:

```python
repository = PostgresOrderRepository()
service = OrderService(repository)
```

Testing:

```python
repository = InMemoryOrderRepository()
service = OrderService(repository)
```

### Why useful?

Dependencies become:

- visible;
- inspectable;
- replaceable;
- part of object construction.

### Lifecycle

The code that constructs the repository can decide whether it is:

- one application-wide object;
- one worker object;
- one request object;
- a factory-created object.

The service does not have to own that decision.

### Trade-off

If a constructor requires a very large number of dependencies, investigate class responsibility before adding a more sophisticated DI system.

---

## 35. Function / Parameter Injection

Sometimes a function is a better unit of abstraction than a class.

```python
def generate_report(data, formatter):
    return formatter(data)
```

Formatter:

```python
def format_text(data) -> str:
    return str(data)
```

Use:

```python
print(generate_report({"count": 3}, format_text))
```

### Why is this useful?

The dependency is:

- temporary;
- stateless;
- algorithmic.

A class hierarchy would add unnecessary machinery.

### Functional-style connection

Explicit parameters are a natural dependency-injection mechanism:

```text
input + explicit dependency → result
```

This can reduce hidden global state.

---

## 36. Method Injection

Method injection supplies a dependency only for one operation.

```python
class ReportService:
    def generate(self, data, formatter):
        return formatter(data)
```

### Good fit

Use this style when:

- the dependency is temporary;
- different calls may use different implementations;
- the service does not need to retain the collaborator.

### Trade-off

If every method repeatedly receives the same dependency:

```python
service.generate(data, formatter)
service.preview(data, formatter)
service.export(data, formatter)
```

then a constructor dependency may be clearer.

---

## 37. Factory Injection

A factory is a component that creates other components.

```python
from typing import Protocol


class Client:
    pass


class ClientFactory(Protocol):
    def create(self) -> Client:
        ...
```

A service can depend on the factory:

```python
class JobRunner:
    def __init__(self, factory: ClientFactory) -> None:
        self.factory = factory

    def run(self) -> Client:
        return self.factory.create()
```

### Why use a factory?

A factory is useful when creation depends on:

- configuration;
- environment;
- resource lifecycle;
- request context;
- lazy initialization;
- implementation selection.

### Testing

```python
class FakeClientFactory:
    def create(self) -> Client:
        return Client()
```

The job runner does not need to know how clients are assembled.

---

## 38. Configuration Injection

Configuration is itself a dependency.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ClientConfig:
    base_url: str
    timeout_seconds: int = 30
    max_retries: int = 3
```

Inject it:

```python
class APIClient:
    def __init__(self, config: ClientConfig) -> None:
        self.config = config
```

### Why useful?

Configuration becomes:

- explicit;
- typed;
- testable;
- reusable;
- optionally immutable.

### Production lesson

Avoid hiding every configuration decision in a module-level global or environment lookup scattered through business logic.

Load configuration at an appropriate outer boundary, construct the model, and inject it.

---

## 39. Inversion of Control

Three terms must remain distinct.

### Dependency Inversion Principle

An architectural principle about dependency direction.

```text
policy → abstraction ← detail
```

### Dependency Injection

A technique for supplying dependencies.

```python
Service(repository)
```

### Inversion of Control

A broader idea in which a component gives up some control over object creation, lifecycle, or execution flow to another component/framework.

### Example

A framework may create your controller and call a lifecycle method:

```text
Framework
   ↓ creates
Controller
   ↓ calls
handle_request()
```

You did not call the controller from the framework's internal event loop; the framework controls the lifecycle.

### Relationship

```text
DIP → what dependency direction should look like
DI  → one way to supply dependencies
IoC → broader transfer of control
```

Do not use them as exact synonyms.

---

## 40. Composition Root

The **composition root** is the application location where concrete objects are assembled.

Example:

```python
repository = PostgresOrderRepository()
gateway = PaymentAPIAdapter(ExternalPaymentAPI())
notifier = EmailSender()

service = OrderService(
    repository=repository,
    gateway=gateway,
    notifier=notifier,
)
```

### Why centralize wiring?

It prevents business logic from becoming construction logic.

```text
Application startup
       |
       +--> create concrete infrastructure
       |
       +--> inject dependencies
       |
       v
Business/application graph
```

### What belongs in the composition root?

- implementation selection;
- environment configuration;
- factories;
- adapters;
- object construction;
- resource setup.

### What should not be hidden there?

Business rules.

The root wires the application; it should not become the place where domain behavior is implemented.

---

## 41. Dependency Graph

Consider:

```text
Application
    |
    v
OrderController
    |
    v
OrderService
    |
    v
OrderRepository Protocol
    ^
    |
PostgresOrderRepository
```

### Read it carefully

`OrderService` depends on the repository capability.

`PostgresOrderRepository` implements that capability.

The composition root creates both and connects them.

### Why diagram dependencies?

It helps identify:

- infrastructure leaking into business logic;
- unexpected cycles;
- oversized services;
- missing boundaries;
- test substitution points.

### Class diagram vs dependency graph

A class diagram asks:

```text
What types exist?
```

A dependency graph asks:

```text
Which component relies on which capability?
```

Both views can be useful.

---

# ADAPTERS AND ARCHITECTURE

## 42. Adapters

An **adapter** converts one interface into another.

Suppose a vendor provides:

```python
class ExternalPaymentAPI:
    def create_payment(self, amount: float) -> bool:
        return amount > 0
```

The application wants:

```python
class PaymentGateway(Protocol):
    def charge(self, amount: float) -> bool:
        ...
```

Adapter:

```python
class PaymentAPIAdapter:
    def __init__(self, client: ExternalPaymentAPI) -> None:
        self.client = client

    def charge(self, amount: float) -> bool:
        return self.client.create_payment(amount)
```

### Why useful?

The adapter contains translation such as:

- method-name differences;
- request-shape conversion;
- response conversion;
- vendor-specific errors;
- authentication setup;
- provider-specific metadata.

### Boundary

```text
Application Port
      ^
      |
    Adapter
      |
      v
Vendor API
```

### Production lesson

The adapter is not "free abstraction." It is a controlled place where external coupling is accepted and isolated.

---

## 43. Port and Adapter Example

```python
from typing import Protocol


class PaymentGateway(Protocol):
    def charge(self, amount: float) -> bool:
        ...


class ExternalPaymentAPI:
    def create_payment(self, amount: float) -> bool:
        return amount > 0


class PaymentAdapter:
    def __init__(self, api: ExternalPaymentAPI) -> None:
        self.api = api

    def charge(self, amount: float) -> bool:
        return self.api.create_payment(amount)


def pay(gateway: PaymentGateway, amount: float) -> bool:
    return gateway.charge(amount)
```

The `PaymentGateway` is the application-facing port.

`PaymentAdapter` translates the external implementation into that port.

---

## 44. Ports and Adapters / Hexagonal Architecture

At a beginner-friendly level:

### Port

An application-facing abstraction describing a boundary.

### Adapter

An implementation that connects that boundary to an external technology.

Diagram:

```text
             External API
                  |
                  v
               Adapter
                  |
                  v
          +----------------+
          |     Port       |
          |    Protocol    |
          +----------------+
                  |
                  v
           Application Core
```

### Why useful?

The application core remains focused on policy while adapters handle:

- HTTP;
- SQL;
- cloud SDKs;
- message brokers;
- storage engines;
- model providers.

### Testing

A fake adapter can satisfy the same port.

### Important

Hexagonal architecture is broader than Protocol. The lesson here is the dependency boundary.

---

## 45. Clean Architecture Connection

Clean Architecture commonly separates responsibilities into areas such as:

```text
Business rules
    ↓
Use cases/application policy
    ↓
Interface adapters
    ↓
Infrastructure details
```

The exact arrangement varies by implementation.

The important connection to this chapter is:

> **Keep higher-level business policy independent from volatile external details when that boundary creates real value.**

Examples:

```text
OrderService
    ↓
OrderRepository
    ↑
Postgres adapter
```

```text
InferenceService
    ↓
Model Protocol
    ↑
Provider adapter
```

DIP provides one of the foundations for these architectures.

---

## 46. Production Boundary Design

A useful production structure is:

```text
                  APPLICATION CORE
                         |
          +--------------+--------------+
          |              |              |
     Repository       Gateway          Clock
      Protocol        Protocol         Protocol
          ^              ^              ^
          |              |              |
     DB Adapter      API Adapter    System Clock
```

### Why this is valuable

The core depends on capabilities.

Infrastructure supplies implementations.

The composition root connects them.

### What this does not solve automatically

You still need:

- retries;
- timeouts;
- observability;
- authorization;
- transactions;
- idempotency;
- data validation;
- resource management.

Abstractions control dependencies; they do not replace engineering of the underlying system.

---

# TESTABILITY

## 47. Testability Through Abstractions

Without injection:

```python
class OrderService:
    def __init__(self) -> None:
        self.repository = PostgresRepository()
```

The unit test may require a database or complex monkeypatching.

With injection:

```python
class OrderService:
    def __init__(self, repository) -> None:
        self.repository = repository
```

Test:

```python
class FakeRepository:
    def __init__(self) -> None:
        self.saved = []

    def save(self, item) -> None:
        self.saved.append(item)
```

Then:

```python
service = OrderService(FakeRepository())
```

### Why useful?

The test can control the dependency.

That makes the test:

- faster;
- deterministic;
- isolated;
- easier to diagnose.

### Important

Not every test needs a fake. Integration tests should test real infrastructure boundaries where appropriate.

---

## 48. Fakes, Stubs, Mocks, and Spies

### Fake

A lightweight working implementation.

```python
class InMemoryRepository:
    def __init__(self) -> None:
        self.items = {}

    def save(self, item) -> None:
        self.items[item.id] = item
```

### Stub

Returns controlled responses.

```python
class FixedClock:
    def now(self) -> str:
        return "2026-01-01"
```

### Mock

A test double configured to simulate/verify interactions, often using `unittest.mock` or another test library.

### Spy

Records calls so tests can inspect interaction history.

### Protocol connection

A Protocol gives the boundary a type-level description:

```python
class Clock(Protocol):
    def now(self) -> str:
        ...
```

The fake need not inherit from it for structural compatibility.

### Do not confuse roles

```text
Protocol → contract
Fake     → lightweight implementation
Mock     → interaction-controlled test double
Test     → verifies behavior
```

---

## 49. Protocols and Mocking

```python
from typing import Protocol


class PaymentGateway(Protocol):
    def charge(self, amount: float) -> bool:
        ...


class FakePaymentGateway:
    def __init__(self, success: bool = True) -> None:
        self.success = success
        self.charged: list[float] = []

    def charge(self, amount: float) -> bool:
        self.charged.append(amount)
        return self.success


class CheckoutService:
    def __init__(self, gateway: PaymentGateway) -> None:
        self.gateway = gateway

    def checkout(self, amount: float) -> bool:
        return self.gateway.charge(amount)
```

Test:

```python
def test_checkout() -> None:
    gateway = FakePaymentGateway()
    service = CheckoutService(gateway)

    assert service.checkout(100.0) is True
    assert gateway.charged == [100.0]
```

### What the Protocol gives us

It makes the intended dependency explicit to humans and static tooling.

### What it does not give us

It does not prove the fake and real gateway have identical business behavior.

That is the purpose of contract and integration tests.

---

## 50. Dependency Injection and Test Isolation

Common replaceable boundaries include:

```text
Database
  Production → Postgres
  Test       → in-memory fake

Clock
  Production → system clock
  Test       → fixed clock

Filesystem
  Production → real filesystem
  Test       → in-memory fake

Queue
  Production → real publisher
  Test       → recording fake

ML model
  Production → remote/local model
  Test       → deterministic fake

LLM
  Production → provider adapter
  Test       → fake client

Embedding service
  Production → real embedding service
  Test       → fixed vector generator

Vector store
  Production → real vector database
  Test       → in-memory fake
```

### Important architecture lesson

Testability is often a consequence of dependency boundaries.

A system with explicit dependencies is easier to replace than a system with hidden construction and global state.

---

# COMMON MISTAKES

## 51. Common Dependency-Injection Mistakes

### Mistake 1 — Creating dependencies internally

Bad:

```python
class Service:
    def __init__(self) -> None:
        self.repository = PostgresRepository()
```

Why problematic:

- hidden dependency;
- hard unit testing;
- infrastructure leakage.

Better:

```python
class Service:
    def __init__(self, repository) -> None:
        self.repository = repository
```

---

### Mistake 2 — Service locator

Bad:

```python
class Service:
    def run(self) -> None:
        repository = global_registry.get("repository")
        repository.save("item")
```

Problems:

- hidden dependencies;
- global state;
- difficult static reasoning;
- hidden setup requirements.

Prefer explicit injection when practical.

---

### Mistake 3 — Hidden global dependencies

Bad:

```python
GLOBAL_CLIENT = RealAPIClient()


class Service:
    def run(self) -> None:
        GLOBAL_CLIENT.call()
```

The class appears dependency-free but is not.

---

### Mistake 4 — Giant interfaces

A service requiring a 30-method Protocol may actually have several distinct responsibilities.

Split based on consumer needs.

---

### Mistake 5 — Unnecessary Protocols

Not every function or class requires a Protocol.

Add one when it creates a useful boundary.

---

### Mistake 6 — Too many constructor parameters

A constructor with many unrelated dependencies may indicate that the class itself is too broad.

Improve responsibility boundaries before reaching for more machinery.

---

### Mistake 7 — Leaking infrastructure types

Bad:

```python
class OrderService:
    def save(self, connection: PostgresConnection) -> None:
        ...
```

Better:

```python
class OrderRepository(Protocol):
    def save(self, order) -> None:
        ...
```

---

### Mistake 8 — Abstracting before variation exists

If there is one tiny implementation and no meaningful boundary, direct code may be clearer.

---

## 52. Common Protocol Mistakes

### Mistake 1 — Protocol when simple duck typing is enough

For a tiny local helper:

```python
def show_name(user) -> str:
    return user.name
```

A Protocol may not add enough value to justify itself.

### Mistake 2 — Giant Protocol

Large Protocols often force consumers to depend on capabilities they do not need.

### Mistake 3 — Protocol contains implementation details

Avoid exposing:

- vendor SDK response types;
- database sessions;
- transport-specific objects;

unless the application contract genuinely requires them.

### Mistake 4 — Assuming Protocol gives runtime enforcement

It does not, by default.

### Mistake 5 — Misunderstanding `runtime_checkable`

It does not validate full signatures or semantic behavior.

### Mistake 6 — Overusing Protocol inheritance

Do not compose Protocols just to create a fashionable hierarchy. Compose capabilities when consumers need them.

### Mistake 7 — Mismatched signatures

A concrete implementation must have compatible typing for static checking.

### Mistake 8 — Confusing structural compatibility with behavioral compatibility

A matching method name is not proof that the implementation has the required semantics.

### Mistake 9 — No variation point

If there is no meaningful implementation boundary, a Protocol may be unnecessary indirection.

---

## 53. When Not to Use Protocol

A Protocol is not automatically required for every component.

### Simple internal code

```python
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b
```

If there is one stable implementation and no useful boundary, a Protocol may add little.

### Trivial functions

```python
def normalize(value: str) -> str:
    return value.strip().lower()
```

Do not create a Protocol for every function.

### Stable local code

Small internal modules often benefit from straightforward dependencies.

### Data-only structures

A dataclass may be clearer:

```python
from dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int
```

### Core rule

> **An abstraction should exist for a reason.**

Useful reasons include:

- multiple implementations;
- external integration boundaries;
- testing;
- plugin architecture;
- independent lifecycle;
- vendor isolation.

---

## 54. When to Use Protocol

Protocols are strong candidates for:

- repositories;
- gateways;
- external API clients;
- data sources;
- model providers;
- LLM clients;
- clocks;
- queue publishers;
- plugin interfaces;
- tool interfaces;
- memory interfaces;
- interchangeable strategies;
- library extension points.

### Example

```python
class Clock(Protocol):
    def now(self):
        ...
```

A production implementation uses the system clock.

A test implementation uses a fixed value.

### Decision question

Ask:

> Is the dependency a meaningful capability that can change independently of the consumer?

If yes, a Protocol may be useful.

---

## 55. Protocol Design Principles

### Small interfaces

Keep the contract focused.

### Consumer-focused

Define what the consumer needs, not the entire provider API.

### Meaningful abstraction

The Protocol should represent a real capability.

### Stable

Avoid volatile vendor details.

### Explicit semantics

Document behavior that types cannot express.

### Composition

Use separate Protocols where multiple capabilities have independent consumers.

### Example

```python
class UserReader(Protocol):
    def get(self, user_id: str):
        ...


class UserWriter(Protocol):
    def save(self, user) -> None:
        ...
```

A read-only consumer can depend only on `UserReader`.

---

## 56. Protocol and Liskov Substitution

A Protocol can describe structural compatibility, but a complete application contract is behavioral.

Suppose:

```python
class Sender(Protocol):
    def send(self, message: str) -> bool:
        ...
```

A concrete implementation might type-check correctly but:

- reject valid messages unexpectedly;
- return the wrong semantic meaning for `True`;
- duplicate side effects;
- violate retry/idempotency requirements.

### Think in layers

```text
TYPE COMPATIBILITY
       ↓
required members and types

BEHAVIORAL COMPATIBILITY
       ↓
semantic contract

OPERATIONAL COMPATIBILITY
       ↓
latency, reliability, security, resources
```

Static typing primarily helps with the first.

Tests and architecture address the others.

---

# REAL-WORLD APPLICATIONS

## 57. Backend Example — Order Repository

Architecture:

```text
HTTP Controller
      ↓
OrderService
      ↓
OrderRepository Protocol
      ↑
PostgresOrderRepository
```

Protocol:

```python
from typing import Protocol


class OrderRepository(Protocol):
    def get(self, order_id: str):
        ...

    def save(self, order) -> None:
        ...
```

In-memory implementation:

```python
class InMemoryOrderRepository:
    def __init__(self) -> None:
        self.orders: dict[str, object] = {}

    def get(self, order_id: str):
        return self.orders.get(order_id)

    def save(self, order) -> None:
        self.orders[order.order_id] = order
```

Service:

```python
class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self.repository = repository

    def place(self, order) -> None:
        self.repository.save(order)
```

### Production lesson

The service owns business policy.

The repository adapter owns persistence mechanics.

---

## 58. Data Engineering Example — Data Source

A data platform may ingest from:

```text
API
File
Database
```

Protocol:

```python
from typing import Protocol


class DataSource(Protocol):
    def fetch(self) -> list[dict[str, object]]:
        ...
```

API implementation:

```python
class APIDataSource:
    def __init__(self, client) -> None:
        self.client = client

    def fetch(self) -> list[dict[str, object]]:
        return self.client.fetch_records()
```

File implementation:

```python
class FileDataSource:
    def __init__(self, path: str) -> None:
        self.path = path

    def fetch(self) -> list[dict[str, object]]:
        return []
```

Fake:

```python
class FakeDataSource:
    def __init__(self, records: list[dict[str, object]]) -> None:
        self.records = records

    def fetch(self) -> list[dict[str, object]]:
        return self.records
```

Pipeline:

```python
def run_pipeline(source: DataSource) -> int:
    return len(source.fetch())
```

### Production lesson

The pipeline depends on ingestion capability, not transport technology.

---

## 59. ML Example — Predictor

Protocol:

```python
from typing import Protocol


class Predictor(Protocol):
    def predict(self, features: list[float]) -> float:
        ...
```

Local:

```python
class LocalPredictor:
    def predict(self, features: list[float]) -> float:
        return sum(features)
```

Remote:

```python
class RemotePredictor:
    def __init__(self, client) -> None:
        self.client = client

    def predict(self, features: list[float]) -> float:
        return self.client.predict(features)
```

Fake:

```python
class FakePredictor:
    def __init__(self, result: float) -> None:
        self.result = result

    def predict(self, features: list[float]) -> float:
        return self.result
```

Consumer:

```python
def score(predictor: Predictor, features: list[float]) -> float:
    return predictor.predict(features)
```

### Production lesson

You can change local versus remote inference without changing the scoring workflow.

---

## 60. LLM Example — Provider Abstraction

Protocol:

```python
from typing import Protocol


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...
```

Provider adapter:

```python
class ProviderAAdapter:
    def __init__(self, client) -> None:
        self.client = client

    def generate(self, prompt: str) -> str:
        return self.client.generate(prompt)
```

Second adapter:

```python
class ProviderBAdapter:
    def __init__(self, client) -> None:
        self.client = client

    def generate(self, prompt: str) -> str:
        return self.client.generate(prompt)
```

Fake:

```python
class FakeLLM:
    def generate(self, prompt: str) -> str:
        return "test-response"
```

Application:

```python
class QASystem:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def answer(self, question: str) -> str:
        return self.client.generate(question)
```

### Architecture

```text
QASystem
   |
   v
LLMClient Protocol
   ^
   |
+--+-------------------+
|          |           |
A adapter  B adapter   Fake
```

### Production lesson

The application can remain provider-neutral while adapters isolate vendor SDKs.

---

## 61. Agentic AI Example — Model, Tool, and Memory Ports

A production-style agent can depend on multiple capabilities.

### Model port

```python
from typing import Protocol


class Model(Protocol):
    def generate(self, prompt: str) -> str:
        ...
```

### Tool port

```python
class Tool(Protocol):
    @property
    def name(self) -> str:
        ...

    def run(self, input: str) -> str:
        ...
```

### Memory port

```python
class Memory(Protocol):
    def add(self, message: str) -> None:
        ...

    def recent(self) -> list[str]:
        ...
```

### Agent composition

```python
class Agent:
    def __init__(
        self,
        model: Model,
        memory: Memory,
        tools: list[Tool],
    ) -> None:
        self.model = model
        self.memory = memory
        self.tools = tools

    def run(self, task: str) -> str:
        self.memory.add(task)
        return self.model.generate(task)
```

### Why Protocols help

They define boundaries among:

```text
Agent Runtime
   |
   +--> Model
   +--> Memory
   +--> Tools
```

A production implementation might connect:

```text
Model → cloud/local inference
Memory → database/Redis/vector store
Tool → HTTP/database/search service
```

### What this does not solve

Protocols do not automatically solve:

- tool authorization;
- prompt injection;
- sandboxing;
- model evaluation;
- retry semantics;
- observability;
- durable state;
- safety policies.

They provide useful dependency boundaries.

---

## 62. Banking Example — Payment Gateway Boundary

A banking/payment-style system can separate business policy from integration details.

```text
PaymentService
      |
      v
PaymentGateway Protocol
      ^
      |
+-----+----------------+
|                      |
RealBankGateway    FakeBankGateway
```

Protocol:

```python
from typing import Protocol


class PaymentGateway(Protocol):
    def charge(self, amount: float) -> bool:
        ...
```

Business service:

```python
class PaymentService:
    def __init__(self, gateway: PaymentGateway) -> None:
        self.gateway = gateway

    def pay(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("amount must be positive")
        return self.gateway.charge(amount)
```

Fake:

```python
class FakeBankGateway:
    def __init__(self, succeed: bool = True) -> None:
        self.succeed = succeed
        self.charges: list[float] = []

    def charge(self, amount: float) -> bool:
        self.charges.append(amount)
        return self.succeed
```

### Production adapter responsibilities

A real banking adapter might handle:

- authentication;
- request signing;
- external API formats;
- provider-specific errors;
- timeout handling;
- idempotency keys;
- audit metadata.

The business service should not need to understand the vendor's SDK internals.

No real credentials or production banking endpoints are required for this learning example.

---

# ADVANCED INTERNAL CONCEPTS

## 63. Advanced Protocol Introspection

Recent Python versions provide public introspection helpers such as:

```python
from typing import Protocol, get_protocol_members, is_protocol


class ExampleProtocol(Protocol):
    def run(self, value: str) -> int:
        ...

    name: str


print(is_protocol(ExampleProtocol))
print(get_protocol_members(ExampleProtocol))
```

The exact set returned is not intended to be manually edited as application configuration.

### Internal names

During debugging or library development you may encounter names such as:

```text
_is_protocol
__protocol_attrs__
```

Treat these as internal/version-sensitive details.

Use documented public APIs for application/tooling code when available.

### Why this matters

A production architecture should depend on stable Python APIs rather than internal implementation details of the typing machinery.

---

## 64. Static Type Checking

Tools such as **mypy** and **pyright** can analyze Protocol compatibility without running the program.

Example:

```python
from typing import Protocol


class Sender(Protocol):
    def send(self, message: str) -> None:
        ...


class EmailSender:
    def send(self, message: str) -> None:
        print(message)


def notify(sender: Sender) -> None:
    sender.send("hello")


notify(EmailSender())
```

A static checker can recognize the structural relationship.

Broken implementation:

```python
class BrokenSender:
    def send(self, message: int) -> None:
        print(message)
```

A configured type checker can report that `BrokenSender` is not compatible with the Protocol when passed where `Sender` is required.

### What static checking does

It analyzes code and type information before runtime.

### What it does not do

It does not prove:

- network availability;
- database health;
- business correctness;
- semantic behavior;
- latency requirements;
- external-system compatibility.

### Production use

Run a type checker in CI when Protocol-heavy architecture is important.

---

## 65. Protocols, Generics, and Variance

Variance matters when generic abstractions are substituted.

At a conceptual level:

```text
Covariance
→ safely producing more-specific values

Contravariance
→ safely accepting values in broader input positions

Invariance
→ neither substitution direction is generally safe
```

Suppose:

```text
Producer[Dog]
```

produces Dogs. It can often be used where a producer of Animal is required because every Dog is an Animal.

A consumer is different:

```text
Consumer[Dog]
```

cannot automatically replace a consumer that promises to accept every Animal.

### Why this matters for Protocols

Generic Protocols can describe producer/consumer contracts, but the type relationships must be sound.

### Practical rule

Do not guess variance.

Use your static type checker to verify generic substitutions.

---

## 66. Recursive Protocols

Protocols can describe recursive structures.

```python
from __future__ import annotations
from typing import Protocol


class Node(Protocol):
    value: str

    def children(self) -> list[Node]:
        ...
```

Implementation:

```python
class TreeNode:
    def __init__(self, value: str) -> None:
        self.value = value
        self._children: list[TreeNode] = []

    def children(self) -> list[TreeNode]:
        return list(self._children)
```

### Where useful

- trees;
- graphs;
- hierarchical resources;
- recursive document structures.

### Caution

Use recursive Protocols only when recursive behavior is part of the actual requirement.

---

## 67. Protocol Composition vs Combined Protocol

You can express a dependency through separate Protocols:

```python
class Identifiable(Protocol):
    @property
    def identifier(self) -> str:
        ...


class Logger(Protocol):
    def log(self, message: str) -> None:
        ...
```

Consumer:

```python
def process(item: Identifiable, logger: Logger) -> None:
    logger.log(item.identifier)
```

Or compose them:

```python
class Processable(Identifiable, Logger, Protocol):
    pass
```

### Which is better?

It depends on the consumer.

If the consumer naturally needs two independent capabilities, separate parameters can be clearer.

If a recurring application boundary genuinely requires both, a combined Protocol can be reasonable.

---

# COMPARISON TABLES

## 68. Protocol vs ABC vs Duck Typing

| Feature | Duck Typing | Protocol | ABC |
|---|---|---|---|
| Main idea | Use supported behavior | Structural contract | Nominal abstraction |
| Explicit declaration | Often implicit | Explicit type contract | Explicit base class |
| Inheritance required | No | No for structural compatibility | Usually yes for normal hierarchy |
| Static checking | Optional | Strong | Strong |
| Runtime enforcement | Actual calls | Limited with `runtime_checkable` | Abstractness enforced by ABC machinery |
| Signature validation at runtime | No | No full validation | No full validation |
| Shared implementation | Not required | Not primary | Strong fit |
| Third-party classes | Easy | Easy | Often more coupled |
| Plugin systems | Possible | Strong fit | Possible |
| Domain hierarchy | Less explicit | Less nominal | Strong fit |
| Test doubles | Easy | Excellent | Easy |
| Typical risk | Hidden contract | Over-abstraction | Hierarchy coupling |

### Decision questions

Use duck typing when:

- the dependency is small and local;
- runtime behavior is obvious;
- static contract overhead is unnecessary.

Use Protocol when:

- a structural contract is valuable;
- implementations are interchangeable;
- testing requires replacement;
- external/vendor boundaries should be isolated.

Use ABC when:

- a nominal family matters;
- shared implementation belongs in the base;
- runtime abstractness is useful.

---

## 69. DIP vs DI vs IoC

| Term | Meaning | Typical example |
|---|---|---|
| DIP | Architectural dependency-direction principle | Service depends on repository abstraction |
| DI | Technique for supplying dependencies | `Service(repository)` |
| IoC | Broader transfer of creation/control | Framework creates and invokes controller |

### Relationship

```text
DIP
 ↓
where dependencies should point

DI
 ↓
how a dependency can be supplied

IoC
 ↓
broader transfer of control
```

Do not use these terms as synonyms.

---

# REFACTORING

## 70. Refactoring From Concrete Infrastructure

### Before

```python
class ReportService:
    def __init__(self) -> None:
        self.database = PostgresDatabase()
        self.email = SMTPEmailSender()

    def generate(self, report) -> None:
        self.database.save(report)
        self.email.send("Report ready")
```

### Problems

- high-level code constructs low-level details;
- tests need infrastructure knowledge;
- vendor changes leak into business code;
- dependencies are hidden in the constructor body.

### Step 1 — Find required behavior

The consumer actually needs:

```text
save(report)
send(message)
```

### Step 2 — Define focused ports

```python
from typing import Protocol


class ReportRepository(Protocol):
    def save(self, report) -> None:
        ...


class Notifier(Protocol):
    def send(self, message: str) -> None:
        ...
```

### Step 3 — Inject dependencies

```python
class ReportService:
    def __init__(
        self,
        repository: ReportRepository,
        notifier: Notifier,
    ) -> None:
        self.repository = repository
        self.notifier = notifier

    def generate(self, report) -> None:
        self.repository.save(report)
        self.notifier.send("Report ready")
```

### Step 4 — Wire implementations outside

```python
repository = PostgresDatabase()
notifier = SMTPEmailSender()

service = ReportService(
    repository=repository,
    notifier=notifier,
)
```

### Step 5 — Test with fakes

```python
class FakeRepository:
    def __init__(self) -> None:
        self.saved = []

    def save(self, report) -> None:
        self.saved.append(report)


class FakeNotifier:
    def __init__(self) -> None:
        self.messages = []

    def send(self, message: str) -> None:
        self.messages.append(message)
```

### Result

```text
Before:

ReportService → PostgreSQL
             → SMTP

After:

ReportService → Repository Protocol ← PostgreSQL
             → Notifier Protocol   ← SMTP
```

### Production lesson

Do not refactor merely to use Protocol syntax. Refactor when the dependency boundary improves changeability, testability, or separation of concerns.

---

# PROGRESSIVE CODING EXAMPLES

## 71. Example 1 — Function Dependency

### Code

```python
def run_operation(value: int, operation) -> int:
    return operation(value)


def double(value: int) -> int:
    return value * 2


print(run_operation(3, double))
```

### Expected behavior

```text
6
```

### Explanation

The dependency is simply a function.

### What Python is doing

A function object is passed as an argument and invoked.

### Common mistake

Creating a class hierarchy for a one-function strategy.

### Production lesson

Use functions when they express the dependency clearly.

---

## 72. Example 2 — Tight Coupling

### Code

```python
class EmailSender:
    def send(self, message: str) -> None:
        print(message)


class Service:
    def __init__(self) -> None:
        self.sender = EmailSender()

    def run(self) -> None:
        self.sender.send("hello")
```

### Expected behavior

`Service()` always creates `EmailSender`.

### Explanation

The dependency is hidden and concrete.

### Common mistake

Treating hidden construction as a harmless detail when the component needs to be tested or replaced.

### Production lesson

Identify the construction boundary before adding abstractions.

---

## 73. Example 3 — Loose Coupling

### Code

```python
class Service:
    def __init__(self, sender) -> None:
        self.sender = sender

    def run(self) -> None:
        self.sender.send("hello")
```

### Expected behavior

Any compatible sender can be supplied.

### Explanation

Construction is separated from use.

### Production lesson

Explicit dependencies are easier to test and reason about.

---

## 74. Example 4 — Interface Concept

### Code

```python
class Sender:
    def send(self, message: str) -> None:
        raise NotImplementedError


class EmailSender(Sender):
    def send(self, message: str) -> None:
        print(f"email:{message}")
```

### Expected behavior

`EmailSender` participates in a nominal interface hierarchy.

### Explanation

This is an explicit base-class contract, though an ABC may be preferable if abstractness should be enforced.

### Production lesson

Nominal interfaces can be useful when the type family itself matters.

---

## 75. Example 5 — Duck Typing

### Code

```python
class EmailSender:
    def send(self, message: str) -> str:
        return f"email:{message}"


class SmsSender:
    def send(self, message: str) -> str:
        return f"sms:{message}"


def notify(sender, message: str) -> str:
    return sender.send(message)


print(notify(EmailSender(), "hello"))
print(notify(SmsSender(), "hello"))
```

### Expected behavior

```text
email:hello
sms:hello
```

### Explanation

No inheritance is required.

### Production lesson

Python naturally supports behavior-based polymorphism.

---

## 76. Example 6 — Simple Protocol

### Code

```python
from typing import Protocol


class Sender(Protocol):
    def send(self, message: str) -> None:
        ...


class EmailSender:
    def send(self, message: str) -> None:
        print(f"email:{message}")


def notify(sender: Sender, message: str) -> None:
    sender.send(message)


notify(EmailSender(), "hello")
```

### Expected behavior

```text
email:hello
```

### What the type checker is doing

It can see that `EmailSender` structurally supplies the required member.

### Production lesson

Protocol gives the behavior contract a visible type-level name.

---

## 77. Example 7 — Multiple Implementations

### Code

```python
from typing import Protocol


class Sender(Protocol):
    def send(self, message: str) -> None:
        ...


class EmailSender:
    def send(self, message: str) -> None:
        print("email")


class SmsSender:
    def send(self, message: str) -> None:
        print("sms")


class FakeSender:
    def send(self, message: str) -> None:
        print("fake")


def notify(sender: Sender) -> None:
    sender.send("hello")


for sender in [EmailSender(), SmsSender(), FakeSender()]:
    notify(sender)
```

### Expected behavior

```text
email
sms
fake
```

### Production lesson

The consumer is independent of the concrete implementation.

---

## 78. Example 8 — Attribute Protocol

### Code

```python
from typing import Protocol


class Named(Protocol):
    name: str


class User:
    def __init__(self, name: str) -> None:
        self.name = name


def greet(value: Named) -> str:
    return f"Hello, {value.name}"


print(greet(User("Alice")))
```

### Expected behavior

```text
Hello, Alice
```

### Production lesson

Use attribute Protocols when the consumer really needs an attribute capability.

---

## 79. Example 9 — Protocol Inheritance

### Code

```python
from typing import Protocol


class Reader(Protocol):
    def read(self) -> str:
        ...


class Writer(Protocol):
    def write(self, value: str) -> None:
        ...


class ReaderWriter(Reader, Writer, Protocol):
    pass


class Buffer:
    def __init__(self) -> None:
        self.value = ""

    def read(self) -> str:
        return self.value

    def write(self, value: str) -> None:
        self.value = value


def copy_text(source: Reader, target: Writer) -> None:
    target.write(source.read())


source = Buffer()
target = Buffer()
source.write("hello")
copy_text(source, target)

print(target.read())
```

### Expected behavior

```text
hello
```

### Production lesson

Consumer-specific capabilities reduce unnecessary coupling.

---

## 80. Example 10 — Generic Protocol

### Code

```python
from dataclasses import dataclass
from typing import Protocol, TypeVar


T = TypeVar("T")


class Repository(Protocol[T]):
    def get(self, key: str) -> T | None:
        ...

    def save(self, item: T) -> None:
        ...


@dataclass
class User:
    user_id: str
    name: str


class UserRepository:
    def __init__(self) -> None:
        self.data: dict[str, User] = {}

    def get(self, key: str) -> User | None:
        return self.data.get(key)

    def save(self, item: User) -> None:
        self.data[item.user_id] = item


repository: Repository[User] = UserRepository()
repository.save(User("u-1", "Alice"))

print(repository.get("u-1"))
```

### Expected behavior

A `User` instance is printed.

### Production lesson

Generic Protocols preserve type relationships across reusable boundaries.

---

## 81. Example 11 — Callable Protocol

### Code

```python
from typing import Protocol


class Predictor(Protocol):
    def __call__(self, text: str) -> float:
        ...


def length_score(text: str) -> float:
    return float(len(text))


class Model:
    def __call__(self, text: str) -> float:
        return float(len(text))


def predict(predictor: Predictor, text: str) -> float:
    return predictor(text)


print(predict(length_score, "hello"))
print(predict(Model(), "hello"))
```

### Expected behavior

```text
5.0
5.0
```

### Production lesson

A dependency can be a function or callable object rather than a full service class.

---

## 82. Example 12 — Runtime Check, Adapter, and Composition

### Code

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class PaymentGateway(Protocol):
    def charge(self, amount: float) -> bool:
        ...


class ExternalAPI:
    def create_payment(self, amount: float) -> bool:
        return amount > 0


class PaymentAdapter:
    def __init__(self, api: ExternalAPI) -> None:
        self.api = api

    def charge(self, amount: float) -> bool:
        return self.api.create_payment(amount)


class PaymentService:
    def __init__(self, gateway: PaymentGateway) -> None:
        self.gateway = gateway

    def pay(self, amount: float) -> bool:
        return self.gateway.charge(amount)


api = ExternalAPI()
adapter = PaymentAdapter(api)
service = PaymentService(adapter)

print(isinstance(adapter, PaymentGateway))
print(service.pay(100.0))
```

### Expected behavior

```text
True
True
```

### Production lesson

The composition root can connect concrete infrastructure to a Protocol boundary.

---

# EXERCISES

## 83. Basic Exercises

### Exercise 1 — Identify the Dependency

#### Problem

Identify the dependency in:

```python
class ReportService:
    def __init__(self, repository) -> None:
        self.repository = repository
```

#### Requirements

Explain what the dependency is and why it matters.

#### Expected behavior

Identify `repository` as the collaborator required by `ReportService`.

#### Solution

The dependency is `repository`. The service needs it to perform storage operations.

#### Explanation

A dependency is any collaborator the component needs, not only a database.

#### Key learning

Architecture starts with identifying dependencies.

---

### Exercise 2 — Identify Tight Coupling

#### Problem

Explain why this is tightly coupled:

```python
class Service:
    def __init__(self) -> None:
        self.repository = PostgresRepository()
```

#### Requirements

Name the concrete choice and explain its effect on testing.

#### Expected behavior

Explain that `Service` controls concrete infrastructure construction.

#### Solution

`Service` directly creates `PostgresRepository`, so the high-level component is coupled to that implementation.

#### Explanation

Changing storage or replacing it in tests requires changing or patching the service construction logic.

#### Key learning

Hidden construction is an important source of coupling.

---

### Exercise 3 — Constructor Injection

#### Problem

Refactor the previous service so the repository is supplied from outside.

#### Requirements

Use constructor injection.

#### Expected behavior

The constructor should accept any compatible repository.

#### Solution

```python
class Service:
    def __init__(self, repository) -> None:
        self.repository = repository
```

#### Explanation

Dependency creation is moved outside the high-level component.

#### Key learning

DI is possible with plain Python.

---

### Exercise 4 — Duck Typing

#### Problem

Create two senders with `send()` and one function that works with both.

#### Requirements

Do not use inheritance.

#### Expected behavior

Both senders can be passed to the function.

#### Solution

```python
class EmailSender:
    def send(self, message: str) -> str:
        return f"email:{message}"


class SmsSender:
    def send(self, message: str) -> str:
        return f"sms:{message}"


def notify(sender, message: str) -> str:
    return sender.send(message)


assert notify(EmailSender(), "hello") == "email:hello"
assert notify(SmsSender(), "hello") == "sms:hello"
```

#### Explanation

The consumer depends on the behavior, not the class identity.

#### Key learning

Polymorphism does not require inheritance.

---

### Exercise 5 — Write a Protocol

#### Problem

Create a `Logger` Protocol with one `log()` method.

#### Requirements

Add a concrete implementation without inheriting from the Protocol.

#### Expected behavior

A function typed with `Logger` should accept the concrete class.

#### Solution

```python
from typing import Protocol


class Logger(Protocol):
    def log(self, message: str) -> None:
        ...


class ConsoleLogger:
    def log(self, message: str) -> None:
        print(message)


def record(logger: Logger) -> None:
    logger.log("started")


record(ConsoleLogger())
```

#### Explanation

The relationship is structural.

#### Key learning

A concrete class does not need Protocol inheritance.

---

### Exercise 6 — Attribute Protocol

#### Problem

Create a Protocol requiring `name: str`.

#### Requirements

Use an instance attribute in the implementation.

#### Expected behavior

A greeting function can read `name`.

#### Solution

```python
from typing import Protocol


class Named(Protocol):
    name: str


class User:
    def __init__(self, name: str) -> None:
        self.name = name


def greet(value: Named) -> str:
    return f"Hello, {value.name}"
```

#### Explanation

The Protocol expresses the consumer's data dependency.

#### Key learning

Protocols can describe attributes as well as methods.

---

### Exercise 7 — Property Protocol

#### Problem

Create a read-only identifier contract.

#### Requirements

Use `@property` in the Protocol.

#### Expected behavior

The implementation provides an identifier without exposing a setter.

#### Solution

```python
from typing import Protocol


class Identifiable(Protocol):
    @property
    def identifier(self) -> str:
        ...


class User:
    def __init__(self, user_id: str) -> None:
        self._user_id = user_id

    @property
    def identifier(self) -> str:
        return self._user_id
```

#### Explanation

The contract asks for read access.

#### Key learning

Interfaces should expose the minimum required capability.

---

### Exercise 8 — Callable Protocol

#### Problem

Create a `Predictor` Protocol using `__call__()`.

#### Requirements

Accept both a function and a callable object conceptually.

#### Expected behavior

Both can be passed to the same consumer.

#### Solution

```python
from typing import Protocol


class Predictor(Protocol):
    def __call__(self, value: float) -> float:
        ...


def double(value: float) -> float:
    return value * 2


def run(predictor: Predictor, value: float) -> float:
    return predictor(value)


assert run(double, 3.0) == 6.0
```

#### Explanation

The callable itself is the dependency.

#### Key learning

Use a callable abstraction when it is the most natural contract.

---

### Exercise 9 — Constructor Injection With a Fake

#### Problem

Create a service that uses an injected notifier.

#### Requirements

Provide a fake notifier for testing.

#### Expected behavior

The fake records the sent message.

#### Solution

```python
class FakeNotifier:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send(self, message: str) -> None:
        self.messages.append(message)


class Service:
    def __init__(self, notifier) -> None:
        self.notifier = notifier

    def run(self) -> None:
        self.notifier.send("done")


notifier = FakeNotifier()
service = Service(notifier)
service.run()

assert notifier.messages == ["done"]
```

#### Explanation

The fake is injected instead of a real notification service.

#### Key learning

DI creates test seams.

---

### Exercise 10 — Generic Repository Protocol

#### Problem

Create `Repository[T]` with `get()` and `save()`.

#### Requirements

Use `TypeVar`.

#### Expected behavior

The concrete repository stores one model type.

#### Solution

```python
from dataclasses import dataclass
from typing import Protocol, TypeVar


T = TypeVar("T")


class Repository(Protocol[T]):
    def get(self, key: str) -> T | None:
        ...

    def save(self, item: T) -> None:
        ...


@dataclass
class User:
    user_id: str


class UserRepository:
    def __init__(self) -> None:
        self.data: dict[str, User] = {}

    def get(self, key: str) -> User | None:
        return self.data.get(key)

    def save(self, item: User) -> None:
        self.data[item.user_id] = item
```

#### Explanation

The Protocol preserves the model type relationship.

#### Key learning

Generic contracts can be reusable without losing type precision.

---

### Exercise 11 — Split a Giant Protocol

#### Problem

Split a storage Protocol containing `read()`, `write()`, and `delete()` into consumer-focused capabilities.

#### Requirements

Create `Reader` and `Writer`.

#### Expected behavior

A read-only function accepts only a `Reader`.

#### Solution

```python
from typing import Protocol


class Reader(Protocol):
    def read(self, key: str) -> str | None:
        ...


class Writer(Protocol):
    def write(self, key: str, value: str) -> None:
        ...


def load(reader: Reader, key: str) -> str | None:
    return reader.read(key)
```

#### Explanation

The consumer depends on what it actually needs.

#### Key learning

Interface segregation limits dependency surface.

---

### Exercise 12 — Runtime-Checkable Protocol

#### Problem

Create a Protocol with `close()` that can be checked with `isinstance()`.

#### Requirements

Use `@runtime_checkable`.

#### Expected behavior

A compatible object passes the check.

#### Solution

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Closable(Protocol):
    def close(self) -> None:
        ...


class Resource:
    def close(self) -> None:
        pass


assert isinstance(Resource(), Closable)
```

#### Explanation

The runtime check is structural and limited.

#### Key learning

Runtime Protocol checks do not prove semantic correctness.

---

### Exercise 13 — Adapter Translation

#### Problem

An external client exposes `create()`, while the application needs `save()`.

#### Requirements

Write an adapter that translates the call.

#### Expected behavior

The application-facing method should call the external method.

#### Solution

```python
from typing import Protocol


class Repository(Protocol):
    def save(self, value: str) -> None:
        ...


class ExternalStore:
    def create(self, value: str) -> None:
        print(f"create:{value}")


class StoreAdapter:
    def __init__(self, store: ExternalStore) -> None:
        self.store = store

    def save(self, value: str) -> None:
        self.store.create(value)
```

#### Explanation

The adapter accepts the external API but exposes the application's contract.

#### Key learning

Translate at the boundary instead of leaking external interfaces inward.

---

### Exercise 14 — Repository Service

#### Problem

Build a user service around a repository Protocol.

#### Requirements

- inject repository;
- create a user;
- save it.

#### Expected behavior

The repository receives the created user.

#### Solution

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass
class User:
    user_id: str
    name: str


class UserRepository(Protocol):
    def save(self, user: User) -> None:
        ...


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: list[User] = []

    def save(self, user: User) -> None:
        self.users.append(user)


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def create(self, user: User) -> None:
        self.repository.save(user)


repository = FakeUserRepository()
service = UserService(repository)
service.create(User("u-1", "Alice"))

assert repository.users == [User("u-1", "Alice")]
```

#### Explanation

The service uses only the repository contract.

#### Key learning

Business code can be independent from persistence technology.

---

### Exercise 15 — Clock Injection

#### Problem

Create a service that uses a clock abstraction.

#### Requirements

Inject a deterministic fake clock.

#### Expected behavior

The test receives a fixed timestamp.

#### Solution

```python
from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        ...


class FixedClock:
    def __init__(self, value: datetime) -> None:
        self.value = value

    def now(self) -> datetime:
        return self.value


class AuditService:
    def __init__(self, clock: Clock) -> None:
        self.clock = clock

    def timestamp(self) -> datetime:
        return self.clock.now()
```

#### Explanation

Time is an ordinary dependency that can be injected.

#### Key learning

DI is useful for deterministic testing even with standard-library functionality.

---

### Exercise 16 — Configuration Injection

#### Problem

Use a frozen configuration model for an API client.

#### Requirements

- `base_url`;
- timeout;
- max retries.

#### Expected behavior

The client retains the supplied config.

#### Solution

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ClientConfig:
    base_url: str
    timeout: int = 30
    max_retries: int = 3


class APIClient:
    def __init__(self, config: ClientConfig) -> None:
        self.config = config


config = ClientConfig("https://example.invalid", timeout=10)
client = APIClient(config)

assert client.config.timeout == 10
```

#### Explanation

Configuration is explicit and can be shared safely if immutable.

#### Key learning

Configuration itself can be a dependency.

---

### Exercise 17 — Factory Injection

#### Problem

Create a factory Protocol that supplies a client to a job.

#### Requirements

- factory Protocol;
- fake factory;
- injected factory.

#### Expected behavior

The job gets a client without constructing one directly.

#### Solution

```python
from typing import Protocol


class Client:
    pass


class ClientFactory(Protocol):
    def create(self) -> Client:
        ...


class FakeFactory:
    def create(self) -> Client:
        return Client()


class Job:
    def __init__(self, factory: ClientFactory) -> None:
        self.factory = factory

    def run(self) -> Client:
        return self.factory.create()


assert isinstance(Job(FakeFactory()).run(), Client)
```

#### Explanation

The job depends on a creation capability.

#### Key learning

Factories can isolate complex or environment-dependent construction.

---

### Exercise 18 — Dependency Graph

#### Problem

Write a small graph for an application with a service, repository, and notifier.

#### Requirements

Show the direction with arrows.

#### Expected behavior

The graph should show service depending on abstractions, while implementations point toward those abstractions.

#### Solution

```text
OrderService
   |
   +--> OrderRepository Protocol
   |
   +--> Notifier Protocol
             ^
             |
       concrete adapter
```

A complete graph can be represented conceptually as:

```text
OrderService
   |          |
   v          v
Repository  Notifier
 Protocol   Protocol
   ^          ^
   |          |
Postgres    SMTP
```

#### Explanation

The consumer depends on capabilities; concrete implementations are supplied from outside.

#### Key learning

Dependency graphs expose architecture more clearly than isolated class snippets.

---

### Exercise 19 — Identify an Over-Broad Protocol

#### Problem

Given:

```python
class Database(Protocol):
    def query(self, sql: str): ...
    def migrate(self): ...
    def backup(self): ...
    def restore(self): ...
```

Explain why a service that only queries may not need `Database`.

#### Requirements

Propose a smaller Protocol.

#### Expected behavior

The revised contract should contain only query behavior.

#### Solution

```python
class QueryExecutor(Protocol):
    def query(self, sql: str):
        ...
```

#### Explanation

The service depends only on query capability.

#### Key learning

Consumer-focused interfaces reduce unnecessary coupling.

---

### Exercise 20 — Behavioral Contract

#### Problem

A Protocol says:

```python
class Queue(Protocol):
    def publish(self, message: str) -> bool:
        ...
```

Write three semantic requirements that are not represented fully by the signature.

#### Requirements

Include behavior, errors, and reliability considerations.

#### Expected behavior

The answer must go beyond method names and types.

#### Solution

Possible requirements:

```text
True means the message has been accepted.
Blank messages raise ValueError.
The implementation does not silently duplicate a message when retrying.
```

#### Explanation

Types describe shape; contracts also describe behavior.

#### Key learning

Protocol conformance is not the complete business contract.

---

### Exercise 21 — LLM Provider Boundary

#### Problem

Create a provider-neutral LLM interface.

#### Requirements

- `generate(prompt: str) -> str`;
- fake implementation;
- injected into a service.

#### Expected behavior

The Q&A service returns the fake output.

#### Solution

```python
from typing import Protocol


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class FakeLLM:
    def generate(self, prompt: str) -> str:
        return "test-answer"


class QASystem:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def answer(self, question: str) -> str:
        return self.client.generate(question)


assert QASystem(FakeLLM()).answer("What is Python?") == "test-answer"
```

#### Explanation

The service does not know the provider.

#### Key learning

Vendor-neutral boundaries improve replacement and testing.

---

### Exercise 22 — Tool Protocol

#### Problem

Create a tool Protocol with a `name` property and `run()` method.

#### Requirements

Implement a calculator-like fake tool.

#### Expected behavior

The tool can be called through the Protocol.

#### Solution

```python
from typing import Protocol


class Tool(Protocol):
    @property
    def name(self) -> str:
        ...

    def run(self, input: str) -> str:
        ...


class EchoTool:
    @property
    def name(self) -> str:
        return "echo"

    def run(self, input: str) -> str:
        return input


def execute(tool: Tool, input: str) -> str:
    return tool.run(input)


assert execute(EchoTool(), "hello") == "hello"
```

#### Explanation

The agent/application can depend on tool capability rather than a vendor-specific implementation.

#### Key learning

Protocol boundaries are useful for plugin-like tools.

---

### Exercise 23 — Banking Gateway Test

#### Problem

Test a payment service with a fake bank gateway.

#### Requirements

- positive amount succeeds;
- non-positive amount raises.

#### Expected behavior

Tests should not call a real bank service.

#### Solution

```python
import pytest


class FakeBank:
    def charge(self, amount: float) -> bool:
        return True


class PaymentService:
    def __init__(self, gateway) -> None:
        self.gateway = gateway

    def pay(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("amount must be positive")
        return self.gateway.charge(amount)


def test_payment() -> None:
    service = PaymentService(FakeBank())
    assert service.pay(100.0) is True


def test_invalid_payment() -> None:
    service = PaymentService(FakeBank())
    with pytest.raises(ValueError):
        service.pay(0.0)
```

#### Explanation

External integration is replaced by a deterministic fake.

#### Key learning

DI makes business-rule tests independent from external services.

---

### Exercise 24 — Final Architecture Decision

#### Problem

A tiny module has one implementation, no external boundary, no test replacement need, and only a three-line algorithm. Should you add a Protocol?

#### Requirements

Give a reasoned answer.

#### Expected behavior

The answer should evaluate abstraction value rather than use a slogan.

#### Solution

Probably not.

A direct function or class is likely clearer until a real variation point or boundary appears.

#### Explanation

The purpose of a Protocol is to communicate and control a meaningful contract. If it adds only indirection, it is not improving the design.

#### Key learning

Good architecture is about managing complexity, not maximizing abstraction.

---

# DEBUGGING LAB

## 125. Debugging Problem 1 — Concrete Dependency Created Internally

### Broken code

```python
class RealRepository:
    def save(self, item) -> None:
        print("saved")


class Service:
    def __init__(self) -> None:
        self.repository = RealRepository()
```

### Expected behavior

A unit test should be able to replace the repository.

### Actual behavior

The service always creates `RealRepository`.

### Debugging clues

Inspect construction inside `Service.__init__`.

### Investigation

The dependency is hard-coded.

### Root cause

The high-level component owns the concrete dependency construction.

### Fixed implementation

```python
class Service:
    def __init__(self, repository) -> None:
        self.repository = repository
```

### Explanation

Construction is moved to the composition layer.

### Production lesson

Explicit dependency boundaries improve testability and changeability.

---

## 126. Debugging Problem 2 — Protocol Signature Mismatch

### Broken code

```python
from typing import Protocol


class Sender(Protocol):
    def send(self, message: str) -> None:
        ...


class BrokenSender:
    def send(self, message: int) -> None:
        print(message)
```

### Expected behavior

`BrokenSender` should satisfy the typed sender contract.

### Actual behavior

A static type checker can report that the parameter type is incompatible.

### Debugging clues

Compare the two signatures.

### Investigation

Protocol:

```text
send(str) -> None
```

Implementation:

```text
send(int) -> None
```

### Root cause

The implementation is not statically compatible.

### Fixed implementation

```python
class FixedSender:
    def send(self, message: str) -> None:
        print(message)
```

### Explanation

Static structural typing checks typed member compatibility.

### Production lesson

Run mypy/pyright in CI when type-level contracts are important.

---

## 127. Debugging Problem 3 — Incorrect `runtime_checkable` Expectation

### Broken code

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Sender(Protocol):
    def send(self, message: str) -> None:
        ...


class WrongSender:
    def send(self, message: int) -> list[int]:
        return [message]


print(isinstance(WrongSender(), Sender))
```

### Expected behavior

The developer expects `False` because the signature does not match.

### Actual behavior

The runtime check can report `True` because it checks member presence rather than fully validating the signature.

### Debugging clues

Look at what `@runtime_checkable` promises.

### Investigation

The required attribute `send` exists.

### Root cause

Runtime Protocol checks are intentionally limited.

### Fixed implementation

Use static type checking and tests for signature and behavior validation.

### Explanation

`runtime_checkable` does not become a runtime type checker.

### Production lesson

Do not rely on runtime structural checks for semantic correctness.

---

## 128. Debugging Problem 4 — Giant Protocol

### Broken code

```python
from typing import Protocol


class Storage(Protocol):
    def read(self, key: str) -> str:
        ...

    def write(self, key: str, value: str) -> None:
        ...

    def delete(self, key: str) -> None:
        ...

    def backup(self) -> None:
        ...

    def replicate(self) -> None:
        ...


def load(storage: Storage, key: str) -> str:
    return storage.read(key)
```

### Expected behavior

`load()` should depend only on reading.

### Actual behavior

The type-level abstraction exposes unrelated capabilities.

### Debugging clues

Inspect which members `load()` actually uses.

### Investigation

Only `read()` is needed.

### Root cause

The interface is broader than the consumer's needs.

### Fixed implementation

```python
from typing import Protocol


class Reader(Protocol):
    def read(self, key: str) -> str:
        ...


def load(reader: Reader, key: str) -> str:
    return reader.read(key)
```

### Explanation

The new Protocol is consumer-focused.

### Production lesson

Smaller interfaces can make systems easier to replace and test.

---

## 129. Debugging Problem 5 — Broken Dependency Injection

### Broken code

```python
class FakeClock:
    def now(self) -> str:
        return "2026-01-01"


class Service:
    def __init__(self, clock) -> None:
        self.clock = clock

    def run(self) -> str:
        return self.clock.current_time()
```

### Expected behavior

`Service(FakeClock()).run()` should return a timestamp.

### Actual behavior

`AttributeError` occurs because `current_time()` does not exist.

### Debugging clues

Compare provider and consumer method names.

### Investigation

Provider:

```text
now()
```

Consumer expects:

```text
current_time()
```

### Root cause

The injected object does not satisfy the intended contract.

### Fixed implementation

```python
class Service:
    def __init__(self, clock) -> None:
        self.clock = clock

    def run(self) -> str:
        return self.clock.now()
```

### Explanation

DI does not magically make incompatible objects compatible.

### Production lesson

Treat dependency contracts as real contracts.

---

## 130. Debugging Problem 6 — Test Double Does Not Match the Contract

### Broken code

```python
from typing import Protocol


class PaymentGateway(Protocol):
    def charge(self, amount: float) -> bool:
        ...


class FakeGateway:
    def charge(self, amount: int) -> bool:
        return True
```

### Expected behavior

The fake should be a compatible implementation.

### Actual behavior

Static analysis can reject the fake because its signature does not match the Protocol.

### Debugging clues

Check parameter types first.

### Investigation

The Protocol requires:

```text
float
```

The fake provides:

```text
int
```

### Root cause

The test double was designed by resemblance instead of the contract.

### Fixed implementation

```python
class FixedFakeGateway:
    def charge(self, amount: float) -> bool:
        return True
```

### Explanation

A fake is still an implementation of the boundary.

### Production lesson

Contract-compatible test doubles are part of good test architecture.

---

## 131. Debugging Problem 7 — Vendor Type Leaking Into Business Logic

### Broken code

```python
class OrderService:
    def __init__(self, postgres_session) -> None:
        self.session = postgres_session

    def save(self, order) -> None:
        self.session.execute("INSERT ...")
```

### Expected behavior

Business logic should not need database-specific APIs.

### Actual behavior

The service depends on a Postgres-specific session and SQL behavior.

### Debugging clues

Look at the constructor type and method body.

### Investigation

The service uses an implementation-specific API.

### Root cause

The abstraction boundary is too low-level.

### Fixed implementation

```python
from typing import Protocol


class OrderRepository(Protocol):
    def save(self, order) -> None:
        ...


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self.repository = repository

    def save(self, order) -> None:
        self.repository.save(order)
```

### Explanation

SQL is now an infrastructure detail.

### Production lesson

Expose domain-relevant capabilities rather than infrastructure operations where useful.

---

## 132. Debugging Problem 8 — Protocol Used Without a Real Boundary

### Broken code

```python
from typing import Protocol


class Adder(Protocol):
    def add(self, a: int, b: int) -> int:
        ...


class DefaultAdder:
    def add(self, a: int, b: int) -> int:
        return a + b


def calculate(adder: Adder, a: int, b: int) -> int:
    return adder.add(a, b)
```

### Expected behavior

Architecture should be justified by a meaningful problem.

### Actual behavior

Nothing is technically broken, but the design may add unnecessary indirection.

### Debugging clues

Ask whether implementations vary or whether testing requires replacement.

### Investigation

If one stable implementation exists and the operation is trivial, the Protocol may not provide meaningful value.

### Root cause

Premature abstraction.

### Fixed implementation

```python
def calculate(a: int, b: int) -> int:
    return a + b
```

### Explanation

The simpler design is easier to read and maintain.

### Production lesson

Abstraction should reduce complexity rather than merely add layers.

---

# MINI-PROJECT

## 133. Pluggable AI Inference and Tool Service

Build a small production-oriented application using Protocol-based boundaries.

### Requirements

The project must include:

- a model Protocol;
- a tool Protocol;
- a memory Protocol;
- a repository Protocol;
- multiple concrete implementations;
- fake/test implementations;
- dependency inversion;
- dependency injection;
- an external-service adapter;
- configuration;
- logging;
- pytest tests;
- a composition root;
- no credentials or real API keys;
- clear dependency ownership.

### Architecture

```text
                    Application
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
     Model Port     Tool Port     Memory Port
          ^             ^             ^
          |             |             |
   Provider adapter  Tool impls   DB/Redis adapter
                        
                    Repository Port
                          ^
                          |
                    Persistence adapter
```

### Step 1 — Configuration

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    model_name: str = "example-model"
    timeout_seconds: int = 30
```

### Step 2 — Domain models

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class InferenceRequest:
    request_id: str
    prompt: str


@dataclass(frozen=True)
class InferenceResponse:
    request_id: str
    text: str
```

### Step 3 — Protocols

```python
from typing import Protocol


class Model(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class Tool(Protocol):
    @property
    def name(self) -> str:
        ...

    def run(self, input: str) -> str:
        ...


class Memory(Protocol):
    def add(self, message: str) -> None:
        ...

    def recent(self) -> list[str]:
        ...


class InferenceRepository(Protocol):
    def save(self, response: InferenceResponse) -> None:
        ...
```

### Step 4 — Fake model

```python
class FakeModel:
    def __init__(self, response: str = "fake-response") -> None:
        self.response = response

    def generate(self, prompt: str) -> str:
        return self.response
```

### Step 5 — In-memory memory

```python
class InMemoryMemory:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def add(self, message: str) -> None:
        self.messages.append(message)

    def recent(self) -> list[str]:
        return list(self.messages[-10:])
```

### Step 6 — Repository

```python
class InMemoryInferenceRepository:
    def __init__(self) -> None:
        self.responses: list[InferenceResponse] = []

    def save(self, response: InferenceResponse) -> None:
        self.responses.append(response)
```

### Step 7 — Tool

```python
class EchoTool:
    @property
    def name(self) -> str:
        return "echo"

    def run(self, input: str) -> str:
        return input
```

### Step 8 — Application service

```python
import logging


logger = logging.getLogger(__name__)


class InferenceService:
    def __init__(
        self,
        config: AppConfig,
        model: Model,
        memory: Memory,
        repository: InferenceRepository,
        tools: list[Tool],
    ) -> None:
        self.config = config
        self.model = model
        self.memory = memory
        self.repository = repository
        self.tools = tools

    def run(self, request: InferenceRequest) -> InferenceResponse:
        if not request.request_id:
            raise ValueError("request_id is required")
        if not request.prompt.strip():
            raise ValueError("prompt cannot be blank")

        self.memory.add(request.prompt)

        logger.info(
            "starting inference",
            extra={"request_id": request.request_id},
        )

        text = self.model.generate(request.prompt)

        response = InferenceResponse(
            request_id=request.request_id,
            text=text,
        )

        self.repository.save(response)
        return response
```

### Step 9 — External model adapter

```python
class ExternalModelClient:
    def generate(self, prompt: str) -> str:
        return f"external:{prompt}"


class ExternalModelAdapter:
    def __init__(self, client: ExternalModelClient) -> None:
        self.client = client

    def generate(self, prompt: str) -> str:
        return self.client.generate(prompt)
```

In a real system, the external client would be a real SDK/client object supplied through secure configuration. No credentials belong in this learning project.

### Step 10 — Composition root

```python
def build_service() -> InferenceService:
    config = AppConfig()
    model = FakeModel()
    memory = InMemoryMemory()
    repository = InMemoryInferenceRepository()
    tools = [EchoTool()]

    return InferenceService(
        config=config,
        model=model,
        memory=memory,
        repository=repository,
        tools=tools,
    )
```

### Step 11 — Tests

```python
import pytest


def test_inference_service_returns_fake_response() -> None:
    service = build_service()

    result = service.run(
        InferenceRequest(
            request_id="req-1",
            prompt="hello",
        )
    )

    assert result == InferenceResponse(
        request_id="req-1",
        text="fake-response",
    )


def test_blank_prompt_is_rejected() -> None:
    service = build_service()

    with pytest.raises(ValueError):
        service.run(
            InferenceRequest(
                request_id="req-1",
                prompt="   ",
            )
        )
```

### What this project demonstrates

```text
Protocol
    ↓
consumer-facing capability

Adapter
    ↓
external translation

Dependency Injection
    ↓
implementation supplied from outside

Composition Root
    ↓
concrete object wiring

Tests
    ↓
fake implementations
```

### Production extensions

A real service would additionally need to consider:

- authentication and secret management;
- request timeouts;
- retries/backoff;
- rate limits;
- streaming;
- model/version metadata;
- tool authorization;
- memory persistence;
- checkpointing;
- tracing;
- metrics;
- structured logs;
- error normalization;
- idempotency.

These concerns should be added behind appropriate boundaries rather than placed into one giant Protocol.

---

# INTERVIEW QUESTIONS

## 134. Beginner Questions

### What is an interface?

An interface is a contract that describes what capability a component exposes to its consumer.

### What is a dependency?

Anything a component needs to perform its work, such as another object, function, database, clock, API client, or model provider.

### What is coupling?

The degree to which one component depends on another component's structure or behavior.

### What is tight coupling?

A strong dependency on a concrete implementation or its internal details.

### What is loose coupling?

Controlled dependency around a stable, useful capability. It does not mean zero dependencies.

### What is duck typing?

A behavior-oriented style where code uses an object based on the operations it provides rather than requiring a specific nominal type.

### What is Protocol?

A typing construct that defines a structural contract that static type checkers can use for structural subtyping.

### Does Protocol require inheritance?

No. A class can structurally satisfy a Protocol without inheriting from it.

---

## 135. Intermediate Questions

### What is structural typing?

Compatibility is based on required structure or members.

### What is nominal typing?

Compatibility is based on explicit declared type relationships such as inheritance.

### Why use a Protocol?

To make a behavioral boundary explicit for static typing and design while retaining structural compatibility.

### How does Protocol differ from ABC?

A Protocol is primarily structural; an ABC is nominal and can enforce abstractness for ordinary subclasses at runtime.

### What is dependency injection?

Supplying dependencies from outside rather than making a component construct them internally.

### What is constructor injection?

Passing a dependency into `__init__()`.

### What is dependency inversion?

A principle that keeps high-level policy from directly depending on low-level implementation details, typically by using stable abstractions.

### What is an adapter?

A component that translates one interface into another.

### What is the composition root?

The place where concrete implementations are created and assembled into the application's dependency graph.

---

## 136. Advanced Questions

### What does `@runtime_checkable` do?

It enables limited runtime structural checks using `isinstance()` and supported `issubclass()` operations.

### What are its limitations?

It checks required member presence rather than fully validating signatures, annotations, or semantic behavior.

### Why is static typing still necessary?

Static type checking can verify richer member/type compatibility before runtime.

### What is a generic Protocol?

A Protocol parameterized by a type variable so reusable interfaces can preserve relationships among input/output types.

### What is a callable Protocol?

A Protocol that describes callable behavior through `__call__()`.

### Why use an adapter around an LLM provider SDK?

To prevent vendor-specific request/response and SDK details from spreading into application logic.

### What is a repository boundary?

An application-facing contract for persistence behavior, separating business code from database implementation details.

### What is ports-and-adapters architecture?

An architecture that defines application-facing ports and connects external technologies through adapters.

### Can a Protocol-compatible implementation still be wrong?

Yes. Structural/type compatibility does not prove semantic correctness.

---

## 137. Architect-Level Questions

### Where should infrastructure dependencies normally be created?

At an outer composition/wiring boundary, such as the application's startup code or composition root.

### How would you design a pluggable LLM provider?

Define a narrow application-facing Protocol, create provider-specific adapters, inject the desired implementation, and prevent provider SDK details from leaking into business logic.

### How would you isolate a database from business logic?

Define a consumer-focused repository contract, inject it into the application service, and implement the contract in a database-specific adapter.

### How would you design a testable agent runtime?

Give the agent explicit dependencies for model, memory, tools, and persistent state where appropriate. Provide fakes or deterministic test implementations and wire production implementations at the composition root.

### When would you avoid Protocol?

When there is no useful abstraction boundary, no meaningful implementation variation, no testing need, and direct code is simpler and clearer.

### How do you decide between Protocol and ABC?

Ask whether structural compatibility or nominal identity is needed, whether shared implementation belongs in a base class, whether runtime abstractness matters, and whether implementations are already-existing third-party types.

---

# ARCHITECTURE QUESTIONS

## 138. Scenario — Service Directly Creates Postgres

A service creates a Postgres repository in its constructor.

### Model answer

Move construction out of the service. Define a repository contract and inject the implementation.

```text
OrderService
     |
     v
Repository Protocol
     ^
     |
Postgres Adapter
```

The composition root creates the concrete repository.

---

## 139. Scenario — Multiple LLM Providers

A company wants to support:

```text
provider A
provider B
local model
fake model
```

### Model answer

Define the smallest contract the application needs, for example:

```python
class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...
```

Wrap provider SDKs with adapters and inject the chosen implementation.

If some providers support streaming or tool calls and others do not, do not automatically stuff all provider-specific features into one universal interface. Consider separate capabilities or higher-level abstractions.

---

## 140. Scenario — Agent With Many Tools

An agent uses tools supplied by different vendors.

### Model answer

Define a tool boundary around the application needs:

```python
class Tool(Protocol):
    @property
    def name(self) -> str:
        ...

    def run(self, input: str) -> str:
        ...
```

Vendor-specific authentication, request formatting, and transport belong in adapters.

For a production agent, also consider authorization, structured arguments, timeouts, error mapping, and auditability.

---

## 141. Scenario — Files, APIs, and Databases

A data pipeline must read from files, APIs, and databases.

### Model answer

Define a `DataSource` capability. Provide separate adapters:

```text
DataSource Protocol
       ^
+------+-------+
|      |       |
File   API   Database
```

The pipeline should not know how each source is transported.

---

## 142. Scenario — Payment Service

A payment service needs real and fake gateways.

### Model answer

Use a `PaymentGateway` Protocol and inject implementations. The service owns business validation and policy; the gateway adapter owns external integration mechanics.

---

## 143. Scenario — Giant Protocol

A Protocol contains 20 methods.

### Model answer

Do not reject it solely because the number is 20. Examine consumers.

If different consumers need unrelated subsets, split the contract. If the methods are cohesive and consumers genuinely need them, the size may be reasonable.

---

## 144. Scenario — Structurally Compatible but Semantically Wrong

A class matches all required method signatures but violates an idempotency guarantee.

### Model answer

Static Protocol compatibility is not behavioral correctness. Add semantic contract tests and integration tests, and document the idempotency expectation explicitly.

---

## 145. Scenario — Too Many Tiny Protocols

A codebase has 30 one-method Protocols.

### Model answer

Review them individually. Keep abstractions that isolate real variation points or important boundaries. Remove ones that create indirection without meaningful value.

---

## 146. Scenario — Multiple Worker Processes

A web service creates a class-level cache and expects every process to share it.

### Model answer

Normal Python memory is process-local. Use an external shared cache/database/message system when cross-process consistency is required.

---

## 147. Scenario — Local vs Remote ML Inference

A system may use a local model today and remote model serving later.

### Model answer

Define a predictor/model boundary, inject the implementation, and isolate remote transport behind an adapter.

---

# KNOWLEDGE CHECK

## 148. Multiple Choice

### Question 1

Which is most tightly coupled?

A.

```python
def run(sender):
    sender.send("hello")
```

B.

```python
class Service:
    def __init__(self, sender) -> None:
        self.sender = sender
```

C.

```python
class Service:
    def __init__(self) -> None:
        self.sender = EmailSender()
```

D.

```python
class Service:
    def send(self, sender) -> None:
        sender.send("hello")
```

**Answer:** C.

**Explanation:** The service directly constructs a concrete implementation.

---

### Question 2

What is the main purpose of `Protocol`?

A. Runtime object creation
B. Structural typing contract
C. Database persistence
D. Thread synchronization

**Answer:** B.

---

### Question 3

Which statement is correct?

A. Protocol always requires inheritance.
B. Protocol proves semantic correctness.
C. Protocol can express structural compatibility to static type checkers.
D. Protocol replaces all ABCs.

**Answer:** C.

---

### Question 4

What does `@runtime_checkable` enable?

A. Complete runtime type checking
B. Limited runtime structural `isinstance()`/supported `issubclass()` checking
C. Automatic mocking
D. Automatic dependency injection

**Answer:** B.

---

### Question 5

Which statement best describes DIP?

A. Every dependency must be a Protocol.
B. All dependencies must be external.
C. High-level policy should avoid direct dependency on low-level implementation details where an abstraction is appropriate.
D. Classes must never depend on other classes.

**Answer:** C.

---

## 149. Predict the Result

### Question 6

```python
from typing import Protocol


class Sender(Protocol):
    def send(self, message: str) -> None:
        ...


class EmailSender:
    def send(self, message: str) -> None:
        print(message)


def notify(sender: Sender) -> None:
    sender.send("hello")


notify(EmailSender())
```

**Answer:**

```text
hello
```

**Explanation:** `EmailSender` structurally provides the required member.

---

### Question 7

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Closable(Protocol):
    def close(self) -> None:
        ...


class Resource:
    def close(self) -> None:
        pass


print(isinstance(Resource(), Closable))
```

**Answer:**

```text
True
```

**Explanation:** The limited runtime protocol check sees the required member.

---

### Question 8

```python
def execute(operation, value):
    return operation(value)


def triple(value: int) -> int:
    return value * 3


print(execute(triple, 4))
```

**Answer:**

```text
12
```

**Explanation:** The function itself is the injected dependency.

---

## 150. Identify the Problem

### Question 9

Why is this a hidden dependency?

```python
class Service:
    def run(self) -> None:
        DatabaseClient().save("item")
```

**Answer:** The service creates the dependency inside the operation instead of receiving it explicitly.

---

### Question 10

Why can the following be an interface-segregation problem?

```python
class Database(Protocol):
    def read(self): ...
    def write(self): ...
    def migrate(self): ...
    def backup(self): ...
```

**Answer:** A consumer that only reads is exposed to methods it does not need.

---

### Question 11

Why can a runtime Protocol check be `True` while a method call still fails semantically?

**Answer:** Runtime Protocol checks only perform limited structural presence checks; they do not prove the full signature or behavior.

---

### Question 12

Why is an adapter useful around a vendor SDK?

**Answer:** It isolates external interface and implementation details from the application's contract.

---

## 151. Short Answer

### Question 13

Does loose coupling mean no dependencies?

**Answer:** No. It means dependencies are controlled around useful boundaries.

### Question 14

Does Protocol require inheritance?

**Answer:** No.

### Question 15

Does `runtime_checkable` validate signatures?

**Answer:** No, not fully. It checks for required member presence.

### Question 16

Does type checking prove a service works against a live database?

**Answer:** No.

### Question 17

Is DI the same as DIP?

**Answer:** No. DIP is a principle; DI is a technique.

### Question 18

Is IoC the same as DI?

**Answer:** No. IoC is broader.

---

## 152. Debugging

### Question 19

A service makes an unexpected network call during a unit test. What should you inspect?

**Answer:** Look for internally constructed concrete clients or hidden global dependencies.

### Question 20

A test fake does not type-check against a Protocol. What should you compare first?

**Answer:** Method/attribute names and type signatures.

### Question 21

A Protocol-compatible implementation fails an idempotency test. What does that show?

**Answer:** Type compatibility is not behavioral compatibility.

### Question 22

A runtime Protocol check unexpectedly fails after a Python-version upgrade. What should you inspect?

**Answer:** Runtime-checkable Protocol semantics and version-specific changes, and avoid depending on undocumented implementation details.

---

## 153. Architecture

### Question 23

Where should concrete database construction normally happen?

**Answer:** In an outer composition/wiring layer such as the composition root.

### Question 24

Where should a model provider's SDK-specific request logic live?

**Answer:** In the provider adapter/infrastructure layer.

### Question 25

Where should the agent's business-level orchestration live?

**Answer:** In the application/core layer that depends on stable capabilities rather than provider implementations.

### Question 26

What is the main purpose of a repository Protocol?

**Answer:** To provide a stable persistence capability to application logic without coupling it to a particular database implementation.

---

# COMMON MISCONCEPTIONS

## 154. Misconception — Protocol Is the Same as ABC

### Correct mental model

```text
Protocol → structural/static contract
ABC      → nominal abstract class mechanism
```

They solve overlapping but distinct design problems.

---

## 155. Misconception — Protocol Must Be Inherited

False.

This is valid structural compatibility:

```python
class EmailSender:
    def send(self, message: str) -> None:
        print(message)
```

without inheriting from the Protocol.

---

## 156. Misconception — Protocol Automatically Enforces Runtime Behavior

False.

A normal Protocol is not a runtime validator.

`@runtime_checkable` enables only limited structural runtime checks.

---

## 157. Misconception — `runtime_checkable` Validates Signatures

False.

It checks required member presence rather than full method signatures or types.

---

## 158. Misconception — Type Hints Enforce Runtime Behavior

False.

Type annotations primarily support static checking, tooling, and documentation.

---

## 159. Misconception — Duck Typing Means No Contract

False.

Duck typing often relies on an implicit contract:

```text
must have send(message)
```

The contract exists even if it is not declared with a Protocol.

---

## 160. Misconception — DI Means a DI Framework

False.

This is DI:

```python
service = Service(repository)
```

No framework is required.

---

## 161. Misconception — DIP Means Use Dependency Injection

Not exactly.

DI can be a technique that helps implement DIP, but DIP is the architectural principle about dependency direction.

---

## 162. Misconception — IoC, DI, and DIP Are Identical

False.

```text
DIP → architecture principle
DI  → dependency-supply technique
IoC → broader control-transfer concept
```

---

## 163. Misconception — Every Class Needs a Protocol

False.

A Protocol should exist only when it provides meaningful abstraction value.

---

## 164. Misconception — More Abstraction Is Always Better

False.

Excessive abstraction can create:

- indirection;
- cognitive load;
- boilerplate;
- difficult debugging.

---

## 165. Misconception — Loose Coupling Means No Dependencies

False.

Useful applications necessarily have dependencies. The goal is controlled dependency relationships.

---

## 166. Misconception — ABC Is Always Better Than Protocol

False.

Protocol may be better for structural boundaries. ABC may be better for nominal hierarchies and shared implementations.

---

## 167. Misconception — Protocol Guarantees Behavioral Correctness

False.

Static compatibility does not prove semantic correctness.

---

## 168. Misconception — Mocks Prove External Services Work

False.

Mocks isolate application behavior. Integration tests are needed to test real external integrations.

---

## 169. Misconception — Adapters Eliminate All Coupling

False.

Adapters isolate and contain coupling. They still depend on the external system.

---

## 170. Misconception — A Repository Interface Must Contain Every Database Operation

False.

The repository contract should be designed around the consumer's actual persistence needs.

---

## 171. Misconception — Dependency Injection Requires a Framework

False.

Functions, constructors, factories, and ordinary object composition are enough.

---

# AVOIDING OVER-ENGINEERING

## 172. Abstraction for a Reason

An abstraction should reduce complexity by controlling change or dependency boundaries.

Good reasons include:

- multiple implementations;
- external systems;
- testing seams;
- plugins;
- vendor isolation;
- independent lifecycle;
- application/infrastructure separation.

---

## 173. Good Abstraction

```python
class PaymentGateway(Protocol):
    def charge(self, amount: float) -> bool:
        ...
```

Possible implementations:

```text
bank adapter
payment provider adapter
fake gateway
```

The variation is real.

---

## 174. Unnecessary Abstraction

```python
class StringLength(Protocol):
    def calculate(self, value: str) -> int:
        ...
```

followed by:

```python
def calculate(value: str) -> int:
    return len(value)
```

If there is no real boundary or implementation variation, the Protocol may simply add indirection.

---

## 175. Indirection Cost

An abstraction path may become:

```text
Service
  ↓
Protocol
  ↓
Factory
  ↓
Adapter
  ↓
Client
  ↓
External API
```

Every layer should answer a real question.

Ask:

```text
Does this layer isolate a meaningful change?
Does it improve testing?
Does it prevent implementation leakage?
Can the team explain why it exists?
```

If not, simplify.

---

## 176. Interface Stability

A good interface should not change every time one implementation changes.

Bad abstraction:

```text
GenericLLM
    + provider_a_special_option
    + provider_b_special_option
    + provider_c_special_option
```

Better:

```text
Application needs
       ↓
minimal stable contract
       ↑
provider-specific adapters
```

### Production lesson

Design around what the consumer needs rather than what the provider happens to expose.

---

# PRODUCTION DESIGN CHECKLIST

## 177. Dependency

- [ ] Is the dependency explicit?
- [ ] Is its lifecycle clear?
- [ ] Is its owner clear?
- [ ] Can it be replaced where necessary?

## Coupling

- [ ] Is high-level policy directly coupled to infrastructure?
- [ ] Are vendor details leaking inward?
- [ ] Is coupling controlled rather than unrealistically eliminated?

## Interface

- [ ] Is the contract small enough for its consumers?
- [ ] Is it consumer-focused?
- [ ] Does it describe a meaningful capability?
- [ ] Are semantic expectations documented?

## Protocol

- [ ] Is structural typing actually useful?
- [ ] Are Protocol methods/attributes correctly typed?
- [ ] Are properties used when read-only capability is appropriate?
- [ ] Are generics used only when they add meaningful type information?

## Runtime

- [ ] Is `runtime_checkable` actually necessary?
- [ ] Does the team understand its limited runtime semantics?
- [ ] Are runtime assumptions covered by tests?

## Static Typing

- [ ] Is mypy or pyright used where appropriate?
- [ ] Does CI check Protocol compatibility?
- [ ] Are type errors distinguished from behavioral failures?

## Dependency Inversion

- [ ] Does high-level policy avoid directly constructing infrastructure?
- [ ] Does the dependency graph point toward stable abstractions?
- [ ] Are implementation details contained at the edge?

## Dependency Injection

- [ ] Are dependencies injected where useful?
- [ ] Are constructors still manageable?
- [ ] Would a function parameter be simpler for a stateless strategy?
- [ ] Is a factory appropriate for lifecycle-dependent creation?
- [ ] Is a DI framework actually necessary?

## Composition Root

- [ ] Is there a clear place for concrete wiring?
- [ ] Does business logic remain independent of startup configuration?

## Adapters

- [ ] Are external/vendor APIs isolated?
- [ ] Are translation responsibilities clear?
- [ ] Are provider-specific errors normalized appropriately?
- [ ] Are credentials managed outside source code?

## Testing

- [ ] Can dependencies be replaced with fakes?
- [ ] Are test doubles compatible with the intended contract?
- [ ] Are semantic behaviors tested?
- [ ] Are real external integrations separately tested where appropriate?

## Distributed Systems

- [ ] Is process-local state being confused with shared state?
- [ ] Is shared infrastructure explicitly externalized when needed?

## Maintainability

- [ ] Does every Protocol have a reason to exist?
- [ ] Are there giant Protocols?
- [ ] Are there needless layers?
- [ ] Can another engineer explain the dependency graph?

---

# FINAL MENTAL MODEL

## 178. The Architecture Picture

```text
                    HIGH-LEVEL POLICY
                           |
                           v
                    +-------------+
                    |  Protocol   |
                    | / Contract  |
                    +-------------+
                      ^         ^
                      |         |
                 Adapter A   Adapter B
                      |         |
                      v         v
                 Concrete    Concrete
              Implementation Implementation
```

### Meaning

- high-level policy depends on the abstraction;
- concrete implementations satisfy that abstraction;
- adapters isolate external systems;
- tests can provide alternative implementations;
- the composition root wires the graph.

---

## 179. Protocol

Think:

```text
Protocol
    = "What capability do I need?"
```

Examples:

```text
Repository.get/save
Gateway.charge
Clock.now
Model.generate
Tool.run
Memory.add
```

---

## 180. Implementation

Think:

```text
Implementation
    = "How is that capability provided?"
```

Examples:

```text
Postgres adapter
cloud model adapter
local model
real clock
fake gateway
Redis memory adapter
```

---

## 181. Dependency Injection

Think:

```text
Dependency Injection
    = "Give the component what it needs."
```

Examples:

```python
Service(repository)
Agent(model, memory, tools)
Pipeline(source)
```

---

## 182. Dependency Inversion

Think:

```text
Dependency Inversion
    = "Keep high-level policy from depending
      directly on low-level implementation details."
```

Visual:

```text
BAD

Policy → Concrete Detail


GOOD

Policy → Abstraction ← Concrete Detail
```

---

## 183. Type Compatibility vs Behavioral Compatibility

Remember:

```text
TYPE COMPATIBILITY
       ↓
shape/member/type relationship

BEHAVIORAL COMPATIBILITY
       ↓
semantic contract

OPERATIONAL COMPATIBILITY
       ↓
latency, reliability, security, resource behavior
```

Static typing primarily helps with the first layer.

Tests and production engineering must validate the others.

---

## 184. DIP vs DI vs IoC

Keep the distinctions:

```text
DIP
→ architecture principle

DI
→ dependency-supply technique

IoC
→ broader transfer of control
```

They work together but are not identical.

---

## 185. Final Decision Framework

Before adding a Protocol or ABC, ask:

```text
1. What problem am I solving?
2. What dependency exists today?
3. Is the implementation likely to vary?
4. Is there an external boundary?
5. Does testing require substitution?
6. What is the smallest useful consumer capability?
7. Is structural typing useful?
8. Is nominal identity important?
9. Do I need shared implementation?
10. Do I need runtime abstractness?
11. Where should concrete implementations be created?
12. Does the abstraction reduce or increase cognitive load?
```

If the abstraction provides a real boundary, implement it.

If it only adds indirection, prefer the simpler design.

---

# REQUIRED API / LANGUAGE FEATURE COVERAGE

## 186. `typing.Protocol`

### Purpose

Defines a structural typing contract.

### Syntax

```python
from typing import Protocol


class Reader(Protocol):
    def read(self) -> str:
        ...
```

### Parameters

The Protocol itself can have type parameters through `TypeVar` or modern generic syntax.

### Return behavior

It defines the type-level contract; the abstract member bodies are not used as ordinary implementation behavior for structural implementations.

### Important limitation

It does not automatically enforce runtime behavior.

### Use case

Repositories, gateways, model clients, plugin boundaries, and test seams.

### Common mistake

Assuming implementations must inherit from the Protocol.

---

## 187. `typing.runtime_checkable`

### Purpose

Marks a Protocol so it can participate in limited runtime structural checks.

### Syntax

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Closable(Protocol):
    def close(self) -> None:
        ...
```

### Return behavior

The decorator returns the Protocol class after enabling runtime checking behavior.

### Exceptions

Applying it to a non-Protocol class raises `TypeError`.

### Important limitation

Runtime checks do not fully validate signatures or semantic behavior.

### Common mistake

Treating it as a runtime type-validation framework.

---

## 188. `typing.TypeVar`

### Purpose

Defines a type variable for generic typing.

### Syntax

```python
from typing import TypeVar


T = TypeVar("T")
```

### Use case

Reusable contracts such as repositories.

### Common mistake

Using generics when no meaningful type relationship exists.

---

## 189. `typing.Generic`

### Purpose

Historically used to define generic classes explicitly.

Modern Python supports newer generic syntax, but `Generic` remains relevant for compatibility and existing code.

### Example

```python
from typing import Generic, TypeVar


T = TypeVar("T")


class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
```

### Practical use

Generic wrappers, repositories, containers, and libraries.

---

## 190. `typing.Callable`

A callable dependency can also be expressed with `Callable`.

```python
from collections.abc import Callable


def apply(operation: Callable[[int], int], value: int) -> int:
    return operation(value)
```

A callable Protocol is more expressive when you need a named contract or additional members.

### Common mistake

Using a class hierarchy when a callable type already expresses the requirement.

---

## 191. `abc.ABC`

### Purpose

Provides a convenient base class for abstract base classes.

### Example

```python
from abc import ABC, abstractmethod


class Repository(ABC):
    @abstractmethod
    def save(self, value) -> None:
        ...
```

### Use case

Nominal domain families and shared implementations.

---

## 192. `abc.abstractmethod`

### Purpose

Marks a method as abstract.

### Syntax

```python
class Service(ABC):
    @abstractmethod
    def run(self) -> None:
        ...
```

### Important

An abstract method can contain an implementation, but concrete subclasses still need to implement required abstract members to become instantiable.

### Common mistake

Assuming abstract means the method body must be empty.

---

## 193. `__call__`

### Purpose

Makes an object callable:

```python
class Predictor:
    def __call__(self, value: float) -> float:
        return value * 2
```

Then:

```python
predictor = Predictor()
print(predictor(3.0))
```

Expected:

```text
6.0
```

### Use case

Strategies, model wrappers, transformations, and callable test doubles.

---

## 194. `isinstance()` With Runtime Protocols

Example:

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Runnable(Protocol):
    def run(self) -> None:
        ...


class Job:
    def run(self) -> None:
        pass


assert isinstance(Job(), Runnable)
```

### Important

This is a limited runtime structural check.

---

## 195. `issubclass()` With Runtime Protocols

A runtime-checkable Protocol can participate in supported class-level structural checks.

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Closable(Protocol):
    def close(self) -> None:
        ...


class Resource:
    def close(self) -> None:
        pass


assert issubclass(Resource, Closable)
```

### Important limitation

Class-level runtime checks are less informative for protocols involving instance-only data attributes. Use object-level checks and static typing where appropriate.

---

## 196. `typing.Callable` and Callable Protocols

Python also provides callable type annotations through `Callable`.

In modern code, callable types are commonly imported from `collections.abc`:

```python
from collections.abc import Callable


def apply(operation: Callable[[int], int], value: int) -> int:
    return operation(value)
```

`typing.Callable` is also part of Python's typing vocabulary and may appear in existing code or in compatibility-focused code.

### When to use Callable

Use a callable type when the dependency is simply a function/callable with a known signature.

### When to use a callable Protocol

Use a callable Protocol when you need a named contract and potentially want to describe additional attributes or methods alongside `__call__()`.

### Common mistake

Creating a full object hierarchy when a callable type already expresses the dependency.

---

## 197. Why `__get__` Matters Only as Background

Descriptors are part of Python's attribute-access machinery, and methods/properties are examples of descriptor-driven behavior.

For this chapter, you only need the connection:

```text
Protocol
    → typing contract

property/method
    → Python descriptor machinery
```

You do not need to implement a custom `__get__()` descriptor to use Protocols or dependency inversion.

The purpose of this topic is to prevent a common conceptual mistake:

> Type-level interfaces and Python's runtime attribute machinery are related areas, but they are not the same mechanism.

---

# PRODUCTION TRADE-OFFS

## 198. Abstraction Boundary vs Indirection

Suppose the production path is:

```text
Application
  ↓
Protocol
  ↓
Adapter
  ↓
SDK Client
  ↓
External API
```

That is more code than:

```text
Application
  ↓
SDK Client
```

The extra layers are justified when they isolate a meaningful change boundary.

### Useful reasons

- external vendor may change;
- multiple providers exist;
- tests need deterministic fakes;
- business logic should not know transport details;
- the implementation has a different lifecycle;
- different environments need different implementations.

### Costs

- more names to navigate;
- more code;
- more construction/wiring;
- more interfaces to maintain;
- possible duplication.

### Decision

Do not optimize for the smallest line count. Optimize for appropriate boundaries and understandable change.

---

## 199. One Implementation Does Not Automatically Mean No Abstraction

A Protocol can still be useful with one current implementation when the boundary is important.

Examples:

```text
production database boundary
clock boundary for deterministic tests
LLM provider boundary
external payment gateway
```

A second implementation may appear later, but the stronger reason can be architectural isolation rather than future speculation.

### Conversely

Multiple implementations do not automatically justify a giant Protocol.

If implementations differ in several unrelated ways, use multiple focused contracts.

---

## 200. Dependency Inversion and Functional Style

Dependency inversion is compatible with functional programming.

Example:

```python
def process(records, validator, formatter):
    valid = [record for record in records if validator(record)]
    return formatter(valid)
```

Here:

```text
validator
formatter
```

are explicit dependencies.

No class hierarchy is necessary.

### Why this matters

Applied AI systems often combine styles:

```text
data models
+ functions
+ classes
+ Protocols
+ composition
```

Do not force every dependency into a class.

---

## 201. Dependency Inversion and Object-Oriented Design

Object-oriented code frequently uses Protocols and composition:

```python
class Service:
    def __init__(self, repository, clock) -> None:
        self.repository = repository
        self.clock = clock
```

Functional-style code may use parameters:

```python
def create_event(data, clock):
    timestamp = clock.now()
    ...
```

Both can express dependency inversion.

The principle is about **dependency direction**, not about class count.

---

## 202. Dependency Graph Cycles

A dependency graph should be inspected for cycles.

Problematic conceptual graph:

```text
Service A
   ↓
Service B
   ↓
Service A
```

This can make:

- initialization harder;
- testing harder;
- ownership unclear;
- architecture brittle.

### Protocols do not automatically solve cycles

You can still create:

```text
Protocol A ← implementation B
Protocol B ← implementation A
```

The important design question is whether the responsibilities should actually depend on each other.

### Production lesson

Use abstractions to improve dependency direction, not to hide cycles.

---

## 203. Dependency Injection and Resource Lifecycle

Consider a database connection.

```python
class Repository:
    def __init__(self, connection) -> None:
        self.connection = connection
```

The repository does not necessarily own the lifetime of the connection.

A composition root or resource manager may create and close it.

### Questions to ask

```text
Who created the resource?
Who should close it?
Can it be shared?
Is it thread-safe?
What is the process lifecycle?
```

### Production lesson

Dependency injection makes ownership explicit, but it does not automatically define resource lifetime. That must be designed.

---

## 204. Dependency Injection and Configuration Scope

Configuration may have multiple scopes:

```text
application defaults
      ↓
worker configuration
      ↓
service instance configuration
      ↓
request-specific overrides
```

A Protocol does not decide the scope.

For example, an LLM service might receive:

```python
class GenerationConfig:
    temperature: float
    max_tokens: int
```

while a request overrides:

```text
temperature
```

The architecture must state which layer owns which value.

---

# PRODUCTION APPLICATION PATTERNS

## 205. Repository Port

A repository port should expose business-relevant persistence operations.

Example:

```python
from typing import Protocol


class UserRepository(Protocol):
    def find_by_id(self, user_id: str):
        ...

    def save(self, user) -> None:
        ...
```

Avoid exposing low-level SQL connection APIs unless the application genuinely requires them.

### Production lesson

Model persistence behavior around use cases, not around every database capability.

---

## 206. Gateway Port

A gateway represents an external service capability.

```python
class ShippingGateway(Protocol):
    def create_shipment(self, order_id: str) -> str:
        ...
```

Adapter:

```python
class CarrierAdapter:
    def __init__(self, client) -> None:
        self.client = client

    def create_shipment(self, order_id: str) -> str:
        response = self.client.create_shipment(order_id)
        return response.tracking_id
```

The application receives a tracking ID rather than a vendor-specific response object.

### Production lesson

The adapter can normalize provider-specific data at the boundary.

---

## 207. Clock Port

Time is a classic deterministic-test boundary.

```python
from datetime import datetime, timezone
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
```

Test implementation:

```python
class FixedClock:
    def __init__(self, value: datetime) -> None:
        self.value = value

    def now(self) -> datetime:
        return self.value
```

### Production lesson

Injecting time can remove nondeterminism from business tests.

---

## 208. Configuration Port vs Configuration Object

Not everything needs a Protocol.

This may be enough:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceConfig:
    timeout: int
    retries: int
```

A configuration object is data.

A Protocol is more appropriate when a dependency has behavior that can vary.

Compare:

```text
Config → values
Protocol → behavior/capability
```

This is a useful distinction for production design.

---

## 209. Tool Port for Agentic Systems

A tool boundary can be:

```python
class Tool(Protocol):
    @property
    def name(self) -> str:
        ...

    def run(self, input: str) -> str:
        ...
```

In a production system, richer contracts might include:

- structured argument schema;
- authentication context;
- authorization decision;
- timeout;
- cancellation;
- result metadata;
- error classification;
- idempotency requirements.

Do not automatically combine every concern into one Protocol. Separate capabilities when consumers and lifecycles differ.

---

## 210. Memory Port for LLM and Agent Systems

A memory interface might be:

```python
class Memory(Protocol):
    def add(self, message: str) -> None:
        ...

    def recent(self, limit: int = 10) -> list[str]:
        ...
```

Possible implementations:

```text
InMemoryMemory
RedisMemory
DatabaseMemory
VectorMemory
```

### Architectural question

Does the application need:

```text
recent messages
semantic retrieval
long-term memory
session state
```

If these are distinct capabilities, split them rather than creating one universal memory interface.

---

## 211. Model Port for ML/LLM Systems

A common model port:

```python
class Model(Protocol):
    def generate(self, prompt: str) -> str:
        ...
```

But real systems may need multiple capabilities:

```text
Generate
Stream
Embed
Moderate
CountTokens
ToolCall
```

Do not force all providers into one generic interface if features differ significantly.

A capability-oriented design can be:

```python
class Generator(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class Streamer(Protocol):
    def stream(self, prompt: str):
        ...
```

### Production lesson

Model interfaces should reflect actual application needs, not every vendor feature.

---

# FINAL SUMMARY

## 212. The Complete Learning Path

The chapter should now be understood as one connected sequence:

```text
Concrete dependency
      ↓
Tight coupling
      ↓
Identify required behavior
      ↓
Interface / contract
      ↓
Duck typing
      ↓
Structural typing
      ↓
Protocol
      ↓
ABC comparison
      ↓
Dependency inversion
      ↓
Dependency injection
      ↓
Composition root
      ↓
Adapter
      ↓
Ports and adapters
      ↓
Test doubles
      ↓
Production boundaries
```

### The central lesson

Do not ask only:

> "How do I use Protocol?"

Ask:

> "What dependency do I have, what capability does the consumer need, what implementation details should remain outside, and does an abstraction make that boundary easier to change and test?"

---

## 213. Applied AI Engineering Mental Model

For production AI systems, think in boundaries:

```text
                Application / Agent
                         |
          +--------------+--------------+
          |              |              |
       Model          Memory           Tools
      Protocol        Protocol         Protocol
          ^              ^              ^
          |              |              |
     Cloud/local      DB/cache       APIs/SDKs
       adapters        adapters        adapters
```

And for data platforms:

```text
Pipeline
   |
DataSource Protocol
   ^
+--+---------+----------+
|            |          |
API        File      Database
Adapter    Adapter    Adapter
```

The application core remains focused on policy while implementations remain replaceable.

---

## 214. Final Decision Checklist

Before writing a Protocol:

```text
WHAT?
What capability does the consumer need?

WHY?
Why is a boundary useful?

VARIATION?
Can implementation vary independently?

BOUNDARY?
Is this an external/infrastructure seam?

TESTING?
Does a fake implementation help?

SCOPE?
Should the dependency be constructor-, method-, or function-injected?

CONTRACT?
What behavior must implementations guarantee?

RUNTIME?
Do I actually need runtime checking?

STATIC?
Would mypy/pyright improve confidence?

ARCHITECTURE?
Where should the concrete implementation be created?

COMPLEXITY?
Does the abstraction reduce complexity?
```

If the answers are weak, keep the design simple.

---

# SELF-REVIEW

## 215. Final Self-Review

Before saving the chapter, verify:

- [x] Beginner explanation exists.
- [x] Tight coupling is explained first.
- [x] Dependencies are explained.
- [x] Coupling is explained.
- [x] Interfaces are explained.
- [x] Contracts are explained.
- [x] Interface versus implementation is explained.
- [x] Duck typing is explained.
- [x] Structural typing is explained.
- [x] Nominal typing is explained.
- [x] `Protocol` is explained.
- [x] Method Protocols are explained.
- [x] Attribute Protocols are explained.
- [x] Property Protocols are explained.
- [x] Protocol inheritance is explained.
- [x] Protocol composition is explained.
- [x] Generic Protocols are explained.
- [x] Callable Protocols are explained.
- [x] `runtime_checkable` is explained.
- [x] Runtime limitations are explained.
- [x] Runtime Protocol checks are distinguished from static checking.
- [x] `isinstance()` is covered with runtime-checkable Protocols.
- [x] `issubclass()` is covered with limitations.
- [x] Protocol introspection is covered without depending on private internals.
- [x] ABCs are explained.
- [x] `abc.ABC` is covered.
- [x] `abstractmethod` is covered.
- [x] Modern ABC decorator combinations are shown.
- [x] Legacy abstract decorator aliases are treated as deprecated/redundant.
- [x] Protocol versus ABC is compared.
- [x] Duck typing versus Protocol versus ABC is compared.
- [x] Interface Segregation is explained.
- [x] DIP is explained.
- [x] DI is explained.
- [x] Constructor injection is explained.
- [x] Function/parameter injection is explained.
- [x] Method injection is explained.
- [x] Factory injection is explained.
- [x] Configuration injection is explained.
- [x] IoC is explained.
- [x] DIP, DI, and IoC are explicitly distinguished.
- [x] Composition root is explained.
- [x] Dependency graph is explained.
- [x] Adapters are explained.
- [x] Ports and adapters / hexagonal architecture are explained.
- [x] Clean Architecture connection is explained.
- [x] Testability is explained.
- [x] Fakes, stubs, mocks, and spies are distinguished.
- [x] Protocol-based test doubles are shown.
- [x] Common DI mistakes are explained.
- [x] Common Protocol mistakes are explained.
- [x] When not to use Protocol is explained.
- [x] When to use Protocol is explained.
- [x] Over-engineering is discussed.
- [x] Backend example exists.
- [x] Data engineering example exists.
- [x] ML example exists.
- [x] LLM example exists.
- [x] Agentic AI example exists.
- [x] Banking example exists.
- [x] API client example exists.
- [x] At least 24 exercises exist.
- [x] Every exercise includes Problem, Requirements, Expected behavior, Solution, Explanation, and Key learning.
- [x] At least 6 debugging scenarios exist.
- [x] Every debugging scenario includes broken code, expected behavior, actual behavior, clues, investigation, root cause, fix, explanation, and production lesson.
- [x] Mini-project exists.
- [x] Mini-project includes Protocols, dependency inversion, dependency injection, adapters, tests, logging, and a composition root.
- [x] Interview questions exist.
- [x] Architecture questions exist.
- [x] Knowledge check exists.
- [x] Common misconceptions exist.
- [x] Production checklist exists.
- [x] Final mental model exists.
- [x] `typing.Protocol` is covered.
- [x] `typing.runtime_checkable` is covered.
- [x] `TypeVar` is covered.
- [x] `Generic` is covered.
- [x] `Callable` is covered.
- [x] `__call__` is covered.
- [x] `ABC` and `abstractmethod` are covered.
- [x] `isinstance()` and `issubclass()` are covered.
- [x] mypy and pyright are covered conceptually.
- [x] Static typing is clearly separated from runtime behavior.
- [x] Type compatibility is clearly separated from behavioral compatibility.
- [x] DIP is clearly separated from DI and IoC.
- [x] No claim says Protocol requires inheritance.
- [x] No claim says Protocol automatically enforces runtime behavior.
- [x] No claim says `runtime_checkable` performs complete signature validation.
- [x] No claim says static typing proves behavioral correctness.
- [x] No claim says DI requires a framework.
- [x] No claim says every class needs a Protocol.
- [x] No claim says more abstraction is always better.
- [x] No real credentials or API keys are used.
- [x] Content progresses Basic → Intermediate → Advanced → Production.
- [x] The topic remains focused on Protocols, interfaces, and dependency inversion.

---

## 216. File-Scope Verification

This task changes only:

```text
08-Object-Oriented-Design-Data-Modelling-and-Functional-Style/05-protocols-interfaces-and-dependency-inversion.md
```

No other file should be modified, created, deleted, renamed, or updated as part of this chapter.
