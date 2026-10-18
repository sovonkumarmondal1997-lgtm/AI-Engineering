# Coverage: Line, Branch, and What It Really Means

> **Stage 1 — Programming & Computational Thinking**  
> **Module 16 — Advanced Testing and Test Architecture**  
> **Lesson 01**  
> **Baseline:** Python 3.12+, pytest 8+, coverage.py 7+  
> **Prerequisites:** pytest assertions, fixtures and parametrization (Module 1.7); functions and control flow (Modules 1.2–1.3); project layout and `pyproject.toml` (Module 1.6).

## Learning outcomes

After completing this lesson, you should be able to:

- Explain the difference between code being executed and its behaviour being verified.
- Install and run `coverage.py` and `pytest-cov`, then interpret statement counts, missed lines, branch counts and percentages.
- Construct an example with 100% line coverage but incomplete branch coverage, and calculate the result correctly.
- Configure source selection, branch measurement, omissions, parallel collection, concurrency, exclusions, missing-line output and a coverage threshold in `pyproject.toml`.
- Use `# pragma: no cover` only when justified and reviewable.
- Combine coverage data from multiple processes or environments, understand subprocess coverage, and publish reports in CI.
- Explain why coverage is a diagnostic metric rather than a proof of correctness.
- Use contexts, risk-based thresholds, mutation testing and code review to make coverage evidence more useful.

---

## 1. The central idea: execution is not verification

**Code coverage** measures which parts of a program ran while a measurement tool was observing it. It answers questions such as:

- Did a test execute this statement?
- Did both outcomes of this conditional execute?
- Which lines remain unvisited under the current test suite?

It does **not** directly answer:

- Did the test assert the correct result?
- Would the test fail if the implementation were wrong?
- Did we implement every requirement?
- Did the system work correctly across its database, network, scheduler or other integrations?

A test can call a function, execute every line, and make no assertion. Coverage can rise even though the test proves almost nothing.

### 1.1 Execution versus behavioural verification

Consider a data pipeline that calculates a discount. A test that calls `discount(100, True)` executes the member path. A test that additionally asserts the result is exactly `90.0` checks a behavioural expectation. A stronger suite also tests non-members, boundary values, invalid inputs if the API defines them, and relevant interactions.

Coverage is therefore best treated as **reachability evidence**: the test suite reached some code. Assertions and test design provide evidence about whether that code behaves correctly.

### 1.2 Why it matters in data engineering

Coverage can reveal that a data-quality check's invalid-row path was never exercised, that a parser's fallback was never run, or that a retry handler is untested. These are useful signals before deploying a batch job or transformation pipeline. But a high percentage cannot prove that a CSV parser handles every encoding, that a transaction is atomic, or that concurrent workers cannot corrupt shared state.

**Rule:** use coverage to find questions to investigate, not as a substitute for answering those questions.

---

## 2. Install the tools and run a first report

Run these commands from the project root in the activated virtual environment. The examples use `uv`, matching the roadmap's environment-management approach.

```bash
uv add --dev pytest pytest-cov coverage
```

Check the installed versions:

```bash
uv run python --version
uv run pytest --version
uv run coverage --version
uv run pytest --help
```

The baseline for this lesson is Python 3.12+, pytest 8+, and coverage.py 7+. `pytest-cov` installs coverage.py as a dependency, but listing both explicitly can make the development-tool intent clear. Use a lock file to make the environment reproducible.

### 2.1 Two common workflows

Measure coverage while running pytest directly through coverage.py:

```bash
uv run coverage run -m pytest
uv run coverage report -m
uv run coverage html
```

Or use the pytest plugin:

```bash
uv run pytest --cov=src --cov-report=term-missing
```

The first workflow starts coverage.py and asks it to run pytest. The second lets pytest-cov manage coverage for the pytest run. Use one deliberately configured workflow in CI; do not accidentally combine overlapping invocations and assume their data semantics are identical.

- `coverage run -m pytest` measures code executed by pytest.
- `coverage report -m` prints a terminal summary and missing line numbers.
- `coverage html` writes an interactive report to `htmlcov/`.
- `--cov=src` selects the `src` directory as the measurement target; replace it with the actual package or source directory in your repository.
- `--cov-report=term-missing` prints line numbers for statements not executed.

If the repository uses a `src/ledger/` package, prefer measuring `src/ledger` or the importable package `ledger` rather than the entire repository. Measure production code, not test files, unless there is a specific reason to measure tests.

### 2.2 A minimal project you can run

Create this layout:

```text
coverage-lab/
├── pyproject.toml
├── src/
│   └── ledger/
│       ├── __init__.py
│       └── pricing.py
└── tests/
    └── test_pricing.py
```

`src/ledger/__init__.py` can be empty.

`src/ledger/pricing.py`:

```python
def discount(price: float, member: bool) -> float:
    if member:
        price *= 0.9
    return price
```

`tests/test_pricing.py`:

```python
from ledger.pricing import discount


def test_member_gets_ten_percent_discount() -> None:
    assert discount(100.0, True) == 90.0
```

Install the package in editable mode along with test tools. If the project does not already define a build system, use the project's normal packaging configuration; this minimal test setup can alternatively set `PYTHONPATH=src` for a one-off lab, but editable installation is preferable for a real project.

```bash
uv pip install -e .
uv run pytest --cov=ledger --cov-report=term-missing
```

If `uv pip install -e .` fails because the directory is not configured as a package, add appropriate project/build-system metadata or use the repository's existing install workflow. Do not hide an import-path problem by permanently adding ad hoc path manipulation to production code.

---

## 3. Read a coverage report accurately

A real report from the minimal `discount` example, measured with branch coverage and `source = ["src/ledger"]`, looked like this in Python 3.13.5 with coverage.py 7.13.3 and pytest 9.0.2:

```text
Name                    Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------
src/ledger/pricing.py       4      0      2      1    83%   2->4
-------------------------------------------------------------------
TOTAL                       4      0      2      1    83%
```

This is an observed result from that environment, not a promise that every version prints identical formatting. The exact columns, rounding and percentages depend on the measured source, exclusions and tool version. A line-only report may not display branch columns. The `2->4` entry means the conditional on line 2 did not take the arc to line 4.

- **Stmts:** executable statements coverage.py identified in the measured source.
- **Miss:** executable statements that were not executed.
- **Branch:** possible branch destinations measured for the code. A conditional commonly contributes two possible destinations.
- **BrPart:** branch opportunities that were only partly exercised—at least one destination was reached and at least one was not.
- **Cover:** the combined coverage percentage when branch measurement is enabled; with branch measurement disabled it is statement coverage.
- **Missing:** line numbers of statements not executed. With branch measurement, reports may also show partial-branch annotations.

Do not infer that `Miss = 0` means every branch was tested. With branch measurement disabled, `Miss` is about statements, not unvisited branch destinations.

### 3.1 Statement coverage calculation

At a simplified level:

\[
\text{statement coverage} =
\frac{\text{executed executable statements}}
{\text{executable statements}} \times 100\%
\]

If a file has 20 executable statements and 18 execute, statement coverage is \(18/20 \times 100 = 90\%\).

Coverage.py uses source analysis and execution tracing to determine executable statements. Comments, blank lines and many non-executable lines are not counted as statements. Therefore, do not calculate coverage from the raw number of physical lines in a file.

### 3.2 Combined coverage calculation

With branch measurement enabled, coverage.py's total percentage accounts for both executable statements and branch destinations. A useful conceptual model is:

\[
\text{combined coverage} =
\frac{\text{executed statements} + \text{executed branch destinations}}
{\text{statements} + \text{branch destinations}} \times 100\%
\]

The report's `Cover` value may therefore be lower than the statement-only percentage. Exclusions and partial branches affect the denominator and reporting. Use coverage.py's own report as the authoritative calculation for a real project.

### 3.3 Find the missing behaviour

When a line is missing:

1. Read the source around the line.
2. Ask which input or state would reach it.
3. Decide whether that input is valid, invalid, rare, or impossible by contract.
4. Add a behavioural test if the path is required.
5. If the path is genuinely irrelevant or impossible, document the reason and consider a narrowly scoped exclusion.
6. Re-run the test suite and inspect the diff in the coverage report.

A missing line is a prompt for investigation, not an automatic instruction to write a test for every line.

---

## 4. Line coverage versus branch coverage

### 4.1 Line coverage

Line coverage asks whether executable source lines were executed at least once. It is useful for locating untouched code, but it does not distinguish all paths through a line or conditional.

### 4.2 Branch coverage

Branch coverage asks whether possible control-flow destinations (arcs) were exercised. For a simple `if`, the destinations are typically the true and false outcomes. Branch coverage helps reveal a missing alternative even when every source statement was reached.

Enable it in pytest-cov with `--cov-branch`, or set `branch = true` in coverage configuration.

### 4.3 Correct, runnable example

Use this exact source and test to observe the distinction.

`src/ledger/pricing.py`:

```python
def discount(price: float, member: bool) -> float:
    if member:
        price *= 0.9
    return price
```

`tests/test_pricing.py`:

```python
from ledger.pricing import discount


def test_member_gets_discount() -> None:
    assert discount(100.0, True) == 90.0
```

Run:

```bash
uv run pytest --cov=ledger --cov-branch --cov-report=term-missing
```

The test executes every executable statement in the function: the function body, the conditional's true path, the multiplication, and the return. Thus the function can have **100% line coverage**. But the false destination of `if member` was not exercised, so branch coverage is incomplete.

In the verified environment described in Section 3, coverage.py counted four statements for this file, including the function definition line, and two branch destinations for the conditional. The test executes all four statements and one of the two branch destinations:

- **Statement/line coverage:** `4 / 4 = 100%`.
- **Branch-destination coverage:** `1 / 2 = 50%`.
- **Combined coverage.py total:** `(4 + 1) / (4 + 2) = 83.33%`, displayed as `83%` with the default whole-percent precision.

The roadmap's illustrative comment says “branch coverage: 75%.” That figure should not be copied as a universal result: the exact statement count and combined percentage depend on the source and tool's accounting. For this concrete example, the observed report is 100% statement coverage, 50% branch-destination coverage, and 83.33% combined coverage. These are three different descriptions; do not label the combined percentage as branch coverage.

Add the missing behavioural test:

```python
from ledger.pricing import discount


def test_member_gets_discount() -> None:
    assert discount(100.0, True) == 90.0


def test_non_member_pays_full_price() -> None:
    assert discount(100.0, False) == 100.0
```

Run the branch report again. The true and false destinations should now be exercised. The exact whole-file percentage can still depend on package files and source configuration.

### 4.4 Keep the three percentages distinct

For the single-test example above, **100% statement/line coverage** means every counted statement ran; **50% branch-destination coverage** means only one of the conditional's two destinations ran; and **83.33% combined coverage** is coverage.py's total when statements and branch destinations are counted together. The same suite can legitimately have all three values. When answering the roadmap self-check, report the branch-destination percentage separately from the combined `Cover` column.

**When to use branch coverage:** use it for decision-heavy business logic, validation, pricing, permission checks, routing and error-handling paths. It usually costs more test-design effort than line coverage, but reveals gaps that line coverage misses.

---

## 5. Configure coverage in `pyproject.toml`

The following is a starting configuration for a conventional `src/ledger/` project. Merge it into the project's existing `pyproject.toml`; do not replace unrelated project, build or pytest settings.

```toml
[tool.coverage.run]
source = ["src/ledger"]
branch = true
omit = [
  "*/tests/*",
  "*/generated/*",
]
parallel = true
concurrency = ["multiprocessing"]
relative_files = true

[tool.coverage.report]
fail_under = 90
show_missing = true
skip_empty = true
exclude_lines = [
  "pragma: no cover",
  "if TYPE_CHECKING:",
]
```

### 5.1 `[tool.coverage.run]`

- **`source`**: packages/directories to measure. This also helps coverage.py find source files that were never imported, so completely untested files can appear in reports. Choose the actual production source root.
- **`branch = true`**: records branch destinations as well as statements.
- **`omit`**: patterns to omit from measurement. Use narrow, justified patterns; broad omissions can conceal production code.
- **`parallel = true`**: writes distinct data-file names for separate processes, which can later be combined. Use it when collecting from multiple processes/runs; it is not a substitute for combining data.
- **`concurrency = ["multiprocessing"]`**: tells coverage.py about the concurrency mechanism so it can collect correctly in multiprocessing scenarios. Specify only mechanisms actually used and supported by the configured measurement core. Threads do not normally need to be listed as a concurrency library in the same way.
- **`relative_files = true`**: stores relative source paths to make reports and data combining across different working directories/environments easier. Keep `source` in the configuration file when using this option.

If you are not using multiple processes, remove `parallel` and the multiprocessing concurrency setting unless your workflow requires them. Extra settings without a need add complexity.

### 5.2 `[tool.coverage.report]`

- **`fail_under = 90`**: make the report command fail when total coverage is below the chosen threshold. The number is a policy example, not a universal quality target.
- **`show_missing = true`**: show line numbers for unexecuted statements in text reports.
- **`skip_empty = true`**: omit files with no executable code from the report.
- **`exclude_lines`**: patterns whose matching lines are excluded from coverage reporting. The list replaces the default exclusion list in coverage.py; if you override it, preserve any default patterns you still rely on.

`raise NotImplementedError` is **not automatically safe to exclude**. An abstract method may be intentionally unimplemented, but a concrete production method raising that exception could indicate an incomplete feature. Add such a pattern only after a deliberate project-wide decision and a review of its consequences.

### 5.3 pytest-cov and configuration interactions

With pytest-cov, a command such as `--cov=ledger` overrides coverage.py's configured `source` selection. `--cov-branch` overrides the configured branch setting. To keep the configuration authoritative, use `--cov` without a source argument when appropriate:

```bash
uv run pytest --cov --cov-report=term-missing
```

pytest-cov 7.x overrides coverage.py's `parallel` option while it manages pytest's coverage run. Do not assume `parallel = true` has the same effect under pytest-cov as when invoking coverage.py directly. Check the installed pytest-cov version's documentation before designing a multi-process workflow.

To make a threshold apply in a pytest-cov run, you can use:

```bash
uv run pytest --cov --cov-branch --cov-report=term-missing --cov-fail-under=90
```

Alternatively, `coverage report` honors `[tool.coverage.report] fail_under` when it generates the report. Avoid enforcing two conflicting thresholds in different places.

---

## 6. `# pragma: no cover`: exception, not escape hatch

Coverage.py recognizes `# pragma: no cover` as an instruction to exclude the marked line from coverage reporting; when used on a control-flow line, the excluded code can affect whether a branch is considered partial. It is not a way to test the code, and it should not be used simply because a line is inconvenient to exercise.

### 6.1 Potentially acceptable uses

Use narrowly and with a clear rationale:

- A defensive branch that is demonstrably unreachable under a stable, documented invariant, while acknowledging that the invariant itself must be tested.
- An `if TYPE_CHECKING:` block that exists only for static type checking and is not executed at runtime.
- A conventional `if __name__ == "__main__":` entry-point guard when the module is tested through its callable entry point and the guard itself is not a meaningful behaviour under test.

Even these are context-dependent. If a command-line entry point is a product requirement, it may deserve an integration test rather than an exclusion.

### 6.2 Misuse

Do not exclude:

- A hard-to-test error path merely because it is hard to trigger.
- A branch that reveals an untested permission, validation or retry behaviour.
- Code that is failing a coverage threshold without first understanding why.
- A large function or block when only one small statement is irrelevant.

Prefer a comment explaining the invariant and a minimal exclusion. Review exclusions as carefully as code. If exclusions grow over time, investigate whether the architecture or test seams need improvement.

---

## 7. Combine coverage from multiple runs and processes

Coverage data is written to a data file, commonly `.coverage`. Parallel runs create uniquely named files so that one process does not overwrite another's data.

### 7.1 Direct coverage.py workflow

Given the configuration above:

```bash
uv run coverage erase
uv run coverage run -m pytest
uv run coverage combine
uv run coverage report -m
```

`coverage erase` removes prior local coverage data; use it only when you intentionally want a fresh run. `coverage combine` merges compatible data files it finds, usually parallel data files in the current directory. `coverage report -m` then reports the combined result.

For multiple environments, collect each environment's coverage data as CI artifacts, preserve compatible source paths (often with `relative_files = true`), place the data files together, and run `coverage combine` before reporting. Different Python versions may produce compatible data, but paths, source revisions, coverage versions and configuration must be controlled. Never combine data from different source revisions and interpret it as one coherent report.

### 7.2 Multiprocessing and concurrency

For multiprocessing, configure the actual concurrency mode, for example:

```toml
[tool.coverage.run]
source = ["src/ledger"]
branch = true
parallel = true
concurrency = ["multiprocessing"]
```

Coverage.py must be configured in a file for multiprocessing support. Ensure child processes terminate in a way that lets coverage data be written. Abrupt kills, crashes, `os._exit`, or forced termination may prevent data from being saved; investigate missing child data rather than assuming a zero-coverage child path.

### 7.3 Subprocess coverage: version-sensitive guidance

Do not blindly copy older `COVERAGE_PROCESS_START`, `sitecustomize.py`, or `.pth` recipes into a modern pytest-cov setup.

In **coverage.py 7.10+**, the `[tool.coverage.run]` `patch` setting supports subprocess instrumentation. **pytest-cov 7.0 requires coverage.py 7.10.6 or newer.** With pytest-cov 7.x, subprocess support was removed from pytest-cov itself; the documented migration is to use coverage.py's subprocess patch:

```toml
[tool.coverage.run]
source = ["src/ledger"]
branch = true
patch = ["subprocess"]
```

The subprocess patch enables parallel data files automatically, so combine data before reporting. It can instrument supported subprocess creation paths, but it is not magic: test the actual process-launch mechanism used by your application, and check coverage.py's current subprocess documentation for limitations. Legacy startup-file methods are relevant to older or special setups, not the default first choice for a new project.

For older coverage.py 7.x versions that do not support `patch = ["subprocess"]`, follow the documentation for that exact version rather than assuming the modern configuration works. `COVERAGE_PROCESS_START` with a `.pth`/`sitecustomize` bootstrap is a legacy alternative in applicable setups and needs careful installation and configuration.

---

## 8. Differential coverage and CI reporting

### 8.1 Differential coverage

A legacy repository may have a large, long-standing coverage gap. A tool such as `diff-cover` can report coverage for changed lines in a patch, allowing teams to improve the baseline incrementally. This answers: “Are the changed lines covered?” It does not answer whether the change is correct or whether unchanged code remains safe.

Example workflow (install `diff-cover` as a development tool and adapt the base ref to your CI provider):

```bash
uv add --dev diff-cover
uv run pytest --cov --cov-branch --cov-report=xml
uv run diff-cover coverage.xml --compare-branch=origin/main --fail-under=90
```

This assumes `coverage.xml` is produced and `origin/main` exists in the local Git checkout. CI must fetch the comparison branch and the right history depth. Differential tools vary in report format support and line-mapping behaviour; confirm the installed version's CLI before relying on this command in a pipeline.

For a mature codebase, combine a stable overall threshold with a changed-line policy. Avoid treating changed-line coverage as proof that the new tests assert the right behaviour.

### 8.2 CI reporting

A practical CI sequence is:

1. Install locked dependencies.
2. Run tests with branch coverage and a threshold.
3. Generate a machine-readable report such as XML for the CI or coverage service.
4. Upload the report using the service's supported action or API.
5. Preserve the report/data files as artifacts when debugging failures.
6. Fail the job when the agreed threshold is missed.

For example:

```bash
uv run pytest --cov --cov-branch --cov-report=term-missing --cov-report=xml --cov-fail-under=90
```

The exact upload step depends on the CI provider and coverage service; do not copy a provider-specific token or action without checking its current documentation. Protect secrets and use least-privilege credentials.

A badge displays a summary of a metric. It is not evidence that tests are meaningful, that the report is current, or that the coverage scope is correct.

---

## 9. Goodhart's law: why coverage can become meaningless

**Goodhart's law** is often summarized as: when a measure becomes a target, it ceases to be a good measure. If a team is rewarded only for reaching 100% coverage, it can write tests that execute code without checking it, test trivial getters while ignoring important failure modes, or exclude difficult code.

### 9.1 A test that raises coverage but proves nothing

Illustrative weak test:

```python
from ledger.pricing import discount


def test_discount_runs() -> None:
    discount(100.0, True)
```

This test executes code but makes no assertion about the result. If the function accidentally returned `100.0` for members, this test would still pass.

A meaningful test checks the contract:

```python
from ledger.pricing import discount


def test_member_gets_ten_percent_discount() -> None:
    assert discount(100.0, True) == 90.0
```

The second test is still not a complete test suite, but it verifies a specific expectation.

### 9.2 What coverage cannot see

Coverage does not directly detect:

- **Data-dependent bugs:** code ran, but the chosen input did not expose a defect.
- **Missing branches in the implementation:** coverage cannot cover a requirement or condition that was never written.
- **Integration failures:** a unit test may cover a database adapter's caller without validating a real transaction, schema or network contract.
- **Untested error handling:** the normal path may be covered while timeouts, malformed input or permission errors are not.
- **Concurrency interleavings:** a line can execute while a race condition remains unobserved.
- **Incorrect assertions:** a test may assert the wrong value or merely assert that a result is truthy.
- **Performance and operational failure:** coverage is not a latency, memory, durability or reliability metric.

Coverage is a map of observed execution, not a specification and not a proof of correctness.

---

## 10. Advanced measurement: contexts, async code and generators

### 10.1 Coverage contexts: which test executed this line?

Coverage contexts attach labels to recorded execution so you can ask which test ran a line. This is useful when several tests execute the same utility function, when investigating redundant tests, or when identifying code that is only reached by an unrelated broad integration test.

With coverage.py, configure function-based dynamic contexts:

```toml
[tool.coverage.run]
source = ["src/ledger"]
branch = true
dynamic_context = "test_function"

[tool.coverage.html]
show_contexts = true
```

Then run:

```bash
uv run coverage run -m pytest
uv run coverage html
```

The HTML report can show which test contexts executed a line. An alternative with pytest-cov is:

```bash
uv run pytest --cov=ledger --cov-context=test --cov-report=html
```

`--cov-context=test` is pytest-cov's supported way to record test contexts. Do not enable both context mechanisms without understanding their interaction. Coverage.py's `dynamic_context = "test_function"` and pytest-cov's test-context feature are related but not interchangeable in every workflow.

Contexts can reveal lines reached by tests that do not uniquely exercise a behaviour. They do not automatically tell you whether a test is valuable: that still requires reading its assertions and intent.

### 10.2 Async functions

Coverage can observe Python statements executed by async functions, but a test only covers an async path when the coroutine is actually awaited and the relevant path runs. Merely constructing a coroutine object does not execute its body.

Illustrative pytest test (requires an async test plugin such as `pytest-asyncio` and its project configuration):

```python
import pytest


async def fetch_value(enabled: bool) -> int:
    if enabled:
        return 42
    return 0


@pytest.mark.asyncio
async def test_fetch_value_enabled() -> None:
    assert await fetch_value(True) == 42
```

For production async code, test success, cancellation, timeout, error propagation and relevant concurrency behaviour according to the function's contract. Coverage does not prove that every task interleaving is safe.

### 10.3 Generators

A generator function's body executes as the generator is iterated, not simply when the generator object is created. A test that calls a generator but never consumes it may execute none of its body.

```python
from collections.abc import Iterator


def positive_values(values: list[int]) -> Iterator[int]:
    for value in values:
        if value > 0:
            yield value


def test_positive_values() -> None:
    assert list(positive_values([-1, 2, 0, 3])) == [2, 3]
```

This exercises filtering and yields. Add tests for empty input and any documented edge cases. For streaming pipelines, also test partial consumption and early termination if they are meaningful to the contract.

### 10.4 Python 3.12+ and `sys.monitoring`

CPython 3.12 introduced `sys.monitoring`, a lower-overhead monitoring interface. Coverage.py 7.9+ introduced a `sysmon` measurement core. It is version- and feature-dependent, not a universal switch that is always faster or fully compatible.

- In Python 3.12 and 3.13, the sysmon core does **not** support branch coverage.
- In Python 3.14+, coverage.py 7.11.1+ supports branch coverage with sysmon, but other limitations remain.
- The sysmon core does not support dynamic contexts or some concurrency libraries/plugins; conflicting configurations can cause fallback or errors depending on the version and whether the core was explicitly selected.
- Do not set `COVERAGE_CORE=sysmon` in a project without checking the exact coverage.py and Python versions, feature requirements and test-runner integration.

If you want to experiment with lower overhead, benchmark a representative suite and compare the reports for correctness. Prefer the default core unless you have evidence that changing it is useful and compatible. For a workflow that needs branch coverage and per-test contexts, the traditional tracing core may be the appropriate choice even on newer Python versions.

---

## 11. Set thresholds sensibly and map coverage to risk

A threshold is a guardrail, not a universal definition of quality. A team might choose 90% overall coverage as an initial policy, but the right value depends on the codebase, coverage scope, risk and test cost.

### 11.1 Ratchet upward

For a legacy codebase:

1. Measure a trusted baseline with a clear source scope and branch setting.
2. Set an achievable threshold that prevents regression.
3. Raise it gradually as meaningful tests are added.
4. Do not lower the threshold to make a failing build green without recording and reviewing the reason.
5. Exclude generated code only when it is truly generated and is validated by an appropriate process.

### 11.2 Risk-based coverage

Spend test effort where a defect has meaningful consequences. For a data engineering system, examples include:

- schema and data validation;
- null, duplicate and malformed-record handling;
- money or unit conversions;
- idempotency and retry logic;
- permission and access checks;
- transaction boundaries;
- recovery and checkpoint code.

A trivial immutable constant may not need the same test depth as a financial calculation or a destructive data-cleanup path. A higher percentage in core logic can be appropriate, but do not compare package percentages without considering their risk and complexity.

### 11.3 Pair coverage with other evidence

Lesson 02 covers mutation testing in detail. For this lesson, understand the relationship:

- **Coverage:** did the tests reach the code or branch?
- **Mutation testing:** do the tests detect selected small changes that break behaviour?
- **Defect and incident history:** where have real failures occurred?
- **Code review:** are the assertions and scenarios aligned with the requirement?

High coverage plus a high mutation score is stronger evidence than high coverage alone, but neither proves the absence of defects. Mutation tools also have equivalent mutants and other limitations; use them as complementary evidence.

### 11.4 Per-package thresholds

Coverage.py's `fail_under` applies to the total report, not as a built-in independent threshold for every package. If per-package thresholds are needed, use separate scoped report commands or a CI script that evaluates each package's report. Be careful: separate scopes can produce different denominators and should be documented. Do not imply that a single `fail_under` automatically enforces a different minimum for every package.

---

## 12. Review coverage in code review

When reviewing a pull request:

1. Inspect the changed production lines and ask which requirements they implement.
2. Look at uncovered changed lines and partial branches.
3. Ask whether tests exercise both expected and rejected inputs where relevant.
4. Read assertions—not just test names.
5. Check error paths, boundary conditions, and side effects.
6. Review any new `pragma: no cover` or exclusion configuration.
7. Confirm the coverage source scope includes the changed production package.
8. Treat a percentage decrease as a prompt to investigate; do not automatically reject every change if the measurement is misleading or scope changed.
9. Confirm the report was generated from the same source revision as the pull request.

A useful review comment asks, “What test proves this invalid-row branch returns the documented error?” rather than merely, “Please increase coverage by 2%.”

---

## 13. Common mistakes and troubleshooting

### Mistake: reporting 100% without branch measurement

**Cause:** only statement coverage was measured.  
**Fix:** enable `branch = true` or pass `--cov-branch`, then inspect partial branches.

### Mistake: measuring the wrong source

**Cause:** pytest imports an installed copy while coverage measures a different directory, or the `--cov` target is incorrect.  
**Fix:** install the package in editable mode, verify import paths, set `source` to the intended production package, and inspect the filenames in the report.

### Mistake: the report omits an unimported module

**Cause:** source selection is absent or misconfigured.  
**Fix:** configure `source` in the coverage config so coverage.py can identify the files that should be measured even if tests never imported them.

### Mistake: threshold failure appears despite a green test suite

**Cause:** tests passed, but the report fell below `fail_under`.  
**Fix:** inspect missing lines/branches and the exact denominator. Add meaningful tests or adjust an incorrectly scoped configuration; do not simply lower the threshold.

### Mistake: subprocess lines are missing

**Cause:** child processes are not instrumented, data is not written, or parallel data has not been combined.  
**Fix:** check the coverage.py version, configure `patch = ["subprocess"]` where supported, inspect child-process termination and data files, and run `coverage combine` before reporting.

### Mistake: combined report shows “couldn't use data” or missing files

**Cause:** paths or source revisions differ across environments, data files are stale, or source files are unavailable at report time.  
**Fix:** combine only compatible runs, use consistent source revisions and paths, consider `relative_files = true`, and inspect the full warning before ignoring it.

### Mistake: assuming `sysmon` supports every measurement feature

**Cause:** `sys.monitoring` support depends on Python and coverage.py versions; branch measurement and dynamic contexts have different compatibility constraints.  
**Fix:** consult the version-specific feature matrix and use the default tracing core for unsupported combinations. The sysmon core does not support branch coverage on Python 3.12 or 3.13, and it does not support dynamic contexts.

### Mistake: chasing 100% by testing trivial getters

**Cause:** the percentage is treated as the goal instead of a signal about tested behaviour.  
**Fix:** prioritize meaningful requirements, boundary cases and failure paths; test a trivial getter when it has behaviour or risk worth verifying, not merely to raise a number.

### Mistake: tests execute code but contain no meaningful assertions

**Cause:** coverage is mistaken for evidence that expected behaviour was checked.  
**Fix:** read each test's assertions and ensure they would fail for a relevant defect. Use the weak-test example in Section 9.1 to compare execution with verification.

### Mistake: `pragma: no cover` spreads

**Cause:** coverage is treated as a target rather than diagnostic evidence.  
**Fix:** review each exclusion, narrow it, and require a reason. Remove exclusions that hide testable behaviour.

---

## 14. Practical labs

Complete the labs in order. Keep your code and tests in a disposable project or branch so you can inspect the impact of configuration changes.

### Lab 1 — Baseline line coverage

**Task**

1. Create the `discount` function and member-only test from Section 2.
2. Run pytest with `--cov=ledger --cov-report=term-missing`.
3. Record the statement count, missed statements and percentage.
4. Explain why the report does not prove the non-member behaviour.

**Acceptance criteria**

- Tests run from the project root.
- The report measures production code, not the tests.
- Your explanation distinguishes execution from assertion.

### Lab 2 — Add branch coverage

**Task**

1. Enable `--cov-branch`.
2. Record the branch/partial-branch counts.
3. Add a non-member test.
4. Re-run the report and explain what changed.

**Acceptance criteria**

- You identify the false outcome of `if member` as the missing destination.
- You calculate percentages from the actual report, not from a copied example.
- Both member and non-member behaviours are asserted.

### Lab 3 — Threshold failure

**Task**

1. Set `fail_under = 95` in the coverage report configuration, or use `--cov-fail-under=95` in pytest-cov.
2. Run the suite and capture the command's exit status.
3. Add meaningful tests until the threshold passes, or explain which remaining gaps are justified.

**Acceptance criteria**

- You can distinguish a test failure from a coverage-threshold failure.
- The threshold is enforced in the same command used by CI.
- You do not add exclusions merely to make the build pass.

### Lab 4 — Test the assertion gap

**Task**

1. Temporarily replace the meaningful member test with `discount(100.0, True)` and no assertion.
2. Compare the coverage report.
3. Restore the assertion.
4. Write two sentences explaining why the coverage number alone cannot distinguish test strength.

**Acceptance criteria**

- You observe that execution coverage can rise without behavioural verification.
- You restore a meaningful assertion before committing.

### Lab 5 — Subprocess or parallel data (optional advanced lab)

**Task**

1. Read the current coverage.py subprocess documentation for your installed version.
2. If using coverage.py 7.10+ and a compatible workflow, configure `patch = ["subprocess"]`.
3. Run a test that launches a Python subprocess which imports your package.
4. Inspect generated coverage data files, combine them, and report.
5. Record any limits in your subprocess launch mechanism or environment.

**Acceptance criteria**

- You can explain why child processes need explicit instrumentation support.
- You combine data before generating the final report.
- You do not claim support for an untested launch mechanism.

### Lab 6 — Review a pull request's coverage

**Task**

Choose a small code change (or create one in a practice branch). Inspect the changed lines, partial branches, assertions, exclusions and source scope. Write a brief review with:
- one uncovered path worth testing;
- one assertion that verifies a requirement;
- any justified exclusion, or a statement that none is needed;
- the risk of the changed behaviour.

---

## 15. Measurable completion checklist

You are ready to move to Lesson 02 when you can check all of these without copying commands blindly:

- [ ] I can install and run coverage.py and pytest-cov.
- [ ] I can explain `Stmts`, `Miss`, `Branch`, `BrPart`, `Cover` and `Missing`.
- [ ] I can demonstrate 100% line coverage with a missing conditional outcome.
- [ ] I can calculate a branch-aware percentage from a clearly stated denominator and verify it against the tool.
- [ ] I can configure source, branch, omit, parallel, concurrency, exclusions, missing-line reporting and `fail_under`.
- [ ] I know when `# pragma: no cover` is defensible and when it hides a test gap.
- [ ] I can combine parallel data and explain version-sensitive subprocess coverage.
- [ ] I can explain differential coverage's value and limitations.
- [ ] I can explain Goodhart's law and why missing assertions matter.
- [ ] I understand contexts, async/generator execution and sys.monitoring compatibility limits.
- [ ] I can justify thresholds based on risk and use coverage as part of code review.

---

## 16. Self-check questions (from the roadmap)

Answer these in your own words and include evidence from your lab.

### 1. Construct a function with 100% line coverage but 50% branch coverage.

**What a good answer includes:** a function with a conditional whose statements are all executed by the chosen test inputs, while only one of the two branch destinations is reached. Show the test and the actual coverage report. Be explicit about whether “50% branch coverage” means branch destinations only or whether you are quoting the report's combined coverage percentage. Those are different measures.

### 2. Why can a test suite with 100% coverage still miss an obvious bug? Write an example.

**What a good answer includes:** a test that executes the function but makes no meaningful assertion, or asserts a weak property that does not detect an incorrect result. Explain how the test can pass after a defect is introduced. Show a corrected assertion that would fail for the defective behaviour.

### 3. Configure `fail_under` and branch coverage, and show a CI failure when a PR lowers coverage.

**What a good answer includes:** a `pyproject.toml` configuration or explicit pytest-cov command, a test run that passes assertions but fails the coverage threshold, the non-zero exit status, and a short explanation of how CI uses that status to fail the job. Do not fabricate terminal output: run the commands and paste your own results.

---

## 17. Reference documentation

Use versioned documentation when a command or feature depends on tool versions:

- [Coverage.py configuration reference](https://coverage.readthedocs.io/en/latest/config.html)
- [Coverage.py branch coverage](https://coverage.readthedocs.io/en/latest/branch.html)
- [Coverage.py measurement contexts](https://coverage.readthedocs.io/en/latest/contexts.html)
- [Coverage.py subprocesses](https://coverage.readthedocs.io/en/latest/subprocess.html)
- [Coverage.py command-line reference](https://coverage.readthedocs.io/en/latest/commands/index.html)
- [pytest-cov configuration](https://pytest-cov.readthedocs.io/en/stable/config.html)
- [pytest-cov subprocess support and migration notes](https://pytest-cov.readthedocs.io/en/latest/subprocess-support.html)
- [pytest-cov contexts](https://pytest-cov.readthedocs.io/en/latest/contexts.html)

The documentation may evolve. Check the installed versions before adopting a version-sensitive option in production.

---

## Final principle

Coverage is most valuable when it exposes an unanswered testing question. A percentage is not quality by itself: combine execution evidence with meaningful assertions, branch-aware tests, risk assessment, mutation testing and careful code review.
