# Practice Assessment — Metaprogramming and Dynamic Python

**Baseline:** Python 3.12+ (roadmap target). **Scope:** Stage 1, Module 1.12, `12-Metaprogramming-and-Dynamic-Python/`, Lessons 01–10. **Use:** attempt the questions first; consult the answer key only afterward.

This assessment follows the source roadmap's four phases: **A — Looking Inside Objects**, **B — Wrapping and Generating Behaviour**, **C — Hooking Class Creation**, and **D — Code as Data**. It tests the roadmap's preferred tool ladder: plain code → decorators → class decorators → `__init_subclass__` → descriptors → metaclasses → AST/`exec`. Use the simplest tool that meets the requirement.

## Instructions and conventions

- Core questions: **35**. Separate security review questions: **6**.
- Each question states its ID, lesson, difficulty, format, and what it assesses.
- For code-output questions, assume the snippet is run as shown and no unrelated names are defined.
- For implementation questions, give a tested solution, not merely a description. Unless specified, include at least one negative test.
- Treat any user-controlled string as untrusted. Do not run arbitrary source during this assessment.
- Python behavior involving annotation evaluation and AST shapes can vary by version; state the target version and verify version-sensitive assumptions.

# Part I — Questions (answers are in Part II)

## Phase A — Looking Inside Objects (Q01–Q08)

### Q01 — Bind before calling an unknown function
- **Lesson:** 01 — introspection with `inspect` and `dir()`
- **Difficulty:** Intermediate
- **Format:** Implementation / test design
- **Demonstrate:** Use `inspect.signature()`, `Signature.bind()`, and `BoundArguments.apply_defaults()` correctly.

Implement `call_by_keywords(fn, supplied: dict[str, object])` that validates the supplied keyword arguments against `fn`'s signature, applies defaults, and invokes the function. It must reject missing required arguments and unknown keywords with the normal `TypeError` behavior. Test it with:

```python
def format_user(name: str, active: bool = True, *, region: str) -> str:
    return f"{name}:{active}:{region}"
```

### Q02 — `dir`, `vars`, and static lookup
- **Lesson:** 01
- **Difficulty:** Basic–Intermediate
- **Format:** Conceptual / code reading
- **Demonstrate:** Distinguish advertised names, instance namespace, and non-triggering attribute inspection.

Given a class with an instance attribute, an inherited method, and a property that increments a counter whenever accessed, explain what `dir(obj)`, `vars(obj)`, `getattr(obj, "value")`, and `inspect.getattr_static(obj, "value")` tell you. Which operation can execute the property's getter? Why should `dir()` not be treated as a stable public API?

### Q03 — Dynamic configuration wrapper
- **Lesson:** 02 — dynamic attribute access
- **Difficulty:** Intermediate
- **Format:** Implementation
- **Demonstrate:** Implement recursive read-only attribute access with correct `AttributeError` behavior.

Implement `Config(data)` so `Config({"db": {"host": "localhost"}}).db.host` returns `"localhost"`; missing attributes raise `AttributeError`; assignment is rejected; and keys beginning with `_` are not exposed. Add tests for a missing key and a key/method-name collision such as `items`.

### Q04 — Diagnose `__getattr__` recursion
- **Lesson:** 02
- **Difficulty:** Intermediate
- **Format:** Find the bug
- **Demonstrate:** Avoid recursive lookup during initialization and preserve Python's missing-attribute contract.

Why can this implementation recurse, and how should it be corrected?

```python
class Proxy:
    def __init__(self, target):
        self.target = target
    def __getattr__(self, name):
        return getattr(self.target, name)
```

Discuss what happens if `target` has not yet been set or if the target itself is missing the requested name. Include one test that confirms missing attributes raise `AttributeError` rather than returning `None`.

### Q05 — `hasattr` hides more than absence
- **Lesson:** 02
- **Difficulty:** Intermediate
- **Format:** Debugging / reasoning
- **Demonstrate:** Explain that `hasattr()` invokes lookup and suppresses `AttributeError` raised during it.

A property raises `AttributeError("backend is misconfigured")` from inside its getter. Explain why `hasattr(obj, "backend")` may return `False`, even though the property exists. Recommend a safer inspection approach when the goal is to inspect the descriptor without invoking it.

### Q06 — Dispatch safely
- **Lesson:** 02
- **Difficulty:** Intermediate
- **Format:** Code correction / security
- **Demonstrate:** Prefer explicit dispatch or allow-lists over unrestricted user-controlled `getattr`.

Replace `getattr(handler, f"handle_{request_kind}")` with an explicit dispatch table for `created` and `deleted`. Unknown kinds must raise a clear `ValueError`; the request must not select arbitrary attributes.

### Q07 — Signature binding versus trial invocation
- **Lesson:** 01
- **Difficulty:** Basic
- **Format:** Short answer
- **Demonstrate:** Explain what `Signature.bind()` validates and what it does not do.

Does `inspect.signature(fn).bind(*args, **kwargs)` execute `fn`? Does it validate semantic constraints such as `age > 0` or verify that a runtime object matches an annotation? Explain.

### Q08 — Introspection under side effects
- **Lesson:** 01
- **Difficulty:** Advanced
- **Format:** Architecture / trade-off
- **Demonstrate:** Choose introspection tools for potentially side-effectful objects.

A plugin inspector scans objects supplied by third parties. Compare `inspect.getmembers()` with `inspect.getattr_static()` for this task. State the trade-off and give a safe inspection policy. Mention why inspecting a hostile object in-process is not made harmless merely by using introspection APIs.

## Phase B — Wrapping and Generating Behaviour (Q09–Q18)

### Q09 — Parameterized retry decorator
- **Lesson:** 03 — parametrized and class-based decorators
- **Difficulty:** Intermediate
- **Format:** Implementation / tests
- **Demonstrate:** Build a decorator factory, preserve metadata, retry only selected exceptions, and re-raise the final failure.

Implement `retry(times=3, exceptions=(OSError,))`. `times` means total attempts and must be at least one. Preserve function metadata with `functools.wraps`; do not swallow the final exception. Test one transient failure followed by success, and a non-retryable exception.

### Q10 — Timing decorator for sync and async functions
- **Lesson:** 03
- **Difficulty:** Advanced
- **Format:** Implementation / tests
- **Demonstrate:** Use `time.perf_counter()` and distinguish coroutine functions from ordinary functions.

Implement `timed(on_elapsed)` that supports both `def` and `async def`, invokes `on_elapsed(seconds)` once per call in a `finally` block, preserves metadata, and preserves return values/exceptions. Test a sync function and an async function. State whether the callback itself is permitted to raise and how you would specify that policy.

### Q11 — `once` and concurrency semantics
- **Lesson:** 03
- **Difficulty:** Advanced
- **Format:** Implementation / architecture
- **Demonstrate:** Define cache semantics, exception behavior, and thread-safety.

Design `once(fn)` for a synchronous zero-argument function: cache the first successful return value, but do not cache exceptions. Give a reference implementation and tests. Then explain why a naïve implementation is not thread-safe and what synchronization changes.

### Q12 — Class-based decorator binding bug
- **Lesson:** 03
- **Difficulty:** Advanced
- **Format:** Find the bug
- **Demonstrate:** Explain descriptor binding for decorated methods.

Why can the following decorator object fail when used on an instance method? Give a corrected descriptor-aware implementation or explain when a function wrapper is the simpler choice.

```python
class CountCalls:
    def __init__(self, fn):
        self.fn = fn
        self.calls = 0
    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.fn(*args, **kwargs)
```

### Q13 — Preserve metadata and signature
- **Lesson:** 03
- **Difficulty:** Intermediate
- **Format:** Code review
- **Demonstrate:** Use `functools.wraps`; distinguish runtime introspection from static typing.

Review a wrapper defined as `def wrapper(*args, **kwargs): return fn(*args, **kwargs)`. What breaks if `@functools.wraps(fn)` is omitted? Does `wraps` alone guarantee that a type checker infers the original parameter types? What typing tools are relevant?

### Q14 — `@auto_repr`
- **Lesson:** 04 — class decorators and class factories
- **Difficulty:** Intermediate
- **Format:** Implementation / tests
- **Demonstrate:** Add behavior to a class while preserving the class object and avoiding accidental disclosure.

Implement `@auto_repr` that adds `__repr__` only if the class does not define one. Render public names from `vars(self)` in sorted order. Test deterministic output and explain why production code may need an explicit field allow-list instead of printing every public attribute.

### Q15 — `@frozen_after_init`
- **Lesson:** 04
- **Difficulty:** Advanced
- **Format:** Implementation / edge cases
- **Demonstrate:** Use a class decorator to enforce a narrowly defined post-initialization mutation policy.

Implement a class decorator that permits assignments during `__init__`, then rejects later assignments to existing public attributes. It must allow initialization of multiple fields and use `object.__setattr__` to avoid recursion. State its limitations for nested mutable objects, deletion, and inheritance; add tests.

### Q16 — Class decorator or class factory?
- **Lesson:** 04
- **Difficulty:** Intermediate
- **Format:** Architecture / trade-off
- **Demonstrate:** Choose based on whether the input is an existing class or a parameterized construction recipe.

Compare a class decorator that adds a method to an existing class with a factory that creates and returns a new class. Discuss identity, `__module__`/`__qualname__`, pickling, debugging, and when a plain helper is enough.

### Q17 — Async decorator test design
- **Lesson:** 03
- **Difficulty:** Advanced
- **Format:** Test design
- **Demonstrate:** Test actual await behavior rather than only checking wrapper type.

List a minimal test matrix for an async-aware decorator: return value, raised exception, metadata, coroutine detection, and callback behavior. Explain why wrapping `async def` with an ordinary `def` that returns a coroutine can change `inspect.iscoroutinefunction()` behavior.

### Q18 — Decorator stacking and observability
- **Lesson:** 03
- **Difficulty:** Advanced
- **Format:** Code reading / security review
- **Demonstrate:** Reason about bottom-up application and safe logging.

For `@outer` above `@inner`, express the equivalent nested call. What should a timing/logging decorator avoid recording? Give two design criteria for deciding whether the behavior belongs in a decorator or explicit composition.

## Phase C — Hooking Class Creation (Q19–Q26)

### Q19 — Subclass registry with `__init_subclass__`
- **Lesson:** 05 — subclass registries
- **Difficulty:** Intermediate
- **Format:** Implementation / tests
- **Demonstrate:** Register subclasses by explicit key, reject duplicate keys, and cooperate with `super()`.

Implement a `Plugin` base with `registry: dict[str, type[Plugin]]`. Subclasses may declare `name="csv"`; the base class itself is not registered. Reject duplicate names and pass unknown class keywords cooperatively through `super().__init_subclass__(**kwargs)`. Test a duplicate and an unnamed subclass.

### Q20 — Class statement to `type()`
- **Lesson:** 06 — dynamic class creation
- **Difficulty:** Intermediate
- **Format:** Code translation
- **Demonstrate:** Map bases, namespace, and class attributes into `type(name, bases, namespace)`.

Translate this class into a `type()` call and verify its behavior:

```python
class Greeter:
    prefix = "Hello"
    def greet(self, name):
        return f"{self.prefix}, {name}"
```

Explain what extra work may be needed for `__module__`, `__qualname__`, descriptors, and pickling if the class is intended to behave like a normal importable top-level class.

### Q21 — Dynamic class and pickling
- **Lesson:** 06
- **Difficulty:** Advanced
- **Format:** Debugging / reasoning
- **Demonstrate:** Explain why dynamic class creation alone does not ensure picklability.

A dynamically created class can be instantiated but pickling fails. List the importability and identity conditions generally required by pickle for ordinary class instances. Give a practical fix or explain why a dynamic class should not be persisted that way.

### Q22 — `__init_subclass__` versus metaclass
- **Lesson:** 05, 07 — metaclasses
- **Difficulty:** Advanced
- **Format:** Architecture
- **Demonstrate:** Choose the least powerful class-creation hook that meets the need.

A base class only needs to collect declared `Field` objects and register subclasses. Would you start with `__init_subclass__`, a metaclass, or `exec`? Justify the choice and describe one condition that could justify escalating to a metaclass.

### Q23 — Singleton metaclass versus module instance
- **Lesson:** 07 — metaclasses
- **Difficulty:** Advanced
- **Format:** Architecture / trade-off
- **Demonstrate:** Compare global lifecycle strategies and testability.

Compare a singleton metaclass with a module-level instance or dependency injection. Discuss subclass semantics, thread-safety, test isolation, reset behavior, and hidden global state. Recommend a default for ordinary application services.

### Q24 — Resolve a metaclass conflict
- **Lesson:** 07
- **Difficulty:** Advanced
- **Format:** Debugging
- **Demonstrate:** Explain the most-derived metaclass rule and a cooperative resolution.

Given unrelated base metaclasses `MetaA` and `MetaB`, why can `class Combined(A, B)` fail? Describe the compatible derived metaclass strategy and explain why blindly composing metaclasses can be unsafe.

### Q25 — Class creation order and descriptor hooks
- **Lesson:** 05, 06, 07
- **Difficulty:** Advanced
- **Format:** Short answer / sequencing
- **Demonstrate:** Describe `__prepare__`, metaclass `__new__`, `type.__new__`, `__set_name__`, `__init_subclass__`, and metaclass `__init__` at a high level.

Give the relevant ordering for a normal class statement and explain why a descriptor assigned to a class *after* class creation does not automatically receive `__set_name__`.

### Q26 — `type()` or `types.new_class()`?
- **Lesson:** 06
- **Difficulty:** Advanced
- **Format:** Design choice
- **Demonstrate:** Recognize when class namespace preparation and metaclass selection matter.

When is `types.new_class()` a better fit than `type()`? Explain the role of a namespace callback and how this relates to metaclass `__prepare__`.

## Phase D — Code as Data (Q27–Q35)

### Q27 — AST visitor, tree shape, and static-analysis limits
- **Lesson:** 08 — AST and code generation
- **Difficulty:** Advanced
- **Format:** Implementation / tests / code analysis
- **Demonstrate:** Traverse nested definitions and report line numbers without executing source; read tree structure accurately.

Write an `ast.NodeVisitor` that reports (a) function/async-function definitions with list/dict/set literal defaults, (b) function/class definitions missing docstrings, (c) calls to `print`, and (d) bare `except:` handlers. It must visit nested functions and classes. Explain why a default like `DEFAULTS` is not identified as mutable by this syntactic check alone. For `ast.parse("a.b(c)", mode="eval")`, identify the `Call`, `Attribute`, and `Name` relationships you expect in `ast.dump()`. Explain why regex is brittle for nested syntax, why `ast.unparse()` cannot preserve comments or original formatting, and how you would extend the visitor to flag functions longer than 40 source lines.

### Q28 — Rewrite `x ** 2` to `x * x`
- **Lesson:** 08
- **Difficulty:** Advanced
- **Format:** Transformation / semantics
- **Demonstrate:** Use `ast.NodeTransformer`, preserve locations, compile the result, and state assumptions.

Implement a transformer that rewrites only `ast.BinOp(ast.Pow, Constant(2))` into multiplication of two copies of the left expression. Test `x ** 2`, `f() ** 2`, `x ** 3`, and `x ** 2.0`. Explain why the rewrite is not universally semantics-preserving for overloaded operators or side-effecting expressions, and state a conservative grammar/assumption or change the rewrite to avoid duplicating evaluation. When would you choose a concrete syntax tree tool such as LibCST instead of `ast`? Name two AST version changes a repository-wide codemod should account for.

### Q29 — Visitor traversal bug
- **Lesson:** 08
- **Difficulty:** Intermediate
- **Format:** Find the bug
- **Demonstrate:** Know when `generic_visit()` is required.

A visitor implements `visit_FunctionDef()` to count functions but never calls `generic_visit(node)`. Why are nested functions/classes inside that function missed? Correct it and compare with `ast.walk()`.

### Q30 — `compile()` is not execution; tokens and scopes
- **Lesson:** 08, 09
- **Difficulty:** Intermediate
- **Format:** Output prediction / explanation
- **Demonstrate:** Distinguish parse, transform, compile, and execute; select the right source-analysis abstraction.

Explain what each stage does for `tree = ast.parse(source)`, `code = compile(tree, "<input>", "exec")`, and `exec(code, namespace)`. At which stage can syntax errors occur? At which stage does the code actually run? Why is executing untrusted code unsafe even if compilation succeeds? Also distinguish what `tokenize` provides that an AST discards, and what `symtable` can tell a static analyzer about scopes. State why AST node structures should be tested against the supported Python versions (for example, type-parameter nodes in 3.12 and template-string nodes in 3.14). Finally, summarize the Python 3.13 `locals()`/default-namespace change relevant to `exec()` and why explicit namespace mappings are preferable when predictable behavior is required.

### Q31 — Harden a numeric expression evaluator
- **Lesson:** 08, 09
- **Difficulty:** Advanced
- **Format:** Security implementation / tests
- **Demonstrate:** Build a small AST interpreter, not `eval`, with explicit nodes/operators and resource limits.

Design an evaluator for numeric constants and `+`, `-`, `*`, `/`, and bounded exponentiation. Reject calls, attributes, names, booleans, unsupported operators, invalid syntax, excessive source length, excessive node count/depth, huge numeric literals, and large exponents. Include at least six tests. Explain why an AST allow-list alone is not a complete DoS defense.

### Q32 — Audit-hook limitations
- **Lesson:** 09
- **Difficulty:** Advanced
- **Format:** Security review
- **Demonstrate:** Distinguish observability from isolation and prevention.

Explain what `sys.addaudithook()` can contribute when reviewing dynamic execution, and why it is not a complete sandbox. Give a safer architecture when arbitrary user code must run.

### Q33 — `literal_eval`, data formats, and untrusted input
- **Lesson:** 09
- **Difficulty:** Intermediate
- **Format:** Short answer / security
- **Demonstrate:** Choose a parser based on intended input grammar.

Choose among JSON/TOML, `ast.literal_eval()`, a dispatch table, and arbitrary `eval()` for (a) application configuration, (b) Python-like literal data, and (c) a user-selectable operation such as `add`. Explain the limits of `literal_eval()` and its potential resource-exhaustion concerns. During the same review, identify why untrusted `pickle.loads()`, unsafe YAML loading, shell commands built with `shell=True`, and code in notebooks/templates need separate threat analysis.

### Q34 — Declarative query DSL
- **Lesson:** 10 — declarative APIs and mini-DSLs
- **Difficulty:** Advanced
- **Format:** Implementation / architecture
- **Demonstrate:** Build expression objects with explicit nodes, use `&`/`|`, validate fields, and parameterize SQL values.

Design a minimal `col("age") > 18` expression tree. It must support comparisons and logical conjunction, reject unknown fields/operators, produce an explainable tree, and compile to SQL with `?` placeholders plus a separate parameter list. Explain why `and`/`or` cannot be overloaded to build equivalent trees and why identifiers need separate validation from values.

### Q35 — Mini-project integration, case study, and design ladder
- **Lesson:** 01–10 (integration)
- **Difficulty:** Advanced
- **Format:** Architecture / test plan / library analysis
- **Demonstrate:** Choose the simplest mechanism for each requirement and design acceptance tests; trace a real declarative API from declaration to behavior.

For a small `declkit` toolkit, map each requirement to a mechanism: signature validation, sync/async function validation, declarative fields, subclass registry, safe filter expression, and linting mutable defaults. Explain where descriptors, `__init_subclass__`, decorators, AST, and a metaclass are justified or unnecessary. Choose one roadmap library—Pydantic, SQLAlchemy, attrs, Typer, or Click—and explain how a user declaration becomes validated behavior, what is introspected or collected, and what trade-off it makes versus ordinary functions. Propose tests including ≥90% branch coverage, adversarial filter inputs, and type checking.

## Six separate spot-the-vulnerability questions (V01–V06)

These are independent from the 35 core questions. Analyze the code; do not execute it with hostile input.

### V01 — User expression passed to `eval`
- **Lesson:** 09
- **Difficulty:** Intermediate
- **Format:** Security review
- **Demonstrate:** Identify code injection and select a grammar-specific alternative.

```python
def calculate(user_text: str):
    return eval(user_text)
```

Identify the vulnerability, impact, and a safer replacement for a calculator that only needs arithmetic.

### V02 — Empty built-ins misconception
- **Lesson:** 09
- **Difficulty:** Advanced
- **Format:** Security review
- **Demonstrate:** Reject the claim that restricted built-ins form a secure sandbox.

```python
def evaluate(user_text: str):
    return eval(user_text, {"__builtins__": {}}, {})
```

Why is this not a security boundary? Give the recommended alternative for untrusted expressions and for arbitrary code that must genuinely execute.

### V03 — User-controlled `exec`
- **Lesson:** 09
- **Difficulty:** Intermediate
- **Format:** Security review
- **Demonstrate:** Identify arbitrary code execution and propose a safer design.

```python
def run_rule(source: str, record: dict[str, object]) -> None:
    exec(source, {"record": record})
```

What trust assumption is missing? Does passing a restricted globals dictionary make this safe? Suggest a data-driven rule representation or external isolation design.

### V04 — Attribute access controlled by request
- **Lesson:** 02, 09
- **Difficulty:** Intermediate
- **Format:** Security review
- **Demonstrate:** Apply an allow-list to dynamic dispatch.

```python
def read_property(obj: object, field: str):
    return getattr(obj, field)
```

Explain how a caller may access unintended attributes or trigger property side effects. Provide a safer field allow-list strategy.

### V05 — Dynamic method invocation with a prefix
- **Lesson:** 02
- **Difficulty:** Advanced
- **Format:** Security review
- **Demonstrate:** Recognize that string prefixes do not constitute authorization.

```python
def invoke(service, action: str, payload):
    method = getattr(service, "handle_" + action, None)
    if method is None:
        raise ValueError("unsupported action")
    return method(payload)
```

Why is the prefix check not a complete allow-list? Rewrite with an explicit dispatch mapping and discuss authorization separately from dispatch.

### V06 — LLM-generated code execution
- **Lesson:** 08–10
- **Difficulty:** Advanced
- **Format:** Security architecture
- **Demonstrate:** Treat generated source as untrusted and choose layered controls.

A service asks an LLM to generate Python for each user request and runs it with `exec()` in the API worker. Identify the principal risks and propose a layered architecture that does not rely on prompt instructions or empty built-ins as the security boundary.

# Part II — Answer Key and Reference Solutions

Solutions are reference answers, not the only acceptable designs. Where the question is architectural, grading should reward explicit assumptions and trade-offs. Most executable examples use assertions and are silent when successful; an uncaught exception or failed assertion indicates a failed check.

## Phase A answers

### A-Q01 — Reference solution

```python
import inspect
from collections.abc import Callable
from typing import Any

def call_by_keywords(fn: Callable[..., Any], supplied: dict[str, object]) -> Any:
    sig = inspect.signature(fn)
    bound = sig.bind(**supplied)  # raises TypeError for missing/extra arguments
    bound.apply_defaults()
    return fn(*bound.args, **bound.kwargs)

def format_user(name: str, active: bool = True, *, region: str) -> str:
    return f"{name}:{active}:{region}"

assert call_by_keywords(format_user, {"name": "Ada", "region": "EU"}) == "Ada:True:EU"
for invalid in (
    {"name": "Ada", "region": "EU", "oops": 1},
    {"name": "Ada"},  # required keyword-only region is missing
):
    try:
        call_by_keywords(format_user, invalid)
    except TypeError:
        pass
    else:
        raise AssertionError(f"invalid binding should fail: {invalid!r}")
```

`bind()` validates call shape without executing the target. `apply_defaults()` fills omitted defaults. The actual function is invoked only after binding. It does not validate semantic constraints or runtime annotation types. Edge cases: built-ins or decorated callables may not expose an inspectable signature; `inspect.signature()` can raise `ValueError`/`TypeError`, so production callers may need a documented fallback.

### A-Q02 — Expected reasoning

- `dir(obj)` returns a useful list of names, commonly including inherited and dynamically advertised names; it may call custom `__dir__` and is not a stable API contract.
- `vars(obj)` returns the object's `__dict__` when available; it does not include inherited members and fails for objects without a suitable namespace.
- `getattr(obj, "value")` performs normal lookup and may execute a property getter or custom `__getattribute__`/`__getattr__`.
- `inspect.getattr_static(obj, "value")` attempts static lookup without invoking the descriptor protocol or dynamic lookup hooks; it may return the property descriptor rather than the computed value.

A property getter can have side effects. For untrusted plugins, inspect statically where possible and do not assume any in-process interaction with a hostile object is a security boundary.

### A-Q03 — Reference solution

```python
class Config:
    __slots__ = ("_data",)

    def __init__(self, data: dict[str, object]) -> None:
        object.__setattr__(self, "_data", dict(data))

    def __getattribute__(self, name: str) -> object:
        # Hide internal implementation names through ordinary instance access.
        if name.startswith("_"):
            raise AttributeError(name)
        return object.__getattribute__(self, name)

    def __getattr__(self, name: str) -> object:
        if name.startswith("_") or name in {"items", "keys", "values"}:
            raise AttributeError(name)
        data = object.__getattribute__(self, "_data")
        try:
            value = data[name]
        except KeyError:
            raise AttributeError(name) from None
        return Config(value) if isinstance(value, dict) else value

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Config is read-only")

cfg = Config({"db": {"host": "localhost"}, "items": "not exposed"})
assert cfg.db.host == "localhost"
try:
    cfg.missing
except AttributeError:
    pass
else:
    raise AssertionError("missing key must raise AttributeError")
try:
    cfg.items
except AttributeError:
    pass
else:
    raise AssertionError("colliding key must not shadow the policy")
try:
    cfg._data
except AttributeError:
    pass
else:
    raise AssertionError("internal storage must not be exposed through normal lookup")
try:
    cfg.db = {"host": "elsewhere"}
except AttributeError:
    pass
else:
    raise AssertionError("configuration must be read-only")
try:
    cfg._private
except AttributeError:
    pass
else:
    raise AssertionError("underscore-prefixed names must not be exposed")
```

This deliberately makes collision behavior explicit and hides internal names during ordinary instance lookup. Another valid design is item access (`cfg["items"]`) for all keys, or a separate namespace for data. This remains a convenience wrapper, not a security boundary: nested dictionaries are copied only at each wrapper boundary, and values may still be mutable; deep immutability would require recursively copying/freezing values. A production type can use `Mapping` and a generic value type instead of a broad `object` return.

### A-Q04 — Correction

The initial access to `self.target` inside `__getattr__` can itself trigger `__getattr__("target")` if initialization has not completed or the attribute was deleted, causing recursion. Delegate to `object.__getattribute__` and translate only the proxy's missing target state deliberately:

```python
class Proxy:
    def __init__(self, target: object) -> None:
        object.__setattr__(self, "_target", target)

    def __getattr__(self, name: str) -> object:
        try:
            target = object.__getattribute__(self, "_target")
        except AttributeError:
            raise AttributeError(name) from None
        return getattr(target, name)  # absent target attribute propagates AttributeError
```

Test with `hasattr(Proxy(object()), "not_there") is False`. Returning `None` for every unknown name is incorrect because it hides typos and breaks normal lookup semantics.

### A-Q05 — Expected reasoning

`hasattr()` calls normal attribute lookup and returns `False` if an `AttributeError` escapes, regardless of whether it means “attribute absent” or was raised inside a descriptor. Use `inspect.getattr_static(obj, "backend", sentinel)` to determine whether a class/instance attribute is statically present without invoking its getter. Static presence does not prove that evaluating the property succeeds.

### A-Q06 — Reference solution

```python
from collections.abc import Callable

class Handler:
    def created(self, event: object) -> str:
        return f"created:{event}"
    def deleted(self, event: object) -> str:
        return f"deleted:{event}"

def dispatch(handler: Handler, kind: str, event: object) -> str:
    routes: dict[str, Callable[[object], str]] = {
        "created": handler.created,
        "deleted": handler.deleted,
    }
    try:
        route = routes[kind]
    except KeyError:
        raise ValueError(f"unsupported event kind: {kind!r}") from None
    return route(event)

assert dispatch(Handler(), "created", 7) == "created:7"
try:
    dispatch(Handler(), "__class__", None)
except ValueError:
    pass
else:
    raise AssertionError("unknown kind must fail")
```

The table is an explicit capability list. Authorization is still a separate concern: a valid action may not be allowed for every caller.

### A-Q07 — Expected answer

`bind()` checks positional/keyword structure, required parameters, duplicate assignments, and unexpected keywords based on the signature. It does not execute the function, validate application invariants, or automatically enforce annotations. An annotation such as `age: int` is metadata unless separate runtime validation is implemented.

### A-Q08 — Expected answer

`inspect.getmembers()` obtains attributes and can trigger descriptors/properties while collecting values. `inspect.getattr_static()` is preferable for passive structural inspection because it avoids ordinary descriptor execution. A safe policy includes a narrow supported object protocol, time/resource limits around plugin execution, avoiding arbitrary method calls during discovery, and process isolation for genuinely hostile plugins. Neither API neutralizes hostile Python objects already executing in the same interpreter.

Raw `__annotations__` may contain strings or unresolved forward references, depending on annotation syntax and interpreter/version. Resolve annotations deliberately with `typing.get_type_hints()` when evaluation is acceptable, or use the version-appropriate annotation inspection API (including `annotationlib` in Python 3.14) when lazy/raw access matters; resolving annotations can evaluate expressions and should not be done blindly on untrusted objects. `inspect.signature()` plus annotations can support dependency injection by mapping parameter types to registered providers, but runtime validation and provider authorization remain separate responsibilities.

## Phase B answers

### B-Q09 — Reference solution

```python
import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def retry(times: int = 3, exceptions: tuple[type[BaseException], ...] = (OSError,)):
    if times < 1:
        raise ValueError("times must be at least 1")
    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times - 1:
                        raise
            raise AssertionError("unreachable")
        return wrapper
    return decorate

attempts = 0
@retry(times=2)
def sometimes() -> str:
    global attempts
    attempts += 1
    if attempts == 1:
        raise OSError("transient")
    return "ok"
assert sometimes() == "ok" and attempts == 2

@retry(times=3)
def not_retryable() -> None:
    raise ValueError("do not retry")
try:
    not_retryable()
except ValueError as exc:
    assert str(exc) == "do not retry"
else:
    raise AssertionError("non-retryable exception should propagate")
try:
    retry(times=0)
except ValueError:
    pass
else:
    raise AssertionError("times=0 should be rejected")
```

A non-retryable exception propagates immediately because it is not in `exceptions`. The final selected exception is re-raised with its traceback. A production API should validate exception classes and consider backoff, jitter, idempotency, cancellation, and retry budgets. Avoid retrying arbitrary side-effectful operations by default.

### B-Q10 — Reference solution

```python
import functools
import inspect
import time
from collections.abc import Callable
from typing import Any

def timed(on_elapsed: Callable[[float], object]):
    def report(seconds: float) -> None:
        # Best-effort telemetry must not replace the target's result/exception.
        try:
            on_elapsed(seconds)
        except Exception:
            # Production code should send this failure to a safe logger/metric.
            pass

    def decorate(fn):
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    return await fn(*args, **kwargs)
                finally:
                    report(time.perf_counter() - start)
            return async_wrapper
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return fn(*args, **kwargs)
            finally:
                report(time.perf_counter() - start)
        return wrapper
    return decorate
```

Test both paths, including exception paths, and assert the callback runs exactly once. This reference policy deliberately treats telemetry as best-effort: callback exceptions are suppressed so they cannot replace the target's return value or exception; production code should report callback failures through a non-throwing logger/metric. Decorators around unusual callable objects or already wrapped async functions need additional tests. Smoke tests for both paths:

```python
import asyncio
elapsed = []
@timed(elapsed.append)
def sync_value(x): return x + 1
@timed(elapsed.append)
async def async_value(x): return x + 2
assert sync_value(1) == 2
assert asyncio.run(async_value(1)) == 3
assert len(elapsed) == 2 and all(value >= 0 for value in elapsed)

@timed(elapsed.append)
def sync_failure(): raise LookupError("expected")
@timed(elapsed.append)
async def async_failure(): raise LookupError("expected")
for call in (sync_failure, lambda: asyncio.run(async_failure())):
    try:
        call()
    except LookupError as exc:
        assert str(exc) == "expected"
    else:
        raise AssertionError("target exception should propagate")
assert len(elapsed) == 4  # callback runs once for each successful or failing call
```

The timing values are intentionally nondeterministic; tests assert invocation count and non-negativity, not an exact duration.

### B-Q11 — Reference solution and trade-off

```python
import functools
from typing import Callable, TypeVar
T = TypeVar("T")

def once(fn: Callable[[], T]) -> Callable[[], T]:
    import threading
    from typing import cast

    condition = threading.Condition()
    state: dict[str, object] = {"status": "empty", "owner": None}

    @functools.wraps(fn)
    def wrapper() -> T:
        ident = threading.get_ident()
        with condition:
            while state["status"] == "running":
                if state["owner"] == ident:
                    raise RuntimeError("recursive call to once-wrapped function")
                condition.wait()
            if state["status"] == "ready":
                return cast(T, state["value"])
            state["status"], state["owner"] = "running", ident
        try:
            value = fn()
        except BaseException:
            with condition:
                state["status"], state["owner"] = "empty", None
                condition.notify_all()
            raise
        with condition:
            state["value"] = value
            state["status"], state["owner"] = "ready", None
            condition.notify_all()
        return value
    return wrapper

calls = 0
@once
def answer():
    global calls
    calls += 1
    return None
assert answer() is None and answer() is None and calls == 1

failures = 0
@once
def fail_once() -> str:
    global failures
    failures += 1
    if failures == 1:
        raise ValueError("first attempt")
    return "recovered"
try:
    fail_once()
except ValueError:
    pass
assert fail_once() == "recovered" and failures == 2

import time
from concurrent.futures import ThreadPoolExecutor
concurrent_calls = 0
@once
def shared_value():
    global concurrent_calls
    concurrent_calls += 1
    time.sleep(0.01)
    return 42
with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(lambda _: shared_value(), range(16)))
assert results == [42] * 16 and concurrent_calls == 1

@once
def recursive():
    return recursive()
try:
    recursive()
except RuntimeError as exc:
    assert "recursive call" in str(exc)
else:
    raise AssertionError("recursive initialization must fail rather than deadlock")
```

The condition serializes concurrent first calls; waiters receive the cached successful result. Exceptions reset the state so a later caller can retry. A recursive call from the initializing thread raises `RuntimeError` instead of deadlocking. This is still a synchronous zero-argument design; async functions need a separate implementation that coordinates awaiters. The included concurrent and recursive tests exercise the principal synchronization branches; production tests should also cover timeout/cancellation policy if those are introduced.

### B-Q12 — Corrected class-based decorator

A decorator object is not automatically a function descriptor. Accessing `instance.method` does not bind `instance` to the stored function unless `__get__` implements binding.

```python
import functools
from types import MethodType

class CountCalls:
    def __init__(self, fn):
        functools.update_wrapper(self, fn)
        self.fn = fn
        self.calls = 0
    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.fn(*args, **kwargs)
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return MethodType(self, obj)
```

`MethodType(self, obj)` binds `obj` as the first argument to `self.__call__`, which then forwards it to the original method. A function-based wrapper is often simpler and naturally participates in function descriptor binding. For production code, test class access, instance access, metadata, inheritance, and concurrency of the counter. Minimal binding checks:

```python
class Greeter:
    @CountCalls
    def greet(self, name): return f"hi {name}"
g = Greeter()
assert g.greet("Ada") == "hi Ada"
assert Greeter.greet(g, "Lin") == "hi Lin"
assert Greeter.greet.calls == 2
assert Greeter.greet.__name__ == "greet"
```

The counter is shared by the decorated method object across all instances and is not synchronized; change the design if per-instance or thread-safe counts are required.

### B-Q13 — Expected answer

Without `wraps`, `__name__`, `__doc__`, `__wrapped__`, and signature introspection can be misleading; frameworks and debuggers may inspect the wrapper instead. `wraps` copies metadata and sets `__wrapped__`, but does not by itself provide precise static typing for arbitrary decorator transformations. Use `ParamSpec`/`TypeVar`, `Concatenate` when injecting arguments, or a carefully designed protocol/stub when necessary.

### B-Q14 — Reference solution

```python
from functools import wraps

def auto_repr(cls):
    if "__repr__" in cls.__dict__:
        return cls
    # Preserve a meaningful repr inherited from a base class.
    if any("__repr__" in base.__dict__ and base.__repr__ is not object.__repr__
           for base in cls.__mro__[1:]):
        return cls
    def __repr__(self):
        values = vars(self)
        public = {k: values[k] for k in sorted(values) if not k.startswith("_")}
        body = ", ".join(f"{k}={v!r}" for k, v in public.items())
        return f"{type(self).__name__}({body})"
    cls.__repr__ = __repr__
    return cls

@auto_repr
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self._token = "secret"

assert repr(User("Ada", 36)) == "User(age=36, name='Ada')"

class Custom:
    def __repr__(self): return "custom"
@auto_repr
class Existing(Custom):
    pass
assert repr(Existing()) == "custom"
```

This is intentionally small. It only includes instance `__dict__` fields and ignores slots/properties. Public attributes may still contain secrets; production representations should use explicit fields, redact sensitive values, and avoid dumping large objects.

### B-Q15 — Reference solution

```python
from functools import wraps

def frozen_after_init(cls):
    original_init = cls.__init__
    @wraps(original_init)
    def init(self, *args, **kwargs):
        object.__setattr__(self, "_initializing", True)
        try:
            original_init(self, *args, **kwargs)
        finally:
            object.__setattr__(self, "_initializing", False)
    cls.__init__ = init
    original_setattr = cls.__setattr__
    def guarded_setattr(self, name, value):
        if not name.startswith("_") and not object.__getattribute__(self, "_initializing"):
            # This implementation deliberately supports ordinary __dict__ instances.
            # Checking the instance dictionary avoids executing property getters.
            values = object.__getattribute__(self, "__dict__")
            if name in values:
                raise AttributeError(f"{name!r} is frozen after initialization")
        original_setattr(self, name, value)
    cls.__setattr__ = guarded_setattr
    return cls

@frozen_after_init
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

p = Point(1, 2)
try:
    p.x = 3
except AttributeError:
    pass
else:
    raise AssertionError("existing public attribute should be frozen")
p.label = "origin"  # allowed by the explicitly stated policy
assert p.label == "origin"
```

This implementation intentionally targets ordinary instances with `__dict__`; it does not support slot-only instances, and it freezes public names already stored in that dictionary. It does not prevent mutation of `p.some_list`, deletion, or every inheritance/custom-`__setattr__` combination. Checking `__dict__` avoids invoking property getters as part of the guard. If the desired policy is true immutability, use a narrower supported class contract or a dataclass with `frozen=True`, while understanding that nested mutable objects remain mutable. A robust production decorator should specify deletion and subclass behavior explicitly.

### B-Q16 — Expected answer

A class decorator receives an existing class and usually mutates or replaces it. A class factory creates a class from parameters, potentially using `type()` or `types.new_class()`. Replacing a class can alter identity, references, pickling/importability, metaclass behavior, and stack traces. Ensure `__module__` and `__qualname__` are suitable and that the class is bound under an importable module name for ordinary pickle use. If only a value transformation or registration is needed, prefer a plain function or decorator.

### B-Q17 — Expected test matrix

Test: returned value; exception propagation; callback exactly once on success and failure; `inspect.iscoroutinefunction()` on async target; `inspect.signature()` and `__wrapped__`; method binding; and cancellation behavior if async. An ordinary `def` wrapper returns a coroutine object but is not itself declared with `async def`, so coroutine-function introspection can differ even though awaiting the returned object works.

### B-Q18 — Expected answer

`@outer` above `@inner` is `fn = outer(inner(fn))`; decorators are applied bottom-up. Avoid logging passwords, tokens, personal data, full request bodies, and arbitrary `repr()` output. Prefer explicit composition when behavior needs visible control flow, has complex ordering, or requires configuration at each call site; use decorators for coherent cross-cutting behavior with well-defined semantics.

## Phase C answers

### C-Q19 — Reference solution

```python
class Plugin:
    registry: dict[str, type["Plugin"]] = {}
    def __init_subclass__(cls, *, name: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if name is None:
            raise TypeError("plugin subclasses must declare name=...")
        if name in Plugin.registry:
            raise ValueError(f"duplicate plugin name: {name!r}")
        Plugin.registry[name] = cls

class CsvPlugin(Plugin, name="csv"):
    pass

assert Plugin.registry["csv"] is CsvPlugin
try:
    class DuplicateCsv(Plugin, name="csv"):
        pass
except ValueError:
    pass
else:
    raise AssertionError("duplicate key should fail")
try:
    class Unnamed(Plugin):
        pass
except TypeError as exc:
    assert "must declare name" in str(exc)
else:
    raise AssertionError("unnamed plugin subclasses must fail")
```

`super().__init_subclass__(**kwargs)` supports cooperative multiple inheritance. This registry is process-global mutable state; tests should isolate/reset it, and plugin names should be trusted or validated if sourced externally. If an abstract intermediate subclass should not register, make that policy explicit (for example, with an opt-out keyword) rather than silently permitting unnamed concrete plugins.

### C-Q20 — Reference solution

```python
namespace = {
    "__module__": __name__,
    "prefix": "Hello",
    "greet": lambda self, name: f"{self.prefix}, {name}",
}
Greeter = type("Greeter", (), namespace)
assert Greeter().greet("Ada") == "Hello, Ada"
```

A lambda has a less useful name/qualname and can complicate debugging/pickling. For a more faithful dynamic definition, create a named function and set `__module__`; bind the class to a top-level module global under the expected name if pickle support is required. `type()` does not reproduce all class-statement namespace preparation and metaclass selection scenarios.

### C-Q21 — Expected answer

Ordinary pickle generally records a class by module and qualified name and expects that import to resolve to the same class object. A dynamically created class may not be bound to a stable importable name, or its module may not expose it. For persisted objects, prefer a normal module-level class or serialize validated data and reconstruct the object. Do not assume arbitrary dynamic classes are portable across processes or versions.

### C-Q22 — Expected answer

Start with `__init_subclass__` for subclass registration and class-level field collection. Use descriptors and `__set_name__` for field metadata. A metaclass may be justified when the behavior must control namespace preparation, class construction itself, or metaclass-level semantics that a base hook cannot express. `exec` is not needed for registration or field collection and expands the security/debugging surface.

### C-Q23 — Expected answer

A singleton metaclass changes construction semantics globally and must define subclass behavior and synchronization. A module-level instance is simpler but still global state. Dependency injection usually improves test isolation, lifecycle control, and explicit dependencies. Prefer ordinary instances with dependency injection unless process-wide uniqueness is a real domain invariant. If a singleton is required, document reset semantics and thread-safety; test isolation must not depend on hidden cached state.

### C-Q24 — Expected answer

Python needs a metaclass compatible with every base's metaclass; the winner must be a subtype of each candidate metaclass. Unrelated `MetaA` and `MetaB` can have no such subtype automatically, so class creation raises `TypeError`. Define a derived metaclass inheriting both only if their construction hooks are compatible and cooperative (`super()`), or refactor the feature to class decorators/`__init_subclass__`. Blind composition can violate assumptions or double-apply transformations.

### C-Q25 — Expected answer

At a high level: choose the metaclass; call its `__prepare__` to obtain the class namespace; execute the class body in that namespace; call the metaclass to create the class (normally `type.__new__`); descriptors in the new namespace receive `__set_name__` during `type.__new__`; the base hook `__init_subclass__` runs as part of type-level class creation; then metaclass `__init__` completes initialization. Exact details should be verified against the target version and custom metaclass. Assigning a descriptor after class creation does not automatically invoke `__set_name__`; call it explicitly if the descriptor contract requires it.

### C-Q26 — Expected answer

`type(name, bases, namespace)` is suitable for a straightforward class with a ready mapping. `types.new_class()` is useful when normal metaclass selection and namespace preparation matter; its callback fills the prepared namespace, which can be provided by a custom metaclass `__prepare__`. Prefer it when emulating class-statement mechanics rather than merely constructing a simple type.

## Phase D answers

### D-Q27 — Reference solution

```python
import ast

class DefaultAndDocstringVisitor(ast.NodeVisitor):
    def __init__(self):
        self.findings: list[tuple[int, str]] = []

    def _check(self, node):
        if ast.get_docstring(node) is None:
            self.findings.append((node.lineno, f"missing docstring: {node.name}"))
        args = node.args
        positional = [*args.posonlyargs, *args.args]
        defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)
        for arg, default in zip(positional, defaults):
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.findings.append((default.lineno, f"mutable default: {node.name}.{arg.arg}"))
        for arg, default in zip(args.kwonlyargs, args.kw_defaults):
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.findings.append((default.lineno, f"mutable default: {node.name}.{arg.arg}"))

    def visit_FunctionDef(self, node):
        self._check(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._check(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        if ast.get_docstring(node) is None:
            self.findings.append((node.lineno, f"missing docstring: class {node.name}"))
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.findings.append((node.lineno, "print call"))
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.findings.append((node.lineno, "bare except"))
        self.generic_visit(node)

source = "\nclass Outer:\n    def f(self, x=[]):\n        print(x)\n        def inner(y={}):\n            return y\n        try:\n            return inner(x)\n        except:\n            return None\n    async def af(self, *, options={1}):\n        return options\n"
tree = ast.parse(source)
visitor = DefaultAndDocstringVisitor()
visitor.visit(tree)
assert any("mutable default: f.x" in msg for _, msg in visitor.findings)
assert any("mutable default: inner.y" in msg for _, msg in visitor.findings)
assert any("mutable default: af.options" in msg for _, msg in visitor.findings)
assert any("missing docstring: class Outer" in msg for _, msg in visitor.findings)
assert any(msg == "print call" for _, msg in visitor.findings)
assert any(msg == "bare except" for _, msg in visitor.findings)
```

The visitor traverses nested class/function bodies through `generic_visit` and checks class docstrings separately. For `a.b(c)`, the outer node is `Call`; its `func` is `Attribute(value=Name(id="a"), attr="b")`, and its argument is `Name(id="c")`. The syntactic rule only catches literal list/dict/set defaults; it cannot infer that `DEFAULTS` references a mutable object without name resolution and deeper analysis. To flag functions longer than 40 source lines, inspect `node.end_lineno - node.lineno + 1` when `end_lineno` is available, and define whether decorators/docstrings count. A production lint rule should document whether it checks public API objects only, all definitions, or module-level docstrings as well. Regex is brittle for nested syntax because strings, comments, multiline expressions, and nested delimiters can resemble code; AST parsing gives structure but intentionally discards comments and much formatting. Use LibCST when formatting-preserving codemods are required.

### D-Q28 — Conservative reference solution

A direct rewrite that duplicates the left AST expression can duplicate side effects (`f()`) and can change overloaded operator behavior. A safe teaching solution should explicitly restrict the left side to a simple `Name` and exponent to integer constant `2`:

```python
import ast

class SquareNameTransformer(ast.NodeTransformer):
    """Rewrite only NAME ** 2 into NAME * NAME; names are assumed pure reads."""
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if (
            isinstance(node.op, ast.Pow)
            and isinstance(node.right, ast.Constant)
            and type(node.right.value) is int
            and node.right.value == 2
            and isinstance(node.left, ast.Name)
            and isinstance(node.left.ctx, ast.Load)
        ):
            replacement = ast.BinOp(
                left=ast.Name(id=node.left.id, ctx=ast.Load()),
                op=ast.Mult(),
                right=ast.Name(id=node.left.id, ctx=ast.Load()),
            )
            return ast.copy_location(replacement, node)
        return node

def transformed_source(source: str) -> str:
    tree = SquareNameTransformer().visit(ast.parse(source))
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)

assert "x * x" in transformed_source("result = x ** 2")
assert "f() ** 2" in transformed_source("result = f() ** 2")
assert "x ** 3" in transformed_source("result = x ** 3")
assert "x ** 2.0" in transformed_source("result = x ** 2.0")

tree = SquareNameTransformer().visit(ast.parse("result = x ** 2\n"))
ast.fix_missing_locations(tree)
code = compile(tree, "<square-rewrite>", "exec")
ns = {"x": 4}
exec(code, ns)
assert ns["result"] == 16
```

The grammar is deliberately narrow: only `Name ** integer-literal-2` is rewritten. `x ** 3`, `x ** 2.0`, `f() ** 2`, attributes, subscripts, and other forms are untouched. Even `x * x` may differ from `x ** 2` for a custom class that overloads arithmetic, so this is only valid under the stated numeric/pure-name assumption. `copy_location` preserves the original expression's source span and `fix_missing_locations` repairs descendants. This compiles and executes the transformed tree in a controlled test; it is not a recommendation to execute untrusted transformed source. Choose LibCST when a codemod must preserve comments, whitespace, and formatting. Version-tolerant tools should account for `ast.Constant` replacing older literal nodes in Python 3.8, type-parameter nodes introduced in 3.12, and `TemplateStr`/`Interpolation` nodes in 3.14; test against every supported interpreter.

### D-Q29 — Correction

```python
import ast

class FunctionCounter(ast.NodeVisitor):
    def __init__(self):
        self.count = 0
    def visit_FunctionDef(self, node):
        self.count += 1
        self.generic_visit(node)
    def visit_AsyncFunctionDef(self, node):
        self.count += 1
        self.generic_visit(node)
```

Without `generic_visit`, the visitor never descends into the function's arguments, decorators, body, nested classes, or nested functions. `ast.walk(tree)` visits descendants breadth-first but does not offer the same specialized control or parent context. A complete smoke test is:

```python
import ast

class FunctionCounter(ast.NodeVisitor):
    def __init__(self): self.count = 0
    def visit_FunctionDef(self, node):
        self.count += 1
        self.generic_visit(node)
    def visit_AsyncFunctionDef(self, node):
        self.count += 1
        self.generic_visit(node)

source = "def outer():\n    class Inner:\n        def method(self):\n            def nested(): pass\n"
visitor = FunctionCounter()
visitor.visit(ast.parse(source))
assert visitor.count == 3  # outer, method, nested
```

### D-Q30 — Expected answer

`ast.parse()` parses source into an AST and can raise `SyntaxError`; `compile(tree, filename, "exec")` compiles the AST into a code object and can raise compilation errors; `exec(code, namespace)` executes the code object and can trigger arbitrary runtime behavior. These are separate stages. `compile()` also accepts `"eval"` for expressions and `"single"` for interactive single statements; source can be tokenized first with `tokenize`, while `symtable.symtable()` provides scope/symbol-table information. In Python 3.13, PEP 667 standardized `locals()` in optimized scopes as a snapshot and aligned default `exec()` locals behavior with that model; do not rely on assignments made by `exec()` with implicit function locals to mutate optimized local variables. Pass explicit globals/locals mappings when you need predictable, inspectable namespace behavior. Successful parsing/compilation does not imply safe execution. Use explicit namespaces for legitimate trusted code, but namespaces are not a sandbox. AST structures evolve: for example, `ast.Constant` replaced older literal node classes in Python 3.8, type-parameter nodes were added in 3.12, and template-string AST support was added in 3.14. Feature-detect or test against each supported interpreter instead of assuming one tree shape.

### D-Q31 — Reference implementation

```python
import ast
import math

class ExpressionRejected(ValueError):
    pass

class ArithmeticEvaluator:
    MAX_CHARS = 256
    MAX_NODES = 64
    MAX_DEPTH = 12
    MAX_ABS = 10**12
    MAX_EXPONENT = 8

    def evaluate(self, source: str) -> int | float:
        if not isinstance(source, str) or len(source) > self.MAX_CHARS:
            raise ExpressionRejected("expression must be text no longer than 256 characters")
        try:
            tree = ast.parse(source, mode="eval")
            nodes = list(ast.walk(tree))
            if len(nodes) > self.MAX_NODES:
                raise ExpressionRejected("expression has too many AST nodes")
            if self._depth(tree) > self.MAX_DEPTH:
                raise ExpressionRejected("expression is nested too deeply")
        except SyntaxError as exc:
            raise ExpressionRejected("invalid expression syntax") from exc
        except RecursionError as exc:
            raise ExpressionRejected("expression exceeds parser or traversal depth limits") from exc
        value = self._eval(tree.body)
        if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > self.MAX_ABS:
            raise ExpressionRejected("result is outside the allowed numeric range")
        return value

    def _depth(self, node: ast.AST) -> int:
        children = list(ast.iter_child_nodes(node))
        return 1 + max((self._depth(child) for child in children), default=0)

    def _eval(self, node: ast.AST) -> int | float:
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if not math.isfinite(node.value) or abs(node.value) > self.MAX_ABS:
                raise ExpressionRejected("numeric literal outside allowed range")
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = self._eval(node.operand)
            result = value if isinstance(node.op, ast.UAdd) else -value
            return self._bounded(result)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
            left, right = self._eval(node.left), self._eval(node.right)
            if isinstance(node.op, ast.Pow):
                if abs(right) > self.MAX_EXPONENT or (left == 0 and right < 0):
                    raise ExpressionRejected("exponent outside allowed range")
                # Bound integer exponentiation before computing; result is checked afterward too.
                if type(left) is int and type(right) is int and right >= 0 and abs(left) > 1 and right > 0:
                    if right * math.log10(abs(left)) > 12:
                        raise ExpressionRejected("power result may be too large")
                result = left ** right
            elif isinstance(node.op, ast.Add): result = left + right
            elif isinstance(node.op, ast.Sub): result = left - right
            elif isinstance(node.op, ast.Mult): result = left * right
            else:
                if right == 0:
                    raise ExpressionRejected("division by zero")
                result = left / right
            return self._bounded(result)
        raise ExpressionRejected(f"unsupported syntax: {type(node).__name__}")

    def _bounded(self, value: int | float) -> int | float:
        if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > self.MAX_ABS:
            raise ExpressionRejected("numeric result outside allowed range")
        return value

calc = ArithmeticEvaluator()
assert calc.evaluate("2 + 3 * 4") == 14
assert calc.evaluate("-(8 / 2)") == -4.0
```

Minimum negative tests:

```python
for bad in ("f(1)", "x + 1", "obj.value", "2 // 1", "1 +", "2 ** 1000", "2 ** (4 + 5)",
            "1" * 300, "True", "999999999999999999999999999999999999999999",
            "0 ** -1", "1 / 0", "(-1.0) ** 0.5",
            "1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1"):
    try:
        calc.evaluate(bad)
    except ExpressionRejected:
        pass
    else:
        raise AssertionError(f"should reject: {bad!r}")
```

This is a bounded teaching interpreter, not a proof of immunity to denial of service. The character/node/depth and numeric limits reduce risk, but parser behavior, recursion, floating-point edge cases, and implementation defects remain concerns. For hostile high-volume inputs, add process-level CPU/memory/time limits and fuzz/property-based tests. Do not add calls, names, attributes, subscripts, or arbitrary objects without a new threat review. Never replace this interpreter with `eval()`. The tests above are expected to raise `ExpressionRejected`; unexpected `RecursionError`, `OverflowError`, or `ZeroDivisionError` escaping the public API should be treated as defects and covered by regression tests.

### D-Q32 — Expected answer

Audit hooks can provide visibility into selected runtime events and help a host log or reject some operations where an applicable event is emitted. They are not a complete policy enforcement layer or a sandbox; coverage and event arguments vary, and hostile code already in-process can exploit many capabilities not adequately constrained by an audit hook. For arbitrary user code, use a separate low-privilege process/container or stronger OS-level isolation with restricted filesystem/network access, CPU/memory/process limits, timeouts, and disposable state. Keep secrets and credentials out of the execution environment.

### D-Q33 — Expected answer

- Configuration: prefer JSON or TOML with schema validation; TOML parsing is available as `tomllib` in Python 3.11+.
- Python-like literal values: `ast.literal_eval()` accepts supported literal/container forms, not arbitrary operators, names, or function calls. It avoids arbitrary code execution but can still consume excessive memory/CPU/stack on pathological input; enforce input/resource limits.
- User-selectable operation: a fixed dispatch table mapping names to known callables.
- Arbitrary `eval()`: do not use for untrusted input. Emptying `__builtins__` does not establish a secure sandbox.
- Adjacent review flags: `pickle.loads()` on untrusted bytes can execute code during deserialization; for YAML use a safe loader for untrusted documents; avoid `subprocess(..., shell=True)` with user-controlled strings and prefer an argument list with `shell=False`. Review template/notebook/code-generation pipelines as execution boundaries, not merely text processing.

### D-Q34 — Reference implementation: a tiny query-expression DSL

This complete example constructs an expression tree, validates fields/operators/types, renders a readable explanation, and compiles values to placeholders. It does **not** execute a database query.

```python
from dataclasses import dataclass
from typing import Any

SCHEMA: dict[str, type] = {"age": int, "score": int, "name": str}
SQL_NAMES = {"age": "age", "score": "score", "name": "name"}  # trusted identifiers

class QueryError(ValueError):
    pass

class Expr:
    def __and__(self, other: object) -> "Expr":
        if not isinstance(other, Expr):
            raise TypeError("right operand of '&' must be a query expression")
        return Logical("AND", self, other)

    def __or__(self, other: object) -> "Expr":
        if not isinstance(other, Expr):
            raise TypeError("right operand of '|' must be a query expression")
        return Logical("OR", self, other)

    def __bool__(self) -> bool:
        raise TypeError("query expressions cannot be used with 'and'/'or'; use '&'/'|'")

    def explain(self) -> str:
        raise NotImplementedError

    def compile(self) -> tuple[str, list[object]]:
        raise NotImplementedError

@dataclass(frozen=True)
class Column(Expr):
    name: str

    def __post_init__(self) -> None:
        if self.name not in SCHEMA or self.name not in SQL_NAMES:
            raise QueryError(f"unknown field: {self.name!r}")

    def explain(self) -> str:
        return f"Column({self.name!r})"

@dataclass(frozen=True)
class Compare(Expr):
    column: Column
    operator: str
    value: object

    def __post_init__(self) -> None:
        if not isinstance(self.column, Column):
            raise QueryError("comparison requires a validated Column node")
        if self.operator not in {"=", "!=", "<", "<=", ">", ">="}:
            raise QueryError(f"unsupported operator: {self.operator!r}")
        expected = SCHEMA[self.column.name]
        if type(self.value) is not expected:
            raise QueryError(f"field {self.column.name!r} expects {expected.__name__}, got {type(self.value).__name__}")

    def explain(self) -> str:
        return f"Compare({self.column.name} {self.operator} {self.value!r})"

    def compile(self) -> tuple[str, list[object]]:
        return f"{SQL_NAMES[self.column.name]} {self.operator} ?", [self.value]

@dataclass(frozen=True)
class Logical(Expr):
    operator: str
    left: Expr
    right: Expr

    def __post_init__(self) -> None:
        if self.operator not in {"AND", "OR"}:
            raise QueryError(f"unsupported logical operator: {self.operator!r}")
        if not isinstance(self.left, (Compare, Logical)) or not isinstance(self.right, (Compare, Logical)):
            raise QueryError("logical operands must be supported expression nodes")

    def explain(self) -> str:
        return f"{self.operator}({self.left.explain()}, {self.right.explain()})"

    def compile(self) -> tuple[str, list[object]]:
        left_sql, left_params = self.left.compile()
        right_sql, right_params = self.right.compile()
        return f"({left_sql} {self.operator} {right_sql})", [*left_params, *right_params]

class ColumnFactory:
    def __init__(self, name: str) -> None:
        if name not in SCHEMA:
            raise QueryError(f"unknown field: {name!r}")
        self.name = name

    def _compare(self, op: str, value: object) -> Compare:
        return Compare(Column(self.name), op, value)

    def __eq__(self, value: object) -> Compare:  # DSL equality, not Python identity
        return self._compare("=", value)

    def __ne__(self, value: object) -> Compare:
        return self._compare("!=", value)

    def __lt__(self, value: object) -> Compare:
        return self._compare("<", value)

    def __le__(self, value: object) -> Compare:
        return self._compare("<=", value)

    def __gt__(self, value: object) -> Compare:
        return self._compare(">", value)

    def __ge__(self, value: object) -> Compare:
        return self._compare(">=", value)

def col(name: str) -> ColumnFactory:
    return ColumnFactory(name)

condition = (col("age") > 18) & (col("name") != "O'Reilly")
sql, params = condition.compile()
assert sql == "(age > ? AND name != ?)"
assert params == [18, "O'Reilly"]
expected_name_repr = repr("O'Reilly")
assert condition.explain() == f"AND(Compare(age > 18), Compare(name != {expected_name_repr}))"

for bad in (lambda: col("password"), lambda: col("age") > True,
            lambda: Compare(Column("age"), "LIKE", 1),
            lambda: Logical("AND", col("age") > 18, object()),
            lambda: (col("age") > 18) & object(),
            lambda: bool(col("age") > 18)):
    try:
        bad()
    except (QueryError, TypeError):
        pass
    else:
        raise AssertionError("invalid DSL input should be rejected")
```

The SQL values are always parameters; the field name is selected from a fixed schema-to-SQL mapping. Do not bind identifiers as values and do not accept arbitrary user strings as SQL fragments. `ColumnFactory` is deliberately small; in a larger library, `Generic`, `overload`, stubs, and type-checker-visible schema declarations can improve static feedback. `dataclass_transform` can describe dataclass-like generated fields to supporting type checkers, but none of these mechanisms replaces runtime validation. `&` and `|` call overloadable methods and construct nodes; `and` and `or` request truth-value conversion and short-circuit, so `Expr.__bool__` raises a diagnostic instead of silently evaluating the expression. Parentheses are important because Python's bitwise operator precedence differs from comparison chaining; write `(col("age") > 18) & (col("score") >= 50)`.

### D-Q35 — Reference architecture

- Signature validation: plain helper using `inspect.signature().bind()`.
- Sync/async function validation: a decorator factory with separate sync/async wrappers, `functools.wraps`, and tests.
- Declarative fields: descriptors with `__set_name__()` for per-field metadata.
- Schema collection: `__init_subclass__()` unless class namespace preparation or deeper class-construction control is required.
- Safe filter expression: explicit parser/AST allow-list interpreter with node, depth, value, and operation limits; never `eval()`.
- Mutable defaults/print/bare-except lint: `ast.NodeVisitor`; static analysis only, with documented limitations. Use LibCST rather than AST when a codemod must preserve comments and formatting.
- Metaclass: only if lower-level hooks cannot express the requirement; do not introduce one just for a registry.
- Static typing for declarative fields: provide stubs or a type-checker-visible protocol where practical; use `dataclass_transform` when a decorator/base/metaclass intentionally provides dataclass-like semantics. These tools inform static analysis; they do not validate untrusted runtime values.

For the library case study, one acceptable example is Pydantic: a class declaration with annotated fields is collected into model metadata, then runtime validation/construction uses that metadata to parse or reject supplied values. Compare that declarative contract with a plain validation function: the model improves reuse, introspection, and schema generation, but adds framework conventions and runtime cost. Verify the exact behavior against the library version under study rather than assuming every annotation is enforced identically.

Acceptance tests should cover happy paths, invalid types/fields/operators, missing attributes, nested definitions, sync and async exceptions, signature metadata, duplicate registry names, expression attacks (calls/attributes/names/large exponent), SQL parameter separation, and type checking. ≥90% branch coverage is a project target, not proof of security or correctness. Add a `DESIGN.md` recording the simplest-tool decision and the assumptions/limits of each mechanism.

## Security question answers (V01–V06)

### V01 — `eval(user_text)`

**Vulnerability:** arbitrary expression evaluation can access capabilities available to the process and may perform code execution, data disclosure, or denial of service. **Safer alternative:** parse a deliberately small arithmetic grammar and interpret only explicitly allowed AST nodes/operators, with input, depth, node, and numeric limits; or use a purpose-built parser. Do not use `literal_eval()` for arithmetic because operators are outside its intended literal grammar.

### V02 — Empty built-ins

Setting `{"__builtins__": {}}` removes a name mapping, not the Python object model or every route to capabilities. It is not a secure sandbox and must not be treated as one. Use a non-executing format/interpreter for constrained input; for arbitrary code, use OS/process isolation and resource limits, not an in-process namespace trick.

### V03 — `exec(source, globals)`

**Vulnerability:** untrusted source is executed in the API process. An explicit globals dictionary is a namespace choice, not isolation. The `record` object may expose capabilities through its attributes and methods. Prefer structured rule data interpreted by allow-listed code. If arbitrary code is a hard requirement, execute it in a disposable, low-privilege isolated worker with strict limits and no application secrets.

### V04 — `getattr(obj, field)`

**Vulnerability:** untrusted field names can expose internal attributes or invoke properties with side effects. Use a schema-defined mapping from public field names to approved accessors; validate before access. Do not rely only on blocking names beginning with `_`, because public properties may still have side effects or disclose sensitive data.

### V05 — Prefix-based method lookup

**Vulnerability:** `handle_` prefixing is not authorization or a strict allow-list; any matching attribute can be exposed, inherited, or added later. Use `routes = {"created": service.handle_created, "deleted": service.handle_deleted}` and look up only exact keys. Apply authorization checks separately, and avoid invoking methods based solely on a user-provided string.

### V06 — LLM-generated code

Treat generated code as untrusted even if the model was instructed to be safe. Risks include prompt injection, unsafe imports/calls, data exfiltration, filesystem/network access, secret leakage, dependency confusion, and resource exhaustion. Safer layers: prefer structured tool calls or a constrained DSL; review/validate generated artifacts; run tests/static analysis; execute only in a disposable isolated worker with least privilege, no secrets, restricted network/filesystem, quotas, timeouts, and monitoring; record provenance; require approval for consequential actions. Prompting and empty built-ins are not security controls.

# Part III — Coverage Matrix

| ID | Lesson(s) | Topic | Difficulty | Assessment type |
|---|---|---|---|---|
| Q01 | 01 | Signature binding and invocation | Intermediate | Implementation/test |
| Q02 | 01 | `dir`/`vars`/static lookup | Basic–Intermediate | Concept/code reading |
| Q03 | 02 | Dynamic config wrapper | Intermediate | Implementation |
| Q04 | 02 | `__getattr__` recursion | Intermediate | Debugging |
| Q05 | 02 | `hasattr` and descriptor errors | Intermediate | Reasoning |
| Q06 | 02 | Allow-listed dispatch | Intermediate | Correction/security |
| Q07 | 01 | Limits of `Signature.bind` | Basic | Short answer |
| Q08 | 01 | Side effects, annotation resolution, dependency injection | Advanced | Architecture |
| Q09 | 03 | Retry decorator | Intermediate | Implementation/test |
| Q10 | 03 | Sync/async timing | Advanced | Implementation/test |
| Q11 | 03 | Once/cache/thread safety | Advanced | Implementation/architecture |
| Q12 | 03 | Descriptor binding for class decorator | Advanced | Debugging |
| Q13 | 03 | Metadata and static typing | Intermediate | Code review |
| Q14 | 04 | `@auto_repr` | Intermediate | Implementation/test |
| Q15 | 04 | Post-init assignment policy | Advanced | Implementation/edge cases |
| Q16 | 04 | Class decorator vs factory | Intermediate | Trade-off |
| Q17 | 03 | Async decorator tests | Advanced | Test design |
| Q18 | 03 | Stacking and safe observability | Advanced | Code review |
| Q19 | 05 | Subclass registry | Intermediate | Implementation/test |
| Q20 | 06 | Class statement to `type()` | Intermediate | Translation |
| Q21 | 06 | Dynamic class pickling | Advanced | Debugging/reasoning |
| Q22 | 05, 07 | Hook selection | Advanced | Architecture |
| Q23 | 07 | Singleton trade-offs | Advanced | Architecture |
| Q24 | 07 | Metaclass conflict | Advanced | Debugging |
| Q25 | 05–07 | Class creation and descriptor hooks | Advanced | Sequencing |
| Q26 | 06 | `type` vs `types.new_class` | Advanced | Design choice |
| Q27 | 08 | AST lint visitor, tree shape, regex/unparse/CST limits | Advanced | Implementation/test/code analysis |
| Q28 | 08 | AST transformation, CST/codemod and version changes | Advanced | Transformation/semantics |
| Q29 | 08 | Visitor traversal | Intermediate | Debugging |
| Q30 | 08–09 | Parse/compile/execute, tokenize, symtable, versioned AST | Intermediate | Output/explanation |
| Q31 | 08–09 | Bounded AST interpreter | Advanced | Security implementation |
| Q32 | 09 | Audit hooks and isolation | Advanced | Security review |
| Q33 | 09 | Safe parsing alternatives | Intermediate | Security reasoning |
| Q34 | 10 | Typed expression DSL, diagnostics, parameterized SQL | Advanced | Implementation/architecture |
| Q35 | 01–10 | `declkit`, typing, library case study, integration | Advanced | Architecture/test plan/library analysis |
| V01 | 09 | `eval` injection | Intermediate | Vulnerability review |
| V02 | 09 | Empty built-ins misconception | Advanced | Vulnerability review |
| V03 | 09 | `exec` injection | Intermediate | Vulnerability review |
| V04 | 02, 09 | User-controlled attribute access | Intermediate | Vulnerability review |
| V05 | 02 | Prefix dispatch | Advanced | Vulnerability review |
| V06 | 08–10 | LLM-generated code | Advanced | Security architecture |

## Phase distribution

| Phase | Core question IDs | Count | Main coverage |
|---|---|---:|---|
| A — Looking Inside Objects | Q01–Q08 | 8 | Lessons 01–02 |
| B — Wrapping and Generating Behaviour | Q09–Q18 | 10 | Lessons 03–04 |
| C — Hooking Class Creation | Q19–Q26 | 8 | Lessons 05–07 |
| D — Code as Data | Q27–Q35 | 9 | Lessons 08–10 |
| **Total core** | **Q01–Q35** | **35** | **All ten lessons** |
| Separate vulnerability set | V01–V06 | 6 | Primarily Lessons 02, 08–10 |

# Part IV — Scoring Rubric

Score each core question from **0–4** (maximum 140), and each vulnerability question from **0–3** (maximum 18), for a total of **158 points**.

## Core-question scoring (0–4)

- **4 — Production-ready:** technically correct; explicit assumptions; appropriate error behavior; meaningful edge/negative tests; security and compatibility considered where relevant.
- **3 — Correct with minor gaps:** core behavior works; one non-critical edge case, explanation, or test is missing.
- **2 — Partially correct:** basic idea is sound but implementation has material gaps, weak validation, or incomplete tests.
- **1 — Minimal:** recognizes the topic but solution is substantially incorrect or not operational.
- **0 — Missing/unsafe:** no answer, fundamentally incorrect reasoning, or dangerous implementation without recognizing the risk.

## Vulnerability-question scoring (0–3)

- **3:** identifies the vulnerability, realistic impact, and threat-model-appropriate mitigation; explicitly rejects the false security premise.
- **2:** identifies the issue and a plausible mitigation but misses an important risk or assumption.
- **1:** vague warning without a practical fix.
- **0:** claims the code is safe without defensible evidence or proposes an equally unsafe substitute.

## Cross-cutting dimensions

For each implementation, assess conceptual accuracy, implementation correctness, edge-case handling, test quality, security awareness, and engineering judgment. A passing score cannot compensate for a critical security misconception: treat claims that empty built-ins sandbox arbitrary Python or that `eval` is appropriate for untrusted input as mandatory remediation regardless of total score.

Suggested interpretation (guidance, not a certification):

- **142–158:** strong command; verify all security-critical items individually.
- **120–141:** solid foundation; target advanced edge cases and architecture choices.
- **95–119:** developing; revisit implementation and testing discipline.
- **Below 95:** revisit the module sequentially and redo the missed questions.

# Part V — Competency Checklist and Remediation Map

Mark each item only after you can explain it and solve its linked questions without looking at the answer key.

| Competency | Evidence questions | If missed, revisit |
|---|---|---|
| Inspect objects and bind calls safely | Q01, Q02, Q07, Q08 | Lesson 01: signatures, static lookup, annotations, side effects |
| Implement dynamic access without recursion | Q03–Q06, V04–V05 | Lesson 02: `__getattr__`, `__setattr__`, `hasattr`, dispatch allow-lists |
| Build correct sync/async decorators | Q09–Q13, Q17–Q18 | Lesson 03: factories, `wraps`, descriptor binding, `ParamSpec`, async behavior |
| Modify or generate classes deliberately | Q14–Q16 | Lesson 04: class decorators/factories, identity, pickling, mutation policy |
| Register subclasses and cooperate with hooks | Q19, Q22, Q25 | Lesson 05: `__init_subclass__`, cooperative `super()`, registry isolation |
| Create runtime classes correctly | Q20–Q21, Q26 | Lesson 06: `type`, `types.new_class`, namespace, importability/pickle |
| Understand metaclasses and conflicts | Q22–Q25 | Lesson 07: metaclass selection, MRO, class lifecycle, simplest-tool ladder |
| Inspect and transform ASTs correctly | Q27–Q30 | Lesson 08: node traversal, locations, compilation, semantic assumptions |
| Design a safe expression evaluator | Q31–Q33, V01–V03 | Lesson 09: AST allow-list, bounds, no in-process hostile-code sandbox, audit-hook limits |
| Design declarative expressions and SQL safely | Q34–Q35 | Lesson 10: expression nodes, `&`/`|`, validation, parameterized SQL, diagnostics |
| Treat generated code as untrusted | Q31–Q33, V01–V06 | Lessons 08–10: source vs data, isolation, least privilege, LLM threat model |

## Final self-assessment

- [ ] I can inspect an unknown function with `inspect.signature()` and validate arguments using `bind()` without invoking it prematurely.
- [ ] I can explain `dir`, `vars`, `getattr`, and `getattr_static`, including descriptor side effects.
- [ ] I can implement dynamic access with correct `AttributeError` behavior and an explicit allow-list.
- [ ] I can implement/test retry, timing, once, and sync/async decorator behavior without hiding exceptions.
- [ ] I understand descriptor binding for class-based decorators and can preserve metadata/signature information.
- [ ] I can explain class decorator versus factory trade-offs.
- [ ] I can use `__set_name__`/`__init_subclass__` for declarative fields and registries before reaching for a metaclass.
- [ ] I can create a simple runtime class with `type()` and explain `types.new_class()` and pickle constraints.
- [ ] I can diagnose metaclass conflicts and explain class-creation order.
- [ ] I can write an AST visitor that traverses nested definitions and a conservative transformer with source locations repaired.
- [ ] I can distinguish parsing, transformation, compilation, and execution.
- [ ] I never treat empty `__builtins__`, an audit hook, or an in-process namespace as a secure sandbox for hostile Python.
- [ ] I can choose JSON/TOML, `literal_eval`, dispatch tables, or a constrained interpreter according to the input grammar.
- [ ] I can design a bounded AST interpreter and state its remaining resource-exhaustion risks.
- [ ] I can construct a mini-DSL expression tree, explain `&`/`|` versus `and`/`or`, and compile SQL using placeholders plus validated identifiers.
- [ ] I can explain when ordinary functions are simpler and document the trade-offs of dynamic APIs.
- [ ] I completed the `declkit` mini-project with adversarial tests, ≥90% branch coverage target, type checking, and a `DESIGN.md`.

**Completion criterion:** all six vulnerability questions must be answered safely, and every core question scored 0–1 should be retried after reviewing the linked lesson. High total score does not override an unsafe security conclusion.
