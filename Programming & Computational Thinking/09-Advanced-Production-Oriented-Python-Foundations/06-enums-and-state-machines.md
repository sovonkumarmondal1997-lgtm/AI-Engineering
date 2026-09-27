# Enums and State Machines

> **Stage 1 — Programming & Computational Thinking**  
> **Module 1.9 — Advanced Production-Oriented Python Foundations**  
> **Topic:** Enums, explicit states, finite-state modeling, transition validation, and production-oriented state management.

---

## Learning Goals

By the end of this chapter, you should be able to:

- explain why Enums exist and when ordinary strings, integers, constants, or booleans are insufficient;
- distinguish an Enum member's **name**, **value**, identity, and external representation;
- use `Enum`, `IntEnum`, `StrEnum`, `Flag`, `IntFlag`, `auto()`, and `@unique` appropriately;
- look up Enum members by name or value;
- use Enums in functions, conditional logic, `match`/`case`, configuration, and API boundaries;
- explain why an Enum is **not** itself a state machine;
- model states and events explicitly;
- represent transitions as `(current_state, event) -> next_state`;
- reject invalid transitions and protect terminal states;
- express invariants and idempotency rules;
- separate state transitions from external side effects;
- reason about persistence, retries, failures, observability, auditing, and concurrency;
- test transition tables and state-machine invariants;
- choose between simple conditionals, an Enum, a transition table, a dedicated state-machine abstraction, and a larger workflow system;
- apply these ideas to data pipelines, model inference, RAG ingestion, evaluation jobs, and agent execution;
- design a small production-oriented state machine without over-engineering it.

---

# 1. Why Enums Exist

## 1.1 The problem: magic values

Suppose we track the status of a job:

```python
status = "pending"
```

That looks simple. But the program may accidentally create inconsistent values:

```python
status = "pendng"
status = "PENDING"
status = "waiting"
status = 3
```

There is no single obvious vocabulary in those examples.

The problem gets worse as the codebase grows:

```python
if status == "pending":
    ...

if job_status == "pending":
    ...

if task_state == "PENDING":
    ...

if status_code == 3:
    ...
```

The strings or integers may represent the same idea, but the code does not make that relationship explicit.

### Common problems with uncontrolled values

| Problem | Example | Engineering consequence |
|---|---|---|
| Typo | `"pendng"` | Invalid value enters the system |
| Inconsistent spelling | `"PENDING"` vs `"pending"` | Logic silently diverges |
| Magic number | `3` | Meaning is hidden |
| Duplicated constants | `"pending"` everywhere | Harder refactoring |
| Weak discoverability | free-form strings | IDEs provide less guidance |
| Weak domain vocabulary | arbitrary values | Intent is harder to understand |
| Difficult validation | accept any `str` | Invalid states are easier to create |

An Enum gives us a controlled vocabulary.

---

# 2. What Is an Enum?

An **enumeration**, commonly called an **Enum**, is a type containing a fixed set of named members.

A simple example:

```python
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
```

Now the valid domain vocabulary is visible:

```python
print(Status.PENDING)
print(Status.RUNNING)
print(Status.COMPLETED)
```

Typical output:

```text
Status.PENDING
Status.RUNNING
Status.COMPLETED
```

The exact `repr()`/`str()` presentation can vary by Enum type and Python version, so the important concept is the member identity, not its display text.

### Mental model

Think of:

```text
Status
├── PENDING
├── RUNNING
└── COMPLETED
```

as a controlled vocabulary.

An Enum is not just a bag of constants. Enum members are objects with Enum semantics.

---

# 3. Enum Members, Names, and Values

Consider:

```python
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
```

There are several distinct things to understand.

## 3.1 The member

```python
Status.PENDING
```

This is the Enum member.

## 3.2 The member name

```python
Status.PENDING.name
```

Output:

```text
PENDING
```

The name is the identifier used to define the member.

## 3.3 The member value

```python
Status.PENDING.value
```

Output:

```text
pending
```

The value is the data associated with that member.

## 3.4 They are not the same thing

```python
print(Status.PENDING)
print(Status.PENDING.name)
print(Status.PENDING.value)
```

Conceptually:

```text
member      -> Status.PENDING
name        -> "PENDING"
value       -> "pending"
```

This distinction becomes especially important when crossing external boundaries such as configuration files, APIs, or storage systems.

---

# 4. Identity, Equality, `repr()`, and `str()`

Start with identity:

```python
from enum import Enum


class Status(Enum):
    PENDING = "pending"


a = Status.PENDING
b = Status.PENDING

print(a is b)
print(a == b)
```

Expected output:

```text
True
True
```

Within an Enum, the canonical member is a stable member object.

Now compare the member to its raw value:

```python
print(Status.PENDING == "pending")
print(Status.PENDING.value == "pending")
```

Typical output:

```text
False
True
```

A normal `Enum` member is not simply the same thing as its value.

### Inspecting representation

```python
print(repr(Status.PENDING))
print(str(Status.PENDING))
```

For a normal Enum, these commonly display the Enum class and member name.

Do not build application logic around a human-facing `str()` representation unless you explicitly define that contract. Prefer `.name` or `.value` when you need a precise representation.

---

# 5. Enum Iteration

An Enum can be iterated:

```python
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"


for status in Status:
    print(status.name, status.value)
```

Output:

```text
PENDING pending
RUNNING running
COMPLETED completed
```

Iteration follows the Enum's definition order for canonical, non-alias members.

This is useful for:

- generating valid choices;
- displaying options;
- configuration validation;
- documentation;
- test cases;
- building finite sets of allowed values.

Example:

```python
valid_values = [status.value for status in Status]
print(valid_values)
```

Output:

```text
['pending', 'running', 'completed']
```

---

# 6. Looking Up Members

Python provides two different lookup mechanisms.

## 6.1 Lookup by value

Use call syntax:

```python
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"


status = Status("pending")
print(status)
```

Conceptually:

```text
"pending"
   ↓
Status("pending")
   ↓
Status.PENDING
```

If the value is invalid, Python raises `ValueError`:

```python
try:
    Status("unknown")
except ValueError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
ValueError
```

## 6.2 Lookup by member name

Use indexing syntax:

```python
status = Status["PENDING"]
print(status)
```

The name must exist exactly.

An unknown name raises `KeyError`:

```python
try:
    Status["UNKNOWN"]
except KeyError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
KeyError
```

### The distinction

| Operation | Meaning |
|---|---|
| `Status("pending")` | Find member by **value** |
| `Status["PENDING"]` | Find member by **name** |

Do not confuse these two APIs.

---

# 7. `__members__`

Enums expose a mapping containing member names and members:

```python
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"


print(Status.__members__)
```

This is particularly useful when you need to inspect all defined names, including aliases.

For example:

```python
for name, member in Status.__members__.items():
    print(name, member.value)
```

This can be useful for diagnostics and tooling, but normal application code should usually access members directly:

```python
Status.PENDING
```

rather than depending heavily on Enum internals.

---

# 8. Enums in Functions

Enums make function contracts clearer.

```python
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"


def can_process(status: Status) -> bool:
    return status in {Status.PENDING, Status.RUNNING}


print(can_process(Status.PENDING))
print(can_process(Status.COMPLETED))
```

Output:

```text
True
False
```

Without an Enum, the function might accept arbitrary strings:

```python
def can_process(status: str) -> bool:
    ...
```

The annotation alone does not restrict runtime values, but the Enum communicates the intended domain vocabulary to:

- humans;
- IDEs;
- static type checkers;
- tests;
- API designers.

---

# 9. Enum and Conditional Logic

For a small number of cases, `if`/`elif` is often perfectly clear:

```python
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"


def describe(status: Status) -> str:
    if status == Status.PENDING:
        return "Waiting to start"
    if status == Status.RUNNING:
        return "Currently processing"
    if status == Status.COMPLETED:
        return "Finished"
    raise ValueError(f"Unsupported status: {status}")
```

This style is easy to read.

---

# 10. Enum with `match` / `case`

Python 3.10+ provides structural pattern matching.

```python
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"


def describe(status: Status) -> str:
    match status:
        case Status.PENDING:
            return "Waiting to start"
        case Status.RUNNING:
            return "Currently processing"
        case Status.COMPLETED:
            return "Finished"
        case _:
            raise ValueError(f"Unsupported status: {status}")
```

`match` can make a finite set of domain states easy to inspect.

However, `match` does not automatically prove that every future Enum member is handled. A default branch such as:

```python
from enum import StrEnum


class Status(StrEnum):
    PENDING = "pending"


def describe(status: Status) -> str:
    match status:
        case Status.PENDING:
            return "waiting"
        case _:
            return "unknown"
```

can still be useful as a runtime guard.

### When to use `if` versus `match`

Use whichever makes the business logic clearer.

A few simple branches do not require `match`.

A larger pattern-driven decision may benefit from `match`.

The key principle is:

> Use the clearest representation of the domain, not the newest syntax available.

---

# 11. String-Backed Enums

Sometimes an Enum needs to interoperate naturally with string-oriented boundaries.

One common pattern is:

```python
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
```

The members are still Enum members, but they are also string subclasses.

This is useful for:

- configuration;
- APIs;
- command-line values;
- serialization boundaries;
- external systems that already use strings.

Example:

```python
environment = Environment.PRODUCTION

print(environment.value)
print(isinstance(environment, str))
```

Output conceptually:

```text
production
True
```

Do not assume that every library treats a `str` subclass exactly like an object whose type is literally `str`. Some code checks exact types rather than using `isinstance()`. Where an exact string is required, an explicit conversion can be appropriate:

```python
raw_value = str(Environment.PRODUCTION)
```

---

# 12. `StrEnum`

Modern Python provides `enum.StrEnum`.

```python
from enum import StrEnum


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
```

`StrEnum` was added in Python 3.11. It provides the same general idea as a `str`-backed Enum with behavior designed for replacing string constants. Python's current standard-library documentation also notes that `str()` and formatting use the string value for `StrEnum`. citeturn442575search0turn442575search1

### Version compatibility

```python
from enum import StrEnum
```

requires Python 3.11 or newer.

For environments supporting older Python versions, the following pattern is commonly used:

```python
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
```

Production code should choose syntax based on the project's supported Python versions, not on the version installed on one developer's machine.

---

# 13. `IntEnum`

`IntEnum` is an Enum whose members are also integers.

```python
from enum import IntEnum


class ExitCode(IntEnum):
    SUCCESS = 0
    INVALID_INPUT = 2
    INTERNAL_ERROR = 3


print(ExitCode.SUCCESS == 0)
print(int(ExitCode.SUCCESS))
```

Output:

```text
True
0
```

This compatibility is useful when integrating with systems that already expect integer constants.

## Important trade-off

Integer semantics can leak into your domain:

```python
result = ExitCode.INVALID_INPUT + 1
print(result)
```

The result is an integer rather than a meaningful `ExitCode` member.

That means `IntEnum` should usually be chosen because integer interoperability is actually required.

Prefer ordinary `Enum` when you want stronger separation between a domain concept and arbitrary integers.

---

# 14. `auto()`

`auto()` asks the Enum machinery to generate values.

```python
from enum import Enum, auto


class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()


for color in Color:
    print(color.name, color.value)
```

Typical output:

```text
RED 1
GREEN 2
BLUE 3
```

For `Flag` and `IntFlag`, `auto()` generates power-of-two values so that bitwise combinations work correctly. For `StrEnum`, `auto()` produces lower-cased member names by default. These are documented standard-library behaviors. citeturn442575search0

## When `auto()` is useful

It is useful when:

- values are internal only;
- exact numeric values do not matter;
- you want to avoid manually maintaining sequential numbers.

## When explicit values are safer

Use explicit values when the value crosses a stable external boundary:

```python
class OrderStatus(StrEnum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
```

These strings are part of the external contract and should not change accidentally.

---

# 15. Enum Aliases

An alias occurs when two names have the same value.

```python
from enum import Enum


class Status(Enum):
    ACTIVE = "active"
    ENABLED = "active"
    DISABLED = "disabled"
```

Then:

```python
print(Status.ACTIVE is Status.ENABLED)
```

Output:

```text
True
```

`ENABLED` is an alias of the canonical `ACTIVE` member.

### Iteration behavior

```python
print(list(Status))
```

The alias is not returned as a separate canonical member during normal Enum iteration.

But `__members__` includes aliases:

```python
print(Status.__members__)
```

This distinction matters when inspecting all declared names.

### Why aliases exist

Aliases can help when:

- migrating legacy terminology;
- supporting old names;
- preserving compatibility.

But aliases can also make the vocabulary less obvious. Use them deliberately.

---

# 16. `@unique`

If duplicate values are not intended, `@unique` makes that rule explicit.

```python
from enum import Enum, unique


@unique
class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
```

If we introduce duplicate values:

```python
from enum import Enum, unique


try:
    @unique
    class Status(Enum):
        ACTIVE = "active"
        ENABLED = "active"
except ValueError as exc:
    print(type(exc).__name__)
```

Output:

```text
ValueError
```

Use `@unique` when duplicate-value aliases would represent a mistake.

Do not use it when aliases are an intentional part of the design.

---

# 17. Functional Enum API

Enums can also be created with a function call:

```python
from enum import Enum


Status = Enum(
    "Status",
    [
        ("PENDING", "pending"),
        ("RUNNING", "running"),
        ("COMPLETED", "completed"),
    ],
)

print(Status.PENDING.value)
```

Output:

```text
pending
```

The functional form can be useful for dynamic generation or when names/values already exist as data.

For ordinary domain models, class syntax is usually easier to read:

```python
class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
```

The goal is not to prefer one style universally. The goal is to choose the form that makes the domain definition obvious.

---

# 18. `Flag`

A normal Enum represents one selected member.

A `Flag` represents independent options that can be combined.

```python
from enum import Flag, auto


class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


read_write = Permission.READ | Permission.WRITE

print(read_write)
print(Permission.READ in read_write)
print(Permission.EXECUTE in read_write)
```

Conceptually:

```text
READ    = 001
WRITE   = 010
EXECUTE = 100

READ | WRITE = 011
```

The bitwise representation is what makes the combination possible.

This is useful for sets of independent capabilities such as:

- permissions;
- feature bits;
- protocol options;
- configuration flags.

It is not a replacement for an ordinary state Enum.

---

# 19. `IntFlag`

`IntFlag` combines flag semantics with integer compatibility.

```python
from enum import IntFlag, auto


class Permission(IntFlag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


permissions = Permission.READ | Permission.WRITE

print(int(permissions))
print(Permission.READ in permissions)
```

Use `IntFlag` when interoperability with integer bit masks is required.

Be cautious because integer operations can produce ordinary integers and expose implementation details:

```python
result = Permission.READ + 2
print(type(result).__name__)
```

Output:

```text
int
```

Again, choose `IntFlag` because integer compatibility is part of the requirement, not because it looks powerful.

---

# 20. `Enum` vs `Flag`

The conceptual difference is:

```text
Enum
 |
 +-- one domain member at a time

Flag
 |
 +-- zero, one, or multiple independent options
```

Example:

```python
class JobState(Enum):
    RUNNING = "running"
```

means the job is in one state.

By contrast:

```python
class Permission(Flag):
    READ = auto()
    WRITE = auto()
```

allows:

```python
Permission.READ | Permission.WRITE
```

which means the object has both capabilities.

Do not model mutually exclusive workflow states as `Flag` values.

---

# 21. Enum and Serialization

Internal Enum representation and external representation are different concerns.

Suppose:

```python
from enum import StrEnum
import json


class Status(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"


payload = {
    "status": Status.PENDING.value,
}

print(json.dumps(payload))
```

Output:

```text
{"status": "pending"}
```

Using `.value` makes the boundary explicit.

A robust design often looks like:

```text
Internal domain
    ↓
Status.PENDING
    ↓
.value
    ↓
"pending"
    ↓
JSON / API / storage
```

This reduces ambiguity.

### Boundary principle

Do not let the external representation accidentally become your entire internal domain model.

An API may say `"pending"` today, while your internal application still benefits from:

```python
Status.PENDING
```

---

# 22. Enum and Configuration

Enums are useful for finite configuration choices.

```python
from enum import StrEnum


class Environment(StrEnum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class ModelProvider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
```

A configuration object can then use these values:

```python
config = {
    "environment": Environment.PROD,
    "model_provider": ModelProvider.LOCAL,
}
```

The code communicates that these fields are finite domain choices.

At an external boundary, you can convert strings into the Enum:

```python
environment = Environment("prod")
```

and reject unknown values early.

---

# 23. Enum and Database-Style Domain Values

Suppose an order can have one of these values:

```text
created
paid
shipped
delivered
cancelled
```

An Enum can express this domain explicitly:

```python
from enum import StrEnum


class OrderState(StrEnum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
```

A persistence layer might store:

```python
state.value
```

rather than a Python-specific representation.

### Production concerns

Changing an externally persisted Enum value may break old data or old consumers.

For example, changing:

```python
PAID = "paid"
```

to:

```python
PAID = "payment_complete"
```

can be a data-compatibility change.

When an Enum value is externally stored or transmitted, treat the value as part of a contract.

Adding a member may also require:

- validation updates;
- UI updates;
- consumer updates;
- migration planning;
- state-machine transition updates.

---

# 24. Enum vs Constant

A plain constant is sometimes enough.

```python
STATUS_PENDING = "pending"
```

An Enum is more structured:

```python
class Status(Enum):
    PENDING = "pending"
```

### Comparison

| Requirement | Constant | Enum |
|---|---:|---:|
| Named value | Yes | Yes |
| Single finite vocabulary | Informal | Explicit |
| Easy iteration | Manual | Built in |
| `.name` / `.value` | No | Yes |
| Member identity | No | Yes |
| Type-level domain vocabulary | Weaker | Stronger |
| External string value | Easy | Easy with explicit `.value` |
| Simplicity | Very high | Moderate |

A few constants may be the clearest solution.

Do not turn every constant into an Enum.

---

# 25. Enum vs Boolean

A boolean represents two states:

```python
is_ready = True
```

This can be excellent when there really are only two meaningful states.

The problem appears when several states emerge:

```python
is_ready = False
is_running = True
is_failed = False
is_cancelled = False
```

Now multiple booleans can represent contradictory combinations.

For example:

```text
is_ready = True
is_running = True
is_failed = True
```

What does that mean?

A single state Enum is often clearer:

```python
class JobState(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
```

### Boolean explosion

Several independent boolean flags can accidentally create many combinations, including invalid ones.

Use an Enum when the domain is a mutually exclusive finite state.

Use booleans when each boolean represents a genuinely independent yes/no fact.

---

# 26. Enum vs String

Compare:

```python
status = "pending"
```

with:

```python
status = Status.PENDING
```

The string is simpler and often appropriate at an external boundary.

The Enum communicates the internal domain better.

A useful pattern is:

```text
external string
    ↓
validate / convert
    ↓
internal Enum
    ↓
business logic
    ↓
Enum.value
    ↓
external string
```

This makes conversion points visible.

---

# 27. Why State Machines Exist

Now we move from Enums to state machines.

An Enum can tell us **what states exist**.

It does not, by itself, tell us:

- which state is current;
- which events are valid;
- which transitions are legal;
- what happens on invalid events;
- which states are terminal;
- which transitions may retry;
- what side effects occur.

For example:

```python
from enum import StrEnum


class OrderState(StrEnum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
```

This defines vocabulary.

A state machine adds transition rules.

---

# 28. State Machine Fundamentals

A finite-state model usually has at least these concepts:

1. **State** — the current condition.
2. **Event** — something that happens.
3. **Transition** — the rule that moves from one state to another.
4. **Initial state** — where the entity starts.
5. **Terminal state** — a state from which no normal transitions leave.
6. **Transition validation** — rules for rejecting invalid events.
7. **Invariant** — a condition that must remain true.
8. **Current state** — the state currently stored for the entity.

A useful mathematical mental model is:

```text
(current_state, event) → next_state
```

Example:

```text
(CREATED, PAY) → PAID
```

---

# 29. State vs Event

This distinction is fundamental.

### State

A state describes a condition:

```text
PAID
```

### Event

An event describes something that happened:

```text
PAY
```

The event can cause the state to change:

```text
CREATED + PAY → PAID
```

Do not model the event itself as the state.

Bad vocabulary:

```text
state = "pay"
```

when what you really mean is:

```text
event = PAY
state = PAID
```

Clear naming prevents many state-machine design errors.

---

# 30. A State Machine Diagram

Consider an order:

```text
                         ┌───────────────┐
                         │   CREATED     │
                         └───────┬───────┘
                                 │ PAY
                                 ▼
                         ┌───────────────┐
                         │     PAID      │
                         └───────┬───────┘
                                 │ SHIP
                                 ▼
                         ┌───────────────┐
                         │    SHIPPED    │
                         └───────┬───────┘
                                 │ DELIVER
                                 ▼
                         ┌───────────────┐
                         │   DELIVERED   │
                         └───────────────┘

CREATED ───────── CANCEL ─────────> CANCELLED
```

The boxes are states.

The arrows are transitions caused by events.

---

# 31. Defining State and Event Enums

A clean starting point is:

```python
from enum import StrEnum


class OrderState(StrEnum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderEvent(StrEnum):
    PAY = "pay"
    SHIP = "ship"
    DELIVER = "deliver"
    CANCEL = "cancel"
```

This gives us two separate controlled vocabularies:

```text
State vocabulary
    CREATED
    PAID
    SHIPPED
    DELIVERED
    CANCELLED

Event vocabulary
    PAY
    SHIP
    DELIVER
    CANCEL
```

Keeping them distinct prevents accidental state/event confusion.

---

# 32. Transition Tables

A transition table explicitly describes legal moves:

```python
TRANSITIONS = {
    OrderState.CREATED: {
        OrderEvent.PAY: OrderState.PAID,
        OrderEvent.CANCEL: OrderState.CANCELLED,
    },
    OrderState.PAID: {
        OrderEvent.SHIP: OrderState.SHIPPED,
    },
    OrderState.SHIPPED: {
        OrderEvent.DELIVER: OrderState.DELIVERED,
    },
}
```

Read one entry as:

```text
current state = CREATED
event          = PAY
next state     = PAID
```

or:

```text
(CREATED, PAY) → PAID
```

This table is valuable because the legal workflow is visible in one place.

---

# 33. Building a Simple State Machine

Here is a small, complete implementation:

```python
from enum import StrEnum


class OrderState(StrEnum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderEvent(StrEnum):
    PAY = "pay"
    SHIP = "ship"
    DELIVER = "deliver"
    CANCEL = "cancel"


TRANSITIONS = {
    OrderState.CREATED: {
        OrderEvent.PAY: OrderState.PAID,
        OrderEvent.CANCEL: OrderState.CANCELLED,
    },
    OrderState.PAID: {
        OrderEvent.SHIP: OrderState.SHIPPED,
    },
    OrderState.SHIPPED: {
        OrderEvent.DELIVER: OrderState.DELIVERED,
    },
}


class Order:
    def __init__(self) -> None:
        self.state = OrderState.CREATED

    def apply(self, event: OrderEvent) -> OrderState:
        allowed_events = TRANSITIONS.get(self.state, {})

        if event not in allowed_events:
            raise ValueError(
                f"Cannot apply {event.value!r} while in {self.state.value!r}"
            )

        self.state = allowed_events[event]
        return self.state


order = Order()

print(order.state)
print(order.apply(OrderEvent.PAY))
print(order.apply(OrderEvent.SHIP))
print(order.apply(OrderEvent.DELIVER))
```

Expected output:

```text
created
paid
shipped
delivered
```

The implementation is deliberately small:

- `OrderState` defines states.
- `OrderEvent` defines events.
- `TRANSITIONS` defines legal moves.
- `Order.state` stores current state.
- `apply()` validates and performs the transition.

---

# 34. Rejecting Invalid Transitions

A state machine is valuable partly because it rejects invalid behavior.

For the order above:

```python
order = Order()

try:
    order.apply(OrderEvent.SHIP)
except ValueError as exc:
    print(exc)
```

The important behavior is:

```text
CREATED + SHIP
```

is rejected.

Without transition validation, the system could jump directly from:

```text
CREATED → SHIPPED
```

which violates the domain.

### Production principle

Fail clearly when an invalid transition is requested.

Do not silently ignore the event unless ignoring it is explicitly part of the domain contract.

---

# 35. Terminal States

Some states are terminal:

```text
DELIVERED
CANCELLED
```

Normally, an order should not leave those states.

The transition table naturally enforces that:

```python
OrderState.DELIVERED not in TRANSITIONS
OrderState.CANCELLED not in TRANSITIONS
```

Then:

```python
order = Order()

for event in (
    OrderEvent.PAY,
    OrderEvent.SHIP,
    OrderEvent.DELIVER,
):
    order.apply(event)

print(order.state)
```

Output:

```text
delivered
```

Any later event is rejected because `DELIVERED` has no outgoing transitions.

---

# 36. Invariants

An **invariant** is a condition that should remain true.

Examples:

- a delivered order cannot become created;
- a cancelled order cannot become shipped;
- a completed job cannot restart;
- a payment should not be captured twice through the same transition;
- a failed terminal workflow cannot silently become completed.

The state machine makes invariants explicit.

A useful design exercise is:

```text
For each state:
    What must always be true?
```

and:

```text
For each event:
    What transitions are legal?
```

---

# 37. Transition Tables as Documentation

A transition table is not only executable data.

It can serve as documentation.

```python
TRANSITIONS = {
    OrderState.CREATED: {
        OrderEvent.PAY: OrderState.PAID,
        OrderEvent.CANCEL: OrderState.CANCELLED,
    },
    OrderState.PAID: {
        OrderEvent.SHIP: OrderState.SHIPPED,
    },
    OrderState.SHIPPED: {
        OrderEvent.DELIVER: OrderState.DELIVERED,
    },
}
```

An engineer can inspect the table and immediately see the domain lifecycle.

This makes the rules:

- visible;
- testable;
- reviewable;
- auditable;
- easier to visualize.

The trade-off is that complex business conditions may not fit cleanly into a simple dictionary.

---

# 38. State Machine with Domain Methods

Another style uses domain methods:

```python
from enum import StrEnum


class OrderState(StrEnum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order:
    def __init__(self) -> None:
        self.state = OrderState.CREATED

    def pay(self) -> None:
        if self.state != OrderState.CREATED:
            raise ValueError("Only a created order can be paid")
        self.state = OrderState.PAID

    def ship(self) -> None:
        if self.state != OrderState.PAID:
            raise ValueError("Only a paid order can be shipped")
        self.state = OrderState.SHIPPED
```

This style can be expressive:

```python
order.pay()
order.ship()
```

The trade-off is that transition rules may become scattered across methods in a larger workflow.

A transition table centralizes rules.

A domain method can make business intent more readable.

Neither design is universally superior.

---

# 39. State Machine with `match`

For smaller workflows, `match` can represent transitions directly:

```python
from enum import StrEnum


class State(StrEnum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"


class Event(StrEnum):
    PAY = "pay"
    SHIP = "ship"


def transition(state: State, event: Event) -> State:
    match (state, event):
        case (State.CREATED, Event.PAY):
            return State.PAID
        case (State.PAID, Event.SHIP):
            return State.SHIPPED
        case _:
            raise ValueError(
                f"Invalid transition: {state.value} + {event.value}"
            )
```

This is explicit and readable for a modest number of transitions.

As the transition set becomes large, a table can be easier to inspect and test.

---

# 40. Representing Transitions as Data

More advanced systems may represent transitions explicitly:

```python
from dataclasses import dataclass
from enum import StrEnum


class OrderState(StrEnum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"


class OrderEvent(StrEnum):
    PAY = "pay"
    SHIP = "ship"


@dataclass(frozen=True)
class Transition:
    source: OrderState
    event: OrderEvent
    target: OrderState


TRANSITIONS = (
    Transition(
        source=OrderState.CREATED,
        event=OrderEvent.PAY,
        target=OrderState.PAID,
    ),
    Transition(
        source=OrderState.PAID,
        event=OrderEvent.SHIP,
        target=OrderState.SHIPPED,
    ),
)
```

Because the transition itself is data, you can more easily attach:

- audit information;
- labels;
- metrics;
- visualization metadata;
- tests;
- policy information.

This is useful when a workflow becomes more than a tiny conditional.

Do not introduce this abstraction just because it is possible.

---

# 41. State Transition vs Side Effect

This distinction is critical in production engineering.

A state machine answers:

> What state is the workflow in?

A side effect answers:

> What external operation should happen?

Example:

```text
State:
EMBEDDING

Side effect:
embedding_provider.embed(document)
```

These are related but not identical.

A good conceptual architecture is:

```text
event arrives
   ↓
validate current state
   ↓
decide transition
   ↓
perform carefully designed side effect
   ↓
record resulting state
```

The exact order depends on the system's consistency guarantees.

Do not put every external operation directly into the state definition itself.

---

# 42. Why Side Effects Make State Machines Harder

Suppose a payment workflow does:

```text
capture payment
update state to PAID
```

The payment succeeds, but the state write fails.

Now the external world says:

```text
payment captured
```

while your stored state may still say:

```text
CREATED
```

The reverse order has a different failure mode.

This is why state machines and side effects should be designed together but kept conceptually separate.

A state transition is not automatically a transaction across every external system.

---

# 43. Persistence

A state machine can exist entirely in memory:

```python
job.state = JobState.RUNNING
```

But production workflows often outlive one process.

Then state may be persisted:

```text
database row
    job_id
    state
    retry_count
    updated_at
```

or another durable store.

The important question becomes:

> What information must survive a process restart?

For long-running workflows, the answer often includes:

- current state;
- identifiers;
- retry count;
- timestamps;
- relevant error information;
- transition history;
- version information.

---

# 44. State Reconstruction

A workflow can sometimes reconstruct state from a history of events:

```text
CREATED
  |
PAY
  v
PAID
  |
SHIP
  v
SHIPPED
```

An event history can be useful for:

- debugging;
- auditing;
- recovery;
- understanding how the current state was reached.

But maintaining an event history is a larger design decision.

This chapter only establishes the foundational idea:

> Current state and state-transition history are related but different data.

---

# 45. Idempotency and Duplicate Events

Real systems often receive duplicate requests or events.

Suppose:

```text
PAID + PAY
```

arrives twice.

A good state machine must define what that means.

Possible domain policies include:

1. reject the second `PAY`;
2. treat it as a harmless duplicate;
3. return the existing result;
4. record the duplicate for auditing.

There is no universal answer.

The important engineering principle is:

> Duplicate events must have an intentional meaning.

Do not let retry behavior accidentally create duplicate business effects.

---

# 46. Retry and Failure States

A job workflow may look like:

```text
QUEUED
   ↓
RUNNING
   ├──────────────→ COMPLETED
   │
   └→ RETRYING → RUNNING
                     │
                     └→ FAILED
```

Possible states:

```python
from enum import StrEnum


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
```

The state machine makes retries visible.

It can also store:

```python
retry_count = 2
```

and enforce:

```text
retry_count < maximum_retries
```

before allowing another retry.

### Transient vs permanent failure

A transient failure may be retried:

```text
temporary network failure
```

A permanent failure may not:

```text
invalid input
```

Do not treat every exception as a retryable state.

---

# 47. Retry State vs Exception

An exception is a runtime event:

```python
raise TimeoutError("provider timed out")
```

A failure state is an application-level representation:

```text
JobState.FAILED
```

These are not the same thing.

A possible flow is:

```text
provider timeout
   ↓
catch/classify failure
   ↓
decide whether retryable
   ↓
state = RETRYING or FAILED
```

This gives operational systems a durable vocabulary for failure.

---

# 48. Background Workers

State machines are useful when work proceeds outside a single synchronous function call.

Example:

```text
QUEUED
   ↓
RUNNING
   ↓
COMPLETED
```

A worker may process the job later.

If the worker crashes, another worker can inspect:

```text
current state
retry count
last update
```

and make a recovery decision.

Explicit state makes long-running workflows easier to reason about than a collection of disconnected booleans.

---

# 49. State Machines in Data Pipelines

A document pipeline might use:

```text
RECEIVED
   ↓
VALIDATING
   ↓
CHUNKING
   ↓
EMBEDDING
   ↓
INDEXING
   ↓
COMPLETED
```

Failures can route to:

```text
FAILED
```

or:

```text
RETRYING
```

The state is operationally useful because engineers can answer:

> Where did this document stop?

rather than inspecting a vague `status = "bad"` field.

---

# 50. State Machines in Model Inference Workflows

A serving workflow might conceptually use:

```text
RECEIVED
   ↓
VALIDATING
   ↓
QUEUED
   ↓
RUNNING
   ↓
COMPLETED
```

Failure paths may include:

```text
RUNNING
   ↓
FAILED
   ↓
RETRYING
   ↓
RUNNING
```

This can support:

- metrics by state;
- retry policies;
- operational alerts;
- debugging;
- SLA analysis.

The Enum defines the vocabulary; the state machine defines legal movement.

---

# 51. Agent Execution States

Agentic systems can also have explicit application state.

For example:

```text
CREATED
   ↓
PLANNING
   ↓
TOOL_CALL
   ↓
OBSERVING
   ↓
DECIDING
   ↓
COMPLETED
```

Failure:

```text
TOOL_CALL
   ↓
FAILED
   ↓
RETRYING
   ↓
TOOL_CALL
```

The purpose is not to force every agent implementation into a rigid finite-state machine.

The purpose is to make lifecycle boundaries explicit when the workflow has real operational states.

---

# 52. Model Output Is Not Application State

Suppose a model returns:

```text
"continue"
```

That is model output.

It does not automatically become:

```python
AgentState.RUNNING
```

A production application should maintain explicit application state:

```text
model output
   ↓
decision/policy layer
   ↓
state transition
```

This separation helps prevent arbitrary model text from becoming the source of truth for system lifecycle.

---

# 53. Enums for Model Providers

A finite provider vocabulary is a natural Enum use case:

```python
from enum import StrEnum


class ModelProvider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
```

This can support routing decisions:

```python
def provider_name(provider: ModelProvider) -> str:
    return provider.value
```

Instead of repeating:

```python
"openai"
"anthropic"
"local"
```

throughout the codebase.

The Enum does not implement provider behavior. It only models the finite choice.

---

# 54. Enums for Pipeline States

A pipeline can use:

```python
from enum import StrEnum


class PipelineState(StrEnum):
    CREATED = "created"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

Now logs and metrics can consistently report:

```python
print(PipelineState.PROCESSING.value)
```

which yields:

```text
processing
```

The vocabulary becomes explicit and consistent across the pipeline.

---

# 55. Enums + Typing

Enums become even more useful when combined with type annotations.

```python
from enum import StrEnum


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobEvent(StrEnum):
    START = "start"
    COMPLETE = "complete"
    FAIL = "fail"


def transition(
    state: JobState,
    event: JobEvent,
) -> JobState:
    if state == JobState.QUEUED and event == JobEvent.START:
        return JobState.RUNNING

    if state == JobState.RUNNING and event == JobEvent.COMPLETE:
        return JobState.COMPLETED

    if state == JobState.RUNNING and event == JobEvent.FAIL:
        return JobState.FAILED

    raise ValueError(f"Invalid transition: {state} + {event}")
```

The function signature communicates:

```text
state must be JobState
event must be JobEvent
result is JobState
```

The previous typing chapter established the deeper static typing concepts; here we are applying them to state modeling.

---

# 56. Enum Comparison Checklist

When reading Enum code, ask:

1. Is this variable a member or a raw value?
2. Should comparison use the member?
3. Should serialization use `.value`?
4. Is `.name` needed for diagnostics or lookup?
5. Does the code require string or integer compatibility?
6. Is this a single state or a combination of independent flags?

Examples:

```python
status == Status.PENDING
```

is an internal domain comparison.

Whereas:

```python
status.value == "pending"
```

is a comparison against the external representation.

---

# 57. Testing Enums

Enums are simple enough that tests should usually focus on behavior rather than implementation details.

### Member/value test

```python
from enum import StrEnum


class Status(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"


def test_status_values() -> None:
    assert Status.PENDING.value == "pending"
    assert Status.COMPLETED.value == "completed"
```

### Lookup test

```python
def test_lookup_by_value() -> None:
    assert Status("pending") is Status.PENDING
```

### Invalid value

```python
import pytest
```

The above import requires pytest, so a dependency-free test can instead use:

```python
def test_invalid_value() -> None:
    try:
        Status("unknown")
    except ValueError:
        return
    raise AssertionError("Expected ValueError")
```

In a real project using pytest, the pytest form is usually cleaner:

```python
import pytest


def test_invalid_status_value() -> None:
    with pytest.raises(ValueError):
        Status("unknown")
```

The point is to verify the contract.

---

# 58. Testing State Machines

The most valuable state-machine tests often cover transitions.

```python
def test_created_can_be_paid() -> None:
    order = Order()

    result = order.apply(OrderEvent.PAY)

    assert result == OrderState.PAID
```

Invalid transitions are equally important:

```python
def test_created_cannot_be_shipped() -> None:
    order = Order()

    try:
        order.apply(OrderEvent.SHIP)
    except ValueError:
        return

    raise AssertionError("Expected invalid transition to fail")
```

### Terminal-state test

```python
def test_delivered_is_terminal() -> None:
    order = Order()

    order.apply(OrderEvent.PAY)
    order.apply(OrderEvent.SHIP)
    order.apply(OrderEvent.DELIVER)

    try:
        order.apply(OrderEvent.CANCEL)
    except ValueError:
        return

    raise AssertionError("Expected terminal state to reject event")
```

---

# 59. Table-Driven Transition Tests

Transition tables are especially easy to test systematically.

```python
CASES = [
    (OrderState.CREATED, OrderEvent.PAY, OrderState.PAID),
    (OrderState.CREATED, OrderEvent.CANCEL, OrderState.CANCELLED),
    (OrderState.PAID, OrderEvent.SHIP, OrderState.SHIPPED),
    (OrderState.SHIPPED, OrderEvent.DELIVER, OrderState.DELIVERED),
]
```

A test can iterate over them:

```python
def apply_transition(
    state: OrderState,
    event: OrderEvent,
) -> OrderState:
    allowed = TRANSITIONS.get(state, {})

    if event not in allowed:
        raise ValueError("Invalid transition")

    return allowed[event]


def test_transition_table() -> None:
    for state, event, expected in CASES:
        assert apply_transition(state, event) == expected
```

This style makes transition coverage visible.

---

# 60. State/Event Matrix

A matrix can document both allowed and forbidden transitions:

| Current State | `PAY` | `SHIP` | `DELIVER` | `CANCEL` |
|---|---|---|---|---|
| `CREATED` | `PAID` | invalid | invalid | `CANCELLED` |
| `PAID` | invalid | `SHIPPED` | invalid | invalid |
| `SHIPPED` | invalid | invalid | `DELIVERED` | invalid |
| `DELIVERED` | invalid | invalid | invalid | invalid |
| `CANCELLED` | invalid | invalid | invalid | invalid |

This is valuable because it exposes gaps before the code runs.

For a small finite workflow, a transition matrix can be excellent design documentation.

---

# 61. Transition Invariants

Suppose the invariant is:

```text
DELIVERED is terminal
```

Then this should always fail:

```python
DELIVERED + PAY
DELIVERED + SHIP
DELIVERED + DELIVER
DELIVERED + CANCEL
```

A test strategy can explicitly assert this.

A robust state machine test suite should ask:

```text
Can any invalid transition reach an impossible state?
```

rather than merely checking the happy path.

---

# 62. Observability

A production state transition is often worth logging.

Useful fields include:

```text
entity_id
previous_state
event
next_state
timestamp
actor/source
request_id
error
retry_count
```

For example:

```python
record = {
    "entity_id": "job-42",
    "previous_state": "running",
    "event": "complete",
    "next_state": "completed",
    "retry_count": 0,
}
```

The point is not the exact logging format.

The point is to make lifecycle movement observable.

This can greatly reduce debugging time.

---

# 63. Auditing

State history can provide an operational trail:

```text
10:00 CREATED
10:01 QUEUED
10:02 RUNNING
10:03 RETRYING
10:04 RUNNING
10:05 COMPLETED
```

This can answer questions such as:

- when did the job start?
- how many retries happened?
- which transition occurred before failure?
- where did time accumulate?

Auditing can be important in operational or regulated workflows.

This chapter does not attempt to teach a complete event-sourcing architecture. It teaches the foundational value of explicit lifecycle history.

---

# 64. Concurrency Concerns

State machines can become incorrect when multiple workers update the same entity.

Suppose two workers both read:

```text
state = PENDING
```

Worker A does:

```text
PENDING → APPROVED
```

Worker B does:

```text
PENDING → CANCELLED
```

If both writes succeed without coordination, one update may overwrite the other.

This is a lost-update problem.

Conceptual solutions include:

- locking;
- optimistic concurrency;
- version numbers;
- atomic conditional updates.

Example conceptual version:

```python
if current_version != expected_version:
    raise RuntimeError("State changed concurrently")
```

Concurrency control belongs to the persistence/coordination layer as well as the state-machine logic.

---

# 65. State + Version

A useful production idea is to store:

```text
state
version
```

For example:

```python
job.state = JobState.RUNNING
job.version = 7
```

A transition can require:

```text
expected version = 7
```

and update atomically to:

```text
state = COMPLETED
version = 8
```

The exact implementation depends on the persistence system, but the conceptual principle is broadly useful:

> A valid transition in your Python code is not enough if another worker can change the state at the same time.

---

# 66. Common Enum Mistake: Confusing `.name` and `.value`

Bad:

```python
class Status(StrEnum):
    PENDING = "pending"


external_value = Status.PENDING.name
```

That produces:

```text
PENDING
```

If an API expects:

```text
pending
```

this is wrong.

Correct:

```python
external_value = Status.PENDING.value
```

Use:

- `.name` for the declared Enum identifier;
- `.value` for the associated value.

---

# 67. Common Enum Mistake: Comparing the Wrong Thing

Bad:

```python
if status == "pending":
    ...
```

when:

```python
status: Status
```

is an internal Enum member.

Correct:

```python
if status == Status.PENDING:
    ...
```

If you intentionally operate at the external boundary:

```python
if status.value == "pending":
    ...
```

The key question is:

> What representation should exist at this point in the architecture?

---

# 68. Common Enum Mistake: Changing External Values Carelessly

Suppose:

```python
class Status(StrEnum):
    PENDING = "pending"
```

Later someone changes it to:

```python
class Status(StrEnum):
    PENDING = "waiting"
```

This may break:

- persisted records;
- API clients;
- event consumers;
- configuration;
- tests;
- dashboards.

If the value is an external contract, treat it like a public API.

---

# 69. Common Enum Mistake: Unnecessary `IntEnum`

Bad reasoning:

> "`IntEnum` is more powerful, so I should use it."

Better reasoning:

> "Does this domain genuinely need integer compatibility?"

Use ordinary `Enum` for a domain state:

```python
class State(Enum):
    READY = "ready"
```

Use `IntEnum` for an established integer contract:

```python
class ExitCode(IntEnum):
    OK = 0
    ERROR = 1
```

Choose based on requirements.

---

# 70. Common State-Machine Mistake: No Explicit Transition Rule

Bad:

```python
if event == "pay":
    state = "paid"
```

When this logic appears in many places, the valid workflow becomes difficult to discover.

Better:

```python
TRANSITIONS = {
    OrderState.CREATED: {
        OrderEvent.PAY: OrderState.PAID,
    },
}
```

The rule is centralized.

For very small programs, an `if` may still be perfectly appropriate. The concern is duplicated and uncontrolled lifecycle logic.

---

# 71. Common State-Machine Mistake: Silently Accepting Invalid Events

Bad:

```python
def apply(event):
    if event not in allowed_events:
        return
```

This can hide bugs.

Better:

```python
def apply(event):
    if event not in allowed_events:
        raise ValueError("Invalid transition")
```

Whether the error should be a custom domain exception or another type is a separate design decision.

The core principle is:

> Invalid state changes should be visible.

---

# 72. Common State-Machine Mistake: Too Many States

State modeling can also be overdone.

A workflow like:

```text
CREATED
VALIDATING
VALIDATION_STARTED
VALIDATION_HALF_COMPLETE
VALIDATION_FINISHING
VALIDATED
```

may contain implementation details rather than meaningful domain states.

Ask:

> Does this state matter to the domain, operations, recovery, or lifecycle?

If not, it may belong in internal execution logic rather than the public state model.

---

# 73. Common State-Machine Mistake: State Explosion

Suppose you have:

- payment status;
- shipping status;
- fraud status;
- fulfillment status;
- notification status.

Combining every possible state into one mega-Enum can create enormous complexity.

Sometimes multiple smaller state dimensions are better:

```text
PaymentState
ShippingState
FraudState
```

rather than:

```text
PAID_SHIPPED_FRAUD_APPROVED_NOTIFICATION_SENT
```

The state model should reflect actual domain structure.

---

# 74. Common State-Machine Mistake: Hidden Side Effects

Bad:

```python
def set_state(state):
    self.state = state
    send_email()
    charge_card()
    create_index()
```

Now merely changing state triggers unrelated external behavior.

This can make:

- testing harder;
- retries dangerous;
- failures ambiguous;
- debugging difficult.

Prefer explicit orchestration where appropriate:

```text
validate event
    ↓
transition
    ↓
planned side effect
    ↓
record outcome
```

The exact design depends on consistency requirements.

---

# 75. Common State-Machine Mistake: No Terminal-State Policy

If `COMPLETED` can accidentally return to `RUNNING`, the workflow may become impossible to reason about.

Explicit terminal-state rules prevent accidental resurrection:

```python
TERMINAL_STATES = {
    JobState.COMPLETED,
    JobState.FAILED,
}
```

You can then make the policy visible in code and tests.

---

# 76. Debugging Enum Problems

A practical debugging workflow is:

### Step 1: Inspect the actual type

```python
print(type(status))
```

### Step 2: Inspect the member

```python
print(status)
```

### Step 3: Inspect the name and value

```python
print(status.name)
print(status.value)
```

### Step 4: Compare explicitly

```python
print(status == Status.PENDING)
print(status.value == "pending")
```

### Step 5: Check the boundary

Ask whether the value came from:

- API input;
- configuration;
- database;
- internal application logic.

Many Enum bugs are actually boundary-conversion bugs.

---

# 77. Debugging State Machines

When a transition behaves incorrectly, collect these facts:

```text
Current state:
Incoming event:
Expected next state:
Actual next state:
Transition rule:
External side effect:
Persisted state:
Retry count:
Version:
```

Then inspect the transition table or matching logic.

A minimal debug print might be:

```python
print(
    f"transition: {state.value} + {event.value} -> {next_state.value}"
)
```

In production, structured logging is often more useful than raw `print()` calls.

---

# 78. Debugging Challenge: Wrong Representation

Broken code:

```python
from enum import StrEnum


class Status(StrEnum):
    PENDING = "pending"


def send_status(status: Status) -> dict[str, str]:
    return {"status": status.name}
```

Question:

> What representation will the external system receive?

The answer is:

```text
PENDING
```

rather than:

```text
pending
```

Correct boundary conversion:

```python
def send_status(status: Status) -> dict[str, str]:
    return {"status": status.value}
```

---

# 79. Debugging Challenge: Invalid Transition

Broken code:

```python
TRANSITIONS = {
    OrderState.CREATED: {
        OrderEvent.PAY: OrderState.PAID,
        OrderEvent.CANCEL: OrderState.CANCELLED,
    },
    OrderState.PAID: {
        OrderEvent.DELIVER: OrderState.DELIVERED,
    },
}
```

Question:

> What transition has probably been modeled incorrectly?

The domain says:

```text
PAID → SHIPPED → DELIVERED
```

but the table incorrectly allows:

```text
PAID + DELIVER → DELIVERED
```

The debugging process is to compare the transition table with the domain specification.

---

# 80. Debugging Challenge: Retry Loop

Consider:

```python
state = JobState.RETRYING

while state != JobState.COMPLETED:
    state = JobState.RETRYING
```

Question:

> What is wrong?

The state never changes.

A retry workflow needs:

- an attempt;
- a success/failure result;
- a retry counter;
- an explicit transition;
- a terminal path.

State machines do not eliminate faulty control flow. They make lifecycle decisions more explicit.

---

# 81. Production-Oriented Design Principles

Use these rules as a practical checklist.

### 81.1 Use an Enum when the vocabulary is finite

Good:

```python
class Environment(StrEnum):
    DEV = "dev"
    PROD = "prod"
```

### 81.2 Keep external values stable

Good:

```python
COMPLETED = "completed"
```

when `"completed"` is an external contract.

### 81.3 Separate state from event

Good:

```text
state = RUNNING
event = COMPLETE
```

### 81.4 Make invalid transitions explicit

Good:

```python
raise ValueError("Invalid transition")
```

### 81.5 Keep side effects separate from transition rules

This improves testability.

### 81.6 Protect terminal states

Terminal states should not accidentally gain hidden outgoing transitions.

### 81.7 Test the transition matrix

Happy paths are not enough.

### 81.8 Make operational state observable

Useful fields:

```text
previous state
event
next state
timestamp
retry count
error
```

### 81.9 Consider persistence and concurrency

A valid in-memory transition is not automatically a safe distributed transition.

### 81.10 Use the simplest state model that captures the actual lifecycle

Do not create a workflow framework for a three-line problem.

---

# 82. When Not to Use an Enum

Do not use an Enum merely because a finite-looking value exists.

A plain string may be enough when:

- the value is naturally free-form;
- the set is intentionally open;
- no stable finite vocabulary exists.

A constant may be enough when:

- one named configuration value is needed;
- no domain enumeration is necessary.

A boolean may be better when:

- exactly two independent conditions exist.

A class may be better when:

- the concept has substantial data and behavior.

A state machine may be unnecessary when:

- there are only one or two simple conditions;
- transition rules are trivial;
- persistence, recovery, or lifecycle semantics do not matter.

---

# 83. When a State Machine Is Worthwhile

A dedicated state-machine design becomes more valuable when several of these are true:

- many explicit states;
- many possible events;
- invalid transitions matter;
- retries exist;
- terminal states matter;
- lifecycle spans multiple processes;
- state must be persisted;
- state transitions must be audited;
- operational observability matters;
- concurrency must be coordinated;
- domain invariants are significant.

Example:

```text
payment processing
```

often benefits from explicit lifecycle rules.

A simple local function:

```python
if active:
    ...
```

may not.

---

# 84. State Machine vs Simple `if`

Consider:

```python
if active:
    process()
```

That does not necessarily need a state machine.

Now consider:

```text
QUEUED
RUNNING
RETRYING
COMPLETED
FAILED
CANCELLED
```

with:

- retries;
- persisted state;
- invalid transitions;
- duplicate events;
- audit history.

Now explicit state-machine modeling becomes much more reasonable.

The architecture should grow with domain complexity.

---

# 85. State Machine vs Workflow Engine

A Python state machine can model:

```text
state + event + transition rules
```

A workflow engine may additionally provide:

- durable execution;
- retries;
- scheduling;
- distributed workers;
- recovery;
- orchestration;
- operational dashboards.

Do not confuse the two.

A state machine is a domain/control-flow abstraction.

A workflow engine is usually a much larger runtime platform.

---

# 86. Production Example: AI Document Processing State Machine

Now combine the concepts.

## 86.1 Domain

Imagine a document-processing job:

```text
CREATED
   ↓
VALIDATING
   ↓
PROCESSING
   ↓
EMBEDDING
   ↓
INDEXING
   ↓
COMPLETED
```

Failures:

```text
any processing state
      ↓
    FAILED
```

Retry path:

```text
FAILED
  ↓ RETRY
RETRYING
  ↓
PROCESSING
```

## 86.2 States

```python
from enum import StrEnum


class DocumentState(StrEnum):
    CREATED = "created"
    VALIDATING = "validating"
    PROCESSING = "processing"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
```

## 86.3 Events

```python
class DocumentEvent(StrEnum):
    START = "start"
    VALIDATION_OK = "validation_ok"
    PROCESS = "process"
    EMBED = "embed"
    INDEX = "index"
    COMPLETE = "complete"
    FAIL = "fail"
    RETRY = "retry"
```

## 86.4 Transition rules

```python
TRANSITIONS = {
    DocumentState.CREATED: {
        DocumentEvent.START: DocumentState.VALIDATING,
    },
    DocumentState.VALIDATING: {
        DocumentEvent.VALIDATION_OK: DocumentState.PROCESSING,
        DocumentEvent.FAIL: DocumentState.FAILED,
    },
    DocumentState.PROCESSING: {
        DocumentEvent.EMBED: DocumentState.EMBEDDING,
        DocumentEvent.FAIL: DocumentState.FAILED,
    },
    DocumentState.EMBEDDING: {
        DocumentEvent.INDEX: DocumentState.INDEXING,
        DocumentEvent.FAIL: DocumentState.FAILED,
    },
    DocumentState.INDEXING: {
        DocumentEvent.COMPLETE: DocumentState.COMPLETED,
        DocumentEvent.FAIL: DocumentState.FAILED,
    },
    DocumentState.FAILED: {
        DocumentEvent.RETRY: DocumentState.RETRYING,
    },
    DocumentState.RETRYING: {
        DocumentEvent.PROCESS: DocumentState.PROCESSING,
        DocumentEvent.FAIL: DocumentState.FAILED,
    },
}
```

The table tells us the allowed workflow.

---

# 87. Production Example: State Machine Class

```python
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class DocumentState(StrEnum):
    CREATED = "created"
    VALIDATING = "validating"
    PROCESSING = "processing"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentEvent(StrEnum):
    START = "start"
    VALIDATION_OK = "validation_ok"
    PROCESS = "process"
    EMBED = "embed"
    INDEX = "index"
    COMPLETE = "complete"
    FAIL = "fail"
    RETRY = "retry"


TRANSITIONS = {
    DocumentState.CREATED: {
        DocumentEvent.START: DocumentState.VALIDATING,
    },
    DocumentState.VALIDATING: {
        DocumentEvent.VALIDATION_OK: DocumentState.PROCESSING,
        DocumentEvent.FAIL: DocumentState.FAILED,
    },
    DocumentState.PROCESSING: {
        DocumentEvent.EMBED: DocumentState.EMBEDDING,
        DocumentEvent.FAIL: DocumentState.FAILED,
    },
    DocumentState.EMBEDDING: {
        DocumentEvent.INDEX: DocumentState.INDEXING,
        DocumentEvent.FAIL: DocumentState.FAILED,
    },
    DocumentState.INDEXING: {
        DocumentEvent.COMPLETE: DocumentState.COMPLETED,
        DocumentEvent.FAIL: DocumentState.FAILED,
    },
    DocumentState.FAILED: {
        DocumentEvent.RETRY: DocumentState.RETRYING,
    },
    DocumentState.RETRYING: {
        DocumentEvent.PROCESS: DocumentState.PROCESSING,
    },
}


@dataclass
class DocumentJob:
    document_id: str
    state: DocumentState = DocumentState.CREATED
    retry_count: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)

    def transition(self, event: DocumentEvent) -> DocumentState:
        allowed = TRANSITIONS.get(self.state, {})

        if event not in allowed:
            raise ValueError(
                f"Invalid transition: "
                f"{self.state.value} + {event.value}"
            )

        previous_state = self.state
        self.state = allowed[event]

        self.history.append(
            {
                "previous": previous_state.value,
                "event": event.value,
                "next": self.state.value,
            }
        )

        return self.state
```

This example combines:

- `Enum` state vocabulary;
- `Enum` event vocabulary;
- transition table;
- validation;
- history;
- explicit retry state;
- type annotations;
- a domain object.

It does **not** contain external API calls, embedding calls, or database access.

That separation is intentional.

---

# 88. Production Example: Separate Side Effects

A workflow orchestrator can decide what happens around a transition:

```python
def handle_embedding(job: DocumentJob, text: str) -> list[float]:
    # The provider call is a side effect.
    embedding = fake_embed(text)

    job.transition(DocumentEvent.INDEX)

    return embedding
```

The state machine itself does not need to know how embeddings are computed.

A cleaner architecture is often:

```text
State machine
    ↓
decides current lifecycle
    ↓
orchestration/service layer
    ↓
external side effect
    ↓
state transition
```

This improves:

- testing;
- replaceability;
- observability;
- failure analysis.

---

# 89. Production Example: Failure Handling

A simple retry policy might look like:

```python
MAX_RETRIES = 3


def record_failure(job: DocumentJob) -> None:
    job.transition(DocumentEvent.FAIL)


def retry_if_possible(job: DocumentJob) -> bool:
    if job.state != DocumentState.FAILED:
        return False

    if job.retry_count >= MAX_RETRIES:
        return False

    job.retry_count += 1
    job.transition(DocumentEvent.RETRY)
    return True
```

This deliberately keeps retry policy visible.

A real distributed system may additionally need:

- exponential backoff;
- jitter;
- timeouts;
- idempotency keys;
- durable scheduling;
- dead-letter handling;
- concurrency controls.

Those are broader systems concerns.

The state-machine foundation still matters because it defines the domain lifecycle.

---

# 90. Production Example: Terminal States

Suppose:

```python
TERMINAL_STATES = {
    DocumentState.COMPLETED,
    DocumentState.FAILED,
}
```

Now you can explicitly reason about:

```python
def is_terminal(state: DocumentState) -> bool:
    return state in TERMINAL_STATES
```

But note that `FAILED` in this design may be temporarily recoverable through `RETRY`.

Therefore you must define what "terminal" means in your domain.

One possible design is:

- `COMPLETED` — final;
- `FAILED` — final after retry budget exhausted;
- `RETRYING` — non-terminal.

The actual domain contract should decide this.

---

# 91. Production Example: Transition History

The `history` field can record:

```python
job = DocumentJob("doc-42")

job.transition(DocumentEvent.START)
job.transition(DocumentEvent.VALIDATION_OK)
job.transition(DocumentEvent.EMBED)
job.transition(DocumentEvent.INDEX)
job.transition(DocumentEvent.COMPLETE)

for item in job.history:
    print(item)
```

Conceptually:

```text
created --start--> validating
validating --validation_ok--> processing
processing --embed--> embedding
embedding --index--> indexing
indexing --complete--> completed
```

The history is useful for:

- debugging;
- audit trails;
- operational metrics;
- reproducing lifecycle behavior.

---

# 92. Applied AI Engineering: RAG Ingestion

A RAG-style ingestion workflow can be represented conceptually as:

```text
RECEIVED
   ↓
VALIDATING
   ↓
CHUNKING
   ↓
EMBEDDING
   ↓
INDEXING
   ↓
READY
```

Failures may be:

```text
FAILED
```

Retries may return to a safe earlier stage:

```text
EMBEDDING
   ↓
RETRYING
   ↓
EMBEDDING
```

The important architecture idea is not the names themselves.

It is that each stage has a clear lifecycle and failure boundary.

---

# 93. Applied AI Engineering: Evaluation Jobs

An evaluation pipeline might use:

```text
CREATED
   ↓
QUEUED
   ↓
RUNNING
   ↓
AGGREGATING
   ↓
COMPLETED
```

or:

```text
RUNNING
   ↓
FAILED
   ↓
RETRYING
```

State becomes useful when many evaluations run simultaneously and operators need to know:

- how many are running;
- how many failed;
- which are waiting;
- which are retrying;
- which are complete.

---

# 94. Applied AI Engineering: Agent Tool Execution

A tool invocation may conceptually move through:

```text
REQUESTED
   ↓
VALIDATING
   ↓
RUNNING
   ↓
SUCCEEDED
```

or:

```text
RUNNING
   ↓
FAILED
   ↓
RETRYING
```

The model may suggest an action, but the application should still validate whether that action is permitted in the current state.

This is where explicit state machines can help make agent execution more deterministic.

---

# 95. Applied AI Engineering: Human Approval

A document or action may require approval:

```text
DRAFT
   ↓
PENDING_REVIEW
   ↓
APPROVED
   ↓
EXECUTED
```

or:

```text
PENDING_REVIEW
   ↓
REJECTED
```

The state machine makes approval boundaries explicit.

This is especially useful when workflows cross people, automated systems, and asynchronous processing.

---

# 96. Applied AI Engineering: Data Pipelines

A data-processing job might move through:

```text
EXTRACTING
   ↓
VALIDATING
   ↓
TRANSFORMING
   ↓
LOADING
   ↓
COMPLETED
```

with:

```text
FAILED
RETRYING
```

This supports a strong operational question:

> What stage owns the current failure?

Without explicit state, pipelines often collapse everything into:

```text
status = "failed"
```

which provides much less diagnostic information.

---

# 97. Enum Decision Framework

Use this guide.

| Choice | Problem it solves | Use when | Avoid when |
|---|---|---|---|
| Constant | One named value | A single stable value is enough | You need a finite vocabulary |
| String | Flexible textual data | Values may be open-ended | Valid set must be controlled |
| `Enum` | Finite symbolic vocabulary | Domain choices are explicit | Free-form values are required |
| `StrEnum` | Enum + string interoperability | String boundary compatibility matters | Project supports older Python without fallback |
| `IntEnum` | Enum + integer compatibility | Legacy integer API exists | Integer semantics are unnecessary |
| `Flag` | Combinable capabilities | Independent options can be combined | States are mutually exclusive |
| `IntFlag` | `Flag` + integer compatibility | Bitmasks/legacy integer APIs matter | No integer compatibility is needed |
| Boolean | Two-state condition | Exactly two values describe an independent fact | Several lifecycle states exist |
| State machine | Controlled lifecycle transitions | Valid/invalid transitions matter | Workflow is trivial |

---

# 98. When to Choose `Enum`

Ask:

> Is this a finite domain vocabulary?

Example:

```text
dev
staging
prod
```

Yes.

Then ask:

> Would explicit names and a controlled vocabulary improve the design?

If yes, an Enum is a reasonable candidate.

---

# 99. When to Choose `StrEnum`

Ask:

> Is this domain concept both an Enum and naturally represented as a string?

Examples:

```text
environment
provider
status
strategy
mode
```

`StrEnum` can be useful, especially at application boundaries.

But verify Python-version support first.

---

# 100. When to Choose `IntEnum`

Ask:

> Does existing code require actual integer compatibility?

Examples:

```text
exit codes
legacy protocol constants
integer status codes
```

If not, ordinary `Enum` often communicates the domain more cleanly.

---

# 101. When to Choose `Flag`

Ask:

> Are these independent capabilities that may be combined?

Good:

```text
READ
WRITE
EXECUTE
```

Less suitable:

```text
CREATED
PAID
SHIPPED
```

An order should normally be in one lifecycle state at a time.

---

# 102. When to Choose a State Machine

Use a state machine when the lifecycle itself is part of the domain.

A useful checklist:

```text
Are states explicit?
        ↓
Do events matter?
        ↓
Do allowed transitions matter?
        ↓
Do invalid transitions matter?
        ↓
Do retries/failures matter?
        ↓
Does persistence or observability matter?
```

The more "yes" answers you have, the stronger the case for explicit state-machine modeling.

---

# 103. Common Over-Engineering Path

It is easy to go from:

```python
status = "ready"
```

to an unnecessary framework containing:

- abstract transition classes;
- registries;
- plugins;
- metaclasses;
- multiple state-machine factories;
- complex event buses.

That may be inappropriate for a small program.

A reasonable progression is:

```text
simple string
    ↓
Enum
    ↓
Enum + if/elif
    ↓
Enum + transition table
    ↓
dedicated state-machine class
    ↓
larger workflow system
```

Move right only when the problem justifies it.

---

# 104. Production Architecture Scenario 1 — Payment Workflow

Imagine:

```text
CREATED
   ↓
AUTHORIZED
   ↓
CAPTURED
   ↓
SETTLED
```

Possible failure:

```text
AUTHORIZED
   ↓
FAILED
```

Questions a strong engineer should ask:

- What events cause each transition?
- Which states are terminal?
- Can capture be repeated?
- What happens after a timeout?
- What is persisted?
- How are duplicate requests handled?
- How are concurrent transitions prevented?
- Which external side effects occur?
- How is the transition observed?

The state machine is only one component of the overall architecture.

---

# 105. Production Architecture Scenario 2 — Background Job

Possible states:

```text
QUEUED
RUNNING
RETRYING
COMPLETED
FAILED
CANCELLED
```

Questions:

- Who owns transitions?
- Can two workers process the same job?
- What happens if the worker dies?
- How is retry count persisted?
- How is cancellation handled?
- Which failures are retryable?
- What is the maximum retry count?
- How is the current state exposed to operators?

---

# 106. Production Architecture Scenario 3 — AI Agent

Possible states:

```text
CREATED
PLANNING
TOOL_CALL
OBSERVING
DECIDING
COMPLETED
FAILED
```

Questions:

- Which state is persisted?
- What constitutes a tool-call failure?
- Can tool calls be retried?
- Is the model allowed to request every event?
- Which transitions are application-controlled?
- How are terminal states protected?
- How are repeated events handled?

A strong design keeps application state under deterministic control even when model output is probabilistic.

---

# 107. Production Architecture Scenario 4 — Multi-Provider Model Routing

Possible provider choices:

```python
class ModelProvider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
```

A routing layer can accept:

```python
provider: ModelProvider
```

This can reduce scattered string literals.

The Enum does not create the provider implementation.

The provider abstraction belongs elsewhere.

The Enum simply describes the finite selection.

---

# 108. Production Architecture Scenario 5 — Plugin Systems

A plugin system may have lifecycle states:

```text
DISCOVERED
LOADED
INITIALIZED
ACTIVE
FAILED
DISABLED
```

Events:

```text
LOAD
INITIALIZE
ACTIVATE
FAIL
DISABLE
```

A state machine can make plugin lifecycle rules explicit.

For example:

```text
DISCOVERED → INITIALIZED
```

may be invalid if loading is required first.

---

# 109. Production Architecture Scenario 6 — Human-in-the-Loop

A review workflow might be:

```text
CREATED
   ↓
PENDING_REVIEW
   ├── APPROVE → APPROVED
   └── REJECT → REJECTED
```

This is a classic finite-state lifecycle.

It can be especially valuable when the workflow must survive:

- browser refreshes;
- process restarts;
- delayed human responses;
- retries;
- reassignment.

---

# 110. Production Observability Checklist

For each important transition, consider recording:

```text
entity_id
event
previous_state
next_state
attempt_number
timestamp
source
request_id
error_type
error_message
```

This supports operational questions such as:

> Why is job-42 still retrying?

instead of forcing an engineer to infer the answer from unrelated logs.

---

# 111. Production Reliability Checklist

For a production state machine, ask:

```text
[ ] Are states explicit?
[ ] Are events explicit?
[ ] Are invalid transitions rejected?
[ ] Are terminal states protected?
[ ] Are retries bounded?
[ ] Are duplicate events defined?
[ ] Are side effects separated?
[ ] Is state persisted where necessary?
[ ] Is concurrency controlled?
[ ] Is transition history observable?
[ ] Are all critical transitions tested?
```

---

# 112. Progressive Exercises

The following exercises build from beginner to architecture-level reasoning.

Do not immediately look at the answer guidance. Try each exercise first.

## Level 1 — Enum Basics

### Exercise 1: Priority Enum

Create:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Requirements:

- use `Enum`;
- give each member a string value;
- print `.name`;
- print `.value`;
- iterate through all members.

**Hint:** Start with `class Priority(Enum):`.

---

### Exercise 2: Environment Enum

Create:

```text
DEV
STAGING
PROD
```

Requirements:

- use `StrEnum` if your supported Python version allows it;
- otherwise use `class Environment(str, Enum)`;
- convert `"prod"` into `Environment.PROD`;
- handle an invalid environment.

**Hint:** Member lookup by value uses call syntax.

---

## Level 2 — Lookup and Representation

### Exercise 3: Status Parser

Write:

```python
def parse_status(raw: str) -> Status:
    ...
```

The function should:

- return the appropriate Enum member;
- reject unknown values;
- keep the external string representation in `.value`.

**Hint:** `Status(raw)` performs lookup by value.

---

### Exercise 4: Name vs Value

Given:

```python
Status.PENDING
```

write code that prints:

```text
name = PENDING
value = pending
```

Then explain in your own words why `.name` and `.value` are different.

---

## Level 3 — Flags

### Exercise 5: Permissions

Create a `Flag`:

```text
READ
WRITE
DELETE
EXECUTE
```

Requirements:

- use `auto()`;
- combine at least two permissions;
- check whether a permission is included.

**Hint:** Use `|` to combine options.

---

## Level 4 — Basic State Machine

### Exercise 6: Traffic Light

States:

```text
RED
GREEN
YELLOW
```

Events:

```text
TIMER
```

Rules:

```text
RED + TIMER → GREEN
GREEN + TIMER → YELLOW
YELLOW + TIMER → RED
```

Requirements:

- Enum for state;
- Enum for event;
- transition table;
- invalid-transition protection.

---

## Level 5 — Order State Machine

### Exercise 7: Order Lifecycle

Implement:

```text
CREATED → PAID → SHIPPED → DELIVERED
```

and:

```text
CREATED → CANCELLED
```

Requirements:

- invalid transitions must raise an exception;
- `DELIVERED` must be terminal;
- `CANCELLED` must be terminal.

**Hint:** A dictionary keyed by current state is sufficient.

---

## Level 6 — Retryable Job

### Exercise 8: Job Lifecycle

States:

```text
QUEUED
RUNNING
RETRYING
COMPLETED
FAILED
```

Events:

```text
START
FAIL
RETRY
COMPLETE
```

Requirements:

- add a retry counter;
- allow at most three retries;
- represent permanent failure;
- reject invalid transitions.

---

## Level 7 — Applied AI Pipeline

### Exercise 9: Document Processing

Model:

```text
CREATED
VALIDATING
PROCESSING
EMBEDDING
INDEXING
COMPLETED
FAILED
```

Events:

```text
START
VALIDATION_OK
PROCESS
EMBED
INDEX
COMPLETE
FAIL
```

Requirements:

- transition table;
- terminal state;
- transition history;
- tests for valid and invalid paths.

---

## Level 8 — Architecture

### Exercise 10: Agent State Machine

Design an agent lifecycle:

```text
CREATED
PLANNING
TOOL_CALL
OBSERVING
DECIDING
COMPLETED
FAILED
```

Answer:

1. Which transitions are allowed?
2. Which events cause them?
3. Which states are terminal?
4. Which transitions may retry?
5. What should be persisted?
6. What should be logged?
7. Which states must be controlled by application code rather than model output?

Do not write a large framework.

The goal is to reason about lifecycle boundaries.

---

# 113. Exercise Answer Guidance

This section is deliberately concise. It is a self-check, not a replacement for your implementation.

## Exercise 1

Expected design:

```python
class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

The important concept is controlled vocabulary plus explicit values.

## Exercise 2

Use:

```python
Environment("prod")
```

for value lookup.

If using `StrEnum`, Python 3.11+ is required.

## Exercise 3

The core operation should be:

```python
from enum import StrEnum


class Status(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"


def parse_status(raw: str) -> Status:
    return Status(raw)


print(parse_status("pending"))
```

with an intentional policy for invalid input.

## Exercise 4

Expected distinction:

```text
.name  → declaration identifier
.value → associated domain/external value
```

## Exercise 5

Expected idea:

```python
read_write = Permission.READ | Permission.WRITE
```

Then:

```python
Permission.READ in read_write
```

should be true.

## Exercise 6

A compact transition table is enough.

## Exercise 7

Ensure:

```text
CREATED + PAY     → PAID
CREATED + CANCEL  → CANCELLED
PAID + SHIP       → SHIPPED
SHIPPED + DELIVER → DELIVERED
```

and reject all other transitions.

## Exercise 8

Retry count belongs to workflow state/data, not merely to the exception object.

## Exercise 9

Tests should include both:

```text
happy path
invalid transition path
```

and should verify terminal behavior.

## Exercise 10

A strong answer separates:

```text
model suggestion
      ↓
application policy
      ↓
event
      ↓
state transition
```

and treats persistence, retries, and observability as explicit production concerns.

---

# 114. Knowledge Checks

Answer these without looking at the previous sections.

## Basic

1. What is an Enum?
2. Why can magic strings become problematic?
3. What is the difference between an Enum member and its `.value`?
4. What is `.name`?
5. How do you look up an Enum member by value?
6. How do you look up an Enum member by name?
7. What does `auto()` do?
8. What does `@unique` check?
9. What is `StrEnum`?
10. What is `IntEnum`?

## Intermediate

11. What is the difference between `Enum` and `Flag`?
12. What is `IntFlag` used for?
13. What is an Enum alias?
14. Why might external Enum values need to remain stable?
15. Why is a boolean sometimes insufficient for modeling workflow state?
16. Why is `status == Status.PENDING` often clearer than `status == "pending"`?
17. Why is an Enum not itself a state machine?
18. What is a state?
19. What is an event?
20. What is a transition?

## Advanced

21. Explain `(current_state, event) → next_state`.
22. What is a terminal state?
23. What is an invariant?
24. Why should invalid transitions usually fail visibly?
25. Why should state transitions and side effects be conceptually separate?
26. What is idempotency?
27. Why can duplicate events be dangerous?
28. How can a state machine support retries?
29. Why is persistence relevant to long-running workflows?
30. What happens if two workers update the same state concurrently?
31. Why is a model output not necessarily application state?
32. How can state-transition history help production debugging?

---

# 115. Interview Questions

## Beginner

### 1. Why would you use an Enum instead of a string?

Strong reasoning should cover:

- finite vocabulary;
- discoverability;
- reduced typo risk;
- clearer domain modeling;
- explicit names and values.

It should also acknowledge that strings can still be appropriate when a value is genuinely open-ended.

### 2. What are `.name` and `.value`?

A strong answer distinguishes the declaration name from the associated value and explains why the distinction matters at API boundaries.

### 3. What is `IntEnum`?

Explain integer interoperability and why that compatibility can also introduce integer semantics.

---

## Intermediate

### 4. What is the difference between `Enum` and `Flag`?

Explain:

```text
Enum  → one symbolic member
Flag  → combinable independent options
```

### 5. What is a state machine?

A strong answer should mention:

- states;
- events;
- transitions;
- current state;
- transition validation.

### 6. State vs event?

Explain:

```text
PAID = state
PAY = event
```

### 7. How do you model transitions?

A good answer can provide:

```text
(current_state, event) → next_state
```

and a dictionary/table or equivalent logic.

---

## Advanced

### 8. Why are explicit transition tables useful?

Mention:

- visibility;
- testability;
- audibility;
- centralized rules;
- easier coverage analysis.

### 9. How would you test every transition?

A strong answer should discuss:

- table-driven tests;
- valid transitions;
- invalid transitions;
- terminal states;
- invariants.

### 10. How do you handle retries?

Discuss:

- retryable vs permanent failures;
- retry count;
- explicit retry state;
- backoff conceptually;
- idempotency;
- observability.

---

## Production

### 11. How would you design a payment state machine?

Discuss:

```text
states
events
transition rules
terminal states
idempotency
persistence
concurrency
side effects
auditing
```

### 12. How would you design an AI job state machine?

Discuss:

```text
QUEUED
RUNNING
RETRYING
COMPLETED
FAILED
CANCELLED
```

plus retry policy, worker failure, persistence, and duplicate event handling.

### 13. How would you handle duplicate transitions?

A strong answer should say the behavior must be explicitly defined. Possible policies include rejection, idempotent success, or returning an already-completed result.

### 14. How would you make state transitions observable?

Mention:

- previous state;
- event;
- next state;
- timestamps;
- identifiers;
- error;
- retry count.

### 15. How would you handle concurrent state updates?

Discuss:

- optimistic concurrency;
- version numbers;
- locks where appropriate;
- atomic conditional updates.

---

# 116. Architecture Scenarios

For each scenario, answer the design questions rather than jumping directly to implementation.

## Scenario A — Payment

Questions:

- What are the states?
- What are the events?
- Which transitions are legal?
- Which states are terminal?
- Which transitions are retryable?
- Which side effects occur?
- What is persisted?
- What must be idempotent?
- How are concurrent updates prevented?

---

## Scenario B — Order Processing

Questions:

- Can an order be cancelled after shipping?
- Can a delivered order be cancelled?
- Can payment occur twice?
- How are duplicate API requests represented?
- Which values cross the API boundary?

---

## Scenario C — Background ML Job

Questions:

- What happens after worker failure?
- When does a retry become permanent failure?
- How is retry count persisted?
- How is a stale worker prevented from overwriting new state?

---

## Scenario D — RAG Ingestion

Questions:

- What is the state after parsing succeeds?
- Can embedding be retried independently?
- Is indexing idempotent?
- What information is logged for a failed document?
- Which stages are terminal?

---

## Scenario E — AI Agent

Questions:

- What states are deterministic application states?
- Which events may originate from model suggestions?
- Which transitions require policy validation?
- Which tool calls can retry?
- What happens after repeated failure?
- What should be persisted so the workflow can resume?

---

# 117. Debugging Challenges

## Challenge 1 — Name/Value Confusion

```python
class Status(StrEnum):
    PENDING = "pending"


value = Status.PENDING.name
```

Question:

> Is `value` suitable for an API expecting `"pending"`?

Expected reasoning:

```text
No.
.name is "PENDING".
.value is "pending".
```

---

## Challenge 2 — Invalid Transition

```python
allowed = {
    OrderState.CREATED: {
        OrderEvent.PAY: OrderState.PAID,
    }
}

next_state = allowed[OrderState.CREATED][OrderEvent.SHIP]
```

Question:

> What should happen?

Expected reasoning:

```text
The event is invalid from CREATED.
```

Do not silently manufacture a state.

---

## Challenge 3 — Terminal State Bypass

```python
order.state = OrderState.DELIVERED
order.state = OrderState.CREATED
```

Question:

> Why is this dangerous?

Expected reasoning:

The state was mutated directly without transition validation.

A controlled API should prevent arbitrary state changes.

---

## Challenge 4 — Duplicate Event

```text
payment captured
PAY event received again
```

Question:

> Should this be an exception, a no-op, or an idempotent success?

Expected reasoning:

The domain contract must decide.

The important part is that the behavior is intentional.

---

## Challenge 5 — Concurrent Update

```text
worker A reads PENDING
worker B reads PENDING
worker A writes APPROVED
worker B writes CANCELLED
```

Question:

> What protects against lost updates?

Expected reasoning:

Discuss optimistic concurrency, versioning, locking, or atomic conditional updates.

---

# 118. Mini-Project — Production-Oriented AI Job State Machine

## Objective

Build a small state-management component for an AI processing job.

Everything described here is part of the exercise. No separate project files are required for this chapter.

## Required States

```text
CREATED
QUEUED
RUNNING
RETRYING
COMPLETED
FAILED
CANCELLED
```

## Required Events

```text
QUEUE
START
RETRY
COMPLETE
FAIL
CANCEL
```

## Minimum Transition Design

One reasonable starting specification is:

```text
CREATED + QUEUE   → QUEUED
QUEUED  + START   → RUNNING
RUNNING + COMPLETE → COMPLETED
RUNNING + FAIL    → FAILED
FAILED + RETRY    → RETRYING
RETRYING + START  → RUNNING
QUEUED + CANCEL   → CANCELLED
RUNNING + CANCEL  → CANCELLED
```

The exercise is to make every other transition explicitly invalid unless you can justify a different rule.

## Requirements

Your implementation should:

- use an Enum for states;
- use an Enum for events;
- use a transition table;
- reject invalid transitions;
- protect terminal states;
- track retry count;
- keep a transition history;
- include structured logging fields;
- use type annotations;
- test success and failure paths;
- define the retry limit;
- document idempotency behavior.

## Suggested Architecture

```text
Job
 |
 +-- current state
 +-- retry count
 +-- transition history
 |
 +-- transition(event)
        |
        +-- validate
        +-- calculate next state
        +-- record transition
        +-- update state
```

Keep external model APIs and databases out of the first version.

## Test Scenarios

At minimum:

1. created job can be queued;
2. queued job can start;
3. running job can complete;
4. running job can fail;
5. failed job can retry;
6. retrying job can start again;
7. completed job rejects further transitions;
8. cancelled job rejects further transitions;
9. retry limit is enforced;
10. transition history contains the correct sequence.

## Extension Challenges

After the basic version works, reason about:

- concurrent workers;
- stale state;
- version numbers;
- duplicate events;
- structured audit events;
- recovery after process restart;
- separating side effects from state transitions.

Do not turn the exercise into a distributed workflow engine.

---

# 119. Mini-Project Review Checklist

Before considering the mini-project complete, verify:

```text
[ ] State vocabulary is explicit.
[ ] Event vocabulary is explicit.
[ ] Transitions are centralized.
[ ] Invalid events are rejected.
[ ] Terminal states are protected.
[ ] Retry behavior is bounded.
[ ] Duplicate-event behavior is documented.
[ ] Side effects are not hidden inside raw state assignment.
[ ] Transition history is available.
[ ] Important transitions are tested.
[ ] Failure paths are tested.
[ ] Concurrency risks are documented.
[ ] External values are stable and intentional.
```

---

# 120. Production-Style Review Questions

Use these when reviewing a state-machine pull request.

### Domain correctness

- Does the model contain the real domain states?
- Are events clearly separated from states?
- Are impossible transitions rejected?
- Are terminal states correct?

### Maintainability

- Can a new engineer understand the lifecycle quickly?
- Are the rules centralized?
- Is the state vocabulary stable?
- Are side effects separated?

### Reliability

- What happens after a worker crash?
- Can duplicate events occur?
- Can the same transition happen twice?
- How are retries bounded?

### Operations

- Can operators see the current state?
- Can they see the previous transition?
- Are failures observable?
- Is transition history available?

### Concurrency

- Can two workers update the same job?
- How is stale state detected?
- Is a version number needed?

---

# 121. Production State-Machine Pattern

A useful overall structure is:

```text
                   ┌────────────────────┐
                   │ External event/input│
                   └─────────┬──────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Validate event/input │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Current state        │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Transition rule      │
                  │ (state, event)       │
                  │ → next state         │
                  └──────────┬───────────┘
                             │
                 ┌───────────┴────────────┐
                 │                        │
                 ▼                        ▼
        ┌────────────────┐      ┌───────────────────┐
        │ state change   │      │ side-effect plan  │
        └───────┬────────┘      └─────────┬─────────┘
                │                         │
                └────────────┬────────────┘
                             ▼
                    ┌─────────────────┐
                    │ persist/observe │
                    └─────────────────┘
```

This is a conceptual architecture, not a mandatory implementation.

---

# 122. What a Good State Machine Gives You

A well-designed state machine makes these questions easy to answer:

```text
What state are we in?
What events are accepted?
What is the next state?
Why was a transition rejected?
Which states are terminal?
Can this event retry?
What happened before this state?
Can another worker update it safely?
```

If your design still makes these questions difficult, adding more classes may not solve the real problem.

The issue may be unclear domain modeling.

---

# 123. Final Mental Model

Keep these concepts separate.

## Enum

> A controlled vocabulary of named values.

```text
Status
├── PENDING
├── RUNNING
└── COMPLETED
```

## State

> The current condition of an entity or workflow.

```text
RUNNING
```

## Event

> Something that happens and may cause a state change.

```text
COMPLETE
```

## Transition

> A rule mapping one state and event to another state.

```text
(current_state, event) → next_state
```

Example:

```text
(RUNNING, COMPLETE) → COMPLETED
```

## State machine

> A controlled model of state, events, and allowed transitions.

```text
State + Event
      ↓
Transition rule
      ↓
Next State
```

## Production state machine

A production-oriented design may add:

```text
States
+
Events
+
Transition rules
+
Validation
+
Failure handling
+
Retries
+
Persistence
+
Observability
+
Concurrency control
+
Audit history
```

Not every system needs every item.

The correct design depends on the workload and domain.

---

# 124. The Most Important Engineering Principle

Do not ask:

> "Should I use an Enum because Enums are better?"

Ask:

> "What domain vocabulary and lifecycle rules actually exist?"

And do not ask:

> "Should I build a state machine because state machines are advanced?"

Ask:

> "Do valid and invalid transitions matter enough that explicit lifecycle modeling improves correctness, observability, and maintainability?"

The abstraction should follow the problem.

---

# 125. Quick Reference

## Enum essentials

```python
from enum import Enum

class Status(Enum):
    PENDING = "pending"

Status.PENDING
Status.PENDING.name
Status.PENDING.value

Status("pending")
Status["PENDING"]

for status in Status:
    print(status)
```

## String-compatible Enum

```python
from enum import StrEnum

class Status(StrEnum):
    PENDING = "pending"
```

Python 3.11+.

## Integer-compatible Enum

```python
from enum import IntEnum

class ExitCode(IntEnum):
    OK = 0
```

## Generated values

```python
from enum import Enum, auto

class Color(Enum):
    RED = auto()
    GREEN = auto()
```

## Flags

```python
from enum import Flag, auto

class Permission(Flag):
    READ = auto()
    WRITE = auto()
```

## State machine

```python
next_state = TRANSITIONS[current_state][event]
```

with validation:

```python
allowed = TRANSITIONS.get(current_state, {})

if event not in allowed:
    raise ValueError("Invalid transition")

next_state = allowed[event]
```

---

# 126. Final Self-Review Checklist

Use this checklist before moving on.

### Enum fundamentals

- [ ] I can explain why Enums exist.
- [ ] I understand Enum members.
- [ ] I can distinguish `.name` from `.value`.
- [ ] I understand identity vs equality.
- [ ] I can iterate over an Enum.
- [ ] I can look up a member by value.
- [ ] I can look up a member by name.
- [ ] I understand aliases.
- [ ] I understand `@unique`.
- [ ] I understand `auto()`.
- [ ] I understand `IntEnum`.
- [ ] I understand `StrEnum`.
- [ ] I understand `Flag`.
- [ ] I understand `IntFlag`.
- [ ] I understand external serialization concerns.

### State machines

- [ ] I can define a state.
- [ ] I can define an event.
- [ ] I can model a transition.
- [ ] I understand `(state, event) → next_state`.
- [ ] I can build a transition table.
- [ ] I can reject invalid transitions.
- [ ] I can identify terminal states.
- [ ] I can state invariants.
- [ ] I can model retries.
- [ ] I can reason about duplicate events.
- [ ] I can separate state changes from side effects.
- [ ] I understand why persistence matters.
- [ ] I understand basic concurrency risks.
- [ ] I can test valid and invalid transitions.
- [ ] I can make transitions observable.

### Applied AI engineering

- [ ] I can model a document-processing lifecycle.
- [ ] I can model an evaluation-job lifecycle.
- [ ] I can model an agent execution lifecycle.
- [ ] I understand why model output is not automatically application state.
- [ ] I can use Enums for finite provider/configuration choices.
- [ ] I can explain where a state machine improves reliability and debugging.

---

# 127. Final Decision Framework

When choosing a modeling technique, walk through this process:

```text
Is the value open-ended?
        |
       YES
        ↓
   use string/data
        |
       NO
        ↓
Is there a small finite vocabulary?
        |
       YES
        ↓
     consider Enum
        |
       NO
        ↓
Are options independently combinable?
        |
       YES
        ↓
   consider Flag
        |
       NO
        ↓
Are there only two independent conditions?
        |
       YES
        ↓
   consider boolean
        |
       NO
        ↓
Is there a lifecycle with events and valid transitions?
        |
       YES
        ↓
 consider state machine
```

Then ask:

```text
Does this lifecycle need persistence?
Does retry matter?
Does concurrency matter?
Does auditing matter?
Does observability matter?
```

The answers determine whether a simple state machine is enough or whether a larger workflow architecture is warranted.

---

# 128. Final Takeaways

The essential ideas are:

1. **Enum** gives a controlled vocabulary of named values.
2. **`.name`** is the declared member identifier.
3. **`.value`** is the associated value.
4. **`StrEnum`** is useful when Enum semantics and string interoperability both matter.
5. **`IntEnum`** is useful when integer compatibility is required.
6. **`Flag`/`IntFlag`** model combinable capabilities rather than mutually exclusive workflow states.
7. An **Enum is not a state machine**.
8. A **state machine** adds current state, events, legal transitions, validation, and lifecycle rules.
9. The key transition model is:
   ```text
   (current_state, event) → next_state
   ```
10. Invalid transitions should normally be explicit and observable.
11. Terminal states and invariants protect domain correctness.
12. Retry and failure behavior should be modeled intentionally.
13. State changes and external side effects should remain conceptually separate.
14. Persistence and concurrency become important when workflows outlive one process.
15. State-transition history improves debugging and operational visibility.
16. Enums and state machines can provide clean foundations for production AI workflows.
17. The right abstraction is the simplest one that accurately represents the domain.

> **Production principle:**  
> **Model finite vocabularies explicitly, model meaningful lifecycles explicitly, reject invalid transitions clearly, and add complexity only when the system's actual reliability and operational requirements justify it.**

---

## References and Version Notes

This chapter uses the Python standard library's `enum` concepts and intentionally keeps framework-specific material out of the examples.

Python's current `enum` documentation covers `Enum`, `IntEnum`, `StrEnum`, `Flag`, `IntFlag`, `auto`, aliases, `@unique`, and related behavior. `StrEnum` was added in Python 3.11, and the standard-library documentation records several Enum changes across recent Python versions. citeturn442575search0turn442575search2

When adopting newer Enum features in a production codebase, check the project's supported Python version and the standard-library documentation for that version.

---

# Appendix A — Compact State Machine Template

```python
from enum import StrEnum


class State(StrEnum):
    START = "start"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class Event(StrEnum):
    BEGIN = "begin"
    COMPLETE = "complete"
    FAIL = "fail"


TRANSITIONS = {
    State.START: {
        Event.BEGIN: State.RUNNING,
    },
    State.RUNNING: {
        Event.COMPLETE: State.DONE,
        Event.FAIL: State.FAILED,
    },
}


def transition(state: State, event: Event) -> State:
    allowed_events = TRANSITIONS.get(state, {})

    try:
        return allowed_events[event]
    except KeyError as exc:
        raise ValueError(
            f"Invalid transition: {state.value} + {event.value}"
        ) from exc
```

The template is deliberately small.

Expand it only when the domain requires:

- history;
- retry counts;
- persistence;
- concurrency;
- observability;
- side-effect coordination.

---

# Appendix B — One-Page Mental Model

```text
                        ENUM
                         |
           +-------------+--------------+
           |                            |
      controlled                   named members
      vocabulary                   with values
           |
           v
       STATE ENUM
           |
           v
     explicit states
           |
           +
           |
           v
      EVENT ENUM
           |
           v
     explicit events
           |
           v
  (state, event) → next_state
           |
           v
    TRANSITION RULES
           |
           v
  invalid transitions rejected
           |
           v
    terminal states
           |
           v
      invariants
           |
           v
 retries / failure handling
           |
           v
 persistence / observability
           |
           v
 concurrency / auditing
           |
           v
 production lifecycle management
```

The final mental model is simple:

> **Enum answers "What values are valid?"**  
> **State machine answers "How may the system move between valid states?"**

And in production:

> **Make state explicit, make transitions explicit, and make the consequences of each transition observable and safe.**
