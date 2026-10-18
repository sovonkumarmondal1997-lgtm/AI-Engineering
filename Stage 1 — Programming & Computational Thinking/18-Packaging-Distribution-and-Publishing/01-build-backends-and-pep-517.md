# Build Backends and PEP 517

> **Stage 1 — Programming & Computational Thinking · Module 18 — Packaging, Distribution and Publishing**  
> Baseline: Python 3.12+, modern PyPA packaging standards, and current versions of the selected build tools. Tool versions and backend defaults evolve; verify exact options against the installed tool's documentation.

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Explain why Python packaging moved away from `setup.py`-only workflows.
- Distinguish packaging standards, build frontends, build backends, runtime dependencies, and build dependencies.
- Configure `pyproject.toml` using PEP 517, PEP 518, PEP 621, PEP 660, PEP 639, and PEP 735 concepts.
- Build and inspect both a source distribution (sdist) and a wheel for `tinytools`.
- Diagnose build isolation, missing-file, dynamic-metadata, native-toolchain, and editable-install problems.
- Choose a backend for pure Python, Rust, and C/C++ projects.
- Validate artifacts in a clean environment and explain the security and reproducibility implications of builds.

### Prerequisites

You should already be comfortable with Python modules and imports, a `src/` project layout, virtual environments, TOML, dependency specifiers, semantic versioning, README files, basic Git, and `pytest`. These concepts were introduced in Stage 1 Module 6 (project layout; `pyproject.toml`, lock files and `uv`; dependency management and semantic versioning; documentation) and Module 10 (release basics and supply-chain awareness). Module 16's installed-artifact testing is especially relevant.

You do not need to know compiler internals to learn the packaging model. Native builds are introduced as a separate case because they have additional operating-system dependencies.

## 2. Mental model: source code is not yet a distributable package

A repository is optimized for contributors. A distribution artifact is optimized for installation by another environment. They are not necessarily the same set of files.

- **Project source tree:** your checked-out files, configuration, tests, docs, and development tools.
- **Source distribution (sdist):** an archive of source and build metadata from which a wheel can normally be built. It is commonly a `.tar.gz` file.
- **Wheel:** a built distribution (`.whl`) with a defined archive layout and metadata. For a pure-Python package it commonly contains Python modules and package data; native wheels can contain compiled extensions and platform-specific files.
- **Build frontend:** coordinates the build, resolves/installs build requirements into a build environment, calls the backend API, and returns artifacts. Examples: `pip`, `uv`, and `build`.
- **Build backend:** knows how this project is built and which files go into its artifacts. Examples: `hatchling`, `setuptools`, `flit-core`, `pdm-backend`, `maturin`, and `scikit-build-core`.
- **Package index:** stores distribution files and exposes metadata so installers can find them. PyPI and TestPyPI are indexes, not build backends.

A useful high-level flow is:

```text
project source + pyproject.toml
              |
              v
      build frontend (pip / uv / build)
              |
              | creates or selects build environment
              | installs build-system requirements
              v
      build backend (Hatchling / setuptools / ...)
              |
              +------> source distribution (.tar.gz)
              |
              +------> wheel (.whl)
                           |
                           v
                installer installs wheel
```

The frontend and backend have separate responsibilities. The frontend is the coordinator; the backend implements the project-specific build. A frontend can work with different backends, and a backend can be invoked by different frontends, provided the relevant interfaces are supported.

### Why the separation matters

Without a standard interface, each installer would need custom knowledge of each build tool. PEP 517 defines an interoperable backend hook interface. PEP 518 declares the minimum requirements needed to start that backend. This separation makes tooling more interchangeable, but it does **not** make every project build identical: backends have different configuration, file-selection rules, native requirements, and capabilities.

## 3. Historical background and the modern standards

### 3.1 From `setup.py` to standardized build interfaces

Historically, many projects used `setup.py`, a Python script that imported `setuptools` (or older `distutils`) and described a package. Commands such as `python setup.py sdist` and `python setup.py bdist_wheel` became common.

- **`distutils`:** the original standard-library packaging/build utility. It was deprecated and then removed from the Python standard library in Python 3.12. Some legacy projects still encounter compatibility shims or third-party copies, but new projects should not depend on the removed standard-library implementation.
- **`setuptools`:** an external, widely used packaging project that extended the older `distutils` model and continues to support many legacy and modern workflows.
- **`easy_install`:** an older `setuptools` installer that could install packages and manage `.egg` distributions. It is obsolete for normal modern installation workflows; use a current installer such as `pip` or `uv`.
- **Egg distributions (`.egg`):** a historical distribution/install format. Wheels superseded eggs as the standardized built-distribution format.
- **`setup.py`:** remains a Python configuration/script file in many existing projects. The issue is not that the filename instantly became invalid; it is that invoking it directly as a command-line build interface is deprecated practice and couples workflows to one implementation. Modern frontends should be used instead.

The migration was incremental. Existing projects can still use `setuptools` and may retain `setup.py` or `setup.cfg`; PEP 517 does not require all project configuration to be rewritten at once. The modern goal is a standardized frontend/backend interface and explicit build requirements.

### 3.2 Standards map: each PEP solves a different problem

| Standard | Main role | What it does not do by itself |
|---|---|---|
| **PEP 517** | Defines the frontend/backend build hook interface. | Does not define all project metadata fields or choose a backend. |
| **PEP 518** | Defines `[build-system]` in `pyproject.toml`, including build requirements and backend selection. | Does not describe all runtime dependencies. |
| **PEP 621** | Standardizes project metadata in `[project]`. | Does not dictate how every backend selects package files. |
| **PEP 660** | Defines editable-install support through editable-wheel hooks for PEP 517 backends. | Does not promise every file or every backend-specific workflow behaves as a live editable view. |
| **PEP 639** | Defines SPDX license expressions and license-file metadata, including modern `license` and `license-files` project metadata. | Does not decide which license is legally appropriate for your project. |
| **PEP 735** | Defines dependency groups for development/workflow dependencies. | Dependency groups are not published as runtime extras in package metadata. |
| **PEP 751** | Defines the interoperable `pylock.toml` lock-file format. | It does not make every tool-specific lockfile interchangeable with `pylock.toml`. |

Standards can be implemented at different times by tools. A PEP being accepted does not guarantee that an old backend version supports every feature. Check the versions of your frontend and backend, especially for newer metadata fields.

### 3.3 PEP 517: the backend hook contract

PEP 517 defines a Python object, selected by an import path in `pyproject.toml`, that exposes hooks used by a frontend. The frontend invokes hooks rather than assuming it can call a particular `setup.py` command.

The important hooks include:

- `build_wheel(wheel_directory, config_settings=None, metadata_directory=None)` — builds a wheel and returns the wheel filename.
- `build_sdist(sdist_directory, config_settings=None)` — builds a source distribution and returns its filename.
- `get_requires_for_build_wheel(config_settings=None)` — optionally returns extra Python build requirements needed for building a wheel or preparing wheel metadata.
- `get_requires_for_build_sdist(config_settings=None)` — optionally returns extra requirements needed for building an sdist.
- `prepare_metadata_for_build_wheel(metadata_directory, config_settings=None)` — optionally prepares wheel metadata without requiring the frontend to build the complete wheel first.

The first two build hooks are the core artifact-building operations. The `get_requires_*` and metadata-preparation hooks are optional; where a hook is absent, the standard defines fallback behavior. For example, a frontend can build a wheel and extract its metadata if the backend lacks `prepare_metadata_for_build_wheel`. Exact call sequences depend on frontend needs and backend capabilities.

`config_settings` is an implementation-defined escape hatch for backend-specific options. It is not a universal configuration schema: a setting meaningful to one backend may be ignored or rejected by another.

PEP 517 also allows frontends to build a wheel from an unpacked sdist to check whether the source archive has enough information to reproduce the build. This is a valuable release-quality check, not merely a theoretical detail.

### 3.4 PEP 518: declare what is needed to start the backend

A modern project normally declares its build requirements in `[build-system]`:

```toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"
```

- `requires` is a list of PEP 508 requirement strings that the frontend makes available in the build environment before calling the backend's initial hooks.
- `build-backend` is an importable Python object path. `hatchling.build` means import module `hatchling.build` and use the backend object exposed there. This lesson uses `hatchling>=1.27` rather than the older `>=1.25` starter example because Hatchling 1.27.0 added support for PEP 639 license-expression metadata; the configured metadata and minimum backend version must agree.
- `backend-path` is optional and allows a backend to be loaded from a directory inside the source tree. It is intended for in-tree backends and is explained later.

Do not put ordinary application runtime dependencies in `build-system.requires` just because your project imports them at runtime. Conversely, if the backend needs a package to execute the build, it belongs in build requirements or in additional requirements declared by the backend hooks.

**Legacy fallback:** if a project has no `pyproject.toml` build-system declaration, or the relevant table does not select a backend, frontends have legacy fallback behavior involving `setuptools` for backward compatibility. The exact fallback path depends on the project and frontend. Do not rely on fallback behavior for a new project: declare the backend explicitly.

### 3.5 PEP 621: declare project metadata

PEP 621 defines standardized metadata in `[project]`, such as name, version, description, Python support, dependencies, authors, URLs, and optional dependencies. A backend translates this metadata into distribution metadata.

A static field is written directly in `pyproject.toml`. A field listed in `dynamic` is supplied by the backend or a configured plugin. A field must not be both statically specified and declared dynamic. Only fields that the metadata specification allows to be dynamic may be declared dynamic; backend-specific behavior still matters.

### 3.6 PEP 660: editable installs

Commands such as `pip install -e .` and `uv pip install -e .` ask the frontend to install the project in editable mode. For a PEP 517 backend, PEP 660 defines editable-wheel hooks, including `build_editable`, with optional companion hooks such as `get_requires_for_build_editable` and `prepare_metadata_for_build_editable`.

The editable wheel is an installation mechanism, not a normal distributable release wheel. A backend may implement editability with a path-based mechanism, generated import hooks, or another supported strategy. Python source edits are usually visible without reinstalling, but changes to metadata, compiled extensions, generated files, or backend configuration may require rebuilding/reinstalling. Editable behavior can differ from a regular wheel, which is why editable tests cannot replace wheel tests.

### 3.7 PEP 639: license expression versus license files

Modern project metadata uses an SPDX expression for the license identifier and `license-files` to select legal text and notices to include in distributions. For example:

```toml
[project]
license = "MIT"
license-files = ["LICENSE", "NOTICE*", "licenses/**"]
```

`license = "MIT"` communicates the SPDX license expression. `license-files` identifies the files to distribute. These serve different purposes and should normally both be considered. The older table form such as `license = { file = "LICENSE" }` or `license = { text = "..." }` was deprecated by PEP 639; do not copy it into new configurations. Legacy license classifiers are also deprecated in favor of `license` expressions, although other classifiers (Python versions, intended audience, development status, and so on) remain useful.

License syntax support depends on the backend version. If the selected backend is too old for PEP 639 metadata, upgrade it or follow its documented compatibility guidance rather than silently changing the expression to arbitrary prose.

## 4. Frontends and backends in practice

### 4.1 Frontends

- **`pip`:** installs packages and builds local source projects as needed. It can invoke a PEP 517 backend while installing from a source tree or sdist.
- **`uv`:** provides project and environment workflows, package installation, building (`uv build`), and publishing (`uv publish`). Its exact command options can vary by version.
- **`build` (`python -m build`):** a dedicated frontend for building sdists and wheels. It is useful in release automation because its job is artifact creation rather than environment management generally.

Frontends do not replace each other in every workflow. `pip install .` means “build/install this project”; `uv build` means “produce distribution artifacts”; `python -m build` also builds artifacts. `build` is a Python distribution named `build`, not a build backend.

### 4.2 Backends and when to choose them

| Project type | Common choice | Why / trade-offs |
|---|---|---|
| Pure Python library | `hatchling`, `flit-core`, or `setuptools` | All can build Python packages. Compare file-selection behavior, plugins, configuration familiarity, and project requirements. |
| Existing or complex legacy project | `setuptools` | Mature compatibility with `setup.py`, `setup.cfg`, custom commands, extensions, and established configuration. Migration can be incremental. |
| Rust extension or Rust-backed Python package | `maturin` | Integrates Rust build tooling and Python packaging. Requires a Rust toolchain and appropriate target setup. |
| C/C++ or CMake-based extension | `scikit-build-core` | Integrates CMake with Python packaging. Requires suitable compilers, CMake, and native dependencies. |
| Project already standardized on PDM | `pdm-backend` | Integrates with PDM-oriented configuration and workflows; do not assume its file rules match Hatchling. |
| Project using Poetry's backend | `poetry-core` | Builds projects configured for Poetry's model; frontend and backend are still separate concepts. |

There is no universally best backend. Choose the simplest backend that supports your build, metadata, and distribution requirements. Avoid selecting a native backend for a pure-Python project unless there is a concrete need.

## 5. A complete `tinytools` example

This lesson uses a small package named `tinytools`, version `0.1.0`. The example is deliberately small enough to inspect, but includes metadata, package data, typing information, and tests so the distribution can be verified.

### 5.1 Directory structure

```text
tinytools/
├── LICENSE
├── README.md
├── pyproject.toml
├── src/
│   └── tinytools/
│       ├── __init__.py
│       ├── core.py
│       ├── py.typed
│       └── data/
│           └── defaults.json
└── tests/
    └── test_core.py
```

Create the files as follows.

**`src/tinytools/core.py`**

```python
from importlib.resources import files
import json


def add(left: int, right: int) -> int:
    """Return the sum of two integers."""
    return left + right


def default_settings() -> dict[str, object]:
    """Load the package's bundled default settings."""
    resource = files("tinytools").joinpath("data/defaults.json")
    return json.loads(resource.read_text(encoding="utf-8"))
```

**`src/tinytools/__init__.py`**

```python
"""Small, packaging-friendly utilities."""

from .core import add, default_settings

__all__ = ["add", "default_settings"]
```

**`src/tinytools/data/defaults.json`**

```json
{
  "mode": "safe",
  "retries": 3
}
```

**`src/tinytools/py.typed`**

```text
```

`py.typed` is an intentionally empty marker file. For a package that publishes inline type annotations and intends type checkers to consume them, it signals that the package is typed under PEP 561. The marker must be included in the distribution.

**`tests/test_core.py`**

```python
from tinytools import add, default_settings


def test_add() -> None:
    assert add(2, 3) == 5


def test_default_settings() -> None:
    assert default_settings() == {"mode": "safe", "retries": 3}
```

**`README.md`**

````markdown
# tinytools

Small utilities for Python 3.12 and newer.

```python
from tinytools import add

assert add(2, 3) == 5
```
````

**`LICENSE`**

Use the full text of the license you have chosen. Do not publish a placeholder or assume that writing `license = "MIT"` creates the license text. For this example, use the standard MIT license text and replace the copyright holder/year with accurate information.

### 5.2 Minimal valid configuration

**`pyproject.toml`**

```toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "tinytools"
version = "0.1.0"
description = "Small utilities for Python"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
license-files = ["LICENSE"]
authors = [
  { name = "Example Maintainer" },
]
keywords = ["utilities", "example"]
classifiers = [
  "Development Status :: 3 - Alpha",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
]

[project.urls]
Homepage = "https://example.invalid/tinytools"
Repository = "https://example.invalid/tinytools"
Issues = "https://example.invalid/tinytools/issues"
```

The `example.invalid` URLs are placeholders and must be replaced before publishing. The configuration deliberately omits runtime dependencies because this tiny example uses only the standard library. In a real package, declare actual runtime dependencies in `project.dependencies`, for example `dependencies = ["httpx>=0.27"]` only if the package truly imports and requires `httpx` at runtime.

Key fields:

- `requires-python` declares the supported Python version range and becomes installer-visible metadata. Test the versions you claim to support.
- `readme` points to a file used as the long description. A Markdown filename lets modern build tools infer the content type; a table form can specify a content type explicitly where needed.
- `authors` and `keywords` improve project metadata and discoverability.
- `classifiers` are controlled metadata strings. Use valid, current Trove classifiers; do not claim support for a Python version without testing it.
- `[project.urls]` adds labeled project links.
- `license` is an SPDX expression; `license-files` selects the actual license/legal files to include.

This is a minimal project configuration, not a universal template. Backend configuration, dependencies, classifiers, license files, and package-data rules must match the actual project.

### 5.3 Configure Hatchling to include the package

For a `src/` layout, make package selection explicit when you want the project to be easy to audit:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/tinytools"]

[tool.hatch.build.targets.sdist]
include = [
  "/src",
  "/tests",
  "/README.md",
  "/LICENSE",
  "/pyproject.toml",
]
```

These are **Hatchling-specific** settings, not universal PEP 517 settings. The wheel's package selection is distinct from the sdist's file selection. Confirm the exact patterns against the Hatchling version used in your environment. The source distribution must contain everything required to build the wheel, including source files, metadata inputs, and any generated-version inputs. If your project uses files outside these paths, add them deliberately.

Hatchling's normal package inclusion behavior often includes files inside the selected package directory, such as `data/defaults.json` and `py.typed`; do not assume this without inspecting the artifact. Explicit include/force-include rules may be needed for unusual layouts. With `setuptools`, comparable tasks often use package discovery, `package_data`, `include-package-data`, and/or `MANIFEST.in`; these options are not interchangeable with Hatchling's configuration.

### 5.4 Add optional dependencies and dependency groups

A runtime extra is published as package metadata and can be requested by users:

```toml
[project.optional-dependencies]
http = ["httpx>=0.27"]
test = ["pytest>=8"]
```

Users can request an extra with an install specifier such as `tinytools[http]`. Only include `http` if the feature really uses `httpx`. The `test` extra is a runtime extra from the packaging-standard point of view; some projects use it, but dependency groups are often a better fit for development-only tools.

PEP 735 dependency groups are for project workflows and are not published as `Provides-Extra` runtime extras:

```toml
[dependency-groups]
test = ["pytest>=8"]
dev = [
  { include-group = "test" },
  "ruff>=0.6",
]
```

The consuming tool must support dependency groups. A lockfile or project manager may use them to resolve a development environment, but a user installing the published wheel does not automatically receive those group dependencies. Do not confuse `[project.optional-dependencies]` with `[dependency-groups]`.

### 5.5 Package data and typing files

Package data includes files imported or read at runtime but which are not Python modules: JSON defaults, templates, schemas, SQL, certificates, and similar resources. Read packaged resources with `importlib.resources` rather than assuming the current working directory or a source-tree path. Include the files in the wheel and verify that they are also present in the sdist when required to rebuild the wheel.

For Hatchling, configure the wheel target as needed and inspect it. For setuptools, package-data behavior is configured through setuptools-specific options. The existence of a file in your checkout does not prove it is present in either artifact.

## 6. Intermediate: lifecycle, hooks, and isolation

### 6.1 What happens during `pip install .`?

A typical PEP 517 source install follows this conceptual sequence:

1. The frontend detects the project source tree and reads `pyproject.toml`.
2. It identifies the backend and the initial requirements in `[build-system].requires`.
3. Unless isolation is disabled or the frontend uses a different supported strategy, it creates an isolated build environment and installs those requirements.
4. It may call `get_requires_for_build_wheel` and install any additional requirements returned by the backend.
5. It obtains wheel metadata, often through `prepare_metadata_for_build_wheel` when available.
6. It builds a wheel through `build_wheel` (some workflows may build an sdist first and build from that).
7. The installer installs the resulting wheel into the target environment and resolves/installs the package's runtime dependencies as appropriate.

The exact order is frontend- and backend-dependent, and not every hook is called in every build. The key guarantee is that the frontend follows the standard interface and makes declared build requirements available in the environment used for the relevant hooks.

### 6.2 Build isolation is not the same as runtime isolation

Build isolation prevents a project build from accidentally relying on whatever build-tool versions happen to be installed in the user's main environment. It gives the frontend a separate environment for build-time Python requirements. It does **not**:

- sandbox malicious build code;
- install system compilers or C libraries automatically;
- guarantee bit-for-bit reproducibility;
- isolate the final application from runtime dependency conflicts;
- eliminate network or index configuration problems while resolving build requirements.

The frontend must be able to obtain compatible versions of the declared build requirements. If a project says `hatchling>=1.27`, the environment may resolve a newer compatible version unless constraints or a lock/build policy limit it. A minimum version is a compatibility floor, not a pin.

### 6.3 Build requirements and constraints

`build-system.requires` lists bootstrap requirements, commonly a backend and its required plugins. A backend can return additional build requirements from `get_requires_for_build_wheel` or `get_requires_for_build_sdist`.

Use constraints intentionally when you need controlled build dependency versions, especially in release CI. A constraint generally restricts versions; it does not necessarily cause a package to be installed by itself. How a frontend accepts build constraints is tool/version-specific. Do not assume the application's lockfile automatically locks the isolated build environment: inspect the frontend's documented behavior and record the actual build toolchain used for releases.

A build dependency conflict may occur when:

- the backend requires a version incompatible with a plugin;
- a backend plugin imports an API removed in a newer backend;
- the project needs different versions for build and runtime phases;
- a transitive build dependency has incompatible constraints;
- a configured private index lacks a required build package.

Diagnose the first meaningful resolver or import error, identify which hook was running, and check the declared build requirements. Avoid solving a build failure by adding unrelated packages to runtime dependencies.

### 6.4 Build from a source distribution

An sdist should contain enough source and metadata inputs to build a wheel without access to the original checkout. This is particularly important when versions are derived from Git tags or generated files.

A reliable release check is:

1. Build an sdist and wheel from a clean checkout.
2. Extract the sdist into a temporary directory.
3. Build a wheel from that extracted directory.
4. Install the resulting wheel in a clean environment and smoke-test it.

If the build only succeeds from the checkout, inspect whether the sdist omitted a file, Git metadata, generated source, version file, or tool configuration. A release process should not depend accidentally on untracked local files.

### 6.5 Build commands for `tinytools`

Install `uv` and use a recent version. From the project root:

```bash
uv build
```

This asks `uv` to build distribution artifacts. For version `0.1.0`, expected artifact names include:

```text
dist/
├── tinytools-0.1.0.tar.gz
└── tinytools-0.1.0-py3-none-any.whl
```

These are expected names for this pure-Python example, not a claim that this command was run. Actual outputs depend on configuration and tool behavior. The wheel tag `py3-none-any` is typical for a pure-Python wheel that does not require a specific CPython ABI or platform.

To use the `build` frontend with `uv` as its installer for build dependencies:

```bash
python -m pip install --upgrade build
python -m build --installer uv
```

The `--installer uv` option selects how `build` installs build requirements; it does not switch the backend from Hatchling. If the installed `build` version does not recognize that option, upgrade `build` and consult `python -m build --help`. Use the same interpreter/environment intentionally; `python -m build` invokes the `build` package installed for that interpreter.

### 6.6 Editable-install workflow

From the project root, in an activated development environment:

```bash
uv pip install -e .
# or
python -m pip install -e .
```

Then test imports and run the tests. If the backend supports PEP 660, the frontend asks it to produce an editable wheel. Editable installs are convenient during development because edits to Python files are usually visible without rebuilding the wheel.

Limitations:

- Editable import behavior may rely on `.pth` files, import hooks, or a backend-specific strategy.
- Package data may not behave exactly like it does in a built wheel, especially if files are generated or copied during builds.
- Metadata changes, entry-point changes, and dependency changes may require reinstalling.
- Compiled extensions generally require rebuilding after source changes.
- A successful editable import does not prove that the wheel contains the same modules and data.

Use editable installs for the development loop, but use built-wheel tests for release validation.

## 7. Metadata, dynamic values, and backend configuration

### 7.1 Static and dynamic metadata

Static metadata is directly declared:

```toml
[project]
name = "tinytools"
version = "0.1.0"
```

Dynamic metadata delegates a permitted field to the backend or a plugin:

```toml
[project]
name = "tinytools"
dynamic = ["version"]
```

When `version` is dynamic, do not also set `version = "0.1.0"` in `[project]`. Configure the backend/plugin to calculate the version. If the project declares `dynamic = ["version"]` but has no working mechanism to provide it, the build should fail or metadata generation will be incomplete; do not rely on a guessed version.

There are three common sources for a dynamic version, and the choice affects reliability and the sdist:

1. **A Python attribute**, such as `tinytools.__version__`. This can keep the version near the code, but the backend must be able to read the attribute without triggering imports that require undeclared runtime dependencies or files that are unavailable during the build.
2. **A version file**, such as `VERSION`. This is straightforward for static release versions, but the file must be included in the sdist and the backend must be configured to read it. The configuration syntax is backend-specific.
3. **VCS tags and repository state.** This can reduce duplicated version declarations and fit tag-driven releases, but a checkout or archive without the expected tags/metadata needs a deliberate fallback.

For example, with **setuptools specifically** (not generic PEP 621 syntax), a project can delegate the version to an attribute or file:

```toml
[project]
name = "tinytools"
dynamic = ["version"]

[tool.setuptools.dynamic]
version = { attr = "tinytools.__version__" }
# Alternatively, use a version file instead of `attr`:
# version = { file = "VERSION" }
```

Do not enable both alternatives at once; choose one and ensure the named attribute or file actually exists. Other backends use different configuration. A static `[project].version` is usually simplest when the release process does not require dynamic versioning.

Two common VCS strategies are:

- **`hatch-vcs`:** a Hatchling plugin that derives version information from version-control metadata/tags.
- **`setuptools-scm`:** integrates with setuptools to derive versions from VCS state and can generate version information for source builds.

These are backend-specific integrations, not generic PEP 517 hooks. Read the plugin's current configuration and versioning rules. A VCS-derived build can fail if the checkout lacks tags, Git metadata, or a supported archive-generated version file.

For an sdist to rebuild successfully, include a version file when the chosen backend relies on one and configure the versioning plugin to work from an sdist, or otherwise ensure the archive contains sufficient version information. Never assume the `.git` directory will be present in an sdist. Compare the trade-offs explicitly: static versions are easy to audit, file/attribute versions can reduce duplication but introduce configuration dependencies, and VCS versions work well with tag-driven release automation but require a reliable source-archive fallback.

### 7.2 README content type

For a Markdown README, `readme = "README.md"` is generally sufficient for modern backends to infer the content type. PEP 621 also permits a table form for explicit content type, for example:

```toml
[project]
readme = { file = "README.md", content-type = "text/markdown" }
```

Use the table form when explicit content type is useful or required by the selected tooling. PyPI renders package metadata's long description, not arbitrary files from your repository. Relative image and link paths may not resolve as expected on the project page; verify the rendered description before publishing.

### 7.3 Authors, classifiers, URLs, extras, and dependencies

- `authors` and `maintainers` are arrays of tables containing supported fields such as `name` and `email`.
- `keywords` is an array of strings, not a sentence.
- `classifiers` should use valid Trove classifier values. They are useful for discovery but do not install dependencies or enforce compatibility.
- `[project.urls]` maps labels to URLs. Use clear labels such as `Homepage`, `Repository`, `Documentation`, `Issues`, and `Changelog` where applicable.
- `dependencies` declares mandatory runtime requirements using PEP 508 strings.
- `[project.optional-dependencies]` declares user-selectable extras and is published into distribution metadata.
- `[dependency-groups]` declares workflow dependencies such as `test`, `lint`, and `docs`; it is not a published runtime-extra interface.
- `requires-python` is an installer-visible compatibility constraint, not a replacement for a test matrix.

Avoid speculative or redundant metadata. Every claim should match the real package and its support policy.

### 7.4 Source layout and file inclusion

A `src/` layout keeps the import package separate from the repository root and reduces accidental imports from the checkout. It does not guarantee correct packaging by itself.

Always ask two separate questions:

1. Does the **sdist** contain everything needed to rebuild?
2. Does the **wheel** contain everything needed to install and use the package?

For example, `tests/` and development configuration may belong in an sdist but not the wheel. Runtime JSON templates and `py.typed` belong in the wheel if the package needs them. A license file should be included according to the modern license metadata rules. Backend include/exclude patterns are tool-specific; do not copy a Hatchling `[tool.hatch...]` table into a setuptools project and expect it to work.

Inspect artifacts rather than inferring their contents from configuration alone.

## 8. Advanced: an educational in-tree backend

A project can set `backend-path` to load a backend from a directory within its source tree. This is useful for learning the PEP 517 contract or for specialized projects that truly need a custom backend. It is **not** a recommendation to write a production backend for ordinary packages.

The following intentionally minimal example illustrates the shape of the contract. It is not a complete, production-capable backend and does not create a valid wheel or sdist; it exists only to show how a frontend resolves the backend import path and calls hooks.

```text
backend-demo/
├── pyproject.toml
└── local_backend.py
```

**`pyproject.toml`**

```toml
[build-system]
requires = []
build-backend = "local_backend"
backend-path = ["."]
```

**`local_backend.py`**

```python
from __future__ import annotations


def get_requires_for_build_wheel(config_settings=None):
    """No additional Python requirements in this teaching example."""
    return []


def get_requires_for_build_sdist(config_settings=None):
    return []


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    raise NotImplementedError(
        "Educational stub only: a real backend must create a valid wheel"
    )


def build_sdist(sdist_directory, config_settings=None):
    raise NotImplementedError(
        "Educational stub only: a real backend must create a valid sdist"
    )
```

`backend-path` entries are paths relative to the source tree and are subject to PEP 517's restrictions. The backend must be importable from the permitted in-tree path; a frontend should not allow the declared backend path to escape the source tree. A real backend must implement the mandatory hooks correctly, create archives that conform to the wheel/sdist specifications, produce consistent metadata, and handle errors and temporary directories robustly. A stub that raises `NotImplementedError` is not a buildable package.

Why not use this in production? You inherit responsibility for archive layout, metadata, file inclusion, security, platform behavior, reproducibility, and compatibility with multiple frontends. Prefer a maintained backend unless you have a specific requirement that existing backends cannot meet.

## 9. Native builds: Rust, C/C++, and system dependencies

A backend can orchestrate a compiler, but it cannot conjure an operating-system toolchain that is absent.

- **Rust:** `maturin` commonly integrates Cargo and Rust extension projects. Build requirements may include `maturin`; the machine or CI image also needs a suitable Rust toolchain and any target-specific setup.
- **C/C++/CMake:** `scikit-build-core` integrates CMake-based builds. The environment may require a compiler, CMake, Python headers, and external libraries.
- **setuptools extensions:** setuptools can build native extensions too, especially in existing projects, but configuration and cross-platform distribution can be complex.

The Python requirements in `[build-system].requires` are not a declaration mechanism for system packages such as `libxml2-dev`, a C compiler, or a Rust toolchain. Document and provision those separately in developer setup and CI. For release builds, record compiler/toolchain versions and target platforms.

### Native build failure triage

1. Identify whether the failure occurred while resolving Python build requirements, importing the backend, configuring the native build system, compiling, linking, or installing the wheel.
2. Read the first actionable error, not only the final `Failed building wheel` summary.
3. Check Python version, architecture, compiler availability, headers, CMake/Cargo version, and system-library development files.
4. Check whether a compatible wheel already exists for the target. A source build may be avoidable for end users if you publish supported wheels.
5. Reproduce in a clean environment and record the exact command and toolchain.

Do not fix a missing compiler by blindly disabling build isolation. Build isolation concerns Python build dependencies, not system compilers.

## 10. Reproducible builds

A reproducible build aims for the same source inputs and build environment to produce byte-identical artifacts. This is stronger than “the build succeeded twice.” Achieving it may require control over source inputs, build dependencies, timestamps, file ordering, generated metadata, compiler behavior, and platform details.

### 10.1 Practical controls

- Build from a clean, tagged source tree; avoid untracked files and mutable external inputs.
- Pin or constrain build dependencies in the release process and record the resolved versions.
- Ensure the sdist includes all build inputs and can build without `.git` or local-only files.
- Use `SOURCE_DATE_EPOCH` where supported by the backend and archive-generation stack. It is a convention consumed by tools, not a universal magic switch; support and semantics vary.
- Ensure archive members and generated files are emitted in deterministic order where the backend/toolchain permits it.
- Avoid embedding current timestamps, random identifiers, absolute paths, or machine-specific values in artifacts.
- For native builds, control compiler/linker versions, flags, system libraries, and target environment; byte-for-byte reproducibility is harder.

### 10.2 Compare artifacts

Build twice from the same clean source revision in separately prepared environments, then compare hashes:

```bash
sha256sum dist/*
```

On systems without `sha256sum`, use an equivalent hashing tool. If hashes differ, compare archive contents and metadata; a tool such as `diffoscope` can help explain differences. Different hashes do not automatically prove a functional problem, but they do show the artifacts are not byte-identical.

Do not claim reproducibility merely because the package builds twice. Record the inputs, tool versions, environment, and comparison result. Some backends may honor `SOURCE_DATE_EPOCH` while others or their dependencies may not.

## 11. Migration from legacy configuration

Migration should separate **standardized metadata** from **tool-specific build behavior**. Do not try to translate every old configuration key into `[project]` blindly.

### 11.1 Inventory the old project

Before changing files, identify:

- package name, version, Python requirement, description, README, license, authors, URLs, dependencies, extras, and classifiers;
- package discovery and package-data rules;
- `MANIFEST.in` rules, generated files, extension modules, custom build commands, entry points, and plugins;
- whether version or metadata is calculated dynamically;
- files required for building from an sdist.

Preserve behavior with tests and artifact inspection, not just a syntactically valid TOML file.

### 11.2 A conservative migration to Hatchling

A simple legacy pure-Python project can begin with:

```toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "tinytools"
version = "0.1.0"
description = "Small utilities for Python"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
license-files = ["LICENSE"]

[tool.hatch.build.targets.wheel]
packages = ["src/tinytools"]
```

Then add actual dependencies, authors, URLs, classifiers, optional dependencies, and any dynamic metadata required by the project. This example assumes a `src/tinytools` package and a modern Hatchling version. A flat layout or unusual package structure needs different package-selection settings.

Migration steps:

1. Add `pyproject.toml` and declare the backend and build requirements.
2. Move standardized metadata from `setup.py`/`setup.cfg` into `[project]` where PEP 621 supports it.
3. Move backend-specific behavior into the new backend's configuration. Hatchling does not understand arbitrary setuptools configuration, and it does not automatically execute custom setuptools commands.
4. Replace legacy license table metadata with a valid SPDX expression and `license-files` as appropriate.
5. Configure package discovery and data inclusion explicitly, then build both artifacts.
6. Test from the extracted sdist and install the built wheel in a clean environment.
7. Remove obsolete configuration only after the new build has been verified. Avoid maintaining contradictory sources of metadata.

### 11.3 `setup.py` and `setup.cfg` projects

A legacy project does not necessarily need to migrate from setuptools to Hatchling. Often the lowest-risk step is to add a correct `[build-system]` declaration selecting setuptools and gradually move supported metadata to `[project]`. Retaining `setup.py` for setuptools-specific extension configuration may be appropriate while the project is modernized. Do not invoke `python setup.py ...` as the preferred user-facing build command; use a frontend.

### 11.4 Poetry-based projects

Poetry has its own project-management conventions. Moving a project from Poetry to Hatchling involves more than renaming `[tool.poetry]` keys:

- Move metadata to standardized `[project]` fields where the PEP 621 schema supports it.
- Convert dependency groups/extras according to their intended meaning.
- Translate package inclusion, scripts, versioning, and build-specific behavior to the chosen backend's supported configuration.
- Revisit lockfile ownership and commands. `uv.lock`, Poetry's lockfile, and other tool lockfiles are not automatically interchangeable.
- Rebuild and inspect artifacts before removing the old configuration.

If you keep Poetry's backend (`poetry-core`), understand that the backend configuration and the tool used to manage environments are related but distinct concerns.

## 12. PEP 751 and lock-file awareness

PEP 751 defines the standardized `pylock.toml` format for recording dependency information intended to support reproducible installation. It is a separate concern from PEP 517 build-backend selection.

`uv.lock` is a tool-specific lockfile used by `uv`. Do **not** assume it is interchangeable with `pylock.toml`, or that one can be renamed to the other. Tool support for generating, consuming, or converting the standardized format may vary. Consult current `uv` and PyPA documentation before choosing a workflow.

Also distinguish:

- **Project dependency declaration:** which dependency ranges the project says it needs.
- **Environment lock:** a resolved set of dependency artifacts for a workflow/environment.
- **Build requirements:** Python packages needed to execute the backend and build hooks.
- **System build inputs:** compilers, headers, libraries, and external tools.

A lockfile for the application environment does not automatically guarantee a locked or reproducible build environment.

## 13. Build-system security

A source build is code execution. A backend and its dependencies run Python code, and native build systems may run compiler tools, build scripts, and configuration commands. An sdist from an unknown or compromised source should be treated as untrusted input.

### 13.1 Wheels and sdists have different risk profiles

A wheel is generally installed by unpacking files and recording metadata; it avoids executing the package's source-build backend during ordinary wheel installation. This is one reason wheels are often preferable operationally. However, a wheel can still contain malicious Python code that executes when imported or run, and a malicious package can target installation-related mechanisms. Wheels are not a guarantee that a package is safe.

An sdist often requires a build step that executes the project's build backend and potentially native build code. That increases the attack surface before installation. Prefer wheels when a suitable, trusted wheel is available, while retaining a policy for cases where source builds are necessary.

To require binary distributions where supported:

```bash
python -m pip install --only-binary :all: some-package
```

This can fail if no compatible wheel exists. It is a policy choice, not a universal fix; native ecosystems and some platforms may require source builds.

### 13.2 Practical controls

- Use trusted indexes and verify project identity before installing.
- Keep build frontends, backends, and build plugins updated.
- Build untrusted sources in disposable, least-privilege environments with restricted secrets and network access where feasible.
- Do not expose publishing credentials to pull-request builds or untrusted build scripts.
- Prefer isolated, ephemeral release runners and record source revisions and tool versions.
- Review backend plugins and custom build hooks as executable code.
- Separate build and publish permissions in CI; the build job should not need upload credentials.
- Inspect artifacts and test the exact files intended for release.

**Important distinction:** PEP 517 build isolation is dependency isolation, not a security sandbox. It does not make a malicious backend safe.

## 14. Common errors and systematic troubleshooting

### 14.1 Missing or incorrect `[build-system]`

**Symptoms:** legacy `setuptools` unexpectedly runs, the backend import fails, or a frontend reports that it cannot find a build backend.

**Checks:**

1. Confirm `pyproject.toml` is at the project root and valid TOML.
2. Confirm `build-backend` is a valid import path for the chosen backend.
3. Confirm `requires` includes the backend and any bootstrap plugins it needs.
4. Confirm the selected backend version supports the metadata/configuration you use.
5. If intentionally using legacy fallback, document that choice; for new projects, declare the backend explicitly.

### 14.2 `ModuleNotFoundError` while building

The missing module may be a build dependency rather than a runtime dependency. Determine which hook failed and which environment is running it. Add the requirement to the build configuration or backend's documented build-requirement mechanism, not automatically to `[project].dependencies`.

If `--no-build-isolation` is enabled, the module may simply be absent from the active environment. First retry with isolation enabled; then fix the declared requirements.

### 14.3 Missing JSON, templates, or `py.typed`

The source checkout works but the installed package fails to open a file, or type checkers do not recognize the package as typed.

**Fix:** inspect the wheel archive; add the resource to the backend's wheel inclusion rules; ensure the sdist also contains it when needed for rebuilding. Test using `importlib.resources` from an installed wheel.

### 14.4 Editable installation passes, wheel fails

Editable mode may import files directly from the checkout. The wheel may omit modules or data files, or may use different generated files.

**Fix:** build a wheel, install it into a fresh environment outside the repository, and run smoke tests there. Do not run the smoke test from the project root if that could cause Python to import the source tree instead of the installed wheel.

### 14.5 Build isolation fails to resolve dependencies

Possible causes include network/index access, unavailable versions, incompatible constraints, a backend plugin missing from `requires`, or a backend hook returning additional requirements that cannot be resolved.

**Fix:** preserve the full error log; identify the failing requirement and hook; verify index configuration and package availability; check constraints; reproduce with the same frontend and Python version. Do not disable isolation as a first response.

### 14.6 `--no-build-isolation` pitfalls

Disabling isolation tells the frontend to use the current environment for build requirements; the user becomes responsible for installing compatible requirements. This can hide incomplete `build-system.requires`, make builds depend on a developer's environment, and produce different results across machines.

Use it only when you deliberately manage the complete build environment, such as a controlled build image, and document the procedure. It is not a substitute for correct build metadata.

### 14.7 Version cannot be determined

For VCS-derived versions, check whether the build has Git tags, whether the source archive includes generated version metadata, and whether the VCS plugin is installed as a build requirement. Build from the sdist to expose missing inputs. If the version is static, ensure `[project].version` is present and valid.

### 14.8 Native compiler or linker error

Check compiler, headers, system libraries, architecture, CMake/Cargo configuration, and wheel availability. Build isolation cannot install operating-system packages. Record the platform and toolchain in the issue or runbook.

## 15. Packaging validation: the “doctor” checklist

Run these checks before publishing. Install the tools into a dedicated development environment or invoke them through a tool runner such as `uvx` where appropriate.

### 15.1 Build cleanly

```bash
rm -rf dist build *.egg-info
uv build
```

The removal command is for a disposable working copy; review paths before running destructive commands. On Windows, use the corresponding PowerShell commands. Confirm both `.tar.gz` and `.whl` artifacts exist.

### 15.2 Check metadata and archive contents

```bash
uvx twine check dist/*
uvx check-wheel-contents dist/*.whl
uvx validate-pyproject pyproject.toml
```

Tool interfaces and supported options may vary by release; check `--help` if a command differs. `twine check` checks distribution metadata/long-description rendering requirements; `check-wheel-contents` checks wheel structure and common content problems; `validate-pyproject` validates `pyproject.toml` against packaging metadata schemas and related rules supported by that tool. These tools complement rather than replace one another.

### 15.3 Inspect the files directly

```bash
python -m zipfile -l dist/tinytools-0.1.0-py3-none-any.whl
python -m tarfile -l dist/tinytools-0.1.0.tar.gz
```

Confirm the wheel includes `tinytools/__init__.py`, `tinytools/core.py`, `tinytools/data/defaults.json`, `tinytools/py.typed`, license files in the expected metadata location, and the `.dist-info` metadata. Confirm the sdist includes all inputs needed to rebuild the wheel. The exact paths and metadata members depend on the specifications and backend implementation; inspect rather than assuming.

### 15.4 Install the built wheel in a clean environment

From a directory outside the repository, use a fresh virtual environment:

```bash
python -m venv /tmp/tinytools-wheel-test
/tmp/tinytools-wheel-test/bin/python -m pip install --upgrade pip
/tmp/tinytools-wheel-test/bin/python -m pip install /absolute/path/to/tinytools/dist/tinytools-0.1.0-py3-none-any.whl
/tmp/tinytools-wheel-test/bin/python -c "from tinytools import add, default_settings; assert add(2, 3) == 5; assert default_settings()['mode'] == 'safe'; print('wheel smoke test passed')"
```

The example uses POSIX virtual-environment paths. On Windows, use `Scripts\python.exe`. Replace `/absolute/path/to/tinytools` with the actual absolute project path. Do not execute from the source root; the purpose is to verify the installed wheel. If the package declares runtime dependencies, installation should resolve them from the configured index or supplied artifacts.

### 15.5 Rebuild from the sdist

From the project root, create a temporary extraction directory and build from the extracted source archive, not from the original checkout. For example, on POSIX systems:

```bash
mkdir -p /tmp/tinytools-sdist-check
tar -xzf dist/tinytools-0.1.0.tar.gz -C /tmp/tinytools-sdist-check
cd /tmp/tinytools-sdist-check/tinytools-0.1.0
uv build
```

The extracted top-level directory name normally includes the normalized project name and version; inspect the archive and adjust the `cd` path if the backend uses a different name. If `uv build` is run there, it builds artifacts from that extracted source tree. Then install the newly built wheel in a separate clean environment and smoke-test it. If the build fails, the sdist may be missing a build input or relying on state available only in the original checkout. These commands are illustrative and were not executed as part of this lesson's static review.

### 15.6 CI expectations

A production packaging job should, at minimum:

- run tests and static checks;
- build both sdist and wheel from a clean checkout;
- validate metadata and archive structure;
- inspect or assert the presence of required package data;
- build a wheel from the sdist;
- install the wheel in a clean environment and run smoke tests;
- record artifact hashes and build-tool versions;
- publish only artifacts that passed the checks.

## 16. Hands-on implementation exercises

Work in a copy of the `tinytools` project. Do not publish to PyPI during this lesson; the module roadmap reserves publishing practice for the later publishing lesson and recommends TestPyPI before any real release.

### Exercise 1 — Build and inspect

1. Create the project structure and files from Section 5.
2. Add the Hatchling configuration.
3. Run `uv build`.
4. List the contents of the wheel and sdist.
5. Record which files appear in each archive and explain why.

**Success criteria:** both artifacts exist; the wheel contains importable code and package data; the sdist contains enough inputs to rebuild.

### Exercise 2 — Break package-data inclusion on purpose

Temporarily change the backend's inclusion configuration so `data/defaults.json` is omitted from the wheel. Build and install the wheel in a clean environment, then run `default_settings()`.

**Questions:** What error appears? Why does the source-tree test potentially pass? Which configuration rule fixes the problem? Restore the correct configuration afterward.

### Exercise 3 — Compare editable and wheel installs

1. Install `tinytools` editable in one environment.
2. Build a wheel and install it in another clean environment.
3. Change `core.py` and observe the editable environment.
4. Observe the already installed wheel environment.
5. Change package metadata and compare whether reinstalling is needed.

**Success criteria:** explain why editable behavior is a development convenience rather than proof of release correctness.

### Exercise 4 — Add an extra and a dependency group

Add a real optional feature dependency to `[project.optional-dependencies]` and a `test` group to `[dependency-groups]`. Explain which appears in published package metadata and which is intended for development tooling. Do not add unused dependencies just to complete the exercise; if no optional feature exists, describe the configuration without adding a fake runtime feature.

### Exercise 5 — Migrate a legacy project

Take a small project with `setup.py` or `setup.cfg`. Inventory all metadata, package discovery, data files, custom commands, and dynamic values. Migrate to PEP 621 metadata and Hatchling **only if Hatchling supports the project's required build behavior**. Otherwise, declare setuptools as the backend and migrate incrementally.

Build both artifacts, inspect their contents, rebuild from the sdist, and install the wheel in a clean environment. Record any behavior that changed.

### Exercise 6 — Reproducibility experiment

Build the same revision twice in clean environments with recorded build-tool versions. Compare SHA-256 hashes. If they differ, inspect archive members and metadata timestamps; test whether setting `SOURCE_DATE_EPOCH` changes the result. Explain what evidence you have and what you cannot conclude.

## 17. Production-oriented packaging lab

**Goal:** deliver a verifiable `tinytools` release candidate without uploading it to an index.

### Phase A — Prepare the source

- [ ] Confirm version and `requires-python` policy.
- [ ] Confirm README and license text are accurate.
- [ ] Confirm runtime dependencies are declared and development-only tools are not misrepresented as runtime requirements.
- [ ] Confirm package data and `py.typed` inclusion.
- [ ] Confirm all required files are tracked by Git and no local secrets are present.

### Phase B — Build

```bash
uv build
```

Record the frontend version, backend version, Python version, platform, source commit, and artifact filenames. If you use `python -m build --installer uv`, record that command and its installed `build` version as well.

### Phase C — Validate

```bash
uvx twine check dist/*
uvx check-wheel-contents dist/*.whl
uvx validate-pyproject pyproject.toml
```

Inspect the wheel and sdist. Build a wheel from the extracted sdist. Install each release wheel candidate into a clean virtual environment and run tests or smoke checks outside the checkout.

### Phase D — Document the evidence

Write a short release note for your own records with:

- source revision and version;
- commands and tool versions used;
- artifact names and SHA-256 hashes;
- validation results;
- any platform or dependency limitations;
- whether rebuilding from the sdist succeeded;
- whether repeated builds were byte-identical, and how you checked.

A package is not release-ready merely because `uv build` exits successfully. Release readiness requires evidence that the metadata is correct, both artifacts are fit for their intended use, and the installed wheel works in an environment that resembles a consumer's environment.

## 18. Self-check questions with explained answers

### 1. What is the difference between a build frontend and a build backend?

A **frontend** coordinates the build: it reads build configuration, prepares a build environment, makes declared build requirements available, calls hooks, and obtains artifacts. A **backend** implements the hooks that create the project's sdist, wheel, and metadata. For example, `python -m build` or `uv build` is a frontend, while `hatchling.build` is a backend. Keeping these roles separate allows different frontends to build projects using the same backend API.

### 2. Why does `pip install .` create an isolated environment?

For a PEP 517 source build, build isolation helps ensure that the backend and its Python build dependencies are available at the versions resolved for the build, instead of relying accidentally on packages in the user's active environment. It reduces environment contamination and makes builds more predictable. It does not sandbox code, install compilers/system libraries, or guarantee byte-identical artifacts. `--no-build-isolation` transfers responsibility for installing compatible build requirements to the caller.

### 3. Convert a legacy `setup.py` project to `pyproject.toml` with Hatchling and verify both artifacts.

First inventory the legacy metadata, package discovery, package-data rules, custom build commands, extension modules, and dynamic versioning. For a simple pure-Python project, declare Hatchling under `[build-system]`, move supported standardized metadata into `[project]`, configure the wheel's package selection, and add explicit inclusion rules for required source and data files. Translate tool-specific settings rather than copying setuptools keys into Hatchling. If custom setuptools behavior cannot be represented, keep setuptools or redesign that behavior before changing backends.

Then run `uv build` (or `python -m build --installer uv`) and confirm that both a `.tar.gz` sdist and `.whl` exist. Inspect each archive; extract the sdist and build a wheel from it; install the wheel in a fresh virtual environment outside the repository; run import, package-data, and test smoke checks. `twine check`, `check-wheel-contents`, and `validate-pyproject` provide complementary checks. This process verifies more than TOML syntax: it verifies the actual artifacts consumers receive.

## 19. Final competency checklist

You are ready to move on when you can explain and demonstrate all of the following without relying on memory alone:

- [ ] Explain the historical roles of `setup.py`, `distutils`, setuptools, `easy_install`, eggs, and wheels.
- [ ] Distinguish PEP 517, PEP 518, PEP 621, PEP 660, PEP 639, PEP 735, and PEP 751.
- [ ] Explain frontend/backend responsibilities and identify common tools in each category.
- [ ] Configure a valid `[build-system]` and `[project]` for a small package.
- [ ] Explain mandatory and optional PEP 517 hooks and why hook call sequences can vary.
- [ ] Explain build isolation, build requirements, constraints, and the risks of disabling isolation.
- [ ] Choose a backend for pure Python, Rust, or C/C++ based on actual requirements.
- [ ] Configure metadata, extras, dependency groups, license files, dynamic versions, and package data appropriately.
- [ ] Explain PEP 660 editable installs and why they do not replace wheel tests.
- [ ] Build and inspect both a wheel and sdist, then rebuild a wheel from the sdist.
- [ ] Explain `SOURCE_DATE_EPOCH` and the limits of reproducibility claims.
- [ ] Describe a conservative migration path from setuptools or Poetry-based configuration.
- [ ] Explain why `uv.lock` and `pylock.toml` are not interchangeable by assumption.
- [ ] Treat source builds as executable code and distinguish build isolation from sandboxing.
- [ ] Validate the wheel in a clean environment and verify required package data is present.

## 20. Authoritative references

Prefer standards and the Python Packaging User Guide over old blog posts. Tool behavior changes, so consult the documentation for the installed version when a command or configuration option differs.

- [PEP 517 — A build-system independent format for source trees](https://peps.python.org/pep-0517/)
- [PEP 518 — Specifying Minimum Build System Requirements for Python Projects](https://peps.python.org/pep-0518/)
- [PEP 621 — Storing project metadata in `pyproject.toml`](https://peps.python.org/pep-0621/)
- [PEP 660 — Editable installs for pyproject.toml based builds](https://peps.python.org/pep-0660/)
- [PEP 639 — Improving License Clarity with Better Package Metadata](https://peps.python.org/pep-0639/)
- [PEP 735 — Dependency Groups in `pyproject.toml`](https://peps.python.org/pep-0735/)
- [PEP 751 — A file format to record Python dependencies for installation reproducibility](https://peps.python.org/pep-0751/)
- [PyPA: `pyproject.toml` specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [PyPA: Declaring project metadata](https://packaging.python.org/en/latest/specifications/declaring-project-metadata/)
- [PyPA: Build system interface](https://packaging.python.org/en/latest/specifications/build-system/)
- [PyPA: Source distribution format](https://packaging.python.org/en/latest/specifications/source-distribution-format/)
- [PyPA: Binary distribution format (wheel)](https://packaging.python.org/en/latest/specifications/binary-distribution-format/)
- [PyPA: License expression specification](https://packaging.python.org/en/latest/specifications/license-expression/)
- [PyPA: `pylock.toml` specification](https://packaging.python.org/en/latest/specifications/pylock-toml/)
- [Hatchling documentation](https://hatch.pypa.io/latest/)
- [setuptools documentation](https://setuptools.pypa.io/en/latest/)
- [Flit documentation](https://flit.pypa.io/en/stable/)
- [PDM backend documentation](https://backend.pdm-project.org/)
- [maturin user guide](https://www.maturin.rs/)
- [scikit-build-core documentation](https://scikit-build-core.readthedocs.io/en/latest/)
- [`build` frontend documentation](https://build.pypa.io/en/stable/)
- [uv documentation](https://docs.astral.sh/uv/)
- [Twine documentation](https://twine.readthedocs.io/en/stable/)
- [check-wheel-contents](https://github.com/jwodder/check-wheel-contents)
- [validate-pyproject](https://validate-pyproject.readthedocs.io/en/latest/)

---

**Lesson complete.** The core habit to retain is simple: declare the build system, build both artifacts, inspect what actually shipped, and test the installed wheel in a clean environment.
