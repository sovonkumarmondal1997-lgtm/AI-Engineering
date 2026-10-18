# Lesson 10 — Anti-patterns and Refactoring to Patterns

> **Roadmap placement:** Stage 1 — Programming & Computational Thinking, Module 1.20: Design Patterns and Library API Design. This lesson pairs with Module 1.23 (code smells, characterization tests, and code review).
>
> **Operating principle:** observe current behaviour, create a safety net, make one structural change, and verify it before proceeding. Patterns are options, not goals.

## 1. Learning objectives and prerequisites

You will learn to diagnose design smells without treating every unusual structure as a defect; capture legacy behaviour with characterization tests; refactor in small behaviour-preserving steps; select a proportionate technique; break module cycles; review architectural boundaries; and document a design in `DESIGN.md`.

**Prerequisites:** Python functions, classes, exceptions, imports, type hints, pytest, composition, protocols, public APIs, compatibility, and the preceding Module 1.20 lessons.

## 2. Code smells and diagnosis

A **smell** is evidence to investigate, not proof of a bug. Ask:

1. What concrete change is difficult or risky?
2. What evidence exists—defects, repeated edits, test fragility, coupling, or incidents?
3. Is the proposed design simpler for actual requirements, or is it speculative?

A one-off script can appropriately be one file. A cohesive class can have many methods. Duplication can be preferable to a premature abstraction when two pieces only look similar but have different semantics. Refactor based on change pressure and evidence, not aesthetics alone.

**Safe diagnostic loop:** inspect callers, tests, docs, configuration, imports and side effects; record inputs, outputs, ordering, exceptions, defaults, and resource effects; write characterization tests; identify a seam; make one small change; run focused and full tests; inspect the diff; measure relevant indicators; repeat.

## 3. Beginner anti-patterns

For each smell, the symptom, cause, consequence, example, and decision criterion matter. The presence of a smell alone does not mandate refactoring.

### God object / big ball of mud
One class/module validates, performs HTTP, retries, parses, caches, logs, and writes files. Responsibilities accumulated for different reasons, so unrelated changes collide and tests need elaborate setup. Extract cohesive functions/classes when the responsibilities change independently or are hard to test. Do not split a short stable workflow into many tiny objects solely to reduce line count.

```python
class FetchManager:
    def fetch_parse_cache_log_write(self, url, cache, logger, output):
        # validation, network, retry, parsing, caching, logging, file output
        ...
```

### Singleton and hidden global state

```python
CACHE = {}
RETRY_COUNT = 0

def fetch(url):
    global RETRY_COUNT
    RETRY_COUNT += 1
    ...
```

Hidden dependencies create order-dependent tests and concurrency/lifecycle hazards. Prefer injected state (`FetchClient(cache=..., policy=...)`). A deliberately shared immutable configuration or connection pool may be valid if ownership and lifecycle are explicit.

### Stringly typed code

```python
if mode == "fastt":  # typo silently falls through
    ...
```

Use `Enum`, `Literal`, or a validated value object when values form a meaningful closed set. Strings remain appropriate for open-ended user labels. Do not create a class for every string.

### Deep inheritance, fragile base classes, and inheritance for reuse
Subclasses can depend on undocumented call order, base internals, or overridden methods called during initialization. A base change then breaks derived classes. Prefer shallow inheritance for a genuine substitutable “is-a” relationship; use composition/delegation when inheritance exists mainly to reuse implementation. Do not replace a clear, stable hierarchy with delegation everywhere.

### Boolean traps and long parameter lists

```python
def fetch(url, raw=False, cache=True, retry=True, json_mode=False): ...
```

Positional booleans obscure intent and create many behavioural combinations. Use distinct named operations or a cohesive validated configuration object when options belong together. A single keyword boolean can be fine when it is obvious and stable.

### Primitive obsession
Passing URL strings, retry counts, deadlines, and cache keys everywhere makes invalid states easy to express. Use a value object when it owns a real invariant:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.25

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.base_delay_seconds < 0:
            raise ValueError("base_delay_seconds cannot be negative")
```

### Premature abstraction / speculative generality
An interface with one implementation, a factory returning one trivial class, or a generic plugin framework without a real extension use case adds indirection. Start concrete and extract an abstraction when a variation point, test seam, or independently changing implementation exists. One implementation alone does not prove an abstraction is wasteful—a fake clock seam can be valuable immediately.

### Shotgun surgery, feature envy, and divergent change
- **Shotgun surgery:** one change edits many unrelated locations because a concept is scattered.
- **Feature envy:** a function repeatedly reads another object's data and performs that object's work.
- **Divergent change:** one module changes for unrelated reasons.

Move behaviour toward the invariant/data it owns or extract a cohesive service/module. Validate the diagnosis with actual change history; file count is not enough.

### Copy-paste, magic numbers, and dead code
Copies drift; unnamed values hide policy or units; dead code confuses readers. Extract duplication only when semantics match. Name values by intent and units (`DEFAULT_TIMEOUT_SECONDS = 5.0`). Before deleting dead code, check exports, reflection, plugin discovery, configuration and compatibility paths.

### Swallowed exceptions and return-code confusion

```python
try:
    save_result(result)
except Exception:
    pass
```

This hides defects and falsely implies success. Catch only expected failures and handle them meaningfully, or propagate. Use exceptions for exceptional failures and return values for ordinary outcomes. Libraries generally raise; application boundaries decide whether to log, retry, return a CLI code, or exit.

### Mutable defaults and unexpected argument mutation

```python
def add_header(name: str, value: str, headers: dict[str, str] = {}) -> dict[str, str]:
    headers[name] = value
    return headers
```

The default dictionary is shared between calls. Make ownership explicit and avoid mutating caller-owned input unexpectedly:

```python
def add_header(name: str, value: str,
               headers: dict[str, str] | None = None) -> dict[str, str]:
    result = dict(headers) if headers is not None else {}
    result[name] = value
    return result
```

Copying can be costly or semantically wrong for large objects; document mutation and ownership instead of copying blindly.

### Import-time side effects and leaky abstractions
Importing a module should normally define names, not open sockets, read secrets, create directories, or start threads. Move work to explicit functions/startup. A leaky abstraction spreads vendor exceptions/types or embeds SQL/HTTP details throughout domain logic. Translate at a boundary if a stable library contract is promised; exposing a vendor type can be intentional if documented.

## 4. Intermediate refactoring catalogue

Refactoring changes structure while preserving observable behaviour. Make one edit, run a focused test, then the relevant suite.

| Technique | Use when | Guardrail |
|---|---|---|
| Extract Function | A block has one coherent purpose | Preserve order, exceptions, mutation |
| Inline Function | A wrapper adds no meaning or seam | Do not remove a useful seam/public API |
| Rename | Name misrepresents behaviour | Check docs, exports, reflection, config and callers |
| Introduce Parameter Object | Related parameters travel together | Validate invariants; avoid unrelated bags of fields |
| Replace Magic Number with Constant | Value expresses policy/units | Preserve exact value and rounding |
| Replace Conditional with Polymorphism/dispatch | Variants are stable and independently changing | Keep a simple conditional if clearer |
| Replace Inheritance with Delegation | Inheritance exists mainly for reuse | Preserve lifecycle and call semantics |
| Extract Class | A responsibility has its own state/invariants | Avoid one-class-per-verb designs |
| Move Function | Behaviour belongs in another module/object | Watch import cycles and public paths |
| Introduce Special Case/Null Object | Absence checks repeat consistently | A no-op must not conceal failure |
| Replace Constructor with Factory | Creation varies or setup needs named intent | Avoid trivial factory indirection |

**Smell-to-pattern is a hypothesis, not a rule:** growing type `if/elif` may suggest a dispatch table/Strategy; scattered construction may justify a factory; repeated vendor calls may need an adapter; repeated notification calls may need events only if decoupling/multiple subscribers matter; duplicated retry loops should be unified only after semantics are compared.

### Behaviour-preserving versus behaviour-changing work

A refactor should not silently change defaults, exception types, output order, network call counts, logs, timing, or public imports. If behaviour intentionally changes, isolate it in a separate change with explicit tests, migration notes and release review.

### When not to refactor

Defer when code is about to be deleted, never changes and is adequately safe, lacks a testable seam and there is no time to establish one, or is a measured performance hot spot. Record the debt, impact, owner and revisit trigger instead of allowing “not now” to become invisible forever.

### Strangler fig and branch by abstraction

- **Strangler fig:** route a subset of calls to the replacement, compare outcomes, expand gradually, then remove the old path.
- **Branch by abstraction:** add an interface, route callers through it, swap implementation, then remove temporary scaffolding.

Both require observability, rollback criteria, compatibility tests and a planned end state.

## 5. Advanced architectural refactoring

### Seams and dependency-breaking techniques

A **seam** is a point where behaviour can be substituted without rewriting the entire system. Techniques include:

- **Parameterize method/constructor:** inject a clock, transport, repository or policy.
- **Wrap method/class:** isolate an external dependency behind an adapter.
- **Extract and override:** isolate a difficult operation in an overridable method; use sparingly because inheritance seams can be fragile.
- **Sprout method/class:** implement new behaviour separately and delegate to it instead of rewriting a risky legacy block all at once.
- **Dependency injection:** constructor injection for long-lived collaborators; method parameters for one-off dependencies.

### Breaking circular dependencies safely

Suppose `fetchkit.client` imports `fetchkit.cache`, while `fetchkit.cache` imports `FetchResult` from `fetchkit.client`. Import order can fail and the layers are coupled.

1. Add characterization tests for public imports and calls.
2. Move the stable `FetchResult` value type into a lower-level `fetchkit.models` module that imports neither client nor cache.
3. Make `cache` import `models`, not `client`.
4. Make `client` depend on a small cache `Protocol` or injected cache object, not the concrete cache module.
5. Add architecture rules: models/core may not import clients, transports, or concrete caches.
6. Run tests after each step. Keep old public re-exports if callers rely on the old path.
7. Remove temporary compatibility imports only under the project's compatibility policy.

For broader coupling, dependency inversion may help. Event-based decoupling can help when direct calls create a real lifecycle dependency, but it introduces ordering/delivery complexity and should not be used reflexively.

### Tooling and architectural safeguards

- `import-linter`: enforce module/layer rules; verify configuration against the installed version.
- `ruff` (`C901`, bugbear), `radon`/`xenon`: complexity signals, not design verdicts.
- `vulture`: candidate dead code; inspect reflection/plugin/export use before deleting.
- `pylint`: design/duplication signals.
- `mypy --strict` or Pyright: type regressions and unclear boundaries.
- IDE refactoring tools; `libcst`/`rope` for structured automation.
- Mutation testing: check whether tests fail when a condition/return value is deliberately altered.

A successful automated rename can still break config keys, plugin lookup, docs, or downstream imports. Human review remains required.

### Technical debt and PR review

Maintain a debt register with problem, impact, evidence, risk, effort, owner and revisit trigger. Prioritize change amplification and incident risk, not aesthetic preference. Use the boy-scout rule for small safe changes; schedule focused work for coordinated architectural changes.

**Refactoring PR checklist:** baseline tests exist; behaviour changes are isolated; tests assert outcomes rather than implementation trivia; public names/defaults/exceptions/order/resource ownership/import paths are preserved; dependencies are simpler; abstractions have a demonstrated purpose; diff is reviewable and reversible.

AI tools may propose extraction or tests, but humans must inspect every semantic change and run tests. Use small patches and verify tests would fail under plausible mutations; do not merge a bulk rewrite on model confidence alone.

## 6. Smell-to-refactoring decision table

| Smell / evidence | First test | Candidate technique/pattern | Main risk |
|---|---|---|---|
| God object | Test each external workflow | Extract Function/Class; boundary facade | Splitting cohesive logic needlessly |
| Hidden global state | Call in different orders; independent instances | Inject state/dependencies | Changing shared-state semantics |
| Stringly typed mode | Valid/invalid mode tests | Enum/`Literal`/value object | Rejecting formerly accepted values |
| Deep inheritance | Subclass contract tests | Delegation/composition | Lifecycle or override-order changes |
| Boolean trap | Exercise each used flag combination | Named methods/config/Strategy | Public signature break |
| Primitive obsession | Boundary/invalid-value tests | Value object/parameter object | Too many tiny classes |
| Shotgun surgery | Representative change scenario | Move Function/Extract Class | New import cycle |
| Copy-paste | Differential tests for each copy | Shared helper if semantics match | Unifying distinct behaviour |
| Swallowed exception | Inject failure and assert visible handling | Narrow catch/domain error | Wrong public exception or secret leak |
| Mutable default/input mutation | Repeated-call and input-unchanged tests | Safe default/explicit ownership | Copy cost or changed contract |
| Import side effect | Import in a clean process | Explicit lifecycle | Missing initialization step |
| Leaky abstraction | Fake vendor error and assert public type | Adapter/anti-corruption layer | Losing diagnostic context |

## 7. `fetchkit` before-and-after case study

This deliberately small example demonstrates safe process, not a full HTTP implementation. Tests are local and require no network.

### 7.1 Original legacy implementation

```python
# legacy_fetchkit.py — intentionally messy
import json
import time

CACHE = {}
RETRIES = 0

def fetch(url, raw=False, retry=True, cache=True, headers={}):
    global RETRIES
    if url == "":
        return "ERROR"
    if cache and url in CACHE:
        return CACHE[url]
    result = None
    for attempt in range(3 if retry else 1):
        RETRIES += 1
        try:
            response = {"status": 200, "body": '{"ok": true}', "headers": headers}
            if response["status"] == 200:
                result = response["body"] if raw else json.loads(response["body"])
                break
            if response["status"] != 503:
                return "ERROR"
            time.sleep(1)
        except Exception:
            pass
    if result is None:
        return "ERROR"
    if cache:
        CACHE[url] = result
    return result
```

**Smell inventory:** mutable global cache/counter; mutable default; boolean traps; magic status codes; stringly typed errors; swallowed exceptions; policy mixed with sleep; fake vendor response baked in; unclear result shape (`str`, decoded value, or error sentinel); implicit transport seam; hidden cache ownership.

### 7.2 Characterization tests first

Before changing the implementation, capture what callers currently observe—including undesirable behaviour—so intentional fixes can be distinguished from refactoring. These tests characterize a *chosen baseline*, not a recommendation that the old contract should remain forever.

```python
# test_legacy_characterization.py
import pytest
import legacy_fetchkit as legacy

@pytest.fixture(autouse=True)
def reset_legacy_globals():
    legacy.CACHE.clear()
    legacy.RETRIES = 0

def test_default_fetch_decodes_json():
    assert legacy.fetch("https://example.invalid") == {"ok": True}

def test_raw_mode_returns_body_text_when_cache_is_empty():
    assert legacy.fetch("https://example.invalid", raw=True) == '{"ok": true}'

def test_legacy_cache_reuses_first_result_shape_across_modes():
    url = "https://example.invalid"
    assert legacy.fetch(url) == {"ok": True}
    # This captures a real legacy defect: cache key ignores the raw/decoded mode.
    assert legacy.fetch(url, raw=True) == {"ok": True}

def test_empty_url_returns_error_sentinel():
    assert legacy.fetch("") == "ERROR"
```

The fixture prevents order-dependent test pollution; the explicit cross-mode test records the existing cache-shape bug rather than pretending it is desirable. The legacy `headers={}` is a mutable default even though this simplified function does not mutate it; it is a latent hazard, not evidence of a currently observed mutation. A later behaviour change should correct the cache key/result contract in a separate, documented change. In a real legacy project, also characterize retry count, error cases, ordering, mutations, and external effects using a fake seam. Do not write tests that depend on incidental internals unless that behaviour is already a public contract.

### 7.3 Prioritized refactoring plan

1. **P0—safety:** add a fakeable transport seam and tests for success, failure and call counts.
2. **P1—state and input ownership:** replace mutable default, make cache explicit, eliminate global retry counter.
3. **P2—policy/effects:** extract retry decision from sleeping; test attempts without real waits.
4. **P3—API clarity:** introduce typed result/error contract in a separately reviewed behaviour change; avoid silently changing the legacy sentinel.
5. **P4—structure:** move transport adapter, core policy and public facade into cohesive modules; preserve import aliases during migration.
6. **P5—architecture:** add import-boundary checks, strict typing, public API tests and a `DESIGN.md`.

### 7.4 Small sequential target refactor

The final target below deliberately has a small number of justified units: a `RetryPolicy` value object, a `Transport` protocol, a pure `decode_body` function, and a `Fetcher` that coordinates them. Cache and retry effects are explicit. This example avoids a full generic plugin system because no such need is demonstrated.

```python
# fetchkit_core.py — Python 3.12+
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
import json

@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3

    def __post_init__(self) -> None:
        # bool is a subclass of int, and floats can pass a simple < 1 check
        # but fail later in range(). Reject both at the configuration boundary.
        if type(self.max_attempts) is not int or self.max_attempts < 1:
            raise ValueError("max_attempts must be an integer >= 1")

@dataclass(frozen=True)
class Response:
    status: int
    body: str

class Transport(Protocol):
    def get(self, url: str) -> Response: ...

class FetchError(Exception):
    """Base exception for fetchkit operational failures."""

class HTTPStatusError(FetchError):
    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__(f"unexpected HTTP status: {status}")

def decode_body(body: str) -> object:
    """Decode JSON without network, clock, or filesystem effects."""
    return json.loads(body)

class Fetcher:
    def __init__(self, transport: Transport, *, retry_policy: RetryPolicy | None = None) -> None:
        self._transport = transport
        self._retry_policy = retry_policy or RetryPolicy()

    def fetch_json(self, url: str) -> object:
        if not isinstance(url, str) or not url.strip():
            raise ValueError("url must be a non-empty string")
        for attempt in range(self._retry_policy.max_attempts):
            response = self._transport.get(url)
            if response.status == 200:
                return decode_body(response.body)
            if response.status != 503 or attempt + 1 == self._retry_policy.max_attempts:
                raise HTTPStatusError(response.status)
        raise AssertionError("validated retry loop must return or raise")
```

**What changed in each step:** transport is injected before relocating code; `RetryPolicy` centralizes and validates the attempt-count invariant; parsing is pure; errors are typed; retries are bounded. The policy rejects booleans and non-integer values because `bool` is an `int` subclass and a float would fail later inside `range()`. The public method rejects non-string and whitespace-only URLs before any transport call. This illustrative refactor does not add sleep/backoff, caching, async support, or plugins because those are separate requirements. It intentionally changes the old sentinel and boolean API only as a **new API**, not as a silent in-place replacement.

### 7.5 Fake transport and target tests

```python
# test_fetchkit_core.py
import pytest
from fetchkit_core import Fetcher, HTTPStatusError, Response, RetryPolicy

class QueueTransport:
    def __init__(self, responses: list[Response]) -> None:
        self._responses = list(responses)
        self.calls = 0

    def get(self, url: str) -> Response:
        self.calls += 1
        if not self._responses:
            raise AssertionError("unexpected extra request")
        return self._responses.pop(0)

def test_success_decodes_json():
    transport = QueueTransport([Response(200, '{"ok": true}')])
    assert Fetcher(transport).fetch_json("https://example.invalid") == {"ok": True}
    assert transport.calls == 1

def test_503_retries_until_success():
    transport = QueueTransport([Response(503, ""), Response(200, "[1, 2]")])
    fetcher = Fetcher(transport, retry_policy=RetryPolicy(max_attempts=2))
    assert fetcher.fetch_json("https://example.invalid") == [1, 2]
    assert transport.calls == 2

def test_permanent_status_is_not_retried():
    transport = QueueTransport([Response(404, "not found")])
    with pytest.raises(HTTPStatusError) as caught:
        Fetcher(transport).fetch_json("https://example.invalid")
    assert caught.value.status == 404
    assert transport.calls == 1

@pytest.mark.parametrize("url", ["", "   ", None, 42])
def test_invalid_url_is_rejected_before_transport(url):
    transport = QueueTransport([])
    with pytest.raises(ValueError, match="url must be a non-empty string"):
        Fetcher(transport).fetch_json(url)
    assert transport.calls == 0

def test_retry_policy_rejects_zero_attempts():
    with pytest.raises(ValueError, match="max_attempts"):
        RetryPolicy(max_attempts=0)

@pytest.mark.parametrize("attempts", [True, False, 1.5, "3"])
def test_retry_policy_rejects_non_integer_attempts(attempts):
    with pytest.raises(ValueError, match="max_attempts"):
        RetryPolicy(max_attempts=attempts)

def test_retry_exhaustion_is_bounded():
    transport = QueueTransport([Response(503, ""), Response(503, "")])
    fetcher = Fetcher(transport, retry_policy=RetryPolicy(max_attempts=2))
    with pytest.raises(HTTPStatusError) as caught:
        fetcher.fetch_json("https://example.invalid")
    assert caught.value.status == 503
    assert transport.calls == 2

def test_json_decode_error_propagates_without_retrying_transport():
    transport = QueueTransport([Response(200, "not-json")])
    with pytest.raises(ValueError):
        Fetcher(transport).fetch_json("https://example.invalid")
    assert transport.calls == 1
```

Run the legacy characterization suite before changes and the target suite after the relevant steps. When the new contract intentionally differs (e.g. raising instead of returning `"ERROR"`), write a migration test and release note; do not pretend old and new behaviour are identical.

### 7.6 Before/after comparison without fabricated metrics

| Dimension | Legacy baseline | Target criterion | Evidence to collect |
|---|---|---|---|
| Retry tests | Hidden in function, real sleep | Inject transport; bounded calls | Test call counts; no real sleep |
| State isolation | Module globals | Instance-owned dependencies | Two-instance isolation test |
| Input mutation | Shared default may mutate | Explicit ownership | Repeated-call and input-unchanged tests |
| Error contract | String sentinel / swallowed errors | Typed exception for new API | `pytest.raises` and error attributes |
| Coupling | Transport/policy/parser together | `Protocol` + pure parser | Import graph / dependency rule |
| Complexity | Nested mixed concerns | Small cohesive functions | Measure before/after with same tool |
| Public API | Boolean flags and unclear result | Named method and documented errors | API snapshot and usage review |

No benchmark or complexity measurement is claimed here. Capture a baseline using the same tool and command before/after; compare representative tasks, not just raw line counts.

### 7.7 Circular-dependency example and sequence

**Problem:** `client.py` imports `cache.py` for `Cache`, while `cache.py` imports `FetchResult` from `client.py`. Both modules own concepts the other needs.

```python
# Bad: client.py
from .cache import Cache

@dataclass
class FetchResult: ...

# Bad: cache.py
from .client import FetchResult
class Cache: ...
```

**Safe sequence:** (1) characterize `FetchResult` imports and cache calls; (2) move the stable result dataclass to `models.py`; (3) update cache to import `models`; (4) make client depend on a `CacheProtocol` in a low-level contracts module or inject an object satisfying it; (5) add an import-linter rule preventing `models` from importing `client`, `cache`, or transport modules; (6) run import and behavioural tests after each move; (7) keep `from .models import FetchResult` in the old public module if compatibility requires it. Do not “fix” the cycle by hiding imports inside functions unless the runtime dependency is genuinely optional/lazy.

A concrete dependency direction after the move can look like this (each block is a separate module in the same package):

```python
# models.py — leaf value types; imports no fetchkit modules
from dataclasses import dataclass

@dataclass(frozen=True)
class FetchResult:
    body: str
```

```python
# contracts.py — shared port; depends only on the leaf model
from typing import Protocol
from .models import FetchResult

class CacheProtocol(Protocol):
    def get(self, key: str) -> FetchResult | None: ...
    def set(self, key: str, value: FetchResult) -> None: ...
```

```python
# cache.py — concrete cache depends on models, never on client
from .models import FetchResult

class MemoryCache:
    def __init__(self) -> None:
        self._items: dict[str, FetchResult] = {}

    def get(self, key: str) -> FetchResult | None:
        return self._items.get(key)

    def set(self, key: str, value: FetchResult) -> None:
        self._items[key] = value
```

```python
# client.py — depends on the port and model, not MemoryCache
from .contracts import CacheProtocol
from .models import FetchResult  # re-exported here for old import paths

class Client:
    def __init__(self, cache: CacheProtocol) -> None:
        self._cache = cache

    def cached_result(self, key: str) -> FetchResult | None:
        return self._cache.get(key)
```

The dependency graph is `client -> contracts -> models` and `cache -> models`; there is no path from `cache` back to `client`, so this version removes the cycle. The client’s import of `FetchResult` also keeps `from fetchkit.client import FetchResult` working while callers migrate. These snippets demonstrate the import boundary; they do not implement HTTP fetching.

### 7.8 Example final `DESIGN.md`

```markdown
# fetchkit Design

> This is the intended package-level design, not a claim that the single-file
> `fetchkit_core.py` teaching example already implements these modules. The
> current example keeps the implementation compact; split modules only when the
> project needs the boundary or the code has grown enough to justify it.

## Responsibilities
- `models`: immutable response and result values; no I/O dependencies.
- `core`: pure JSON decoding and policy/value objects; no network or sleep calls.
- `transports`: HTTP-specific adapters; translates vendor details at the boundary.
- `client`: public orchestration facade; owns injected collaborators and lifecycle.
- Retry orchestration belongs in the client/shell in this proposed layout; the
  current minimal example keeps that loop in `Fetcher` in `fetchkit_core.py`.

## Patterns used and why
- Dependency injection / Protocol: makes transport replaceable in tests and alternative runtimes.
- Value object (`RetryPolicy`): validates retry invariants once.
- Adapter: contains vendor-specific calls and exception translation.
- Functional core / imperative shell: keeps parsing and policy deterministic.

## Alternatives rejected
- Singleton cache: hidden state and test interference without a demonstrated need.
- Generic plugin framework: no current extension requirement in this minimal design.
- Deep inheritance: composition is enough for one transport seam.

## Public API and compatibility
- Export only documented names from `fetchkit.__init__` and maintain an API snapshot.
- Treat signatures, defaults, exceptions, return values, and import paths as contracts.
- Deprecate legacy aliases with warnings and a migration period before removal.

## Trade-offs and known limits
- Retry behaviour is bounded but this minimal example has no backoff or jitter.
- The sample transport is synchronous; an async shell needs a separate non-blocking driver.
- Caching and plugin discovery are intentionally out of scope until requirements justify them.
```

The document above is a model for the **design note**, not proof that every listed module has been implemented in a real package.

## 8. Testing strategy and exercises

### Testing strategy

- **Characterization tests:** record current externally visible behaviour before touching the code.
- **Unit tests:** pure parsing, validation, policy and transformation.
- **Seam tests:** fake transport/clock/cache; assert calls and effects, not private call order unless contractual.
- **Contract tests:** run the same expected behaviour against each adapter/implementation.
- **Integration tests:** a small number verify real boundaries and resource cleanup.
- **Architecture tests:** imports obey layer rules; importing core does not load optional network dependencies.
- **Mutation tests:** alter a branch/return value and verify a relevant test fails.

### Practical exercises

1. Pick five smells from Section 3. For each, name a refactoring, a target pattern only if justified, and the first characterization test.
2. Implement the circular-dependency sequence in a toy package. Keep the public import stable with a re-export.
3. Take a 300-line function from an earlier project. Before splitting it, record inputs, outputs, side effects, ordering, exceptions, and representative edge cases. Add characterization tests. Identify three cohesive responsibilities; extract one at a time and run tests after each extraction. Move one responsibility only after its dependency seam is clear. Measure cyclomatic complexity with the same tool before and after, count changed call sites, record test runtime, and verify public API snapshots. Report actual numbers from your run; do not invent results. The target is three cohesive units, not three arbitrary chunks of 100 lines.
4. Write a short retrospective: which patterns paid off, which abstractions were removed, what compatibility was preserved, and what remains debt.

## 9. Common mistakes

The roadmap highlights three recurring failures:

1. **Refactoring without tests.** Add characterization tests and seams before restructuring; if a complete suite is impossible, record the untested risks and constrain the change.
2. **Mixing behaviour changes into refactor commits.** Keep structure-only changes separate from deliberate API or runtime changes. Assert defaults, exceptions, ordering and side effects.
3. **Replacing one rigid structure with an over-engineered one.** Require a demonstrated variation point or complexity reduction. A dispatch table, protocol, event bus, factory or hierarchy is not automatically an improvement.

Also avoid treating metrics as goals, deleting “dead” public names without a compatibility check, using broad exception suppression, and trusting AI-generated edits without running human-reviewed tests.

## 10. Self-check questions with model answers

### 1. For five smells, name a refactoring, target pattern, and first test.

Example answers:

- Boolean flags: characterize each used combination; introduce named methods or a config object; use Strategy only if algorithms vary independently.
- Global cache: test independent clients and cache hit/miss semantics; inject a cache; use a cache adapter only if implementations vary.
- Vendor types leaking everywhere: test translated error type and cause; wrap with an adapter/anti-corruption layer.
- Duplicated retry loops: test attempt count and retryable categories for each path; extract a common retry policy only if semantics match.
- God object: test each user-visible workflow; extract a cohesive responsibility/facade without creating arbitrary microservices.

### 2. Show a step-by-step sequence to break a circular dependency without breaking the public API.

Add import/behaviour characterization tests; move the shared stable type into a lower-level module; make both modules depend on that module or a small protocol; update imports one at a time; add architecture rules; run tests after each step; retain a re-export at the old public path until the documented deprecation/removal policy permits removal.

### 3. Refactor a 300-line function into three cohesive units with measurable complexity reduction.

First write tests for outputs, exceptions, ordering, mutation and side effects. Identify three responsibilities from actual change pressure—not line ranges. Extract the first responsibility, run focused and full tests, then repeat. Record the same complexity metric before and after, test runtime, files touched for a representative change, and public API snapshot. Report measured values only after running tools. Do not claim a result from this lesson's illustrative example.

## 11. Summary and completion checklist

- [ ] I can distinguish a smell from a proven defect and explain the change pressure.
- [ ] I can write characterization tests before refactoring legacy code.
- [ ] I can apply the catalogue techniques without silently changing behaviour.
- [ ] I can justify a pattern—or choose a simple function instead.
- [ ] I can create seams and inject I/O dependencies.
- [ ] I can break circular imports without breaking the public API.
- [ ] I can enforce architecture boundaries and review them with tests.
- [ ] I can measure complexity/coupling/change amplification rather than inventing improvements.
- [ ] I can review AI-assisted refactors with human-verified tests and small diffs.
- [ ] I can document patterns, rejected alternatives, API policy, compatibility and trade-offs in `DESIGN.md`.
- [ ] I can complete the 300-line function exercise safely and report actual measurements.

## 12. Authoritative references

These references support the techniques; use versions appropriate to your project.

- Martin Fowler, *Refactoring: Improving the Design of Existing Code*, 2nd ed. — refactoring catalogue and behavioural-preservation discipline.
- Michael Feathers, *Working Effectively with Legacy Code* — seams, characterization tests, sprout method/class, and dependency-breaking techniques.
- Python documentation, `unittest.mock`: <https://docs.python.org/3/library/unittest.mock.html>
- Python documentation, `typing.Protocol`: <https://docs.python.org/3/library/typing.html#typing.Protocol>
- pytest documentation: <https://docs.pytest.org/>
- Ruff rules: <https://docs.astral.sh/ruff/rules/>
- import-linter documentation: <https://import-linter.readthedocs.io/>
- Radon documentation: <https://radon.readthedocs.io/>
- Vulture documentation: <https://github.com/jendrikseipp/vulture>
- LibCST documentation: <https://libcst.readthedocs.io/>

**Source alignment:** the anti-pattern catalogue, refactoring sequence, tools, debt-management concepts, review guidance, `DESIGN.md` synthesis, three common mistakes, and three self-checks above follow Lesson 10 of the supplied Module 1.20 roadmap. Examples and additional guardrails are instructional elaborations, not claims about an existing published `fetchkit` implementation.
