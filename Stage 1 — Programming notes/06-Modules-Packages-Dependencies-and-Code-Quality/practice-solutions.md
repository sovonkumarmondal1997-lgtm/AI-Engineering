# Module 1.6 — Cumulative Practice Questions: Complete Solutions

**Source:** `practice-questions(20261110-055939).md`  
**Coverage:** All 28 questions across Module 1.6 Lessons 01–07  
**Purpose:** Step-by-step solutions with code walkthroughs, engineering reasoning, and scope kept to concepts already taught.

---

## 1. Learning-level and project-tree assessment

Your Stage 1 roadmap contains 24 modules, progressing from Python fundamentals through data structures, algorithms, files/CLI, packages, dependencies, code quality, testing, OOP, and production Python.

Four Stage 1 capstones are the Personal Expense Ledger CLI, Log Investigation and Reliability CLI, `dqpipe` data-quality pipeline, and `riskreview` rule-based risk engine.

You completed Module 05's file, CSV/JSON, CLI, logging, configuration, and validation lessons. Module 1.6 Lessons 01–07 covered:

1. Imports, modules, and `__main__`.
2. Project layout and package structure.
3. `pyproject.toml`, lock files, and `uv`.
4. Dependency management and Semantic Versioning.
5. Ruff formatting and linting.
6. Type hints and type checking.
7. Docstrings, READMEs, and user documentation.

**Assessment:** You are a beginner progressing toward intermediate Python engineering. Your completed lessons provide the prerequisites for all 28 questions. The solutions combine those concepts without assuming later advanced Python modules.

# Part 1 — Basic

## Question 1 — Import name collision

**Problem:** Two `from ... import dumps` statements bind the same name in `main.py`.

```python
import json
import my_logging_shim

print(json.dumps({"a": 1}))
print(my_logging_shim.dumps({"a": 1}))
```

**Explanation, line by line**

1. `import json` binds the standard-library module to the local name `json`; it does not create a bare local name called `dumps`.
2. `import my_logging_shim` binds the project module under a different local name.
3. `json.dumps(...)` explicitly selects the JSON serializer.
4. `my_logging_shim.dumps(...)` explicitly selects the project function.

The original code imported `dumps` twice. The second import rebound the same local name, silently replacing the first reference. Python namespaces are name-to-object mappings; a later binding to the same name wins. Module-qualified access prevents the collision and makes the source of each function obvious.

## Question 2 — Safe import and `__main__`

```python
def build_report(title: str) -> str:
    return f"=== {title} ==="


def main() -> int:
    print(build_report("Demo Report"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Explanation, line by line**

1. `def build_report...` defines a reusable function; defining it does not print anything.
2. `return f"...{title}..."` constructs and returns the report string.
3. `def main() -> int` creates the program entry-point function and declares its exit-status result.
4. `print(build_report(...))` runs the demo only when `main()` is called.
5. `return 0` reports successful completion.
6. `if __name__ == "__main__":` is true when this file is executed as the program, but false when another module imports it.
7. `raise SystemExit(main())` converts the returned integer into the process exit status.

The original top-level `print()` ran during import because Python executes module-level statements when importing. Moving executable work into `main()` and guarding its call makes `import report` safe and testable.

## Question 3 — File, module, package, project, and `src` layout

Given `weather_cli/src/weather/{__init__.py, cli.py, forecasting.py}`, `tests/`, `pyproject.toml`, and `README.md`:

- `weather_cli/` is the **project/repository**: the complete collection of source, tests, and metadata.
- `weather/` is a **Python package**: a directory with `__init__.py`.
- `cli.py` is a **module**: one Python source file, importable as `weather.cli`.
- `README.md` is a documentation **file**, not a Python module.

This is a **src layout** because the importable package is nested under `src/`.

It reduces the risk of tests accidentally importing the source directory directly from the project root rather than importing the package as installed. This makes packaging mistakes—such as source files omitted from the built distribution—more likely to be detected during development. The project normally needs an editable installation before `weather` is importable from the root.

## Question 4 — Development-only dependency with a bounded version range

Command:

```bash
uv add --dev "pandas>=2.0,<3.0"
```

Conceptual `pyproject.toml` result:

```toml
[project]
dependencies = [
    "requests>=2.31,<3.0",
]

[dependency-groups]
dev = [
    "pandas>=2.0,<3.0",
]
```

**Explanation**

- `uv add` declares a dependency, resolves the dependency graph, updates `uv.lock`, and syncs the environment.
- `--dev` puts `pandas` in the development dependency group, not the runtime dependency list.
- `pandas>=2.0` permits versions from 2.0 upward.
- `<3.0` prevents automatic resolution across the next major-version boundary without a deliberate constraint change.
- `requests` is a runtime dependency because the shipped application needs it to run.
- `pandas` is development-only in this scenario, so production need not install it.

The exact TOML representation can vary with `uv` version and configuration; the important distinction is runtime dependencies versus the development group.

## Question 5 — Semantic Versioning

- `1.4.0 → 1.4.1`: **PATCH**. A backward-compatible bug fix; existing callers should continue to work.
- `1.4.1 → 1.5.0`: **MINOR**. New backward-compatible functionality; existing callers should continue to work.
- `1.5.0 → 2.0.0`: **MAJOR**. A potentially breaking change; callers must replace `validate()` with `check()` and adapt to the new result object.

A constraint such as `strictjson>=1.4,<2.0` allows compatible 1.x releases but excludes 2.x until the consuming project deliberately reviews and changes the upper bound.

SemVer communicates maintainer intent; it is not a tool-enforced guarantee. Run tests after PATCH updates too.

## Question 6 — Ruff formatting versus linting

Problems:

| Code issue | Category | Reason |
|---|---|---|
| `calculate(x,y)` | Formatting | Missing space after comma |
| `x+y` | Formatting | Missing spaces around operator |
| Unused `os` import | Linting (`F401`) | Unused import |
| Unused `sys` import | Linting (`F401`) | Unused import |
| Assigned but unread `unused_variable` | Linting (`F841`) | Unused local variable |

Commands:

```bash
uv run ruff format .
uv run ruff check --fix .
```

- `ruff format .` rewrites Python formatting consistently.
- `ruff check --fix .` applies fixes Ruff considers safe, such as removing unused imports.
- Review `git diff` after automated fixes.

Ruff may leave the unused local variable because deleting it could hide a logic mistake. A human should decide whether it is genuinely dead code.

## Question 7 — Google-style function docstring and `__doc__`

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    Args:
        price: Unit price.
        quantity: Number of items.

    Returns:
        The total price.
    """
    return price * quantity
```

**Explanation**

1. The first line is a concise summary.
2. `Args:` documents the meaning of each parameter, not its type again; the signature already states `float` and `int`.
3. `Returns:` explains what the returned value represents.
4. `return price * quantity` performs the calculation.

Python stores the first string statement in the function body as `calculate_total.__doc__`. It can be viewed with `print(calculate_total.__doc__)` or `help(calculate_total)`. A string appearing after another executable statement is not the function docstring.

# Part 2 — Moderate

## Question 8 — Import-time side effects

Safe rewrite:

```python
def connect_to_database():
    ...


def load_config_from_disk():
    ...


def process_order(order_id: int) -> None:
    ...


def main() -> int:
    print("Starting application...")
    db_connection = connect_to_database()
    config = load_config_from_disk()
    print("Processing orders...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Explanation, line by line**

1. The first two `def` statements define functions; they do not connect to a database or read a file.
2. `process_order` remains independently importable by tests.
3. `main()` owns application startup and the real side effects.
4. `connect_to_database()` runs only when `main()` is called.
5. `load_config_from_disk()` likewise runs only during application startup.
6. The guard prevents `main()` from running during an ordinary import.
7. `SystemExit` propagates the returned status to the operating system.

In the original, both resource operations were at module level. Therefore `from app import process_order` unexpectedly connected to the database and read configuration. Importable modules should define reusable objects; explicit functions should perform operational work.

## Question 9 — Why a `src` package is not found

The command fails:

```bash
cd project
python -c "import app"
```

The package is at `project/src/app`, but Python searches directories on `sys.path`. Running from `project/` normally makes the project root available—not automatically `project/src/`. Therefore Python cannot find the top-level package `app`.

Two ways to make it importable:

**Option A — run from `src/`:**

```bash
cd project/src
python -c "import app; print('works')"
```

The current directory now contains `app/`, so it is on the import search path. This is a fragile workaround because commands and tests must use that working directory.

**Option B — install the project (recommended):**

```bash
cd project
uv sync
```

For a project configured for editable development installation, `uv sync` installs the project into its managed environment. Then run commands through that environment, for example `uv run python -c "import app; print('works')"`.

The install approach exercises the package as an installed user would. It is the intended development workflow for a `src` layout. The exact install result depends on valid package/build configuration in `pyproject.toml`.

## Question 10 — `pyproject.toml` changed but lock file did not

The declaration changed from:

```toml
"requests>=2.31,<2.32"
```

to:

```toml
"requests>=2.31,<3.0"
```

This widens the allowed range. It does **not** itself choose a newer version or rewrite `uv.lock`.

Correct workflow:

```bash
uv lock
uv lock --upgrade-package requests  # only if the PR intends to upgrade requests
git diff uv.lock
uv sync
```

**Explanation**

1. `uv lock` resolves the graph using the new declared constraints and updates the lock file. It can retain the currently locked version if that version still satisfies the widened range.
2. `uv lock --upgrade-package requests` deliberately asks the resolver to upgrade that package within the allowed range.
3. `git diff uv.lock` exposes the exact direct and transitive version changes for review.
4. `uv sync` aligns the local environment with the lock file.
5. Commit `pyproject.toml` and `uv.lock` together.

A stale or unreviewed lock file weakens reproducibility. A reviewer must distinguish “the range is now wider” from “the package was actually upgraded.”

## Question 11 — Prevent unreviewed major dependency upgrades

Correct declaration:

```toml
dependencies = [
    "pydantic>=2.0,<3.0",
]
```

- `>=2.0` permits updates within the 2.x line.
- `<3.0` blocks the resolver from selecting 3.x.
- `==2.5.0` would be an exact pin and would also block routine 2.x updates, which the team wants to receive.

A bounded range allows routine compatible updates while requiring a deliberate edit/review before crossing the next major boundary. SemVer is a compatibility convention, so tests and release-note review remain necessary.

## Question 12 — Modern Ruff config and test-only import exceptions

```toml
[tool.ruff]

[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"tests/*.py" = ["F401"]
```

**Explanation**

- `[tool.ruff]` is the root Ruff configuration table.
- `[tool.ruff.lint]` is where modern Ruff expects lint rule settings.
- `select` enables the chosen rule families: `E`/`F` diagnostics and import sorting via `I`.
- `ignore = ["E501"]` ignores the selected line-length rule project-wide.
- `[tool.ruff.lint.per-file-ignores]` introduces exceptions scoped by file pattern.
- `"tests/*.py" = ["F401"]` suppresses unused-import warnings only for matching test files where fixture imports may be intentional.

Do not globally disable `F401` just to accommodate test conventions. Use the narrowest exception that matches the real reason, and document the policy. Confirm the glob matches the actual test directory layout.

## Question 13 — Correct function annotations and docstring

```python
def create_user(name: str, age: int | None) -> None:
    """Create a user.

    Args:
        name: User's display name.
        age: User's age in years, or None if the age is unknown.
    """
```

**Three issues**

1. `name` had no annotation. `name: str` makes the expected type visible to readers and type checkers.
2. The docstring claimed `age` was always an `int`, while `Optional[int]` permits `None`. The corrected prose now states that possibility.
3. The old docstring repeated types already present in annotations and added little meaning. The revised prose explains domain meaning instead.

`age: int | None` still means the caller must pass the argument. To make it optional to omit, use `age: int | None = None`. The `|` union syntax requires Python 3.10 or later.

## Question 14 — Make README instructions executable

```markdown
## Prerequisites

- Python 3.12+
- uv

## Installation

```bash
git clone https://github.com/example/billing-service.git
cd billing-service
uv sync
```

## Usage

```bash
uv run python -m billing_service balance --customer-id 12345
# Customer 12345: $128.50
```
```

**Explanation**

- Prerequisites identify required tools before the reader starts.
- `git clone` obtains the repository.
- `cd` enters the project directory.
- `uv sync` installs the declared dependencies into the project environment.
- The usage command shows the actual CLI invocation and its required option.
- The output comment shows what success should look like.

The URL, module name, argument, and output above are illustrative. Replace them with real project values and run the commands before publishing. Documentation examples must not be invented as if verified.

# Part 3 — Hard

## Question 15 — Circular imports and `sys.modules`

The cycle is:

```text
orders/__init__.py -> imports CustomerId from customers
customers/__init__.py -> imports OrderId from orders
```

**What happens**

1. Python begins importing `mypackage.orders`.
2. It creates the module object and places it in `sys.modules` before executing the module body.
3. `orders` imports `CustomerId` from `customers`, so Python begins initializing `customers`.
4. `customers` imports `OrderId` from `orders`.
5. Python finds `orders` already in `sys.modules`; it does not restart the import.
6. But `orders` has not finished executing, so `OrderId` may not yet exist. The partially initialized module causes the import error.

**Preferred structural fix:** move the genuinely shared identifiers into a third lower-level module.

```text
mypackage/
├── shared/
│   └── __init__.py
├── orders/
│   └── __init__.py
└── customers/
    └── __init__.py
```

```python
# shared/__init__.py
CustomerId = str
OrderId = str
```

```python
# orders/__init__.py
from mypackage.shared import CustomerId
```

```python
# customers/__init__.py
from mypackage.shared import OrderId
```

Each subpackage now depends on `shared`, not on the other subpackage. This removes the dependency cycle rather than hiding it with a delayed import. In a real project, place the shared types in the module that best represents their domain.

## Question 16 — Impossible transitive dependency constraints

The requirements are:

```text
A requires B < 3
C requires B >= 3
```

No version of `B` can satisfy both constraints: one requires a version below 3, the other requires 3 or above. `uv add`/`uv sync` must fail dependency resolution.

`A` likely pins `B < 3` because its maintainers have not verified compatibility with B's major version 3, which may contain breaking changes under SemVer.

Two structural resolutions:

1. Upgrade `A` to a release that supports `B >= 3`, if such a compatible release exists.
2. Replace one conflicting dependency (`A` or `C`) with a compatible alternative if neither package has a release that resolves the conflict.

Do not force an installation that violates declared requirements. That hides the resolver's useful error and can produce runtime failures.

## Question 17 — Dependency drift between CI and production

**Root cause:** CI independently resolved unpinned package names at one point in time, while the production image retained older cached versions. With no committed lock file used consistently, the environments can contain different dependency graphs. This is dependency drift.

**Reproducible workflow**

```bash
uv add pandas requests
uv lock
git add pyproject.toml uv.lock
```

Then CI and container builds should use the committed files:

```bash
uv sync --locked
```

**Line-by-line**

1. `uv add` records direct dependencies in `pyproject.toml`, resolves their transitive dependencies, updates `uv.lock`, and syncs the environment.
2. `uv lock` explicitly resolves and writes the lock file when needed.
3. Commit both metadata files together so the declared constraints and resolved versions travel together.
4. `uv sync --locked` installs from the committed lock and fails if it is missing or stale rather than silently updating it.

Use the same lock-driven install in developer validation, CI, and container builds. This makes dependency selection consistent. It does not guarantee identical operating systems, system libraries, hardware, or external services.

## Question 18 — Why Ruff misses a dictionary-key typo

Original bug:

```python
active.append(u["nam"])
```

Ruff does not know the valid keys of a plain `dict`; `"nam"` is a syntactically valid string key. This requires a more precise data shape.

```python
from typing import TypedDict


class User(TypedDict):
    name: str
    status: str


def get_active_users(users: list[User]) -> list[str]:
    active: list[str] = []
    for user in users:
        if user["status"] == "active":
            active.append(user["name"])
    return active
```

**Explanation**

1. `TypedDict` declares the expected keys and value types for each user record.
2. `name: str` declares the valid name key.
3. `status: str` declares the status key.
4. `users: list[User]` tells the type checker each list item follows that declared shape.
5. `active: list[str] = []` creates a typed result list.
6. The `if` checks the status value.
7. `user["name"]` uses the declared key and appends its string value.
8. `return active` returns the collected names.

A type checker such as mypy or Pyright can flag `user["nam"]` because it is not a declared key. Ruff linting, type checking, and runtime tests are different quality layers; none replaces the others.

## Question 19 — Storage `Protocol` and stable public API

```python
# mypackage/storage/_protocol.py
from typing import Protocol


class StorageBackend(Protocol):
    def read(self, key: str) -> bytes: ...
    def write(self, key: str, data: bytes) -> None: ...
```

```python
# mypackage/storage/_local.py
class LocalStorageBackend:
    def read(self, key: str) -> bytes:
        ...

    def write(self, key: str, data: bytes) -> None:
        ...
```

```python
# mypackage/__init__.py
from .storage._protocol import StorageBackend
from .storage._local import LocalStorageBackend

__all__ = ["StorageBackend", "LocalStorageBackend"]
```

**Explanation**

- `Protocol` defines the required method shapes without requiring concrete classes to inherit from it.
- `read` accepts a key and returns bytes.
- `write` accepts a key and bytes, and returns `None`.
- `LocalStorageBackend` satisfies the protocol by providing matching methods.
- The package `__init__.py` re-exports the supported names.
- `__all__` lists names included by `from mypackage import *` and signals the intended public surface.

Callers can import from `mypackage` rather than depending on internal module paths. Underscore-prefixed modules are conventionally internal; this is a convention, not access control. A future cloud backend can satisfy the same protocol without changing the caller's interface.

## Question 20 — Document a database-backed API contract

```python
def get_order_total(order_id: int) -> float:
    """Return the total price of an order's line items.

    Args:
        order_id: Identifier of an existing order.

    Returns:
        The line-item subtotal in the order's currency, excluding tax
        and shipping.

    Raises:
        OrderNotFoundError: If the order does not exist.

    Side effects:
        Reads the order from the database. Does not modify order data.

    Compatibility:
        The result remains a line-item subtotal. Including tax or
        shipping would change the public contract.
    """
    order = database.fetch_order(order_id)
    if order is None:
        raise OrderNotFoundError(order_id)
    return sum(item.price * item.quantity for item in order.items)
```

**Code walkthrough**

1. `order_id: int` declares the identifier's type.
2. The docstring explains its meaning and the function contract.
3. `database.fetch_order(order_id)` performs external database I/O.
4. `if order is None` checks whether lookup found a record.
5. `raise OrderNotFoundError(order_id)` reports the missing order to the caller.
6. `sum(...)` multiplies each line item's price by quantity and adds the results.
7. The function does not write to the database, but it is not side-effect-free because it performs I/O.

README usage:

```python
from myapp.orders import get_order_total

total = get_order_total(order_id=501)
print(f"Order total: ${total:.2f}")
```

The README gives a short usage path; the docstring carries the full API contract. In a real system, document currency and decimal precision carefully; a `float` may not be appropriate for financial arithmetic.

## Question 21 — CLI with encoding configuration

A suitable package layout:

```text
wordcount/
├── __init__.py
├── __main__.py
└── cli.py
```

`cli.py`:

```python
import argparse
import os
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument(
        "--encoding",
        default=os.environ.get("WORDCOUNT_ENCODING", "utf-8"),
    )
    return parser


def count_words(path: str, encoding: str) -> int:
    with open(path, encoding=encoding) as file:
        return len(file.read().split())


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        total = count_words(args.file, args.encoding)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    print(f"{total} words")
    return 0
```

`__main__.py`:

```python
from wordcount.cli import main

raise SystemExit(main())
```

**Walkthrough**

- `argparse`, `os`, and `sys` provide argument parsing, environment lookup, and stderr.
- `build_parser()` creates the parser.
- `add_argument("file")` defines the required positional input path.
- `--encoding` accepts an override; if absent, its default comes from `WORDCOUNT_ENCODING`, falling back to UTF-8.
- `count_words()` opens the file using the selected encoding.
- `read()` loads the text; `split()` separates whitespace-delimited words; `len()` counts them.
- `main(argv)` accepts explicit arguments, making it easy to call directly in tests.
- `parse_args(argv)` uses the supplied list; when `argv` is `None`, argparse reads normal command-line arguments.
- The `try` block catches a missing file.
- The error is printed to stderr and status `1` is returned.
- Success prints the count and returns `0`.
- `__main__.py` makes `python -m wordcount` execute the CLI and converts its result into the process exit status.

README configuration row:

```markdown
| Variable | Required | Default | Description |
|---|---|---|---|
| `WORDCOUNT_ENCODING` | No | `utf-8` | Encoding used to read the input text file. |
```

README usage and exit code:

```markdown
## Usage

```bash
uv run python -m wordcount myfile.txt
# 452 words
```

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Input file not found |
```

Note: `python -m wordcount` requires `wordcount/__main__.py`. A guard placed only inside `cli.py` would support `python -m wordcount.cli`, not the package-level command shown above.

# Part 4 — Advanced

## Question 22 — Production Python service design

Directory structure:

```text
project/
├── src/
│   └── service/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── validation.py
│       └── processing.py
├── tests/
│   ├── test_validation.py
│   └── test_processing.py
├── pyproject.toml
├── uv.lock
├── README.md
└── CONTRIBUTING.md
```

**Responsibilities**

- `cli.py`: argument parsing, `main() -> int`, and the `__main__` entry point.
- `config.py`: environment/CLI configuration and precedence.
- `validation.py`: reusable validation functions.
- `processing.py`: core business logic.
- `tests/`: automated behavior checks.
- `pyproject.toml` and `uv.lock`: declared and resolved dependencies.
- `README.md`: user onboarding.
- `CONTRIBUTING.md`: developer workflow.

**Contributor command sequence**

```bash
uv sync --locked
uv run ruff format .
uv run ruff check .
uv run mypy .
uv run pytest
git diff
```

1. `uv sync --locked` installs the committed dependency graph and rejects a stale lock.
2. `ruff format .` formats source files.
3. `ruff check .` reports lint problems without silently applying fixes.
4. `mypy .` checks static type consistency.
5. `pytest` runs runtime tests.
6. `git diff` lets the contributor review all changed files.

For a pre-commit workflow, formatting can modify files; run it before the final lint/type/test checks and inspect the diff. CI should use strict lock checking too.

**README:** purpose, prerequisites, install command, configuration, first usage example, expected output, common troubleshooting, and link to developer docs.

**CONTRIBUTING.md:** development setup, tests, Ruff, type-check commands, code conventions, branch/commit expectations, PR review requirements, and how to run focused tests.

These layers are complementary: formatting checks layout; linting catches suspicious patterns; type checking catches static type inconsistencies; tests exercise runtime behavior.

## Question 23 — Staged modernization of a legacy project

1. **Stabilize dependencies.** Add `pyproject.toml`, declare current direct dependencies with reviewed constraints, generate and commit `uv.lock`. This comes first because every later tool must run in a consistent environment. Trade-off: infrastructure work has little immediate visible feature value.
2. **Introduce Ruff conservatively.** Add it as a dev dependency, format, inspect `git diff`, and enable a small rule set first. Trade-off: a broad initial rule set can overwhelm the team with legacy findings.
3. **Resolve import structure.** Fix unused/shadowed imports, avoid wildcard imports, and remove circular dependencies by extracting shared code. Trade-off: refactoring costs time but simplifies dependency direction before typing.
4. **Add type hints at public boundaries.** Start with functions used by other modules; run a type checker in permissive mode, then increase strictness gradually. Trade-off: partial typing gives useful value sooner than a risky all-at-once conversion.
5. **Add useful documentation.** Write docstrings for public APIs and repair README installation, configuration, and usage commands using the now-stable project setup. Trade-off: defer broad prose updates until names and commands stop changing, but document critical operational behavior as it is fixed.

Each stage should be a separate reviewable change with its own validation. Do not combine a large package restructure, broad lint auto-fix, and API behavior change in one unreviewable commit.

## Question 24 — AI/ML service boundaries

Suggested layout:

```text
src/agent_service/
├── __init__.py
├── cli.py
├── config.py
├── providers/
│   ├── __init__.py
│   ├── _protocol.py
│   └── _openai_provider.py
├── tools/
│   ├── __init__.py
│   ├── _protocol.py
│   └── search_tool.py
└── orchestration.py
tests/
```

Provider interface:

```python
from typing import Protocol


class ModelProvider(Protocol):
    def complete(self, prompt: str) -> str: ...
```

Tool interface:

```python
from typing import Protocol


class Tool(Protocol):
    name: str

    def run(self, arguments: dict[str, object]) -> str: ...
```

**Boundaries and what they prevent**

- `config.py` centralizes environment access so provider/orchestration code does not independently read configuration or embed secrets.
- `ModelProvider` lets orchestration depend on behavior rather than a concrete vendor client. A fake provider can be passed in tests; swapping providers need not change orchestration.
- `Tool` defines the expected shape of callable tools. New tool implementations can be added without making orchestration depend on each concrete tool class.
- `orchestration.py` coordinates providers and tools; it should not contain provider-specific transport details.
- `tests/` can supply fake implementations to avoid real network calls.

Ruff catches selected lint issues but does not prove architectural boundaries are respected. Code review and deliberate module boundaries are still needed. Documentation should state tool inputs/outputs, permissions, side effects, timeout/retry behavior, provider/model version, and failure behavior. Safety restrictions must be enforced in tool code, not only in prompts.

## Question 25 — Vulnerable transitive dependency

A transitive dependency is still installed and may be reachable at runtime. The fact that the project did not declare it directly does not remove the vulnerability or its exposure.

**Priority workflow**

1. Identify the affected package and exact locked version.
2. Read the advisory and patched release notes; determine the fixed version and compatibility constraints.
3. Attempt a targeted lock update:

```bash
uv lock --upgrade-package vulnerable-package
```

4. Inspect the change:

```bash
git diff uv.lock
```

5. Confirm the lock now selects the patched version; inspect any other dependency changes.
6. Run the project's tests and type checks.
7. Commit the relevant dependency metadata/lock changes and record the advisory in the change description.
8. Fast-track the security fix rather than waiting for the normal dependency-update cycle.

If the direct dependency still requires the vulnerable transitive range, upgrading it may not be sufficient. Look for a newer direct-dependency release that permits the patched version. If none exists, evaluate replacing the direct dependency with a compatible alternative. If no safe path exists, document and escalate the unresolved risk rather than forcing an invalid dependency graph.

Security updates need the same compatibility verification as routine updates, but higher priority and urgency.

## Question 26 — Notification `Protocol` and ADR

```python
# notifications/_protocol.py
from typing import Protocol


class Notifier(Protocol):
    def send(self, recipient: str, message: str) -> bool:
        """Return whether the backend accepted the message for delivery."""
        ...
```

```python
# notifications/_email.py
class EmailNotifier:
    def send(self, recipient: str, message: str) -> bool:
        ...
```

```python
# notifications/__init__.py
from ._protocol import Notifier
from ._email import EmailNotifier

__all__ = ["Notifier", "EmailNotifier"]
```

**Walkthrough**

- `Notifier` defines the behavior consumers require.
- `send()` accepts recipient and message strings.
- `-> bool` reports whether the backend accepted the request; it does not prove final delivery.
- `EmailNotifier` satisfies the method shape without inheriting from `Notifier`.
- Package re-exports provide a stable public import path.
- `__all__` documents the intended star-import surface.

**ADR**

```markdown
# ADR 0004: Use Protocol for notification backends

## Context
The application needs interchangeable email and future SMS backends,
and tests need lightweight fake implementations.

## Decision
Define Notifier as a typing.Protocol with send(recipient, message).
Implementations need matching methods but do not need inheritance.

## Alternatives Considered
- ABC: valid, but requires implementations and test doubles to inherit
  from a shared base even though they share no implementation.
- Unannotated duck typing: flexible, but loses static signature checks.

## Consequences
- Email, SMS, and test fakes can satisfy the same structural contract.
- A type checker can verify the required method signature.
- Protocol provides no shared implementation; reconsider an ABC if
  genuine shared behavior is later required.
```

A `Protocol` is appropriate because the implementations share a contract, not necessarily common code. An ABC is useful when shared implementation or runtime abstract-class enforcement is required.

## Question 27 — CI and documentation drift: what can be automated?

There are three separate failures, and it is important not to claim that every prose mismatch can be detected automatically.

**Failure 1: README CLI examples are stale.** Turn important README commands into smoke tests. For example, execute `uv run python -m app --help` and representative documented commands in a controlled test environment; assert the expected exit status and output. Run these tests in CI. This catches executable examples that no longer work.

**Failure 2: docstring says a function returns `None` but it now returns a value.** Arbitrary prose is not reliably machine-readable. A linter can check docstring presence/style, and doctest can execute examples, but neither can generally infer whether a sentence such as “Returns: None” accurately describes every implementation. The reliable control is a code-review requirement: whenever a public function's behavior changes, reviewers must compare its `Returns`/`Raises` contract with the implementation and tests. If the docstring contains a doctest that demonstrates the return value, that executable example can catch some mismatches.

**Failure 3: no traceability between code changes and documentation changes.** Adopt Documentation as Code: update docs in the same branch/commit/PR as the behavior change. Make documentation review a required PR checklist item. Git history then links the code change and its documentation update.

Example CI sequence:

```bash
uv sync --locked
uv run pytest --doctest-modules src tests
uv run ruff check .
uv run mypy .
```

- `uv sync --locked` installs the exact committed dependency graph.
- `pytest --doctest-modules` discovers and executes docstring doctests in the selected source/test paths.
- `ruff check .` checks configured lint rules.
- `mypy .` checks static types.

Add a separate README-command smoke test to the test suite. Keep human review for prose claims and same-PR traceability. The underlying discipline is Documentation as Code plus automated checks for executable examples and human review for meaning.

## Question 28 — Capstone: production-oriented migration plan

### Starting point

The project has one file mixing argument parsing, business logic, and file I/O; unpinned dependencies; no lock file; a minimal README; no tests, linting, or type hints.

### Target structure

```text
project/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── validation.py
│       └── processing.py
├── tests/
│   ├── test_validation.py
│   └── test_processing.py
├── pyproject.toml
├── uv.lock
├── README.md
└── CONTRIBUTING.md
```

**Module responsibilities**

- `__main__.py`: calls the CLI entry point for `python -m app`.
- `cli.py`: parses arguments, calls application functions, prints user-facing output, returns an exit code.
- `config.py`: loads and validates configuration in one place.
- `validation.py`: pure validation functions.
- `processing.py`: core business logic, kept independent from CLI parsing and file I/O where possible.
- `tests/`: checks validation and processing behavior.

### Migration sequence and trade-offs

**Step 1 — Capture dependencies and create a reproducible environment.**

```bash
uv init .
uv add package_one package_two
uv lock
```

Replace the illustrative package names with every actual direct dependency from the old requirements file, using reviewed version ranges.

- `uv init .` initializes project metadata.
- `uv add ...` records dependencies and resolves them.
- `uv lock` writes the resolved graph.

Commit `pyproject.toml` and `uv.lock`. Trade-off: this is infrastructure work with no new feature, but it prevents developers and CI from independently installing different dependency versions.

**Step 2 — Record current behavior before refactoring.**

Run the existing CLI manually with representative valid and invalid inputs. Save known inputs and expected outputs/exit statuses. Add a small set of regression tests around the most important behavior where feasible.

Trade-off: tests take time, but they reduce the risk of changing behavior accidentally during the upcoming file move. Do not rely only on memory of how the old program behaved.

**Step 3 — Split the monolithic file into package responsibilities.**

Move argument parsing into `cli.py`, configuration into `config.py`, pure validation into `validation.py`, and business logic into `processing.py`. Add `__init__.py` and `__main__.py`. Configure the package/build metadata for the `src` layout and install the project in editable development mode through the project environment.

Trade-off: this is a higher-risk structural change. Make it in small commits and compare the refactored CLI against the recorded behavior from Step 2. The `src` layout reduces accidental imports from the repository root.

**Step 4 — Add tests around the separated functions.**

Test valid inputs, invalid inputs, boundary cases, and the CLI's exit statuses. Keep business logic tests independent of terminal parsing and filesystem setup where possible.

Trade-off: tests add maintenance work, but they create a safety net before automated code changes and broader typing.

**Step 5 — Add Ruff.**

```bash
uv add --dev ruff
uv run ruff format .
uv run ruff check --fix .
uv run ruff check .
```

- `uv add --dev ruff` adds a development-only tool.
- `ruff format .` applies consistent formatting.
- `ruff check --fix .` applies safe lint fixes.
- `ruff check .` reports remaining issues.

Inspect `git diff`; begin with a focused rule set such as `F` and `I`, then expand deliberately. Trade-off: conservative adoption reduces noise in legacy code and makes each fix reviewable.

**Step 6 — Add type hints at public/module boundaries.**

Annotate public functions, parameters, and return values first. Use specific collection types and `Protocol` where the project needs swappable behavior. Run the chosen type checker in a permissive configuration initially, then tighten it as the codebase improves.

Trade-off: typing every internal variable immediately is expensive. Boundary typing gives the greatest communication and checking benefit first.

**Step 7 — Write and verify documentation.**

Replace `README.txt` with `README.md`. Include purpose, prerequisites, exact installation commands, configuration table, real CLI examples and output, exit codes, and troubleshooting. Add docstrings to public functions and classes. Put developer setup, test/lint/type commands, and contribution rules in `CONTRIBUTING.md`.

Trade-off: write detailed documentation after the structure and commands have stabilized, so it does not immediately become stale. However, update critical behavior/configuration documentation in the same PR as the change rather than deferring it.

**Step 8 — Make the workflow repeatable in CI.**

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run mypy .
uv run pytest
```

CI checks the committed lock, formatting, linting, types, and runtime tests. Add doctests and README command smoke tests when examples are executable. Require review of public API documentation and same-PR doc updates.

### Why this order?

- Reproducible dependencies come first because every later tool needs a stable environment.
- Baseline behavior is captured before moving code because the original project has no tests.
- Package boundaries make code independently testable and maintainable.
- Tests protect behavior before lint and typing changes.
- Ruff gives consistent formatting and catches configured suspicious patterns.
- Type hints communicate and statically check public contracts.
- Documentation is updated against the stabilized interface, then continuously maintained with code.
- CI makes the checks repeatable rather than dependent on individual developer memory.

This is a staged migration, not a rewrite. Each step should be independently reviewable and leave the project in a better state even if later work is delayed.

---

## Final coverage and completion checklist

All 28 questions are addressed: Q1–Q7 (imports, layout, dependencies, SemVer, Ruff, docstrings); Q8–Q14 (side effects, `sys.path`, lock consistency, typing, README); Q15–Q21 (circular imports, dependency conflicts, `TypedDict`, `Protocol`, API contracts, CLI); Q22–Q28 (production architecture, legacy modernization, AI/ML boundaries, security, ADR, documentation CI, capstone).

**Key engineering distinctions to retain**

1. `import module` avoids collisions that can occur when multiple `from module import name` statements bind the same local name.
2. Importing a module executes its top-level code; keep real I/O and startup work behind explicit function calls.
3. A `src` layout normally expects installation before imports from the project root.
4. `pyproject.toml` declares acceptable dependencies; `uv.lock` records the resolved dependency graph.
5. Formatting, linting, type checking, and tests detect different classes of problems.
6. Type hints describe data shape; docstrings explain meaning, behavior, errors, and side effects.
7. `Protocol` describes structural behavior; `__init__.py` and `__all__` help define the stable package API.
8. Documentation examples should be executable where practical; prose contracts still need human review.
9. Documentation must change with the code, not in a later forgotten task.
10. A safe migration is incremental, validated, and reviewable.

**Learning boundary:** This completes the Module 1.6 cumulative practice set. No next module or lesson is started here.
