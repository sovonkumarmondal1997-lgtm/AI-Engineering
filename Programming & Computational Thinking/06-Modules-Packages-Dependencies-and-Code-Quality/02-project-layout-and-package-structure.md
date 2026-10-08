# Project Layout and Package Structure

## Learning Objectives

By the end of this chapter you will be able to:

- Explain what a project layout is and why deliberate file/folder
  organization matters as a Python codebase grows beyond a handful of
  files.
- Clearly distinguish a file, a module, a package, and a project, and
  explain how each nests inside the next.
- Explain and compare the **flat layout** and the **src layout**,
  including their real tradeoffs — not "src is always better."
- Design a package's internal structure: subpackages, module
  boundaries, `__init__.py`'s role, and the difference between public
  and private (underscore-prefixed) modules.
- Separate a project into responsibility layers (CLI, configuration,
  validation, business logic, I/O) and explain why dumping everything
  into one `main.py` breaks down as a project grows.
- Organize a CLI application's source tree using everything Module 1.5
  taught (argparse, streams/exit codes, logging, configuration,
  validation, file processing) and this module's own import/module
  foundations.
- Place a `tests/` directory correctly relative to source code, and
  explain why tests are conventionally kept separate from application
  code.
- Explain what `pyproject.toml` is for, at a foundational level,
  without duplicating this module's dedicated dependency-management
  chapter.
- Distinguish source code, project configuration, runtime
  configuration, and secrets — and where each belongs (or explicitly
  does not belong) in version control.
- Organize data directories, scripts, and CLI entry points sensibly.
- Explain how project layout affects import resolution, and diagnose
  the resulting `ModuleNotFoundError`/import problems systematically.
- Recognize how poor package boundaries create circular dependencies,
  and redesign around them.
- Compare feature/domain-based and layer-based organization for larger
  applications, and explain why neither is universally correct.
- Evolve a project's structure appropriately as it grows, avoiding both
  "everything in one file" and premature over-engineering.
- Design a stable public package API, distinguishing it from internal
  implementation modules.
- Explain namespace packages and the source-tree-to-installed-package
  relationship at a conceptual level.
- Explain how good project structure supports readability,
  maintainability, testing, code review, onboarding, and debugging.
- Design a complete, production-oriented Python CLI project layout
  from scratch, and justify every directory and file in it.

## Prerequisites

This chapter builds directly on
[01-imports-modules-and-main.md](01-imports-modules-and-main.md) —
modules, packages, `__init__.py`, namespaces, absolute/relative
imports, circular imports, and the `main() -> int` /
`if __name__ == "__main__":` pattern are all assumed knowledge here,
reused rather than re-taught. It also draws on Stage 1 Module 1.5's
CLI, streams/exit-codes, logging, and configuration/validation
chapters as the concrete responsibilities a well-organized project
needs to house. Packaging and dependency management
(`pyproject.toml`, lock files, `uv`) are introduced here only at the
depth needed to understand project layout — the dedicated chapters
later in this module cover them in full.

## 1. What Is a Project Layout?

A **project** is the complete collection of files that make up one
piece of software — source code, tests, configuration, documentation,
and metadata, all together, usually living inside one directory (and
one version-control repository). A **project layout** is simply *how
those files and folders are organized* — which files live where, and
why.

For a five-line script, layout barely matters — a single file is
layout enough. The moment a project grows past that point, though,
layout stops being a cosmetic choice and starts being an **engineering
decision** with real consequences:

- **Maintainability** — can a new contributor (or you, in six months)
  find the code responsible for a given behavior without searching the
  entire codebase?
- **Imports** — [01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
  §13–§15 already established that *where* a file lives directly
  determines how (and whether) it can be imported — project layout is
  what determines those locations in the first place.
- **Testing** — can the test suite exercise application logic without
  fighting the project's own structure to do it?

A tiny, concrete before/after makes the stakes vivid. Consider a
single file that reads a CSV, validates it, and prints a summary — all
in one 200-line `app.py`. Six months later, someone needs to add a
second input format. Where does that logic go? Is it safe to change
the validation without breaking the CLI parsing that happens to live
in the same file? Nothing about the *file* answers these questions —
only **structure** does, by giving each responsibility its own,
predictable home. This chapter is about designing that structure
deliberately, not by accident.

The relationship layout governs, stated simply and expanded in full
through §2: **folders group related files; files (modules) group
related code; and the way you nest folders and files is what Python's
own import system (`sys.path`, packages, `__init__.py` — all from the
previous chapter) actually navigates at runtime.** Layout is not
decoration on top of the code — it *is* one of the mechanisms the code
runs through.

## 2. File vs. Module vs. Package vs. Project

Four terms this chapter uses precisely, building directly on
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s §1
and §16:

```
PROJECT
├── PACKAGE
│   ├── MODULE
│   └── MODULE
└── tests/
```

- **File** — the plain, general term for anything stored on disk;
  `notes.txt` is a file, and so is `utils.py`.
- **Module** — a named unit of Python code that can be imported and
  that provides its own namespace, as `01`'s §1 established. A `.py`
  source **file** is the most common way to define one, and the only
  kind this chapter works with; not every file is meant to be a module
  (a `README.md` is a file, never a module).
- **Package** — a **directory** of related modules, given its own
  namespace — conventionally a *regular package* via `__init__.py`
  (or, for namespace packages, §23, without one). A package can itself contain **subpackages** —
  packages nested inside packages.
- **Project** — the **whole** thing: one or more packages, plus tests,
  configuration, documentation, and metadata, organized under one root
  directory.

A concrete, minimal example tying all four together:

```
weather_cli/                  ← PROJECT (the whole repository)
├── src/
│   └── weather/               ← PACKAGE (a directory, has __init__.py)
│       ├── __init__.py
│       ├── cli.py              ← MODULE (a single .py file)
│       └── forecasting.py       ← MODULE
├── tests/
│   └── test_forecasting.py
└── pyproject.toml
```

`weather` is a (regular) package because it's a directory containing an
`__init__.py`; `cli.py` and `forecasting.py` are modules because
they're individual, importable `.py` files inside it;
`weather_cli/` — the whole repository, including `tests/` and
`pyproject.toml`, neither of which is Python source code meant to be
imported by the application itself — is the project. Every section
from here forward is about how to arrange exactly this kind of
structure well, as complexity grows.

## 3. Simple Python Project Structure

The most natural starting point for a small program:

```
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

**What works here:** `app.py` and `utils.py` sit side by side, so
`from utils import load_numbers` works without any special
configuration — Python adds a script's own directory to `sys.path`
automatically (per
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
§23), and both files are right there. For a genuinely small tool, this
is not a "wrong" structure — it's appropriately simple for the problem
size.

**What becomes difficult as it grows:** there's no clear place for
tests (dropping a `test_utils.py` next to `utils.py` works, but starts
cluttering the same flat list of files); there's no package namespace
at all (`utils` is a bare top-level module name — any other project
or dependency that also happens to define a module named `utils`
risks a naming collision, per
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
§28 scenario 7); and as more files accumulate (`validators.py`,
`config.py`, `logging_setup.py`, ...), the project root becomes a flat,
undifferentiated pile with no grouping at all. §4–§5 show the two
standard next steps.

## 4. Flat Project Layout

The first real step up in structure — introducing a proper package,
while keeping it directly at the project root:

```
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

This is called a **flat layout** because the importable package
(`package/`) sits directly inside the project root, at the same level
as `tests/` and `pyproject.toml` — nothing extra wraps around it.

**Advantages:** simple and immediately understandable; one less level
of nesting than the src layout (§5); works fine for small-to-medium
projects, and is genuinely common in real, well-maintained open-source
projects.

**Disadvantages, and the specific risk they create:** because the
project root itself (where you typically run commands *from*) is on
`sys.path` when you run scripts or tests from there, it becomes
possible to accidentally import the **local, uninstalled** `package/`
directory directly — even when you *meant* to test against the
actually-**installed** version of your package (the one `pip install`
or an editable install would put in `site-packages`). If your test
suite silently imports the local source tree instead of the installed
package, a packaging mistake (a file that works locally but was never
actually included in the built package) can go completely undetected
until a real user installs it and it breaks.

**Import behavior and testing considerations:** running `pytest` from
the project root with a flat layout typically finds and imports
`package/` directly off disk, bypassing installation entirely — fast
and simple, but exactly the blind spot described above.

**When it's appropriate:** small-to-medium projects, especially ones
not primarily distributed as an installable package (e.g., an internal
tool run directly from a cloned repository, rather than `pip
install`ed by end users) — where the accidental-local-import risk
above matters much less, because there's no meaningfully different
"installed" version to diverge from in the first place.

## 5. `src/` Layout

The alternative, increasingly the default recommendation for
distributable Python packages:

```
project/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── cli.py
│       └── utils.py
├── tests/
│   └── test_utils.py
├── pyproject.toml
└── README.md
```

The only structural difference from §4 is one extra directory:
`mypackage/` lives *inside* `src/`, rather than directly at the
project root.

**Why this exists — the specific problem it prevents:** with a src
layout, the project root itself contains **no importable package** at
all — only `src/` (which is not, itself, added to `sys.path`
automatically the way the project root is). This means that
`import mypackage` run from the project root will not work merely
because `src/mypackage` exists. The recommended, normal way to make it
importable while developing is a proper **installation** — most
commonly an **editable install**
(conceptually: telling Python "treat this source directory as if it
were installed, but keep reading directly from these files as I edit
them," a mechanism this module's dedicated packaging chapter covers in
full) — which encourages your development and testing environment to
exercise the *exact same* import path a real end user's installation
would use. (Python can also import the package if `src/` is placed on
`sys.path` some other deliberate way — running from inside `src/`,
`PYTHONPATH`, or IDE/test-runner configuration — but those are
workarounds, not the preferred project-structure solution.) The exact
bug §4 described — a test accidentally passing
against local files that were never actually included in the shipped
package — becomes structurally much harder to hit by accident, because
there's no "local package sitting right there in `sys.path`" to
accidentally fall back on.

**Editable installation, briefly:** rather than copying `mypackage`'s
files into `site-packages`, an editable install registers a pointer
back to `src/mypackage`, so changes to the source are picked up
immediately without reinstalling — combining the convenience of
editing files directly with the correctness of testing through the
real installed-package import path. The full mechanics (and the exact
command) belong to this module's packaging/dependency-management
chapters; what matters here is *why* this exists, structurally.

**Testing implications:** a test suite for a src-layout project
imports `mypackage` exactly the way a real user would (`import
mypackage`), never `from src.mypackage import ...` or anything path-
dependent — this is a direct, deliberate consequence of the src
directory not being importable on its own.

**Packaging implications:** because `src/` cleanly separates
"everything that gets built and shipped" (inside `src/mypackage/`)
from "everything that supports development but isn't part of the
package" (`tests/`, docs, project metadata), it's structurally harder
to accidentally ship a test file, a scratch script, or other
development-only cruft as part of the actual distributed package.

**Flat vs. src — the honest tradeoff, not "src is always better":**

| | Flat layout | src layout |
|---|---|---|
| Setup simplicity | Slightly simpler, one less directory | One extra level of nesting |
| Accidental local-import risk | Real — the package is directly importable from the project root | Substantially reduced — normally an install (or deliberate path setup) is needed |
| Best fit | Small tools, internal scripts, projects not meaningfully "installed" separately from their source checkout | Any project meant to be properly installed and distributed (a real library, a packaged CLI tool) |
| Learning curve | None beyond ordinary imports | Requires understanding editable installs |

For a small learning project or an internal script you'll always run
directly from its own checked-out directory, flat is perfectly
reasonable. For anything meant to be `pip install`ed — by other
people, in CI, or even just by "future you" from a different
directory — src is the safer default, precisely because it encourages the
installed-package import path to be exercised from day one, rather
than only being discovered as a surprise later.

## 6. Package Structure

Inside a package, modules can be organized flat, or grouped further
into **subpackages** — packages nested inside packages — once related
modules start accumulating.

```
mypackage/
├── __init__.py
├── module_a.py
├── module_b.py
└── subpackage/
    ├── __init__.py
    └── module_c.py
```

`mypackage.module_a`, `mypackage.module_b`, and
`mypackage.subpackage.module_c` are each independently importable,
with names that directly mirror this directory structure — exactly
the dotted-name-mirrors-directory-structure relationship
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
§16 introduced, now with one additional level of nesting.

**Package namespace:** `mypackage` itself is one namespace
(`mypackage.some_name`); `mypackage.subpackage` is a *nested* namespace
within it — this is precisely how a package's internal organization
can grow without every module needing a globally unique, increasingly
long name (`module_c` doesn't need to be renamed
`mypackage_subpackage_module_c` — its position in the package tree
already disambiguates it).

**Module boundaries:** each module should have one clear
responsibility (a direct application of §1's maintainability point) —
`module_a.py` handling one concern, `module_b.py` another, rather than
either growing to hold everything.

**Package API vs. internal modules:** which of `mypackage`'s modules
and names are meant to be used by code *outside* the package, and
which are purely internal implementation detail the package is free to
change later — this distinction, introduced here, is developed fully
in §22.

## 7. `__init__.py`

[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
§17 already covered `__init__.py`'s mechanics in full — this section
applies that knowledge specifically to project *layout* decisions.

```python
# mypackage/__init__.py — deliberately minimal
```
An **empty** `__init__.py` is completely valid and extremely common —
its only job, in this form, is marking `mypackage/` as an importable
package, with every submodule imported explicitly by its full path
(`from mypackage.module_a import something`).

```python
# mypackage/__init__.py — re-exporting a curated public API
from .module_a import public_function
from .processing import process_data

__all__ = ["public_function", "process_data"]
```
This lets users of the package write the shorter
`from mypackage import public_function` instead of reaching into
`mypackage.module_a` directly — a deliberate **package API design**
choice (§22), not a requirement.

**Avoiding excessive logic in `__init__.py`:** because
`__init__.py`'s own top-level code runs the first time *anything*
inside the package is imported (per the previous chapter's §17), any
import-time side effect placed there (§10 of the previous chapter)
affects *every single import* of *anything* in the whole package —
the widest possible blast radius for that mistake. **When
`__init__.py` should remain minimal:** as a strong default, unless you
have a specific, deliberate reason to re-export a curated public API
(§22) — an empty or near-empty `__init__.py`, with real logic living
in properly named submodules, is almost always the safer, more
predictable choice.

## 8. Public vs. Private Modules

Python has a **naming convention**, not an enforced access-control
mechanism, for signaling which modules and names are part of a
package's intended public interface and which are internal
implementation detail.

```
mypackage/
├── __init__.py
├── processing.py          ← public — meant to be imported by users of this package
└── _internal_helpers.py    ← private — an implementation detail; not meant to be imported directly
```

```python
# _internal_helpers.py
def _format_row(row):   # leading underscore: also signals "internal" at the function level
    ...
```

**What "private" means in Python:** a single leading underscore
(`_internal_helpers.py`, or `_format_row`) is a **convention**,
understood by every experienced Python developer (and respected by
tools like `from module import *`, which skips underscore-prefixed
names by default) — it is *not* enforced by the language the way
`private` is enforced in some other languages. Nothing stops another
file from writing `from mypackage._internal_helpers import
_format_row` and importing it anyway; Python simply trusts you not to.

**Why naming conventions matter anyway:** they communicate *intent*
clearly, even without hard enforcement — a leading underscore tells
every future reader (including future you) "this can change or
disappear without warning; don't build anything on it," which is
exactly the signal §22's stable-public-API discussion depends on. A
package's author is free to completely rewrite `_internal_helpers.py`
between versions without it counting as a breaking change to the
package's actual, documented interface — because nothing outside the
package was ever supposed to depend on it directly.

## 9. Project Responsibility Boundaries

A direct, structural application of the layering principle
`07-standard-streams-and-exit-codes.md`'s §45 and
`09-environment-configuration-and-input-validation.md`'s §21–§22
already introduced at the *function* level — now expressed as actual
project structure:

```
CLI layer                  (argparse, main(), stdout/stderr, exit codes)
        ↓
application/service layer    (coordinates: parses input, calls domain logic, formats output)
        ↓
domain/business logic          (the actual rules and computations — no I/O, no CLI knowledge)
        ↓
data/file layer                  (reading/writing files, CSV/JSON, the filesystem)
```

**Why putting everything into `main.py` becomes difficult**, concretely:
a single file mixing argument parsing, validation, business logic, and
file I/O has no internal boundaries at all — testing the business
logic in isolation requires also exercising (or elaborately mocking)
argparse and file I/O; adding a second input format means editing the
same file that also handles CLI parsing, risking breaking one while
changing the other; and a new contributor has no way to answer
"where's the actual validation logic?" without reading the entire file
top to bottom.

**Bad:**
```python
# main.py — everything in one file, one function
def main():
    import sys, argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    with open(args.file) as f:
        rows = [line.split(",") for line in f]   # parsing AND "business logic" tangled together

    total = 0
    for row in rows:
        if len(row) != 2:
            print("bad row", file=sys.stderr)
            continue
        total += float(row[1])
    print(total)
```

**Better — the same behavior, split along the responsibility
boundaries above:**
```
project/
├── src/
│   └── app/
│       ├── cli.py          # argparse + main() — the CLI layer
│       ├── processing.py    # reads rows, coordinates validation + summing — the service layer
│       └── validators.py     # validate_row(row) -> float — pure domain logic
```
Each file now answers one question, and each can be tested (or
changed) independently — exactly the payoff
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s §24
and §30 mini project demonstrated at the module level; this section is
that same idea, scaled up to project structure.

## 10. Organizing CLI Applications

Bringing every relevant Module 1.5 topic together into one concrete,
justified project structure:

```
project/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── cli.py               # argparse + main() -> int + __main__ guard
│       ├── config.py             # AppConfig, build_config() — env + CLI precedence, validation
│       ├── logging_config.py      # configure_logging() — handlers, formatters, levels
│       ├── validation.py           # reusable validators — pure functions, no I/O
│       └── processing.py            # the actual business logic — reads/transforms/writes data
├── tests/
├── pyproject.toml
└── README.md
```

What each file owns, and why it's separate:

- **`cli.py`** — the thin CLI layer: builds the `argparse.ArgumentParser`,
  defines `main(argv) -> int`, and holds the `__main__` guard. This is
  the *only* file that should import `argparse` or reference `sys.argv`
  directly, per
  [06-command-line-arguments-with-argparse.md](../05-Text-Files-Structured-Data-and-CLI-Programs/06-command-line-arguments-with-argparse.md)'s
  thin-CLI-layer principle.
- **`config.py`** — configuration precedence and validation, per
  [09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
  `build_config()`/`AppConfig` pattern; the *only* file reading
  `os.environ` directly.
- **`logging_config.py`** — one place that calls
  `logging.basicConfig()`/`dictConfig()`, per
  [08-logging-versus-print.md](../05-Text-Files-Structured-Data-and-CLI-Programs/08-logging-versus-print.md)'s
  centralized-configuration principle.
- **`validation.py`** — small, pure, reusable validator functions with
  no CLI, logging, or I/O dependencies at all — trivially unit-testable
  in isolation.
- **`processing.py`** — the actual work the tool exists to do,
  depending only on already-validated inputs, never on `argparse` or
  `os.environ` directly.

`cli.py` is the only file that imports from the others; none of
`config.py`, `logging_config.py`, `validation.py`, or `processing.py`
needs to import from `cli.py` — the same one-directional dependency
shape
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s §30
mini project used, now scaled to five files, with each Module 1.5
concept given its own clearly-named home.

## 11. Tests Directory

`tests/` is placed **outside** the package's own source tree —
directly at the project root, as a sibling to `src/` (or the flat
package directory, §4), rather than nested *inside* the package
itself. This is the convention this chapter recommends, not a Python
language requirement — some projects place certain tests elsewhere
depending on their repository architecture and tooling.

```
project/
├── src/
│   └── app/
│       ├── validators.py
│       └── processing.py
└── tests/
    ├── test_validators.py
    └── test_processing.py
```

**Why tests are kept separate from application source:** tests are
*about* the application code, not *part of* what the application
actually ships and runs in production — keeping them separate means a
built/installed package doesn't need to include test files at all, and
anyone browsing `src/app/` sees only real application code, without
test files interleaved among it.

**Test file naming and organization:** a common, simple convention —
one test file per source module, named `test_<module_name>.py`, as
shown above — makes it immediately obvious which tests exercise which
piece of source code, without needing any other documentation to find
them. As a test suite grows, subdirectories mirroring the package's
own subpackage structure (`tests/processing/test_transform.py`
alongside `src/app/processing/transform.py`) extend this same mapping
principle.

**Unit tests vs. integration-style tests**, at the conceptual level
this chapter needs (the dedicated testing module covers this in full):
a **unit test** exercises one small piece of logic in isolation (e.g.
`test_validators.py` calling `validate_row(...)` directly, with no
files, no CLI, no real I/O involved); an **integration-style test**
exercises several pieces working together (e.g. calling `main([...])`
end to end and checking its printed output and exit code, the same
pattern used throughout Module 1.5's own test examples). A well-
structured project supports both naturally, precisely *because* its
responsibility boundaries (§9) make it possible to test `validators.py`
completely alone.

## 12. Project Metadata

**`pyproject.toml`** is the standard, modern file describing a Python
project's own metadata — its name, version, dependencies, and build
configuration — conventionally placed **at the project root** (build tools look for it
there), sitting alongside `src/`/`tests/`, rather than inside the
package itself.

```toml
[project]
name = "app"
version = "0.1.0"
description = "A small data-processing CLI."
requires-python = ">=3.11"
```

At the foundational level this chapter needs: `[project]` holds basic
**package metadata** (name, version, description); a (not-shown-in-
depth-here) dependencies list declares what third-party packages the
project needs, conceptually extending
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s §26
distinction between standard-library, local, and third-party imports —
every third-party import a project's own code uses should correspond
to an entry here; **build configuration** (also not covered in depth
here) tells installation tools how to actually turn this source tree
into an installable package; and **tool configuration** sections
(for a linter, a formatter, a type checker — later chapters in this
module) commonly live in this same file too, under their own named
sections.

**Why `pyproject.toml` belongs at project root**, not inside `src/` or
the package directory: it describes the **project as a whole** —
including `tests/`, documentation, and tooling configuration, none of
which is part of the installable package itself — so its natural home
is the root that contains *everything*, not a subdirectory that
contains only the shippable source code. This chapter deliberately
stops here — full dependency declaration, version pinning, lock files,
and `uv` usage are this module's next dedicated chapters.

## 13. README and Documentation Files

Alongside `pyproject.toml`, a handful of other files conventionally
live at the project root:

- **`README.md`** — the first thing anyone (a new contributor, a user,
  future you) reads to understand what the project does and how to
  use it; conventionally covers what the project is, how to install/
  run it, and basic usage examples.
- **`LICENSE`** — states the legal terms under which the project's
  code may be used, modified, or redistributed — relevant the moment a
  project is shared with anyone else, even informally.
- **`.gitignore`** — tells Git which files/patterns to *never* track
  (build artifacts, virtual environment directories, local `.env`
  files, per §14) — this chapter does not teach Git itself, but the
  file's *purpose within project layout* (keeping generated/local-only
  files out of version control) is directly relevant here.
- **`pyproject.toml`** — already covered in §12; listed again here
  simply to confirm it belongs in this same root-level group.

By convention, all four sit at the project root (this is a
project-layout convention, not a Python requirement) for the same
underlying reason `pyproject.toml` does: they describe or govern the project **as a
whole**, not any one specific package or module inside it.

## 14. Configuration Files

Four genuinely different things, worth telling apart precisely,
directly extending
[09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
§1 into project-layout terms:

| Kind | Example | Belongs in version control? | Lives where |
|---|---|---|---|
| **Source code** | `cli.py`, `processing.py` | Yes | `src/` |
| **Project configuration** | `pyproject.toml` | Yes | project root |
| **Runtime configuration** | a `config.yaml` a deployment supplies | Usually not itself (a *template*/example version is) | project root or a `config/` directory |
| **Environment configuration / secrets** | `.env`, real API keys | **Never** the file with real values | `.gitignore`d locally; real values live only in the actual deployment environment |

**Why secrets should not be placed in source-controlled configuration
files**: this is exactly the rule
[09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
§5–§6 established for `.env` files and hard-coded secrets, restated
here as a *layout* rule — a project's structure should make the safe
choice the *obvious* one: an `.env.example` (with placeholder values,
safe to commit) sits at the project root; the real `.env` (with actual
secrets) is `.gitignore`d and never committed at all. Structuring a
project this way means a new contributor sees exactly which
environment variables are expected (from `.env.example`) without ever
being tempted to commit their own real values by accident.

## 15. Data Directories

Where project **data** (as opposed to source code) lives is itself a
layout decision:

```
project/
├── src/
├── tests/
└── data/
    ├── raw/          # original, unmodified input data
    ├── processed/     # generated output — the result of running the pipeline
    └── fixtures/       # small, deliberately-crafted files used by tests
```

- **Source data** (`data/raw/`) — the original input a program
  processes; whether this belongs in version control depends entirely
  on its size and sensitivity (a small, stable reference dataset might
  reasonably be committed; a large or frequently-changing one usually
  should not be).
- **Generated data** (`data/processed/`) — output *produced by running*
  the program; this should generally **not** be committed at all — it
  can always be regenerated by re-running the pipeline against the raw
  data, and committing it just adds noise (and staleness risk) to
  version control.
- **Temporary data** — scratch files a program creates and discards
  during a run; these belong in a genuinely temporary location (or a
  `.gitignore`d directory), never checked in.
- **Test fixtures** (`data/fixtures/`, or often `tests/fixtures/`) —
  small, deliberately crafted input files a test suite depends on
  (e.g. a three-row CSV with a known-good and a known-bad row) — these
  *are* typically committed, since they're small, stable, and
  essential for the tests to run at all.

**Why large or generated data should not automatically be committed**:
version control (particularly Git) is built for tracking meaningful
changes to relatively small text files over time — it handles large
binary or frequently-regenerated data poorly (bloating repository
size, slowing every clone, and providing little real value once the
data can simply be regenerated). This chapter's concern is purely
*where such data belongs structurally* — the mechanics of `.gitignore`
patterns themselves are outside this chapter's scope.

## 16. Scripts and Entry Points

A useful three-way distinction, directly extending
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s §22
(script vs. module):

- **Reusable package code** — lives inside the package (`src/app/`),
  designed to be imported, with no unwanted side effects (per the
  previous chapter's §10, §21).
- **One-off scripts** — small, standalone files for a specific,
  occasional task (a one-time data migration, a quick exploratory
  check) — these can reasonably live in their own `scripts/` directory,
  clearly separated from the package's actual, ongoing, reusable code.
- **CLI entry points** — the specific, designated way a package is
  *run* as a program — typically `cli.py`'s `main()`, guarded by
  `if __name__ == "__main__":` exactly as
  [01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
  §8–§9 established, and (once packaging is covered later in this
  module) potentially also registered as an installed command a user
  can simply type by name.

**Why putting every utility into random scripts creates maintenance
problems**: a `scripts/` folder that accumulates dozens of ad hoc,
undocumented one-off files, each duplicating logic that also exists
(slightly differently) inside the real package, becomes exactly the
kind of maintenance burden §1 warned about — nobody can tell which
scripts are still relevant, which duplicate real package
functionality, or which are safe to delete. The discipline worth
keeping: if a "script" starts being run regularly, or starts
containing logic other code should reuse, it has outgrown `scripts/`
and belongs in the real package instead, exposed through a proper CLI
entry point.

## 17. Imports and Project Layout

Project layout directly determines how imports behave — this section
makes that connection explicit, building on
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
§13–§15 and §23.

**Package imports** work based on where a package actually sits
relative to `sys.path` — which, per the previous chapter's §13, is
populated differently depending on *how* Python was invoked and
*which* layout (flat, §4, or src, §5) the project uses.

**Absolute vs. relative imports** inside the package itself follow the
same rules as before — `from app.validation import validate_row`
(absolute) versus `from .validation import validate_row` (relative,
valid only with real package context, per the previous chapter's
§15).

**Working directory matters** because it affects what's on `sys.path`
in the ways already described — running a command from the project
root versus from inside `src/` versus from some entirely different
directory can change whether an import succeeds at all, which is
exactly why "it works from this directory but not another" (a genuine,
common real-world confusion) has a precise, diagnosable explanation
rather than being mysterious: `sys.path`'s contents (and therefore
what's importable) depend on how Python was invoked (a script's
directory, `-m`, `-c`, the current directory), on the environment
(`PYTHONPATH`, installed packages, IDE or test-runner configuration),
and only in part on the current working directory — not on some fixed,
universal property of the project's layout alone.

**Installed package vs. editable installation**, connecting directly
to §5: once a package is genuinely installed (a real install, or an
editable one), it is found via the environment's own `site-packages`
location (or the editable install's pointer back to `src/`) rather
than by searching relative to wherever the command happened to be run
from. This is the single biggest practical advantage of installing a
project properly (even just as an editable install during
development) over always running it as a bare script from a specific
directory: it makes imports **much less dependent on the working
directory**. It is a practical benefit, not an unconditional guarantee:
Python still resolves imports through `sys.path`, and the invocation can
add entries to it, so a local file or directory with the same name as
an installed package can still shadow it in some contexts (for example,
running `python -c "import app"` from a directory that contains its own
`app/` folder).

A realistic example of the exact confusion this section explains:

```bash
$ cd project/src
$ python -c "import app; print('works')"
works

$ cd project
$ python -c "import app; print('works')"
ModuleNotFoundError: No module named 'app'
```

With a src layout, **no** installation, and no other path
configuration in place, `app` is only importable from *inside* `src/`
(because that's the directory actually on `sys.path` in the first
invocation) — this is precisely why a src layout is meant to be paired
with an actual (typically editable) install, per §5, rather than run by
manually `cd`-ing into `src/` every time.

## 18. Common Import/Layout Problems

**1. `ModuleNotFoundError` from the wrong working directory**
*Root cause:* the package's containing directory isn't on `sys.path`
given how (and from where) the command was run. *Diagnosis:* `print
(sys.path)` and compare against where the package actually lives.
*Fix:* run from the correct directory, use `python -m package.module`
(per the previous chapter's §23), or install the package (editable
install, §5). *Better design:* don't rely on a specific working
directory at all — a properly installed package is generally
importable from anywhere (§17).

**2. Running a module from the wrong directory**
*Root cause:* `python src/app/cli.py` directly, inside a src-layout
project, gives `cli.py` no real package context (same failure mode as
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s §28
scenario 1, now specifically tied to the src layout). *Fix:* run via
`python -m app.cli` (with an editable install or `src/` correctly on
`sys.path`) instead of a bare file path.

**3. Incorrect relative import**
*Root cause:* a relative import (`from .validation import ...`) used
inside a file that was executed directly rather than run with package
context — identical to the previous chapter's §15/§28 scenario 3,
resurfacing here specifically because layout (which file is treated as
the "entry point") is what determines whether package context exists
at all.

**4. Duplicate module names**
*Root cause:* two different top-level packages/modules in the project
(or one project-local file and one installed third-party package)
share the same importable name — per
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s §28
scenario 7, whichever is found first on `sys.path` wins, silently.
*Diagnosis:* check `imported_thing.__file__` to see exactly which file
was actually loaded. *Fix:* rename the project-local module, or (for
the flat-vs-src risk from §4) ensure you're testing against the
intended (installed vs. local) version deliberately.

**5. Package not installed**
```
ModuleNotFoundError: No module named 'app'
```
even though `src/app/` clearly exists. *Root cause:* with a src layout
(§5) and no install (or other deliberate path configuration such as
`PYTHONPATH`) performed at all, nothing on `sys.path` makes `app`
importable from outside `src/` itself. *Fix:* perform an editable
install (this module's packaging chapter covers the exact command), or,
during early learning, run commands from inside `src/` (a real, if less
convenient, alternative) until installation is covered.

**6. Wrong Python environment**
Identical root cause and diagnosis to
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s §28
scenario 6 (`sys.executable` doesn't match where the package was
actually installed) — project layout doesn't change this failure mode,
but it's worth re-checking whenever an import mysteriously fails right
after what looked like a successful install.

**7. Accidentally importing local files instead of an installed
package**
*Root cause:* exactly §4's flat-layout risk — a local, uninstalled
package directory sitting on `sys.path` (because it's at the project
root, where commands are commonly run from) shadows the actually-
installed version. *Diagnosis:* check `package.__file__` — does it
point into your local source tree, or into `site-packages`? *Fix:*
adopt a src layout (§5) if this distinction genuinely matters for your
project (most importantly, for anything you intend to distribute).

## 19. Circular Dependency and Package Design

Directly extending
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
§19 — circular imports at the *module* level generalize naturally to
circular dependencies at the **package/subpackage** level, and poor
project structure is frequently the actual root cause.

```
mypackage/
├── orders/
│   └── __init__.py        # imports from customers/
└── customers/
    └── __init__.py         # imports from orders/
```

If `orders/__init__.py` imports something from `customers`, and
`customers/__init__.py` imports something from `orders`, the exact
same "partially initialized module" failure from the previous
chapter's §19 occurs — just at the subpackage level instead of the
single-file level, and often harder to spot precisely because the
actual conflicting imports are buried inside each subpackage's own
`__init__.py` rather than sitting visibly at the top of an obviously
related pair of files.

**Dependency direction** — the fix, restated at the project-structure
level: decide, deliberately, which subpackage is allowed to depend on
which, and never let that decision be circular. **Reducing unnecessary
coupling**: does `orders` genuinely need *all* of `customers`, or just
one small piece of shared data (a customer ID type, a lookup function)
that could live somewhere both can depend on without depending on each
other? **Moving shared functionality**: exactly the previous chapter's
preferred fix, now expressed as a project-structure decision —
introduce a `shared/` (or `common/`) subpackage that both `orders` and
`customers` can depend on, with neither depending on the other:

```
mypackage/
├── shared/
│   └── __init__.py     # customer ID types, shared lookups — neither orders nor customers depend on EACH OTHER
├── orders/
│   └── __init__.py       # imports from shared/
└── customers/
    └── __init__.py         # imports from shared/
```

**Clearer package boundaries**, as a preventive measure rather than a
fix: deciding subpackage responsibilities and their allowed dependency
directions *before* writing the code (§20's layer-based organization
is one common way to make this decision systematically) makes circular
dependencies far less likely to arise in the first place, compared to
letting package boundaries emerge accidentally as code is added over
time. This chapter deliberately does not introduce dependency-
injection frameworks or other advanced decoupling techniques — for
the scale of project this course currently addresses, clear,
deliberate dependency direction (as shown above) is sufficient.

## 20. Domain-Oriented Organization

Two common, genuinely different ways to organize a larger application's
internal structure — worth knowing both, and knowing that **neither is
universally correct**.

**Feature/domain-based** — grouped by *what part of the business/
problem* the code addresses:
```
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
    ├── models.py
    └── service.py
```

**Layer-based** — grouped by *what kind of responsibility* the code
has:
```
app/
├── cli/
│   ├── users_cli.py
│   └── orders_cli.py
├── services/
│   ├── users_service.py
│   └── orders_service.py
├── domain/
│   ├── users_domain.py
│   └── orders_domain.py
└── data/
    ├── users_data.py
    └── orders_data.py
```

**Feature/domain-based advantages:** everything related to "users" — a
new feature request, a bug report — lives in one place; adding a
genuinely new, self-contained feature (`reports/`) means adding one new
top-level folder, touching nothing else. **Disadvantages:** shared
logic used by *multiple* features (e.g. both `users` and `orders`
needing the same date-formatting helper) has no obvious single home,
and can end up duplicated or awkwardly placed.

**Layer-based advantages:** every file of the same *kind*
("validation logic," "CLI entry points") lives in one place, making it
easy to see, at a glance, everything at one architectural layer;
this is exactly the shape §10's CLI organization example used, at
smaller scale. **Disadvantages:** understanding one complete feature
("everything to do with orders") requires looking across *every*
layer folder at once, rather than one single directory.

**Why there is no universal folder structure**: the right choice
depends on how the codebase is actually likely to *change* — a
codebase where features are added and removed independently (a
plugin-like system) tends to favor feature-based organization; a
codebase where the *layers themselves* are the stable, long-lived
concept (a CLI tool with a small, fixed set of features but complex,
evolving business logic) tends to favor layer-based organization, as
§10's CLI example did. Neither this course nor the wider Python
community treats one as strictly superior — the deciding question is
always "which grouping will make *this specific project's* likely
future changes easiest to make correctly."

## 21. Small Project vs. Large Project

Project structure should **evolve with actual complexity**, not be
decided once, upfront, at whatever scale a future version of the
project might eventually reach.

**Small** (§3):
```
app.py
utils.py
```

**Medium** — a proper package, tests, and configuration separated out
(combining §4/§5's package layer with §10's file responsibilities,
introduced only once there's enough logic to justify splitting it):
```
src/
    app/
        cli.py
        processing.py
tests/
config/
```

**Larger** — layer-based (or feature-based) internal organization
within the package, once even `processing.py` alone has grown enough
to need its own internal structure:
```
src/
    app/
        domain/
        services/
        infrastructure/
        cli/
tests/
docs/
```

**Why premature over-engineering is also a real problem**, stated as
plainly as the opposite risk this chapter has spent most of its time
warning against: building the full "larger" structure above for a
50-line script adds directories, `__init__.py` files, and navigation
overhead that provide **zero actual benefit** at that size, while
making the project *harder*, not easier, to understand — a new reader
has to hunt through five nested folders to find a function that could
have simply been one visible line in `app.py`. The skill this section
is actually teaching is **recognizing which stage a project is
currently at**, and resisting the urge to either flatten a genuinely
complex project into one file *or* scaffold an elaborate structure for
one that hasn't earned it yet.

## 22. Package API Design

Every package presents some **public interface** to its users, and
(ideally, deliberately) keeps everything else as internal
implementation detail — directly building on §8's public/private
naming convention, now applied to what a package as a whole *exposes*.

```python
from mypackage import process_data
```
versus
```python
from mypackage.internal.processing_helpers import process_data
```

The first form depends only on `mypackage`'s **stable public API** —
whatever `mypackage/__init__.py` chooses to re-export (§7). The second
form reaches directly into an internal module, bypassing that
boundary entirely — anyone importing this way is now depending on
`mypackage`'s *actual internal file layout*, not just its intended
public interface.

**Why stable public APIs matter**: if `mypackage`'s author later
decides to reorganize `processing_helpers.py` into two smaller files
(a completely reasonable, internal refactor, from the author's
perspective), every piece of code using the first form
(`from mypackage import process_data`) keeps working without any
change at all — the `__init__.py` re-export simply points at wherever
`process_data` now actually lives. Every piece of code using the
second form **breaks immediately**, because it depended on an internal
detail the package's author never promised to keep stable.

**Practical guidance**: design a package's `__init__.py` (§7) to
re-export exactly the names external users are genuinely meant to use,
document that as the package's real interface, and treat everything
else inside the package as free to reorganize at will — this is
precisely the discipline that makes a package safe to refactor
internally without breaking everyone depending on it.

## 23. Namespace Packages

A brief, foundational note on a mechanism worth recognizing by name,
without needing to use it in most everyday code — building directly on
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
§16 mention.

A **regular package** is a directory containing an `__init__.py`
file, exactly as this entire chapter has assumed so far. A
**namespace package** (supported since Python 3.3) is a package
assembled by Python's namespace-package mechanism **without**
requiring an `__init__.py` in each contributing directory — Python's import system can, under
specific conditions, combine several separate directories (potentially
from entirely different installed distributions) that share the same
top-level name into one logical package.

**Why namespace packages exist**: primarily to let a single logical
package's functionality be split across multiple, independently
installable distributions (an advanced packaging scenario — for
example, a large ecosystem where different optional components are
installed separately, but all appear under one shared top-level
import name). This is genuinely uncommon in everyday application code.

**The basic practical difference to remember**: if you see a package
directory in the wild with **no** `__init__.py` at all and it still
imports successfully, it's very likely relying on this namespace-
package mechanism rather than being a mistake. For essentially every
project this course builds, an explicit `__init__.py` (even an empty
one) remains the clearer, more predictable, recommended default —
namespace packages are worth recognizing, not something to reach for
deliberately at this stage.

## 24. Project Layout and Packaging

A conceptual pipeline worth having in mind, connecting this chapter's
source-tree focus to what a later chapter in this module (dependency
management and packaging) covers in full:

```
source tree           (what you actually see and edit — src/mypackage/, per §5)
        ↓
package                 (the logical Python package Python's import system understands)
        ↓
build/package artifact    (a distributable file — e.g. a wheel — built FROM the source tree)
        ↓
installation                (that artifact is unpacked into an environment's site-packages,
                              or an editable install points back at the source tree directly)
```

**Why source layout and installed layout are related but not
identical**: the way your files are arranged in your own repository
(`src/mypackage/cli.py`) does not have to be byte-for-byte identical to
how they end up laid out once installed (though for a simple pure-
Python package, per this course's needs, they typically *do*
correspond directly) — the build step is what defines that mapping,
and packaging configuration (part of `pyproject.toml`, §12) is what
controls it. This chapter deliberately stops at this conceptual level;
actually building and publishing a package is this module's dedicated
packaging chapter's job, not this one's.

## 25. Project Layout and Code Quality

Gathering this chapter's recurring theme into one explicit statement:
**folder structure is an engineering tool, not decoration.** Concrete,
specific payoffs, each traceable to a section above:

- **Readability** — a clear structure (§9, §10) lets a reader predict
  where a given piece of logic lives, without searching.
- **Maintainability** — well-bounded responsibilities (§9) mean a
  change to one concern doesn't risk silently breaking an unrelated
  one living in the same file.
- **Testing** — separated concerns (§9, §11) are independently
  testable; a src layout (§5) protects against tests silently
  exercising the wrong version of the code.
- **Code review** — a reviewer can reason about a change to
  `validators.py` without needing the entire application's context
  loaded into their head at once.
- **Onboarding** — a predictable, conventional layout (flat or src,
  package/tests/metadata at recognizable locations) means a new
  contributor's existing Python experience transfers directly, rather
  than needing this specific project's idiosyncrasies explained from
  scratch.
- **Dependency management** — `pyproject.toml` at the root (§12), and
  clear internal dependency direction (§19), make it possible to
  reason about what depends on what.
- **Debugging** — knowing which layer (§9) is responsible for a given
  behavior narrows where to look first when something breaks.
- **Reuse** — a package with a stable public API (§22) can be reused
  by other projects (or other parts of a larger one) without those
  users needing to understand its internals at all.

None of these benefits come from the folder tree *looking* organized —
they come from the boundaries the structure enforces actually
corresponding to real, meaningful divisions in the code's
responsibilities.

## 26. Bad vs. Better Project Structures

**Bad:**
```
project/
├── everything.py
├── random_utils.py
├── test.py
├── final.py
└── final2.py
```
**Why this becomes difficult**: no file name indicates what it's
actually responsible for; `final.py` and `final2.py` (a depressingly
common real-world pattern) suggest an unclear, ad hoc revision history
baked directly into the file structure itself; a single `test.py`
gives no indication of what it tests, or whether it's still relevant;
there is no package at all, no metadata, and no separation between
reusable code and one-off logic.

**Better (step 1 — introduce a real package and clear names):**
```
project/
├── package/
│   ├── __init__.py
│   ├── cli.py
│   └── processing.py
├── tests/
│   └── test_processing.py
└── pyproject.toml
```
This alone (§4's flat layout) fixes the naming and grouping problems —
every file's responsibility is now clear from its name and location.

**Better (step 2 — src layout, once distribution/installation
matters):**
```
project/
├── src/
│   └── package/
│       ├── __init__.py
│       ├── cli.py
│       └── processing.py
├── tests/
│   └── test_processing.py
├── pyproject.toml
└── README.md
```
This adds §5's protection against accidental local-import shadowing —
appropriate once the project is meant to be genuinely installed, not
just run in place.

**Better (step 3 — responsibility layering, once `processing.py`
itself grows too large):**
```
project/
├── src/
│   └── package/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── validation.py
│       └── processing.py
├── tests/
├── pyproject.toml
└── README.md
```
This applies §9's/§10's layer separation — appropriate once a single
`processing.py` has started doing several genuinely distinct jobs
(processing, configuring, validating) that deserve their own files.

Each step is a **deliberate response to actual, demonstrated
complexity** — exactly §21's evolutionary principle, worked through
concretely from the worst possible starting point to a clean,
justified structure.

## 27. Production-Oriented Project Structure

One complete, realistic structure, combining everything this chapter
has covered, shown here purely as a Markdown example (no files are
created):

```
project/
├── src/
│   └── application/
│       ├── __init__.py
│       ├── cli.py                # argparse + main() -> int + __main__ guard (thin CLI layer)
│       ├── config.py               # AppConfig + build_config() — env/CLI precedence, validation
│       ├── logging_config.py        # configure_logging() — the one place logging is set up
│       ├── validation.py             # pure, reusable validators — no I/O, no CLI, no logging
│       ├── processing/                # a subpackage — processing has grown enough to need its own structure
│       │   ├── __init__.py
│       │   ├── csv_processing.py
│       │   └── json_processing.py
│       └── domain/                      # core business rules/types — depends on nothing above it
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

**Every directory/file and its responsibility:**

- **`src/application/`** — the installable package itself (§5); the
  root of everything that actually ships.
- **`cli.py`** — the CLI entry point (§9, §10) — the *only* file
  touching `argparse`, `sys.argv`, or the `__main__` guard directly.
- **`config.py`** — configuration precedence and validation (§14,
  reusing
  [09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
  pattern) — the *only* file reading `os.environ` directly.
- **`logging_config.py`** — the *only* file calling
  `logging.basicConfig()`/`dictConfig()`.
- **`validation.py`** — small, pure validator functions, independently
  unit-testable with no other dependency (§11).
- **`processing/`** — a subpackage (§6), because processing logic has
  grown enough (two distinct input formats) to warrant its own internal
  structure, rather than one increasingly large file.
- **`domain/`** — core types/business rules that both `processing/`
  submodules can depend on without depending on *each other* — the
  §19 "extract shared functionality" pattern, applied preemptively as
  good design rather than reactively as a circular-import fix.
- **`tests/`** — outside the package entirely (§11), mirroring
  `src/application/`'s own internal structure (note
  `tests/processing/`, matching `src/application/processing/`).
- **`data/`** — raw input and test fixtures (§15); no generated output
  directory shown here since this hypothetical CLI writes its results
  elsewhere (e.g. wherever the user directs via `--output`), rather
  than to a fixed in-repository location.
- **`docs/`** — documentation beyond what fits in `README.md`.
- **`pyproject.toml`, `README.md`, `.gitignore`** — project-root
  metadata and documentation (§12–§13).

This structure is not presented as "the" universally correct layout —
per §20–§21, the right structure always depends on the specific
project's actual complexity and likely evolution — but every piece of
it is justified by a specific, named principle from earlier in this
chapter, which is the actual skill this chapter is teaching: not
memorizing one tree, but being able to justify *why* each piece of
whatever tree you design belongs where it does.

## 28. Progressive Coding Examples

**1. One-file project**
```
app.py
```
Everything in one file — appropriate only for the smallest scripts
(§3).

**2. Multiple modules, no package**
```
app.py
utils.py
```
`from utils import helper` works because both files share the same
directory, which is on `sys.path` for the running script (§3, and
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
§23).

**3. A simple package**
```
package/
    __init__.py
    utils.py
```
`from package.utils import helper`, now with a real namespace (§6).

**4. A package with a subpackage**
```
package/
    __init__.py
    processing/
        __init__.py
        csv_processing.py
```
`from package.processing.csv_processing import process_csv` — the
dotted path directly mirrors the nested directories (§6).

**5. Flat project layout**
```
project/
    package/
    tests/
    pyproject.toml
```
The package sits directly at project root, alongside `tests/` (§4) —
imports work the same as example 3, but now with tests and metadata
properly separated out.

**6. Src layout**
```
project/
    src/
        package/
    tests/
    pyproject.toml
```
Now `package` is normally importable through an install (editable,
during development), or by deliberately placing `src/` on `sys.path`
(e.g. running from inside `src/`) — but not accidentally from the
project root (§5).

**7. CLI application structure**
```
src/app/
    cli.py
    config.py
    processing.py
```
`cli.py` imports `config` and `processing`; neither of the latter two
imports `cli` — one-directional dependency (§9, §10, §19).

**8. Tests organization**
```
tests/
    test_config.py
    test_processing.py
```
One test file per source module, mirroring `src/app/`'s own file names
(§11) — makes the mapping between tests and source obvious without any
extra documentation.

**9. Public/private package API**
```
mypackage/
    __init__.py          # from .processing import process_data
    processing.py          # the real implementation
    _internal_helpers.py    # not re-exported; internal only
```
`from mypackage import process_data` is the stable, intended interface
(§22); `mypackage._internal_helpers` exists but is never meant to be
imported directly by anything outside `mypackage` itself (§8).

**10. Production-oriented layout**
Exactly §27's full tree — the culmination of every example above,
combined and justified as one coherent structure.

## 29. Mini Project — Production-Style Python CLI Project Layout

**Scenario:** design (not implement in full — this is a layout
exercise) the project structure for a realistic small data-processing
CLI, `orders-report`, that reads a directory of order CSV files,
validates and cleans them, and writes a JSON summary — reusing exactly
the concepts Module 1.5 and this chapter's own sections have covered.

**Complete directory tree:**
```
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

**Responsibility of each component:**

- **`cli.py`** — defines `build_parser()` (an `--input-dir` argument, a
  `--output` argument), `main(argv) -> int`, and the `__main__` guard;
  imports `config`, `logging_config`, and `processing`; contains no
  business logic of its own.
- **`config.py`** — `AppConfig` (frozen dataclass: `input_dir`,
  `output_path`, `log_level`) and `build_config(argv)`, following
  [09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
  pattern — CLI arguments override an optional `LOG_LEVEL` environment
  variable.
- **`logging_config.py`** — `configure_logging(level)`, called once
  from `main()`, setting up a console handler per
  [08-logging-versus-print.md](../05-Text-Files-Structured-Data-and-CLI-Programs/08-logging-versus-print.md).
- **`validation.py`** — `validate_row(row)`, pure, reusable, no I/O.
- **`processing.py`** — `process_orders_directory(config)`, reading
  every CSV in `config.input_dir`, validating each row (error
  collection, per
  [09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)'s
  §17), and writing the JSON summary to `config.output_path`.

**Import relationships:**
```
cli.py  →  config.py
cli.py  →  logging_config.py
cli.py  →  processing.py
processing.py  →  validation.py
```
No arrows point back toward `cli.py` from any other file — the same
one-directional shape every prior section has reinforced, meaning
nothing here risks a circular import (§19).

**Execution flow:** `python -m orders_report.cli --input-dir data/raw
--output summary.json` → `cli.py`'s guard fires → `main(None)` →
`build_config(None)` parses CLI args and reads `LOG_LEVEL` →
`configure_logging(config.log_level)` → `process_orders_directory
(config)` reads each CSV, calling `validate_row` per row → a JSON
summary is written to `config.output_path` and printed to stdout →
`main()` returns an exit code reflecting whether every row was valid.

**Import flow at the module level**: `cli.py`'s three imports each
trigger
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s §3
process independently — `config.py`, `logging_config.py`, and
`processing.py` (which itself imports `validation.py`) are each loaded,
executed once, and cached (§11 of the previous chapter) the first time
`cli.py` is run; none of their own top-level code has any side effects
(§10 of the previous chapter) — only function *definitions* happen at
import time, with all real work deferred to `main()`'s explicit calls.

**Configuration flow:** CLI `--input-dir`/`--output` (always
authoritative for this tool, since there's no sensible environment-
variable equivalent for "which directory to process") combined with an
optional `LOG_LEVEL` environment variable (defaulting to `"INFO"`) —
resolved once, inside `build_config()`, into one immutable `AppConfig`.

**Data flow:** `data/raw/*.csv` (not committed — real input data, per
§15) → validated, in-memory rows → a summary dict → `summary.json`
(written wherever `--output` points, not necessarily inside the
repository at all).

**Logging flow:** `logging_config.configure_logging()` sets up a
console handler once, at startup; `processing.py` logs a `WARNING` per
invalid row and an `INFO` summary at the end, exactly per
[08-logging-versus-print.md](../05-Text-Files-Structured-Data-and-CLI-Programs/08-logging-versus-print.md)'s
established pattern — kept entirely on stderr, separate from the JSON
result on stdout.

**Why this design is maintainable:** every file answers exactly one
question (§9); `validation.py` and `processing.py` are testable with
plain function calls and `tmp_path`-based fixtures, no CLI invocation
needed (§11); adding a second output format (e.g. CSV instead of
JSON) touches only `processing.py`, never `cli.py` or `config.py`;
and the src layout (§5) means an eventual `pip install orders-report`
exercises exactly the same import paths this project's own tests
already use.

## 30. Exercises + Answer Key

**Beginner**

1. Given a small folder containing `app.py`, `helpers.py`, and a
   `data/` directory, identify which items are files, which are
   modules, and explain why `data/` is neither.
2. Take the flat, unstructured "bad" example from §26 and reorganize
   it into a simple flat layout (§4), giving each file a name that
   reflects its actual responsibility.
3. Explain, in your own words, what problem a `tests/` directory
   solves, and where it should sit relative to a package.
4. Given a package `mypackage/` containing `__init__.py`, `core.py`,
   and `_helpers.py`, explain what each file's naming signals about
   its intended use.

**Intermediate**

5. Convert this flat-layout project into a src-layout project, showing
   the resulting tree, and explain the one concrete risk the
   conversion removes:
   ```
   project/
       package/
           __init__.py
           logic.py
       tests/
       pyproject.toml
   ```
6. Design a CLI project structure (files and their responsibilities,
   not full code) for a tool that validates JSON files and prints a
   summary — reusing this chapter's CLI/config/logging/validation
   separation.
7. A teammate reports `ModuleNotFoundError: No module named 'app'`
   when running `python -c "import app"` from the project root of a
   src-layout project. Diagnose the likely cause and describe two
   possible fixes.
8. Given a package where `orders/__init__.py` imports from
   `customers/`, and `customers/__init__.py` imports from `orders/`,
   redesign the package structure to remove the circular dependency.
9. Explain, with a concrete before/after import statement, the
   difference between depending on a package's stable public API
   versus depending on one of its internal modules directly.

**Advanced**

10. You inherit a project where `main.py` is 800 lines long, mixing
    argument parsing, configuration, validation, business logic, and
    file I/O all in one file, with no tests. Describe, step by step,
    how you would restructure it — which files you'd create, in what
    order, and why that order minimizes risk.
11. Choose between feature-based and layer-based organization for a
    CLI tool that has exactly three fixed capabilities (validate,
    transform, report) that rarely change, versus a web-style
    application that frequently gains entirely new, independent
    features. Justify each choice.
12. Design a package's public API (its `__init__.py` re-exports) for a
    data-processing library with five internal modules, only two of
    which should be considered part of the stable public interface.
13. Identify at least three specific structural decisions in §27's
    production-oriented layout that would be excessive for a 100-line
    personal script, and explain why removing them would be the right
    call at that smaller scale (not merely "it's simpler").
14. Design the full project layout (tree, plus a one-line
    responsibility note per file) for a production-oriented CLI of
    your own choosing, distinct from every example already shown in
    this chapter.

**Answer key**

1. `app.py`, `helpers.py`, and everything inside `data/` (if
   text/data files) are all *files*; `app.py` and `helpers.py` are
   additionally *modules*, because they're `.py` files meant to be
   run/imported as Python code; `data/` is neither a module nor a
   package (it holds no Python code and isn't meant to be imported) —
   it's simply a directory holding non-code data (§1–§2).
2. A reasonable reorganization: `package/cli.py` (or similarly named),
   `package/utils.py`, `tests/test_utils.py`, `pyproject.toml` — the
   answer should demonstrate that every file's *name* now indicates
   its actual responsibility, unlike `final.py`/`final2.py` (§4, §26).
3. `tests/` verifies the application's source code behaves correctly;
   it conventionally sits as a sibling to the package (at the project
   root, or alongside `src/`) rather than nested inside the package
   itself, because tests are about the code, not part of what actually
   ships — a project-organization convention, not a Python language
   requirement (§11).
4. `__init__.py` marks the directory as a package (and may re-export a
   curated public API); `core.py` (no leading underscore) signals a
   public module, safe for external code to import directly;
   `_helpers.py` (leading underscore) signals an internal
   implementation detail not meant to be imported from outside the
   package (§7–§8).
5. 
   ```
   project/
       src/
           package/
               __init__.py
               logic.py
       tests/
       pyproject.toml
   ```
   The risk removed: with the flat layout, `package/` sits directly on
   `sys.path` when running commands from the project root, meaning
   tests could accidentally exercise the local source tree directly
   instead of a properly installed version — the src layout substantially
   reduces this by keeping `package` off the project root's import path,
   so it normally takes an actual (typically editable) install to make
   it importable (§4–§5).
6. A reasonable structure: `cli.py` (argparse + `main()`), `config.py`
   (any configurable options, e.g. `--strict`), `logging_config.py`
   (console logging setup), `validation.py` (JSON schema/shape
   checks), `processing.py` (reads files, calls validators, builds the
   summary) — mirroring §10's and §29's established pattern.
7. Likely cause: the src-layout package has never been installed, and
   nothing on `sys.path` from the project root makes `src/app`
   importable (§17, §18 scenario 5). Two fixes: perform an editable
   install (the recommended one), or run the command with `src/` on
   `sys.path` explicitly (e.g. from inside `src/`, or via `PYTHONPATH`)
   until installation is set up properly.
8. Introduce a `shared/` (or `common/`) subpackage holding whatever
   `orders` and `customers` both genuinely need (e.g. a shared
   customer-ID type or lookup function); have both `orders/__init__.py`
   and `customers/__init__.py` import from `shared/` instead of from
   each other, removing the cycle entirely (§19).
9. Before (fragile): `from mypackage.internal.helpers import
   compute_summary` — depends on `mypackage`'s actual internal file
   layout. After (stable): `from mypackage import compute_summary`,
   with `mypackage/__init__.py` re-exporting it — depends only on the
   package's documented, intentional public interface, which can
   remain stable even if `internal/helpers.py` is later renamed,
   split, or moved (§22).
10. A reasonable order: (1) extract pure validation logic into
    `validation.py` first, since it's the easiest to isolate and test
    with zero dependencies on the rest; (2) extract configuration
    reading into `config.py` next; (3) extract the actual business/
    processing logic into `processing.py`, now that it can depend on
    already-validated, already-configured inputs; (4) reduce `main.py`
    (renamed `cli.py`) down to argument parsing and wiring the pieces
    together last, once everything it needs to call already exists
    independently. Doing validation first (lowest risk, easiest to
    verify in isolation) before touching the riskier, more tangled
    business logic minimizes the chance of breaking something at each
    step (§9, §26).
11. For the fixed-capability CLI (validate/transform/report), layer-
    based organization fits well — the layers (CLI, validation,
    processing) are the stable, long-lived concept, and the three
    capabilities can share those same layers cleanly, similar to §10's
    example. For the frequently-growing web-style application,
    feature-based organization fits better — each new, largely
    independent feature can be added as its own self-contained folder
    without needing to touch every existing layer folder (§20).
12. A reasonable `__init__.py`:
    ```python
    from .core_api import process, validate
    __all__ = ["process", "validate"]
    ```
    with the remaining three internal modules (e.g. `_parsing.py`,
    `_formatting.py`, `_cache.py`) never re-exported, signaling clearly
    that only `process` and `validate` are the package's stable,
    supported interface (§7, §22).
13. Any three of: a `processing/` *subpackage* (a single
    `processing.py` file is plenty at that size); a `domain/`
    subpackage (no meaningful shared domain types yet at 100 lines); a
    src layout at all (§5's protection matters for distributed
    packages, not a personal script always run from its own checkout);
    separate `config.py`/`logging_config.py` files (a single small
    script can reasonably keep minimal configuration/logging setup
    inline, or in one small shared file) — the underlying reasoning in
    every case: the structural overhead isn't justified by complexity
    that doesn't yet exist (§21, §25).
14. Answers will vary; a strong answer explicitly names, for each file
    or directory, which section's principle justifies its existence
    (e.g. "`config.py` — separated per §9/§14 because this tool reads
    both CLI flags and an environment variable"), rather than simply
    presenting a tree with no stated reasoning — matching this
    chapter's core teaching goal of justifying structure, not just
    describing one.

## 31. Debugging Lab

**1. `ModuleNotFoundError` caused by layout**
```
project/
    src/
        app/
            cli.py
```
```bash
$ cd project
$ python -c "import app"
ModuleNotFoundError: No module named 'app'
```
*Diagnosis:* `print(sys.path)` — `src/` (where `app` actually lives)
isn't on it when running from the project root. *Root cause:* a src
layout (§5) with no installation performed, and no other `sys.path`
configuration. *Fix:* perform an editable install (recommended), or
run from inside `src/`. *Better design:* treat "install before running" as a normal
part of this project's documented setup instructions (its `README.md`,
§13), not an afterthought.

**2. Wrong working directory**
```bash
$ cd project/src/app
$ python cli.py
ModuleNotFoundError: No module named 'app'
```
*Diagnosis:* running `cli.py` directly from *inside* its own package
directory gives it no package context at all — `app` itself isn't
findable as a package from this location, since Python only sees
`cli.py`'s own directory, not its parent. *Root cause:* directly
executing a file that's meant to be run with real package context
(same underlying issue as the previous chapter's §23). *Fix:* run
`python -m app.cli` from `project/src/` (or from the project root,
with a proper install) instead.

**3. Package not installed**
```
$ pip show orders_report
WARNING: Package(s) not found: orders_report
```
*Diagnosis:* confirm whether an install (editable or otherwise) was
ever actually performed for this src-layout project. *Root cause:* a
src layout is not importable from the project root merely because the
source exists under `src/`; normal development commonly uses an install
(such as an editable install), although other deliberate path
configuration can also make `src/` importable (§5, §18 scenario 5).
*Fix:* perform the install.

**4. Incorrect relative import**
```python
# src/app/processing/csv_processing.py
from .validation import validate_row   # BUG: validation.py is in app/, not app/processing/
```
*Diagnosis:* check the actual directory `validation.py` lives in
relative to `csv_processing.py`. *Root cause:* the relative-import dot
count doesn't match the real directory nesting — `validation.py` is
one level *up* from `csv_processing.py`, requiring `..`, not `.`.
*Fix:* `from ..validation import validate_row`.

**5. Circular package dependency**
```
app/orders/__init__.py     — from app.customers import lookup_customer
app/customers/__init__.py   — from app.orders import lookup_order
```
*Diagnosis:* trace which `__init__.py` executes first and where it
fails trying to import from the other, not-yet-fully-initialized one.
*Root cause:* §19 — mutual dependency between two subpackages. *Fix:*
introduce a `shared/` subpackage holding whatever both genuinely need,
removing the direct dependency between `orders` and `customers`
entirely.

**6. Duplicate module names**
A project defines its own top-level `config.py`; a third-party
dependency the project also uses happens to internally import
something also named `config` from *its own* package (fully qualified,
so not actually at risk) — but a **careless absolute import** elsewhere
in the project (`import config`) picks up the *local* file when a
different, differently-named local module was actually intended.
*Diagnosis:* check `config.__file__` to see exactly which file was
loaded. *Root cause:* an overly generic, easily-collided module name
at the project's top level. *Fix:* rename to something more specific
(`app_config.py`), reducing collision risk with both the standard
library and third-party packages (§18 scenario 4).

**7. Local module shadowing another module**
A project names one of its own files `email.py`; every later
`import email` anywhere in the codebase — including indirectly, inside
a third-party dependency — now imports the *local* file instead of the
standard library's real `email` package, producing confusing,
seemingly-unrelated `AttributeError`s deep inside unrelated code.
*Diagnosis:* `email.__file__` — does it point to the project's own
file? *Root cause:* the project's own top-level directory is searched
before standard-library locations (identical mechanism to
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
§28 scenario 7, now surfacing specifically because of *layout* — a
flat, unpackaged file sitting at the very top level, most exposed to
this kind of collision). *Fix:* rename the file, and note that a real
package namespace (`app.email`, §6) — rather than a bare top-level
module — would have avoided the collision entirely, since it would
never be spelled just `email`.

**8. Source-layout import confusion during testing**
Tests pass when run with `pytest` from the project root, but fail with
`ModuleNotFoundError` when a teammate runs the exact same test file
directly with `python tests/test_processing.py`.
*Diagnosis:* compare how each invocation populates `sys.path` — a test
runner like pytest is typically configured (via `pyproject.toml` or an
install) to correctly resolve the package under test, while directly
executing a test file as a bare script is not. *Root cause:* relying
on an implicit, tool-specific mechanism for resolving imports, rather than a real (even if editable) installation that makes imports
far more consistent however a specific file happens to be invoked.
*Fix:* ensure the project has a real (editable) install configured, so
imports resolve consistently across every invocation style, not just
the one the test runner happens to handle specially.

## 32. Interview + Architecture Questions

1. What is a project layout, and why does it matter beyond aesthetics?
2. What's the difference between a module, a package, and a project?
3. Compare the flat layout and the src layout. What specific problem
   does the src layout prevent?
4. Why does an editable install matter for the src layout specifically?
5. What is `__init__.py`'s role, and why might it deliberately be left
   empty?
6. How does Python signal "this module/name is internal, not public,"
   and how strictly is that enforced?
7. Describe a package API design where `from mypackage import
   do_thing` remains stable even after significant internal
   refactoring. What makes that possible?
8. Where should a CLI application's `argparse` code live, and why
   should the rest of the application avoid depending on it?
9. Why should `tests/` be placed outside the package's own source
   tree?
10. What does `pyproject.toml` describe, and why does it belong at the
    project root rather than inside the package?
11. How does working directory affect whether an import succeeds?
12. What's the difference between an absolute import and a relative
    import, in terms of how project layout affects each?
13. How can poor package structure create a circular dependency, and
    what's the preferred fix?
14. Compare feature-based and layer-based organization. When would you
    choose each?
15. How should a project's structure change as it grows from a small
    script to a larger application? What's the risk of skipping ahead
    too early?
16. How does clean project structure make automated testing easier?
17. What kinds of files/directories typically live at the project
    root versus inside the package itself?
18. Where do secrets belong in a well-structured project, and where do
    they explicitly not belong?
19. What is a namespace package, and how does it differ from a
    traditional package?
20. Design, at a high level, the project layout you'd recommend for a
    small, production-oriented data-processing CLI, and justify each
    major decision.

**Answer key**

1. It's the organization of a project's files and folders; it matters
   because it directly determines how imports resolve, how easily
   code can be tested in isolation, and how easily a reader can find
   the code responsible for any given behavior (§1, §25).
2. A module is a named, importable unit of Python code (most commonly
   a single `.py` file); a package is a
   directory of related modules with its own namespace; a project is
   the entire collection — one or more packages, plus tests,
   configuration, and metadata (§2).
3. Flat layout places the package directly at the project root; src
   layout nests it inside a `src/` directory. The src layout prevents
   a local, uninstalled package from being accidentally importable
   directly from the project root, encouraging development and testing
   to go through a real (typically editable) installation instead
   (§4–§5).
4. Without an editable install (or other deliberate path setup),
   nothing on `sys.path` makes a src-layout package importable outside
   `src/`; an editable install registers a pointer back to the source
   files, letting `import mypackage` work from most directories while
   still reflecting live edits (§5).
5. `__init__.py` marks a directory as an importable package, and its
   top-level code runs once, the first time anything in the package is
   imported; it may be left empty because marking the directory as a
   package is sufficient on its own — re-exporting a curated API is an
   optional, deliberate choice (§7).
6. A single leading underscore (a module or name prefixed with `_`) is
   the conventional signal for "internal, not public"; it is not
   enforced by the language — nothing prevents another file from
   importing it anyway — it relies entirely on convention and
   communicated intent (§8).
7. By re-exporting `do_thing` through `mypackage/__init__.py`, so
   external code depends only on `from mypackage import do_thing`
   rather than on whichever specific internal module currently
   contains its implementation — the internal module can be freely
   renamed, split, or moved as long as the `__init__.py` re-export is
   updated to match (§22).
8. In a dedicated CLI module (e.g. `cli.py`); the rest of the
   application should avoid depending on it so that business logic
   remains testable and reusable without needing argparse, `sys.argv`,
   or any CLI concept involved at all (§9, §10, §25).
9. Because tests are about verifying the application's source code,
   not part of what the application actually ships or runs in
   production — keeping them separate means the shipped package
   doesn't need to include test files, and the package's own directory
   contains only real application code (§11).
10. `pyproject.toml` describes the project as a whole — its metadata,
    dependencies, build configuration, and often tool configuration —
    including things (like `tests/`) that aren't part of the
    installable package itself, which is why it belongs at the root
    that contains everything, not inside the package (§12).
11. `sys.path` (which determines what's importable) is populated
    depending on how Python was invoked, the environment (installed
    packages, `PYTHONPATH`, tool configuration) and, in some
    invocations, the current working directory; running the same
    command from two different directories can produce two different
    `sys.path` contents, and therefore two different import outcomes
    (§17).
12. An absolute import spells out a module's full path and works the
    same regardless of the importing file's own location; a relative
    import is expressed relative to the importing file's position
    inside its package, and requires that file to actually have
    package context (achieved via a real import, or `python -m`, not a
    bare direct file execution) (§15 of the previous chapter, §17).
13. Two subpackages (or modules) that each import from the other
    create a cycle, exactly like a two-module circular import, just at
    a coarser structural level; the preferred fix is extracting the
    functionality both genuinely need into a third, shared
    subpackage that neither depends on the other for (§19).
14. Feature-based groups code by business/problem area (`users/`,
    `orders/`) and suits applications that frequently gain independent
    new features; layer-based groups code by responsibility kind
    (`cli/`, `services/`, `domain/`) and suits applications with a
    small, stable set of features but complex, evolving logic within
    each layer — neither is universally correct (§20).
15. Structure should grow from a single file/pair of files, to a
    simple package with separated tests and metadata, to a layered or
    feature-organized package with subpackages — each step justified
    by actual, demonstrated complexity. Skipping ahead too early
    (building elaborate structure for a tiny script) adds navigation
    overhead with no corresponding benefit (§21).
16. By enforcing clear responsibility boundaries (§9) and keeping
    tests separate from source (§11), clean structure lets tests
    exercise focused pieces of logic (validators, business logic)
    directly, without needing to also involve unrelated concerns like
    CLI parsing or logging setup.
17. Project-root files typically include `pyproject.toml`,
    `README.md`, `LICENSE`, `.gitignore`, and `tests/`/`docs/`
    directories — things describing or supporting the project as a
    whole; the package's own directory (`src/mypackage/` or
    `mypackage/`) contains only the actual, shippable application
    source code (§12–§13, §27).
18. Secrets belong only in the actual runtime environment (real
    environment variables, or a secrets manager) and, locally, in a
    `.gitignore`d `.env` file — never in any file committed to version
    control, including `pyproject.toml` or a checked-in configuration
    file; a committed `.env.example` with placeholder values documents
    what's expected without exposing anything real (§14).
19. A traditional package is a directory containing `__init__.py`; a
    namespace package is a directory Python treats as part of an
    importable package without requiring `__init__.py` at all,
    primarily used to let one logical package span multiple,
    separately-installed distributions — an uncommon, advanced
    scenario compared to the traditional package this course uses by
    default (§23).
20. A strong answer names a src layout (for proper installability,
    §5), a thin `cli.py` (§9–§10), separate `config.py`/
    `logging_config.py` following Module 1.5's own patterns, pure
    `validation.py`, `processing.py` (split into a subpackage only if
    genuinely complex enough, §21), `tests/` mirroring the package
    structure (§11), and root-level `pyproject.toml`/`README.md`/
    `.gitignore` (§12–§13) — with each choice justified by the
    specific section of this chapter that motivates it, exactly per
    §27's worked example and §30 exercise 14's grading criterion.

## 33. Knowledge Check

**Conceptual**
1. Why is "folder structure is just organization" an incomplete way to
   think about project layout?
2. Why does a src layout require an installation step that a flat
   layout does not strictly require?

**Folder-tree interpretation**
3. Given this tree, identify: which directory is the package, which is
   likely not importable at all, and which file is project metadata.
```
widget_tool/
├── src/
│   └── widget_tool/
│       ├── __init__.py
│       └── core.py
├── tests/
├── pyproject.toml
└── README.md
```

**Import reasoning**
4. Given the tree above, would `import widget_tool` succeed if run
   from `widget_tool/` (the project root) with no installation
   performed? Why or why not?

**Code-reading**
5. What does this `__init__.py` tell you about the package's intended
   public API?
```python
# mypackage/__init__.py
from .core import run_pipeline
__all__ = ["run_pipeline"]
```

**Debugging**
6. A colleague's project has both `app/utils.py` and a `utils.py`
   accidentally left at the project root. `import utils` inside
   `app/cli.py` picks up the wrong one. Explain, precisely, why.

**Design**
7. You're asked to add a brand-new, mostly self-contained "exports"
   capability to a CLI tool currently organized by layer (`cli/`,
   `services/`, `domain/`, `data/`). Would you keep the layer-based
   structure, switch entirely to feature-based, or do something else?
   Justify your answer.
8. A 40-line script currently lives as a single `report.py`. Should it
   be restructured into a src-layout package with `domain/`,
   `services/`, and `cli/` subpackages right now? Why or why not?

---

**Answer key**

1. Because folder structure directly determines how Python resolves
   imports (`sys.path`, package namespaces) and how independently
   testable different pieces of logic are — it has real, functional
   consequences, not just a tidier appearance (§1, §17, §25).
2. Because a flat layout places the package directly at the project
   root, which is already on `sys.path` for commands run from there;
   a src layout deliberately keeps the package *out* of that
   automatically-searched location, so nothing except a real
   installation (or other deliberate path setup) makes it importable —
   this is precisely the mechanism that substantially reduces
   accidental local-import shadowing (§4–§5).
3. `widget_tool/widget_tool/` (inside `src/`) is the package; `src/`
   itself is likely **not** importable on its own (only what's inside
   it is meant to become importable, via installation); `pyproject.toml`
   is the project metadata (§5, §12).
4. No — with a src layout and no installation or other path
   configuration, `src/` isn't automatically added to `sys.path` by
   running from the project root, so `widget_tool` (which lives inside
   `src/`) isn't importable from there; it would need an install (the
   recommended approach) or `src/` placed on `sys.path` deliberately,
   e.g. by running from inside `src/` (§5, §17–§18).
5. It tells you `run_pipeline` is the package's intended, stable public
   entry point (`from mypackage import run_pipeline`), and that
   everything else inside `core.py` (and any other module in the
   package) should be treated as internal implementation detail unless
   also explicitly re-exported (§7, §22).
6. Because the project's own top-level directory (where the root-level
   `utils.py` sits) is searched before — or instead of — the intended
   `app/utils.py`, depending on exactly how `import utils` (a bare,
   ambiguous name) resolves relative to `sys.path`; the fix is either
   renaming the stray root-level file or using the fully-qualified
   `from app import utils` / `from app.utils import ...` to remove the
   ambiguity entirely (§18 scenario 4, §31 scenario 6–7).
7. A reasonable answer: keep the layer-based structure if the existing
   three layers still make sense for the new capability (add an
   `exports_cli.py`, an `exports_service.py`, etc., following the
   existing pattern) — switching the *entire* project to feature-based
   organization for one new feature is a much larger, likely
   unjustified change; the deciding question is whether *this specific*
   addition fits the existing organizing principle, not which paradigm
   is abstractly "better" (§20).
8. No — a 40-line script does not have anywhere near the complexity
   that would justify subpackages, layering, or even necessarily a src
   layout; per §21's evolutionary principle, the appropriate response
   is to keep it simple (perhaps a package with `cli.py` and one or two
   other files, at most) until real, demonstrated complexity actually
   arrives — introducing that structure now would be the over-
   engineering §21 explicitly warns against.

## 34. Production Checklist

**Project root**
- [ ] A clear project root exists, containing `pyproject.toml`,
      `README.md`, and (if applicable) `LICENSE`/`.gitignore` — not
      scattered or duplicated elsewhere.

**Package boundaries**
- [ ] The package has a logical namespace (`mypackage/`, or
      `src/mypackage/`), not a flat pile of unrelated top-level files.
- [ ] Subpackages exist only where genuine internal complexity
      justifies them — not created preemptively.

**Module responsibilities**
- [ ] Every module has one clear, nameable responsibility; file names
      reflect what they actually do.
- [ ] No `final.py`/`final2.py`/`misc.py`-style files with unclear or
      historically-accumulated purpose.

**Imports**
- [ ] Imports are predictable and do not depend on a particular working
      directory — typically because the package is properly (often editably)
      installed, not just run from a specific directory by convention.
- [ ] Import-time side effects are minimal to none (per
      [01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
      §10).
- [ ] No unnecessary wildcard imports.

**CLI separation**
- [ ] `argparse`, `sys.argv`, and the `__main__` guard live in exactly
      one, clearly-named module (`cli.py`).
- [ ] Business logic has no dependency on the CLI layer at all.

**Tests**
- [ ] `tests/` conventionally sits outside the package's own source tree, mirroring
      its internal structure where useful.
- [ ] Business logic (validation, processing) is testable without
      invoking the CLI or argparse.

**Configuration and secrets**
- [ ] Project configuration (`pyproject.toml`) is separated from
      runtime/environment configuration.
- [ ] No secrets exist in any version-controlled file; a
      `.env.example` (placeholders only) documents what's expected.

**Package API**
- [ ] The package's public interface (via `__init__.py` re-exports, or
      documented top-level modules) is stable and deliberately curated.
- [ ] Internal implementation modules are named/signaled as private
      (leading underscore) and not depended on from outside the
      package.

**Dependency direction**
- [ ] Dependencies between modules/subpackages flow in one direction;
      no circular dependencies exist.
- [ ] Shared functionality lives in a common module/subpackage both
      dependents can rely on, rather than depending on each other.

**Appropriate complexity**
- [ ] The current structure matches the project's actual complexity —
      neither one giant unstructured file, nor an elaborately layered
      structure for a project that hasn't earned it yet.

**Documentation and metadata**
- [ ] `README.md` and `pyproject.toml` exist at the project root and
      accurately describe the project and its dependencies.
