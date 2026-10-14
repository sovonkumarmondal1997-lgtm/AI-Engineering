# Module 0.4 — Developer Environment

**Status:** Not Started
**Roadmap source:** Stage 0 — Computer, Linux, and Developer Foundations, Module 0.4 — "Developer
Environment"

This README is a **roadmap and navigation document only**. It defines what this module covers, in
what order, and why — it does not contain the lessons themselves. Lesson content is written later,
inside each numbered concept file, during the actual teaching phase.

---

## 1. Module purpose

Module 0.4 builds a real, working developer environment: an editor you can navigate confidently, a
debugger you can trust, and a Python setup that is isolated and reproducible per project. It is the
last module of Stage 0 and produces the actual workspace that Stage 1 — Programming Foundations
will be built in.

Everything from here on is written and run inside this environment. Without it, every later
mistake — a package installed in the wrong place, a script run with the wrong interpreter, an
untracked change — becomes confusing instead of routine.

## 2. Prerequisites

Modules 0.2 and 0.3 — Operating System Fundamentals and Command Line, specifically processes,
filesystems, permissions, and the terminal. A computer running Linux, Ubuntu, or WSL2 (Windows
Subsystem for Linux) is required, alongside VS Code and a recent Python installation.

## 3. Learning objectives

By the end of Module 0.4, the learner should be able to:

- Open a project folder (not individual files) in VS Code and navigate its Explorer, integrated
  terminal, search, and source-control views.
- Explain core IDE concepts: syntax highlighting, IntelliSense/autocomplete, and the difference
  between an editor and an IDE.
- Install and manage only trusted, necessary VS Code extensions.
- Explain what formatters and linters do and why they catch different classes of problems.
- Use a debugger to set a breakpoint, step through code, and inspect variables instead of
  debugging by scattering `print` statements.
- Explain why Python packages should be isolated per project, and create a virtual environment.
- Explain the difference between `pip`, `venv`, and `uv`, and use one workflow consistently.
- Explain a normal project's structure (source, tests, configuration, dependencies) and why it
  matters.
- Check the Python interpreter version, run a file, and read a traceback from bottom to top to find
  the actual error.
- Use `pyproject.toml` to understand a project's declared dependencies and metadata.

## 4. Learning sequence

Work through the numbered concept files in order. The editor and IDE concepts come first because
every later concept — the debugger, virtual environments, package managers — is used from inside
VS Code's terminal and panels.

| # | File | Concept(s) covered |
|---|---|---|
| 1 | [`01-vscode-and-terminal.md`](./01-vscode-and-terminal.md) | VS Code and the integrated terminal |
| 2 | [`02-ide-concepts.md`](./02-ide-concepts.md) | IDE concepts |
| 3 | [`03-extensions.md`](./03-extensions.md) | extensions |
| 4 | [`04-formatters-and-linters.md`](./04-formatters-and-linters.md) | formatters and linters |
| 5 | [`05-debugger.md`](./05-debugger.md) | debugger |
| 6 | [`06-virtual-environments.md`](./06-virtual-environments.md) | virtual environments |
| 7 | [`07-package-managers.md`](./07-package-managers.md) | package managers |
| 8 | [`08-project-structure.md`](./08-project-structure.md) | project structure |
| 9 | [`09-python-tooling.md`](./09-python-tooling.md) | Python tooling (`uv`, `pip`, `venv`, `pyproject.toml`) |
| 10 | [`10-git-github-and-ssh-basics.md`](./10-git-github-and-ssh-basics.md) | Git, GitHub, and SSH basics — repositories, commits, branches, remotes, pull requests, `.gitignore` |
| 11 | [`11-reproducible-python-workspaces-with-uv.md`](./11-reproducible-python-workspaces-with-uv.md) | reproducible Python workspaces with `uv` — isolated environments, dependency declarations, lock files |
| 12 | [`12-secrets-and-local-security-hygiene.md`](./12-secrets-and-local-security-hygiene.md) | secrets and local security hygiene — `.env`, `.env.example`, safe credential handling, exposure response |
| 13 | [`13-evidence-based-debugging-and-notes.md`](./13-evidence-based-debugging-and-notes.md) | evidence-based debugging and notes — the goal-assumptions-experiment loop and `learning-notes.md` |

## 5. Why this module matters for AI engineering

Every Python, backend, data, and AI project from Stage 1 onward is built, run, and debugged inside
the environment this module sets up. Concretely:

- **VS Code, the terminal, and the debugger** are how you will read tracebacks, step through model
  code, and inspect variables when a script produces the wrong output instead of the right one —
  far faster than debugging by trial and error.
- **Virtual environments (`venv`, `uv`)** keep each project's dependencies isolated, so installing
  one project's packages (for example, a specific ML library version) cannot silently break
  another project on the same machine.
- **`pip`, `venv`, and `uv`** are the exact tools used later to install and manage LLM SDKs, web
  frameworks, and data libraries — knowing the difference between them prevents mixing workflows
  and producing an environment nobody else can reproduce.
- **`pyproject.toml` and reproducibility** mean any later project — a FastAPI backend, a model
  fine-tuning script, an agent framework — can be set up identically on another machine or by a
  teammate, which is required once work moves beyond a single local script.
- **Reading a traceback from bottom to top** is the single most-used debugging skill in every later
  stage: it tells you exactly which line failed and why, before you touch any AI-specific tooling.
- **Git hygiene and secret safety**, covered alongside this module in the Stage 0 roadmap's gaps,
  belong here because this is where `.gitignore`, `.env` files, and committed dependencies are first
  set up — get them right once, in this module, and every later project inherits the habit.

Without this module, later Python errors, dependency conflicts, and "works on my machine" problems
have no reliable environment to fall back on and reproduce from.

## 6. Practical verification and projects

This module no longer keeps its own local `labs/`, `exercises/`, `examples/`, or `project/`
folders — the practical, verifiable work for all of Stage 0, including this module, is now
consolidated in the Stage 0 roadmap. See
[`../00-Stage-0-Overview/learning-plan.md`](../00-Stage-0-Overview/learning-plan.md) for:

- the audit evidence used to verify Module 0.4 is operational, not just read — creating an isolated
  workspace, installing one package, running a file, and documenting setup from a clean terminal
  (Section 2 — "Audit of the original four modules");
- **Gap 0A (Git, GitHub, and SSH basics)** and **Gap 0E (Secrets and local security hygiene)**,
  which extend this module with the version-control and secret-safety habits every reproducible
  Python workspace needs (Section 3 — "Gaps to close before Stage 1");
- **Project 0.1 — Developer Environment Health Check** and **Project 0.4 — Reproducible Python
  Workspace Bootstrap**, this module's main hands-on proof: a documented, version-controlled setup
  and a minimal `uv`-based Python project that another person could run from the README (Section 5
  — "Practical projects"); and
- the Stage 0 completion gate that this module feeds into, including "I can create and run a
  reproducible minimal Python workspace with `uv`" (Section 8 — "Stage 0 completion gate").

## 7. Projects

This module has two local, hands-on projects, built in a separate practice repository rather than
inside this curriculum folder. See [`Projects/README.md`](./Projects/README.md) for the index. They
practise environment verification, Git hygiene, reproducible Python setup with `uv`, reading a real
traceback, and secret safety — turning Topics 01–13 into a documented, version-controlled setup you
built yourself.

---

_This README defines structure and sequence only. No lesson content has been written. Each
numbered concept file is a scaffold — see the file itself for its current status._
