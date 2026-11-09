# 08 — Logging versus print()
## Complete Lesson Summary, Stage 1 Roadmap Review, Exercises, Debugging, and Mini-Project

**Roadmap:** Stage 1 — Programming & Computational Thinking  
**Module:** 05 — Text Files, Structured Data, and CLI Programs  
**Lesson:** 08 — Logging versus print()

---

# Part A — Complete lesson summary

## 1. `print()` fundamentals

`print()` writes text to a stream. By default, that stream is `sys.stdout`. It converts supplied objects to strings, separates multiple objects, appends a newline, and returns `None`.

```python
print("Hello")
print("count:", 5, True)             # count: 5 True
print("a", "b", "c", sep=", ")       # a, b, c
print("loading", end="...")
print("done")                         # loading...done
```

Its full signature is:

```python
print(*objects, sep=" ", end="\n", file=sys.stdout, flush=False)
```

- `*objects`: values to convert with `str()` and write.
- `sep`: text between values; default is one space.
- `end`: text after the values; default is newline.
- `file`: destination stream; defaults to stdout. It can be `sys.stderr` or another writable file-like object.
- `flush`: request immediate flushing instead of leaving output buffered.

```python
print([1, 2, 3])                      # [1, 2, 3]
print({"a": 1})                       # {'a': 1}

name = "Alice"
count = 3
print(f"{name} processed {count} records")
```

`print()` is appropriate for actual user-facing CLI results, small one-off scripts, learning/experimentation, temporary debugging, and simple interactive progress messages that will not contaminate machine-readable stdout.

It is not inherently bad. The mistake is using it as the only long-term diagnostic system for an application.

## 2. Why `print()` is not application logging

`print()` has no built-in:
1. **Severity levels:** every call is just text; `"ERROR:"` is only a string.
2. **Filtering:** there is no standard way to enable warnings but suppress routine detail.
3. **Metadata:** timestamps, module, line number, process/thread IDs must be added manually at every call.
4. **Routing:** changing destinations requires editing calls or building custom logic.
5. **Central configuration:** verbosity and destinations cannot be adjusted centrally.
6. **Production management:** diagnostics are difficult to enable/disable in running systems without code changes.
7. **Aggregation/search:** ad hoc text is harder for centralized systems to filter and query.
8. **Automation:** monitoring cannot reliably react to a true severity level if severity exists only in message text.
9. **Output separation:** result text and diagnostic text can become mixed on stdout.
10. **Operational durability:** output not captured or routed to durable storage may be lost after a production incident.

Bad example:

```python
def process_file(path):
    print(f"Processing {path}")
    try:
        data = load(path)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return
    print(f"Done: {len(data)} records")
```

It cannot filter progress, add consistent metadata, route errors, or preserve a traceback.

Improved example:

```python
import logging

logger = logging.getLogger(__name__)

def process_file(path):
    logger.info("Processing %s", path)
    try:
        data = load(path)
    except Exception:
        logger.exception("Failed to process %s", path)
        return
    logger.info("Done: %d records", len(data))
```

This introduces named loggers, severity, lazy message formatting, and traceback-aware exception logging.

## 3. Logging architecture

Python's standard-library `logging` module provides a configurable diagnostic system without third-party dependencies.

```text
Application code → Logger → LogRecord → Handler → Formatter → Destination
                                      ↑
                                    Filter
```

- **Logger:** object called by application code, e.g. `logger.info(...)`. Its level decides whether to create a record.
- **LogRecord:** structured event object with message, level, timestamp, logger name, module, line number, and other metadata.
- **Handler:** decides destination: console, file, rotating file, or multiple destinations.
- **Formatter:** decides how a record is rendered as text (which fields and order).
- **Filter:** optional custom gate that can accept/reject or modify records.
- **Root logger:** top-level logger in the hierarchy.
- **Named logger:** logger obtained with `logging.getLogger("name")`.

Import:

```python
import logging
```

The two ways to log:

```python
# Module-level convenience functions: use the root logger
logging.debug("debug")
logging.info("info")
logging.warning("warning")
logging.error("error")
logging.critical("critical")
logging.exception("exception")  # only inside an except block
```

```python
# Preferred in real modules
logger = logging.getLogger(__name__)

logger.debug("debug")
logger.info("info")
logger.warning("warning")
logger.error("error")
logger.critical("critical")
logger.exception("exception")
logger.log(logging.INFO, "explicit level: %s", "info")
```

`logger.log(level, ...)` is the general form; use it when the level is selected dynamically. Otherwise use the named convenience methods.

## 4. Five standard logging levels

| Level | Number | Intended meaning | Example |
|---|---:|---|---|
| `DEBUG` | 10 | Fine-grained diagnostic detail | Parsed row 42 |
| `INFO` | 20 | Normal operational progress | Loaded 1,200 records |
| `WARNING` | 30 | Unexpected but recoverable issue | Skipping row with missing ID |
| `ERROR` | 40 | An operation failed | Could not write output |
| `CRITICAL` | 50 | Severe failure threatening continued operation | Service unavailable; shutdown |

Two independent thresholds matter:
- **Logger level:** determines whether a record is created/passed onward.
- **Handler level:** determines whether a particular destination emits that record.

```python
logger.setLevel(logging.DEBUG)
console_handler.setLevel(logging.WARNING)
```

The logger can pass DEBUG records while the console handler emits only WARNING and above. A separate file handler could accept DEBUG.

Production normally uses INFO or WARNING. DEBUG is detailed and high-volume; enable it deliberately during investigation.

## 5. `logging.exception()` and traceback handling

`logger.exception(message)` logs at ERROR and automatically attaches the current exception traceback. It is intended for use inside an `except` block.

```python
try:
    result = risky_operation()
except Exception:
    logger.exception("Operation failed")
```

Equivalent in effect to:

```python
logger.error("Operation failed", exc_info=True)
```

Difference:

```python
logger.error("Operation failed")       # message only
logger.exception("Operation failed")  # message plus current traceback
```

Do not call `logger.exception()` when no exception is being handled. It may produce `NoneType: None`. For a validation condition that did not raise an exception, use `logger.error()` or `logger.warning()`.

## 6. Logger hierarchy and propagation

Logger names form a dotted hierarchy:

```python
logging.getLogger()          # root
logging.getLogger("app")     # child of root
logging.getLogger("app.io")  # child of app
```

Use this in each module:

```python
logger = logging.getLogger(__name__)
```

`__name__` matches the module's dotted import path, so the logger naturally fits the package hierarchy.

By default, records propagate from a child logger to ancestor handlers, up to root. The originating logger's level is checked first. During propagation, ancestor logger levels are not re-checked, but each receiving handler's level and filters are applied.

```python
parent = logging.getLogger("app")
parent.setLevel(logging.ERROR)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
parent.addHandler(handler)

child = logging.getLogger("app.io")
child.setLevel(logging.DEBUG)

child.debug("dropped by handler: DEBUG is below INFO")
child.info("emitted: handler accepts INFO")
```

The parent logger's ERROR level does not reject the propagated child INFO record; its handler's INFO level controls emission. `propagate=False` stops upward propagation and is a special-case setting, not the default solution.

## 7. Handlers

A handler controls where records go.

```python
import logging
import sys

console = logging.StreamHandler(sys.stderr)  # stderr is default
console.setLevel(logging.WARNING)

file_handler = logging.FileHandler("app.log", encoding="utf-8")
```

- `StreamHandler`: writes to a stream, normally stderr.
- `FileHandler`: writes to a file; appends by default.
- `RotatingFileHandler`: rotates when file size reaches `maxBytes`.
- `TimedRotatingFileHandler`: rotates on a time schedule.

```python
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

size_handler = RotatingFileHandler(
    "app.log", maxBytes=10_000_000, backupCount=5, encoding="utf-8"
)
daily_handler = TimedRotatingFileHandler(
    "app.log", when="midnight", backupCount=14, encoding="utf-8"
)
```

A logger can have multiple handlers. For example, console accepts WARNING and above while a file accepts DEBUG and above. Each handler can have its own level and formatter.

## 8. Formatters and metadata

A formatter turns a LogRecord into its final text:

```python
formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
handler.setFormatter(formatter)
```

Example:

```text
2026-09-22 14:03:11,502 INFO app.io: Processing data.csv
```

Useful fields:
- `%(asctime)s`: timestamp.
- `%(levelname)s`: severity name.
- `%(name)s`: logger name.
- `%(message)s`: final message.
- `%(filename)s`: source filename.
- `%(module)s`: module name.
- `%(funcName)s`: calling function.
- `%(lineno)d`: source line number.
- `%(process)d`: process ID.
- `%(thread)d`: thread ID.

Metadata makes a production event traceable to when, where, and which process/thread emitted it without manually adding those values to every message.

## 9. Filters

A Filter performs custom record filtering or modification beyond severity levels.

```python
class OnlyIOModuleFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith("app.io")

handler.addFilter(OnlyIOModuleFilter())
```

Return `True` to pass the record and `False` to reject it. Filters can also modify records, for example to redact sensitive values or route records based on custom attributes. Use them only when ordinary level thresholds are insufficient.

## 10. Configuration: `basicConfig()` and `dictConfig()`

For a simple script:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    filename=None,
    encoding="utf-8",
)
```

- `level`: root logger threshold.
- `format`: formatter template.
- `filename`: if supplied, log to a file; otherwise console (stderr).
- `encoding`: file encoding, meaningful with filename.

**Common trap:** `basicConfig()` does nothing if the root logger already has a handler. A module-level logging call can implicitly configure the root logger first:

```python
logging.warning("this triggers implicit root configuration")
logging.basicConfig(level=logging.DEBUG)  # too late; does nothing
logging.debug("not displayed")
```

Call `basicConfig()` early, before any logging calls, ideally at the application entry point.

For more complex configuration, use `dictConfig()`:

```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "WARNING",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": "app.log",
            "maxBytes": 10_000_000,
            "backupCount": 5,
            "encoding": "utf-8",
            "level": "DEBUG",
        },
    },
    "root": {"level": "DEBUG", "handlers": ["console", "file"]},
}
logging.config.dictConfig(LOGGING_CONFIG)
```

`dictConfig()` expresses formatters, handlers, and levels as data. It is useful when there are multiple handlers or environment-specific configurations. `fileConfig()` is an older INI-based alternative; `dictConfig()` is generally more flexible.

## 11. stdout, stderr, and CLI design

- `print()` writes to stdout by default.
- `logging.StreamHandler()` writes to stderr by default.

This follows the previous lesson's contract: stdout is the actual result; stderr is diagnostic output.

```bash
python app.py > output.txt
```

The print result goes into `output.txt`; default console log messages remain on stderr, usually the terminal. This keeps JSON/CSV stdout valid for a pipeline.

Use:
- `print()`/stdout for requested results, reports, JSON, CSV.
- logging/stderr for DEBUG, INFO progress, WARNING, ERROR, CRITICAL, and tracebacks.

```python
logger = logging.getLogger(__name__)

def main() -> int:
    logger.info("Starting processing")
    result = process_all_records()
    print(result.summary_json())
    logger.info("Finished: %d records", result.count)
    return 0
```

## 12. Exceptions, errors, and duplicate logging

Choose levels based on what happened:
- Invalid but skippable record: usually WARNING.
- Expected failure that prevents an operation: ERROR.
- Unexpected exception: log traceback with `logger.exception()` at the decision boundary, then re-raise or fail deliberately.

**Log where you have context; decide what to do where you know the right response.** Avoid logging the same exception at every layer.

Bad:

```python
def load_row(row):
    try:
        return parse(row)
    except ValueError:
        logger.exception("Failed to parse row")
        raise

def process_file(path):
    for row in read_rows(path):
        try:
            load_row(row)
        except ValueError:
            logger.exception("Failed to parse row")
```

The same failure is logged twice. Better:

```python
def load_row(row):
    return parse(row)

def process_file(path):
    skipped = 0
    for row in read_rows(path):
        try:
            load_row(row)
        except ValueError:
            logger.warning("Skipping invalid row: %r", row)
            skipped += 1
    return skipped
```

Never silently swallow failures:

```python
try:
    risky_operation()
except Exception:
    logger.exception("risky_operation failed")
    raise
```

If a failure is safely recoverable, log a concise warning and continue intentionally.

## 13. Logging file and data processing

CSV example:

```python
import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def process_csv(path: Path) -> dict:
    logger.info("Opening %s", path)
    valid = 0
    skipped = 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            if not row.get("id"):
                logger.warning("Skipping row %d: missing 'id'", line_number)
                skipped += 1
                continue
            try:
                value = float(row["value"])
            except (KeyError, ValueError):
                logger.warning("Skipping row %d: invalid 'value'", line_number)
                skipped += 1
                continue
            logger.debug("Row %d parsed: id=%s value=%s", line_number, row["id"], value)
            valid += 1
    logger.info("Processed %s: %d valid, %d skipped", path, valid, skipped)
    return {"valid": valid, "skipped": skipped}
```

JSON Lines example:

```python
import json

def process_json_lines(path: Path) -> dict:
    valid = failed = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                logger.error("Line %d: invalid JSON (%s)", line_number, exc)
                failed += 1
                continue
            valid += 1
    logger.info("Processed %s: %d valid, %d failed", path, valid, failed)
    return {"valid": valid, "failed": failed}
```

Use DEBUG for per-record detail, WARNING for recoverable skipped records, ERROR for failed operations/invalid input the process cannot use, and INFO for progress and final counts.

## 14. File logging and rotation

`FileHandler` appends to its file. Without rotation, a long-running application can fill the disk.

- `RotatingFileHandler`: size-based rotation using `maxBytes`; `backupCount` controls retained backups.
- `TimedRotatingFileHandler`: time-based rotation using `when`; `backupCount` controls retained periods.

Choose retention based on operational need versus disk use. Set encoding explicitly and use a writable log directory.

## 15. Security and sensitive data

Never log passwords, API keys, access tokens, encryption/signing keys, authorization headers, full payment-card/account numbers, government IDs, or raw request bodies that may contain secrets.

Unsafe:

```python
logger.info("Authenticating with token %s", auth_token)
logger.debug("Payload: %s", request_body)
```

Safer:

```python
logger.info("Authenticating user %s", user_id)
logger.debug("Payload keys: %s", list(request_body.keys()))
```

Masking example:

```python
def mask(value: str, keep: int = 4) -> str:
    if keep < 0:
        raise ValueError("keep must be non-negative")
    if len(value) <= keep:
        return "*" * len(value)
    return "*" * (len(value) - keep) + value[len(value) - keep:]

logger.info("Processing card ending in %s", mask(card_number))

assert mask("") == ""
assert mask("123") == "***"
assert mask("1234567890", 4) == "******7890"
assert mask("1234567890", 0) == "**********"
```

A filter can centralize redaction, but mutating a shared LogRecord affects later handlers too. A handler-level filter is useful when destinations need different representations. Masking one call does not guarantee the raw value is absent from all other logs; omit secrets whenever possible.

## 16. Logging performance and lazy formatting

Avoid excessive INFO messages in tight loops. DEBUG is intended for high-volume detail and should be enabled deliberately.

Bad:

```python
logger.debug(f"Full record: {expensive_summary(record)}")
```

The f-string and function call happen even if DEBUG is disabled.

Better, but the function argument still runs:

```python
logger.debug("Full record: %s", expensive_summary(record))
```

Preferred for an expensive argument:

```python
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Full record: %s", expensive_summary(record))
```

`%`-style logging defers final string formatting until the record is emitted. It does not defer evaluation of argument expressions. Guard expensive computations with `isEnabledFor()`.

## 17. Library versus application logging

Both use:

```python
logger = logging.getLogger(__name__)
```

A library should:
- Use its own named logger.
- Never call `basicConfig()` or `dictConfig()`.
- Never configure the root logger or attach handlers globally.
- Optionally attach `logging.NullHandler()` to its package logger.

```python
logging.getLogger(__name__).addHandler(logging.NullHandler())
```

`NullHandler` prevents the library from forcing a fallback warning when the application has not configured logging.

The application owns configuration at its top-level entry point. One root configuration controls well-behaved child/library loggers through propagation.

## 18. Structured logging and observability

Plain-text log:

```text
2026-09-22 14:03:11 INFO Processed transactions.csv: 1200 records
```

Structured JSON log:

```json
{"timestamp":"2026-09-22T14:03:11Z","level":"INFO","event":"file_processed","file":"transactions.csv","records":1200}
```

Structured logs contain named fields, making large-scale search, filtering, and aggregation more reliable than parsing free-form sentences.

Python's standard logging does not natively emit JSON, but a custom formatter can do so:

```python
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(payload)
```

Observability commonly combines:
- **Logs:** timestamped events; what happened in this process?
- **Metrics:** numeric measurements over time; how many/ how fast?
- **Traces:** a request's path across services; where did this operation spend time?

This lesson focuses on logs; metrics and distributed tracing are later topics.

## 19. Common mistakes

1. Using print everywhere for diagnostics — use logging for diagnostics.
2. Wrong severity — match level to actual impact.
3. Too many messages — keep routine output useful and detailed output at DEBUG.
4. Too little context — include file, row, record ID, or count when safe.
5. Logging secrets — omit or mask sensitive data.
6. Duplicate messages — configure handlers once and understand propagation.
7. Duplicate exception logging — log once at the decision boundary.
8. Calling `basicConfig()` too late — configure before the first logging call.
9. Library configuring root logger — let the application configure it.
10. Missing traceback — use `logger.exception()` inside `except`.
11. Unbounded file — configure rotation and retention.
12. Mixing result and diagnostics — stdout for result, logging/stderr for diagnostics.
13. Swallowing exceptions — report and handle or re-raise deliberately.

## 20. All 14 progressive examples

1. `print("Result:", 42)` — use print for the actual result.
2. `logging.basicConfig(level=logging.INFO); logging.info("Application started")` — configure and emit INFO.
3. Set level WARNING; DEBUG/INFO are filtered, WARNING/ERROR appear.
4. `logging.getLogger(__name__)` — create a module-named logger.
5. Attach `StreamHandler`, set a formatter with timestamp/level/name/message, and log.
6. `StreamHandler(sys.stderr)` explicitly sends diagnostics to stderr.
7. `FileHandler("app.log", encoding="utf-8")` writes formatted log entries to a file.
8. Catch `ZeroDivisionError` and call `logger.exception("Division failed")` inside except.
9. Attach console WARNING handler and file DEBUG handler to one DEBUG logger; DEBUG goes only to file, WARNING goes to both.
10. In a CLI, `print("42")` is stdout result; `logger.info(...)` is stderr diagnostic.
11. `count_lines(path)` logs start/end, iterates file lines, returns count.
12. `RotatingFileHandler("app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")` bounds file growth.
13. `dictConfig()` declares formatter, StreamHandler, and root level/handlers as data.
14. A custom JSONFormatter serializes level, logger, and message as JSON.

## 21. API reference

| API | Purpose |
|---|---|
| `logging.getLogger(name)` | Get named logger |
| `debug/info/warning/error/critical` | Emit standard severity |
| `exception()` | ERROR plus active traceback |
| `log(level, ...)` | Emit dynamic level |
| `setLevel()` | Configure logger/handler threshold |
| `isEnabledFor()` | Check whether a level is enabled |
| `Logger`, `LogRecord` | Event source and event data |
| `Handler`, `StreamHandler`, `FileHandler` | Destination routing |
| `RotatingFileHandler`, `TimedRotatingFileHandler` | File rotation |
| `Formatter` | Format record |
| `Filter` | Custom filtering/redaction |
| `basicConfig()` | Simple root configuration |
| `dictConfig()` / `fileConfig()` | Declarative configuration |
| `NullHandler` | Library-safe no-op handler |
| `propagate` | Control upward record propagation |

---

# Part B — Stage 1 roadmap and current-level analysis

## 1. Roadmap structure

The roadmap defines Stage 1 — Programming & Computational Thinking — as **24 modules, 212 numbered lessons, and 282 files**. Its 24 modules are:

1. Computational Thinking and Program Design.
2. Python Core Language and Data Types.
3. Control Flow, Functions, Scope, and Errors.
4. Problem-Solving, Collections, and Algorithmic Habits.
5. Text Files, Structured Data, and CLI Programs.
6. Modules, Packages, Dependencies, and Code Quality.
7. Testing and Systematic Debugging.
8. Object-Oriented Design, Data Modelling, and Functional Style.
9. Advanced Production-Oriented Python Foundations.
10. Production Habits for Python Programs.
11. Advanced Python Data Model and Object Design.
12. Metaprogramming and Dynamic Python.
13. Standard Library Toolkit.
14. Bytes, Binary Data, and Advanced Text Processing.
15. Modern Python Language Features.
16. Advanced Testing and Test Architecture.
17. Profiling, Memory, and Runtime Performance.
18. Packaging, Distribution, and Publishing.
19. CPython Internals and Runtime Behaviour.
20. Design Patterns and Library API Design.
21. Data Visualization and Notebook Workflows.
22. Secure Python Coding.
23. Code Reading, Refactoring, and Code Review.
24. Functions and OOP Gap Lessons.

## 2. Module 05 sequence and progress

1. Reading and Writing Text Files — completed.
2. `pathlib` and Portable Paths — completed.
3. CSV Files — completed.
4. JSON and Serialization — completed.
5. Encodings and Newlines — completed.
6. Command-Line Arguments with `argparse` — completed.
7. Standard Streams and Exit Codes — completed.
8. **Logging versus Print — current lesson.**
9. Environment Configuration and Input Validation — not yet completed.
10. Module README and practice questions — later.

## 3. Stage 1 projects

- **Personal Expense Ledger CLI:** command-line expense tracking and reporting.
- **Log Investigation and Reliability CLI:** operational log inspection and reliability analysis.
- **Data Quality and Transformation Pipeline:** `orders.csv`, a `dqpipe` package (`cli.py`, `config.py`, `pipeline.py`, `rules.py`), tests, configuration, and data contract.
- **Rule-Based Risk Review Engine:** `transactions.csv`, `rules.toml`, a `riskreview` package (`cli.py`, `engine.py`, `io.py`, `models.py`, `rules.py`), tests, and golden decision data.

## 4. Current level and scope decision

Your recorded level is **beginner progressing toward intermediate**. You have studied Python fundamentals, collections, control flow, functions, argument design, scope, pure functions, side effects, exceptions, parsing, Big-O, text files, `pathlib`, CSV, JSON, encodings/newlines, `argparse`, and standard streams/exit codes.

This lesson is the direct continuation of Lesson 07. The exercises can use `logging`, functions, `Path`, CSV/JSON, `argparse`, exceptions, `main(argv)`, and the pytest capture patterns already introduced. The lesson mentions structured logs and observability, but those are explained conceptually rather than expanded into advanced infrastructure. The solutions avoid introducing unrelated libraries or later-stage engineering topics.

The most relevant projects are the Log Investigation CLI, Data Quality Pipeline, and Risk Review Engine: they need useful operational diagnostics, clean machine-readable output, traceable failures, and bounded log storage.

---

# Part C — All 12 coding exercises solved

## Beginner

### 1. Use print for the actual result

```python
total = 125
print(total)  # The user asked for the calculated result, not a diagnostic.
```

`total` stores the result. `print()` writes that requested result to stdout. Logging is unnecessary for this one-off user-facing output.

### 2. Emit all five standard levels

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Detailed row parsing")
logger.info("Started processing")
logger.warning("Skipped an invalid row")
logger.error("Could not write output")
logger.critical("Required service is unavailable")
```

`DEBUG` is the lowest standard level, so a DEBUG threshold allows all five messages. The named logger propagates to the configured root handler.

### 3. Create a named logger

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Data pipeline started")
```

`getLogger(__name__)` names the logger after this module. `.info()` creates an INFO record; it appears because the configured root level allows it.

## Intermediate

### 4. Console WARNING and file DEBUG

```python
import logging

logger = logging.getLogger("exercise4")
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.WARNING)

file_handler = logging.FileHandler("exercise4.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

logger.addHandler(console)
logger.addHandler(file_handler)

logger.debug("detail")
logger.warning("recoverable problem")
```

The logger accepts DEBUG and above. The console handler rejects DEBUG but accepts WARNING. The file handler accepts both. Inspect the terminal and `exercise4.log` to verify independent filtering.

### 5. Formatter with timestamp, level, and filename

```python
import logging

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s %(filename)s: %(message)s"
))

logger = logging.getLogger("exercise5")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.info("Loaded input.csv")
```

`asctime` is the event timestamp; `levelname` is INFO; `filename` is the source Python file containing this logging call. The message follows the colon.

### 6. Log an exception with traceback

```python
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

try:
    number = int("not-a-number")
except ValueError:
    logger.exception("Could not convert input to an integer")
```

`int()` raises `ValueError`. The except block handles it, so `logger.exception()` can attach the active traceback. The log includes the message, exception type, and traceback.

### 7. Keep stdout result separate from stderr log

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> int:
    logger.info("Starting")
    print("42")
    logger.info("Finished")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Run `python app.py > out.txt`. `out.txt` contains only `42`; default logging remains on stderr. `main()` returns 0 and the entry point turns it into process status 0.

### 8. Verify FileHandler append behavior

```python
import logging

logger = logging.getLogger("exercise8")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("append-test.log", encoding="utf-8")
logger.addHandler(handler)

logger.info("run completed")
handler.close()
logger.removeHandler(handler)
```

Run the script twice. `FileHandler` appends by default, so the file contains both runs. The handler is closed and removed after use.

## Advanced

### 9. Demonstrate size-based rotation

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("exercise9")
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.WARNING)

file_handler = RotatingFileHandler(
    "rotate.log", maxBytes=300, backupCount=3, encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(console)
logger.addHandler(file_handler)

for number in range(100):
    logger.debug("Record %d: sample diagnostic message", number)
```

The console accepts WARNING and above; the file accepts DEBUG. Small `maxBytes` makes rotation easy to trigger. After enough records, inspect `rotate.log`, `rotate.log.1`, and other retained backups. `backupCount=3` limits retained rotated files.

### 10. Reproduce the handler setup with dictConfig

```python
import logging.config

config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(levelname)s %(name)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "WARNING",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "rotate-config.log",
            "maxBytes": 300,
            "backupCount": 3,
            "encoding": "utf-8",
            "formatter": "default",
            "level": "DEBUG",
        },
    },
    "root": {"level": "DEBUG", "handlers": ["console", "file"]},
}

logging.config.dictConfig(config)
logger = logging.getLogger("exercise10")
logger.debug("written to file")
logger.warning("written to file and console")
```

The dictionary declares formatter, both handlers, their thresholds, and root configuration. `dictConfig()` applies the setup in one place.

### 11. Redact a sensitive field with a Filter

```python
import logging

class RedactTokenFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        record.msg = message.replace("secret-token", "***REDACTED***")
        record.args = ()
        return True

handler = logging.StreamHandler()
handler.addFilter(RedactTokenFilter())

logger = logging.getLogger("exercise11")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

logger.info("Request used token %s", "secret-token")
```

The filter obtains the fully formatted message, replaces the sensitive token, clears formatting arguments, and allows the record through. In production, avoid logging secrets at all; this simple demonstration is not a complete universal redaction system. Because a filter mutates the record, other handlers receiving the same record may see the masked version too.

### 12. Logging strategy for sensitive customer data

- DEBUG: safe technical detail, record IDs only when permitted, field names, counts; never raw customer payloads or secrets.
- INFO: batch start/end, filenames, totals, valid/invalid counts, upload completion.
- WARNING: invalid/skipped record identifiers and reason codes, with sensitive values omitted or masked.
- ERROR: failed file read, transformation, or upload, with safe context and exception details that do not expose secrets.
- CRITICAL: system-wide failure preventing safe processing, such as storage being unavailable.
- stdout: only requested machine-readable result/summary.
- stderr/log handlers: diagnostics.
- Configure rotation and retention; restrict access to log storage.
- Use a consistent redaction policy and tests to prevent secret leakage.



## Line-by-line walkthrough of the 12 exercise solutions

1. **Result with `print()`:** `total = 125` stores the computed value. `print(total)` sends that result to stdout. The comment explains why it is user output, not an operational diagnostic.
2. **Five levels:** `import logging` loads the standard library. `basicConfig(level=logging.DEBUG)` configures root to accept the lowest standard level. `getLogger(__name__)` creates this module's logger. Each of the five calls creates a record with its corresponding severity; all pass the DEBUG threshold.
3. **Named logger:** `basicConfig(level=logging.INFO)` configures output before the first logging call. `getLogger(__name__)` gives the module a hierarchical logger name. `.info(...)` emits a routine operational event.
4. **Two handlers:** `getLogger("exercise4")` creates a named logger; `setLevel(DEBUG)` lets detailed records through. The console handler rejects below WARNING. The file handler rejects below DEBUG. Both are attached to the same logger. DEBUG is therefore written only to the file, while WARNING reaches both destinations.
5. **Formatter:** `StreamHandler()` selects stderr by default. `setFormatter(...)` defines three metadata fields and the message. `getLogger(...)` creates a named logger, `setLevel(INFO)` permits INFO, `addHandler(...)` connects the destination, and `.info(...)` produces a test record.
6. **Traceback:** `basicConfig(ERROR)` allows error-level events. `getLogger` creates the module logger. `int("not-a-number")` raises `ValueError`. The `except` block establishes the active exception context. `logger.exception(...)` logs the message and traceback.
7. **CLI separation:** `basicConfig(INFO)` configures diagnostic output. `main()` logs start, prints the actual value to stdout, logs completion, and returns zero. The `if __name__ == "__main__"` guard prevents automatic process termination when imported. `SystemExit(main())` applies the returned status only when run as a script.
8. **Append test:** `getLogger` creates a logger and `setLevel(INFO)` allows its messages. `FileHandler` opens the file in append mode by default. `addHandler` connects it. Each run writes one new record. Closing and removing the handler releases the file and avoids leaving the handler attached.
9. **Rotation:** the logger accepts DEBUG. Console only accepts WARNING. The rotating file handler accepts DEBUG and rotates after roughly 300 bytes, retaining three backups. The loop emits enough messages to exceed the limit repeatedly. Inspect the active file and backups to verify rotation.
10. **Declarative configuration:** `version` identifies the dictConfig schema. `formatters` names the output format. `handlers` declares console and rotating-file destinations with separate thresholds. `root` connects both handlers and accepts DEBUG. `dictConfig` applies the entire configuration. The two log calls demonstrate destination-specific filtering.
11. **Redaction filter:** the class extends `logging.Filter`. Its `filter(record)` method obtains the formatted message, replaces the demonstration token, clears old formatting arguments so they are not applied again, and returns True to allow output. The handler runs this filter before formatting. The logger emits an INFO record through that handler.
12. **Sensitive-data policy:** the five bullet levels distinguish detail, routine status, recoverable data problems, failed operations, and system-wide failures. The destination rules keep actual results on stdout and diagnostics in logging. Rotation and access control protect operational history. Redaction tests help detect accidental leakage.


---

# Part D — All 9 debugging lab exercises

1. **`basicConfig()` does nothing:** an earlier module-level logging call implicitly configured root. Move `basicConfig()` before every logging call.
2. **Duplicate log lines:** the same logger has two StreamHandlers or configuration ran repeatedly. Add each handler once; guard or clear before reconfiguration.
3. **Logs on wrong stream:** inspect whether a StreamHandler was explicitly pointed at stdout or print was pointed at stderr. Keep default StreamHandler on stderr.
4. **Missing traceback:** `logger.error()` logs only text. Inside the `except` block, use `logger.exception()`.
5. **Log file missing:** confirm configuration ran before logging, the target directory exists/is writable, and the path is relative to the expected current working directory.
6. **DEBUG missing:** check both logger and handler levels. A DEBUG logger record can still be rejected by an INFO-level handler.
7. **Huge log file:** DEBUG or per-record INFO may be enabled at high volume. Use INFO/WARNING defaults and configure rotation.
8. **Wrong severity:** classify the actual outcome. Recoverable issue is often WARNING; failed operation is ERROR; severe system failure is CRITICAL.
9. **Repeated configuration duplicates handlers:** a function that adds a handler each call accumulates them. Check `logger.handlers` or clear/close existing handlers before rebuilding configuration.

---

# Part E — Interview questions and answers

1. **print vs logging?** `print()` writes unstructured text; logging provides severity, filtering, metadata, configurable destinations, and tracebacks.
2. **When is print correct in production?** When writing the actual user-requested result, not a diagnostic.
3. **Why does StreamHandler default to stderr?** Diagnostics should not contaminate stdout result data.
4. **Logger vs LogRecord?** Logger is the API called by code; LogRecord is the structured event created for an accepted call.
5. **Handler vs Formatter?** Handler chooses destination; Formatter chooses rendered representation.
6. **What does Filter add?** Custom record-level logic such as module selection or redaction.
7. **What is root logger?** Top-level ancestor that receives propagated records and can centrally control application output.
8. **Hierarchy/propagation?** `app.io` is a child of `app`; records propagate to ancestor handlers unless disabled.
9. **Five levels?** DEBUG detail, INFO routine operation, WARNING recoverable issue, ERROR failed operation, CRITICAL severe system failure.
10. **exception vs error?** Both log at ERROR; exception adds the currently handled traceback.
11. **Why inside except?** It needs an active exception context to obtain the traceback.
12. **FileHandler risk?** It appends to disk; without rotation it can grow until disk space is exhausted.
13. **Rotating vs TimedRotating?** One rotates by size; the other by time.
14. **Why no secrets in logs?** Logs persist and are forwarded/retained, so leaked credentials can remain exposed long after execution.
15. **Why lazy `%` formatting?** Final string formatting is deferred until the record is emitted; f-strings are evaluated immediately.
16. **Library vs application responsibility?** Library emits through its named logger; application owns global configuration.
17. **Why library must not call basicConfig?** It would unexpectedly alter the embedding application's logging configuration.
18. **Structured logging?** Named machine-readable fields, commonly JSON, make large-scale filtering/search/aggregation reliable.
19. **Logs vs metrics vs traces?** Logs describe events; metrics aggregate numeric behavior; traces show one operation's path across components.
20. **Pipeline CLI strategy?** stdout for clean result, logging/stderr and optionally file for diagnostics, exit code for automation.

---

# Part F — Knowledge-check answers

1. Logging provides built-in severity levels and filtering; print does not.
2. Log once where the response decision is made to avoid duplicate records as exceptions propagate.
3. Only the WARNING message appears: the named logger's WARNING threshold rejects INFO.
4. The f-string and `expensive_repr()` execute even when DEBUG is disabled; use lazy formatting and an `isEnabledFor(DEBUG)` guard for expensive argument computation.
5. Check whether the intended handler is attached and whether `maxBytes`/the inspected file path are correct.
6. `logger.exception()` was called outside an active except block.
7. A print or handler is writing diagnostics to stdout; route all diagnostics to logging/stderr.
8. The library likely prints directly or configures root; it should use `getLogger(__name__)` and leave configuration to the application.
9. DEBUG per-file parsing; INFO start/finish/upload; WARNING skipped invalid file; ERROR upload operation failure; CRITICAL whole-batch-threatening service failure.

---

# Part G — End-to-end mini-project: Production-Style File Processing CLI

## 1. Requirements and architecture

Build `process_records.py` to:
- Read a JSON Lines file.
- Validate each record.
- Print a clean JSON summary to stdout.
- Send progress, warnings, and errors through logging.
- Support `--log-level` and `--log-file`.
- Write console and rotating file logs.
- Return 0 if all records are valid, 3 if some records are invalid, and 2 if the input cannot be read/found.
- Never log secrets.
- Keep validation separate from logging and process termination.

Architecture:

```text
build_parser()
    ↓
configure_logging()  # top-level application responsibility
    ↓
validate_record()    # pure validation
    ↓
process_file()       # file processing + operational diagnostics
    ↓
main(argv)           # final stdout result + exit status
    ↓
SystemExit(main())
```

## 2. Implementation

```python
import argparse
import json
import logging
import logging.config
from collections.abc import Sequence
from pathlib import Path

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a JSON Lines file of records."
    )
    parser.add_argument("input_file", type=Path)
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("process_records.log"),
    )
    return parser


def configure_logging(level: str, log_file: Path) -> None:
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s %(name)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": str(log_file),
                "maxBytes": 1_000_000,
                "backupCount": 3,
                "encoding": "utf-8",
                "level": "DEBUG",
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        },
    })


def validate_record(record: dict) -> list[str]:
    errors = []
    if "id" not in record:
        errors.append("missing 'id'")
    if "value" not in record:
        errors.append("missing 'value'")
    return errors


def process_file(path: Path) -> dict:
    valid = 0
    invalid = 0
    logger.info("Starting processing of %s", path)

    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue

            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                logger.warning("Line %d: invalid JSON: %s", line_number, exc)
                invalid += 1
                continue

            if not isinstance(record, dict):
                logger.warning("Line %d: expected a JSON object", line_number)
                invalid += 1
                continue

            logger.debug(
                "Line %d: parsed record with keys %s",
                line_number,
                list(record.keys()),
            )

            errors = validate_record(record)
            if errors:
                logger.warning(
                    "Line %d: invalid record (%s)",
                    line_number,
                    "; ".join(errors),
                )
                invalid += 1
                continue

            valid += 1

    logger.info(
        "Finished processing %s: %d valid, %d invalid",
        path,
        valid,
        invalid,
    )
    return {"valid": valid, "invalid": invalid}


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure_logging(args.log_level, args.log_file)

    if not args.input_file.is_file():
        logger.error("Input file not found: %s", args.input_file)
        return 2

    try:
        summary = process_file(args.input_file)
    except (OSError, UnicodeDecodeError) as exc:
        logger.error("Could not read %s: %s", args.input_file, exc)
        return 2

    print(json.dumps(summary))
    return 0 if summary["invalid"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
```

## 3. Explanation

- `build_parser()` declares the required input path and configurable log level/file.
- `configure_logging()` sets up two destinations: console at the selected threshold and a rotating file at DEBUG. The root level is DEBUG so the file can receive detailed records.
- `validate_record()` checks required keys and returns errors. It does not log or exit.
- `process_file()` reads line by line, skips blank lines, parses JSON, checks the top-level type, validates keys, counts valid/invalid records, and logs contextual diagnostics.
- Expected invalid JSON and invalid schema are warnings because the batch can continue.
- `main()` configures logging once, validates file availability, catches expected I/O/decode failures, prints only the JSON summary to stdout, and returns a documented status.
- `raise SystemExit(main())` converts the return code to the process exit status.

## 4. Example

Input:

```json
{"id": 1, "value": "a"}
{"id": 2}
not json
```

Run:

```bash
python process_records.py data.jsonl --log-level INFO --log-file run.log
```

stdout (machine-readable):

```json
{"valid": 1, "invalid": 2}
```

stderr/log file: start message, warnings for line 2 and line 3, and final counts. Exit status is 3.

## 5. Tests

```python
import json
import logging
import pytest

from process_records import main, process_file, validate_record


@pytest.fixture(autouse=True)
def restore_root_logger():
    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level
    yield
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        if handler not in saved_handlers:
            handler.close()
    for handler in saved_handlers:
        root.addHandler(handler)
    root.setLevel(saved_level)


def test_validate_record():
    assert validate_record({"id": 1, "value": "x"}) == []
    assert validate_record({}) == ["missing 'id'", "missing 'value'"]


def test_all_valid_records(tmp_path, capsys):
    path = tmp_path / "data.jsonl"
    path.write_text('{"id": 1, "value": "a"}\n', encoding="utf-8")
    log_path = tmp_path / "app.log"

    status = main([str(path), "--log-file", str(log_path)])
    captured = capsys.readouterr()

    assert status == 0
    assert json.loads(captured.out.strip()) == {"valid": 1, "invalid": 0}
    assert log_path.exists()


def test_invalid_record_logged(tmp_path, caplog):
    path = tmp_path / "data.jsonl"
    path.write_text('{"id": 1}\n', encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        summary = process_file(path)

    assert summary == {"valid": 0, "invalid": 1}
    assert any("invalid record" in record.message for record in caplog.records)


def test_unreadable_input_returns_2(tmp_path, monkeypatch, capsys):
    path = tmp_path / "data.jsonl"
    path.write_text('{"id": 1, "value": "a"}\n', encoding="utf-8")

    def deny(path):
        raise PermissionError("denied")

    monkeypatch.setattr("process_records.process_file", deny)
    status = main([str(path), "--log-file", str(tmp_path / "app.log")])

    assert status == 2
    assert capsys.readouterr().out == ""


def test_unexpected_error_is_not_swallowed(tmp_path, monkeypatch):
    path = tmp_path / "data.jsonl"
    path.write_text("{}\n", encoding="utf-8")

    def bug(path):
        raise RuntimeError("programming error")

    monkeypatch.setattr("process_records.process_file", bug)
    with pytest.raises(RuntimeError):
        main([str(path), "--log-file", str(tmp_path / "app.log")])
```

`restore_root_logger` prevents `dictConfig()` from leaving the root logger changed for later tests. `capsys` verifies stdout; `caplog` inspects records; `tmp_path` supplies isolated files; `monkeypatch` simulates an I/O failure or unexpected bug. The expected I/O failure maps to status 2; an unexpected programming error is not silently swallowed.

**Production improvements identified by the lesson:** structured JSON log output, `--fail-fast`, an invalid-record percentage threshold, external environment-specific logging configuration, and a fully documented exit-code contract.

---

# Part H — Mastery checklist

- [ ] Explain exactly what `print()` does and its legitimate uses.
- [ ] Explain why print-only diagnostics do not scale.
- [ ] Describe Logger → LogRecord → Handler → Formatter → destination.
- [ ] Select DEBUG, INFO, WARNING, ERROR, and CRITICAL correctly.
- [ ] Distinguish logger and handler levels.
- [ ] Use `getLogger(__name__)` and understand propagation.
- [ ] Configure StreamHandler, FileHandler, and rotation.
- [ ] Format timestamps, levels, module names, and line numbers.
- [ ] Use filters for custom record handling and redaction.
- [ ] Configure basicConfig early and understand why it may do nothing.
- [ ] Use dictConfig for multiple handlers.
- [ ] Keep stdout for results and stderr/logging for diagnostics.
- [ ] Use exception logging only inside an except block.
- [ ] Avoid duplicate logging and swallowed exceptions.
- [ ] Never log secrets or raw sensitive customer data.
- [ ] Use lazy `%` formatting and guard expensive computations.
- [ ] Keep library logging separate from application configuration.
- [ ] Explain structured logs, metrics, and traces.
- [ ] Test stdout, stderr, log records, file output, and exit status.
- [ ] Build the production-style JSONL processing CLI.

**Next roadmap lesson:** `09-environment-configuration-and-input-validation.md`. Do not advance until you can configure a logger, write clean stdout output, capture diagnostics separately, rotate a log file, and test the CLI's behavior.
