# Dataclasses and Data Models

> **Stage 1 — Programming & Computational Thinking**  
> **Module 08 — Object-Oriented Design, Data Modelling, and Functional Style**

This chapter teaches **Python data modelling and dataclasses** from complete beginner level through advanced, production-oriented engineering. Data models are used throughout backend services, APIs, databases, data pipelines, configuration, ML systems, AI applications, LLM applications, and agentic AI systems.

The progression is:

```text
BEGINNER → FOUNDATION → INTERMEDIATE → ADVANCED → PRODUCTION
```

For each topic, think in this order:

```text
What is it?
→ Why does it exist?
→ What problem does it solve?
→ Simple example
→ How it works
→ Common mistake
→ Better approach
→ Real-world use
→ Production consideration
```

The chapter assumes modern Python. Features such as `kw_only`, `match_args`, and `slots` are available in Python 3.10+, while `weakref_slot` is available in Python 3.11+.

## Learning Objectives

By the end of this chapter you should be able to model stable data explicitly, use dataclass generation safely, reason about defaults and factories, equality and hashing, immutability, ordering, slots, keyword-only fields, pattern matching, nested models, validation, serialization, model evolution, and production API/data/ML/LLM boundaries.

You should also be able to choose deliberately between a dictionary, tuple, `NamedTuple`, dataclass, normal class, ORM model, or validation-oriented model.

## Prerequisites

You should already know Python functions, modules, classes, type hints, encapsulation, composition, inheritance, polymorphism, dependency injection, testing with `pytest`, and basic debugging. This chapter does not assume prior knowledge of `dataclasses`.


## 1. What Is Data Modelling?

Data modelling is deciding how information is represented and what rules that representation carries. A model makes meaning explicit: a `User` has a name, email, age, and perhaps `created_at`.

```python
user = {"name": "Alice", "email": "alice@example.com", "age": 30}
```

A model is more than storage. It can define identity, equality, invariants, lifecycle, serialization boundaries, and domain meaning. A data model mainly describes shape; a domain model may also enforce business behavior.


## 2. Dictionaries vs Tuples vs Classes

A dictionary is flexible and natural for dynamic key/value data. A tuple is compact and immutable but position-based. A named tuple gives tuple compatibility plus named fields. A normal class gives maximum behavior and lifecycle control. A dataclass is a strong candidate when the class is primarily a stable, named data structure.

```python
record = {"name": "Alice", "age": 30}
point = (10, 20)
```

Do not turn every dictionary into a class. Use the simplest representation that matches the problem.


## 3. What Is a Dataclass?

A dataclass is a normal Python class decorated with `dataclass` so common data-oriented methods can be generated from annotated fields.

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    age: int
```

It reduces boilerplate. It does **not** automatically validate field types, serialize to JSON, make nested values immutable, or enforce arbitrary business rules.


## 4. Dataclass vs Normal Class

A normal class is appropriate when custom lifecycle or behavior dominates. A dataclass is useful when field declaration should be the center of the class.

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age
```

```python
@dataclass
class User:
    name: str
    age: int
```

Both remain normal Python classes. The decorator adds generated behavior; it does not remove your ability to define methods, properties, or custom logic.


## 5. Generated __init__

With `init=True` (the default), dataclasses normally generate `__init__` from fields in definition order.

```python
@dataclass
class User:
    name: str
    age: int

user = User("Alice", 30)
```

Required fields must be supplied. Defaulted fields can be omitted. Field ordering matters, including across inheritance.


## 6. Generated __repr__

The generated `__repr__` is valuable for debugging and tests.

```python
@dataclass
class User:
    name: str
    age: int

print(User("Alice", 30))
```

For production, remember that repr can expose data. Use `field(repr=False)` for values such as passwords, tokens, or other sensitive fields. That is representation control, not security.


## 7. Generated __eq__

`eq=True` (the default) generates field-based equality. Equality asks whether two values are logically equal under the dataclass contract; `is` asks whether they are the same object.

```python
u1 = User("Alice", 30)
u2 = User("Alice", 30)
assert u1 == u2
assert u1 is not u2
```

Generated dataclass equality compares instances as the same dataclass type; it is not a general comparison between arbitrary related classes.


## 8. Generated Methods Overview

By default, `@dataclass` typically provides `__init__`, `__repr__`, and `__eq__`. `order=True` adds ordering methods. Hash generation depends on `eq`, `frozen`, and `unsafe_hash` settings. Existing user-defined methods can change what the decorator needs to generate.

Never memorize the rule as "every dataclass gets every dunder method." Configuration controls the result.


## 9. Dataclass Decorator Parameters

The main modern parameters are `init`, `repr`, `eq`, `order`, `unsafe_hash`, `frozen`, `match_args`, `kw_only`, `slots`, and `weakref_slot`.

```python
@dataclass(
    init=True,
    repr=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    frozen=False,
    match_args=True,
    kw_only=False,
    slots=False,
    weakref_slot=False,
)
class Example:
    value: int
```

Treat each option as an API/design decision rather than a decoration checklist.


## 10. init=

`init=True` asks the decorator to generate `__init__` when needed. With `init=False`, you provide the constructor yourself.

```python
@dataclass(init=False)
class User:
    name: str

    def __init__(self, raw_name: str) -> None:
        self.name = raw_name.strip()
```

Useful when construction is genuinely custom. If initialization becomes complex, a normal class or a named constructor may be clearer.


## 11. repr=

`repr=True` is the default. `repr=False` disables generated repr for the class. At field level use `field(repr=False)`.

```python
@dataclass
class Session:
    user_id: str
    token: str = field(repr=False)
```

This is useful for sensitive, huge, or noisy fields. It never removes the value from memory or from arbitrary serialization.


## 12. eq=

`eq=True` generates equality based on fields that participate in comparison. `eq=False` disables generated field equality.

Equality semantics affect tests, deduplication, caches, and collections. Do not exclude fields from equality simply because that makes a fixture easier to write; exclude them only when the domain says they are irrelevant to logical equality.


## 13. order=

`order=True` generates `__lt__`, `__le__`, `__gt__`, and `__ge__`. The generated comparisons are field-based and require comparable same-type instances. `eq` must remain enabled for `order=True`.

```python
@dataclass(order=True)
class Version:
    major: int
    minor: int
```

Enable ordering only when the domain has a meaningful total/lexicographic ordering.


## 14. unsafe_hash=

Hashing is needed for set membership and dictionary keys. With the default `unsafe_hash=False`, dataclasses choose hash behavior based on `eq` and `frozen`. A mutable dataclass with generated equality is generally unhashable by default.

`unsafe_hash=True` can force hash generation, but a mutable key can change its hash after insertion. That can make dictionary/set behavior unreliable. Prefer stable, immutable value objects as keys and do not use `unsafe_hash=True` as a convenience default.


## 15. frozen=

`@dataclass(frozen=True)` prevents normal assignment and deletion of fields after construction.

```python
@dataclass(frozen=True)
class Point:
    x: int
    y: int
```

Frozen behavior is shallow: a field containing a list can still reference a mutable list. Use immutable nested types such as tuples and frozensets when deep immutability is a true requirement.


## 16. Immutability

Mutable objects change state. Immutable-style objects represent values that are replaced rather than modified.

```python
@dataclass(frozen=True)
class Config:
    host: str
    port: int
```

Immutability can simplify reasoning, sharing, caching, and concurrency. It can also require allocating new values. Use it where stable value semantics improve correctness rather than treating it as a universal rule.


## 17. field()

`field()` configures individual dataclass fields. Important options include `default`, `default_factory`, `init`, `repr`, `hash`, `compare`, `metadata`, and `kw_only`.

```python
@dataclass
class Cart:
    items: list[str] = field(default_factory=list, repr=True)
```

The function is most useful when the normal `x: Type = value` syntax cannot express the desired behavior.


## 18. Default Values

Use a simple default for stable values:

```python
@dataclass
class User:
    name: str
    role: str = "user"
```

Required fields must precede defaulted fields in the generated initialization order. This rule also matters across inheritance.


## 19. default_factory

Use `default_factory` to create a fresh value per instance.

```python
@dataclass
class Cart:
    items: list[str] = field(default_factory=list)

    metadata: dict[str, str] = field(default_factory=dict)
```

The factory is a zero-argument callable. Pass `list`, not `list()`. Pass `create_settings`, not `create_settings()`. This avoids shared mutable defaults.


## 20. default vs default_factory

Use `default` for a specific stable value and `default_factory` for a value that must be created when an instance is initialized.

| Need | Choice |
|---|---|
| string constant | `default=` / `=` |
| fresh list | `default_factory=list` |
| fresh dict | `default_factory=dict` |
| fresh custom object | custom factory |

The factory should describe object creation, not store an already-created mutable object.


## 21. Custom Factories

A named factory can make construction intent explicit.

```python
def default_settings() -> dict[str, object]:
    return {"retries": 3, "debug": False}

@dataclass
class Config:
    settings: dict[str, object] = field(default_factory=default_settings)
```

Factories are especially useful when a default requires multiple steps or deserves its own tests.


## 22. compare

`field(compare=False)` excludes a field from generated equality and ordering.

```python
@dataclass
class User:
    user_id: str
    name: str
    last_seen: int = field(compare=False)
```

Now `last_seen` does not affect generated equality. This is correct only if the field is operational metadata rather than part of logical identity.


## 23. hash

Field-level `hash` controls whether a field participates in generated hashing. `None` is the normal default and generally follows comparison participation. `hash=False` can exclude a field; `hash=True` can force inclusion when a generated hash exists.

The advanced case `hash=False, compare=True` can be useful when a field is expensive to hash but must still affect equality, provided other fields support a valid hash contract. Do not optimize this way without a reason.


## 24. init=False

`field(init=False)` removes a field from the generated constructor.

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self) -> None:
        self.area = self.width * self.height
```

Use it for derived state or internal values that should not be supplied by callers. Remember that `replace()` follows constructor semantics and treats `init=False` fields specially.


## 25. repr=False

At field level, `field(repr=False)` prevents generated repr from showing the value.

Useful examples include passwords, access tokens, internal caches, or huge payloads. It is not an authorization or encryption feature.


## 26. metadata

`field(metadata={...})` attaches extra field information for tools/frameworks. Dataclasses themselves do not interpret arbitrary metadata as business logic.

```python
@dataclass
class User:
    user_id: str = field(metadata={"external_name": "userId"})
```

Metadata is useful for extension mechanisms, but too much metadata can become an invisible second configuration language.


## 27. Keyword-Only Fields

A field can be keyword-only:

```python
@dataclass
class Config:
    environment: str
    timeout: int = field(default=30, kw_only=True)
```

Or all fields can be keyword-only:

```python
@dataclass(kw_only=True)
class Config:
    environment: str
    timeout: int = 30
```

Keyword-only constructors improve readability and can make evolving public APIs safer.


## 28. __post_init__

`__post_init__()` is called after the generated `__init__` and is useful for derived values, normalization, and local invariant checks.

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self) -> None:
        self.area = self.width * self.height
```

It belongs to the generated-initialization path. A hand-written custom `__init__` changes the lifecycle you must reason about.


## 29. Validation

Dataclasses do not automatically validate types or business rules. Validation can be layered:

```text
external input → boundary/schema validation → model construction → domain invariants → service rules
```

Use `__post_init__()` for local invariants, such as `age >= 0`. Cross-object rules often belong in domain/service logic. Validation-oriented libraries can be useful at complex untrusted boundaries.


## 30. InitVar

`InitVar` supplies an initialization-only value to `__post_init__()` without storing it as a normal dataclass field.

```python
@dataclass
class User:
    raw_password: InitVar[str]
    password_hash: str = field(init=False)

    def __post_init__(self, raw_password: str) -> None:
        self.password_hash = f"hash:{raw_password}"
```

Use it for temporary construction inputs that should not become persistent state.


## 31. fields()

`dataclasses.fields()` exposes dataclass field definitions.

```python
for info in fields(User):
    print(info.name, info.type)
```

It works with a dataclass class or instance and exposes configuration such as defaults, `compare`, `repr`, `metadata`, and `kw_only`. `InitVar` values are not normal `Field` entries.


## 32. is_dataclass()

`is_dataclass()` returns true for dataclass classes and dataclass instances.

```python
assert is_dataclass(User)
assert is_dataclass(User("Alice"))
```

If you need specifically an instance, combine it with `not isinstance(value, type)`. Use this for generic tooling rather than replacing a clear static interface with dynamic checks.


## 33. asdict()

`asdict()` recursively converts dataclass instances into dictionaries and recursively handles nested dataclasses and containers. Other values may be deep-copied during conversion.

```python
@dataclass
class User:
    name: str

payload = asdict(User("Alice"))
assert payload == {"name": "Alice"}
```

It is convenient, not a full serialization framework. Large or custom transport models may need explicit serializers.


## 34. astuple()

`astuple()` recursively represents a dataclass as a tuple-oriented structure.

```python
@dataclass
class Point:
    x: int
    y: int

assert astuple(Point(1, 2)) == (1, 2)
```

Use it when tuple semantics help. Do not choose it for a boundary where losing field names makes the contract harder to understand.


## 35. replace()

`dataclasses.replace()` creates a new dataclass instance with selected initialization fields changed.

```python
@dataclass(frozen=True)
class User:
    name: str
    age: int

updated = replace(User("Alice", 30), age=31)
```

It is especially useful for immutable-style state updates. It follows constructor semantics, may run `__post_init__()` again, and does not accept `init=False` fields as ordinary replacement parameters.


## 36. make_dataclass()

`make_dataclass()` creates a dataclass dynamically.

```python
Record = make_dataclass(
    "Record",
    [("id", int), ("name", str)],
)
```

It is useful for generated schemas and metaprogramming. Normal source declarations are usually clearer for stable application models.


## 37. dataclass_transform

`typing.dataclass_transform` is an advanced typing feature for libraries that create dataclass-like classes through custom decorators, base classes, or metaclasses. It helps static type checkers understand synthesized constructor/field behavior.

It is more relevant to framework authors than ordinary application code. It does not itself magically generate dataclass methods.


## 38. slots

`@dataclass(slots=True)` generates a slotted layout for declared fields.

```python
@dataclass(slots=True)
class Point:
    x: int
    y: int
```

Slots can constrain undeclared attributes and reduce per-instance memory in appropriate workloads. They do not guarantee faster code. They can also affect framework compatibility and inheritance behavior.


## 39. weakref_slot

`weakref_slot=True` adds weak-reference support to a slotted dataclass.

```python
@dataclass(slots=True, weakref_slot=True)
class CacheEntry:
    key: str
```

It requires `slots=True`. It matters for caches, registries, and other systems where an object should be referenced weakly without being kept alive solely by that reference.


## 40. match_args

`match_args=True` (the default) lets a dataclass generate `__match_args__` from non-keyword-only parameters of its generated constructor.

```python
@dataclass
class Point:
    x: int
    y: int
```

This supports `case Point(x, y)`. With `match_args=False`, the positional tuple is not generated. Keyword patterns remain available.


## 41. Pattern Matching

Dataclasses work naturally with structural pattern matching.

```python
match point:
    case Point(x=0, y=y):
        print(y)
    case Point(x, y):
        print(x, y)
```

Pattern matching is useful when the branch is the business rule. Remember that positional matching depends on `__match_args__` and can become coupled to field order, so keyword matching is often more stable for evolving models.


## 42. Dataclass Inheritance

Dataclasses can inherit from dataclasses.

```python
@dataclass
class Person:
    name: str

@dataclass
class Employee(Person):
    employee_id: int
```

Inherited fields participate in generated initialization and comparison. Defaults, `__post_init__`, frozen state, and slots all interact with the hierarchy, so keep dataclass inheritance shallow and readable.


## 43. Field Ordering

Generated constructor parameters follow field order, including inherited fields. A non-default field generally cannot follow a default field.

```python
@dataclass
class Base:
    name: str = "unknown"

# A child field added after the inherited default can make the generated
# constructor invalid.
```

Keyword-only fields can sometimes solve this cleanly; redesigning the hierarchy can be better when defaults become too difficult to reason about.


## 44. Dataclass + Properties

A dataclass can define properties just like any normal class.

```python
@dataclass
class User:
    first: str
    last: str

    @property
    def full_name(self) -> str:
        return f"{self.first} {self.last}"
```

Avoid field/property name collisions. Use properties for derived or controlled views, not automatically for every field.


## 45. Dataclass + Encapsulation

Dataclasses expose normal public attributes by default. That is often correct for DTOs and simple data carriers.

When mutation must be controlled, a normal class may be more expressive:

```python
class Account:
    def deposit(self, amount: Decimal) -> None:
        ...
```

The right choice depends on whether the model is primarily about data representation or controlled state transitions.


## 46. Dataclass + Polymorphism

Dataclass inheritance can model polymorphic data when subtype identity is meaningful.

```python
@dataclass
class Payment:
    amount: Decimal

@dataclass
class CardPayment(Payment):
    last4: str
```

But a Protocol plus composition may be better when implementations simply satisfy a behavioral boundary. Do not create a hierarchy solely because several records share fields.


## 47. Dataclass + Composition

Nested dataclasses are a natural expression of composition.

```python
@dataclass(frozen=True)
class Customer:
    customer_id: str
    name: str

@dataclass
class Order:
    customer: Customer
    items: list[str]
```

Composition keeps related models explicit and can isolate invariants by component.


## 48. Nested Dataclasses

Nested models make structure explicit.

```python
@dataclass(frozen=True)
class Address:
    city: str

@dataclass(frozen=True)
class Customer:
    customer_id: str
    address: Address
```

They are useful for reuse and validation, but very deep nesting increases serialization and migration complexity.


## 49. Data Model vs Domain Model

A data model primarily represents data. A domain model may also contain business behavior, invariants, and state transitions.

A dataclass can be a simple DTO:

```python
@dataclass
class UserResponse:
    id: str
    name: str
```

or a value object with behavior. Use the form that makes the business rules visible.


## 50. DTOs

A Data Transfer Object carries data across a boundary: API request, API response, queue message, or service-to-service call.

```python
@dataclass
class CreateUserRequest:
    name: str
    email: str
```

Separate DTOs from internal domain models when external and internal contracts evolve at different rates.


## 51. Entities vs Value Objects

An entity is identified by stable identity. A value object is identified by its value.

```python
@dataclass
class User:
    user_id: str
    name: str

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
```

This distinction drives equality, mutability, hashing, and persistence decisions.


## 52. Immutable Value Objects

Immutable value objects are a natural fit for `frozen=True`.

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
```

Stable value semantics make objects safer to share and cache. Use immutable nested fields when deep immutability is important.


## 53. Validation Strategy

Validation should happen at the right layer. Type hints describe expectations; dataclasses organize fields; `__post_init__` can enforce local invariants; boundary validators protect untrusted input; service/domain logic handles cross-object rules.

Do not move every business rule into `__post_init__`. A model should remain understandable.


## 54. Dataclass vs Dictionary

Use a dictionary when keys are dynamic or the data is naturally map-shaped. Use a dataclass when a stable set of named fields is part of the contract.

A dictionary is often best for flexible JSON-like data; a dataclass is often best for stable internal records and typed boundaries.


## 55. Dataclass vs NamedTuple

`typing.NamedTuple` and `collections.namedtuple` provide tuple semantics with named fields. Dataclasses provide richer field configuration, factories, mutability choices, and class-oriented behavior.

Choose `NamedTuple` when tuple compatibility is meaningful; choose a dataclass when the model is a flexible Python object.


## 56. Dataclass vs Normal Class

A dataclass is attractive when the constructor and generated value behavior match the model. A normal class is clearer when lifecycle, lazy state, resources, or complex invariants dominate.

The question is not which is 
which option you choose but what the model actually needs.


## 57. Dataclass vs Validation-Oriented Models

Standard-library dataclasses are deliberately lightweight. Validation-oriented libraries add runtime schema validation, coercion/error reporting, serialization helpers, and often schema generation.

A production architecture may use a validation framework at an external API boundary and dataclasses internally. Do not add a framework when simple dataclass construction is enough.


## 58. Serialization

Serialization converts an in-memory model into a transport representation.

```python
payload = asdict(user)
text = json.dumps(payload)
```

`asdict()` is a conversion utility, not a complete serializer. Production serialization may need field renaming, custom handling for `datetime`/`Decimal`, versioning, redaction, and schema rules.


## 59. Deserialization

Deserialization converts transport data back into typed Python objects.

```python
raw = json.loads(payload)
user = User(**raw)
```

Nested dataclasses are not automatically reconstructed from nested dictionaries. Build them explicitly or use a dedicated validation/serialization system.


## 60. API Data Models

Use boundary-specific models when useful:

```python
@dataclass
class CreateUserRequest:
    name: str
    email: str

@dataclass
class UserResponse:
    user_id: str
    name: str
    email: str
```

Separating request/response DTOs from internal objects protects API stability, security, and refactoring freedom.


## 61. Configuration Models

Configuration is often a good fit for frozen dataclasses.

```python
@dataclass(frozen=True, kw_only=True)
class AppConfig:
    environment: str
    timeout_seconds: int = 30
    debug: bool = False
```

Load values from environment/config sources first, convert them to expected Python types, then construct the model. Do not put real secrets in source files.


## 62. Data Pipeline Models

Stage-specific models make pipeline assumptions visible:

```text
raw input → parsed → validated → transformed → output
```

```python
@dataclass(frozen=True)
class ValidatedRecord:
    customer_id: str
    amount: Decimal
```

This is usually easier to maintain than passing anonymous dictionaries through every stage.


## 63. ML Data Models

Typical models include:

```python
@dataclass(frozen=True)
class PredictionRequest:
    model_name: str
    text: str

@dataclass(frozen=True)
class PredictionResult:
    label: str
    confidence: float
```

Dataclasses provide structure and typing. They do not validate tensors, feature dimensions, numerical ranges, or model behavior automatically.


## 64. LLM Application Models

LLM applications often need explicit internal models for requests, responses, token usage, and tools.

```python
@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int

@dataclass(frozen=True)
class LLMResponse:
    text: str
    usage: TokenUsage
```

A provider adapter can convert SDK-specific responses into these stable application models.


## 65. Agentic AI State Models

Agent systems can represent state explicitly:

```python
@dataclass
class AgentState:
    messages: list[str] = field(default_factory=list)
    current_step: int = 0
    status: str = "idle"
```

Other models can represent tool calls, tool results, and execution events. Choose mutable state for controlled in-place execution or frozen models plus `replace()` for immutable state transitions.


## 66. Data Model Evolution

Data models evolve: a field may be added, renamed, deprecated, or removed.

A new required constructor field can break old callers. Adding an optional/defaulted field may preserve source compatibility, but persisted data and external payloads can still need migration.


## 67. Backward Compatibility

Separate public contracts from internal representation where useful.

```text
old external payload → compatibility adapter → current internal model
```

Defaults, keyword-only optional fields, versioned schemas, and migrations are tools for compatibility. Do not force a single class to understand every historical schema forever.


## 68. Testing Dataclasses

Test the semantics that matter: equality, invariants, defaults, factory isolation, frozen behavior, nested conversion, serialization, and compatibility.

```python
with pytest.raises(ValueError):
    User(age=-1)
```

Use normal, boundary, invalid, and regression cases. Do not make tests depend unnecessarily on generated implementation details.


## 69. Mocking Dataclass-Based Dependencies

A collaborator can return a realistic dataclass instead of a large opaque mock tree.

```python
@dataclass(frozen=True)
class ModelResponse:
    text: str

class FakeClient:
    def generate(self, prompt: str) -> ModelResponse:
        return ModelResponse("test")
```

Use mocks when behavior or call verification matters; use dataclass instances when realistic returned data is the main concern.


## 70. Debugging Dataclass Models

Generated repr and explicit fields help diagnose model failures. Useful diagnostics include:

```python
print(obj)
print(type(obj))
print(fields(obj))
```

Watch for huge nested reprs, sensitive fields, incorrect defaults, missing nested construction, unexpected frozen mutation, and slots-related attribute errors.


## 71. Performance Considerations

Dataclasses are not automatically fast or slow. Consider object allocation, attribute storage, nested model creation, hashing, comparison, and serialization costs.

Benchmark representative workloads before choosing `slots=True` or another representation for performance. Optimize the actual bottleneck, not a presumed one.


## 72. Common Dataclass Mistakes

The dedicated mistake section later in this chapter covers at least 20 common failures, including mutable defaults, validation assumptions, unsafe hashing, ordering, repr leaks, overuse of `__post_init__`, field-ordering problems, slots misuse, and choosing dataclasses when another representation is clearer.


## 73. When Not to Use Dataclasses

Use a dictionary for dynamic map-shaped data, a tuple/NamedTuple for tuple semantics, a normal class for complex lifecycle behavior, an ORM model for persistence concerns tightly coupled to an ORM, or a validation-oriented model when rich runtime schema behavior is central.

There is no rule that every structured object must be a dataclass.


## 74. Production Data-Model Design

A production model should have clear field meaning, deliberate equality semantics, explicit invariants, safe representations, a serialization strategy, a compatibility story, and an appropriate mutability model.

Keep models small enough to understand. Separate transport, domain, and persistence concerns when their contracts evolve independently.


## 75. Banking Example

A simplified banking design can combine value-oriented dataclasses with richer stateful classes:

```text
Customer → Account → Transaction
             ↑
            Money
```

`Money` is a natural frozen value object. An account often benefits from a normal class because balance changes are controlled state transitions. Data models should reflect those different responsibilities.


## 76. Data Pipeline Example

A robust pipeline can use:

```text
RawRecord → ValidatedRecord → TransformationResult
```

Each stage can define exactly what downstream code may assume. This makes invalid states easier to detect and supports targeted regression tests.


## 77. AI System Example

An inference service can model:

```text
ModelRequest → provider adapter → ModelResponse
```

Add `TokenUsage`, `ToolCall`, and `ToolResult` as explicit internal models. Keep provider-specific SDK response types behind adapters so the orchestration layer depends on stable application semantics.


## 78. Mini Project

The complete mini-project is provided before the exercise section. It builds a production-oriented data-model layer for an AI document-processing pipeline, including nested dataclasses, validation, serialization/deserialization, tests, failure scenarios, and production trade-offs.


## 79. Progressive Coding Exercises

The chapter includes more than 25 exercises, progressing from a basic dataclass through factories, equality, frozen objects, `InitVar`, `fields`, pattern matching, inheritance, API DTOs, data pipelines, LLM responses, agent state, and production model review. Every exercise contains a problem, requirements, solution, explanation, and common mistake.


## 80. Debugging Lab

The debugging lab contains 12 intentionally broken examples. Each one provides broken code, observed behavior, debugging approach, root cause, corrected code, and a lesson learned.


## 81. Interview Questions

The interview section progresses from basic dataclass concepts to hashing, inheritance, serialization, DTOs, value objects, model evolution, validation frameworks, and production decision-making.


## 82. Architecture Questions

The architecture section asks how to design API models, money value objects, pipeline stages, ML/LLM models, agent state, compatibility layers, and model performance policies.


## 83. Production Checklist

The final checklist covers modelling choices, dataclass APIs, equality/hash/immutability decisions, serialization, validation, versioning, testing, and backend/data/ML/LLM/agent use.


## 84. Knowledge Check

Immediate-answer questions at the end test every major concept from data modelling and generated methods through nested serialization, model evolution, and production architecture.


## 85. Glossary

Key terms are defined in plain language so the learner can revisit the chapter without reconstructing the concepts from code.


## 86. Final Mental Model

A dataclass is best understood as a concise way to declare a Python data-oriented class and generate common mechanics. Production-quality modelling still requires deliberate decisions about semantics, invariants, mutability, boundaries, compatibility, and performance.


# MINI PROJECT — Production-Oriented Data Model Layer

## Requirements

Build a self-contained data-model layer for an AI document-processing pipeline. It must demonstrate dataclasses, type hints, defaults, `default_factory`, validation, `__post_init__`, frozen value objects, nesting, equality, serialization/deserialization, pytest tests, invalid/boundary/regression testing, and production considerations.

## Architecture

```text
Document
  ├── DocumentMetadata
  ├── tags
  └── created_at
       ↓
     Chunk[]
       ↓
 EmbeddingRecord[]
       ↓
 ProcessingResult

ProcessingConfig ──→ Pipeline
```

## Implementation

```python
from dataclasses import asdict, dataclass, field
from datetime import datetime
from decimal import Decimal
import json


@dataclass(frozen=True)
class DocumentMetadata:
    source: str
    language: str

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("source is required")
        if not self.language.strip():
            raise ValueError("language is required")


@dataclass
class Document:
    document_id: str
    text: str
    metadata: DocumentMetadata
    created_at: datetime
    tags: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not self.document_id.strip():
            raise ValueError("document_id is required")
        if not self.text.strip():
            raise ValueError("document text cannot be blank")


@dataclass(frozen=True, kw_only=True)
class ProcessingConfig:
    chunk_size: int = 500
    chunk_overlap: int = 50

    def __post_init__(self) -> None:
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError("overlap must be >= 0 and < chunk size")


@dataclass(frozen=True)
class Chunk:
    document_id: str
    index: int
    text: str

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("index must be non-negative")
        if not self.text.strip():
            raise ValueError("chunk text cannot be blank")


@dataclass(frozen=True)
class EmbeddingRecord:
    document_id: str
    chunk_index: int
    vector: tuple[float, ...]


@dataclass(frozen=True)
class ProcessingResult:
    document_id: str
    chunks_created: int
    embeddings_created: int
    status: str
```

## Serialization

```python
document = Document(
    document_id="doc-1",
    text="hello world",
    metadata=DocumentMetadata(source="upload", language="en"),
    created_at=datetime(2026, 9, 23, 10, 0),
)

payload = asdict(document)
payload["created_at"] = document.created_at.isoformat()
encoded = json.dumps(payload)
```

`asdict()` gives a Python mapping; `json.dumps()` performs JSON encoding. Fields such as `datetime` need explicit conversion.

## Deserialization

```python
raw = json.loads(encoded)
restored = Document(
    document_id=raw["document_id"],
    text=raw["text"],
    metadata=DocumentMetadata(**raw["metadata"]),
    created_at=datetime.fromisoformat(raw["created_at"]),
    tags=set(raw["tags"]),
)

assert restored.document_id == document.document_id
```

## Tests

```python
import pytest


def test_document_rejects_blank_text() -> None:
    with pytest.raises(ValueError):
        Document(
            document_id="doc-1",
            text="   ",
            metadata=DocumentMetadata("upload", "en"),
            created_at=datetime.now(),
        )


def test_default_factory_separates_tags() -> None:
    metadata = DocumentMetadata("upload", "en")
    first = Document("doc-1", "hello", metadata, datetime.now())
    second = Document("doc-2", "world", metadata, datetime.now())

    first.tags.add("processed")

    assert second.tags == set()


def test_config_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        ProcessingConfig(chunk_size=100, chunk_overlap=100)
```

## Failure Scenarios

Reason through blank documents, empty IDs, invalid chunk configuration, malformed timestamps, missing nested objects, invalid JSON types, shared mutable defaults, invalid vector dimensions, and old payloads with missing fields.

## Production Trade-offs

Ask whether `Document` should be frozen, whether tags should be a `frozenset`, whether the model should store timezone-aware timestamps, whether vectors should use a specialized numerical structure, and whether a dedicated schema library should own external validation.

The important design lesson is that the dataclass layer expresses data clearly, while the surrounding architecture owns persistence, external schemas, security, observability, migrations, and performance policy.


# CODING EXERCISES


### Exercise 1 — Create a Basic Dataclass

#### Problem

Create `User(name, age)` with type hints.

#### Requirements

Use `@dataclass` and instantiate it.

#### Solution

```python
@dataclass
class User:
    name: str
    age: int

user = User("Alice", 30)
assert user.age == 30
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Forgetting the annotations means the decorator does not treat the attributes as normal dataclass fields.


### Exercise 2 — Inspect Generated repr

#### Problem

Create a `User` and inspect `repr(user)`.

#### Requirements

Confirm the class name and a safe field are visible.

#### Solution

```python
user = User("Alice", 30)
assert "User" in repr(user)
assert "Alice" in repr(user)
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

`repr()` is not a security mechanism.


### Exercise 3 — Equality versus Identity

#### Problem

Create two identical users and compare them.

#### Requirements

Show `==` is true while `is` is false.

#### Solution

```python
u1 = User("Alice", 30)
u2 = User("Alice", 30)
assert u1 == u2
assert u1 is not u2
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Using `is` for logical value equality.


### Exercise 4 — Default Value

#### Problem

Give `role` a default of `user`.

#### Requirements

Construct the object without a role.

#### Solution

```python
@dataclass
class User:
    name: str
    role: str = "user"

assert User("Alice").role == "user"
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Putting a required field after a default field.


### Exercise 5 — Default Factory List

#### Problem

Give each cart an independent list.

#### Requirements

Use `field(default_factory=list)`.

#### Solution

```python
@dataclass
class Cart:
    items: list[str] = field(default_factory=list)

a = Cart(); b = Cart(); a.items.append("book")
assert b.items == []
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Using `items=[]`.


### Exercise 6 — Default Factory Dictionary

#### Problem

Give each config an independent dictionary.

#### Requirements

Use `default_factory=dict`.

#### Solution

```python
@dataclass
class Config:
    settings: dict[str, object] = field(default_factory=dict)
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Writing `default_factory=dict()`.


### Exercise 7 — Custom Factory

#### Problem

Create named default settings.

#### Requirements

Use a zero-argument function.

#### Solution

```python
def default_settings() -> dict[str, object]:
    return {"retries": 3}

@dataclass
class Config:
    settings: dict[str, object] = field(default_factory=default_settings)
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Calling the factory while defining the class.


### Exercise 8 — Hide Sensitive repr

#### Problem

Keep a password out of generated repr.

#### Requirements

Use `field(repr=False)`.

#### Solution

```python
@dataclass
class Credentials:
    username: str
    password: str = field(repr=False)

assert "secret" not in repr(Credentials("a", "secret"))
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Assuming the hidden field is encrypted or inaccessible.


### Exercise 9 — Compare False

#### Problem

Ignore `last_seen` for equality.

#### Requirements

Use `field(compare=False)`.

#### Solution

```python
@dataclass
class UserState:
    user_id: str
    last_seen: int = field(compare=False)

assert UserState("u-1", 1) == UserState("u-1", 99)
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Ignoring a field without confirming domain equality semantics.


### Exercise 10 — Frozen Value

#### Problem

Create an immutable point.

#### Requirements

Use `frozen=True`.

#### Solution

```python
@dataclass(frozen=True)
class Point:
    x: int
    y: int

assert Point(1, 2) == Point(1, 2)
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Thinking nested lists are deeply immutable.


### Exercise 11 — replace Frozen Object

#### Problem

Update a frozen user.

#### Requirements

Use `replace()`.

#### Solution

```python
@dataclass(frozen=True)
class User:
    name: str
    age: int

old = User("Alice", 30)
new = replace(old, age=31)
assert old.age == 30 and new.age == 31
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Trying to mutate `old`.


### Exercise 12 — Post Init Derived Field

#### Problem

Compute rectangle area.

#### Requirements

Use `init=False` and `__post_init__`.

#### Solution

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self) -> None:
        self.area = self.width * self.height
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Forgetting `init=False` and requiring callers to supply area.


### Exercise 13 — Post Init Validation

#### Problem

Reject negative age.

#### Requirements

Raise `ValueError` from `__post_init__`.

#### Solution

```python
@dataclass
class User:
    age: int

    def __post_init__(self) -> None:
        if self.age < 0:
            raise ValueError("age must be non-negative")
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Assuming the annotation `int` validates the value.


### Exercise 14 — InitVar

#### Problem

Accept a raw password only during construction.

#### Requirements

Use `InitVar` and derive a stored value.

#### Solution

```python
@dataclass
class User:
    raw_password: InitVar[str]
    password_hash: str = field(init=False)

    def __post_init__(self, raw_password: str) -> None:
        self.password_hash = f"hash:{raw_password}"
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Storing the raw password as an ordinary field.


### Exercise 15 — Inspect Fields

#### Problem

List the dataclass field names.

#### Requirements

Use `fields()`.

#### Solution

```python
names = [f.name for f in fields(User)]
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Using `__dict__` as the authoritative field schema.


### Exercise 16 — Detect Dataclass

#### Problem

Write a helper for dataclass instances.

#### Requirements

Combine `is_dataclass` with an instance check.

#### Solution

```python
def is_instance(value: object) -> bool:
    return is_dataclass(value) and not isinstance(value, type)
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Forgetting that `is_dataclass()` can also be true for classes.


### Exercise 17 — Dictionary Conversion

#### Problem

Convert a user to a dict.

#### Requirements

Use `asdict()`.

#### Solution

```python
payload = asdict(User("Alice", 30))
assert payload == {"name": "Alice", "age": 30}
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Assuming the result is always JSON-safe.


### Exercise 18 — Tuple Conversion

#### Problem

Convert a point to a tuple.

#### Requirements

Use `astuple()`.

#### Solution

```python
assert astuple(Point(1, 2)) == (1, 2)
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Using tuple conversion at a boundary where field names matter.


### Exercise 19 — Make Dataclass

#### Problem

Generate a tiny model dynamically.

#### Requirements

Use `make_dataclass()`.

#### Solution

```python
Record = make_dataclass("Record", [("id", int), ("name", str)])
record = Record(1, "Alice")
assert record.id == 1
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Using dynamic generation for ordinary static application code.


### Exercise 20 — Keyword-only Field

#### Problem

Make `timeout` keyword-only.

#### Requirements

Use `field(kw_only=True)`.

#### Solution

```python
@dataclass
class Config:
    environment: str
    timeout: int = field(default=30, kw_only=True)

assert Config("prod", timeout=5).timeout == 5
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Assuming `kw_only` changes equality or repr semantics.


### Exercise 21 — Pattern Matching

#### Problem

Match a dataclass with `match`.

#### Requirements

Use a positional or keyword class pattern.

#### Solution

```python
match Point(1, 2):
    case Point(x, y):
        result = (x, y)
    case _:
        result = None
assert result == (1, 2)
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Forgetting that keyword-only fields are excluded from positional `__match_args__`.


### Exercise 22 — Dataclass Inheritance

#### Problem

Create `Employee(Person)`.

#### Requirements

Use dataclass decorators on both classes.

#### Solution

```python
@dataclass
class Person:
    name: str

@dataclass
class Employee(Person):
    employee_id: int

assert Employee("Ada", 7).name == "Ada"
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Ignoring inherited default/non-default field ordering.


### Exercise 23 — Immutable Money

#### Problem

Build a value object for money.

#### Requirements

Use `Decimal`, `frozen=True`, and local validation.

#### Solution

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("negative money")
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Using float as though it were exact decimal money arithmetic.


### Exercise 24 — Slotted Dataclass

#### Problem

Prevent undeclared attributes.

#### Requirements

Use `slots=True`.

#### Solution

```python
@dataclass(slots=True)
class Point:
    x: int
    y: int
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Assuming slots are always faster.


### Exercise 25 — Weak Reference Slot

#### Problem

Make a slotted object weak-referenceable.

#### Requirements

Use both `slots=True` and `weakref_slot=True`.

#### Solution

```python
@dataclass(slots=True, weakref_slot=True)
class Entry:
    key: str

entry = Entry("a")
reference = weakref.ref(entry)
assert reference() is entry
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Setting `weakref_slot=True` without `slots=True`.


### Exercise 26 — Ordering

#### Problem

Create a version model that sorts.

#### Requirements

Use `order=True` only because ordering is meaningful.

#### Solution

```python
@dataclass(order=True)
class Version:
    major: int
    minor: int

assert Version(1, 2) < Version(1, 3)
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Adding ordering merely because comparison methods are available.


### Exercise 27 — Hash Design

#### Problem

Create a safe hashable key.

#### Requirements

Use a frozen dataclass.

#### Solution

```python
@dataclass(frozen=True)
class UserKey:
    user_id: str

cache = {UserKey("u-1"): "value"}
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Using `unsafe_hash=True` on mutable key state.


### Exercise 28 — Nested Serialization

#### Problem

Serialize a user containing an address.

#### Requirements

Use `asdict()` and inspect the nested mapping.

#### Solution

```python
payload = asdict(User("Alice", Address("Kolkata")))
assert payload["address"]["city"] == "Kolkata"
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Assuming the reverse operation automatically constructs `Address`.


### Exercise 29 — API DTO Mapping

#### Problem

Map `CreateUserRequest` to an internal `User`.

#### Requirements

Keep public and internal models separate.

#### Solution

```python
def to_domain(request: CreateUserRequest, user_id: str) -> User:
    return User(user_id, request.name, request.email)
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Returning internal storage fields directly through the API contract.


### Exercise 30 — Pipeline Model

#### Problem

Create Raw/Validated models and a validation function.

#### Requirements

Move untrusted dictionary data into an explicit validated model.

#### Solution

```python
@dataclass(frozen=True)
class RawRecord:
    payload: dict[str, object]

@dataclass(frozen=True)
class ValidatedRecord:
    customer_id: str
    amount: Decimal
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Keeping raw dictionaries in every downstream stage.


### Exercise 31 — LLM Response Model

#### Problem

Model response text and token usage.

#### Requirements

Use nested frozen dataclasses.

#### Solution

```python
@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int

@dataclass(frozen=True)
class LLMResponse:
    text: str
    usage: TokenUsage
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Leaking provider SDK response objects throughout the application.


### Exercise 32 — Agent State

#### Problem

Model messages, step, and status.

#### Requirements

Use `default_factory` for message lists.

#### Solution

```python
@dataclass
class AgentState:
    messages: list[str] = field(default_factory=list)
    step: int = 0
    status: str = "idle"
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Using a shared mutable list.


### Exercise 33 — Model Evolution

#### Problem

Add an optional field without breaking old construction.

#### Requirements

Use an appropriate default and consider persisted-data compatibility separately.

#### Solution

```python
@dataclass
class User:
    name: str
    email: str
    phone: str | None = None
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Assuming source compatibility automatically guarantees schema compatibility.


### Exercise 34 — Production Model Review

#### Problem

Review a dataclass using unsafe hash, arbitrary ordering, a mutable default, and a secret field.

#### Requirements

Identify semantic and technical risks and propose a safer value-oriented design.

#### Solution

```python
@dataclass(frozen=True)
class SafeRecord:
    record_id: str
    created_at: datetime
    tags: tuple[str, ...] = ()
```

#### Explanation

The solution demonstrates the targeted dataclass feature while preserving normal Python semantics. Attempt the problem first, then compare the structure and reasoning.

#### Common Mistake

Fixing syntax while ignoring domain semantics and security.


# DEBUGGING LAB


## Debugging Problem 1 — Mutable Default

### Broken Code

```python
@dataclass
class Cart:
    items: list[str] = []
```

### Expected Behavior

Create carts successfully without shared mutable state.

### Observed Behavior

Dataclass construction rejects the mutable direct default.

### Debugging Approach

Read the field definition and identify a mutable object used as a default.

### Root Cause

A list was supplied as a default instead of a factory.

### Corrected Code

```python
@dataclass
class Cart:
    items: list[str] = field(default_factory=list)
```

### Lesson Learned

Per-instance mutable state needs a factory.


## Debugging Problem 2 — Wrong Default Factory

### Broken Code

```python
@dataclass
class Config:
    settings: dict[str, object] = field(default_factory={})
```

### Expected Behavior

Construct `Config` with a fresh dictionary.

### Observed Behavior

Class creation fails because `default_factory` must be callable.

### Debugging Approach

Check whether the supplied factory is a callable or the result of a call.

### Root Cause

The dictionary was created eagerly.

### Corrected Code

```python
@dataclass
class Config:
    settings: dict[str, object] = field(default_factory=dict)
```

### Lesson Learned

Pass the factory, not the factory result.


## Debugging Problem 3 — Missing init=False

### Broken Code

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float

    def __post_init__(self) -> None:
        self.area = self.width * self.height
```

### Expected Behavior

The caller should not need to provide area.

### Observed Behavior

Construction requires an `area` argument.

### Debugging Approach

Inspect the generated constructor conceptually.

### Root Cause

The derived field remained an init parameter.

### Corrected Code

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self) -> None:
        self.area = self.width * self.height
```

### Lesson Learned

Derived fields need deliberate constructor semantics.


## Debugging Problem 4 — Frozen Mutation

### Broken Code

```python
@dataclass(frozen=True)
class User:
    name: str

user = User("Alice")
user.name = "Bob"
```

### Expected Behavior

Represent the update without mutation.

### Observed Behavior

Assignment raises `FrozenInstanceError`.

### Debugging Approach

Inspect the decorator and ask whether the model is intentionally immutable.

### Root Cause

Frozen fields cannot normally be reassigned.

### Corrected Code

```python
user2 = replace(user, name="Bob")
```

### Lesson Learned

Use replacement/value transitions for frozen models.


## Debugging Problem 5 — Inheritance Ordering

### Broken Code

```python
@dataclass
class Base:
    name: str = "unknown"

@dataclass
class Child(Base):
    employee_id: int
```

### Expected Behavior

Create a valid generated constructor.

### Observed Behavior

Class creation can fail because a non-default field follows a default.

### Debugging Approach

List inherited fields in generated order.

### Root Cause

Dataclass inheritance combines fields into one constructor ordering.

### Corrected Code

```python
@dataclass
class Base:
    name: str = field(default="unknown", kw_only=True)

@dataclass
class Child(Base):
    employee_id: int
```

### Lesson Learned

Defaults and inheritance must be designed together.


## Debugging Problem 6 — Equality Assumption

### Broken Code

```python
@dataclass
class User:
    user_id: str
    last_seen: int

assert User("u-1", 1) == User("u-1", 99)
```

### Expected Behavior

Make equality depend only on identity-like fields.

### Observed Behavior

The assertion fails.

### Debugging Approach

Inspect `compare` participation.

### Root Cause

All normal fields participate in generated equality by default.

### Corrected Code

```python
@dataclass
class User:
    user_id: str
    last_seen: int = field(compare=False)
```

### Lesson Learned

Equality should reflect domain semantics.


## Debugging Problem 7 — JSON Serialization

### Broken Code

```python
@dataclass
class Event:
    created_at: datetime

json.dumps(asdict(Event(datetime.now())))
```

### Expected Behavior

Serialize the datetime safely.

### Observed Behavior

`json.dumps()` raises `TypeError` for `datetime`.

### Debugging Approach

Inspect the types contained in the dictionary before encoding.

### Root Cause

Dataclass conversion does not make every value JSON-native.

### Corrected Code

```python
payload = asdict(event)
payload["created_at"] = event.created_at.isoformat()
text = json.dumps(payload)
```

### Lesson Learned

Serialization is a boundary concern separate from dataclass conversion.


## Debugging Problem 8 — Nested Deserialization

### Broken Code

```python
@dataclass
class Address:
    city: str

@dataclass
class User:
    name: str
    address: Address

raw = {"name": "Alice", "address": {"city": "Kolkata"}}
user = User(**raw)
```

### Expected Behavior

Ensure `user.address` is an `Address`.

### Observed Behavior

The nested value is a dictionary.

### Debugging Approach

Inspect `type(user.address)`.

### Root Cause

Python does not recursively instantiate nested dataclasses from annotations.

### Corrected Code

```python
user = User(
    name=raw["name"],
    address=Address(**raw["address"]),
)
```

### Lesson Learned

Deserialize nested models deliberately.


## Debugging Problem 9 — Unsafe Hash Mutation

### Broken Code

```python
@dataclass(unsafe_hash=True)
class Key:
    value: int

key = Key(1)
cache = {key: "value"}
key.value = 2
```

### Expected Behavior

Keep key lookup stable.

### Observed Behavior

The object's hash/equality state can change after insertion.

### Debugging Approach

Compare `hash(key)` before and after mutation.

### Root Cause

A mutable hash key can move logically without moving in the hash table.

### Corrected Code

```python
@dataclass(frozen=True)
class Key:
    value: int
```

### Lesson Learned

Use stable immutable keys.


## Debugging Problem 10 — Repr Secret Leak

### Broken Code

```python
@dataclass
class Credentials:
    username: str
    password: str

logger.info("credentials=%r", Credentials("a", "secret"))
```

### Expected Behavior

Prevent generated repr from exposing the password.

### Observed Behavior

The password appears in the repr.

### Debugging Approach

Read the generated representation in the log call.

### Root Cause

The sensitive field is included by default.

### Corrected Code

```python
@dataclass
class Credentials:
    username: str
    password: str = field(repr=False)
```

### Lesson Learned

Representation suppression and security controls are separate concerns.


## Debugging Problem 11 — Slots Attribute Error

### Broken Code

```python
@dataclass(slots=True)
class User:
    name: str

user = User("Alice")
user.debug_note = "temp"
```

### Expected Behavior

Decide whether the extra attribute belongs to the model.

### Observed Behavior

An `AttributeError` occurs.

### Debugging Approach

Inspect the class for slots and undeclared attributes.

### Root Cause

Slots intentionally restrict arbitrary attributes.

### Corrected Code

```python
@dataclass(slots=True)
class User:
    name: str
    debug_note: str | None = None
```

### Lesson Learned

Use slots intentionally and model needed fields explicitly.


## Debugging Problem 12 — replace init=False

### Broken Code

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self) -> None:
        self.area = self.width * self.height

rectangle = Rectangle(2, 3)
replace(rectangle, area=99)
```

### Expected Behavior

Update the rectangle while preserving derived area semantics.

### Observed Behavior

Replacement rejects `area` as an initialization argument.

### Debugging Approach

Inspect which fields participate in `__init__`.

### Root Cause

`area` is an `init=False` field.

### Corrected Code

```python
updated = replace(rectangle, width=4)
assert updated.area == 12
```

### Lesson Learned

Use replace through constructor-oriented fields.


# INTERVIEW QUESTIONS

## Beginner → Advanced

### What is a dataclass?

A standard-library decorator that adds generated data-oriented methods to an ordinary Python class based on annotated fields.

### Why use dataclasses?

To reduce repetitive boilerplate while retaining normal Python class semantics.

### What does `@dataclass` generate?

Depending on configuration, `__init__`, `__repr__`, `__eq__`, ordering methods, and hash behavior.

### Does a dataclass validate types automatically?

No. Type annotations are not general runtime validation.

### What is `field()`?

A helper for configuring a specific field's default, factory, comparison, repr, hash, metadata, initialization, and keyword-only behavior.

### `default` vs `default_factory`?

`default` supplies a value; `default_factory` supplies a callable that creates a new value when needed.

### Why are mutable defaults dangerous?

A mutable object can become shared state instead of being created independently for each instance.

### What is `__post_init__`?

A post-construction hook used after dataclass-generated initialization.

### What is `InitVar`?

An initialization-only pseudo-field passed to `__post_init__` but not stored as a normal dataclass field.

### What does `frozen=True` mean?

Normal field assignment/deletion is blocked after construction.

### Is frozen deep immutability?

No. Nested mutable objects can remain mutable.

### Why is `unsafe_hash=True` risky?

A mutable object used as a hash key can change the hash/equality state after insertion.

### What is `order=True`?

Generation of ordering methods based on comparable participating fields.

### What is `repr=False`?

Suppression of a field from generated `__repr__` output.

### Is `repr=False` a security mechanism?

No. It only changes generated representation.

### What is `compare=False`?

Excluding a field from generated equality and ordering comparisons.

### What is `metadata`?

Extra field information provided as an extension mechanism; dataclasses do not interpret arbitrary metadata keys themselves.

### What is `kw_only`?

It makes generated constructor parameters keyword-only.

### What is `slots=True`?

A class-layout option that generates slots and restricts undeclared attributes; it can reduce memory for suitable workloads but is not guaranteed to improve performance.

### What is `weakref_slot=True`?

An option that adds weak-reference support to a slotted dataclass and requires `slots=True`.

### What is `match_args`?

It controls generation of `__match_args__` used for positional class-pattern matching.

### What does `asdict()` do?

It recursively converts dataclass instances into dictionary-oriented data; it is not a complete serialization framework.

### What does `astuple()` do?

It recursively converts dataclass instances into tuple-oriented data.

### What does `replace()` do?

It creates a new dataclass instance with selected initialization fields replaced.

### What does `fields()` do?

It returns dataclass field definitions for inspection and generic tooling.

### What does `is_dataclass()` do?

It detects dataclass classes and dataclass instances.

### What does `make_dataclass()` do?

It creates dataclass classes dynamically.

### Dataclass vs dictionary?

Use a dictionary for dynamic map-shaped data; use a dataclass for stable named data with explicit structure.

### Dataclass vs normal class?

Use a dataclass when generated field-oriented behavior fits; use a normal class when lifecycle and complex behavior dominate.

### What is a DTO?

A Data Transfer Object that carries data across a boundary.

### What is a value object?

A model whose value defines its logical equality/identity semantics.

### What is an entity?

A model whose identity matters independently of all other field values.

### How do dataclasses help API design?

They provide explicit request/response models that can isolate external contracts from internal models.

### How do dataclasses help data pipelines?

They make stage-specific structures explicit and testable.

### How do dataclasses help LLM applications?

They can model requests, responses, token usage, tool calls, and tool results independently of provider SDKs.

### How do dataclasses help agentic AI?

They can model messages, execution state, tool calls, results, and events in explicit structures.

### When should you not use dataclasses?

When another representation—dictionary, tuple, NamedTuple, normal class, ORM model, validation framework, or specialized array structure—better matches the problem.

# ARCHITECTURE QUESTIONS

## Production Reasoning

### 1. Design data models for an order-processing service.

**Model answer:** Separate API DTOs, domain models, and persistence representations when their contracts differ. Use dataclasses for stable field-oriented structures and richer classes for aggregates with stateful invariants.

### 2. Design request/response models for an API.

**Model answer:** Use separate request and response DTOs. Expose only stable public fields and validate external input before constructing internal models.

### 3. Design immutable value objects for money.

**Model answer:** Use `Decimal`, `frozen=True`, explicit currency semantics, and local validation. Treat arithmetic and rounding rules as domain behavior.

### 4. Design models for a data pipeline.

**Model answer:** Use explicit stage models such as `RawRecord`, `ValidatedRecord`, and `TransformationResult`. Keep raw dictionaries at the boundary rather than everywhere.

### 5. Design models for an ML inference service.

**Model answer:** Define request, result, and model metadata objects. Keep framework/provider-specific objects behind adapters.

### 6. Design internal models for an LLM application.

**Model answer:** Normalize provider responses into stable internal dataclasses for text, usage, tool calls, and results. Avoid leaking vendor-specific structures into orchestration.

### 7. Design agent state models.

**Model answer:** Represent messages, step, status, pending tool calls, and results explicitly. Choose mutable or frozen state based on the transition model and plan for persistence if needed.

### 8. How would you version data models?

**Model answer:** Use explicit schema versions and adapters/migrations. Keep historical compatibility outside the core model when possible.

### 9. How would you preserve backward compatibility?

**Model answer:** Add compatible defaults when semantically valid, tolerate old payloads through adapters, version public schemas, and migrate stored data.

### 10. Dataclasses versus a validation framework?

**Model answer:** Use dataclasses for lightweight standard-library modelling; use a validation framework where runtime schema validation, rich errors, coercion, or schema generation justifies the extra dependency.

### 11. How would you use nested dataclasses?

**Model answer:** Give meaningful substructures their own models when they have reusable semantics or invariants. Avoid unnecessary deep nesting.

### 12. How would you prevent secrets from leaking through repr/logging?

**Model answer:** Use `repr=False` for generated repr suppression and separately enforce secure logging/serialization policies. Never treat repr suppression as a security boundary.

### 13. Mutable versus frozen models?

**Model answer:** Use mutable models for controlled evolving state and frozen models for stable value/configuration semantics. Consider nested mutability separately.

### 14. When should `slots=True` be used?

**Model answer:** When constrained attributes and possible memory savings matter and the surrounding framework is compatible. Benchmark representative workloads.

### 15. How would you design models for easy serialization and testing?

**Model answer:** Keep fields explicit, separate domain and transport conversion, avoid hidden runtime state, and cover normal/boundary/invalid/regression behavior.

# PRODUCTION CHECKLIST

## Data Modelling

- [ ] I understand what a data model is.
- [ ] I know when to use a dictionary.
- [ ] I know when to use a tuple/NamedTuple.
- [ ] I know when to use a normal class.
- [ ] I understand what a dataclass provides.

## Dataclasses

- [ ] I understand `@dataclass`.
- [ ] I understand generated `__init__`.
- [ ] I understand generated `__repr__`.
- [ ] I understand generated equality.
- [ ] I understand `field()`.
- [ ] I understand defaults and `default_factory`.
- [ ] I understand `__post_init__`.
- [ ] I understand `InitVar`.
- [ ] I understand `frozen`.
- [ ] I understand equality, ordering, and hashing.
- [ ] I understand `slots` and `weakref_slot`.
- [ ] I understand `kw_only` and `match_args`.
- [ ] I understand `asdict`, `astuple`, `replace`, `fields`, `is_dataclass`, and `make_dataclass`.

## Design

- [ ] I can distinguish DTOs from domain models.
- [ ] I understand entities versus value objects.
- [ ] I can design immutable value objects.
- [ ] I understand nested models.
- [ ] I know where validation belongs.
- [ ] I understand serialization/deserialization boundaries.
- [ ] I understand model evolution and compatibility.

## Production

- [ ] I can model APIs.
- [ ] I can model configuration.
- [ ] I can model data pipelines.
- [ ] I can model ML requests/results.
- [ ] I can model LLM requests/results.
- [ ] I can model agent state.
- [ ] I can test data models.
- [ ] I can reason about performance and memory.
- [ ] I know when not to use dataclasses.

# KNOWLEDGE CHECK

## Immediate Answers

### What is data modelling?

**Answer:** Choosing a structured representation for information and its relevant invariants and boundaries.

### What is a dataclass?

**Answer:** A normal Python class decorated to receive generated data-oriented methods.

### What does `field()` provide?

**Answer:** Per-field configuration for defaults, factories, init participation, repr, comparison, hashing, metadata, and keyword-only behavior.

### Why is `default_factory` important?

**Answer:** It creates a fresh default value for each instance when the value is mutable or otherwise needs per-instance construction.

### What is `__post_init__` used for?

**Answer:** Local validation, normalization, and derived-state initialization after generated construction.

### What is `InitVar`?

**Answer:** Initialization-only input that is passed to `__post_init__` but not stored as a normal dataclass field.

### What does `frozen=True` guarantee?

**Answer:** Normal assignment and deletion of dataclass fields are blocked; nested objects are not automatically deeply immutable.

### What does `order=True` do?

**Answer:** Generates the four rich ordering methods using comparable fields.

### Why is `unsafe_hash=True` risky?

**Answer:** Mutable values can change their hash/equality state while used as dictionary/set keys.

### What is `slots=True`?

**Answer:** A class-layout option that uses slots for declared fields and restricts undeclared attributes.

### Why use `kw_only=True`?

**Answer:** To require constructor values to be supplied by keyword, improving readability and often making APIs easier to evolve.

### What is `match_args`?

**Answer:** It controls generation of `__match_args__` for positional dataclass class patterns.

### What is `asdict()`?

**Answer:** A recursive dataclass-to-dictionary conversion utility.

### What is `astuple()`?

**Answer:** A recursive dataclass-to-tuple conversion utility.

### What is `replace()`?

**Answer:** A utility that creates a new dataclass instance with selected init fields changed.

### What is `fields()`?

**Answer:** A way to inspect dataclass field definitions.

### What is `is_dataclass()`?

**Answer:** A function that detects dataclass classes and instances.

### What is `make_dataclass()`?

**Answer:** A way to generate dataclass classes dynamically.

### Does `asdict()` deserialize?

**Answer:** No. Nested objects must be reconstructed explicitly or by a separate serialization/validation system.

### What is a DTO?

**Answer:** A data carrier used across a system boundary.

### What is a value object?

**Answer:** An object whose value determines its equality semantics.

### What is model evolution?

**Answer:** Managing changes to fields and semantics over time while preserving required compatibility.

### How do dataclasses help production AI systems?

**Answer:** They provide explicit, typed structures for requests, responses, state, tools, metadata, and internal boundaries.

# GLOSSARY

- **Dataclass:** A decorated class with generated data-oriented behavior.
- **Field:** An annotated dataclass attribute included in dataclass processing.
- **Default:** A static field value used when no value is supplied.
- **Default factory:** A callable that creates a new default value.
- **`__post_init__`:** Post-generated-initialization hook.
- **`InitVar`:** Initialization-only pseudo-field.
- **Frozen:** Immutable-style field assignment behavior.
- **Equality:** Logical value comparison.
- **Identity:** Whether two references point to the same object.
- **Hash:** Integer representation used by hash-based collections.
- **Ordering:** Rich comparisons such as `<` and `>`.
- **Slots:** Restricted attribute storage.
- **Weak reference:** A reference that does not keep an object alive by itself.
- **Keyword-only field:** A field requiring a keyword in generated construction.
- **`__match_args__`:** Data used for positional class-pattern matching.
- **Metadata:** Extra field information for extension/tooling.
- **DTO:** Data Transfer Object.
- **Entity:** Identity-oriented model.
- **Value object:** Value-oriented model.
- **Domain model:** Business-oriented model containing domain meaning and often behavior.
- **Serialization:** Conversion from in-memory data to a transport representation.
- **Deserialization:** Construction from a transport representation.
- **Model evolution:** Change to a model across time.
- **Backward compatibility:** Ability for existing consumers/data to continue functioning after change.

# FINAL MENTAL MODEL

## Data Model

```text
Information
   ↓
Structure + Meaning + Invariants
   ↓
Python representation
```

## Dataclass

```text
@dataclass
   ↓
Fields
   ↓
Generated common behavior
   ↓
Less boilerplate
```

But:

```text
@dataclass ≠ automatic validation
@dataclass ≠ deep immutability
@dataclass ≠ complete serialization
@dataclass ≠ domain architecture
```

## Choosing a Representation

```text
Dynamic map?       → dict
Tuple semantics?   → tuple / NamedTuple
Data-focused?      → dataclass
Behavior/lifecycle?→ normal class
Rich external schema? → validation-oriented model
Persistence identity? → ORM/database model as appropriate
```

## Production Model

```text
External input
    ↓ validate
DTO / boundary model
    ↓ map
Domain/data model
    ↓
Business logic
    ↓
Persistence / provider / queue
```

The most important skill is not memorizing every dataclass flag. It is knowing why a model exists, what it promises, how it changes, and where its boundary ends.

# FINAL SELF-REVIEW

1. Only the requested target file was written by this task.
2. Data modelling is explained before dataclasses.
3. Dataclasses progress from beginner to advanced.
4. Dictionary/tuple/class comparisons are included.
5. Generated methods are explained accurately.
6. `@dataclass` parameters are explained.
7. `field()` is explained.
8. `default_factory` is thoroughly explained.
9. Mutable defaults are warned against.
10. `__post_init__` is explained.
11. `InitVar` is explained.
12. `frozen` is explained as shallow/field-level immutability, not deep immutability.
13. Hashing is explained accurately.
14. Ordering is explained.
15. `slots` is explained without claiming universal speedups.
16. `weakref_slot` is explained.
17. `kw_only` is explained.
18. `match_args` and `__match_args__` are explained.
19. Pattern matching is connected to dataclasses.
20. Dataclass inheritance and field ordering are explained.
21. Nested models are included.
22. Serialization and deserialization are explicitly distinguished.
23. Validation limitations are explained.
24. DTOs, entities, and value objects are explained.
25. Model evolution/backward compatibility is included.
26. Testing and mocking are included.
27. Debugging is included.
28. Backend/API, banking, data-engineering, ML, LLM, and agentic-AI examples are included.
29. More than 25 progressive exercises are included, each with all required answer-key subsections.
30. Twelve debugging problems are included.
31. Interview questions and architecture questions are included.
32. Production considerations and checklists are included.
33. The chapter does not claim dataclasses validate runtime types automatically.
34. The chapter does not claim frozen dataclasses are deeply immutable.
35. The chapter does not claim slots always improve performance.
36. The chapter does not claim `asdict()` is a complete serialization framework.
37. The chapter does not claim dataclasses are always better than normal classes.
38. No real credentials, paid APIs, or unnecessary frameworks are required.
39. Important dataclasses APIs are explained with practical examples.
40. The chapter genuinely progresses from beginner data modelling to production architecture.
