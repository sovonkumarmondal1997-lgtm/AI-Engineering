# Project Structure

**Module:** Developer Environment
**Roadmap reference:** Stage 0 — Module 0.4 — Developer Environment
**Concept(s) covered:** project structure, foundational `pyproject.toml`
**Prerequisites:** Module 0.1 (How Computers Work), Module 0.2 (Operating System Fundamentals),
Module 0.3 (Command Line), Module 0.4 Lessons 01–07 (VS Code and Terminal, IDE Concepts, Extensions,
Formatters and Linters, Debugger, Virtual Environments, Package Managers)
**Status:** Complete

All file trees, configuration examples, and command output shown in this lesson are illustrative
teaching examples, clearly labeled as such. No command was actually executed while writing this
lesson, and no tool output, package version, or file listing is presented as genuine execution
evidence.

---

## 1. Introduction

### What project structure means

**Project structure** is how a project's files and directories are organized — which pieces live
where, and why. It is not decoration; it is a deliberate answer to a real engineering question: "when
someone (including future you) needs to find the source code, the tests, the configuration, or the
documentation, where do they look?"

### Why this lesson exists

Every lesson so far in Module 0.4 has focused on a *tool*: an editor (`01-vscode-and-terminal.md`),
an IDE's capabilities (`02-ide-concepts.md`), extensions (`03-extensions.md`), formatters and linters
(`04-formatters-and-linters.md`), a debugger (`05-debugger.md`), an isolated environment
(`06-virtual-environments.md`), and a package manager (`07-package-managers.md`). This lesson is
different: it is about how the **project itself** — the actual files a developer writes, organizes,
and shares — should be arranged so that all of those tools, and the humans using them, can work with
it effectively.

### Where this fits in Module 0.4

```text
01 VS Code and Terminal
02 IDE Concepts
03 Extensions
04 Formatters and Linters
05 Debugger
06 Virtual Environments
07 Package Managers
08 Project Structure   <-- this lesson (final lesson of Module 0.4)
```

### How it builds on virtual environments and package managers

`06-virtual-environments.md` established that a project needs its own isolated environment
(conventionally `.venv`). `07-package-managers.md` established that a package manager (`pip` or `uv`)
populates that environment with dependencies, and briefly previewed that `pyproject.toml` declares
what those dependencies are (`07-package-managers.md`, Section 23). This lesson picks up exactly
there: it places `.venv` and `pyproject.toml` correctly within a project's overall structure, and
teaches `pyproject.toml` itself at the foundational level this module requires — full depth on
Python packaging is a later roadmap stage (Section 4, Section 48).

---

## 2. What Is a Project?

### Core vocabulary

- **Project** — a directory (and everything inside it) that a developer treats as one coherent unit
  of work, intended to work together toward one purpose.
- **Application** — the actual running program a project produces — what the project's source code,
  once executed, does.
- **Source code** — the human-written code that defines the application's behavior (Module 0.1;
  `05-debugger.md`, Section 1).
- **Configuration** — values that control how the application behaves without being part of its core
  logic (expanded fully in Section 9).
- **Dependencies** — external packages the project's code relies on (`07-package-managers.md`,
  Section 2, Section 7).
- **Documentation** — written material explaining what the project is, how it works, and how to use
  it (Section 8).
- **Tests** — code written specifically to check that the application behaves correctly
  (`05-debugger.md`, Section 16; expanded in Section 7).
- **Generated artifacts** — files produced *by* running the project, rather than written by a
  developer as part of it (expanded fully in Section 10).

### Distinguishing a project from a single source-code file

A single `.py` file with a few lines of code is not yet a "project" in the sense this lesson uses the
word — it is just source code. A **project** exists once there is enough surrounding structure
(dependencies to manage, configuration to track, tests to keep separate, documentation for others to
read) that *how it is organized* becomes a real engineering decision, not an afterthought. This
lesson is about that organizational decision — not about any one specific file's contents.

---

## 3. Why Project Structure Matters

Good project structure directly affects:

- **Readability** — a newcomer (or future you) can predict where to look for something, rather than
  searching the entire project.
- **Maintainability** — changes are easier to make safely when related things are grouped together
  and unrelated things are kept apart (Section 25).
- **Discoverability** — tools, teammates, and automated systems can locate the project's important
  parts (source, tests, configuration) using consistent, predictable locations.
- **Collaboration** — a shared, understood structure lets multiple people work on the same project
  without constantly re-explaining "where does this go?"
- **Testing** — a clear separation between application code and tests (Section 7) makes it obvious
  what is being tested and what is doing the testing.
- **Tooling** — IDEs, formatters, linters, debuggers, and package managers (Module 0.4's previous
  lessons) all work better when they can reliably find the project root, source, and configuration
  (Section 28).
- **Debugging** — `05-debugger.md`, Section 17's systematic workflow depends on knowing exactly where
  relevant code and configuration live; disorganized projects make "reproduce the problem" and
  "identify the smallest useful reproduction" harder than they need to be.
- **Dependency management** — `07-package-managers.md`'s entire workflow assumes a predictable place
  for environment and dependency declarations (Section 12, Section 13).
- **Deployment** — preparing a project to run somewhere else depends on knowing precisely what is
  source, what is configuration, and what should never leave the developer's own machine (Section 24,
  Section 31).
- **Scalability of the codebase** — a structure that works for ten files does not automatically work
  for a thousand; deliberate organization is what allows a project to keep growing without collapsing
  into confusion (Section 4 shows what happens without it).

### Why "everything in one folder" becomes problematic as projects grow

A handful of files in one flat folder is easy to keep track of by memory alone. As a project
accumulates more source files, more configuration, more generated output, and more contributors, that
same flat approach stops scaling — there is no longer one person who can hold "where everything is"
in their head, and nothing in the structure itself helps anyone else figure it out.

---

## 4. The Problem With an Unstructured Project

### A conceptual example

```text
my-project/
├── random.py
├── test.py
├── model.py
├── data.csv
├── output.csv
├── notes.txt
├── config.json
├── model-final-final-v2.py
├── temp.py
├── secret.txt
└── ...
```

### The engineering problems this creates

- **Ambiguous purpose** — `random.py` and `temp.py` give no indication of what they actually do or
  whether they are still needed.
- **Version confusion** — `model.py` and `model-final-final-v2.py` coexisting suggests neither name
  reliably indicates which one is actually current or in use — directly the kind of version confusion
  `07-package-managers.md`, Section 8 warned about, now happening to the project's *own* code instead
  of a dependency.
- **No separation of tests from application code** — `test.py`, sitting alongside `model.py` with no
  distinguishing structure, gives no clear signal of what is being tested versus what is the actual
  application (Section 7).
- **Data and output mixed with source code** — `data.csv` and `output.csv` sit directly alongside the
  code that presumably produced or consumes them, with nothing distinguishing "input the project
  needs" from "output the project generated" (Section 10).
- **A secret sitting in plain view** — `secret.txt`, with no `.gitignore` (Section 11) or separation
  from the rest of the project, is at real risk of being accidentally shared or committed to version
  control (Section 31).
- **No documentation** — `notes.txt` is not a substitute for an actual README (Section 8) explaining
  what the project is or how to use it.

### An important accuracy boundary

**This lesson does not claim that every flat project structure is inherently wrong.** A very small,
genuinely simple script might legitimately need nothing more than a single file. The problem above is
not "files existing in one folder" in the abstract — it is the *absence of any deliberate
organization* as a project's real complexity (multiple source files, tests, data, secrets, generated
output) grows past what a flat layout can clearly represent. **Structure should match project
complexity and requirements** — a principle Section 21 returns to directly.

---

## 5. Basic Project Structure

### A simple conceptual example

```text
my-project/
├── src/
├── tests/
├── docs/
├── .venv/
├── pyproject.toml
├── README.md
└── .gitignore
```

### Every component, briefly

- **`src/`** — the project's own source code (Section 6).
- **`tests/`** — code that tests the application (Section 7).
- **`docs/`** — documentation beyond the top-level README (Section 8).
- **`.venv/`** — the project's isolated virtual environment (`06-virtual-environments.md`, Section 9;
  Section 12 below).
- **`pyproject.toml`** — the project's metadata/configuration file (Section 14 onward).
- **`README.md`** — the project's primary, top-level explanation (Section 8).
- **`.gitignore`** — a list of files/patterns Git should not track (Section 11).

### An important accuracy boundary

**This lesson does not imply that this exact structure is mandatory for every Python project.**
Section 20 introduces alternative, equally legitimate layouts. This example exists to give a concrete,
labeled starting point for the detailed, component-by-component explanations in Sections 6–13.

---

## 6. Source Code Directory

### Core vocabulary

- **Source code** — already defined in Section 2: the human-written code defining the application's
  behavior.
- **Application logic** — the specific source code responsible for what the application actually
  does, as opposed to tests, configuration, or documentation.
- **Modules** — individual source files containing code (`07-package-managers.md`, Section 2).
- **Packages, at a foundational level** — a way of organizing related modules together under one
  named grouping, so that related code can be imported and referred to as a unit. This lesson uses
  this word only at this introductory level — the deeper mechanics of how Python's own import system
  treats packages belong to later, dedicated material (Section 4's scope boundary).

### Why source code is separated from other project assets

Keeping source code in its own clearly identified location (commonly `src/`, Section 5) means tools,
tests, and teammates can immediately identify "this is the application's actual logic" without it
being mixed together with tests, generated output, or configuration.

### Introducing `src/` carefully

A **`src/` layout** places a project's source code inside a dedicated `src/` directory (typically with
a further subdirectory named after the project or package itself), rather than directly in the
project's root. This is one common, widely used convention — not the only one (Section 20 compares it
directly against a simpler alternative).

### Multiple legitimate layouts exist

**This lesson does not turn this into advanced packaging.** Whether source code lives directly in the
project root, in a `src/` subdirectory, or in some other arrangement, is a real design decision
(Section 20, Section 21) — not something with one single universally correct answer, and not
something this foundational lesson resolves definitively on the learner's behalf.

---

## 7. Tests Directory

### Why tests are separated

Directly connecting to `05-debugger.md`, Section 16: a **test** is code written specifically to run
other code and check whether its actual behavior matches an expected outcome. Keeping tests in their
own directory (conventionally `tests/`, Section 5) makes clear which code is *being tested* (the
application, in `src/`) and which code *does the testing*.

### Why tests should not normally be mixed with application code

Mixing test code directly among application source files blurs exactly this distinction — a reader
(or a tool) cannot easily tell, at a glance, "is this file part of what the application does, or is
it verifying that something else works correctly?"

### How tests help catch regressions

A **regression** is a previously working piece of behavior that breaks again later, often as a side
effect of an unrelated change. Tests, run repeatedly, are what actually catch this — directly echoing
`04-formatters-and-linters.md`, Section 16 ("Test confirms the fix") and `05-debugger.md`, Section 17,
step 15 ("add/strengthen a regression test").

### How project structure makes testing easier

A clear, separate `tests/` directory makes it obvious, both to a human and to test-running tooling,
exactly what should be executed when "running the tests" — rather than requiring some other mechanism
to distinguish test code from everything else in the project.

**Scope note:** this lesson does not teach `pytest` (or any specific testing tool) in depth — testing
itself receives its own, deeper treatment later in the roadmap (Section 48). Here, only the
*organizational* role of a tests directory is taught.

---

## 8. Documentation Directory

### Core vocabulary

- **README** — the project's primary, top-level document, typically the first thing anyone opens to
  understand what the project is and how to use it.
- **Documentation** — more detailed written material beyond what a single README can reasonably hold
  — architecture notes, usage instructions, and similar, commonly kept in a dedicated `docs/`
  directory (Section 5).
- **Architecture notes** — documentation specifically explaining how a project's pieces fit together
  and why particular design decisions were made.
- **Usage instructions** — documentation explaining how to actually run or use the project.
- **Learning notes** — documentation capturing what a developer learned or decided while building the
  project — directly relevant to this roadmap's own learning-journal spirit.

### Three distinct levels of documentation

| Level | Purpose | Typical location |
|---|---|---|
| **Project README** | A short, high-level overview — what this is, how to get started | `README.md`, at the project root |
| **Detailed documentation** | Deeper material — architecture, detailed usage, design decisions | `docs/` directory (Section 5) |
| **Source-code comments/docstrings** | Explaining specific, non-obvious pieces of code, directly next to that code | Inline, within the source files themselves (`src/`, Section 6) |

Each serves a different reader, at a different level of detail — a newcomer typically starts with the
README, someone needing deeper understanding turns to `docs/`, and someone reading a specific piece of
code benefits from comments/docstrings explaining *that specific code's* non-obvious reasoning.

**Scope note:** this is not a full documentation course — only the organizational placement of each
level is taught here.

---

## 9. Configuration

### Configuration vs. code

**Configuration** is data that controls how an application behaves, kept separate from the application
logic itself — for example, a setting controlling which environment a service should connect to. Code
defines *what the application does*; configuration adjusts *how it does it* in a specific situation,
without requiring the code itself to change.

### Environment-specific configuration

Different situations (a developer's own machine, a shared testing setup, eventually production —
Section 24) often need different configuration values, even while running the exact same source code.

### Configuration files

Configuration is commonly stored in dedicated files, separate from source code — directly why a
project structure benefits from a clear, identifiable location for configuration (Section 5's example
keeps configuration-related files at the project root or in a dedicated directory, depending on the
project).

### Environment variables

Directly connecting to Module 0.3 and `01-vscode-and-terminal.md`, Section 4: **environment
variables** are one common mechanism for supplying configuration to a running program, without that
configuration needing to be written directly into a file inside the project at all.

### Secrets

A **secret** — a credential, API key, or similarly sensitive value — is a particular, especially
sensitive category of configuration. **Secrets should not be committed to source control.** This
principle is stated here and enforced concretely in Section 11 (`.gitignore`) and Section 31
(security).

**Scope note:** this lesson does not teach advanced secret-management systems (a later-stage,
production-engineering topic) — only the foundational principle that secrets are configuration, and
must be kept separate from, and out of, a project's committed source code.

---

## 10. Generated Files and Artifacts

### Core vocabulary

- **Generated files** — files produced by *running* the project, rather than written directly by a
  developer as part of it.
- **Build artifacts** — files produced by a build process (mentioned here only for completeness — deep
  build mechanics are a later-stage topic, Section 4's scope boundary).
- **Model artifacts** — files produced or used by a machine-learning model (for example, a saved
  model checkpoint).
- **Logs** — records of what happened while a program ran (previewed conceptually in
  `05-debugger.md`, Section 15).
- **Caches** — files kept around to speed up a later, repeated operation (`07-package-managers.md`,
  Section 28).
- **Temporary files** — files meant to exist only briefly, during a specific operation.
- **Output files** — the actual results a program produces when run.

### Why these should be distinguished from source code

Generated files are not something a developer directly authored — they can typically be *regenerated*
by rerunning whatever produced them, given the same source code and inputs (directly echoing
`06-virtual-environments.md`, Section 15's "environment = disposable project infrastructure" — the
same "regenerable, not irreplaceable" reasoning applies here, now to generated *output* rather than to
an environment).

### AI-specific examples

- **Model checkpoints** — a saved snapshot of a trained model's parameters, often quite large.
- **Embeddings** — numerical representations of data, commonly produced by a model as part of a
  pipeline.
- **Evaluation results** — the output of measuring how well a system performs.
- **Datasets** — the input data a project processes or trains on.
- **Generated reports** — summaries or visualizations produced from a project's own output.

### Not every generated artifact belongs inside the source repository

Some generated artifacts (small, essential configuration-like output) may reasonably be kept with the
project; many others — especially large datasets and model checkpoints — are commonly kept *outside*
the source repository entirely (in dedicated storage suited to large files), with only a reference to
where they live kept inside the project. Section 22, Section 23, and Section 34 (Level 5) return to
this specific AI-relevant decision directly.

---

## 11. `.gitignore`

### What `.gitignore` is

A **`.gitignore`** file is a list of file/directory name patterns that tells Git (a version-control
tool, previewed only at a high level in `02-ide-concepts.md`, Section 4) which files should *not* be
tracked.

### Why it exists

Not every file in a project directory belongs in version control (Section 5) — generated artifacts
(Section 10), environment directories (Section 12), and secrets (Section 9) are all things a project
typically needs *present on disk* to run, but does not want *tracked and shared* through version
control.

### Commonly ignored types of files

- `.venv/` — the project's own virtual environment (`06-virtual-environments.md`, Section 15's
  "disposable infrastructure" — Section 12 below explains this specifically).
- Caches — regenerable, not meaningfully part of the project's actual source.
- Temporary files — not meant to persist or be shared at all.
- Generated artifacts (Section 10) — regenerable from source, and often too large or too frequently
  changing to usefully track.
- Local environment/configuration files — settings specific to one developer's own machine, not
  meant to be imposed on everyone else working on the project.

### An important accuracy boundary

**`.gitignore` prevents selected files from being newly tracked by Git — it does not delete files
from disk, and it does not teach Git itself.** A file listed in `.gitignore` remains exactly where it
is; Git simply stops offering to track changes to it. This lesson does not teach Git in depth — that
is a separate, later topic.

---

## 12. The `.venv` Relationship

This connects directly to `06-virtual-environments.md`.

```text
Project
|
+-- source code
+-- tests
+-- documentation
+-- configuration
+-- pyproject.toml
\-- .venv
```

### The relationship, stated precisely

- **`.venv` belongs to the local development environment** — it is infrastructure for *running* the
  project (`06-virtual-environments.md`, Section 4), not the project's own work product.
- **Source code is the project** — the actual, original work a developer authored; what makes this
  project *this* project, as opposed to any other.
- **`.venv` is an environment used to run the project** — regenerable at any time
  (`06-virtual-environments.md`, Section 16) from the project's own declared dependencies (Section
  17), given a Python installation and a package manager.
- **`.venv` should generally not be committed to version control** — directly why it is a standard,
  common entry in `.gitignore` (Section 11): it is large, machine-specific, and entirely
  regenerable — none of the properties that make something worth tracking in version control.

**Scope note:** this section deliberately does not repeat the complete virtual-environment lesson —
its full mechanics (creation, activation, interpreter selection) belong to `06-virtual-environments.md`
alone. Here, `.venv` is placed correctly within the *project's overall structure*, which is this
lesson's own subject.

---

## 13. The Package Manager Relationship

This connects directly to `07-package-managers.md`.

```text
Project
   |
Project metadata/configuration
   |
Package manager
   |
Virtual environment
   |
Installed dependencies
   |
Application
```

### The roles, made explicit

- **Project structure** (this lesson) — the physical organization of files and directories.
- **`pyproject.toml`** (Section 14 onward) — where the project *declares* its metadata and
  dependencies.
- **Package manager** (`07-package-managers.md`, Section 4) — the tool (`pip` or `uv`) that reads
  those declared dependencies and installs them.
- **Virtual environment** (`06-virtual-environments.md`, Section 4) — the isolated place those
  dependencies actually get installed into.
- **Installed packages** — the result: a populated, isolated environment the application can actually
  run against.

### Making the boundaries explicit

Each of these five plays a genuinely different role, directly echoing `06-virtual-environments.md`,
Section 15's "pyproject.toml" preview and `07-package-managers.md`, Section 15's "do not blur these
roles" principle, now extended one layer further: project structure is *where things live*;
`pyproject.toml` is *what the project declares it needs*; the package manager is *the tool that acts
on that declaration*; the virtual environment is *where the result lives*. None of these four
substitutes for any of the others.

---

## 14. What Is `pyproject.toml`?

### Precise, beginner-friendly definition

**`pyproject.toml`** is a standardized Python project configuration/metadata file — a single,
structured file where a project records information about itself (its name, version, dependencies,
and tool configuration) in a format both humans and tools can read reliably.

### Why modern Python tooling uses it

Before a single standardized file like this existed, different tools each tended to expect their own,
separate configuration file, which meant a project's overall configuration could be scattered across
many different files, each with its own format. `pyproject.toml` gives the broader Python tooling
ecosystem one common, standard place to look (Section 18 expands this specifically).

### What `pyproject.toml` is NOT

This is an essential accuracy boundary for this lesson:

- **Not a Python script** — it does not contain executable Python code; it is a structured data/
  configuration file, in a format called TOML.
- **Not a virtual environment** — it does not create or contain an isolated environment
  (`06-virtual-environments.md`, Section 4); it only *declares* what a project needs (Section 17).
- **Not a package manager** — it does not itself install anything (`07-package-managers.md`, Section
  4); `pip` or `uv` reads it and does the actual installation work.
- **Not a dependency itself** — it describes a project's dependencies; it is not one of them.

---

## 15. Why `pyproject.toml` Exists

### The engineering problems it helps address

- **Project metadata** — a project needs some standard place to record its own name, version, and
  description.
- **Tool configuration** — as previewed in `04-formatters-and-linters.md`, Section 13 and
  `03-extensions.md`, Section 11: formatters, linters, and other tools need configuration, and a
  single standard file gives them a common, predictable place to find it (Section 18).
- **Dependency declarations** — directly `07-package-managers.md`, Section 22, Section 23: a
  structured, standard record of exactly what a project depends on, supporting reproducibility.
- **Standardized project configuration** — one agreed format the broader Python ecosystem can rely on,
  rather than every tool inventing its own.
- **Interoperability between Python tools** — because many different tools can read the *same* file,
  they can cooperate around one shared source of truth about the project, rather than each needing
  separate, possibly inconsistent configuration of their own.

This lesson keeps this explanation strictly foundational — the deeper standards and mechanics behind
`pyproject.toml` (build backends, packaging metadata standards, and similar) belong to the later,
dedicated Stage 6.2 Packaging module (Section 4, Section 48).

---

## 16. Basic `pyproject.toml` Structure

### A small conceptual example

```toml
[project]
name = "example-project"
version = "0.1.0"
description = "Example Python project"
requires-python = ">=3.12"
dependencies = [
    "some-package",
]
```

### Each field, explained

- **`[project]`** — a section header, grouping the fields that describe the project itself.
- **`name`** — the project's own name.
- **`version`** — the project's current version (`07-package-managers.md`, Section 8's version concept,
  now applied to the project itself rather than to a dependency).
- **`description`** — a short, human-readable summary of what the project is.
- **`requires-python`** — the range of Python interpreter versions (`06-virtual-environments.md`,
  Section 3) the project is declared to support.
- **`dependencies`** — the project's own direct dependencies (`07-package-managers.md`, Section 7),
  listed by name (and, commonly, version constraints).

### Important accuracy notes

**This lesson does not invent a real package version, and does not claim this exact configuration is
universally correct.** `some-package` above is a clearly fictional placeholder, not a real,
recommended dependency. The actual fields, values, and dependency specifications any real project
needs depend entirely on that specific project — this example exists only to make the *structure and
purpose* of a `pyproject.toml` file concrete, not to prescribe one correct configuration for every
project.

---

## 17. `pyproject.toml` and Dependencies

```text
pyproject.toml
      |
declares project/dependency information
      |
package manager
      |
resolves/installs dependencies
      |
virtual environment
```

`pyproject.toml`'s `dependencies` field (Section 16) is a **declaration** — a statement of what the
project needs. A package manager (`pip` or `uv`, `07-package-managers.md`) reads that declaration,
resolves what it actually requires (including transitive dependencies,
`07-package-managers.md`, Section 7), and installs the result into the project's virtual environment
(`06-virtual-environments.md`).

**Scope note, strictly enforced:** this lesson does not teach dependency resolution in depth — how a
package manager decides on a specific, compatible combination of versions to satisfy a project's
declared requirements. That mechanism was already deliberately kept out of scope in
`07-package-managers.md`, Section 8, and remains out of scope here; this section exists only to
connect `pyproject.toml`'s declaration role to that lesson's already-established package-manager
concepts.

---

## 18. `pyproject.toml` and Tools

Modern Python tooling can use `pyproject.toml` as a shared configuration location, rather than each
tool requiring its own separate file.

- **Formatters** (`04-formatters-and-linters.md`) — can read formatting-related settings from
  `pyproject.toml`.
- **Linters** (`04-formatters-and-linters.md`) — can similarly read their own rule configuration from
  it.
- **Type checkers** (introduced only for this list, per `04-formatters-and-linters.md`, Section 10's
  boundary — not taught in depth here) — can also be configured through it.
- **Test tooling** (Section 7's testing preview) — can likewise be configured through it.

### The architectural role, not a configuration guide

**This lesson does not turn this into a deep configuration guide** for any of these tools. The point
here is architectural: `pyproject.toml` can serve as **one centralized location** several different,
otherwise-independent tools can all read from — directly extending the "IDE as tool-integration
layer" pattern already established in `02-ide-concepts.md`, Section 11 and `03-extensions.md`, Section
11, now applied to configuration itself rather than to execution.

---

## 19. Project Structure vs `pyproject.toml`

### The distinction, stated precisely

- **Project structure** = the physical organization of a project's files and directories (Sections
  2–13 of this lesson).
- **`pyproject.toml`** = project metadata and configuration (Sections 14–18 of this lesson) — a
  single file describing and configuring aspects of the project.

### One is physical organization; the other describes/configures the project

Project structure answers "where does everything live?" `pyproject.toml` answers "what is this
project, and what does it need?" A project could, in principle, have excellent physical organization
and a poorly maintained `pyproject.toml`, or vice versa — they are related, complementary aspects of
a well-run project (Section 6's mental model diagram in Section 44 places both explicitly), not the
same thing, and improving one does not automatically improve the other.

---

## 20. Common Python Project Layouts

### Simple layout

```text
project/
├── app.py
├── tests/
├── pyproject.toml
└── README.md
```

Source code lives directly at the project root (here, as a single `app.py`, though a small simple
layout project can have more than one root-level source file), rather than inside a dedicated
subdirectory.

### Source layout

```text
project/
├── src/
│   └── package_name/
├── tests/
├── pyproject.toml
└── README.md
```

Source code lives inside a dedicated `src/` directory (Section 6), commonly further nested inside a
subdirectory named after the project's own package.

### Trade-offs

| | Simple layout | Source (`src/`) layout |
|---|---|---|
| **Simplicity** | Easier to navigate for a very small project | Slightly more nesting to move through |
| **Clarity for larger projects** | Can become ambiguous as more top-level files accumulate | Keeps source code clearly, unambiguously separated from everything else at the project root |
| **Common for** | Small scripts, quick prototypes | Projects expected to grow, or intended to be installed/distributed as a package (a later-stage concern, Section 4) |

### No universal winner

**This lesson does not claim one structure is universally correct.** Both are legitimate, widely used
conventions — Section 21 teaches how to reason about which fits a specific project.

---

## 21. Choosing a Project Structure

### Factors to weigh

- **Project size** — a handful of files versus dozens or hundreds.
- **Number of developers** — one person working alone versus a team needing shared, predictable
  conventions (Section 3's collaboration point).
- **Application type** — a small script versus a larger service.
- **Test requirements** — how much testing (Section 7) the project actually needs.
- **Packaging requirements** — whether the project is ever meant to be installed or distributed as a
  package (a later-stage concern, Section 4's scope boundary) — a factor that often favors a `src/`
  layout (Section 20).
- **Deployment model** — how, and to where, the project will eventually run (Section 24).
- **Expected growth** — whether the project is likely to stay small or grow substantially over time.
- **Tooling** — what the project's chosen formatter, linter, tests, and package manager
  (`04-formatters-and-linters.md`, `07-package-managers.md`) expect or work best with.

### The guiding principle

**Use the simplest structure that provides the necessary separation and maintainability.** More
structure than a project actually needs adds unnecessary overhead (directly connecting to Section
33's misconception that "more directories automatically mean better architecture"); less structure
than a project actually needs recreates Section 4's problems as the project grows. The right amount
of structure is the amount that genuinely serves the project's real, current complexity — not a fixed
target to reach for its own sake.

---

## 22. Project Structure for AI Engineering

### A conceptual example

```text
ai-project/
├── src/
│   └── application/
├── tests/
├── configs/
├── data/
├── models/
├── evaluations/
├── notebooks/
├── scripts/
├── docs/
├── .venv/
├── pyproject.toml
├── README.md
└── .gitignore
```

### Every directory, explained

- **`src/application/`** — the project's own source code (Section 6), following a `src/` layout
  (Section 20).
- **`tests/`** — the project's tests (Section 7), covering the application code.
- **`configs/`** — configuration (Section 9), commonly separated out further in AI projects because
  many different runs/experiments may each need their own configuration.
- **`data/`** — datasets the project processes or trains on (Section 10).
- **`models/`** — model artifacts, such as saved checkpoints (Section 10).
- **`evaluations/`** — evaluation results (Section 10) — the output of measuring how well a model or
  system performs.
- **`notebooks/`** — interactive, exploratory work, kept separate from the project's actual
  application source (Section 25 explains why this separation matters specifically).
- **`scripts/`** — small, standalone scripts (for example, one-off data-processing or setup tasks) that
  are not part of the core application itself.
- **`docs/`** — documentation (Section 8).
- **`.venv/`** — the project's isolated environment (Section 12).
- **`pyproject.toml`** — the project's metadata/configuration (Sections 14–18).
- **`README.md`, `.gitignore`** — as in Section 5, Section 11.

### An important accuracy boundary

**This is an example, not a mandatory universal AI project structure.** A real AI project's actual
structure depends on its specific size, purpose, and the same factors introduced in Section 21 —
this layout is a labeled, educational illustration of how the general project-structure principles
from earlier sections apply specifically to AI work, not a template every AI project must follow
exactly.

---

## 23. AI Project Structure and Reproducibility

### How structure supports reproducibility

- **Reproducibility** — directly connecting to `06-virtual-environments.md`, Section 28 and
  `07-package-managers.md`, Section 22: a clear, consistent structure (Section 22) makes it easier to
  know exactly which code, configuration, and data produced a given result, which is a prerequisite
  for being able to reproduce that result later.
- **Experiment organization** — separating configuration (`configs/`) from results (`evaluations/`)
  from the code that produced them (`src/`) makes it possible to trace which specific configuration
  led to which specific outcome.
- **Model/evaluation separation** — keeping `models/` (the artifact) and `evaluations/` (the
  assessment of that artifact) distinct makes it clear which evaluation results correspond to which
  specific model.
- **Data lineage, at a basic level** — knowing, structurally, where `data/` sits relative to `src/`
  and `models/` at least establishes the basic shape of "this data went in, this code processed it,
  this model/result came out" — a foundational precursor to the deeper data-lineage practices taught
  in later, dedicated material.
- **Dependency management** — Section 13's chain, applied specifically to an AI project's often
  larger and more complex dependency set (`07-package-managers.md`, Section 30).
- **Collaboration** — Section 3's collaboration point, especially valuable in AI projects where
  experiments, data, and models change frequently and need to remain understandable to teammates.
- **Debugging** — a clear structure makes `05-debugger.md`, Section 17's workflow easier to apply,
  since the relevant code, configuration, and data are not tangled together.

**Scope note:** this lesson does not teach advanced MLOps (a later-stage discipline covering deeper
experiment tracking, data versioning, and pipeline automation) — only the foundational, structural
contribution to reproducibility that good project organization provides.

---

## 24. Project Structure and Deployment

### How clean organization helps later, at a foundational level

- **Application packaging** — a project with a clearly identified source directory (Section 6) and
  declared dependencies (`pyproject.toml`, Section 17) is far easier to package for distribution or
  deployment than one with source, data, and configuration all tangled together.
- **Containers** (a later-stage topic, mentioned only as a forward reference,
  `06-virtual-environments.md`, Section 19 and Section 33) — a container built from a project needs to
  know exactly what to copy in (source, `pyproject.toml`) and what to leave out (`.venv`, generated
  artifacts, secrets) — directly the same distinctions this lesson has already established (Section
  11, Section 12).
- **Deployment** — running the project somewhere other than a developer's own machine depends on
  being able to reliably recreate its environment (Section 13) from its declared dependencies, and on
  knowing precisely which files actually constitute "the application" versus local development
  infrastructure.
- **CI/CD** (a later-stage topic, mentioned only as a forward reference,
  `04-formatters-and-linters.md`, Section 23) — automated pipelines typically need to locate the
  project's source, tests, and dependency declarations using the same predictable structure a human
  developer relies on.
- **Configuration** — Section 9's environment-specific configuration concept becomes directly relevant
  once a project needs to behave correctly in more than one place (a developer's machine, a shared
  test environment, eventually production).
- **Testing** — Section 7's separated tests directory is exactly what an automated deployment pipeline
  would run before allowing a change to proceed.

**Scope note, strictly enforced:** this lesson does not teach Docker, Kubernetes, or CI/CD in depth —
those are dedicated, much later roadmap stages (Section 48). This section establishes only *why* good
project structure makes those later topics easier when the learner eventually reaches them.

---

## 25. Project Structure and Separation of Concerns

### The concept

**Separation of concerns** means keeping genuinely different kinds of things — application code,
tests, configuration, documentation, data, generated artifacts, environment files — in genuinely
separate places, rather than mixing them together.

### Why separation reduces confusion and change risk

When each kind of content has its own clear, predictable location (Sections 6–13, Section 22), a
change to one of them (for example, updating configuration) does not require touching, or even
looking at, unrelated content (for example, application source code) — reducing both the *confusion*
of figuring out what is relevant to a given change, and the *risk* of accidentally affecting something
unrelated while making it.

### An explicit example, connecting back to Section 22

Separating `notebooks/` from `src/application/` (Section 22) is a direct instance of this principle:
exploratory, interactive work (notebooks) is a genuinely different *kind* of concern than the
project's actual, maintained application logic — keeping them apart prevents exploratory code from
being mistaken for, or accidentally relied upon as, production logic (directly connecting to Section
33's misconception: "notebooks should always contain the production logic").

**Scope note:** this lesson does not turn this into a full software-architecture course — Section 48
explicitly preserves the boundary with the later, dedicated Software Engineering stage covering
deeper architectural principles (SOLID, clean architecture, and similar). Here, separation of concerns
is taught only at the level of *project structure* — where files live — not at the level of code
design within those files.

---

## 26. Internal Mechanics: What Happens When a Python Project Runs?

```text
Developer
   |
Project directory
   |
Python interpreter
   |
Virtual environment
   |
Installed dependencies
   |
Application source code
   |
Configuration
   |
Runtime
```

- **Developer** — the person working within the project directory (Section 2).
- **Project directory** — the organized structure this entire lesson has taught (Sections 5–13,
  Section 22).
- **Python interpreter** — the program that will actually execute the code
  (`06-virtual-environments.md`, Section 3).
- **Virtual environment** — the isolated environment (Section 12) providing that interpreter and its
  installed packages.
- **Installed dependencies** — what the package manager (Section 13) placed into that environment,
  based on `pyproject.toml`'s declarations (Section 17).
- **Application source code** — the project's own logic (Section 6), now running using the
  interpreter and dependencies above.
- **Configuration** — values (Section 9) the running application reads to adjust its behavior for
  this specific situation.
- **Runtime** — the application actually executing, doing whatever it was built to do.

### The connection to earlier lessons

This chain is not a new concept — it is the **combination** of `06-virtual-environments.md`, Section
7's environment pipeline and `07-package-managers.md`, Section 6's package-manager mental model, now
anchored at its starting point in the project's own organized directory structure (this lesson's
subject). Nothing above requires new mechanics beyond what those two lessons already established;
this section exists to show precisely *where* project structure fits into that already-familiar
pipeline.

---

## 27. Project Structure and the Operating System

This connects back to Module 0.2 and Module 0.3, without repeating either.

### What a project structure ultimately consists of

- **Directories** — the folders (Module 0.2) organizing a project's files.
- **Files** — the actual project content (Module 0.2).
- **Paths** — the specific locations of those files and directories, whether relative or absolute
  (Module 0.3; `01-vscode-and-terminal.md`, Section 6).
- **Permissions** — the access rules (Module 0.3) governing who/what can read, write, or execute a
  given file.
- **Processes** — the running instances (Module 0.2; `05-debugger.md`, Section 5) that actually read
  and execute a project's source code.
- **Environment variables** — configuration values (Module 0.2; Section 9) inherited by whatever
  process runs the project.

### How the shell navigates the project

Exactly as taught in Module 0.3 and reinforced throughout Module 0.4
(`01-vscode-and-terminal.md`, Section 6): a shell session has a current working directory, and
commands run within a project (activating its environment, running its tests, executing its source
code) depend on that working directory correctly corresponding to the project's own structure.

**Scope note:** this lesson does not repeat the Command Line course — this section exists only to make
explicit that a "project structure," at its foundation, is nothing more than an organized arrangement
of the exact same OS-level directories, files, and paths already covered in Module 0.2 and Module
0.3, with no new underlying mechanism introduced.

---

## 28. Project Structure and IDEs

This connects to `01-vscode-and-terminal.md` and `02-ide-concepts.md` without re-teaching either.

### How IDE/editor tooling discovers project components

- **Project root** — an IDE typically identifies a project's root the same way it was taught to in
  `01-vscode-and-terminal.md`, Section 2 and `02-ide-concepts.md`, Section 9: whichever folder was
  opened as the workspace.
- **Source files** — located via the project's actual structure (Section 6) — a `src/` layout
  (Section 20) versus a simple layout can affect exactly how an IDE's project-awareness features
  (`02-ide-concepts.md`, Section 9) present and search the project.
- **Tests** — an IDE's testing integration (previewed conceptually in `02-ide-concepts.md`, Section 4)
  depends on being able to locate a clearly separated tests directory (Section 7).
- **Interpreter** — directly `06-virtual-environments.md`, Section 13: the IDE's interpreter selection
  needs to correctly identify the project's own virtual environment (Section 12).
- **Virtual environment** — located, by convention, at a predictable path (commonly `.venv/`,
  `06-virtual-environments.md`, Section 9) relative to the project root.
- **Configuration** — an IDE, or the tools it integrates (`03-extensions.md`, Section 5), can read
  `pyproject.toml` (Section 18) directly, benefiting from its centralized, standardized location.
- **Tooling configuration** — formatter/linter settings (`04-formatters-and-linters.md`, Section 13)
  are far easier for an IDE's integrated tools to discover when they live in a predictable, standard
  location such as `pyproject.toml`, rather than being scattered arbitrarily.

### Why a well-structured project improves developer experience

Every one of these IDE capabilities depends on being able to reliably *find* the relevant piece of the
project — a direct, practical consequence of the discoverability principle from Section 3, now
specifically at the level of tooling rather than only human readability.

**Scope note:** this lesson does not reteach VS Code or IDE concepts — those are the dedicated subjects
of `01-vscode-and-terminal.md` and `02-ide-concepts.md`. This section only connects this lesson's own
subject (project structure) to capabilities those earlier lessons already established.

---

## 29. Common Project-Structure Failure Modes

Each entry: symptom, likely cause, corrective direction.

1. **Source code placed in random directories.**
   *Symptom:* application logic is scattered with no consistent location. *Cause:* no deliberate
   structure was ever established (Section 4). *Correction:* consolidate source code into one clearly
   identified location (Section 6, Section 20).

2. **Tests difficult to locate.**
   *Symptom:* it is unclear what, if anything, is actually tested. *Cause:* tests were never separated
   from application code (Section 7). *Correction:* establish a dedicated `tests/` directory.

3. **Configuration mixed with application logic.**
   *Symptom:* changing a setting requires editing source code directly. *Cause:* configuration
   (Section 9) was never separated out. *Correction:* extract configuration into its own clearly
   identified location.

4. **Generated files committed accidentally.**
   *Symptom:* version control contains large, frequently changing output files. *Cause:* generated
   artifacts (Section 10) were never excluded via `.gitignore` (Section 11). *Correction:* add the
   relevant patterns to `.gitignore`.

5. **`.venv` committed.**
   *Symptom:* version control contains a large, machine-specific environment directory. *Cause:*
   `.venv` (Section 12) was never added to `.gitignore`. *Correction:* add `.venv/` to `.gitignore`;
   the environment can be recreated (`06-virtual-environments.md`, Section 16) rather than tracked.

6. **Secrets committed.**
   *Symptom:* a credential or key appears inside version-controlled files. *Cause:* Section 9's
   "secrets should not be committed" principle was not followed. *Correction:* remove the secret and
   ensure the relevant file is excluded via `.gitignore` going forward (Section 31 expands this risk
   further).

7. **Wrong working directory.**
   *Symptom:* commands fail or behave unexpectedly. *Cause:* directly `01-vscode-and-terminal.md`,
   Section 6/Section 10, now specifically in the context of a structured project — the shell's current
   working directory does not match the project root. *Correction:* confirm and correct the working
   directory before running project commands.

8. **Duplicate configuration.**
   *Symptom:* the same setting appears, possibly inconsistently, in more than one place. *Cause:* no
   single, centralized configuration location was established (Section 18's "one centralized
   location" principle was not followed). *Correction:* consolidate configuration into one authoritative
   location.

9. **Confusing project root.**
   *Symptom:* it is unclear which directory is actually "the project" — for example, when a project is
   nested inside several unrelated parent folders. *Cause:* the project root was never clearly
   established or communicated. *Correction:* clearly identify and document the actual project root
   (Section 27).

10. **Inconsistent naming.**
    *Symptom:* similar things are named differently across the project (directly echoing Section 4's
    `model.py` vs. `model-final-final-v2.py` example). *Cause:* no naming convention was established
    or followed. *Correction:* adopt and consistently apply a clear naming convention.

11. **Data mixed with source code.**
    *Symptom:* datasets (Section 10) sit directly alongside application logic (Section 6) with no
    distinction. *Cause:* Section 22's `data/` separation was never applied. *Correction:* move data
    into its own clearly identified location.

12. **Model artifacts mixed with application source.**
    *Symptom:* large model files (Section 10) sit directly among source code files. *Cause:* Section
    22's `models/` separation was never applied. *Correction:* move model artifacts into their own
    location, separate from `src/`.

13. **Notebooks becoming the only source of truth.**
    *Symptom:* the actual, current application logic exists only inside exploratory notebooks, with no
    corresponding maintained source code. *Cause:* Section 25's separation-of-concerns principle
    (application logic vs. exploratory work) was never applied. *Correction:* extract the logic that
    is actually meant to be production application behavior into `src/`, keeping notebooks for
    exploration only.

14. **Scripts duplicating application logic.**
    *Symptom:* the same logic exists, copy-pasted with small variations, in both `scripts/` and
    `src/`. *Cause:* no clear boundary was maintained between "standalone helper scripts" (Section 22)
    and "the actual application" (Section 6). *Correction:* have scripts call into the shared
    application logic in `src/`, rather than duplicating it.

---

## 30. Systematic Troubleshooting Workflow

```text
1. Identify the project root
2. Inspect directory structure
3. Identify the source directory
4. Identify configuration
5. Identify tests
6. Identify environment
7. Identify dependencies
8. Identify generated artifacts
9. Identify the runtime entry point
10. Determine which component is misplaced or missing
11. Form a hypothesis
12. Make the smallest correction
13. Verify the project still works
14. Document the structural decision
```

This workflow directly extends the evidence-based methodology already established in
`05-debugger.md` (Section 2, Section 17), `06-virtual-environments.md` (Section 27), and
`07-package-managers.md` (Section 26) — now applied specifically to project-structure problems
(Section 29).

- Steps 1–9 systematically establish exactly where each component of Section 6's mental model
  (Section 26) actually lives in this specific project — gathering evidence rather than assuming.
- Step 10 pinpoints the actual discrepancy — directly echoing `05-debugger.md`, Section 2's
  symptom-vs-root-cause distinction, now applied to structure rather than to code behavior.
- Steps 11–12 apply a targeted, minimal fix — consistent with `05-debugger.md`, Section 17's "make the
  smallest appropriate fix" principle.
- Step 13 verifies rather than assumes the fix worked (the same discipline emphasized throughout
  Module 0.4).
- Step 14 closes the loop by recording *why* the structure now looks the way it does — directly
  supporting Section 3's collaboration and maintainability goals for whoever encounters this project
  next.

---

## 31. Security Considerations

### Risks associated with poor project organization

- **Accidentally committed secrets** — directly Section 29, Failure 6: a credential mixed into the
  project with no clear separation (Section 9) is at real risk of ending up in version control.
- **Exposed local configuration** — configuration meant only for one developer's own machine, if not
  clearly separated (Section 9), can be inadvertently shared as if it were the project's general
  configuration.
- **Committed credentials** — the same risk as above, specifically for authentication-related secrets.
- **Untrusted generated files** — generated artifacts (Section 10) from an unreviewed or unexpected
  source should not be blindly trusted as safe to use or share.
- **Unsafe scripts** — a `scripts/` directory (Section 22) containing scripts that perform sensitive
  or destructive actions deserves the same careful review as any other code.
- **Dependency configuration mistakes** — directly `07-package-managers.md`, Section 27: a
  `pyproject.toml` (Section 17) declaring an unreviewed or untrusted dependency introduces the same
  supply-chain risk already established in that lesson.

### Safe principles

- **Never commit real credentials** — restated directly from Section 9, and enforced structurally via
  `.gitignore` (Section 11).
- **Separate secrets from source** — keep sensitive configuration in a location clearly distinguished
  from, and excluded from, the project's tracked source code.
- **Use `.gitignore` appropriately** — proactively exclude generated artifacts, environments, and
  local/sensitive configuration (Section 11), rather than relying on remembering not to commit them
  manually.
- **Avoid unnecessary privileges** — directly `07-package-managers.md`, Section 27: routine project
  work should not require elevated system access.
- **Treat third-party dependencies as untrusted input from a supply-chain perspective** — directly
  restating `07-package-managers.md`, Section 27's core principle: a dependency declared in
  `pyproject.toml` is code you did not write, running with the same access as any other code you run.

**Scope note:** this lesson does not teach advanced security engineering — only the foundational,
structural practices (clear separation, `.gitignore` discipline) that directly reduce the everyday
risks described above.

---

## 32. Project Structure Trade-offs

| Trade-off | One side | The other side |
|---|---|---|
| **Simple vs. complex structures** | Fewer directories, less to navigate for a small project | More structure supports larger, more complex projects (Section 21) |
| **Flat vs. nested layouts** | Easier to see everything at once for a small project | Nesting groups related things together as a project grows |
| **`src/` layout vs. simple layout** | `src/` gives a clean, unambiguous separation (Section 20) | Simple layout is faster to navigate for a genuinely small project |
| **Central configuration vs. scattered configuration** | `pyproject.toml` (Section 18) as one shared source of truth | Scattered, tool-specific configuration can sometimes offer more per-tool flexibility |
| **Notebooks vs. source code** | Notebooks are fast for exploration (Section 22) | Source code (`src/`) is what should be maintained and trusted as the actual application (Section 25) |
| **Local artifacts vs. external artifact storage** | Keeping artifacts (Section 10) locally is simple for a small project | Large datasets/models are often better kept in dedicated external storage, referenced rather than committed (Section 10, Section 22) |
| **Convenience vs. maintainability** | A quick, unstructured approach is faster in the very short term | A deliberately organized structure (Sections 2–28) pays off as the project grows (Section 3) |

**No universal winner is declared for any row above.** As in Section 20 and Section 21, the right
balance depends on the specific project's actual size, purpose, and expected future — this lesson does
not prescribe one universal structure.

---

## 33. Common Misconceptions

1. **"There is one official Python project structure."**
   Incorrect — directly Section 20/Section 21: several legitimate layouts exist, and the right choice
   depends on the specific project.

2. **"`src/` is mandatory."**
   Incorrect — directly Section 6/Section 20: `src/` is a common, widely used convention, not a
   technical requirement every project must follow.

3. **"`pyproject.toml` is the application."**
   Incorrect — directly Section 14: it is metadata/configuration describing the project; the
   application is the actual running source code (Section 6).

4. **"`pyproject.toml` replaces Python."**
   Incorrect — directly Section 14: it is not executable Python code at all; it is a structured
   configuration file that tools and package managers read.

5. **"The virtual environment is the project."**
   Incorrect — directly Section 12: `.venv` is regenerable infrastructure used to *run* the project;
   the source code is the project itself.

6. **"Everything generated by the application belongs in Git."**
   Incorrect — directly Section 10/Section 11: many generated artifacts are regenerable and are
   commonly excluded via `.gitignore`.

7. **"All datasets belong inside the repository."**
   Incorrect — directly Section 10/Section 22: datasets, especially large ones, are frequently kept
   in dedicated external storage rather than committed directly.

8. **"All model checkpoints belong inside the repository."**
   Incorrect — for the same reason as above, directly Section 22: model artifacts are commonly large
   and are often stored externally rather than committed.

9. **"Notebooks should always contain the production logic."**
   Incorrect — directly Section 25/Section 29, Failure 13: notebooks are well suited to exploration,
   not to serving as a project's only maintained source of production behavior.

10. **"A larger folder structure means better engineering."**
    Incorrect — directly Section 21's guiding principle: the *right amount* of structure for a
    project's actual needs is the goal, not simply *more* structure.

11. **"More directories automatically mean better architecture."**
    Incorrect, for the same reason as above — structure should reflect genuine separation of concerns
    (Section 25), not be added for its own sake.

12. **"The README is the project structure."**
    Incorrect — directly Section 8/Section 19: the README is one piece of documentation *within* the
    project's structure, not the structure itself.

13. **"The IDE creates the architecture for you."**
    Incorrect — directly Section 28: an IDE can *discover and work with* a project's existing
    structure, and can scaffold some starting files, but the actual organizational decisions (Section
    21) remain the developer's own engineering judgment, not something the IDE decides on its own.

---

## 34. Practical Exercises

All exercises use disposable, local practice directories and require no external credentials, paid
services, cloud infrastructure, or production data anywhere in this section. All instructions remain
inside this file — no additional files are permanently created inside this learning repository as
part of these exercises.

### Level 1 — Conceptual

1. In your own words, define "project" and explain how it differs from a single source file (Section
   2).
2. Define "source code" and explain why it is typically kept separate from tests (Section 6, Section
   7).
3. Define "configuration" and explain how it differs from application code (Section 9).
4. Define "documentation" and describe the three levels introduced in Section 8.
5. Define "generated artifact" and give an AI-specific example (Section 10).
6. Explain what `.venv` is and why it is generally excluded from version control (Section 11, Section
   12).
7. Explain what `.gitignore` does, and explicitly state what it does *not* do (Section 11).
8. Explain what `pyproject.toml` is, and state one thing it is commonly mistaken for (Section 14).
9. Define "project root" and explain why it matters (Section 27, Section 28).

### Level 2 — Hands-On

Use a disposable local directory for all steps below; nothing here needs to be created inside this
learning repository.

1. Create a disposable practice project directory containing a simple structure similar to Section 5's
   example (`src/`, `tests/`, `README.md`).
2. From within it, confirm the current working directory using the techniques from
   `01-vscode-and-terminal.md`, Section 6 — this is your project root.
3. Create one small placeholder source file inside `src/`, and one small placeholder test file inside
   `tests/`, and explain in your own words why they are kept apart (Section 7).
4. Create a `docs/` directory and place a short note inside it, distinguishing it from your top-level
   `README.md` (Section 8).
5. Identify (in your notes) which files in your practice project are configuration, and which are
   application source code (Section 9).
6. Create a small, disposable "generated" file (for example, a placeholder output file) and identify,
   in your own words, why it should not be treated the same as your source code (Section 10).
7. Create a `.gitignore` file listing at least `.venv/` and your placeholder generated file from step
   6 (Section 11).
8. Write a minimal, illustrative `pyproject.toml` for this disposable project, following Section 16's
   example structure (using a fictional package name and description — no real dependency required).
9. Using `06-virtual-environments.md`'s techniques, create a `.venv` for this practice project, and
   confirm (`06-virtual-environments.md`, Section 25) it does not interfere with your source files.

### Level 3 — Reasoning

1. A small, one-file script with no tests and no dependencies is being planned. Would you recommend a
   `src/` layout or a simple layout (Section 20, Section 21)? Justify your answer.
2. A project's configuration values are currently hardcoded directly inside its main source file.
   Where should they move, and why (Section 9, Section 25)?
3. A file named `output_2024.csv` currently sits in the project root, produced by running the project's
   own script. Is this source code or a generated artifact (Section 10)? How would you confirm?
4. A project processes a 20 GB dataset. Should this dataset be committed directly into the project's
   version control? Justify your reasoning (Section 10, Section 22, Section 33).
5. You inherit a project where `random.py`, `model.py`, and `model_v2_final.py` all coexist with no
   clear indication of which is current. What structural problems does this reveal (Section 4, Section
   29, Failure 10)?
6. Where should a project's tests live relative to its source code, and why does this placement matter
   for both humans and tooling (Section 7, Section 28)?
7. A teammate suggests ignoring `.venv/` in `.gitignore` "just to be safe, in case someone needs it."
   Evaluate this reasoning against Section 12's explanation of why `.venv` is regenerable.
8. An AI project has both a `notebooks/` directory and a `src/application/` directory containing
   very similar logic. What does this suggest about the project's current state, and what corrective
   action would you recommend (Section 25, Section 29, Failure 13)?
9. Decide where AI evaluation artifacts (Section 10, Section 22) should live in a project structure,
   and justify your placement relative to `models/` and `src/`.

### Level 4 — Debugging

Each provides a scenario, symptoms, and an investigation goal. Reason through each using Section 30's
workflow before concluding.

1. **Scenario:** A developer runs their project's tests and nothing is found to run.
   **Symptoms:** the test tool reports zero tests discovered. **Investigation goal:** determine
   whether the tests directory is missing, misplaced, or simply not where the test tool expects to
   look (Section 7, Section 28).

2. **Scenario:** A newcomer to a project cannot find the main application entry point.
   **Symptoms:** several similarly named files exist at the project root with no clear indication of
   which one actually starts the application. **Investigation goal:** identify the actual runtime
   entry point (Section 26, step 9) and determine what structural clarity is missing (Section 29,
   Failure 10).

3. **Scenario:** A project's `.gitignore` exists, but a large generated file still appears in version
   control.
   **Symptoms:** the file matches a pattern that looks like it should be ignored. **Investigation
   goal:** determine whether the file was already tracked *before* the `.gitignore` rule was added
   (Section 11's "does not delete files" boundary is a relevant clue here).

4. **Scenario:** A project's configuration values differ unexpectedly between two developers' machines.
   **Symptoms:** the same source code behaves differently for each person. **Investigation goal:**
   determine whether local, machine-specific configuration (Section 9) is being conflated with shared
   project configuration.

5. **Scenario:** A project fails to run when launched from a parent directory, but works when launched
   from inside the project folder itself.
   **Symptoms:** file-not-found-style errors. **Investigation goal:** determine whether the working
   directory (Section 27; `01-vscode-and-terminal.md`, Section 6) matches the project root the code
   assumes.

6. **Scenario:** An AI project's `models/` directory has grown to occupy most of the repository's size.
   **Symptoms:** cloning or working with the repository has become slow and unwieldy. **Investigation
   goal:** determine whether these model artifacts (Section 10, Section 22) should instead be tracked
   via external storage.

7. **Scenario:** Two configuration files in the same project specify conflicting values for the same
   setting.
   **Symptoms:** the application's actual behavior is inconsistent or unpredictable. **Investigation
   goal:** identify both configuration sources and determine which one, per Section 18's "centralized
   location" principle, should be treated as authoritative.

8. **Scenario:** A `scripts/` directory contains a script that appears to duplicate logic already
   present in `src/`.
   **Symptoms:** a bug fixed in `src/` does not seem to affect behavior when the script is run
   separately. **Investigation goal:** confirm whether the script is calling into the shared
   application logic or has its own separate, duplicated copy (Section 29, Failure 14).

### Level 5 — Applied AI Engineering

All examples are local, conceptual, and require no API keys, paid services, cloud infrastructure, or
production credentials.

1. Design a basic conceptual structure for a small local LLM application (no real API key required),
   deciding where prompt-construction logic, configuration, and any example outputs would live
   (Section 22).
2. Organize a conceptual RAG project's structure, explicitly deciding where source code, retrieval
   configuration, and any local sample documents would live (Section 22, Section 25).
3. For a conceptual model/evaluation setup, decide where model artifacts and evaluation results should
   live relative to each other and to source code, and justify the separation (Section 22, Section
   23).
4. Given a project that currently has its application logic only inside a notebook, describe how you
   would restructure it to separate exploratory work from maintained application source (Section 25,
   Section 29, Failure 13).
5. Design a structure for a small conceptual AI API service, explicitly deciding what belongs in Git
   versus what should be treated as external/generated (datasets, model checkpoints, logs — Section
   10, Section 33).

---

## 35. Structured Debugging Exercise

### "Why Does My Python Project Work From One Directory but Fail From Another?"

**Scenario.** A learner has a small, disposable practice project with a `src/` layout (Section 20): a
`src/app/` package containing the application's source code, a `tests/` directory, a `pyproject.toml`,
and a `.venv`. Running the application from inside the project's root directory works correctly. Later,
the learner navigates into a subdirectory *inside* the project (for example, `src/app/`) and tries to
run the same command from there — it fails, reporting that a file or module cannot be found.

**The learner's task, following this exact loop:**

1. **Reproduce the problem** — confirm the command fails consistently when run from inside `src/app/`,
   and succeeds consistently when run from the project root.
2. **Identify expected behavior** — the application should run the same way regardless of which
   directory it happens to be launched from, as long as the correct command and interpreter are used.
3. **Identify the project root** — determine, explicitly, which directory is actually the project's
   root (Section 27, Section 30).
4. **Inspect the current working directory** — using `01-vscode-and-terminal.md`, Section 6's
   techniques, confirm exactly which directory the shell is currently in when the command fails.
5. **Inspect the project structure** — confirm where the relevant source files, and any
   relatively-referenced configuration or data files, actually live relative to the project root
   (Section 6, Section 26).
6. **Identify the Python interpreter/environment** — using `06-virtual-environments.md`, Section 25's
   techniques, confirm that the same `.venv` interpreter is being used in both cases (ruling out an
   interpreter mismatch, `06-virtual-environments.md`, Section 13, as a competing explanation).
7. **Inspect relevant configuration** — check whether the application, or its configuration, relies on
   any relative paths (Section 9; `01-vscode-and-terminal.md`, Section 6) that assume a specific
   working directory.
8. **Form a hypothesis** — based on steps 3–7, state a specific, testable guess: for example, "the
   application (or a file it reads) uses a relative path that only resolves correctly when the current
   working directory is the project root."
9. **Test the hypothesis** — deliberately run the command from the project root again, and from
   `src/app/` again, explicitly comparing the current working directory (step 4) against what the
   relative path in question assumes.
10. **Fix the root cause** — either run the command consistently from the correct working directory
    (the project root), or, where appropriate, adjust the reliance on a relative path so it does not
    depend on which directory the command happens to be launched from.
11. **Verify the project** — confirm the application now runs correctly and consistently, regardless of
    which directory within the project it is launched from (or, if the fix is "always run from the
    project root," confirm that constraint is now clearly understood and followed).
12. **Explain why the structure/path caused the failure** — in your own words, state precisely why a
    correct project structure (Section 5, Section 20) does not, by itself, prevent a working-directory-
    dependent failure — the structure defines *where things live*; the working directory determines
    *how relative references to those things resolve* (directly connecting Section 26's "runtime"
    step back to Section 27's operating-system-level path concepts).
13. **Explain how to prevent recurrence** — describe what habit (explicitly confirming the working
    directory before running project commands, `01-vscode-and-terminal.md`, Section 6) would have
    caught this mismatch immediately.

**Scope note:** this exercise deliberately does not teach advanced Python import-system internals
(Section 4's scope boundary) — the actual mechanism explored here is the same working-directory
concept already fully established in `01-vscode-and-terminal.md`, Section 6, now applied specifically
to a structured, multi-directory project rather than a single flat folder.

---

## 36. Mini-Project

### Python Project Structure Design Lab

Design a small, disposable Python project structure for a hypothetical AI application. All work stays
local and conceptual — no API keys, paid services, cloud infrastructure, or production data are
required anywhere in this project, and no files are permanently created inside this learning
repository.

### Requirements

Decide where each of the following would live in your designed structure:

- source code,
- tests,
- configuration,
- documentation,
- scripts,
- notebooks,
- datasets,
- model artifacts,
- evaluation results,
- virtual environment,
- project metadata (`pyproject.toml`).

### Learner tasks

1. **Identify the project root** — state clearly what the top-level directory of your hypothetical
   project is (Section 27).
2. **Design a reasonable directory structure** — sketch out a full directory tree (similar in spirit
   to Section 22's example), sized appropriately for a small hypothetical AI project (Section 21's
   "simplest structure that provides necessary separation" principle).
3. **Explain every directory** — for each directory in your design, write one sentence stating its
   purpose, directly grounded in the corresponding section of this lesson (Sections 6–13, Section 22).
4. **Create a conceptual/minimal `pyproject.toml`** — following Section 16's example structure, using
   a fictional name, version, description, and at most one or two fictional/placeholder dependencies
   — explicitly not claiming these are real, recommended packages.
5. **Explain how the package manager relates to the project** — in your own words, describe how `pip`
   or `uv` (`07-package-managers.md`) would use your `pyproject.toml` to populate your project's
   environment (Section 13, Section 17).
6. **Explain how the virtual environment relates to the project** — in your own words, describe why
   your design's `.venv` is regenerable infrastructure rather than part of the project's actual source
   (Section 12).
7. **Identify files that should not be committed** — list, explicitly, which parts of your design
   belong in `.gitignore` (Section 11) and why.
8. **Identify generated artifacts** — explicitly list which parts of your design are generated
   (Section 10) rather than authored directly, and reason about whether each should live inside the
   repository or in external storage (Section 22, Section 33).
9. **Identify security-sensitive files** — explicitly identify where secrets/credentials would live in
   your design, and confirm they are kept separate from, and excluded from, your source code (Section
   9, Section 31).
10. **Intentionally introduce one structural mistake** — deliberately violate one of your own design's
    principles (for example, place a dataset directly inside `src/`, echoing Section 29, Failure 11).
11. **Diagnose the mistake** — using Section 30's systematic troubleshooting workflow, identify exactly
    what is wrong with the deliberately introduced mistake and why.
12. **Correct it** — restore your design to follow its own stated principles.
13. **Explain the engineering reasoning** — in your own words, summarize why the corrected structure is
    better than the mistaken one, referencing the specific principle(s) from this lesson (Section 3,
    Section 21, Section 25) that justify the correction.

### Emphasis

This mini-project is deliberately design-oriented rather than purely hands-on with real files — its
purpose is to practice the **engineering reasoning** behind project structure (Section 21's "why" over
Section 5's "what"), applying it specifically to the AI-project context introduced in Section 22 and
Section 23.

---

## 37. Review

- **Project** — a directory (and everything inside it) treated as one coherent unit of work (Section
  2).
- **Project root** — the top-level directory identifying where a specific project begins (Section 27,
  Section 30).
- **Source code** — the human-written code defining application behavior, conventionally kept in
  `src/` or at the project root (Section 6, Section 20).
- **Tests** — code that verifies application behavior, kept separate from application code (Section
  7).
- **Documentation** — README, `docs/`, and source-code comments/docstrings, each serving a different
  level of detail (Section 8).
- **Configuration** — values controlling application behavior, kept separate from code, with secrets
  kept especially carefully separate (Section 9).
- **Generated artifacts** — regenerable output (logs, model checkpoints, evaluation results), commonly
  excluded from version control (Section 10).
- **`.gitignore`** — a list of patterns telling Git what not to track; does not delete files (Section
  11).
- **`.venv`** — the project's disposable, regenerable local environment (`06-virtual-environments.md`;
  Section 12).
- **Package manager** — the tool (`pip`/`uv`) that installs a project's declared dependencies
  (`07-package-managers.md`; Section 13).
- **`pyproject.toml`** — standardized project metadata/configuration; not code, not an environment, not
  a package manager, not a dependency (Sections 14–18).
- **Project layout** — the physical organization choice (simple vs. `src/`, and others), chosen based
  on the project's actual needs (Section 20, Section 21).
- **AI project structure** — the same general principles applied to AI-specific concerns: data,
  models, evaluations, notebooks (Section 22, Section 23).
- **Separation of concerns** — keeping genuinely different kinds of content in genuinely separate
  places, reducing confusion and change risk (Section 25).
- **Reproducibility** — supported, but not automatically guaranteed, by good structure combined with
  declared dependencies and clear separation (Section 23; `06-virtual-environments.md`, Section 28;
  `07-package-managers.md`, Section 22).

---

## 38. Self-Assessment

- [ ] I can explain what project structure is and why it matters.
- [ ] I can identify the difference between source code, tests, configuration, documentation, and
  generated artifacts in a real project.
- [ ] I can design a basic project structure appropriate for a small project's actual needs.
- [ ] I can distinguish a simple layout from a `src/` layout, and justify choosing one over the other.
- [ ] I can explain what `pyproject.toml` is, and clearly state what it is not.
- [ ] I can identify what belongs in `.gitignore` for a given project and explain why.
- [ ] I can explain why `.venv` should generally not be committed to version control.
- [ ] I can troubleshoot a project that behaves differently depending on the current working
  directory.
- [ ] I can distinguish generated artifacts from source code in an AI project.
- [ ] I can justify where model artifacts, datasets, and evaluation results should live relative to
  source code.
- [ ] I can identify structural problems in a disorganized project and propose a correction.
- [ ] I can apply these concepts to design a structure for a hypothetical AI application.

---

## 39. Interview Questions

**Q: What is project structure, and why does it matter?**
A: The deliberate organization of a project's files and directories; it directly affects readability,
maintainability, collaboration, tooling, and how easily the project can grow (Section 3).

**Q: What is the difference between a simple layout and a `src/` layout?**
A: A simple layout keeps source code at the project root; a `src/` layout places it inside a dedicated
subdirectory, giving a clearer separation from other project content — neither is universally correct
(Section 20).

**Q: Where should tests live, and why?**
A: In their own dedicated directory (conventionally `tests/`), separate from application code, so it
is always clear what is being tested versus what does the testing (Section 7).

**Q: What is a project root?**
A: The top-level directory that identifies where a specific project begins, which shells, IDEs, and
tools all rely on to correctly locate the project's other components (Section 27, Section 28).

**Q: What is `pyproject.toml`?**
A: A standardized Python project configuration/metadata file — not executable code, not an
environment, and not a package manager — used to declare a project's identity, dependencies, and tool
configuration (Section 14).

**Q: What is the relationship between `pyproject.toml` and dependency installation?**
A: `pyproject.toml` declares what a project needs; a package manager (`pip`/`uv`) reads that
declaration and installs the actual dependencies into the project's virtual environment (Section 17).

**Q: Why should `.venv` generally not be committed to version control?**
A: Because it is large, machine-specific, and entirely regenerable from the project's own declared
dependencies — none of the properties that justify tracking something in version control (Section
12).

**Q: What does `.gitignore` actually do?**
A: It tells Git which files/patterns not to track; it does not delete files from disk, and it does not
retroactively remove files that were already tracked before the rule was added (Section 11).

**Q: Why is dependency declaration important for reproducibility?**
A: Because it gives a project a maintained, standard record of exactly what it needs, allowing its
environment to be reliably recreated later or on a different machine, rather than depending on
whatever happens to already be installed (Section 17, connecting to `07-package-managers.md`, Section
22).

**Q: How should an AI project organize datasets, models, and evaluation results?**
A: Generally in their own clearly separated directories (for example, `data/`, `models/`,
`evaluations/`), distinct from application source code — with large datasets and model checkpoints
often stored externally rather than committed directly to version control (Section 22, Section 33).

**Q: Why can the same project fail from one directory but succeed from another?**
A: Because relative paths and working-directory assumptions can cause commands to resolve differently
depending on where they are actually launched from — a good project structure defines where things
live, but does not by itself remove the need to run commands from the correct working directory
(Section 35).

---

## 40. Architecture / Engineering Questions

**Q: How would you structure a Python project expected to grow significantly?**
A: Favor a `src/` layout (Section 20) with clearly separated tests, configuration, and documentation
(Sections 7–9) from the outset, since a structure that already anticipates growth is easier to extend
than one that must be retrofitted later (Section 21).

**Q: When would you choose a flat layout versus a `src/` layout?**
A: A flat layout for a genuinely small, unlikely-to-grow script; a `src/` layout when the project is
expected to grow, be packaged/distributed, or needs an unambiguous separation between source and
everything else (Section 20, Section 21).

**Q: Where should tests live and why?**
A: In a dedicated `tests/` directory, separate from application code, so both humans and testing
tooling can unambiguously identify what constitutes the test suite (Section 7, Section 28).

**Q: Where should model checkpoints live?**
A: Generally in their own dedicated location (for example, `models/`), separate from `src/`, and
frequently stored externally rather than committed directly given their typical size (Section 10,
Section 22, Section 33).

**Q: How would you structure an AI application containing source code, data, evaluations, and
notebooks?**
A: With each kept in its own clearly separated directory (`src/`, `data/`, `evaluations/`,
`notebooks/`), applying separation of concerns (Section 25) so exploratory work never becomes
conflated with maintained application logic, and so data/evaluation artifacts never become mixed with
source code (Section 22, Section 23).

**Q: What belongs in `pyproject.toml`?**
A: Project metadata (name, version, description), the supported Python version range, declared
dependencies, and centralized tool configuration — not application logic, not secrets, and not the
environment itself (Section 16, Section 18).

**Q: What should remain outside the Git repository?**
A: The virtual environment, generated artifacts, secrets/credentials, and — commonly — large datasets
and model checkpoints, all enforced via `.gitignore` (Section 11, Section 22, Section 31).

**Q: How does project structure affect deployment?**
A: A clearly organized project (identified source, declared dependencies, separated configuration)
is far easier to package and run somewhere else reliably than one where those elements are tangled
together (Section 24).

**Q: How does project structure affect reproducibility?**
A: Good structure, combined with declared dependencies (`pyproject.toml`) and a clear separation
between source, configuration, and generated output, makes it possible to know exactly what produced a
given result and to recreate that result later — though structure alone does not guarantee this
completely (Section 23).

---

## 41. Production Application

```text
Organized Project Structure
              |
   Clear Source / Test / Config Boundaries
              |
    Declared Dependencies (pyproject.toml)
              |
   Reproducible, Deployable Project
              |
     Production Python/AI System
```

Project structure is applied to production Python and AI systems through:

- **Clear source boundaries** — knowing exactly what constitutes "the application" (Section 6), a
  prerequisite for packaging it for deployment.
- **Test organization** — a dedicated `tests/` directory (Section 7) that a production pipeline can
  run automatically before allowing a change to proceed (a forward reference to CI/CD, Section 24).
- **Configuration separation** — environment-specific configuration (Section 9) that can differ
  between development and production without requiring code changes.
- **Environment separation** — the same isolation principle from `06-virtual-environments.md`,
  extended across development, testing, and production contexts (Section 24).
- **Dependency metadata** — `pyproject.toml`'s declared dependencies (Section 17), the basis for
  reliably recreating the exact environment a production deployment needs.
- **Documentation** — Section 8's levels, supporting anyone who later needs to understand or maintain
  the system in production.
- **Generated artifacts** — Section 10's distinction, critical in production for knowing what must be
  produced fresh versus what is part of the deployed system itself.
- **Model artifacts** — Section 22's `models/` separation, directly relevant to how a production AI
  system manages and updates its deployed model.
- **Evaluation artifacts** — Section 23's reproducibility connection, relevant to tracking how a
  production system's quality is measured over time.
- **Deployment preparation** — Section 24's foundational connection to packaging, containers, and
  CI/CD.
- **Reproducibility** — Section 23, at production stakes: being able to recreate exactly what is
  running.
- **Maintainability** — Section 3's core argument, sustained at production scale and lifespan.
- **Collaboration** — Section 3's collaboration point, especially important once a system involves a
  team responsible for its ongoing operation.

None of the deeper production mechanics (Docker, Kubernetes, CI/CD pipeline design) are taught in this
lesson (Section 48). The purpose here is only to establish that the structural discipline built
throughout this lesson is the direct foundation those later, more advanced practices are built on.

---

## 42. Applied AI Engineering Connection

This is a forward-looking preview only — none of the following systems are taught in depth here.

### Where project structure becomes important

- **LLM applications** — organizing prompt-construction logic, configuration, and any supporting
  utilities clearly (Section 22).
- **RAG systems** — separating retrieval logic, ingestion scripts, and configuration from the core
  application (Section 22, Section 25).
- **AI APIs** — clearly separating service source code, configuration, and tests, directly supporting
  later deployment (Section 24).
- **Agent systems** — keeping orchestration logic, tool definitions, and configuration organized as
  the system's complexity grows.
- **Evaluation pipelines** — separating evaluation code and its results (`evaluations/`) from the
  system being evaluated (Section 22, Section 23).
- **Model inference services** — separating model artifacts (`models/`) from the serving application
  code (`src/`).
- **Data pipelines** — separating data-processing source code from the data itself (`data/`, Section
  22).
- **Multimodal applications** — the same principles, applied across a potentially larger set of data
  types and processing stages.

### How poor structure can lead to real problems

- **Duplicated logic** — directly Section 29, Failure 14: scripts or notebooks quietly reimplementing
  what `src/` already does, drifting out of sync over time.
- **Hidden dependencies** — configuration or paths implicitly assumed rather than explicitly declared
  (Section 17), making the project fragile when moved or shared.
- **Difficult debugging** — a disorganized project makes `05-debugger.md`, Section 17's systematic
  workflow harder to apply, since relevant code and configuration are not clearly located.
- **Experiment confusion** — without clear separation (Section 23), it becomes unclear which
  configuration or code actually produced a given evaluation result.
- **Accidental artifact commits** — directly Section 29, Failure 4/5: large, regenerable files ending
  up tracked in version control.
- **Unclear configuration** — directly Section 29, Failure 8: the same setting specified inconsistently
  in more than one place.
- **Deployment problems** — directly Section 24: a project that was never clearly organized is harder
  to reliably package and deploy.
- **Reproducibility problems** — directly Section 23: without clear structure and declared
  dependencies, recreating a specific past result becomes unreliable guesswork.

---

## 43. Example AI Project Structure

```text
ai-application/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── services/
│       └── ...
├── tests/
├── configs/
├── scripts/
├── notebooks/
├── data/
├── evaluations/
├── models/
├── docs/
├── .venv/
├── .gitignore
├── pyproject.toml
└── README.md
```

- **`src/app/`** — the application's source code (Section 6), with `main.py` as its runtime entry
  point (Section 26, step 9), `config.py` handling configuration loading (Section 9), and `services/`
  grouping related functionality.
- **`tests/`, `configs/`, `scripts/`, `notebooks/`, `data/`, `evaluations/`, `models/`, `docs/`** — as
  explained in Section 22.
- **`.venv/`, `.gitignore`, `pyproject.toml`, `README.md`** — as explained in Section 5, Section 11,
  Sections 14–18, and Section 8.

### An important accuracy boundary

**This is an educational example, and NOT a mandatory universal architecture.** It exists to make
Section 22's more abstract structure concrete, with plausible file names inside `src/app/`, for the
purpose of illustration only. This lesson does not teach the individual AI framework implementations
that would actually populate `services/`, `main.py`, or any other file in this example — those are
later-stage subjects entirely outside this lesson's scope (Section 4, Section 48).

---

## 44. Relationship Map

```text
                    Python Project
                         |
          +--------------+--------------+
          v              v              v
     Source Code       Tests       Documentation
          |
          v
      Configuration
          |
          v
    pyproject.toml
          |
          v
    Package Manager
          |
          v
   Virtual Environment
          |
          v
     Dependencies
          |
          v
       Runtime
```

### Explained, in beginner-friendly language

A **Python Project** (Section 2) branches, at the top level, into three roughly parallel concerns:
its **Source Code** (Section 6, what the application actually does), its **Tests** (Section 7,
verifying that behavior), and its **Documentation** (Section 8, explaining it to humans). Following
the Source Code branch further down: the application's behavior is adjusted by **Configuration**
(Section 9); the project's overall metadata and dependency needs are declared in **`pyproject.toml`**
(Sections 14–18); a **Package Manager** (`07-package-managers.md`) reads that declaration and installs
what is needed into a **Virtual Environment** (`06-virtual-environments.md`), producing the actual
**Dependencies** available at runtime; and finally, all of this together — source code, configuration,
and installed dependencies — is what actually executes as the project's **Runtime** (Section 26).

This diagram is this lesson's single most condensed summary: every section from 2 through 28 explains
one node or one connecting arrow in this exact picture.

---

## 45. Cross-Platform Requirements

Because this lesson focuses on structure rather than command-line mastery, command examples are kept
limited and purposeful — reused directly from `01-vscode-and-terminal.md` and
`06-virtual-environments.md` rather than introduced newly here.

**Confirming the current working directory (illustrative — commands differ by platform/shell, per
`06-virtual-environments.md`, Section 25):**

- **Linux/macOS shells:** `pwd`
- **Windows PowerShell:** `Get-Location`
- **Windows CMD:** `cd` (with no arguments)
- **WSL2:** behaves as Linux/macOS, since it runs a real Linux environment
  (`01-vscode-and-terminal.md`'s prerequisites)

**Listing a directory's contents (illustrative):**

- **Linux/macOS shells:** `ls`
- **Windows PowerShell:** `Get-ChildItem` (commonly aliased as `dir`)
- **Windows CMD:** `dir`
- **WSL2:** as Linux/macOS

**Accuracy note:** as established throughout Module 0.4, this lesson does not claim any of these
commands behaves identically across every shell and platform — each is labeled to the specific
platform/shell it applies to, consistent with `01-vscode-and-terminal.md`, Section 5's terminal-vs-
shell distinction.

---

## 46. Safety Requirements

All practical work in this lesson (Section 34, Section 35, Section 36) requires no real credentials,
API keys, production data, private repositories, paid services, unnecessary administrator privileges,
or modification of the system Python. Every exercise uses disposable local practice directories, and
no exercise instructs the learner to commit secrets or sensitive data anywhere — Section 31's
principles apply throughout.

---

## 47. Accuracy Notes

Restated explicitly, consistent with every claim made throughout this lesson:

- There is no single mandatory Python project structure for every project (Section 20, Section 21).
- `src/` is a common layout, not a universal requirement (Section 6, Section 20).
- `pyproject.toml` is not Python code (Section 14).
- `pyproject.toml` is not a virtual environment (Section 14).
- `pyproject.toml` is not itself a package manager (Section 14).
- `.venv` is an environment, not the source project (Section 12).
- `.gitignore` controls which matching files Git ignores; it does not delete files (Section 11).
- Generated artifacts are not automatically source code (Section 10).
- Datasets do not automatically belong inside Git (Section 10, Section 22).
- Model checkpoints do not automatically belong inside Git (Section 22).
- Notebooks are useful but should not automatically become the only source of production logic
  (Section 25).
- More directories do not automatically mean better architecture (Section 21, Section 33).
- A clean project structure does not guarantee good software architecture (Section 25's scope
  boundary with the later Software Engineering stage).
- Project structure improves organization but does not by itself guarantee reproducibility (Section
  23).
- Exact behavior of tooling may vary by tool, version, and platform (Section 45).
- No command output, tool result, package version, or example `pyproject.toml` in this lesson is
  presented as a claim of universal correctness or genuine execution evidence.

---

## 48. Scope Boundary With Later Roadmap Stages

This lesson deliberately preserves the following boundaries.

### Stage 5 — Software Engineering

Not taught in depth here: SOLID, clean architecture, hexagonal architecture, domain-driven design,
microservices, advanced testing, advanced code quality. This lesson establishes only the foundational
relationship — that a clean project structure (Section 25) is a prerequisite that makes those later,
deeper architectural principles easier to apply, not a substitute for learning them.

### Stage 6 — Python Production Engineering

Not taught in depth here: advanced Python packaging, wheels, source distributions, dependency groups,
editable installs, package publishing, private packages, build systems, `twine`, advanced package
layout. This lesson's `pyproject.toml` coverage (Sections 14–18) is strictly foundational — sufficient
to understand its role and write a simple example, not to publish or build a distributable package.

### Stage 17+ — Containers/Deployment

Not taught here: Docker, Kubernetes, cloud deployment, production CI/CD. Section 24 establishes only
that good project structure makes those later topics easier to approach — no container or deployment
mechanics are taught in this lesson.

---

## 49. Key Takeaways

- Project structure is a deliberate engineering decision, not decoration — it directly affects
  readability, maintainability, collaboration, tooling, and how well a project scales.
- There is no single mandatory Python project structure; the right structure depends on a project's
  actual size, purpose, and expected growth.
- Source code, tests, configuration, documentation, and generated artifacts each deserve their own
  clearly separated location.
- `.venv` is regenerable local infrastructure, not the project itself, and generally should not be
  committed to version control.
- `pyproject.toml` is standardized project metadata/configuration — not Python code, not an
  environment, and not a package manager.
- Project structure, `pyproject.toml`, a package manager, and a virtual environment each play a
  distinct, complementary role — none of them substitutes for the others.
- `.gitignore` controls what Git tracks; it does not delete files or manage the project's actual
  organization.
- Good structure improves reproducibility and deployment readiness but does not, by itself, guarantee
  either completely.
- More directories or a more elaborate structure do not automatically mean better engineering — use
  the simplest structure that provides the necessary separation and maintainability.
- AI projects benefit from the same structural principles as any Python project, applied specifically
  to data, models, evaluations, and notebooks — kept clearly separate from maintained application
  source.
- Secrets and sensitive configuration must always be kept separate from, and excluded from, a
  project's committed source code.
- The structural discipline built in this lesson is the direct foundation for later software
  engineering, packaging, and production/deployment practices covered deeper elsewhere in this
  roadmap.
