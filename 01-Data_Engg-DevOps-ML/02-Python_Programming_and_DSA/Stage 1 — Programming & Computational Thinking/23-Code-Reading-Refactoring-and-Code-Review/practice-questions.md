# Module 1.23 — Practice Questions

> **Module:** Code Reading, Refactoring and Code Review  
> **Scope:** Lessons 01–08  
> **Use:** Attempt the questions before consulting the answer key. All commit IDs, repository layouts, metrics, and pull requests in this file are illustrative teaching data, not claims about a real repository.

## How to use this bank

There are 37 questions across the four phases specified by the module roadmap, keeping close to the roadmap’s target of approximately 35. Questions progress from orientation and characterization to risk-based refactoring, review, history investigation, open-source contribution, and source reading. Questions with an explicit evaluation rubric can have more than one defensible answer; explain assumptions and evidence.

Suggested practice: complete each phase in order, keep code and investigation notes in a scratch repository, and use the answer key only after recording your own reasoning. Use the project's documented commands when a real repository differs from the examples here.

## Phase A — Understanding Existing Code

### A01 — Plan repository orientation

**Lesson:** 01 — Reading Unfamiliar Codebases  
**Level:** Foundational

You join a legacy ETL repository with this illustrative tree:

```text
legacy-ledger/
├── README.md
├── pyproject.toml
├── requirements.txt
├── run_daily.py
├── ledger/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   ├── report.py
│   └── storage.py
├── tests/
│   ├── test_transform.py
│   └── test_report.py
├── data_samples/
│   └── ledger-small.csv
└── docs/
    └── architecture.md
```

The daily job has failed, but no failure details are available yet. Write a first-hour investigation plan in 6–10 ordered steps. Name the files or commands you would inspect and explain how you would avoid changing behavior before understanding it.

**Produce:** An ordered plan and at least three questions you need answered.  
**Evaluation:** Prioritizes documented run instructions, entry point, execution flow, tests, inputs/outputs, and evidence collection; avoids speculative refactoring.

### A02 — Trace an execution flow

**Lesson:** 01 — Reading Unfamiliar Codebases  
**Level:** Foundational

```python
# run_daily.py
from ledger.extract import read_rows
from ledger.transform import normalize_rows
from ledger.report import summarize

rows = read_rows("daily.csv")
clean = normalize_rows(rows)
summary = summarize(clean)
print(summary)
```

Assume `read_rows` reads CSV records, `normalize_rows` standardizes field names and numeric values, and `summarize` aggregates totals. Draw the execution flow and list the observable boundaries where you would inspect data shape, exceptions, and side effects.

**Produce:** A small diagram or numbered call path, plus a boundary table.  
**Evaluation:** Identifies file I/O, transformations, aggregation, output, and likely exception/validation boundaries without assuming undocumented function behavior.

### A03 — Identify test seams in legacy code

**Lesson:** 01 — Reading Unfamiliar Codebases; Lesson 02 — Characterization Tests
**Level:** Intermediate

```python
# ledger/report.py
import csv
from datetime import date
from pathlib import Path

TAX_RATE = 0.08


def daily_report(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    total = sum(float(row["amount"]) for row in rows)
    return {"date": date.today().isoformat(), "total_with_tax": total * (1 + TAX_RATE)}
```

Identify at least four seams that could make this function easier to test or reason about. For each seam, propose the smallest useful change and state whether it should change behavior.

**Produce:** A seam list with risk notes.  
**Evaluation:** May discuss filesystem input, current date, tax policy, parsing/validation, calculation, and output; distinguishes introducing seams from altering the contract.

### A04 — Characterize behavior before refactoring

**Lesson:** 02 — Characterization Tests for Legacy Code  
**Level:** Intermediate

```python
def normalize_code(value):
    if value is None:
        return ""
    return str(value).strip().upper()
```

Write pytest tests that characterize the current behavior for `None`, an empty string, whitespace, a number, and a mixed-case string. Do not “improve” the behavior in this question; the goal is to record what the code currently does.

**Produce:** A valid test function or parametrized test.  
**Evaluation:** Tests current outputs explicitly, including `normalize_code(17) == "17"`; identifies that characterization does not prove the behavior is desirable.

### A05 — Behavior is not the same as correctness

**Lesson:** 02 — Characterization Tests for Legacy Code  
**Level:** Intermediate

A legacy function returns `0.0` for a missing amount because it catches `KeyError` and substitutes zero. Downstream reports have relied on this for three years. A new analyst says missing amounts should be rejected.

Explain how you would document and test the current behavior, decide whether it is a bug, and introduce a behavior change safely.

**Produce:** A short migration/testing plan.  
**Evaluation:** Separates characterization from requirements, checks business semantics and callers, proposes an explicit behavior-change decision with regression tests and release communication where needed.

### A06 — Choose the right test boundary

**Lesson:** 02 — Characterization Tests for Legacy Code  
**Level:** Intermediate

A report function reads a file, calls a database, calculates totals, and sends an email. The regression under investigation is an incorrect rounding result. You have a small sample of rows and can run a local unit test suite, but no test database or mail server.

Choose the most appropriate initial test boundary and identify which dependencies should be replaced or held constant. Explain what an integration test would add later.

**Produce:** Test strategy and rationale.  
**Evaluation:** Isolates the deterministic calculation with a small fixture first; does not claim that unit tests alone prove database/email integration works.

## Phase B — Changing Code Safely

### B01 — Apply a named refactoring

**Lesson:** 03 — Refactoring Catalogue  
**Level:** Intermediate

Refactor the repeated classification logic below using **Extract Function** only. Preserve the current outputs exactly.

```python
def classify_a(score):
    if score >= 80:
        return "pass"
    return "review"


def classify_b(score):
    if score >= 80:
        return "pass"
    return "review"
```

**Produce:** Refactored code and tests for `79`, `80`, and `81`. State whether the duplicate function names should remain public.

**Evaluation:** Extracts a shared helper without silently changing threshold semantics; discusses compatibility before removing or renaming public functions.

### B02 — Smell and remediation selection

**Lesson:** 04 — Code Smells and Technical Debt  
**Level:** Intermediate

A 180-line function mixes CSV parsing, schema validation, currency conversion, database writes, and Slack notifications. It has five nested branches and is changed in nearly every incident fix. Name at least three smells, propose a staged remediation, and identify one refactoring you would *not* combine with a bug fix.

**Produce:** Smell → evidence → action table.  
**Evaluation:** Grounds labels in observed characteristics, recommends seams/tests and small extractions, and separates behavior changes from structural changes.

### B03 — Read churn and complexity data

**Lesson:** 04 — Code Smells and Technical Debt  
**Level:** Intermediate

Illustrative sample:

| File | Changed lines in 90 days | Commits touching file | Cyclomatic complexity of largest function | Production incidents linked |
|---|---:|---:|---:|---:|
| `ledger/transform.py` | 1,400 | 24 | 18 | 4 |
| `ledger/report.py` | 320 | 8 | 7 | 0 |
| `ledger/storage.py` | 900 | 5 | 12 | 3 |
| `ledger/formatting.py` | 1,900 | 31 | 4 | 0 |

Using the lesson's illustrative screening thresholds (high complexity = cyclomatic complexity `>= 15`; high churn = changed lines `>= 200`), classify a file as a **metric hotspot only when both thresholds are met**; otherwise classify it as **not a metric hotspot**. Then choose two files for further risk investigation, distinguishing the metric-based result from incident-driven risk. Explain what the data suggests and does *not* prove, and name two additional data points you would collect.

**Produce:** A classification table plus a ranked shortlist with caveats.  
**Evaluation:** Applies the stated thresholds consistently; distinguishes `transform.py` as a metric hotspot from `storage.py` as an incident-driven risk candidate; does not treat churn alone as defect probability.

### B04 — Structural versus behavioral change

**Lesson:** 03 — Refactoring Catalogue; Lesson 02 — Characterization Tests  
**Level:** Intermediate

A proposed PR renames `calculate_total` to `compute_total`, moves it into `ledger/calculations.py`, changes rounding from `round(x, 2)` to `Decimal`, and adds a new missing-value exception. Classify each change as structural, behavioral, or potentially both. Recommend how to split or sequence the work.

**Produce:** Classification and safe sequence.  
**Evaluation:** Identifies rename/move as intended structural changes if interfaces are preserved; rounding and exception changes alter behavior and need explicit requirements/tests.

### B05 — Hotspot prioritization under constraints

**Lesson:** 04 — Code Smells and Technical Debt  
**Level:** Advanced

A team has one engineer-day available. `transform.py` has high churn and four incidents; `formatting.py` has higher churn but no incidents and low complexity; `storage.py` has fewer changes but three data-loss incidents. What evidence do you request, and what would you prioritize first? State your assumptions.

**Produce:** Decision memo under 200 words.  
**Evaluation:** Weighs incident severity/blast radius, reproducibility, ownership, test coverage, and business risk rather than ranking by a single metric.

### B06 — What is the next safest step? (Puzzle 1 of 6)

**Lesson:** 02 — Characterization Tests; Lesson 03 — Refactoring Catalogue  
**Level:** Intermediate

You must extract tax calculation from a legacy report function. There are no tests. The only known example is a production CSV whose output is available. Choose the next safest step from: (a) extract the function immediately, (b) add a new tax policy, (c) capture representative current outputs and write characterization tests, (d) rewrite the report with a class hierarchy.

**Produce:** Choice and two-sentence rationale.  
**Evaluation:** Selects (c) or a similarly safe evidence-gathering step before structural edits.

### B07 — What is the next safest step? (Puzzle 2 of 6)

**Lesson:** 03 — Refactoring Catalogue  
**Level:** Intermediate

A function has duplicated validation branches. Tests cover valid values but not empty input, malformed input, or `None`. A developer wants to replace the branches with a dictionary dispatch table.

**Produce:** The next action and the minimum cases you would characterize before changing dispatch.  
**Evaluation:** Adds tests for relevant existing edge/error behavior first; avoids choosing a new dispatch structure before knowing branch semantics.

### B08 — What is the next safest step? (Puzzle 3 of 6)

**Lesson:** 04 — Code Smells and Technical Debt  
**Level:** Intermediate

A dashboard labels `ledger/storage.py` a hotspot, but the only evidence currently available is that the file has 12 functions and high churn; the underlying complexity score and threshold are unavailable. No incident is currently reproducible.

**Produce:** The next investigation step, not a rewrite plan.  
**Evaluation:** Requests call-path/ownership/incident context, inspects tests and change history, and gathers evidence before selecting a refactoring.

### B09 — What is the next safest step? (Puzzle 4 of 6)

**Lesson:** 03 — Refactoring Catalogue; Lesson 05 — Code Review  
**Level:** Advanced

A PR combines a large rename, a new algorithm, a formatter run over 70 files, and a bug fix. CI is red. What should the author do next?

**Produce:** A practical recovery sequence.  
**Evaluation:** Re-establishes a known baseline, separates unrelated changes, identifies the failing check, and restores reviewability before adding more edits.

### B10 — What is the next safest step? (Puzzle 5 of 6)

**Lesson:** 02 — Characterization Tests; Lesson 03 — Refactoring Catalogue  
**Level:** Advanced

You are replacing a global database client with dependency injection. Only a handful of tests exist, and the nightly pipeline is business-critical.

**Produce:** A staged plan for the next commit and the validation you require before proceeding.  
**Evaluation:** Adds a seam and characterization/integration coverage in small steps, preserves default behavior, and avoids combining a new connection policy with the injection refactor.

### B11 — What is the next safest step? (Puzzle 6 of 6)

**Lesson:** 04 — Code Smells and Technical Debt; Lesson 06 — Git History Archaeology  
**Level:** Advanced

A high-churn file has a mass-formatting commit in its blame history. You need to decide whether to refactor it because the current line-by-line blame appears to implicate a recent author.

**Produce:** The next evidence-gathering step.  
**Evaluation:** Uses the ignore-revs configuration and history-aware blame, inspects meaningful changes and linked issues, and avoids assigning intent from blame metadata alone.

### B12 — Select a safe refactoring sequence

**Lesson:** 03 — Refactoring Catalogue  
**Level:** Advanced

A function both mutates a global dictionary and returns a formatted report. You need to make it deterministic for unit tests. Propose three small commits, each with a clear purpose, and list a test/check after each commit.

**Produce:** Commit sequence with test evidence.  
**Evaluation:** Introduces seams incrementally, protects existing behavior, and separates pure calculation/external effects without a large rewrite.

## Phase C — Working With Other People

### C01 — Review a seeded PR by severity

**Lesson:** 05 — Writing and Receiving Code Review  
**Level:** Advanced

PR description: “Refactor ledger lookup and improve performance.” Assume `customer_id` may originate from an untrusted request parameter. Diff:

```python
import sqlite3


def get_customer_total(db_path, customer_id):
    conn = sqlite3.connect(db_path)
    query = f"SELECT amount FROM ledger WHERE customer_id = {customer_id}"
    rows = conn.execute(query).fetchall()
    total = sum(row[0] for row in rows)
    return round(total, 2)
```

List findings ordered as blocking, important, and optional. Include correctness, security, resource management, tests, and maintainability. Do not merely comment on style.

**Produce:** Review findings with evidence and a suggested fix.  
**Evaluation:** Identifies SQL injection risk, missing connection cleanup/context handling, absent input/error/empty-row contract, and missing tests; distinguishes severity based on context.

### C02 — Rewrite harsh review comments

**Lesson:** 05 — Writing and Receiving Code Review  
**Level:** Intermediate

Rewrite each comment to be specific, respectful, and actionable:

1. “This is obviously wrong.”
2. “Why would you ever do it this way?”
3. “Bad tests. Fix them.”

**Produce:** Three replacement comments, each explaining impact or asking a genuine question.  
**Evaluation:** Critiques code rather than people, states evidence/impact, and suggests a path forward without hiding a blocking concern.

### C03 — Design a useful PR template

**Lesson:** 05 — Writing and Receiving Code Review  
**Level:** Intermediate

Create a concise PR template for a Python data-processing library. It must prompt the author to explain the problem, solution, tests, compatibility or migration impact, risk/rollback, documentation/changelog, and any relevant data/privacy implications. Avoid requiring irrelevant screenshots for every change.

**Produce:** Markdown template.  
**Evaluation:** Clear checkboxes and fields; adapts to change type; does not claim that checkboxes replace reviewer judgment.

### C04 — Respond to maintainer feedback

**Lesson:** 05 — Writing and Receiving Code Review; Lesson 07 — Open-Source Contributions  
**Level:** Intermediate

A maintainer says: “This adds an abstraction we do not need. Please use the existing helper and add a regression test for empty input.” You disagree about the abstraction but agree the test is missing.

Write a response and list the code changes you would make next. Include how you would handle the disagreement if the project has an established convention.

**Produce:** Response plus action list.  
**Evaluation:** Acknowledges the actionable test gap, asks or explains trade-offs respectfully, checks project conventions, and avoids treating review as a personal conflict.

### C05 — Diagnose CI failure

**Lesson:** 05 — Writing and Receiving Code Review; Lesson 07 — Open-Source Contributions  
**Level:** Intermediate

A PR passes `pytest` locally but fails CI in these jobs:

```text
Linux / Python 3.12: PASS
Windows / Python 3.12: FAIL — path assertion expected '/tmp/a.csv'
Python 3.13: FAIL — DeprecationWarning treated as error
Lint: PASS
Type check: PASS
```

Give an ordered diagnostic plan and explain why “CI is broken” is not yet a sufficient conclusion.

**Produce:** Troubleshooting checklist.  
**Evaluation:** Investigates platform-specific path assumptions, warning/version compatibility, reproduces the matrix failures, reads CI config, and reports evidence before changing code.

### C06 — Handle a design disagreement

**Lesson:** 05 — Writing and Receiving Code Review  
**Level:** Advanced

A reviewer wants a generic plugin architecture for two implementations. You think a simple function parameter is enough. The PR is already 500 changed lines and includes unrelated formatting.

Describe how you would resolve the design question and improve the review process.  
**Produce:** A short facilitation plan.  
**Evaluation:** Uses requirements and likely extension points, suggests an issue/design discussion for nontrivial decisions, narrows the diff, and accepts that maintainers decide project direction.

### C07 — Identify review risk beyond correctness

**Lesson:** 05 — Writing and Receiving Code Review  
**Level:** Advanced

A PR adds a new dependency to parse uploaded CSV files. The unit tests pass. List the additional checks you would request before approval, including supply-chain, compatibility, operational, and privacy considerations.

**Produce:** Risk checklist with priorities.  
**Evaluation:** Includes license/maintenance/version policy, dependency and vulnerability review, untrusted-input handling, file-size/resource limits, supported Python/platforms, reproducibility, and data exposure.

## Phase D — Going Upstream

### D01 — Bisect exit-code interpretation

**Lesson:** 06 — Git Blame, Bisect and History Archaeology  
**Level:** Intermediate

A script used with `git bisect run` returns these statuses:

- `0`: the regression test passes.
- `1`: the regression test fails.
- `125`: the test cannot run on this revision because a required interpreter is unavailable.

Explain how Git interprets these values. What should the script return if a test runner itself crashes due to an infrastructure issue that makes the result inconclusive? The regression test is also flaky: it sometimes fails and sometimes passes on the same revision. Explain how you would avoid classifying a revision from one noisy run; define a repeat policy and state what the wrapper should do when the result remains inconclusive.

**Produce:** Explanation and safe script policy.  
**Evaluation:** Correctly identifies 0 as good, 1–124 and 126–127 as bad, 125 as skip; explains that other statuses can abort bisect and that infrastructure failures need deliberate handling, not arbitrary classification as good/bad.

### D02 — Choose the history search

**Lesson:** 06 — Git Blame, Bisect and History Archaeology  
**Level:** Intermediate

For each question, choose `git log -S`, `git log -G`, `git log -L`, `git blame`, or `git bisect`, and explain why:

1. Which commit changed the number of occurrences of `retry_count`?
2. Which commits have added or removed diff lines matching a regex for a timeout assignment?
3. How did one function evolve over time?
4. Which commit first made a deterministic regression test fail between a known-good and known-bad revision?
5. Which change last touched a specific current line, after ignoring a known formatter commit?

**Produce:** Five command choices with example syntax.  
**Evaluation:** Distinguishes occurrence-count pickaxe (`-S`), regex-diff pickaxe (`-G`), line/function history (`-L`), binary search (`bisect`), and line attribution (`blame`).

### D03 — Find the commit (Scenario 1 of 4): regression window

**Lesson:** 06 — Git Blame, Bisect and History Archaeology  
**Level:** Advanced

Illustrative repository history:

```text
A0 v1.2.0 — regression test passes
A1 add logging
A2 change tax rounding
A3 update docs
A4 refactor report formatting
A5 v1.3.0 — regression test fails
```

Assume each revision is buildable and the test is deterministic. State the safest bisect workflow and the evidence you would record before fixing the bug. Do not claim these commit labels are real Git hashes.

**Produce:** Commands and interpretation.  
**Evaluation:** Uses `git bisect start`, marks known bad and good endpoints, runs the test at each candidate, records the first bad commit, inspects its diff and linked context, and resets bisect state.

### D04 — Find the commit (Scenario 2 of 4): search for behavior change

**Lesson:** 06 — Git Blame, Bisect and History Archaeology  
**Level:** Advanced

A report began including `retry_count` in serialized output sometime in the last year. The variable name appears in many commits, but the relevant change may have introduced or removed the exact key from a dictionary. Which history search would you try first, what is its limitation, and what would you do if it finds nothing?

**Produce:** Commands and fallback strategy.  
**Evaluation:** Starts with `git log -S"retry_count" -- path` where appropriate; explains `-S` tracks occurrence-count changes, not all semantically related edits; tries `-G` for matching diff lines and follows commits/issues/tests.

### D05 — Find the commit (Scenario 3 of 4): function history

**Lesson:** 06 — Git Blame and History Archaeology  
**Level:** Advanced

The function `normalize_rows` exists today, but a refactor moved it from `ledger/transform.py` to `ledger/normalize.py`. You need to understand how its empty-input behavior changed. Provide a history-investigation plan using function/line history and rename-aware file history, and explain what evidence would establish intent.

**Produce:** Commands plus evidence chain.  
**Evaluation:** Uses `git log -L` where applicable, `git log --follow` for path history, `git show`/tests and linked PR/issue; recognizes `-L` syntax depends on function/line-range support and that history does not prove intent alone.

### D06 — Find the commit (Scenario 4 of 4): formatting and blame

**Lesson:** 06 — Git Blame and History Archaeology  
**Level:** Advanced

A repository contains an illustrative formatter-only commit `f00ba42` that changed thousands of lines. Current blame points to that commit for logic that predates it. Describe a safe, repository-local approach to improve blame output and verify the logic's history. Do not rewrite shared history.

**Produce:** Configuration and verification commands.  
**Evaluation:** Adds the verified hash to `.git-blame-ignore-revs`, uses `git blame --ignore-revs-file .git-blame-ignore-revs ...`, checks the commit really is formatting-only, and inspects earlier history without treating ignore configuration as deletion of history.

### D07 — Open-source contribution workflow

**Lesson:** 07 — Contributing to Open-Source Python Projects  
**Level:** Intermediate

You find a possible bug in a Python library you use. The repository has `CONTRIBUTING.md`, a `SECURITY.md`, a `pyproject.toml`, and a PR template. Give the workflow from discovery to PR submission. Include what you would do if the issue might expose a security vulnerability.

**Produce:** Ordered workflow and a sample minimal bug report outline.  
**Evaluation:** Reads project policy, searches existing issues/PRs, reproduces with version/environment and minimal input, uses private security reporting when appropriate, follows environment/checks/changelog conventions, and does not claim a PR was accepted.

### D08 — Source-reading question: Python, stub, or accelerator?

**Lesson:** 08 — Reading CPython and Library Source  
**Level:** Intermediate

Your IDE navigates `heapq.heappush` to `Lib/heapq.py`, but runtime inspection shows `_heapq` is loaded. Explain how you would determine the active implementation path, compare behavior, and avoid confusing a type stub with executable source. Name at least three pieces of evidence.

**Produce:** Investigation steps and evidence list.  
**Evaluation:** Checks interpreter/version/module path, reads wrapper dispatch and accelerator source for the matching version, inspects tests, and uses a controlled experiment without asserting that import presence alone proves every call's path.

### D09 — Source-reading question: C-level investigation

**Lesson:** 08 — Reading CPython and Library Source  
**Level:** Advanced

A teammate claims that `list.append` always reallocates the underlying array. Plan a source-based investigation in CPython. Identify relevant repository areas, the experiment you would run, and how you would distinguish a CPython implementation detail from a language guarantee.

**Produce:** Investigation plan with evidence types.  
**Evaluation:** Starts in the matching `Objects/listobject.c` and related declarations/tests, traces resize/allocation helpers, records interpreter/build, tests repeated appends, and avoids treating capacity/allocation policy as a portable language contract.

### D10 — Open-source contribution: choose a useful scope

**Lesson:** 07 — Contributing to Open-Source Python Projects  
**Level:** Advanced

You have four possible contributions: (a) fix a typo in a frequently used guide, (b) redesign a public API without discussion, (c) add a regression test for a reproducible issue, (d) upgrade five major dependencies while fixing a bug. Rank these by a sensible first-contribution strategy and explain when the lower-ranked choices might become appropriate.

**Produce:** Ranking with assumptions.  
**Evaluation:** Prefers useful, scoped, verifiable work (often c or a depending on project need), checks project direction and guidelines, and explains why broad API/dependency changes need prior discussion and expanded validation.

### D11 — Module capstone integration

**Lessons:** 01–08; module mini-project  
**Level:** Advanced

For the roadmap's `legacy-ledger` mini-project, propose an evidence-driven plan that includes: (1) an onboarding note completed within a four-hour time box, with dependency diagram, main flows, and exactly three unresolved questions; (2) characterization/golden-master tests for the three riskiest flows; (3) a technical-debt report with hotspot evidence; (4) at least 30 small refactoring commits producing the required layering, value objects, dispatch table, injected dependencies, type hints, and `import-linter` contracts; (5) a seeded regression investigated in a roughly 300-commit disposable history with a flaky-ish test and formatting-only commit, then bisected, fixed, and documented; (6) a mock review cycle and committed team checklist/template; and (7) the mini-project's upstream contribution (or a clearly labeled private-mirror rehearsal if network/time is constrained). Include the roadmap's acceptance metrics.

**Produce:** Milestones, evidence artifacts, risk controls, and measurable completion criteria.
**Evaluation:** Sequences discovery/tests before refactoring; keeps behavior changes separate; records coverage and mutation score where available; includes `.git-blame-ignore-revs`, `-S`/`-L`, bisect log and postmortem; includes all specified architecture/refactoring deliverables; requires at least 85% characterized-area coverage, at least 40% complexity reduction across the top-five hotspot functions without behavior changes proven by golden tests, green CI, reproducible bisect evidence, and committed review checklist/PR template; reports upstream status honestly.

### D12 — Lesson 08 source-reading report capstone

**Lesson:** 08 — Reading CPython and Library Source
**Level:** Advanced

The Lesson 08 capstone requires three distinct source-reading reports, not three reports about the same layer. Plan these reports for a specific version/tag:

1. A pure-Python standard-library mechanism (for example, `dataclasses` or `functools.lru_cache`).
2. A CPython C-level mechanism (for example, list over-allocation, dictionary lookup, or a loop's bytecode execution path).
3. A third-party library vertical slice (for example, an `httpx` request path or pytest assertion rewriting).

For each report, specify the question, exact version/commit, source files/functions, tests/design documents to consult, an experiment or benchmark/debugger session, a diagram, the evidence-backed conclusion, and one design choice you would copy and one you would avoid. Explain how you will time-box the investigation and verify any AI-assisted explanation or line reference. Do not invent benchmark results or cite line numbers from a different version.

**Produce:** A three-report plan with a minimum evidence checklist for each report.
**Evaluation:** Covers all three required implementation layers; pins every report to a real tag/commit; uses source and test evidence plus an experiment; distinguishes language guarantees from version-specific implementation details; includes diagrams and “copy/avoid” lessons; records actual results and limitations; verifies AI-generated claims against source rather than trusting summaries.

## Answer Key and Reasoned Solutions

> The answers below are representative solutions. For open-ended questions, assess evidence, safety, and reasoning rather than exact wording. For a real repository, its documented conventions take precedence over generic examples.

### Phase A answers

#### A01

A defensible first hour: (1) read `README.md` and `docs/architecture.md`; (2) inspect `pyproject.toml` and the documented environment; (3) reproduce the failure using the documented command and capture the full traceback/logs; (4) trace `run_daily.py` through extract → transform → report; (5) inspect input schema and a small sample; (6) run the narrow existing tests; (7) inspect recent changes only after capturing current evidence; (8) write down assumptions and questions. Questions include: what input failed, what output is expected, which environment/version failed, and whether the failure is reproducible. Avoid changing code before a baseline is known.

#### A02

```text
run_daily.py
  -> read_rows("daily.csv")       [filesystem / CSV parsing]
  -> normalize_rows(rows)          [schema and value transformation]
  -> summarize(clean)              [aggregation]
  -> print(summary)                [observable output]
```

Inspect file-not-found/permission/encoding/CSV errors at extraction; row schema and numeric conversion errors at normalization; empty input, duplicate rows, rounding and aggregation semantics at summarization; and output formatting at the final boundary. These are candidate boundaries; the actual contracts must be confirmed from implementation/tests.

#### A03

Possible seams: pass `today` or a date provider rather than calling `date.today()` internally; separate CSV reading from calculation; inject or parameterize tax policy; isolate amount parsing/validation; extract a pure total/tax calculation; return a report object or dictionary independently of file I/O. Start with tests of the existing function. A seam-only refactor should preserve the same date format, float behavior, rounding (currently none), missing-key exception, and output shape unless a separately reviewed behavior change is approved.

#### A04

```python
import pytest

@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, ""),
        ("", ""),
        ("  ", ""),
        (17, "17"),
        (" Ab c ", "AB C"),
    ],
)
def test_normalize_code_characterizes_current_behavior(value, expected):
    assert normalize_code(value) == expected
```

This records present behavior, including coercing non-strings with `str()`. It does not establish whether coercion is a desirable business rule. If this test is in a separate file, import the function from the module under test.

#### A05

First characterize the current fallback with tests and identify callers, reports, and business rules that depend on it. Ask product/domain owners whether missing means zero, unknown, or invalid. If the requirement changes, write an explicit behavior-change test, update docs/changelog and affected callers, decide on compatibility/deprecation if public, and roll out with monitoring. Do not silently change the characterization test to make a new implementation pass without recording the requirement change.

#### A06

Start with a unit test for the deterministic calculation and a fixed sample fixture, injecting or separating the calculation from I/O. Stub the database and mail sender at this boundary. Then add integration coverage for actual database schema/query behavior and a mail adapter test or safe test server where useful. Unit tests give fast precise feedback; they do not prove external integration or delivery semantics.

### Phase B answers

#### B01

```python
def _classify(score):
    return "pass" if score >= 80 else "review"


def classify_a(score):
    return _classify(score)


def classify_b(score):
    return _classify(score)
```

The threshold remains inclusive at 80: 79 → `review`, 80 → `pass`, 81 → `pass`. A representative test protects the boundary for both public wrappers:

```python
import pytest

@pytest.mark.parametrize("score, expected", [
    (79, "review"),
    (80, "pass"),
    (81, "pass"),
])
def test_classify_a_preserves_threshold(score, expected):
    assert classify_a(score) == expected

@pytest.mark.parametrize("score, expected", [
    (79, "review"),
    (80, "pass"),
    (81, "pass"),
])
def test_classify_b_preserves_threshold(score, expected):
    assert classify_b(score) == expected
```

Keeping the public wrappers is a conservative compatibility choice; deleting or renaming them requires checking callers and API policy. The named refactoring is extraction; avoid introducing new score validation in the same change.

#### B02

Evidence-supported potential smells include a long method, mixed responsibilities, deep conditional nesting, and high coupling to external effects. Confirm duplication before labeling it a duplicated-code smell; the prompt does not establish that repeated logic exists. First add characterization/regression tests and map side effects. Then extract small pure functions (for validation/calculation), introduce explicit interfaces for storage/notification, and keep commits behavior-preserving. Do not combine a new currency conversion policy or database transaction behavior with structural extraction; that is a separate behavior change with domain review.

#### B03

Applying the stated thresholds (`complexity >= 15` and `changed lines >= 200`), only `ledger/transform.py` is a metric hotspot: 1,400 changed lines and complexity 18. `ledger/report.py` and `ledger/storage.py` have high churn but do not meet the complexity threshold; `ledger/formatting.py` has high churn but complexity 4. Nevertheless, `storage.py` is a strong second **risk-investigation** candidate because three incidents are linked and their severity may include data loss. `formatting.py` deserves context gathering because churn alone can reflect mechanical or low-risk changes. Additional data: incident severity/blast radius, test coverage/mutation results, recent diff themes, ownership concentration, change failure rate, and dependency/call-path information. The thresholds are screening rules, not proof of causation or a universal risk score.

#### B04

Renaming/moving can be structural if compatibility and imports are preserved. Switching from binary floating-point rounding to `Decimal` may change results and is behavioral; raising a missing-value exception is behavioral and may break callers. Safer sequence: add characterization tests; perform move/rename with compatibility wrappers and tests; then in a separate change define the rounding/missing-value requirements, update tests/docs and migration notes, and review behavior impact.

#### B05

A defensible memo prioritizes the file associated with the most severe and reproducible production risk, not simply the highest churn. If `storage.py` incidents involved data loss, investigate that first with incident timelines, write/read paths, transaction semantics, and tests. If `transform.py` incidents are frequent and affect every daily run, compare severity and recovery cost. Use the day to reproduce, map the path, add a regression test, and propose the smallest safe fix; do not promise a large refactor from summary metrics alone.

#### B06 — next safest step

Choose **(c)**. Capture representative current output and write characterization tests first. The output fixture should include meaningful edge cases and should be reviewed for sensitive data. Extraction comes after a testable baseline; a new policy or class hierarchy is outside the immediate task.

#### B07 — next safest step

Add tests for empty input, malformed values, `None`, valid values at branch boundaries, and any current exception behavior before changing dispatch. Confirm each branch's output and side effects. A dispatch table may be appropriate, but the test suite must protect existing semantics first.

#### B08 — next safest step

First verify how the dashboard calculated its hotspot label and obtain the actual complexity metric, threshold, and time window. Then inspect recent diffs, call sites, tests, and incident records; reproduce or construct a narrow test around a concrete risk. Collect data on change types and blast radius. Churn and function count are triage signals, not sufficient evidence to refactor blindly.

#### B09 — next safest step

Pause further edits. Re-establish a clean baseline and split unrelated formatter changes from the functional work if practical. Re-run the exact failing CI command or inspect its log, classify the failure, and reduce the PR to a reviewable change. Do not declare the formatter or CI at fault without evidence. After the failing check is understood, address it and rerun the relevant matrix.

#### B10 — next safest step

Introduce the smallest injectable boundary while preserving the current default client and behavior. Add characterization tests for successful operations and failure/cleanup behavior; test the seam without connecting to production. Then migrate one caller at a time and run unit plus safe integration tests. Keep connection policy, retries, and transaction behavior unchanged unless separately specified.

#### B11 — next safest step

Verify the formatting commit is truly formatting-only, add its full hash to `.git-blame-ignore-revs`, and run blame with that ignore file. Then inspect prior diffs, tests, issues, and PR discussions. Blame is a navigation aid, not proof of fault or intent; no shared history should be rewritten to “fix” blame.

#### B12

One defensible sequence: (1) add characterization tests around the current global-mutating function, including repeated calls and empty input; run tests; (2) extract pure formatting/calculation logic while retaining the global interface; run tests and compare output; (3) inject the dictionary/client or return explicit state, with compatibility behavior preserved and tests for side effects. Each commit should be small and revertible. The precise split depends on callers and the actual side effects.

### Phase C answers

#### C01

- **Blocking security (given the stated untrusted-input assumption):** SQL is assembled with an f-string. Bind `customer_id` as a parameter: `conn.execute("SELECT amount FROM ledger WHERE customer_id = ?", (customer_id,))`.
- **Important resource handling:** the connection is not closed explicitly. `with conn:` manages transaction commit/rollback; it does **not** close the SQLite connection. Use `contextlib.closing(sqlite3.connect(db_path))` or an explicit `try/finally: conn.close()` for lifecycle management, and handle transaction semantics separately if writes are introduced.
- **Important contract/correctness:** no matching rows currently produce `0` because `sum([]) == 0`; confirm whether that is the intended business contract. Also clarify accepted customer-ID types, `NULL` amounts (which can make summation fail), invalid database paths, and whether rounding is part of the business rule.
- **Important tests:** cover matching rows, no rows, numeric values, injection-shaped IDs, errors, resource cleanup, and expected rounding.
- **Optional maintainability:** name the query or document units once behavior is protected. Do not make style the only review finding.

A safer core query is:

```python
query = "SELECT amount FROM ledger WHERE customer_id = ?"
rows = conn.execute(query, (customer_id,)).fetchall()
```

Parameter binding prevents values from being interpreted as SQL syntax. A full fix still needs a defined type/empty-result contract and connection lifecycle.

#### C02

1. “I’m concerned this branch may not match the intended behavior. Could you add a focused test for the failing case and link the requirement or reproduction? That will make the expected result verifiable.”
2. “Could you explain which requirement calls for this approach? I wonder whether the existing helper covers the same behavior; if not, could you point out the difference so we can compare the trade-offs?”
3. “The tests do not yet show which edge case this change is intended to protect. Could you add a regression test for the reported failure and relevant boundary cases, with the expected behavior documented?”

Good answers are specific and respectful while retaining the substance of the concern.

#### C03

```markdown
## Summary
What problem does this solve, and why now?

## Change
What changed? Link related issue(s):

## Validation
- [ ] Focused tests added/updated
- [ ] Relevant test suite run (commands/results below)
- [ ] Lint/type/docs checks run as required by the project

Commands and results:

## Compatibility and data impact
API/config/schema/migration impact, supported Python versions, and privacy implications:

## Risk and rollback
Potential failure modes, monitoring, and rollback/revert plan:

## Documentation and release notes
- [ ] Docs updated if needed
- [ ] Changelog/release fragment added if required by this project

## Checklist
- [ ] Diff is focused and self-reviewed
- [ ] Project contribution instructions followed
```

The template should be adapted to repository policy and change type. Screenshots are optional only when they provide value, such as a UI/documentation rendering change.

A compact `CONTRIBUTING.md` review section could define severity labels such as **blocking** (correctness/security/data loss), **important** (material maintainability, compatibility, or test gap), and **optional** (non-blocking suggestion); request focused, logically grouped PRs; state a realistic review-response target that accounts for volunteer capacity; require authors to report checks actually run; and direct unresolved architecture disagreements to an issue/design discussion. A one-page feedback guide should ask reviewers to cite code/evidence, explain impact, make a concrete request or ask a genuine question, distinguish requirements from preferences, and critique the change rather than the author. Authors should acknowledge feedback, clarify disagreements with evidence, update tests/code, and close threads once resolved. Escalation should follow the project's code of conduct and governance, not public shaming or arbitrary deadlines.

#### C04

Sample response: “Thanks for the review. I’ll add a regression test for empty input and run the focused suite. I’ll also check the existing helper and project conventions. I was considering the abstraction because the two callers currently need different policies; I’ll show that difference in the issue/PR and am happy to use the simpler helper if it covers the intended extension point.” Then make the test change, rerun checks, and resolve the thread when addressed. If conventions are established, follow them unless there is evidence for changing project direction; take larger design questions to an issue/discussion rather than prolonging a comment argument.

#### C05

1. Save the CI logs and reproduce the Windows job locally or in a matching environment. Replace hard-coded POSIX path expectations with platform-neutral `pathlib` or compare path semantics appropriately.
2. Reproduce Python 3.13's warning-as-error failure and inspect the warning location. Fix deprecated usage or establish the project's supported compatibility policy; do not blanket-disable warnings without understanding them.
3. Read workflow configuration and dependency versions; run the exact commands used by CI.
4. Add or adjust tests to cover platform/version behavior, then rerun the relevant matrix.

CI may be wrong, but the log provides concrete evidence of portability and version issues that should be investigated first.

#### C06

Agree on the problem the abstraction is intended to solve, number and likely stability of implementations, extension points, and maintenance cost. Compare a function parameter with a plugin design against those requirements. Move the decision to an issue/design note if it affects architecture. Split formatter noise from behavior changes and reduce the PR to a reviewable size. If the maintainer chooses a simpler pattern consistent with the project, implement it unless there is a strong, evidence-based reason to revisit the decision.

#### C07

Prioritized checks: (1) verify need and existing dependencies/features; (2) inspect license, maintenance health, release cadence, vulnerability history and transitive dependencies; (3) check supported Python/platform versions and package-size/startup impact; (4) test malformed/hostile CSV inputs, huge files, encoding, memory and CPU limits; (5) confirm uploads and parsed values do not leak sensitive data into logs or telemetry; (6) update lock/metadata/docs/changelog per policy; (7) validate in CI and record provenance. Passing unit tests alone does not settle supply-chain or operational risk.

### Phase D answers

#### D01

Git's `bisect run` convention is: exit `0` means good; exits `1`–`124` and `126`–`127` mean bad; `125` skips a revision that cannot be tested; exits above `127` abort the run. A wrapper must distinguish a demonstrated regression assertion failure from test collection, dependency, interpreter, and infrastructure failures. Use `125` when this particular revision genuinely cannot be evaluated (for example, a required interpreter is unavailable only for that revision). If the runner crashes because of a transient or shared infrastructure problem, stop/abort and repair or retry the harness; do not mark the revision bad, and do not skip many revisions for a problem unrelated to their contents.

For the flaky test, predeclare a repeat rule rather than deciding after seeing the outcome. For example, run the isolated test five times: classify as bad only if at least four runs fail, good only if at most one fails, and treat two or three failures as inconclusive (`125`) pending further investigation. Verify that each run actually executed the target test; collection/setup failures are not product failures. Repeated runs reduce noise but do not eliminate it, so record each result and confirm that the chosen rule is suitable for the test's known flakiness.

#### D02

1. `git log -S'retry_count' --oneline -- path/to/file.py` — changes in the number of occurrences of the string.
2. `git log -G'timeout[[:space:]]*=' --oneline -- path/to/file.py` — diffs with added/removed lines matching the regex (adjust regex and path to the language).
3. `git log -L :normalize_rows:path/to/file.py` — history of a function/line range when supported by the current Git version and file type.
4. `git bisect start`, mark bad/good endpoints, and run a deterministic regression test or wrapper.
5. `git blame --ignore-revs-file .git-blame-ignore-revs -L 10,30 -- path/to/file.py` — line attribution for lines 10–30 while ignoring listed commits. Replace the example range and path with the target lines and file; confirm the ignore file is supported and hashes are verified.

#### D03 — Find the commit, Scenario 1

Illustrative command sequence (the revision labels are conceptual):

```bash
KNOWN_BAD_REVISION='replace-with-real-bad-ref'
KNOWN_GOOD_REVISION='replace-with-real-good-ref'
git bisect start
git bisect bad "$KNOWN_BAD_REVISION"
git bisect good "$KNOWN_GOOD_REVISION"
git bisect run ./scripts/bisect-test.sh
git bisect log
git bisect reset
```

Replace both variable values with refs that exist in the practice repository. The wrapper must return `0` only when the regression test passes, a bad status only when the target assertion is demonstrably failing, and `125` when that specific revision cannot be tested. A pytest process exit code alone is not always enough: collection errors, missing dependencies, and runner failures must not be misclassified as product regressions. For pytest, exit `1` can represent test failures, while `2`–`5` indicate interruption, internal error, usage error, or no tests collected; inspect the actual result and map setup failures to skip or abort as appropriate. Implement and test the wrapper first. Record the candidate SHA, output, and `git show "$CANDIDATE_SHA"` after setting `CANDIDATE_SHA` to the real hash, plus parent/merge context, relevant tests, and linked issue/PR. Confirm the finding by checking the good parent and bad commit if feasible. Do not assume the commit message establishes intent.

#### D04 — Find the commit, Scenario 2

Because the question is about a quoted dictionary key, start with `git log -S'"retry_count"' --oneline -- path/to/file.py`; this searches for commits where the occurrence count of that exact quoted string changes. `-S` can miss semantically related changes that do not alter that count. If no result, broaden to `git log -G'retry_count' -p -- path/to/file.py`, inspect the serialization path, search tests and history for the output key, and follow the relevant PR/issue. The file path and exact string should be adjusted to the actual repository.

#### D05 — Find the commit, Scenario 3

Use `git log -L :normalize_rows:ledger/normalize.py` for function history where supported; inspect `git log --follow --oneline -- ledger/normalize.py` and the old path's history. `--follow` follows renames for a single path but has limitations. Use `git show COMMIT_SHA` (replace with the actual hash) and compare tests around empty input across revisions. To infer intent, look for linked PR/issue, design notes, commit message and tests. If rationale is not recorded, say that; code diffs alone do not establish intent with certainty.

#### D06 — Find the commit, Scenario 4

First verify the full hash and inspect the diff to establish that `f00ba42` is genuinely formatting-only. Add the verified full hash to `.git-blame-ignore-revs`, then run:

```bash
FORMAT_COMMIT='replace-with-verified-full-hash'
git blame --ignore-revs-file .git-blame-ignore-revs -L 10,30 -- path/to/file.py
git show --format=fuller "$FORMAT_COMMIT"
git log --oneline -- path/to/file.py
```

Replace the variable value with the actual verified object ID before running the commands. This changes blame presentation, not repository history. Do not amend/rebase/force-push a shared branch to alter the historical formatter commit. A real report should not copy the illustrative hash unless it exists in that repository.

#### D07

Workflow: read README, contribution guide, code of conduct, security policy, license, issue/PR templates and development instructions; search for duplicates; reproduce with exact package/Python/OS versions and minimal input; ask maintainers before a large design change; fork/clone, add upstream remote, create a topic branch; add a regression test and minimal fix; run the documented tests/lint/type/docs/changelog checks; write a clear PR description; respond to review and update CI. If a vulnerability may be involved, use the private channel in `SECURITY.md` or the project's designated security contact, not a public issue with exploit details.

Minimal bug report outline: title; package/version and Python/OS; exact input and short code; expected versus actual result; full traceback; smallest reproduction; whether it reproduces on a supported version; relevant logs with secrets removed.

A three-contribution progression can be: (1) a documentation/test improvement with the project's required checks; (2) a triage report for a reproducible bug, including version details, minimal reproduction, and history evidence where useful; and (3) a focused bug fix with a regression test, required changelog/docs, and CI results. Keep a link or private practice artifact, commands/results actually run, review rounds, feedback response, and retrospective for each. Mark each outcome as prepared, submitted, accepted/merged, or declined/pending based on evidence; a private-mirror rehearsal is not upstream acceptance.

#### D08

Record `sys.version`, `sys.implementation`, `heapq.__file__`, and `sys.modules` state. Read the matching `Lib/heapq.py` dispatch logic and `_heapq` implementation in the exact CPython version, plus tests. A `.pyi` stub describes a typing interface, not runtime execution. Use a small set of inputs and compare outputs/edge cases. Evidence should include runtime paths, dispatch code, test coverage, and observed output. Merely seeing `_heapq` in `sys.modules` does not prove every function call uses a C implementation.

#### D09

Inspect the exact CPython tag's `Objects/listobject.c`, relevant declarations under `Include/`, allocation/resize helpers, comments, and tests. Use a controlled script that appends many elements and records observable size/timing, but note that `sys.getsizeof` alone does not reveal capacity exactly and is allocator/version dependent. A debug build or instrumentation may be needed to observe internal capacity reliably. The language guarantees list behavior, not a fixed growth factor or precise allocation schedule; report only the implementation detail verified in that source version.

#### D10

A defensible ranking depends on project need: (c) a reproducible issue plus regression test is often high-value and testable; (a) a clear typo/documentation gap is a low-risk first contribution and may be best for a newcomer; (d) a multi-dependency upgrade plus bug fix is broad and hard to review, so split it and discuss first; (b) public API redesign without discussion is usually the riskiest and should begin with an issue/design proposal. Score each by user impact, scope, reproducibility, maintainers' priorities, and review cost—not by a universal fixed ranking.

#### D11

A strong capstone has milestones and evidence: (1) `ONBOARDING.md` completed within a four-hour time box, with run commands, architecture/dependency diagram, main flows, glossary, and exactly three unresolved questions; (2) characterization/golden-master tests for three risky flows, with at least 85% characterized-area coverage and mutation score reported where tools are available; (3) debt report with smell evidence and hotspot analysis using Git history and complexity data; (4) at least 30 small behavior-preserving refactor commits delivering layered structure, value objects, a dispatch table, injected dependencies, type hints, and `import-linter` contracts; (5) a roughly 300-commit disposable history with a flaky-ish test and formatting-only commit, plus a reproducible `git bisect run`, `-S`/`-L` and blame evidence, `.git-blame-ignore-revs`, fix, and postmortem; (6) a mock PR review, response evidence, and committed review checklist/template; (7) one upstream contribution or a clearly labeled private-mirror rehearsal. Acceptance also requires at least 40% complexity reduction across the top-five hotspot functions with behavior preserved by golden tests, green CI, and a reproducible bisect. The completion report must distinguish submitted, accepted, and merely prepared contributions.

#### D12

A complete plan has three non-substitutable reports, each 2–4 pages and pinned to a real tag/commit: (1) a pure-Python stdlib path such as `Lib/dataclasses.py` or the pure-Python fallback path in `Lib/heapq.py`; (2) a C-level CPython path such as `Objects/listobject.c` or `Objects/dictobject.c`, including relevant declarations/tests; and (3) a third-party vertical slice traced from public API through internal layers to tests. Each report should state a concrete question, identify source and design/history evidence, include a diagram, run a bounded experiment (benchmark, debugger, controlled behavior test, or modified build as appropriate), and distinguish observation from inference. Include one design decision to copy and one to avoid, with rationale. Time-box each investigation and maintain unresolved questions rather than reading the repository linearly. For AI-assisted work, verify function names, source locations, claims, and benchmark procedures directly against the pinned source/tests; report measured results only if actually run. If a full CPython build or debugger session is unavailable, state the limitation and use a narrower reproducible experiment without pretending the unavailable validation occurred.

## Coverage Map

| Lesson | Questions |
|---|---|
| 01 — Reading Unfamiliar Codebases | A01–A03 |
| 02 — Characterization Tests for Legacy Code | A03–A06, B04, B06–B07, B10, C01, D11 |
| 03 — Refactoring Catalogue | B01, B04, B06–B07, B09–B10, B12 |
| 04 — Code Smells and Technical Debt | B02–B05, B08, B11–B12, D11 |
| 05 — Writing and Receiving Code Review | B09, B12, C01–C07, D11 |
| 06 — Git Blame, Bisect and History Archaeology | B11, D01–D06, D11 |
| 07 — Contributing to Open-Source Python Projects | C04–C05, D07, D10–D11 |
| 08 — Reading CPython and Library Source | D08–D09, D11–D12 |

## Self-assessment rubric

Score each dimension from 0 to 3:

- **0 — Missing:** no answer or unsupported assertions.
- **1 — Developing:** recognizes the topic but misses important evidence or risk.
- **2 — Competent:** provides a correct, reasoned answer with appropriate tests/commands and caveats.
- **3 — Production-aware:** adds reproducibility, version/context boundaries, rollback or compatibility concerns, and explains why plausible alternatives are less safe.

Dimensions: repository orientation; characterization/testing; refactoring safety; smell/hotspot evidence; review quality; Git investigation; open-source workflow; source-reading evidence. Revisit any dimension below 2 before completing the Module 1.23 mini-project.
