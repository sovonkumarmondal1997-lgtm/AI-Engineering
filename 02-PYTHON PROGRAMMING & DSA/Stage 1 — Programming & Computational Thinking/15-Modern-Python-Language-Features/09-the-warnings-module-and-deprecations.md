# Lesson 09 — The `warnings` Module and Deprecations

> **Version policy:** examples target Python 3.12+. `warnings.deprecated` is available in the standard library from **Python 3.13** (PEP 702). For older Python versions, use `typing_extensions.deprecated` when its runtime behavior fits, or emit a warning explicitly. Test the exact behavior against the versions your package supports.
>
> **Roadmap alignment:** this lesson follows Lesson 09 in `roadmap-Modern-Python-Language-Features.md`: warning categories and filters, `stacklevel`, deprecated API decorators, tests and CI, module-level `__getattr__`, resource warnings, lifecycle policy, filter state, dependency warnings, migration tools, and observability.

## Learning objectives

By the end of this lesson, you can:

- distinguish a warning from an exception and choose a useful category;
- emit warnings that identify the consumer's call site;
- configure filters without accidentally hiding important signals;
- test warning category, message, count, and location;
- deprecate functions, classes, parameters, attributes, and behavior changes;
- write a staged migration plan and enforce it in CI;
- explain warning registries, filter state, and operational limitations.

## 1. Warnings are signals, not failed operations

An **exception** interrupts ordinary execution unless it is caught. A **warning** normally reports a condition and allows execution to continue. Warning filters can change that behavior: an `error` filter turns a matching warning into an exception.

Use warnings when a program can continue but a caller should know about a questionable or soon-to-change behavior. Use exceptions when the operation cannot safely or meaningfully proceed.

```python
import warnings

warnings.warn("configuration key 'colour' is deprecated; use 'color'", DeprecationWarning)
print("the program continues unless the warning is filtered as an error")
```

Typical output when the warning is visible includes a filename, line number, category, and message, followed by:

```text
the program continues unless the warning is filtered as an error
```

The warning line itself is not guaranteed to appear. Visibility depends on category, filter rules, execution context, warning registries, interpreter flags, and test-runner configuration.

## 2. Warning categories and intended audiences

| Category | Typical use | Default visibility considerations |
|---|---|---|
| `UserWarning` | Unexpected or noteworthy application/user condition without a more specific category | Usually visible under the default filter |
| `DeprecationWarning` | Library/developer-facing API is deprecated | Commonly ignored outside `__main__`; test runners may change filters |
| `FutureWarning` | Behavior change that should reach application end users | Usually visible under the default filter |
| `RuntimeWarning` | Suspicious runtime behavior, such as certain numerical conditions | Usually visible under the default filter |
| `ResourceWarning` | Resource lifecycle issue, such as an unclosed file/socket | Usually ignored by default in normal execution; development mode can expose more of these |
| `PendingDeprecationWarning` | Early notice before a formal deprecation policy is activated | Commonly ignored by default |

Do not choose a category solely because it is visible. Match the audience and contract. For public libraries, `DeprecationWarning` is generally appropriate for developers upgrading code. `FutureWarning` is often better when an end-user-facing behavior change needs to be seen in ordinary application runs.

### Default filters are contextual

Python's initial warning filters include special handling for `DeprecationWarning` in `__main__`; other contexts often ignore it. `ResourceWarning` and `PendingDeprecationWarning` are commonly ignored. Filters may be changed by `-W`, `PYTHONWARNINGS`, `-X dev`, code calling `warnings`, `site` configuration, and frameworks such as pytest. A warning is not an alerting system and must not be assumed to be visible to every consumer.

## 3. Emit a useful warning with `warnings.warn`

The core interface is:

```python
warnings.warn(message, category=UserWarning, stacklevel=1)
```

- `message`: what is wrong or changing, ideally with the replacement and migration path.
- `category`: a warning class, usually a subclass of `Warning`.
- `stacklevel`: how many frames to step outward when reporting the source location. For a wrapper called by user code, `stacklevel=2` usually points to the user's call site instead of the wrapper.

### A consistent API-renaming example

Imagine package `acme_text` renames `normalize_legacy()` to `normalize_text()`. Keep the old function as a forwarding wrapper during the grace period.

```python
# acme_text/normalize.py
import warnings

def normalize_text(value: str) -> str:
    """Normalize whitespace using the current public API."""
    return " ".join(value.split())


def normalize_legacy(value: str) -> str:
    """Deprecated: use normalize_text()."""
    warnings.warn(
        "normalize_legacy() is deprecated; use normalize_text() instead. "
        "It is planned for removal in acme-text 3.0.",
        DeprecationWarning,
        stacklevel=2,
    )
    return normalize_text(value)
```

Calling `normalize_legacy("  hello   world ")` returns `'hello world'` and emits a `DeprecationWarning` when the active filters allow it. The warning location should be the caller's line. Forwarding preserves behavior while giving consumers a migration signal.

**Compatibility note:** do not change the old function's behavior at the same time you announce a name deprecation unless the behavior change is separately specified and tested. Deprecation is easier to adopt when the old call remains functionally equivalent.

### `stacklevel` and helper functions

If every deprecation uses a shared helper, account for the extra stack frame. `stacklevel=2` inside a helper points to the helper's caller, which may itself be a wrapper; use `skip_file_prefixes` on supported Python versions when a more robust package-internal-frame skip is useful, or compute/document a correct stack level. Do not blindly copy `stacklevel=2` into deeply nested helper layers.

## 4. Filters: decide what happens to a warning

The standard warning actions are:

| Action | Effect |
|---|---|
| `default` | Show a matching warning for each source location, generally once per location and warning category/message according to the warning registry |
| `always` | Show every occurrence |
| `once` | Show only the first occurrence for the warning message/category across locations, subject to registry behavior |
| `module` | Show once per module for the warning message/category |
| `ignore` | Suppress matching warnings |
| `error` | Raise the warning as an exception |

The exact suppression scope involves the warning registry and filter state; do not use these actions as a precise event-counting mechanism.

### Configure warnings in code

```python
import warnings

warnings.simplefilter("default", DeprecationWarning)
warnings.filterwarnings(
    "error",
    message=r".*normalize_legacy.*",
    category=DeprecationWarning,
)
```

`simplefilter()` adds a broad rule. `filterwarnings()` can narrow a rule by message, category, module, and line. Filter order matters: filters are normally checked in order, and newer inserted rules are often placed before existing rules unless `append=True` is used. Read configuration carefully when multiple rules overlap. **Important:** a module filter matches the module associated with the reported warning location. If a library uses `stacklevel=2` to point at consumer code, a module filter for the library may not match that warning; test the actual call path before relying on module-scoped enforcement.

### Command-line and environment configuration

Examples:

```bash
# Show deprecation warnings in a developer run
python -Wd -m my_application

# Treat all warnings as errors for a focused run
python -W error -m pytest

# Set a process-level filter (shell syntax varies by platform)
PYTHONWARNINGS=default::DeprecationWarning python -m my_application
```

`-W` options and `PYTHONWARNINGS` have a defined filter syntax; category names and module patterns must be valid. For a project-specific CI rule, prefer pytest configuration or a narrowly scoped filter over permanently changing the environment for every Python process.

### Temporarily capture or alter warnings

```python
import warnings

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    warnings.warn("example", UserWarning)

assert len(caught) == 1
assert caught[0].category is UserWarning
assert str(caught[0].message) == "example"
```

`catch_warnings()` is useful for tests and small local scopes, but warning filters and registries are process-level state. Do not use it as an isolation boundary for unrelated concurrent tasks. In particular, concurrent mutation of global warning configuration can cause surprising interactions; test on the Python versions you support and avoid changing filters in request-handling hot paths.

## 5. Decorator-based deprecation: Python 3.13+

PEP 702 adds `warnings.deprecated` in Python 3.13. It marks an API as deprecated for static analyzers and emits a runtime warning when the decorated function is called, class instantiated, or class subclassed, depending on the decorated object. The warning category defaults to `DeprecationWarning` and can be selected explicitly.

```python
# Python 3.13+
from warnings import deprecated

@deprecated("Use normalize_text() instead; removal planned for acme-text 3.0.")
def normalize_legacy(value: str) -> str:
    return normalize_text(value)
```

For a class, annotate the class definition with the decorator; for a function, annotate the function. Verify runtime behavior and static-checker support in your toolchain: type checkers and IDEs can surface deprecations even when runtime warnings are hidden.

### Python 3.12 and earlier-compatible alternatives

`typing_extensions.deprecated` provides a compatible decorator for older Python versions, but package behavior depends on the installed `typing_extensions` version and the use case. It marks the object for static tooling and can emit runtime warnings. If your project cannot depend on it, use an explicit wrapper with `warnings.warn(..., DeprecationWarning, stacklevel=2)`.

```python
from typing_extensions import deprecated  # external dependency

@deprecated("Use normalize_text() instead")
def normalize_legacy(value: str) -> str:
    return normalize_text(value)
```

Keep the supported Python range and `typing_extensions` dependency in project metadata and CI. Avoid claiming that a decorator is available on every Python version simply because its typing metadata is understood by a type checker.

## 6. Test warning contracts with pytest

Test the category and message. Also test the replacement behavior, and when relevant, the reported location.

```python
# tests/test_normalize.py
import pytest
from acme_text.normalize import normalize_legacy, normalize_text

def test_new_api():
    assert normalize_text("  hello   world ") == "hello world"

def test_legacy_api_warns_and_forwards():
    with pytest.warns(DeprecationWarning, match=r"normalize_legacy\(\).*normalize_text") as record:
        result = normalize_legacy("  hello   world ")

    assert result == "hello world"
    assert len(record) == 1
    assert record[0].category is DeprecationWarning
    assert "removal" in str(record[0].message)
```

The regular expression is matched against the warning message; escape parentheses when you mean literal parentheses. `pytest.warns()` temporarily enables capture for the expected category, so a warning can be asserted even if it is normally ignored by the interpreter's default filters.

### Assert the call-site location

```python
def test_warning_points_to_consumer_line():
    with pytest.warns(DeprecationWarning) as record:
        expected_lineno = __import__("inspect").currentframe().f_lineno + 1
        normalize_legacy("x")

    assert record[0].filename == __file__
    assert record[0].lineno == expected_lineno
```

This test is deliberately sensitive to source edits; keep the line calculation adjacent to the call. A simpler test can assert only filename or line range if exact-line assertions would be brittle in your test layout.

### Treat warnings as errors in tests

`pytest.ini` example:

```ini
[pytest]
filterwarnings =
    error
    ignore::DeprecationWarning:known_noisy_dependency
```

This makes warnings errors by default, with a targeted exception for a known dependency. Filter precedence matters: pytest's filter entries and command-line options can override one another. Prefer narrow exceptions with an issue and expiry date; do not ignore all deprecations to keep CI green.

A command-line alternative is:

```bash
python -W error -m pytest
```

Use a separate CI job for stricter policies if the full dependency tree currently emits warnings that your project cannot yet fix. Do not confuse “warning did not fail the build” with “warning is harmless.”

## 7. Deprecating different public API shapes

### Functions and classes

Use the decorator on Python 3.13+, `typing_extensions.deprecated` for supported older environments, or a manual wrapper. Keep the old name documented and forwarding until the announced removal version.

### Parameters

Python does not have a built-in decorator that automatically deprecates one individual function parameter. Detect the old parameter at runtime, warn, and translate it to the replacement parameter. Preserve validation and avoid ambiguous combinations.

```python
import warnings

_SENTINEL = object()

def connect(*, timeout=_SENTINEL, timeout_seconds=_SENTINEL):
    if timeout is not _SENTINEL and timeout_seconds is not _SENTINEL:
        raise TypeError("pass only one of timeout and timeout_seconds")
    if timeout is not _SENTINEL:
        warnings.warn(
            "connect(timeout=...) is deprecated; use timeout_seconds=...",
            DeprecationWarning,
            stacklevel=2,
        )
        timeout_seconds = timeout

    if timeout_seconds is _SENTINEL:
        timeout_seconds = 10
    return {"timeout_seconds": timeout_seconds}
```

The sentinel distinguishes “not supplied” from an explicit `None`. If `None` has a special meaning in the API, keep that behavior explicit. In a real implementation, add type annotations and validation matching the library's contract.

### Attributes and properties

A deprecated property can warn on access while preserving a route to the replacement. Ensure setters and deleters are covered if they are part of the public contract.

```python
import warnings

class Client:
    @property
    def old_endpoint(self) -> str:
        warnings.warn(
            "Client.old_endpoint is deprecated; use Client.endpoint",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.endpoint

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint
```

This example deprecates reads only. If the old attribute used to be writable, a migration may require a setter that warns and updates `endpoint`; silently removing write behavior is a separate breaking change.

### Module-level names and `__getattr__` (PEP 562)

At module scope, Python calls `__getattr__(name)` when normal attribute lookup fails. It can keep a renamed import working and emit a warning:

```python
# acme_text/__init__.py
import warnings
from .normalize import normalize_text

__all__ = ["normalize_text", "normalize_legacy"]

def __getattr__(name: str):
    if name == "normalize_legacy":
        # Return the forwarding wrapper; it warns when called, with a useful call-site.
        from .normalize import normalize_legacy
        return normalize_legacy
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

This is a compatibility bridge for missing module attributes, not a universal interception hook:

- it does not intercept names that already exist in the module's global dictionary;
- it does not intercept ordinary global-name lookup inside the module itself;
- it is called for module attribute access, including many `from module import name` cases, but tooling and introspection may behave differently;
- `from acme_text import normalize_legacy` binds the returned object in the importing module, so later uses of that local binding do not trigger module `__getattr__` again;
- `dir()` listing and star-import behavior need deliberate support (`__all__`, and optionally `__dir__`).

In this example, the module-level lookup does not itself warn: the forwarding function warns when called, which gives `stacklevel=2` a useful consumer call site. If you instead warn inside `__getattr__` as well as inside the function, importing the old name and calling it can produce two warnings. Choose one clear warning boundary or explicitly test the two distinct events. Avoid warning on every introspection path unless that is intended.

## 8. `ResourceWarning`, development mode, and logging

`ResourceWarning` is useful for resource lifecycle defects such as unclosed files or sockets. It is commonly hidden by default in ordinary runs. Development mode (`python -X dev`) enables additional runtime checks and changes warning behavior, making it useful in CI and local diagnostics.

```bash
python -X dev -m pytest
```

This is a diagnostic mode, not a replacement for correct resource management. Prefer context managers (`with open(...) as file:`) and deterministic cleanup.

### Forward warnings to logging

```python
import logging
import warnings

logging.basicConfig(level=logging.WARNING)
logging.captureWarnings(True)
warnings.warn("deprecated option used", DeprecationWarning, stacklevel=1)
```

`logging.captureWarnings(True)` routes warnings through the `py.warnings` logger. Configure that logger's level and handlers as part of your logging setup. It does not make ignored warnings visible; the warning must pass the warning filters before it is forwarded. If warning records are sent to a central system, avoid including secrets in warning messages.

## 9. The full deprecation lifecycle

A warning alone is not a lifecycle. A safe API change has a public rationale, migration path, release policy, tests, and an explicit removal decision.

### Example release plan: rename `normalize_legacy()`

| Phase | Release | Action |
|---|---|---|
| Announcement | `2.4` | Add `normalize_text()`, document both names, publish a migration note, and keep old behavior working |
| Grace period | `2.5` and `2.6` | Emit `DeprecationWarning` from old name; add examples and codemod guidance; collect usage signals |
| Removal decision | Before `3.0` | Review support policy, downstream reports, telemetry, and release notes; announce removal date |
| Removal | `3.0` | Remove the old name in a major release, publish migration steps, and keep a clear error for accidental stale imports where feasible |

This is an example, not a universal mandate. The roadmap recommends a grace period of at least two minor releases or 6–12 months, with removal in a major release. Follow your published compatibility policy and the risk profile of your consumers. Security fixes or legal requirements may need a different schedule, but explain the exception.

### Release checklist

1. **Announce:** changelog entry, API docs, reason, replacement, and planned removal release/date.
2. **Add replacement:** ensure it is feature-complete and tested before warning consumers away from the old API.
3. **Warn precisely:** select the right category, message, `stacklevel`, and runtime/static deprecation mechanism.
4. **Provide migration guidance:** old/new code snippets, parameter mapping, behavior differences, and automated migration if safe.
5. **Test both paths:** new API has no deprecation warning; old API warns and preserves behavior during the grace period.
6. **Monitor:** review issue reports, downstream compatibility tests, package downloads, opt-in telemetry, and support requests.
7. **Remove deliberately:** align with the announced release policy and publish a final migration note.

### Migration note example

````markdown
## Deprecated: `normalize_legacy()`

`normalize_legacy()` is deprecated as of acme-text 2.4 and is planned for
removal in 3.0. Use `normalize_text()` instead.

Before:

```python
from acme_text import normalize_legacy
value = normalize_legacy(raw_text)
```

After:

```python
from acme_text import normalize_text
value = normalize_text(raw_text)
```

The replacement preserves whitespace-normalization behavior. If you rely on
any undocumented edge case, run your regression suite before upgrading.
````

The changelog should state the first release with the warning, the planned removal release, and any behavioral difference. Avoid an indefinite “will be removed in a future release.”

## 10. Warning state, registries, and concurrency

Warnings are controlled by both an ordered filter list and per-module warning registries (commonly exposed as `__warningregistry__`). The registry helps suppress repeats according to the selected action. This has practical consequences:

- running the same code twice in one process may not display the same warning twice;
- `default`, `once`, and `module` are suppression policies, not durable usage counters;
- changing filters can alter visibility, and a module registry can affect repeated tests;
- reloading modules or clearing registries can change observed behavior, but should not be the basis of production monitoring;
- warning filters are process-wide configuration, so unrelated code can influence them.

`catch_warnings()` is convenient for a local test, but do not treat it as a task-local context manager in concurrent application logic. Newer Python versions have improved context-aware behavior in some configurations, but concurrency semantics and interpreter settings vary by version. The robust policy is to configure filters during process startup and avoid frequent runtime mutation.

## 11. Library authors versus applications

**Library authors** should emit the appropriate category, select a useful call site, document the replacement and removal schedule, and avoid globally overriding their consumers' warning filters.

**Application owners** decide which warnings are visible, logged, promoted to errors, or temporarily filtered. Applications should generally expose warnings during development and tests, then define explicit production handling.

### Enforce deprecation policy in CI

A module-only pytest filter is not always reliable for a library's deprecations: a correctly chosen `stacklevel=2` attributes the warning to consumer code, not to `acme_text`. A robust baseline is to make warnings errors and add only narrow, temporary exceptions for known dependency noise:

```ini
[pytest]
filterwarnings =
    error
    ignore::DeprecationWarning:known_noisy_dependency
```

This policy is intentionally broad: it catches warnings regardless of the module where they are reported, except for the explicit dependency exception. Keep that exception tracked with an issue, owner, and expiry date. Verify precedence with the pytest version used in CI and retain focused tests for your own deprecated wrappers. If you need a narrower rule, match a stable warning message or test the relevant API directly rather than assuming the warning's module will remain the library module.

Do not use `ignore::DeprecationWarning` globally. If a dependency emits noise, prefer upgrading it, reporting the warning upstream, or adding a narrow module/message filter with an issue, owner, and expiry date. Test periodically against upcoming Python and dependency releases to find future incompatibilities early.

### Monitoring deprecated API usage

Warnings are not reliable telemetry by themselves because they may be filtered and suppressed. Options include:

- downstream integration tests and reverse-dependency CI;
- opt-in, privacy-reviewed telemetry with a versioned event name;
- counting explicit calls in a compatibility wrapper, if overhead and concurrency are understood;
- support tickets, issue searches, and migration feedback.

Never include argument values, tokens, user data, or other secrets in telemetry. Explain what is collected, minimize retention, and offer opt-out where appropriate. Do not infer that zero visible warnings means zero usage.

## 12. Behavior changes and `FutureWarning`

Use `FutureWarning` when a change affects application end users and should normally be visible in ordinary execution. State the current behavior, the future behavior, when it changes, and how to opt in or retain the old behavior during the transition.

```python
import warnings

def parse_record(text: str, *, strict: bool = False) -> dict[str, str]:
    if not strict:
        warnings.warn(
            "parse_record() will default to strict parsing in 3.0; "
            "pass strict=True now to adopt it early",
            FutureWarning,
            stacklevel=2,
        )
        # Legacy behavior: accept unstructured text.
        return {"text": text}

    # New behavior: require a key=value record.
    key, separator, value = text.partition("=")
    if not separator or not key.strip():
        raise ValueError("expected a non-empty key=value record")
    return {key.strip(): value.strip()}
```

For example, `parse_record("hello")` follows the legacy path and warns, while `parse_record("hello", strict=True)` raises `ValueError`; `parse_record("name = Ada", strict=True)` returns `{"name": "Ada"}` without a transition warning. Do not emit a `FutureWarning` indefinitely: provide an explicit opt-in path, measure adoption, and remove the transition warning when the new behavior becomes the default.

## 13. Automated migration: Ruff and LibCST

Automated edits are useful when the transformation is deterministic. Ruff has rules and fixes for selected modernization patterns, and LibCST can build codemods that preserve formatting and comments. Neither tool can safely infer every semantic change from a deprecation message.

A safe codemod workflow:

1. specify the exact source-to-source transformation and supported syntax;
2. test against representative fixtures, including comments, aliases, multiline calls, and edge cases;
3. run the codemod on a branch and inspect the diff;
4. run formatters, static checks, unit tests, and integration tests;
5. provide a manual fallback for cases the codemod cannot prove safe.

Do not claim that enabling Ruff alone migrates every deprecated third-party API. Check the selected Ruff version, rule set, and whether the relevant rule has a fix.

## 14. Common mistakes and trade-offs

- **Wrong category:** `DeprecationWarning` is often hidden in imported application code; `FutureWarning` is intended for user-visible behavior transitions.
- **Wrong location:** forgetting `stacklevel` makes users inspect library internals instead of their own call.
- **Warning spam:** emitting on every inner-loop call can overwhelm logs; do not silently suppress it without a documented policy.
- **No replacement:** “this is deprecated” without a concrete replacement or removal schedule is not actionable.
- **Breaking behavior too early:** forwarding wrappers should normally preserve old behavior during the grace period.
- **Global suppression:** broad ignores can hide unrelated warnings and future Python incompatibilities.
- **Testing only visibility:** tests should verify category, message, behavior, and useful location—not merely that some warning appeared.
- **Assuming telemetry:** warning filters and registries mean observed warnings are not a complete usage count.
- **Overpromising decorators:** static deprecation markers do not guarantee every editor or type checker reports the warning; runtime visibility is independently filtered.

## 15. Practical comparison table

| Mechanism | Best for | Limitation |
|---|---|---|
| `warnings.warn()` | Custom runtime warnings and parameter/attribute deprecation | Requires correct category, stack level, and tests |
| `warnings.deprecated` (3.13+) | Marking functions/classes deprecated for static tools and runtime | Not available in Python 3.12; tool support varies |
| `typing_extensions.deprecated` | Cross-version deprecation metadata/decorator | Requires dependency and compatibility testing |
| `pytest.warns()` | Asserting warning category and message | Captures expected warnings; does not prove ordinary-run visibility |
| `-W error` / pytest `filterwarnings` | CI enforcement | May expose noisy dependencies; filters need careful scope |
| Module `__getattr__` | Deprecated module-level names and import compatibility | Only handles missing module attributes; not every access path |
| Changelog + migration guide | Communicating lifecycle and replacement | Cannot enforce runtime behavior alone |
| Telemetry / downstream CI | Estimating adoption and ecosystem impact | Privacy, coverage, and sampling limitations |

## 16. Exercises

### Exercise 1 — Write a warning wrapper

Implement `old_slug(text)` that warns with `DeprecationWarning`, points to its caller, and returns the same result as `slugify(text)`.

### Exercise 2 — Test a warning

Write a pytest test that asserts the warning category, matches `old_slug`, and confirms the output remains unchanged.

### Exercise 3 — Filter policy

A third-party dependency emits `DeprecationWarning` from `noisy_dep.compat`. Your own package must treat its deprecations as errors. Write a pytest filter configuration that scopes the rules and explain why broad suppression is risky.

### Exercise 4 — Design the lifecycle

Your library renames `connect(timeout=...)` to `connect(timeout_seconds=...)`. Draft a three-release lifecycle with migration docs and a removal criterion.

### Exercise 5 — Module compatibility

Explain what module `__getattr__` can preserve for a renamed export and name two access paths it does not continuously intercept.

## 17. Worked solutions

### Solution 1

```python
import warnings

def slugify(text: str) -> str:
    return "-".join(text.lower().split())

def old_slug(text: str) -> str:
    warnings.warn(
        "old_slug() is deprecated; use slugify() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return slugify(text)

assert old_slug("Hello World") == "hello-world"
```

The assertion is about return behavior. In a normal imported-module run the `DeprecationWarning` may be hidden, while `pytest.warns()` can capture it.

### Solution 2

```python
import pytest

def test_old_slug_warns():
    with pytest.warns(DeprecationWarning, match=r"old_slug\(\).*slugify"):
        assert old_slug("Hello World") == "hello-world"
```

The test checks the category and the migration message while ensuring the wrapper still forwards correctly.

### Solution 3

```ini
[pytest]
filterwarnings =
    default::DeprecationWarning
    ignore::DeprecationWarning:noisy_dep\.compat
    error::DeprecationWarning:acme_text(\.|$)
```

Keep the dependency exception narrow, tracked, and temporary. Filter order and warning source location matter; validate this configuration with the pytest version in CI. Do not ignore every `DeprecationWarning`, because doing so hides both your package's regressions and upstream compatibility signals.

### Solution 4

- Release `2.4`: add `timeout_seconds`, document both forms, announce removal in `3.0`.
- Releases `2.5` and `2.6`: warn when `timeout` is supplied, reject ambiguous simultaneous values, publish examples and a codemod if the call shape is deterministic.
- Before `3.0`: review downstream test results and opt-in usage metrics, announce the final date, and verify migration docs.
- Release `3.0`: remove `timeout`, include a clear error for stale usage where feasible, and document the breaking change.

This follows the roadmap's example of at least two minor releases or 6–12 months of grace where the package's compatibility policy permits it.

### Solution 5

Module `__getattr__` can return a deprecated alias when a module attribute is missing, allowing some old import forms to continue to work while warning. It does not intercept an attribute already present in the module dictionary, and after `from module import old_name` binds the object locally, later uses of that local variable do not re-enter module `__getattr__`. It also does not intercept ordinary global-name lookup inside the module itself.

## 18. Final checklist

Before shipping a deprecation:

- [ ] Is the warning category appropriate for the intended audience?
- [ ] Does the message name the replacement and planned removal release?
- [ ] Does `stacklevel` identify the consumer's call site?
- [ ] Does the old API preserve behavior during the grace period?
- [ ] Are category, message, output, and location tested?
- [ ] Is the warning policy enforced in CI without globally silencing dependencies?
- [ ] Are changelog and migration documentation published?
- [ ] Is the removal decision informed by compatibility policy and evidence?
- [ ] Are telemetry and logging privacy-safe?
- [ ] Has the behavior been tested across the package's supported Python versions?

**Key principle:** deprecation is a managed compatibility process—not just a call to `warnings.warn()`.
