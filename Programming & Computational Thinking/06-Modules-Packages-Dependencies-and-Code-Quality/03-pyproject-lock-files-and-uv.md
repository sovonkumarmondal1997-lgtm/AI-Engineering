# `pyproject.toml`, Lock Files, and `uv`

## Learning Objectives

By the end of this chapter you will be able to:

- Explain what a dependency is, and distinguish direct dependencies
  from transitive ones.
- Explain why unmanaged dependencies cause real, recurring engineering
  problems ("works on my machine," broken deployments, silent version
  drift).
- Read and write a `pyproject.toml` file's `[project]` table, including
  `name`, `version`, `description`, `readme`, `requires-python`,
  `dependencies`, and `optional-dependencies` — with enough TOML
  literacy to understand the syntax, not just copy it.
- Read and write Python version specifiers (`>=`, `>`, `==`, `<=`,
  `<`, `~=`, and ranges like `>=2,<3`), and explain the tradeoffs
  between an exact pin, a minimum version, a bounded range, and a
  compatible-release specifier.
- Explain what a dependency resolver does, using a concrete
  conflicting-constraints example, and diagnose a resolution failure.
- Explain virtual environments conceptually, and why per-project
  isolation matters.
- Explain what a lock file is and why it exists, and state precisely
  how `pyproject.toml` (what the project *requires*) differs from
  `uv.lock` (which exact versions were *resolved* and should be
  installed).
- Use `uv` as a project/dependency manager: `uv init`, `uv add`,
  `uv remove`, `uv sync`, `uv run`, and `uv lock` — understanding what
  each command actually changes (the `pyproject.toml`, the `uv.lock`,
  and/or the environment).
- Distinguish runtime dependencies from development dependencies, and
  declare each correctly.
- Explain optional dependencies ("extras") conceptually.
- Explain how a lock file supports reproducibility across developers,
  CI/CD, containers, and production deployments.
- Explain the tradeoffs between application and library dependency
  strategies.
- Reason about dependency security: outdated packages, transitive
  vulnerabilities, and the risks of both never updating and blindly
  updating everything.
- Recognize and avoid the classic dependency-management mistakes.
- Design a small, reproducible, production-oriented Python CLI project
  using `pyproject.toml` and `uv` from end to end.

## Prerequisites

This chapter builds on
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
distinction between standard-library, local, and third-party imports,
and on
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
project structure (`src/` layout, `pyproject.toml` at the project
root, `tests/` placement) — this chapter is what actually fills in
`pyproject.toml`'s dependency-related content, and introduces the tool
(`uv`) used to manage it day to day. No prior packaging or TOML
knowledge is assumed.

**A note on command behavior:** `uv` is an actively developed tool, and
exact flag names or defaults can shift between versions. This chapter
teaches the underlying *concepts* and the *stable, well-established*
commands (`init`, `add`, `remove`, `sync`, `run`, `lock`) precisely —
where a specific detail might vary by installed version, that is
called out explicitly, with the instruction to verify against
`uv --help` or the currently installed version rather than assuming.

## Core Mental Model

Before any syntax, fix the shape of the whole system this chapter
teaches:

```
pyproject.toml
    ↓
Project requirements / declared dependencies
    ↓
Dependency resolver
    ↓
Resolved dependency graph
    ↓
uv.lock
    ↓
Reproducible environment
    ↓
Installed packages / application
```

- **`pyproject.toml`** describes **what the project requires** —
  "I need `requests`, version 2 or later" — written by a human,
  intentionally loose enough to allow reasonable flexibility.
- The **dependency resolver** (built into `uv`) takes those
  requirements, plus every dependency's *own* requirements
  (transitive dependencies, §9), and works out one specific, mutually
  compatible set of exact versions that satisfies all of them at once.
- **`uv.lock`** records **which resolved versions** that process
  produced — not what the project merely *requires*, but the *precise,
  reproducible answer* the resolver already worked out, for the
  environments the project supports.
- The **environment** (a virtual environment, §12) is where those
  exact, locked versions actually get installed, ready for the
  application to import and run.

The single sentence to hold onto through the rest of this chapter:
**`pyproject.toml` and `uv.lock` have different jobs.** One is a
human-authored statement of intent; the other is a machine-generated,
exact, reproducible record of one specific solution to that intent.
Confusing the two — editing `uv.lock` by hand, or expecting
`pyproject.toml` alone to guarantee reproducibility — is the root
cause of most of the debugging scenarios in §36.

## 1. What Is a Dependency?

A **dependency** is external code your project needs in order to run,
that isn't part of the Python standard library and isn't code you
wrote yourself. This directly extends
[01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s §26
three-way distinction (standard-library / local / third-party) — a
dependency is specifically the *third-party* category, now considered
as something that must be explicitly **declared and managed**, not
just imported.

```python
import requests   # this import statement is only possible if `requests` is installed
```

**Library/package** — a `requests`-style piece of published code your
project imports and calls into. **Direct dependency** — something
*your own project* explicitly declares and relies on (most often because
its code imports it). A literal `import` is the common case, not the
universal definition: a plugin, a runtime-discovered component, a
command-line tool, or a framework integration can also be a direct
dependency without any simple static `import` of it. **Transitive
dependency** — something *one of your dependencies* itself relies on,
which your project therefore also needs, without ever importing it
directly:

```
my_project
    ↓ (direct dependency)
  requests
    ↓ (requests' OWN dependencies — transitive, from my_project's perspective)
  urllib3, certifi, idna, charset-normalizer
```

`my_project` never writes `import urllib3` anywhere in its own code —
but it still needs `urllib3` installed, correctly, and at a version
`requests` is compatible with, purely because `requests` depends on
it. §9 develops this distinction fully; it's introduced here because
it's the reason dependency management is a genuinely nontrivial
problem, not just "list the packages you import."

**Why applications depend on external packages at all**: writing an
HTTP client, a CSV parser with every edge case handled, or a
cryptography library completely from scratch is enormous, error-prone
work that thousands of other projects have already solved (often
better, and more securely, than a from-scratch attempt would manage).
Depending on well-maintained third-party packages is a deliberate,
sensible engineering tradeoff — but every dependency taken on is also
a piece of *someone else's* code your project now needs to track,
update, and trust, which is exactly why **dependency management**
becomes a real discipline as a project grows past a handful of
imports.

## 2. Why Dependency Management Exists

A concrete, realistic scenario makes the problem vivid before any
tooling is introduced.

Two developers, Alex and Priya, both work on the same project. Alex
installed `pandas` eight months ago — whatever the latest version was
then. Priya joins the team today and runs `pip install pandas` —
getting whatever the latest version is *now*, which may have changed
its API in ways the project's code doesn't expect.

**Problems this causes, concretely:**

- **"Works on my machine"** — Alex's code runs fine locally; Priya's
  identical checkout fails, because they're actually running against
  two different versions of the same dependency, with no record
  anywhere of which version is the "correct" one.
- **Incompatible packages** — two of the project's dependencies might
  each require conflicting versions of a *third*, shared dependency
  (§11 works through this concretely).
- **Accidental upgrades** — installing without a recorded set of
  versions means a *new* environment (or a newly installed package) gets
  whatever is newest at that moment, and an unreviewed `pip install
  --upgrade` (or a new dependency that requires a newer version) can
  change something already installed — changing behavior with no
  corresponding code change to explain why. (A plain `pip install
  package` does not upgrade a package that is already installed and
  satisfies the request.)
- **Missing packages** — a developer manually `pip install`s something
  to make their own environment work, forgets to record it anywhere,
  and the next person's environment is missing it entirely.
- **Difficult deployment** — a production server, built independently
  of any developer's laptop, has no way to know which exact versions
  were actually tested, absent some explicit record.
- **Difficult reproduction** — a bug report says "it happens in
  production" but no one can recreate the *exact* dependency versions
  production is actually running, on a local machine, to investigate.
- **Security/update management problems** — with no clear record of
  what's installed and why, deciding when (and how safely) to update a
  dependency with a known vulnerability becomes guesswork.

Every one of these problems has the same underlying cause: **no
explicit, shared, machine-readable record of exactly which
dependencies — and which exact versions — the project actually
depends on.** This chapter's remaining sections build exactly that
record, in two complementary parts: `pyproject.toml` (intent) and
`uv.lock` (exact resolution).

## 3. `pyproject.toml` Fundamentals

`pyproject.toml` is a **standardized configuration file** for Python
projects, written in TOML (§4 introduces the syntax), that lives at
the **project root** — directly alongside `src/` and `tests/`, per
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
§12.

It is worth being precise from the outset: **`pyproject.toml` is not
merely a dependency file.** It is the standardized home for several
distinct kinds of project configuration at once:

- **Project metadata** — name, version, description, and similar
  descriptive facts about the project (§5).
- **Dependency declarations** — what the project requires to run
  (§7).
- **Build configuration** — instructions for how the project should be
  turned into an installable package (a later chapter in this module
  covers this in depth; this chapter only needs you to know the
  section exists).
- **Tool configuration** — many Python tools (linters, formatters,
  type checkers, `uv` itself) read their own settings from named
  sections inside this same file, rather than requiring a separate
  configuration file each.

**Why it lives at the project root**: exactly the same reasoning
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
§12 already established — it describes the *project as a whole*,
including things (tests, tooling) that aren't part of the installable
package itself, so it belongs at the root that contains everything,
not nested inside the package's own source directory.

## 4. Basic `pyproject.toml` Structure

A minimal, modern example:

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Example project"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.0"
]
```

**A brief, sufficient introduction to TOML** — the file format itself,
for readers with no prior exposure:

- **Sections** (also called "tables") are written in square brackets:
  `[project]` starts a new named group of settings; everything below
  it, until the next `[section]` line, belongs to `[project]`.
- **Keys and values** are written as `key = value`, one per line —
  `name = "my-project"` sets the key `name` to the value
  `"my-project"`.
- **Strings** are quoted: `"my-project"`, `">=3.12"`. TOML treats a
  quoted value as text, exactly like a Python string literal.
- **Arrays (lists)** are written in square brackets, with each item
  comma-separated: `dependencies = ["requests>=2.0"]` — this is a list
  containing one string; more items would simply be added,
  comma-separated, inside the same brackets (as shown, one per line,
  for readability, in the multi-line form above).
- **Version strings** (`">=3.12"`, `">=2.0"`) are, syntactically, just
  ordinary TOML strings — their special *meaning* (a version
  constraint) is interpreted by Python packaging tools, not by TOML
  itself, which only sees "a string."

**Every field in the example, explained:**

- **`name = "my-project"`** — the project's own name, used when it's
  installed or referenced by other tools.
- **`version = "0.1.0"`** — the project's current version number
  (this module's later chapter on semantic versioning covers version
  numbering conventions in depth; this chapter only needs you to know
  this field exists and holds a version string).
- **`description = "Example project"`** — a short, human-readable
  summary of what the project does.
- **`requires-python = ">=3.12"`** — the minimum Python version this
  project supports (§6).
- **`dependencies = ["requests>=2.0"]`** — the project's direct
  runtime dependencies, each written as a package name plus an
  optional version specifier (§7–§8).

This is deliberately shown as a **minimal** example — real projects
typically have more metadata and more dependencies, but every
additional field is an extension of exactly this same `[section]` /
`key = value` / string / array structure.

## 5. Project Metadata

The `[project]` table's most commonly used metadata fields, gathered
in one place:

| Field | Meaning |
|---|---|
| `name` | The project's own name (used for installation and by tooling) |
| `version` | The project's current version string |
| `description` | A short, one-line summary of what the project does |
| `readme` | The filename of the project's README (commonly `"README.md"`), which becomes the project's long description when packaged |
| `requires-python` | The minimum (and optionally maximum) supported Python version(s) (§6) |
| `dependencies` | The list of direct runtime dependencies (§7) |
| `optional-dependencies` | Named groups of extra, opt-in dependencies (§22) |

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

**Why this metadata matters**, beyond simply "documenting" the
project: `name` and `version` are what installation tools and other
projects use to refer to this one specifically; `requires-python` lets
installation tools refuse to install the project into an incompatible
Python version *before* something fails confusingly at import time;
`readme` connects the file described in
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
§13 directly into the project's own packaged metadata, so it's visible
wherever the package is later published or inspected. This chapter
covers metadata only to the depth needed to understand dependency
management; the full packaging specification (additional metadata
fields, classifiers, authors, and so on) is beyond this chapter's
scope.

## 6. Python Version Requirements

```toml
[project]
requires-python = ">=3.12"
```

`requires-python` declares the **minimum Python version** (and,
optionally, a bounded range) the project is designed and tested to run
on. This is a **compatibility declaration**, not a description of
what's currently installed on any one machine — it tells installation
tools (and `uv` itself) "refuse to install this project into a Python
interpreter older than 3.12," rather than letting the project install
successfully and then fail with confusing syntax or behavior errors
partway through actually running.

**Why Python compatibility should be declared explicitly**: without
it, nothing stops the project from being installed into an
incompatible Python version — a syntax feature used in the project's
own code (or in one of its dependencies) that doesn't exist in an
older Python would only surface as a runtime failure, potentially deep
into actually using the software, rather than as an immediate, clear
installation-time rejection.

**The relationship between project requirements and the runtime
environment**: `requires-python` describes what the *project itself*
needs; it does not, by itself, install or manage *which* Python
interpreter is actually used to create the project's virtual
environment — that's a separate concern `uv` (§17 onward) and virtual
environments (§12) address. `requires-python` is the project's own
statement of "here's what I need," checked against whatever
interpreter is actually being used to set the project up.

## 7. Dependency Declarations

```toml
[project]
dependencies = [
    "requests>=2.0",
    "pydantic>=2.0,<3.0",
]
```

Each entry in `dependencies` is a string combining a **package name**
and an optional **version specifier** — §8 covers the specifier syntax
in full; this section focuses on the declaration's overall shape and
purpose.

- **`"requests>=2.0"`** — the package `requests`, with a **minimum
  version** constraint: any version 2.0 or later is acceptable.
- **`"pydantic>=2.0,<3.0"`** — the package `pydantic`, constrained to a
  **bounded range**: version 2.0 or later, but strictly less than 3.0.

**Why unconstrained dependencies can be risky** — a bare
`"requests"` with no version specifier at all means "any version,
whatsoever, is acceptable," including a future major version that
might change its API incompatibly in ways this project's code was
never tested against.

**Why overly strict constraints can also be problematic** — pinning
every dependency to one exact version (`"requests==2.31.0"`, and
nothing else, everywhere) means the project can never pick up even a
routine bug-fix release without a manual edit, and — more seriously —
it can make it genuinely impossible for the resolver to find a
compatible set of versions at all, if two of the project's
dependencies each demand a different exact version of some shared
transitive dependency (§10–§11 work through exactly this failure
mode). The right level of constraint is a deliberate middle ground,
covered concretely in §8.

## 8. Version Specifiers

The standard Python dependency-version syntax, each operator explained
with its actual meaning:

| Specifier | Meaning | Example |
|---|---|---|
| `>=` | This version or newer | `requests>=2.0` — 2.0, 2.31, 3.0, all acceptable |
| `>` | Strictly newer than this version | `requests>2.0` — 2.0 itself is *not* acceptable |
| `==` | Exactly this version — an **exact pin** | `requests==2.31.0` — only this precise version |
| `<=` | This version or older | `requests<=2.31.0` |
| `<` | Strictly older than this version | `requests<3.0` |
| `~=` | "Compatible release" — allows patch/minor updates but not the next major/minor boundary | `requests~=2.31` — allows `2.31.x` and `2.32+` up to (but not including) `3.0`, depending on how many version segments are given |

**Combinations**, joined with a comma (meaning "all of these
constraints must hold at once"):
```
requests>=2.0,<3.0
```
This means "version 2.0 or later, **and** strictly less than 3.0" — a
**bounded range**, allowing any 2.x release while explicitly excluding
an eventual, potentially-incompatible 3.0.

**The four styles, compared directly:**

- **Exact pin (`==2.31.0`)** — maximum reproducibility for *that one
  declaration*, zero flexibility; appropriate when a specific, known
  version is required for correctness or compatibility reasons, and
  updates should only ever happen deliberately.
- **Minimum version (`>=2.0`)** — maximum flexibility, minimum
  protection against a future breaking change; appropriate when you
  trust the package's own versioning discipline (§4 of this module's
  semantic-versioning chapter covers this trust relationship in
  depth) and want to freely receive updates.
- **Bounded range (`>=2.0,<3.0`)** — a practical middle ground: room to
  receive updates and bug fixes within a known-compatible major
  version, while guarding against an unreviewed jump to a version that
  might break compatibility.
- **Compatible release (`~=2.31`)** — a concise shorthand expressing
  roughly the same intent as a bounded range, following the
  convention that the *last* given version segment is allowed to
  increase, but not any segment before it.

For most application dependencies (§30), a **bounded range** is a
reasonable, common default — flexible enough to receive routine
updates, constrained enough to avoid an unreviewed breaking change
silently entering the project.

## 9. Direct vs. Transitive Dependencies

Returning to §1's diagram with the full vocabulary now established:

```
DIRECT:
my-project → requests

TRANSITIVE:
my-project → requests → urllib3
```

A **direct** dependency is one `my-project` itself explicitly declares
(lists in its own `dependencies` array) because it needs it — typically
because its code imports it, though plugins, runtime discovery, or
command-line/framework integration can also make a package direct
without a literal `import`. A **transitive** dependency
is one that a direct dependency itself needs, pulled in automatically
without `my-project` ever mentioning it by name.

**Why developers usually declare only direct dependencies
explicitly**, rather than manually listing every transitive one:
`requests` itself already knows, and declares, exactly which versions
of `urllib3`, `certifi`, `idna`, and `charset-normalizer` it needs —
duplicating that knowledge inside `my-project`'s own `pyproject.toml`
would be redundant, and would immediately go stale the moment
`requests` itself changes its own transitive requirements in a future
release. The **resolver** (§10) is specifically the mechanism that
reads every direct dependency's own declared requirements and works
out the full transitive set automatically — this is precisely the
value it adds, and precisely why manually tracking transitive
dependencies by hand doesn't scale.

## 10. Dependency Resolution

**Dependency resolution** is the process of taking every declared
requirement — the project's own direct dependencies, plus every one of
*their* dependencies, transitively — and finding **one specific
version of each package** that satisfies every constraint
simultaneously.

A concrete example, worked through explicitly:

```
my-project requires:      A >= 2
A requires:                 B < 5
my-project ALSO requires:    C
C requires:                    B >= 4
```

The resolver needs to find one version of `B` satisfying **both**
`B < 5` (from `A`) and `B >= 4` (from `C`) at the same time — in this
case, any `B` version in the range `[4, 5)` (i.e., `4.x`) works, so a
resolution *does* exist: pick `A`'s and `C`'s latest compatible
versions, and `B`'s latest version that's `>=4` and `<5`.

**The dependency graph**: conceptually, every package and its
requirements form a graph — `my-project` at the root, pointing to
`A` and `C`, each of which points to their own further requirements
(here, both converging on `B`). The resolver's job is to walk this
entire graph and find a single, consistent assignment of exact
versions to every node that satisfies every edge's constraint.

**This is not magic** — it is a genuinely computational
constraint-satisfaction process, and (as §11 shows) it can
legitimately **fail** when no such consistent assignment exists at
all. Modern resolvers (including `uv`'s) are fast and generally
reliable at finding a solution when one exists, but they cannot
invent compatibility that isn't actually there in the packages'
own declared constraints.

## 11. Dependency Conflicts

Extending §10's example to a case with **no solution**:

```
my-project requires:      A >= 2
A requires:                 B < 5
my-project ALSO requires:    C
C requires:                    B >= 6
```

Now `B` would need to be simultaneously `< 5` **and** `>= 6` — no
version can satisfy both at once. This is a genuine **dependency
conflict**, and the resolver will fail, typically with an error
message naming the conflicting requirements it found.

**Why resolution can fail**: because the constraints, as declared,
are mathematically incompatible — no amount of retrying or
"working harder" would find a valid answer, because none exists given
those exact requirements.

**How to diagnose a conflict**, systematically:
1. Read the resolver's error message carefully — modern tools
   (including `uv`) typically report *which* packages and *which*
   specific version constraints are in conflict, not just "resolution
   failed."
2. Identify which of your **direct** dependencies actually introduced
   each conflicting constraint.
3. Check whether a newer (or older) version of one of your direct
   dependencies would relax its own transitive requirement enough to
   resolve the conflict.
4. Consider whether one of your own version constraints (§7–§8) is
   more restrictive than it actually needs to be.

**Why blindly forcing a version is dangerous**: manually overriding
the resolver's decision (installing a specific version by hand,
outside of what was actually resolved) can produce an environment
that *looks* installed successfully but violates one of the actual
declared constraints — meaning the overridden package may not
actually be compatible with something else that depends on it,
producing subtle, hard-to-diagnose runtime failures instead of a
clear, upfront resolution error. A genuine conflict should be resolved
by adjusting the actual declared constraints (upgrading a dependency,
loosening an overly strict range) — not by forcing an answer the
resolver correctly determined didn't exist.

## 12. Virtual Environments

A **virtual environment** is an isolated, self-contained installation
of Python packages, separate from your system's own global Python
installation and separate from every other project's own virtual
environment.

**Why isolation matters**: without it, every Python project on a
single machine would share **one** global set of installed packages —
meaning two projects needing two different, incompatible versions of
the same package could never both work correctly on that machine at
the same time. This is a direct, practical instance of §2's
"incompatible packages" problem, solved structurally rather than by
hoping no two projects ever disagree.

**System Python vs. project environment**: the Python interpreter
installed system-wide (or via whatever mechanism your OS or a version
manager provides) is meant to remain a stable, general-purpose tool —
installing project-specific dependencies directly into it risks
polluting it for every other use of that same interpreter. A **project
environment** — a virtual environment created specifically for one
project — keeps that project's dependencies entirely separate.

```
Project
  ↓
Virtual Environment      (an isolated set of installed packages, specific to this project)
  ↓
Installed Dependencies    (exactly what pyproject.toml/uv.lock resolved and specify)
```

This chapter does not teach manually creating and activating virtual
environments with Python's own built-in `venv` module in depth — `uv`
(§17 onward) manages this step automatically as part of its normal
workflow (`uv sync`, `uv run`), which is one of its central practical
conveniences: you generally do not need to think about virtual
environment creation/activation as a separate manual step at all once
`uv` is managing the project.

## 13. Lock Files

A **lock file** is a machine-generated record of the **exact, specific
versions** of every dependency (direct *and* transitive) that a
resolver determined satisfy the project's declared requirements — at
one specific point in time.

The distinction this chapter has been building toward, stated as
precisely as possible:

- **`pyproject.toml`** = **what the project requires** — a
  human-authored statement of intent (`requests>=2.0`), deliberately
  loose enough to allow reasonable version flexibility.
- **`uv.lock`** = **the resolved dependency state** — a specific
  answer (`requests==2.31.0`, plus every transitive dependency's own
  resolved version) that the resolver determined satisfies every
  requirement, recorded so it can be reproduced without re-running
  resolution from scratch. The lock file records the resolved
  dependency graph for the project's supported environments: in the
  common case that is one version per package, but when different
  Python versions, operating systems, or architectures need different
  versions, the same package can appear more than once, each variant
  tied to an environment marker.

**Declared requirements vs. resolved versions**: `requests>=2.0` in
`pyproject.toml` could be satisfied by many different actual versions
depending on *when* resolution happens (2.28 last year, 2.31 today,
2.35 next year) — the lock file removes that ambiguity entirely by
recording one specific answer, valid until the lock file is
deliberately regenerated (§14, §26).

**Reproducibility and deterministic installation**: given the *same*
`uv.lock` (used as-is, see §23), installing dependencies on a machine
within the supported environments, at any later time, selects the same
locked versions for that environment — this is what makes "it worked
on my machine" a solvable problem rather than a recurring mystery:
everyone, and every environment (CI, a container, production), installs
from the same already-resolved lock file,
rather than each independently re-running resolution against
potentially-different available package versions.

## 14. `uv.lock`

`uv.lock` is `uv`'s own lock file format — automatically generated and
updated by `uv` itself (`uv add`, `uv lock`, `uv sync` — §20, §23, §26
cover exactly when).

**Its relationship to `pyproject.toml`**: `uv.lock` is *derived from*
`pyproject.toml` — it exists specifically to record one resolved
answer to whatever `pyproject.toml` currently declares. **Resolved and
transitive dependencies**: `uv.lock` records not just the project's
direct dependencies' resolved versions, but *every* transitive
dependency's resolved version too — the complete, resolved dependency
graph from §10, pinned down. Because the lock file is cross-platform,
a package that needs different versions on different Python versions
or platforms is recorded once per variant, with the environment
marker that selects it.

**Reproducibility**: as long as `uv.lock` exists and is used as-is
(via `uv sync --locked`, or `uv sync` while the lock is up to date, §23),
every environment set up from it gets the locked versions for its
platform and Python version, regardless of when it's set up.

**Why it should normally be committed to version control for
application projects**: an application (§30) is typically deployed
as a specific, whole, working unit — committing `uv.lock` means every
developer, CI run, and deployment installs the *same locked*,
already-verified-to-work-together set of dependency versions, rather
than each independently re-resolving and potentially arriving at
subtly different results.

**When lock-file strategy may differ for libraries**: a library
(§30) is typically *installed into someone else's project*, which
will do its own resolution alongside its other dependencies — a
library's own lock file (if it maintains one at all) is primarily a
development-time convenience for the library's own contributors, not
something consumers of the library ever directly use; consumers
resolve the library's declared version *ranges* (§7–§8) against their
own project's other requirements instead.

**`uv.lock` is not meant to be hand-edited.** It is a generated
artifact, produced and maintained by `uv` itself as a direct,
mechanical consequence of running its commands — treat it the way you
would treat any other tool-generated file: read it to understand
what's currently resolved, but make changes by adjusting
`pyproject.toml` and re-running the relevant `uv` command, never by
editing `uv.lock`'s contents by hand.

## 15. Why Lock Files Matter

A realistic scenario, extending §2's Alex/Priya example with the
missing piece:

```
Developer A (eight months ago):  pip install pandas  →  gets pandas 2.1
Developer B (today):               pip install pandas  →  gets pandas 2.8
```

With no lock file, this divergence is invisible until something
actually breaks — a behavior change between `pandas` 2.1 and 2.8 (real
or hypothetical) manifests as a confusing, hard-to-reproduce bug that
"only happens for Developer B."

**With a lock file in place**, this scenario simply cannot happen:
`uv.lock` records `pandas`'s resolved version; every subsequent
`uv sync` (§23) against an unchanged, up-to-date lock file, by anyone,
at any time, installs *that* recorded version for their environment —
Developer A and Developer B both get `pandas` 2.1 (or whatever the lock
file currently says), regardless of when each of them happens to set up
their environment.

**Connecting this to every stage of a real project's lifecycle:**

- **Local development** — every teammate's environment matches, from
  day one.
- **CI/CD** (§28) — the locked dependencies tested in CI are the ones
  that will be deployed; no "it passed CI but failed in
  production because of a version difference."
- **Containers** (§29) — a container image built from the locked
  dependencies is reproducible across every build, not just "whatever
  was available on PyPI the day the image happened to be built."
- **Production deployments** — the deployed environment matches
  exactly what was developed and tested against, closing the loop
  §2 opened with "difficult deployment" and "difficult reproduction."

## 16. `pyproject.toml` vs. `uv.lock`

| Aspect | `pyproject.toml` | `uv.lock` |
|---|---|---|
| **Purpose** | Declares what the project requires | Records exactly which versions were resolved |
| **Human-edited?** | Yes — written and edited directly (or via `uv add`/`uv remove`) | No — generated and maintained by `uv`; not hand-edited |
| **Declares requirements?** | Yes — version ranges, minimums, etc. | No — no ranges, only resolved versions |
| **Records resolved versions?** | No | Yes — every direct and transitive dependency, pinned (per environment marker where needed) |
| **Reproducibility** | Allows flexibility (different resolutions possible at different times) | Provides reproducible dependency selection for the environments it covers |
| **Committed to version control?** | Always, for both applications and libraries | Recommended for applications (§14, §30); often less central for libraries |
| **Contains project metadata (name, version, etc.)?** | Yes | No — purely dependency-resolution data |

The memorable version of this table, restated one final time: **you
write `pyproject.toml`; `uv` writes `uv.lock`.** One expresses intent;
the other records a specific, reproducible fact about how that intent
was satisfied.

## 17. What Is `uv`?

**`uv`** is a modern Python **project and package manager** — a single
tool that handles dependency resolution, virtual environment
management, lock-file generation, and running commands within a
project's managed environment, replacing what has historically
required several separate tools used together.

**The distinction worth being precise about**: `pyproject.toml` is a
**standard** — a file format and structure defined by the Python
packaging community, that *any* compliant tool can read and write.
`uv` is one specific **tool** that reads and writes that standard
format (among others). This matters because it means the
`pyproject.toml` this chapter teaches isn't "a `uv` file" — it's a
standard Python project file that `uv` happens to be an excellent,
modern tool for working with; a project's `[project]` table remains
meaningful even if a team later chose a different tool to manage it.

**What `uv` actually does, gathered in one place** (each covered in
depth in its own section below): creates and initializes new projects
(§19); resolves and records dependencies (§20, §26); manages the
project's virtual environment automatically, without manual `venv`
steps (§12, §23); and runs commands inside that correctly-resolved
environment (§24).

## 18. Installing and Verifying `uv`

This chapter does not prescribe one specific installation method,
since installation mechanisms and recommendations can change over
time and differ by operating system — installing `uv` itself is an
**operating-system-level** action (installing a program onto your
machine), distinct from anything covered by `pyproject.toml` or
project-level commands.

Once installed, verify it's available and check its version:

```bash
uv --version
```

This should print a version string (e.g. `uv 0.x.y`). If this command
fails (not found), `uv` either isn't installed, or isn't on your
shell's `PATH` — a system-configuration issue to resolve before
proceeding, distinct from anything project-specific.

**If you need to install or update `uv` itself**, follow the current,
official installation instructions for your operating system rather
than relying on a specific command memorized from any one source
(including this chapter) — installation methods are exactly the kind
of detail that can change between when this is written and when you
read it.

## 19. Initializing a Project with `uv`

```bash
uv init my-project
```

Conceptually, this **creates a new project skeleton** — a project
directory, a starting `pyproject.toml` with basic metadata already
filled in, and typically a minimal starting source file — giving you a
working, valid `pyproject.toml` to build on rather than writing one
completely from scratch.

**Why project initialization matters**: it ensures the `[project]`
table (§4–§5) is syntactically correct and contains the fields tools
expect from the very first commit, avoiding the class of subtle
formatting mistakes that can come from hand-authoring TOML with no
starting template.

**Project root**: wherever `uv init` is run (or the directory name
given to it) becomes the project root — the same location
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)
established as the home for `pyproject.toml`, `src/`, and `tests/`.

**A note on exact generated behavior**: precisely which files `uv
init` creates, which flags it supports (e.g., for choosing a src
layout versus a flat layout, or an application versus a library
template), and its exact default output can vary across `uv` versions.
Rather than memorizing one specific generated structure as universal,
run `uv init --help` (or consult the currently installed version's own
documentation) to confirm current behavior before relying on
specifics beyond what this chapter has stated conceptually.

## 20. Adding Dependencies with `uv`

```bash
uv add requests
```

The conceptual pipeline this one command triggers, directly extending
this chapter's Core Mental Model:

```
uv add requests
        ↓
updates pyproject.toml's dependencies list to include "requests"
        ↓
resolves the full dependency graph (including requests' own transitive dependencies)
        ↓
updates/creates uv.lock with the resolved, exact versions
        ↓
synchronizes the project's virtual environment to match
```

A single command performs **all four** of these steps automatically —
this is the practical value `uv` adds over manually editing
`pyproject.toml` and separately running a resolver/installer: the
declaration, the resolution, the locking, and the environment update
all stay consistent with each other, by construction, every time.

**Version constraints** can be specified directly:
```bash
uv add "requests>=2.31,<3.0"
```
This adds the dependency to `pyproject.toml` with exactly the
specifier given, rather than an unconstrained bare name — a direct,
practical application of §7–§8's guidance about choosing a sensible
constraint rather than leaving a dependency unconstrained by default.

## 21. Development Dependencies

**Runtime dependencies** are needed for the application to actually
run in production — `requests`, if the application makes HTTP calls,
belongs here. **Development dependencies** are needed only while
*developing* the project — a test runner, a linter, a type checker —
and should never need to be installed on a production machine just to
*run* the finished application.

```bash
uv add --dev pytest ruff mypy
```

This adds `pytest`, `ruff`, and `mypy` to the **`dev` dependency
group** — a `[dependency-groups]` table in `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.5",
    "mypy>=1.10",
]
```

A dependency group is for *development workflows*; it is **not** part
of the project's published metadata and is not something end users can
request. That makes it different from the optional dependencies
(extras) of §22, which are optional *features* of the project itself.
A dev group is conceptually and practically
distinct from the main `dependencies` list, so that a production
install (or a minimal container image, §29) can skip installing them
entirely, since they serve no purpose once the application is actually
running.

**Why this separation matters**: a production deployment installing
`pytest` and `mypy` alongside the application's real runtime needs
adds unnecessary size and unnecessary (unused) dependencies to a
production environment — dependencies that themselves carry their
own transitive dependencies, their own potential vulnerabilities
(§31), and their own maintenance burden, all for tools that provide
zero value once the code is actually running rather than being
developed.

## 22. Optional Dependencies / Extras

Sometimes a project supports **optional features**, each requiring its
own additional dependencies that most users won't need. **Optional
dependencies** (also called **extras**, declared under
`[project.optional-dependencies]`) are part of the project's published
metadata, and are *not* the same mechanism as the development
dependency groups of §21 (`[dependency-groups]`). They let a project
declare these
without forcing every installation to include them by default.

```toml
[project]
name = "orders-report"
dependencies = [
    "requests>=2.31,<3.0",
]

[project.optional-dependencies]
excel = ["openpyxl>=3.0"]
```

A user installing the base project gets only `requests`; a user who
specifically needs Excel export functionality would additionally
request the `excel` extra (the exact installation syntax for
requesting an extra is a packaging-tool detail beyond this chapter's
scope — the concept, and how to declare one in `pyproject.toml`, is
what matters here).

**Why applications/libraries need this**: it lets a project support a
broader set of use cases without imposing every possible dependency on
every single user — someone who never needs Excel export never needs
`openpyxl` installed at all, keeping their environment smaller and
reducing their exposure to a dependency they don't actually use.

## 23. Syncing the Environment

```bash
uv sync
```

`uv sync` works in two steps:

```
uv sync
    ↓
ensure the lock state is usable/current   (re-lock if pyproject.toml changed)
    ↓
synchronize the environment to the lock
```

It reads the project's current requirements (`pyproject.toml`) and its
lock file (`uv.lock`). If the lock file is missing or no longer matches
`pyproject.toml`, plain `uv sync` **updates `uv.lock` first** and then
brings the project's virtual environment **into alignment** with the
result — installing anything missing, and removing anything present that
shouldn't be (including extraneous packages), so the installed
environment matches the locked state.

When the intent is *"use the existing lock file as-is, and fail if it is
not already up to date"*, use the strict form:

```bash
uv sync --locked     # error instead of updating uv.lock
```

(`--frozen` goes further and skips checking whether the lock file is up
to date at all.) The chapter's convention is:

```
Development:            uv sync
CI (strict):            uv sync --locked
Production (strict):    uv sync --locked --no-dev
```

Plain `uv sync` also installs the `dev` group (§21); `--no-dev` excludes
it.

This is the command you run: after cloning a project someone else set
up (to get your own local environment matching their locked
dependencies); after pulling changes that modified
`pyproject.toml` or `uv.lock`; or simply to confirm your environment
is currently correct and up to date. `uv sync` is what makes §15's
promise concrete and actionable — it's the specific command that
turns "a lock file exists" into "my actual, running environment
matches it."

## 24. Running Commands with `uv`

```bash
uv run python app.py
uv run pytest
```

`uv run` executes a given command **inside the project's own managed
virtual environment** — automatically, without you needing to
separately activate that environment first (a manual step this
chapter's §12 deliberately avoided teaching in depth, precisely
because `uv run` handles it).

**Why this matters**: running `python app.py` directly, without `uv
run`, might silently execute against your *system* Python (or whatever
environment happens to be currently active in your shell) — potentially
missing the project's own dependencies entirely, or picking up the
wrong versions of them. `uv run python app.py` executes the command in the project's own
managed environment, with the project's resolved dependencies
available, regardless of what else might be active in your shell at
that moment. The same applies to `uv run pytest` — the test suite runs
against the project's actual dependencies, not whatever happens to be
globally available.

Like `uv sync`, `uv run` makes sure the lock file and environment are
up to date before running, which means it can **update `uv.lock`** if
`pyproject.toml` has changed. Plain `uv run` is the normal development
form; when the existing lock file must be accepted as-is, use
`uv run --locked ...`, which fails instead of updating it.

## 25. Adding / Removing / Updating Dependencies

The core dependency-lifecycle commands, gathered together:

```bash
uv add requests            # add a new runtime dependency
uv add --dev pytest         # add a new development dependency (§21)
uv remove requests            # remove a dependency, updating pyproject.toml and uv.lock together
uv sync                         # bring the environment in line with the lock file, re-locking first if needed (§23)
```

Each of these commands keeps `pyproject.toml` and `uv.lock` **in
sync with each other automatically** — `uv add` and `uv remove` both
update the declared dependency list *and* re-resolve/update the lock
file in one step, which is precisely the guarantee this chapter's Core
Mental Model depends on: these two files should never be allowed to
drift apart from each other, and letting `uv` perform every change
through its own commands (rather than hand-editing either file
directly) is what keeps that guarantee intact.

**Checking current dependency state**: `uv --help` (and the help text
for each specific subcommand, e.g. `uv add --help`) is the reliable way
to check exactly which flags and inspection commands your currently
installed version of `uv` supports — this chapter deliberately does
not enumerate every possible flag, since new ones are added over time;
the four commands above represent the stable, foundational workflow
this chapter is responsible for teaching.

## 26. Locking and Updating

Four related but genuinely distinct operations, worth telling apart
precisely:

- **Declaring** a dependency — adding it (with whatever version
  constraint) to `pyproject.toml`'s `dependencies` list.
- **Resolving** a dependency — the resolver (§10) working out one
  specific, compatible version that satisfies the declared
  constraint(s), alongside every other requirement in the project.
- **Locking** a dependency — recording that resolved version (and
  every transitive dependency's resolved version) into `uv.lock`, so
  it doesn't need to be re-resolved from scratch every time.
- **Installing/synchronizing** — actually placing the locked versions
  into the project's virtual environment (`uv sync`, §23).

```bash
uv lock       # re-run resolution and update uv.lock, WITHOUT touching the environment
uv sync       # install/synchronize the environment to match the (possibly just-updated) lock file
              # (plain `uv sync` would also re-lock if needed; `uv sync --locked` never does)
```

**Why changing `pyproject.toml` and changing `uv.lock` are related but
not identical operations**: editing `pyproject.toml` by hand (e.g.,
loosening a version constraint) changes only what the project
*declares* — it does **not**, by itself, automatically re-resolve or
update `uv.lock`. `uv.lock` remains whatever it last was until a
command that explicitly re-resolves (`uv add`, `uv remove`, or
explicitly `uv lock`) is run. This is precisely why a manually-edited
`pyproject.toml`, with no corresponding `uv lock`/`uv sync`, can leave
the project in an inconsistent state — §36 covers exactly this
scenario as a debugging lab entry.

**Updating a dependency** to a newer version within its existing
constraints is, conceptually, "re-run resolution and pick the latest
version that still satisfies every declared constraint" — the specific
command/flag for deliberately requesting an update (as opposed to
`uv add`/`uv remove` changing the declared dependencies themselves) is
exactly the kind of detail worth confirming against your installed
`uv`'s own `--help` output, per this chapter's stated approach to
version-dependent specifics.

## 27. Reproducible Development

Putting §13–§26 together into the complete, end-to-end reproducibility
workflow:

```
Developer
    ↓
pyproject.toml     (checked into version control — declares requirements)
    ↓
uv.lock              (checked into version control — records the exact resolution)
    ↓
uv sync                (run by anyone, anywhere, anytime; `--locked` in CI/deploy)
    ↓
the same locked dependency versions for each supported environment
```

**Onboarding**: a new team member clones the repository and runs `uv
sync` — one command, and their environment matches everyone
else's (for the same platform and Python version), with no manual "here's the list of packages you need to
install" documentation required at all (the `pyproject.toml`/`uv.lock`
pair *is* that documentation, in exact, executable form).

**CI** (§28), **deployment**, and **container builds** (§29) each
perform a strict `uv sync --locked` step, against the same committed
`uv.lock` — meaning the dependency versions actually tested in CI are
the same locked versions that end up deployed to production (for the
same platform and Python version). Strictness matters: plain `uv sync`
would quietly re-lock a stale `uv.lock`, whereas `--locked` turns that
situation into an error. This is the concrete, mechanical realization
of §15's promise: reproducibility isn't a hope or a convention here,
it's a direct consequence of every stage reading from the same lock
file.

## 28. CI/CD Use

A conceptual CI pipeline, extending
[07-standard-streams-and-exit-codes.md](../05-Text-Files-Structured-Data-and-CLI-Programs/07-standard-streams-and-exit-codes.md)'s
§23 CI discussion with the dependency-installation step now made
explicit:

```
checkout code
    ↓
install/sync environment       ←  uv sync --locked  (uses the COMMITTED uv.lock; fails if stale)
    ↓
run tests                       ←  uv run --locked pytest
    ↓
run lint/type checks              ←  uv run --locked ruff check .  /  uv run --locked mypy .
    ↓
build/deploy
```

**Why reproducibility matters here specifically**: a CI run that
resolves dependencies *fresh*, independently, on every run (rather
than installing from a committed lock file) risks testing against
*different* dependency versions than what a developer actually tested
locally, or than what will eventually be deployed — reintroducing
exactly the "works on my machine, fails somewhere else" problem this
entire chapter exists to solve, just relocated to "works in CI, fails
in production" instead. Using `uv sync --locked` against the
committed `uv.lock` in CI closes this gap: the same resolved
dependencies are used at every stage, from a developer's laptop through
CI to production, and a `pyproject.toml` change that was committed
without updating `uv.lock` fails the build instead of being silently
re-locked. (`uv run --locked ...` applies the same strictness to each
command; plain `uv run` is for local development.)

## 29. Containers and Deployment

Conceptually, a containerized application's build process benefits
from the same strict lock-file discipline as CI:

```
copy pyproject.toml + uv.lock into the image
        ↓
uv sync --locked --no-dev   (installs the locked runtime dependencies into the image; skips the dev group)
        ↓
copy application source code
        ↓
build the final image
```

Because dependency installation is driven by the already-resolved
`uv.lock` rather than re-running resolution fresh inside the container
build (and `--locked` makes a stale lock file an error rather than a
silent re-lock), **every image built for the same platform and Python
version from the same lock file gets the same dependency versions** — a
container built today and one built six months from now, from an
unchanged `uv.lock`, install the same package versions, regardless of
what newer versions might have been published to package indexes in the
meantime. `--no-dev` leaves out the development group (§21), which a
production image does not need. This chapter
deliberately stops at this conceptual level — writing an actual
`Dockerfile` and the full mechanics of container builds are outside
this chapter's scope; what matters here is understanding *why* the
lock file is exactly as valuable in a containerized deployment as it
is in local development and CI.

## 30. Application vs. Library Dependency Strategy

An important distinction, presented as a genuine tradeoff rather than
a universal rule:

**Application** (a CLI tool, a service you deploy and run yourself):
- **Reproducibility is critical** — you control the exact deployment
  environment, and you want it to match exactly what was developed and
  tested.
- **The lock file is highly valuable** — commit `uv.lock`; every
  environment (developer, CI, production) should install from it
  (§27–§29).
- **The exact resolved dependency set matters directly** — you're the
  only consumer of this dependency set, so pinning it down precisely
  carries no downside for anyone else.

**Library** (code published for *other* projects to depend on, e.g.
via PyPI):
- **Consumers resolve dependencies in their own environment** —
  someone installing your library will run resolution *themselves*,
  alongside their own project's other dependencies; your library's own
  lock file (if you maintain one for your own development) is never
  actually consulted by the people installing your library.
- **Version ranges matter more than exact pins** — declaring
  `requests>=2.0` (a range) rather than `requests==2.31.0` (an exact
  pin) in a *library's* `dependencies` gives consumers room to satisfy
  *their own* other requirements without your library forcing an
  unnecessarily exact, potentially conflicting version on them.
- **Dependency declarations and lock-file strategy can differ**: a
  library still benefits from a lock file for its *own* development
  and CI reproducibility, but that lock file's role is narrower — it
  never travels with the library to its actual consumers the way an
  application's lock file travels with it to production.

This is presented explicitly as a **tradeoff based on who consumes the
dependency information**, not an absolute rule — a project that is
*primarily* an internal application but is occasionally installed as a
dependency by a sibling internal tool might reasonably borrow practices
from both sides of this distinction, depending on which concern
matters more in that specific situation.

## 31. Security and Dependencies

Dependency management is not purely a reproducibility concern — it's
also a **security** concern, worth treating with the same defensive,
practical mindset this course has applied to every other form of
untrusted or external input.

- **Dependency vulnerabilities**: a security flaw discovered in a
  package you depend on (directly or transitively) becomes, in effect,
  a security flaw in your own project — even if you never call the
  specific vulnerable function yourself, merely having it installed
  and reachable can be a real exposure depending on the flaw.
- **Outdated packages**: a dependency that hasn't been updated in a
  long time may be carrying known, unpatched vulnerabilities simply
  because no one has reviewed whether an update is needed.
- **Transitive dependencies** carry exactly the same risk as direct
  ones, but are easy to overlook precisely because they were never
  explicitly chosen — a vulnerability three levels deep in a
  transitive dependency chain is just as real a risk as one in a
  package you added yourself.
- **Dependency review**: before adding a new dependency, it's
  reasonable engineering practice to consider how actively maintained
  it is, how widely used and trusted it is, and how large a transitive
  dependency footprint it brings with it — not every convenience is
  worth the added exposure.
- **Why blindly upgrading everything is risky**: an automatic,
  unreviewed mass-upgrade of every dependency to its latest version can
  introduce breaking API changes, or even a newly-introduced
  vulnerability, with no human review of what actually changed —
  exactly the "accidental upgrade" problem §2 opened with, now
  considered specifically from a security angle.
- **Why never updating dependencies is also risky**: the opposite
  extreme — freezing dependencies indefinitely and never revisiting
  them — leaves known vulnerabilities unpatched indefinitely, trading
  the risk of a bad upgrade for the guaranteed, growing risk of running
  increasingly outdated, potentially compromised code.

The practical, defensive middle ground this chapter recommends:
**review and update dependencies deliberately and periodically** —
using the lock file's own change history (since it's version-
controlled, per §14) to see exactly what changed with each update,
rather than either freezing dependencies forever or upgrading
everything reflexively with no review at all.

## 32. Common Mistakes

1. **Installing packages globally.** *Why:* pollutes the system Python
   for every other use of it, and creates exactly the isolation
   failure §12 exists to prevent. *Fix:* always work within a
   project-specific virtual environment, managed via `uv`.
2. **Forgetting virtual environments entirely.** *Why:* without one,
   there's no isolation between this project's dependencies and every
   other project's (or the system's) — the "incompatible packages"
   problem from §2 becomes likely rather than merely possible. *Fix:*
   let `uv sync`/`uv run` manage the environment automatically (§12,
   §23–§24), rather than installing packages ad hoc.
3. **Manually editing `uv.lock`.** *Why:* `uv.lock` is a generated,
   derived artifact — hand-editing it can produce an internally
   inconsistent file that no longer accurately reflects a real,
   valid resolution (§14). *Fix:* change `pyproject.toml` and re-run
   the appropriate `uv` command (`uv add`, `uv remove`, or `uv lock`)
   instead.
4. **Committing inconsistent dependency files.** *Why:* committing a
   `pyproject.toml` change without also committing the resulting
   `uv.lock` update leaves the two files describing different states,
   breaking reproducibility for the next person who clones the repo
   (§26–§27). *Fix:* always commit `pyproject.toml` and `uv.lock`
   together, as one atomic change.
5. **Changing `pyproject.toml` without understanding the resulting
   lock state.** *Why:* loosening or tightening a version constraint
   by hand, with no re-resolution, leaves `uv.lock` stale relative to
   the new declaration (§26). *Fix:* run `uv lock` (or `uv sync`) after
   any manual `pyproject.toml` edit, to bring the lock file back in
   sync.
6. **Ignoring dependency conflicts.** *Why:* forcing an install past a
   genuine resolution failure (§11) can produce an environment that
   looks installed but violates a real, declared constraint
   somewhere. *Fix:* diagnose and resolve the actual underlying
   conflict — adjust constraints or dependency versions — rather than
   overriding the resolver's result.
7. **Using overly broad version constraints.** *Why:* a bare,
   unconstrained dependency (§7) offers no protection against a future
   breaking change. *Fix:* use a bounded range (§8) reflecting the
   actual compatibility you've verified.
8. **Pinning everything blindly.** *Why:* exact-pinning every single
   dependency, including deep transitive ones, by hand removes all
   flexibility and can make legitimate future resolutions impossible
   (§7–§8, §11). *Fix:* let the resolver and lock file (§10, §13–§14)
   handle exact version pinning automatically; declare only your own
   direct dependencies' constraints deliberately.
9. **Confusing direct and transitive dependencies.** *Why:* manually
   adding a transitive dependency as if it were a direct one duplicates
   information the resolver already derives automatically, and can go
   stale (§9). *Fix:* declare only what your own project directly needs (typically what
its code imports); let resolution handle the rest.
10. **Installing packages manually, without declaring them.** *Why:*
    a package installed by hand (outside of `uv add`) exists in *your*
    environment only — nothing records it in `pyproject.toml` or
    `uv.lock`, so it silently disappears for anyone else who runs `uv
    sync` (§2's "missing packages" problem, concretely). *Fix:* always
    add a genuinely needed dependency through `uv add`, never by
    installing it manually and hoping to remember to declare it later.
11. **Relying on a local environment that isn't reproducible.**
    *Why:* an environment assembled through ad hoc, manual installs
    over time has no record anywhere of how it actually got that way —
    exactly the opposite of §13–§15's entire point. *Fix:* treat
    `pyproject.toml` + `uv.lock` as the *only* authoritative source of
    what's installed; rebuild the environment from them (`uv sync`)
    whenever in doubt, rather than trusting an environment's accumulated
    history.
12. **Using the wrong Python environment.** *Why:* running a command
    outside `uv run`, or activating an unrelated environment by
    accident, can execute code against entirely the wrong set of
    installed dependencies (echoing
    [01-imports-modules-and-main.md](01-imports-modules-and-main.md)'s
    §28 "wrong environment" scenario, now specifically in the `uv`
    workflow). *Fix:* prefer `uv run` for every project-related
    command, so the correct environment is used automatically, every
    time.

## 33. Progressive Coding/CLI Examples

**1. The dependency concept, stated as code**
```python
import requests   # requires `requests` to be installed — a direct dependency
```

**2. A minimal `pyproject.toml`**
```toml
[project]
name = "demo"
version = "0.1.0"
```

**3. Declaring a Python version requirement**
```toml
[project]
name = "demo"
version = "0.1.0"
requires-python = ">=3.12"
```

**4. Adding one dependency (declared by hand)**
```toml
[project]
name = "demo"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.0",
]
```

**5. A bounded version constraint**
```toml
dependencies = [
    "requests>=2.31,<3.0",
]
```

**6. A direct-vs-transitive dependency graph, written out explicitly**
```
demo → requests → urllib3, certifi, idna, charset-normalizer
```
`demo`'s own `dependencies` list names only `requests`; `uv.lock`
(example 13) will record all five packages' exact resolved versions.

**7. Initializing a project with `uv`**
```bash
uv init demo
cd demo
```
Creates a starting `pyproject.toml` and project skeleton (§19).

**8. Adding a dependency with `uv`**
```bash
uv add requests
```
Updates `pyproject.toml`, resolves, updates `uv.lock`, and syncs the
environment — all in one step (§20).

**9. Adding a development dependency**
```bash
uv add --dev pytest ruff mypy
```
Adds these to a separate development-dependency group, not the main
runtime `dependencies` list (§21).

**10. `uv sync`**
```bash
uv sync
```
Brings the environment into alignment with the current
`pyproject.toml`/`uv.lock` state, re-locking first if the lock file is
stale (§23) — the command to run after cloning a project, or after
pulling changes to either file.

**11. `uv run`**
```bash
uv run python -m demo.cli
uv run pytest
```
Runs each command inside the project's own managed environment, so the
project's resolved dependencies are used (§24).

**12. Removing and updating a dependency**
```bash
uv remove requests
uv add "requests>=2.32"
```
Removing and re-adding with a tightened minimum version — each command
updates both `pyproject.toml` and `uv.lock` together (§25–§26).

**13. A conceptual lock-file entry** (illustrative, not `uv`'s exact
real format, which is more detailed):
```
name = "requests"
version = "2.31.0"

name = "urllib3"
version = "2.0.7"
```
This is `uv.lock`'s job made concrete: resolved versions, for every
package, direct and transitive alike (§14). (The real file also carries
environment markers, so one package can appear at several versions when
different Python versions or platforms need them.)

**14. A reproducible project setup, from scratch, on a new machine**
```bash
git clone <repository>
cd <repository>
uv sync
uv run pytest
```
Three commands take a fresh checkout to a fully working, correctly
dependency-resolved, tested environment (§27).

**15. A CI-oriented workflow**
```bash
uv sync --locked
uv run --locked pytest
uv run --locked ruff check .
uv run --locked mypy .
```
Every step runs inside the same locked environment, and fails rather
than silently re-locking if `uv.lock` is stale (§28) —
directly extending
[07-standard-streams-and-exit-codes.md](../05-Text-Files-Structured-Data-and-CLI-Programs/07-standard-streams-and-exit-codes.md)'s
§23 CI-pipeline discussion with the dependency-installation step made
concrete.

## 34. Mini Project — Reproducible Python CLI Project with `uv`

**Scenario:** design a small, production-oriented CLI, `orders-report`
(the same tool
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
§29 mini project laid out structurally), now with its dependency
management fully specified using `pyproject.toml` and `uv`.

**Project structure:**
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
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

**`pyproject.toml`:**
```toml
[project]
name = "orders-report"
version = "0.1.0"
description = "Validate a directory of order CSV files and produce a JSON summary."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0,<3.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.5",
    "mypy>=1.10",
]
```

The development tools live in a `[dependency-groups]` `dev` group — the
same mechanism `uv add --dev` manages (§21) — not in
`[project.optional-dependencies]`, which is reserved for optional
features of the project itself (§22).

**Project setup, from a fresh clone:**
```bash
git clone <repository-url> orders-report
cd orders-report
uv sync
```

**Dependency declaration:** `pydantic` is the project's one genuine
runtime dependency (used, hypothetically, for record validation);
`pytest`, `ruff`, and `mypy` are development-only, never needed to
actually *run* the finished CLI.

**Dependency resolution and lock generation:** the first `uv sync`
(or an earlier `uv add pydantic` during initial development) triggers
resolution — `pydantic`'s own transitive dependencies get resolved
alongside it — and the result is written to `uv.lock`, which is then
committed to version control.

**Environment synchronization:** every subsequent `uv sync` (by any
developer, by CI, during a container build) reads that already-
resolved `uv.lock` and installs those locked versions for its
environment. Developers use plain `uv sync`; CI and container builds use
`uv sync --locked` so that a stale `uv.lock` is an error rather than a
silent re-resolution.

**Running the application:**
```bash
uv run python -m orders_report.cli --input-dir data/raw --output summary.json
```

**Running tests:**
```bash
uv run pytest
```

**Reproducibility:** because `uv.lock` is committed, a teammate
cloning this repository six months from now, and CI running against
tomorrow's commit, both get the **same locked** `pydantic` (and its
transitive dependencies) that were originally resolved and tested
against — not whatever happens to be the latest available version at
whatever moment they happen to run `uv sync`.

**CI/CD usage:**
```bash
uv sync --locked
uv run --locked pytest
uv run --locked ruff check .
uv run --locked mypy .
```
Each CI run installs from the committed lock file as-is (and fails if
it is stale) — closing the "works in CI, fails elsewhere" gap directly
(§28).

**Production considerations:** a production deployment (or a container
build, §29) runs `uv sync --locked --no-dev` against the same
committed `uv.lock`, and — per §21's separation — does not install the
`dev` group at all, since `pytest`/`ruff`/`mypy` serve no purpose once
the application is actually deployed and running.

## 35. Exercises + Answer Key

**Beginner**

1. Given `requests` (imported directly by your code) and `urllib3`
   (which your code never imports, but `requests` needs), identify
   which is a direct dependency and which is transitive.
2. Read this `pyproject.toml` snippet and state, in your own words,
   what each line means:
   ```toml
   [project]
   name = "widget-tool"
   version = "1.2.0"
   requires-python = ">=3.11"
   dependencies = ["click>=8.0,<9.0"]
   ```
3. Explain, in one or two sentences each, what `pyproject.toml` is for
   and what `uv.lock` is for, making the distinction between them
   clear.
4. What does `uv sync` do, in your own words?

**Intermediate**

5. Write the `uv` command to add `httpx` as a runtime dependency with
   a minimum version of `0.27`.
6. Write the `uv` command to add `pytest` as a development dependency.
7. Given `A requires B < 5` and a separately-added dependency
   `C requires B >= 3`, explain why this does *not* cause a conflict,
   and name one version of `B` that would satisfy both.
8. What is the difference between running `python app.py` directly and
   running `uv run python app.py`? Which would you use, and why?
9. Explain the difference between `dependencies` and
   `optional-dependencies` in `pyproject.toml`.

**Advanced**

10. Design a reproducible onboarding workflow (as a short sequence of
    commands) for a new team member joining a `uv`-managed project,
    and explain what guarantees each step provides.
11. A teammate manually edited `uv.lock` to change one package's
    pinned version, without touching `pyproject.toml`. Explain why
    this is risky, and describe the correct way to achieve the same
    goal.
12. Design a dependency strategy (version constraint style and
    lock-file policy) for (a) an internal CLI application your team
    deploys, and (b) an open-source library your team publishes.
    Justify the difference.
13. A resolver reports a conflict between two of your dependencies
    over a shared transitive package. Describe your systematic
    diagnostic process, step by step.
14. Design the dependency-installation stage of a CI pipeline for a
    `uv`-managed project, explaining why each command is included and
    in what order.

**Answer key**

1. `requests` is direct (imported explicitly by your code); `urllib3`
   is transitive (needed only because `requests` itself depends on
   it) (§1, §9).
2. `name`/`version` identify the project and its current version;
   `requires-python` means this project needs Python 3.11 or newer;
   `dependencies` declares one runtime dependency, `click`, constrained
   to any 8.x release (§4–§8).
3. `pyproject.toml` declares what the project *requires* (intent,
   often expressed as flexible version ranges); `uv.lock` records
   exactly which versions were *resolved* to satisfy those
   requirements, for reproducible installation (§13, §16).
4. It makes sure the lock file is current (re-locking if
   `pyproject.toml` changed, unless `--locked`/`--frozen` is given),
   then updates the project's virtual environment to match it —
   installing anything missing and aligning versions with what's
   locked (§23).
5. `uv add "httpx>=0.27"` (§20).
6. `uv add --dev pytest` (§21).
7. No conflict, because both constraints can be satisfied
   simultaneously — any `B` version that is both `< 5` and `>= 3`
   (e.g., `B == 4.0`) satisfies both `A`'s and `C`'s requirements at
   once (§10).
8. `python app.py` runs against whatever Python/environment happens to
   currently be active in the shell, which may not have the project's
   dependencies correctly installed; `uv run python app.py` executes
   inside the project's own managed, correctly-resolved environment —
   `uv run` is the safer, more reliable choice for any project-related
   command (§24).
9. `dependencies` are always installed for anyone using the project;
   `optional-dependencies` (extras) define named, opt-in groups of extra
   dependencies for specific optional *features* (§22) that aren't
   installed unless specifically requested. Development tools belong in
   a separate mechanism, `[dependency-groups]` (§21), not in extras.
10. A reasonable workflow: `git clone <repo>`, `cd <repo>`, `uv sync`
    — each step's guarantee: cloning gets the exact committed
    `pyproject.toml`/`uv.lock`; `uv sync` installs the locked
    dependency versions, so this new environment matches every other
    team member's (for the same platform and Python version), with zero
    manual dependency installation steps (§27).
11. Risky because `uv.lock` is meant to be a generated, internally
    consistent artifact — hand-editing one entry can leave it
    describing a state the resolver never actually verified as
    consistent with the rest of the locked graph, and the change will
    be silently overwritten or become confusingly stale the next time
    `uv` regenerates it. The correct approach: adjust the relevant
    constraint in `pyproject.toml` (or run the appropriate `uv`
    update command) and let `uv` re-resolve and re-lock properly
    (§14, §26, §32 mistake 3).
12. (a) The internal application should use bounded ranges (§8) for
    its own review comfort, but rely primarily on its committed
    `uv.lock` for actual reproducibility across dev/CI/production
    (§30). (b) The published library should favor version *ranges*
    (not exact pins) in its declared `dependencies`, since its
    consumers will resolve those ranges alongside their own project's
    other requirements; the library's own lock file, if it has one, is
    a development-time convenience only, never shipped to or used by
    consumers (§30).
13. A reasonable process: read the resolver's error message carefully
    to identify exactly which packages and constraints conflict;
    identify which of your own *direct* dependencies introduced each
    conflicting transitive requirement; check whether upgrading (or,
    if appropriate, downgrading) one of those direct dependencies would
    relax the conflicting transitive constraint; reconsider whether any
    of your own declared version constraints are more restrictive than
    genuinely necessary — never force an override past a real,
    unresolved conflict (§11).
14. A reasonable pipeline: `uv sync --locked` (install the locked
    dependencies, failing if `uv.lock` is stale, so the versions used in
    development are used here too) → `uv run --locked pytest` (verify
    correctness against those dependencies) → `uv run --locked ruff
    check .` / `uv run --locked mypy .` (additional quality gates, run
    in the same environment) — each step deliberately runs *after* the
    sync, and every command uses `uv run` rather than a bare
    `python`/tool invocation, so every stage uses the same locked
    dependency set (§28, §24).

## 36. Debugging Lab

**1. Dependency cannot be resolved**
```
error: No solution found when resolving dependencies:
  Because project depends on A>=2 and A>=2 depends on B<5,
  and project depends on C, and C depends on B>=6, no solution exists.
```
*Diagnosis:* read the error precisely — it already names the exact
conflicting constraints. *Root cause:* `A` and `C` require mutually
incompatible versions of `B` (§10–§11). *Fix:* check whether a
different version of `A` or `C` relaxes its own requirement on `B`;
if not, this may indicate `A` and `C` are genuinely incompatible in
your project and one may need to be replaced. *Prevention:* review a
new dependency's own transitive requirements (via its own published
metadata) before adding it, especially if the project already has many
existing dependencies.

**2. Package installed but not declared**
A teammate's environment has a package installed that isn't listed
anywhere in `pyproject.toml`. *Diagnosis:* check whether it was
installed manually (outside `uv add`) at some point. *Root cause:*
§32 mistake 10 — a manual install with no corresponding declaration.
*Fix:* if the package is genuinely needed, add it properly with
`uv add`; if it isn't actually needed, it can simply be left out of a
fresh `uv sync` (which won't install anything not declared).
*Prevention:* always use `uv add` for anything the project genuinely
needs, never a manual, undeclared install.

**3. Package works locally but fails in a clean environment**
*Diagnosis:* run `uv sync` into a genuinely fresh virtual environment
(or a clean container) and reproduce the failure there. *Root cause:*
almost always §32 mistake 10 again — something manually installed
locally (directly, or as a side effect of installing something else
globally) that was never actually declared, so a truly clean
environment (installing only from `pyproject.toml`/`uv.lock`) doesn't
have it. *Fix:* identify the missing dependency and add it properly.

**4. Wrong Python environment**
```bash
$ uv run python -c "import myapp"
ModuleNotFoundError: No module named 'myapp'
```
despite `myapp` clearly being part of the project.
*Diagnosis:* confirm the project's own package is actually installed
(editably) into its managed environment (e.g. check `uv pip list` or
`uv run python -c "import sys; print(sys.path)"`), per
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)'s
§5 src-layout discussion. *Root cause:* a src-layout project's own
package needs to be part of the resolved/installed project, not just
its dependencies — depending on project configuration, this may
require confirming the project itself (not merely its dependencies)
is correctly set up for editable use. Whether `uv sync` installs the
project itself depends on the project's configuration (for example,
whether it is set up as a package with a `[build-system]`) and the `uv`
version, so *fix* it by verifying with `uv --help`/current
documentation how your `uv` version handles installing the project's
own package as part of `uv sync`.

**5. `pyproject.toml` changed but the environment is stale**
A teammate added a new dependency to `pyproject.toml` by hand, but
never ran anything afterward — their own environment is missing it,
and so is `uv.lock`. *Diagnosis:* compare `pyproject.toml`'s declared
dependencies against `uv.lock`'s recorded ones — they no longer
match. *Root cause:* §26 — editing `pyproject.toml` alone doesn't
trigger resolution or installation. *Fix:* run `uv lock` (to
re-resolve) followed by `uv sync` (or simply `uv sync`, which
typically handles both) to bring both `uv.lock` and the environment
back in line.

**6. Lock file/environment mismatch**
`uv.lock` and `pyproject.toml` are both up to date and consistent with
each other, but a developer's *actual installed environment* still
doesn't match (perhaps because they installed something manually on
top of it, per mistake 10 again). *Diagnosis:* run `uv sync` and
observe what it changes. *Root cause:* the environment drifted from
the lock file independently of any project-file change. *Fix:* `uv
sync` should, by design, reconcile this automatically — bringing the
environment back to exactly what's locked.

**7. Conflicting dependency versions**
Two teammates each independently ran `uv add` for two different
packages, in two different branches, and each branch's `uv.lock` now
reflects a different resolution. *Diagnosis:* this is a normal,
expected merge conflict in `uv.lock`, not a project bug. *Root cause:*
`uv.lock` is a generated file that changes whenever dependencies
change — parallel, independent changes on different branches will
conflict when merged, exactly like any other file two people edit
concurrently. *Fix:* after merging `pyproject.toml`'s changes cleanly,
re-run `uv lock` (or `uv sync`) to regenerate a fresh, consistent
`uv.lock` reflecting *both* changes together, rather than attempting
to manually merge `uv.lock`'s own contents.

**8. Missing development dependency**
`uv run pytest` fails with `ModuleNotFoundError: No module named
'pytest'` even though the project clearly uses pytest for testing.
*Diagnosis:* check whether `pytest` was ever actually added as a
dependency (development or otherwise) with `uv add --dev pytest`, or
merely assumed to be available. *Root cause:* §32 mistake 10's
"assumed, not declared" pattern, specifically for a development
dependency. *Fix:* `uv add --dev pytest`, then re-run.

**9. `uv run` vs. direct Python behaving differently**
`uv run python app.py` works; a bare `python app.py` (run without
`uv run`, perhaps from an old habit or a script that forgot to use it)
fails with missing-dependency errors. *Diagnosis:* compare
`sys.executable` and `sys.path` under each invocation. *Root cause:*
the bare `python` command is very likely resolving to a *different*
Python interpreter/environment than the project's own managed one —
exactly the scenario §24 warns against. *Fix:* consistently use `uv
run` for anything related to this project, everywhere (scripts,
documentation, CI configuration).

**10. A dependency update unexpectedly changes transitive packages**
Running an update for one direct dependency also changes several
*unrelated*-looking transitive packages in `uv.lock`. *Diagnosis:*
review the actual diff of `uv.lock` — is the updated direct dependency
now requiring newer versions of its own transitive dependencies than
before? *Root cause:* this is often entirely expected — updating a
direct dependency can legitimately require the resolver to also update
whatever it depends on, since resolution finds one mutually-compatible
graph, not each package's version independently. *Fix:* this isn't
necessarily a bug at all; review the actual changes (via `uv.lock`'s
version-controlled diff, per §31's security-review practice) to
confirm they're expected and acceptable before committing, rather than
assuming an update should only ever touch the one package you asked
for.

## 37. Interview + Architecture Questions

1. What is a dependency, and what's the difference between a direct
   and a transitive dependency?
2. What is `pyproject.toml`, and why is it more than just "the
   dependencies file"?
3. What does `requires-python` declare, and why does it matter?
4. Explain the difference between `>=2.0`, `==2.0`, and `>=2.0,<3.0` as
   version specifiers.
5. What does a dependency resolver actually do?
6. Describe a scenario where dependency resolution genuinely fails,
   and explain why forcing an install past that failure is dangerous.
7. What is a virtual environment, and why does per-project isolation
   matter?
8. What is a lock file, and why does it exist?
9. Precisely distinguish `pyproject.toml` from `uv.lock`.
10. What is `uv`, and how does it differ from `pyproject.toml` as a
    standard?
11. What does `uv init` do?
12. What does `uv add requests` actually change, step by step?
13. What does `uv sync` do, and when would you run it?
14. What does `uv run` do, and why is it safer than running a command
    directly?
15. What does `uv lock` do, and how does it differ from `uv sync`?
16. How would you add a development-only dependency, and why should it
    be kept separate from runtime dependencies?
17. What are optional dependencies/extras, and why do they exist?
18. Why does reproducibility matter for local development, CI/CD, and
    production deployment specifically?
19. Explain the key difference between an application's and a
    library's ideal dependency-versioning strategy.
20. What are the security risks of both over-updating and
    under-updating dependencies, and how would you balance them?

**Answer key**

1. A dependency is external code a project needs but doesn't write
   itself; a direct dependency is one the project explicitly declares
   because it needs it (typically because its code imports it); a transitive dependency is one a direct dependency
   itself needs, pulled in automatically (§1, §9).
2. It's a standardized project configuration file holding not just
   dependency declarations, but also project metadata, build
   configuration, and often tool configuration — all in one
   standardized location at the project root (§3).
3. It declares the minimum (and optionally maximum) Python version(s)
   the project supports, letting installation tools reject an
   incompatible interpreter upfront rather than failing confusingly
   later (§6).
4. `>=2.0` means version 2.0 or any newer version, unconstrained above;
   `==2.0` means exactly that one version, no others; `>=2.0,<3.0`
   means any 2.x version, explicitly excluding an eventual 3.0 — a
   minimum, an exact pin, and a bounded range, respectively (§8).
5. It takes every declared requirement (direct and transitive) and
   finds one specific set of exact versions that satisfies every
   constraint simultaneously, essentially solving a constraint-
   satisfaction problem over the project's full dependency graph (§10).
6. Two dependencies each require mutually incompatible versions of a
   shared transitive package (e.g. one needs `B<5`, another needs
   `B>=6`) — no valid assignment exists. Forcing an install past this
   is dangerous because it produces an environment that violates a
   real, declared constraint, risking subtle runtime failures instead
   of a clear, upfront error (§11).
7. A virtual environment is an isolated set of installed packages
   specific to one project; per-project isolation matters because
   different projects (or the system Python itself) may need
   different, incompatible versions of the same package, which cannot
   coexist in one shared, global installation (§12).
8. A lock file is a generated record of the exact, resolved versions
   of every dependency; it exists to make dependency installation
   deterministic and reproducible, rather than re-resolving (and
   potentially arriving at a different answer) every time (§13).
9. `pyproject.toml` is human-authored and declares requirements
   (often as flexible ranges); `uv.lock` is machine-generated and
   records one exact, resolved answer to those requirements, including
   every transitive dependency (§16).
10. `uv` is a tool that reads and writes the `pyproject.toml`
    standard (among other things) while also managing virtual
    environments, resolution, locking, and running commands — the
    standard and the tool are related but distinct: other tools could,
    in principle, also work with the same standard file (§17).
11. It creates a new project skeleton, including a starting,
    syntactically valid `pyproject.toml` with basic metadata already
    filled in (§19).
12. It adds `requests` to `pyproject.toml`'s `dependencies`, resolves
    the full dependency graph (including `requests`' own transitive
    dependencies), updates `uv.lock` with the resolved versions, and
    synchronizes the project's virtual environment to match — all in
    one command (§20).
13. It makes sure the lock file is current (re-locking if
    `pyproject.toml` changed, unless `--locked`/`--frozen` is used) and
    brings the actual installed environment into alignment with it; the
    strict `uv sync --locked` form fails instead of re-locking, and
    `--no-dev` skips the development group; run it after cloning a project, after pulling changes to
    `pyproject.toml`/`uv.lock`, or to confirm your environment is
    currently correct (§23).
14. It executes a given command inside the project's own managed
    virtual environment automatically; it's safer than running a
    command directly because a bare invocation might silently use the
    wrong Python interpreter or environment, missing (or mismatching)
    the project's actual resolved dependencies (§24).
15. `uv lock` re-runs resolution and updates `uv.lock` without
    touching the installed environment; `uv sync` installs/aligns the
    actual environment to match whatever the current lock file (freshly
    updated or not) specifies (§26).
16. Using `uv add --dev <package>`, which records it in the `dev`
    dependency group (`[dependency-groups]`); development dependencies (test
    runners, linters, type checkers) are needed only while developing,
    never to actually run the finished application, so keeping them
    separate avoids installing unnecessary packages (and their own
    transitive dependencies and potential vulnerabilities) into
    production (§21).
17. Named, opt-in groups of additional dependencies for optional
    features, declared under `[project.optional-dependencies]` (distinct
    from development dependency groups); they exist so a project can support extra functionality without forcing
    every user to install dependencies they don't need (§22).
18. Because each of these environments needs to behave like the
    others for confidence that "it works" actually means it will keep
    working after deployment — reproducibility (via a shared, committed
    lock file used strictly in CI and production) is what keeps
    development, CI, and production on the same locked dependency
    versions for their platform (§27–§29).
19. An application controls its own deployment environment entirely,
    so exact reproducibility via a committed lock file is highly
    valuable and carries no downside; a library's dependencies get
    resolved *inside* someone else's project alongside their other
    requirements, so flexible version ranges (rather than exact pins)
    are more valuable, since they avoid unnecessarily constraining
    what the consumer's own resolution can achieve (§30).
20. Over-updating without review risks introducing an unreviewed
    breaking change or newly-introduced vulnerability; under-updating
    risks running known, unpatched vulnerabilities indefinitely. The
    balance: review and update dependencies deliberately and
    periodically, using the lock file's own version-controlled history
    to see exactly what changed with each update, rather than either
    extreme (§31).

## 38. Knowledge Check

**Conceptual**
1. In your own words, why can't `pyproject.toml` alone guarantee
   reproducibility, without a lock file?
2. Why does `uv` manage virtual environments automatically rather than
   requiring a separate manual `venv` step?

**`pyproject.toml` reading**
3. Given
   ```toml
   [project]
   name = "tool"
   version = "2.0.0"
   requires-python = ">=3.10,<3.13"
   dependencies = ["click>=8.1"]
   ```
   what Python versions does this project support, and what does it
   require of `click`?

**Dependency-resolution reasoning**
4. Two dependencies require `X>=1.0,<2.0` and `X>=1.5,<2.5`
   respectively. What is the valid range for `X` that satisfies both?

**Command-output reasoning**
5. After running `uv add "flask>=3.0"`, which two files would you
   expect to see changed, and what changed in each?

**Debugging**
6. A CI job fails with a dependency resolution error that never occurs
   on any developer's local machine. What's the first thing you'd
   check, given that both environments claim to use the same
   `uv.lock`?

**Design**
7. You're deciding whether to commit `uv.lock` for a small internal
   automation script versus a published open-source library. What
   would you decide for each, and why?

---

**Answer key**

1. Because `pyproject.toml`'s version ranges can be satisfied by
   different specific versions at different points in time (as new
   package releases become available) — without a lock file recording
   one specific, exact resolution, two installs at two different times
   could legitimately produce two different sets of versions, even
   from the identical `pyproject.toml` (§13, §15).
2. Because manually creating, activating, and remembering to use a
   separate virtual environment is an extra manual step users can
   forget or get wrong (accidentally installing into the system Python
   instead, per §32 mistake 1); `uv run`/`uv sync` fold environment
   management into the same commands used for everything else,
   removing that failure mode by design (§12, §17).
3. Python 3.10 up to (but not including) 3.13; `click` version 8.1 or
   any newer release, unconstrained above (§6, §8).
4. `X` must satisfy both `[1.0, 2.0)` and `[1.5, 2.5)` simultaneously —
   the overlap is `[1.5, 2.0)`, i.e. any `X` version from 1.5 up to
   (but not including) 2.0 (§10).
5. `pyproject.toml` — `flask` added to `dependencies` with the given
   constraint; `uv.lock` — updated to include `flask`'s newly resolved
   exact version, along with any of its own transitive dependencies'
   resolved versions (§20).
6. Confirm that CI is actually using the committed `uv.lock` as-is
   (`uv sync --locked`, rather than plain `uv sync`, which re-locks a
   stale file, or some separate, possibly stale cached environment, or
   accidentally re-resolving fresh instead of installing from the lock
   file) — a resolution error appearing only
   in CI despite an identical lock file strongly suggests CI isn't
   actually consuming that lock file the way it appears to be (§28,
   §36 scenario 6).
7. For the small internal automation script (an application, per
   §30): commit `uv.lock` — reproducibility across whoever runs it,
   and whenever, is valuable and low-cost. For the published
   open-source library (per §30): a lock file may still be maintained
   for the library's *own* development/CI reproducibility, but it is
   not something consumers of the library rely on directly — the
   library's actual `dependencies` version ranges are what matters
   most to them, since they'll resolve it within their own project's
   environment.

## 39. Production Checklist

**Project metadata**
- [ ] `pyproject.toml` exists at the project root with accurate
      `name`, `version`, and `description`.
- [ ] `requires-python` is declared and reflects the versions the
      project is actually tested against.

**Dependency declarations**
- [ ] Every runtime dependency the project needs (typically everything
      its code imports) is declared in `dependencies` — nothing relied upon that isn't declared.
- [ ] Direct dependencies are distinguished from transitive ones; only
      genuinely direct dependencies are listed explicitly.
- [ ] Version constraints are deliberate (bounded ranges or justified
      minimums), not left unconstrained by default and not blindly
      pinned to exact versions everywhere.

**Lock file**
- [ ] `uv.lock` is committed to version control (for applications,
      §14, §30) and kept in sync with `pyproject.toml` at every commit.
- [ ] `uv.lock` is never hand-edited; changes flow through
      `pyproject.toml` plus the appropriate `uv` command.

**Reproducibility**
- [ ] A fresh clone plus `uv sync` reliably reproduces a working
      environment for the supported platforms, with no undocumented manual installation steps.
- [ ] Virtual environment isolation is used consistently (via `uv`),
      never a global/system Python install.

**Runtime vs. development dependencies**
- [ ] Test/lint/type-check tools are declared as development
      dependencies (a `[dependency-groups]` `dev` group), separate from
      runtime `dependencies` and from optional-dependency extras.
- [ ] Production/deployment installs skip development dependencies
      entirely (e.g. `uv sync --locked --no-dev`).

**Secrets**
- [ ] No secrets are declared or embedded anywhere in
      `pyproject.toml` or `uv.lock` (neither file is an appropriate
      place for them at all — see
      [09-environment-configuration-and-input-validation.md](../05-Text-Files-Structured-Data-and-CLI-Programs/09-environment-configuration-and-input-validation.md)).

**Conflicts and updates**
- [ ] Dependency conflicts are diagnosed and resolved at the
      constraint level, never forced past.
- [ ] Dependency updates are reviewed deliberately (via the lock
      file's version-controlled diff) rather than applied blindly or
      never applied at all.

**CI/CD and deployment**
- [ ] CI installs dependencies via `uv sync --locked` against the
      committed `uv.lock`, not a fresh, independent resolution.
- [ ] Every CI/build/deployment stage uses `uv run` (with `--locked`
      where the lock file must be accepted as-is, or an equivalent
      environment-correct invocation), not a bare command that might
      resolve to the wrong environment.
- [ ] Container/deployment builds install from the same locked
      dependencies used in development and CI.

**Security**
- [ ] Dependencies (direct and transitive) are periodically reviewed
      for known vulnerabilities and update recency, not left
      indefinitely frozen or indefinitely unreviewed.
