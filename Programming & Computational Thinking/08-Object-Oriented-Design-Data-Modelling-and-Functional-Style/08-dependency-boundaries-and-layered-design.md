# Dependency Boundaries and Layered Design

This chapter develops a practical production-engineering skill: designing Python systems so that **dependencies cross deliberate boundaries and responsibilities remain understandable as the codebase grows**.

The progression is intentionally concrete:

> **Mixed code → identify responsibilities → identify dependencies → control coupling → define dependency boundaries → dependency direction → dependency injection → Protocols/ports → adapters → layered design → package boundaries → transaction/error/reliability boundaries → production architecture**

The goal is not architectural purity. Real software needs databases, HTTP APIs, files, clocks, queues, cloud services, model runtimes, vector stores, and other effects. The goal is to make those dependencies **visible, owned, testable, replaceable where useful, and correctly directed**, while keeping important business rules independent of volatile implementation details.

> **Production mental model:** high cohesion inside a component, controlled coupling between components, explicit dependency direction, and boundaries that protect stable policy from volatile details.

> **Learning sequence:** Start with ordinary Python code before introducing architecture labels. First learn to see the problem. Then learn the boundary vocabulary that solves that problem.

## Architectural lens for this chapter

A useful distinction is:

```text
WHAT the system must do
    = domain / business policy

WHAT sequence completes the use case
    = application orchestration

HOW the process talks to the outside world
    = infrastructure / adapters

HOW users, APIs, jobs, and messages enter
    = presentation / inbound adapters
```

The same concepts can be represented with classes, functions, modules, packages, or a combination. The architecture is not the folder tree; it is the **responsibility map and dependency graph**.


## 1. Learning Objectives

By the end of this chapter, the learner should be able to:

- identify dependencies between values, functions, classes, modules, packages, and external systems;
- distinguish direct, indirect, hidden, and explicit dependencies;
- analyze coupling and cohesion;
- identify domain logic, application logic, infrastructure, and presentation responsibilities;
- extract important business rules from mixed code;
- define explicit dependency boundaries and explain why the boundary exists;
- reason about dependency direction instead of merely counting interfaces;
- distinguish Dependency Injection, Dependency Inversion, and Inversion of Control;
- use constructor, function, method, and factory injection without requiring a container;
- use `Protocol` or `ABC` when a real abstraction boundary exists;
- understand ports, adapters, inbound adapters, and outbound adapters;
- explain layered architecture, hexagonal architecture, Clean Architecture concepts, feature-based organization, and Functional Core / Imperative Shell;
- separate domain models, DTOs, persistence models, and serialized representations where useful;
- design package/module boundaries and prevent circular dependency problems;
- design repository, gateway, clock, configuration, filesystem, HTTP, queue, and model-provider boundaries;
- reason about transaction ownership, Unit of Work, error translation, retries, idempotency, and outbox workflows;
- design test strategies that combine unit, fake/mock, contract, integration, and end-to-end tests;
- reason about async, concurrency, distributed systems, and event-driven boundaries;
- apply the same design thinking to backend services, data engineering, ML systems, LLM applications, RAG, and agentic AI;
- decide when a boundary adds meaningful value and when it would be unnecessary architecture.


## 2. Prerequisites

The learner should already have seen the concepts below, but mastery is not assumed.

Prerequisites are:

- functions, parameters, arguments, and return values;
- variables and scopes;
- lists, dictionaries, tuples, and basic classes/objects;
- instance state;
- pure functions and basic immutability;
- Protocols/interfaces and dependency inversion;
- dependency injection;
- exceptions;
- pytest-level testing fundamentals.

Do not assume mastery. Throughout the chapter, concepts such as hidden dependencies, state, validation, exceptions, and interfaces are briefly refreshed when needed.


## 3. Start With a Real Problem

Start with an intentionally mixed function:

```python
def process_order(order_id, database, send_email, http_client):
    response = http_client.get(
        f"https://example.invalid/orders/{order_id}",
        timeout=5,
    )
    order = response.json()

    customer = database.get_customer(order["customer_id"])
    subtotal = sum(
        item["price"] * item["quantity"]
        for item in order["items"]
    )
    tax = subtotal * 0.18
    total = subtotal + tax

    database.save_total(order_id, total)
    send_email(customer["email"], f"Order total: {total:.2f}")
    return total
```

The calculation of `subtotal`, `tax`, and `total` is domain-oriented. The HTTP request, customer lookup, database write, and email send are effects. The overall function is also orchestration.

This is the starting problem:

```text
Mixed function
   |
   +--> external effects
   +--> parsing
   +--> business rules
   +--> orchestration
```

The chapter will repeatedly ask:

> **Which part of this code is actually the business rule?**


## 4. Mental Model: Inside vs Outside

A useful beginner mental model is to divide work into three broad categories:

```text
DOMAIN
  What does the business/problem mean?
  - pricing rules
  - eligibility
  - validation of domain invariants
  - state transitions
  - deterministic transformations

APPLICATION
  What sequence of work completes this use case?
  - load data
  - invoke domain rules
  - call external capabilities
  - save results
  - publish notifications

INFRASTRUCTURE
  How does the process talk to other systems?
  - SQL
  - HTTP
  - filesystem
  - queue
  - cloud storage
  - LLM provider
  - vector database
```

These categories are useful boundaries, not universal folder names. A real codebase may combine or rename them.

A second mental model is:

```text
                    Outside world
       DB / HTTP / Files / Queue / Clock / LLM
                         |
                         v
                 Effect boundary
                         |
                         v
                 Application flow
                         |
                         v
                 Domain decisions
```


## 5. What Is Domain Logic?

**Domain logic** means rules and decisions that express what the business or problem domain is supposed to do.

Examples:

- tax calculation;
- discount policy;
- eligibility;
- transfer validation;
- account rules;
- order constraints;
- normalization that has domain meaning;
- policy checks for an AI agent.

Domain logic is not synonymous with “a domain class.” It can be a function, value object, entity method, policy object, or explicit state transition.

A useful test is:

> If I changed the database from PostgreSQL to another storage system, would this rule still describe the same business behavior?

If yes, it is a strong candidate for domain logic.


## 6. Domain Logic vs Application Logic

**Domain logic** answers “What rule applies?”

**Application logic** answers “What steps should the application perform to complete this use case?”

```text
Application Service
    |
    +--> Load Order
    |
    +--> Load Customer
    |
    +--> Apply Domain Rule
    |
    +--> Save Result
    |
    +--> Send Notification
```

Domain:

```python
def calculate_total(subtotal: int, tax_rate: float) -> float:
    if subtotal < 0:
        raise ValueError("subtotal cannot be negative")
    if not 0 <= tax_rate <= 1:
        raise ValueError("tax_rate must be between 0 and 1")
    return subtotal * (1 + tax_rate)
```

Application:

```python
def complete_order(order_id, repository, tax_rate):
    order = repository.get(order_id)
    total = calculate_total(order.subtotal, tax_rate)
    repository.save_total(order_id, total)
    return total
```

Terminology varies between architectural styles. “Application service,” “use case,” “interactor,” and “handler” may refer to similar responsibilities in different codebases.


## 7. What Is a Side Effect?

A **side effect** is an observable interaction with state or a resource outside the function’s local value transformation.

Common side effects include:

- writing files;
- writing databases;
- HTTP requests;
- queue publication;
- sending email;
- printing;
- logging;
- changing shared mutable state;
- reading current time;
- reading environment configuration;
- randomness;
- model/API calls.

Side effects and I/O overlap but are not identical concepts:

```python
shared_cache = {}

def remember(key, value):
    shared_cache[key] = value
```

This does not perform file or network I/O, but it mutates shared state.

Also:

```python
from datetime import datetime

def current_hour():
    return datetime.now().hour
```

This may not write anything, but it depends on external state: the system clock.


## 8. Pure vs Impure Functions

A practical model for purity is:

1. the result is determined by the relevant explicit inputs;
2. the call does not introduce observable external effects.

Pure:

```python
def calculate_tax(subtotal: float, tax_rate: float) -> float:
    return subtotal * tax_rate
```

Effectful:

```python
def calculate_tax(subtotal: float, repository) -> float:
    tax_rate = repository.load_tax_rate()
    return subtotal * tax_rate
```

The second implementation is not “bad.” It simply has a dependency that belongs at a boundary if the goal is to make the rule independently testable.

Purity improves testability and reasoning, but production systems still need effectful code.


## 9. Why Separation Matters

Side effects are easiest to control when they are named and localized.

```text
Pure:
  calculate
  validate
  transform
  decide

Effect:
  load
  save
  send
  publish
  fetch
  now
  randomize
  log
```

A function may have both domain calculations and effects, but every extra mixed responsibility increases the number of reasons a test can fail.

Useful review questions:

- What outside state can this function observe?
- What outside state can it modify?
- Could I replay the call with the same explicit inputs?
- Could I unit-test the rule without a database or network?


## 10. Identifying Side Effects and Effects

| Property | Domain-focused pure function | Effectful function |
|---|---|---|
| Inputs visible in signature | Usually | Not always |
| Depends on external state | Ideally no | Often |
| Mutates shared state | No | May |
| I/O | No | Often |
| Direct unit testing | Usually easy | Often needs setup/doubles |
| Deterministic replay | Usually easier | Often harder |
| Provider replacement | Irrelevant | Important |
| Retry semantics | Usually simple | Potentially dangerous |
| Concurrency reasoning | Often simpler | Requires resource/state analysis |

Do not confuse “pure” with “returns a value.” A function can return a value while performing a database write.


## 11. Why Separation Matters in Production

Separation helps because:

- pure business rules can be unit-tested independently;
- infrastructure failures can be diagnosed separately from rule failures;
- provider changes affect adapters rather than every domain function;
- configuration, time, and randomness become explicit dependencies;
- concurrent code has less hidden shared state;
- important workflows are easier to replay and debug.

However, separation does not automatically create a good architecture. You can produce a deeply layered system with unclear ownership. The boundary must earn its complexity.


## 12. Identifying Domain Logic in Mixed Code

For a mixed function, classify each operation.

Ask:

1. Does it calculate a domain value?
2. Does it apply a business rule?
3. Does it read external state?
4. Does it write external state?
5. Does it communicate with another process/service?
6. Does it depend on time, randomness, or environment?
7. Does it convert transport data into application/domain data?
8. Does it orchestrate other operations?

Example:

```python
def checkout(order_id, repository, payment, clock):
    order = repository.get(order_id)              # effect
    if order is None:
        raise LookupError("order not found")      # application/domain error boundary

    if order.expires_at <= clock.now():            # external time + domain rule
        raise ValueError("order expired")

    total = calculate_total(order)                # pure rule
    payment.charge(order.customer_id, total)     # effect
    repository.mark_paid(order_id)                # effect
    return total
```

The classification is more important than the exact architecture vocabulary.


## 13. Extracting Pure Business Rules

Refactor by extracting the business rule:

```python
def calculate_order_total(order, tax_rate):
    subtotal = sum(
        item.price * item.quantity
        for item in order.items
    )
    return subtotal * (1 + tax_rate)
```

Then orchestrate outside it:

```python
def process_order(order_id, repository, tax_rate):
    order = repository.get(order_id)
    total = calculate_order_total(order, tax_rate)
    repository.save_total(order_id, total)
    return total
```

Now the core rule accepts the values it needs. This is the central refactoring move of the chapter:

> **Replace “discover dependencies inside the rule” with “supply dependencies from outside.”**


## 14. Functional Core / Imperative Shell

### Functional Core

A functional core contains as much as practical of:

- deterministic calculations;
- business rules;
- validation;
- transformations;
- policy decisions;
- explicit state transitions.

### Imperative Shell

An imperative shell performs or coordinates:

- database I/O;
- HTTP;
- filesystem;
- queues;
- time;
- randomness;
- configuration;
- logging/metrics/traces;
- LLM/model calls.

```text
             External World
                   |
                   v
        +-------------------------+
        |     Imperative Shell    |
        | DB / HTTP / Files       |
        | Queue / Clock / LLM     |
        +------------+------------+
                     |
                     v
        +-------------------------+
        |     Functional Core     |
        | validation              |
        | business rules          |
        | calculations            |
        | transformations         |
        | decisions               |
        +-------------------------+
```

The shell is not “bad code.” It exists because production software interacts with reality.


## 15. Functional Core Does Not Mean Zero State

A functional core can operate on state without hiding that state.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CounterState:
    value: int


def apply_event(state: CounterState, event: str) -> CounterState:
    if event == "increment":
        return CounterState(state.value + 1)
    if event == "decrement":
        return CounterState(state.value - 1)
    raise ValueError(f"unsupported event: {event}")
```

The function is a state transition:

```text
old state + event -> new state
```

The pattern does not require every data structure to be immutable. The important idea is that the state being transformed is explicit rather than hidden in shared process-wide mutation.


## 16. Imperative Shell

A shell can be very small or fairly substantial. “Thin” means that business rules are not needlessly buried inside infrastructure orchestration.

```python
def handle_request(request, repository, clock):
    order = repository.load(request.order_id)
    now = clock.now()

    result = calculate_result(order, now)

    repository.save(result)
    return result
```

The shell owns:

- loading;
- obtaining the clock value;
- saving.

The domain rule owns the calculation.

A larger workflow can still have a well-designed shell when each call has a clear purpose.


## 17. Dependency Boundaries

Dependency boundaries are deliberate seams between application behavior and external systems.

Typical boundaries:

```text
Database
HTTP API
Filesystem
Message Queue
Clock
Random source
Configuration
LLM provider
Vector store
Cloud object store
```

The useful rule is:

> **Push provider mechanics outward; pull only the data or capability the application actually needs inward.**

For example, a pricing rule usually needs a `tax_rate`, not a database connection.


## 18. Dependency Injection

Dependency injection means supplying a dependency from outside.

Bad coupling:

```python
class OrderService:
    def __init__(self):
        self.repository = PostgresOrderRepository()
```

Explicit dependency:

```python
class OrderService:
    def __init__(self, repository):
        self.repository = repository
```

Composition:

```python
service = OrderService(repository=PostgresOrderRepository())
```

A Protocol can document a boundary:

```python
from typing import Protocol


class OrderRepository(Protocol):
    def get(self, order_id: str):
        ...

    def save(self, order) -> None:
        ...
```

Dependency injection is not the same thing as dependency inversion, and neither requires a DI framework.


## 19. Ports and Adapters

A **port** is an application-facing boundary describing an interaction the application needs.

An **adapter** connects that boundary to a concrete external system.

```text
External Provider
       |
       v
    Adapter
       |
       v
  Port / Protocol
       |
       v
Application Core
```

Examples:

| Port | Adapter |
|---|---|
| `OrderRepository` | PostgreSQL repository |
| `PaymentGateway` | provider HTTP client |
| `EmailSender` | SMTP/API adapter |
| `LLMClient` | cloud/local model adapter |
| `VectorStore` | vector database adapter |
| `ObjectStore` | S3-like storage adapter |

The boundary matters more than the naming.


## 20. Hexagonal Architecture

Hexagonal architecture (ports and adapters) keeps the application core relatively independent from external technologies.

```text
            HTTP Adapter
                 |
        +--------v--------+
DB ---> |      CORE       | <--- LLM Adapter
        +--------+--------+
                 |
            Queue Adapter
```

The “hexagon” is conceptual. The architecture is about:

- inside/outside boundaries;
- dependency direction;
- replaceable external implementations;
- keeping business/application policy independent from provider details.

Not every system needs every adapter abstraction.


## 21. Clean Architecture Connection

Clean Architecture commonly separates:

- domain/entities and business rules;
- use cases/application behavior;
- interface/boundary concerns;
- infrastructure/framework details.

The important relationship is conceptual:

```text
Stable business policy
        ^
        |
   application policy
        ^
        |
external implementations
```

Different teams use different folder layouts. Do not treat one folder tree as mandatory. Evaluate whether the dependency direction makes business rules easier to understand and change.


## 22. Layered Architecture

A common layered model is:

```text
Presentation
    |
Application
    |
Domain
    |
Infrastructure
```

A simple layered application may permit direct calls downward. A dependency-inverted design may instead define ports near the core and let infrastructure implement them.

| Architecture | Strength | Risk |
|---|---|---|
| Simple layers | low cognitive load | leakage between layers |
| Dependency-inverted layers | stronger boundaries | added indirection |
| Ports/adapters | good external isolation | more concepts |

Choose based on the actual system.


## 22A. Dependency Rules for Layers

A layered design becomes useful when the allowed dependencies are explicit.

A common conceptual rule is:

```text
Presentation
     ↓
Application
     ↓
Domain
```

Infrastructure may implement the contracts needed by the application/domain side:

```text
Application / Domain
        ↑
   Protocol / Port
        ↑
Infrastructure Adapter
```

The important point is that the exact arrow direction depends on where the contract is owned. In a dependency-inverted design, the application can own a port while infrastructure implements it.

### Rule 1 — Keep direction intentional

Avoid accidental graphs such as:

```text
Presentation → Domain → Infrastructure → Presentation
```

That cycle usually signals unclear responsibility.

### Rule 2 — Stable policy should not know volatile implementation detail unnecessarily

A tax rule may depend on `tax_rate`; it does not need to know the SQL syntax that retrieved it.

### Rule 3 — Dependencies should point toward the reason for change

If a provider SDK changes frequently while a business rule changes rarely, a boundary can prevent provider churn from spreading through the business code.

### Rule 4 — Do not make the layer diagram stricter than the use case requires

Some systems legitimately allow application code to query a data-access abstraction directly. Some small systems skip an application layer altogether.

The engineering question is always:

> **What dependency relationship makes this system easiest to change safely?**

## 22B. Conceptual Layers vs Physical Modules

A layer is a **responsibility concept**. A module is a Python file. A package is a Python namespace/grouping mechanism.

They are related, but not identical:

```text
Architecture concept       Python mechanism
-----------------------    -----------------
Domain layer               domain package/modules
Application layer          application modules
Infrastructure layer       infrastructure modules
Presentation layer         API/CLI/consumer modules
Boundary contract          Protocol / ABC / callable / data model
```

A folder named `domain/` does not prove that the code is domain logic. You must inspect its imports and responsibilities.

Conversely, a single `app.py` can contain conceptually separated functions if the system is small enough.

## 22C. Feature-Based Organization

A large application does not have to organize every file by technical layer.

Layer-oriented layout:

```text
controllers/
services/
repositories/
models/
```

Feature-oriented layout:

```text
accounts/
orders/
payments/
notifications/
```

Feature-based organization can improve **change locality** because the behavior for one capability lives close together.

A hybrid can work well:

```text
orders/
    api.py
    application.py
    domain.py
    ports.py
    persistence.py

payments/
    api.py
    application.py
    domain.py
    ports.py
    gateway.py

shared/
    infrastructure/
```

Use feature boundaries when they improve cohesion and ownership. Do not turn every file into an independent architecture layer.

## 22D. Dependency Graph Thinking

Before creating interfaces, draw a dependency graph.

```text
CLI ────────┐
REST API ───┼──→ Application Service ──→ Domain Rules
Worker ─────┘              |
                           v
                     Ports / Contracts
                       ^        ^
                       |        |
                    DB Adapter  LLM Adapter
                       |        |
                       v        v
                    Database  Model API
```

Now ask:

- Which nodes are stable?
- Which nodes are volatile?
- Which nodes are expensive to test?
- Which dependency edges are business-relevant?
- Which edges should be inverted?
- Which edges are unnecessary?

This is often more valuable than memorizing the names of architecture styles.

## 22E. When a Layer Should Stay Thin, and When It Should Not

“Thin controller” and “thin service” are heuristics, not line-count targets.

A layer is useful when it owns a meaningful responsibility. A 30-line application service that coordinates a transaction, domain policy, and two external ports can be architecturally substantial. A 300-line service full of validation, SQL, HTTP parsing, and formatting is usually doing too much.

Judge thickness by **responsibility density**, not by line count alone.

## 23. Domain Models

Domain models express concepts meaningful to the problem.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str


@dataclass(frozen=True)
class OrderItem:
    sku: str
    quantity: int
    unit_price: Money
```

Domain models may contain:

- invariants;
- value semantics;
- identity;
- explicit state;
- domain behavior.

They do not need to be ORM entities. Separating persistence representation from domain representation can reduce infrastructure leakage, but small systems may reasonably use a shared model.


## 24. Domain Invariants

An invariant is a condition that valid domain state or an allowed operation must satisfy.

```python
def calculate_discount(price: float, percentage: float) -> float:
    if price < 0:
        raise ValueError("price cannot be negative")
    if not 0 <= percentage <= 100:
        raise ValueError("percentage must be between 0 and 100")
    return price * percentage / 100
```

Distinguish:

- structural validation: “Is the request shape usable?”
- domain validation: “Is this operation allowed?”
- infrastructure validation: “Can this provider accept the request?”

Where validation lives depends on the responsibility and trust boundary.


## 25. Input Validation vs Domain Validation

Input validation asks whether data is structurally usable:

- required fields;
- shape;
- parsing;
- type constraints;
- serialization format.

Domain validation asks whether the operation follows business rules:

- quantity limits;
- discount policy;
- transfer rules;
- account constraints.

A web framework may reject malformed JSON at the edge. A domain rule may still reject a perfectly well-formed request because the business operation is invalid.


## 26. DTO vs Domain Model

A DTO is primarily boundary/transport data.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderRequest:
    customer_id: str
    items: list[dict]
```

A domain model represents domain meaning:

```python
@dataclass(frozen=True)
class OrderItem:
    sku: str
    quantity: int
    unit_price: int
```

DTOs are useful when external representations evolve independently from internal concepts. They are not mandatory in every application.


## 27. Serialization Boundaries

Keep serialization near the boundary:

```text
JSON
  |
  v
Deserialize / validate
  |
  v
DTO
  |
  v
Domain model
  |
  v
Business rules
  |
  v
Domain result
  |
  v
DTO / serialization
  |
  v
JSON
```

This avoids forcing domain code to know transport-specific field names and representation details. It also helps with versioning and API contracts.


## 28. Database Boundary

SQL belongs naturally to the database boundary when the application is using a relational database.

Mixed:

```python
def calculate_discount(order_id, connection):
    row = connection.execute(
        "SELECT total, tier FROM orders WHERE id = ?",
        (order_id,),
    ).fetchone()
    return row["total"] * (0.20 if row["tier"] == "gold" else 0.05)
```

Separated:

```python
def calculate_discount(total, tier):
    return total * (0.20 if tier == "gold" else 0.05)


order = repository.get(order_id)
discount = calculate_discount(order.total, order.tier)
```

Do not turn this into “never calculate in SQL.” Large aggregations may belong in the database for performance or locality. The key is knowing which computation is business policy and which is data processing.


## 29. Repository Pattern

A repository presents persistence-oriented operations to the application.

```python
from typing import Protocol


class OrderRepository(Protocol):
    def get(self, order_id: str):
        ...

    def save(self, order) -> None:
        ...
```

A fake can support unit tests:

```python
class InMemoryOrderRepository:
    def __init__(self):
        self.orders = {}

    def get(self, order_id):
        return self.orders.get(order_id)

    def save(self, order):
        self.orders[order.id] = order
```

A repository can reduce persistence coupling, but it should not become a giant abstraction over every feature of the underlying database.


## 30. HTTP/API Boundary

External APIs should be isolated in an adapter or gateway boundary.

Mixed:

```python
def calculate_shipping(order, http_client):
    response = http_client.get(
        "https://example.invalid/rates",
        timeout=5,
    )
    rate = response.json()["rate"]
    return order.total + rate
```

Separated:

```python
def calculate_shipping(order_total, shipping_rate):
    return order_total + shipping_rate


def checkout(order, shipping_client):
    rate = shipping_client.get_rate(order.destination)
    return calculate_shipping(order.total, rate)
```

The adapter owns URL details, serialization, authentication, timeouts, retry policy, and provider-specific failures.


## 31. Filesystem Boundary

Filesystem effects should be separated from parsing when practical.

```python
def read_text(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def parse_document(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


text = read_text("document.txt")
document = parse_document(text)
```

The parser can be tested entirely in memory. The filesystem adapter can be tested separately.

This pattern generalizes to PDF/text extraction, CSV ingestion, object storage, and cloud file systems.


## 32. Clock / Time Boundary

Current time is external state.

Less deterministic:

```python
from datetime import datetime

def is_expired(expiry):
    return datetime.now() > expiry
```

More deterministic:

```python
def is_expired(expiry, now):
    return now > expiry
```

For one function, a timestamp parameter may be the simplest boundary. For a component using time repeatedly, a Protocol can be useful:

```python
from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        ...
```

For timeout measurement, use an elapsed-time-oriented clock appropriate to the runtime rather than assuming wall-clock timestamps are suitable for every timing problem.


## 33. Randomness Boundary

Randomness is not inherently bad; hidden randomness is merely harder to reproduce.

```python
import random

choices = [5, 10, 15]
index = random.randrange(len(choices))
```

A deterministic rule can receive the selected index:

```python
def choose_discount(choices, index):
    return choices[index]
```

This lets tests control the random decision.

When randomness is part of the domain, make the random source or its generated value explicit. For experiments, sampling, exploration, or games, randomness is a legitimate business/system requirement.


## 34. Environment Variables / Configuration

Environment variables are a configuration boundary.

Avoid:

```python
import os

def calculate_limit(amount):
    limit = int(os.getenv("LIMIT", "1000"))
    return min(amount, limit)
```

Prefer:

```python
def calculate_limit(amount, limit):
    return min(amount, limit)
```

Then load configuration at startup:

```python
import os

limit = int(os.getenv("LIMIT", "1000"))
```

The general flow is:

```text
Environment -> configuration -> application -> domain rule
```

This makes configuration visible and improves reproducibility.


## 35. Logging Boundary

Logging, metrics, and traces are observable effects.

Prefer to keep incidental observability near application/effect boundaries:

```python
approved = approve_loan(score, threshold)
logger.info(
    "loan_decision",
    extra={"approved": approved, "score": score},
)
```

However, audit requirements may be part of the domain. A domain operation can produce an explicit audit event as data, and an outer layer can emit that event to logs, an audit store, or a message bus.

The correct rule is not “never log in domain code.” It is “avoid accidental coupling to observability infrastructure when it does not belong there.”


## 36. Database Transactions

Transactions define a local atomicity boundary.

```text
Begin transaction
      |
      v
Load state
      |
      v
Apply business rules
      |
      v
Persist changes
      |
      v
Commit / rollback
```

The application or transaction-owning infrastructure normally decides when to begin and complete the transaction. Domain calculations should not know SQL transaction APIs unless the domain abstraction explicitly includes transactional semantics.

Important limit:

> A local database transaction does not automatically make an external HTTP request, message-broker publish, or payment-provider call atomic with the database.


## 37. Unit of Work

A Unit of Work groups related persistence operations within one transaction boundary.

Illustrative boundary:

```python
from typing import Protocol


class UnitOfWork(Protocol):
    orders: "OrderRepository"

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
```

A Unit of Work can coordinate multiple repository operations. It is useful when a use case has a meaningful local transaction boundary. It is not mandatory and does not solve distributed atomicity.


## 37A. Transaction Ownership vs Domain Ownership

A common mistake is to make a domain object responsible for persistence because the business operation “feels transactional.”

Consider:

```text
Domain rule:
    calculate new state

Application transaction:
    begin
    load state
    calculate new state
    persist new state
    commit
```

The domain owns **meaning**. The application/infrastructure boundary owns **transaction mechanics**.

For example:

```python
def calculate_new_balance(balance: int, amount: int) -> int:
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > balance:
        raise ValueError("insufficient balance")
    return balance - amount
```

A Unit of Work or transaction manager can then coordinate persistence around that result.

This separation matters because the same rule may be used by a synchronous API, batch process, or message consumer while their transaction mechanisms differ.

## 37B. Command, Query, and Effect Ownership

A **command** asks the system to perform a state-changing operation. A **query** asks for information.

```text
Query:
    repository.get_account(id)

Command:
    transfer_money(command)
```

A query is not automatically pure: reading a database is still dependence on external state.

Likewise, a command does not have to put every rule in the application service. A useful shape is:

```text
Command
  ↓
Application orchestration
  ↓
Domain decision
  ↓
Effect boundary
```

This makes side-effect ownership and business ownership visible.

## 38. Error Handling at Boundaries

Different failure types often deserve different handling:

- domain error: invalid business operation;
- application error: use-case/orchestration failure;
- infrastructure error: database/network/provider failure.

Example:

```python
class OrderPersistenceError(RuntimeError):
    pass


def save_order(repository, order):
    try:
        repository.save(order)
    except DatabaseError as exc:
        raise OrderPersistenceError("Could not persist order") from exc
```

`raise ... from ...` preserves the original exception as the cause.

Do not swallow failures with broad `except Exception` blocks unless the boundary has a deliberate, audited reason to do so.


## 39. Retries and Side Effects

Retries belong near effectful operations because that is where transient failure semantics are known.

Typical retryable situations may include:

- transient network timeout;
- throttling;
- temporary provider unavailability;
- temporary connection failures.

A policy may include max attempts, exponential backoff, jitter, timeout budgets, and a classification of retryable versus non-retryable failures.

The critical point is:

> A timeout can mean “the outcome is unknown,” not “the effect definitely did not occur.”

Therefore retries on side effects require idempotency or reconciliation.


## 40. Idempotency

An operation is idempotent when repeating the same logical request does not create unintended additional effects.

Examples:

- setting a status to `closed` can be designed to be idempotent;
- charging a payment is not naturally safe to repeat;
- queue delivery can be duplicated;
- an HTTP client can retry after a timeout.

A common design is:

```text
logical request + stable idempotency key
             |
             v
      check prior result
        /          \
      found        new
       |            |
 return prior    perform effect
 result          and record result
```

Idempotency is a reliability design concern, not just a database detail.


## 41. Command vs Query

A **command** requests a state change. A **query** requests information.

```python
def get_order(order_id):
    ...


def cancel_order(order_id):
    ...
```

A query can still be effectful because it may read a database. The distinction describes intent, not mathematical purity.

This distinction helps when reasoning about caching and retries, but do not assume every query is safe to repeat under every business context.


## 42. Orchestration vs Business Rules

Orchestration sequences collaborators. Business rules explain decisions.

```python
def checkout(order_id, orders, customers, payments):
    order = orders.get(order_id)
    customer = customers.get(order.customer_id)
    result = calculate_checkout(order, customer)
    payments.charge(customer.id, result.amount)
    orders.save(result.order)
    return result
```

Business rule:

```python
def calculate_checkout(order, customer):
    if customer.is_suspended:
        raise ValueError("customer is suspended")
    amount = sum(item.price * item.quantity for item in order.items)
    return CheckoutResult(order=order, amount=amount)
```

The application is effectful. The domain calculation remains explicit.


## 43. Application Services

An application service can be class-based:

```python
class CheckoutService:
    def __init__(self, orders, payments):
        self.orders = orders
        self.payments = payments

    def checkout(self, order_id):
        order = self.orders.get(order_id)
        amount = calculate_total(order)
        self.payments.charge(order.customer_id, amount)
        return amount
```

It can also be a function:

```python
def checkout(order_id, orders, payments):
    order = orders.get(order_id)
    amount = calculate_total(order)
    payments.charge(order.customer_id, amount)
    return amount
```

Use whichever better communicates state, lifecycle, dependency grouping, and the use-case's complexity.


## 44. Function-Based vs Class-Based Application Services

| Concern | Function-based use case | Class-based use case |
|---|---|---|
| Few dependencies | Often concise | Still fine |
| Stateful lifecycle | Less natural | Often clearer |
| Grouping many stable dependencies | Parameter list | Constructor state |
| One-off workflow | Often direct | May be unnecessary |
| Explicitness | High | High when naming is good |
| Testability | Direct call | Inject dependencies on construction |

There is no rule that production architecture must use classes. The class becomes useful when it organizes meaningful state or dependencies.


## 45. Testing Benefits

A separation-oriented test strategy often looks like:

```text
Fast, isolated tests
  -> pure domain rules and transformations

Boundary tests
  -> database, HTTP, file, queue, serialization adapters

Contract tests
  -> important interface/adapter expectations

End-to-end tests
  -> critical workflows through real application wiring
```

This is a heuristic, not an absolute testing pyramid law. The correct mix depends on risk, architecture, and external behavior.


## 46. Test Doubles

Test doubles include:

- **stub:** returns controlled data;
- **fake:** simplified working implementation;
- **mock:** records/asserts expected interactions;
- **spy:** records calls for later assertions.

Example:

```python
class FakePaymentGateway:
    def __init__(self):
        self.charges = []

    def charge(self, customer_id, amount):
        self.charges.append((customer_id, amount))
```

Pure rules usually need fewer mocks because they do not require simulated infrastructure just to calculate a result.

A fake repository tests application behavior against the fake; it does not prove the production database adapter works.


## 47. Debugging Benefits

When a failure occurs, first ask:

1. Is the failure in domain logic?
2. Is the input state wrong?
3. Is a dependency returning unexpected data?
4. Did an external call fail or time out?
5. Is transaction state correct?
6. Did a retry occur?
7. Could the operation have been duplicated?

A pure function can often be replayed with captured inputs. A boundary failure can be investigated at the adapter level. Separation narrows the search space.


## 48. Observability

Useful observability boundaries include the incoming request, application use case, and external adapters.

Log/measure:

- correlation/request ID;
- operation name;
- latency;
- dependency latency;
- retry count;
- outcome/error type;
- safe provider metadata.

Do not put provider SDK imports into domain functions simply because production requires metrics. Keep the domain focused unless the observability requirement is itself part of the business behavior, such as an explicit audit event.


## 49. Async Code

Asynchronous I/O should normally remain near the effect boundary:

```python
async def fetch_customer(client, customer_id):
    return await client.get(customer_id)


def calculate_discount(customer):
    return 0.20 if customer.is_priority else 0.05
```

Do not make every function async just because the outer API framework is async. A pure transformation does not need an event loop merely because its caller performs asynchronous I/O.

Domain logic may legitimately be asynchronous when the domain operation truly depends on asynchronous collaborators; the design should make that reason explicit.


## 50. Concurrency

Concurrency concerns include:

- shared mutable state;
- race conditions;
- concurrent writes;
- task cancellation;
- transaction isolation;
- cache coordination;
- process boundaries.

Explicit state transitions and pure calculations often reduce shared-state coordination, but they do not make a whole system thread-safe automatically.

The important engineering question is:

> **Which state can be observed or changed concurrently, and who owns synchronization for it?**


## 51. Distributed Systems

Distributed systems add independent failure domains:

- network failures;
- partial failures;
- duplicate messages;
- eventual consistency;
- provider-specific retries;
- uncertain operation outcomes;
- clock differences.

A local pure calculation can be deterministic while the overall workflow remains distributed and failure-prone. Keep the domain model honest about what is known versus what is externally confirmed.


## 52. Event-Driven Architecture

Event-driven systems may follow:

```text
Command
   |
   v
Domain decision
   |
   v
State change
   |
   v
Event data
   |
   v
Message broker
   |
   +--> Consumer A
   +--> Consumer B
```

A domain event describes a meaningful domain occurrence. An integration event is usually shaped for cross-system communication.

Publishing the event is an effect. The core can create event data; an outer boundary can publish it.


## 53. Outbox Pattern

The outbox pattern addresses a reliability gap:

```text
DB state commit succeeds
         |
         X
message publication fails
```

Basic idea:

```text
One DB transaction
  |
  +--> update domain state
  +--> write outbox event
  |
  +--> commit

Separate publisher
  |
  +--> read outbox
  +--> publish
  +--> mark delivery state
```

The outbox improves durability of event intent. It does not magically guarantee exactly-once delivery, so idempotent consumers or deduplication are still often needed.


## 54. Real-World Banking Example

Banking transfer example:

```text
Transfer request
      |
      v
Load accounts              [Effect]
      |
      v
Validate transfer          [Pure]
      |
      v
Calculate new state        [Pure]
      |
      v
Persist balances           [Effect]
      |
      v
Publish event               [Effect]
```

Pure rule:

```python
def apply_transfer(source_balance: int, target_balance: int, amount: int):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if source_balance < amount:
        raise ValueError("insufficient funds")
    return source_balance - amount, target_balance + amount
```

Production concerns include transaction ownership, idempotency, duplicate client requests, reconciliation, and reliable event publication. Never use real banking credentials or production APIs in a learning project.


## 55. Real-World Data Engineering Example

A data-engineering pipeline can separate effectful ingestion/output from deterministic transformations:

```text
S3 / API / Database
       |
       v
Read data                [Effect]
       |
       v
Parse                    [Pure]
       |
       v
Validate                 [Pure]
       |
       v
Transform                [Pure]
       |
       v
Aggregate                [Pure]
       |
       v
Write output             [Effect]
```

Pure transforms can be unit-tested against fixtures. Source adapters own connection details, authentication, retries, serialization, and provider-specific errors.


## 56. Real-World ML Example

ML pipeline:

```text
Load model               [Effect]
     |
Preprocess               [Pure]
     |
Inference                [Depends on runtime/resources]
     |
Postprocess              [Pure]
     |
Store/Serve              [Effect]
```

Example:

```python
def normalize_features(values, means, scales):
    return [
        (value - mean) / scale
        for value, mean, scale in zip(values, means, scales)
    ]
```

Inference is not automatically pure or impure in every implementation. It depends on model/runtime behavior, randomness, resource state, batching, external services, and configuration.


## 57. Real-World LLM Example

LLM pipeline:

```text
Request
  |
  v
Validate                 [Pure]
  |
  v
Build prompt             [Pure]
  |
  v
Call LLM                 [Effect]
  |
  v
Parse response           [Pure]
  |
  v
Validate output          [Pure]
  |
  v
Persist/return           [Effect]
```

Example:

```python
def build_prompt(context: str, question: str) -> str:
    return f"Context:\n{context}\n\nQuestion:\n{question}"


def normalize_answer(text: str) -> str:
    return text.strip()
```

The LLM adapter owns provider SDK mechanics, authentication, timeout, retry, provider errors, and model metadata.


## 58. Real-World Agentic AI Example

Agentic-AI workflow:

```text
Agent request
    |
Validate input                    [Pure]
    |
Build state                       [Mostly pure]
    |
Plan / policy decision             [Pure where possible]
    |
Model call                         [Effect]
    |
Tool selection                     [Pure]
    |
Tool execution                     [Effect]
    |
Normalize result                   [Pure]
    |
Write memory                      [Effect]
```

Example:

```python
def choose_tool(state):
    if state["needs_customer"]:
        return "lookup_customer"
    if state["needs_balance"]:
        return "get_balance"
    return "respond"
```

The runtime can then perform the effect:

```python
def execute_tool(tool_registry, name, arguments):
    return tool_registry[name](arguments)
```

This separation is valuable for replay, evaluation, safety-policy testing, and debugging.


## 59. Refactoring Workflow

A practical refactoring workflow:

1. Find effects.
2. Find business rules.
3. Extract pure functions.
4. Make hidden dependencies explicit.
5. Introduce domain models where useful.
6. Define boundaries.
7. Add Protocols only when useful.
8. Inject dependencies.
9. Implement adapters.
10. Move wiring to the composition root.
11. Unit-test core rules.
12. Integration-test adapters.
13. End-to-end test critical workflows.

The order matters: **understand the problem before adding architecture.**


## 60. Before/After Refactoring

### Before

```python
def process_payment(order_id, db):
    order = db.get_order(order_id)
    api_key = os.getenv("PAYMENT_API_KEY")
    response = requests.post(
        "https://example.invalid/charge",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"amount": order.total, "customer_id": order.customer_id},
        timeout=10,
    )
    if response.status_code != 200:
        raise RuntimeError("payment failed")
    fee = round(0.02 * order.total)
    db.mark_paid(order_id, fee)
    return order.total + fee
```

### After

The following is an illustrative architecture sketch; the infrastructure classes are intentionally placeholders.

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PaymentResult:
    provider_reference: str
    amount: int


def calculate_fee(amount: int, rate: float) -> int:
    if amount < 0:
        raise ValueError("amount cannot be negative")
    return round(amount * rate)


class PaymentGateway(Protocol):
    def charge(self, customer_id: str, amount: int, idempotency_key: str) -> PaymentResult:
        ...


class OrderRepository(Protocol):
    def get(self, order_id: str):
        ...

    def mark_paid(self, order_id: str, fee: int, reference: str) -> None:
        ...


def process_payment(order_id, repository, gateway, fee_rate, idempotency_key):
    order = repository.get(order_id)
    fee = calculate_fee(order.total, fee_rate)
    result = gateway.charge(
        order.customer_id,
        order.total + fee,
        idempotency_key,
    )
    repository.mark_paid(order_id, fee, result.provider_reference)
    return result
```

What changed:

- configuration is loaded outside domain calculations;
- provider authentication is adapter responsibility;
- fee logic is explicit;
- repository and gateway are boundaries;
- idempotency is a deliberate part of the payment call;
- the application use case coordinates the steps.


## 61. When Not to Separate Aggressively

Do not separate aggressively when the boundary does not provide meaningful value.

Potential warning signs:

- one-line delegation layers;
- a Protocol for a helper used only once;
- a repository that simply mirrors a single ORM call;
- dozens of files for a simple internal tool;
- duplicate DTO/domain/ORM models that carry no additional meaning.

Simple code can remain simple:

```python
def format_username(first_name, last_name):
    return f"{first_name.strip()} {last_name.strip()}".title()
```

Use complexity, change frequency, testing needs, external risk, team structure, and domain complexity to decide whether another boundary is justified.


## 62. Common Mistakes

Common failure modes include:

- SQL mixed with business rules;
- domain functions calling HTTP clients;
- `os.getenv()` buried inside policy code;
- `datetime.now()` scattered through domain logic;
- global configuration;
- global singletons;
- overusing dependency injection;
- Protocols for everything;
- giant repositories;
- business rules in controllers;
- giant service classes;
- making every function async;
- swallowing infrastructure exceptions;
- retrying non-idempotent effects blindly;
- mixing transaction control with pure calculations;
- excessive logging;
- over-mocking;
- ORM/database objects leaking into core logic;
- adding architecture layers without a concrete reason.

For each mistake, ask: **what responsibility leaked across the boundary, and what is the smallest refactoring that restores clarity?**


## 63. API / Function Coverage

The chapter should not treat every available Python feature as architectural ceremony. The most relevant APIs and constructs are covered here and connected to actual boundary problems:

| Construct | Purpose in this topic | Boundary lesson |
|---|---|---|
| `datetime.now()` | current wall-clock time | make time explicit when deterministic tests matter |
| `time` concepts | elapsed timing/timeouts | choose the right clock semantics |
| `os.getenv()` | configuration | load at an outer boundary |
| `open()` | filesystem I/O | isolate file access |
| `print()` | stdout effect | keep observability intentional |
| `random` | randomness | control or inject when reproducibility matters |
| `getattr()` | dynamic attribute access | useful at adapters; avoid unnecessary magic |
| `setattr()` | dynamic mutation | recognize it as state change |
| `raise` | signal errors | use typed semantic errors |
| `try/except` | boundary error handling | catch specific expected failures |
| `else/finally` | exception structure/resource cleanup | make cleanup and success paths explicit |
| `raise ... from ...` | exception translation | preserve failure cause |
| `map()` / `filter()` | transformations | can be used, but clarity matters |
| comprehensions | data transformation | often readable for local transforms |
| `sorted()` | ordering | key functions isolate comparison logic |
| `any()` / `all()` | predicate aggregation | short-circuiting queries |
| `Protocol` | structural boundary | use when contract/substitution matters |
| `runtime_checkable` | runtime protocol checks | not a behavioral correctness guarantee |
| `Callable` | simple behavior dependency | use a callable contract when sufficient |
| `ClassVar` | class-level state annotation | useful for clear ownership, not DI magic |
| `Optional` / `| None` | explicit absence | make boundary state visible |
| `dataclass` | domain/DTO data model | explicit data representation |
| `field()` | dataclass field configuration | safe per-instance defaults |
| `frozen=True` | assignment restriction | useful for value-oriented models; not deep immutability |

Where exact provider behavior matters, treat the provider adapter as the source of truth and test it.


## 64. Error Translation

Infrastructure errors should usually stop at a meaningful abstraction boundary.

```python
class RetrievalUnavailable(RuntimeError):
    pass


def retrieve(adapter, query):
    try:
        return adapter.search(query)
    except ProviderTimeout as exc:
        raise RetrievalUnavailable("retrieval temporarily unavailable") from exc
```

This allows upper layers to reason about a semantic failure rather than a provider-specific type. The original provider exception remains available through exception chaining.

Do not translate every exception indiscriminately. A retry policy may need to distinguish timeout, authentication failure, invalid request, rate limit, and permanent provider errors.


## 65. Transaction and Failure Model

Consider:

```text
Load -> Validate -> Calculate -> Persist -> Publish
```

Possible failure questions:

- Load fails: no state transition yet.
- Validate fails: no persistence should occur.
- Calculate fails: transaction may roll back.
- Persist fails: state should not be treated as committed.
- Publish fails: database state may already be committed.

The last failure reveals why local and distributed atomicity are different. A database transaction can protect database writes, but an external broker, email service, or HTTP provider may have accepted a request independently.

Production design therefore needs explicit failure, retry, idempotency, and reconciliation strategies.


## 66. Testing Strategy

Testing should match the boundary:

### Unit
Pure calculations, validation, transformations, state transitions.

### Integration
Database adapters, HTTP clients, queues, filesystem, serialization.

### Contract
Important assumptions between a port and its adapters/provider expectations.

### End-to-end
Critical workflows through real application wiring.

A healthy design does not try to prove every behavior with mocks. It uses the least expensive test that answers the question reliably.


## 67. Debugging Strategy

Debugging workflow:

1. Determine whether the failure is domain or infrastructure.
2. Capture the relevant input state.
3. Reproduce pure logic independently where possible.
4. Inspect dependency responses.
5. Inspect transaction state.
6. Inspect retry behavior.
7. Inspect logs/traces/correlation IDs.
8. Check for duplicate processing or idempotency failures.

Separation is valuable because it gives you smaller, more deterministic units to inspect.


## 67A. Mini-Project Architecture Brief — Layered Transaction Processing Service

Before implementation, define the architecture in words.

### Goal

Build a small service that processes a financial-style transaction without connecting to a real bank.

### Required boundaries

```text
HTTP / CLI / Message Consumer
            ↓
      Application Service
            ↓
        Domain Rules
            ↑
    Repository / Clock Ports
            ↑
     Infrastructure Adapters
```

### Responsibilities

| Component | Responsibility |
|---|---|
| Presentation adapter | parse/format external representations |
| Application service | orchestrate the use case |
| Domain | invariants and business decisions |
| Repository port | application-facing persistence contract |
| Repository adapter | actual persistence implementation |
| Clock port | time dependency where required |
| Configuration | runtime settings at startup |
| Composition root | construct concrete dependencies |

### Acceptance criteria

- A domain transfer rule can be unit-tested without a database.
- The application service can run with an in-memory repository.
- Concrete database creation does not occur in domain code.
- Infrastructure exceptions do not become the domain API.
- Retry/idempotency concerns are documented for any externally effectful operation.
- Package imports do not create an architectural cycle.

This is deliberately a design exercise before code. Good architecture starts by clarifying responsibility.

## 68. Mini-Project

### Mini-project: Production-Style Order Processing / AI Document Processing Service

Build a small production-oriented service with this flow:

```text
Input Adapter
      |
      v
Application Service
      |
      v
Pure Domain Logic
      |
      v
Ports / Protocols
      ^
      |
Infrastructure Adapters
```

Required capabilities:

- domain logic;
- application orchestration;
- Protocol-based ports where useful;
- repository adapter;
- external API or LLM adapter;
- configuration boundary;
- time boundary;
- error translation;
- transaction analysis;
- idempotency analysis;
- logging/observability;
- pytest unit tests;
- integration tests around adapters;
- fake dependencies;
- no secrets/real credentials.

#### Domain model

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    document_id: str
    text: str


@dataclass(frozen=True)
class ProcessedDocument:
    document_id: str
    category: str
    summary: str
```

#### Pure functions

```python
def validate_document(document: Document) -> Document:
    if not document.document_id:
        raise ValueError("document_id is required")
    if not document.text.strip():
        raise ValueError("document text is empty")
    return document


def build_prompt(document: Document) -> str:
    return (
        "Classify and summarize this document.\n"
        f"Document ID: {document.document_id}\n"
        f"Text:\n{document.text.strip()}"
    )


def normalize_model_output(document_id: str, output: dict) -> ProcessedDocument:
    category = str(output["category"]).strip().lower()
    summary = str(output["summary"]).strip()
    if not category or not summary:
        raise ValueError("invalid model output")
    return ProcessedDocument(document_id, category, summary)
```

#### Ports

```python
from typing import Protocol


class DocumentRepository(Protocol):
    def save(self, document: ProcessedDocument) -> None:
        ...


class LLMClient(Protocol):
    def generate_structured(self, prompt: str) -> dict:
        ...
```

#### Application orchestration

```python
class DocumentService:
    def __init__(self, repository: DocumentRepository, llm: LLMClient):
        self.repository = repository
        self.llm = llm

    def process(self, document: Document) -> ProcessedDocument:
        validated = validate_document(document)
        prompt = build_prompt(validated)
        raw = self.llm.generate_structured(prompt)
        result = normalize_model_output(validated.document_id, raw)
        self.repository.save(result)
        return result
```

#### Test fakes

```python
class FakeLLM:
    def generate_structured(self, prompt: str) -> dict:
        return {"category": "invoice", "summary": "Test summary"}


class FakeRepository:
    def __init__(self):
        self.saved = []

    def save(self, document):
        self.saved.append(document)
```

#### Unit test

```python
def test_prompt_is_deterministic():
    document = Document("doc-1", "  Hello  ")
    assert build_prompt(document) == (
        "Classify and summarize this document.\n"
        "Document ID: doc-1\n"
        "Text:\nHello"
    )
```

#### Production tasks

- Define request/response DTOs if the transport format is complex.
- Decide which state is owned by the repository versus the process.
- Put model provider mechanics in the adapter.
- Translate provider errors.
- Add timeouts and targeted retries.
- Define idempotency behavior for repeated document IDs.
- Add database integration tests separately.
- Add critical workflow end-to-end coverage.
- Record safe observability metadata.
- Never store secrets in the source file.

A useful project acceptance question is:

> Can the business validation, prompt construction, and output normalization be tested without contacting the database or the model provider?


## 69. Applied AI Engineering Connection

The design connects directly to Applied AI Engineering:

```text
INPUT
  |
  v
+---------------------------+
|       PURE / EXPLICIT     |
| validation                |
| normalization             |
| routing                   |
| prompt construction       |
| policy checks             |
| evaluation transforms     |
+-------------+-------------+
              |
              v
      EXPLICIT EFFECTS
      /       |        \
    DB       LLM       API
              |
            Queue
              |
         Vector Store
```

Useful applications:

- backend business rules;
- ETL/ELT transformations;
- feature preprocessing;
- inference request construction;
- model output validation;
- RAG retrieval/result formatting;
- prompt construction;
- evaluation pipelines;
- agent routing and policy;
- tool execution;
- memory persistence;
- observability.

The same boundary pattern supports reliable systems because AI applications combine deterministic application logic with probabilistic or external infrastructure.


## 70. API Reference: Boundary-Oriented Python

This section is an API-oriented reference for boundary design.

### `datetime.now()`
**Purpose:** read current wall-clock time.

```python
from datetime import datetime
now = datetime.now()
```

**Return:** a `datetime`.  
**Limitation:** depends on system time.  
**Common mistake:** calling it deep inside rules that need deterministic tests.  
**Practical use:** outer boundary obtains `now` and passes it inward.

### `os.getenv(name, default=None)`
**Purpose:** read an environment variable.  
**Return:** a string or the default.  
**Limitation:** environment is process/execution state.  
**Common mistake:** converting it deep inside domain code.  
**Practical use:** load configuration at startup.

### `open(file, mode="r", ...)`
**Purpose:** access a filesystem resource.  
**Return:** a file object.  
**Limitation:** may raise I/O errors; resource must be closed.  
**Common mistake:** mixing reading with domain parsing.

### `print(*objects, sep=" ", end="\n", ...)`
**Purpose:** write to stdout.  
**Return:** `None`.  
**Limitation:** observable effect.  
**Practical use:** command-line boundaries and local diagnostics.

### `random` functions
**Purpose:** generate pseudo-random choices/numbers.  
**Limitation:** output depends on random state/source.  
**Practical use:** inject a generated value/source when reproducibility matters.

### `getattr(obj, name, default=None)`
**Purpose:** dynamic attribute lookup.  
**Return:** attribute value or default.  
**Common mistake:** replacing clear direct attribute access with unnecessary dynamic behavior.

### `setattr(obj, name, value)`
**Purpose:** dynamic attribute assignment.  
**Return:** `None`.  
**Side effect:** usually mutates object state.  
**Common mistake:** treating dynamic mutation as if it were a pure transformation.

### `raise`, `try`, `except`, `else`, `finally`
**Purpose:** controlled failure and cleanup.  
**Common mistake:** catching `Exception` too broadly and losing error semantics.

### `raise ... from ...`
**Purpose:** translate an error while preserving the original cause.  
**Practical use:** provider → application error translation.

### `map(function, iterable, ...)`
**Purpose:** lazy transformation over one or more iterables.  
**Return:** iterator.  
**Limitation:** consumed once; readability depends on the task.

### `filter(function, iterable)`
**Purpose:** lazy filtering.  
**Return:** iterator of items for which the predicate is truthy.  
**Common mistake:** assuming the result is a list.

### Comprehensions
**Purpose:** readable local collection transformations.  
**Common mistake:** using several nested expressions that are harder to read than explicit loops.

### `sorted(iterable, *, key=None, reverse=False)`
**Purpose:** return a new sorted list.  
**Side effect:** does not mutate the input list itself.  
**Common mistake:** using a side-effecting key function.

### `any(iterable)` / `all(iterable)`
**Purpose:** aggregate truthiness with short-circuiting.  
**Empty behavior:** `any([]) is False`; `all([]) is True`.  
**Common mistake:** assuming both evaluate every item.

### `Protocol`
**Purpose:** structural interface for static type checking.  
**Common mistake:** assuming runtime enforcement exists automatically.

### `runtime_checkable`
**Purpose:** allow selected `isinstance()`/`issubclass()` checks against Protocols.  
**Limitation:** runtime checks do not validate full signatures or behavior. Use static type checking and tests for stronger guarantees.

### `Callable`
**Purpose:** annotate a callable dependency.

```python
from collections.abc import Callable


def transform(value: int, operation: Callable[[int], int]) -> int:
    return operation(value)
```

### `ClassVar`
**Purpose:** communicate that a value belongs to class-level state rather than per-instance state.  
**Use here:** reason about ownership of shared configuration/cache state.

### `Optional` / `| None`
Use explicit absence at boundaries:

```python
def find_order(order_id: str) -> Order | None:
    ...
```

### `dataclass`
**Purpose:** concise data models.  
**Use here:** DTOs, domain/value-oriented records.

### `field()`
**Purpose:** configure dataclass fields, especially safe per-instance defaults.

```python
from dataclasses import dataclass, field


@dataclass
class Request:
    tags: list[str] = field(default_factory=list)
```

### `frozen=True`
**Purpose:** prevent normal attribute assignment after initialization.  
**Limitation:** it does not deep-freeze nested mutable objects and does not make all state globally immutable.


### Python imports and package boundaries

Imports are dependency edges in the Python dependency graph.

```python
# absolute import
from app.domain.models import Account

# relative import from inside a package
from ..domain.models import Account
```

An import is not inherently bad. The architectural question is whether the imported module exposes an implementation detail that should remain behind a boundary.

#### Modules and packages

A **module** is a Python source module, commonly a `.py` file. A **package** groups modules under a package namespace.

```text
app/
    domain/
        __init__.py
        models.py
        rules.py
```

`__init__.py` initializes a regular package and can expose a deliberate package-level API. Keep package initialization lightweight; importing a package should not unexpectedly open a database or make a network call.

#### `__all__`

`__all__` can document an intended public export surface:

```python
from .models import Account
from .rules import calculate_interest

__all__ = ["Account", "calculate_interest"]
```

It does not make names private or secure. It mainly communicates and influences wildcard-import behavior.

#### Relative vs absolute imports

Absolute imports are often easier to understand from the project root. Relative imports can communicate local package relationships. Either can be appropriate when used consistently.

The architecture question is not “Which syntax is always better?” but:

> **Does this import represent an intentional dependency edge?**

### `ABC` and `abstractmethod`

`ABC` and `abstractmethod` support nominal abstract base classes:

```python
from abc import ABC, abstractmethod


class MessageSender(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        raise NotImplementedError
```

A subclass must implement the abstract operation before it can be instantiated. This is different from a structural `Protocol`: inheritance is part of the contract model.

Use an ABC when the explicit nominal hierarchy or shared behavior is useful. Do not convert every Protocol into an ABC merely to make the architecture look more formal.

## 71. Exercise Framework

### Exercise requirements

Every exercise includes Problem, Requirements, Expected behavior, Solution, Explanation, and Key learning.

The sequence is designed to move from simple identification to production architecture.


## 72. Debugging Lab Framework

### Debugging-lab requirements

Every debugging scenario includes:

- broken code;
- expected behavior;
- actual behavior;
- debugging clues;
- investigation;
- root cause;
- corrected code;
- explanation;
- production lesson.


## 73. Interview Framework

### Interview depth

Interview questions should be answered using engineering reasoning, not memorized architecture slogans. Be prepared to explain what changes when the external system is slow, unavailable, duplicated, or replaced.


## 74. Architecture Reasoning

### Architecture reasoning

When evaluating architecture, ask:

- What is the business rule?
- What is the external effect?
- Who owns state?
- Who owns the transaction?
- What can fail independently?
- What can be retried?
- What must be idempotent?
- Which boundary reduces meaningful coupling?
- What test can prove each assumption?


## 75. Common Architecture Traps

### Common misconceptions

The most dangerous mistakes in this topic are absolute rules. “Always pure,” “always a repository,” “always async,” “always five layers,” and “always retry” all ignore context. Good architecture is proportional to complexity and risk.


## 76. When Not to Layer or Separate

### When not to separate

Avoid needless architecture for tiny scripts, prototypes, simple CRUD, one-off utilities, and code with no meaningful variation point. Separation becomes more valuable as domain complexity, external dependencies, failure modes, team size, and production risk increase.


## 77. Performance and Architectural Complexity

### Performance and complexity

Evaluate:

- algorithmic complexity;
- serialization;
- copying;
- object creation;
- function-call overhead;
- adapter indirection;
- database/network latency;
- cache memory;
- transaction cost.

Measure before optimizing. Architectural separation can cost runtime and cognitive overhead while still being worth it for correctness and maintainability.


## 78. Concurrency and Async

### Concurrency and async

Explicit boundaries help, but they do not eliminate race conditions. Identify shared mutable resources, transaction isolation, async-task interaction, cancellation, and ownership of external clients.


## 79. Distributed Systems Reliability

### Distributed reliability

Important concepts include timeouts, retries, idempotency, duplicate delivery, eventual consistency, outbox, and observability. Do not assume local success implies remote success.


## 80. Advanced Architecture Diagram

### Advanced architecture diagram

```text
                     USER / CLIENT
                          |
                          v
                   +----------------+
                   |   Controller   |
                   +-------+--------+
                           |
                           v
                   +----------------+
                   |  Application   |
                   |   Service /    |
                   |    Use Case    |
                   +-------+--------+
                           |
                 +---------+----------+
                 |                    |
                 v                    v
          Pure Domain Logic     Ports / Protocols
                                      ^
                                      |
                         +------------+------------+
                         |            |            |
                         v            v            v
                     Database       API          Queue
                     Adapter       Adapter       Adapter
                         |            |            |
                         +------------+------------+
                                      |
                                      v
                                External World
```

This diagram combines the major ideas:

- controller handles transport;
- application service orchestrates;
- pure domain logic expresses rules;
- ports define needed interactions;
- adapters connect those ports to actual systems.


## 81. Real-World AI System Architecture

### Real-world AI system architecture

```text
                 Upload API
                     |
                     v
             Application Service
                     |
          +----------+----------+
          |                     |
          v                     v
    Pure Parsing         Pure Validation
          |                     |
          +----------+----------+
                     |
                     v
                Prompt Builder
                     |
                     v
               LLM Port
                     ^
                     |
                 LLM Adapter
                     |
                     v
               External Model
                     |
                     v
             Output Normalizer
                     |
                     v
               Repository Port
                     ^
                     |
             Database Adapter
```

Side effects occur at upload, model, storage, database, and queue boundaries. Pure logic handles parsing, validation, prompt construction, output normalization, and deterministic policy. Retries belong near effect boundaries. Observability should capture useful request/dependency information without coupling every pure function to a logging SDK.


## 82. Applied AI Engineering Connection

### Applied AI Engineering connection

The most useful production habit is to look at an AI workflow and ask which parts can be replayed without infrastructure.

Examples:

- **RAG:** query normalization, context formatting, ranking policy, prompt construction can often be pure; vector search and model calls are effects.
- **Inference:** validation and preprocessing can be pure; model runtime may depend on loaded artifacts, GPU state, randomness, and scheduling.
- **Evaluation:** scoring functions can often be pure; dataset ingestion, model invocation, and result persistence are effects.
- **Agentic AI:** state-transition and policy decisions can be pure; tool execution, model calls, memory writes, and network access are effects.
- **Data engineering:** parse/validate/transform/aggregate can often be pure; S3/API/database ingestion and output are effects.


## 83. Code Quality Requirements

### Code quality rules

All examples must:

- use valid Python syntax;
- use meaningful names;
- avoid real credentials and real API keys;
- use safe placeholder endpoints when network calls are illustrative;
- prefer standard-library examples;
- label illustrative infrastructure snippets when they are not independently runnable;
- show expected output only when it has been checked;
- avoid claiming performance benefits without measurement;
- avoid needless frameworks.


## 84. Progressive Complexity

### Progressive complexity

The chapter should be mentally traversed as:

```text
mixed function
 -> effects
 -> domain logic
 -> pure logic
 -> explicit state/dependencies
 -> functional core
 -> imperative shell
 -> boundaries
 -> injection
 -> Protocols
 -> ports/adapters
 -> application services
 -> persistence/time/configuration boundaries
 -> transactions/errors/retries/idempotency
 -> testing/observability
 -> concurrency/distribution/events/outbox
 -> backend/data/ML/LLM/agentic AI
 -> production architecture
```

Do not skip the underlying problem when teaching the architecture vocabulary.


## 85. Final Self-Review

### Final self-review

The chapter is complete when:

- beginner explanations exist;
- mixed code appears before architecture;
- domain/application/infrastructure responsibilities are distinguished;
- side effects are defined accurately;
- pure logic is extracted;
- functional core / imperative shell is explained;
- dependency injection and Protocols are connected without duplicating the earlier Protocol chapter;
- ports/adapters, hexagonal, clean, and layered concepts are explained;
- boundaries for DB/HTTP/files/time/randomness/configuration are covered;
- transactions, Unit of Work, errors, retries, idempotency, commands/queries are covered;
- repositories, DTOs, serialization, orchestration, application services are covered;
- testing, debugging, observability, async/concurrency/distributed systems are covered;
- event-driven architecture and outbox are covered;
- banking, data engineering, ML, LLM, and agentic-AI examples exist;
- there are 25+ exercises, 7+ debugging scenarios, a mini-project, interview questions, architecture questions, and a 20+ question knowledge check;
- misconceptions and “when not to separate” are covered;
- code contains no secrets;
- only the target file is modified.


## 86. File-Scope Verification

### File-scope verification

This task is limited to:

`08-Object-Oriented-Design-Data-Modelling-and-Functional-Style/08-dependency-boundaries-and-layered-design.md`

No README, practice question file, previous topic, future topic, project file, or auxiliary file should be changed.


## 87. Final Mental Model: Dependency Boundaries and Layered Design

### Final mental model

> **Business meaning should be explicit. External effects should be explicit. Dependencies should be intentional. The boundary and direction between them should be understandable.**

The complete progression is:

```text
MIXED CODE
   |
IDENTIFY SIDE EFFECTS
   |
IDENTIFY DOMAIN LOGIC
   |
EXTRACT PURE LOGIC
   |
DEFINE BOUNDARIES
   |
DEPENDENCY INJECTION
   |
PORTS / PROTOCOLS
   |
ADAPTERS
   |
FUNCTIONAL CORE / IMPERATIVE SHELL
   |
APPLICATION SERVICES
   |
TRANSACTIONS / ERROR TRANSLATION
   |
RETRIES / IDEMPOTENCY
   |
TESTING / OBSERVABILITY
   |
DISTRIBUTED + EVENT-DRIVEN SYSTEMS
   |
BACKEND / DATA / ML / LLM / AGENTIC AI
   |
PRODUCTION ARCHITECTURE
```

The purpose of this design is not to eliminate effects. It is to keep effects **visible, owned, testable, and operationally safe**, while keeping valuable business rules understandable without infrastructure.


### Basic Exercises

## Exercise 1 — Identify mixed responsibilities

**Problem**

Classify each line in a checkout function as domain, application, boundary, or effect.

**Requirements**

Mark repository, clock, calculation, persistence, and notification separately.

**Expected behavior**

A calculation is domain; repository/clock/notification are external concerns; orchestration connects them.

**Solution**

Classification makes refactoring targeted instead of mechanical.

**Explanation**

Classification makes refactoring targeted instead of mechanical.

**Key learning**

Learn to see responsibility before designing abstractions.


## Exercise 2 — Extract an eligibility rule

**Problem**

A customer eligibility function loads a remote profile and compares a score.

**Requirements**

Move the HTTP dependency outside the rule.

**Expected behavior**

Create `is_eligible(score, threshold)` and let the adapter provide the score.

**Solution**

The provider is an effect; the threshold comparison is domain policy.

**Explanation**

The provider is an effect; the threshold comparison is domain policy.

**Key learning**

Explicit inputs reveal the real business rule.


## Exercise 3 — Make configuration explicit

**Problem**

A limit rule reads `os.getenv()` inside the function.

**Requirements**

Move environment access to the application boundary.

**Expected behavior**

The rule accepts `limit` directly.

**Solution**

The same arguments now produce the same result regardless of process environment.

**Explanation**

The same arguments now produce the same result regardless of process environment.

**Key learning**

Configuration is a dependency.


## Exercise 4 — Inject a clock

**Problem**

An expiry check calls `datetime.now()`.

**Requirements**

Accept `now` as an argument.

**Expected behavior**

The test supplies a fixed `now`.

**Solution**

Time becomes explicit external state.

**Explanation**

Time becomes explicit external state.

**Key learning**

Deterministic tests require controllable time.


## Exercise 5 — Separate filesystem parsing

**Problem**

A function reads a file and parses records.

**Requirements**

Create a parser that accepts text.

**Expected behavior**

The file function reads; the parser transforms.

**Solution**

The parser can run without a filesystem.

**Explanation**

The parser can run without a filesystem.

**Key learning**

Acquisition and transformation are separate responsibilities.


## Exercise 6 — Design a repository port

**Problem**

An order service constructs its own database repository.

**Requirements**

Inject a repository and define a useful Protocol if warranted.

**Expected behavior**

Tests can provide an in-memory fake.

**Solution**

Construction moves to the composition root.

**Explanation**

Construction moves to the composition root.

**Key learning**

Dependency injection exposes ownership.


## Exercise 7 — Build an HTTP gateway

**Problem**

A domain calculation calls `requests.get()`.

**Requirements**

Create an adapter that returns only the required data.

**Expected behavior**

The domain rule receives plain values.

**Solution**

Provider details stay outside the core.

**Explanation**

Provider details stay outside the core.

**Key learning**

The domain should depend on meaning, not transport.


## Exercise 8 — Distinguish DTO and domain data

**Problem**

An endpoint passes raw JSON deep into business rules.

**Requirements**

Create a boundary conversion.

**Expected behavior**

Business code receives domain-oriented values.

**Solution**

Transport concerns are isolated.

**Explanation**

Transport concerns are isolated.

**Key learning**

Boundary models protect domain language.


### Intermediate Exercises

## Exercise 9 — Define a state transition

**Problem**

A banking transfer mutates two account objects in place.

**Requirements**

Return explicit new balances from a pure function.

**Expected behavior**

The function either returns valid new state or raises a domain error.

**Solution**

The state transition can be tested without a DB.

**Explanation**

The state transition can be tested without a DB.

**Key learning**

State can be explicit without being globally mutable.


## Exercise 10 — Handle domain errors

**Problem**

Invalid order quantity is represented by a low-level provider exception.

**Requirements**

Raise a semantic domain error.

**Expected behavior**

Application code can distinguish invalid business input from infrastructure failure.

**Solution**

Error types communicate boundaries.

**Explanation**

Error types communicate boundaries.

**Key learning**

Error translation preserves architecture.


## Exercise 11 — Translate infrastructure errors

**Problem**

A PostgreSQL exception leaks to an API controller.

**Requirements**

Translate it at the adapter/application boundary and preserve the cause.

**Expected behavior**

Higher layers handle `OrderPersistenceError`.

**Solution**

Provider details stay localized.

**Explanation**

Provider details stay localized.

**Key learning**

Use `raise ... from ...` deliberately.


## Exercise 12 — Design transaction ownership

**Problem**

A domain function directly calls `commit()`.

**Requirements**

Move transaction ownership outward.

**Expected behavior**

Application orchestration decides transaction scope.

**Solution**

The domain rule remains independent of storage mechanics.

**Explanation**

The domain rule remains independent of storage mechanics.

**Key learning**

Transaction ownership is an architectural concern.


## Exercise 13 — Evaluate Unit of Work

**Problem**

A workflow changes two repositories that must commit together.

**Requirements**

Describe a Unit of Work boundary.

**Expected behavior**

Both changes commit or roll back together in the local DB.

**Solution**

The Unit of Work coordinates local persistence, not external atomicity.

**Explanation**

The Unit of Work coordinates local persistence, not external atomicity.

**Key learning**

Use the pattern when there is a meaningful transaction.


## Exercise 14 — Make retries safe

**Problem**

A payment times out and the client automatically retries.

**Requirements**

Introduce idempotency semantics.

**Expected behavior**

Repeated requests map to one logical charge.

**Solution**

Retrying an effect requires knowledge of the provider outcome.

**Explanation**

Retrying an effect requires knowledge of the provider outcome.

**Key learning**

Retries are reliability behavior, not just a loop.


## Exercise 15 — Design an outbox

**Problem**

Database commit succeeds but event publish fails.

**Requirements**

Persist event intent in the same transaction.

**Expected behavior**

A publisher retries later from the outbox.

**Solution**

Event intent survives the process that performed the transaction.

**Explanation**

Event intent survives the process that performed the transaction.

**Key learning**

Local atomicity and remote delivery are distinct.


## Exercise 16 — Separate query and command

**Problem**

A handler reads a balance then changes it in the same function.

**Requirements**

Split read intent from state-changing command handling.

**Expected behavior**

Each path has clear ownership.

**Solution**

Clear intent helps caching/retry analysis.

**Explanation**

Clear intent helps caching/retry analysis.

**Key learning**

Query/command is not identical to pure/impure.


## Exercise 17 — Build a pure data transform

**Problem**

A data pipeline transformation reads environment configuration.

**Requirements**

Pass configuration as an argument.

**Expected behavior**

Same data + same config gives repeatable output.

**Solution**

Reproducibility improves.

**Explanation**

Reproducibility improves.

**Key learning**

ETL transformations benefit from explicit inputs.


## Exercise 18 — Build a prompt builder

**Problem**

Prompt formatting is mixed with an LLM SDK call.

**Requirements**

Separate string construction from network access.

**Expected behavior**

Prompt tests do not require the model provider.

**Solution**

The model adapter owns external behavior.

**Explanation**

The model adapter owns external behavior.

**Key learning**

LLM orchestration benefits from effect isolation.


### Advanced Exercises

## Exercise 19 — Split agent routing

**Problem**

One agent function plans, calls tools, writes memory, and logs.

**Requirements**

Extract deterministic routing/policy decisions.

**Expected behavior**

A pure decision function returns an action; executor performs it.

**Solution**

Policy tests can run without tools or a model.

**Explanation**

Policy tests can run without tools or a model.

**Key learning**

Separate decision from execution.


## Exercise 20 — Evaluate a Protocol

**Problem**

A team created interfaces for every helper.

**Requirements**

Identify which boundaries actually vary.

**Expected behavior**

Keep local helpers concrete; abstract meaningful replacement points.

**Solution**

Fewer unnecessary abstractions improve navigation.

**Explanation**

Fewer unnecessary abstractions improve navigation.

**Key learning**

Protocols should earn their complexity.


## Exercise 21 — Review ORM leakage

**Problem**

Domain rules accept ORM objects with lazy-loading behavior.

**Requirements**

Decide whether to map to domain data.

**Expected behavior**

Business logic runs on stable domain values when mapping is useful.

**Solution**

Provider/session semantics stop leaking inward.

**Explanation**

Provider/session semantics stop leaking inward.

**Key learning**

Persistence models and domain models can serve different purposes.


## Exercise 22 — Design observability

**Problem**

A pure pricing function imports the logging framework.

**Requirements**

Move incidental logging to the application boundary.

**Expected behavior**

Business calculation remains ordinary Python.

**Solution**

Observability still exists at the use-case boundary.

**Explanation**

Observability still exists at the use-case boundary.

**Key learning**

Effects can be observed without contaminating every rule.


## Exercise 23 — Async boundary

**Problem**

Every domain helper is declared `async` because the API is async.

**Requirements**

Keep pure calculations synchronous.

**Expected behavior**

Only the I/O boundary awaits the client.

**Solution**

The domain is simpler.

**Explanation**

The domain is simpler.

**Key learning**

Async should follow actual asynchronous work.


## Exercise 24 — Duplicate message

**Problem**

A queue redelivers a payment request.

**Requirements**

Design deduplication/idempotency.

**Expected behavior**

The second delivery does not repeat the charge.

**Solution**

Processing state or provider idempotency is durable.

**Explanation**

Processing state or provider idempotency is durable.

**Key learning**

Messaging semantics affect domain/effect design.


### Production / Architecture Exercises

## Exercise 25 — Provider replacement

**Problem**

A service is tightly coupled to one LLM SDK.

**Requirements**

Introduce an application-facing client contract and adapter.

**Expected behavior**

A second implementation can satisfy the same need.

**Solution**

Provider-specific mechanics remain localized.

**Explanation**

Provider-specific mechanics remain localized.

**Key learning**

Ports create a useful seam when provider change is real.


## Exercise 26 — Test the pure core

**Problem**

A business rule requires a database fixture before it can be exercised.

**Requirements**

Extract the rule and write direct tests.

**Expected behavior**

Tests run with normal Python values.

**Solution**

The dependency footprint becomes smaller.

**Explanation**

The dependency footprint becomes smaller.

**Key learning**

Pure core means fewer test setup costs.


## Exercise 27 — Refactor controller logic

**Problem**

The HTTP controller contains all business rules.

**Requirements**

Move rules into application/domain functions.

**Expected behavior**

Controller handles transport; core handles business behavior.

**Solution**

Transport changes have less impact on business logic.

**Explanation**

Transport changes have less impact on business logic.

**Key learning**

Controllers are boundaries, not business-rule dumping grounds.


## Exercise 28 — Assess simple CRUD

**Problem**

A tiny internal CRUD service has repository, use-case, port, adapter, and DTO layers for every field.

**Requirements**

Evaluate whether each layer provides value.

**Expected behavior**

Keep genuinely useful boundaries and simplify ceremonial ones.

**Solution**

Keep only boundaries that reduce meaningful coupling, isolate real external variation, or provide valuable tests/operations.

**Explanation**

The result may be fewer layers.

**Key learning**

Architecture should fit the problem.


## Debugging Scenario 1 — SQL mixed with business rule

### Broken code

```python
def discount(order_id, connection):
    row = connection.execute(
        "SELECT total, tier FROM orders WHERE id = ?",
        (order_id,),
    ).fetchone()
    return row["total"] * (0.20 if row["tier"] == "gold" else 0.05)
```

### Expected behavior

The discount policy should be testable without a database.

### Actual behavior

Tests require SQL fixtures and fail when the DB is unavailable.

### Debugging clues

Business calculation and SQL access are in the same function.

### Investigation

Separate data acquisition from policy evaluation.

### Root cause

Persistence and domain policy are coupled.

### Corrected code

```python
def discount(total, tier):
    return total * (0.20 if tier == "gold" else 0.05)
```

### Explanation

The adapter supplies `total` and `tier`.

### Production lesson

Keep data-intensive SQL concerns separate from reusable policy where practical.


## Debugging Scenario 2 — Hidden environment dependency

### Broken code

```python
import os

def limit(value):
    return min(value, int(os.getenv("LIMIT", "1000")))
```

### Expected behavior

The same explicit input should produce stable behavior in tests.

### Actual behavior

Changing the environment changes the result.

### Debugging clues

Search for `os.getenv()` inside the rule.

### Investigation

Make configuration explicit.

### Root cause

The environment is hidden state.

### Corrected code

```python
def limit(value, maximum):
    return min(value, maximum)
```

### Explanation

The outer layer loads the environment value and passes it in.

### Production lesson

Configuration boundaries improve reproducibility.


## Debugging Scenario 3 — Current-time dependency

### Broken code

```python
from datetime import datetime

def can_cancel(deadline):
    return datetime.now() <= deadline
```

### Expected behavior

Tests should control the time.

### Actual behavior

Tests pass or fail depending on the real clock.

### Debugging clues

The function has no clock argument.

### Investigation

Supply a fixed timestamp.

### Root cause

Wall-clock time is a hidden dependency.

### Corrected code

```python
def can_cancel(deadline, now):
    return now <= deadline
```

### Explanation

The boundary owns the clock; the rule receives the value.

### Production lesson

Time should be explicit when correctness depends on it.


## Debugging Scenario 4 — HTTP call inside domain logic

### Broken code

```python
def eligible(customer_id, http):
    profile = http.get(f"https://example.invalid/{customer_id}").json()
    return profile["score"] >= 700
```

### Expected behavior

Eligibility should be testable offline.

### Actual behavior

Tests depend on remote network behavior.

### Debugging clues

The domain predicate imports/uses an HTTP client.

### Investigation

Extract the score at the boundary.

### Root cause

Transport is coupled to business policy.

### Corrected code

```python
def eligible(score):
    return score >= 700
```

### Explanation

The adapter retrieves the score; the domain evaluates it.

### Production lesson

Provider availability should not be required to test business rules.


## Debugging Scenario 5 — Incorrect DI fallback

### Broken code

```python
class Service:
    def __init__(self, repository=None):
        self.repository = repository or RealRepository()
```

### Expected behavior

A caller-supplied fake must be respected even if it is falsey.

### Actual behavior

A falsey fake causes construction of the real repository.

### Debugging clues

The `or` expression conflates falsey with absent.

### Investigation

Use `is None`.

### Root cause

The dependency default has incorrect semantics.

### Corrected code

```python
class Service:
    def __init__(self, repository=None):
        if repository is None:
            repository = RealRepository()
        self.repository = repository
```

### Explanation

`None` specifically means no dependency was supplied.

### Production lesson

Dependency injection must preserve explicit substitutions.


## Debugging Scenario 6 — Infrastructure exception leaks

### Broken code

```python
def save(repository, order):
    repository.save(order)
```

### Expected behavior

Upper layers should not depend on a provider-specific exception when a semantic error is appropriate.

### Actual behavior

Controllers catch `PostgresError`.

### Debugging clues

Provider-specific exception crosses the boundary.

### Investigation

Translate at the adapter/application boundary.

### Root cause

No error boundary exists.

### Corrected code

```python
class OrderPersistenceError(RuntimeError):
    pass


def save(repository, order):
    try:
        repository.save(order)
    except PostgresError as exc:
        raise OrderPersistenceError("save failed") from exc
```

### Explanation

Exception chaining preserves the provider failure as the cause.

### Production lesson

Error translation is part of interface design.


## Debugging Scenario 7 — Retry duplicates a side effect

### Broken code

```python
def charge(gateway, customer_id, amount):
    for _ in range(3):
        try:
            return gateway.charge(customer_id, amount)
        except TimeoutError:
            continue
    raise RuntimeError("failed")
```

### Expected behavior

A timeout must not cause duplicate charges.

### Actual behavior

The provider may have completed the first request while the client timed out.

### Debugging clues

Timeout is an ambiguous outcome.

### Investigation

Add idempotency and provider-aware retry/reconciliation.

### Root cause

Retrying without idempotency is unsafe for non-idempotent effects.

### Corrected code

```python
def charge(gateway, customer_id, amount, idempotency_key):
    return gateway.charge(
        customer_id,
        amount,
        idempotency_key=idempotency_key,
    )
```

### Explanation

A stable logical request key lets the provider/application recognize repeats.

### Production lesson

Retry behavior must be designed with side-effect semantics.


## Debugging Scenario 8 — DB commit then publish

### Broken code

```python
def create_order(uow, broker, order):
    uow.orders.save(order)
    uow.commit()
    broker.publish({"type": "OrderCreated", "id": order.id})
```

### Expected behavior

State change and event intent should not silently diverge.

### Actual behavior

The DB commits but publication fails.

### Debugging clues

There is a failure window between commit and publish.

### Investigation

Use an outbox or another explicit consistency workflow.

### Root cause

Local DB atomicity does not cover the broker.

### Corrected code

Record the event intent in the same transaction; publish asynchronously and make consumers idempotent.

### Explanation

The outbox moves the problem from a fragile two-step sequence to durable delivery.

### Production lesson

Distributed effects need an explicit reliability model.


# 74. Interview Questions

## Beginner

### 1. What is domain logic?
**Strong answer:** Domain logic is the set of business/problem rules and decisions that explain what the system is supposed to do.

### 2. What is a side effect?
**Strong answer:** An observable interaction with state/resources outside a local value transformation, such as DB writes, HTTP calls, shared mutation, logging, or reading current time.

### 3. Why separate effects from domain logic?
**Strong answer:** It makes important rules easier to test, replay, reason about, and change independently from infrastructure.

### 4. What is a pure function?
**Strong answer:** A function whose result is determined by its relevant inputs and whose call does not introduce observable external effects.

## Intermediate

### 5. What is Functional Core / Imperative Shell?
**Strong answer:** Concentrate deterministic business rules and transformations in a core; keep I/O and other external effects in an outer shell.

### 6. What is dependency injection?
**Strong answer:** Supply dependencies from outside rather than constructing them internally. A constructor/function parameter is enough.

### 7. What is a repository?
**Strong answer:** A persistence-facing abstraction tailored to application needs.

### 8. What is an adapter?
**Strong answer:** A concrete implementation that connects an application-facing boundary to an external provider/technology.

### 9. What is a port?
**Strong answer:** A boundary contract describing an interaction required by the application/core.

## Advanced

### 10. How do you isolate time?
**Strong answer:** Pass time as an argument for simple cases, or inject a clock abstraction when repeated clock behavior warrants it.

### 11. Why can retries be dangerous?
**Strong answer:** A timeout can leave an effect outcome unknown. Repeating a non-idempotent effect can duplicate the operation.

### 12. What is idempotency?
**Strong answer:** Repeating the same logical operation does not create unintended additional effects.

### 13. Why use `raise ... from ...`?
**Strong answer:** To translate an exception while preserving the original exception as the cause.

### 14. What does an outbox solve?
**Strong answer:** It improves consistency between a local DB state change and later event publication by durably recording event intent in the same transaction.

## Architecture

### 15. How would you structure a banking transfer?
**Strong answer:** Load state at a boundary, apply a deterministic transfer rule, persist in an explicit transaction, and publish downstream intent through a reliable event mechanism. Add idempotency/reconciliation for repeated requests and uncertain external outcomes.

### 16. How would you isolate an LLM provider?
**Strong answer:** Keep validation/prompt construction/response parsing separate from the provider adapter, with provider SDK, auth, timeout, retry, and error translation inside the adapter.

### 17. How would you separate agent planning from tool execution?
**Strong answer:** Extract deterministic policy/routing into functions over explicit state; let an outer runtime perform tool calls and manage effects.

### 18. How would you build a reproducible ML pipeline?
**Strong answer:** Make preprocessing/configuration explicit, isolate model/runtime dependencies, record relevant configuration/model versions, and test pure transformations independently.

### 19. Do all systems need repositories?
**Strong answer:** No. Repositories are useful when they create meaningful persistence isolation; direct data access can be appropriate in simpler systems.

### 20. Does every dependency need a Protocol?
**Strong answer:** No. A Protocol is valuable when a stable contract, substitution, or static typing helps. Otherwise direct parameters or concrete types are often clearer.
### 21. What is the difference between an architectural layer and an adapter?
**Strong answer:** A layer groups responsibilities at a conceptual level; an adapter is a concrete translation/implementation at a system boundary. One layer can contain several adapters, and an adapter can participate in an architecture without implying a specific folder.

### 22. Why can a feature-based architecture coexist with layered thinking?
**Strong answer:** A feature can own presentation, application, domain, and infrastructure-facing code locally while still preserving clear dependency direction. Feature organization changes locality; layering still describes responsibilities.

### 23. What makes a dependency boundary stable?
**Strong answer:** Its contract should express a capability the consumer actually needs and avoid exposing volatile provider-specific details.

### 24. When would you use an `ABC` instead of a `Protocol`?
**Strong answer:** When nominal inheritance, shared implementation, explicit abstract base behavior, or runtime abstract-class semantics are useful. Use Protocols when structural typing and consumer-owned contracts are a better fit.

### 25. Why is a composition root important?
**Strong answer:** It centralizes concrete dependency choices, making the dependency graph visible and keeping business/application code from constructing infrastructure unexpectedly.

### 26. How would you detect an unwanted dependency between packages?
**Strong answer:** Inspect imports and call paths, build a dependency graph, identify cycles or references to volatile internals, and compare the actual graph with the intended architecture.

### 27. Why can DTO mapping be worth the extra code?
**Strong answer:** It can prevent transport or persistence concerns from becoming domain contracts, making versioning and internal changes easier. It is not always worth the boilerplate.

### 28. What is a god service?
**Strong answer:** A service that coordinates too many unrelated responsibilities, often accumulating validation, domain rules, persistence, API calls, formatting, and observability. The solution is responsibility analysis, not automatically more classes.

### 29. How would you test a real PostgreSQL repository?
**Strong answer:** Use integration tests against a controlled database/schema to validate SQL, mappings, constraints, and transaction behavior. Unit tests with a fake do not prove database correctness.

### 30. How would you isolate a vector database in a RAG system?
**Strong answer:** Define a retrieval capability around the application’s actual needs, implement a vector-store adapter, keep ranking/context policy outside the SDK, and use a deterministic fake or fixture for most unit tests.

### 31. What belongs in the adapter when calling an external API?
**Strong answer:** Provider-specific serialization, authentication mechanics, timeouts, status handling, response mapping, retry classification, and provider error translation.

### 32. How does dependency direction affect maintainability?
**Strong answer:** It controls which changes propagate. A core policy that depends on volatile infrastructure details tends to absorb provider changes; a stable boundary can contain that volatility.

# 75. Architecture Questions

1. A repository contains pricing rules. How would you refactor it?
**Model answer:** Decide whether the rule is domain policy. If yes, expose the required data and evaluate the policy in domain code. Keep SQL-specific optimization where data locality genuinely matters.

2. A domain function reads `os.getenv()`. What is the issue?
**Model answer:** Configuration is hidden. Load it at an outer boundary and pass the relevant value/object inward.

3. An LLM function validates input, builds prompts, retries the model, parses output, and stores a record. Refactor it.
**Model answer:** Separate deterministic validation/prompt/parse functions, LLM adapter, repository adapter, and application orchestration.

4. An agent has one 500-line function for planning, tools, memory, logs, and retries.
**Model answer:** Split state representation, decision policy, model port, tool execution boundary, memory boundary, and observability/orchestration.

5. A payment client times out and the client retries.
**Model answer:** Treat the outcome as ambiguous, use idempotency, and reconcile when necessary.

6. DB commit succeeds but event publish fails.
**Model answer:** Consider an outbox or equivalent reliable event workflow.

7. A team created a Protocol for every helper.
**Model answer:** Measure actual variation/testing value and remove ceremonial abstractions.

8. A tiny CRUD app has twenty layers.
**Model answer:** Simplify unless the layers solve concrete change/test/reliability problems.

9. A data pipeline transformation reads global configuration.
**Model answer:** Make configuration an explicit function input and record it for reproducibility.

10. Tests fail depending on the current minute.
**Model answer:** Inject time or a clock boundary.

11. A global singleton API client is used everywhere.
**Model answer:** Evaluate lifecycle/reuse benefits against hidden coupling, configuration changes, test isolation, and concurrency.

12. Domain functions accept ORM objects with lazy relationships.
**Model answer:** Decide whether ORM behavior is leaking infrastructure into domain rules. Map to domain data when that improves isolation.

13. The product requires audit logging for every transfer.
**Model answer:** Represent the audit fact/event explicitly and emit/persist it at an appropriate boundary. Do not confuse a required business event with incidental debug logging.

14. A team made everything async.
**Model answer:** Keep async at real async I/O boundaries; synchronous deterministic logic can remain synchronous.
# 76. Knowledge Check

1. **MCQ:** Which is the best reason to extract a pure domain rule?
A. It is always faster. B. It eliminates all state. C. It can be tested without infrastructure. D. It never raises errors.
**Answer:** C.

2. **Classify:** `repository.save(order)`
**Answer:** infrastructure effect coordinated by application logic.

3. **Classify:** `calculate_tax(subtotal, rate)`
**Answer:** domain calculation.

4. **MCQ:** What is dependency injection?
A. Global state. B. Framework-only wiring. C. Supplying dependencies externally. D. Making everything static.
**Answer:** C.

5. **Predict:** `print(any([]))`
**Answer:** `False`.

6. **Predict:** `print(all([]))`
**Answer:** `True`.

7. **Identify hidden dependency:** `datetime.now()`
**Answer:** system wall clock.

8. **Identify hidden dependency:** `os.getenv("LIMIT")`
**Answer:** process environment/configuration.

9. **Architecture:** Can a DB transaction automatically roll back an external payment provider call?
**Answer:** No, not in the general case.

10. **Define:** port.
**Answer:** application-facing interaction boundary/contract.

11. **Define:** adapter.
**Answer:** concrete implementation connecting the contract to an external system.

12. **Why use outbox?**
**Answer:** durable event intent within the same DB transaction as state change.

13. **What is idempotency?**
**Answer:** repetition does not cause unintended additional effects.

14. **Debugging:** a test changes behavior when environment variables change. What should you inspect?
**Answer:** hidden configuration dependency.

15. **Debugging:** a retry doubles a payment. What should you inspect?
**Answer:** provider semantics, timeout ambiguity, retry policy, idempotency key.

16. **Domain vs application:** loading an order then calling a calculator is what?
**Answer:** application orchestration around a domain rule.

17. **Why isolate prompt building?**
**Answer:** deterministic prompt logic can be tested without the model provider.

18. **Why isolate agent tool selection?**
**Answer:** routing/policy can be tested without executing side effects.

19. **What is a DTO?**
**Answer:** boundary/transport data representation.

20. **What is a domain invariant?**
**Answer:** a condition required for valid domain state/operation.

21. **MCQ:** Which should usually own provider-specific HTTP timeouts?
A. Domain function. B. Adapter/gateway. C. DTO. D. Value object.
**Answer:** B.

22. **MCQ:** Which design is the smallest abstraction for one timestamp dependency?
A. DI framework. B. Protocol. C. direct timestamp parameter. D. service locator.
**Answer:** C.

23. **Predict failure:** queue redelivers the same payment event.
**Answer:** duplicate effect is possible unless processing is idempotent/deduplicated.

24. **Architecture:** Why can a query still be effectful?
**Answer:** it may read external state such as a database.

25. **Complexity:** Does more architecture automatically mean better software?
**Answer:** No; added complexity must create useful boundaries.
# 77. Common Misconceptions

### “All business logic must be pure.”
Not necessarily. Many workflows coordinate state, transactions, and effects. Extract pure rules where that improves reasoning, but do not force artificial purity.

### “Pure functions cannot use objects.”
False. They can accept objects as long as relevant behavior/state is supplied and no prohibited external effects occur.

### “Side effects are always bad.”
False. Production systems require effects. The problem is hidden or uncontrolled effects.

### “Database code can never be close to business logic.”
Too absolute. Data-intensive calculations may be appropriate in the database. Separate responsibilities when it improves clarity, correctness, or change isolation.

### “Every function should be pure.”
No. Controllers, adapters, orchestrators, and infrastructure are inherently effectful.

### “Every project needs Clean Architecture.”
No. Architecture should match the problem.

### “Every class needs a Protocol.”
No. Protocols should correspond to meaningful contracts/variation points.

### “Repositories are mandatory.”
No.

### “Functional core means no state.”
False. A functional core can transform explicit state.

### “Imperative shell means bad code.”
False. The shell is where the real world is handled.

### “Logging should never happen near domain code.”
Too absolute. Incidental observability can move outward; domain audit requirements may legitimately originate from domain behavior.

### “All validation belongs in the domain.”
No. Structural validation and business validation are different concerns.

### “All validation belongs at the API boundary.”
No. Domain invariants still need domain-aware checks.

### “Dependency injection requires a framework.”
False. Passing a dependency as a function/constructor argument is DI.

### “Retries are always safe.”
False. They can duplicate effects.

### “A DB transaction makes an external API call atomic.”
False in the general case.

### “Async code should be used everywhere.”
No. Use async where it serves real asynchronous work.

### “Pure code automatically makes distributed systems safe.”
No. Distribution introduces independent failures and consistency challenges.

### “More layers always mean better architecture.”
No. Indirection has cost. Each layer should solve a real problem.
# 78. When Not to Separate

Keep code simple for:

- tiny scripts;
- one-off utilities;
- prototypes;
- straightforward internal tools;
- simple CRUD operations;
- code with no meaningful variation point.

Evaluate:

| Factor | Question |
|---|---|
| Complexity | Are multiple responsibilities truly mixed? |
| Change frequency | Do rules and infrastructure change independently? |
| Testing | Is infrastructure blocking important tests? |
| External risk | Are failures, timeouts, or provider changes important? |
| Team | Will the boundary improve collaboration? |
| Production risk | What is the consequence of failure? |
| Domain complexity | Are the rules worth explicit modeling? |

The principle is:

> **Separate when the boundary provides meaningful value.**
# 79. Production Architecture Checklist

### Domain
- [ ] Business rules are explicit.
- [ ] Important invariants are visible.
- [ ] Important rules are independently testable.

### Effects
- [ ] DB/HTTP/files/queues/model calls are identifiable.
- [ ] Time/randomness/configuration are deliberate dependencies.
- [ ] Shared mutable state has an owner.

### Dependencies
- [ ] Dependencies are explicit.
- [ ] Protocols are used only where useful.
- [ ] Provider-specific details stay near adapters.

### Transactions
- [ ] Transaction ownership is clear.
- [ ] Failure windows are understood.
- [ ] Local atomicity is not confused with distributed atomicity.

### Errors
- [ ] Domain/application/infrastructure errors are distinguishable where useful.
- [ ] Specific exceptions are caught.
- [ ] Causes are preserved when translating.

### Retries
- [ ] Retryable errors are classified.
- [ ] Timeouts are treated as potentially ambiguous outcomes.
- [ ] Idempotency/reconciliation is designed.

### Testing
- [ ] Pure logic has direct unit tests.
- [ ] Adapters have integration/contract tests where needed.
- [ ] Critical workflows have end-to-end coverage.

### Observability
- [ ] Useful logs, metrics, and traces exist at effect boundaries.
- [ ] Sensitive data is protected.
- [ ] Dependency failures can be localized.

### Architecture
- [ ] Each abstraction reduces meaningful complexity.
- [ ] Provider changes are localized.
- [ ] The use-case flow remains understandable.

# 80. Performance and Complexity

Separation can add:

- function calls;
- object creation;
- DTO/domain mapping;
- copying;
- serialization;
- adapter indirection;
- transaction work.

External effects usually dominate latency far more than small local function calls, but do not assume this for every workload.

Measure:

- algorithmic complexity;
- allocation/copying;
- database latency;
- network latency;
- retry frequency;
- cache hit rate;
- transaction duration.

Prefer clarity until measurements show a real hotspot. A more abstract architecture is not automatically faster, and a pure implementation is not automatically faster.
# 81. Concurrency and Async

Separation helps reduce hidden shared state:

```text
explicit input -> deterministic calculation -> explicit result
```

But concurrency safety still requires analysis of:

- DB transactions/locks;
- cache behavior;
- shared mutable objects;
- task cancellation;
- message duplication;
- process boundaries.

Async should generally live where asynchronous I/O is performed. Pure CPU transformations can stay ordinary synchronous functions.

Do not claim “pure = thread-safe application.” Pure functions help, but system-level concurrency depends on the whole state graph.
# 82. Distributed Systems

When effects cross services, process boundaries, or cloud providers, expect:

- partial failure;
- retries;
- duplicate delivery;
- eventual consistency;
- independent timeouts;
- uncertain outcomes.

Useful reliability concepts:

- idempotency;
- outbox;
- timeouts;
- targeted retries;
- circuit breakers conceptually;
- reconciliation;
- observability.

Do not over-expand this topic into a full distributed-systems course. The key lesson is that effect boundaries become more important as failure domains multiply.
# 83. Event-Driven Architecture

A practical event-driven workflow:

```text
Command
  |
  v
Application Use Case
  |
  v
Domain State Transition
  |
  v
Event Data
  |
  v
Outbox / Broker
  |
  +--> downstream consumers
```

The core can produce event data. The external publish is an effect.

Questions to answer:

- When is the event considered committed?
- What happens if publication is delayed?
- Can consumers see duplicates?
- Is event processing idempotent?
- Is the event versioned?

# 84. Advanced Production Architecture

Use this review sequence:

```text
INPUT
  |
  v
Transport validation
  |
  v
Application use case
  |
  +----> retrieve external state
  |
  v
Domain validation/rules
  |
  v
State transition
  |
  +----> transaction boundary
  |
  +----> external effects
  |
  v
Result mapping
```

For each edge, document:

- data shape;
- owner;
- failure mode;
- retry behavior;
- idempotency;
- transaction scope;
- observability;
- test strategy.

A mature engineer can explain not only where code lives, but why the dependency direction exists.
# Appendix A — Detailed Production Review Heuristics

### Strong signals

- domain functions consume explicit data;
- application workflows read like a sequence;
- adapter/provider code is clearly identifiable;
- tests can reproduce business decisions without infrastructure;
- configuration is loaded at a controlled boundary;
- time and randomness are controllable;
- provider-specific exceptions are translated;
- retries and idempotency are designed together;
- transaction ownership is explicit;
- event publication consistency is intentional.

### Warning signals

- `requests.get()` inside a function named `calculate_*`;
- `os.getenv()` inside policy logic;
- `datetime.now()` spread through domain code;
- SQL strings inside business rules;
- global clients required for every unit test;
- repository abstractions that mirror an entire ORM API;
- Protocols for private helpers with no substitution need;
- retry loops around payment/email/message effects without idempotency;
- controller code that contains domain policy;
- domain objects that require a database session to inspect their state.

These are review signals, not absolute proof of bad architecture.
# Appendix B — Final Interview Drill

Answer these aloud without notes:

1. Which code is the domain rule in a mixed workflow?
2. Why is current time a dependency?
3. How do you make configuration explicit?
4. How do you isolate a database repository?
5. When does a Protocol help?
6. What is a port?
7. What is an adapter?
8. Where should retries live?
9. Why is a timeout different from a confirmed failure?
10. What is idempotency?
11. What does an outbox solve?
12. How do you separate an LLM call from prompt construction?
13. How do you separate agent planning from tool execution?
14. How do pure transformations help data pipelines?
15. When would you deliberately keep code simple rather than introduce another layer?

A strong Applied AI Engineer can answer these as concrete engineering trade-offs rather than slogans.