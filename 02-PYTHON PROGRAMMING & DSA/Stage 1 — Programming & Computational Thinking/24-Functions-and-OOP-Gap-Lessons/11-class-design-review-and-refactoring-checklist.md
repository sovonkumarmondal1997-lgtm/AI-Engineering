# Class Design Review and Refactoring Checklist

> **Purpose:** a practical review instrument for Python classes, from a small value object to a production service. Use it alongside `07-function-design-review-and-refactoring-checklist.md`; neither checklist replaces domain understanding, tests, or engineering judgment.
>
> **Target:** Python 3.12+. Examples use standard-library typing and pytest-style tests. This is a learning and review guide, not a claim that any unavailable Stage 1 project source has been audited.

## 1. Learning objectives

By completing this lesson, you should be able to:

- Assess whether a class is the right abstraction and explain its purpose in one sentence.
- Review construction, invariants, public API, representation, equality, mutability, and tests.
- Find coupling, cohesion, lifecycle, inheritance, concurrency, and architectural risks.
- Choose a dataclass, function, value object, entity, service, port, or collaborator based on the problem.
- Recommend incremental refactorings that preserve externally observable behavior.
- Support findings with evidence, severity, a test or validation method, and a practical next action.
- Produce a review report that combines function-level and class-level findings for the Stage 1 consolidation capstone.

## 2. Scope and prerequisites

This lesson consolidates concepts introduced in Stage 1 Module 1.8 (Object-Oriented Design, Data Modelling and Functional Style), Module 1.9 (Production-Oriented Python Foundations), and Lessons 08–10 in this module. It previews—but does not replace—the later modules on the data model, descriptors, `__slots__`, MRO/cooperative inheritance, copying/pickling, deprecations, plugin extension points, security, and advanced testing.

Expected background:

- Functions, exceptions, modules, type hints, pytest, and basic object construction.
- Instance/class attributes, dataclasses, protocols, dependency injection, inheritance, and `super()`.
- Basic refactoring and the difference between a unit test and an integration test.

**Scope boundary:** use later-module material only as a review signal. Do not try to solve every descriptor, metaclass, serialization-hook, or multiple-inheritance problem inside this checklist.

## 3. How to perform a class design review

### 3.1 Review in caller-facing order

1. **Establish the contract.** Read the class docstring, constructor, public methods, call sites, tests, and relevant module boundaries. Ask what callers rely on, not only what the author intended.
2. **Map responsibility and state.** List the state the class owns, the rules it protects, the collaborators it calls, and the reasons it may change.
3. **Trace lifecycle.** Follow construction, normal method calls, errors, retries, cleanup, and shutdown. Check whether the object remains valid after every public operation.
4. **Inspect dependencies.** Follow imports and constructor parameters. Identify hidden globals, concrete infrastructure dependencies, circular imports, and dependency-direction violations.
5. **Run evidence-producing checks.** Execute relevant tests and quality gates when available. Record exact commands and outcomes; distinguish a command not run from a failure.
6. **Prioritize findings.** Address correctness, security, data loss, invariant breaks, and compatibility risks before style or speculative future flexibility.
7. **Propose small changes.** Prefer a characterization test and a sequence of reversible commits over a large rewrite.
8. **Review the caller again.** A design is not better if it makes the public API harder to understand or silently changes semantics.

### 3.2 Severity and priority rubric

Use severity for impact and priority for scheduling. Adapt this rubric to the team's incident and release process.

| Severity | Typical evidence | Response |
|---|---|---|
| **S0 — Critical** | Exploitable trust-boundary flaw, severe data corruption/loss, or a defect that invalidates a core safety guarantee | Stop release or mitigate immediately; add a regression test and involve the responsible owner |
| **S1 — High** | Public operation violates an invariant, common path fails, resource leak can exhaust the service, or a compatibility break is likely | Fix before release where practical; add targeted and regression tests |
| **S2 — Medium** | Strong coupling, repeated defects, poor testability, or a costly change path with a concrete example | Plan a bounded refactor; capture evidence and tests |
| **S3 — Low** | Naming, documentation, minor duplication, or a speculative concern with low current impact | Improve opportunistically; avoid blocking delivery without reason |

Security and correctness findings may be high severity even when the code is short. A large class is not automatically defective, and a low metric score is not proof of good design.

### 3.3 Quick 20-item scorecard for a focused review

The roadmap's larger refactoring exercise asks you to score a class against a 20-item checklist. Use this compact scorecard for that exercise, then use Sections 4–6 for detailed review questions. Mark each item `Pass`, `Concern`, `Fail`, or `N/A` and cite evidence; do not convert the result into a universal quality grade.

| # | Criterion | Evidence prompt |
|---:|---|---|
| 1 | Purpose and name | One-sentence purpose; name reflects it |
| 2 | Cohesion | State and methods share a responsibility |
| 3 | Abstraction fit | Class is simpler than a function/DTO/closure alternative |
| 4 | Construction | Valid object immediately after construction; no hidden I/O |
| 5 | Invariants | Invalid state is rejected or made unrepresentable |
| 6 | Mutable ownership | No accidental shared defaults or mutable aliases |
| 7 | Public API | Small, caller-oriented, documented surface |
| 8 | Encapsulation | Callers cannot bypass rules through public state |
| 9 | Representation | `repr` useful and secret-safe; `str` justified |
| 10 | Equality/hash | Identity/value semantics intentional and consistent |
| 11 | Types/docs | Public types and lifecycle/ownership notes are clear |
| 12 | Tests | Success, invalid input, transitions, equality, errors covered |
| 13 | Coupling | Dependencies explicit and narrow |
| 14 | Dependency direction | Domain does not depend on concrete infrastructure |
| 15 | Inheritance | Substitutability and `super()` chain are tested |
| 16 | State/lifecycle | Transitions, resource ownership, and cleanup are clear |
| 17 | Error safety | Failure preserves invariants where feasible |
| 18 | Concurrency | Shared state and thread/async guarantees are documented |
| 19 | Evolution/serialization | Public API and persisted schema have a compatibility plan |
| 20 | Operational fit | Performance/security/observability risks are checked against actual use |

A `Fail` on a correctness or security invariant is not offset by nineteen `Pass` marks. Record the three highest-impact findings separately.

### 3.4 Evidence record for every meaningful finding

Use a compact record:

- **ID / severity / priority:** `C-01 / S1 / P1`
- **Location:** file, class, method, and relevant line range or call site.
- **Observed behavior:** reproducible facts, not adjectives such as “bad” or “messy.”
- **Risk:** the user-visible or operational consequence.
- **Evidence:** test, traceback, call graph, dependency path, metric, or inspected state.
- **Recommendation:** the smallest change that removes or reduces the risk.
- **Validation:** regression test, contract test, type check, integration test, benchmark, or security check.
- **Status:** open, accepted, fixed, deferred with rationale, or not applicable.

### 3.5 Scoring without false precision

A team may mark each applicable criterion `Pass`, `Concern`, `Fail`, or `N/A`. Do not treat the number of concerns as an objective quality score: one S0 defect outweighs many passing style checks. Keep the checklist's role as a prompt for evidence-based discussion.

---

## 4. Beginner checklist — purpose, construction, and public contract

For each row, answer the review question and record evidence. Suggested severity is a starting point, not a fixed mapping.

| ID | Review question | Why it matters | Warning signs | Evidence to inspect | Recommended action | Typical severity | Validation |
|---|---|---|---|---|---|---|---|
| B1 Purpose and name | Can the class be described in one sentence? Does its noun match a domain concept or clear technical role? | A name frames the expected contract. | `Manager`, `Helper`, `Util`, or `Processor` accumulates unrelated work; the description contains several “and” clauses. | Docstring, public methods, call sites, module name. | Rename around the stable responsibility; split unrelated reasons to change only when evidence supports it. | S2–S3 | Caller/API review; focused unit tests remain unchanged. |
| B2 Cohesion | Do most methods operate on the same state and serve the same purpose? | Cohesion reduces change propagation. | Methods use disjoint groups of fields; only one method uses a dependency; several independent subsystems live together. | Method-to-state map; commit history; dependency list. | Extract a cohesive collaborator or move behavior to the object that owns the relevant data. | S2 | Unit tests for extracted behavior; inspect imports and coupling. |
| B3 Is a class needed? | Would a module function, dataclass, `NamedTuple`, `TypedDict`, closure, or existing type be simpler? | Classes add identity, lifecycle, and API surface; those costs need a reason. | Stateless namespace class; data-only class with handwritten boilerplate; one function wrapped without state or invariant. | Call sites, mutable state, equality expectations, tests. | Prefer a function for stateless work, DTO for boundary data, dataclass for data-centric values, or a class when behavior protects state/invariants. | S3, unless it causes real defects | Compare API and tests before/after. |
| B4 Construction | Is every instance valid immediately after `__init__`? Are required dependencies explicit? | Half-valid objects make every method harder to reason about. | Required fields assigned later by `setup()`; constructor opens network connections; silent sentinel values hide missing configuration. | `__init__`, factory methods, all construction call sites. | Validate required inputs and establish invariants in construction; move parsing/loading and I/O to factories or adapters. | S1–S2 | Valid/invalid constructor tests; factory tests. |
| B5 Mutable defaults | Does each instance receive its own mutable state? | Shared defaults can leak data between instances. | `def __init__(self, tags=[]):`; class-level list/dict used as per-instance state. | Constructor defaults, class attributes, mutation paths. | Use `None` or a sentinel and create a fresh container; copy inputs when ownership requires it. | S1–S2 | Construct two instances; mutate one; assert the other is unchanged. |
| B6 Public API | Are public methods few, verb-named, and caller-oriented? Are internals marked with `_`? | Public surface becomes a compatibility commitment. | Callers modify internal fields directly; many redundant getters/setters; methods expose implementation details. | Imports and usages across repository, docs, tests. | Minimize public methods; expose intention-revealing operations; keep implementation details private by convention. | S2–S3 | API tests and search for external/private-member use. |
| B7 Encapsulation and properties | Can callers violate invariants by assigning attributes or mutating returned collections? | Invariants must be protected at the boundary. | `obj.balance = -1` when forbidden; returning the internal list directly. | Setters, properties, collection-returning methods, mutation sites. | Validate state transitions; return immutable views/copies where needed; avoid properties that hide expensive I/O. | S1–S2 | Adversarial mutation tests; invariant tests. |
| B8 Representation | Does `repr(obj)` help debugging without leaking secrets? Is `str(obj)` user-facing only when needed? | Debug output should be useful and safe. | Tokens/passwords in `repr`; unstable memory-address-only representation for a domain value; `__str__` duplicates an unclear format contract. | `__repr__`, `__str__`, log statements, tests. | Include stable diagnostic fields; redact secrets; define user-facing `str` only when there is a clear need. | S1 if secret leakage; otherwise S3 | Representation tests and secret-redaction test. |
| B9 Equality and hashing | Is equality identity-based or value-based by design? Is hashing consistent with equality? | Incorrect equality can corrupt sets, dict keys, deduplication, or caches. | Mutable object used as a hash key; `__eq__` without a compatible hash policy; dataclass equality includes irrelevant fields. | `__eq__`, `__hash__`, dataclass options, collection use. | Choose entity identity versus value equality explicitly; prefer `@dataclass(frozen=True)` for simple value objects when appropriate. | S1–S2 | Equal values compare equal; hash contract tested only where hashability is intended. |
| B10 Typing and docs | Do public attributes and methods have meaningful annotations and docstrings explaining invariants? | Types and docs make the contract discoverable. | `Any` everywhere; vague `object`; undocumented units, mutability, lifecycle, or thread-safety. | Public signatures, README/API docs, examples. | Add precise types and explain units, ownership, failure behavior, and concurrency guarantees. | S2–S3 | Type checker; documentation build or API review. |
| B11 Tests | Are construction, public methods, invalid input, invariants, equality, and representation tested? | Tests define what callers may rely on. | Tests assert private implementation details only; no negative tests; no tests for method sequences. | Test suite, fixtures, mutation paths. | Add public-contract tests, boundary cases, and invariant checks after sequences of calls. | S1–S2 | `pytest`; coverage used as a gap-finding signal, not proof. |

### Beginner decision guide: choose the simplest correct abstraction

| Need | Often suitable | Be cautious when |
|---|---|---|
| Stateless transformation | Module-level function | The function is accumulating hidden state or many collaborators |
| Data transfer at a boundary | `TypedDict`, `NamedTuple`, or dataclass | Validation or behavior is substantial and needs a clear owner |
| Value with equality by its fields | Frozen dataclass or carefully designed value object | Fields need normalization, domain-specific operators, or custom invariants |
| Entity with identity and lifecycle | Class with explicit behavior and invariant protection | It is only a record and no lifecycle or domain rule exists |
| Orchestration around I/O | Service class/function with injected ports | Domain rules become buried in transport/database code |
| Several interchangeable algorithms | Function or strategy object behind a protocol | Inheritance is used only to avoid passing a collaborator |

---

## 5. Intermediate checklist — boundaries, state, collaboration, and change safety

| ID | Review question | Why it matters | Warning signs | Evidence to inspect | Recommended action | Typical severity | Validation |
|---|---|---|---|---|---|---|---|
| I1 Law of Demeter / tell-don't-ask | Does a caller navigate deep object graphs to calculate or mutate another object's state? | Deep knowledge creates coupling to internal structure. | Repeated `order.customer.address.city`; callers manually reproduce domain rules. | Call sites, repeated expressions, domain methods. | Move behavior to the object with the information; offer a meaningful operation rather than a getter chain. Do not hide every field behind a method mechanically. | S2 | Caller tests; test behavior at the owning abstraction. |
| I2 Collection ownership | Does the class protect internal collections from external aliasing? | A caller can bypass validation through a shared list/dict. | Store caller's list and return it directly; `list` property promises a snapshot but returns live state. | Constructor inputs, getters, mutation APIs. | Copy on input/output where ownership demands it; expose tuple or read-only view if suitable; document intentionally shared mutable state. | S1–S2 | Alias tests: mutate source and returned values. |
| I3 Dependency direction | Does the class depend on small abstractions rather than constructing concrete infrastructure? | Injected dependencies improve testing and limit coupling. | Constructor calls global database/client factory; imports web framework into domain model; module cycles. | Constructor signature, import graph, module boundaries. | Inject a `Protocol`/port; create concrete adapters at the composition root; move imports to a better layer. | S2, S1 if reliability/security affected | Fake collaborator tests; import-linter/dependency graph. |
| I4 Coupling and cohesion | Are collaborators few and related to the responsibility? | High fan-out makes changes risky and unit tests cumbersome. | Large constructor with many unrelated services; one class knows transport, persistence, formatting, and domain policy. | Dependency graph, constructor parameters, method usage. | Extract a cohesive collaborator; introduce a parameter object only when parameters form a meaningful concept; avoid splitting merely to lower a count. | S2 | Unit tests and dependency review. |
| I5 Inheritance suitability | Is the subtype genuinely substitutable for the base contract? Is `super()` chaining consistent? | Inheritance couples behavior and construction contracts. | Subclass changes meaning, rejects valid base inputs, skips parent initialization, or inherits only to reuse code. | Base and overrides, MRO, subclass tests. | Prefer composition/delegation for optional behavior; use `@override` where available and contract tests for true subtypes. | S1–S2 | Shared contract test suite; subclass compatibility tests. |
| I6 State model | Are valid states and transitions explicit? | Implicit combinations create impossible or ambiguous states. | Several booleans permit contradictory combinations; a `status` string accepts typos; method calls work in invalid order. | State fields, transition methods, error paths. | Use an enum or explicit state type and transition table where complexity justifies it; centralize transition checks. | S1–S2 | Transition matrix, invalid-transition tests, property-based tests. |
| I7 Lifecycle and resources | Who owns opening, closing, and cleanup? Is cleanup safe after partial failure? | Resource leaks and double-close behavior harm reliability. | Constructor opens file/socket without clear close contract; cleanup only on happy path; blocking cleanup in async code. | Context manager methods, `close`, `__aenter__`, `__aexit__`, call sites. | Make ownership explicit; use `with`/`async with`; make cleanup idempotent when appropriate; handle cancellation deliberately. | S1–S2 | Failure-injection and cleanup tests. |
| I8 Error behavior | Are domain exceptions specific and informative? Does failure preserve invariants where feasible? | Catching vague errors hides causes; partial mutation is dangerous. | `except Exception: pass`; generic `ValueError` for unrelated conditions; method mutates before validating. | Exception hierarchy, order of mutations, logs, caller retries. | Validate before mutation or use a rollback/transaction; raise meaningful exceptions and chain low-level errors with `raise ... from exc`. | S1–S2 | Invalid-input tests; failure injection; assert object remains valid. |
| I9 Mutability and thread safety | Is mutation necessary and is the concurrency contract documented? | Shared state can race even if individual methods look simple. | Mutable cache accessed by threads without policy; a frozen dataclass contains a mutable list; callers assume atomicity. | Mutable fields, async tasks, thread entry points, cache logic. | Prefer immutable values; use locks or confinement where needed; document non-thread-safe classes; do not assume the GIL makes compound operations safe. | S1–S2 | Deterministic concurrency tests where feasible; stress tests as supplemental evidence. |
| I10 Dataclass or handwritten class | Is generated behavior consistent with the domain semantics? | Dataclasses generate init/repr/eq/hash behavior that may be wrong for entities or mutable models. | Dataclass used for a resource-owning service; accidental equality includes cache/session fields; `frozen=True` mistaken for deep immutability. | Decorator options, fields, equality/hash use. | Use dataclasses for data-centric records; mark non-comparable fields `compare=False` when justified; write a class when lifecycle or custom behavior dominates. | S2–S3 | Construction/equality tests; type checking. |
| I11 Idempotency and retries | Can a retried operation duplicate side effects? | Retries are common in production pipelines. | `send()` or `charge()` is retried without idempotency key; operation updates state before a fallible call. | Retry caller, external API, persisted identifiers, transaction boundaries. | Separate pure decisions from side effects; use idempotency keys/transactional design; document at-least-once versus exactly-once claims precisely. | S1 | Retry simulation, duplicate-request tests, integration tests. |
| I12 Refactoring fit | Does a named refactoring solve a demonstrated problem without broad behavior change? | Mechanical changes need a safety net. | “Rewrite as clean architecture” without baseline tests; extract class that only adds indirection. | Characterization tests, diff size, callers, baseline metrics. | Use small steps: test, extract/move, inject, compare behavior, then simplify. | S2 | Characterization and regression tests after each step. |

### Refactoring patterns to consider

| Pattern | Use when | Guardrail |
|---|---|---|
| **Extract Class** | A cohesive group of state/methods has a separate reason to change. | Define ownership and API; avoid creating a pass-through object with no responsibility. |
| **Move Method** | A method repeatedly reaches into another object to use its data or rules. | Keep behavior with the state/rule owner; review dependencies to avoid cycles. |
| **Replace Primitive with Object** | A primitive has domain semantics, validation, units, or equality rules. | Use a small value object only when it centralizes real meaning. |
| **Replace Inheritance with Delegation** | A subclass only reuses code or changes behavior that should be independently selectable. | Preserve public behavior and test the delegated contract before removing the subtype. |
| **Introduce Parameter Object** | Several parameters always travel together and represent one concept. | Do not bundle unrelated values merely to reduce argument count. |
| **Strategy / Replace Conditional with Polymorphism** | A changing algorithm is selected by type or configuration. | A plain function/registry may be simpler than a hierarchy. |
| **Encapsulate Collection** | External callers can mutate internal state and bypass rules. | Preserve intentional bulk operations and avoid needless defensive copying of huge data. |
| **Hide Delegate** | Callers depend on too many internal collaborators. | Avoid creating a façade that merely forwards every method without improving the domain API. |
| **Remove Middle Man** | A class only forwards calls and adds no policy or boundary. | Keep a façade when it intentionally isolates a volatile subsystem. |

---

## 6. Advanced checklist — domain boundaries, operations, and evolution

| ID | Review question | Why it matters | Warning signs | Evidence to inspect | Recommended action | Typical severity | Validation |
|---|---|---|---|---|---|---|---|
| A1 Domain model | Is this an entity, value object, aggregate, service, or repository/port—and does the code match that role? | Different roles have different identity, lifecycle, and dependency rules. | Entity equality based on every mutable field; repository performs domain policy; aggregate exposes mutable internals. | Domain vocabulary, IDs, transaction boundaries, model methods. | Model identity/lifecycle in entities; immutable equality in value objects; enforce aggregate invariants; keep persistence behind ports/adapters. | S1–S2 | Domain invariant tests; repository contract tests. |
| A2 Anemic versus oversized model | Are core rules near the data they protect while orchestration and I/O stay at appropriate boundaries? | Both anemic models and god objects increase coupling. | Service performs all arithmetic and state transitions; entity owns HTTP client and SQL connection. | Call graph, imports, business rule locations. | Keep invariants in domain types; orchestrate in services; isolate I/O in adapters. A small script may not need a DDD architecture. | S2 | Unit tests for domain rules; integration tests for adapters. |
| A3 Functional core / imperative shell | Can deterministic business decisions be tested without database, network, or clock access? | Pure logic is easy to test and replay. | Domain method reads environment or current time directly; computation interleaves API calls and state changes. | Global reads, side effects, function signatures. | Inject time/randomness; make decisions pure; put effects in a narrow shell. | S1–S2 | Pure unit tests and adapter integration tests. |
| A4 Concurrency and async | Are shared mutable state, blocking calls, cancellation, and cleanup handled explicitly? | Races and cancellation leaks are operational failures. | Blocking network call inside `async def`; async generator/resource not closed; state assumes one task at a time. | `async` methods, locks, context managers, task ownership. | Use async-compatible clients; define ownership and cancellation behavior; lock or confine shared state; avoid holding locks across unrelated awaits. | S1–S2 | Cancellation tests, async integration tests, controlled concurrency tests. |
| A5 Memory and performance | Is object allocation or attribute overhead a measured bottleneck? | Premature micro-optimization can worsen design. | Millions of tiny objects without profiling; `__slots__` added without considering inheritance/weakrefs; expensive `cached_property` on every object. | Profiles, allocation snapshots, instance counts, workload. | Profile first; consider `slots=True`/`__slots__` for measured memory pressure; compare columnar/batched representations for large data. | S2–S3 | Representative benchmark and memory profile before/after. |
| A6 API evolution | Can the public constructor and extension points evolve without surprising callers? | Public signatures become long-term contracts. | New required positional arg breaks callers; undocumented private access is widespread; schema shape changes silently. | Call-site search, changelog, serialized fixtures, external usage. | Add optional/keyword-only parameters where compatible; deprecate before removal; version serialized schemas; document supported extension points. | S1–S2 | Compatibility tests, warnings tests, schema-version tests. |
| A7 Typing constructs | Do types express the actual boundary and extension contract? | Precise typing catches invalid states and reduces concrete coupling. | `Any` leaks everywhere; `Protocol` duplicates one implementation; `Literal` used for an unbounded domain; `TypedDict` treated as runtime validation. | Type signatures, runtime boundary validation, checker output. | Use `Protocol` for structural collaborators; `Self` for fluent methods that return the same subtype; generics for reusable relationships; `@final` to discourage unsupported subclassing; `@override` to catch signature drift; `Enum`/`Literal` for finite states; `TypedDict` for dictionary-shaped data. Validate untrusted data at runtime. | S1–S3 | `mypy --strict` or configured checker; boundary tests. |
| A8 ML/AI class conventions | Are estimator/transformer, dataset, model, configuration, tool, and prompt contracts explicit and reproducible? | Hidden work or mutable configuration harms reproducibility and serving parity. | Estimator trains or loads network resources in `__init__`; `transform` differs between training and serving; learned attributes not distinguished from parameters; tool accepts unchecked schema. | `fit`/`transform`/`predict`, `__len__`/`__getitem__`, config objects, prompt builders, tool schemas. | Store estimator parameters unchanged in `__init__`; perform learning in `fit`; use trailing-underscore convention for learned attributes when compatible with framework; separate immutable config from runtime state; validate tool input; version preprocessing and prompt templates. | S1–S2 | Reproducibility test, train/serve parity tests, schema validation tests. |
| A9 Architecture and module cohesion | Are dependencies flowing in the intended direction? Are circular imports or layer violations present? | Architecture-level cycles make changes and initialization unpredictable. | Domain imports a web framework or concrete DB implementation; cross-module cycles; broad import-time side effects. | Import graph, module responsibilities, `import-linter` output. | Move interfaces inward; construct adapters at the edge; break cycles by relocating shared abstractions to a stable module. | S2; S1 if deployment broken | Import graph checks, package import tests. |
| A10 Metrics and gates | Are metrics used as signals and thresholds introduced without freezing legacy code? | Thresholds can guide review but are not universal design laws. | Failing a build because a legacy class exceeds a magic line count; suppressing warnings globally. | Ruff/Pylint/radon config, trend history, baseline. | Enable relevant rules; ratchet gradually; justify suppressions locally; prioritize real behavior over raw counts. | S2–S3 | CI checks; compare trend and findings. |
| A11 CRC and caller-oriented design | Have responsibilities and collaborators been sketched, and was the API tested from the caller's viewpoint? | Early interaction design exposes missing responsibilities. | Class owns too much; collaborator relationship is unclear; caller must perform internal choreography. | CRC cards (Class–Responsibility–Collaborator), API examples, sequence diagrams. | Write one card per candidate class; list responsibilities and collaborators; write a small caller example before implementation. | S2–S3 | API-focused tests and pair/mob review. |
| A12 Serialization and schema | Is persisted state treated as a versioned boundary rather than a dump of internals? | Internal field changes should not silently corrupt old records. | Pickling arbitrary runtime services; serialization depends on private field layout; no schema version or migration path. | `to_dict`/`from_dict`, JSON fixtures, cache/job payloads. | Prefer explicit stable DTOs; add `schema_version`; validate during loading; avoid serializing live clients, locks, sockets, or secrets. | S1–S2 | Round-trip and backward-compatibility tests; untrusted-payload tests. |

### Lightweight domain-driven design vocabulary

- **Entity:** identity matters across state changes (for example, an `Account` identified by account ID).
- **Value object:** value defines equality; often immutable (for example, `Money(amount, currency)`).
- **Aggregate:** a consistency boundary whose public operations preserve a group of invariants. Avoid introducing aggregates when there is no consistency rule to protect.
- **Service:** coordinates an operation that does not naturally belong to one entity/value object; usually delegates to injected collaborators.
- **Repository/port:** a boundary that describes how the domain/application requests persistence or another capability without depending on a concrete adapter.

These labels are tools for reasoning, not mandatory class names or a requirement to build a large architecture for a small script.

### CRC card template

```text
Class / candidate:
Purpose (one sentence):
Responsibilities (verbs):
State/invariants owned:
Collaborators (what each supplies):
Public caller-facing operations:
What this class explicitly does NOT do:
Tests that prove the contract:
```

---

## 7. Class-design anti-pattern catalogue

| Smell | Diagnosis question | Common consequence | Refactoring direction | Avoid overcorrecting by… |
|---|---|---|---|---|
| God class / `*Manager` | Does one class own unrelated policies, storage, transport, reporting, and formatting? | High fan-out and multiple reasons to change. | Extract cohesive responsibilities; inject repository/notifier/formatter ports. | Splitting every method into a one-method class. |
| Anemic model | Are all invariants implemented elsewhere while the model is a mutable bag of fields? | Rules duplicated across services and callers. | Move core domain behavior to the model or a dedicated domain function. | Forcing every business operation into an entity even when it is orchestration. |
| Leaky encapsulation | Can callers mutate fields/collections to bypass validation? | Invalid state and aliasing bugs. | Encapsulate collection and expose intention-revealing operations. | Hiding every field without a meaningful contract. |
| Primitive obsession | Are raw strings/numbers carrying units, validation, or domain semantics? | Repeated validation and ambiguous values. | Introduce a value object or enum for stable domain meaning. | Wrapping every primitive in a new class. |
| Subclass per configuration | Does every combination of retry, formatting, transport, or policy require another subclass? | Combinatorial hierarchy and brittle changes. | Compose independent strategies; use a registry for supported implementations. | Replacing a clear two-branch conditional with an elaborate plugin system. |
| Inheritance for reuse | Is the subtype truly substitutable, or does it merely want a helper method? | Fragile base-class coupling. | Delegate to a collaborator or extract a function. | Removing inheritance where a stable subtype contract is valuable. |
| Feature envy / deep navigation | Does a method repeatedly inspect another object's fields? | Caller knows too much about collaborator internals. | Move the rule to the owner or introduce a focused operation. | Hiding data behind a chain of trivial getters. |
| Constructor doing work | Does construction perform network, database, filesystem, or training work? | Slow, flaky construction and difficult tests. | Keep construction cheap; use explicit factory/`connect`/`fit` operation. | Delaying required validation until a random later call. |
| Hidden lifecycle | Is ownership of close/cleanup unclear? | Leaks, double cleanup, cancellation bugs. | Context manager and explicit ownership. | Adding `close()` to a class that owns no resource. |
| Global/singleton dependency | Does the class reach global state rather than receive a dependency? | Non-determinism and test interference. | Constructor injection and a composition root. | Injecting trivial pure functions that do not need a seam. |
| Mutable shared defaults | Can one instance affect another through a shared container? | Cross-request state leakage. | Fresh containers, defensive copies, explicit shared cache abstraction. | Copying every large input without considering ownership/performance. |
| DTO with accidental behavior | Does a data transfer object also manage sessions and execute policy? | Unclear boundary and serialization complexity. | Keep DTOs data-focused; put behavior in domain/service layer. | Banning all useful methods on dataclasses. |
| Overabstracted framework | Are there interfaces/adapters for hypothetical variation only? | More indirection than behavior. | Start with the simplest working design; introduce seam when a second implementation or testing need exists. | Ignoring a real boundary or security constraint. |

---

## 8. Refactoring techniques and safe sequencing

### 8.1 The safe sequence

1. **Capture current behavior.** Add characterization tests around the public API, including edge cases and error behavior. Do not “correct” undocumented behavior silently if callers may rely on it.
2. **Record a baseline.** Note tests, lint/type-check output, dependency/coupling observations, relevant complexity metrics, and a representative performance measure if performance is part of the concern.
3. **Name the responsibility problem.** State the concrete change that is hard today: e.g. “adding a new channel requires editing the account domain and report formatter.”
4. **Choose one refactoring.** Extract a class, move a method, encapsulate a collection, introduce a parameter object, or replace inheritance with delegation. Avoid combining many transformations into one commit.
5. **Keep the public contract stable.** Add an adapter or deprecated wrapper if needed. Preserve return values, ordering, exceptions, timing assumptions, and side-effect semantics unless a deliberate behavior change is approved.
6. **Run focused tests after every step.** Then run the full suite and quality gates. Inspect the diff and search for old API usages.
7. **Compare the baseline.** Report what changed, what did not, and whether any metric worsened. Metrics are evidence, not the goal.
8. **Document decisions.** Use an ADR when the choice is consequential, non-obvious, affects public APIs, or establishes an architectural convention. A simple local extraction may need only a review note.
9. **Remove temporary compatibility code only through an explicit deprecation/removal step.** Check downstream callers before deletion.

### 8.2 Example eight-commit refactoring plan

For a class with persistence, notification, formatting, and domain rules, a reasonable plan could be:

1. Add characterization tests for current success/error behavior.
2. Add invariant and aliasing tests around its mutable state.
3. Extract the domain value object while retaining the existing façade.
4. Move formatting to a pure function or formatter collaborator.
5. Define small repository/notifier `Protocol`s and inject implementations.
6. Move persistence/notification wiring to the composition root.
7. Replace subclass-per-configuration behavior with a strategy/delegate where tests demonstrate the need.
8. Remove obsolete forwarding code, update docs, and add contract/architecture checks.

This is an example sequence, not a requirement to make exactly eight commits in every change. Keep each commit reviewable and revertible.

### 8.3 Before/after measurements

Record measurements that correspond to the stated problem. For example:

| Measure | Before | After | Interpretation |
|---|---|---|---|
| Public behavior tests | 8 | 14 | More boundary/invariant cases now cover the contract; test count alone does not prove quality. |
| Concrete infrastructure dependencies in domain class | 3 | 0 | Domain logic now receives ports; concrete adapters are wired at the edge. |
| Modules importing the concrete DB client | 5 | 1 | Dependency direction improved, assuming the one import is the intended adapter/composition root. |
| Cyclomatic complexity of a dispatch method | 11 | 4 | A decision point was decomposed; confirm the behavior is still easy to follow. |
| Runtime for representative 10k-item workload | Not measured | Not measured | Do not claim a performance improvement without a comparable benchmark. |

**Illustrative values only:** the numbers above demonstrate how to report measurements; they are not measurements of a supplied project. In an actual review, replace them with tool output or inspected facts. Never fabricate a baseline.

### 8.4 Architecture Decision Record (ADR) template

```markdown
# ADR-NNN: <decision title>

- Status: Proposed | Accepted | Superseded
- Date:

## Context
What concrete constraint or repeated change motivates this decision?

## Decision
What design will we use, and what is explicitly out of scope?

## Alternatives considered
- Option A — benefits, costs, risks
- Option B — benefits, costs, risks

## Consequences
Compatibility, operational impact, team ownership, performance, and future changes.

## Validation
Tests, metrics, migration steps, and conditions for revisiting the decision.
```

---

## 9. Tooling and automated review gates

Tooling should expose risk and make progress repeatable. Use project-pinned versions and document any local suppression.

### 9.1 Suggested checks

```bash
python -m pytest
ruff check .
ruff format --check .
mypy --strict src/
```

Run only commands that are installed and configured in the project. A successful command is evidence for that check—not proof of overall design quality. If a tool is unavailable, record `not run` rather than implying success.

### 9.2 Relevant Ruff rule families

Ruff's available rules depend on enabled/selectors and installed Ruff version. Review configured rules such as:

- `PLR0904` — too many public methods (pylint refactor family).
- `PLR0902` — too many instance attributes.
- `PLR0913` — too many arguments.
- `C901` — complexity prompt from the McCabe family.
- `SLF001` — private member access from outside a class/module boundary.
- `D` — docstring conventions.
- `ANN` — annotation coverage.
- `B023` — loop-variable binding mistakes in callbacks, useful for class-generated handlers too.
- `E731` and `FBT` where the project has chosen to disallow lambda assignment or ambiguous boolean flags.

These rules may require selecting the relevant families in `pyproject.toml`; they are not all necessarily enabled by default. Confirm rule codes and semantics against the installed Ruff version before standardizing them.

Example configuration fragment (adapt to the actual project; do not blindly replace existing configuration):

```toml
[tool.ruff.lint]
select = ["E", "F", "B", "C90", "D", "ANN", "PLR", "SLF", "FBT"]
```

A broad selection can surface many legacy findings. Roll it out with a baseline/ratchet, fix high-risk issues first, and avoid blanket ignores that hide future regressions.

### 9.3 Other useful tools

- **Pylint design checks:** class attributes, too-many-methods/arguments, inheritance and interface warnings.
- **Radon:** complexity and maintainability indicators; interpret alongside actual change risk.
- **import-linter:** encode allowed dependency directions and catch circular/layer violations.
- **mypy --strict:** useful when the codebase is ready to enforce explicit typing; type checking does not validate arbitrary runtime input.
- **vulture:** candidate dead code; verify dynamic registrations and plugin usage before deletion.
- **pytest-cov / mutation testing:** reveal untested branches and weak assertions; coverage is not correctness.
- **Profilers and tracemalloc:** use for measured runtime/allocation concerns, not to justify speculative optimization.

### 9.4 CI policy

- Fail new high-severity defects and regressions; avoid making legacy debt an all-at-once blocker.
- Ratchet complexity, type, and lint baselines gradually.
- Require tests for invariant changes and public API changes.
- Pin tool versions and keep configuration reviewable.
- Treat security, compatibility, and correctness findings separately from style warnings.

---

## 10. Worked example: notification orchestration class

> **Evidence label:** the following is an illustrative teaching example, not an audit of a real Stage 1 project. The supplied project tree and roadmap identify Stage 1 project descriptions, but a source class is not included in this example. Replace it with inspected project code when doing the capstone.

### 10.1 Flawed design

```python
from pathlib import Path
import json


class NotificationManager:
    """Load, validate, send, log, and export notifications."""

    def __init__(self, config_path: str, endpoint: str) -> None:
        self.config_path = config_path
        self.endpoint = endpoint
        self.sent: list[dict[str, str]] = []
        self.config = json.loads(Path(config_path).read_text())
        # Real code might also construct a network client here.

    def send(self, recipient: str, message: str, channel: str) -> bool:
        if not recipient:
            return False
        if channel == "email":
            # Imagine SMTP details here.
            result = True
        elif channel == "sms":
            # Imagine provider-specific details here.
            result = True
        else:
            return False
        self.sent.append({"recipient": recipient, "message": message, "channel": channel})
        self._write_log(recipient, channel, result)
        return result

    def _write_log(self, recipient: str, channel: str, result: bool) -> None:
        Path("notifications.log").open("a").write(
            f"{recipient},{channel},{result}\n"
        )

    def export_json(self, output_path: str) -> None:
        Path(output_path).write_text(json.dumps(self.sent))
```

Problems to verify in a real version:

- The constructor performs filesystem I/O and parsing, so even creating an object can fail because of the environment.
- Validation, channel dispatch, transport, logging, and export are mixed together.
- The `sent` collection is public and mutable; callers can rewrite history or insert malformed records.
- `False` merges invalid input, unsupported channel, and delivery failure into one outcome.
- Channel branches become a growing conditional as channels are added.
- The class uses a broad “Manager” name that does not communicate its contract.
- Resource ownership and error behavior are unclear; the example's simplified transport is not production-ready.
- `_write_log()` opens a file without a `with` block, so deterministic closure is not guaranteed by the code; its comma-separated format also does not escape commas or newlines in values. Prefer a context manager and a structured logger or `csv.writer` if a delimited file is the actual contract.
- `send()` appends to `sent` before the log write completes. If logging raises, the call fails but the in-memory history already contains the notification. Decide whether the history means “transport returned successfully” or “the whole operation completed,” then test that failure contract explicitly.

Not every issue must be fixed in one refactor. Start by writing tests for existing externally observable behavior and deciding which behaviors are intended contracts.

### 10.2 A more cohesive design

The corrected design separates a validated domain value, a transport protocol, orchestration, and export formatting. The sample uses in-memory behavior so tests can run without network or filesystem access.

```python
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Notification:
    """A validated notification request."""

    recipient: str
    message: str
    channel: str

    def __post_init__(self) -> None:
        if not self.recipient.strip():
            raise ValueError("recipient must not be empty")
        if not self.message.strip():
            raise ValueError("message must not be empty")
        if not self.channel.strip():
            raise ValueError("channel must not be empty")


class Notifier(Protocol):
    """Port implemented by an email, SMS, or other transport adapter."""

    def send(self, notification: Notification) -> None:
        """Deliver one notification or raise a meaningful exception."""


class NotificationService:
    """Validate and dispatch notifications while tracking successful sends."""

    def __init__(self, notifiers: dict[str, Notifier]) -> None:
        if not notifiers:
            raise ValueError("at least one notifier is required")
        # Own a shallow copy so callers cannot mutate our routing table later.
        self._notifiers = dict(notifiers)
        self._sent: list[Notification] = []

    @property
    def sent(self) -> tuple[Notification, ...]:
        """Return an immutable snapshot of successful notifications."""
        return tuple(self._sent)

    def send(self, notification: Notification) -> None:
        """Send through the configured channel and record success only."""
        try:
            notifier = self._notifiers[notification.channel]
        except KeyError as exc:
            raise ValueError(
                f"unsupported notification channel: {notification.channel!r}"
            ) from exc
        notifier.send(notification)
        self._sent.append(notification)


def notifications_to_records(
    notifications: tuple[Notification, ...],
) -> list[dict[str, str]]:
    """Convert notifications to plain records suitable for JSON encoding."""
    return [asdict(notification) for notification in notifications]
```

Why this is better for this example:

- `Notification` owns simple field invariants and has value semantics.
- `NotificationService` owns routing and the successful-send record; it does not read configuration files or open a network connection.
- A `Notifier` protocol lets a test fake or real adapter satisfy the same contract without inheritance.
- A copied routing dictionary prevents the caller from replacing routes through the original dictionary. The service still owns its private copy; if runtime route mutation is needed, provide a deliberate method.
- `sent` returns a tuple snapshot, so callers cannot append/remove from the service's internal list.
- Export formatting is a pure conversion function. The caller decides whether and where to write JSON.
- Delivery errors propagate instead of being silently converted into `False`; production code should define retry and error policies at the appropriate boundary.

Trade-offs: this introduces a protocol and a separate value type. For a tiny one-off script with one fixed channel, a function and a simple dictionary may be more appropriate. The design is justified when channel implementations vary, tests need a transport seam, or routing is a real responsibility.

### 10.3 Tests for the corrected design

```python
import pytest


class FakeNotifier:
    def __init__(self) -> None:
        self.calls: list[Notification] = []

    def send(self, notification: Notification) -> None:
        self.calls.append(notification)


def test_notification_rejects_blank_recipient() -> None:
    with pytest.raises(ValueError, match="recipient must not be empty"):
        Notification(recipient=" ", message="Hello", channel="email")


def test_service_dispatches_and_records_only_after_success() -> None:
    fake = FakeNotifier()
    service = NotificationService({"email": fake})
    notification = Notification("person@example.test", "Hello", "email")

    service.send(notification)

    assert fake.calls == [notification]
    assert service.sent == (notification,)


def test_unsupported_channel_has_context_and_does_not_record() -> None:
    service = NotificationService({"email": FakeNotifier()})
    notification = Notification("person@example.test", "Hello", "sms")

    with pytest.raises(ValueError, match="unsupported notification channel"):
        service.send(notification)

    assert service.sent == ()


def test_failed_delivery_is_not_recorded_as_success() -> None:
    class BrokenNotifier:
        def send(self, notification: Notification) -> None:
            raise OSError("provider unavailable")

    service = NotificationService({"email": BrokenNotifier()})
    notification = Notification("person@example.test", "Hello", "email")

    with pytest.raises(OSError, match="provider unavailable"):
        service.send(notification)

    assert service.sent == ()


def test_route_dictionary_is_copied() -> None:
    fake = FakeNotifier()
    routes = {"email": fake}
    service = NotificationService(routes)
    routes.clear()

    notification = Notification("person@example.test", "Hello", "email")
    service.send(notification)
    assert service.sent == (notification,)


def test_export_conversion_is_repeatable() -> None:
    notification = Notification("person@example.test", "Hello", "email")
    records = notifications_to_records((notification,))
    assert records == [{
        "recipient": "person@example.test",
        "message": "Hello",
        "channel": "email",
    }]
```

The test double is structurally compatible with `Notifier`; it need not inherit from it. In a production codebase, add adapter integration tests, safe logging tests, retry/idempotency tests if applicable, and schema/version tests for exported records.

### 10.4 Contract-test pattern for interchangeable implementations

A contract test runs the same observable requirements against each implementation of an interface. The following small example is executable and illustrates the pattern without requiring a framework or inheritance hierarchy.

```python
from decimal import Decimal
from typing import Protocol

import pytest


class DiscountPolicy(Protocol):
    def discount_for(self, subtotal: Decimal) -> Decimal: ...


class NoDiscount:
    def discount_for(self, subtotal: Decimal) -> Decimal:
        return Decimal("0")


class TenPercentDiscount:
    def discount_for(self, subtotal: Decimal) -> Decimal:
        return subtotal * Decimal("0.10")


@pytest.mark.parametrize(
    ("policy", "subtotal", "expected"),
    [
        (NoDiscount(), Decimal("10.00"), Decimal("0")),
        (TenPercentDiscount(), Decimal("10.00"), Decimal("1.0000")),
    ],
)
def test_discount_policy_contract(
    policy: DiscountPolicy, subtotal: Decimal, expected: Decimal
) -> None:
    discount = policy.discount_for(subtotal)
    assert Decimal("0") <= discount <= subtotal
    assert discount == expected
```

The same idea scales to repositories, notification transports, serializers, and subclasses: define caller-visible behavior once, then run it against every supported implementation. For real subclasses, also test base-class preconditions/postconditions and ensure overrides do not strengthen preconditions or weaken guarantees. A protocol establishes a static structural contract; it does not enforce runtime behavior by itself.

### 10.5 Review findings example

| Finding | Severity | Evidence in illustrative code | Recommendation | Validation |
|---|---|---|---|---|
| C-01 Constructor performs file I/O | S2 | `Path(config_path).read_text()` in `__init__` | Move loading/parsing to a factory or configuration adapter | Test object construction without filesystem access |
| C-02 Public mutable history | S2 | `self.sent` is a writable list | Encapsulate collection; expose immutable snapshot | Alias/mutation test |
| C-03 Transport and export mixed | S2 | `send` and `export_json` live together | Inject transport port; make conversion pure and write at edge | Unit test with fake notifier; pure conversion test |
| C-04 Failure semantics ambiguous | S1/S2 depending on callers | Invalid recipient and unknown channel both return `False` | Define domain errors and delivery failure contract | Invalid-input and failure-injection tests |
| C-05 Growing channel conditional | S2 when channels change often | Branches by channel inside service | Route to injected strategies/registry if variants are expected | Add a new fake channel without editing domain logic |

Severity depends on actual usage, data sensitivity, and whether callers rely on the old behavior. This is a worked illustration, not a claim about unseen project source.

### 10.6 Before/after comparison

| Dimension | Flawed example | Corrected example | What to verify in a real refactor |
|---|---|---|---|
| Construction | Reads file during construction | Receives an already-built routing map | Configuration parsing remains covered at the boundary |
| Responsibility | Dispatch, I/O, log, export | Domain value, dispatch, conversion are separate | No behavior was accidentally dropped |
| Dependencies | Knows filesystem and implied transports | Depends on a `Notifier` protocol | Concrete adapters are wired at the application edge |
| Failure semantics | Boolean collapses outcomes | Explicit validation error / transport exception | Callers are migrated or compatibility wrapper added |
| State ownership | Public list | Private list with tuple snapshot | Snapshot behavior matches intended contract |
| Tests | Requires environment for construction | Uses fakes and pure conversion | Integration tests still cover actual adapters |

No performance improvement is claimed: the corrected sample has not been benchmarked, and it is not intended as a drop-in production implementation.

---

## 11. Worked review report template

Use this structure for a real class. Clearly separate inspected facts, illustrative examples, and recommendations.

```markdown
# Class Design Review: <ClassName>

## Scope and evidence
- Repository/commit:
- Files and line ranges inspected:
- Tests and commands run (exact outcomes):
- Sources not available / assumptions:

## Contract summary
- Purpose:
- Public API:
- State and invariants:
- Collaborators and ownership:

## Findings
| ID | Severity | Evidence | Risk | Recommendation | Validation | Status |
|---|---|---|---|---|---|---|

## Baseline and follow-up measurements
- Tests:
- Complexity/coupling indicators:
- Performance/memory (only if measured):

## Refactoring plan
1. Small step + test
2. Small step + test

## Decisions / ADRs
- Decision needed? Why or why not?

## Residual risks and deferred work

## Reviewer conclusion
```

### Sample completed report (illustrative only)

**Class:** `NotificationManager` from Section 10.1. **Evidence status:** code shown in this lesson only; no external repository inspected.

| ID | Severity | Finding | Action | Validation | Status |
|---|---|---|---|---|---|
| C-01 | S2 | Constructor parses a file | Move file loading to boundary/factory | Test service construction with no filesystem | Proposed |
| C-02 | S2 | Public `sent` list bypasses ownership | Return immutable snapshot | Mutate returned value and verify internal history remains intact | Proposed |
| C-03 | S2 | Transport, logging, export coupled | Inject notifier; extract conversion function | Fake-based unit tests and adapter integration tests | Proposed |
| C-04 | S1/S2 | Boolean outcome conflates distinct failures | Define validation and delivery error contract | Failure matrix and caller compatibility tests | Proposed |

**Baseline metrics:** not measured. **Refactoring metrics:** not measured. The table records proposed actions, not completed changes. For a real review, replace all illustrative rows with observed evidence and test/tool results.

---

## 12. Exercises and solutions

### Exercise 1 — Is this class justified?

```python
class StringHelper:
    def normalize(self, value: str) -> str:
        return value.strip().casefold()
```

Decide whether to keep the class, and explain the criterion you used.

**Solution:** If the operation is stateless and has no configuration or invariant, a module-level `normalize_text(value: str) -> str` is simpler. Keep a class only if it represents a stable policy with meaningful configuration/state or forms a required extension point. Do not create a protocol solely because a second implementation might exist someday.

### Exercise 2 — Protect an invariant and internal collection

Implement `JobQueue` with these requirements:

- `Job` has a non-empty `job_id` and payload string.
- Queue starts empty.
- `enqueue` rejects duplicate IDs.
- `jobs` returns an immutable snapshot.
- Callers cannot mutate the queue through the returned collection or by changing a queued `Job`.

**Solution:**

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Job:
    job_id: str
    payload: str

    def __post_init__(self) -> None:
        if not self.job_id.strip():
            raise ValueError("job_id must not be empty")


class JobQueue:
    def __init__(self) -> None:
        self._jobs: list[Job] = []
        self._job_ids: set[str] = set()

    @property
    def jobs(self) -> tuple[Job, ...]:
        return tuple(self._jobs)

    def enqueue(self, job: Job) -> None:
        if job.job_id in self._job_ids:
            raise ValueError(f"duplicate job_id: {job.job_id!r}")
        self._jobs.append(job)
        self._job_ids.add(job.job_id)
```

The queue API accepts one `Job` at a time, not an input collection, so there is no bulk-input alias to test here. If a bulk-enqueue API is later added, test its input ownership separately. The current solution should be tested for blank IDs, duplicate rejection, unchanged state after rejection, and snapshot isolation:

```python
import pytest


def test_queue_starts_empty_and_returns_snapshot() -> None:
    queue = JobQueue()
    assert queue.jobs == ()

    job = Job("job-1", "payload")
    queue.enqueue(job)
    snapshot = queue.jobs

    assert snapshot == (job,)
    with pytest.raises(AttributeError):
        snapshot.append(job)  # type: ignore[attr-defined]
    assert queue.jobs == (job,)


def test_blank_job_id_is_rejected() -> None:
    with pytest.raises(ValueError, match="job_id must not be empty"):
        Job("  ", "payload")


def test_duplicate_job_id_does_not_change_queue() -> None:
    queue = JobQueue()
    job = Job("job-1", "payload")
    queue.enqueue(job)

    with pytest.raises(ValueError, match="duplicate job_id"):
        queue.enqueue(Job("job-1", "another payload"))

    assert queue.jobs == (job,)
```

Run these tests in the same module or fixture context as the `Job` and `JobQueue` definitions above. If the queue is shared across threads, this implementation needs a documented concurrency policy or synchronization; the GIL is not a complete thread-safety contract.

### Exercise 3 — Dataclass or handwritten value object?

A `Money` type needs amount/currency validation, equality by normalized currency and amount, readable representation, and no mutation after construction. Compare a handwritten class with a frozen dataclass. What would you choose?

**Solution:** Start with `@dataclass(frozen=True, slots=True)` if normalization and validation fit naturally in `__post_init__`. Use `Decimal` for decimal monetary amounts when appropriate, and define currency/rounding rules explicitly. A handwritten class is justified if equality, arithmetic, normalization, or construction semantics are materially different from generated dataclass behavior. `frozen=True` is shallow: nested mutable values would still be mutable, so keep value fields immutable.

### Exercise 4 — Replace subclass-per-channel with composition

A design has `EmailWithRetry`, `EmailWithoutRetry`, `SmsWithRetry`, `SmsWithoutRetry`, and matching Slack classes. Propose a smaller design and tests.

**Solution:** Model transport (`EmailSender`, `SmsSender`, `SlackSender`) and retry policy as separate collaborators satisfying small protocols. A notification service receives a sender and a retry policy. Test each sender contract, retry policy behavior, and service orchestration independently. A registry can map channel names to configured sender factories. Keep inheritance only if the subclasses share a stable substitutable contract; do not build a plugin registry if the application only has one fixed channel.

### Exercise 5 — Review a class with evidence

Choose a class from your own project. Complete the beginner checklist and at least six intermediate/advanced rows. Identify the three highest-impact findings. For each, write one review comment using the template below and specify the test that would demonstrate the risk.

**Solution outline:** There is no universal answer. A strong submission identifies the exact code/call path, states an observable consequence, proposes a small fix, and names a validating test. “This class is too big” is not enough; “`send()` writes to the DB before validating the recipient, so invalid input can create a partial record; move validation before the write and add a regression test” is actionable.

### Exercise 6 — Build the mini-project review in eight small steps

Select a class of at least 200 lines from an available Stage 1 project or a clearly identified open-source repository. Refactor in at least eight small commits. Track tests, coupling, complexity, and behavior after each meaningful step. Include an ADR if choosing between composition and inheritance is non-obvious.

**Solution outline:** Use the eight-commit sequence in Section 8.2 as a starting point. Do not invent metrics or claim unseen source review. For each commit record: intent, files changed, tests run, observed result, and remaining risk. The best final design is the one that improves the real change path without adding unnecessary abstractions.

---

## 13. Review-comment examples

Good comments are specific, respectful, and testable.

**High priority — invariant violation**

> `Account.balance` can be set directly to a negative value, bypassing the validation in `withdraw()`. Could we make the stored balance private and expose validated operations? Please add a test proving all public mutation paths preserve the non-negative-balance invariant.

**Medium priority — hidden dependency**

> This constructor creates the HTTP client internally, which makes timeouts and provider failures difficult to test in isolation. Could we inject a small client protocol and wire the concrete client at the application boundary? A fake-client test should cover the error path without network access.

**Medium priority — inheritance contract**

> This override rejects a value that the base class documents as valid, so callers typed against the base class may fail for this subtype. Could we preserve the base contract or use a separate strategy instead? Please run the shared contract tests against both implementations.

**Low priority — naming**

> `process()` appears to format a report rather than execute a domain transition. Would `render_report()` make the caller-facing intent clearer? No behavior change should be needed.

Avoid comments that merely express taste. If the risk is uncertain, ask a question and request evidence rather than declaring a defect.

---

## 14. Joint function-and-class review: Stage 1 consolidation capstone

The module roadmap calls for a **joint function + class design review** of one Stage 1 project, presented as if to a team lead. The class checklist is only one half of the review.

### 14.1 Scope and evidence discipline

1. Choose a project description under `00-Stage-1-Overview/Projects/` from the actual project tree.
2. Confirm whether the source implementation is available. A project description is not proof that a source file exists or behaves as described.
3. Select **two functions and two classes** from the actual implementation when available. If only a project brief is present, mark code findings as unavailable and create an explicitly labeled illustrative review plan instead.
4. Record repository revision, file paths, line ranges, exact commands, tests, and tool versions.
5. Separate observed facts, hypotheses, and recommendations.

### 14.2 Required deliverables

- `REVIEW.md` with function-level findings from Lesson 07 and class-level findings from this lesson.
- Before/after code snippets for completed refactorings, with tests demonstrating preserved behavior.
- Prioritized findings with evidence and owners or proposed next actions.
- Baseline and post-refactor measurements for relevant complexity/coupling indicators; runtime or memory claims only if measured comparably.
- Remaining recommendations and risks, including accepted/deferred items.
- An ADR for any consequential, non-obvious architecture choice.
- Commit history showing small, test-backed refactoring steps.

### 14.3 Suggested team-lead report structure

```markdown
# Stage 1 Consolidation Review

## Executive summary
- Most important risk:
- Highest-value completed fix:
- Decision needed from the team lead:

## Scope and evidence
- Project and revision:
- Two functions reviewed:
- Two classes reviewed:
- Files unavailable / scope limits:
- Tests and commands actually run:

## Prioritized findings
| ID | Area (function/class/architecture) | Severity | Evidence | Action | Validation | Status |
|---|---|---|---|---|---|---|

## Refactorings completed
- Commit / behavior preserved / tests:

## Before-and-after metrics
- Metric, tool, command, baseline, result, interpretation:

## Remaining risks and recommendations

## ADRs and decisions requested
```

### 14.4 Relationship to `gapcheck`

The module mini-project builds `gapcheck` with functional utilities, callable policies, and model examples such as `Money`, `Account`/`SavingsAccount`, `Celsius`, and `Config`. Its `REVIEW.md` should apply the function checklist to two functions and this class checklist to two classes, with before/after code and metrics. Include constructor/invariant tests, contract tests for subclasses, fake-clock tests for time-dependent behavior, and the configured quality gates. The acceptance target of at least 90% branch coverage is a project-specific goal, not a universal guarantee of correctness.

---

## 15. Self-check questions

1. What evidence would justify extracting a class instead of moving a function to a module?
2. How can a frozen dataclass still expose mutable state?
3. Why can returning a mutable internal list violate an invariant even if all class methods validate input?
4. What is the difference between an entity and a value object?
5. When should a service depend on a `Protocol` instead of a concrete repository/client?
6. What test demonstrates behavioral substitutability of a subclass?
7. Why is a class-size or public-method-count threshold a review signal rather than a universal law?
8. How would you preserve backward compatibility while changing a constructor?
9. What should happen to an object's state when an operation fails halfway through?
10. Which class behaviors should be pure, and which belong at an I/O boundary?
11. When is a strategy object justified, and when is a conditional clearer?
12. Which claims in your review are observed facts, and which are hypotheses or recommendations?

## 16. Summary

A good class has a clear purpose, cohesive responsibilities, valid state, a small caller-oriented API, explicit dependencies, and tests that verify public behavior and invariants. The best design is not necessarily the most object-oriented or abstract: it is the simplest design that keeps domain rules correct, changes localized, failures understandable, and operations testable. Use metrics to discover questions, not to replace judgment. Refactor incrementally, preserve observable behavior deliberately, and support every important finding with evidence.

## 17. Completion checklist

- [ ] I can explain each reviewed class's purpose, state, invariants, and collaborators.
- [ ] I considered whether a function, dataclass, value object, entity, service, or protocol is the simpler correct abstraction.
- [ ] I reviewed constructor behavior, mutable defaults, ownership, public API, representation, equality, and hashing.
- [ ] I tested invalid inputs and invariant preservation across method sequences.
- [ ] I reviewed encapsulation, Law of Demeter, coupling, dependency direction, and circular imports.
- [ ] I evaluated inheritance and `super()` against substitutability and considered composition where appropriate.
- [ ] I reviewed state transitions, resource ownership, failure behavior, idempotency, and concurrency assumptions.
- [ ] I considered domain boundaries, functional core/imperative shell, serialization, API evolution, and ML/AI conventions where relevant.
- [ ] I used automated checks as evidence and avoided universal metric laws.
- [ ] I proposed small refactoring steps with tests and recorded baseline/after measurements honestly.
- [ ] I can distinguish inspected facts from illustrative examples and unverified assumptions.
- [ ] I completed the joint function-and-class review for the module mini-project or Stage 1 consolidation capstone.

**Next:** use this checklist on real code, then revisit the relevant Stage 1 lessons on advanced data-model behavior, testing architecture, profiling, security, and refactoring as the evidence requires.
