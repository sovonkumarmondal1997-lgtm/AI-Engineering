# Flaky Tests and Test Isolation

> **Module:** Stage 1 — Programming & Computational Thinking  
> **Module 16:** Advanced Testing and Test Architecture  
> **Lesson 05 of 09**  
> **Target environment:** Python 3.12+, pytest 8+  
> **Prerequisites:** pytest fixtures and parametrization; monkeypatching and test doubles; tracebacks and minimal reproductions; `threading`, `asyncio`, `tempfile`, `random`, and `subprocess` basics.

## Learning outcomes

By the end of this lesson, you should be able to:

- Define flakiness and explain its technical and organizational cost.
- Classify common sources of nondeterminism and test contamination.
- Detect intermittent failures using repetition, randomized order, isolation, and parallel workers.
- Design tests with explicit ownership of files, environment variables, global state, network access, databases, threads, and event loops.
- Replace arbitrary sleeps with deterministic synchronization or controlled fakes.
- Reproduce, minimize, hypothesize, and verify a failure while retaining the seed and environment evidence needed to explain it.
- Measure flake rate, assign ownership, and quarantine failures only under a temporary, accountable policy.
- Apply deterministic simulation techniques to distributed systems and write a useful post-mortem.

The central engineering principle is **make the test deterministic by removing or controlling the source of nondeterminism**. Re-running is a diagnostic technique, not a fix.

---

## 1. What is a flaky test?

A test is **flaky** when the same test and relevant code produce different outcomes across runs because of uncontrolled variation in state, timing, scheduling, environment, or dependencies. A flaky test may pass ten times and fail on the eleventh without a meaningful code change.

Do not confuse flakiness with:
- **A deterministic failure:** it fails consistently for a given input.
- **A legitimate nondeterministic contract:** for example, a distributed service may promise eventual convergence rather than a particular arrival order. The test should assert the contract, not an accidental schedule.
- **An environment-specific defect:** if a supported OS or Python version consistently fails, that may be a compatibility bug rather than flakiness. It still deserves a fix.
- **An intermittent product bug:** a race in production code is real even when the test is the first place it becomes visible.

### Why flakiness is expensive

1. **Signal-to-noise collapses.** Engineers cannot tell whether a red build reflects a regression or noise.
2. **Retries normalize ignoring failures.** People learn to rerun until green; real failures are eventually hidden in the same habit.
3. **Feedback gets slower.** Each rerun consumes CI time, worker capacity, and developer attention.
4. **Coverage becomes less trustworthy.** A suite that is not reproducible cannot reliably establish that a change is safe.
5. **Incident risk rises.** Race conditions and cleanup defects may be the same defects that affect production.
6. **Ownership becomes unclear.** Quarantined tests can persist indefinitely if nobody owns their repair.

A green build after a retry is not evidence that the code is correct. It is evidence that one run passed.

## 2. A taxonomy of common causes

Use this table as a first-pass diagnostic map. A symptom is a clue, not proof of root cause.

| Cause | Typical symptom | Strong first diagnostic |
|---|---|---|
| Shared mutable global, singleton, registry, cache | Passes alone; fails after another test | Run in randomized order; inspect writes and teardown |
| Test order dependence | Fails only in suite or after a specific test | Reuse random seed; bisect preceding tests |
| Wall-clock time or sleeps | CI-only timeout or boundary failure | Replace elapsed-time assumption with a deadline and synchronization |
| Randomness / generated IDs | Rare data-specific failure | Record seed; inject a local RNG or deterministic ID source |
| External network / DNS / remote API | Intermittent timeout or changed response | Disable external sockets; use a fake or recorded response |
| Thread/task race | Fails under load or parallelism | Add synchronization; capture thread/task state |
| Fixed port / shared resource | Address already in use; cross-worker interference | Bind port `0`; allocate per-worker namespace |
| Leftover files / cwd / environment | Passes on clean checkout only | Use `tmp_path`, monkeypatch, and cleanup assertions |
| Timezone / locale / platform | Fails on one machine or CI image | Pin the relevant setting; assert normalized semantics |
| Dict/set ordering assumptions | Different output ordering | Sort only where the contract requires canonical order |
| Resource limits / leaks | Slow, hung, or memory-dependent failures | Measure resource use; close/join/await resources |
| Dependency or OS drift | Failure appears after an upgrade | Lock dependencies and retain runtime/platform metadata |

### 2.1 Shared state and order dependence

A minimal broken example:

```python
# test_cache.py
CACHE: dict[str, int] = {}

def test_a_populates_cache():
    CACHE["customer"] = 1

def test_b_starts_with_empty_cache():
    assert CACHE == {}
```

`test_b_starts_with_empty_cache` only passes if it happens to run before `test_a_populates_cache`. The defect is not pytest ordering; the defect is that one test relies on process-global state left by another.

**Preferred fix:** make state local to the test or create/reset it through a fixture. Reset the state in teardown, even when assertions fail.

```python
# cache.py
CACHE: dict[str, int] = {}

def put(key: str, value: int) -> None:
    CACHE[key] = value
```

```python
# test_cache.py
import pytest
import cache

@pytest.fixture(autouse=True)
def clean_cache():
    # Establish the precondition before each test; do not restore leaked test state.
    cache.CACHE.clear()
    try:
        yield
    finally:
        cache.CACHE.clear()

def test_put():
    cache.put("customer", 1)
    assert cache.CACHE == {"customer": 1}

def test_cache_starts_empty():
    assert cache.CACHE == {}
```

This fixture intentionally clears the cache before and after each test; it does **not** preserve pre-existing process state. In a larger suite, prefer a dedicated cache instance injected into the code rather than a global. If values inside the cache are mutable, a shallow copy is not enough to restore nested mutations; dependency injection is usually clearer than trying to snapshot arbitrary global state.

A snapshot-and-restore fixture is appropriate only when preserving an explicitly defined baseline is part of the test contract. It must still establish the required precondition before `yield`. For example, if the baseline itself is known and trusted:

```python
@pytest.fixture
def isolated_registry():
    previous = dict(REGISTRY)  # assumes REGISTRY is imported and values are not mutated in place
    REGISTRY.clear()
    try:
        yield REGISTRY
    finally:
        REGISTRY.clear()
        REGISTRY.update(previous)
```

This is a fragment that assumes `REGISTRY` is defined in the module and that restoring its shallow mapping is sufficient. If earlier tests may leave invalid state, do not treat that leaked state as a trusted baseline; reset to a known baseline or inject a fresh registry. Broad `autouse` fixtures can hide dependencies and add unnecessary cost.

### 2.2 Time and sleeps

Real-time clocks, wall-clock boundaries, and arbitrary sleeps introduce nondeterminism. Prefer an injected clock for business-time logic and a monotonic deadline for elapsed-time limits. This test is fragile:

```python
def test_background_work_finishes():
    start_background_job()
    time.sleep(1)
    assert job_finished()
```

One second is neither a guarantee nor a meaningful synchronization primitive. A slow worker may need longer; a fast worker wastes time. Increasing the sleep often only lowers the probability of failure.

Use a completion event if the code exposes a clear completion signal:

```python
from threading import Event, Thread

def worker(done: Event, results: list[int]) -> None:
    results.append(42)
    done.set()

def test_worker_completion():
    done = Event()
    results: list[int] = []
    thread = Thread(target=worker, args=(done, results), daemon=False)
    thread.start()
    try:
        assert done.wait(timeout=2.0), "worker did not signal completion"
        assert results == [42]
    finally:
        thread.join(timeout=2.0)
        assert not thread.is_alive(), "worker leaked past test teardown"
```

The event expresses the condition the test needs. The timeout is a failure bound, not a sleep used to guess when work finishes. A thread that ignores cancellation may still outlive the test; design workers to cooperate and always investigate a failed join.

For an asynchronous function, await the task and apply a timeout around the await rather than sleeping. The example uses `pytest-asyncio` for the `@pytest.mark.asyncio` marker (`uv add --dev pytest-asyncio`):

```python
import asyncio
import pytest

async def produce_value() -> int:
    await asyncio.sleep(0)  # cooperative scheduling point in this illustrative worker
    return 42

@pytest.mark.asyncio
async def test_async_result():
    result = await asyncio.wait_for(produce_value(), timeout=1.0)
    assert result == 42
```

The `sleep(0)` here yields control in a toy coroutine; it is not a timing delay used by the test. Real code should expose an awaited completion condition. `asyncio.wait_for` cancels the awaited operation on timeout, but cancellation cleanup must still be correct.

### 2.3 Randomness and IDs

Global random state is shared and can be consumed by unrelated code. Seeded randomness helps reproduce a run, but a test that depends on a module-global RNG can still be order-dependent if other tests draw from it.

Inject a local generator:

```python
import random

def sample_batch(values: list[int], size: int, *, rng: random.Random) -> list[int]:
    if size < 0 or size > len(values):
        raise ValueError("size must be between zero and len(values)")
    return rng.sample(values, size)
```

```python
import random

def test_sample_batch_is_reproducible():
    values = list(range(20))
    first = sample_batch(values, 5, rng=random.Random(731))
    second = sample_batch(values, 5, rng=random.Random(731))
    assert first == second
    assert len(set(first)) == 5
    assert set(first) <= set(values)
```

The local seed is an explicit test input. Do not assume a seed makes every source of nondeterminism disappear: OS scheduling, clocks, network responses, and hash randomization are separate sources.

For UUIDs or timestamps, inject a factory/clock into the unit under test. Patch the symbol where the code looks it up, not necessarily where it was originally defined.

### 2.4 Network, DNS, and remote services

A unit test should not call a production API merely to verify response handling. Remote services change, rate-limit, require credentials, and fail for reasons unrelated to the code under test.

Use, in order of preference:
1. A deterministic fake for unit-level logic.
2. A local fake server when HTTP serialization, routing, or socket behavior matters.
3. Recorded, scrubbed responses for selected integration behavior.
4. A separately marked integration test against a controlled test service.

Set explicit connection and read timeouts in production HTTP clients. Tests should verify timeout and retry policies using a fake clock/client or controlled server, not wait for a real remote timeout.

`pytest-socket` can restrict network access:

```bash
uv add --dev pytest-socket
pytest --disable-socket
```

If a test intentionally needs a local socket, configure the plugin to allow only the necessary loopback access using the installed plugin's documented option. Do not disable the restriction globally just to make an unexplained test pass. Network isolation may expose tests that silently depended on the internet—that is useful information.

Recorded cassettes must not contain API keys, cookies, access tokens, personal data, or other secrets. Scrub sensitive headers and payloads before committing fixtures.

### 2.5 Filesystem, environment, locale, and ordering

Prefer `tmp_path` for per-test files and `tmp_path_factory` for intentionally shared session/worker fixtures. Avoid hard-coded paths under the repository, `/tmp`, or a user's home directory.

```python
def test_export_uses_requested_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_MODE", "test")
    output = tmp_path / "out.csv"

    write_report(output, rows=[{"name": "Ada", "count": 2}])

    assert output.read_text(encoding="utf-8") == "name,count\nAda,2\n"
```

Pytest's `monkeypatch` restores environment variables, attributes, `sys.path`, and current directory changes made through its API after the test. It cannot clean arbitrary external side effects such as a file created elsewhere or a remote record. Use a `yield` fixture or context manager for those.

Other environment hazards:
- **Timezone:** UTC timestamps and local calendar dates are different concepts. Set a known timezone in the test environment where supported, or inject a clock/timezone and test the intended semantics. `datetime.now()` without a timezone is difficult to reason about.
- **Locale:** decimal separators, collation, and date formatting can vary. Explicitly specify locale or test locale-independent behavior; avoid assuming a locale exists on every CI image.
- **Line endings and encoding:** use explicit UTF-8 and normalize line endings only if the contract permits it.
- **Ordering:** dicts preserve insertion order in modern Python, but the insertion order may originate from an unstable input. Sets are unordered. Sort output when the public contract promises canonical ordering; do not sort when order is semantically meaningful and should be preserved.
- **Resource limits:** CPU throttling, file descriptor limits, memory pressure, and slow disk can expose assumptions. A unit test should avoid arbitrary timing expectations; performance tests need explicit budgets and an appropriate environment.

---

## 3. Detecting flakiness systematically

A single passing run tells you very little about a rare failure. Use several complementary probes.

### 3.1 Run a test repeatedly

Install `pytest-repeat` if you need `--count`:

```bash
uv add --dev pytest pytest-repeat
pytest tests/test_worker.py::test_completion --count=50 -x
```

Expected outcome: either all 50 executions pass, or pytest stops at the first failure and reports it. Repetition can reveal a race, but 50 passing runs do not prove the test is deterministic.

Without a plugin, use a shell loop:

```bash
for i in $(seq 1 50); do
  pytest -q tests/test_worker.py::test_completion || break
done
```

On Windows PowerShell:

```powershell
1..50 | ForEach-Object {
  pytest -q tests/test_worker.py::test_completion
  if ($LASTEXITCODE -ne 0) { break }
}
```

Record the exact command, exit status, and environment. Avoid loops that discard output or always return success.

### 3.2 Randomize test order and retain the seed

```bash
uv add --dev pytest-randomly
pytest --randomly-seed=1234
```

`pytest-randomly` reports the seed it used; preserve that seed when a run fails. Re-run with the same seed to reproduce the order:

```bash
pytest --randomly-seed=1234 -x
```

If it fails, try the affected test alone:

```bash
pytest tests/path/test_module.py::test_name -q
```

Interpretation:
- **Fails alone:** likely intrinsic nondeterminism, environment dependence, or a true intermittent defect.
- **Passes alone, fails in suite:** suspect state contamination, order dependence, shared resources, or global plugin/fixture effects.
- **Fails only in one order:** find the smallest contaminating prefix or preceding test.

`pytest --lf` runs tests that failed previously; `pytest --ff` runs the full selection with previous failures first. Use them as separate commands—do not combine `--lf` and `--ff` in one invocation. They are useful for iteration but do not identify a contaminating test by themselves.

### 3.3 Run in parallel

```bash
uv add --dev pytest-xdist
pytest -n auto
```

Parallel execution can expose shared database schemas, filenames, ports, mutable services, and session fixtures that assumed one process. It can also change timing and CPU contention. A test passing with `-n auto` does not guarantee it is safe under every degree of parallelism.

For diagnosis, compare:
```bash
pytest -q
pytest -n 2 -q
pytest -n 4 -q
```

If the test suite shares a resource, allocate a namespace per worker using `worker_id` from `pytest-xdist` or a unique test identifier. Never rely on a fixed global database/table name when workers can write concurrently.

### 3.4 Isolate the failure and inspect warnings

```bash
pytest tests/test_pipeline.py::test_one_case -vv -x
pytest -W error::RuntimeWarning -W error::ResourceWarning
```

Promoting warnings to errors is useful for finding unawaited coroutines and resource leaks, but third-party libraries may emit unrelated warnings. Triage them deliberately; do not silence all warnings to get a green build.

Use `pytest-timeout` to bound hangs:

```bash
uv add --dev pytest-timeout
pytest --timeout=10
```

A timeout is a diagnostic guardrail, not a way to make a race correct. On some platforms or timeout modes, a timed-out test may not be safely interruptible; keep cleanup and process isolation in mind.

### 3.5 Reproducible test matrix

A practical escalation sequence:

1. Run the failing test once with verbose output.
2. Run it alone repeatedly.
3. Run the full file repeatedly.
4. Run the full suite with a fixed randomized seed.
5. Run the suite with different recorded seeds.
6. Run serial and parallel variants.
7. Re-run on the same Python/OS/dependency environment.
8. Compare the supported OS/Python matrix and resource limits.
9. If a race is suspected, deliberately vary CPU contention or worker count as a stress probe, while retaining the exact command and environment. On Linux, `taskset` can constrain CPU affinity (for example, `taskset -c 0 pytest -n 2 -q` where CPU 0 exists and permissions permit it); controlled CPU load can also expose scheduling assumptions. These are diagnostic stress tests, not deterministic reproductions or proof that a race is fixed.

Do not start with every dimension at once. Change one factor at a time so the evidence helps narrow the cause.

---

## 4. Root-cause workflow: reproduce → minimize → hypothesize → verify

This is the core debugging method for intermittent failures.

### Step 1 — Reproduce

Preserve the exact failure context:
- Git commit and working-tree changes.
- Full command, including seed, worker count, selection expression, and flags.
- Python version, OS/image, dependency lock state, locale, timezone, and relevant environment variables.
- Worker ID, test ID, retry attempt, resource limits, and relevant logs.
- Whether the test passes alone and whether it fails only after another test.

Do not print secrets into logs. Redact credentials and personal data before attaching logs to an issue.

### Step 2 — Minimize

Reduce the test selection while preserving the failure:
- Single test, then single file, then a smaller set of preceding tests.
- Remove unrelated fixtures or parametrized cases one at a time.
- Reduce concurrency while retaining the schedule that triggers the failure.
- Minimize the input dataset or request sequence.
- Keep the seed and environment fixed while changing one factor.

For order dependence, use manual bisection: split the candidate preceding tests into halves and determine which half retains the contamination. Some contamination requires a particular pair or sequence, so repeat the process rather than assuming one test is solely responsible.

### Step 3 — Hypothesize

Write a falsifiable explanation, not just “timing issue.” Example:

> Hypothesis: `test_write_report` leaves `APP_OUTPUT_DIR` set globally, and `test_default_output` reads it when run later. If removing the first test or resetting the variable makes the second test pass, the hypothesis gains support.

Identify the observation that would disprove the hypothesis. This prevents endless random changes.

### Step 4 — Verify

Change one thing:
- Add a clean fixture.
- Replace a sleep with an event.
- Inject a local RNG.
- Allocate unique files/ports/database schema.
- Close or join a leaked resource.
- Use a fake clock/network.

Then run the smallest reproduction, the randomized suite, repeated runs, and parallel execution as appropriate. Confirm the fix addresses the root cause, not merely the observed symptom.

### Example: identify the contaminating test

Suppose `test_uses_default_config` fails only in the full suite. Start with:

```bash
pytest tests/config/test_config.py::test_uses_default_config -q
pytest --randomly-seed=1234 -vv
```

Record the order reported by the seed. Run the suspected predecessor and failing test together, then bisect the preceding test set. Inspect module globals, `os.environ`, `os.chdir`, `logging` configuration, monkeypatching performed manually, and caches. If the culprit is an environment variable, use `monkeypatch.setenv`/`delenv` so pytest restores it; if the application reads a cached value at import time, patching the environment later may not reset the cache—reset or inject the configuration source as well.

---

## 5. Isolation patterns that hold up in CI

### 5.1 Use function-scoped fixtures by default

Function scope creates a fresh resource per test and should be the default when isolation matters. Broader fixture scopes can improve speed, but only when the resource is immutable or safely namespaced and its lifecycle is understood.

```python
import sqlite3
import pytest

@pytest.fixture
def db_connection(tmp_path):
    db_path = tmp_path / "test.sqlite"
    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            "CREATE TABLE events (event_id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
        )
        connection.commit()
        yield connection
    finally:
        connection.close()

def test_insert_event(db_connection):
    db_connection.execute("INSERT INTO events (name) VALUES (?)", ("loaded",))
    row = db_connection.execute("SELECT name FROM events").fetchone()
    assert row == ("loaded",)
```

A unique database file and explicit close prevent state from leaking between tests. If using a shared database server, a unique schema/database per test or worker plus deterministic teardown may be more appropriate.

### 5.2 Environment variables, current directory, and patched attributes

```python
def test_reads_mode_from_environment(monkeypatch):
    monkeypatch.setenv("APP_MODE", "test")
    assert read_mode() == "test"

def test_missing_mode_uses_default(monkeypatch):
    monkeypatch.delenv("APP_MODE", raising=False)
    assert read_mode() == "development"
```

For attributes, patch the name the module under test actually looks up:

```python
# service.py
from time import time

def created_at() -> float:
    return time()
```

```python
def test_created_at(monkeypatch):
    import service
    monkeypatch.setattr(service, "time", lambda: 123.0)
    assert service.created_at() == 123.0
```

Patching `time.time` would not necessarily affect `service.time`, because `service` imported the function into its own namespace. This is a common source of false confidence.

### 5.3 Reset registries, caches, and logging state

A registry fixture must establish the precondition before the test and restore state afterward:

```python
import pytest
from app.registry import HANDLERS

@pytest.fixture(autouse=True)
def isolated_handlers():
    HANDLERS.clear()
    try:
        yield
    finally:
        HANDLERS.clear()
```

This fixture deliberately leaves the registry empty after each test rather than restoring potentially contaminated state from a previous test. If a test needs handlers, register them explicitly as part of its own setup. Prefer dependency injection over manipulating globals when feasible.

For caches, clear them before each test and clear/restore them in teardown. For `functools.lru_cache`, call the function's `cache_clear()` in setup and teardown where available. Logging is trickier: avoid manually replacing root handlers unless the test owns that setup; use `caplog` for assertions and remove any handler the test explicitly adds in a `finally` block. Pytest's capture fixtures manage their own lifecycle.

Do not reseed the global `random` module in a fixture and assume the suite is now deterministic. It may interfere with other code and with test-order randomization. Inject a `random.Random(seed)` instance instead.

### 5.4 Unique IDs and xdist worker namespaces

Generate resource names from test/worker identity, not a constant like `test_db`:

```python
import os
import uuid
import pytest

@pytest.fixture
def resource_name(request):
    worker = os.environ.get("PYTEST_XDIST_WORKER", "master")
    node = request.node.nodeid.replace("/", "_").replace("::", "_")
    return f"test_{worker}_{node}_{uuid.uuid4().hex[:8]}"
```

A random suffix helps avoid collisions; if a deterministic name is required, combine a worker identifier with a test ID and ensure the backend namespace is unique. Never assume that uniqueness in one Python process implies uniqueness across CI jobs or machines.

### 5.5 Free ports: bind to port zero

Avoid hard-coded ports such as `8000`. Ask the operating system to allocate a free port:

```python
import socket

def test_server_binds_ephemeral_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        host, port = sock.getsockname()
        assert host == "127.0.0.1"
        assert port > 0
```

This tests ephemeral-port allocation only; it does not prove a later server can bind to the same port. A common but unsafe pattern is: find a free port, close the socket, then start a server on that port. Another process can claim the port in the gap (TOCTOU race). Prefer configuring the server to bind directly to port `0` and reading back the actual bound port, if the server framework supports it. Keep the listening socket open for the duration it is needed.

### 5.6 Database rollback and external-resource cleanup

For database tests, use a transaction per test and roll it back when the database and code under test support that model:

```python
@pytest.fixture
def transaction(connection):
    connection.execute("BEGIN")
    try:
        yield connection
    finally:
        connection.rollback()
```

This simplified pattern assumes the connection starts outside any existing transaction and that code under test does not commit the outer transaction. Some databases, ORM sessions, DDL statements, or nested transactions have different semantics; use the framework's documented savepoint/transaction fixture when necessary. A rollback cannot undo emails, HTTP requests, messages already published to a broker, or other external side effects. Fake those boundaries or allocate and clean up unique test resources.

For resources outside pytest's control, write teardown that is idempotent and executes in `finally`/fixture teardown. If cleanup fails, report it clearly; do not swallow cleanup errors silently.

---

## 6. Replace timing guesses with synchronization

### 6.1 Event-based thread test

```python
from threading import Event, Thread

def process_record(record: dict[str, int], finished: Event, output: list[int]) -> None:
    output.append(record["value"] * 2)
    finished.set()

def test_process_record():
    finished = Event()
    output: list[int] = []
    thread = Thread(
        target=process_record,
        args=({"value": 21}, finished, output),
        daemon=False,
    )
    thread.start()
    try:
        assert finished.wait(2.0), "worker did not finish in time"
        assert output == [42]
    finally:
        thread.join(2.0)
    assert not thread.is_alive(), "worker thread leaked"
```

The event synchronizes completion; the timeout prevents a hung test from blocking forever. The worker's simple append happens before it sets the event, so the waiting test observes the completed operation. For more complex shared state, use a queue, lock, or thread-safe result object.

### 6.2 Poll a condition with a deadline

Sometimes there is no event or callback. Poll the condition with a monotonic deadline and a small bounded interval:

```python
import time
from collections.abc import Callable

def wait_until(
    predicate: Callable[[], bool],
    *,
    timeout: float,
    interval: float = 0.01,
) -> bool:
    deadline = time.monotonic() + timeout
    while True:
        if predicate():
            return True
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(interval, remaining))
```

```python
def test_status_eventually_changes():
    start_operation()
    assert wait_until(lambda: read_status() == "complete", timeout=2.0)
```

This is bounded polling, not a fixed sleep. `time.monotonic()` is used because wall clocks can jump. Polling should be the fallback when the system exposes no better synchronization primitive; the predicate must be safe to poll and the timeout should be based on a reasonable service/test budget.

For async code, use async polling that awaits between checks, or better, await the operation's completion event. Do not block an event loop with `time.sleep`.

### 6.3 Controlled fakes for time and backoff

A unit test of retry/backoff logic should not actually wait seconds. Inject a clock/sleep abstraction:

```python
from collections.abc import Callable

def retry_operation(
    operation: Callable[[], int],
    *,
    sleep: Callable[[float], None],
    attempts: int = 3,
) -> int:
    if attempts < 1:
        raise ValueError("attempts must be positive")
    for attempt in range(attempts):
        try:
            return operation()
        except TemporaryError:
            if attempt == attempts - 1:
                raise
            sleep(0.1 * (2 ** attempt))
    raise AssertionError("unreachable")
```

```python
class TemporaryError(Exception):
    pass

def test_retry_backoff_without_waiting():
    calls = 0
    delays: list[float] = []

    def operation() -> int:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise TemporaryError()
        return 7

    result = retry_operation(operation, sleep=delays.append, attempts=3)

    assert result == 7
    assert calls == 3
    assert delays == [0.1, 0.2]
```

The fake `sleep` records intended delays without waiting. The test verifies policy, not the real passage of time. A separate integration test may verify that the actual scheduler honors the injected delay abstraction. Retries in application code can be correct when the external operation is transient and idempotent; retries of a flaky test are not a substitute for understanding why its outcome changes.

---

## 7. Concurrency, async code, and resource leaks

Concurrency flakiness often reveals an actual correctness defect.

### 7.1 Race conditions and lock ownership

A shared counter increment is a read-modify-write operation; do not assume a multi-step operation is atomic merely because an individual Python bytecode or the GIL exists.

```python
from threading import Lock, Thread

def increment_many(counter: list[int], lock: Lock, count: int) -> None:
    for _ in range(count):
        with lock:
            counter[0] += 1

def test_threaded_counter():
    counter = [0]
    lock = Lock()
    threads = [
        Thread(target=increment_many, args=(counter, lock, 5_000))
        for _ in range(4)
    ]
    for thread in threads:
        thread.start()
    try:
        for thread in threads:
            thread.join(timeout=10.0)
        assert all(not thread.is_alive() for thread in threads)
        assert counter[0] == 20_000
    finally:
        # Join again to make teardown explicit if an earlier assertion fails.
        for thread in threads:
            thread.join(timeout=2.0)
    assert all(not thread.is_alive() for thread in threads)
```

This tests a lock-protected counter and ensures all threads finish. In production code, encapsulate the counter and lock rather than exposing a mutable list. Never “fix” a race by adding a sleep; fix synchronization, ownership, or algorithmic assumptions.

### 7.2 Thread leaks

- Use non-daemon threads for work that must be observed and cleaned up.
- Give workers a cooperative stop signal and ensure they periodically check it.
- Join threads during teardown and fail if they remain alive.
- Avoid background threads that continue mutating globals after a test ends.
- When a worker may block indefinitely, use a bounded queue/operation timeout and a shutdown path.

A `join(timeout=...)` does not kill a thread. If it is still alive, the leak remains; the test must report that fact and the code needs a cooperative shutdown strategy.

### 7.3 Async task and event-loop leaks

- Await tasks you create.
- Cancel pending tasks and await their cancellation during cleanup.
- Use pytest's async fixture/plugin lifecycle rather than manually reusing a loop across tests without a clear policy.
- Do not call `asyncio.run()` from inside an already running event loop.
- Treat “coroutine was never awaited” as a defect, not harmless log noise.

Example with task cleanup:

```python
import asyncio
import pytest

async def wait_for_shutdown(stop: asyncio.Event) -> None:
    await stop.wait()

@pytest.mark.asyncio
async def test_background_task_is_cancelled():
    stop = asyncio.Event()
    task = asyncio.create_task(wait_for_shutdown(stop))
    try:
        assert not task.done()
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert task.done()
```

This example deliberately cancels and awaits the task, so its exception is retrieved and it cannot leak into another test. In real applications, prefer a task group or structured-concurrency scope so child tasks cannot outlive their parent operation.

### 7.4 Warnings and resource closure

Run targeted warning checks:

```bash
pytest -W error::RuntimeWarning -W error::ResourceWarning
```

Look for:
- Unclosed files, sockets, subprocess pipes, and database connections.
- Unawaited coroutines and unhandled task exceptions.
- Missing subprocess waits or thread joins.
- Event loops closed while tasks are still pending.
- Fixture teardown that fails to run due to abrupt process termination.

Use context managers (`with open(...)`, `with socket.socket(...)`) and `try/finally` for cleanup. When a process or server is started, make shutdown and wait/join part of the fixture contract.

---

## 8. Network isolation, timeouts, and useful failure evidence

### 8.1 Fake server or fake client?

Use a fake client when testing business logic such as “HTTP 503 triggers the fallback.” Use a local fake server when testing request serialization, headers, routing, or actual HTTP client integration. A local server should bind to loopback, use an ephemeral port, expose a readiness condition, and shut down and join in teardown.

Avoid remote internet calls in unit tests. Keep integration tests explicitly marked and separately configurable so a normal local test run does not unexpectedly require credentials or external availability.

### 8.2 Timeouts belong at boundaries

A robust client normally needs distinct connection and read/overall timeouts. Tests should assert the configured timeout or use a controlled fake to simulate timeout exceptions. A timeout prevents indefinite waiting; it does not prove a request is safe to retry. Retrying a non-idempotent write can duplicate side effects.

### 8.3 Capture evidence on failure

Collect enough context to reproduce without leaking secrets:
- Random seed and `pytest-randomly` seed.
- `PYTEST_XDIST_WORKER` or worker ID, node ID, retry number.
- Python version, OS/container image, dependency lock/hash.
- CPU/memory limits and relevant environment settings.
- Logs, exception traceback, task/thread state, resource identifiers.
- For async or distributed work, trace/correlation IDs and event sequence numbers.

Use structured logs and redact credentials. Do not dump the full environment or entire request headers indiscriminately.

---

## 9. Dependency and environment drift

A test can become intermittently red because the environment is not actually constant:
- Dependency ranges resolve to new versions.
- CI images or system packages change.
- DNS, remote services, or certificates change.
- CPU quotas and memory pressure differ across runners.
- Clock synchronization or timezone settings differ.
- Python versions differ in warnings, library behavior, or supported APIs.

Engineering controls:
1. Commit and enforce the project's lock file.
2. Capture Python, OS, and key dependency versions in CI artifacts.
3. Test supported Python/OS combinations intentionally rather than assuming one runner represents all environments.
4. Pin service/container images for reproducibility, while scheduling deliberate dependency-update jobs.
5. Avoid making unit tests depend on DNS, wall-clock synchronization, or external package indexes.
6. Keep a small, explicit integration suite for dependencies whose real behavior matters.

A lock file improves reproducibility but does not freeze the OS, system libraries, remote services, hardware behavior, or all sources of nondeterminism. Record enough metadata to distinguish environment drift from a code regression.

---

## 10. Flake-rate measurement and accountable ownership

Treat reliability as an engineering metric, not a collection of anecdotes.

### 10.1 Define the metric

One useful definition is:

\[
\text{flake rate} =
\frac{\text{test executions that fail and then pass on rerun without relevant change}}
{\text{eligible test executions}}
\]

Document the denominator. Teams may instead measure the proportion of test cases that exhibit at least one intermittent failure over a time window. These metrics answer different questions; do not compare them without aligning definitions.

Track at least:
- Test ID and owning team.
- First failure and subsequent result.
- Commit, branch, seed, worker, platform, and dependency context.
- Number of retries and time consumed.
- Time to diagnosis and age of any quarantine.
- Root cause and remediation PR/issue.

Do not interpret a retry-pass as proof that a failure was harmless. It is a useful flakiness signal that should trigger diagnosis.

### 10.2 Ownership policy

A workable policy:
- Every flaky test has a named owner and a linked issue.
- Quarantine is temporary, documented, and has an expiry/review date.
- The owner records the failure mode, impact, and remediation plan.
- Quarantined tests remain visible in reporting and are run in a dedicated job where possible.
- CI reports flake rate and total rerun cost.
- A rising flake rate triggers a reliability review; critical paths may block merges until fixed.
- Delete a test only when its assertion is obsolete or the behavior is intentionally no longer supported—not merely because it is inconvenient.
- Prefer “fix or remove obsolete coverage” over indefinite suppression.

### 10.3 Retries: when they help and when they hurt

If the project temporarily quarantines a test, `pytest-rerunfailures` supports a visible marker-based policy. Install it as a development dependency and register the marker when strict marker validation is enabled:

```bash
uv add --dev pytest-rerunfailures
```

```python
import pytest

@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_temporarily_quarantined_case():
    ...  # replace with the real test body; this is a policy illustration, not a runnable test
```

The marker requests reruns; it does not make the test reliable. Configure `flaky` in the project's pytest marker list when using `--strict-markers`, keep the initial failure visible in CI reporting, attach an issue and owner, and set an expiry/review date. Verify the installed plugin's supported options against its pinned version before adopting a repository-wide policy.

A retry can be useful as a **temporary diagnostic** to classify an intermittent failure or as a carefully designed production resilience mechanism for a transient, idempotent operation. It is harmful when:
- CI automatically retries until green and hides the initial failure.
- A race remains and only its probability is reduced.
- A test shares a database or port and retries sometimes land in a cleaner state.
- A test's result depends on external service health without being marked as integration.

If quarantine or reruns are unavoidable during repair, preserve the original failed result, label it clearly, link the issue, and enforce a time limit. Never report a retried pass as though the initial failure did not occur.

---

## 11. Deterministic simulation for distributed systems

Distributed systems combine network delay, retries, duplicate delivery, clocks, concurrency, and partial failure. Tests that use real timing and public networks are slow and nondeterministic.

Use seams that allow control over:
- **Clock:** inject a clock interface; use a fake clock that advances only when the test asks.
- **Network:** use a fake transport or in-memory message bus that can delay, reorder, duplicate, or drop messages deterministically.
- **Scheduler:** run state-machine transitions under a seeded schedule or explicit event sequence.
- **IDs:** inject deterministic IDs so traces and expected outputs are stable.
- **Failure injection:** explicitly choose when a request times out, a worker crashes, or an acknowledgement is lost.

Example of a deterministic delivery simulator:

```python
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

@dataclass(frozen=True)
class Message:
    key: str
    value: int

class FakeBus:
    def __init__(self) -> None:
        self.pending: deque[Message] = deque()

    def send(self, message: Message) -> None:
        self.pending.append(message)

    def deliver_next(self, handler: Callable[[Message], None]) -> None:
        if not self.pending:
            raise LookupError("no pending message")
        handler(self.pending.popleft())

def test_consumer_handles_explicit_delivery_order():
    bus = FakeBus()
    seen: list[tuple[str, int]] = []
    bus.send(Message("a", 1))
    bus.send(Message("b", 2))

    bus.deliver_next(lambda m: seen.append((m.key, m.value)))
    bus.deliver_next(lambda m: seen.append((m.key, m.value)))

    assert seen == [("a", 1), ("b", 2)]
    assert not bus.pending
```

This fake makes delivery order explicit; it does not simulate TCP or prove the real broker is correct. Extend it with explicit scenarios for duplicates, dropped messages, retries, and reordering. Test the application contract—for example, idempotent handling of duplicate message IDs—rather than asserting a single timing schedule.

Do not rely on a seeded random scheduler alone. Keep the seed, event trace, and minimal sequence so a failing schedule can be replayed exactly.

---

## 12. Common mistakes and their corrections

### Mistake 1: “It passed on retry, so it is fine.”

**Why it fails:** the first failure is evidence. A retry may simply avoid the race or contamination.

**Better:** preserve the failed attempt, record context, reproduce, and fix the root cause.

### Mistake 2: Add `time.sleep(1)` “to be safe.”

**Why it fails:** timing depends on machine load and scheduling.

**Better:** wait on an event/future, use a condition with a monotonic deadline, or replace the real dependency with a controlled fake.

### Mistake 3: All tests share one real database.

**Why it fails:** order, parallelism, stale rows, and partial cleanup affect later tests.

**Better:** use a transaction/savepoint or unique database/schema per test or worker; clean external effects separately.

### Mistake 4: Only reset state after the test.

**Why it fails:** if state was already polluted, the test still starts dirty.

**Better:** establish the required precondition before the test, then restore/clean in teardown.

### Mistake 5: Seed the global RNG once for the entire suite.

**Why it fails:** unrelated draws consume shared state and test order changes the sequence.

**Better:** pass a local `random.Random(seed)` or injected ID generator to the code under test.

### Mistake 6: Find a free port, close it, then bind the server.

**Why it fails:** another process can claim the port between the two operations.

**Better:** let the server bind directly to port zero and keep the bound socket open.

### Mistake 7: Run randomized tests once and assume all order issues are gone.

**Why it fails:** a single seed samples only one ordering.

**Better:** retain failing seeds, run several seeds, and use bisection to isolate contaminating tests.

### Mistake 8: Catch and ignore warnings.

**Why it fails:** unawaited coroutines, leaked files, and pending tasks may become future cross-test failures.

**Better:** promote relevant warnings to errors and close, await, cancel, or join resources correctly.

### Mistake 9: Quarantine without ownership or an expiry.

**Why it fails:** temporary suppression becomes permanent test-suite debt.

**Better:** link an issue, name an owner, preserve failure reporting, set a review date, and monitor quarantine age.

### Mistake 10: Sort everything to make tests pass.

**Why it fails:** sorting can hide a real ordering-contract bug.

**Better:** normalize only when ordering is explicitly irrelevant; otherwise assert the documented order.

---

## 13. Practical lab: harden a flaky data pipeline test

Consider a report generator that reads an environment variable, writes a file, uses a timestamp, and starts a background task. Your goal is to make the test independent of process state and wall-clock timing.

### Step A — identify the bad assumptions

```python
# Deliberately fragile example; do not copy into production tests.
def test_report():
    os.environ["REPORT_DIR"] = "/tmp/report"
    start_export()
    time.sleep(1)
    assert Path("/tmp/report/report.csv").exists()
```

Problems:
- Hard-coded shared output path.
- Environment mutation not restored.
- Fixed sleep guesses completion.
- Leftover output can make a broken export appear successful.
- Test does not inspect report contents or verify the task finished.
- A previous run may leave state behind.

### Step B — design explicit dependencies

Refactor the export operation so the caller supplies the output path and the worker returns completion through a `Future` or `Event`. Inject the clock if output includes timestamps. The test should create a fresh directory and assert the content, not just file existence.

One simple synchronous version:

```python
from pathlib import Path
import csv

def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "status"])
        writer.writeheader()
        writer.writerows(rows)
```

```python
def test_write_report_isolated(tmp_path):
    output = tmp_path / "run-1" / "report.csv"
    write_report(output, [{"name": "daily", "status": "complete"}])

    assert output.read_text(encoding="utf-8") == (
        "name,status\n"
        "daily,complete\n"
    )
```

This test has a fresh path and asserts the observable output. If asynchronous execution is part of the contract, test that layer separately with an event/future and bounded cleanup.

### Step C — validate the fix

Run:
```bash
pytest tests/test_report.py -q
pytest tests/test_report.py --count=50 -q
pytest --randomly-seed=1234 -q
pytest -n 2 -q
```

Expected outcome: all relevant runs pass, with no shared output collisions or timing assumptions. If any run fails, retain the failing command and evidence; do not simply increase the sleep or rerun until green.

---

## 14. Case study and post-mortem exercise

Choose a real flaky-test issue from an open-source project's issue tracker, pull request, or CI discussion. Use an issue with enough evidence to distinguish the symptom from the root cause. Do not invent a root cause when the public report does not establish one.

Write a post-mortem with these headings:

1. **Impact:** which tests/builds failed, how often, and what work was blocked?
2. **Observed symptom:** exact assertion, traceback, or timeout.
3. **Reproduction context:** commit, command, seed, worker/platform, dependencies, and whether the test failed alone.
4. **Minimized reproduction:** smallest test selection/input that still fails.
5. **Hypothesis:** the suspected mechanism and evidence that would disprove it.
6. **Root cause:** the demonstrated state leak, race, timing assumption, environment drift, or other defect.
7. **Fix:** the smallest change that removes the cause.
8. **Verification:** repeated runs, randomized order, parallel execution, platform matrix, or other checks relevant to the cause.
9. **Prevention:** ownership, a new invariant/test, resource cleanup, or a CI guardrail.
10. **Residual uncertainty:** what was not verified.

**Assessment rule:** a post-mortem that says only “CI was flaky; we added retries” is incomplete. The report must separate what was observed from what was proven.

---

## 15. Exercises

### Exercise 1 — root causes and isolation

List five distinct causes of flakiness and pair each with an isolation technique. Include at least one example involving global state, one involving time, one involving networking, one involving shared external resources, and one involving environment drift.

### Exercise 2 — find the contaminating test

A test passes alone but fails in the full suite. Describe the commands and bisection strategy you would use to find the earliest test or sequence that contaminates it. Explain why `pytest --lf` or `pytest --ff` is helpful but not sufficient.

### Exercise 3 — replace a two-second sleep

Rewrite a test that calls `start_background_thread()`, sleeps two seconds, and checks a result. Specify the synchronization primitive, timeout, cleanup, and what the test should assert if the worker does not finish.

### Exercise 4 — parallel database safety

Two xdist workers both write to `test_events`. Propose two viable designs: transaction rollback and worker/test-specific database namespaces. Explain which side effects rollback cannot undo.

### Exercise 5 — reproducible random failure

A test fails for one generated dataset in CI. Describe what metadata you would capture and how you would replace global random state with a local seeded generator.

### Exercise 6 — race versus resource leak

A test sometimes times out and emits `ResourceWarning`. Give a step-by-step investigation plan that checks task/thread lifecycle, socket/file closure, timeout behavior, and the possibility that the warning is a consequence rather than the root cause.

### Exercise 7 — governance

Draft a quarantine policy with owner, issue link, expiry/review date, reporting behavior, and a merge-blocking threshold. Explain how you would measure flake rate without hiding failures.

### Exercise 8 — distributed simulation

Extend `FakeBus` to test duplicate delivery and message reordering. Define the expected application invariant and make the event sequence explicit. Do not use real sleeps or a public broker.

---

## 16. Self-check with model answers

### 1. List five root causes of flaky tests and an isolation technique for each.

- Shared mutable global state → use a fresh instance or fixture that establishes a clean precondition and restores state in teardown.
- Real-time sleeps → synchronize with an event/future or poll a condition using a monotonic deadline.
- Randomness → inject a local seeded `random.Random` and preserve the seed.
- Network dependence → fake the client/server or use scrubbed record-and-replay fixtures; restrict unexpected sockets.
- Shared database/files/ports → unique per-test or per-worker namespace, transaction rollback where supported, `tmp_path`, and explicit cleanup.
- Timezone/locale drift → inject the clock and specify timezone/formatting rules; run a deliberate platform matrix.

### 2. How would you find which earlier test pollutes global state?

First run the failing test alone and repeatedly. Re-run the suite with the same `pytest-randomly` seed and record the order. Test the failing case with likely predecessors, then bisect the preceding tests while preserving the failure. Inspect module globals, environment, current directory, logging, registries, caches, and resources. Fix the contaminating setup/teardown or remove the shared mutable dependency. `--lf`/`--ff` helps prioritize failures but does not isolate their cause.

### 3. Rewrite a test that sleeps two seconds waiting for a background thread.

Have the worker signal an `Event` or complete a `Future`. Start the worker, wait on that signal with a finite timeout, assert the result, and always join/shut down the worker in `finally`. If the signal is not received, fail with a useful message and still attempt cleanup. A fixed sleep does not establish that the worker completed.

### 4. Why are retries not a substitute for root-cause fixes?

Retries can make an intermittent defect less visible without changing the defect. They can hide state leakage, races, and external side effects; they also increase CI time and normalize ignoring the first failure. Keep retry results visible and use them as evidence, then remove the underlying nondeterminism.

### 5. What evidence should a flaky-test report include?

Exact command and test ID, commit, random seed, worker ID, Python/OS/dependency versions, relevant locale/timezone/environment, failure traceback/logs, input data, whether it fails alone, repetition count, and a minimized reproduction. Redact secrets and personal data.

### 6. What should be done when a test is quarantined?

Assign a named owner, link an issue, preserve the initial failure in reporting, set an expiry/review date, monitor age and flake rate, and run it separately where possible. Quarantine is a temporary safety valve, not deletion of evidence or a permanent substitute for repair.

---

## 17. Completion checklist

- [ ] I can define flakiness and explain why rerun-until-green culture is dangerous.
- [ ] I can recognize shared state, time, randomness, network, races, ports, files, locale, ordering, and resource-limit failures.
- [ ] I can repeat a test, randomize order, run in parallel, and retain the seed.
- [ ] I can use `tmp_path`, `monkeypatch`, function-scoped fixtures, unique resources, and cleanup.
- [ ] I can replace timing guesses with events, futures, bounded polling, or controlled fakes.
- [ ] I can isolate database state and understand the limits of transaction rollback.
- [ ] I can investigate thread/task leaks, unawaited coroutines, and resource warnings.
- [ ] I can reproduce, minimize, hypothesize, and verify a flaky failure.
- [ ] I can measure flake rate and apply accountable quarantine policy.
- [ ] I can simulate distributed message sequences deterministically and write an evidence-based post-mortem.

**Next lesson:** `06-testing-cli-and-subprocess-programs.md`.
