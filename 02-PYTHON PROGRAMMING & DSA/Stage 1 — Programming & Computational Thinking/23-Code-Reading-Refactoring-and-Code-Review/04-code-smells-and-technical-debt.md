# Code Smells and Technical Debt

**Stage 1 — Programming & Computational Thinking · Module 1.23 · Lesson 04**  
**Audience:** Python engineers progressing from beginner to advanced; emphasis on data engineering and production reliability.  
**Target environment:** Python 3.12+, Git 2.40+, `pytest`, Ruff, Radon/Xenon, Vulture; optional Pylint, `deptry`, `wily`, `import-linter`, and plotting libraries.

## Learning outcomes

By the end, you should be able to:

1. Distinguish a code smell (a diagnostic clue) from a confirmed defect and from an intentional trade-off.
2. Recognise the five classic smell families and common Python-specific warning signs.
3. Map a smell to a proportionate refactoring or investigation rather than mechanically applying a pattern.
4. Explain technical debt as principal plus ongoing interest, classify its causes, and make it visible.
5. Use repository history, complexity, defect evidence, and architectural signals to identify high-value hot spots.
6. Prioritise remediation using impact, risk, effort, and business context.
7. Assess code, test, architecture, data/ML, dependency, infrastructure, security, knowledge, documentation, and process debt.
8. Build a reproducible Technical Debt Report with evidence, a hot-spot plot, a debt register, a three-month plan, and a management summary.

## 1. What is a code smell?

A **code smell** is a surface-level symptom that may indicate a deeper design, maintainability, reliability, or changeability problem. It is not proof that the code is wrong. A 70-line function might be a coherent parser with a stable contract; a 12-line function might hide a security defect. Smells are prompts to investigate, not automatic verdicts.

A **defect** is an observable failure to meet an expected requirement or contract. A **smell** is evidence that a design may make defects, changes, or comprehension harder. A **trade-off** is a deliberate choice made under constraints; it can still accrue debt if its costs are not managed.

Ask four questions before recommending a fix:

- **Evidence:** What concrete code, history, test, incident, or developer-friction evidence supports the concern?
- **Consequence:** What can go wrong or become slower because of it?
- **Context:** Is this code frequently changed, performance-sensitive, generated, stable, or scheduled for deletion?
- **Remedy:** What is the smallest intervention that reduces the demonstrated risk?

### Smell versus defect: examples

| Observation | Classification | Next step |
|---|---|---|
| A function is 90 lines long but has one coherent parsing algorithm and strong tests. | Potential smell; not a defect by itself. | Inspect cohesion, branches, change history, and readability. |
| A mutable default list leaks records between calls. | Python-specific smell and likely defect when callers expect isolation. | Reproduce it, add a regression test, then fix separately from unrelated cleanup. |
| Two modules duplicate a rule because they intentionally serve independently versioned products. | Duplication signal; possibly a valid boundary. | Check whether the rules must evolve together before consolidating. |
| A dependency has a known exploitable vulnerability in the deployed version. | Confirmed security risk, not merely a smell. | Follow incident/security remediation policy and test an upgrade. |
| A module has many imports but is a stable public facade. | Metric/smell signal requiring context. | Inspect dependency direction and API purpose before splitting it. |

## 2. The five classic smell families

The categories below follow the catalogue referenced in the module roadmap. Names are useful shared vocabulary, not a mandatory scoring system.

### 2.1 Bloaters

| Smell | What it looks like | Typical risk | Candidate response |
|---|---|---|---|
| **Long Function** | Many responsibilities, nested branches, repeated setup or cleanup. | Hard to test individual decisions; changes interact. | Extract cohesive functions, name intermediate concepts, separate I/O from transformation. |
| **Large Class** | Many unrelated reasons to change; many methods or fields. | High coupling and difficult ownership. | Extract class/module around a real domain boundary; avoid splitting by line count alone. |
| **Long Parameter List** | Many related values passed together. | Call-site mistakes and noisy interfaces. | Introduce a parameter object/dataclass when the values form a stable concept. |
| **Primitive Obsession** | Repeated raw strings, numbers, or booleans represent domain concepts. | Invalid states and duplicated validation. | Add a value object or `Enum` when it enforces meaningful invariants. |
| **Data Clumps** | The same group of fields travels together across functions. | Call signatures drift and invariants are scattered. | Introduce a parameter object or cohesive record if the fields share meaning. |

### 2.2 Object-orientation abusers

| Smell | What it looks like | Candidate response and caution |
|---|---|---|
| **Type-based conditional chain** | `if kind == ...` repeated across multiple functions. | Use a dispatch table for a small stable mapping, or polymorphism when behavior and lifecycle genuinely belong to types. One `if` is not automatically bad. |
| **Temporary Field** | An instance attribute is only meaningful during one operation or in certain modes. | Pass operation state explicitly or create a short-lived helper object; check whether optional state is a real domain lifecycle. |
| **Refused Bequest** | A subclass inherits behavior it cannot honor or overrides most of it. | Prefer composition or split the abstraction; inheritance is not inherently wrong. |
| **Alternative Classes with Different Interfaces** | Two classes do the same role but callers must use different method names or argument shapes. | Align the interface or add adapters; preserve legitimate differences at boundaries. |

### 2.3 Change preventers

| Smell | What it looks like | Candidate response |
|---|---|---|
| **Divergent Change** | One module changes for unrelated reasons (schema updates, email templates, pricing rules). | Separate responsibilities along reasons to change. |
| **Shotgun Surgery** | One business-rule change requires edits in many files. | Consolidate the rule behind a stable module/API; first check whether the files intentionally belong to different services. |
| **Parallel Inheritance Hierarchies** | Adding a subtype in one hierarchy repeatedly requires a matching subtype elsewhere. | Combine responsibilities, use composition, or replace parallel class families with a shared strategy object. |

### 2.4 Dispensables

| Smell | What it looks like | Candidate response |
|---|---|---|
| **Duplicate Code** | Similar logic copied across locations. | Extract shared logic only if semantics and change reasons are truly the same. |
| **Dead Code** | Unreachable code, unused functions, obsolete flags or branches. | Verify runtime/plugin/reflection entry points, then delete in a reviewed change. Tools produce candidates, not proof. |
| **Speculative Generality** | Abstractions, hooks, flags, or base classes for imagined future needs. | Remove unused complexity or simplify to current requirements; retain extension points justified by real consumers. |
| **Lazy Class** | A class adds little behavior or value. | Inline it or merge it where this reduces indirection; tiny classes can still express useful domain concepts. |
| **Inappropriate comments** | Comments narrate syntax or defend confusing code rather than explain intent/constraints. | Improve names and structure; retain comments documenting rationale, invariants, legal constraints, or non-obvious decisions. |
| **Data Class used without appropriate behavior** | A record owns domain rules elsewhere despite being the natural invariant boundary. | Move cohesive validation/behavior to the domain object where that improves cohesion. Data-transfer records are often correctly behavior-light. |

### 2.5 Couplers

| Smell | What it looks like | Candidate response |
|---|---|---|
| **Feature Envy** | A method repeatedly reads another object’s data to perform that object’s work. | Move the method or ask the data-owning object to perform the operation. |
| **Inappropriate Intimacy** | Classes depend on each other’s internals or mutate private state. | Reduce shared mutable state, introduce a clear interface, or merge if they are truly one concept. |
| **Message Chains** | `order.customer.address.region.code` leaks a path through object structure. | Add a meaningful query at the appropriate boundary; do not blindly create forwarding methods for every property. |
| **Middle Man** | A class mostly forwards calls to another class. | Remove the indirection or give the intermediary a real policy/responsibility. A facade/adapter is justified when it protects a boundary. |

## 3. Python-specific smells and why they matter

These are warning signs. Some are style issues; others can be correctness, security, or operational risks.

### Mutable default arguments

```python
# Smell: the same list survives across calls.
def add_record(record, records=[]):
    records.append(record)
    return records

# Safer when per-call isolation is intended.
def add_record(record, records=None):
    if records is None:
        records = []
    records.append(record)
    return records
```

The second version changes behavior for callers who intentionally relied on shared state. Characterize call sites before treating it as a purely structural cleanup.

### Bare or overly broad exception handling

```python
import logging

logger = logging.getLogger(__name__)


def parse_legacy_row(row: str) -> object | None:
    # Smell: hides programming errors and interrupts such as KeyboardInterrupt.
    try:
        return parse_row(row)  # supplied by the legacy module
    except:
        return None


def parse_row_safely(row: str) -> object | None:
    # Handle only failures this caller knows how to recover from.
    try:
        return parse_row(row)
    except (ValueError, TypeError) as exc:
        logger.warning("Invalid row: %s", exc)
        return None
```

Do not narrow an exception handler without checking the existing contract and error policy. `except Exception` can be justified at a process boundary when the exception is logged and handled deliberately; swallowing it silently is the smell.

### Wildcard imports and global state

```python
from legacy_helpers import *  # unclear names and collision risk
CURRENT_TENANT = "default"   # hidden mutable process-wide state
```

Prefer explicit imports and pass tenant/configuration as an explicit dependency. Beware that global state can be intentionally used for immutable constants or controlled registries.

### Stringly typed dictionaries and excessive `**kwargs`

```python
# Spelling errors and undocumented combinations are easy.
def build_job(config: dict[str, object]) -> None:
    if config.get("rety_count"):
        ...

# Give stable domain configuration a typed shape.
from dataclasses import dataclass

@dataclass(frozen=True)
class JobConfig:
    retry_count: int
    source_name: str
```

A dictionary remains appropriate for genuinely dynamic payloads or wire formats. A function with `**kwargs` may be a deliberate adapter; it is a smell when it hides the supported contract and suppresses useful type checking.

### Overlong comprehensions

```python
# Too many filters, transformations, and conditionals in one expression.
selected = [normalize(r) for r in rows if r.get("active") and valid(r) and (r.get("region") or "unknown") != "blocked"]

# Name the decisions.
def is_eligible(row: dict[str, object]) -> bool:
    return bool(row.get("active")) and valid(row) and (row.get("region") or "unknown") != "blocked"

selected = [normalize(row) for row in rows if is_eligible(row)]
```

### Import-time side effects and hidden I/O in constructors

Avoid opening network connections, reading production secrets, connecting to a database, or starting threads merely because a module is imported or an object is constructed. Prefer explicit factories/startup functions and injected clients. This improves testability and makes process startup and failure behavior predictable.

### Other Python signals

- **`type()` checks:** repeated concrete-type branching can indicate a missing protocol or strategy, but exact type checks are legitimate for serialization boundaries and carefully constrained code.
- **Missing useful `__repr__`:** hard-to-diagnose objects slow debugging; provide a safe representation that does not expose secrets or huge payloads.
- **Leftover `print`:** use structured logging for operational diagnostics; do not remove deliberate CLI output.
- **`assert` for runtime validation:** Python can remove assertions under optimization (`-O`). Use explicit validation and exceptions for untrusted/runtime input; assertions are appropriate for developer invariants and tests.
- **Hidden equality or identity assumptions:** `is` is for identity/singletons such as `None`, not value equality. Changing equality semantics can affect dictionary/set behavior.
- **Unclear generator/list behavior:** replacing a generator with a list changes eager evaluation, memory use, exception timing, and side-effect timing.

## 4. Tooling: detect signals, then investigate

Use tools to narrow the search space, not to decide architecture automatically. Pin tool versions in the project environment and run tools against the same source scope when comparing trends.

### A practical baseline

```bash
# Run the project-defined checks first.
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run mypy src                 # if configured; use pyright if that is the project standard

# Complexity reports; -nc shows blocks at grade C or worse.
uv run radon cc -s -a -nc src
uv run radon mi -s src          # maintainability index: comparative signal, not quality truth
uv run radon raw -s src         # raw metrics such as LOC/comments

# Enforce a chosen complexity policy; tune limits to the existing baseline.
uv run xenon --max-absolute B --max-modules A --max-average A src

# Find likely unused code (review results manually).
uv run vulture src --min-confidence 80

# Dependency declaration issues; exact behavior depends on deptry configuration/version.
uv run deptry .

# Optional Pylint duplication/design checks; confirm the checker supports these options.
uv run pylint --enable=duplicate-code src

# History for churn investigation.
git log --since="12 months ago" --format= --numstat
```

Tool notes:

- **Ruff**: fast linting and formatting; rule families such as `C90`, `B`, `SIM`, `ARG`, `ERA`, and selected `PLR` rules can flag complexity, suspicious constructs, simplification opportunities, unused arguments, commented-out code, and design signals. The exact enabled rules are determined by `pyproject.toml`.
- **Pylint**: broader diagnostics, design metrics, and optional duplicate-code detection; it can be noisier and slower than Ruff. Treat each duplicate-code message as a candidate block, not a percentage of the codebase. If reporting a duplication ratio, define the eligible source scope and overlap policy, then calculate `duplicated eligible LOC / total eligible LOC × 100`; do not infer that ratio from the number of Pylint messages alone. Compare runs only with the same tool version and configuration, and inspect whether the duplicated blocks encode the same rule.
- **Radon**: cyclomatic complexity, maintainability index, raw metrics, and Halstead metrics.
- **Xenon**: gates Radon complexity at configured thresholds.
- **Vulture**: finds likely unused code; dynamic imports, plugin registration, reflection, and framework conventions can produce false positives.
- **deptry**: checks dependency declarations/usage patterns; it does not establish that a dependency is secure or semantically compatible.
- **Duplication tools**: useful for candidate discovery, but copied code may have deliberately different semantics.
- **wily**: tracks selected code metrics over version history; configure and validate the repository baseline before comparing results.
- **Dependency/architecture tools**: `import-linter`, `pydeps`, or `pyreverse` can help reveal cycles and layer violations. A graph needs interpretation: some cycles are runtime-only or type-checking-only, and not every dependency is harmful.

### Thresholds are heuristics, not universal laws

The roadmap gives screening heuristics such as cyclomatic complexity above 10, function length above 40–50 lines, more than 4–5 parameters, nesting deeper than 3, or files above 500–800 lines. Treat these as **review prompts**, not hard laws. Domain algorithms, generated files, public compatibility wrappers, and stable code may warrant exceptions. A short, highly coupled function can be riskier than a long, linear one. Set thresholds based on team context and baseline; gate new or changed code first.

## 5. Smell → investigation → refactoring

| Smell or signal | First investigation | Possible remediation | Evidence of improvement |
|---|---|---|---|
| Long function | Identify separate reasons to change; branch and exception map. | Extract cohesive functions; separate pure transformation from I/O. | Same behavior tests pass; complexity per unit falls; callers become clearer. |
| Large class | Count responsibilities, dependencies, and independent change reasons. | Extract class/module around a domain boundary. | Fewer unrelated dependencies; no new circular imports; focused tests. |
| Long parameter list / data clump | See whether the same values travel together and share invariants. | Parameter object/dataclass. | Fewer call-site mistakes; validation centralized; API migration tested. |
| Primitive obsession | Find repeated validation and invalid combinations. | Enum/value object/typed model. | Invalid states rejected at one boundary; serialization contract unchanged. |
| Type conditional chain | Find all branches and identify what varies. | Dispatch table for simple mapping; polymorphism/strategy for behavior-rich variants. | Branch coverage preserved; unknown-key behavior explicit. |
| Divergent change / shotgun surgery | Use `git log` and co-change analysis to identify reasons for edits. | Move rule behind a stable module/API. | Fewer files touched for a representative change, without hiding dependencies. |
| Duplicate code | Compare semantics, tests, and independent reasons to change. | Extract shared function or keep copies intentionally separate. | One rule source with tests for all consumers; no over-generalized abstraction. |
| Dead code | Search references, entry points, plugins, reflection, runtime registration. | Delete in a small commit with tests and release notes if public. | No live references; package/API tests still pass. |
| Feature envy / message chain | Determine which object owns the invariant and how stable the navigation path is. | Move method or add a meaningful query at a boundary. | Reduced knowledge of internal structure; coupling does not simply move elsewhere. |
| Mutable default / global state | Reproduce cross-call leakage and enumerate callers. | Explicit state or dependency injection. | Isolation tests pass; intentional shared-state behavior remains documented. |
| Import-time I/O | Import in a clean subprocess and inspect side effects. | Explicit initialization/factory. | Import is side-effect-light; startup behavior tested at application boundary. |
| Flaky/slow tests | Track reruns, duration, external dependencies, over-mocking. | Stabilize fixtures, isolate boundaries, reduce unnecessary integration scope. | Lower flake rate and runtime without losing meaningful production-path coverage. |

Do not treat the table as an automatic mapping. For example, replacing a type-based conditional with polymorphism may add needless classes when a simple dictionary of functions is clearer.

## 6. Technical debt: principal, interest, and intent

Technical debt is the future cost created when current implementation or operating choices make later changes more expensive or risky. The metaphor has two parts:

- **Principal:** the estimated work and risk required to address the underlying issue.
- **Interest:** recurring costs paid while the issue remains: slower delivery, extra testing, incidents, support load, onboarding time, operational toil, and more expensive future changes.

A small principal can have high interest if the code is on the critical path of every release. A large principal may be low priority if the component is isolated and scheduled for retirement. Estimates should include uncertainty and ongoing risk, not only lines of code.

### Deliberate versus inadvertent; prudent versus reckless

A useful Fowler-style quadrant crosses two questions:

| | Prudent | Reckless |
|---|---|---|
| **Deliberate** | “We know the shortcut and will repay it after the release; here is the owner and date.” | “We know this bypasses validation but will ship anyway without a safety plan.” |
| **Inadvertent** | “We learned a simpler design after shipping; the earlier choice was reasonable with the knowledge available.” | “We did not understand the design and accumulated avoidable complexity.” |

Intent is not the same as risk. Deliberate debt still needs a clear owner, expiry/trigger, monitoring, and exit plan. Inadvertent debt should be treated as learning, not blame.

### Debt categories

| Category | Examples | Typical controls |
|---|---|---|
| Code/design | Long functions, duplicated rules, unclear boundaries. | Refactoring, tests, code ownership, design review. |
| Architecture | Cycles, layer violations, distributed monolith, inconsistent domain models. | Architecture fitness functions, dependency contracts, modular boundaries. |
| Test | Missing safety net, flaky tests, excessive runtime, over-mocking. | Characterization tests, stable fixtures, test pyramid, duration/flake tracking. |
| Documentation/knowledge | Missing runbooks, tribal knowledge, single maintainer. | ADRs, docs-as-code, pairing, rotation, onboarding guides. |
| Dependency/platform | EOL runtime, vulnerable package, pinned-forever dependency, vendored fork. | Upgrade playbooks, automated PRs, compatibility tests, deprecation tracking. |
| Infrastructure/operations | Manual deployments, snowflake environments, weak observability. | Infrastructure as code, deployment automation, runbooks, SLOs. |
| Data | Undocumented schema contracts, quality drift, unsafe backfills, unclear lineage. | Data contracts, schema checks, lineage, replay/backfill tests. |
| Security | Missing validation, unpatched CVEs, secret leakage, weak authorization boundaries. | Threat modeling, dependency scanning, secure defaults, incident response. |
| ML/AI | Pipeline jungles, training-serving skew, configuration sprawl, unreproducible experiments. | Versioned data/config/evaluation assets, reproducible builds, monitoring. |
| Process/organizational | Slow review, unclear ownership, repeated manual approvals, no debt budget. | Explicit ownership, smaller PRs, quality gates, time-boxed remediation. |

## 7. Make debt visible and actionable

### Debt register

A debt register is not a list of vague complaints. Each entry should identify a location, evidence, consequence, owner, effort range, risk, and a trigger or target date. Link a `TODO` to a tracked issue (`TODO(PLAT-241): ...`) rather than leaving an unowned promise in source. Use architecture decision records (ADRs) to document consequential choices and their trade-offs; do not turn every minor cleanup into an ADR.

**Illustrative debt-register rows — fictional sample, not measured repository data:**

| ID | Evidence / location | Impact and risk | Effort | Owner | Priority / trigger |
|---|---|---|---:|---|---|
| DEBT-01 | `src/etl/reconcile.py::reconcile_batch`; 4 branches added in last 6 months; two incident links | Incorrect reconciliation can corrupt downstream totals; high operational impact | 3–5 engineer-days | Data Platform | P1; before next schema expansion |
| DEBT-02 | `src/connectors/legacy_api.py`; dependency unsupported; no contract tests | Upgrade/security and availability risk; uncertain compatibility | 2–4 days | Ingestion team | P1; upgrade spike this month |
| DEBT-03 | `tests/test_month_end.py`; 11-minute suite segment, intermittent external API failures | Slower feedback and missed releases; medium impact | 2–3 days | Reporting team | P2; next sprint |
| DEBT-04 | `src/features/assemble.py`; duplicated feature definitions in training and serving | Train/serve skew risk and repeated changes | 5–8 days | ML Platform | P1; before next model release |

Effort is a range, not a promise. Include dependencies and confidence; split discovery work from implementation when uncertainty is high.

### Quality dashboards

Track a small set of indicators with stable definitions: changed-line complexity, top-hotspot trend, duplicate-code candidates, dependency age/security findings, test duration and flake rate, change failure rate, mean time to restore, data-quality incidents, and lead time. Avoid one composite “quality score” that obscures trade-offs. Metrics should help ask better questions, not become targets that teams game.

## 8. Hot spots: complexity × change frequency

A **hot spot** is a component where complexity and change frequency intersect. High complexity alone can be acceptable in stable, well-tested code. High churn alone may reflect a healthy, active feature. High complexity *and* high churn is a stronger candidate for investigation, especially when linked to defects or incidents.

### Reproducible analysis method

1. Choose a time window (the roadmap suggests 12 months) and a consistent branch/revision.
2. Extract per-file change activity from Git history. Decide whether “churn” means commit count, number of changed lines, or number of commits touching a file; do not mix definitions silently.
3. Measure complexity with Radon on the same revision and source scope.
4. Join by normalized repository-relative path. Exclude generated/vendor files explicitly and document exclusions.
5. Inspect top-ranked files and verify with bug-fix commits, incidents, ownership, and upcoming work.
6. Plot the joined values. Label the data source and date range; the plot is a prioritization aid, not proof of debt.

Example history commands:

```bash
# Commit count touching each tracked file (simple, easy-to-explain churn proxy).
git log --since="12 months ago" --name-only --format= -- '*.py' \
  | sed '/^$/d' | sort | uniq -c | sort -rn | head -20

# Changed-line counts by file; --numstat emits additions/deletions per commit.
git log --since="12 months ago" --format= --numstat -- '*.py'

# Inspect likely bug-fix history for a candidate file.
git log --since="12 months ago" --oneline --grep='fix' -- src/etl/reconcile.py
```

Caveats: rename detection, merge commits, deleted files, generated files, and paths with unusual whitespace need deliberate handling. The first command counts appearances in commit output, not unique semantic changes; the second needs aggregation and should treat binary `-` values carefully. A script should parse Git output robustly instead of relying on shell splitting for production reports.

### Small illustrative dataset

The following dataset is **invented for teaching**; it is not output from the attached project or any real repository. “Churn commits” is the number of commits that touched the file over a fixed sample window. “Complexity” is the maximum Radon cyclomatic complexity among its functions. The values only illustrate ranking logic.

| File | Churn commits | Max complexity | Bug-fix commits | Notes |
|---|---:|---:|---:|---|
| `etl/reconcile.py` | 28 | 18 | 5 | Core reconciliation path |
| `api/client.py` | 24 | 7 | 2 | Frequent contract changes |
| `reports/month_end.py` | 18 | 16 | 4 | Financial close report |
| `models/customer.py` | 6 | 13 | 0 | Complex but relatively stable |
| `utils/formatting.py` | 20 | 3 | 1 | High churn, low complexity |
| `experiments/old_model.py` | 1 | 22 | 0 | Experimental, possibly unused |

A transparent teaching-only **hot-spot score** can be `normalized_churn × normalized_complexity`, where each variable is divided by the maximum in this sample. It is not a standard industry metric and should not be compared across repositories or time windows without re-normalization.

For example, `etl/reconcile.py` has normalized churn `28/28 = 1.0` and normalized complexity `18/22 ≈ 0.818`, giving a score of about `0.818`. `reports/month_end.py` scores `(18/28) × (16/22) ≈ 0.468`. `experiments/old_model.py` scores `(1/28) × (22/22) ≈ 0.036`. The old model's high complexity does not make it a top priority without usage/ownership evidence.

A simple ranking table is sufficient to illustrate the result. Do not present a plot as measured evidence unless the underlying values came from an actual checked-out repository and the extraction procedure is reproducible. For the capstone, generate a plot from your actual Git/Radon data and retain the CSV/script used to create it.

### Bug-fix density and co-change

- **Bug-fix density:** count commits classified as fixes for a file, then inspect the actual diffs/issues. Commit-message grep is a noisy proxy; teams use inconsistent messages, and one commit may touch many files. Report numerator, denominator, and time window rather than an unexplained percentage.
- **Co-change:** find files frequently changed in the same commits. Repeated co-change may indicate a hidden shared rule, a cross-module contract, a broad feature, or simply a common refactor. Validate against the commit content and domain architecture.
- **Temporal coupling:** a file is a temporal companion when it tends to change alongside another file even though the dependency is not explicit in imports. This is evidence to investigate, not proof that the files should be merged.

## 9. Prioritization: choose work that reduces real risk

A practical prioritization process considers:

1. **Impact:** data correctness, security, availability, user/business harm, delivery delays, and incident cost.
2. **Exposure:** frequency of change, number of consumers, volume of records, or blast radius.
3. **Evidence:** defects, incidents, review friction, test failures, repeated work, or reliable metrics.
4. **Effort and uncertainty:** implementation size, migration risk, unknown behavior, test gaps, external dependencies.
5. **Timing:** upcoming releases, contract/schema changes, deprecation deadlines, planned deletion, and team capacity.

A simple score may be useful for sorting, but do not confuse it with objective truth. Example: `priority = impact (1–5) × likelihood (1–5) × exposure (1–3) / effort_days`. Use this only when the team agrees on scales. A security issue may bypass the score due to policy. High uncertainty may call for a discovery spike rather than a large estimate.

### Worked prioritization exercise

Suppose a team has these candidate tasks (all values below are illustrative):

| Task | Impact | Likelihood | Exposure | Effort (days) | Score |
|---|---:|---:|---:|---:|---:|
| Fix reconciliation corruption risk | 5 | 4 | 3 | 4 | 15.0 |
| Stabilize flaky report tests | 2 | 4 | 2 | 2 | 8.0 |
| Simplify stable formatting helper | 1 | 2 | 1 | 1 | 2.0 |
| Upgrade unsupported critical HTTP client | 5 | 3 | 3 | 3 | 15.0 |

Calculation: `impact × likelihood × exposure / effort`. The two 15-point tasks are tied by the heuristic; the decision should then use deadlines, exploitability/support status, reversibility, and dependency order. A prudent sequence might start with an immediate risk-reduction mitigation, then a focused compatibility spike for the client upgrade, while adding characterization tests around reconciliation before changing its logic. The formatting cleanup is deferred unless bundled safely with nearby work. A score is not permission to ignore mandatory security or data-integrity controls.

### Incremental ways to pay down debt

- **Boy Scout rule:** improve a small, relevant piece when already changing it; avoid unrelated diff expansion.
- **Refactor-as-you-go:** include the smallest structural cleanup needed for a feature, separately identifiable in review.
- **Dedicated debt budget:** reserve a transparent capacity allocation (for example, 10–20% if justified by the team's situation), then assess whether it changes outcomes.
- **Targeted spike:** time-box uncertainty; publish findings and a decision rather than an unbounded prototype.
- **Delete and deprecate:** remove dead features safely; track public API deprecation and consumers.
- **Automated dependency upgrades:** use Dependabot/Renovate-style PRs with tests, release notes, compatibility review, and rollback paths.

## 10. Advanced architecture and dependency debt

### Dependency cycles and layer violations

A cycle means two or more modules depend on each other, directly or indirectly. It may make initialization, testing, and independent changes harder. Common remedies include moving a shared abstraction to a lower-level module, inverting a dependency through a `Protocol`, passing callbacks, or restructuring package boundaries. Do not move code to a generic `common.py` merely to break an import cycle; that can create a new dumping ground.

Example boundary:

```python
from typing import Protocol

class CustomerReader(Protocol):
    def get_customer(self, customer_id: str) -> dict[str, object]: ...

class InvoiceService:
    def __init__(self, customers: CustomerReader) -> None:
        self._customers = customers

    def customer_region(self, customer_id: str) -> str:
        customer = self._customers.get_customer(customer_id)
        return str(customer["region"])
```

The service depends on a small interface, not a concrete database implementation. In a mature domain, replace the generic dictionary with a typed domain model. A protocol is useful only if it reflects a real boundary; do not add one for every class.

**Architecture fitness functions** automate rules that should remain true: domain modules cannot import infrastructure modules; API schema compatibility is checked; dependency cycles are rejected; latency or resource budgets are monitored. Keep rules small, explain violations, and introduce them incrementally.

### Churn, ownership, and layer violations together

A high-risk hotspot is more convincing when multiple independent signals align: high complexity, frequent changes, repeated bug fixes, cross-team ownership, a layer violation, and a missing safety net. A low Radon score cannot prove good architecture; static metrics cannot fully observe runtime coupling or domain semantics.

## 11. Test debt and feedback quality

Test debt is not simply “low coverage.” It includes:

- **Missing safety nets:** critical paths lack unit, integration, characterization, or contract tests.
- **Flaky tests:** outcomes depend on time, ordering, shared state, network conditions, or random seeds.
- **Slow suites:** every edit takes too long to validate, encouraging developers to skip checks.
- **Over-mocking:** tests assert implementation choreography and pass while real integrations are broken.
- **Low-value assertions:** tests execute code but do not fail when important behavior changes.
- **Brittle snapshots:** large expected outputs change for irrelevant fields, hiding meaningful differences.

Useful indicators include median and p95 suite duration, rerun/flake rate, changed-line coverage in critical modules, mutation-test results for selected code, and escaped defects. Coverage measures execution, not assertion quality or correctness. Mutation testing can reveal weak tests, but surviving mutants may be equivalent or irrelevant.

Remediation sequence: stabilize the most relied-on checks, add tests at externally observable boundaries, isolate genuine nondeterminism, remove excessive mocks where they hide integration contracts, and split slow integration tests from fast checks without deleting the former.

## 12. Data-engineering and ML/AI technical debt

### Data pipelines

- **Pipeline jungles:** duplicated transformations across scripts, schedulers, notebooks, and services; ownership and lineage are unclear.
- **Schema/contract debt:** producers and consumers silently assume column names, nullability, units, timezone, ordering, or evolution rules.
- **Backfill/replay debt:** transformations are not idempotent, checkpoints are implicit, or late-arriving data corrupts aggregates.
- **Data-quality debt:** missing constraints, weak anomaly detection, undocumented deduplication, and inconsistent definitions of business metrics.
- **Operational debt:** manual recovery, unclear retry policy, unbounded batches, missing resource limits, or no dead-letter/replay procedure.

Controls: versioned data contracts, explicit schema validation, idempotency keys, checkpoint/replay tests, lineage, reconciliation counts, data-quality SLAs, runbooks, and controlled backfill rehearsals. Before refactoring a pipeline, capture row counts, schema, null/duplicate rates, key distributions, checksums where meaningful, and output tolerances. Do not rely on a single checksum if harmless row ordering or floating-point aggregation can differ.

### ML/AI systems

- **Hidden dependencies:** feature definitions, model weights, prompt templates, evaluation sets, package versions, or environment variables are not versioned.
- **Feature entanglement / CACE:** changing one feature unexpectedly changes many downstream predictions or consumers.
- **Training-serving skew:** training and online inference use different preprocessing, defaults, or time semantics.
- **Configuration debt:** scattered flags and undocumented defaults create irreproducible runs.
- **Experiment sprawl:** abandoned code paths and duplicated notebooks survive without ownership.
- **Evaluation debt:** test sets leak into development, metrics are not segmented, prompts change without evals, and model quality regressions go unnoticed.
- **LLM-specific debt:** prompt/model/version sprawl, unstable provider responses, unversioned tools, no safety/evaluation corpus, and unclear fallback behavior.

Controls: version data, code, configs, model artifacts, prompts, and evaluation datasets; fix seeds where deterministic behavior is available; test deterministic preprocessing independently from model sampling; record model/provider versions and request metadata; evaluate offline and in shadow mode before rollout; monitor drift and segment-level metrics. Fixed seeds do not guarantee bitwise determinism across hardware, kernels, providers, or distributed execution.

## 13. Dependency, platform, documentation, and organizational debt

- **Dependency/platform debt:** unsupported Python or library versions, dependencies pinned indefinitely, abandoned forks, end-of-life services, and compatibility assumptions. Maintain an inventory, owner, upgrade cadence, deprecation calendar, and compatibility tests. Dependency age alone is not risk; support status, vulnerability, and exposure matter.
- **Documentation/knowledge debt:** missing runbooks, architecture context, onboarding steps, and single-person ownership. Improve docs near the work, add tested examples, rotate ownership, pair on critical systems, and document decisions with ADRs.
- **Infrastructure debt:** manual deployment, snowflake environments, weak rollback, inconsistent secrets/configuration, and no disaster-recovery practice. Use infrastructure as code and rehearsed recovery, not only more documentation.
- **Security debt:** unsupported packages, weak authorization boundaries, secrets in logs, insufficient validation, or unreviewed threat models. Prioritize by exposure and impact; follow security incident policies where applicable.
- **Process debt:** large PRs, unclear “done” criteria, slow review queues, repeated manual release steps, and no owner for recurring failures. Improve workflow constraints and ownership rather than blaming individuals.

## 14. Rewrite versus refactor

A rewrite replaces a large portion of a system; a refactor changes structure in smaller, behavior-preserving steps. Neither is automatically superior.

Evaluate:

- How well is the existing domain understood?
- Are characterization, contract, and integration tests available?
- How much hidden business behavior and operational knowledge lives in the system?
- Is the platform genuinely obsolete, or merely unpleasant?
- Can the team support old and new implementations during migration?
- What are the opportunity cost, feature-freeze risk, second-system effect, and rollback options?
- Can success be defined with measurable exit criteria?

**Prefer incremental refactoring** when the system still works, behavior is complex, and safe seams can be introduced. **Consider replacement** when a platform is unsupported or fundamentally cannot meet a required constraint, and migration is funded with explicit validation. **Hybrid approaches** often work best: branch by abstraction, strangler migration, modular extraction, adapters, dual-run/shadow comparison, and expand-migrate-contract API/schema changes.

A safe decision record should state the problem, options considered, estimated costs and uncertainty, migration strategy, validation evidence, rollback path, success criteria, and what will not be migrated. “The code is ugly” is not a sufficient business case for a rewrite.

## 15. Public failure case studies and lessons

These examples are widely discussed in public postmortems and engineering writing. They illustrate controls and organizational failure modes; do not infer that a single code smell alone caused the event.

- **Knight Capital (2012):** a software deployment activated legacy functionality on some trading servers; the incident is commonly discussed in relation to deployment consistency, stale code paths, and inadequate rollout safeguards. Lesson: remove obsolete paths deliberately, verify deployment state across the fleet, use canaries/health checks, and have tested kill switches and rollback procedures. Source starting point: U.S. Securities and Exchange Commission, *In the Matter of Knight Capital Americas LLC* (2013), https://www.sec.gov/litigation/admin/2013/34-70694.pdf.
- **left-pad/npm ecosystem (2016):** removal of a small package disrupted downstream builds and highlighted dependency-chain and ecosystem concentration risk. Lesson: inventory transitive dependencies, use lockfiles and reproducible builds, maintain incident response for dependency outages, and avoid assuming a tiny package has tiny blast radius. Context: npm’s public account of the 2016 left-pad incident and subsequent package-policy discussions; treat the event as dependency resilience evidence, not proof that all small dependencies are bad.
- **Machine-learning technical debt:** Sculley et al., *Hidden Technical Debt in Machine Learning Systems* (NeurIPS 2015) describes entanglement, data dependencies, configuration issues, and boundary erosion. Lesson: production ML debt often sits outside model code—in data, interfaces, monitoring, configuration, and reproducibility. Paper: https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html.

For a formal report, cite the specific postmortem or primary source, identify which facts it supports, and separate documented causes from your own engineering interpretation.

## 16. Commands and scripts for a reproducible report

### Record a baseline before changes

Create the output directory before redirecting command output; otherwise the shell fails if `artifacts/` does not already exist.

```bash
mkdir -p artifacts
git rev-parse HEAD
python --version
uv run pytest --durations=20 -q
uv run ruff check .
uv run radon cc -s -a src > artifacts/radon-complexity.txt
uv run radon mi -s src > artifacts/radon-maintainability.txt
uv run vulture src --min-confidence 80 > artifacts/vulture-candidates.txt || true
uv run deptry . > artifacts/deptry.txt || true
```

Store command output as artifacts, note tool versions, and distinguish warnings from failures. The `|| true` examples are for evidence collection only; do not copy them into CI if they suppress a required gate. `radon`, Vulture, and dependency checks can exit nonzero when findings exist or configuration fails, so preserve exit status separately in automated pipelines.

### Basic Python aggregation for an already parsed Git CSV

For a production report, prefer a robust parser for `git log --numstat` or export a CSV with explicit columns. The following small example scores **already-joined rows** from illustrative data. It does not parse Git/Radon output or perform the join; prepare and validate the joined CSV separately before using this scoring function:

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Hotspot:
    path: str
    churn_commits: int
    max_complexity: int
    bug_fix_commits: int


def score_hotspots(rows: list[Hotspot]) -> list[tuple[str, float]]:
    if not rows:
        return []
    max_churn = max(row.churn_commits for row in rows) or 1
    max_complexity = max(row.max_complexity for row in rows) or 1
    scored = [
        (
            row.path,
            (row.churn_commits / max_churn)
            * (row.max_complexity / max_complexity),
        )
        for row in rows
    ]
    return sorted(scored, key=lambda item: item[1], reverse=True)


sample = [
    Hotspot("etl/reconcile.py", 28, 18, 5),
    Hotspot("api/client.py", 24, 7, 2),
    Hotspot("reports/month_end.py", 18, 16, 4),
    Hotspot("models/customer.py", 6, 13, 0),
    Hotspot("utils/formatting.py", 20, 3, 1),
    Hotspot("experiments/old_model.py", 1, 22, 0),
]

for path, score in score_hotspots(sample):
    print(f"{score:.3f}\t{path}")
```

Expected ranking (scores rounded to three decimals; sorted descending):

```text
0.818    etl/reconcile.py
0.468    reports/month_end.py
0.273    api/client.py
0.127    models/customer.py
0.097    utils/formatting.py
0.036    experiments/old_model.py
```

Run the example to reproduce the values. The code computes the scores from the stated formula; the table is illustrative, not measured repository evidence. `bug_fix_commits` is retained as a separate evidence field and is deliberately not part of the numeric score; review it alongside the ranking rather than silently treating it as a calibrated risk weight.

### Plot only with actual joined data

For the capstone, plot `x = churn commits`, `y = maximum cyclomatic complexity`, and label the axes and date window. The CSV below is an **input contract**, not sample measurements:

```csv
path,churn_commits,max_complexity
```

Populate it from the same checked-out revision and documented history window used for the report. The following plotting script consumes that joined CSV; it does not invent rows or compute Git/Radon metrics. It requires `matplotlib` and fails on malformed numeric fields rather than silently dropping them.

```python
import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot repository hot spots from joined Git/Radon data.")
    parser.add_argument("csv_path", type=Path, help="CSV with path,churn_commits,max_complexity columns")
    parser.add_argument("--window", required=True, help="Documented Git history window, e.g. 2025-10-01..2026-10-01")
    parser.add_argument("--output", type=Path, default=Path("hotspots.png"))
    args = parser.parse_args()

    rows = []
    with args.csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"path", "churn_commits", "max_complexity"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise SystemExit(f"CSV must contain columns: {', '.join(sorted(required))}")
        for line_number, row in enumerate(reader, start=2):
            try:
                churn = int(row["churn_commits"])
                complexity = float(row["max_complexity"])
            except (TypeError, ValueError) as exc:
                raise SystemExit(f"Invalid numeric value on CSV line {line_number}: {exc}") from exc
            if churn < 0 or complexity < 0:
                raise SystemExit(f"Negative churn/complexity on CSV line {line_number}")
            rows.append((row["path"], churn, complexity))

    if not rows:
        raise SystemExit("CSV contains no data rows; refusing to create an empty plot")

    fig, ax = plt.subplots(figsize=(10, 6))
    for path, churn, complexity in rows:
        ax.scatter(churn, complexity)
        ax.annotate(path, (churn, complexity), xytext=(4, 4), textcoords="offset points", fontsize=8)
    ax.set_xlabel(f"Commits touching file in window {args.window}")
    ax.set_ylabel("Maximum function/method cyclomatic complexity (Radon)")
    ax.set_title("Repository hot spots — investigation candidates, not automatic priorities")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(args.output, dpi=160)
    plt.close(fig)
    print(f"Wrote {args.output} using {len(rows)} CSV rows; verify the input revision and filters in the report.")


if __name__ == "__main__":
    main()
```

A scatter plot can reveal quadrants, but it cannot decide priority without defect, impact, ownership, and upcoming-change context. The script validates the CSV's basic shape and numeric values; it cannot verify that the rows came from the correct revision or that exclusions were appropriate. Preserve the CSV, extraction script, tool versions, commit SHA, time window, and filter rules. Do not create a chart from fictional rows and label it as measured repository evidence.

## 17. Common mistakes and troubleshooting

- **Treating every smell as urgent:** rank by impact, exposure, evidence, and effort. A stable ugly helper may be harmless; a small risky boundary can be urgent.
- **Fixing symptoms only:** extracting a long function without clarifying responsibilities can simply move complexity around.
- **Over-abstraction:** turning every conditional into a class hierarchy increases indirection. Choose the simplest design that supports actual variation.
- **Metric gaming:** lowering function length or complexity while increasing coupling and indirection is not improvement. Review representative changes and outcomes.
- **Assuming unused means safe to delete:** plugins, reflection, entry points, and runtime registration can evade static analysis.
- **Using commit-message grep as ground truth:** bug-fix labels are incomplete and inconsistent; validate with diffs and incident records.
- **Ignoring generated/vendor files:** they distort complexity and churn; document exclusions and do not conceal first-party vendored code that the team owns.
- **Mixing cleanup and behavior changes:** separate them into reviewable commits with explicit intent and tests.
- **Using one score as an absolute ranking:** security policy, data integrity, legal deadlines, and migration dependencies can override it.
- **No baseline:** without a fixed revision, time window, tool version, and scope, before/after metrics are not comparable.
- **Treating coverage as quality:** check assertions, branch behavior, mutation sensitivity, and real integration boundaries.
- **Confusing technical debt with blame:** document system conditions, trade-offs, and ownership; do not label people as debt.

If a tool command fails, check the installed version, project configuration, source path (`src` versus package root), and exit code. Read the tool's help output before relying on a rule name. For metrics that cannot be collected reliably, state the limitation rather than fabricating a number.

## 18. Exercises with solutions

### Exercise 1 — classify the smell

```python
def send_invoice(customer, amount, currency, tax_rate, due_date, locale):
    # build message, format money, calculate tax, save invoice, send email...
    ...
```

**Question:** Identify at least two possible smells and a safe next step.

**Solution:** The long parameter list may be a data clump if these values form a stable invoice context; the function may be a Long Function if it combines formatting, tax calculation, persistence, and messaging. First map responsibilities and existing behavior, add characterization tests, then extract cohesive units. Introduce a parameter object only if the fields share domain meaning. Do not split merely because the signature is long.

### Exercise 2 — rank hotspots

Use the six-row illustrative dataset in Section 8. Which file should be investigated first?

**Solution:** `etl/reconcile.py` has the highest normalized churn × complexity score (0.818) and five bug-fix commits in the sample, so it is a strong candidate. Confirm its business criticality and inspect commits/incidents before deciding the remediation. `reports/month_end.py` is a second candidate. The experimental model should not be prioritized based on complexity alone.

### Exercise 3 — debt principal versus interest

A dependency upgrade is estimated at four days. The current unsupported client has caused two production incidents and blocks security patches. A formatting helper is estimated at one day and has no known defects.

**Solution:** The upgrade has higher recurring interest and operational/security exposure despite greater principal. Start with a compatibility spike, contract tests, and a staged rollout. Defer formatting cleanup unless it is a low-risk adjacent change.

### Exercise 4 — choose a quality gate

A legacy repository has many functions above complexity grade B. A hard gate on all existing code would fail every PR.

**Solution:** Capture a baseline, gate newly added/changed functions or require no regression in changed-file metrics, and ratchet the limit down as hotspots are remediated. Keep exceptions explicit and time-bound. The purpose is to stop debt growing, not to hide existing debt.

### Exercise 5 — when is duplication acceptable?

Two services have nearly identical tax calculations but serve different jurisdictions with different release calendars.

**Solution:** Do not immediately extract a shared helper. Verify whether the rules are legally identical and must evolve together. If they differ or need independent release/ownership, duplication may be safer. If a common rule exists, create a versioned shared domain contract and test jurisdiction-specific cases.

### Exercise 6 — rewrite or refactor?

A pipeline has a 200-line transformation, no tests, implicit timezone assumptions, and downstream reports that depend on its quirks.

**Solution:** Avoid a big-bang rewrite. Characterize output for representative datasets, record suspicious behavior, establish schemas and data-quality checks, introduce seams around I/O, and extract small pure transformations. Consider a parallel/shadow implementation after the contract is understood. Explicitly separate intended behavior changes from structural refactoring.

## 19. Capstone — Technical Debt Report

Produce a report for the practice repository (the module roadmap describes a deliberately messy `legacy-ledger`-style ETL/reporting project). The report must be evidence-backed; do not use the illustrative data from this lesson as if it came from your repository.

### Required deliverables

1. **One-page management summary**: business impact, top risks, recommended investment, three-month milestones, and measurable outcomes in plain language.
2. **Top ten smells**: for each, provide file/function, smell category, code excerpt or tool evidence, why it matters, confidence, likely remediation, and test/safety prerequisite. Include evidence, not only labels.
3. **Hot-spot plot**: join actual Git history churn (document the exact definition and time window) with Radon complexity at a recorded commit. Label axes, identify exclusions, retain input CSV and script, and interpret the highest-risk points.
4. **Debt register**: at least the top actionable entries with impact, likelihood/risk, effort range, owner, dependencies, priority, and target/trigger. Link issues and ADRs where appropriate.
5. **Prioritized three-month remediation plan**: staged work with owners, dependencies, rollout/rollback plan, and quality gates. Include a mix of quick risk reduction, test safety-net work, and structural remediation.
6. **Measurement plan**: baseline and target for relevant indicators (e.g., critical-path complexity, high-risk coverage/mutation evidence, test flake rate, pipeline incidents, deployment/change-failure measures). State how each is measured and limitations.
7. **Evidence appendix**: tool versions, commands, commit SHA, report generation steps, and any unavailable/low-confidence measurements.

### Suggested three-month sequence

- **Month 1 — Establish trust and reduce immediate risk:** characterize top critical flows, fix or mitigate urgent security/data-integrity issues, create baseline metrics, assign owners, and make the first changed-line quality gate.
- **Month 2 — Reduce the highest-interest hot spots:** refactor one or two high-churn/high-complexity paths in small tested steps; stabilize flaky critical tests; introduce one architecture contract; pilot a dependency upgrade.
- **Month 3 — Make improvement durable:** finish a staged migration where justified, add quality ratchets and runbooks, validate before/after metrics, and review whether incident rate, lead time, and test feedback improved.

This is a template, not a prescription. Adjust based on actual evidence, release calendars, team capacity, security requirements, and data criticality.

### Acceptance criteria

- [ ] Ten smells are backed by repository-specific evidence and ranked by consequence, not appearance.
- [ ] Hot-spot plot is generated from actual Git/Radon data at a recorded revision; no illustrative numbers are misrepresented as measured.
- [ ] Debt register has owners, impact, effort ranges, risks, dependencies, and actionable next steps.
- [ ] Three-month plan has milestones, quality gates, and rollback/mitigation options.
- [ ] One-page summary translates engineering debt into business risk, delivery lead time, incident cost, and reliability.
- [ ] Metrics have definitions, baselines, targets, time windows, and limitations.
- [ ] Findings distinguish symptoms from confirmed defects and intentional trade-offs.

## 20. Self-assessment

Answer without looking back, then use the sections above to close gaps.

1. Why is a code smell not proof of a defect?
2. Name the five smell families and give two examples from each.
3. When is a long function acceptable, and what evidence would make it a priority?
4. Explain principal versus interest in technical debt with a production example.
5. What is the difference between deliberate/inadvertent debt and prudent/reckless debt?
6. Why is complexity × churn more useful than either metric alone, and what does it still miss?
7. How can commit-message grep mislead bug-fix density analysis?
8. Describe two causes of architectural debt and a suitable fitness function for each.
9. Give three examples of data/ML debt that live outside model algorithm code.
10. When might duplicated logic be safer than a shared abstraction?
11. Why is a changed-line quality ratchet often safer than enforcing a strict threshold across a legacy repository?
12. What evidence would justify a rewrite rather than incremental refactoring?
13. Which DORA metrics can help communicate outcomes, and why should they not be used as a simplistic score for one developer?
14. What makes a Technical Debt Report actionable rather than a list of complaints?

**Ready-for-practice standard:** You can show evidence for a smell, explain its likely cost, propose a proportionate intervention, state how you will verify it, and identify what remains uncertain.

## References and further reading

- Martin Fowler, *Refactoring: Improving the Design of Existing Code*, 2nd ed. (2018); refactoring.com.
- Martin Fowler, “Technical Debt Quadrant,” martinfowler.com/bliki/TechnicalDebtQuadrant.html.
- Ward Cunningham, “The WyCash Portfolio Management System” (1992), origin of the technical-debt metaphor.
- Adam Tornhill, *Your Code as a Crime Scene* (2015), code churn and hotspot analysis.
- Nicole Forsgren, Jez Humble, and Gene Kim, *Accelerate* (2018), delivery performance and operational outcomes.
- Sculley et al., “Hidden Technical Debt in Machine Learning Systems,” NeurIPS 2015: https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html.
- U.S. Securities and Exchange Commission, *In the Matter of Knight Capital Americas LLC* (2013): https://www.sec.gov/litigation/admin/2013/34-70694.pdf.
- Official tool documentation: Ruff (https://docs.astral.sh/ruff/), Radon (https://radon.readthedocs.io/), Xenon (https://xenon.readthedocs.io/), Vulture (https://github.com/jendrikseipp/vulture), Pylint (https://pylint.readthedocs.io/), and deptry (https://deptry.com/).

---

**Core principle:** smell detection is the start of an investigation. Remediate the risks that matter, keep behavior and architecture claims evidence-based, and measure whether the system became easier and safer to change.
