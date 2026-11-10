# 04 — Dependency Management and Semantic Versioning
## Complete Chapter Summary, Project-Tree Review, Exercises, Debugging, and Review Answers

**Roadmap:** Stage 1 — Programming & Computational Thinking  
**Module:** 06 — Modules, Packages, Dependencies, and Code Quality  
**Lesson:** 04 — Dependency Management and Semantic Versioning  
**Prerequisite:** Lesson 03 — `pyproject.toml`, Lock Files, and `uv`

---

# Part A — Complete Chapter Summary

## 1. What dependency management means

A **dependency** is external code your project needs but does not implement itself. Dependency management is the ongoing engineering discipline of deciding which packages a project uses, which versions it accepts, and how those decisions remain correct as the project and its dependencies evolve.

Important terms:

- **Direct dependency:** a package your project itself declares as required. If your code imports `requests`, it is normally a direct dependency.
- **Transitive dependency:** a package required by one of your direct dependencies. For example, `requests` depends on other packages such as `urllib3`.
- **Version:** a specific release, such as `2.31.0`.
- **Constraint:** a rule describing acceptable versions, such as `>=2.0`.

```text
your application
    └── requests          direct dependency
          └── urllib3     transitive dependency
```

Your application normally declares `requests`, not every package that `requests` itself needs. The dependency resolver calculates the complete graph, and the lock file records the selected versions.

A one-time `pip install requests` is not enough for a real project: it does not provide a durable record of which version was installed, does not ensure teammates install the same version, and does not define a safe update process.

## 2. Why dependency management matters

Without deliberate dependency management, a data-processing CLI can encounter:

- **Works on my machine:** developers have different package versions.
- **Incompatible versions:** two dependencies require mutually exclusive versions of a shared package.
- **Missing packages:** someone manually installed a package but never declared it.
- **Unexpected upgrades:** a later install resolves newer versions than those originally tested.
- **Broken deployments:** production installs a different combination from development or CI.
- **Unreproducible environments:** the team cannot reliably recreate the versions running in production.
- **Security vulnerabilities:** vulnerable or outdated direct and transitive dependencies go unnoticed.
- **Dependency drift:** developer, CI, staging, and production environments gradually diverge.

The common cause is the absence of a shared, version-controlled record of the dependency state and a deliberate process for changing it. The previous lesson introduced the tools (`pyproject.toml`, `uv.lock`, `uv sync`, `uv run`); this lesson teaches the versioning judgment and update discipline.

## 3. Direct versus transitive dependencies

A longer dependency chain looks like this:

```text
Application → Package A → Package B → Package C
```

The application declares A. A declares B. B declares C. From the application's perspective, A, B, and C must all be installed and compatible, but the application normally declares only A because that is its intentional direct requirement.

Manually declaring every transitive dependency duplicates information already maintained by upstream packages. It becomes stale when an upstream package changes its own requirements. Let the resolver compute the full graph and let `uv.lock` record its resolved state.

A direct dependency is defined by the project declaring it; an import statement is a common reason, but not the only possible reason, to declare a dependency.

## 4. Dependency constraints

A version constraint describes which releases the resolver may choose.

| Constraint | Meaning |
|---|---|
| `>=2.0` | 2.0 or newer |
| `>2.0` | Strictly newer than 2.0 |
| `==2.0` | Exactly 2.0 |
| `<=2.0` | 2.0 or older |
| `<3.0` | Strictly older than 3.0 |
| `~=2.31` | `>=2.31, ==2.*`; stays in the 2.x line |
| `~=2.31.0` | `>=2.31.0, ==2.31.*`; stays in the 2.31.x line |
| `>=2.0,<3.0` | Bounded range from 2.0 up to, but excluding, 3.0 |

Multiple comma-separated constraints must all be true. For example, `requests>=2.31,<3.0` accepts versions at least 2.31 but below 3.0.

- A **minimum** says the project needs at least a certain release.
- A **maximum** says the project does not yet accept versions beyond a boundary.
- An **exact pin** accepts only one version.
- A **bounded range** combines a lower and upper boundary.
- A **compatible-release constraint** (`~=`) expresses a compatibility boundary concisely.

Very loose constraints maximize flexibility but can permit a future breaking release when the project next resolves. Exact pins maximize predictability for that declaration but increase maintenance and can create resolver conflicts. A bounded range informed by the package's versioning practices is often a useful middle ground, but not universally correct. Critical dependencies or packages with poor compatibility records may need tighter controls.

## 5. Version pinning versus lock files

Compare:

```text
package==1.4.2
package>=1.4
```

The first is an exact pin in the project declaration. The second allows newer versions in principle.

The important distinction:

- `pyproject.toml` expresses **acceptable requirements** — what the project is willing to use.
- `uv.lock` records the **resolved dependency state** — the exact versions selected for reproducible installation, potentially with different variants for different supported Python versions or platforms.

For example, `pyproject.toml` may allow `package>=1.4`, while `uv.lock` records `1.4.7` today. Future releases do not automatically change the committed lock file. A deliberate update/re-resolution must change it.

An exact declaration is not the same thing as a generated lock file. A loose declaration plus a committed lock can provide both future flexibility and a reproducible current installation.

## 6. Semantic Versioning (SemVer)

**Semantic Versioning** is a convention for communicating compatibility through a version number:

```text
MAJOR . MINOR . PATCH
  2   .   7   .   4
```

- **MAJOR:** increments when a release may break existing consumer code.
- **MINOR:** adds new backward-compatible functionality; existing use should continue working.
- **PATCH:** provides backward-compatible bug fixes only.

The intended contract is that consumers can generally adopt PATCH and MINOR releases without changing existing code, while MAJOR releases require active compatibility review.

**Critical caveat:** SemVer is a convention chosen by package maintainers. Python, `pip`, and `uv` do not enforce that a package's release actually obeys it. A mistake can put a breaking change into a MINOR or PATCH release. Treat version numbers as useful signals, not guarantees.

## 7. SemVer examples

```text
1.2.3 → 1.2.4   PATCH: bug fix
1.2.3 → 1.3.0   MINOR: new backward-compatible feature
1.2.3 → 2.0.0   MAJOR: potentially breaking change
```

Examples of a PATCH: correcting an incorrect nested-list validation result without intentionally changing the public API. A MINOR could add a new function such as `validate_partial()` while leaving existing functions unchanged. A MAJOR could rename `validate()` to `check()` and change its return behavior.

Suppose a project declares `strictjson>=1.4,<2.0`. The range permits compatible 1.x updates, but a committed lock file does not change merely because a new release appears. A deliberate lock update is required. A 2.0 release is outside the declared range and should require a deliberate migration decision.

## 8. Breaking versus non-breaking changes

Evaluate compatibility from the **consumer's perspective**: will existing code that uses the package continue to work?

Potentially breaking changes include:

- Removing a public function or class.
- Removing a parameter, changing its meaning, or changing its type incompatibly.
- Dropping support for a Python version your project still requires.
- Changing runtime behavior, such as returning `None` on failure versus raising an exception.
- Making previously optional configuration mandatory.

Generally backward-compatible changes include:

- A bug fix that restores the documented intended behavior.
- Adding a new optional feature without altering existing code paths.
- Adding a new function while leaving existing functions unchanged.

A subtle example: a library fixes `compute_total()` so it returns the correct result. A consumer had unknowingly relied on the old buggy result. The maintainer may reasonably classify the fix as PATCH, but that consumer can still break. This is why release-note review, testing, and application-behavior checks remain necessary even for PATCH and MINOR releases.

## 9. Pre-release versions

Pre-releases signal that a version is not yet the final stable release:

```text
1.0.0-alpha    early, incomplete, likely to change
1.0.0-beta     more complete, still subject to changes
1.0.0-rc.1     release candidate, believed ready but undergoing final checks
1.0.0          stable release
```

- **Alpha:** early development; substantial changes are expected.
- **Beta:** more complete, but bugs and changes are still expected.
- **Release candidate (rc):** believed ready, published for final verification.
- **Stable:** no pre-release suffix.

Production applications should treat pre-releases cautiously because their purpose is to allow change before stability commitments apply. Resolvers such as `uv` generally avoid selecting pre-releases for ordinary constraints unless explicitly requested.

## 10. Development versions and `0.x`

Under the SemVer convention, a version below `1.0.0` is still in initial development. Its API may change at any time, including between MINOR releases:

```text
0.3.0 → 0.4.0
```

This can include a breaking change, even though `1.3.0 → 1.4.0` would normally be expected to preserve existing behavior.

Practically, treat a MINOR bump of a `0.x` package with caution similar to a MAJOR bump in a stable package. Some maintainers keep pre-1.0 APIs relatively stable, but do not assume the normal SemVer compatibility promise applies until `1.0.0`.

## 11. SemVer and Python package constraints

The package's published version communicates the maintainer's compatibility intent. Your constraint encodes how much of that promise your project is willing to accept:

```toml
[project]
dependencies = [
    "requests>=2.31,<3.0",
]
```

Interpretation:

- `>=2.31`: the project needs at least the fixes/features in 2.31.
- `<3.0`: the project is willing to accept the 2.x line but wants a deliberate review before 3.0.

This is a practical use of the MAJOR boundary. The resolver evaluates this range alongside every other constraint in the project.

## 12. Dependency resolution

The resolver must find a version satisfying every constraint for a package.

A valid example:

```text
Application requires A >=2, <4
Package B requires A >=2, <3
Package C requires A >=2.5
```

The overlap is `[2.5, 3.0)`. A version in that interval satisfies all three constraints.

A conflict:

```text
Package B requires A <3
Package C requires A >=3
```

There is no overlap. No single version can be less than 3 and at least 3 simultaneously. The resolver should fail rather than create an invalid environment.

## 13. Dependency conflicts

Common causes, in likely order:

1. Direct or transitive packages require incompatible ranges of the same package.
2. A dependency's Python-version requirement conflicts with the project's supported Python version.
3. The conflict is several levels deep in the transitive graph.
4. Your own constraint is unnecessarily restrictive.

Possible fixes and trade-offs:

- Upgrade one conflicting dependency to a release with relaxed transitive requirements. Review that upgrade too.
- Relax your own constraint if it was more restrictive than necessary. This reduces a guardrail.
- Replace one dependency with an alternative. This is more disruptive.
- Reconsider whether both packages are actually needed.

Read the resolver error and identify the exact conflicting packages and ranges before changing anything. Never force a version past a genuine conflict; that hides an incompatibility rather than solving it.

## 14. Writing useful dependency declarations

Example:

```toml
[project]
dependencies = [
    "requests>=2.0,<3.0",
    "pydantic>=2.0,<3.0",
]
```

For each dependency, choose:

- A lower bound representing the earliest release with the features/fixes the project needs.
- An upper bound representing the boundary beyond which the team wants a deliberate review, often the next MAJOR version.

A range makes PATCH and MINOR releases within it eligible, but eligible does not mean automatically installed. The committed lock remains unchanged until a deliberate update. The resolver evaluates the ranges and writes its selected versions into `uv.lock`.

## 15. Lock file versus dependency declaration: four distinct operations

```text
pyproject.toml = dependency requirements (acceptable ranges)
uv.lock        = resolved dependency state
```

Keep these operations separate conceptually:

1. **Declaration:** write or edit a constraint in `pyproject.toml`.
2. **Resolution:** calculate a compatible set satisfying all constraints.
3. **Locking:** record the resolved versions in `uv.lock`.
4. **Installation/synchronization:** install those versions with `uv sync`.

Plain `uv sync` can re-lock if the lock is stale. `uv sync --locked` fails if the lock would need to change. `uv sync --frozen` uses the lock without checking whether it is current.

A widened constraint does not necessarily upgrade an already-locked package. If the old version still satisfies the new range, `uv lock` normally preserves it unless an explicit upgrade is requested.

## 16. Dependency drift

**Dependency drift** is gradual divergence between environments that should use the same dependency state.

```text
Today:                  Later, without shared locking:
A 2.1                   A 2.9
B 4.0                   B 4.8
```

A developer laptop set up today, a new laptop set up months later, CI, staging, and production can independently resolve different versions from the same loose constraints.

A committed `uv.lock`, consistently installed across environments, prevents this class of drift. Developers can use `uv sync`; CI and production should use strict lock behavior such as `uv sync --locked`.

## 17. Dependency updates

Four situations:

- **No update:** the locked version remains. This avoids immediate change but can accumulate outdated-package and security risk.
- **PATCH update:** usually the lowest-risk change under SemVer, but not zero risk.
- **MINOR update:** should add compatible functionality; still deserves review.
- **MAJOR update:** crosses a boundary that may break consumer code and requires active review/migration.

Updates should be intentional. Review release notes, compare the changes with how your application uses the dependency, inspect the lock diff (including transitive changes), run tests, and verify application behavior.

## 18. Safe update strategy — ten steps

1. Identify the exact package and target update.
2. Read its changelog/release notes.
3. Review compatibility against your own usage.
4. Change the requirement or invoke the appropriate `uv` command.
5. Resolve the full dependency graph.
6. Inspect the `uv.lock` diff, including transitive changes.
7. Run the test suite.
8. Run lint and type checks where applicable.
9. Check application behavior that tests may not cover.
10. Commit `pyproject.toml` and `uv.lock` together with a clear message explaining what changed and why.

Skipping release-note review makes the update blind. Skipping lock-diff review hides the full impact. Skipping tests or behavior checks allows regressions to reach production. Committing only one of the two dependency files can leave the repository inconsistent.

## 19. PATCH, MINOR, and MAJOR update strategy

- **PATCH:** lower risk; skim release notes and run tests.
- **MINOR:** review new functionality and any interaction with existing behavior; run the full test suite.
- **MAJOR:** read the migration guide, identify breaking changes, expect code modifications, test in a non-production environment, and use the complete review process.

The version number alone never guarantees safety. Scrutiny should scale with the risk, but never drop to zero.

## 20. Dependency rollback

Rollback is appropriate when an update causes a production problem and restoring a known-good state is safer than debugging under incident pressure.

Because `pyproject.toml` and `uv.lock` are committed, revert the commit that introduced the dependency change and redeploy the previous known-good build:

```bash
git revert <the-commit-that-updated-the-dependency>
```

The reverted build can then synchronize from its committed lock, for example:

```bash
uv sync --locked --no-dev
```

In production, normally redeploy the previous known-good artifact or rebuild from the reverted commit; do not casually mutate a live server by hand.

- **Rollback:** restore a previously verified state quickly.
- **Forward-fix:** create a new change that corrects the problem while keeping the update.

Rollback is generally safer during an active incident. Investigate calmly after service is stable; then decide whether to report the issue upstream, patch around it, or retry the update with better tests.

## 21. What the `uv` commands do in this chapter

| Command | Responsibility |
|---|---|
| `uv add package` | Declares the dependency, resolves, locks, and syncs |
| `uv remove package` | Removes the declaration and updates the resolved environment |
| `uv lock` | Resolves/updates the lock as needed; does not install packages and does not upgrade already-locked packages just because newer versions exist |
| `uv sync` | Aligns installed packages with the lock; may re-lock if stale |
| `uv run ...` | Runs a command in the project's managed environment |

Use the commands for the correct stage of the update workflow. Check `uv --help` and subcommand help because exact flags and behavior can vary by installed version.

## 22. Updating dependencies with `uv`

There are three distinct operations:

1. Change the accepted requirement.
2. Resolve and record the new state in `uv.lock`.
3. Install the locked state into the environment.

Change a requirement:

```bash
uv add "requests>=2.32,<3.0"
```

This declares the new range and normally resolves, locks, and syncs. Widening the range alone may not move the already-locked version.

To deliberately upgrade within an existing range:

```bash
uv lock --upgrade-package pydantic
```

To target a specific version, where supported by the installed `uv` version:

```bash
uv lock --upgrade-package pydantic==2.5.1
```

Then inspect the result:

```bash
git diff pyproject.toml uv.lock
```

The diff is the evidence of what the resolver changed. Verify exact CLI syntax with `uv lock --help` before relying on a particular flag.

## 23. Runtime, development, and optional dependencies

```toml
[project]
dependencies = ["requests>=2.31,<3.0"]

[dependency-groups]
dev = ["pytest>=8.0", "ruff>=0.5"]

[project.optional-dependencies]
excel = ["openpyxl>=3.0"]
```

- **Runtime:** required for the application to run; declared in `[project].dependencies`. Changes directly affect production.
- **Development:** test, lint, and type-check tools; declared in `[dependency-groups]`, such as `dev`. They are not needed by the running application.
- **Optional extra:** published opt-in feature dependencies, declared in `[project.optional-dependencies]`. Here, `openpyxl` is needed only when a user chooses Excel export.

These mechanisms are not interchangeable. CI needs development tools to run tests; production usually excludes them. An optional dependency only matters to users who enable the relevant feature.

## 24. Application versus library dependency strategy

**Application:**
- The team controls its own deployment.
- A committed lock file is highly valuable.
- Tighter, well-reviewed bounded ranges are reasonable because the application has one deployment environment to satisfy.

**Library:**
- Many downstream projects consume it and resolve its requirements alongside their own.
- Overly tight dependency constraints can create unnecessary conflicts for consumers.
- Prefer minimally restrictive, well-considered compatibility ranges. A library can still keep a lock file for its own development and CI; consumers do not use that development lock to resolve their projects.

The application optimizes its own reproducibility. The library must avoid unnecessarily restricting downstream consumers.

## 25. Dependency security and supply-chain risk

- **Vulnerable dependency:** a direct or transitive package with a known security flaw. Investigate exploitability based on the affected functionality and how the application exposes it.
- **Outdated package:** may miss fixes and security updates.
- **Transitive vulnerability:** a flaw several levels deep is still a real risk, even if your code never imports that package directly.
- **Supply-chain risk:** a dependency or one of its dependencies is compromised and introduces malicious code rather than merely a bug.
- **Typosquatting:** a malicious package uses a name similar to a popular package, hoping a developer mistypes it.
- **Source trust:** know where packages come from; prefer trusted, established sources.

Defensive practices: verify package names, review maintenance and trustworthiness before adding packages, keep a known dependency inventory, monitor security advisories, update deliberately, and test the resulting changes. Neither blind upgrades nor never upgrading is safe.

## 26. Python/platform compatibility

A dependency works only when several dimensions line up:

```text
Python version + package version + OS/platform + CPU architecture
```

Packages with compiled components may not provide a compatible build for every platform or architecture. A new package release may also drop support for an older Python version.

Your project's `requires-python` must be compatible with every dependency's own supported Python versions. If a dependency raises its minimum Python version above yours, either use an older compatible dependency release or deliberately raise your project's Python minimum after checking every other dependency and your own code.

## 27. Dependency graph thinking

Dependencies form a graph, not a flat list:

```text
Application
├── A
│   ├── B
│   └── C
└── D
    └── C
```

C is shared by A and D. If A requires `C<2.0` and D requires `C>=2.0`, the graph contains a conflict even though A and D do not directly depend on each other.

Every direct dependency can bring a subtree of transitive packages. As the project grows, the number of possible conflicts, compatibility questions, and security exposures grows too. This is why a resolver and lock file are engineering necessities rather than optional convenience.

## 28. Fifteen common mistakes

1. **Installing globally:** pollutes system Python. Use the project's managed environment.
2. **Not declaring a dependency:** a clean sync will not preserve a manual install. Use `uv add`.
3. **Pinning every transitive dependency manually:** duplicates upstream metadata. Declare your direct dependencies and let the resolver manage the rest.
4. **Blindly upgrading everything:** can introduce unreviewed breakage. Update deliberately.
5. **Never upgrading:** leaves vulnerabilities unpatched and makes later catch-up harder. Review periodically.
6. **Treating SemVer as a guarantee:** the version is a signal, not enforced proof. Always test.
7. **Ignoring pre-releases:** alpha/beta/rc versions may change. Keep them out of production unless there is a deliberate reason.
8. **Ignoring Python compatibility:** a package may no longer support your project's interpreter. Check `requires-python`.
9. **Ignoring lock diffs:** transitive packages may change too. Review the complete diff.
10. **Editing `uv.lock` by hand:** can create inconsistent generated state. Change declarations and re-lock.
11. **Resolving but not testing:** a successful resolution proves constraint compatibility, not your application's behavior. Run tests.
12. **Ignoring security updates:** leaves known risk active. Prioritize genuine advisories.
13. **Overly strict constraints:** can block valid resolutions and increase maintenance. Use justified ranges.
14. **Overly loose constraints:** can admit an unreviewed major release. Add a deliberate upper boundary where appropriate.
15. **Assuming PATCH/MINOR is risk-free:** SemVer is not a guarantee. Test every update.

## 29. All 14 progressive coding/configuration examples

1. Direct import:

   ```python
   import requests
   ```

   Your code directly uses `requests`; its own dependencies are transitive.

2. Minimum constraint:

   ```toml
   dependencies = ["requests>=2.0"]
   ```

3. Exact pin:

   ```toml
   dependencies = ["requests==2.31.0"]
   ```

4. Bounded range:

   ```toml
   dependencies = ["requests>=2.31,<3.0"]
   ```

5. SemVer bump:

   ```text
   examplelib 2.31.0 → 2.32.0
   ```

   Illustrative MINOR update: new feature, existing usage should remain compatible.

6. Changelog classification:

   ```text
   v2.31.1: fixed redirects for PUT requests       → PATCH
   v3.0.0: removed Session.request_hook parameter  → MAJOR
   ```

7. Bounded Pydantic declaration:

   ```toml
   [project]
   dependencies = ["pydantic>=2.0,<3.0"]
   ```

   Accept 2.x updates; review before 3.0.

8. Conflict:

   ```text
   Application requires A >=2,<4
   B requires A <3
   C requires A >=3
   ```

   No A version satisfies both B and C.

9. Add and review:

   ```bash
   uv add "pydantic>=2.0,<3.0"
   git diff pyproject.toml uv.lock
   ```

   First command declares/resolves/locks/syncs; second shows the actual changes.

10. Safe update:

   ```bash
   uv add "pydantic>=2.5,<3.0"
   git diff uv.lock
   uv run pytest
   git add pyproject.toml uv.lock
   git commit -m "Update pydantic after review"
   ```

   Read release notes and check compatibility first; then update, inspect, test, and commit both dependency files together.

11. Separate lock and install:

   ```bash
   uv lock
   git diff uv.lock
   uv sync
   ```

   Resolve and review before installing the new locked state.

12. Rollback:

   ```bash
   git log --oneline -- pyproject.toml uv.lock
   git revert <that-commit>
   uv sync --locked
   ```

   Identify and revert the change, then synchronize to the known-good state locally. Production should redeploy the known-good artifact.

13. Application policy:

   ```toml
   dependencies = ["httpx>=0.27,<0.28"]
   ```

   Tight, reviewed range plus committed lock; the example is especially cautious because the package is pre-1.0.

14. Production/CI workflow:

   ```bash
   uv sync --locked
   uv run --locked pytest
   uv run --locked ruff check .
   git push
   ```

   CI installs the committed lock strictly, runs checks, and deploys only the reviewed state. Production sync generally excludes development dependencies with `uv sync --locked --no-dev`.

## 30. Mini-project — `orders-report` dependency lifecycle

The project extends the earlier CSV-to-report CLI:

```text
orders-report/
├── src/orders_report/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── validation.py
│   └── processing.py
├── tests/
│   ├── test_validation.py
│   └── test_processing.py
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

Dependency-focused `pyproject.toml` excerpt:

```toml
[project]
name = "orders-report"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pydantic>=2.0,<3.0"]

[dependency-groups]
dev = ["pytest>=8.0", "ruff>=0.5"]
```

Because this is a `src/` layout, the complete project also needs a suitable `[build-system]` configuration so the project package itself is installed and importable. The excerpt focuses on dependencies, not the full build setup.

**Lifecycle simulation:**

1. **Initial setup:** `uv sync` after cloning. Installs Pydantic, pytest, Ruff, and transitive dependencies from the lock. Plain sync includes the dev group.
2. **Add HTTP feature:** `uv add "httpx>=0.27,<0.28"`. This adds an intentional runtime dependency for exchange-rate requests. The narrow pre-1.0 range reduces surprise but requires a deliberate decision before 0.28.
3. **Review resolution:** `git diff pyproject.toml uv.lock`. Confirm the direct package and transitive additions.
4. **PATCH update:** if Pydantic 2.5.1 is the newest allowed release, run `uv lock --upgrade-package pydantic`, then `uv run pytest`. A plain `uv lock` can keep the existing locked version if it still satisfies the range. Targeting a precise version requires the supported target syntax for the installed `uv` version.
5. **MINOR update:** to adopt Pydantic 2.6, use `uv add "pydantic>=2.6,<3.0"` and run tests. Review the new optional helpers and existing behavior.
6. **MAJOR update:** before Pydantic 3.0, read its migration guide and update `validation.py` to handle the new error format. Only then change the constraint to `>=3.0,<4.0`, resolve, and test. This is a migration, not a routine bump.
7. **Conflict:** suppose `fx-rates-extra` requires `httpx>=0.28,<0.29`, conflicting with the project's `<0.28`. Resolution fails. If the team verifies 0.28 works with its own code, widen to `httpx>=0.27,<0.29` and retry. Do not widen merely to silence the error.
8. **Rollback:** if the Pydantic 3.0 deployment causes a rare production validation failure, revert the dependency-update commit and redeploy the known-good build with its lock. This sacrifices the new feature for stability.
9. **Security update:** if a transitive dependency of HTTPX has an advisory, explicitly upgrade that vulnerable package if a fixed version is available within constraints. Inspect `uv.lock`, read relevant release information, and test. Security urgency does not remove the need for review.
10. **CI/CD:** run `uv sync --locked`, `uv run --locked pytest`, and `uv run --locked ruff check .`. CI must verify the committed lock rather than silently generating a new one. Production uses the locked runtime dependencies, excluding dev tools.

---

# Part B — Project-Tree and Current-Level Assessment

## 1. Stage 1 project-tree position

The Stage 1 roadmap contains 24 modules and builds from computational thinking through production-oriented Python engineering. Its module sequence is:

1. Computational Thinking and Program Design.
2. Python Core Language and Data Types.
3. Control Flow, Functions, Scope, and Errors.
4. Problem-Solving, Collections, and Algorithmic Habits.
5. Text Files, Structured Data, and CLI Programs.
6. Modules, Packages, Dependencies, and Code Quality.
7. Testing and Systematic Debugging.
8. Object-Oriented Design, Data Modelling, and Functional Style.
9. Advanced Production-Oriented Python Foundations.
10. Production Habits for Python Programs.
11. Advanced Python Data Model and Object Design.
12. Metaprogramming and Dynamic Python.
13. Standard Library Toolkit.
14. Bytes, Binary Data, and Advanced Text Processing.
15. Modern Python Language Features.
16. Advanced Testing and Test Architecture.
17. Profiling, Memory, and Runtime Performance.
18. Packaging, Distribution, and Publishing.
19. CPython Internals and Runtime Behaviour.
20. Design Patterns and Library API Design.
21. Data Visualization and Notebook Workflows.
22. Secure Python Coding.
23. Code Reading, Refactoring, and Code Review.
24. Functions and OOP Gap Lessons.

The Stage 1 overview has four major projects:

- **Personal Expense Ledger CLI:** file-backed command-line application.
- **Log Investigation and Reliability CLI:** log processing and reliability analysis.
- **Data Quality and Transformation Pipeline:** `orders.csv`, a `dqpipe` package, CLI/configuration/pipeline/rules, tests, and a data contract.
- **Rule-Based Risk Review Engine:** `transactions.csv`, `rules.toml`, a `riskreview` package, tests, and golden decision data.

The project-tree plan also includes later stages for data engineering, data architecture, DevOps/platform engineering, mathematics, ML, deep learning, backend engineering for AI systems, LLM applications, RAG, evaluation, agents, safety, model customization, LLMOps, portfolio projects, interviews, and career growth.

## 2. Current learning level

Your current level is **beginner progressing toward intermediate** in Python engineering. You have already studied:

- Core Python types, collections, mutation, and data modelling fundamentals.
- Conditionals, loops, functions, scope, side effects, exceptions, and validation.
- Searching, grouping, deduplication, sorting, complexity, and data-structure selection.
- Files, paths, CSV, JSON, encodings, command-line arguments, streams, exit codes, logging, environment configuration, and input validation.
- Imports, modules, `__main__`, project layout, packages, `pyproject.toml`, `uv.lock`, virtual environments, and the core `uv` commands.

This lesson adds **dependency lifecycle engineering**: version compatibility, resolver conflicts, release risk, security, deliberate upgrades, and rollback. These are directly relevant to your `dqpipe` and `riskreview` applications because production data pipelines must be reproducible and safely maintained.

The solutions below stay within the current lesson and its prerequisites. They use Python imports, TOML declarations, dependency graphs, `uv`, Git, and test commands. They do not jump into advanced packaging internals or unrelated frameworks.

---

# Part C — All 14 Formal Exercises Solved

## Beginner

### 1. Direct versus transitive

- `pandas` is direct because `myapp` imports and declares it.
- `numpy` is transitive because `pandas` requires it.

### 2. Classify version changes

- `4.2.1 → 4.2.2`: PATCH — final segment increases.
- `4.2.2 → 4.3.0`: MINOR — middle segment increases.
- `4.3.0 → 5.0.0`: MAJOR — first segment increases.

### 3. Interpret `requests>=2.28,<3.0`

Accept 2.28 and later 2.x releases. Reject versions below 2.28 and versions 3.0 or later. Both conditions must hold.

### 4. `pyproject.toml` versus `uv.lock`

`pyproject.toml` records acceptable dependency ranges. `uv.lock` records the exact resolved versions to reproduce the selected dependency state.

## Intermediate

### 5. Range for version 1.9.4

```toml
dependencies = ["package>=1.9,<2.0"]
```

`>=1.9` allows updates within the 1.x line; `<2.0` requires a deliberate review before the next MAJOR release.

### 6. Find the overlap

- A requires `[1, 2)`.
- B requires `[1.5, 2.5)`.
- Shared valid range: **`[1.5, 2.0)`**.

For example, 1.7 satisfies both.

### 7. Why passing tests does not prove complete safety

Tests cover only the behaviors they exercise. The teammate must also read release notes, review how the project uses the dependency, inspect the lock diff, and check important application behavior not covered by tests.

### 8. Place dependencies in the correct groups

- `requests`, `pydantic`: `[project].dependencies` — runtime.
- `pytest`, `mypy`: `[dependency-groups].dev` — development.
- `openpyxl`: `[project.optional-dependencies].excel` — optional Excel feature.

### 9. Update a dependency constraint

```bash
uv add "package>=3.1,<4.0"
```

- `uv add` changes the declaration in `pyproject.toml`.
- It resolves and updates `uv.lock`.
- It synchronizes the environment.

## Advanced

### 10. Safe 1.x to 2.0.0 upgrade

1. Read the 2.0 changelog and migration guide.
2. Find every location where your code uses the dependency.
3. Identify removed APIs, changed parameters, return types, behavior, and Python support.
4. Update your code for the new API.
5. Change the version constraint.
6. Resolve and inspect the lock diff.
7. Run tests and quality checks.
8. Test important application behavior.
9. Commit the declaration and lock file together.

### 11. Resolve the shared C conflict

A requires `C<2.0`; D requires `C>=2.0`.

- **Option 1:** upgrade A or D to a release whose C constraint overlaps. Trade-off: the upgraded package needs its own compatibility review.
- **Option 2:** replace A or D with an alternative. Trade-off: more code and integration changes.

### 12. Production rollback plan

```bash
git log --oneline -- pyproject.toml uv.lock
git revert <dependency-update-commit>
```

1. Identify the exact commit that introduced the change.
2. Revert it, restoring the previous dependency declaration and lock.
3. Redeploy the previous known-good artifact or rebuild from the reverted commit.
4. Synchronize the build from its lock using `uv sync --locked --no-dev`.
5. Confirm the production regression is gone.
6. Investigate and add regression coverage before considering another update.

### 13. Published library versus internal application

- **Library:** use sensible, minimally restrictive version ranges so consumers can resolve the library with their other dependencies. Keep a lock for the library's own development/CI if useful.
- **Internal application:** use well-reviewed bounded ranges and commit `uv.lock`, because the team controls its deployment and needs reproducibility.

### 14. How a SemVer-compliant MINOR release can still break a consumer

A library fixes a bug in a MINOR release. The maintainer considers the fix backward-compatible because it restores documented behavior. A consumer's code had relied on the old buggy output, so that code breaks. The protection is to read release notes, test the consumer's own usage, and review actual application behavior after every update.

---

# Part D — All 10 Debugging Scenarios

1. **Resolver conflict:** identify the exact shared package and incompatible ranges; try compatible releases or replace/reconsider one dependency.
2. **Package missing on a clean machine:** it was probably installed manually but not declared. Add it using `uv add`.
3. **Unexpected upgrade during sync:** inspect Git history and diffs for `pyproject.toml`/`uv.lock`; plain sync may re-lock stale declarations. Restore the previous lock if the change was unintended.
4. **Lock file changed unexpectedly:** inspect the diff. A command may have re-resolved a stale project. Treat every lock diff as a reviewable dependency change.
5. **Package requires Python 3.13 but project supports 3.12+:** use an older package version that supports the project's Python range, or deliberately raise `requires-python` after checking all code and dependencies.
6. **Major update breaks tests:** read the migration guide, update the application's code to the new API, and rerun the suite. Do not treat a MAJOR update as routine.
7. **New package causes transitive conflict:** identify the shared transitive dependency and both constraints. Find compatible package releases or reconsider the new dependency.
8. **CI cannot import pytest:** CI probably installed runtime-only dependencies. Include the `dev` group in the test job's sync; production should still exclude it.
9. **Production issue after deployment:** revert the dependency-update commit and redeploy the known-good locked build. Add a regression test before retrying.
10. **Works locally but fails in CI:** verify CI uses the committed lock from the same commit with `uv sync --locked`, not a stale cache or independent resolution.

---

# Part E — Interview and Architecture Questions

The source lists 22 questions. Concise model answers:

1. **Dependency management:** deliberate selection, declaration, constraint, resolution, locking, updating, and testing of dependencies; manual installs do not provide reproducibility.
2. **Direct/transitive:** `requests` is direct if the application declares it; `urllib3` is transitive if required by requests.
3. **Loose versus strict constraints:** loose ranges increase flexibility but admit future changes; exact pins constrain resolution and increase maintenance.
4. **SemVer:** MAJOR may break, MINOR adds compatible features, PATCH fixes bugs compatibly.
5. **Is SemVer enforced?** No. It is a maintainer convention, not a guarantee enforced by Python tools.
6. **Major versus patch:** removing a public function is MAJOR; correcting a bug without intended API change is PATCH.
7. **Consumer perspective:** a change can break existing consumer behavior even if the maintainer considers it compatible.
8. **Pre-release:** alpha, beta, and rc versions are not final; production should avoid them unless instability is explicitly accepted.
9. **0.x:** compatibility can change even between MINOR releases; treat updates cautiously before 1.0.
10. **Resolver:** it finds one version satisfying every direct and transitive constraint; overlapping ranges resolve, disjoint ranges fail.
11. **Conflict:** `X<3` and `X>=3` cannot both hold. Forcing a version hides a real incompatibility.
12. **Project file versus lock:** `pyproject.toml` declares requirements; `uv.lock` records the resolved versions.
13. **Dependency drift:** environments independently resolve different versions over time; a committed lock provides a common resolved state.
14. **Safe update:** identify, read notes, review compatibility, change requirement, resolve, inspect lock diff, test, run quality checks, verify behavior, commit both files.
15. **Different scrutiny:** PATCH is usually lower risk, MINOR moderate, MAJOR highest; none is risk-free.
16. **Rollback versus forward-fix:** rollback restores known-good behavior during an incident; forward-fix is appropriate after diagnosis when a new correction can be safely verified.
17. **uv commands:** `add`/`remove` change declarations and resolve; `lock` updates lock; `sync` installs locked state; `run` executes in the managed environment.
18. **Dependency groups:** runtime for application execution; dev for development/test tooling; optional extras for opt-in features.
19. **Application versus library:** application favors reproducibility and bounded ranges; library avoids unnecessarily restricting downstream consumers.
20. **Supply-chain risk:** a dependency is compromised and introduces malicious code; verify package names, sources, and maintenance.
21. **Python compatibility:** a package may raise its minimum Python version; check it against the project's `requires-python`.
22. **Graph thinking:** each direct package adds transitive subtrees that can conflict or contain vulnerabilities; review the complete graph, not only direct names.

---

# Part F — All 8 Knowledge-Check Answers

1. **Why test a MINOR update?** SemVer describes intent, not a guarantee. A release can accidentally break code or change behavior your project relied on.
2. **Why library and application strategies differ:** a library's constraints affect many consumers' graphs; an application controls its own deployment and can prioritize a reproducible lock.
3. **Deprecation plus replacement function in 3.4.0 from 3.3.2:** MINOR. The old function still works, though it warns; a new replacement is added without removing the old API.
4. **Valid C range:** `[1,2)` intersected with `[1.5,3)` is `[1.5,2)`.
5. **Unconstrained `httpx` versus `>=0.27,<0.28`:** unconstrained accepts any future release, including potentially breaking pre-1.0 changes. The bounded range restricts the accepted line and forces a deliberate review before crossing it.
6. **CI resolution failure:** first confirm CI uses the committed lock file from the same commit with `uv sync --locked`; check for stale caches, wrong branch, or fresh re-resolution.
7. **A 0.9.3 to 0.10.0 update:** be highly cautious. Under the 0.x convention, a MINOR bump may contain breaking changes. Read release notes and run the full tests.
8. **Policy for a critical dependency:** use a bounded range aligned to its current MAJOR line, e.g. `>=2.4,<3.0`; add focused tests around critical usage and apply the full update review even to PATCH releases.

---

# Final Production Checklist

- [ ] Every direct runtime dependency is declared.
- [ ] Constraints are deliberate and reflect actual compatibility needs.
- [ ] Direct and transitive dependencies are understood.
- [ ] `uv.lock` is committed and kept consistent with `pyproject.toml`.
- [ ] Developers, CI, staging, and production use the same locked state.
- [ ] Every update includes release-note and compatibility review.
- [ ] The full lock diff is inspected, including transitive changes.
- [ ] Tests run after every update, including PATCH updates.
- [ ] MAJOR updates are treated as migration work.
- [ ] Pre-release and `0.x` dependencies receive extra caution.
- [ ] Python version and platform compatibility are checked.
- [ ] Runtime, development, and optional dependencies are separated.
- [ ] New packages are checked for trustworthiness and maintenance.
- [ ] Security advisories are monitored and prioritized.
- [ ] Rollback to a known-good locked build is understood.
- [ ] CI uses `uv sync --locked`; production excludes dev dependencies where appropriate.

**Core principle:** dependency management is not just installing packages. It is the disciplined process of declaring acceptable versions, resolving the complete graph, locking the selected state, reviewing changes, testing compatibility, and retaining a reliable rollback path. SemVer helps estimate risk, but your own tests and review establish whether an update is safe for your application.
