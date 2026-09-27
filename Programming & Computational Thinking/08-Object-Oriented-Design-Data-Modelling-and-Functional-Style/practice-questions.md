# Module 08 Practice Questions

## How to Use This Practice Set

This practice set is based on the eight completed Module 08 learning files. The questions deliberately move from foundational implementation to debugging, refactoring, design, and production architecture.

For each question, read the **Problem** and **Requirements** first. Try to solve it without looking at the **Solution**. Then compare your design with the solution and focus on the reasoning in **How to Solve It** and **Why This Solution Works** rather than only on the final code.

The four difficulty levels are based on reasoning depth, number of interacting concepts, and architectural consequences—not simply on code length.

# Part 1 — Basic Questions

### Question 1

#### Problem

A `BankAccount` object exposes its balance as a public attribute. Any caller can assign an invalid balance directly:

```python
class BankAccount:
    def __init__(self, balance: int):
        self.balance = balance
```

A new requirement says the account balance must never become negative through an ordinary withdrawal operation. Refactor the class so the state is controlled.

#### Requirements

- Keep the account balance in instance state.
- Provide a read-only `balance` view.
- Add a `withdraw(amount)` method.
- Reject non-positive withdrawals.
- Reject withdrawals larger than the available balance.
- Raise `ValueError` for invalid operations.

#### Expected Outcome

The caller can read `account.balance`, but cannot directly replace the internal balance through that property. Invalid withdrawals are rejected before state changes.

#### Solution

```python
class BankAccount:
    def __init__(self, balance: int):
        if balance < 0:
            raise ValueError("balance cannot be negative")
        self._balance = balance

    @property
    def balance(self) -> int:
        return self._balance

    def withdraw(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient balance")
        self._balance -= amount


account = BankAccount(100)
account.withdraw(30)
print(account.balance)
```

Output:

```text
70
```

#### How to Solve It

1. Identify the state that needs protection: the balance.
2. Move it behind an internal attribute, `_balance`.
3. Use a property to expose controlled read access.
4. Put the business invariant in the operation that mutates the state.
5. Mutate state only after all checks succeed.

#### Why This Solution Works

Encapsulation gives the object ownership of its state. The property is an access boundary, while `withdraw()` is the controlled mutation boundary. This is stronger than relying on callers to remember the rule themselves. The design also keeps the invariant close to the state it protects.

#### Common Mistake(s)

- Leaving `balance` directly writable and merely adding validation elsewhere.
- Checking the withdrawal amount after subtracting it.
- Treating the leading underscore as a security feature. `_balance` is a Python convention for internal use, not enforcement.

#### Key Learning

Encapsulation is about controlling access to state and protecting invariants; abstraction is about exposing the behavior or concept callers actually need.

### Question 2

#### Problem

A team writes this class:

```python
class Worker:
    tasks = []

    def __init__(self, name: str):
        self.name = name

    def add_task(self, task: str) -> None:
        self.tasks.append(task)


alice = Worker("Alice")
bob = Worker("Bob")
alice.add_task("build")

print(alice.tasks)
print(bob.tasks)
```

They expect Alice and Bob to have independent task lists, but both show the same task. Fix the design.

#### Requirements

- Each `Worker` must own its own task list.
- Preserve the `name` attribute.
- Keep `add_task()` unchanged in purpose.
- Demonstrate the corrected independent state.

#### Expected Outcome

Alice's task list contains only `"build"`; Bob's task list is empty.

#### Solution

```python
class Worker:
    def __init__(self, name: str):
        self.name = name
        self.tasks = []

    def add_task(self, task: str) -> None:
        self.tasks.append(task)


alice = Worker("Alice")
bob = Worker("Bob")
alice.add_task("build")

print(alice.tasks)
print(bob.tasks)
```

Output:

```text
['build']
[]
```

#### How to Solve It

1. Ask who owns `tasks`.
2. A worker's task list is per-object state, not shared class state.
3. Therefore create the list inside `__init__`.
4. The method can continue mutating `self.tasks` because the list now belongs to that instance.

#### Why This Solution Works

Class attributes live on the class and can be found through instances during attribute lookup. A mutable class attribute therefore becomes shared state unless shadowed by an instance attribute. Creating `self.tasks` gives every object a separate list and a separate state lifecycle.

#### Common Mistake(s)

- Changing `tasks = []` to `tasks = tuple()` while leaving `add_task()` unchanged.
- Assuming `self.tasks` automatically means a separate object even when no instance attribute exists.
- Reassigning the class attribute instead of creating instance state.

#### Key Learning

Always ask whether state belongs to the class or to each instance. Mutable class attributes are a common source of accidental shared state.

### Question 3

#### Problem

You need a small value object representing a monetary amount. It should support equality by value and must not be accidentally changed after creation.

#### Requirements

- Use a dataclass.
- Store `amount` and `currency`.
- Make instances frozen.
- Create two equal values and show that equality works.
- Demonstrate that rebinding a field is rejected.

#### Expected Outcome

Two objects with the same values compare equal, and assigning a new amount raises a dataclass-generated `FrozenInstanceError`.

#### Solution

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str


first = Money(500, "INR")
second = Money(500, "INR")

print(first == second)

try:
    first.amount = 600
except Exception as exc:
    print(type(exc).__name__)
```

Output:

```text
True
FrozenInstanceError
```

#### How to Solve It

1. The object is mainly data, so `@dataclass` is appropriate.
2. Value-like behavior means generated equality is useful.
3. `frozen=True` prevents ordinary field assignment after initialization.
4. Compare the two instances to verify value equality.
5. Attempt assignment to confirm the frozen behavior.

#### Why This Solution Works

A frozen dataclass models a value object conveniently. It provides generated methods such as `__init__`, `__repr__`, and `__eq__`, while `frozen=True` adds assignment restrictions. This is shallow immutability: nested mutable objects, if added later, would still require separate consideration.

#### Common Mistake(s)

- Saying that `frozen=True` makes every nested object deeply immutable.
- Confusing object identity with equality.
- Using a mutable default such as `tags: list[str] = []` in a dataclass.

#### Key Learning

Dataclasses reduce boilerplate for data-oriented types. Frozen dataclasses are useful for value objects, but frozen does not mean the entire object graph is deeply immutable.

### Question 4

#### Problem

A base class defines common report formatting, and a subclass needs to specialize the content while preserving the base setup.

```python
class Report:
    def __init__(self, title: str):
        self.title = title

    def render(self) -> str:
        return f"Report: {self.title}"
```

Create a `SalesReport` subclass that adds a region and overrides `render()` while still using the base implementation.

#### Requirements

- Inherit from `Report`.
- Accept `title` and `region` in the child constructor.
- Initialize the base class correctly.
- Override `render()`.
- Use `super()` to reuse the base behavior.

#### Expected Outcome

`SalesReport("Revenue", "East").render()` returns `"Report: Revenue [East]"`.

#### Solution

```python
class Report:
    def __init__(self, title: str):
        self.title = title

    def render(self) -> str:
        return f"Report: {self.title}"


class SalesReport(Report):
    def __init__(self, title: str, region: str):
        super().__init__(title)
        self.region = region

    def render(self) -> str:
        return f"{super().render()} [{self.region}]"


report = SalesReport("Revenue", "East")
print(report.render())
```

Output:

```text
Report: Revenue [East]
```

#### How to Solve It

1. Extend the constructor signature with the new child-specific state.
2. Call `super().__init__(title)` so the inherited initialization contract is respected.
3. Store the child state on the instance.
4. Override `render()` and delegate the shared part to `super().render()`.

#### Why This Solution Works

Inheritance is useful when the child is a genuine specialization of the parent contract. `super()` follows the method-resolution order rather than meaning "call my parent directly," which becomes especially important with multiple inheritance. Here the child extends, rather than replaces, the base behavior.

#### Common Mistake(s)

- Forgetting `super().__init__()` and leaving `title` uninitialized.
- Reimplementing the base formatting unnecessarily.
- Thinking overriding and overloading are the same concept.

#### Key Learning

Inheritance provides reuse and specialization. `super()` is the mechanism for cooperating with inherited behavior and the MRO.

### Question 5

#### Problem

You want a reporting service to accept any object that can produce a text report. The implementation should not require subclasses to inherit from the service's own base class.

#### Requirements

- Define a small `Protocol` named `Reporter` with `render() -> str`.
- Write `generate_summary(reporter)` using that contract.
- Create one implementation that does not inherit from `Reporter`.
- Explain why the implementation can still be used.

#### Expected Outcome

An object with a compatible `render()` method can be passed to `generate_summary()` without explicit inheritance.

#### Solution

```python
from typing import Protocol


class Reporter(Protocol):
    def render(self) -> str:
        ...


def generate_summary(reporter: Reporter) -> str:
    return reporter.render()


class DailyReport:
    def render(self) -> str:
        return "daily report"


print(generate_summary(DailyReport()))
```

Output:

```text
daily report
```

#### How to Solve It

1. Identify the behavior the consumer needs: `render()`.
2. Express that behavior as a small Protocol.
3. Type the consumer against the Protocol instead of a concrete class.
4. Create a normal class with a compatible method.
5. Pass it to the consumer.

#### Why This Solution Works

A Protocol supports structural typing for static type checkers. `DailyReport` does not need to inherit from `Reporter`; it is compatible because it provides the required operation. This reduces unnecessary coupling to a class hierarchy while keeping the expected contract visible.

#### Common Mistake(s)

- Assuming `Protocol` automatically performs runtime validation of behavior.
- Requiring every implementation to inherit from the Protocol.
- Making the Protocol much larger than the consumer actually needs.

#### Key Learning

A useful interface describes the behavior a consumer needs. Python's `Protocol` can express that contract without requiring nominal inheritance.

### Question 6

#### Problem

Classify and repair this function:

```python
import random


def total_with_bonus(values):
    values.append(100)
    return sum(values) + random.choice([0, 10])
```

You need a deterministic transformation that does not mutate its input.

#### Requirements

- Remove the mutation of `values`.
- Remove the hidden randomness from the function.
- Make all relevant inputs explicit.
- Return a deterministic result.

#### Expected Outcome

Calling the function twice with the same inputs produces the same result and leaves the original list unchanged.

#### Solution

```python
def total_with_bonus(values, bonus: int) -> int:
    return sum(values) + 100 + bonus


values = [10, 20]
result1 = total_with_bonus(values, 5)
result2 = total_with_bonus(values, 5)

print(values)
print(result1 == result2)
print(result1)
```

Output:

```text
[10, 20]
True
135
```

#### How to Solve It

1. List the observable effects: list mutation and randomness.
2. Decide whether each effect is actually part of the domain rule. For this exercise, it is not.
3. Represent the bonus as an explicit input.
4. Return the computed value without mutating the list.

#### Why This Solution Works

The corrected function has explicit data flow and deterministic behavior. That makes it much easier to test, debug, cache when appropriate, and compose with other transformations. Functional style is being used as a tool for predictability, not as a rule that all production code must be pure.

#### Common Mistake(s)

- Making a copy and leaving randomness hidden inside the function.
- Calling a function that mutates input and assuming returning a value makes it pure.
- Treating randomness as universally bad rather than as a dependency that should be explicit when the behavior requires it.

#### Key Learning

A function that returns a value can still be impure. Purity requires reasoning about hidden dependencies, mutation, and observable effects—not merely the presence of `return`.

### Question 7

#### Problem

Consider this function:

```python
def process_file(path, repository, logger):
    text = open(path, "r", encoding="utf-8").read()
    value = text.strip().lower()
    repository.save(value)
    logger.info("saved %s", value)
    return value
```

Identify which parts are domain logic and which parts are side effects.

#### Requirements

- Separate file reading from transformation.
- Keep the transformation as a pure function.
- Explain what remains in the effectful shell.

#### Expected Outcome

The string normalization can be tested independently of the filesystem, repository, and logger.

#### Solution

```python
def normalize_text(text: str) -> str:
    return text.strip().lower()


def process_file(path, repository, logger) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()

    value = normalize_text(text)
    repository.save(value)
    logger.info("saved %s", value)
    return value
```

#### How to Solve It

1. Mark operations that interact with the external world: `open`, repository persistence, and logging.
2. Identify the business-neutral transformation: stripping and lowercasing text.
3. Extract that transformation into a function whose behavior depends only on its argument.
4. Leave orchestration and effects in the outer function.

#### Why This Solution Works

This is the functional core / imperative shell idea in a small form. The pure transformation becomes easy to test and reason about. The shell coordinates I/O and external dependencies. The separation does not remove side effects; it gives them a clear boundary.

#### Common Mistake(s)

- Calling all string processing infrastructure because it happens inside an I/O function.
- Moving logging into `normalize_text()`.
- Attempting to make the whole workflow pure even though persistence is an intentional effect.

#### Key Learning

When reading mixed code, ask: "What is the business transformation?" and "What interacts with the outside world?" That classification is the foundation for good boundaries.

### Question 8

#### Problem

This service is tightly coupled to a concrete database implementation:

```python
class Database:
    def save(self, value: str) -> None:
        print(f"saving {value}")


class ReportService:
    def __init__(self):
        self.db = Database()

    def save_report(self, value: str) -> None:
        self.db.save(value)
```

Refactor it so the dependency is supplied from outside.

#### Requirements

- Use constructor injection.
- Do not instantiate `Database` inside `ReportService`.
- Keep the service focused on orchestration.
- Show a simple fake dependency for a test.

#### Expected Outcome

`ReportService` works with both the real database implementation and a test double without changing the service code.

#### Solution

```python
class Database:
    def save(self, value: str) -> None:
        print(f"saving {value}")


class FakeDatabase:
    def __init__(self):
        self.saved = []

    def save(self, value: str) -> None:
        self.saved.append(value)


class ReportService:
    def __init__(self, db):
        self.db = db

    def save_report(self, value: str) -> None:
        self.db.save(value)


fake = FakeDatabase()
service = ReportService(fake)
service.save_report("report-1")
print(fake.saved)
```

Output:

```text
['report-1']
```

#### How to Solve It

1. Find where the concrete dependency is created.
2. Move that construction outside the service.
3. Add a constructor parameter and store the supplied object.
4. At runtime, the composition root chooses `Database()`; in tests, it chooses `FakeDatabase()`.

#### Why This Solution Works

Constructor injection makes the service's dependency explicit. It is a technique that supports easier substitution and testing. Dependency Injection is not the same thing as Dependency Inversion: injection changes how a dependency is supplied, while inversion is a design principle about which direction high-level policy depends on details.

#### Common Mistake(s)

- Adding a default `Database()` inside the constructor and believing the dependency is fully inverted.
- Introducing a DI framework before there is a real problem.
- Mocking everything instead of using a simple fake when a fake is clearer.

#### Key Learning

Explicit dependencies are easier to reason about. Python's flexible object model often lets you use DI directly without a container framework.

# Part 2 — Moderate Questions

### Question 9

#### Problem

A notification system has grown into a hierarchy:

```python
class EmailNotifier:
    def send(self, message: str) -> None:
        print(f"email: {message}")


class UrgentEmailNotifier(EmailNotifier):
    def send(self, message: str) -> None:
        print(f"URGENT email: {message}")


class SmsNotifier(EmailNotifier):
    def send(self, message: str) -> None:
        print(f"sms: {message}")
```

The team now needs email, SMS, and in-app notifications to be combined in the same workflow. Refactor the design to favor composition over an artificial inheritance relationship.

#### Requirements

- Do not make `SmsNotifier` a subclass of `EmailNotifier`.
- Define a small notification behavior contract.
- Build a service that can contain multiple notification implementations.
- Demonstrate using two different notifiers together.
- Keep the implementations independent.

#### Expected Outcome

The notification service can send a message through any supplied notifier without requiring those notifiers to share a concrete inheritance hierarchy.

#### Solution

```python
from typing import Protocol


class Notifier(Protocol):
    def send(self, message: str) -> None:
        ...


class EmailNotifier:
    def send(self, message: str) -> None:
        print(f"email: {message}")


class SmsNotifier:
    def send(self, message: str) -> None:
        print(f"sms: {message}")


class NotificationService:
    def __init__(self, notifiers: list[Notifier]):
        self.notifiers = list(notifiers)

    def notify(self, message: str) -> None:
        for notifier in self.notifiers:
            notifier.send(message)


service = NotificationService([EmailNotifier(), SmsNotifier()])
service.notify("Order shipped")
```

Output:

```text
email: Order shipped
sms: Order shipped
```

#### How to Solve It

1. Ask whether email and SMS are true specializations of the same concrete type. They are not; they are different strategies for performing notification.
2. Identify the behavior the service needs: `send(message)`.
3. Put that behavior behind a small Protocol.
4. Compose a service from multiple implementations.
5. Keep the concrete notifiers independent.

#### Why This Solution Works

Composition models a "has many notification mechanisms" relationship directly. The Protocol makes the dependency visible without forcing unrelated implementations into one class tree. This also makes later replacement or testing straightforward. Inheritance would still be valid when a real subtype relationship and a stable parent contract exist, but it is not required merely to obtain polymorphism.

#### Common Mistake(s)

- Creating a `BaseNotifier` only so every class has a parent.
- Keeping `SmsNotifier(EmailNotifier)` even though SMS is not an email specialization.
- Replacing the hierarchy with a huge interface containing unrelated notification operations.

#### Key Learning

Composition and Protocol-based polymorphism are complementary tools. Prefer the relationship that matches the domain rather than forcing reuse through inheritance.

### Question 10

#### Problem

You receive a request model containing a mutable list, then store it inside a supposedly immutable configuration object:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    model_name: str
    stop_words: list[str]


config = ModelConfig("classifier", ["a", "the"])
```

A caller still has a way to mutate the list. Redesign the data model so the configuration's collection is immutable at the boundary.

#### Requirements

- Keep `ModelConfig` frozen.
- Store `stop_words` as an immutable sequence suitable for read-only use.
- Demonstrate that assigning a field is rejected.
- Demonstrate that the stop-word collection cannot be appended to.
- Explain the remaining difference between immutable and merely frozen state.

#### Expected Outcome

The outer dataclass cannot have its fields reassigned, and the `stop_words` collection itself cannot be mutated through list methods.

#### Solution

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    model_name: str
    stop_words: tuple[str, ...]


config = ModelConfig("classifier", ("a", "the"))
print(config.stop_words)

try:
    config.model_name = "other"
except Exception as exc:
    print(type(exc).__name__)

try:
    config.stop_words.append("an")
except AttributeError as exc:
    print(type(exc).__name__)
```

Output:

```text
('a', 'the')
FrozenInstanceError
AttributeError
```

#### How to Solve It

1. `frozen=True` controls assignment to dataclass fields.
2. The original `list` remains mutable even inside a frozen dataclass.
3. Replace the nested list with a tuple.
4. Keep the dataclass frozen so callers cannot reassign the tuple field either.

#### Why This Solution Works

Immutability applies to objects, not names. A frozen dataclass prevents ordinary assignment to its fields, but it does not recursively freeze referenced objects. Modeling a collection as a tuple makes that part of the object graph immutable too. This is still not a claim of universal deep immutability: arbitrary nested objects need their own appropriate modeling.

#### Common Mistake(s)

- Believing `frozen=True` recursively freezes every nested object.
- Replacing a tuple with a mutable list after construction.
- Confusing `config = other_config` rebinding with mutation of `config`.

#### Key Learning

Frozen containers and immutable nested values work together. Good immutable data modeling starts by asking what can still be mutated through each reference.

### Question 11

#### Problem

A logging system uses two mixins that both define `format()` and rely on cooperative inheritance:

```python
class TimestampMixin:
    def format(self, message: str) -> str:
        return f"[time] {super().format(message)}"


class LevelMixin:
    def format(self, message: str) -> str:
        return f"[INFO] {super().format(message)}"
```

The class below must produce a final string, but it currently has no terminal implementation.

#### Requirements

- Add a base class with the terminal `format()` implementation.
- Create a class using both mixins.
- Make cooperative `super()` calls work through the MRO.
- State the resulting MRO.
- Show the output.

#### Expected Outcome

The chain executes through both mixins and terminates in the base class, producing `[time] [INFO] hello`.

#### Solution

```python
class BaseFormatter:
    def format(self, message: str) -> str:
        return message


class TimestampMixin:
    def format(self, message: str) -> str:
        return f"[time] {super().format(message)}"


class LevelMixin:
    def format(self, message: str) -> str:
        return f"[INFO] {super().format(message)}"


class ConsoleFormatter(TimestampMixin, LevelMixin, BaseFormatter):
    pass


formatter = ConsoleFormatter()
print(formatter.format("hello"))
print([cls.__name__ for cls in ConsoleFormatter.__mro__])
```

Output:

```text
[time] [INFO] hello
['ConsoleFormatter', 'TimestampMixin', 'LevelMixin', 'BaseFormatter', 'object']
```

#### How to Solve It

1. A cooperative chain needs a terminal implementation.
2. Put the terminal behavior in `BaseFormatter`.
3. Order the mixins in the desired MRO.
4. Each mixin must use `super()` rather than naming a particular parent.
5. Inspect `__mro__` to verify the actual lookup order.

#### Why This Solution Works

Python's multiple inheritance uses a consistent method-resolution order. Cooperative mixins can wrap behavior by forwarding through `super()`. The technique is powerful but requires every participant to honor a compatible contract; otherwise one class can break the chain.

#### Common Mistake(s)

- Calling `TimestampMixin.format(self, message)` manually and bypassing the MRO.
- Omitting the terminal implementation.
- Using mixins that expect incompatible method signatures.

#### Key Learning

Multiple inheritance is not simply "search the first parent." Python follows the MRO, and cooperative inheritance works only when participating classes agree on the call chain.

### Question 12

#### Problem

A checkout service directly constructs its payment gateway, making it hard to test:

```python
class PaymentGateway:
    def charge(self, amount: int) -> str:
        return "real-payment"


class CheckoutService:
    def __init__(self):
        self.gateway = PaymentGateway()

    def checkout(self, amount: int) -> str:
        return self.gateway.charge(amount)
```

Refactor it to use a Protocol and constructor injection, then test with a fake implementation.

#### Requirements

- Define `PaymentGateway` as a Protocol with `charge(amount: int) -> str`.
- Rename the concrete gateway if necessary so the contract and implementation are distinct.
- Inject the gateway through the constructor.
- Provide a fake gateway.
- Test without constructing the concrete gateway.

#### Expected Outcome

The service can be tested entirely in memory and accepts any structurally compatible gateway.

#### Solution

```python
from typing import Protocol


class PaymentGateway(Protocol):
    def charge(self, amount: int) -> str:
        ...


class RemotePaymentGateway:
    def charge(self, amount: int) -> str:
        return f"remote-{amount}"


class FakePaymentGateway:
    def __init__(self):
        self.charges: list[int] = []

    def charge(self, amount: int) -> str:
        self.charges.append(amount)
        return "fake-payment"


class CheckoutService:
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway

    def checkout(self, amount: int) -> str:
        if amount <= 0:
            raise ValueError("amount must be positive")
        return self.gateway.charge(amount)


fake = FakePaymentGateway()
service = CheckoutService(fake)

print(service.checkout(250))
print(fake.charges)
```

Output:

```text
fake-payment
[250]
```

#### How to Solve It

1. Identify the stable behavior required by checkout.
2. Express that behavior as a Protocol.
3. Remove concrete construction from the high-level service.
4. Inject either a real adapter or a fake.
5. Keep domain/application validation in the service or domain layer rather than in the gateway contract.

#### Why This Solution Works

The service now depends on a contract instead of a concrete infrastructure class. The fake provides the same required behavior and records calls for assertions. This supports dependency inversion and dependency injection together, without requiring a framework.

#### Common Mistake(s)

- Calling `PaymentGateway()` as though a Protocol were a concrete implementation.
- Making the Protocol include vendor-specific methods.
- Testing only that `FakePaymentGateway` was called without testing the business rule itself.

#### Key Learning

Use a small abstraction at a meaningful dependency boundary. Inject concrete implementations from outside the high-level policy.

### Question 13

#### Problem

You have a collection of raw customer names. The desired transformation is: trim whitespace, normalize case, and retain only names with at least five characters after normalization.

#### Requirements

- Build the transformation from reusable functions.
- Keep the transformations pure.
- Use a functional pipeline.
- Avoid mutating the input list.
- Show the final result.

#### Expected Outcome

Input `[' Alice ', 'BOB', '  carol  ', 'Dee ']` becomes `['alice', 'carol']`.

#### Solution

```python
def normalize(name: str) -> str:
    return name.strip().lower()


def long_enough(name: str) -> bool:
    return len(name) >= 5


def clean_names(names: list[str]) -> list[str]:
    normalized = map(normalize, names)
    filtered = filter(long_enough, normalized)
    return list(filtered)


names = [" Alice ", "BOB", "  carol  ", "Dee "]
print(clean_names(names))
print(names)
```

Output:

```text
['alice', 'carol']
[' Alice ', 'BOB', '  carol  ', 'Dee ']
```

#### How to Solve It

1. Separate normalization from filtering.
2. Make normalization and the predicate pure functions.
3. Feed the output of `map()` into `filter()`.
4. Consume the lazy pipeline with `list()` at the boundary where a concrete collection is needed.
5. Verify the original input remains unchanged.

#### Why This Solution Works

The pipeline makes the data flow explicit. `map()` and `filter()` return lazy iterators, so the transformations can be chained without creating intermediate lists for every stage. A list comprehension could also be clearer for a short one-off transformation; functional tools are not automatically superior.

#### Common Mistake(s)

- Calling `normalize` before passing it and accidentally supplying its result instead of a function object.
- Mutating `names` during normalization.
- Forgetting to consume the iterator when a concrete list is required.

#### Key Learning

Higher-order functions enable reusable transformations. Choose `map()`, `filter()`, comprehensions, or explicit loops based on clarity and workload rather than ideology.

### Question 14

#### Problem

This order-processing function mixes data retrieval, business calculation, persistence, and notification:

```python
def finalize_order(order_id, repository, notifier):
    order = repository.get(order_id)
    subtotal = sum(item["price"] * item["quantity"] for item in order["items"])
    discount = subtotal * 0.10 if subtotal >= 1000 else 0
    total = subtotal - discount
    repository.save_total(order_id, total)
    notifier.send(order["customer_id"], total)
    return total
```

Refactor the business rule into a pure function and leave orchestration in an application-level function.

#### Requirements

- Extract a pure `calculate_total(order)` function.
- Keep repository and notifier operations outside it.
- Preserve the original discount rule.
- Make the pure function independently testable.

#### Expected Outcome

The pure calculation can run with a plain order object and has no repository or notifier dependency.

#### Solution

```python
def calculate_total(order: dict) -> float:
    subtotal = sum(
        item["price"] * item["quantity"]
        for item in order["items"]
    )
    discount = subtotal * 0.10 if subtotal >= 1000 else 0
    return subtotal - discount


def finalize_order(order_id, repository, notifier) -> float:
    order = repository.get(order_id)
    total = calculate_total(order)
    repository.save_total(order_id, total)
    notifier.send(order["customer_id"], total)
    return total


sample_order = {
    "customer_id": "c-1",
    "items": [
        {"price": 600, "quantity": 2},
        {"price": 200, "quantity": 1},
    ],
}

print(calculate_total(sample_order))
```

Output:

```text
1260.0
```

#### How to Solve It

1. Identify which lines only calculate a result from existing data.
2. Extract those lines into `calculate_total()`.
3. Leave loading, saving, and notification in the orchestrator.
4. Pass all business inputs explicitly.
5. Test the pure function without any external dependency.

#### Why This Solution Works

The domain rule is now isolated from infrastructure. The outer function is allowed to be effectful because it coordinates the use case. This is functional core / imperative shell applied within an application service.

#### Common Mistake(s)

- Moving `repository.get()` into the pure function.
- Creating a global discount constant that hides part of the rule without a clear ownership decision.
- Claiming the whole `finalize_order()` function must become pure.

#### Key Learning

A useful refactoring target is not "make every function pure." It is "make the important business rule independently testable and keep effects at explicit boundaries."

### Question 15

#### Problem

An API receives this JSON-like dictionary:

```python
{
    "customer_id": "c-10",
    "items": [
        {"sku": "A1", "quantity": 2, "price": 50}
    ]
}
```

The database layer expects an internal `Order` model. Define separate request and domain models and map between them.

#### Requirements

- Use dataclasses.
- Define `CreateOrderRequest`, `OrderItem`, and `Order`.
- Validate that quantity is positive.
- Convert the external representation to the domain representation.
- Do not use the raw API dictionary inside the domain rule.

#### Expected Outcome

The API boundary converts untrusted external data into typed domain objects before business logic executes.

#### Solution

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderRequest:
    customer_id: str
    items: list[dict]


@dataclass(frozen=True)
class OrderItem:
    sku: str
    quantity: int
    price: int


@dataclass(frozen=True)
class Order:
    customer_id: str
    items: tuple[OrderItem, ...]


def to_domain(request: CreateOrderRequest) -> Order:
    items = []
    for raw_item in request.items:
        quantity = raw_item["quantity"]
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        items.append(
            OrderItem(
                sku=raw_item["sku"],
                quantity=quantity,
                price=raw_item["price"],
            )
        )
    return Order(request.customer_id, tuple(items))


request = CreateOrderRequest(
    customer_id="c-10",
    items=[{"sku": "A1", "quantity": 2, "price": 50}],
)
order = to_domain(request)
print(order.items[0].sku)
```

Output:

```text
A1
```

#### How to Solve It

1. Identify the boundary representation: API data.
2. Create a domain model that expresses the internal concept.
3. Convert and validate at the boundary.
4. Store domain items in a tuple to prevent accidental collection mutation after conversion.
5. Pass the domain object to domain functions.

#### Why This Solution Works

DTO-style request data and domain models can evolve for different reasons. Separating them prevents HTTP/JSON shape from becoming the application's internal model. The domain object is also easier to reason about and test because the expected structure is explicit.

#### Common Mistake(s)

- Passing the raw dictionary through every layer.
- Treating a frozen dataclass as automatically deep-immutable while storing mutable nested values.
- Duplicating the same validation in every layer without deciding which boundary owns which rule.

#### Key Learning

A boundary often exists partly to translate representations. DTO-to-domain mapping can reduce coupling, but simple applications may reasonably combine models when the complexity does not justify separation.

### Question 16

#### Problem

Two Python modules have become circularly dependent:

```text
orders.py      imports PaymentService from payments.py
payments.py    imports Order from orders.py
```

The import cycle causes initialization problems. Redesign the dependency so the modules do not need to import each other's concrete implementation.

#### Requirements

- Keep `Order` as a domain model.
- Keep payment behavior behind a small contract.
- Make the application service depend on the contract rather than a concrete payment module.
- Explain where concrete construction should occur.

#### Expected Outcome

The dependency graph becomes one-directional: the application/domain-facing code depends on a stable contract, while infrastructure supplies an implementation from the composition root.

#### Solution

```python
# domain.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_id: str
    amount: int
```

```python
# ports.py
from typing import Protocol

from domain import Order


class PaymentGateway(Protocol):
    def charge(self, order: Order) -> str:
        ...
```

```python
# application.py
from domain import Order
from ports import PaymentGateway


class CheckoutService:
    def __init__(self, payment_gateway: PaymentGateway):
        self.payment_gateway = payment_gateway

    def checkout(self, order: Order) -> str:
        return self.payment_gateway.charge(order)
```

```python
# infrastructure.py
from domain import Order


class RemotePaymentGateway:
    def charge(self, order: Order) -> str:
        return f"charged:{order.order_id}"
```

```python
# main.py
from application import CheckoutService
from infrastructure import RemotePaymentGateway


service = CheckoutService(RemotePaymentGateway())
```

#### How to Solve It

1. Separate the stable domain model from infrastructure concerns.
2. Identify the behavior the application needs from payments.
3. Put that contract in a module that does not import the concrete payment implementation.
4. Make the application depend on the contract.
5. Construct the concrete adapter at the composition root.

#### Why This Solution Works

The import graph now reflects the desired architecture. A domain model does not need to know about payment infrastructure, and the application service does not construct a concrete gateway. The code still has dependencies, but they are intentional and directional rather than cyclic.

#### Common Mistake(s)

- Solving the cycle only by moving one import inside a function while keeping the same architectural dependency.
- Creating a giant shared module containing every type.
- Making `ports.py` depend on infrastructure, which simply moves the cycle.

#### Key Learning

Circular imports are often a symptom of architectural dependency cycles. The durable fix is to reconsider responsibility and dependency direction, not merely to hide an import statement.

# Part 3 — Hard Questions

### Question 17

#### Problem

A bank transfer use case is implemented as one tightly coupled function:

```python
def transfer(account_id, destination_id, amount, db, notifier):
    source = db.get_account(account_id)
    destination = db.get_account(destination_id)

    if amount <= 0:
        raise ValueError("amount must be positive")
    if source.balance < amount:
        raise ValueError("insufficient funds")

    source.balance -= amount
    destination.balance += amount
    db.save(source)
    db.save(destination)
    notifier.send(account_id, destination_id, amount)
```

Refactor the design around explicit domain logic and dependency boundaries. You do not need a real database or notification system.

#### Requirements

- Model `Account` as a dataclass with a clear state representation.
- Isolate the transfer rule in a pure domain function.
- Define repository and notification contracts with Protocols.
- Inject those dependencies into an application service.
- Clearly identify where a real transaction boundary would belong.
- Keep notification outside the pure domain rule.

#### Expected Outcome

The transfer rule can be unit-tested without a database or notification service, while the application service coordinates persistence and notification.

#### Solution

```python
from dataclasses import dataclass, replace
from typing import Protocol


@dataclass(frozen=True)
class Account:
    account_id: str
    balance: int


class AccountRepository(Protocol):
    def get(self, account_id: str) -> Account:
        ...

    def save(self, account: Account) -> None:
        ...


class TransferNotifier(Protocol):
    def send(self, source_id: str, destination_id: str, amount: int) -> None:
        ...


def apply_transfer(
    source: Account,
    destination: Account,
    amount: int,
) -> tuple[Account, Account]:
    if amount <= 0:
        raise ValueError("amount must be positive")
    if source.balance < amount:
        raise ValueError("insufficient funds")

    return (
        replace(source, balance=source.balance - amount),
        replace(destination, balance=destination.balance + amount),
    )


class TransferMoney:
    def __init__(
        self,
        repository: AccountRepository,
        notifier: TransferNotifier,
    ):
        self.repository = repository
        self.notifier = notifier

    def execute(self, source_id: str, destination_id: str, amount: int) -> None:
        source = self.repository.get(source_id)
        destination = self.repository.get(destination_id)

        updated_source, updated_destination = apply_transfer(
            source,
            destination,
            amount,
        )

        self.repository.save(updated_source)
        self.repository.save(updated_destination)
        self.notifier.send(source_id, destination_id, amount)
```

A production repository would normally coordinate both writes within the appropriate transaction boundary, possibly through a Unit of Work rather than independent `save()` calls. The example intentionally keeps that infrastructure concern outside `apply_transfer()`.

#### How to Solve It

1. Separate state from effects by modeling accounts as data.
2. Identify the actual business rule: whether the transfer is valid and what the new balances are.
3. Make the rule a deterministic function over explicit inputs.
4. Identify external capabilities: loading/saving accounts and sending notifications.
5. Define small contracts for those capabilities.
6. Inject them into the use-case service.
7. Treat transaction coordination as an application/infrastructure concern, not part of the pure calculation.

#### Why This Solution Works

The pure function computes a state transition. It does not know where accounts are stored or how notifications are sent. Frozen dataclass instances make accidental in-place mutation less likely and `replace()` expresses "produce new state" clearly. The application service orchestrates effects through explicit dependencies.

The design is not automatically complete for banking production: concurrency control, transaction isolation, idempotency, authorization, audit requirements, and failure handling still need explicit decisions. The value of the boundary is that those concerns can evolve without rewriting the core transfer rule.

#### Common Mistake(s)

- Keeping `db.get_account()` inside `apply_transfer()`.
- Mutating the input accounts and calling the function pure because it returns `None` or a tuple.
- Treating two separate database writes as automatically atomic.
- Assuming Protocols themselves create transaction guarantees.

#### Key Learning

A strong domain boundary is a state-transition boundary: explicit input state enters, business rules run, explicit output state leaves, and infrastructure handles persistence and external effects.

### Question 18

#### Problem

An order system selects behavior with type checks:

```python
class CardPayment:
    def charge(self, amount: int) -> str:
        return f"card:{amount}"


class BankTransfer:
    def charge(self, amount: int) -> str:
        return f"bank:{amount}"


def pay(method, amount: int) -> str:
    if isinstance(method, CardPayment):
        return method.charge(amount)
    if isinstance(method, BankTransfer):
        return method.charge(amount)
    raise TypeError("unsupported payment method")
```

Add a new `WalletPayment` implementation without changing `pay()` and make the common capability explicit.

#### Requirements

- Replace the type-based branching with a `Protocol`.
- Keep the three implementations independent.
- Show polymorphism through the shared behavior.
- Do not require explicit inheritance from the Protocol.
- Explain why this is different from an ABC-based hierarchy.

#### Expected Outcome

`pay()` calls `charge()` on any compatible payment object, including `WalletPayment`, without adding a new `isinstance()` branch.

#### Solution

```python
from typing import Protocol


class PaymentMethod(Protocol):
    def charge(self, amount: int) -> str:
        ...


class CardPayment:
    def charge(self, amount: int) -> str:
        return f"card:{amount}"


class BankTransfer:
    def charge(self, amount: int) -> str:
        return f"bank:{amount}"


class WalletPayment:
    def charge(self, amount: int) -> str:
        return f"wallet:{amount}"


def pay(method: PaymentMethod, amount: int) -> str:
    return method.charge(amount)


methods = [CardPayment(), BankTransfer(), WalletPayment()]
for method in methods:
    print(pay(method, 100))
```

Output:

```text
card:100
bank:100
wallet:100
```

#### How to Solve It

1. Identify the repeated capability shared by all implementations: `charge(amount)`.
2. Put only that capability into a Protocol.
3. Type the consumer against that protocol.
4. Remove concrete type inspection from the consumer.
5. Add new implementations that provide the same behavior.

#### Why This Solution Works

The consumer is coupled to behavior rather than concrete type identity. This is structural polymorphism: compatibility is based on the required members. An ABC would instead provide a nominal class hierarchy and may enforce abstract methods during instantiation. Neither mechanism is universally better; the choice depends on whether a meaningful class hierarchy or merely a capability contract is needed.

#### Common Mistake(s)

- Adding `WalletPayment()` to another `isinstance()` branch.
- Making every implementation inherit from the Protocol because it looks like a normal base class.
- Treating `isinstance(method, PaymentMethod)` as proof that the payment will behave correctly.

#### Key Learning

When a type-based branch exists only to discover whether an object supports an operation, a behavior-oriented abstraction may remove the branching and make extension less invasive.

### Question 19

#### Problem

A batch application uses a class attribute as a cache:

```python
class BatchProcessor:
    cache = {}

    def __init__(self, batch_id: str):
        self.batch_id = batch_id

    def remember(self, key: str, value: str) -> None:
        self.cache[key] = value
```

Tests create several processors and observe data from earlier tests. A production deployment also uses multiple worker threads. Diagnose the design and decide what scope the cache should have.

#### Requirements

- Explain why the current cache is shared.
- Move request/batch-specific state to the appropriate scope.
- If a process-wide cache is genuinely desired, make that ownership explicit.
- Do not claim that changing the attribute automatically solves all thread-safety concerns.

#### Expected Outcome

The batch-specific example has independent state. Any intentionally shared cache is clearly identified as shared state requiring its own concurrency policy.

#### Solution

```python
class BatchProcessor:
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.cache = {}

    def remember(self, key: str, value: str) -> None:
        self.cache[key] = value


first = BatchProcessor("batch-1")
second = BatchProcessor("batch-2")

first.remember("user-1", "done")

print(first.cache)
print(second.cache)
```

Output:

```text
{'user-1': 'done'}
{}
```

#### How to Solve It

1. Determine who owns the data. Here the cache is associated with each batch, so instance scope is appropriate.
2. Move the dictionary into `__init__`.
3. Re-run tests with multiple instances and confirm state is isolated.
4. If the actual requirement is a process-wide shared cache, keep it shared intentionally but document the scope and concurrency semantics instead of pretending it is per-instance state.

#### Why This Solution Works

Class attributes are shared through the class namespace; mutable values therefore become shared mutable state. State ownership is an architectural decision. In concurrent code, removing accidental sharing reduces one source of race conditions, but it does not make the surrounding system automatically thread-safe.

#### Common Mistake(s)

- Assuming `self.cache` is always instance-local even when it was never assigned in `__init__`.
- Using `ClassVar` to describe state and assuming typing changes runtime ownership.
- Adding a lock everywhere without first deciding whether the cache should be shared at all.

#### Key Learning

Before choosing a synchronization mechanism, choose the correct state scope. Module, class, instance, request, and external state have different ownership and concurrency implications.

### Question 20

#### Problem

A team caches a function that reads the current environment:

```python
import os
from functools import cache


@cache
def service_url() -> str:
    return os.getenv("SERVICE_URL", "http://localhost")
```

A test changes `SERVICE_URL` between cases but still receives the old value. Diagnose the problem and redesign the code.

#### Requirements

- Explain why `@cache` is unsafe for the current design.
- Make configuration an explicit input to pure logic where possible.
- Keep environment access at the boundary.
- Show a safe way to construct a configured function or service.

#### Expected Outcome

Changing the environment does not silently leave a stale cached result in the business logic.

#### Solution

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    service_url: str


def build_request(path: str, config: Config) -> str:
    return f"{config.service_url.rstrip('/')}/{path.lstrip('/')}"


config = Config("https://example.invalid")
print(build_request("health", config))
```

Output:

```text
https://example.invalid/health
```

At the application boundary, read the environment once and construct `Config`:

```python
import os


config = Config(os.getenv("SERVICE_URL", "http://localhost"))
```

#### How to Solve It

1. Inspect what determines the function's result. It is not just the explicit arguments; it also depends on the process environment.
2. Recognize that `@cache` assumes repeated calls with the same key can reuse the same result safely.
3. Move environment access to configuration construction.
4. Pass configuration explicitly into the logic that needs it.
5. Cache only functions whose result is stable for the cache's lifetime and whose arguments are suitable cache keys.

#### Why This Solution Works

The redesigned function has explicit inputs. It no longer changes meaning because a hidden environment variable changes. Caching may be reintroduced around a function whose inputs fully capture the result and whose cache lifetime matches the data's validity.

#### Common Mistake(s)

- Calling `cache_clear()` in every test without fixing the architectural hidden dependency.
- Assuming caching is merely a performance feature rather than a semantic commitment to reuse prior results.
- Reading environment variables throughout the domain layer.

#### Key Learning

A cache is safe only when the cache key captures the relevant inputs and the cached result remains valid for the intended lifetime. Explicit configuration makes that reasoning much easier.

### Question 21

#### Problem

An LLM document classifier currently does everything in one function:

```python
def classify_document(text, client, store):
    prompt = f"Classify this document as invoice, contract, or other:\n{text}"
    response = client.generate(prompt)
    label = response.strip().lower()
    store.save(label)
    return label
```

Refactor it so prompt construction and output normalization are independent of the model provider and persistence mechanism.

#### Requirements

- Use a dataclass for the classifier request or result where useful.
- Create pure prompt-building and response-normalization functions.
- Define an LLM client Protocol.
- Define a persistence Protocol.
- Inject both dependencies.
- Show a fake LLM implementation for deterministic testing.

#### Expected Outcome

A unit test can validate prompt construction and output normalization without making an LLM call. The application service can be tested with a fake client and fake store.

#### Solution

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ClassificationRequest:
    text: str


@dataclass(frozen=True)
class ClassificationResult:
    label: str


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class ResultStore(Protocol):
    def save(self, result: ClassificationResult) -> None:
        ...


def build_prompt(request: ClassificationRequest) -> str:
    return (
        "Classify this document as invoice, contract, or other:\n"
        f"{request.text}"
    )


def normalize_label(raw: str) -> ClassificationResult:
    label = raw.strip().lower()
    allowed = {"invoice", "contract", "other"}
    if label not in allowed:
        raise ValueError(f"invalid model label: {label!r}")
    return ClassificationResult(label)


class DocumentClassifier:
    def __init__(self, client: LLMClient, store: ResultStore):
        self.client = client
        self.store = store

    def classify(self, request: ClassificationRequest) -> ClassificationResult:
        prompt = build_prompt(request)
        raw = self.client.generate(prompt)
        result = normalize_label(raw)
        self.store.save(result)
        return result


class FakeLLMClient:
    def generate(self, prompt: str) -> str:
        return "Invoice"


class FakeResultStore:
    def __init__(self):
        self.saved = []

    def save(self, result: ClassificationResult) -> None:
        self.saved.append(result)


store = FakeResultStore()
classifier = DocumentClassifier(FakeLLMClient(), store)
result = classifier.classify(ClassificationRequest("April invoice"))
print(result)
print(store.saved)
```

Output:

```text
ClassificationResult(label='invoice')
[ClassificationResult(label='invoice')]
```

#### How to Solve It

1. Identify pure transformations: prompt construction and label normalization.
2. Identify external effects: model invocation and persistence.
3. Define only the model and storage capabilities the application needs.
4. Inject those capabilities.
5. Keep external calls inside the orchestration boundary.
6. Test the pure functions directly and the orchestration with fakes.

#### Why This Solution Works

The model provider is now an adapter behind a contract. Prompt logic can evolve independently from the provider SDK. Output normalization protects the application from provider-specific formatting. The same structure works whether the underlying adapter calls a hosted API, a local model, or a test fake.

#### Common Mistake(s)

- Putting provider SDK request construction inside `build_prompt()`.
- Caching model calls without considering freshness, side effects, or request identity.
- Treating a fake LLM result as proof that the real provider contract is correct.

#### Key Learning

In AI systems, model calls are effects; prompt construction, validation, parsing, routing, and normalization are often good candidates for isolated pure logic.

### Question 22

#### Problem

A data pipeline reads records from S3, cleans them, calculates a risk bucket, and writes results back to storage. The current transformer calls S3 directly:

```python
def transform_bucket(object_key, s3_client):
    raw_records = s3_client.read_json(object_key)
    output = []
    for record in raw_records:
        score = float(record["score"])
        bucket = "high" if score >= 0.8 else "low"
        output.append({"id": record["id"], "bucket": bucket})
    s3_client.write_json(object_key + ".out", output)
```

Refactor so the transformation is reusable with local data and storage is injected at the boundary.

#### Requirements

- Keep storage access out of the transformation function.
- Use a dataclass for the normalized result.
- Use a pure transformation function.
- Define a storage Protocol.
- Show how the application-level pipeline coordinates read/transform/write.

#### Expected Outcome

The pure transformation can be tested with a plain Python list, while S3 or another storage implementation can be substituted without changing the transformation.

#### Solution

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RiskRecord:
    record_id: str
    bucket: str


class ObjectStore(Protocol):
    def read_json(self, key: str) -> list[dict]:
        ...

    def write_json(self, key: str, value: list[RiskRecord]) -> None:
        ...


def transform_records(records: list[dict]) -> list[RiskRecord]:
    output = []
    for record in records:
        score = float(record["score"])
        bucket = "high" if score >= 0.8 else "low"
        output.append(RiskRecord(record["id"], bucket))
    return output


def process_object(key: str, store: ObjectStore) -> None:
    records = store.read_json(key)
    results = transform_records(records)
    store.write_json(key + ".out", results)
```

#### How to Solve It

1. Separate ingestion from transformation.
2. Treat `read_json()` and `write_json()` as effectful operations.
3. Represent the transformed result with a domain/data model.
4. Make `transform_records()` accept only the data it needs.
5. Inject the storage boundary into the orchestrator.

#### Why This Solution Works

The transformation no longer cares whether data came from S3, a database, or a local fixture. The storage adapter owns the external protocol. The dataclass gives the pipeline a clear internal representation. This improves testability and allows the same core transformation to be reused in batch jobs, local development, or another storage workflow.

#### Common Mistake(s)

- Creating an S3 client inside `transform_records()`.
- Returning storage-specific response objects from the pure function.
- Assuming changing storage is free: serialization formats, latency, retries, consistency, and operational semantics still belong to the boundary.

#### Key Learning

Data engineering pipelines become easier to test and evolve when ingestion/output are explicit effects and the transformation layer works on stable internal data.

### Question 23

#### Problem

An agent runtime has become a 500-line method that validates requests, builds prompts, calls an LLM, chooses tools, executes tools, writes memory, and logs every step. You do not need to implement the entire agent. Design a focused set of boundaries that separates decisions from effects.

#### Requirements

- Define contracts for model calls, tool execution, and memory persistence.
- Represent agent state with a dataclass.
- Keep routing/decision logic independent of the concrete tools.
- Show a small application orchestrator.
- Identify which steps are pure candidates and which are effectful.

#### Expected Outcome

The architecture has explicit dependency boundaries that permit deterministic tests of validation/routing/state transformations and isolated tests of effectful adapters.

#### Solution

```python
from dataclasses import dataclass, replace
from typing import Protocol


@dataclass(frozen=True)
class AgentState:
    user_text: str
    next_tool: str | None = None
    tool_result: str | None = None


class ModelPort(Protocol):
    def decide_tool(self, state: AgentState) -> str | None:
        ...


class ToolPort(Protocol):
    def execute(self, tool_name: str, state: AgentState) -> str:
        ...


class MemoryPort(Protocol):
    def save(self, state: AgentState) -> None:
        ...


def choose_tool(state: AgentState, available: set[str]) -> AgentState:
    # Deterministic policy example; real systems may use model output.
    if "weather" in state.user_text.lower() and "weather" in available:
        return replace(state, next_tool="weather")
    return replace(state, next_tool=None)


class AgentRuntime:
    def __init__(
        self,
        model: ModelPort,
        tools: ToolPort,
        memory: MemoryPort,
    ):
        self.model = model
        self.tools = tools
        self.memory = memory

    def run(self, state: AgentState, available_tools: set[str]) -> AgentState:
        routed = choose_tool(state, available_tools)
        if routed.next_tool is None:
            routed = replace(
                routed,
                next_tool=self.model.decide_tool(routed),
            )

        if routed.next_tool is not None:
            result = self.tools.execute(routed.next_tool, routed)
            routed = replace(routed, tool_result=result)

        self.memory.save(routed)
        return routed
```

#### How to Solve It

1. Inventory the responsibilities in the giant function.
2. Separate deterministic transformations and policies from external effects.
3. Model state explicitly instead of hiding it in many local variables or globals.
4. Define small ports for model, tools, and memory.
5. Keep the runtime as orchestration rather than embedding each vendor/tool implementation.
6. Place concrete adapters and configuration in the composition root.

#### Why This Solution Works

The architecture does not promise that every agent decision can be pure; model calls can be nondeterministic and are effects from the application's perspective. However, routing rules, validation, state transformations, prompt construction, and result normalization can often be separated. This gives the system testable seams without pretending the whole agent is deterministic.

#### Common Mistake(s)

- Calling every component a Protocol even when there is no replacement or test seam.
- Putting tool SDK code directly in `choose_tool()`.
- Treating agent state as global mutable state.
- Assuming an injected model is deterministic simply because it is behind a Protocol.

#### Key Learning

Agent architecture benefits from separating **decision**, **state transformation**, and **effect execution**. Boundaries should reflect real variation and failure modes.

### Question 24

#### Problem

A package contains:

```text
app/
    orders.py
    payments.py
    models.py
```

`orders.py` imports `PaymentService` from `payments.py`, while `payments.py` imports `Order` from `orders.py`. Refactor the dependency graph so both modules can use stable shared concepts without a circular import.

#### Requirements

- Keep the domain `Order` definition independent from payment infrastructure.
- Introduce a focused contract for payment behavior.
- Make the application service depend on the contract.
- Keep the concrete adapter in an infrastructure-oriented module.
- Explain the conceptual package dependency graph.

#### Expected Outcome

The desired graph is approximately:

```text
domain/models
      ↑
 application/checkout
      ↑
 infrastructure/payment
```

with the contract owned at the boundary needed by the application, rather than a cycle between concrete implementations.

#### Solution

```python
# app/domain.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_id: str
    amount: int
```

```python
# app/ports.py
from typing import Protocol
from app.domain import Order


class PaymentGateway(Protocol):
    def charge(self, order: Order) -> str:
        ...
```

```python
# app/application.py
from app.domain import Order
from app.ports import PaymentGateway


class CheckoutService:
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway

    def checkout(self, order: Order) -> str:
        return self.gateway.charge(order)
```

```python
# app/infrastructure.py
from app.domain import Order


class RemotePaymentGateway:
    def charge(self, order: Order) -> str:
        return f"charged:{order.order_id}"
```

```python
# main.py
from app.application import CheckoutService
from app.infrastructure import RemotePaymentGateway


service = CheckoutService(RemotePaymentGateway())
```

#### How to Solve It

1. Identify the cycle: concrete order code and concrete payment code both depend directly on each other.
2. Move the domain data concept to a stable domain module.
3. Define the payment capability at the dependency boundary.
4. Make application code depend on the capability rather than the concrete adapter.
5. Assemble the real adapter at the entry point.

#### Why This Solution Works

The architecture uses package boundaries to reinforce conceptual boundaries. The exact package names are not mandatory; the important property is the dependency direction. The application can reason about the capability it needs without importing vendor or infrastructure implementation details.

#### Common Mistake(s)

- Creating a giant `common.py` that becomes another coupling hub.
- Hiding the cycle with function-local imports while retaining the same conceptual dependency.
- Moving all classes into one module and calling the result "layered architecture."

#### Key Learning

A package boundary is useful only when it represents a real responsibility boundary. Architecture is expressed by dependency relationships, not folder names alone.

# Part 4 — Advanced Questions

### Question 25

#### Problem

Design a production-oriented bank transfer component using the concepts from the module. The use case must validate and calculate a transfer without depending on PostgreSQL, while the outer application must coordinate persistence and notification.

You are given these requirements:

```text
Client request
    ↓
Presentation
    ↓
Transfer use case
    ↓
Domain rules
    ↓
Repository + transaction boundary
    ↓
Event/notification boundary
```

#### Requirements

- Define `Money` and `Account` as appropriate dataclasses.
- Protect a basic transfer invariant: amount must be positive and the source must have sufficient funds.
- Use a pure function for the state transition.
- Use a repository Protocol.
- Use a notification Protocol.
- Show a Unit of Work concept or a clear transaction boundary.
- Inject dependencies at the composition root.
- Explain where DTO mapping and error translation belong.

#### Expected Outcome

The domain rule is independently testable, infrastructure is replaceable, and the dependency flow is explicit.

#### Solution

```python
from dataclasses import dataclass, replace
from typing import Protocol


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("money amount cannot be negative")


@dataclass(frozen=True)
class Account:
    account_id: str
    balance: Money


class AccountRepository(Protocol):
    def get(self, account_id: str) -> Account:
        ...

    def save(self, account: Account) -> None:
        ...


class UnitOfWork(Protocol):
    accounts: AccountRepository

    def commit(self) -> None:
        ...


class TransferNotifier(Protocol):
    def publish(self, source_id: str, destination_id: str, amount: Money) -> None:
        ...


def transfer_state(
    source: Account,
    destination: Account,
    amount: Money,
) -> tuple[Account, Account]:
    if amount.amount <= 0:
        raise ValueError("transfer amount must be positive")
    if source.balance.currency != amount.currency:
        raise ValueError("source currency mismatch")
    if destination.balance.currency != amount.currency:
        raise ValueError("destination currency mismatch")
    if source.balance.amount < amount.amount:
        raise ValueError("insufficient funds")

    return (
        replace(
            source,
            balance=Money(source.balance.amount - amount.amount, amount.currency),
        ),
        replace(
            destination,
            balance=Money(destination.balance.amount + amount.amount, amount.currency),
        ),
    )


class TransferMoney:
    def __init__(self, unit_of_work: UnitOfWork, notifier: TransferNotifier):
        self.unit_of_work = unit_of_work
        self.notifier = notifier

    def execute(self, source_id: str, destination_id: str, amount: Money) -> None:
        source = self.unit_of_work.accounts.get(source_id)
        destination = self.unit_of_work.accounts.get(destination_id)
        updated_source, updated_destination = transfer_state(
            source,
            destination,
            amount,
        )
        self.unit_of_work.accounts.save(updated_source)
        self.unit_of_work.accounts.save(updated_destination)
        self.unit_of_work.commit()
        self.notifier.publish(source_id, destination_id, amount)
```

The presentation adapter should translate a request DTO into `Money` and identifiers. A concrete database Unit of Work is assembled by the composition root. A production design should also address concurrency, idempotency, audit requirements, and the fact that `commit()` and external notification are not automatically one atomic distributed operation. An outbox-style design can address reliable event publication when that reliability is required.

#### How to Solve It

1. Start from the business rule rather than from the database technology.
2. Decide which state must cross the domain boundary.
3. Make the state transition a pure function.
4. Identify external capabilities and define small ports.
5. Put transaction ownership in the application/infrastructure side.
6. Assemble concrete adapters at the composition root.
7. Keep request serialization and infrastructure exceptions out of the domain model.

#### Why This Solution Works

This design combines encapsulation, dataclasses/value objects, pure functions, Protocols, dependency injection, dependency inversion, and layered/ports-and-adapters thinking. The domain is protected from PostgreSQL and notification-provider details. The application service coordinates the use case, while infrastructure controls the transaction implementation.

The important production property is not the exact number of classes. It is clear ownership: the domain owns business rules, the application owns use-case orchestration, and infrastructure owns concrete external mechanisms.

#### Common Mistake(s)

- Putting `commit()` inside `transfer_state()`.
- Treating a database transaction as an atomic guarantee across a separate message broker or notification API.
- Creating a Protocol for every tiny helper.
- Putting request parsing and JSON serialization directly in the domain model.

#### Key Learning

Architecture becomes useful when it makes ownership and failure boundaries explicit. A production transfer service is more than classes and folders; it is a set of intentional dependency and transaction decisions.

### Question 26

#### Problem

Your LLM application currently imports one vendor SDK directly into the application service. Product requirements now include local-model tests and the possibility of replacing the model provider later.

#### Requirements

Design an LLM boundary with:

- a request dataclass,
- pure prompt construction,
- a model Protocol,
- two implementations: a fake and a provider adapter,
- application orchestration,
- provider-specific code isolated from the domain/application logic,
- a composition-root example.

#### Expected Outcome

The application service can be tested without network access and the provider can be replaced without changing prompt/domain logic.

#### Solution

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ClassificationRequest:
    document: str


@dataclass(frozen=True)
class ClassificationResult:
    label: str


class ModelPort(Protocol):
    def generate(self, prompt: str) -> str:
        ...


def build_prompt(request: ClassificationRequest) -> str:
    return (
        "Classify the document as invoice, contract, or other.\n"
        f"Document:\n{request.document}"
    )


def parse_model_output(text: str) -> ClassificationResult:
    label = text.strip().lower()
    if label not in {"invoice", "contract", "other"}:
        raise ValueError("unsupported classification")
    return ClassificationResult(label)


class DocumentClassifier:
    def __init__(self, model: ModelPort):
        self.model = model

    def classify(self, request: ClassificationRequest) -> ClassificationResult:
        prompt = build_prompt(request)
        raw = self.model.generate(prompt)
        return parse_model_output(raw)


class FakeModel:
    def generate(self, prompt: str) -> str:
        return "invoice"


class ProviderModel:
    def __init__(self, client):
        self.client = client

    def generate(self, prompt: str) -> str:
        # The vendor SDK call belongs inside this adapter.
        return self.client.generate(prompt)


# Composition root:
# classifier = DocumentClassifier(ProviderModel(real_client))
# Unit test:
classifier = DocumentClassifier(FakeModel())
print(classifier.classify(ClassificationRequest("April invoice")))
```

Output:

```text
ClassificationResult(label='invoice')
```

#### How to Solve It

1. Identify the application-level capability: generating text for a prompt.
2. Define that capability in `ModelPort`.
3. Keep prompt construction and result parsing as ordinary Python logic.
4. Put vendor-specific SDK details in an adapter.
5. Inject the model into the application service.
6. Use a fake for deterministic unit tests and a real adapter only in integration paths.

#### Why This Solution Works

The provider is treated as an implementation detail of an outbound boundary. Prompt and parsing logic therefore remain reusable across providers. The Protocol documents the minimal interaction the application requires. This is dependency inversion in practical Python form; dependency injection is the mechanism used to supply the implementation.

A real production adapter would also own timeout handling, retry policy appropriate to the provider, error translation, request metadata, and observability. Those concerns should not leak into `build_prompt()` or the domain classifier rules.

#### Common Mistake(s)

- Defining a Protocol that exposes the entire vendor SDK surface.
- Making prompt construction depend on the provider client.
- Treating a fake provider as validation that the external provider works.
- Hiding all provider differences behind an abstraction even when the differences are essential to application behavior.

#### Key Learning

A useful provider boundary hides accidental vendor coupling while keeping meaningful provider-specific behavior visible where it matters.

### Question 27

#### Problem

A data engineering team receives data from three sources: an HTTP API, a local JSON file for backfills, and an object store. The transformation logic is currently tied to one source SDK and mutates records in place.

Design a boundary-oriented pipeline that allows all three sources to feed the same pure transformation core.

#### Requirements

- Define a source Protocol that provides records.
- Represent normalized records using a dataclass.
- Keep normalization and validation pure.
- Demonstrate a simple functional pipeline.
- Keep storage/source adapters outside the transformation core.
- Explain where output storage belongs.

#### Expected Outcome

The same transformation function accepts records regardless of their source, and source changes do not require rewriting the business transformation.

#### Solution

```python
from dataclasses import dataclass
from typing import Protocol, Iterable


@dataclass(frozen=True)
class RawRecord:
    record_id: str
    amount: str


@dataclass(frozen=True)
class CleanRecord:
    record_id: str
    amount: int


class Source(Protocol):
    def read(self) -> Iterable[RawRecord]:
        ...


class ApiSource:
    def __init__(self, client):
        self.client = client

    def read(self) -> Iterable[RawRecord]:
        return self.client.fetch_records()


class FileSource:
    def __init__(self, path: str):
        self.path = path

    def read(self) -> Iterable[RawRecord]:
        # File I/O belongs at the effect boundary.
        import json

        with open(self.path, "r", encoding="utf-8") as handle:
            rows = json.load(handle)
        return [RawRecord(row["id"], row["amount"]) for row in rows]


def normalize(record: RawRecord) -> CleanRecord:
    amount = int(record.amount)
    if amount < 0:
        raise ValueError("amount cannot be negative")
    return CleanRecord(record.record_id, amount)


def transform(records: Iterable[RawRecord]) -> list[CleanRecord]:
    return [normalize(record) for record in records]


def process(source: Source) -> list[CleanRecord]:
    records = source.read()
    return transform(records)
```

#### How to Solve It

1. Identify the volatile part: how records are acquired.
2. Define the stable data needed by the transformation core.
3. Convert source-specific responses into `RawRecord` at the boundary.
4. Keep `normalize()` deterministic and free of I/O.
5. Put source construction and output storage in the outer pipeline/application layer.

#### Why This Solution Works

The source is an adapter behind a small contract. The pure core operates on dataclasses instead of SDK-specific objects. That makes local backfills, production ingestion, and unit tests share the same transformation rules.

The example returns a list for simplicity. A high-volume pipeline could instead use iterators/generators to control memory usage. That is a performance choice, not an architectural requirement.

#### Common Mistake(s)

- Passing vendor response objects directly into domain transformations.
- Embedding S3 or HTTP calls in `normalize()`.
- Assuming `frozen=True` on the dataclass alone guarantees the source data was validated correctly.
- Introducing a repository abstraction for every intermediate list.

#### Key Learning

Separate source acquisition from data meaning. Data engineering boundaries should make source technology replaceable while keeping transformation semantics stable.

### Question 28

#### Problem

A pricing engine uses a deep inheritance hierarchy:

```text
PricingRule
├── CustomerPricingRule
│   └── PremiumCustomerPricingRule
└── RegionPricingRule
```

The new requirement says a premium customer may also receive a regional adjustment and a promotional discount. Adding more subclasses would create combinations such as `PremiumRegionalPromotionRule`.

Refactor the design so pricing behavior can be combined without creating a subclass for every combination.

#### Requirements

- Demonstrate composition instead of combinatorial inheritance.
- Keep each pricing rule small and focused.
- Use a common callable behavior where appropriate.
- Make the composed calculation easy to test.
- Explain when inheritance would still be reasonable.

#### Expected Outcome

Multiple pricing policies can be composed in a single calculator without creating a new subclass for each combination.

#### Solution

```python
from typing import Callable


PriceRule = Callable[[float], float]


def premium_discount(price: float) -> float:
    return price * 0.90


def regional_discount(price: float) -> float:
    return price * 0.95


def promotional_discount(price: float) -> float:
    return price * 0.80


def compose_price_rules(*rules: PriceRule) -> PriceRule:
    def apply(price: float) -> float:
        for rule in rules:
            price = rule(price)
        return price

    return apply


premium_regional = compose_price_rules(
    premium_discount,
    regional_discount,
)

print(premium_regional(100.0))
print(compose_price_rules(
    premium_discount,
    regional_discount,
    promotional_discount,
)(100.0))
```

Output:

```text
85.5
81.2
```

#### How to Solve It

1. Look for independent dimensions of variation rather than asking which subclass a customer belongs to.
2. Model each pricing behavior as a small strategy function.
3. Compose strategies sequentially.
4. Test each strategy separately and the composition as a workflow.
5. Keep an inheritance hierarchy only for genuine specialization with a stable parent contract.

#### Why This Solution Works

Composition avoids subclass explosion. A new discount can be combined with existing rules without adding another class for every possible combination. The functions are also pure, which makes their order and effect easier to test.

The example does not prove composition is always superior. A domain with a true subtype hierarchy and shared lifecycle/state could benefit from inheritance. The important design question is whether the varying behavior is independent and combinable.

#### Common Mistake(s)

- Building a class hierarchy for every combination of rules.
- Assuming functional composition is always clearer than objects.
- Forgetting that rule order is part of the behavior.

#### Key Learning

Composition is especially powerful when multiple independent policies need to vary and combine. It can model behavior without encoding every combination in the type hierarchy.

### Question 29

#### Problem

A production service has a pure domain calculator, a PostgreSQL repository, an HTTP payment adapter, and a web controller. Design a testing strategy that catches domain regressions, adapter integration problems, and end-to-end wiring failures without turning every unit test into a large mock-based test.

#### Requirements

Describe and show representative tests for:

- pure domain unit tests,
- repository integration tests,
- payment contract/integration tests,
- application-service tests with a fake,
- one end-to-end workflow.

Also explain what each level does and does not prove.

#### Expected Outcome

The test suite is layered around architectural boundaries rather than relying on one test type for everything.

#### Solution

A pure domain rule can be tested directly:

```python
def calculate_discount(total: int) -> int:
    return 100 if total >= 1000 else 0


def test_calculate_discount_boundary() -> None:
    assert calculate_discount(999) == 0
    assert calculate_discount(1000) == 100
```

An application service can use fakes:

```python
class FakeOrderRepository:
    def __init__(self):
        self.orders = {"o-1": {"total": 1200}}
        self.saved = []

    def get(self, order_id):
        return self.orders[order_id]

    def save(self, order_id, value):
        self.saved.append((order_id, value))


class FakePaymentGateway:
    def __init__(self):
        self.charges = []

    def charge(self, amount):
        self.charges.append(amount)
        return "ok"


def process_order(order_id, repository, gateway):
    order = repository.get(order_id)
    discount = calculate_discount(order["total"])
    amount = order["total"] - discount
    gateway.charge(amount)
    repository.save(order_id, amount)
    return amount
```

An integration test should exercise the real repository against a controlled test database. A payment adapter integration/contract test should verify the adapter's assumptions about the provider. An end-to-end test should exercise the real application wiring for a small number of critical workflows.

#### How to Solve It

1. Start with the purest code and test it directly.
2. Use fakes at application boundaries where deterministic orchestration behavior is the target.
3. Exercise real infrastructure separately where correctness of the adapter matters.
4. Use contract tests when an external interface has assumptions worth verifying.
5. Reserve end-to-end tests for critical workflows because they validate more of the system but are usually more expensive and diagnostic information is less local.

#### Why This Solution Works

Dependency boundaries create natural test seams. Pure domain tests are fast and focused. Fakes validate orchestration behavior without requiring live infrastructure. Integration tests prove that concrete adapters actually communicate with their dependencies. End-to-end tests prove that the assembled system works across boundaries.

No level substitutes completely for another. An in-memory fake can demonstrate repository behavior expected by the application, but it does not prove PostgreSQL queries, transactions, indexes, or connection handling work correctly.

#### Common Mistake(s)

- Mocking every internal object until the test only verifies implementation details.
- Treating unit tests as proof that external APIs work.
- Using only end-to-end tests and then debugging failures from the entire stack.
- Assuming a Protocol guarantees that a concrete adapter behaves correctly.

#### Key Learning

Test boundaries according to what they can realistically prove. Architecture and testing should reinforce each other rather than forcing one test style onto every layer.

### Question 30

#### Problem

A small internal CRUD tool has been designed with 20 layers:

```text
Controller
RequestMapper
ApplicationFacade
UseCaseFactory
DomainService
RepositoryPort
RepositoryFactory
InfrastructureRepository
TransactionManager
UnitOfWork
EventPort
EventPublisher
MetricsFacade
LoggingFacade
DTOMapper
ResponseMapper
Serializer
ConfigurationProvider
DependencyContainer
Bootstrapper
```

The team argues that this is better architecture because it is "more enterprise." Evaluate the design and propose a proportional alternative.

#### Requirements

- Do not simply call the design bad.
- Identify which boundaries might be justified by actual variation or risk.
- Propose a simpler structure for a small tool.
- State conditions under which additional boundaries might become worthwhile.
- Explain the cost of indirection.

#### Expected Outcome

The recommendation is based on system complexity, change frequency, testing needs, team context, and operational risk—not on the number of layers.

#### Solution

A reasonable starting point for a small internal tool might be:

```text
feature/
    models.py
    service.py
    repository.py
    api.py
main.py
```

The service can depend on a concrete repository initially if there is no meaningful replacement point. A Protocol can be introduced later when an actual testing, replacement, or architectural boundary justifies it.

For example:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    item_id: str
    name: str


class ItemRepository:
    def get(self, item_id: str) -> Item:
        # Simple application-specific implementation.
        return Item(item_id, "example")


class ItemService:
    def __init__(self, repository: ItemRepository):
        self.repository = repository

    def get_item(self, item_id: str) -> Item:
        return self.repository.get(item_id)
```

#### How to Solve It

1. Determine the system's real complexity and production risk.
2. Identify actual variation points: database replacement, multiple interfaces, distributed transactions, independent teams, or strong test seams.
3. Keep boundaries that reduce meaningful coupling.
4. Remove layers that only forward calls without adding policy, translation, ownership, or protection.
5. Reassess the architecture as the system grows.

#### Why This Solution Works

Architecture has a cognitive and maintenance cost. A layer is valuable when it isolates a meaningful responsibility or change boundary. A forwarding layer that adds no policy or isolation can increase navigation cost without reducing coupling.

This is architectural proportionality. A simple system can still use good boundaries, but those boundaries should be justified by real requirements rather than by a belief that more indirection is inherently more professional.

#### Common Mistake(s)

- Treating architecture diagrams or folder counts as quality metrics.
- Removing all abstractions simply because the application is small.
- Assuming a current one-implementation dependency can never become a future boundary.
- Adding an abstraction because a pattern name sounds senior.

#### Key Learning

Good architecture is proportional. Use the simplest design that keeps responsibilities, dependencies, and failure modes understandable as the system's complexity requires.

### Question 31

#### Problem

The following service has several architectural problems:

```python
# order_service.py
import os
from datetime import datetime
from database import Database
from payment import PaymentClient
from models import Order


def calculate_total(order: Order) -> float:
    tax = float(os.getenv("TAX_RATE", "0.18"))
    if datetime.now().hour >= 18:
        tax += 0.02
    return order.subtotal * (1 + tax)


class OrderService:
    def checkout(self, order_id: str) -> float:
        db = Database()
        payment = PaymentClient()
        order = db.get_order(order_id)
        total = calculate_total(order)
        payment.charge(total)
        db.save_total(order_id, total)
        return total
```

A test fails at different times of day, another test cannot control `TAX_RATE`, and unit tests unexpectedly create real clients. Diagnose the architecture and refactor the critical path.

#### Requirements

Identify and fix at least these issues:

- hidden environment dependency,
- hidden current-time dependency,
- concrete dependencies created internally,
- domain logic coupled to infrastructure/configuration,
- difficulty testing the calculation independently.

Use a configuration object and injected dependencies where appropriate.

#### Expected Outcome

The calculation can be tested with explicit `tax_rate` and `hour` inputs, and `OrderService` can be tested with injected fakes without constructing real infrastructure.

#### Solution

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Order:
    order_id: str
    subtotal: float


@dataclass(frozen=True)
class PricingConfig:
    tax_rate: float
    evening_surcharge: float


def calculate_total(
    order: Order,
    config: PricingConfig,
    hour: int,
) -> float:
    tax = config.tax_rate
    if hour >= 18:
        tax += config.evening_surcharge
    return order.subtotal * (1 + tax)


class OrderRepository(Protocol):
    def get_order(self, order_id: str) -> Order:
        ...

    def save_total(self, order_id: str, total: float) -> None:
        ...


class PaymentPort(Protocol):
    def charge(self, amount: float) -> None:
        ...


class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
        payment: PaymentPort,
        config: PricingConfig,
        clock,
    ):
        self.repository = repository
        self.payment = payment
        self.config = config
        self.clock = clock

    def checkout(self, order_id: str) -> float:
        order = self.repository.get_order(order_id)
        total = calculate_total(order, self.config, self.clock.hour())
        self.payment.charge(total)
        self.repository.save_total(order_id, total)
        return total
```

A minimal clock dependency can be an object with `hour()` for tests and production. Environment loading happens once when constructing `PricingConfig` in the composition root.

#### How to Solve It

1. List every hidden input and external effect.
2. Turn configuration and current time into explicit dependencies.
3. Extract the deterministic calculation.
4. Inject repository and payment dependencies instead of constructing them internally.
5. Assemble production implementations outside the service.

#### Why This Solution Works

The original calculation looked like a function of `order` but actually depended on environment and wall-clock time. The refactored function exposes those inputs, restoring deterministic testability. The application service remains responsible for orchestration and effects.

The design also improves change isolation: a new configuration source or clock implementation can be changed without rewriting the pricing rule.

#### Common Mistake(s)

- Reading `os.getenv()` inside `calculate_total()` because it is "just configuration."
- Monkey-patching `datetime.now()` globally instead of making the relevant time input explicit.
- Injecting dependencies but still creating real clients as fallback values inside the service.

#### Key Learning

Debugging architectural bugs often starts by finding hidden inputs. Time, configuration, and external clients are dependencies even when they do not appear in a function's parameter list.

### Question 32

#### Problem

You are designing a production-oriented agentic AI service that processes support requests. The agent may retrieve knowledge, call tools, ask an LLM to plan, update conversation state, and persist the final outcome.

The first design is a single function with direct SDK calls for the model, vector database, tools, logging, and storage.

Design a boundary-aware architecture that keeps policy and transformation logic as independent as practical while acknowledging that model calls and tool calls are effects.

#### Requirements

Your design must include:

- request and state dataclasses,
- an LLM/model Protocol,
- a retrieval Protocol,
- a tool Protocol,
- a memory/state-store Protocol,
- pure validation/routing/transformation functions where practical,
- an application-level orchestrator,
- explicit observability boundaries,
- retry and idempotency considerations for effectful operations,
- a testing strategy,
- a composition-root example,
- a dependency diagram.

#### Expected Outcome

The agent can be tested without invoking real external services, model providers can be replaced, and state/effect boundaries are visible enough to reason about failures and retries.

#### Solution

```python
from dataclasses import dataclass, replace
from typing import Protocol


@dataclass(frozen=True)
class AgentRequest:
    request_id: str
    text: str


@dataclass(frozen=True)
class AgentState:
    request: AgentRequest
    context: tuple[str, ...] = ()
    selected_tool: str | None = None
    result: str | None = None


class ModelPort(Protocol):
    def plan(self, text: str, context: tuple[str, ...]) -> str | None:
        ...


class RetrievalPort(Protocol):
    def search(self, query: str) -> list[str]:
        ...


class ToolPort(Protocol):
    def execute(self, name: str, request_id: str, text: str) -> str:
        ...


class StateStore(Protocol):
    def save(self, state: AgentState) -> None:
        ...


def validate_request(request: AgentRequest) -> AgentRequest:
    if not request.text.strip():
        raise ValueError("request text cannot be empty")
    return request


def select_deterministic_tool(
    request: AgentRequest,
    available_tools: set[str],
) -> str | None:
    text = request.text.lower()
    if "refund" in text and "refund" in available_tools:
        return "refund"
    return None


def with_context(
    state: AgentState,
    context: list[str],
) -> AgentState:
    return replace(state, context=tuple(context))


class SupportAgent:
    def __init__(
        self,
        model: ModelPort,
        retrieval: RetrievalPort,
        tools: ToolPort,
        state_store: StateStore,
    ):
        self.model = model
        self.retrieval = retrieval
        self.tools = tools
        self.state_store = state_store

    def run(self, request: AgentRequest, available_tools: set[str]) -> AgentState:
        request = validate_request(request)
        state = AgentState(request=request)

        context = self.retrieval.search(request.text)
        state = with_context(state, context)

        tool_name = select_deterministic_tool(request, available_tools)
        if tool_name is None:
            tool_name = self.model.plan(request.text, state.context)
        state = replace(state, selected_tool=tool_name)

        if tool_name is not None:
            result = self.tools.execute(
                tool_name,
                request.request_id,
                request.text,
            )
            state = replace(state, result=result)

        self.state_store.save(state)
        return state
```

A conceptual dependency graph is:

```text
                    CLIENT
                       |
                       v
                +--------------+
                | Presentation |
                +------+-------+
                       |
                       v
                +--------------+
                | Application   |
                | Agent Runtime  |
                +------+-------+
                       |
          +------------+-------------+
          |            |             |
          v            v             v
       Model        Retrieval       Tool
       Port           Port          Port
          ^            ^             ^
          |            |             |
       adapter      adapter       adapter
          |            |             |
       LLM API      Vector DB    External API
                       
                       +----> State Store
```

Logging, metrics, and tracing should generally be added at application/effect boundaries where useful. Retries belong around operations whose failure semantics support retrying; a tool that charges money cannot be treated the same way as a read-only retrieval call. Idempotency keys or request identifiers should be carried through operations that must not create duplicate effects.

#### How to Solve It

1. Start by separating the agent's conceptual responsibilities.
2. Identify external effects: model calls, retrieval, tool execution, and persistence.
3. Define minimal contracts for those capabilities.
4. Make request/state transformations explicit through dataclasses and pure helper functions where practical.
5. Keep orchestration in the application layer.
6. Put concrete adapters and configuration in the composition root.
7. Decide retry and idempotency rules per effect rather than applying one global retry policy.
8. Test pure policies directly, orchestration with fakes, adapters with integration/contract tests, and critical paths end-to-end.

#### Why This Solution Works

Agentic systems contain inherently effectful and often nondeterministic operations. Trying to make the entire agent pure would be unrealistic. Instead, the architecture isolates deterministic decisions and transformations from effects. This improves testability and makes failures easier to localize.

The Protocols create replaceable boundaries for model, retrieval, tool, and memory implementations. Dataclasses make state transitions explicit. The request ID provides a natural starting point for idempotency and observability correlation, although a real production system may require stronger distributed consistency mechanisms.

The architecture also respects the distinction between dependency inversion and dependency injection: the high-level agent policy depends on stable capabilities, while concrete implementations are supplied at the composition root.

#### Common Mistake(s)

- Putting vendor SDK objects directly into `AgentState` and then passing them across all layers.
- Treating the LLM as a pure deterministic function in every environment.
- Retrying every tool call automatically.
- Making the `ToolPort` include unrelated methods for all possible tools.
- Assuming a Protocol proves tool safety or business correctness.
- Adding a new abstraction layer for observability on every function instead of instrumenting meaningful boundaries.

#### Key Learning

A production AI architecture should separate **policy and transformation** from **effect execution** as far as practical. The goal is not zero effects; it is explicit, testable, replaceable, and observable boundaries around them.

# Coverage Summary

| Source File | Major Concepts Practiced | Question Numbers |
|---|---|---|
| `01-encapsulation-abstraction-and-composition.md` | Encapsulation, properties, invariants, composition, delegation, composition root, information hiding, composition vs inheritance | Q1, Q9, Q17, Q21, Q28, Q32 |
| `02-inheritance-and-polymorphism.md` | Inheritance, overriding, `super()`, MRO, cooperative mixins, polymorphism, duck typing, substitutability, inheritance vs composition | Q4, Q9, Q11, Q18, Q28 |
| `03-dataclasses-and-data-models.md` | Dataclasses, frozen models, default/data ownership, DTOs, domain models, value objects, serialization boundaries | Q3, Q10, Q15, Q17, Q21, Q22, Q25, Q26, Q27, Q32 |
| `04-class-and-instance-attributes.md` | Instance/class state, mutable class attributes, attribute ownership, shared state, object identity, concurrency implications | Q2, Q11, Q19, Q28, Q31 |
| `05-protocols-interfaces-and-dependency-inversion.md` | Protocols, structural typing, ABC comparison, dependency inversion, dependency injection, test doubles, ports, adapters, provider boundaries | Q5, Q8, Q12, Q16, Q17, Q18, Q21, Q22, Q23, Q24, Q25, Q26, Q27, Q29, Q32 |
| `06-pure-functions-immutability-and-higher-order-functions.md` | Pure functions, side effects, determinism, immutability, higher-order functions, composition, `map`/`filter`, functional pipelines, callable behavior | Q6, Q10, Q13, Q14, Q17, Q20, Q22, Q28, Q31, Q32 |
| `07-separating-side-effects-from-domain-logic.md` | Domain/application logic, functional core/imperative shell, dependency boundaries, repositories, ports/adapters, time/randomness/configuration, transactions, errors, retries, idempotency, testing, AI boundaries | Q7, Q12, Q14, Q17, Q20, Q21, Q22, Q23, Q25, Q26, Q27, Q29, Q31, Q32 |
| `08-dependency-boundaries-and-layered-design.md` | Dependency direction, coupling/cohesion, layers, repositories, Unit of Work, composition root, DTO mapping, package boundaries, circular dependencies, feature organization, async/distributed boundaries, production architecture | Q8, Q14, Q16, Q17, Q21, Q22, Q23, Q24, Q25, Q26, Q27, Q29, Q30, Q31, Q32 |

## Difficulty and Skill Distribution

| Difficulty | Questions | Primary emphasis |
|---|---|---|
| Basic | Q1–Q8 | Foundational implementation, state ownership, basic contracts, purity, obvious boundaries |
| Moderate | Q9–Q16 | Multi-concept implementation, refactoring, Protocol + DI, datamodel boundaries, package cycles |
| Hard | Q17–Q24 | Realistic refactoring, polymorphism, state/concurrency reasoning, repositories, AI/data architecture |
| Advanced | Q25–Q32 | Production architecture, trade-offs, layered systems, testing strategy, provider boundaries, agentic AI |

The set contains substantially more than the minimum number of cross-topic problems. Questions Q17, Q21, Q22, Q23, Q25, Q26, Q27, Q29, and Q32 integrate concepts from at least four source files, with several also requiring production-level reasoning.

# Final Module 08 Review

Use this checklist after completing the 32 questions:

- Can you protect object invariants with encapsulation without confusing it with security?
- Can you decide when state belongs to a class versus an instance?
- Can you diagnose mutable class attributes and shared-state bugs?
- Can you decide whether inheritance represents a true subtype relationship?
- Can you explain how `super()` and the MRO affect cooperative inheritance?
- Can you replace unnecessary inheritance with composition when behavior needs to vary independently?
- Can you choose a dataclass, frozen dataclass, ordinary class, or simpler structure based on the model's needs?
- Can you distinguish a DTO from a domain model and map between them at a boundary?
- Can you define a small Protocol around a capability instead of a concrete implementation?
- Can you distinguish Dependency Injection from the Dependency Inversion Principle?
- Can you identify pure domain logic and move external effects into an explicit shell?
- Can you reason about mutation, immutability, and deterministic behavior?
- Can you use higher-order functions and functional pipelines when they improve clarity?
- Can you identify hidden dependencies on time, randomness, configuration, and environment?
- Can you identify domain, application, infrastructure, and presentation responsibilities?
- Can you explain ports, adapters, repositories, and composition roots without treating them as mandatory patterns?
- Can you reason about transaction ownership, retries, and idempotency without assuming external operations are automatically atomic?
- Can you choose unit, integration, contract, and end-to-end tests according to what each level actually proves?
- Can you diagnose circular dependency problems by examining the architecture rather than only moving import statements?
- Can you evaluate whether a proposed architecture is proportional to the system's complexity?
- Can you apply these principles to backend services, data pipelines, ML systems, LLM applications, and agentic AI?

The central Module 08 mental model is:

```text
Objects and data models
        ↓
Clear ownership of state
        ↓
Encapsulation + appropriate abstraction
        ↓
Composition and controlled polymorphism
        ↓
Explicit dependencies
        ↓
Pure logic where practical
        ↓
Dependency boundaries
        ↓
Ports / Protocols / adapters where justified
        ↓
Layered or feature-oriented organization
        ↓
Testable application services
        ↓
Explicit transaction / error / retry / observability boundaries
        ↓
Production architecture matched to actual complexity
```

The objective is not to memorize architecture patterns. It is to learn how to recognize responsibility, state ownership, dependency direction, and change boundaries so that a Python system can grow without accumulating accidental coupling.
