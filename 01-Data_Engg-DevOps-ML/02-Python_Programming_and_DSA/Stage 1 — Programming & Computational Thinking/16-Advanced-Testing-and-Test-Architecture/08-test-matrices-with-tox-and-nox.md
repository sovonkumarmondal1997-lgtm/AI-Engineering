# Test Matrices with `tox` and `nox`

> **Stage 1 · Module 16 — Advanced Testing and Test Architecture · Lesson 08**
>
> Target file: `08-test-matrices-with-tox-and-nox.md`

## Learning objectives

By the end of this lesson, you should be able to:

- Explain why a library needs a compatibility matrix rather than one successful local test run.
- Choose between `tox` and `nox`, configure isolated environments, and pass arguments to test commands.
- Test supported Python versions, operating systems, dependency ranges, and optional extras without creating an unmanageable matrix.
- Test declared minimum dependency versions and pre-releases deliberately.
- Separate test, lint, type-check, documentation, packaging, security, performance, and coverage tasks.
- Test the built wheel and source distribution in clean environments without accidentally importing the checkout.
- Reproduce a failed matrix session locally and understand the limits of caches and lock files.

This lesson uses a hypothetical installable package named `ledger` with a `src/` layout. Replace its package name, extras, paths, and commands with those from your project. The examples are configuration patterns, not a claim that every tool release or platform combination has been verified. Always validate the chosen versions in your own supported environment.

---

## 1. Why test matrices exist

A library can pass on one machine and still fail for users. A single run only demonstrates that one combination worked:

- one Python interpreter and implementation;
- one operating system and architecture;
- one dependency resolution;
- one set of optional dependencies;
- one collection of system libraries and environment variables;
- one installation path (often the checkout rather than an installed artifact).

A **test matrix** deliberately varies selected dimensions to find incompatibilities before users do.

| Dimension | Example values | What it catches |
|---|---|---|
| Python | 3.12, 3.13, 3.14 | Syntax, standard-library, interpreter and packaging differences |
| OS | Linux, Windows, macOS | Path, process, filesystem, compiler and platform differences |
| Dependency set | lowest supported, latest compatible | Incorrect lower bounds and regressions in newer releases |
| Extras | base, `pandas`, `all` | Missing optional dependencies and broken integrations |
| Artifact | source checkout, wheel, sdist | Packaging omissions and import-path mistakes |
| Runtime mode | regular CPython, optional free-threaded build | Thread-safety and runtime-compatibility issues |

Not every Cartesian product is worth running on every commit. The objective is **useful coverage of risk**, not the largest possible matrix.

### Compatibility is a claim you must test

If `pyproject.toml` says `requires-python = ">=3.12"`, users may reasonably expect every supported Python version in that range that your project claims to support. If a dependency is declared as `library-x >= 2.4`, your code should work with an allowed version satisfying that lower bound, subject to the dependency's own platform and Python constraints.

A successful run with the newest dependency does not prove that the declared minimum works. Likewise, a successful Linux run does not prove Windows path handling works.

### Example package layout

```text
ledger-project/
├── pyproject.toml
├── tox.ini
├── noxfile.py
├── src/
│   └── ledger/
│       ├── __init__.py
│       └── core.py
├── tests/
│   └── test_core.py
└── docs/
```

A `src/` layout makes accidental imports from the repository root less likely. It does not, by itself, guarantee that a test imports the installed distribution: the test environment and import path still matter.

---

## 2. What `tox` and `nox` do

Both tools create isolated environments, install the dependencies required for a task, and run commands in those environments. Their isolation helps prevent a developer's global packages from silently determining test results.

### `tox`: environment-oriented configuration

`tox` typically declares environments in configuration. Environment names such as `py312`, `py313`, and `py314` communicate intent and can be used to select sessions.

Typical uses:

- running tests across supported Python versions;
- installing a project's test extra;
- running lint/type/docs/package checks in separate environments;
- reusing environment definitions locally and in CI.

### `nox`: Python-defined sessions

`nox` defines sessions in `noxfile.py`. A session is a Python function receiving a session object. This makes branching, parametrization, shared helper functions, and dynamic environment construction natural.

Typical uses:

- matrix dimensions that need Python logic;
- parametrized sessions such as minimum/latest dependency resolution;
- reusable functions shared by several repositories;
- sessions with different installation or command policies.

### Choosing between them

| Concern | `tox` | `nox` |
|---|---|---|
| Main configuration | `tox.ini` or supported `pyproject.toml` sections | `noxfile.py` |
| Session definition | Configuration environments | Python functions/decorators |
| Simple version matrix | Very concise | Also straightforward |
| Dynamic branching | Possible, but configuration-centric | Natural Python control flow |
| Session arguments | `{posargs}` in commands | `session.posargs` |
| Typical invocation | `tox -e py313` | `nox -s tests-3.13` |
| Environment reuse | `tox` reuses matching environments by default; `-r` recreates | Nox reuses sessions' virtualenvs by default; `--reuse-venv`/`--no-reuse-venv` control behavior depending on version |

Pick one primary runner unless there is a concrete reason to maintain both. Running both with overlapping responsibilities can double maintenance and create inconsistent definitions of “the test suite.”

**Version note:** exact command-line flags and configuration options evolve. Check the documentation for the versions pinned by your project before treating an example as authoritative.

---

## 3. Project metadata and test dependencies

A runner can only install a package and its extras correctly when the project metadata is accurate. A representative `pyproject.toml` might include:

```toml
[build-system]
requires = ["hatchling>=1.26"]
build-backend = "hatchling.build"

[project]
name = "ledger"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "requests>=2.31",
]

[project.optional-dependencies]
pandas = ["pandas>=2.2"]
all = ["requests>=2.31", "pandas>=2.2"]

test = [
  "pytest>=8",
  "pytest-cov>=5",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"
```

This is illustrative metadata. Use a build backend appropriate for the actual project, and make sure the backend's package-discovery configuration includes `src/ledger`. Do not copy dependency constraints blindly.

**Important packaging detail:** PEP 621 project metadata supports optional dependency groups under `[project.optional-dependencies]`. A key named `test` there creates an installable extra, so `pip install -e ".[test]"` or `session.install(".[test]")` can request it. Modern packaging also has a separate concept of development dependency groups (for example, `[dependency-groups]` as supported by the relevant tooling). A development group is not automatically the same as a published extra. Confirm how your selected installer resolves groups.

---

## 4. A practical `tox.ini`

The following is a compact configuration pattern for a current tox 4-style project. It defines Python-version test environments and independent lint/type sessions. Pin tox and any plugins in the developer tooling environment, and check option names against the installed tox release.

```ini
[tox]
env_list = py312, py313, py314, lint, type
requires = tox>=4

[testenv]
package = editable
extras = test
commands = pytest {posargs}

[testenv:lint]
skip_install = true
deps = ruff
commands =
    ruff check .
    ruff format --check .

[testenv:type]
skip_install = true
deps =
    mypy
    types-requests
commands = mypy src/ledger
```

### What the sections mean

- `[tox]` selects the default environments. `tox -e py313` selects only the Python 3.13 test environment.
- `requires = tox>=4` expresses a minimum tox version for tox to bootstrap. In a real project, consider a narrower tested range or a pinned development environment.
- `[testenv]` is the common environment definition inherited by version-specific environments. `extras = test` requests the project's `test` extra.
- `package = editable` installs the project in editable mode. This is convenient for ordinary development tests, but it is **not** the final-artifact verification described later.
- `{posargs}` forwards extra arguments supplied after `--` to pytest.
- `skip_install = true` in lint/type sessions means the project itself is not installed by tox in those sessions. Their commands operate on the checkout and use the session's tool dependencies.

Run examples:

```bash
tox
tox -e py313
tox -e py313 -- tests/test_core.py -q
tox -e lint,type
tox -r -e py313
```

Expected behavior:

- `tox` creates or reuses the configured environments and runs each selected command.
- `tox -e py313` requests the interpreter represented by that environment name. If the corresponding interpreter is not available or cannot be provisioned, environment creation fails; it does not magically make every Python version available on every machine.
- `tox -e py313 -- tests/test_core.py -q` forwards the test path and quiet option to pytest.
- `tox -r -e py313` recreates the selected environment rather than trusting its previous contents.

### `tox` and interpreter availability

For the lesson's matrix, `py312`, `py313`, and `py314` mean Python 3.12, 3.13, and 3.14 interpreters respectively. They are not promises that all interpreters are installed.

Before running:

```bash
python --version
tox --version
```

Install the required interpreters using your operating system's package manager, `uv python install`, `pyenv`, a CI setup action, or another approved mechanism. Check the project's platform support and the selected tool's interpreter-discovery behavior. Python 3.14 availability, pre-release builds, and platform-specific wheels depend on the date and environment; confirm them rather than assuming.

### A supported `pyproject.toml` alternative

Tox supports configuration in `pyproject.toml` through its own tool section in supported releases. Do not mix two competing sources of tox configuration. A tox 4-style equivalent can be represented as:

```toml
[tool.tox]
requires = ["tox>=4"]
env_list = ["py312", "py313", "py314", "lint", "type"]

[tool.tox.env_run_base]
package = "editable"
extras = ["test"]
commands = [["pytest", "{posargs}"]]

[tool.tox.env.lint]
skip_install = true
deps = ["ruff"]
commands = [
  ["ruff", "check", "."],
  ["ruff", "format", "--check", "."],
]

[tool.tox.env.type]
skip_install = true
deps = ["mypy", "types-requests"]
commands = [["mypy", "src/ledger"]]
```

**Treat this as a configuration pattern, not a compatibility guarantee for every tox 4 minor release.** TOML schema details and environment override semantics must be checked against the exact tox version used by the repository. If the team already has a working `tox.ini`, there is no need to migrate just for appearance.

A useful audit is to run the tool's configuration display/listing command, then execute each session. Parsing valid TOML only proves the file is syntactically valid; it does not prove tox recognizes every key or that the resulting commands work.

---

## 5. A practical `noxfile.py`

Nox configuration is Python code. Here is a straightforward version matrix with test, lint, type-check, docs, and build-check sessions.

```python
import nox

PYTHONS = ["3.12", "3.13", "3.14"]


@nox.session(python=PYTHONS)
def tests(session: nox.Session) -> None:
    """Run the test suite on each selected interpreter."""
    session.install("-e", ".[test]")
    session.run("pytest", "--cov=ledger", "--cov-report=term-missing",
                *session.posargs)


@nox.session
def lint(session: nox.Session) -> None:
    """Check formatting and lint without installing the project."""
    session.install("ruff")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


@nox.session
def typecheck(session: nox.Session) -> None:
    """Run static type checking."""
    session.install("mypy", "types-requests")
    session.run("mypy", "src/ledger")


@nox.session
def docs(session: nox.Session) -> None:
    """Build documentation."""
    session.install("sphinx")
    session.run("sphinx-build", "-W", "-b", "html", "docs", "build/html")


@nox.session
def build_check(session: nox.Session) -> None:
    """Build artifacts and check their distribution metadata."""
    session.install("build", "twine")
    session.run("python", "-m", "build")
    artifacts = sorted(Path("dist").glob("*"))
    if not artifacts:
        session.error("Build produced no distribution artifacts in dist/.")
    session.run("twine", "check", "--strict", *(str(path) for path in artifacts))
```

The `build_check` example assumes the build backend is declared in project metadata and that the `build` command can write to `dist/`.

Run:

```bash
nox --list
nox -s tests-3.13
nox -s tests-3.13 -- tests/test_core.py -q
nox -s lint
nox -s typecheck
nox -s docs
nox -s build_check
```

Session names are normally derived from the function name and Python version. `tests` with `python="3.13"` is commonly selected as `tests-3.13`; inspect `nox --list` for the actual names generated by your installed Nox version.

`session.posargs` forwards user arguments as separate arguments. Avoid building shell command strings; `session.run("pytest", *session.posargs)` preserves argument boundaries more safely.

### `nox.parametrize` for dimensions

For a small, explicit dimension, parametrization can create several sessions:

```python
import nox


@nox.session(python=["3.12", "3.13", "3.14"])
@nox.parametrize("constraints", ["constraints-min.txt", "constraints-latest.txt"])
def dependency_matrix(session: nox.Session, constraints: str) -> None:
    # Each constraints file must be maintained and reviewed for this project.
    # Constraints affect versions of requested packages; they do not install
    # packages by themselves.
    session.install("-e", ".[test]", "-c", constraints)
    session.run("pytest", *session.posargs)
```

This is an executable pattern if both constraints files exist and cover the dependencies you intend to control. The “minimum” file should pin direct dependencies to their declared minimums while retaining a compatible transitive resolution; the “latest” file should constrain packages to the latest compatible versions you intend to test. Verify the resolved environment in each session. A parameter name alone does not create a dependency strategy, and constraints do not install packages that are not requested.

---

## 6. Session arguments, environment variables, and isolation

### Forwarding arguments

In tox:

```text
commands = pytest {posargs}
```

Then:

```bash
tox -e py312 -- tests/test_api.py -k pagination -vv
```

In Nox:

```python
session.run("pytest", *session.posargs)
```

Then:

```bash
nox -s tests-3.12 -- tests/test_api.py -k pagination -vv
```

Arguments are useful for narrowing a failed test, running a marker, or passing a pytest option. Make sure the command actually consumes the forwarded arguments.

### Environment variables

Environment variables often influence tests through locale, time zone, credentials, feature flags, or backend selection. Declare required variables explicitly and use safe test values. Do not leak production credentials into test sessions.

For example, a tox environment can set deterministic locale settings where those locales are available:

```ini
[testenv]
set_env =
    PYTHONUTF8 = 1
    TZ = UTC
```

`TZ` support and the installed locale database vary by platform. A Windows environment does not necessarily behave like Linux for every environment variable. Avoid relying on a variable that the platform or runtime does not honor. Prefer tests that set their required context explicitly.

In Nox:

```python
@nox.session(python="3.13")
def tests_utc(session: nox.Session) -> None:
    session.install("-e", ".[test]")
    session.run(
        "pytest",
        env={"TZ": "UTC", "PYTHONUTF8": "1"},
        *session.posargs,
    )
```

The `env` mapping is an environment override for the command; consult your Nox version for whether values replace or augment the inherited environment and use the documented behavior. Keep test configuration explicit so that local and CI runs can be compared.

Nox also provides a `--no-install` command-line option that skips calls to `session.install()` for a run. It is useful only when the selected session's required tools and package are already available in the environment; for example, a tool-only session can use it when a separate bootstrap step has installed Ruff. It is not a substitute for declaring dependencies in the normal reproducible session, and a session that relies on `session.install("ruff")` will not work with `--no-install` unless Ruff is provisioned by another explicit mechanism.

### Isolation is not the same as hermeticity

A virtual environment isolates Python packages, but does not isolate all system libraries, network state, databases, file permissions, clocks, or environment variables. If a test depends on PostgreSQL, OpenSSL behavior, or another system service, provision and version that dependency separately or use a controlled service/container. Record the system requirements.

---

## 7. Using `uv` and `tox-uv`

`uv` is a fast Python package and environment tool. It can install interpreters, create environments, resolve dependencies, and run commands. `tox-uv` is a tox plugin/backend integration intended to use uv for selected tox operations. It is not required to use tox or Nox.

Examples of common workflows:

```bash
uv python install 3.12 3.13 3.14
uv run --python 3.12 pytest
uv run --python 3.13 pytest
uv add --dev pytest pytest-cov tox nox
```

These commands assume a uv release that supports the relevant command and the Python versions are available for the current platform. Check `uv --version` and `uv help` when commands differ. `uv run --python 3.12` selects an interpreter for that invocation; it does not automatically execute every matrix combination.

### Dependency groups versus extras

Use a development dependency group for tools needed by contributors (test runner, formatter, type checker) if your package metadata and installer support it. Use published extras for optional runtime integrations that downstream users install, such as `ledger[pandas]`.

Do not conflate:

- **runtime dependencies**: needed by ordinary imports/use;
- **optional extras**: feature-specific dependencies exposed to package consumers;
- **development dependencies**: tools needed to develop, test, document, or release the project;
- **locked environment dependencies**: exact resolution chosen for a reproducible application or CI job.

`uv`'s project workflow and `uv pip` workflow have different dependency-management semantics. Pick the interface that fits the project and consult its version-specific documentation.

### When to use `tox-uv`

Use it when the team wants tox's environment/session model but uv's environment creation or installation behavior. Pin tox and the plugin in the tool bootstrap environment, then run a smoke test of the actual sessions. Do not assume installing the plugin automatically changes every package installation path, or that every tox configuration option has identical semantics under every backend.

---

## 8. Matrix dimensions and test strategy

A conceptual matrix might be:

| Job family | Python | Dependencies | OS | Frequency |
|---|---|---|---|---|
| Fast tests | 3.12, 3.13, 3.14 | Locked/default | Main CI OS | Every change |
| Portability smoke | Key supported versions | Default | Linux, Windows, macOS | Every pull request or selected branches |
| Lower-bound check | Supported baseline | Lowest compatible direct deps | One or more key OSs | Pull request or scheduled |
| Latest-dependency check | Current supported Python | Latest compatible deps | Main CI OS | Scheduled or pull request |
| Optional integrations | Relevant Python | `pandas` or other extra | Selected OS | Targeted |
| Artifact install | Supported Python | Fresh resolution | Selected OSs | Release and regular CI |
| Free-threaded / experimental runtime | Compatible interpreter build | Compatible dependencies | Supported runner | Non-blocking until stable |
| Full extended matrix | Multiple dimensions | Selected combinations | All supported OSs | Nightly/release |

### The Cartesian-product problem

If there are 3 Python versions × 3 operating systems × 2 dependency resolutions × 3 extras, a full product contains \(3 \times 3 \times 2 \times 3 = 54\) combinations before adding artifact type or runtime mode. That can be too expensive for every commit.

Control matrix size using:

1. **Smoke tests everywhere**: import, package installation, and a small high-value test subset.
2. **Full tests on representative combinations**: include the oldest and newest supported Python, and platform-specific risks.
3. **Pairwise coverage**: choose combinations that cover pairs of dimensions when exhaustive testing is impractical.
4. **Scheduled jobs**: run slow compatibility and long-tail combinations nightly or weekly.
5. **Risk-based expansion**: add a combination when code or dependency changes affect it.
6. **Separate signal from noise**: experimental runtime jobs can be non-blocking while the project evaluates compatibility.

Do not describe a reduced matrix as exhaustive. Document what is tested on every change and what runs on a schedule.

---

## 9. Lowest direct dependency versions and declared lower bounds

The roadmap calls out `uv pip install --resolution lowest-direct` as a way to test lowest direct dependency versions. This is a useful strategy, but it must be applied to the actual project environment and verified against the selected uv version.

For example, in a fresh environment where the project and test tools have already been installed in a controlled way, a command of this form may be appropriate:

```bash
uv pip install --resolution lowest-direct -e ".[test]"
```

**Do not assume this single command always creates a valid lower-bound test.** It resolves the install request according to uv's resolution policy, but details depend on the current environment, what is already installed, optional extras, build requirements, and tool version. For a reliable lower-bound job:

1. Start from a fresh environment.
2. Use the intended interpreter.
3. Install the package and the dependencies being tested using the selected lowest-direct policy.
4. Inspect the resolved dependency versions (`uv pip freeze` or the appropriate environment inspection command).
5. Run tests and retain the resolution output as a CI artifact.
6. Test optional extras separately if their lower bounds matter.

For pip-based workflows, a constraints file pinning the minimum versions can be clearer for a small dependency set, but it needs maintenance and must include compatible transitive constraints. Never claim to test a lower bound unless the resolved versions demonstrate it.

### Latest-compatible dependencies

A “latest” run should resolve the latest versions allowed by the project's constraints, not blindly upgrade past declared upper bounds or install incompatible major versions. Run in a fresh environment without a stale lock file constraining the resolution, unless the purpose is specifically to test the lock.

### Pre-releases

Pre-release testing helps detect upcoming dependency or Python incompatibilities. Make it a deliberate, separate job, often scheduled and initially non-blocking. Enable pre-release resolution only for the packages and resolver behavior you intend to test, record the selected versions, and do not silently replace the stable-release matrix with pre-release dependencies.

### Lower bounds versus support policy

A metadata constraint is a compatibility promise. If your project declares `dependency >= 2.4`, a minimum-version test failing at 2.4 is evidence to investigate: either fix the code or raise the declared lower bound with an explicit compatibility decision. Do not merely pin CI to the newest release and ignore the promise.

---

## 10. Separate sessions for separate responsibilities

Independent sessions make failures easier to diagnose and allow different tools to have independent dependencies.

### Lint and formatting

Example commands:

```bash
ruff check .
ruff format --check .
```

A lint session should not need to install runtime dependencies unless the tool genuinely requires them. Keep it fast.

### Type checking

```bash
mypy src/ledger
```

Install type-checker plugins and third-party stubs required by the project. Type-checking source paths avoids relying solely on test imports, but the configuration still needs to reflect package imports and supported Python versions.

### Documentation

```bash
sphinx-build -W -b html docs build/html
```

The `-W` option promotes warnings to errors for the selected Sphinx invocation. This is useful for broken references, missing documents, and documentation drift. Make sure the docs environment installs all extensions used by the project.

### Packaging checks

```bash
python -m build
twine check --strict dist/*
```

`build` creates distribution artifacts according to project metadata and the configured build backend. `twine check` checks distribution metadata and README rendering, but it does not prove the package installs or works. Artifact installation is a separate test.

### Security checks

The roadmap identifies `pip-audit` and `bandit` as tools worth considering. Example:

```bash
pip-audit
bandit -r src/ledger
```

Use these as focused sessions, pin tools as appropriate, and define how findings are triaged. An audit result is not a guarantee of security; tool coverage and vulnerability databases have limitations. A security session may need network access, unlike an intentionally offline unit-test session.

### Performance regression checks

Use a dedicated session for benchmarks such as `pytest-benchmark`, with controlled hardware and stable baselines. A noisy shared CI runner can make strict wall-clock assertions flaky. Prefer benchmark history and thresholds designed for the execution environment. Keep performance results separate from functional correctness unless a very coarse guard protects against catastrophic regressions.

### Coverage and combining results

Coverage collected in multiple environments can be combined, but the data files must use compatible coverage versions/settings and be gathered into a single workspace. One common pattern is to use parallel coverage data, collect artifacts from matrix jobs, then run:

```bash
coverage combine
coverage report --fail-under=90
```

The exact artifact-download and directory layout is CI-specific. `coverage combine` cannot combine data files that were never transferred to the same workspace. Use compatible source paths and coverage configuration across jobs. Do not sum percentages or average percentages from independent jobs; combine the underlying data and calculate the total from that.

---

## 11. Testing the installed wheel and source distribution

A critical packaging failure occurs when tests import the working checkout instead of the artifact users will install. This can hide missing files, incorrect package discovery, and broken metadata.

### Build first, then install into a clean environment

For a manual smoke test:

```bash
python -m build
python -m venv /tmp/ledger-artifact-test
# Activate the environment using the platform-specific command.
python -m pip install dist/ledger-0.1.0-py3-none-any.whl
python -c "import ledger; print(ledger.__file__)"
```

The wheel filename shown is illustrative; inspect `dist/` for the actual artifact name. On Windows, use a Windows-compatible virtual-environment path and activation command. A fresh environment is important: do not install the wheel into an environment that already has `ledger` editable-installed.

For the sdist, build and install the `.tar.gz` artifact in another fresh environment. Installing an sdist invokes its build process, so build-system dependencies and compiler/system-library requirements can expose additional failures.

### Keep the source tree out of the import path

Run artifact tests from a directory outside the repository, and ensure `PYTHONPATH` does not point to `src/`. Confirm the import origin:

```bash
python -c "import ledger; print(ledger.__file__)"
```

Expected: the path should point inside the fresh environment's installed `site-packages` (or the platform's equivalent), not the repository's `src/ledger`.

A test runner launched from the repository can put the current directory on `sys.path`. For artifact tests, place test files in a separate temporary directory or configure the run so the checkout cannot shadow the installed package. Verify the actual import path rather than assuming isolation worked.

### Example Nox artifact session

The following sketch builds the wheel, creates a fresh environment, installs the wheel, and runs tests from a separate test directory. It needs adaptation to the project's build output and test packaging. It deliberately avoids `session.install("-e", ".[test]")`, which would install the checkout and defeat the artifact test.

```python
from pathlib import Path
import shutil
import tempfile

import nox


@nox.session(python="3.13")
def wheel_smoke(session: nox.Session) -> None:
    session.install("build", "pytest")
    session.run("python", "-m", "build", "--wheel")
    wheels = sorted(Path("dist").glob("*.whl"))
    if len(wheels) != 1:
        session.error(f"Expected exactly one wheel, found: {wheels}")
    session.install(str(wheels[0].resolve()))

    # Copy artifact tests outside the checkout so neither the repository root
    # nor src/ can shadow the installed distribution during import.
    test_source = Path("artifact-tests").resolve()
    if not test_source.is_dir():
        session.error("Create artifact-tests/ containing tests for the installed package.")
    with tempfile.TemporaryDirectory(prefix="ledger-wheel-smoke-") as temporary:
        run_dir = Path(temporary)
        test_dir = run_dir / "tests"
        shutil.copytree(test_source, test_dir)
        session.chdir(run_dir)
        session.run("pytest", str(test_dir), env={"PYTHONPATH": str(test_dir)})
```

This is a starting pattern, not a complete universal artifact harness. It copies the artifact tests to a temporary directory outside the checkout, changes the command working directory, and sets `PYTHONPATH` to the copied tests directory rather than the source tree. The strongest check is to assert or log `ledger.__file__` from inside the artifact test process and ensure it resolves inside the fresh environment's installed `site-packages`, not the checkout. Confirm the result on each supported platform because path and environment handling differ.

Do not use the same environment for wheel and sdist checks; separate fresh environments help identify which artifact is broken.

---

## 12. Optional extras and operating-system dependencies

Optional extras represent separate compatibility surfaces. If `ledger[pandas]` is supported, test it explicitly:

```bash
python -m pip install -e ".[test,pandas]"
pytest
```

This command is suitable for development tests, not an installed-wheel check. For an artifact test, install the built wheel with the requested extra (for example, `ledger[pandas]`) in a fresh environment, or install the wheel and optional dependency set using a carefully controlled process.

For a full extra, do not assume `all` is automatically defined. It must exist in `[project.optional-dependencies]`.

System-level dependencies such as `libpq`, OpenSSL, compilers, or database clients may be needed by native extensions or integration tests. A Python virtual environment does not install these. Use documented OS packages, containers, or service fixtures and pin their versions where reproducibility matters. Tools such as `tox-docker` may help with container-backed dependencies, but their configuration and compatibility should be checked against the selected tox version.

---

## 13. GitHub Actions: connect the matrix to sessions

The goal here is to configure the runner sessions that CI invokes, not to replace the separate CI curriculum. A minimal job can delegate test logic to Nox:

```yaml
strategy:
  fail-fast: false
  matrix:
    python: ["3.12", "3.13", "3.14"]

steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python }}
  - run: python -m pip install nox
  - run: nox -s tests-${{ matrix.python }}
```

This is an illustrative fragment rather than a complete workflow. The action versions, Python availability, runner operating systems, and Nox session names should be checked at implementation time. The `tests` session must exist and map to the selected Python version. If using a tox environment instead, the corresponding command might be `tox -e py313` for a fixed Python 3.13 job.

Avoid duplicating test commands in YAML and the session file. Define commands once in tox/Nox and let CI select the session. That makes a CI failure reproducible locally with the same command.

---

## 14. Free-threaded Python and experimental JIT

The roadmap calls out free-threaded builds (for example, a `3.14t` environment label) and experimental JIT as compatibility areas worth exploring in a non-blocking job.

These runtimes may have distinct availability, ABI, extension-module compatibility, and tooling constraints. Do not assume that `3.14t` is a universally valid tox environment name or that every dependency provides a compatible wheel. Configure a dedicated environment only after confirming the runner can install the intended interpreter and all required dependencies.

A responsible rollout:

1. Start with import and focused smoke tests.
2. Identify dependencies with native extensions and their free-threading support.
3. Make the job informational/non-blocking while the ecosystem or project support is experimental.
4. Record interpreter build, dependency versions, OS, and failures.
5. Promote it to a required check only after the project explicitly adopts that support target.

Similarly, experimental JIT behavior should be treated as an additional runtime dimension, not a replacement for the stable interpreter matrix. Verify the exact runtime flag or build mechanism for the selected Python release; do not copy a flag from another release without checking.

---

## 15. Lock files, caches, and reproducibility

A reproducible environment and a compatibility environment answer different questions.

### Lock files

- **Application or deployment tests:** a lock file can reproduce the selected dependency graph used in production.
- **Library compatibility tests:** a single lock file can prevent the job from exploring the dependency range users may install. Use a deliberate minimum/latest strategy in separate fresh environments.
- **Release build:** retain the build environment details and test the actual artifacts.

A lock file does not prove that your package's declared lower bounds are correct. Conversely, a lower-bound test is not necessarily a faithful reproduction of a deployment lock.

### Caches

Caches improve speed but can hide stale state if keys are too broad or environment contents are reused incorrectly. Include relevant dimensions in cache keys, such as OS, Python version, dependency lock/hash, and tool version. Avoid sharing writable virtual environments across incompatible matrix jobs.

Tox/Nox environment reuse is useful during local development. When diagnosing unexplained behavior, recreate the environment (`tox -r` or the appropriate Nox no-reuse option) before concluding that the configuration is correct.

### Reproducibility record

For important CI failures, capture:

- runner OS and architecture;
- exact Python and runner versions;
- tox/Nox/uv and plugin versions;
- dependency resolution output;
- selected session and command;
- relevant environment variables (redacting secrets);
- whether the environment was fresh or reused.

This turns “works on my machine” into a concrete comparison.

---

## 16. Local reproduction of CI failures

Start with the exact failing session, not the entire matrix:

```bash
tox -e py313
nox -s tests-3.13
```

Then narrow the test command:

```bash
tox -e py313 -- tests/test_core.py -q
nox -s tests-3.13 -- tests/test_core.py -q
```

If the failure appears only in CI:

1. Compare the interpreter patch version, OS, architecture, and installed system packages.
2. Compare the resolved dependency versions, not just `pyproject.toml`.
3. Recreate the environment from scratch.
4. Check environment variables, locale, time zone, path assumptions, filesystem permissions, and network access.
5. Confirm the imported module path.
6. Run the exact matrix dimension that failed before widening the investigation.

If a failure only occurs with the newest dependency, preserve the resolution and reduce the reproducer. If it only occurs on Windows/macOS, inspect platform-specific assumptions rather than forcing the test to skip without explanation.

---

## 17. Common failure modes and fixes

| Failure | Likely cause | Better response |
|---|---|---|
| `py314` cannot be created | Python 3.14 interpreter unavailable or unsupported by runner/tool | Provision the interpreter explicitly; verify support and runner availability |
| Test passes locally but fails in tox/Nox | Hidden global dependency or environment variable | Reproduce in a fresh session and declare dependencies explicitly |
| Minimum-version job uses latest packages | Resolver/environment was not actually reset or minimum policy was not applied | Use a fresh environment, inspect resolved versions, retain the resolution log |
| Optional feature fails only for users | Extra not tested or not declared correctly | Test the extra as a distinct compatibility surface |
| Tests pass from checkout but wheel is broken | Source tree shadows the installed artifact or files are missing from distribution | Test the wheel in a fresh environment outside the checkout and inspect `module.__file__` |
| Huge CI bill or slow feedback | Cartesian-product matrix too large | Use smoke/full/nightly tiers and risk-based dimensions |
| Coverage is lower after combining jobs | Data files not transferred or source paths/config differ | Combine raw coverage data in one workspace with compatible settings |
| Lint session installs the whole application unnecessarily | Session responsibilities are coupled | Use a tool-only environment where possible |
| Cache causes mysterious stale behavior | Cache key omits a compatibility dimension or environment reuse is masking changes | Include OS/Python/lock/tool hashes; recreate the environment |
| `twine check` passes but install fails | Metadata validation is not an installation/runtime test | Add fresh-environment wheel and sdist install tests |
| System-library import fails in clean CI | Python venv lacks an OS dependency | Provision and document the system package/container explicitly |
| Free-threaded job fails before tests run | Dependency/toolchain lacks compatible support | Keep a dedicated informational job; identify incompatible dependency/build requirements |

---

## 18. Hands-on exercises

1. **Basic tox matrix:** Create `py312`, `py313`, and `py314` test environments. Run one environment and forward a single test path plus `-q`. Record which interpreters were available.
2. **Nox sessions:** Write `tests`, `lint`, `typecheck`, and `build_check` sessions. Confirm each session can be invoked independently and that session arguments reach pytest.
3. **Lowest bounds:** Choose one direct runtime dependency. Run the minimum-resolution job in a fresh environment, capture resolved versions, and demonstrate that the installed version actually matches the intended lower-bound strategy.
4. **Latest dependencies:** Run a separate fresh latest-compatible resolution. Compare results with the minimum run and fix or explain any incompatibility.
5. **Optional extra:** Add a `pandas` extra and test base versus extra installation. Confirm the base package still imports without the optional dependency.
6. **Artifact test:** Build wheel and sdist. Install each in a fresh environment and run a smoke test outside the checkout. Assert that `ledger.__file__` points to the installed environment.
7. **Matrix budget:** Calculate the full Cartesian product for your project. Propose a fast per-PR matrix and a nightly matrix, and explain the risk covered by each.
8. **CI reproduction:** Simulate a failed CI session locally. Record the interpreter, dependency resolution, session command, and import path in a short incident note.

---

## 19. Self-check with model answers

### 1. Why test the installed wheel instead of the working directory?

Because the working tree can make imports succeed even when the wheel is missing modules or has incorrect package discovery/metadata. A fresh environment outside the checkout verifies what users will install. Check the module's `__file__` to ensure it came from the installed environment, not `src/`.

### 2. Write a `noxfile.py` with test, lint, type-check and build-check sessions.

A valid design defines independent session functions:

- `tests`: select supported Python versions, install the package and test dependencies, run pytest, and forward `session.posargs`;
- `lint`: install Ruff and run lint/format checks without installing the package if not required;
- `typecheck`: install mypy and required stubs, then check `src/ledger`;
- `build_check`: install `build` and `twine`, run `python -m build`, then `twine check --strict dist/*`.

The example in Section 5 provides a complete starting point. Check the generated session names with `nox --list`.

### 3. How do you verify that your declared `>=` lower bounds actually work?

Create a fresh environment for the intended interpreter, install the package and test dependencies using a deliberate lowest-direct dependency resolution strategy or maintained minimum constraints, inspect and save the resolved versions, and run tests. Confirm the minimum versions were actually selected. If the tests fail, either fix compatibility or reconsider the declared lower bound; do not quietly run only against latest dependencies.

---

## 20. Production checklist

- [ ] `requires-python` and dependency constraints reflect the actual support policy.
- [ ] Test environments cover supported Python versions, including 3.12, 3.13, and 3.14 where the project claims support and interpreters are available.
- [ ] tox/Nox and plugins are pinned or constrained to a tested toolchain.
- [ ] Session commands are centralized and can be reproduced locally.
- [ ] Arguments are forwarded correctly; environment variables are explicit and secrets are not leaked.
- [ ] Minimum and latest-compatible dependency jobs use fresh environments and verify resolved versions.
- [ ] Optional extras have explicit coverage.
- [ ] Lint, type, docs, package, security, performance, and coverage jobs have clear responsibilities.
- [ ] Wheel and sdist installation tests run in fresh environments outside the source tree.
- [ ] Coverage is combined from raw data, not by averaging percentages.
- [ ] Caches include the dimensions that affect environment compatibility.
- [ ] Experimental free-threaded/JIT jobs are labeled accurately and do not silently redefine stable support.
- [ ] Matrix size is controlled through risk-based smoke/full/nightly tiers.
- [ ] System-library requirements and local CI reproduction steps are documented.

## Final principle

A matrix is only as trustworthy as the combinations it actually exercises and the evidence it retains. Keep the session definitions reproducible, verify dependency resolutions, test the artifacts users receive, and make every compatibility claim match the jobs you run.
