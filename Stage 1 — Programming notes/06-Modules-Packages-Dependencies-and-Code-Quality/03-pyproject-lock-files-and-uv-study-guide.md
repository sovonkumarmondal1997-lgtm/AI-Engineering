# 03 — `pyproject.toml`, Lock Files, and `uv`
## Complete Chapter Summary, Project-Tree Review, Exercises, and Review Answers

**Roadmap:** Stage 1 · Module 1.6 · Lesson 03  
**Prerequisites:** Imports, Modules, and `__main__`; Project Layout and Package Structure  
**Source lesson:** `03-pyproject-lock-files-and-uv.md`

---

# Part A — Complete Chapter Summary

## 1. What dependency management solves

A **dependency** is third-party code that your project needs but does not implement itself. For example:

```python
import requests
```

Your program can import `requests` only if that package is installed in the Python environment running the program.

There are two important categories:

- **Direct dependency:** your project explicitly needs and declares it. `requests` is direct if your own application uses it.
- **Transitive dependency:** a package required by one of your direct dependencies. For example, `requests` relies on packages such as `urllib3`, `certifi`, `idna`, and `charset-normalizer`. Your application may never import those packages directly, but they are still required for the complete dependency graph.

```text
your project
    └── requests                 direct
          ├── urllib3            transitive
          ├── certifi            transitive
          ├── idna               transitive
          └── charset-normalizer transitive
```

Normally, declare the packages your own project directly depends on. Let the resolver discover and manage the transitive dependencies from each package's metadata. Manually listing every transitive dependency duplicates information and can become incorrect when a direct dependency changes its requirements.

Third-party packages save engineering effort, but they also introduce code that your project must track, update, and trust.

### Why unmanaged dependencies are dangerous

Imagine two developers install `pandas` at different times. One has version 2.1; the other installs version 2.8. Their source code is identical, but their environments differ. This can cause:

- **Works on my machine:** one developer's code runs while another's fails.
- **Version drift:** packages change over time without a corresponding source-code change.
- **Missing dependencies:** someone installs a package manually and forgets to record it.
- **Deployment mismatch:** production does not know which versions were tested.
- **Poor bug reproduction:** developers cannot recreate the production dependency set.
- **Security uncertainty:** it is difficult to identify and update vulnerable direct or transitive packages.

Dependency management creates a shared, machine-readable description of what a project needs and which exact versions were selected.

## 2. The core dependency-management model

```text
pyproject.toml
    ↓
Declared project requirements
    ↓
Dependency resolver
    ↓
Compatible, resolved dependency graph
    ↓
uv.lock
    ↓
Virtual environment
    ↓
Installed packages used by the application
```

Remember the central distinction:

- **`pyproject.toml` describes what the project requires.** It is the project's declaration of intent.
- **`uv.lock` records the exact dependency versions resolved to satisfy those requirements.** It is the reproducible result of resolution.
- **The virtual environment contains the packages actually installed.**

The project file is not a substitute for the lock file. The lock file is not a substitute for the project file. They have different responsibilities.

## 3. What `pyproject.toml` is

`pyproject.toml` is a standardized Python project configuration file written in TOML. It belongs at the project root, beside directories such as `src/` and `tests/`.

It is more than a dependency list. It can contain:

1. Project metadata.
2. Runtime dependency declarations.
3. Optional dependencies (extras).
4. Build-system configuration.
5. Tool configuration for formatters, linters, type checkers, and other tools.

A basic example:

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Example project"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.0",
]
```

### TOML syntax

TOML is a configuration format, not Python code.

- `[project]` starts a table (a named group of settings).
- `name = "my-project"` assigns a string value to a key.
- Strings are quoted.
- Arrays use square brackets and comma-separated values.
- A version expression such as `">=3.12"` is still a string in TOML. Packaging tools interpret its version meaning.

The common `[project]` fields are:

| Field | Purpose |
|---|---|
| `name` | Project's distribution name |
| `version` | Project's version |
| `description` | Short description |
| `readme` | README file used as long project description when packaged |
| `requires-python` | Supported Python version range |
| `dependencies` | Direct runtime dependencies |
| `optional-dependencies` | Named opt-in feature dependencies |

Example:

```toml
[project]
name = "orders-report"
version = "0.1.0"
description = "Validate and summarize order CSV files."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31,<3.0",
]
```

Metadata matters operationally: installation tools use the name and version, Python compatibility can be checked before installation, and the README can become part of the published package metadata.

## 4. Python version requirements

```toml
[project]
requires-python = ">=3.12"
```

This says the project supports Python 3.12 and later. It is a compatibility declaration, not an instruction to install Python 3.12. The actual interpreter used to create the environment is a separate concern.

A bounded example:

```toml
requires-python = ">=3.10,<3.13"
```

This allows Python 3.10, 3.11, and 3.12, but excludes 3.13 and later. Declare versions that the project is actually designed and tested to support. Otherwise an incompatible interpreter may accept installation and fail later during execution.

## 5. Declaring dependencies and choosing version constraints

A dependency declaration combines a package name with an optional version specifier:

```toml
[project]
dependencies = [
    "requests>=2.0",
    "pydantic>=2.0,<3.0",
]
```

Common operators:

| Operator | Meaning | Example |
|---|---|---|
| `>=` | This version or newer | `requests>=2.0` |
| `>` | Strictly newer | `requests>2.0` |
| `==` | Exact version pin | `requests==2.31.0` |
| `<=` | This version or older | `requests<=2.31.0` |
| `<` | Strictly older | `requests<3.0` |
| `~=` | Compatible-release range | `requests~=2.31` |

Multiple comma-separated constraints mean **all constraints must hold**:

```text
requests>=2.0,<3.0
```

This permits versions from 2.0 up to, but not including, 3.0.

Four strategies:

- **Exact pin (`==2.31.0`):** no version flexibility. Useful when a specific version is deliberately required, but routine updates require a declaration change.
- **Minimum (`>=2.0`):** flexible, but permits future major releases that may introduce breaking changes.
- **Bounded range (`>=2.0,<3.0`):** practical middle ground when compatibility with the 2.x series has been established.
- **Compatible release (`~=2.31`):** permits compatible updates within the specified compatibility boundary. The number of version segments matters: `~=2.31` permits later 2.x versions below 3.0; `~=2.31.0` is narrower, below 2.32.

For many applications, a bounded range is a sensible starting point. The lock file, rather than manually exact-pinning every transitive dependency in `pyproject.toml`, records the actual selected versions.

## 6. Dependency resolution and conflicts

A **dependency resolver** examines direct requirements and all transitive requirements, then finds one exact version for each package that satisfies every constraint simultaneously.

A valid example:

```text
your project requires A >= 2
A requires B < 5
your project also requires C
C requires B >= 4
```

Both packages require a compatible `B` in the overlap `[4, 5)`. A resolver can select a version in that range.

A genuine conflict:

```text
A requires B < 5
C requires B >= 6
```

No version can be both below 5 and at least 6. Resolution must fail because no valid solution exists.

A systematic diagnosis:

1. Read the resolver error and identify the packages and constraints it names.
2. Identify which direct dependencies introduced those transitive constraints.
3. Check whether another version of one direct dependency relaxes the conflict.
4. Review whether your own constraints are unnecessarily restrictive.
5. Replace a genuinely incompatible dependency if no valid combination exists.

Do not force an arbitrary installation around a real conflict. It can produce an environment that appears installed but violates a package's declared compatibility assumptions, leading to subtle runtime failures.

## 7. Virtual environments

A **virtual environment** is an isolated Python environment with its own installed packages. Each project can have its own versions without changing the system Python or interfering with another project.

For example:

```text
Project A environment: library-x 1.x
Project B environment: library-x 2.x
System Python:          not polluted by either project
```

Without isolation, projects share one global package installation and can require incompatible versions. This chapter uses `uv` to manage the environment, so you generally do not need to manually create and activate it as a separate step.

## 8. Lock files and `uv.lock`

A **lock file** is a generated record of the exact versions selected by the resolver for the dependency graph, including direct and transitive dependencies.

Example concept:

```text
pyproject.toml: requests>=2.0

uv.lock:
requests == 2.31.0
urllib3  == 2.0.7
certifi  == <resolved version>
...
```

The lock file may contain multiple package variants with environment markers when different supported Python versions or platforms require different builds or versions.

| Question | `pyproject.toml` | `uv.lock` |
|---|---|---|
| Main purpose | Declares requirements | Records resolved versions |
| Typical author | Developer or `uv` command | `uv` |
| Version ranges | Yes | No; records exact resolutions |
| Transitive graph | Declares direct requirements | Records full resolved graph |
| Project metadata | Yes | No |
| Hand-edit? | Yes, when necessary; then re-lock | No |
| Version control | Commit it | Commit for applications; useful for library development too |

The lock file makes **dependency selection** reproducible for the supported environments. It does not guarantee identical program execution across every machine. Python version, operating system, native libraries, environment variables, external services, and build artifacts can still differ.

Do not hand-edit `uv.lock`. Change the declaration or use a `uv` command, then let the resolver regenerate the lock.

### Why lock files matter

Without a lock file, the same flexible declaration may resolve to different package versions at different dates. With a committed lock file, developers, CI, containers, and production can install the same resolved versions for their supported environment. This makes bugs easier to reproduce and reduces the chance of CI and production silently using different dependency sets.

## 9. What `uv` is

`uv` is a Python project and package manager. It can initialize projects, manage dependencies, resolve versions, generate lock files, manage virtual environments, and run commands in the project's environment.

Important distinction:

- `pyproject.toml` is a Python packaging **standard**.
- `uv` is a particular **tool** that works with that standard and provides additional environment and workflow features.

`pyproject.toml` is not a proprietary `uv` file.

Check the installed tool:

```bash
uv --version
```

If the shell reports that the command is not found, `uv` may not be installed or may not be on the shell's `PATH`. Installation instructions can change, so use the current official instructions for your operating system. Check available commands and flags with `uv --help` and the relevant subcommand's help.

## 10. Initializing a project

```bash
uv init my-project
cd my-project
```

`uv init` creates a starter project structure and a basic `pyproject.toml`. The exact generated files and flags can vary by `uv` version. Do not assume every invocation creates a `src/` package or a `cli.py`; inspect the generated files and use:

```bash
uv init --help
```

## 11. Adding runtime dependencies

```bash
uv add requests
```

In the normal workflow this command:

1. Adds `requests` to the project's runtime dependencies in `pyproject.toml`.
2. Resolves its full dependency graph.
3. Creates or updates `uv.lock` with exact versions.
4. Synchronizes the project's environment.

A constraint can be specified explicitly:

```bash
uv add "requests>=2.31,<3.0"
```

This records the chosen requirement range rather than an unconstrained package name.

## 12. Development dependencies

Runtime dependencies are needed to run the application in production. Development dependencies are tools needed to build, test, lint, or type-check the project.

```bash
uv add --dev pytest ruff mypy
```

This typically creates or updates a development group:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.5",
    "mypy>=1.10",
]
```

Keep these separate from runtime dependencies. Production does not need a test runner or type checker merely to run the application. Excluding development packages reduces deployment size, maintenance, and unnecessary dependency exposure.

## 13. Optional dependencies (extras)

Extras are opt-in dependencies for optional product features. They are declared in `[project.optional-dependencies]`:

```toml
[project]
name = "orders-report"
dependencies = [
    "requests>=2.31,<3.0",
]

[project.optional-dependencies]
excel = ["openpyxl>=3.0"]
```

A normal installation uses the base runtime dependency. A user who needs the Excel feature can request the `excel` extra using the installation tool's extra-selection syntax.

Do not confuse extras with development groups:

- `[dependency-groups].dev`: tools for developing the project.
- `[project.optional-dependencies]`: opt-in features offered to users of the project.

## 14. Synchronizing the environment: `uv sync`

```bash
uv sync
```

`uv sync` checks the project and lock state, updates the lock if necessary, and aligns the virtual environment with it. It installs missing packages and removes extraneous packages so the environment matches the project's selected dependency state.

Strict mode:

```bash
uv sync --locked
```

This uses the existing lock file and fails if it is stale instead of silently updating it. `--frozen` is stricter in a different way: it skips checking whether the lock is up to date.

Typical patterns:

```bash
uv sync                       # local development; dev group included
uv sync --locked              # CI; fail if lock is stale
uv sync --locked --no-dev     # production dependencies only
```

Run `uv sync` after cloning a project, after pulling dependency-file changes, or when you need to restore the environment to the locked state.

## 15. Running commands: `uv run`

```bash
uv run python app.py
uv run pytest
```

`uv run` runs the command in the project's managed environment, without requiring you to activate it manually. A bare `python app.py` might use a different interpreter or environment and therefore have missing or incompatible packages.

`uv run` normally ensures the project/lock environment is up to date and may update the lock if declarations changed. When a command must use the lock exactly as committed:

```bash
uv run --locked pytest
```

Use `uv run` for project commands so the correct interpreter and dependencies are selected consistently.

## 16. Adding, removing, locking, and updating

Core lifecycle commands:

```bash
uv add requests          # declare a runtime dependency and resolve it
uv add --dev pytest      # declare a development dependency
uv remove requests      # remove a dependency and update the lock
uv lock                 # re-resolve and update uv.lock; does not install packages
uv sync                 # synchronize installed environment to the lock
```

Keep four operations distinct:

1. **Declare:** specify a package and constraint in `pyproject.toml`.
2. **Resolve:** find compatible exact versions across the full graph.
3. **Lock:** record those versions in `uv.lock`.
4. **Install/sync:** place those versions into the environment.

Editing `pyproject.toml` manually does not itself update `uv.lock` or install anything. Run `uv lock` or `uv sync` afterward.

A controlled update workflow:

```bash
git status
uv lock --upgrade-package requests
git diff uv.lock
uv sync --locked
uv run pytest
git add uv.lock
git commit -m "Update requests"
```

This example upgrades one package and whatever needs to change with it. `uv lock --upgrade` can update all packages allowed by the constraints, creating a larger change to review. Confirm flags with your installed version's help. Review the lock diff and run tests before committing.

## 17. Reproducible development, CI/CD, and containers

A reproducible workflow uses the same committed dependency declarations and lock file:

```text
pyproject.toml + uv.lock in version control
                 ↓
              uv sync
                 ↓
      locked versions installed locally
                 ↓
      same lock used by CI and deployment
```

A new developer can clone the repository and run:

```bash
git clone <repository>
cd <repository>
uv sync
uv run pytest
```

CI should install from the committed lock strictly:

```bash
uv sync --locked
uv run --locked pytest
uv run --locked ruff check .
uv run --locked mypy .
```

This prevents CI from silently re-locking a stale file and testing against a different dependency set.

A conceptual container build follows the same rule:

```text
copy pyproject.toml and uv.lock
          ↓
uv sync --locked --no-dev
          ↓
copy application source
          ↓
build final image
```

Production images generally exclude development dependencies. This chapter explains the dependency-management principle; it does not teach writing a full Dockerfile.

## 18. Application versus library strategy

An **application** is deployed and run as a whole unit by your team. Commit its `uv.lock` so developers, CI, containers, and production use the same resolved versions.

A **library** is installed inside other people's projects. Its consumers resolve its declared version ranges alongside their own dependencies. Therefore, a library should generally declare sensible compatibility ranges rather than forcing consumers to use one exact dependency version. The library may still keep a lock file for its own development and CI, but consumers do not use that lock file to resolve their projects.

This is a practical distinction, not an absolute law: choose based on who owns the deployment and who performs dependency resolution.

## 19. Dependency security

A vulnerable transitive dependency matters even if your code never imports it directly. Before adding a package, consider whether it is maintained, trusted, widely used, and whether its dependency footprint is justified.

There are two bad extremes:

- **Blindly upgrading everything:** can introduce breaking changes or newly introduced vulnerabilities without review.
- **Never updating:** leaves known vulnerabilities unpatched and allows dependencies to become increasingly outdated.

The sensible approach is periodic, deliberate updates: inspect the `uv.lock` diff, understand what changed, run tests and quality checks, and commit the reviewed result.

## 20. Common dependency-management mistakes

1. Installing project packages globally and polluting system Python.
2. Failing to isolate each project's dependencies.
3. Editing `uv.lock` by hand.
4. Committing `pyproject.toml` and `uv.lock` in inconsistent states.
5. Editing project requirements without re-locking.
6. Ignoring genuine resolver conflicts.
7. Using unconstrained version declarations without considering compatibility.
8. Manually exact-pinning every transitive dependency.
9. Declaring packages that are only transitive instead of declaring actual direct requirements.
10. Installing packages manually without recording them through the project.
11. Trusting a local environment assembled through undocumented manual installs.
12. Running project commands with the wrong Python interpreter instead of using `uv run`.

The general fix is to make `pyproject.toml` and `uv.lock` authoritative, use `uv` commands for dependency changes, isolate environments, and verify the lock in CI.

## 21. The 15 progressive coding/CLI examples

The lesson's progressive examples build from a simple import to reproducible CI:

1. **Dependency import:** `import requests` requires the third-party package to be installed.
2. **Minimal project metadata:** `[project]`, `name`, and `version`.
3. **Python compatibility:** add `requires-python = ">=3.12"`.
4. **Declare a dependency:** add `"requests>=2.0"` to `dependencies`.
5. **Bound the version:** use `"requests>=2.31,<3.0"`.
6. **Read a dependency graph:** `demo → requests → urllib3, certifi, idna, charset-normalizer`; the lock records all resolved packages.
7. **Initialize:** `uv init demo` then `cd demo`; generated files vary by version.
8. **Add runtime package:** `uv add requests`.
9. **Add development tools:** `uv add --dev pytest ruff mypy`.
10. **Synchronize:** `uv sync` to align the environment with the lock.
11. **Run inside environment:** `uv run python -m demo.cli` and `uv run pytest`. The module command assumes a `demo` package with `cli.py` exists and is importable; a starter `main.py` may instead be run with `uv run python main.py`.
12. **Remove and update:** `uv remove requests`, then `uv add "requests>=2.32"`.
13. **Understand lock contents:** a conceptual entry records names and exact versions for both direct and transitive packages; the real format also includes environment-specific data.
14. **Fresh-machine setup:** `git clone`, `cd`, `uv sync`, `uv run pytest`.
15. **CI workflow:** `uv sync --locked`, then `uv run --locked pytest`, `ruff`, and `mypy`.

## 22. Mini-project — reproducible `orders-report` CLI

The lesson extends the previous project-layout lesson by adding dependency management to the same CSV-to-JSON reporting application.

```text
orders-report/
├── src/
│   └── orders_report/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── logging_config.py
│       ├── validation.py
│       └── processing.py
├── tests/
│   ├── test_validation.py
│   └── test_processing.py
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

Example `pyproject.toml`:

```toml
[project]
name = "orders-report"
version = "0.1.0"
description = "Validate order CSV files and produce a JSON summary."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0,<3.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.5",
    "mypy>=1.10",
]
```

- `pydantic` is a runtime dependency in this example.
- `pytest`, `ruff`, and `mypy` are development dependencies.
- `[build-system]` identifies the build backend. With a valid package/build configuration, `uv sync` can install the project itself (editable by default), allowing the `src/orders_report` package to be imported. Having dependencies installed is not the same as having your own `src/` package installed.
- `uv.lock` is generated from the declared requirements and committed for reproducibility.

Fresh setup:

```bash
git clone <repository-url> orders-report
cd orders-report
uv sync
```

Run the application:

```bash
uv run python -m orders_report.cli --input-dir data/raw --output summary.json
uv run python -m orders_report.cli --help
```

Run tests:

```bash
uv run pytest
```

Strict CI:

```bash
uv sync --locked
uv run --locked pytest
uv run --locked ruff check .
uv run --locked mypy .
```

Production/container setup:

```bash
uv sync --locked --no-dev
```

The key engineering result is that the same resolved dependency set is used for development, CI, and deployment, while production excludes tools used only during development.

---

# Part B — Project-Tree and Current-Level Assessment

## 1. Roadmap context

Your Stage 1 roadmap contains 24 modules, 212 numbered lessons, and 282 files. The four Stage 1 projects are:

1. Personal Expense Ledger CLI.
2. Log Investigation and Reliability CLI.
3. Data Quality and Transformation Pipeline (`orders.csv`, `dqpipe` package with CLI, configuration, pipeline, rules, tests, and a data contract).
4. Rule-Based Risk Review Engine (`transactions.csv`, `rules.toml`, `riskreview` package with CLI, engine, I/O, models, rules, tests, and golden decision data).

You have completed the foundations in Module 03 (control flow, functions, scope, side effects, exceptions, and validation), Module 04 (collections, problem-solving, and algorithmic habits), and Module 05 Lessons 01–09 (files, paths, CSV, JSON, encodings, CLI arguments, streams/exit codes, logging, environment configuration, and input validation).

Within Module 1.6, the previous lessons covered:

- Lesson 01: Imports, Modules, and `__main__`.
- Lesson 02: Project Layout and Package Structure.
- Current lesson: `pyproject.toml`, Lock Files, and `uv`.

## 2. Current level

Your current level is **beginner progressing toward intermediate** in Python engineering. You already have the core programming and CLI knowledge needed for this lesson. You understand file processing, command-line interfaces, configuration, logging, validation, module imports, and package structure.

This lesson adds project-level dependency engineering:

- Declare what a project needs.
- Distinguish direct and transitive packages.
- Resolve version constraints.
- Isolate dependencies.
- Lock exact versions.
- Reproduce environments across developers, CI, and deployment.

The exercise solutions stay within the lesson and its prerequisites. They use TOML examples, shell commands, dependency graphs, and the Python project architecture already studied. They do not introduce advanced packaging internals, Dockerfile implementation, or unrelated frameworks.

---

# Part C — All 14 Formal Exercises Solved

## Beginner

### 1. Identify direct and transitive dependencies

- `requests` is **direct** because your project imports and uses it.
- `urllib3` is **transitive** because `requests` requires it, even though your project does not import it directly.

### 2. Explain the `widget-tool` metadata

```toml
[project]
name = "widget-tool"
version = "1.2.0"
requires-python = ">=3.11"
dependencies = ["click>=8.0,<9.0"]
```

- `[project]` begins the project metadata table.
- `name` identifies the project.
- `version` is the project's own version.
- `requires-python` means Python 3.11 or newer.
- `dependencies` declares `click` as a runtime dependency.
- `click>=8.0,<9.0` permits 8.x versions from 8.0 onward, but excludes 9.0.

### 3. Distinguish `pyproject.toml` and `uv.lock`

`pyproject.toml` declares the project's requirements, often using flexible version ranges. `uv.lock` records the exact versions the resolver selected for the complete dependency graph, including transitive dependencies, so installations can reproduce that selection.

### 4. Explain `uv sync`

`uv sync` checks the project and lock state, updates the lock if required, and installs/removes packages so the project's virtual environment matches the locked dependency set. Use `uv sync --locked` when the lock must not be changed and a stale lock should cause an error.

## Intermediate

### 5. Add `httpx` as a runtime dependency, minimum 0.27

```bash
uv add "httpx>=0.27"
```

This declares `httpx` in runtime dependencies and resolves/locks it.

### 6. Add `pytest` as a development dependency

```bash
uv add --dev pytest
```

This places `pytest` in the development dependency group rather than the runtime dependency list.

### 7. Determine whether the constraints conflict

Given:

```text
A requires B < 5
C requires B >= 3
```

There is no conflict. Both constraints are true for versions in `[3, 5)`. For example, `B == 4.0` satisfies both.

### 8. Compare `python app.py` and `uv run python app.py`

- `python app.py` uses whichever interpreter/environment the shell resolves as `python`; it might not contain this project's dependencies.
- `uv run python app.py` runs in the project's managed environment.

Use `uv run` for project commands because it selects the intended environment and dependency set.

### 9. `dependencies` versus `optional-dependencies`

- `dependencies` contains packages required by the base application.
- `optional-dependencies` contains named extras for opt-in features, such as Excel export requiring `openpyxl`.

Development tools belong in `[dependency-groups]`, not in optional feature extras.

## Advanced

### 10. Design reproducible onboarding

```bash
git clone <repository>
cd <repository>
uv sync
uv run pytest
```

Line by line:

1. `git clone` retrieves the project, including its committed `pyproject.toml` and `uv.lock`.
2. `cd` enters the project root so `uv` finds the project configuration.
3. `uv sync` creates/updates the managed environment to match the lock.
4. `uv run pytest` runs the tests in that environment.

This reproduces the locked dependency versions for the same supported platform and Python environment. It does not guarantee identical execution across all operating systems or external services.

### 11. Explain why hand-editing `uv.lock` is risky and how to update correctly

`uv.lock` is a generated resolution of the entire dependency graph. Changing one version manually can make the graph inconsistent with the constraints and other packages. The resolver has not verified the hand-edited result.

Correct approach:

```bash
uv lock --upgrade-package package-name
git diff uv.lock
uv sync --locked
uv run pytest
```

1. Ask `uv` to update the selected package and any dependencies that need to change.
2. Review the generated lock-file diff.
3. Install the exact new lock.
4. Run tests.
5. Commit only after the change is understood and validated.

If the declaration itself needs a new range, change it through `uv add` or edit `pyproject.toml`, then re-lock.

### 12. Choose strategies for an application and a library

**(a) Internal CLI application**

- Declare deliberate, tested version ranges for direct dependencies.
- Commit `uv.lock`.
- Use `uv sync --locked` in CI and deployment.
- Reason: your team controls the deployed environment and wants it to match the tested environment.

**(b) Published library**

- Declare sensible compatibility ranges rather than exact-pinning every dependency for consumers.
- A lock file may be kept for the library team's own development and CI.
- Reason: consumers resolve the library alongside their own dependencies; an exact pin can unnecessarily conflict with their project.

### 13. Diagnose a resolver conflict systematically

1. Read the error to identify the shared package and conflicting constraints.
2. Trace each constraint back to the direct dependency that introduced it.
3. Check whether a different version of one direct dependency has compatible transitive requirements.
4. Review whether your own version ranges are unnecessarily strict.
5. If no compatible solution exists, replace one of the incompatible dependencies.

Do not force an install that violates the declared constraints. That hides the problem instead of solving it.

### 14. Design the dependency-installation stage of CI

```bash
uv sync --locked
uv run --locked pytest
uv run --locked ruff check .
uv run --locked mypy .
```

- `uv sync --locked` installs the committed resolution and fails if the lock is stale.
- `uv run --locked pytest` tests with the same locked environment.
- `ruff check .` checks code quality in that environment.
- `mypy .` runs type checks in that environment.

The order matters: synchronize first, then run quality checks. Strict lock handling prevents CI from silently generating a different dependency solution.

---

# Part D — All 10 Debugging Scenarios

1. **Dependency cannot be resolved:** identify the conflicting transitive constraints from the error; upgrade/downgrade a direct dependency or replace an incompatible package.
2. **Package installed but not declared:** if genuinely required, add it with `uv add`; if not, do not depend on it. A clean sync will not preserve an undocumented manual installation.
3. **Works locally but fails in a clean environment:** recreate with `uv sync` in a fresh environment; find the missing undeclared package and add it properly.
4. **Project package cannot be imported under `uv run`:** verify the package itself is installed, not just its dependencies. For a `src/` project, inspect `[build-system]`, package discovery, and the current `uv` project-install behaviour.
5. **`pyproject.toml` changed but environment is stale:** run `uv lock` followed by `uv sync`, or plain `uv sync` to re-lock and synchronize.
6. **Lock and project files are current but installed environment differs:** run `uv sync` to reconcile manually introduced or stale packages with the lock.
7. **Lock conflict after merging branches:** merge the intended `pyproject.toml` declarations, then regenerate `uv.lock` with `uv lock` or `uv sync`. Do not hand-merge generated lock contents.
8. **`pytest` is missing:** declare it with `uv add --dev pytest`, then synchronize/run again.
9. **`uv run` works but bare Python fails:** compare `sys.executable` and `sys.path`; the commands are likely using different interpreters/environments. Use `uv run` consistently.
10. **Updating one dependency changes several transitive packages:** inspect the lock diff. This can be expected because the updated package may require new versions of its own dependencies. Test and review before committing.

---

# Part E — All 20 Interview and Architecture Answers

1. **Dependency:** external code required by a project. Direct dependencies are declared by the project; transitive dependencies are required by those direct packages.
2. **`pyproject.toml`:** standardized project configuration containing metadata, dependencies, build settings, and tool configuration.
3. **`requires-python`:** declares supported Python versions so incompatible interpreters can be rejected early.
4. **Version specifiers:** `>=2.0` means 2.0 or newer; `==2.0` means exactly 2.0; `>=2.0,<3.0` means the compatible range below 3.0.
5. **Resolver:** finds one set of exact package versions satisfying all direct and transitive constraints.
6. **Resolution failure:** occurs when constraints have no overlap, such as `B<5` and `B>=6`. Forcing installation can create an incompatible environment.
7. **Virtual environment:** isolated package installation for one project; it prevents incompatible projects from sharing one global dependency set.
8. **Lock file:** generated exact record of the resolved dependency graph, used to reproduce dependency selection.
9. **`pyproject.toml` vs `uv.lock`:** declaration of requirements versus generated record of exact resolved versions.
10. **`uv` vs standard:** `pyproject.toml` is a standard; `uv` is a tool that reads/writes it and manages environments, resolution, locking, and command execution.
11. **`uv init`:** creates a starter project and basic metadata file; exact generated structure varies by version.
12. **`uv add requests`:** declares the package, resolves direct/transitive requirements, updates `uv.lock`, and normally syncs the environment.
13. **`uv sync`:** ensures lock state is usable/current and aligns installed packages with it; use after clone or dependency changes.
14. **`uv run`:** runs a command in the project's managed environment rather than whichever Python happens to be active in the shell.
15. **`uv lock` vs `uv sync`:** `uv lock` re-resolves and writes the lock without installing; `uv sync` installs/alines the environment to the lock.
16. **Development dependency:** add with `uv add --dev <package>`; tests and linters are not runtime requirements and should not burden production.
17. **Extras:** named optional dependencies for optional user-facing features; they differ from development dependency groups.
18. **Reproducibility:** a committed lock ensures local development, CI, and deployment use the same resolved dependency versions for their supported environments.
19. **Application vs library:** applications benefit from a committed lock for deployment; libraries should publish compatible dependency ranges because consumers resolve them with their own requirements.
20. **Dependency security:** blind upgrades risk breaking changes; never updating leaves vulnerabilities unpatched. Review and update periodically, inspect lock diffs, and test.

---

# Part F — All 7 Knowledge-Check Answers

1. **Why isn't `pyproject.toml` alone enough for reproducibility?** Its version ranges can resolve to different exact versions at different dates. A lock file records one exact resolution.
2. **Why does `uv` manage virtual environments?** It removes manual environment creation/activation steps and reduces the chance of installing into the wrong interpreter.
3. **Interpret the Python/click constraints:**

   ```toml
   [project]
   name = "tool"
   version = "2.0.0"
   requires-python = ">=3.10,<3.13"
   dependencies = ["click>=8.1"]
   ```

   Python 3.10, 3.11, and 3.12 are supported; Python 3.13 is excluded. `click` 8.1 or newer is permitted, with no upper bound stated.

4. **Find the overlap:** `X>=1.0,<2.0` and `X>=1.5,<2.5` overlap at `[1.5,2.0)`. Any version in that range satisfies both.
5. **After `uv add "flask>=3.0"`:** `pyproject.toml` gains the declared Flask requirement; `uv.lock` gains Flask's exact resolved version and any required transitive package changes.
6. **CI reports a resolution error despite claiming to use the same lock:** first verify it really runs `uv sync --locked` against the committed `uv.lock`, not plain `uv sync`, a stale cache, or a fresh independent resolution. Also verify the checked-out files are the expected commit.
7. **Commit lock for an internal script or a library?** Commit it for the internal application because it controls its own deployment and benefits from reproducible installs. A library may keep a lock for its own development/CI, but consumers rely on its declared version ranges, not its development lock.

---

# Final Production Mastery Checklist

- [ ] `pyproject.toml` is at the project root with accurate metadata.
- [ ] `requires-python` matches the Python versions actually tested.
- [ ] Every required direct runtime dependency is declared.
- [ ] Direct and transitive dependencies are understood.
- [ ] Version constraints are deliberate and not blindly broad or exact-pinned.
- [ ] Resolver conflicts are fixed at the constraint/dependency level.
- [ ] `uv.lock` is committed for application projects and kept consistent with `pyproject.toml`.
- [ ] `uv.lock` is never edited by hand.
- [ ] Virtual environments are isolated and not replaced by global installs.
- [ ] Development tools are in a development dependency group.
- [ ] Optional user-facing features use extras.
- [ ] Production sync excludes development dependencies.
- [ ] Secrets are not stored in `pyproject.toml` or `uv.lock`.
- [ ] CI uses `uv sync --locked` and runs tools with `uv run --locked`.
- [ ] Dependency updates are reviewed, tested, and committed deliberately.
- [ ] Direct and transitive dependencies are reviewed for security and maintenance.

**Core engineering principle:** `pyproject.toml` declares the project's dependency intent, `uv.lock` records the exact resolved dependency graph, and `uv sync` makes the installed environment match that record. Use the same committed lock across development, CI, and deployment to make dependency selection reproducible.
