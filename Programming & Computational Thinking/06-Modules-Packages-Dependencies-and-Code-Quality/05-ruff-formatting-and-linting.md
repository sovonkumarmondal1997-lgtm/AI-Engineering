# Ruff, Formatting, and Linting

## Learning Objectives

By the end of this chapter you will be able to:

- Explain what code quality means, and identify formatting problems,
  style problems, and correctness-related problems as distinct
  categories.
- Explain what a code formatter and a linter each are, how they
  differ, and how both differ from a type checker and a test
  framework.
- Explain what Ruff is, what problem it solves, and what it does
  *not* replace (tests, type checkers, security review, architectural
  judgment).
- Install Ruff as a project development dependency with `uv`, and use
  its core commands: `ruff check`, `ruff format`, `ruff check --fix`,
  and `ruff format --check`.
- Read and reason about Ruff's rule system: rule codes, rule families
  (`F`, `E`/`W`, `UP`, `B`, `SIM`, `I`, `N`, `A`, `C4`, `PIE`, `RUF`),
  selection, and ignoring.
- Diagnose and fix common lint problems: unused imports, unused
  variables, undefined names, and outdated syntax patterns.
- Use `ruff check --fix` safely, understanding the difference between
  safe, mechanical fixes and changes that deserve manual review.
- Configure Ruff in `pyproject.toml`, including `line-length`,
  `target-version`, `exclude`/`extend-exclude`,
  `lint.select`/`lint.ignore`/`lint.extend-select`/
  `lint.extend-ignore`, `lint.per-file-ignores`, and
  `format.quote-style`/`format.indent-style`/`format.line-ending`.
- Use inline suppression (`# noqa`, rule-specific `# noqa: CODE`)
  judiciously, and per-file ignores for legitimate exceptions (tests,
  `__init__.py`, generated code).
- Integrate Ruff into an editor, `pre-commit`, and a CI/CD pipeline,
  and explain why CI must independently verify what a developer's
  local tooling claims.
- Explain how Ruff's exit codes connect to shell automation and CI
  gating, extending this course's earlier standard-streams/exit-code
  chapter.
- Distinguish formatting, linting, type checking, and testing as
  complementary, non-overlapping layers of quality assurance.
- Reason about false positives, rule-suppression discipline, and
  gradual, low-friction Ruff adoption in a legacy codebase.
- Design a sensible Ruff configuration for a small project and for a
  larger, production-oriented one, understanding the tradeoffs
  involved.

## 1. Why Code Quality Matters

Before introducing any tool, look directly at the problem the rest of
this chapter exists to solve.

```python
import os
import sys

def calculate(x,y):
    unused_variable = 10
    return x+y
```

A careful human reader, given enough time, could find several
problems here — but notice how many genuinely *different kinds* of
problems are tangled together in four short lines:

- **`import os`** is never used anywhere in this file — a **dead
  import**.
- **`def calculate(x,y):`** has no space after the comma — a
  **formatting** inconsistency.
- **`unused_variable = 10`** is assigned and never read — **dead
  code**.
- **`return x+y`** has no spaces around `+` — another **formatting**
  inconsistency, distinct from the comma issue above.
- **`import sys`** is also never used — a second dead import,
  potentially easy to miss once you've already spotted the first one.

**Code quality** is the general term for how easy a codebase is to
read, trust, change safely, and reason about — as distinct from
whether it simply *runs*. Code that works can still be low quality:
this four-line snippet runs without error, computes the right answer,
and yet already carries several problems that will make it harder to
maintain than it needs to be.

**What makes Python code difficult to maintain**, in general: **dead
code** (logic or variables that are never actually used, silently
wasting a reader's attention trying to understand why they're there);
**unused imports** (importing something and never using it, which
misleads a reader into thinking the module depends on something it
doesn't); **undefined names** (referencing a variable or function that
was never actually defined — usually a typo, and a real, immediate
bug, not just a style issue); **suspicious constructs** (code that is
syntactically valid but almost certainly not what the author meant —
comparing with `==` where `is` was intended, a mutable default
argument, an unreachable branch after a `return`); **style
inconsistencies** (some functions using single quotes, others double;
inconsistent spacing; inconsistent line lengths) that make a codebase
feel unpredictable to read, even when every individual piece is
correct; and **maintainability problems** more broadly — code that's
technically correct today but structured in a way that makes tomorrow's
change riskier than it needs to be.

**Distinguishing the categories precisely**, since this chapter
returns to this distinction constantly:

| Category | Example from the snippet | What kind of problem |
|---|---|---|
| Formatting problem | `def calculate(x,y):` (missing space) | Purely cosmetic — doesn't change what the code does |
| Style problem | mixing single and double quotes across a file | Cosmetic, but at the *project* level rather than one line |
| Correctness-related problem | a genuinely undefined name | An actual bug, not just untidiness |
| Maintainability problem | `unused_variable = 10` | Not a bug today, but wastes future readers' attention and hides intent |

**Why humans cannot reliably review every small style problem, every
time, on every line, in every pull request**: it's tedious, easy to
overlook amid reviewing the *actual logic* of a change (which is what
a human reviewer's attention is genuinely valuable for), and
inconsistent between reviewers — one person's "please add a space
here" is invisible to another. **This is exactly why automated
tooling exists**: a formatter and a linter can check *every* line, of
*every* file, *every* time, with zero fatigue and perfect consistency
— freeing human reviewers to spend their limited attention on the
things only a human can actually judge (is this the right approach,
does this logic make sense, is this the right abstraction). Every
section that follows is about two specific tools that automate exactly
this — a **formatter** (§2–§3) and a **linter** (§4) — and, starting
in §6, one modern tool (**Ruff**) that provides both at once.

## 2. What Is Code Formatting?

**Formatting** is the visual, textual arrangement of code — spacing,
indentation, line breaks, quote style — that has **no effect on what
the code actually does**, only on how it looks to a human reading it.

In Python specifically, **indentation is not purely cosmetic** — it is
syntactically meaningful, defining which statements belong to which
block. This makes Python somewhat unusual: get indentation *wrong*
(inconsistent tabs/spaces, an incorrectly indented line) and the code
may fail to run at all, or run with a different meaning than intended.
Everything else this section covers — spacing, blank lines, quote
style, trailing commas — is **not** syntactically meaningful in the
same way; it can vary freely without changing behavior at all, which
is exactly why it's worth automating rather than debating.

**What formatting covers, concretely:**

- **Consistent spacing** — `x+y` versus `x + y`; `def f(x,y):` versus
  `def f(x, y):`.
- **Blank lines** — how many blank lines separate top-level functions,
  or statements within a function.
- **Line length** — how long a single line of code is allowed to
  become before it should wrap onto multiple lines.
- **Quotes** — single (`'text'`) versus double (`"text"`) — Python
  accepts both interchangeably; a formatter picks one consistently.
- **Trailing commas** — whether the last item in a multi-line list/
  call includes a comma after it (useful for cleaner diffs when adding
  a new item later).
- **Parentheses, function definitions, imports, multi-line
  expressions, dictionaries, lists, function calls, class
  definitions** — each has its own set of formatting conventions
  (how to wrap a long function signature across multiple lines; how to
  lay out a long dictionary literal) that a formatter applies
  consistently, everywhere, without a human needing to decide it fresh
  each time.

**Code that works vs. code that is readable vs. code that follows a
consistent format** — three genuinely different properties:

**Before:**
```python
def calculate_total(items):
    total=0
    for item in items:
        total+=item["price"]
    return total
```

**After:**
```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item["price"]
    return total
```

Both versions **work identically** — they compute the exact same
result for the exact same input. The "after" version is more
**readable** specifically because spacing around `=` and `+=` gives
the eye natural resting points, matching a convention every
experienced Python reader already expects. And because that spacing
convention is applied the *same way*, everywhere, by a tool rather than
by individual habit, the codebase also gains **consistency** — a
property that only exists at the level of the whole project, not any
one function in isolation.

**Why automatic formatting is useful**: once a formatting convention
exists, applying it by hand, consistently, across every file, forever,
is exactly the kind of repetitive, error-prone, attention-draining task
§1 argued automation is suited for — and it removes an entire category
of unproductive disagreement from code review (nobody needs to debate
spacing style in a pull-request comment if a tool already enforces one
answer, automatically, before the review even happens).

## 3. What Is a Formatter?

A **formatter** is a program that reads source code and rewrites it
into a canonical, consistent layout — without changing what the code
*does*.

**Automatic** — it runs without a human deciding, line by line, how
each piece should be laid out; you invoke it, and it makes every
formatting decision itself, according to its own rules. **Deterministic**
— given the exact same input, a formatter always produces the exact
same output, every single time, on any machine — there's no
randomness or "mood" to a formatter's decisions. **Opinionated** — a
modern formatter typically offers few (or no) configurable style
choices; rather than letting every project invent its own bespoke
spacing rules, it enforces one, carefully chosen convention, precisely
so that formatting stops being something individual projects (or
individual developers within a project) need to debate at all.
**Idempotent** — running a formatter on already-formatted code changes
nothing; formatting is a one-way operation that reaches a stable
"fixed point," not a repeated transformation that keeps shifting code
around indefinitely.

**The conceptual pipeline a formatter follows:**
```
Python source code
        ↓
Formatter PARSES the code (understanding its actual structure)
        ↓
Formatting decisions (spacing, line breaks, quote style, ...)
        ↓
Reformatted source code (same meaning, consistent layout)
```

**Why a formatter needs to understand Python's syntax, rather than
simply manipulating text** (e.g., a find-and-replace script) is the
single most important internal-mechanics idea in this section. A
naive text-replacement approach — "replace `x+y` with `x + y`
everywhere" — would break the instant it encountered `x+y` inside a
string literal (where it must **not** be touched, since it's data, not
code) or a more complex expression it wasn't specifically anticipating.
A real formatter instead **parses** the code into a structured
representation of its actual grammar — conceptually, an **Abstract
Syntax Tree (AST)**, a tree data structure representing "this is a
function definition, containing this expression, which is a binary
operation between these two names" — and then decides how to *render*
that structured tree back into text, using its own consistent rules.
Because it operates on the code's actual *meaning* (its parsed
structure), rather than blindly pattern-matching text, it can
correctly leave a string literal's contents completely untouched while
still reformatting the surrounding code with full confidence that it
hasn't changed what anything actually *does*. This chapter does not go
further into compiler/parsing theory than this — the practical
takeaway is simply: **a formatter is syntax-aware, not text-aware**,
and that's precisely what makes it safe to run automatically, on
every file, without manual review of each individual change.

## 4. What Is Linting?

A **linter** is a program that analyzes source code to find problems —
without actually running the program. The term comes from an old Unix
tool called `lint`, originally built to find suspicious constructs in
C code; the name stuck, and "linting" now broadly means "automated
source-code analysis looking for problems," regardless of language.

**What problems can a linter detect?** Things a formatter has no
concept of at all, because they're about *meaning*, not layout:
unused imports, unused variables, references to names that were never
defined, unreachable code after a `return` statement, and a wide range
of other suspicious-but-syntactically-valid constructs.

**A lint rule** is one specific check the linter knows how to perform
(e.g., "flag any imported name that's never used anywhere in this
file"). **A lint violation** is one specific place in the code where
that rule's condition was actually triggered. A **diagnostic** is the
message the linter produces describing a violation — typically naming
the rule, the location (file and line), and a short explanation.

```python
import os

def greet(name):
    unused = 10
    return "Hello " + name
```

A linter examining this file would conceptually report:

- `import os` is never used anywhere in the file — an **unused
  import** violation.
- `unused = 10` is assigned but never read — an **unused variable**
  violation.

Neither of these is a **syntax error** — the code runs perfectly
fine, producing `"Hello Alice"` for `greet("Alice")`, exactly as
intended. Both are, instead, signals that something in the code
doesn't match what a careful author would actually write — the
unused import suggests either a forgotten cleanup or a genuine mistake
(did you mean to use `os` for something?); the unused variable
suggests either dead logic or a typo (was `unused` meant to be used
somewhere, and a later line changed without updating this one?).

**Warning vs. error, as concepts** (the exact terminology and default
severity for any specific rule is tool-specific, and this chapter
avoids overclaiming Ruff's own severity model beyond what §9
establishes): broadly, a **warning**-level diagnostic flags something
worth a human's attention but not necessarily "broken"; an **error**-
level diagnostic flags something more likely to represent an actual
bug (an undefined name that would crash at runtime the moment that
line executes, for instance).

**Linting is static analysis** — it examines source code as *text and
structure*, without ever executing it. This is a crucial, defining
property: a linter can find "this variable is never used" by reading
the code's structure alone; it cannot find "this function returns the
wrong value for input X" without actually running the function against
that input — that kind of problem is exactly what **testing** (§31)
exists for, a fundamentally different kind of quality check this
chapter is careful never to conflate with linting.

## 5. Formatter vs. Linter vs. Type Checker vs. Tests

This distinction is the single most important one in this entire
chapter — every later section depends on keeping these four
genuinely different tools straight.

| | **Formatter** | **Linter** | **Type checker** | **Test framework** |
|---|---|---|---|---|
| **Purpose** | Consistent code layout | Find suspicious/problematic patterns | Verify type consistency | Verify actual behavior |
| **What it analyzes** | Syntax structure, for layout only | Syntax structure and simple patterns | Declared/inferred types across the codebase | The program's actual runtime behavior |
| **What it changes** | Rewrites code layout (never behavior) | Nothing, by default (some violations offer fixes, §11) | Nothing — reports only | Nothing — reports only |
| **Typical output** | Reformatted source files | A list of diagnostics (rule + location + message) | A list of type errors | Pass/fail per test, with failure details |
| **Example tool** | Ruff's formatter | Ruff's linter | mypy, Pyright (not covered in depth here) | pytest |
| **Limitations** | Says nothing about correctness or logic | Cannot verify actual runtime behavior; some checks are inherently pattern-based, not semantic | Cannot catch every logic error; only catches what's expressible as a type mismatch | Only catches what's actually exercised by a written test |

**Formatting ≠ linting**: a perfectly formatted file can still contain
an unused import or an undefined name — layout and correctness-
adjacent analysis are unrelated concerns. **Linting ≠ type checking**:
a linter (as this chapter's Ruff coverage focuses on it) generally
does not perform deep type inference across a whole codebase to verify
that a function is always called with arguments of the correct type —
that is a type checker's specific, more involved job (§32 draws this
line precisely). **Linting ≠ testing**: a linter can flag "this
variable is never used"; it cannot tell you "this function computes
the wrong average" — only running the function against known inputs
and checking the output (a test) can establish that (§31 works through
a concrete example).

**A realistic development pipeline**, showing how these tools
complement, rather than duplicate, each other:

```
formatter          (consistent layout — no logic checked)
    ↓
linter               (suspicious patterns, dead code, style rules)
    ↓
type checker           (type consistency across the codebase)
    ↓
tests                     (actual behavior, verified against expectations)
    ↓
build
    ↓
CI/CD
```

Each stage catches a category of problem the stages before it
structurally cannot — this is why real Python projects run *all* of
these together, not just one, and why the rest of this chapter,
introducing Ruff specifically, is careful to keep saying exactly which
one or two of these five roles Ruff actually fills (formatter and
linter — never type checker, never test framework).

## 6. What Is Ruff?

**Ruff** is a modern Python tool that provides **both** a linter and a
formatter in a single program — replacing what has historically
required several separate tools (a formatter, plus a linter, plus
often several linter *plugins* each providing one specific category of
extra checks) used together.

**What problem does Ruff solve?** Before tools like Ruff existed, a
typical Python project might run a formatter and a separate linter
(potentially with several plugins, each its own installed dependency,
each with its own configuration section) as distinct steps, each with
its own startup time, its own configuration file or section, and its
own version to keep updated. Ruff consolidates a large portion of that
functionality into one fast, single tool with one configuration
location (`pyproject.toml`, §15).

**Why is Ruff popular in modern Python projects?** Primarily for two
reasons: **speed** — Ruff is implemented for high performance and
runs noticeably fast even on large codebases, which matters
concretely for tight local development feedback loops, for
pre-commit hooks (§25) that run on every commit, and for CI pipelines
(§26) where tool startup and execution time accumulates across every
pull request; and **consolidation** — having fewer separate tools to
install, configure, and keep version-compatible with each other
genuinely simplifies a project's development workflow, directly
connecting to this module's own dependency-management chapters (fewer
development dependencies to track and update).

**Ruff, described precisely as what it conceptually is:**
- A **linter** (§4) — detecting unused imports, undefined names, and a
  wide range of other suspicious patterns.
- A **formatter** (§3) — rewriting code into a consistent, deterministic
  layout.
- A **static analysis tool** (§4) — everything it does is based on
  reading source code, never executing it.
- An **auto-fixer** for certain classes of violations (§11) — capable
  of automatically rewriting code to resolve some diagnostics it
  finds, not merely reporting them.

**Ruff provides both linting and formatting** — this is worth stating
plainly, since it's easy to think of "Ruff" as only a linter (an
earlier, common association) when it is, today, genuinely both.

**What Ruff does *not* replace**, stated explicitly and without
exception, per §5's table:

- **pytest** (or any test framework) — Ruff cannot verify your
  program's actual behavior is correct (§31).
- **A dedicated type checker** (like mypy or Pyright) — Ruff does not
  perform the kind of deep, whole-codebase type inference a type
  checker specializes in (§32).
- **Runtime debugging** — finding out why a *specific* running process
  is behaving unexpectedly is a different activity from static
  analysis entirely.
- **Integration tests** — verifying that multiple real components work
  together correctly.
- **Security review** — Ruff includes some security-*adjacent* lint
  rules (§33), but is not a substitute for genuine security analysis
  or dependency-vulnerability scanning.
- **Architectural review** — whether a design is *well-structured* (the
  entire subject of this module's earlier chapters on project layout)
  is a human judgment call Ruff has no concept of at all.

## 7. Installing Ruff

Directly extending
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
own dependency-management workflow — Ruff is installed exactly the
way any other Python tool is: as a project dependency, managed with
`uv`.

**Installing Ruff globally** (system-wide, outside any specific
project) is possible, but reintroduces exactly the reproducibility
problem this module's earlier chapters spent so much effort solving:
a globally-installed Ruff has no recorded version tied to any specific
project, meaning two developers (or a developer and CI) could be
running two different Ruff versions with no record of the mismatch,
and potentially getting different results from the same code.

**Installing Ruff inside a project, as a managed development
dependency**, is the preferred, project-oriented approach — directly
reusing
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§21 development-dependency concept:

```bash
uv add --dev ruff
```

**`--dev`** marks this as a **development dependency** — needed only
while developing the project (running the linter/formatter locally
and in CI), never needed for the application to actually *run* in
production, exactly the same reasoning already established for
`pytest` in the previous chapter. **Project dependency** — this
command updates the project's own `pyproject.toml` (adding `ruff` to
its development dependency group) and `uv.lock` (recording the exact
resolved Ruff version), giving Ruff the same reproducibility guarantee
every other dependency in the project already has, per
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§13–§16.

**Why reproducibility matters specifically for a linter/formatter**:
if different developers (or CI) run different Ruff *versions*, they
can genuinely see different results — a newer Ruff release might add
new rules, or a formatter update might make a slightly different
layout decision — producing exactly the "works on my machine, fails
in CI" confusion this whole module has been building tools and habits
to prevent. Pinning Ruff's version through `uv.lock`, exactly like any
other dependency, closes this gap completely.

Once added, Ruff is run through the project's managed environment,
exactly as
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§24 established for any project tool:

```bash
uv run ruff --version
```

## 8. Basic Ruff Commands

**`ruff check`** — runs the **linter** against the project, reporting
diagnostics. Run with no path, it typically checks the current project
(based on its configuration); run with an explicit path, it checks
exactly that.

```bash
uv run ruff check .
```
- **What it does**: analyzes every Python file under the current
  directory (respecting configuration in `pyproject.toml`, §15) and
  prints every diagnostic it finds.
- **Why you use it**: to see, at a glance, every lint problem across
  the whole project.
- **When you use it**: locally during development, in pre-commit
  (§25), and in CI (§28).
- **What happens internally, at a high level**: Ruff parses each file
  (§3's AST concept), runs every currently-selected rule (§9) against
  that parsed structure, and collects every violation found into a
  report.
- **Common mistake**: running `ruff check` with no path from the wrong
  directory, and being confused when it reports nothing (or reports on
  the wrong files) — always confirm which directory you're running
  from, or pass an explicit path.
- **Production usage**: this exact command, run in CI, is what gates a
  pull request on lint cleanliness (§28).

```bash
uv run ruff check <file>
uv run ruff check <directory>
```
- Restrict the check to a specific file or directory — useful when
  investigating one particular module, or when a large project only
  wants a subset checked during a specific workflow step.

**`ruff format`** — runs the **formatter**, rewriting files in place to
match Ruff's consistent style.

```bash
uv run ruff format .
```
- **What it does**: reformats every Python file under the current
  directory, in place, according to Ruff's formatting rules.
- **Why/when you use it**: any time you want the whole project's
  formatting brought into a consistent, canonical state — commonly
  run locally before committing (§30), or on save in an editor (§24).
- **Internally**: parses each file (exactly like `ruff check` does),
  then renders it back out using Ruff's own deterministic formatting
  decisions (§3).
- **Common mistake**: running `ruff format` and being surprised that
  it *changed files* — this is expected, intended behavior (unlike
  `ruff check`, which only reports); always review the resulting
  diff (§11, §30) before committing.

```bash
uv run ruff format <file>
```
Restricts formatting to one specific file, exactly like `ruff check`'s
path argument.

**`ruff format --check`** — verifies formatting **without** modifying
any files:
```bash
uv run ruff format --check .
```
- **What it does**: reports which files *would* be reformatted, and
  exits with a non-zero status if any would — but changes nothing.
- **Why/when you use it**: exactly the use case CI needs (§27) — verify
  that formatting is already correct, without CI ever silently
  rewriting a developer's code.

**The difference between checking, formatting, automatic fixing, and
format verification, stated precisely, since these four terms are
easy to conflate:**

| Term | What it means |
|---|---|
| **Checking** (`ruff check`) | Report lint violations; change nothing |
| **Formatting** (`ruff format`) | Rewrite files to match the formatter's style |
| **Automatic fixing** (`ruff check --fix`, §11) | Rewrite code to resolve *lint* violations that have a known-safe fix |
| **Format verification** (`ruff format --check`) | Report whether formatting is already correct; change nothing |

## 9. Ruff Rules

A **rule** is one specific, named check Ruff knows how to perform. Each
rule has a **rule code** — a short prefix identifying its **rule
family** (the category/source of the check), followed by a number.

```
F401   →   family "F" (Pyflakes-derived rules), rule number 401 (specifically: unused import)
```

A **diagnostic** is the actual message Ruff prints when a rule fires;
a **violation** is the specific occurrence in your code that triggered
it. **Rule selection** is choosing which rule codes/families are
active for your project (§16); **rule exclusion** (or **ignoring**) is
explicitly turning specific rules off, either project-wide or for
specific files (§16, §18); **rule suppression** is silencing one
*specific occurrence* of a violation directly in the source code
(§17), distinct from disabling the rule entirely.

**Common rule families, introduced progressively** (these are real,
established Ruff rule-family prefixes — not invented for this
chapter):

| Family | What it covers |
|---|---|
| **F** | Pyflakes-derived checks — unused imports, unused variables, undefined names, and similar correctness-adjacent issues |
| **E** / **W** | pycodestyle-derived style checks (errors/warnings) — many of these overlap with what the formatter itself already handles |
| **UP** | pyupgrade — suggests modernizing code to use newer Python syntax/features (§21) |
| **B** | flake8-bugbear — likely-bug patterns beyond basic correctness (e.g. mutable default arguments) |
| **SIM** | flake8-simplify — suggests simpler, more idiomatic equivalents for unnecessarily complex code |
| **I** | isort-derived — import sorting and organization (§12) |
| **N** | pep8-naming — naming-convention checks (e.g. class names should be `CapWords`) |
| **A** | flake8-builtins — flags shadowing a Python builtin name (e.g. a variable named `list`) |
| **C4** | flake8-comprehensions — suggests more idiomatic comprehension usage |
| **PIE** | flake8-pie — miscellaneous small correctness/clarity checks |
| **RUF** | Ruff's own, Ruff-specific rules, not derived from another tool |

**Do not blindly enable every available rule** — Ruff supports many
rule families beyond this introductory list, and turning all of them
on at once, especially on an existing codebase, tends to produce
overwhelming amounts of noise (§34–§35 cover exactly this concern in
depth). Each family represents a genuinely different *category* of
concern, and a sensible project deliberately chooses which categories
actually matter for it, rather than reflexively maximizing rule count.

**A representative example, walked through fully — an `F401` unused
import:**

**Problematic code:**
```python
import os

def greet(name):
    return f"Hello, {name}"
```

**Ruff diagnostic** (conceptually):
```
file.py:1:8: F401 `os` imported but unused
```

**Explanation**: `os` is imported but never referenced anywhere in the
file — the import serves no purpose and misleads a reader into
thinking the module depends on `os`'s functionality.

**Corrected code:**
```python
def greet(name):
    return f"Hello, {name}"
```

**A second example — a `B006` mutable default argument (family `B`,
flake8-bugbear):**

**Problematic code:**
```python
def add_item(item, items=[]):
    items.append(item)
    return items
```

**Explanation**: a mutable default argument (`items=[]`) is created
**once**, when the function is defined — not fresh on every call —
meaning every call that doesn't supply its own `items` shares and
mutates the *same* list across calls, a classic, genuinely surprising
Python bug.

**Corrected code:**
```python
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

## 10. Common Lint Problems

Working through several representative categories in depth, each with
the full bad-code → diagnostic → explanation → fix pattern.

**Unused imports (`F401`):**
```python
# bad
import json
import os

def load_config(path):
    with open(path) as f:
        return json.loads(f.read())
```
`os` is never used. **Fix:** remove it.
```python
# good
import json

def load_config(path):
    with open(path) as f:
        return json.loads(f.read())
```

**Unused variables (`F841`):**
```python
# bad
def process(records):
    count = 0
    total = 0
    for record in records:
        total += record["value"]
    return total
```
`count` is assigned but never used or updated meaningfully. **Fix:**
remove it if it's genuinely unnecessary, or use it if it was meant to
track something.
```python
# good
def process(records):
    total = 0
    for record in records:
        total += record["value"]
    return total
```

**Undefined names (`F821`):**
```python
# bad
def greet(name):
    return f"Hello, {nam}"   # typo: `nam` instead of `name`
```
This is a genuine bug — `nam` was never defined anywhere, and this
code would raise `NameError` the moment it actually runs. Ruff catches
this **statically**, without ever executing the function. **Fix:**
```python
# good
def greet(name):
    return f"Hello, {name}"
```

**Unreachable code (part of Ruff's broader correctness-adjacent
checks):**
```python
# bad
def status(code):
    return "ok"
    print("this line never runs")   # unreachable — after a return
```
**Fix:** remove the unreachable line, or restructure the logic if it
was meant to run under some condition.

**Unnecessary expressions / suspicious constructs**, an illustrative
`SIM`-family example:
```python
# bad
if is_valid == True:
    process()
```
Comparing a boolean directly to `True` is redundant — `is_valid`
already *is* the boolean value being tested. **Fix:**
```python
# good
if is_valid:
    process()
```

**Incorrect/outdated import structure**, an illustrative `UP`-family
modernization (§21 covers this family in full):
```python
# bad — Python 2-era style, unnecessary in modern Python
class Config(object):
    pass
```
```python
# good — modern Python classes don't need to inherit from `object` explicitly
class Config:
    pass
```

**Deprecated syntax patterns**, another `UP`-family example:
```python
# bad — old-style string formatting
message = "Hello, %s" % name
```
```python
# good — modern f-string
message = f"Hello, {name}"
```

Every one of these examples shares the same shape: code that **runs**
(with the partial exception of the genuinely-buggy undefined-name
case), but that a linter can identify as worth reconsidering — dead
weight, a likely mistake, or an outdated idiom a modern equivalent
expresses more clearly.

## 11. Automatic Fixes

```bash
uv run ruff check --fix .
```

**What automatic fixing means**: for a subset of lint rules, Ruff
knows not just *that* something is wrong, but exactly *how* to
rewrite the code to fix it — and `--fix` tells Ruff to actually apply
those rewrites, rather than merely reporting them.

**Why automatic fixes are useful**: many violations (an unused import,
outdated syntax `UP` suggests modernizing) have one obvious, mechanical
correction — manually applying that same correction, one violation at
a time, across a whole codebase is exactly the kind of repetitive task
worth automating (§1's founding argument, applied directly to fixing,
not just detecting).

**What kinds of fixes can be considered safe**: removing a genuinely
unused import; rewriting `object`-inheriting class syntax to modern,
implicit-`object` syntax; rewriting an old-style `%`-format string to
an f-string where the transformation is unambiguous. Each of these
changes code in a way that's mechanically verifiable to preserve
behavior.

**Why not every violation should be automatically fixed**: some
violations require genuine *judgment* about intent — an unused
variable might indicate dead code to delete, *or* it might indicate a
bug where the variable was meant to be used somewhere and a fix should
add that usage back, not remove the variable. Ruff is conservative
about which fixes it applies automatically for exactly this reason —
but "conservative" does not mean "risk-free": **always review what
`--fix` actually changed** before trusting it, per the workflow below.

**Reviewing generated changes — the essential habit:**
```bash
uv run ruff check --fix .
git diff
```
`git diff` shows exactly what `--fix` changed, line by line — this is
not an optional extra step; it's the way you actually verify an
automated fix did what you expected, rather than trusting it blindly.

**The engineering principle underlying this entire section**:
**automate repetitive, mechanical changes; review semantic changes
manually.** Removing a genuinely unused import is mechanical — there's
no judgment call involved, the import is provably unused. Deciding
whether an unused variable represents dead code or a hidden bug is
semantic — it requires understanding *intent*, something no purely
static analysis can fully recover on its own. Ruff's own fix
categorization broadly respects this line, but the *reviewing*
responsibility never goes away — `git diff` after every `--fix` run,
every time, without exception.

## 12. Import Sorting

Extending
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
own import-hygiene guidance (§20 of that chapter) with the specific,
automated tool that enforces it.

**The conventional grouping**, directly reusing
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
own terms:

```python
# standard library
import json
import sys
from pathlib import Path

# third-party
import requests

# local/application
from myapp.config import load_config
```

- **Standard-library imports** first.
- **Third-party imports** next.
- **Local/application imports** last.
- Within each group, imports are conventionally sorted alphabetically.
- A blank line typically separates each group.

**Ruff's `I` rule family** (isort-derived) checks exactly this
grouping and ordering, and can automatically reorganize a file's
imports to match it (via `--fix`, §11) — including removing truly
unused imports (which overlaps with, but is distinct from, `F401`'s
own detection of the same underlying problem from a different rule
family).

**Before:**
```python
from myapp.config import load_config
import sys
import requests
import json
```

**After (Ruff's `I` family, applied):**
```python
import json
import sys

import requests

from myapp.config import load_config
```

**Why deterministic import ordering matters specifically in team
repositories**: without an enforced convention, imports drift into
whatever order each individual contributor happened to add them in —
producing noisy, inconsistent diffs every time someone touches a
file's imports for an unrelated reason, and making it harder to
quickly scan "what does this file actually depend on" at a glance.
Automating this removes it as a source of both inconsistency and
unproductive review comments, exactly the same reasoning §2 gave for
formatting generally.

## 13. Ruff Formatter

Revisiting `ruff format` (§8) in full depth.

**Formatter philosophy**: Ruff's formatter, like other modern Python
formatters, is deliberately **opinionated** (§3) — it makes most
layout decisions itself, offering only a small number of genuine
configuration choices (§15's `format.*` settings), rather than
exposing dozens of tunable style knobs. This is a deliberate design
choice: the less a formatter's output can be individually customized,
the less any two projects' formatted code differs *purely due to
configuration preference*, and the less any one project's team needs
to spend time debating formatting minutiae at all.

**What it covers, concretely, building on §2's list:**
- **Line wrapping** — how a line exceeding the configured length is
  split across multiple lines.
- **Strings/quotes** — Ruff's formatter can enforce a consistent quote
  style project-wide (configurable, §15).
- **Trailing commas** — added consistently to multi-line collections
  and calls, to keep future diffs clean when a new item is added.
- **Indentation** — consistently applied (configurable between spaces
  and tabs, §15, though spaces are the overwhelmingly common and
  recommended default).
- **Blank lines** — a consistent number of blank lines between
  top-level definitions, and within functions.
- **Function definitions, collections, long expressions** — each
  wrapped and laid out according to the formatter's own consistent
  rules once they exceed the configured line length.

**Before:**
```python
def process_order(order_id, customer_name, items, discount_percentage=0, apply_tax=True, notes=None):
    pass
```

**After** (Ruff's formatter, wrapping a signature that exceeds the
configured line length):
```python
def process_order(
    order_id,
    customer_name,
    items,
    discount_percentage=0,
    apply_tax=True,
    notes=None,
):
    pass
```

**Why formatting should generally be automated rather than debated
manually in code review**: exactly §2's closing argument, restated one
final time as this section's own conclusion — once a formatter is in
place and run consistently, "please add a trailing comma" or "please
wrap this differently" should never appear as a human review comment
again; the formatter has already made that decision, consistently,
before the reviewer ever looks at the diff.

## 14. Ruff Format vs. Ruff Check

The clearest possible statement of a distinction this chapter has been
building toward since §8.

| Command | Primary purpose | Modifies files? | Detects violations? | Fixes violations? | Typical workflow usage |
|---|---|---|---|---|---|
| `ruff format` | Apply consistent formatting | **Yes** | No (formatting isn't a "violation" — it's simply rewritten) | N/A | Run locally before committing; run on save |
| `ruff format --check` | Verify formatting without changing files | **No** | Reports files that would be reformatted | No | Run in CI (§27) |
| `ruff check` | Report lint violations | No | **Yes** | No | Run locally and in CI (§28) |
| `ruff check --fix` | Report **and** automatically resolve fixable lint violations | **Yes**, for fixable violations | **Yes** | **Yes**, for fixable ones | Run locally, reviewed via `git diff` before committing (§11) |

**A realistic local workflow:**
```bash
uv run ruff format .
uv run ruff check --fix .
```

**Why the order can matter, depending on project configuration**:
running the formatter first ensures every file is already in a
consistent layout before the linter runs — some lint fixes (§11) can
themselves produce code that then benefits from a formatting pass
(e.g., `--fix` reorganizing imports, per §12, may leave spacing the
formatter would otherwise adjust). Running `ruff format` before
`ruff check --fix` is the generally recommended order for exactly this
reason, though a project's own configuration and specific rule
selection can occasionally make the reverse order more appropriate —
this is worth verifying for your own project's specific setup rather
than assumed universally.

## 15. `pyproject.toml` Configuration

Directly extending
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
own `pyproject.toml` literacy — Ruff reads its configuration from a
`[tool.ruff]` section (and its nested subsections) in the same file
this module has already established as the project's central
configuration home.

**A minimal starting configuration:**
```toml
[tool.ruff]
line-length = 100
target-version = "py312"
```

**Progressively adding more:**
```toml
[tool.ruff]
line-length = 100
target-version = "py312"
exclude = ["build", "dist"]
extend-exclude = ["migrations"]
include = ["*.py"]
extend-include = ["*.pyi"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
ignore = ["E501"]
extend-select = ["SIM"]
extend-ignore = []
per-file-ignores = { "tests/*.py" = ["F401"] }

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
```

**Every field, explained:**

- **`line-length`** — the maximum line length the formatter targets
  and (for the relevant lint rules) the linter checks against; a
  common convention is somewhere between 79 and 100+ characters,
  chosen per-project.
- **`target-version`** — the minimum Python version the project
  supports (§20), used by Ruff to decide which syntax features/
  modernization suggestions are actually valid to apply.
- **`exclude`** — a list of paths/patterns Ruff should never analyze
  at all (§19) — for a project's own build artifacts, virtual
  environments, or similar.
- **`extend-exclude`** — **adds** additional exclusions on top of
  Ruff's own sensible built-in defaults, rather than replacing them
  entirely (the distinction between a plain setting and its
  `extend-` counterpart recurs throughout Ruff's configuration, and is
  explained precisely in §16).
- **`include`** / **`extend-include`** — the mirror image of
  `exclude`/`extend-exclude`: which file patterns Ruff *should*
  consider (by default, `*.py`; `extend-include` is useful for adding
  something like `*.pyi` stub files without replacing the default).
- **`lint.select`** — which rule codes/families are active (§16).
- **`lint.ignore`** — which rule codes are turned off, project-wide
  (§16).
- **`lint.extend-select`** / **`lint.extend-ignore`** — add to
  `select`/`ignore` without replacing them entirely (§16).
- **`lint.per-file-ignores`** — rule exceptions scoped to specific
  file patterns (§18).
- **`format.quote-style`** — `"double"` or `"single"` — which quote
  character the formatter standardizes on.
- **`format.indent-style`** — `"space"` or `"tab"` — spaces are the
  overwhelmingly common, recommended choice for Python.
- **`format.line-ending`** — how the formatter handles line endings
  (e.g. `"auto"`, letting it detect and preserve the project's
  existing convention, connecting directly to
  [05-encodings-and-newlines.md](../05-Text-Files-Structured-Data-and-CLI-Programs/05-encodings-and-newlines.md)'s
  `\n`/`\r\n` discussion from Module 1.5).

**A note on configuration evolution, addressed directly rather than
glossed over**: Ruff's configuration structure has changed over its
own development history — in particular, lint-related settings
(`select`, `ignore`, and related keys) now live under a nested
**`[tool.ruff.lint]`** table, as shown above, rather than directly
under the top-level `[tool.ruff]` table the way some **older**,
**legacy** Ruff configurations (and documentation predating this
change) place them. If you encounter an existing project's
`pyproject.toml` with `select`/`ignore` written directly under
`[tool.ruff]` (with no `[tool.ruff.lint]` table at all), recognize
that as the **legacy** form — the modern, current equivalent is the
nested `[tool.ruff.lint]` structure this section teaches. Always
verify the exact schema your installed Ruff version expects (via its
own current documentation, or `uv run ruff config --help` /
equivalent, per this chapter's stated commitment not to assume
unverified specifics) rather than copying a configuration from an
older tutorial without checking it still matches.

## 16. Selecting and Ignoring Rules

```toml
[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]
extend-select = ["UP", "B"]
extend-ignore = ["F401"]
```

- **`select`** — the base set of rule codes/families to enable,
  **replacing** whatever Ruff's own default selection would otherwise
  be.
- **`ignore`** — rule codes to turn off from within that selected set.
- **`extend-select`** — **adds** additional rules on top of whatever
  `select` already specifies, without needing to repeat the entire
  list.
- **`extend-ignore`** — **adds** additional ignored rules on top of
  whatever `ignore` already specifies.

**Why projects sometimes exclude specific rules**: a rule might not
fit a project's own conventions (a team that deliberately allows lines
longer than the default in specific, justified cases might disable
the corresponding length-related rule); a rule might produce too many
false positives for a project's specific coding patterns (§36); or a
project might be in the middle of a gradual migration (§34–§35) and
deliberately deferring a whole rule family until later.

**Disabling a rule globally** (project-wide, via `ignore`/
`extend-ignore` in `[tool.ruff.lint]`) vs. **disabling a rule for one
file** (via `per-file-ignores`, §18) vs. **disabling a rule for one
category/directory** (also via `per-file-ignores`, using a glob
pattern matching that directory) vs. **inline suppression** (silencing
one *specific occurrence*, directly in the source, §17) — four
distinct scopes, from broadest to narrowest, and choosing the
*narrowest scope that genuinely fits the situation* is the underlying
engineering principle this section (and §17–§18) both reinforce.

**The danger of excessive ignores**: every ignored rule is a category
of problem the project has explicitly chosen to stop checking for —
reasonable when deliberate and justified, but a project that
accumulates a long, undocumented list of ignored rules over time has
effectively degraded its own linting into "checks for whatever happens
to still be enabled," with no one able to easily reconstruct *why*
each ignore exists. **The engineering principle worth internalizing**:
**configuration should encode deliberate project policy, not hide
problems.** An ignore added because "this rule doesn't apply to how
our project legitimately does X" is policy; an ignore added because
"this rule was too annoying to actually fix the violations for" is
hiding a problem — the configuration file itself cannot tell these
apart, which is exactly why the discipline behind *why* an ignore
exists matters as much as the ignore itself (ideally documented with a
comment directly in `pyproject.toml`).

## 17. Inline `noqa` / Suppression

For a single, specific occurrence of a violation that's genuinely
justified in context, Ruff supports inline suppression using a
`# noqa` comment (a convention inherited from the broader Python
linting ecosystem, not unique to Ruff):

```python
import used_only_conditionally  # noqa: F401
```

**Rule-specific suppression** (`# noqa: F401`) silences only that one
specific rule, for that one specific line — this is strongly
preferable to a **bare** `# noqa` (silencing *every* rule that would
otherwise fire on that line), because a bare suppression can silently
hide a completely unrelated, *future* violation on that same line that
nobody intended to suppress at all.

```python
# BAD — bare noqa, silences everything on this line, forever, unconditionally
import used_only_conditionally  # noqa

# BETTER — rule-specific, silences only the one, understood, justified violation
import used_only_conditionally  # noqa: F401
```

**When suppression is justified**: a genuinely rare, well-understood
exception — an import that's technically "unused" from Ruff's static
point of view but is actually required for a specific runtime side
effect (e.g., some libraries require importing a module purely to
register something, with no name from it ever referenced directly).

**When suppression is a code smell**: reaching for `# noqa` as the
default response to any inconvenient violation, rather than actually
fixing the underlying code — this defeats the entire purpose of
linting, converting "the linter caught something worth looking at"
into "the linter has been told to stop looking here," permanently,
without necessarily any real justification behind it.

**Documenting an unusual exception**, the recommended practice:
```python
import side_effect_only_module  # noqa: F401  -- imported for its registration side effect
```
A short comment explaining *why* the suppression exists turns a
silent, unexplained exception into a documented, reviewable one — the
next person reading this line (including future you) can immediately
understand the reasoning, rather than wondering whether it was ever
justified at all.

## 18. Per-File Ignores

Some files legitimately need different rules than the rest of a
project — not because the project's own standards are inconsistent,
but because the *purpose* of that specific file genuinely differs.

```toml
[tool.ruff.lint.per-file-ignores]
"tests/*.py" = ["F401"]
"__init__.py" = ["F401"]
```

**Why some files legitimately need different rules**:
- **Tests** — a test file might deliberately import a fixture or a
  module purely for its side effects (setting up test data), in a way
  the ordinary "unused import" rule would otherwise flag unfairly.
- **`__init__.py`** — per
  [02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
  §7, an `__init__.py` frequently re-exports names purely for a
  package's public API — those imports are, by design, not "used"
  within `__init__.py` itself, yet are entirely intentional.
- **Migration files** — auto-generated database migration scripts
  (a later Stage topic) often follow their own generation-tool
  conventions that don't match ordinary project style.
- **Generated files** (§19) — code produced by another tool, where
  editing it by hand to satisfy a lint rule would be pointless and
  immediately overwritten the next time it's regenerated.
- **Compatibility code** — a small module deliberately written to
  support an older Python version or dependency, which might
  necessarily use patterns the rest of the project's modernization
  rules (§21) would otherwise flag.
- **Scripts** — a one-off script (per
  [02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
  §16) might reasonably be held to a slightly different, less strict
  standard than the core reusable package.

**How per-file ignores work**, mechanically: each key in
`per-file-ignores` is a glob pattern matching one or more files; the
associated list is the set of rule codes ignored *specifically* for
files matching that pattern — every other file in the project remains
subject to the full, normal rule selection.

**Why generated code should generally not be manually edited just to
satisfy linting**: any manual edit to a generated file is guaranteed
to be silently discarded and overwritten the next time the generation
process runs — "fixing" a lint violation in generated code by hand
produces a change that provides zero lasting value; the correct
response is almost always to exclude the generated file from linting
entirely (§19), not to chase its violations one regeneration at a
time.

## 19. Generated Code and Exclusions

Several categories of files should generally never be treated as
ordinary application source code for linting/formatting purposes:

- **Generated files** — code produced by another tool (a code
  generator, an ORM's migration tool, a protocol-buffer compiler) —
  per §18, editing these by hand to satisfy a lint rule is pointless.
- **Vendor code** — third-party code vendored directly into a
  repository (copied in, rather than installed as a dependency) —
  typically not something the project's own team maintains or should
  be reformatting according to its own conventions.
- **Build directories** — output produced by a packaging/build process
  (this module's own build-configuration coverage in
  [03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
  §24) — not source code at all.
- **Virtual environments** — the actual installed package files inside
  a project's own `.venv`-style directory (per
  [03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
  §12) — these are *other projects'* source code, entirely outside
  this project's own responsibility.
- **Caches** — tool-generated cache directories (including Ruff's own
  cache) — never meant to be linted or version-controlled at all.
- **Generated schemas** — auto-produced data-schema files, similarly
  to generated code generally.
- **Temporary files** — scratch output, never meant to be part of the
  reviewed, committed codebase.

```toml
[tool.ruff]
exclude = ["build", "dist", ".venv", "__pycache__"]
extend-exclude = ["src/myapp/generated"]
```

`exclude` sets (or fully replaces) the base exclusion list; `extend-
exclude` **adds** to Ruff's own already-sensible built-in defaults
(which already cover many of the common cases above, like
`__pycache__` and `.venv`-style directories, without needing to be
listed explicitly) — exactly the same `extend-`-prefix pattern §16
already established for rule selection, now applied to path exclusion
instead.

**The difference between project source code and generated/external
artifacts, restated as this section's central principle**: linting and
formatting exist to maintain the quality of code *your team actually
writes and maintains* — code you didn't write, don't maintain by
hand, or that gets regenerated automatically, should be excluded from
that process entirely, not fought against every time it happens to
violate a rule it was never written with in mind.

## 20. Target Python Version

```toml
[tool.ruff]
target-version = "py312"
```

**Why Ruff needs to know the target Python version**: several of
Ruff's checks and formatting decisions depend directly on *which*
Python syntax features are actually available and safe to suggest.
`target-version` tells Ruff "assume this project runs on at least this
Python version" — directly mirroring
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§6 `requires-python` declaration, though the two are configured
separately (`requires-python` lives in `[project]`; `target-version`
lives in `[tool.ruff]`) and, in a well-maintained project, should
agree with each other.

**How Python versions affect Ruff's behavior:**
- **Syntax** — some syntax is only valid on newer Python versions
  (e.g., certain typing syntax introduced in a specific release);
  Ruff needs to know your minimum supported version before suggesting
  (or accepting) such syntax.
- **Available language features** — similarly, some standard-library
  features or language constructs simply don't exist on older Python
  versions.
- **Lint rules** — certain rules are only meaningful, or only
  triggerable, in the context of a specific Python version's actual
  capabilities.
- **Modernization suggestions** (§21) — the entire `UP` rule family
  depends directly on `target-version`: Ruff will not suggest
  rewriting code to use a newer syntax feature if that feature isn't
  actually available on the project's own declared minimum Python
  version.

**Connecting this to the project's own dependency compatibility**: if
`target-version` claims a newer Python than the project's actual
`requires-python` genuinely supports, Ruff could suggest (or silently
apply, via `--fix`) modernizations that would break on the project's
own oldest supported Python version — keeping the two settings
consistent is a real, practical correctness concern, not just tidiness.

## 21. Modernization Rules

The **`UP`** family (short for "pyupgrade," the tool this rule family
is derived from) specifically suggests rewriting older Python idioms
into their modern equivalents, once `target-version` (§20) confirms
the modern syntax is actually available.

```
Older Python style
        ↓
Modern Python syntax
```

**Example 1 — old-style string formatting:**
```python
# before
message = "Hello, %s! You are %d years old." % (name, age)

# after (UP suggests)
message = f"Hello, {name}! You are {age} years old."
```

**Example 2 — unnecessary `object` inheritance:**
```python
# before
class Config(object):
    pass

# after
class Config:
    pass
```

**Example 3 — an older-style type-hint import pattern** (illustrative
of the *kind* of modernization this family covers, without asserting
a specific exact rule number):
```python
# before (older-style typing import for a feature now built into the language)
from typing import List

def get_names() -> List[str]:
    ...

# after (modern Python allows the builtin directly, once target-version confirms support)
def get_names() -> list[str]:
    ...
```

**The difference between formatting, linting, and modernization,
stated precisely**: formatting changes *layout only* (spacing, line
breaks); ordinary linting (the `F`/`E`/`B` families, for instance)
flags *problems* (unused code, likely bugs) without necessarily
proposing a *stylistic rewrite*; **modernization** specifically
proposes rewriting *correct, working* code into a newer, generally
preferred idiom — the code being flagged wasn't broken, it's simply
not using the *current* recommended way of expressing the same idea.

**Compatibility considerations before applying modernization rules**:
always confirm `target-version` (§20) genuinely matches your project's
actual minimum supported Python version *before* enabling or trusting
`UP`-family auto-fixes — applying a modernization that assumes a newer
Python than what your project (or its users) actually run would
introduce a real, environment-specific bug, precisely the kind of
mistake this rule family's own configuration (`target-version`) exists
to prevent.

## 22. Configuration Design

Rather than simply handing over one large configuration file, this
section walks through the **decisions** behind writing one well.

**A minimal starting configuration** — appropriate for a brand-new
project, or the very first step of adopting Ruff on an existing one:
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.format]
quote-style = "double"
```
This alone gives a project consistent formatting and Ruff's own
sensible default lint selection — a genuinely reasonable starting
point, not something to be embarrassed about shipping.

**A beginner project configuration** — adding a small, well-understood
set of rule families deliberately:
```toml
[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```
`E`/`F` (basic style and correctness-adjacent checks), `I` (import
sorting, §12), and `UP` (modernization, §21) together form a small,
easy-to-justify starting selection — each family's purpose is easy to
explain to a new contributor in one sentence.

**A production project configuration** — layering in additional rule
families deliberately, each for a stated reason:
```toml
[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "N", "A", "C4", "PIE", "RUF"]
ignore = ["E501"]   # line length is enforced by the formatter itself; avoid redundant/conflicting signal

[tool.ruff.lint.per-file-ignores]
"tests/*.py" = ["F401"]
"__init__.py" = ["F401"]
```

**Discussing the decisions, not just presenting the file:**
- **Consistency** — every rule enabled should apply uniformly across
  the codebase, with per-file exceptions (§18) used only for
  genuinely different file purposes, never as a workaround for
  inconsistent effort.
- **Maintainability** — a smaller, well-justified rule selection that
  the whole team actually understands and agrees with is more
  maintainable than a maximal selection nobody can fully explain.
- **Strictness** — should scale with the project's actual maturity and
  risk tolerance (§39 develops this further); a young, fast-moving
  prototype and a stable production service reasonably differ here.
- **Developer experience** — an overly strict configuration introduced
  all at once on a team unfamiliar with it creates friction and
  resentment; a configuration introduced gradually (§34) with clear
  reasoning builds buy-in instead.
- **CI reliability** — every rule enabled in CI should be one the team
  is actually prepared to enforce as a genuine merge gate (§26, §28) —
  not aspirational rules nobody intends to actually fix violations
  for.
- **Gradual adoption** — §34–§35 cover this in full; the configuration
  design itself should anticipate that a real project's rule selection
  will likely grow over time, not be finalized on day one.

**Do not encourage unnecessarily complicated configuration** — the
goal of a well-designed Ruff configuration is a small number of
deliberate, well-understood decisions, not the largest possible
configuration file.

## 23. Editor / IDE Integration

Ruff commonly integrates directly into a code editor, providing
immediate, in-context feedback as you type — rather than only being
run separately, after the fact, from the terminal.

**In VS Code specifically** (used here as a concrete, common example,
without implying it's the only supported editor): the official Python
extension provides general Python language support, and a dedicated
**Ruff extension/integration** connects Ruff's own linter and
formatter directly into the editor's diagnostics and formatting
systems — meaning violations appear as inline squiggly underlines, and
formatting can be triggered directly from within the editor, without
switching to a terminal at all.

**The conceptual flow:**
```
save file
    ↓
formatter runs (if format-on-save is enabled, §24)
    ↓
linter runs
    ↓
diagnostics appear inline, in the editor
    ↓
developer reviews and fixes issues (possibly via a "quick fix" action the editor offers)
```

**Quick fixes**: many editors surface Ruff's auto-fixable violations
(§11) as a one-click (or one-keystroke) "quick fix" action directly
at the location of the diagnostic — applying the same underlying fix
`ruff check --fix` would, but scoped to that one specific violation,
interactively, as you're already looking at it.

**Why editor feedback is useful but should not be the only enforcement
mechanism**: editor integration is genuinely valuable for immediate,
in-the-moment feedback while writing code — but it depends entirely on
*every* contributor having it correctly configured, and on nobody ever
committing code without having actually looked at their editor's
diagnostics first. Neither of these is a safe assumption for a real
team — which is exactly why **pre-commit** (§25) and, more
importantly, **CI** (§26) exist as independent, unavoidable
enforcement layers that don't depend on any individual developer's
local editor setup at all.

## 24. Format on Save

**Format on save** is an editor setting that automatically runs the
formatter (§13) every time a file is saved, without the developer
needing to manually invoke it. **Lint-on-save** is the equivalent idea
for the linter — diagnostics refresh automatically as you save (many
editors also refresh linting live, as you type, not only on save).
**Automatic fixes on save** goes one step further, applying certain
auto-fixable lint corrections (§11) automatically at save time too.

**Benefits**: an extremely tight feedback loop — formatting and many
lint issues are resolved the instant you save, with essentially zero
manual effort, and code committed from an editor configured this way
is very likely already close to the project's actual, enforced
standard by the time it reaches `git diff` at all.

**Trade-offs**: format-on-save changes files *without* an explicit,
separate step you consciously decided to run — meaning it's
especially important to still review `git diff` before committing
(§30), since files can be silently reformatted as a side effect of
simply opening and re-saving them for an unrelated reason. **Aggressive
auto-fixing on save specifically can be undesirable** in one particular
case: if a fix-on-save action rewrites code *while you're still in the
middle of typing it* (an incomplete expression, a not-yet-finished
edit), it can interfere with your own in-progress work rather than
helping it — many developers deliberately enable format-on-save
(generally safe, since formatting never changes meaning) while being
more selective about which specific fix categories, if any, apply
automatically on save versus only when explicitly requested (§11's
own "review before trusting" discipline, applied here to *when* a fix
gets applied at all, not just whether to trust it once applied).

## 25. Pre-Commit

**`pre-commit`** is a widely-used framework for running automated
checks **immediately before a Git commit is created**, directly on the
developer's own machine — rejecting the commit outright if any
configured check fails.

**Why teams use it**: it catches problems (formatting drift, lint
violations) at the earliest possible point — before a commit even
exists, let alone before it reaches a shared branch or a pull
request — giving the fastest possible feedback loop of any enforcement
layer this chapter covers.

```
git commit
    ↓
pre-commit hooks run automatically
    ↓
Ruff format / Ruff check run as configured hooks
    ↓
commit ACCEPTED (all hooks passed) or REJECTED (a hook failed)
```

**How Ruff participates**: a project's `pre-commit` configuration
(typically a `.pre-commit-config.yaml` file — a separate configuration
file this chapter does not go further into, beyond noting where Ruff
fits into it) can register Ruff's formatter and linter as hooks, so
every commit automatically runs `ruff format --check` (or `ruff
format`, applying fixes directly) and `ruff check` before the commit
is allowed to be created at all.

**The difference between local developer checks, pre-commit checks,
and CI checks — three genuinely different enforcement layers:**

| Layer | Runs when | Enforced how strictly |
|---|---|---|
| **Local developer checks** (editor integration, §23) | While actively editing, or manually invoked | Entirely optional — depends on the individual developer's setup and habits |
| **Pre-commit checks** | Automatically, at `git commit` time | Blocks the commit itself if a check fails — but can, in principle, be bypassed by the developer (e.g. with an explicit override flag) |
| **CI checks** (§26) | Automatically, on every push/pull request, on a shared, controlled server | The strongest layer — cannot be bypassed by any individual developer's local configuration or choices |

Pre-commit is a genuinely valuable *early* layer, but — precisely
because it runs on each individual developer's own machine, under
their own control — it is not, by itself, a substitute for the
independent, un-bypassable verification CI provides (§26).

## 26. CI/CD Integration

A complete, realistic professional workflow, tying every layer covered
so far together:

```
Developer
    ↓
Local Ruff (format + check, §8, §23-25)
    ↓
Git commit (possibly gated by pre-commit, §25)
    ↓
Pull request
    ↓
CI
    ↓
Ruff format --check   (§27)
    ↓
Ruff check              (§28)
    ↓
Tests
    ↓
Build/deploy
```

**Why CI should independently verify code quality**, rather than
simply trusting that a developer ran the right commands locally:
directly extending
[07-standard-streams-and-exit-codes.md](../05-Text-Files-Structured-Data-and-CLI-Programs/07-standard-streams-and-exit-codes.md)'s
§23 CI discussion — a developer's local environment might be
misconfigured, might have skipped a step, or might be running a
different (unpinned, out-of-date) Ruff version than the project
actually declares (§7). CI, running in a clean, reproducible
environment built from the project's own committed
`pyproject.toml`/`uv.lock` (per
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§28), is the one place that verifies code quality **the same way,
every time, regardless of any individual developer's local setup**.

**Reproducibility, clean builds, failed checks, pull requests, branch
protection**: CI's Ruff check runs against the exact locked Ruff
version (reproducibility); starts from a genuinely clean checkout, not
an accumulated local environment (a clean build); a failing check
produces a clearly failed CI run, visible directly on the pull
request; and a repository's **branch protection** settings can require
that CI check to pass before a pull request is even allowed to be
merged — turning "please run the linter" from a polite request into a
structurally enforced requirement no pull request can bypass.

## 27. Format Checking in CI

```bash
uv run ruff format --check .
```

**Why CI should generally *verify* formatting, rather than *modify*
source code directly**: CI's job is to **confirm** that a developer
already did the right thing locally, not to silently fix it on their
behalf — if CI simply ran `ruff format .` and then, say, committed the
result automatically, it would be modifying a pull request's code
without the author's direct knowledge or explicit review, which
undermines the reviewability and ownership every change in version
control should have.

**Developer responsibility vs. CI verification responsibility**: the
**developer** is responsible for running `ruff format` locally (or
having it applied via format-on-save, pre-commit, or an editor
integration) *before* pushing; **CI** is responsible only for
*independently confirming* that responsibility was actually met —
`ruff format --check` reports non-zero (§29) if anything would still
be reformatted, failing the CI run and clearly signaling to the
developer "you forgot to run the formatter," without CI ever touching
the code itself.

**Why CI should generally fail when formatting is inconsistent**: this
is precisely what keeps formatting a *fully automated, zero-debate*
concern (§13's closing point) — if CI merely warned, rather than
failing outright, formatting drift would gradually creep back into the
codebase over time, exactly undoing the entire point of having an
opinionated, automated formatter in the first place.

## 28. Linting in CI

```bash
uv run ruff check .
```

**Appropriate CI behavior**: run this exact command against the pull
request's code; if Ruff finds any violation under the project's
current rule selection (§16), the command exits non-zero (§29), and
the CI pipeline stage fails — blocking the pull request from being
merged, exactly like a failing test would.

**Exit codes, success, failure, diagnostics, pipeline gating** —
directly reusing
[07-standard-streams-and-exit-codes.md](../05-Text-Files-Structured-Data-and-CLI-Programs/07-standard-streams-and-exit-codes.md)'s
own established vocabulary: `ruff check`'s **exit code** is the
*single* piece of information CI actually needs to make its merge
decision (§29 works through this precisely); the **diagnostics**
Ruff prints are for the *human* reading the failed CI log to
understand exactly what to fix; **pipeline gating** is the general
term for using a step's exit status to decide whether the rest of the
pipeline (tests, build, deploy) should even proceed at all.

## 29. Exit Codes and Automation

Directly connecting Ruff to
[07-standard-streams-and-exit-codes.md](../05-Text-Files-Structured-Data-and-CLI-Programs/07-standard-streams-and-exit-codes.md)'s
entire chapter, now applied to a real, concrete tool rather than
hypothetical example scripts.

Conceptually, and consistent with the standard Unix convention that
chapter established in depth:
```
ruff check .    exits 0   →   no violations found (given current configuration) — SUCCESS
ruff check .    exits non-zero   →   at least one violation was found — FAILURE
```
The same pattern applies to `ruff format --check` (non-zero if any
file would be reformatted) and `ruff check --fix` (its exit status
reflects whether any *unfixable* violations remain after applying
every available automatic fix).

**How CI systems use this**: exactly
[07-standard-streams-and-exit-codes.md](../05-Text-Files-Structured-Data-and-CLI-Programs/07-standard-streams-and-exit-codes.md)'s
§22–§23 — a CI system runs the command and checks *only* its exit
status to decide pass/fail, never needing to parse Ruff's printed
diagnostic text to make that decision (though a human reading the CI
log absolutely benefits from that same printed text).

**Connecting Ruff to shell scripts, Makefiles, CI pipelines, and
automation generally**, directly reusing
[07-standard-streams-and-exit-codes.md](../05-Text-Files-Structured-Data-and-CLI-Programs/07-standard-streams-and-exit-codes.md)'s
§21 shell-chaining vocabulary:
```bash
uv run ruff format --check . && uv run ruff check . && uv run pytest
```
`&&` chains each command so that the next one only runs if the
previous one **succeeded** (exit `0`) — a direct, practical, shell-level
application of exactly the exit-code automation principle this
course's Module 1.5 chapter first established, now composing three
real, independent quality-assurance tools (formatter, linter, tests)
into one linear, fail-fast pipeline.

## 30. Ruff and Git

A professional, deliberate Git workflow incorporating everything this
chapter has covered so far:

```
edit code
    ↓
ruff format .
    ↓
ruff check --fix .
    ↓
review git diff
    ↓
run tests
    ↓
commit
```

**Why developers should inspect automatic changes before committing**
— restating and consolidating §11's and §24's review discipline as a
firm, final habit: both `ruff format` and `ruff check --fix` *rewrite
files*; committing without first reviewing exactly what they changed
means committing changes you haven't actually looked at, which is
never a sound practice regardless of how much you trust the tool that
made them.

**Noisy formatting commits**: running a formatter for the *first
time* on an existing, previously-unformatted file can produce a large,
sweeping diff purely from reformatting — even when the actual, intended
change is small. **Unrelated changes**: mixing a genuine logic change
together with a large, incidental reformatting of unrelated code in
the same commit makes that commit much harder to review, since a
reviewer now has to mentally separate "what changed on purpose" from
"what changed because the formatter touched it." **Reviewability and
clean commits**: the practical remedy is to keep formatting-only
changes in their **own**, separate commit (or even a separate pull
request, for a large first-time reformat of an existing codebase),
distinct from commits that contain actual logic changes — exactly the
same "atomic, reviewable change" discipline
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§32 established for `pyproject.toml`/`uv.lock` changes, now applied to
formatting/lint-fix changes specifically.

## 31. Ruff and Testing

**Ruff does not replace tests — this needs to be stated as plainly as
possible, because it is the single most consequential misunderstanding
a beginner can carry out of this chapter.**

```python
def average(numbers):
    return sum(numbers) / len(numbers) - 1   # BUG: the "- 1" should not be here
```

This function:
- **Passes Ruff's linter** — there's no unused import, no undefined
  name, no suspicious construct Ruff's rules are designed to catch;
  syntactically and structurally, this is perfectly ordinary code.
- **Would pass a type checker** too (§32) — `numbers` is used
  consistently, the arithmetic is type-correct, and the return value
  is a valid `float`.
- **Still contains a genuine logical bug** — it computes the wrong
  answer, off by exactly one, for every single input.

```python
>>> average([2, 4, 6])
3.0   # WRONG — the correct average is 4.0
```

**Only a test** — actually *running* the function against a known
input and checking the output against the *expected* result — can
catch this:
```python
def test_average():
    assert average([2, 4, 6]) == 4.0   # this test would correctly FAIL, exposing the bug
```

This is exactly why §5's layered pipeline lists **linting** and
**testing** as distinct, complementary stages, each catching a
category of problem the other structurally cannot:

```
formatting        — layout only; no idea whether the code is "correct" at all
linting             — structural/pattern problems; still no idea whether the LOGIC is correct
type checking          — type consistency; still no idea whether the VALUE is correct
unit testing               — verifies specific, known input/output pairs
integration testing            — verifies multiple real components working together
system testing                    — verifies the whole system behaves correctly end to end
```

Every layer is necessary; none is sufficient on its own. Ruff earns
its place in this pipeline specifically by handling formatting and
linting extremely well and extremely fast — it was never designed to,
and does not attempt to, replace any of the layers beneath it.

## 32. Ruff and Type Checkers

A **type checker** (such as mypy or Pyright — mentioned here purely as
contextual, well-known examples, not as a tutorial) performs a
fundamentally different kind of analysis than Ruff's linter: it
verifies that values flowing through a program are used **consistently
with their declared or inferred types**, across the *entire* codebase
at once, following how a value moves from one function to another.

```python
def get_user_age(user: dict) -> int | None:
    return user.get("age")

def print_next_birthday_age(age: int) -> None:
    print(age + 1)

age = get_user_age({"name": "Alice"})
print_next_birthday_age(age)   # BUG: age could be None here, but print_next_birthday_age expects int
```

A type checker examining this code would flag `print_next_birthday_age(age)`
specifically because `age`'s declared type is `int | None` (it can
legitimately be `None`, per `get_user_age`'s own return type), while
`print_next_birthday_age` declares that it requires a plain `int` —
a real, structural type mismatch that would only surface at *runtime*
(as a `TypeError` inside `age + 1`, if `age` actually happened to be
`None` for this particular call) without a type checker's static
analysis catching it beforehand.

**Ruff's linter, by contrast**, does not perform this kind of deep,
cross-function type-flow analysis at all — it is not what its rule
families (§9) are designed to detect. **Ruff and a dedicated type
checker solve genuinely different problems**: Ruff focuses on
formatting consistency and a broad range of pattern-based
correctness/style checks that don't require deep type inference;
a type checker focuses specifically, and deeply, on type consistency
across the whole program. A well-configured production Python project
typically runs **both**, as genuinely separate, complementary pipeline
stages (§5's diagram already placed them this way), each catching
what the other cannot. This chapter deliberately does not turn into a
type-checking tutorial — that is a dedicated topic of its own,
elsewhere in this course.

## 33. Ruff and Security

**Linting is not equivalent to security scanning** — a distinction
worth stating with the same directness as §31's testing distinction.

Ruff does include some **security-adjacent lint rules** (certain rule
families flag patterns that are frequently, though not exclusively,
associated with security problems — for instance, patterns resembling
unsafe use of certain standard-library functions). These rules are
genuinely useful, real signal — but they are a **narrow, pattern-based
slice** of what real security analysis involves, not a comprehensive
security tool.

What Ruff **can** contribute: flagging a small set of known-risky
*code patterns*, purely by recognizing their textual/structural shape
— exactly the kind of static, pattern-based check §4 already
established as linting's fundamental nature and limit.

What Ruff **cannot** do, and was never designed to do:
- **Dependency vulnerability scanning** — checking whether any of your
  project's actual, resolved dependency *versions* (per
  [04-dependency-management-and-semantic-versioning.md](04-dependency-management-and-semantic-versioning.md)'s
  §25 security discussion) have a known, published vulnerability — a
  fundamentally different check requiring a database of known
  vulnerabilities and your project's exact dependency graph, not
  source-code pattern analysis.
- **Secret detection** — finding accidentally-committed credentials or
  API keys in your codebase — a different kind of specialized scanning
  entirely, not something Ruff's rule families are built for.
- **SAST (Static Application Security Testing)** more broadly —
  dedicated security-analysis tools perform much deeper, security-
  specific static analysis than a general-purpose linter's occasional
  security-adjacent rule can provide.
- **Dependency scanning** — a distinct category of tooling, separate
  from Ruff entirely, specifically for auditing a project's dependency
  tree against known vulnerability databases.

**The honest, accurate summary this section insists on**: treat Ruff's
security-adjacent rules as a small, genuinely useful *bonus* layer of
defense-in-depth, never as a substitute for dedicated
dependency-vulnerability scanning, secret detection, or real security
review. Overstating what a general-purpose linter catches, security-
wise, is itself a real risk — a false sense of security is often worse
than clearly knowing a gap exists.

## 34. Rule Management Strategy

How a real engineering team might adopt Ruff **gradually**, rather
than attempting to enable everything at once:

**Stage 1 — formatter only.** Adopt `ruff format` first, alone.
Formatting changes are the lowest-risk, easiest-to-review category of
change (they never alter behavior, per §3), making this the safest
possible first step, and immediately establishing a consistent,
debate-free baseline across the whole codebase.

**Stage 2 — basic linting.** Enable a small, well-understood rule
selection (`E`, `F`, perhaps `I`) — catching unused imports, undefined
names, and basic style issues, without yet introducing more opinionated
or higher-noise families.

**Stage 3 — automatic safe fixes.** Once the team is comfortable with
Stage 2's diagnostics, start applying `ruff check --fix` (§11)
regularly, always reviewed via `git diff` — mechanically resolving
the easy, safe violations, freeing attention for anything that needs
genuine judgment.

**Stage 4 — additional rule families.** Layer in further families
deliberately — `UP` (modernization, §21), `B` (bug-pattern detection),
`SIM` (simplification suggestions) — each introduced as its own
considered decision, not all at once.

**Stage 5 — CI enforcement.** Once local usage feels settled and the
number of *new* violations being introduced has genuinely dropped,
promote both the formatter check (§27) and the linter (§28) into a
required, blocking CI check (§26) — the point at which code quality
stops being "encouraged" and becomes structurally enforced.

**Stage 6 — stricter production policy.** For a maturing, long-lived
production codebase, continue expanding rule coverage deliberately
over time, tightening `per-file-ignores` (§18) as legacy exceptions
are genuinely resolved rather than left indefinitely, and treating the
Ruff configuration itself as a living document the team periodically
revisits.

**Why gradual adoption, rather than "enable everything on day one":**
**legacy code** — an existing codebase, written before Ruff was
adopted, will almost certainly contain a large number of pre-existing
violations under any sufficiently broad rule selection; **migration
cost** — fixing all of them at once is a large, disruptive undertaking
competing for time against actual feature work; **false positives**
(§36) — a broader rule selection increases the chance of encountering
a rule that doesn't fit a specific, legitimate pattern in your
codebase, each of which needs individual judgment to resolve
correctly; **developer friction** — introducing a large, unfamiliar
set of new failures all at once, with no ramp-up, breeds resentment
and workarounds rather than genuine buy-in; **rule noise** — a
selection so broad that most of its output is either false positives
or low-value nitpicks trains developers to stop actually reading
Ruff's output at all, defeating its entire purpose.

## 35. Legacy Project Migration

A practical, step-by-step strategy for introducing Ruff into an
**existing** Python project that has never used it before:

1. **Inspect the repository.** Understand its current size, structure
   (per this module's own
   [02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)
   chapter), and existing conventions before changing anything.
2. **Establish a baseline.** Run `ruff check .` (with Ruff's own
   default selection, or a small, deliberate starting selection) and
   simply *observe* how many violations exist, without fixing anything
   yet — this baseline count is your starting point for measuring
   progress.
3. **Format carefully.** Run `ruff format .` as its own, isolated,
   dedicated commit — reviewed on its own, kept entirely separate from
   any other change (§30), since a first-time reformat of an existing
   codebase can be a very large diff.
4. **Identify violations.** Review the baseline `ruff check .` output
   in full.
5. **Classify issues.** Sort violations into categories: genuinely
   safe to auto-fix (§11); requiring a small manual fix; requiring
   deeper investigation; or genuinely not applicable to this project
   (candidates for a deliberate, documented ignore, §16).
6. **Fix safe issues.** Apply `--fix` for the mechanically safe
   category, reviewed via `git diff`, ideally as its own dedicated
   commit separate from manual fixes.
7. **Configure justified exclusions.** For violations genuinely not
   applicable, add deliberate, documented `ignore`/`per-file-ignores`
   entries (§16, §18) — not as a way to hide unaddressed work, but as
   an honest, reviewed policy decision.
8. **Gradually enable rules.** Rather than enabling every remaining
   rule family at once, add them incrementally, addressing each new
   family's resulting violations before moving to the next (directly
   applying §34's staged adoption).
9. **Enforce in CI.** Once the local violation count has stabilized at
   a level the team is comfortable with, promote the checks into a
   required CI gate (§26, §28).

**Why blindly enabling hundreds of rules at once can create
unnecessary noise**: an existing, previously-unlinted codebase can
easily accumulate thousands of violations across a broad rule
selection — presenting all of them at once, with no way to
distinguish "genuinely important" from "minor style nitpick" from
"false positive," overwhelms rather than guides; a staged,
deliberate rollout (this section, and §34) turns an intimidating wall
of output into a manageable, prioritized body of work.

## 36. False Positives and Engineering Judgment

**A false positive** is a diagnostic Ruff reports that, on closer
inspection, does **not** actually represent a real problem in this
specific context — the rule's general pattern matched, but the
specific situation is a legitimate exception. **A false negative** is
the mirror image: a real problem that no currently-enabled rule
happened to catch at all. **Lint rule limitations**: every rule is,
fundamentally, a pattern-matching heuristic (per §4's static-analysis
foundation) — it cannot understand full context or intent the way a
human reviewer can, which means some rate of both false positives and
false negatives is an inherent, unavoidable property of any linter,
not a defect specific to Ruff.

**How engineers should respond to a suspected false positive, as a
deliberate sequence, not a reflex:**

1. **Understand the rule.** Read what the rule is actually designed to
   catch, and why — not just "it fired," but *what pattern* it's
   flagging and *why that pattern is usually worth flagging*.
2. **Inspect the context.** Does this specific occurrence genuinely
   fall outside what the rule is meant to catch, or does it actually
   represent exactly the kind of problem the rule exists to prevent,
   just not one you'd initially noticed?
3. **Decide whether the code or the configuration should change.** If
   the rule is correct and the code is genuinely the problem, fix the
   code. If the code is genuinely fine and the rule's general pattern
   simply doesn't apply to this legitimate case, then — and only
   then — consider a suppression.
4. **Suppress only when justified**, and do so at the narrowest
   possible scope (§16's scope hierarchy: inline, §17, before
   per-file, §18, before global, §16) — with a documented reason.

**Do not teach (or practice) blindly silencing warnings.** The
temptation to reach immediately for `# noqa` the moment a rule is
inconvenient is exactly the failure mode §17 and §28's "Legacy
Project Migration" both warn against — a suppression added without
genuinely working through steps 1–3 above is not engineering judgment,
it's just making the linter quieter without actually resolving
anything.

## 37. Performance and Scale

**Why fast tooling matters**, across every context where linting/
formatting actually gets run:

- **Local development** — a slow linter interrupts a developer's flow
  every time they want quick feedback; a fast one can be run
  constantly, almost without thinking about the cost.
- **Large repositories** — as a codebase grows to thousands of files,
  a linter's per-file overhead compounds; a linter with poor
  performance characteristics becomes a genuine bottleneck at scale,
  not just a minor annoyance.
- **Monorepos** (§38) — a single repository containing many packages
  multiplies this concern further.
- **CI/CD** — every CI run's total duration includes however long the
  linting/formatting steps take; a slow tool adds real, repeated cost
  across every single pull request, forever.
- **Pre-commit** (§25) — because pre-commit runs on *every single
  commit*, on a developer's own machine, a slow tool here directly and
  repeatedly interrupts the developer's own local workflow, more
  acutely than almost any other stage.

**Ruff's performance, at a high level, without unsupported benchmark
claims**: Ruff is specifically designed and implemented with
performance as a first-class engineering goal, which is a substantial
part of why it has been broadly adopted in place of older, separately-
composed toolchains — but this chapter deliberately does not cite
specific speed multipliers or benchmark numbers, since exact figures
depend heavily on codebase size, hardware, and the specific comparison
being made, and can become stale or misleading if stated as a
universal fact. **The engineering implication that matters,
regardless of exact numbers**: fast tooling changes what's *practical*
to run, *how often* — a genuinely fast linter/formatter can reasonably
run on every save, every commit, and every CI run without becoming a
practical burden on the development workflow, which is precisely the
condition every enforcement layer this chapter has covered (editor
integration, §23; pre-commit, §25; CI, §26) actually depends on to be
worth adopting at all.

## 38. Monorepos and Large Projects

A **monorepo** is a single repository containing multiple, distinct
Python packages/projects together, rather than one repository per
package. Several considerations change at this scale:

- **Multiple packages** — each package might reasonably want its own,
  slightly different rule selection (a library component held to
  stricter modernization standards than a legacy internal script
  living in the same repository, for instance).
- **Shared configuration** — a monorepo commonly wants a *baseline*
  Ruff configuration shared across every package, to avoid each one
  reinventing (and potentially disagreeing about) fundamental
  decisions like line length or quote style.
- **Repository-wide rules vs. package-specific exceptions** —
  `per-file-ignores` (§18) scales naturally to this: glob patterns can
  target a specific package's directory just as easily as a specific
  file type.
- **Generated code** (§19) — a monorepo often has more of this,
  proportionally, than a single-package project, and benefits
  correspondingly more from deliberate, well-organized exclusions.
- **CI scope** — a large monorepo's CI can often be optimized to only
  run checks against the specific packages actually affected by a
  given change, rather than the entire repository on every single
  pull request — though the exact mechanism for this is a CI-platform-
  specific concern, outside Ruff's own configuration itself.
- **Incremental adoption** — §34–§35's gradual-adoption strategy
  applies with even more force at monorepo scale, since a single "big
  bang" rule-selection change now potentially affects every team
  contributing to every package in the repository at once.

**A note on configuration organization**: this chapter deliberately
does not assert a specific mechanism for "configuration inheritance"
across multiple `pyproject.toml` files within one monorepo beyond what
this chapter has already firmly established (a single, project-root
`[tool.ruff]` configuration, per
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
own project-root conventions) — if your specific monorepo structure
requires per-package Ruff configuration beyond what `per-file-ignores`
and path-based exclusions can express, verify the exact, current
mechanism your installed Ruff version supports directly (per this
chapter's consistent commitment not to assert unverified behavior)
rather than assuming a specific inheritance model.

## 39. Library vs. Application

Directly extending
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
and
[04-dependency-management-and-semantic-versioning.md](04-dependency-management-and-semantic-versioning.md)'s
own library-vs-application distinctions into code-quality policy
specifically.

**Different Python project kinds, and reasonable strictness
differences:**

- **A published library** — its public API is a genuine, long-lived
  compatibility contract with external consumers (per
  [04-dependency-management-and-semantic-versioning.md](04-dependency-management-and-semantic-versioning.md)'s
  §6–§8 SemVer discussion); code quality here often warrants
  particularly strict naming (`N`) and modernization (`UP`, calibrated
  carefully against the library's own, possibly broad,
  `target-version` support matrix) discipline, since its code is read
  and depended upon by people outside the immediate team.
- **A backend service** — internally deployed, controlling its own
  runtime environment entirely; strictness can reasonably prioritize
  whatever the owning team finds genuinely valuable, calibrated
  against their own velocity needs.
- **A CLI tool** — similar to a backend service in most respects, with
  perhaps additional attention to the specific patterns this course's
  own Module 1.5 covered (argparse usage, exit codes, logging)
  benefiting from consistent style since they're used so pervasively
  throughout such a tool's own codebase.
- **A data pipeline** — often benefits particularly from strict
  correctness-adjacent rules (`F`, `B`) given how costly a silent data-
  processing bug can be to detect after the fact, compared to a purely
  cosmetic issue.
- **An ML project** — frequently involves a mix of exploratory
  (notebook-adjacent, rapidly-iterated) code and production-grade
  serving code; a reasonable policy often applies lighter rule
  selection to clearly-exploratory code paths and full production
  strictness to whatever actually ships and runs in a serving context.
- **An AI agent system** — combines CLI-like entry points, backend-
  service-like reliability needs, and rapidly-evolving logic; the same
  general principle applies: strictness should track how much a given
  piece of code's *correctness* actually matters operationally, not be
  applied uniformly by default regardless of context.

**Connecting this to your own long-term Applied AI Engineering goal**:
the projects this course is building you toward — data pipelines,
backend APIs serving models, agentic AI tooling — are exactly the
kind of production systems where a silent bug or an inconsistent,
hard-to-review codebase carries real operational cost. The habit this
chapter is building — formatting and linting as an automated,
non-negotiable baseline, layered underneath testing and type checking,
with strictness calibrated deliberately rather than either ignored or
maximized reflexively — is precisely the discipline that scales from a
small personal script all the way up to a production AI system many
people depend on.

## 40. Production AI/ML Project Example

A realistic project structure, directly extending
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
own production-oriented layout, now with Ruff woven through it:

```
ml-pipeline/
├── src/
│   └── ml_pipeline/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── data_processing.py
│       └── inference.py
├── tests/
│   ├── test_data_processing.py
│   └── test_inference.py
├── scripts/
│   └── explore_dataset.py
├── pyproject.toml
├── uv.lock
└── README.md
```

**`pyproject.toml`, showing Ruff configuration alongside the project's
own dependency declarations** (directly extending
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
own examples):
```toml
[project]
name = "ml-pipeline"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0,<3.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.5"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ruff.lint.per-file-ignores]
"tests/*.py" = ["F401"]
"scripts/*.py" = ["F401", "T20"]

[tool.ruff.format]
quote-style = "double"
```

**Demonstrating the workflow directly against this structure:**
```bash
uv run ruff format .              # consistent layout across src/, tests/, and scripts/
uv run ruff check .                 # lint the whole project
uv run ruff check --fix src/           # apply safe fixes, scoped to the core package
git diff                                 # review exactly what changed
uv run pytest                              # verify actual behavior, per §31
```

**How this applies to real data pipelines, backend APIs, ML services,
and agentic AI systems**: `data_processing.py` (a data pipeline
component) benefits especially from `F`/`B`'s correctness-adjacent
checks, given the cost of a silent data bug (§39); `inference.py` (an
ML-serving component, or the core of a backend API) benefits from the
same consistent formatting and import hygiene as any other production
module; `scripts/explore_dataset.py` (a one-off exploratory script,
per
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
§16) reasonably receives a looser `per-file-ignores` treatment,
reflecting that its purpose and lifecycle genuinely differ from the
core package's own reusable modules — exactly the deliberate,
justified-per-file-exception pattern §18 and §39 both established, now
applied concretely to a project shape directly relevant to this
course's own long-term direction.

## 41. Complete Professional Workflow

The full, end-to-end lifecycle, from a brand-new project through a
merged pull request:

1. **Create the project** — per
   [02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
   own project-layout guidance and
   [03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
   `uv init`.
2. **Add Ruff as a development dependency** — `uv add --dev ruff`
   (§7).
3. **Configure Ruff** — a deliberate, justified `[tool.ruff]`
   configuration in `pyproject.toml` (§15, §22).
4. **Write Python code** — the actual application logic.
5. **Run the formatter** — `uv run ruff format .` (§13).
6. **Run the linter** — `uv run ruff check .` (§8).
7. **Apply safe fixes** — `uv run ruff check --fix .` (§11), reviewed.
8. **Inspect the Git diff** — `git diff`, confirming every change is
   understood and intended (§11, §30).
9. **Run tests** — `uv run pytest` (§31) — verifying actual behavior,
   which neither formatting nor linting can do.
10. **Commit** — a clean, reviewed, atomic commit.
11. **Pre-commit checks** — an automatic, local gate re-verifying
    formatting/linting before the commit is even accepted (§25).
12. **Pull request** — the change is proposed for review, visible to
    teammates.
13. **CI runs Ruff** — `ruff format --check` and `ruff check`,
    independently, in a clean environment (§26–§28).
14. **CI runs tests** — the project's full automated test suite.
15. **Merge** — only once every gate (formatting, linting, tests) has
    passed, per the repository's own branch-protection policy (§26).

Every stage in this list maps directly to a specific section of this
chapter — this workflow is not a new idea introduced here at the end,
but the natural, complete assembly of everything §7 through §30
already taught individually.

## 42. Complete Example Project

**"Production-Style Python Code Quality Demo"** — walking one small
project through its full evolution, from intentionally problematic
code to a clean, enforced state.

**Starting structure:**
```
demo/
├── src/
│   └── demo/
│       ├── __init__.py
│       └── orders.py
├── tests/
│   └── test_orders.py
└── pyproject.toml
```

**`src/demo/orders.py`, initially — deliberately problematic:**
```python
import os
import json
from typing import List

class order_processor(object):
    def __init__(self,tax_rate=0.08):
        self.tax_rate=tax_rate

    def process(self, items):
        unused=1
        total=0
        for item in items:
            total+=item["price"]
        if total>0==True:
            total=total*(1+self.tax_rate)
        return total

def load_items(path) -> List[dict]:
    with open(path) as f:
        return json.loads(f.read())
```

**Step 1 — run the formatter:**
```bash
uv run ruff format .
```
Fixes spacing, consistent quote style, and layout — but changes
nothing about the *logic* problems still present.

**Step 2 — run the linter:**
```bash
uv run ruff check .
```
Conceptually reports:
```
orders.py:1:8: F401 `os` imported but unused
orders.py:5:23: UP004 class `order_processor` inherits from `object` unnecessarily
orders.py:5:7: N801 class name `order_processor` should use CapWords convention
orders.py:9:9: F841 local variable `unused` is assigned to but never used
orders.py:13:12: SIM201 use `total > 0` instead of `total > 0 == True`
orders.py:3:1: UP035 `typing.List` is deprecated, use `list` instead
```

**Step 3 — apply safe fixes, then review:**
```bash
uv run ruff check --fix .
git diff
```
This mechanically removes the unused `os` import, rewrites
`order_processor(object)` to drop the unnecessary `object` base, and
rewrites the redundant `== True` comparison — but leaves the
**unused variable** (`unused = 1`) and the **class naming** violation
(`N801`) for manual judgment, since renaming a class or deciding
whether an unused variable indicates a real bug both require actual
understanding of intent, not just mechanical rewriting (§11's own
principle, demonstrated concretely).

**Step 4 — manually address the remaining issues:**
```python
import json
from pathlib import Path


class OrderProcessor:
    def __init__(self, tax_rate: float = 0.08):
        self.tax_rate = tax_rate

    def process(self, items: list[dict]) -> float:
        total = 0.0
        for item in items:
            total += item["price"]
        if total > 0:
            total = total * (1 + self.tax_rate)
        return total


def load_items(path: Path) -> list[dict]:
    with path.open() as handle:
        return json.loads(handle.read())
```

**Step 5 — configure Ruff to keep the codebase at this standard going
forward:**
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "N"]

[tool.ruff.format]
quote-style = "double"
```

**Step 6 — run the tests**, confirming the cleanup changed nothing
about actual behavior:
```bash
uv run pytest
```

**Step 7 — the Git workflow**, exactly per §30 and §41:
```bash
git add src/demo/orders.py pyproject.toml
git commit -m "Introduce Ruff; fix lint violations and modernize orders.py"
```

This complete evolution — problematic code → formatted → linted →
safely auto-fixed → manually corrected → configured → tested →
committed — is the concrete, worked example every earlier section of
this chapter has been building toward in the abstract.

## 43. Debugging Lab

The following (fictional) file, `reports.py`, has several problems.
Diagnose each one before reading the answer key below it.

```python
import sys
import csv
from collections import OrderedDict

def Generate_Report(data,output_path='report.csv'):
    rows=[]
    total=0
    for row in data:
        if row['amount']==None:
            continue
        total+=row['amount']
        rows.append(row)
    with open(output_path,'w') as f:
        writer=csv.writer(f)
        for r in rows:
            writer.writerow(r)
    return totl  # bug
```

**Diagnose the following, before reading further:**
1. A formatting problem.
2. An unused import.
3. A naming-convention issue.
4. A suspicious comparison.
5. An undefined name.
6. A missing CSV-specific `open()` parameter (connecting to
   [03-csv-files.md](../05-Text-Files-Structured-Data-and-CLI-Programs/03-csv-files.md)'s
   own `newline=""` requirement — not a Ruff-specific rule, but a real
   correctness issue worth noticing during any code-quality pass).

**Answer key:**

1. **Formatting**: `def Generate_Report(data,output_path='report.csv'):`
   and `total+=row['amount']` both lack conventional spacing — the
   formatter (`ruff format`) resolves these automatically.
2. **Unused import (`F401`)**: `sys` is imported but never used
   anywhere in the file.
3. **Naming convention (`N802`-family, function naming)**:
   `Generate_Report` doesn't follow Python's conventional
   `lowercase_with_underscores` function-naming style — Ruff's `N`
   family would flag this.
4. **Suspicious comparison (`E711`)**: `row['amount']==None` should be
   `row['amount'] is None` — comparing to `None` with `==` is
   discouraged; `is` is the correct, idiomatic check for identity with
   the singleton `None`.
5. **Undefined name (`F821`)**: `return totl` references `totl`, which
   was never defined — `total` (defined earlier) was clearly intended;
   this is a genuine bug Ruff catches statically, without ever running
   the function.
6. **Missing `newline=""`**: `open(output_path, 'w')` should be
   `open(output_path, 'w', newline="")` for correct CSV writing,
   exactly per
   [03-csv-files.md](../05-Text-Files-Structured-Data-and-CLI-Programs/03-csv-files.md)'s
   own established requirement — a reminder that Ruff's own rule set,
   however broad, does not catch every correctness issue a careful,
   knowledgeable reviewer (or a dedicated CSV-specific check) might
   still need to catch.

**Corrected version:**
```python
import csv
from pathlib import Path


def generate_report(data, output_path="report.csv"):
    rows = []
    total = 0
    for row in data:
        if row["amount"] is None:
            continue
        total += row["amount"]
        rows.append(row)
    with Path(output_path).open("w", newline="") as handle:
        writer = csv.writer(handle)
        for r in rows:
            writer.writerow(r)
    return total
```

(`OrderedDict` was also removed — it was imported but never actually
used anywhere in the original file either, a second unused import
beyond `sys` worth catching in the same pass.)

## 44. Coding Exercises

**Level 1 — Basic**

1. Given a short snippet with inconsistent spacing around operators,
   identify every formatting problem by eye, then run `ruff format`
   on it and compare the result to your own prediction.
2. Run `ruff check .` against a small file containing one unused
   import and one unused variable; read and explain each diagnostic
   line in your own words.
3. Run `ruff format --check .` against an already-formatted file, and
   again after manually introducing one formatting inconsistency;
   explain the difference in output and exit code.
4. Explain, for a specific diagnostic Ruff produces, what the rule
   code's family prefix tells you before you even read the message.

**Level 2 — Intermediate**

5. Write a minimal `[tool.ruff]` configuration for a new project,
   including `line-length` and `target-version`, and justify each
   value you chose.
6. Add a `[tool.ruff.lint]` section selecting `E`, `F`, and `I`;
   explain what each family adds to the base configuration.
7. Add an `ignore` entry for one specific rule code, with a comment
   explaining why — then explain what would happen if you removed the
   comment.
8. Run `ruff check --fix` on a file with several fixable violations;
   use `git diff` to confirm exactly what changed, and identify which
   changes were "mechanical" versus anything you'd still want to
   review carefully.

**Level 3 — Advanced**

9. Design a `per-file-ignores` configuration for a project with
   `tests/`, `scripts/`, and a core `src/` package, justifying each
   entry.
10. Set `target-version` for a project that must support Python 3.10
    as its minimum, and explain what would go wrong if you set it to
    `py312` instead while the project's own `requires-python` still
    said `>=3.10`.
11. Design a step-by-step plan (using §35's migration strategy) to
    introduce Ruff into an existing, previously-unlinted 50-file
    project, including how you'd decide the *order* in which to
    enable additional rule families.
12. Design a team Ruff configuration policy document (a short written
    policy, not just a config file) explaining which rule families are
    required, which are optional, and how exceptions get approved.

**Level 4 — Production**

13. Design the exact CI workflow steps (as shell commands, in order)
    that would enforce both formatting and linting as required,
    blocking checks on every pull request.
14. Design a `pre-commit` integration plan for Ruff, explaining what
    should run at commit time versus what should be reserved for CI
    only, and why.
15. Describe a plan for migrating a legacy repository with an
    estimated 2,000 existing lint violations into full CI enforcement,
    including how you'd sequence the work across multiple pull
    requests.
16. Write a short production code-quality policy statement for a data
    pipeline project, specifying which rule families are mandatory
    given the cost of silent data-processing bugs (§39).

**Answer key**

1. Answers will vary by snippet; the key skill being tested is
   correctly predicting *before* running the tool — confirming your
   own understanding of §2's formatting rules, not just trusting the
   tool's output blindly.
2. A reasonable explanation names the rule code (e.g. `F401`), the
   specific name involved, the file/line location, and restates in
   plain language what the rule is checking for (§9–§10).
3. Against an already-formatted file: exit `0`, no output (nothing
   would change). After introducing an inconsistency: non-zero exit,
   and output naming the specific file that would be reformatted
   (§8, §27, §29).
4. E.g., an `F`-prefixed code signals a Pyflakes-derived, generally
   correctness-adjacent check; a `UP`-prefixed code signals a
   modernization suggestion — recognizing the family before reading
   the message tells you roughly what *category* of concern you're
   looking at (§9).
5. A reasonable answer picks a `line-length` matching the team's own
   preference (commonly 88–100) and a `target-version` matching the
   project's actual `requires-python` minimum, with justification tied
   to readability and actual deployment compatibility respectively
   (§15, §20, §22).
6. `E`/`F` add basic style and correctness-adjacent checks; `I` adds
   import sorting/organization (§9, §12).
7. The comment documents *why* the rule doesn't apply here, turning a
   silent policy decision into a reviewable, understandable one;
   without it, a future reader (including the original author, later)
   has no way to know whether the ignore is still justified or was
   simply never revisited (§16).
8. `git diff` should show only mechanical, provably-safe changes
    (e.g. an import removed, syntax modernized) if `--fix` was scoped
    correctly; anything touching logic or naming, per §11 and §42's
    worked example, still deserves a closer, deliberate look even
    after review, not just a glance.
9. A reasonable configuration ignores `F401` in `tests/*.py` (fixture
   imports) and in `scripts/*.py` (one-off, less strictly-held code),
   while keeping the core `src/` package under the project's full,
   default rule selection with no exceptions (§18).
10. Setting `target-version = "py312"` while the project still claims
    `requires-python = ">=3.10"` risks Ruff suggesting (or `--fix`
    silently applying) a modernization that assumes syntax only
    available in 3.12+ — which would then break for any user or
    deployment still running Python 3.10 or 3.11, a real,
    environment-specific bug introduced by a configuration mismatch
    (§20–§21).
11. A reasonable plan follows §35's nine-step sequence explicitly:
    baseline first, format as its own commit, classify remaining
    violations, fix safe ones, add justified exclusions, then add
    additional rule families one at a time — prioritizing families most
    likely to catch genuine bugs (`F`, `B`) before purely stylistic or
    modernization-focused ones (`UP`, `SIM`), so the earliest, most
    disruptive migration work delivers the highest-value catches first.
12. A reasonable policy document names the mandatory baseline
    (formatter, plus `E`/`F`/`I` at minimum), names which additional
    families are encouraged but not yet enforced, and describes a
    concrete process for proposing and approving a new `ignore` or
    `per-file-ignores` entry (e.g., requiring a comment and a specific
    reviewer's sign-off) — directly applying §16's "configuration
    encodes deliberate policy" principle as an actual team process.
13. A reasonable CI sequence:
    ```bash
    uv sync
    uv run ruff format --check .
    uv run ruff check .
    uv run pytest
    ```
    each step gating the next, exactly per §26–§29.
14. A reasonable plan runs the *fast*, low-friction checks (formatting,
    and perhaps only the fastest lint rules) at commit time via
    pre-commit, reserving the *full*, authoritative check (the complete
    rule selection, plus tests) for CI — reflecting §25's own
    distinction that pre-commit is a fast, locally-bypassable early
    layer, while CI is the un-bypassable, authoritative one.
15. A reasonable plan sequences the work across several pull requests
    rather than one enormous change: (1) formatter-only PR; (2) a PR
    fixing/ignoring `F`-family violations; (3) a PR addressing `B`;
    (4) subsequent PRs for each additional family; (5) a final PR
    enabling CI enforcement once the violation count has reached a
    genuinely manageable, agreed-upon baseline — directly applying
    §34's staged-adoption model at a scale requiring explicit
    sequencing across time.
16. A reasonable policy names `F` and `B` as mandatory (correctness-
    adjacent, directly protecting against the kind of silent data bug
    §39 specifically calls out as costly for a data pipeline), with
    `UP`/`SIM`/`N` as encouraged but not blocking, tying the reasoning
    explicitly back to the operational cost of an undetected data-
    processing bug versus a purely stylistic inconsistency.

## 45. Mini Project — Production-Ready Python Code Quality Pipeline

**Requirements**: design (as code snippets and configuration inside
this document — no actual files are created) a small Python project
demonstrating the complete pipeline this chapter has taught, from
intentionally broken code through full CI-oriented enforcement.

**Project structure:**
```
quality-demo/
├── src/
│   └── quality_demo/
│       ├── __init__.py
│       └── inventory.py
├── tests/
│   └── test_inventory.py
├── pyproject.toml
├── uv.lock
└── README.md
```

**`src/quality_demo/inventory.py`, with intentional problems
introduced deliberately:**
```python
import sys
import json

def Check_Stock(items,threshold=5):
    low_stock=[]
    for item in items:
        if item['quantity']<threshold:
            low_stock.append(item)
    return low_stock

def save_report(data, path):
    f=open(path,'w')
    f.write(json.dumps(data))
    f.close()
```

**Detecting the problems:**
```bash
uv add --dev ruff
uv run ruff check .
```
Conceptual diagnostics: `F401` (`sys` unused), `N802` (`Check_Stock`
naming), formatting violations (spacing), and a resource-handling
concern (`f = open(...)` with no context manager — connecting directly
back to
[01-reading-and-writing-text-files.md](../05-Text-Files-Structured-Data-and-CLI-Programs/01-reading-and-writing-text-files.md)'s
own §21 context-manager guidance; whether a specific Ruff rule flags
this exact pattern depends on your enabled rule selection, but it's
worth fixing regardless, as a matter of the correctness principles
this whole course has built, not only whatever any one linter happens
to catch).

**Fixing:**
```bash
uv run ruff format .
uv run ruff check --fix .
git diff
```

**Manually addressing what `--fix` correctly leaves for judgment:**
```python
import json
from pathlib import Path


def check_stock(items, threshold=5):
    low_stock = []
    for item in items:
        if item["quantity"] < threshold:
            low_stock.append(item)
    return low_stock


def save_report(data, path):
    with Path(path).open("w") as handle:
        handle.write(json.dumps(data))
```

**Configuring the project for ongoing enforcement:**
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "N"]

[tool.ruff.lint.per-file-ignores]
"tests/*.py" = ["F401"]

[tool.ruff.format]
quote-style = "double"
```

**Running tests:**
```bash
uv run pytest
```

**Inspecting changes and committing:**
```bash
git add src/ pyproject.toml
git commit -m "Add Ruff; fix formatting, naming, and unused imports; use context manager for file I/O"
```

**A CI-oriented check, as the project's own enforcement layer going
forward:**
```bash
uv sync
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

This mini project deliberately exercises every major stage this
chapter has taught: introducing realistic problems, detecting them,
distinguishing mechanical fixes from judgment calls, configuring rule
selection and per-file exceptions deliberately, and finishing with the
exact CI-shaped command sequence a real pull request would need to
pass.

## 46. Common Beginner Mistakes

1. **Thinking formatter and linter are the same tool/concept.** *Why
   it happens:* Ruff conveniently provides both, so the distinction can
   blur. *Why problematic:* leads to confusion about what each command
   actually does and doesn't check (§5, §14). *Better approach:* keep
   §5's table firmly in mind — formatting is layout; linting is
   pattern-based problem detection.
2. **Thinking Ruff replaces tests.** *Why it happens:* Ruff catches a
   genuinely large, useful category of problems, which can create a
   false sense of complete coverage. *Why problematic:* §31's `average()`
   example — a perfectly "clean" Ruff report says nothing about
   whether the logic is actually correct. *Better approach:* always
   run tests; never treat a clean lint report as equivalent to
   verified correctness.
3. **Blindly using `--fix` without reviewing changes.** *Why it
   happens:* it feels efficient to trust an automated tool completely.
   *Why problematic:* even "safe" fixes deserve verification (§11);
   trusting blindly means committing changes you haven't actually
   looked at. *Better approach:* always `git diff` after `--fix`,
   every time, without exception.
4. **Disabling rules instead of fixing the underlying code.** *Why it
   happens:* an ignore is faster than actually addressing a violation.
   *Why problematic:* accumulates hidden problems rather than resolving
   them, and erodes the actual value of linting over time (§16, §36).
   *Better approach:* work through §36's judgment sequence before ever
   reaching for a suppression.
5. **Using too many ignores.** *Why it happens:* often the accumulated
   result of mistake 4, repeated many times. *Why problematic:* a
   long, undocumented ignore list makes it impossible to tell
   deliberate policy from unaddressed technical debt (§16). *Better
   approach:* document every ignore's justification; periodically
   review whether it's still needed.
6. **Putting generated files under ordinary linting.** *Why it
   happens:* forgetting that a specific directory's contents aren't
   hand-written source code. *Why problematic:* wastes effort "fixing"
   code that will be silently overwritten on the next regeneration
   (§18–§19). *Better approach:* exclude generated code explicitly via
   `exclude`/`extend-exclude`.
7. **Not committing the Ruff configuration.** *Why it happens:*
   treating `pyproject.toml`'s `[tool.ruff]` section as a personal,
   local preference rather than a shared project standard. *Why
   problematic:* recreates exactly the inconsistency
   [03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
   entire chapter fought against — different developers/CI using
   different, unrecorded configurations. *Better approach:* always
   commit `pyproject.toml`'s Ruff configuration alongside everything
   else.
8. **Relying only on editor checks.** *Why it happens:* editor
   feedback feels sufficient day to day. *Why problematic:* depends
   entirely on every contributor having correctly configured tooling,
   with nothing catching a lapse (§23). *Better approach:* always back
   editor integration with pre-commit and, critically, CI (§25–§26).
9. **Skipping CI validation.** *Why it happens:* trusting that local
   checks were "probably" run. *Why problematic:* removes the one
   enforcement layer that can't be bypassed by an individual
   developer's local setup or oversight (§26). *Better approach:*
   always gate merges on an independent CI check.
10. **Ignoring the target Python version.** *Why it happens:*
    forgetting `target-version` exists, or letting it drift out of sync
    with `requires-python`. *Why problematic:* risks modernization
    suggestions (or auto-fixes) that assume syntax unavailable on the
    project's actual minimum supported Python (§20–§21). *Better
    approach:* keep `target-version` and `requires-python` deliberately
    aligned.
11. **Changing formatting manually during code review.** *Why it
    happens:* an old habit from before an automated formatter was
    adopted. *Why problematic:* reintroduces exactly the unproductive,
    inconsistent debate the formatter exists to eliminate (§2, §13).
    *Better approach:* let the formatter make every formatting
    decision; reserve human review for logic and design.
12. **Not reviewing automatic changes.** *Why it happens:* the same
    root cause as mistake 3, generalized beyond just `--fix` to
    `ruff format` itself. *Why problematic:* even "safe," deterministic
    tools can occasionally surprise you, especially the first time
    they run against previously-unformatted code (§30). *Better
    approach:* `git diff`, always, before committing any automated
    change.
13. **Introducing too many rules at once.** *Why it happens:*
    enthusiasm after learning about Ruff's full rule catalog. *Why
    problematic:* overwhelms a team (or a legacy codebase) with more
    violations than can be reasonably triaged at once, breeding
    friction and workarounds rather than genuine adoption (§34–§35).
    *Better approach:* adopt gradually, one deliberate stage at a time.

## 47. Production Code-Quality Checklist

- [ ] Ruff is installed as a project development dependency (`uv add
      --dev ruff`), not installed globally.
- [ ] Ruff's configuration is committed in `pyproject.toml`, shared by
      the whole team and CI alike.
- [ ] The formatter is configured deliberately (`line-length`,
      `format.quote-style`, and similar settings chosen and justified).
- [ ] Linting is configured deliberately (`lint.select`, and any
      `lint.ignore`, each with a stated reason).
- [ ] Rules are intentionally selected, not left at an unreviewed
      default nor maximized reflexively.
- [ ] Unnecessary or undocumented ignores are avoided; every ignore
      that exists has a clear, stated justification.
- [ ] Generated files, vendor code, build output, and virtual
      environments are appropriately excluded (`exclude`/
      `extend-exclude`).
- [ ] `target-version` is set and kept consistent with the project's
      own `requires-python`.
- [ ] Local checks are readily available to every developer (via
      `uv run ruff format`/`ruff check`, and/or editor integration).
- [ ] Editor/IDE integration is in place for immediate, in-context
      feedback (§23–§24), understood as a convenience layer, not the
      sole enforcement mechanism.
- [ ] Pre-commit is configured to catch formatting/lint issues before
      a commit is even created (§25).
- [ ] CI independently runs `ruff format --check` and `ruff check`,
      gating merges on both (§26–§28).
- [ ] Tests run as their own, separate pipeline stage — never
      conflated with or substituted by linting (§31).
- [ ] Automated changes (`ruff format`, `ruff check --fix`) are always
      reviewed via `git diff` before committing (§11, §30).
- [ ] The whole environment (including Ruff's own pinned version) is
      reproducible via the committed `uv.lock` (§7, connecting to
      [03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)).
- [ ] The project's Ruff configuration and its rationale are
      documented somewhere the whole team can reference (a comment in
      `pyproject.toml`, a short policy note in `README.md`, or
      equivalent).

## 48. Interview Questions

**Beginner**
1. What is formatting?
2. What is linting?
3. What is Ruff?
4. What is a formatter, precisely?
5. What is a linter, precisely?

**Intermediate**
6. Ruff vs. a separate formatter tool (e.g. Black) — what's the
   practical relationship, conceptually?
7. Ruff vs. a separate, older linter (e.g. Flake8) — what's the
   practical relationship, conceptually?
8. Why does Ruff's configuration live in `pyproject.toml`?
9. What does `ruff check` do?
10. What does `ruff format` do?
11. What does `--fix` do?

**Advanced**
12. How would you introduce Ruff into a legacy project?
13. How would you design a project's rule selection?
14. How would you prevent lint-suppression abuse on a team?
15. How would you integrate Ruff into CI?
16. How would you handle generated code with respect to linting?

**Production**
17. Design a code-quality pipeline for a large Python repository.
18. How would you balance strictness and developer velocity?
19. How would you migrate thousands of existing violations?
20. How would you enforce code quality consistently across multiple
    teams?
21. What should Ruff be responsible for, versus type checking and
    testing?

**Answer key**

1. The consistent visual/textual arrangement of code (spacing, line
   breaks, quote style) with no effect on behavior (§2).
2. Static analysis of source code to detect suspicious patterns,
   dead code, and likely mistakes, without executing the program (§4).
3. A modern Python tool providing both a fast linter and a fast
   formatter in one program (§6).
4. A program that rewrites source code into a consistent, canonical
   layout, deterministically and without changing behavior (§3).
5. A program that analyzes source code (without running it) to
   report violations of specific, named rules (§4).
6. Ruff's own formatter is designed to be broadly compatible with the
   kind of opinionated, deterministic output tools like Black
   produce — conceptually, Ruff's formatter fills the same *role* a
   separate formatter tool would, now built into the same tool as the
   linter, reducing the number of separate tools a project needs (§6,
   §13).
7. Ruff's linter re-implements (and extends) much of the functionality
   historically provided by Flake8 and its many separate plugins,
   consolidated into one fast tool, drastically reducing the number of
   separate dependencies and configuration sections a project needs to
   maintain (§6, §9).
8. Because `pyproject.toml` is the standardized, project-root
   configuration file this whole module has established as the home
   for a Python project's metadata, dependencies, and tool
   configuration together — Ruff follows this same, shared convention
   rather than requiring its own separate configuration file (§15,
   connecting to
   [03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
   §3).
9. Runs the linter, reporting every lint violation found, without
   modifying any files (§8).
10. Rewrites files in place to match Ruff's consistent formatting
    rules (§8).
11. Automatically rewrites code to resolve lint violations that have a
    known-safe correction, for the subset of rules that support it
    (§11).
12. Following §35's staged plan: establish a baseline, format as its
    own isolated commit, classify and gradually address violations,
    add justified exclusions, expand rule coverage incrementally, and
    only then promote checks into required CI enforcement.
13. Start from a small, well-understood, easily-justified selection
    (`E`, `F`, `I`, perhaps `UP`), and expand deliberately over time,
    with each additional family chosen for a specific, stated reason
    rather than maximized reflexively (§9, §22, §34).
14. Require rule-specific (never bare) `# noqa` suppressions,
    accompanied by a comment explaining the justification, and treat
    any suppression as something requiring the same review scrutiny as
    any other code change — combined with a documented team policy for
    when a suppression is (and isn't) appropriate (§16–§17, §36, §44
    exercise 12).
15. Run `uv sync`, then `ruff format --check .` and `ruff check .`, as
    required, independently-gating steps in the CI pipeline, before
    tests and build/deploy stages (§26–§29).
16. Exclude it entirely from linting/formatting via `exclude`/
    `extend-exclude`, rather than manually editing it to satisfy rules
    it will simply be regenerated past on the next run (§18–§19).
17. A reasonable design: local editor integration for immediate
    feedback → pre-commit for a fast, early local gate → CI running
    `ruff format --check`, `ruff check`, a type checker, and the test
    suite as independent, required gates → branch protection requiring
    all of them to pass before merge (§23–§28, §41).
18. Calibrate rule selection and strictness to the project's actual
    risk profile (§39) rather than either extreme; adopt new rules
    gradually (§34) so developer friction stays proportional to actual
    value delivered, and invest in fast tooling (§37) so quality checks
    never become a practical bottleneck to velocity in the first
    place.
19. Following §35's and §44 exercise 15's staged migration:
    baseline, format-only commit, then incremental, family-by-family
    remediation across multiple pull requests, sequenced by
    correctness-impact (highest-value families first), only enforcing
    in CI once the remaining count is genuinely manageable.
20. A shared, committed, root-level Ruff configuration (§15, §38) as
    the common baseline, with narrowly-scoped, documented
    `per-file-ignores` (§18) for legitimate team- or package-specific
    exceptions, enforced uniformly through the same CI gate for every
    team's contributions (§26).
21. Ruff: formatting consistency and pattern-based static
    correctness/style checks. Type checking: cross-codebase type
    consistency. Testing: actual runtime behavior against known,
    expected outcomes. Each is necessary; none substitutes for another
    (§5, §31–§32).

## 49. Architecture Questions

1. **Where does Ruff belong in a CI/CD pipeline?** Early — before
   tests and build/deploy — since formatting/lint failures are cheap
   and fast to detect, and there's little value running slower stages
   (tests, builds) against code that hasn't even passed basic quality
   checks yet (§26, §29).
2. **Should formatting happen locally or in CI?** Both, in different
   roles: **locally**, the developer actually applies formatting
   (`ruff format .`, ideally via format-on-save or pre-commit);
   **in CI**, only *verification* (`ruff format --check`) happens —
   CI should never be the first place formatting is actually applied
   (§27).
3. **Should CI automatically modify code (e.g., auto-commit
   formatting fixes)?** Generally no, for the reason §27 gives
   directly: it removes the author's direct visibility and review over
   changes to their own pull request, undermining reviewability — CI's
   role is to verify and gate, not to silently rewrite.
4. **How should a monorepo manage Ruff configuration?** A shared,
   root-level baseline configuration, with `per-file-ignores` (or
   path-scoped patterns) expressing legitimate, package-specific
   exceptions — verified against your specific Ruff version's actual
   supported mechanisms rather than assumed (§38).
5. **How should legacy services adopt Ruff?** Gradually, following
   §35's staged migration — baseline, isolated formatting commit,
   incremental rule adoption, CI enforcement only once the remaining
   violation count is manageable — never as a single, disruptive,
   all-at-once change.
6. **How should AI/ML repositories enforce consistent code quality?**
   By calibrating rule strictness to each component's actual
   operational risk (§39–§40) — correctness-adjacent rules (`F`, `B`)
   applied firmly to data-processing and serving code, with lighter
   treatment for genuinely exploratory scripts — enforced uniformly
   through the same CI gate every other production Python project in
   this course's trajectory would use.

## 50. Knowledge Check

1. What is the difference between a formatter and a linter?
2. What is static analysis, and how does it differ from actually
   running a program?
3. What is Ruff, in one sentence?
4. What is a Ruff rule, and what is a rule family?
5. What is a diagnostic?
6. What does `--fix` do, and what should you always do immediately
   after using it?
7. What is the purpose of formatting specifically, as distinct from
   linting?
8. Where does Ruff's configuration live, and what is the modern
   location for `select`/`ignore` specifically?
9. What is rule selection, and what is rule ignoring?
10. What are per-file ignores, and name one legitimate reason to use
    them.
11. What does `target-version` control?
12. What is `pre-commit`, and how does it differ from CI?
13. What does CI verify independently, and why does that matter?
14. What does a non-zero exit code from `ruff check` signal to an
    automated pipeline?
15. Describe a realistic Git workflow incorporating Ruff.
16. Give an example of something Ruff cannot catch that testing can.
17. Give an example of something Ruff cannot catch that a type checker
    can.
18. What are production workflows expected to include beyond just
    running Ruff locally?

**Answer key**

1. A formatter changes code's *layout* only, with no effect on
   behavior; a linter *detects* problems (dead code, likely bugs,
   style issues) without changing anything, by default (§2–§5).
2. Static analysis examines source code's text/structure without
   executing it; running a program actually exercises its logic
   against real inputs, which is what testing (not linting) does
   (§4, §31).
3. A modern Python tool combining a fast linter and a fast formatter
   in one program (§6).
4. A rule is one specific, named check; a rule family is a group of
   related rules sharing a common code prefix and origin/category
   (e.g. `F` for Pyflakes-derived checks) (§9).
5. The message Ruff produces for one specific violation, naming the
   rule, its location, and a short explanation (§4, §9).
6. It automatically rewrites code to resolve fixable violations; you
   should always run `git diff` immediately afterward to review
   exactly what changed (§11).
7. Formatting exists purely for consistent, readable layout; it says
   nothing about whether code is correct, unused, or well-designed —
   that's linting's (and other tools') job (§2, §5).
8. `pyproject.toml`, under `[tool.ruff]`; the modern location for
   `select`/`ignore` is the nested `[tool.ruff.lint]` table, not
   directly under `[tool.ruff]` as in older, legacy configurations
   (§15).
9. Rule selection (`select`) chooses which rule codes/families are
   active; rule ignoring (`ignore`) turns specific rules off from
   within that active set (§16).
10. Configuration exceptions scoped to specific file patterns; a
    legitimate reason is `tests/*.py` legitimately needing an
    exception for fixture imports that would otherwise trigger an
    "unused import" violation (§18).
11. Which Python version(s) Ruff should assume are available,
    affecting which syntax/modernization suggestions are valid to make
    (§20).
12. A framework running automated checks immediately before a Git
    commit, on the developer's own machine; unlike CI, it runs locally
    and can, in principle, be bypassed by the developer, whereas CI
    runs on a shared, controlled server and cannot be bypassed by any
    individual's local choices (§25).
13. CI independently re-runs formatting/lint checks (and tests) in a
    clean, reproducible environment, regardless of what any individual
    developer's local setup did or didn't do — this matters because
    local setups can be inconsistent, outdated, or simply skipped
    (§26).
14. Failure — at least one violation exists under the project's
    current rule selection, and the pipeline stage (and typically the
    whole CI run) should be treated as failed (§28–§29).
15. Edit code → `ruff format .` → `ruff check --fix .` → review
    `git diff` → run tests → commit (§30, §41).
16. A logical bug that produces the wrong output for valid input (e.g.
    an incorrect arithmetic formula) — syntactically and structurally
    fine, but factually wrong; only running the code against known
    expected results (a test) reveals it (§31).
17. A value whose declared type could legitimately be `None` being
    passed to a function that requires a non-`None` value — a
    cross-function type-consistency issue Ruff's linter does not
    perform the deep analysis needed to catch (§32).
18. Editor integration for immediate feedback, pre-commit for an early
    local gate, and — critically — independent CI enforcement gating
    merges, alongside the project's own test suite and (where used) a
    type checker (§23–§32, §41, §47).

## 51. Glossary

- **Formatter** — a tool that rewrites source code into a consistent,
  deterministic layout, without changing its behavior (§3).
- **Linter** — a tool that statically analyzes source code to detect
  suspicious patterns, dead code, and likely mistakes, without
  executing the program (§4).
- **Lint rule** — one specific, named check a linter can perform,
  identified by a rule code (§9).
- **Diagnostic** — the message produced for one specific violation of
  a rule, naming the rule, location, and explanation (§4, §9).
- **Static analysis** — examining source code's text/structure without
  executing it (§4).
- **Code quality** — how easy a codebase is to read, trust, and change
  safely, as distinct from merely whether it runs (§1).
- **Auto-fix** — automatically rewriting code to resolve a lint
  violation with a known-safe correction (`ruff check --fix`, §11).
- **Rule family** — a group of related lint rules sharing a common
  code prefix and origin/category (e.g. `F`, `UP`, `B`) (§9).
- **Suppression** — silencing one specific occurrence of a violation
  directly in the source code (e.g. `# noqa: F401`) (§17).
- **`noqa`** — the inline comment convention used to suppress a
  specific lint violation on a specific line (§17).
- **`pyproject.toml`** — the standardized project configuration file
  holding, among other things, Ruff's own configuration under
  `[tool.ruff]` (§15).
- **Pre-commit** — a framework running automated checks immediately
  before a Git commit is created, on the developer's own machine
  (§25).
- **CI (Continuous Integration)** — an automated system that
  independently verifies code quality (formatting, linting, tests) on
  every push/pull request, in a clean, reproducible environment (§26).
- **Exit code** — the numeric status a command reports on completion;
  `0` for success, non-zero for failure, used by automation to gate
  pipelines (§29, connecting to
  [07-standard-streams-and-exit-codes.md](../05-Text-Files-Structured-Data-and-CLI-Programs/07-standard-streams-and-exit-codes.md)).
- **Target Python version** — the minimum Python version a project
  supports, configured via `target-version`, affecting which syntax/
  modernization suggestions Ruff considers valid (§20).
- **Generated code** — code produced automatically by another tool,
  which should generally be excluded from linting/formatting rather
  than manually edited (§18–§19).
- **False positive** — a diagnostic that fires but doesn't actually
  represent a real problem in its specific context (§36).
- **False negative** — a real problem that no currently-enabled rule
  happened to catch (§36).
- **Technical debt** — the accumulated cost of unresolved code-quality
  issues (excessive ignores, unaddressed violations, inconsistent
  style) deferred rather than fixed, which tends to compound and
  become more expensive to address the longer it's left unattended
  (§16, §34–§36).

## 52. Final Mental Model

```
WRITE CODE
    ↓
FORMAT CODE            (consistent layout — protects against style debate and inconsistency)
    ↓
LINT CODE                (structural/pattern checks — protects against dead code, likely bugs, style drift)
    ↓
FIX SAFE ISSUES            (mechanical corrections, always reviewed — protects against repetitive manual toil)
    ↓
REVIEW CHANGES                (git diff — protects against blindly trusting automation)
    ↓
TYPE CHECK                        (cross-codebase type consistency — protects against type-mismatch bugs)
    ↓
TEST                                (actual behavior verification — protects against logical/correctness bugs)
    ↓
COMMIT                                (a clean, reviewed, atomic unit of change)
    ↓
CI VALIDATION                            (independent, un-bypassable re-verification of everything above)
    ↓
MERGE
    ↓
DEPLOY
```

Each layer protects against a category of problem the layers around it
structurally cannot: formatting protects against inconsistency (never
correctness); linting protects against a broad class of pattern-based
problems (never deep type mismatches or logical errors); type checking
protects against type-flow mistakes (never arbitrary logic errors);
testing protects against logical/behavioral mistakes (only for what's
actually tested); and CI protects against the possibility that any of
the above was skipped, misconfigured, or run against the wrong
environment anywhere upstream of it. No single layer is sufficient by
itself — the whole pipeline, run consistently, is what actually
delivers production-grade Python code quality.

## Final Takeaways

Ruff gives a Python project two of the cheapest, fastest, highest-
leverage quality-assurance layers available: consistent formatting and
broad, pattern-based linting — both automatable, both nearly free to
run constantly, and both capable of eliminating entire categories of
unproductive debate and preventable mistakes from a team's daily
work. None of that makes Ruff a substitute for the judgment, testing,
and type-checking discipline the rest of this course (and this
module's own later chapters) continues to build — it is, precisely and
only, the fast, automated foundation layer everything else in a
production Python workflow sits on top of. The habit worth carrying
forward from this chapter is not "run Ruff" as an isolated command,
but the complete mental model in §52: write, format, lint, fix, review,
type-check, test, commit, validate, merge, deploy — each step earning
its place by catching something none of the others can.
