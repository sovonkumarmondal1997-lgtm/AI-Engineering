# Module 06 — Type Hints and Type Checking
## Complete Lesson Summary, Project-Tree Assessment, and Exercise Solutions

> Scope: Module 1.6, Lesson 06. The source chapter is the authority for the concepts and exercise requirements below. The explanations are simplified for study, while retaining its terminology and Python-version distinctions.

# Part A — Complete Chapter Summary

## 1. Why types matter; Python's typing model

A **type** describes what kind of value an object is and which operations make sense for it. For example:

```python
age = 25          # int
name = "Rahul"    # str
price = 99.50     # float
active = True     # bool
```

Python values always have types. `"5" + 3` raises `TypeError` when executed because string concatenation cannot combine a string and integer. Python is **dynamically typed**: a name can refer to different types over time:

```python
x = 10
x = "hello"       # legal: x is a name, not a permanently declared int slot
```

Do not say Python has no type system. Python has a rich runtime type system; what it does not enforce by default is static type checking. A separate checker such as mypy or Pyright reads annotated source and detects inconsistencies before execution.

An unannotated function such as `def add(a, b): return a + b` leaves callers guessing whether numbers, strings, or lists are intended. Annotations make the function's intended contract visible, especially as projects and teams grow.

```python
def add(a: int, b: int) -> int:
    return a + b

add("hello", "world")  # Python executes string concatenation; a checker flags the call
```

**The central distinction:** Python executes according to actual runtime values. A type checker separately checks whether code agrees with its declared type contracts.

## 2. Type hints are not runtime validation

A type hint/type annotation is syntax attached to a variable, parameter, or return value:

```python
name: str = "Alice"
age: int = 30

def greet(name: str) -> str:
    return f"Hello, {name}"

def log_message(message: str) -> None:
    print(message)
```

`name: str` communicates the expected type. `-> str` communicates the expected return type. `-> None` explicitly promises that the function has no meaningful return value. A function with no explicit return annotation leaves that promise unstated.

Annotations do **not** automatically:
- reject a wrong value;
- convert `"10"` to `10`;
- validate data arriving from a file, JSON, CLI, environment variable, or API.

For example, `age: int = "twenty"` runs and binds a string. `set_age("banana")` can also execute even if the parameter is annotated `int`. A static checker reports the mismatch without running the program.

Keep four ideas separate:
1. **Type hint:** declaration of intended types.
2. **Static checking:** external analysis of source code.
3. **Runtime validation:** actual executed code that checks untrusted values and raises/returns controlled errors.
4. **Runtime enforcement:** Python automatically refusing an operation because an annotation was violated; ordinary Python annotations do not provide this.

This connects directly to the earlier Module 05 input-validation lesson: annotations describe what trusted internal code expects; validation establishes that an external value really meets that expectation.

## 3. Basic annotations and useful placement

Common types:

```python
username: str = "arjun"
retry_count: int = 3
timeout_seconds: float = 30.0
is_enabled: bool = True
payload: bytes = b"raw data"
result: None = None

MAX_RETRIES: int = 5
DEFAULT_TIMEOUT: float = 30.0
```

`bool` is technically a subtype of `int`, but type checkers and normal annotations treat it as its own meaningful type. `None` is the singleton no-value object and can appear as an annotation. Constants are conventionally uppercase; this is a naming convention, not a typing feature.

Do not annotate every obvious local variable just for volume. `count = 0` is usually inferable. Annotations are especially valuable at function boundaries, module-level declarations, constants, and configuration values whose intended type is not obvious.

## 4. Collections, tuples, mappings, and abstractions

Python 3.9+ supports built-in generic collection syntax:

```python
names: list[str] = ["Alice", "Bob"]
scores: dict[str, float] = {"Alice": 92.5, "Bob": 88.0}
unique_tags: set[str] = {"python", "typing"}
user_ages: dict[str, int] = {"alice": 30, "bob": 25}
user_scores: dict[str, list[int]] = {"alice": [85, 90], "bob": [78]}
```

The inner type specifies the expected elements, keys, or values. A checker can flag `names.append(42)` against `list[str]`; Python itself will still allow that mutation at runtime. `frozenset[str]` describes an immutable set of strings.

Tuple annotations express shape:
- `tuple[str, int]`: exactly two elements, first string and second integer.
- `tuple[float, float]`: two floats, such as x/y coordinates.
- `tuple[int, ...]`: any number of integers.
- `tuple[str, ...]`: any number of strings.

Use fixed-length tuples when each position has its own meaning; use the ellipsis form for a homogeneous tuple of variable length.

Nested types compose: `dict[str, list[int]]` means string keys mapped to integer lists. A vague `dict[str, object]` is sometimes honest for unknown data, but the checker cannot safely assume a value supports arithmetic or string operations until it is narrowed.

Prefer behavioral abstractions from `collections.abc` when a function does not need a concrete container:

```python
from collections.abc import Sequence

def total(values: Sequence[float]) -> float:
    return sum(values)
```

- `Iterable[T]`: can be used in a `for` loop; no promise of length or indexing.
- `Iterator[T]`: iterable that also supports `next()`; typically a stateful, single-pass cursor.
- `Sequence[T]`: ordered, sized, indexable collection; lists and tuples satisfy it.
- `Mapping[K, V]`: read-only key-to-value lookup interface; dictionaries satisfy it.

Engineering rule: accept the most general abstraction your implementation genuinely needs, and return the most specific type you actually guarantee.

## 5. Optional values, unions, aliases, and finite choices

`str | None` (Python 3.10+) means a string or exactly `None`. Older equivalent syntax is `Optional[str]`. The caller must narrow before using string-only operations:

```python
def find_user(user_id: int) -> str | None:
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)

user_name = find_user(3)
if user_name is not None:
    print(user_name.upper())
else:
    print("User not found")
```

A union such as `int | str` says either type is intentionally accepted. Older equivalent syntax is `Union[int, str]`. A huge union often signals that a function is doing too many unrelated jobs.

A **type alias** gives an existing type a meaningful name; it does not create a new distinct type:

```python
UserId = int
Coordinates = tuple[float, float]
```

Python 3.12+ preferred explicit syntax is `type UserId = int`. `TypeAlias` is an explicit portable alternative for 3.10/3.11, but is deprecated since 3.12 in favor of the `type` statement. Match syntax to the project's `requires-python`/target version.

`Literal` restricts a value to a finite set of exact values:

```python
from typing import Literal

Mode = Literal["development", "production"]

def configure(mode: Mode) -> None:
    ...
```

A checker rejects `"prod"` as outside the declared set. It is useful for stable, small choices such as HTTP methods, statuses, and log levels. It is static-only and creates no runtime enum object.

`Enum` creates a genuine runtime type with namespacing, iteration, and runtime rejection of invalid values (`Mode("staging")` raises `ValueError`). Plain string constants provide neither static literal restriction nor Enum runtime guarantee. Use `Literal` when the value should remain a plain serialized string; use `Enum` when the choice has runtime/domain significance.

## 6. `Any`, `object`, `Never`, and callable values

`Any` opts a value out of static checking. Operations and assignments involving it are broadly accepted, and the loss of precision propagates to derived values:

```python
from typing import Any

def parse(data: Any) -> Any:
    return data["result"]["items"][0]
```

This can allow invalid operations to pass silently. Use `Any` narrowly when information genuinely is unavailable, such as an untyped dependency.

`object` is a real base type that can represent any Python object, but the checker permits only operations guaranteed for all objects. Narrow it before type-specific use:

```python
def describe(value: object) -> str:
    if isinstance(value, int):
        return f"an integer: {value}"
    if isinstance(value, str):
        return f"a string: {value}"
    return f"something else: {value!r}"
```

Prefer `object` to `Any` for unknown values when you want to retain type-checker protection.

`Never` (Python 3.11+) / older `NoReturn` describes a function that never returns normally because it always raises or does not terminate:

```python
from typing import Never

def fail(message: str) -> Never:
    raise RuntimeError(message)
```

`assert_never` can support exhaustive handling: if a `Literal`/Enum later gains a case that is not handled, the checker can report that the supposedly unreachable branch is now reachable.

`Callable` describes a function-like value:

```python
from collections.abc import Callable

def apply_operation(operation: Callable[[int, int], int],
                    a: int, b: int) -> int:
    return operation(a, b)

def add(x: int, y: int) -> int:
    return x + y

result = apply_operation(add, 3, 4)  # 7
```

`Callable[[int, int], int]` means two integer parameters and an integer result. It is useful for callbacks and simple dependency injection; use a `Protocol` when several methods must be described together.

## 7. Generics and type variables

A `TypeVar` preserves a relationship between input and output types:

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]
```

A `list[int]` produces an inferred `int`; a `list[str]` produces `str`. `Any` would accept both but lose this relationship.

A generic class applies the same principle to an object:

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, item: T) -> None:
        self.item = item

    def get(self) -> T:
        return self.item

int_box: Box[int] = Box(42)
str_box: Box[str] = Box("hello")
```

Built-in containers (`list[T]`, `dict[K, V]`) are generic too.

Python 3.12+ PEP 695 syntax declares parameters inline:

```python
def first[T](items: list[T]) -> T:
    return items[0]

class Box[T]:
    def __init__(self, item: T) -> None:
        self.item = item
    def get(self) -> T:
        return self.item
```

Use this only when the project's minimum Python is 3.12+. For older supported versions, use `TypeVar`/`Generic[T]`.

A **bound** says a type variable can be any subtype of a specified type/capability. A **constraint** says it must resolve to one member of a closed list:

```python
TNumber = TypeVar("TNumber", int, float)

def double(value: TNumber) -> TNumber:
    return value * 2
```

A bound is open-ended and preserves a caller's more specific subtype. A constraint is a closed choice and resolves to the listed type (a subclass of `int` is promoted to `int` in this example). Use a bound when the implementation needs a capability; use constraints for a genuinely small closed set.

## 8. Type narrowing, `TypeGuard`, and `TypeIs`

A union must be narrowed before using operations that apply to only one member:

```python
def describe(value: str | int) -> str:
    if isinstance(value, str):
        return value.upper()
    return str(value * 2)
```

A checker follows `isinstance`, `is None`/`is not None`, appropriate truthiness checks, `assert`, and control flow such as `return` and `raise`. Runtime code actually evaluates the condition; the checker separately reasons about the branches statically.

`TypeGuard` lets a custom Boolean-returning function tell the checker what type an argument has when it returns true:

```python
from typing import TypeGuard

def is_str_list(items: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(item, str) for item in items)
```

The helper must genuinely check the claimed property. `TypeIs` is a related, newer narrowing tool that communicates a type relationship and can narrow both the true and false branches more precisely; choose it when its stricter subtype relationship is appropriate. Neither decorator magically validates data: the function body must perform the actual runtime check. `TypeGuard` is useful for a custom predicate that narrows an argument on a true result. `TypeIs` (Python 3.13+) is a related alternative with more precise narrowing in both true and false branches; it requires Python 3.13+, so do not use it if the project's supported interpreter is older. For a 3.12 baseline, recognize it but use a compatible alternative unless the minimum version is raised.

## 9. Structural typing: `Protocol` vs inheritance and ABC

A `Protocol` describes required behavior. A class satisfies it structurally by having compatible methods/attributes; it need not inherit from the protocol:

```python
from typing import Protocol

class Storage(Protocol):
    def save(self, item: str) -> None: ...

class FileStorage:
    def save(self, item: str) -> None:
        print(item)

class MemoryStorage:
    def save(self, item: str) -> None:
        print(item)
```

Both classes can be passed where `Storage` is expected if their signatures match. This supports loose coupling, test fakes, provider abstraction, and dependency injection.

Inheritance is nominal: the class declares its relationship through a base class. An **abstract base class (ABC)** can enforce that concrete subclasses implement abstract methods at runtime when instantiated. A `Protocol` primarily gives static structural compatibility; it does not force unrelated classes to inherit or automatically enforce method presence at runtime. Use ABCs when shared implementation/runtime inheritance contract is needed; use Protocol when consumers need a behavior contract independent of class hierarchy.

A protocol method must have `self` for an ordinary instance method. Implementations must be callable in a way compatible with the protocol: an extra required parameter breaks substitutability.

## 10. Domain data modeling

A plain alias improves readability but does not distinguish values. For stronger domain modeling use:
- `NewType` (advanced section): creates a static distinction such as `UserId` vs ordinary `int`, with no runtime wrapper enforcement.
- `TypedDict`: describes the expected keys and value types of a dictionary. It remains an ordinary `dict` at runtime and does not validate external data.
- `dataclass`: creates a real class with attribute access and generated methods such as `__init__` and `__repr__`.
- `ClassVar`: marks a class-level shared attribute rather than an instance field.
- `Self`: annotates methods returning the same actual class as the receiver, including subclasses; useful for fluent/chained APIs.

Example:

```python
from dataclasses import dataclass
from typing import TypedDict

UserId = int

@dataclass
class User:
    id: UserId
    name: str

class UserPayload(TypedDict):
    id: int
    name: str
```

`TypedDict` can model optional keys as well as optional values. `total=False` makes all declared keys optional; `Required[...]` and `NotRequired[...]` allow required and optional keys to be mixed (Python 3.11+). Nested TypedDicts model nested JSON-like records. Remember that required-key presence is still a runtime validation concern. Use `TypedDict` for dictionary-shaped payloads and dataclasses for domain objects with real attributes/behavior. `ClassVar[T]` marks a class-level shared attribute so it is not treated as an instance field. `-> Self` (Python 3.11+) is more subclass-safe than returning the base class's concrete name from a chainable method.

## 11. Forward references and runtime annotation introspection

A forward reference mentions a type before its definition or refers to a class within its own annotation. It can be written as a quoted name or supported by:

```python
from __future__ import annotations
```

The future import postpones evaluation of annotations, reducing definition-order problems and helping with circular type references. Runtime annotation representation can vary with Python version and future-import behavior.

`__annotations__` exposes annotation data at runtime. `inspect.get_annotations()` is recommended on Python 3.10–3.13; Python 3.14+ also provides `annotationlib.get_annotations()` and deferred annotation evaluation by default. Evaluating annotations can execute expressions or raise `NameError` for unresolved names, so do not casually evaluate annotations from untrusted code. Frameworks may use annotation introspection to build validation, serialization, or dependency-injection behavior; that runtime framework behavior is distinct from static checking. These are runtime metadata, not a static checker. A checker reasons about source and types; introspection reads stored annotation objects/strings after import.

## 12. Static type checkers and development workflow

mypy and Pyright/basedpyright analyze code without running it. They infer types, follow control flow, check calls/assignments/returns, and report violations of the declared contracts. They do not prove business correctness or replace runtime validation.

A practical workflow:
1. Declare the supported Python version and configure the checker in `pyproject.toml`.
2. Run the checker locally and inspect diagnostics.
3. Annotate public functions and important module boundaries.
4. Fix real errors rather than silencing them reflexively.
5. Integrate the checker as an independent CI gate.
6. Keep Ruff, type checking, and tests as separate checks.

Ruff handles fast linting/formatting and selected static rules; it is not a full type checker. Tests execute code and verify selected behavior; a checker analyzes type consistency without execution. A program can pass one and fail another, so all three are complementary.

Type-checking modes range from permissive to strict. Start at a level the current codebase can sustain, then tighten gradually. `reveal_type(value)` is a checker diagnostic for inspecting inferred types; it is not an ordinary runtime function and should not be left as a runtime call unless a tool/runtime explicitly provides it.

Type inference means the checker derives types from assignments, expressions, and function bodies. Explicit annotations remain important at public APIs, module boundaries, configuration, ambiguous empty collections, and places where the intended contract is broader or more specific than a literal would reveal.

## 13. Common type-checking errors and None-safety

Common diagnostics include:
- incompatible assignment;
- wrong argument type;
- incompatible return type or missing return path;
- possibly-`None` access;
- missing/incorrect attribute or method;
- untyped or overly broad collection;
- incompatible override/protocol implementation;
- incorrect callable signature;
- invalid union operation;
- untyped dependency/`Any` leakage.

`None` safety matters at real boundaries. A lookup may return nothing; a config key may be absent; a JSON field may be missing; a CLI option may be omitted; a path operation may fail. Represent this honestly with `T | None` or a specific exception, then narrow before using the value. Do not lie to the checker to avoid handling absence.

Use early returns/raises to make control flow obvious:

```python
user = repository.get(user_id)
if user is None:
    raise ValueError("user not found")
return user.name
```

## 14. Untrusted data: JSON, CLI, environment, filesystem

External values begin as untrusted. A type hint on a variable does not validate what was decoded or read. The safe architecture is:

**raw `object` → parse and validate at boundary → typed representation → business logic → output**

- **JSON:** `json.loads()` can produce different shapes/types. Check the outer container, required keys, and each value; convert validated values into a `TypedDict`/dataclass/domain model.
- **CLI:** `argparse` can convert basic values, but cross-field/business constraints still need validation. Treat omitted optional arguments as possibly `None`.
- **Environment:** environment values are strings or missing. Parse them explicitly; do not assume `PORT` is already an integer or `DEBUG` is already a Boolean.
- **Filesystem:** paths and file operations can fail or return absent values. Annotate path interfaces and handle `None`/exceptions and I/O errors explicitly.

Type hints improve the contract after validation; runtime checks make the contract true.

## 15. Typed modules, packages, dependencies, stubs

Annotate public interfaces between modules first. A data-access module might expose `get_user(user_id: UserId) -> User | None`; a service module consumes that contract and owns business rules. Keep imports and dependencies directed cleanly to avoid circular dependencies.

Package exports (`__init__.py`) can define a deliberate public API. Type annotations at those boundaries make refactoring safer and help IDEs/checkers understand usage.

Third-party packages may provide inline annotations or `.pyi` **stub files**. A stub describes a module's interface for static tools; it is not the runtime implementation. `py.typed` is a marker included by a package to signal that its inline typing information is intended to be consumed by type checkers. Untyped dependencies can introduce `Any` at the boundary. Prefer maintained stubs or small local boundary wrappers rather than spreading `Any` through the application.

## 16. Ruff, tests, documentation, IDEs, refactoring, API design

- **Ruff:** formatting/linting; separate from full type checking.
- **Tests:** execute behavior; annotations do not prove behavior and tests do not prove all type paths.
- **Documentation:** annotations provide structured, machine-readable API documentation, but do not replace explanations of business rules.
- **IDE:** uses annotations/checker information for completion, navigation, parameter hints, and refactoring support.
- **Refactoring:** typed boundaries expose callers affected by a signature change; still run tests.
- **API design:** use precise inputs/outputs, explicit optionality, small unions, and stable domain types. Accept abstractions when appropriate; return concrete guarantees.

## 17. Engineering applications

**Backend services:** type request/response models, service interfaces, repositories, and optional lookup results. Validate incoming requests before constructing trusted domain objects.

**Data engineering:** model raw records separately from validated/normalized records and output records. Type transformation stages so a function expecting validated data cannot accidentally receive raw input. Use `Decimal` for exact money rather than float where appropriate; model CSV/JSON fields as strings until converted and validated; use `Iterable` for streaming input and a `Protocol` for pluggable sinks.

**Machine learning:** distinguish raw features, validated feature records, model inputs, predictions, and evaluation outputs. Type interfaces for data loaders, model adapters, and metrics. Annotations do not validate tensor shape, numerical range, schema, or model quality; explicit checks/tests still matter.

**Applied AI/agent systems:** define provider/client protocols for model invocation, embedding, retrieval, tool execution, and persistence. Use dependency injection to swap providers, fakes, and test implementations. Give request/response and tool payloads explicit types, validate untrusted model/tool outputs, and keep provider-specific details behind adapters.

**Protocol-based provider abstraction:** define the minimum operations the service requires, e.g. `generate(prompt: str) -> str`; provider adapters implement it. The business service depends on the protocol, not a vendor SDK. This reduces coupling and makes testing and provider changes easier.

**Dependency injection:** pass repository/client/sink dependencies into functions or constructors rather than constructing concrete implementations deep inside business logic. Type the dependency against a Protocol so production and test implementations can both satisfy the same contract.

## 18. Advanced typing tools

- **`overload`:** multiple static signatures for one function whose return type depends on input shape. Provide `@overload` declarations followed by exactly one real implementation broad enough to handle them. Overloads aid static analysis; they do not create multiple runtime functions.
- **`cast(T, value)`:** tells the checker to treat a value as `T`; it performs no runtime conversion or validation. Use only when another mechanism establishes the fact.
- **`NewType`:** creates a distinct static domain type based on an existing type, e.g. `UserId = NewType("UserId", int)`. It helps prevent mixing semantically different integers but does not add runtime validation.
- **`Final`:** marks a name as not intended to be reassigned (and can mark final class members); checker-enforced, not a universal runtime immutability mechanism.
- **`Annotated[T, metadata]`:** keeps the base type `T` while attaching metadata for tools/frameworks. A checker generally treats the base type as `T`; metadata has meaning only to consumers that understand it.
- **`ParamSpec`:** captures a callable's complete parameter signature for decorators/wrappers, preserving parameter types.
- **`Concatenate`:** adds/removes leading parameters in a callable signature, commonly for decorators that inject a dependency such as a request/session.
- **`TypeAliasType`:** the runtime object created by the modern `type` statement (Python 3.12+). It is distinct from a plain assignment such as `UserId = int`, which simply binds another name to the same type object. `type UserId = int` creates an explicit alias object that tools can inspect; it is still an alias, not a new nominal domain type like `NewType`.

These tools solve specific API/type-expression problems. Avoid using them merely because they are advanced.

## 19. Gradual typing, legacy migration, strictness, CI, pre-commit, performance

Python supports **gradual typing**: annotated and unannotated portions can coexist. You do not need to type an entire repository before a checker is useful.

A sensible migration sequence:
1. Inventory modules and choose a supported Python version/checker.
2. Start with critical modules and public entry points.
3. Annotate public functions and module boundaries.
4. Add precise domain/data models.
5. Annotate internal helpers and remove unnecessary `Any`.
6. Fix diagnostics and introduce stronger checking incrementally.
7. Make the selected checks part of CI and maintain the policy.

For a large repository, define team rules: checker, version, scope, strictness, baseline, allowed suppressions, and ownership. Avoid a massive one-time strict migration that blocks delivery. Use targeted ignores with explanations and remove them over time.

CI should independently run locked environment setup, Ruff format check, Ruff lint, type checker, and tests. Each should fail the pipeline on a non-zero exit. Pre-commit can run quick local checks, but CI remains authoritative because local hooks can be skipped or environments differ.

Type checking generally has development-time cost, not application runtime cost. Annotations can have import/introspection implications depending on evaluation strategy, but ordinary static checking does not execute application code. Keep checker scope and cache/configuration practical in monorepos.

## 20. Common beginner mistakes and final mental model

Avoid:
- believing annotations enforce runtime types;
- using `Any` to silence every diagnostic;
- using `object` and then skipping narrowing;
- writing bare `list`/`dict` when element types are known;
- annotating an optional result as non-optional;
- using `if value` when an explicit `is not None` is needed;
- confusing a type alias with `NewType`;
- confusing `TypedDict` with runtime validation;
- assuming Protocol means inheritance;
- writing a Protocol method with a wrong signature or missing `self`;
- using Python 3.12 syntax when the project supports older Python;
- using `cast` as if it converts/checks;
- forgetting the real implementation after `@overload`;
- using `Self` incorrectly in subclassable fluent APIs;
- treating Ruff, tests, and type checking as interchangeable;
- annotating only local variables while leaving public boundaries vague;
- suppressing errors instead of understanding them.

The complete mental model is:
1. Python values always have runtime types; Python is dynamically typed.
2. Annotations express intended contracts.
3. Static checkers analyze those contracts without executing the program.
4. Runtime validation checks untrusted data.
5. Narrowing connects checks to safe use.
6. Protocols and domain models define modular interfaces.
7. Tests verify actual behavior.
8. Ruff checks formatting/lint rules.
9. CI runs these independent layers consistently.

# Part B — Project-Tree and Current-Level Assessment

## Roadmap position

Your known Stage 1 roadmap contains 24 modules, covering computational thinking, Python fundamentals, control flow/functions/errors, collections/algorithms, files/structured data/CLI, modules/packages/dependencies/code quality, testing/debugging, OOP/data modeling, and advanced production-oriented Python. The four Stage 1 capstones are:

1. Personal Expense Ledger CLI.
2. Log Investigation and Reliability CLI.
3. Data Quality and Transformation Pipeline (`dqpipe`) with CLI, config, pipeline, rules, tests, and data contract.
4. Rule-Based Risk Review Engine (`riskreview`) with CLI, engine, I/O, models, rules, tests, and golden decision data.

## Current demonstrated foundation

Before this lesson, the completed Module 05 work included text files, pathlib, CSV, JSON, encodings/newlines, argparse, standard streams/exit codes, logging, environment configuration, and input validation. Module 1.6 Lessons 01–05 covered imports/`__main__`, project/package layout, `pyproject.toml`/lock files/`uv`, dependency management/SemVer, and Ruff formatting/linting.

That is an appropriate foundation for this chapter. You already have the prerequisites to understand typed function boundaries, configuration validation, package interfaces, dependency protocols, and CI quality gates. Your current level is beginner progressing toward intermediate in Python engineering; this lesson is a step from single-program correctness toward maintainable multi-module engineering.

## How this lesson fits the roadmap

Lesson 06 adds static contracts to the engineering practices already learned:
- Module 05 validation ensures runtime input is valid.
- Module 1.6 Lessons 01–04 establish module/package/dependency structure.
- Lesson 05 Ruff checks formatting/lint rules.
- Lesson 06 adds static type checking.
- The next roadmap topic is not started here.

## Applying types to your four Stage 1 projects

- Expense Ledger: type money/transactions/categories; use `Decimal` where exact currency arithmetic is required; represent missing lookups as `T | None`; validate CSV/CLI data before creating trusted records.
- Log Investigation CLI: type parsed log records, filters, severity values, and report outputs; use `Literal`/Enum for finite levels where appropriate.
- `dqpipe`: distinguish raw CSV row, validated row, transformed record, and output; use `TypedDict` for dictionary-shaped records, dataclasses for domain objects, and `Protocol` for storage/output adapters.
- `riskreview`: model transaction/rule/decision types; use Protocol for rule or policy providers; use explicit unions and `None` handling for optional decision evidence.

The immediate mastery target is not advanced typing syntax everywhere. It is accurate annotations on public functions, precise collection types, explicit optionality, runtime validation at boundaries, and running a type checker independently from Ruff and tests.

# Part C — All 21 Coding Exercises, Solved Step by Step

The examples target the chapter's stated Python 3.12+ baseline where modern `[T]` syntax is used. Where useful, a portable `TypeVar` alternative is shown.

## Level 1 — Basic

### 1. Annotate three variables and justify the annotations

```python
count: int = 0
names: list[str] = ["Alice", "Bob"]
config_value: object = load_config_value()
```

- `count: int`: the literal already makes the type obvious, so the annotation is optional.
- `names: list[str]`: useful because it documents the element contract, especially if the list is later mutated.
- `config_value: object`: appropriate when the source is not yet known; narrow it before type-specific operations.
- `load_config_value()` represents an existing function in the application; the exercise is about the receiving variable's contract.

### 2. Annotate a two-parameter function

```python
def calculate_total(price: float, quantity: int) -> float:
    return price * quantity
```

- `price: float` declares the expected unit price.
- `quantity: int` declares a whole-number quantity.
- `-> float` declares the returned total.
- The annotation documents and enables static checking; it does not convert a string price at runtime.

### 3. Add `-> None` to a print-only function

```python
def show_status(message: str) -> None:
    print(message)
```

`message: str` describes the input. `-> None` explicitly states that callers should not expect a meaningful result. Without it, the checker may infer the behavior, but the public contract is less explicit.

### 4. Annotate list, dictionary, and fixed tuple

```python
names: list[str] = ["a", "b"]
ages: dict[str, int] = {"a": 1}
record: tuple[str, int, bool] = ("x", 1, True)
```

- `list[str]`: any number of strings.
- `dict[str, int]`: string keys and integer values.
- `tuple[str, int, bool]`: exactly three positions with those types in that order.

### 5. Identify a wrong argument from the signature

```python
def calculate_total(price: float, quantity: int) -> float:
    return price * quantity

calculate_total("9.99", 3)
```

The first argument is the mismatch: `price` expects `float`, but receives `str`. `quantity` is correct (`int`). Python may execute string repetition, so this is a static-contract error even if no runtime exception occurs.

## Level 2 — Intermediate

### 6. Return `str | None` and narrow at the call site

```python
def find_name(user_id: int) -> str | None:
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)

name = find_name(1)
if name is not None:
    print(name.upper())
else:
    print("User not found")
```

The function honestly represents a missing lookup. `is not None` narrows `name` to `str` in the first branch; only there is `.upper()` safe. The `else` handles absence.

### 7. Rewrite `Optional[int]`

```python
# Older:
# def retry_count(value: Optional[int]) -> None: ...

# Modern Python 3.10+:
def retry_count(value: int | None) -> None:
    if value is not None:
        print(value + 1)
```

`Optional[int]` and `int | None` mean exactly the same thing. The union operator is preferred when the project's minimum Python version supports it.

### 8. Define and use a three-field `TypedDict`

```python
from typing import TypedDict

class CustomerRow(TypedDict):
    customer_id: int
    name: str
    active: bool

def describe_customer(customer: CustomerRow) -> str:
    return f"{customer['name']} ({customer['customer_id']})"

def make_customer(customer_id: int, name: str, active: bool) -> CustomerRow:
    return {
        "customer_id": customer_id,
        "name": name,
        "active": active,
    }
```

The class describes the expected dictionary keys and their value types. The consumer reads those keys; the factory builds a dictionary matching the contract. `TypedDict` does not validate an external dictionary at runtime.

### 9. Create a domain type alias

```python
UserId = int

def load_user(user_id: UserId) -> str | None:
    users = {1: "Alice"}
    return users.get(user_id)
```

`UserId` makes the domain meaning visible at every interface. It remains exactly `int`; it does not prevent another integer from being passed. Use `NewType` only when a distinct static identity is required.

### 10. Generic function returning the last sequence item

```python
from collections.abc import Sequence

def last[T](items: Sequence[T]) -> T:
    if not items:
        raise ValueError("items must not be empty")
    return items[-1]
```

`T` captures the element type. A `Sequence[int]` returns `int`; a `Sequence[str]` returns `str`. The empty check makes the runtime behavior safe and justifies the non-optional return type. For older Python versions:

```python
from typing import TypeVar
T = TypeVar("T")

def last(items: Sequence[T]) -> T:
    if not items:
        raise ValueError("items must not be empty")
    return items[-1]
```

### 11. Narrow a `str | int`

```python
def normalize(value: str | int) -> str:
    if isinstance(value, str):
        return value.strip().upper()
    return str(value * 2)
```

Inside the first branch, the checker knows `value` is a string. After that branch returns, the remaining possible type is integer, so multiplication is valid. Each branch performs a type-appropriate operation.

## Level 3 — Advanced

### 12. Protocol with two unrelated implementations

```python
from typing import Protocol

class Notifier(Protocol):
    def send(self, recipient: str, message: str) -> bool: ...
    def health_check(self) -> bool: ...

class EmailNotifier:
    def send(self, recipient: str, message: str) -> bool:
        return True
    def health_check(self) -> bool:
        return True

class ConsoleNotifier:
    def send(self, recipient: str, message: str) -> bool:
        print(f"{recipient}: {message}")
        return True
    def health_check(self) -> bool:
        return True

def notify(client: Notifier, recipient: str, message: str) -> bool:
    return client.send(recipient, message)
```

Neither implementation inherits from `Notifier`. Both satisfy it by exposing compatible methods. `notify()` depends on behavior, not a vendor/class hierarchy.

### 13. Bounded type variable requiring a method

```python
from typing import Protocol

class HasTotal(Protocol):
    def total(self) -> int: ...

def calculate[T: HasTotal](item: T) -> int:
    return item.total()
```

The bound tells the checker that every permitted `T` has `total()`. The function can safely call that method. For pre-3.12 syntax, declare `T = TypeVar("T", bound=HasTotal)` and use `def calculate(item: T) -> int`.

### 14. `TypeGuard` for `list[int]`

```python
from typing import TypeGuard

def is_int_list(items: list[object]) -> TypeGuard[list[int]]:
    return all(isinstance(item, int) and not isinstance(item, bool)
               for item in items)

values: list[object] = [1, 2, 3]
if is_int_list(values):
    total = sum(values)
```

The helper checks every element and returns true only when all are integers. The `not isinstance(item, bool)` condition is included because Python's `bool` is a subtype of `int`, while this example intends ordinary integers. In the true branch, the checker treats the list as `list[int]`.

### 15. Two overloads and one implementation

```python
from typing import overload

@overload
def repeat(value: str, count: int) -> str: ...

@overload
def repeat(value: int, count: int) -> list[int]: ...

def repeat(value: str | int, count: int) -> str | list[int]:
    if isinstance(value, str):
        return value * count
    return [value] * count
```

The overload declarations describe the input/output relationship to the checker. They are not separate runtime implementations. The final function executes and handles both cases.

### 16. Fluent class using `Self`

```python
from typing import Self

class QueryBuilder:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def select(self, fields: str) -> Self:
        self.parts.append(f"SELECT {fields}")
        return self

    def where(self, condition: str) -> Self:
        self.parts.append(f"WHERE {condition}")
        return self
```

Both methods return the actual receiver. `Self` preserves a subclass's type through chaining; returning `QueryBuilder` would make a checker see the base type even when the receiver is a subclass.

## Level 4 — Production

### 17. Annotate public functions first

Before:

```python
def read_amount(row):
    return float(row["amount"])

def summarize(rows):
    return sum(read_amount(row) for row in rows)
```

After defining the expected row shape:

```python
from typing import TypedDict
from collections.abc import Iterable

class AmountRow(TypedDict):
    amount: str

def read_amount(row: AmountRow) -> float:
    return float(row["amount"])

def summarize(rows: Iterable[AmountRow]) -> float:
    return sum(read_amount(row) for row in rows)
```

The public `summarize` contract is made explicit first, then the helper. In a real ingestion boundary, validate the raw row and amount before treating it as `AmountRow`; these annotations alone do not validate CSV data.

### 18. Typed boundaries between data access and business logic

`repository.py`:

```python
from dataclasses import dataclass

@dataclass
class Order:
    order_id: int
    amount: float

def get_order(order_id: int) -> Order | None:
    # Replace with actual storage access.
    return None
```

`service.py`:

```python
from .repository import Order, get_order

def order_total(order_id: int) -> float:
    order: Order | None = get_order(order_id)
    if order is None:
        raise ValueError(f"order {order_id} not found")
    return order.amount
```

The repository owns data access and communicates absence explicitly. The service owns business behavior and narrows the optional result before accessing `.amount`. The import is a package-relative import consistent with the earlier package lesson.

### 19. Type an API/service function with an optional field

```python
from dataclasses import dataclass

@dataclass
class Customer:
    customer_id: int
    name: str
    email: str | None

def customer_response(customer: Customer) -> dict[str, int | str | None]:
    return {
        "customer_id": customer.customer_id,
        "name": customer.name,
        "email": customer.email,
    }
```

The input is a domain object; output is a dictionary with known value possibilities. `email` is explicitly optional. At a real API boundary, serialize and validate according to the API schema; the return annotation is not a serializer or validator.

### 20. Add CI type checking

Example `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
files = ["src"]
check_untyped_defs = true
warn_return_any = true
```

First install the chosen checker as a development dependency and run it locally. Fix or baseline current findings. Then add an independent CI command, for example `uv run mypy src`, after Ruff checks and before/alongside tests. Make a non-zero exit fail CI. Do not assume a successful Ruff run means type checking passed.

### 21. Migrate a partially typed repository

1. Inventory modules, runtime support, and checker configuration.
2. Prioritize critical modules and public entry points.
3. Annotate public functions and module boundaries.
4. Add domain models and precise collection types.
5. Annotate internal helpers and narrow/remove `Any`.
6. Fix diagnostics; use narrow, documented temporary suppressions only when justified.
7. Raise strictness gradually and enforce the chosen policy in CI.

A partially typed repository is valid: gradual typing allows annotated and unannotated code to coexist. Prioritize modules with high business impact, frequent changes, and clear interfaces rather than trying to annotate everything in one large change.

# Part D — Debugging Lab Solutions

The source's `inventory.py` example has six issues:

1. `find_item()` promises `Item` but falls through and implicitly returns `None`. Change its return type to `Item | None` and explicitly `return None` after the loop.
2. `total_quantity(items: list)` uses an unparameterized list. Change it to `list[Item]` so `item.quantity` can be checked.
3. `get_metadata()` returns a known dictionary but declares `Any`. Use `dict[str, str | int]`, or a `TypedDict` if the shape is reused.
4. `restock(..., amount)` and `FileStorage.save(..., path)` omit parameter annotations. Use `amount: int` and `path: Path`.
5. `Storage.save` omits `self`. For an instance method, declare `def save(self, item: Item) -> None: ...`.
6. `FileStorage.save(self, item, path)` requires an extra argument not in the protocol. Remove `path` or make it optional with a default so the method remains callable using the protocol's signature.

The corrected protocol and implementation must agree:

```python
class Storage(Protocol):
    def save(self, item: Item) -> None: ...

class FileStorage:
    def save(self, item: Item) -> None:
        ...
```

# Part E — Complete Example Projects: What to Learn

## 1. Typed service project

The source's `typed-service/` project separates `models.py`, `repository.py`, `service.py`, `client.py`, and `main.py`.

- `UserId = int` is a readable alias.
- `User` is a dataclass domain object.
- `UserPayload` is a TypedDict describing a dictionary payload.
- `UserRepository` is a Protocol implemented by an in-memory repository.
- `first_or_none()` demonstrates a generic `Sequence[T]` helper.
- `parse_user_payload()` accepts untrusted `dict[str, object]`, checks each required value with `isinstance`, and returns a validated `UserPayload`.
- `register_user()` validates before constructing/saving the domain object.
- `get_user_or_raise()` explicitly handles a missing repository result.
- `NotificationClient` is a Protocol; the console implementation can be replaced.
- `main()` is a thin entry point and uses the `__main__` guard.

The architecture is **untrusted input → validation → typed model → business logic → dependency interface**. Ruff, a type checker, and tests provide independent quality checks.

## 2. Production-ready typed data-processing service

The source's mini-project demonstrates this pipeline:

`raw input → parse/validate → ValidatedRecord → transform → ProcessedRecord → RecordSink`

- `RawRecord` is a TypedDict describing expected input keys (`id`, `amount`, `category`).
- `ValidatedRecord` and `ProcessedRecord` are separate dataclasses, making pipeline stages explicit.
- `parse_record(raw: object)` does not trust the annotation of the input. It checks dictionary shape, required keys, and string value types.
- It converts the ID to `int`, parses money from a string into `Decimal`, rejects invalid/non-finite/negative amounts, and raises a controlled `RecordValidationError`.
- `apply_tax()` is typed business logic. `Decimal("0.08")` and `Decimal("0.01")` avoid binary floating-point currency representation; `ROUND_HALF_UP` states the rounding policy.
- `RecordSink` is a Protocol. Console and in-memory implementations can be substituted.
- `run_pipeline()` accepts `Iterable[object]`, validates each item, skips controlled invalid records, writes processed records, and returns a count.
- Tests verify tax calculation and that invalid records are skipped while a valid record continues through the pipeline.

This is the strongest data-engineering lesson in the chapter: **types describe each stage, runtime validation establishes trust, and distinct models prevent raw records from being accidentally passed into transformations that require validated data.**

# Part F — Interview Questions (22) and Architecture Questions (7)

## Interview questions and concise answers

1. **What are type hints?** Annotations describing intended variable, parameter, and return types for readers and static tools.
2. **What is dynamic typing?** Runtime values determine a name's current type; Python checks operation validity when executed.
3. **What is static type checking?** A separate tool analyzes annotated source without executing the program.
4. **Do hints enforce runtime types?** No. They do not convert or reject values by themselves.
5. **What does `-> str` mean?** The function promises to return a string.
6. **Optional vs Union?** `Optional[T]` equals `T | None`; a general union such as `int | str` represents alternatives.
7. **`list[str]` vs `list[Any]`?** The first lets the checker enforce string elements; the second largely opts element operations out of checking.
8. **`Any` vs `object`?** `Any` disables checking; `object` accepts any value but requires narrowing before type-specific use.
9. **TypedDict vs dataclass?** TypedDict models a dictionary's key/value shape; dataclass creates a real class with attributes and generated methods.
10. **Alias vs NewType?** Alias renames an existing type; NewType creates a distinct static type identity.
11. **What is TypeVar?** A placeholder preserving a relationship between types, often input and output.
12. **What is Generic?** A class/function parameterized by type variables.
13. **What is Protocol?** A behavioral contract checked structurally.
14. **Structural typing?** Compatibility depends on provided methods/attributes, not declared inheritance.
15. **TypeGuard?** A function return annotation that tells a checker what type an argument has when the function returns true.
16. **overload?** Multiple static signatures for one runtime implementation.
17. **ParamSpec?** Captures a callable's full parameter signature, useful for typed decorators.
18. **Legacy migration?** Prioritize critical modules/public interfaces, type them, then helpers, and tighten gradually.
19. **Large-repository strategy?** Set team policy, target version, checker, strictness, baseline, and suppression rules; migrate incrementally.
20. **Ruff + checker + tests?** Run as independent quality gates because they check different properties.
21. **External API boundaries?** Treat payload as untrusted, validate shape and values, then convert to typed domain models.
22. **Protocol for decoupling?** Define required behavior in a Protocol and inject concrete provider/repository implementations.

## Architecture questions and answers

1. **Where should type checking occur in CI?** As its own independent stage, not hidden inside Ruff or tests.
2. **Which boundaries deserve strong typing?** Public module APIs, service/repository interfaces, configuration, data contracts, and external provider adapters.
3. **How should an AI platform type model providers?** Define small Protocols for required operations and implement adapters for each provider.
4. **How does Protocol support provider abstraction?** Business logic depends on the interface, so SDK/provider implementations can be swapped or faked in tests.
5. **How should a pipeline represent raw vs validated data?** Use separate input and validated domain models; validate at ingestion and type each transformation stage.
6. **How should a monorepo adopt strict typing?** Establish shared configuration, start with high-value packages, track debt, and tighten package-by-package.
7. **How should service interfaces be typed?** Specify request/response models, explicit optionality/errors, stable domain types, and versioned contracts.

# Part G — Knowledge Check (40 Answers)

1. A type categorizes data and determines valid operations.
2. Dynamic typing means the runtime value determines the name's current type; static checking analyzes type consistency before execution.
3. A hint communicates intent to readers/checkers; it does not enforce runtime values.
4. Annotation is metadata/contract; runtime validation is executed checking/conversion logic.
5. `age` is a `str`; `print(type(age))` prints `<class 'str'>`.
6. `list[str]` says every element should be a string; bare `list` does not specify element type.
7. `tuple[str, int]` is fixed length and heterogeneous; `tuple[str, ...]` is variable length and homogeneous.
8. `str | None`.
9. Each union member widens accepted inputs and reduces what can be assumed without narrowing.
10. An alias gives an existing type a meaningful name; it does not create a new type.
11. `Any` disables checking for that value and contaminates derived values with the same permissiveness.
12. `object` preserves checking and requires narrowing before type-specific operations.
13. `Never`/`NoReturn` says a function never returns normally.
14. A callable taking two integers and returning an integer.
15. TypeVar preserves the relationship between the actual input element type and output type; Any loses it.
16. A bound accepts any subtype of a base/capability; a constraint resolves to one of a closed list.
17. The checker needs to follow the code's actual control flow and checks.
18. TypeGuard communicates a narrowed argument type on a true result; its function must really check the property.
19. Protocol structural typing checks required behavior rather than inheritance.
20. ABC uses inheritance and can enforce abstract methods at instantiation; Protocol primarily supports static structural compatibility.
21. TypedDict models a dictionary's expected key/value shape; it is not runtime validation.
22. Dataclass creates a real class with attributes and generated methods.
23. ClassVar marks a class-level shared attribute, not an instance field.
24. Self preserves the actual possibly-subclassed receiver type in return annotations.
25. A forward reference names a type defined later or itself; quoting or postponed annotations resolves definition-order issues.
26. `__annotations__` stores runtime annotation metadata; static checking analyzes source independently.
27. No. A static checker reads/analyzes code without executing the program.
28. Type inference derives types from expressions/assignments; explicit annotations remain valuable at public boundaries and ambiguous declarations.
29. `reveal_type` asks a checker to report its inferred type; it is not generally an ordinary runtime function.
30. Examples: wrong argument, incompatible assignment, missing return path, unsafe None access, wrong Protocol signature.
31. System boundaries frequently produce absent values; explicit optionality prevents unsafe dereferencing.
32. Hints are static and do not inspect/validate actual external payloads.
33. `py.typed` signals that a package's inline type information is intended for type checkers.
34. Untyped dependencies can cause values to become Any, weakening checks at that boundary.
35. Ruff performs formatting/lint checks; a type checker analyzes type consistency.
36. Type consistency does not prove business logic or runtime correctness.
37. Hints are machine-readable API contracts used by IDEs, documentation tools, and checkers.
38. `@overload` requires one real implementation covering the declared signatures.
39. `cast()` changes the checker's view only; it does not convert or validate the runtime value.
40. CI must run type checking independently because local checks can be skipped and Ruff/tests do not replace it.

# Part H — Mastery Checklist

- [ ] Explain dynamic typing vs static checking accurately.
- [ ] Explain why annotations do not validate or convert runtime values.
- [ ] Annotate parameters, returns, collections, and optional values.
- [ ] Choose concrete vs abstract collection interfaces appropriately.
- [ ] Use `Any` narrowly and `object` with narrowing.
- [ ] Understand aliases, Literal, Enum, TypeVar, Generic, bounds, and constraints.
- [ ] Use `isinstance`/None checks and understand TypeGuard/TypeIs.
- [ ] Design Protocol-based interfaces and dependency injection.
- [ ] Choose TypedDict vs dataclass for the right data shape.
- [ ] Type public module boundaries and external input pipelines.
- [ ] Distinguish Ruff, type checking, and tests.
- [ ] Run type checking locally and in CI.
- [ ] Migrate gradually without blocking all work on a whole-repository rewrite.

## Final learning position

Lesson 06 is complete in this guide. The priority is to apply the core features to the existing Stage 1 projects: typed public functions, precise collections, `T | None`, validated boundary data, dataclasses/TypedDict where appropriate, and Protocols for replaceable dependencies. Advanced features should be learned in context rather than applied indiscriminately. No next lesson is started here.
