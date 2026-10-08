# Imports, Modules, and `__main__`

## Learning Objectives

By the end of this chapter you will be able to:

- Explain what a Python module actually is, and why organizing code
  into modules matters for reuse, namespace isolation, and
  maintainability.
- Use every common import style (`import`, `import ... as ...`,
  `from ... import ...`, `from ... import ... as ...`) and know when
  each is appropriate.
- Explain, step by step, what Python actually does when it imports a
  module — searching, loading, executing, and binding — and why
  importing is not "copying code into the current file."
- Explain module namespaces and module attributes, including
  `__name__`, `__file__`, `__doc__`, `__package__`, and `__spec__`.
- Explain `__name__` precisely — what it holds when a file is imported
  versus executed directly — and use `if __name__ == "__main__":`
  correctly.
- Design a `main() -> int` entry point combined with
  `raise SystemExit(main())`, connecting directly to this course's
  prior CLI, exit-code, and logging chapters.
- Explain import caching and `sys.modules`, and why, under normal
  imports, a module's top-level code runs only once per process.
- Explain `sys.path` and how Python searches for modules, and diagnose
  `ModuleNotFoundError`/`ImportError` systematically.
- Use absolute and relative imports correctly, and explain why relative
  imports depend on package context.
- Explain packages, `__init__.py`, and namespace packages at a
  foundational level sufficient to understand imports.
- Explain why `from module import *` is discouraged, and what `__all__`
  controls.
- Diagnose and redesign around circular imports.
- Apply good import hygiene: ordering, explicitness, avoiding
  import-time side effects, avoiding unnecessary or wildcard imports.
- Design a module that is simultaneously reusable (importable) and
  executable (runnable directly) using the `__main__` guard.
- Explain the difference between `python file.py` and
  `python -m package.module`, and when each is the right choice.
- Explain how clean module boundaries make CLI programs and their
  logic easier to test.
- Distinguish standard-library, local, and third-party imports.
- Use `importlib.import_module()` and understand `importlib.reload()`
  as a development/debugging tool, not an application architecture
  technique.
- Debug realistic import failures systematically.
- Design a small, multi-module CLI application with clean import
  boundaries and no unwanted import-time side effects.

## Prerequisites

This chapter assumes you've completed Stage 1 Module 1.5 (Text Files,
Structured Data, and CLI Programs) — in particular
`06-command-line-arguments-with-argparse.md`'s `main(argv) -> int`
pattern, `07-standard-streams-and-exit-codes.md`'s exit-code
conventions, and `08-logging-versus-print.md`'s logging setup — all of
which this chapter extends into proper multi-file module design. No
prior knowledge of Python's import system is assumed.

## 1. What Is a Python Module?

The simplest possible starting point: **a Python module is a named
unit of Python code managed by the import system**, and a `.py` file is
the most common way to define one. Calling a `.py` file a "module"
rather than "a file" signals something specific: it's a file whose code
is meant to be **imported and reused** by other code, not (necessarily)
run directly.

```python
# math_utils.py

def add(a, b):
    return a + b


def multiply(a, b):
    return a * b
```

Another file can now reuse this code without copying it:

```python
# main_program.py
import math_utils

result = math_utils.add(2, 3)
print(result)   # 5
```

**Why modules exist** — the same handful of reasons this entire course
has been building toward since its very first chapters:

- **Code organization** — a single, giant file containing everything
  a program does becomes hard to navigate as it grows; splitting
  related functionality into separate files gives each piece a clear,
  findable home.
- **Reuse** — `math_utils.py`'s functions can be imported by any number
  of other files, without copying and pasting the same code into each
  one (and then needing to fix a bug in every copy separately).
- **Namespace isolation** — `math_utils.add` and some other module's
  own `add` function can coexist without colliding, because each lives
  inside its own module's namespace (§4 makes this precise).
- **Maintainability** — a bug in how addition is implemented has
  exactly one place to be fixed: `math_utils.py` — not scattered across
  every file that happens to need addition.

The distinction between "a Python file" and "a Python module" is
really a distinction of **intent and usage**, not syntax — any `.py`
file *can* be imported as a module (this chapter works exclusively with
`.py`-file modules); whether it's *designed* to be
reused that way is a design choice this entire chapter is about
making deliberately, rather than by accident.

## 2. Import Basics

Python offers four common import forms, each with a different effect
on what names become available and how.

```python
import math
print(math.sqrt(16))   # 4.0
```
`import math` binds the name `math` in the current namespace to the
module object itself. Every name defined inside `math` must be
accessed *through* that module name — `math.sqrt`, not a bare `sqrt`.

```python
import math as m
print(m.sqrt(16))   # 4.0
```
`import math as m` does the same thing, but binds the module to the
name `m` instead of `math` — useful for shortening a long or
frequently-repeated module name (this is exactly why you will later
see conventions like `import numpy as np`), or for avoiding a naming
collision with something else already using the name `math` in the
same file.

```python
from math import sqrt
print(sqrt(16))   # 4.0
```
`from math import sqrt` binds only the name `sqrt` directly into the
current namespace — no `math.` prefix needed, but also no access to
anything else inside the `math` module through this import alone (a
separate `from math import sqrt, pow` would be needed for more names).

```python
from math import sqrt as square_root
print(square_root(16))   # 4.0
```
`from math import sqrt as square_root` combines both ideas: importing
a specific name directly, and giving it a new local name.

**Namespace differences, made concrete:**

| Form | What's bound | Access pattern |
|---|---|---|
| `import math` | the module `math` | `math.sqrt(...)` |
| `import math as m` | the module, renamed `m` | `m.sqrt(...)` |
| `from math import sqrt` | just the name `sqrt` | `sqrt(...)` |
| `from math import sqrt as square_root` | `sqrt`, renamed | `square_root(...)` |

**When each style is appropriate:**

- **`import module`** is the clearest choice when you use several
  names from that module, or when keeping `module.name` visible at the
  call site makes code easier to read (it's immediately obvious
  `math.sqrt` comes from `math`, without scrolling up to check the
  imports).
- **`import module as alias`** is appropriate for long, awkward, or
  conventionally-abbreviated module names, or to resolve a genuine
  naming conflict.
- **`from module import name`** is appropriate when you use one or two
  specific names very frequently, and the module prefix would add
  noise without adding clarity (e.g. `from pathlib import Path`,
  used throughout this course).
- **`from module import name as alias`** is appropriate when the
  imported name would otherwise collide with something else already
  defined or imported in the current file.

**A naming-conflict example** worth seeing directly:
```python
from json import dumps
from my_custom_serializer import dumps   # BUG: silently replaces the previous `dumps`
```
The second import silently shadows the first — any later call to
`dumps(...)` now uses `my_custom_serializer`'s version, not `json`'s,
with no error or warning at all. This is exactly the kind of problem
`import module` (keeping both accessible as `json.dumps` and
`my_custom_serializer.dumps`) or an explicit alias
(`from my_custom_serializer import dumps as custom_dumps`) avoids.

## 3. What Happens During Import?

It is tempting to think of `import module` as "paste `module.py`'s
code into this file" — this mental model is **wrong**, and the
difference matters for everything from §10's import-side-effects
discussion to §11's caching behavior. The actual sequence:

```
1. Python receives an import request        (import module_name)
2. Python checks sys.modules first            (§11 — already imported?)
3. If not cached, the import system FINDS the module   (§13 — e.g. via sys.path)
   and produces a "spec" describing how to load it
4. Python CREATES and initializes an empty module OBJECT
5. Python places that module object in sys.modules (the cache)
   BEFORE running any of the module's code
6. Python EXECUTES the module's top-level code, once, top to bottom;
   everything defined during that execution (functions, classes,
   variables) becomes an attribute of the module object
7. If execution succeeds, the import completes
8. The import statement binds the requested name(s) in the IMPORTING
   code's namespace (the module itself, or a specific name from it)
```

The ordering of steps 4–6 matters: the module object exists, and is
already visible in `sys.modules`, *while* its own top-level code is
still running. §19 relies on exactly this fact to explain circular
imports. (If the module's code raises an exception during step 6,
Python removes the half-built module from `sys.modules` again, so a
failed import does not leave a broken cached module behind.)

A concrete example makes step 6 — "executes the module's top-level
code" — vivid:

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

```bash
$ python main.py
greeting.py is being executed
Hello!
```

Notice `"greeting.py is being executed"` prints **immediately when
`import greeting` runs** — before `say_hello()` is ever called. This is
the concrete proof that importing genuinely *executes* the module's
top-level code (defining `say_hello` is itself one of the things that
execution does), rather than merely making its text available for
later use. §10 builds directly on this fact to explain why unexpected
module-level side effects are dangerous.

The **module object** created in step 4 (and filled in during step 6)
is the thing `import greeting`
actually binds to the name `greeting` in `main.py` — every function,
class, and variable `greeting.py` defines at its top level becomes an
**attribute** of that one object, which is exactly why
`greeting.say_hello()` works: it's ordinary attribute access on an
ordinary (if special-purpose) Python object.

## 4. Module Namespace

A **namespace** is a mapping from names to objects — a place where
names are looked up. Every module has its **own** namespace, entirely
separate from every other module's namespace and from the namespace of
whatever file imports it. This is precisely what §1 meant by
"namespace isolation."

```python
# module_a.py
value = "from module_a"

# module_b.py
value = "from module_b"

# main.py
import module_a
import module_b

print(module_a.value)   # from module_a
print(module_b.value)   # from module_b
```

Both modules define a variable named `value` — and there is **no
collision at all**, because each `value` lives inside its own module's
namespace, accessed only through that module's name
(`module_a.value` vs. `module_b.value`). This is the namespace
boundary `import module_name` (as opposed to `from module_name import
*`, §18) preserves — and exactly why it's a much safer default import
style.

`math.sqrt` is this same idea applied to the standard library: `sqrt`
is a name that exists *inside* `math`'s namespace, not floating freely
in whatever file imports `math` — which is precisely why two different
modules can each define their own function named `sqrt` (or anything
else) without any conflict, as long as each is accessed through its
own module's name.

## 5. Module Attributes

Because a module is an ordinary Python **object** once imported
(§3's step 4), it can have **attributes** beyond just the names you
explicitly defined — Python automatically populates several special
ones for you.

```python
import math

print(math.__name__)   # 'math'
print(math.__doc__)    # the module's docstring, if any
```

| Attribute | Meaning |
|---|---|
| `__name__` | The module's name as known to the import system (or `"__main__"` — §6) |
| `__file__` | The filesystem path the module was loaded from (absent for some built-in/frozen modules) |
| `__doc__` | The module's docstring — the string literal, if any, at the very top of the file |
| `__package__` | The package context the module belongs to: `""` for an *imported* top-level module, the package name (e.g. `"mypackage"`) for a module inside a package, and `None` for a file run directly as a script (see below) |
| `__spec__` | A `ModuleSpec` object describing how this module was found and loaded (its origin, loader, and more) — mainly consulted by the import system itself and by tools that introspect it |

```python
# greeting.py
"""A tiny greeting module."""

def say_hello():
    print("Hello!")
```
```python
import greeting

print(greeting.__doc__)     # A tiny greeting module.
print(greeting.__file__)    # /path/to/greeting.py
print(greeting.__package__) # '' (empty — greeting.py is a top-level module, not inside a package)
```

`__package__` also depends on *how* a file is run, not only where it
lives (verified on CPython 3.14):

| How it runs | `__name__` | `__package__` | `__spec__` |
|---|---|---|---|
| `import greeting` (top-level module) | `"greeting"` | `""` | a `ModuleSpec` |
| `import mypackage.cli` | `"mypackage.cli"` | `"mypackage"` | a `ModuleSpec` |
| `python file.py` | `"__main__"` | `None` | `None` |
| `python -m mypackage.cli` | `"__main__"` | `"mypackage"` | a `ModuleSpec` |

These attributes are not obscure CPython trivia — `__name__` (§6) is
central to the entire `__main__` pattern this chapter builds toward;
`__file__` and `__doc__` are genuinely useful for introspection,
tooling, and documentation generation; `__package__` and `__spec__`
matter once relative imports (§15) and packages (§16) enter the
picture — each is introduced here, at the depth needed to understand
imports, and revisited in more detail exactly where it becomes
relevant.

## 6. `__name__`

`__name__` is the single most important module attribute in this
chapter — it is what makes the `if __name__ == "__main__":` pattern
(§8) work at all.

```python
# greeting.py
print(f"__name__ is: {__name__!r}")
```

Run it two different ways:

```bash
$ python greeting.py
__name__ is: '__main__'
```
```text
>>> import greeting
__name__ is: 'greeting'
```

This is the entire mechanism, stated precisely:

- **When a file is executed directly** (`python greeting.py`), Python
  sets that file's own `__name__` to the special string
  `"__main__"` — regardless of what the file is actually named.
- **When a file is imported** as a module, Python sets `__name__` to
  the module's own name (its filename without `.py`, or its full
  dotted path if it's inside a package — e.g. `"mypackage.greeting"`).

Why this distinction matters: it gives every module a reliable way to
answer, **at runtime**, the question "was I the file the user actually
ran, or was I imported by something else?" — without that question
needing to be answered any other way (an environment variable, a
command-line flag, a global setting). §7–§8 build the rest of this
chapter's central pattern directly on top of this one fact.

## 7. `__main__`

`__main__` is Python's name for **the program's entry point** — the
one module that was actually *run*, as opposed to every other module
that got pulled in along the way by being imported.

- **`python file.py`** — Python runs `file.py` directly, and (per §6)
  sets `file.py`'s own `__name__` to `"__main__"` for the duration of
  that run.
- **`python -m package.module`** — Python locates `package.module`
  using the *same import machinery* used for a normal `import`
  statement (§13's `sys.path` search applies), but then **runs it as
  the main program** — meaning *that* module's `__name__` also becomes
  `"__main__"`, even though it was found via the package/import system
  rather than executed as a bare file path. §23 works through the
  practical difference between these two invocation styles in full.

Either way, exactly **one** module in a given run is `"__main__"` — the
entry point — while every other module involved (everything it
imports, directly or indirectly) keeps its own real name. This is
precisely why library code can safely check `if __name__ ==
"__main__":` (§8): that block will run only when *this specific file*
was the one actually launched, never when it was merely imported by
something else.

## 8. `if __name__ == "__main__":`

This is the pattern this entire chapter has been building toward:

```python
def greet(name: str) -> None:
    print(f"Hello, {name}!")


if __name__ == "__main__":
    greet("World")
```

- **Run directly:** `python greeting.py` → `__name__` is `"__main__"`
  → the `if` block executes → `"Hello, World!"` is printed.
- **Imported elsewhere:** `import greeting` → `greeting.py`'s
  `__name__` is `"greeting"`, not `"__main__"` → the `if` block does
  **not** execute → only `greet` becomes available as `greeting.greet`,
  with no side effect from the guarded code. (The guard only protects
  the code placed *inside* it; any other module-level statement outside
  the guard still runs during import — see §10.)

**Why this pattern exists**, restated precisely: it lets a single file
serve **two roles at once** — a **reusable module** (its functions and
classes can be imported and used by other code, silently, with no
unwanted side effects) and an **executable script** (running it
directly performs some specific action) — with one `if` statement
deciding, at runtime, which role currently applies.

**What it prevents**, made concrete with a "before" version that lacks
the guard:

```python
# BAD — no guard at all
def greet(name: str) -> None:
    print(f"Hello, {name}!")

greet("World")   # this runs EVERY time this file is imported, anywhere, for any reason
```
Any other file that does `import greeting_bad` — even just to reuse
`greet` as a function — immediately, silently triggers
`"Hello, World!"` being printed, as an unavoidable side effect of the
import itself. This is confusing at best (unexpected output from a
module that was only supposed to provide a function) and dangerous at
worst (§10 shows a version of this with real consequences, like
connecting to a database).

**Testing and CLI benefits**, connecting directly to this course's
prior chapters: a test file can `import greeting` and call
`greeting.greet("Test")` directly, asserting on its behavior, with
*zero* risk of the module's own "run as a script" behavior firing
during the test — this is only possible because that behavior lives
inside the `__main__` guard, not at bare module level. The exact same
property is what let
`06-command-line-arguments-with-argparse.md`'s and
`07-standard-streams-and-exit-codes.md`'s test suites call
`main([...])` directly, or `parser.parse_args([...])`, without ever
actually launching the program as a subprocess.

## 9. `main()` Function

Placing significant executable logic directly inside the
`if __name__ == "__main__":` block itself works, but scales poorly the
moment that logic grows beyond a couple of lines. An `if` block does
**not** create a new scope in Python, so any variable assigned directly
inside `if __name__ == "__main__":` is an ordinary module-level (global)
name — it lives in the module's namespace like any other. By contrast, a
variable assigned inside `main()` is local to that function and
disappears when it returns. On top of that, none of the logic inside the
guard can be called, tested, or reused as a unit.

The standard fix: wrap the entry-point logic in its own function,
conventionally named `main()`, and call *that* from the guard:

```python
def main() -> None:
    print("Running the program")


if __name__ == "__main__":
    main()
```

Directly extending
`06-command-line-arguments-with-argparse.md`'s,
`07-standard-streams-and-exit-codes.md`'s, and
`08-logging-versus-print.md`'s established production pattern, `main()`
should **return an integer status** rather than returning nothing, and
that status should be handed to `SystemExit`:

```python
import sys


def main() -> int:
    print("Running the program")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Why this exact shape is worth using for every CLI program from here
on: `main()` becomes an ordinary, callable, **testable** function — a
test can call `main([...])` directly (if it accepts `argv`, exactly as
in the argparse chapter) and assert on its return value, with no
subprocess and no risk of accidentally triggering `sys.exit()`'s
process-terminating behavior mid-test. `raise SystemExit(main())` is
the **one** place, at the very bottom of the file, where that return
value is translated into an actual process exit status — connecting
`main()`'s ordinary Python return value to the OS-level exit-code
mechanism `07-standard-streams-and-exit-codes.md` covered in full. Every
one of this course's CLI examples going forward will use exactly this
shape: `argparse` for parsing, `logging` for diagnostics, input
validation at the boundary, and `main() -> int` /
`raise SystemExit(main())` for the entry point — this chapter is what
explains *why* that specific shape, and not some other one, is the
right default.

## 10. Module-Level Code and Import Side Effects

Every statement at a module's top level — not just function/class
definitions — executes the moment that module is imported (§3, step
6). This includes things far more consequential than a `print()`
statement.

**Bad — real side effects at import time:**
```python
# app.py
print("Starting application...")
connect_to_database()          # a real network connection, opened just by importing this file
config = load_config_from_disk()  # file I/O, just from an import
```

If *any other file* — including a test file that only wants to reuse
one small function from `app.py` — writes `import app`, all of this
runs immediately and unconditionally: a database connection opens, a
config file is read from disk, and `"Starting application..."` prints
— none of which the importing code asked for or necessarily wants,
and none of which is skippable, since it's not behind any guard at
all.

**Why import-time side effects are dangerous**, concretely:

- **Unpredictability** — the mere act of importing a module for one
  small utility function can trigger unrelated, expensive, or
  stateful operations (network calls, file writes, opening a database
  connection) that the importing code never asked for.
- **Untestability** — a test that imports the module to test one
  function now also, unavoidably, opens a real database connection —
  turning a fast, isolated unit test into a slow, environment-
  dependent one, or an outright failing one if no database is
  reachable in the test environment.
- **Import-order fragility** — if two modules each have import-time
  side effects that depend on some shared state being set up first,
  the *order* modules happen to be imported in can silently change
  behavior.

**Better separation — definitions at module level, execution inside
functions, entry point behind the guard:**
```python
# app.py

def connect_to_database():
    ...   # defining the function has NO side effect — it only runs when CALLED

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

Now, `import app` (from a test, or from any other module wanting to
reuse `connect_to_database` in isolation) executes **only the function
definitions themselves** — so this module has no import-time side
effects — and none of the actual database connection, file read, or startup message happens
unless `main()` is explicitly called (which only happens automatically
when `app.py` is run directly, per §8). This is the concrete,
practical payoff of the `__main__` guard: it's not a stylistic
convention, it's what keeps importing a module a safe, predictable, and
cheap operation. Note the limit of that guarantee: the guard only keeps
the code *inside* it from running on a normal import. Module-level code
*outside* the guard still executes during import, so keeping it free of
side effects remains the module author's responsibility.

## 11. Import Caching

Under normal import behavior, a module's top-level code — including
whatever side effects it might have (§10) — runs **once per Python
process**, no matter how many different files import it. (The only
ways to run it again are explicit ones, such as `importlib.reload()`,
§27, or loading the same source under a different module name.)

```python
# counted.py
print("counted.py is executing")
```
```python
# main.py
import counted
import counted   # a second import — does NOT print again
```
```bash
$ python main.py
counted.py is executing
```

The message prints exactly **once**, even though `import counted`
appears twice. This is **import caching**: the first time a module is
imported anywhere in a running process, Python executes its top-level
code and stores the resulting module object in a cache. Every
subsequent `import counted` — from the same file, or from any other
file in the same running process — simply **reuses that same cached
module object**, without re-running its top-level code at all.

Why this matters: it means importing the same module from many
different files across a project is cheap (the expensive work happens
once, not once per import statement) and, more subtly, it means every
part of a program that imports the same module is genuinely sharing
**the same module object** — the same functions, the same module-level
variables — not separate, independent copies. A module-level variable
mutated by one part of the program (an uncommon but occasionally
useful pattern) would be visible to every other part that imported the
same module, precisely because there's only ever one instance of it
per process.

Two caveats keep this model honest. `importlib.reload()` (§27)
deliberately re-executes a module's code on request. And the cache is
keyed by module *name*: if the same source file ends up loaded under two
different names (for example, a file run as `__main__` that is also
imported by its normal name), Python treats them as two separate module
objects, each executing the code once.

## 12. `sys.modules`

The cache §11 described is a real, inspectable object:
`sys.modules` — a dictionary mapping module names to their already-
imported module objects.

```python
import sys
import math

print("math" in sys.modules)   # True — it's been imported and cached
print(sys.modules["math"] is math)   # True — the exact same object
```

`sys.modules` is what Python actually checks **first**, before doing
any of the searching or loading work described in §3 and §13 — if a
module name is already a key in `sys.modules`, Python simply returns
that cached object immediately, skipping the search/load/execute steps
entirely. This is the concrete mechanism behind "a module's top-level
code runs once per process under normal imports."

`sys.modules` is genuinely useful to **inspect** — printing
`list(sys.modules.keys())` during debugging can reveal exactly what's
been imported so far, which is occasionally the fastest way to
diagnose an unexpected import-order or caching-related bug. It is
**not** something normal application code should manually modify —
directly deleting or replacing entries in `sys.modules` bypasses the
whole import system's guarantees and is a technique reserved for
specialized tooling (test frameworks doing careful module isolation, or
import hooks), not everyday application logic.

## 13. `sys.path`

When Python needs to import a module it hasn't already cached (§12),
it has to **find** it — and for ordinary source-file modules, `sys.path`
is the list of locations it searches, in order. (Python's import
machinery uses `sys.path` as an important set of search locations; the
full import system is more general and can use different finders and
loaders as well, which this chapter does not need to go into.)

```python
import sys
print(sys.path)
```
```
['', '/usr/lib/python3.12', '/usr/lib/python3.12/lib-dynload',
 '/home/user/.venv/lib/python3.12/site-packages', ...]
```

The exact contents vary, but conceptually `sys.path` typically
includes, in some order: an entry for the **current script's own
directory** (or the current working directory, depending on how
Python was invoked — §23 covers this distinction concretely);
**standard library locations** (where `math`, `json`, `csv`, and every
other built-in module this course has used actually live on disk);
and **installed third-party package locations** — commonly a
`site-packages` directory belonging to whichever Python environment
(system Python, or a virtual environment) is currently active.

Python checks each entry in `sys.path`, in order, looking for a
matching module or package, until it finds one or exhausts the list.
The environment variable **`PYTHONPATH`**, if set, adds additional
directories to this search list — a mechanism worth knowing the name
of, though this course does not depend on setting it directly.

**Why import errors happen when Python can't find a module** follows
directly from this: if the directory containing the module you're
trying to import is not, for whatever reason, anywhere in `sys.path`
at the moment of the import, Python has genuinely nowhere left to look
— it's not that the file doesn't exist; it's that it isn't in one of
the specific places Python was told to search. §14 turns this into a
systematic diagnostic process.

## 14. Module Search and Import Errors

Two distinct exceptions signal an import failure, and knowing which
one you're looking at narrows the diagnosis significantly.

- **`ModuleNotFoundError`** — a subclass of `ImportError`, raised
  specifically when Python's search (§13) never finds a module with
  the requested name anywhere in `sys.path` at all.
- **`ImportError`** — the more general exception, also raised for
  narrower failures: the module *was* found, but a specific name you
  tried to import *from* it doesn't exist there (e.g.
  `from math import not_a_real_function`), or the module's own code
  raised an exception while executing (§3's step 6).

```text
>>> import definitely_not_a_real_module
ModuleNotFoundError: No module named 'definitely_not_a_real_module'

>>> from math import not_a_real_function
ImportError: cannot import name 'not_a_real_function' from 'math'
```

**Common causes, systematically:**

- **Wrong module name** — a typo, or the wrong case (Python module
  names are case-sensitive on virtually every real deployment target,
  even if the local filesystem happens to be case-insensitive).
- **Wrong working directory** — the module exists, but not relative to
  wherever the Python process's current directory happens to be when
  it was launched, and nothing else in `sys.path` covers its actual
  location.
- **Package structure problem** — a file expected to be part of a
  package isn't actually where the package's structure requires it to
  be (§16–§17 cover exactly what that structure needs to look like).
- **Environment mismatch** — the module (typically a third-party
  package) is installed in a *different* Python environment/virtual
  environment than the one actually running the script.
- **Missing dependency** — a genuinely uninstalled third-party package
  (this course's later chapters on dependency management cover
  installing these correctly; this chapter only needs you to recognize
  the symptom).
- **Incorrect import path** — using an absolute import
  (`from mypackage.utils import helper`) when the package isn't
  actually structured, installed, or run the way that import statement
  assumes (§15, §23).

**Systematic debugging**, in order:
```python
import sys
print(sys.path)                 # is the expected directory even in here?
print(sys.executable)           # which Python interpreter is actually running?
import subprocess
subprocess.run([sys.executable, "-m", "pip", "show", "package_name"], check=False)   # is it installed HERE?
```
Invoking pip as `[sys.executable, "-m", "pip", ...]` (or `python -m pip`
in a shell) guarantees it inspects the *same* interpreter that runs your
application, which a bare `pip` command on `PATH` does not. Checking
`sys.path` directly (does it contain what you expect?) and
`sys.executable` (is this genuinely the Python/virtual environment you
think it is?) resolves the large majority of real-world
`ModuleNotFoundError` confusion — most such errors turn out to be "the
right code, run by the wrong interpreter" or "the right file, just not
where Python is currently looking," rather than a mysterious Python
bug. §28's debugging lab works through several of these scenarios in
full.

## 15. Absolute vs. Relative Imports

**Absolute imports** spell out a module's full path from the top of
its package, exactly the way it would be imported from anywhere else
in the project:

```python
from mypackage.utils import helper
```

**Relative imports** instead describe a module's location *relative to
the importing module's own position inside its package*, using leading
dots:

```python
from .utils import helper        # a sibling module in the SAME package
from ..common import helper      # a module in the PARENT package
```

- A single `.` means "this same package" — the package the current
  module itself lives directly inside.
- Two dots, `..`, means "one level up" — the parent of that package.
  Each additional dot climbs one further level.

**Why package context matters**: a relative import only works when the
importing file is genuinely being treated as part of a package by
Python's import system — which requires it to actually be *imported as
part of that package* (e.g. via `python -m mypackage.module`, §23, or
by another module inside the same package importing it normally), not
run as a bare, standalone script (`python mypackage/module.py`
directly). Running a file directly sets its `__name__` to `"__main__"`
(§6) with no package context at all, and a relative import inside a
file executed that way raises
`ImportError: attempted relative import with no known parent package`
— one of the most common, and most confusing to a beginner, real-world
import errors, precisely because the *code* looks correct in
isolation; only the *way it's run* is the actual problem.

**Readability and maintainability tradeoffs**: absolute imports are
generally more explicit and readable — anyone reading
`from mypackage.utils import helper` immediately knows exactly where
`helper` lives, without needing to know the current file's own
location in the package tree first. Relative imports can be more
convenient *within* a package's own internal structure (especially
when refactoring — moving a whole package to a new location doesn't
require updating every internal absolute import that names the
package by its own name), but are easy to get wrong when a package's
internal layout changes. Many real projects favor absolute imports
for anything crossing a meaningful internal boundary, and reserve
relative imports for very closely related, sibling modules within the
same small subpackage.

## 16. Packages

A **package** is how Python groups multiple related modules together
under one shared namespace — the natural next step once a project
outgrows a single file, or even a handful of unrelated top-level
modules.

```
myproject/
    mypackage/
        __init__.py
        utils.py
        processing.py
    main.py
```

Here, `mypackage` is a package (a *directory*, rather than a single
file) containing two **submodules**, `utils.py` and `processing.py`.
From outside the package:

```python
from mypackage.utils import helper
from mypackage import processing
```

The dotted name `mypackage.utils` mirrors the directory structure
directly — this is exactly the naming pattern behind `__name__` (§6)
for any module living inside a package: its `__name__` would be
`"mypackage.utils"`, not just `"utils"`.

**`__init__.py`** is what marks a directory as a **regular package**
(the traditional, and still most common, kind) rather than just an
ordinary directory that happens to contain `.py` files — §17 covers
its role in full. It is *not* required for every package, though:
**namespace packages**, at a purely conceptual
level worth knowing the name of: modern Python (3.3+) also supports
packages *without* an `__init__.py` file at all, called **namespace
packages**, primarily useful for splitting a single logical package's
code across multiple separate distributions — a genuinely advanced,
uncommon scenario this chapter does not need to teach in depth; for
essentially all code you'll write in this course and beyond, an
explicit `__init__.py` remains the standard, clearest choice.

This chapter introduces packages only to the depth imports require;
project layout and package structure design in full is the dedicated
subject of the very next chapter in this module.

## 17. `__init__.py`

`__init__.py` is a file placed directly inside a package directory,
and it plays two closely related roles.

**Marking a directory as a regular package** — historically, and still
the clearest, most explicit signal — the presence of `__init__.py` (even
if completely empty) tells Python "treat this directory as a regular
importable package." `__init__.py` is used for regular packages and is
optional for namespace packages (§16), but for the code you write in
this course, including it is the standard, clearest choice.

**Package initialization** — `__init__.py`'s own top-level code runs
(§3) exactly once, the first time *any* module inside that package is
imported — before the specific submodule you actually asked for. This
makes it a natural, if optional, place to set up anything the whole
package needs available immediately.

**Controlling the package-level API** is the most common deliberate
use of `__init__.py`'s content: re-exporting specific names from
submodules, so users of the package can write a shorter, more
convenient import:

```python
# mypackage/__init__.py
from .utils import helper
from .processing import transform
```

```python
# without this __init__.py content, users would need:
from mypackage.utils import helper

# with it, this shorter form also works:
from mypackage import helper
```

**Why it may contain little or no code** is equally important to
understand: an empty `__init__.py` is completely valid, and extremely
common — it's sufficient just to mark the directory as a package,
with every actual submodule imported explicitly by its own full path
(`from mypackage.utils import helper`). Whether to add re-exports is a
deliberate API-design choice (making a package's *public* surface
smaller and more convenient), not something every package must do —
an `__init__.py` stuffed with substantial, non-trivial logic can
itself become a source of surprising import-time side effects (§10),
exactly the failure mode this chapter has been warning against
throughout.

## 18. `from ... import *`

The **wildcard import** pulls every public name out of a module
directly into the importing file's own namespace, with no prefix at
all:

```python
from math import *

print(sqrt(16))   # works — but where did `sqrt` come from?
print(pi)          # also works — same question
```

**Why this is generally discouraged:**

- **Namespace pollution** — every name the module exposes becomes
  part of the current file's namespace at once, whether or not you
  actually need (or even know about) most of them.
- **Readability** — anyone reading `sqrt(16)` later, without seeing
  the import statement itself, has no way to tell where `sqrt` came
  from — `import math; math.sqrt(16)` answers that question at the
  call site, every time, with zero ambiguity.
- **Name collisions** — if two different wildcard-imported modules
  both define something named, say, `pi` (however unlikely for `pi`
  specifically, this generalizes to any name), the second import
  silently overwrites the first, exactly like §2's `dumps` collision
  example, but far harder to spot since neither name appears explicitly
  anywhere in the importing code.

**`__all__`**, at a conceptual level: a module can define a list named
`__all__` containing the specific names it considers its intended
*public* API —

```python
# mymodule.py
__all__ = ["public_function"]

def public_function():
    ...

def _internal_helper():   # not exported by "from mymodule import *"
    ...
```

`from mymodule import *` then imports **only** the names listed in
`__all__`, if it's defined — a way for a module's author to at least
bound the damage of a wildcard import, though it does nothing to
address the readability problem at each individual call site. The
practical guidance this course follows throughout: prefer explicit
imports (`import module`, or `from module import specific_name`) in
essentially all real code; treat `from module import *` as something
you might occasionally *see* in older code or quick interactive
exploration, not something to reach for in code meant to be
maintained.

## 19. Circular Imports

A **circular import** happens when two modules depend on each other —
module A imports module B, and module B (directly, or through some
chain of other imports) imports module A right back.

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

```bash
$ python -c "import a"
```
This raises an `ImportError`. Its representative form is:

```text
ImportError: cannot import name 'function_a' from partially initialized
module 'a' (most likely due to a circular import)
```

The exact wording varies between Python versions (some versions append a
file path or a "consider renaming" hint instead), so rely on the
*meaning* — "the name isn't there yet, because the module is only
partially initialized" — rather than on an exact string. Not every
circular-looking layout fails: plain `import a` / `import b` at the top
of both files, with the other module's names used only inside function
bodies, usually imports without error (the names are looked up later,
when the functions are called). The failure above happens because
`from ... import name` needs the name to exist *at import time*.
(Run it as `import a` rather than `python a.py`: running `a.py` as the
script makes it `__main__`, so `b`'s `from a import ...` imports `a` a
second time under the name `a`, and the error then names `function_b`
instead — a small demonstration of the "same source, different module
identity" caveat from §11.)

**Why this happens**, connecting directly to §3 and §11, step by step
for `import a`:

1. Python creates module `a`, puts it in `sys.modules` (§3 step 5), and
   starts executing `a.py`'s top-level code.
2. The first line of `a.py`, `from b import function_b`, begins
   importing `b`, so Python starts executing `b.py`.
3. The first line of `b.py`, `from a import function_a`, asks for
   `function_a` from `a`.
4. `a` is **already in `sys.modules`**, so Python does **not** re-run
   `a.py` (that would loop forever); it uses the module object it has.
5. But `a` has not finished executing — it is still stuck on line 1 —
   so `def function_a` has not run yet, and `function_a` does not exist
   on the module object.
6. Python therefore reports that it cannot import `function_a` from a
   **partially initialized module** — the error shown above.

**Symptoms worth recognizing**: an `ImportError` mentioning "partially
initialized module"; behavior that changes depending on which of the
two files is run or imported *first*; a working `import` statement
followed by an `AttributeError` when a specific name from that module
is actually used, because the module object existed but wasn't fully
populated yet at the moment the import completed.

**How to diagnose**: trace the actual import chain — which module
imports which, in what order — often most easily done by temporarily
adding a `print(f"importing {__name__}")` at the very top of each
suspect module and observing the order they actually print in.

**Redesigning around it — design solutions, not hacks:**

- **Merge the two modules** if they're this tightly coupled — genuine
  mutual dependency at the module level is often a sign the split
  between them was drawn in the wrong place to begin with.
- **Extract the shared functionality** both modules need into a
  *third*, lower-level module that neither `a` nor `b` needs to import
  the other for.
  ```python
  # shared.py — both a.py and b.py import THIS, neither imports the other
  def shared_logic():
      ...
  ```
- **Move the import inside a function**, deferring it until the
  function is actually called rather than at module import time — a
  legitimate, occasionally-necessary technique for breaking a genuine
  cycle, but one that should be treated as a narrow, deliberate escape
  hatch, not a first-choice fix, since it hides the dependency from
  anyone scanning the file's top-level imports.
- **Reconsider the dependency direction** — often, one of the two
  modules doesn't actually need to depend on the *whole* other module,
  only on one small piece of it, which can be restructured (passed in
  as a parameter, or moved to the shared module above) to remove the
  cycle entirely.

## 20. Import Style and Code Quality

Good import hygiene, gathered into one place, extending the PEP 8
convention this section introduces conceptually (without requiring you
to memorize the full style guide):

- **Imports at the top of the file** — before any other code, so
  every one of a file's dependencies is visible at a glance, in one
  place, rather than scattered throughout.
- **Grouped by origin, in order:** standard library imports first
  (`os`, `sys`, `json`), then third-party package imports, then local/
  project imports — conventionally with a blank line separating each
  group.
  ```python
  import json
  import sys
  from pathlib import Path

  import requests   # a third-party package

  from mypackage.utils import helper   # a local, project-specific import
  ```
- **Explicit imports** over wildcard imports (§18).
- **Meaningful aliases** (§2) — `import numpy as np` is a well-known,
  readable convention; `import numpy as n2` is not.
- **Avoid unnecessary imports** — an imported name that's never
  actually used adds noise, and (more importantly) can hide accidental
  unused-dependency bloat that later confuses anyone trying to
  understand what a module actually needs.
- **Avoid import-time side effects** (§10) — imports should be safe
  and cheap, every time, with no exceptions "just this once."
- **Avoid circular dependencies** (§19) — treat one as a signal to
  reconsider the module boundary, not merely a bug to route around.

## 21. Reusable Module Design

Putting §1–§20 together into one concrete, well-organized module
shape:

```python
# report_utils.py
"""Utilities for building simple text reports."""

# --- constants ---
DEFAULT_WIDTH = 40

# --- helper functions (private-ish; not part of the intended public API) ---
def _pad_line(text: str, width: int) -> str:
    return text.ljust(width)

# --- public functions ---
def build_report(title: str, lines: list[str], width: int = DEFAULT_WIDTH) -> str:
    header = _pad_line(title, width)
    body = "\n".join(_pad_line(line, width) for line in lines)
    return f"{header}\n{'-' * width}\n{body}"

# --- entry point (only relevant when this file is run directly) ---
def main() -> int:
    report = build_report("Demo Report", ["line one", "line two"])
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

The shape, named explicitly: **constants** first (data every function
below might need); **helper functions** (an underscore prefix is the
conventional signal "this is an internal implementation detail, not
part of what this module promises to other code" — Python doesn't
enforce this, but it communicates intent clearly); **public functions**
(the module's actual, intended interface); **`main()`**, containing
whatever this file should do *if run directly*; and the **`__main__`
guard**, the one line deciding whether that happens.

**What happens during import** of this exact file: every constant and
function *definition* executes (cheaply — defining a function does not
run its body), but **nothing else** — no report is built, nothing is
printed, `main()` is never called. **What happens during direct
execution**: everything above, *plus* the guard fires, calling
`main()`, which builds and prints a demo report, and the process exits
with status `0`. Every module you write from this point in the course
onward should be evaluated against this same shape: can it be safely
imported, for just its functions, with zero unwanted side effects?

## 22. Script vs. Module

Two words this chapter has used carefully, worth defining against each
other directly:

- A **script** is a file primarily meant to be **executed directly** —
  its main value is *what running it does*, not what other code might
  import from it.
- A **module** is a file primarily meant to be **imported and
  reused** — its main value is the functions/classes/constants it
  makes available to other code.

Many real files are neither purely one nor the other — and, crucially,
**one Python file can intentionally support both roles at once**,
exactly via the `__main__` guard pattern §8–§9 and §21 built up in
full: reusable (its functions can be imported with zero side effects)
*and* executable (running it directly performs a specific, useful
action). This dual nature is not a compromise or a hack — it's a
deliberate, standard, widely-used Python design pattern, and it's the
default shape this course recommends for essentially every non-trivial
Python file you write from here on.

## 23. `python file.py` vs. `python -m`

Two different ways to run the *same* code can behave differently in
ways that matter, once packages (§16) are involved.

**`python app.py`** runs `app.py` as a standalone script. Python adds
`app.py`'s own containing directory to the *front* of `sys.path`
(§13) — meaning `app.py` can freely import sibling files in that same
directory with plain `import` statements — but `app.py` itself has
**no package context** at all (its `__package__` is `None` and its
`__spec__` is `None`, while its `__name__` is `"__main__"`, per §6). This is exactly why a relative
import (§15) inside a file run this way fails: there is no package for
`.` or `..` to be relative *to*.

**`python -m package.module`** instead tells Python to use its normal
**import machinery** (the same search process, `sys.path` and all) to
locate `package.module`, and then run *that* module as the program's
entry point. Because it's located through the actual package/import
system, it genuinely has package context — `__package__` is correctly
set to `"package"`, and relative imports inside it work exactly as
they would if it had been imported normally from elsewhere in the
project. Its `__name__` is still `"__main__"` (it *is* the entry
point); the package context comes from `__package__`, not from
`__name__`.

A concrete project structure makes the difference vivid:

```
myproject/
    mypackage/
        __init__.py
        cli.py           # uses `from .utils import helper` — a RELATIVE import
        utils.py
```

```bash
$ cd myproject
$ python mypackage/cli.py
ImportError: attempted relative import with no known parent package

$ python -m mypackage.cli
# works correctly — cli.py has real package context this way
```

**Why `python -m` is often preferable for package-based applications**:
it makes relative imports work correctly, it more reliably reflects
how the code will actually be imported and run once installed as a
real, distributable package, and it avoids a whole class of
`sys.path`-related surprises that come from Python's "add the script's
own directory to `sys.path`" behavior for plain `python file.py`
invocations. As a project grows past a single flat script into a real
package (the subject of this module's very next chapter), `python -m`
becomes the standard way to run it during development.

## 24. Imports and CLI Programs

Connecting directly to Module 1.5's architecture, extended now with
proper multi-file structure:

```
CLI arguments
      ↓
main()                    — defined in the entry-point module (or cli.py)
      ↓
application logic          — imported from a separate, focused module
      ↓
helper modules               — imported by the application-logic module
      ↓
file/data operations           — imported by whichever module actually needs them
```

```python
# validators.py — no CLI knowledge at all
def validate_positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise ValueError(f"must be positive, got {number}")
    return number
```
```python
# cli.py — imports validators.py; owns argparse, main(), and the __main__ guard
import argparse
from validators import validate_positive_int


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=validate_positive_int, default=1)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(f"count = {args.count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Splitting `validators.py` out from `cli.py` this way makes exactly the
kind of clean boundary this whole module is about: `validators.py` can
be imported and unit-tested completely independently of any CLI
concern at all (no `argparse`, no `sys.argv`, no `main()`), and `cli.py`
stays a thin layer whose only job is wiring argparse to the validated,
reusable logic that lives elsewhere — directly extending the "thin CLI
layer" architecture from `06-command-line-arguments-with-argparse.md`'s
§40 and `07-standard-streams-and-exit-codes.md`'s §45, now expressed as
an actual multi-file module boundary rather than just separate
functions inside one file.

## 25. Imports and Testability

The reason this chapter has repeatedly emphasized "importing a module
should not unexpectedly execute the whole application" is, ultimately,
about **testability** — a topic Stage 1's dedicated testing module
covers in full, but whose foundation is laid entirely here, in how
modules are structured.

A test file needs to `import` the code under test — there is no other
way to call a function from a test. If that import, by itself,
triggers real side effects (§10) — a database connection, a file
write, a `main()` call that never checks a `__main__` guard — the test
inherits every one of those side effects, unavoidably, just from the
act of importing, before the test has even started asserting anything.

```python
# GOOD — safe to import for testing
def validate_positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise ValueError(f"must be positive, got {number}")
    return number
```
```python
# test_validators.py — a conceptual sketch of what a test would do,
# without turning this chapter into a testing tutorial
import pytest
from validators import validate_positive_int

def test_rejects_zero():
    with pytest.raises(ValueError):
        validate_positive_int("0")
```

This test can `import validators` freely and repeatedly, in complete
isolation, precisely *because* `validators.py` was designed (§21, §24)
with no module-level side effects and no unguarded entry-point logic.
The dedicated testing chapters in this course will build pytest
knowledge in full; the point to take from this chapter specifically is
architectural: **clean module design is what makes that later testing
work straightforward, rather than something the test suite has to fight
against.**

## 26. Imports and Dependencies

Every `import` statement in a file is a small, explicit declaration:
"this code depends on that." Reading a file's imports is one of the
fastest ways to understand what it actually relies on — which is
exactly why keeping them explicit, minimal, and well-organized (§20)
matters beyond mere style.

Three distinct origins worth telling apart, using imports you've
already used throughout this course:

- **Standard-library modules** — part of Python itself, installed
  wherever Python is installed, requiring no separate installation
  step: `os`, `sys`, `json`, `csv`, `pathlib`, `argparse`, `logging`.
- **Local modules** — files that are part of *your own* project,
  imported by their project-relative name (`import validators`, or
  `from mypackage.utils import helper`).
- **Third-party packages** — code someone else published, that must be
  explicitly installed into your environment before it can be imported
  at all (e.g. `import requests`, `import numpy`) — recognizable in
  code by the fact that they aren't standard library and aren't part
  of your own project's files.

```python
import json               # standard library
import sys                # standard library

import requests            # third-party — must be installed separately

from validators import validate_positive_int   # local — part of this project
```

This chapter deliberately stops here on the *dependency-management*
side of this topic — actually declaring, installing, pinning, and
managing third-party dependencies (via `pyproject.toml`, lock files,
and tools like `uv`) is the dedicated subject of later chapters in
this exact module. What matters here is simpler and foundational: an
import statement is a dependency declaration, and recognizing which of
these three categories any given import belongs to is the first step
toward reasoning about a project's dependencies at all.

## 27. Advanced Import Concepts

**`importlib.import_module()`** lets you import a module using a
**string** naming it, decided at runtime, rather than a hardcoded
`import` statement written into the source code:

```python
import importlib

module_name = "json"    # could come from a config file, a CLI argument, etc.
json_module = importlib.import_module(module_name)

print(json_module.dumps({"key": "value"}))
```

This is a **dynamic import** — genuinely useful when the specific
module to load isn't known until the program is actually running (a
plugin system choosing among several optional modules by name, for
instance) — but it should be treated as a deliberate, occasional tool,
not a default replacement for ordinary `import` statements, which
remain more readable, more easily analyzed by tooling (linters, IDEs),
and simpler to reason about for the overwhelming majority of code.

**`importlib.reload()`** re-executes an *already-imported* module's
top-level code. It does **not** create a new module object or replace the
entry in `sys.modules` (§12): the existing module object is normally
reused, and running the source again updates that same object's
namespace in place (so `importlib.reload(mymodule) is mymodule` is
`True`). It is most commonly encountered in
interactive development (a REPL, or a Jupyter-style notebook) when
you've edited a module's source file and want the running session to
pick up the change without restarting the whole process:

```python
import importlib
import mymodule

# ... edit mymodule.py on disk ...

importlib.reload(mymodule)   # re-executes mymodule's top-level code, updating the same module object
```

**This is explicitly a development/debugging convenience, not a normal
application architecture technique.** Production code should not rely
on `reload()` to pick up changes at runtime — because reload updates
the module's namespace but cannot reach other code that already holds
references to the *old* functions, classes, or objects (for example, anything bound earlier with
`from mymodule import some_function`), a program can end up in an
inconsistent state — some code holding the *old* version of a function
or class, other code holding the *new* one — and a normal
deployment process (restarting the actual process to run updated code)
is the correct, reliable way to apply code changes in any real system.

**`__spec__`**, revisited from §5: the `ModuleSpec` object the import
system itself uses internally to describe where a module came from and
how to load it — occasionally useful for advanced introspection or
tooling, but not something ordinary application code needs to read or
manipulate directly. **Module identity**: because of import caching
(§11–§12), `import module_name` from two different files, in the same
process, yields the *same* underlying object — verifiable directly
with `is` (`sys.modules["math"] is math` is `True`) — a fact worth
knowing mainly because it explains why module-level state (§11's
closing point) is genuinely shared, process-wide, not duplicated per
importer. (The identity is per module *name*: the same source loaded
under a different name, as in the `__main__` case from §11, produces a
separate module object.)

## 28. Debugging Import Problems

**1. `ModuleNotFoundError` for a module you're sure exists**
```
ModuleNotFoundError: No module named 'validators'
```
*Diagnosis:* print `sys.path` and check whether the directory
containing `validators.py` is actually in it. *Root cause:* almost
always, the script is being run from a different working directory
than expected, or `validators.py` lives somewhere `sys.path` doesn't
cover. *Fix:* run the script from the correct directory, restructure
as a proper package and use `python -m` (§23), or (as a last resort,
and only when genuinely necessary) explicitly adjust `sys.path` at the
very top of the entry-point script. *Better design:* organize the
project as a real package from the start (this module's next chapter),
so "where do I run this from" stops being an ambiguous question.

**2. `ImportError: cannot import name 'X' from 'Y'`**
*Diagnosis:* the module `Y` was found and imported successfully, but
`X` doesn't actually exist inside it — check for a typo in the name,
or confirm `X` is genuinely defined in `Y.py` (not, for instance, only
inside a function or class inside it, which wouldn't make it a
module-level name). *Root cause:* commonly a rename that wasn't
updated everywhere, or confusion about a name defined inside a class
versus at module level. *Fix:* correct the name, or add/re-export the
name from `Y` if it's genuinely meant to be part of `Y`'s public API.

**3. Relative import failure**
```
ImportError: attempted relative import with no known parent package
```
*Diagnosis:* this file uses `from .something import X` but was
executed directly (`python mypackage/module.py`), not run with package
context. *Root cause:* §15/§23 — a relative import requires being
imported *as part of a package*, which running a file directly does
not provide. *Fix:* run it with `python -m mypackage.module` instead,
or restructure so the entry point is a separate top-level script that
imports the package normally (absolute import) rather than being a
file *inside* the package that's executed directly.

**4. Circular import**
```text
ImportError: cannot import name 'function_a' from partially initialized module 'a'
(exact wording varies by Python version)
```
*Diagnosis:* trace the actual import chain (§19) — which module
imports which, and in what order, at the point of failure. *Root
cause:* two modules depend on each other directly or through a chain.
*Fix:* extract shared functionality into a third module neither
depends on the other for (§19's preferred solution), rather than
reordering imports or moving them inside functions as a first resort.

**5. Unexpected code execution during import**
A test importing a module for one function also, mysteriously, prints
startup messages or makes a real network call. *Diagnosis:* search the
imported module for module-level statements outside any function or
the `__main__` guard. *Root cause:* §10 — real logic living at module
level instead of inside `main()` (or another function), unguarded.
*Fix:* move that logic into a function, called only from
`if __name__ == "__main__":`.

**6. Wrong Python environment**
A package installs successfully (a bare `pip install somepackage`) but
`import somepackage` still fails inside the actual project.
*Diagnosis:* `print(sys.executable)` and compare it against which
Python/virtual environment the install command actually targeted —
they frequently turn out to be two different interpreters, especially
with multiple virtual environments or a system Python installed
alongside them. *Fix:* activate the correct virtual environment before
both installing and running, install with `python -m pip install ...`
(so the same interpreter is used), and confirm with `sys.executable`
that they now match.

**7. Duplicate module name shadowing a standard-library or third-party
module**
A project has its own file named `json.py` at its top level; suddenly,
`import json` anywhere in that project imports the *local* file
instead of the standard library's `json` module, and standard-library
JSON functions mysteriously stop existing (`AttributeError`).
*Diagnosis:* check `some_module.__file__` — does it point at your own
project file instead of the expected standard-library location?
*Root cause:* because the current script's own directory is placed at
the *front* of `sys.path` (§13, §23), a same-named local file takes
priority over a standard-library or third-party module with the exact
same name. *Fix:* never name a project file identically to a standard-
library or well-known third-party module (`json.py`, `types.py`,
`email.py`, and similarly-named files are the classic examples worth
specifically avoiding).

## 29. Progressive Coding Examples

**1. A simple module**
```python
# greetings.py
def hello():
    print("Hello!")
```

**2. A basic import**
```python
import greetings
greetings.hello()
```

**3. Different import styles**
```python
import greetings as g
from greetings import hello
from greetings import hello as say_hello

g.hello()
hello()
say_hello()
```

**4. Observing module namespace**
```python
import greetings
print(dir(greetings))   # lists names defined in the module, including `hello`
```

**5. `__name__` in action**
```python
# demo.py
print(__name__)
```
```bash
$ python demo.py     # prints: __main__
```
```text
>>> import demo       # prints: demo
```

**6. The `__main__` guard**
```python
def hello():
    print("Hello!")

if __name__ == "__main__":
    hello()
```

**7. The `main()` pattern**
```python
def main() -> None:
    print("Running")

if __name__ == "__main__":
    main()
```

**8. `main()` returning an exit code**
```python
def main() -> int:
    print("Running")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

**9. A file that is both reusable and executable**
```python
def add(a: int, b: int) -> int:
    return a + b

def main() -> int:
    print(add(2, 3))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```
`import this_file; this_file.add(2, 3)` works with zero side effects;
`python this_file.py` prints `5` and exits `0`.

**10. Multiple cooperating modules**
```python
# math_ops.py
def add(a, b): return a + b

# text_ops.py
def shout(text): return text.upper() + "!"

# app.py
from math_ops import add
from text_ops import shout

print(shout(f"sum is {add(2, 3)}"))
```

**11. A package import**
```python
# mypackage/__init__.py   (can be empty)
# mypackage/utils.py
def helper(): return "helping"
```
```python
from mypackage.utils import helper
print(helper())
```

**12. A relative import inside a package**
```python
# mypackage/cli.py
from .utils import helper

def main() -> int:
    print(helper())
    return 0
```
Run correctly with `python -m mypackage.cli` (§23) — running
`python mypackage/cli.py` directly would raise the relative-import
error from §28's scenario 3.

**13. Demonstrating import caching**
```python
# once.py
print("once.py executing")
```
```python
import once
import once   # prints nothing further — already cached (§11)
```

**14. Inspecting `sys.path` while debugging**
```python
import sys
for entry in sys.path:
    print(entry)
```

**15. Avoiding a circular import by extracting shared code**
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
Neither `a.py` nor `b.py` imports the other — the cycle is designed
away entirely, per §19's preferred solution.

**16. A clean CLI project structure (sketch)**
```
myapp/
    validators.py     # pure functions, no CLI/logging/side effects
    processing.py      # business logic, imports validators
    cli.py               # argparse + main() + __main__ guard, imports processing
```
`python -m myapp.cli` becomes the program's single entry point,
importing everything else in a clean, one-directional chain:
`cli.py → processing.py → validators.py`, with no module needing to
import back "up" the chain — exactly the shape §30's mini project
implements in full.

## 30. Mini Project — Reusable CLI Application with Clean Module Boundaries

**Requirements:** a small CLI tool, structured as three cooperating
modules (all shown here as separate code blocks, since this chapter
does not create actual project files — see each block's filename
comment), that reads a list of numbers from the command line, validates
them, computes basic statistics, and prints a result — demonstrating
reusable functions, a clean `main()`, the `__main__` guard, no
import-time side effects, and clear module boundaries.

**Project structure (conceptual):**
```
stats_cli/
    validators.py    # pure validation — no CLI, no I/O, no side effects
    stats.py           # pure business logic — no CLI, no I/O
    cli.py                # argparse + main() + __main__ guard — the only "impure" module
```

**Import relationships:**
```
cli.py
  ├── imports validators.py   (to validate each raw CLI argument)
  └── imports stats.py         (to compute the actual statistics)

validators.py   — imports nothing project-local (no dependency on cli.py or stats.py)
stats.py          — imports nothing project-local (no dependency on cli.py or validators.py)
```

Notice the dependency arrows all point **one direction**, toward
`cli.py` — `validators.py` and `stats.py` know nothing about each
other or about the CLI at all, which is exactly what makes this
structure free of any risk of a circular import (§19): there is no
cycle to even accidentally create, because the lower-level modules
never need to import anything from the layer above them.

**Implementation:**

```python
# validators.py — pure, reusable, side-effect-free
"""Validators for the stats CLI. No CLI or I/O concerns live here."""


def validate_number(raw_value: str) -> float:
    try:
        return float(raw_value)
    except ValueError:
        raise ValueError(f"not a valid number: {raw_value!r}") from None
```

```python
# stats.py — pure business logic, no CLI or I/O concerns
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

```python
# cli.py — the only module that knows about argparse, stdout/stderr, and exit codes
"""CLI entry point for the stats tool."""
import argparse
import json
import sys
from collections.abc import Sequence

from validators import validate_number
from stats import compute_stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute basic statistics for a list of numbers.")
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

**Execution flow** (running `python -m stats_cli.cli 1 2 3`, per
§23's guidance for a package-based tool): `cli.py`'s `__name__` becomes
`"__main__"` → the guard fires → `main(None)` runs → `sys.argv[1:]` is
parsed by argparse into `args.numbers = ["1", "2", "3"]` → each raw
string is validated (and converted to `float`) by
`validators.validate_number` → `stats.compute_stats` computes the
result from already-validated floats → the JSON result is printed to
stdout → `main()` returns `0` → `raise SystemExit(0)` sets the actual
process exit status.

**Import flow**: at the moment `cli.py` is first loaded (whether run
directly or imported), Python executes `from validators import
validate_number` and `from stats import compute_stats` — each of
which, per §3, executes `validators.py`'s and `stats.py`'s own
top-level code exactly once (defining their functions; no side
effects at all, per their design) and caches both modules in
`sys.modules` (§11–§12) — so if anything else in a larger project also
imports `validators` or `stats`, that work isn't repeated.

**Why this design is maintainable:** `validators.py` and `stats.py` can
each be tested completely independently, with plain function calls and
no CLI or argparse involved at all (§25) — a test can call
`compute_stats([1.0, 2.0, 3.0])` directly and assert on the result
dict. Adding a new CLI flag only touches `cli.py`; adding a new
statistic only touches `stats.py`; neither change risks breaking the
other, because neither module depends on the other at all.

**Common mistakes this design avoids**: putting validation logic
directly inline inside `cli.py`'s `main()` (making it untestable
without going through argparse); computing statistics with a bare
`print()` scattered through `stats.py` instead of returning a value
(mixing business logic with output, exactly the anti-pattern
`07-standard-streams-and-exit-codes.md`'s §44 warned against);
`validators.py` importing something from `stats.py` "just because it's
convenient," accidentally introducing a dependency (and a future risk
of a cycle) that was never actually needed.

**Debugging approach**: if `python -m stats_cli.cli 1 2 3` fails with
`ModuleNotFoundError: No module named 'validators'`, the most likely
cause (§28) is that `validators.py` isn't actually inside a package
recognized correctly relative to how the command was invoked — check
`sys.path` and confirm the actual working directory and package
structure match what `python -m stats_cli.cli` expects.

**Production improvements worth naming:** replacing the ad hoc
`print(..., file=sys.stderr)` diagnostics with proper `logging` (per
`08-logging-versus-print.md`); adding a `pyproject.toml` (this module's
upcoming chapter) so `stats_cli` becomes a properly installable
package rather than a directory that has to be run from exactly the
right working directory; adding type hints checked by a static type
checker (a later chapter in this module) across all three files.

## 31. Exercises + Answer Key

**Beginner**

1. Create two tiny modules, each defining a function with the same
   name, and import both into a third file using `import module_name`
   (not `from`). Confirm both functions are callable without
   collision.
2. Write one module and import it four different ways (`import`,
   `import ... as ...`, `from ... import ...`,
   `from ... import ... as ...`), printing the result each way.
3. Add `print(__name__)` to a file, then both run it directly and
   import it from another file, observing the two different printed
   values.
4. List at least three attributes every imported module has, and
   explain what each contains, using a real standard-library module to
   check.

**Intermediate**

5. Take a file with real logic at bare module level (no guard at all)
   and refactor it to use `if __name__ == "__main__":` plus a `main()`
   function, explaining in a comment what importing it now does
   differently.
6. Create a two-module package (with an `__init__.py`) and import a
   function from a submodule two different ways: via an absolute
   import, and via a re-export configured in `__init__.py`.
7. Write a file that uses a relative import and demonstrate both the
   working invocation (`python -m package.module`) and the failing one
   (`python package/module.py` directly), explaining the error.
8. Demonstrate import caching directly: create a module whose
   top-level code prints something, import it twice in the same file,
   and explain in a comment why the message appears only once.
9. Print `sys.path` in a small script and identify (in a comment)
   which entry you believe corresponds to the script's own directory.

**Advanced**

10. Construct a genuine circular import between two files, observe the
    exact error, then fix it using the "extract shared logic" pattern
    from §19, and explain why that fix — rather than reordering
    imports — is the better long-term design.
11. Design (with actual code, across multiple code blocks) a
    three-module CLI structure with one-directional dependencies (no
    module importing "upward"), and explain how you'd add a new
    feature without risking a cycle.
12. Take a module with an import-time side effect (a `print()` or a
    simulated "connection" call at bare module level) and explain,
    concretely, what would go wrong if a test suite imported it —
    then fix it.
13. Explain, in your own words, why `python -m package.module` is
    generally preferable to `python package/module.py` once a project
    has more than one file organized as a real package.
14. Design a small module intended to be both reusable and executable,
    including a `main() -> int` and `raise SystemExit(main())`, and
    explain why this shape is preferable to a `main()` that returns
    nothing.

**Answer key**

1. Both functions remain independently accessible as
   `module_one.function_name` and `module_two.function_name` — each
   module's own namespace (§4) keeps them from colliding, which would
   not be true with `from module import *` from both.
2. All four print the same underlying value/behavior; the difference
   is purely in what name(s) become available and how they're accessed
   (§2's table) — none of the four forms changes what the module
   itself actually does.
3. Run directly: `__main__`. Imported: the module's own name (e.g.
   `demo`) — this is precisely §6's core mechanism, and the reason
   `if __name__ == "__main__":` works at all.
4. Any three of `__name__`, `__file__`, `__doc__`, `__package__`,
   `__spec__` (§5) — e.g., `import math; print(math.__name__,
   math.__file__, math.__doc__)`.
5. The refactored version should move all real logic into `main()`
   (or other functions), with only definitions left at bare module
   level; the comment should note that importing it now runs *no*
   logic at all — only defines functions — whereas the original would
   have executed its logic immediately on import (§10).
6. The absolute-import version: `from package.submodule import
   function_name`; the re-export version requires
   `from .submodule import function_name` inside `__init__.py`,
   enabling `from package import function_name` directly (§17).
7. `python -m package.module` should succeed; `python package/module.py`
   should raise `ImportError: attempted relative import with no known
   parent package`, because running the file directly gives it no
   package context for the relative import to resolve against (§15,
   §23, §28 scenario 3).
8. The message should print exactly once, even with two `import`
   statements — the comment should reference `sys.modules` (§11–§12):
   the second `import` finds the module already cached and reuses the
   existing module object without re-executing its top-level code.
9. Typically the first entry (often an empty string `''`, representing
   the current working directory, or the script's own directory,
   depending on invocation) — the exact entry and its meaning should
   be explained by referencing §13 and confirmed by testing where the
   script actually is relative to that path.
10. The error should resemble
    `ImportError: cannot import name '...' from partially initialized
    module '...'` (exact wording varies by Python version) — which
    requires each file to use `from other import name` at the top, as
    in §19's example (§19, §28 scenario 4); the fix should introduce a
    third `shared.py` module neither original file needs to import the
    other for; the explanation should note that reordering imports
    only delays the problem or makes it fragile to future changes,
    while extracting shared logic removes the actual mutual dependency
    that caused it.
11. A reasonable structure mirrors §30's `validators.py` → `stats.py`
    → `cli.py` example (or similar); the explanation should identify
    that a new feature belongs in the *lowest* layer that doesn't
    already need to depend on something *above* it, keeping the
    dependency graph acyclic by construction.
12. The side effect (e.g. a `print()` or simulated database connection
    at bare module level) would fire the moment a test does
    `import module_under_test`, even if the test only wants to check
    one small function — polluting test output, or, worse, requiring
    a real dependency (a database) to be available just to run an
    otherwise-simple unit test (§10, §25). The fix moves that logic
    into a function, called only from behind `if __name__ ==
    "__main__":`.
13. `python -m` uses the real import system (so relative imports and
    `__package__` work correctly, §15, §23) and better reflects how the
    code will behave once it's actually installed and imported as a
    package elsewhere, whereas `python file.py` treats the file as a
    standalone script with no real package context, regardless of
    which directory it happens to live in.
14. `main() -> int` (rather than `main()` returning nothing) lets the
    function's success/failure be expressed as an ordinary return
    value, testable directly (`assert main([...]) == 0`) with no
    process involved; `raise SystemExit(main())` is the one place that
    turns that value into the process's actual exit status, keeping
    the translation from "what happened" to "how the process ends"
    isolated to a single line (§9).

## 32. Debugging Lab

**1. `ModuleNotFoundError` despite the file existing**
```
$ python cli.py
ModuleNotFoundError: No module named 'validators'
```
*Diagnosis:* `print(sys.path)` at the top of `cli.py` and confirm
whether `validators.py`'s directory is actually listed. *Root cause:*
the script was run from a different working directory than
`validators.py` lives in, and nothing adds that directory to
`sys.path`. *Fix:* run from the correct directory, or restructure as a
package and use `python -m` (§23, §28 scenario 1).

**2. `ImportError: cannot import name`**
```python
from stats import compute_statistics   # actual function is named compute_stats
```
*Diagnosis:* open `stats.py` and check the actual defined name.
*Root cause:* a typo, or a rename in `stats.py` that wasn't reflected
in every importer. *Fix:* correct the imported name to
`compute_stats` (§28 scenario 2).

**3. Relative import failure**
```python
# mypackage/cli.py
from .utils import helper
```
```bash
$ python mypackage/cli.py
ImportError: attempted relative import with no known parent package
```
*Diagnosis:* this file is being executed directly, not run with
package context. *Root cause:* §15/§23 — running a file inside a
package directly leaves its `__package__` as `None`, so there is no
package for the relative import to resolve against. *Fix:* `python -m mypackage.cli`.

**4. Circular import**
```python
# orders.py
from customers import get_customer_name

# customers.py
from orders import get_order_total
```
*Diagnosis:* trace which module's top-level code is executing when the
error fires; identify that each imports the other. *Root cause:*
genuine mutual dependency at the module level (§19). *Fix:* extract
`get_customer_name`'s and `get_order_total`'s genuinely shared
dependencies (if any) into a third module, or reconsider whether
`orders.py` needs the *whole* of `customers.py` or just one small piece
that could live elsewhere.

**5. Unexpected code execution during import**
```python
# reporting.py
print("Generating report...")
report = build_report()   # runs immediately at import time
```
```python
import reporting   # "Generating report..." prints immediately — surprising for a "utility" import
```
*Diagnosis:* look for statements outside any function definition and
outside a `__main__` guard. *Root cause:* §10 — real logic sitting at
bare module level. *Fix:* move it into a function, called only from
`if __name__ == "__main__":`.

**6. Incorrect `sys.path` assumption**
A script assumes its own directory is always in `sys.path`, and works
fine when run as `python app.py` but fails with `ModuleNotFoundError`
when run as `python -m app` from a different parent directory.
*Diagnosis:* print `sys.path` under both invocation styles and compare.
*Root cause:* the two invocation styles populate `sys.path`'s first
entry differently (§13, §23) — assuming one specific behavior without
checking it directly is fragile. *Fix:* don't rely on an assumed
`sys.path` entry; restructure the project as a proper package with
explicit imports that don't depend on this ambiguity.

**7. Wrong environment**
```bash
$ pip install requests        # a bare `pip` may belong to a different Python
$ python app.py
ModuleNotFoundError: No module named 'requests'
```
*Diagnosis:* `print(sys.executable)` inside `app.py`, and compare it
against which Python `pip` actually installed into (`pip --version`
shows this, and `python -m pip --version` is the form tied to the
interpreter you intend to run). *Root cause:* `pip install` and `python app.py`
used two different Python installations/virtual environments. *Fix:*
activate the same virtual environment for both the install and the run,
or install with `python -m pip install requests` so the same
interpreter is used for both (§28 scenario 6).

**8. Duplicate module name**
A project has its own `email.py` at the top level; `import email`
anywhere in the project (including inside the standard library itself,
transitively) now imports the *local* file instead of the standard
library's `email` package, causing confusing, unrelated
`AttributeError`s.
*Diagnosis:* check `email.__file__` — does it point to the project's
own file rather than a standard-library location? *Root cause:* the
current script's own directory is searched before standard-library
locations (§13, §28 scenario 7). *Fix:* rename the local file to
something that doesn't collide with a standard-library (or common
third-party) module name.

## 33. Interview + Architecture Questions

1. What is a Python module, and how does it differ from "just a file"?
2. What actually happens, step by step, when Python executes an
   `import` statement?
3. Why is "importing copies the code into the current file" an
   incorrect mental model?
4. What is a namespace, and how does a module provide one?
5. What is `__name__`, and what values can it hold?
6. What is `__main__`, and how does it differ between
   `python file.py` and `python -m package.module`?
7. Why does `if __name__ == "__main__":` exist, and what specific
   problem does it solve?
8. Why is `main() -> int` combined with `raise SystemExit(main())`
   preferable to a bare `main()` with no return value?
9. What is import caching, and what role does `sys.modules` play in
   it?
10. What is `sys.path`, and how does Python use it during an import?
11. What's the difference between `ModuleNotFoundError` and the more
    general `ImportError`?
12. What is the difference between an absolute import and a relative
    import? When does a relative import fail?
13. What does `__init__.py` do, and why might it be empty?
14. Why is `from module import *` generally discouraged? What does
    `__all__` control?
15. What is a circular import, and why does it typically produce an
    error about a "partially initialized module"?
16. Name at least two design-level (not hacky) ways to resolve a
    circular import.
17. What is an import-time side effect, and why is it dangerous?
18. What's the practical difference between `python file.py` and
    `python -m package.module`?
19. Why does clean module design make code easier to test?
20. What's the difference between a standard-library import, a local
    import, and a third-party import?
21. What does `importlib.import_module()` do, and when is it
    appropriate to use instead of a normal `import` statement?
22. Why is `importlib.reload()` considered a development tool rather
    than a production technique?

**Answer key**

1. A module is a named unit of Python code managed by the import
   system; a `.py` file is the most common way to define one. The term
   specifically signals that the file is designed to be imported and
   reused by other code — the distinction is one of intent and design,
   not a different file type (§1).
2. Python checks `sys.modules` first; if not cached, the import system
   finds the module (e.g. via `sys.path`), creates the module object,
   places it in `sys.modules` *before* running any of its code, then
   executes the module's top-level code once; if that succeeds, the
   import completes and the requested name is bound in the importing
   code's own namespace (§3).
3. Because importing genuinely *executes* the module's code (once,
   with real side effects if any exist) and produces a distinct module
   object with its own namespace — it is not textual substitution, and
   two modules with a same-named function never collide the way a
   literal copy-paste would risk (§3–§4).
4. A namespace is a mapping from names to objects; a module provides
   one by holding every name it defines as an attribute of its own
   module object, accessed via `module.name`, keeping it separate from
   every other module's own names (§4).
5. `__name__` holds either the module's own dotted name (if imported)
   or the special string `"__main__"` (if that file was the one
   actually executed, directly or via `-m`) (§6).
6. `__main__` is the name Python gives to whichever module was
   actually run as the program's entry point; `python file.py` sets
   `file.py`'s `__name__` to `"__main__"` with no package context,
   while `python -m package.module` locates the module through the
   real import system first and then runs it as `__main__`, giving it
   genuine package context (§7, §23).
7. It exists to let one file serve as both a reusable module (safe to
   import, no side effects) and an executable script (does something
   useful when run directly), by checking, at runtime, whether this
   specific file was the one launched (§8).
8. Because it separates "what happened" (an ordinary, testable return
   value) from "how the process ends" (one line, translating that value
   into an actual OS exit status), making `main()` callable and
   assertable directly in tests without risking early process
   termination (§9).
9. Import caching means that, under normal imports, a module's
   top-level code runs only once per process (`importlib.reload()`
   re-runs it explicitly); `sys.modules` is the actual dictionary Python
   checks first (before searching/loading) and stores the result in,
   which is what makes repeated imports of the same module cheap and
   consistent (§11–§12).
10. `sys.path` is the ordered list of locations Python searches when
    looking for a module to import; Python checks each entry in order
    until it finds a match or exhausts the list, at which point a
    `ModuleNotFoundError` is raised (§13).
11. `ModuleNotFoundError` (a subclass of `ImportError`) means the named
    module itself was never found anywhere in `sys.path`;
    `ImportError` more generally also covers cases where the module
    *was* found, but a specific name from it doesn't exist, or its own
    code raised an exception while executing (§14).
12. An absolute import spells out a module's full path from the top of
    its package (`from mypackage.utils import helper`); a relative
    import (`from .utils import helper`) is expressed relative to the
    importing module's own position in a package, and fails with "no
    known parent package" if that file has no real package context —
    most commonly because it was executed directly rather than run via
    `-m` or imported normally (§15, §23).
13. `__init__.py` marks a directory as a regular importable package
    (namespace packages can exist without it) and runs once, the first
    time anything inside that package is imported;
    it's often empty because marking the directory as a package is
    sufficient on its own — re-exporting names to shorten import paths
    is a deliberate, optional choice, not a requirement (§17).
14. It's discouraged because it pulls every public name from a module
    directly into the current namespace with no prefix, risking silent
    name collisions and making it impossible to tell, from the call
    site alone, where a given name came from; `__all__`, if defined,
    limits exactly which names a wildcard import actually pulls in
    (§18).
15. A circular import happens when two modules depend on each other,
    directly or through a chain; the "partially initialized module"
    error occurs because Python, encountering the second module's
    attempt to import back from the first, finds the first module
    already present in `sys.modules` but not yet fully executed —
    meaning not every name it will eventually define exists on it yet
    (§19).
16. Any two of: extracting the shared functionality into a third,
    lower-level module neither original module needs to import the
    other for; merging the two modules if they're genuinely one unit;
    reconsidering which module actually needs to depend on the other,
    and in which direction (§19) — deferred/local imports inside a
    function are a narrower, last-resort technique, not a primary
    design solution.
17. An import-time side effect is any real action (I/O, a network
    call, printing, mutating shared state) that happens merely from
    importing a module, rather than from calling one of its functions;
    it's dangerous because it makes importing unpredictable, expensive,
    order-dependent, and hard to test in isolation (§10, §25).
18. `python file.py` runs a file as a standalone script with no real
    package context (relative imports fail inside it); `python -m
    package.module` uses the actual import system to locate and run
    the module, giving it correct package context, including working
    relative imports (§23).
19. Because a module that can be imported with zero unwanted side
    effects can also be imported by a test in complete isolation, with
    no need to work around database connections, network calls, or
    unguarded startup logic just to test one small function (§25).
20. A standard-library import comes from Python itself, needing no
    separate installation; a local import refers to a file that's part
    of your own project; a third-party import refers to externally
    published code that must be explicitly installed into the current
    environment before it can be imported (§26).
21. It imports a module using a string name decided at runtime rather
    than a hardcoded `import` statement — appropriate for genuinely
    dynamic scenarios (e.g. a plugin system choosing among modules by
    name), but not a default replacement for ordinary, statically
    readable `import` statements (§27).
22. Because `reload()` re-executes the module's code into the same module
    object, other code that already holds references to its old
    functions/classes (e.g. from `from module import name`) keeps the
    old versions, leaving the program in an inconsistent state, and because a real deployment simply restarts
    the process to run updated code reliably — `reload()` is a
    convenience for interactive development sessions, not a technique
    a running production system should depend on (§27).

## 34. Knowledge Check

**Conceptual**
1. In your own words, why is a namespace the mechanism that lets two
   modules each define a function with the same name with no conflict?
2. Why does Python execute a module's top-level code at import time,
   rather than only when something from it is actually used?

**Code-reading**
3. What does this print, and why, both when run directly and when
   imported?
```python
# mystery.py
print(f"Loading: {__name__}")

def run():
    print("Running")

if __name__ == "__main__":
    run()
```
4. What's wrong with this import, specifically?
```python
from json import dumps
from custom_json import dumps
print(dumps({"a": 1}))
```

**Output-prediction**
5. Given `once.py` containing only `print("side effect")`, what is
   printed by the following, and why?
```python
import once
import once
import once
```

**Debugging**
6. A colleague's package works when run as `python -m mypackage.cli`
   but fails with a relative-import error when they instead run
   `python mypackage/cli.py`. What's the single-sentence explanation?

**Design**
7. You're asked to add a `main()` function and `__main__` guard to a
   file that currently has real logic (a file write) directly at
   module level, with no functions at all. Describe the two things you
   would change.
8. Design (in words, not full code) a three-file structure for a small
   CLI that avoids any risk of a circular import between its files.

---

**Answer key**

1. Because each module has its own, separate namespace — a name
   defined inside one module's namespace is accessed only through that
   module's own name (`module.name`), so two same-named functions in
   different modules simply never occupy the same slot at all (§4).
2. Because executing the top-level code *is* how the module object gets
   populated — defining functions and classes, and creating
   module-level variables, are all things that only happen by actually
   running that code once; there's no other
   mechanism by which those names could come to exist (§3).
3. Run directly: prints `Loading: __main__`, then (because the guard
   matches) `Running`. Imported (as `import mystery`): prints
   `Loading: mystery`, and does **not** print `Running`, because
   `__name__` is `"mystery"`, not `"__main__"`, so the guard's
   condition is false (§6, §8).
4. The second import silently shadows the first — any call to
   `dumps(...)` afterward uses `custom_json.dumps`, not `json.dumps`,
   with no error or warning; the fix is to keep both accessible
   explicitly, e.g. `import json` and `import custom_json`, or alias
   one of them (`from custom_json import dumps as custom_dumps`) (§2).
5. Only `"side effect"` once — the first `import once` executes the
   module's top-level code and caches the resulting module object in
   `sys.modules`; the second and third `import once` statements find it
   already cached and simply reuse that object, with no re-execution
   (§11–§12).
6. Running the file directly gives it no package context at all
   (`__package__` is `None`), so a relative import inside it has nothing to
   resolve `.` or `..` against, whereas `python -m` locates it through
   the real import system, which does establish that context (§15,
   §23).
7. Wrap the file-write logic in a function (e.g. `main()`), and add
   `if __name__ == "__main__": raise SystemExit(main())` at the bottom
   — this removes the unconditional side effect from bare module level
   entirely, so importing the file no longer triggers the file write;
   it only happens when the file is run directly (§10, §21).
8. A reasonable design: a bottom layer with pure, dependency-free logic
   (e.g. `validators.py`), a middle layer that imports only from the
   bottom layer (e.g. `processing.py`), and a top `cli.py` that imports
   from both but is never imported *by* either — every dependency arrow
   points strictly "upward" toward `cli.py`, and no lower layer ever
   needs to import from a higher one, so a cycle has no way to form
   (§19, §30).

## 35. Production Checklist

**Module boundaries**
- [ ] Each module has one clear responsibility; unrelated logic isn't
      crammed into a single file "for convenience."
- [ ] Dependencies between modules flow in one direction — no module
      needs to import "upward" toward something that depends on it.

**Imports**
- [ ] Every import is explicit (`import module` or
      `from module import specific_name`) — no wildcard imports.
- [ ] Imports are grouped (standard library, third-party, local) and
      placed at the top of the file.
- [ ] Every import is actually used; no leftover, unused imports.
- [ ] No local file shadows a standard-library or well-known
      third-party module name.

**Import-time behavior**
- [ ] No real side effects (I/O, network calls, printing, mutating
      shared state) happen at bare module level.
- [ ] All meaningful logic lives inside functions, called explicitly —
      never triggered merely by importing the file.
- [ ] No circular dependencies exist between modules; if two modules
      seem to need each other, shared logic has been extracted into a
      third module instead.

**Entry point**
- [ ] Every executable script has a `main()` function, not bare logic
      directly under the `__main__` guard.
- [ ] `main()` returns an `int` status; the guard uses
      `raise SystemExit(main())`, not a bare `main()` call.
- [ ] The `if __name__ == "__main__":` guard is present on every file
      meant to be both reusable and executable.

**Package structure and invocation**
- [ ] Package-based projects are run with `python -m package.module`
      where relative imports or package context are needed, not a bare
      `python package/module.py`.
- [ ] `__init__.py` is present where a directory is meant to be a
      regular package, and contains only deliberate re-exports (or nothing) —
      not substantial, side-effect-bearing logic.

**Testability**
- [ ] Business logic can be imported and unit-tested with no CLI,
      argparse, or process-level concerns involved at all.
- [ ] Importing any module for testing never triggers a real database
      connection, network call, or file write as a side effect.

**Debugging readiness**
- [ ] `sys.path` and `sys.executable` are the first things checked
      when an import fails unexpectedly — not guessed at.
- [ ] `ModuleNotFoundError` vs. `ImportError` is used to narrow the
      diagnosis (module not found at all, vs. found but a specific
      name is missing) before investigating further.
