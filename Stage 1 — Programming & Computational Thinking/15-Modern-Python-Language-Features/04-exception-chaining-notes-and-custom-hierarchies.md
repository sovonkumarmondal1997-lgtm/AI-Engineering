# Exception Chaining, Notes, and Custom Exception Hierarchies

> **Level:** Beginner → Intermediate → Advanced  
> **Repository policy:** Write new code for Python 3.12+. Version requirements are called out explicitly.  
> **Running example:** a data-ingestion service that loads configuration, reads source records, parses fields, and reports safe operational errors.

## Learning outcomes

By the end, you should be able to read chained tracebacks; distinguish `__cause__`, `__context__`, and `__traceback__`; build a package-level exception hierarchy; add notes without unnecessary wrapping; translate low-level failures at system boundaries; choose retry/logging/API policies; and test exception contracts, including pickling where needed.

## 1. A useful mental model

An exception is both a **control-flow signal** and a **diagnostic object**. Good production design answers three separate questions:

1. **What happened?** Exception type and stable code classify the failure.
2. **Where and why?** Traceback, cause/context, and notes give diagnostic history.
3. **What should the caller do?** The public exception contract distinguishes invalid input, missing resources, transient infrastructure failures, and programming defects.

Do not make one message do all three jobs. Callers should branch on documented exception types or codes, not parse arbitrary message text.

## 2. Beginner: exception-handling fundamentals

### 2.1 `try`, `except`, `else`, and `finally`

- `try`: run code that may fail.
- `except SpecificError`: handle a failure you understand.
- `else`: run only if the `try` suite completed without an exception.
- `finally`: run cleanup regardless of success or failure, except when process termination prevents normal execution.

```python
def read_first_line(path):
    try:
        handle = open(path, encoding="utf-8")
    except OSError:
        # Opening failed; propagate because this function cannot recover.
        raise
    else:
        # This block runs only when open() succeeds.
        try:
            return handle.readline()
        finally:
            handle.close()
```

The `else` suite runs only when the `try` suite completes without an exception. The `finally` suite runs during normal success or exception propagation; if cleanup itself raises, that new exception can replace the one already propagating. A context manager is usually preferable for files because it makes resource ownership clearer:

```python
def read_first_line(path):
    with open(path, encoding="utf-8") as handle:
        return handle.readline()
```

### 2.2 Catch specific exceptions and re-raise correctly

```python
def parse_quantity(raw: str) -> int:
    try:
        quantity = int(raw)
    except ValueError:
        # Bare raise re-raises the active exception with its traceback.
        raise
    if quantity < 0:
        raise ValueError("quantity must be non-negative")
    return quantity
```

If no recovery or extra context is needed, do not catch just to re-raise. Inside an `except` block, `raise` is the normal way to propagate the current exception. `raise err` can add a new raise location and is not the preferred plain re-raise.

Avoid bare `except:`: it catches `BaseException` subclasses such as `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit`. `except Exception:` is narrower but still broad; use it only at an intentional boundary.

### 2.3 Implicit chaining: `__context__`

If an exception is raised while another exception is being handled, Python normally links the new exception to the active one through `__context__`.

```python
try:
    int("not-an-integer")
except ValueError:
    raise RuntimeError("could not convert configuration value")
```

The displayed traceback resembles:

```text
ValueError: invalid literal for int() with base 10: 'not-an-integer'

During handling of the above exception, another exception occurred:

RuntimeError: could not convert configuration value
```

The `ValueError` happened first; code raised `RuntimeError` while handling it. The link is implicit.

### 2.4 Explicit chaining: `__cause__`

At a system boundary, a low-level error may not be the right abstraction for callers. Translate it while preserving the original cause:

```python
class ConfigurationError(Exception):
    """Configuration could not be loaded."""


def load_config_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError as err:
        raise ConfigurationError("configuration file was not found") from err
    except PermissionError as err:
        raise ConfigurationError("configuration file is not readable") from err
```

A traceback includes a separator like:

```text
FileNotFoundError: [Errno 2] No such file or directory: '/private/path/app.toml'

The above exception was the direct cause of the following exception:

ConfigurationError: configuration file was not found
```

`raise NewError(...) from err` sets `__cause__` to `err` and tells traceback formatting to show the explicit cause. It does not erase the original exception. A safe public message need not repeat a sensitive absolute path; trusted internal diagnostics can retain the cause.

### 2.5 Suppressing displayed context: `from None`

```python
def public_config_error():
    try:
        int("secret-like-input")
    except ValueError:
        raise ConfigurationError("configuration contains an invalid value") from None
```

`from None` sets `__suppress_context__` to true, suppressing the implicit context in standard traceback display. The original exception may still be available as `__context__`; this is display suppression, not erasure. Use it when the lower-level context is confusing or unsuitable for a displayed traceback, not as a substitute for safe logging and redaction.

### 2.6 The exception attributes are not interchangeable

| Attribute | Meaning | Typical use |
| --- | --- | --- |
| `exc.__cause__` | Explicit cause from `raise ... from cause`; otherwise normally `None`. | Understand a deliberate translation boundary. |
| `exc.__context__` | Exception being handled when this exception was raised. | Understand implicit nested failure history. |
| `exc.__traceback__` | Linked traceback nodes showing frames and source locations. | Inspect or format the stack. |
| `exc.__suppress_context__` | Whether standard formatting suppresses implicit context. | Understand `from None` and explicit-cause display. |
| `exc.__notes__` | Notes added with `add_note()`. | Diagnostic breadcrumbs. |

A traceback is frame history, not the same thing as causal linkage between exception objects.

### 2.7 Re-raise, annotate, or wrap?

Use the least disruptive action that meets the caller's needs.

```python
try:
    record = parse_record(raw)
except ValueError:
    raise  # same exception; preserve active traceback
```

Add a note when the exception type is already appropriate but context is missing:

```python
try:
    record = parse_record(raw)
except ValueError as err:
    err.add_note("source=batch-17.csv, row=42")
    raise
```

Wrap when callers need a stable domain type or structured data:

```python
try:
    quantity = int(raw)
except ValueError as err:
    raise RecordValidationError(
        "quantity must be an integer",
        field="quantity",
        code="INVALID_INTEGER",
        row_number=42,
    ) from err
```

Do not wrap reflexively: each wrapper adds traceback noise unless it provides useful domain meaning or context.

## 3. Intermediate: design an exception hierarchy

### 3.1 Package-level exception tree

```text
IngestionError(Exception)
├── ConfigurationError
│   └── ConfigurationFormatError
├── SourceReadError
│   ├── SourceNotFoundError
│   └── SourceUnavailableError       # potentially transient
├── RecordValidationError            # usually permanent for this input
└── IngestionStateError              # often a caller/programming contract issue
```

A package base lets callers handle expected library failures as a group; subclasses enable precise policy. The implementations below keep `SourceNotFoundError` and `SourceUnavailableError` under `SourceReadError`, matching the tree. Create a class when callers need a meaningful distinction, not for every possible sentence.

### 3.2 Structured information and `__str__`

```python
class IngestionError(Exception):
    """Base class for documented ingestion failures."""
    code = "INGESTION_ERROR"


class ConfigurationError(IngestionError):
    code = "CONFIGURATION_ERROR"


class RecordValidationError(IngestionError):
    code = "RECORD_VALIDATION_ERROR"

    def __init__(
        self,
        message: str,
        *,
        field: str,
        code: str = "INVALID_FIELD",
        row_number: int | None = None,
        value: str | None = None,
    ) -> None:
        super().__init__(message)
        self.field = field
        self.code = code
        self.row_number = row_number
        # Store only a safe/redacted value, never a raw credential or payload.
        self.value = value
```

```python
error = RecordValidationError(
    "quantity must be a positive integer",
    field="quantity",
    code="INVALID_QUANTITY",
    row_number=42,
)
assert str(error) == "quantity must be a positive integer"
assert error.field == "quantity"
assert error.code == "INVALID_QUANTITY"
assert error.row_number == 42
assert error.value is None

# If the rejected value is safe to retain, pass a bounded/sanitized representation.
safe_error = RecordValidationError(
    "quantity must be positive",
    field="quantity",
    code="NON_POSITIVE_QUANTITY",
    row_number=42,
    value="-3",  # safe normalized value in this example
)
assert safe_error.value == "-3"
```

`Exception.__str__()` normally formats the positional arguments stored in `args`. Calling `super().__init__(message)` keeps `str(error)` useful. Override `__str__` only when there is a clear reason; keep it stable and do not put secrets or raw payloads in it. Consumers should use attributes/codes, not parse the message.

### 3.3 Avoid sensitive values in exception text

Good:

```python
raise RecordValidationError(
    "API token is required",
    field="api_token",
    code="MISSING_TOKEN",
)
```

Bad:

```python
# May leak through logs, tracebacks, notes, crash reporting, and API responses.
raise ConfigurationError(f"invalid API token {raw_token!r}")
```

If diagnosis genuinely requires value context, redact and length-limit it before storing or logging. Prefer safe identifiers such as field name, source ID, row number, and correlation ID.

### 3.4 Translate low-level errors at boundaries

```python
from pathlib import Path


class IngestionError(Exception):
    """Base class for expected ingestion failures."""


class SourceReadError(IngestionError):
    """Configured source could not be read."""


class SourceNotFoundError(SourceReadError):
    """Configured source file does not exist."""


class SourceUnavailableError(SourceReadError):
    """Configured source may become available again."""


def read_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as err:
        raise SourceNotFoundError("configured input source was not found") from err
    except (PermissionError, IsADirectoryError, UnicodeDecodeError) as err:
        raise SourceReadError("configured input source could not be read") from err
```

Catch only failures whose meaning you understand. Do not relabel `MemoryError`, `KeyboardInterrupt`, or arbitrary defects as “source unavailable.” Avoid catching your own domain exception and wrapping it again unless the new layer adds meaningful abstraction.

## 4. Exception notes (Python 3.11+)

`BaseException.add_note(note)` was added in **Python 3.11**. Standard traceback formatting displays notes after the exception message. Notes add breadcrumbs while preserving the exception type and object.

```python
def parse_row(raw: str, *, source_name: str, row_number: int) -> dict[str, str]:
    try:
        parts = raw.split(",")
        if len(parts) != 3:
            raise ValueError("expected exactly three columns")
        return {"account": parts[0], "quantity": parts[1], "region": parts[2]}
    except ValueError as err:
        err.add_note(f"source={source_name!r}, row={row_number}")
        raise
```

Example display:

```text
ValueError: expected exactly three columns
source='batch-17.csv', row=42
```

Notes are diagnostic, not a structured API. Use them for safe context (source identifier, row number, operation, correlation ID); use stable types and attributes for machine-readable decisions. `add_note()` requires a string; non-strings raise `TypeError`. Python before 3.11 lacks this method. If supporting older versions, use an explicit compatibility helper or another documented strategy rather than pretending a manually assigned `__notes__` attribute will be formatted by the interpreter.

```python
def add_diagnostic_note(exc: BaseException, note: str) -> None:
    """Attach a note only on Python versions that support it."""
    add_note = getattr(exc, "add_note", None)
    if add_note is not None:
        add_note(note)
```

Do not put secrets in notes: notes often appear in logs and crash reports.

## 5. Traceback inspection and logging

### 5.1 Formatting and inspecting `__traceback__`

```python
import traceback


def format_error(exc: BaseException) -> str:
    return "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )


def traceback_locations(exc: BaseException) -> list[tuple[str, int, str]]:
    return [
        (frame.filename, frame.lineno, frame.name)
        for frame in traceback.extract_tb(exc.__traceback__)
    ]
```

The three-argument `traceback.format_exception(type, value, tb)` form is explicit and familiar; modern Python also supports `traceback.format_exception(exc)`. Tracebacks can expose paths, source lines, and implementation details. Never return a raw traceback to an untrusted client.

`exc.with_traceback(tb)` sets the exception’s traceback and returns the same exception object. It is an advanced tool, not the normal way to re-raise. Use bare `raise` inside an active handler when propagating unchanged.

### 5.2 `logging.exception()` and log once

```python
import logging

logger = logging.getLogger(__name__)


def run_batch() -> None:
    try:
        ingest_batch()
    except IngestionError:
        logger.exception("batch ingestion failed", extra={"batch_id": "batch-17"})
        raise
```

This is appropriate only if this layer owns the logging decision. If an API handler, task supervisor, or CLI entry point will log the failure, lower layers should usually raise without logging too. **Log once at the boundary that can make the operational decision.** Lower layers can add notes or chain domain errors; the boundary logs with safe structured fields and a correlation ID. Do not log tokens, passwords, raw payloads, or unredacted personal data.

## 6. Context managers and intentional suppression

### 6.1 Prefer context managers for cleanup

```python
from pathlib import Path


def load_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as handle:
        return handle.read()
```

A context manager’s `__exit__` can suppress an exception if it returns a truthy value. Ordinary file objects do not suppress read errors. Custom managers should suppress only when that is their explicit contract.

### 6.2 `contextlib.suppress()` for narrow, expected absence

```python
from contextlib import suppress
from pathlib import Path


def remove_stale_marker(path: Path) -> None:
    with suppress(FileNotFoundError):
        path.unlink()
```

The missing marker is explicitly harmless. Do not use `suppress(Exception)` around parsing, ingestion, or persistence: it can hide defects and silently discard records. Suppress only a narrow exception for a documented reason.

A `finally` block runs during normal propagation, but an exception raised inside `finally` can replace the exception already propagating. Prefer context managers for resources. If cleanup can fail, define whether that failure is primary, secondary, logged, or attached as a note.

## 7. Advanced: production error taxonomy and policy

### 7.1 Programmer, operational, validation, and configuration errors

| Category | Examples | Typical policy |
| --- | --- | --- |
| Programmer/contract defect | Internal `TypeError`, `AssertionError`, invalid lifecycle use | Fix the bug; do not retry blindly or mislabel as client input. |
| Operational failure | Source unavailable, timeout, temporary database outage | Retry only if classified transient and operation is safe; use bounded backoff. |
| Validation failure | Missing field, malformed quantity, unsupported record shape | Report stable validation error; identical input usually remains invalid. |
| Configuration failure | Missing required setting, invalid config format | Fail fast and correct configuration; no retry without a state change. |

These categories do not map perfectly to built-in types. A `ValueError` may mean invalid external data or a programming defect depending on where it originates. Translate where the meaning is known.

### 7.2 Retryable versus permanent

Do not retry based on message substrings. Use exception types, structured codes, and operation semantics. A robust retry policy:

1. Retries only classified transient failures.
2. Has a finite attempt/time budget.
3. Uses exponential backoff with jitter.
4. Respects cancellation and shutdown.
5. Avoids repeating non-idempotent side effects unless protected by idempotency keys or transactions.
6. Records the final outcome once at the task boundary.

Validation failures and missing configuration are usually permanent for the same input. A timeout may be transient, but a timed-out write could already have committed; blindly retrying can duplicate side effects.

### 7.3 Map errors to API responses without leaking internals

```python
def api_error_response(exc: IngestionError) -> tuple[int, dict[str, str]]:
    if isinstance(exc, RecordValidationError):
        return 422, {"code": exc.code, "message": str(exc)}
    if isinstance(exc, SourceNotFoundError):
        # Internal configured source: not necessarily a client-facing 404.
        return 503, {
            "code": "SOURCE_NOT_AVAILABLE",
            "message": "The ingestion source is currently unavailable.",
        }
    return 500, {
        "code": "INGESTION_FAILED",
        "message": "The ingestion request could not be completed.",
    }
```

This is an example policy, not a universal status mapping. `404` fits only when the missing resource is part of the client-facing resource model. An internal file missing from deployment may be a configuration/operational failure. Do not expose `repr(exc)`, tracebacks, filesystem paths, SQL, connection strings, tokens, or untrusted payload fragments in response bodies.

### 7.4 Map failures to process exit codes

```python
import logging
import sys

logger = logging.getLogger(__name__)


def main() -> int:
    try:
        run_ingestion()
    except RecordValidationError as err:
        logger.error("input validation failed: %s", err)
        return 2
    except IngestionError:
        logger.exception("ingestion failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Document CLI exit codes. Do not catch `BaseException` just to force a code; interrupt and termination semantics matter.

### 7.5 Exceptions are part of the public API

Document expected exception types, operations that raise them, retryability, stable attributes/codes, chaining behavior, and whether messages are end-user or operator oriented.

```python
def load_settings(path: str) -> dict[str, str]:
    """Load required ingestion settings.

    Raises:
        ConfigurationError: Settings cannot be loaded or parsed.
    """
    ...
```

Choose a consistent boundary: translate low-level errors into documented domain exceptions, or explicitly document selected built-ins that propagate. Avoid surprising, release-to-release changes in exception behavior.

### 7.6 Exceptions and hot-loop performance

Python 3.11 improved the normal path through many `try` constructs (often described as “zero-cost exceptions”), but raising and handling an exception is still expensive compared with ordinary branching. Avoid using exceptions for routine control flow in hot loops when a direct condition expresses the expected case:

```python
for raw in records:
    if raw == "":
        continue
    process(raw)
```

Do not add pre-checks that introduce race conditions—for example, checking that a file exists and then opening it instead of opening and handling `FileNotFoundError`. Benchmark representative workloads before making performance claims.

## 8. Pickling and multiprocessing-safe exceptions

Exceptions can cross process boundaries in multiprocessing or job frameworks. Default exception pickling commonly reconstructs an exception from `.args`; a custom constructor that requires keyword-only attributes may not be reconstructible.

```python
class PickleSafeValidationError(IngestionError):
    def __init__(
        self,
        message: str,
        field: str,
        code: str = "INVALID_FIELD",
        row_number: int | None = None,
    ) -> None:
        super().__init__(message)
        self.field = field
        self.code = code
        self.row_number = row_number

    def __reduce__(self):
        return (
            type(self),
            (str(self), self.field, self.code, self.row_number),
        )
```

This example explicitly reconstructs the exception from positional arguments. Test the actual process path and all promised attributes. Do not serialize sensitive payloads into exception state. **Never unpickle untrusted data**; pickle can execute arbitrary code during loading. Multiprocessing behavior can vary by platform and start method.

```python
import pickle

original = PickleSafeValidationError(
    "quantity must be positive", "quantity", "INVALID_QUANTITY", 42
)
restored = pickle.loads(pickle.dumps(original))
assert type(restored) is PickleSafeValidationError
assert str(restored) == str(original)
assert restored.field == original.field
assert restored.code == original.code
assert restored.row_number == original.row_number
```

## 9. Top-level exception hooks and asyncio

### 9.1 `sys.excepthook` and `threading.excepthook`

`sys.excepthook` handles uncaught exceptions in the main thread (with special handling for `SystemExit`). `threading.excepthook` handles uncaught exceptions from `threading.Thread` targets. These are process/application crash-reporting hooks, not substitutes for local recovery.

```python
import sys
import traceback


def top_level_hook(exc_type, exc_value, exc_tb) -> None:
    # Keep the hook minimal and robust so it does not recursively fail.
    traceback.print_exception(exc_type, exc_value, exc_tb)


# Install only at an application entry point, if needed:
# sys.excepthook = top_level_hook
```

A custom thread hook can log an uncaught worker exception. Install it only at the application boundary:

```python
import logging
import threading

logger = logging.getLogger(__name__)


def thread_exception_hook(args: threading.ExceptHookArgs) -> None:
    logger.error(
        "uncaught exception in thread %s",
        args.thread.name if args.thread is not None else "unknown",
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
    )


# threading.excepthook = thread_exception_hook
```

Preserve appropriate default behavior where needed and avoid leaking secrets in crash reports. A hook should be minimal and robust: if the hook itself raises, diagnostics can be lost or recursion can occur.

### 9.2 `asyncio` exception handler

An event-loop handler receives a context dictionary for errors the loop reports. It is not a universal substitute for awaiting tasks and handling their exceptions.

```python
import asyncio
import logging

logger = logging.getLogger(__name__)


def loop_exception_handler(
    loop: asyncio.AbstractEventLoop,
    context: dict[str, object],
) -> None:
    message = str(context.get("message", "unhandled asyncio error"))
    exc = context.get("exception")
    if isinstance(exc, BaseException):
        logger.error(message, exc_info=(type(exc), exc, exc.__traceback__))
    else:
        logger.error("%s", message)


async def main() -> None:
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(loop_exception_handler)
    # Still await tasks and handle expected failures explicitly.
```

Use this for application-level observability. Prefer explicit task ownership, `await`, cancellation handling, and structured concurrency. Python 3.11 introduced `ExceptionGroup` and `except*` for multiple concurrent failures; that is the next lesson.

## 10. Production-oriented ingestion example

The following example combines hierarchy, safe messages, translation, notes, and validation. It targets Python 3.12+.

```python
from pathlib import Path


class IngestionError(Exception):
    """Base exception for expected ingestion failures."""


class ConfigurationError(IngestionError):
    """Required configuration cannot be loaded."""


class SourceReadError(IngestionError):
    """Configured source could not be read."""


class SourceNotFoundError(SourceReadError):
    """Configured source does not exist."""


class SourceUnavailableError(SourceReadError):
    """Configured source may become available again."""


class RecordValidationError(IngestionError):
    """A record violates the ingestion schema."""

    def __init__(
        self,
        message: str,
        *,
        field: str,
        code: str,
        row_number: int,
        value: str | None = None,
    ) -> None:
        super().__init__(message)
        self.field = field
        self.code = code
        self.row_number = row_number
        self.value = value  # safe/redacted value only; never a raw secret


def load_settings(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as err:
        raise ConfigurationError("required configuration is missing") from err
    except (PermissionError, IsADirectoryError, UnicodeDecodeError) as err:
        raise ConfigurationError("configuration could not be read") from err


def read_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as err:
        raise SourceNotFoundError("configured ingestion source was not found") from err
    except (PermissionError, IsADirectoryError, UnicodeDecodeError) as err:
        raise SourceReadError("configured ingestion source could not be read") from err


def parse_quantity(raw: str, *, row_number: int) -> int:
    try:
        quantity = int(raw)
    except ValueError as err:
        err.add_note(f"row={row_number}, field='quantity'")
        raise RecordValidationError(
            "quantity must be an integer",
            field="quantity",
            code="INVALID_QUANTITY",
            row_number=row_number,
            # Only retain a value if policy says it is safe; do not store raw input here.
        ) from err

    if quantity <= 0:
        raise RecordValidationError(
            "quantity must be positive",
            field="quantity",
            code="NON_POSITIVE_QUANTITY",
            row_number=row_number,
        )
    return quantity
```

Design notes:

- Public messages avoid absolute paths and raw input values.
- `ValueError` is retained as `__cause__` when conversion is translated.
- The note adds a safe row/field breadcrumb to the low-level exception.
- Stable attributes support caller decisions; the message remains human-readable.
- The optional `value` attribute is deliberately omitted from this error because raw input may be sensitive. Supply only a sanitized value when there is a documented diagnostic need.
- The function does not log; the task/API boundary owns logging and response policy.
- This is an exception-policy example, not a complete CSV parser. Real ingestion should use a real parser and validate quoting, columns, encoding, and schema.

A single logging boundary might look like this. `path.name` is shown as a simple example identifier; in systems where filenames are sensitive, use a controlled source ID instead:

```python
import logging

logger = logging.getLogger(__name__)


def process_input(path: Path) -> int:
    try:
        text = read_source(path)
        processed = 0
        for row_number, row in enumerate(text.splitlines(), start=1):
            if not row:
                continue
            parse_quantity(row, row_number=row_number)
            processed += 1
        return processed
    except IngestionError:
        logger.exception("ingestion failed", extra={"source_id": path.name})
        raise
```

In a real application, choose this function or a higher supervisor as the owner of the traceback log; do not log and re-raise at every layer.

## 11. Tests: assert the contract

These examples use `pytest`. To run the suite, place the relevant class definitions from Sections 3, 8, and 10 in an importable module (for example, `ingestion_errors.py`) and import `ConfigurationError`, `RecordValidationError`, and `PickleSafeValidationError`. The note test requires Python 3.11+ and imports `traceback`. The optional `value` attribute must contain only a bounded, sanitized representation; omit it for secrets or sensitive payloads.

```python
import pickle
import traceback
import pytest


def test_explicit_cause_is_preserved():
    try:
        try:
            int("bad")
        except ValueError as err:
            raise ConfigurationError("invalid configuration value") from err
    except ConfigurationError as outer:
        assert isinstance(outer.__cause__, ValueError)
        assert outer.__context__ is outer.__cause__
        assert outer.__suppress_context__ is True
        assert str(outer) == "invalid configuration value"
    else:
        pytest.fail("ConfigurationError was not raised")


def test_implicit_context_is_preserved():
    try:
        try:
            int("bad")
        except ValueError:
            raise RuntimeError("conversion failed")
    except RuntimeError as outer:
        assert isinstance(outer.__context__, ValueError)
        assert outer.__cause__ is None
        assert outer.__suppress_context__ is False
    else:
        pytest.fail("RuntimeError was not raised")


def test_from_none_suppresses_displayed_context():
    try:
        try:
            int("bad")
        except ValueError:
            raise ConfigurationError("invalid value") from None
    except ConfigurationError as outer:
        assert isinstance(outer.__context__, ValueError)
        assert outer.__cause__ is None
        assert outer.__suppress_context__ is True


def test_validation_error_has_structured_fields():
    err = RecordValidationError(
        "quantity must be positive", field="quantity",
        code="NON_POSITIVE_QUANTITY", row_number=7, value="-1",
    )
    assert str(err) == "quantity must be positive"
    assert err.field == "quantity"
    assert err.code == "NON_POSITIVE_QUANTITY"
    assert err.row_number == 7
    assert err.value == "-1"


def test_message_matches_documented_contract():
    with pytest.raises(ConfigurationError, match="invalid configuration value"):
        try:
            int("bad")
        except ValueError as err:
            raise ConfigurationError("invalid configuration value") from err


def test_add_note_is_visible_in_formatted_traceback():
    try:
        try:
            raise ValueError("bad row")
        except ValueError as err:
            err.add_note("source='safe.csv', row=3")
            raise
    except ValueError as err:
        formatted = "".join(
            traceback.format_exception(type(err), err, err.__traceback__)
        )
        assert "source='safe.csv', row=3" in formatted
        assert err.__notes__ == ["source='safe.csv', row=3"]


def test_pickle_safe_exception_round_trip():
    original = PickleSafeValidationError(
        "bad quantity", "quantity", "INVALID_QUANTITY", 3
    )
    restored = pickle.loads(pickle.dumps(original))
    assert type(restored) is PickleSafeValidationError
    assert str(restored) == str(original)
    assert restored.field == "quantity"
    assert restored.code == "INVALID_QUANTITY"
    assert restored.row_number == 3
```

The first three tests intentionally nest `try` blocks so the first exception remains active when the next is raised. A test that only checks `pytest.raises(Exception)` is weak; assert the documented type and contract properties.

### Testing checklist

- [ ] Exact expected type or intentional subclass.
- [ ] Safe, stable message or error code.
- [ ] `__cause__` when explicit chaining is promised.
- [ ] `__context__` only when implicit chaining is relevant.
- [ ] Notes include the safe breadcrumb (Python 3.11+).
- [ ] Formatted tracebacks do not leak secrets.
- [ ] Pickle round-trip preserves promised attributes if needed.
- [ ] Retry classification and API/CLI mapping are tested at the boundary.

## 12. Common mistakes and corrections

| Mistake | Risk | Better approach |
| --- | --- | --- |
| `except:` | Catches interrupts and termination signals. | Catch a specific `Exception` subclass. |
| `except Exception: pass` | Hides defects and silently drops records. | Recover explicitly or propagate. |
| Raise a domain error in a handler without `from` | Implicit context remains but the translation is less explicit. | Use `raise DomainError(...) from err` when the cause is direct. |
| Wrap every exception | Noisy traceback and loss of useful public type. | Re-raise, annotate, or wrap only when it adds value. |
| `raise err` for plain re-raise | Can add traceback location. | Use bare `raise` in the handler. |
| Put secrets in messages/notes | Leaks through logs, tracebacks, and responses. | Use safe messages and redacted identifiers. |
| Log at every layer | Duplicate tracebacks and alerts. | Log once at the operational boundary. |
| Retry all exceptions | Retries bugs/permanent failures and can duplicate side effects. | Classify transient failures and enforce a budget. |
| Assume custom exceptions pickle automatically | Constructor may not reconstruct from `.args`. | Define and test a serialization contract. |
| `suppress(Exception)` | Hides unrelated failures. | Suppress only narrow, harmless failures. |
| Return raw traceback in API | Leaks internal details. | Return stable code and safe message. |

## 13. Exercises

Try these before reading the solutions.

### Exercise 1 — Read the chain

Given:

```python
try:
    int("north")
except ValueError as err:
    raise ConfigurationError("region must be configured") from err
```

What are `__cause__`, `__context__`, and `__suppress_context__` on the raised exception?

### Exercise 2 — Choose a strategy

A parser raises `ValueError` for a malformed row. The public API promises `RecordValidationError` with `field`, `code`, and `row_number`. Should you re-raise, add a note, or wrap? Why?

### Exercise 3 — Remove secret leakage

Rewrite `raise ConfigurationError(f"invalid credential: {token!r}")`. What safe context might you retain?

### Exercise 4 — Retry policy

Classify: (a) invalid integer `RecordValidationError`; (b) temporary network timeout; (c) database write timeout after possible commit; (d) internal `TypeError` from a wrong argument.

### Exercise 5 — Fix suppression

Why is this unsafe, and how should it be rewritten?

```python
try:
    ingest_row(row)
except Exception:
    pass
```

### Exercise 6 — Pickle safety

Why might an exception with `__init__(message, *, field)` fail during unpickling? Name one remedy.

### Exercise 7 — Logging boundary

A storage function logs and re-raises; the job runner also logs and alerts. What should change, and which layer usually logs?

### Exercise 8 — Traceback display

Compare `raise PublicError(...) from err` with `raise PublicError(...) from None`. Does `from None` erase `__context__`?

## 14. Exercise solutions

### Solution 1

`__cause__` is the original `ValueError`; `__context__` is also normally that active `ValueError`; `__suppress_context__` is true because an explicit cause was supplied. The standard traceback uses the “direct cause” separator.

### Solution 2

Wrap as `RecordValidationError` because the public contract requires the domain type and structured attributes. Use `raise RecordValidationError(...) from err` to retain the parsing failure as `__cause__`. A note alone leaves the public exception as `ValueError`.

### Solution 3

For example, `raise ConfigurationError("credential configuration is invalid")`. Retain a safe configuration key, source identifier, or correlation ID, not the token itself.

### Solution 4

(a) Usually permanent for the same record. (b) Potentially retryable with a finite budget and safe operation semantics. (c) Depends on idempotency and commit certainty; blind retry may duplicate side effects. (d) Programmer defect; fix it rather than retry.

### Solution 5

It silently discards ordinary exceptions, including bugs and failures that should stop a batch. Catch a specific recoverable error and record a safe rejection, or propagate:

```python
try:
    ingest_row(row)
except RecordValidationError as err:
    reject_row(row_number=42, code=err.code)
```

The rejection handler must itself be reliable and avoid persisting sensitive raw rows unnecessarily.

### Solution 6

Default exception pickling commonly reconstructs from `.args`. If `.args` contains only the message, unpickling may call the constructor without required `field`. Use a reconstructible positional constructor or implement/test `__reduce__` or another explicit state contract.

### Solution 7

The storage layer should generally add context or chain a domain error and re-raise without logging. The job runner knows task-level metadata and can make retry/alert decisions, so it usually logs once. Log separately in storage only for a distinct independently actionable event.

### Solution 8

`from err` sets explicit `__cause__` and displays the original as the direct cause. `from None` suppresses normal display of implicit context. It does not erase `__context__`; the context can still be inspected programmatically.

## 15. Self-check

1. What does `__cause__` represent, and how is it set?
2. What does `__context__` represent when a new exception is raised during handling?
3. Why is `__traceback__` not the same as a cause?
4. When is `raise ... from None` justified?
5. When is an exception note preferable to a wrapper?
6. Why use stable error codes/attributes instead of parsing messages?
7. Which failures should generally not be retried?
8. Why is logging and re-raising at every layer a poor default?
9. What should an API return instead of a traceback?
10. What should be tested if exceptions cross a multiprocessing boundary?

## Key takeaways

- Catch specific exceptions and make handling policy explicit.
- Use `raise` to propagate unchanged, `raise NewError(...) from err` to translate with explicit cause, and `from None` only when suppressing traceback display is intentional.
- `__cause__` is explicit causality; `__context__` is implicit handling context; `__traceback__` is frame history.
- Use `add_note()` (Python 3.11+) for safe breadcrumbs without changing the exception type.
- Keep exception hierarchies small and stable; expose structured attributes and safe messages.
- Retry only classified transient failures; log once at the operational boundary; do not leak secrets through messages, notes, logs, or API responses.
- If exceptions cross process boundaries, test their serialization/reconstruction contract.
