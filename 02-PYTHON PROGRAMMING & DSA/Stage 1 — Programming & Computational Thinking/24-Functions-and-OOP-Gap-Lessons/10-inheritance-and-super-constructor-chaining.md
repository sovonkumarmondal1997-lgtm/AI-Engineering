# Inheritance and `super()` Constructor Chaining

> **Target:** Python 3.12+ · **Level:** beginner to advanced practical use · **Focus:** single inheritance, constructor chaining, overriding, substitutability, and design choice.

## Learning objectives

By the end of this lesson, you should be able to:

- Explain what a subclass inherits and distinguish inheritance from object composition.
- Override a method without silently breaking the parent's behavioral contract.
- Implement a subclass constructor that preserves parent invariants by calling `super().__init__(...)` with the right arguments.
- Explain why `super()` means “continue lookup after this class in the method resolution order (MRO),” not simply “call my parent.”
- Use `isinstance`, `issubclass`, `type`, and `ClassName.mro()` appropriately.
- Recognize basic Liskov Substitution Principle (LSP) violations and test a family of implementations against a shared contract.
- Decide when a strategy, delegate, function, or registry is simpler than another subclass.

## Prerequisites and scope boundaries

You should know classes, instances, `self`, `__init__`, methods, type annotations, exceptions, and pytest basics. Lesson 08 introduces classes and objects; Lesson 09 explains construction through `__new__` and `__init__`. This lesson uses those foundations without repeating the full object-construction protocol.

The roadmap places C3 linearization, deep MRO mechanics, cooperative multiple inheritance, and mixin pitfalls in **Stage 1 Module 1.11, lessons 08–09**. Here, MRO is introduced only enough to use `super()` correctly. Dataclass inheritance details belong to the dedicated dataclass lesson. Class-design review and refactoring are consolidated in Lesson 11.

---

## 1. Inheritance fundamentals

Inheritance declares that a class specializes another class:

```python
class Account:
    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner
        self.balance = balance

    def describe(self) -> str:
        return f"{self.owner}: {self.balance:.2f}"


class SavingsAccount(Account):
    def __init__(
        self,
        owner: str,
        balance: float = 0.0,
        rate: float = 0.02,
    ) -> None:
        super().__init__(owner, balance)
        self.rate = rate

    def describe(self) -> str:
        return f"{super().describe()} (rate {self.rate:.1%})"


account = SavingsAccount("Ana", 100.0)
print(account.describe())
print(isinstance(account, SavingsAccount))
print(isinstance(account, Account))
print(issubclass(SavingsAccount, Account))
print(type(account) is SavingsAccount)
```

Expected output:

```text
Ana: 100.00 (rate 2.0%)
True
True
True
True
```

- `class SavingsAccount(Account):` declares the subclass relationship.
- `SavingsAccount` inherits `Account`'s methods unless it overrides them.
- `super().__init__(owner, balance)` initializes the base portion of the object.
- `describe` extends the inherited description rather than duplicating its formatting.
- `isinstance` answers whether the object is an instance of the requested class **or a subclass**. `type(account) is SavingsAccount` tests exact type and is less flexible; use exact-type checks only when exact type is part of the requirement.

The “is-a” question is necessary but not sufficient. A `SavingsAccount` should also be usable wherever an `Account` is expected without surprising callers or violating the parent's promises.

### Inherited attributes and methods

An instance of `SavingsAccount` can access `owner`, `balance`, and `describe` because its construction initializes those attributes and its class inherits that method. In general, attribute lookup considers the instance and class hierarchy according to Python's lookup rules. A subclass attribute can shadow an inherited class attribute; an override can replace an inherited method for instances of that subclass.

Avoid mutable class attributes for per-instance state:

```python
class BadBatch:
    records: list[str] = []  # shared by every instance that uses this list


first = BadBatch()
second = BadBatch()
first.records.append("row-1")
print(second.records)  # ['row-1']
```

Correct per-instance state belongs in the initializer:

```python
class Batch:
    def __init__(self) -> None:
        self.records: list[str] = []
```

Class attributes are appropriate for shared constants and metadata, not usually for mutable instance data.

---

## 2. Method overriding and polymorphism

A subclass overrides a method by defining an attribute with the same name. The new implementation should preserve the documented contract: accepted inputs, return meaning, relevant side effects, and failure behavior.

```python
class Notifier:
    def send(self, recipient: str, message: str) -> str:
        """Send a message and return a delivery reference."""
        return f"queued:{recipient}:{message}"


class AuditNotifier(Notifier):
    def send(self, recipient: str, message: str) -> str:
        reference = super().send(recipient, message)
        return f"audited:{reference}"


notifiers: list[Notifier] = [Notifier(), AuditNotifier()]
for notifier in notifiers:
    print(notifier.send("ops@example.test", "pipeline complete"))
```

Expected output:

```text
queued:ops@example.test:pipeline complete
audited:queued:ops@example.test:pipeline complete
```

This is polymorphism: the caller depends on the `send` contract rather than checking each concrete type.

### Override signatures and `typing.override`

Python 3.12 provides `typing.override` to mark methods intended to override a base method. A compatible static type checker can then detect a misspelled method or incompatible override. It does not enforce compatibility at runtime.

```python
from typing import override

class JsonNotifier(Notifier):
    @override
    def send(self, recipient: str, message: str) -> str:
        return super().send(recipient, message)
```

An override should not demand *more* from callers than the base contract (for example, adding a new required argument) or promise *less* (for example, returning `None` when callers expect a reference). Adding optional keyword-only configuration is often safer than changing existing positional arguments, but compatibility depends on the actual public API and typing contract.

Do not catch broad exceptions merely to make an override appear compatible. Preserve the parent’s error semantics unless the contract explicitly allows a narrower or more informative behavior.

---

## 3. Constructor chaining: why `super().__init__` matters

A child that defines its own `__init__` does not automatically execute the parent initializer. If the child omits the call, parent-managed state may never be set.

### Deliberately flawed version

```python
class Account:
    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner
        self.balance = balance

    def describe(self) -> str:
        return f"{self.owner}: {self.balance:.2f}"


class SavingsAccount(Account):
    def __init__(self, owner: str, rate: float) -> None:
        self.rate = rate  # parent initializer was skipped


broken = SavingsAccount("Ana", 0.02)
print(broken.describe())  # AttributeError: no attribute 'owner'
```

The instance exists, but it violates the invariant expected by `Account`. The defect may surface later, far from construction.

### Corrected version with explicit forwarding

```python
class SavingsAccount(Account):
    def __init__(
        self,
        owner: str,
        balance: float = 0.0,
        rate: float = 0.02,
    ) -> None:
        super().__init__(owner=owner, balance=balance)
        self.rate = rate
```

Use explicit parameter names when it improves readability and makes forwarding intent clear. Forward only arguments the parent accepts; do not pass child-only options to the parent.

### Call order

For `SavingsAccount("Ana", 100.0, 0.03)`, the conceptual order is:

```text
SavingsAccount.__init__(...)
  ├─ super().__init__(owner="Ana", balance=100.0)
  │    └─ Account.__init__(...)
  │         ├─ set self.owner
  │         └─ set self.balance
  └─ set self.rate
```

The result is one instance, initialized in stages. The base initializer establishes the base class's state contract; the child then establishes its additional state.

### Is `super()` always the first line?

Often, but not as an absolute rule. The correct order depends on the base class's documented requirements. A base initializer may call overridable methods or rely on state already established by the child, although calling overridable methods during initialization is itself a design hazard because the child may not yet be ready. Prefer base classes whose constructors establish their own invariants without calling subclass hooks. Follow a framework's explicit construction contract when it differs.

---

## 4. What `super()` means

`super()` does **not** literally mean “call the class written immediately above me.” It creates a proxy that continues attribute lookup after the current class in the instance's method resolution order (MRO). In simple single inheritance, that usually looks like the parent. This distinction matters when a hierarchy later gains multiple inheritance.

```python
class Root:
    def run(self) -> str:
        return "root"


class Middle(Root):
    def run(self) -> str:
        return "middle -> " + super().run()


class Leaf(Middle):
    def run(self) -> str:
        return "leaf -> " + super().run()


print(Leaf().run())
print([cls.__name__ for cls in Leaf.mro()])
```

Expected output:

```text
leaf -> middle -> root
['Leaf', 'Middle', 'Root', 'object']
```

`Leaf.mro()` is a safe, useful inspection tool. You do not need to calculate the MRO by hand in this lesson. `object` is the common root of ordinary new-style class hierarchies.

### Why prefer `super()` to `Parent.__init__(self, ...)`?

Hard-coding `Parent.__init__(self, ...)` bypasses the cooperative lookup chain and can call the wrong implementation if the hierarchy changes. In single inheritance it may appear to work, but `super()` expresses the intended delegation and is the conventional choice. Cooperative multiple inheritance requires every participating initializer to use a compatible protocol; a single inconsistent class can break the chain. The full mechanics belong to Module 1.11, lesson 08.

For this lesson, remember:

1. Use `super()` in the subclass to continue the MRO lookup.
2. Forward the correct parent arguments.
3. Keep initialization responsibilities clear.
4. Do not mix cooperative and hard-coded parent calls in a hierarchy intended to cooperate.

---

## 5. Preserve parent invariants

A base class defines assumptions that its methods rely on. Its constructor and public methods should maintain those assumptions. A subclass must not skip base initialization or change the meaning of inherited state.

```python
class Account:
    def __init__(self, owner: str, balance: float = 0.0) -> None:
        if not owner.strip():
            raise ValueError("owner must not be blank")
        if balance < 0:
            raise ValueError("balance must be non-negative")
        self.owner = owner
        self.balance = balance


class SavingsAccount(Account):
    def __init__(self, owner: str, balance: float = 0.0, rate: float = 0.02) -> None:
        if not 0 <= rate <= 1:
            raise ValueError("rate must be between 0 and 1")
        super().__init__(owner, balance)
        self.rate = rate
```

The child validates its own invariant and delegates shared validation and state setup to `Account`. If base initialization raises, the caller does not receive a successfully constructed object through this ordinary call. Avoid publishing `self` to registries, callbacks, or other threads from inside `__init__`; doing so can expose a partially initialized object.

For money-sensitive production systems, `float` may not be appropriate because binary floating-point cannot exactly represent many decimal fractions. The example focuses on inheritance mechanics; a real account model should use a carefully specified monetary representation and explicit currency/rounding rules.

### Liskov Substitution Principle (LSP)

A subtype should be usable where its base type is expected without breaking caller expectations. Practical checks:

- Does the child accept at least the inputs the parent contract promises to accept?
- Does it preserve return types and meanings?
- Does it preserve documented postconditions and invariants?
- Does it avoid surprising extra side effects or new failure modes?

A `ReadOnlyAccount` subclass of a mutable `Account` that overrides `deposit()` to always raise `PermissionError` is not substitutable if callers are promised that every account can accept deposits. Prefer a separate read-only interface/type or expose permissions through a different contract rather than pretending the subtype supports an operation it refuses.

---

## 6. Template method and contract testing

A template method keeps a stable algorithm in the base class and delegates one defined step to a subclass. Use it when the algorithm really is shared and extension points are narrow and documented.

```python
from abc import ABC, abstractmethod


class Exporter(ABC):
    def export(self, rows: list[dict[str, str]]) -> str:
        """Validate, format, and return a complete export payload."""
        if not rows:
            raise ValueError("rows must not be empty")
        body = self.render(rows)
        return f"rows={len(rows)}\n{body}"

    @abstractmethod
    def render(self, rows: list[dict[str, str]]) -> str:
        """Render rows in the export format provided by the subclass."""
        raise NotImplementedError


class CsvExporter(Exporter):
    def render(self, rows: list[dict[str, str]]) -> str:
        columns = list(rows[0])
        lines = [",".join(columns)]
        lines.extend(",".join(row.get(column, "") for column in columns) for row in rows)
        return "\n".join(lines)


print(CsvExporter().export([{"id": "1", "status": "ok"}]))
```

Expected output:

```text
rows=1
id,status
1,ok
```

This is a compact teaching example, not a production CSV serializer: it does not escape commas, quotes, or newlines. A production implementation should use Python's `csv` module.

Contract tests verify behavior promised by the base abstraction, not the implementation's internal details. For each concrete exporter, test the same required properties: rejects empty input, returns a string, and includes the row count. Then add format-specific tests for CSV escaping, column order, and so on. A test that only checks each class's private helper can miss substitutability defects.

---

## 7. Composition versus inheritance

Inheritance models an **is-a** relationship with substitutable behavior. Composition models **has-a**: an object delegates a responsibility to another object. Do not create subclasses merely to reuse a few lines of code.

### A fragile hierarchy

Imagine a notification system with `BaseNotifier`, `RetryingNotifier`, `TemplatedNotifier`, `AuditedNotifier`, `RetryingTemplatedNotifier`, `RetryingAuditedNotifier`, and separate combinations for each channel. As retrying, templating, and auditing are independent features, combinations multiply and each subclass becomes responsible for more inherited assumptions.

### Composition-based alternative

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    recipient: str
    body: str


class Sender:
    def send(self, message: Message) -> str:
        return f"sent:{message.recipient}:{message.body}"


class RetryingSender:
    def __init__(self, delegate: Sender, attempts: int = 3) -> None:
        if attempts < 1:
            raise ValueError("attempts must be at least 1")
        self._delegate = delegate
        self._attempts = attempts

    def send(self, message: Message) -> str:
        last_error: Exception | None = None
        for _ in range(self._attempts):
            try:
                return self._delegate.send(message)
            except (TimeoutError, ConnectionError) as exc:
                last_error = exc
        assert last_error is not None
        raise last_error


def add_prefix(message: Message, prefix: str) -> Message:
    return Message(message.recipient, f"{prefix}{message.body}")


base = Sender()
retrying = RetryingSender(base, attempts=2)
print(retrying.send(add_prefix(Message("ops@example.test", "done"), "[ETL] ")))
```

Expected output:

```text
sent:ops@example.test:[ETL] done
```

The example illustrates delegation; a real retry wrapper should inject time/sleep behavior, define retryable errors, use bounded backoff, and account for idempotency. The `Sender` example is concrete for simplicity; production code can type the delegate against a `Protocol` and inject email/SMS implementations.

| Situation | Likely better fit |
|---|---|
| True subtype with substitutable behavior and a stable base contract | Shallow inheritance |
| Reuse a capability without claiming “is-a” | Composition/delegation |
| Behavior varies per job or deployment | Inject a strategy object or function |
| Several orthogonal features must combine | Composition/decorators around a collaborator |
| Framework explicitly requires a base class | Inherit and follow its documented contract |
| Only need a named collection of constants | Module or enum, not a class hierarchy |

Composition is not automatically superior: a framework extension point may require inheritance, and a small stable hierarchy can be clearer than indirection. Choose based on substitutability, change patterns, and testability.

---

## 8. Standard-library subclassing examples

### `threading.Thread`

If subclassing `threading.Thread`, call its initializer so its internal state is configured before the thread is started. Do not call `run()` directly when you intend to start a new thread; `start()` manages thread startup and then invokes `run()` in the new thread.

```python
from threading import Thread


class Worker(Thread):
    def __init__(self, job_id: str) -> None:
        super().__init__(name=f"worker-{job_id}")
        self.job_id = job_id

    def run(self) -> None:
        print(f"processing {self.job_id}")


worker = Worker("42")
print(worker.name)
worker.start()
worker.join()
```

The first output line is deterministically `worker-42`; the worker line is `processing 42`, printed by the worker thread. Avoid tests that rely on the relative ordering of unrelated threads' output. In production, prefer passing a `target` callable to `Thread` when subclassing adds no meaningful behavior.

### Custom exceptions

Call the parent initializer so the exception's message and argument tuple are set consistently:

```python
import pickle


class DataQualityError(Exception):
    """Raised when an input dataset violates a quality rule."""

    def __init__(self, dataset: str, detail: str) -> None:
        self.dataset = dataset
        self.detail = detail
        # Preserve the constructor arguments so pickle can reconstruct the exception.
        super().__init__(dataset, detail)

    def __str__(self) -> str:
        return f"{self.dataset}: {self.detail}"


error = DataQualityError("events", "missing event_id")
print(str(error))
print(error.args)
restored = pickle.loads(pickle.dumps(error))
print(type(restored) is DataQualityError, restored.dataset, restored.detail)
```

Expected output:

```text
events: missing event_id
('events', 'missing event_id')
True events missing event_id
```

For picklable custom exceptions, the stored `args` must be compatible with the constructor used during unpickling. Here `args` contains `(dataset, detail)`, so the default exception reconstruction can call `DataQualityError(dataset, detail)`; `__str__` provides the human-readable message. Test round-tripping in the actual process/serialization environment when it is a requirement, especially if the class later gains custom state.

---

## 9. Common mistakes and safer alternatives

| Mistake | Why it fails | Safer action |
|---|---|---|
| Child defines `__init__` but skips `super().__init__` | Parent state/invariants are missing | Chain to `super()` with the required arguments |
| Passes child-only keyword arguments to parent | Unexpected-keyword `TypeError` | Design explicit child parameters and forward only parent parameters |
| Calls `Parent.__init__(self, ...)` everywhere | Hard-codes hierarchy and bypasses cooperative lookup | Use `super()` for conventional chaining |
| Changes a method's signature incompatibly | Existing callers may fail | Preserve contract; add optional parameters carefully; type-check overrides |
| Uses inheritance solely to copy implementation | False “is-a” relationship and fragile coupling | Extract a function or collaborator and compose it |
| Parent initializer calls an overridable child method | Child method may observe incomplete child state | Avoid virtual calls during construction; use explicit post-construction hooks/factories if needed |
| Uses mutable class attributes for per-instance state | Instances unexpectedly share data | Initialize a new mutable value per instance |
| Assumes `super()` always names the lexical parent | Incorrect mental model for MRO | Inspect `ClassName.mro()` and learn cooperative lookup before using multiple inheritance |
| Overrides a method but ignores its return value/side effects | Subclass violates caller expectations | Document and test the base contract |
| Tests only the concrete class internals | Misses substitutability regressions | Test behavior through the base interface |

---

## 10. Testing inheritance and constructor chains

Use tests to prove both parent state and child-specific state exist, invalid input is rejected, and public methods preserve their contract. The following pytest tests are self-contained and executable.

Save as `test_inheritance.py`:

```python
import pickle
from abc import ABC, abstractmethod
from typing import override

import pytest


class DataQualityError(Exception):
    def __init__(self, dataset: str, detail: str) -> None:
        self.dataset = dataset
        self.detail = detail
        super().__init__(dataset, detail)

    def __str__(self) -> str:
        return f"{self.dataset}: {self.detail}"


class Account:
    def __init__(self, owner: str, balance: float = 0.0) -> None:
        if not owner.strip():
            raise ValueError("owner must not be blank")
        if balance < 0:
            raise ValueError("balance must be non-negative")
        self.owner = owner
        self.balance = balance

    def describe(self) -> str:
        return f"{self.owner}: {self.balance:.2f}"


class SavingsAccount(Account):
    def __init__(self, owner: str, balance: float = 0.0, rate: float = 0.02) -> None:
        if not 0 <= rate <= 1:
            raise ValueError("rate must be between 0 and 1")
        super().__init__(owner, balance)
        self.rate = rate

    @override
    def describe(self) -> str:
        return f"{super().describe()} (rate {self.rate:.1%})"


class Exporter(ABC):
    def export(self, rows: list[dict[str, str]]) -> str:
        if not rows:
            raise ValueError("rows must not be empty")
        return f"rows={len(rows)}\n{self.render(rows)}"

    @abstractmethod
    def render(self, rows: list[dict[str, str]]) -> str:
        raise NotImplementedError


class CsvExporter(Exporter):
    @override
    def render(self, rows: list[dict[str, str]]) -> str:
        columns = list(rows[0])
        lines = [",".join(columns)]
        lines.extend(",".join(row.get(column, "") for column in columns) for row in rows)
        return "\n".join(lines)


class KeyValueExporter(Exporter):
    @override
    def render(self, rows: list[dict[str, str]]) -> str:
        return "\n".join(
            " ".join(f"{key}={value}" for key, value in row.items())
            for row in rows
        )


class BrokenSavingsAccount(Account):
    def __init__(self, owner: str) -> None:
        self.rate = 0.02  # intentionally omits super().__init__


def test_constructor_chains_and_method_is_overridden() -> None:
    account = SavingsAccount("Ana", 100.0, 0.03)
    assert account.owner == "Ana"
    assert account.balance == 100.0
    assert account.rate == 0.03
    assert account.describe() == "Ana: 100.00 (rate 3.0%)"
    assert isinstance(account, Account)


@pytest.mark.parametrize("owner", ["", "   "])
def test_blank_owner_is_rejected(owner: str) -> None:
    with pytest.raises(ValueError, match="owner must not be blank"):
        SavingsAccount(owner)


def test_negative_balance_is_rejected() -> None:
    with pytest.raises(ValueError, match="balance must be non-negative"):
        SavingsAccount("Ana", -1.0)


@pytest.mark.parametrize("rate", [-0.01, 1.01])
def test_invalid_rate_is_rejected(rate: float) -> None:
    with pytest.raises(ValueError, match="rate must be between 0 and 1"):
        SavingsAccount("Ana", rate=rate)


@pytest.mark.parametrize(
    "exporter",
    [CsvExporter(), KeyValueExporter()],
    ids=["csv", "key-value"],
)
def test_exporter_contract(exporter: Exporter) -> None:
    result = exporter.export([{"id": "1", "status": "ok"}])
    assert isinstance(result, str)
    assert result.startswith("rows=1\n")


def test_csv_exporter_format() -> None:
    result = CsvExporter().export([{"id": "1", "status": "ok"}])
    assert "id,status" in result


def test_key_value_exporter_format() -> None:
    result = KeyValueExporter().export([{"id": "1", "status": "ok"}])
    assert "id=1 status=ok" in result


def test_exporter_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="rows must not be empty"):
        CsvExporter().export([])


def test_missing_parent_initialization_breaks_inherited_method() -> None:
    account = BrokenSavingsAccount("Ana")
    with pytest.raises(AttributeError, match="owner"):
        account.describe()


def test_custom_exception_pickle_round_trip() -> None:
    original = DataQualityError("events", "missing event_id")
    restored = pickle.loads(pickle.dumps(original))
    assert type(restored) is DataQualityError
    assert restored.dataset == original.dataset
    assert restored.detail == original.detail
    assert str(restored) == str(original)
    assert restored.args == ("events", "missing event_id")
```

Run:

```bash
python -m pytest -q test_inheritance.py
```

The suite parametrizes the same contract over two concrete exporters, then keeps format-specific assertions separate. When a project adds a new implementation, add it to the contract-test parameters first; it must satisfy the same base guarantees before its format-specific behavior is considered. Tests should not depend on a particular private attribute layout unless that layout is itself a documented compatibility requirement.

### Test the failure mode of a missing parent call

A deliberately broken subclass can be used in a focused regression test:

```python
class BrokenSavingsAccount(Account):
    def __init__(self, owner: str) -> None:
        self.rate = 0.02


def test_missing_parent_initialization_is_visible() -> None:
    account = BrokenSavingsAccount("Ana")
    with pytest.raises(AttributeError, match="owner"):
        account.describe()
```

Do not retain a broken implementation in production merely to test it. This example demonstrates why testing construction invariants catches defects earlier:

```python
def test_subclass_has_required_parent_state() -> None:
    account = SavingsAccount("Ana")
    assert account.owner
    assert account.balance >= 0
```

---

## 11. Exercises and solutions

Try each exercise before reading the solution. All examples target Python 3.12+.

### Exercise 1 — Add a fee-bearing account

Implement `FeeAccount(Account)` with a non-negative `monthly_fee`. Constructor chaining must initialize `owner` and `balance`. Add a method that returns the balance after one fee is deducted, without mutating the stored balance.

**Solution:**

```python
class FeeAccount(Account):
    def __init__(self, owner: str, balance: float, monthly_fee: float) -> None:
        if monthly_fee < 0:
            raise ValueError("monthly_fee must be non-negative")
        super().__init__(owner, balance)
        self.monthly_fee = monthly_fee

    def projected_balance_after_fee(self) -> float:
        return self.balance - self.monthly_fee
```

The child validates its own rule, delegates base validation, then stores its own state. A production monetary model should also define precision and currency semantics.

### Exercise 2 — Repair a signature and chaining bug

Given:

```python
class Job:
    def __init__(self, job_id: str, priority: int = 0) -> None:
        self.job_id = job_id
        self.priority = priority


class ScheduledJob(Job):
    def __init__(self, job_id: str, run_at: str) -> None:
        self.run_at = run_at
```

Repair it so `ScheduledJob` retains the parent's state and accepts an optional priority.

**Solution:**

```python
class ScheduledJob(Job):
    def __init__(self, job_id: str, run_at: str, priority: int = 0) -> None:
        super().__init__(job_id=job_id, priority=priority)
        self.run_at = run_at
```

If `run_at` has a formal timestamp contract, parse it into an appropriate timezone-aware type and validate it rather than leaving arbitrary strings in the domain model.

### Exercise 3 — Identify an LSP violation

A base `Storage` promises `save(key, value)`. A subclass `ReadOnlyStorage` inherits from `Storage` but always raises `PermissionError` from `save`. Why is this problematic? Propose two alternatives.

**Solution:** The subtype rejects an operation the base contract promises. Alternatives include (1) define separate `ReadableStorage` and `WritableStorage` protocols/interfaces and type consumers to the capabilities they require, or (2) use a read-only adapter that does not claim to implement the writable contract. If permissions are dynamic, model authorization explicitly and document the operation's failure contract.

### Exercise 4 — Inheritance or composition?

A pipeline can send alerts through email, SMS, or Slack. Each channel may independently use retries, templating, and audit logging. Should you create a subclass for every combination?

**Solution:** Usually not. Keep a small channel interface or protocol, then compose wrappers/strategies for retry, templating, and audit. This avoids a class for each Cartesian combination. A base class remains reasonable if it provides a genuinely shared, stable algorithm and documented extension points.

### Exercise 5 — Contract-test a new subtype

Write a test reusable for every implementation of `Exporter`: empty input raises `ValueError`, non-empty input returns a string, and the output contains the number of rows. Add format-specific tests for each concrete exporter.

**Solution sketch:** Put the shared assertions in a helper such as `assert_exporter_contract(exporter: Exporter)`, then call it with each implementation using parametrization or fixtures. Keep CSV quoting and ordering assertions in `CsvExporter`-specific tests.

---

## 12. Self-check

Answer without looking back:

1. What does a child lose if it defines `__init__` and does not call the parent's initializer?
2. What is the difference between `isinstance(obj, Parent)` and `type(obj) is Parent`?
3. Why is `super()` more accurate to describe as “continue lookup after this class” than “call my parent”?
4. Which part of a subclass constructor should validate child-specific invariants, and which part should establish base invariants?
5. What does LSP require of an override's inputs, outputs, and behavior?
6. When would a delegate or strategy be preferable to a subclass?
7. What is a contract test, and how does it help when adding a new subtype?
8. Where does the curriculum cover C3 linearization and cooperative multiple inheritance in depth?

### Answer key

1. Parent-managed state and invariants may be absent; inherited methods can fail later.
2. `isinstance` accepts instances of subclasses; `type(obj) is Parent` requires exact type.
3. `super()` follows the MRO and remains cooperative if the hierarchy changes.
4. The child validates its own rules; the base initializer establishes base rules, with ordering governed by the base contract.
5. A subtype should not strengthen required preconditions or weaken promised postconditions, and should preserve the base behavioral contract.
6. When the relationship is “has-a,” behavior varies independently, or code reuse is the only motivation for inheritance.
7. A shared test suite verifies base guarantees against each implementation, catching substitutability regressions.
8. Stage 1 Module 1.11, lessons 08–09.

---

## 13. Summary

- Inheritance is a behavioral relationship, not merely a code-reuse mechanism.
- A subclass that defines `__init__` must deliberately initialize the base part when the base contract requires it; `super().__init__(...)` is the normal pattern.
- Forward the right arguments and preserve parent invariants.
- `super()` continues lookup through the MRO. Use `ClassName.mro()` to inspect a hierarchy; leave advanced C3 mechanics to the dedicated module.
- Overrides must preserve behavioral contracts and substitutability, not just method names.
- Contract tests help ensure new subtypes work anywhere the base abstraction is expected.
- Prefer composition or strategy injection when features vary independently or inheritance does not represent a genuine “is-a” relationship.

## Completion checklist

- [ ] I can define a parent and child and explain inherited behavior.
- [ ] I can override a method and extend parent behavior with `super()`.
- [ ] I can write a child initializer that forwards arguments correctly and preserves base invariants.
- [ ] I can explain the basic MRO and inspect it with `.mro()`.
- [ ] I can identify a likely LSP violation and suggest a contract-preserving design.
- [ ] I can write a contract test that runs against multiple implementations.
- [ ] I can justify inheritance versus composition for a concrete production requirement.
- [ ] I can run the included pytest tests and add regression tests for a new subtype.
