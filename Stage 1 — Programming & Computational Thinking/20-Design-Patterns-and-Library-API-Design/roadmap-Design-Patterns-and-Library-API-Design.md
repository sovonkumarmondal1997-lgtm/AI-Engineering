# Roadmap — Module 1.20: Design Patterns and Library API Design

This is the learning roadmap for the twentieth module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
about design patterns and about designing APIs other people depend on,
**in what order**, **how** to practise each topic, and **how to prove to
yourself** that you have learned it.

Design patterns are named, reusable solutions to recurring design problems.
In Python many classic (Java/C++-era) patterns collapse into first-class
functions, modules, decorators, generators and protocols — so the skill is
not memorising UML but recognising the *problem* and choosing the lightest
Pythonic solution. Library API design is the other half: once other people
(or other teams, or future you) import your code, every name, signature,
exception and default becomes a contract that you must keep stable.

This module builds on Module 1.8 (encapsulation, composition, inheritance,
protocols, dependency inversion, layered design), Module 1.11 (data model),
Module 1.12 (decorators, registries, DSLs), Module 1.15 (signatures, errors,
deprecations), and Module 1.18 (packaging, entry points, versioning). It
prepares you for the backend, agent and evaluation stages, where frameworks
are assembled from exactly these patterns (strategy, registry, adapter,
pipeline, observer, command).

> Target: **Python 3.12+**, type-checked with `mypy`/`pyright` in strict mode for new code.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain the purpose and trade-offs of the main GoF patterns and say which ones
  Python usually replaces with simpler constructs.
- Implement factory, builder, singleton **alternatives**, adapter, facade, proxy/decorator,
  strategy, observer and command patterns idiomatically and test them.
- Build plugin/registry mechanisms with clear contracts and safe discovery.
- Design a **public API**: naming, module layout, `__all__`, public vs private, typing, docs, examples.
- Plan **backward compatibility**: what is breaking, how to deprecate, how to test compatibility.
- Design **exception hierarchies** for libraries and decide what to raise, wrap or let through.
- Apply **sans-I/O** and dependency-injection techniques to make libraries testable and reusable
  across sync/async/frameworks.
- Recognise anti-patterns (god object, singleton abuse, deep inheritance, stringly-typed APIs, hidden global state)
  and refactor towards patterns safely, with tests.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Encapsulation, abstraction, composition | Module 1.8 (01) | Foundation of all patterns |
| Inheritance, polymorphism | Module 1.8 (02) | Strategy/template method trade-offs |
| Protocols, dependency inversion | Module 1.8 (05) | Interfaces for adapters/strategies |
| Separating side effects, layered design | Module 1.8 (07, 08) | Facade, ports/adapters, sans-I/O |
| Data model, ABCs, mixins | Module 1.11 | Pythonic interfaces |
| Decorators, registries, DSLs | Module 1.12 | Plugin and builder patterns |
| Modern signatures, errors, warnings | Module 1.15 | API ergonomics and deprecations |
| Entry points, versioning, release | Module 1.18 | Plugin discovery, compatibility |
| Testing and mocking | Modules 1.7, 1.16 | Verifying pattern implementations |
| Code smells and refactoring | Module 1.23 (preview) | Anti-pattern fixes |

**Tools:** `uv`, `pytest`, `mypy --strict` or `pyright`, `ruff`, `griffe` (API diff), `import-linter`, `sphinx`/`mkdocs`, `hypothesis` (optional).

---

## 3. How the module is organised

```text
Phase A — Thinking in Patterns                   (Basics)
  01 Pythonic design patterns overview
  02 creational patterns
Phase B — Structure and Behaviour                (Intermediate)
  03 structural patterns
  04 behavioural patterns
  05 plugin and registry patterns
Phase C — Designing for Other People             (Advanced)
  06 designing public APIs
  07 backward compatibility and deprecation policy
  08 error hierarchies for libraries
  09 sans-I/O and testable library design
Phase D — Judgement                              (Advanced)
  10 anti-patterns and refactoring to patterns
```

Pace: about 3–4 weeks part-time. Use one running case study, `fetchkit` — a
small data-fetching library (HTTP source, cache, parser, retry policy,
output sinks) — evolving through the lessons. Each lesson ends with a
refactor of `fetchkit` plus tests.

---

## Lesson 01 — `01-pythonic-design-patterns-overview.md`

**Why it matters.** Patterns give teams a shared vocabulary ("use a
strategy here", "wrap it in an adapter") and prevent reinventing awkward
solutions. But applying Java-style patterns literally in Python produces
bloated code. You need to know which patterns are *natural*, which are
*built in*, and which are *unnecessary*.

### Basic — what to learn

- Definition of a pattern: **name, problem, solution, consequences**. Three families (GoF): creational, structural, behavioural.
- Why patterns exist: manage change, reduce coupling, communicate intent.
- The Pythonic toolbox that replaces boilerplate:
  - first-class functions & closures replace Strategy/Command/Factory classes,
  - modules are singletons,
  - decorators implement Decorator/Proxy-like wrapping,
  - generators/iterators implement Iterator,
  - context managers implement RAII/resource patterns,
  - duck typing/Protocols replace many interface hierarchies,
  - `dataclasses`/`enum` replace Value Object/State boilerplate.

```python
# Strategy without classes: pass a function
def total(items, pricing):               # pricing: Callable[[Item], Decimal]
    return sum(pricing(i) for i in items)

total(cart, lambda i: i.price * (1 - i.discount))
```

### Intermediate — what to learn

- Pattern catalogue map: *Creational* (Factory Method, Abstract Factory, Builder, Prototype, Singleton), *Structural* (Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy), *Behavioural* (Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor).
- For each, one-line "Pythonic form" (e.g. State → enum + dispatch table or `match`; Visitor → `functools.singledispatch`/`match`; Template Method → hooks or higher-order functions; Memento → `copy`/`dataclasses.replace`).
- Architectural patterns relevant to AI/data work: pipeline (chain of transformations), plugin architecture, repository, unit of work, ports-and-adapters (hexagonal), event-driven/pub-sub, retry/circuit-breaker, idempotent consumer (Stage 2 covers data-pipeline specifics).
- How to choose: start with the simplest code; introduce a pattern when there are **≥ 2–3 real variants** or a measurable pain (duplication, change amplification, test difficulty).
- Reading real code for patterns: `logging` (handlers = Observer/Strategy; filters = Chain), `pathlib` (Facade), `sqlalchemy` (Unit of Work, Identity Map), `requests` adapters (Adapter), `pytest` (Plugin/Hook), `argparse` (Builder/Command).
- Pattern descriptions in a design doc: context, forces, decision, alternatives considered.

### Advanced — what to learn

- Design principles behind patterns: SOLID (single responsibility, open/closed, Liskov, interface segregation, dependency inversion), "composition over inheritance", "program to an interface", Law of Demeter, YAGNI, DRY vs the wrong abstraction (rule of three).
- Cost model of abstraction: indirection, cognitive load, performance, testing overhead; "accidental complexity" and speculative generality.
- Pattern languages for distributed/AI systems (awareness): saga, outbox, CQRS, circuit breaker, bulkhead, backpressure, fan-out/fan-in, map-reduce — detailed in later stages.
- Architecture decision records (ADRs): capture why a pattern was chosen; revisit conditions.
- Pattern **smells**: patterns applied reflexively, class names like `AbstractFooFactoryManager`, one-implementation interfaces, deep hierarchies.
- Conway's law & module boundaries; public vs internal APIs (lesson 06); evolutionary design with tests as a safety net.
- Exercise: take three well-known Python libraries, identify at least two patterns in each, and write a one-page comparison of how they are expressed Pythonically.

### Common mistakes

- Translating Java patterns class-for-class.
- Introducing abstractions before a second use case exists.
- Treating patterns as goals instead of tools.

### Self-check

1. Which GoF patterns become "a function" or "a module" in Python? Give examples.
2. State the rule of three and give a counter-example where you would abstract earlier.
3. Pick a pattern from the standard library and explain the forces it resolves.

---

## Lesson 02 — `02-creational-patterns-factory-builder-and-singleton-alternatives.md`

**Why it matters.** Object creation logic spreads and hardens quickly:
constructors with ten parameters, `if kind == ...` ladders, global instances
that make tests order-dependent. Creational patterns isolate that.

### Basic — what to learn

- **Simple factory**: a function that returns the right object based on input.
- **Factory method / classmethod constructors**: `Config.from_env()`, `Path.home()`, `datetime.fromisoformat`, `dict.fromkeys` — named constructors beat overloaded `__init__`.
- Registry-driven factories: `FORMATS = {"json": JsonWriter, "csv": CsvWriter}`; `make_writer(kind)`.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Source:
    url: str
    timeout: float = 10.0

    @classmethod
    def from_env(cls, env: dict[str, str]) -> "Source":
        return cls(env["SOURCE_URL"], float(env.get("SOURCE_TIMEOUT", 10)))

WRITERS = {"json": JsonWriter, "csv": CsvWriter}
def make_writer(kind: str):
    try: return WRITERS[kind]()
    except KeyError: raise ValueError(f"unknown writer {kind!r}; choose from {sorted(WRITERS)}") from None
```

### Intermediate — what to learn

- **Abstract factory**: create families of related objects (e.g. a "cloud provider" factory producing storage + queue + secrets clients); in Python often a class/dataclass of callables or a Protocol with methods.
- **Builder**: step-by-step construction of complex objects (fluent API) — when keyword arguments with defaults aren't enough (validation across fields, optional sections, immutability): `QueryBuilder`, `HttpRequestBuilder`; build() returns an immutable object; compare with `dataclasses.replace` and `functools.partial`.
- **Prototype**: `copy`/`deepcopy`/`dataclasses.replace` for cloning with modifications.
- **Singleton and its alternatives**: module-level instance; dependency injection (pass the instance); `functools.cache` on a factory function; per-process lazily-initialised resource; why a metaclass/`__new__` singleton harms testability (global state, hidden coupling, thread-safety, multiprocessing forks).
- Dependency injection basics: constructor injection with defaults; composition root; no service locator globals.
- Lazy initialisation and `functools.cached_property`.
- Object pools (database connections, HTTP clients): reuse expensive objects with limits and health checks (Stage 2 covers connection pooling).

```python
class RequestBuilder:
    def __init__(self, url): self._url, self._headers, self._params = url, {}, {}
    def header(self, k, v): self._headers[k] = v; return self
    def param(self, k, v):  self._params[k] = v; return self
    def build(self) -> "Request":
        if not self._url.startswith(("http://", "https://")):
            raise ValueError("url must be http(s)")
        return Request(self._url, dict(self._headers), dict(self._params))
```

### Advanced — what to learn

- Choosing creation APIs: constructor vs classmethod vs factory function vs builder vs config object; ergonomics for users and type checkers (`@overload`, `Self`, `Literal` keys → precise return types).
- Factories and typing: `type[T]` parameters, `Protocol` with `__call__`, generic factories (`def create[T: Plugin](cls: type[T]) -> T`).
- Dependency injection containers (`dependency-injector`, `lagom`, FastAPI `Depends`) vs manual wiring; composition root design; scoped lifetimes (request, task), async resources via `contextlib.asynccontextmanager`.
- Configuration → object graph: validating config (Pydantic) then constructing components; fail fast at startup; health checks.
- Thread-safety and process-safety of lazily created shared objects (locks, double-checked initialisation), forks (don't share sockets/clients across `fork`), per-worker initialisers.
- Testing creation: injecting fakes, asserting builders produce valid immutable objects, property-based tests for builder invariants.
- Anti-patterns: god factories, configuration via global mutable singletons, constructors doing I/O, boolean-flag parameter explosions.
- Case study: refactor `fetchkit` so its `Fetcher` is built by a composition root from config, with swappable HTTP client, cache and clock.

### Common mistakes

- Singleton via metaclass for convenience.
- Constructors that open files/connections.
- Builders that allow invalid intermediate states to escape.

### Self-check

1. Why prefer `Foo.from_env()` over `Foo(env=...)` with many optional arguments?
2. Replace a metaclass-singleton settings object with DI and show the test benefit.
3. Implement a fluent builder that produces an immutable object and test its invariants.

---

## Lesson 03 — `03-structural-patterns-adapter-facade-and-proxy.md`

**Why it matters.** Real systems glue together incompatible interfaces,
hide complex subsystems, and add cross-cutting behaviour (caching, retries,
auth, logging). Structural patterns keep that glue out of your core logic.

### Basic — what to learn

- **Adapter**: convert one interface to another — wrap a third-party client so your code depends on *your* `Protocol`, not on the vendor SDK.
- **Facade**: a simple entry point over a complex subsystem (`pathlib.Path`, `requests.get`, a `Pipeline.run()` hiding ten steps).
- **Decorator (object-wrapping)**: add behaviour by wrapping an object with the same interface (vs Python decorators on functions).
- **Proxy**: stand-in controlling access (lazy loading, caching, access control, remote proxy).

```python
from typing import Protocol

class Storage(Protocol):
    def read(self, key: str) -> bytes: ...
    def write(self, key: str, data: bytes) -> None: ...

class S3Adapter:                                 # adapts boto3 to Storage
    def __init__(self, client, bucket): self._c, self._b = client, bucket
    def read(self, key):  return self._c.get_object(Bucket=self._b, Key=key)["Body"].read()
    def write(self, key, data): self._c.put_object(Bucket=self._b, Key=key, Body=data)

class CachingStorage:                            # decorator/proxy wrapping any Storage
    def __init__(self, inner: Storage): self._in, self._cache = inner, {}
    def read(self, key):
        if key not in self._cache:
            self._cache[key] = self._in.read(key)
        return self._cache[key]
    def write(self, key, data): self._cache.pop(key, None); self._in.write(key, data)
```

### Intermediate — what to learn

- **Composite**: treat single objects and groups uniformly (file/directory trees, expression trees, pipeline stages composed of stages).
- **Bridge**: separate abstraction from implementation to vary both (e.g. `Report` × `Renderer`); often equals "composition + protocol".
- **Flyweight**: share immutable state to save memory (interning, `__slots__`, `functools.cache`d factories, enums).
- **Delegation helpers**: `__getattr__` forwarding (Module 1.12 lesson 02), `functools.singledispatchmethod`, `contextlib.ExitStack` for composing resources, wrapper classes with `__enter__/__exit__`.
- **Ports and adapters (hexagonal) architecture**: core domain defines ports (Protocols); adapters implement them for DB, HTTP, filesystem, LLM provider; swapping adapters for tests and migrations. Maps to LLM provider abstraction layers in later stages.
- Layered facades for libraries: a small public façade (`fetchkit.fetch(url)`) over internal modules.
- Transparent proxies: lazy objects, remote objects (RPC stubs), `unittest.mock` as proxy; pitfalls with `isinstance`, equality, pickling.
- Cross-cutting concerns as wrappers: retry, timeout, rate-limit, circuit breaker, tracing, metrics — compose them (`Retry(Timeout(Client()))`) and test each in isolation.

### Advanced — what to learn

- Wrapper **ordering** semantics (caching before retry vs retry before caching; auth outermost?), idempotency implications; documenting the middleware stack (ASGI/WSGI middleware, HTTPX transports, `requests` adapters).
- Making wrappers transparent: preserve method signatures, async variants (sync vs async wrappers — avoid duplicate code via sans-I/O, lesson 09), context managers, `__repr__` showing the chain; typing with `Protocol` + generics.
- Interface segregation: small protocols (`Reader`, `Writer`) rather than a fat `Storage`; adapters implementing only what's needed; capability discovery.
- Anti-corruption layer (DDD): translate foreign models into your domain types at the boundary; versioned vendor schemas; contract tests against recorded fixtures.
- Proxies for expensive objects in data/ML code: lazy dataset loading, memory-mapped arrays, remote model clients with caching and batching.
- Performance considerations: wrapper overhead is small; unnecessary layers cost clarity; measure before collapsing layers.
- Pitfalls: leaky adapters (vendor exceptions escaping), facades that grow into god objects, proxies that break identity semantics, cache invalidation in caching proxies, thread-safety of shared wrappers.
- Case study: add `RetryingFetcher`, `CachingFetcher`, `RateLimitedFetcher` wrappers to `fetchkit` and test composition order with fake clients and fake clocks (Module 1.16 lesson 07).

### Common mistakes

- Depending directly on vendor SDK types throughout the code.
- Facades exposing every internal option.
- Wrapping without preserving error semantics.

### Self-check

1. How does an adapter differ from a facade? From a proxy?
2. Compose retry, cache and timeout wrappers; argue for an order and test it.
3. Define a `Protocol` for LLM completion providers and write two adapters with contract tests.

---

## Lesson 04 — `04-behavioural-patterns-strategy-observer-and-command.md`

**Why it matters.** Behavioural patterns define how objects collaborate and
how algorithms vary. Strategy, observer and command appear in every
framework: scoring functions, event hooks, job queues, undo stacks, agent
tool calls.

### Basic — what to learn

- **Strategy**: interchangeable algorithms behind one interface; in Python a function/callable or Protocol (`Callable[[Item], float]`); `sorted(key=...)` is Strategy.
- **Observer / publish-subscribe**: subjects notify subscribers (`signals`, event emitters, `logging` handlers, GUI callbacks).
- **Command**: encapsulate a request as an object/callable (queue it, log it, retry it, undo it) — `functools.partial`, dataclass commands, job queues.
- **Template method**: base algorithm with overridable hooks vs passing functions in.

```python
from collections import defaultdict
from collections.abc import Callable

class EventBus:
    def __init__(self): self._subs: dict[str, list[Callable]] = defaultdict(list)
    def subscribe(self, topic: str, fn: Callable) -> Callable[[], None]:
        self._subs[topic].append(fn)
        return lambda: self._subs[topic].remove(fn)          # unsubscribe handle
    def publish(self, topic: str, **event):
        for fn in list(self._subs[topic]):                    # copy: handlers may unsubscribe
            fn(**event)
```

### Intermediate — what to learn

- **State**: behaviour varies with state; implement with `enum` + transition table (`dict[(State, Event), State]`), or `match`, or state classes (Module 1.9 lesson 06 state machines).
- **Chain of Responsibility / middleware**: ordered handlers that process or pass on a request (validation → auth → rate-limit → handler); function composition; `logging` filter chain; web middleware.
- **Iterator** (built in) and generators for pipelines; **Visitor** via `singledispatch`/`match`.
- **Mediator** (event bus) vs direct calls; **Memento** (snapshot for undo using immutable dataclasses and `replace`).
- Command pattern details: serialisable commands (dataclass + `to_dict`), idempotency keys, retries, dead-letter handling; command bus; undo/redo with inverse commands; relation to task queues (Stage 7) and agent tool calls (Stage 11).
- Observer pitfalls: ordering, exceptions in handlers (isolate), re-entrancy (publish during publish), memory leaks (strong refs → `weakref.WeakMethod`, Module 1.13 lesson 10), synchronous vs asynchronous delivery.
- Strategy selection: config-driven registries (lesson 05), default strategies, validating strategy signatures.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class DeleteFile:
    path: str
    def do(self): ...
    def undo(self): ...

history: list[DeleteFile] = []
def run(cmd): cmd.do(); history.append(cmd)
def undo_last(): history.pop().undo()
```

### Advanced — what to learn

- **Async events and backpressure**: bounded queues, fan-out, ordering guarantees, at-least-once delivery, idempotent handlers; `asyncio` event buses; avoiding unbounded subscriber lists.
- **Hooks systems**: `pluggy` (hook specs, `firstresult`, `hookwrapper`), pytest hooks as a case study (links to Module 1.16 lesson 03); designing hook points in your library (when to emit, what data, mutability of event payloads).
- Strategy in ML/AI code: scoring functions, samplers, retrievers, rerankers, evaluators swapped via config; making strategies **pure** and cacheable; typing generic strategies (`Protocol[T_in, T_out]`).
- Policy objects (retry policy, backoff, circuit-breaker thresholds) as strategies with explicit parameters; testing with fake clocks.
- Workflow/state-machine libraries (`transitions`, `python-statemachine`), durable state machines, and when explicit tables beat frameworks.
- Concurrency of observers/commands: thread-safety of subscriber lists, copy-on-write lists, locks, `queue.Queue` for cross-thread dispatch, structured concurrency for async handlers (`TaskGroup`).
- Observability patterns: events as structured logs/metrics/traces; correlation ids via `contextvars` (Module 1.13).
- Anti-patterns: callback hell, hidden global event buses, observers mutating subjects, command objects containing huge payloads, state explosion without tests.
- Case study: give `fetchkit` an event system (`on_request`, `on_retry`, `on_error`), a pluggable retry **policy** (strategy), and a replayable `FetchCommand` with idempotency key.

### Common mistakes

- Subscribers that raise and break other subscribers.
- Mutating the subscriber list while iterating.
- Using inheritance (template method) where passing a function is simpler.

### Self-check

1. Turn a three-branch `if kind == ...` into a Strategy implemented as functions and justify.
2. Where can an observer-based design leak memory and how do you prevent it?
3. Implement undo/redo for a small text editor using commands and test it.

---

## Lesson 05 — `05-plugin-and-registry-patterns.md`

**Why it matters.** Open-ended systems — writers, parsers, model
providers, data connectors, evaluation metrics, agent tools — need to add
capabilities **without editing the core**. Registries and plugins
are how pytest, dbt, Airflow, LangChain and your own platforms scale.

### Basic — what to learn

- **Registry**: mapping from names to implementations; registration by decorator, by explicit call, by `__init_subclass__` (Module 1.12 lesson 05), or by entry points (Module 1.18 lesson 04).
- Contract: an interface (`Protocol`/ABC) + a stable identifier + a version.
- Looking up with helpful errors: unknown name → list available names, suggest close matches (`difflib`, Module 1.14 lesson 05).

```python
from collections.abc import Callable

class Registry[T]:
    def __init__(self, kind: str): self.kind, self._items = kind, {}
    def register(self, name: str) -> Callable[[T], T]:
        def deco(obj: T) -> T:
            if name in self._items: raise ValueError(f"{self.kind} {name!r} already registered")
            self._items[name] = obj; return obj
        return deco
    def get(self, name: str) -> T:
        try: return self._items[name]
        except KeyError:
            raise LookupError(f"unknown {self.kind} {name!r}; available: {sorted(self._items)}") from None

PARSERS: Registry[type] = Registry("parser")
@PARSERS.register("csv")
class CsvParser: ...
```

### Intermediate — what to learn

- Discovery strategies compared: import side effects, explicit `register_all()`, `pkgutil.iter_modules`/`importlib` scanning a package, **entry points** for third-party plugins, configuration listing import paths (`"pkg.mod:Class"` strings loaded lazily).
- Lazy loading & error isolation: store import paths, import on first use; a broken plugin yields a clear error and doesn't crash unrelated functionality.
- Plugin metadata: name, version, capabilities, supported API version, config schema; `--list-plugins` command; `doctor` output.
- Plugin configuration & validation: each plugin declares a config model; the host validates before instantiation.
- Lifecycle: `setup()`, `run()`, `teardown()`; context-managed plugin instances; ordering/priority/dependencies between plugins (topological sort).
- Testing registries: isolating global registries per test (fixture snapshot/restore), contract tests that every registered plugin must pass (`pytest.mark.parametrize` over the registry).
- Alternatives: dependency injection of a mapping (no globals) — pass the registry into the app object.

### Advanced — what to learn

- **Versioned plugin APIs**: semantic versioning for the contract, capability negotiation, adapters for old plugin versions, deprecation timeline (lesson 07); compatibility test matrix of host × plugin versions.
- **Security & trust**: plugins are code execution; allow-list by name/signature; run untrusted plugins out-of-process (subprocess/RPC, WASM, containers); supply-chain concerns (Module 1.18 lessons 06, 10); least-privilege capabilities (e.g. plugin gets a restricted context object, not global state).
- Hook-based architectures (`pluggy`) vs registry-based: when you need multiple implementations called in order vs one chosen by name; `firstresult`, wrappers, hook specs, historic calls.
- Registry design details: namespacing (`vendor.name`), aliases, conflicts, override rules, per-environment registration, thread-safe mutation, immutability after startup ("freeze").
- Performance: lazy imports (Module 1.19 lesson 04), caching discovery results, avoiding repeated `entry_points()` scans.
- Documenting plugin authoring: template repo, contract tests as a public test kit (`fetchkit.testing.PluginContractTests`), examples, compatibility badges.
- AI-system examples: model-provider registry, tool registry for agents (tool schemas validated on registration), metric registry for evals, retriever/reranker registries; how to log which implementation produced each result for reproducibility.
- Case study: extend `fetchkit` with parser and sink plugins discovered via entry points; build a `fetchkit.testing` contract-suite; create two sample plugin packages.

### Common mistakes

- Global mutable registries leaking across tests.
- Import-time side effects with no documented import step.
- No error isolation for broken plugins.

### Self-check

1. Compare four discovery mechanisms and choose one for a third-party-extensible library.
2. How do you test that every registered writer satisfies the writer contract?
3. Design the trust model for loading plugins from untrusted sources.

---

## Lesson 06 — `06-designing-public-apis.md`

**Why it matters.** Your API is the product. Good APIs are easy to use
correctly and hard to use incorrectly; bad ones generate support requests,
bugs and breaking changes. This applies equally to a library, an internal
module shared by teams, a CLI, a REST/Python SDK for an AI service, or a
tool interface exposed to an agent.

### Basic — what to learn

- Public vs private: leading underscore convention, `__all__`, documented vs undocumented; "if it's not documented, it's not API" (but users depend on it anyway — Hyrum's law).
- Package layout for APIs: `from fetchkit import fetch, Fetcher, FetchError`; internals in `_internal/` or `_impl` modules; re-export in `__init__.py`; avoid deep import paths in docs.
- Naming: verbs for functions, nouns for classes, consistent vocabulary, no abbreviations surprises, `is_/has_` for booleans, units in names or types (`timeout_seconds`), plural vs singular.
- Signature basics: required args first, optional keyword-only, sensible defaults, no boolean traps (Module 1.15 lesson 03).
- Type hints on every public function; return concrete, accept abstract (`Iterable`, `Mapping`); `py.typed`.
- Docstrings with examples (doctests), parameter semantics, units, raised exceptions.

```python
# fetchkit/__init__.py
from ._fetcher import Fetcher, fetch
from ._errors import FetchError, TransientFetchError, PermanentFetchError

__all__ = ["Fetcher", "fetch", "FetchError", "TransientFetchError", "PermanentFetchError"]
```

### Intermediate — what to learn

- **Principle of least astonishment**; consistency across the API; "one obvious way".
- Make invalid states unrepresentable: enums/`Literal` instead of magic strings; value objects (`Timeout`, `Url`) with validation; immutable results (frozen dataclasses); avoid returning `None` for "error".
- Progressive disclosure: simple things simple (`fetch(url)`), advanced things possible (`Fetcher(client=..., policy=...)`); sensible defaults and escape hatches.
- Return types: results objects vs tuples; iterators vs lists (laziness); pagination; sync vs async variants and naming (`fetch` / `afetch` or separate `aio` module).
- Configuration objects vs many keyword args; builder or dataclass for complex configuration; environment-driven defaults documented and overridable.
- Extension points (callbacks, protocols, plugins) designed deliberately (lessons 04, 05).
- Documentation as part of the API: quick start, how-to guides, reference (generated from docstrings), explanation; examples are tested (`doctest`, `pytest --doctest-modules`, `mkdocs` + `mkdocstrings`).
- Typing ergonomics: avoid `Any`, precise overloads, `TypedDict` for kwargs, generics for containers, `Self`; run `mypy --strict` against example code *as a user*.
- Usability testing: write the README **first**; have a teammate try the API without help; collect friction.

### Advanced — what to learn

- Hyrum's law and the public-surface audit: what do users depend on beyond the docs (error messages, ordering, timing, private attribute access)? Reduce accidental surface: don't expose internals, return copies/views, hide implementation types behind protocols.
- API stability levels: stable / provisional / experimental; `warnings` for experimental features; separate `fetchkit.experimental` namespace; semantic versioning mapping (Module 1.18 lesson 07).
- Design for evolution: keyword-only extension points, `**options` bags with validation, result objects that can gain fields, sealed enums vs extensible registries, versioned wire formats.
- Cross-language/transport APIs: CLI flags & exit codes, config files, REST/JSON schemas, Python SDK wrappers, MCP/tool schemas for agents (Stage 8/11) — consistency principles are the same: stable names, explicit schemas, helpful errors, idempotency.
- Error design as API (lesson 08), logging as API (logger names, structured fields, levels), metrics names; avoid printing from libraries.
- Performance contracts: complexity guarantees, laziness, thread-safety and async-safety statements, resource ownership and cleanup (`close()`/context manager).
- Review process: API design review checklist, RFC template, deprecation plan required for changes, `griffe`/`api-diff` in CI to detect accidental API changes, public API snapshot tests.
- Accessibility: good error messages, typed completion in IDEs, discoverability (`dir()` of public names, `help()`), minimal imports at top level for fast startup.
- Case study: critique three real APIs (e.g. `requests`, `httpx`, `pathlib`, `subprocess.run`, `sklearn` estimators, OpenAI/Anthropic SDKs) — what is excellent, what is awkward, what would you change; write a one-page critique.

### Common mistakes

- Exposing implementation types (return `requests.Response` from your library).
- Magic strings and boolean flags.
- Changing defaults silently.

### Self-check

1. List five ways an API can make misuse hard.
2. Apply `__all__`, `_internal` modules and a snapshot test to lock the public surface of `fetchkit`.
3. Write the README quick-start for a library before implementing it and revise the API after trying to write the examples.

---

## Lesson 07 — `07-backward-compatibility-and-deprecation-policy.md`

**Why it matters.** Users' code is a large, invisible test suite for your
library. Breaking it without warning destroys trust; never changing anything
freezes the project. A written, automated compatibility policy lets you
evolve responsibly — and applies equally to internal platform libraries,
CLI interfaces, data schemas and model/tool APIs.

### Basic — what to learn

- What counts as **breaking**: removing/renaming public names; changing signatures (parameter order/names/required-ness/types); changing return types or shapes; changing exceptions raised; changing default behaviour; raising minimum Python or dependency versions; changing CLI flags/exit codes/output formats; changing file/DB/wire formats.
- Non-obvious breaks: tightening validation, changing iteration order, timing/performance cliffs, logging output relied upon by parsers, transitive dependency changes.
- Semantic versioning obligations (Module 1.6, 1.18 lesson 07); `0.y.z` caveats.
- The deprecation warning mechanics from Module 1.15 lesson 09 (`warnings.warn(..., DeprecationWarning, stacklevel=2)`, `@deprecated`).

```python
def fetch(url, *, timeout=10, retries=None, max_retries=None):
    if retries is not None:
        warnings.warn("`retries` is deprecated; use `max_retries` (removal in 3.0)",
                      DeprecationWarning, stacklevel=2)
        max_retries = retries if max_retries is None else max_retries
    ...
```

### Intermediate — what to learn

- A **written policy**: supported Python versions, deprecation period (e.g. ≥ 2 minor releases or 6 months), what is public API, how breaking changes are announced (changelog, release notes, migration guide), LTS lines.
- Techniques for non-breaking evolution: add optional keyword-only parameters; add new function and deprecate old; accept both old and new forms during transition; module `__getattr__` aliases for renamed modules; keep re-exports from old import paths with warnings; versioned endpoints/schemas; feature flags / opt-in future behaviour (`from __future__`-style flags, `FutureWarning`).
- **Compatibility tests**: run the previous version's test-suite or documented examples against the new code; golden-file and snapshot tests for outputs; contract tests for plugins; `griffe check` / `api-diff` to detect signature changes automatically; type-check examples with both old and new versions.
- Migration tooling: codemods (`libcst`, `ruff` rules, `pyupgrade`-style scripts), migration guides with before/after snippets, `python -W error::DeprecationWarning` for users' CI.
- Dependency compatibility: lower-bound testing (Module 1.16 lesson 08), avoiding unnecessary upper bounds, vendoring vs dependency, protecting against transitive breaks with constraints and lock files in applications.
- Communicating: changelog categories (Added/Changed/Deprecated/Removed/Fixed/Security), release notes highlight breaking items first, advance notices on issue tracker and mailing lists, deprecation timelines in docs.

### Advanced — what to learn

- **Compatibility across time and space**: forward compatibility (old readers, new data — ignore unknown fields), backward compatibility (new readers, old data — defaults for missing fields), schema evolution rules for JSON/Avro/Protobuf/Parquet and API payloads (Stage 2 data contracts); never reuse field names/ids; tolerant reader pattern.
- Python-specific hazards: changing a function to a generator or vice versa; returning a view vs list; `dict` ordering assumptions; `isinstance` checks against changed class hierarchies; pickled objects and class moves (provide `__reduce__`/aliases); changes in `__repr__` that others parse; `__slots__` addition breaking dynamic attributes; making a class `frozen`; changing `__eq__`/`__hash__`.
- Large-scale evolution strategies: parallel APIs (`v1`/`v2` namespaces), strangler pattern, adapter shims, dual-write/dual-read for data, gradual rollout with telemetry on deprecated usage (count warnings, usage metrics) to decide removal timing.
- Governance: who approves breaking changes (maintainer/API review board), RFC/ADR process, major-version planning, "breaking change budget", communicating to enterprise consumers, support for older majors (security backports).
- Case studies: Python 2→3, pandas deprecation cycles (`FutureWarning`), NumPy 2.0 migration (ruff rule `NPY201`), Django's deprecation policy (two releases), `requests` stability promises, Pydantic v1→v2 (compat layer) — extract lessons and write a post-mortem summary of what worked.
- Tooling projects: build a `compat-check` script that imports two versions of a package (in separate venvs), diffs public API (names, signatures, annotations) and fails CI on undocumented breaks.
- Internal platform context: compatibility with ML pipelines — feature definitions, prompt templates, model signatures, tool schemas: version them, record versions in run metadata.

### Common mistakes

- Removing something "nobody uses" without checking telemetry.
- Silent behavioural changes under unchanged signatures.
- Deprecating without telling users how to migrate.

### Self-check

1. Classify 10 listed changes as breaking/non-breaking and defend borderline cases.
2. Implement a rename of a public function with alias, warning, test, changelog and removal timeline.
3. Build the API-diff check and run it on two tagged versions of an open-source library.

---

## Lesson 08 — `08-error-hierarchies-for-libraries.md`

**Why it matters.** Errors are part of your API: callers write `except`
clauses against them. A good hierarchy lets callers handle categories
(retryable vs permanent, user error vs bug), without parsing messages or
depending on your internals' exceptions.

### Basic — what to learn

- One **base exception** per library: `class FetchError(Exception)`; users can catch everything from the library with one clause without catching unrelated errors.
- Subclasses by *what the caller can do*: `TransientFetchError` (retry), `PermanentFetchError` (don't), `ValidationError` (fix input), `ConfigError` (fix configuration), `NotFoundError`.
- Standard exceptions still apply for programming errors: `TypeError`, `ValueError` for wrong arguments; don't wrap everything.
- Good messages (Module 1.15 lesson 04): what happened, which value, what to do; no secrets.

```python
class FetchError(Exception):
    """Base class for all fetchkit errors."""

class TransientFetchError(FetchError):
    """Operation may succeed if retried."""
    def __init__(self, message: str, *, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after

class PermanentFetchError(FetchError):
    """Retrying will not help."""
```

### Intermediate — what to learn

- **Translate at boundaries**: wrap vendor/stdlib exceptions (`httpx.ConnectError`, `OSError`, `json.JSONDecodeError`) into your hierarchy using `raise NewError(...) from err` so the cause remains but callers don't depend on the vendor type.
- Structured data on exceptions: attributes (`status_code`, `url`, `field`, `attempt`), `__str__` and `__repr__`, safe for logging; picklable (pass args to `super().__init__`; implement `__reduce__` if the constructor signature differs) so they work across `multiprocessing`.
- Documenting `Raises:` sections; testing exceptions (`pytest.raises(match=...)`, attributes, cause chain).
- Mapping errors to external contracts: HTTP status codes (Stage 7), CLI exit codes (Module 1.10 lesson 03), error codes in APIs (stable machine-readable `code` strings).
- Aggregating errors: `ExceptionGroup` for batch operations (Module 1.15 lesson 05); partial-success result objects.
- When to return a result instead of raising (`Result`/`Optional` for expected misses) vs raising (exceptional conditions); don't use exceptions for ordinary control flow in hot paths.
- Warnings vs errors vs logs: when to warn, when to raise, when to log and continue.

### Advanced — what to learn

- Hierarchy design principles: shallow (2–3 levels), organised by recovery action, stable names, multiple inheritance to also subclass builtins for compatibility (`class ConfigError(FetchError, ValueError)`), avoid exposing internal-only exception types.
- Compatibility rules: adding subclasses is safe; changing a base class or moving an exception is breaking; re-parent via aliases and deprecation (lesson 07).
- Error taxonomy mapping for distributed AI systems: transient (rate limit 429, timeout, 5xx), permanent (4xx validation, auth), degraded (partial results), policy (content filter), capacity (quota); retry/backoff policy keyed on the taxonomy (Stage 7 resilience).
- Exception safety / guarantees: basic (no leaks), strong (rollback on failure), no-throw; cleanup via context managers; partial writes (Module 1.10 lesson 05).
- Observability: attach correlation ids, include sanitized request context, hook into structured logging; avoid duplicate logging at every layer ("log once at the boundary").
- Library vs application responsibilities: libraries raise, applications decide to log/exit; never call `sys.exit()` or `print` in libraries; avoid catching `BaseException`.
- Async and concurrency: exceptions in tasks (`TaskGroup` groups), cancellation (`CancelledError` must propagate), thread exceptions via futures.
- Security considerations: don't leak internals/secrets in messages, sanitize user-controlled strings in exception text (log injection), avoid revealing whether a user exists (auth errors).
- Case study: design the complete hierarchy for `fetchkit` (network, protocol, parse, validation, auth, rate-limit, config), with translation tests using fake HTTP responses and a table mapping each exception to retry policy and CLI exit code.

### Common mistakes

- Raising bare `Exception` or string messages as the only API.
- Leaking third-party exception types.
- Exception classes that cannot be pickled.

### Self-check

1. Why organise exceptions by recovery action rather than by module?
2. Show wrapping an `httpx` error while preserving the cause, and test `__cause__`.
3. Make an exception with extra attributes that survives `pickle` round-trip.

---

## Lesson 09 — `09-sans-io-and-testable-library-design.md`

**Why it matters.** Libraries tied to a specific I/O style (blocking sockets,
`requests`, `asyncio`) must be rewritten or duplicated for the other. The
**sans-I/O** approach separates *protocol logic* (pure state machines that
consume bytes/events and emit bytes/events) from *I/O* (reading and writing
those bytes). The result: one implementation usable from sync, async,
threads, tests and exotic environments — and trivial to test deterministically.

### Basic — what to learn

- The problem: duplicate sync/async code (`requests` vs `aiohttp`), mixed I/O and logic, hard-to-test code that needs sockets or sleeps.
- **Functional core, imperative shell**: pure functions for decisions and parsing; a thin shell for I/O (links to Module 1.8 lesson 07).
- Pure data in/out: functions take values and return values (or plan objects) and don't read clocks, files or networks.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RetryDecision:
    retry: bool
    delay: float

def decide(attempt: int, status: int, *, max_attempts=5) -> RetryDecision:   # pure
    if status in (429, 502, 503, 504) and attempt < max_attempts:
        return RetryDecision(True, min(2 ** attempt, 30))
    return RetryDecision(False, 0.0)

# shell: sync
def get(url):
    for attempt in range(1, 10):
        r = client.get(url)
        d = decide(attempt, r.status_code)
        if not d.retry: return r
        time.sleep(d.delay)
```

### Intermediate — what to learn

- **Sans-I/O protocol objects**: a class with `receive_data(bytes)` → events and `send(event)` → bytes (as in `h11`, `h2`, `wsproto`, `hyperframe`); the caller does the socket reads/writes in whatever style it likes.
- Writing a mini sans-I/O parser: e.g. a line-based or length-prefixed protocol state machine fed arbitrary chunks (handles partial frames) producing typed events; test with split/merged/corrupted byte streams (property-based tests, Module 1.16).
- Dependency injection of side effects: pass a `Clock`, `Sleeper`, `RandomSource`, `Transport` (Protocol) instead of calling globals; default real implementations, fakes in tests (Module 1.16 lesson 07).
- Generators/iterators as coroutines for protocol logic (`yield` requests, `send` responses); trampolines that run the same generator under sync and async drivers.
- Thin sync and async shells sharing the core: `Client` and `AsyncClient` with ~20 lines each around the sans-I/O engine (as in `httpx`/`httpcore` design).
- Resource management: ownership of connections, context managers, explicit `close()`; timeouts are shell concerns, deadlines are core data.
- API surface: keep the core importable without heavy dependencies (no `requests` import to use parsers).

### Advanced — what to learn

- Designing the **effect interface**: the core returns *commands/effects* (`SendRequest`, `Sleep(2.0)`, `Log`, `Done(result)`) to be interpreted by a driver; allows deterministic simulation (fake time), record/replay, and testing retry/backoff/timeouts instantly (a lightweight form of the "free monad"/interpreter pattern).
- Time as data: pass `now` explicitly or use deadlines; avoid `time.time()` inside core logic; simulate hours of retries in milliseconds.
- Supporting both sync and async without duplication: code generation (`unasync`), single core + two drivers, `anyio` abstractions, `asyncio.to_thread` bridging — trade-offs; avoid blocking the event loop in async shells (Stage 7).
- Streaming and backpressure in sans-I/O designs; incremental parsing of huge inputs; bounded buffers; protocol limits (max header size) as security controls.
- Applying the approach beyond networking: file formats (parsers fed chunks), LLM streaming parsers (SSE events → structured chunks), retry/rate-limit policies, tool-call loops for agents (core decides next action; shell calls model/tools), data-pipeline step planners.
- Test strategy: unit-test the core exhaustively with in-memory events; contract-test shells against a local fake server; a few end-to-end tests; mutation testing on the core (Module 1.16 lesson 02).
- Architecture documentation: diagram of core vs shell vs adapters; dependency rules enforced by `import-linter` (core must not import `socket`, `asyncio`, `requests`).
- Case study: restructure `fetchkit` into `core` (retry policy, pagination planning, parsing, request building), `sync` shell, `async` shell, and `testing` fakes; demonstrate simulating a 10-minute outage test in milliseconds.

### Common mistakes

- Core logic importing the HTTP client.
- Mixing time/sleep calls into decision logic.
- Duplicating logic across sync and async clients.

### Self-check

1. Why does sans-I/O make a library both easier to test and usable under both sync and async?
2. Write a length-prefixed protocol parser as a sans-I/O class and test it with arbitrarily chunked input.
3. Implement an effect-returning retry planner and a driver that simulates time.

---

## Lesson 10 — `10-anti-patterns-and-refactoring-to-patterns.md`

**Why it matters.** Knowing patterns is half the skill; the other half is
spotting when code has outgrown its structure and refactoring it **safely**
into a better one, one small, tested step at a time. This lesson pairs with
Module 1.23 (code smells, characterization tests, refactoring catalogue).

### Basic — what to learn

- Common anti-patterns in Python code:
  - **God object / big ball of mud**: one class/module does everything.
  - **Singleton/global state abuse**: hidden dependencies, order-dependent tests.
  - **Stringly-typed code**: magic strings and dict-of-anything instead of enums/dataclasses.
  - **Deep inheritance & fragile base class**; inheritance for reuse instead of composition.
  - **Boolean flag parameters**; long parameter lists; primitive obsession.
  - **Premature abstraction / speculative generality**: interfaces with one implementation, factories for one product.
  - **Shotgun surgery / feature envy / divergent change**: poorly placed responsibilities.
  - **Copy-paste programming**, **magic numbers**, **dead code**.
  - **Swallowing exceptions**, **return codes instead of exceptions**, **`except Exception: pass`**.
  - **Mutable default arguments**, **mutating arguments**, **import-time side effects**.
  - **Leaky abstractions** (vendor types, SQL in domain logic).
- Smell → likely pattern mapping (e.g. `if/elif` on type → strategy/dispatch table/polymorphism; scattered construction → factory/builder; vendor calls everywhere → adapter/facade; many `notify_*` calls → observer/event; duplicated retry code → decorator/wrapper).

### Intermediate — what to learn

- **Refactoring safely**: first write **characterization tests** to pin current behaviour (Module 1.23 lesson 02); make small steps (extract function/class, move method, introduce parameter object, replace conditional with polymorphism/registry, replace inheritance with delegation); run tests after each step; commit frequently.
- Refactoring catalogue essentials (Fowler): Extract Function, Inline Function, Rename, Introduce Parameter Object, Replace Magic Number with Constant, Replace Conditional with Polymorphism, Replace Inheritance with Delegation, Extract Class, Move Function, Introduce Special Case/Null Object, Replace Constructor with Factory.
- Tools: `ruff` (complexity `C901`, bugbear), `radon`/`xenon` (cyclomatic complexity), `vulture` (dead code), `pylint` (duplication, design checks), `import-linter` (layer rules), `mypy` strictness as a refactoring safety net, IDE refactorings (rename/extract in VS Code/PyCharm), `libcst`/`rope` for automated refactors.
- Measuring improvement: complexity, coupling (imports), test speed, number of files touched for a typical change, size of public surface.
- When **not** to refactor: no tests and no time; code that never changes; about-to-be-deleted code; performance-critical hot spots (measure).
- Strangler fig / branch by abstraction: introduce an interface, route new behaviour through it, migrate callers gradually, delete old path.

### Advanced — what to learn

- **Refactoring toward patterns** in large legacy modules: sequencing (tests → seams → extract → inject → replace), dependency-breaking techniques (Michael Feathers): seams, extract and override, parameterize constructor/method, wrap method/class, sprout method/class.
- Designing seams in Python: dependency injection via parameters, monkeypatch-friendly module structure, protocols for external systems, wrapper functions for I/O.
- Architectural refactors: layering enforcement with `import-linter` contracts; breaking cycles (dependency inversion, event-based decoupling, moving shared types to a lower layer); splitting packages (Module 1.18 lesson 08).
- Technical debt management: debt register, impact vs effort, "boy scout rule", refactoring within feature work vs dedicated sprints, communicating value to stakeholders; risk of big-bang rewrites vs incremental migration.
- Code review for design: review checklist (responsibilities, naming, coupling, public API surface, error handling, tests); reviewing refactor PRs (behaviour-preserving vs behaviour-changing separated).
- AI-assisted refactoring: use tools to propose changes but keep human-verified tests; guard against subtle behaviour changes; require diffs in small, reviewable steps.
- Anti-pattern case studies: pick a messy open-source module or your own earlier project (e.g. Stage 1 projects), document smells, propose a target design, refactor the first three steps with tests, and write a retrospective.
- Final synthesis: produce `DESIGN.md` for `fetchkit` listing each pattern used, why, alternatives rejected, public API policy, compatibility plan, and known trade-offs.

### Common mistakes

- Refactoring without tests.
- Mixing behaviour changes into refactor commits.
- Replacing one rigid structure with a more complex, over-engineered one.

### Self-check

1. For each of five given smells, name a refactoring and a target pattern, and the test you would write first.
2. Show a step-by-step sequence to break a circular dependency between two modules without breaking public API.
3. Take a 300-line function from an earlier project, add characterization tests, and refactor it into three cohesive units with measurable complexity reduction.

---

## 4. Practice questions (`practice-questions.md`)

About **35 questions**:

| Phase | Question types |
| --- | --- |
| A | Identify patterns in snippets; choose pattern vs function; critique over-engineered designs |
| B | Implement factory/builder/adapter/strategy/observer/command variants; design a registry and its contract tests |
| C | API critique and redesign; classify breaking changes; design an exception hierarchy; make a sync/async core |
| D | Refactoring plans for smelly code with test-first steps; dependency-breaking exercises |

Include 6 **"what's wrong with this API?"** items (boolean traps, leaking vendor types, silent default change, mutable defaults, misleading names, exceptions as strings).

---

## 5. Module mini-project

**Build and evolve `fetchkit`** across four tagged releases (`v0.1` → `v1.0`):

1. `v0.1`: simple `fetch(url)` function, single module, tests (ugly on purpose).
2. `v0.5`: refactor with adapters (HTTP client port), strategy for retry policy, builder/config object, event hooks, caching/retry wrappers; sans-I/O core for retry/pagination with sync and async shells.
3. `v0.9`: plugin system — parsers and sinks via entry points; contract test kit; error hierarchy with translation tests; public API (`__all__`, `py.typed`, docs with tested examples).
4. `v1.0`: compatibility policy, `griffe`-based API diff in CI, deprecation of two `v0.x` APIs with warnings and a migration guide; `DESIGN.md` and ADRs for each pattern; architecture tests with `import-linter`.
5. Add a mutation-testing run on the sans-I/O core and a performance sanity benchmark confirming wrappers add negligible overhead.

Acceptance: strict typing passes, ≥ 90 % branch coverage, public API snapshot test, a user-level README quick-start that runs as a doctest, and a written retrospective on which patterns paid off and which you removed.

---

## 6. Completion checklist

- [ ] I can name the main design patterns and give the Pythonic form of each.
- [ ] I can implement factories, builders and singleton alternatives with dependency injection.
- [ ] I can use adapters, facades and proxies/wrappers and reason about wrapper order.
- [ ] I can implement strategy, observer, command and state without needless class hierarchies.
- [ ] I can build a safe, testable plugin/registry system with versioned contracts.
- [ ] I can design a small, consistent, well-typed public API with documented stability.
- [ ] I can run a deprecation cycle and detect API changes automatically.
- [ ] I can design and test an exception hierarchy organised by recovery action.
- [ ] I can separate protocol logic from I/O and drive it from sync and async code.
- [ ] I can recognise anti-patterns and refactor safely toward better designs.
- [ ] I completed the `fetchkit` mini-project.

**Next:** Module 1.21 — Data Visualization and Notebook Workflows.
