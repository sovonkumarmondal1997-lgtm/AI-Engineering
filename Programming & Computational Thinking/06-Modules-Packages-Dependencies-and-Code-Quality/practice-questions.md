# Module 06 Practice Questions

## Instructions

This set contains **28 practice questions** covering everything taught
across the seven files in this module — imports/modules/`__main__`,
project layout and package structure, `pyproject.toml`/lock files/`uv`,
dependency management and Semantic Versioning, Ruff formatting and
linting, type hints and type checking, and docstrings/READMEs/user
documentation. Questions are grouped into four difficulty levels (Basic,
Moderate, Hard, Advanced), each containing 7 questions, with difficulty
increasing across the set. Every **Problem** is followed immediately by
its **Solution** — work the problem yourself first, then compare your
reasoning against the solution, not just the final answer. Hard and
Advanced questions deliberately combine concepts from more than one
source file, exactly the way real engineering problems rarely respect
chapter boundaries.

---

# Part 1 — Basic

## Question 1

### Problem

The following file defines a small utility and a second file uses it,
but a subtle bug has been introduced:

```python
# serializers.py
from json import dumps

def to_json(data):
    return dumps(data)
```

```python
# main.py
from json import dumps
from my_logging_shim import dumps   # a project-local module that ALSO defines `dumps`

print(dumps({"a": 1}))
```

Running `main.py` produces output that doesn't look like valid JSON.
Explain exactly what is happening, and rewrite `main.py` so both
`dumps` functions remain usable without either one silently replacing
the other.

### Solution

**What's wrong:** `main.py` imports the name `dumps` twice — once from
the standard library's `json` module, and once from a project-local
module `my_logging_shim`. The second `from ... import dumps` **silently
shadows** the first: after both lines run, the name `dumps` in
`main.py`'s namespace refers only to `my_logging_shim.dumps`, not
`json.dumps`, with no error or warning at all.

**Why it happens:** `from module import name` binds `name` directly into
the current file's own namespace. Namespaces are just mappings from
names to objects, and a second assignment to the same name — including
via a second `import` — simply overwrites the first, exactly the way
`x = 1; x = 2` leaves `x` equal to `2`.

**The fix — use `import module` to keep both accessible through their
own module names:**

```python
import json
import my_logging_shim

print(json.dumps({"a": 1}))         # unambiguously the standard-library version
print(my_logging_shim.dumps({"a": 1}))  # unambiguously the local version
```

**Why this works:** `import json` binds the *module itself* to the name
`json`, not any individual name from inside it — every name inside
`json` (including `dumps`) is only ever reached through
`json.<name>`, so it can never collide with a same-named function from
another module bound the same way. This is exactly why `import module`
is the safer default whenever more than one thing in scope could
plausibly share a name, and why `from module import name` is best
reserved for a small number of frequently-used, unambiguous names.

**Production consideration:** this exact bug — a second import silently
replacing an earlier one — produces no exception and no warning, so it
is discovered only when the *behavior* is visibly wrong (as in this
question), which can be much later and much harder to trace back to its
actual cause than a normal `ImportError` would be.

---

## Question 2

### Problem

The following file is meant to work both as an importable module and as
a runnable script, but it does not behave correctly when imported:

```python
# report.py
def build_report(title: str) -> str:
    return f"=== {title} ==="

print(build_report("Demo Report"))
```

A teammate writes `import report` from another file just to reuse
`build_report`, and is confused when `"=== Demo Report ==="` prints
immediately, with no call to anything. Explain why this happens, and
fix `report.py` so it can be imported safely with zero side effects,
while still printing the demo report when run directly with
`python report.py`.

### Solution

**What's wrong:** `print(build_report("Demo Report"))` sits at the
module's top level, outside any function and outside any guard. Per
how Python imports work, **every top-level statement in a module
executes the moment that module is imported** — not just function and
class *definitions*. Importing `report.py` therefore runs this `print`
line unconditionally, exactly as if it had been executed directly.

**Why it happens:** there is no way for Python to distinguish "this file
is being imported for reuse" from "this file is being run as the
program" without an explicit check — and this file never performs that
check.

**The fix — use the `__name__` / `if __name__ == "__main__":` pattern:**

```python
# report.py
def build_report(title: str) -> str:
    return f"=== {title} ==="


def main() -> int:
    print(build_report("Demo Report"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Why this works:** when a file is executed directly (`python
report.py`), Python sets that file's own `__name__` to the special
string `"__main__"`; when the same file is *imported* elsewhere,
`__name__` is instead set to the module's own name (`"report"`). The
`if __name__ == "__main__":` guard therefore only fires when the file
was the one actually launched — `import report` now executes only the
function *definitions* (which have no side effects of their own),
leaving `build_report` available with no unwanted output.

**Production consideration:** this pattern is what makes a module safe
to import in a test file — a test can `import report` and call
`build_report(...)` directly, asserting on its return value, with zero
risk of triggering the "run as a script" behavior as an unintended side
effect of the import itself.

---

## Question 3

### Problem

Given this directory tree:

```
weather_cli/
├── src/
│   └── weather/
│       ├── __init__.py
│       ├── cli.py
│       └── forecasting.py
├── tests/
│   └── test_forecasting.py
├── pyproject.toml
└── README.md
```

1. Classify each of the following as a **file**, a **module**, a
   **package**, or the **project**: `weather_cli/`, `weather/`,
   `cli.py`, `README.md`.
2. Is this a **flat layout** or a **src layout**? Name the one specific
   risk this layout choice avoids, compared to the alternative.

### Solution

**1. Classification:**

- **`weather_cli/`** — the **project**: the whole repository, including
  source, tests, and metadata files, all together.
- **`weather/`** — a **package**: a directory containing an
  `__init__.py`, giving it its own namespace and making it importable
  as a unit.
- **`cli.py`** — a **module**: a single `.py` file meant to be imported
  and reused (here, as part of the `weather` package, importable as
  `weather.cli`).
- **`README.md`** — a plain **file**. It is not a module — it is never
  meant to be imported; it is project documentation, not Python source.

**2. Layout and risk:** this is a **src layout** — the importable
package (`weather/`) sits *inside* `src/`, rather than directly at the
project root alongside `tests/` and `pyproject.toml`.

**The specific risk it avoids:** with a **flat layout** (no `src/`
directory — `weather/` sitting directly at the project root), the
project root is commonly on `sys.path` when running scripts or tests
from there, which makes it possible to **accidentally import the local,
uninstalled package directly** rather than the actually-**installed**
version (e.g. via an editable install). If a test suite silently
imports the local source tree instead of the installed package, a
packaging mistake — a file that works locally but was never actually
included in the built package — can go completely undetected until a
real user installs it and it breaks. With a src layout, `src/` itself
is *not* added to `sys.path` automatically, so the *only* way to import
`weather` at all is through a proper installation, forcing development
and testing to exercise the same import path a real user's installation
would use.

**Production consideration:** a src layout is the safer default for
anything meant to be `pip`-installed by other people or by CI; a flat
layout remains perfectly reasonable for a small internal tool always run
directly from its own checked-out directory, where there's no
meaningfully different "installed" version to diverge from.

---

## Question 4

### Problem

A new project needs `pandas` as a **development-only** dependency (used
only for exploratory scripts, never imported by the shipped
application), constrained so that any `2.x` release is acceptable but a
future `3.0` requires deliberate review.

1. Write the exact `uv` command that adds this dependency correctly.
2. Show the resulting `pyproject.toml` fragment this command should
   produce, and explain the difference between where this dependency
   lands versus where a runtime dependency like `requests` would land.

### Solution

**1. The command:**

```bash
uv add --dev "pandas>=2.0,<3.0"
```

`--dev` marks this as a **development dependency** — needed only while
developing (here, for exploratory scripts), never required for the
shipped application to actually run in production. `"pandas>=2.0,<3.0"`
is a **bounded range**: the lower bound (`>=2.0`) says "any 2.x release
is acceptable," and the upper bound (`<3.0`) says "require a deliberate
review before accepting a `3.0` upgrade" — directly reflecting what a
MAJOR-version bump is supposed to signal under Semantic Versioning.

**2. The resulting configuration**, conceptually:

```toml
[project]
name = "demo"
version = "0.1.0"
dependencies = [
    "requests>=2.31,<3.0",
]

[dependency-groups]
dev = [
    "pandas>=2.0,<3.0",
]
```

*(The exact table name/shape `uv` writes for development dependencies
can vary by version — the important, stable fact this question tests is
that `--dev` places the dependency in a **separate group** from the
main runtime `dependencies` list, not that group's exact TOML key.)*

**Why the separation matters:** a runtime dependency (`requests` above)
is needed for the application to run and therefore belongs in every
environment, including production. A development dependency (`pandas`
here) is needed only for local development work — installing it
alongside the application's real runtime needs in a production
deployment would add unnecessary size and an unnecessary transitive
dependency footprint for a tool that provides zero value once the
application is actually running rather than being developed.

**Production consideration:** `uv add` updates `pyproject.toml`,
resolves the full dependency graph, updates `uv.lock`, and syncs the
local environment in one step — all four stay consistent with each
other automatically, which is exactly the guarantee that lets a
production deployment safely install only the runtime group while
skipping the development group entirely.

---

## Question 5

### Problem

A package's changelog shows the following three consecutive releases:

```
1.4.0 → 1.4.1   fixed a bug where nested lists were validated incorrectly
1.4.1 → 1.5.0   added a new validate_partial() function; nothing existing changed
1.5.0 → 2.0.0   renamed validate() to check(), and it now returns a result object instead of raising
```

For each bump, state whether it is a `MAJOR`, `MINOR`, or `PATCH`
change, and explain — in one sentence each — what a consumer should
expect from each one under the Semantic Versioning convention.

### Solution

- **`1.4.0 → 1.4.1` — PATCH.** A backward-compatible bug fix only; a
  consumer's existing code should be entirely unaffected in terms of
  what functions exist or how they behave, aside from the specific bug
  now being fixed.
- **`1.4.1 → 1.5.0` — MINOR.** New, backward-compatible functionality
  was added (`validate_partial()`); existing code that doesn't use the
  new function should keep working completely unchanged.
- **`1.5.0 → 2.0.0` — MAJOR.** A change that **may break** existing
  code: `validate()` was renamed to `check()` and its return behavior
  changed from raising to returning a result object — any consumer
  calling `validate()` directly must update their own code before
  upgrading across this boundary.

**Why this matters practically:** a project pinned to
`strictjson>=1.4,<2.0` receives the `1.4.1` and `1.5.0` updates
automatically and safely under the SemVer contract; the `2.0.0` release
requires the project's own code to be updated (`validate()` →
`check()`, and adjusting to the new return type) *before* the version
constraint's upper bound could even be raised to allow it — which is
precisely why the upper bound exists in the first place.

**Production consideration:** SemVer is a **convention communicating
maintainer intent**, not a guarantee enforced by any tool — even a
PATCH release that's supposed to be purely a bug fix can, in principle,
change behavior something else was inadvertently depending on. This is
why running the test suite after *any* update, including a "safe"
PATCH bump, remains good practice regardless of which segment changed.

---

## Question 6

### Problem

```python
import os
import sys

def calculate(x,y):
    unused_variable = 10
    return x+y
```

1. Classify each problem in this snippet as a **formatting** issue or a
   **linting** issue.
2. Give the exact Ruff commands to (a) fix the formatting issues and
   (b) automatically fix the safely-fixable linting issues, and explain
   what each command actually does.

### Solution

**1. Classification:**

| Problem | Category |
|---|---|
| `def calculate(x,y):` — missing space after comma | **Formatting** — purely cosmetic, doesn't change behavior |
| `return x+y` — no spaces around `+` | **Formatting** — same reason |
| `import os` — never used | **Linting** — an unused import (`F401`); about correctness/dead code, not layout |
| `import sys` — never used | **Linting** — a second unused import (`F401`) |
| `unused_variable = 10` — assigned, never read | **Linting** — an unused variable (`F841`); dead code, not a layout concern |

**2. The commands:**

```bash
uv run ruff format .
```
Runs the **formatter** — rewrites every Python file in place to match
Ruff's consistent, deterministic layout (spacing around operators and
commas, among other rules). This fixes both formatting issues
automatically.

```bash
uv run ruff check --fix .
```
Runs the **linter** and automatically applies fixes for violations Ruff
considers **safe** to fix mechanically — removing a genuinely unused
import (`F401`) is exactly this kind of safe, mechanical fix. The
result:

```python
def calculate(x, y):
    unused_variable = 10
    return x + y
```

Note `unused_variable = 10` is **not** removed automatically by
default in every configuration — an unused variable can indicate either
genuinely dead code (safe to delete) or a bug where the variable was
meant to be used somewhere (deleting it would hide the bug rather than
fix it), so it requires a human judgment call rather than a purely
mechanical one.

**Production consideration:** always run `git diff` after `ruff check
--fix` to review exactly what was changed — automating the mechanical
part of the fix does not eliminate the responsibility to verify it did
what was expected.

---

## Question 7

### Problem

Write a Google-style docstring for the following function, and then
explain, in one sentence, what `calculate_total.__doc__` will contain
once it's added.

```python
def calculate_total(price: float, quantity: int) -> float:
    return price * quantity
```

### Solution

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

**Why this is a complete, appropriate docstring:** it opens with a
concise, one-line summary; the `Args:` section describes what each
parameter *means* rather than repeating its type (the type hints
`price: float` and `quantity: int` already communicate the type — see
the "type hints vs. docstrings" distinction developed further in
Question 13); and `Returns:` states what the return value represents.

**`calculate_total.__doc__`**: once this docstring is added, it becomes
the value of `calculate_total.__doc__` — Python automatically stores
the string literal that is the *first statement* of a function's body
as that function's `__doc__` attribute, retrievable at runtime (e.g.
via `print(calculate_total.__doc__)` or `help(calculate_total)`) without
needing to open the source file at all.

**Common mistake:** placing the docstring after some other statement
(even a comment doesn't count as "other code," but an assignment or
`print()` would) — only a string literal as the *very first* statement
becomes `__doc__`; anything else, and `__doc__` stays `None`.

---

# Part 2 — Moderate

## Question 8

### Problem

A teammate's module makes their test suite unexpectedly slow and prone
to failing outside their machine:

```python
# app.py
print("Starting application...")
db_connection = connect_to_database()      # a real network connection
config = load_config_from_disk()             # real file I/O

def process_order(order_id: int) -> None:
    ...

def main() -> int:
    print("Processing orders...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

A test file does `from app import process_order` just to unit-test that
one function. Diagnose exactly what happens when the test file does
this, and rewrite `app.py` so it can be imported safely.

### Solution

**Diagnosis:** `db_connection = connect_to_database()` and `config =
load_config_from_disk()` sit at **module level**, outside any function.
Because Python executes a module's entire top-level code the moment it
is imported — not just its function/class definitions — `from app
import process_order` triggers a **real database connection** and
**real file I/O** as an unavoidable side effect of the import itself,
even though the test only wanted one small function. This makes the
test slow (a real network round-trip), environment-dependent (it fails
outright if no database is reachable from the test environment), and
liable to leave a dangling open connection nothing in the test ever
asked for.

**The fix — move all real work into functions, called only from behind
the `__main__` guard:**

```python
# app.py
def connect_to_database():
    ...   # defining the function has NO side effect — only calling it does

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

**Why this works:** `import app` (or `from app import process_order`)
now executes only the function **definitions** — genuinely
side-effect-free — with no database connection, no file I/O, and no
printed output, unless `main()` is explicitly called. A test can now
`from app import process_order` freely and repeatedly, in complete
isolation.

**Production consideration:** this is not a cosmetic style preference —
it is precisely what makes clean module design compatible with fast,
reliable automated testing rather than something the test suite has to
fight against on every run.

---

## Question 9

### Problem

A project uses a **src layout**:

```
project/
├── src/
│   └── app/
│       ├── __init__.py
│       └── cli.py
├── tests/
└── pyproject.toml
```

No installation (editable or otherwise) has been performed yet. A
developer runs:

```bash
$ cd project
$ python -c "import app; print('works')"
ModuleNotFoundError: No module named 'app'
```

1. Explain precisely why this fails, even though `src/app/` clearly
   exists.
2. Give two different, valid ways to make `import app` succeed, and
   explain the tradeoff between them.

### Solution

**1. Why it fails:** with a src layout, the package (`app/`) lives
*inside* `src/`, and — unlike the project root for a flat layout —
`src/` is **not** automatically added to `sys.path` just because a
command happens to be run from the project root. Python searches only
the locations actually present in `sys.path` (the current
directory/script location, standard-library locations, and installed
third-party locations); since nothing here has put `src/` on that list,
Python genuinely has nowhere to find `app` from the project root, even
though the files exist on disk.

**2. Two valid fixes:**

- **Run from inside `src/` directly:**
  ```bash
  $ cd project/src
  $ python -c "import app; print('works')"
  works
  ```
  This works because the current directory (`src/`) is now the one
  containing `app/`, and Python adds a script/interactive session's own
  working context to `sys.path`. **Tradeoff:** fragile and
  inconvenient — every command must be run from inside `src/`
  specifically, which doesn't reflect how the package will actually be
  imported once installed, and doesn't scale to running tests or tools
  from the project root the way a real project needs to.
- **Perform an (editable) installation of the package** so `app`
  becomes importable through the environment's own package-resolution
  mechanism, regardless of current working directory. **Tradeoff:**
  requires one extra setup step (the install), but this is precisely
  the point of a src layout — it *forces* development to exercise the
  same import path a real end-user's installation would use, from any
  directory, closing the "accidentally imports local, uninstalled
  files" gap a flat layout doesn't guard against.

**Production consideration:** the second option is the one a src-layout
project is actually designed around — relying on the first as a
permanent workaround defeats the entire structural reason for choosing
a src layout in the first place.

---

## Question 10

### Problem

A developer opens a colleague's pull request and sees this diff:

```diff
 [project]
 dependencies = [
-    "requests>=2.31,<2.32",
+    "requests>=2.31,<3.0",
 ]
```

The PR modifies only `pyproject.toml` — it does not touch `uv.lock` at
all. Explain precisely what state this leaves the project in, why it is
a problem, and the exact commands needed to fix it before merging.

### Solution

**What state this leaves the project in:** `pyproject.toml` now
**declares** a wider acceptable range for `requests` (`<3.0` instead of
`<2.32`), but `uv.lock` — the record of the **exact, resolved** version
currently installed — was never regenerated. Changing a declared
constraint by hand does **not**, by itself, automatically re-resolve or
update the lock file; `uv.lock` remains whatever it last was until a
command that explicitly re-resolves (`uv add`, `uv remove`, or
`uv lock`) is run.

**Why it's a problem:** `pyproject.toml` and `uv.lock` now describe two
different, inconsistent things — one person cloning the repo and running
`uv sync` would still get the *old*, narrowly-locked version (since
`uv.lock` hasn't changed), while the declared constraint suggests a
newer version is intended. This is one of the classic dependency-
management mistakes: committing `pyproject.toml` and `uv.lock` as if
they were independent, unrelated files, when they must always be kept
in sync with each other as one atomic change.

**The fix:**

```bash
uv lock
git diff uv.lock
uv sync
```

`uv lock` re-runs resolution against the *new* declared constraint and
updates `uv.lock` to match, without touching the installed environment.
`git diff uv.lock` is how a reviewer (or the author, before pushing)
inspects exactly what the resolver changed — including any transitive
dependency shifts — before trusting the result. `uv sync` then
installs/aligns the actual environment to match the freshly updated
lock file. Both `pyproject.toml` **and** the regenerated `uv.lock` must
then be committed together, as one atomic change.

**Production consideration:** a reviewer should treat "`pyproject.toml`
changed but `uv.lock` didn't" as an automatic request-changes signal on
any dependency-related PR — it is precisely the situation that lets
`uv sync` silently install something different from what the PR's
author actually tested against.

---

## Question 11

### Problem

A project's `pyproject.toml` declares:

```toml
dependencies = [
    "pydantic>=2.0",
]
```

The team wants to keep receiving routine `pydantic` updates
automatically, but wants to require a deliberate review before ever
accepting a `pydantic` `3.0` release. Explain what is wrong with the
current declaration, and rewrite it correctly, justifying your choice
of specifier.

### Solution

**What's wrong:** `pydantic>=2.0` is an **unbounded minimum-version
constraint** — it accepts version `2.0`, `2.9`, `3.0`, `4.5`, or any
future release whatsoever, with no upper limit at all. This offers no
protection against a future `MAJOR` release (which, under Semantic
Versioning, may contain breaking changes) silently entering the project
the next time dependencies are resolved — exactly the opposite of what
the team says it wants.

**The fix — a bounded range:**

```toml
dependencies = [
    "pydantic>=2.0,<3.0",
]
```

**Why this is correct:** the lower bound (`>=2.0`) preserves the
team's stated goal of receiving PATCH and MINOR updates within the `2.x`
line automatically — under SemVer's own contract, these are expected to
be backward-compatible. The upper bound (`<3.0`) is set exactly at the
next MAJOR-version boundary, which is precisely the boundary SemVer
signals as the one that *may* contain breaking changes — the resolver
will never silently select a `3.x` release to satisfy this constraint;
doing so would require someone to deliberately edit `pyproject.toml`
first, which is exactly the "deliberate review" gate the team asked
for.

**Why not an exact pin (`==2.5.0`) instead:** an exact pin would also
prevent an unreviewed `3.0` upgrade, but it would *also* prevent the
team from automatically receiving routine PATCH/MINOR bug-fix and
feature releases within `2.x` — which the team explicitly said they
still want. A bounded range is the middle ground that satisfies both
stated requirements at once.

**Production consideration:** this exact pattern — bounding a
dependency's upper end at its own next MAJOR-version boundary — is the
single most common, defensible default for application dependencies,
and should be the reviewer's expectation for any new dependency added
without a specific reason to deviate from it.

---

## Question 12

### Problem

A project's `pyproject.toml` contains this Ruff configuration:

```toml
[tool.ruff]
select = ["E", "F", "I"]
ignore = ["E501"]
```

Two problems: (1) this uses a **legacy** configuration shape that
modern Ruff versions expect elsewhere, and (2) the project's test files
frequently import fixtures purely for their side effects, which now
triggers unnecessary `F401` (unused import) violations across every
test file. Fix both problems.

### Solution

**Problem 1 — legacy configuration shape:** lint-related settings
(`select`, `ignore`, and related keys) belong under a **nested
`[tool.ruff.lint]` table** in modern Ruff configuration, not directly
under the top-level `[tool.ruff]` table. The version shown is the
older, legacy form still recognized by some Ruff versions but not the
current, expected structure.

**Fix:**
```toml
[tool.ruff]

[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]
```

**Problem 2 — test files need an exception, not a global rule change:**
turning off `F401` entirely (via the top-level `ignore` list) would
disable the "flag unused imports" check **project-wide**, including in
real application code where an unused import genuinely does indicate a
mistake or dead code. The correct scope is narrower: only test files
need this exception.

**Fix — use `per-file-ignores`, scoped to test files specifically:**
```toml
[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"tests/*.py" = ["F401"]
```

**Why the scoped fix is correct engineering practice:** disabling a
rule globally (via `ignore`/`extend-ignore`), disabling it for one
file/category (via `per-file-ignores`), and suppressing it for one
specific line (via inline `# noqa: F401`) are three genuinely different
scopes — the right choice is always the **narrowest scope that
genuinely fits the situation**. Here, the exception applies specifically
to *why test files import things* (fixtures imported for side effects),
not to a project-wide judgment that unused imports don't matter, so
`per-file-ignores` scoped to `tests/*.py` is the correct level, not a
blanket `ignore`.

**Production consideration:** every ignore — at any scope — should
encode a *deliberate, understood* policy decision, ideally with the
reasoning visible nearby (a comment in `pyproject.toml`), not simply
"this rule was inconvenient to fix."

---

## Question 13

### Problem

Correct every problem in this function signature and docstring:

```python
from typing import Optional

def create_user(name, age: Optional[int]) -> None:
    """Create a user.

    Args:
        name (str): A string containing the name.
        age (int): An integer representing the age.
    """
```

There are at least three distinct issues. Identify each and fix them.

### Solution

**Issue 1 — `name` has no type hint at all.** The function signature
only annotates `age`, leaving `name`'s expected type entirely
undocumented in the signature itself — a caller (and a type checker)
has no static information about what `name` should be.

**Fix:** `name: str`

**Issue 2 — `age`'s docstring entry claims a plain `int`, but the
signature says `Optional[int]`.** The docstring's `age (int):` doesn't
mention that `age` can also be `None` — it directly contradicts the
actual, more permissive signature, which is worse than simply being
redundant: it's actively misleading about a real possibility (`age`
being absent) a caller needs to handle.

**Issue 3 — the docstring redundantly repeats each parameter's type in
parentheses, when type hints already communicate it.** `name (str): A
string containing the name.` and `age (int): An integer representing
the age.` both restate information the type hints already provide
precisely, while adding no information about what each parameter
actually *means* or what constraints apply — and it's a second place
that can (as Issue 2 shows) drift out of sync with the real signature.

**Corrected version:**
```python
def create_user(name: str, age: int | None) -> None:
    """Create a user.

    Args:
        name: User's display name.
        age: User's age in years, or None if not provided.
    """
```

**Why this is better:** the type hints alone now communicate the exact
shape (`str`, and `int | None`); the docstring prose instead
communicates *meaning* — what `name` represents, and what a `None` age
signifies — exactly the complementary division of labor between type
hints (shape) and docstrings (behavior/meaning/constraints) that a
typed codebase should maintain, rather than duplicating the same
information in two places that can silently disagree.

---

## Question 14

### Problem

A README's entire "Installation" and "Usage" section reads:

```markdown
## Installation

Install the requirements and run the app.

## Usage

Use the balance command to check a balance.
```

Identify what's wrong with this documentation, and rewrite both
sections so a new developer can go from a fresh clone to a successful
run without asking the author a single question.

### Solution

**What's wrong:** both sections describe *that* something should be
done, without giving the *exact, runnable commands* to do it. "Install
the requirements" doesn't say which tool, what command, or what
prerequisites (a Python version?) are assumed. "Use the balance command"
doesn't show the actual command, its arguments, or what successful
output looks like. A reader is forced to guess or ask — exactly the
outcome a good README exists to make unnecessary.

**Corrected version:**
```markdown
## Prerequisites

- Python 3.12+
- uv (https://docs.astral.sh/uv/)

## Installation

\`\`\`bash
git clone https://github.com/example/billing-service.git
cd billing-service
uv sync
\`\`\`

## Usage

\`\`\`bash
uv run python -m billing_service balance --customer-id 12345
# Customer 12345: $128.50
\`\`\`
```

**Why this is better:** every step is now a **copy-pasteable command**,
in the order it must run, with prerequisites stated *before* they're
needed rather than discovered via a confusing error. The usage example
shows both the exact command **and** its expected output, so the reader
can confirm success without guessing whether it "worked."

**Production consideration:** a README should let a new developer move
from clone → install → configure → run → test without needing to ask
the author basic questions — vague, command-free instructions like the
original are one of the most common real-world documentation failures,
and are the single easiest category of documentation problem to fix
mechanically once recognized.

---

# Part 3 — Hard

## Question 15

### Problem

```
mypackage/
├── orders/
│   └── __init__.py        # from mypackage.customers import CustomerId
└── customers/
    └── __init__.py         # from mypackage.orders import OrderId
```

Running any code that imports either subpackage raises:
```
ImportError: cannot import name 'CustomerId' from partially initialized module 'mypackage.customers'
```

1. Explain precisely why this happens, connecting it to how Python
   executes a module's top-level code and caches it in `sys.modules`.
2. Propose the preferred structural fix (not a quick workaround), and
   show the resulting package layout.

### Solution

**1. Why it happens:** `orders/__init__.py` and `customers/__init__.py`
depend on each other directly — a **circular import** at the
subpackage level. Say something first imports `mypackage.orders`:
Python begins executing `orders/__init__.py`'s top-level code, which
hits `from mypackage.customers import CustomerId`. Python begins
executing `customers/__init__.py` in turn — but that file immediately
hits `from mypackage.orders import OrderId`. Since `mypackage.orders`
is **already in the process of being imported** (its module object
exists in `sys.modules`, but it's only partway through executing — its
own body hasn't reached the point of defining `OrderId` yet), Python
does not re-run it from scratch (that would infinite-loop); it returns
the **partially initialized** module object it already has — one that
doesn't yet have `OrderId` defined on it — producing exactly this
"partially initialized module" error.

**2. The preferred fix — extract shared functionality into a third
module neither depends on the other for**, rather than reordering
imports or hiding the dependency inside a function (a narrow,
last-resort escape hatch, not a first-choice design fix):

```
mypackage/
├── shared/
│   └── __init__.py     # CustomerId, OrderId — neither orders nor customers depends on the OTHER
├── orders/
│   └── __init__.py       # imports from shared/
└── customers/
    └── __init__.py         # imports from shared/
```

```python
# shared/__init__.py
CustomerId = str   # or wherever these shared types genuinely belong
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

**Why this is the preferred fix over alternatives:** merging the two
subpackages is too disruptive when they represent genuinely distinct
domains; moving an import inside a function only hides the dependency
from anyone scanning the file's top-level imports, without addressing
the underlying design issue. Extracting the *specific* shared piece
each side actually needs into a lower-level module that neither
`orders` nor `customers` depends on the *other* for removes the cycle
structurally — a direct application of "reconsider the dependency
direction" rather than routing around the symptom.

**Production consideration:** a circular dependency is best treated as a
signal that a package boundary was drawn in the wrong place, not merely
a bug to patch around — deciding subpackage responsibilities and their
allowed dependency directions *before* writing the code prevents this
class of problem from arising in the first place.

---

## Question 16

### Problem

A project's dependency graph is:

```
my-project requires:      A >= 2
A requires:                 B < 3
my-project ALSO requires:    C
C requires:                    B >= 3
```

1. Explain whether `uv add`/`uv sync` can succeed here, and why.
2. `A`'s own maintainers most likely chose `B < 3` deliberately — explain
   what that constraint is very likely protecting against, in terms of
   Semantic Versioning.
3. Give two structurally different ways this conflict could genuinely
   be resolved (not "force an install").

### Solution

**1. Whether resolution can succeed:** **No.** The resolver needs one
version of `B` that is simultaneously `< 3` (required by `A`) **and**
`>= 3` (required by `C`) — no such version can exist, since these two
ranges share no overlap at all (`[..., 3.0)` versus `[3.0, ...)`). This
is a genuine **dependency conflict**, not a transient failure — `uv
add`/`uv sync` will report a resolution failure naming the conflicting
constraints, and no amount of retrying will produce a different result
given these exact requirements.

**2. What `A`'s `B < 3` constraint is protecting against:** almost
certainly, `A`'s maintainers know (or suspect) that `B`'s upcoming
`3.0.0` release is a MAJOR, potentially breaking change under Semantic
Versioning, and `A`'s own code has not been verified compatible with
it. The version boundary in `A`'s constraint is a direct, practical
reflection of what a MAJOR version bump is supposed to signal — "review
before crossing this boundary" — applied by `A`'s own maintainers to
their own dependency on `B`.

**3. Two genuinely different resolutions:**

- **Upgrade `A` to a newer release** whose own transitive requirement on
  `B` has since relaxed (e.g., a newer `A` that has itself been updated
  to support `B >= 3`) — the cleanest fix when available, but requires
  reviewing *that* upgrade for its own compatibility implications before
  accepting it, exactly like any other dependency update.
- **Replace one of the conflicting dependencies** (`A` or `C`) with an
  alternative package serving the same purpose, if no compatible version
  of either exists — a more disruptive change, appropriate specifically
  when the conflict is fundamentally unresolvable through an upgrade
  alone.

**What must never be done:** manually forcing a version past the
resolver's determination that no valid set exists — the resulting
environment would *look* installed while actually violating a real,
declared constraint somewhere, producing subtle, hard-to-diagnose
runtime failures instead of the clear, upfront resolution error the
resolver correctly produced.

---

## Question 17

### Problem

A team reports: "It passed code review and CI, but broke immediately
when deployed." Investigation reveals CI's dependency-install step ran
`pip install pandas requests` directly from a `requirements.txt` file
with **no version pins**, while production was built from a Docker
image that had cached older dependency versions from weeks earlier.

1. Diagnose the root cause using this module's vocabulary.
2. Redesign the workflow using `pyproject.toml` and `uv.lock` so this
   category of failure becomes structurally impossible.

### Solution

**1. Root cause — dependency drift, caused by the absence of a lock
file used consistently everywhere.** With unpinned requirements, every
environment that independently resolves — CI, run fresh today, versus
the production image, built weeks earlier from a cache — can legitimately
arrive at a *different* resolved set of exact versions, simply because
newer package releases became available in the meantime. Neither
environment did anything "wrong" in isolation; they simply never agreed
with each other in the first place, because nothing recorded *one*
specific, shared, resolved answer for both to install from.

**2. The redesign:**

```
copy pyproject.toml + uv.lock into the CI environment / container image
        ↓
uv sync   (installs the EXACT locked versions — never re-resolves independently)
        ↓
run tests / build
```

- Declare dependencies in `pyproject.toml` with sensible bounded ranges
  (e.g. `pandas>=2.0,<3.0`), per this module's version-constraint
  guidance.
- Run `uv lock` (or let `uv add` do it) to produce a committed
  `uv.lock`, recording the exact resolved version of every direct and
  transitive dependency.
- **Commit `uv.lock` to version control alongside `pyproject.toml`.**
- Replace the CI step with `uv sync`, which installs from the
  **already-resolved, committed** `uv.lock` rather than re-running
  resolution fresh.
- Build the production image the same way: copy `pyproject.toml` +
  `uv.lock` into the image, then `uv sync` — never a bare, unpinned
  `pip install` of package names.

**Why this eliminates the category of failure, not just this specific
instance:** because dependency installation is now driven by the
already-resolved `uv.lock` at every stage — developer machines, CI, and
the container build — every one of them installs the **exact same**
set of dependency versions, regardless of *when* each one happens to
run. A container built today and one built from an unchanged `uv.lock`
months from now install identical versions, closing the exact gap that
let CI and production silently diverge in this scenario.

**Production consideration:** this is precisely why CI must
independently install from the committed lock file rather than trusting
that "it resolved fine on a developer's machine" — the whole point of
committing `uv.lock` is that every stage of the pipeline reads from one
shared, reproducible source of truth instead of each re-deriving its
own.

---

## Question 18

### Problem

```python
def get_active_users(users: list[dict]) -> list[str]:
    active = []
    for u in users:
        if u["status"] == "active":
            active.append(u["nam"])   # typo: should be "name"
    return active
```

Running `uv run ruff check .` on this file reports **no violations at
all**, yet the function has a real bug. Explain precisely why Ruff
doesn't catch this, what category of tool *would* catch it (and how),
and fix the code.

### Solution

**Why Ruff doesn't catch this:** `u["nam"]` is a dictionary key lookup
using a plain string literal — from Ruff's (and any linter's)
perspective, this is syntactically valid, ordinary code with no
detectable pattern-level problem: `u` is typed only as `dict`, with no
declared shape for its keys, so there is nothing statically suspicious
about indexing it with *any* string, correct or not. This is not a
category of bug a **linter** (which analyzes syntax structure and known
suspicious patterns, such as unused imports or undefined names) is
designed to catch at all — it requires either running the code against
real data, or a much more precise *type* for `u` that could flag `"nam"`
as an invalid key.

**What category of tool would catch it, and how:** a more precisely
typed function signature, checked by a **static type checker** (a
fundamentally different tool from Ruff — see the earlier chapter's
`TypedDict` coverage), could catch this *before* runtime:

```python
from typing import TypedDict

class User(TypedDict):
    name: str
    status: str


def get_active_users(users: list[User]) -> list[str]:
    active = []
    for u in users:
        if u["status"] == "active":
            active.append(u["nam"])   # a type checker now flags: "nam" is not a valid key of User
    return active
```

With `users: list[User]` (a `TypedDict` declaring exactly which keys
exist), a type checker like mypy or Pyright can verify `u["nam"]`
against `User`'s actual declared keys and report an error *without ever
running the function* — something Ruff's linting alone cannot do,
because Ruff does not perform the deep, whole-codebase type inference a
dedicated type checker specializes in. Absent a type checker actually
being run, this bug would only surface at runtime, as a `KeyError`,
whenever an active user is actually processed.

**Fix:**
```python
active.append(u["name"])
```

**Production consideration:** formatting, linting, type checking, and
testing are four **complementary, non-overlapping** layers — a project
that runs only Ruff and assumes it also covers type-correctness has a
real, unaddressed gap; the two tools genuinely catch different
categories of problem and neither substitutes for the other.

---

## Question 19

### Problem

A package needs a stable, typed public interface for storage backends
that can be swapped (a local filesystem backend today, cloud storage
later) without callers depending on either concrete implementation.

1. Design a `Protocol` describing the minimal behavior every backend
   must provide.
2. Show how `mypackage/__init__.py` should expose this so that callers
   depend only on the package's stable public API, not on any internal
   module.

### Solution

**1. The `Protocol`:**

```python
# mypackage/storage/_protocol.py   -- underscore-prefixed: internal module
from typing import Protocol


class StorageBackend(Protocol):
    def read(self, key: str) -> bytes: ...
    def write(self, key: str, data: bytes) -> None: ...
```

`StorageBackend` describes **structural** compatibility: any class with
matching `read`/`write` methods satisfies this protocol automatically,
with **no inheritance required at all** — a local filesystem
implementation and a future cloud-storage implementation can each
satisfy it independently, without either needing to know about the
other or about `StorageBackend` itself beyond matching its method
shapes.

```python
# mypackage/storage/_local.py
class LocalStorageBackend:
    def read(self, key: str) -> bytes:
        ...
    def write(self, key: str, data: bytes) -> None:
        ...
```

A function using this boundary:
```python
def sync_data(backend: StorageBackend, key: str, data: bytes) -> None:
    backend.write(key, data)
```
`sync_data` depends only on the **behavior** `StorageBackend` describes
— it works identically whether handed a `LocalStorageBackend`, a future
cloud backend, or any other object with matching methods, with zero
coupling to any specific class hierarchy.

**2. `mypackage/__init__.py`, exposing a stable public API:**

```python
# mypackage/__init__.py
from mypackage.storage._protocol import StorageBackend
from mypackage.storage._local import LocalStorageBackend

__all__ = ["StorageBackend", "LocalStorageBackend"]
```

Callers write:
```python
from mypackage import StorageBackend, LocalStorageBackend
```

**Why this is the correct package-API design:** the underscore-prefixed
module names (`_protocol.py`, `_local.py`) signal — by convention, not
enforcement — that they are internal implementation detail, free to be
reorganized later without it counting as a breaking change, *because*
nothing outside the package was ever supposed to import them directly.
`__init__.py`'s re-exports, combined with `__all__`, define the
package's actual, stable, documented interface: if the internal files
are later split or renamed, every caller using `from mypackage import
StorageBackend` keeps working unchanged, while any caller that had
instead reached directly into `mypackage.storage._local` would break —
exactly the risk a stable public API, combined with a structurally
typed `Protocol` boundary, is designed to prevent.

**Production consideration:** this combination — a `Protocol` for
behavioral substitutability, plus a curated `__init__.py` for interface
stability — is precisely the pattern used for swapping model providers
or storage backends in larger typed Python systems without callers ever
needing to know which concrete implementation is actually in use.

---

## Question 20

### Problem

Write a complete, production-quality docstring for the function below,
covering its input expectations, output behavior, errors, side effects,
and compatibility — then write the matching two or three lines a
README's "Usage" section should contain for it.

```python
def get_order_total(order_id: int) -> float:
    order = database.fetch_order(order_id)
    if order is None:
        raise OrderNotFoundError(order_id)
    return sum(item.price * item.quantity for item in order.items)
```

### Solution

**The docstring — an API contract, not a restatement of the code:**

```python
def get_order_total(order_id: int) -> float:
    """Return the total price of an order's line items.

    Input expectations:
        order_id must refer to an existing order. A deleted order is
        NOT distinguished from a nonexistent one — both raise
        OrderNotFoundError.

    Output behavior:
        Returns the sum of price * quantity across every line item on
        the order, in the order's own currency. Does not include tax
        or shipping.

    Raises:
        OrderNotFoundError: If order_id does not resolve to an
            existing order.

    Side effects:
        None — this function performs a read-only database lookup and
        computes a value; it does not modify any stored data.

    Compatibility:
        The returned value's meaning (line-item subtotal, excluding
        tax/shipping) is a stable contract; a future change to include
        tax would be a breaking change requiring a major version bump.
    """
    order = database.fetch_order(order_id)
    if order is None:
        raise OrderNotFoundError(order_id)
    return sum(item.price * item.quantity for item in order.items)
```

**Why each part earns its place:** the "input expectations" note
documents a real, non-obvious behavioral choice (deleted vs. nonexistent
orders are indistinguishable) that a reader cannot infer from the code
alone. "Output behavior" clarifies what the returned `float` actually
represents — critically, that it **excludes** tax and shipping, which a
caller could easily assume otherwise. "Side effects" explicitly states
there are none, which matters because a reader cannot always assume a
function named `get_...` is read-only without it being said. The
"Compatibility" note tells a future maintainer what would count as a
breaking change to this function's contract.

**The matching README "Usage" section:**

```markdown
## Usage

\`\`\`python
from myapp.orders import get_order_total

total = get_order_total(order_id=501)
print(f"Order total: ${total:.2f}")
\`\`\`
```

**Why the README stays short while the docstring is thorough:** the
README's job is to show a realistic, runnable example so a new user can
get oriented quickly; the full contract — including the exception
behavior, the currency/tax exclusion, and the compatibility guarantee —
belongs in the docstring (and, if generated, an API reference), which a
caller consults specifically when they need those details, rather than
in every README that merely wants to demonstrate basic usage.

---

## Question 21

### Problem

Design and document a small CLI tool `wordcount` that counts words in a
file, with an optional `--encoding` flag. Show:

1. `cli.py`'s `main(argv) -> int` implementation, using the
   `__main__` guard.
2. A `WORDCOUNT_ENCODING` environment-variable row for the README's
   configuration table.
3. The README's CLI usage example, including expected output and one
   documented exit code.

### Solution

**1. `cli.py`:**

```python
# cli.py
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
    with open(path, encoding=encoding) as f:
        return len(f.read().split())


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        total = count_words(args.file, args.encoding)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    print(f"{total} words")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

`main(argv) -> int` is defined as an ordinary, testable function
accepting an optional `argv` list — a test can call `main([...])`
directly and assert on its return value, with no subprocess involved.
`os.environ.get("WORDCOUNT_ENCODING", "utf-8")` is the **only** place
that reads the environment variable directly, giving `--encoding` a
sensible default sourced from configuration without scattering
`os.environ` access throughout the file. `raise SystemExit(main())`
translates the function's ordinary return value into the process's
actual OS-level exit status, and only fires when this file is executed
directly, never when it's imported for testing.

**2. README configuration table row:**

```markdown
| Variable | Required | Default | Description |
|---|---|---|---|
| `WORDCOUNT_ENCODING` | No | `utf-8` | Text encoding used to read the input file. |
```

**3. README CLI usage:**

```markdown
## Usage

\`\`\`bash
uv run python -m wordcount myfile.txt
# 452 words
\`\`\`

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | File not found |
```

**Why this design connects the module's concepts correctly:** `cli.py`
is the thin CLI layer — the only file touching `argparse`, `sys.argv`
(indirectly, via `parse_args`), and the `__main__` guard, per this
module's responsibility-layering guidance; `count_words` is a small,
separately testable function with no CLI or environment knowledge at
all; the configuration table states the variable's requiredness,
default, and purpose exactly as this module's configuration-
documentation guidance specifies; and the exit-code table turns CLI
`--help`-adjacent behavior into documented, scannable reference
material rather than something a user has to discover by trial and
error.

---

# Part 4 — Advanced

## Question 22

### Problem

**Scenario A — Production Python Service.** A team is building a new
Python data-processing service from scratch. They want reproducible
dependencies, enforced code quality, type safety, tests, and usable
documentation from day one. Using only concepts from this module,
design (a) the project's directory structure, (b) the exact sequence of
setup/quality commands a contributor runs before every commit, and (c)
what belongs in the README versus what belongs in developer-only
documentation.

### Solution

**(a) Directory structure** — a src layout (protecting against
accidentally testing against an uninstalled local package), with
responsibility-layered modules:

```
project/
├── src/
│   └── service/
│       ├── __init__.py
│       ├── cli.py               # argparse + main() -> int + __main__ guard
│       ├── config.py              # env/CLI precedence — the only file reading os.environ
│       ├── validation.py           # pure, reusable validators — no I/O
│       └── processing.py            # core business logic
├── tests/
│   ├── test_validation.py
│   └── test_processing.py
├── pyproject.toml
├── README.md
└── CONTRIBUTING.md
```

**(b) The pre-commit command sequence, and what each stage catches
that the others structurally cannot:**

```bash
uv sync                    # ensure the environment matches pyproject.toml/uv.lock exactly
uv run ruff format .        # consistent layout — no logic checked
uv run ruff check --fix .    # unused imports/variables, suspicious patterns, import order
uv run mypy .                  # type consistency across the codebase — Ruff does not do this
uv run pytest                    # actual runtime behavior, verified against expectations
git diff                          # review what --fix and formatting actually changed
```

Each stage is deliberately kept, not collapsed — formatting says
nothing about correctness; linting cannot verify type consistency
project-wide; a type checker cannot verify actual runtime behavior;
tests only verify what's actually been written and exercised. Skipping
any one reopens exactly the category of bug the skipped stage exists to
catch.

**(c) README vs. developer-only documentation:**

- **README (user-facing)**: overview, prerequisites (`Python 3.12+`,
  `uv`), installation (`uv sync`), configuration table, basic usage
  example with expected output, and a link to `CONTRIBUTING.md` — the
  minimum needed for someone to get the service running.
- **`CONTRIBUTING.md` (developer-facing)**: the exact commands from
  part (b), coding standards, branch/PR workflow, and commit
  expectations — information only someone *changing* the code needs,
  which would only add noise to a README aimed at someone merely
  *using* it.

**Production consideration:** committing `uv.lock` alongside
`pyproject.toml`, and running every quality stage through `uv run`
rather than a bare interpreter invocation, guarantees the exact same
dependency versions are exercised locally, in CI, and in the eventual
deployment — the single structural fix this entire module's dependency
chapters build toward.

---

## Question 23

### Problem

**Scenario B — Legacy Project.** A large legacy Python project has:
inconsistent, unorganized imports; weak or absent type coverage;
missing documentation; and dependency drift (no lock file, unpinned
`pip install` calls scattered in onboarding notes). Propose a **staged**
modernization strategy, using only concepts taught in this module, that
does not require rewriting the project in one disruptive pass. Justify
the order of the stages.

### Solution

**Stage 1 — Stop the drift first: introduce `pyproject.toml` and
`uv.lock`.** Before touching code quality at all, capture the project's
*actual current* dependencies (even loosely constrained) into
`pyproject.toml`, and generate a committed `uv.lock`. This is placed
first deliberately: every later stage (running Ruff, running a type
checker, running tests) depends on a reproducible environment existing
in the first place — modernizing code quality on top of an
unreproducible environment risks every contributor seeing different
results.

**Stage 2 — Add Ruff, in check-only (non-blocking) mode first.**
Install Ruff as a development dependency (`uv add --dev ruff`), run
`ruff format .` once as a single, large, mechanical formatting pass
(reviewed via `git diff`, but not requiring behavioral review since
formatting never changes behavior), then enable linting gradually — via
`[tool.ruff.lint] select = [...]`, deliberately starting with a small,
high-value rule set (e.g. `F` for genuine correctness-adjacent issues)
rather than every available rule family at once, which would produce
overwhelming noise on a legacy codebase not written with those rules in
mind.

**Stage 3 — Clean up imports specifically**, using Ruff's `I` family and
manual review together: fix genuinely unused imports (`F401`), resolve
any naming collisions from wildcard or shadowing imports, and address
any circular-import problems surfaced along the way by extracting
shared functionality into lower-level modules — this is placed before
type-hint adoption because a codebase with tangled, side-effect-laden
imports makes accurately reasoning about types significantly harder.

**Stage 4 — Adopt type hints gradually, starting at public
boundaries.** Rather than typing the entire codebase at once, annotate
function signatures at module and package **boundaries** first (public
functions other code calls into) — exactly where type hints add the
most value and are cheapest to add correctly — and run a type checker
in a permissive mode initially, tightening strictness only as coverage
grows.

**Stage 5 — Backfill documentation last, prioritizing what's most
load-bearing.** Add docstrings to the same public boundaries just typed
in Stage 4 (type hints and docstrings were just established there
together, so this is the cheapest moment to document them), and write
or repair the README's installation/usage sections using the now-
accurate `pyproject.toml`/`uv.lock` from Stage 1.

**Why this order, not another**: each stage is chosen so it does not
depend on a *later* stage having already happened, and each produces
independent, already-useful value even if the project stalls partway
through — a team that only completes Stages 1–2 already has
reproducible dependencies and consistent formatting, real, durable
improvements on their own, rather than an all-or-nothing rewrite that
risks stalling with nothing usable to show for it.

---

## Question 24

### Problem

**Scenario C — AI/ML Project.** A Python AI service has a model client,
a tool layer (functions an agent can call), agent orchestration,
configuration, and tests. Using package structure, type hints
(specifically `Protocol`), Ruff, and documentation concepts from this
module, design maintainable boundaries between these pieces. Be
specific about what each boundary actually prevents.

### Solution

**Package structure**, following this module's layer-based
organization guidance:

```
src/
└── agent_service/
    ├── __init__.py
    ├── cli.py                    # entry point
    ├── config.py                   # the only file reading os.environ
    ├── providers/
    │   ├── __init__.py
    │   ├── _protocol.py             # ModelProvider Protocol
    │   └── _openai_provider.py       # one concrete implementation
    ├── tools/
    │   ├── __init__.py
    │   ├── _protocol.py               # Tool Protocol
    │   └── search_tool.py               # one concrete tool
    └── orchestration.py                   # agent loop — depends only on the Protocols above
```

**The `Protocol` boundary, and what it specifically prevents:**

```python
# providers/_protocol.py
from typing import Protocol

class ModelProvider(Protocol):
    def complete(self, prompt: str) -> str: ...
```

`orchestration.py` depends only on `ModelProvider`, never on
`_openai_provider.py` directly. **What this specifically prevents**:
swapping model providers (a different vendor, or a mock provider for
testing) would otherwise require changing `orchestration.py` itself if
it depended on a concrete class — with the `Protocol` boundary in place,
any object with a matching `complete()` method satisfies it, so
orchestration code never needs to change when a provider is swapped, and
a test can pass a trivial fake `ModelProvider` with no real network
dependency at all.

**The tool layer follows the identical pattern:**
```python
# tools/_protocol.py
class Tool(Protocol):
    name: str
    def run(self, arguments: dict) -> str: ...
```
This lets `orchestration.py` iterate over a list of `Tool`-shaped
objects without knowing or caring what each one concretely is — adding
a new tool means writing one new file satisfying `Tool`, never editing
`orchestration.py`.

**Ruff's role, and its limit:** `uv add --dev ruff`, with
`per-file-ignores` scoped to `tests/*.py` for fixture-only imports,
catches unused imports and dead code across every layer above uniformly
— but Ruff has no concept of whether the `ModelProvider`/`Tool`
boundaries are being *respected* (e.g., `orchestration.py` accidentally
importing `_openai_provider` directly, bypassing the Protocol) — that
discipline is enforced by code review and package-naming convention
(underscore-prefixed internal modules), not by any tool covered in this
module.

**Documentation, matching this module's AI/agentic-system guidance:**
document, per tool, its purpose, inputs, outputs, and **failure
behavior** explicitly (e.g., "on a provider timeout, `orchestration.py`
retries twice with backoff, then raises — it does not silently return a
fabricated response") — because an AI system's behavior additionally
depends on things (a provider's model version, non-determinism) that
aren't visible from reading the surrounding Python code the way
ordinary deterministic logic is, making this kind of explicit,
behavior-focused documentation more load-bearing here than in an
equivalent non-AI service.

---

## Question 25

### Problem

A security advisory is published for a package your project depends on
transitively (not a direct dependency — it's pulled in by a direct
dependency several levels deep). The currently locked version is
affected; a patched version exists.

1. Explain why "we didn't add this dependency ourselves" does not make
   this any less urgent.
2. Walk through the exact update-and-verification workflow, using this
   module's terminology, distinguishing this from a routine, non-urgent
   update.
3. Explain what to do if updating the direct dependency that pulls this
   package in does **not** relax the transitive requirement enough to
   pick up the patched version.

### Solution

**1. Why it's still urgent despite being transitive:** a vulnerability
in a transitive dependency is exactly as real a risk as one in a
directly-chosen package — simply having the vulnerable code installed
and reachable can be a genuine exposure, whether or not the project's
own code happens to call the specific vulnerable function itself.
Transitive dependencies are easy to overlook precisely *because* they
were never a deliberate choice, but that doesn't reduce their actual
risk.

**2. The workflow, following this module's safe-update discipline, with
urgency (not scope of review) elevated:**

1. **Identify the update precisely** — which package, current locked
   version, and target patched version.
2. **Read the advisory and the patched release's notes** — confirm
   what's actually fixed and whether the patched version is compatible
   with the direct dependency currently requiring it.
3. **Attempt the update**:
   ```bash
   uv lock --upgrade-package vulnerable-package
   ```
   *(the exact upgrade-specific flag should be confirmed against the
   currently installed `uv --help`, consistent with this module's
   guidance not to assume unverified flag specifics)* — or, if simpler,
   upgrade the **direct** dependency that pulls it in, if a newer release
   of that direct dependency itself requires a patched version of the
   vulnerable transitive package.
4. **Review the `uv.lock` diff** (`git diff uv.lock`) carefully —
   confirm the vulnerable package's version actually changed to the
   patched one, and note any other transitive shifts that came along
   with it.
5. **Run the full test suite and type checks** — a security patch is
   still a real dependency change and deserves the same verification any
   update does.
6. **Commit `pyproject.toml`/`uv.lock` together**, with a commit message
   explicitly naming the advisory being addressed, and treat this as a
   **priority** merge rather than deferring it into a routine update
   batch.

**What's different from a routine update:** the *review depth* (steps
2, 4, 5) stays the same as any responsible update — the difference is
**priority and urgency**: this update should not wait for a scheduled,
periodic dependency review; it should be fast-tracked ahead of routine,
non-urgent updates precisely because the risk of *not* patching grows
the longer it's deferred.

**3. If the direct dependency doesn't relax the requirement enough:**
consider **replacing** the direct dependency with an alternative package
serving the same purpose, if one exists whose own dependency chain
isn't affected — the same "replace a conflicting dependency" resolution
strategy used for an ordinary conflict, now applied under security
urgency rather than a routine version mismatch. If no alternative
exists and no update path relaxes the requirement, this becomes a
genuine engineering tradeoff requiring explicit, documented review —
not something to silently ignore.

---

## Question 26

### Problem

Design a typed interface for a swappable notification backend (email
today, SMS possibly later), and produce the accompanying Architecture
Decision Record explaining the choice to use structural typing
(`Protocol`) instead of an abstract base class with inheritance.

### Solution

**The typed interface:**

```python
# notifications/_protocol.py
from typing import Protocol


class Notifier(Protocol):
    def send(self, recipient: str, message: str) -> bool:
        """Send message to recipient.

        Returns:
            True if the backend accepted the message for delivery;
            does not guarantee final delivery to the recipient.
        """
        ...
```

```python
# notifications/_email.py
class EmailNotifier:
    def send(self, recipient: str, message: str) -> bool:
        ...  # SMTP call
```

```python
# notifications/__init__.py
from notifications._protocol import Notifier
from notifications._email import EmailNotifier

__all__ = ["Notifier", "EmailNotifier"]
```

**The ADR:**

```markdown
# ADR 0004: Use Protocol, not an abstract base class, for Notifier

## Context

We need a swappable notification backend — email now, likely SMS
later — that calling code can depend on without knowing which
concrete implementation is in use, and that's easy to fake in tests.

## Decision

Define `Notifier` as a `typing.Protocol` with one method, `send()`.
Concrete backends (`EmailNotifier`, and a future `SmsNotifier`)
implement matching methods with NO inheritance from `Notifier`
required.

## Alternatives Considered

- **Abstract base class (`abc.ABC`) with an abstract `send()`
  method**: rejected as the primary mechanism. It would work, but it
  requires every backend — including test doubles — to explicitly
  inherit from `NotifierBase`, coupling every implementation to one
  specific class hierarchy even when no shared implementation code is
  actually needed between backends. A structural `Protocol` achieves
  the same call-site safety (a type checker still verifies `send()`'s
  signature) without that inheritance coupling.
- **No formal interface at all (duck typing with no annotation)**:
  rejected — callers would lose static verification entirely; a typo
  in a backend's method name would only surface at runtime.

## Consequences

- Any object with a matching `send(recipient: str, message: str) ->
  bool` method satisfies `Notifier` automatically — a test can pass a
  trivial fake object with no real inheritance or network dependency
  at all.
- If backends ever need genuinely shared implementation code (not just
  a shared signature), this decision would need revisiting — a
  `Protocol` provides no shared method bodies the way a base class
  could.
```

**Why `Protocol` over inheritance here specifically:** the three
backends (current and future) share no actual implementation logic —
only a common *shape*. A `Protocol` verifies that shape statically
without forcing every implementation, including lightweight test
doubles, into a shared class hierarchy they gain nothing from — exactly
the tradeoff the ADR's "Alternatives Considered" section makes
explicit, including the one condition (shared implementation code
becoming necessary) under which the decision should be revisited.

**Production consideration:** documenting *why* `Protocol` was chosen
over an ABC — not just that it was — is what lets a future maintainer
evaluate whether a later requirement (e.g., genuinely shared retry
logic across backends) invalidates the original reasoning, rather than
either blindly preserving or carelessly discarding a decision whose
rationale was never recorded.

---

## Question 27

### Problem

A team notices their documentation has quietly become unreliable: three
README code examples no longer match the current CLI, a docstring
claims a function returns `None` when it now returns a value, and no
one can say which of these changes broke which documentation. Design a
CI-integrated process, using only concepts from this module, that would
have caught each of these three specific failures automatically, and
explain the underlying discipline it depends on.

### Solution

**Failure 1 — stale README code examples.** The fix is **executable
documentation**: wherever practical, express README/docstring examples
as `doctest`-style blocks and run them as part of the test suite:

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    >>> calculate_total(10.0, 3)
    30.0
    """
    return price * quantity
```

```bash
uv run python -m doctest src/app/pricing.py -v
```

Because `doctest` actually **executes** the example and compares real
output against what's written, a CLI/function change that breaks the
example fails this check immediately — converting a silent drift into a
loud, CI-caught failure, rather than something only a human reader
eventually notices by trial and error.

**Failure 2 — a docstring claiming the wrong return behavior.** This is
harder to catch mechanically (a plain-prose `Returns:` claim isn't
executable), which is exactly why it must be caught **during code
review**, per this module's documentation-in-code-review guidance: a
reviewer explicitly asks, for any PR that changes a public function's
behavior, "does the docstring's `Returns:`/`Raises:` section still
match this change?" — treating a stale docstring exactly like a broken
test, something that blocks merge, not an afterthought.

**Failure 3 — no one can trace which change broke which documentation.**
This is a **Documentation as Code** discipline failure: documentation
must be updated **in the same commit/PR** as the code change that
requires it, not as a separate, later, easily-forgotten task. The fix
is procedural, enforced at review time: a reviewer checking "is the
public API documented, are examples still correct, are configuration
changes documented" as a standing part of every PR review — exactly
this module's documentation-review checklist — means the *commit
history itself* records which change caused which documentation update,
because they land together.

**The CI pipeline, assembled:**

```
checkout code
    ↓
uv sync
    ↓
uv run pytest            # includes doctests, catching Failure 1's category
    ↓
uv run ruff check .
    ↓
uv run mypy .
    ↓
(code review gate — catches Failures 2 and 3's category, since these
 are not mechanically detectable)
    ↓
merge
```

**The underlying discipline this all depends on:** documentation drift
is not eliminated by any single tool — it is reduced by combining what
*can* be automated (executable examples, run in the same test suite as
everything else) with what genuinely requires human judgment
(reviewing whether prose still accurately describes behavior), and by
never letting a documentation update be deferred to "a follow-up PR,"
which is, in practice, one of the most common ways this exact kind of
accumulated documentation debt begins.

---

## Question 28

### Problem

**Capstone.** A legacy CLI project currently looks like this:

```
project/
├── app.py            # everything: argparse, business logic, file I/O, all in one file
├── requirements.txt    # unpinned package names, no lock file
└── README.txt            # three sentences, no install/usage instructions
```

No tests, no linter, no type hints. Produce a complete, prioritized
migration plan to bring this project to the production-oriented
standard taught across this module (src layout, `pyproject.toml`/
`uv.lock`, Ruff, type hints, and documentation), and justify your
prioritization with an explicit trade-off analysis — not just a list of
steps.

### Solution

**Step 1 — Establish reproducibility first: `pyproject.toml` +
`uv.lock`.**
```bash
uv init .
uv add <every package currently in requirements.txt, with sensible bounded ranges>
```
**Trade-off:** this is pure infrastructure work with no visible feature
change, which can be a hard sell to stakeholders — but it is prioritized
first because *every later step's own tooling* (Ruff, a type checker,
tests) needs a reproducible, shared environment to run consistently
against; doing anything else first risks each subsequent step being
independently, silently inconsistent across contributors.

**Step 2 — Introduce a src-layout package, moving `app.py`'s logic
into responsibility-separated modules, before adding any quality
tooling.**
```
project/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── cli.py           # argparse + main() -> int + __main__ guard
│       ├── validation.py     # pure validators, extracted from app.py
│       └── processing.py      # business logic, extracted from app.py
├── tests/
├── pyproject.toml
└── README.md
```
**Trade-off:** this is the single riskiest step — moving working code
risks introducing regressions with no test suite yet in place to catch
them. It's prioritized *before* Ruff/type hints specifically because
restructuring a tangled single file is significantly harder once strict
lint/type rules are also being enforced on it mid-move; separating
"move the code" from "clean up the code" keeps each step individually
reviewable. Mitigate the regression risk with careful manual testing of
the CLI's existing behavior before and after the move.

**Step 3 — Add a minimal test suite around the newly separated
modules**, specifically `validation.py` and `processing.py` (now
side-effect-free and independently testable, unlike the original
tangled `app.py`).
**Trade-off:** writing tests for legacy behavior (rather than
new, desired behavior) is unglamorous work, but it's prioritized here,
*before* Ruff/type-hint adoption, because it provides the safety net
every subsequent, more invasive change (auto-fixes, type-hint
corrections) needs in order to be applied with confidence rather than
hope.

**Step 4 — Add Ruff, starting with formatting and a conservative rule
set.**
```bash
uv add --dev ruff
uv run ruff format .
uv run ruff check --fix .
```
**Trade-off:** enabling every Ruff rule family at once on a legacy
codebase produces overwhelming noise; starting narrow (`F`, `I`) and
expanding gradually keeps the signal-to-noise ratio high enough that the
team actually acts on findings rather than tuning them out.

**Step 5 — Adopt type hints at module boundaries, then run a type
checker in a permissive mode, tightening gradually.**
**Trade-off:** typing 100% of a legacy codebase immediately is rarely
worth the effort relative to typing the functions other code actually
calls into (module/package boundaries) — this targets the highest-value
20% first rather than chasing full coverage as a goal in itself.

**Step 6 — Rewrite `README.txt` as `README.md`**, now that installation
(`uv sync`), usage, and configuration are all accurate and stable enough
to document without immediately going stale — covering prerequisites,
installation, usage with real example output, and a short
troubleshooting section.
**Trade-off:** documentation is deliberately placed **last**, not
because it matters least, but because documenting a project that is
still actively being restructured (Steps 1–5) produces documentation
that would immediately go stale — writing it once the structure has
stabilized avoids that churn.

**Overall justification for this ordering:** each step is sequenced so
it does not depend on a later step having already happened, and each
provides independent value even if the migration stalls after that
step — exactly the same "staged, non-disruptive" principle used in
Question 23's legacy-modernization scenario, now applied end-to-end
across every concept this module teaches, from dependency management
through documentation.

---

# Final Coverage Review

Across these 28 questions, every one of the seven source files
contributed multiple, meaningfully tested concepts: **imports/modules**
(naming collisions, the `__main__` guard, import-time side effects,
circular imports, `sys.path`) in Questions 1, 2, 8, 9, 15, 23, 28;
**project layout** (file/module/package/project, flat vs. src layout,
responsibility boundaries, package API design) in Questions 3, 9, 15,
19, 22, 24, 28; **`pyproject.toml`/lock files/`uv`** (dependency
declarations, version specifiers, `uv add`/`sync`/`lock`,
reproducibility, CI/containers) in Questions 4, 10, 16, 17, 22, 25, 28;
**dependency management/SemVer** (MAJOR/MINOR/PATCH, bounded ranges,
conflicts, drift, safe updates, security) in Questions 5, 11, 16, 17,
25, 28; **Ruff** (formatting vs. linting, commands, rule families,
configuration, per-file-ignores, CI integration) in Questions 6, 12, 18,
22, 27; **type hints/type checking** (`Optional`/`None`, `Protocol`,
`TypedDict`, the type-checker-vs-linter distinction) in Questions 13,
18, 19, 24, 26; and **docstrings/READMEs/documentation** (Google-style
docstrings, type hints vs. docstrings, README structure, API contracts,
ADRs, documentation drift, CI-integrated documentation testing) in
Questions 7, 13, 14, 20, 21, 26, 27. Hard and Advanced questions
deliberately combined concepts across multiple files — reflecting how
these seven topics function together in a real Python codebase, not as
seven isolated subjects.
