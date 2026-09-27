# Dependency Upgrades and Supply-Chain Awareness

> Stage 1 — Programming & Computational Thinking  
> Module 10 — Production Habits for Python Programs

A dependency is part of your software system even though you did not write its source code.

That single idea changes how a production Python engineer thinks about packages. Installing a library is only the beginning. A mature workflow also answers:

```text
What do we depend on?
        ↓
Which versions do we allow?
        ↓
What versions were actually resolved?
        ↓
Can another machine reproduce them?
        ↓
How do we upgrade safely?
        ↓
How do we detect compatibility and security problems?
        ↓
How do we roll back?
```

The central habit in this chapter is:

> **Treat dependency management as an engineering lifecycle, not as a one-time installation task.**

This chapter uses the standard Python packaging model and a modern `uv` project workflow. Tool behavior can evolve, so always check the version of the tool and its current documentation before relying on a newly introduced command or option.

## 1. Overview

This chapter takes you from the beginner statement:

> “I just install whatever package my Python program needs.”

to the production-engineering statement:

> “I understand my dependency graph, can reproduce my environment, can upgrade dependencies systematically, can investigate conflicts, can review dependency changes, and understand the major software supply-chain risks associated with third-party dependencies.”

The scope is deliberately focused. We will study dependency declarations, version constraints, resolution, lock files, reproducible environments, `pyproject.toml`, `uv`, upgrades, rollback, dependency inventories, and supply-chain awareness.

We will not turn this into a full packaging-internals course or a full cybersecurity course. The goal is a strong Stage 1 foundation that lets you make sound engineering decisions before you move to larger systems.

## 2. Learning Objectives

By the end of the chapter you should be able to:

- explain what a dependency is and why projects use dependencies;
- distinguish the Python standard library from third-party distributions;
- distinguish a package/project name from its import name;
- identify direct and transitive dependencies;
- read a simple dependency graph;
- understand why two projects with different resolved versions may behave differently;
- read and write basic `[project]` information in `pyproject.toml`;
- use dependency version specifiers such as `>=`, `<`, `==`, and `~=`;
- explain the intended meaning of major, minor, and patch versions under Semantic Versioning;
- understand declared requirements versus concrete resolved versions;
- explain what a lock file contributes to reproducibility;
- use basic `uv` project commands;
- separate runtime, optional, and development dependencies appropriately;
- plan and test a dependency upgrade;
- review a dependency diff rather than only the top-level package change;
- reason about dependency conflicts;
- understand supply-chain risks such as typosquatting, dependency confusion, compromised packages, and vulnerable transitive dependencies;
- understand package provenance and integrity at a conceptual level;
- explain why a lock file does not eliminate all security risk;
- build a rollback plan;
- apply the workflow to data and Applied AI projects.

## 3. What Is a Dependency?

A dependency is software that your program relies on to perform some function.

For example:

```python
import requests
```

or:

```python
import pydantic
```

Your application code is one part of the system. The imported project is another part:

```text
Your application
      |
      +---- third-party dependency
```

Why use dependencies?

1. You avoid reimplementing mature functionality.
2. You can benefit from an ecosystem that has already solved common problems.
3. Your own code can stay smaller and focused on the application's domain.
4. You can use libraries that are already tested and maintained.

But there is a trade-off:

> Every dependency reduces some development effort while adding another piece of software, another version constraint, another upgrade path, and another source of operational or security risk.

A dependency is therefore not “someone else's problem.” Once your application depends on it, its behavior becomes part of the environment your application runs in.

**Key Takeaway:** A third-party package is part of your system boundary, even when its source code is outside your repository.

## 4. Why Python Programs Use Dependencies

Suppose you want to build a web client, a validation layer, or a data-processing application. You could write everything yourself, but that often creates unnecessary complexity.

Common reasons to use a dependency:

```text
Need a feature
    ↓
Check whether a suitable maintained project exists
    ↓
Evaluate it
    ↓
Add it as a dependency
```

Examples:

```text
HTTP client       → requests / httpx
Data analysis     → pandas
Data validation   → pydantic
Testing           → pytest
Linting           → ruff
```

The important production question is not only:

> “Does this package solve the problem?”

It is also:

> “Am I willing to operate this package, its dependencies, its upgrades, and its risks?”

When you add a package, you have also accepted responsibility for understanding at least:

- its version constraints;
- its place in the dependency graph;
- its maintenance status;
- compatibility with your Python versions;
- how to test upgrades;
- how to respond to a security advisory.

**Production Note:** “Small package” does not automatically mean “small operational impact.” A tiny package can still sit on a critical execution path.

## 5. Standard Library vs Third-Party Dependencies

Python ships with a large standard library. Typical examples include:

```python
import pathlib
import json
import logging
import datetime
import collections
```

You normally do not install these separately when using that Python installation.

Third-party projects are different:

```python
import requests
import pydantic
```

These distributions normally have to be installed into the environment.

Keep this mental model:

```text
Python implementation
      ↓
Standard library
      ↓
Your application
      ↑
Third-party packages (when needed)
```

A project may use both.

A strong production habit is to prefer the standard library when it already provides the needed capability and the trade-offs are acceptable. This is not a rule that “third-party is bad.” It is a reminder that every added dependency increases the system you have to maintain.

**Common Mistake:** Thinking that every import means “install this package.” `json`, `pathlib`, and `logging` are standard-library modules; they are not ordinary third-party dependencies.

## 6. Direct vs Transitive Dependencies

A **direct dependency** is a project your application explicitly declares.

```text
my-app
  └── requests
```

A **transitive dependency** is required by another dependency.

```text
my-app
  └── requests
       ├── urllib3
       ├── certifi
       ├── charset-normalizer
       └── idna
```

You might never write:

```python
import urllib3
```

and still have it installed because `requests` needs it.

This matters for three reasons:

1. **Compatibility:** your application can break when an indirect dependency changes.
2. **Security:** a vulnerability can exist in a transitive dependency.
3. **Reproducibility:** the full resolved graph must be understood, not only the top-level package list.

The mental model is:

```text
Direct
  ↓
Indirect
  ↓
Transitive
  ↓
Full runtime environment
```

**Key Takeaway:** “I don't import it directly” is not the same as “it is not part of my application environment.”

## 7. Dependency Graphs

A dependency graph represents relationships between projects.

```text
Application
├── A
│   ├── C
│   └── D
└── B
    └── D
```

Here:

- `A` and `B` are direct dependencies.
- `C` and `D` are transitive dependencies.
- `D` is shared by both branches.

A conflict can happen when requirements cannot be satisfied simultaneously:

```text
A requires D >= 1,<2
B requires D >= 2,<3
```

There is no single version of `D` that satisfies both ranges, so a resolver may be unable to produce a valid environment.

Think of dependency resolution as solving a constraint problem:

```text
project requirements
        +
transitive requirements
        +
Python version/platform rules
        ↓
candidate versions
        ↓
compatible resolved graph
```

A graph is useful during debugging because it turns a vague problem such as:

> “Package X broke.”

into a more precise question:

> “Which dependency changed, which package required it, and what other constraints affected resolution?”

## 8. Why Dependency Management Matters

Unmanaged dependencies create hidden state.

Imagine two machines:

```text
Machine A
A = 2.1
B = 4.3
C = 1.7
```

and:

```text
Machine B
A = 2.3
B = 4.5
C = 2.0
```

The Python source code might be identical while the environment is not.

That difference can cause:

- different behavior;
- different exceptions;
- different serialization formats;
- different performance;
- different supported APIs;
- different vulnerability exposure.

Production dependency management therefore connects to the same engineering habits from the previous chapters:

```text
Explicit configuration
      ↓
Reproducible environment
      ↓
Predictable behavior
      ↓
Testable upgrades
      ↓
Controlled deployment
```

The objective is not to freeze software forever. The objective is to make change deliberate.

## 9. Python Package Ecosystem

At a high level, the Python packaging ecosystem contains:

- project metadata;
- package distributions;
- package indexes;
- wheels;
- source distributions;
- dependency metadata;
- installers/resolvers.

A useful distinction is:

```text
Project/distribution
    ↓
published artifact
    ↓
installation
    ↓
importable module/package
```

The thing you install is a **distribution**. The importable code may have a different name.

For example, a project might publish a distribution named `some-library` while the Python import might be:

```python
import some_library
```

The exact naming relationship varies by project.

You do not need to memorize packaging internals at this stage. The important point is that package management operates on distributions and metadata, while Python source code operates on importable modules and packages.

## 10. Package Indexes and Package Installation

A package index is a source from which package distributions can be discovered and downloaded.

A common default source in Python workflows is the Python Package Index (PyPI), although organizations may also use private indexes or controlled mirrors.

Conceptually:

```text
pyproject.toml
      ↓
package manager / resolver
      ↓
configured package index
      ↓
candidate distributions
      ↓
selected version
      ↓
environment
```

Do not treat the existence of a package name on an index as proof that it is the package you intended to install.

Production engineers verify:

- the spelling of the project name;
- project documentation;
- expected publisher/maintainer information;
- source/index policy;
- version constraints;
- integrity information where available.

**Security Note:** Installation itself is a trust decision. A dependency is not safe merely because it can be downloaded.

## 11. Package Names vs Import Names

A common beginner mistake is to assume the package installation name must match the Python import name.

This is not guaranteed.

You might run:

```bash
pip install package-name
```

and later use:

```python
import package_name
```

The two names can also differ more substantially.

When debugging:

```text
ModuleNotFoundError
      ↓
Was the distribution installed?
      ↓
Did I use the correct Python environment?
      ↓
Is the distribution/import name different?
      ↓
Is the dependency declared in the project?
```

Do not immediately run another install command without finding the actual cause.

A production workflow favors diagnosis over repeated trial-and-error installation.

## 12. Dependency Declaration

A dependency declaration is a statement of what your project requires.

A modern Python project commonly places project metadata and dependencies in `pyproject.toml`.

Conceptually:

```text
Application requirements
        ↓
dependency declaration
        ↓
resolver
        ↓
resolved environment
```

The declaration should answer:

> “What does this project need?”

It is different from the lock state, which answers:

> “Which concrete compatible artifacts did the resolver choose for this environment?”

Keep those questions separate throughout this chapter.

## 13. pyproject.toml

`pyproject.toml` is the standard configuration/metadata file format defined by the Python packaging specifications. The `[project]` table is the standardized place for core project metadata, including dependencies.

A minimal example:

```toml
[project]
name = "example-project"
version = "0.1.0"
requires-python = ">=3.12"

dependencies = [
    "requests>=2.0,<3.0",
]
```

The important fields here are:

```text
name
    project/distribution name

version
    project version

requires-python
    Python versions the project supports

dependencies
    runtime requirements
```

Project configuration can also contain other standardized metadata and tool-specific configuration, but we will stay focused on dependency management.

**Production Note:** Keep dependency declarations understandable. A future engineer should be able to look at the project metadata and understand the intended runtime requirements without reverse-engineering a machine-specific environment.

## 14. Project Metadata

The `[project]` table can contain metadata such as:

```toml
[project]
name = "example-project"
version = "0.1.0"
description = "Example application"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31,<3",
]
```

For this chapter, the most important concept is that project metadata describes the project's declared requirements.

Do not confuse:

```text
project version
```

with:

```text
dependency version
```

These are different pieces of metadata.

Your application might be:

```text
example-project = 0.4.0
```

while it depends on:

```text
requests >=2.31,<3
```

The project version describes your software. The dependency specifier describes a constraint on another project.

## 15. Dependency Specifications

A dependency specification can be very loose or very strict.

Examples:

```text
requests
requests>=2.31
requests==2.32.5
requests>=2.31,<3
requests~=2.31
```

Read these as constraints rather than promises.

For example:

```text
requests>=2.31,<3
```

means:

```text
minimum accepted version: 2.31
maximum boundary: below 3
```

The resolver chooses a concrete candidate that satisfies the constraints and the rest of the dependency graph.

The exact version selected is therefore a resolution outcome, not simply a copy of the human-written dependency declaration.

## 16. Version Specifiers

Python dependency specifiers support operators including:

```text
>=
>
<=
<
==
!=
~=
===
```

Multiple clauses separated by commas are combined as logical AND constraints.

For example:

```text
requests>=2.31,<3
```

means a candidate must satisfy both conditions.

The compatible-release operator is useful when you want a compatible version range:

```text
~=2.31
```

which is approximately:

```text
>=2.31, ==2.*
```

while:

```text
~=2.31.4
```

narrows the compatible prefix:

```text
>=2.31.4, ==2.31.*
```

These rules come from the Python packaging version-specifier specification.

**Common Mistake:** Treating `~=` as “anything newer.” It is a compatibility constraint, not an unrestricted upgrade.

## 17. Exact Versions

An exact specifier looks like:

```toml
dependencies = [
    "requests==2.32.5",
]
```

This asks for that exact public version.

Exact pins can be useful for applications where reproducibility and tightly controlled deployments matter. They can also make security maintenance and upgrades more deliberate because a security fix does not automatically fit the declaration.

For published libraries, the packaging specification cautions against using strict equality without a wildcard because it can make downstream security updates harder. Application dependency strategy can be different.

The engineering question is:

> Where should reproducibility be enforced: in the editable dependency declaration, in the lock state, or in both?

Do not assume that exact pins in every field are automatically the best design.

## 18. Minimum Versions

A minimum version such as:

```toml
dependencies = [
    "requests>=2.31",
]
```

communicates:

> “The application requires at least this capability level.”

It gives the resolver more freedom to select newer compatible versions.

Advantages:

- less restrictive;
- easier for downstream environments to combine requirements;
- can allow bug/security fixes without changing the declaration.

Trade-offs:

- broader possible resolution space;
- more runtime variability if no lock is used;
- behavior can still change across versions.

For an application, a lock file can provide concrete reproducibility while the project declaration remains a meaningful statement of supported requirements.

## 19. Compatible Version Ranges

A bounded range:

```toml
dependencies = [
    "requests>=2.31,<3",
]
```

communicates an intended compatibility window.

This can be helpful when the project has not been validated against a future major version.

The idea is:

```text
known-compatible lower boundary
          +
known-unsafe / untested upper boundary
```

An upper bound should be based on a real compatibility reason. Arbitrary upper bounds can create unnecessary maintenance.

**Production Lesson:** Version constraints are communication. A future maintainer should be able to understand why a boundary exists.

## 20. Upper Bounds

An upper bound such as:

```text
<3
```

can protect an application from a major release that may contain breaking changes.

For example:

```text
requests>=2.31,<3
```

This does not mean:

> “Version 3 is bad.”

It means:

> “This project currently declares compatibility only within this range.”

The engineering practice is to revisit upper bounds when the ecosystem moves forward.

An upper bound that remains forever without review can become dependency debt.

Questions to ask:

- What compatibility assumption caused the bound?
- Is it still necessary?
- Have tests demonstrated compatibility with the newer major version?
- Can the bound be relaxed after a controlled upgrade?

## 21. Version Pinning

Pinning means constraining a dependency to a concrete version.

```text
requests==2.32.5
```

Benefits:

- repeatable resolution;
- controlled upgrades;
- easier rollback to a known state.

Costs:

- packages can become stale;
- security fixes require explicit maintenance;
- upgrades become a recurring engineering task.

A common mature strategy is:

```text
human-readable dependency declaration
        +
resolved lock file
```

instead of putting every exact resolved transitive version directly into the top-level declaration.

The right strategy depends on whether you are maintaining an application, a library, or another kind of project.

## 22. Semantic Versioning

Semantic Versioning, commonly written:

```text
MAJOR.MINOR.PATCH
```

For example:

```text
2.7.4
```

is conventionally interpreted as:

```text
2 = major
7 = minor
4 = patch
```

The intended SemVer model is roughly:

- **major:** incompatible changes may occur;
- **minor:** backward-compatible functionality is added;
- **patch:** backward-compatible fixes are made.

But SemVer is a convention/specification, not a guarantee that every project follows it perfectly.

Therefore:

```text
version number
      ↓
useful signal
      ↓
not a substitute for release notes + tests
```

**Key Takeaway:** Never reduce upgrade safety to “major means dangerous; patch means safe.” Read what the project actually changed.

## 23. Major / Minor / Patch Versions

Suppose a dependency moves:

```text
2.4.7 → 2.4.8
```

The change is a patch-level change under SemVer.

Another move:

```text
2.4.7 → 2.5.0
```

is minor.

And:

```text
2.4.7 → 3.0.0
```

is major.

These numbers help you reason about the expected level of change, but they do not answer:

- whether your code is compatible;
- whether performance changed;
- whether defaults changed;
- whether a transitive dependency changed.

Use version numbers as one signal among several.

## 24. Pre-release Versions

Python version specifiers can encounter pre-release versions such as:

```text
3.0.0a1
3.0.0b1
3.0.0rc1
```

Common terms:

```text
alpha  → a
beta   → b
release candidate → rc
```

For normal production dependency management, stable releases are generally preferred unless you have a deliberate reason to test a pre-release.

Packaging tools have rules for when pre-releases are considered, so do not assume that an unconstrained command will always install the newest pre-release.

**Production Note:** If you intentionally depend on a pre-release, document why and test it as a special compatibility decision.

## 25. Version Specifier Examples

Here is a practical comparison:

| Specifier | Meaning |
|---|---|
| `requests` | no explicit version constraint |
| `requests>=2.31` | 2.31 or newer |
| `requests==2.32.5` | exactly 2.32.5 |
| `requests>=2.31,<3` | within a bounded range |
| `requests~=2.31` | compatible with the 2.x series under the compatible-release rule |
| `requests!=2.32.5` | exclude one version |

A useful exercise is to say the requirement aloud before using it.

For example:

> “I need at least 2.31 but I am not declaring compatibility with 3.x.”

That sentence is often clearer than thinking only in symbols.

## 26. Dependency Resolution

Dependency resolution is the process of finding concrete versions that satisfy all applicable constraints.

Imagine:

```text
Your app
 ├── A >=1,<2
 └── B >=3,<4
```

and:

```text
A → C >=5,<6
B → C >=5.2,<6
```

The resolver must find a version of `C` satisfying both.

Conceptually:

```text
declared requirements
       +
transitive requirements
       +
Python/platform conditions
       ↓
candidate graph
       ↓
compatible resolved graph
```

When the constraints have no common solution, resolution fails rather than producing an environment that violates the requirements.

**Important:** Resolution is not the same as compatibility testing. A resolver can find a mathematically compatible dependency set while your application still fails because your code relied on behavior that changed.

## 27. Dependency Conflicts

A conflict is a case where requirements cannot be satisfied together.

Example:

```text
Application → A
Application → B

A requires C >=1,<2
B requires C >=2,<3
```

No single `C` version satisfies both.

A conflict can also arise from:

- Python version requirements;
- platform markers;
- optional features;
- different package sources;
- upper bounds.

When a resolver reports a conflict, do not immediately remove random dependencies.

Instead:

```text
Read the conflict
      ↓
Identify each requirement
      ↓
Find the shared package
      ↓
Check compatible ranges
      ↓
Decide which requirement must change
```

This is dependency reasoning rather than dependency guessing.

## 28. Transitive Dependency Conflicts

A project may conflict because of a package it does not list directly.

```text
App
├── A
│   └── C <2
└── B
    └── C >=2
```

The application did not declare `C`, but the resolver must still account for it.

This is why a dependency upgrade should be reviewed at graph level:

```text
Direct package changed
        ↓
transitive graph may change
        ↓
environment behavior may change
```

**Common Mistake:** Looking only at the direct package that changed and ignoring the rest of the lock diff.

## 29. Dependency Trees

A dependency tree is a human-readable view of the graph.

With current `uv`, a project can use:

```bash
uv tree
```

The tree helps answer:

- Which package introduced this dependency?
- Is it direct or transitive?
- Which package depends on the version in question?
- Is a package shared by multiple branches?

You can also inspect the environment using the compatible `uv pip` interface when working at the environment level:

```bash
uv pip tree
```

The two commands answer related but different questions: project-oriented dependency structure versus environment-oriented package state.

**Try It Yourself**

```bash
uv tree
```

Before reading the output, predict which direct dependencies you expect to see.

## 30. Reproducible Environments

A reproducible environment means that another machine can recreate a dependency environment from version-controlled project information with predictable results.

A useful mental model is:

```text
source code
+
Python version policy
+
dependency declaration
+
lock information
+
controlled installation process
=
reproducible environment
```

Reproducibility is not only about package versions. Different Python versions, platforms, environment variables, and external services can also affect behavior.

The practical goal is:

> Reduce accidental variability so that differences in program behavior can be investigated rather than dismissed as “environment issues.”

## 31. Why "Works on My Machine" Happens

The phrase usually means the developer's environment contains information that the repository did not fully describe.

Typical causes:

```text
unrecorded dependency
different dependency version
different Python version
different operating system
missing optional dependency
manually installed package
stale virtual environment
different environment variables
```

A stronger project workflow makes important state visible:

```text
pyproject.toml
      +
lock information
      +
Python version declaration
      +
documented setup
```

The more precisely the environment is defined, the easier it is to reproduce and debug.

## 32. Lock Files

A lock file records the concrete dependency resolution chosen for a project.

In a `uv` project, the lock file is:

```text
uv.lock
```

Current `uv` documentation describes `uv.lock` as a cross-platform lockfile containing exact dependency information and recommends checking it into version control for consistent installations across machines. The file is managed by `uv` and should not be treated like a hand-edited dependency declaration.

Conceptually:

```text
pyproject.toml
    ↓
broad requirements
    ↓
resolver
    ↓
uv.lock
    ↓
concrete resolved graph
```

**Production Note:** Commit the lock file for application projects when the team's workflow uses it for reproducibility, and let the package manager update it rather than hand-editing it.

## 33. Declared Dependencies vs Resolved Dependencies

This distinction is foundational.

Declared:

```toml
[project]
dependencies = [
    "requests>=2.31,<3",
]
```

Resolved:

```text
requests 2.32.x
```

The declaration says:

> “These versions are acceptable according to our project requirements.”

The lock file says:

> “This concrete graph was resolved for the project.”

Keep the model:

```text
Declaration = desired constraint
Resolution  = selected solution
Environment = installed realization
```

These are related but not identical.

**Interview Tip:** When asked why a lock file is useful, explain that it narrows a broad requirement set to concrete dependency choices that can be reproduced more reliably.

## 34. Lock File Purpose

A lock file is useful because it captures the resolver's concrete result.

Without a lock file, two installations satisfying:

```text
A>=1,<2
B>=3,<4
```

could potentially resolve to different compatible versions at different times.

With lock information:

```text
same project
    ↓
same recorded graph
    ↓
more predictable environment
```

Locking improves reproducibility, but it does not eliminate:

- application bugs;
- dependency vulnerabilities;
- malicious upstream changes that are intentionally upgraded later;
- platform-specific behavior;
- Python-version differences that the lock supports differently;
- compromised build/deployment infrastructure.

A lock file is a control, not a complete security strategy.

## 35. uv and Modern Python Dependency Management

`uv` is a modern Python package and project management tool. Current `uv` documentation provides project-level workflows around `pyproject.toml`, `uv.lock`, virtual environments, dependency groups, and commands such as `uv init`, `uv add`, `uv remove`, `uv sync`, `uv lock`, and `uv tree`.

The most important beginner model is:

```text
uv
├── project creation
├── dependency declaration
├── dependency resolution
├── lock management
├── environment synchronization
└── dependency inspection
```

`uv` is one tool in the Python ecosystem, not the only valid way to manage dependencies.

For this roadmap, it is useful because it makes the full dependency lifecycle visible in a modern project workflow.

## 36. Creating a Project with uv

A typical project initialization flow is:

```bash
uv init my-project
cd my-project
```

`uv init` creates a project structure and `pyproject.toml`. Current project documentation also describes the role of the project's `.venv`, `.python-version`, and `uv.lock` as the project workflow evolves.

Conceptually:

```text
uv init
   ↓
project metadata
   ↓
add dependencies
   ↓
lock + sync
```

Do not memorize generated scaffolding. Learn which files represent which state.

**Production Note:** Treat generated project files as artifacts of a tool-supported workflow, not as magic files whose purpose you must guess.

## 37. Adding Dependencies

To add a runtime dependency:

```bash
uv add requests
```

Current `uv` documentation says `uv add` updates `pyproject.toml`, the lockfile, and the project environment.

You can add a constrained dependency:

```bash
uv add 'requests>=2.31,<3'
```

Or an exact version:

```bash
uv add 'requests==2.32.5'
```

The important engineering sequence is:

```text
declare
  ↓
resolve
  ↓
lock
  ↓
sync
```

Avoid manually editing several environment artifacts whenever the package manager can keep them consistent.

## 38. Removing Dependencies

To remove a direct project dependency:

```bash
uv remove requests
```

Current `uv` documentation describes `uv remove` as updating the project dependencies and corresponding lock/environment state.

After removal:

```text
project no longer declares package
        ↓
resolver recomputes dependency graph
        ↓
unused transitive packages may disappear
```

The exact resulting graph depends on whether other dependencies still require the removed package.

**Common Mistake:** Assuming removing one direct dependency necessarily removes every package that was installed alongside it.

## 39. Updating Dependencies

Current `uv` supports targeted and broad lockfile upgrades.

Targeted upgrade:

```bash
uv lock --upgrade-package requests
```

This asks `uv` to allow a newer compatible version for the named package while retaining other locked versions where possible.

Broad upgrade:

```bash
uv lock --upgrade
```

This allows package upgrades across the lockfile, subject to the project's constraints.

A useful production choice is to start with the smallest change that answers the problem:

```text
security issue in one package
        ↓
targeted upgrade
```

rather than automatically creating an unrelated ecosystem-wide diff.

## 40. Locking Dependencies

The project lock operation is:

```bash
uv lock
```

It resolves the dependency graph into the lock file without requiring you to manually calculate every transitive version.

A useful distinction:

```text
uv add
    = change declared dependency requirements

uv lock
    = resolve/update lock state

uv sync
    = install/synchronize environment from project + lock state
```

Current `uv` documentation explains that locking is resolution while syncing installs the selected subset into the project environment.

When reviewing a dependency change, inspect both the declaration and the lock diff.

## 41. Syncing Environments

`uv sync` updates the project environment to match the project's dependency state.

```bash
uv sync
```

Current `uv` documentation describes synchronization as installing project dependencies from the lockfile and, by default, removing packages that are extraneous from the project environment.

This gives you a clean mental model:

```text
pyproject.toml
      +
uv.lock
      ↓
uv sync
      ↓
.venv
```

When debugging “works locally” problems, sync is useful because it reduces hidden environment drift.


### A small Python inspection helper

The following program does not change the environment. It simply asks the running Python environment which distribution versions are installed.

```python
from importlib.metadata import PackageNotFoundError, version


def installed_version(distribution_name: str) -> str | None:
    try:
        return version(distribution_name)
    except PackageNotFoundError:
        return None


for name in ("requests", "pydantic"):
    print(f"{name}: {installed_version(name)}")
```

What this demonstrates:

- `importlib.metadata.version()` asks the current environment for a distribution's installed version.
- `PackageNotFoundError` means the requested distribution is not installed in that environment.
- This is a runtime inspection tool, not a replacement for the project's declared requirements or lock file.

**Common Mistake:** Using the output from the current machine as the project's dependency specification. The machine tells you what is installed here; `pyproject.toml` and lock state describe the project workflow.

## 42. Inspecting Dependency State

Useful `uv` inspection commands include:

```bash
uv tree
uv pip list
uv pip show requests
uv pip check
```

Current `uv` exposes both project-oriented and environment-oriented inspection commands. `uv tree` displays the project's dependency tree, while the `uv pip` interface offers environment-focused commands such as `list`, `show`, `tree`, and `check`.

Use the narrowest tool for the question:

```text
What does the project declare/resolve?
    → uv tree

What is installed in this environment?
    → uv pip list

What do I know about one installed package?
    → uv pip show <package>

Are installed requirements compatible?
    → uv pip check
```

Inspection before change is a production habit.

## 43. Reproducibility

A useful `uv` project model is:

```text
pyproject.toml
    = project requirements and metadata

uv.lock
    = concrete resolved dependency graph

.venv
    = local installed environment
```

Current `uv` documentation recommends checking `uv.lock` into version control for consistent installations and notes that `uv run` automatically checks lock/environment state as part of its project workflow.

Reproducibility is strengthened when the team also controls:

- supported Python versions;
- source/index policy;
- dependency declarations;
- lock state;
- build instructions;
- environment-specific configuration.

It is not enough to say “we use a lock file” without asking whether the lock file is actually used during installation and deployment.

## 44. Development vs Production Dependencies

Not every package belongs in the production runtime.

Example:

```text
Runtime:
    pydantic
    requests

Development/testing:
    pytest
    ruff
    type checker
```

Why separate them?

```text
production dependency set
        ↓
smaller runtime surface
        ↓
less installation overhead
        ↓
less maintenance and attack surface
```

The exact mechanism depends on the packaging/workflow. With modern `uv`, development dependencies are commonly represented using the standardized `[dependency-groups]` mechanism.

The engineering goal is not “minimize packages at all costs.” It is “include what the environment actually needs, and distinguish purposes clearly.”

## 45. Optional Dependencies

Optional dependencies are useful when a published project has optional features.

For example:

```toml
[project.optional-dependencies]
cli = [
    "rich",
    "click",
]
```

The keys define extras, and tools such as `pip` and `uv` can install a project with a selected extra.

This is conceptually different from local development dependencies.

```text
optional-dependencies
    = published feature extras

dependency-groups
    = local workflow groups, such as dev/test/lint
```

Current PyPA guidance distinguishes packaging extras under `[project.optional-dependencies]` from the standardized `[dependency-groups]` mechanism used for internal development use cases.

**Common Mistake:** Calling every “optional” package a development dependency. The purpose and publication behavior matter.


With current `uv`, an optional dependency can also be added through the `--optional` option. For example, the intent is conceptually:

```bash
uv add --optional cli rich
```

This puts `rich` into the project's `cli` optional extra. Verify the command against the installed `uv --version` and current documentation in environments where CLI behavior has changed.

Do not confuse this with:

```bash
uv add --dev pytest
```

which is intended for local development dependencies.

## 46. Dependency Groups

Modern Python packaging includes standardized dependency groups.

Example:

```toml
[dependency-groups]
dev = [
    "pytest",
    "ruff",
]
```

Current `uv` documentation uses this mechanism for development dependencies and supports commands such as:

```bash
uv add --dev pytest
uv add --group lint ruff
```

The `dev` group is treated specially by `uv` defaults, while additional groups can be included or excluded through group flags.

Groups are helpful because they represent local workflow needs without turning those tools into published runtime requirements.

**Production Note:** Know which dependency groups actually reach your production image/environment.

## 47. Dependency Constraints

Constraints exist at several levels.

Project-level declaration:

```toml
dependencies = [
    "requests>=2.31,<3",
]
```

Transitive package requirement:

```text
some-library → requests>=2.30
```

Python/platform condition:

```text
package; sys_platform == "win32"
```

The resolver must consider all applicable requirements.

A dependency constraint can therefore describe:

- acceptable versions;
- excluded versions;
- environment-specific applicability;
- optional features.

The important question is:

> What problem is this constraint solving?

Constraints without a reason can make upgrades harder to understand.

## 48. Dependency Upgrade Strategies

There are several legitimate upgrade scopes.

### Targeted upgrade

One dependency changes.

Useful for:

- a specific security fix;
- a known bug fix;
- investigating one dependency issue.

### Group upgrade

A related set changes together.

Useful when:

- several packages are released as a coordinated ecosystem;
- compatibility requires synchronized movement.

### Broad upgrade

Many dependencies update.

Useful when:

- intentionally refreshing the full environment;
- reducing accumulated version drift.

The larger the change, the larger the testing and diagnosis surface.

```text
small change
    → easier attribution

large change
    → more uncertainty
```

This is not a rule against broad upgrades. It is a reminder to understand the change surface.

## 49. Upgrade Everything vs Targeted Upgrades

Suppose your lock state contains 80 packages and one dependency has a security release.

Targeted:

```bash
uv lock --upgrade-package dependency-name
```

Broad:

```bash
uv lock --upgrade
```

Current `uv` supports both forms, while the targeted form is specifically intended to update one package to the latest compatible version while retaining other locked packages where possible.

A sensible decision process is:

```text
What problem are we solving?
        ↓
How much change is necessary?
        ↓
What is the smallest useful upgrade?
        ↓
What testing scope does that require?
```

The right answer depends on the situation.

## 50. Safe Upgrade Workflow

Use this workflow as a default production habit:

```text
1. Identify why the upgrade is needed
2. Inspect the current version and graph
3. Read release notes
4. Check compatibility
5. Change the dependency requirement if needed
6. Update lock information
7. Review the dependency diff
8. Run unit tests
9. Run integration tests
10. Run lint/type checks
11. Exercise important workflows
12. Benchmark important paths when relevant
13. Review security implications
14. Make the change easy to review and revert
15. Deploy progressively
16. Observe
17. Roll back if necessary
```

The order matters.

Do not start with:

```text
upgrade
    ↓
hope
```

Start with:

```text
reason
    ↓
inspect
    ↓
change
    ↓
prove
```

## 51. Read Release Notes

Before upgrading an important package, read the package's release notes or changelog.

Look for:

- breaking changes;
- removed APIs;
- deprecations;
- changed defaults;
- changed exception behavior;
- Python support changes;
- dependency changes;
- performance changes;
- security fixes;
- migration steps.

A version number gives you a hint about scope. Release notes explain what actually happened.

**Example reasoning**

```text
Current:
library 4.8

Target:
library 4.9

Question:
What changed between 4.8 and 4.9?
```

You are looking for changes that intersect your code, not every sentence in the changelog.

## 52. Check Compatibility

Check compatibility before and after the upgrade.

Useful questions:

```text
Does the package support our Python version?
Does it support our operating systems?
Did an API we use change?
Did defaults change?
Did a transitive package move?
Did a test fixture or serialization format change?
```

For a production application, compatibility is a three-way relationship:

```text
Your code
   ↕
Dependency behavior
   ↕
Python/runtime environment
```

A package may install successfully while still being incompatible with a particular combination of application code and runtime configuration.

## 53. Update Lock Information

After changing project requirements, refresh the lock state.

For example:

```bash
uv lock
```

or for a targeted upgrade:

```bash
uv lock --upgrade-package requests
```

Current `uv` project documentation describes automatic lock/sync behavior around common commands, while `--locked` and `--frozen` are available when you need to enforce or reuse existing lock state instead of allowing changes.

The important review point is:

```text
pyproject.toml diff
        +
uv.lock diff
        =
dependency change
```

Do not review only the human-edited line.

## 54. Run Tests

A successful resolver result proves only that the dependency graph satisfies the declared constraints.

It does not prove that your application still behaves correctly.

Run:

```text
unit tests
integration tests
CLI tests
serialization tests
important workflows
```

Then consider performance-sensitive checks where relevant.

An upgrade can break behavior without changing your source code because the dependency's implementation changed.

**Production Lesson:** Compatibility testing is the application owner's responsibility. The resolver solves dependency constraints; it does not know your business logic.

## 55. Run Linters and Type Checkers

Dependency upgrades can expose problems in:

- imports;
- removed symbols;
- changed signatures;
- changed type hints;
- deprecated APIs.

Run your project's static checks after an upgrade.

The goal is not to trust a linter or type checker as a complete compatibility test. It is to add another evidence layer.

```text
Resolver
   ↓
static checks
   ↓
unit tests
   ↓
integration tests
```

Different tools detect different classes of breakage.

## 56. Run Integration Tests

Integration tests exercise boundaries between your code and dependencies.

Examples:

```text
database client
HTTP client
serialization library
file parser
SDK
model client
```

A unit test may still pass while a real integration path breaks after a package upgrade.

Use integration tests selectively on high-value paths rather than turning every test run into a massive end-to-end environment.

**Key Takeaway:** The closer a dependency sits to an external boundary, the more valuable compatibility-focused integration testing becomes.

## 57. Inspect Behavioral Changes

Not every breaking change produces an import error.

A dependency can change:

- default timeout;
- error type;
- ordering;
- serialization;
- precision;
- resource usage;
- logging behavior;
- retry defaults.

Therefore inspect behavior, not just installation.

A practical review:

```text
What did we rely on before?
        ↓
Did the dependency change that behavior?
        ↓
Do our tests cover the behavior?
        ↓
Do targeted manual/integration checks still pass?
```

## 58. Benchmark Important Workloads When Appropriate

Some upgrades change performance.

For example:

```text
parser
database driver
serialization library
vector-store client
data-frame operation
```

Do not assume:

```text
newer = faster
```

or:

```text
older = safer
```

Use the measurement method from the previous chapter when performance matters:

```text
baseline
    ↓
upgrade
    ↓
same workload
    ↓
measure again
    ↓
compare
```

The purpose is not to create a benchmark for every dependency upgrade. It is to recognize when performance is an important compatibility dimension.

## 59. Review the Dependency Diff

Suppose the direct dependency changed from:

```text
A 1.4 → 1.5
```

but the lockfile shows:

```text
A 1.5
B 2.3 → 2.4
C 4.1
D new
```

The review question is:

> “Why did B change and why did D appear?”

Useful questions:

- Which package introduced the new package?
- Is the change expected?
- Did the dependency graph become larger?
- Did package sources change?
- Did platform-specific dependencies appear?
- Does a vulnerability scanner now report something new?
- Did deployment size change?

Graph-level review is one of the biggest differences between beginner and production dependency management.

## 60. Rollback

Rollback means returning to a known-good dependency state.

A good upgrade process makes rollback straightforward:

```text
Known-good state
      ↓
Upgrade commit
      ↓
Problem discovered
      ↓
Revert / restore known-good lock state
      ↓
Rebuild + retest
```

Possible rollback artifacts include:

- version-control history;
- previous `pyproject.toml`;
- previous `uv.lock`;
- previous deployment image/environment.

Do not assume that reverting only a top-level version will necessarily recreate the previous transitive graph. The lock state is part of the reproducible dependency state.

## 61. Handling Failed Upgrades

When an upgrade fails, classify the failure.

```text
Resolver failure
    → dependency constraints conflict

Import failure
    → API/name/environment issue

Unit-test failure
    → behavior/API regression

Integration failure
    → boundary behavior changed

Performance regression
    → runtime/resource behavior changed

Security finding
    → dependency state requires remediation
```

Then decide:

```text
fix application compatibility
or
adjust dependency constraint
or
upgrade related packages
or
rollback
```

Avoid “fixing” a dependency failure by deleting tests or swallowing exceptions. The failure is useful evidence.

## 62. Dependency Pinning Strategies

Three common styles illustrate the trade-offs:

### Exact pin

```text
A==1.2.3
```

### Bounded range

```text
A>=1.2,<2
```

### Minimum

```text
A>=1.2
```

A fourth practical layer is lock information:

```text
declaration
    ↓
constraints
    ↓
lockfile
    ↓
concrete environment
```

The lock file can provide repeatable application deployments without forcing every declaration to encode every transitive exact version.

**Production Note:** Pinning is a strategy, not a religion. The right level of constraint depends on whether you publish a reusable library or deploy an application.

## 63. Pinning Trade-offs

Exact pinning often improves reproducibility but reduces upgrade flexibility.

Broad ranges increase flexibility but allow more resolution variability.

A simplified comparison:

| Strategy | Reproducibility at declaration level | Upgrade flexibility | Maintenance style |
|---|---:|---:|---|
| Exact pin | high | lower | explicit refresh |
| Bounded range | medium | medium | controlled compatibility window |
| Minimum | lower | higher | broader compatibility target |
| Lock file + meaningful declarations | high in deployments | flexible declaration layer | deliberate lock refresh |

The final row is often useful for application projects because the declaration communicates requirements while the lock captures a selected environment.

Do not infer that “more pinned” means “more secure.” Security depends on timely updates and review as well as reproducibility.

## 64. Security vs Stability Trade-offs

Dependency upgrades often create a tension:

```text
new version
→ may contain a security or bug fix

but

new version
→ may change application behavior
```

The correct engineering response is not to choose “security” or “stability” blindly.

Instead:

```text
Understand the issue
     ↓
Determine affected versions
     ↓
Determine whether your usage is relevant
     ↓
Identify compatible remediation
     ↓
Test
     ↓
Deploy deliberately
```

A known vulnerability is not automatically proof that an application is exploitable. Relevance depends on affected versions, how the vulnerable component is used, exposure, and available remediation.

**Production Lesson:** Stability is not the absence of change. A stale, vulnerable dependency can itself be an operational risk.

## 65. Supply-Chain Awareness

Now move from dependency management into software supply-chain thinking.

A supply chain is the larger system through which software reaches your application:

```text
Developer
   ↓
source repository
   ↓
release/build process
   ↓
package artifact
   ↓
package index
   ↓
package manager
   ↓
dependency graph
   ↓
application build
   ↓
production
```

A weakness or compromise can occur at multiple points.

You do not need to become a security specialist to practice supply-chain awareness. You do need to ask:

> “Where did this software come from, and what assumptions are we making about it?”

## 66. What Is a Software Supply Chain?

The software supply chain includes:

- source code;
- package maintainers;
- release artifacts;
- package indexes;
- build systems;
- dependency resolvers;
- deployment pipelines;
- third-party services that produce or transport software.

For a Python application:

```text
your code
  +
third-party package
  +
transitive packages
  +
Python runtime
  +
build/deployment process
```

Together these form the environment in which your software exists.

**Key Takeaway:** Software provenance and dependency management are connected. Knowing exactly what you installed is part of knowing what you are running.

## 67. Why Dependencies Create Supply-Chain Risk

Every dependency adds another trust relationship.

If your project has 5 third-party packages:

```text
your team
   ↓
5 external projects
```

If those packages have 20 transitive dependencies:

```text
your team
   ↓
5 direct
   ↓
20+ indirect
```

The number is not the only risk metric, but graph size increases the number of components you may need to understand, update, and monitor.

Risk categories include:

- malicious package;
- compromised maintainer;
- compromised release process;
- known vulnerability;
- dependency confusion;
- typosquatting;
- abandoned project.

**Production Note:** Dependency minimization can reduce complexity, but “zero dependencies” is not a practical goal for most real applications.

## 68. Typosquatting

Typosquatting occurs when a malicious or misleading package name resembles a legitimate package name.

Conceptually:

```text
legitimate-package
legitmate-package
```

A developer who copies an incorrect name can install the wrong distribution.

Defensive habits:

1. verify the spelling;
2. use official project documentation;
3. prefer trusted package sources;
4. review dependency changes;
5. keep lock state and source policy controlled.

Do not blindly copy an install command from an unknown page.

**Security Principle:** A package name is an identifier, not a proof of identity.

## 69. Dependency Confusion

Dependency confusion is a supply-chain risk involving package naming and source resolution when private/internal package names overlap with names available from public repositories.

A conceptual scenario:

```text
internal project name
        +
public package index
        ↓
unexpected package resolution
```

Defensive controls include:

- clear package naming conventions;
- explicit package-index policy;
- private repository configuration;
- CI installation controls;
- review of resolved sources.

Do not treat this chapter as an exploitation guide. The goal is to recognize the risk and build safer dependency-source policies.

## 70. Malicious Packages

A malicious package is intentionally designed to harm or compromise the consumer.

Potential risks include:

- data theft;
- credential exposure;
- arbitrary code execution during installation or use;
- unexpected network activity;
- manipulated output.

You do not need malicious implementation examples to understand the engineering problem.

Use this model instead:

```text
package install
      ↓
trust decision
      ↓
code becomes part of environment
```

Before adding a package, ask:

```text
Is this the package I intended?
Do I know its source?
Do I need it?
Is it maintained?
How will I update it?
```

## 71. Compromised Maintainer Accounts

A legitimate project can become risky if an authorized maintainer account is compromised.

The package name may remain correct.

The project may remain popular.

Your installation command may remain unchanged.

Yet the released artifact could still be altered.

This is why supply-chain awareness cannot stop at:

> “We use a popular package.”

Additional controls can include:

- lock files;
- integrity information;
- trusted source policy;
- dependency review;
- automated scanning;
- staged rollout;
- monitoring;
- incident response.

No single control solves every supply-chain failure mode.

## 72. Compromised Releases

A release artifact is the software you actually install.

A compromise can occur between source code and the published artifact, or within release infrastructure.

Think:

```text
source
  ↓
build
  ↓
artifact
  ↓
index
  ↓
installation
```

A secure engineering process cares about each transition.

A developer should not assume:

```text
source repository looks correct
→
artifact must be correct
```

Artifact integrity and provenance help reduce uncertainty, but they are part of a layered control strategy.

## 73. Abandoned Dependencies

A dependency can be legitimate and non-malicious but still become a maintenance problem.

Warning signs include:

- no meaningful maintenance for a long time;
- no support for required Python versions;
- unaddressed bugs;
- stale dependencies of its own;
- unclear ownership;
- broken release process.

Abandonment is not a proof that a package is unsafe.

Instead ask:

```text
Does this project still meet our needs?
Can we replace it?
Can we safely pin it?
Can we maintain a fork if necessary?
```

The production goal is to avoid being surprised by a dependency becoming operationally irrelevant.

## 74. Vulnerable Dependencies

A vulnerable dependency is a legitimate component with a known security weakness.

Differentiate it from:

```text
malicious package
```

which is intentionally harmful.

A vulnerability finding is evidence that requires investigation.

Ask:

```text
Which versions are affected?
Which versions do we use?
Is the vulnerable functionality reachable in our application?
What is the exposure?
Is there a fixed version?
What testing is needed?
```

Do not claim a current vulnerability without verification.

**Important:** Vulnerability severity in an advisory and actual risk to a specific application are related but not identical concepts.

## 75. Transitive Dependency Risk

A transitive dependency can create risk even when you never import it directly.

```text
App
 ↓
Framework
 ↓
Library
 ↓
Transitive dependency
```

The transitive component can still:

- execute at runtime;
- contribute APIs;
- affect serialization;
- influence security;
- influence performance;
- appear in the final environment.

Therefore production engineers inspect the complete graph.

Useful question:

> “Who brought this package into the environment?”

The dependency tree is often the fastest way to answer that question.

## 76. Dependency Provenance

Provenance means being able to reason about where a dependency came from.

Useful provenance questions:

```text
Which project is this?
Which source/index provided it?
Which version was resolved?
Which release artifact was selected?
Which direct dependency introduced it?
```

For a production application, provenance can matter during:

- security incidents;
- audits;
- dependency migrations;
- reproducibility investigations;
- emergency upgrades.

Do not treat a URL or package name alone as full provenance. Source identity, artifact identity, and the project's trust policy all matter.

## 77. Package Integrity

Integrity asks:

> “Is this artifact the artifact we expected?”

Hash-based integrity information can help detect unexpected changes to a downloaded artifact.

Conceptually:

```text
expected artifact
    ↓
hash/integrity information
    ↓
downloaded artifact
    ↓
compare
```

Integrity does not mean:

```text
trusted = guaranteed safe
```

A malicious artifact can still have a valid hash if the attacker was the party that produced the expected hash.

Therefore:

```text
integrity
+
trusted source
+
provenance
+
review
+
scanning
+
controlled build
```

provide stronger defense in combination.

Avoid saying that “hashes solve supply-chain security.” They solve a narrower integrity problem.

## 78. Hashes and Reproducibility

Hashes can help make a dependency installation more exact because the installer can distinguish the expected artifact from a different artifact with the same version label.

A reproducible workflow often combines:

```text
declared requirements
+
lock state
+
artifact integrity
+
controlled sources
```

This reduces accidental variation.

It still does not solve all risks:

- compromised developer machine;
- compromised build runner;
- stolen secrets;
- malicious source changes that are intentionally accepted;
- vulnerable application usage;
- insecure deployment configuration.

**Production Note:** Reproducibility is a reliability property and a security-supporting property, not a complete security boundary.

## 79. Lock Files and Integrity

Lock files can contain exact package information and, depending on the format/tool, additional artifact/integrity metadata.

For `uv`, the lockfile contains concrete dependency resolution information and is designed to support reproducible project environments. Current documentation states that `uv.lock` is managed by `uv` and should not be manually edited.

A strong review asks:

```text
Did the version change?
Did the source change?
Did the artifact selection change?
Did transitive dependencies change?
Did platform-specific resolution change?
```

The lock file is therefore both a reproducibility artifact and an important review artifact.

## 80. Vulnerability Scanning

Dependency vulnerability scanners compare project/environment components against known security information.

A useful workflow is:

```text
dependency inventory
       ↓
vulnerability check
       ↓
affected version?
       ↓
usage/exposure assessment
       ↓
remediation
```

Do not treat a scanner result as the final application-risk verdict.

A scanner can tell you:

> “This component/version has a known advisory.”

Current `uv` also exposes:

```bash
uv audit
```

as a project dependency audit command. The output and coverage of any security tool can change over time, so treat it as one layer in the security process rather than as the sole source of truth.

Your engineering investigation must still determine:

> “What does that mean for this application?”

## 81. Automated Dependency Updates

Automation can create update proposals automatically.

Conceptually:

```text
new dependency release
       ↓
automated update proposal
       ↓
CI
       ↓
tests
       ↓
human review
       ↓
merge
```

Benefits:

- smaller upgrade backlog;
- faster response to fixes;
- regular maintenance.

Risks:

- update noise;
- accidental broad changes;
- false confidence from green tests that do not cover important behavior.

The important principle is:

> Automation should accelerate review, not replace engineering judgment.

## 82. Reviewing Automated Updates

When an automated update arrives, review it like any other change.

Check:

```text
What changed?
Why did it change?
What transitive packages changed?
What release notes apply?
Which tests ran?
Which tests did not run?
Did Python support change?
Did runtime behavior change?
```

A green CI status means:

> “The configured checks passed.”

It does not necessarily mean:

> “Every production property is unchanged.”

Review the change surface.

## 83. CI/CD Dependency Checks

A production pipeline can include dependency controls:

```text
commit
  ↓
install from project/lock state
  ↓
unit tests
  ↓
lint/type checks
  ↓
dependency/security checks
  ↓
build
  ↓
deploy
```

The specific tools can vary by organization.

The important architecture principle is:

```text
dependency state
    ↓
validated before deployment
```

Useful checks include:

- lock consistency;
- successful clean installation;
- dependency compatibility;
- test suite;
- vulnerability reporting;
- package source policy.

## 84. Secrets and Dependencies

Dependencies can become dangerous when combined with secrets.

For example:

```text
CI environment
   ↓
secret token
   ↓
third-party package code
```

If arbitrary or untrusted code runs in a highly privileged environment, the potential impact is larger.

Therefore:

- do not place unnecessary secrets in developer environments;
- keep CI permissions minimal;
- avoid executing untrusted package code in privileged contexts;
- separate build and deployment permissions where practical.

This is an example of least-privilege thinking applied to dependency management.

## 85. Install-Time Code and Risk

Package installation and build workflows can involve build backends or package build logic. That means installation is not purely passive file copying in every packaging scenario.

The safe mental model is:

> **Installing software is itself a trust decision.**

Defensive habits:

```text
verify project
+
verify source
+
use trusted environment
+
limit privileges
+
review dependency changes
+
avoid arbitrary installation commands
```

Do not copy random shell commands from an unknown source and run them with elevated privileges.

This chapter intentionally stays at the defensive level.

## 86. Least-Privilege Thinking

Least privilege means granting software only the access it actually needs.

Applied to dependency workflows:

```text
developer environment
    → normal user privileges when possible

CI job
    → only required repository/build permissions

deployment
    → only required runtime permissions

dependency installation
    → controlled sources and limited credentials
```

The fewer privileges a compromised dependency can access, the smaller the blast radius.

This is a security design principle, not a Python-specific feature.

## 87. Dependency Inventory

A production team should be able to answer:

```text
What packages are we using?
Which versions?
Which are direct?
Which are transitive?
Which Python versions do we support?
Where do packages come from?
When were dependencies last reviewed?
```

An inventory is useful for:

- incident response;
- vulnerability response;
- upgrade planning;
- auditing;
- migration work.

Useful sources include:

```text
pyproject.toml
lockfile
dependency tree
environment inspection
build artifacts
```

The key principle is visibility.

## 88. Software Bill of Materials — Conceptual Introduction

A Software Bill of Materials (SBOM) is an inventory of software components included in a software product.

Conceptually:

```text
Application
├── component A
├── component B
├── transitive C
└── transitive D
```

An SBOM can help answer:

> “Which components are present?”

That is related to, but broader than, simply maintaining a top-level dependency list.

This chapter only needs the concept:

```text
inventory
→ provenance
→ vulnerability response
→ dependency operations
```

Detailed SBOM formats and tooling belong in later security/platform work.

## 89. Production Dependency Policy

A simple production dependency policy might say:

```text
1. Declare dependencies explicitly.
2. Use an appropriate lock mechanism for applications.
3. Review dependency changes.
4. Test upgrades.
5. Maintain dependencies regularly.
6. Monitor known vulnerabilities.
7. Avoid unnecessary dependencies.
8. Prefer trusted package sources.
9. Keep rollback possible.
10. Separate runtime and development dependencies appropriately.
```

Each rule exists because dependency state changes over time.

A policy is most useful when it is executable:

```text
policy
   ↓
tooling
   ↓
CI checks
   ↓
review habits
```

A policy nobody can follow is documentation, not operational control.

## 90. Common Dependency Management Anti-Patterns

| Anti-pattern | Problem | Better approach |
|---|---|---|
| Randomly installing packages | Unrecorded environment state | Declare dependencies |
| No lock information | More variability | Use appropriate lock workflow |
| Blind broad upgrades | Large debugging surface | Upgrade deliberately |
| Never upgrading | Dependency debt | Maintain continuously |
| Pin forever | Stale software | Refresh deliberately |
| Trusting package names | Typosquatting risk | Verify identity |
| Ignoring transitive dependencies | Hidden risk | Inspect graph |
| Skipping tests | Compatibility surprises | Test |
| Ignoring release notes | Missed behavior changes | Read changelog |
| Shipping dev-only packages | Unnecessary runtime surface | Separate dependency purpose |
| Unknown package sources | Supply-chain risk | Controlled source policy |
| Assuming lock = security | False confidence | Layered controls |

The central anti-pattern behind all of these is:

> **Treating dependencies as passive installation artifacts instead of active parts of the system.**

## 91. Real-World Python Examples

### Example: a small CLI

```text
my-cli
├── requests
├── rich
└── pytest (development)
```

Runtime and development purposes are different.

### Example: data-processing application

```text
pipeline
├── pandas
├── pyarrow
├── database driver
├── cloud SDK
└── validation library
```

A change in any one of these can affect data types, serialization, performance, or runtime behavior.

### Example: internal tool

```text
tool
├── HTTP client
├── configuration library
└── CLI framework
```

If the tool is deployed into automation, dependency reproducibility becomes operationally important because a different environment can produce a different command outcome.

The lesson across all three:

```text
code + dependencies + environment
```

is the actual executable system.

## 92. Applied AI Engineering Examples

Applied AI systems often have larger dependency graphs than beginner projects.

### LLM application

```text
application
├── model/API SDK
├── HTTP client
├── validation library
├── serialization
└── logging
```

An SDK upgrade may affect:

- request construction;
- response parsing;
- authentication behavior;
- model configuration;
- error handling.

### RAG application

```text
RAG
├── document parser
├── tokenizer
├── embedding client
├── vector database client
└── application framework
```

### Data/ML pipeline

```text
pipeline
├── pandas
├── pyarrow
├── database driver
├── cloud SDK
└── validation
```

### AI evaluation system

```text
evaluation
├── dataset loader
├── model client
├── parsing/serialization
├── metrics library
└── reporting
```

The larger the graph, the more important it becomes to understand:

```text
direct
+
transitive
+
resolved
+
tested
```

## 93. Production Upgrade Workflow

Use this as a repeatable operating procedure.

### Phase A — Understand

```text
Why are we upgrading?
Which package?
Which versions are affected?
```

### Phase B — Inspect

```text
current declaration
current lock state
dependency tree
release notes
Python compatibility
```

### Phase C — Change

```text
targeted or deliberate upgrade
```

### Phase D — Prove

```text
clean installation
unit tests
integration tests
static checks
important workflows
performance checks when needed
```

### Phase E — Review

```text
pyproject diff
lock diff
source/provenance changes
security impact
```

### Phase F — Operate

```text
commit
deploy
observe
rollback if needed
```

This is the lifecycle you should be able to explain in an interview and use in a real project.

## 94. Debugging Dependency Problems

Use a disciplined debugging workflow.

```text
1. Identify the failing command
2. Identify the Python interpreter/environment
3. Inspect the declared dependency
4. Inspect the resolved version
5. Inspect the dependency tree
6. Read the error message
7. Check release notes
8. Compare Python versions
9. Check optional/group dependencies
10. Reproduce in a clean environment
11. Decide whether code or dependency constraints should change
12. Add regression coverage
```

The first principle is:

> **Diagnose the environment before changing it.**

Repeatedly installing packages into the same stale environment can hide the real cause.

When possible, reproduce from the project's declared and lock state rather than a hand-modified environment.

## 95. Complete Production Example — Safe Dependency Upgrade

Imagine:

```text
Current:
requests 2.31.x

Desired:
latest compatible 2.x release
```

Step 1: understand the reason.

```text
Security fix?
Bug fix?
Python support?
Feature?
```

Step 2: inspect the graph.

```bash
uv tree
```

Step 3: read release notes.

Step 4: perform a targeted upgrade:

```bash
uv lock --upgrade-package requests
uv sync
```

Step 5: run tests.

Step 6: inspect the lock diff.

Step 7: run the application's important workflow.

Step 8: commit the dependency change so that rollback is easy.

The exact target version is intentionally omitted here because dependency versions change over time. The engineering method is the reusable lesson.


### Concrete Python application

Assume the application validates a small JSON request using `pydantic`.

`app.py`:

```python
from __future__ import annotations

import sys

from pydantic import BaseModel, Field


class Request(BaseModel):
    name: str = Field(min_length=1)
    count: int = Field(ge=1, le=100)


def run(payload: dict[str, object]) -> str:
    request = Request.model_validate(payload)
    return f"{request.name}: {request.count}"


def main() -> int:
    payload = {"name": "demo", "count": 3}

    try:
        print(run(payload))
    except Exception as exc:
        print(f"Application error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

The important lesson is not the particular validation library. It is that dependency upgrades must be tested against actual application behavior.

After upgrading a dependency:

```bash
uv run python app.py
```

Then run the project's test suite:

```bash
uv run pytest
```

A small test:

```python
from app import run


def test_run_valid_payload() -> None:
    assert run({"name": "demo", "count": 3}) == "demo: 3"
```

A validation test:

```python
import pytest

from app import run


def test_run_rejects_invalid_payload() -> None:
    with pytest.raises(ValueError):
        run({"name": "", "count": 3})
```

The exact exception class exposed by a third-party validation library can be a compatibility surface. That is precisely why application tests matter during dependency upgrades.

### Example `pyproject.toml`

```toml
[project]
name = "dependency-health-demo"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2,<3",
]

[dependency-groups]
dev = [
    "pytest>=8,<9",
    "ruff>=0.12,<0.13",
]
```

The dependency declarations intentionally use broad compatibility windows while the lock file records the concrete environment chosen by the resolver.

### Review sequence

```bash
uv tree
uv lock
uv sync
uv run pytest
uv run ruff check .
```

For a targeted upgrade:

```bash
uv lock --upgrade-package pydantic
uv sync
uv run pytest
uv run ruff check .
```

Then review the `uv.lock` diff before merging.

**Production Note:** The `except Exception` shown in this deliberately small CLI boundary is not a recommendation to hide bugs. It is a top-level example where the program converts an unhandled application failure into a non-zero process result. In a real project, diagnostic logging, error classification, and a controlled exception boundary would be designed explicitly.

## 96. Compatibility Failure Walkthrough

Suppose an upgrade produces:

```text
AttributeError:
module 'library' has no attribute 'old_api'
```

Do not immediately pin the old version forever.

Investigate:

```text
Was the API removed?
Was it renamed?
Was it deprecated?
Did our import path change?
Did the major/minor version change?
```

Then:

```text
read release notes
      ↓
confirm behavior
      ↓
update application if appropriate
      ↓
test
```

A temporary version constraint can be a legitimate containment step, but it should be accompanied by a maintenance decision.

## 97. Security Advisory Walkthrough

Imagine a scanner identifies:

```text
transitive dependency C
```

Do not conclude immediately:

> “Production is compromised.”

Instead:

```text
1. Identify affected versions.
2. Identify the resolved version.
3. Find which direct dependency introduced C.
4. Determine whether C is used by the affected code path.
5. Check whether an upgraded direct dependency resolves the issue.
6. If necessary, constrain C explicitly only when appropriate.
7. Test the resulting graph.
8. Record the remediation.
```

This prevents two opposite mistakes:

```text
ignore everything
```

and:

```text
panic over every advisory without investigation
```

Security work is evidence-driven.

## 98. Dependency Review Checklist for Pull Requests

For a dependency-change pull request, ask:

```text
[ ] Why is the dependency changing?
[ ] Is the change targeted?
[ ] Were release notes reviewed?
[ ] Did Python compatibility change?
[ ] Did direct requirements change?
[ ] Did transitive packages change?
[ ] Did package sources change?
[ ] Did tests pass?
[ ] Did important integration workflows pass?
[ ] Did performance-sensitive paths change?
[ ] Was a known vulnerability involved?
[ ] Is rollback obvious?
```

This checklist is small enough to use repeatedly.

## 99. Exercise Set — Beginner

The following exercises are intentionally practical. All solutions remain in this file.

### Exercise 1 — Identify Dependencies

**Problem:** Given:

```python
import json
import pathlib
import requests
import logging
```

Classify the imports as standard library or third party.

**Requirements**

- Give one answer per import.
- Explain why.

**Hint**

Ask whether the module ships with the normal Python standard library.

**Expected behavior**

You should identify `json`, `pathlib`, and `logging` as standard-library modules and `requests` as a third-party project.

**Solution**

```text
json      → standard library
pathlib   → standard library
requests  → third party
logging   → standard library
```

**Explanation**

The classification is about where the code comes from, not how important it is.

**Common Mistake**

Assuming every import requires a `pip install`.

---

### Exercise 2 — Read Version Constraints

**Problem:** Explain:

```text
pydantic>=2.0,<3
```

**Solution**

It requests a version at least `2.0` but below `3`.

**Why It Matters**

This is a bounded compatibility window. It is more expressive than blindly pinning a single version.

---

### Exercise 3 — Direct or Transitive?

**Problem**

```text
my-app
 ├── A
 │    └── C
 └── B
      └── D
```

Is `C` direct or transitive?

**Solution**

`C` is transitive because the application receives it through `A`.

---

### Exercise 4 — Package vs Import Name

**Problem**

Why should a developer not assume the installation name is identical to the import name?

**Solution**

Python distributions and importable modules use related but independent naming systems. A project's distribution name may contain hyphens or otherwise differ from the Python import name.

## 100. Exercise Set — Intermediate

### Exercise 5 — Design a Dependency Declaration

**Problem**

Your application requires:

```text
Python 3.12+
requests in the 2.x line
```

Write a basic declaration.

**Solution**

```toml
[project]
name = "example-app"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "requests>=2,<3",
]
```

**Explanation**

The declaration communicates the supported Python version and a bounded dependency range.

---

### Exercise 6 — Inspect a Dependency Tree

**Problem**

You discover a new package named `D` in the lock diff.

What command would you use in a modern `uv` project to inspect the project graph?

**Solution**

```bash
uv tree
```

Then determine which package introduced `D`.

---

### Exercise 7 — Targeted Upgrade

**Problem**

You need to upgrade only `requests`.

**Solution**

```bash
uv lock --upgrade-package requests
uv sync
```

**Why It Matters**

A targeted upgrade reduces the change surface when only one dependency needs attention. Current `uv` documentation explicitly supports this workflow.

---

### Exercise 8 — Dependency Conflict

**Problem**

```text
A requires C <2
B requires C >=2
```

Can one version of `C` satisfy both requirements?

**Solution**

No. The ranges do not overlap.

---

### Exercise 9 — Dev Dependency

**Problem**

Your package requires `pytest` only for local testing.

Which conceptual category should it belong to?

**Solution**

A development dependency, not a runtime dependency.

With current `uv` workflows, a common declaration is a `dev` dependency group.

## 101. Exercise Set — Advanced

### Exercise 10 — Review a Dependency Diff

**Problem**

```text
Before:
A 1.4
B 2.3
C 5.1

After:
A 1.5
B 2.4
C 5.2
D 0.8
```

List four questions you would ask before approving.

**Solution**

```text
Why did A change?
Why did B change?
Why did C change?
Which dependency introduced D?
```

Additional useful questions include whether Python compatibility changed, whether release notes explain the changes, and whether the new graph introduces a security concern.

---

### Exercise 11 — Rollback

**Problem**

A dependency upgrade breaks production. What should your upgrade workflow have made easy?

**Solution**

Returning to the previous known-good dependency and lock state, rebuilding the environment, and redeploying through the normal release mechanism.

---

### Exercise 12 — Transitive Vulnerability

**Problem**

A scanner reports a vulnerability in a package you do not directly declare.

**Solution**

Find the direct dependency that introduces it, determine whether your resolved version is affected, evaluate application relevance, and choose a remediation such as upgrading the introducing dependency or otherwise changing constraints.

---

### Exercise 13 — Supply-Chain Review

**Problem**

You find a package with a name very similar to the package you intended.

**Solution**

Stop before installing it. Verify the official project name and source. Do not rely on visual similarity.

**Production Lesson**

Package naming is not proof of identity.

## 102. Mini-Project — Python Dependency Health and Upgrade Workflow

## Project Goal

Create a small production-oriented application whose dependency lifecycle can be inspected, tested, upgraded, and rolled back.

The project is described here but must remain self-contained inside this Markdown chapter.

## Requirements

The project should contain conceptually:

```text
pyproject.toml
application code
tests
lock information
documented upgrade procedure
```

The application can be a small JSON document processor.

Runtime dependency example:

```text
pydantic
```

Development dependencies:

```text
pytest
ruff
```

## Architecture

```text
Developer
   ↓
pyproject.toml
   ↓
uv resolution
   ↓
uv.lock
   ↓
uv sync
   ↓
clean environment
   ↓
tests
   ↓
application
```

## Step 1 — Initialize

```bash
uv init dependency-health-demo
cd dependency-health-demo
```

## Step 2 — Add runtime dependency

```bash
uv add pydantic
```

## Step 3 — Add development tools

```bash
uv add --dev pytest
uv add --dev ruff
```

## Step 4 — Inspect

```bash
uv tree
```

## Step 5 — Synchronize

```bash
uv sync
```

## Step 6 — Write tests

Test:

```text
valid input
invalid input
serialization
CLI behavior if added
```

## Step 7 — Perform a targeted upgrade

```bash
uv lock --upgrade-package pydantic
uv sync
```

## Step 8 — Review

Inspect:

```text
pyproject.toml
uv.lock
uv tree
test results
```

## Step 9 — Record rollback

Your release notes for the project should say:

```text
Previous known-good dependency state:
<version-control reference>

Rollback:
restore previous pyproject.toml/uv.lock state
sync clean environment
run tests
```

## Expected Learning Outcome

You should be able to explain the complete lifecycle:

```text
declare
→ resolve
→ lock
→ sync
→ inspect
→ upgrade
→ test
→ review
→ deploy
→ rollback
```

## Production Improvements

For a larger real system, add:

- automated dependency checks;
- vulnerability scanning;
- CI installation from controlled lock state;
- reproducible build environments;
- staged deployment;
- SBOM generation;
- dependency ownership;
- upgrade SLAs;
- rollback automation.

Those are extensions of the core habit, not replacements for it.

## 103. Interview Questions — Basic

### Question 1 — What is a dependency?

**How to Think**

Think about software your program relies on but does not implement itself.

**Answer**

A dependency is another software project/component required by your application to provide functionality.

**Why It Matters**

Dependencies are part of the application's operational environment.

---

### Question 2 — What is a direct dependency?

**Answer**

A project the application explicitly declares.

**Why It Matters**

Direct dependencies define the top-level requirements of the application.

---

### Question 3 — What is a transitive dependency?

**Answer**

A dependency required indirectly through another dependency.

**Why It Matters**

Transitive packages can affect compatibility and security even when you never import them directly.

---

### Question 4 — What is a lock file?

**Answer**

A file that records concrete dependency resolution so an environment can be reproduced more reliably.

**Why It Matters**

It reduces accidental version drift.

---

### Question 5 — What is Semantic Versioning?

**Answer**

A versioning convention using major, minor, and patch components with intended compatibility semantics.

**Why It Matters**

It gives engineers useful signals, but release notes and tests remain necessary.

## 104. Interview Questions — Intermediate

### Question 6 — Why can “works on my machine” happen?

**Answer**

Because local environments can contain different dependency versions, Python versions, optional packages, platform behavior, or unrecorded state.

**Why It Matters**

Reproducible project state reduces environment drift.

### Question 7 — What is the difference between declared and resolved dependencies?

**Answer**

A declaration specifies acceptable requirements. Resolution selects concrete versions satisfying the full graph.

### Question 8 — Why read release notes before upgrading?

**Answer**

Because the version number alone does not tell you which APIs, defaults, dependencies, or behaviors changed.

### Question 9 — Why is `except`-style rollback not enough?

**Answer**

Because dependency problems are environment changes. You need to restore the known-good dependency graph, not merely catch a runtime exception.

### Question 10 — Why can a transitive dependency be a security concern?

**Answer**

Because the transitive package is still installed and can execute or influence runtime behavior.

## 105. Interview Questions — Advanced

### Question 11 — How would you safely upgrade one dependency?

**Answer**

Establish the current state, read release notes, check compatibility, perform a targeted upgrade, review the lock diff, run functional checks, verify critical workflows, and keep rollback easy.

### Question 12 — What is dependency resolution?

**Answer**

It is the process of selecting concrete package versions that satisfy the complete set of applicable dependency constraints.

### Question 13 — Why does a lock file not solve security?

**Answer**

A lock file reproduces a chosen dependency state; it does not prove that the packages are vulnerability-free, trustworthy, correctly configured, or used safely.

### Question 14 — How would you handle a vulnerable transitive dependency?

**Answer**

Identify the affected resolved version, trace which direct dependency introduces it, determine application relevance, and choose a tested remediation path.

### Question 15 — How would you debug a failed dependency upgrade?

**Answer**

Reproduce in a clean environment, inspect the resolver error or application traceback, inspect the dependency tree and lock diff, read the relevant release notes, and classify the failure before deciding whether to update code, constraints, or the dependency set.

## 106. Architecture Questions

### 1. How would you manage dependencies for a production RAG service?

**Answer**

Use explicit project declarations, a lock workflow, reproducible environment creation, separated runtime/dev dependencies, dependency inspection, automated checks, and staged upgrades. Keep package sources controlled and make rollback to a known-good graph straightforward.

### 2. How would you ensure reproducible deployments?

**Answer**

Version-control the application source, dependency declarations, lock state, Python version policy, and build instructions. Install from the declared/locked state in clean environments rather than relying on pre-existing machine state.

### 3. How would you handle a vulnerable transitive dependency?

**Answer**

Trace its origin, confirm affected versions, evaluate relevance, identify compatible remediation, update and lock the resulting graph, run the appropriate tests, and document the decision.

### 4. How would you design dependency upgrade automation?

**Answer**

Create automated proposals for dependency changes, run a comprehensive CI gate, require review for important changes, and keep the update scope understandable.

### 5. How would you prevent unreviewed dependency changes reaching production?

**Answer**

Require dependency changes to flow through version control and CI, validate lock consistency, apply dependency/security policies, and prevent production deployment from using unmanaged environments.

### 6. How would you separate runtime and development dependencies?

**Answer**

Declare runtime requirements in project dependencies and use development-oriented dependency groups for tools that are not needed by the production application.

### 7. How would you design rollback?

**Answer**

Keep the previous known-good lock state and build/deployment artifact identifiable and reproducible, then restore that exact state and verify the deployment.

### 8. How would you manage dev/staging/prod?

**Answer**

Keep a common dependency specification and lock strategy where practical, vary only environment-specific configuration, and verify the exact artifacts deployed to each environment.

### 9. What would you do when two libraries conflict?

**Answer**

Identify the shared dependency and requirement ranges, determine whether a compatible version exists, and if not, decide whether to upgrade one parent package, constrain a dependency, or replace a library.

### 10. How would you maintain dependencies across many AI services?

**Answer**

Centralize policy, automate inventory and checks, define ownership, standardize upgrade workflows, measure dependency age and advisory exposure, and avoid forcing identical versions when services have legitimate compatibility differences.

### 11. How would you investigate an unexpected new transitive dependency?

**Answer**

Inspect the dependency tree and lock diff, find the introducing parent package, read its release notes, and decide whether the new package is expected and acceptable.

### 12. How would you establish a dependency policy?

**Answer**

Define declaration, locking, source, review, testing, vulnerability-response, ownership, and rollback requirements; then encode critical parts in CI.

## 107. Knowledge Check

Answer these without looking back.

### Conceptual

1. Why is a dependency part of your software system?
2. Why are transitive dependencies important?
3. What is the difference between declaration and resolution?
4. Why can two machines have different environments even with the same source code?
5. Why is a lock file useful?

### Version Resolution

6. What versions can satisfy:

```text
A>=2,<3
```

7. What happens if one package requires `C<2` and another requires `C>=2`?
8. Why is `==` not automatically the best dependency strategy?
9. Why does SemVer not replace testing?

### `uv`

10. What does `uv add` do?
11. What does `uv sync` do?
12. What does `uv tree` help you inspect?
13. What is the difference between `uv lock --upgrade` and `uv lock --upgrade-package <package>`?

### Supply Chain

14. What is typosquatting?
15. What is dependency confusion?
16. Why can a legitimate package become risky if its maintainer account is compromised?
17. Why can a transitive package matter to security?
18. What does a hash contribute?
19. Why is a hash not proof of trust?
20. What is an SBOM?

### Scenario

Imagine:

```text
App
├── A
│   └── C
└── B
    └── C
```

Then an upgrade of `A` changes `C`.

**Question:** What should you inspect before merging?

**Answer**

At minimum:

```text
A release notes
C version change
dependency tree
lock diff
tests
important workflows
security impact
rollback path
```

### Scenario

Your CI succeeds, but production fails after an upgrade.

**Answer**

Investigate differences in:

```text
Python version
OS/platform
dependency resolution
environment configuration
optional groups
runtime-only dependencies
```

The fact that CI passed is useful evidence, but not proof that production is identical.


### A small dependency-reporting script

A Python program can print the versions of packages that are important to a workflow:

```python
from importlib.metadata import PackageNotFoundError, version


REQUIRED_DISTRIBUTIONS = (
    "pydantic",
    "requests",
)


def report_versions(names: tuple[str, ...]) -> None:
    for name in names:
        try:
            installed = version(name)
        except PackageNotFoundError:
            installed = "<not installed>"
        print(f"{name}=={installed}")


if __name__ == "__main__":
    report_versions(REQUIRED_DISTRIBUTIONS)
```

This is useful when diagnosing a runtime environment, but the report should be treated as evidence about that environment rather than as the source of truth for the project's dependency policy.

## 108. Completion Checklist

### Fundamentals

- [ ] I understand what a dependency is.
- [ ] I understand standard-library vs third-party dependencies.
- [ ] I understand package names vs import names.
- [ ] I understand direct dependencies.
- [ ] I understand transitive dependencies.
- [ ] I can read a dependency graph.
- [ ] I understand why dependency management matters.

### Project Metadata

- [ ] I understand `pyproject.toml`.
- [ ] I understand `[project]`.
- [ ] I understand `requires-python`.
- [ ] I understand `project.dependencies`.
- [ ] I understand optional dependencies.
- [ ] I understand dependency groups.

### Versioning

- [ ] I understand version specifiers.
- [ ] I understand exact pins.
- [ ] I understand minimum versions.
- [ ] I understand bounded ranges.
- [ ] I understand compatible-release specifiers.
- [ ] I understand Semantic Versioning and its limitations.
- [ ] I understand pre-release concepts.

### Resolution and Reproducibility

- [ ] I understand dependency resolution.
- [ ] I understand dependency conflicts.
- [ ] I understand declared vs resolved dependencies.
- [ ] I understand lock files.
- [ ] I understand `uv.lock`.
- [ ] I understand why reproducibility matters.
- [ ] I can reason about “works on my machine.”

### `uv`

- [ ] I can use `uv init`.
- [ ] I can use `uv add`.
- [ ] I can use `uv remove`.
- [ ] I can use `uv lock`.
- [ ] I can use `uv sync`.
- [ ] I can use `uv tree`.
- [ ] I understand targeted upgrades.
- [ ] I understand broad upgrades.
- [ ] I know how to inspect environment state.

### Safe Upgrades

- [ ] I know why release notes matter.
- [ ] I check Python compatibility.
- [ ] I review dependency diffs.
- [ ] I run unit tests.
- [ ] I run integration tests.
- [ ] I run static checks.
- [ ] I benchmark important workflows when appropriate.
- [ ] I keep rollback possible.

### Supply Chain

- [ ] I understand typosquatting.
- [ ] I understand dependency confusion conceptually.
- [ ] I understand malicious packages.
- [ ] I understand compromised maintainer accounts.
- [ ] I understand compromised releases.
- [ ] I understand abandoned dependencies.
- [ ] I understand vulnerable dependencies.
- [ ] I understand transitive dependency risk.
- [ ] I understand provenance.
- [ ] I understand package integrity and hashes conceptually.
- [ ] I understand vulnerability scanning.
- [ ] I understand automated dependency updates.
- [ ] I understand CI dependency checks.
- [ ] I understand least-privilege thinking.
- [ ] I understand dependency inventory.
- [ ] I understand SBOM conceptually.

### Applied AI

- [ ] I can apply dependency-management thinking to an LLM application.
- [ ] I can reason about dependencies in a RAG system.
- [ ] I can manage dependencies in a data pipeline.
- [ ] I can review an AI SDK upgrade.
- [ ] I can trace a transitive dependency in an AI project.

### Production Mindset

- [ ] I treat dependencies as part of the system.
- [ ] I can explain why installation success does not prove compatibility.
- [ ] I can explain why locking does not replace security controls.
- [ ] I can perform a controlled upgrade.
- [ ] I can investigate a dependency conflict.
- [ ] I can roll back to a known-good dependency graph.

## 109. Final Self-Review and File-Scope Verification

## Self-Review

The chapter was reviewed against the requested scope.

### Content coverage

- beginner dependency foundations;
- standard library vs third party;
- package/import naming;
- direct and transitive dependencies;
- dependency graphs;
- package ecosystem;
- `pyproject.toml`;
- project metadata;
- version specifiers;
- exact/minimum/ranged constraints;
- upper bounds;
- pinning;
- Semantic Versioning;
- pre-releases;
- resolution and conflicts;
- reproducibility;
- lock files;
- declared vs resolved dependencies;
- `uv` project workflow;
- runtime/development/optional/group dependencies;
- upgrade strategies;
- release-note review;
- testing and static checks;
- integration and performance checks;
- dependency diffs;
- rollback;
- supply-chain awareness;
- typosquatting;
- dependency confusion;
- malicious/compromised packages;
- abandoned dependencies;
- vulnerable transitive packages;
- provenance and integrity;
- hashes;
- vulnerability scanning;
- automated updates;
- CI/CD controls;
- secrets and least privilege;
- inventory and SBOM;
- Applied AI examples;
- production workflow;
- debugging;
- exercises and solutions;
- mini-project;
- interview questions;
- architecture questions;
- knowledge check;
- completion checklist.

### Technical accuracy notes

- Dependency declarations are distinguished from resolved versions.
- Direct and transitive dependencies are distinguished.
- SemVer is treated as a convention/specification rather than a guarantee.
- Exact pinning is presented as a trade-off.
- Lock files are presented as reproducibility controls, not complete security solutions.
- `uv add`, `uv remove`, `uv sync`, `uv lock`, `uv lock --upgrade`, `uv lock --upgrade-package`, and `uv tree` are described according to current official `uv` documentation.
- `[project.optional-dependencies]` is distinguished from standardized `[dependency-groups]`.
- Supply-chain discussion is defensive and does not provide exploitation instructions.
- No current package vulnerability is asserted as fact without a current advisory source.

### File-scope verification

This task's intended modification is only:

```text
Programming & Computational Thinking/
└── 10-Production-Habits-for-Python-Programs/
    └── 07-dependency-upgrades-and-supply-chain-awareness.md
```

No additional Markdown, Python, project, configuration, or folder artifacts are intentionally created by this chapter-generation task.

**Final Mental Model**

```text
DEPENDENCIES ARE PART OF THE SYSTEM
              ↓
declare
              ↓
resolve
              ↓
lock
              ↓
sync
              ↓
inspect
              ↓
upgrade deliberately
              ↓
test
              ↓
review graph + provenance
              ↓
deploy
              ↓
monitor
              ↓
rollback when necessary
```

A production Python engineer does not merely know how to install a package.

A production Python engineer knows how to **operate dependency state responsibly over time**.


# Official References Consulted

For version-sensitive packaging and `uv` behavior, consult the current official documentation:

- Python Packaging User Guide — `pyproject.toml`: https://packaging.python.org/en/latest/specifications/pyproject-toml/
- Python Packaging User Guide — dependency specifiers: https://packaging.python.org/en/latest/specifications/dependency-specifiers/
- Python Packaging User Guide — version specifiers: https://packaging.python.org/en/latest/specifications/version-specifiers/
- Python Packaging User Guide — dependency groups: https://packaging.python.org/en/latest/specifications/dependency-groups/
- `uv` project guide: https://docs.astral.sh/uv/guides/projects/
- `uv` dependency management: https://docs.astral.sh/uv/concepts/projects/dependencies/
- `uv` locking and syncing: https://docs.astral.sh/uv/concepts/projects/sync/
- `uv` command reference: https://docs.astral.sh/uv/reference/cli/

These references are provided because package-manager commands and security practices can evolve. When working on a real production repository, prefer the documentation version that matches the tools installed in that repository.
