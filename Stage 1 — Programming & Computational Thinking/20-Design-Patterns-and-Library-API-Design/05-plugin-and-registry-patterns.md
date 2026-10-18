# Plugin and Registry Patterns

> **Stage:** 1 — Programming & Computational Thinking  
> **Module:** 1.20 — Design Patterns and Library API Design  
> **Lesson:** 05 — Plugin and Registry Patterns  
> **Target:** Python 3.12+  
> **Running case study:** `fetchkit`, a small data-fetching library

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Distinguish registration, discovery, selection, loading, initialization, execution, and teardown.
- Implement a typed name-to-implementation registry with stable identifiers, contracts, metadata, duplicate protection, and actionable lookup errors.
- Choose among explicit registration, decorators, `__init_subclass__`, package scanning, configured import paths, and Python package entry points.
- Load plugins lazily and report a broken plugin without making unrelated built-in functionality unavailable.
- Validate plugin metadata, API versions, capabilities, configuration, lifecycle, ordering, and dependencies.
- Isolate registries in tests and use reusable contract tests for third-party implementations.
- Explain the trade-offs between a global mutable registry, dependency injection, and hook systems such as `pluggy`.
- Define a threat model for plugins, recognizing that importing a plugin executes code and that a name allow-list alone is not a sandbox.
- Extend `fetchkit` with parser and sink plugins and test the public contracts without third-party packages or network access.

### Prerequisites

The roadmap builds on composition, dependency inversion, and `Protocol`/ABC interfaces (Module 1.8); decorators and registries (Module 1.12); modern errors and API design (Module 1.15); testing and contract-oriented test architecture (Modules 1.7 and 1.16); and package entry points, versioning, and release practices (Module 1.18). Lesson 04 introduced strategy selection and event/command boundaries. This lesson applies those ideas to extension points that other teams or separately distributed packages can implement.

The examples use only the standard library and `pytest` for tests. The core examples do not require `pluggy`, external services, or installing a third-party plugin. The implementation is written to be runnable on current Python 3.12+ and is also compatible with Python 3.11+ where practical.

## 2. Registry and plugin mental models

### 2.1 Registry versus plugin architecture

A **registry** is a mapping from a stable identifier to a class, function, factory, or other implementation. It answers: “Given this name, which implementation is available?” A **plugin architecture** is the larger system around extension implementations: contracts, discovery, compatibility, configuration, lifecycle, error handling, security, observability, and distribution.

A registry can be entirely internal:

```python
from collections.abc import Callable
from typing import TypeVar, Generic

T = TypeVar("T")

class Registry(Generic[T]):
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self._items: dict[str, T] = {}

    def register(self, name: str) -> Callable[[T], T]:
        def decorate(item: T) -> T:
            if name in self._items:
                raise ValueError(f"{self.kind} {name!r} is already registered")
            self._items[name] = item
            return item
        return decorate

    def get(self, name: str) -> T:
        try:
            return self._items[name]
        except KeyError:
            available = ", ".join(sorted(self._items)) or "(none)"
            raise LookupError(
                f"unknown {self.kind} {name!r}; available: {available}"
            ) from None

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._items))

PARSERS: Registry[type] = Registry("parser")

@PARSERS.register("csv")
class CsvParser:
    pass
```

The registry above deliberately does not instantiate or execute the object. It stores a mapping and resolves names. This separation makes discovery, construction, and execution independently testable.

### 2.2 Six separate operations

These terms should not be conflated:

1. **Registration** records a known identifier and a reference to an implementation or loader.
2. **Discovery** finds candidates, for example through package entry points or configured import paths.
3. **Selection** chooses an implementation, for example `parser="json"` from configuration.
4. **Loading** imports the module or resolves the implementation object. Loading Python code can execute module-level statements.
5. **Initialization** validates configuration and prepares an instance, often through `setup()` or a factory.
6. **Execution and teardown** invoke the contract and release resources.

A design can register a lazy loader without importing the plugin yet. It can discover ten entry points but load only the one selected by the user. It can also reject an implementation at startup before accepting work. Keeping these stages distinct improves startup latency, diagnostics, and security review.

### 2.3 Stable names, contracts, and metadata

Names are public API. Prefer identifiers such as `csv`, `json`, `parquet`, or `vendor.csv` over a class's `__name__`, module path, or display label. Class and module names often change during refactoring; configuration names and persisted job definitions may live for years. Treat renaming as a compatibility event and use explicit aliases with a deprecation window when needed.

A plugin contract specifies what the host calls and what the implementation promises. Use a `Protocol` for structural typing when implementations need not inherit from your base class. Use an ABC when shared implementation or enforced inheritance is valuable. Neither mechanism proves that runtime behavior is correct; contract tests do that.

```python
from typing import Protocol

class Parser(Protocol):
    name: str
    api_version: int

    def parse(self, payload: bytes) -> list[dict[str, str]]: ...
```

Metadata commonly includes:

- stable name and human-readable description;
- plugin distribution/version;
- supported host API version or compatibility range;
- capabilities (for example `streaming`, `schema-validation`, `binary-input`);
- configuration schema and defaults;
- optional priority, dependencies, and provenance.

Do not treat a metadata claim as proof of behavior. Validate syntax and compatibility at registration or startup, then verify the contract with tests.

### 2.4 Registration styles

| Style | Useful when | Main risk |
|---|---|---|
| Explicit call, `registry.register(name, factory)` | Dependencies and registration order should be visible | Repetitive wiring if many built-ins exist |
| Decorator registration | A module owns a small, stable set of built-ins | Importing the module mutates global state |
| `__init_subclass__` | A controlled class hierarchy needs automatic subclass tracking | Hidden subclass creation side effects and difficult test isolation |
| Configured import path such as `pkg.mod:Plugin` | Operators explicitly configure a small set of extensions | Import paths are brittle and importing executes code |
| Package entry points | Separately installed distributions advertise plugins | Discovery can expose broken, incompatible, or untrusted candidates |

A registration decorator is a convenient syntax, not a discovery mechanism by itself. Decorators run when their defining module is imported. A decorated plugin is invisible if that module is never imported. Similarly, `__init_subclass__` sees subclasses only after Python creates their class; it does not search the environment for classes in modules that have not been imported.

### 2.5 Helpful lookup errors

An unknown name is usually a configuration or user-input problem. Raise an error that identifies the requested kind/name and available names; a close-match suggestion can reduce diagnosis time. `difflib.get_close_matches` is useful for suggestions, but suggestions must not silently change the selected plugin.

```python
from difflib import get_close_matches

available = ["csv", "json", "xml"]
requested = "jsn"
suggestion = get_close_matches(requested, available, n=1, cutoff=0.6)
print(f"unknown parser {requested!r}; available: {', '.join(available)}")
if suggestion:
    print(f"Did you mean {suggestion[0]!r}?")
```

Keep the original exception chain when an import or initialization fails. A useful public exception should explain which plugin failed and during which stage, while preserving the underlying cause for debugging.

## 3. Beginner implementation

### 3.1 A minimal typed registry with invariants

A reliable registry should define its invariants rather than relying on convention. For a small registry, useful invariants are:

- names are non-empty normalized strings;
- duplicate registration fails unless an explicit override policy is in force;
- lookup never silently picks an arbitrary implementation;
- listing is deterministic;
- the stored object is not constructed merely because it was registered;
- errors identify the plugin kind and available names;
- the registry can be instantiated independently for tests and separate application instances.

The following minimal implementation stores objects, not instances. It rejects duplicates and returns names in sorted order.

```python
from collections.abc import Callable
from difflib import get_close_matches
from typing import Generic, TypeVar

T = TypeVar("T")

class RegistryError(Exception):
    """Base error for registry operations."""

class DuplicatePluginError(RegistryError):
    pass

class UnknownPluginError(RegistryError, LookupError):
    pass

class Registry(Generic[T]):
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self._items: dict[str, T] = {}
        self._frozen = False

    def register(self, name: str, item: T) -> None:
        if self._frozen:
            raise RegistryError(f"{self.kind} registry is frozen")
        if not name or name.strip() != name:
            raise ValueError("plugin name must be non-empty and have no surrounding whitespace")
        if name in self._items:
            raise DuplicatePluginError(f"{self.kind} {name!r} is already registered")
        self._items[name] = item

    def get(self, name: str) -> T:
        try:
            return self._items[name]
        except KeyError:
            names = list(self.names())
            available = ", ".join(names) or "(none)"
            suggestion = get_close_matches(name, names, n=1, cutoff=0.6)
            hint = f"; did you mean {suggestion[0]!r}?" if suggestion else ""
            raise UnknownPluginError(
                f"unknown {self.kind} {name!r}; available: {available}{hint}"
            ) from None

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._items))

    def freeze(self) -> None:
        self._frozen = True

    @property
    def frozen(self) -> bool:
        with self._lock:
            return self._frozen
```

Example use:

```python
parsers: Registry[type] = Registry("parser")
parsers.register("csv", CsvParser)
print(parsers.names())  # ('csv',)
print(parsers.get("csv"))
```

This version uses explicit registration to make mutation visible. A decorator can delegate to `register`, but the registry's invariants should remain in one implementation. The registry freezes only its own mapping; it does not freeze plugin objects or make arbitrary code thread-safe. Freeze after startup wiring if runtime registration is not a supported feature.

### 3.2 What should a registry store?

Choose the value type based on the lifecycle:

- **Class or factory:** create a new instance for each consumer or configuration.
- **Singleton instance:** share a stateful object intentionally; document concurrency and lifecycle semantics.
- **Lazy loader:** defer import and construction until selection.
- **Metadata record plus loader:** support listing/diagnostics without importing every plugin.

Storing an instance by default can accidentally share mutable state across requests or tests. Storing a class is not enough if constructor arguments differ; a factory is often the cleanest seam. Do not call a factory while listing names.

### 3.3 Minimal tests

```python
import pytest


def test_register_and_lookup() -> None:
    registry: Registry[int] = Registry("metric")
    registry.register("count", 3)
    assert registry.get("count") == 3
    assert registry.names() == ("count",)


def test_duplicate_registration_fails() -> None:
    registry: Registry[int] = Registry("metric")
    registry.register("count", 1)
    with pytest.raises(DuplicatePluginError, match="already registered"):
        registry.register("count", 2)


def test_unknown_name_lists_options_and_suggests_close_match() -> None:
    registry: Registry[int] = Registry("parser")
    registry.register("json", 1)
    registry.register("csv", 2)
    with pytest.raises(UnknownPluginError, match="available: csv, json") as error:
        registry.get("jsn")
    assert "did you mean 'json'?" in str(error.value)


def test_freeze_prevents_late_registration() -> None:
    registry: Registry[int] = Registry("metric")
    registry.freeze()
    with pytest.raises(RegistryError, match="frozen"):
        registry.register("count", 1)
```

These tests establish the mapping's public invariants. They do not prove that every plugin implements the expected parser behavior; that requires a separate contract suite in Section 8.

## 4. Intermediate discovery and lifecycle

### 4.1 Discovery mechanisms and operational trade-offs

**Import side effects.** Importing a module runs its top-level code. A decorator can register a built-in at import time, but the import must be documented and its side effects must be safe. Avoid importing every optional integration just to make a registry appear populated.

**Explicit `register_all()`.** The application imports a curated list of built-ins and registers their factories. This is easy to understand, deterministic, and friendly to static analysis. It does require maintaining the list.

**`pkgutil` / `importlib` package scanning.** Scanning modules by naming convention can be useful for plugins shipped inside one controlled package. Importing discovered modules still executes code; scanning is not a sandbox. Avoid recursively importing arbitrary environment packages.

**Entry points.** Python package metadata allows a separately installed distribution to advertise a plugin under a group such as `fetchkit.parsers`. The host can enumerate metadata without importing each target module, then load only the selected entry point. Entry-point discovery is the natural distribution mechanism for third-party extensions, but discovery does not guarantee trust or compatibility.

**Configured import paths.** An operator can configure a path such as `my_plugins.fast_parser:FastParser`. Validate the shape and source of configuration. Import only paths permitted by policy, and surface import errors with the configured identifier.

### 4.2 Lazy loading and error isolation

A lazy registration stores a loader callable or import path. Listing available plugins should not import them. Selection invokes the loader and wraps expected loading failures in a plugin-specific exception. This isolates a broken optional plugin from unrelated core features; it does not mean every error should be swallowed.

Use distinct stages in diagnostics:

- discovery error: metadata could not be read (`PluginDiscoveryError`);
- load error: module or entry point could not be imported/resolved (`PluginLoadError`);
- validation error: object does not meet the contract, API version, or requested capabilities;
- configuration error: plugin-specific settings are invalid;
- setup error: initialization failed;
- execution error: the selected plugin failed while processing work;
- teardown error: cleanup failed.

A plugin load failure should include the plugin name, source/entry-point value if available, stage, and chained cause. Do not convert `KeyboardInterrupt`, `SystemExit`, or other `BaseException` subclasses into ordinary plugin errors. Catch `Exception` around plugin boundaries unless a stronger process-level policy is explicitly justified.

### 4.3 Entry-point discovery without importing every plugin

The standard library's `importlib.metadata.entry_points()` exposes installed entry-point metadata. This small example lists candidates, then loads one chosen entry point. It has no third-party dependency and does not require any external service.

```python
from importlib.metadata import entry_points

GROUP = "fetchkit.parsers"


def list_parser_entry_points() -> tuple[tuple[str, str], ...]:
    """Return (name, value) metadata without loading target objects."""
    candidates = entry_points(group=GROUP)
    return tuple(sorted((ep.name, ep.value) for ep in candidates))


def load_parser_entry_point(name: str):
    """Load only the requested entry point; loading executes plugin code."""
    candidates = {ep.name: ep for ep in entry_points(group=GROUP)}
    try:
        chosen = candidates[name]
    except KeyError:
        raise LookupError(
            f"unknown parser entry point {name!r}; available: {', '.join(sorted(candidates)) or '(none)'}"
        ) from None
    return chosen.load()
```

`entry_points(group=...)` is the modern API. Package metadata and installed distributions can change while a long-running process is alive, so cache discovery deliberately and define when it refreshes. Do not assume an entry-point name is unique: multiple distributions can advertise the same name. The example above's dictionary comprehension would silently choose one if duplicates existed, so a production loader must detect and reject or explicitly resolve collisions. The `fetchkit` implementation below does so.

To advertise a parser from a separately built distribution, the plugin package can include this metadata:

```toml
[project.entry-points."fetchkit.parsers"]
json = "fetchkit_json.plugin:JsonParser"
```

For a sink, use the group `fetchkit.sinks`. This declaration advertises a load target; it does not prove that `JsonParser` implements the required contract. The host must validate it after loading. Installing or importing a plugin executes code; entry points are a discovery convention, not a security boundary.

### 4.4 Metadata, capabilities, configuration, and startup validation

A plugin descriptor should separate metadata from the loaded implementation. At minimum, record the stable name, source, plugin version, API version, and capabilities. Validate these fields before admitting the plugin to normal operation. A host may require a capability such as `streaming` or reject a plugin that advertises an unsupported API version.

Configuration should be validated before execution. For simple plugins, a dataclass and explicit validation may be enough. Larger libraries can offer a schema protocol or optional integration with a validation library, but the core plugin interface should not force users to install a third-party package. Never pass unvalidated arbitrary dictionaries deep into plugin code and assume the plugin will interpret them consistently.

A practical startup sequence is:

1. Build a fresh registry.
2. Register trusted built-ins explicitly.
3. Discover metadata from approved sources.
4. Detect duplicate names and invalid metadata.
5. Load only plugins required by configuration, or eagerly validate all allow-listed plugins if startup policy requires it.
6. Validate API compatibility, capabilities, config, and dependencies.
7. Call `setup(context)` and record successful initialization.
8. Freeze the registry if late mutation is unsupported.
9. Start accepting work and expose `list-plugins` / `doctor` diagnostics.

There is no universal answer about eager validation. Eagerly loading every plugin catches failures before serving requests but increases startup time and expands the code executed at startup. Lazy loading reduces startup work but shifts failures to the first selected use. Make the trade-off explicit.

### 4.5 Lifecycle, ordering, and dependencies

A lifecycle contract might provide `setup(context)`, `run(input)`, and `teardown()`. Keep the lifecycle small and define exactly when each method runs. If `setup` fails, do not call `run`; if setup succeeded, ensure teardown is attempted even when execution raises. If several plugins are started, tear them down in reverse successful-initialization order, similar to resource-stack cleanup.

Ordering matters when plugins are pipelines, middleware, or hooks. A numeric priority can establish a stable order, but ties need a deterministic secondary key such as plugin name. If plugin B requires plugin A, model the relationship as a dependency graph and topologically sort it; detect cycles and missing dependencies before initialization. Do not use arbitrary alphabetical ordering as a substitute for dependency semantics.

A single selected parser usually needs no dependency graph. A sequence of transformations, hooks, or sinks may. Use the simplest model that matches actual composition requirements.

### 4.6 Isolation in tests and operational diagnostics

A registry should be an ordinary object that can be created afresh in a test. Prefer this over clearing a process-wide global registry between tests. If legacy code requires a global registry, provide a fixture that snapshots and restores it in `try/finally`; ensure the fixture does not erase registrations made by unrelated tests or plugins.

A `fetchkit plugins list`-style interface should report plugin name, source, version, API compatibility, capabilities, load state, and failure stage. A `fetchkit plugins doctor`-style diagnostic should distinguish “not installed,” “discovered but not loaded,” “load failed,” “incompatible,” “setup failed,” and “ready.” Never make diagnostic listing import every plugin merely to print its name.

## 5. Advanced security and compatibility

### 5.1 Versioned plugin APIs

Version the **host contract**, not just the plugin package. A plugin's own version answers “which release is this?”; the API version answers “which contract does it implement?” These values are related but not interchangeable.

A host can require an exact API major version, accept a declared range, or negotiate individual capabilities. Use semantic-versioning rules deliberately: additive optional capabilities may be compatible, while changing required method signatures or semantics is usually breaking. Compatibility adapters can translate an older contract into the current one, but should be narrow, tested, and scheduled for removal. Publish a deprecation timeline and test host/plugin compatibility combinations that the project claims to support.

Do not claim that comparing version strings lexically is safe (`"10" < "2"` is true lexically). Use integer API generations, a documented parser, or a proper version type. A capability check should validate behavior where possible rather than trusting a string alone.

### 5.2 Trust boundaries: loading is code execution

A plugin is executable code, not passive data. Importing a Python module can run arbitrary top-level statements; calling an entry point can instantiate arbitrary objects; `setup`, `run`, and `teardown` can access anything permitted to the process. A signed distribution or allow-listed package helps with provenance and policy, but does not make the code harmless after it is loaded.

A practical trust model has three tiers:

- **Built-in/trusted:** shipped with the application, reviewed and tested as part of the release. Import from known modules and register explicitly.
- **Approved third-party:** installed through a controlled dependency process, pinned or constrained, reviewed/scanned as appropriate, and allow-listed by distribution and plugin identity. Run with only the privileges the host process itself has.
- **Untrusted or user-supplied:** do not import into the main process. Run out-of-process with a narrow RPC/message schema, resource limits, timeouts, filesystem/network restrictions, and an explicit capability set. Depending on the threat model, use an OS sandbox, container, or WASM runtime; a subprocess alone is not automatically a secure sandbox.

Least privilege means passing a restricted context object rather than exposing the application's full dependency container, environment, credentials, filesystem handles, or global state. Never place secrets in plugin configuration or error messages by default. Audit plugin provenance, pin versions, monitor advisories, and record which implementation produced each result.

**Important limitation:** an allow-list by name or distribution is a policy gate, not isolation. Python's in-process object model does not provide a general-purpose sandbox for arbitrary plugins.

### 5.3 `pluggy` hooks versus a registry

A registry typically answers “which one implementation should I select for this name?” Hook systems answer “which set of implementations should be called at this extension point, and in what order?”

`pluggy` (used by pytest) provides hook specifications, hook implementations, ordering controls, wrappers, options such as `firstresult`, and historic calls when late-registered plugins need selected prior hook calls replayed. It is a good fit when many plugins contribute to a host-defined set of hooks. A plain registry is simpler for selecting one parser, serializer, provider, or sink by stable identifier. The two can coexist: a registry chooses a model provider, while hooks let plugins contribute telemetry or validation around provider calls.

A hook framework does not solve trust or process isolation. Hook implementations are still code executed by the host unless explicitly isolated. Avoid adding `pluggy` to a small core example merely to select one implementation.

### 5.4 Namespaces, collisions, aliases, overrides, and concurrency

- **Namespaces:** use names like `vendor.format` when independently developed parties may choose the same short name. Define normalization and case-sensitivity rules.
- **Collisions:** reject duplicates by default and report both sources. “Last import wins” makes behavior depend on import order and is hard to reproduce.
- **Aliases:** resolve an old name to a canonical implementation and emit a deprecation warning or diagnostic. Do not register two independent copies if one alias entry is sufficient.
- **Overrides:** if supported, make override explicit, scoped, and logged. Avoid implicit replacement. Prefer a per-application registry rather than mutating a global one.
- **Environment isolation:** development, test, and production should be able to build separate registries. A test plugin must not leak into another test's registry.
- **Thread safety:** the simplest design is build-then-freeze, then perform concurrent reads. If runtime writes are required, protect mutation and compound operations with a lock. A thread-safe dictionary alone does not make “check duplicate then insert” atomic.
- **Freezing:** freeze after discovery and validation if the application expects the set of available plugins to remain stable. The freeze operation controls registry mutation, not behavior of the plugins themselves.

### 5.5 Lazy imports and discovery caching

Cache discovered entry-point metadata to avoid repeatedly scanning installed distributions. Define cache scope and refresh semantics: process-lifetime cache is simple; an explicit refresh may be useful for administrative tooling, but dynamically installing packages into a live process is often operationally surprising. If you cache loaded objects, also decide whether instances are shared or created per request.

Lazy loading should preserve clear states (`discovered`, `loading`, `ready`, `failed`) and cache a load failure or retry it according to a documented policy. Repeatedly importing a broken plugin on every request can turn one bad configuration into repeated latency and noisy logs. Conversely, permanent caching of a transient setup failure may prevent recovery. Separate import failure from per-instance setup failure so that the retry policy can differ.

### 5.6 AI and data-platform examples

The same design applies across a data or AI platform:

- **Model-provider registry:** `openai`, `local`, or `test-double`; metadata includes supported modalities, context limits, and provider API generation. Secrets should be supplied through a credential boundary, not logged.
- **Agent-tool registry:** tool name, input/output schema, capability requirements, and side-effect classification. Validate tool arguments before dispatch and require authorization separately from registration.
- **Parser registry:** CSV/JSON/line-oriented or domain-specific parsing. Contract tests establish how malformed input is handled.
- **Sink registry:** write to a file, object store, database, or test collector. Define atomicity, idempotency, flush, and close behavior.
- **Retriever/reranker registries:** record embedding/index compatibility, score semantics, and model versions; avoid comparing incomparable scores without normalization.
- **Evaluation-metric registry:** stable metric identifier, input schema, deterministic behavior, aggregation semantics, and metric implementation version.

For reproducibility, persist the canonical plugin name, plugin distribution/version, host API version, relevant configuration (redacting secrets), model/data version where applicable, and a run identifier. A result without provenance may be impossible to reproduce after a registry default changes.

## 6. Discovery-mechanism comparison table

| Mechanism | Import timing | Best fit | Strengths | Risks and controls |
|---|---|---|---|---|
| Import side effects / decorators | When module is imported | Small built-in set | Concise; co-located declaration | Hidden registration; document imports; avoid broad import sweeps |
| Explicit `register_all()` | During known application wiring | Core-owned implementations | Deterministic, reviewable, easy to test | Manual list; make missing registration visible |
| `__init_subclass__` | When subclass statement executes | Controlled class family | Low boilerplate for internal hierarchy | Hidden mutation; subclasses must be imported; global state leaks |
| `pkgutil` + `importlib` scan | Usually imports discovered modules | Plugins inside one controlled package | Convention-based discovery | Executes module code; package traversal complexity; scan only trusted namespaces |
| Configured `module:object` path | When selected path is loaded | Operator-configured extensions | Explicit deployment configuration; lazy | Brittle path; typo/load failures; allow-list and validate |
| `importlib.metadata` entry points | Metadata can be listed first; target loads on `.load()` | Third-party distributions | Packaging-standard discovery; lazy selection | Duplicate names, incompatible or malicious code; validate and define trust policy |
| `pluggy` hooks | Plugin modules must be loaded/registered; hooks run when called | Multiple contributors to extension points | Hook specs, ordering, wrappers, `firstresult` | More concepts; not a sandbox; overkill for one-name selection |

**Default recommendation:** use explicit registration for built-ins and entry points for approved third-party packages. Enumerate metadata first, detect duplicate names, load only selected plugins, validate them, and freeze the registry before serving work. Choose another mechanism only when its trade-offs fit a clear requirement.

## 7. `fetchkit` plugin implementation

This reference implementation adds two extension points: a parser converts response bytes into records, and a sink consumes records. It demonstrates typed contracts, metadata, duplicate protection, lazy entry-point discovery/loading, load-error isolation, API checks, dependency-injected registries, deterministic diagnostics, and simple lifecycle management. The built-in examples require no third-party plugin package and perform no network I/O.

### 7.1 Contract and metadata model

The parser contract returns a list of string-keyed records and rejects malformed CSV row widths and duplicate headers. The sink contract writes those records and exposes `close()`. The built-in sink factories are zero-argument so the pipeline does not branch on plugin names; production plugins can expose a validated configuration factory when construction requires options. This is intentionally small; a production library should document encoding, row ordering, streaming, partial writes, cancellation, and resource ownership as part of the contract.

### 7.2 Complete implementation (`fetchkit_plugins.py`)

Save the following code as `fetchkit_plugins.py`.

```python
from __future__ import annotations

import csv
import io
import json
import threading
from dataclasses import dataclass, field
from difflib import get_close_matches
from importlib.metadata import EntryPoint, entry_points
from typing import Any, Callable, Protocol, TypeVar, Generic

API_VERSION = 1
PARSER_GROUP = "fetchkit.parsers"
SINK_GROUP = "fetchkit.sinks"


class PluginError(RuntimeError):
    """Base class for plugin lifecycle and loading errors."""


class DuplicatePluginError(PluginError):
    pass


class UnknownPluginError(PluginError, LookupError):
    pass


class PluginDiscoveryError(PluginError):
    pass


class PluginLoadError(PluginError):
    pass


class PluginInitializationError(PluginError):
    pass


class PluginContractError(PluginError):
    pass


class RegistryFrozenError(PluginError):
    pass


@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str
    api_version: int | None = API_VERSION
    capabilities: frozenset[str] = frozenset()
    source: str = "builtin"


class Parser(Protocol):
    metadata: PluginMetadata

    def parse(self, payload: bytes) -> list[dict[str, str]]: ...


class Sink(Protocol):
    metadata: PluginMetadata

    def write(self, records: list[dict[str, str]]) -> None: ...

    def close(self) -> None: ...


T = TypeVar("T")


@dataclass(frozen=True)
class PluginSpec(Generic[T]):
    metadata: PluginMetadata
    loader: Callable[..., T] | EntryPoint
    # A normal registration stores a factory/class. Entry points are retained
    # as metadata-backed lazy loaders until the selected name is created.


class PluginRegistry(Generic[T]):
    """Registry with lazy loaders, duplicate detection, and build-then-freeze."""

    def __init__(self, kind: str, entry_point_group: str | None = None) -> None:
        self.kind = kind
        self.entry_point_group = entry_point_group
        self._specs: dict[str, PluginSpec[T]] = {}
        self._states: dict[str, str] = {}
        self._failure_stages: dict[str, str] = {}
        self._frozen = False
        self._lock = threading.RLock()
        self._discovery_cache: tuple[EntryPoint, ...] | None = None

    def register(
        self,
        metadata: PluginMetadata,
        factory: Callable[..., T] | EntryPoint,
        *,
        replace: bool = False,
    ) -> None:
        with self._lock:
            if self._frozen:
                raise RegistryFrozenError(f"{self.kind} registry is frozen")
            self._validate_metadata(metadata)
            if metadata.name in self._specs and not replace:
                prior = self._specs[metadata.name].metadata.source
                raise DuplicatePluginError(
                    f"duplicate {self.kind} {metadata.name!r}: existing source={prior!r}, "
                    f"new source={metadata.source!r}"
                )
            if replace and metadata.name not in self._specs:
                raise UnknownPluginError(
                    f"cannot replace unknown {self.kind} {metadata.name!r}"
                )
            self._specs[metadata.name] = PluginSpec(metadata, factory)
            self._states[metadata.name] = "discovered" if isinstance(factory, EntryPoint) else "registered"
            self._failure_stages.pop(metadata.name, None)

    def _validate_metadata(self, metadata: PluginMetadata) -> None:
        if not isinstance(metadata, PluginMetadata):
            raise TypeError("plugin metadata must be a PluginMetadata instance")
        if not isinstance(metadata.name, str) or not metadata.name or metadata.name.strip() != metadata.name:
            raise ValueError("plugin name must be a non-empty string with no surrounding whitespace")
        if not isinstance(metadata.version, str) or not metadata.version or metadata.version.strip() != metadata.version:
            raise ValueError("plugin version must be a non-empty string with no surrounding whitespace")
        if metadata.api_version is not None and (
            not isinstance(metadata.api_version, int)
            or isinstance(metadata.api_version, bool)
            or metadata.api_version != API_VERSION
        ):
            raise PluginContractError(
                f"{self.kind} {metadata.name!r} supports API {metadata.api_version!r}; "
                f"host requires API {API_VERSION}"
            )
        if not isinstance(metadata.capabilities, frozenset) or any(
            not isinstance(capability, str)
            or not capability
            or capability.strip() != capability
            for capability in metadata.capabilities
        ):
            raise ValueError("plugin capabilities must be a frozenset of non-empty normalized strings")
        if not isinstance(metadata.source, str) or not metadata.source:
            raise ValueError("plugin source must be a non-empty string")

    def names(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._specs))

    def metadata(self, name: str) -> PluginMetadata:
        with self._lock:
            try:
                return self._specs[name].metadata
            except KeyError:
                raise self._unknown(name) from None

    def _unknown(self, name: str) -> UnknownPluginError:
        available = list(sorted(self._specs))
        hint = get_close_matches(name, available, n=1, cutoff=0.6)
        suggestion = f"; did you mean {hint[0]!r}?" if hint else ""
        return UnknownPluginError(
            f"unknown {self.kind} {name!r}; available: {', '.join(available) or '(none)'}{suggestion}"
        )

    def add_entry_point_metadata(self) -> tuple[str, ...]:
        """Discover entry-point metadata without loading target plugin modules.

        Returns names successfully added. Duplicate names fail explicitly. Discovery
        results are cached for this registry instance; create a new registry or call
        `refresh_discovery()` to observe environment metadata changes.
        """
        if self.entry_point_group is None:
            return ()
        with self._lock:
            if self._frozen:
                raise RegistryFrozenError(f"{self.kind} registry is frozen")
            if self._discovery_cache is None:
                try:
                    self._discovery_cache = tuple(entry_points(group=self.entry_point_group))
                except Exception as exc:
                    raise PluginDiscoveryError(
                        f"failed to discover {self.kind} entry points in "
                        f"group {self.entry_point_group!r}: {exc}"
                    ) from exc
            candidates = tuple(sorted(self._discovery_cache, key=lambda item: (item.name, item.value)))
            seen: set[str] = set()
            for ep in candidates:
                if ep.name in self._specs or ep.name in seen:
                    raise DuplicatePluginError(
                        f"duplicate {self.kind} entry point {ep.name!r} from {ep.value!r}; "
                        "use a unique name or an explicit override policy"
                    )
                seen.add(ep.name)
            # Validate every candidate before mutating: collisions or malformed
            # names must not leave a partially populated registry.
            pending: list[tuple[PluginMetadata, EntryPoint]] = []
            for ep in candidates:
                metadata = PluginMetadata(
                    name=ep.name,
                    version="unknown",
                    api_version=None,
                    capabilities=frozenset(),
                    source=f"entry-point:{ep.value}",
                )
                self._validate_metadata(metadata)
                pending.append((metadata, ep))
            added: list[str] = []
            for metadata, ep in pending:
                self.register(metadata, ep)
                added.append(ep.name)
            return tuple(added)

    def refresh_discovery(self) -> None:
        """Forget cached metadata; this does not remove already registered plugins."""
        with self._lock:
            if self._frozen:
                raise RegistryFrozenError(f"{self.kind} registry is frozen")
            self._discovery_cache = None

    def create(
        self,
        name: str,
        *args: Any,
        required_capabilities: frozenset[str] = frozenset(),
        **kwargs: Any,
    ) -> T:
        """Load one plugin and optionally require declared capabilities.

        `required_capabilities` is reserved by the registry and is not passed to
        the plugin factory. A plugin's capability declaration is a claim, not a
        security boundary; validate behavior with contract tests as well.
        """
        with self._lock:
            try:
                spec = self._specs[name]
            except KeyError:
                raise self._unknown(name) from None
            self._states[name] = "loading"
        try:
            factory = spec.loader.load() if isinstance(spec.loader, EntryPoint) else spec.loader
            instance = factory(*args, **kwargs)
        except Exception as exc:
            with self._lock:
                self._states[name] = "failed"
                self._failure_stages[name] = "load"
            raise PluginLoadError(
                f"failed to load/construct {self.kind} {name!r} from "
                f"{spec.metadata.source!r}: {exc}"
            ) from exc
        try:
            self._validate_instance(name, instance)
            actual_metadata = instance.metadata
            missing = required_capabilities - actual_metadata.capabilities
            if missing:
                raise PluginContractError(
                    f"{self.kind} {name!r} lacks required capabilities: "
                    f"{', '.join(sorted(missing))}"
                )
        except Exception as exc:
            self._cleanup_failed_instance(instance, exc, "validation")
            with self._lock:
                self._states[name] = "failed"
                self._failure_stages[name] = "validation"
            raise
        setup = getattr(instance, "setup", None)
        if callable(setup):
            try:
                setup()
            except Exception as exc:
                # A failed setup may have acquired resources before raising.
                self._cleanup_failed_instance(instance, exc, "setup")
                with self._lock:
                    self._states[name] = "failed"
                    self._failure_stages[name] = "setup"
                raise PluginInitializationError(
                    f"failed to initialize {self.kind} {name!r} from "
                    f"{spec.metadata.source!r}: {exc}"
                ) from exc
        with self._lock:
            self._states[name] = "ready"
            self._failure_stages.pop(name, None)
        return instance

    @staticmethod
    def _cleanup_failed_instance(instance: Any, primary_error: Exception, stage: str) -> None:
        """Attempt cleanup without masking a validation/setup failure."""
        cleanup = getattr(instance, "teardown", None)
        if not callable(cleanup):
            cleanup = getattr(instance, "close", None)
        if callable(cleanup):
            try:
                cleanup()
            except Exception as cleanup_exc:
                primary_error.add_note(
                    f"cleanup after {stage} failure also failed: {cleanup_exc!r}"
                )

    def _validate_instance(self, name: str, instance: Any) -> None:
        if self.kind == "parser" and not callable(getattr(instance, "parse", None)):
            raise PluginContractError(f"parser {name!r} must define callable parse(payload)")
        if self.kind == "sink":
            if not callable(getattr(instance, "write", None)):
                raise PluginContractError(f"sink {name!r} must define callable write(records)")
            if not callable(getattr(instance, "close", None)):
                raise PluginContractError(f"sink {name!r} must define callable close()")
        metadata = getattr(instance, "metadata", None)
        # Always validate the loaded implementation. In particular, entry-point
        # metadata is provisional and must never make api_version=None acceptable
        # merely because a plugin happens to compare equal to the provisional record.
        if not isinstance(metadata, PluginMetadata):
            raise PluginContractError(f"{self.kind} {name!r} must expose PluginMetadata")
        try:
            self._validate_metadata(metadata)
        except (TypeError, ValueError, PluginContractError) as exc:
            raise PluginContractError(f"{self.kind} {name!r} exposes invalid metadata: {exc}") from exc
        if metadata.name != name:
            raise PluginContractError(
                f"{self.kind} {name!r} exposes metadata name {metadata.name!r}"
            )
        if metadata.api_version != API_VERSION:
            raise PluginContractError(
                f"{self.kind} {name!r} exposes API {metadata.api_version!r}; "
                f"host requires API {API_VERSION}"
            )

    def freeze(self) -> None:
        with self._lock:
            self._frozen = True

    @property
    def frozen(self) -> bool:
        with self._lock:
            return self._frozen

    def diagnostics(self) -> tuple[dict[str, str], ...]:
        """List known metadata without importing plugin targets."""
        with self._lock:
            return tuple(
                {
                    "name": spec.metadata.name,
                    "version": spec.metadata.version,
                    "api_version": str(spec.metadata.api_version) if spec.metadata.api_version is not None else "unknown",
                    "source": spec.metadata.source,
                    "state": self._states[name],
                    "failure_stage": self._failure_stages.get(name, ""),
                }
                for name, spec in sorted(self._specs.items())
            )


@dataclass(frozen=True)
class CsvParser:
    metadata: PluginMetadata = PluginMetadata(
        "csv", "1.0.0", capabilities=frozenset({"text", "records"})
    )

    def parse(self, payload: bytes) -> list[dict[str, str]]:
        text = payload.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text, newline=""))
        if reader.fieldnames is None:
            return []
        if any(not name or name.strip() != name for name in reader.fieldnames):
            raise ValueError("CSV header contains an empty or whitespace-padded column name")
        if len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("CSV header contains duplicate column names")
        records: list[dict[str, str]] = []
        for row_number, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"CSV row {row_number} has a different number of fields than the header")
            records.append(dict(row))
        return records


@dataclass(frozen=True)
class JsonRecordsParser:
    metadata: PluginMetadata = PluginMetadata(
        "json", "1.0.0", capabilities=frozenset({"text", "records"})
    )

    def parse(self, payload: bytes) -> list[dict[str, str]]:
        value = json.loads(payload.decode("utf-8"))
        if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
            raise ValueError("JSON parser expects a list of objects")
        records: list[dict[str, str]] = []
        for row in value:
            if any(not isinstance(key, str) for key in row):
                raise ValueError("record keys must be strings")
            records.append({key: str(item) for key, item in row.items()})
        return records


@dataclass
class MemorySink:
    records: list[dict[str, str]] = field(default_factory=list)
    metadata: PluginMetadata = PluginMetadata(
        "memory", "1.0.0", capabilities=frozenset({"in-memory", "test"})
    )
    closed: bool = False

    def write(self, records: list[dict[str, str]]) -> None:
        if self.closed:
            raise RuntimeError("sink is closed")
        self.records.extend(dict(row) for row in records)

    def close(self) -> None:
        self.closed = True


@dataclass
class JsonLinesSink:
    stream: Any = field(default_factory=io.StringIO)
    metadata: PluginMetadata = PluginMetadata(
        "jsonl", "1.0.0", capabilities=frozenset({"text", "streaming"})
    )
    closed: bool = False

    def write(self, records: list[dict[str, str]]) -> None:
        if self.closed:
            raise RuntimeError("sink is closed")
        for record in records:
            self.stream.write(json.dumps(record, sort_keys=True) + "\n")

    def close(self) -> None:
        self.closed = True
        # The caller owns the stream; this plugin flushes but does not close it.
        flush = getattr(self.stream, "flush", None)
        if callable(flush):
            flush()


def build_default_registries() -> tuple[PluginRegistry[Parser], PluginRegistry[Sink]]:
    """Create isolated registries; no import-time global mutation."""
    parsers: PluginRegistry[Parser] = PluginRegistry("parser", PARSER_GROUP)
    sinks: PluginRegistry[Sink] = PluginRegistry("sink", SINK_GROUP)
    parsers.register(CsvParser.metadata, CsvParser)
    parsers.register(JsonRecordsParser.metadata, JsonRecordsParser)
    sinks.register(MemorySink.metadata, MemorySink)
    sinks.register(JsonLinesSink.metadata, JsonLinesSink)
    return parsers, sinks


class FetchKitPipeline:
    """A tiny dependency-injected pipeline; networking is intentionally absent."""

    def __init__(self, parsers: PluginRegistry[Parser], sinks: PluginRegistry[Sink]) -> None:
        self.parsers = parsers
        self.sinks = sinks

    def transform(self, payload: bytes, *, parser: str, sink: str) -> Sink:
        source = self.parsers.create(parser)
        primary_error: BaseException | None = None
        try:
            parsed = source.parse(payload)
        except BaseException as exc:
            primary_error = exc
            raise
        finally:
            # Parser instances may hold buffers or file handles. Teardown is
            # optional; when absent, close() is the conventional fallback.
            cleanup = getattr(source, "teardown", None)
            if not callable(cleanup):
                cleanup = getattr(source, "close", None)
            if callable(cleanup):
                try:
                    cleanup()
                except Exception as cleanup_exc:
                    if primary_error is not None:
                        primary_error.add_note(
                            f"parser cleanup also failed: {cleanup_exc!r}"
                        )
                    else:
                        raise

        target = self.sinks.create(sink)
        try:
            target.write(parsed)
        except Exception as exc:
            try:
                target.close()
            except Exception as cleanup_exc:
                exc.add_note(f"sink cleanup after write failure also failed: {cleanup_exc!r}")
            raise
        return target


def main() -> None:
    parsers, sinks = build_default_registries()
    # Explicitly opt in to third-party discovery; the built-in path works offline.
    parsers.add_entry_point_metadata()
    sinks.add_entry_point_metadata()
    parsers.freeze()
    sinks.freeze()
    pipeline = FetchKitPipeline(parsers, sinks)
    result = pipeline.transform(b"name,score\nAda,10\n", parser="csv", sink="memory")
    print(result.records)  # [{'name': 'Ada', 'score': '10'}]
    print(parsers.diagnostics())
    result.close()


if __name__ == "__main__":
    main()
```

### 7.3 Important implementation notes

- `build_default_registries()` creates a new registry per application/test. There is no process-wide mutable registry and no registration occurs merely by importing the module.
- The built-in CSV parser and JSON-record parser are examples; the in-memory and JSON-lines sinks are examples. They intentionally do not make network calls.
- `add_entry_point_metadata()` enumerates metadata, then stores `EntryPoint` objects as lazy loaders. The plugin target is imported only by `create(name)` after selection.
- Duplicate entry-point names fail instead of depending on distribution enumeration order. For an application that wants to override a built-in, require an explicit policy and log the source change; do not quietly make `replace=True` the default.
- `create()` wraps ordinary import/constructor failures in `PluginLoadError`, validates the contract, and calls an optional zero-argument `setup()` hook. Setup failures become `PluginInitializationError`; both errors preserve the original cause. If setup fails after acquiring resources, the registry attempts `teardown()` or `close()` and records cleanup failure as an exception note without masking the setup failure. A production system should distinguish a factory object from a zero-argument loader with a dedicated `PluginLoader` type rather than guessing from callability.
- The sample stores entry-point package version and API version as `unknown` until the target is loaded; the loaded object's `PluginMetadata` is then checked against the host API. `create(required_capabilities=...)` also checks required capability names against the loaded metadata, while contract tests must verify that the advertised behavior is real. This means lazy discovery cannot prove API compatibility before import unless the publisher supplies a separate, verifiable metadata manifest. Real production metadata should be obtained from the owning distribution and checked against an explicit API-version declaration. Never infer API compatibility from the package's distribution version.
- `FetchKitPipeline` is intentionally a minimal synchronous example. It demonstrates dependency injection and a stable seam, not a production streaming or transaction system. Parser cleanup (`teardown()` or `close()`) is attempted after parsing, including parse failure. On sink write failure, `close()` is attempted and any cleanup failure is attached to the primary exception rather than silently discarded. On success, the returned sink remains caller-owned and the caller must close it. A real pipeline should document partial writes and atomicity.

### 7.4 Running and discovering plugins

Run the built-in demonstration:

```bash
python fetchkit_plugins.py
```

List known metadata without importing target modules by calling `diagnostics()`; `add_entry_point_metadata()` enumerates entry-point metadata without loading targets. To demonstrate lazy loading, create a registry with a fake `EntryPoint` in a unit test or install a test-only distribution that advertises the `fetchkit.parsers` group. Do not add a fake plugin module to production startup merely to demonstrate the feature.

A third-party package can declare the `fetchkit.parsers` and `fetchkit.sinks` entry-point groups in its own `pyproject.toml`. The host should additionally verify distribution allow-list policy, API metadata, and contract tests before considering it approved. Discovery alone is not authorization.

### 7.5 Global registration versus dependency injection

| Design | Advantages | Costs / risks | Best fit |
|---|---|---|---|
| Global mutable registry | Convenient import-time decorators; easy access from anywhere | Hidden coupling, order dependence, test leakage, hard tenant/environment isolation, concurrency concerns | Small applications with a deliberately fixed built-in set |
| Dependency-injected registry | Explicit dependencies, per-app isolation, easy fake registries, straightforward tests | More wiring and constructor parameters | Libraries, services, multi-tenant apps, tests, configurable platforms |
| Global registry built once then frozen | Simple read path with stable contents | Still requires controlled startup imports; process-global configuration | A small single-application CLI with one plugin environment |

For a reusable library, prefer dependency injection. Let the application compose registries and pass them into `FetchKitPipeline`. Avoid a module-level `PARSERS` dictionary that changes whenever some unrelated module is imported. If a global is needed for convenience, keep the underlying registry API explicit, provide a documented registration phase, and freeze it before serving concurrent work.

### 7.6 Security model for `fetchkit`

The code above assumes built-ins are trusted. Entry points are disabled unless the application explicitly calls discovery. In production, approved third-party plugins should be installed through a controlled build/deployment process, pinned, allow-listed by distribution and plugin name, checked for API compatibility, and run with only the host process's necessary privileges. The core must not import arbitrary configured paths from untrusted input.

Untrusted plugins must run in a separate process or stronger sandbox with a narrow serialized protocol, timeouts, resource limits, and restricted filesystem/network access. Passing a restricted Python object to in-process plugin code is good least-privilege design, but not a security boundary: code can still reach ambient process capabilities. Record the selected plugin's canonical name, distribution/version, API version, and configuration fingerprint with outputs so a result can be reproduced.

## 8. Contract tests and exercises

### 8.1 Reusable parser contract

A contract test suite expresses the behavior a plugin author must satisfy. It should be distributed as a public test helper or documented fixture pattern—for example, `fetchkit.testing.PluginContractTests`—so third-party authors can run the same checks before publishing. Contract tests complement type checking: a `Protocol` can verify method shape, but not decoding rules, error semantics, determinism, or resource handling.

```python
from collections.abc import Callable
import pytest

from fetchkit_plugins import API_VERSION, CsvParser, JsonRecordsParser, MemorySink, PluginMetadata, Parser

ParserFactory = Callable[[], Parser]

@pytest.mark.parametrize("factory", [CsvParser, JsonRecordsParser])
def test_parser_contract_returns_list_of_string_records(factory: ParserFactory) -> None:
    parser = factory()
    assert isinstance(parser.metadata, PluginMetadata)
    assert parser.metadata.name
    assert parser.metadata.api_version == API_VERSION
    payload = (
        b"name,score\nAda,10\n"
        if parser.metadata.name == "csv"
        else b'[{"name":"Ada","score":10}]'
    )
    records = parser.parse(payload)
    assert isinstance(records, list)
    assert records == [{"name": "Ada", "score": "10"}]
    assert all(isinstance(record, dict) for record in records)
    assert all(isinstance(k, str) and isinstance(v, str) for row in records for k, v in row.items())


@pytest.mark.parametrize("factory", [MemorySink])
def test_sink_contract_accepts_records_and_can_close(factory) -> None:
    sink = factory([])
    records = [{"name": "Ada", "score": "10"}]
    sink.write(records)
    assert sink.records == records
    sink.close()
    assert sink.closed
    with pytest.raises(RuntimeError, match="closed"):
        sink.write(records)
```

For an external plugin, parameterize the same suite over factories discovered from the registry after applying the host's allow-list. Avoid automatically loading every discovered plugin in ordinary unit tests: a third-party plugin may be broken, slow, or unsafe. Keep a separate integration test job for approved installed plugins.

### 8.2 Registry, discovery, and failure tests

The following tests exercise duplicate registration, unknown names, discovery and loading failures, API/capability incompatibility, diagnostics without loading, and the pipeline. Save as `test_fetchkit_plugins.py` next to the implementation.

```python
import io
import pytest
from importlib.metadata import EntryPoint

import fetchkit_plugins
from fetchkit_plugins import (
    API_VERSION,
    CsvParser,
    DuplicatePluginError,
    FetchKitPipeline,
    JsonLinesSink,
    MemorySink,
    PluginContractError,
    PluginDiscoveryError,
    PluginInitializationError,
    PluginLoadError,
    PluginMetadata,
    PluginRegistry,
    RegistryFrozenError,
    UnknownPluginError,
    build_default_registries,
)


def test_duplicate_registration_is_rejected_with_sources() -> None:
    registry = PluginRegistry("parser")
    registry.register(CsvParser.metadata, CsvParser)
    duplicate = PluginMetadata("csv", "2.0", source="test-plugin")
    with pytest.raises(DuplicatePluginError, match="existing source"):
        registry.register(duplicate, CsvParser)


def test_unknown_plugin_lists_names_and_close_match() -> None:
    registry = PluginRegistry("parser")
    registry.register(CsvParser.metadata, CsvParser)
    with pytest.raises(UnknownPluginError, match="available: csv") as error:
        registry.create("cvs")
    assert "did you mean 'csv'?" in str(error.value)


def test_incompatible_api_is_rejected_at_registration() -> None:
    registry = PluginRegistry("parser")
    metadata = PluginMetadata("old", "0.9", api_version=API_VERSION - 1)
    with pytest.raises(PluginContractError, match="host requires API"):
        registry.register(metadata, CsvParser)


def test_freeze_rejects_mutation() -> None:
    registry = PluginRegistry("parser")
    registry.freeze()
    with pytest.raises(RegistryFrozenError):
        registry.register(CsvParser.metadata, CsvParser)


def test_loader_failure_is_wrapped_and_chained() -> None:
    def broken_factory():
        raise ImportError("optional dependency is missing")

    registry = PluginRegistry("parser")
    metadata = PluginMetadata("broken", "1.0", source="test")
    registry.register(metadata, broken_factory)
    with pytest.raises(PluginLoadError, match="broken") as error:
        registry.create("broken")
    assert isinstance(error.value.__cause__, ImportError)


def test_contract_failure_is_clear() -> None:
    registry = PluginRegistry("parser")
    metadata = PluginMetadata("bad", "1.0")
    registry.register(metadata, lambda: object())
    with pytest.raises(PluginContractError, match="must define callable parse"):
        registry.create("bad")


def test_metadata_rejects_malformed_capability_declarations() -> None:
    registry = PluginRegistry("parser")
    malformed = PluginMetadata("bad-capabilities", "1.0", capabilities=frozenset({"", "streaming"}))
    with pytest.raises(ValueError, match="capabilities must be a frozenset"):
        registry.register(malformed, CsvParser)


def test_required_capabilities_are_checked_against_loaded_metadata() -> None:
    registry = PluginRegistry("parser")
    registry.register(CsvParser.metadata, CsvParser)
    with pytest.raises(PluginContractError, match="lacks required capabilities: streaming"):
        registry.create("csv", required_capabilities=frozenset({"streaming"}))
    assert registry.diagnostics()[0]["state"] == "failed"


def test_csv_parser_rejects_rows_with_missing_or_extra_fields() -> None:
    parser = CsvParser()
    with pytest.raises(ValueError, match="different number of fields"):
        parser.parse(b"name,score\nAda\n")
    with pytest.raises(ValueError, match="different number of fields"):
        parser.parse(b"name,score\nAda,10,extra\n")
    with pytest.raises(ValueError, match="duplicate column names"):
        parser.parse(b"name,name\nAda,Byron\n")


def test_setup_failure_is_reported_as_initialization_error() -> None:
    class SetupFailureParser:
        metadata = PluginMetadata("setup-failure", "1.0")

        def parse(self, payload: bytes) -> list[dict[str, str]]:
            return []

        def setup(self) -> None:
            raise RuntimeError("configuration rejected")

    registry = PluginRegistry("parser")
    registry.register(SetupFailureParser.metadata, SetupFailureParser)
    with pytest.raises(PluginInitializationError, match="failed to initialize") as error:
        registry.create("setup-failure")
    assert isinstance(error.value.__cause__, RuntimeError)
    assert registry.diagnostics()[0]["state"] == "failed"
    assert registry.diagnostics()[0]["failure_stage"] == "setup"


def test_setup_failure_attempts_cleanup_without_hiding_primary_error() -> None:
    cleanup_calls = 0

    class PartialSetupParser:
        metadata = PluginMetadata("partial-setup", "1.0")

        def parse(self, payload: bytes) -> list[dict[str, str]]:
            return []

        def setup(self) -> None:
            raise RuntimeError("setup failed")

        def teardown(self) -> None:
            nonlocal cleanup_calls
            cleanup_calls += 1
            raise OSError("cleanup failed")

    registry = PluginRegistry("parser")
    registry.register(PartialSetupParser.metadata, PartialSetupParser)
    with pytest.raises(PluginInitializationError) as error:
        registry.create("partial-setup")
    assert isinstance(error.value.__cause__, RuntimeError)
    assert cleanup_calls == 1
    assert any("cleanup after setup failure" in note for note in error.value.__cause__.__notes__)


def test_loaded_entry_point_must_declare_compatible_api(monkeypatch) -> None:
    class MissingApiParser:
        metadata = PluginMetadata("external", "unknown", api_version=None)

        def parse(self, payload: bytes) -> list[dict[str, str]]:
            return []

    ep = EntryPoint(name="external", value="fetchkit_plugins:CsvParser", group="fetchkit.parsers")
    monkeypatch.setattr(EntryPoint, "load", lambda self: MissingApiParser)
    monkeypatch.setattr(fetchkit_plugins, "entry_points", lambda *, group: [ep])
    registry = PluginRegistry("parser", "fetchkit.parsers")
    registry.add_entry_point_metadata()
    with pytest.raises(PluginContractError, match="host requires API"):
        registry.create("external")


def test_pipeline_always_tears_down_parser_after_parse_failure() -> None:
    calls = 0

    class FailingParser:
        metadata = PluginMetadata("failing", "1.0")

        def parse(self, payload: bytes) -> list[dict[str, str]]:
            raise ValueError("bad payload")

        def teardown(self) -> None:
            nonlocal calls
            calls += 1

    parsers = PluginRegistry("parser")
    sinks = PluginRegistry("sink")
    parsers.register(FailingParser.metadata, FailingParser)
    pipeline = FetchKitPipeline(parsers, sinks)
    with pytest.raises(ValueError, match="bad payload"):
        pipeline.transform(b"invalid", parser="failing", sink="memory")
    assert calls == 1


def test_default_registries_are_isolated_and_pipeline_works() -> None:
    parsers, sinks = build_default_registries()
    second_parsers, _ = build_default_registries()
    assert parsers.names() == ("csv", "json")
    assert second_parsers.names() == parsers.names()
    pipeline = FetchKitPipeline(parsers, sinks)
    result = pipeline.transform(b"name,score\nAda,10\n", parser="csv", sink="memory")
    assert isinstance(result, MemorySink)
    assert result.records == [{"name": "Ada", "score": "10"}]
    result.close()


def test_pipeline_selects_jsonl_sink_without_sink_name_special_cases() -> None:
    parsers, sinks = build_default_registries()
    pipeline = FetchKitPipeline(parsers, sinks)
    result = pipeline.transform(b"name,score\nAda,10\n", parser="csv", sink="jsonl")
    assert isinstance(result, JsonLinesSink)
    assert result.stream.getvalue() == '{"name": "Ada", "score": "10"}\n'
    result.close()


def test_json_lines_sink_writes_deterministic_records() -> None:
    stream = io.StringIO()
    sink = JsonLinesSink(stream)
    sink.write([{"z": "2", "a": "1"}])
    sink.close()
    assert stream.getvalue() == '{"a": "1", "z": "2"}\n'


def test_diagnostics_do_not_construct_plugins() -> None:
    calls = 0

    def factory():
        nonlocal calls
        calls += 1
        return CsvParser()

    registry = PluginRegistry("parser")
    registry.register(CsvParser.metadata, factory)
    details = registry.diagnostics()
    assert details[0]["state"] == "registered"
    assert calls == 0


def test_entry_point_discovery_is_lazy_until_selected(monkeypatch) -> None:
    ep = EntryPoint(name="csv", value="fetchkit_plugins:CsvParser", group="fetchkit.parsers")
    monkeypatch.setattr(fetchkit_plugins, "entry_points", lambda *, group: [ep])
    registry = PluginRegistry("parser", "fetchkit.parsers")
    assert registry.add_entry_point_metadata() == ("csv",)
    assert registry.diagnostics()[0]["state"] == "discovered"
    # Listing metadata has not called EntryPoint.load(); create() does so on demand.
    assert isinstance(registry.create("csv"), CsvParser)
    assert registry.diagnostics()[0]["state"] == "ready"


def test_invalid_entry_point_metadata_fails_without_partial_registration(monkeypatch) -> None:
    candidates = [
        EntryPoint(name="valid", value="fetchkit_plugins:CsvParser", group="fetchkit.parsers"),
        EntryPoint(name=" invalid ", value="fetchkit_plugins:JsonRecordsParser", group="fetchkit.parsers"),
    ]
    monkeypatch.setattr(fetchkit_plugins, "entry_points", lambda *, group: candidates)
    registry = PluginRegistry("parser", "fetchkit.parsers")
    with pytest.raises(ValueError, match="surrounding whitespace"):
        registry.add_entry_point_metadata()
    assert registry.names() == ()


def test_entry_point_discovery_failure_is_distinct_and_chained(monkeypatch) -> None:
    def broken_discovery(*, group):
        raise OSError("metadata unavailable")

    monkeypatch.setattr(fetchkit_plugins, "entry_points", broken_discovery)
    registry = PluginRegistry("parser", "fetchkit.parsers")
    with pytest.raises(PluginDiscoveryError, match="failed to discover") as error:
        registry.add_entry_point_metadata()
    assert isinstance(error.value.__cause__, OSError)


def test_duplicate_entry_points_fail_without_partial_registration(monkeypatch) -> None:
    candidates = [
        EntryPoint(name="same", value="fetchkit_plugins:CsvParser", group="fetchkit.parsers"),
        EntryPoint(name="same", value="fetchkit_plugins:JsonRecordsParser", group="fetchkit.parsers"),
    ]
    monkeypatch.setattr(fetchkit_plugins, "entry_points", lambda *, group: candidates)
    registry = PluginRegistry("parser", "fetchkit.parsers")
    with pytest.raises(DuplicatePluginError, match="duplicate parser entry point"):
        registry.add_entry_point_metadata()
    assert registry.names() == ()
```

**Note on the entry-point test boundary:** the implementation deliberately separates metadata enumeration from `EntryPoint.load()`. A robust test can inject a fake `EntryPoint` object or use a temporary test distribution; do not mock `importlib.metadata` in a way that hides duplicate candidates. The code's duplicate detection must be verified against two entry points sharing one name, and production policy must identify both sources. A minimal package integration test is valuable when the project begins publishing actual plugins.

### 8.3 Suggested test matrix

| Concern | Test method | Failure that should be visible |
|---|---|---|
| Duplicate name | Register two sources with same name | Deterministic duplicate error with both sources |
| Unknown selection | Request misspelled name | Available names and optional close match |
| Contract shape | Instantiate plugin | Missing method or metadata rejected |
| Contract semantics | Shared parameterized tests | Wrong output type, invalid decoding behavior, nondeterministic behavior |
| Lazy loading | Diagnostics before `create()` | Loader was not invoked by listing |
| Load failure | Factory/entry point raises | Plugin-specific error retains chained cause |
| Initialization failure | Optional `setup()` raises | `PluginInitializationError` retains chained cause and state becomes failed |
| API compatibility | Register incompatible API version | Rejected before work is accepted |
| Lifecycle | Setup succeeds, run fails | Teardown is attempted and cleanup failure is reported |
| Isolation | Build two registries | Registering in one does not change the other |
| Thread safety | Concurrent registration/lookup stress test | No partial mutation or silent replacement |
| Security policy | Disallowed distribution/name | Plugin is not loaded at all |
| Reproducibility | Capture provenance with output | Result identifies implementation and version |

### 8.4 Exercises

1. Add a YAML parser without adding a hard dependency to the core. Make it an optional entry-point plugin and ensure its import error is reported only when selected.
2. Add `setup(context)` and `teardown()` to a sink protocol. Ensure setup failures prevent execution and teardown runs for successfully initialized sinks even if writing fails.
3. Add a plugin dependency graph and topological sort. Reject missing dependencies and cycles before initialization.
4. Add explicit aliases and a deprecation warning. Verify aliases resolve to the same canonical implementation and do not bypass allow-list policy.
5. Build a `fetchkit plugins list` command that reports source, API version, capabilities, and load state without importing every target.
6. Extend provenance with a stable configuration fingerprint. Ensure secrets are redacted and that plugin name/version/API are attached to each produced result.
7. Write a contract test kit that a separately distributed plugin can run without importing private `fetchkit` internals.

## 9. Common mistakes

These are the roadmap's required mistakes, with the engineering consequences made explicit.

### 9.1 Global mutable registries leaking across tests

Import-time decorators and process-wide dictionaries can retain registrations between tests. Test order then changes behavior, and parallel tests may race. Prefer a registry factory and dependency injection. If a global is unavoidable, use a fixture that snapshots and restores it, and do so in `try/finally`; avoid a blunt `.clear()` that removes built-ins or state owned by another test.

### 9.2 Import-time side effects with no documented import step

A decorator cannot register a class in a module that has never been imported. Hidden import requirements create empty registries and order-dependent startup. Document explicit imports or registration functions, or use entry-point metadata and lazy loading. Avoid scanning and importing arbitrary packages just to trigger side effects.

### 9.3 No error isolation for broken plugins

One optional plugin may fail because of an incompatible dependency, malformed metadata, or an exception during import. If all plugins are eagerly imported in one unguarded loop, a single broken extension can prevent the host from starting. Isolate discovery/load/validation/setup stages, report failures with plugin identity and chained causes, and define whether the application can continue without that plugin. Do not hide errors silently or catch `BaseException` indiscriminately.

### 9.4 Other recurring failure modes

- Treating discovery as authorization or security isolation.
- Letting duplicate names resolve by “last import wins.”
- Using a plugin package version as if it were the host API version.
- Instantiating every plugin merely to display a plugin list.
- Mutating a registry after concurrent request processing begins without a defined synchronization policy.
- Replacing a global registry in tests instead of injecting a fresh one.
- Exposing all host dependencies, credentials, and ambient process capabilities to plugin code.
- Treating type checking as a substitute for semantic contract tests.
- Using `pluggy` when a name-to-factory registry is sufficient, or using a registry when many ordered hook implementations are required.
- Recording only the plugin name and not the implementation version/configuration that produced a result.

## 10. Self-check questions with model answers

### 1. Compare four discovery mechanisms and choose one for a third-party-extensible library.

**Model answer:** Explicit registration is deterministic and ideal for built-ins. Decorator/import-side-effect registration is concise but requires importing each declaring module and can hide ordering. `pkgutil`/`importlib` scanning fits a controlled package namespace but imports discovered modules and executes code. Entry points let independently installed distributions advertise extensions in package metadata, and the host can enumerate metadata before loading only the selected target. For a third-party-extensible library, I would explicitly register built-ins and use entry points for approved third-party plugins. I would detect duplicate names, check allow-list policy, load lazily, validate API compatibility and contracts, isolate failures, and freeze the registry after startup. Entry points are discovery—not trust or sandboxing.

### 2. How do you test that every registered writer satisfies the writer contract?

**Model answer:** Define a public writer/sink contract in a `Protocol` and specify behavioral semantics: accepted input, output/side effects, error handling, lifecycle, resource ownership, and idempotency if required. Build a reusable pytest contract suite and parameterize it over approved plugin factories. Test metadata/API compatibility, valid and invalid input, write behavior, close/teardown, and failure paths. Run the suite against built-ins in normal CI and against installed third-party plugins in an isolated integration job. Do not blindly import every discovered plugin in ordinary unit tests. Type checking catches method-shape mismatches; runtime contract tests catch semantic violations.

### 3. Design the trust model for loading plugins from untrusted sources.

**Model answer:** Do not import untrusted plugin code into the host process. Treat importing, setup, execution, and teardown as arbitrary code execution with the host process's privileges. For trusted built-ins, use explicit registration. For approved third-party packages, control installation, pin versions, verify provenance, allow-list distributions and plugin identities, validate API compatibility, and grant only necessary capabilities. For untrusted/user-supplied code, run it out-of-process or in a stronger sandbox such as a constrained container or WASM runtime, with a narrow serialized RPC contract, timeouts, resource limits, and restricted filesystem/network access. A name allow-list, signature, or subprocess alone is not a complete sandbox. Record plugin provenance with outputs and never expose secrets unnecessarily.

## 11. Summary and completion checklist

A registry is the name-to-implementation mapping; a plugin architecture includes discovery, contracts, loading, validation, lifecycle, compatibility, security, diagnostics, and provenance. Keep registration, discovery, selection, loading, initialization, execution, and teardown distinct. For a reusable library, use explicit built-in registration plus entry-point discovery for approved third-party packages; load only selected plugins, fail clearly on collisions, validate API contracts, and freeze after startup when practical. Prefer dependency-injected registries over hidden mutable globals. Treat every plugin import as code execution, and isolate untrusted code outside the host process.

Before marking this lesson complete, verify that you can:

- [ ] Explain the difference between registration, discovery, selection, loading, initialization, execution, and teardown.
- [ ] Implement a typed registry with deterministic listing, duplicate protection, helpful lookup errors, and optional freeze semantics.
- [ ] Compare import side effects, explicit registration, scanning, configured paths, entry points, and hooks.
- [ ] Demonstrate lazy loading and preserve plugin-specific error context.
- [ ] Validate metadata, API versions, capabilities, configuration, and lifecycle.
- [ ] Write reusable parameterized contract tests and isolate registries in tests.
- [ ] Explain global state versus dependency injection and when `pluggy` is appropriate.
- [ ] State clearly that plugin loading executes code and design separate trust tiers.
- [ ] Record plugin provenance for reproducibility.
- [ ] Answer all three self-check questions without relying on the model answers.

## 12. Authoritative references

Use official documentation as the primary reference. Confirm current behavior against the Python version and packaging tools supported by the project.

1. Python `importlib.metadata` — entry points and distribution metadata: <https://docs.python.org/3/library/importlib.metadata.html>
2. Python `importlib` — import system and programmatic imports: <https://docs.python.org/3/library/importlib.html>
3. Python `pkgutil` — package/module discovery helpers: <https://docs.python.org/3/library/pkgutil.html>
4. Python `typing.Protocol` — structural typing: <https://docs.python.org/3/library/typing.html#typing.Protocol>
5. Python `abc` — abstract base classes: <https://docs.python.org/3/library/abc.html>
6. Python `difflib.get_close_matches` — close-match suggestions: <https://docs.python.org/3/library/difflib.html#difflib.get_close_matches>
7. Python Packaging User Guide — entry points and plugin discovery: <https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/>
8. PyPA entry points specification: <https://packaging.python.org/en/latest/specifications/entry-points/>
9. `pluggy` documentation — hook-based plugin systems: <https://pluggy.readthedocs.io/en/stable/>
10. Python Packaging User Guide — dependency and distribution security considerations: <https://packaging.python.org/en/latest/guides/>

The roadmap's intended sequence is preserved: Lesson 04's strategy/event ideas lead into registries and plugin contracts here; Lessons 06–08 then address public API design, backward compatibility/deprecation, and library error hierarchies. This lesson introduces only the compatibility and error distinctions needed to build a sound plugin boundary.
