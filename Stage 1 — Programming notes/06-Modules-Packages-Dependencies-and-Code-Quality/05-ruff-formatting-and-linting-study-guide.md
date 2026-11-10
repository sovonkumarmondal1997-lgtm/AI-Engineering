# 05 — Ruff, Formatting, and Linting
## Complete Chapter Summary, Project-Tree Assessment, Exercises, Debugging Lab, and Review Answers

**Roadmap:** Stage 1 — Programming & Computational Thinking  
**Module:** 06 — Modules, Packages, Dependencies, and Code Quality  
**Lesson:** 05 — Ruff, Formatting, and Linting  
**Prerequisites:** imports/modules, project layout, `pyproject.toml`, `uv`, dependency management, files/CSV, CLI, exit codes, Git basics.

---

# Part A — Complete Chapter Summary

## 1. Why code quality matters

Code quality means how easy a codebase is to read, trust, maintain, and change safely—not merely whether it runs.

Consider:

```python
import os
import sys

def calculate(x,y):
    unused_variable = 10
    return x+y
```

This program may run, but it has several quality problems:

- `os` and `sys` are unused imports: they falsely suggest dependencies.
- `x,y` has inconsistent spacing: a formatting problem.
- `unused_variable` is dead code: it adds noise and may indicate unfinished logic.
- `x+y` lacks conventional spacing.

Keep these categories separate:

| Category | Meaning | Example |
|---|---|---|
| Formatting | Visual layout | `x+y` instead of `x + y` |
| Style | Project-wide convention | Mixed quote conventions |
| Correctness-related | Likely or actual bug | Undefined variable |
| Maintainability | Makes future changes harder | Unused code |

A human reviewer should focus on design, business logic, edge cases, and correctness. Automated tools consistently handle repetitive layout and pattern checks.

## 2. What code formatting is

Formatting is the visual arrangement of source code: spacing, indentation, blank lines, line breaks, quotes, and trailing commas. Its purpose is to improve readability without changing program behaviour.

Python indentation is special: it defines code blocks and is syntactically meaningful. Incorrect indentation can change the program or cause an error. Most other formatting choices, such as spaces around operators, are not semantically meaningful.

Before:

```python
def calculate_total(items):
    total=0
    for item in items:
        total+=item["price"]
    return total
```

After:

```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item["price"]
    return total
```

Both compute the same result. The second is easier to scan and follows a consistent convention.

Formatting covers spacing, blank lines, line length, quote style, trailing commas, and layout of function definitions, collections, calls, classes, and multi-line expressions.

## 3. What a formatter is and how it works

A formatter automatically rewrites source into a consistent layout. A good formatter is:

- **Automatic:** makes layout decisions without a human editing each line.
- **Deterministic:** the same input and formatter configuration produce the same output.
- **Opinionated:** offers a limited set of style choices to avoid endless debate.
- **Idempotent:** formatting already-formatted code again makes no further changes.

Conceptual process:

```text
Python source
    ↓
Parse Python syntax
    ↓
Understand code structure (conceptually an AST)
    ↓
Apply layout rules
    ↓
Render consistently formatted source
```

A formatter must understand syntax, not blindly replace text. Replacing every `x+y` with `x + y` could alter a string literal. A syntax-aware formatter distinguishes code from data and reformats the structure safely.

## 4. What linting is

A **linter** statically analyzes source code without running the program. It detects suspicious patterns such as unused imports, unused variables, undefined names, and other style or correctness-adjacent issues.

```python
import os

def greet(name):
    unused = 10
    return "Hello " + name
```

A linter can report `os` as unused and `unused` as assigned but never read. These are not syntax errors; the function can still return `"Hello Alice"`. They are signals that the code may contain unnecessary work or a mistake.

Terminology:

- **Rule:** one named check, e.g. “unused import”.
- **Violation:** a location where the rule is triggered.
- **Diagnostic:** the message reporting the rule, location, and explanation.
- **Static analysis:** examining code structure without executing it.

A linter can identify an undefined name such as `nam`, but it cannot generally determine whether a mathematically valid formula returns the correct business answer. Tests are needed for runtime behaviour. Whether unreachable code is reported depends on enabled rules and Ruff version; do not assume every code-review concern has a Ruff diagnostic.

## 5. Formatter vs. linter vs. type checker vs. tests

| Tool | Purpose | Example |
|---|---|---|
| Formatter | Consistent source layout | `ruff format` |
| Linter | Pattern-based source diagnostics | `ruff check` |
| Type checker | Type consistency across code | mypy, Pyright |
| Test framework | Actual behaviour against expectations | pytest |

Formatting does not prove correctness. Linting does not verify business logic. Type checking does not prove that a calculation is correct. Tests only verify cases actually exercised.

A quality pipeline uses these layers together. The chapter's conceptual order is formatting, linting, type checking, tests, then build/CI. In the concrete local Ruff workflow, run lint auto-fixes first, formatting second, then a final lint check; the formatter should have the last word on layout.

## 6. What Ruff is

**Ruff** is a modern Python tool combining a linter and a formatter in one fast program. It consolidates functionality that historically required separate tools and plugins.

Ruff does not replace:

- pytest or other tests;
- a dedicated type checker;
- dependency vulnerability scanning;
- secret detection or comprehensive SAST;
- code review, architecture decisions, or domain knowledge.

It is a development tool, not a runtime dependency of the application.

## 7. Installing Ruff with `uv`

Add Ruff to the development dependency group:

```bash
uv add --dev ruff
```

This updates the project's `pyproject.toml` and `uv.lock`. Ruff belongs in development dependencies because developers and CI use it to check code; the production application does not need Ruff to execute.

A representative declaration is:

```toml
[dependency-groups]
dev = [
    "ruff>=0.5",
]
```

The version range expresses acceptable releases; `uv.lock` records the selected version for reproducibility. Run it through the project's environment:

```bash
uv run ruff --version
```

Locking Ruff matters: if developers and CI use different Ruff versions, they may see different rules or formatting output.

## 8. Four basic Ruff commands

### Lint the project

```bash
uv run ruff check .
```

Checks Python files under the current directory using the active rules and configuration. It reports diagnostics and does not rewrite files.

Target a file or directory:

```bash
uv run ruff check path/to/file.py
uv run ruff check src/
```

Run from the intended project directory or provide an explicit path.

### Format the project

```bash
uv run ruff format .
```

Rewrites files in place to the formatter's canonical layout. This changes files, so inspect the diff afterward.

### Verify formatting without changing files

```bash
uv run ruff format --check .
```

Reports files that would be reformatted and returns a non-zero status when formatting is not compliant. It does not modify source. This is suitable for CI.

### Automatic lint fixes

```bash
uv run ruff check --fix .
```

Applies available safe fixes for supported lint rules. It modifies files, unlike plain `ruff check`.

The distinctions:

| Command | Reports lint issues | Changes source |
|---|---:|---:|
| `ruff check` | Yes | No |
| `ruff format` | No; formats layout | Yes |
| `ruff check --fix` | Yes | Yes, for fixable rules |
| `ruff format --check` | Reports formatting drift | No |

## 9. Ruff rule codes and rule families

Each lint rule has a code consisting of a family prefix and a number. Example: `F401` means an unused import; `F` identifies the family.

| Family | General purpose |
|---|---|
| `F` | Pyflakes-derived: unused imports/variables, undefined names |
| `E` / `W` | pycodestyle style checks |
| `UP` | Modernize old Python syntax (pyupgrade) |
| `B` | Bug-prone patterns (flake8-bugbear), e.g. mutable defaults |
| `SIM` | Simplify unnecessarily complex code |
| `I` | Import sorting/organization (isort-derived) |
| `N` | Naming conventions |
| `A` | Shadowing built-in names |
| `C4` | Comprehension idioms |
| `PIE` | Miscellaneous clarity/correctness checks |
| `RUF` | Ruff-specific rules |

Do not enable every rule family automatically. Select rules based on value, project maturity, and acceptable noise.

Example `F401`:

```python
import os

def greet(name):
    return f"Hello, {name}"
```

`os` is unused. Remove it:

```python
def greet(name):
    return f"Hello, {name}"
```

Example `B006`, a mutable default:

```python
def add_item(item, items=[]):
    items.append(item)
    return items
```

The default list is created once when the function is defined, so calls can share the same list. Correct it with a `None` sentinel:

```python
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

## 10. Common lint problems

### Unused import — `F401`

```python
import json
import os

def load_config(path):
    with open(path) as f:
        return json.loads(f.read())
```

`os` is not used. Remove it.

### Unused variable — `F841`

```python
def process(records):
    count = 0
    total = 0
    for record in records:
        total += record["value"]
    return total
```

`count` is never read or used. Remove it if genuinely unnecessary; if it was meant to count records, implement that intention.

### Undefined name — `F821`

```python
def greet(name):
    return f"Hello, {nam}"
```

`nam` is not defined. Correct it to `name`. Ruff can detect this without running the function; execution would raise `NameError`.

### Unreachable code

```python
def status(code):
    return "ok"
    print("this line never runs")
```

The print is unreachable because the function already returned. Remove it or restructure the logic. The chapter treats this as a general review concern, not a guaranteed Ruff diagnostic.

### Redundant Boolean comparison

```python
if is_valid == True:
    process()
```

Prefer:

```python
if is_valid:
    process()
```

### Old class syntax

```python
class Config(object):
    pass
```

Modern Python:

```python
class Config:
    pass
```

### Old string formatting

```python
message = "Hello, %s" % name
```

Modern equivalent:

```python
message = f"Hello, {name}"
```

## 11. Safe and unsafe automatic fixes

Ruff can mechanically fix some diagnostics:

```bash
uv run ruff check --fix .
```

Examples include removing an unused import and certain unambiguous syntax modernizations. Ruff applies fixes it classifies as safe by default. Safe is a tool classification and design intent, not mathematical proof that no behaviour can change.

Some fixes are classified as unsafe because they may affect runtime behaviour or comments. They require explicit opt-in:

```bash
uv run ruff check --fix --unsafe-fixes .
```

Use unsafe fixes cautiously and review them carefully. An unused variable may be dead code, or it may reveal a missing use that should be restored. A tool cannot infer the author's intent in every case.

Always inspect changes:

```bash
uv run ruff check --fix .
git diff
```

Principle: automate mechanical edits; manually judge semantic changes.

## 12. Import sorting

A conventional import layout groups standard library, third-party, and local application imports:

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

Ruff's `I` family checks and can fix ordering.

Before:

```python
from myapp.config import load_config
import sys
import requests
import json
```

After:

```python
import json
import sys

import requests

from myapp.config import load_config
```

Consistent import ordering makes dependencies easier to scan and reduces noisy diffs.

## 13. Ruff formatter behaviour

Ruff's formatter is opinionated. It handles line wrapping, quotes, trailing commas, indentation, blank lines, function signatures, collections, and long expressions.

Before:

```python
def process_order(order_id, customer_name, items, discount_percentage=0, apply_tax=True, notes=None):
    pass
```

After:

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

The purpose is predictable layout, not changing the function's business logic.

## 14. Correct local command order

The chapter's recommended local workflow:

```bash
uv run ruff check --fix .
uv run ruff format .
uv run ruff check .
```

Why this order?

1. `ruff check --fix` makes available lint corrections, including import changes.
2. `ruff format` applies the final layout after those edits.
3. `ruff check` reports anything still requiring manual attention.

Ruff's formatter does not sort imports; the linter's `I` rules do that. The final check confirms remaining violations.

## 15. Configure Ruff in `pyproject.toml`

Minimal example:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
```

Expanded example:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
exclude = ["build", "dist"]
extend-exclude = ["migrations"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
ignore = ["E501"]
extend-select = ["SIM"]
per-file-ignores = { "tests/*.py" = ["F401"] }

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
```

Settings:

- `line-length`: target maximum line length for formatting and relevant lint checks.
- `target-version`: Python version Ruff assumes for syntax and modernization decisions.
- `exclude`: exclusion patterns; setting this replaces the base list.
- `extend-exclude`: adds patterns to built-in/default exclusions.
- `include`: replaces the default included file patterns.
- `extend-include`: adds patterns to the applicable include set.
- `lint.select`: selects active rules, replacing Ruff's default selection.
- `lint.ignore`: disables selected rule codes.
- `lint.extend-select`: adds rule families without replacing the existing selection.
- `lint.per-file-ignores`: exceptions for matching files.
- `format.quote-style`: `"double"` or `"single"`.
- `format.indent-style`: `"space"` or `"tab"`; spaces are conventional for Python.
- `format.line-ending`: line-ending behaviour such as `"auto"`.

Modern Ruff puts lint configuration under `[tool.ruff.lint]`. Older tutorials may show legacy keys directly under `[tool.ruff]`. Confirm the schema supported by your installed version rather than copying outdated configuration. `extend-ignore` is deprecated in current configuration guidance; use `ignore`.

## 16. Selecting and ignoring rules

Example:

```toml
[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501", "F401"]
extend-select = ["UP", "B"]
```

- `select` replaces the default rule selection.
- `ignore` disables specific rules within the selection.
- `extend-select` adds rules to the selected set.

A rule may be ignored because it conflicts with a deliberate project convention, creates a genuine false positive, or is being deferred during a gradual migration. An ignore should encode policy, not hide work. Document why it exists and periodically revisit it.

There are different scopes: project-wide ignore, per-file ignore, directory/file-pattern ignore, and inline suppression. Prefer the narrowest scope that fits.

## 17. Inline `noqa`

For one justified occurrence:

```python
import used_only_conditionally  # noqa: F401
```

A rule-specific `# noqa: F401` is better than bare `# noqa`, which suppresses every rule on that line and can hide future unrelated issues.

A legitimate case is an import needed only for a registration side effect:

```python
import side_effect_only_module  # noqa: F401 -- imported for registration side effect
```

Explain the reason. Do not use suppression as the default response to inconvenient diagnostics.

## 18. Per-file ignores

Some files have a legitimate purpose that differs from ordinary application modules:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/*.py" = ["F401"]   # only if deliberate fixture/side-effect imports require it
"__init__.py" = ["F401"]  # intentional public API re-exports
```

Potential cases include tests with side-effect imports, `__init__.py` public re-exports, generated migrations, compatibility modules, and generated files. Being a test or script alone is not sufficient justification. Use a narrow glob and rule list, and document the reason.

## 19. Generated code and exclusions

Usually exclude code your team does not maintain manually:

- generated source and schemas;
- vendored third-party code;
- build output such as `build/` and `dist/`;
- virtual environments such as `.venv`;
- caches and temporary files.

```toml
[tool.ruff]
exclude = ["build", "dist", ".venv", "__pycache__"]
extend-exclude = ["src/myapp/generated"]
```

`exclude` sets the exclusion list; `extend-exclude` adds to Ruff's built-in defaults. Do not manually reformat generated code: regeneration will overwrite the edit. Exclude it instead.

## 20. Target Python version

```toml
[tool.ruff]
target-version = "py312"
```

This tells Ruff which Python language features it may assume when checking or suggesting modern syntax. It is related to, but distinct from, `[project].requires-python`.

- `requires-python` declares the versions your project supports.
- `target-version` tells Ruff what version to target.

Keep them consistent. If the project supports Python 3.10 but Ruff targets 3.12, Ruff may suggest syntax unavailable on Python 3.10.

## 21. Modernization rules — `UP`

The `UP` family suggests replacing older but working Python idioms with modern equivalents supported by `target-version`.

Old formatting:

```python
message = "Hello, %s! You are %d years old." % (name, age)
```

Modern f-string:

```python
message = f"Hello, {name}! You are {age} years old."
```

Old class declaration:

```python
class Config(object):
    pass
```

Modern class:

```python
class Config:
    pass
```

Older typing import:

```python
from typing import List

def get_names() -> List[str]:
    ...
```

Modern syntax, when the target Python supports it:

```python
def get_names() -> list[str]:
    ...
```

Formatting changes layout. Linting flags patterns. Modernization proposes a clearer current idiom even when the old code works. Check `target-version` before enabling or auto-fixing `UP` rules.

## 22. Configuration design

A minimal new-project configuration:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.format]
quote-style = "double"
```

A beginner rule selection:

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

A more production-oriented selection:

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "N", "A", "C4", "PIE", "RUF"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"tests/*.py" = ["F401"]
"__init__.py" = ["F401"]
```

The `E501` decision needs thought: the formatter targets line length but cannot wrap every long string, comment, or URL. If `E501` is ignored, those remaining long lines are not reported by that rule.

Good configuration balances consistency, maintainability, strictness, developer experience, CI reliability, and gradual adoption. A smaller understood rule set is better than a huge unexplained configuration.

## 23. Editor/IDE integration

Ruff can provide inline diagnostics and formatting inside an editor. In VS Code, the Python extension provides Python language support and a Ruff integration connects Ruff's linter/formatter.

Conceptually:

```text
edit/save
   ↓
formatter (if configured)
   ↓
linter
   ↓
diagnostics appear in editor
   ↓
developer fixes issues
```

Editors may offer quick fixes for individual diagnostics. Editor integration is convenient but cannot be the only enforcement: contributors may have different or missing local configurations. Pre-commit and CI provide independent layers.

## 24. Format on save

- **Format on save:** formatter runs each time a file is saved.
- **Lint on save:** lint diagnostics refresh on save (or as you type).
- **Fix on save:** selected auto-fixable lint violations are corrected automatically.

Benefits: immediate feedback and fewer manual commands. Trade-offs: edits may happen without a separate deliberate command; aggressive auto-fixing can interfere with incomplete code while typing. Always inspect `git diff` before committing.

## 25. Pre-commit

`pre-commit` is a framework that runs configured checks immediately before a Git commit. If a hook fails, the commit is rejected.

```text
git commit
    ↓
pre-commit hooks
    ↓
Ruff formatter/linter
    ↓
commit accepted or rejected
```

It is an early local gate. It can be bypassed by a developer, so it is not a substitute for CI.

## 26. CI/CD integration

A professional pipeline:

```text
local editor checks
    ↓
pre-commit
    ↓
pull request
    ↓
CI: formatting verification
    ↓
CI: lint check
    ↓
CI: tests
    ↓
build/deploy
```

CI should use a clean, reproducible environment and the committed lock file. For strict dependency verification:

```bash
uv sync --locked
```

This prevents CI from silently changing a stale lock. CI independently checks code even if the developer forgot, skipped, or misconfigured local tools. Branch protection can require successful checks before merge.

## 27. Format checking in CI

```bash
uv run ruff format --check .
```

Developers apply formatting locally. CI verifies only; it should not silently rewrite a pull request. A non-zero result means formatting is not compliant and should fail the check.

## 28. Linting in CI

```bash
uv run ruff check .
```

If any enabled rule reports a violation, the command exits non-zero and CI fails. The exit status drives automation; the printed diagnostic helps a human understand what to fix.

## 29. Exit codes and automation

Conceptually:

```text
ruff check .
exit 0       → no violations under the current configuration
exit nonzero → one or more violations; command failed
```

`ruff format --check` also returns non-zero if files need formatting. The exit code is what shell scripts and CI use to gate the next step.

```bash
uv run ruff format --check . && uv run ruff check . && uv run pytest
```

The `&&` operator runs the next command only if the previous command exits successfully. This is fail-fast command composition.

## 30. Ruff and Git

Recommended local workflow:

```text
edit code
  ↓
ruff check --fix .
  ↓
ruff format .
  ↓
git diff
  ↓
run tests
  ↓
commit
```

Review all automatic changes. First-time formatting can create a large diff unrelated to the feature. Keep formatting-only changes in a separate commit or pull request from logic changes so review remains understandable.

## 31. Ruff does not replace tests

Example:

```python
def average(numbers):
    return sum(numbers) / len(numbers) - 1  # incorrect formula
```

Ruff may report no issue. A type checker may also accept the types. Yet the result is wrong:

```pycon
>>> average([2, 4, 6])
3.0
```

The correct average is `4.0`. A test exposes the bug:

```python
def test_average():
    assert average([2, 4, 6]) == 4.0
```

Formatting checks layout, linting checks patterns, type checking checks type consistency, unit tests verify specific input/output pairs, integration tests verify components together, and system tests verify end-to-end behaviour. Each catches different failures.

## 32. Ruff does not replace type checkers

A type checker follows values across functions and verifies declared/inferred type compatibility.

```python
def get_user_age(user: dict) -> int | None:
    return user.get("age")

def print_next_birthday_age(age: int) -> None:
    print(age + 1)

age = get_user_age({"name": "Alice"})
print_next_birthday_age(age)
```

`age` may be `None`, but `print_next_birthday_age` requires `int`. A type checker can flag this mismatch. Ruff's ordinary linting does not perform this deep cross-function type-flow analysis. Production projects commonly use Ruff and a dedicated type checker separately.

## 33. Ruff is not comprehensive security scanning

Ruff has some security-adjacent pattern rules, but it is not a complete security tool. It does not comprehensively scan:

- dependency versions against vulnerability databases;
- committed secrets and credentials;
- all application security risks (SAST);
- the dependency supply chain.

Use dedicated dependency vulnerability scanners, secret detection, and security review. Treat Ruff's security-related rules as one small defence-in-depth layer, not a substitute.

## 34. Gradual rule-management strategy

A practical six-stage rollout:

1. **Formatter only:** establish consistent layout first.
2. **Basic linting:** enable a small selection such as `E`, `F`, and perhaps `I`.
3. **Safe fixes:** use `ruff check --fix`, reviewing `git diff`.
4. **Additional families:** add `UP`, `B`, and `SIM` deliberately.
5. **CI enforcement:** make formatting and lint checks required once local violations are manageable.
6. **Mature policy:** expand coverage and retire legacy exceptions over time.

A big-bang rollout can overwhelm a legacy project with thousands of findings, false positives, and developer friction. Gradual adoption makes the work manageable.

## 35. Migrating a legacy project

Nine-step migration:

1. Inspect repository structure and conventions.
2. Establish a baseline by running `ruff check .` and recording violations.
3. Run `ruff format .` as a separate, reviewed formatting-only commit.
4. Review lint diagnostics.
5. Classify each issue: safe fix, small manual fix, deeper investigation, or justified exception.
6. Apply safe fixes and inspect `git diff`.
7. Add only justified, documented exclusions.
8. Enable rule families incrementally.
9. Enforce checks in CI when the violation count is manageable.

Do not enable hundreds of rules at once without a remediation plan. Prioritize meaningful correctness-adjacent findings over cosmetic noise.

## 36. False positives and engineering judgment

- **False positive:** a rule fires, but the specific case is legitimate.
- **False negative:** a real issue is not caught by the enabled rules.

A linter uses patterns and heuristics; it cannot fully understand intent. Both false positives and false negatives are unavoidable.

When a diagnostic seems wrong:

1. Understand what the rule checks and why.
2. Inspect the exact context.
3. Decide whether the code is wrong or the rule does not fit this legitimate case.
4. If suppression is justified, use the narrowest scope and document why.

Do not reflexively silence warnings.

## 37. Performance and scale

Fast tooling matters because Ruff may run during editing, on every commit, in large repositories, and on every CI pull request. Slow tools interrupt developer flow and increase CI cost. Ruff is designed with performance as a first-class goal; avoid quoting universal speed multipliers because actual results depend on hardware, project size, and comparison.

## 38. Monorepos and large projects

A **monorepo** contains multiple projects/packages in one repository.

At scale, consider:

- a shared baseline configuration;
- package-specific exceptions using justified path patterns;
- generated code exclusions;
- CI checks scoped to affected packages where the CI platform supports it;
- gradual rollout across teams.

Do not assume configuration inheritance across multiple `pyproject.toml` files. Verify the exact behaviour supported by the installed Ruff version.

## 39. Library vs. application policy

Different project types need different quality emphasis:

- **Published library:** public API is a long-lived contract; naming (`N`) and modernization (`UP`) discipline can matter greatly, while `target-version` must reflect the supported Python matrix.
- **Backend service:** calibrate strictness to reliability and team velocity.
- **CLI:** keep style consistent and pay attention to CLI, logging, and exit-code behaviour.
- **Data pipeline:** correctness-adjacent `F` and `B` rules are valuable because silent data errors can be costly.
- **ML project:** distinguish exploratory notebooks/scripts from production serving code.
- **AI agent system:** apply strict checks to operationally critical components, while treating exploratory code proportionately.

The rule is to align strictness with operational risk, not maximize rule count everywhere.

## 40. Production AI/ML project example

Example project:

```text
ml-pipeline/
├── src/ml_pipeline/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── data_processing.py
│   └── inference.py
├── tests/
│   ├── test_data_processing.py
│   └── test_inference.py
├── scripts/
│   └── explore_dataset.py
├── pyproject.toml
├── uv.lock
└── README.md
```

Example configuration:

```toml
[project]
name = "ml-pipeline"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pydantic>=2.0,<3.0"]

[dependency-groups]
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

The example's ignores are illustrative, not automatic recommendations: allow them only if the relevant test imports or script patterns genuinely justify them.

Workflow:

```bash
uv run ruff check .
uv run ruff check --fix src/
uv run ruff format .
git diff
uv run pytest
```

Data-processing code benefits from correctness-adjacent checks; inference code benefits from consistent quality controls; exploratory scripts may have narrowly justified exceptions.

## 41. Complete professional workflow

The complete lifecycle:

1. Create project with `uv init` and a deliberate layout.
2. Add Ruff as a dev dependency: `uv add --dev ruff`.
3. Configure Ruff in `pyproject.toml`.
4. Write application code.
5. Run `uv run ruff check .`.
6. Apply safe fixes with `uv run ruff check --fix .`.
7. Run `uv run ruff format .`.
8. Review `git diff`.
9. Run `uv run pytest`.
10. Commit an atomic, reviewed change.
11. Run pre-commit checks.
12. Open a pull request.
13. CI runs `ruff format --check` and `ruff check` from a locked environment.
14. CI runs tests.
15. Merge only when required checks pass; deploy through the project's controlled process.

## 42. Complete worked example project

The source uses a small `demo/` project and deliberately problematic `orders.py`:

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
        if (total>0)==True:
            total=total*(1+self.tax_rate)
        return total

def load_items(path) -> List[dict]:
    with open(path) as f:
        return json.loads(f.read())
```

Run formatter:

```bash
uv run ruff format .
```

This fixes layout but not logic or naming issues. Then lint:

```bash
uv run ruff check .
```

Illustrative diagnostics include unused `os` (`F401`), unnecessary `object` inheritance (`UP004`), class naming (`N801`), unused local variable (`F841`), comparison to `True` (`E712`), and old `typing.List` (`UP035`).

Apply safe fixes and inspect:

```bash
uv run ruff check --fix .
git diff
```

Ruff can remove the unused import and modernize class inheritance. The class rename, unused variable intention, and Boolean comparison still need judgment. Manually correct them:

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

Then configure, test, and commit:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "N"]

[tool.ruff.format]
quote-style = "double"
```

```bash
uv run pytest
git add src/demo/orders.py pyproject.toml
git commit -m "Introduce Ruff and clean up orders.py"
```

The source labels its diagnostics as conceptual examples, not captured output. It also explains that `(total>0)==True` is not the same as the chained expression `total>0==True`; parentheses matter to the parsed meaning.

## 43. Debugging lab — `reports.py`

Problematic source:

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
    return totl
```

Problems:

1. Formatting: missing spaces and inconsistent layout.
2. Unused import: `sys`; `OrderedDict` is also unused.
3. Naming: `Generate_Report` should be `generate_report` (`N` family).
4. Comparison: use `is None`, not `== None` (`E711`).
5. Undefined name: `totl` should be `total` (`F821`).
6. CSV correctness: use `newline=""` when opening a CSV output file. This is a Python CSV requirement, not necessarily a Ruff diagnostic.

Corrected code:

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
        for row in rows:
            writer.writerow(row)
    return total
```

Line-by-line reasoning:

- Import only `csv` and `Path`, both used.
- Use lowercase snake_case for the function.
- Initialize `rows` and `total`.
- Skip rows whose amount is `None`.
- Add each valid amount to the total.
- Preserve the valid row for output.
- Open the CSV with `newline=""`.
- Use a context manager so the file closes reliably.
- Write each row with `csv.writer`.
- Return the calculated total, not an undefined variable.

## 44. Coding exercises

The source chapter contains 16 coding exercises, answered step by step in Part C below.

---

# Part B — Project-Tree and Current-Level Assessment

## 1. Where this lesson fits

The Stage 1 roadmap has 24 modules. Its early sequence builds fundamentals before production habits:

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

Module 06 contains seven lessons:

1. Imports, Modules, and `__main__`.
2. Project Layout and Package Structure.
3. `pyproject.toml`, Lock Files, and `uv`.
4. Dependency Management and Semantic Versioning.
5. Ruff, Formatting, and Linting — current lesson.
6. Type Hints and Type Checking.
7. Docstrings, READMEs, and User Documentation.

The next module is Testing and Systematic Debugging, but this guide does not advance into that module.

## 2. Existing Stage 1 project work

The Stage 1 overview contains four major projects:

- **Personal Expense Ledger CLI:** file-backed CLI, structured data, validation, and reporting.
- **Log Investigation and Reliability CLI:** log parsing, filtering, aggregation, and reliability analysis.
- **Data Quality and Transformation Pipeline:** `orders.csv`, a `dqpipe` package with CLI/config/pipeline/rules, tests, and a data contract.
- **Rule-Based Risk Review Engine:** `transactions.csv`, `rules.toml`, a `riskreview` package, tests, and golden decision data.

Ruff is directly useful in all four: it catches unused imports and undefined names, standardizes formatting, and helps prevent suspicious patterns from entering the projects. The data pipeline and risk engine especially benefit from correctness-adjacent checks, but they still require tests for business rules and data outcomes.

## 3. Your current learning level and scope

Your current level is beginner progressing toward intermediate in Python engineering. The previous completed lessons have given you the required prerequisites:

- Python data types, collections, mutability, and core syntax.
- Functions, loops, scope, exceptions, validation, and side effects.
- Search/filter/group/sort patterns and algorithmic reasoning.
- Text and structured files, paths, CSV, JSON, encodings.
- CLI arguments, standard streams, exit codes, and logging.
- Environment configuration and input validation.
- Imports, modules, `__main__`, packages, and project layout.
- `pyproject.toml`, virtual environments, dependency groups, lock files, and `uv`.
- Version constraints, dependency resolution, and safe dependency updates.
- Git diff and commit concepts from the earlier project workflow.

That is sufficient foundation for this lesson. The solutions stay within Module 06 and earlier topics: Python syntax, imports, TOML, Ruff commands, `uv`, Git, and the already-introduced test command. They do not assume that you have completed the next type-checking lesson.

---

# Part C — Debugging Lab and Review Answers


## 44. Sixteen coding exercises and solutions

### Level 1 — Basic

**1. Predict formatting changes**

Given:

```python
def total(items):
    result=0
    for item in items:
        result+=item["amount"]
    return result
```

Expected formatted form:

```python
def total(items):
    result = 0
    for item in items:
        result += item["amount"]
    return result
```

The function signature, assignment, and augmented assignment receive conventional spacing. The algorithm is unchanged. Verify with `uv run ruff format file.py`, then inspect `git diff`.

**2. Explain unused import and variable diagnostics**

```python
import os

def count_rows(rows):
    count = 0
    return len(rows)
```

- `F401`: `os` is imported but never used.
- `F841`: `count` is assigned but never read.
- Remove them if they are truly unnecessary. Do not hide the diagnostics without understanding intent.

Run `uv run ruff check file.py`; a diagnostic identifies file, line/column, rule code, and message.

**3. Explain `ruff format --check`**

```bash
uv run ruff format --check .
```

- Already formatted: exit code `0`; no files need changes.
- Introduce inconsistent spacing: Ruff reports the file would be reformatted and exits non-zero.
- The check never modifies the file. Run `uv run ruff format .` locally to apply the formatting.

**4. Interpret a rule-family prefix**

Examples:

- `F401`: `F` means Pyflakes-derived; this code is unused import.
- `UP035`: `UP` means modernization/pyupgrade.
- `B006`: `B` means bug-prone pattern checks.

The prefix tells you the diagnostic category before you read the full message.

### Level 2 — Intermediate

**5. Minimal configuration and justification**

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
```

- 100 is a deliberate readability convention; a team could choose 88 or another consistent value.
- `py312` is correct only if Python 3.12 is the project's actual minimum supported version. Match it to `requires-python`.

**6. Select E, F, I**

```toml
[tool.ruff.lint]
select = ["E", "F", "I"]
```

- `E`: pycodestyle style diagnostics.
- `F`: unused names/imports and undefined-name diagnostics.
- `I`: import ordering.
- `select` replaces Ruff's default selection. `extend-select` adds families to the existing selection instead.

**7. Add a documented ignore**

```toml
[tool.ruff.lint]
ignore = ["E501"]  # Deliberately allow long comments/URLs that formatter cannot wrap.
```

The comment explains the policy. If removed, the configuration still functions, but future maintainers cannot easily understand why the rule was disabled. Reassess whether this ignore is truly appropriate; do not use it to avoid fixing ordinary long lines.

**8. Run safe auto-fixes and review**

```bash
uv run ruff check --fix .
git diff
```

Mechanical changes may include removing an unused import or a safe modernization. Review every change. If a change affects logic, comments, or intent, inspect it carefully and make a manual decision. Do not enable `--unsafe-fixes` casually.

### Level 3 — Advanced

**9. Design per-file ignores**

```toml
[tool.ruff.lint.per-file-ignores]
"tests/*.py" = ["F401"]   # only when deliberate fixture imports are required
"src/myapp/__init__.py" = ["F401"]  # intentional public re-exports
```

Keep `src/` core code under normal checks. Do not automatically exempt every script. Add a `scripts/*.py` exception only when a particular rule is genuinely inappropriate, with a reason. Each glob should be as narrow as possible.

**10. Target Python 3.10**

```toml
[project]
requires-python = ">=3.10"

[tool.ruff]
target-version = "py310"
```

If Ruff is set to `py312` while the project claims 3.10 support, it may suggest or apply syntax unavailable in Python 3.10/3.11. The application can then fail for supported users. Keep the minimum target aligned.

**11. Introduce Ruff to an existing 50-file project**

1. Inspect package structure and existing conventions.
2. Add Ruff as a dev dependency and pin it through the lock.
3. Run a baseline `ruff check .`; record findings without changing code.
4. Run `ruff format .` in a separate formatting-only commit.
5. Review diagnostics and classify by severity/intent.
6. Fix high-value `F` findings (unused/undefined names) and bug-prone `B` findings.
7. Apply safe fixes, then inspect `git diff`.
8. Add `E` and `I` for style/import consistency.
9. Add `UP` and `SIM` only after checking the target Python version and reviewing modernization.
10. Add narrow, documented exceptions only for real false positives.
11. Add CI `format --check` and `check` after the baseline is manageable.
12. Require the CI checks before merge.

Prioritize likely correctness problems (`F`, `B`) before lower-risk stylistic/modernization rules.

**12. Team Ruff policy document**

A suitable policy:

> All maintained production Python source must pass Ruff formatting and the mandatory lint families `E`, `F`, and `I`. `B` is mandatory for production data-processing code because bug-prone patterns can cause silent data errors. `UP`, `SIM`, `N`, `A`, `C4`, `PIE`, and `RUF` may be introduced as the project matures. Any suppression must be rule-specific, narrowly scoped, and include a reason. A new global or per-file ignore requires reviewer approval and a documented justification. Generated/vendor/build files are excluded. CI runs the committed Ruff version and blocks merge on formatting or lint failures. Ruff does not replace tests or type checking.

### Level 4 — Production

**13. Exact CI command sequence**

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

- Install exactly the committed dependency state.
- Verify formatting without changing files.
- Run lint checks.
- Run tests.
- Each command must succeed before the next stage proceeds. Configure repository branch protection to require the CI job.

**14. Pre-commit integration plan**

At commit time, run fast Ruff checks (formatter verification and selected lint checks, or configured hooks that apply fixes and then re-check). These catch issues early on the developer's machine. CI independently runs the complete required rule set, format verification, and tests in a clean locked environment. Pre-commit is locally bypassable; CI is the authoritative merge gate. Avoid slow or broad checks that make every commit unnecessarily burdensome.

**15. Migrate a legacy repository with 2,000 violations**

Use multiple small pull requests:

1. PR 1: pin Ruff, commit baseline configuration, and apply formatting only.
2. PR 2: address `F` violations, separating safe fixes from manual intent decisions.
3. PR 3: address `B` bug-pattern findings.
4. PR 4: enable and remediate `E` and `I`.
5. Later PRs: introduce `UP`, `SIM`, `N`, and other useful families one at a time.
6. Add documented per-file exceptions only for genuine cases.
7. Prevent new violations from being introduced while the old baseline is reduced (for example, by enforcing the agreed clean scope or a staged baseline policy).
8. Once the count is manageable, make format and lint checks blocking CI gates.
9. Periodically remove obsolete ignores.

Do not combine 2,000 findings into one unreviewable change.

**16. Data-pipeline code-quality policy**

> Every maintained data-pipeline module must use Ruff formatting and mandatory `F` and `B` checks. `E` and `I` are required for consistent style and imports. These checks run in CI using the committed lock file and block merge. `UP`, `SIM`, and `N` are introduced as appropriate. Exceptions must be narrow, rule-specific, justified, and reviewed. Tests must separately cover transformations, boundary values, invalid records, and regression cases. Ruff cannot prove data correctness, so clean lint output is never treated as proof that a pipeline's results are correct.


## Debugging lab — all six issues

The complete corrected `reports.py` and line-by-line explanation are in Part A, Section 43. The six findings are formatting, unused imports (`sys` and `OrderedDict`), naming convention, comparison to `None`, undefined return variable, and missing CSV `newline=""`.

Important distinction: Ruff can catch several of these, but the CSV `newline=""` requirement comes from the CSV/file-handling contract, not from a guarantee that Ruff will report it.

## Twenty-one interview questions

1. **Formatting:** consistent visual arrangement of source code.
2. **Linting:** static analysis for suspicious patterns and likely mistakes.
3. **Ruff:** one tool providing a Python linter and formatter.
4. **Formatter:** deterministic source rewriter for layout that aims to preserve behaviour.
5. **Linter:** source analyzer that reports rule violations without executing code.
6. **Ruff vs. Black:** Ruff's formatter fills the same general role as a separate opinionated formatter, consolidated into Ruff.
7. **Ruff vs. Flake8:** Ruff consolidates much of the linter/plugin ecosystem's functionality in one tool.
8. **Why `pyproject.toml`:** it is the shared standardized home for project and tool configuration.
9. **`ruff check`:** report lint diagnostics without changing files.
10. **`ruff format`:** rewrite files into consistent formatting.
11. **`--fix`:** apply supported automatic lint corrections; review `git diff`.
12. **Legacy project adoption:** baseline, format-only commit, classify and fix incrementally, document exceptions, then enforce in CI.
13. **Rule selection:** begin with a small understood set and add families for explicit reasons.
14. **Prevent suppression abuse:** require rule-specific `noqa`, reason comments, review approval, and narrow scope.
15. **CI integration:** locked sync, format check, lint check, tests, and branch-protection gating.
16. **Generated code:** exclude it rather than editing files that regeneration overwrites.
17. **Large repository pipeline:** editor feedback → pre-commit → CI format/lint/type/test gates → protected merge.
18. **Strictness vs. velocity:** calibrate to risk, adopt gradually, and keep checks fast.
19. **Thousands of violations:** baseline and remediate family by family across multiple PRs.
20. **Multiple teams:** shared committed configuration, justified per-file exceptions, and uniform CI.
21. **Ruff vs. type checking/testing:** Ruff checks layout and patterns; type checkers check type flow; tests check actual behaviour.

## Six architecture questions

1. **Where should Ruff run?** Early in CI, before slower tests/build/deploy.
2. **Local or CI formatting?** Apply locally; verify in CI with `ruff format --check`.
3. **Should CI rewrite code?** Generally no; CI should verify and gate, not silently modify pull requests.
4. **Monorepo configuration?** Shared root baseline with narrow path-based exceptions; verify exact supported config behaviour.
5. **Legacy service adoption?** Baseline, format-only change, incremental rule adoption, then CI enforcement.
6. **AI/ML code quality?** Enforce correctness-adjacent rules firmly on data and serving code; allow proportionate treatment of genuinely exploratory scripts.

## Eighteen knowledge-check answers

1. Formatter changes layout; linter detects suspicious code patterns.
2. Static analysis examines source without executing it; runtime execution exercises behaviour.
3. Ruff combines a Python linter and formatter.
4. A rule is one check; a family groups related rules sharing a prefix/category.
5. A diagnostic is the message for a violation, including rule, location, and explanation.
6. `--fix` rewrites fixable code; run `git diff` immediately afterward.
7. Formatting ensures consistent layout; it does not prove correctness.
8. Ruff configuration lives in `pyproject.toml`; modern lint selection is under `[tool.ruff.lint]`.
9. `select` enables rules; `ignore` disables selected rules.
10. Per-file ignores scope exceptions to file patterns, e.g. intentional public API re-exports in `__init__.py`.
11. `target-version` tells Ruff which Python version/features it may assume.
12. Pre-commit runs checks locally before a commit; CI is an independent shared server-side check.
13. CI independently verifies formatting, linting, and tests in a reproducible environment.
14. A non-zero Ruff exit code means the command failed (for `ruff check`, violations remain under the active rules).
15. Edit → lint auto-fix → format → inspect diff → test → commit.
16. Ruff cannot detect every logical formula error; a test can compare actual output with expected output.
17. A type checker can detect a possibly-`None` value passed where an `int` is required.
18. Production workflows need editor feedback, pre-commit, required CI, tests, and type checking where used.

---

# Production Code-Quality Checklist

- [ ] Ruff is installed as a development dependency with `uv add --dev ruff`.
- [ ] Ruff version is locked in `uv.lock`.
- [ ] Ruff configuration is committed in `pyproject.toml`.
- [ ] `line-length` and quote/indent conventions are deliberate.
- [ ] `lint.select` is deliberate and understandable.
- [ ] Every ignore has a clear reason.
- [ ] Generated/vendor/build/virtual-environment files are excluded appropriately.
- [ ] `target-version` agrees with the project's actual minimum Python support.
- [ ] Developers can run Ruff locally or through editor integration.
- [ ] Pre-commit provides an early local check.
- [ ] CI independently runs `ruff format --check` and `ruff check`.
- [ ] Tests run as a separate stage.
- [ ] Every automated rewrite is reviewed with `git diff`.
- [ ] CI uses the committed lock with `uv sync --locked`.
- [ ] Team policy explains the required rule families and exception process.

# Glossary

- **Formatter:** tool that rewrites code into a consistent layout.
- **Linter:** static analyzer that reports suspicious code patterns.
- **Lint rule:** one named check identified by a rule code.
- **Diagnostic:** message reporting a specific violation.
- **Static analysis:** source analysis without executing the program.
- **Code quality:** readability, trustworthiness, and maintainability.
- **Auto-fix:** automated rewrite for a supported lint violation.
- **Rule family:** group of related rules sharing a prefix, e.g. `F`, `UP`, `B`.
- **Suppression:** silencing a specific violation, e.g. `# noqa: F401`.
- **Pre-commit:** local checks run immediately before a Git commit.
- **CI:** independent automated verification on a shared build system.
- **Exit code:** numeric command result; `0` means success, non-zero means failure.
- **Target Python version:** Python version Ruff assumes for syntax/modernization.
- **Generated code:** code automatically produced by another tool.
- **False positive:** diagnostic that is not a real problem in its context.
- **False negative:** real problem not caught by enabled rules.
- **Technical debt:** future maintenance cost created by deferred or unresolved quality issues.

# Final Mental Model

```text
WRITE CODE
    ↓
LINT CODE
    ↓
FIX SAFE ISSUES
    ↓
FORMAT CODE
    ↓
REVIEW git diff
    ↓
TYPE CHECK
    ↓
TEST
    ↓
COMMIT
    ↓
CI VALIDATION
    ↓
MERGE
    ↓
DEPLOY
```

Formatting prevents inconsistent layout. Linting catches a broad class of pattern-based issues. Type checking catches type-flow problems. Tests catch behavioural errors for the cases exercised. CI verifies that the agreed checks were actually run in the shared environment. No single layer is sufficient.

**Final principle:** Ruff is a fast, automated foundation for Python code quality—not a guarantee that the program is correct. Use it with disciplined code review, type checking where appropriate, tests, reproducible dependencies, and CI enforcement.
