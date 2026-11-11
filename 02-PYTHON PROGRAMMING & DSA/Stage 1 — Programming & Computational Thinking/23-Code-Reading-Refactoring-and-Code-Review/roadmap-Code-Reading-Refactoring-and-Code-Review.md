# Roadmap — Module 1.23: Code Reading, Refactoring and Code Review

This is the learning roadmap for the twenty-third module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
about reading unfamiliar code, changing it safely, reviewing others' work
and contributing to shared projects, **in what order**, **how** to practise
each topic, and **how to prove to yourself** that you have learned it.

Professional engineers spend far more time reading, understanding and
modifying existing code than writing new code. Most of your work in a data
or AI team will be: understanding a pipeline someone else wrote two years
ago, adding a feature without breaking nightly jobs, finding which commit
introduced a bug, reviewing a colleague's pull request, and eventually
contributing a fix to an open-source library you depend on. These skills
separate juniors who can only build greenfield toys from engineers who can be
trusted with production systems.

This module ties together everything before it: testing (1.7, 1.16),
design (1.8, 1.20), tooling (1.6), debugging (1.7, 1.19), security (1.22),
packaging (1.18) and Git basics from Stage 0. It is also the bridge to
the interview and career stages, where code reading and review are
explicitly evaluated.

> Target: Python 3.12+, Git 2.40+, GitHub (or GitLab) workflow, `pytest`, `ruff`, `mypy`/`pyright`, `radon`/`xenon`, `vulture`, `import-linter`, `libcst` (optional).

---

## 1. Module outcome

By the end of this module you will be able to:

- Explore an unfamiliar codebase systematically and build a mental model within hours, not weeks.
- Write **characterization tests** that pin down legacy behaviour before changing it.
- Apply a catalogue of **safe refactorings** in small, test-protected steps, using tool support.
- Identify **code smells and technical debt**, quantify them and propose pragmatic remediation plans.
- Give and receive **effective code reviews**: what to check, how to word feedback, how to keep PRs reviewable.
- Use Git as an investigative tool: `blame`, `log -S/-G/-L`, `bisect`, `reflog`, `worktree`, `rebase -i` (non-interactive alternatives noted), history archaeology.
- Contribute to an open-source Python project: find an issue, reproduce, fix, test, document and submit a PR that follows project conventions.
- Read the source of CPython and major libraries to answer "how does this actually work?" questions.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Git, GitHub and SSH basics | Stage 0 — Module 0.4 (10) | History tools, PR workflow |
| Developer environment, debugging notes | Stage 0 — Module 0.4 (05, 13) | Tracing code paths |
| Project layout, linting, type checking | Module 1.6 | Orientation and safety nets |
| Pytest, test design, regression tests | Modules 1.7, 1.16 | Characterization tests |
| Tracebacks, minimal reproductions | Module 1.7 (06) | Bug investigation |
| OOP design, layered design | Modules 1.8, 1.20 | Recognising structure and smells |
| Profiling, internals | Modules 1.17, 1.19 | Reading performance-critical code |
| Security basics | Module 1.22 | Security-focused review |
| Packaging and release | Module 1.18 | Contribution and release processes |
| Anti-patterns & refactoring preview | Module 1.20 (10) | Deep dive here |

**Tools:** `git` (with `delta` or `diff-so-fancy` optional), `gh` CLI, `rg` (ripgrep), `fd`, `tree`, `ctags`/Pyright "Go to definition", `pydeps`/`pyreverse` (pylint), `radon`, `vulture`, `import-linter`, `coverage`, `pytest`, `ruff`, `libcst`/`rope` (optional), VS Code with Python/Pylance, GitLens (optional).

---

## 3. How the module is organised

```text
Phase A — Understanding Existing Code           (Basics → Intermediate)
  01 reading unfamiliar codebases
  02 characterization tests for legacy code
Phase B — Changing It Safely                    (Intermediate)
  03 refactoring catalogue
  04 code smells and technical debt
Phase C — Working With Other People             (Intermediate → Advanced)
  05 writing and receiving code review
  06 git blame, bisect and history archaeology
Phase D — Going Upstream                        (Advanced)
  07 contributing to open-source Python projects
  08 reading CPython and library source
```

Pace: about 3 weeks part-time. You will need a **legacy practice repository**:
use a deliberately messy ~1,500-line project (e.g. an old ETL/report script
collection, or a small open-source project at an old commit) and keep an
`investigation-log.md` throughout.

---

## Lesson 01 — `01-reading-unfamiliar-codebases.md`

**Why it matters.** The first day in a new codebase decides how confident
and productive you will be. A systematic method turns an intimidating
10,000-line repo into a map you can navigate, and the same method works for
a library you must debug, an incident in a service you don't own, or an
interview "read this code" exercise.

### Basic — what to learn

- Orientation checklist (first 30 minutes): `README`, `CONTRIBUTING`, `docs/`, `pyproject.toml` (dependencies, entry points, Python version, tools), `Makefile`/`justfile`/`noxfile.py`, CI config (`.github/workflows`), `Dockerfile`, directory tree, licence, changelog, issues/PR history.
- Get it running: create the environment (`uv sync`), run the tests, run the app/CLI with sample data; record the exact commands and any fixes in a notes file. If you can't run it, you can't understand it.
- Find the **entry points**: `[project.scripts]`, `__main__.py`, `if __name__ == "__main__"`, web routes, task/DAG definitions, CLI commands, scheduled jobs, notebooks, test fixtures.
- Navigate with tools: `rg "def process_order"`, `rg -n "class .*Error"`, IDE "Go to definition / Find references / Call hierarchy", `git grep`, `tree -L 2 -I '__pycache__|.venv'`.
- Basic technique: **follow one concrete flow end to end** (e.g. "what happens when the nightly job runs for one order?") using logs, debugger breakpoints (`breakpoint()`), or print-tracing, writing down the call chain.

```bash
tree -L 2 -I '__pycache__|.venv|node_modules'
rg -n "__main__|argparse|click|typer|FastAPI\(|@app\.|@task|DAG\(" src
uv run pytest -x -q
```

### Intermediate — what to learn

- Build a **mental model in layers**: (1) purpose & users; (2) architecture (modules, layers, external systems); (3) data model (key types, schemas, tables); (4) control flow (main paths, error paths, async/concurrency); (5) cross-cutting concerns (config, logging, auth, retries, caching); (6) operations (deploy, monitoring, runbooks).
- Draw it: module dependency graph (`pydeps src/pkg --max-bacon=2`, `pyreverse`, `import-linter` contracts), simple sequence diagram for the main flow, data-flow diagram of inputs → transformations → outputs; annotate unknowns as questions.
- Use **tests as documentation**: read test names and fixtures to learn intended behaviour; run `pytest --collect-only -q`; look at `conftest.py` for how components are assembled.
- Use **types and docstrings**: public API signatures, dataclasses/Pydantic models, `Protocol`s reveal the design; mypy/pyright "hover" types.
- Dynamic exploration: REPL/IPython with the package imported, `inspect`/`help`, `dir`, instantiate objects with sample data, `pdb` stepping into a call, `sys.settrace`-style tracers for call graphs, `python -X importtime`, `coverage run -m pytest` + HTML report to see which code is actually exercised.
- Read in the right order: start from **interfaces and data structures**, then main flows, then utilities; skim big files by outline (`ctags`, IDE outline) before reading linearly; don't read generated code/vendor directories.
- Identify the "hot spots": largest/most-changed files (`git log --format= --name-only | sort | uniq -c | sort -rn | head`), complexity (`radon cc -s -a src`), TODO/FIXME/HACK comments, deprecated markers.
- Keep an investigation log: questions, answers, surprises, glossary of domain terms, diagrams; convert it into a short onboarding doc/PR afterwards (improve the repo as you learn).

### Advanced — what to learn

- Reading **large and unfamiliar frameworks** (Django, Airflow, scikit-learn, FastAPI, pandas): learn their extension points and conventions first (settings, app registry, operators, estimators API), then trace a feature; rely on official architecture docs and design docs/PEPs; read the tests for edge cases.
- Reading **concurrent and async code**: identify event loops/executors/queues, ownership of state, cancellation paths, locks; draw thread/task diagrams; check shutdown behaviour.
- Reading **data pipelines**: sources → ingestion → transformations → sinks; schemas and contracts; idempotency and checkpoints; backfill paths; failure handling; configuration per environment; how to run locally with sample data; lineage metadata (Stage 2).
- Reading **ML/AI code**: data loading, preprocessing, model definition, training loop, evaluation, config/seeds, experiment tracking, serving path; identify train/serve skew risks and leakage.
- **Hypothesis-driven reading**: form hypotheses ("retries happen in `client.py`"), test them quickly with search/debugger, update the model; timebox exploration; know when to ask a human (after 30–60 minutes, with a precise question and what you've tried).
- Reverse-engineering **without docs**: logging/tracing to reveal behaviour; `strace`/`ltrace`/network capture for black boxes; reading bytecode (Module 1.19) when source is unavailable (rare); inspecting database schemas and sample data; reading dashboards and alerts to understand real behaviour.
- Reading **dependencies' source** to resolve bugs: jump from stack trace into site-packages, check versions, find the commit that changed behaviour, compare releases (`pip download` + `diff -r`, GitHub compare view).
- Building **personal tooling**: scripts that summarise a repo (LOC by module, dependency graph, public API list, test coverage by package), a template `ONBOARDING.md`, saved `rg` queries, IDE bookmarks.
- Capstone: pick an unfamiliar medium-size OSS project (e.g. `httpx`, `rich`, `typer`, `pydantic-core` Python layer, `dbt-core` subset, `airflow` provider) and produce a 2-page architecture note with a dependency diagram, main flows, extension points, and three questions you could not answer, within a time-box of four hours.

### Common mistakes

- Starting to read files top to bottom without a goal.
- Refusing to run the code ("reading only").
- Not writing down what you learn.

### Self-check

1. What are your first five actions in a new repo and why?
2. How do you trace a single request/job through an unfamiliar codebase?
3. Produce an architecture note plus dependency graph for the practice repository within a time-box.

---

## Lesson 02 — `02-characterization-tests-for-legacy-code.md`

**Why it matters.** Legacy code is, in Michael Feathers' definition, code
without tests. You can't safely refactor what you can't verify. A
characterization (a.k.a. "golden master") test captures what the code *actually
does today* — right or wrong — so changes that alter behaviour become visible
immediately.

### Basic — what to learn

- Purpose: **document and protect existing behaviour**, not assert correctness. The test says "given X the system returns Y today".
- The method: (1) put the code in a test harness (call it from a test); (2) write an assertion you expect to fail with an obviously wrong value; (3) run, observe the actual value; (4) change the expectation to the actual value; (5) repeat for many inputs, including edge cases; (6) note suspicious behaviours as potential bugs (but don't fix yet).
- Simple example:

```python
def test_discount_current_behavior():
    assert legacy.discount(100, "gold") == 85.0
    assert legacy.discount(100, "") == 100.0
    assert legacy.discount(-5, "gold") == -4.25      # suspicious! recorded, not "fixed"
```
- Choosing inputs: representative production-like samples, boundaries, empty/None, large, malformed, special values, different locales/time zones; use real (anonymised) data where possible.
- Make tests fast and deterministic: sample files in `tests/fixtures`, fixed seeds, frozen clock (Module 1.16 lesson 07).

### Intermediate — what to learn

- **Golden master / approval tests** for large outputs (reports, CSV, JSON, HTML, parquet): run the legacy code on a corpus of inputs, store outputs, compare after each change (Module 1.16 lesson 04 snapshot testing); masks for volatile data (timestamps, ids).
- **Seams** (Feathers): places where you can alter behaviour without editing in place — to isolate dependencies for testing: parameterise constructor/function, extract & override, wrap external calls, monkeypatch module attributes (`monkeypatch.setattr(legacy, "datetime", FakeDatetime)`), dependency injection of file paths/clients/clocks.
- Breaking dependencies on the **database, network, filesystem, clock, randomness, environment**: fake with in-memory SQLite, local fake server (Module 1.13), `tmp_path`, `freezegun`/clock injection, seeded RNG, `monkeypatch.setenv`.
- **Characterise through the outside in**: black-box tests at the CLI / API boundary first (cover most behaviour cheaply), then pin down internals as you refactor them.
- Coverage-guided exploration: run with `coverage`, look at uncovered branches in the area you will touch, add inputs until covered; consider **mutation testing** (Module 1.16 lesson 02) on the area to check that the characterization tests are sensitive.
- **Property and differential tests**: compare old vs new implementation on random inputs (`hypothesis`) during a rewrite (the "parallel run" technique); record mismatches and decide which are bugs vs intended changes.
- Handling nondeterminism & flakiness while characterising (ordering, parallelism, floats): normalise outputs (sort, round, `pytest.approx`).
- Don't fix bugs inside characterization commits: record them as `xfail(strict=True)` tests or issues; fix in separate, reviewed commits so behaviour changes are explicit.

```python
# differential test: legacy vs refactored
from hypothesis import given, strategies as st

@given(st.integers(-1_000, 10_000), st.sampled_from(["gold", "silver", "", None]))
def test_refactor_matches_legacy(amount, tier):
    assert new.discount(amount, tier) == legacy.discount(amount, tier)
```

### Advanced — what to learn

- **Legacy data pipelines & scripts**: capture input → output snapshots for representative days/partitions, compare row counts, schema, checksums, distributions (Stage 2 data quality); parity tests between old and new pipeline outputs with tolerances; shadow runs in production writing to a scratch location.
- Testing code with **hard-wired globals** and module-level side effects: import-time behaviour captured by subprocess runs; reload modules; patch at import boundaries; wrap legacy functions with adapter functions as the new public seam.
- Test **performance and resource behaviour** characteristics before refactoring (benchmarks, memory ceilings — Module 1.17) so refactors don't introduce regressions.
- **Strangler fig pattern** with tests: build a facade, route a slice of behaviour to new code while the old remains, compare outputs, switch gradually, delete the old; feature flags and canary rollouts; automatic diff reporting between old and new paths in production (shadow traffic) with PII-safe logging.
- Characterising **ML/AI behaviour**: pin evaluation metrics, seed-controlled outputs, golden predictions on a fixed sample, tolerance bands; for LLM-calling code, record/replay responses (cassettes) and test the surrounding logic deterministically; evals (later stage) for quality.
- Dealing with **huge untestable functions**: sprout method/class (add new behaviour in a new tested unit called from the old), wrap method/class, extract pure logic out of I/O-heavy code first (Module 1.8 lesson 07), "scratch refactoring" (experimental refactor to understand, then discard via `git restore`).
- Test-suite hygiene for legacy: tag characterization tests (`@pytest.mark.characterization`), keep them until replaced by proper unit tests, track the ratio; remove snapshots that were never reviewed; document known-bug tests.
- Measuring safety: coverage of changed lines (`diff-cover`), mutation score for the module, flake rate; "can I make this change with confidence?" as the objective, not 100 % coverage.
- Capstone: for the practice repository, characterise a 200-line function using the 6-step method plus golden master on 20 sample inputs; then refactor it (lesson 03) with all tests green at every commit; record at least three discovered bugs as `xfail` tests/issues.

### Common mistakes

- Fixing bugs while characterising (mixing behaviour change into the safety net).
- Writing tests that mirror the implementation line by line.
- Snapshots that nobody reviewed.

### Self-check

1. Explain the six steps of writing a characterization test.
2. What is a seam and name three ways to create one in Python.
3. Build a golden-master test for a CSV report generator, including masking volatile fields.

---

## Lesson 03 — `03-refactoring-catalogue.md`

**Why it matters.** Refactoring is changing structure without changing
behaviour. Done in small, mechanical, test-protected steps it is safe and
fast; done as a big-bang rewrite it is the leading cause of regressions
and cancelled projects. A shared catalogue gives you named, repeatable moves.

### Basic — what to learn

- Definition & rules: **no behaviour change; small steps; tests green after each step; commit often; separate refactor commits from feature/bug-fix commits; never refactor and change behaviour at once.**
- The core catalogue (Fowler) with Python examples:
  - **Rename** variable/function/class/module (IDE rename across project + grep for strings/config).
  - **Extract Function**: pull a cohesive block into a named function.
  - **Inline Function / Inline Variable**.
  - **Extract Variable** (explaining name for complex expression).
  - **Change Function Declaration** (rename/add/remove parameters safely: introduce new function, delegate, migrate callers, remove old).
  - **Replace Magic Number/Literal with Named Constant / Enum**.
  - **Introduce Parameter Object** (group parameters into a dataclass).
  - **Replace Temp with Query**; **Split Variable**; **Remove Dead Code**.
- Tooling: VS Code/PyCharm refactorings, `ruff --fix` (safe fixes), `rope`/`libcst` for scripted refactors, git for easy rollback.

```python
# before
def invoice(items, tax, d):
    t = 0
    for i in items:
        t += i[1] * i[2]
    return t * (1 + tax) * (1 - d)

# after: extract function, rename, parameter object
@dataclass(frozen=True)
class LineItem:
    sku: str; unit_price: Decimal; quantity: int

def subtotal(items: Iterable[LineItem]) -> Decimal:
    return sum((i.unit_price * i.quantity for i in items), Decimal(0))

def invoice_total(items, *, tax_rate: Decimal, discount: Decimal) -> Decimal:
    return subtotal(items) * (1 + tax_rate) * (1 - discount)
```

### Intermediate — what to learn

- **Moving features between objects**: Move Function/Method, Extract Class, Inline Class, Hide Delegate, Remove Middle Man.
- **Organising data**: Encapsulate Record/Collection, Replace Primitive with Object (value objects: `Money`, `Email`, `UserId`), Replace Dict with Dataclass/TypedDict, Change Value to Reference and vice versa.
- **Simplifying conditional logic**: Decompose Conditional, Consolidate Conditional Expression, Replace Nested Conditional with Guard Clauses, Replace Conditional with Polymorphism / dispatch table / `match`, Introduce Special Case (Null Object), Introduce Assertion.
- **Refactoring APIs**: Separate Query from Modifier, Parameterize Function, Remove Flag Argument, Preserve Whole Object, Replace Parameter with Query, Replace Constructor with Factory Function, Replace Function with Command.
- **Dealing with inheritance**: Pull Up/Push Down Method/Field, Replace Subclass with Delegate, Replace Superclass with Delegate (composition over inheritance), Collapse Hierarchy, Extract Superclass.
- Python-specific refactorings: loops → comprehensions/generators/`itertools`; manual resource handling → context managers; `getter/setter` → properties; class with only data → dataclass; callbacks → closures/`partial`; string building → f-strings/`join`; `dict` of `if` chains → dispatch tables; `isinstance` ladders → `singledispatch`/`match`; module-level globals → injected dependencies; script → `main()` + importable functions.
- **Mechanics for safe change**: (1) ensure tests; (2) make the smallest step; (3) run tests/type-check/lint; (4) commit; (5) repeat. Use "parallel change" (expand → migrate → contract) for signature changes and API replacement.
- Using **types as a refactoring safety net**: add annotations to the area first; run `mypy --strict` on it; changes ripple as type errors rather than runtime failures.

### Advanced — what to learn

- **Large-scale refactoring strategies**: branch by abstraction, strangler fig, feature toggles, expand-contract (parallel change) for database/schema/API migrations, codemods across many files (`libcst`, `ruff` rules, `sed`-safe patterns, `comby`), staged rollouts with metrics; handling in-flight branches (merge conflicts) by landing refactors early and in small PRs.
- **Architecture-level refactors**: introduce layers and enforce them (`import-linter` contracts: "domain must not import infra"), break cyclic dependencies (dependency inversion, move shared types down, event-based decoupling), split packages/monorepo moves (Module 1.18 lesson 08), extract services only when modular monolith boundaries are proven; "modular monolith first".
- **Refactoring tests**: extract fixtures, remove duplication (parametrization), fix over-mocking (prefer fakes), make tests behaviour-focused, speed up slow tests; apply the same discipline — tests are code.
- **Performance-aware refactoring**: don't undo performance-critical code without benchmarks; refactor for clarity first, optimise with data (Module 1.17); document why hot paths look odd.
- **Data & ML code refactoring**: notebooks → modules (Module 1.21), pandas chains → `pipe` steps with typed contracts, scattered feature logic → feature functions with tests, configuration extraction, reproducible training entry points, separation of data loading / transforms / model / evaluation; guard against train/serve skew when moving code.
- **Behaviour-changing "refactors" in disguise**: floating-point ordering changes, dict/set iteration order, laziness (generator vs list), exception types, logging side effects, timing/ordering of I/O, mutable default fixes, `is`→`==` — identify and test explicitly.
- Automating mechanical refactors: write a `libcst` codemod (e.g. rename function + update call sites + adjust imports) with tests on before/after snippets; run it over the repo; review the diff.
- Measure results: complexity (`radon cc`), function length, coupling (imports), duplication (`pylint --enable=duplicate-code`), test time, change-failure rate; present before/after.
- Pairing/mob refactoring and review practice: keep each PR to one refactoring theme; describe intent ("no behaviour change") and evidence (tests, snapshots); reviewers focus on mechanical correctness.
- Capstone: refactor the characterised 200-line function from lesson 02 into well-named units with a parameter object, guard clauses and a dispatch table; commit history of ≥ 15 tiny commits, each passing tests; final PR description with before/after metrics and a note of every suspected bug you deliberately left unchanged.

### Common mistakes

- Big-bang rewrites.
- Mixing refactoring with feature changes in a single commit/PR.
- Refactoring code with no tests and no type checks.

### Self-check

1. List the five rules of safe refactoring.
2. Show "parallel change" for renaming a widely used function's parameter without breaking callers.
3. Replace an `if/elif` chain on a string type with a dispatch table, using only green-test steps.

---

## Lesson 04 — `04-code-smells-and-technical-debt.md`

**Why it matters.** Smells are symptoms that a design is straining. Spotting
them early tells you where to refactor; ignoring them accumulates **technical
debt** — the future cost of shortcuts — that slows every change and raises
incident risk. Engineers who can name, size and communicate debt get time to
fix it.

### Basic — what to learn

- A **code smell** = a surface indication of a deeper problem (not necessarily a bug). Catalogue (Fowler/Kerievsky) with Python flavour:
  - **Bloaters**: Long Function, Large Class, Long Parameter List, Primitive Obsession, Data Clumps.
  - **Object-orientation abusers**: Switch/`if` chains on type, Temporary Field, Refused Bequest, Alternative Classes with Different Interfaces.
  - **Change preventers**: Divergent Change, Shotgun Surgery, Parallel Inheritance Hierarchies.
  - **Dispensables**: Duplicate Code, Dead Code, Speculative Generality, Lazy Class, Comments that explain bad code, Data Class (when it should have behaviour).
  - **Couplers**: Feature Envy, Inappropriate Intimacy, Message Chains (`a.b.c.d()`), Middle Man.
  - **Python specifics**: mutable default args, bare `except`, `import *`, global state, stringly-typed dicts, `type()` checks, over-use of `**kwargs`, long comprehensions, import-time side effects, hidden I/O in constructors, missing `__repr__`, `print` debugging left in, `assert` for validation.
- Detecting smells with tools: `ruff` (many rule families: `C90` complexity, `PLR` design, `B` bugbear, `SIM`, `ARG`, `ERA` commented-out code), `pylint`, `radon cc/mi/raw/hal`, `xenon` (complexity gates), `vulture` (dead code), `deptry`, `pylint --enable=duplicate-code`, `wily` (complexity over time).
- Know thresholds as guidelines: cyclomatic complexity > 10, function length > 40–50 lines, parameters > 4–5, nesting depth > 3, file > 500–800 lines.

```bash
uv run radon cc -s -a -nc src      # complexity grade C or worse
uv run xenon --max-absolute B --max-modules A --max-average A src
uv run vulture src --min-confidence 80
```

### Intermediate — what to learn

- **Smell → refactoring → pattern** mapping (lesson 03, Module 1.20 lesson 10): e.g. Long Function → Extract Function; Primitive Obsession → value objects; Switch statements → polymorphism/dispatch; Feature Envy → Move Method; Shotgun Surgery → Move/Inline to consolidate; Data Clumps → Introduce Parameter Object.
- **Technical debt** concept (Ward Cunningham): *deliberate vs inadvertent* × *prudent vs reckless* (Fowler's quadrant); debt as interest (slower changes, bugs, outages), principal (cost to fix).
- Debt categories: code, design/architecture, test, documentation, dependency/version, infrastructure, data (schemas, quality), security, knowledge (bus factor), process.
- **Making debt visible**: debt register (issue label `tech-debt`: description, location, impact, effort, risk, owner), `# TODO(ticket)` policy (no TODO without a ticket), architecture decision records, dashboards (complexity trend, dependency age, coverage, flaky tests, build time, CVEs).
- Prioritising: impact (how often do we touch this? how many incidents?) × effort × risk; focus on **hot spots** = high complexity × high churn (`git log` churn + `radon` complexity; "CodeScene"-style analysis you can script with `git log --numstat`).
- Paying down strategies: Boy-Scout rule (leave it a little cleaner), refactor-as-you-go in feature work, dedicated "debt budget" per sprint (e.g. 10–20 %), targeted spikes, deletion days, deprecate-and-remove, automated upgrades (Renovate/Dependabot), codemods.
- Communicating with non-engineers: translate to business risk and speed (lead time, change failure rate, onboarding time, incident cost); show before/after metrics; propose incremental milestones; DORA metrics as language (deployment frequency, lead time, change failure rate, MTTR).

### Advanced — what to learn

- **Churn × complexity analysis**: script it — parse `git log --numstat --since=12.months` to count changes per file, join with `radon` complexity, rank top 10 hot spots; verify by checking bug-fix commit density (`git log --grep -i fix`); present as a scatter plot (Module 1.21) with an action list.
- **Temporal coupling and co-change analysis**: files that always change together reveal hidden dependencies (mine from git history); detect missing abstractions or wrong module boundaries.
- **Architectural debt**: cyclic dependencies, layer violations, god modules, inconsistent data models across services, duplicated business rules, hidden global state, implicit contracts between pipelines (schema drift), "distributed monolith"; measure with `import-linter`, dependency graphs, ownership maps (CODEOWNERS), change-coupling.
- **Test debt**: low-value/slow/flaky tests, missing characterization tests around risky areas, over-mocked tests that pass while production fails; track flake rate, test duration, escaped defects (Module 1.16).
- **Data & ML debt** (Sculley et al., "Hidden Technical Debt in ML Systems"): glue code, pipeline jungles, dead experimental codepaths, unstable data dependencies, feedback loops, configuration debt, entanglement (changing one feature changes all — CACE principle), undeclared consumers, training/serving skew, reproducibility gaps; prompts and evaluation sets as versioned assets; model/prompt/version sprawl.
- **Dependency & platform debt**: outdated Python/libraries, pinned-forever dependencies, vendored forks, EOL runtimes, unsupported cloud services; upgrade playbooks (Module 1.15 lesson 10), automated update PRs, compatibility testing, deprecation tracking.
- **Documentation & knowledge debt**: missing runbooks, tribal knowledge, bus-factor risk; ADRs, onboarding docs, code ownership rotation, pairing; docs-as-code and docs tests (doctests, link checks).
- **Governance**: definition of done includes tests/docs; quality gates (complexity thresholds on changed files only — "ratchet" so debt can't increase), architecture fitness functions (automated checks for properties like layering, API stability, latency budgets), periodic architecture reviews.
- **Rewrite vs refactor decision framework**: factors (understanding, tests, domain complexity, business pressure, team skill, platform shifts), risks (second-system effect, feature freeze, regression), hybrid approaches (strangler, modular extraction), cost-benefit with explicit exit criteria.
- Case studies: read postmortems or public write-ups of debt-driven failures (e.g. Knight Capital dead code/feature flag incident, left-pad/dependency incidents, famous rewrites like Netscape) and extract preventive controls relevant to Python/data teams.
- Capstone: produce a **Technical Debt Report** for the practice repo: top-10 smells with evidence (tool output + code snippets), hot-spot analysis plot, debt register entries with effort/impact, a prioritised 3-month remediation plan with quality gates, and a one-page manager summary using business language.

### Common mistakes

- Treating all smells as equally urgent.
- "Fix everything" crusades with no measurable goal.
- Hiding debt rather than recording it.

### Self-check

1. Name five smells and the refactoring that addresses each.
2. How do you identify the hot spots most worth refactoring?
3. Write a convincing one-paragraph case to management for a two-week debt reduction with measurable outcomes.

---

## Lesson 05 — `05-writing-and-receiving-code-review.md`

**Why it matters.** Code review is the main quality, learning and
knowledge-sharing mechanism in professional teams — and a place where careers
are built (or damaged) by communication style. Good reviews catch defects
early, spread context, keep standards consistent and build trust; bad reviews
are slow, nitpicky, personal or rubber stamps.

### Basic — what to learn

- Purposes of review: correctness, design, readability/maintainability, tests, security, performance, consistency, knowledge sharing, bus factor — **not** policing style (automate that with `ruff`/formatters/CI).
- **As an author**: keep PRs small (< 400 changed lines; one logical change), self-review the diff first, write a clear description (what/why/how tested/risks/screenshots/links), link the issue, include tests and docs, keep commits tidy, mark drafts, respond to every comment, don't take feedback personally.
- **As a reviewer**: understand the goal first (read description & issue), review the tests first, then the design, then details; check the happy path **and** failure paths; suggest rather than dictate; ask questions; approve when it improves the code health even if not perfect (Google's standard); respond within a day.
- Comment hygiene: be specific and kind; explain the *why*; prefix intent (`nit:`, `question:`, `suggestion:`, `blocking:`, `praise:`); separate must-fix from optional; offer an example or a suggested change (GitHub suggestion blocks).

```text
blocking: `fetch()` retries on every exception, including 401. That will hammer the auth
endpoint during an outage — can we retry only on `TransientFetchError`? (see lib/errors.py)
nit: `data` → `orders` would read better here.
praise: the parametrised boundary tests are great.
```

### Intermediate — what to learn

- **Review checklist** (adapt per team):
  1. *Correctness*: does it do what the issue says? edge cases (empty, None, large, duplicate, unicode, time zones), error paths, off-by-one, concurrency/races, idempotency.
  2. *Design*: right place/layer? duplication? unnecessary abstraction? public API impact? backwards compatibility (Module 1.20)? naming?
  3. *Tests*: do they fail without the change? behaviour not implementation? deterministic? enough boundary/negative cases?
  4. *Readability*: clear names, small functions, comments explaining *why*, docstrings for public API, consistent style.
  5. *Security & privacy*: input validation, injection, secrets/PII in logs, authz checks, dependency additions (Module 1.22).
  6. *Performance & resources*: accidental O(n²), N+1 queries, memory blow-ups, unbounded retries/queues, timeouts.
  7. *Operations*: logging/metrics, config, migrations, rollbacks, feature flags, docs/runbooks.
  8. *Dependencies*: new package justified? licence? maintenance? lock file updated?
- Reviewing **different kinds of changes**: refactors (behaviour-preserving evidence), bug fixes (regression test + root cause), new features (design fit, API), data/SQL/migration changes (idempotency, backfill, locking, rollback), notebooks (diff tooling, outputs stripped), ML/AI changes (eval results, data leakage, reproducibility, cost/latency, prompt versions), infrastructure/CI changes (blast radius).
- Tooling: GitHub/GitLab review UIs, `gh pr checkout`, `gh pr diff`, local checkout and running tests, reading in the IDE with full context, `git diff --stat`, `--color-moved`, ignoring whitespace (`-w`), reviewing commit-by-commit, CODEOWNERS and required reviews, branch protection, status checks, stacked PRs.
- Automation to reduce noise: formatters, linters, type checks, security scans, test/coverage gates, PR templates and checklists, danger-style bots, automated dependency PRs — humans review design and logic.
- **Receiving feedback**: assume good intent, separate ego from code, ask for clarification, explain trade-offs, push back respectfully with evidence, thank reviewers, resolve threads when addressed, escalate disagreements to a design discussion rather than a comment war.
- Review etiquette & inclusivity: avoid "obviously/just/simply", critique code not people, consider time zones, use neutral/inclusive language (and they/them when unsure of pronouns), recognise seniority gaps (juniors should review seniors too).

### Advanced — what to learn

- **Review effectiveness research**: optimum review size and speed (~200–400 LOC, < 60 minutes), defect detection rates, reviewer fatigue; techniques: checklist reviews, two-pass reviews (design then details), pair review, "review the tests first", rotating reviewers for knowledge spread.
- **Design reviews and RFCs** before code: problem statement, goals/non-goals, alternatives, trade-offs, rollout/rollback, risks, open questions; ADRs; reviewing architecture diagrams; asynchronous design discussion; decision records; managing bike-shedding (timebox, default to author's choice for reversible decisions).
- **Reviewing for risk**: blast radius, feature flags, migrations, data loss potential, backward/forward compatibility, rollout plan, monitoring and alerting, fallback; "what happens at 3 a.m. if this breaks?"; reviewing security-sensitive code with a second specialist; threat-model deltas (Module 1.22 lesson 08).
- **Reviewing AI/ML/data PRs**: data lineage and schema changes, training/eval split integrity, leakage checks, seed/determinism, metric definitions and significance (Stage 4/10), prompt/version changes with eval results attached, cost/latency regressions, safety/guardrail impact, PII in datasets/logs/prompts, model/dataset licence, reproducibility of results.
- **Scaling review culture**: team agreements (review SLAs, size limits, who must review what, definition of done), onboarding juniors via review, "review of the reviews" retrospectives, avoiding bottleneck reviewers (rotation, CODEOWNERS granularity), measuring cycle time (PR open → merge), balancing speed vs safety; trunk-based development with small frequent PRs vs long-lived branches; stacked diffs.
- **Handling difficult situations**: large unreviewable PRs (ask to split; offer to pair), repeated nits (automate), defensive authors, overly strict reviewers, disagreement on design, urgent hotfix reviews (post-merge review policy), rubber-stamp culture, AI-generated code in PRs (require author understanding, tests, small diffs; verify claims and licences; watch for plausible-looking bugs and hallucinated APIs).
- **AI-assisted review**: use LLM review tools as a first pass for obvious issues, never as the sole approval; verify suggestions; protect confidential code (data-handling policy); track false positives; add repo-specific guidance files.
- Practice: review three real PRs from an open-source project (read-only; do not comment unless invited): write your review notes with severity labels; compare with the actual maintainers' comments; reflect on what you missed.
- Practice: review a deliberately flawed PR you are given or create (seeded with: a missing edge case, a security issue, an N+1 query, flaky test, poor naming, unneeded dependency, behaviour change inside a "refactor") and see how many you catch; then **author** a PR, request review, and respond to feedback professionally; write a short retrospective.
- Capstone: write the team's `CONTRIBUTING.md` review section and PR template (checklist, size guidance, labels, SLAs), and a one-page "How we give feedback" guide.

### Common mistakes

- Reviewing only style and missing logic/design/security.
- Leaving vague or harsh comments ("this is bad").
- Letting giant PRs through with "LGTM".

### Self-check

1. What do you review first and why?
2. Rewrite three harsh comments into constructive, actionable ones.
3. Review the seeded-flaw PR and list findings by severity within a time-box.

---

## Lesson 06 — `06-git-blame-bisect-and-history-archaeology.md`

**Why it matters.** Version control is a time machine. When a bug appears,
a behaviour seems illogical, or you need to know *why* code exists, Git can
tell you who changed it, when, in which commit, with what message and
discussion — and can find the exact commit that introduced a regression
automatically. Stage 0 covered Git basics; this lesson makes it an
investigation tool.

### Basic — what to learn

- Inspecting history: `git log --oneline --graph --decorate --all`, `git log -p -- path`, `git log --follow -- path` (renames), `git show <commit>`, `git diff A..B`, `git diff A...B` (merge-base), `git log --stat`, `--since/--until/--author`.
- `git blame path` (line-by-line authorship), `git blame -L 120,160 path`, `git blame -w -C -C -C` (ignore whitespace, detect moved/copied lines), `git blame --ignore-rev <sha>` and `.git-blame-ignore-revs` for mass-formatting commits (e.g. "apply black/ruff format").
- Reading **commit messages and linked PRs/issues** to learn intent: `gh pr view`, `gh issue view`, `git log --format=%B`; the GitHub UI "View blame" and "Blame prior to this change".
- Good commit hygiene (so your history is searchable): imperative subject ≤ 72 chars, body explains *why*, reference issue, atomic commits, conventional commits (Module 1.18 lesson 07).

```bash
git log --oneline --follow -- src/etl/transform.py | head
git blame -w -C -L 80,120 src/etl/transform.py
git show a1b2c3d --stat
```

### Intermediate — what to learn

- **Pickaxe search**: `git log -S"retry_count" --oneline` (commits that changed the *number of occurrences* of a string), `git log -G"regex"` (diffs matching a regex), `git log -L :function_name:path` (history of a function/line range), `git log --grep="timeout" -i`.
- **`git bisect`**: binary search for the commit that introduced a bug. Manual: `git bisect start`, `git bisect bad` (current), `git bisect good v1.4.0`, test, mark good/bad until it names the first bad commit; **automated**: `git bisect run pytest tests/test_x.py::test_regression -x` or a script returning exit code 0 (good), 1–124/126–127 (bad), **125 (skip, can't test)`; `git bisect reset`. Requirements: a reproducible, fast test; handle skipped commits (build failures).
- Recovering lost work: `git reflog`, `git restore -s <commit> -- path`, `git cherry-pick`, `git revert` (safe undo on shared branches) vs `git reset` (local only), finding dangling commits (`git fsck --lost-found`), recovering deleted branches.
- Working across versions without disturbing your tree: `git worktree add ../repo-old v1.2.0` to run old code side by side; `git stash` (and its limits); temporary branches for experiments; `git restore`/`git switch`.
- Comparing releases: `git diff v1.3.0..v1.4.0 -- src/`, `git log v1.3.0..v1.4.0 --oneline`, `git shortlog -sn`, GitHub compare view, `pip download pkg==x` + `diff -r` for packages without repo access; reading `CHANGELOG`/release notes first.
- Using history for **ownership & expertise**: `git shortlog -sn -- path`, `git log --format='%an' -- path | sort | uniq -c`, CODEOWNERS, "who to ask" (kindly) — plus bus-factor insights.

```bash
git bisect start
git bisect bad HEAD
git bisect good v1.4.0
git bisect run uv run pytest tests/test_totals.py::test_rounding -x -q
git bisect reset
```

### Advanced — what to learn

- **Hard cases with bisect**: flaky tests (run N times per step; script exit codes), tests that need new fixtures (copy test files outside the tree or use `git bisect run` with a wrapper that checks out the test from the good commit), dependency-environment changes between commits (use `uv run --with` locked environment per commit or containerised runs), merge-heavy histories (`--first-parent` bisect), non-code regressions (data, config), performance regressions (bisect with a benchmark threshold script; noisy → repeated measurements), bisecting across large ranges quickly (~log₂ N steps: 1,000 commits → 10 steps).
- **History rewriting with care**: interactive rebase (`git rebase -i` — in non-interactive environments use `GIT_SEQUENCE_EDITOR` or `git commit --fixup` + `git rebase --autosquash`), `commit --amend`, `git rebase --onto`, `filter-repo` for removing secrets/large files (and why rotation is still required); **never rewrite shared history** without coordination; protect main with branch rules; `--force-with-lease` instead of `--force`.
- **Mining history for insight**: churn/hot-spot analysis (lesson 04), co-change coupling (`git log --name-only` pair counts), bug-fix density (`git log --grep` + path), time-to-fix, author concentration, commit size distribution; tools: `git-fame`, `gitinspector`, `pydriller` (Python library to mine repos programmatically), `code-maat`, `CodeScene` (commercial); write a `pydriller` script that finds files with highest bug-fix churn.
- **Archaeology of intent**: connect code → commit → PR → issue → design doc/ADR → incident postmortem; use `git log --follow`, `blame --ignore-revs-file`, searching PR discussions (`gh search prs`), reading removed code in diffs to learn failed approaches; documenting findings in code comments/ADRs so the next person doesn't repeat the dig.
- **Debugging with history in production contexts**: map deployed version → commit (embed `git describe`/build SHA in `--version`, logs, metrics tags, container labels; Module 1.18), `git describe --tags --dirty`, compare deployed vs main, hotfix branches, release tags and signed tags (Module 1.18 lesson 06), reverting a release safely, cherry-picking fixes to maintenance branches.
- **Monorepo and large-repo techniques**: sparse checkout, partial clone (`--filter=blob:none`), shallow clones and their effect on bisect/blame (`git fetch --unshallow`), `git maintenance`, commit-graph for speed, path-limited bisect (`git bisect start -- path`), `git log --since` limited analysis.
- **Collaboration workflows**: trunk-based vs GitFlow vs GitHub Flow, feature flags, PR merge strategies (merge commit vs squash vs rebase) and their effects on blame/bisect/readability (squash loses fine-grained history; merge commits preserve context; rebase gives linear history), `git notes`, `git replace` (awareness), `git rerere` for repeated conflict resolution, conflict resolution strategies (`merge.conflictstyle=zdiff3`, `git mergetool`).
- **Security & integrity**: signed commits/tags (SSH or GPG signing), verifying signatures in CI, detecting force-pushes, protecting against malicious history (e.g. suspicious `git blame`-hidden commits, supply-chain incidents like xz backdoor — read the timeline), `git fsck`, verifying release artifacts against tags.
- Capstone: given a repository with a seeded regression (you create or receive one) in ~300 commits with a flaky-ish test and a formatting-only mass-change commit: (1) write the failing test; (2) set `.git-blame-ignore-revs`; (3) use `git bisect run` to find the culprit; (4) use `git log -S/-L` and blame to find the *intent*; (5) write the fix + regression test; (6) write a short postmortem naming the commit, cause, detection gap and prevention.

### Common mistakes

- Using `blame` as a blame tool for people rather than a context tool.
- Bisecting without an automatable, reliable test.
- Rewriting history on shared branches.

### Self-check

1. Explain `-S` vs `-G` vs `-L` in `git log` and when to use each.
2. Describe how `git bisect run` interprets exit codes, including `125`.
3. After a mass reformat commit, how do you keep `blame` useful?

---

## Lesson 07 — `07-contributing-to-open-source-python-projects.md`

**Why it matters.** Open source is how the Python ecosystem works. Contributing
teaches you to work in unfamiliar codebases, follow standards, communicate
asynchronously, and ship through someone else's review process — a
credible, public portfolio signal for hiring (Stage 16/17) and a way to fix
the bugs that block your own work.

### Basic — what to learn

- Why contribute: fix bugs you hit, learn from maintainers, build reputation, give back, shape tools you depend on.
- Start small and **be useful**: documentation fixes/typos, clarify docs and examples, add tests, reproduce and triage issues ("can reproduce on 3.13, here's a minimal example"), type-annotation improvements, good-first-issue labels (`good first issue`, `help wanted`), `up-for-grabs`, Python project mentorship programmes.
- Read project docs first: `README`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` (security issues are reported privately!), issue/PR templates, governance, roadmap, licence (inbound=outbound, DCO/CLA requirements).
- Workflow (GitHub): fork → clone → add `upstream` remote → create a topic branch → set up the dev environment as described (often `uv sync`, `pre-commit install`, `nox`/`tox`/`make test`) → make a focused change → add tests/docs/changelog entry → run the project's checks locally → push → open a PR following the template → respond to review.

```bash
gh repo fork org/project --clone && cd project
git remote -v    # origin = your fork, upstream = org/project
git switch -c fix-docs-typo
# ... edit, test ...
git push -u origin fix-docs-typo && gh pr create --fill
```

### Intermediate — what to learn

- **Before coding**: search existing issues/PRs to avoid duplicates; comment to claim an issue or ask a clarifying question; for non-trivial changes propose the approach first (issue/discussion) — maintainers' time is the scarce resource; make a **minimal reproducible example** (Module 1.7 lesson 06) for bugs: versions (Python, OS, package, dependencies), exact steps, expected vs actual, full traceback, smallest code.
- **Writing a good fix**: reproduce with a failing test first; change the minimum; follow project style (formatter, linters, type checker, docstring conventions, naming); keep the diff small and focused; include tests (regression + edge cases); update docs/changelog (`towncrier` fragment, `CHANGES.rst`); mind supported Python versions and dependency ranges; avoid unrelated refactors.
- **Pull request quality**: title in project convention (e.g. conventional commits), description with problem/solution/testing/risks/links (`Fixes #123`), screenshots or benchmarks if relevant, checklist completed, CI green (explain unrelated failures), tidy commits (squash if requested), rebase on upstream main when asked.
- **Interacting with maintainers**: be patient (days/weeks), polite, concise; accept "no" gracefully; respond to every review comment; don't force-push in a way that destroys review context unless asked (use `fixup` commits and ask); say thank you; if you can't continue, say so so someone else can pick it up.
- Running the project's checks locally: `pre-commit run --all-files`, `nox -s tests`, `pytest -k`, type checkers; reading CI configs to see what runs; testing on multiple Python versions (Module 1.16 lesson 08).
- Documentation contributions: fix examples that don't run (doctest), clarify confusing sections, add how-to guides or migration notes; docs builds (`sphinx-build`, `mkdocs serve`) and link-checking.
- Reviewing others' PRs/triaging issues as a contribution: reproduce bugs, bisect (lesson 06) to find the offending commit, add labels/minimal repros, test PRs locally and report results.
- Choosing projects: libraries you use (httpx, pydantic, pandas, pytest plugins, ruff/uv ecosystem, scikit-learn, FastAPI, dbt, Airflow providers, LangChain integrations), healthy signals (recent commits, responsive maintainers, clear contribution guide, CI, labels), size and complexity fit.

### Advanced — what to learn

- **Substantial contributions**: designing a feature with maintainers (design doc/RFC/PEP-like proposal), implementing in stages with feature flags/experimental status, API stability considerations (Module 1.20 lessons 06–07), performance benchmarks and regression tests (`asv`, `pytest-benchmark`), docs + migration notes, cross-platform considerations (Windows/macOS/Linux, CPU architectures), free-threaded/typing compatibility.
- **Contributing to CPython and the standard library**: Developer's Guide (devguide.python.org), `gh`/GitHub workflow, issue triage, building CPython from source (`./configure --with-pydebug && make -j`), running the test suite (`./python -m test -j0`), PEP process for language/library changes, Discourse discussions, core mentorship, CLA signing (PSF), news entries (`blurb`), backports labels; start with docs, tests, small bugs; reading `Lib/` Python modules (Lesson 08).
- **Maintainer's perspective**: triaging issues, writing templates, labelling, release management, CI maintenance, handling toxic behaviour, burnout, funding (GitHub Sponsors, Open Collective, Tidelift, employer support), governance models (BDFL, steering council, foundations: PSF, NumFOCUS, Linux Foundation, Apache); enforcing code of conduct; maintainers' security obligations (2FA, trusted publishing — Module 1.18).
- **Legal & licensing**: understanding licences (MIT/BSD/Apache/GPL/AGPL), contributor agreements (CLA vs DCO sign-off `git commit -s`), employer policies on open-source contributions and IP, avoiding copying incompatible-licensed code, attribution; **AI-generated code** policies (many projects restrict or require disclosure—read the policy).
- **Security disclosure**: how to report vulnerabilities privately (`SECURITY.md`, GitHub private advisories, `security@`), coordinated disclosure timelines, CVE requests, never opening public issues with exploit details for unpatched bugs.
- **Sustained contribution**: build a track record (small → medium → feature), become a triager/reviewer, write maintainers' docs, speak/write about it, mentor newcomers; manage your time and set boundaries; track contributions in a portfolio page with links, impact, and what you learned (interview material for Stage 17).
- **Internal open source (inner-source)** in companies: same practices for shared internal libraries (contribution guide, CODEOWNERS, issue templates, good-first-issues), reducing platform team bottlenecks.
- **Forks and vendoring** as last resorts: when upstream is unresponsive, maintain a patched fork temporarily, upstream the fix, track divergence, set exit criteria; don't vendor code with incompatible licences.
- Capstone: complete **three upstream contributions** in an actively maintained Python project (or, if network/time-limited, run the entire workflow in a private mirror with a mentor): (1) docs/test improvement, (2) triaged bug with minimal reproduction and bisect result, (3) a small bug fix with regression test and changelog entry accepted by maintainers; write a retrospective (time spent, review rounds, lessons, feedback), and a portfolio entry.

### Common mistakes

- Opening a huge PR without discussing it first.
- Ignoring contribution guidelines and CI failures.
- Taking review feedback personally or abandoning silently.

### Self-check

1. List the steps from "I found a bug in a library" to "my fix is merged".
2. What makes a bug report maintainers love?
3. Prepare (and, if possible, submit) a PR fixing a documentation or test gap, following every project convention.

---

## Lesson 08 — `08-reading-cpython-and-library-source.md`

**Why it matters.** When documentation is thin, an error is mysterious or
behaviour is surprising, the source is the ground truth. Reading the source
of the standard library, CPython itself and key third-party libraries makes
you faster at debugging, better at API design (you absorb how experts structure
code), and prepares you for contributing upstream.

### Basic — what to learn

- Where the source lives: Python standard library in `Lib/` (pure Python modules like `argparse.py`, `collections/`, `dataclasses.py`, `functools.py`, `pathlib/`, `asyncio/`, `json/`), C accelerators in `Modules/` and `Objects/`, interpreter core in `Python/`, headers in `Include/`; browse on GitHub (`github.com/python/cpython`) or locally (`python -c "import json, inspect; print(inspect.getsourcefile(json))"`).
- Reading pure-Python stdlib first: `functools.lru_cache` wrapper logic, `dataclasses._process_class`, `collections.OrderedDict`/`namedtuple` generation, `heapq`, `bisect`, `enum`, `contextlib`, `argparse`, `logging`, `pathlib`, `shutil`, `subprocess`, `typing`.
- Navigation tips: use the IDE "Go to definition" into stdlib stubs (`typeshed`) vs real source; open `site-packages` code for third-party libraries; `help()`/`inspect.getsource()`/`inspect.getsourcelines()`; GitHub code search and blame to see why a line exists; `git log -S` in the CPython repo.
- Read with a question: *"How does `dataclass` generate `__init__`?"*, *"Why does `lru_cache` hold references?"*, *"What does `json.dumps` do with `NaN`?"*; find the entry point, trace to the answer, write the answer down in your own words with a link to the lines.

```python
import inspect, functools
print(inspect.getsource(functools.cached_property))
```

### Intermediate — what to learn

- **Reading C-implemented pieces** at a practical level: understand the shape of `Objects/listobject.c` (struct layout, `list_append`, over-allocation formula), `Objects/dictobject.c` (compact dict design, comments at the top are excellent), `Python/ceval.c`/`bytecodes.c` (instruction semantics), `Modules/_json.c` (accelerator for `json`); read the **comment blocks and design docs** first (`InternalDocs/` directory in the repo: GC, frames, interpreter, exception handling, JIT), then the code; don't try to read all C — find specific functions with `rg`.
- Matching Python-level behaviour with the C implementation: pure-Python fallbacks (e.g. `_pyio`, `heapq` Python vs `_heapq`, `functools` `_lru_cache_wrapper` in C) — comparing both clarifies semantics; test with `python -X importtime`/`sys.modules["_heapq"]`; disabling accelerators with `test.support.import_helper.import_fresh_module` in tests.
- **PEPs as design documentation**: read the PEP for features you read the source of (PEP 557 dataclasses, PEP 3119 ABCs, PEP 343 `with`, PEP 484/585/695 typing, PEP 554/684/703 concurrency, PEP 659 specialisation); PEPs record motivation, rejected alternatives and semantics; `python.org/dev/peps`, Discourse discussions, "What's New" docs.
- **Third-party library reading skills**: start from the public API (`__init__.py`/`__all__`), follow the main call path for one feature, read the tests for edge cases, check extension points (hooks/plugins/protocols), read `CHANGELOG` for design shifts; for large codebases read architecture docs, then a single vertical slice (e.g. `requests.get` → `Session.request` → adapters → `urllib3`).
- Tools: `pydeps`/`pyreverse` for module graphs, `ctags`, `rg --type py`, ast-based call graph (`pycg`, `code2flow`), debugger stepping *into* library code (`justMyCode=false`), setting breakpoints in site-packages, `sys.settrace`/`sys.monitoring` call tracers (Module 1.19 lesson 10), `strace` for syscalls.
- Reading **type stubs** (`typeshed`) as concise API documentation; reading **tests** as executable specifications; reading **benchmarks** to learn performance-sensitive paths.
- Build a **"source reading notebook"**: one page per investigated mechanism (question, files/lines, explanation, diagram, surprising details, link), searchable and versioned (Markdown in a repo); this becomes your interview ammunition and team knowledge.

### Advanced — what to learn

- **Building and debugging CPython from source**: debug build (`--with-pydebug`), `PYTHONMALLOC=debug`, `-X dev`, `gdb`/`lldb` with `python-gdb.py` (`py-bt`, `py-locals`), adding a `printf`/`fprintf` to observe behaviour, running a single test (`./python -m test test_dataclasses -v`), reading `Tools/` helper scripts, using `Tools/c-analyzer`, PGO/LTO flags; experimenting with a trivial change (e.g. add a new method to `list` or a new opcode in a throwaway branch) to understand the pipeline (grammar → compiler → opcode → eval loop), with the explicit goal of learning, not upstreaming.
- **Cross-reading performance-critical designs**: `dict` and `set` hashing/probing, `str` representation (PEP 393), small-int and interning caches, `list.sort` (Timsort — `Objects/listsort.txt` is a masterpiece), `re`/`_sre`, `asyncio` event loop and `selectors`, `concurrent.futures` executors, `queue`, `threading` internals, `multiprocessing` start methods; relate each to the measurements you made in Module 1.17 and the runtime model from Module 1.19.
- **Reading major libraries critically**: pandas (indexing, `BlockManager`/Copy-on-Write — Stage 2), NumPy (ufunc machinery, dtype system, strides), scikit-learn (estimator API, `check_estimator`), PyTorch Python layer (`nn.Module`, autograd graph building, `torch.compile` frontend), Hugging Face `transformers` (config → model → generation loop), FastAPI/Starlette (ASGI, dependency injection), SQLAlchemy (Core vs ORM, unit of work), Pydantic (schema building; Rust core), httpx/httpcore (sans-I/O design — Module 1.20 lesson 09), pytest (plugin hooks; assertion rewriting), ruff/uv (Rust codebases: how Python tooling is changing). For each: sketch the architecture and name 3 design decisions you would copy and 1 you would avoid.
- **Source-level debugging of real incidents**: given a perplexing exception from a dependency (stack trace into site-packages), find the lines, understand the preconditions, craft a minimal repro, check whether it's your misuse or a bug, find the upstream fix (`git log`/issues), choose workaround/upgrade/patch (monkeypatch with tests and a removal date).
- **Auditing dependencies for security and quality**: reading `setup.py`/build backends, install-time hooks, network calls, `exec`/`eval`/`pickle`/`subprocess` use (Module 1.22), obfuscated code, typosquatting indicators, maintainer history; tools: `guarddog`, `pip-audit`, `bandit` on site-packages, diffing releases (`pip download` two versions → `diff -r`); sandbox suspicious packages (containers, no network). Practise on a known historical malicious-package case study (read-only).
- **Teaching what you read**: write a blog-style deep dive ("How `functools.lru_cache` works", "Inside `dataclasses`", "How `asyncio.TaskGroup` cancels siblings"), give a 20-minute internal talk or record a walkthrough; explaining forces precision and reveals gaps; contribute documentation or comments upstream where explanations were missing.
- **Contributing upstream from source reading**: improve docstrings/comments/typing stubs, add missing tests found while reading, report discrepancies between docs and behaviour with minimal repros (lesson 07).
- **Time-boxing & strategy for huge codebases**: choose depth over breadth; maintain a question list; stop when your question is answered; revisit later with new questions; leverage LLM assistants for navigation and summaries but verify against the code and tests (they can hallucinate APIs and line references).
- Capstone: write **three source-reading reports** (each 2–4 pages, with diagrams and code references to a specific commit/tag): (1) one pure-Python stdlib mechanism (e.g. `dataclasses` or `functools.lru_cache`), (2) one CPython C-level mechanism (e.g. list over-allocation or dict lookup or `for` loop bytecode), (3) one third-party library vertical slice (e.g. `httpx` request path or `pytest` assertion rewriting); each includes an experiment (benchmark, debugger session or modified build) that confirms your understanding and a "what I would copy / avoid" section.

### Common mistakes

- Trying to read an entire codebase linearly.
- Reading without a question or without experiments to confirm understanding.
- Trusting summaries (including AI-generated) without checking the code.

### Self-check

1. Where in the CPython repo would you look to understand how `dict` handles resizing and why?
2. How do you step through a third-party library's code in a debugger?
3. Produce a one-page explanation, with line references, of how `functools.lru_cache` decides what to evict.

---

## 4. Practice questions (`practice-questions.md`)

About **35 questions**:

| Phase | Question types |
| --- | --- |
| A | Orientation planning for a given repo layout; seam identification; write characterization tests for snippets |
| B | Apply named refactorings step by step; classify smells; compute hot spots from sample git/complexity data |
| C | Review a seeded PR (list findings by severity); rewrite harsh comments; design a PR template |
| D | Bisect scenarios (exit codes, flaky tests); history search command selection; OSS contribution walkthrough; source-reading questions |

Include 6 **"what is the next safest step?"** refactoring puzzles and 4 **"find the commit"** history-investigation scenarios.

---

## 5. Module mini-project

**Inherit, stabilise and improve `legacy-ledger`** (a deliberately messy ~1,500-line ETL/reporting project with minimal tests, long functions, globals, copy-paste, and a seeded regression):

1. `ONBOARDING.md` from the lesson-01 method: run instructions, architecture sketch with dependency graph, main flows, glossary, open questions.
2. Characterization + golden-master tests for the three riskiest flows; seams introduced; coverage and mutation score reported; known bugs recorded as `xfail`/issues.
3. A Technical Debt Report (smells with evidence, hot-spot plot from `git log` + `radon`, prioritised plan, manager summary).
4. A refactoring series (≥ 30 small commits) producing layered structure, value objects, a dispatch table instead of `if` chains, injected dependencies, type hints, and `import-linter` contracts — all tests green at each commit; behaviour-change commits separated and reviewed.
5. Use `git bisect run` to locate the seeded regression, document the intent via `log -S/-L` and blame (with `.git-blame-ignore-revs`), fix with a regression test, and write the postmortem.
6. Run a mock review cycle: open PRs for the refactor series, have a peer (or use a checklist self-review plus tool bots) review them using the lesson-05 checklist; respond to feedback; record the review retrospective.
7. Upstream contribution: submit (or prepare in a private mirror) one real PR to an open-source Python library you used, following its contribution guide; include the minimal repro and test.
8. Source-reading report on one mechanism that your project depends on (library or stdlib), with an experiment.

Acceptance: ≥ 85 % characterised-area coverage, complexity of the top-5 hot-spot functions reduced by ≥ 40 % with no behaviour changes proven by golden tests, all CI checks green, the bisect result reproducible by script, review checklist and PR template committed, and a final retrospective describing time spent, risks avoided, and what you would do differently.

---

## 6. Completion checklist

- [ ] I can orient myself in an unfamiliar codebase quickly and document what I learn.
- [ ] I can write characterization and golden-master tests and create seams in legacy code.
- [ ] I can apply the refactoring catalogue in small, test-protected steps, with tool support.
- [ ] I can identify smells and technical debt, find hot spots with data, and argue for remediation.
- [ ] I can give and receive code reviews that are specific, kind and effective, and I use checklists and automation.
- [ ] I can use Git to investigate: blame, pickaxe, log -L, bisect (automated), reflog and worktrees.
- [ ] I can contribute a well-scoped, well-tested PR to an open-source project following its conventions.
- [ ] I can read stdlib, CPython and library source to answer questions and confirm my understanding with experiments.
- [ ] I completed the `legacy-ledger` mini-project.

**Next:** Module 1.24 — Functions and OOP Gap Lessons (closures, lambdas, callables, object construction and class design review), a compact consolidation module that you may also take **before** Modules 1.11–1.12 if you want a gentler path into advanced OOP and metaprogramming.
