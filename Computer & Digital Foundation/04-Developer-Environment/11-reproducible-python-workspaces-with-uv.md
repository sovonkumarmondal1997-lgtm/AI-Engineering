# Reproducible Python Workspaces with uv

**Module:** Developer Environment
**Roadmap reference:** Stage 0 — Computer, Linux, and Developer Foundations, Gap 0D —
"Reproducible Python workspace" (extends Module 0.4 — Developer Environment)
**Concept(s) covered:** the Python interpreter, isolated environments, `uv`, `venv`, `pip`,
`pyproject.toml`, dependency declarations, lock files, reading a traceback
**Prerequisites:** `06-virtual-environments.md`, `07-package-managers.md`,
`08-project-structure.md`, `09-python-tooling.md`
**Status:** Not Started

---

## Learning Outcomes

By the end of this lesson you will be able to:

- Check which Python interpreter and version you have, from the terminal.
- Explain why every project needs its own isolated environment, with a concrete example of what
  goes wrong without one.
- Explain the distinct roles of `uv`, `venv`, `pip`, and `pyproject.toml` — and where dependency
  declarations and lock files fit.
- Initialize a minimal project with `uv`, inspect its `pyproject.toml`, and run a program inside it.
- Sync a project's dependencies reproducibly.
- Read a Python traceback from bottom to top and identify the actual failing line.
- Explain why mixing `uv`, `venv`, and `pip` randomly within one project causes problems.
- Diagnose the most common beginner environment problems: missing Python, missing `uv`, the wrong
  interpreter, and an unsynced environment.

## Prerequisites

- **`06-virtual-environments.md`** — the concept of an isolated environment.
- **`07-package-managers.md`** — what a package manager does.
- **`08-project-structure.md`** — where `pyproject.toml` sits in a project.
- **`09-python-tooling.md`** — how these tools fit together, at a conceptual level.

This lesson turns those concepts into one consistent, repeatable, hands-on workflow.

## Key Terms

- **Python interpreter** — the program that actually reads and executes Python source code; your
  machine may have more than one installed.
- **Isolated environment** — a self-contained space holding one specific interpreter and its own
  installed packages, separate from any other project's.
- **`uv`** — a modern, fast tool that can create and manage a project's environment and its
  dependencies in one workflow.
- **`venv`** — Python's built-in tool for creating an isolated environment (without managing
  dependency installation itself).
- **`pip`** — Python's traditional package installer, used to install packages into an environment.
- **`pyproject.toml`** — a file declaring a project's metadata and its dependencies.
- **Dependency declaration** — a statement in `pyproject.toml` naming a package your project needs
  (and optionally, an acceptable version range).
- **Lock file** — a file recording the *exact* version of every dependency (and its own
  dependencies) that was actually installed, so a future install reproduces precisely the same
  environment.
- **Traceback** — the multi-line message Python prints when a program raises an unhandled error,
  showing the chain of calls that led to it.

---

## 1. Why Reproducibility Matters Before You Write Any Real Code

"It works on my machine" is one of the most common, most avoidable failures in software. It almost
always traces back to one thing: an environment that was never actually reproducible — packages
installed by hand, in whatever order, with whatever versions happened to be available that day. This
lesson builds the habit of making every project's setup explicit and repeatable from the very first
`uv init`, so a script running on your machine will run the same way on anyone else's.

## 2. The Python Interpreter, and Checking Its Version

```bash
python3 --version
which python3
```

- `python3 --version` — prints the interpreter's version.
- `which python3` — prints the full path to the actual interpreter program that command runs.

**Why check both:** a machine can have multiple Python interpreters installed (a system one, one
from a package manager, one inside a project environment). `which` tells you exactly which one
you're about to use — this single check prevents a large share of "wrong Python" confusion later.

## 3. Why Every Project Needs Its Own Isolated Environment

Imagine two projects on the same machine: Project A needs version 1 of a library; Project B needs
version 2. If both projects shared one global set of installed packages, only one version could be
installed at a time — installing Project B's dependencies would silently break Project A.

An **isolated environment** solves this by giving each project its own private set of installed
packages, tied to one specific interpreter. Installing a package for Project A never touches Project
B's environment at all — they simply don't share anything.

## 4. The Roles of `uv`, `venv`, `pip`, and `pyproject.toml`

| Tool | What it actually does |
|---|---|
| **`venv`** | Creates the isolated environment itself — a private folder holding an interpreter and its own packages. It does not install packages on its own. |
| **`pip`** | Installs, upgrades, and removes packages *into* an environment. It does not create the environment itself. |
| **`uv`** | A newer tool that can do both jobs — create the environment and manage its dependencies — through one consistent workflow, and is often significantly faster. |
| **`pyproject.toml`** | Declares a project's dependencies and metadata as a file, so "what this project needs" is written down, not just remembered. |

**The practical distinction:** `venv` + `pip` are two separate tools you coordinate yourself;
`uv` is one tool that coordinates the same underlying ideas for you. Both approaches produce a
working isolated environment — this lesson teaches `uv` as the default for new projects, while
making sure you can recognize and work with `venv`/`pip` in projects that already use them
(Section 6).

## 5. Dependency Declarations and Lock Files

A **dependency declaration**, inside `pyproject.toml`, names a package your project needs:

```toml
[project]
dependencies = [
    "requests>=2.31",
]
```

This says "this project needs `requests`, version 2.31 or newer" — but doesn't pin an exact version.
A **lock file** (created automatically by `uv` when you sync dependencies, Section 10) records the
*exact* version actually installed, down to every indirect dependency. **Why both matter together:**
the declaration expresses intent ("something compatible with 2.31 or later"); the lock file
guarantees reproducibility ("this exact set of versions is what was tested and is known to work") —
installing from the lock file on a different machine reproduces the identical environment, not just
a roughly similar one.

## 6. A Consistent Beginner Workflow

**The rule this lesson teaches:** use `uv` for every new project you start yourself. Recognize and
work correctly with `venv`/`pip` when you join or clone an existing project that already uses them
— don't try to convert someone else's project to a different tool just to match your own
preference. Section 12 explains why mixing tools *within* one project, rather than choosing one
consistently, causes real problems.

## 7. Step-by-Step: Initializing a Minimal Project with `uv`

```bash
mkdir -p ~/practice-shell/uv-workspace
cd ~/practice-shell/uv-workspace
uv init
```

- `uv init` — creates a new, minimal project in the current directory: a `pyproject.toml`, a small
  starter Python file, and project scaffolding — without installing anything yet.

```bash
ls -la
```

You should see `pyproject.toml` and a small `.py` file it generated, among a few other project
files.

## 8. Inspecting `pyproject.toml`

```bash
cat pyproject.toml
```

**Example content** (illustrative — your exact output may differ slightly by `uv` version):

```toml
[project]
name = "uv-workspace"
version = "0.1.0"
description = "Add your description here"
requires-python = ">=3.11"
dependencies = []
```

Read this line by line: `name` and `version` are metadata (Section 4's "declares a project's ...
metadata"); `requires-python` states which interpreter versions this project supports; `dependencies
= []` means no packages are declared yet — exactly what you'd expect from a fresh, minimal project.

## 9. Running a Simple Program Through the Project Environment

```bash
uv run python -c "import sys; print(sys.executable); print(sys.version)"
```

- `uv run COMMAND` — runs `COMMAND` inside this project's own isolated environment, creating that
  environment automatically the first time if it doesn't exist yet.

**What to notice in the output:** `sys.executable` points to an interpreter *inside* this project's
own environment folder (not your system Python from Section 2) — direct proof that `uv run`
executed your code through the isolated environment, not the global interpreter.

## 10. Syncing Dependencies

Add a small, harmless dependency to `pyproject.toml`'s `dependencies` list (for example,
`"requests>=2.31"`), then:

```bash
uv sync
```

- `uv sync` — reads `pyproject.toml`'s declared dependencies, resolves exact compatible versions,
  installs them into the project's environment, and writes (or updates) a lock file recording
  exactly what was installed.

```bash
cat uv.lock | head -n 20
```

Confirm a lock file now exists, and skim its first lines — you don't need to fully understand its
format, only recognize that it records exact, specific versions (Section 5), not the loose ranges
`pyproject.toml` declared.

## 11. Reading a Traceback from Bottom to Top

Create a file, `broken.py`, with a deliberate, simple error:

```python
def divide(a, b):
    return a / b

print(divide(10, 0))
```

Run it:

```bash
uv run python broken.py
```

**Example traceback:**

```text
Traceback (most recent call last):
  File "broken.py", line 4, in <module>
    print(divide(10, 0))
  File "broken.py", line 2, in divide
    return a / b
ZeroDivisionError: division by zero
```

**Read it from the bottom up:** the **last line** names the actual error
(`ZeroDivisionError: division by zero`) — start here, not at the top. The line just above it
(`return a / b`) is the exact line that raised it. The lines above *that* show the chain of calls
that led there (`divide(10, 0)` was called from line 4). This bottom-to-top reading order is the
single most useful debugging habit for any Python error you'll encounter for the rest of this
roadmap.

## 12. Reproducibility and Clean Setup Instructions

A reproducible project lets someone else (or you, on a different machine) get to a working state
from nothing but your repository and a README. A good, minimal setup section reads like this:

```markdown
## Setup

1. Install `uv` (see uv's official documentation for your OS).
2. `uv sync`
3. `uv run python broken.py`
```

**Why this matters:** it doesn't say "install these seven packages in this order" — it says "run
`uv sync`," which reads `pyproject.toml` and the lock file and reproduces the *exact* environment,
every time, on any machine.

**Avoid randomly mixing tools within one project.** Running `pip install` by hand inside a
`uv`-managed project's environment can install a package that `pyproject.toml` and the lock file
don't know about — the next `uv sync` (on your machine or anyone else's) won't reproduce it,
silently breaking the exact reproducibility this whole lesson is about. Pick one workflow per
project, and let its own tool (`uv sync`, or `pip install -r requirements.txt` in a `venv`/`pip`
project) be the *only* way dependencies get installed.

## 13. Troubleshooting

| Problem | Likely cause | Safe next step |
|---|---|---|
| `python3: command not found` | Python isn't installed, or is installed as `python` not `python3` | Try `python --version`; if neither works, install Python 3 from your OS's official source (Section 2). |
| `uv: command not found` | `uv` isn't installed yet | Install it following `uv`'s own official documentation for your OS; then open a **new** terminal window before retrying. |
| `uv run` uses a different Python version than you expected | The project's `requires-python` in `pyproject.toml` doesn't match the interpreter you assumed | Check `pyproject.toml`'s `requires-python` value and compare it to `python3 --version` from Section 2 — `uv` selects a compatible interpreter, which may not be your system default. |
| `ModuleNotFoundError` for a package you're sure you declared | The environment hasn't been synced since you edited `pyproject.toml` | Run `uv sync` again — a dependency only becomes installed after syncing, not the moment it's added to the file. |

## 14. Why This Matters for AI Engineering

- **Every later Python, LLM, or backend project** in this roadmap starts exactly the way Section 7
  did: `uv init`, declare dependencies, `uv sync` — the same reproducible pattern, regardless of
  what the project actually does.
- **Reading a traceback bottom-to-top (Section 11)** is the single most common debugging action
  you'll take when a training script, an API call, or an agent's tool call fails — this lesson is
  the foundation every later Python debugging session builds on.
- **Lock files (Section 5)** are exactly what lets a teammate, a CI system, or a deployment
  pipeline reproduce your exact environment — critical the moment more than one machine is
  involved, which is essentially immediately in real AI-engineering work.
- **Avoiding mixed-tool environments (Section 12)** prevents the specific, common failure mode
  where a project "works for me" because of a hand-installed package nobody else's setup has.

---

## Exercises

1. Check your Python version and the full path to your interpreter with `python3 --version` and
   `which python3`. Write both down.
2. Initialize a new `uv` project, and read through the generated `pyproject.toml` line by line,
   explaining each field in your own words.
3. Add one small dependency to `pyproject.toml`, run `uv sync`, and confirm a lock file now exists.
4. Write a small script with a deliberate, simple error (a typo in a variable name, or a division
   by zero like Section 11's example). Run it, and before reading the traceback's earlier lines,
   read only the **last** line and state what you think went wrong.
5. Write a two-line `## Setup` section for a fictional project, following Section 12's pattern.

## Expected Results

- **Exercise 1:** the path from `which python3` should be a real, existing file path on your
  system.
- **Exercise 2:** your explanation should correctly separate `name`/`version` (metadata) from
  `dependencies` (what the project needs), matching Section 4 and Section 8.
- **Exercise 3:** `uv.lock` (or your `uv` version's equivalent lock filename) exists and contains
  specific version numbers, not loose ranges.
- **Exercise 4:** your read of the last line alone should already correctly identify the error
  type — confirming the bottom-to-top approach from Section 11 works even before reading the full
  trace.
- **Exercise 5:** your setup section should rely on a single sync command, not a list of manual
  package installs.

---

## Summary

Every project needs its own isolated environment so its dependencies can never silently conflict
with another project's. `venv` creates an environment; `pip` installs into one; `uv` does both,
consistently, and is this lesson's default for new projects. `pyproject.toml` declares what a
project needs; a lock file records exactly what was installed, making setup reproducible on any
machine via a single `uv sync`. Reading a traceback from the bottom up — error first, then the
exact failing line, then the chain of calls above it — is the core Python debugging skill this
lesson builds. Never mix tools at random within one project; let one workflow's own command be the
only way dependencies get installed.

## Completion Checklist

- [ ] I checked my Python version and interpreter path, and know the difference between them.
- [ ] I can explain, with a concrete example, why two projects sharing one global environment can
      break each other.
- [ ] I can explain the distinct roles of `uv`, `venv`, `pip`, and `pyproject.toml` in my own words.
- [ ] I initialized a project with `uv init` and read through its generated `pyproject.toml`.
- [ ] I ran a program with `uv run` and confirmed it used the project's own interpreter, not my
      system one.
- [ ] I added a dependency, ran `uv sync`, and confirmed a lock file was created.
- [ ] I deliberately caused and then correctly read a real traceback, bottom to top.
- [ ] I can explain why mixing `pip install` by hand into a `uv`-managed project breaks
      reproducibility.
- [ ] I completed the exercises above and my results match the expected results.

---

_This lesson is complete. It covers reproducible Python workspaces from Stage 0 Gap 0D, building
directly on `06-virtual-environments.md`, `07-package-managers.md`, and `09-python-tooling.md`. It
intentionally does not teach Python language syntax, packaging for distribution (publishing to
PyPI), or every alternative Python packaging tool — those remain later, more advanced topics.
Secrets hygiene for exactly this kind of project is covered next, in
[`12-secrets-and-local-security-hygiene.md`](./12-secrets-and-local-security-hygiene.md)._
