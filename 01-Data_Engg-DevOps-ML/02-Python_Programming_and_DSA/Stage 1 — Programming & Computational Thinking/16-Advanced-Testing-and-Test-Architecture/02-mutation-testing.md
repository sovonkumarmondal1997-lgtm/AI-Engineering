# Mutation Testing

> **Stage 1 — Programming & Computational Thinking**  
> **Module 16 — Advanced Testing and Test Architecture**  
> **Lesson 02**  
> **Baseline:** Python 3.12+, pytest 8+, mutmut 3.x (verify the installed release)  
> **Prerequisites:** pytest assertions, fixtures and parametrization (Module 1.7); control flow and functions (Modules 1.2–1.3); coverage concepts from Lesson 01.

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain how mutation testing evaluates whether tests detect deliberately introduced faults.
- Recognize mutations to operators, constants, conditions and return values.
- Distinguish killed, surviving, timed-out, suspicious and equivalent mutants.
- Calculate a mutation score using a clearly stated denominator.
- Run mutmut, inspect its results, and investigate individual survivors.
- Configure mutation scope and test selection using a supported `pyproject.toml` configuration.
- Improve weak tests using boundary cases, negative cases, parametrization and property-based testing awareness.
- Explain the cost of mutation testing and choose practical scope, caching, parallelism and CI schedules.
- Combine coverage, mutation score and escaped-defect information without treating any one metric as proof of quality.

---

## 1. What mutation testing asks

Code coverage tells you whether tests **reach** statements or branch destinations. Mutation testing asks a different question:

> If a small, plausible defect were introduced into the code, would the tests notice?

A mutation tool creates altered versions of source code called **mutants**, then runs tests against those versions. If a test fails because the changed behaviour is detected, the mutant is **killed**. If the relevant tests still pass, the mutant **survives** and may reveal a gap in assertions or scenarios.

Mutation testing is a form of fault-oriented test evaluation. It does not prove the suite is correct, but it probes whether tests are sensitive to selected changes in behaviour.

### 1.1 Why it matters

A test suite can achieve high line and branch coverage while asserting too little. For example, a test may call a pricing function and assert only that the result is truthy. A mutation that changes the exact price might survive.

Mutation testing makes this weakness more concrete: instead of asking “does this test look strong?”, it asks “does this test fail when a plausible behaviour change is made?”

### 1.2 When to use it

Mutation testing is especially useful for:

- validation and boundary logic;
- pricing, risk scores and other business rules;
- parsers and transformation functions;
- error-handling and retry logic;
- critical code where incorrect results have a high cost;
- evaluating whether new tests actually protect a bug fix.

It is usually less efficient to run every mutant against a large, slow integration suite on every commit. Start with small, fast unit tests and critical modules.

---

## 2. What is a mutant?

A **mutant** is a program variant created by applying a small change to the original source. Mutation operators define the changes the tool can make. The goal is not to generate arbitrary broken programs; it is to introduce plausible, localized faults.

Common mutation categories include:

| Category | Example mutation | Possible defect represented |
|---|---|---|
| Comparison operator | `age >= 18` → `age > 18` | Incorrect boundary |
| Arithmetic operator | `total + fee` → `total - fee` | Wrong calculation |
| Constant | `retry_limit = 3` → `retry_limit = 4` | Wrong threshold or literal |
| Condition | `if valid:` → `if not valid:` | Inverted decision |
| Boolean expression | `is_admin and enabled` → `is_admin or enabled` | Incorrect authorization/eligibility |
| Return value | `return total` → `return 0` | Incorrect result |
| Loop control | `break` → `continue` | Different iteration behaviour |
| String constant | `"invalid row"` → a changed message | Output contract changed; often lower value if message text is not part of the contract |

The available operators depend on the mutation tool and its version. Do not assume every category is generated automatically. Some tools focus on syntax inside functions, so module-level declarations, asynchronous constructs or type-level behaviour may not be covered.

### 2.1 A mutation is a hypothesis, not necessarily a real bug

A mutant is a test of the suite, not proof that the mutation is a realistic defect. Some changes are equivalent to the original program for all relevant inputs. Others are detectable only through behaviour the product does not promise, such as an internal log message. Review the mutant before treating its status as a quality signal.

---

## 3. The mutant lifecycle and result categories

A mutation run typically follows this workflow:

1. Discover the source files and test suite.
2. Identify mutation locations and candidate operators.
3. Create or apply one mutant.
4. Run the tests selected for that mutant.
5. Record the outcome.
6. Repeat for the remaining mutants.
7. Summarize results so the developer can investigate survivors and other noteworthy outcomes.

The exact internal implementation and output labels vary by tool/version. Understand the concepts below rather than relying on a label alone.

### 3.1 Killed mutant

A mutant is **killed** when a test fails in a way attributable to the mutation. This is evidence that the test suite detects that particular change.

A failure caused by a broken test environment, import error, or unrelated flaky test should not automatically be counted as a meaningful kill. Inspect suspicious failures and ensure the original, unmutated suite passes first.

### 3.2 Surviving mutant

A mutant **survives** when the relevant tests complete successfully despite the mutation. This often indicates one of the following:

- a missing assertion;
- a missing boundary or negative test;
- an assertion that is too broad;
- the mutated behaviour is not observable through the tested interface;
- the mutation does not change behaviour for the tested inputs;
- the tests selected for the mutant do not include the relevant tests.

A survivor is a prompt for investigation, not a command to add an assertion for every implementation detail. Sometimes the mutant is equivalent or the behaviour is intentionally unspecified.

### 3.3 Timed-out mutant

A **timed-out** mutant causes the test execution to exceed the configured limit. For example, a mutation might turn a terminating loop into a non-terminating one.

A timeout is not automatically a successful kill. Some tools classify timeouts separately because slow environments, external services, or flaky tests can also cause them. Review the tool's outcome semantics and the failing process before counting a timeout as detected.

### 3.4 Suspicious or errored mutant

A mutant may be labelled **suspicious**, errored, or otherwise inconclusive if the tool cannot confidently interpret the run—for example, the mutated program fails during import, the test runner crashes, or a test process fails for reasons unrelated to a behavioural assertion.

Do not silently count inconclusive outcomes as kills. Investigate the failure, rerun it if needed, and report the classification policy explicitly.

### 3.5 Equivalent mutant

A mutant is **equivalent** when the mutated program has the same observable behaviour as the original for all inputs and environments within the defined contract. For example, a change in an internal expression might be algebraically equivalent under the function's actual domain, or a mutated logging string might not affect the externally promised behaviour.

Equivalence is difficult to prove in general. A mutant that survives is not necessarily equivalent; it may simply reveal a missing test. Mark a mutant equivalent only after reasoned review, not because it is inconvenient to kill.

Equivalent mutants should be excluded from the mutation-score denominator when they have been identified and classified as such. If they remain in the denominator, they can make a good suite appear weaker than it is.

---

## 4. Mutation score: formula and interpretation

The roadmap's basic formula is:

\[
\text{Mutation score} =
\frac{\text{Killed mutants}}
{\text{Total non-equivalent mutants}} \times 100\%
\]

For a transparent calculation, let:

- \(K\) = killed mutants;
- \(S\) = surviving mutants;
- \(E\) = confirmed equivalent mutants;
- \(I\) = inconclusive outcomes (such as errors or timeouts not yet resolved).

If all non-equivalent mutants have a resolved outcome, then:

\[
\text{Mutation score} = \frac{K}{K + S} \times 100\%
\]

Equivalent mutants are excluded. Inconclusive outcomes should be resolved or reported separately; do not quietly treat them as kills or remove them without explanation.

### 4.1 Worked example

Suppose a run identifies:

- 64 killed mutants;
- 16 surviving mutants;
- 10 confirmed equivalent mutants;
- 5 timeouts still under investigation.

Do **not** present a final score as though all 95 outcomes were resolved. If the 5 timeouts are excluded temporarily, state that the score is provisional and based on the 80 resolved, non-equivalent mutants:

\[
64 / (64 + 16) \times 100\% = 80\%
\]

The report should say: **provisional mutation score 80% among resolved non-equivalent mutants; 5 timed-out mutants remain unresolved; 10 equivalent mutants were excluded.**

This is more honest and actionable than presenting a single number without its denominator or unresolved outcomes.

### 4.2 Why 100% is not the goal

A 100% mutation score is not automatically practical or desirable:

- equivalent mutants may be hard to identify;
- some mutations represent irrelevant implementation changes;
- mutation operators do not represent every real-world defect;
- certain behaviours are expensive or impossible to test deterministically;
- chasing the final few percentage points can cost more than the risk reduction justifies.

A strong process reviews surviving mutants in high-risk logic, documents equivalent or irrelevant mutants, and uses the score as one signal alongside other evidence.

---

## 5. The roadmap's age-validation example: boundary tests matter

Consider this function:

```python
def is_adult(age: int) -> bool:
    return age >= 18
```

The contract is that age 18 and above is adult; ages below 18 are not. The following test is weak:

```python
def test_adult() -> None:
    assert is_adult(30)
```

A mutant that changes `age >= 18` to `age > 18` still passes this test because `30 > 18` is true. The mutant **survives**. The test never checks the boundary where the two implementations differ.

### 5.1 Strengthen the test with boundary cases

A better test suite checks ages immediately below, at, and above the boundary:

```python
import pytest

from age_rules import is_adult


@pytest.mark.parametrize(
    ("age", "expected"),
    [
        (17, False),
        (18, True),
        (19, True),
    ],
)
def test_is_adult_boundary(age: int, expected: bool) -> None:
    assert is_adult(age) is expected
```

This is a complete test module if `age_rules.py` contains the `is_adult` function above and the module is importable from the test environment. It will kill the `>=` to `>` mutant because the case `age=18` expects `True`, while the mutant returns `False`.

Why all three cases?

- **17** tests the negative side of the boundary.
- **18** tests the exact boundary and distinguishes `>=` from `>`.
- **19** tests the positive side away from the boundary.

The boundary case is the critical one for this specific mutant, but the surrounding cases make the intended rule explicit and help detect other plausible errors.

### 5.2 Negative cases and contract decisions

If the function is supposed to reject negative ages, its contract must say so and the implementation must enforce it. Do not invent validation rules that the API has not promised.

For example, this is a different contract:

```python
def is_adult(age: int) -> bool:
    if age < 0:
        raise ValueError("age must be non-negative")
    return age >= 18
```

Tests should now check both the return-value boundary and the invalid-input behaviour:

```python
import pytest

from age_rules import is_adult


@pytest.mark.parametrize(
    ("age", "expected"),
    [
        (0, False),
        (17, False),
        (18, True),
        (19, True),
    ],
)
def test_is_adult_valid_ages(age: int, expected: bool) -> None:
    assert is_adult(age) is expected


def test_is_adult_rejects_negative_age() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        is_adult(-1)
```

The negative-age test is appropriate only if rejecting negative values is part of the stated contract. The lesson is to align tests with requirements, not to expand the API arbitrarily.

---

## 6. Install and run mutmut

The roadmap names `mutmut` and lists the commands `mutmut run`, `mutmut results`, and `mutmut show <id>`. **These command examples are version-sensitive.** Current mutmut 3 documentation uses `mutmut run` and an interactive `mutmut browse` workflow; older releases documented `results` and `show`. Check the installed release before using older commands. Do not assume a mutmut 2 command works with mutmut 3.

### 6.1 Install

Use a clean working tree and install mutmut as a development dependency:

```bash
uv add --dev mutmut
uv run mutmut --help
uv run mutmut run --help
```

Mutmut requires operating-system `fork` support in the current documented workflow; on Windows, use an appropriate Linux environment such as WSL. Verify the current installation requirements for your platform.

Before the mutation run, execute the ordinary suite and ensure it passes:

```bash
uv run pytest
```

Mutation testing is not a substitute for a green baseline. If the original tests already fail, mutation results are difficult to interpret.

### 6.2 Configure current mutmut 3+ with `pyproject.toml`

The current mutmut documentation uses a `[tool.mutmut]` table and the `source_paths` setting to define what code is eligible for mutation. A typical setup is:

```toml
[tool.mutmut]
source_paths = ["src/ledger/"]
pytest_add_cli_args_test_selection = ["tests/"]
```

Use paths that exist in your project. `pytest_add_cli_args_test_selection` supplies pytest arguments for test selection; it is not a list of source files. Configuration keys have changed across mutmut releases, so check the documentation for the installed version before copying an older example. In particular, do not assume the older `paths_to_mutate` setting is the current `pyproject.toml` spelling; current documentation uses `source_paths`.

Run from the project root:

```bash
uv run mutmut run
```

Mutmut maintains state so interrupted work can often be resumed. Review the tool's output and result browser rather than assuming the run completed every mutant.

### 6.3 Inspect results and individual mutants

For current mutmut 3 documentation, use the interactive browser:

```bash
uv run mutmut browse
```

Use the interface to inspect mutant names/diffs, investigate survivors, and retest selected mutants as supported by the installed release. Consult its built-in help and documentation for keyboard controls.

Older mutmut releases documented commands such as:

```bash
# Legacy/version-dependent examples — do not assume these work on mutmut 3:
mutmut results
mutmut show 12
```

If you are following an older repository or tutorial, identify the installed version first:

```bash
uv run python -c "from importlib.metadata import version; print(version('mutmut'))"
uv run mutmut --help
```

The roadmap's `mutmut run --paths-to-mutate src/ledger/pricing.py` example is version-sensitive and should not be assumed to work with current mutmut 3+. For current mutmut, configure `source_paths` in `pyproject.toml` and use documented function/module patterns or options supported by the installed release. Do not present the roadmap's command as universally executable.

### 6.4 Safe mutant investigation

When a survivor is interesting:

1. Read the original source and the mutant diff.
2. Predict which input should distinguish the mutant from the original.
3. Add a test expressing the public contract.
4. Run the new test against the original implementation.
5. Retest the mutant using the tool's supported workflow.
6. Confirm the mutant is now killed.
7. Ensure the source is restored and the normal suite passes.

Keep the repository under version control and start from a clean commit. If a workflow applies mutants directly to source files, never leave a mutant committed by mistake.

---

## 7. Interpret survivors by category

Not all surviving mutants mean the same thing. Categorize them before adding tests.

### 7.1 Logic mutations

Examples include inverted conditions, `and` changed to `or`, or a comparison boundary changed. These often expose missing negative or boundary tests.

**Response:** identify an input where the intended and mutated logic differ, then assert the expected behaviour.

### 7.2 Arithmetic mutations

Examples include `+` to `-`, or a changed threshold constant. These are especially important for totals, pricing, rates and risk scores.

**Response:** use exact expected results where appropriate, test boundaries and sign changes, and consider invariants that hold across a range of inputs.

### 7.3 Constant mutations

A constant may represent a retry limit, threshold, default value, or status code. Some constants are part of a public contract; others are implementation details.

**Response:** test the observable behaviour affected by the constant. Avoid tests that only inspect private source text unless source structure itself is the contract.

### 7.4 String and logging mutations

A mutation that changes a log message may survive if tests correctly focus on business behaviour. Exact log messages are often not a core contract, although messages can matter for a CLI, an API response, audit requirements or operational alert parsing.

**Response:** decide whether the text is part of the promised interface. Do not add brittle assertions merely to kill a low-value string mutation.

### 7.5 Return-value mutations

A changed return value is often a valuable mutant because callers observe it directly.

**Response:** assert exact values or meaningful invariants rather than only checking that a result is non-`None` or truthy.

### 7.6 Surviving validation mutants may indicate unobservable behaviour

If a mutation in validation code survives because no caller can observe whether invalid data was rejected, the problem may be architectural rather than just a missing test. Validation should have a clear outcome: a return value, a documented exception, a structured error, or a visible rejection in the pipeline.

A survivor can therefore drive design improvements: simplify the logic, expose a meaningful result, or define the contract more clearly.

---

## 8. Use parametrization and property-based testing awareness

### 8.1 Parametrized tests

Parametrization makes a group of related boundary and negative cases explicit and reduces duplicated test code. The age example uses cases 17, 18 and 19 to target a comparison mutation.

Good parametrization should have descriptive case IDs where that improves failure diagnosis, and should keep each case's expected behaviour clear. Do not create a large list of values without explaining which requirement they represent.

### 8.2 Property-based testing awareness

Property-based testing tools such as Hypothesis generate many inputs and check general properties. They can be especially effective for boundary and arithmetic mutants because generated values may find cases that hand-picked examples miss.

For instance, the property “every non-negative age below 18 is not an adult” expresses a general rule rather than three fixed examples. Property-based testing is covered in more depth in Stage 2; here, the important point is that generated tests can complement explicit examples and mutation testing.

A property-based test is not automatically strong. The property itself must be correct and sufficiently specific. A weak property can pass for both original and mutated implementations.

### 8.3 Fault-oriented test design

For each survivor, ask:

1. What exact behaviour did the mutation change?
2. Which input makes the original and mutant diverge?
3. Is that input within the contract?
4. What observable result should differ?
5. What assertion would fail for the mutant and pass for the original?

This is more effective than writing random tests merely to increase a score.

---

## 9. Coverage-guided test selection

A large suite may take a long time to run for every mutant. **Coverage-guided test selection** uses information about which tests execute which code to run only tests likely to be affected by a mutant.

The reasoning is straightforward: if a test never executes the mutated function, it is unlikely to detect a behavioural change inside that function. Restricting test execution can save substantial time.

Mutmut documents that it learns which tests to execute and remembers previous work. However, test-selection mechanisms are tool-specific, and overly narrow selection can miss indirect dependencies or effects. Validate the tool's selection behaviour in your project and periodically run broader/full mutation jobs.

Use test selection as an optimization, not as a replacement for full regression testing.

---

## 10. Runtime cost, caching, parallelism and incremental work

Mutation testing can be expensive because it runs tests repeatedly against many code variants.

A rough conceptual cost model is:

\[
\text{work} \approx \text{number of mutants} \times \text{test-run cost per mutant}
\]

Actual runtime is affected by test selection, caching, process startup, parallelism, timeouts, and whether the suite uses databases, networks or other slow resources.

### 10.1 Start with fast tests

Use unit tests and the critical module first. Avoid running the entire slow end-to-end suite for every mutant unless the extra coverage of integration behaviour is justified.

A useful staged strategy is:

1. Fast unit tests on a critical module during development.
2. A broader mutation run on core packages before release.
3. Full or sampled mutation testing nightly when runtime is significant.

### 10.2 Caching and incremental runs

Mutmut remembers previous work and can resume interrupted runs. This is useful during iterative development: add a test, rerun relevant mutants, and see whether survivors are now killed.

Caches are valid only for the source, tests, configuration and dependencies they represent. If the source or relevant non-Python test inputs change, ensure the tool invalidates or refreshes the relevant state. When results seem inconsistent, consult the tool's cache guidance and perform a clean run when necessary.

Do not assume a cached run is a full run. Record whether a report represents all mutants, a subset, or only work resumed from a prior run.

### 10.3 Parallelism

Parallel workers can reduce wall-clock time, but add process and resource pressure. Tests that use shared databases, fixed ports, global state, background threads or non-fork-safe libraries can behave differently in mutation workers.

Current mutmut documentation describes process-isolation options such as `fork` and `forkserver`, both requiring fork support. Start with the default documented strategy. If runs hang, crash or become non-reproducible because test setup has process-level side effects, investigate isolation settings. Do not change process settings without understanding the operating system and test dependencies.

Parallelism is an optimization; it does not fix flaky or non-isolated tests.

### 10.4 Incremental scope

The roadmap recommends mutating changed files or core modules. In current mutmut, configure the source scope and use only filters/options supported by the installed release. Some versions support function/module patterns or other selection mechanisms; command syntax is version-sensitive.

A focused run is useful for fast feedback, but label its scope clearly. A score from one critical file is not comparable to a score from the entire project.

---

## 11. CI strategy: commit, nightly and pre-release

Mutation testing is often too costly for every commit, especially when tests include I/O. A balanced policy may look like this:

| Stage | Suggested mutation scope | Purpose |
|---|---|---|
| Developer loop | One function or critical module | Quickly investigate survivors |
| Pull request | Optional targeted mutation job for changed critical logic | Early feedback without excessive CI cost |
| Nightly | Broader package or project run | Find gaps missed by routine tests |
| Pre-release | Broad, reviewed run with stable dependencies | Assess high-risk changes before shipping |

These are policy options, not rigid rules. A small project with fast tests may run mutation testing on every pull request. A large I/O-heavy repository may reserve full mutation runs for nightly or pre-release jobs.

### 11.1 CI discipline

A mutation job should:

1. install locked dependencies and the pinned mutation tool;
2. run the ordinary suite first;
3. run the agreed mutation scope;
4. preserve results and diagnostics as artifacts;
5. report killed, surviving, equivalent and inconclusive outcomes distinctly;
6. fail only according to a documented policy that the tool actually enforces.

Do not invent a universal mutmut score flag or assume a command from another version works. Check `mutmut --help` and the installed version's documentation. If a CI threshold is needed but the tool does not provide the required gate in your version, implement a small, reviewed reporting step around the tool's supported output rather than parsing unstable terminal text without tests.

---

## 12. Higher-order mutants and sampling

A **first-order mutant** changes one location or applies one mutation. A **higher-order mutant** combines multiple mutations in the same variant.

Higher-order mutants can model interacting faults, but interpretation becomes harder: a test may kill the combined variant even if it would not detect either individual change, and the combined mutation can behave differently from the sum of its parts. They also increase the search space.

**Statistical sampling** runs a representative subset of possible mutants when a complete run is too expensive. Sampling can provide useful trend information, but a sample score has uncertainty and may miss a specific critical mutation. Document the sampling strategy and avoid presenting a sample as a complete census.

Use higher-order mutation or sampling only when the added insight justifies the complexity. For most learning and routine unit-test evaluation, start with first-order mutants on a focused scope.

---

## 13. Limitations and complementary techniques

Mutation testing evaluates only the mutations that the tool generates and the tests it runs. It has important limitations:

- **It cannot test missing features.** If a requirement is absent from the implementation entirely, ordinary mutations of existing code may not expose it.
- **Equivalent mutants exist.** Some changes do not alter observable behaviour.
- **I/O-heavy suites are expensive.** Repeating database, network or external-service tests can be slow and flaky.
- **Some mutation operators are missing.** Async behaviour, type-level logic, framework-specific code or module-level constructs may not be well represented by a tool.
- **Noise exists.** Logging and formatting mutations may not matter unless those outputs are part of the contract.
- **Survivors need interpretation.** A surviving mutant may indicate a weak test, an irrelevant change or equivalent behaviour.
- **A killed mutant does not prove broad correctness.** It proves only that some test detected that particular variant under that run.

Compare mutation testing with other approaches:

- **Test review:** checks whether assertions match requirements.
- **Property-based testing:** explores many inputs against specified properties.
- **Fault injection:** introduces failures into dependencies or runtime conditions, such as a failed network call.
- **Coverage:** shows which code and branches were reached.
- **Incident history:** shows which defects escaped in production and where risk is concentrated.

These approaches answer different questions and work best together.

### 13.1 Cross-language awareness

Mutation testing is a general practice, not a Python-only technique. Tools such as **Stryker** in JavaScript/TypeScript ecosystems and **PIT** in Java ecosystems apply the same broad idea: introduce small code changes and evaluate whether tests detect them. Their operators, configuration and scoring details differ; do not transfer one tool's commands or semantics to another.

---

## 14. Combine coverage, mutation score and escaped defects

Use three complementary signals:

1. **Coverage (reach):** Did tests execute the relevant statements and branch destinations?
2. **Mutation score (test sensitivity):** Did tests detect selected plausible changes?
3. **Escaped-defect rate / incident history (real-world outcome):** What defects still reached users or production systems?

An illustrative interpretation:

| Coverage | Mutation result | Possible interpretation | Next action |
|---|---|---|---|
| Low | Low or unknown | Significant code may not be reached | Add tests for required paths |
| High | Low | Tests execute code but may not assert behaviour strongly | Review survivors and assertions |
| High | High | Stronger evidence for the mutations tested | Continue risk-based review; do not assume defect-free code |
| High | High, but incidents persist | The measured tests or mutations may not represent real failure modes | Study incidents, integration gaps and missing requirements |

A high mutation score with a high escaped-defect rate can indicate that the mutation operators or tested scope do not model the failures that matter. A low score in a low-risk formatting helper may matter less than a single survivor in authorization or data deletion logic.

Do not combine these signals into an arbitrary composite number unless the organization has a defensible model. Use them to guide investigation and engineering decisions.

---

## 15. Common mistakes

### Mistake 1: Running mutation testing over slow integration suites on every commit

**Why it fails:** every mutant multiplies test cost, and external systems add flakiness.  
**Better approach:** begin with fast unit tests, focus on critical modules, and schedule broader runs nightly or pre-release when appropriate.

### Mistake 2: Chasing equivalent mutants

**Why it fails:** some variants do not change observable behaviour, and trying to kill them can produce brittle tests or test implementation details.  
**Better approach:** inspect the mutant, reason about the contract, document confirmed equivalence, and exclude it from the score denominator transparently.

### Mistake 3: Ignoring survivors in critical code

**Why it fails:** survivors in validation, financial calculations, permission checks or recovery paths may reveal serious assertion gaps.  
**Better approach:** triage by risk, find an input that distinguishes the original from the mutant, and add a contract-level test when justified.

### Additional operational mistakes

- Starting mutation testing before the baseline suite passes.
- Treating every timeout or import error as a killed mutant.
- Comparing scores from different scopes or tool versions as though they were equivalent.
- Running only a tiny incremental subset but reporting it as a full project score.
- Writing tests that mirror implementation details rather than observable behaviour.
- Leaving an applied mutant in the working tree or committing it accidentally.
- Using obsolete mutmut commands without checking the installed version.
- Assuming a high mutation score means missing requirements or integration failures have been tested.

---

## 16. Practical experiment: a module with 95% coverage

The roadmap asks you to take a module with approximately 95% coverage, run mutation testing, and write a report describing weak spots and tests added.

### Experiment steps

1. Choose a small module with existing tests and approximately 95% line coverage. Record the source scope and branch-coverage setting so the baseline is reproducible.
2. Ensure the unmutated suite passes.
3. Run mutmut using the configuration and command appropriate to your installed version.
4. Inspect the mutation outcomes. Record killed, surviving, equivalent and unresolved mutants separately.
5. Select at least three survivors or suspicious outcomes. For each, write the original expression, mutant expression, likely behavioural difference and a candidate distinguishing input.
6. Predict which test should kill each mutant **before** changing the tests.
7. Add meaningful boundary, negative or parametrized tests as the contract requires.
8. Retest the mutants and confirm that the intended ones are now killed.
9. Re-run the ordinary test suite and coverage report.
10. Write a short report with the before/after evidence and remaining risks.

### Suggested experiment report template

```text
Module:
Source revision:
Python / pytest / mutmut versions:
Baseline test result:
Baseline line coverage:
Baseline branch coverage (if measured):
Mutation scope:
Total mutants:
Killed:
Survived:
Equivalent (reviewed):
Timed out / suspicious / unresolved:
Provisional or final mutation score and denominator:

Survivor 1
- Original code:
- Mutated code:
- Predicted distinguishing input:
- Test added:
- Outcome after retest:
- Why the test expresses the contract:

Survivor 2
...

Tests added:
- Boundary cases:
- Negative cases:
- Parametrized/property-style cases:

Remaining survivors and rationale:
Runtime and tooling observations:
Risks not represented by this mutation run:
```

Do not fill the report with invented results. Record only what your actual run produced. If the module does not have exactly 95% coverage, record the actual value and explain the selected baseline.

### Acceptance criteria

- The baseline suite is green before mutation testing.
- At least three mutant outcomes are investigated.
- At least one weak boundary test is strengthened.
- The score includes a clearly stated denominator and handles equivalent/inconclusive outcomes transparently.
- The report explains what the experiment did not test.

---

## 17. Self-check questions (from the roadmap)

Answer each question in your own words and use evidence from your experiment.

### 1. What does a surviving mutant tell you?

A strong answer explains that the selected tests did not detect that particular change. It identifies several possible reasons: a missing assertion, missing boundary/negative case, irrelevant or equivalent mutation, unobservable behaviour, or incomplete test selection. It does not claim that every survivor proves a defective test.

### 2. Why is an equivalent mutant a problem for the score?

A strong answer explains that the mutation does not change observable behaviour under the relevant contract, so tests cannot reasonably be expected to distinguish it. Including confirmed equivalent mutants in the denominator can lower the score unfairly. The answer should also recognize that proving equivalence is difficult and that a survivor must not be casually labelled equivalent.

### 3. Pick a function, predict three surviving mutants before running the tool, then compare.

Choose a small function, such as a threshold check, a total calculation, or a validation rule. Before running mutmut, predict three plausible mutants that you expect to survive and explain why the current tests would miss each one. For each prediction, write down an input that should distinguish the mutant from the original. Then run the tool, inspect the actual mutants, and compare your predictions with the outcomes.

A complete answer includes:
- the original function and its contract;
- three predicted mutations;
- a distinguishing input and expected result for each;
- the actual mutation-tool outcome;
- any tests added and the result after retesting;
- an explanation of any discrepancy between prediction and outcome.

---

## 18. Completion checklist

You are ready to continue when you can check all of the following:

- [ ] I can explain what mutation testing measures and how it complements coverage.
- [ ] I can identify mutations to operators, constants, conditions and return values.
- [ ] I can distinguish killed, surviving, timed-out, suspicious and equivalent mutants.
- [ ] I can calculate a mutation score with an explicit denominator and transparent treatment of equivalent mutants.
- [ ] I can run mutmut and inspect a specific mutant using commands supported by my installed version.
- [ ] I can use `pyproject.toml` to scope mutation testing and test selection.
- [ ] I can strengthen a weak age-validation test with cases 17, 18 and 19.
- [ ] I understand how parametrization and property-based testing can expose boundary weaknesses.
- [ ] I can explain coverage-guided selection, caching, parallelism and incremental runs.
- [ ] I can justify when mutation testing belongs in developer, PR, nightly or pre-release workflows.
- [ ] I understand higher-order mutants, sampling, equivalent mutants and tool limitations.
- [ ] I can combine coverage, mutation score and escaped-defect history without treating a metric as proof of correctness.

---

## 19. Reference documentation

Commands and configuration are version-sensitive. Consult the current documentation for the version installed in your environment:

- [mutmut documentation](https://mutmut.readthedocs.io/en/latest/)
- [mutmut configuration](https://mutmut.readthedocs.io/en/latest/#configuration)
- [mutmut workflow and result browsing](https://mutmut.readthedocs.io/en/latest/#workflow)
- [pytest documentation](https://docs.pytest.org/en/stable/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/en/latest/)

The roadmap's `mutmut results` and `mutmut show <id>` examples describe an older CLI surface. Current mutmut 3 documentation describes the `browse` workflow. Always verify the installed version's `--help` output before adopting commands in scripts or CI.

---

## Final principle

Coverage tells you whether tests reach code. Mutation testing probes whether they notice selected changes to that code. A surviving mutant is a useful question to investigate—not an automatic verdict. Prioritize survivors by risk, strengthen tests around the intended contract, and interpret every score alongside its scope, unresolved outcomes and real-world defect history.
