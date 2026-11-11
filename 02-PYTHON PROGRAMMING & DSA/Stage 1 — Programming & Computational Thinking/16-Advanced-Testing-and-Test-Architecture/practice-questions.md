# Practice Questions --- Module 1.16: Advanced Testing and Test Architecture

**Target baseline:** Python 3.12+, pytest 8+, coverage.py 7+. Use the
roadmap's tools where relevant: `pytest-cov`, `pytest-xdist`,
`pytest-randomly`, `mutmut`, Hypothesis, Syrupy, tox, and Nox.

## How to use this document

Attempt each question before reading the answer key. For code tasks,
write and run the test or configuration where possible. Answers describe
one defensible solution; equivalent designs are acceptable when they
preserve the stated contract, isolation, and reliability properties.

**Question count:** 35 substantive questions. The six exercises
explicitly titled **"Why is this test bad?"** are included in that
count, not added to it.

------------------------------------------------------------------------

# Questions

## Phase A --- Measuring Test Quality

### A1. Line coverage versus branch coverage --- code-reading puzzle

Consider:

``` python
def fee(amount: float, premium: bool) -> float:
    if premium:
        amount *= 0.8
    if amount < 0:
        raise ValueError("amount must be non-negative")
    return round(amount, 2)
```

A test suite calls `fee(100, True)` and `fee(100, False)`, but never
passes a negative amount. Which lines and branches have been exercised?
Explain why line coverage can look healthy while the rejection path
remains untested. Propose the smallest additional tests that cover the
meaningful branch outcomes without confusing coverage with correctness.

### A2. Coverage configuration and reporting --- hands-on

Write a `pyproject.toml` coverage configuration for package code under
`src/ledger`, with branch measurement enabled, missing lines shown, and
a minimum total coverage threshold of 90%. Give commands to run pytest
with coverage, print a terminal report, and generate an HTML report.
Explain when `coverage combine` is useful and name one legitimate and
one illegitimate use of `# pragma: no cover`.

### A3. What coverage cannot tell you --- test-design problem

This function has full line and branch coverage under the tests shown:

``` python
def is_valid_batch_size(size: int) -> bool:
    return size > 0

def test_sizes():
    assert is_valid_batch_size(1) is True
    assert is_valid_batch_size(-1) is False
```

A developer changes the implementation to `return size >= 0`; the tests
still pass for the current examples. Identify a missing case, write the
additional assertion, and explain the distinction between execution
coverage and specification coverage.

### A4. Mutation testing --- interpret the survivor

The original function is:

``` python
def is_adult(age: int) -> bool:
    return age >= 18
```

Tests only check ages 30 and 12. A mutation tool changes `>=` to `>` and
the mutant survives. Explain what a surviving mutant means, provide
boundary tests that should kill this mutant, and explain why an
equivalent mutant must be treated differently from a real surviving
defect.

### A5. Mutation score --- calculation and judgement

A `mutmut` run reports 50 mutants: 32 killed, 8 survived, 5 timed out,
and 5 were classified as equivalent after review. Calculate (a) the
simple killed/total score and (b) a score excluding the five documented
equivalent mutants if the denominator otherwise includes the timeouts.
State why the number alone is not enough to judge test quality, and
suggest how to handle timeouts in a report.

### A6. Coverage contexts and risk-based interpretation

A critical parser has 96% branch coverage, but a production incident
came from a malformed length field. Describe a targeted investigation
using missing-branch reports, test-to-line coverage contexts or
equivalent tooling, boundary tests, and mutation testing. Explain why
adding tests only to raise the percentage may fail to address the
incident.

### A7. **Why is this test bad? --- no meaningful assertion**

``` python
def test_normalize_record():
    normalize_record({"Name": "Ada", "AGE": "37"})
```

Explain what this test proves and does not prove. Rewrite it with
meaningful assertions for the expected output and at least one
invalid-input contract. If normalization mutates the input, state how
you would test that behavior explicitly.

### A8. Mutation-testing strategy at scale

A repository has 2,000 tests, including slow integration tests. Propose
a practical mutation-testing plan for a core pricing/validation module.
Address scope, fast test selection, caching or parallelism, CI cadence,
equivalent mutants, and how coverage and mutation results complement
each other. Include a reasonable interpretation of the roadmap's target
of at least 80% mutation score on core logic, excluding documented
equivalents.

------------------------------------------------------------------------

## Phase B --- Architecture of a Test Suite

### B1. Layered `conftest.py` design

A project has unit, integration, and CLI tests. Design a directory
layout for layered `conftest.py` files and describe which fixtures
belong at each level. Include one factory fixture, one per-test
isolation fixture, and one expensive resource fixture. Explain why tests
should not import helpers from `conftest.py` as if it were an ordinary
module.

### B2. Fixture scope and isolation --- diagnose the bug

``` python
CACHE = {}

@pytest.fixture(scope="session")
def cache():
    return CACHE

def test_insert(cache):
    cache["account"] = 42

def test_starts_empty(cache):
    assert cache == {}
```

Why can the suite fail depending on order? Give two possible repairs and
discuss the trade-off between resetting shared state and creating a
fresh object per test.

### B3. Markers and a custom pytest option --- coding exercise

Write the essential `conftest.py` code to register a `--run-integration`
option and automatically skip tests marked `integration` unless that
option is supplied. Show how to register the `integration` and `slow`
markers in `pyproject.toml`. Explain why strict marker checking is
useful. Include how pytest resolves fixture overrides by directory scope
and identify when `pytest_generate_tests` or `pytest_runtest_setup`,
`pytest_runtest_call`, and `pytest_runtest_teardown` are appropriate.

### B4. Plugin hooks and testing the plugin

Design a small pytest plugin that prints the ten slowest test calls in
the terminal summary. Identify appropriate hooks and the data that must
be collected. Explain how the `pytester` fixture can test the plugin in
isolation, including one expected assertion about the output. Avoid
depending on private pytest internals.

### B5. **Why is this test bad? --- order dependence**

``` python
REGISTRY = {}

def test_register():
    REGISTRY["alpha"] = object()

def test_registry_starts_empty():
    assert REGISTRY == {}
```

Identify the order dependency and give a repair that makes each test
independently reliable. Explain how `pytest-randomly` and `pytest-xdist`
can help reveal related problems, and why simply forcing an order is not
a fix.

### B6. Snapshot/golden-file stability

A CLI report includes a generated timestamp, a random run ID, absolute
temporary paths, platform-specific line endings, floating-point values,
and rows from a dictionary. The snapshot fails on every run even when
business behavior is unchanged. Describe a normalization strategy and a
review workflow. Explain why non-deterministic LLM output should not be
treated as an exact-output correctness snapshot without a record/replay
or evaluation strategy. State when a structured assertion is
better than snapshotting the whole output, and why CI should not
automatically update snapshots.

### B7. **Why is this test bad? --- giant snapshot**

A test stores a 900-line snapshot containing CLI help, report data,
environment details, timestamps, and debug logs in one expected-output
file. Every small change creates an enormous diff. Diagnose at least
three problems and propose a decomposition using focused snapshots and
explicit assertions. Explain what must still be reviewed before
accepting a snapshot update.

### B8. Fixture factories, parametrization, and markers

Write a small example of a factory fixture `make_record()` that returns
a callable for constructing independent records. Show how `pytest.param`
IDs and a marker could distinguish an invalid-data case. Explain when
parametrized fixtures are preferable to one large fixture with hidden
conditional behavior.

### B9. Test architecture review

A suite uses an autouse session fixture that starts a database, writes
to a fixed directory, and is required by almost every test. Propose a
refactor that improves startup time and isolation. Address fixture
scopes, explicit dependencies, `tmp_path`, worker-safe resources under
xdist, and the distinction between unit, integration, and end-to-end
tests.

------------------------------------------------------------------------

## Phase C --- Reliability and Determinism

### C1. Diagnose a flaky test

A test passes locally but fails intermittently in CI. It depends on a
real HTTP endpoint, sleeps for 0.2 seconds, uses a fixed port, and
shares a module-level cache. Give a root-cause investigation plan in the
order you would perform it. For each source of nondeterminism, propose
an isolation or synchronization technique and explain what failure
evidence to record.

### C2. **Why is this test bad? --- sleeps for coordination**

``` python
def test_worker_finishes():
    start_worker()
    time.sleep(0.1)
    assert worker.finished is True
```

Explain why this can fail both on fast and slow machines. Replace the
sleep-based coordination with a synchronization primitive and a bounded
wait. State how you would ensure the worker is cleaned up if the
assertion fails.

### C3. Patch the correct lookup target

Production module `billing.py` contains:

``` python
from gateway import charge

def settle(invoice):
    return charge(invoice.total)
```

Write a test patching the `charge` name used by `billing.settle`, not
the original name in `gateway`. Explain the import-binding rule behind
the patch target and how an incorrect target can make a test call the
real external dependency.

### C4. **Why is this test bad? --- patching the wrong lookup target**

``` python
# billing.py: from gateway import charge
def settle(invoice):
    return charge(invoice.total)

def test_settle(monkeypatch):
    monkeypatch.setattr("gateway.charge", lambda amount: "ok")
    assert billing.settle(invoice) == "ok"
```

Assume `billing` was imported before the patch. Explain why the test may
still call the original function and show the corrected patch target.
Describe one way to assert the exact amount passed to the fake.

### C5. CLI testing --- in-process and subprocess

A command `datadrop validate INPUT` returns exit code 0 for valid data,
2 for invalid input, writes diagnostics to stderr, and can encounter a
broken pipe when output is piped to a consumer that exits early. Design
a layered test plan covering `--help`, a missing file, an invalid flag,
valid and invalid input, subprocess smoke tests, and a broken-pipe test.
Include the subprocess APIs and assertions you would use; do not use
`os.system` or shell command strings.

### C6. Deterministic retries, time, and randomness

A retry function uses `time.sleep`, `datetime.now`, and random jitter.
Explain how you would inject or patch these dependencies at their lookup
boundaries. Sketch a test that verifies retry count and computed delays
without waiting in real time. Distinguish wall-clock time from monotonic
time and identify which is appropriate for measuring elapsed duration.

### C7. Threads and asynchronous work

A shared counter is incremented by multiple threads and occasionally
loses updates. Design a test that can expose the race without depending
on a single lucky schedule. Describe synchronization, repeated stress
runs, cleanup/join behavior, and the role and limits of assertions about
final state. Briefly explain how an async test should ensure created
tasks are awaited or cancelled.

### C8. **Why is this test bad? --- retries hide a race**

``` python
@pytest.mark.flaky(reruns=5)
def test_parallel_imports_all_rows():
    import_rows_concurrently(rows)
    assert count_rows() == len(rows)
```

Explain why rerunning the test can hide rather than fix the defect. Give
a better diagnostic and repair plan, including deterministic
synchronization, race reproduction, idempotency/transaction boundaries
if relevant, and a temporary quarantine policy that does not erase
ownership.

### C9. Resource failures, cleanup, and the mini-project's reliability bar

A CLI writes a partial report and then fails because the destination is
read-only or a downstream pipe closes. Propose tests for error messages,
exit codes, partial-output cleanup, and resource closure. Then describe
how you would run a suite 50 times with `pytest-randomly` and `xdist`,
capture a reproducible seed, and document root causes in `FLAKES.md`.

------------------------------------------------------------------------

## Phase D --- Scale and Safety Nets

### D1. Design a practical Nox matrix

Write a `noxfile.py` outline with test sessions for Python 3.12, 3.13,
and 3.14, plus separate lint, type-check, and build-check sessions.
Tests should accept forwarded pytest arguments. Explain which sessions
should install the package and why the matrix should not multiply every
dimension for every commit.

### D2. Dependency compatibility

A library declares `dependency>=2.4`, but tests only run against the
newest dependency release. Design a minimum-dependency job and a
latest-dependency job. Explain the purpose and limits of lowest-direct
dependency resolution, and how you would test optional extras without
creating an unmanageable matrix. Mention lock files' different roles for
reproducible application tests versus library compatibility tests.

### D3. Installed artifact versus source tree

A test passes from the repository root but fails when users install the
wheel. Explain how a `src/` layout helps, and outline a test that builds
a wheel, installs it into a fresh virtual environment, and runs tests
outside the source checkout. Include what you would verify for the wheel
and sdist, and how `twine check` fits in.

### D4. Broad exception swallowing in a fuzz harness --- code review

``` python
def TestOneInput(data):
    try:
        parse(data)
    except Exception:
        pass
```

Although this is not one of the six required roadmap diagnostic
categories, analyze this code as a safety-net design problem: what
genuine bugs can it hide? Rewrite the harness to catch only the parser's
documented rejection exception and preserve unexpected exceptions for
the fuzzer. Explain why expected malformed-input rejection and an
unexpected `TypeError` must be treated differently.

### D5. Fuzzing harness and oracle

The following length-prefixed parser is deliberately flawed: it trusts
the declared payload length even when the input is truncated.

``` python
class ParseError(ValueError):
    pass

def parse_frame(data: bytes) -> bytes:
    if len(data) < 2:
        raise ParseError("missing length header")
    declared = int.from_bytes(data[:2], "big")
    return data[2:2 + declared]  # defect: silently accepts truncated payloads
```

Identify an input that demonstrates the defect, then correct the parser
with a documented maximum payload length and exact-length validation.
Design bounded Hypothesis tests and/or an Atheris harness. Include byte
inputs and text inputs when a text API exists, the documented rejection
exception, at least two oracles (such as no unexpected exception and a
round-trip property), and a regression test for the exact failing bytes.
Explain instrumentation, seed corpora/dictionaries, minimization, and
how raw byte mutation differs from structure-aware strategies. Do not
perform network or destructive filesystem operations in the harness.

### D6. Test matrix and CI budget

A project supports three Python versions, two operating systems,
minimum/latest dependencies, and two optional extras. The full Cartesian
matrix has 24 combinations before test types are considered. Propose a
staged strategy for pull requests and scheduled jobs. Explain how smoke
tests, a selected full-test subset, nightly long-tail jobs, coverage
combination, and a non-blocking experimental job can control cost
without silently dropping compatibility risks.

### D7. Native extensions, sanitizer awareness, and fuzzing policy

A Python package wraps C code and exposes a stateful cache API; the
service also publishes an OpenAPI schema. Describe what Python-level
fuzzing can find and what it cannot reliably detect without native
instrumentation. Explain ASan/UBSan, corpus seeding/minimization, and
continuous fuzzing systems such as OSS-Fuzz or ClusterFuzzLite. Explain
when Hypothesis RuleBasedStateMachine is appropriate for operation
sequences and what Schemathesis contributes when fuzzing an OpenAPI
service. Propose a short ownership policy for harnesses, corpora,
resource budgets, and regression cases.

### D8. Differential and metamorphic tests for data/ML pipelines

Two JSON implementations parse the same records, and a data aggregation
should be invariant to row order. Design one differential test and one
metamorphic test. Explain how to distinguish legitimate differences in
documented semantics from a defect, and why a fuzzer that only asserts
"does not crash" cannot prove aggregate correctness.

### D9. Mini-project acceptance review

For the `ledger`/`datadrop` test-hardening mini-project, list the
required deliverables and acceptance thresholds. Your answer must cover:
baseline line and branch coverage; branch coverage at least 90%; core
mutation score at least 80% excluding documented equivalents; layered
fixtures, markers, `--run-integration`, and a slow-test summary; stable
snapshots; 50 randomized/parallel runs with zero remaining flaky tests;
CLI exit-code and broken-pipe tests; injected retry dependencies and a
threaded-counter race test; Nox sessions for Python 3.12--3.14, lint,
type, build, and lowest dependencies; fuzz regression cases; and README
testing instructions.

------------------------------------------------------------------------

# Answer Key and Explanations

## Phase A --- Measuring Test Quality

### A1. Answer

The `premium=True` branch is exercised by the first call and
`premium=False` by the second. Both calls exercise the non-negative
return path. The `amount < 0` true branch and `ValueError` path are not
exercised. Add, at minimum, a negative amount test for the exception
path, and retain both premium values. For example:

``` python
import pytest

@pytest.mark.parametrize("premium, expected", [(True, 80.0), (False, 100.0)])
def test_fee_for_nonnegative_amount(premium, expected):
    assert fee(100, premium) == expected

def test_fee_rejects_negative_amount():
    with pytest.raises(ValueError, match="non-negative"):
        fee(-1, False)
```

Coverage tells you which paths ran. The assertions and chosen examples
determine whether the behavior is adequately specified. For the negative
amount case, the `premium=True` combination may also be relevant if
transformations could alter validation semantics; here a negative amount
remains negative.

### A2. Answer

One suitable configuration:

``` toml
[tool.coverage.run]
source = ["src/ledger"]
branch = true

[tool.coverage.report]
show_missing = true
fail_under = 90
```

Commands:

``` bash
uv run pytest --cov=ledger --cov-branch --cov-report=term-missing
uv run coverage report -m
uv run coverage html
```

When measured coverage falls below `fail_under`, the coverage report
returns a failing status suitable for CI; confirm the chosen pytest-cov
command propagates that status in the project's CI runner. If coverage
contexts are enabled (for example, `dynamic_context = "test_function"`),
they can show which test covers a line. If coverage is configured to
collect parallel data, or data files are produced by separate matrix
sessions, `coverage combine` merges compatible coverage data before
reporting. A legitimate
`# pragma: no cover` can exclude a genuinely unreachable defensive
branch with a documented rationale. An illegitimate use is excluding a
reachable error-handling path merely because it is difficult to test or
lowers the percentage.

### A3. Answer

Add the boundary value zero:

``` python
def test_zero_is_not_a_valid_batch_size():
    assert is_valid_batch_size(0) is False
```

The current examples do not distinguish `size > 0` from `size != 0`;
zero is the discriminating input. Coverage measures executed code paths,
not whether tests distinguish the intended implementation from plausible
incorrect implementations. The function's specification should
explicitly say whether zero is invalid, and tests should include that
boundary.

### A4. Answer

A surviving mutant means the test suite did not detect the introduced
change under the tested scenarios; it may indicate a missing assertion
or boundary case, though the mutant might be equivalent for the actual
specification. Add:

``` python
def test_age_17_is_not_adult():
    assert is_adult(17) is False

def test_age_18_is_adult():
    assert is_adult(18) is True
```

The `age == 18` test kills the `>` mutant because the mutant returns
`False` at the threshold. Tests at ages 17 and 19 make the rejection and
acceptance sides of the boundary explicit as well. An equivalent mutant does not change observable behavior under
the defined contract and should be documented and excluded from the
meaningful-mutant denominator rather than "fixed" by a contrived test.

### A5. Answer

(a) Simple score using all 50 reported mutants: (32/50 = 64%).

(b) Excluding the five documented equivalent mutants while retaining the
    timeouts in the denominator gives
    (32/(50-5) = 32/45 ≈ 71.1%). State explicitly that timeout
    handling depends on the tool's reporting convention; timeouts are
    not automatically killed and should be reported separately as
    inconclusive or suspicious. A single score can hide whether
    survivors cluster in critical validation logic, whether many mutants
    time out, or whether equivalent mutants were classified
    consistently. Review survivors and timeouts, and document the
    denominator used.

### A6. Answer

Start with branch-aware coverage output and identify the untested
branches around length validation. If coverage contexts are enabled,
determine which tests exercise each relevant line and whether the
incident path is asserted meaningfully. Add tests for missing, negative,
too-small, too-large, and inconsistent length fields according to the
parser contract. Run mutation testing on the parser to see whether
changes to length comparisons or validation order survive. A higher
percentage alone does not guarantee that assertions detect the defect;
tests must distinguish correct from incorrect behavior.

### A7. Answer

The test proves only that `normalize_record` returns control without
raising an exception for that input. It does not check the normalized
result, its types, or any mutation contract. Example:

``` python
def test_normalize_record():
    record = {"Name": "Ada", "AGE": "37"}
    result = normalize_record(record)
    assert result == {"name": "Ada", "age": 37}

def test_normalize_record_rejects_invalid_age():
    with pytest.raises(ValueError):
        normalize_record({"Name": "Ada", "AGE": "unknown"})
```

Adjust the expected keys and exception to the actual public contract. If
the function promises in-place mutation, assert the original object
changed as specified. If it promises a new mapping and preserves input,
assert the original remains unchanged. The contract must decide; do not
guess from the function name.

### A8. Answer

Mutate only the core pricing/validation module first; run fast unit
tests selected by coverage where supported; parallelize or cache when
reliable; review survivors and timeouts; document equivalent mutants.
For example, scope `mutmut` to the core module (`uv run mutmut run
--paths-to-mutate src/ledger/pricing.py`) and inspect survivors with
`uv run mutmut results` / `uv run mutmut show <id>`; confirm exact flags
against the installed mutmut version. Run focused mutation checks on pull
requests when affordable and broader or nightly runs for expensive
modules. Add boundary and negative tests
for surviving logic mutants. The ≥80% target is a project acceptance
threshold for the core module, not proof that every defect is caught.
Pair mutation results with branch coverage, test review, property tests,
and incident history.

------------------------------------------------------------------------

## Phase B --- Architecture of a Test Suite

### B1. Answer

A reasonable layout:

``` text
tests/
  conftest.py                 # common lightweight factories/configuration
  unit/
    conftest.py               # unit-only fixtures
    test_*.py
  integration/
    conftest.py               # integration resources and cleanup
    test_*.py
  cli/
    conftest.py               # CLI helpers
    test_*.py
```

The root file can define a `make_record` factory fixture and shared
immutable sample data. Unit tests should create fresh objects per test.
Integration fixtures may start an expensive service only for integration
tests and must guarantee teardown with `yield`/finalizers. CLI fixtures
can prepare isolated temporary directories. Pytest discovers
`conftest.py` fixtures by directory scope; importing from it as a normal
module creates fragile import paths and bypasses pytest's
fixture-discovery model. Move reusable ordinary helper functions into a
normal module under `tests` if they truly need imports.

### B2. Answer

`cache` returns the same process-global dictionary for every test. After
`test_insert`, `test_starts_empty` fails; order changes the outcome.
Repairs include creating a fresh dictionary per test:

``` python
@pytest.fixture
def cache():
    return {}
```

or explicitly clearing/restoring the shared cache before and after each
test. Fresh per-test objects are simpler and more isolated. Resetting is
appropriate when the real behavior depends on a singleton or shared
registry, but cleanup must also happen if the test fails, and concurrent
tests must not share mutable state accidentally.

### B3. Answer

One implementation:

``` python
# conftest.py
import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )

def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-integration"):
        return
    skip = pytest.mark.skip(reason="pass --run-integration to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)
```

Register markers:

``` toml
[tool.pytest.ini_options]
addopts = "--strict-markers"
markers = [
  "integration: requires integration resources",
  "slow: long-running test",
]
```

Strict marker checking catches typos and unregistered markers early,
preventing intended selection or skip behavior from silently failing.
Pytest searches applicable `conftest.py` files from the test directory
upward; nearer fixtures can override broader ones. Use
`pytest_generate_tests` for collection-time dynamic parametrization, and
setup/call/teardown hooks only when a plugin truly needs lifecycle-wide
behavior rather than a normal fixture.

### B4. Answer

Use `pytest_runtest_makereport` to record duration when a test call
report is produced (or another supported hook that has start/stop
timing), then `pytest_terminal_summary` to sort and print the ten
slowest calls. Keep only stable data such as node ID and elapsed
seconds; avoid private pytest internals. The `pytester` fixture can
create a temporary test file and load the plugin, run pytest, and assert
the summary contains the expected slow test name and the heading. Plugin
tests should also cover no tests, fewer than ten tests, and
deterministic ordering for equal durations where feasible. Timing tests
should use tolerances or injected data rather than asserting exact real
durations.

### B5. Answer

The first test leaves a global entry that changes the starting state for
the second test. Make the registry fixture-scoped and fresh, or restore
its prior contents in a fixture's teardown:

``` python
@pytest.fixture
def registry(monkeypatch):
    local_registry = {}
    return local_registry

def test_register(registry):
    registry["alpha"] = object()
    assert "alpha" in registry

def test_registry_starts_empty(registry):
    assert registry == {}
```

`pytest-randomly` changes order and can expose hidden dependencies;
record its seed (for example, `--randomly-seed=1234`) so the order can be
reproduced. `pytest-xdist` introduces process/worker variation and
exposes unsafe shared resources or assumptions; repeated runs and a
minimal failing test help isolate the cause, but neither tool guarantees
every race will be found. Forcing a fixed order hides the coupling rather than removing
it.

### B6. Answer

Normalize or inject volatile values at the boundary: freeze/inject time,
replace generated IDs with a stable placeholder, normalize temporary
paths and line endings, round/compare floats according to the contract,
sort rows by a documented key, and remove debug/environment data from
the contract snapshot. For LLM pipelines, prefer recorded/replayed
fixtures or task-specific evaluations over assuming live model output is
byte-for-byte deterministic. Keep a focused snapshot for CLI help and
another for stable report output; use explicit assertions for important
fields such as row count, totals, and schema. Review diffs in version
control and update snapshots deliberately with the change rationale. CI
should never auto-approve a new expected output because that could
silently bless a regression.

### B7. Answer

Problems include: unrelated outputs are coupled; volatile fields cause
noisy failures; a huge diff hides meaningful changes; environment/debug
details become accidental contract; reviewers may approve updates
blindly. Split into focused snapshots (help text, stable report section)
and explicit assertions for totals, schema, and exit behavior. Normalize
volatile values first. Before accepting an update, inspect the diff,
verify the changed behavior is intended, check for secrets/PII, and
confirm the snapshot still covers a useful contract.

### B8. Answer

Example:

``` python
import pytest

@pytest.fixture
def make_record():
    def factory(name="Ada", age=37):
        return {"name": name, "age": age}
    return factory

@pytest.mark.parametrize(
    "record, valid",
    [
        pytest.param({"name": "Ada", "age": 37}, True, id="valid-record"),
        pytest.param({"name": "", "age": -1}, False, id="invalid-record",
                     marks=pytest.mark.slow),
    ],
)
def test_record_validation(record, valid):
    assert validate_record(record) is valid
```

A factory makes independent values and keeps setup readable.
Parametrization is useful when the same behavior must be checked against
a table of inputs. Use a parametrized fixture when setup itself has a
finite set of meaningful configurations; avoid a giant fixture with
hidden conditionals that obscure what each test needs.

### B9. Answer

Move database startup into an explicit integration fixture used only by
integration tests; use a factory or in-memory substitute for unit tests.
Replace fixed paths with `tmp_path` and use `yield` teardown for
services and files. Under xdist, allocate per-worker database/schema
names and ports or use a service designed for isolated workers. Keep
unit tests fast and in-process; integration tests exercise component
boundaries; end-to-end tests cover a small number of packaged, realistic
workflows. Explicit fixture dependencies make setup cost and
requirements visible.

------------------------------------------------------------------------

## Phase C --- Reliability and Determinism

### C1. Answer

First capture the exact failing test, seed, worker ID, platform, logs,
and failure timing. Re-run the test in isolation, then with randomized
order and parallel execution. Replace the real HTTP endpoint with a
fake/local server or recorded contract; use an ephemeral port rather
than a fixed port; replace sleep-based coordination with
events/conditions and bounded deadlines; reset or scope the cache per
test. Reproduce before changing multiple variables. Record the root
cause and regression test in `FLAKES.md`, not merely that a rerun
passed.

### C2. Answer

The worker may need longer than 0.1 seconds under load, or may finish
before the test checks it; the sleep does not establish synchronization.
Use an event or future with a timeout:

``` python
def test_worker_finishes():
    finished = threading.Event()
    worker = start_worker(on_finished=finished.set)
    try:
        assert finished.wait(timeout=2.0)
    finally:
        worker.join(timeout=2.0)
        assert not worker.is_alive()
```

This assumes `start_worker` accepts a completion callback and returns a
joinable thread; adapt the interface if needed. The timeout bounds the
wait, and `finally` ensures cleanup even when the assertion fails. Avoid
asserting exact scheduling time.

### C3. Answer

Patch `billing.charge`, because `billing.py` imported the object into
its own namespace:

``` python
from types import SimpleNamespace

def test_settle(monkeypatch):
    import billing
    seen = []
    monkeypatch.setattr(
        billing, "charge", lambda amount: seen.append(amount) or "ok"
    )
    invoice = SimpleNamespace(total=125)
    assert billing.settle(invoice) == "ok"
    assert seen == [125]
```

When `from gateway import charge` executes, `billing.charge` becomes the
name looked up by `settle`. Patching `gateway.charge` after `billing`
has imported it does not replace that existing binding.

### C4. Answer

The test patches `gateway.charge`, but `billing.settle` looks up the
already-bound `billing.charge`. Patch the lookup site:

``` python
seen = []
monkeypatch.setattr(billing, "charge", lambda amount: seen.append(amount) or "ok")
assert billing.settle(invoice) == "ok"
assert seen == [invoice.total]
```

If the real `gateway.charge` is invoked, the test may make an external
call or fail for environmental reasons. Assertions on `seen` verify the
exact argument, not just the return value.

### C5. Answer

Test `main([...])` in-process for `--help`, parsing, a missing file, an
invalid flag, validation, output, and returned status (or the documented
`SystemExit` contract). Use `capsys`/`capfd` to inspect stdout/stderr;
assert the documented exit code for each outcome. Add subprocess smoke tests
with
`subprocess.run(
    [sys.executable, "-m", "datadrop", "validate", str(path)],
    capture_output=True, text=True, timeout=10, check=False,
)`
and assert `returncode`, stdout, and stderr. For broken pipe, use a
controlled subprocess pipeline or a small helper process that closes its
read end; assert the program exits according to its documented policy
and does not emit an uncontrolled traceback. Avoid shell strings and
`os.system`; use argument lists and explicit timeouts.

### C6. Answer

Inject a clock function, a sleep function, and a jitter/random source as
arguments or patch names where the retry module looks them up. Use fakes
that record calls rather than waiting:

``` python
def test_retry_delays():
    delays = []
    sleeps = []
    attempts = 0

    def fake_sleep(seconds):
        sleeps.append(seconds)

    def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise TemporaryError
        return "ok"

    result = retry(operation, sleep=fake_sleep, jitter=lambda: 0.0)
    assert result == "ok"
    assert attempts == 3
    assert sleeps == [1.0, 2.0]  # for a contract using exponential base delays
```

This assumes the retry contract uses 1- and 2-second base delays and
zero jitter; align expectations to the actual function signature. Use
wall-clock timestamps for calendar meaning and a monotonic clock for
elapsed durations because wall clocks can jump due to synchronization or
manual changes.

### C7. Answer

Use a barrier or events to align worker starts, run enough iterations to
increase the chance of interleavings, and assert the final count equals
the number of successful increments. Always join threads in teardown and
fail if a thread remains alive. A stress test is probabilistic and may
not expose the race on every run; a deterministic test hook or deliberately
controlled interleaving is stronger when practical. It does not prove race freedom; use explicit locking or a thread-safe design and
test the invariant. Async tests should await tasks, or cancel and gather
them in cleanup, so failures and exceptions are not lost and tasks do
not leak into later tests.

### C8. Answer

Retries can make the test green without removing the underlying race and
can hide how often it occurs. First capture failing seeds, logs, and
worker context; reproduce with controlled scheduling; inspect shared
mutable state, transaction boundaries, and idempotency. Add
barriers/events or deterministic hooks to force the risky interleaving,
then repair locking/atomicity/transaction logic and keep a regression
test. Quarantine only temporarily, with an owner, issue, expiry/review
date, and explicit reporting; reruns are diagnostic evidence, not the
fix.

### C9. Answer

Use temporary directories and permissions controlled by the test; assert
the documented error message and nonzero exit code, and check that
partial outputs are removed or marked incomplete according to the
contract. For a broken pipe, verify graceful shutdown and resource
closure. Use context managers and `finally` cleanup. Run repeated
randomized/parallel tests with the project's chosen command, for
example:

``` bash
uv run pytest --randomly-seed=1234 -n auto
```

For repeated runs, use a loop or CI job to run the suite 50 times,
recording each seed and exit status; do not assume one seed covers all
orders. Record root cause, reproduction command, affected tests, and fix
in `FLAKES.md`.

------------------------------------------------------------------------

## Phase D --- Scale and Safety Nets

### D1. Answer

One possible outline:

``` python
import nox

@nox.session(python=["3.12", "3.13", "3.14"])
def tests(session):
    session.install("-e", ".[test]")
    session.install("pytest", "pytest-cov")
    session.run("pytest", *session.posargs)

@nox.session
def lint(session):
    session.install("ruff")
    session.run("ruff", "check", ".")

@nox.session
def typecheck(session):
    session.install("-e", ".[test]", "mypy")
    session.run("mypy", "src")

@nox.session
def buildcheck(session):
    session.install("build", "twine")
    import shutil
    from pathlib import Path
    shutil.rmtree("dist", ignore_errors=True)  # avoid checking stale artifacts
    session.run("python", "-m", "build")
    artifacts = sorted(Path("dist").glob("*"))
    if not artifacts:
        session.error("Build produced no artifacts in dist/")
    session.run("twine", "check", "--strict", *(str(p) for p in artifacts))
```

The test sessions install the package and test extras so tests use an
intentional environment. Lint can skip package installation if it only
inspects source. A build-check should build distribution artifacts. A
large Cartesian matrix can be split into fast pull-request smoke jobs
and scheduled full compatibility jobs; retain clear ownership for the
combinations not run on each commit.

### D2. Answer

Run one session with the lowest supported direct dependency versions
(for example, `uv pip install --resolution lowest-direct ...`) and
another with current/latest compatible versions. Lowest-direct
resolution tests declared direct dependency lower bounds, but transitive
dependencies may still resolve differently and the command does not
replace explicit constraints or a lockfile strategy. Test high-value
extras such as `.[pandas]` in selected jobs and include each extra in at
least one scheduled compatibility run. Locked environments help
reproduce application behavior; libraries also need
unlocked/minimum/latest jobs to discover compatibility issues across
supported dependency ranges.

### D3. Answer

A `src/` layout prevents repository-root imports from accidentally
finding the package before the installed artifact. Build with
`python -m build`, create a fresh virtual environment outside the
checkout, install the wheel, and run tests from a temporary directory
with no source-tree path on `sys.path`. Verify import location, version,
package data, and entry points. Also install and smoke-test the sdist
where feasible, since it must contain the files needed to build the
wheel. `twine check dist/*` checks distribution metadata and
long-description rendering; it does not replace installation tests.

### D4. Answer

A broad `except Exception` catches programmer defects such as
`TypeError`, `AttributeError`, and unexpected `ValueError`, making the
fuzzer report malformed input as harmless. Catch only the parser's
documented rejection exception:

``` python
def TestOneInput(data: bytes) -> None:
    try:
        parse(data)
    except ParseError:
        return  # documented invalid-input rejection
```

Do not catch unexpected exceptions; let them escape so the test/fuzzer
identifies them. The parser's contract should distinguish malformed user
input from implementation bugs. This exercise is a diagnostic safety-net
design question; the roadmap's six required "Why is this test bad?"
exercises are the six designated in Phases A--C.

### D5. Answer

The defect is demonstrated by `parse_frame(b"\x00\x03ab")`: the header
claims three payload bytes, but only two are present, and the flawed
implementation silently returns `b"ab"`. A corrected parser must reject
that input rather than silently truncating it:

``` python
MAX_PAYLOAD = 2048

class ParseError(ValueError):
    pass

def parse_frame(data: bytes) -> bytes:
    if len(data) < 2:
        raise ParseError("missing length header")
    declared = int.from_bytes(data[:2], "big")
    if declared > MAX_PAYLOAD:
        raise ParseError("payload too large")
    if len(data) != 2 + declared:
        raise ParseError("length mismatch")
    return data[2:]

import pytest

def test_truncated_length_prefixed_payload_is_rejected():
    with pytest.raises(ParseError, match="length mismatch"):
        parse_frame(b"\x00\x03ab")
```

For property-based testing, cap generated input size and only treat the
parser's documented rejection exception as expected. If a text API is
part of the contract, exercise it separately with bounded Unicode text:

``` python
from hypothesis import given, strategies as st

@given(st.binary(max_size=2050))
def test_binary_parser_has_no_unexpected_exception(data):
    try:
        parse_frame(data)
    except ParseError:
        pass  # documented malformed-input rejection

@given(st.text(max_size=512))
def test_text_parser_has_no_unexpected_exception(text):
    try:
        parse_text(text)
    except ParseError:
        pass  # only if ParseError is the documented rejection type
```

This is a crash-resistance oracle, not a semantic correctness oracle. Do
not catch `Exception`, `BaseException`, `AssertionError`, or timeouts as
normal malformed-input outcomes: only the documented rejection exception
is expected. Configure an external process-level timeout and memory/CPU
budget for potentially hostile inputs; an input-size cap alone cannot
guarantee bounded execution. Add a round-trip property over valid generated values:
`parse(serialize(value)) == value`. The corrected parser rejects a missing
header, a declared payload above `MAX_PAYLOAD`, a truncated payload, and
trailing bytes that violate its strict framing contract. Include boundary
cases for oversized or inconsistent length fields. Consider recursion
and decompression expansion limits, catastrophic regular-expression
behavior (ReDoS), and parsers of archives, images, serialized records,
and prompt/tool-call formats when those surfaces exist in the project.
A quick hand-rolled baseline can use `random.Random(0)` to generate a
repeatable set of byte strings with lengths capped at 2050; use Hypothesis
when shrinking and strategy composition are valuable. Raw byte mutation is
cheap but often produces inputs rejected at the first parser check;
structure-aware strategies generate more valid headers/payloads. For
Atheris, define `TestOneInput(data: bytes)`, instrument the target import
with `atheris.instrument_imports()` where supported, and seed the corpus
with valid records, malformed boundaries, and regression inputs. A
dictionary of meaningful tokens or field markers can help structured
formats (`-dict=path` is a libFuzzer-style option). A minimal runner ends
with `atheris.Setup(sys.argv, TestOneInput)` and `atheris.Fuzz()`; launch
it with a corpus directory, for example `python fuzz_parser.py corpus/`.
Keep the harness fast and deterministic, and avoid I/O/network/global
accumulation. `python-afl` is an alternative
to recognize, but its instrumentation and launch workflow differs from
Atheris; do not mix their commands. When a failure occurs, preserve the
original bytes, minimize with Hypothesis or the fuzzer's corpus
minimizer, classify it, and add a deterministic regression test
containing the exact minimized input and expected outcome. Use
process-level time and memory limits for potentially hostile parsers; an
input-size cap alone cannot guarantee bounded execution.

### D6. Answer

On pull requests, run a smoke test across every supported Python version
on the primary OS and a smaller representative set of
OS/dependency/extra combinations. Run full tests on the main supported
combination and key compatibility extremes. On a schedule, cover all 24
combinations and longer tests. Combine compatible coverage data from
separate jobs before reporting when using matrix/parallel collection.
Keep experimental free-threaded/JIT jobs non-blocking until their status
is explicitly promoted. Add separate performance sessions (for example,
`pytest-benchmark` with reviewed baselines) and security sessions
(`pip-audit`, `bandit`). If system libraries such as OpenSSL or libpq are
required, provision them explicitly in the CI image/container; a Python
virtual environment does not install OS-level dependencies. Publish which
combinations run on each cadence; do not let cost reduction silently
eliminate minimum-dependency or OS coverage.

### D7. Answer

Python-level fuzzing finds Python exceptions, incorrect validation,
logic errors, and some resource pathologies. It cannot reliably detect
native memory-safety defects without native instrumentation. ASan helps
detect memory errors such as out-of-bounds access/use-after-free; UBSan
detects classes of undefined behavior in instrumented native code. Build
compatible native dependencies with sanitizers, then drive them from the
Python harness. Keep seed corpora small, representative, reviewed,
minimized, and free of sensitive data. Continuous fuzzing systems can
run campaigns and retain crash artifacts; CI can run bounded smoke
campaigns. A policy should name each harness owner, target and oracle,
corpus location, CPU/time/memory budget, triage SLA, and requirement to
add regression tests for confirmed findings. Use Hypothesis
`RuleBasedStateMachine` to generate sequences such as
insert/read/delete/reset and assert invariants after each operation. Use
Schemathesis to exercise an HTTP API from its OpenAPI schema, with an
isolated test environment and safe resource limits; it complements
rather than replaces unit tests.

### D8. Answer

Differential test: parse the same valid and invalid corpus with both
JSON implementations and compare normalized results or documented
exception categories. Do not assume exact error messages must match
unless that is part of the contract. Metamorphic test: aggregate a
dataset, permute row order, aggregate again, and assert equality when
the aggregation is specified as order-independent:

``` python
def test_aggregate_invariant_to_row_order():
    rows = [
        {"account": "a", "amount": 3},
        {"account": "b", "amount": 5},
        {"account": "a", "amount": 7},
    ]
    expected = aggregate(rows)
    permuted = rows[1:] + rows[:1]
    assert aggregate(permuted) == expected
```

For floating-point reductions, use a documented tolerance if order can
change rounding. A no-crash oracle says only that the input did not
trigger a detected crash; it cannot prove the computed aggregate is
correct or invariant.

### D9. Answer

Required deliverables: recorded line/branch coverage baseline; at least
90% branch coverage; core mutation score target of at least 80%
excluding documented equivalent mutants; layered `conftest.py`;
registered `slow` and `integration` markers; `--run-integration`; a
plugin/summary for the ten slowest tests; stable snapshots for CLI help
and report output with volatile fields masked; 50 randomized/parallel
runs with zero remaining flaky tests and root causes documented in
`FLAKES.md`; in-process and subprocess CLI tests covering exit codes and
broken pipe; injected clock/sleep/random dependencies and deterministic
retry/back-off tests; a threaded-counter race test; Nox tests for Python
3.12--3.14, lint, type checking, build check, and lowest dependencies;
fuzz harness plus regression corpus/cases; and README "Testing"
instructions for each layer. Acceptance is not just green CI: results
and commands must be reproducible and the README must explain how to run
them.

------------------------------------------------------------------------

# Final self-assessment

Before considering the module complete, confirm that you can:

-   Explain line versus branch coverage and why 100% coverage is not
    proof of correctness.
-   Interpret mutation survivors, timeouts, equivalent mutants, and the
    ≥80% core-module target.
-   Design layered fixtures, markers, custom options, plugin hooks, and
    plugin tests.
-   Keep snapshots stable, focused, reviewable, and free of secrets or
    volatile data.
-   Reproduce flaky tests, control time/randomness/concurrency, and
    remove order dependence.
-   Test CLI behavior in-process and as a subprocess, including exit
    codes, broken pipes, and cleanup.
-   Design a practical Nox matrix and verify minimum dependency claims
    and installed artifacts.
-   Build a safe fuzz harness with explicit oracles, bounded
    inputs/resources, and regression cases.
-   Complete the module mini-project with the roadmap's acceptance
    thresholds and a useful README testing guide.
