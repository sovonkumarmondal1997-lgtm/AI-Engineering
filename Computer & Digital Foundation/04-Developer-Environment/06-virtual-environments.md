# Virtual Environments

**Module:** Developer Environment
**Roadmap reference:** Stage 0 — Module 0.4 — Developer Environment
**Concept(s) covered:** virtual environments, `venv`
**Prerequisites:** Module 0.1 (How Computers Work), Module 0.2 (Operating System Fundamentals),
Module 0.3 (Command Line), Module 0.4 Lessons 01–05 (VS Code and Terminal, IDE Concepts, Extensions,
Formatters and Linters, Debugger)
**Status:** Complete

All commands and output shown in this lesson are illustrative teaching examples, clearly labeled as
such. No command was actually executed while writing this lesson, and no output is presented as a
genuine execution record.

---

## 1. Introduction

### What a virtual environment is

A **virtual environment** is an isolated, self-contained space on your computer where a specific
Python interpreter and a specific set of installed packages live, separate from the Python
interpreter and packages installed system-wide, and separate from any other project's virtual
environment.

### Why Python projects need isolated environments

A Python project is rarely just its own source code. It typically depends on **packages** —
pre-written code someone else published, that your project's code relies on to work. Different
projects, on the same computer, often need different packages, or even different *versions* of the
same package (expanded fully in Section 2). Without some way to keep each project's dependencies
separate, these needs can directly conflict with each other.

### The problem of dependency conflicts, briefly

If every project on a machine shared one single set of installed packages, two projects that need
different versions of the same package could not both be satisfied at the same time — installing the
version one project needs could break the other. Section 2 develops this problem in full before this
lesson introduces virtual environments as the solution.

### Why installing everything globally is problematic

"Globally" means installed once, for the whole machine, shared by every program and project that
uses that Python installation. This might seem simpler at first, but it means every project is
implicitly coupled to whatever the global environment currently contains — a change made for one
project's sake can silently affect every other project relying on that same global environment.

### The relationship between a project and its environment

A well-organized Python project has its own dedicated virtual environment, used specifically for that
project's own dependencies, kept separate from every other project's environment and from the
system's global Python installation. This lesson builds, step by step, a precise mental model of what
that environment actually is, why it works the way it does, and how to use it correctly and safely.

### The big picture

```text
Python Project
      |
Needs Dependencies
      |
Different Projects Need Different Versions
      |
Global Python Environment Becomes Problematic
      |
Virtual Environment
      |
Isolated Project Environment
      |
More Reproducible Development
```

This lesson does not teach virtual environments as a sequence of commands to memorize. The goal is
the underlying mental model above — understood precisely enough that the commands in Section 8 feel
like natural consequences of that model, not arbitrary incantations.

---

## 2. The Problem Before Virtual Environments

### A concrete scenario

```text
Project A
needs package X version 1

Project B
needs package X version 2
```

Both projects exist on the same machine. Both depend on a package called `X`. But `A` was built
against `X`'s older behavior (version 1), and `B` was built against `X`'s newer behavior (version 2)
— and these two versions are not interchangeable for these projects' purposes.

### Why a single shared/global environment creates problems

If there is only one global installation of `X` on the machine, it can only be *one* version at a
time. Whichever version is currently installed will work for one of the two projects and very likely
break the other. This is the **dependency conflict** at the center of this problem.

### Specific consequences of a shared, global environment

- **Dependency conflicts** — as above: two projects needing different, incompatible versions of the
  same package cannot both be satisfied by one shared installation.
- **Incompatible versions** — even without a direct conflict, a package version that works for one
  project's code may not behave the way another project's code expects.
- **Accidental upgrades** — installing or updating a package for one project's sake can silently
  upgrade the version another, unrelated project was relying on.
- **Accidental removals** — uninstalling a package no longer needed by one project can break another
  project that was quietly depending on it too.
- **Project coupling** — every project sharing the same global environment becomes implicitly coupled
  to every other project's dependency needs, even though the projects themselves may be entirely
  unrelated.
- **"Works on my machine" problems** — a project might behave correctly on a developer's machine
  purely because of whatever global packages happen to already be installed there, and fail
  differently on another machine, or after that machine's global environment changes.
- **Difficulty reproducing an environment** — without a clear, isolated record of exactly which
  packages and versions a specific project actually needs, recreating that project's working setup
  elsewhere (or later, on the same machine) becomes guesswork.

### An important accuracy boundary

Virtual environments, introduced in Section 4, address these problems by providing **isolation** —
but this lesson does not claim they solve every reproducibility problem on their own. Section 28
returns to this precisely: isolation is necessary but not, by itself, sufficient for complete
reproducibility, which also depends on dependency and version management practices covered more fully
in this module's later package-manager lesson.

---

## 3. What Is a Python Environment?

### Core vocabulary

- **Python interpreter** — the program that reads and executes Python source code (introduced
  conceptually in `05-debugger.md`, Section 5, as part of "running program"). There can be more than
  one Python interpreter installed on a single machine.
- **Environment** — the specific combination of a Python interpreter plus whatever packages are
  currently installed and accessible to it.
- **Installed packages** — the pre-written code (Section 1) currently available for a given
  interpreter to import and use.
- **Package location** — the specific place on disk where an environment's installed packages are
  actually stored, associated with one specific interpreter.
- **Executable paths** — the filesystem locations of the actual interpreter program (and related
  tools) that a shell resolves when you type a command like `python` (directly connecting to Module
  0.2/0.3's `PATH` concept, and `01-vscode-and-terminal.md`, Section 4).
- **Project environment** — the specific environment a given project is intended to be run and
  developed with.
- **Global/system Python** — the Python interpreter (and its packages) installed at the machine level,
  not tied to any one specific project (Section 6, Section 17 expand this fully).

### The relationship

```text
Python Environment
+-- Python interpreter
+-- installed packages
+-- executable tools
+-- environment-specific configuration
```

An "environment," in this general sense, is not one single file — it is the *combination* of a
specific interpreter, whatever is currently installed for it, and the tools/configuration tied to
that specific interpreter. A machine can have several such environments simultaneously coexisting: the
global/system one, and — as this lesson develops — one or more isolated, project-specific ones.

---

## 4. What Is a Virtual Environment?

### Definition

A **virtual environment** is a self-contained, isolated Python environment (Section 3), created
specifically to keep one project's interpreter and installed packages separate from the
global/system Python and from other projects' virtual environments.

### Key vocabulary

- **Isolation** — the property of one environment's packages not being visible to, or affecting, any
  other environment.
- **Environment boundary** — the conceptual line separating what belongs to one specific virtual
  environment from everything outside it (the global Python, or another project's virtual
  environment).
- **Project-specific environment** — a virtual environment created and used specifically for one
  project, holding only that project's own dependencies.

### What a virtual environment is NOT

This is an essential accuracy boundary for this lesson, expanded fully in Section 18 and Section 19:

- **Not a virtual machine** — it does not emulate or virtualize computer hardware or an entire
  operating system (Section 18).
- **Not a container** — it does not package an application together with OS-level isolation
  mechanisms (Section 19).
- **Not an operating system** — it is a Python-level construct, running entirely within the same
  operating system as everything else on the machine (Module 0.2).
- **Not a separate physical computer** — it shares the same CPU, memory, and filesystem as everything
  else running on the machine (Module 0.1, Module 0.2).
- **Not a complete OS-level isolation boundary** — processes, files, and system resources outside of
  Python packages are not isolated by a virtual environment (Section 29 expands this specifically for
  security).

### What it isolates and what it does not

| Isolated by a virtual environment | Not isolated by a virtual environment |
|---|---|
| Which Python interpreter version is used for this project (to the extent multiple are available) | The operating system itself |
| Which packages, and which versions, are installed and importable for this project | Filesystem access outside of Python's own package resolution |
| Executable tools installed alongside packages for this project (Section 3) | Network access |
| | Process/thread execution generally (Module 0.2; `05-debugger.md`, Section 22) |
| | Security/trust boundaries (Section 29) |

---

## 5. Why Virtual Environments Exist

Directly solving the problems introduced in Section 2:

- **Dependency isolation** — each project's installed packages are kept separate, so Project A's `X`
  version 1 and Project B's `X` version 2 (Section 2's scenario) can coexist without conflict.
- **Version isolation** — the specific version of a package used by one project has no effect on what
  version another project sees.
- **Project isolation** — a project's environment reflects only what that specific project actually
  needs, rather than everything ever installed on the machine.
- **Safer experimentation** — trying out a new package, or a different version of one, inside a
  project's own virtual environment cannot accidentally break an unrelated project or the global
  Python installation.
- **Reproducible development workflows** — a project's environment can be recreated (Section 16)
  from a clear record of what it needs, rather than depending on whatever happens to already be
  installed globally.
- **Avoiding global package pollution** — the global/system Python (Section 3) stays clean, rather
  than accumulating every package ever needed by every project a developer has worked on.
- **Easier onboarding** — a new contributor to a project can set up an environment specific to that
  project, without needing to first understand or replicate the state of someone else's global Python
  installation.
- **Reducing accidental dependency interference** — directly addressing Section 2's "accidental
  upgrades" and "accidental removals": changes made inside one project's virtual environment cannot
  spill over into another project's.

### A concrete example, resolved

Returning to Section 2's scenario: with virtual environments, Project A gets its own environment with
`X` version 1 installed, and Project B gets its own separate environment with `X` version 2 installed.
Both coexist on the same machine, each seeing only its own version of `X`, with neither project aware
of or affected by the other's environment.

---

## 6. Global Python vs Virtual Environment

| Aspect | Global/System Environment | Virtual Environment |
|---|---|---|
| Scope | Broader/shared across the whole machine | Project-specific |
| Dependency isolation | Low | High |
| Project conflicts | Possible (Section 2) | Greatly reduced |
| Experimentation | Riskier — can affect other projects/the system | Safer — changes are contained |
| Reproducibility | Harder — depends on whatever is already installed | Easier — environment can be recreated from a clear record (Section 28) |
| Environment management | Shared among everything using that Python installation | Isolated per project |

**Accuracy note:** exact behavior can vary by operating system and Python installation. This table
describes the general, conceptual distinction this lesson is built around — not a claim that every
platform or installation implements these details identically.

---

## 7. How Virtual Environments Work Internally

This is the conceptual core of the lesson.

### The general pipeline

```text
Project Directory
      |
Virtual Environment Directory
      |
Environment Metadata / Interpreter Setup
      |
Environment-Specific Package Installation
      |
Project Uses That Environment
```

### The pieces

- **Environment directory** — when a virtual environment is created (Section 8), a new directory is
  created on disk (commonly inside, or near, the project's own directory — Section 15) to hold
  everything that environment needs.
- **Python interpreter relationship** — a virtual environment does not necessarily duplicate an entire
  separate copy of the Python interpreter program; conceptually, it establishes a specific,
  identifiable interpreter (commonly linked to, or a copy of, the Python installation used to create
  it) that this environment's tools will use.
- **Executable paths** — the environment directory contains its own executable entries (for example, a
  `python` command specific to this environment) that, once selected (via activation, Section 10, or
  direct interpreter selection, Section 12), are what a shell or tool actually resolves and runs.
- **Package installation locations** — packages installed while this specific environment is active
  (or targeted directly) are stored inside this environment's own directory structure, separate from
  the global Python's package location (Section 3) and from any other project's environment.
- **Environment metadata** — the environment directory typically also holds some record of how it was
  created (for example, which Python version it is based on), used internally by the tooling that
  manages it.
- **How commands resolve differently** — once a specific environment's `python` (and related tools) is
  what a shell or tool actually invokes, running `python` (or installing a package) affects *that
  environment specifically* — reading and writing to its own package location, not the global one or
  another project's.

### Accuracy boundaries (deliberately explicit)

- This lesson does **not** claim that every Python installation creates a virtual environment in
  exactly the same physical way on disk.
- Implementation details — exact directory layout, whether the interpreter is copied or referenced,
  and related specifics — **can differ by platform and Python version**.
- The goal of this section is the conceptual pipeline above, sufficient to reason correctly about
  activation (Section 10), interpreter selection (Section 13), and troubleshooting (Section 26,
  Section 27) — not a low-level specification of any one platform's exact file layout.

---

## 8. `venv`

The roadmap identifies `venv` as primary Python tooling for this module, so it is taught directly
here as the concrete mechanism behind everything conceptual covered so far.

### What `venv` is

**`venv`** is a tool built into Python itself (meaning no separate installation is required beyond
having Python installed) whose specific purpose is to create virtual environments (Section 4).

### What problem it solves

`venv` provides the standard, built-in way to actually create the "Virtual Environment Directory" step
in Section 7's pipeline — turning the *concept* of a virtual environment into an actual, usable
directory and interpreter setup on disk.

### Relationship between Python and `venv`

`venv` is invoked *through* an existing Python interpreter — you use an already-installed Python
interpreter to create a new virtual environment. That new environment's own interpreter is then
conceptually tied to the interpreter that created it (Section 7).

### Creating a virtual environment

**Illustrative example** (conceptual — run from within a project's directory, in a terminal, per
`01-vscode-and-terminal.md`):

```bash
python -m venv .venv
```

This asks the `python` command to run its built-in `venv` module, creating a new virtual environment
in a directory named `.venv` (Section 9 explains this naming convention).

### Activation, deactivation, and checking the active interpreter

These are covered in full in Section 10, Section 11, and Section 25 respectively — introduced only
briefly here to complete the basic workflow shape:

- **Activation** — a shell command that changes how the *current terminal session* resolves `python`
  and related tools, pointing them at this specific virtual environment (Section 10).
- **Deactivation** — reverses that, for the current terminal session, without affecting the
  environment itself (Section 11).
- **Checking the active interpreter** — confirming, with evidence rather than assumption, which
  specific Python is currently being used (Section 25).

### Platform-specific activation, clearly labeled

**Activation commands differ by shell and operating system** — this lesson does not claim any single
command works universally (per the roadmap's cross-platform accuracy requirement). The following are
labeled, illustrative examples of the general *pattern* each platform commonly uses, not a claim that
these exact commands are correct for every installation:

- **Linux/macOS shells (illustrative, Bash-style):**
  ```bash
  source .venv/bin/activate
  ```
- **Windows Command Prompt (illustrative):**
  ```bat
  .venv\Scripts\activate.bat
  ```
- **Windows PowerShell (illustrative):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

**Accuracy note:** not every shell behaves identically, and PowerShell's execution policy or other
local configuration can affect whether an activation script is allowed to run at all (Section 26,
Failure 2). This lesson does not assume any one of these commands is the "correct" one universally —
which to use depends entirely on the specific shell actually in use, which the learner should already
be able to identify from `01-vscode-and-terminal.md`, Section 5.

### Using the environment for a project

Once activated (or once its interpreter is directly selected, Section 12), running `python`, or
installing a package, operates specifically within this environment — per Section 7's conceptual
pipeline.

---

## 9. Why `.venv` Is Common

### The convention

`.venv` is a very commonly used name for a project's virtual environment directory, but it is **a
convention, not a requirement.**

### Why this specific name is common

- It is short and immediately recognizable to developers familiar with the convention.
- The leading dot (`.`) follows a common convention (already touched on in Module 0.3) for marking a
  directory as auxiliary/tooling-related rather than part of the project's primary source content —
  many tools and interfaces treat dot-prefixed entries as less prominent by default.

### Why developers often keep the environment inside the project directory

Keeping `.venv` directly inside the project's own directory makes the relationship between "this
project" and "this project's environment" immediately visible and easy to locate — directly
supporting the working-directory reasoning already established in `01-vscode-and-terminal.md`, Section
6.

### Why the directory is usually treated as project-local, not shared

Because a virtual environment is specific to one project (Section 4, Section 5), placing it inside
that project's own directory (rather than somewhere shared) keeps that relationship clear and avoids
implying the environment is meant to be reused elsewhere.

### Naming is a convention, not a universal requirement

**`.venv` is not mandatory.** A virtual environment can technically be created with a different name
or in a different location — `venv`'s own command (Section 8) accepts any directory name the developer
chooses. `.venv` is simply the name this lesson (and much of the broader Python community) commonly
uses, because of the reasons above, not because any tooling strictly requires it.

---

## 10. Activation

### What activation means

**Activation** is running a specific script (Section 8) that changes the *current terminal/shell
session's* command resolution, so that typing `python` (and related tool names) resolves to this
specific virtual environment's interpreter and tools, instead of the global/system Python.

### Shell environment changes, conceptually

Activation works by adjusting the current shell session's environment — most notably, by changing
`PATH` (already introduced in Module 0.2 and `01-vscode-and-terminal.md`, Section 4) so that this
environment's executable directory (Section 7) is searched *before* the global Python's location. This
is exactly why, after activation, typing `python` can resolve to a completely different interpreter
than it did before — the shell is now finding the virtual environment's `python` first.

### The conceptual model

```text
Before activation:

shell
  |
system/global Python

After activation:

shell
  |
virtual environment Python
```

### The critical distinction: activation does not "start" or "create" the environment

**Activation is primarily a convenience mechanism for changing command resolution and environment
variables in the current shell — not a mechanism for bringing the environment into existence or
"turning it on."** The virtual environment (Section 4, Section 7) exists on disk as soon as it is
created (Section 8), entirely independent of whether any shell session is currently activated into it.
Activation only changes *how the current terminal session's commands resolve* — it does not create,
start, launch, or otherwise bring the environment "to life." This distinction matters directly for
Section 12: because the environment's existence does not depend on activation, tools can use it
without ever activating a shell into it at all.

---

## 11. Deactivation

### What `deactivate` does

Running `deactivate` (a command made available specifically by having activated an environment,
Section 10) reverses activation's shell-level changes for the **current terminal session** — restoring
`python` and related commands to whatever they resolved to before activation.

### Why it affects the current shell

Exactly as with activation, `deactivate` only changes the current terminal session's own command
resolution and environment state (Section 10). It does not affect any other open terminal session, and
it does not affect the environment itself.

### What happens conceptually to command resolution

After deactivation, typing `python` in that terminal session again resolves the way it did before
activation — typically back to the global/system Python (Section 3), unless something else was
already configured differently.

### Why deactivation does not delete the virtual environment

Deactivation is purely a **shell-session-level** change (Section 10, Section 11) — it has no effect on
the virtual environment's directory or its installed packages on disk (Section 7). The environment
continues to exist, entirely unchanged, ready to be activated again later (Section 16's lifecycle).

### The distinction, made explicit

```text
deactivate
!=
delete environment
```

Deactivating only affects how the *current shell session* resolves commands going forward. Deleting an
environment (Section 15, Section 16) means removing its directory from disk entirely — a completely
different, separate action.

---

## 12. Activation vs Using the Interpreter Directly

### Activation is convenience, not necessity

Section 10 already established that a virtual environment exists independently of shell activation.
This section makes the practical consequence of that explicit: **a virtual environment can be used
without relying entirely on shell activation.**

### Invoking the environment's interpreter directly

Because the environment's interpreter (Section 7) is simply a specific, identifiable program sitting
at a specific location on disk, a tool (or a developer) can invoke that specific interpreter directly
by its full path or through direct interpreter selection, without ever running the activation script
at all.

### What this reveals about environment identity

- **Activation is convenience** — it changes what a *shell* resolves `python` to, purely for the
  convenience of typing shorter commands.
- **Environment identity comes from which interpreter is actually being used** — not from whether
  activation happened. Two ways of running "the same environment's Python" — through an activated
  shell, or by directly pointing at that environment's specific interpreter — are, in terms of which
  packages and interpreter are actually used, equivalent.
- **Scripts, IDEs, and tooling can explicitly select an interpreter** — this is directly why an IDE
  can be configured to use a specific project's virtual environment (Section 13) without the developer
  ever needing to manually activate that environment in the IDE's own integrated terminal first —
  though, per Section 13, the terminal and the IDE each still resolve `python` independently unless
  both are explicitly aligned.

**Scope note:** this lesson does not turn this into an advanced automation topic — the point here is
only the conceptual distinction between "the environment" and "a shell activated into it," which is
essential for correctly understanding interpreter selection (Section 13) and several common failure
modes (Section 26).

---

## 13. Python Interpreter Selection

### The core vocabulary, reconnected

- **System Python** — the global/system Python interpreter (Section 3, Section 6).
- **Virtual environment Python** — a specific project's isolated interpreter (Section 4, Section 7).
- **Selecting the correct interpreter** — ensuring that whatever tool or shell you are using is
  actually pointed at the interpreter you intend, per Section 12's "environment identity comes from
  which interpreter is actually used."

### Why an IDE may appear to use the "wrong Python"

An IDE (`02-ide-concepts.md`) typically has its own, separate notion of "which interpreter to use for
this project" (directly echoing `01-vscode-and-terminal.md`, Section 9's brief introduction to
interpreter selection). This IDE-level selection is independent of whatever a terminal session
currently resolves `python` to (Section 10, Section 12) — they are two *separate* mechanisms that can,
if not both deliberately aligned, disagree.

### Why terminal and IDE can disagree

```text
Terminal -> Python A

IDE -> Python B

Result:
"Why does it work in terminal but not in the IDE?"
```

If a developer activates a project's virtual environment in the terminal (Section 10) but the IDE is
separately configured (or defaults) to use a different interpreter — the global Python, or a different
project's environment entirely — then code that behaves correctly when run from the terminal can
behave differently, or fail to find an installed package, when run through the IDE, and vice versa.

### Why this is one of the most common beginner environment problems

This mismatch is subtle precisely because both the terminal and the IDE *appear* to be working with
"the project" — the confusion comes from not realizing that interpreter selection is tracked
separately in each context (Section 12). Section 26 (Failure 1 and Failure 4) and Section 27's
troubleshooting workflow both address this directly, with Section 36's structured exercise built
specifically around this exact scenario.

**Scope note:** this lesson does not turn this into a full VS Code course — the underlying interpreter-
selection mismatch is the durable concept; the specific IDE menu or setting used to fix it belongs to
tool-specific documentation, not this lesson.

---

## 14. Virtual Environment and Environment Variables

This connects directly to Module 0.2 and Module 0.3, without re-teaching either.

### The relevant concepts, reconnected

- **Environment variables** — named values available to a running process, inherited from whatever
  started it (Module 0.2; `01-vscode-and-terminal.md`, Section 4).
- **`PATH`** — the specific environment variable a shell consults to find which program a typed
  command name actually refers to (Module 0.2, Module 0.3; `01-vscode-and-terminal.md`, Section 4) —
  directly the mechanism activation modifies (Section 10).
- **Activation scripts** — the specific scripts (Section 8, Section 10) that make these environment-
  variable changes when run.
- **Shell environment** — the current, in-memory set of environment variables (including `PATH`) held
  by one specific running shell session (Module 0.2).
- **Inheritance, at a high level** — a new process (for example, one started from within an activated
  shell) inherits that shell's current environment variables, including its modified `PATH` (Module
  0.2) — this is exactly why a program launched from an activated terminal correctly uses that
  environment's Python without any further configuration.

### Why this matters here specifically

Section 10's explanation of activation ("changes the current shell session's `PATH`") only makes
sense with this Module 0.2/0.3 background already in place. This lesson does not re-teach environment
variables from scratch — it applies that existing understanding directly to explain precisely
*how* activation achieves its effect.

---

## 15. Virtual Environment and File System

This connects to the filesystem concepts from Module 0.2 and Module 0.3.

### Where the environment directory lives

As introduced in Section 7 and Section 9, a virtual environment is, physically, a directory on disk —
commonly located inside (or near) the project's own directory, most often named `.venv` by convention.

### Why it contains environment-specific files

This directory holds everything Section 7 described: the interpreter setup, executable entries, and
the location where this specific environment's packages are actually installed — all specific to this
one environment, not shared with anything else on the machine.

### Why developers normally do not manually edit internal environment files

The contents of a virtual environment's directory are generated and managed by the tooling that
creates and maintains it (Section 8) — manually editing these internal files directly risks putting the
environment into an inconsistent state that the tooling does not expect, for no real benefit, since the
same result can always be achieved properly through the tooling itself (creating, activating, and
installing packages the intended way).

### Why environments can be deleted and recreated

Because a virtual environment's directory holds *derived*, reproducible content — an interpreter setup
and installed packages, both of which can be regenerated from a clear starting point (the Python
installation used to create it, and a record of which packages to install) — it is generally safe to
delete and recreate an entire virtual environment when needed (Section 16, Section 26).

### The core idea

```text
Environment = disposable project infrastructure
```

**Clarification:** this applies to the environment directory itself — *not* to the project's actual
source code. A project's source files represent the developer's own original work and are not
regenerable the way an environment's installed packages are; they should never be treated as
disposable in the way the environment directory can be.

---

## 16. Virtual Environment Lifecycle

```text
Create
  |
Activate / Select
  |
Install Dependencies
  |
Develop
  |
Run
  |
Deactivate
  |
Recreate / Remove When Necessary
```

- **Create** — using `venv` (Section 8) to generate a new environment directory.
- **Activate / Select** — either activating a shell session into it (Section 10) or directly selecting
  its interpreter in a tool (Section 12, Section 13).
- **Install Dependencies** — adding the specific packages this project needs into this environment
  (briefly touched on in Section 21 — full depth belongs to `07-package-managers.md`).
- **Develop** — writing and editing the project's code, using this environment's interpreter for any
  editor-integrated features (Section 13).
- **Run** — actually executing the project's code using this environment's Python.
- **Deactivate** — returning the current shell session to its prior command resolution (Section 11),
  when the environment is no longer needed for that session.
- **Recreate / Remove When Necessary** — deleting and regenerating the environment directory (Section
  15), in situations described below.

### When an environment might need to be recreated

- **Corrupted environment** — the environment's internal state has become inconsistent or broken.
- **Wrong interpreter** — the environment was created using an unintended Python version.
- **Stale dependencies** — installed packages no longer reflect what the project actually needs.
- **Incompatible dependency state** — conflicting or broken combinations of installed packages have
  accumulated.
- **Switching project setup** — the project's requirements have changed enough that starting from a
  clean environment is clearer than trying to reconcile the old one.

**Important qualification:** recreation should **not** be the first, reflexive response to every
problem. Section 20 and Section 27's systematic troubleshooting workflow exist precisely because many
environment problems have a specific, identifiable root cause (a wrong interpreter selected, a
misunderstood activation state) that recreating the environment would not actually address — and would
cost time without fixing anything.

---

## 17. Virtual Environment vs System Python

### Why installing project-specific packages directly into system/global Python is generally undesirable

- **Permissions** — depending on the operating system and installation, modifying the system Python's
  packages may require elevated privileges (Module 0.3's permissions concepts), which is both an extra
  hurdle and an unnecessary risk for routine project work.
- **Conflicts** — directly Section 2's core problem, applied at the system level: installing a
  project-specific package version globally can conflict with what other software on the machine
  expects.
- **Unintended upgrades** — upgrading a package globally for one project's benefit can silently change
  behavior for everything else on the machine relying on that global installation.
- **Dependency contamination** — the system Python's package set becomes an unpredictable mixture of
  whatever every project ever needed, rather than a clean, minimal system installation.
- **Multiple project requirements** — a machine used for more than one project (the normal case) simply
  cannot satisfy every project's needs through one single shared global environment (Section 2).

### System Python may still be needed by the operating system or other software

Some operating systems and installed tools rely on a specific system Python installation to function
correctly. Modifying that installation's packages — adding, upgrading, or removing them for a specific
project's convenience — risks breaking something entirely unrelated to your own project work.

### The guidance

**Do not encourage modifying system Python unnecessarily.** Project-specific dependency work belongs
in a dedicated virtual environment (Section 4), leaving the system Python installation untouched and
stable for whatever else on the machine may depend on it.

---

## 18. Virtual Environment vs Virtual Machine

### Virtual Environment

Provides Python-level, project-specific dependency isolation (Section 4) — an interpreter and a set of
installed packages, kept separate from other such sets, all running within the *same* operating system.

### Virtual Machine (introduced only for this comparison — not taught here)

A **virtual machine** provides a virtualized *operating-system-level* environment — effectively an
entire simulated computer, including its own operating system, running on top of (or alongside) the
host machine's own operating system.

### Comparison

| | Virtual Environment | Virtual Machine |
|---|---|---|
| **Scope** | Python interpreter + packages | An entire simulated computer, including its own OS |
| **Isolation level** | Python package/interpreter level only (Section 4's "what it isolates") | Full operating-system-level isolation |
| **Resource overhead** | Low — mostly just files on disk plus package installations | Substantially higher — running an entire separate operating system consumes real memory, CPU, and disk resources |
| **Use cases** | Isolating one Python project's dependencies from another | Running an entirely different operating system, or fully isolating a workload at the OS level |
| **Portability** | Tied to the host machine's own OS and installed Python; not something you move as a self-contained unit in the way a VM image can be | A VM image can commonly be moved and run on a different physical host that supports the same virtualization technology |

**Scope note:** this lesson does not go deeply into virtualization technology — the comparison above
exists only to make the boundary from Section 4 ("not a virtual machine") precise and concrete, not to
teach how virtual machines themselves work.

---

## 19. Virtual Environment vs Container

This distinction matters because containers appear later in this roadmap.

### Virtual Environment

Python dependency/interpreter isolation (Section 4) — operating entirely within the host machine's
existing operating system.

### Container (introduced only for this comparison — a later-stage topic, not taught here)

A **container** packages an application together with (some of) its dependencies and environment,
using operating-system-level isolation mechanisms — broader in scope than just Python packages, and
involving a different underlying mechanism than a virtual environment's Python-only isolation.

### The relationship

A container **can** contain a Python virtual environment inside it — the two are not mutually
exclusive — but they are **not the same concept**, and one does not replace the need to understand the
other. A virtual environment, by itself, isolates Python dependencies; it does nothing about the
broader OS-level packaging and isolation a container provides.

**Scope note, strictly enforced:** this lesson does **not** teach Docker or container implementation.
Containers are a dedicated, later-stage topic in this roadmap. This section exists only to correctly
place virtual environments relative to a concept the learner will encounter later, so that when
containers are eventually taught, this lesson's Python-level isolation is not confused with that
broader, OS-level mechanism.

---

## 20. Virtual Environment vs Conda

Mentioned here only at a conceptual comparison level.

### `venv`

The tool this lesson teaches (Section 8) — Python's own, built-in mechanism for creating virtual
environments, specifically managing Python interpreters and packages.

### Conda environments (introduced only for this comparison — not taught here)

**Conda** is a different ecosystem's environment and package management tool, capable of managing not
only Python packages but also other, non-Python dependencies and even different versions of Python
itself, using its own separate mechanisms distinct from `venv`.

### Why the roadmap uses `venv` as the foundational Python environment mechanism

`venv` is built directly into Python, requires no separate installation, and directly demonstrates the
core concepts this lesson teaches — environment isolation, activation, interpreter selection — using
Python's own standard tooling, which is why this roadmap establishes it as the foundational mechanism
before (if ever) encountering alternative ecosystems.

**Scope note:** this is not a Conda tutorial, and this lesson does not introduce further alternatives
beyond this brief, clarifying comparison — the goal is only to prevent the misconception (Section 34)
that `venv` is the only tool of its kind that exists, while keeping this lesson's actual teaching focus
strictly on `venv` and the concepts it demonstrates.

---

## 21. Relationship With Package Managers

### The distinction

A **virtual environment** provides isolation (Section 4) — a separate space where packages *can* be
installed, separate from other such spaces.

A **package manager** handles the actual work of installing, upgrading, and removing packages *within*
a given environment.

```text
Virtual Environment
        +
Package Manager
        v
Project Development Environment
```

These solve two different, complementary problems: the environment provides the isolated *place*;
the package manager performs the actual *installation work* inside that place.

### `pip` and `uv`, mentioned only to establish this relationship

- **`pip`** — Python's standard package manager, commonly used to install packages into a currently
  selected (activated, or directly targeted) virtual environment.
- **`uv`** — another package-management tool named in this module's roadmap tooling list, which can
  also install packages into a virtual environment (and, depending on how it is used, help manage
  environments themselves).

**Scope note, strictly enforced:** this lesson does **not** teach the full `pip`/`uv` workflow. Their
detailed treatment belongs to `07-package-managers.md`. Here, they are mentioned only to make clear
that "creating an isolated environment" (this lesson's subject) and "installing packages into it"
(the package-manager lesson's subject) are related but distinct steps in a project's setup.

---

## 22. Relationship With `pyproject.toml`

### The distinction

Project metadata and dependency *declarations* — what a project says it needs — can be represented
separately from the actual environment where those dependencies are physically installed.

```text
Project Metadata / Dependencies
            |
       pyproject.toml

Project Environment
            |
          .venv
```

`pyproject.toml` (introduced here only at the level of this distinction) is a file that can record
*what a project declares it depends on*; `.venv` (Section 9) is the actual, physical environment where
those dependencies are installed and used. One is a **declaration**; the other is an **installed,
isolated runtime space**.

**Scope note, strictly enforced:** this lesson does **not** teach `pyproject.toml` in depth. Its full
treatment belongs to this module's later project-structure lesson. The distinction established here —
declared dependencies vs. the actual environment — is sufficient background for this lesson's purposes,
and is directly relevant to Section 28's reproducibility discussion.

---

## 23. Dependency Isolation Example

### The scenario

```text
Project A
Python environment A
package version X

Project B
Python environment B
package version Y
```

### Why both projects can coexist without conflict

Because each project has its **own** virtual environment (Section 4), each environment's installed
packages are entirely separate (Section 7). Project A's environment contains version `X` of some
package; Project B's environment contains a different version, `Y`, of the same package. Neither
environment is aware of, or affected by, the other's installed packages — there is no shared global
state (Section 2) for these two versions to conflict over.

This example does not require any external package to demonstrate — the same reasoning applies exactly
to the disposable, dependency-free exercises used later in this lesson (Section 24, Section 35): two
separate `.venv` directories, for two separate disposable project folders, are already, by construction,
fully isolated from one another, regardless of what (if anything) is installed inside each.

---

## 24. Safe Hands-On `venv` Workflow

All steps below use disposable, local practice directories — not any real project — and require no
`sudo`, no system-wide destructive commands, no real credentials, and no production data or
directories.

### The workflow

1. **Create a project directory.**
   ```bash
   mkdir venv-practice
   cd venv-practice
   ```
2. **Create `.venv`.**
   ```bash
   python -m venv .venv
   ```
3. **Activate it** — using the labeled, platform-appropriate command from Section 8 (for example, the
   Linux/macOS illustrative form: `source .venv/bin/activate`).
4. **Verify interpreter/environment** — using the verification techniques from Section 25, before
   assuming activation succeeded.
5. **Use Python** — for example, opening the Python interpreter interactively or running a small
   script, confirming it behaves as expected within this environment.
6. **Deactivate** (Section 11):
   ```bash
   deactivate
   ```
7. **Reactivate** — repeating step 3, confirming the same environment can be re-entered at any later
   time.
8. **Remove/recreate the environment when appropriate** (Section 16) — for example:
   ```bash
   rm -rf .venv
   python -m venv .venv
   ```

**Illustrative labeling:** every command above shows the *action* to take; none of the expected results
are shown as genuine captured output — where this lesson describes what should happen (for example,
"the shell prompt commonly changes to indicate the active environment"), that description is explicitly
conceptual/illustrative, not a claim of actual observed output.

**Cleanup:** once finished practicing, the entire `venv-practice` directory (including its `.venv`) can
be safely deleted, since it was created purely for this exercise.

---

## 25. Verifying Which Python Is Being Used

### Why verification matters

Given Section 13's explanation of how terminal and IDE interpreter selection can silently disagree,
**assuming** which Python is currently active is unreliable — the same discipline already established
in `05-debugger.md` (treat runtime evidence as more reliable than assumption) applies directly here.

### Concepts to check

- **Checking the Python version** — confirming which version of Python the currently resolved
  interpreter actually is.
- **Checking which executable is being used** — confirming the actual filesystem location (Section 7)
  the `python` command currently resolves to, not merely assuming it is the intended environment's.
- **Comparing system vs. virtual environment interpreter** — explicitly comparing the location found
  above against both the global Python's known location and the specific virtual environment's known
  location, to determine which one is actually active.

### Platform-appropriate examples (illustrative — commands differ by OS/shell)

- **Linux/macOS shells (illustrative):**
  ```bash
  which python
  python --version
  ```
- **Windows PowerShell (illustrative):**
  ```powershell
  Get-Command python
  python --version
  ```
- **Windows Command Prompt (illustrative):**
  ```bat
  where python
  python --version
  ```

**Accuracy note:** exact commands for locating executables differ between operating systems and shells
(directly per the roadmap's cross-platform accuracy requirement) — the commands above are labeled
examples of the general pattern, not a universal, single correct command. No output from these
commands is fabricated anywhere in this lesson; where a result is discussed, it is described only
conceptually (for example, "the path shown should be inside the project's `.venv` directory if that
environment is correctly active").

---

## 26. Common Failure Modes

Each follows: symptom, likely cause, evidence to inspect, corrective action, prevention.

### Failure 1 — Wrong Python interpreter

1. **Symptom:** the project behaves differently from expected — for example, an installed package
   appears unavailable, or a different package version's behavior shows up.
2. **Likely cause:** the IDE or terminal is using a different interpreter than the one intended for
   this project (Section 13).
3. **Evidence to inspect:** the actual resolved interpreter's path/version in both the terminal
   (Section 25) and the IDE's own interpreter selection (Section 13).
4. **Corrective action:** explicitly select or activate the intended environment in whichever context
   is using the wrong one.
5. **Prevention:** verify the active interpreter (Section 25) at the start of a work session, rather
   than assuming it is correct.

### Failure 2 — Activation appears not to work

1. **Symptom:** running an activation command produces no apparent change, or an error.
2. **Likely cause:** wrong shell for the activation command used (Section 8's platform-specific
   labeling); wrong activation command for the current shell; execution-policy or similar restrictions
   (for example, on some PowerShell configurations) preventing a script from running; running the
   command from the wrong directory (so the referenced path does not exist); the environment does not
   actually exist yet (Section 8's creation step was skipped or failed).
3. **Evidence to inspect:** which shell is actually running (`01-vscode-and-terminal.md`, Section 5);
   the current working directory (`01-vscode-and-terminal.md`, Section 6); whether the `.venv`
   directory actually exists at the expected location.
4. **Corrective action:** use the activation command matching the actual shell in use; run it from the
   correct directory; address any shell-specific restriction preventing script execution; recreate the
   environment if it does not actually exist.
5. **Prevention:** confirm which shell is in use, and the current working directory, before attempting
   activation.

### Failure 3 — Package installed but Python cannot import it

1. **Symptom:** a package was apparently installed, but attempting to use it in code fails as if it
   were never installed at all.
2. **Likely cause:** the package was installed into a *different* environment (for example, the global
   Python, Section 17) than the one actually being used to run the code; the wrong interpreter is
   active (Section 13); a different terminal session than the one where installation happened is now
   being used.
3. **Evidence to inspect:** which interpreter was active at the time of installation, versus which
   interpreter is active now when attempting to use the package (Section 25).
4. **Corrective action:** install the package into the actual environment currently being used, or
   switch to the environment the package was actually installed into.
5. **Prevention:** verify the active environment (Section 25) both before installing a package and
   before relying on it.

### Failure 4 — IDE and terminal disagree

1. **Symptom:** code behaves correctly in one context (terminal or IDE) but not the other.
2. **Likely cause:** exactly Section 13's core scenario — separate, independently configured
   interpreter selections in each context.
3. **Evidence to inspect:** the specific interpreter path/version each context is actually using
   (Section 25 for the terminal; the IDE's own interpreter-selection display for the IDE).
4. **Corrective action:** explicitly align both contexts to the same, intended environment.
5. **Prevention:** treat interpreter selection as something to be explicitly set and verified in both
   contexts, not assumed to automatically match.

### Failure 5 — `.venv` deleted accidentally

1. **Symptom:** activation (Section 10) or interpreter selection (Section 13) fails because the
   expected environment directory no longer exists.
2. **Likely cause:** the `.venv` directory was deleted, intentionally or accidentally.
3. **Evidence to inspect:** whether the `.venv` directory is actually present at the expected location.
4. **Corrective action:** recreate the environment (Section 8, Section 16) and reinstall the needed
   packages.
5. **Prevention:** per Section 15's "disposable project infrastructure" principle — this is normally
   recoverable, precisely because the environment is not itself irreplaceable project work; the
   project's *source code* is what must never be treated this way.

### Failure 6 — Environment becomes inconsistent

1. **Symptom:** package behavior becomes unpredictable, or installation/usage produces errors that do
   not make sense given what is believed to be installed.
2. **Likely cause:** an accumulation of conflicting or partially completed package changes over time
   (Section 16's "incompatible dependency state").
3. **Evidence to inspect:** a review of what is actually currently installed in the environment,
   compared against what the project is believed to need.
4. **Corrective action:** where the inconsistency cannot be clearly traced to one specific, fixable
   cause, recreating the environment from a clean state (Section 16) is a reasonable response here —
   distinct from Failure 1–4, where the root cause is a specific, identifiable selection mismatch that
   recreation would not actually fix.
5. **Prevention:** avoid ad hoc, undocumented package changes accumulating over a long period without
   review.

### Failure 7 — Global package accidentally used

1. **Symptom:** code appears to work even though the developer does not recall installing the package
   it relies on into the project's own environment.
2. **Likely cause:** the global Python (Section 3, Section 17) happens to already have that package
   installed, and the code is actually running against the global Python rather than the intended
   virtual environment (Failure 1's root cause, manifesting here specifically as an unnoticed "false
   success").
3. **Evidence to inspect:** the active interpreter (Section 25) at the moment the code ran, compared
   against the intended project environment.
4. **Corrective action:** confirm and switch to the intended environment, and explicitly install the
   package there rather than relying on whatever happens to already exist globally.
5. **Prevention:** verify the active environment (Section 25) rather than judging correctness purely by
   "the code ran without an error."

---

## 27. Systematic Troubleshooting Workflow

```text
Problem
  |
Identify Project
  |
Identify Expected Python Environment
  |
Check Current Interpreter
  |
Check Environment Activation/Selection
  |
Check Environment Location
  |
Check Package Installation Target
  |
Compare Expected vs Actual
  |
Fix the Root Cause
  |
Verify
```

- **Identify Project** — confirm exactly which project's environment is relevant to the current
  problem.
- **Identify Expected Python Environment** — state, explicitly, which environment *should* be in use
  for this project (Section 4, Section 9).
- **Check Current Interpreter** — using Section 25's verification techniques, determine which
  interpreter is *actually* currently resolved, in whichever context (terminal, IDE) the problem is
  occurring in.
- **Check Environment Activation/Selection** — confirm whether the intended environment is actually
  activated (Section 10) or explicitly selected (Section 12, Section 13) in that context.
- **Check Environment Location** — confirm the expected `.venv` (or equivalent, Section 9) directory
  actually exists at the expected path (directly relevant to Failure 2 and Failure 5, Section 26).
- **Check Package Installation Target** — confirm which environment a relevant package was actually
  installed into (directly relevant to Failure 3, Section 26).
- **Compare Expected vs Actual** — explicitly compare what *should* be true (from the "Identify
  Expected" step) against what the evidence gathered above actually shows.
- **Fix the Root Cause** — correct whichever specific mismatch the comparison revealed.
- **Verify** — re-check (Section 25) that the fix actually produces the expected, correct interpreter
  and environment state.

### Emphasize evidence over guessing

This workflow directly applies the same evidence-based discipline already taught in `05-debugger.md`
(Section 2's reasoning loop, and Section 19's systematic troubleshooting workflow from
`04-formatters-and-linters.md`) to the specific, recurring problem of environment/interpreter mismatch.
**This lesson does not turn this into a general debugging lesson** — the workflow above is scoped
specifically to virtual-environment and interpreter problems, building directly on debugging
methodology already taught rather than re-deriving it from scratch.

---

## 28. Reproducibility

### The relevant concepts, reconnected

- **Environment isolation** — Section 4/Section 5: keeping one project's dependencies separate from
  others.
- **Reproducibility** — the ability to recreate a working environment reliably, whether on the same
  machine later or on a different machine entirely.
- **Dependency versions** — exactly which version of each package a project actually needs (Section 2).
- **Environment recreation** — regenerating an environment from a clean state (Section 16).
- **Environment declarations** — a recorded statement of what a project needs (briefly connected in
  Section 22's `pyproject.toml` mention).

### The essential clarification

**A virtual environment improves isolation but does not automatically guarantee complete
reproducibility.** An environment, by itself (Section 4, Section 7), is just an isolated *place* where
packages happen to be installed — it does not, on its own, keep a record of exactly which packages and
versions were installed, in a form that could reliably reproduce the same environment elsewhere or
later.

### Why dependency/version management is also required

Achieving genuine reproducibility requires, *in addition to* environment isolation, a clear,
maintained record of exactly which packages and versions a project depends on (Section 22's
declaration concept) — so that a new environment, created fresh, can be populated with precisely the
same dependencies as before. This record-keeping and precise version management is the subject of this
module's later package-manager lesson, not this one.

**Scope note:** this lesson does not teach lockfiles (a specific, more precise form of this
dependency-version record) in depth — they are mentioned here only to indicate that this deeper
reproducibility mechanism exists and belongs to later material.

---

## 29. Security Considerations

### Risks to be aware of

- **Untrusted packages** — a package installed into a virtual environment is still code that runs with
  whatever access the process running it has; installing an unfamiliar package carries real risk,
  regardless of which environment it is installed into.
- **Dependency installation risks** — installing a package can itself execute code as part of the
  installation process, not only when later imported and used.
- **Executing untrusted code** — running any code (a package, or a script) you have not reviewed
  carries risk proportional to what that code is actually capable of doing on the machine.
- **Environment isolation is not a security sandbox** — directly restated from Section 4's "what it
  does not isolate": a virtual environment does not restrict what a package's code is capable of
  doing on the machine (accessing files, the network, and so on) — it only keeps *which packages are
  installed* separate between projects.
- **Secrets should not be stored casually inside environments** — an environment's directory (Section
  15) is project-local infrastructure, not a secure storage mechanism; sensitive values do not belong
  there.
- **Do not commit credentials into project directories** — a broader, general engineering practice,
  directly relevant here because a project's directory (where `.venv` commonly lives, Section 9) is
  often also the directory tracked by version control; credentials placed anywhere in that directory
  risk being inadvertently shared.

### The core principle

**A virtual environment is primarily a dependency isolation mechanism, not a security boundary.** It
does not prevent a compromised or malicious package from affecting the machine it runs on — a package
installed inside a virtual environment still executes with the same access to the filesystem, network,
and other resources (Module 0.2) that any other code run by that same user account would have. This
lesson does not imply otherwise anywhere in its examples or exercises.

### For this lesson's exercises specifically

**Never use real credentials, API keys, production secrets, or personal data anywhere in this lesson's
exercises (Section 24, Section 35–37).** Every exercise uses only small, disposable, local example
projects.

---

## 30. Performance and Storage Considerations

- **Environments consume disk space** — each virtual environment's directory (Section 7, Section 15)
  holds its own copy of installed packages, taking up real storage on disk.
- **Multiple projects may have separate environments** — since isolation (Section 4, Section 5)
  specifically means *not* sharing installed packages between projects, working on several projects
  means maintaining several separate environments, each with its own storage cost.
- **Environment creation has a cost** — creating a new environment (Section 8) and installing its
  packages takes some real time, not an instantaneous action.
- **Environments make development safer but are not free** — the isolation benefits described
  throughout this lesson (Section 5) come at the real, measurable cost of additional disk space and
  setup time compared to one single shared global environment.
- **Unnecessary environments can create clutter** — accumulating many old, unused virtual environments
  (for abandoned experiments, or projects no longer worked on) consumes disk space without providing
  any ongoing benefit; removing environments that are no longer needed (Section 15's "disposable
  infrastructure" principle) is a reasonable, low-risk cleanup practice.

**Accuracy note:** this lesson does not fabricate or claim any specific benchmark numbers for disk
space or creation time — the exact costs depend on the specific packages involved, the platform, and
the Python installation in use.

---

## 31. Real-World Use Cases

All examples below remain conceptual — none of the referenced technologies are taught here.

### Web application

A web application project depends on a specific set of framework and library versions; its own virtual
environment keeps these separate from any other project's needs on the same machine.

### Data science project

A data science project depends on specific numerical/data-handling libraries, often at specific
versions tied to how the project's analysis code was written; its own environment prevents these from
conflicting with a different project's data libraries.

### Machine learning project

An ML project may depend on a specific version of a machine learning framework, chosen deliberately for
compatibility with the project's own code and models; its own environment keeps this separate from a
different project that might need a different framework version.

### LLM application

An LLM application project depends on a specific combination of SDK and supporting library versions;
its own environment prevents these from conflicting with an unrelated project's dependencies.

### RAG application

A retrieval-augmented-generation project may depend on specific retrieval, vector-storage, or
database-client library versions; its own environment isolates these from other, unrelated projects.

### Agent system

An agent-system project may depend on specific orchestration and tooling library versions; its own
environment keeps these separate from any other project's dependency needs.

Every one of these examples applies the exact same underlying mechanism this entire lesson has
taught — none of them requires any new environment concept beyond what has already been covered.

---

## 32. Applied AI Engineering Connection

This is a forward-looking preview only — none of the referenced technologies are taught here.

### Why virtual environments become especially important in AI engineering

- **Rapidly changing AI libraries** — AI/ML libraries frequently release new versions, sometimes with
  breaking changes, making version isolation (Section 5) especially valuable for keeping a working
  project stable while other projects adopt newer versions independently.
- **Model-serving dependencies** — code that serves a trained model for use commonly has its own
  specific dependency set, separate from the code used to train that model.
- **GPU/CPU-related Python packages** — some AI-related packages are tied to specific hardware-support
  versions; keeping these isolated per project avoids one project's hardware-specific requirements
  conflicting with another's.
- **ML frameworks** — as in Section 31, different projects can require different framework versions.
- **Data-processing libraries** — different projects' data pipelines may depend on different versions
  of the same processing libraries.
- **LLM SDKs** — as in Section 31.
- **Retrieval libraries** — as in Section 31's RAG example.
- **Agent frameworks** — as in Section 31's agent example.
- **Evaluation tooling** — tooling used to assess a system's outputs may itself have its own dependency
  needs, separate from the system being evaluated.

### The engineering problem, stated directly

```text
AI Project A
Dependency Set A

AI Project B
Dependency Set B

AI Project C
Dependency Set C

        v

Isolation prevents project environments
from unnecessarily interfering with each other.
```

**Virtual environments are foundational infrastructure for Python-based AI development.** Every AI
project the learner builds throughout the rest of this roadmap will depend on this same underlying
mechanism — a dedicated, isolated environment, created the same way, activated or selected the same
way, and troubleshot using the same evidence-based workflow (Section 27) taught in this lesson.

---

## 33. Production Engineering Connection

This is a conceptual connection only — none of the referenced later-stage topics are taught here.

```text
Local Virtual Environment
        v
Managed Dependencies
        v
Reproducible Environment
        v
Container / Deployment Environment
        v
Production Runtime
```

- **Local Virtual Environment** — this lesson's subject: an isolated Python environment on a
  developer's own machine.
- **Managed Dependencies** — a maintained, explicit record of exactly what a project needs (Section
  22, Section 28), going beyond what a virtual environment alone provides.
- **Reproducible Environment** — the combination of isolation (this lesson) and dependency management
  (a later lesson) that allows the same environment to be reliably recreated elsewhere.
- **Container / Deployment Environment** — a later-stage packaging and OS-level isolation mechanism
  (Section 19), which can itself contain a Python virtual environment as one of its internal pieces.
- **Production Runtime** — the actual environment in which a finished system runs and serves real use.

**Explanation of the progression:** these are related but genuinely distinct layers, each building on
the one before it, rather than one simply being a bigger version of the last. A production deployment
does not merely "use a bigger virtual environment" — it typically involves entirely separate mechanisms
(container/deployment tooling) built on top of the same underlying principle of dependency isolation
this lesson establishes. This lesson does not teach those later layers in depth; it establishes only
the foundational layer they are built on top of.

---

## 34. Common Misconceptions

1. **"A virtual environment is a virtual machine."**
   Incorrect — directly Section 4/Section 18: a virtual environment isolates Python interpreters and
   packages; a virtual machine virtualizes an entire operating system.

2. **"Activation creates the environment."**
   Incorrect — directly Section 10: the environment is created by `venv` (Section 8) and exists on
   disk independently of whether any shell has activated it.

3. **"Deactivation deletes the environment."**
   Incorrect — directly Section 11: deactivation only affects the current shell session's command
   resolution; the environment's directory and installed packages remain unchanged on disk.

4. **"A virtual environment is a security sandbox."**
   Incorrect — directly Section 29: it isolates which packages are installed, not what those packages
   are capable of doing once running.

5. **"Every project must use `.venv`."**
   Incorrect — directly Section 9: `.venv` is a common convention for the directory's name and
   location, not a technical requirement.

6. **"Virtual environments automatically guarantee reproducibility."**
   Incorrect — directly Section 28: isolation alone does not guarantee reproducibility without
   accompanying dependency/version management.

7. **"The environment directory should always be manually edited."**
   Incorrect — directly Section 15: internal environment files are managed by the tooling that creates
   them; manual edits risk an inconsistent state for no real benefit.

8. **"Installing a package globally is equivalent to installing it into the project environment."**
   Incorrect — directly Section 3/Section 17/Section 26 (Failure 3, Failure 7): a global installation
   and a project-specific virtual environment installation are separate, independent package
   locations.

9. **"If a package exists on my machine, every project can automatically use it."**
   Incorrect, for the same reason as above — a package is only usable by the specific environment it
   was actually installed into (Section 7), not automatically by every environment on the machine.

10. **"The IDE automatically uses the same Python as the terminal."**
    Incorrect — directly Section 13: the two contexts track interpreter selection independently, and
    can disagree unless explicitly aligned.

11. **"Virtual environments replace package managers."**
    Incorrect — directly Section 21: a virtual environment provides isolation (the place); a package
    manager performs installation (the work) — the two solve different, complementary problems.

12. **"Virtual environments are only useful for AI projects."**
    Incorrect — directly Section 31: the same isolation problem, and the same solution, applies to any
    kind of Python project; AI projects are simply an especially motivating case (Section 32) because
    of how frequently their dependencies change.

---

## 35. Practical Exercises

All exercises use disposable, local practice directories and require no external services, real
credentials, or production data.

### Level 1 — Conceptual

1. In your own words, define "virtual environment" and explain what problem it solves (Section 2,
   Section 4).
2. Define "isolation" as it applies to virtual environments (Section 4).
3. Explain the difference between the global/system Python and a project's virtual environment
   (Section 6).
4. Define "Python interpreter" and explain how a virtual environment relates to it (Section 3, Section
   7).
5. Explain what activation does, and explicitly state what it does *not* do (Section 10).
6. Explain what deactivation does, and explicitly state what it does *not* do (Section 11).
7. In your own words, explain why two projects needing different versions of the same package cause a
   conflict without virtual environments (Section 2).
8. Explain why a virtual environment does not, by itself, guarantee complete reproducibility (Section
   28).

### Level 2 — Hands-On

1. Create a disposable practice directory and create a `.venv` inside it (Section 8, Section 24).
2. Activate the environment using the command appropriate to your actual shell (Section 8).
3. Verify which Python interpreter is currently active (Section 25).
4. Deactivate the environment (Section 11) and verify (Section 25) that the resolved interpreter has
   changed back.
5. Reactivate the same environment and confirm it is the same one as before (its location on disk has
   not changed, Section 10/Section 15).
6. Compare the interpreter path shown while activated against the interpreter path shown while
   deactivated (Section 25), and explain the difference in your own words.
7. Deliberately activate the environment from the wrong directory (one without a `.venv`) and observe
   what happens, connecting the result to Section 26's Failure 2.
8. Remove the practice `.venv` directory and recreate it from scratch (Section 8, Section 16), then
   verify it is usable again (Section 25).

### Level 3 — Reasoning

For each scenario, identify: likely cause, evidence to inspect, corrective action.

1. A package works in Project A but the same package appears unavailable in Project B, on the same
   machine.
2. The terminal reports one Python version; the IDE reports a different one, for the same project.
3. A package was apparently installed (no error occurred), but importing it in code fails.
4. A project worked correctly yesterday but fails today, with no code changes made.
5. Two projects on the same machine need conflicting versions of the same package.
6. A developer activates an environment, but `python --version` still shows the global Python's
   version.
7. A teammate reports a project "works on their machine" but fails identically set up on another
   machine.
8. After deleting a `.venv` directory by mistake, a developer worries the project's source code has
   been lost.

### Level 4 — Debugging

Each provides a symptom, context, expected behavior, and actual behavior. Investigate using Section
27's workflow before concluding. Solutions are not given immediately — work through your own reasoning
first.

1. **Context:** A developer activates `.venv` in the terminal.
   **Expected:** `python --version` shows the version used to create the environment.
   **Actual:** it shows a completely different, older version.
   **Task:** determine whether activation actually succeeded, and what the current `PATH` resolution
   actually is.

2. **Context:** A developer runs `pip install` for a package, then immediately tries to import it.
   **Expected:** the import succeeds.
   **Actual:** the import fails as if the package were never installed.
   **Task:** determine whether the install and the import happened using the same interpreter.

3. **Context:** A developer switches from one open terminal tab to another, both supposedly in the
   same project.
   **Expected:** both tabs show the same active Python.
   **Actual:** one tab shows the virtual environment's Python; the other shows the global Python.
   **Task:** determine why activation state differs between the two tabs.

4. **Context:** A developer's IDE shows a "module not found" warning for a package that is definitely
   installed, confirmed from the terminal.
   **Expected:** the IDE should recognize the installed package.
   **Actual:** it does not.
   **Task:** determine whether the IDE's selected interpreter matches the terminal's.

5. **Context:** A developer tries to activate an environment using a Linux-style command inside
   PowerShell.
   **Expected:** the environment activates normally.
   **Actual:** the command fails or is not recognized.
   **Task:** determine what the correct activation command is for the shell actually in use.

6. **Context:** A developer's `.venv` directory exists, but running the activation script produces an
   error related to script execution being blocked.
   **Expected:** activation completes without error.
   **Actual:** it is blocked.
   **Task:** determine what shell-level restriction might be preventing the script from running.

7. **Context:** A developer recreates a `.venv` from scratch after deleting it, but a package they
   need is now missing.
   **Expected:** the project works exactly as before.
   **Actual:** it does not, because the package was never reinstalled.
   **Task:** determine what step in the lifecycle (Section 16) was skipped.

8. **Context:** Two developers on the same team report different behavior from what should be
   identical project code.
   **Expected:** identical behavior, since the code is unchanged.
   **Actual:** different behavior.
   **Task:** determine what specifically might differ between their two environments (Section 26,
   Section 28).

### Level 5 — Applied AI Engineering

All examples are local, conceptual, and require no API keys or external services.

1. **ML project dependencies:** You are starting a small ML experimentation project on a machine that
   already has an unrelated data-analysis project. Explain how you would set up its environment so
   neither project's dependencies interfere with the other (Section 5, Section 31).
2. **LLM SDK dependencies:** You need to try a newer version of an LLM SDK for one project while
   keeping an existing project on an older, known-working version. Explain how virtual environments
   let you do this on the same machine (Section 2, Section 5).
3. **RAG dependencies:** You are building a small RAG-related prototype alongside your existing ML
   project. Explain why giving the prototype its own environment, rather than adding its dependencies
   to the ML project's existing one, is the safer choice (Section 5, Section 17).
4. **Data-processing dependencies:** A data-processing project's environment has become inconsistent
   after many ad hoc package installs during experimentation. Explain how you would decide whether to
   troubleshoot the existing environment or recreate it (Section 16, Section 26 Failure 6).
5. **Agent/tooling dependencies:** You are asked to onboard a new teammate onto an agent-system project.
   Explain what you would tell them to set up so their environment matches what the project expects,
   and what limits (Section 28) exist to that guarantee using only what this lesson has covered so far.

---

## 36. Structured Debugging Exercise

### "Why Is My Project Using the Wrong Python?"

**Scenario.** A learner has a small project with its own virtual environment, created at
`project-folder/.venv`. They activated the environment in a terminal earlier, installed a package
there, and confirmed it worked. Later, they open the same project in their IDE and run the same code
through the IDE's own "Run" feature. The code fails, reporting that the package cannot be found —
even though the terminal, in the same project folder, still shows it working correctly.

**Learner tasks:**

1. **Reproduce the problem** — confirm the failure occurs consistently when run through the IDE, and
   does not occur when run from the terminal.
2. **Identify expected behavior** — both contexts should be using the project's `.venv` environment,
   and the package should be found in both.
3. **Inspect the current interpreter** — in the terminal, using Section 25's techniques, confirm the
   interpreter path currently active there.
4. **Inspect environment selection** — in the IDE, using its own interpreter-selection display
   (Section 13), determine which interpreter the IDE is actually configured to use for this project.
5. **Inspect package location, conceptually** — reason about where the package was actually installed
   (Section 21) relative to each of the two interpreters identified above (Section 26, Failure 3).
6. **Form a hypothesis** — based on the evidence gathered, state a specific, testable guess for why the
   two contexts disagree.
7. **Test the hypothesis** — compare the terminal's interpreter path directly against the IDE's
   selected interpreter path; do they point to the same `.venv`, or to two different environments (or
   one being the project's `.venv` and the other the global Python)?
8. **Correct the environment selection** — explicitly set the IDE's interpreter selection to match the
   project's actual `.venv` (Section 12, Section 13).
9. **Verify the result** — rerun the code through the IDE and confirm the package is now found
   correctly.
10. **Explain the root cause** — in your own words, state precisely why this specific mismatch caused
    exactly this symptom (echoing Section 2's symptom-vs-root-cause distinction).
11. **Explain how to prevent the issue** — describe what habit (Section 25, Section 27) would have
    caught this mismatch earlier, before it caused confusion.

This exercise requires no external packages and no network access — the specific package involved is
incidental; the actual subject under investigation is the interpreter-selection mismatch itself
(Section 13), which is the true, general-purpose lesson this exercise is built to teach.

---

## 37. Mini-Project

### Project Environment Isolation Lab

Create two small, entirely disposable local Python projects, conceptually representing two unrelated
pieces of work:

```text
Project A
Project B
```

### Requirements

- Each project gets its own directory and its own `.venv`, created independently (Section 8).
- No external services, real credentials, or production data are involved anywhere in this project.
- All work can be done using only what this lesson has covered — no package installation is strictly
  required to demonstrate isolation (Section 23), though you may optionally install one small,
  harmless package differently in each environment if you want to observe isolation directly.

### What you must demonstrate

- **Separate environments** — two distinct `.venv` directories, one per project, confirmed to exist
  independently (Section 15).
- **Separate interpreter selection** — confirming, for each project, which interpreter is active when
  working within it (Section 25).
- **Environment activation** — activating each project's environment in turn (Section 10).
- **Deactivation** — deactivating cleanly between switching from one project to the other (Section 11).
- **Environment verification** — using Section 25's techniques to confirm, with evidence, which
  environment is active at each step, rather than assuming.
- **Dependency isolation concept** — explicitly reasoning (Section 23) about why something installed
  into Project A's environment would not appear in Project B's, even without necessarily installing
  anything at all.
- **Environment recreation** — deleting and recreating at least one of the two environments (Section
  16), then re-verifying it.

### Documentation to produce (in your own notes — this file itself is not to be modified for this
project)

For each of the two projects, document:

- **Project purpose** — a one-sentence description (entirely fictional/disposable is fine).
- **Environment location** — the exact path of its `.venv` directory.
- **Interpreter used** — the specific interpreter path/version confirmed active for this project
  (Section 25).
- **Activation/deactivation process** — the exact commands used, and which shell they were run in.
- **Verification evidence** — what you actually checked to confirm the correct environment was active
  at each step.
- **Failure encountered** — at least one deliberately induced problem (for example, attempting to
  activate from the wrong directory, or checking the interpreter before activating) and what it looked
  like.
- **Troubleshooting process** — how you applied Section 27's systematic workflow to resolve the
  deliberately induced failure.
- **Final result** — confirmation that both environments work correctly and independently.
- **Lessons learned** — in your own words, what this exercise demonstrated about isolation, activation,
  and verification that a purely conceptual reading of this lesson would not have made as concrete.

### Why this project matters

This mini-project is designed to make Section 4's abstract definition of "isolation" into something
directly observed and verified, rather than only read about — applying, in miniature, the exact same
environment-per-project discipline (Section 5, Section 32) that every subsequent Python-based project
in this roadmap will depend on.

---

## 38. Review

- **What is a Python environment?** The combination of a specific interpreter and whatever packages
  are currently installed and accessible to it (Section 3).
- **What is a virtual environment?** An isolated, project-specific Python environment, separate from
  the global Python and from other projects' environments (Section 4).
- **Why does isolation matter?** Without it, different projects' conflicting dependency needs cannot
  all be satisfied by one shared environment (Section 2, Section 5).
- **Global vs. project environment?** The global Python is shared machine-wide; a virtual environment
  is scoped to one specific project (Section 6).
- **What is `venv`?** Python's built-in tool for creating virtual environments (Section 8).
- **What does activation actually do?** Changes the current shell session's command resolution
  (`PATH`) to point at a specific environment's interpreter — it does not create or "start" the
  environment (Section 10).
- **What does deactivation do?** Reverses that shell-session-level change; it does not delete the
  environment (Section 11).
- **How does interpreter selection work?** Different contexts (a terminal session, an IDE) each
  independently resolve which interpreter to use, and can be pointed at different environments
  (Section 12, Section 13).
- **Why can IDE and terminal disagree?** Because their interpreter selection is tracked separately,
  unless both are explicitly aligned to the same environment (Section 13).
- **Virtual environment vs. package manager?** One provides isolation (the place); the other performs
  installation (the work) — complementary, not interchangeable (Section 21).
- **Virtual environment vs. virtual machine?** Python-level isolation vs. full operating-system-level
  virtualization (Section 18).
- **Virtual environment vs. container?** Python-level isolation vs. broader, OS-level application
  packaging; a container can contain a virtual environment, but they are not the same thing (Section
  19).
- **Reproducibility?** Isolation alone is necessary but not sufficient; dependency/version management
  is also required (Section 28).
- **Failure modes?** Interpreter mismatches, activation problems, and installation-target mismatches
  are the most common — all addressed by evidence-based verification rather than guessing (Section 26,
  Section 27).
- **Security boundaries?** A virtual environment isolates which packages are installed, not what those
  packages can do — it is not a security sandbox (Section 29).
- **AI engineering applications?** The same isolation mechanism underlies every Python-based AI project
  this roadmap will build, especially given how rapidly AI libraries change (Section 32).
- **Production implications?** Local environment isolation is the first of several distinct layers
  leading toward reproducible, deployed, production systems (Section 33).

---

## 39. Self-Assessment

- [ ] I can explain a virtual environment in my own words.
- [ ] I understand why global dependencies can cause conflicts.
- [ ] I understand what `venv` provides.
- [ ] I can create a virtual environment.
- [ ] I can activate it.
- [ ] I can deactivate it.
- [ ] I can verify which Python interpreter is being used.
- [ ] I understand why activation changes command resolution.
- [ ] I understand that activation does not create the environment.
- [ ] I understand that deactivation does not delete the environment.
- [ ] I can identify an interpreter mismatch.
- [ ] I can troubleshoot a package/environment mismatch.
- [ ] I understand the relationship between virtual environments and package managers.
- [ ] I understand virtual environment vs. container.
- [ ] I understand virtual environment vs. virtual machine.
- [ ] I understand that a virtual environment is not a security sandbox.
- [ ] I understand the role of virtual environments in AI engineering.
- [ ] I can explain the concept to another beginner.

---

## 40. Interview Questions

**Q: What is a virtual environment?**
A: An isolated, project-specific Python environment — a specific interpreter plus a specific set of
installed packages, kept separate from the global Python and from other projects' environments
(Section 4).

**Q: Why use virtual environments?**
A: To prevent dependency conflicts between projects that need different package versions, and to keep
each project's dependencies clean, isolated, and easier to reproduce (Section 2, Section 5).

**Q: What problem does `venv` solve?**
A: It provides Python's standard, built-in way to actually create an isolated virtual environment
(Section 8), turning the concept of isolation into a real, usable environment on disk.

**Q: What is the difference between global Python and a virtual environment?**
A: Global Python is shared across the whole machine; a virtual environment is scoped specifically to
one project, with its own separate interpreter and package set (Section 6).

**Q: What does activation actually do?**
A: It changes the current shell session's command resolution (via `PATH`) so that `python` and related
commands point to a specific environment's interpreter (Section 10).

**Q: Does activation create a virtual environment?**
A: No. The environment is created separately, using `venv` (Section 8); activation only changes how
the current shell resolves commands, and the environment exists independently of whether it is
currently activated (Section 10).

**Q: What does deactivation do?**
A: It reverses activation's shell-session-level changes; it does not delete the environment or any of
its installed packages (Section 11).

**Q: Why might an IDE use a different Python than the terminal?**
A: Because the IDE and the terminal each independently track which interpreter to use, and can be
configured (or default) to different environments unless explicitly aligned (Section 13).

**Q: Why can a package be installed but still fail to import?**
A: Because it may have been installed into a different environment than the one actually being used to
run the code — a global vs. virtual-environment mismatch, or an interpreter-selection mismatch
(Section 26, Failure 3).

**Q: What is the relationship between virtual environments and package managers?**
A: A virtual environment provides the isolated place where packages are installed; a package manager
performs the actual installation, upgrade, and removal of those packages within that place — different,
complementary responsibilities (Section 21).

**Q: Are virtual environments security boundaries?**
A: No. They isolate which packages are installed for a project, but do not restrict what a package's
code is capable of doing once it runs — they are a dependency-isolation mechanism, not a security
sandbox (Section 29).

**Q: What is the difference between a virtual environment and a container?**
A: A virtual environment isolates Python interpreters and packages; a container packages an application
with broader, OS-level isolation mechanisms — a container can contain a virtual environment, but they
are not the same concept (Section 19).

**Q: Why is `.venv` commonly used?**
A: It is a short, widely recognized convention, with the leading dot marking it as auxiliary tooling
rather than primary project content — but it is a convention, not a technical requirement (Section 9).

**Q: Why might you recreate an environment?**
A: A corrupted or inconsistent environment, a wrong interpreter used at creation, or stale/incompatible
dependencies are common reasons — though recreation should follow, not replace, actually diagnosing the
root cause (Section 16, Section 20).

**Q: How do virtual environments help AI engineering?**
A: AI/ML libraries change rapidly and often have version-specific requirements; isolating each
project's dependencies prevents one project's needs from interfering with another's, which becomes
increasingly important as a developer works on multiple AI projects on the same machine (Section 32).

---

## 41. Architecture / Engineering Questions

**Q: How would you structure Python environments for multiple AI projects on one machine?**
A: Give each project its own dedicated virtual environment (Section 4, Section 9), verified
independently (Section 25), rather than sharing one environment across projects — directly applying
Section 5's isolation rationale at the scale of an entire machine's worth of AI work.

**Q: How would you prevent dependency conflicts between ML and LLM projects?**
A: Keep each project's virtual environment fully separate (Section 5, Section 23), so that each
project's specific framework or SDK version requirements never have to be reconciled against another,
unrelated project's requirements.

**Q: How would you diagnose an environment mismatch in a development team?**
A: Apply Section 27's systematic workflow — explicitly compare each team member's active interpreter
and environment location against what the project expects, rather than assuming everyone's setup
matches just because the code is the same.

**Q: How does local environment isolation relate to production deployment environments?**
A: It is the foundational first layer (Section 33) — production environments build on the same
isolation principle, but typically add dependency-version management and OS-level packaging (a
container or similar deployment mechanism) beyond what a local virtual environment alone provides.

**Q: Why should environment isolation be separated conceptually from dependency management?**
A: Because they solve different problems (Section 21, Section 28) — isolation provides a separate
place; dependency management provides a reliable, reproducible record of exactly what belongs in that
place. Conflating them leads to the misconception (Section 34) that isolation alone guarantees
reproducibility.

**Q: How would you design a reproducible Python development workflow?**
A: Combine a dedicated virtual environment per project (this lesson) with an explicit, maintained
record of that project's dependencies (Section 22, Section 28 — the subject of this module's later
package-manager lesson), so the environment can be reliably recreated from that record rather than
relying on whatever happens to already be installed.

**Q: How would virtual environments fit into a future containerized AI application?**
A: A container can hold a Python virtual environment as one of its internal pieces (Section 19),
combining the container's broader, OS-level packaging and isolation with the Python-specific dependency
isolation this lesson teaches — the two mechanisms operate at different layers and are not
interchangeable.

**Q: What problems remain unsolved even after using virtual environments?**
A: Complete reproducibility (without an explicit dependency-version record, Section 28), security
(virtual environments provide no protection against malicious or vulnerable package code, Section 29),
and OS-level or hardware-level differences between machines (which a Python-level isolation mechanism
does not address at all, Section 18).

---

## 42. Production Application

```text
Developer Machine
        v
Project-Specific Environment
        v
Controlled Dependencies
        v
Reproducible Development
        v
Build / Deployment Environment
        v
Production Runtime
```

Understanding environment isolation — precisely, at the level of mental model this lesson has built,
not merely as a sequence of commands — is foundational for:

- **backend engineering** — services with their own dependency sets, isolated the same way,
- **ML engineering** — training and inference code with framework-specific dependency needs (Section
  32),
- **LLM application engineering** — SDK and supporting library dependencies (Section 32),
- **RAG systems** — retrieval and storage client dependencies (Section 31, Section 32),
- **agent systems** — orchestration and tooling dependencies (Section 31, Section 32),
- **deployment** — the transition from a developer's local environment toward a controlled,
  reproducible build (Section 33),
- **containers** — a later-stage mechanism that can itself hold a Python virtual environment (Section
  19, Section 33),
- **cloud environments** — remote infrastructure that ultimately still runs Python code within some
  environment, built on the same underlying isolation principle.

None of these later subjects are taught in depth here. The purpose of this section is only to
establish that the environment-isolation mental model built in this lesson is not a beginner-only
concern — it is the first, foundational layer of a progression that continues throughout the rest of
this roadmap.

---

## 43. Key Takeaways

- A virtual environment isolates project-level Python dependencies from the global Python and from
  other projects.
- `venv` is Python's standard, built-in mechanism for creating virtual environments.
- Activation is primarily a shell convenience for selecting environment-specific commands/interpreters
  — it does not create or "start" the environment.
- Deactivation does not delete the environment.
- A virtual environment is not a virtual machine.
- A virtual environment is not a container.
- A virtual environment is not a security sandbox.
- Virtual environments reduce dependency conflicts between projects.
- Virtual environments improve development isolation but do not alone guarantee complete
  reproducibility.
- Package managers and virtual environments solve different, complementary problems.
- Interpreter selection is critical — the same code can behave differently under a different
  interpreter.
- Terminal and IDE environments can disagree, and should be explicitly verified rather than assumed to
  match.
- Environment problems should be investigated using evidence rather than guesswork.
- Virtual environment knowledge is foundational for Python-based Applied AI Engineering, and for every
  layer of production engineering built on top of it.
