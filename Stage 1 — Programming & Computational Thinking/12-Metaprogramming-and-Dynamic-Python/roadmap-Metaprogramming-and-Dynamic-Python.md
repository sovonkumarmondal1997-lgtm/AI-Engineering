# Roadmap — Module 1.12: Metaprogramming and Dynamic Python

This is the learning roadmap for the twelfth module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
about Python's dynamic features, **in what order**, **how** to practise
each topic, and **how to prove to yourself** that you have learned it.

Metaprogramming is code that inspects, generates or modifies other code.
It is how `dataclasses` writes `__init__` for you, how Pydantic and
SQLAlchemy turn class bodies into schemas, how `pytest` rewrites asserts,
how FastAPI reads your type hints to build routes, how `typing.NamedTuple`
works, and how plugin systems discover subclasses. You will rarely write a
metaclass in application code — but you will **read** this kind of code
constantly, and knowing the mechanism removes the magic.

> **Rule of this module:** reach for the simplest tool first. The order of
> preference is: plain code → decorators → class decorators →
> `__init_subclass__` → descriptors → metaclasses → AST/`exec`. Each lesson
> says when a heavier tool is *not* justified.

> Target version: **Python 3.12+**. Notes on 3.13/3.14 are flagged inline.

---

## 1. Module outcome

By the end of this module you will be able to:

- Inspect live objects, signatures, source and annotations with `inspect`,
  `dir`, `vars`, `getattr_static` and `typing.get_type_hints`.
- Use `getattr`, `setattr`, `hasattr`, `__getattr__`, `__setattr__` and
  `__getattribute__` safely, without infinite recursion.
- Write decorators with arguments, class-based decorators and
  signature-preserving wrappers that work on sync and async functions.
- Use class decorators and class factories to generate behaviour.
- Use `__init_subclass__` and `__set_name__` to build registries and
  validated class definitions.
- Create classes at runtime with `type()` and `types.new_class`.
- Explain what a metaclass is, write a small one, and decide when *not* to.
- Parse, inspect and transform code with the `ast` module and compile it.
- Explain the risks of `eval`/`exec` and use safe alternatives
  (`ast.literal_eval`, dispatch tables, parsers).
- Design a small declarative API / mini-DSL on top of these tools.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Functions are first-class; closures | Module 1.24 (01, 03) | Decorators are closures |
| Decorators (basic) | Module 1.9 (02) | Lesson 03 extends them |
| `functools.partial`, `cache`, `wraps` | Module 1.9 (09) | Wrapper metadata |
| Descriptors, attribute lookup, MRO | Module 1.11 (05, 06, 08) | Metaclasses and `__getattr__` build on them |
| Python object model | Module 1.9 (10) | Everything is an object, including classes |
| Type hints | Module 1.6 (06), 1.9 (05) | Introspection of annotations |
| Testing with pytest | Module 1.7 | Metaprogramming needs strong tests |

**Tools:** Python 3.12+, `pytest`, `ruff`, `mypy`/`pyright`, and a debugger.
Use `python -m dis`, `ast.dump(..., indent=2)` and `inspect.getsource`
liberally to *see* what happens.

---

## 3. How the module is organised

```text
Phase A — Looking Inside Objects                  (Basics)
  01 introspection with inspect and dir
  02 getattr, setattr and dynamic attribute access
Phase B — Wrapping and Generating Behaviour       (Intermediate)
  03 parametrized and class-based decorators
  04 class decorators and class factories
Phase C — Hooking Class Creation                  (Advanced)
  05 __init_subclass__ and subclass registries
  06 type() and dynamic class creation
  07 metaclasses
Phase D — Code as Data                            (Advanced)
  08 ast and code generation basics
  09 eval, exec and their risks
  10 declarative APIs and mini-DSLs
```

Pace: about 3–4 weeks part-time. Each lesson ends with a small tested
exercise; the module ends with a mini-project.

---

## Lesson 01 — `01-introspection-with-inspect-and-dir.md`

**Why it matters.** Debuggers, REPLs, documentation generators, test
frameworks, dependency-injection containers and serialisation libraries all
start by *looking at* objects. Introspection is also how you explore an
unfamiliar library quickly.

### Basic — what to learn

- `type(x)`, `isinstance`, `issubclass`, `id`, `callable`.
- `dir(obj)` (names, including inherited) vs `vars(obj)` / `obj.__dict__`
  (the instance's own namespace).
- `help(obj)`, `obj.__doc__`, `obj.__name__`, `obj.__module__`, `obj.__qualname__`.
- Everything is an object: functions have `__code__`, `__defaults__`,
  `__annotations__`; classes have `__mro__`, `__bases__`, `__subclasses__()`.

```python
def greet(name: str, punct: str = "!") -> str:
    """Say hello."""
    return f"Hello {name}{punct}"

print(greet.__name__, greet.__defaults__, greet.__annotations__)
print(greet.__code__.co_varnames, greet.__code__.co_argcount)
```

### Intermediate — what to learn

- `inspect.signature(fn)` → `Signature` with `Parameter` kinds
  (`POSITIONAL_ONLY`, `POSITIONAL_OR_KEYWORD`, `VAR_POSITIONAL`,
  `KEYWORD_ONLY`, `VAR_KEYWORD`), defaults and annotations;
  `sig.bind(*args, **kwargs)` to validate a call.
- `inspect.getmembers(obj, predicate)`, `isfunction`, `ismethod`, `isclass`,
  `iscoroutinefunction`, `isgeneratorfunction`.
- `inspect.getsource`, `getsourcefile`, `getdoc`, `cleandoc`.
- `typing.get_type_hints()` resolves string annotations and forward
  references; why `__annotations__` alone is not enough.
- Stack inspection: `inspect.stack()`, `currentframe()`, `frame.f_locals` —
  and why it is slow and fragile.

```python
import inspect

def call_with_validation(fn, **kwargs):
    sig = inspect.signature(fn)
    bound = sig.bind(**kwargs)          # raises TypeError on bad call
    bound.apply_defaults()
    return fn(*bound.args, **bound.kwargs)
```

### Advanced — what to learn

- Annotation evaluation changes: `from __future__ import annotations`,
  and **deferred evaluation of annotations in 3.14** (PEP 649/749) with
  `annotationlib.get_annotations()`; consequences for libraries that read
  annotations (Pydantic, FastAPI, dataclasses).
- `inspect.getattr_static` to look up attributes **without** triggering
  descriptors or `__getattr__`.
- Code objects: `co_code`, `co_consts`, `co_names`, `co_flags` (generator,
  coroutine, varargs flags); building decorators that behave differently for
  async functions.
- `sys._getframe`, `traceback`, `warnings` stack-level for library authors.
- Building a mini dependency-injection container from `signature()` and
  type hints (resolve constructor parameters by annotation).
- Safe introspection of untrusted objects (descriptors and properties can run code).

### Common mistakes

- Using `dir()` output as a stable API.
- Calling `getattr` on a property that performs I/O during introspection.
- Reading `__annotations__` directly instead of `get_type_hints`/`get_annotations`.

### Self-check

1. Difference between `dir(x)` and `vars(x)`?
2. How does `Signature.bind` differ from just calling the function?
3. Why can `getattr_static` return something different from `getattr`?

---

## Lesson 02 — `02-getattr-setattr-and-dynamic-attribute-access.md`

**Why it matters.** Dynamic attribute access powers ORM models, API client
wrappers (`client.users.list()`), config objects, mocks (`MagicMock`),
proxies and lazy loaders. It is also a common source of recursion bugs and
silent typos.

### Basic — what to learn

- Built-ins: `getattr(obj, name[, default])`, `setattr`, `hasattr`, `delattr`.
- Use cases: reading a field named in a config, dispatching to
  `handle_<event>` methods, iterating over attribute names.
- `hasattr` calls `getattr` — it hides *any* `AttributeError`, including bugs.

```python
class Handler:
    def handle_created(self, e): return f"created {e}"
    def handle_deleted(self, e): return f"deleted {e}"
    def dispatch(self, kind, e):
        method = getattr(self, f"handle_{kind}", None)
        if method is None:
            raise ValueError(f"unknown event {kind!r}")
        return method(e)
```

### Intermediate — what to learn

- `__getattr__(self, name)`: called **only** when normal lookup fails;
  raise `AttributeError` for unknown names (so `hasattr` and `copy` work).
- `__setattr__(self, name, value)`: called on **every** assignment; use
  `super().__setattr__` or `object.__setattr__` to avoid recursion.
- `__delattr__`, and `__dir__` to expose dynamic names to `dir()` and
  autocompletion.
- Building an attribute-style dictionary wrapper (`cfg.db.host`) and its
  pitfalls with key names that clash with methods.
- Dispatch tables (`dict[str, Callable]`) as the explicit alternative to
  string-built `getattr`.

```python
class Config:
    def __init__(self, data: dict) -> None:
        object.__setattr__(self, "_data", data)

    def __getattr__(self, name: str):
        try:
            value = self._data[name]
        except KeyError:
            raise AttributeError(name) from None
        return Config(value) if isinstance(value, dict) else value

    def __setattr__(self, name, value):
        raise AttributeError("Config is read-only")
```

### Advanced — what to learn

- `__getattribute__` runs on *every* access; overriding it is the sharpest
  tool: always delegate to `object.__getattribute__`.
- Proxy / delegation objects: forwarding attributes and dunder methods
  (dunder methods are looked up on the **type**, so `__getattr__` does not
  forward `len(proxy)` or `proxy + 1`).
- Lazy attributes and lazy modules (`module.__getattr__`, PEP 562) for
  deprecations and lazy imports.
- Interaction with `copy`, `pickle` and `hasattr` when `__getattr__` is too
  permissive (the infinite recursion on `__setstate__` / `__deepcopy__` lookup).
- Typing dynamic attribute access: `__getattr__` return annotations, `Protocol`,
  `typing.TYPE_CHECKING` stubs, and `Literal` keys.
- Performance: dynamic lookup defeats the specialising interpreter; keep it off hot paths.
- Security: user-controlled attribute names (`getattr(obj, request.args["f"])`)
  expose internals (`__class__`, `__globals__`); allow-list names.

### Common mistakes

- `__getattr__` that returns `None` for everything (hides typos).
- Recursion by reading `self._data` in `__getattr__` before `_data` exists.
- Forgetting dunder lookup happens on the type.

### Self-check

1. When is `__getattr__` called and when is `__getattribute__` called?
2. Why does `len(proxy)` fail even though `proxy.__getattr__` handles `__len__`?
3. How do you make a class "write-once" using `__setattr__`?

---

## Lesson 03 — `03-parametrized-and-class-based-decorators.md`

**Why it matters.** Retry, rate-limit, cache, authorise, time, trace,
register and validate — production code is full of decorators with
parameters. Writing them correctly (metadata, async, typing) is a core
senior skill. Basic decorators were introduced in Module 1.9; this lesson
makes them production-grade.

### Basic — what to learn

- Recap: a decorator is a callable taking a function and returning a callable.
- **Decorator factories** (three nested levels): `@retry(times=3)`.
- `functools.wraps` to preserve `__name__`, `__doc__`, `__wrapped__`, signature.

```python
import functools, time

def retry(times: int = 3, delay: float = 0.1, exceptions=(Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    time.sleep(delay * attempt)
        return wrapper
    return decorator
```

### Intermediate — what to learn

- Supporting both `@deco` and `@deco(arg=...)` forms (optional-argument decorators).
- **Class-based decorators** with `__init__` (receives the function) and
  `__call__`; keeping state (call counts, caches) and using
  `functools.update_wrapper(self, fn)`.
- Decorating **methods**: class-based decorators need `__get__` to bind
  correctly; function-based wrappers work automatically.
- Stacking decorators and **order of application** (bottom-up).
- Async-aware decorators: detect with `inspect.iscoroutinefunction` and
  return an `async def` wrapper.
- Registering decorators (return the original function) vs wrapping decorators.

```python
class CountCalls:
    def __init__(self, fn):
        functools.update_wrapper(self, fn)
        self.fn, self.calls = fn, 0
    def __call__(self, *a, **k):
        self.calls += 1
        return self.fn(*a, **k)
    def __get__(self, obj, objtype=None):       # makes it work on methods
        return functools.partial(self.__call__, obj) if obj else self
```

### Advanced — what to learn

- Typing decorators with `ParamSpec` and `TypeVar` so the wrapped
  signature is preserved for type checkers; `Concatenate` for decorators
  that inject a first argument; typing class-based decorators.
- Decorating generators, context managers (`contextlib.contextmanager`) and
  coroutines correctly (the wrapper of a generator function is not a generator
  unless you write one).
- Thread-safety and re-entrancy of stateful decorators.
- Cache invalidation design; interaction with `functools.cache` and unhashable args.
- Observability decorators: timing with `time.perf_counter`, structured logging,
  OpenTelemetry-style spans; avoid logging secrets in arguments.
- Testing decorators: assert on behaviour **and** metadata; test with sync,
  async and method targets.
- Decorators that modify signatures (`__signature__`) for framework use (FastAPI-style).
- When *not* to use a decorator: hidden control flow, hard-to-debug stacks — prefer explicit composition.

### Common mistakes

- Forgetting `@wraps` (breaks introspection, pytest fixtures, FastAPI).
- Swallowing exceptions or return values.
- Using mutable default state shared across all decorated functions.

### Self-check

1. In `@retry(times=3)`, how many nested functions exist and what does each receive?
2. Why do class-based decorators need `__get__` to decorate methods?
3. Write a decorator that works on both `def` and `async def` functions.

---

## Lesson 04 — `04-class-decorators-and-class-factories.md`

**Why it matters.** `@dataclass`, `@total_ordering`, `@runtime_checkable`
and `@final` are class decorators. They are the lightest way to *add or
rewrite* behaviour on a class without inheritance or metaclasses.

### Basic — what to learn

- A class decorator receives a class and returns a class (usually the same,
  modified).
- Adding attributes/methods: `cls.method = fn`, `setattr(cls, name, value)`.
- Registering classes in a dict (plugin registration).

```python
REGISTRY: dict[str, type] = {}

def register(name: str):
    def deco(cls):
        REGISTRY[name] = cls
        return cls
    return deco

@register("csv")
class CsvReader: ...
```

### Intermediate — what to learn

- Adding methods generated from class annotations (a mini-`dataclass`):
  read `cls.__annotations__`, build `__init__`/`__repr__`/`__eq__`.
- Wrapping every method of a class (e.g. logging, tracing), skipping
  dunder, static and class methods properly.
- **Class factories**: a function that builds and returns a new class,
  often with closures capturing parameters (`make_validator(min, max)`).
- `functools.total_ordering` as a worked example: read its source.
- `typing.final`, `@runtime_checkable` — decorators that mostly *mark* classes.

```python
def auto_repr(cls):
    fields = list(cls.__annotations__)
    def __repr__(self):
        body = ", ".join(f"{f}={getattr(self, f)!r}" for f in fields)
        return f"{type(self).__name__}({body})"
    cls.__repr__ = __repr__
    return cls

@auto_repr
class Point:
    x: int
    y: int
    def __init__(self, x, y): self.x, self.y = x, y
```

### Advanced — what to learn

- Using `exec` / `types.FunctionType` / `ast` safely to generate fast `__init__`
  methods — what `dataclasses` does and why (avoids per-call overhead).
- Returning a **new class** from a decorator (as `dataclass(slots=True)` does) and the
  consequences: `super()` zero-arg breakage (`__class__` cell), identity differences, pickling.
- Class decorators vs `__init_subclass__` vs metaclass: a decision table —
  decorator for opt-in per class, `__init_subclass__` for every subclass,
  metaclass for control over class *creation* itself.
- Stacking class decorators and interaction with `dataclass`.
- Idempotency (applying twice) and detection of already-decorated classes.
- Typing: decorators that add attributes are invisible to type checkers —
  `dataclass_transform` (PEP 681) for libraries that behave like dataclasses.

### Common mistakes

- Forgetting to return the class (it becomes `None`).
- Wrapping dunder/static methods the wrong way.
- Expecting type checkers to see injected attributes.

### Self-check

1. What does a class decorator receive and return?
2. Why can `dataclass(slots=True)` break zero-argument `super()` in methods in some situations?
3. Implement `@frozen_after_init`, which blocks attribute assignment after `__init__`.

---

## Lesson 05 — `05-init-subclass-and-subclass-registries.md`

**Why it matters.** Plugin systems ("every subclass of `Handler`
automatically registers itself"), validation of subclass contracts, and
declarative frameworks used to need a metaclass. `__init_subclass__`
(Python 3.6+) does most of it with far less machinery.

### Basic — what to learn

- `__init_subclass__(cls, **kwargs)` is a classmethod-like hook called on the
  **parent** whenever a subclass is *defined*.
- Class keyword arguments: `class Csv(Reader, format="csv")`.
- Always call `super().__init_subclass__(**kwargs)`.

```python
class Reader:
    registry: dict[str, type["Reader"]] = {}

    def __init_subclass__(cls, *, format: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if format:
            Reader.registry[format] = cls

class CsvReader(Reader, format="csv"): ...
class JsonReader(Reader, format="json"): ...
print(Reader.registry)
```

### Intermediate — what to learn

- Validating subclasses at definition time (required class attributes,
  abstract-method-like checks, naming conventions) and raising `TypeError`.
- `__set_name__` on attributes inside the class body (the sister hook) to
  record the attribute name and the owner class.
- Registries: keyed by attribute, by name, by entry point; avoiding global
  mutable state problems (tests that import plugins, double registration).
- Walking subclasses: `cls.__subclasses__()` (direct) vs recursive collection;
  weak references and garbage-collected classes.
- Ordering: registration happens at **import time** — importing the module
  is required; the hidden-import trap.

```python
class Plugin:
    required = ("name", "run")
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        missing = [a for a in Plugin.required if not hasattr(cls, a)]
        if missing and not getattr(cls, "__abstract__", False):
            raise TypeError(f"{cls.__name__} missing {missing}")
```

### Advanced — what to learn

- Cooperative `__init_subclass__` in multiple inheritance and mixins.
- Interaction with `abc.ABC` and `typing.Protocol`; with `dataclass` (field
  processing order: `__init_subclass__` runs **before** the `@dataclass`
  decorator on the subclass).
- Deferred/lazy discovery using `importlib.metadata.entry_points` — preview of
  Module 1.18 lesson 04.
- Registry design: namespacing, versioning, conflict detection, and
  thread-safety.
- Class-level configuration through class keywords vs class attributes.
- Testing registries: isolating global state with fixtures that snapshot and restore.
- When a metaclass is *still* needed: customising `__prepare__`,
  `__call__`, or class namespace.

### Common mistakes

- Not calling `super().__init_subclass__`, breaking cooperating mixins.
- Relying on import side effects without documenting them.
- Global registry polluted across tests.

### Self-check

1. When exactly does `__init_subclass__` run?
2. How does it differ from a class decorator applied to each subclass?
3. Build a plugin base class that rejects subclasses without a `name` and registers by name.

---

## Lesson 06 — `06-type-and-dynamic-class-creation.md`

**Why it matters.** `class` is just syntax for calling `type(name, bases,
namespace)`. Understanding that call demystifies metaclasses, `namedtuple`,
`enum.Enum('Color', 'RED GREEN')`, Pydantic's `create_model` and ORM model
factories.

### Basic — what to learn

- `type(obj)` returns the class; `type(name, bases, dict)` **creates** a class.
- Classes are objects; their class is `type` (and `type` is its own type).
- Equivalence between a `class` statement and `type(...)`.

```python
def hello(self): return f"hi from {type(self).__name__}"

Dynamic = type("Dynamic", (object,), {"greet": hello, "x": 1})
print(Dynamic().greet(), Dynamic.__mro__)
```

### Intermediate — what to learn

- What the `class` statement does step by step: evaluate bases → choose
  metaclass → `__prepare__` → execute body in a namespace → call the
  metaclass.
- `types.new_class(name, bases, kwds, exec_body)` — the correct way when
  metaclass and keywords are involved.
- `types.FunctionType`, `types.MethodType`, `types.SimpleNamespace`,
  `types.MappingProxyType` (why `cls.__dict__` is read-only).
- Real factories: `collections.namedtuple`, `typing.NamedTuple`,
  `dataclasses.make_dataclass`, `enum.Enum` functional API,
  `pydantic.create_model` (awareness).
- Building classes from a schema (e.g. one class per database table or JSON schema).

```python
from dataclasses import make_dataclass

Invoice = make_dataclass(
    "Invoice", [("id", int), ("total", float), ("paid", bool, False)]
)
print(Invoice(1, 9.99))
```

### Advanced — what to learn

- Setting `__module__`, `__qualname__` and `__doc__` on generated classes so
  they pickle, repr and document correctly (a generated class defined in a
  function is not importable → pickling fails).
- Generated classes and type checking: dynamic classes are invisible to
  static analysis; provide `.pyi` stubs or `TYPE_CHECKING` declarations.
- Adding methods after creation (`setattr(cls, ...)`) vs at creation;
  patching and its effect on existing instances.
- Class caching/memoisation of generated classes to avoid unbounded class creation (memory leak).
- Security: building classes from untrusted names/schemas.
- Instance `__class__` assignment and its restrictions (`obj.__class__ = Other`).
- Monkeypatching in tests (`monkeypatch.setattr`) and why patching a class
  attribute differs from patching an instance attribute.

### Common mistakes

- Generating classes without `__module__`, breaking pickle.
- Creating a new class on every call (memory growth, `isinstance` failures).
- Expecting IDE autocompletion for dynamic classes.

### Self-check

1. Write the `type(...)` call equivalent to a `class` statement with one method and one attribute.
2. Why is `types.new_class` preferred when a metaclass is involved?
3. Why does pickling a class created inside a function fail?

---

## Lesson 07 — `07-metaclasses.md`

**Why it matters.** A metaclass is the class of a class. It lets you
control class creation (`__new__`, `__init__`, `__prepare__`) and class-level
behaviour (`__call__`, `__getattr__` on the class). Django models, SQLAlchemy
declarative bases, `ABCMeta` and `EnumMeta` rely on them. The advice from
Python core developers: *"If you wonder whether you need one, you don't."*

### Basic — what to learn

- The class statement calls `type(name, bases, ns)`; a metaclass is a
  subclass of `type` that replaces this call.
- `class Foo(metaclass=Meta)`; metaclass is inherited by subclasses.
- A minimal metaclass that reports class creation.

```python
class Meta(type):
    def __new__(mcls, name, bases, ns, **kw):
        print(f"creating {name}")
        return super().__new__(mcls, name, bases, ns, **kw)

class Model(metaclass=Meta): ...
class User(Model): ...          # prints "creating User"
```

### Intermediate — what to learn

- `__new__` (modify the namespace/bases before creation) vs `__init__`
  (modify the class after creation).
- `__prepare__` — return a custom namespace (e.g. an ordered/recording dict
  to detect duplicate definitions, or to track definition order before 3.6).
- `__call__` on a metaclass controls **instantiation** (singleton, instance
  caching, enforcing factory use).
- Collecting declared fields from the class body into `_fields` (the Django
  / ORM pattern) — and compare against a descriptor + `__set_name__` + `__init_subclass__` solution.
- `ABCMeta` and `EnumMeta` as case studies: read their behaviour.

```python
class Singleton(type):
    _instances: dict[type, object] = {}
    def __call__(cls, *a, **k):
        if cls not in Singleton._instances:
            Singleton._instances[cls] = super().__call__(*a, **k)
        return Singleton._instances[cls]

class Settings(metaclass=Singleton): ...
assert Settings() is Settings()
```

### Advanced — what to learn

- **Metaclass conflict**: combining classes with different metaclasses needs a
  common derived metaclass; why `ABC` + framework base can clash.
- Metaclass attribute lookup: methods on a metaclass are available on the
  class but not on instances; `type.__getattribute__` for class-level access.
- Custom `__instancecheck__` / `__subclasscheck__` (as `ABCMeta` does).
- Metaclasses and `__slots__`, `dataclass`, and `Generic` interplay (`Generic`
  used a metaclass before 3.7).
- Alternatives ladder: class decorator → `__init_subclass__` → descriptors →
  metaclass; write the same registry feature four ways and compare lines of
  code, debuggability and type-checker friendliness.
- Debugging metaclass code: `type(cls)`, `cls.__mro__`, `inspect`.
- Singleton alternatives: module-level instance, `functools.cache`d factory,
  dependency injection — the metaclass singleton is rarely right.
- Performance and import-time cost; test isolation.

### Common mistakes

- Using a metaclass when `__init_subclass__` suffices.
- Metaclass conflicts in multiple inheritance.
- Forgetting to call `super().__new__`/`__call__`.

### Self-check

1. What does a metaclass control that `__init_subclass__` cannot?
2. How do you resolve a metaclass conflict between two bases?
3. Re-implement the `Singleton` using a module-level instance and compare trade-offs.

---

## Lesson 08 — `08-ast-and-code-generation-basics.md`

**Why it matters.** The `ast` module exposes Python source as a tree you can
read, check and rewrite. It underpins linters (`ruff` has its own parser but
the concepts are the same), `pytest` assertion rewriting, code formatters,
coverage tools, security scanners (`bandit`), and macro-like transformations.

### Basic — what to learn

- Source → tokens → AST → bytecode (`compile`) → execution (pipeline detail in Module 1.19).
- `ast.parse(source)` → `Module`; `ast.dump(tree, indent=2)` to **look** at it.
- Node types: `Module`, `FunctionDef`, `ClassDef`, `Assign`, `Call`, `Name`,
  `Attribute`, `Constant`, `BinOp`, `If`, `For`, `Return`…

```python
import ast
tree = ast.parse("total = price * (1 + tax)")
print(ast.dump(tree, indent=2))
```

### Intermediate — what to learn

- `ast.NodeVisitor` (read-only traversal) with `visit_<NodeType>` and
  `generic_visit`; `ast.walk`.
- Writing a mini static checker: find calls to `print`, functions without
  docstrings, `except:` bare handlers, mutable default arguments.
- `ast.NodeTransformer` to rewrite code; `ast.fix_missing_locations`.
- `ast.unparse(tree)` (3.9+) to turn an AST back into source.
- `ast.literal_eval` for safe literal parsing.
- `compile(tree, filename, mode)` and `exec` of the compiled result.

```python
class FindMutableDefaults(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        for d in node.args.defaults:
            if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                print(f"{node.name}:{node.lineno} mutable default")
        self.generic_visit(node)

FindMutableDefaults().visit(ast.parse("def f(x=[]): pass"))
```

### Advanced — what to learn

- Rewriting expressions (e.g. constant folding, replacing `assert x == y` with
  a version that records intermediate values — the idea behind pytest's
  assertion rewriting).
- Preserving line numbers/column offsets so tracebacks remain meaningful.
- Code generation: building ASTs by hand vs generating source strings vs
  templates; why `dataclasses` uses `exec` of generated source.
- `symtable` and `tokenize` for scope analysis and comments (the AST drops comments).
- Concrete syntax trees (`libcst`) when you must preserve formatting — codemods.
- AST changes across Python versions (3.8 `Constant`, 3.12 type-parameter nodes,
  3.14 template strings) and writing version-tolerant tools.
- Building a project-specific lint rule or codemod and running it across a repo.
- Security scanners and taint-style analysis (preview of Module 1.22).

### Common mistakes

- Forgetting `generic_visit`, so children are skipped.
- Producing nodes without locations → `compile` errors.
- Using regexes to analyse code that an AST can analyse precisely.

### Self-check

1. What does `ast.dump` of `a.b(c)` look like, node by node?
2. Why can't `ast.unparse` reproduce comments?
3. Write a visitor that reports functions longer than 40 lines.

---

## Lesson 09 — `09-eval-exec-and-their-risks.md`

**Why it matters.** `eval` and `exec` run arbitrary Python from a string. They
are occasionally legitimate (REPLs, notebooks, templating engines, code
generation) and the source of serious vulnerabilities when fed untrusted
input. A senior engineer knows exactly when they are acceptable, and the
safe alternatives.

### Basic — what to learn

- `eval(expr)` evaluates an expression and returns a value; `exec(code)` runs
  statements and returns `None`; `compile` turns text into a code object.
- Globals/locals dictionaries: `eval("x + 1", {"x": 2})`.
- The danger: `eval(user_input)` can call `__import__("os").system(...)`.

```python
print(eval("2 + 3 * 4"))                 # 14
ns = {}
exec("def sq(n): return n * n", ns)
print(ns["sq"](5))                       # 25
```

### Intermediate — what to learn

- **Why restricting `__builtins__` does not make `eval` safe**: attribute
  chains (`().__class__.__mro__[1].__subclasses__()`) bypass it.
- Safe alternatives, in order of preference:
  1. data formats (`json`, `tomllib`),
  2. `ast.literal_eval` for literals only,
  3. dispatch tables / allow-lists of named operations,
  4. a real expression parser (`ast` with an allow-listed node visitor, or
     a library such as `simpleeval`),
  5. a sandboxed subprocess / container with resource limits (Module 1.22).
- Legitimate uses: generating methods in `namedtuple`/`dataclass`, REPL tools,
  `timeit`, templating compile steps — with **trusted** source only.
- `compile` with flags; `exec` with explicit namespace dictionaries to avoid
  polluting module globals.

```python
import ast, operator as op

_OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
        ast.USub: op.neg}

def safe_eval(expr: str) -> float:
    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.operand))
        raise ValueError("unsupported expression")
    return ev(ast.parse(expr, mode="eval").body)
```

### Advanced — what to learn

- Threat modelling for dynamic code: injection via config files, templates,
  notebooks, ML "model cards", serialised objects (links to `pickle`).
- Audit hooks: `sys.addaudithook` events for `exec`, `compile`, `import`,
  `open` — monitoring rather than preventing.
- Resource exhaustion: `eval("9**9**9")`, deeply nested expressions (recursion
  limits), `"a" * 10**10` — time and memory limits.
- Sandboxing options and their limits: `RestrictedPython`, subprocess +
  `resource` limits, containers, WebAssembly; why in-process Python sandboxes
  are considered unsafe.
- Python 3.13+/3.14 changes to `exec`/`eval` namespace semantics (`locals()` semantics, PEP 667) — read before relying on `locals()` writes.
- Code review checklist: flag every `eval`/`exec`/`compile`/`__import__`/`pickle.loads`/`yaml.load`/`subprocess(shell=True)`.
- LLM-generated code execution: why running model output requires the same sandboxing discipline (link to the AI Agents stage).

### Common mistakes

- Believing `eval(s, {"__builtins__": {}})` is safe.
- Using `eval` to parse JSON or numbers (`json.loads`, `float`, `int` exist).
- Using `exec` to avoid writing a dispatch table.

### Self-check

1. Show an input that escapes `eval(x, {"__builtins__": {}})`.
2. Replace an `eval`-based calculator with the AST allow-list version and add tests for abusive inputs.
3. Which of `literal_eval`, `json.loads` and `eval` would you use for a config value, and why?

---

## Lesson 10 — `10-designing-declarative-apis-and-mini-dsls.md`

**Why it matters.** Libraries people love — SQLAlchemy, Pydantic, Django,
FastAPI, pandas, Airflow, `argparse`, `pytest` — expose *declarative* APIs
where you describe **what** you want and the library figures out **how**.
Combining the tools from lessons 01–09 into a coherent, safe, well-typed
API is the capstone of this module.

### Basic — what to learn

- Imperative vs declarative style, shown with the same task both ways.
- Fluent / builder interfaces (method chaining returning `self` or a new
  immutable object).
- Context-manager and decorator based DSLs (`with pipeline():`, `@task`).

```python
class Query:
    def __init__(self, table, filters=(), limit=None):
        self.table, self.filters, self._limit = table, filters, limit
    def where(self, cond: str) -> "Query":
        return Query(self.table, (*self.filters, cond), self._limit)
    def limit(self, n: int) -> "Query":
        return Query(self.table, self.filters, n)
    def sql(self) -> str:
        w = f" WHERE {' AND '.join(self.filters)}" if self.filters else ""
        l = f" LIMIT {self._limit}" if self._limit else ""
        return f"SELECT * FROM {self.table}{w}{l}"
```

### Intermediate — what to learn

- Operator-based DSLs (`col("age") > 18`, `a & b`, `Path / "x"`) returning
  expression objects that are compiled later (the pandas/SQLAlchemy/Polars idea).
- Declarative class bodies with descriptors: fields collected through
  `__set_name__` / `__init_subclass__` into a schema.
- Deferred evaluation: build an expression tree first, then interpret it
  (to SQL, to a pandas call, to a validator) — the **interpreter pattern**.
- Immutability of builders so partial queries can be reused safely.
- Error messages as part of the API: point at the user's line, suggest fixes.

```python
class Expr:
    def __gt__(self, v): return Cmp(self, ">", v)
    def __and__(self, o): return And(self, o)
class Col(Expr):
    def __init__(self, name): self.name = name
    def sql(self): return self.name
class Cmp(Expr):
    def __init__(self, l, op, r): self.l, self.op, self.r = l, op, r
    def sql(self): return f"{self.l.sql()} {self.op} {self.r!r}"
class And(Expr):
    def __init__(self, a, b): self.a, self.b = a, b
    def sql(self): return f"({self.a.sql()} AND {self.b.sql()})"

print(((Col("age") > 18) & (Col("score") > 50)).sql())
```

### Advanced — what to learn

- Typing a DSL: `dataclass_transform`, `Generic`, `overload`, stub files so
  IDEs and type checkers understand dynamic fields.
- Parameterised queries — never splice values into SQL; DSLs must make the
  safe path the default (injection prevention, link to Module 1.22).
- Designing for introspection (`repr` of the expression tree, `explain()`).
- Versioning and evolving a DSL without breaking users (deprecation policy,
  Module 1.20).
- Documentation and discoverability: docstrings, examples as doctests, generated reference.
- Performance: building expression trees is overhead — compile once, reuse.
- The restraint test: would a plain function with keyword arguments be
  clearer? Write both and compare.
- Case-study reading: pick one of `attrs`, `Pydantic`, `SQLAlchemy`'s
  `declarative`, `Typer` or `Click`, and trace how the declaration becomes behaviour.

### Common mistakes

- Overloading operators with surprising meaning (`__and__` returning `bool`).
- Magic that cannot be debugged or typed.
- String-based DSLs with no validation or escaping.

### Self-check

1. Why do `&` and `|` (not `and`/`or`) build expressions in pandas/SQLAlchemy?
2. How would you let a type checker see fields declared via a custom base class?
3. Add `.explain()` to the expression DSL above that prints the tree.

---

## 4. Practice questions (`practice-questions.md`)

About **35 questions**:

| Phase | Question types |
| --- | --- |
| A | Introspect an unknown function and call it safely with `bind`; implement `__getattr__` config; find the recursion bug |
| B | Write `retry`, `timed`, `once` decorators with tests (sync + async); build `@auto_repr` and `@frozen_after_init` |
| C | Registry via `__init_subclass__`; equivalent `type()` call; metaclass singleton vs module instance; resolve a metaclass conflict |
| D | AST visitor for lint rules; transform `x ** 2` → `x * x`; harden an `eval` calculator; design a mini query DSL |

Include 6 **"spot the vulnerability"** questions using `eval`, `exec`, `getattr` with user input.

---

## 5. Module mini-project

**Build `declkit`**, a tiny declarative validation and registry toolkit:

1. `Field` descriptors (`Int(min=…)`, `Str(max_len=…)`, `Choice([...])`)
   collected by `__set_name__`.
2. A `Schema` base class using `__init_subclass__` to gather fields, build a
   signature (`__signature__`), and register the schema by name.
3. `@validated` decorator (sync + async) that validates function arguments
   against annotations using `inspect.signature`.
4. A safe expression filter (`"age > 18 and country == 'DE'"`) built on the
   `ast` allow-list, used to filter lists of `Schema` instances.
5. An AST-based lint script `check_defaults.py` that reports mutable default
   arguments and missing docstrings across a directory.
6. A short `DESIGN.md` explaining why each tool in the "simplest first" ladder
   was (or was not) chosen.

Acceptance: ≥ 90 % branch coverage, type-checker clean, adversarial tests for
the expression filter (attribute access, calls, huge exponents), README with examples.

---

## 6. Completion checklist

- [ ] I can inspect any object, signature and source without running risky code.
- [ ] I can implement `__getattr__`/`__setattr__` without recursion and with correct `AttributeError`.
- [ ] I can write decorator factories and class-based decorators that preserve metadata and support async.
- [ ] I can write a class decorator and a class factory and explain `dataclass`'s approach.
- [ ] I can build a registry with `__init_subclass__` and test it in isolation.
- [ ] I can express any `class` statement as a `type(...)` call.
- [ ] I can write a metaclass **and** justify not using one.
- [ ] I can parse, analyse and transform code with `ast`.
- [ ] I can explain why `eval` sandboxing by emptying builtins fails, and I use safe alternatives.
- [ ] I can design a small declarative API with good errors and types.
- [ ] I completed the `declkit` mini-project.

**Next:** Module 1.13 — Standard Library Toolkit, the batteries you will use
daily after these language-level tools.
