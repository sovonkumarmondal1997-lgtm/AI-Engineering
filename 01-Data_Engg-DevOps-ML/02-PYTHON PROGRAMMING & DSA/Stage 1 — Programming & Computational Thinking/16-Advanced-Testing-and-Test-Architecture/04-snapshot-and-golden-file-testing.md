# Snapshot and Golden-File Testing

> **Stage 1 · Module 16 — Advanced Testing and Test Architecture · Lesson 04**  
> **Scope:** pytest 8+, Python 3.12+, snapshot and regression-testing workflows.  
> **Core rule:** an expected output is a reviewed specification, not a file to refresh until CI turns green.

## Learning outcomes

After this lesson, you should be able to:

- Explain what snapshots and golden files test well—and when explicit assertions are better.
- Maintain a plain golden file and compare generated output exactly.
- Use Syrupy's `snapshot` fixture, `.ambr` files, JSON extensions, parametrization, and deliberate update workflow.
- Stabilize time, randomness, IDs, paths, line endings, locale, and floating-point representations without hiding meaningful regressions.
- Choose among Syrupy, `pytest-regressions`, ApprovalTests, and `inline-snapshot`.
- Build small golden datasets for data pipelines, combine output comparisons with invariants, and snapshot schemas as contracts.
- Test prompts and LLM-pipeline intermediate artifacts safely while avoiding false confidence from nondeterministic model output.
- Review diffs, handle obsolete snapshots and migrations, and answer all roadmap self-check questions.

## 1. What is a snapshot test?

**How to read the examples:** the plain golden-file renderer, clock-injection function, random-sample function, and small normalizers are self-contained examples. Tests that call application-specific names such as `render_report`, `build_report`, `build_daily_totals`, `describe_schema`, or `main` are focused teaching snippets: those functions are assumed to be implemented by the project under test. Install optional tools such as Syrupy or `pytest-regressions` in the project's test environment before running examples that use their fixtures. Snapshot baselines are created by a deliberate local review workflow; they are not included as generated outputs in this lesson.

A snapshot test captures a program's observable output as an expected baseline, then compares future output against it. The baseline may be a text file, JSON file, image, tabular dataset, generated SQL, CLI output, schema description, or a serialized intermediate artifact.

A **golden file** is a human-maintained expected output file. A **snapshot testing library** automates parts of creating, locating, serializing, comparing, and reporting differences in such baselines. They share the same principle: a difference is a signal to investigate, not proof that either the code or baseline is correct.

Typical workflow:

```text
small, controlled input
        |
        v
code under test generates output
        |
        v
normalize only known nondeterminism
        |
        v
compare with reviewed baseline
        |
   +----+----+
   |         |
 equal    different
   |         |
 pass     inspect diff
             |
       +-----+------+
       |            |
   regression   intentional change
       |            |
   fix code     review and update
```

Snapshots are especially useful when the output is large or structured enough that manually writing every expected value is cumbersome, but still small and readable enough for a reviewer to understand.

### 1.1 Good use cases

- Rendered reports, HTML fragments, generated SQL, command-line help, error messages, or configuration output.
- A parser's normalized representation or a compiler/code generator's output.
- A bounded API response after volatile fields have been normalized.
- A small data-pipeline result where column names, ordering, schema, and selected values matter.
- A prompt template or deterministic intermediate representation sent to an LLM.
- Visual output, if image-diff noise and platform differences are controlled.

### 1.2 Poor use cases

- A huge output that no reviewer can meaningfully inspect.
- Values that change every run for reasons unrelated to correctness.
- Nondeterministic LLM responses treated as exact expected strings.
- A value whose correctness is better expressed by a few precise predicates.
- An entire database export when a schema contract and representative rows would be more informative.
- Sensitive data, credentials, tokens, or raw production records.
- A baseline whose updates are accepted automatically without understanding the diff.

Snapshots verify **regression against an existing baseline**. They do not prove that the baseline is correct, that the requirements are complete, or that missing behaviour exists. A wrong implementation can produce a wrong snapshot that later becomes institutionalized.

## 2. Plain golden files: the basic technique

Use a plain file when exact text is the contract and you want zero additional dependencies.

Suggested layout:

```text
project/
├── src/
│   └── ledger/
│       └── report.py
└── tests/
    ├── golden/
    │   └── daily-summary.txt
    └── test_report.py
```

Suppose the function under test is:

```python
def render_summary(rows: list[dict[str, object]]) -> str:
    total = sum(int(row["amount"]) for row in rows)
    return f"rows={len(rows)}\ntotal={total}\n"
```

Golden file `tests/golden/daily-summary.txt`:

```text
rows=2
total=125
```

Test:

```python
from pathlib import Path

def test_render_summary_matches_golden_file():
    rows = [
        {"amount": 100},
        {"amount": 25},
    ]
    actual = render_summary(rows)
    expected_path = Path(__file__).parent / "golden" / "daily-summary.txt"
    expected = expected_path.read_text(encoding="utf-8")

    assert actual == expected
```

**Expected behaviour:** the test passes if the function returns exactly the file contents, including line breaks and the final newline. If the golden file does not have the same final newline as `actual`, the assertion fails. That is often useful for text output, but it must be an intentional policy.

Use a path anchored to `__file__`, not the process's current working directory. CI, IDEs, and local shells may start pytest from different directories.

### 2.1 Inspect the diff, don't just read the failure message

For larger output, show a unified diff:

```python
import difflib
from pathlib import Path

def assert_text_matches_golden(actual: str, expected_path: Path) -> None:
    expected = expected_path.read_text(encoding="utf-8")
    if actual != expected:
        diff = "".join(
            difflib.unified_diff(
                expected.splitlines(keepends=True),
                actual.splitlines(keepends=True),
                fromfile=str(expected_path),
                tofile="actual",
            )
        )
        raise AssertionError(f"Golden-file mismatch:\n{diff}")
```

This helper is deliberately small. For a project-wide library, use a maintained regression/snapshot tool rather than reinventing serialization, naming, binary handling, and update workflows.

### 2.2 Manual update workflow

When output changes:

1. Run the failing test and capture the actual output.
2. Determine whether the change is intended and consistent with requirements.
3. Inspect the diff with enough context to understand every changed section.
4. Update only the relevant expected file.
5. Add or adjust targeted assertions for important invariants.
6. Run the test again, then run the relevant surrounding suite.
7. Commit the test and expected-output change together with an explanatory reviewable diff.

Never write a helper that replaces the expected file every time the test runs. That turns regression detection into a no-op.

## 3. Syrupy: snapshots integrated with pytest

A CLI help snapshot is useful when help text is a user-facing contract. This focused snippet assumes `main(argv)` uses `argparse`, whose `--help` path raises `SystemExit(0)`:

```python
import pytest

def test_cli_help(snapshot, capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    assert capsys.readouterr().out == snapshot
```

If the CLI framework returns normally rather than raising `SystemExit`, adapt the test to that documented behavior. Capture the intended stream (stdout versus stderr) and compare it to the reviewed baseline.

Syrupy is a pytest plugin that supplies a `snapshot` fixture and stores expected values under a `__snapshots__/` directory beside the test module. Its default human-readable `.ambr` format is useful for reviewing structured representations. Install it in the project's test environment:

```bash
python -m pip install syrupy
```

Check the installed version against the project's Python and pytest versions. Syrupy's compatibility matrix changes across major versions; use its current documentation and the project's lockfile rather than assuming all versions work with all pytest releases.

### 3.1 First snapshot

```python
def test_report(snapshot):
    actual = render_summary([
        {"amount": 100},
        {"amount": 25},
    ])
    assert actual == snapshot
```

On the first run, the snapshot is missing, so the test fails and reports that an expected snapshot must be created. After independently checking the intended output, deliberately generate it:

```bash
pytest --snapshot-update
```

Syrupy creates a file under `tests/__snapshots__/` (for example, `test_report.ambr`). Commit that file with the test. On later runs, Syrupy compares current output to the committed baseline.

**Important:** `--snapshot-update` is not a routine test flag. Syrupy's update mode updates mismatches and can delete unused snapshots. Use it only in a controlled local workflow after inspecting the reason for the change. For new snapshots without changing existing mismatches, Syrupy also documents `--snapshot-update-new-only`; verify options with the installed version's `pytest --help`.

A typical review sequence:

```bash
pytest tests/test_report.py
# Investigate the failure; do not update yet.

pytest --snapshot-update tests/test_report.py
git status --short
git diff -- tests/
pytest tests/test_report.py
```

For an additive workflow, `pytest --snapshot-update-new-only tests/test_report.py` creates missing snapshots without replacing existing mismatches. By contrast, `--snapshot-update` updates mismatches and removes unused snapshots unless cleanup is disabled. Confirm these options with `pytest --help` for the installed Syrupy version. The update command can make files match current output; it cannot determine whether the output is correct. A passing test immediately after a snapshot update is not evidence that the code is right.

### 3.2 Naming multiple snapshots in one test

If a test has multiple snapshot assertions, Syrupy uses an index by default. Prefer descriptive names when they improve reviewability:

```python
def test_report_sections(snapshot):
    assert render_header() == snapshot(name="header")
    assert render_totals() == snapshot(name="totals")
```

Custom names must be unique within that test case. Keep each snapshot focused. If a single test compares unrelated objects, split it so a change in one behaviour does not produce an opaque combined diff.

### 3.3 JSON snapshots

For JSON-like structures, use Syrupy's JSON extension:

```python
from syrupy.extensions.json import JSONSnapshotExtension

def test_api_payload(snapshot):
    payload = {
        "status": "ok",
        "records": [
            {"id": 1, "name": "Ada"},
            {"id": 2, "name": "Lin"},
        ],
    }
    assert payload == snapshot(extension_class=JSONSnapshotExtension)
```

The extension stores a `.json` snapshot with readable formatting. This can be more familiar to API and data-engineering reviewers than the default `.ambr` representation.

If many tests need the same JSON defaults, define a fixture in `conftest.py`:

```python
import pytest
from syrupy.extensions.json import JSONSnapshotExtension

@pytest.fixture
def snapshot_json(snapshot):
    return snapshot.with_defaults(extension_class=JSONSnapshotExtension)
```

Then:

```python
def test_api_payload(snapshot_json):
    payload = {"status": "ok", "count": 3}
    assert payload == snapshot_json
```

Syrupy also supports `PNGImageSnapshotExtension` and `SVGImageSnapshotExtension` for image data, and `SingleFileSnapshotExtension` as a building block for single-file output. For binary snapshots, use an extension intended for that data type. The default snapshot mode expects serializable values and may reject arbitrary non-byte-like objects. Consult the Syrupy extension documentation before assuming an output format is supported.

### 3.4 Parametrized snapshots

Parametrize cases when they exercise the same contract with different inputs:

```python
import pytest

@pytest.mark.parametrize(
    "currency, amount",
    [
        pytest.param("USD", 125, id="usd"),
        pytest.param("EUR", 90, id="eur"),
    ],
)
def test_render_amount(currency, amount, snapshot):
    actual = render_amount(currency=currency, amount=amount)
    assert actual == snapshot
```

The IDs make test names and associated snapshots easier to interpret. Avoid generating dozens of nearly identical snapshots when one focused parameterized assertion or a small invariant would communicate the contract better.

### 3.5 Matchers and volatile fields

Sometimes only selected fields are volatile. Syrupy offers matchers and filters to exclude or normalize paths. For example, with a JSON-like payload, excluding a known field can be concise:

```python
from syrupy.filters import props

def test_response_ignores_request_id(snapshot):
    response = {
        "request_id": "generated-uuid",
        "status": "accepted",
        "count": 3,
    }
    assert response == snapshot(exclude=props("request_id"))
```

This intentionally removes `request_id` from the snapshot comparison. It also means regressions in that field are not caught by this snapshot. Add a targeted assertion if its type or format is part of the contract:

```python
def test_response_ignores_request_id_but_checks_its_shape(snapshot):
    response = {
        "request_id": "generated-uuid",
        "status": "accepted",
        "count": 3,
    }
    assert response == snapshot(exclude=props("request_id"))
    assert isinstance(response["request_id"], str)
    assert response["request_id"]
```

Do not exclude broad objects or whole sections just to make tests pass. Prefer normalizing a field to a stable placeholder if its presence and shape matter. Syrupy's `path_type`, `path_value`, and matcher composition APIs can express more specific policies; confirm exact matcher signatures in the installed version's docs.

### 3.6 Unused snapshots and lifecycle

A snapshot can become obsolete when a test is deleted, renamed, or no longer makes an assertion. Syrupy detects unused snapshots and, by default, treats them as a problem. `--snapshot-warn-unused` can change this to a warning; `--snapshot-no-cleanup` controls cleanup during update runs. These options are useful for migrations, not as a permanent way to ignore stale baselines.

When removing a test, check the associated snapshot. When renaming or restructuring tests, inspect the resulting snapshot diff and ensure no expected behaviour has disappeared accidentally.

## 4. Stabilize output without hiding regressions

A snapshot must be deterministic enough that unrelated environmental variation does not create noise. Normalization should remove only values whose variation is explicitly outside the contract.

### 4.1 Control time

Prefer injecting a clock over patching global time throughout the application:

```python
from datetime import datetime, timezone

def render_report(*, now: datetime) -> str:
    return f"generated_at={now.isoformat()}\n"

def test_report_time_is_explicit():
    fixed = datetime(2025, 1, 2, 3, 4, tzinfo=timezone.utc)
    assert render_report(now=fixed) == "generated_at=2025-01-02T03:04:00+00:00\n"
```

The expected output is fixed and the time dependency is visible in the function signature. If the application cannot accept an injected clock, use a time-freezing library such as `freezegun` where appropriate, and scope the freeze narrowly. Be aware that freezing wall-clock time does not necessarily freeze monotonic clocks used for elapsed-time measurement.

For timestamps that are not part of the behaviour under test, normalize them to a stable placeholder or exclude them deliberately. If timezone conversion is the contract, do not remove the timezone from the snapshot.

### 4.2 Control randomness and generated identifiers

Seed a random generator when the exact random sequence is part of the test:

```python
import random

def make_sample(seed: int) -> list[int]:
    rng = random.Random(seed)
    return [rng.randint(1, 9) for _ in range(4)]

def test_sample_is_reproducible():
    first = make_sample(7)
    assert first == make_sample(7)
    assert len(first) == 4
    assert all(1 <= value <= 9 for value in first)
```

The repeated-call assertion checks reproducibility for the same seed; the length and range assertions express separate invariants. This is not a test of the statistical quality of the random generator. A local `random.Random(seed)` avoids mutating global random state. Do not depend on a seed to make external services, UUIDs, concurrency, or model outputs deterministic. For generated IDs, inject an ID factory or normalize the ID only if the ID's specific value is irrelevant.

### 4.3 Mask IDs and timestamps carefully

A good normalizer is explicit and narrow:

```python
from copy import deepcopy

def normalize_response(payload: dict) -> dict:
    result = deepcopy(payload)
    result["request_id"] = "<request-id>"
    result["created_at"] = "<timestamp>"
    return result

def test_response_shape(snapshot):
    payload = {
        "request_id": "abc-123",
        "created_at": "2025-01-02T03:04:05Z",
        "status": "accepted",
        "count": 3,
    }
    assert normalize_response(payload) == snapshot
```

This stabilizes exact ID/time values but preserves field presence. Add separate assertions for validity if needed:

```python
def test_normalized_response_preserves_id_contract():
    payload = {
        "request_id": "abc-123",
        "created_at": "2025-01-02T03:04:05Z",
        "status": "accepted",
        "count": 3,
    }
    normalized = normalize_response(payload)

    assert normalized["request_id"] == "<request-id>"
    assert normalized["created_at"] == "<timestamp>"
    assert payload["request_id"]
    assert payload["status"] == "accepted"
```

Avoid regex replacement that can accidentally scrub meaningful text or mask a real bug. Test the normalizer itself on representative values, including malformed or missing fields when relevant.

### 4.4 Normalize paths, line endings, locale, and encoding

Absolute temporary paths differ by machine and worker. Convert known roots to placeholders:

```python
from pathlib import Path

def normalize_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()
```

This function assumes `path` is inside `root`; it deliberately raises `ValueError` otherwise instead of silently replacing an unexpected path. If external paths are allowed, handle them explicitly.

For generated text:

```python
def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")
```

Normalize line endings only if LF/CRLF is not part of the contract. Read and write text with explicit UTF-8 encoding. If locale affects number or date formatting, set a deterministic locale in the test environment or inject formatting rules; do not rely on the developer's operating-system locale.

Avoid replacing every slash, backslash, or colon globally. That can damage URLs, escaped strings, or Windows-specific output that is itself under test.

### 4.5 Floating-point and numeric output

Choose the comparison method according to the contract:

- If a rendered decimal string is an externally visible format, specify rounding and formatting in production code and snapshot the resulting string.
- If values are numeric measurements with tolerance, use numeric comparisons rather than an exact text snapshot.
- If a table or dataframe is expected to match exactly, use exact comparisons where appropriate and explicitly configure tolerances only for known numerical variation.

For example:

```python
def render_total(amount: float) -> str:
    return f"{amount:.2f}"

def test_render_total_rounds_to_two_places():
    assert render_total(12.345) == "12.35"
```

For floating-point data, use tolerances that reflect domain requirements. Excessively broad tolerances can hide real regressions; excessively tight tolerances can fail across numerical libraries or platforms for insignificant differences.

### 4.6 Normalize collections and serialization

JSON object key order is not usually a semantic contract, but array order often is. If the contract treats records as an unordered set, sort by a stable business key before snapshotting. Do not sort output merely to silence a diff if order is meaningful.

Serialize JSON deterministically when a text representation is the contract:

```python
import json

def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        indent=2,
        allow_nan=False,
    ) + "\n"
```

`allow_nan=False` rejects non-standard `NaN`/infinity JSON output. Sorting keys does not sort arrays. If Unicode normalization matters for the domain, normalize strings explicitly with `unicodedata.normalize` and document the policy.

## 5. Reviewable snapshot diffs and update governance

Snapshots become valuable when their diffs are understandable. Apply these rules:

- **Small and focused:** one snapshot should represent one logical output or contract.
- **Meaningful names:** use test IDs and explicit snapshot names that communicate scenario and purpose.
- **Readable serialization:** prefer formatted text/JSON over opaque binary where feasible.
- **Review in version control:** commit baselines; inspect `git diff` in pull requests.
- **Explain intentional changes:** state why output changed and what behavioural contract changed.
- **Pair with targeted assertions:** snapshots are broad regression checks, not a substitute for all semantic checks.
- **Delete obsolete snapshots deliberately:** check why a baseline became unused before removing it.
- **Keep update operations local and explicit:** never put snapshot-update flags into default project configuration or routine CI test commands.

### 5.1 Why CI must not auto-update snapshots

CI must run tests against committed expected values, not rewrite those values to match the code being tested. If CI updates snapshots automatically, a broken change can update the baseline and pass on the same run. The comparison no longer protects against regressions; it merely records the current output.

A safe CI command is ordinary pytest, for example:

```bash
pytest
```

Do not add `--snapshot-update` to `addopts`, CI scripts, pre-commit hooks, or release jobs. A human can run an explicit update command locally after reviewing the output, then submit the baseline changes for normal code review.

### 5.2 A snapshot review checklist

For every changed baseline, ask:

1. What code or requirement caused this change?
2. Is the changed output intentional, or did environment/time/randomness drift?
3. Does the diff include unexpected IDs, secrets, paths, ordering, or unrelated fields?
4. Are any fields missing because a normalizer or exclusion is too broad?
5. Is the output still valid under its schema and domain invariants?
6. Is the snapshot small enough to review?
7. Do the tests include targeted assertions for critical values?
8. Did the update delete or rename snapshots that still represent required behaviour?
9. Does the baseline contain PII, credentials, tokens, or proprietary data?
10. Can the reviewer explain why the new expected output is correct?

If these questions cannot be answered, do not approve the snapshot update.

## 6. Alternatives and complementary tools

Different tools suit different baseline types. Check versions and configuration before adopting a command from a tutorial.

### 6.1 `pytest-regressions`

`pytest-regressions` provides fixtures for data, files, numbers, dataframes, arrays, and images. It is particularly useful when a pipeline produces structured data or files.

Example for a dictionary:

```python
def test_summary_data(data_regression):
    actual = {
        "row_count": 3,
        "invalid_count": 1,
        "columns": ["customer_id", "amount"],
    }
    data_regression.check(actual)
```

On the first run, the fixture reports that the baseline is missing and writes an obtained baseline file. Review it and commit it intentionally. Later runs compare against it. The plugin has regeneration flags such as `--regen-all`; these are powerful and should not be used blindly. A regeneration run may update many baselines at once.

For dataframe output, the plugin's `dataframe_regression` supports tolerances for numeric data. For file output, `file_regression` can compare text or bytes. See the official API for the precise fixture signatures and supported data types.

### 6.2 ApprovalTests

ApprovalTests is useful when a large output benefits from an external diff reporter or approval workflow. A minimal example:

```python
from approvaltests.approvals import verify

def test_report_approval():
    result = render_summary([{"amount": 100}, {"amount": 25}])
    verify(result)
```

The first run establishes an approved baseline through the configured reporter/workflow; later differences are reviewed. Treat approval as a deliberate human decision, not an automatic acceptance. ApprovalTests supports multiple test frameworks; pytest-specific reporter options may require its companion plugin. Some reporter/configuration modes may invoke external tools or scripts, so review their CI and network implications.

### 6.3 `inline-snapshot`

`inline-snapshot` stores expected values in test code, which can make small values and transformations convenient to review:

```python
from inline_snapshot import snapshot

def test_tax_rate():
    actual = calculate_tax_rate("standard")
    assert actual == snapshot(0.20)
```

Run its review/report workflow as documented for the installed version. The tool's pytest options have evolved; current versions support modes such as `review`, `report`, `create`, `fix`, and `update`, but the exact defaults and behavior depend on version and environment. Do not assume a mode is read-only: some modes modify source code. CI should use the documented non-mutating/disabled mode and must not auto-approve changes.

### 6.4 Decision table

| Need | Likely starting point | Why |
|---|---|---|
| A short stable text file | Plain golden file | Minimal dependency, transparent diff |
| Many pytest snapshots of strings/objects | Syrupy | Snapshot discovery, readable `.ambr`, extensions and matchers |
| Structured data files, dataframes, numbers, images | `pytest-regressions` | Specialized regression fixtures and tolerances |
| Large output with rich external diff workflow | ApprovalTests | Approval reporters for complex output |
| Small values embedded in test source | `inline-snapshot` | Expected values stay near assertions |
| A handful of semantic requirements | Explicit assertions | Most direct statement of behaviour |

These tools can overlap. Select one main workflow for a given class of output instead of maintaining multiple competing baselines for the same behaviour.

## 7. Over-snapshotting and stronger assertions

A 500-line snapshot may catch a change but provide little guidance about whether it matters. It can also create review fatigue: contributors approve large diffs because they cannot interpret them. Signs of over-snapshotting include:

- One baseline combines unrelated report sections, environment metadata, and diagnostics.
- Every field is snapshot-tested even when only two fields represent the public contract.
- A small harmless formatting change produces hundreds of lines of churn.
- Reviewers routinely approve all changes without reading them.
- Snapshots duplicate explicit assertions without adding meaningful regression coverage.

### 7.1 Use a snapshot plus targeted assertions

For a large JSON report, keep the full output as a regression baseline but assert critical properties explicitly:

```python
def test_report(snapshot_json):
    report = build_report()

    # Broad regression protection for the bounded, normalized representation.
    assert report == snapshot_json

    # Important contract invariants remain obvious to reviewers.
    assert report["schema_version"] == 2
    assert report["summary"]["row_count"] >= 0
```

The invariant assertions are independent of the baseline: they explain important requirements in executable form. If the snapshot changes to a structurally plausible but invalid value, these assertions can still fail.

For some outputs, omit the full snapshot and assert the contract directly:

```python
def test_sql_contains_required_filter():
    sql = build_query(start_date="2025-01-01")
    assert "WHERE event_date >=" in sql
    assert "2025-01-01" in sql
```

Use exact full-text snapshots when formatting or the whole rendered artifact is itself the contract. Use partial or structured assertions when only selected semantics matter. Use property-style invariants for facts that must hold across many outputs, such as idempotency, schema validity, or non-negative counts.

## 8. Golden datasets for data pipelines

Snapshot testing can be valuable for transformations, but it should not turn a data pipeline test into a giant opaque dump.

### 8.1 Use small, representative fixtures

Keep input data small and purposeful:

```text
tests/
├── fixtures/
│   ├── orders.csv
│   └── expected_daily_totals.csv
└── test_daily_totals.py
```

Example test:

```python
from pathlib import Path
import pandas as pd
from pandas.testing import assert_frame_equal

def test_daily_totals_matches_golden_dataset():
    test_dir = Path(__file__).parent
    orders = pd.read_csv(test_dir / "fixtures" / "orders.csv")
    actual = build_daily_totals(orders)
    expected = pd.read_csv(
        test_dir / "fixtures" / "expected_daily_totals.csv"
    )

    actual = actual.sort_values(["event_date", "currency"]).reset_index(drop=True)
    expected = expected.sort_values(["event_date", "currency"]).reset_index(drop=True)

    assert_frame_equal(actual, expected, check_dtype=True)
```

The test assumes both dataframes contain `event_date` and `currency`. The sort is correct only if row order is not itself a contract. If the pipeline promises sorted output, assert that property rather than silently normalizing it.

`pandas.testing.assert_frame_equal` supports explicit controls for dtype, index, column order, and numeric tolerances. Choose them deliberately. If small numeric differences are acceptable, use a domain-appropriate `rtol`/`atol` or a regression fixture with tolerance support. Do not choose a tolerance simply to make the test green.

### 8.2 Schema snapshots and contract tests

Schema tests are often more durable than snapshots of every row. A schema contract may include:

- Column names and order, if order matters.
- Data types and nullable rules.
- Required keys and uniqueness constraints.
- Allowed categorical values or enumerations.
- Units, time zone, and semantic meaning.
- Compatibility expectations for downstream consumers.

For example, snapshot a normalized schema description, then add direct assertions:

```python
def test_output_schema(snapshot):
    schema = describe_schema(build_daily_totals(empty_orders()))
    assert schema == snapshot
    assert schema["columns"]["event_date"]["nullable"] is False
    assert schema["columns"]["total_amount"]["type"] in {"decimal", "float64"}
```

The helper names here represent project functions that the learner implements. The contract is the important part: the schema snapshot shows the complete declared shape, while targeted assertions highlight non-negotiable constraints.

### 8.3 Files beyond CSV

For Parquet or other binary formats, compare logical content and schema rather than raw bytes unless byte-for-byte determinism is required. Binary file bytes can vary due to metadata, compression settings, library versions, or writer implementation even when the logical dataset is equivalent.

A useful pipeline baseline often combines:

1. A small input fixture with boundary cases.
2. A readable expected CSV/JSON or normalized records.
3. A dataframe/array comparison with explicit tolerance where needed.
4. Schema and key invariants.
5. A test of a meaningful failure mode.

Avoid checking in large production samples. Generate synthetic, minimal, privacy-safe examples instead.

## 9. Prompts, LLM pipelines, record-and-replay, and privacy

Snapshotting LLM-related artifacts requires separating **deterministic program behaviour** from **nondeterministic model behaviour**.

### 9.1 Good candidates for snapshots

- The rendered prompt template when inputs and template logic are deterministic.
- A normalized request payload sent to a model client, with credentials removed.
- A parser's normalized representation of a model response.
- A deterministic routing decision or tool-call schema.
- A small, curated evaluation case with a pinned model/configuration only when exact reproducibility is realistically guaranteed.

### 9.2 Bad candidates for exact correctness snapshots

Model responses may change due to model version, server-side updates, sampling, nondeterministic execution, safety layers, or provider behavior. An exact snapshot of free-form generated text is usually brittle and can fail for semantically equivalent responses—or remain green while quality regresses if the baseline is updated blindly.

Use evaluation tests for model quality: rubric-based scoring, golden question/answer sets with tolerances or semantic criteria, structured-output validation, policy checks, and aggregate metrics. Keep exact snapshots for deterministic prompt construction and post-processing where exact representation is a real contract.

### 9.3 Record-and-replay cassettes

Tools such as VCR.py and `pytest-recording` can record HTTP interactions and replay them in tests. This reduces network dependency and makes tests repeatable, but a cassette is itself a golden artifact that needs review.

- Remove authorization headers, API keys, cookies, and other credentials.
- Scrub names, emails, IDs, account details, and other personal or proprietary data.
- Do not commit raw production responses.
- Use synthetic records and a dedicated test account where recording is required.
- Restrict recorded requests to expected hosts and routes.
- Treat cassette changes like code changes; inspect request and response diffs.
- Avoid recording non-repeatable or sensitive model output as if it were a deterministic contract.

Network replay does not prove that the live service still behaves the same way. Keep a small, explicitly controlled integration check when live compatibility matters.

## 10. Cross-platform stability, obsolete snapshots, and migrations

### 10.1 Cross-platform differences

Common sources of snapshot noise include:

- `\r\n` versus `\n` line endings.
- Absolute paths and temporary-directory names.
- Locale-dependent dates, decimal separators, and sorting.
- Platform-specific path separators and permission messages.
- Runtime or dependency versions that alter formatting.
- Floating-point or image-rendering differences.

First decide whether the difference is part of the public contract. If not, normalize narrowly and test the normalizer. If it is part of the contract, keep the platform-specific expectation or test each platform explicitly rather than erasing the difference.

### 10.2 Unused snapshots

An unused snapshot can indicate a removed test, a renamed test, a conditional path that no longer runs, or an accidentally removed assertion. Do not treat every unused snapshot as harmless cleanup. Investigate its origin, verify the corresponding behaviour is no longer required, and delete it intentionally.

### 10.3 Snapshot format migration

When moving from `.ambr` to JSON, changing a schema serializer, or reorganizing golden files:

1. Pin the old and new tool versions in a controlled branch.
2. Capture a small representative sample and compare semantic values.
3. Identify formatting-only changes separately from behaviour changes.
4. Avoid updating all baselines before proving the new serializer preserves meaning.
5. Use a script only when it is deterministic, reviewable, and tested on a small sample.
6. Review generated deletions, new files, naming changes, and unused-snapshot warnings.
7. Run ordinary tests without update flags after migration.
8. Document the baseline format and version expectations.

A mass snapshot rewrite should be treated as a migration with a review plan, not a routine cleanup commit.

## 11. Practical exercises

### Exercise A — create a manual golden file

Create a function that renders a two-row summary. Store its expected output in a text file and compare exactly. Then remove the final newline from the expected file and observe the failure.

**Solution:** anchor the file path to `Path(__file__).parent`, read with `encoding="utf-8"`, and compare strings directly. The missing final newline is a real byte/text difference under exact comparison.

### Exercise B — Syrupy first snapshot

Write a test that snapshots a report, run it once, inspect the proposed output, deliberately update it, and commit the generated snapshot file.

**Solution:** install Syrupy, use `assert actual == snapshot`, run ordinary pytest first, inspect the missing-snapshot failure, then use `pytest --snapshot-update` locally. Inspect `git diff`, rerun without update flags, and commit the test and baseline together.

### Exercise C — make volatile output stable

A report includes a UUID, a timestamp, and an absolute temporary path. Normalize the values without removing their fields.

**Solution sketch:**

```python
def normalize_report(report: dict, project_root: Path) -> dict:
    result = dict(report)
    result["request_id"] = "<request-id>"
    result["generated_at"] = "<timestamp>"
    result["output_path"] = Path(result["output_path"]).resolve().relative_to(
        project_root.resolve()
    ).as_posix()
    return result
```

This assumes `output_path` is inside `project_root`; unexpected external paths raise rather than being silently scrubbed. For nested structures, use a deep copy and a tested path-aware normalizer. Add assertions that the original values have valid shapes.

### Exercise D — shrink a giant JSON snapshot

A 60-line expected JSON literal contains a status, row count, schema version, generated timestamp, request ID, and many record details. Replace it with a snapshot plus two targeted assertions.

**Solution:** normalize or match the volatile timestamp and ID, snapshot the bounded payload, then assert two critical invariants explicitly, such as `status == "ok"` and `row_count >= 0`. Keep record details only if the exact records are part of the regression contract. Do not snapshot secrets or production PII.

### Exercise E — decide between tools

Choose a tool for each output: a CLI report, a dataframe with floating-point measures, a short value in the test itself, and a long text diff that reviewers want to inspect in a dedicated viewer.

**Solution:** plain golden file or Syrupy for CLI text; `pytest-regressions`/`pandas.testing` for dataframe values with explicit tolerances; `inline-snapshot` for a small in-source value; ApprovalTests for the long output if its reporter workflow fits the team. These are starting points, not mandatory one-to-one mappings.

## 12. Self-check with solutions

### 1. Why must CI never run with `--snapshot-update`?

Because CI would rewrite the expected baseline to match the current output, potentially allowing a regression to update its own oracle and pass. CI should compare code against committed snapshots and fail on unexplained differences. Developers can update baselines locally after reviewing diffs and then submit those changes for normal review. Keep update flags out of default `addopts` and CI commands.

### 2. Make a snapshot of a report that contains timestamps and UUIDs stable.

Inject a fixed clock and ID factory where possible. Otherwise, normalize only those fields to stable placeholders before snapshot comparison. Preserve their existence and shape, and add targeted assertions for validity if they are part of the contract. Do not remove the whole metadata object just to avoid changing values. The example in Section 4.3 demonstrates a narrow normalizer.

### 3. Replace a 60-line expected-JSON assertion with a snapshot plus two targeted assertions.

Create a JSON snapshot of the normalized response, then add two direct assertions for the most important invariants—for example, the schema version and non-negative row count. Remove fields from the snapshot only when they are truly volatile or irrelevant; if excluding a field means it is no longer checked, add an appropriate targeted assertion. This retains broad regression protection while making critical requirements explicit and reviewable.

## 13. Final review checklist

Before approving any snapshot change:

- [ ] The test's input is small, deterministic, and representative.
- [ ] The output is appropriate for a snapshot rather than a few explicit assertions.
- [ ] Volatile values are controlled or normalized narrowly.
- [ ] No secret, token, PII, or production-only data is included.
- [ ] Formatting, ordering, schema, and numeric tolerance policies are intentional.
- [ ] The diff is focused and every meaningful change is explained.
- [ ] Important invariants are asserted independently where appropriate.
- [ ] The baseline update was deliberate and run locally.
- [ ] CI uses ordinary comparison mode and cannot auto-approve changes.
- [ ] Unused snapshots and generated deletions have been investigated.
- [ ] Tests pass again without update flags.
- [ ] The commit message or PR description explains why the baseline changed.

## References

The roadmap defines the learning requirements; these official project references are for checking current tool APIs and version-specific behavior:

- [Syrupy documentation](https://syrupy-project.github.io/syrupy/)
- [Syrupy source and release compatibility notes](https://github.com/syrupy-project/syrupy)
- [pytest-regressions documentation](https://pytest-regressions.readthedocs.io/en/latest/)
- [pytest-regressions API reference](https://pytest-regressions.readthedocs.io/en/latest/api.html)
- [ApprovalTests for Python](https://github.com/approvals/ApprovalTests.Python)
- [inline-snapshot documentation](https://15r10nk.github.io/inline-snapshot/)
- [VCR.py documentation](https://vcrpy.readthedocs.io/en/latest/)
- [pytest-recording project](https://github.com/kiwicom/pytest-recording)
- [pandas testing utilities](https://pandas.pydata.org/docs/reference/api/pandas.testing.assert_frame_equal.html)
- [pytest documentation](https://docs.pytest.org/en/stable/)

**Version note:** snapshot libraries evolve independently. Confirm the exact command-line flags, extension classes, and fixture APIs against versions pinned in your project. Treat every baseline as reviewed test data, not generated build output.
