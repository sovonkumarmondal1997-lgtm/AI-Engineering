# Python Version Differences: 3.10 to 3.14

> **Repository policy:** new code targets **Python 3.12+**. This lesson also explains Python 3.10 and 3.11 so engineers can maintain older applications, publish compatible libraries when required, and plan upgrades safely.
>
> **Facts checked:** 17 October 2026. Release status changes over time; re-check the official status page before making a support-policy decision. The feature tables describe CPython's language and standard-library availability unless noted otherwise.

## Learning objectives

By the end of this lesson, you should be able to:

1. Read Python release schedules and official “What's New” pages efficiently.
2. Identify the first Python version that supports a syntax feature, standard-library API, or typing feature.
3. Explain the difference between syntax compatibility, runtime API availability, and third-party dependency compatibility.
4. Declare a truthful minimum version in package metadata and align it with source code and CI.
5. Build a version test matrix with `uv`, `tox`, or `nox`; interpret Ruff's `UP` suggestions safely.
6. Evaluate performance changes with reproducible measurements rather than release-note headlines.
7. Plan an interpreter upgrade, including native extensions, warnings, security, rollout, and rollback.
8. Distinguish stable features from experimental JIT and free-threaded configurations.

## Prerequisites

You should understand virtual environments, imports, type annotations, `pyproject.toml`, pytest, dependency pinning, basic CI, and the difference between Python source code and compiled native extensions. Lessons 06–09 in this module provide useful background on modern typing, f-strings, and deprecations.

---

## 1. How Python versions and support work

### 1.1 Release lifecycle

Python's feature releases have historically arrived around October, on an approximately yearly cadence. A release is not supported indefinitely. The development guide describes phases: feature development, prerelease, bug-fix maintenance, security-only maintenance, and end of life (EOL). The schedule is governed by release PEPs and can vary in detail across generations. The often-quoted five-year window is the overall lifecycle, not five years of regular bug-fix releases: older branches typically transition from bug-fix to security-only maintenance before EOL, and the current phase durations are documented on the status page.

At the date shown at the top of this lesson, the official status page lists Python 3.14 in bug-fix maintenance, Python 3.13 and 3.12 in security maintenance, and Python 3.10 as EOL. Python 3.11 is in security-only maintenance at this date; always check the live table because release managers and schedules can change. Python 3.10's five-year support window has ended, so it is useful here for migration education, not as a default new production target.

Official references:

- [Status of Python versions](https://devguide.python.org/versions/)
- [Python release cycle and development process](https://devguide.python.org/development/)
- [PEP 602 — Annual release cycle](https://peps.python.org/pep-0602/)
- [Python downloads](https://www.python.org/downloads/)

**Why EOL matters:** an EOL interpreter no longer receives upstream security fixes. New versions of dependencies may stop supporting it; operating-system images and build tooling may drop it; and incident response becomes harder because fixes may require an unmaintained fork or a runtime upgrade. “It still runs” is not evidence that it is safe to keep in production.

### 1.2 Read “What's New” efficiently

For a migration, read the official page for **every version between the current and target runtime**, not only the target version. Then inspect the dedicated porting guide and deprecation/removal sections.

Recommended reading order:

1. Summary/release highlights: identify major syntax and standard-library additions.
2. “Porting to Python X.Y”: look for changed behavior, removals, and API compatibility traps.
3. “Deprecated” and “Removed” sections: search the repository for affected imports and calls.
4. Library docs for APIs that your application actually uses.
5. Relevant PEPs for semantics that are easy to misunderstand.
6. The target interpreter's status and the dependency ecosystem's support statements.

Official release notes:

- [What's New in Python 3.10](https://docs.python.org/3.10/whatsnew/3.10.html)
- [What's New in Python 3.11](https://docs.python.org/3.11/whatsnew/3.11.html)
- [What's New in Python 3.12](https://docs.python.org/3.12/whatsnew/3.12.html)
- [What's New in Python 3.13](https://docs.python.org/3.13/whatsnew/3.13.html)
- [What's New in Python 3.14](https://docs.python.org/3.14/whatsnew/3.14.html)
- [Python 3.14 `asyncio` policy deprecations](https://docs.python.org/3.14/library/asyncio-policy.html)
- [Python 3.14 free-threading status](https://docs.python.org/3.14/howto/free-threading-python.html)

Release notes are an index, not a substitute for API contracts. An implementation-specific optimization in CPython may not be a language guarantee for every Python implementation.

### 1.3 Package support metadata

For this repository's new code, declare Python 3.12 or newer in `pyproject.toml`:

```toml
[project]
name = "example-package"
version = "0.1.0"
requires-python = ">=3.12"

classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Programming Language :: Python :: 3.14",
]
```

The `requires-python` field is the machine-readable compatibility constraint used by packaging tools. Classifiers are descriptive metadata; they do **not** enforce runtime compatibility. Add a version classifier only for a version you actually support and test. Update classifiers as the support policy changes.

A package claiming `requires-python = ">=3.10"` must not unconditionally use Python 3.12-only grammar or imports. It must either avoid those features, use compatible alternatives, or raise the minimum. Metadata, source syntax, imports, dependencies, documentation, and CI must all tell the same story.

### 1.4 Three different compatibility questions

| Compatibility layer | Question | Typical failure | What to verify |
|---|---|---|---|
| **Syntax / parser** | Can this interpreter parse the source file? | `SyntaxError` before code can branch | Parse every shipped module with the oldest claimed interpreter; check grammar features such as PEP 695 and t-strings. |
| **Runtime API** | Does the running interpreter expose the imported name or behavior? | `ImportError`, `AttributeError`, changed semantics | Check standard-library availability and behavioral differences. |
| **Third-party / native dependency** | Does the selected dependency release and wheel support this interpreter, OS, architecture, and ABI? | No compatible wheel, compiler failure, import crash, incorrect behavior | Check dependency metadata, wheel tags, extension compatibility, and real environment installation. |

A runtime `if sys.version_info >= ...` cannot rescue a file containing syntax the old parser cannot understand. Similarly, a parser-compatible module can still fail at import time if it imports a newer standard-library name unconditionally.

---

## 2. Version comparison at a glance

| Release | Released | Main additions relevant to this module | Compatibility / migration notes | Lifecycle note as of 2026-10-17 |
|---|---|---|---|---|
| **3.10** | 2021-10-04 | `match`/`case`, `X | Y` union annotations, parenthesized context managers, `zip(strict=True)`, more precise line information and error suggestions | Syntax and APIs added in 3.11+ are unavailable; `distutils` is deprecated, not yet removed | **EOL**; do not choose for new production systems |
| **3.11** | 2022-10-24 | Specializing interpreter, `ExceptionGroup`/`except*`, `tomllib`, `Self`, `BaseException.add_note()`, `asyncio.TaskGroup` and `asyncio.timeout()` | Removed modules and APIs arrive in later releases; native extensions must be validated | Security-only maintenance |
| **3.12** | 2023-10-02 | PEP 695 type parameter syntax and `type` statement, PEP 701 f-strings, `typing.override`, `itertools.batched`, `sys.monitoring` | `distutils`, `imp`, `asynchat`, and `asyncore` are removed; `datetime.utcnow()` is deprecated | Security-only maintenance |
| **3.13** | 2024-10-07 | Improved REPL, `copy.replace`, `warnings.deprecated`, `TypeIs`, `ReadOnly`, defined `locals()` semantics | Free-threaded CPython and JIT are experimental in 3.13; PEP 594 modules removed | Security-only maintenance |
| **3.14** | 2025-10-07 | Template strings, deferred annotation evaluation, `concurrent.interpreters`, `InterpreterPoolExecutor`, `compression.zstd`, `uuid.uuid7`, debugger-attach improvements, optional experimental tail-call interpreter | Free-threaded build is officially supported but optional; JIT and tail-call interpreter remain experimental; POSIX process-start defaults change; `asyncio` policy APIs deprecated | Bug-fix maintenance |

Dates and lifecycle status come from the official Python release documentation and status page linked above. The list is deliberately selective; consult the release notes for a complete inventory.

---

## 3. Chronological release tour

### 3.1 Python 3.10 — structural pattern matching and stricter iteration

Important additions:

- **Structural pattern matching** (`match` / `case`, PEPs 634–636) supports branching on values and object structure. `match` and `case` are soft keywords, but the statement itself is new grammar and cannot be backported with a runtime conditional.
- **Union type syntax** (`int | str`) is supported natively for annotations. For libraries targeting older Python versions, `typing.Union[int, str]` remains a broad-compatibility option.
- **Parenthesized context managers** allow multiline grouping of `with` items.
- **`zip(strict=True)`** raises `ValueError` when iterables have unequal lengths instead of silently truncating to the shortest.
- **Error and debugging improvements** include better “Did you mean?” suggestions and more reliable line-number information (PEP 626).

```python
# Python 3.10+
match command.split():
    case ["get", key]:
        print("read", key)
    case ["set", key, value]:
        print("write", key, value)
    case _:
        raise ValueError("unsupported command")

for name, score in zip(names, scores, strict=True):
    print(name, score)
```

`zip(strict=True)` detects length mismatch when iteration reaches the point at which the mismatch is observable. If the consumer stops early, it may not observe a later mismatch; consume the iterator fully when equal lengths are a correctness requirement.

**Migration note:** Python 3.10 is EOL as of the fact-check date. It remains relevant for understanding older deployments, but do not treat it as a safe long-term destination.

### 3.2 Python 3.11 — exception groups, structured async, and performance work

Important additions:

- CPython's specializing adaptive interpreter, zero-cost exception handling for common `try` paths, and other changes produced substantial benchmark-suite gains. The official release notes report a **10–60% range across the benchmark suite** and an average 1.25× speedup in their measured suite. These are not a promise that your workload will speed up by the same amount.
- **`ExceptionGroup` and `except*`** let code represent and handle multiple concurrent failures.
- **`tomllib`** parses TOML from the standard library; it does not write TOML.
- **`typing.Self`** represents the current class in return types and related typing positions.
- **`BaseException.add_note()`** attaches contextual notes to an exception traceback.
- **`asyncio.TaskGroup` and `asyncio.timeout()`** provide structured task lifetime and timeout scopes.
- Tracebacks gained finer-grained error locations (PEP 657).

```python
# Python 3.11+
import asyncio
import tomllib
from typing import Self

class Builder:
    def configure(self, **options: object) -> Self:
        self.options = options
        return self

async def fetch_all() -> None:
    async with asyncio.TaskGroup() as group:
        group.create_task(fetch_one())
        group.create_task(fetch_two())

with open("settings.toml", "rb") as file:
    settings = tomllib.load(file)
```

`TaskGroup` cancels sibling tasks when an unhandled task failure occurs and raises grouped failures as appropriate. It is not merely a spelling replacement for `gather()`: review cancellation and error-propagation semantics when migrating.

### 3.3 Python 3.12 — modern generic syntax and f-string grammar

Important additions:

- **PEP 695** introduces type parameter syntax such as `def first[T](items: Sequence[T]) -> T` and the `type` statement for aliases.
- **PEP 701** formalizes f-string grammar, allowing same-quote reuse, multiline expressions, comments, and backslashes in replacement expressions where otherwise valid.
- **`typing.override`** marks methods intended to override a base-class member; it supports static checking and has no runtime override enforcement by itself.
- **`itertools.batched(iterable, n)`** lazily groups items into tuples of up to `n` elements. The `strict` parameter is available starting in 3.13, not 3.12.
- **`sys.monitoring`** (PEP 669) offers low-impact monitoring events for tools such as debuggers and profilers.
- The C API gained per-interpreter-GIL capabilities (PEP 684); this is not the same thing as a general promise that arbitrary Python threads run without the GIL.
- **`distutils` was removed** from the standard library. The `imp`, `asynchat`, and `asyncore` modules were also removed in 3.12.

```python
# Python 3.12+ syntax: older parsers cannot load this module.
def first[T](items: list[T]) -> T:
    return items[0]

type UserId = int

user_id: UserId = 42
label = f"{ {'user': user_id}["user"] = }"
```

The final f-string demonstrates quote reuse enabled by PEP 701; format it for readability in real code. Do not put this snippet in a module that claims compatibility with Python 3.11 or earlier. A runtime `if` does not help because an older parser rejects the source before executing it.

**Migration traps:** code that imports `distutils` or `imp` may fail at import time. `venv` no longer preinstalls `setuptools` by default in 3.12; declare `setuptools` explicitly if your application actually needs it. Do not assume every historical build script still works because `pip install` works for pure-Python packages.

### 3.4 Python 3.13 — improved REPL, new typing/deprecation tools, and experimental execution modes

Important additions:

- The new interactive interpreter improves multiline editing, history, color, and interactive usability.
- **`copy.replace(obj, **changes)`** creates a same-type replacement for supported objects and classes implementing `__replace__()`; it complements rather than replaces `copy.copy()` or `deepcopy()`.
- **`warnings.deprecated()`** (PEP 702) marks APIs as deprecated for static analysis and emits a runtime warning when the decorated API is used, according to the decorator's contract.
- **`typing.TypeIs`** supports type narrowing with semantics distinct from `TypeGuard`; **`typing.ReadOnly`** marks `TypedDict` items as read-only for type checkers.
- `locals()` behavior in optimized scopes is defined by PEP 667. Code that depended on incidental mutation behavior of a returned locals mapping should be reviewed.
- PEP 594 “dead batteries” removals include modules such as `cgi`, `cgitb`, `telnetlib`, `audioop`, `aifc`, `imghdr`, and others. Use the official removal list for the full inventory.
- **Free-threaded CPython** (GIL disabled) is experimental in 3.13 and uses a distinct build, commonly identified with a `t` suffix. Some extensions may not support it; a workload may be slower rather than faster.
- **The JIT is experimental and disabled by default** in 3.13. Do not describe it as a generally enabled production speedup.

```python
# Python 3.13+
from copy import replace
from typing import ReadOnly, TypedDict, TypeIs

class Config(TypedDict):
    name: ReadOnly[str]
    retries: int

def is_text(value: object) -> TypeIs[str]:
    return isinstance(value, str)

# For a supported dataclass / named tuple / custom __replace__ object:
# newer = replace(old_config, retries=5)
```

`copy.replace` only works for supported types or a custom class implementing the protocol; it is not a generic way to update any mutable object. `ReadOnly` is a typing constraint, not a runtime immutable wrapper.

### 3.5 Python 3.14 — template strings, deferred annotations, and multiple interpreters

Important additions:

- **Template string literals** (`t"...{expr}..."`, PEP 750) produce a `Template` object made from literal segments and interpolation objects rather than immediately formatting to a plain string. This is an extension point for safe templating; it is not a drop-in replacement for f-strings and should not be assumed to sanitize values automatically.
- **Deferred annotation evaluation** (PEPs 649 and 749) changes when annotations are evaluated and adds `annotationlib` support for introspection. Frameworks that inspect `__annotations__` directly should be tested; use the documented annotation introspection APIs for the desired format instead of relying on incidental internal representation.
- **Free-threaded build support is officially supported but optional** (PEP 779). “Supported build” does not mean every dependency or extension is free-threading-safe, nor does it mean free-threading is the default interpreter.
- **`concurrent.interpreters`** exposes multiple interpreters in the standard library (PEP 734). `concurrent.futures.InterpreterPoolExecutor` offers a pool of isolated interpreters for parallel execution. Review object-sharing and extension compatibility; interpreter isolation is not equivalent to ordinary threads sharing arbitrary objects.
- **`compression.zstd`** adds standard-library Zstandard compression support (PEP 784).
- **`uuid.uuid7()`** adds time-ordered UUIDv7 generation. UUIDv7 is useful for sortable identifiers, but its time component has privacy and ordering implications; it is not a substitute for authorization or a secret token.
- **External debugger attachment** improvements (PEP 768) provide a controlled way for a debugger to attach to a running process when enabled and permitted. Treat this as an operational/security feature and restrict access appropriately.
- The **JIT remains experimental** in 3.14. Official macOS and Windows release binaries include an experimental JIT that can be enabled for testing, but the release notes do not recommend it for production use; measured impact can range from slower to faster depending on workload. JIT and free-threaded builds are not a combined mode in this release line.
- CPython 3.14 has an optional **experimental tail-call interpreter** selected at build time with `--with-tail-call-interp` on supported compiler/build configurations. It is a different interpreter implementation, not the JIT, not a language feature, and not a portable runtime switch. Do not assume a distribution build enables it.
- On Unix platforms other than macOS, the default multiprocessing start method changed from `fork` to `forkserver`; Windows and macOS continue to default to `spawn`. Make process creation explicit where behavior matters and test startup, imports, pickling, and child initialization.
- The `asyncio` event-loop policy system and `asyncio.iscoroutinefunction()` are deprecated in 3.14 and scheduled for removal in 3.16. `asyncio.get_event_loop()` on the default policy also raises `RuntimeError` when no event loop is set. Prefer `asyncio.run()` or `asyncio.Runner(loop_factory=...)` and `inspect.iscoroutinefunction()` as appropriate.

```python
# Python 3.14+
import uuid
import compression.zstd
from concurrent.futures import InterpreterPoolExecutor

request_id = uuid.uuid7()

with InterpreterPoolExecutor() as pool:
    results = list(pool.map(expensive_pure_function, input_items))
```

The example is illustrative: `expensive_pure_function` and `input_items` must be defined, and callables/arguments/results must satisfy the executor's serialization and interpreter constraints. Measure whether interpreter isolation helps the actual workload.

---

## 4. Feature-to-minimum-version reference

“Minimum” below means the first CPython release that provides the named syntax or standard-library API. Typing backports may make selected annotations available earlier, but they do not backport grammar or interpreter semantics.

| Feature | Minimum version | Compatibility note |
|---|---:|---|
| `match` / `case` statement | 3.10 | New grammar; no runtime shim for older parsers |
| Native `X | Y` union evaluation | 3.10 | `typing.Union` is broadly compatible; postponed annotations can help in some contexts but do not change parser grammar generally |
| `zip(strict=True)` | 3.10 | Strict mismatch raises `ValueError` when reached during iteration |
| `ExceptionGroup`, `except*` | 3.11 | `exceptiongroup` backport can help older runtimes, but `except*` syntax cannot be backported |
| `tomllib` | 3.11 | Use `tomli` for Python 3.10 and earlier; both parse TOML, not write it |
| `typing.Self` | 3.11 | `typing_extensions.Self` for older runtimes |
| `BaseException.add_note()` | 3.11 | Guard or omit on older runtimes; no exact stdlib-equivalent traceback note API |
| `asyncio.TaskGroup`, `asyncio.timeout` | 3.11 | Review structured-concurrency semantics before substituting older patterns |
| PEP 695 generic syntax / `type Alias = ...` | 3.12 | Grammar feature; older Python cannot parse it |
| PEP 701 f-string grammar relaxations | 3.12 | Avoid new grammar in modules targeting earlier parsers |
| `typing.override` | 3.12 | `typing_extensions.override` for older versions |
| `itertools.batched` | 3.12 | `strict=` option was added in 3.13 |
| `sys.monitoring` | 3.12 | Monitoring API availability and event semantics are version-specific |
| `copy.replace` | 3.13 | Supports built-in types and classes implementing `__replace__` |
| `warnings.deprecated` | 3.13 | `typing_extensions.deprecated` is a practical backport for supported older versions |
| `typing.TypeIs` | 3.13 | `typing_extensions.TypeIs` for older versions |
| `typing.ReadOnly` | 3.13 | `typing_extensions.ReadOnly` for older versions |
| Defined `locals()` semantics (PEP 667) | 3.13 | Revisit code mutating or retaining locals mappings |
| `t"..."` template string syntax | 3.14 | New grammar; produces template/interpolation objects, not a formatted `str` |
| Deferred annotation evaluation / `annotationlib` | 3.14 | Introspection frameworks need cross-version tests |
| `concurrent.interpreters` | 3.14 | Check C-extension support and isolation requirements |
| `InterpreterPoolExecutor` | 3.14 | Multiple isolated interpreters; benchmark and test serialization constraints |
| `compression.zstd` | 3.14 | Standard-library Zstandard API |
| `uuid.uuid7()` | 3.14 | Time-ordered UUIDs; do not assume they are secrets |
| POSIX non-macOS `forkserver` multiprocessing default | 3.14 | Explicitly configure and test start method if required |
| Optional experimental tail-call interpreter build option | 3.14 | Build-time option (`--with-tail-call-interp`), not a runtime feature guarantee; validate compiler/build support and benchmark separately |
| `asyncio` event-loop policy APIs and `asyncio.iscoroutinefunction()` deprecated | 3.14 | Scheduled for removal in 3.16; prefer runner APIs and `inspect.iscoroutinefunction()` |
| Default-policy `asyncio.get_event_loop()` raises when no loop is set | 3.14 | Use `asyncio.get_running_loop()` inside async code and `asyncio.run()` / `Runner` at application boundaries |

### 4.1 Backports and compatibility shims

Use a backport when it solves a real compatibility requirement, not merely because it is available.

```python
# TOML parsing: Python 3.11+ uses tomllib; Python 3.10 uses tomli.
import sys
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # dependency required on Python 3.10
```

Declare the conditional dependency in metadata rather than relying on a developer's machine:

```toml
[project]
requires-python = ">=3.10"
dependencies = [
  "tomli>=2; python_version < '3.11'",
  "exceptiongroup>=1; python_version < '3.11'",
]
```

Only include `exceptiongroup` if your code actually uses its backport API on Python 3.10. Its existence does **not** make `except*` syntax legal on Python 3.10. If the project follows this repository's Python 3.12+ policy, do not add these compatibility branches without a concrete need.

For typing features, `typing_extensions` commonly backports `Self`, `override`, `deprecated`, `TypeIs`, and `ReadOnly`. Pin a version that actually provides the names you import and test the lowest supported dependency version. Do not assume “typing extensions installed” means every newest typing feature is present.

`from __future__ import annotations` postpones annotation evaluation according to the future-import semantics available in that interpreter. It can help with forward references, but **does not backport new syntax** such as `def f[T](...)`, the `type` statement, or template-string literals. It also does not make a missing runtime API such as `itertools.batched` exist. Be careful with frameworks that evaluate annotations at runtime; Python 3.14 changes annotation behavior and introspection APIs.

### 4.2 Prefer capability detection when it expresses the requirement

Use version checks when the compatibility rule is genuinely tied to interpreter version. Use feature detection when availability can vary by implementation, vendor build, or backport.

```python
import itertools

if hasattr(itertools, "batched"):
    batched = itertools.batched
else:
    # A minimal fallback for Python < 3.12.
    from itertools import islice

    def batched(iterable, n):
        if n < 1:
            raise ValueError("n must be at least one")
        iterator = iter(iterable)

        def generate():
            while batch := tuple(islice(iterator, n)):
                yield batch

        return generate()
```

This fallback matches the basic lazy batching behavior and validates `n` immediately, like the standard-library API, but it intentionally does not implement Python 3.13's `strict=True` option. Document and test that limitation rather than pretending the shim is fully identical.

```python
import sys

if sys.version_info >= (3, 14):
    # Use a 3.14-only API in this branch, provided this file's syntax
    # remains parseable by the declared minimum interpreter.
    ...
```

For interpreter-specific behavior such as multiprocessing start methods, prefer an explicit application setting over depending on a default that changed between releases. Do not scatter version checks throughout business logic; centralize compatibility code in a small module and remove it when old versions leave support.

---

## 5. Multiple interpreters and version matrices

### 5.1 Install interpreters with `uv`

`uv` can install and select Python interpreters independently of the system interpreter. Commands vary slightly with uv versions; consult [uv's Python documentation](https://docs.astral.sh/uv/guides/install-python/).

```bash
uv python install 3.10 3.11 3.12 3.13 3.14
uv python list
uv run --python 3.12 python --version
uv run --python 3.14 python --version
```

The installation command is an instruction, not evidence that all versions are installed on every host. Availability depends on platform, architecture, build, and network access. For a reproducible team setup, pin the toolchain version and record exact interpreter patch releases in CI or a lock/toolchain file where supported.

### 5.2 Choose a matrix that matches the policy

If the package claims `>=3.12`, the minimum supported version must be tested. A practical matrix is:

- **Minimum**: 3.12, to detect accidental use of newer syntax/APIs.
- **Current production**: the interpreter used in production.
- **Newest supported**: 3.14, to detect future compatibility issues early.
- **Optional experimental jobs**: free-threaded 3.14t or JIT-enabled builds, isolated from release-blocking stable jobs until support is intentional.

A full 3.10–3.14 matrix is appropriate for a library that explicitly supports all those versions. It is not automatically necessary for a service that has deliberately dropped 3.10 and 3.11. Do not declare 3.10 support solely because a matrix still contains a stale job.

#### Example `tox.ini` for a package supporting Python 3.12–3.14

```ini
[tox]
env_list = py312, py313, py314
skip_missing_interpreters = false

[testenv]
description = run tests with warnings treated as errors
package = wheel
deps =
    pytest
commands = python -W error -m pytest {posargs}
```

The `py314` environment requires a usable Python 3.14 interpreter on the runner. `skip_missing_interpreters = false` makes a missing interpreter fail rather than silently reducing coverage.

#### Example `noxfile.py`

```python
import nox

@nox.session(python=["3.12", "3.13", "3.14"])
def tests(session):
    session.install("pytest", ".")
    session.run("python", "-W", "error", "-m", "pytest", *session.posargs)
```

Nox and tox are alternatives; a project generally does not need both. In CI, make the selected Python versions explicit and verify the matrix actually ran.

#### Example GitHub Actions matrix

```yaml
name: tests
on: [push, pull_request]
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.12", "3.13", "3.14"]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: python -m pip install --upgrade pip
      - run: python -m pip install -e . pytest
      - run: python -W error -m pytest
```

For real production CI, pin or review third-party action versions according to your supply-chain policy, use a lock file or controlled dependency resolver, and add OS/architecture jobs if you ship native extensions. This YAML is a minimal illustration, not a complete hardened CI workflow.

### 5.3 Warnings in CI

A useful policy is to fail on warnings emitted by your own package while treating dependency warnings deliberately. `-W error` is strong but can expose warnings from dependencies or test plugins. Do not globally suppress them just to make CI green.

```bash
python -W error -m pytest
```

When a third-party dependency emits a warning, identify the source, determine whether it signals a real upcoming break, upgrade or report the dependency, and use a narrowly scoped temporary filter only if necessary. Track an owner and removal date for any exception. See Lesson 09 for warning categories, filters, `pytest.warns`, and deprecation policy.

### 5.4 Ruff `UP` modernization

Ruff's `UP` rules are derived from pyupgrade-style modernization checks. They can suggest newer syntax and APIs based on a configured target version.

```toml
[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "UP"]
```

```bash
ruff check --select UP src tests
ruff check --select UP --fix src tests
```

Review every automated edit. Set the target version to the project's **actual minimum**, not the newest interpreter on your laptop. A modernization can be valid for Python 3.12+ but silently violate a package's advertised 3.10 support. Linters cannot prove runtime behavior, dependency availability, or type-checker correctness.

---

## 6. Deprecations, removals, and changed behavior to audit

Search release notes for “deprecated”, “removed”, “changed”, “default”, and “porting”. Review at least the following examples when moving across 3.10–3.14.

| Change | Version context | Migration action |
|---|---|---|
| `distutils` deprecated | 3.10 | Replace build/runtime use with maintained packaging/build tooling; do not start new dependencies on it |
| `distutils`, `imp`, `asynchat`, `asyncore` removed | 3.12 | Replace imports and behavior; check transitive build tooling too |
| `datetime.datetime.utcnow()` deprecated | 3.12 | Prefer `datetime.datetime.now(datetime.UTC)` (or `timezone.utc` where appropriate); be explicit about naive vs aware values |
| PEP 594 “dead batteries” removals, including `cgi` and `telnetlib` | 3.13 | Use a maintained third-party library or supported standard-library alternative; review security implications |
| `locals()` semantics in optimized scopes | 3.13 | Do not rely on mutating a mapping returned by `locals()` to modify local variables; use explicit data structures |
| `tarfile` extraction filters | Introduced earlier, default changed in 3.14 | Audit extraction code, path handling, symlinks, and trusted/untrusted archives; use an explicit policy and test it |
| Multiprocessing default on POSIX non-macOS | 3.14 | Do not rely on implicit `fork`; set an explicit start method when required and test process initialization |
| Deferred annotation evaluation | 3.14 | Test decorators, serializers, dependency-injection frameworks, ORMs, and tools reading `__annotations__` |
| JIT/free-threaded/tail-call interpreter configurations | 3.13 free-threaded and JIT experimental; 3.14 free-threaded officially supported as optional build, JIT and tail-call interpreter experimental | Test as distinct runtime/build targets; don't infer extension support from the base version alone |
| `asyncio` policy system and `asyncio.iscoroutinefunction()` deprecations | 3.14; scheduled for removal in 3.16 | Prefer `asyncio.run()` / `asyncio.Runner(loop_factory=...)` and `inspect.iscoroutinefunction()` |

### 6.1 `datetime.utcnow()` and timezone correctness

`datetime.utcnow()` returns a naive datetime and is deprecated starting in 3.12. Prefer an aware UTC datetime:

```python
from datetime import UTC, datetime

created_at = datetime.now(UTC)
```

`datetime.UTC` is available from Python 3.11. For code that must run on 3.10, use `timezone.utc`:

```python
from datetime import datetime, timezone

created_at = datetime.now(timezone.utc)
```

Do not mechanically replace `utcnow()` without reviewing callers that assume a naive value. Correctness requires agreeing on whether persisted timestamps are aware, naive UTC, or local time.

### 6.2 `tarfile` extraction security

Extraction filters were introduced in Python 3.12, and Python 3.14 changed the default extraction filter to the safer `data` policy. Do not assume the same default across the whole version range. For untrusted archives, select and test an explicit safe extraction policy supported by the minimum runtime; on 3.10/3.11, use a carefully reviewed compatibility strategy rather than assuming the API exists. Also account for paths, links, permissions, and post-extraction behavior. A filter is defense in depth, not a substitute for validating archive provenance and application-level expectations.

### 6.3 Multiprocessing defaults

In Python 3.14, `forkserver` becomes the default start method on supported Unix platforms other than macOS; Windows and macOS continue to default to `spawn`. Code that relied on inherited open sockets, globals, monkeypatches, or initialized libraries from `fork` can fail. Test under the intended method and use the `if __name__ == "__main__":` guard where required.

```python
import multiprocessing as mp

def worker(item: int) -> int:
    return item * 2

if __name__ == "__main__":
    context = mp.get_context("spawn")  # choose deliberately, not accidentally
    with context.Pool() as pool:
        print(pool.map(worker, [1, 2, 3]))
```

Select `spawn` here as an explicit example, not a universal recommendation. Choose the start method that matches the platform and safety requirements; test it under production-like conditions.

### 6.4 `asyncio` policy deprecations in 3.14

Python 3.14 deprecates the event-loop policy system and `asyncio.iscoroutinefunction()`; the policy classes/functions and `asyncio.iscoroutinefunction()` are scheduled for removal in Python 3.16. Also, `asyncio.get_event_loop()` using the default policy now raises `RuntimeError` if no loop is set, instead of implicitly creating one in that situation. Prefer the top-level runner APIs and `inspect`'s coroutine predicate:

```python
import asyncio
import inspect

async def main() -> None:
    ...

asyncio.run(main())

# If a specific event-loop implementation is required and supports this API:
# asyncio.run(main(), loop_factory=MyEventLoop)

is_async_callable = inspect.iscoroutinefunction(main)
```

Do not mechanically replace every `get_event_loop()` call without checking context: inside running coroutines, use `asyncio.get_running_loop()`; for application entry points, prefer `asyncio.run()` or `asyncio.Runner`. Official reference: [asyncio policies](https://docs.python.org/3.14/library/asyncio-policy.html).

---

## 7. Performance across interpreter versions

### 7.1 What not to conclude

Do not translate a release-note benchmark into a service-level SLA. Performance depends on workload shape, dependency versions, CPU, operating system, compiler, warm-up, I/O, allocation patterns, concurrency, and whether the process is cold or steady-state. A version can improve CPU-heavy loops and still regress an I/O-heavy service due to unrelated dependency or configuration changes.

### 7.2 Benchmark methodology for 3.10, 3.12, and 3.14

Use the same application commit, input data, dependency lock strategy, hardware, environment variables, and command line. If a dependency cannot be held at the same version across all interpreters, record the change as a confounder. Do not compare a 3.10 app with old dependencies against a 3.14 app with a new dependency stack and attribute all differences to CPython.

1. Define the decision: latency, throughput, CPU, memory, startup time, or cost per request.
2. Choose representative production-shaped inputs, including small and large cases.
3. Run a correctness suite first on every interpreter.
4. Warm up and run multiple measured repetitions; record median and spread, not just the best run.
5. Separate cold-start and steady-state measurements.
6. Capture CPU and memory profiles to explain changes.
7. Run the same benchmark with the same command and environment; store raw outputs.
8. Report hardware, OS, exact Python patch version, build flags, dependency versions, and workload commit.
9. Repeat enough times to understand noise; don't claim a difference smaller than observed variation.
10. Publish actual measurements only after executing them. This lesson intentionally contains **no fabricated benchmark numbers**.

A minimal repeatable timing harness might be:

```python
from statistics import median
from time import perf_counter


def measure(fn, repeats: int = 7) -> dict[str, float]:
    samples = []
    fn()  # warm-up; adapt if the workload is stateful
    for _ in range(repeats):
        started = perf_counter()
        fn()
        samples.append(perf_counter() - started)
    return {
        "median_seconds": median(samples),
        "min_seconds": min(samples),
        "max_seconds": max(samples),
    }
```

Use this only for a controlled in-process benchmark. For a service, measure request-level latency and throughput using a load test that reflects concurrency, I/O, connection reuse, and deployment topology. Ensure each iteration does equivalent work and does not accidentally reuse cached state on only one version.

### 7.3 JIT and free-threaded Python

Treat each as a distinct build/runtime axis, not a simple version toggle.

- **Python 3.13 free-threaded:** experimental; extensions may require special builds, and single-thread performance can regress.
- **Python 3.14 free-threaded:** officially supported as an optional build, but adoption remains ecosystem-dependent. Confirm every critical extension's support and audit shared-state assumptions.
- **JIT:** experimental in both releases described here. In 3.14, official macOS and Windows binaries include a JIT that can be enabled for testing, but it is not recommended for production use in the release notes. Free-threaded builds do not support the JIT in this release line.

Thread-safety review should cover mutable global state, caches, lazy initialization, C-extension assumptions, reference ownership, callbacks, and test isolation. The GIL never made arbitrary application-level compound operations a robust synchronization contract. Use explicit locks, queues, immutable messages, and documented concurrency boundaries.

---

## 8. Wheels, ABI, native extensions, and dependencies

A pure-Python wheel may work across several Python versions if its syntax and runtime API requirements permit it. A compiled extension adds platform, architecture, Python ABI, C runtime, and build-tool constraints.

- Inspect wheel tags and package metadata before assuming a binary exists.
- `abi3` wheels use CPython's limited API and may support several CPython versions when the extension and packaging are correctly built for it; `abi3` does not mean cross-platform or universal compatibility.
- A wheel tagged for a free-threaded ABI (for example, a `cp313t` build) is distinct from a conventional GIL-enabled CPython wheel. Do not assume one can be substituted for the other.
- If no compatible wheel exists, pip may attempt a source build. That build needs a compiler, headers, system libraries, and compatible build dependencies; production images may intentionally lack these.
- Test import and representative operations, not only installation. ABI compatibility does not guarantee semantic or thread-safety compatibility.
- Check transitive dependencies: a top-level package can declare support while one of its dependencies does not.

Useful checks:

```bash
python -m pip debug --verbose
python -m pip index versions SOME_PACKAGE
python -m pip install --only-binary=:all: SOME_PACKAGE
```

`pip index` availability depends on pip version and index configuration. `--only-binary=:all:` is a diagnostic for wheel availability, not a universal install policy. For private indexes, authenticate and check the intended repository. Review [Python packaging specifications](https://packaging.python.org/en/latest/specifications/) and the dependency's own support matrix.

### 8.1 Dependency and supply-chain review

For each dependency during an upgrade, record: supported Python versions, release activity, known vulnerabilities, native wheels, transitive dependency changes, license constraints, and maintainer/security policy. Use a lockfile or constrained resolver for reproducibility; update dependencies deliberately rather than taking an unconstrained latest set at the same time as the interpreter upgrade. Validate artifact provenance and hashes where the workflow supports them, keep build isolation in mind, and monitor advisories.

---

## 9. Docker images and reproducibility

Choose an image by compatibility, security updates, operational footprint, native-library needs, and reproducibility—not by size alone.

- A tag such as `python:3.12-slim` is readable but mutable: a future pull may resolve to a different image digest.
- Pinning an image digest makes a build more reproducible, but it also freezes the image until an intentional update. Automate update review so pinning does not become a security trap.
- Keep build and runtime dependencies separate when practical; compile native dependencies in a controlled build stage and copy only runtime artifacts into the final image.
- Rebuild regularly for OS and Python security updates, scan the image, and record the base digest and build metadata.
- Ensure the interpreter in the image matches the version used in CI and staging. Test the built image itself, not just a developer virtual environment.

Example only (replace the tag/digest with the project's approved image and pinning policy):

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir .
USER 10001
CMD ["python", "-m", "your_package"]
```

For reproducibility, use a digest-pinned base image in release builds and a documented process to refresh it. Do not paste an arbitrary digest into a long-lived Dockerfile without an update mechanism.

---

## 10. Production upgrade playbook

Treat an interpreter upgrade as a compatibility and operational change, not just a package reinstall.

### Phase 1 — Inventory and baseline

- [ ] Record the current interpreter, patch release, OS image digest, architecture, libc, build flags, and package manager.
- [ ] Inventory direct/transitive dependencies, native extensions, wheels, plugins, build backends, and runtime tools.
- [ ] Capture current tests, coverage, warning output, startup time, memory, latency, throughput, and error rates.
- [ ] Search source and build scripts for deprecated/removed modules and APIs.
- [ ] Identify annotation introspection, `tarfile`, multiprocessing, serialization, and C-extension-sensitive paths.
- [ ] Agree on a target version and minimum version; document why the policy is supportable.

### Phase 2 — Expand CI before production

- [ ] Add the target interpreter to CI while retaining the current production version.
- [ ] Test minimum and newest supported versions; add OS/architecture jobs for native extensions.
- [ ] Run install/build tests from a clean environment, including wheel installation if you publish wheels.
- [ ] Run tests with warnings visible, then eliminate owned deprecations and make selected warnings fatal.
- [ ] Upgrade incompatible dependencies in controlled groups and lock the resolved result.
- [ ] Run static typing, linting, security scanning, and package build validation.

### Phase 3 — Correct behavior and measure

- [ ] Replace removed APIs and verify semantics, not just imports.
- [ ] Review `datetime` awareness, annotation introspection, process-start behavior, archive extraction, and async cancellation.
- [ ] Test cancellation, shutdown, signals, child process startup, and failure handling.
- [ ] Benchmark the same workload on the old and new runtimes using the methodology above.
- [ ] Run integration, contract, migration, load, and resilience tests against realistic dependencies.
- [ ] Build and scan the actual deployment image; test startup and health checks inside it.

### Phase 4 — Staging, canary, and rollout

- [ ] Deploy to staging with production-like configuration and representative data.
- [ ] Validate observability, tracing, profilers, debugger policy, metrics, logs, and alerting.
- [ ] Canary a small percentage of traffic or a single worker; compare error rate, p95/p99 latency, CPU, memory, queue depth, and restart rate.
- [ ] Define objective stop/rollback thresholds before the canary begins.
- [ ] Expand gradually only after the agreed observation window and acceptance criteria pass.
- [ ] Retain a known-good image and dependency lock for rollback.

### Phase 5 — Policy and cleanup

- [ ] Change `requires-python`, classifiers, deployment manifests, base image, and documentation together.
- [ ] Remove obsolete compatibility shims only after the oldest supported version no longer needs them.
- [ ] Record findings, benchmark methodology/results, known limitations, and follow-up work.
- [ ] Update the support calendar and dependency vulnerability monitoring.

### Rollback checklist

- [ ] Keep the old image digest and lockfile available and deployable.
- [ ] Define rollback triggers (e.g. sustained error-rate increase, latency SLO breach, memory growth, worker crashes, failed jobs, or data-integrity issues).
- [ ] Verify rollback works before rollout; do not assume the previous image can consume data written by the new version.
- [ ] Make database/schema and serialized-data changes backward-compatible or separately reversible.
- [ ] Preserve request IDs, logs, metrics, traces, and crash reports for diagnosis.
- [ ] Assign an incident owner and communication channel.

---

## 11. Version-support policy: choose deliberately

A policy such as “support the last N Python versions” is easy to state but can be misleading unless the team defines what “support” means. Specify whether support means tests passing, security fixes, wheels published, best-effort issue triage, or production SLO coverage.

For a library, a policy can follow the scientific Python SPEC 0 approach or another published policy, but verify the policy's current dates and scope before adopting it. The current SPEC 0 recommendation is to drop Python support three years after a feature release and core-package dependency support two years after that dependency's feature release. This is a recommendation for the Scientific Python ecosystem, not a universal requirement; it also does not replace the interpreter vendor's security lifecycle. [SPEC 0](https://scientific-python.org/specs/spec-0000/) is a reference point, not a universal requirement for every organization.

A defensible policy balances:

- customer/deployment demand and upgrade cadence;
- upstream interpreter support and security fixes;
- dependency and native-wheel availability;
- cost of CI matrix and bug triage;
- syntax/API opportunities that materially improve maintainability;
- enterprise or platform constraints and formal compliance requirements.

For this repository, **Python 3.12+ is the baseline for new code**. Supporting 3.10 or 3.11 should be an explicit exception with a named owner, a reason, a sunset date, and CI evidence—not an accidental side effect of old metadata.

---

## 12. Internal Python upgrade RFC template

Use this structure for a production change request.

```markdown
# RFC: Upgrade service-name from Python X.Y to A.B

## Decision requested
- Target interpreter and patch policy:
- Target date / owner:
- Scope and excluded components:

## Current state
- Runtime, image digest, OS, architecture:
- Dependency lock and native extensions:
- Baseline SLOs, incidents, warnings, benchmarks:

## Compatibility findings
- Removed/deprecated APIs:
- Dependency/wheel/ABI findings:
- Annotation, multiprocessing, tarfile, and async risks:
- Test matrix and gaps:

## Rollout
- Staging and canary cohorts:
- Metrics and acceptance thresholds:
- Observation window:
- Rollback triggers and verified procedure:

## Security and operations
- EOL/security timeline:
- Image and artifact provenance:
- Observability / debugger access:

## Acceptance criteria
- Correctness tests pass on minimum and target versions:
- No unapproved warnings:
- Performance within agreed bounds:
- Dependency and image scans pass:
- Rollback tested:

## Decision / sign-off
- Approvers:
- Known risks accepted:
- Follow-up actions and dates:
```

---

## 13. Hands-on exercises

### Exercise 1 — Feature timeline

A package claims `requires-python = ">=3.10"` but uses `def parse[T](value: T) -> T`, imports `tomllib`, and calls `itertools.batched(..., strict=True)`. Identify each incompatibility and propose a support-policy correction.

**Hint:** check syntax separately from imports and keyword arguments.

**Solution:** PEP 695 generic syntax requires Python 3.12 and is rejected by older parsers; `tomllib` requires 3.11; `itertools.batched` starts in 3.12 and its `strict` option starts in 3.13. Either raise `requires-python` to `>=3.13` (if no other requirements differ) and test 3.13+ or rewrite the syntax and provide carefully tested runtime compatibility for lower versions. Metadata and CI must be updated at the same time.

### Exercise 2 — Make a minimal compatibility shim

Write a module that imports `tomllib` on 3.11+ and `tomli` on 3.10. Declare the conditional dependency. Explain why `from __future__ import annotations` does not solve the missing import.

**Hint:** see section 4.1.

**Solution:** use the conditional import example and dependency marker in section 4.1. Future annotations affects annotation evaluation; it does not install a module or change standard-library contents.

### Exercise 3 — Choose a matrix

Your service deploys only on 3.13 today, but policy requires 3.12+ and you want to prepare for 3.14. Design a CI matrix and explain why a 3.10 job is optional rather than required.

**Solution:** run 3.12 (minimum), 3.13 (production), and 3.14 (newest target) with warnings visible and tests installed from clean builds. Add OS/architecture and native-wheel jobs as needed. Do not add 3.10 unless it is intentionally supported or needed for a specific migration test.

### Exercise 4 — Interpret a benchmark

A local microbenchmark is 8% faster on 3.14 but p95 latency in staging is 3% worse. List at least five hypotheses and a next experiment.

**Hint:** CPU-only microbenchmarks do not capture service I/O, dependencies, cold starts, or concurrency.

**Solution:** possible causes include dependency changes, different image or CPU throttling, allocation/GC changes, connection-pool behavior, workload mix, concurrency/queueing, cold-start regressions, measurement noise, and different process-start behavior. Repeat on identical hardware and dependency lock; capture profiles and request-level traces; compare p50/p95/p99, CPU, memory, and throughput under equivalent load before deciding.

### Exercise 5 — Upgrade RFC

Draft a one-page plan to move a service from 3.10 to 3.13 when it has a C-extension dependency and parses user-provided tar archives. Include a dependency/wheel plan, test matrix, security review, canary thresholds, and rollback.

**Solution outline:** inventory extension and wheel tags; verify source-build toolchain; test 3.10 baseline and 3.13 target in CI; expand matrix to target before production; remove APIs absent in 3.13 and inspect PEP 594 removals; explicitly select safe tar extraction policy and test traversal/link attacks; run warning-as-error tests; benchmark representative traffic; deploy target image to staging and canary; define error-rate/latency/memory thresholds; keep old image and compatible data formats for rollback. Since 3.10 is EOL as of the lesson's fact-check date, make the migration a security priority and avoid extending its support window without a documented exception.

---

## 14. Case study: modernize a data-ingestion service

### Current state

A service ingests CSV and TOML configuration, decompresses uploaded archives, starts worker processes, and uses a native parsing extension. It runs Python 3.10, has no explicit Python classifiers, pins dependencies loosely, and reports that “tests pass locally.” The team wants Python 3.14 because it expects free performance gains.

### Correct decision framing

The team should not begin by changing the Docker tag. Python 3.10 is EOL; the immediate goal is a supported, secure runtime with known compatibility, not a presumed speedup. Python 3.14 is a reasonable target candidate, but native-wheel availability, changed multiprocessing defaults, annotation introspection, archive handling, and dependency support must be verified first.

### Plan

1. **Inventory:** capture the current image digest, Python patch release, dependency tree, native extension version, compiler/runtime libraries, archive extraction code, and multiprocessing behavior.
2. **Baseline:** preserve the current lockfile and capture correctness results, throughput, latency, CPU, memory, startup time, and failure rates.
3. **Compatibility branch:** add Python 3.12, 3.13, and 3.14 CI jobs; if the native extension lacks a 3.14 wheel, coordinate a supported wheel or build pipeline rather than silently relying on a production compiler.
4. **API audit:** remove `distutils`/`imp` usage if present; replace `utcnow()` where used; test annotation-reading frameworks on 3.14; explicitly review `tarfile` extraction policy; make multiprocessing start method intentional.
5. **Dependency upgrade:** upgrade the native extension and other packages in controlled steps; lock exact compatible versions and run vulnerability checks.
6. **Correctness:** run unit, integration, contract, malformed-archive, cancellation, child-process, and end-to-end tests on the target image. Use warnings-as-errors for owned code and triage dependency warnings.
7. **Performance:** run the same benchmark workload on 3.10, 3.12, and 3.14 where interpreters and dependencies can be installed. Record exact patch versions, hardware, OS, build flags, dependencies, warm-up, repetitions, median/spread, CPU, and memory. If the same dependency set cannot support all versions, disclose that confounder. Do not invent numbers or assume the 3.11 release-note gains apply to this service.
8. **Canary:** deploy a small target cohort. Compare error rate, p95/p99, throughput, CPU, memory, queue depth, restarts, and archive-processing failures against the baseline. Roll back if pre-agreed thresholds fail.
9. **Policy update:** after success, set `requires-python`, classifiers, Docker image digest policy, and CI to match the actual supported versions. Publish the upgrade RFC and a deprecation/retirement date for the old image.

### Acceptance criteria

- The native extension installs and runs on all supported production targets; ABI and wheel support are evidenced, not assumed.
- User-provided archive tests demonstrate the intended extraction security policy.
- All correctness, integration, and operational smoke tests pass on the target image.
- No unexplained warnings remain; dependency warnings have owners and disposition.
- Performance is within an agreed tolerance based on measurements, not release-note claims.
- Canary and rollback have been rehearsed, and the previous image remains deployable.
- Package metadata, docs, dependency lock, CI matrix, and production runtime agree.

---

## 15. Final checklists and common mistakes

### Before merging code that uses a new feature

- [ ] Does the declared minimum interpreter parse this file?
- [ ] Does every imported API exist on the minimum interpreter?
- [ ] Does a dependency or typing backport need a conditional marker?
- [ ] Do type checking, lint target version, docs, classifiers, and CI agree?
- [ ] Are behavioral changes tested rather than inferred from version numbers?

### Before upgrading production

- [ ] Is the target interpreter supported upstream?
- [ ] Are dependencies, native extensions, wheels, and ABI validated?
- [ ] Are deprecations/removals and defaults reviewed across every skipped release?
- [ ] Have tests and benchmarks run on actual target interpreters?
- [ ] Are Docker digest, dependency lock, security scans, and provenance controlled?
- [ ] Are canary acceptance thresholds and rollback tested?

### Common mistakes

- **Pinning EOL Python because it works.** Operational compatibility does not restore upstream security support.
- **Using new syntax under an old `requires-python`.** Runtime branches cannot fix parser failures.
- **Checking only the target release notes.** Intermediate releases can remove APIs or change defaults.
- **Confusing a backport with a language feature.** A package can supply a typing name or exception class, but not make a new grammar valid on an old parser.
- **Trusting classifiers as enforcement.** `requires-python`, actual code, and CI must agree.
- **Assuming a wheel exists.** Native builds depend on platform, architecture, ABI, compiler, and library availability.
- **Turning on free-threading or JIT in production because it is newer.** Validate the entire ecosystem and benchmark under representative load.
- **Upgrading Python and all dependencies simultaneously.** This destroys the ability to attribute regressions.
- **Accepting Ruff `UP` edits blindly.** Ensure the target version is the actual minimum and review semantic changes.
- **Claiming performance gains without measurement.** Publish the workload, method, versions, and actual results.

## References

Primary sources for the version facts in this lesson:

1. [Python version status](https://devguide.python.org/versions/)
2. [What's New in Python 3.10](https://docs.python.org/3.10/whatsnew/3.10.html)
3. [What's New in Python 3.11](https://docs.python.org/3.11/whatsnew/3.11.html)
4. [What's New in Python 3.12](https://docs.python.org/3.12/whatsnew/3.12.html)
5. [What's New in Python 3.13](https://docs.python.org/3.13/whatsnew/3.13.html)
6. [What's New in Python 3.14](https://docs.python.org/3.14/whatsnew/3.14.html)
7. [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/)
8. [PEP 701 — Syntactic formalization of f-strings](https://peps.python.org/pep-0701/)
9. [PEP 702 — Marking deprecations using the type system](https://peps.python.org/pep-0702/)
10. [PEP 703 — Making the Global Interpreter Lock optional](https://peps.python.org/pep-0703/)
11. [PEP 734 — Multiple interpreters in the stdlib](https://peps.python.org/pep-0734/)
12. [PEP 749 — Implementing deferred evaluation of annotations](https://peps.python.org/pep-0749/)
13. [uv Python installation guide](https://docs.astral.sh/uv/guides/install-python/)
14. [Ruff rule reference](https://docs.astral.sh/ruff/rules/)
15. [Python Packaging User Guide — specifications](https://packaging.python.org/en/latest/specifications/)
16. [Scientific Python SPEC 0](https://scientific-python.org/specs/spec-0000/)

---

**Lesson takeaway:** choose a truthful support policy, make metadata/source/dependencies/CI agree, review every intervening release, test the actual target build, and measure real workloads before declaring an upgrade successful.
