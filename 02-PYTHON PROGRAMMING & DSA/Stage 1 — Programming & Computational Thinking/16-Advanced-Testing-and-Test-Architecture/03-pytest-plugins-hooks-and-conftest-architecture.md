# Pytest Plugins, Hooks, and `conftest.py` Architecture

> **Stage 1 · Module 16 — Advanced Testing and Test Architecture · Lesson 03**  
> Target baseline: pytest 8+, Python 3.12+. Plugin APIs and third-party tools can evolve; check the installed versions when adapting examples.

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain how pytest discovers `conftest.py`, fixtures, and plugins, and why tests should not import from `conftest.py`.
- Choose fixture scope deliberately; use `autouse`, `yield` teardown, and the `request` object safely.
- Use pytest's built-in fixtures, markers, parametrization, factories, builders, and fixture overrides.
- Configure pytest, skip tests intentionally, and define custom command-line options.
- Explain the responsibilities and signatures of important pluggy hooks.
- Build and test a small installable pytest plugin, including a `pytest11` entry point and `pytester` tests.
- Understand assertion rewriting, and when to call `pytest.register_assert_rewrite`.
- Design test suites that remain isolated, deterministic, performant, parallel-safe, and governed as they grow.

**How to read the examples:** code blocks that identify a file and provide the surrounding setup (notably the installable plugin in Section 12) are intended to form a runnable example when copied into the shown project. Short blocks that call application-specific names such as `load_environment`, `validate_record`, `ApiClient`, or `make_repository` are focused teaching fragments; those functions/classes must exist in the project being tested. Ellipses (`...`) deliberately mark omitted application-specific code, not valid standalone implementations. Commands involving third-party plugins require those plugins to be installed in the active environment.

## 1. Where this lesson fits

Module 1.7 introduced pytest, fixtures, parametrization, and mocking. This lesson builds the architecture around those fundamentals. Lesson 04 covers snapshot and golden-file testing; later lessons address flakiness, subprocesses, time and concurrency, test matrices, and fuzzing. Keep this lesson focused on pytest's test infrastructure rather than duplicating those later topics.

The key idea is that **test infrastructure is production code**: it has dependencies, lifetimes, global state, compatibility requirements, and failure modes. A clever fixture that hides side effects or a plugin that changes collection unexpectedly can make an entire suite less trustworthy.

## 2. Start with a small, understandable project

A representative layout:

```text
ledger-project/
├── pyproject.toml
├── src/
│   └── ledger/
│       ├── __init__.py
│       └── pricing.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    │   ├── conftest.py
    │   └── test_pricing.py
    ├── integration/
    │   ├── conftest.py
    │   └── test_repository.py
    └── factories/
        ├── __init__.py
        └── users.py
```

The exact layout is a choice, not a pytest requirement. A feature-oriented layout can be as valid as `unit/`, `integration/`, and `e2e/`. Choose one that helps contributors find tests and understand their risk and dependencies.

A minimal project configuration:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-ra", "--strict-markers"]
xfail_strict = true
filterwarnings = ["error"]
markers = [
  "slow: tests that take a noticeable amount of time",
  "integration: tests that require an external service or realistic integration",
  "e2e: end-to-end tests across system boundaries",
  "network: tests that require network access",
]
```

`filterwarnings = ["error"]` is a useful strict policy, but it can expose warnings from dependencies. If adopted, manage exceptions narrowly and intentionally. `--strict-markers` turns misspelled or unregistered marker names into errors. `xfail_strict = true` makes an unexpected pass of an expected-failure test fail the run.

Install tools only when needed. With `uv`, for example:

```bash
uv add --dev pytest pytest-cov pytest-xdist pytest-randomly pytest-mock
uv run pytest
```

Add async, timeout, snapshot, socket-blocking, or benchmark plugins when the project actually needs them. Avoid installing a large plugin bundle without an owner and a policy.

## 3. `conftest.py`: discovery, scope, and layering

### 3.1 What `conftest.py` is

A `conftest.py` file is a **local pytest plugin**. It can define fixtures and supported pytest hook implementations. Pytest discovers it while initializing the test paths, and its fixtures/hooks are available to tests in the corresponding directory subtree.

For example:

```text
tests/
├── conftest.py                 # shared across tests/
├── unit/
│   ├── conftest.py             # additions/overrides for tests/unit/
│   └── test_prices.py
└── integration/
    ├── conftest.py             # additions/overrides for tests/integration/
    └── test_database.py
```

Conceptually, fixture lookup follows the test's directory context outward through applicable parent `conftest.py` files and registered plugins. A fixture in `tests/unit/conftest.py` is not generally available to `tests/integration/test_database.py`. A deeper fixture can override a fixture with the same name from a parent context.

```text
test function in tests/unit/test_prices.py
             |
             v
tests/unit/conftest.py       (nearest applicable definition)
             |
             v
tests/conftest.py            (shared parent definition)
             |
             v
registered plugins / built-in fixtures
```

This is a conceptual lookup diagram, not a promise about every plugin's load order. Pytest's plugin discovery and fixture resolution have documented rules; inspect `pytest --trace-config` when debugging unexpected plugin loading.

### 3.2 Why tests should not import from `conftest.py`

Do not write:

```python
# Avoid this in a test:
from conftest import sample_user
```

`conftest.py` is discovered by pytest in directory context; it is not intended to be a normal importable utility module. Importing it directly can create path-dependent imports, duplicate module identities, circular imports, or confusing behaviour when multiple directories have their own `conftest.py`.

Instead, put reusable domain helpers in a regular module:

```python
# tests/factories/users.py
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    user_id: str
    email: str
    active: bool = True

def build_user(
    user_id: str = "user-1",
    email: str = "user@example.test",
    *,
    active: bool = True,
) -> User:
    return User(user_id=user_id, email=email, active=active)
```

Then a fixture may compose that helper:

```python
# tests/conftest.py
import pytest
from tests.factories.users import build_user

@pytest.fixture
def user():
    return build_user()
```

If `tests` is not a package in your project, use an importable test-support package or a project-supported import layout rather than adding brittle path hacks. The general rule is: **fixtures belong in pytest's fixture layer; reusable construction logic belongs in ordinary Python modules.**

### 3.3 Layering and overrides

A parent fixture establishes a default. A lower-level `conftest.py` or test module can override it for that scope:

```python
# tests/conftest.py
import pytest

@pytest.fixture
def service_url():
    return "https://service.example.test"
```

```python
# tests/integration/conftest.py
import pytest

@pytest.fixture
def service_url():
    return "http://127.0.0.1:8080"
```

Tests under `tests/integration/` resolve the nearer override; other tests keep the parent value. This is useful when integration tests need a local endpoint, but excessive same-name overrides can obscure which environment a test uses. Name materially different resources explicitly where clarity is more important than override convenience.

`pytest_plugins = [...]` can load plugin modules, but defining it in a non-root `conftest.py` is deprecated and can become an error. For shared support, prefer a top-level test configuration or a proper installed plugin.

## 4. Fixture lifecycle and scope

### 4.1 The five common scopes

| Scope | Cached lifetime | Typical use | Main risk |
|---|---|---|---|
| `function` (default) | One test function invocation | Fresh state, isolated records | Repeated setup cost |
| `class` | One test class | Shared class-level resource | State leakage between methods |
| `module` | One test module | Expensive module-local resource | Tests mutate shared state |
| `package` | Tests in a package, according to pytest package boundaries | Package-level resource | Scope boundaries are less obvious |
| `session` | One pytest session per process | Read-only metadata, expensive setup | Shared mutable state; not one global instance across xdist workers |

A broader scope reduces repeated setup but increases the amount of state that can be shared. Start with function scope. Broaden only after profiling setup cost and proving the resource can be shared safely.

Pytest prevents a fixture from depending on a narrower-scoped fixture: for example, a session-scoped fixture cannot depend on a function-scoped fixture. That would require a short-lived object to outlive its owner.

A broader-scoped fixture must use compatible dependencies. For example, `tmp_path` is function-scoped, so a session-scoped fixture should use `tmp_path_factory` instead:

```python
# tests/conftest.py
import sqlite3
import pytest

@pytest.fixture(scope="session")
def sample_db(tmp_path_factory):
    path = tmp_path_factory.mktemp("db") / "sample.sqlite"
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE entries (entry_id INTEGER PRIMARY KEY, amount INTEGER)"
        )
        connection.commit()
    finally:
        connection.close()
    return path
```

This creates one database path per pytest process/session. Under `pytest-xdist`, each worker process has its own session fixture instance unless the suite explicitly coordinates shared setup. Treat this database as shared state: tests should use isolated rows/transactions or create their own database when they need mutation.

### 4.2 Yield-based teardown

Use `yield` when setup creates a resource that must be cleaned up:

```python
# tests/conftest.py
from pathlib import Path
import sqlite3
import pytest

@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    path = tmp_path / "ledger.sqlite"
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE entries (entry_id INTEGER PRIMARY KEY, amount INTEGER)"
        )
        connection.commit()
    finally:
        connection.close()
    return path

@pytest.fixture
def open_database(database_path: Path):
    connection = sqlite3.connect(database_path)
    try:
        yield connection
    finally:
        connection.close()
```

The first fixture demonstrates a setup resource with explicit cleanup. The second yields a live connection and closes it after the test. Code after `yield` runs during teardown even if the test fails, provided execution reached the `yield`. If setup raises before reaching `yield`, post-yield teardown code does not run; clean up partially acquired resources inside setup using `try/finally` or an `ExitStack`.

A safe general pattern:

```python
@pytest.fixture
def managed_resource():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        resource.close()
```

Do not suppress cleanup exceptions casually. A failed teardown can reveal leaked or corrupted resources.

### 4.3 `autouse=True`: useful, but easy to abuse

An autouse fixture runs automatically for tests in its applicable scope, even when the test does not name it:

```python
@pytest.fixture(autouse=True)
def clear_local_cache():
    cache.clear()
    yield
    cache.clear()
```

This can enforce a small, universal invariant, such as clearing a process-local cache. But hidden setup makes test behaviour harder to understand, and an expensive autouse fixture slows every affected test. Prefer explicit dependencies when a resource is important to the test's meaning. Use autouse for narrow cross-cutting cleanup or policy, not as a hidden dependency-injection framework.

### 4.4 The `request` fixture object

`request` is pytest's `FixtureRequest`, available as a built-in fixture. It exposes context about the requesting test and fixture invocation.

- `request.param`: value for a parametrized fixture; it exists only when the fixture is parametrized.
- `request.node`: the test item or collection node requesting the fixture; useful for node IDs and markers.
- `request.config`: the active pytest configuration object.
- `request.getfixturevalue("name")`: dynamically requests another fixture. Use sparingly because it makes dependencies less visible than declaring fixture arguments.

Example:

```python
import pytest

@pytest.fixture(params=["memory", "sqlite"], ids=["memory", "sqlite"])
def repository_kind(request):
    return request.param

def test_repository_backend(repository_kind):
    assert repository_kind in {"memory", "sqlite"}
```

Do not access `request.param` from a non-parametrized fixture and assume it always exists. For ordinary dependencies, fixture arguments are clearer than dynamic lookup.

## 5. Built-in fixtures you should reach for first

| Fixture | What it provides | Example use |
|---|---|---|
| `tmp_path` | A unique `pathlib.Path` temporary directory per test | Files, small databases, generated output |
| `monkeypatch` | Reversible changes to environment variables, attributes, mappings, paths, and working directory | Isolate configuration and replace a dependency |
| `capsys` | Captured Python-level stdout/stderr | Assert command output |
| `caplog` | Captured logging records | Assert log level, message, or structured context |
| `request` | Current fixture/test context | Parametrized fixture values, node/config access |
| `pytestconfig` | Active pytest `Config` object | Read a custom CLI option |
| `recwarn` | Warnings emitted in the test | Assert warning category and message |

Examples:

```python
def test_config_uses_default(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    assert load_environment() == "development"
```

`monkeypatch` undoes its changes after the requesting test/fixture finishes. Patch where the code under test looks up the dependency, not necessarily where that dependency was originally defined.

```python
def test_cli_output(capsys):
    print("loaded 3 rows")
    captured = capsys.readouterr()
    assert captured.out == "loaded 3 rows\n"
    assert captured.err == ""
```

For subprocesses writing directly to file descriptors, `capfd` may be more appropriate than `capsys`.

```python
import logging

def test_rejected_record_is_logged(caplog):
    with caplog.at_level(logging.WARNING, logger="ledger.validation"):
        validate_record({"amount": -1})

    assert any(
        record.levelno == logging.WARNING
        and "negative amount" in record.getMessage()
        for record in caplog.records
    )
```

```python
import warnings

def test_deprecated_option_warns(recwarn):
    use_legacy_option()
    warning = recwarn.pop(DeprecationWarning)
    assert "legacy option" in str(warning.message)
```

`recwarn` is for warning assertions, not a replacement for a deliberate warnings policy. Prefer checking the warning class and a meaningful message fragment rather than matching fragile entire messages.

Use `pytestconfig.getoption("--run-integration")` or `pytestconfig.getoption("run_integration")` depending on the option declaration; examples below use the option's destination name when explicitly set.

## 6. Markers: metadata, policy, and selection

Markers attach metadata to tests. They do not change behaviour by themselves unless pytest or a plugin interprets them.

```python
import pytest

@pytest.mark.slow
def test_large_backfill():
    ...
```

Register custom markers in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = ["-ra", "--strict-markers"]
markers = [
  "slow: slower than the normal unit-test budget",
  "integration: exercises a service boundary",
  "e2e: end-to-end test",
]
```

Useful commands:

```bash
pytest -m "not slow"
pytest -m "integration and not slow"
pytest --markers
pytest --collect-only -q
```

`-m` selects by marker expression. It is distinct from `-k`, which selects by keyword/name expression. `--strict-markers` catches typos such as `@pytest.mark.integartion`. Marker names should form a small, documented vocabulary. Avoid creating one marker for every individual test characteristic; prefer a marker when it changes how tests are selected, provisioned, or governed.

## 7. Fixture design: composability, factories, parametrization, and builders

### 7.1 Small composable fixtures

A fixture should usually do one thing: construct a resource, provide a configured client, or manage a lifetime. Compose fixtures rather than building one giant fixture that creates users, database rows, a web server, and a fake clock all at once.

```python
@pytest.fixture
def api_client():
    return ApiClient(base_url="http://testserver")

@pytest.fixture
def active_user():
    return build_user(active=True)

@pytest.fixture
def authenticated_client(api_client, active_user):
    api_client.authenticate_as(active_user)
    return api_client
```

The dependency graph is explicit:

```text
active_user ─┐
             ├──> authenticated_client ──> test
api_client ──┘
```

### 7.2 Factory fixtures

A factory fixture returns a callable when each test needs to create several objects with different values:

```python
import itertools
import pytest
from tests.factories.users import build_user

@pytest.fixture
def make_user():
    counter = itertools.count(1)

    def _make_user(*, email=None, active=True):
        number = next(counter)
        return build_user(
            user_id=f"user-{number}",
            email=email or f"user-{number}@example.test",
            active=active,
        )

    return _make_user

def test_deactivation(make_user):
    first = make_user()
    second = make_user(active=False)
    assert first.active is True
    assert second.active is False
    assert first.user_id != second.user_id
```

The counter is scoped to the fixture invocation, so a fresh test gets a fresh counter. Avoid module-global counters that make test order affect generated IDs.

### 7.3 Parametrized fixtures and `pytest.param`

```python
@pytest.fixture(params=[
    pytest.param("memory", id="memory"),
    pytest.param("sqlite", id="sqlite"),
])
def repository(request):
    return make_repository(request.param)
```

For test-specific parameter marks:

```python
@pytest.mark.parametrize(
    "amount, expected",
    [
        pytest.param(0, "zero", id="zero"),
        pytest.param(10, "positive", id="positive"),
        pytest.param(-1, "invalid", marks=pytest.mark.xfail(reason="validation not implemented", strict=True), id="negative-pending"),
    ],
)
def test_classify_amount(amount, expected):
    assert classify_amount(amount) == expected
```

Only use `xfail` when the failure is a known, documented limitation. The example's third case is intentionally expected to fail until validation is implemented; when the bug is fixed, `strict=True` makes an unexpected pass visible so the marker can be removed.

Parametrization expands a test into multiple test cases. Give important cases readable IDs so CI failures are diagnostic. Avoid huge Cartesian products that multiply runtime without adding useful behavioural coverage.

### 7.4 Builders and object mothers

A builder or object mother centralizes valid default data and exposes meaningful variation. It should not hide the behaviour being tested.

```python
def build_entry(*, entry_id=1, amount=100, currency="USD"):
    return {
        "entry_id": entry_id,
        "amount": amount,
        "currency": currency,
    }

def test_usd_entry_is_preserved():
    entry = build_entry(amount=250, currency="USD")
    result = normalize_entry(entry)
    assert result["amount"] == 250
    assert result["currency"] == "USD"
```

Prefer named arguments and valid defaults. Avoid builders with dozens of unrelated options or clever implicit behaviours. A test's critical input should remain visible at the call site.

## 8. Skipping and expected failures

These mechanisms have different meanings:

- `pytest.skip("reason")` skips at runtime after the test starts.
- `@pytest.mark.skipif(condition, reason="...")` declares a condition known before execution.
- `pytest.importorskip("optional_dependency")` skips when an optional dependency cannot be imported.
- `@pytest.mark.xfail(..., strict=True)` marks a known defect or unsupported case as expected to fail. If it unexpectedly passes, the test suite fails.
- `pytest.param(value, marks=pytest.mark.skip(...))` or `pytest.param(..., marks=pytest.mark.xfail(...))` marks one parameter case.

```python
import sys
import pytest

@pytest.mark.skipif(sys.platform == "win32", reason="POSIX-specific permission semantics")
def test_posix_mode_bits():
    ...

def test_optional_arrow_backend():
    arrow = pytest.importorskip("pyarrow")
    assert arrow.__version__
```

Use precise skip reasons and keep them current. A skipped test is not evidence that behaviour works. A strict xfail should have an issue reference or a clear reason and an owner; remove it when the defect is fixed. Avoid broad `importorskip` around a dependency that is actually required by the package under test, because that can hide a broken environment.

## 9. Custom CLI options and collection-time policy

### 9.1 Add `--run-integration`

Put both hooks in the root `tests/conftest.py` (or a plugin loaded by the test suite):

```python
# tests/conftest.py
import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run tests marked integration",
    )

def pytest_collection_modifyitems(config, items):
    if config.getoption("run_integration"):
        return

    skip_integration = pytest.mark.skip(
        reason="pass --run-integration to enable integration tests"
    )
    for item in items:
        if item.get_closest_marker("integration") is not None:
            item.add_marker(skip_integration)
```

Register the marker in `pyproject.toml`. Run:

```bash
pytest                         # integration tests are collected but skipped
pytest --run-integration       # integration tests execute
pytest -m "not integration"    # excludes them from selection entirely
```

These are different controls: the hook preserves visibility of skipped tests in reports, while `-m "not integration"` deselects them. `pytest_collection_modifyitems(config, items)` receives collected items and may modify the list or add marks. Do not perform network calls or expensive provisioning in this hook; collection should be fast and predictable.

`pytest_addoption(parser)` is a configuration hook used to register options before normal command-line parsing is completed. If multiple plugins use the same option name, pytest reports a conflict. Prefix project-specific options when appropriate to avoid collisions.

### 9.2 Configuration belongs in one deliberate place

Example:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-ra", "--strict-markers"]
xfail_strict = true
filterwarnings = ["error"]
markers = [
  "slow: slow-running tests",
  "integration: requires a service boundary",
  "e2e: end-to-end test",
]
```

Keep universal defaults in project configuration and exceptional invocation choices in CI commands or developer scripts. Be careful with `addopts`: a hidden default can make local and CI commands behave differently. `pytest --trace-config` helps identify loaded plugins and configuration.

## 10. The plugin ecosystem: choose tools for explicit jobs

| Tool | Main job | Practical caveat |
|---|---|---|
| `pytest-xdist` | Distribute tests across worker processes (`-n auto`, `-n 4`) | Tests and resources must be parallel-safe; session fixtures run in each worker process unless deliberately coordinated |
| `pytest-randomly` | Randomize test order and reseed common random sources; report a reproducible seed | Random order reveals coupling; it does not itself fix it |
| `pytest-cov` | Integrate coverage.py into pytest (`--cov`, `--cov-branch`) | Configure source and branch policy consistently; subprocess coverage needs explicit setup |
| `pytest-mock` | Provides the `mocker` fixture around `unittest.mock` | Mock the dependency boundary; excessive mocking can couple tests to implementation |
| `pytest-asyncio` / `anyio` | Test async functions and event-loop behaviour | Follow the selected plugin's event-loop and fixture-scope policy; don't casually mix competing async test modes |
| `pytest-timeout` | Fail or interrupt tests that exceed a time limit | A timeout is a safety net, not a performance diagnosis; platform and timeout method matter |
| `pytest-benchmark` | Track benchmark results | Benchmarks need stable environments and should not be treated like ordinary unit assertions |
| `syrupy` | Snapshot testing | Review diffs; don't auto-approve snapshots in CI |
| `pytest-socket` | Restrict network/socket access during tests | Allowlist only the required local/network behaviour; run network-dependent tests in a clearly separated job |

Examples:

```bash
pytest -n auto
pytest --randomly-seed=1234
pytest --cov=ledger --cov-branch --cov-report=term-missing
pytest --disable-socket
```

Plugin command-line flags can vary by plugin version. Confirm with `pytest --help` and the plugin's own documentation. Use a small, maintained set of plugins and periodically review their compatibility with the project's pytest version.

## 11. Pluggy hooks and the pytest execution model

Pytest is extensible through **pluggy**, which calls hook implementations registered by built-in plugins, installed plugins, and `conftest.py` plugins. Hook functions are named according to documented specifications, typically with a `pytest_` prefix. Implement the documented signature and semantics; do not treat internal `_pytest` modules as a stable public API.

### 11.1 Simplified execution flow

```text
startup
  ├─ parse early plugin-blocking / plugin-loading options
  ├─ load built-in and installed plugins
  ├─ load initial conftest.py files
  └─ parse configuration and configure plugins
       |
       v
collection
  ├─ discover files / collect test items
  ├─ pytest_generate_tests can add parameter sets during collection
  ├─ pytest_collection_modifyitems(config, items)
  └─ collection/report hooks
       |
       v
each test item
  ├─ pytest_runtest_setup(item)
  ├─ pytest_runtest_makereport(item, call) -> setup report
  ├─ pytest_runtest_call(item)
  ├─ pytest_runtest_makereport(item, call) -> call report
  ├─ pytest_runtest_teardown(item, nextitem)
  └─ pytest_runtest_makereport(item, call) -> teardown report
       |
       v
reporting and session finish
  ├─ pytest_runtest_logreport(report)
  ├─ pytest_terminal_summary(terminalreporter, exitstatus, config)
  └─ pytest_sessionfinish(session, exitstatus)
```

This omits internal details and conditional branches. For example, the call phase is not run if setup fails. `pytest_runtest_makereport` is called for setup, call, and teardown phases, so failure-handling logic should inspect `report.when` and `report.failed` instead of assuming every report represents the test body.

### 11.2 High-value hooks

| Hook | Typical purpose | Signature shape |
|---|---|---|
| `pytest_addoption(parser)` | Register CLI options and ini values | `parser` |
| `pytest_configure(config)` | Register markers or initialize plugin state | `config` |
| `pytest_sessionstart(session)` | Session-start work after configuration | `session` |
| `pytest_generate_tests(metafunc)` | Add parametrization during collection | `metafunc` |
| `pytest_collection_modifyitems(config, items)` | Mark, reorder, or filter collected items | `config, items` |
| `pytest_runtest_setup(item)` | Before fixture setup/test execution | `item` |
| `pytest_runtest_call(item)` | Invoke the test call phase | `item` |
| `pytest_runtest_teardown(item, nextitem)` | Tear down test state | `item, nextitem` |
| `pytest_runtest_makereport(item, call)` | Produce a report for each test phase | `item, call` |
| `pytest_runtest_logreport(report)` | Observe a completed phase report | `report` |
| `pytest_terminal_summary(terminalreporter, exitstatus, config)` | Add a terminal summary section | `terminalreporter, exitstatus, config` |
| `pytest_sessionfinish(session, exitstatus)` | Final session processing | `session, exitstatus` |

Important distinctions:

- `pytest_configure` is for configuration-time setup; it is not called once per test.
- `pytest_collection_modifyitems` sees collected items and is a natural place for selection policy.
- `pytest_generate_tests` is invoked for a test's `Metafunc` and is useful for dynamic parametrization.
- `pytest_runtest_makereport` is a **first-result hook** in pytest's hook specifications. If implementing it to replace the default report, use the documented `@pytest.hookimpl(hookwrapper=True)` pattern or another supported documented approach; do not accidentally suppress the normal report.
- A hook wrapper can execute code before and after other implementations. Learn the pluggy wrapper protocol before using it.
- Terminal reporting hooks should consume stored, per-test observations. They should not reach back into the test body or rerun tests.

## 12. Building a small installable pytest plugin

Use a real plugin package when functionality should be shared across repositories, versioned, tested independently, and installed through packaging metadata. A project-local `conftest.py` is usually sufficient for repository-specific fixtures and policy.

### 12.1 Package layout and entry point

```text
pytest-slowledger/
├── pyproject.toml
├── src/
│   └── pytest_slowledger/
│       ├── __init__.py
│       └── plugin.py
└── tests/
    └── test_plugin.py
```

`pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "pytest-slowledger"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["pytest>=8"]

[project.entry-points.pytest11]
slowledger = "pytest_slowledger.plugin"
```

The `pytest11` entry-point group tells pytest which module to load as an installed plugin. The distribution name and entry-point name are identifiers; the module path must match the source package. Install the package into the environment used to run pytest, typically as an editable development install:

```bash
python -m pip install -e .
pytest --trace-config
```

### 12.2 Implement a slow-test summary

This small plugin records call-phase durations and prints those greater than one second:

```python
# src/pytest_slowledger/__init__.py
"""Pytest plugin package."""
```

```python
# src/pytest_slowledger/plugin.py
from __future__ import annotations

import pytest

_SLOW_CALLS = pytest.StashKey[list[tuple[float, str, str]]]()

def pytest_addoption(parser):
    group = parser.getgroup("slowledger")
    group.addoption(
        "--slowledger-threshold",
        action="store",
        type=float,
        default=1.0,
        help="report test call phases slower than this many seconds",
    )

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slowledger_ignore: do not include this test in the slow-call summary",
    )
    config.stash[_SLOW_CALLS] = []

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # Measure only the test-call phase, not fixture setup or teardown.
    if report.when != "call":
        return
    if item.get_closest_marker("slowledger_ignore") is not None:
        return

    item.config.stash[_SLOW_CALLS].append(
        (report.duration, item.nodeid, report.outcome)
    )

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    threshold = config.getoption("slowledger_threshold")
    slow_items = [
        row for row in config.stash[_SLOW_CALLS]
        if row[0] > threshold
    ]
    if not slow_items:
        return

    terminalreporter.write_sep("=", f"slow test calls (> {threshold:.2f}s)")
    for duration, nodeid, outcome in sorted(slow_items, reverse=True):
        terminalreporter.write_line(
            f"{duration:8.3f}s [{outcome}] {nodeid}"
        )
```

The hook uses the public hook-wrapper mechanism to observe the `TestReport` created by other implementations. `report.duration` is the duration for that phase. The code deliberately records only the call phase and stores results in `config.stash` under a plugin-owned `pytest.StashKey`; this avoids attaching ad hoc attributes to pytest's `Config` object. Under `pytest-xdist`, each worker has its own config and stash; worker summaries are not automatically a single globally aggregated report. If cross-worker aggregation is required, design and test that protocol separately.

A hook implementation can be concise, but it should remain observable, deterministic, and limited in responsibility. Avoid monkeypatching pytest internals or importing `_pytest.*` modules.

### 12.3 Test the plugin with `pytester`

`pytester` creates an isolated temporary pytest project and lets the test invoke pytest as a subprocess-like test run. Enable it from the **project-root** `conftest.py` (the top-level conftest for this test run), so the declaration is not placed in a nested conftest where `pytest_plugins` is deprecated:

```python
# conftest.py at the repository root
pytest_plugins = ["pytester"]
```

Test the public behaviour, not just that the module imports:

```python
# tests/test_plugin.py
def test_slowledger_reports_slow_call(pytester):
    pytester.makepyprojecttoml("""
        [tool.pytest.ini_options]
        addopts = []
    """)
    pytester.makeconftest("""
        pytest_plugins = ["pytest_slowledger.plugin"]
    """)
    pytester.makepyfile("""
        import time

        def test_slow():
            time.sleep(1.05)
    """)

    result = pytester.runpytest("--slowledger-threshold=1.0", "-q")

    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines([
        "*slow test calls (> 1.00s)*",
        "*test_slow*",
    ])
```

This test intentionally takes about a second. In a large plugin suite, avoid making every test slow; you can test threshold boundaries with a controlled clock or test a helper that formats/filter observations, while retaining at least one integration test for the real hook path. The example uses the plugin module directly in the isolated test project; the `pytest11` entry point is verified separately by installing the package into a clean environment and checking `pytest --trace-config`.

If the plugin is not automatically available to the child pytest process, install it into the same environment or explicitly load it with `-p pytest_slowledger.plugin`. The clean-environment install test is the definitive check for packaging and entry-point discovery.

## 13. Assertion rewriting and helper modules

Pytest improves plain `assert` failures by rewriting test and plugin modules' abstract syntax trees during import. This allows output such as the actual values of subexpressions rather than only `AssertionError`.

Not every arbitrary helper module is automatically rewritten. If an installed plugin has a helper module whose assertions need pytest's introspection, register it **before it is imported**:

```python
# src/pytest_slowledger/__init__.py
import pytest

pytest.register_assert_rewrite("pytest_slowledger.assertions")
```

```python
# src/pytest_slowledger/assertions.py
def assert_valid_amount(amount):
    assert amount >= 0
    assert amount < 10_000
```

Because importing the package's `__init__.py` occurs before importing its submodule in this example, the helper can be registered in time. If `pytest_slowledger.assertions` has already been imported, registering it later cannot retroactively rewrite the already-loaded module. Do not use `assert` for validation in production code: Python can remove assertions under optimization, and production error handling should use explicit exceptions. Assertion rewriting is for test diagnostics, not runtime input validation.

## 14. Test architecture at scale

### 14.1 Separate test levels by purpose

A pragmatic structure:

```text
tests/
├── unit/          # fast, isolated, deterministic
├── integration/   # database, queue, API, filesystem boundaries
├── e2e/           # critical user/system journeys
├── contract/      # provider/consumer expectations at boundaries
├── factories/     # ordinary reusable data builders
└── conftest.py    # shared pytest fixtures and policy
```

Unit tests should dominate the fast feedback loop. Integration tests verify real boundary behaviour with controlled dependencies. End-to-end tests cover a small number of critical paths. Contract tests assert that two components agree on an interface, schema, event, or protocol; they are not a synonym for all integration tests.

Mirrored source/test layouts can make navigation easy. Feature-oriented layouts can keep code and tests close conceptually. Choose a convention, document it, and avoid duplicate tests that assert the same behaviour at every layer without adding confidence.

### 14.2 Parallel execution and shared resources

`pytest-xdist` runs tests in separate worker processes. A session-scoped fixture generally runs once **per worker**, not once globally across the whole distributed run. Shared databases, object stores, ports, queues, and files need explicit isolation.

Useful practices:

- Use `worker_id` from xdist to derive unique schemas, prefixes, file paths, or test accounts. Without xdist it returns `"master"`.
- Prefer OS-assigned ephemeral ports (bind to port `0`) over hard-coded ports.
- Give each worker a separate database/schema or use per-test transactions with reliable rollback where appropriate.
- Use `--dist loadgroup` and the `xdist_group` marker only when tests genuinely need to stay on the same worker; grouping is not a substitute for shared-state cleanup.
- If all workers must share a generated artifact, use a lock and an atomic write protocol. Do not assume session fixture caching is shared between processes.
- Never let tests depend on a fixed execution order, even if a particular xdist distribution mode appears to preserve some grouping.

Example for unique worker-specific names (`worker_id` is provided by the installed `pytest-xdist` plugin):

```python
import pytest

@pytest.fixture
def schema_name(worker_id):
    return f"test_schema_{worker_id}"
```

For tests that create multiple resources within one worker, include a per-test unique component as well. `worker_id` alone separates workers, not tests in the same worker.

### 14.3 Fixture performance and isolation trade-offs

Measure fixture costs before optimizing. Common improvements:

1. Keep unit-test setup local and cheap.
2. Reuse immutable/read-only expensive setup at a broader scope only when safe.
3. For database tests, consider transaction rollback or disposable schemas; ensure application code cannot commit around the rollback strategy.
4. Use `tmp_path_factory` for session- or module-scoped temporary directories, rather than requesting function-scoped `tmp_path` from a broad-scoped fixture.
5. Avoid loading large data, starting containers, or opening network connections from an autouse fixture used by all tests.
6. Report setup, call, and teardown time separately when diagnosing slowness; a slow fixture is not necessarily a slow test body.

An expensive session fixture is not inherently wrong. A mutable session fixture used by unrelated tests without reset boundaries is the problem.

### 14.4 Order independence and randomization

Run the suite with a random-order plugin, for example:

```bash
pytest --randomly-seed=1234
```

Record the seed and failing node IDs when investigating a failure. Re-run with the same seed to reproduce, then isolate the smallest pair or group of tests that demonstrates the dependency. Randomization reveals hidden coupling; the fix is to reset state, create unique resources, or remove the order assumption—not to pin the suite permanently to the lucky seed.

### 14.5 Governance for a maintainable suite

Establish lightweight rules:

- **Naming:** use descriptive `test_...` names that state behaviour or an observable outcome.
- **Markers:** define an approved vocabulary, register every custom marker, and document the CI job that runs each category.
- **Ownership:** assign an owner for custom plugins, shared fixtures, and flaky tests.
- **Flaky quarantine:** quarantine only with an issue, owner, reason, expiry/review date, and separate reporting. Quarantine must not silently become permanent.
- **Removal:** delete obsolete tests when behaviour is removed, but preserve regression tests for defects that could recur.
- **Review:** reject assertions coupled only to private implementation details unless those details are themselves a deliberate contract.
- **Plugin hygiene:** pin or constrain versions, review plugin changes, check `pytest --trace-config`, and keep a documented upgrade path.
- **CI:** use a fast deterministic unit-test job on every change; reserve slow integration, benchmark, and broader compatibility jobs for appropriate stages.
- **Network policy:** use socket restrictions by default where feasible, then run explicitly marked network tests in a controlled job. A test that unexpectedly reaches the public internet is not isolated.
- **Metrics:** treat duration, flakiness, coverage, and mutation score as diagnostic signals—not goals that can replace code review.

## 15. Common mistakes and their corrections

| Mistake | Why it harms the suite | Better approach |
|---|---|---|
| Autouse fixture provisions expensive infrastructure | Adds hidden cost to unrelated tests | Make the dependency explicit or scope it narrowly |
| Mutable session-scoped fixture | Test outcomes depend on earlier mutations | Use immutable shared data, per-test copies, or reset boundaries |
| `from conftest import ...` | Creates brittle import and discovery behaviour | Move helper logic to a normal module; expose setup as fixtures |
| Giant fixture does everything | Hides dependencies and makes failures hard to diagnose | Compose small fixtures with clear names |
| Markers are not registered | Typos silently persist unless strict mode catches them | Register markers and use `--strict-markers` |
| `xfail` is non-strict and forgotten | A fixed bug can remain labelled expected failure | Prefer `xfail_strict = true` and track removal |
| Collection hook performs I/O | Makes collection slow and non-deterministic | Restrict collection hooks to metadata and cheap policy |
| Plugin relies on `_pytest` internals | Upgrades can break it without a public API guarantee | Use documented hook specs and public pytest APIs |
| Plugin tests only import the module | Does not prove hooks, CLI options, or entry points work | Test with `pytester` and a clean installed environment |
| Assuming one session fixture across xdist | Workers are separate processes | Isolate by worker or coordinate shared setup explicitly |
| Randomized failures are “fixed” by pinning a seed | The hidden dependency remains | Reproduce by seed, then remove shared state/order dependence |
| Blanket socket disable breaks every integration test | Policy is not aligned to test categories | Separate offline tests from explicit network-enabled tests |

## 16. Practical exercises

### Exercise A — fixture discovery

Create a root `tests/conftest.py` fixture named `mode` returning `"default"` and a `tests/integration/conftest.py` override returning `"integration"`. Add one test in each subtree. Predict each value before running pytest.

**Expected result:** unit/default tests see `"default"`; tests under `integration/` see `"integration"`.

### Exercise B — safe teardown

Write a fixture that opens a temporary text file, yields its path, and ensures the handle is closed even when an assertion fails. Explain what happens if setup raises before `yield`.

**Solution sketch:** acquire the handle, use `try: yield path finally: handle.close()`. If setup fails before reaching `yield`, the post-yield block is not entered, so use a `try/finally` around acquisition/setup to close partially acquired resources.

### Exercise C — integration option

Implement `--run-integration`; when absent, mark tests carrying `@pytest.mark.integration` as skipped. Register the marker and verify the difference between `pytest` and `pytest -m "not integration"`.

**Solution:** use the `pytest_addoption` and `pytest_collection_modifyitems` implementation in Section 9. The first run reports skipped integration tests; the marker expression deselects them.

### Exercise D — remove a god fixture

Given a fixture that creates a user, database, API client, and mock clock, split it into four fixtures and compose only what each test needs.

**Review criterion:** dependencies are visible in test signatures; unrelated tests do not pay for unused resources.

### Exercise E — plugin design

Build the slow-call plugin in Section 12. Add tests for: no test exceeding threshold, one test exceeding threshold, the ignore marker, and a failed test whose call duration is still reported. Test the entry point in a clean environment.

**Review criterion:** call-phase duration is recorded once, setup/teardown are excluded, reporting does not change the test outcome, and worker aggregation limitations are documented.

## 17. Self-check with solutions

### 1. Where does pytest look for fixtures, and how does overriding work?

Pytest discovers fixtures from applicable `conftest.py` files in the test's directory context and parent directories, as well as registered plugins and built-in fixtures. A nearer fixture definition can override a parent fixture with the same name for tests in that subtree. A fixture in one sibling subtree is not generally available in the other sibling. Do not import from `conftest.py`; move shared non-fixture logic into normal modules.

### 2. Write a `--run-integration` option that auto-skips integration tests.

Define `pytest_addoption(parser)` and add a boolean `--run-integration` option. In `pytest_collection_modifyitems(config, items)`, return immediately when `config.getoption("run_integration")` is true; otherwise add `pytest.mark.skip(reason=...)` to each item whose closest `integration` marker exists. Register `integration` in `[tool.pytest.ini_options].markers`. The complete example is in Section 9.1.

### 3. Sketch a plugin that records slow tests (> 1 s) in a terminal summary, with a `pytester` test.

Implement `pytest_runtest_makereport(item, call)` as a hook wrapper, yield to other implementations, inspect the returned report, and record `report.duration`, `item.nodeid`, and `report.outcome` only when `report.when == "call"`. In `pytest_terminal_summary(terminalreporter, exitstatus, config)`, filter recorded calls by the configured threshold and print them. Enable `pytester` using `pytest_plugins = ["pytester"]` in the plugin test suite, then call `pytester.runpytest(...)` on an isolated test project and assert both outcomes and summary text. Section 12 contains a runnable minimal implementation and a focused integration test.

## 18. Completion checklist

You are ready to move on when you can:

- [ ] Explain `conftest.py` subtree visibility and override rules without importing it.
- [ ] Select fixture scope based on measured cost and state-sharing risk.
- [ ] Write a yield fixture with correct cleanup for success and failure paths.
- [ ] Use `tmp_path`, `monkeypatch`, `capsys`, `caplog`, `request`, `pytestconfig`, and `recwarn`.
- [ ] Register markers and select tests with `-m`.
- [ ] Build factory fixtures and data builders without global mutable counters.
- [ ] Distinguish `skip`, `skipif`, `importorskip`, and strict `xfail`.
- [ ] Add and test a custom CLI option and collection policy.
- [ ] Explain the role of configuration, collection, execution, reporting, and terminal-summary hooks.
- [ ] Package a plugin through `pytest11`, test it with `pytester`, and understand assertion rewriting.
- [ ] Run tests in random order and under xdist without shared-resource collisions.
- [ ] Describe your team's marker, flaky-test, plugin-upgrade, and test-ownership policies.

## References

Use official documentation as the source of truth for API details and plugin-version-specific flags:

- [pytest: Writing plugins](https://docs.pytest.org/en/stable/how-to/writing_plugins.html)
- [pytest: API reference and hook specifications](https://docs.pytest.org/en/stable/reference/reference.html)
- [pytest: Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest: Markers](https://docs.pytest.org/en/stable/how-to/mark.html)
- [pytest-xdist documentation](https://pytest-xdist.readthedocs.io/en/stable/)
- [pytest-randomly documentation](https://github.com/pytest-dev/pytest-randomly)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/en/latest/)
- [pytest-mock documentation](https://pytest-mock.readthedocs.io/en/latest/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/en/stable/)
- [AnyIO testing documentation](https://anyio.readthedocs.io/en/stable/testing.html)
- [pytest-timeout documentation](https://github.com/pytest-dev/pytest-timeout)
- [Syrupy documentation](https://syrupy.readthedocs.io/en/latest/)
- [pytest-socket documentation](https://github.com/miketheman/pytest-socket)
- [Pluggy documentation](https://pluggy.readthedocs.io/en/stable/)

**Version note:** pytest, pluggy, and third-party plugins evolve independently. Before copying a plugin hook or CLI flag into production, check the documentation matching the versions pinned in your lockfile. The examples here use documented pytest hook names and APIs and deliberately avoid reliance on pytest's private implementation modules.
