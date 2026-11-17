# Roadmap — Module 1.16: Advanced Testing and Test Architecture

This is the learning roadmap for the sixteenth module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
about professional-grade testing, **in what order**, **how** to practise each
topic, and **how to prove to yourself** that you have learned it.

Module 1.7 taught you to write tests (pytest, fixtures, parametrization,
mocking) and to debug. This module is about **trusting your test suite**:
Are the tests meaningful or just green? Do they fail when the code is
wrong? Are they fast, isolated and deterministic? Can they run across Python
versions and in CI? A test suite that is flaky, slow, or covers lines without
checking behaviour is worse than useless — it gives false confidence. In AI
engineering this matters even more: pipelines, prompts, parsers and
evaluation code all need reliable tests before any model quality can be
measured.

Property-based testing with Hypothesis and CI pipelines are covered in
Stage 2 (`Python for Data Engineering_1`, modules 18–19) and in the
Evaluation stage; this module covers the Python-level skills those build on
and **does not repeat them**.

> Target: **pytest 8+**, Python 3.12+, `coverage.py` 7+.

---

## 1. Module outcome

By the end of this module you will be able to:

- Measure line **and branch** coverage, read reports, enforce thresholds, and
  explain why 100 % coverage does not mean correct code.
- Use **mutation testing** to measure the real strength of your assertions.
- Structure a large test suite: `conftest.py` layering, fixture scopes,
  factories, markers, custom plugins and hooks.
- Write snapshot / golden-file tests that are reviewable and stable.
- Diagnose and eliminate flaky tests; isolate global state, time, network and filesystem.
- Test command-line programs and subprocesses end to end.
- Test code that depends on time, randomness and concurrency deterministically.
- Run tests across Python versions and dependency sets with `tox`/`nox`.
- Apply fuzzing basics to find crashes and security bugs in parsers.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Test levels, pytest basics, fixtures, parametrization | Module 1.7 (01–04) | This module extends them |
| Debuggers, tracebacks, minimal reproductions | Module 1.7 (05, 06) | Diagnosing flaky tests |
| Mocking and test doubles | Module 1.7 (07) | Isolation techniques |
| CLI programs, exit codes | Module 1.5 (06, 07) | CLI testing |
| Context managers, decorators | Module 1.9 (02, 03) | Fixtures and plugins |
| Standard library toolkit (`subprocess`, `tempfile`, `random`) | Module 1.13 | Test utilities |
| Packaging and project layout | Module 1.6 (02, 03) | `tox`/`nox` matrices |
| Metaprogramming basics | Module 1.12 | How pytest collects and rewrites asserts |

**Tools:** `uv add --dev pytest pytest-cov pytest-xdist pytest-randomly mutmut hypothesis syrupy tox nox`
(install only as each lesson requires).

---

## 3. How the module is organised

```text
Phase A — Measuring Test Quality                 (Basics → Intermediate)
  01 coverage: line, branch and what it means
  02 mutation testing
Phase B — Architecture of a Test Suite           (Intermediate)
  03 pytest plugins, hooks and conftest architecture
  04 snapshot and golden-file testing
Phase C — Reliability and Determinism            (Advanced)
  05 flaky tests and isolation
  06 testing CLI and subprocess programs
  07 testing time, randomness and concurrency
Phase D — Scale and Safety Nets                  (Advanced)
  08 test matrices with tox and nox
  09 fuzzing basics
```

Pace: about 2–3 weeks part-time. Each lesson builds on one shared
sample project (`ledger/` from Module 1.7, or a new small package).

---

## Lesson 01 — `01-coverage-line-branch-and-what-it-really-means.md`

**Why it matters.** Coverage tells you what code your tests *executed*, not
whether they *verified* anything. Used right it finds untested paths; used as
a vanity metric it encourages meaningless tests.

### Basic — what to learn

- Install and run: `coverage run -m pytest`, `coverage report -m`, `coverage html`,
  or `pytest --cov=src --cov-report=term-missing`.
- Reading a report: statements, missed lines, percentages.
- **Line coverage vs branch coverage** (`--cov-branch` / `branch = true`):
  `if x:` without a test for the `False` path has 100 % line but not branch coverage.

```python
def discount(price: float, member: bool) -> float:
    if member:
        price *= 0.9
    return price

def test_member():                # line coverage: 100 %, branch coverage: 75 %
    assert discount(100, True) == 90
```

### Intermediate — what to learn

- Configuration in `pyproject.toml`: `[tool.coverage.run]` (`source`, `branch`,
  `omit`, `parallel`, `concurrency`), `[tool.coverage.report]` (`fail_under`, `exclude_lines`, `show_missing`).
- `# pragma: no cover` — acceptable uses (defensive unreachable branches,
  `if TYPE_CHECKING`, `__main__` guards) and misuse.
- Combining data from parallel runs / multiple Python versions: `coverage combine`.
- Coverage in subprocesses and multiprocessing (`COVERAGE_PROCESS_START`, `sitecustomize`/`.pth`
  or `patch = subprocess`).
- Differential coverage: only enforce on changed lines (`diff-cover`) for legacy codebases.
- Uploading reports to CI services; badges are not quality.

```toml
[tool.coverage.run]
source = ["src/ledger"]
branch = true

[tool.coverage.report]
fail_under = 90
show_missing = true
exclude_lines = ["pragma: no cover", "if TYPE_CHECKING:", "raise NotImplementedError"]
```

### Advanced — what to learn

- **Goodhart's law**: when a measure becomes a target it ceases to be a good
  measure. Coverage without assertions: write a test with no `assert` and watch coverage rise.
- What coverage cannot see: data-dependent bugs, missing branches in the code
  (what you forgot to write), integration behaviour, concurrency interleavings, error handling you never triggered.
- Coverage contexts (`dynamic_context = test_function`) to see **which test covers which line**
  and find tests that cover nothing unique.
- Coverage of async code and generators; `sys.monitoring` core in 3.12+ (`COVERAGE_CORE=sysmon`) for lower overhead.
- Setting thresholds sensibly: ratchet upward (never allow decrease), higher on core logic,
  exclude generated code; per-package thresholds.
- Mapping coverage to risk: pair with mutation score (lesson 02) and incident history.
- Reviewing coverage as a code-review tool: look at the **uncovered** lines of a PR.

### Common mistakes

- Chasing 100 % by testing trivial getters.
- Tests with no assertions.
- Excluding inconvenient code with `no cover`.

### Self-check

1. Construct a function with 100 % line coverage but 50 % branch coverage.
2. Why can a test suite with 100 % coverage still miss an obvious bug? Write an example.
3. Configure `fail_under` and branch coverage, and show a CI failure when a PR lowers coverage.

---

## Lesson 02 — `02-mutation-testing.md`

**Why it matters.** Mutation testing answers "if I break the code, do my
tests notice?" It inserts small bugs (mutants) and checks whether any test
fails. Surviving mutants reveal weak assertions that coverage cannot.

### Basic — what to learn

- Concept: mutate operators (`+`→`-`, `<`→`<=`), constants, conditions, return values;
  **killed** (a test failed) vs **survived** (all tests passed) vs timeout/suspicious.
- **Mutation score** = killed / total (non-equivalent) mutants.
- Run a tool: `mutmut run`, `mutmut results`, `mutmut show <id>` (or `cosmic-ray`).

```python
def is_adult(age: int) -> bool:
    return age >= 18

def test_adult():
    assert is_adult(30)            # mutant `age > 18` survives: boundary untested
```

### Intermediate — what to learn

- Reading survivors and fixing them by adding **boundary** and negative tests
  (age 17/18/19) — often reveals missing specifications.
- **Equivalent mutants** (changes that don't alter behaviour) and why score
  100 % is not the goal.
- Scoping runs: mutate only changed files or core modules; use test selection per mutant
  (coverage-guided) to cut runtime.
- Configuring `mutmut` in `pyproject.toml`/`setup.cfg`: paths to mutate, runner command, `--paths-to-mutate`.
- Interpreting results by category: logic vs arithmetic vs string constants (log messages are usually noise).
- Relationship with parametrized tests and property-based tests (Hypothesis kills many boundary mutants).

```bash
uv run mutmut run --paths-to-mutate src/ledger/pricing.py
uv run mutmut results
uv run mutmut show 12
```

### Advanced — what to learn

- Cost: mutants × test time; strategies — fast unit tests only, parallel workers,
  incremental/cached runs in CI nightly, limit to critical modules.
- Mutation testing in CI as a **nightly** or **pre-release** job, not per-commit.
- Higher-order mutants and statistical sampling; when the tool lacks operators (e.g. async, type-level logic).
- Using survivors to drive design: surviving mutants in validation code often mean
  validation is unobservable → simplify or expose behaviour.
- Combine metrics: coverage (reach) + mutation score (strength) + escaped-defect rate (reality).
- Limitations: doesn't test missing features, slow for I/O-heavy tests, noise from logging/formatting;
  compare with other approaches (test review, property-based tests, fault injection).
- Cross-language ideas: Stryker, PIT — shows the practice is general.
- Experiment: take a module with 95 % coverage, run mutation testing, and write a report of weak spots and the tests added.

### Common mistakes

- Running mutation testing over slow integration suites on every commit.
- Chasing equivalent mutants.
- Ignoring survivors in critical code.

### Self-check

1. What does a surviving mutant tell you?
2. Why is an equivalent mutant a problem for the score?
3. Pick a function, predict three surviving mutants before running the tool, then compare.

---

## Lesson 03 — `03-pytest-plugins-hooks-and-conftest-architecture.md`

**Why it matters.** Large projects need shared fixtures, custom markers,
command-line options and reporting hooks. Understanding pytest's plugin
architecture lets you extend it instead of fighting it — and read the
source of plugins like `pytest-django` or `pytest-asyncio`.

### Basic — what to learn

- `conftest.py` files: fixtures and hooks available to the directory subtree;
  layering root → package → test directory; no imports from `conftest`.
- Fixture scopes: `function`, `class`, `module`, `package`, `session`; `autouse`; `yield` fixtures for teardown;
  `request` object (`request.param`, `request.node`, `request.config`).
- Built-in fixtures: `tmp_path`, `monkeypatch`, `capsys`, `caplog`, `request`, `pytestconfig`, `recwarn`.
- Markers: `@pytest.mark.slow`, registering them in `pyproject.toml`
  (`markers = [...]`), `--strict-markers`, `-m "not slow"`.

```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def sample_db(tmp_path_factory):
    path = tmp_path_factory.mktemp("db") / "test.sqlite"
    ...
    return path

@pytest.fixture
def clean_env(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
```

### Intermediate — what to learn

- **Fixture design**: small, composable, explicit; factory fixtures
  (`def make_user(): ...; return make_user`); parametrized fixtures (`params=`);
  fixture overriding at lower levels; avoid hidden dependencies and giant "god" fixtures.
- Test data builders / object mothers; `pytest.param(..., id=..., marks=...)`.
- Skipping and expected failures: `skipif`, `xfail(strict=True)`, `importorskip`.
- Custom CLI options with `pytest_addoption` and `pytestconfig.getoption`
  (e.g. `--run-integration`); auto-skipping marked tests via `pytest_collection_modifyitems`.
- Configuring pytest: `[tool.pytest.ini_options]` (`testpaths`, `addopts`, `filterwarnings`, `xfail_strict`, `markers`).
- Plugins you should know: `pytest-xdist` (parallel), `pytest-randomly`, `pytest-cov`,
  `pytest-mock`, `pytest-asyncio`/`anyio`, `pytest-timeout`, `pytest-benchmark`, `syrupy`, `pytest-socket`.

```python
# conftest.py
def pytest_addoption(parser):
    parser.addoption("--run-integration", action="store_true", help="run integration tests")

def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-integration"):
        return
    skip = pytest.mark.skip(reason="need --run-integration")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)
```

### Advanced — what to learn

- The **hook system** (pluggy): `pytest_configure`, `pytest_collection_modifyitems`,
  `pytest_runtest_setup/call/teardown`, `pytest_runtest_makereport` (attach screenshots/logs on failure),
  `pytest_generate_tests` (dynamic parametrization), `pytest_terminal_summary`.
- Writing an installable plugin: package with `pytest11` entry point (links to Module 1.18 lesson 04),
  `pytester` fixture to test the plugin itself.
- How assertion rewriting works (AST transformation at import — links to Module 1.12 lesson 08); `register_assert_rewrite` for helper modules.
- Test architecture at scale: `tests/unit`, `tests/integration`, `tests/e2e`, shared `tests/factories`,
  contract tests; mirrored layout vs feature layout; keeping tests independent of implementation details.
- Parallel execution with `xdist`: shared resources (ports, files, DB), `worker_id`, session fixtures per worker,
  `--dist loadgroup`.
- Fixture performance: expensive session fixtures vs per-test isolation (transactions rollback pattern).
- Ordering and independence: run with `pytest-randomly`; tests must pass in any order.
- Governance: test naming conventions, markers policy, deleting obsolete tests, flaky quarantine policy.

### Common mistakes

- Autouse fixtures that hide setup and slow every test.
- Shared mutable session fixtures causing order dependence.
- Importing from `conftest.py` modules.

### Self-check

1. Where does pytest look for fixtures, and how does overriding work?
2. Write a `--run-integration` option that auto-skips integration tests.
3. Sketch a plugin that records slow tests (> 1 s) in a terminal summary, with a `pytester` test.

---

## Lesson 04 — `04-snapshot-and-golden-file-testing.md`

**Why it matters.** For large structured outputs (rendered reports, CLI
help, generated SQL, API responses, parsed ASTs, LLM-pipeline intermediate
JSON) hand-written assertions are unwieldy. Snapshot tests compare output
against a stored, reviewed "golden" version.

### Basic — what to learn

- Golden file idea: store expected output in `tests/golden/*.txt|json`; the test
  computes output and compares; update deliberately.
- Plain approach: `expected = Path("golden/report.txt").read_text()`; `assert actual == expected`.
- Library approach with **syrupy**: `assert result == snapshot`; `pytest --snapshot-update`;
  `.ambr` files committed to the repo.

```python
def test_report(snapshot):
    out = render_report(sample_data())
    assert out == snapshot
```

### Intermediate — what to learn

- Making snapshots **stable**: sort keys, fix time (`freezegun`/clock injection), seed randomness,
  mask volatile fields (ids, timestamps, absolute paths), normalise line endings and floats.
- Snapshot formats: text, JSON (`snapshot(extension_class=JSONSnapshotExtension)`), images/binary.
- Reviewing snapshot diffs in PRs like code; naming snapshots; keeping them small and focused.
- Updating workflow: run, inspect `git diff`, commit with explanation; CI must **never** auto-update.
- Combining with parametrization; per-case snapshots.
- Approval-style tools alternatives: `pytest-regressions`, `approvaltests`, `inline-snapshot` (snapshots in the test source).

```python
def test_cli_help(snapshot, capsys):
    main(["--help"])
    assert capsys.readouterr().out == snapshot
```

### Advanced — what to learn

- Smells of over-snapshotting: huge snapshots nobody reads; "approve all" culture;
  tests that fail on irrelevant changes → use partial/structured assertions or matchers.
- Property-style invariants alongside snapshots (e.g. valid JSON Schema, idempotency).
- Golden datasets for data pipelines: small input fixtures → expected parquet/CSV with
  tolerant comparisons (`pandas.testing`, Stage 2); schema snapshots as contract tests.
- Snapshotting prompts and LLM outputs: record-and-replay (VCR-style cassettes with `vcrpy`/`pytest-recording`),
  never snapshot non-deterministic model output as a correctness test; use evals instead (Evaluation stage).
- Security and privacy: no secrets/PII in snapshots; scrub cassettes.
- Cross-platform snapshot differences (path separators, locale); normalising in a fixture.
- Migrating snapshot formats and handling obsolete snapshots (`--snapshot-warn-unused`).
- Cost-benefit analysis: when a snapshot is the right tool vs explicit asserts.

### Common mistakes

- Snapshotting values that change every run.
- Blindly updating snapshots.
- Giant snapshots mixing unrelated concerns.

### Self-check

1. Why must CI never run with `--snapshot-update`?
2. Make a snapshot of a report that contains timestamps and UUIDs stable.
3. Replace a 60-line expected-JSON assertion with a snapshot plus two targeted assertions.

---

## Lesson 05 — `05-flaky-tests-and-test-isolation.md`

**Why it matters.** Flaky tests (pass/fail with no code change) destroy trust:
people re-run CI until green and real failures hide. Fixing flakiness is
mostly about **isolation and determinism**.

### Basic — what to learn

- Definition and cost of flakiness; the "re-run" culture problem.
- Common causes: shared state between tests, test order dependence, real time/sleep,
  randomness, network, concurrency races, fixed ports, leftover files, timezone/locale,
  dict/set ordering assumptions, resource limits.
- Detect: run tests repeatedly (`pytest --count`, `pytest-repeat`), random order
  (`pytest-randomly`), parallel (`xdist`), isolate a single test (`pytest path::test -x`).

```python
# order-dependent bug
CACHE = {}
def test_a(): CACHE["k"] = 1
def test_b(): assert "k" not in CACHE      # fails if test_a ran first
```

### Intermediate — what to learn

- Isolation tools: `tmp_path`, `monkeypatch` (env, attributes, cwd), fixtures that reset
  global state (singletons, registries, caches, `logging` config, `random` seed), `autouse` cleanup.
- Replace `time.sleep` with explicit synchronisation (events, polling with timeout and deadline), or fakes.
- Free ports: bind to port `0`; unique temp dirs/DB schemas per xdist worker.
- Network isolation: `pytest-socket` (`--disable-socket`), local fake servers (Module 1.13 lesson 09), recorded cassettes.
- Finding order dependence with bisection (re-run with the failing seed: `pytest --randomly-seed=1234`; then `pytest --lf --ff` and manual bisection of the test list).
- `pytest-timeout` to turn hangs into failures; capture logs on failure.
- Quarantine policy: mark `@pytest.mark.flaky` (via `pytest-rerunfailures`) **temporarily**, track in an issue, never let it grow.

```python
@pytest.fixture(autouse=True)
def reset_registry():
    snapshot = dict(REGISTRY)
    yield
    REGISTRY.clear(); REGISTRY.update(snapshot)
```

### Advanced — what to learn

- Root-cause method: reproduce → minimise → hypothesise → verify; collect metadata
  (seed, worker id, platform, load) on failure; stress with `taskset`/CPU load to expose races.
- Concurrency flakiness: lock-order, missing joins, daemon threads, event-loop leakage between tests,
  unawaited coroutines (`-W error::RuntimeWarning`), `ResourceWarning` for leaked files/sockets.
- Environment drift: dependency versions (lock files), OS differences, container CPU limits, DNS, clock skew.
- Test data hygiene: unique ids per test, transactional rollback for DB tests, cleaning external resources.
- Metrics: track flake rate per test in CI, auto-detect tests that fail then pass on retry;
  dashboards and ownership.
- Cultural/process: "fix or delete" rule, SLA for flaky tests, blocking merges when flake rate rises.
- Deterministic simulation approaches for distributed code (fake clock, fake network, seeded schedulers).
- Case study writing: pick a real flaky test (from OSS issue trackers), write a post-mortem.

### Common mistakes

- Adding retries instead of fixing the cause.
- `sleep(1)` "to be safe".
- Tests sharing a real database without isolation.

### Self-check

1. List five root causes of flaky tests and the isolation technique for each.
2. How would you find which earlier test pollutes global state for a failing test?
3. Rewrite a test that sleeps 2 s waiting for a background thread so it is deterministic.

---

## Lesson 06 — `06-testing-cli-and-subprocess-programs.md`

**Why it matters.** CLIs and scripts are how data jobs run in production.
You must test argument parsing, exit codes, stdout/stderr, environment
handling and end-to-end behaviour — both **in-process** (fast) and as a real
**subprocess** (faithful).

### Basic — what to learn

- Design for testability: `def main(argv: list[str] | None = None) -> int:` and
  `if __name__ == "__main__": raise SystemExit(main())`.
- In-process tests: call `main([...])`, capture with `capsys`/`capfd`, assert exit code;
  `pytest.raises(SystemExit)` for `argparse` errors.
- `monkeypatch.setenv`, `monkeypatch.chdir(tmp_path)`, `monkeypatch.setattr(sys, "stdin", io.StringIO(...))`.

```python
def test_cli_ok(tmp_path, capsys):
    f = tmp_path / "in.csv"; f.write_text("a,b\n1,2\n")
    code = main([str(f), "--format", "json"])
    out = capsys.readouterr()
    assert code == 0 and '"a": 1' in out.out and out.err == ""
```

### Intermediate — what to learn

- Subprocess tests: `subprocess.run([sys.executable, "-m", "pkg", ...], capture_output=True, text=True, timeout=30, cwd=..., env=...)`
  — tests the real entry point, packaging and import path.
- Testing console scripts after installation (`uv run`/`pipx run` in CI; editable installs).
- Testing `stdin`/pipes, exit codes (0/1/2/130), signals (`SIGINT`, `SIGTERM`), long-running processes with timeouts.
- Click/Typer testing helpers (`CliRunner`) as awareness.
- Testing logging output and verbosity flags; `--help` snapshot (lesson 04); `--version`.
- Testing idempotency: run twice, same result; dry-run mode does not write.
- Fixtures for sample files and a fake `PATH` with stub executables when the CLI shells out.

```python
import subprocess, sys
def test_exit_code_on_bad_input(tmp_path):
    r = subprocess.run([sys.executable, "-m", "ledger", "missing.csv"],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 2 and "No such file" in r.stderr
```

### Advanced — what to learn

- Pseudo-terminals for interactive programs (`pexpect`, `pty`) and prompts; testing `getpass`/`input` flows.
- Coverage for subprocess-launched code (lesson 01 settings).
- Cross-platform CLI testing: quoting, path separators, line endings, encodings (`PYTHONUTF8`, `PYTHONIOENCODING`).
- Contract between CLI and automation: stable machine-readable output (`--json`), exit-code table,
  stderr vs stdout discipline; tests enforce the contract.
- Resource & failure injection: read-only directories, disk full (tmpfs), permission errors, huge inputs, broken pipes (`| head`).
- Testing scheduled/long jobs: checkpoints, resume after kill, partial outputs cleaned up.
- Performance regression guards in CLI tests (coarse upper bounds, benchmark separately).
- Test pyramid for CLIs: most tests in-process, a few subprocess smoke tests, one packaged-install test in CI.

### Common mistakes

- Only testing happy paths and never exit codes.
- Using `os.system` or shell strings in tests.
- Tests relying on the current working directory.

### Self-check

1. Why is `main(argv)` easier to test than code at module top level?
2. Write tests for `--help`, a missing file, a bad flag (exit code 2) and a successful run.
3. How do you test behaviour when stdout is a closed pipe?

---

## Lesson 07 — `07-testing-time-randomness-and-concurrency.md`

**Why it matters.** Time, randomness and concurrency are *non-determinism
sources*. Code that reads the clock, rolls dice or spawns threads cannot be
tested reliably unless you control them. This is the heart of reproducible
data-pipeline and retry/backoff testing.

### Basic — what to learn

- **Dependency injection of the clock**: pass `now: Callable[[], datetime]` or a `Clock` object;
  default to the real one.
- Seed randomness: `random.Random(42)` instance injected; NumPy `default_rng(42)`.
- Freeze time: `freezegun` / `time-machine`; `monkeypatch.setattr(time, "time", ...)` limitations (imports by name).

```python
from datetime import datetime, timezone
from collections.abc import Callable

def is_expired(expires_at: datetime, now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> bool:
    return now() >= expires_at

def test_expired():
    fixed = lambda: datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert is_expired(datetime(2025, 12, 31, tzinfo=timezone.utc), fixed)
```

### Intermediate — what to learn

- Testing timeouts, TTL caches, retries with backoff: inject `sleep` and `clock`; assert the sequence of waits without actually sleeping.
- Timezone and DST edge cases: tests near transitions, leap years/days, month ends, week boundaries
  (`zoneinfo`; links to Module 1.9 lesson 07).
- Testing threads: use `threading.Event`/`Barrier` to coordinate, `join(timeout)`, assert no leaked threads; deterministic queues.
- Testing `asyncio`: `pytest-asyncio`/`anyio`, `asyncio.timeout`, fake event loop time; controlling task interleavings with `Event`s; detect unawaited coroutines.
- Testing randomness: statistical tests with fixed seeds and tolerances; testing invariants rather than exact outputs
  (property-based tests — Stage 2); sampling functions tested for distribution with large N and loose bounds.
- Time-based scheduling logic with a fake scheduler.

```python
class FakeClock:
    def __init__(self, t=0.0): self.t = t
    def now(self): return self.t
    def sleep(self, s): self.t += s

def test_retry_backoff():
    clock, waits = FakeClock(), []
    def sleep(s): waits.append(s); clock.sleep(s)
    attempts = iter([Exception, Exception, "ok"])
    ...   # call retry(fn, sleep=sleep) and assert waits == [1, 2]
```

### Advanced — what to learn

- Race-condition testing: stress tests (many iterations, many threads), `sys.setswitchinterval` to
  increase interleavings, running under load; tools like `pytest-repeat`; free-threaded builds make races visible.
- Deterministic scheduling frameworks: `hypothesis` stateful testing, `trio.testing` / `anyio` test helpers, `asynctest`-style fake loops,
  model-checking ideas (TLA+ awareness) for protocols.
- Testing idempotency and exactly-once semantics under retries and duplicates.
- Fault injection: fail the Nth call, delay responses, drop connections (`toxiproxy` awareness).
- Time-travel testing for batch pipelines: run the same job for logical dates; late-arriving data; backfills.
- Floating-point nondeterminism across platforms/threads (reductions) and tolerances (`pytest.approx`, `math.isclose`).
- Clock pitfalls: wall clock vs monotonic (`time.monotonic`) — use monotonic for durations;
  NTP jumps; mocking only what you must.
- Guidelines: control non-determinism at the **boundary**, keep core logic pure.

### Common mistakes

- Mocking `datetime.datetime.now` incorrectly (patching where it's looked up).
- Tests that depend on real `sleep` durations.
- Asserting exact outputs of random code without seeding.

### Self-check

1. Why is injecting a clock better than patching `time.time`?
2. Test a retry-with-jitter function without sleeping and without randomness flakiness.
3. Write a test that reliably fails (before a lock is added) for a race on a shared counter.

---

## Lesson 08 — `08-test-matrices-with-tox-and-nox.md`

**Why it matters.** "Works on my machine with Python 3.12" is not enough
for libraries or shared tooling. Matrices test multiple Python versions,
dependency ranges (lowest/highest), OSs and optional-dependency sets in
clean, reproducible environments.

### Basic — what to learn

- What `tox` and `nox` do: create isolated virtualenvs per session, install your package, run commands.
- `tox.ini`/`pyproject.toml` (`[tool.tox]`) with `env_list = ["py312", "py313", "py314", "lint", "type"]`;
  `noxfile.py` with `@nox.session(python=["3.12", "3.13"])`.
- Running one environment: `tox -e py313`, `nox -s tests-3.13`; reuse venvs (`-r`).

```python
# noxfile.py
import nox

@nox.session(python=["3.12", "3.13", "3.14"])
def tests(session):
    session.install(".[test]")
    session.run("pytest", "--cov=ledger", *session.posargs)

@nox.session
def lint(session):
    session.install("ruff")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")
```

### Intermediate — what to learn

- With `uv`: `tox-uv` or `uv run --python 3.12 pytest`, `uv` dependency groups; speed benefits.
- Matrix dimensions: Python version × dependency set (`min` pins vs `latest`) × OS (CI matrix);
  optional extras (`.[pandas]`, `.[all]`); `nox.parametrize`.
- Testing against **lowest direct dependency versions** (`uv pip install --resolution lowest-direct`) to
  validate declared lower bounds; testing pre-releases.
- Separate sessions for lint, type-check, docs build, packaging check (`build` + `twine check`), and coverage combine.
- Passing arguments (`{posargs}` / `session.posargs`); environment variables; `--no-install` for non-package sessions.
- CI integration: GitHub Actions matrix calling `nox -s tests-${{ matrix.python }}` (CI pipelines are covered in Stage 2/7; here you write the sessions).
- Caching and reproducibility: lock files for app tests vs unlocked for library compatibility tests.

```ini
# tox.ini
[tox]
env_list = py312, py313, lint
[testenv]
extras = test
commands = pytest {posargs}
[testenv:lint]
skip_install = true
deps = ruff
commands = ruff check .
```

### Advanced — what to learn

- Testing the **installed** artifact, not the source tree: build wheel/sdist, install into a fresh venv, run tests
  against the installed package (`src/` layout prevents accidental imports; Module 1.6 lesson 02).
- Compatibility strategy for free-threaded builds (`3.14t`) and experimental JIT in a non-blocking CI job.
- Combining coverage across sessions (`coverage combine`) and enforcing a total threshold.
- Matrix explosion control: smoke tests on all combos, full tests on key combos; scheduled nightly jobs for the long tail.
- Test dependencies on system libraries (OpenSSL, libpq): containers (`docker`) in sessions; `tox-docker` awareness.
- Reproducing CI failures locally with the same session; sharing `noxfile.py` across repos (internal tooling packages).
- Performance regression sessions with `pytest-benchmark` and stored baselines.
- Security sessions: `pip-audit`, `bandit` (Module 1.22).

### Common mistakes

- Tests importing from the source tree instead of the installed package.
- Matrix too large to run regularly.
- Forgetting to test minimum dependency versions you advertise.

### Self-check

1. Why test the installed wheel instead of the working directory?
2. Write a `noxfile.py` with test, lint, type-check and build-check sessions.
3. How do you verify that your declared `>=` lower bounds actually work?

---

## Lesson 09 — `09-fuzzing-basics.md`

**Why it matters.** Parsers, deserialisers, tokenisers, protocol handlers
and file-format readers crash on inputs their authors never imagined.
Fuzzing generates huge numbers of weird inputs to find crashes, hangs and
security bugs automatically.

### Basic — what to learn

- Fuzzing = feeding random/mutated inputs to find unexpected failures;
  **oracle**: "must not crash/hang/leak"; or "round-trip must hold".
- Hand-rolled random fuzzing: random bytes/strings into your parser; catch only the *expected* exceptions.
- Hypothesis as a "fuzzer-lite": `@given(st.binary())`, `st.text()`; shrinking minimal failing cases.

```python
from hypothesis import given, strategies as st

@given(st.binary(max_size=2000))
def test_parser_never_crashes(data):
    try:
        parse(data)
    except ParseError:
        pass                         # expected, documented failure
```

### Intermediate — what to learn

- Coverage-guided fuzzing with **Atheris** (libFuzzer for Python) and **python-afl** awareness:
  harness function `TestOneInput(data)`, instrumented imports, corpus and seed inputs, dictionaries.
- Designing harnesses: small, fast, deterministic, no I/O, no global state accumulation; limit input size.
- Properties to assert: no unexpected exceptions, bounded time/memory, round-trip `parse(serialize(x)) == x`,
  differential testing (two implementations agree, e.g. `json` vs `orjson`).
- Triage: minimise crashing inputs (`atheris` / `hypothesis` shrinking), turn each into a **regression test** with the exact bytes.
- Structure-aware fuzzing (grammars/strategies that produce mostly-valid inputs) vs dumb byte mutations.
- Common bug classes found: unhandled exceptions, infinite loops, excessive recursion/memory, ReDoS (Module 1.14 lesson 04), integer/length overflow handling in binary parsers, decompression bombs.

```python
import atheris, sys

with atheris.instrument_imports():
    import mypkg.parser as p

def TestOneInput(data: bytes):
    try:
        p.parse(data)
    except p.ParseError:
        pass

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
```

### Advanced — what to learn

- Fuzzing C extensions and native code from Python (sanitizers: ASan/UBSan), why pure-Python fuzzing finds logic bugs
  while native bugs need sanitizers.
- Continuous fuzzing: OSS-Fuzz, ClusterFuzzLite in CI; corpus management and minimisation; budgeted nightly runs.
- Stateful/API fuzzing: Hypothesis stateful testing (`RuleBasedStateMachine`) for sequences of operations
  (e.g. a cache or a file-format writer/reader); `schemathesis` for OpenAPI services (Stage 7 awareness).
- Security perspective: fuzzing untrusted-input surfaces (archives, images, pickle-free deserialisers, template engines, prompt/tool-call parsers for LLM agents).
- Differential and metamorphic testing for ML/data code (e.g. permuting rows must not change aggregates).
- Limits: fuzzers find "can crash", not "does the right thing"; combine with specs, unit tests, mutation testing (lesson 02).
- Resource limits when fuzzing (`resource.setrlimit`, timeouts) and avoiding side effects (never fuzz code that deletes files).
- Writing a fuzzing policy/checklist for a codebase: which components get harnesses, seed corpora, ownership.

### Common mistakes

- Catching `Exception` broadly in the harness (hides real bugs).
- Fuzzing code with side effects or network access.
- Not converting findings into regression tests.

### Self-check

1. What is the oracle in "the parser must not crash"? How does it differ from a round-trip oracle?
2. Write a Hypothesis test that finds a bug in a deliberately flawed length-prefixed parser, then add the regression test.
3. List three input-handling components in your own projects that deserve fuzz harnesses and why.

---

## 4. Practice questions (`practice-questions.md`)

About **35 questions**:

| Phase | Question types |
| --- | --- |
| A | Branch-coverage puzzles; spot the surviving mutants; configure coverage |
| B | Design a `conftest.py` layout; write a marker/option plugin; stabilise a snapshot |
| C | Diagnose flaky test scenarios; write CLI tests; inject clock/randomness/concurrency |
| D | `noxfile.py` design; matrix strategy; fuzz harness and triage |

Add 6 **"why is this test bad?"** items (no assertion, order-dependent, sleeps, patched the wrong target, giant snapshot, retries hiding a race).

---

## 5. Module mini-project

**Harden the test suite of a small data tool (`ledger`/`datadrop` from earlier modules):**

1. Baseline: measure line + branch coverage; record the number.
2. Run mutation testing on the core logic; add tests until the mutation score on that module is ≥ 80 % (excluding documented equivalents).
3. Refactor `conftest.py` into layered fixtures, markers (`slow`, `integration`), a `--run-integration` option and a tiny plugin that prints the 10 slowest tests.
4. Add snapshot tests for CLI help and a rendered report with all volatility masked.
5. Run the suite 50× under `pytest-randomly` and `xdist`; fix every flaky or order-dependent test; document root causes in `FLAKES.md`.
6. Add in-process and subprocess CLI tests including exit codes and a broken-pipe case.
7. Inject clock/sleep/random into the retry code and test back-off deterministically; add a threaded-counter race test.
8. Add `noxfile.py` (tests on 3.12–3.14, lint, type, build check) and a lowest-dependency session.
9. Write a fuzz harness (Hypothesis and/or Atheris) for the input parser; commit regression cases.

Acceptance: branch coverage ≥ 90 %, mutation score target met on core module, 0 flaky tests across 50 randomised runs, all `nox` sessions green, README "Testing" section describing how to run each layer.

---

## 6. Completion checklist

- [ ] I can explain line vs branch coverage and why coverage is not quality.
- [ ] I can run mutation testing and turn survivors into better tests.
- [ ] I can structure fixtures, markers, options and plugins for a large suite.
- [ ] I can write stable snapshot/golden tests and review snapshot diffs.
- [ ] I can find and fix flaky tests and enforce isolation.
- [ ] I test CLIs in-process and as subprocesses, including exit codes and signals.
- [ ] I control time, randomness and concurrency in tests.
- [ ] I run test matrices across Python versions and dependency sets.
- [ ] I can write a fuzz harness and convert findings into regression tests.
- [ ] I completed the test-suite hardening mini-project.

**Next:** Module 1.17 — Profiling, Memory and Runtime Performance.
