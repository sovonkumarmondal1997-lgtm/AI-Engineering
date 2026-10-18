# Backward Compatibility and Deprecation Policy

> **Module 1.20 — Design Patterns and Library API Design, Lesson 07**  
> Target: Python 3.12+; new examples should be checked with `mypy --strict` or Pyright strict mode.  
> Running case study: `fetchkit`, a small data-fetching library.

> **Scope note:** All `fetchkit` versions and release dates in this lesson are hypothetical teaching examples, not claims about a published package. The policy is an example to adapt, not a universal rule for every library.

## 1. Objectives and prerequisites

By the end of this lesson, you should be able to:

- Identify source, behavioural, typing, import-path, configuration, and serialization breaks.
- Distinguish additive changes from changes that violate an existing contract.
- Define a written support and deprecation policy, including what counts as public API.
- Deprecate two legacy `fetchkit` functions with actionable warnings, forwarding wrappers, tests, release notes, and a migration guide.
- Snapshot a public API and gate changes in CI; know when to use a tool such as `griffe` and when a custom check is sufficient.
- Plan compatibility across Python versions, dependencies, plugin APIs, and serialized data.
- Explain the limits of semantic versioning, warnings, telemetry, and automated API-diff tools.

### Prerequisites

You should understand public exports and `__all__` (Lesson 06), function signatures and warnings, package versioning and releases (Module 1.18), pytest, type hints, and dependency injection. You should also have a basic understanding of CI and virtual environments.

## 2. Compatibility mental model

A library's users form a large, mostly invisible test suite. Their code may rely on documented behaviour, examples, type annotations, import paths, exceptions, defaults, ordering, and sometimes details the maintainer never intended to promise. Hyrum's law captures the risk: with enough users, every observable behaviour will be depended on by somebody.

**Backward compatibility** means that code or data written against an earlier supported version continues to work when used with the newer version, within the project's stated policy. Compatibility is not a single yes/no property.

| Compatibility dimension | Example contract | Potential break |
|---|---|---|
| Source/API | `fetch_url(url, *, timeout=10.0)` accepts the same calls | Renaming `timeout` to `deadline` breaks keyword callers |
| Behavioural | A successful call returns bytes; invalid URL raises `ValueError` | Silently returning decoded text instead of bytes |
| Typing | A function accepts `str` and returns `bytes` | Narrowing accepted input to a custom subtype without a migration path |
| Import path | `from fetchkit import FetchError` works | Moving the exception without retaining an old-path export |
| Configuration | `timeout = 10` means ten seconds | Reinterpreting the value as milliseconds |
| Serialization/wire | Stored JSON fields retain their meanings | Reusing a field name for a different meaning or changing a wire format incompatibly |
| Operational/observable | Ordering, laziness, exit status, or resource ownership is documented | Replacing a list with a one-shot generator or closing a caller-owned resource |

A performance change can also be compatibility-relevant if the library promised a latency bound, laziness, bounded memory, or non-blocking behaviour. Incidental timing is not automatically a guarantee, but a performance cliff can still be a serious regression.

### Breaking versus additive changes

An additive change is often compatible when it preserves existing calls and semantics—for example, adding a new function or an optional keyword-only parameter with a backward-compatible default. “Often” matters: adding a keyword may collide with `**kwargs` forwarding, and an optional argument may alter overload resolution or behaviour if its default is not truly neutral.

A breaking change makes previously valid code fail or changes its observable meaning. Examples include removing a public name, making an optional parameter required, changing the default behaviour, changing exception types, changing return shape, raising the minimum Python version, or changing a serialized field's meaning.

### Public contract is broader than `__all__`

Treat names documented as public, exported from the package root, used in quick starts, or deliberately supported as public contracts. `__all__` helps define wildcard imports and communicates intended exports; it does **not** prevent direct access to other module attributes or make undocumented details impossible for users to depend on. Do not silently promote every implementation detail to a guarantee, but be honest when a previously documented or widely used name is being retired.

### Semantic versioning—and the `0.y.z` caveat

Under Semantic Versioning for a stable `1.x` API, releases generally use:

- **PATCH** for compatible bug fixes;
- **MINOR** for backward-compatible functionality;
- **MAJOR** for incompatible public API changes.

The `0.y.z` series is for initial development and does not provide the same stable-API promise under SemVer. That is not a reason to surprise users. A project can voluntarily provide stronger guarantees during `0.x`; `fetchkit` does so in the hypothetical policy below. Also state supported Python and dependency ranges independently of the package's version number.

### Deprecation is not removal

Deprecation is an explicit notice that a feature remains available for now but should no longer be used. A good deprecation tells users **what to use instead, why if relevant, when removal is planned, and where to find migration instructions**. Removal is a later, separately communicated compatibility change. A deprecation warning alone does not guarantee that users saw it: `DeprecationWarning` is ignored by default in most imported application contexts, so release notes and migration docs remain necessary.

## 3. Beginner concepts

### Signatures, defaults, exceptions, and results are contracts

Consider this established call:

```python
payload = fetchkit.fetch_url("https://example.test/data", timeout=5.0)
```

The parameter name `timeout`, its unit (seconds), its optional status, and its default all matter. Renaming it breaks keyword calls even if positional calls still work. Changing the default from seconds to milliseconds is a behavioural/configuration break. Returning a tuple instead of bytes, returning text instead of bytes, or changing a documented `FetchError` into an unrelated `RuntimeError` can break callers too.

A documented exception type lets callers write targeted recovery logic:

```python
try:
    payload = fetchkit.fetch_url(url)
except fetchkit.FetchTimeoutError:
    retry_later()
except fetchkit.FetchError:
    report_fetch_failure()
```

Do not change the exception hierarchy casually. If you need to wrap a low-level error, preserve the cause with `raise PublicError(...) from exc`, and document which failures callers may catch.

### Compatibility categories in practice

- **Source compatibility:** old expressions still parse and call successfully.
- **Behavioural compatibility:** old calls preserve results, side effects, ordering, and documented failure modes.
- **Typing compatibility:** annotations and overloads continue to support previously valid typed callers. Runtime compatibility and static typing compatibility can diverge.
- **Import compatibility:** old module and package paths continue to resolve while supported.
- **Configuration compatibility:** old config keys, CLI flags, environment variables, and units keep their meaning during transition.
- **Serialization compatibility:** readers can process data produced by supported earlier writers, and field IDs/names are not repurposed. Explicitly distinguish backward compatibility (new reader reads old data) from forward compatibility (old reader tolerates new data).

A change may be source-compatible but behaviour-breaking, or runtime-compatible but typing-breaking. Review all dimensions, not only whether imports succeed.

### A first deprecation warning

For a library API, use `DeprecationWarning` for developer-facing deprecations and set `stacklevel=2` so the warning points to the caller rather than the wrapper implementation:

```python
import warnings


def old_name(value: str) -> str:
    warnings.warn(
        "old_name() is deprecated; use new_name() instead. "
        "Removal is planned for v2.0. See the migration guide.",
        DeprecationWarning,
        stacklevel=2,
    )
    return new_name(value)
```

`FutureWarning` is typically more visible to end users and is appropriate when the warning is intended for application users rather than library developers. Do not choose a category solely to make a warning disappear or appear; choose it based on the audience and compatibility intent. Python's `warnings` filters can suppress or turn warnings into errors, and test suites should exercise the intended behaviour.

## 4. Intermediate deprecation workflow

### A policy users can plan around

A useful policy names:

1. **Public API definition:** documented names, package-root exports, stable namespaces, configuration keys, CLI flags, and published schemas.
2. **Support window:** supported Python versions, dependency ranges, and which package release lines receive bug/security fixes.
3. **Notice period:** for example, keep deprecated APIs through at least two subsequent minor releases or six months, whichever is longer, where practical.
4. **Communication:** deprecation warning, changelog entry, release notes, migration guide, and announcement channel appropriate to the project's audience.
5. **Removal gate:** usage evidence where available, migration coverage, tests, and explicit maintainer approval.
6. **Exceptions:** urgent security or legal changes may require faster removal, with an incident note and a migration or mitigation path where possible.

A notice period is a project policy, not a Python language rule. Pick one the project can sustain. Under `0.x`, say explicitly whether the policy is stronger than SemVer's default expectations.

### The lifecycle

1. **Propose:** state the problem, affected public names, compatibility dimensions, alternatives, and expected user impact in an issue/RFC/ADR.
2. **Add the replacement first:** document and test the new API before warning users away from the old one.
3. **Forward old calls:** preserve behaviour through an alias or wrapper. If signatures differ, a wrapper can translate arguments explicitly.
4. **Warn at the call site:** include old name, replacement, first deprecated version, target removal version or policy, and migration guide.
5. **Test both paths:** test new behaviour, old wrapper forwarding, warning category/message/stack level, and important error cases.
6. **Communicate:** add a `Deprecated` changelog entry, migration example, release note, and relevant documentation updates.
7. **Measure responsibly:** use opt-in telemetry or warning counts if appropriate and privacy-compliant; do not assume absence of telemetry means absence of use.
8. **Remove only at a policy-approved release:** delete old tests only after the supported compatibility window ends; retain migration documentation.

### Warning mechanics and testing

- Use `warnings.warn(message, DeprecationWarning, stacklevel=2)` inside a public wrapper. Increase `stacklevel` if additional wrapper layers mean the warning still points inside the library.
- Avoid warning on module import just because a legacy symbol is imported; that creates noisy import-time side effects. Warn when the deprecated API is called, unless the deprecated behaviour is specifically the import path and a module-level `__getattr__` is deliberately used.
- Do not warn every internal call to the deprecated function. Make new internal code call the replacement directly.
- Use `pytest.warns(DeprecationWarning, match="...")` to assert the warning, and separately test that the wrapper forwards arguments and preserves return/exception behaviour.
- Run a CI job with `python -W error::DeprecationWarning -m pytest` for the project’s own tests to reveal internal use of deprecated APIs. Third-party dependencies may emit warnings too, so handle known external warnings narrowly rather than disabling the category globally.

### Aliases, wrappers, and module moves

A direct alias is appropriate when semantics and signature are identical and no per-call warning is needed:

```python
new_name = implementation
```

A forwarding wrapper is better when the legacy name must warn or translate parameters:

```python
def old_name(value: str, *, legacy_mode: bool = False) -> str:
    warnings.warn("old_name() is deprecated; use new_name()", DeprecationWarning, stacklevel=2)
    return new_name(value, mode="legacy" if legacy_mode else "standard")
```

When moving a module, keep a re-export at the old path during the transition. Module-level `__getattr__` can lazily resolve renamed symbols, but it must be tested and documented because introspection, type checkers, and `from old_module import name` behaviour need consideration. Do not make `__getattr__` a mysterious catch-all for arbitrary names.

### Changelogs and migration guides

Use predictable categories such as **Added**, **Changed**, **Deprecated**, **Removed**, **Fixed**, and **Security**. Put breaking changes and migration actions near the top of release notes. A migration guide should show before/after snippets and call out changes that cannot be mechanically rewritten.

Example changelog entry:

```markdown
## [0.9.0] — hypothetical

### Deprecated
- `fetchkit.download_text()` is deprecated; use `fetchkit.fetch_text()`.
  The old wrapper remains available through the v1.x compatibility window;
  removal is planned no earlier than v2.0.0. See `docs/migration.md`.
```

## 5. Advanced compatibility automation

### API snapshots and API-diff tools

A public API snapshot records exported names and signatures. It is useful for detecting accidental removals, parameter renames, default changes, and annotation drift. Keep the snapshot reviewed and versioned; an approved breaking change should update it only alongside release notes and a migration plan.

Snapshot tests do **not** prove behavioural compatibility, nor do they automatically understand semantic changes in annotations or defaults. Combine them with runtime tests, type-checking, documentation examples, and compatibility tests from prior releases.

A lightweight snapshot for the small case study appears in Section 8. For larger projects, tools such as [`griffe`](https://mkdocstrings.github.io/griffe/) can extract and compare API structures. Pin the tool version in CI and review its configuration, visibility rules, and output; do not treat a green diff as proof that behaviour is unchanged. An alternative is comparing signatures extracted from installed old and new wheels in separate virtual environments.

### CI and supported-version matrix

A release pipeline should include, as appropriate:

- Unit and integration tests on the minimum supported and newest supported Python versions.
- Lower-bound dependency testing and a representative latest-dependency job.
- Type-checking (`mypy --strict` or Pyright strict) and linting.
- API snapshot/API-diff check.
- Documentation examples and doctests.
- Deprecation-warning-as-error tests for first-party code.
- Tests that old public names still import and forward during the deprecation window.
- Plugin host × plugin API compatibility tests if `fetchkit` plugins are part of the supported interface.
- A release checklist requiring an explicit decision for every public API diff.

Do not promise compatibility with every dependency version. Publish a support matrix and test its endpoints. Avoid gratuitous upper bounds, but use constraints when a real incompatibility requires them. Applications may lock exact versions; libraries should state realistic ranges.

### Compatibility across time and serialized data

For JSON/configuration/schema evolution, define old-reader/new-data and new-reader/old-data expectations separately. Prefer adding optional fields with safe defaults, ignoring unknown fields where the format allows it, and never reusing a field name or numeric identifier for a different meaning. If the format is externally persisted, version it and provide readers/adapters for supported older versions. Pickle is especially sensitive to class/module moves and should not be treated as a stable cross-version wire format unless the project explicitly commits to it.

For CLI, REST/JSON, SDK, and agent-tool interfaces, the same principle applies: parameter names, defaults, exit codes, output shape, schemas, and error structures are contracts. A schema change that is additive for a tolerant consumer may still break a strict validator.

### Plugin API compatibility

If plugins implement a public `Protocol` or ABC, changing a required method, argument, return type, or lifecycle order can break all external plugins even when the host package's top-level API looks unchanged. Version the plugin contract separately where necessary; record plugin name/version/API version, negotiate capabilities, and provide compatibility adapters for older supported plugin APIs. Test a matrix of host versions against plugin API versions. Deprecate plugin methods with the same notice and removal discipline as ordinary public functions.

### Risk-based review and exceptional breaks

Classify changes by impact, likelihood, exposure, and reversibility. A low-frequency CLI output change can be severe if scripts parse it. A rarely used undocumented private helper is lower risk, unless telemetry, code search, or support tickets show broad reliance. A security vulnerability, legal requirement, or data-integrity issue may justify an accelerated break; document why, identify affected users, publish mitigations, and avoid using “security” as a blanket excuse for avoidable incompatibility.

### Case-study lessons from real projects

These are high-level design lessons from the roadmap's suggested cases, not a claim that every project follows an identical policy today:

- **Python 2 → 3:** a language/runtime transition demonstrates that migration tooling, dual-version transition periods, and clear ecosystem coordination can reduce friction, but some breaks are too fundamental for a simple alias.
- **pandas deprecations:** user-facing data workflows benefit from visible notices and staged migration; warnings need to explain the replacement and should be tested before removal.
- **NumPy 2.0:** large ecosystems need explicit migration guidance and automated assistance for common source changes; codemods help but cannot prove semantic correctness.
- **Django's staged deprecation approach:** a predictable release-based window helps downstream maintainers plan, provided the project states exactly how the window is counted.
- **Pydantic v1 → v2:** a compatibility namespace/layer can buy time for migration, but it adds maintenance cost and should have a defined support boundary.
- **Requests and stability promises:** a clear public contract can be a competitive advantage; maintainers should distinguish that commitment from a guarantee about every transitive dependency.

A case-study review should record: what changed, what was public, how long users had to migrate, what tools/docs existed, what remained incompatible, and what you would borrow for your own library. Verify current project policies from their official documentation before using these cases as evidence in a real policy decision.

## 6. Change-classification table

| Proposed change | Default risk | Rationale / review notes |
|---|---|---|
| Add a new public function | Usually low | Additive if it does not shadow an existing name or change import-time behaviour |
| Add optional keyword-only parameter with neutral default | Low–medium | Check wrappers, `**kwargs`, overloads, and default semantics |
| Rename a public function and remove old name immediately | High / breaking | Old imports and call sites fail |
| Keep old function as warning wrapper | Low during window | Usually source-compatible; warning policy and forwarding semantics must be tested |
| Rename a parameter used by keyword | High / breaking | `f(old_name=...)` stops working |
| Change default timeout from 10 seconds to 1 second | Medium–high | May change failures and runtime behaviour even though signature remains valid |
| Change timeout units from seconds to milliseconds | High / breaking | Same numeric value has a different meaning; configuration contract breaks |
| Add a new exception subclass under existing public base | Usually low | Existing catches of the base continue; exact-type checks may still break |
| Replace a documented exception with unrelated exception | High / breaking | Callers' recovery paths fail |
| Change return from `list[T]` to one-shot iterator | High / breaking | Indexing, repeated iteration, length, and materialization behaviour change |
| Add optional field to a versioned JSON object | Low–medium | Safe only if old readers tolerate unknown fields and new readers handle missing fields |
| Change meaning of existing JSON field | High / breaking | Old data becomes ambiguous; version or new field required |
| Move module but re-export old path | Low during window | Check introspection, pickles, type-checkers, and warning policy |
| Raise minimum Python version | High for affected users | Requires explicit support-policy change and migration window |
| Change internal private helper not documented/exported | Usually low | Still audit accidental exposure, downstream reliance, and implementation constraints |
| Change plugin protocol's required method | High / ecosystem-breaking | Host may stop loading third-party plugins; version and adapt the contract |
| Change log wording | Low to medium | Low unless logs are documented or machine-parsed; structured logs are stronger contracts |
| Change iteration order | Medium–high | Callers may depend on observed order; preserve if documented or widely relied on |
| Change `repr()` format | Context-dependent | Usually diagnostic, but breaking if documented or used for serialization/parsing |

“Default risk” is a starting hypothesis, not a substitute for impact analysis. Consider all supported consumer types and the library's actual promises.

## 7. `fetchkit` migration case study

### Initial API (hypothetical v0.1)

Assume `fetchkit` initially exposed a small API:

```python
# Historical public API in this teaching scenario
from urllib.request import urlopen


def fetch(url: str, timeout: float = 10.0) -> bytes:
    with urlopen(url, timeout=timeout) as response:
        return response.read()


def download_text(url: str, timeout: float = 10.0, encoding: str = "utf-8") -> str:
    return fetch(url, timeout).decode(encoding)
```

This API has issues beyond naming: `timeout` is positional-or-keyword, URL scheme/error handling is underspecified, and `download_text` calls the old API internally. The initial code is intentionally small; do not interpret it as the production implementation.

### Proposed breaking change

A maintainer proposes renaming `fetch` to `fetch_url`, renaming `download_text` to `fetch_text`, making `timeout` keyword-only, and adding a public exception hierarchy. Removing the old names in one release breaks imports and calls; making `timeout` keyword-only also breaks positional calls such as `fetch(url, 5.0)`. A better transition introduces the new API while preserving the old entry points, then separately schedules any signature tightening.

### Compatibility wrapper implementation

The runnable reference implementation for this lesson is in the accompanying examples in this Markdown: the `fetchkit/__init__.py` module below is self-contained for a compact exercise. It deliberately uses `urllib.request.urlopen`, which tests replace with a fake response; no network service is required for the test suite.

```python
# fetchkit/__init__.py — Python 3.12+
from __future__ import annotations

import warnings
from urllib.error import URLError
from urllib.request import urlopen

__version__ = "0.9.0"  # hypothetical teaching version

__all__ = [
    "FetchError",
    "FetchTimeoutError",
    "fetch_url",
    "fetch_text",
    "fetch",
    "download_text",
]


class FetchError(Exception):
    """Base exception for expected fetchkit request failures."""


class FetchTimeoutError(FetchError):
    """Raised when a request exceeds its configured timeout."""


def fetch_url(url: str, *, timeout: float = 10.0) -> bytes:
    """Fetch bytes from an absolute HTTP(S) URL.

    Raises:
        ValueError: If URL or timeout is invalid.
        FetchTimeoutError: If the request times out.
        FetchError: For other URL-opening failures.
    """
    import math
    from urllib.parse import urlsplit

    # TypeError distinguishes a wrong type from a numeric value outside the
    # documented domain. bool is excluded even though bool subclasses int.
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise TypeError("timeout must be a real number")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be finite and greater than zero")
    if not isinstance(url, str):
        raise TypeError("url must be a string")
    try:
        parts = urlsplit(url)
    except ValueError as exc:
        raise ValueError("url must be a valid absolute HTTP(S) URL") from exc
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("url must be an absolute HTTP(S) URL")
    try:
        with urlopen(url, timeout=timeout) as response:
            return response.read()
    except TimeoutError as exc:
        raise FetchTimeoutError(f"request timed out after {timeout:g}s") from exc
    except URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise FetchTimeoutError(f"request timed out after {timeout:g}s") from exc
        raise FetchError(f"request failed for {url!r}: {exc.reason}") from exc
    except OSError as exc:
        raise FetchError(f"request failed for {url!r}: {exc}") from exc


def fetch_text(url: str, *, timeout: float = 10.0, encoding: str = "utf-8") -> str:
    """Fetch text and decode bytes using the explicit encoding."""
    return fetch_url(url, timeout=timeout).decode(encoding)


def fetch(url: str, timeout: float = 10.0) -> bytes:
    """Deprecated alias for :func:`fetch_url`; planned removal in v2.0.0."""
    warnings.warn(
        "fetchkit.fetch() is deprecated since v0.5; use fetchkit.fetch_url(); "
        "the alias is planned for removal in v2.0.0. See the migration guide.",
        DeprecationWarning,
        stacklevel=2,
    )
    return fetch_url(url, timeout=timeout)


def download_text(url: str, timeout: float = 10.0, encoding: str = "utf-8") -> str:
    """Deprecated alias for :func:`fetch_text`; planned removal in v2.0.0."""
    warnings.warn(
        "fetchkit.download_text() is deprecated since v0.9; use fetchkit.fetch_text(); "
        "the alias is planned for removal in v2.0.0. See the migration guide.",
        DeprecationWarning,
        stacklevel=2,
    )
    return fetch_text(url, timeout=timeout, encoding=encoding)
```

This implementation's public surface intentionally keeps both old names in `__all__` during the transition. `__all__` does not prohibit other attributes from being accessed; the API policy and tests define the intended supported surface. The `fetch` wrapper intentionally retains its historical positional-or-keyword `timeout` parameter while forwarding it by keyword to the new API. The replacement uses a keyword-only parameter, but old callers can continue using `fetch(url, 5.0)` throughout the transition. This illustrates why a compatibility wrapper's signature may intentionally differ from the replacement signature. The `download_text` wrapper also retains its historical positional-or-keyword timeout and encoding parameters.

**Exception-contract caveat:** the minimal hypothetical `v0.1` sample above did not document its low-level exception types. The `v0.9` example defines a `FetchError` hierarchy and normalizes transport failures; that is only compatible if the earlier exception behaviour was not part of the supported contract. If the old release documented or intentionally exposed `urllib` exceptions, this implementation would need an adapter that preserves those old exceptions (and tests for them), or the exception normalization must be postponed to a separately announced breaking release. Never assume an undocumented exception is unused simply because it was undocumented; investigate downstream reliance and make the contract decision explicit.

The key rule: **a compatibility wrapper must accept the old call shapes**, even if the replacement API has a better signature.

### Two legacy APIs and their deprecation notices

- `fetch` → `fetch_url`: deprecated in hypothetical `v0.5`, warning on invocation, kept through `v1.x`, removal no earlier than hypothetical `v2.0.0`.
- `download_text` → `fetch_text`: deprecated in hypothetical `v0.9`, warning on invocation, kept through `v1.x`, removal no earlier than hypothetical `v2.0.0`.

The `v2.0.0` target is deliberately conservative: a pre-1.0 project should not imply that SemVer itself guarantees a `0.x` compatibility window. This hypothetical project voluntarily keeps the aliases across the whole `1.x` line and only removes them in the next major line, after a published policy review. If user demand or support evidence requires a longer window, extend it.

### Migration guide example

````markdown
# Migration guide: legacy fetch names

## `fetch` → `fetch_url`

Before:

```python
payload = fetchkit.fetch(url, timeout=5.0)
```

After:

```python
payload = fetchkit.fetch_url(url, timeout=5.0)
```

## `download_text` → `fetch_text`

Before:

```python
text = fetchkit.download_text(url, encoding="utf-8")
```

After:

```python
text = fetchkit.fetch_text(url, encoding="utf-8")
```

The old names warn during the transition and remain available throughout the documented v1.x window. Do not suppress the warning without scheduling the migration. The planned earliest removal is v2.0.0; check release notes before upgrading to that major line.
````

### Hypothetical release-by-release plan

| Release | Public API action | Compatibility promise and release gate |
|---|---|---|
| `v0.1` | Initial `fetch` and `download_text` functions | Pre-release API; document that the API is evolving, but do not imply users have no expectations |
| `v0.5` | Add `fetch_url`; keep `fetch` wrapper and emit `DeprecationWarning` on calls | Publish deprecation note, migration snippet, tests, and removal target; old calls still work |
| `v0.9` | Add `fetch_text`; deprecate `download_text` with its own warning | Keep the two deprecation timelines explicit; do not silently change return types/defaults |
| `v1.0` | Declare the supported public API stable; retain both deprecated wrappers | SemVer stable API policy starts; release gate includes snapshot, docs, warning tests, Python/dependency matrix |
| `v1.x` | Bug fixes and additive changes; maintain wrappers | Continue compatibility; removal needs an approved major-version plan, not merely elapsed time |
| `v2.0.0` | Earliest planned removal of `fetch` and `download_text` | Remove only if the published notice window and review criteria are met; highlight migration in release notes |

These are **hypothetical release milestones**, not actual `fetchkit` release history. A real project should count its deprecation window unambiguously (e.g., two subsequent minor releases after the warning first ships) and align removal with its support policy.

## 8. Tests and practical exercises

### Compatibility tests for the old and new paths

The core tests should verify:

- Explicit public exports exist and match the reviewed snapshot.
- New API returns the documented type and rejects invalid input clearly.
- Each legacy API emits the intended warning and forwards to the new implementation.
- Warnings point to the caller (`stacklevel=2`).
- Legacy calls preserve the old accepted call shape, including positional parameters if the historical signature allowed them.
- No external network is required: replace the transport with a deterministic fake.

Example pytest tests:

```python
import warnings
import pytest
import fetchkit


def test_legacy_fetch_warns_and_forwards(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return None
        def read(self): return b"payload"

    monkeypatch.setattr(fetchkit, "urlopen", lambda url, *, timeout: Response())
    with pytest.warns(DeprecationWarning, match="use fetchkit.fetch_url"):
        assert fetchkit.fetch("https://example.test/data") == b"payload"


def test_legacy_download_text_warns_and_forwards(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return None
        def read(self): return b"hello"

    monkeypatch.setattr(fetchkit, "urlopen", lambda url, *, timeout: Response())
    with pytest.warns(DeprecationWarning, match="use fetchkit.fetch_text"):
        assert fetchkit.download_text("https://example.test/data") == "hello"
```

These are illustrative tests. A complete suite should also check exception wrapping, timeout handling, invalid encodings, positional compatibility of legacy wrappers, and the precise warning filename/line. The additional checks below demonstrate those compatibility edges without a live network request.

```python
def test_legacy_fetch_keeps_positional_timeout_and_warns_at_caller(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return None
        def read(self): return b"payload"

    monkeypatch.setattr(fetchkit, "urlopen", lambda url, *, timeout: Response())
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        result = fetchkit.fetch("https://example.test/data", 2.5)
    assert result == b"payload"
    assert len(caught) == 1
    assert caught[0].category is DeprecationWarning
    assert caught[0].filename == __file__


def test_timeout_must_be_finite_and_positive(monkeypatch):
    import math

    for invalid in (0, -1, math.inf, -math.inf, math.nan):
        with pytest.raises(ValueError, match="finite and greater than zero"):
            fetchkit.fetch_url("https://example.test/data", timeout=invalid)
    with pytest.raises(TypeError, match="real number"):
        fetchkit.fetch_url("https://example.test/data", timeout=True)
```

The warning-location assertion checks the filename; a line-number assertion should compare against the exact call line in the test file rather than hard-code a number that will become stale when the test is edited.

### Public API snapshot check

For a small package, a committed JSON snapshot is a useful first guard. Run this script against the installed package from the same environment used for the tests, and review updates rather than blindly accepting them.

```python
# tools/dump_public_api.py
from __future__ import annotations

import inspect
import json
import fetchkit


def snapshot() -> dict[str, object]:
    names: dict[str, object] = {}
    for name in fetchkit.__all__:
        obj = getattr(fetchkit, name)
        if inspect.isclass(obj) or inspect.isfunction(obj):
            try:
                signature = str(inspect.signature(obj))
            except (TypeError, ValueError):
                # Some built-in/extension classes (including exception types)
                # do not expose an inspectable signature on every Python build.
                signature = None
            names[name] = {
                "kind": "class" if inspect.isclass(obj) else "function",
                "signature": signature,
                "annotations": {
                    key: repr(value) for key, value in getattr(obj, "__annotations__", {}).items()
                },
                "module": obj.__module__,
            }
        else:
            names[name] = {"kind": type(obj).__name__}
    # Keep package version outside the API baseline: otherwise every release
    # changes the snapshot even when the public API is identical.
    return {"exports": names}


print(json.dumps(snapshot(), indent=2, sort_keys=True))
```

Generate and review the expected snapshot with:

```bash
python tools/dump_public_api.py > api-snapshot.json
# Commit api-snapshot.json only after a maintainer reviews the API change.
python tools/dump_public_api.py > /tmp/api-snapshot-current.json
diff -u api-snapshot.json /tmp/api-snapshot-current.json
```

For CI, compare the generated output with the committed snapshot and fail when they differ. A simple shell implementation can use `diff -u`; a Python script can return nonzero when the JSON objects differ. Do not regenerate the snapshot automatically on every PR, because that would turn the guard into an approval bypass. This snapshot catches exported-name, inspectable function/class signature, and direct annotation changes, but not all docstrings, runtime behaviour, import paths, or serialization semantics. For built-in or extension classes whose signatures cannot be inspected, it records `null`; that is not proof their constructor contract is unchanged. It also does not model every overload, inherited member, or semantic annotation change; use `griffe` or a richer policy-specific checker when those details are contractual.

### Running compatibility checks in CI

```bash
python -m pytest -q
python -W error::DeprecationWarning -m pytest
python tools/dump_public_api.py > /tmp/api-snapshot-current.json
diff -u api-snapshot.json /tmp/api-snapshot-current.json
mypy --strict src/fetchkit tests
```

The commands assume the package, tests, snapshot, and `mypy` are installed/configured in that CI environment. The strict-warning command may reveal warnings from third-party dependencies; triage those narrowly. Do not claim the checks pass unless they were run.

### Compatibility matrix template

| Axis | Minimum supported | Latest supported | Additional release gate |
|---|---|---|---|
| Python | Lowest declared Python version | Newest supported Python | Import, unit, typing, and docs tests |
| Runtime dependency | Lowest supported version | Current compatible version | Lock/constraints review for known incompatibilities |
| Public API | Previous supported release's examples | Candidate release | Old API smoke tests + API diff |
| Plugin contract | Oldest supported plugin API | Current plugin API | Host × plugin compatibility matrix |
| Serialized data | Oldest supported schema fixture | Current schema | Read old fixtures; verify unknown-field policy |

### Exercises

1. **Classify ten changes.** Select ten rows from Section 6. Mark each as compatible, breaking, or context-dependent; explain the consumer code that could fail and the mitigation.
2. **Rename a function safely.** Deprecate a public function with a wrapper, warning, test, changelog entry, migration guide, and a removal timeline. Include a positional-call test if the old signature allowed positional arguments.
3. **Build an API-diff check.** Tag or install two versions of a real open-source library in separate virtual environments. Extract names and signatures with `griffe` or an inspection script, compare the results, and manually classify each difference. Never treat every diff as automatically breaking or every no-diff as safe.
4. Add a CI matrix for minimum/latest Python and dependencies; document which compatibility axes are not covered.
5. Propose an RFC for a change that must break compatibility due to a security issue. Include a mitigation, communication plan, and rationale for shortening the normal deprecation period.

## 9. Common mistakes

These three mistakes are explicitly called out by the roadmap:

1. **Removing something because “nobody uses it” without checking telemetry.** Usage data may be absent, incomplete, privacy-limited, or skewed toward a subset of users. Combine evidence sources—code search, issue/support history, opt-in telemetry, and ecosystem feedback—and still provide a clear notice period.
2. **Making silent behavioural changes under unchanged signatures.** A function can keep the same name and type hints while changing defaults, ordering, exception behaviour, units, laziness, or side effects. Test observable behaviour, not just the signature.
3. **Deprecating without telling users how to migrate.** A warning without a replacement, example, target timeline, and migration guide transfers the design work to users and erodes trust.

Additional traps:

- Removing a deprecated API before the stated window expires.
- Using `DeprecationWarning` but assuming users necessarily see it.
- Warning at import time and producing noise for code that does not call the deprecated function.
- Letting the new implementation call the old wrapper internally, causing warnings for new callers.
- Writing a wrapper that accidentally stops accepting positional arguments or changes defaults.
- Updating an API snapshot without reviewing the diff.
- Relying on an API-diff tool to detect behavioural or data-format changes.
- Claiming `0.x` releases automatically owe no compatibility, or conversely assuming SemVer itself gives a `0.x` API a stable promise.
- Changing plugin contracts without testing external plugins or offering adapters.
- Treating undocumented implementation details as guaranteed contracts—or dismissing a documented/publicly exported name as “internal.”

## 10. Self-check questions with model answers

### 1. Classify ten listed changes as breaking/non-breaking and defend borderline cases.

**Model answer:** There is no single answer without the published contract and consumer context. Removing a public function is breaking; adding a new function is normally additive. Adding an optional keyword-only parameter is usually compatible if its default preserves old behaviour, but it may collide with wrappers forwarding arbitrary `**kwargs`. Changing a default timeout may be source-compatible but behaviour-breaking. Changing an exception from a documented base class to an unrelated type is breaking. Adding an exception subclass under the existing base is often compatible for callers catching the base, but may affect exact-type checks. Changing a list to a generator is breaking for consumers that index or iterate twice. Adding an optional JSON field can be compatible for tolerant readers, but strict schema validators may reject it. Moving a module is compatible only if the old import path remains usable for the promised window. Raising the minimum Python version breaks users on dropped versions. State the dimension, evidence, and mitigation for every borderline case.

### 2. Implement a rename of a public function with alias, warning, test, changelog and removal timeline.

**Model answer:** Add the new function first. Keep the old name as a forwarding wrapper that accepts the old signature, calls `warnings.warn(..., DeprecationWarning, stacklevel=2)`, and delegates to the replacement. Test the warning, caller stack location, return value, exception behaviour, and old call forms. Add a `Deprecated` changelog entry and migration guide with before/after examples. State the first deprecated version and earliest removal release. Do not remove the wrapper until the project's published notice period and release policy permit it.

### 3. Build the API-diff check and run it on two tagged versions of an open-source library.

**Model answer:** Create isolated environments for both tagged releases so import resolution cannot mix versions. Use `griffe` or an inspection script to export public names, signatures, and—if policy requires—annotations. Compare outputs and fail CI on unreviewed differences. Then manually classify each diff: a changed signature may be breaking, a new function may be additive, and a diff-free change can still alter behaviour. Save the approved baseline, pin the tool version, and document any intentional changes with release notes and tests.

## 11. Summary and completion checklist

Backward compatibility is a promise about observable contracts, not just function names. A good policy makes that promise explicit, gives users a migration path, and automates the checks that are practical to automate. Warnings, wrappers, API snapshots, compatibility matrices, and release notes work together; none replaces maintainer judgement.

Before marking the lesson complete:

- [ ] I can identify source, behavioural, typing, import, configuration, serialization, and operational compatibility risks.
- [ ] I can explain how SemVer differs from a project's voluntary `0.x` policy.
- [ ] I can write a useful `DeprecationWarning` with correct `stacklevel` and a tested forwarding wrapper.
- [ ] I can test both old and new APIs during a transition.
- [ ] I can write a migration guide and release note with a specific removal timeline.
- [ ] I can run and review a public API snapshot or `griffe` diff.
- [ ] I can describe the supported Python/dependency/plugin compatibility matrix.
- [ ] I know when security, legal, or data-integrity constraints may require an accelerated break and how to communicate it.
- [ ] I have answered all three self-check questions and completed the practical exercises.

## 12. Authoritative references

Use official documentation to verify exact tool behaviour and current project policies before making a production decision.

- [Semantic Versioning 2.0.0](https://semver.org/) — version-number contract; read the `0.y.z` section carefully.
- [Python `warnings` documentation](https://docs.python.org/3/library/warnings.html) — warning categories, filters, and stack levels.
- [Python `inspect.signature`](https://docs.python.org/3/library/inspect.html#inspect.signature) — runtime signature inspection for API snapshots.
- [Python Packaging User Guide](https://packaging.python.org/) — package metadata and release/distribution guidance.
- [Griffe documentation](https://mkdocstrings.github.io/griffe/) — API extraction and compatibility checking.
- [NumPy 2.0 migration guide](https://numpy.org/devdocs/numpy_2_0_migration_guide.html) — large-scale API/runtime migration guidance.
- [pandas deprecation policy](https://pandas.pydata.org/docs/development/policies.html) — consult the current development policy for deprecation conventions.
- [Django deprecation policy](https://docs.djangoproject.com/en/stable/internals/release-process/#deprecation-policy) — release-based deprecation guidance; check the current stable docs.
- [Pydantic migration guide](https://docs.pydantic.dev/latest/migration/) — v1-to-v2 migration and compatibility namespace discussion.
- [Requests documentation](https://requests.readthedocs.io/) — public API and usage documentation for a widely used HTTP library.
- [Python `urllib.request` documentation](https://docs.python.org/3/library/urllib.request.html) — behaviour of the transport used in the case study.

The roadmap also points to Module 1.6 and Module 1.18 for SemVer/versioning, and Module 1.15 for warning mechanics. Revisit those lessons when writing the actual project's policy.
