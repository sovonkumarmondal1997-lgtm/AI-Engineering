# Modern Python Language Features — Practice Questions and Answer Key

**Module:** Stage 1 — Programming & Computational Thinking, Module 1.15  
**Source of scope:** `Roadmap_ptree.md` and `roadmap-Modern-Python-Language-Features.md`  
**Repository policy:** Write new code for Python 3.12+. This question bank also tests the ability to reason about older and newer runtimes when supporting a declared compatibility range.

## How to use this question bank

- Attempt the questions before reading the answer key.
- Questions are grouped in the roadmap's four phases and progress from foundational semantics to production decisions.
- Each question identifies its lesson reference, difficulty, question type, context, and assessed skill.
- There are **36 core questions**, including **exactly six** items labelled **Predict the Output**. Those six are Q-A01, Q-A04, Q-B10, Q-B13, Q-C20, and Q-D31.
- Version-sensitive questions label the relevant Python versions. Unless stated otherwise, code is intended for Python 3.12+.
- Type-checker diagnostics are static-analysis outcomes, not Python runtime errors. Where a result depends on a particular checker or configuration, that dependency is stated.

---

# Questions

## Phase A — Control Flow and Signatures

### Q-A01 — Predict the Output: capture versus constant pattern
- **Topic / roadmap reference:** Lesson 01 — structural pattern matching; capture and value patterns.
- **Difficulty:** Beginner
- **Question type:** Predict the Output
- **Question:** What does this program print? Explain why the first case matches.
- **Code (Python 3.10+):**

```python
RED = "red"
value = "blue"

match value:
    case RED:
        print("matched", RED)
```

- **Skill assessed:** Distinguish a capture pattern from a constant value pattern and identify a common correctness bug.

### Q-A02 — Choose and refactor a pattern-matching design
- **Topic / roadmap reference:** Lesson 01 — literal, sequence, mapping, class, OR, AS, guard patterns; conversion from `if/elif`; exhaustiveness.
- **Difficulty:** Intermediate
- **Question type:** Implementation / refactoring
- **Question:** Implement `describe(event)` for these inputs: `{"type": "click", "pos": (x, y)}`, `{"type": "key", "key": "q"}`, and `("run", command, *args)`. Return useful descriptions, reject unknown shapes with `ValueError`, and avoid treating strings as sequences. Explain when a dispatch table or ordinary `if` would be clearer than `match`. For a closed union of event dataclasses, explain how `assert_never` can help a type checker detect a missing case.
- **Constraints:** Use Python 3.10+ syntax. Mapping patterns may accept extra keys unless you explicitly capture and validate them.
- **Skill assessed:** Compose patterns correctly and make a reasoned control-flow design choice.

### Q-A03 — Audit a walrus refactor
- **Topic / roadmap reference:** Lesson 02 — assignment expressions, comprehension scope, loop refactoring, readability trade-offs.
- **Difficulty:** Intermediate
- **Question type:** Code review / refactoring
- **Question:** Review this code:

```python
accepted = [score for row in rows if (score := parse_score(row)) >= 0]
```

State the scope of `score`, identify a case where the expression improves the code, and identify a case where a separate assignment would be clearer. Explain why rebinding the comprehension iteration variable with `:=` is prohibited. Then show how you would use `while (chunk := stream.read(8192))` to process a stream until EOF, and briefly compare it with `iter(read_chunk, b"")` for a binary stream.
- **Constraints:** Assume `parse_score` returns an integer and `rows` is iterable. The stream example is Python 3.8+ and `read_chunk()` returns `bytes`.
- **Skill assessed:** Reason about PEP 572 binding rules, loop termination, and readability rather than treating shorter code as automatically better.

### Q-A04 — Predict the Output: comprehension binding
- **Topic / roadmap reference:** Lesson 02 — assignment-expression target scope in comprehensions.
- **Difficulty:** Beginner
- **Question type:** Predict the Output
- **Question:** What is printed, and why does `last` remain available after the comprehension?
- **Code (Python 3.8+):**

```python
values = [1, 2, 3, 4]
squares = [last for item in values if (last := item * item) > 4]
print(squares, last)
```

- **Skill assessed:** Trace a comprehension and distinguish the comprehension's iteration variable from a walrus target bound in the enclosing scope.

### Q-A05 — Design a stable function signature
- **Topic / roadmap reference:** Lesson 03 — positional-only, keyword-only, `*args`, `**kwargs`, defaults, signature evolution.
- **Difficulty:** Intermediate
- **Question type:** Implementation
- **Question:** Design `connect(host, port, /, *, timeout=5.0, retries=3, **options)` and demonstrate one valid call and two invalid calls. Explain which parameters are positional-only, which are keyword-only, and what `**options` should and should not be used for. Then explain how this signature protects the names `host` and `port` from becoming permanent keyword API commitments. Finally, sketch how `ParamSpec` types a forwarding decorator without erasing the wrapped callable's static signature, and how `TypedDict` plus `Unpack` can constrain accepted `**kwargs` on Python 3.11+.
- **Constraints:** Use Python 3.8+ for the `connect` signature; `ParamSpec` is available in `typing` from Python 3.10, and `Unpack`/PEP 692 support from Python 3.11. Do not rely on an undocumented `**options` catch-all to silently accept misspelled configuration keys.
- **Skill assessed:** Build and explain a deliberate public API contract.

### Q-A06 — Sentinel versus `None`
- **Topic / roadmap reference:** Lesson 03 — defaults, sentinels, API evolution.
- **Difficulty:** Intermediate
- **Question type:** Debugging / API design
- **Question:** A function `def find_user(user_id, default=None): ...` uses `None` to mean “no default supplied,” but callers must also be able to explicitly request `None` as the fallback. Repair the API with a private sentinel, show the key branch, and explain why `default=[]` is not a safe alternative.
- **Skill assessed:** Distinguish omission from an explicitly supplied value and avoid mutable-default bugs.

### Q-A07 — Convert an `if/elif` ladder safely
- **Topic / roadmap reference:** Lesson 01 — matching structured data; guards, OR patterns, mapping and sequence patterns.
- **Difficulty:** Intermediate
- **Question type:** Refactoring
- **Question:** Refactor a command parser with branches for `"start"`, `"stop"`, and `"status"` into `match` cases that validate argument shape. Include a guard for a positive integer retry count. Explain why `case command:` is not a test that `command` equals a previously defined constant, and why `case [verb, *args]` will not match a `str`.
- **Constraints:** Python 3.10+; invalid commands and malformed arguments must fail explicitly.
- **Skill assessed:** Translate branching logic without changing validation semantics.

### Q-A08 — Make a match exhaustive
- **Topic / roadmap reference:** Lesson 01 — enums, union models, `typing.assert_never`, exhaustive handling.
- **Difficulty:** Advanced
- **Question type:** Implementation / static-analysis reasoning
- **Question:** Given `Shape = Circle | Rectangle`, where each is a dataclass, write `area(shape)` with structural matching and an explicit unreachable fallback using `assert_never`. Explain what a static type checker can detect when a new variant is added and why the fallback alone does not make runtime matching magically exhaustive.
- **Constraints:** `assert_never` is available in `typing` on Python 3.11+; for older versions, use a compatible typing backport or a version-appropriate alternative.
- **Skill assessed:** Combine algebraic data modelling, runtime behavior, and static exhaustiveness checking.

### Q-A09 — Review a public API change
- **Topic / roadmap reference:** Lesson 03 — positional-only and keyword-only design; safe function-API evolution.
- **Difficulty:** Advanced
- **Question type:** System-design judgment
- **Question:** A library wants to add `timeout` to `fetch(url, headers=None)` while preserving callers that pass `headers` positionally and preventing future internal parameter names from becoming public keyword names. Propose a signature and a migration plan. Discuss whether adding a keyword-only parameter is normally safer than inserting a new positional parameter, and how you would test compatibility.
- **Skill assessed:** Evaluate compatibility risk and plan an additive API change.

---

## Phase B — Errors and Types

### Q-B10 — Predict the Output: implicit exception chaining
- **Topic / roadmap reference:** Lesson 04 — `__cause__`, `__context__`, traceback interpretation.
- **Difficulty:** Beginner
- **Question type:** Predict the Output
- **Question:** What does the program print? Explain the difference between `__context__` and `__cause__` here.
- **Code (Python 3.0+):**

```python
try:
    try:
        int("not-an-int")
    except ValueError:
        raise RuntimeError("could not parse identifier")
except RuntimeError as error:
    print(type(error.__context__).__name__)
    print(error.__cause__)
```

- **Skill assessed:** Trace implicit exception chaining without confusing it with explicit `raise ... from ...`.

### Q-B11 — Preserve context while raising a domain exception
- **Topic / roadmap reference:** Lesson 04 — exception chaining, custom hierarchies, `add_note`.
- **Difficulty:** Intermediate
- **Question type:** Implementation
- **Question:** Implement `load_record(path)` so that a low-level `OSError` becomes a `RecordLoadError` with the original exception preserved as its explicit cause. Add a note that identifies the record ID when available. Explain when `raise RecordLoadError(...) from exc` is better than suppressing the cause with `from None`.
- **Constraints:** `BaseException.add_note` is available in Python 3.11+. If supporting 3.10, explain a compatibility alternative rather than calling it unconditionally.
- **Skill assessed:** Design actionable domain errors without losing diagnostic context.

### Q-B12 — Choose an exception hierarchy
- **Topic / roadmap reference:** Lesson 04 — custom exception hierarchies and useful error messages.
- **Difficulty:** Intermediate
- **Question type:** Code review
- **Question:** A data-import library raises `ValueError` for malformed CSV, missing required columns, permission failures, and a remote-service timeout. Propose a small exception hierarchy and state which underlying exceptions should usually remain chained. Explain why catching `Exception` at every layer and re-raising `RuntimeError("failed")` damages diagnosis. If a custom exception must cross a multiprocessing boundary, explain what its constructor and `args` need to preserve for pickling.
- **Skill assessed:** Separate failure domains and preserve useful error messages.

### Q-B13 — Predict the Output: exception-group splitting
- **Topic / roadmap reference:** Lesson 05 — `ExceptionGroup`, splitting, selective handling with `except*`.
- **Difficulty:** Intermediate
- **Question type:** Predict the Output
- **Question:** What does the program print? State how many failures are in each resulting subgroup.
- **Code (Python 3.11+):**

```python
errors = ExceptionGroup(
    "batch failed",
    [ValueError("bad row 1"), TypeError("wrong type"), ValueError("bad row 2")],
)
value_errors, remainder = errors.split(ValueError)
print(len(value_errors.exceptions))
print(len(remainder.exceptions))
print(type(remainder.exceptions[0]).__name__)
```

- **Skill assessed:** Understand exception-group splitting and the fact that unmatched exceptions remain in the remainder.

### Q-B14 — Handle independent concurrent failures
- **Topic / roadmap reference:** Lesson 05 — `except*`, group splitting, concurrent validation.
- **Difficulty:** Advanced
- **Question type:** Implementation / debugging
- **Question:** Write a handler for an `ExceptionGroup` raised by batch validation that handles all `ValueError` instances as input failures and all `TimeoutError` instances as retryable failures, while allowing unexpected exception types to propagate. Explain why `except*` clauses are not ordinary sequential `except` clauses, why a subgroup can contain nested groups, why plain `except` and `except*` cannot be mixed in one `try`, and how `asyncio.TaskGroup` failure propagation differs from `asyncio.gather(..., return_exceptions=True)`.
- **Constraints:** Python 3.11+. Do not flatten away information that callers need for diagnosis.
- **Skill assessed:** Selectively handle grouped failures without swallowing unrelated errors.

### Q-B15 — Modern generic function and class
- **Topic / roadmap reference:** Lesson 06 — PEP 695 generic syntax, generic classes, type aliases.
- **Difficulty:** Intermediate
- **Question type:** Implementation
- **Question:** Using Python 3.12+ syntax, implement `first[T](items: Sequence[T]) -> T` and a `Box[T]` class with a `value` attribute. Add a `type` alias for a mapping from strings to lists of `T`. Explain why this syntax is not parseable by Python 3.11 and how the traditional `TypeVar` spelling differs.
- **Skill assessed:** Write modern generic declarations and connect syntax to minimum-version policy.

### Q-B16 — Model a partially optional payload
- **Topic / roadmap reference:** Lesson 06 — `TypedDict`, `Required`, `NotRequired`, `ReadOnly`, narrowing.
- **Difficulty:** Advanced
- **Question type:** Type-contract design
- **Question:** Define a `TypedDict` for an ingestion event with required `event_id`, optional `source`, and a required, read-only `created_at` key. Explain the difference between a key being non-required and a value being nullable. Explain why `TypedDict` does not validate untrusted JSON at runtime and name an appropriate runtime validation strategy.
- **Constraints:** `ReadOnly` is available in `typing` on Python 3.13+; `NotRequired` is in `typing` from Python 3.11. Show a compatibility import strategy using `typing_extensions` when supporting Python 3.10–3.12.
- **Skill assessed:** Specify structural data contracts while separating static typing from runtime validation.

### Q-B17 — Choose among `Self`, `@override`, and `TypeIs`
- **Topic / roadmap reference:** Lesson 06 — modern type narrowing, `Self`, `override`, `TypeIs`, runtime-versus-static typing.
- **Difficulty:** Advanced
- **Question type:** Code review
- **Question:** For a fluent builder subclass, explain why a method returning `Self` can preserve the concrete subclass type. Show where `@override` belongs and what it communicates to a type checker. Then distinguish `TypeIs[T]` from `TypeGuard[T]` at a high level and explain why these annotations do not automatically enforce runtime correctness.
- **Constraints:** `Self` is in `typing` from Python 3.11; `override` from Python 3.12; `TypeIs` from Python 3.13. Mention backports where relevant.
- **Skill assessed:** Choose type-system features based on the contract and the supported interpreter range.

### Q-B18 — Design a static/runtime type boundary
- **Topic / roadmap reference:** Lesson 06 — `TypedDict`, generic APIs, narrowing, runtime-versus-static typing.
- **Difficulty:** Advanced
- **Question type:** System-design judgment
- **Question:** A public API accepts dictionaries decoded from untrusted JSON and returns typed domain objects. Propose where static annotations, runtime validation, and domain exceptions belong. Explain why a type checker accepting a `TypedDict` does not prove that a production JSON payload conforms to it, and how you would test malformed, missing, and extra fields.
- **Skill assessed:** Design a robust boundary between external data and typed internal code.

---

## Phase C — Data and Text

### Q-C19 — Configure a dataclass for safe construction
- **Topic / roadmap reference:** Lesson 07 — `field`, `default_factory`, `InitVar`, `__post_init__`, `slots`, inheritance.
- **Difficulty:** Intermediate
- **Question type:** Implementation
- **Question:** Implement a dataclass `Job` with a required `name`, an independent mutable `tags` list per instance, a keyword-only `priority` defaulting to 0, and an `InitVar` containing a raw secret. In `__post_init__`, derive and store only a non-secret fingerprint; do not store the raw secret as a field. Explain the purpose of `default_factory`, `InitVar`, and `kw_only`.
- **Constraints:** `kw_only` is available from Python 3.10. The supplied `fingerprint()` helper returns a safe, non-reversible identifier and is provided by the application.
- **Skill assessed:** Use dataclass field configuration to control initialization and state while minimizing secret retention.

### Q-C20 — Predict the Output: dataclass mutability
- **Topic / roadmap reference:** Lesson 07 — `default_factory`, frozen versus deeply immutable values.
- **Difficulty:** Beginner
- **Question type:** Predict the Output
- **Question:** What is printed? Explain why changing one instance does not affect the other.
- **Code (Python 3.7+):**

```python
from dataclasses import dataclass, field

@dataclass
class Batch:
    items: list[int] = field(default_factory=list)

a = Batch()
b = Batch()
a.items.append(7)
print(a.items)
print(b.items)
```

- **Skill assessed:** Distinguish per-instance mutable defaults from shared mutable state.

### Q-C21 — Frozen is not deeply immutable
- **Topic / roadmap reference:** Lesson 07 — frozen dataclasses, nested mutability, `__post_init__`.
- **Difficulty:** Intermediate
- **Question type:** Debugging / explanation
- **Question:** A developer marks `@dataclass(frozen=True)` on a class containing `items: list[str]` and claims that instances are deeply immutable and safe as hash keys. Explain what is actually prevented, demonstrate the nested-mutation problem, and propose two designs depending on whether the data must be hashable.
- **Skill assessed:** Understand shallow freezing, mutation, and hashability contracts.

### Q-C22 — Select the right data-model tool
- **Topic / roadmap reference:** Lesson 07 — dataclasses versus `attrs`, `TypedDict`, `NamedTuple`, Pydantic.
- **Difficulty:** Advanced
- **Question type:** Architecture decision
- **Question:** Choose a representation for each case and justify the trade-offs: (a) internal mutable domain entity, (b) JSON-like static shape used only by type checking, (c) compact immutable tuple-like record, (d) untrusted API payload requiring runtime validation/coercion, and (e) a domain model needing richer validators and conversion hooks. Consider dataclasses, `attrs`, `TypedDict`, `NamedTuple`, and Pydantic.
- **Skill assessed:** Match a modelling tool to runtime guarantees, ergonomics, and validation requirements.

### Q-C23 — F-string formatting and evaluation
- **Topic / roadmap reference:** Lesson 08 — format specs, `!r`, debug `=`, evaluation and formatting pitfalls.
- **Difficulty:** Beginner
- **Question type:** Code reading
- **Question:** Explain the difference between `f"{value}"`, `f"{value!r}"`, `f"{value=}"`, and `f"{ratio:.2%}"`. State when formatting may invoke user-defined code and why an f-string used as a logging argument is usually eager.
- **Skill assessed:** Read format conversions/specifications and identify evaluation costs.

### Q-C24 — Explain PEP 701 compatibility
- **Topic / roadmap reference:** Lesson 08 — f-string grammar and PEP 701.
- **Difficulty:** Intermediate
- **Question type:** Debugging / version compatibility
- **Question:** Explain the version difference for this snippet:

```python
parts = ["alpha", "beta"]
joined = f"{'\n'.join(parts)}"
record = {"id": 7}
label = f"{record["id"]}"
```

The snippet is intended for Python 3.12+. Explain why Python 3.11 rejects the source during parsing, and rewrite it so the package still parses on Python 3.11. Distinguish a parser `SyntaxError` from a runtime exception.
- **Skill assessed:** Identify grammar-version boundaries and preserve compatibility without obscuring intent.

### Q-C25 — SQL, logging, and interpolation safety
- **Topic / roadmap reference:** Lesson 08 — SQL injection, logging, format-string risks, template design.
- **Difficulty:** Advanced
- **Question type:** Security code review
- **Question:** Review these patterns and correct them: (1) `query = f"SELECT * FROM users WHERE name = '{name}'"`; (2) `logger.debug(f"loaded {record_id}")`; (3) rendering an untrusted template with `user_template.format(value)`. Explain parameterized SQL, lazy logging arguments, and why Python 3.14 template strings are not automatically safe unless a consumer handles interpolation values correctly.
- **Constraints:** Label `t"..."` template strings as Python 3.14+ and distinguish their `Template` object from a normal `str`.
- **Skill assessed:** Prevent injection and avoid misleading assumptions about interpolation safety.

### Q-C26 — Design a template-string consumer
- **Topic / roadmap reference:** Lesson 08 — Python 3.14 template strings, structured interpolation, secure consumers.
- **Difficulty:** Advanced
- **Question type:** System-design judgment / implementation sketch
- **Question:** Sketch the contract of a Python 3.14+ `sql()` consumer that accepts a `string.templatelib.Template` and returns `(query, parameters)`. Use SQLite-style `?` placeholders for the example. Explain why the consumer must preserve literal segments and bind interpolation values rather than concatenate `str(value)` into SQL. State what must be tested for quoting, parameter order, and malicious input.
- **Constraints:** Python 3.14+ only; a t-string is a `Template`, not a `str`. The consumer may reject conversion flags or format specifications it does not explicitly support.
- **Skill assessed:** Design a safe interpolation boundary and avoid claiming the language feature itself sanitizes values.

### Q-C27 — Make data models predictable
- **Topic / roadmap reference:** Lesson 07 — dataclass inheritance, `slots`, `__post_init__`, `attrs` trade-offs.
- **Difficulty:** Advanced
- **Question type:** Debugging / code review
- **Question:** Diagnose both defects in this Python 3.12+ example:

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Base:
    name: str
    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name is required")

@dataclass(slots=True)
class Child(Base):
    enabled: bool = True
    def __post_init__(self) -> None:
        self.cache = {}  # no declared slot
```

Explain why assigning `cache` fails and why the base validation is skipped. Show a corrected design, discuss safe `super()` use with `slots=True`, and explain constructor field ordering when inherited defaults are involved. State when `attrs` or an explicit initializer may be more suitable.
- **Skill assessed:** Diagnose dataclass inheritance and initialization interactions rather than assuming decorators remove all object-model constraints.

---

## Phase D — Evolution and Compatibility

### Q-D28 — Write a correct deprecation warning
- **Topic / roadmap reference:** Lesson 09 — warning categories, filters, `stacklevel`, `FutureWarning`.
- **Difficulty:** Intermediate
- **Question type:** Implementation
- **Question:** Implement a deprecated library function `old_lookup()` that forwards to `lookup()`, emitting `DeprecationWarning` at the caller's source line. Explain why `stacklevel=2` is appropriate for a simple wrapper, when a larger wrapper stack may require a different level, and when an end-user-facing behavioral change might warrant `FutureWarning` instead. Also explain what Python 3.13+'s `warnings.deprecated` decorator adds beyond a hand-written runtime warning, and name a compatibility approach for older versions.
- **Skill assessed:** Emit actionable warnings with an appropriate category and location.

### Q-D29 — Test warnings without masking regressions
- **Topic / roadmap reference:** Lesson 09 — `pytest.warns`, matching category/message, `-W error`, filters, registries, concurrency.
- **Difficulty:** Intermediate
- **Question type:** Test design / debugging
- **Question:** Write a pytest test that asserts the category, message, and caller location for `old_lookup()`. Propose a CI policy that treats warnings from your own package as errors without blanket-suppressing third-party warnings. Explain how filter ordering and `stacklevel` affect a module-qualified filter, what `default`, `always`, `once`, and `module` actions mean at a high level, and why changing global filters or using `catch_warnings()` around concurrent work requires care. Include how `ResourceWarning`, `-X dev`, and `logging.captureWarnings(True)` fit into diagnosis.
- **Skill assessed:** Verify warning contracts and reason about warning-filter state rather than treating warnings as globally reliable alerts.

### Q-D30 — Deprecate a module attribute safely
- **Topic / roadmap reference:** Lesson 09 — module-level `__getattr__`, attributes, limitations and removal timelines.
- **Difficulty:** Advanced
- **Question type:** Implementation / API lifecycle
- **Question:** A module renamed `OldClient` to `Client`. Implement module-level `__getattr__` that returns the new class for `OldClient`, emits a warning, and raises `AttributeError` for unknown names. Explain limitations for `from module import OldClient`, repeated attribute access, introspection, and static type checkers. Propose a grace period and removal criteria.
- **Skill assessed:** Deprecate a module export while accounting for runtime and tooling behavior.

### Q-D31 — Predict the Output: version-gated standard-library API
- **Topic / roadmap reference:** Lesson 10 — feature availability, minimum Python versions, compatibility shims.
- **Difficulty:** Beginner
- **Question type:** Predict the Output
- **Question:** Assuming Python 3.13, what is printed? What changes on Python 3.10? Explain why the version branch is needed even though both branches expose the same local name.
- **Constraints:** Assume the `tomli` dependency is installed on Python 3.10; otherwise the older-version import fails before any output.
- **Code (Python 3.10–3.13):**

```python
import sys

if sys.version_info >= (3, 11):
    import tomllib as toml_reader
    source = "stdlib"
else:
    import tomli as toml_reader
    source = "backport"

print(source)
print(hasattr(toml_reader, "loads"))
```

- **Skill assessed:** Trace a compatibility shim and reason about standard-library introduction versions. On Python 3.10, assume the `tomli` dependency is installed.

### Q-D32 — Match features to minimum versions
- **Topic / roadmap reference:** Lesson 10 — Python 3.10–3.14 feature timeline; syntax versus runtime API availability.
- **Difficulty:** Intermediate
- **Question type:** Version compatibility
- **Question:** Give the minimum CPython version for each feature and one compatibility strategy where older versions matter: (a) `match/case` and `zip(strict=True)`, (b) `ExceptionGroup`/`except*`, `tomllib`, and `asyncio.TaskGroup`, (c) PEP 695 `class Box[T]`, `type Alias = ...`, and PEP 701 f-string syntax, (d) `itertools.batched` and `@override`, (e) `copy.replace`, `warnings.deprecated`, `TypeIs`, and `ReadOnly`, (f) PEP 649/749 deferred annotation evaluation, and (g) template strings, `compression.zstd`, `uuid.uuid7`, and `concurrent.interpreters`. Also identify when `distutils` was removed and when `datetime.utcnow()` was deprecated. Explain why `from __future__ import annotations` cannot make later syntax parse on an older interpreter.
- **Skill assessed:** Map language syntax and APIs to runtime requirements accurately.

### Q-D33 — Build a multi-version test strategy
- **Topic / roadmap reference:** Lesson 10 — `uv`, tox/nox, CI matrix, Ruff `UP`, warning collection.
- **Difficulty:** Advanced
- **Question type:** Test strategy / implementation
- **Question:** A library declares `requires-python = ">=3.12"` but a contributor wants to test 3.11 as well. Design a coherent policy and CI matrix. Include environment installation with `uv`, test execution, a static lint/modernization step using Ruff `UP` rules, and warning-as-error coverage. Explain why testing 3.11 cannot compensate for shipping 3.12-only syntax under a `>=3.11` declaration.
- **Skill assessed:** Align package metadata, parser requirements, dependencies, and CI evidence.

### Q-D34 — Plan an interpreter upgrade with native extensions
- **Topic / roadmap reference:** Lesson 10 — production upgrade playbook, C extensions, wheels/ABI, canary and rollback.
- **Difficulty:** Advanced
- **Question type:** System-design judgment
- **Question:** A service moves from Python 3.10 to 3.13 and depends on three C-extension packages. Propose an ordered upgrade plan covering dependency and wheel inventory, CI expansion, warning cleanup, dependency upgrades, full tests, staging, canary rollout, observability, rollback, and the final `requires-python` change. Explain the risks of changing interpreter and all dependencies at once.
- **Skill assessed:** Plan a reversible production migration and identify native-extension compatibility risks.

### Q-D35 — Evaluate performance and experimental runtimes
- **Topic / roadmap reference:** Lesson 10 — performance evaluation, JIT/free-threaded builds, ecosystem readiness.
- **Difficulty:** Advanced
- **Question type:** Experiment design
- **Question:** Design a reproducible benchmark comparing one representative workload on Python 3.10, 3.12, and 3.14. Specify inputs, warm-up, repeated runs, environment controls, metrics, correctness checks, and how results should be reported. Separately explain why a free-threaded or JIT-enabled build must be evaluated as a distinct runtime configuration and why no speed-up number should be inferred from release notes alone.
- **Skill assessed:** Measure real workload behavior and separate stable interpreter releases from optional runtime configurations.

### Q-D36 — Draft a support-policy and upgrade RFC
- **Topic / roadmap reference:** Lesson 10 — lifecycle/security policy, Docker reproducibility, minimum versions, RFC, deprecation handling.
- **Difficulty:** Advanced
- **Question type:** System-design judgment / written proposal
- **Question:** Draft the outline of an internal RFC for raising a service's minimum Python version. Include current and target support windows, security and CVE implications, dependency supply-chain review, Docker image/tag or digest strategy, acceptance criteria, deployment stages, rollback triggers, and the date/criteria for raising package metadata. Explain how you would justify a “last N versions” policy versus a fixed minimum-version policy and how you would treat EOL interpreters.
- **Skill assessed:** Turn technical compatibility facts into a maintainable support and governance policy.

---

# Answer Key and Explanations

## Phase A — Control Flow and Signatures

### A-A01 — Q-A01

**Exact output:**

```text
matched blue
```

`case RED` is a **capture pattern**, not a comparison against the existing module-level name `RED`. It binds the subject (`"blue"`) to the name `RED`, so the case matches and the program prints `matched blue`. A subsequent `case _` would make the code fail to compile because the capture case is irrefutable and makes later cases unreachable. To compare with a constant, use a dotted value pattern such as `case Colors.RED:` or `case config.RED:`. For a string constant, a literal pattern such as `case "red":` is also unambiguous.

### A-A02 — Q-A02

One valid implementation:

```python
def describe(event: object) -> str:
    match event:
        case {"type": "click", "pos": (x, y)}:
            return f"click at ({x}, {y})"
        case {"type": "key", "key": "q"}:
            return "quit key"
        case ("run", command, *args):
            return f"run {command!r} with {len(args)} argument(s)"
        case _:
            raise ValueError(f"unsupported event: {event!r}")
```

Mapping patterns intentionally allow extra keys by default; add `**rest` and validate it if the contract requires exact keys. A sequence pattern does not match `str` or `bytes`, so the tuple command branch does not accidentally parse a string character by character. Use a dispatch table when the operation is a flat mapping from stable keys to callables; use ordinary `if` for simple boolean decisions. For a closed union, put `assert_never(value)` in the fallback after all known variants. A type checker can flag that fallback as reachable if a new union member is added; runtime code still raises if an unexpected value arrives.

### A-A03 — Q-A03

The walrus target `score` is bound in the **enclosing scope**, not isolated inside the comprehension. It receives the result for each row on which `parse_score(row)` is evaluated; after completion, it contains the last computed score (or remains unbound if the expression was never evaluated). The refactor avoids calling `parse_score(row)` twice, which is useful when it is expensive or stateful. A separate assignment is clearer if the expression grows, multiple computed values are needed, or readers must reason about several side effects. The comprehension's iteration variable `row` must not be rebound by an assignment expression in the same comprehension; this is prohibited by the language to avoid confusing iteration semantics.

For a binary stream, a walrus loop is:

```python
while (chunk := stream.read(8192)):
    process(chunk)
```

It stops when `read()` returns `b""`. An equivalent sentinel form is `for chunk in iter(read_chunk, b""):` when `read_chunk()` performs one read per call. Choose the form that best communicates the I/O contract; neither should hide error handling or cleanup.

### A-A04 — Q-A04

**Exact output:**

```text
[9, 16] 16
```

The iteration variable `item` takes 1, 2, 3, and 4. The walrus expression assigns `item * item` to `last` in the surrounding scope, and the filter retains only values greater than 4. Thus the list contains 9 and 16. On the final iteration `last` becomes 16, and the target remains available after the comprehension. If `values` were empty, `last` would never be assigned and reading it afterward would raise `NameError`.

### A-A05 — Q-A05

```python
def connect(host, port, /, *, timeout=5.0, retries=3, **options):
    allowed = {"tls", "source_address"}
    unknown = options.keys() - allowed
    if unknown:
        raise TypeError(f"unexpected option(s): {', '.join(sorted(unknown))}")
    return {"host": host, "port": port, "timeout": timeout,
            "retries": retries, **options}  # placeholder for connection setup
```

Valid call: `connect("db.example", 5432, timeout=2.0, tls=True)`. Invalid calls include `connect(host="db.example", port=5432)` because `host` and `port` are positional-only, and `connect("db.example", 5432, timout=2)` because `timout` is an unknown option and should not silently pass. `/` prevents parameter names from becoming keyword API commitments; `*` makes later configuration options keyword-only. `**options` should be an intentionally validated extension point, not a way to hide misspellings. In production, the function would continue after validation and actually establish the connection. For a forwarding decorator, use `ParamSpec` so the checker preserves the wrapped callable's parameter types:

```python
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def traced(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)
    return wrapper
```

For an intentionally limited keyword extension point, a `TypedDict` plus `Unpack` describes accepted keyword names to type checkers (Python 3.11+ typing support):

```python
from typing import NotRequired, TypedDict, Unpack

class ExportOptions(TypedDict):
    include_header: NotRequired[bool]

def export_data(data: list[str], /, **options: Unpack[ExportOptions]) -> None:
    ...
```

A type checker can flag unsupported option names; runtime validation is still needed if callers can supply untrusted mappings.

### A-A06 — Q-A06

```python
_MISSING = object()

def find_user(user_id, default=_MISSING):
    user = lookup_user(user_id)
    if user is not None:
        return user
    if default is _MISSING:
        raise LookupError(f"no user found for {user_id!r}")
    return default
```

The unique sentinel distinguishes “argument omitted” from “caller explicitly passed `None`.” A mutable default such as `[]` is created once when the function is defined and can leak mutations between calls. The example assumes `lookup_user` returns a user or `None`; adapt the sentinel contract if `None` is itself a valid stored result.

### A-A07 — Q-A07

Example parser:

```python
def parse_command(value: object) -> tuple[str, list[object]]:
    match value:
        case [("start" | "stop" | "status") as verb, *args]:
            if args:
                raise ValueError("this command takes no arguments")
            return verb, []
        case ["retry", count] if type(count) is int and count > 0:
            return "retry", [count]
        case ["retry", _]:
            raise ValueError("retry count must be a positive integer")
        case _:
            raise ValueError(f"invalid command: {value!r}")
```

The guard uses `type(count) is int`, not only `isinstance(count, int)`, because `bool` is a subclass of `int` and `True` should not silently count as a retry count of 1. A production signature may use a more precise alias or explicit validation for string tokens; this example intentionally accepts a sequence-like command shape. `case command:` captures any subject; compare constants using a literal or dotted value pattern. Sequence patterns do not match `str` or `bytes`. Validate argument counts rather than assuming the pattern establishes all semantic constraints. A flat dispatch table may be easier to maintain if each command maps directly to a handler and has no structural payload.

### A-A08 — Q-A08

```python
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class Circle:
    radius: float

@dataclass(frozen=True)
class Rectangle:
    width: float
    height: float

Shape = Circle | Rectangle

def area(shape: Shape) -> float:
    match shape:
        case Circle(radius=r):
            return 3.141592653589793 * r * r
        case Rectangle(width=w, height=h):
            return w * h
        case _:
            assert_never(shape)
```

A checker that understands the union can verify that every variant is handled and report the fallback if a newly added variant makes `shape` no longer `Never`. `assert_never` also raises if reached at runtime. It does not change Python's runtime matching rules or prove external data is a valid `Shape`. `typing.assert_never` is available in Python 3.11+; use a suitable backport for older supported versions.

### A-A09 — Q-A09

A safe additive signature is `def fetch(url, headers=None, *, timeout=10.0): ...`. Existing calls `fetch(url)` and `fetch(url, headers)` retain their meaning, while the new timeout must be explicit by keyword. If the goal is also to prevent `url` and `headers` names becoming keyword commitments, a new major API could instead be `def fetch(url, headers=None, /, *, timeout=10.0)`—but changing existing parameters to positional-only would break callers already using `fetch(url=...)` or `fetch(headers=...)`, so it requires a compatibility review and likely a deprecation period. Test old positional and keyword call forms, new timeout use, invalid values, and deprecation warnings. Never insert a new positional parameter before existing positional parameters because that can silently reinterpret calls.

---

## Phase B — Errors and Types

### A-B10 — Q-B10

**Exact output:**

```text
ValueError
None
```

`int("not-an-int")` raises `ValueError`. While handling it, the code raises `RuntimeError` without `from`, so Python records the handled `ValueError` as the new exception's implicit `__context__`. The explicit `__cause__` remains `None` because no `raise ... from ...` was used. The traceback normally displays “During handling of the above exception…” for this implicit chain.

### A-B11 — Q-B11

```python
class RecordLoadError(Exception):
    """A record could not be loaded."""

def load_record(path, record_id=None):
    try:
        return read_record_file(path)  # application-specific function
    except OSError as exc:
        error = RecordLoadError(f"could not load record from {path!s}")
        if record_id is not None:
            if hasattr(error, "add_note"):  # Python 3.11+
                error.add_note(f"record_id={record_id!r}")
        raise error from exc
```

`raise error from exc` preserves the low-level failure as `__cause__`, giving callers a stable domain exception while retaining diagnostic details. `from None` intentionally suppresses display of the implicit context and should be used only when that context is misleading or sensitive, not merely to make tracebacks shorter. For Python 3.10, `add_note` does not exist; log or include safe context in the exception message, or provide a compatibility helper. `read_record_file` is deliberately an application-specific dependency and must be implemented by the consuming project.

### A-B12 — Q-B12

A useful hierarchy might be:

```python
class ImportErrorBase(Exception):
    """Base class for expected import failures."""

class MalformedInputError(ImportErrorBase):
    pass

class SchemaError(ImportErrorBase):
    pass

class RemoteServiceError(ImportErrorBase):
    pass
```

Malformed CSV can be wrapped as `MalformedInputError`; absent required columns as `SchemaError`; a remote timeout can be wrapped as `RemoteServiceError` while chaining the original timeout. A local permission failure may be allowed to remain an `OSError` if callers can handle that standard category usefully, or wrapped with `raise ... from exc` if the public contract promises a domain hierarchy. Catch only errors that can be meaningfully translated or recovered from. Catching `Exception` everywhere and replacing it with `RuntimeError("failed")` erases the failure category, original message, and actionable context, unless the cause is carefully chained. For exceptions sent through multiprocessing, keep the constructor arguments pickle-compatible and ensure `exc.args` can reconstruct the exception; avoid non-picklable state or custom reconstruction that loses the original fields. Test an actual pickle round trip if this is part of the public contract.

### A-B13 — Q-B13

**Exact output:**

```text
2
1
TypeError
```

`ExceptionGroup.split(ValueError)` recursively separates matching leaves from the rest while preserving group structure where needed. `value_errors` contains the two `ValueError` instances. `remainder` contains the one unmatched `TypeError`; it is not silently discarded. On Python 3.10 the built-in `ExceptionGroup` API is unavailable; it was introduced in Python 3.11 (the `exceptiongroup` backport can support older runtimes when deliberately used).

### A-B14 — Q-B14

```python
try:
    raise ExceptionGroup(
        "validation batch",
        [ValueError("missing id"), TimeoutError("service timeout"), TypeError("bug")],
    )
except* ValueError as group:
    report_invalid_inputs(group.exceptions)
except* TimeoutError as group:
    schedule_retry(group.exceptions)
```

The `TypeError` subgroup is unmatched, so it propagates after the matching `except*` clauses have run. That is desirable for an unexpected bug. `except*` partitions a group by matching exception type and can run multiple matching handlers for one raised group. It is not equivalent to ordinary `except`, which handles a single matching exception flow. Nested exception groups can remain nested in subgroups to preserve the original failure structure. `asyncio.TaskGroup` cancels remaining sibling tasks when a child fails (subject to cancellation semantics) and raises grouped failures on exit; `gather(return_exceptions=True)` instead returns exception objects as result entries and does not provide the same structured-concurrency failure behavior. The functions `report_invalid_inputs` and `schedule_retry` represent application-specific reporting and retry logic.

### A-B15 — Q-B15

```python
from collections.abc import Sequence

def first[T](items: Sequence[T]) -> T:
    if not items:
        raise ValueError("items must not be empty")
    return items[0]

class Box[T]:
    def __init__(self, value: T) -> None:
        self.value = value

type StringLists[T] = dict[str, list[T]]
```

This uses PEP 695 type-parameter syntax and the `type` statement, introduced in Python 3.12. Python 3.11 cannot parse `def first[T]` or `class Box[T]`, even if the code path is never executed; this is a syntax/parser compatibility issue. Traditional syntax uses `T = TypeVar("T")`, then `def first(items: Sequence[T]) -> T` and `class Box(Generic[T])`. Type parameter scope and introspection details differ, but both express relationships between input and output types. The explicit empty-sequence check provides a runtime contract; static types alone do not guarantee a non-empty sequence.

### A-B16 — Q-B16

```python
from typing import TypedDict

try:  # Python 3.13+ provides both names in typing
    from typing import NotRequired, ReadOnly
except ImportError:  # Python 3.10–3.12
    from typing_extensions import NotRequired, ReadOnly

class IngestionEvent(TypedDict):
    event_id: str
    source: NotRequired[str]
    created_at: ReadOnly[str]
```

A non-required key may be absent; a nullable value is present but may contain `None` (for example, `source: str | None`). `ReadOnly` constrains mutation for static type checking; it does not freeze the underlying dictionary at runtime. `ReadOnly` is in `typing` starting with Python 3.13; `typing_extensions` can supply it on older supported interpreters. Decode external JSON, validate its shape and values at runtime (for example with Pydantic, a schema validator, or explicit checks), and only then treat it as an `IngestionEvent`. Static annotations are not runtime validation.

### A-B17 — Q-B17

`Self` expresses that a method returns the same concrete subtype as its receiver, which is useful for fluent builders. Example (Python 3.12+):

```python
from typing import Self, override

class Builder:
    def add_option(self, key: str, value: str) -> Self:
        return self

class SpecialBuilder(Builder):
    @override
    def add_option(self, key: str, value: str) -> Self:
        return self
```

`@override` belongs on the subclass method that intentionally replaces a base-class method; a supporting type checker can flag a misspelled or no-longer-overriding method. `Self` is in `typing` from Python 3.11, `override` from Python 3.12, and `TypeIs` from Python 3.13; `typing_extensions` supports older versions as appropriate. `TypeIs[T]` communicates a predicate that narrows a value to `T` in the true branch and excludes `T` in the false branch, subject to type-checker semantics; `TypeGuard[T]` primarily narrows the true branch and can express some cases `TypeIs` cannot, such as narrowing a mutable invariant container. Exact diagnostics depend on the checker and configuration. These constructs do not enforce runtime truthfulness: an incorrect predicate can still return a misleading boolean.

### A-B18 — Q-B18

Use runtime validation at the boundary: decode JSON to a generic object, validate required keys, value types, and policy constraints, then construct a domain object. Static annotations document and check the internal contract; they do not inspect external bytes at runtime. A Pydantic model or explicit validation function can reject missing required keys, invalid values, and forbidden extras. Decide explicitly whether extra fields are rejected, ignored, or retained; that is an API compatibility choice. Test valid payloads, missing `event_id`, wrong value types, `null` for non-nullable fields, unexpected keys, and boundary values. Convert validation failures into a stable domain error while preserving useful context.

---

## Phase C — Data and Text

### A-C19 — Q-C19

```python
from dataclasses import InitVar, dataclass, field

@dataclass(slots=True)
class Job:
    name: str
    raw_secret: InitVar[str]
    tags: list[str] = field(default_factory=list)
    priority: int = field(default=0, kw_only=True)
    secret_fingerprint: str = field(init=False)

    def __post_init__(self, raw_secret: str) -> None:
        self.secret_fingerprint = fingerprint(raw_secret)  # application-specific function
```

`default_factory=list` creates a fresh list for every instance. `InitVar` is accepted by the generated initializer and passed to `__post_init__`, but it is not stored as an ordinary dataclass field; the code stores only a derived fingerprint. `kw_only=True` makes `priority` a keyword-only constructor parameter. `slots=True` avoids a normal per-instance `__dict__` for declared fields, subject to inheritance details. The `fingerprint` function must be provided by the application and should not store or log the raw secret.

### A-C20 — Q-C20

**Exact output:**

```text
[7]
[]
```

`field(default_factory=list)` calls `list` separately for each `Batch` instance, so `a.items` and `b.items` refer to different lists. Appending to `a.items` does not change `b.items`. This is the correct pattern for mutable dataclass defaults. A shared list defined once and used as the default would create cross-instance state; modern dataclasses reject many unhashable defaults, but `default_factory` is still the explicit and maintainable solution.

### A-C21 — Q-C21

`frozen=True` prevents ordinary attribute rebinding such as `obj.items = []`, but it does not recursively freeze objects referenced by fields:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Snapshot:
    items: list[str]

snapshot = Snapshot(["first"])
snapshot.items.append("second")  # allowed: mutates the nested list
# snapshot.items = []              # raises FrozenInstanceError
```

Therefore the instance is not deeply immutable and is not automatically a safe hash key; dataclass hash generation depends on configuration and field properties, and hashing a mutable list fails. In a frozen dataclass's `__post_init__`, a derived field declared with `field(init=False)` can be initialized with `object.__setattr__(self, "field_name", value)`; ordinary assignment is blocked by the generated frozen behavior. If deep immutability/hashability is required, use immutable field types such as tuples and frozen nested values. If mutable collections are required, keep the object explicitly unhashable or define a carefully justified hash based only on stable identity fields. Do not imply that `frozen=True` recursively freezes nested objects.

### A-C22 — Q-C22

- **(a) Internal mutable domain entity:** a dataclass or `attrs` class; `attrs` is attractive for its validators, converters, and mature customization.
- **(b) JSON-like static shape:** `TypedDict`, because it describes dictionary keys to type checkers without creating a runtime model object.
- **(c) Compact immutable tuple-like record:** `NamedTuple`, when tuple behavior and positional indexing are part of the contract; a frozen dataclass is often clearer when named fields matter more than tuple compatibility.
- **(d) Untrusted API payload needing runtime validation/coercion:** Pydantic or an explicit validation layer; annotations alone are not enough.
- **(e) Rich validators/converters/hooks:** `attrs` or Pydantic depending on whether the main requirement is domain-object ergonomics or boundary parsing/validation.

There is no universal winner. Compare runtime validation, conversion, serialization, immutability, dependencies, performance, and public API stability. A `TypedDict` is not a runtime validator; a dataclass does not automatically coerce or validate values merely because fields are annotated.

### A-C23 — Q-C23

- `f"{value}"` formats the value using its normal format protocol.
- `f"{value!r}"` applies `repr(value)` before formatting, often useful for debugging.
- `f"{value=}"` is the debug form: it includes the expression text and its representation, such as `value='hello'` for a string.
- `f"{ratio:.2%}"` formats the numeric value as a percentage with two digits after the decimal point; for `ratio = 0.125`, the result is `12.50%`.
- A format such as `f"{amount:>{width},.2f}"` combines right alignment, a dynamic width, thousands grouping, and two fractional digits; `f"{dt:%Y-%m-%d}"` delegates date formatting to the object's format protocol.

Formatting may invoke `__format__`, `__str__`, or `__repr__` implementations, which can execute user-defined code or raise errors. `logger.debug(f"loaded {record_id}")` eagerly constructs the string even if debug logging is disabled. Prefer `logger.debug("loaded %s", record_id)` so the logging framework can defer formatting until it needs the message.

### A-C24 — Q-C24

PEP 701 formalized f-string parsing in Python 3.12, allowing constructs previously rejected by the older f-string parser, including same-quote reuse in nested expressions, comments and backslashes in expression portions where valid under the grammar. Python 3.12+ parses the question's snippet; Python 3.11 rejects it during parsing with `SyntaxError`, before any line runs. For code that must also parse on Python 3.11, move the backslash-containing expression out of the f-string and use distinct quote delimiters:

```python
joined = "\n".join(parts)
label = f"{record['id']}"
```

A parser `SyntaxError` differs from a runtime `ValueError` or other exception, which occurs only after successful parsing. `from __future__ import annotations` cannot backport new expression grammar.

### A-C25 — Q-C25

1. Use a database driver's parameter binding, for example:

   ```python
   cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
   ```

   Placeholder syntax is driver-specific (`?`, `%s`, or named placeholders); use the driver's documented parameter API. Do not interpolate untrusted values into SQL text.

2. Use lazy logging formatting:

   ```python
   logger.debug("loaded %s", record_id)
   ```

3. Do not execute an arbitrary untrusted format string with `user_template.format(value)`. It can access attributes/indexes and can expose data or trigger surprising behavior. Use a restricted template language and explicit allowed names if user-authored templates are a requirement.

Python 3.14 template strings (`t"..."`) produce a structured `Template` object containing literal segments and interpolation metadata, not a normal `str`. They do not sanitize by themselves. Safety depends on a consumer that correctly treats values as data—for SQL, bind parameters; for HTML, context-aware escaping; for shell commands, avoid string assembly and pass argument arrays to subprocess APIs.

### A-C26 — Q-C26

A deliberately narrow SQLite-style consumer can preserve the literal segments and turn each interpolation into a bound parameter:

```python
# Python 3.14+ only
from string.templatelib import Template

def sql(template: Template) -> tuple[str, tuple[object, ...]]:
    parameters: list[object] = []
    pieces: list[str] = []
    for index, literal in enumerate(template.strings):
        pieces.append(literal)
        if index < len(template.interpolations):
            part = template.interpolations[index]
            if part.conversion is not None or part.format_spec:
                raise ValueError("SQL interpolations do not accept conversions or format specs")
            pieces.append("?")
            parameters.append(part.value)
    return "".join(pieces), tuple(parameters)

name = "' OR 1=1 --"
query, params = sql(t"SELECT * FROM users WHERE name = {name}")
# query == "SELECT * FROM users WHERE name = ?"
# params == ("' OR 1=1 --",)
```

This is a contract sketch, not a general SQL library: placeholder syntax varies by driver, and a production implementation must validate the template type, interpolation policy, literal SQL, and supported value types. The malicious-looking input remains a parameter value rather than changing SQL structure. Test parameter order for multiple and repeated interpolations, `None` and supported data types, literal text preservation, unsupported conversion/format options, and malicious-looking values. T-strings preserve structure; the consumer is responsible for safe binding and correct destination-specific behavior.

### A-C27 — Q-C27

The assignment `self.cache = {}` fails because `@dataclass(slots=True)` creates a class whose instances have slots only for declared fields; there is no `cache` slot or ordinary instance `__dict__`. Declare `cache` as a field (for example, `cache: dict[str, object] = field(default_factory=dict, init=False, repr=False)`) or remove slots if dynamic attributes are part of the design. The base validation is skipped because defining `Child.__post_init__` overrides the inherited method and the generated dataclass initializer calls the most-derived `__post_init__` once; it does not automatically chain base post-init methods.

A corrected design is:

```python
from dataclasses import dataclass, field

@dataclass(slots=True)
class Base:
    name: str
    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name is required")

@dataclass(slots=True)
class Child(Base):
    enabled: bool = True
    cache: dict[str, object] = field(default_factory=dict, init=False, repr=False)
    def __post_init__(self) -> None:
        super(Child, self).__post_init__()  # explicit form avoids the zero-arg-super slots pitfall
        self.enabled = bool(self.enabled)
```

With `slots=True`, the decorator returns a replacement class; zero-argument `super()` can fail in some dataclass-slots inheritance situations because its `__class__` cell can refer to the original class. Test the exact interpreter and inheritance layout; `super(Child, self)` or an explicit base call may be necessary. Dataclass inheritance combines fields in order, so a required non-default field after an inherited default can raise a constructor-ordering `TypeError`; keyword-only fields can often avoid that ordering conflict. `attrs` or an explicit initializer may be more suitable when inheritance and validation rules become complex.
---

## Phase D — Evolution and Compatibility

### A-D28 — Q-D28

```python
import warnings

def lookup(key):
    # New implementation.
    ...

def old_lookup(key):
    warnings.warn(
        "old_lookup() is deprecated; use lookup()",
        DeprecationWarning,
        stacklevel=2,
    )
    return lookup(key)
```

For a simple wrapper, `stacklevel=2` points to the immediate caller rather than the `warnings.warn` line in the library. If multiple wrapper layers intervene, determine the intended public call site and adjust the stack level or use a more deliberate helper strategy. `DeprecationWarning` is appropriate for developers/library consumers and is normally ignored outside `__main__` under default filters; tests often enable it explicitly. A visible behavior change aimed at application end users may warrant `FutureWarning`, depending on the library's audience and migration policy. Python 3.13+'s `warnings.deprecated` can mark a function or class as deprecated for runtime warnings and static tooling; for older versions, use `typing_extensions.deprecated` when its behavior fits or combine a manual wrapper warning with appropriate type-checker support. Do not select a category merely to make the warning visible; choose it based on who needs to act.

### A-D29 — Q-D29

```python
import inspect
import pytest


def test_old_lookup_warns():
    with pytest.warns(DeprecationWarning, match=r"old_lookup\(\).*use lookup") as caught:
        expected_line = inspect.currentframe().f_lineno + 1
        old_lookup("k")
    assert len(caught) == 1
    assert caught[0].filename == __file__
    assert caught[0].lineno == expected_line
```

The `pytest.warns` validates category and regex-matched message; the captured record can verify `filename` and `lineno` when the call site is stable. With `stacklevel=2`, assert that the warning points to the test's call line, not the wrapper's `warnings.warn` line. The actions mean: `default` shows a matching warning once per source location (using a registry), `always` shows every occurrence, `once` shows it once per warning message/category across locations, and `module` shows it once per module location policy. The exact suppression behavior interacts with warning registries. For CI, make first-party warnings errors and review third-party warnings deliberately; do not globally ignore them. Later matching filters can override earlier ones, and a caller-attributed warning may not match a filter scoped only to the library module. `catch_warnings()` and filter changes mutate process-level warning configuration; do not assume independent, thread-safe filter state around concurrent tasks, especially across interpreter versions. Use `-W error` or pytest `filterwarnings` carefully and document narrow exceptions. `ResourceWarning` can expose leaked files/sockets and is commonly hidden by normal default filters; `-X dev` enables additional development checks and makes more resource warnings visible. `logging.captureWarnings(True)` redirects warning messages to the `py.warnings` logger, but it does not replace a deliberate filter policy or guarantee that every warning is emitted.

### A-D30 — Q-D30

```python
import warnings

# Assume Client is the new public class in this module.
def __getattr__(name: str):
    if name == "OldClient":
        warnings.warn(
            "OldClient is deprecated; use Client",
            DeprecationWarning,
            stacklevel=2,
        )
        return Client
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

Module-level `__getattr__` (PEP 562, Python 3.7+) is called for missing module attributes, enabling a compatibility alias. It supports `from module import OldClient`, but that import can emit a warning during import and then bind the alias locally; subsequent uses of that local binding do not necessarily trigger the module hook again. Repeated direct lookups can emit repeated warnings unless you design caching or warning policy deliberately. Introspection, `dir()`, documentation tools, static type checkers, and stub files may need explicit support; add the old name to `__all__` or `__dir__` only if that matches the intended compatibility behavior. Document the replacement, provide a migration guide, keep the alias for a defined grace period (for example at least two minor releases or 6–12 months if that matches project policy), and remove it only after a release note, tests, dependency/user impact review, and a major-version or otherwise explicitly allowed breaking release. Where feasible, measure deprecated API use through privacy-safe, low-cardinality telemetry or explicit opt-in diagnostics; never log secrets or assume warning counts alone equal production usage, because filters and warning registries can suppress repeats.

### A-D31 — Q-D31

**Exact output on Python 3.13 (assuming the code runs and imports succeed):**

```text
stdlib
True
```

Python 3.11+ provides `tomllib` in the standard library, so `source` becomes `"stdlib"` and the module exposes `loads`. On Python 3.10, the code takes the `tomli` branch and prints `backport` then `True`, assuming `tomli` is installed. If `tomli` is missing on 3.10, the import fails with `ModuleNotFoundError`; the shim does not install dependencies by itself. `tomllib` parses TOML but is read-only; code needing to write TOML needs a separate package or its own serializer.

### A-D32 — Q-D32

| Feature / change | Minimum version | Compatibility or migration note |
|---|---:|---|
| `match` / `case` syntax; `zip(strict=True)` | 3.10 | `match` syntax needs a separate older-compatible implementation; use explicit length checks or a tested helper instead of `zip(strict=True)` on older runtimes. |
| Built-in `ExceptionGroup` / `except*`; `tomllib`; `Self`; `asyncio.TaskGroup` and `asyncio.timeout` | 3.11 | Use the `exceptiongroup` backport for the group API, `tomli` for TOML reading, and `typing_extensions.Self` where appropriate; `except*` syntax itself cannot be parsed on older versions. |
| PEP 695 `class Box[T]`, `type Alias = ...`, and PEP 701 f-string grammar | 3.12 | Use traditional `TypeVar`/`Generic` and alias assignments; refactor f-string expressions to older grammar if older parsers must load the module. |
| `itertools.batched`; `typing.override`; `sys.monitoring`; `distutils` removal | 3.12 | Use a small tested batching helper or `more_itertools`; backport `override` from `typing_extensions`; replace `distutils` imports with supported packaging/build tools. |
| `copy.replace`; `warnings.deprecated`; `typing.TypeIs`; `typing.ReadOnly`; defined `locals()` semantics (PEP 667) | 3.13 | Use `dataclasses.replace` for dataclasses or a type-specific helper; use `typing_extensions` for supported backports; do not rely on old optimized-scope `locals()` mutation behavior. |
| Deferred annotation evaluation (PEP 649/749); template strings (PEP 750); `compression.zstd`; `uuid.uuid7`; `concurrent.interpreters`; `sys.remote_exec` | 3.14 | Treat annotation introspection as a compatibility boundary; use explicit APIs or third-party packages where older runtimes must be supported; t-string consumers must implement destination-specific safety. |
| Experimental free-threaded build | 3.13 (experimental); 3.14 has official support status for the build | It is still a distinct runtime configuration; verify dependency and extension compatibility, thread safety, and workload benchmarks rather than assuming universal readiness. |
| `datetime.utcnow()` deprecation | 3.12 | Prefer `datetime.now(timezone.utc)` for an aware UTC timestamp. |
| `imp`, `asynchat`, and other PEP 594 dead batteries removed | 3.12 | Replace each removed module with its documented modern alternative; test import paths at the declared minimum. |
| Multiprocessing default start-method change on supported POSIX platforms | 3.14 | Do not rely on inherited parent-process state; select a context deliberately and test spawn/forkserver-safe imports and pickling. |

`from __future__ import annotations` affects annotation evaluation/stringization behavior; it does not teach an old parser new grammar. For example, Python 3.11 cannot parse PEP 695 bracketed type parameters or Python 3.14 t-string syntax merely because the future import is present. Static type-checker diagnostics are also separate from runtime behavior: backported annotations may be understood by a checker even when the runtime API is absent.
### A-D33 — Q-D33

First reconcile the policy: if `requires-python = ">=3.12"`, Python 3.11 is not a supported runtime, so 3.11 CI can be an informational compatibility probe but must not be advertised as supported. If the project intends to support 3.11, change the metadata only after ensuring all source syntax, imports, dependencies, and runtime behavior work there. Example matrix outline:

```toml
[project]
requires-python = ">=3.12"

[tool.ruff]
target-version = "py312"

[tool.pytest.ini_options]
filterwarnings = [
  "error::DeprecationWarning:my_package(\\.|$)",
]
```

Then use `uv python install 3.12 3.13` and tox/nox environments (or CI matrix jobs) to run `uv run --python 3.12 pytest` and `uv run --python 3.13 pytest`, with dependency lock strategy documented. Add `ruff check --select UP` or configure `UP` rules in the project's Ruff configuration, review diffs manually, and run type checking separately. If 3.11 is intentionally tested, label it non-blocking/unsupported and avoid claiming compatibility from that job. A package's declared minimum must match syntax, imports, dependency metadata, and the versions exercised by required CI jobs.

### A-D34 — Q-D34

A safe sequence is:

1. Inventory production Python versions, package constraints, transitive dependencies, native extensions, wheel tags/platforms, and any source builds.
2. Establish a baseline of correctness, latency, memory, error rates, and startup time on Python 3.10.
3. Add Python 3.13 to CI and staging without removing the existing baseline. Verify wheels are available for every target platform and architecture; build from source only with reproducible toolchains and a clear fallback.
4. Upgrade incompatible dependencies in controlled, reviewable batches. Fix deprecation warnings and removed APIs, including behavior changes that tests may not expose.
5. Run unit, integration, contract, load, migration, and failure-injection tests under the target interpreter. Treat warnings from first-party code as errors where practical.
6. Deploy to staging, then canary a small traffic slice. Monitor crashes, latency percentiles, CPU/memory, queue depth, retries, native crashes, and business correctness.
7. Define rollback triggers and verify that the previous image and dependency lock remain deployable. Avoid irreversible schema/data changes in the interpreter rollout.
8. Expand traffic only after an agreed observation window. Change `requires-python` and classifiers only when the supported package policy actually changes.

Changing Python and all dependencies simultaneously makes regressions difficult to attribute. Native extensions may lack compatible wheels, require recompilation, or have ABI/free-threading assumptions. Audit behavior changes as well as removed imports: for example, review `tarfile` extraction filters and the Python 3.14 multiprocessing default start method on Linux (`forkserver`), then test code that relies on extraction behavior, inherited process state, or `fork`. Keep the rollback artifact and a known-good lockfile until the new runtime is accepted.

### A-D35 — Q-D35

Use the same workload inputs and correctness assertions on Python 3.10, 3.12, and 3.14, with pinned dependencies where feasible. Record exact interpreter patch/build, OS/kernel, CPU, memory, compiler/build flags, container image digest, dependency versions, and whether JIT/free-threaded options are enabled. Separate setup from measured work; warm up consistently where relevant; repeat enough independent runs to report a distribution (median and spread, not only the best result). Measure wall-clock latency/throughput and memory, and profile to explain material changes. Keep input size and output validation identical; run the benchmark in a quiet, controlled environment and publish raw data and the harness. Do not invent a result before running it. A free-threaded build or JIT-enabled configuration is a distinct runtime configuration: extension compatibility, thread safety, workload parallelism, warm-up, and build status can differ from the standard build. Release-note claims are not a substitute for measuring the service's own workload.

### A-D36 — Q-D36

A useful RFC outline:

1. **Decision and scope:** current minimum, proposed minimum, service/package boundaries, and why now.
2. **Support and security:** official Python lifecycle dates, EOL exposure, patch process, CVE response, dependency maintenance, and supply-chain controls.
3. **Compatibility inventory:** dependencies, C extensions, wheel coverage by OS/architecture, startup/runtime behavior, and removed/deprecated APIs.
4. **Build/reproducibility:** Docker base image, immutable digest pinning where required, lockfiles, build provenance, vulnerability scanning, and scheduled image refreshes.
5. **Test and rollout plan:** CI matrix, warnings-as-errors policy, integration/load tests, staging, canary percentage, observation window, and monitoring owners.
6. **Acceptance criteria:** no correctness regression, agreed latency/memory/error budgets, supported wheel coverage, zero unapproved first-party deprecation warnings, and verified rollback.
7. **Rollback:** quantitative triggers, previous image/lock artifact, decision owner, and steps to restore traffic.
8. **Metadata and communication:** when `requires-python` and classifiers change, release notes, migration guide, and deadline for consumers.

A “last N versions” policy is easy to communicate but must be grounded in the project's users, dependencies, and release cadence; a fixed minimum can be more predictable for long-lived products but may strand users unless reviewed regularly. SPEC 0 is a community policy for participating scientific Python projects, not a universal mandate. EOL interpreters should not be treated as secure merely because a workload still runs; either migrate, isolate with an explicit risk acceptance, or stop claiming support.

---

# Self-Assessment Rubric

Use this after completing the bank:

- **Strong:** Can explain the semantics, identify version boundaries, implement the solution, test edge cases, and justify trade-offs without relying on the answer key.
- **Developing:** Understands the main feature but misses an edge case, compatibility boundary, or failure mode.
- **Revisit:** Can repeat the syntax but cannot explain why it behaves as shown or how it affects a public API or production deployment.

Suggested scoring: 1 point for a correct core answer and up to 2 additional points for correct reasoning, edge cases, and compatibility/design justification. For Predict the Output questions, award full credit only when both output and explanation are correct. Use the rubric diagnostically; it is not a substitute for the module roadmap's completion checklist.
