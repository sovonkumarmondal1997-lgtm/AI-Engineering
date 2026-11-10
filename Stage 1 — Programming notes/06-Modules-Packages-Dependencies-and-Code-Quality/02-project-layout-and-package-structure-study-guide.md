# 02 — Project Layout and Package Structure
## Complete Chapter Summary, Roadmap Review, and Exercise Solutions

**Roadmap:** Stage 1 · Module 1.6 · Lesson 02  
**Prerequisite:** `01-imports-modules-and-main.md` and Module 1.5 CLI/data-processing foundations  
**Source:** `02-project-layout-and-package-structure.md`

---

# Part A — Complete Chapter Summary

## 1. What project layout means

A **project** is the complete collection of files that make up a software application: source code, tests, configuration, documentation, and metadata. A **project layout** is the deliberate arrangement of those files and directories.

Layout is an engineering decision, not decoration. It affects:

- **Maintainability:** developers can find the code responsible for a behaviour.
- **Imports:** directory placement affects `sys.path`, package discovery, and import resolution.
- **Testing:** business logic can be tested without invoking unrelated CLI or I/O code.
- **Collaboration:** reviewers and new contributors can understand where responsibilities belong.

For example, a 200-line `app.py` that parses a CSV, validates it, and prints a summary becomes hard to extend when a second input format is added. Separating CLI, validation, and processing gives each responsibility a predictable home.

## 2. File, module, package, project

These terms are related but not interchangeable:

- **File:** anything stored on disk, such as `notes.txt` or `utils.py`.
- **Module:** a named, importable unit of Python code with its own namespace. A `.py` file is the common form.
- **Package:** a directory grouping related modules under a namespace. A regular package conventionally contains `__init__.py`; a namespace package can omit it.
- **Project:** the entire repository: package(s), tests, configuration, documentation, and metadata.

```text
weather_cli/                 # project
├── src/
│   └── weather/              # package
│       ├── __init__.py
│       ├── cli.py             # module
│       └── forecasting.py    # module
├── tests/
│   └── test_forecasting.py
└── pyproject.toml
```

`tests/` and `pyproject.toml` are project contents, not application modules.

## 3. The simplest project

```text
my_project/
├── app.py
├── utils.py
└── data/
```

```python
# utils.py
def load_numbers(path):
    with open(path, encoding="utf-8") as handle:
        return [float(line) for line in handle]
```

```python
# app.py
from utils import load_numbers

def main() -> int:
    numbers = load_numbers("data/numbers.txt")
    print(sum(numbers))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

The files sit together, so `from utils import load_numbers` works when the script directory is on `sys.path`. This is appropriate for a tiny tool. As the project grows, generic top-level names such as `utils.py` can collide with other modules, and a flat root becomes cluttered.

## 4. Flat layout

```text
project/
├── package/
│   ├── __init__.py
│   ├── cli.py
│   └── utils.py
├── tests/
│   └── test_utils.py
├── pyproject.toml
└── README.md
```

The package is directly inside the project root.

**Advantages:** simple, familiar, fewer directories, suitable for small-to-medium projects and internal tools run from a checkout.

**Risk:** when commands run from the project root, that root is commonly on `sys.path`. Python can import the local, uninstalled `package/` directly. Tests may therefore pass against local source files even if the built/installed distribution accidentally omitted a file. This is called accidental local-import or packaging-test blindness.

Flat layout is not inherently wrong. It is often a sensible choice when the project is not meaningfully installed separately from its source checkout.

## 5. `src/` layout

```text
project/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── cli.py
│       └── utils.py
├── tests/
├── pyproject.toml
└── README.md
```

The package lives under `src/`, not directly at the project root. Running `import mypackage` from the project root does not normally work just because `src/mypackage` exists: Python does not automatically add `src/` to `sys.path`.

The preferred development solution is an **editable install**. Conceptually, the environment registers a pointer to the source package, so imports behave like an installed package while edits to source files are immediately reflected. The exact installation mechanics belong to the later packaging chapter.

Other deliberate path setups (such as adding `src/` to `PYTHONPATH`, IDE/test configuration, or running from inside `src/`) can also make it importable, but are not the preferred default.

**Benefits:** tests exercise the installed-package import path like a user would; accidental local imports are reduced; tests, scratch scripts, and documentation are clearly outside the shippable package.

| Consideration | Flat | `src/` |
|---|---|---|
| Setup | Simpler | One extra directory and usually an install |
| Local-import risk | Local package may be imported accidentally | Substantially reduced |
| Good fit | Internal/small tools | Distributable libraries and packaged CLI tools |

The correct choice depends on whether the project is meant to be installed and distributed. `src/` is a safer default for distributable packages, not a universal rule for every script.

## 6. Packages and subpackages

A package can contain modules directly and can contain nested packages called **subpackages**:

```text
mypackage/
├── __init__.py
├── module_a.py
├── module_b.py
└── subpackage/
    ├── __init__.py
    └── module_c.py
```

The import paths mirror the directory structure:

```python
from mypackage.module_a import something
from mypackage.subpackage.module_c import something_else
```

Subpackages create nested namespaces and keep related modules grouped. Each module should have a clear responsibility; create subpackages when related modules genuinely accumulate, not simply to make the tree look sophisticated.

## 7. `__init__.py` and the package API

An empty `__init__.py` is valid. It marks a regular package, and callers can import submodules explicitly:

```python
from mypackage.module_a import something
```

It can also re-export a curated public API:

```python
# mypackage/__init__.py
from .module_a import public_function
from .processing import process_data

__all__ = ["public_function", "process_data"]
```

Then users can write:

```python
from mypackage import public_function
```

Keep `__init__.py` empty or lightweight unless there is a deliberate public API to expose. Its top-level code executes when the package is first imported, so heavy work or side effects there affect imports of the entire package.

## 8. Public and private modules

A leading underscore communicates that a module or name is internal:

```text
mypackage/
├── __init__.py
├── processing.py
└── _internal_helpers.py
```

```python
# _internal_helpers.py
def _format_row(row):
    ...
```

This is a **convention**, not access control. Other code can still import `_internal_helpers`. The underscore tells maintainers that external callers should not depend on it and that it may change without compatibility guarantees.

A module without an underscore is not automatically part of the supported public API. The package's documented API determines what external users should rely on.

## 9. Responsibility boundaries

A common layered design is:

```text
CLI layer                       argparse, main(), streams, exit codes
    ↓
application/service layer       coordinates work and formats results
    ↓
domain/business logic           rules and computations; no CLI or I/O
    ↓
data/file layer                  reads/writes files, CSV, JSON, filesystem
```

A poor all-in-one `main.py` mixes argument parsing, file I/O, validation, business rules, and output. This makes isolated testing difficult and means a change to one concern can break another.

A better structure separates `cli.py`, `processing.py`, and `validators.py`. Each module has a single explainable responsibility and can be changed or tested independently.

## 10. Organizing a CLI application

The chapter maps Module 1.5 topics into a project:

```text
project/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── logging_config.py
│       ├── validation.py
│       └── processing.py
├── tests/
├── pyproject.toml
└── README.md
```

- `cli.py`: `argparse`, `main(argv) -> int`, `__main__` guard; the only module that needs CLI parsing and `sys.argv`.
- `config.py`: `AppConfig`, `build_config()`, configuration precedence; the only module reading `os.environ` directly.
- `logging_config.py`: centralized logging setup.
- `validation.py`: pure reusable validators, without I/O or CLI dependencies.
- `processing.py`: actual business work, depending on validated inputs rather than `argparse` or environment variables.

The intended dependency direction is from the CLI into the other modules. Lower-level modules must not import the CLI. This is the one-way dependency principle.

## 11. The `tests/` directory

Conventionally, `tests/` is a sibling of `src/` or the flat package, not inside the shipped package:

```text
project/
├── src/
│   └── app/
│       ├── validators.py
│       └── processing.py
└── tests/
    ├── test_validators.py
    └── test_processing.py
```

Tests verify application code; they are not normally part of the production package. Keeping them separate avoids shipping test files and makes source directories easier to navigate.

A common naming convention is `test_<module_name>.py`. Larger test trees can mirror source subpackages.

- **Unit test:** tests one small function/module in isolation, e.g. a validator with no file or CLI.
- **Integration-style test:** tests multiple parts working together, e.g. `main([...])` and its output/exit code.

These are organizational concepts here; the dedicated testing chapter covers the framework in depth.

## 12. `pyproject.toml`

`pyproject.toml` is the standard modern project metadata/configuration file, placed at the project root:

```toml
[project]
name = "app"
version = "0.1.0"
description = "A small data-processing CLI."
requires-python = ">=3.11"
```

At this chapter's level:

- `[project]` describes name, version, description, and Python requirement.
- A dependency declaration records third-party packages the project needs.
- Build configuration tells tools how to build an installable package.
- Tool-specific sections can configure linters, formatters, and type checkers.

It belongs at the root because it describes the whole project, including tests, documentation, and tools. Detailed dependency declarations, version pinning, lock files, and `uv` are deliberately deferred to later chapters.

## 13. Root-level documentation and metadata

Common root files:

- `README.md`: purpose, installation/run instructions, basic examples; the first orientation for users and contributors.
- `LICENSE`: legal terms for use, modification, and redistribution.
- `.gitignore`: patterns for untracked local/generated files such as build outputs, virtual environments, and `.env`.
- `pyproject.toml`: project metadata and tool/build configuration.

These belong at the root by convention because they govern or describe the project as a whole. `.gitignore` does not automatically untrack a file already tracked by Git.

## 14. Source, project, runtime configuration, and secrets

Keep four categories distinct:

| Category | Example | Typical location / version-control rule |
|---|---|---|
| Source code | `cli.py`, `processing.py` | `src/`; commit it |
| Project config | `pyproject.toml` | root; commit it |
| Runtime config | non-secret `config.yaml` | root or `config/`; commit only safe, environment-independent values/templates |
| Secrets/environment values | real API keys, `.env` | never commit real values; local `.env` is ignored; deployment secrets belong in the runtime environment/secrets manager |

Commit `.env.example` with placeholder values to document expected settings. Keep the real `.env` ignored. A safe layout makes the safe behaviour obvious and reduces accidental secret exposure.

## 15. Data directories

```text
project/
├── src/
├── tests/
└── data/
    ├── raw/
    ├── processed/
    └── fixtures/
```

- `raw/`: original input. Commit only if small, stable, and non-sensitive.
- `processed/`: generated output; usually do not commit because it can be regenerated and becomes stale/noisy.
- Temporary data: use a temporary or ignored location; do not check it in.
- `fixtures/`: small, deterministic test inputs (e.g. a three-row CSV with good and bad rows); normally commit these because tests need them.

Large/binary/frequently regenerated data bloats version control and is poorly suited to ordinary source history. The chapter teaches placement, not detailed Git ignore syntax.

## 16. Scripts and entry points

Three distinct roles:

1. **Reusable package code:** lives inside the package and is safe to import.
2. **One-off scripts:** occasional standalone tasks can live in `scripts/`.
3. **CLI entry point:** a designated package interface, commonly `cli.py` with `main()` and the `__main__` guard; later packaging may expose an installed command.

A `scripts/` directory full of undocumented duplicates becomes maintenance debt. If a script is used regularly or contains logic others need, move reusable logic into the package and expose a proper CLI.

## 17. Imports and layout

Import success depends on the relationship between package location and `sys.path`. `sys.path` varies with invocation (`python file.py`, `-m`, `-c`), environment (`PYTHONPATH`, installed packages), IDE/test-runner configuration, and working directory.

Absolute imports name the package from its top-level namespace; relative imports depend on the importing module's package context. A properly installed package is much less dependent on the directory from which it is run, though local names can still shadow installed modules in some contexts.

Example for an uninstalled `src/` project:

```bash
cd project/src
python -c "import app; print('works')"   # works: src is on sys.path

cd project
python -c "import app; print('works')"   # ModuleNotFoundError
```

This is why `src/` projects normally use an editable install rather than repeatedly changing directories.

## 18. Common import/layout failures

1. **`ModuleNotFoundError` from wrong directory:** inspect `sys.path`; run with correct package context or install the package.
2. **Directly running a package file:** `python src/app/cli.py` gives no package context; use `python -m app.cli` with the package importable.
3. **Incorrect relative import:** dot count does not match the directory nesting, or the file has no package context.
4. **Duplicate module names:** whichever matching top-level name is found first on `sys.path` wins; inspect `module.__file__`.
5. **Uninstalled `src/` package:** install editably or deliberately configure the path during early learning.
6. **Wrong Python environment:** inspect `sys.executable`; install into the interpreter actually running the program.
7. **Local source shadows installed package:** inspect `package.__file__`; consider `src/` layout for distributable projects.

## 19. Circular package dependencies

Circular imports can happen between subpackages as well as individual modules. Example: `orders/__init__.py` imports `customers`, while `customers/__init__.py` imports `orders`. One package is still partially initialized when the other requests a name.

Fix the architecture, not merely the import order:

```text
mypackage/
├── shared/
│   └── __init__.py
├── orders/
│   └── __init__.py
└── customers/
    └── __init__.py
```

Move the genuinely shared type/function into `shared/`; both packages depend on it, and neither depends on the other. Decide dependency direction before modules become tightly coupled. This chapter does not require dependency-injection frameworks.

## 20. Feature/domain-based vs layer-based organization

**Feature/domain-based** groups by business area:

```text
app/
├── users/
│   ├── models.py
│   ├── validation.py
│   └── service.py
├── orders/
│   ├── models.py
│   ├── validation.py
│   └── service.py
└── reports/
```

Advantage: everything for one feature is together; adding a new independent feature can be self-contained. Disadvantage: shared logic used by multiple features may be duplicated or awkwardly located.

**Layer-based** groups by responsibility type:

```text
app/
├── cli/
├── services/
├── domain/
└── data/
```

Advantage: all code of one architectural type is together. Disadvantage: understanding one feature may require visiting several directories.

Choose based on how the system is likely to change. Frequently added independent features often favour feature-based organization; a stable set of features with evolving layers may favour layer-based organization. Neither is universally superior.

## 21. Let structure evolve with project size

- **Small:** `app.py`, `utils.py`.
- **Medium:** package, tests, config, and metadata.
- **Larger:** layer-based or feature-based subpackages, plus docs.

Do not put a 50-line script into five layers and subpackages. That adds navigation overhead without solving a real problem. Equally, do not leave a genuinely complex application in one enormous file. Add structure when actual complexity justifies it.

## 22. Stable public package API

A caller can import a stable public name:

```python
from mypackage import process_data
```

or reach into an internal implementation:

```python
from mypackage.internal.processing_helpers import process_data
```

The first depends on the package API, usually re-exported by `__init__.py`. The second depends on the exact internal file layout. If implementation files move, a curated public API can remain unchanged as long as the re-export is updated.

Re-export only the names external users are meant to rely on. Keep internal helpers private and undocumented as public interfaces.

## 23. Namespace packages

A regular package has `__init__.py`. A **namespace package** (Python 3.3+) can omit it; Python can combine matching package portions from multiple directories or separately installed distributions into one logical package namespace.

This is useful in advanced ecosystems where optional components are distributed separately. It is uncommon in everyday application code. For this roadmap, an explicit `__init__.py`, even empty, is the clearer default.

## 24. Source tree to installed package

```text
source tree (e.g. src/mypackage/)
       ↓
logical Python package
       ↓
build artifact (e.g. wheel)
       ↓
installation into site-packages, or editable pointer to source
```

The repository's source tree and installed representation are related but not necessarily identical. The build configuration in `pyproject.toml` controls what is included and how it is installed. Building/publishing is deferred to the dedicated packaging chapter.

## 25. How structure improves code quality

Good boundaries improve readability, maintainability, unit testing, code review, onboarding, dependency reasoning, debugging, and reuse. The benefits come from meaningful responsibility boundaries, not from a tree that merely looks tidy.

## 26. Bad vs better structures

Bad:

```text
project/
├── everything.py
├── random_utils.py
├── test.py
├── final.py
└── final2.py
```

Better first step:

```text
project/
├── package/
│   ├── __init__.py
│   ├── cli.py
│   └── processing.py
├── tests/
│   └── test_processing.py
└── pyproject.toml
```

When distribution matters, move to `src/package/`. When processing grows into several distinct concerns, split it into modules such as `config.py`, `validation.py`, and `processing.py`. Each change should answer demonstrated complexity.

## 27. Production-oriented project structure

```text
project/
├── src/
│   └── application/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── logging_config.py
│       ├── validation.py
│       ├── processing/
│       │   ├── __init__.py
│       │   ├── csv_processing.py
│       │   └── json_processing.py
│       └── domain/
│           ├── __init__.py
│           └── models.py
├── tests/
│   ├── test_config.py
│   ├── test_validation.py
│   └── processing/
│       └── test_csv_processing.py
├── data/
│   ├── raw/
│   └── fixtures/
├── docs/
│   └── usage.md
├── pyproject.toml
├── README.md
└── .gitignore
```

Responsibilities:

- `src/application/`: installable application package.
- `cli.py`: thin CLI, parser, `main()`, entry guard.
- `config.py`: immutable configuration and environment/CLI resolution.
- `logging_config.py`: one place for logging setup.
- `validation.py`: pure validation functions.
- `processing/`: subpackage because CSV and JSON processing have grown into separate modules.
- `domain/`: core types/rules shared by processing modules.
- `tests/`: outside shipped package, mirroring source structure.
- `data/raw/`: real input; `data/fixtures/`: committed small test data.
- `docs/`: longer documentation.
- root metadata/docs/ignore files describe the project as a whole.

This is an example, not a mandatory template. Use it only when project complexity justifies it.

## 28. Ten progressive structure examples

The lesson progresses through these examples:

1. One-file `app.py` for a tiny script.
2. `app.py` + `utils.py`, imported as `from utils import helper`.
3. A package with `__init__.py` and `utils.py`; import `package.utils`.
4. A nested `processing/` subpackage; import `package.processing.csv_processing`.
5. Flat layout with package, tests, and `pyproject.toml`.
6. `src/` layout, normally importable after install or deliberate path configuration.
7. CLI package with `cli.py`, `config.py`, and `processing.py`; only CLI depends on lower layers.
8. Separate `tests/test_config.py` and `tests/test_processing.py`.
9. Public/private API: `__init__.py` re-exports `process_data`; `_internal_helpers.py` stays internal.
10. The complete production-oriented tree in §27.

## 29. Mini-project — `orders-report`

This is a **layout design exercise**, not a full implementation. The CLI reads a directory of order CSVs, validates/cleans rows, and writes a JSON summary.

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
├── data/
│   └── fixtures/
│       └── sample_orders.csv
├── pyproject.toml
├── README.md
└── .gitignore
```

- `cli.py`: `build_parser()`, `--input-dir`, `--output`, `main(argv) -> int`, guard; calls other layers, no business rules.
- `config.py`: frozen `AppConfig(input_dir, output_path, log_level)` and `build_config(args)`; receives parsed args, reads `LOG_LEVEL` (default `INFO`); no `--log-level` option exists in this example.
- `logging_config.py`: `configure_logging(level)`, called once at startup.
- `validation.py`: pure `validate_row(row)`.
- `processing.py`: reads CSV files, validates each row, collects errors, writes JSON summary.

Dependencies:

```text
cli.py → config.py
cli.py → logging_config.py
cli.py → processing.py
processing.py → validation.py
```

Execution:

```bash
python -m orders_report.cli --input-dir data/raw --output summary.json
```

This assumes the `src/` package is already installed (typically editably) or otherwise made importable. The CLI parses arguments, resolves config, configures logging, calls processing, and returns a status based on data validity. The JSON result goes to stdout; logs/diagnostics go to stderr. Raw input is not committed; small fixtures are. Tests call validation/processing functions directly with temporary paths, rather than needing the CLI.

Importing the modules loads declarations but should not start processing or write files. Configuration is resolved once into an immutable object. A second output format should generally change processing, not CLI/config. This structure supports testing, extension, and consistent installed-package imports.

## 30–33. Exercises, debugging, interview, knowledge check

The source contains 14 formal exercises, 8 debugging scenarios, 20 interview/architecture questions, and 8 knowledge-check questions. Complete answers are in Parts C–F below. The main tested reasoning is: distinguish project elements; choose flat vs `src/`; separate CLI/config/logging/validation/processing; make dependencies one-way; maintain a stable public API; choose feature vs layer organization; and avoid over-engineering.

## 34. Production checklist

- Root contains `pyproject.toml`, `README.md`, and appropriate `LICENSE`/`.gitignore`.
- Package has a meaningful namespace; subpackages exist only when justified.
- Every module has one clear responsibility and a meaningful name.
- Imports are predictable, minimal, and not dependent on a particular working directory.
- Import-time side effects are minimal.
- CLI parsing and entry guard live in one CLI module; business logic does not depend on it.
- `tests/` is outside the package and mirrors source structure where useful.
- Configuration and secrets are separated; no real secrets are committed.
- Public API is deliberate; internal modules are signalled as private.
- Dependencies flow one way; shared logic lives in a common lower-level module.
- Structure matches actual project complexity.
- Root documentation and metadata accurately describe the project.

---

# Part B — Project-Tree and Current-Level Assessment

## Your roadmap position

Your Stage 1 roadmap contains 24 modules, 212 numbered lessons, and 282 files. Its four Stage 1 projects are:

1. Personal Expense Ledger CLI.
2. Log Investigation and Reliability CLI.
3. Data Quality and Transformation Pipeline (`orders.csv`, `dqpipe` package with CLI/config/pipeline/rules, tests, and data contract).
4. Rule-Based Risk Review Engine (`transactions.csv`, `rules.toml`, `riskreview` package with CLI/engine/I/O/models/rules, tests, and golden decision data).

You have completed Module 03 foundations (control flow, functions, scope, side effects, exceptions and validation), Module 04 problem-solving/collections/algorithmic habits, and Module 05 Lessons 01–09 (text files, paths, CSV, JSON, encodings/newlines, `argparse`, streams/exit codes, logging, and environment configuration/input validation).

## Current level and implications

Your current level is **beginner progressing toward intermediate** in Python engineering. You already understand the responsibilities that this chapter places into a project tree: CLI parsing, configuration, logging, validation, file processing, return codes, and reusable functions.

The new learning challenge is architectural rather than syntactic: deciding boundaries, package layout, import paths, public APIs, and dependency direction. The exercises below use standard-library Python and the module's concepts. They do not introduce dependency-management commands, build backends, advanced testing frameworks, or web frameworks; those belong to later lessons.

---

# Part C — All 14 Formal Exercises, Solved

## 1. Identify files, modules, and data directory

```text
project/
├── app.py
├── helpers.py
└── data/
    └── input.csv
```

- `app.py` and `helpers.py` are files and Python modules.
- `input.csv` is a file, but not a Python module.
- `data/` is a directory for data, not a Python package in this example.

**Reason:** a module is importable Python code; a data directory stores non-code input.

## 2. Reorganize an unstructured project

```text
project/
├── package/
│   ├── __init__.py
│   ├── cli.py
│   └── utils.py
├── tests/
│   └── test_utils.py
├── pyproject.toml
└── README.md
```

- `cli.py`: command-line interface.
- `utils.py`: reusable helper functions.
- `test_utils.py`: tests for helper behaviour.
- `__init__.py`: regular package marker.
- Root metadata/docs describe the whole project.

Names such as `final.py` and `final2.py` do not communicate responsibility.

## 3. Explain `tests/` placement

Put `tests/` as a project-root sibling of `src/` or the flat package. Tests verify the package but are not normally shipped as application code. This separation keeps production source clean and lets unit tests call business functions without starting the CLI.

## 4. Interpret `__init__.py`, `core.py`, `_helpers.py`

- `__init__.py`: marks a regular package and may re-export the supported API.
- `core.py`: not marked private, but that alone does not promise it is public.
- `_helpers.py`: underscore signals internal implementation detail; Python does not enforce privacy.

## 5. Convert flat layout to `src/`

Before:

```text
project/
├── package/
│   ├── __init__.py
│   └── logic.py
├── tests/
└── pyproject.toml
```

After:

```text
project/
├── src/
│   └── package/
│       ├── __init__.py
│       └── logic.py
├── tests/
└── pyproject.toml
```

The change reduces the risk that tests run from the project root import the uninstalled local package and miss packaging mistakes. The package normally needs an editable install to be importable from the root.

## 6. Design a JSON validation CLI

```text
json-checker/
├── src/
│   └── json_checker/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── logging_config.py
│       ├── validation.py
│       └── processing.py
├── tests/
│   ├── test_validation.py
│   └── test_processing.py
├── data/
│   └── fixtures/
├── pyproject.toml
└── README.md
```

- `cli.py`: argparse, `main(argv)`, stdout/stderr and exit code.
- `config.py`: validated settings such as strict mode.
- `logging_config.py`: configure logs once.
- `validation.py`: validate JSON structure/content.
- `processing.py`: read files, call validators, count valid/invalid files, build summary.
- Tests independently cover validation and processing.

Dependency direction: `cli → config/processing/logging`, and `processing → validation`.

## 7. Diagnose missing `app` in a `src/` project

Likely cause: package is in `src/app`, but the project root invocation has not installed the package and `src/` is not on `sys.path`.

Two fixes:

1. Recommended: install the project editably using the procedure taught in the later packaging chapter.
2. Temporary learning workaround: deliberately put `src/` on the import path, e.g. run from inside `src/` or configure `PYTHONPATH`.

Do not change imports to `from src.app...`; `src` is a source-layout container, not the package name.

## 8. Remove circular `orders` / `customers` imports

```text
mypackage/
├── shared/
│   ├── __init__.py
│   └── identifiers.py
├── orders/
│   └── __init__.py
└── customers/
    └── __init__.py
```

Move shared customer-ID types or shared lookup contracts into `shared/`. Both `orders` and `customers` import from `shared`; neither imports the other. This removes the cycle rather than relying on import timing.

## 9. Public API versus internal module

Fragile internal dependency:

```python
from mypackage.internal.helpers import compute_summary
```

Stable package API:

```python
# mypackage/__init__.py
from .internal.helpers import compute_summary
__all__ = ["compute_summary"]

# external caller
from mypackage import compute_summary
```

If implementation moves, update the re-export; external callers keep the same import. The public interface is the compatibility boundary.

## 10. Refactor an 800-line `main.py` safely

Recommended sequence:

1. **Create `validation.py` first.** Extract pure validation functions; these have few dependencies and are easiest to test.
2. **Create `config.py`.** Move environment/config parsing and build a single validated configuration object.
3. **Create `processing.py`.** Move business logic and file-processing coordination; make it accept already-validated inputs/config.
4. **Create `logging_config.py`.** Centralize logging setup if it is substantial enough to warrant a module.
5. **Create `cli.py` last.** Keep argparse, `main(argv)`, output-stream decisions, and exit-code mapping here; call the other modules.
6. **Create `tests/`.** Add focused tests around extracted functions and integration-style tests for `main()`.

After each extraction, run the existing behaviour checks and compare outputs/exit codes. Extracting pure, low-dependency code first reduces risk; keep the old CLI working until the new modules are verified.

## 11. Choose feature-based or layer-based

- Fixed CLI capabilities (`validate`, `transform`, `report`) that rarely change: layer-based organization is suitable because CLI/validation/processing are stable architectural responsibilities and capabilities can share them.
- Web-style application gaining independent features frequently: feature-based organization is suitable because each feature can live in its own directory and evolve independently.

The decision follows expected change patterns, not a universal ranking.

## 12. Export only two of five internal modules

Example package API:

```python
# mypackage/__init__.py
from .core_api import process, validate

__all__ = ["process", "validate"]
```

The other modules can be `_parsing.py`, `_formatting.py`, and `_cache.py`. They support implementation but are not re-exported as stable public names. Keep the public API small and deliberate.

## 13. Identify over-engineering for a 100-line script

At least three choices from the large production tree would be excessive:

- A `processing/` subpackage: one `processing.py` is enough if there are only a few functions.
- A `domain/` subpackage: unnecessary if there are no shared domain models/rules.
- A `src/` layout: its strongest benefit is testing/distribution of an installable package; a personal script always run from its checkout may not need it.
- Separate `config.py` and `logging_config.py`: minimal setup can stay in the small script until there is enough complexity to justify modules.
- Multiple nested test folders: a small script may need only a compact test file.

The reason is not merely fewer folders: each abstraction has navigation and maintenance cost. Add it only when it isolates a real responsibility or solves a real import/distribution/testing risk.

## 14. Design a distinct production CLI

Example: `archive-audit`, a CLI that inventories files, validates naming/size rules, and writes a JSON audit report.

```text
archive-audit/
├── src/
│   └── archive_audit/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── logging_config.py
│       ├── validation.py
│       ├── inventory.py
│       └── report.py
├── tests/
│   ├── test_validation.py
│   ├── test_inventory.py
│   └── test_report.py
├── data/
│   └── fixtures/
├── docs/
│   └── usage.md
├── pyproject.toml
├── README.md
└── .gitignore
```

- `cli.py`: argparse, `main(argv)`, streams and exit codes.
- `config.py`: validated input/output paths and runtime settings.
- `logging_config.py`: console/file handler configuration.
- `validation.py`: pure filename and size-rule validators.
- `inventory.py`: filesystem traversal and metadata collection.
- `report.py`: converts validated inventory into JSON report data.
- `tests/`: focused tests, including temporary-directory fixtures.
- `data/fixtures/`: small committed test inputs.
- `docs/usage.md`: extended operational instructions.
- Root files: metadata, usage overview, and ignore rules.

Dependency direction: `cli → config/inventory/report`; `inventory → validation`; `report` consumes inventory results. Lower-level modules do not import `cli`. This tree is justified because the scenario has distinct I/O, validation, reporting, and CLI responsibilities.

---

# Part D — All 8 Debugging Scenarios

1. **`ModuleNotFoundError` from project root:** in a `src/` layout, `src/` is not automatically on `sys.path`. Inspect `sys.path`; install editably or deliberately configure the path.
2. **Running `cli.py` from inside its package:** direct file execution lacks package context and may not find the top-level package. Run `python -m app.cli` from a directory where `app` is importable.
3. **Package not installed:** `pip show` says not found. Verify the active interpreter and perform the project install in that environment.
4. **Wrong relative-import dot:** `csv_processing.py` is inside `app/processing/`, while `validation.py` is in `app/`. Use `from ..validation import validate_row`, not `from .validation`.
5. **Circular package dependency:** `orders` and `customers` import one another. Trace package initialization and extract shared contracts/functions to `shared/`.
6. **Generic `config` name collision:** inspect `config.__file__`; rename a generic root-level module to a project-specific name and use fully qualified imports.
7. **Local `email.py` shadows standard library:** inspect `email.__file__`; rename it. A project package namespace such as `app.email` avoids a bare top-level collision.
8. **Tests work under pytest but not direct file execution:** the two invocations can construct different `sys.path` values. Use a proper editable install and package imports instead of relying on test-runner-specific path setup.

---

# Part E — 20 Interview and Architecture Answers

1. **Project layout:** organization of files/folders; it affects imports, testability, maintainability, and onboarding.
2. **Module/package/project:** module is importable code; package groups modules under a namespace; project includes packages plus tests/config/docs/metadata.
3. **Flat vs `src/`:** flat puts package at root; `src/` puts it under `src/` and reduces accidental local imports.
4. **Editable install:** makes a `src/` package importable through the environment while reflecting source edits.
5. **`__init__.py`:** marks a regular package and may re-export names; empty is valid and avoids unnecessary import-time work.
6. **Private naming:** leading underscore is a convention, not enforced access control.
7. **Stable API:** re-export supported names from `__init__.py`; internal modules can move without breaking callers.
8. **CLI location:** dedicated `cli.py`; business logic should not depend on argparse or `sys.argv`.
9. **Tests outside source:** test files are not normally part of the production package and can exercise source independently.
10. **`pyproject.toml`:** project metadata, dependencies, build and tool configuration; root-level because it describes the whole project.
11. **Working directory:** invocation and environment affect `sys.path`, so different launch locations can produce different imports.
12. **Absolute/relative imports:** absolute names the top-level package; relative names a sibling/parent and requires package context.
13. **Circular dependency:** two modules/packages import each other; move shared functionality into a third lower-level module.
14. **Feature/layer organization:** feature groups business areas; layer groups responsibility types; choose based on expected change.
15. **Growth:** start simple, add packages/tests, then layers/subpackages when complexity demands; premature structure adds overhead.
16. **Testing:** responsibility boundaries allow direct tests of validation/business logic without CLI and I/O.
17. **Root vs package:** root has README, LICENSE, `.gitignore`, `pyproject.toml`, tests/docs; package contains shippable application code.
18. **Secrets:** runtime environment/secrets manager or ignored local `.env`; never committed; `.env.example` contains placeholders.
19. **Namespace package:** package portions can combine across directories/distributions without each containing `__init__.py`; uncommon in ordinary apps.
20. **Production CLI design:** `src/` package, thin CLI, config/logging/validation/processing modules, tests outside package, fixtures/docs/root metadata; every module has one responsibility and dependencies flow one way.

---

# Part F — All 8 Knowledge-Check Answers

1. **Why is layout more than organization?** Because it changes what Python can import through `sys.path`, how package namespaces work, and whether responsibilities can be tested separately.
2. **Why does `src/` need installation?** The project root does not contain the package directly, and Python does not normally add `src/` to the path just because it exists.
3. **Interpret `widget_tool/`:** `src/widget_tool/` is the package; `src/` is a source container, not normally the import package; `pyproject.toml` is project metadata.
4. **Will `import widget_tool` work from project root without installation?** Normally no; `src/` is not on `sys.path`. Install editably or deliberately add `src/`.
5. **What does `__init__.py` export?** `run_pipeline` is the explicitly intended stable package-level API; `__all__` documents the wildcard export list.
6. **Why does root `utils.py` win?** A bare `import utils` searches top-level entries in `sys.path`; the project root may expose its `utils.py` before the intended package module. Use `from app import utils` or `from app.utils import ...`, and remove/rename the ambiguous root file.
7. **Should one new exports feature trigger a complete reorganization?** No. Keep the existing layer-based structure if it still fits; add exports components in the existing pattern. Reorganize only if the old structure no longer supports the project's changes.
8. **Should a 40-line script become a layered `src/` package now?** No. Keep it simple until it has real reuse, distribution, testing, or complexity needs that justify the extra boundaries.

---

# Final Mastery Checklist

- [ ] Explain file vs module vs package vs project.
- [ ] Choose flat or `src/` layout based on distribution/testing needs.
- [ ] Explain why an editable install is normally used with `src/`.
- [ ] Design packages and subpackages around real responsibilities.
- [ ] Keep `__init__.py` lightweight and curate public exports.
- [ ] Treat underscore-prefixed modules as internal conventions.
- [ ] Separate CLI, configuration, logging, validation, processing, and data access.
- [ ] Keep tests outside the shipped package.
- [ ] Keep secrets out of version control.
- [ ] Distinguish raw, generated, temporary, and fixture data.
- [ ] Diagnose import failures using `sys.path`, `sys.executable`, and `module.__file__`.
- [ ] Remove circular dependencies through shared lower-level modules.
- [ ] Choose feature- or layer-based organization based on expected change.
- [ ] Add structure only when actual complexity justifies it.

**Core engineering principle:** a good project tree is not the most elaborate tree. It is the smallest clear structure that gives each responsibility a home, makes imports predictable, keeps dependencies one-way, and makes the important logic independently testable.
