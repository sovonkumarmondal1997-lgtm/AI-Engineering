# Python Namespace Packages and Monorepos

> **Audience:** Python developers progressing from packaging fundamentals to platform and library architecture.  
> **Running example:** an organization named `acme` publishes separately installable `acme-core`, `acme-ml`, and `acme-etl` distributions.  
> **Baseline:** Python 3.12+, `uv` workspaces, `hatchling` for builds, and pytest for tests. Backend behavior is identified where it is backend-specific.

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Explain PEP 420 implicit namespace packages and distinguish them from regular packages.
- Design multiple distributions that contribute `acme.core`, `acme.ml`, and `acme.etl` without conflicting over the `acme` root.
- Configure package discovery for namespace layouts and diagnose why a checkout import can differ from an installed-wheel import.
- Use a `uv` workspace to manage several packages with one lockfile while preserving package-specific metadata and release responsibilities.
- Test members individually and together, enforce dependency direction, and choose independent or lockstep versioning deliberately.
- Plan migrations, compatibility constraints, builds, and releases for a multi-package repository.

### Prerequisites

You should already understand `pyproject.toml`, `src/` layouts, build frontends/backends, wheels and sdists, dependency declarations and lockfiles, Git branches/tags, Python imports, pytest, and public API compatibility. The module roadmap places this lesson after package building, entry points, publishing, trusted publishing, and release automation.

## 2. Namespace-package mental model

A **distribution** is an installable artifact managed by packaging tools (for example, `acme-core-1.4.0.whl`). An **import package** is a name Python resolves at runtime (for example, `acme.core`). They are related by build configuration, not by a required naming convention.

| Distribution name | Import names it can provide |
|---|---|
| `acme-core` | `acme.core` |
| `acme-ml` | `acme.ml` |
| `acme-etl` | `acme.etl` |

A namespace package lets multiple independently installed distributions contribute portions of the same top-level import namespace. It is useful when teams need separately versioned libraries, optional integrations, or different release cadences while preserving a coherent import prefix.

```text
Applications
    |
    +-- import acme.core       <- distribution acme-core
    +-- import acme.ml         <- distribution acme-ml
    +-- import acme.etl        <- distribution acme-etl

Installed environment / site-packages
    acme/                      <- namespace package; no root __init__.py
      core/                    <- provided by acme-core
      ml/                      <- provided by acme-ml
      etl/                     <- provided by acme-etl
```

The packages do not need to be installed from the same index, directory, or repository. They must, however, follow compatible namespace conventions and avoid colliding over the same concrete module paths.

### What PEP 420 does

PEP 420 defines **implicit namespace packages**. When the import system searches path entries for a name such as `acme`, it can collect namespace-package portions from multiple locations if it does not find a regular package or module that wins resolution. The namespace package has no `__init__.py` executed at the root and its `__path__` can represent portions from multiple locations.

A namespace package is not merely a folder without `__init__.py`: the import system must be able to find it on the applicable import path. A folder in an uninstalled source tree is not automatically importable from every working directory.

## 3. Regular packages versus implicit namespace packages

### Regular package

```text
src/
  acme/
    __init__.py
    core/
      __init__.py
```

`acme/__init__.py` makes `acme` a regular package. It can execute initialization code and define attributes, but it also means the root is supplied as one concrete package. If multiple distributions each ship their own `acme/__init__.py`, whichever package path is selected can prevent the expected namespace composition. Legacy namespace mechanisms exist, but this lesson uses PEP 420 implicit namespaces.

### Implicit namespace package

```text
src/
  acme/              # intentionally no __init__.py here
    core/
      __init__.py
```

The child package `acme.core` is a regular package; the shared parent `acme` is implicit. Each distribution can ship its own child subtree. Do **not** add `src/acme/__init__.py` to one of these distributions unless you deliberately intend to change the architecture and have validated all consumers.

The phrase “adding `__init__.py` breaks the namespace” is a useful warning, but the exact outcome depends on what other packages and path entries are present. A regular `acme` package can shadow namespace portions located elsewhere; it does not mean every possible installation fails in exactly the same way.

### How resolution works

At a high level, Python's import machinery consults `sys.meta_path` finders, including the standard path-based finder. The path-based finder searches entries in `sys.path` (and a package's `__path__` for submodules). For a top-level name, it can find a concrete module/package or collect namespace portions from path entries. The namespace package's path can be recomputed as import paths change. Avoid depending on private import internals; inspect behavior through `acme.__spec__`, `acme.__path__`, and imports in a clean environment.

```python
import acme

print(acme.__spec__)       # typically identifies a namespace package loader as None
print(list(acme.__path__)) # locations contributing namespace portions
```

Exact representation of `ModuleSpec` fields can vary by Python version and import context; use this as diagnostic output, not as a brittle assertion against a hard-coded string.

## 4. Complete multi-distribution example

The example has three independently buildable distributions. Each package owns a distinct subpackage, and no distribution includes `acme/__init__.py`.

```text
acme-platform/
├── packages/
│   ├── acme-core/
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   ├── src/acme/core/__init__.py
│   │   ├── src/acme/core/math.py
│   │   └── tests/test_math.py
│   ├── acme-ml/
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   ├── src/acme/ml/__init__.py
│   │   ├── src/acme/ml/features.py
│   │   └── tests/test_features.py
│   └── acme-etl/
│       ├── pyproject.toml
│       ├── README.md
│       ├── src/acme/etl/__init__.py
│       ├── src/acme/etl/pipeline.py
│       └── tests/test_pipeline.py
├── pyproject.toml
├── uv.lock
├── .python-version
├── pyproject.toml               # root is shown below; one root file only
├── README.md
└── .gitignore
```

The complete layout has one root `pyproject.toml` and one in each distribution:

```text
acme-platform/
├── pyproject.toml
├── uv.lock
├── .python-version
├── README.md
└── packages/
    ├── acme-core/
    │   ├── pyproject.toml
    │   ├── README.md
    │   ├── src/acme/core/__init__.py
    │   ├── src/acme/core/math.py
    │   └── tests/test_math.py
    ├── acme-ml/
    │   ├── pyproject.toml
    │   ├── README.md
    │   ├── src/acme/ml/__init__.py
    │   ├── src/acme/ml/features.py
    │   └── tests/test_features.py
    └── acme-etl/
        ├── pyproject.toml
        ├── README.md
        ├── src/acme/etl/__init__.py
        ├── src/acme/etl/pipeline.py
        └── tests/test_pipeline.py
```

### `acme-core`

`packages/acme-core/pyproject.toml`:

```toml
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[project]
name = "acme-core"
version = "1.4.0"
description = "Shared core utilities for Acme projects"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"

[tool.hatch.build.targets.wheel]
only-include = ["src/acme/core"]
sources = ["src"]

[tool.hatch.build.targets.sdist]
only-include = ["pyproject.toml", "README.md", "src/acme/core", "tests"]
```

`packages/acme-core/src/acme/core/__init__.py`:

```python
"""Public API for acme-core."""
from .math import add

__all__ = ["add"]
```

`packages/acme-core/src/acme/core/math.py`:

```python
def add(left: int, right: int) -> int:
    """Return the sum of two integers."""
    return left + right
```

Notice the `only-include` path: the wheel contains `acme/core`, not an `acme/__init__.py`. Hatchling configuration is backend-specific; verify the built wheel contents when changing backend or version. The sdist includes the files needed to rebuild the package and its tests.

### `acme-ml`

`packages/acme-ml/pyproject.toml`:

```toml
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[project]
name = "acme-ml"
version = "0.8.0"
description = "Machine-learning utilities for Acme projects"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
dependencies = ["acme-core>=1.4,<2"]

[tool.hatch.build.targets.wheel]
only-include = ["src/acme/ml"]
sources = ["src"]

[tool.hatch.build.targets.sdist]
only-include = ["pyproject.toml", "README.md", "src/acme/ml", "tests"]
```

`packages/acme-ml/src/acme/ml/__init__.py`:

```python
"""Public API for acme-ml."""
from .features import feature_names

__all__ = ["feature_names"]
```

`packages/acme-ml/src/acme/ml/features.py`:

```python
from acme.core import add


def feature_names() -> list[str]:
    """Return a demonstration feature list."""
    return [f"feature_{add(1, 1)}"]
```

### `acme-etl`

`packages/acme-etl/pyproject.toml`:

```toml
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[project]
name = "acme-etl"
version = "0.5.0"
description = "ETL utilities for Acme projects"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
dependencies = ["acme-core>=1.4,<2"]

[tool.hatch.build.targets.wheel]
only-include = ["src/acme/etl"]
sources = ["src"]

[tool.hatch.build.targets.sdist]
only-include = ["pyproject.toml", "README.md", "src/acme/etl", "tests"]
```

`packages/acme-etl/src/acme/etl/__init__.py`:

```python
"""Public API for acme-etl."""
from .pipeline import run_pipeline

__all__ = ["run_pipeline"]
```

`packages/acme-etl/src/acme/etl/pipeline.py`:

```python
from acme.core import add


def run_pipeline() -> int:
    """Return a tiny demonstration pipeline result."""
    return add(20, 22)
```

The example dependencies intentionally point one-way from higher-level packages to `acme-core`. The published dependency constraint `acme-core>=1.4,<2` is the consumer-facing compatibility promise. Workspace source overrides used during development do not replace the need for correct, publishable metadata.

## 5. Monorepo and workspace architecture

A **monorepo** stores multiple projects in one repository. A **workspace** is a tool-level model that coordinates some of those projects. They are related but not synonymous: a monorepo can have no formal workspace, and workspaces can be used in different repository arrangements.

Reasons to use a monorepo:

- Atomic changes across related packages.
- Shared lint, type-checking, test, documentation, and security policy.
- One place to review dependency changes and architecture boundaries.
- Shared CI and release orchestration.

Costs include larger CI graphs, ownership coordination, accidental coupling, and more complicated releases. Use separate repositories when access control, release independence, incompatible toolchains, or organizational ownership outweigh atomic-change benefits.

### Root workspace `pyproject.toml`

The root is the workspace root and is also a workspace member, but it need not be an installable distribution. This example treats it as a **virtual project**: `tool.uv.package = false` tells uv to install its dependency groups without trying to build/install a root Python package. The three child distributions remain independently buildable packages.

```toml
[project]
name = "acme-platform-dev"
version = "0.1.0"
description = "Development environment for the Acme package workspace"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = [
  "pytest>=8.0",
  "ruff>=0.6",
  "mypy>=1.11",
  "import-linter>=2.0",
]

[tool.uv]
package = false

[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
acme-core = { workspace = true }
acme-ml = { workspace = true }
acme-etl = { workspace = true }

[tool.pytest.ini_options]
testpaths = ["packages"]
python_files = ["test_*.py"]

[tool.ruff]
line-length = 100
```

The root is a virtual workspace member too; `packages/*` includes the three package projects. uv uses a shared `uv.lock` for the workspace and workspace-member dependencies are installed editable during normal sync. `tool.uv.sources` maps dependency names to workspace members. The metadata in each member's `[project].dependencies` still describes what a published consumer needs; workspace source settings are development overrides and should not be treated as published requirements. Because the root has `package = false`, its project metadata and dependency groups do not imply that a root wheel will be built or published.

A workspace uses one dependency resolution and a shared lockfile. It does **not** mean every package has one shared version, nor does it isolate every package's dependencies from every other package. uv documents that workspace members share a single `requires-python` intersection, so packages with incompatible Python support needs may be better managed separately.

### Workspace commands

From the repository root:

```bash
uv lock                         # resolve/update shared uv.lock
uv sync --all-packages          # install all workspace members and dev tools
uv run --all-packages pytest    # run tests in the synced workspace environment
uv run --all-packages pytest packages/acme-core/tests
uv run --all-packages pytest packages/acme-ml/tests
uv run --all-packages pytest packages/acme-etl/tests
uv run --all-packages ruff check packages
```

Exact CLI behavior evolves with uv; check the installed version's `uv --help` and official workspace documentation if a command differs. `--all-packages` ensures all workspace members are included in the workspace environment; the commands above retain the root development dependency group (including pytest). A package-specific `uv run --package NAME ...` is useful when you deliberately want that member's project context, but ensure test tools are declared in the selected member or otherwise available in the environment. Do not assume the workspace's editable install is equivalent to testing built distributions.

### Package boundaries and dependency direction

A sensible dependency graph is:

```text
            acme-core
             /     \
            v       v
        acme-ml   acme-etl
```

More precisely, arrows here mean “depends on”: `acme-ml -> acme-core` and `acme-etl -> acme-core`. `acme-core` must not import either higher-level package. If it does, the architecture becomes cyclic and the lower-level library cannot be reused independently.

Use design rules such as:

- `core` contains stable primitives and avoids application-specific dependencies.
- `ml` and `etl` depend on `core`, not on each other unless the dependency is explicit and justified.
- Public APIs are documented and exported intentionally (`__all__` is a signal, not a security boundary).
- Internal modules are not imported by downstream packages unless explicitly supported.
- CODEOWNERS and required reviews align ownership with package boundaries.

## 6. Package discovery and build configuration

Package discovery is the mapping from source files to files included in the wheel and sdist. Namespace layouts need explicit attention because the shared root lacks `__init__.py`.

### Hatchling

The example uses `only-include` and `sources` so each distribution includes its own subtree. Backend configuration differs between projects; do not copy configuration from one backend to another without checking its docs. Validate the artifact rather than inferring contents from a successful build:

```bash
cd packages/acme-core
uv build
python -m zipfile -l dist/acme_core-1.4.0-py3-none-any.whl
```

Wheel filenames normalize punctuation in distribution names, so `acme-core` commonly appears as `acme_core` in artifact filenames. The wheel should contain `acme/core/...` and must not contain `acme/__init__.py`.

For setuptools, configure namespace-aware discovery, for example:

```toml
[tool.setuptools.packages.find]
where = ["src"]
namespaces = true
```

This is an alternative backend configuration, not an extra block to add to the Hatchling project. Confirm setuptools' package-discovery behavior for the backend version in use.

### Why one stray root file matters

If one distribution includes `acme/__init__.py`, that distribution may cause `acme` to resolve as a regular package, shadowing namespace portions elsewhere on `sys.path`. This can manifest as a missing `acme.ml` even though `acme-ml` is installed. Inspect wheel contents and test combinations of distributions rather than only importing from the checkout.

### Editable installs versus wheels

Editable installs are excellent for development, but they can expose source directories and conceal missing wheel files or incorrect discovery rules. Built wheels test what consumers actually receive. Test both:

1. Workspace tests for fast feedback.
2. Build every member.
3. Install selected wheels into a clean environment outside the repository.
4. Run imports and behavioral smoke tests from a different working directory.

## 7. Testing and debugging installation behavior

### Basic unit tests

`packages/acme-core/tests/test_math.py`:

```python
from acme.core import add


def test_add() -> None:
    assert add(2, 3) == 5
```

`packages/acme-ml/tests/test_features.py`:

```python
from acme.ml import feature_names


def test_feature_names_uses_core() -> None:
    assert feature_names() == ["feature_2"]
```

`packages/acme-etl/tests/test_pipeline.py`:

```python
from acme.etl import run_pipeline


def test_pipeline() -> None:
    assert run_pipeline() == 42
```

Run member-specific tests and the integrated suite. Unit tests should not require all unrelated members unless that dependency is intentional.

### Clean environment test using wheels

Build artifacts in each package directory, then install all three wheel files into a temporary environment. Commands below are intended to be run from the repository root in a shell that supports the shown syntax; adjust wheel paths if your backend emits different normalized filenames.

```bash
uv build --package acme-core
uv build --package acme-ml
uv build --package acme-etl
```

If your installed uv version does not support building a workspace member via `--package`, build from each member directory instead:

```bash
(cd packages/acme-core && uv build)
(cd packages/acme-ml && uv build)
(cd packages/acme-etl && uv build)
```

Create a temporary venv outside the repository so the current directory cannot provide imports:

```bash
python -m venv /tmp/acme-wheel-test
# POSIX activation; on Windows use /tmp/acme-wheel-test/Scripts/activate
. /tmp/acme-wheel-test/bin/activate
python -m pip install --upgrade pip
python -m pip install \
  packages/acme-core/dist/acme_core-1.4.0-py3-none-any.whl \
  packages/acme-ml/dist/acme_ml-0.8.0-py3-none-any.whl \
  packages/acme-etl/dist/acme_etl-0.5.0-py3-none-any.whl
cd /tmp
python -c "import acme.core, acme.ml, acme.etl; print(acme.core.add(20, 22))"
python -c "from acme.etl import run_pipeline; assert run_pipeline() == 42"
```

The filenames above assume the exact versions and a pure-Python `py3-none-any` wheel. If build output differs, install the actual files under `dist/`; do not rename artifacts manually. The install may resolve `acme-core` from the local wheel arguments, satisfying the `acme-core>=1.4,<2` requirement. This is a local smoke test, not a complete test of every platform or dependency resolver.

On Windows, use a fresh path under `%TEMP%` and invoke its interpreter directly from PowerShell, for example:

```powershell
$venv = Join-Path $env:TEMP "acme-wheel-test-unique"
python -m venv $venv
& "$venv\Scripts\python.exe" -m pip install --upgrade pip
& "$venv\Scripts\python.exe" -m pip install `
  packages/acme-core/dist/acme_core-1.4.0-py3-none-any.whl `
  packages/acme-ml/dist/acme_ml-0.8.0-py3-none-any.whl `
  packages/acme-etl/dist/acme_etl-0.5.0-py3-none-any.whl
Push-Location $env:TEMP
& "$venv\Scripts\python.exe" -c "import acme.core, acme.ml, acme.etl; print(acme.core.add(20, 22))"
& "$venv\Scripts\python.exe" -c "from acme.etl import run_pipeline; assert run_pipeline() == 42"
Pop-Location
```

Choose a path that does not already contain an environment; recreate it if you need to guarantee a clean install. For reproducible automation, use a temporary-directory mechanism appropriate to the CI operating system rather than hard-coding `/tmp`.

### Diagnose the “works from checkout, fails after install” problem

Use this sequence:

1. **Check current directory:** Python prepends the script/current directory to import search paths in common invocation modes. Run the test from outside the repo.
2. **Check import origin:** print `acme.__path__`, `acme.core.__file__`, and `acme.ml.__file__` to confirm which locations were imported.
3. **Inspect wheel contents:** confirm `acme/core` and `acme/ml` exist in the corresponding wheels and no distribution accidentally ships the namespace root `acme/__init__.py`.
4. **Check installation metadata:** `python -m pip show acme-core acme-ml` and `python -m pip list`.
5. **Check version constraints:** the installed `acme-core` must satisfy the dependency range declared by `acme-ml` and `acme-etl`.
6. **Check shadowing:** look for a local `acme.py`, another `acme` regular package, duplicate distributions, or an unexpected `PYTHONPATH`.
7. **Rebuild from clean source:** remove stale `dist/` artifacts and inspect the newly generated wheels.

Do not “fix” namespace behavior by randomly adding `__init__.py` at the root. First determine whether you intend a namespace package or one regular package distributed as a unit.

## 8. Dependency boundaries, versioning, and release responsibility

### Published constraints versus workspace sources

A package's `[project].dependencies` must be meaningful outside the repository. For example:

```toml
dependencies = ["acme-core>=1.4,<2"]
```

means consumers can resolve a compatible published `acme-core` release within that range. In the workspace, `tool.uv.sources` can redirect the same dependency to the local member for development. Verify both modes:

- **Workspace mode:** does the integrated source tree work with all member edits?
- **Published mode:** can the package install from built artifacts using only declared metadata and a package index or local wheelhouse?

Do not publish a dependency on an unpublished package version. Release dependency packages before packages that require them, or coordinate a release train with explicit compatible constraints.

### Independent versioning

Example versions: `acme-core 1.4.0`, `acme-ml 0.8.0`, `acme-etl 0.5.0`. Each package bumps when its own public API or behavior changes. This is useful when teams release independently, but requires automation to understand the dependency graph and compatibility constraints.

### Lockstep versioning

All members share a version such as `2.3.0`. This simplifies coordinated releases and support matrices but can force unrelated packages to release together. Lockstep is not automatically enforced by a workspace: CI/release tooling must implement it.

### Test packages individually and as a system

A release matrix should include:

- Unit tests per member.
- Integrated tests for supported combinations of packages.
- Lower and upper supported dependency bounds where practical.
- Wheel and sdist build checks per member.
- Clean-environment installation tests.
- Public API/compatibility checks for packages with downstream consumers.
- Dependency graph validation and cycle detection.

## 9. Advanced architectural trade-offs

### Monorepo versus polyrepo versus one distribution

| Choice | Best fit | Costs and risks |
|---|---|---|
| One distribution | Components almost always release together and are consumed together | Harder to keep optional dependencies and ownership boundaries clean; consumers install more code |
| Monorepo, multiple distributions | Related packages need atomic changes and shared tooling, but independent releases | CI complexity, workspace-wide Python constraints, accidental coupling, coordinated release logic |
| Multiple repositories | Different access controls, teams, release cadences, or toolchains | Cross-repository changes require coordination; integration testing and dependency updates are harder |

A namespace package is an import architecture, not a requirement to use a monorepo. The same `acme.*` namespace can be supplied by distributions developed in separate repositories. Conversely, a monorepo can contain packages that do not share a namespace.

### Shared tooling and ownership

Keep common lint/test settings at the root, but allow package-specific settings where they express real needs. Use CODEOWNERS and branch protection to require the appropriate review for package-specific changes. Keep each package's README, metadata, tests, changelog policy, release version, and owner discoverable.

### Migration from one package to multiple distributions

A gradual “strangler” migration can preserve old imports while new distributions take over responsibilities:

1. Inventory public imports and dependencies; draw the target dependency graph.
2. Define which package owns each module and which APIs are public.
3. Move a subtree while preserving import paths where feasible, or introduce a compatibility shim that re-exports from the new package.
4. Add deprecation warnings for old paths and publish a migration guide.
5. Test old and new installations in clean environments, including combinations of distributions.
6. Publish the foundational package first, then consumers with compatible dependency constraints.
7. Remove shims only after the announced deprecation window and compatibility policy allow it.

### Namespace collisions and operational edge cases

- **Name collisions:** two distributions may both provide `acme.core`; avoid overlapping ownership. Python does not merge two different files with the same import name into a meaningful combined API.
- **Shadowing:** a regular `acme` package or local module may take precedence over namespace portions.
- **Duplicate installations/indexes:** installing similarly named distributions from different sources can create confusing or unsafe environments. Use one trusted index strategy and inspect installed metadata.
- **Partial uninstall:** namespace directories may remain because another distribution still owns files in that tree. Inspect the installed files rather than deleting directories manually.
- **Zip/frozen applications:** importers and bundlers may handle namespace packages differently. Test the actual packaging method if using zipapps or freezing tools.
- **Type checking and IDEs:** configure namespace-package support for the chosen checker, and verify package roots; do not assume runtime discovery rules and static-analysis configuration are identical.

### Enforcing boundaries with `import-linter`

Install the tool in the development group and configure a forbidden dependency contract. For this example, the contract forbids the lower-level `acme.core` package from importing the higher-level `acme.ml` package.

Add this to the root `pyproject.toml`:

```toml
[tool.importlinter]
root_package = "acme"
include_external_packages = true

[[tool.importlinter.contracts]]
name = "Core must not depend on ML"
type = "forbidden"
source_modules = ["acme.core"]
forbidden_modules = ["acme.ml"]
```

Then run it from the root after syncing the workspace:

```bash
uv sync --all-packages
uv run lint-imports
```

`import-linter` configuration and command behavior should be checked against the installed version's documentation. The contract checks import relationships visible to the tool; it is not a sandbox and cannot prevent dynamic imports or all runtime coupling. Add architecture tests and code review for critical boundaries.

## 10. Hands-on workspace lab

### Goal

Create a two-package namespace workspace (`acme-core` and `acme-ml`), verify imports in a clean environment, and prevent `acme.core` from importing `acme.ml`.

### Steps

1. Create the root workspace and the two package directories shown above. You may omit `acme-etl` for this lab.
2. Ensure `src/acme/` has **no** `__init__.py` in either distribution.
3. Add `__init__.py` only to `src/acme/core/` and `src/acme/ml/`.
4. Add the package metadata and Hatchling include rules; declare `acme-ml`'s dependency as `acme-core>=1.4,<2`.
5. Configure `[tool.uv.workspace] members = ["packages/*"]` and `tool.uv.sources` for `acme-core`.
6. Add unit tests and the import-linter contract.
7. Run `uv lock`, `uv sync --all-packages`, package-specific tests, and `uv run lint-imports`.
8. Build both distributions. Inspect each wheel to ensure it contains only its owned subtree and no `acme/__init__.py`.
9. Install both wheel files into a fresh virtual environment outside the repository. Run `import acme.core, acme.ml` and a behavioral assertion from a directory outside the checkout.
10. Intentionally add `src/acme/__init__.py` to one distribution, rebuild, and observe whether the other namespace portion is still discoverable in your installed environment. Revert the file and document the finding.

### Acceptance criteria

- Both distributions build from their own directories.
- `acme-core` and `acme-ml` have distinct distribution metadata but share the `acme` import namespace.
- The root namespace has no `__init__.py` in either wheel.
- A fresh environment installed from wheels imports both `acme.core` and `acme.ml` while the working directory is outside the repository.
- Tests pass individually and together.
- The import-linter contract rejects an introduced forbidden import from `acme.core` to `acme.ml`.
- You record the commands, Python/uv versions, wheel filenames, and observed import paths in the lab notes.

This document supplies a reproducible exercise, not evidence that the commands were run in your environment.

## 11. Troubleshooting quick reference

| Symptom | Likely cause | Diagnostic / fix |
|---|---|---|
| `ModuleNotFoundError: acme.ml` | `acme-ml` not installed, wrong wheel contents, shadowed `acme`, or bad package discovery | Inspect `pip show`, wheel listing, `acme.__path__`, and current directory |
| Works in repo but fails in clean venv | Checkout path or editable install concealed missing files | Build and install wheels outside repo |
| `acme` has unexpected `__file__` | A regular package is being imported | Inspect `acme.__spec__`, `acme.__path__`, and competing distributions |
| `acme-ml` cannot resolve `acme-core` | Dependency metadata absent or version range incompatible | Check `[project].dependencies` and installed versions |
| Workspace lock unexpectedly changes | Member metadata or sources changed | Review `uv.lock` diff; run `uv lock` deliberately and inspect dependency graph |
| Boundary check passes despite a runtime dependency | Dynamic import or configuration beyond static analysis | Add runtime tests, stricter architecture rules, and review |
| CI tests pass but release wheel fails | CI tests only exercised editable source | Make wheel installation/smoke tests a release gate |

## 12. Self-check questions with explained answers

### 1. What happens if one distribution ships `acme/__init__.py`?

It can turn `acme` into a regular package when that location is found, causing it to shadow namespace-package portions contributed by other distributions on different path entries. The exact behavior depends on `sys.path` ordering and what packages are installed, so diagnose the actual import resolution rather than assuming every installation fails identically. For a PEP 420 shared namespace, keep `acme/__init__.py` absent from every contributing distribution and verify built wheels.

### 2. Create a two-package namespace workspace and make `import acme.core, acme.ml` work from a clean venv.

Create `packages/acme-core` with `src/acme/core/__init__.py` and `packages/acme-ml` with `src/acme/ml/__init__.py`; omit `src/acme/__init__.py` in both. Give the distributions separate `pyproject.toml` files, declare `acme-ml`'s runtime dependency on `acme-core`, and configure the root uv workspace with `members = ["packages/*"]` plus a workspace source for `acme-core`. Run the workspace tests, build both wheels, and install the actual wheel paths into a new virtual environment located outside the repository. From a directory outside the checkout, run `python -c "import acme.core, acme.ml"`. If it fails, inspect wheel contents, installed distributions, `acme.__path__`, package discovery, and dependency constraints. The success criterion is the clean wheel-based import, not just an editable import from the checkout.

### 3. Write an `import-linter` contract that forbids `acme.core` from importing `acme.ml`.

Use this root configuration:

```toml
[tool.importlinter]
root_package = "acme"
include_external_packages = true

[[tool.importlinter.contracts]]
name = "Core must not depend on ML"
type = "forbidden"
source_modules = ["acme.core"]
forbidden_modules = ["acme.ml"]
```

Install `import-linter` in the development environment, then run `uv run lint-imports`. Verify that the contract passes with the intended dependency graph and fails when a module in `acme.core` imports a module from `acme.ml`. This is a static architecture guard; complement it with code review and tests because dynamic imports and runtime coupling may not be fully captured.

## 13. Final competency checklist

- [ ] I can explain PEP 420 and distinguish an implicit namespace from a regular package.
- [ ] I can explain why distribution names and import names differ.
- [ ] Each namespace contributor owns a distinct subtree and omits the namespace-root `__init__.py`.
- [ ] Each distribution has its own valid metadata, build configuration, tests, and release responsibility.
- [ ] I have inspected wheels rather than trusting only a successful source-tree import.
- [ ] I can configure and use a uv workspace and understand its shared lockfile and Python-version intersection.
- [ ] Published dependency ranges are valid outside the workspace.
- [ ] I test each member and the integrated package set.
- [ ] I can detect import cycles and enforce dependency direction with architecture checks.
- [ ] I can choose between a monorepo, polyrepo, and one distribution based on concrete trade-offs.
- [ ] I have a clean-environment installation test in CI and a documented recovery path for import failures.

## 14. Authoritative references

- PEP 420 — Implicit Namespace Packages: https://peps.python.org/pep-0420/
- Python import system: https://docs.python.org/3/reference/import.html
- Python Packaging User Guide — src layout vs flat layout: https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- uv workspaces: https://docs.astral.sh/uv/concepts/projects/workspaces/
- uv dependency sources: https://docs.astral.sh/uv/concepts/dependencies/
- uv locking and syncing: https://docs.astral.sh/uv/concepts/projects/sync/
- Hatchling documentation: https://hatch.pypa.io/latest/
- setuptools package discovery: https://setuptools.pypa.io/en/latest/userguide/package_discovery.html
- import-linter documentation: https://import-linter.readthedocs.io/
- pytest import mechanisms: https://docs.pytest.org/en/stable/explanation/pythonpath.html
