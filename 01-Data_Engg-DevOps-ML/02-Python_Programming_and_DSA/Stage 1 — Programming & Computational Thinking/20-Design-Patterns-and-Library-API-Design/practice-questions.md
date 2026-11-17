# Module 1.20 — Design Patterns and Library API Design: Practice Questions

> **Purpose:** assess practical design judgment across the ten-lesson module, from recognizing a useful pattern to shipping a stable, testable Python library. The running case study is `fetchkit`, a data-fetching library with HTTP sources, cache and retry policies, parsers, output sinks, and plugin extensions.

## How to use this bank

- Attempt the questions before reading the answer key. Questions are numbered once, from 1 to 35; the answer key uses the same numbers.
- For code questions, submit executable code, imports and types, tests, and a short rationale. Unless stated otherwise, use Python 3.11+ and pytest; use deterministic fakes and no network access.
- State assumptions. More than one design can be correct: justify the choice against the stated requirements rather than naming a pattern for its own sake.
- In refactoring tasks, preserve observable behaviour first. Separate behaviour changes from behaviour-preserving refactors and run tests after each small step.
- Suggested scoring: 0 = absent/incorrect; 1 = partial; 2 = sound but incomplete; 3 = correct, tested, and justified. Use the question-specific rubric in the key where supplied. Do not grade a different but defensible design as wrong merely because it differs from the reference solution.

## Scope and prerequisites

This bank follows `roadmap-Design-Patterns-and-Library-API-Design.md` and the Stage 1 project tree. It assumes Python functions/classes, composition, inheritance, typing and `Protocol`, exceptions, modules/imports, pytest, decorators, and basic package/version concepts. `fetchkit` examples use fake transports so exercises are deterministic and credential-free.

### Difficulty levels

- **Beginner:** explain a defined concept, recognize a smell/pattern, or make a bounded design choice.
- **Intermediate:** implement a pattern or API and demonstrate behaviour with tests.
- **Advanced:** reason about compatibility, failure isolation, architectural boundaries, migration risk, or measurable maintainability trade-offs.

## Phase A — Foundations and pattern recognition

### Question 1 — Describe a pattern without treating it as a goal

**Skill:** design-pattern reasoning; pattern consequences. **Difficulty:** Beginner. **Format:** structured explanation. **Lessons:** 01.

Describe one design pattern you would consider for `fetchkit`. State (a) the recurring problem, (b) the pattern name and its essential structure, (c) the consequences and costs, and (d) one situation where you would not use it. Do not define it only by its class diagram.

### Question 2 — Classify patterns and Pythonic alternatives

**Skill:** pattern families and idiomatic Python. **Difficulty:** Beginner. **Format:** table with rationale. **Lessons:** 01–04.

Classify Factory, Adapter, Strategy, Observer, and Command as creational, structural, or behavioural. For each, name a Python construct or standard-library idea that may make a class-based implementation unnecessary, and give a concrete `fetchkit` example. Explain why “use a pattern” is not itself a requirement.

### Question 3 — Recognize the design in a snippet

**Skill:** code reading and pattern recognition. **Difficulty:** Beginner. **Format:** diagnosis and small rewrite. **Lessons:** 01, 04.

```python
def parse(payload: bytes, kind: str):
    if kind == "json":
        return parse_json(payload)
    if kind == "csv":
        return parse_csv(payload)
    raise ValueError(f"unknown kind: {kind}")
```

Assume `fetchkit` now supports six parser types, and downstream code adds branches whenever a parser is added. Propose two plausible designs (for example, a dispatch mapping and Strategy objects/functions). Give a criterion for choosing between them and one test for unknown parser names.

### Question 4 — Pattern or plain function?

**Skill:** appropriate abstraction; YAGNI; rule of three. **Difficulty:** Intermediate. **Format:** design decision. **Lessons:** 01, 04.

A single caller needs a custom retry delay calculation. There is one implementation, no plugin requirement, and no state. Should you introduce a `RetryStrategy` ABC, a class hierarchy, or pass a callable? Explain the simplest design now and what concrete evidence would justify changing it later. Include one counter-example where an interface would be justified earlier.

### Question 5 — SOLID, composition, and over-engineering review

**Skill:** design review. **Difficulty:** Intermediate. **Format:** code review bullets and revised sketch. **Lessons:** 01–03, 10.

Review this design: `FetchManager` inherits `RequestsClient`, `RetryMixin`, `CacheMixin`, `JSONParserMixin`, and `MetricsMixin`; its constructor creates a global cache and opens a connection. Identify at least four risks, connect them to relevant principles (such as single responsibility, dependency inversion, or composition over inheritance), and sketch a composition-based alternative. State one abstraction you would deliberately postpone.

## Phase B — Pattern implementation and testing

### Question 6 — Factory and named constructors

**Skill:** creational patterns and clear construction. **Difficulty:** Intermediate. **Format:** complete implementation and pytest tests. **Lessons:** 02.

Implement `HttpSource.from_env(environ: Mapping[str, str]) -> HttpSource` that reads `FETCHKIT_BASE_URL`, validates it, and creates a source without opening a network connection. Also implement `from_url(url: str)`. Use a small immutable dataclass or equivalent. Test valid input, missing configuration, invalid URL, and prove construction performs no I/O. Explain why a named constructor can be clearer than a constructor with many optional arguments.

### Question 7 — Builder invariants versus a simple constructor

**Skill:** builder selection and invariant enforcement. **Difficulty:** Intermediate. **Format:** comparison plus code. **Lessons:** 02.

`FetchPlan` contains a required source, parser, and sink, plus optional retry and cache policies. Implement either (a) a validated constructor/factory or (b) a builder that does not expose an invalid final plan. State why your chosen design fits the number of options and construction steps. Add tests proving a missing source/parser/sink cannot produce a usable plan. Explain when a builder would be unnecessary.

### Question 8 — Replace singleton state with dependency injection

**Skill:** singleton alternatives and test isolation. **Difficulty:** Intermediate. **Format:** refactor and tests. **Lessons:** 02, 10.

The current code uses `Settings.instance()` and a module-global cache. Refactor `Fetcher` to receive `Settings` and a cache through its constructor or factory. Show two fetchers configured differently in the same process and a test using an in-memory fake cache. Identify the hidden coupling and order-dependent test risk removed by the change.

### Question 9 — Adapter versus facade versus proxy

**Skill:** structural pattern selection and error semantics. **Difficulty:** Intermediate. **Format:** comparison and small implementations. **Lessons:** 03.

A vendor SDK returns `VendorResponse(status_code, body, vendor_headers)` and raises `VendorTimeout`. `fetchkit` wants its own `Response(status: int, body: bytes, headers: Mapping[str, str])`. Explain the distinct roles of an adapter, facade, and proxy. Implement a `VendorAdapter` that translates the response and translates only the vendor timeout into `FetchTimeout` using exception chaining. Add a test asserting `exc.value.__cause__` is the original vendor exception.

### Question 10 — Wrapper ordering and observable semantics

**Skill:** decorators/proxies, caching, retry, timeout. **Difficulty:** Advanced. **Format:** executable composition and tests. **Lessons:** 03.

Compose a fake transport with a retry wrapper, a cache wrapper, and a timeout boundary. State the order you choose and explain how it affects (a) whether cache hits trigger network calls, (b) whether retries repeat cache lookups, and (c) whether timeout applies to every attempt or the whole operation. Implement a minimal deterministic test that distinguishes at least two possible orders. Explicitly state any semantic choice rather than implying there is one universally correct order.

### Question 11 — Strategy with functions and a fake clock

**Skill:** behavioural patterns and sans-I/O seam awareness. **Difficulty:** Intermediate. **Format:** code and tests. **Lessons:** 04, 09.

Implement `retry_delay(attempt: int, policy: Callable[[int], float]) -> float` or an equivalent design that accepts a delay strategy. Supply fixed and exponential strategies, validate attempt/delay inputs, and test without sleeping. Explain why a callable is enough here and when a strategy object with state or configuration would be appropriate.

### Question 12 — Observer failure isolation and subscription lifetime

**Skill:** Observer semantics and resource lifecycle. **Difficulty:** Intermediate. **Format:** implementation, tests, and design note. **Lessons:** 04.

Implement a small event publisher with `subscribe()` and `publish(event)`. Choose and document what happens when one subscriber raises: abort publication, collect failures, or report them through a separate error hook. Ensure mutation of subscriptions during publication cannot corrupt iteration. Add tests for a failing subscriber, self-unsubscription, and subscriber lifetime/memory considerations. Do not silently swallow failures.

### Question 13 — Command pattern with undo/redo

**Skill:** Command and reversible operations. **Difficulty:** Advanced. **Format:** implementation and test suite. **Lessons:** 04.

Implement `InsertText` and `DeleteText` commands for a minimal text buffer. Each command must support `execute()` and `undo()`; add a history object with undo and redo. Test insertion, deletion, undo, redo, invalid ranges, and how a new command after undo affects the redo stack. State the invariant that makes each undo correct.

### Question 14 — Registry contract and plugin isolation

**Skill:** plugin architecture and contract tests. **Difficulty:** Advanced. **Format:** typed registry, fake plugin, contract tests. **Lessons:** 05.

Design a registry for named `Parser` implementations. Define a `Protocol` for the parser contract, reject duplicate names deterministically, and avoid a global registry that leaks state between tests. Write one reusable contract-test function and apply it to two parser implementations. Explain the difference between an explicit in-process registration API and package-entry-point discovery, and why loading an installed plugin is not the same as safely sandboxing untrusted code.

### Question 15 — Choose a discovery mechanism

**Skill:** plugin discovery and trust boundaries. **Difficulty:** Advanced. **Format:** comparison matrix and recommendation. **Lessons:** 05.

Compare these choices for `fetchkit`: explicit registration, built-in registry, configuration-based dotted import path, and package entry points. For each, assess discoverability, deployment friction, deterministic testing, security/trust assumptions, and operational failure modes. Recommend a default for a small library with third-party extensions, plus a fallback for applications that need deterministic startup. Include how a broken plugin is reported without making unrelated plugins unusable.

## Phase C — API and production-library design

### Question 16 — Public surface and `__all__`

**Skill:** public/private API design and API snapshots. **Difficulty:** Intermediate. **Format:** package layout and tests. **Lessons:** 06.

Propose a package layout for `fetchkit` with stable public imports, internal implementation modules, and a deliberate `__all__`. Show what `from fetchkit import Fetcher, FetchError` should expose. Write a public API test that checks the supported export set and explain why `__all__` alone does not make a symbol stable or private names impossible to import.

### Question 17 — Signature, types, and usability

**Skill:** API ergonomics and extension points. **Difficulty:** Intermediate. **Format:** API redesign with typed code. **Lessons:** 06.

Redesign `fetch(url, retries=3, cache=True, raw=False, timeout=None, parser=None, client=None)` for a library used by both simple callers and advanced applications. Provide a concise quick-start example first, then a typed API sketch. Explain which options belong in a policy/configuration object, which deserve named parameters, and which extension points should remain internal until a real use case exists. Avoid forcing every user to understand all internals.

### Question 18 — Compatibility and deprecation plan

**Skill:** semver judgement, warning policy, migration tests. **Difficulty:** Advanced. **Format:** change classification and migration plan. **Lessons:** 07.

For each change, classify it as breaking, likely compatible, or context-dependent, and justify: (a) remove an exported function, (b) add an optional keyword-only parameter, (c) change default retry count from 3 to 0, (d) change an exception superclass, (e) stop returning a vendor response type, (f) add a deprecation warning to an alias. Then outline a staged rename from `fetch_json()` to `fetch()`, including warning category/stacklevel, tests, changelog, migration instructions, and a removal release. Do not assume a signature-preserving default change is behaviour-compatible.

### Question 19 — Error taxonomy and retry classification

**Skill:** exception hierarchy, chaining, recovery semantics. **Difficulty:** Advanced. **Format:** exception definitions, decision table, tests. **Lessons:** 08.

Design a public `FetchError` hierarchy that distinguishes invalid request, timeout, transport failure, HTTP status failure, and parser failure. Define which errors are normally retryable and which should pass through. Implement translation from a low-level timeout with `raise FetchTimeout(...) from exc`. Test the exception type, useful attributes, and `__cause__`. Explain why retryability should not be inferred from matching message strings.

### Question 20 — What's wrong with this API? Boolean traps

**Skill:** API critique and migration-safe redesign. **Difficulty:** Intermediate. **Format:** defect list, corrected implementation, tests. **Lessons:** 06, 10.

**Flawed API:**
```python
def fetch(url: str, raw: bool = False, cache: bool = True,
          retry: bool = True, async_mode: bool = False) -> object:
    ...
```

**Scenario:** callers must remember the order and meaning of four flags; combinations can be contradictory, and adding another mode expands the state space. Identify the usability, typing, and maintenance defects. Rewrite the interface using named, typed choices (for example, separate sync/async entry points and explicit policy objects) without building an unnecessary framework. Add tests for the important combinations and explain how to migrate callers while preserving compatibility where practical.

### Question 21 — What's wrong with this API? Leaking vendor types

**Skill:** API boundary design and adapter use. **Difficulty:** Advanced. **Format:** critique, corrected implementation, contract tests. **Lessons:** 03, 06, 08.

**Flawed API:**
```python
import requests

def fetch(url: str) -> requests.Response:
    return requests.get(url)
```

**Scenario:** applications use `fetchkit` but now depend on `requests.Response`, `requests` exceptions, and vendor-specific headers. The library may need to change transport implementation. Identify the coupling and propose a stable `FetchResponse` type and transport adapter. Include status/body/header behavior, error translation and tests. Discuss which details may remain intentionally exposed if they are part of an explicit compatibility contract.

### Question 22 — What's wrong with this API? Silent default changes

**Skill:** compatibility analysis and deprecation/migration policy. **Difficulty:** Advanced. **Format:** release plan, tests, and communication. **Lessons:** 07.

**Flawed change:** `fetch(url, retries=3)` remains unchanged in the signature, but version 0.8 silently changes the default to `retries=0`. Existing users experience more transient failures. Identify why this can be breaking even though the signature is unchanged. Give a safer migration strategy, including how to represent “not explicitly supplied” if needed, warning policy, versioning, release notes, tests for omitted versus explicit values, and a defensible removal timeline.

### Question 23 — What's wrong with this API? Mutable defaults

**Skill:** Python semantics, state isolation, API correctness. **Difficulty:** Intermediate. **Format:** corrected implementation and regression tests. **Lessons:** 06, 10.

**Flawed API:**
```python
def fetch_many(urls: list[str], headers: dict[str, str] = {}) -> list[bytes]:
    headers.setdefault("User-Agent", "fetchkit")
    ...
```

**Scenario:** a header added during one call appears during later calls, and callers may mutate the same mapping. Explain the object-lifetime issue. Correct the implementation using an appropriate `None` sentinel or immutable default and copy/normalization semantics. Test that two calls do not share mutations and state whether the caller's mapping is mutated.

### Question 24 — What's wrong with this API? Misleading names

**Skill:** naming, units, side effects, return semantics. **Difficulty:** Intermediate. **Format:** critique and redesign. **Lessons:** 06, 10.

**Flawed API:**
```python
def refresh(url: str, timeout: float = 5.0) -> bool:
    # Performs a network request, retries twice, writes cache, then returns True
    # if a response object exists—even for HTTP 500.
    ...
```

**Scenario:** callers assume `refresh()` only updates local cache and interpret `True` as successful HTTP status; they also do not know whether `timeout` is seconds or milliseconds. Identify the concealed effects and ambiguous contract. Rename/redesign the function, document units and success semantics, define side-effect and error behavior, and show tests for a 200 response, a 500 response, and timeout.

### Question 25 — What's wrong with this API? Exceptions represented as strings

**Skill:** structured errors, typing, retry and caller recovery. **Difficulty:** Advanced. **Format:** corrected implementation and tests. **Lessons:** 08.

**Flawed API:**
```python
def fetch(url: str) -> bytes | str:
    try:
        return transport.get(url).body
    except TimeoutError:
        return "TIMEOUT"
    except OSError as exc:
        return f"ERROR: {exc}"
```

**Scenario:** a caller accidentally writes returned error text to a file and cannot reliably distinguish payload bytes from failure. Identify the contract and observability defects. Redesign using documented exceptions and a public hierarchy; preserve causes when translating. Show a caller that catches only retryable failures and tests that prove successful payloads cannot be confused with errors. Explain when a `Result` type could be appropriate, if the library explicitly chose that style.

### Question 26 — Sans-I/O retry planning and sync/async shells

**Skill:** separation of decisions from effects. **Difficulty:** Advanced. **Format:** typed implementation and deterministic tests. **Lessons:** 09.

Implement a pure retry planner that receives attempt number, failure classification, policy, and current time and returns a decision such as “stop” or “retry after N seconds.” It must not sleep, read the wall clock, or make HTTP requests. Show a synchronous driver using injected sleep/clock functions and describe an async shell using `asyncio.sleep`. Test the planner with a fake clock and no real delay. State which logic is shared and which belongs in each shell.

## Phase D — Refactoring and dependency boundaries

### Question 27 — Map smells to safe refactorings

**Skill:** anti-pattern recognition and prioritization. **Difficulty:** Intermediate. **Format:** table. **Lessons:** 10.

For each smell, choose a likely first refactoring, a possible target pattern (if justified), and the first test you would add: (a) scattered vendor calls, (b) repeated retry loops, (c) a 12-branch parser conditional, (d) a 300-line fetch function, (e) global mutable registry, (f) one interface with one implementation and no plausible second use case, (g) boolean flags plus a long parameter list/primitive obsession, (h) magic numbers and dead code, (i) mutable defaults, unexpected argument mutation, or swallowed exceptions, and (j) feature envy, shotgun surgery, divergent change, or a leaky vendor abstraction. Include at least one example of stringly typed code and deep inheritance. Map the applicable catalogue operations—Extract Function, Inline Function, Rename, Introduce Parameter Object, Extract Class, Move Function, Replace Conditional with Polymorphism, Replace Inheritance with Delegation, Introduce Special Case/Null Object, Replace Constructor with Factory, and Replace Magic Number with Constant—to a plausible smell. Explain why a pattern is conditional, not mandatory, and identify one case where doing nothing is rational.

### Question 28 — Characterization tests before refactoring

**Skill:** safe incremental change. **Difficulty:** Intermediate. **Format:** test-first plan and code. **Lessons:** 10.

A legacy `fetchkit` function retries twice, catches a timeout, returns `b""` on a 404, and caches the returned bytes. No written specification exists. Write characterization tests for the observed behaviour before changing the implementation. Then propose three small refactoring commits, with tests run at each step. Separate “preserve existing behavior” from any later decision to change 404 semantics.

### Question 29 — Break a circular dependency without breaking public imports

**Skill:** dependency boundaries and public API stability. **Difficulty:** Advanced. **Format:** before/after module graph and code sketch. **Lessons:** 06, 10.

`fetchkit.parsers` imports `fetchkit.client.Response`, while `fetchkit.client` imports `fetchkit.parsers.parse`. Design a way to break the cycle without needlessly breaking `from fetchkit import Response, Fetcher`. Consider moving shared types to a lower-level module, dependency inversion through a `Protocol`, and re-exporting public symbols in `__init__.py`. State the new dependency direction and tests/tools that can guard it.

### Question 30 — Is the abstraction worth keeping?

**Skill:** maintainability evidence and YAGNI. **Difficulty:** Advanced. **Format:** decision memo with measurable criteria. **Lessons:** 01, 05, 10.

A new `AbstractUniversalFetchProviderFactoryBuilder` has one implementation, forwards every call unchanged, and adds 11 files. The team claims it is “future proof.” Decide whether to keep, simplify, or remove it. List evidence to inspect (change frequency, independent variation, coupling, test friction, public surface, performance if relevant), define a small measurement plan, and record the rejected alternative in `DESIGN.md`. Add a technical-debt register entry with impact, likelihood, remediation cost, owner/trigger, and a decision to refactor now or defer. Do not invent measurements; distinguish current evidence from a proposed experiment.

### Question 31 — Refactor a god object using seams

**Skill:** characterization tests, seams, extraction and dependency injection. **Difficulty:** Advanced. **Format:** staged refactoring plan plus representative code. **Lessons:** 09, 10.

`FetchManager` currently loads configuration, constructs the vendor client, retries, parses JSON, writes files, emits events, and formats logs. Propose a sequence using the roadmap’s “tests → seams → extract → inject → replace” order. Include at least three concrete seams (such as injected transport, parser callable, sink protocol, clock/sleep), the first characterization tests, and a target decomposition. Explain how you would keep each pull request reviewable.

### Question 32 — Review a registry and import-time side effects

**Skill:** plugin lifecycle and architectural safety. **Difficulty:** Advanced. **Format:** code review and repair. **Lessons:** 05, 10.

Review this module:
```python
REGISTRY = {}
for plugin in discover_everything():
    REGISTRY[plugin.name] = plugin.load()
```

It executes on import, silently overwrites duplicate names, and a broken plugin prevents the package from importing. Propose explicit discovery/initialization, duplicate validation, per-plugin failure reporting, isolated tests, and a trust boundary. Explain what should happen by default on importing `fetchkit` and how applications opt into plugin loading.

### Question 33 — Code review: separate refactoring from behaviour changes

**Skill:** review quality, compatibility, test coverage. **Difficulty:** Advanced. **Format:** review comments and commit plan. **Lessons:** 07, 10.

A pull request extracts a retry helper, changes the default retry count from 3 to 0, replaces `FetchTimeout` with `RuntimeError`, and renames `fetch_json()`—all in one diff. Write prioritized review comments. Split the work into behaviour-preserving refactor and separately reviewed behaviour/API changes. Include required tests, compatibility/deprecation considerations, and what evidence would make the default change worthwhile. The author used an AI coding assistant to propose the patch: describe how you would independently inspect the diff, run characterization and regression tests, probe edge cases, and reject unsupported claims or broad rewrites. Add the debt item to a tracked register if deferred rather than fixed now.

### Question 34 — Architectural case study: v0.1 to v1.0

**Skill:** end-to-end architecture and trade-offs. **Difficulty:** Advanced. **Format:** architecture proposal, module graph, and tests. **Lessons:** 01–10.

Plan `fetchkit` from an initial v0.1 implementation to a v1.0 library with HTTP transport, cache/retry policies, parsers, sinks, and third-party plugins. Specify (a) public API and `__all__`, (b) chosen patterns and simpler alternatives rejected, (c) dependency direction and sans-I/O core, (d) error hierarchy/retry rules, (e) plugin contract/discovery and failure isolation, (f) compatibility/deprecation policy, (g) test layers including contract and public API tests, and (h) known trade-offs in `DESIGN.md`. Use fake dependencies in tests and identify the release gates that must pass before 1.0, including strict typing, the roadmap branch-coverage target, a public API snapshot, tested quick-start documentation, `import-linter` architecture contracts, mutation testing of the sans-I/O core, and a measured performance sanity benchmark for wrappers. Treat the benchmark as evidence to collect, not a result to assume.

### Question 35 — Final mastery: refactor a 300-line function

**Skill:** synthesis, safe refactoring, measurable improvement. **Difficulty:** Advanced. **Format:** staged plan, tests, evidence and retrospective. **Lessons:** 01, 06–10.

Choose a 300-line function from a project you can legally inspect, or use the `FetchManager` scenario in Question 31. First create characterization tests for representative normal, boundary, and failure cases. Then refactor it into three cohesive units without changing behaviour in the first sequence. Define before/after evidence such as cyclomatic complexity, imports/dependencies, changed files for a representative change, public surface, and test runtime. Explain how you will detect accidental behaviour changes, handle a circular dependency if discovered, and document one rejected abstraction. Do not claim a metric improved until measured.

---

# Six dedicated “What's wrong with this API?” exercises

These are Questions **20–25**. Each exercise is a separate review task and has its own answer-key entry. The six defects are intentionally distinct: do not treat them as interchangeable examples of “bad API design.”

# Complete answer key

The reference solutions demonstrate one defensible approach, not the only acceptable one. Evaluate against the stated requirements and contract. For implementation questions, award full credit only when the response includes relevant tests and explains material trade-offs.

## Phase A answers

### Answer 1

A strong answer names the forces and consequences. Example: **Adapter** solves the mismatch between a vendor transport contract and the `fetchkit` contract. A `VendorAdapter` translates inputs, outputs, and selected exceptions; it isolates vendor coupling. Costs include another layer and translation policy. It is not justified if the library has one internal call site and deliberately promises the vendor type as part of its public API. A pattern definition that gives only the class names earns partial credit.

**Evaluation (0–3):** problem and context (1); structure and consequences (1); sensible non-use case (1). Common error: claiming a pattern is inherently better than a direct function.

### Answer 2

| Pattern | Family | Pythonic option / example | Trade-off |
|---|---|---|---|
| Factory | Creational | function or `classmethod` such as `HttpSource.from_env()` | no factory class unless construction policy merits one |
| Adapter | Structural | function or small wrapper object | object is useful when translating a stable multi-method contract |
| Strategy | Behavioural | pass a callable for retry delay/parser choice | use an object when strategy has meaningful state or several operations |
| Observer | Behavioural | callback list or standard event mechanism | lifecycle and failure isolation still need explicit design |
| Command | Behavioural | callable for a simple one-shot action | command object is justified for undo, queueing, metadata, or replay |

The family describes the kind of design problem, not a mandate to use GoF class structures. **Evaluation:** all five families (1), relevant Python alternative/examples (1), trade-offs (1). Common error: calling every callback an Observer or every constructor function a Factory pattern implementation.

### Answer 3

A dispatch table is simplest when the variation is only a name-to-callable mapping:
```python
from collections.abc import Callable

Parser = Callable[[bytes], object]
PARSERS: dict[str, Parser] = {"json": parse_json, "csv": parse_csv}

def parse(payload: bytes, kind: str) -> object:
    try:
        parser = PARSERS[kind]
    except KeyError as exc:
        raise ValueError(f"unknown parser: {kind}") from exc
    return parser(payload)
```
If parsers require configuration, multiple methods, lifecycle, or capability metadata, a typed protocol and objects may be clearer. Test `parse(b"x", "yaml")` raises `ValueError` and that the error identifies the unknown key. Avoid broad exception handling that masks a parser’s own `KeyError`. **Evaluation:** two viable designs (1), criterion grounded in complexity/state (1), unknown-name test and correct error boundary (1).

### Answer 4

Pass a callable: `delay_for_attempt: Callable[[int], float]`. There is one stateless implementation and no plugin contract, so an ABC would add indirection without buying independent variation. Abstract earlier when a real boundary is required—for example, multiple independently maintained plugins must satisfy a shared contract or the strategy has several operations and lifecycle state. The rule of three is a heuristic, not a prohibition: a security boundary or independently deployed extension can justify an interface with one current implementation. **Evaluation:** simple choice (1), reason/YAGNI (1), plausible earlier-abstraction counterexample (1). “Always wait for three implementations” is too rigid.

### Answer 5

Risks include a fragile multiple-inheritance method-resolution order, coupled responsibilities, hidden global cache, import/constructor side effects, hard-to-isolate tests, and a subclass forced to inherit unrelated implementation details. Prefer composition: `Fetcher(transport, retry_policy, cache, parser, metrics)` or a factory that wires these dependencies at the application boundary. Use small protocols only at genuine seams. Postpone a universal plugin framework or abstract base hierarchy until an actual extension requirement appears. **Evaluation:** four concrete risks (1), coherent composition/dependency sketch (1), explicit postponed abstraction (1). A response that merely renames the god object does not address coupling.

## Phase B answers

### Answer 6

One reference implementation:
```python
from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlsplit

@dataclass(frozen=True)
class HttpSource:
    base_url: str

    def __post_init__(self) -> None:
        parts = urlsplit(self.base_url)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            raise ValueError("base_url must be an absolute HTTP(S) URL")

    @classmethod
    def from_url(cls, url: str) -> "HttpSource":
        return cls(base_url=url.rstrip("/"))

    @classmethod
    def from_env(cls, environ: Mapping[str, str]) -> "HttpSource":
        try:
            url = environ["FETCHKIT_BASE_URL"]
        except KeyError as exc:
            raise ValueError("FETCHKIT_BASE_URL is required") from exc
        return cls.from_url(url)
```
Tests should cover valid URL, missing key, invalid scheme/authority, and the absence of network calls (the code has no transport dependency). For full credit, validate before use and avoid reading ambient `os.environ` implicitly when a mapping is passed. **Common error:** open a connection during construction. **Evaluation:** typed constructors/invariant (1), three error/success cases (1), no-I/O test/rationale (1).

### Answer 7

A validated dataclass/factory is likely enough if the plan is created in one place and options are few; a builder is reasonable if there are many staged, optional steps or conditional configuration. For example:
```python
from dataclasses import dataclass
from typing import Protocol

class Source(Protocol):
    def fetch(self, key: str) -> bytes: ...
class Parser(Protocol):
    def parse(self, payload: bytes) -> object: ...
class Sink(Protocol):
    def write(self, value: object) -> None: ...

@dataclass(frozen=True)
class FetchPlan:
    source: Source
    parser: Parser
    sink: Sink
    retries: int = 0

    def __post_init__(self) -> None:
        if self.retries < 0:
            raise ValueError("retries must be non-negative")
```
The required fields prevent a plan without source/parser/sink. Add fake implementations and assert invalid retry counts fail. **Evaluation:** design fits construction complexity (1), required invariants/types (1), tests and reason not to use builder (1). A builder that permits `build()` with missing required parts is incorrect.

### Answer 8

```python
from typing import Protocol
from dataclasses import dataclass

class Cache(Protocol):
    def get(self, key: str) -> bytes | None: ...
    def set(self, key: str, value: bytes) -> None: ...

@dataclass(frozen=True)
class Settings:
    retries: int

class Fetcher:
    def __init__(self, settings: Settings, cache: Cache) -> None:
        self._settings = settings
        self._cache = cache
```
Use separate settings and fresh fake caches for two fetchers. Tests can configure retries 0 versus 2 without monkeypatching singleton state. Constructor injection exposes dependencies, allows parallel tests, and avoids hidden process-wide configuration. **Evaluation:** injection (1), independent instances/test fake (1), explanation of isolation (1). A singleton reset fixture is a weaker workaround, not the requested architectural fix.

### Answer 9

An **adapter** translates one interface to another; a **facade** simplifies a subsystem behind a narrower interface; a **proxy** controls access while generally preserving the target interface (for example, caching or authorization). Example:
```python
from dataclasses import dataclass
from collections.abc import Mapping

class FetchError(Exception): pass
class FetchTimeout(FetchError): pass

@dataclass(frozen=True)
class Response:
    status: int
    body: bytes
    headers: Mapping[str, str]

class VendorAdapter:
    def __init__(self, client: object) -> None:
        self._client = client

    def get(self, url: str) -> Response:
        try:
            result = self._client.get(url)
        except VendorTimeout as exc:
            raise FetchTimeout(f"request timed out: {url}") from exc
        return Response(result.status_code, result.body, dict(result.headers))
```
Assume `VendorTimeout` is imported from the fake/vendor transport in the exercise. For example, with a fake client returning `status_code=201`, `body=b"ok"`, and `headers={"X-Test": "yes"}`, assert the public response has `status == 201`, `body == b"ok"`, and the normalized header. For a raised vendor timeout, assert `exc.value.__cause__ is original`. Do not translate every vendor exception into timeout. **Evaluation:** distinguishes all three patterns (1), adapter mapping (1), precise exception test (1).

### Answer 10

There is no universal order; state a contract. One defensible choice is **timeout around each transport attempt**, retry around that attempt boundary, and cache outside retry: `Cache(Retry(Timeout(Transport)))`. Then cache hits bypass transport/retry, retry performs repeated attempts on cache miss, and each attempt has its own timeout. If timeout should bound the whole operation, a separate outer deadline is needed. Minimal executable sketch:
```python
from collections.abc import Callable

class FakeTimeout(Exception): pass

class Retry:
    def __init__(self, target, attempts: int) -> None:
        self.target, self.attempts = target, attempts
    def get(self, key: str) -> bytes:
        for attempt in range(self.attempts):
            try:
                return self.target.get(key)
            except FakeTimeout:
                if attempt + 1 == self.attempts:
                    raise
        raise AssertionError("unreachable")

class Cache:
    def __init__(self, target) -> None:
        self.target, self.items = target, {}
    def get(self, key: str) -> bytes:
        if key not in self.items:
            self.items[key] = self.target.get(key)
        return self.items[key]

class SequenceTransport:
    def __init__(self, outcomes: list[bytes | Exception]) -> None:
        self.outcomes, self.calls = list(outcomes), 0
    def get(self, key: str) -> bytes:
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

transport = SequenceTransport([FakeTimeout(), b"ok"])
client = Cache(Retry(transport, attempts=2))
assert client.get("k") == b"ok" and transport.calls == 2
assert client.get("k") == b"ok" and transport.calls == 2
```
This sketch models per-attempt timeout by letting the underlying transport raise `FakeTimeout`; a real timeout wrapper would enforce the deadline. Tests should count transport calls and use deterministic timeout fakes. **Evaluation:** order stated (1), explains at least two semantic consequences (1), test distinguishes orders (1). Merely nesting wrappers without describing observable behaviour is incomplete.

### Answer 11

```python
from collections.abc import Callable

def fixed_delay(_: int) -> float:
    return 0.25

def exponential_delay(attempt: int) -> float:
    if attempt < 1:
        raise ValueError("attempt must be >= 1")
    return min(0.25 * (2 ** (attempt - 1)), 8.0)

def retry_delay(attempt: int, policy: Callable[[int], float]) -> float:
    if attempt < 1:
        raise ValueError("attempt must be >= 1")
    delay = policy(attempt)
    if delay < 0:
        raise ValueError("delay must be non-negative")
    return delay
```
Tests check attempts 1–4, cap, invalid attempts, and negative policy output; no sleeping occurs. A callable fits one operation with no state. An object is appropriate for multi-method policy, stateful jitter source, or inspectable configuration. **Evaluation:** implementation/validation (1), deterministic tests (1), abstraction rationale (1).

### Answer 12

A defensible publisher snapshots the subscriber collection before iteration and makes failures observable. One minimal policy is to continue and return collected exceptions:
```python
from collections.abc import Callable
from dataclasses import dataclass

@dataclass(frozen=True)
class Event:
    name: str

Subscriber = Callable[[Event], None]

class Publisher:
    def __init__(self) -> None:
        self._subscribers: list[Subscriber] = []
    def subscribe(self, callback: Subscriber) -> Callable[[], None]:
        self._subscribers.append(callback)
        def unsubscribe() -> None:
            if callback in self._subscribers:
                self._subscribers.remove(callback)
        return unsubscribe
    def publish(self, event: Event) -> list[Exception]:
        failures: list[Exception] = []
        for callback in tuple(self._subscribers):
            try:
                callback(event)
            except Exception as exc:
                failures.append(exc)
        return failures
```
Tests should verify that a later subscriber runs after an earlier failure, self-unsubscription does not corrupt the active snapshot, and a returned unsubscribe function releases subscriptions. Never silently discard exceptions. If abort-on-first-error is the intended contract, test and document that instead. Weak references may help for bound-method subscribers, but explicit unsubscribe tokens are simpler and deterministic. **Evaluation:** explicit failure policy (1), safe iteration/lifecycle (1), tests and memory explanation (1).

### Answer 13

A command captures enough state to reverse its own operation. A compact reference implementation for insertion and history is:
```python
from dataclasses import dataclass

@dataclass
class InsertText:
    index: int
    text: str
    def execute(self, buffer: list[str]) -> None:
        if not 0 <= self.index <= len(buffer):
            raise IndexError("insert index out of range")
        buffer[self.index:self.index] = list(self.text)
    def undo(self, buffer: list[str]) -> None:
        end = self.index + len(self.text)
        if buffer[self.index:end] != list(self.text):
            raise RuntimeError("buffer changed outside command history")
        del buffer[self.index:end]

class History:
    def __init__(self, buffer: list[str]) -> None:
        self.buffer = buffer
        self.undo_stack: list[InsertText] = []
        self.redo_stack: list[InsertText] = []
    def execute(self, command: InsertText) -> None:
        command.execute(self.buffer)
        self.undo_stack.append(command)
        self.redo_stack.clear()
    def undo(self) -> None:
        if not self.undo_stack:
            raise IndexError("nothing to undo")
        command = self.undo_stack.pop()
        command.undo(self.buffer)
        self.redo_stack.append(command)
    def redo(self) -> None:
        if not self.redo_stack:
            raise IndexError("nothing to redo")
        command = self.redo_stack.pop()
        command.execute(self.buffer)
        self.undo_stack.append(command)
```
A complete reference also needs `DeleteText`; the implementation below records the exact removed text before mutation and restores it at the original index:
```python
@dataclass
class DeleteText:
    index: int
    count: int
    removed: str = ""
    def execute(self, buffer: list[str]) -> None:
        if self.count < 0 or self.index < 0 or self.index + self.count > len(buffer):
            raise IndexError("delete range out of bounds")
        self.removed = "".join(buffer[self.index:self.index + self.count])
        del buffer[self.index:self.index + self.count]
    def undo(self, buffer: list[str]) -> None:
        if not 0 <= self.index <= len(buffer):
            raise IndexError("restore index out of range")
        buffer[self.index:self.index] = list(self.removed)
```
For either command, test that execute → undo restores the original buffer and execute → undo → redo restores the post-execute buffer. Also test invalid ranges, empty history, and that a new command after undo clears redo. Avoid reversing strings blindly when indices or repeated text make that ambiguous. **Evaluation:** correct state capture (1), stack semantics (1), edge-case tests (1). A command object is justified here because actions need history and inverse operations.

### Answer 14

Example contract:
```python
from typing import Protocol

class Parser(Protocol):
    def parse(self, payload: bytes) -> object: ...

class ParserRegistry:
    def __init__(self) -> None:
        self._items: dict[str, Parser] = {}

    def register(self, name: str, parser: Parser) -> None:
        if not name.strip():
            raise ValueError("name must not be empty")
        if name in self._items:
            raise ValueError(f"parser already registered: {name}")
        self._items[name] = parser

    def get(self, name: str) -> Parser:
        try:
            return self._items[name]
        except KeyError as exc:
            raise LookupError(f"unknown parser: {name}") from exc
```
Each test creates a new registry. A reusable contract test checks valid input, malformed input policy, and deterministic output for each implementation. Explicit registration is easy to reason about; entry points suit installed third-party extensions but require discovery/loading error handling. Python plugins execute with process privileges; entry points do not sandbox hostile code. **Evaluation:** contract/duplicate handling (1), isolation and reusable tests (1), discovery/trust distinction (1).

### Answer 15

- **Explicit registration:** best determinism and test control; caller must register.
- **Built-in registry:** simple for built-ins; avoid mutable global state or provide a fresh registry per app/test.
- **Dotted import path:** flexible but config errors/import side effects/security/troubleshooting are harder.
- **Package entry points:** suitable for third-party installed extensions; discovery is environment-dependent and loading can fail.

Recommend built-ins plus explicit registration as the deterministic core; offer entry-point discovery as an opt-in or clearly documented startup action. Isolate each plugin load, report plugin name and cause, and make fail-fast versus continue-on-error policy explicit. Do not claim untrusted plugins are sandboxed. **Evaluation:** comparison covers requested dimensions (1), justified recommendation (1), safe failure/trust policy (1).

## Phase C answers

### Answer 16

One layout:
```text
fetchkit/
  __init__.py        # Fetcher, FetchResponse, FetchError; __all__
  _client.py         # implementation
  _transport.py      # transport adapters
  _errors.py         # stable error types, if publicly re-exported
  parsers.py         # supported parser interface
```
`__all__ = ["Fetcher", "FetchResponse", "FetchError"]` documents star-import exports, and public API tests assert names and selected signatures. A symbol can still be imported from an internal module and `__all__` does not itself promise stability; stability comes from documented support policy and compatibility tests. **Evaluation:** coherent layout/exports (1), test strategy (1), limitation explained (1).

### Answer 17

Keep the common path short, for example `fetch(url)`; expose advanced behaviour through typed policy/configuration or a configured `Fetcher`. Separate `fetch()` and `async_fetch()` if they have genuinely different execution semantics rather than a boolean mode. Use keyword-only options for individual common, stable choices; use a `RetryPolicy`/`FetchConfig` when settings form a cohesive concept. Avoid a public parameter for every internal component until extension needs are real. A good answer includes a quick-start snippet that reads naturally and tests its documented behavior. **Evaluation:** usability (1), typed/extension design (1), restrained abstraction and example (1). One giant `**kwargs` bag is not a substitute for a contract.

### Answer 18

(a) Removing an exported function: breaking. (b) Adding an optional keyword-only parameter: usually compatible, but check wrappers/subclasses/introspection and whether the name collides with callers using `**kwargs`. (c) Retry default 3→0: behaviour-breaking for some users. (d) Changing an exception superclass: context-dependent and often breaking for catch clauses. (e) Stop returning vendor response: likely breaking if public return type was documented/used. (f) Add warning to alias: usually compatible but warnings-as-errors can affect CI; choose category and stacklevel carefully.

For rename, add `fetch()` while retaining `fetch_json()` as a wrapper; emit `DeprecationWarning` with `stacklevel=2`; test both behavior and warning; document replacement and a target removal release; update changelog/migration guide; remove only after the stated policy/version window. **Evaluation:** classifications and nuance (1), staged migration (1), tests and communication (1). A signature-only diff misses behavioural compatibility.

### Answer 19

A possible hierarchy:
```python
class FetchError(Exception): pass
class InvalidRequest(FetchError): pass
class TransportError(FetchError): pass
class FetchTimeout(TransportError): pass
class HTTPStatusError(FetchError):
    def __init__(self, status: int, message: str = "HTTP status failure") -> None:
        super().__init__(message)
        self.status = status
class ParseError(FetchError): pass
```
Normally retry transient timeout/selected transport failures and perhaps selected status codes according to policy; do not retry invalid input or deterministic parse errors by default. HTTP status retry decisions depend on status and idempotency, not just class. Translate low-level exceptions with `raise FetchTimeout(...) from exc`; assert type, status attributes, and `__cause__`. Structured types support reliable catch logic and diagnostics; string matching breaks when wording changes. **Evaluation:** hierarchy (1), recovery policy nuance (1), chaining tests (1).

### Answer 20 — Boolean traps

Problems: multiple independent flags create a combinatorial set of states, call sites such as `fetch(url, True, False, True, False)` are unreadable, `object` return type cannot describe raw/parsed results, sync/async should not be hidden as a mode flag, and invalid combinations are representable. One possible redesign:
```python
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class FetchOptions:
    use_cache: bool = True

class Parser(Protocol):
    def parse(self, body: bytes) -> object: ...

class Fetcher:
    def fetch_bytes(self, url: str, *, options: FetchOptions | None = None) -> bytes: ...
    def fetch_parsed(self, url: str, *, parser: Parser,
                     options: FetchOptions | None = None) -> object: ...

async def async_fetch_bytes(url: str, *, options: FetchOptions | None = None) -> bytes: ...
```
These are API sketches; complete implementation must define transport and errors. Use explicit policy types when retry/cache choices grow; separate entry points only if sync/async are genuinely different. Keep the old function as a compatibility wrapper if already public, deprecate ambiguous modes with migration examples, and test each supported path plus rejected invalid configurations. **Evaluation:** identifies flags/type-state issue (1), usable typed replacement (1), compatibility and tests (1). Simply making every flag keyword-only improves readability but may not solve invalid combinations.

### Answer 21 — Leaking vendor types

The function couples public callers to `requests`, its response attributes and exceptions. Define a stable `FetchResponse` dataclass with documented fields and an adapter that translates vendor responses and selected exceptions. Tests use a fake vendor client and assert only the public contract; contract tests should run against each supported adapter. Avoid leaking `requests.Response` from either annotations or runtime returns. If exposing vendor types is an intentional design goal, document it as a dependency and compatibility commitment instead of pretending the transport is replaceable. **Evaluation:** identifies concrete coupling (1), stable boundary and adapter (1), tests plus explicit trade-off (1). Do not return a locally fabricated “response-like” object without a specified contract.

### Answer 22 — Silent default change

The unchanged signature hides changed observable behaviour: transient failures that previously succeeded may now escape, changing reliability and request volume. Safer choices include a major-version change with prominent migration guidance, or a staged explicit policy: preserve default while introducing an opt-in setting, warn only where a deprecation is genuinely planned, and change the default at a documented release boundary. Use a sentinel if the implementation must distinguish omission from explicit `retries=3`:
```python
_UNSET = object()
def fetch(url: str, *, retries: int | object = _UNSET) -> bytes:
    if retries is _UNSET:
        effective_retries = 3  # current compatibility default
    else:
        effective_retries = int(retries)
    ...
```
In production typing, prefer a private sentinel with a precise overload/type alias rather than exposing `object` as a broad public type. Validate explicit values rather than coercing arbitrary inputs with `int()` (which accepts values such as `True` and numeric strings). Test omitted, explicit old value, explicit new value, and invalid types/ranges. State a removal timeline tied to the project’s release policy, not an arbitrary date. **Evaluation:** behavioural break recognized (1), staged plan (1), omitted/explicit tests and communication (1).

### Answer 23 — Mutable defaults

Function defaults are created once at function definition; the same dict is reused across calls. Corrected version:
```python
from collections.abc import Mapping

def fetch_many(urls: list[str], headers: Mapping[str, str] | None = None) -> list[bytes]:
    effective_headers = dict(headers) if headers is not None else {}
    effective_headers.setdefault("User-Agent", "fetchkit")
    # Perform fetches with effective_headers; return bodies.
    return []
```
A complete implementation delegates each URL to an injected transport and returns its bodies. A minimum regression test can use a fake transport that records a copy of each headers mapping; call `fetch_many(["a"], caller_headers)` twice and assert (1) each request has `User-Agent: fetchkit`, (2) neither recorded mapping gains unrelated changes from the other call, and (3) `caller_headers` is unchanged. The copy is important even when a caller supplied a mutable mapping. **Evaluation:** lifetime bug explained (1), safe default/copy (1), isolation tests (1). Using `{}` and clearing it afterward is brittle and still shares state.

### Answer 24 — Misleading names

`refresh` hides a network request, retries, and cache writes; `bool` means response object exists rather than successful HTTP status; timeout units are unstated. Prefer a name such as `fetch_and_cache()` or separate `fetch()` from cache policy. Document timeout in seconds, define HTTP error behavior (for example, return a response for all statuses or raise a typed `HTTPStatusError`), and reserve a boolean for a genuinely boolean predicate. Test 200, 500, and timeout, including whether cache is written on failure. **Evaluation:** names/effects/units identified (1), coherent contract (1), tests (1). Merely renaming `timeout` to `timeout_seconds` without defining success semantics is incomplete.

### Answer 25 — Exceptions as strings

Strings make the return type ambiguous and prevent reliable error classification; they can be mistaken for payloads and discard traceback/cause context. Prefer raising `FetchTimeout`/`TransportError` and preserve causes:
```python
class FetchError(Exception): pass
class FetchTimeout(FetchError): pass
class TransportError(FetchError): pass

def fetch(url: str, transport) -> bytes:
    try:
        return transport.get(url).body
    except TimeoutError as exc:
        raise FetchTimeout(f"timed out fetching {url}") from exc
    except OSError as exc:
        raise TransportError(f"transport failed for {url}") from exc
```
Caller:
```python
try:
    payload = fetch(url, transport)
except FetchTimeout:
    schedule_retry(url)
```
Tests assert that a successful fake transport returns exactly `b"payload"`, a timeout raises `FetchTimeout` with the original timeout in `__cause__`, and an `OSError` raises `TransportError` with its cause preserved; no failure path returns a string payload. A `Result`/sum type can be valid if chosen consistently and documented, but must distinguish `Ok[bytes]` from `Err[FetchError]` without magic strings. **Evaluation:** contract defect (1), typed/chained solution (1), safe caller/tests and alternative nuance (1).

### Answer 26

Keep planning pure: inputs contain attempt count, failure classification, policy and an explicit current time; output contains retry/stop plus delay. A minimal pure planner:
```python
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass(frozen=True)
class RetryDecision:
    retry: bool
    delay_seconds: float
    next_time: datetime | None

def plan_retry(*, attempt: int, max_attempts: int, retryable: bool,
               delay_seconds: float, now: datetime) -> RetryDecision:
    if attempt < 1 or max_attempts < 1:
        raise ValueError("attempt and max_attempts must be >= 1")
    if delay_seconds < 0:
        raise ValueError("delay_seconds must be non-negative")
    should_retry = retryable and attempt < max_attempts
    next_time = now + timedelta(seconds=delay_seconds) if should_retry else None
    return RetryDecision(should_retry, delay_seconds if should_retry else 0.0, next_time)
```
The sync driver injects `clock()` and `sleep(seconds)`; an async driver awaits `asyncio.sleep(seconds)` but calls the same decision logic. Minimum assertions: with `attempt=1`, `max_attempts=3`, retryable failure, `delay_seconds=2.0`, and fixed `now`, the decision is retry with `next_time == now + timedelta(seconds=2)`; at `attempt=3` or for a non-retryable failure, it stops with `next_time is None`; negative delay and attempt zero raise `ValueError`. The sync driver’s fake sleeper records `[2.0]` without waiting; the async shell uses `await asyncio.sleep(...)` and must not call blocking `time.sleep`. Ensure max-attempt and retryable-error rules are explicit. **Evaluation:** pure planner (1), effectful shells injected (1), deterministic tests and sync/async separation (1). A function that sleeps inside the planner is not sans-I/O.

## Phase D answers

### Answer 27

| Smell | Likely first refactoring | Possible target | First test |
|---|---|---|---|
| Vendor calls scattered | Extract/wrap transport calls | Adapter | response and exception translation |
| Repeated retry loops | Extract shared retry decision | function/decorator/policy | attempt count and terminal error |
| Parser conditional | Extract dispatch mapping | Strategy/registry if justified | every supported key plus unknown key |
| 300-line function | Characterization tests, extract cohesive functions | several collaborators only after responsibilities emerge | normal, boundary, failure outputs |
| Global mutable registry | inject registry/construct per app | Registry | no cross-test leakage and duplicate handling |
| One useless interface | Inline Function / remove abstraction | none | existing behavior stays the same |
| Boolean flags, long parameter list, primitive obsession | Introduce Parameter Object; replace booleans with named options/enum where it clarifies valid states | config value object, only if cohesive | omitted/default and supported combinations |
| Magic numbers or dead code | Replace Magic Number with Constant; delete code only after proving it is unreachable/unused | usually none | boundary/constant behavior and import/API checks |
| Mutable defaults or mutated arguments | use `None`/immutable default and copy inputs; extract normalization | none required | independent calls and unchanged caller input |
| Swallowed exceptions | expose documented exception or explicit error hook; do not use `except Exception: pass` | error hierarchy only if callers need categories | failure propagates or is reported as promised |
| Feature envy / shotgun surgery / divergent change | Move Function; Extract Class when responsibilities cohere; separate modules by reason to change | adapter/facade only if a real boundary exists | behavior of the moved responsibility and affected callers |
| Stringly typed code / deep inheritance / leaky abstraction | use enum/dataclass at a real domain boundary; Replace Inheritance with Delegation; wrap vendor API | registry/adapter only when variation or isolation warrants it | valid/invalid values, public contract, and dependency direction |

Do nothing when code is stable, clear, low-risk and unlikely to change; a refactor has cost. **Evaluation:** sensible mappings across the listed smells (2), first tests and sequencing (1); credit alternate refactorings if defended.

### Answer 28

Characterization tests must capture the current contract, including the surprising empty bytes for 404, two retries, timeout handling and cache contents. Use a fake transport with a predetermined sequence and an in-memory cache; do not hit the network. Three commits: (1) tests and fakes only; (2) extract retry decision/loop without changing semantics; (3) inject transport/cache and move parsing or cache responsibilities behind a seam. Run the full suite after every commit. A later behaviour change for 404 requires a separate decision, tests, compatibility note and migration path. **Evaluation:** captures normal/boundary/failure behaviour (1), safe incremental sequence (1), separates behaviour change (1). Tests that assert only the “desired” new behavior do not characterize the legacy system.

### Answer 29

Move shared response/value types into a low-level module such as `fetchkit.types` that does not import client or parsers. Let `client` depend on parser protocol/Callable; parser implementation depends only on the low-level types. Public `fetchkit.__init__` re-exports `Response` and `Fetcher` to preserve imports. Graph: `client -> parser contract`, `parsers -> types`, `client -> types`, and public facade -> modules; no `parsers -> client`. Add import smoke/API tests and an `import-linter` contract forbidding low-level modules from importing client. **Evaluation:** cycle removed with correct direction (1), public imports preserved (1), regression guard (1). Moving code without checking dependency direction can leave the cycle intact.

### Answer 30

Default to simplify/remove unless the abstraction represents a real stable boundary or required variation. Inspect call sites, change frequency, independent implementations, dependency coupling, test friction, public API impact, and performance only if relevant. Measure a representative change: files touched, amount of adapter/boilerplate code, tests needed, and time/complexity—not vague “future proofing.” Record current evidence separately from planned measurement. `DESIGN.md` should record the rejected wrapper and conditions that would justify reintroducing an interface. The debt register should name the impact and likelihood, a rough remediation cost, an owner or review trigger, and why the item is accepted now; do not treat the register as permission to ignore risk. **Evaluation:** evidence-based decision (1), measurable plan and debt decision (1), explicit alternative/trade-off (1). Invented performance gains receive no credit.

### Answer 31

Sequence: (1) characterize public outputs, retry counts, cache writes, parser errors, events and logs that callers rely on; (2) introduce seams around transport, clock/sleep, parser and sink while keeping behavior; (3) extract cohesive retry and parse/cache operations; (4) inject dependencies in constructors/factory; (5) replace vendor-specific calls behind adapter; (6) only then consider strategy/registry. Use small PRs each with focused tests and unchanged public API where possible. A seam is a place where behavior can be substituted for tests or migration; it is not necessarily an interface class. **Evaluation:** safe order (1), three concrete seams (1), reviewable commits and tests (1).

### Answer 32

Importing `fetchkit` should not discover/load arbitrary plugins or perform network/file-system effects. Provide an explicit `load_entry_points()`/`discover_plugins()` call or application startup factory; validate names and report duplicates; isolate each plugin’s load error with plugin identity and chained cause; make continue/fail-fast policy explicit. Use a fresh registry for each app/test. Document that loading code executes with process privileges and only load trusted installed packages. **Evaluation:** removes import-time side effects (1), deterministic duplicate/error handling (1), lifecycle/trust/isolation (1). Silent overwrite is unacceptable because registration order changes behavior invisibly.

### Answer 33

Priority review comments: the PR mixes behavior and public API changes, making regressions hard to isolate; retry default change alters reliability; replacing `FetchTimeout` breaks caller exception handling; rename needs alias/deprecation. Suggested commits: (1) characterization tests; (2) extract retry helper with unchanged default/errors; (3) add new name and deprecated alias with warning/migration docs; (4) separately propose retry-default change with evidence, release policy and explicit opt-in; (5) if changing exception types, maintain subtype/alias compatibility where possible and document migration. Tests cover retry attempts, old/new names and warnings, exception catches, and public API snapshot. For the AI-proposed patch, review the actual diff line-by-line, independently reproduce the behavior with characterization tests, add tests for edge/error cases, run the project's formatter/type checker/test suite, and verify each claimed improvement against measurements. Do not accept generated explanations as evidence; keep changes small enough for human review. If a fix is deferred, record the risk, owner, and trigger in the debt register. **Evaluation:** prioritized review (1), separable plan (1), compatibility/test and independent verification specifics (1).

### Answer 34

Strong proposal: expose a small documented facade (`Fetcher`, `FetchResponse`, stable `FetchError` family), keep implementation modules private, and assert public exports. Core retry planning/parsing is deterministic and sans-I/O; transport, sleep, clock, cache and sinks are injected. Use an adapter for vendor transport; a callable for simple strategy; a registry for explicit parser plugins only if extension is required; observer/command only where events/history semantics justify them. Errors distinguish invalid input, timeout, transport, status and parse failures with chained causes and retry classification. Test pure core, adapter contract, plugin contracts, public API, compatibility alias/warnings, and sync/async shells with fakes. Define plugin trust and failure policy. Before v1.0, require docs/examples tests, API diff review, strict typing/lint/test checks, no import-time I/O, documented compatibility/deprecation policy, `import-linter` rules for forbidden dependency directions, mutation testing of retry/planning logic, and a repeatable benchmark comparing wrappers with a baseline. Report measured values and environment; do not assert negligible overhead until the benchmark supports it. The roadmap’s branch-coverage target and public API snapshot must be release gates. List rejected alternatives and known trade-offs. **Evaluation:** 3 points for complete boundaries/API/errors/tests, 3 for justified patterns and alternatives, 3 for release/compatibility/trust/architecture evidence. Deduct for pattern names without requirements or unsupported guarantees.

### Answer 35

Expected deliverable is a staged evidence-backed refactor, not a speculative rewrite. Tests should cover representative valid input, empty/missing input, boundary values and failure paths. First sequence should preserve behavior; rename and behavior changes are separate. Three units should have cohesive responsibilities (for example, request execution, retry planning, and response processing) justified by actual dependencies, not a quota to create classes. Measure a baseline and repeat the same measurement after changes: complexity (same tool/settings), import/coupling graph, changed files for a representative feature, public exports, and test runtime. Use fake transport/time to avoid flaky external behavior. If a cycle appears, introduce a low-level contract/type or invert the dependency, then protect the graph with import tests. Record one rejected abstraction in a retrospective/`DESIGN.md`. **Evaluation:** tests and safe order (1), cohesive design with unchanged behavior (1), comparable measurements and honest trade-offs (1). “Reduced complexity” without a baseline is an unsupported claim.

---

## Roadmap self-check and common-mistake traceability

- **Lesson 10 self-check 1:** Question 27 requires smell → first refactoring/possible pattern → first test for multiple smells; its answer key includes the expanded mapping table.
- **Lesson 10 self-check 2:** Question 29 requires a before/after dependency graph, preserved public re-exports, and architecture regression guards.
- **Lesson 10 self-check 3:** Question 35 requires characterization tests, three cohesive units, and comparable before/after complexity evidence; it explicitly forbids claiming improvement before measurement.
- **Common mistake: refactor without tests:** Questions 28 and 31 require characterization tests before extraction.
- **Common mistake: mix behavior changes into refactor commits:** Questions 18, 22, and 33 classify and separate compatibility changes.
- **Common mistake: replace rigidity with over-engineering:** Questions 4, 27, and 30 require a defensible no-pattern/no-refactor alternative.

# Evaluation rubric

Use the 0–3 scale stated at the beginning for each question (maximum 105 points). For Questions 20–25, use their individual criteria and confirm the corrected code is materially different from the flawed design.

| Score | General standard |
|---:|---|
| 0 | Missing, non-runnable, materially incorrect, or unrelated to the scenario. |
| 1 | Some correct concepts, but important requirements, tests, or trade-offs are absent. |
| 2 | Correct and reasonably complete; minor omissions in edge cases, typing, or explanation. |
| 3 | Correct, tested, readable, appropriately abstracted, explicit about error/compatibility semantics, and justified against alternatives. |

For implementation/refactoring answers, inspect correctness, naming/readability, typing, invariant enforcement, dependency isolation, deterministic tests, error semantics, maintainability and roadmap alignment. For advanced answers, also inspect migration risks, trust boundaries, measurable evidence, and whether public compatibility is preserved intentionally. A different solution can earn full marks when it meets the contract and its trade-offs are explained.

Suggested interpretation (guidance, not a validated certification):
- **90–105:** strong mastery; review edge cases and release/migration judgment.
- **72–89:** competent; target missed tests and boundary reasoning.
- **53–71:** developing; revisit implementation and compatibility lessons.
- **0–52:** rebuild foundations and repeat with runnable tests before progressing.

# Coverage matrix

| Q | Phase | Main coverage | Lesson(s) |
|---:|---|---|---|
| 1 | A | Problem/solution/consequences; pattern as tool | 01 |
| 2 | A | Creational/structural/behavioural; Python alternatives | 01–04 |
| 3 | A | Conditional dispatch vs Strategy; unknown names | 01, 04 |
| 4 | A | Callable vs interface; YAGNI/rule of three | 01, 04 |
| 5 | A | SOLID, composition, hidden effects, over-engineering | 01–03, 10 |
| 6 | B | Factory/named constructors; validation/no I/O | 02 |
| 7 | B | Builder vs constructor; invariants | 02 |
| 8 | B | Singleton alternatives; DI and isolation | 02, 10 |
| 9 | B | Adapter/facade/proxy; error translation | 03, 08 |
| 10 | B | Wrapper order, retry/cache/timeout semantics | 03 |
| 11 | B | Strategy functions and deterministic timing | 04, 09 |
| 12 | B | Observer failure policy and lifecycle | 04 |
| 13 | B | Command, undo/redo | 04 |
| 14 | B | Registry, Protocol, contract tests | 05 |
| 15 | B | Discovery choices, plugin trust/isolation | 05 |
| 16 | C | Public/private API, `__all__`, API tests | 06 |
| 17 | C | Signatures, types, extension points, quick-start | 06 |
| 18 | C | Breaking changes, alias, warnings, migration | 07 |
| 19 | C | Error taxonomy, chaining, retry classification | 08 |
| 20 | C | API critique: boolean traps | 06, 10 |
| 21 | C | API critique: vendor type leakage | 03, 06, 08 |
| 22 | C | API critique: silent default change | 07 |
| 23 | C | API critique: mutable defaults | 06, 10 |
| 24 | C | API critique: misleading names/effects/units | 06, 10 |
| 25 | C | API critique: exceptions as strings | 08 |
| 26 | C | Sans-I/O retry planner; sync/async shells | 09 |
| 27 | D | Smell-to-refactoring mapping; refactoring catalogue; tests-first choices | 01, 05, 10 |
| 28 | D | Characterization tests and safe steps | 10 |
| 29 | D | Circular imports, dependency inversion, stable exports | 06, 10 |
| 30 | D | Abstraction value, technical-debt register, evidence, DESIGN.md | 01, 05, 10 |
| 31 | D | Seams, extraction, injection, reviewable PRs | 09, 10 |
| 32 | D | Registry lifecycle, import side effects, failure isolation | 05, 10 |
| 33 | D | Separate refactor from behavior/API changes; AI-assisted patch verification; debt tracking | 07, 10 |
| 34 | D | End-to-end v0.1→v1.0 architecture, import-linter, mutation/benchmark and release gates | 01–10 |
| 35 | D | 300-line function, tests, measurable refactoring | 01, 06–10 |

# Final mastery checklist

Before considering Module 1.20 complete, confirm that you can:

- [ ] Explain a pattern in terms of problem, solution, consequences, and non-use case.
- [ ] Choose a function/module/callable before reaching for a class hierarchy when it is enough.
- [ ] Implement and test factory, builder-or-constructor, adapter, wrapper, strategy, observer, command, and registry designs.
- [ ] Explain wrapper ordering and preserve exception semantics.
- [ ] Define plugin contracts, deterministic registration, discovery policy, and failure/trust boundaries.
- [ ] Design a small documented public API with stable exports, types, tests, and migration guidance.
- [ ] Distinguish signature compatibility from behavioural compatibility; stage deprecations responsibly.
- [ ] Raise structured exceptions, preserve causes, and classify retries by error semantics rather than strings.
- [ ] Keep decision logic sans-I/O and inject time, sleep, transport, and other effects.
- [ ] Write characterization tests before changing legacy behavior and refactor in small steps.
- [ ] Break dependency cycles while preserving intended public imports.
- [ ] Justify each abstraction with real variation or a required boundary and document rejected alternatives.
- [ ] Produce `DESIGN.md` for `fetchkit` that explains patterns used, simpler alternatives rejected, API/compatibility policy, and known trade-offs.
