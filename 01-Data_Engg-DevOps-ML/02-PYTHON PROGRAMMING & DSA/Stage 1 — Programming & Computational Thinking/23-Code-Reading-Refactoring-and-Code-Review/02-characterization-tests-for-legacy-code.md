# Characterization Tests for Legacy Code

**Module:** Stage 1 — Programming & Computational Thinking, Module 1.23: Code Reading, Refactoring and Code Review  
**Lesson:** 02 of 08  
**Target environment:** Python 3.12+, `pytest`, Git; optional `hypothesis`, `coverage`, `mutmut`/`cosmic-ray`, `freezegun`  
**Estimated study time:** 6–9 hours, plus the capstone

> **Core rule:** A characterization test records what a system does now. It does not declare that behaviour correct. Preserve observation and decision-making as separate activities.

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

1. Explain the difference between characterization, regression, and specification tests.
2. Apply the six-step workflow to observe legacy behaviour, including suspicious behaviour, without silently fixing it.
3. Choose meaningful inputs across normal, boundary, empty, `None`, malformed, large, and production-like cases.
4. Build deterministic `pytest` tests and golden-master tests for structured and substantial outputs.
5. Create test seams and isolate filesystems, clocks, randomness, environment variables, databases, and network calls.
6. Use tests, coverage, branch exploration, and mutation testing to assess how well behaviour is characterized.
7. Compare legacy and replacement implementations using differential and property-based tests.
8. Characterize data pipelines and ML/AI systems, including their output contracts, resource behaviour, and operational risks.
9. Apply characterization tests to gradual migrations and difficult-to-test legacy code.
10. Complete the capstone: characterize a roughly 200-line function, create a golden master for 20 sample inputs, protect each refactoring step with green tests, and record at least three discovered bugs separately.

### Prerequisites

You should be comfortable with Python functions, collections, exceptions, modules/imports, file I/O, environment variables, Git basics, and basic `pytest` fixtures/assertions. Review these Stage 1 topics if needed:

- Module 1.6: modules, packages, dependencies, project configuration, and quality tooling.
- Module 1.7: testing, fixtures, debugging, tracebacks, and minimal reproductions.
- Module 1.8: separating side effects from domain logic and dependency boundaries.
- Module 1.16: advanced testing, snapshot testing, mutation testing, and flaky tests.
- Module 1.17: profiling, performance, and memory behaviour.
- Module 1.20: refactoring and anti-patterns.
- Stage 0 Git basics and Stage 2 data-quality concepts when working on pipelines.

## 2. Why characterization matters in production engineering

Legacy code is not necessarily old code. It is code whose behaviour is insufficiently specified or protected by tests. It may be business-critical, poorly documented, tightly coupled to infrastructure, or simply unfamiliar to the current team.

Before changing it, an engineer needs evidence about its current observable behaviour. A function may have undocumented rounding rules; a CSV report may contain columns in a particular order; an ETL job may treat blank strings differently from null values; a retry loop may emit duplicate records after a partial failure. A seemingly harmless cleanup can change any of these contracts.

Characterization tests create a safety net around the behaviour that exists today. They let the team distinguish three separate questions:

1. **Observation:** What does the current system do for this input and environment?
2. **Decision:** Is that behaviour intended, acceptable, or a bug?
3. **Change:** If behaviour must change, how do we make the change explicitly and safely?

Do not collapse these questions into one test-writing step. If a test captures a suspicious negative discount, a surprising exception, or an odd output column, record it as an observation. Do not silently replace it with the result you think the code ought to produce.

### 2.1 Characterization vs regression vs specification tests

| Test type | Primary question | Expected result comes from | Typical use |
|---|---|---|---|
| Characterization | What does the current implementation do? | Observed current behaviour | Establishing a baseline before a refactor |
| Regression | Did a previously fixed failure return? | A known defect/fix or previously established contract | Protecting a bug fix from recurrence |
| Specification | What should the system do? | Requirements, domain rules, API contract, or an explicit product decision | Verifying intended behaviour |

A characterization test can later serve as a regression test once the team consciously adopts its expectation as a contract. That transition should be explicit. A passing characterization test only shows that the current implementation still matches the recorded observation for the tested cases; it does not prove correctness, completeness, security, or fitness for every input.

### 2.2 A small example

Suppose an unfamiliar module contains:

```python
# legacy.py

def discount(amount: float, tier: str | None) -> float:
    if tier == "gold":
        return amount * 0.85
    if tier == "silver":
        return amount * 0.95
    return amount
```

The observed behaviour includes the following:

```python
# test_legacy.py
import pytest
import legacy

pytestmark = pytest.mark.characterization


def test_discount_current_behavior_for_representative_inputs() -> None:
    assert legacy.discount(100.0, "gold") == pytest.approx(85.0)
    assert legacy.discount(100.0, "silver") == pytest.approx(95.0)
    assert legacy.discount(100.0, "") == pytest.approx(100.0)
    assert legacy.discount(-5.0, "gold") == pytest.approx(-4.25)
    assert legacy.discount(100.0, None) == pytest.approx(100.0)
```

The negative amount result may be suspicious. The test records it rather than asserting that negative amounts are a valid business case. Create a ticket or known-bug note and decide separately whether the behaviour should change.

`pytest.approx` uses a tolerance, so it can hide sufficiently small numerical changes; use it only when that tolerance is acceptable for the contract. If exact current floating-point output is the behaviour being recorded, assert the exact observed value and runtime context instead. For real currency, binary floating-point may be inappropriate; use the existing domain representation during characterization, and do not replace it with `Decimal` in the same change unless the migration explicitly intends a behaviour change.

## 3. The six-step characterization workflow

Use this repeatable sequence. It is intentionally observation-first.

1. **Put the code in a test harness.** Call the legacy entry point from a test with the smallest safe input. If the function is inaccessible, add a narrow wrapper or choose a CLI/API boundary.
2. **Write an assertion with an obviously wrong expectation.** For example, assert that the result is `"definitely-not-the-output"`. Do not use a destructive or expensive input just to force a failure.
3. **Run the test and observe the actual result.** Inspect the return value, exception type/message, output file, logs, side effects, or exit code. Capture evidence, not guesses.
4. **Replace the deliberately wrong expectation with the observed result.** Make the assertion precise enough to detect meaningful change, but not so brittle that irrelevant details dominate.
5. **Repeat across representative and edge inputs.** Include normal cases, boundaries, empty values, `None`, malformed data, large inputs, and environment-specific cases that matter to the contract.
6. **Record suspicious behaviour separately.** Add a known-bug issue or a clearly justified strict expected-failure test. Do not fix the bug in the characterization change.

A deliberate wrong assertion is a temporary discovery technique, not a test to commit. Avoid exposing secrets or personal data in assertion diffs, snapshots, or CI logs.

### 3.1 Input selection matrix

| Input class | Questions to ask | Example |
|---|---|---|
| Typical | What does a normal production-like record do? | A valid order with two items |
| Boundary | What happens at minimum/maximum values? | Zero amount, maximum allowed batch size |
| Empty | Does empty mean no work, default, or invalid? | `[]`, `""`, empty CSV |
| Null-like | Is `None` distinct from missing or blank? | `tier=None`, absent JSON key |
| Malformed | Is it rejected, coerced, skipped, or partially processed? | Invalid date or bad numeric field |
| Large | Does scaling alter behaviour or resource use? | 100,000 rows, long text |
| Special | Are locale, timezone, encoding, precision, or ordering relevant? | DST boundary, comma decimal separator |
| Failure | What is left behind after a partial failure? | Sink write fails after batch 2 |
| Repeat | Is running twice safe? | Retry the same partition or event |

Prefer anonymized production-like examples where permitted. Preserve the relevant shape and edge conditions while removing sensitive fields. A handful of hand-picked examples is useful, but not a substitute for broader generated inputs when the input space is large.

### 3.2 Determinism is a requirement for useful evidence

A test should control inputs and environmental dependencies wherever possible. Keep small fixtures under `tests/fixtures/`; use fixed random seeds when the code accepts a random generator; freeze or inject the clock; use temporary directories; avoid live services in ordinary unit tests. If the existing system is inherently nondeterministic, define which dimensions are contractual and normalize only the irrelevant variation.

Example fixed-seed test:

```python
import random


def test_legacy_sampling_is_repeatable_for_a_fixed_seed() -> None:
    rng = random.Random(2026)
    first = [rng.random() for _ in range(3)]

    rng = random.Random(2026)
    second = [rng.random() for _ in range(3)]

    assert first == second
```

This proves the local pseudorandom sequence is repeatable for that seed in the tested runtime. It does **not** prove a legacy function uses the supplied generator; pass the generator into that function or patch its random source to characterize its actual behaviour.

## 4. A worked `pytest` example

Assume a legacy CSV importer converts rows to normalized records. The rules are not documented, so we observe the current results before deciding what the rules should be.

```python
# legacy_import.py
from __future__ import annotations

import csv
from pathlib import Path


def load_orders(path: str | Path) -> list[dict[str, str]]:
    """Return current importer output; behavior is not yet specified."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        result: list[dict[str, str]] = []
        for row in rows:
            # Existing behavior: trim customer name, preserve order ID text.
            result.append({
                "order_id": row["order_id"],
                "customer": row["customer"].strip(),
                "amount": row["amount"],
            })
        return result
```

Create a fixture `tests/fixtures/orders.csv`:

```csv
order_id,customer,amount
001,  Ada Lovelace  ,12.50
002,,0
```

Then characterize it:

```python
# tests/test_legacy_import.py
from pathlib import Path

import pytest

from legacy_import import load_orders

FIXTURE = Path(__file__).parent / "fixtures" / "orders.csv"
pytestmark = pytest.mark.characterization


def test_importer_current_output_shape_and_values() -> None:
    assert load_orders(FIXTURE) == [
        {"order_id": "001", "customer": "Ada Lovelace", "amount": "12.50"},
        {"order_id": "002", "customer": "", "amount": "0"},
    ]
```

Register the marker in `pyproject.toml` to avoid an unknown-marker warning:

```toml
[tool.pytest.ini_options]
markers = [
  "characterization: records observed legacy behavior; not a correctness claim",
]
```

Run from the repository root:

```bash
python -m pytest -q tests/test_legacy_import.py
```

Expected outcome: one passing test if the source and fixture match the examples. This test captures the preservation of leading zeroes in `order_id`, whitespace trimming for `customer`, and the current string representation of `amount`. It does not prove these are desirable business rules, that malformed CSV is handled safely, or that the importer scales to large files.

### 4.1 Exceptions and side effects are behaviour too

A legacy function's observable contract can include exception type, exit status, output files, database writes, logging, or network calls. Capture these only when they matter to callers. Avoid asserting unstable full tracebacks or timestamps unless they are part of the supported interface.

```python
import pytest


def test_missing_file_currently_raises_file_not_found(tmp_path) -> None:
    # This test belongs in the same test module as the earlier importer test,
    # or import load_orders from the application module here.
    missing = tmp_path / "does-not-exist.csv"
    with pytest.raises(FileNotFoundError):
        load_orders(missing)
```

This records the exception class. If callers depend on a particular message, characterize that too; otherwise exact message assertions can be brittle across operating systems and Python versions.

## 5. Golden-master and approval testing

A golden master is a reviewed baseline output captured from the existing implementation. It is useful when outputs are too large or structured to assert field by field: CSV exports, JSON payloads, HTML reports, rendered documents, SQL plans, or serialized data files.

### Workflow

1. Select representative input fixtures and run the current implementation in a controlled environment.
2. Store outputs as reviewed test artifacts under version control when size and sensitivity permit.
3. Normalize only known irrelevant volatility, such as generated timestamps or request IDs.
4. Compare the current output to the baseline in tests.
5. Review every baseline update as a contract change; never blindly regenerate snapshots just to make tests pass.

Golden masters are strong at detecting change, but weak at explaining whether the change is correct. They can preserve bugs, encode environment-specific details, or become noise if normalization is too broad.

### 5.1 Normalize volatile fields

Suppose a JSON report includes a generated timestamp and request ID. Normalize those fields while retaining meaningful content:

```python
# tests/helpers.py
from copy import deepcopy
from typing import Any


def normalize_report(report: dict[str, Any]) -> dict[str, Any]:
    """Remove fields known to vary and canonicalize unordered collections."""
    normalized = deepcopy(report)
    normalized.pop("generated_at", None)
    normalized.pop("request_id", None)
    if isinstance(normalized.get("warnings"), list):
        normalized["warnings"] = sorted(normalized["warnings"])
    return normalized
```

```python
# tests/test_report_snapshot.py
import json
from pathlib import Path

from tests.helpers import normalize_report


def test_report_matches_reviewed_golden_master(report_factory) -> None:
    actual = normalize_report(report_factory())
    expected = json.loads(
        (Path(__file__).parent / "golden" / "report.json").read_text(encoding="utf-8")
    )
    assert actual == expected
```

`report_factory` represents the existing system's report-generation call and must be supplied by your project or fixture. This is an illustrative integration point, not a standalone runnable test until that fixture and baseline file exist. For `from tests.helpers import normalize_report` to resolve reliably, make `tests/` a local package by adding an empty `tests/__init__.py`; alternatively, place the helper in your application package and import it from there. The helper intentionally removes only two named fields and sorts warnings **only under the explicit assumption that warning order is not contractual**. Add a test proving that a changed status or record amount still differs after normalization, for example:

```python
def test_normalization_preserves_meaningful_report_changes():
    baseline = {
        "generated_at": "2026-01-01T00:00:00Z",
        "request_id": "req-1",
        "status": "ok",
        "records": [{"account": "A", "amount": 10}],
    }
    volatile_only = {
        **baseline,
        "generated_at": "2026-01-02T00:00:00Z",
        "request_id": "req-2",
    }
    assert normalize_report(baseline) == normalize_report(volatile_only)
    assert normalize_report(baseline) != normalize_report({**baseline, "status": "error"})
    assert normalize_report(baseline) != normalize_report(
        {**baseline, "records": [{"account": "A", "amount": 11}]}
    )
```

Do not sort rows or remove IDs if order or identity is meaningful. If a timestamp affects partition selection or business logic, it is not irrelevant volatility.

For text output, normalize line endings when the platform difference is irrelevant. For floating-point values, use domain-specific tolerances (`pytest.approx`) rather than rounding everything indiscriminately. For CSV, parse into rows and compare semantic fields when quoting/line-ending formatting is not the contract; compare bytes when exact serialization is the contract. For Parquet, compare schema, row values, null counts, and selected statistics rather than binary file bytes, which may vary with metadata or writer versions.

### 5.2 Snapshot review policy

- Keep snapshots small, readable, and tied to explicit fixtures.
- Include the generation command and runtime/dependency version when output depends on them.
- Review the diff before updating a baseline.
- Never commit secrets, credentials, production PII, or unapproved datasets.
- Split volatile metadata from semantic output where possible.
- Use snapshots to complement focused assertions, not replace them.

## 6. Seams and isolating dependencies

A **seam** is a place where you can alter or replace a dependency's behaviour without rewriting the whole system. Legacy code often hard-wires the clock, filesystem, network client, database, random generator, or environment into a function. Characterization becomes safer when these dependencies can be controlled.

### 6.1 Common seam techniques

1. **Parameterize dependencies:** accept a path, clock, client, or random generator as a parameter.
2. **Extract and override:** move an external call behind a small method or function.
3. **Wrap external APIs:** create a narrow adapter that can be faked in tests.
4. **Monkeypatch module attributes:** replace the symbol used by the legacy module, not necessarily the original symbol in its defining library.
5. **Use temporary resources:** `tmp_path`, temporary environment variables, in-memory databases, and local fake services.
6. **Subprocess isolation:** use a separate process for code whose import or global state cannot be reset safely.

Prefer a small seam that preserves current behaviour. Avoid large redesigns as part of the characterization step.

### 6.2 Filesystem, environment, and clock

```python
from pathlib import Path


def read_config(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")
```

```python

def test_read_config_uses_supplied_path(tmp_path) -> None:
    # Import read_config from the module containing the preceding example.
    config = tmp_path / "settings.toml"
    config.write_text("mode = 'test'\n", encoding="utf-8")
    assert read_config(config) == "mode = 'test'\n"
```

Use `monkeypatch.setenv("APP_MODE", "test")` and `monkeypatch.delenv("APP_MODE", raising=False)` to control environment variables. The `monkeypatch` fixture restores changes after the test.

For clocks, the cleanest seam is often an injected callable:

```python
from datetime import datetime, timezone
from collections.abc import Callable


def created_at(now: Callable[[], datetime] | None = None) -> str:
    clock = now if now is not None else (lambda: datetime.now(timezone.utc))
    return clock().isoformat()
```

```python
from datetime import datetime, timezone


def test_created_at_with_fixed_clock() -> None:
    fixed = datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)
    assert created_at(lambda: fixed) == "2026-01-02T03:04:00+00:00"
```

If the legacy code imports `datetime` directly, patch the name where the module under test looks it up. A library such as `freezegun` can help with broader clock usage, but it adds a dependency and may not control external processes or remote services.

### 6.3 Network and database isolation

- Replace an HTTP client with a fake or use a local test server. Do not let ordinary unit tests make real production requests.
- Use in-memory SQLite only if its SQL semantics and transaction behaviour are sufficiently representative. SQLite is not a drop-in simulation of PostgreSQL, MySQL, or a cloud warehouse.
- Use disposable database schemas/containers for integration tests that depend on dialect-specific behaviour.
- Ensure fake clients reproduce the failure modes relevant to the test: timeouts, rate limits, partial responses, and retries.

### 6.4 Randomness and nondeterminism

Inject `random.Random(seed)` or a NumPy generator when possible. Seed control does not guarantee identical results across library versions, devices, parallel execution, or nondeterministic kernels. Record library/runtime versions when they affect reproducibility.

## 7. Characterize from the outside in

Start at the public boundary when possible: CLI command, HTTP endpoint, job runner, or exported function. Boundary tests show what a real caller experiences and often capture wiring, configuration, serialization, and error handling that unit tests miss. Then add focused internal tests for risky logic as you refactor.

For a CLI, capture:

- arguments and environment;
- stdout and stderr separately;
- exit code;
- files or other side effects;
- behaviour on invalid input.

For an API, capture status code, headers that are contractual, response schema, error format, and meaningful side effects. Avoid hard-coding unstable framework tracebacks or incidental header ordering.

Outside-in tests can be slower and harder to diagnose than unit tests. Keep a layered suite: a small set of high-value boundary tests plus faster tests for complex internal behaviour.

## 8. Coverage-guided exploration and mutation testing

Coverage tells you which code ran; it does not tell you whether the assertions would detect a wrong result.

Run tests with coverage:

```bash
python -m pip install pytest coverage
python -m coverage run --branch -m pytest
python -m coverage report -m
python -m coverage html
```

Open `htmlcov/index.html` locally to inspect uncovered lines and branches. Coverage commands may need to be adapted to the repository's package manager and test selection. Do not install packages into a shared production environment.

Use uncovered branches to ask questions: What input selects this branch? Is it reachable? Is it relevant to the behaviour being changed? Add tests for meaningful behaviours rather than chasing 100% mechanically. Branch coverage is useful for conditionals whose alternatives have different effects.

**Mutation testing** changes code in small ways (for example, `>` to `>=`, or removing a condition) and checks whether tests fail. A surviving mutant can reveal weak assertions or an untested contract. Some mutants are equivalent or unreachable, so mutation score needs interpretation.

Example workflow with a compatible mutation tool such as `mutmut`:

```bash
python -m pip install mutmut
mutmut run
mutmut results
```

Exact CLI options can differ by `mutmut` version; consult the installed version's help and project configuration before running it. Run mutation testing on a focused module first because it can be expensive. A killed mutant means a test detected that mutation, not that the entire behaviour is correct.

## 9. Property-based and differential testing

**Differential testing** runs the same input through the legacy and replacement implementations, then compares their observable outputs. **Property-based testing** generates many inputs from defined strategies and checks a property. Hypothesis combines well with differential testing when the old implementation can serve as an oracle for behaviour preservation.

Install the optional dependency in a development environment:

```bash
python -m pip install hypothesis pytest
```

Example:

```python
# test_discount_differential.py
from hypothesis import given, strategies as st

from legacy import discount as old_discount
from replacement import discount as new_discount


@given(
    amount=st.integers(min_value=-1_000, max_value=10_000),
    tier=st.sampled_from(["gold", "silver", "", None]),
)
def test_replacement_matches_legacy(amount: int, tier: str | None) -> None:
    assert new_discount(amount, tier) == old_discount(amount, tier)
```

This example assumes both functions accept those values and return directly comparable outputs. If the legacy function is known to behave differently for a documented bug, do not hide the mismatch with broad exceptions or arbitrary filters. Classify it: intended correction, preserved compatibility, or unresolved issue. Keep the comparison rule explicit.

Hypothesis shrinks failures to a smaller counterexample, which is valuable for debugging. It does not automatically select domain-representative inputs; strategies should reflect real types, boundaries, invariants, and constraints. For external effects, use a fake or deterministic seam so generated examples do not trigger real network/database operations.

### 9.1 Floating-point, ordering, and normalization

- Use `pytest.approx(expected, rel=..., abs=...)` when small floating-point differences are acceptable under a justified tolerance.
- Do not compare unordered collections as ordered lists unless order is contractual. Compare sets or sort by a stable key where appropriate.
- Do not normalize away duplicate rows, nulls, schema differences, or meaningful ordering merely to make a test green.
- Avoid broad rounding that hides numerical drift. Set tolerances based on business or scientific requirements.
- For parallel outputs, separate nondeterministic scheduling from semantic results. If order matters, test it; if not, canonicalize deterministically.
- A flaky characterization test is weak evidence. Identify the source of nondeterminism, control it, or explicitly test a range/distribution if randomness is the intended behaviour.

## 10. Known bugs and expected failures

Do not mix bug fixes into a commit whose purpose is to characterize current behaviour. Record suspicious cases in an issue or known-bugs file with:

- input and environment;
- observed output/exception;
- why it appears suspicious;
- evidence and impact;
- owner or follow-up issue;
- whether compatibility requires preserving it temporarily.

`pytest.mark.xfail(strict=True)` can be appropriate when a test expresses a known, reproducible defect and the team wants CI to fail if the defect unexpectedly starts passing (which forces review/removal of the marker). It should not be used as a dumping ground for failing characterization tests.

```python
import pytest


@pytest.mark.xfail(
    strict=True,
    reason="BUG-123: negative amounts are accepted; tracked separately from characterization",
)
def test_negative_amount_is_rejected_after_bug_fix() -> None:
    with pytest.raises(ValueError, match="amount"):
        discount(-5, "gold")
```

This example assumes the approved desired contract is to reject a negative amount with `ValueError` mentioning `amount`; confirm that contract with the domain owner and adapt the exception if the real specification differs. This is an **expected specification after the planned fix**, not a pure characterization test. Keep that distinction visible in the test name, marker, and issue. While the legacy function returns `-4.25`, the test is expected to fail and be reported as xfailed. If the defect is fixed and the test passes, `strict=True` reports an XPASS failure so the team reviews the marker and removes it.

## 11. Advanced characterization for legacy data pipelines

For ETL and reporting code, a single output equality assertion is rarely enough. Characterize multiple dimensions across representative partitions and failure modes.

### 11.1 What to measure

| Dimension | Example evidence | Why it matters |
|---|---|---|
| Input scope | Source partition/date range, input file hashes | Ensures old and new runs saw equivalent inputs |
| Row counts | Input/output counts, rejected-row counts | Detects dropped or duplicated records |
| Schema | Column names/order, types, nullability | Detects contract drift |
| Values | Key fields, aggregates, row-level comparisons | Detects transformation differences |
| Nulls/duplicates | Null count per column, unique-key violations | Detects data-quality changes |
| Distributions | Min/max, quantiles, category frequencies | Detects broad shifts missed by totals |
| Integrity | Stable checksum over canonicalized rows | Detects changes where full diffs are costly |
| Operational behaviour | Duration, memory, retries, checkpoint state | Detects reliability/resource regressions |

Use deterministic representative partitions, including an ordinary day, a high-volume day, an empty partition, malformed records, late-arriving data, and a replay/backfill case. Hashes are only comparable if canonicalization, encoding, row ordering, null representation, and hash algorithm are consistent.

### 11.2 A small standard-library comparison helper

```python
from collections import Counter
from collections.abc import Iterable, Mapping
from typing import Any


def profile_rows(rows: Iterable[Mapping[str, Any]], key: str) -> dict[str, Any]:
    materialized = list(rows)
    schema = tuple(materialized[0].keys()) if materialized else ()
    missing_key_count = sum(key not in row for row in materialized)
    null_key_count = sum(key in row and row[key] is None for row in materialized)
    # Count duplicates only for present, non-null key values. Null/missing-key
    # policy varies by data contract and should be reported separately.
    non_null_keys = [row[key] for row in materialized if key in row and row[key] is not None]
    return {
        "row_count": len(materialized),
        "schema": schema,
        "missing_key_count": missing_key_count,
        "null_key_count": null_key_count,
        "duplicate_key_count": sum(
            count - 1 for count in Counter(non_null_keys).values() if count > 1
        ),
    }
```

This helper is deliberately small and materializes its iterable, so it is unsuitable for unbounded streams or very large datasets without adaptation. It assumes key values are hashable for `Counter`; adapt it for complex key values. Its schema is taken from the first row and does not validate every row's keys or types. Missing keys, explicit null keys, and duplicate non-null keys are reported separately; some data contracts intentionally treat nulls differently, so adjust the policy explicitly. In production-grade checks, use an explicit schema contract and a streaming/profile approach appropriate to the data volume.

A focused unit test should verify that the profile does not conflate missing keys with explicit nulls:

```python
def test_profile_rows_distinguishes_missing_null_and_duplicate_keys():
    rows = [{"order_id": "A"}, {"order_id": None}, {"order_id": "A"}, {}]
    result = profile_rows(rows, key="order_id")
    assert result["row_count"] == 4
    assert result["missing_key_count"] == 1
    assert result["null_key_count"] == 1
    assert result["duplicate_key_count"] == 1
```

A pipeline characterization test might compare profiles and key-level outputs:

```python
def test_new_pipeline_matches_legacy_for_fixed_partition(sample_partition):
    old_rows = run_legacy(sample_partition)
    new_rows = run_replacement(sample_partition)

    assert profile_rows(new_rows, key="order_id") == profile_rows(old_rows, key="order_id")
    assert sorted(new_rows, key=lambda row: row["order_id"]) == sorted(
        old_rows, key=lambda row: row["order_id"]
    )
```

`sample_partition`, `run_legacy`, and `run_replacement` are project-specific fixtures/functions. If records contain decimals, timestamps, or floating-point aggregates, normalize them according to the actual data contract. The comparison above assumes every output row has a non-null, mutually comparable `order_id`; if that is not guaranteed, validate/reject missing keys explicitly before sorting. For large datasets, compare partitioned digests and targeted samples, but do not rely on a single checksum as the only correctness measure.

### 11.3 Data-pipeline hazards to investigate

- **Idempotency:** Does replaying the same input create duplicates or alter previous results?
- **Checkpointing:** Is checkpoint state committed before or after sink writes? What happens after partial failure?
- **Schema evolution:** What happens when a column is added, removed, renamed, or changes type?
- **Late data and backfills:** Are watermarks, partition boundaries, and correction windows preserved?
- **Data contracts:** Are keys, nullability, units, timezone, ordering, and rejection rules explicit?
- **Lineage and observability:** Can you identify source versions, transformations, output partitions, and rejected records?
- **Privacy:** Do snapshots and diffs avoid leaking PII or secrets?

Shadow runs should write to isolated scratch sinks and must not trigger duplicate customer notifications, payments, or irreversible side effects.

## 12. Globals, import-time effects, and difficult legacy functions

### 12.1 Hard-wired globals and import-time behaviour

Python modules execute top-level statements when imported (subject to the import cache). If importing a module opens files, reads environment variables, starts threads, or connects to a service, tests can become order-dependent or unsafe.

Preferred approach: move effects behind an explicit function or adapter and call it at the runtime boundary. When changing the module is not yet possible:

- patch the symbol where the module under test uses it;
- use `importlib.reload()` only with care, because it re-executes top-level code and does not reset every reference elsewhere;
- use subprocess tests to isolate import-time side effects and `sys.modules` state;
- set environment variables before importing the module;
- avoid importing modules that might perform production writes in a test environment.

Subprocesses are slower but give a cleaner boundary for global state. Tests should use temporary paths and explicitly safe configuration.

### 12.2 Sprout method/class and wrapper techniques

When a huge function is difficult to test, do not begin by rewriting it all.

- **Sprout method/class:** add the new behaviour in a new, testable function or class, then make a narrow call from the legacy function. Existing code remains in place while the new behaviour gains tests.
- **Wrap method/class:** place a thin adapter around the legacy component to create a seam for inputs, outputs, or dependencies.
- **Extract pure logic first:** isolate deterministic transformations from I/O-heavy code. Pure logic is easier to characterize.
- **Scratch refactoring:** experiment on a disposable branch or worktree to understand a safe shape, then discard the experiment and apply small, tested changes to the real branch if necessary.

Example wrapper:

```python
from pathlib import Path
from collections.abc import Callable


def export_orders(path: str | Path, write_text: Callable[[str, str], None]) -> None:
    """Thin seam around a legacy exporter; write_text(path, content) is injectable."""
    content = legacy_render_orders()
    write_text(str(path), content)
```

A test can inject a recorder instead of writing to a real destination. This wrapper is a pattern example; adapt the signature to the actual legacy API and preserve its observable behaviour.

## 13. Performance and resource-behaviour baselines

Characterization may include performance, memory, file handles, database query counts, and network request counts when they are important to safe refactoring. A behaviour-preserving refactor that changes a nightly job from 10 minutes to 3 hours is not operationally neutral.

- Use stable representative inputs and record runtime environment, dataset size, hardware, Python/library versions, and warm/cold conditions.
- Prefer repeated benchmark measurements and report a distribution or median rather than a single wall-clock number.
- Use `time.perf_counter()` for simple elapsed-time measurements; use profilers and `tracemalloc` for diagnosis.
- Use broad thresholds only when CI hardware variability is understood. Strict timing assertions in shared CI can be flaky.
- Record memory peaks, rows/second, request counts, and query counts where those metrics explain production risk.
- Separate correctness assertions from performance tests so a performance threshold does not obscure a semantic mismatch.

Performance baselines are evidence about a particular environment and workload, not universal guarantees. Re-run them after meaningful runtime, dependency, or hardware changes.

## 14. Safe migrations: strangler, shadow, flags, and canaries

A **strangler-fig migration** gradually routes selected behaviour to a replacement while the legacy path remains available. Characterization tests establish a baseline before routing changes.

A safe sequence is:

1. Characterize the old boundary and record representative outputs.
2. Introduce a facade/adapter that can call either implementation.
3. Run the new path against the same inputs in a scratch sink or shadow mode.
4. Compare outputs automatically and report differences without logging sensitive data.
5. Classify mismatches as bugs, intended changes, environmental noise, or unresolved cases.
6. Use a feature flag to route a small, reversible slice when evidence is adequate.
7. Canary the change with operational metrics and rollback criteria.
8. Expand gradually, then remove the old path only after explicit acceptance and rollback windows.

Shadow mode must not repeat irreversible side effects. For example, do not let both paths send real emails or charge a card. Use no-op adapters, isolated databases, or carefully designed read-only execution. Feature flags add operational complexity and require an owner, expiry/removal plan, and monitoring. A canary is not safe without a clear rollback mechanism and alerting.

## 15. Characterizing ML and AI systems

ML behaviour includes more than a function's return value. Characterize the full path relevant to the change: data loading, preprocessing, feature transformations, model/config versions, training, evaluation, and serving.

### 15.1 Useful baselines

- Fixed, versioned evaluation sample with documented provenance and privacy controls.
- Evaluation metrics and acceptance thresholds, including slice-level metrics where important.
- Seed-controlled training or sampling where deterministic execution is feasible.
- Golden predictions with tolerance bands rather than exact equality when numerical kernels differ.
- Model artifact, feature schema, tokenizer, prompt, and dependency versions.
- Latency, memory, throughput, and failure-rate baselines for serving.
- Explicit checks for train/serve skew, leakage, data drift, and non-reproducible preprocessing.

A fixed seed does not guarantee bitwise-identical GPU or distributed training. Record hardware, library versions, deterministic settings, and known sources of nondeterminism. Evaluation data must remain isolated from training when measuring generalization.

### 15.2 LLM integrations

For code that calls a hosted LLM, record/replay provider responses with a cassette or fake client and test the deterministic surrounding logic: prompt construction, tool routing, parsing, validation, retry policy, and error handling. Keep cassettes scrubbed of secrets and personal data. A recorded response makes a test reproducible but does not prove the live model will always respond that way. Use separate evaluations for output quality, safety, and drift; do not treat exact text snapshots as a sufficient quality measure.

## 16. Test-suite hygiene and measuring safety

- Mark characterization tests consistently, for example with `@pytest.mark.characterization`, and register the marker in the repository's existing `pyproject.toml` configuration (merge this entry into an existing pytest options table rather than creating a duplicate table):

  ```toml
  [tool.pytest.ini_options]
  markers = [
    "characterization: captures observed legacy behaviour, not correctness",
  ]
  ```
- Keep characterization tests until their behaviour is intentionally replaced by stronger specification/regression tests or the old behaviour is removed.
- Track the number or proportion of characterization tests over time as a migration indicator, not as a standalone quality score; a falling ratio is meaningful only when the tests are replaced by stronger evidence.
- Review snapshots and delete obsolete artifacts deliberately; do not regenerate blindly.
- Track flaky-test rate and investigate root causes rather than repeatedly rerunning until green.
- Measure changed-line coverage with a tool such as `diff-cover` where configured; changed-line coverage is often more actionable than repository-wide coverage alone.
- Track mutation score for the changed module when practical; interpret surviving/equivalent mutants carefully.
- Measure test duration and keep slow integration/benchmark suites separately selectable.
- Document known bugs and their status; remove `xfail` markers when the defect is fixed or the expectation is abandoned.

The goal is **confidence proportional to risk**, not 100% coverage. High-risk payment, privacy, schema, or checkpoint code deserves stronger evidence than a low-impact formatting helper.

## 17. Practical command reference

Run commands from the repository root unless noted. Inspect `pyproject.toml`, the lock file, and contributor instructions first; use the project's chosen environment manager where available.

| Goal | Command | Notes |
|---|---|---|
| Run focused tests | `python -m pytest -q tests/test_legacy_import.py` | Uses the active Python environment |
| Run marked tests | `python -m pytest -m characterization -q` | Requires marker registration for clean output |
| List collected tests | `python -m pytest --collect-only -q` | Helps discover test structure and fixtures |
| Branch coverage | `python -m coverage run --branch -m pytest` | Requires `coverage` installed |
| Coverage summary | `python -m coverage report -m` | Shows missing lines; inspect branches separately in HTML |
| Inspect diff | `git diff -- tests/` | Review expected-output changes before committing |
| Find a symbol | `rg -n "discount|load_orders" src tests` | `rg` (ripgrep) is optional; use `git grep` or IDE search otherwise |
| Inspect changed files | `git status --short` | Check generated snapshots and unintended artifacts |

Install optional tools only in a project-managed development environment. On Windows PowerShell, commands are generally the same when executables are on `PATH`; path quoting and shell pipelines differ. In PowerShell, `;` separates commands and is not a portable substitute for every POSIX pipeline. On Windows, use `py -m pytest` if `python` is not the intended interpreter. Avoid destructive commands and never run unfamiliar project scripts against production credentials or datasets.

## 18. Common mistakes and troubleshooting

### Mistake: fixing the bug while capturing the baseline

**Why it fails:** You lose evidence of the old contract and combine two review questions.  
**Better approach:** Record observed behaviour, file a separate issue, then fix it in a separate change with an explicit specification test.

### Mistake: asserting the implementation line by line

**Why it fails:** Tests mirror internals and break during harmless refactoring.  
**Better approach:** Assert observable results, boundaries, side effects, and error contracts that matter to callers.

### Mistake: accepting snapshots nobody reviewed

**Why it fails:** A defect can be approved accidentally as a baseline.  
**Better approach:** Review the diff, explain meaningful changes, and require approval for baseline updates.

### Mistake: over-normalizing

**Why it fails:** Sorting, rounding, or removing fields can hide real regressions.  
**Better approach:** Document each normalization rule and test that it removes only irrelevant variation.

### Mistake: using live dependencies in unit tests

**Why it fails:** Network, clock, database, and environment changes cause flakiness and unsafe side effects.  
**Better approach:** Add seams and fakes; reserve real-service tests for controlled integration environments.

### Mistake: treating coverage as proof

**Why it fails:** A line can execute without an assertion detecting a wrong result.  
**Better approach:** Review branch cases and use mutation testing on risky code.

### Mistake: differential testing hides known differences

**Why it fails:** Broad exception handling or normalization can hide real mismatches.  
**Better approach:** Classify each mismatch and encode the decision explicitly.

### Troubleshooting quick checks

- **Test output changes each run:** inspect clocks, randomness, unordered data, parallelism, environment variables, and remote dependencies.
- **Snapshot diff is huge:** canonicalize semantic structures, split large fixtures, or compare focused contracts; do not simply suppress all differences.
- **Import causes side effects:** isolate the import in a subprocess or move effects behind an explicit entry point.
- **SQLite test passes but production DB fails:** validate dialect-specific types, transactions, constraints, and query semantics against the real engine in integration tests.
- **Hypothesis test is slow:** constrain strategies to valid domain inputs, isolate side effects, and use focused examples before broad generation.
- **Mutation run is expensive:** scope it to the changed module and run it after the ordinary suite is stable.
- **A test is xfailed but the bug is fixed:** remove the marker and replace the test with a normal assertion for intended behaviour.

## 19. Hands-on exercises

Use a disposable branch or practice repository. Do not run these experiments against production data.

### Exercise 1 — Characterize a legacy function

Given the `discount()` example, write tests for gold, silver, unknown tier, empty tier, `None`, zero, and negative amount. Include at least one suspicious observation in a separate known-bug note.

**Expected result:** Tests describe current outputs, including the negative amount result; the note states why it may be wrong without changing the function.

### Exercise 2 — Golden-master CSV

Run an existing CSV report generator against at least three fixtures: ordinary rows, empty input, and malformed input. Save reviewed baselines. Normalize only line endings or volatile fields shown to be irrelevant.

**Expected result:** Repeated runs produce stable comparisons. A changed amount, row count, or required column causes a meaningful failure.

### Exercise 3 — Introduce a seam

Find a legacy function that calls `datetime.now()`, reads an environment variable, or writes directly to a fixed path. Add a minimal seam and test it using a fixed clock, `monkeypatch`, or `tmp_path`.

**Expected result:** The test does not depend on the real clock/environment/filesystem destination, and observed behaviour remains unchanged for the baseline case.

### Exercise 4 — Differential comparison

Run old and new implementations through Hypothesis for a representative input domain. Save at least one discovered mismatch as a minimal example and classify it.

**Expected result:** The test catches differences; no mismatch is silently ignored. If the mismatch is an accepted bug fix, the comparison policy and specification test are explicit.

### Exercise 5 — Pipeline profile

For a fixed partition, compare row counts, schema, null/duplicate keys, selected aggregates, and canonicalized row outputs between old and new pipeline paths.

**Expected result:** A report identifies which dimensions match and which differ, with evidence and a decision for each difference.

### Exercise 6 — Mutation sensitivity

Run a mutation tool against a small, characterized function. Inspect at least one killed mutant and one surviving or equivalent mutant if available.

**Expected result:** Explain what the killed mutant demonstrates and why a surviving mutant does not automatically mean the test suite is inadequate.

## 20. Self-check questions and answer key

Try answering before reading the key.

1. What is the primary purpose of a characterization test?
2. Explain the six-step workflow.
3. Why is a passing characterization test not proof of correctness?
4. Name three ways to create a seam in Python.
5. When should you use a golden master, and what must be reviewed before updating it?
6. What does branch coverage tell you, and what does it not tell you?
7. How does mutation testing assess test sensitivity?
8. Why might `pytest.approx` be appropriate for one output but wrong for another?
9. What should you compare when characterizing an ETL pipeline?
10. Why can `importlib.reload()` fail to reset all legacy global state?
11. What precautions are needed for shadow execution?
12. How should a known bug be represented without mixing it into characterization?

<details>
<summary><strong>Answer key</strong></summary>

1. To record and protect observable behaviour that the current implementation exhibits, whether or not it is correct.
2. Put code in a harness; assert an obviously wrong expectation; run and observe; replace it with the observed result; repeat across representative/edge inputs; record suspicious behaviour separately.
3. It covers only tested cases and preserves existing defects as readily as intended behaviour.
4. Inject a dependency as a parameter; wrap an external API; monkeypatch the module-level name used by the code; extract/override a method; use temporary resources or subprocess isolation.
5. Use it for substantial or structured outputs. Review every semantic diff, verify normalization, and never blindly regenerate the baseline.
6. It shows which branches ran, not whether assertions would detect wrong results or whether untested behaviour is correct.
7. It mutates code and checks whether tests fail; surviving mutants can expose weak assertions but may also be equivalent or unreachable.
8. Small floating-point variation may be acceptable for numerical outputs, but exact identifiers, counts, schema, or monetary rules may require exact/domain-specific comparisons.
9. Input scope, row counts, schema, key/value parity, nulls, duplicates, distributions, checksums/canonicalized rows, and operational behaviour such as retries, checkpointing, runtime, and memory.
10. Reload re-executes one module, but references imported elsewhere, external resources, and other module state may persist; import-time effects can run again.
11. Use isolated scratch sinks, avoid irreversible side effects, scrub PII/secrets from diffs, compare equivalent inputs, monitor failures, and define rollback/stop criteria.
12. Record input, observed result, impact, evidence, and issue separately; if using `xfail(strict=True)`, make clear it expresses a planned specification/known defect and remove it when resolved.

</details>

## 21. Capstone — characterize a 200-line legacy function

**Goal:** Establish a reliable behavioural baseline for a roughly 200-line function in the module's practice repository, then prepare it for the safe refactoring work in Lesson 03.

### Constraints

- Use a disposable branch or worktree and safe sample data.
- Select a real legacy function around 200 lines. If the exact function is slightly shorter or longer, document why it is the best representative target.
- Do not combine bug fixes with characterization.
- Use 20 representative sample inputs for a golden-master baseline.
- Keep all tests green at every refactoring commit in the subsequent Lesson 03 work.
- Record at least three discovered bugs separately as issues or carefully justified expected-failure tests.

### Four phases

**Phase A — Understand and select (30–45 minutes)**

1. Identify the function's callers, dependencies, inputs, outputs, side effects, and failure modes.
2. Write a short behaviour hypothesis and list unknowns.
3. Choose 20 sample inputs spanning ordinary, boundary, empty/null, malformed, and high-volume or special cases where appropriate.
4. Note the runtime/dependency versions and commands needed to reproduce results.

**Phase B — Characterize (60–90 minutes)**

1. Apply all six workflow steps.
2. Add tests at the public boundary first, then targeted tests for risky branches.
3. Capture the 20-input golden master. Normalize only explicitly irrelevant volatility.
4. Run the suite and inspect coverage/branches in the target area.
5. Record at least three suspicious behaviours with evidence and separate follow-up issues. Do not silently fix them.

**Phase C — Assess sensitivity and stability (30–45 minutes)**

1. Repeat the tests to check determinism.
2. Review snapshots manually and ensure no secrets/PII are present.
3. Add Hypothesis differential tests if a candidate replacement exists; otherwise use generated inputs to explore the legacy behaviour.
4. Run mutation testing on the target when feasible, or document why it is impractical and use an explicit manual sensitivity review.
5. Record known limitations: untested branches, external systems not isolated, performance assumptions, and environment constraints.

**Phase D — Prepare for refactoring (30 minutes)**

1. Write a concise baseline summary: what is observed, what remains unknown, and what is suspicious.
2. Identify seams needed before larger changes.
3. Define how to detect behaviour changes in the next lesson.
4. Commit the characterization work separately from future bug fixes and structural refactoring.

### Required deliverables

- `tests/` characterization tests with a clear marker or naming convention.
- A golden-master baseline for 20 sample inputs, with a documented generation/review process.
- A short behaviour note listing inputs, outputs, side effects, exception paths, and environment assumptions.
- At least three separate known-bug records with evidence and impact; use `xfail(strict=True)` only where its meaning is justified.
- Test and coverage output, plus mutation results if available.
- A list of unresolved questions and a proposed seam/refactoring order.

### Acceptance criteria

- [ ] All 20 sample inputs are represented and traceable to fixtures or documented cases.
- [ ] Tests pass repeatedly in the declared environment without unexplained flakiness.
- [ ] Observed behaviour is separated from desired behaviour.
- [ ] Golden-master updates are reviewable and normalize only irrelevant fields.
- [ ] Important boundary, error, and side-effect paths are represented.
- [ ] At least three suspected bugs are documented separately and not silently fixed.
- [ ] External dependencies are controlled or their uncontrolled status is documented.
- [ ] The next refactoring phase has a clear baseline and a small-step test strategy.
- [ ] The work can be reproduced from written commands and fixture instructions.

The capstone is successful when you can explain what evidence you have, what it covers, what it does not cover, and which behaviour changes require an explicit decision. It is not successful merely because the test count is high.

## 22. Final competency checklist

You are ready to proceed when you can do the following without relying on guesswork:

- [ ] Distinguish characterization, regression, and specification tests.
- [ ] Apply the six-step observation workflow and preserve suspicious behaviour separately.
- [ ] Design representative inputs and deterministic fixtures.
- [ ] Build and review golden masters with careful normalization.
- [ ] Introduce seams and isolate external dependencies.
- [ ] Use outside-in tests, coverage, and mutation testing appropriately.
- [ ] Compare legacy and replacement implementations without hiding mismatches.
- [ ] Characterize pipeline schemas, counts, distributions, idempotency, and checkpoint behaviour.
- [ ] Identify ML reproducibility, leakage, and train/serve-skew risks.
- [ ] Establish performance/resource baselines where risk warrants them.
- [ ] Explain how strangler migrations, shadow runs, flags, and canaries use characterization evidence.
- [ ] Complete the capstone with a reproducible baseline, 20 inputs, and three separately documented suspected bugs.

## 23. References

Use the versions supported by the target repository and verify commands against the installed tool version.

- `pytest` documentation: https://docs.pytest.org/
- Hypothesis documentation: https://hypothesis.readthedocs.io/
- Coverage.py documentation: https://coverage.readthedocs.io/
- Python `unittest.mock` documentation: https://docs.python.org/3/library/unittest.mock.html
- Python `tempfile` documentation: https://docs.python.org/3/library/tempfile.html
- Python `importlib` documentation: https://docs.python.org/3/library/importlib.html
- Michael Feathers, *Working Effectively with Legacy Code* — characterization tests and seams.
- Martin Fowler, *Refactoring* — safe incremental changes and behaviour preservation.
- Sculley et al., “Hidden Technical Debt in Machine Learning Systems” — https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html

---

**Lesson boundary:** This lesson establishes evidence about existing behaviour. The next lesson uses that evidence to refactor in small, reversible steps. Do not treat characterization as a substitute for a specification, and do not combine structural cleanup with unreviewed behaviour changes.
