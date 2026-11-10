# 01 — Imports, Modules, and `__main__`
## Complete Chapter Summary, Project-Tree Review, and Exercise Solutions

> **Scope:** Stage 1 · Module 1.6 · Imports, Modules, and `__main__`  
> **Source lesson:** `01-imports-modules-and-main.md`  
> **Approach:** Source-faithful teaching summary first, then worked exercises and review.  
> **Level assumption:** Module 1.5 lessons 01–09 are complete. The solutions use the Python standard library and concepts already introduced in the roadmap.

---

# Part A — Complete Chapter Summary

## 1. What a Python module is and why modules matter

A **module** is a named unit of Python code managed by Python's import system. A `.py` file is the most common way to create one. A file becomes useful as a module when other code can import and reuse its functions, classes, and constants.

Example:

```python
# math_utils.py
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
```

Another file can reuse it:

```python
# main_program.py
import math_utils

result = math_utils.add(2, 3)
print(result)  # 5
```

Modules provide four major benefits:

1. **Organization:** related code has a clear home instead of living in one giant file.
2. **Reuse:** many programs can use the same implementation without copy-paste.
3. **Namespace isolation:** `math_utils.add` and `text_utils.add` can coexist.
4. **Maintainability:** a bug in one shared implementation is fixed in one place.

A `.py` file and a module are not different file formats. The difference is the intended use: a module is designed to be imported and reused.

## 2. Four common import forms

Python provides four common ways to import code.

```python
import math
print(math.sqrt(16))  # 4.0
```
This binds the module object to the name `math`. Access its members through `math.`.

```python
import math as m
print(m.sqrt(16))  # 4.0
```
This binds the same module under the alias `m`. Aliases are useful for long names, established conventions, or avoiding a genuine name conflict.

```python
from math import sqrt
print(sqrt(16))  # 4.0
```
This binds only `sqrt` directly in the current namespace. The `math.` prefix is no longer needed.

```python
from math import sqrt as square_root
print(square_root(16))  # 4.0
```
This imports one specific name and gives it a different local name.

| Import form | Name made available | How to call it |
|---|---|---|
| `import math` | `math` module | `math.sqrt(16)` |
| `import math as m` | `m` module alias | `m.sqrt(16)` |
| `from math import sqrt` | `sqrt` | `sqrt(16)` |
| `from math import sqrt as square_root` | `square_root` | `square_root(16)` |

Prefer `import module` when using several members or when the source should be obvious at the call site. Use `from module import name` for a small number of frequently used names. Use aliases when they improve clarity or prevent a collision.

A collision can silently replace a previously imported name:

```python
from json import dumps
from my_custom_serializer import dumps  # replaces the first local name
```

After the second import, `dumps()` refers to the custom serializer. Avoid this by keeping module namespaces:

```python
import json
import my_custom_serializer

json.dumps({"a": 1})
my_custom_serializer.dumps({"a": 1})
```

Or alias the specific name:

```python
from my_custom_serializer import dumps as custom_dumps
```

## 3. What Python does during an import

Importing is **not** copying source text into the importing file. The normal process is:

1. Python receives `import module_name`.
2. It checks `sys.modules` to see whether the module is already cached.
3. If not cached, the import system searches for it (commonly using `sys.path`) and obtains a module specification.
4. Python creates and initializes a module object.
5. It puts that object in `sys.modules` **before** executing the module's code.
6. Python executes the module's top-level statements from top to bottom. Function and class definitions and variables become attributes of the module object.
7. If execution succeeds, import completes.
8. The importing code receives the requested module or imported name in its own namespace.

The early insertion into `sys.modules` is important: a module can be visible while still being only partially initialized. Circular imports exploit this timing and can fail because a requested name has not yet been defined.

Example:

```python
# greeting.py
print("greeting.py is being executed")

def say_hello():
    print("Hello!")
```

```python
# main.py
import greeting
greeting.say_hello()
```

Running `python main.py` prints:

```text
greeting.py is being executed
Hello!
```

The first message appears at the import statement, before `say_hello()` is called. Importing executes top-level code; it does not merely make the source available.

The imported module object is an ordinary Python object. Names defined at its top level become attributes, so `greeting.say_hello()` is ordinary attribute access.

## 4. Module namespaces

A **namespace** is a mapping between names and objects. Each module has its own namespace, separate from other modules and from the importing file.

```python
# module_a.py
value = "from module_a"

# module_b.py
value = "from module_b"

# main.py
import module_a
import module_b

print(module_a.value)  # from module_a
print(module_b.value)  # from module_b
```

Both modules can define `value` because the names live in separate module objects. This is one reason `import module` is a safe, explicit default: the origin of each name remains visible.

## 5. Useful module attributes

Python automatically provides special attributes on module objects.

| Attribute | Meaning |
|---|---|
| `__name__` | Module's import name, or `"__main__"` when it is the entry point |
| `__file__` | Filesystem path from which the module was loaded; may be absent for built-in/frozen modules |
| `__doc__` | Module docstring, if one is present |
| `__package__` | Package context used for relative imports |
| `__spec__` | `ModuleSpec` describing how the module was found and loaded |

Example:

```python
# greeting.py
"""A tiny greeting module."""

def say_hello():
    print("Hello!")
```

```python
import greeting

print(greeting.__doc__)      # A tiny greeting module.
print(greeting.__file__)     # path to greeting.py
print(greeting.__package__)  # '' for an imported top-level module
```

The chapter gives these typical values:

| How the module is used | `__name__` | `__package__` | `__spec__` |
|---|---|---|---|
| `import greeting` | `"greeting"` | `""` | `ModuleSpec` |
| `import mypackage.cli` | `"mypackage.cli"` | `"mypackage"` | `ModuleSpec` |
| `python file.py` | `"__main__"` | `None` | `None` |
| `python -m mypackage.cli` | `"__main__"` | `"mypackage"` | `ModuleSpec` |

`__name__` drives the entry-point pattern. `__file__` and `__doc__` help with inspection and documentation. `__package__` and `__spec__` become important with packages and relative imports.

## 6. `__name__` and `__main__`

`__name__` tells a file how Python is currently treating it.

```python
# greeting.py
print(f"__name__ is: {__name__!r}")
```

Run directly:

```bash
python greeting.py
```

Output:

```text
__name__ is: '__main__'
```

Import it:

```python
import greeting
```

Output:

```text
__name__ is: 'greeting'
```

Rules:

- When the file is executed as the program, Python sets its `__name__` to `"__main__"`.
- When imported, `__name__` is its module name, including the dotted package path when applicable.

`__main__` is the name assigned to the one module that is the program's entry point. It can be reached with `python file.py` or `python -m package.module`. Other imported modules retain their normal names.

## 7. The `if __name__ == "__main__":` guard

This guard makes a file both importable and executable:

```python
def greet(name: str) -> None:
    print(f"Hello, {name}!")

if __name__ == "__main__":
    greet("World")
```

- Run directly: `__name__` is `"__main__"`, so the greeting runs.
- Import elsewhere: `__name__` is the module's real name, so the guarded call does not run. The `greet` function is available to reuse.

Without the guard:

```python
def greet(name: str) -> None:
    print(f"Hello, {name}!")

greet("World")  # runs every time this module is imported
```

Any importer triggers the greeting, even if it only wanted the function. The guard protects only the statements placed inside it; unguarded top-level statements still run during import.

This pattern helps tests import a module and call a function without accidentally starting the program.

## 8. `main()` and process exit status

Putting a large program directly inside the guard becomes hard to test and reuse. Also, an `if` block does not create a new local scope: names assigned there are module-level names.

Put the entry-point logic in a function:

```python
def main() -> None:
    print("Running the program")

if __name__ == "__main__":
    main()
```

For CLI applications, the established course pattern is stronger:

```python
def main() -> int:
    print("Running the program")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

For a CLI that accepts arguments:

```python
import argparse
from collections.abc import Sequence

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="world")
    args = parser.parse_args(argv)
    print(f"Hello, {args.name}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

`argv=None` makes `argparse` read the normal command-line arguments. A test can instead call `main(["--name", "Ada"])`.

`main()` returns a normal integer that tests can inspect. `raise SystemExit(main())` translates that integer into the process exit status at one controlled location. If `argparse` rejects invalid arguments, it raises `SystemExit` itself; a test for invalid arguments must expect that exception, not a return value.

## 9. Module-level code and import-time side effects

Every top-level statement executes during import, including printing, file I/O, configuration loading, and network/database operations.

Bad design:

```python
# app.py
print("Starting application...")
connect_to_database()
config = load_config_from_disk()
```

A test that only wants one helper function still triggers all three actions. This creates:

- **Unpredictability:** importing a small utility can trigger expensive work.
- **Untestability:** tests require real external services or files.
- **Import-order fragility:** behaviour can depend on which module imported first.

Better design:

```python
# app.py
def connect_to_database():
    ...  # performs the connection only when called

def load_config_from_disk():
    ...

def main() -> int:
    print("Starting application...")
    connect_to_database()
    config = load_config_from_disk()
    ...
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Now an ordinary `import app` defines functions but does not start the application. The important rule is: definitions and harmless constants can live at module level; meaningful work should happen inside functions and be called deliberately.

## 10. Import caching and `sys.modules`

Under normal imports, a module's top-level code runs once per process.

```python
# counted.py
print("counted.py is executing")
```

```python
# main.py
import counted
import counted
```

The message prints once. The first import executes and caches the module; later imports reuse the same module object.

`sys.modules` is the actual dictionary that stores imported modules by module name:

```python
import sys
import math

print("math" in sys.modules)          # True
print(sys.modules["math"] is math)    # True
```

Python checks `sys.modules` before searching and loading. It is useful to inspect during debugging, but normal application code should not manually delete or replace entries.

Important qualifications:

- `importlib.reload()` explicitly re-executes a module.
- The cache is keyed by module name. The same source loaded under two different names can create two module objects. A file run as `__main__` and also imported by its ordinary name is an example.

## 11. `sys.path` and module search

`sys.path` is an ordered list of search locations used by the normal import system for ordinary source modules.

```python
import sys
print(sys.path)
```

It may contain:

- The script directory or current working directory, depending on invocation.
- Standard-library locations.
- Third-party installation directories such as the active environment's `site-packages`.

Python checks entries in order. `PYTHONPATH`, if set, adds further directories. Some standard-library modules (such as `sys`) are built into the interpreter and are not ordinary files found through `sys.path`.

If the required directory is not in the search locations, Python cannot find the module even if the file exists somewhere else.

## 12. `ModuleNotFoundError` versus `ImportError`

- `ModuleNotFoundError` is a subclass of `ImportError`. It indicates that the requested module name was not found in the search locations. The missing module may be a nested dependency imported by the module you requested.
- `ImportError` is broader. It can mean the module was found but the requested name does not exist, or that an exception occurred while the module was executing.

Examples:

```python
import definitely_not_a_real_module
# ModuleNotFoundError
```

```python
from math import not_a_real_function
# ImportError
```

Read the **whole traceback**. For example, if `import report` finds `report.py` but `report.py` contains `import pandas`, then the missing module is `pandas`, not `report`. Fix the dependency/environment rather than moving `report.py`.

Common causes include misspelled/case-mismatched names, wrong working directory, incorrect package structure, wrong virtual environment, missing third-party dependency, and an import path inconsistent with the way the program is run.

Systematic diagnostic code:

```python
import sys
import subprocess

print(sys.path)       # where this interpreter searches
print(sys.executable) # which Python is running
subprocess.run(
    [sys.executable, "-m", "pip", "show", "package_name"],
    check=False,
)
```

Using `sys.executable -m pip` checks the environment belonging to the running interpreter. A bare `pip` executable may belong to another Python installation.

## 13. Absolute and relative imports

An **absolute import** names the path from the top-level package:

```python
from mypackage.utils import helper
```

A **relative import** names a location relative to the current module's package:

```python
from .utils import helper   # sibling module
from ..common import helper # module in parent package
```

One dot means the same package; two dots move one package level upward.

Relative imports require package context. They work when the module is imported as part of its package or run using `python -m package.module`. They fail when the file is run as a bare script:

```text
ImportError: attempted relative import with no known parent package
```

Absolute imports are explicit and easy to read from any location. Relative imports can be convenient within a tightly related package and can make moving the package easier, but they depend on internal layout. The chapter recommends absolute imports for meaningful boundaries and relative imports mainly for close siblings.

## 14. Packages and `__init__.py`

A **package** groups related modules under one namespace:

```text
myproject/
    mypackage/
        __init__.py
        utils.py
        processing.py
    main.py
```

`mypackage.utils` mirrors the directory structure. From outside the package:

```python
from mypackage.utils import helper
from mypackage import processing
```

A regular package traditionally contains `__init__.py`. Modern Python also supports **namespace packages** without it (Python 3.3+), mainly for advanced cases where one logical package is distributed across multiple locations. For this course, an explicit `__init__.py` is the clearest default.

`__init__.py` has two roles:

1. It marks the directory as a regular package.
2. Its top-level code executes once when the package is first imported, before the requested submodule.

It may re-export names to provide a convenient package API:

```python
# mypackage/__init__.py
from .utils import helper
from .processing import transform
```

Then both forms can work:

```python
from mypackage.utils import helper  # direct submodule import
from mypackage import helper        # package-level re-export
```

An empty `__init__.py` is valid and common. Re-exports are optional API design. Avoid placing substantial work in `__init__.py`, because it can create import-time side effects.

## 15. Wildcard imports and `__all__`

A wildcard import pulls public names into the current namespace:

```python
from math import *

print(sqrt(16))
print(pi)
```

It is discouraged because it pollutes the namespace, hides where names came from, and can create silent name collisions.

A module can define `__all__` to list the names intended for wildcard export:

```python
# mymodule.py
__all__ = ["public_function"]

def public_function():
    ...

def _internal_helper():
    ...
```

Then `from mymodule import *` imports only `public_function`. `__all__` limits the wildcard export list; it does not fix the readability problem. Prefer explicit imports.

## 16. Circular imports

A circular import occurs when module A imports B and B imports A, directly or through another module.

```python
# a.py
from b import function_b

def function_a():
    return "A"
```

```python
# b.py
from a import function_a

def function_b():
    return function_a()
```

A representative error is:

```text
ImportError: cannot import name 'function_a' from partially initialized module 'a'
```

Why it happens:

1. Python creates module `a` and puts it in `sys.modules`.
2. `a.py` begins executing and imports `b`.
3. `b.py` begins executing and imports `function_a` from `a`.
4. Python finds `a` in `sys.modules`; it does not execute it again.
5. But `a.py` has not reached the `def function_a` statement yet.
6. Therefore `function_a` is not yet present, and the import fails.

The exact error wording varies by Python version. A circular-looking dependency does not always fail: `import a` and `import b` may work if the other module's names are only accessed inside functions after both imports finish. The shown `from module import name` form needs the name immediately.

Design-level fixes:

- Merge modules if they are actually one tightly coupled unit.
- Extract shared functionality into a third lower-level module.
- Reconsider dependency direction; pass a needed value/function as an argument or move a small shared responsibility.
- A local import inside a function can defer a dependency, but it is a narrow escape hatch, not the first design fix.

Trace the import chain and order to diagnose the cycle. A temporary `print(f"importing {__name__}")` at module top level can reveal the sequence.

## 17. Import style and code quality

Use these habits:

- Put imports at the top by default. A local import inside a function is appropriate only for a deliberate optional or deferred dependency.
- Group imports: standard library, third-party, then local/project imports, with blank lines between groups.
- Prefer explicit imports, not wildcard imports.
- Use meaningful aliases (`import numpy as np`, not arbitrary abbreviations).
- Remove unused imports.
- Keep imports safe and cheap: no real work at import time.
- Avoid circular dependencies by designing one-way module relationships.

Example grouping:

```python
import json
import sys
from pathlib import Path

import requests

from mypackage.utils import helper
```

## 18. A reusable module's recommended structure

```python
# report_utils.py
"""Utilities for building simple text reports."""

# Constants
DEFAULT_WIDTH = 40

# Private helper
def _pad_line(text: str, width: int) -> str:
    return text.ljust(width)

# Public function
def build_report(title: str, lines: list[str], width: int = DEFAULT_WIDTH) -> str:
    header = _pad_line(title, width)
    body = "\n".join(_pad_line(line, width) for line in lines)
    return f"{header}\n{'-' * width}\n{body}"

# Entry point
def main() -> int:
    report = build_report("Demo Report", ["line one", "line two"])
    print(report)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

The intended order is constants, private helpers, public functions, `main()`, then the guard. A leading underscore communicates internal intent; Python does not enforce privacy.

When imported, definitions are created but the report is not built or printed. When executed directly, the guard calls `main()`, prints the report, and exits with status 0.

## 19. Script versus module

- A **script** is primarily intended to be executed.
- A **module** is primarily intended to be imported and reused.

One file can intentionally support both roles using the `__main__` guard. This is a standard design, not a workaround.

## 20. `python file.py` versus `python -m package.module`

`python app.py` executes a standalone script. Python places the script's containing directory at the front of `sys.path`, so sibling imports may work. But the script has no package context: `__name__` is `"__main__"`, while `__package__` and `__spec__` are `None`. Relative imports therefore fail.

`python -m package.module` asks Python's import machinery to locate the package module and execute it as the entry point. Its `__name__` is still `"__main__"`, but `__package__` is set to the package name and relative imports work.

Example:

```text
myproject/
    mypackage/
        __init__.py
        cli.py
        utils.py
```

If `cli.py` uses `from .utils import helper`:

```bash
python mypackage/cli.py       # relative-import error
python -m mypackage.cli       # package context is available
```

For package-based applications, `-m` is usually preferable during development because it uses package-aware import behaviour and better reflects how the application will run when installed.

## 21. Imports and CLI architecture

A clean CLI architecture separates argument handling from reusable logic:

```text
CLI arguments
    ↓
main() in cli.py
    ↓
application/business logic
    ↓
helper modules and data operations
```

Example:

```python
# validators.py
def validate_positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise ValueError(f"must be positive, got {number}")
    return number
```

```python
# cli.py
import argparse
from collections.abc import Sequence
from validators import validate_positive_int

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=validate_positive_int, default=1)
    return parser

def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(f"count = {args.count}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

`validators.py` can be tested without `argparse`, `sys.argv`, or the CLI. `cli.py` stays a thin adapter.

## 22. Imports and testability

Tests must import the code they test. If import itself connects to a database, writes a file, or runs `main()`, the test inherits that side effect before it can assert anything.

A safe module contains reusable definitions without application startup logic:

```python
# validators.py
def validate_positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise ValueError(f"must be positive, got {number}")
    return number
```

Conceptual test:

```python
import pytest
from validators import validate_positive_int

def test_rejects_zero():
    with pytest.raises(ValueError):
        validate_positive_int("0")
```

The lesson is architectural: side-effect-free imports make later unit testing straightforward.

## 23. Standard-library, local, and third-party imports

- **Standard library:** ships with Python, e.g. `os`, `sys`, `json`, `csv`, `pathlib`, `argparse`, `logging`.
- **Local:** belongs to your own project, e.g. `from validators import validate_positive_int`.
- **Third-party:** published separately and installed into the active environment, e.g. `requests`, `numpy`.

```python
import json
import sys                  # standard library

import requests             # third-party

from validators import validate_positive_int  # local
```

This chapter introduces dependency categories, not full dependency installation, version pinning, lock files, `pyproject.toml`, or `uv`; those are later topics.

## 24. Dynamic imports and reload

`importlib.import_module()` imports a module whose name is known only at runtime:

```python
import importlib

module_name = "json"
json_module = importlib.import_module(module_name)
print(json_module.dumps({"key": "value"}))
```

It is useful for deliberate dynamic behaviour such as plugin selection. It is not a replacement for ordinary explicit imports.

`importlib.reload()` re-executes an already imported module's top-level code, normally reusing the same module object:

```python
import importlib
import mymodule

# Edit mymodule.py on disk
importlib.reload(mymodule)
```

Important caveats:

- A previously imported name (`from mymodule import greet`) still points to the old function object after reload.
- `mymodule.greet` may point to the new function.
- Names deleted from the source can remain in the module namespace because reload does not clear it first.
- Other code may hold old functions/classes while the module exposes new ones, creating inconsistent state.

Reload is a development/interactive convenience. Production systems should restart the process to load a consistent version.

`__spec__` describes the module's loading metadata. Module identity is shared for imports of the same module name in one process; loading the same source under a different name can create a separate object.

## 25. The chapter's import-debugging reference

Use the traceback and inspect the actual interpreter and search path before changing code.

| Symptom | Likely reason | First response |
|---|---|---|
| `ModuleNotFoundError` although file exists | Directory not in `sys.path` or wrong launch directory | Print `sys.path`; inspect working directory |
| `cannot import name X` | Name typo, rename, or name not defined at module level | Inspect the target module |
| Relative import has no known parent | Package file run directly | Use `python -m package.module` |
| Partially initialized module | Circular import | Trace dependency chain; extract shared code |
| Import prints/connects/writes unexpectedly | Top-level side effect | Move work into functions and guard entry point |
| Installed package still missing | Different Python environment | Check `sys.executable`; use `python -m pip` |
| Standard-library module behaves strangely | Local file shadows its name | Inspect `module.__file__`; rename local file |

The chapter's concrete examples include:
- A `report.py` that imports `pandas`: the traceback shows `pandas` is missing, not `report`.
- A misspelled `compute_statistics` when the actual function is `compute_stats`.
- A `mypackage/cli.py` relative import failing under direct execution but working with `-m`.
- `orders.py` and `customers.py` importing each other.
- `reporting.py` printing and building a report at import time.
- A `sys.path` assumption that differs between invocation modes.
- `pip install requests` targeting a different interpreter from `python app.py`.
- A local `email.py` or `json.py` shadowing the standard library; inspect `email.__file__` or `json.__file__`.

## 26. All 16 progressive coding examples

The chapter's examples build progressively:

1. `greetings.py` defines `hello()`.
2. `import greetings; greetings.hello()` calls it.
3. Use `import greetings as g`, `from greetings import hello`, and `from greetings import hello as say_hello`; all call the same function through different local names.
4. `dir(greetings)` lists module attributes, including `hello`.
5. `print(__name__)` shows `__main__` when run and `demo` when imported.
6. A `__main__` guard calls `hello()` only during direct execution.
7. A `main() -> None` function groups startup code.
8. `main() -> int` returns `0`, and `raise SystemExit(main())` sets the process status.
9. One file exposes reusable `add()` and an executable `main()`; importing it has no output, while direct execution prints `5`.
10. `math_ops.py` and `text_ops.py` expose `add()` and `shout()`; `app.py` imports both and prints `SUM IS 5!`.
11. A package with `__init__.py` and `utils.py` supports `from mypackage.utils import helper`.
12. A package's `cli.py` uses `from .utils import helper` and should be run with `python -m mypackage.cli`.
13. `once.py` prints at top level; two imports print the message only once due to caching.
14. A `for` loop prints each `sys.path` entry.
15. `shared.py` provides common logic imported by `a.py` and `b.py`, preventing a cycle.
16. A three-layer layout uses `validators.py`, `processing.py`, and `cli.py` with one-way dependencies.

Example 10 in full:

```python
# math_ops.py
def add(a, b):
    return a + b

# text_ops.py
def shout(text):
    return text.upper() + "!"

# app.py
from math_ops import add
from text_ops import shout

print(shout(f"sum is {add(2, 3)}"))
```

Example 15 in full:

```python
# shared.py
def shared_logic():
    return "shared"

# a.py
from shared import shared_logic
def function_a():
    return shared_logic()

# b.py
from shared import shared_logic
def function_b():
    return shared_logic()
```

## 27. Mini-project — reusable statistics CLI

The chapter's mini-project has three modules:

```text
stats_cli/
    validators.py  # validate raw input
    stats.py       # compute statistics
    cli.py         # argparse, output, exit status
```

The dependency design is one-way: the CLI imports the validator and statistics functions; the lower-level modules do not import the CLI or each other.

`validators.py`:

```python
"""Validators for the stats CLI."""

def validate_number(raw_value: str) -> float:
    try:
        return float(raw_value)
    except ValueError:
        raise ValueError(f"not a valid number: {raw_value!r}") from None
```

`stats.py`:

```python
"""Basic descriptive statistics over a list of numbers."""

def compute_stats(numbers: list[float]) -> dict:
    if not numbers:
        raise ValueError("cannot compute statistics for an empty list")
    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
    }
```

`cli.py`:

```python
import argparse
import json
import sys
from collections.abc import Sequence

from validators import validate_number
from stats import compute_stats

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute basic statistics for a list of numbers."
    )
    parser.add_argument("numbers", nargs="+", help="One or more numbers")
    return parser

def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        numbers = [validate_number(raw) for raw in args.numbers]
        result = compute_stats(numbers)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    print(json.dumps(result))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Execution with inputs `1 2 3` follows this sequence: package entry point starts → guard calls `main()` → `argparse` reads three strings → validator converts each to `float` → statistics function returns a dictionary → JSON is printed to stdout → `main()` returns `0` → `SystemExit` sets process status 0. Invalid numeric input prints an error to stderr and returns 3.

The modules can be tested independently. A new CLI option belongs in `cli.py`; a new statistic belongs in `stats.py`. Production improvements named by the source are proper logging, a `pyproject.toml` for an installable package, and static type checking.

**Source consistency note:** the lesson describes the files under a `stats_cli/` package and invokes `python -m stats_cli.cli`, but the displayed `cli.py` uses top-level imports (`from validators ...`, `from stats ...`) rather than package-relative imports. Those imports require the modules to be resolvable as top-level modules. For a conventional package layout, package-relative imports (`from .validators ...`, `from .stats ...`) would match the `python -m stats_cli.cli` invocation. This is a clarification of an inconsistency in the source example, not a change to the concepts taught.

---

# Part B — Project-Tree and Current-Level Assessment

## 1. Roadmap position

Your Stage 1 roadmap contains 24 modules, 212 numbered lessons, and 282 files. It is designed to move from programming fundamentals into production-oriented Python engineering.

Relevant completed foundations:

- Module 03: control flow, functions, parameters/returns, scope, pure functions, side effects, exceptions, validation, and useful errors.
- Module 04: problem-solving, collections, search/filter/aggregate, complexity, and algorithmic habits.
- Module 05: text files, paths, CSV, JSON, encodings/newlines, `argparse`, standard streams/exit codes, logging, and environment configuration/input validation.
- Module 05 Lessons 01–09 are recorded as completed.

The four Stage 1 projects in the roadmap are:

1. Personal Expense Ledger CLI.
2. Log Investigation and Reliability CLI.
3. Data Quality and Transformation Pipeline (`orders.csv`, `dqpipe` package with CLI/config/pipeline/rules, tests, and data contract).
4. Rule-Based Risk Review Engine (`transactions.csv`, `rules.toml`, `riskreview` package with CLI/engine/I/O/models/rules, tests, and golden decision data).

The new chapter is the next conceptual step: it takes a CLI that previously could be written in one file and teaches you how to split it into importable, testable modules.

## 2. Current learning level

Your current level is **beginner progressing toward intermediate** in Python engineering. You have enough foundation to understand:

- Function definitions and return values.
- Exceptions and input validation.
- Paths and file handling.
- CSV and JSON.
- CLI parsing with `argparse`.
- stdout/stderr and exit codes.
- Logging and environment-based configuration.
- Why reusable logic should be separated from CLI code.

The new concepts are the Python import system, module objects and namespaces, `sys.modules`, `sys.path`, package context, relative imports, circular imports, and dynamic imports. These are new topics in this lesson, so the solutions below explain them from first principles.

## 3. Scope discipline

The solutions stay within this chapter and prior Module 05 foundations. They use standard-library imports and small multi-file examples. `pytest` appears only where the source itself uses it as a conceptual test example; this is not a full testing-framework lesson.

---

# Part C — All Exercises Solved

> **Word-limit note:** This section is designed to remain under 3,500 words. Each code solution is followed by a line-by-line explanation or a precise design explanation. The chapter's debugging lab, interview questions, and knowledge check are also answered below.

## Exercise 1 — Two modules with the same function name

`module_one.py`:

```python
def describe():
    return "I am module one"
```

`module_two.py`:

```python
def describe():
    return "I am module two"
```

`main.py`:

```python
import module_one
import module_two

print(module_one.describe())
print(module_two.describe())
```

**Line by line:** each `def` creates a function in its own module namespace. The two `import` statements bind two module objects. The qualified calls select the correct function, so the names do not collide.

## Exercise 2 — Four import styles

`greeter.py`:

```python
def hello():
    return "Hello"
```

`main.py`:

```python
import greeter
import greeter as g
from greeter import hello
from greeter import hello as say_hello

print(greeter.hello())
print(g.hello())
print(hello())
print(say_hello())
```

**Line by line:** the first import binds `greeter`; the second binds the same module under `g`; the third binds its function as `hello`; the fourth binds that function as `say_hello`. Each call returns `"Hello"`. The forms change the local names, not the function's behaviour.

## Exercise 3 — Observe `__name__`

`demo.py`:

```python
print(__name__)
```

Run `python demo.py`: output is `__main__`. From another file, run `import demo`: output is `demo`.

**Explanation:** direct execution marks the file as the entry point. Importing gives it its normal module name.

## Exercise 4 — Inspect module attributes

```python
import math

print(math.__name__)
print(math.__doc__)
print(math.__spec__)
```

- `__name__` is the module's name (`math`).
- `__doc__` is its documentation string, if provided.
- `__spec__` describes how Python found/loaded it.

For a file-backed module, `__file__` can also show its source path. Some built-in modules do not have a normal filesystem path.

## Exercise 5 — Refactor top-level work into `main()`

Before:

```python
print("Writing report")
with open("report.txt", "w", encoding="utf-8") as file:
    file.write("Report")
```

After:

```python
def main() -> int:
    print("Writing report")
    with open("report.txt", "w", encoding="utf-8") as file:
        file.write("Report")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

**Line by line:** `main()` contains the real work; the `with` block safely manages the file; `return 0` reports success; the guard calls it only when this file is executed; `SystemExit` converts the returned status into the process exit code. Importing this file now defines `main()` but does not write the file.

## Exercise 6 — Package import and re-export

Structure:

```text
mypackage/
    __init__.py
    utils.py
```

`utils.py`:

```python
def helper():
    return "helping"
```

Absolute import:

```python
from mypackage.utils import helper
print(helper())
```

Add this to `__init__.py`:

```python
from .utils import helper
```

Now this also works:

```python
from mypackage import helper
print(helper())
```

**Explanation:** the first form names the submodule directly. The second works because package initialization re-exports `helper` at package level. The leading dot means the sibling `utils` module inside the same package.

## Exercise 7 — Relative import and invocation

Structure:

```text
project/
    mypackage/
        __init__.py
        utils.py
        cli.py
```

`utils.py`:

```python
def helper():
    return "helping"
```

`cli.py`:

```python
from .utils import helper

def main() -> int:
    print(helper())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

From the `project` directory:

```bash
python -m mypackage.cli
```

This works because Python supplies package context. This fails:

```bash
python mypackage/cli.py
```

Direct execution has no parent package context, so `.` cannot be resolved.

## Exercise 8 — Demonstrate caching

`once.py`:

```python
print("module loaded")
```

`main.py`:

```python
import once
import once
```

The message appears once. The first import executes the module and stores it in `sys.modules`; the second import reuses the cached object.

## Exercise 9 — Inspect `sys.path`

```python
import sys

for entry in sys.path:
    print(entry)
```

The loop prints each search location in order. Depending on how Python was invoked, the first entry may be the script directory or an empty string representing the current working directory. Do not assume: inspect the actual value and compare it with the script's location.

## Exercise 10 — Create and fix a circular import

Problem:

`a.py`:

```python
from b import function_b

def function_a():
    return "A"
```

`b.py`:

```python
from a import function_a

def function_b():
    return function_a()
```

The first module asks for the second; the second immediately asks for a name from the first before the first has defined it. Python reports a partially initialized module.

Fix by extracting common work:

`shared.py`:

```python
def shared_logic():
    return "shared"
```

`a.py`:

```python
from shared import shared_logic

def function_a():
    return shared_logic()
```

`b.py`:

```python
from shared import shared_logic

def function_b():
    return shared_logic()
```

**Why this is better:** both modules depend on a lower-level shared module; neither depends on the other. Reordering imports only changes timing and leaves the circular design intact.

## Exercise 11 — Three-module CLI with one-way dependencies

Structure:

```text
myapp/
    validators.py
    processing.py
    cli.py
```

`validators.py`:

```python
def validate_positive(value: int) -> bool:
    return value > 0
```

`processing.py`:

```python
from validators import validate_positive

def double_positive(value: int) -> int:
    if not validate_positive(value):
        raise ValueError("value must be positive")
    return value * 2
```

`cli.py`:

```python
import argparse
from collections.abc import Sequence
from processing import double_positive

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("value", type=int)
    args = parser.parse_args(argv)
    try:
        print(double_positive(args.value))
    except ValueError as exc:
        parser.error(str(exc))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

**Line by line:** the lowest layer validates; the processing layer imports validation and implements business logic; the CLI imports processing and owns argument parsing and process entry. Dependencies point one way: `cli → processing → validators`. A new business rule belongs in the lowest appropriate reusable layer, not in a lower module that would need to import the CLI.

## Exercise 12 — Remove an import-time side effect

Bad:

```python
print("Connecting")
connection = connect_to_service()
```

A test importing this module prints and attempts the connection even if it only needs a helper.

Better:

```python
def connect():
    print("Connecting")
    return connect_to_service()

def main() -> int:
    connect()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

The connection occurs only when `main()` is called by direct execution. An importer can use the function definitions without starting the service.

## Exercise 13 — Why prefer `python -m` for packages?

`python -m package.module` locates the module through Python's import system and gives it package context, so relative imports work. `python package/module.py` treats it as a standalone script with no parent package context. The module invocation also better reflects how a real package is imported and run.

## Exercise 14 — Reusable and executable module

```python
def add(a: int, b: int) -> int:
    return a + b

def main() -> int:
    print(add(2, 3))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- `add()` is reusable business logic.
- `main()` owns the executable demonstration and returns a status.
- The guard prevents the demonstration from running on import.
- `SystemExit` translates the return value into the OS process status.

This is more testable than a `main()` that returns nothing because a test can call `main()` and inspect its integer result without terminating the test process.

---

# Part D — Debugging Lab Answers

1. **File exists but `ModuleNotFoundError`:** print `sys.path`; the file's directory may not be included. Run from the correct location or package the project and use `python -m`.
2. **`cannot import name`:** check the exact function spelling and whether it is defined at module level. Change the import to the real name.
3. **Relative import failure:** direct script execution has no package context. Run `python -m mypackage.cli`.
4. **Circular import:** trace the import chain and identify mutual dependencies. Extract shared logic into a third module.
5. **Unexpected print/network action during import:** inspect bare module-level statements. Move real work into functions and call them through the guard.
6. **Different `sys.path` under different launch modes:** print and compare `sys.path` for both. Prefer a proper package and package-aware invocation rather than relying on an assumed path.
7. **Wrong Python environment:** inspect `sys.executable`; install using `python -m pip install package_name` with the same interpreter used to run the program.
8. **Local `email.py` or `json.py` shadows standard library:** inspect `module.__file__`; rename the local file so it no longer collides.

---

# Part E — Interview and Architecture Questions

1. **Module:** a named, import-managed unit of code, commonly a `.py` file, intended for reuse.
2. **Import sequence:** check cache, find module, create object, cache it, execute top-level code, then bind requested names.
3. **Why not copy-paste:** import executes code and creates a module object with its own namespace.
4. **Namespace:** mapping of names to objects; module attributes are kept in that module's namespace.
5. **`__name__`:** normal dotted module name when imported; `"__main__"` when executed as entry point.
6. **`__main__`:** the entry-point module. Direct file execution has no package context; `-m` has package context.
7. **Guard:** makes one file both importable and executable without running the executable part during import.
8. **`main() -> int` plus `SystemExit`:** the function's result is testable; one final line maps it to process status.
9. **Caching:** normal imports execute once per process; `sys.modules` stores module objects by name.
10. **`sys.path`:** ordered module-search locations.
11. **`ModuleNotFoundError` vs `ImportError`:** requested module not found versus broader import failure, including a missing name inside a found module.
12. **Absolute vs relative:** full package path versus location relative to package; relative imports need package context.
13. **`__init__.py`:** marks a regular package, initializes it, and may re-export names; it may be empty.
14. **Wildcard import:** pollutes names and hides origins; `__all__` restricts wildcard exports.
15. **Circular import:** mutual dependency; a module is found in cache before all its names have been defined.
16. **Design fixes:** extract shared code, merge tightly coupled modules, or reverse/rethink dependency direction.
17. **Import-time side effect:** real work triggered merely by import; makes code unpredictable and hard to test.
18. **`python file.py` vs `-m`:** standalone script without package context versus package-aware module execution.
19. **Testability:** safe imports let tests call functions without triggering startup, I/O, or external connections.
20. **Import origins:** standard library ships with Python; local is project code; third-party must be installed.
21. **`importlib.import_module()`:** imports by runtime string name, useful for plugin-like dynamic selection.
22. **`importlib.reload()`:** re-executes code but cannot update old references elsewhere; use for interactive development, not production deployment.

---

# Part F — Knowledge Check Answers

1. **Why can two modules use the same function name?** Each function belongs to its own module namespace and is accessed as `module.function`.
2. **Why execute top-level code on import?** That execution creates the module's functions, classes, and variables and populates the module object.
3. **`mystery.py` output:** direct run prints `Loading: __main__` then `Running`; import prints `Loading: mystery` only. The guard is true only for direct execution.
4. **Two `dumps` imports:** the second silently shadows the first. Use module-qualified calls or an alias.
5. **Three imports of `once`:** `"side effect"` prints once because later imports reuse `sys.modules`.
6. **`-m` works but direct run fails:** direct execution has no package context for the relative import.
7. **Refactor file write:** move the write into `main()` and add `if __name__ == "__main__": raise SystemExit(main())`.
8. **Three-file acyclic CLI:** pure low-level validators, middle processing that imports validators, top-level CLI that imports processing; lower layers never import upward.

---

# Part G — Production Checklist

Use this checklist when reviewing a multi-module Python application.

- [ ] Each module has one clear responsibility.
- [ ] Dependencies flow in one direction.
- [ ] Imports are explicit, grouped, used, and normally at the top.
- [ ] Local files do not shadow standard-library or popular third-party names.
- [ ] No I/O, network calls, printing, or shared-state mutation occur at bare module level.
- [ ] Meaningful work lives in functions.
- [ ] No circular imports; extract shared logic when needed.
- [ ] Executable files have `main() -> int` and `raise SystemExit(main())`.
- [ ] Reusable/executable files use the `__main__` guard.
- [ ] Package modules that need package context are run with `python -m package.module`.
- [ ] `__init__.py` is present for regular packages and contains only deliberate, lightweight re-exports or nothing.
- [ ] Business logic can be imported and tested without CLI/process concerns.
- [ ] Importing a module does not connect to a database, call a network service, or write files.
- [ ] When imports fail, inspect `sys.path` and `sys.executable` first.
- [ ] Use the traceback and distinguish `ModuleNotFoundError` from `ImportError`.

---

# Final Revision Notes

1. **Most important mental model:** importing finds, creates, caches, and executes a module object; it does not paste code into the importer.
2. **Most important safety rule:** keep imports side-effect-free.
3. **Most important executable pattern:** `main() -> int` followed by `if __name__ == "__main__": raise SystemExit(main())`.
4. **Most important package rule:** use `python -m package.module` when package context and relative imports are required.
5. **Most important architecture rule:** make dependencies flow in one direction; shared code belongs in a lower-level module.
6. **Most important debugging rule:** inspect the traceback, `sys.path`, `sys.executable`, and `module.__file__` before changing paths or reinstalling packages.

**Chapter completion target:** You should be able to explain imports, write a reusable module, build a small package-based CLI, avoid import-time side effects and circular imports, and diagnose common import failures without guessing.
