# Exception Groups and `except*`

> **Target runtime:** Python 3.12+ for new examples.  
> **Feature introduction:** `ExceptionGroup`, `BaseExceptionGroup`, and `except*` were introduced in **Python 3.11** (PEP 654).  
> **Compatibility:** Python 3.10 and earlier cannot parse `except*` syntax. The `exceptiongroup` backport provides group classes on older versions, but it cannot add new syntax to the language.

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain why one batch or concurrent operation can produce several independent failures.
- Construct and inspect `ExceptionGroup` and `BaseExceptionGroup` instances.
- Use `except*` to handle selected exception types while preserving unmatched failures.
- Read nested groups and use `.subgroup()` and `.split()` with types or predicates.
- Understand how `asyncio.TaskGroup`, `asyncio.gather()`, and `concurrent.futures` expose failures.
- Accumulate validation errors with record-specific context and design safe retry, rollback, and partial-success policies.
- Test, log, and trace grouped failures without losing their structure or leaking sensitive data.

---

## 1. Mental model: one operation, several failures

Ordinary exception handling usually models one failure at a time: a function raises one exception, and the caller handles it or lets it propagate. Some operations have multiple independent units of work:

- validating 500 input records;
- running several independent asynchronous tasks;
- waiting for multiple futures;
- closing several resources after a batch has failed;
- running multiple checks where reporting only the first defect would force repeated fix-and-run cycles.

In these cases, failing fast at the first error can hide useful diagnostic information. An exception group is a **tree of exception objects**: its leaves are the individual failures, and nested groups preserve meaningful boundaries such as task, batch, or subsystem.

```text
ExceptionGroup("batch failed")
├── ValueError("invalid quantity")
├── TypeError("unexpected input type")
└── ExceptionGroup("worker-3")
    ├── TimeoutError("service timed out")
    └── PermissionError("access denied")
```

Three distinctions are essential:

1. **The group is an exception object.** It has a message, traceback, notes, and an `.exceptions` tuple.
2. **The leaves are exception objects too.** Each leaf has its own type, message, traceback, and potentially notes.
3. **Handling a subset is not the same as consuming the whole group.** `except*` gives its handler a subgroup containing matching exceptions. Unmatched parts continue through later `except*` clauses or propagate after the `try` statement.

Exception groups preserve structure; they do not decide business policy. Your code must still choose whether to retry, reject a batch, roll back, quarantine records, or continue with partial success.

## 2. `ExceptionGroup` and `BaseExceptionGroup`

### 2.1 Construct a group

```python
errors = [
    ValueError("quantity must be positive"),
    TypeError("quantity must be an integer"),
]

group = ExceptionGroup("record validation failed", errors)
print(group.message)
print(len(group.exceptions))
print([type(exc).__name__ for exc in group.exceptions])
```

Expected output:

```text
record validation failed
2
['ValueError', 'TypeError']
```

`.exceptions` is a tuple, not a mutable list. `ExceptionGroup` accepts instances of `Exception` (including subclasses), and cannot contain `KeyboardInterrupt`, `SystemExit`, or other direct `BaseException` subclasses that are not `Exception`.

### 2.2 When is `BaseExceptionGroup` needed?

`BaseExceptionGroup` can contain any `BaseException`, including `Exception` subclasses and control-flow exceptions such as `KeyboardInterrupt`. If every member is an `Exception`, constructing `BaseExceptionGroup(...)` automatically produces an `ExceptionGroup` instead. Prefer `ExceptionGroup` for ordinary application failures; use `BaseExceptionGroup` only when there is a deliberate reason to aggregate non-`Exception` base exceptions.

```python
ordinary = BaseExceptionGroup("ordinary", [ValueError("bad value")])
assert isinstance(ordinary, ExceptionGroup)

mixed_base = BaseExceptionGroup(
    "base-level failures",
    [ValueError("bad value"), KeyboardInterrupt()],
)
assert type(mixed_base) is BaseExceptionGroup
```

Do not routinely catch `BaseException` or group cancellation and process-control exceptions as normal business errors. Most application recovery should operate on `Exception` and leave cancellation, `KeyboardInterrupt`, and `SystemExit` semantics intact.

### 2.3 Group nesting and construction constraints

Groups may contain other exception groups. They may not be empty, and their members must be exception instances. A nested group is useful when its boundary has meaning—for example, one subgroup per shard or worker. Avoid flattening away that boundary unless a consumer explicitly needs a flat list.

```python
worker_a = ExceptionGroup("worker A", [TimeoutError("request timed out")])
worker_b = ExceptionGroup("worker B", [ValueError("bad payload")])
all_workers = ExceptionGroup("parallel ingest failed", [worker_a, worker_b])

assert len(all_workers.exceptions) == 2
assert isinstance(all_workers.exceptions[0], ExceptionGroup)
```

`len(group.exceptions)` counts direct children, not all leaves. To inspect all leaf failures, traverse recursively; a helper appears in Section 10.

## 3. `except*`: selective handling

`except*` is designed to match a subset of an exception group. It differs from ordinary `except`:

| Ordinary `except` | `except*` |
| --- | --- |
| Matches the exception object being raised as a whole. | Selects matching exceptions within a group, preserving group structure where possible. |
| `except ValueError` does not catch an `ExceptionGroup` merely because one leaf is a `ValueError`. | `except* ValueError` selects the `ValueError` leaves from a group. |
| Handler receives the raised exception object. | Handler receives the matching subgroup object, normally still an exception group—not each leaf separately. |
| A matched exception is handled as a whole. | Only the matching portion is handled; unmatched portions continue. |

### 3.1 First example

```python
try:
    raise ExceptionGroup(
        "batch",
        [ValueError("bad quantity"), TypeError("wrong type"), ValueError("bad price")],
    )
except* ValueError as matched:
    print("value errors:", [str(exc) for exc in matched.exceptions])
except* TypeError as matched:
    print("type errors:", [str(exc) for exc in matched.exceptions])
```

Expected output:

```text
value errors: ['bad quantity', 'bad price']
type errors: ['wrong type']
```

Here, `matched` is an `ExceptionGroup` containing the selected `ValueError` leaves. It is not a single `ValueError`. For a nested original group, the matching subgroup can itself remain nested.

### 3.2 Trace a mixed group through handlers

Consider this original group:

```text
original = ExceptionGroup("ingest", [
    ValueError("bad schema"),
    TimeoutError("service timeout"),
    PermissionError("access denied"),
])
```

The handlers below are evaluated in order against the portions still available for matching:

```python
try:
    raise ExceptionGroup(
        "ingest",
        [ValueError("bad schema"), TimeoutError("service timeout"),
         PermissionError("access denied")],
    )
except* ValueError as validation_group:
    # Receives a subgroup containing ValueError("bad schema").
    print("validation:", [type(e).__name__ for e in validation_group.exceptions])
except* TimeoutError as retry_group:
    # Receives a subgroup containing TimeoutError("service timeout").
    print("retry:", [type(e).__name__ for e in retry_group.exceptions])
```

Expected output:

```text
validation: ['ValueError']
retry: ['TimeoutError']
```

The `PermissionError` did not match either handler. It remains unhandled and propagates after the `try` as a group containing the unmatched portion (possibly with the original group metadata and nesting preserved). If a later handler matches `PermissionError`, that portion can be handled there. If no handler matches it, it is not silently discarded.

A handler can also raise a new exception. Such a new failure is combined with any unmatched original portion when the `except*` statement finishes. Therefore, do not assume that the last handler has consumed the entire original group simply because it ran.

### 3.3 Handler rules

- Do not mix ordinary `except` and `except*` clauses in the same `try` statement. They have different matching semantics. Use an outer `try` if a separate ordinary exception boundary is needed.
- `return`, `break`, and `continue` are prohibited inside an `except*` handler because the language must reconcile all matching and unmatched portions of the group. Set a flag or collect a result in the handler, then act after the `try` statement.
- Multiple `except*` clauses can run for one raised group, each for its own matching subset.
- A matching handler receives a subgroup, not the original group wholesale and not necessarily a flat list of leaves.
- Avoid `except* BaseException` as a generic cleanup or recovery strategy. It can match control-flow exceptions that should not be treated as ordinary failures.

If you need to catch a non-group exception alongside groups, use nested `try` statements:

```python
try:
    try:
        await_operation()  # illustrative function; may raise a group
    except* TimeoutError as timeouts:
        record_timeouts(timeouts)
except OSError as exc:
    handle_outer_os_error(exc)
```

The functions in this illustration are placeholders; this snippet demonstrates syntax and structure, not a standalone program. The outer `except OSError` handles an ordinary `OSError` raised directly by `await_operation()`. It does **not** inspect an unmatched `OSError` leaf inside an exception group; that leaf propagates as part of the remaining group. If grouped `OSError` leaves also need selective handling, add an `except* OSError` clause to the inner `try` (or explicitly route the group through a separate group-handling boundary).

## 4. Nested groups, `.subgroup()`, and `.split()`

Both methods filter a group recursively and preserve the group tree and metadata for the selected portions.

- `group.subgroup(condition)` returns the matching portion, or `None` if nothing matches.
- `group.split(condition)` returns `(matching, non_matching)`. Either side may be `None`.
- `condition` may be an exception type (or tuple of types) or a predicate that accepts an exception object and returns a truth value.
- A predicate can see nested group objects as well as leaf exceptions. For leaf classification, write the predicate to classify the intended exception types explicitly.

```python
errors = ExceptionGroup(
    "pipeline",
    [
        TimeoutError("source A timed out"),
        ExceptionGroup(
            "source B",
            [ValueError("invalid record"), TimeoutError("source B timed out")],
        ),
    ],
)

retryable, permanent = errors.split(TimeoutError)
assert retryable is not None
assert permanent is not None

print(retryable)
print(permanent)
```

The `retryable` result retains the nested structure necessary to identify that one timeout came from `source B`; the `permanent` result contains the `ValueError` branch. Exact traceback display varies with formatting and is not used as a programmatic assertion.

A predicate example:

```python
class RetryableError(Exception):
    pass

class PermanentError(Exception):
    pass

failures = ExceptionGroup(
    "jobs",
    [RetryableError("temporary outage"), PermanentError("invalid configuration")],
)

retryable, not_retryable = failures.split(lambda exc: isinstance(exc, RetryableError))
```

Use `.subgroup()` when you need one subset; use `.split()` when you need both sides. Neither method retries, logs, mutates, or consumes the original group automatically.

## 5. Bulk validation with record-specific context

Bulk validation often benefits from reporting all invalid rows in one pass. Add notes to the individual exception before placing it in the group so that the row context stays attached to the leaf failure. `BaseException.add_note()` was introduced in Python 3.11.

```python
from collections.abc import Iterable, Mapping


def validate_record(row: Mapping[str, object]) -> None:
    quantity = row.get("quantity")
    if not isinstance(quantity, int) or isinstance(quantity, bool):
        raise TypeError("quantity must be an integer")
    if quantity <= 0:
        raise ValueError("quantity must be positive")


def validate_all(rows: Iterable[Mapping[str, object]]) -> None:
    failures: list[Exception] = []
    for row_number, row in enumerate(rows, start=1):
        try:
            validate_record(row)
        except (TypeError, ValueError) as exc:
            exc.add_note(f"row_number={row_number}")
            # Do not put raw row contents in notes: they may contain secrets or PII.
            failures.append(exc)

    if failures:
        raise ExceptionGroup("bulk validation failed", failures)
```

Example caller:

```python
try:
    validate_all([
        {"quantity": 2},
        {"quantity": 0},
        {"quantity": "many"},
    ])
except* ValueError as values:
    print("invalid quantities:", len(values.exceptions))
except* TypeError as types:
    print("wrong quantity types:", len(types.exceptions))
```

This design deliberately separates **validation** from **policy**. Validation collects failures; the caller decides whether to reject the entire batch, quarantine only invalid rows, or proceed with valid rows. If one validation failure should prevent later checks for that same row, the simple example is appropriate. If you need multiple independent checks per row, collect multiple exceptions per row and give each note a stable row identifier plus a field/check identifier.

### 5.1 Choosing the group message and error data

Use a stable high-level message such as `"bulk validation failed"`. Put actionable, bounded context on individual exceptions with notes. Avoid embedding full records, credentials, access tokens, or large payloads into exception messages or notes; tracebacks and logs are often exported to third-party systems.

If consumers need machine-readable details, define domain exception classes with fields such as `row_number`, `field_name`, or `error_code`. Notes are excellent diagnostics, but should not be your only structured API contract because callers would need to parse human-readable strings.

## 6. Concurrent failures with `asyncio.TaskGroup`

`asyncio.TaskGroup` (Python 3.11+) is a structured-concurrency context manager. When a child task fails with an ordinary exception, the task group cancels remaining child tasks, waits for them to finish, and raises the failures it collected as an exception group. More than one child may fail before cancellation takes effect, so the final group can contain multiple errors.

```python
import asyncio


async def fetch_source(name: str, delay: float, *, fail: bool = False) -> str:
    await asyncio.sleep(delay)
    if fail:
        raise TimeoutError(f"{name} timed out")
    return f"data from {name}"


async def load_sources() -> None:
    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(fetch_source("A", 0.01, fail=True))
            group.create_task(fetch_source("B", 0.02, fail=True))
            group.create_task(fetch_source("C", 1.00))
    except* TimeoutError as timeouts:
        # The handler gets a subgroup, which may contain one or more timeouts.
        print("source timeouts:", len(timeouts.exceptions))


asyncio.run(load_sources())
```

This illustrates TaskGroup's failure model; exact group membership depends on scheduling and cancellation timing. Do not promise that both `A` and `B` will always fail visibly: after the first failure, task `B` may be cancelled before it reaches its own failure. Tests should control synchronization rather than rely on sleeps when they need deterministic multi-failure behavior.

For a deterministic demonstration, synchronize both children at an `asyncio.Barrier` and have each raise immediately after the barrier releases. This makes both child failures ready before TaskGroup can cancel a sibling at a later suspension point:

```python
async def demonstrate_two_failures() -> None:
    barrier = asyncio.Barrier(3)  # two children plus the parent
    try:
        async with asyncio.TaskGroup() as group:
            async def fail(name: str) -> None:
                await barrier.wait()
                raise ValueError(name)

            group.create_task(fail("A"))
            group.create_task(fail("B"))
            await barrier.wait()
    except* ValueError as errors:
        print(sorted(str(exc) for exc in errors.exceptions))


asyncio.run(demonstrate_two_failures())
```

Expected output:

```text
['A', 'B']
```

This pattern is for testing grouped failure handling, not a general production synchronization recipe. If the worker raises a different exception type or has another suspension point after the barrier, the resulting group may differ.

### 6.1 Cancellation semantics

`asyncio.CancelledError` subclasses `BaseException`, not `Exception`. TaskGroup uses cancellation internally to stop sibling tasks after a failure. Usually, a child task that ends by cancellation does not appear as an ordinary failure leaf in the resulting `ExceptionGroup`.

- Use `try/finally` for cleanup in coroutines.
- If you catch `asyncio.CancelledError` to perform work, generally re-raise it after cleanup.
- Do not swallow cancellation casually. Structured-concurrency primitives rely on cancellation state and propagation to work correctly.
- `except* Exception` does not match `CancelledError` because it is not an `Exception` subclass.
- `KeyboardInterrupt` and `SystemExit` receive special treatment by TaskGroup: after sibling cleanup, they are re-raised rather than treated as ordinary grouped application errors.

```python
async def worker() -> None:
    resource = await acquire_resource()
    try:
        await process(resource)
    except asyncio.CancelledError:
        await record_cancelled_work()
        raise
    finally:
        await resource.aclose()
```

`acquire_resource`, `process`, and `record_cancelled_work` are placeholders for application functions. In real code, ensure cleanup itself is cancellation-safe and bounded; do not create an unbounded second wait during shutdown.

## 7. `TaskGroup` versus `gather(return_exceptions=True)`

These APIs have different contracts; choose based on the workflow rather than style.

| Behavior | `asyncio.TaskGroup` | `asyncio.gather(..., return_exceptions=True)` |
| --- | --- | --- |
| Failure representation | Raises grouped failures when the context exits. | Returns exceptions as result-list elements. |
| Sibling behavior after a child raises an ordinary exception | Cancels remaining children and waits for them. | With `return_exceptions=True`, continues collecting outcomes; it does not cancel siblings just because one child failed. |
| Result association | Tasks can be named/retained explicitly; TaskGroup itself is not a result list. | Results preserve input order, including exception objects at the corresponding positions. |
| Structured lifetime | Context exit waits for all child tasks. | Lifetime is controlled by the gather await and the awaitables supplied. |
| Best fit | Work that should be treated as one structured unit and fail together. | Independent operations where partial results and per-item failure objects are expected outputs. |

Example of explicit partial results:

```python
async def load_independently(names: list[str]) -> list[str | BaseException]:
    return await asyncio.gather(
        *(fetch_source(name, 0.01, fail=(name == "bad")) for name in names),
        return_exceptions=True,
    )


async def inspect_results() -> None:
    outcomes = await load_independently(["A", "bad", "C"])
    successes = [item for item in outcomes if not isinstance(item, BaseException)]
    failures = [item for item in outcomes if isinstance(item, BaseException)]
    print("successes:", len(successes), "failures:", len(failures))
```

For typing and policy, note that `gather(return_exceptions=True)` can return `BaseException` instances, not just `Exception` subclasses. Avoid accidentally treating `CancelledError`, `KeyboardInterrupt`, or `SystemExit` as routine business outcomes. If cancellation semantics matter, inspect those cases explicitly and re-raise or propagate them according to your application contract.

With the default `return_exceptions=False`, `gather()` propagates the first exception it observes to the awaiting task, but other submitted awaitables are not automatically cancelled just because one raised; they may continue running. If the gather operation itself is cancelled, unfinished awaitables are cancelled. This differs from TaskGroup's fail-fast sibling cancellation behavior.

## 8. Classify retryable and fatal failures

Retry classification should be based on exception types and domain policy, not message matching. A timeout or transient connection reset may be retryable; invalid input, permission denial, and schema incompatibility are usually permanent. Some types require context: `OSError` is broad, and not every `OSError` is transient.

```python
class RetryableSourceError(Exception):
    pass

class InvalidRecordError(Exception):
    pass


failures = ExceptionGroup(
    "source batch failed",
    [
        RetryableSourceError("temporary service outage"),
        InvalidRecordError("unsupported schema version"),
    ],
)

retryable, fatal = failures.split(RetryableSourceError)

if retryable is not None:
    schedule_retry(retryable)  # application-defined policy
if fatal is not None:
    raise fatal
```

The example's `schedule_retry` is an application placeholder. In production, retry only the affected idempotent units, use bounded exponential backoff with jitter, enforce an attempt/deadline budget, and emit metrics for each attempt. Do not retry the entire batch if some records have already committed unless the write path is idempotent or has a transaction/compensation strategy.

The `fatal` value is a subgroup, not a single leaf. Re-raising it preserves the remaining grouped structure. If you want to preserve the original group as the cause of a new domain-level error, raise the domain error `from failures`; if you only need to propagate the fatal subset, raise `fatal`.

## 9. Futures and multiple cleanup failures

### 9.1 Collect exceptions from `concurrent.futures`

A future stores its outcome; calling `.result()` re-raises that future's exception. To report multiple failures, inspect all completed futures and group the exceptions deliberately.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def transform(item: int) -> int:
    if item % 2:
        raise ValueError(f"odd item: {item}")
    return item * 10


def transform_all(items: list[int]) -> list[int]:
    results: list[int] = []
    failures: list[Exception] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(transform, item) for item in items]
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as exc:
                failures.append(exc)
    if failures:
        raise ExceptionGroup("one or more transforms failed", failures)
    return results
```

This simple example raises after all submitted futures have been inspected and the executor context has shut down. If results need stable input order, map each future to its original index and store results by index; `as_completed()` yields completion order, not submission order. In production, attach a task ID as an exception note or structured field. Do not catch `BaseException` just to aggregate every possible interruption.

### 9.2 Multiple cleanup failures: do not assume `ExitStack` groups them

`contextlib.ExitStack` and `AsyncExitStack` unwind callbacks/context managers in LIFO order and follow context-manager exception propagation/suppression semantics. **They do not promise to aggregate every failing cleanup callback into an `ExceptionGroup`.** If the application requires all cleanup failures to be retained, explicitly collect them while attempting every cleanup, then raise a group after the cleanup pass. Preserve the primary operation failure separately so a cleanup failure does not silently erase the reason the operation failed.

```python
from collections.abc import Callable, Iterable


def run_cleanups(cleanups: Iterable[Callable[[], None]]) -> None:
    failures: list[Exception] = []
    for cleanup in cleanups:
        try:
            cleanup()
        except Exception as exc:
            failures.append(exc)
    if failures:
        raise ExceptionGroup("one or more cleanup operations failed", failures)
```

This helper intentionally attempts all cleanup callbacks. It is not a replacement for `ExitStack` when resource acquisition and nested context-manager suppression semantics matter; use it when the desired contract is specifically “attempt every cleanup and aggregate ordinary cleanup exceptions.” If a primary exception is already propagating, choose and document a policy: attach cleanup errors as notes, raise a new group that includes the primary and cleanup failures, or preserve the primary and report cleanup failures through a separate logging/monitoring channel. Do not discard either category accidentally.

A minimal pattern that preserves the primary failure and reports cleanup failures as notes is:

```python
primary: BaseException | None = None
try:
    perform_operation()  # application function
except BaseException as exc:
    primary = exc

cleanup_errors: list[Exception] = []
for cleanup in cleanups:
    try:
        cleanup()
    except Exception as exc:
        cleanup_errors.append(exc)

if primary is not None:
    for exc in cleanup_errors:
        primary.add_note(f"cleanup failure: {type(exc).__name__}: {exc}")
    raise primary
if cleanup_errors:
    raise ExceptionGroup("cleanup failures", cleanup_errors)
```

This pattern is illustrative, and production code must consider cancellation and traceback preservation carefully. Catching `BaseException` is shown only to preserve the primary failure while running a controlled cleanup phase; it must not be used to convert process-control exceptions into routine application errors. If asynchronous cleanup can itself be cancelled, design the cancellation policy explicitly rather than assuming this synchronous pattern is sufficient.

## 10. Inspecting and logging grouped failures

### 10.1 Traverse leaves without losing nesting in the original

Use a recursive helper when you need one structured log event per leaf. Keep the original group for the exception traceback and diagnostic context; flatten only for the particular output format that needs a flat representation.

```python
from collections.abc import Iterator


def iter_leaves(exc: BaseException) -> Iterator[BaseException]:
    if isinstance(exc, BaseExceptionGroup):
        for child in exc.exceptions:
            yield from iter_leaves(child)
    else:
        yield exc
```

`BaseExceptionGroup` is the correct base class for a helper intended to traverse both `ExceptionGroup` and base-level groups. If the application only permits ordinary `Exception` leaves, use `ExceptionGroup` in the type contract and avoid swallowing non-`Exception` base exceptions.

### 10.2 Structured logging and tracing

Log grouped failures once at the service or job boundary, with the full grouped traceback and stable correlation identifiers. Avoid logging the same exception in every layer and then re-raising it, which creates duplicate alerts. If a log sink cannot represent exception trees, emit a parent event plus child records containing fields such as `batch_id`, `task_id`, `exception_type`, `message_safe`, `retryable`, and `attempt`; preserve parent-child relationships with a group or trace ID.

```python
import logging

logger = logging.getLogger(__name__)

async def log_pipeline_failure() -> None:
    try:
        await load_pipeline()  # application function
    except* TimeoutError as timeouts:
        logger.warning(
            "pipeline had retryable timeouts",
            extra={"failure_count": sum(1 for _ in iter_leaves(timeouts))},
        )
    except* Exception as others:
        logger.exception(
            "pipeline had non-timeout failures",
            extra={"failure_count": sum(1 for _ in iter_leaves(others))},
        )
```

This snippet is a pattern for an async function; `await` must be inside `async def`. In the second handler, `logger.exception()` is useful when called while handling an exception, but logging policy should be consistent and avoid duplicate stack traces. Do not assume a logging formatter will flatten group leaves into your desired JSON schema; test your formatter and exporter. Sanitize messages and notes before shipping them to centralized logging or tracing systems.

For a traceback string, `traceback.format_exception(group)` supports exception groups on Python 3.11+. It formats nested failures in a human-readable tree. Prefer standard traceback formatting over parsing `str(group)`; exception string representations are not a stable serialization format.

## 11. Choosing a public error contract

Use `ExceptionGroup` when callers genuinely need to inspect and handle heterogeneous independent exceptions by type—for example, a concurrent orchestration boundary or a validation API that intentionally exposes leaf exception types.

Prefer a single domain-specific aggregate exception when callers need a stable domain contract independent of low-level implementation details. For example, `BatchRejected(errors=[...])` could expose a documented list of validation issues without forcing clients to depend on parser internals. The aggregate can itself wrap or chain an exception group internally if appropriate.

Consider:

- **Stability:** exception group leaf types become part of the public API if callers are expected to match them.
- **Compatibility:** a public `except*` requirement forces Python 3.11+ syntax in caller code.
- **Serialization:** exception groups are not a wire protocol. Convert failures to a documented, versioned data structure before sending them over HTTP, queues, or process boundaries.
- **Security:** avoid leaking secrets, internal paths, raw records, or vendor response bodies.
- **Partial success:** return structured per-record outcomes when success and failure are both first-class results, rather than using exceptions for expected validation results on every record.

## 12. Testing exception groups with pytest

Use supported pytest APIs and assert structure or types, not the exact full traceback string. `pytest.raises(ExceptionGroup)` is available in modern pytest versions. `ExceptionInfo.group_contains()` is available in pytest 8+, but it answers whether a matching exception exists; by itself, it does **not** prove that no unexpected exceptions are present. To inspect all members or verify that no extras exist, inspect `excinfo.value` or use `pytest.RaisesGroup` where supported by your installed pytest version.

```python
import pytest


def raise_mixed_group() -> None:
    raise ExceptionGroup(
        "mixed",
        [ValueError("bad row"), TypeError("wrong field type")],
    )


def test_group_contains_expected_errors() -> None:
    with pytest.raises(ExceptionGroup) as excinfo:
        raise_mixed_group()

    group = excinfo.value
    assert group.message == "mixed"
    assert len(group.exceptions) == 2
    assert any(isinstance(exc, ValueError) for exc in group.exceptions)
    assert excinfo.group_contains(TypeError)
```

Test selective handling and unmatched propagation separately:

```python
def test_except_star_handles_only_matching_subset() -> None:
    handled: list[str] = []
    with pytest.raises(ExceptionGroup) as excinfo:
        try:
            raise ExceptionGroup(
                "mixed",
                [ValueError("invalid"), PermissionError("denied")],
            )
        except* ValueError as values:
            handled.extend(type(exc).__name__ for exc in values.exceptions)

    assert handled == ["ValueError"]
    assert len(excinfo.value.exceptions) == 1
    assert isinstance(excinfo.value.exceptions[0], PermissionError)
```

For nested groups, test the expected shape and leaf set. For `TaskGroup`, use events/barriers or controlled coroutines to ensure multiple failures occur before cancellation if you need deterministic assertions. Avoid sleep-based tests that pass only under one scheduler timing. For retry policy, assert that only retryable leaves are scheduled and fatal leaves remain visible.

`pytest.RaisesGroup` is a pytest API in recent releases; check your project's minimum pytest version before using it. If portability across pytest versions matters, use `pytest.raises(ExceptionGroup)` and inspect `excinfo.value` directly.

## 13. Ingestion design: partial success, retries, rollback

A grouped exception reports failures; it does not make writes transactional. Design the ingestion workflow around explicit state transitions:

1. **Validate before side effects where possible.** Accumulate independent schema and row-level failures, then reject or quarantine according to the contract.
2. **Partition work into idempotent units.** Give each record or partition a stable idempotency key so retrying a failed subset does not duplicate already committed writes.
3. **Choose transaction boundaries.** If all-or-nothing semantics are required, validate first and commit atomically, or use a transaction/saga with compensation. A group does not roll back successful operations automatically.
4. **Represent partial outcomes explicitly.** Track accepted, rejected, retried, and permanently failed counts. If partial success is normal, return a result object containing per-item outcomes instead of throwing a group for every expected rejection.
5. **Classify errors.** Split transient infrastructure failures from permanent data/configuration failures. Retry only transient failures with backoff, jitter, a deadline, and a maximum attempt count.
6. **Preserve context.** Attach stable record IDs and task/shard IDs to exceptions, not raw sensitive payloads. Carry correlation IDs into logs, traces, and dead-letter records.
7. **Report once.** Log the grouped traceback at the orchestration boundary, and expose a stable summary/metric to callers and monitoring.

### Example policy sketch

```python
def handle_batch_failure(group: ExceptionGroup) -> None:
    retryable, permanent = group.split(RetryableSourceError)

    if permanent is not None:
        send_to_dead_letter(permanent)  # application-defined

    if retryable is not None:
        enqueue_retry(retryable)  # application-defined, bounded and idempotent
```

This is a policy sketch, not a complete ingestion engine. It intentionally does not claim rollback or exactly-once processing. Those guarantees depend on storage transactions, idempotency, durable checkpoints, and the retry protocol.

## 14. Compatibility before Python 3.11

- Python 3.11 introduced the built-in group classes, `except*`, `BaseException.add_note()`, and the language/runtime machinery for exception groups.
- Python 3.10 and earlier cannot parse `except*`, even if the `exceptiongroup` package is installed. You must use version-specific modules or ordinary exception/aggregate-result patterns in code that must parse on older interpreters.
- The third-party `exceptiongroup` package provides backported group classes and related helpers for older runtimes. It does **not** backport the `except*` syntax; use its `catch()` API where appropriate or maintain a separate compatibility path. Check the package's current documentation and your supported-version matrix.
- If your library supports both old and new runtimes, decide whether the public API exposes groups only on 3.11+, exposes a stable domain aggregate on all supported versions, or returns per-item outcomes. Document the choice.
- Do not scatter version checks through business logic. Isolate compatibility behavior at a small boundary and test each supported interpreter in CI.

## 15. Common mistakes

1. **Using `except ValueError` for a group.** It does not search inside a group; use `except* ValueError` when selective group handling is intended.
2. **Assuming a handler gets one leaf.** An `except*` variable is a matching subgroup; inspect or traverse its `.exceptions`.
3. **Assuming the first handler consumes the original group.** Unmatched exceptions continue and can be raised after the `try` statement.
4. **Mixing `except` and `except*` in one `try`.** Use nested `try` statements to separate the two boundaries.
5. **Using `return`, `break`, or `continue` inside `except*`.** Record a decision and perform control flow after the handler.
6. **Flattening every group immediately.** You can lose task, shard, or nested-batch context.
7. **Catching `BaseException` as ordinary application failure.** This risks swallowing cancellation and process-control signals.
8. **Assuming TaskGroup always reports every task's planned failure.** A sibling may be cancelled before reaching its own failing line.
9. **Assuming `gather(return_exceptions=True)` raises a group.** It returns outcomes in a list; exceptions are values in that result list.
10. **Assuming `ExitStack` automatically aggregates cleanup errors.** Its documented context-manager unwinding semantics are not a guarantee of an `ExceptionGroup` containing every callback failure.
11. **Using `group_contains()` to prove absence of unexpected failures.** It proves presence, not exclusivity.
12. **Using exception messages as a retry protocol.** Use types and structured fields; messages can change and can expose sensitive data.
13. **Assuming a group implies rollback.** It is a failure representation, not a transaction manager.
14. **Logging every leaf and every parent at every layer.** Define one logging boundary and preserve correlation identifiers.

## 16. Exercises with solutions

### Exercise 1 — selective handling

Create a group containing two `ValueError` leaves and one `OSError` leaf. Handle the `ValueError` subset with `except*`; verify that the unmatched `OSError` still propagates.

**Solution:**

```python
try:
    raise ExceptionGroup(
        "exercise",
        [ValueError("a"), OSError("disk"), ValueError("b")],
    )
except* ValueError as values:
    print("handled", len(values.exceptions))
```

The handler prints `handled 2`; the remaining `OSError` is propagated in an exception group.

### Exercise 2 — classify retryable failures

Given `ExceptionGroup("jobs", [TimeoutError(...), ValueError(...)])`, use `.split(TimeoutError)` and show that the timeout subset is retryable while the value error remains fatal.

**Solution:**

```python
retryable, fatal = failures.split(TimeoutError)
if retryable is not None:
    retry(retryable)  # bounded, idempotent retry policy
if fatal is not None:
    raise fatal
```

`retry()` is application-defined; `.split()` only partitions the group and does not perform a retry.

### Exercise 3 — row context

Extend `validate_all()` so each invalid row has a note with a stable row ID and field name. Explain why raw input values should not automatically be placed in notes.

**Solution:** Add a note such as `exc.add_note(f"row_id={row_id}; field=quantity")` before appending the exception. Use bounded identifiers and avoid raw values that may contain secrets or personal data.

### Exercise 4 — concurrent policy

Choose between `TaskGroup` and `gather(return_exceptions=True)` for (a) a set of dependent subtasks that should fail together, and (b) independent source lookups where successful responses should still be returned.

**Solution:** Prefer `TaskGroup` for (a), because failure cancels sibling tasks and the group reports collected failures at context exit. Prefer `gather(return_exceptions=True)` for (b), because it returns each outcome in input order so successes and exceptions can be processed independently.

### Exercise 5 — tests

Write a test that proves a `ValueError` was handled but a `PermissionError` was not swallowed by an `except* ValueError` handler.

**Solution:** Use `pytest.raises(ExceptionGroup)` around the nested `try` statement and inspect `excinfo.value.exceptions` for the remaining `PermissionError`, as shown in Section 12.

## 17. Self-check

Before moving on, verify that you can answer these without looking back:

- What is the difference between `ExceptionGroup` and `BaseExceptionGroup`?
- What object does an `except*` handler receive?
- What happens to unmatched exceptions after all handlers have run?
- How do `.subgroup()` and `.split()` differ?
- Why can multiple `TaskGroup` child failures appear, and why is that not guaranteed for every task that was scheduled to fail?
- How does cancellation differ from an ordinary application exception?
- When is a single domain aggregate exception a better public API than exposing a group?
- Why does grouping failures not provide rollback, idempotency, or exactly-once semantics?

## Further reading

- Python documentation: [Built-in Exceptions — Exception Groups](https://docs.python.org/3/library/exceptions.html#exception-groups)
- Python documentation: [Compound statements — `except*`](https://docs.python.org/3/reference/compound_stmts.html#except-star)
- Python documentation: [Task groups and cancellation](https://docs.python.org/3/library/asyncio-task.html#task-groups)
- Python documentation: [`asyncio.gather()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather)
- Python documentation: [`contextlib.ExitStack`](https://docs.python.org/3/library/contextlib.html#contextlib.ExitStack)
- PEP 654: [Exception Groups and `except*`](https://peps.python.org/pep-0654/)
