# Testing Time, Randomness, and Concurrency

**Stage 1 — Programming & Computational Thinking · Module 16 — Advanced Testing and Test Architecture · Lesson 07**

## Learning objectives

By the end of this lesson, you should be able to:

- explain why wall clocks, random-number generators, thread scheduling, async task scheduling, external services, and floating-point reductions can make tests nondeterministic;
- control time through injected callables/clock objects and fake sleepers, and understand when time-freezing libraries help;
- inject isolated `random.Random` and NumPy `Generator` instances rather than changing global random state;
- test TTLs, retries, exponential backoff, jitter, and calendar boundaries without real waiting;
- coordinate threads and async tasks with explicit synchronization and bounded cleanup;
- test random algorithms with invariants and statistical methods that have defensible tolerances;
- distinguish deterministic synchronization tests from probabilistic stress tests;
- reason about race conditions, duplicate delivery, idempotency, and “exactly once” claims;
- test data pipelines for logical dates, late-arriving data, backfills, faults, and floating-point variation.

Examples use Python 3.11+ syntax and pytest. NumPy, pytest-asyncio/AnyIO, freezegun, and time-machine are optional tools and are identified as such. The core examples use the standard library unless otherwise stated.

---

**Basic — foundations:** identify nondeterministic dependencies, inject a clock, isolate random generators, and understand patching and frozen-time tools.

## 1. The central principle: control nondeterminism at boundaries

A unit test is easiest to reason about when the same input produces the same observable result. Nondeterminism enters when code silently reads or controls something outside its explicit inputs.

| Source | Example | Reliable control |
|---|---|---|
| Wall clock | `datetime.now()` decides whether a record is expired | Inject a clock or freeze the relevant time API |
| Elapsed time | timeout measured with `time.time()` | Inject a monotonic clock |
| Waiting | `time.sleep(2)` before asserting | Inject a sleeper or synchronize with an event |
| Randomness | global `random.random()` | Inject a dedicated seeded generator |
| Threads | worker and test race to access shared state | Events, barriers, queues, locks, bounded joins |
| Async tasks | one coroutine runs before another reaches a checkpoint | Events, controlled fake dependencies, async test utilities |
| External boundary | API response is delayed or dropped | Fake client, fault-injecting transport, local test server |
| Calendar | local midnight or daylight-saving transition | Explicit timezone-aware datetimes and boundary cases |
| Floating point | parallel reduction sums values in a different order | Tolerance, stable algorithms, documented numerical contract |

The best architecture separates **pure policy** from **effectful adapters**:

```python
def should_expire(expires_at, now):
    return now >= expires_at
```

This policy is deterministic when its arguments are fixed. The caller decides how `now` is obtained. The same principle applies to retry policy, scheduling decisions, random sampling, and pipeline partition selection.

Do not try to mock every source of nondeterminism globally. Prefer a narrow seam: inject the clock into the service that needs it, the random generator into the sampler, and the sleep function into retry code. Keep integration tests that verify the real adapters still work.

---

## 2. Time: model the clock as a dependency

### 2.1 Wall time and monotonic time are different contracts

- **Wall clock** answers “what date and time is it?” Use aware `datetime` values for timestamps, expiration dates, business dates, and audit records.
- **Monotonic clock** answers “how much time has elapsed?” `time.monotonic()` is designed not to go backwards due to wall-clock adjustments. Its origin is unspecified; do not persist it as a calendar timestamp.
- **Process time** (`time.process_time()`) measures CPU time consumed by the process, not elapsed waiting time.

Network time synchronization, administrator changes, VM clock adjustments, and daylight-saving rules can move wall time forward or backward. A duration measured as `time.time() - start` can therefore be wrong. For a timeout, prefer a monotonic deadline:

```python
import time

def wait_until_ready(is_ready, timeout, *, monotonic=time.monotonic):
    deadline = monotonic() + timeout
    while not is_ready():
        if monotonic() >= deadline:
            return False
    return True
```

This sketch intentionally has no sleep and would busy-spin; production code should wait on an event/condition or use a polling interval while still checking a monotonic deadline. The example illustrates the clock contract, not a recommended polling loop.

### 2.2 Inject a callable clock

```python
from collections.abc import Callable
from datetime import datetime, timezone

Clock = Callable[[], datetime]

def is_expired(expires_at: datetime, now: Clock) -> bool:
    if expires_at.tzinfo is None or expires_at.utcoffset() is None:
        raise ValueError("expires_at must be timezone-aware")
    current = now()
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("clock must return an aware datetime")
    return current >= expires_at

def test_is_expired():
    fixed_now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    clock = lambda: fixed_now
    assert is_expired(
        datetime(2025, 12, 31, tzinfo=timezone.utc), clock
    )
    assert not is_expired(
        datetime(2026, 1, 2, tzinfo=timezone.utc), clock
    )
```

Expected result: both assertions pass. No real clock is read.

A callable is a good fit when the only required operation is “give me the current instant.” Use a protocol or clock object when the application needs several related operations:

```python
from typing import Protocol
from datetime import datetime, timezone
import time

class ClockProtocol(Protocol):
    def now(self) -> datetime: ...
    def monotonic(self) -> float: ...

class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def monotonic(self) -> float:
        return time.monotonic()
```

The concrete implementation is an adapter. Business logic should depend on the interface, not call `datetime.now()` in multiple places.

**Avoid this default argument:**

```python
# Avoid capturing a value at function-definition time:
# def f(now=datetime.now()): ...
```

That captures one datetime when the module is imported. A callable default such as `now=None` followed by a call inside the function, or explicit dependency injection, avoids the bug. For library code, an explicit clock parameter often makes tests and semantics clearer.

### 2.3 Fake clocks and fake sleepers

A fake clock should advance only when the test or system under test tells it to. It must not consult real time.

```python
class FakeClock:
    def __init__(self, start: float = 0.0):
        self.current = start

    def monotonic(self) -> float:
        return self.current

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("sleep duration must be non-negative")
        self.current += seconds

clock = FakeClock(10)
clock.sleep(2.5)
assert clock.monotonic() == 12.5
```

Expected result: the assertion passes. This is suitable for synchronous logic that treats `sleep` as a dependency. It does **not** automatically advance the real asyncio event loop, wake real OS timers, or coordinate real threads. Fake time and real scheduling are separate domains.

### 2.4 Freeze time with a library—know its limits

Tools such as `freezegun` and `time-machine` can freeze or travel wall-clock APIs and are useful for integration tests where many modules call date/time functions. They reduce invasive injection when testing legacy code. Install and configure the chosen library in the project’s test dependencies.

However:

- freezing wall time does not necessarily freeze every clock, native extension, database server, remote service, or monotonic timer;
- behavior depends on library version and configuration;
- a frozen wall clock can make code that expects real elapsed time behave strangely;
- concurrent tests can interfere if a library patches process-global functions;
- a fake clock injected at a narrow boundary is usually easier to reason about for retry policy and timeout arithmetic.

Prefer explicit injection for new code. Use time travel to characterize legacy code or exercise broad integration paths, then retain a small real-clock smoke test where appropriate.

### 2.5 Monkeypatch the lookup site, not the concept

Suppose a module does:

```python
# app.py
from time import time

def created_at():
    return time()
```

Patching `time.time` may not change `app.created_at()`: `app` already holds its own name `time`. Patch the symbol where it is looked up:

```python
def test_created_at(monkeypatch):
    import app
    monkeypatch.setattr(app, "time", lambda: 123.0)
    assert app.created_at() == 123.0
```

For `import time`, code uses `time.time()` and patching `app.time.time` can work, but remember that `app.time` refers to the shared `time` module object: patching its attribute may affect other code in the process. Restore it with `monkeypatch` and keep the patch scoped.

Patching `datetime.datetime.now` directly is often difficult because `datetime.datetime` is a built-in immutable type. Better approaches are:
1. inject a callable or clock object;
2. patch a `datetime` name imported into the module with a controlled replacement;
3. use a time-freezing library if its semantics fit the test.

A broad patch is not proof that all time sources have been controlled.

---

**Intermediate — deterministic boundary tests:** fake time and sleeping, verify TTL/retry boundaries, cover calendar transitions, and synchronize concurrent work explicitly.

## 3. TTL caches, retries, backoff, and jitter

### 3.1 TTL expiration is a boundary rule

Decide whether an entry expires when `now >= expires_at` or only when `now > expires_at`. Then test the exact boundary.

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass
class Entry(Generic[T]):
    value: T
    expires_at: float

class TTLCache(Generic[T]):
    def __init__(self, clock):
        self._clock = clock
        self._entries: dict[str, Entry[T]] = {}

    def put(self, key: str, value: T, ttl: float) -> None:
        if ttl < 0:
            raise ValueError("ttl must be non-negative")
        self._entries[key] = Entry(value, self._clock() + ttl)

    def get(self, key: str):
        entry = self._entries.get(key)
        if entry is None:
            return None
        if self._clock() >= entry.expires_at:
            del self._entries[key]
            return None
        return entry.value

def test_ttl_boundary():
    now = [100.0]
    cache = TTLCache(lambda: now[0])
    cache.put("job", "ready", ttl=5)
    assert cache.get("job") == "ready"
    now[0] = 104.999
    assert cache.get("job") == "ready"
    now[0] = 105.0
    assert cache.get("job") is None
```

Expected result: all assertions pass. This cache is intentionally small and not thread-safe; production caches need a concurrency contract, eviction policy, and perhaps a monotonic clock. Use monotonic values for elapsed TTLs, not wall-clock timestamps.

### 3.2 Retry policy should expose sleep and randomness

A test should verify *which waits were requested*, not wait in real time. Separate the policy from the actual sleeper.

```python
from collections.abc import Callable
import random
from typing import TypeVar

T = TypeVar("T")

def retry(
    operation: Callable[[], T],
    *,
    attempts: int,
    sleep: Callable[[float], None],
    rng: random.Random,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    jitter: bool = True,
):
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    if base_delay < 0 or max_delay < 0:
        raise ValueError("delays must be non-negative")

    for attempt in range(attempts):
        try:
            return operation()
        except (TimeoutError, ConnectionError):
            if attempt == attempts - 1:
                raise
            cap = min(max_delay, base_delay * (2 ** attempt))
            delay = rng.uniform(0.0, cap) if jitter else cap
            sleep(delay)
    raise AssertionError("unreachable")
```

Test it without sleeping. This test continues from the `retry()` definition immediately above; in a standalone test module, keep the implementation and test together:

```python
def test_retry_jitter_is_bounded_and_deterministic():
    calls = 0
    waits = []

    def operation():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise TimeoutError("temporary")
        return "ok"

    result = retry(
        operation,
        attempts=3,
        sleep=waits.append,
        rng=random.Random(42),
        base_delay=1,
        max_delay=10,
        jitter=True,
    )

    assert result == "ok"
    assert calls == 3
    assert len(waits) == 2
    assert 0 <= waits[0] <= 1
    assert 0 <= waits[1] <= 2
```

Expected result: the test passes; it does not depend on wall time. The seed makes the generator sequence repeatable within the intended Python implementation contract, but the key assertions are semantic bounds and attempt counts, not hard-coded floating-point samples.

**Production considerations:**

- Catch only retryable exceptions; never retry every `Exception` by default.
- Define whether `attempts` means total attempts or retries after the first call.
- Bound the delay and the overall operation deadline.
- Jitter reduces synchronized retry storms; test the bounds and policy, not a single exact random value.
- Consider server-provided `Retry-After`, cancellation, idempotency keys, and observability.
- An injected sleeper should be a no-op/recording fake in a unit test. Do not use a fake sleeper for an integration test intended to verify actual timer wiring.

### 3.3 Test timeouts using deadlines, not elapsed wall time

Avoid tests like `assert function() finishes in under 0.1 seconds`; scheduler load and CI virtualization make tight timing assertions fragile. Unit-test the deadline calculation with a fake monotonic clock. Separately use a coarse watchdog timeout to prevent a hung test from blocking CI.

A timeout is a safety limit, not a synchronization mechanism. `sleep(0.1)` does not guarantee that a worker has run. Wait for an explicit event, queue item, or condition and use a timeout only as a bound.

---

## 4. Calendar time: zones, DST, leap years, and boundaries

### 4.1 Use aware instants and explicit business zones

A naive datetime has no unambiguous timezone. For an event timestamp, use UTC or an aware datetime. For business rules such as “run at 09:00 in New York,” preserve the named IANA timezone and the local scheduling rule.

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc
NEW_YORK = ZoneInfo("America/New_York")

def local_business_date(instant: datetime, zone: ZoneInfo) -> str:
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("instant must be timezone-aware")
    return instant.astimezone(zone).date().isoformat()

def test_business_date_boundary():
    just_before_midnight = datetime(2026, 1, 1, 4, 59, tzinfo=UTC)
    just_after_midnight = datetime(2026, 1, 1, 5, 1, tzinfo=UTC)
    assert local_business_date(just_before_midnight, NEW_YORK) == "2025-12-31"
    assert local_business_date(just_after_midnight, NEW_YORK) == "2026-01-01"
```

Expected result: both assertions pass. They explicitly test the local date boundary rather than depending on the machine timezone.

### 4.2 Daylight-saving transitions are not ordinary clock arithmetic

In a zone with daylight-saving transitions, some local times do not exist (spring-forward gap), and some occur twice (fall-back fold). Attaching a `ZoneInfo` object does not by itself validate whether a local wall time was a real, unique instant.

For an absolute timestamp, store/compare aware UTC instants. For a recurring local schedule, define product policy for nonexistent and ambiguous times (skip, shift, choose first occurrence, choose second occurrence) and test that policy explicitly. Do not assume every local day is exactly 24 elapsed hours.

A useful diagnostic for a local time is a UTC round-trip:

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def valid_local_candidates(local_naive: datetime, zone: ZoneInfo):
    if local_naive.tzinfo is not None:
        raise ValueError("pass a naive local wall time")
    candidates = []
    for fold in (0, 1):
        aware = local_naive.replace(tzinfo=zone, fold=fold)
        round_trip = aware.astimezone(timezone.utc).astimezone(zone)
        if round_trip.replace(tzinfo=None) == local_naive and round_trip.fold == fold:
            candidates.append(aware)
    # For ordinary times, folds may represent the same offset; deduplicate by instant.
    return list({c.astimezone(timezone.utc): c for c in candidates}.values())
```

Use this as a teaching utility, and verify it against the project’s supported timezone database and Python versions before adopting it as a scheduling library. Many applications should use a dedicated, well-tested scheduling abstraction instead of rolling their own DST policy.

### 4.3 Leap years, month ends, and week boundaries

```python
import calendar
from datetime import date, timedelta

def last_day_of_month(year: int, month: int) -> date:
    return date(year, month, calendar.monthrange(year, month)[1])

def test_calendar_edges():
    assert last_day_of_month(2024, 2) == date(2024, 2, 29)
    assert last_day_of_month(2025, 2) == date(2025, 2, 28)
    assert last_day_of_month(2026, 4) == date(2026, 4, 30)
    assert date(2026, 1, 5).weekday() == 0  # Monday
    assert date(2026, 1, 4) + timedelta(days=1) == date(2026, 1, 5)
```

Expected result: the test passes. Test month-end rules using dates, not “add 30 days.” “One month later” is a business rule: define what happens when the target month has fewer days.

Also test inclusive/exclusive boundaries, ISO week-year transitions, midnight in the business zone, and the same event represented in UTC and local time. Do not hard-code the host’s locale or timezone into a test.

---

## 5. Randomness: isolate generator state

### 5.1 Inject `random.Random`, not the module-global generator

```python
import random

def choose_partition(partitions: list[str], rng: random.Random) -> str:
    if not partitions:
        raise ValueError("partitions cannot be empty")
    return rng.choice(partitions)

def test_choose_partition():
    rng = random.Random(42)
    first = choose_partition(["a", "b", "c"], rng)
    second = choose_partition(["a", "b", "c"], rng)
    assert first in {"a", "b", "c"}
    assert second in {"a", "b", "c"}
    # Reproducibility is isolated to this generator:
    replay = random.Random(42)
    assert [choose_partition(["a", "b", "c"], replay) for _ in range(2)] == [
        first, second
    ]
```

Expected result: the test passes. A dedicated generator avoids unrelated tests consuming or reseeding global state. A seed is not a universal guarantee across every algorithm, library version, or language runtime; use it to make a test reproducible in its declared environment, and assert invariants where exact sequences are not the contract.

Never use `random.Random` for secrets, authentication tokens, or security-sensitive identifiers; use `secrets` or a cryptographically secure source. Tests should inject a fake secure-token provider if deterministic outputs are needed.

### 5.2 NumPy random generators

If NumPy is a project dependency, use `numpy.random.default_rng(seed)` and pass the resulting `Generator` into the function under test:

```python
# Optional dependency: NumPy
import numpy as np

def noisy_measurements(values, rng: np.random.Generator):
    return np.asarray(values) + rng.normal(0.0, 0.1, size=len(values))

def test_noisy_measurements_reproducible():
    a = noisy_measurements([10.0, 20.0], np.random.default_rng(7))
    b = noisy_measurements([10.0, 20.0], np.random.default_rng(7))
    np.testing.assert_array_equal(a, b)
```

Expected result: the arrays are equal in the same supported environment. NumPy explicitly recommends the `Generator` API for new code. Avoid global `np.random.seed()` in a large suite because it couples test order and shared state. For parallel simulations, use independently derived streams (for example, `SeedSequence`) rather than giving every worker the same seed and accidentally duplicating samples.

### 5.3 Test invariants first, distributions second

For a shuffle, assert length and multiset preservation; for a sampler, assert range and shape; for a randomized algorithm, assert validity and termination. Exact-output assertions are appropriate only if exact output is part of the contract and the generator/algorithm is deliberately pinned.

Statistical tests require special care. A test that fails when a valid random sample is merely unusual is flaky by design. Prefer:
1. fixed-seed examples for repeatable regression cases;
2. invariants that must always hold;
3. distribution tests with a precomputed statistical bound, a documented false-positive rate, and enough samples to make the test meaningful;
4. more extensive statistical validation in a dedicated test/analysis job, not every quick unit-test run.

For example, for a fair Bernoulli sample of size \(n\), the count has mean \(n/2\) and standard deviation \(\sqrt{n}/2\). A broad bound such as several standard deviations can catch gross bias, but no finite sample proves fairness. Select the threshold before observing the test result, and account for repeated tests increasing the overall false-positive probability.

```python
import random
import math

def test_bernoulli_sampler_is_not_grossly_biased():
    rng = random.Random(2026)
    n = 10_000
    successes = sum(rng.random() < 0.5 for _ in range(n))
    expected = n / 2
    sigma = math.sqrt(n * 0.5 * 0.5)
    assert abs(successes - expected) < 5 * sigma
```

Expected result: passes reliably for this fixed seed. The tolerance is intentionally loose; it detects gross deviations, not subtle statistical defects. Do not turn this into a claim that a random algorithm is correct based on one seed.

---

**Advanced — concurrency and production reliability:** force interleavings, reason about idempotency and distributed failure, stress-test without overclaiming, and validate pipeline behavior across logical time.

## 6. Thread tests: coordinate events, not sleeps

### 6.1 Event-driven synchronization

A `threading.Event` is a one-bit signal. One thread calls `set()`, and waiting threads unblock. It is useful when the test needs to know that a worker reached a checkpoint.

```python
import threading

def worker(started: threading.Event, release: threading.Event, result: list[str]):
    started.set()
    if not release.wait(timeout=2):
        raise TimeoutError("test did not release worker")
    result.append("done")

def test_worker_checkpoint():
    started = threading.Event()
    release = threading.Event()
    result: list[str] = []
    thread = threading.Thread(
        target=worker, args=(started, release, result), daemon=False
    )
    thread.start()
    try:
        assert started.wait(timeout=2), "worker never reached checkpoint"
        assert result == []
        release.set()
        thread.join(timeout=2)
        assert not thread.is_alive(), "worker leaked or deadlocked"
        assert result == ["done"]
    finally:
        release.set()
        thread.join(timeout=2)
    assert not thread.is_alive()
```

Expected result: the test passes. Every wait and join is bounded, and the `finally` block releases the worker if an assertion fails. A timeout is a failure bound; the synchronization is provided by the events. In production, prefer non-daemon workers with explicit shutdown when resource cleanup matters.

If a worker can raise, capture the exception in a thread-safe result/queue and assert it in the main test. Unhandled exceptions in a worker do not automatically propagate as a normal exception from `join()`.

### 6.2 Barriers and queues

- **Barrier**: coordinates a known group of participants at a rendezvous point. Set a timeout and handle `BrokenBarrierError`; if a participant fails before reaching it, other participants must not wait forever.
- **Queue**: transfers work/results safely between threads. `queue.Queue` is often preferable to hand-built shared lists and flags.
- **Lock**: protects a critical section; it does not make unrelated multi-step invariants atomic.
- **Condition**: waits for a predicate to become true; always wait in a loop because wakeups can be spurious and another thread may change the predicate.

A queue-based test should verify the result and then join the worker with a timeout. Avoid asserting a particular order unless the protocol guarantees that order.

### 6.3 A deterministic test for a shared-counter race

The goal is to force a lost update rather than hope the scheduler happens to expose one. This example creates an explicit interleaving using a barrier between the read and write. It is a controlled demonstration, not a model of every possible race.

```python
import threading

def test_lost_update_without_lock():
    counter = 0
    both_read = threading.Barrier(2)

    def increment():
        nonlocal counter
        current = counter
        both_read.wait(timeout=2)
        counter = current + 1

    threads = [threading.Thread(target=increment) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=2)

    assert all(not thread.is_alive() for thread in threads)
    assert counter == 1  # both read 0; one increment is lost
```

Expected result: the assertion `counter == 1` passes because both workers read before either writes. This deliberately buggy implementation reliably demonstrates the lost-update schedule under this controlled barrier.

A locked implementation:

```python
def increment_safely(counter_box, lock):
    with lock:
        counter_box[0] += 1
```

A corresponding test should start many workers, join all of them, and assert the final count. Do not put a barrier *inside* a critical section if the barrier requires more participants than can enter the lock; that creates a deadlock. Also do not assume that every compound operation is safe merely because one Python build happens to have a GIL.

### 6.4 Bounded joins and leaked-thread checks

Always design test cleanup before starting a worker:

1. decide how to signal shutdown;
2. start the worker;
3. wait for a specific readiness/result event with a timeout;
4. release/cancel it in `finally`;
5. join with a timeout;
6. assert it is no longer alive.

Do not rely on daemon threads to hide leaks. Be careful when joining a thread that waits forever on a resource the test has not closed. If the test fails before releasing a barrier or event, the cleanup path must still unblock the worker.

### 6.5 Stress testing is evidence, not proof

Repeat tests with more workers, varied workload, randomized yields, CPU load, and—where useful—a temporarily smaller `sys.setswitchinterval()` to increase opportunities for thread switches. Restore the previous interval in a `finally` block because it is process-global, and remember that changing it only influences scheduling opportunities; it does not force a particular interleaving. Tools such as `pytest-repeat` can repeat a scenario, while a captured seed and environment metadata make failures easier to reproduce. Run under different Python builds, OSs, and CI worker counts. Record the seed, Python version, platform, worker count, and failing schedule metadata.

These techniques can reveal races but cannot prove a race is absent. A passing stress run only means that tested schedules did not expose the defect. Use deterministic interleaving tests for known hazards, lock/ownership design, invariant checks, state-machine testing, and code review in addition to stress tests.

Free-threaded CPython builds (where the GIL is disabled) make reliance on accidental GIL serialization more visible. Treat free-threaded compatibility as an explicit test matrix dimension where supported. Do not claim that free-threaded execution automatically makes every race reproducible or that a GIL-enabled build has no races.

---

## 7. Asyncio: control task checkpoints and clean up

Use `pytest-asyncio` or AnyIO according to the project’s async framework. Do not mix event-loop ownership models casually: a test fixture and library should agree on which loop runs the tasks.

```python
import asyncio
import pytest

async def producer(ready: asyncio.Event, release: asyncio.Event):
    ready.set()
    await release.wait()
    return "complete"

@pytest.mark.asyncio
async def test_task_interleaving_is_controlled():
    ready = asyncio.Event()
    release = asyncio.Event()
    task = asyncio.create_task(producer(ready, release))
    try:
        async with asyncio.timeout(2):
            await ready.wait()
        assert not task.done()
        release.set()
        async with asyncio.timeout(2):
            assert await task == "complete"
    finally:
        release.set()
        if not task.done():
            task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
```

Expected result: passes with `pytest-asyncio` installed and configured. The events define the ordering; the timeouts prevent a hang. The `finally` block releases and awaits the task so it does not leak into another test.

Important distinctions:

- `asyncio.timeout()` is a real event-loop timeout; it does not itself freeze time.
- Injected fake monotonic clocks are useful for policy arithmetic, but they do not advance the event loop’s internal clock unless the chosen test framework explicitly supports that.
- For async timeout/backoff logic, inject the sleep/wait abstraction or use framework-provided test clocks (for example, Trio’s testing tools where appropriate).
- Always await created tasks or cancel and await them. “Task was destroyed but it is pending” and unawaited-coroutine warnings indicate cleanup defects.
- Do not use `asyncio.run()` inside a test already managed by an async pytest plugin.
- A timeout should be long enough to avoid scheduler noise but finite enough to bound hangs. It is not the primary synchronization mechanism.

For deterministic async interleavings, place explicit events at the relevant checkpoints. For more complex protocols, use state-machine/property-based testing or a deterministic scheduler if the framework offers one. Trio’s `trio.testing` has specialized test helpers; AnyIO provides cross-backend test support but fake-clock features depend on the backend and tool versions. Verify the API of the exact installed version instead of assuming a generic “fake event loop” interface.

---

## 8. Idempotency, duplicate delivery, and “exactly once”

Distributed systems commonly retry after timeouts because the caller cannot tell whether the remote operation completed. The server may have committed the write and lost the response. Therefore, a retry can produce duplicate delivery even when the caller sends only one logical request.

A robust design often provides **at-least-once delivery plus idempotent effects**, using a unique idempotency key and a transactional uniqueness constraint. “Exactly once” should be defined at a specific boundary; end-to-end exactly-once behavior across arbitrary services is not created by a retry loop alone.

A small in-memory example:

```python
class IdempotentLedger:
    def __init__(self):
        self._applied: dict[str, int] = {}
        self.balance = 0

    def apply(self, operation_id: str, amount: int) -> bool:
        if operation_id in self._applied:
            if self._applied[operation_id] != amount:
                raise ValueError("operation id reused with a different amount")
            return False
        # In a real database, record the id and effect atomically.
        self._applied[operation_id] = amount
        self.balance += amount
        return True

def test_duplicate_delivery_has_one_effect():
    ledger = IdempotentLedger()
    assert ledger.apply("event-17", 5) is True
    assert ledger.apply("event-17", 5) is False
    assert ledger.balance == 5
    try:
        ledger.apply("event-17", 7)
    except ValueError as exc:
        assert str(exc) == "operation id reused with a different amount"
    else:
        raise AssertionError("expected conflicting reuse to be rejected")
    assert ledger.balance == 5
```

Expected result: passes. This toy object is not thread-safe and is not durable. In production, the idempotency record and business effect must commit atomically; otherwise a crash between them can still cause a duplicate or lost effect.

Test:
- same key/same payload repeated;
- same key/different payload (usually reject as a conflict);
- timeout after commit but before response;
- process restart after commit;
- concurrent duplicates;
- retries across transaction boundaries;
- replay and out-of-order delivery;
- exactly-once claims at the database, queue, and downstream side-effect boundaries.

A strong test injects failure at a specific point—for example, “commit succeeded but acknowledgement was dropped”—and verifies the observable business invariant, not merely the number of calls made by a mock.

---

## 9. Fault injection and system boundaries

Unit tests can inject exceptions deterministically. Integration tests can use fake transports or controlled local servers. Tools such as Toxiproxy can simulate latency, connection resets, and dropped connections in an environment where that extra infrastructure is justified.

A simple fail-on-the-Nth-call fake:

```python
class FailOnCall:
    def __init__(self, fail_at: int):
        self.calls = 0
        self.fail_at = fail_at

    def send(self, payload: bytes) -> str:
        self.calls += 1
        if self.calls == self.fail_at:
            raise ConnectionError("injected failure")
        return "ack"

def test_fail_on_nth_call_injects_transient_failure():
    sender = FailOnCall(fail_at=2)
    assert sender.send(b"a") == "ack"
    try:
        sender.send(b"b")
    except ConnectionError as exc:
        assert str(exc) == "injected failure"
    else:
        raise AssertionError("expected injected failure")
```

Expected result: passes. This verifies the fake's failure behavior; it does not itself test a retry policy. For a retrying service, wrap this fake in the retry abstraction and assert the final state and recorded attempts.

Useful fault cases include:
- the Nth read/write fails;
- an acknowledgement is lost after a successful commit;
- a dependency returns slowly or closes a connection;
- a batch is interrupted after writing a partial output;
- a checkpoint is written before/after a commit;
- duplicate and late messages arrive;
- disk space or permissions fail;
- cancellation arrives during cleanup.

Avoid globally monkeypatching sockets or time APIs when a fake dependency can represent the same fault. Boundary-level injection is easier to scope, replay, and diagnose.

---

## 10. Time-travel testing for data pipelines

Separate **processing time** (when the job runs) from **event time/logical date** (which data interval the job is processing). A reproducible batch pipeline should take its logical date or interval explicitly.

```python
from datetime import date

def select_partition(run_date: date) -> str:
    return f"events/date={run_date.isoformat()}"

def test_backfill_partition_selection():
    assert select_partition(date(2026, 3, 1)) == "events/date=2026-03-01"
    assert select_partition(date(2026, 2, 28)) == "events/date=2026-02-28"
```

Expected result: passes without reading the current date. In a real pipeline, pass the logical interval to transformations and isolate input/output locations for each test.

Test these scenarios explicitly:

1. rerun the same logical date and verify idempotency;
2. process late-arriving data and verify the defined correction/backfill policy;
3. run dates in a different order and ensure results do not depend on wall-clock execution time;
4. fail after producing an intermediate artifact, then resume and verify partial outputs are cleaned or safely reused;
5. ensure checkpoints describe committed work, not merely attempted work;
6. verify retention/TTL logic at exact cutoff boundaries;
7. test daylight-saving and business-zone partition selection if the pipeline uses local business dates.

Time travel does not mean changing the machine clock for the entire test process. Usually the most reliable design is to pass `run_date`, `start_instant`, or a logical interval explicitly.

---

## 11. Floating-point nondeterminism

Floating-point addition is not associative:

\[
(a + b) + c \ne a + (b + c)
\]

in finite-precision arithmetic. Parallel reductions, different chunking, compiler optimizations, BLAS implementations, and CPU architectures may sum values in different orders. A test that compares a floating result exactly can fail even when the result is acceptable under the numerical contract.

```python
import math
import pytest

def test_numeric_result_uses_tolerance():
    actual = 0.1 + 0.2
    assert actual == pytest.approx(0.3, rel=1e-12, abs=1e-12)
    assert math.isclose(actual, 0.3, rel_tol=1e-12, abs_tol=1e-12)
```

Expected result: passes. `pytest.approx` and `math.isclose` need tolerances chosen for the problem—not copied blindly. The absolute tolerance matters near zero; relative tolerance matters for values across scales.

For data pipelines:
- specify acceptable numerical error and units;
- use stable summation such as `math.fsum` when appropriate;
- avoid assuming parallel reductions are bitwise reproducible;
- compare array outputs with library-aware tolerance tools;
- distinguish numerical noise from an actual algorithmic regression;
- use exact equality for integers, identifiers, schemas, and values whose contract is exact.

A tolerance that is too wide can hide real bugs. Test known error bounds and edge cases, including large/small magnitude mixtures and cancellation.

---

## 12. Scheduling, fake schedulers, and deterministic simulation

Scheduling logic should be separated from the mechanism that wakes a job. For example, a pure function can decide the next due instant from a supplied `now`, schedule policy, and prior state. Test that function with fixed inputs. Test the scheduler adapter separately with a small integration test.

A fake scheduler can maintain a queue of `(deadline, callback)` pairs and advance a logical clock when instructed. That lets a test run “one hour later” without waiting an hour. Ensure that:
- advancing to a deadline executes only the tasks due under the documented inclusive/exclusive rule;
- callbacks scheduled by callbacks are handled consistently;
- cancellation removes or marks tasks so they do not execute;
- recurring tasks cannot create an infinite loop during a single advance;
- exceptions from callbacks are surfaced to the test;
- ordering for equal deadlines is defined if it matters.

For distributed protocols, deterministic simulation can combine a fake clock, fake network, seeded event selection, and a model of node state. Hypothesis stateful testing can generate action sequences; model-checking approaches (for example, TLA+ awareness) help specify invariants and interleavings. These approaches explore more states than hand-written examples, but their value depends on the fidelity of the model and the state space explored.

---

## 13. Common mistakes and reliable fixes

| Mistake | Why it fails | Better approach |
|---|---|---|
| Patching `time.time` when code imported `time` by name | The code uses a different module-level binding | Patch the lookup site or inject a clock |
| Patching `datetime.datetime.now` directly | Built-in type is not a convenient patch seam | Inject a callable, replace the module-local name, or use a time-freezing library |
| Calling real `sleep()` in unit tests | Scheduler/load differences make timing fragile and slow | Inject sleeper; use events/queues for synchronization |
| Seeding global randomness in every test | Test order and parallel execution share mutable generator state | Pass a dedicated `Random`/NumPy `Generator` |
| Asserting one exact random result without a contract | Algorithm/version changes can invalidate incidental output | Assert invariants; pin exact sequences only when required |
| Using `time.time()` for durations | Wall time may jump | Use `time.monotonic()` and a monotonic deadline |
| Assuming frozen wall time freezes all timers | Monotonic clocks, native libraries, and remote services may differ | Freeze only intended APIs; inject duration dependencies |
| Using arbitrary sleeps to order threads/tasks | A delay is not a happens-before relationship | Events, barriers, queues, conditions, or explicit async events |
| Unbounded `join()` or `await` | A bug can hang the entire suite | Bounded waits plus cleanup and liveness assertions |
| Relying on daemon threads | Resources may be abandoned during shutdown | Explicit stop signal, close resources, join, assert termination |
| Putting a barrier inside a lock incorrectly | Participants may be unable to reach the barrier | Design the rendezvous and critical section separately |
| Treating stress tests as proof of no races | Only a subset of schedules ran | Deterministic interleaving tests, invariants, design review, stress |
| Assuming the GIL makes compound operations safe | Thread safety is not implied for multi-step invariants; free-threaded builds change assumptions | Protect invariants with locks/queues or explicit ownership |
| Claiming end-to-end exactly once from a retry loop | A timeout may occur after the remote commit | Idempotency key, atomic commit, duplicate-delivery tests |
| Testing only successful external calls | Failures, lost acknowledgements, and partial outputs are untested | Inject faults at specific boundaries and verify final state |
| Comparing floating-point results exactly | Summation order and hardware can differ | Define numerical tolerance and stable algorithm requirements |
| Using host-local timezone in tests | CI machines may have different zones or DST rules | Explicit `ZoneInfo` and aware datetimes |
| Assuming every local time exists once | DST gaps and folds violate that assumption | Define and test policy for ambiguous/nonexistent local times |

---

## 14. A practical testing strategy

Use layers rather than trying to make one test prove everything.

1. **Pure policy tests:** expiration comparisons, retry delay calculations, partition naming, calendar decisions, invariants.
2. **Injected-boundary tests:** fake clock, fake sleeper, seeded RNG, fail-on-Nth-call transport.
3. **Deterministic concurrency tests:** explicit events/barriers/queues that force a known interleaving or verify a protocol invariant.
4. **Integration tests:** real event loop, real database transaction, scheduler adapter, or local transport with bounded timeouts.
5. **Stress tests:** repeated runs, many workers, varied seeds, CPU load, multiple interpreter builds and OSs.
6. **Production observability:** record retry count, idempotency conflicts, queue lag, timeout causes, logical run date, and correlation identifiers.

For flaky failures, use the discipline **reproduce → minimize → hypothesize → verify**. Record the seed, test order, worker ID, Python version, platform, dependency versions, and relevant timing/load metadata. Rerunning is useful to gather evidence, not to declare a failure harmless. Fix the cause or quarantine a test only temporarily with ownership and an expiry date.

---

## 15. Hands-on exercises

Try each exercise before reading the solution outline.

### Exercise 1 — Clock injection

Implement `is_expired(expires_at, now)` with timezone-aware datetimes. Test before, exactly at, and after expiration. Reject naive datetimes.

**Solution outline:** inject `now: Callable[[], datetime]`; define `now >= expires_at` as expired; test all three boundary cases with one fixed UTC instant.

### Exercise 2 — Retry and jitter

Implement a retry function with at most four total attempts, exponential backoff capped at eight seconds, jitter, and injected `sleep` and `random.Random`. Verify the waits without real sleep.

**Solution outline:** record delays in a list; assert there are no more than three waits, each delay is within its cap, and a fixed seed replays the same sequence. Verify non-retryable exceptions escape immediately.

### Exercise 3 — TTL cache

Use a fake monotonic clock to test a cache entry just before and exactly at expiry. Decide whether zero TTL is immediately expired.

**Solution outline:** document the boundary rule and test it explicitly. Avoid wall-clock time for elapsed TTL.

### Exercise 4 — Calendar edges

Test February in a leap year, month-end handling, local midnight in an explicit `ZoneInfo`, and a DST transition relevant to your product.

**Solution outline:** separate instant conversion from local scheduling policy; do not assume `+ timedelta(days=1)` always means the same local wall time.

### Exercise 5 — Thread coordination

Rewrite a test that sleeps two seconds waiting for a worker. Use an event, bounded wait, cleanup in `finally`, bounded join, and a final `is_alive()` assertion.

**Solution outline:** the worker sets a readiness event when it reaches the checkpoint; the test waits for that signal, then releases it and joins. A sleep alone does not establish ordering.

### Exercise 6 — Demonstrate and fix a race

Write a shared-counter implementation and a deterministic test that forces both threads to read before either writes. Then add a lock and verify the correct count.

**Solution outline:** use a barrier between read and write to force a lost update. Do not put the barrier inside the lock. Keep the failing example intentionally separate from the production implementation.

### Exercise 7 — Async cleanup

Write an async producer/consumer test coordinated by `asyncio.Event`. Ensure cancellation and cleanup happen if an assertion fails.

**Solution outline:** use `asyncio.timeout` around waits, release/cancel tasks in `finally`, and await every task to completion or cancellation.

### Exercise 8 — Duplicate delivery

Simulate a successful commit followed by a lost acknowledgement, then retry the same operation ID. Assert that the business effect occurs once.

**Solution outline:** the idempotency record and effect must be atomic in a real database. Test same-key/different-payload conflicts too.

### Exercise 9 — Statistical test

Create a fixed-seed sampler test that verifies output range and shape, then a separate loose distribution check. Explain the expected false-positive risk.

**Solution outline:** invariant assertions should carry most correctness weight. Choose statistical bounds before running the test and do not interpret one passing sample as proof of fairness.

### Exercise 10 — Pipeline time travel

Run the same logical partition twice, simulate late data, and inject a failure after an intermediate write. Define the expected backfill and cleanup behavior.

**Solution outline:** pass the logical date explicitly; isolate temporary outputs; make reruns idempotent; commit checkpoints only after durable work.

---

## 16. Self-check questions with model answers

### 1. Why is injecting a clock better than patching `time.time`?

**Model answer:** Injection makes the time dependency explicit, local, and easy to control. It avoids patching the wrong lookup site and accidentally affecting unrelated code. A clock interface can distinguish wall time from monotonic time. Patching remains useful for legacy seams, but it is more coupled to module import style and global state.

### 2. Test a retry-with-jitter function without sleeping and without randomness flakiness.

**Model answer:** Inject a `sleep` callable that records requested durations and a dedicated seeded `random.Random` instance. Force the operation to fail a known number of times and then succeed. Assert attempt count, result, number of waits, and each wait’s permitted range/cap. If the precise sequence is part of the contract, pin it intentionally; otherwise avoid brittle exact-delay assertions. The test never calls real sleep.

### 3. Write a test that reliably fails (before a lock is added) for a race on a shared counter.

**Model answer:** Use two threads and a barrier between reading the shared value and writing the incremented value. The barrier guarantees both threads read the old value before either write, so the final count is one rather than two. Join with a timeout and assert no thread remains alive. Then protect the read-modify-write sequence with a lock and test the correct final count. This demonstrates one controlled lost-update interleaving; it does not enumerate every possible race.

---

## 17. Final review checklist

Before merging code that depends on time, randomness, or concurrency, ask:

- [ ] Is wall time separated from elapsed-time measurement?
- [ ] Are business timestamps timezone-aware, and is the business timezone explicit?
- [ ] Are DST gaps/folds, leap days, month ends, and scheduling boundaries tested where relevant?
- [ ] Are clock, sleeper, random generator, and external effects injectable?
- [ ] Do TTL and retry tests cover exact boundaries without real waiting?
- [ ] Are random tests based on invariants first and defensible tolerances second?
- [ ] Are thread tests coordinated by events/barriers/queues rather than arbitrary sleeps?
- [ ] Does every started thread/task have bounded, explicit cleanup?
- [ ] Are known races tested with controlled interleavings, with stress testing used as additional evidence rather than proof?
- [ ] Are free-threaded Python and platform differences considered where the application supports them?
- [ ] Are duplicate delivery and failure-after-commit scenarios covered?
- [ ] Are fault injection and partial-output/checkpoint behavior tested?
- [ ] Are floating-point tolerances tied to the numerical contract?
- [ ] Does the core policy remain deterministic when boundary dependencies are faked?

The target is not to eliminate every real-world variation from all tests. It is to make each test’s assumptions explicit, deterministic where possible, bounded where not, and diagnostic when a failure occurs.
