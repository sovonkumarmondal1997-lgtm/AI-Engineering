# Logging versus print()

## Learning Objectives

By the end of this chapter you will be able to:

- Explain precisely what `print()` does, and use it correctly for its
  legitimate purposes: user-facing CLI output and quick, temporary
  debugging.
- Explain, concretely, why `print()` is not a substitute for an
  application's diagnostic/logging system — not because `print()` is
  "bad," but because of specific, nameable capabilities it lacks.
- Explain Python's logging architecture: `Logger`, `LogRecord`,
  `Handler`, `Formatter`, and `Filter`, and how data flows through
  them.
- Use every standard severity level (`DEBUG`, `INFO`, `WARNING`,
  `ERROR`, `CRITICAL`) appropriately, and control filtering with
  logger and handler levels.
- Use `logging.getLogger(__name__)`, the logger hierarchy, and
  propagation correctly, including why library code and application
  code have different responsibilities.
- Use `StreamHandler`, `FileHandler`, `RotatingFileHandler`, and
  `TimedRotatingFileHandler`, and configure `Formatter` objects with
  the metadata fields production logs rely on.
- Use `logging.exception()` correctly, inside an `except` block, and
  explain how it differs from `logger.error()`.
- Configure logging with `basicConfig()` for simple programs and
  `logging.config.dictConfig()` for structured, production
  configuration — and explain why `basicConfig()` can appear "not to
  work."
- Explain the relationship between `print()`/logging and stdout/stderr,
  building directly on
  [07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md).
- Separate user-facing output from diagnostic output in a CLI program,
  and explain why that separation matters for pipelines, automation,
  and CI/CD.
- Log exceptions and errors correctly — preserving tracebacks, avoiding
  duplicate logging, and avoiding silently swallowed failures.
- Apply logging to realistic file/data-processing scenarios: invalid
  records, skipped rows, transformation failures, progress, and
  summaries.
- Set up file logging and rotation, and explain the tradeoffs between
  size-based and time-based rotation.
- Recognize what must never appear in logs (secrets, credentials,
  sensitive personal data) and apply basic masking/redaction.
- Use lazy `%`-style log message formatting and explain why it is
  preferred over eager string formatting for performance.
- Explain the difference between library logging and application
  logging, and why a library should never configure logging globally.
- Explain structured (machine-readable) logging conceptually, and why
  production systems favor it for aggregation and search.
- Place logs correctly relative to metrics and traces in the broader
  concept of observability.
- Recognize and avoid the classic logging mistakes.
- Design a production-style CLI that cleanly separates business logic,
  user output, and logging.

## Prerequisites

This chapter assumes you have completed
[06-command-line-arguments-with-argparse.md](06-command-line-arguments-with-argparse.md)
(the `main(argv) -> int` CLI architecture) and
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)
(stdin/stdout/stderr, exit codes, and the stdout-vs-stderr separation
principle this chapter extends directly into logging). No prior
knowledge of Python's `logging` module is assumed.

## 1. `print()` Fundamentals

Before critiquing `print()` as a logging tool, make sure its actual
mechanics are completely clear — everything that follows depends on
understanding exactly what `print()` does and does not do.

```python
print("Hello")
```

Conceptually, this one line: builds the string `"Hello"`, writes it to
`sys.stdout` (§13 connects this directly to the previous chapter),
appends a trailing newline, and returns `None`. Nothing more happens —
`print()` has no concept of severity, no concept of "this is a debug
message versus a real result," and no built-in way to turn it off
later without editing or deleting the call.

The full signature, and what each part controls:

```python
print(*objects, sep=" ", end="\n", file=sys.stdout, flush=False)
```

- **Positional arguments (`*objects`)** — any number of values;
  `print()` converts each to a string (via `str()`) automatically.
  ```python
  print("count:", 5, True)   # count: 5 True
  ```
- **`sep=`** — the string placed *between* multiple positional
  arguments (default a single space).
  ```python
  print("a", "b", "c", sep=", ")   # a, b, c
  ```
- **`end=`** — what's written *after* everything else, instead of the
  default trailing newline.
  ```python
  print("loading", end="...")
  print("done")
  # loading...done
  ```
- **`file=`** — which stream to write to; defaults to `sys.stdout`,
  and can be set to `sys.stderr` (§13) or any other writable, file-like
  object.
- **`flush=`** — whether to force this call's output out immediately
  rather than leaving it in a buffer (see
  [07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)'s
  §14 for the full buffering explanation).

Printing objects other than strings works via `str()` conversion:

```python
print([1, 2, 3])          # [1, 2, 3]
print({"a": 1})            # {'a': 1}
```

f-strings are the standard, readable way to build the message itself
before printing it:

```python
name = "Alice"
count = 3
print(f"{name} processed {count} records")
```

`print()` has two primary, appropriate uses in a well-designed Python
program (this is this chapter's teaching framing, not a rule defined by
Python): **user-facing CLI output** (the actual result the program
exists to produce) and **temporary, throwaway debugging** or
experimentation during development (a `print(x)` you add to see a
value, then delete). §2–§3 work through why those two uses are
appropriate and why other uses are where problems start.

## 2. When `print()` Is Appropriate

State this plainly, because it is easy to over-correct after learning
about logging's advantages: **`print()` is not inherently bad.** It is
the right, simple, standard tool for several genuinely common
situations:

- **User-facing CLI output** — the actual result a command-line program
  exists to produce: a summary, a computed value, a machine-readable
  document (JSON, a report). This is exactly the "stdout carries the
  program's intended output" principle from
  [07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)'s
  §7 and §9.
- **Program results in simple, one-off scripts** — a fifteen-line
  script that reads a file and prints a number has no real need for
  a logging framework.
- **Learning and experimentation** — when you're actively learning a
  new API or exploring how some code behaves, `print()` is the fastest
  possible feedback loop, with zero setup.
- **Temporary debugging** — adding a `print(some_variable)` while
  chasing down a bug, with the clear, explicit intention of deleting it
  once the bug is found.
- **Appropriate progress/status messages for a human running a tool
  interactively** — a short-lived CLI utility printing `"Processing
  file 3 of 10..."` directly to a human watching it run is a
  reasonable design choice, provided (§14) it doesn't end up polluting
  machine-readable stdout output.

The issue this whole chapter builds toward is narrower and more
specific than "`print()` is bad": **using `print()` as an
application's long-term, only diagnostic and logging mechanism** does
not scale, for reasons §3 makes concrete one at a time.

## 3. Why `print()` Is Not Application Logging

Each limitation below is real, specific, and independently sufficient
to cause real problems in anything beyond a small script.

**No standard severity levels.** Every `print()` call is equally
"important" from the language's point of view — there is no built-in
way to distinguish "this is routine detail" from "this is a critical
failure" without inventing your own ad hoc convention (`print("DEBUG:
...")`, `print("ERROR: ...")`) that nothing else in the language
understands or can act on.

**Weak filtering.** Because there are no real severity levels, there is
no way to say "show me only warnings and above" without either
commenting out `print()` calls by hand or building your own filtering
logic from scratch — every single time, in every single program.

**Limited metadata.** A `print()` call carries only what you
explicitly typed into the string. No timestamp, no module name, no
line number, no process ID — unless you manually add every one of
those, to every single call, yourself.

**Difficult routing.** Every `print()` call goes to exactly one place —
wherever `file=` points (stdout, by default). Sending some messages to
the console, others to a file, and others to a monitoring system,
*without editing every call site*, is not something `print()` supports
at all.

**Difficult configuration.** There is no central place to say "turn on
verbose output" or "log to this file instead" for a program built on
`print()` — that behavior, if you want it, has to be hand-built,
program by program.

**Difficult production management.** In a running production system —
especially one with multiple processes or containers — there is no
standard way to enable, disable, or adjust `print()`-based diagnostics
without redeploying code.

**Difficult aggregation/search.** Modern production systems typically
collect logs from many processes into one searchable system. Doing
this reliably depends on some consistency in format and structure
(§21) — unstructured `print()` output, one ad hoc string at a time,
resists this badly.

**Difficult automation.** Nothing can reliably react to `print()`
output — a monitoring system can't easily be told "alert me whenever
an ERROR-level message appears" if there's no concept of level at all.

**Mixing user output with diagnostics.** Without a deliberate
separation, `print()` calls for "the actual result" and `print()`
calls for "just letting you know what's happening" end up on the same
stream, in the same undifferentiated stream of text — directly
recreating the exact problem
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)'s
§9 diagnosed for stdout/stderr, now inside a single program's own
internal design.

**Poor operational visibility.** When something goes wrong in
production, at 3 a.m., with no one watching a terminal, `print()`
output that was never captured or routed anywhere durable is
effectively gone.

**Bad code → problem → improved code**, concretely:

```python
# BAD: ad hoc severity via string prefixes, no real filtering, no metadata
def process_file(path):
    print(f"Processing {path}")
    try:
        data = load(path)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return
    print(f"Done: {len(data)} records")
```

*Problem:* no way to suppress the "Processing..." line in production
without deleting it; no timestamp on the error; no way to route the
error somewhere durable; "ERROR:" is just a string, meaningless to any
other tool.

```python
# IMPROVED: real levels, real metadata, real filtering, real routing
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

Section 4 onward builds up exactly what makes this "improved" version
work — and why every piece of it (the logger, the level, the
`%s`-style formatting, `logger.exception`) exists for a specific
reason, not as ceremony.

## 4. Python Logging Fundamentals

```python
import logging
```

The `logging` module, part of the Python standard library, is the
answer to every limitation in §3 — a real, structured, configurable
diagnostic system, built into Python itself, requiring no third-party
dependency.

The mental model to build first, before any API details:

```
APPLICATION CODE
      ↓  logger.info("message", ...)
    LOGGER            — decides: is this severe enough to matter at all?
      ↓
  LogRecord            — one structured object: message + level + time + module + ...
      ↓
   HANDLER             — decides: where should this go? (console? file? both?)
      ↓
  FORMATTER            — decides: what should the final text actually look like?
      ↓
  DESTINATION          — console, a file, or wherever the handler points
```

Each component has one clear job:

- **`Logger`** — the object your code actually calls
  (`logger.info(...)`, `logger.error(...)`). It decides, based on its
  own configured level (§5), whether a given call is even worth
  turning into a record at all.
- **`LogRecord`** — created automatically, once per logging call that
  passes the level check. It's a structured object carrying the
  message, the severity level, a timestamp, the logger's name, the
  module and line number the call came from, and more (§10 shows how
  to display these fields).
- **`Handler`** — decides *where* a `LogRecord` ends up: the console
  (`StreamHandler`), a file (`FileHandler`), a rotating file (§17), or
  several destinations at once (a logger can have multiple handlers).
- **`Formatter`** — decides what the final text actually looks like —
  which fields appear, in what order, in what format.
- **`Filter`** — an optional, finer-grained gate beyond level checking,
  covered in §11.
- **The root logger** — a single, always-present, top-level logger
  every other logger is ultimately a descendant of (§8).
- **A named logger** — a logger obtained via
  `logging.getLogger("some.name")`, distinct from the root logger, and
  the standard way real applications and libraries get a logger of
  their own (§8).

Every section from here through §17 fills in one part of this
pipeline in full detail; §4's job is only to make sure the whole shape
is visible before the details arrive.

## 5. Logging Levels

Python's logging module defines five standard severity levels, each
with a specific meaning:

| Level | Numeric value | Meaning | Realistic example |
|---|---|---|---|
| `DEBUG` | 10 | Fine-grained detail, useful only while actively diagnosing a problem | `"Parsed row 42: {'id': 7, 'value': 'x'}"` |
| `INFO` | 20 | Confirmation that things are working as expected; routine operational events | `"Processing file data.csv"`, `"Loaded 1,200 records"` |
| `WARNING` | 30 | Something unexpected happened, or a potential problem, but the program can continue | `"Skipping row 12: missing 'id' field"` |
| `ERROR` | 40 | A real failure — some specific operation could not complete | `"Failed to write output file: permission denied"` |
| `CRITICAL` | 50 | A severe failure, often threatening the whole program's ability to continue | `"Database connection pool exhausted; shutting down"` |

Each level has both a **logger-level** and a **handler-level** setting,
and both act as filters:

- **Logger level** — the minimum severity this logger will even
  produce a `LogRecord` for. A logger set to `WARNING` will simply
  discard `DEBUG` and `INFO` calls before any handler ever sees them
  — cheaply, with almost no overhead (§19 covers exactly how cheap).
- **Handler level** — a *further* filter, applied per-destination,
  *after* the logger has already decided to produce a record. This
  lets one handler show everything at `DEBUG` (e.g., a detailed log
  file) while another shows only `WARNING` and above (e.g., the
  console), from the same logger, at the same time.

```python
logger.setLevel(logging.DEBUG)          # the logger itself passes DEBUG and above onward
console_handler.setLevel(logging.WARNING)  # but this handler only displays WARNING and above
```

Why `DEBUG` should normally be controlled deliberately in production:
`DEBUG`-level messages are, by design, extremely detailed and
high-volume — appropriate while actively investigating a specific
problem, but typically far too noisy (and, per §19, not free) to leave
enabled by default in a running production system. The standard
pattern is to run production at `INFO` or `WARNING`, and temporarily
raise the level to `DEBUG` (via configuration, §12 — never by editing
and redeploying code) when actively diagnosing an issue.

## 6. Required Python Logging APIs

Two distinct ways to call the logging module exist, and it's important
to know both — and which one to actually use.

**Module-level convenience functions** — quick, but implicitly use the
**root logger**:

```python
import logging

logging.debug("debug message")
logging.info("info message")
logging.warning("warning message")
logging.error("error message")
logging.critical("critical message")
logging.exception("error with traceback")   # §7 — call only inside except
```

**Explicit `Logger` object methods** — the standard pattern for real
applications and modules (§8 explains exactly why):

```python
logger = logging.getLogger(__name__)

logger.debug("debug message")
logger.info("info message")
logger.warning("warning message")
logger.error("error message")
logger.critical("critical message")
logger.exception("error with traceback")
logger.log(logging.INFO, "explicit level: %s", "info")   # rarely needed directly
logger.setLevel(logging.DEBUG)
```

`logger.log(level, message, ...)` is the fully general form every
convenience method (`.debug()`, `.info()`, etc.) is shorthand for —
useful mainly when the level itself is a variable, computed at
runtime, rather than known in advance.

**Configuration entry points:**

```python
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
```

`basicConfig()` is the quick, one-call way to set up the root logger
with a level, a format, and (implicitly) a console handler — the right
tool for simple scripts and this chapter's early examples (§12 covers
its behavior, and its most common pitfall, in full).

**Key classes and components**, each covered in its own section below:
`Logger` (§8), `LogRecord` (§4), `Handler`/`StreamHandler`/
`FileHandler`/`RotatingFileHandler`/`TimedRotatingFileHandler` (§9,
§17), `Formatter` (§10), `Filter` (§11).

**Structured configuration:**

```python
import logging.config

logging.config.dictConfig({...})   # §12 — production-grade configuration as data, not code
```

`logging.config.fileConfig()` is an older, `.ini`-file-based
alternative to `dictConfig()` — functionally similar in purpose
(external, declarative logging configuration) but generally considered
less flexible and less commonly used in modern code; `dictConfig()`
(taking a plain Python dictionary, easily built from JSON or YAML) is
the more common modern choice and the one this chapter focuses on.

## 7. `logging.exception()`

`logger.exception(message)` is a specialized method, meant to be
called **from inside an `except` block**, that logs the given message
at `ERROR` level *and automatically attaches the current exception's
full traceback*.

```python
try:
    result = risky_operation()
except Exception:
    logger.exception("Operation failed")
```

Mechanically, `logger.exception(msg)` is equivalent to
`logger.error(msg, exc_info=True)` — it captures whatever exception is
currently being handled (via `sys.exc_info()`, checked internally) and
includes its full traceback in the resulting log output, without you
needing to format or capture that traceback yourself.

The distinction that matters:

```python
logger.error("Operation failed")          # message only — NO traceback attached
logger.exception("Operation failed")      # message + full traceback attached
```

`logger.error()` and `logger.exception()` produce a log record at the
exact same severity (`ERROR`) — the only difference is whether
traceback information is attached. Use `logger.exception()` whenever
you are inside an `except` block and want the traceback preserved
(nearly always the right choice there); use `logger.error()` for
error-level messages that aren't tied to a currently-handled exception
at all.

**Correct usage** — inside `except`, where there genuinely is a
current exception to attach:
```python
try:
    value = int(raw_value)
except ValueError:
    logger.exception("Could not parse %r as an integer", raw_value)
```

**Incorrect usage** — calling `logger.exception()` outside any
`except` block, where there is no current exception:
```python
def check(value):
    if value < 0:
        logger.exception("Value must not be negative")   # WRONG — no active exception here
```
Called this way, `logger.exception()` doesn't fail outright, but the
traceback information it attempts to attach reflects "no exception is
currently being handled" — typically rendering as a confusing
`NoneType: None` in the traceback section of the log output, which is
worse than no traceback at all, since it looks like a real traceback
line at first glance. Use `logger.error(...)` for this case instead —
there is no exception here to attach.

## 8. Logger Hierarchy

Every logger in a Python program is part of a single, shared **name-
based hierarchy**, rooted at one special logger: the **root logger**.

```python
logging.getLogger()          # the root logger
logging.getLogger("app")     # a named logger, a direct child of root
logging.getLogger("app.io")  # a named logger, a child of "app"
```

The hierarchy is determined entirely by **dotted names** — `"app.io"`
is understood as a child of `"app"`, which is itself a child of the
root logger, exactly the way Python packages and modules nest. This is
not a coincidence: the standard, idiomatic pattern is

```python
logger = logging.getLogger(__name__)
```

placed near the top of every module. Since `__name__` is automatically
the module's own dotted import path (e.g. `"myapp.processing.csv"`),
this single line gives every module its own logger, automatically
positioned in the hierarchy exactly matching your package structure —
with **no manual naming required, and no risk of two unrelated modules
accidentally colliding on the same logger name.**

**Propagation** is what connects this hierarchy to actual output: by
default, a `LogRecord` that passes a logger's own level check is
*also* passed up to that logger's parent (and its parent's parent, and
so on, up to the root), and **every handler attached anywhere along
that chain** gets a chance to process it. This is why a real
application commonly configures handlers **only on the root logger**
(via `basicConfig()` or `dictConfig()`, §12) and simply calls
`logging.getLogger(__name__)` everywhere else in its own code — every
module's own logger has no handlers of its own, but its records
propagate up to the root, where the configured handler(s) actually do
something with them.

```python
logger = logging.getLogger("app.io")
logger.propagate  # True by default — records flow up to "app", then to root
```

Setting `logger.propagate = False` stops this — used deliberately when
a specific logger should *not* have its records also handled by
whatever's configured further up the hierarchy (an uncommon, special-
case setting, not something to reach for by default).

## 9. Handlers

A **`Handler`** decides *where* a `LogRecord` that has passed all
level/filter checks actually ends up.

**`StreamHandler`** — writes to a stream, most commonly `sys.stderr`
(its default, connecting directly to §13):
```python
import logging
import sys

handler = logging.StreamHandler(sys.stderr)   # explicit, though this is also the default
handler.setLevel(logging.WARNING)
```

**`FileHandler`** — writes to a specific file on disk, appending by
default:
```python
handler = logging.FileHandler("app.log", encoding="utf-8")
```

**`RotatingFileHandler`** — like `FileHandler`, but automatically
rotates to a new file once the current one reaches a given size (full
treatment in §17):
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler("app.log", maxBytes=10_000_000, backupCount=5, encoding="utf-8")
```

**`TimedRotatingFileHandler`** — like `RotatingFileHandler`, but
rotates on a time interval instead of a size threshold (§17):
```python
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler("app.log", when="midnight", backupCount=14, encoding="utf-8")
```

A single logger can have **multiple handlers attached at once** — a
console handler for immediate visibility and a file handler for
durable storage, simultaneously, from the same logging calls:

```python
logger = logging.getLogger("app")
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler("app.log"))
```

Each handler can have its **own** level and its **own** formatter
(§10) — this is precisely how a program can, for example, show only
`WARNING`-and-above on the console while writing full `DEBUG` detail
to a file, from identical logging calls in the application code.

## 10. Formatters

A **`Formatter`** controls the exact text a `LogRecord` is turned into,
using a template string with named fields:

```python
formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
handler.setFormatter(formatter)
```

```
2026-09-22 14:03:11,502 INFO app.io: Processing data.csv
```

Useful fields, each pulled directly from the `LogRecord`:

| Field | Meaning |
|---|---|
| `%(asctime)s` | Human-readable timestamp of when the record was created |
| `%(levelname)s` | The severity level's name (`"INFO"`, `"ERROR"`, ...) |
| `%(name)s` | The logger's name (typically the module's `__name__`) |
| `%(message)s` | The formatted log message itself |
| `%(filename)s` | The source filename the logging call was made from |
| `%(module)s` | The module name (filename without path/extension) |
| `%(funcName)s` | The function name the logging call was made from |
| `%(lineno)d` | The line number the logging call was made from |
| `%(process)d` | The OS process ID |
| `%(thread)d` | The thread ID |

Why this metadata matters, concretely: when something goes wrong in a
production system running many processes, possibly across many
machines or containers, `%(asctime)s` tells you *when*, `%(name)s` and
`%(filename)s`/`%(funcName)s`/`%(lineno)d` tell you *exactly where in
the code*, and `%(process)d`/`%(thread)d` tell you *which running
instance* — all automatically, from every single logging call, with no
extra work at each call site. This is precisely the "limited metadata"
gap §3 identified in `print()`-based diagnostics, closed completely.

## 11. Filters

A **`Filter`** is a finer-grained gate than level checking alone — a
way to accept or reject `LogRecord`s based on arbitrary custom logic,
attached to either a logger or a handler.

```python
import logging


class OnlyIOModuleFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith("app.io")


handler.addFilter(OnlyIOModuleFilter())
```

A `Filter` subclass implements `filter(record)`, returning `True` to
let the record through and `False` to drop it — the exact same shape
as Python's built-in `filter()` function, applied to `LogRecord`
objects instead of arbitrary values.

Realistic use cases: temporarily restricting a handler to records from
one specific module while debugging; redacting or modifying sensitive
fields on a record before it reaches a formatter (a filter's
`filter()` method can also *mutate* the record before returning
`True`, a common technique for the redaction pattern in §18); or
routing based on some custom attribute attached to specific log calls
(via the `extra=` parameter, briefly touched on in §21). Keep filters
narrow and purpose-built — level-based filtering (§5) already handles
the overwhelming majority of real filtering needs; reach for a custom
`Filter` only when the condition genuinely can't be expressed by level
alone.

## 12. Logging Configuration

**`basicConfig()`** is the quickest way to configure the root logger:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    filename=None,      # None (the default) means log to the console (stderr)
    encoding="utf-8",   # only meaningful when filename= is given
)
```

Key parameters: `level=` sets the root logger's minimum severity;
`format=` sets the formatter template (§10); `filename=` switches the
default handler from console output to a `FileHandler` writing to that
path; `encoding=` sets the text encoding used when writing to a file
(connecting directly to
[05-encodings-and-newlines.md](05-encodings-and-newlines.md) — always
set this explicitly, exactly as with any other file you open).

**The single most common `basicConfig()` mistake: it appears "not to
work."** The documented behavior is that `basicConfig()` **does
nothing if the root logger already has at least one handler attached**
— which can easily have happened already, invisibly, if some earlier
import or library call configured logging first.

```python
import logging

logging.warning("this triggers implicit root configuration")  # implicitly calls basicConfig()!
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")  # too late — silently does nothing
logging.debug("this will NOT appear")
```

Any call to a module-level convenience function (`logging.info(...)`,
`logging.warning(...)`, etc.) **before** your own explicit
`basicConfig()` call will itself trigger an *implicit*, default
`basicConfig()` call internally, the first time it's needed — silently
consuming the one chance `basicConfig()` gets to configure anything.
The fix: call `basicConfig()` **once, as early as possible** in your
program (ideally at the very top of `main()`), before any other
logging call of any kind has a chance to run.

**`logging.config.dictConfig()`** is the structured, production-grade
alternative — configuration expressed entirely as data (a plain
dictionary, easily loaded from JSON or YAML) rather than a sequence of
Python calls:

```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
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
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

`dictConfig()` becomes worth the extra structure once a program has
more than one or two handlers, needs different formats for different
destinations, or benefits from keeping logging setup as external,
inspectable, and (in principle) environment-specific configuration
rather than a hardcoded sequence of Python calls.

## 13. stdout vs. stderr

Directly connecting to
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md):

- **`print()` writes to `sys.stdout` by default.**
- **`logging.StreamHandler()`'s default destination is `sys.stderr`**
  — not stdout — when no stream is explicitly specified.

This is not an arbitrary choice; it directly encodes the exact
separation the previous chapter established: stdout carries a
program's actual, intended output; stderr carries diagnostics. Because
logging output is, by definition, diagnostic, the module's own default
behavior already agrees with that principle before you write a single
line of configuration. (Stderr is the recommended conventional
destination for CLI diagnostics; handlers can be explicitly configured
to use another stream or destination.)

```bash
python app.py > output.txt
```

With this redirection, and logging configured with its default
`StreamHandler` (stderr), **user-facing `print()` output goes into
`output.txt`**, while **log messages still appear on the terminal
screen** — because only stdout was redirected. This is the concrete,
observable payoff of both the previous chapter and this one: a well-
built CLI's actual result can be captured cleanly into a file, or
piped into another program, while its logging output remains visible
(or separately redirectable with `2>`) without interfering at all.

This is exactly why the separation matters for shell pipelines,
scripts, automation, and CI/CD: a script or pipeline consuming
`output.txt` (or another program's stdin, via a pipe) sees *only* the
intended result — never a stray `INFO`-level progress message mixed in
to corrupt it.

## 14. Logging in CLI Applications

Putting §13 into an explicit design rule for every CLI program you
build from here on:

**USER OUTPUT** (→ `print()`, → stdout):
- final results
- output explicitly requested by the user (a report, a summary, the
  requested data itself)
- machine-readable output (JSON, CSV) meant for another program to
  consume

**DIAGNOSTIC OUTPUT** (→ `logging`, → stderr by default):
- `DEBUG` — fine-grained internal detail
- `INFO` — routine progress and status
- `WARNING` — recoverable problems, skipped or suspect data
- `ERROR` — real failures
- traceback information (via `logger.exception()`, §7)

```python
import logging

logger = logging.getLogger(__name__)

def main() -> int:
    logger.info("Starting processing")
    result = process_all_records()
    print(result.summary_json())     # the actual result — stdout
    logger.info("Finished: %d records processed", result.count)  # diagnostic — stderr
    return 0
```

Why this separation is worth defending consistently: a shell pipeline
piping this program's stdout into `jq` or another data tool must never
see an `INFO` line mixed into the JSON; a CI job checking this
program's exit status and parsing its stdout as the actual test result
must never have that parsing broken by a stray log line; and a human
operator debugging a failed production run needs the diagnostic trail
(stderr, or a log file, §17) to actually be there, separate from
whatever data the program produced.

## 15. Exception and Error Logging

Several related but distinct situations, each calling for slightly
different handling:

- **Validation errors** — input that's simply invalid by the program's
  own rules (a missing required field, an out-of-range value). Usually
  a `WARNING` (if the program can skip the bad record and continue) or
  `ERROR` (if it can't).
- **Expected, recoverable errors** — a specific, anticipated failure
  mode the program has explicit handling for (a file not found, a
  malformed row). Log at `WARNING` or `ERROR`, and continue if the
  overall operation can still make progress.
- **Unexpected exceptions** — anything not specifically anticipated.
  Should be logged (via `logger.exception()`, preserving the
  traceback) and then either re-raised or turned into a clean failure
  at the application boundary — never silently discarded.

**Logging vs. raising, logging vs. handling** — a rule worth stating
directly: **log at the point where you have the most context about
what happened; decide whether to continue, retry, or fail at the point
where you know what the *right response* is** — these are not always
the same place in the code. A low-level function might log a warning
and return `None` for a skippable bad record; a higher-level function
decides whether "too many skipped records" should itself become a
program-level failure.

**Duplicate logging** is a real, common mistake: logging the same
exception at multiple levels of a call stack as it propagates.

```python
# BAD — logs the same failure twice as it propagates up
def load_row(row):
    try:
        return parse(row)
    except ValueError:
        logger.exception("Failed to parse row")
        raise                      # re-raised...

def process_file(path):
    for row in read_rows(path):
        try:
            load_row(row)
        except ValueError:
            logger.exception("Failed to parse row")   # ...and logged again here
```

**Correct pattern — log once, at the level that decides what to do
about it:**
```python
def load_row(row):
    return parse(row)   # let ValueError propagate; don't log here

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

**Preserving the traceback and avoiding swallowed exceptions:**
```python
# BAD — the exception disappears entirely; nothing is ever logged
try:
    risky_operation()
except Exception:
    pass

# GOOD — logged with full traceback, then re-raised (or handled deliberately)
try:
    risky_operation()
except Exception:
    logger.exception("risky_operation failed")
    raise
```

A bare `except: pass` (or `except Exception: pass`) is one of the most
damaging patterns a program can contain — it converts a genuine
failure into complete, silent invisibility. If a failure is genuinely
safe to ignore, that decision should itself be visible in the log (at
minimum a `WARNING` explaining what was ignored and why) — "ignored
silently" and "ignored and logged" are very different in what they
leave behind for the next person debugging a production incident.

## 16. Logging File/Data Processing

Realistic logging for the exact kind of file-processing programs this
module has been building throughout — reading files, CSV, JSON:

```python
import csv
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def process_csv(path: Path) -> dict:
    logger.info("Opening %s", path)

    valid = 0
    skipped = 0

    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):  # header is line 1
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


def process_json_lines(path: Path) -> dict:
    valid = 0
    failed = 0
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

Notice the deliberate level choices: **`DEBUG`** for per-row detail
(too verbose for routine use, invaluable while actively investigating
a specific parsing problem); **`WARNING`** for individually skippable,
recoverable problems; **`ERROR`** for a genuinely malformed record the
program cannot make sense of at all; **`INFO`** for the routine,
useful summary a normal production run should always produce. This is
precisely the "progress, record counts, output generation" visibility
§3 identified `print()`-only code as lacking a real mechanism for.

## 17. File Logging and Rotation

`FileHandler` writes log records to a specific file, **appending** by
default (each new run adds to the existing file rather than replacing
it):

```python
import logging

handler = logging.FileHandler("app.log", encoding="utf-8")
```

Points worth being deliberate about: the **file's location** should
generally be a directory your process actually has permission to
write to, and ideally one intended for logs specifically (not mixed in
with application code or data files); **always set `encoding=`
explicitly** (§05's chapter applies here exactly as it does to any
other file your program opens); **append behavior is usually correct**
for a long-running or repeatedly-invoked service, since it preserves
history across runs — but note the direct consequence: a plain
`FileHandler`, left running indefinitely, produces an **unbounded**
log file that will eventually consume all available disk space if
nothing else intervenes.

**`RotatingFileHandler`** solves this with **size-based rotation**:
once the current log file reaches `maxBytes`, it's renamed (e.g.
`app.log` → `app.log.1`) and a fresh, empty `app.log` is started;
`backupCount` limits how many old, rotated files are kept before the
oldest is deleted.

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "app.log",
    maxBytes=10_000_000,   # rotate once this file reaches ~10 MB
    backupCount=5,          # keep at most 5 old rotated files
    encoding="utf-8",
)
```

**`TimedRotatingFileHandler`** rotates on a **time interval** instead
— useful when "one log file per day" (or per hour, per week) is a more
natural retention unit than a fixed size:

```python
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(
    "app.log",
    when="midnight",    # rotate once per day, at midnight
    backupCount=14,      # keep 14 days of history
    encoding="utf-8",
)
```

**Retention** is the general concept both `backupCount` parameters
express: how much log history is worth keeping before it's discarded,
balancing operational usefulness (being able to look back far enough
to diagnose an issue) against disk usage. Choosing size-based versus
time-based rotation, and the specific retention window, is an
application/operations decision, not something the logging module
mandates — a busy service might reasonably rotate hourly and keep only
a few days; a low-volume tool might rotate weekly and keep months.

## 18. Security and Sensitive Data

Logs are frequently persisted, forwarded to other systems, and kept
for far longer than the process that wrote them runs — a direct
extension of
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)'s
§47 security discussion, now applied specifically to a durable,
long-lived logging destination rather than transient stderr output.

Logs must never contain: **passwords**; **API keys and access
tokens**; **secrets** of any kind (encryption keys, signing keys);
**authentication headers** (an `Authorization` header's raw value);
**financial information** (full card numbers, account numbers);
**sensitive personal information** (a full legal name paired with
identifying details, government ID numbers); or **raw sensitive
request/response bodies** that might themselves contain any of the
above.

**Unsafe:**
```python
logger.info("Authenticating user with token %s", auth_token)
logger.debug("Request payload: %s", request_body)   # might contain a password field
```

**Safe:**
```python
logger.info("Authenticating user %s", user_id)   # an identifier, not a secret
logger.debug("Request payload keys: %s", list(request_body.keys()))  # structure, not content
```

**Masking/redaction** — when a value is useful to see *some* of, for
correlation or debugging, but must not be fully exposed:

```python
def mask(value: str, keep: int = 4) -> str:
    if len(value) <= keep:
        return "*" * len(value)
    return "*" * (len(value) - keep) + value[-keep:]

logger.info("Processing card ending in %s", mask(card_number))
# Processing card ending in ************1234
```

A `Filter` (§11) is a reasonable place to apply masking consistently,
across every log call, rather than remembering to call a masking
function manually at every single site where a sensitive value might
appear — the more centralized and automatic the protection, the less
it depends on every future contributor remembering the rule. Filters
can be attached to a logger or to a specific handler; a handler-level
filter is preferable when different destinations need different
representations (e.g. masked on the console, fuller in a protected
file). Note that mutating a shared `LogRecord` affects every
subsequent handler that sees it; where appropriate, a handler filter
can copy the record (or return a replacement) instead of mutating the
shared one.

## 19. Logging Performance

Logging is cheap when done correctly, but two specific habits can make
it genuinely expensive.

**Excessive logs and DEBUG volume** — logging every single record in a
high-throughput pipeline at `INFO` (rather than `DEBUG`), or logging
inside a tight inner loop without regard for volume, can itself become
a meaningful source of slowdown and noise, independent of whether
anyone ever reads those specific lines.

**Expensive message construction** is the more subtle issue:

```python
# WASTEFUL — the f-string (and the expensive_summary() call) run EVERY time,
# even if DEBUG is disabled and this record will be discarded immediately.
logger.debug(f"Full record: {expensive_summary(record)}")
```

```python
# BETTER, BUT NOT ENOUGH — % formatting defers building the final string,
# yet expensive_summary(record) is still called EVERY time (Python evaluates
# arguments before calling logger.debug()).
logger.debug("Full record: %s", expensive_summary(record))
```

```python
# PREFERRED for an expensive argument — skip the computation entirely
# when DEBUG is disabled.
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Full record: %s", expensive_summary(record))
```

This is the concrete reason `logger.debug("User %s processed", user_id)`
(rather than an f-string) is the preferred style throughout production
logging code: passing the message template and its arguments
*separately*, using `%`-style placeholders, lets the logger check
"is this level even enabled?" **first**, and only perform the actual
string formatting (the interpolation) if the record will actually be
used. This defers only the **formatting**, not the evaluation of
argument expressions: a call like `expensive_summary(record)` still
runs before `logger.debug()` is entered, so an expensive argument needs
the `logger.isEnabledFor(...)` guard shown above. An f-string, by
contrast, builds the entire final string *before* `logger.debug()` is
even called — the cost is paid unconditionally, even when `DEBUG` is
disabled and the entire call would otherwise be free.

## 20. Library vs. Application Logging

```python
logger = logging.getLogger(__name__)
```

This single line is used identically in both library code and
application code — but the two have genuinely different
**responsibilities** around what happens *around* it.

**A library's responsibility:** obtain a logger via `getLogger(__name__)`
and use it freely to log — but **never configure logging globally**.
A library should never call `basicConfig()`, never attach handlers to
the root logger, and never set levels on loggers outside its own
namespace. Doing so would silently override or interfere with
whatever the *application* embedding this library has already decided
about its own logging setup — a serious, hard-to-diagnose form of
unwanted global side effect from what looks like an innocuous import.
A well-behaved library, if it wants to guarantee "no warnings if
nothing is configured," attaches a `logging.NullHandler()` to its own
top-level logger — a handler that does nothing at all, existing purely
to silence Python's own "no handlers could be found" fallback warning
without asserting any actual configuration.

```python
# inside a library's __init__.py or top-level module
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
```

**An application's responsibility:** the application — specifically,
its own top-level entry point (`main()`) — should normally be the
place that calls `basicConfig()` or `dictConfig()` (a strong
recommended architecture, not a Python requirement), deciding
levels, formats, and handlers for the entire program, including every
library it imports. This is a direct, deliberate application of §8's
hierarchy and propagation: because every logger, everywhere, is a
descendant of the root logger, configuring the root logger *once*, at
the top level, is sufficient to control output from the application's
own code *and* every well-behaved library it depends on, without
either needing to know about the other's internal logger names.

## 21. Structured Logging

Everything up through §20 has produced **plain-text logs** — human-
readable lines, formatted for a person reading a terminal or a log
file directly. **Structured logs** instead represent each log entry as
a well-defined data structure — commonly JSON — with named fields,
designed to be read by *machines* (log-aggregation and search systems)
as reliably as by humans.

```json
{"timestamp": "2026-09-22T14:03:11Z", "level": "INFO", "event": "file_processed", "file": "transactions.csv", "records": 1200}
```

Compare this to the equivalent plain-text line:
```
2026-09-22 14:03:11 INFO Processed transactions.csv: 1200 records
```

Both convey the same information to a human. The structured version's
advantage shows up at scale: a log-aggregation system ingesting
millions of lines from many processes can reliably filter, search, and
compute metrics on structured **fields** (`"event": "file_processed"`,
`"records": 1200`) — something that requires fragile, error-prone text
parsing (regular expressions against a human-oriented sentence) when
the underlying data is unstructured free text instead.

Python's `logging` module doesn't produce JSON logs natively — but the
concept can be approximated directly with a custom `Formatter` (a full
production system would typically use a small third-party library for
this, which this chapter deliberately does not teach in detail, per
its own scope):

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

The key idea worth taking from this section — independent of any
specific tool — is the **concept**: plain-text logs are optimized for a
human reading one line at a time; structured logs are optimized for a
machine processing millions of lines at once. Production systems at
any real scale generally favor structured logs precisely because log
*volume* eventually makes "a human reads the log file directly"
impractical as the primary consumption method.

## 22. Logging and Observability

**Logs**, **metrics**, and **traces** are the three pillars commonly
referred to together as **observability** — related, but distinct,
tools for understanding a running system's behavior:

| Concept | What it captures | Typical question it answers |
|---|---|---|
| **Logs** | Discrete, timestamped events with context (what this chapter covers) | "What exactly happened, and when, in this specific process?" |
| **Metrics** | Numeric measurements aggregated over time (counters, gauges, histograms) | "How many requests per second? What's the average latency?" |
| **Traces** | The path of a single request or operation as it moves across multiple components/services | "Where, specifically, did this one slow request spend its time?" |

This chapter deliberately stays focused on logs — metrics and
distributed tracing are each substantial topics of their own, well
beyond this module's scope — but knowing where logging fits in this
larger picture matters: logging answers "what happened, specifically,
in this process, at this moment," which is a genuinely different (and
complementary) question from "how is the system performing in
aggregate" (metrics) or "how did this one request travel across many
services" (traces). A mature production system typically has all
three; a CLI tool or small service, built well, often needs only
logging (this chapter) plus the exit-code-based signaling from
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md)
to be genuinely production-ready.

## 23. Common Mistakes

1. **`print()` everywhere, as the only diagnostic mechanism.**
   *Why:* every limitation in §3 applies at once. *Fix:* use `logging`
   for diagnostics; reserve `print()` for actual user-facing output.
2. **Wrong log level chosen.** *Why:* routine detail logged as `ERROR`
   trains people to ignore real errors; genuine failures logged at
   `INFO` get missed entirely. *Fix:* match the level to §5's table
   deliberately, per message.
3. **Too many logs.** *Why:* buries genuinely important messages in
   noise, and costs real performance (§19) at high volume. *Fix:* use
   `DEBUG` for detail, reserve `INFO`-and-above for what a production
   operator actually needs to see routinely.
4. **Too little context.** *Why:* `"error occurred"` with no
   identifying detail is nearly useless when actually debugging a
   production incident. *Fix:* include the specific identifiers
   (`%s`-style, §19) that let a reader connect the log line to a
   specific record, request, or file.
5. **Secrets in logs.** *Why:* §18 — logs are durable and often
   forwarded elsewhere. *Fix:* never log raw secrets; mask or omit
   them entirely.
6. **Duplicate messages.** *Why:* the same event logged from multiple
   handlers or multiple propagating loggers clutters output and can
   double-count in any downstream metric derived from log volume.
   *Fix:* configure handlers once, typically only on the root logger
   (§8, §20), and check `propagate` settings if duplication appears.
7. **Duplicate exception logging.** *Why:* §15 — the same traceback
   logged at multiple layers as it propagates up a call stack. *Fix:*
   log once, at the layer that decides what to do about the failure.
8. **Incorrect `basicConfig()` usage.** *Why:* §12 — called too late,
   after an earlier logging call already triggered an implicit default
   configuration. *Fix:* call `basicConfig()` once, as early as
   possible, before any other logging call.
9. **Root logger misuse.** *Why:* library code configuring or logging
   directly through the root logger can silently interfere with
   whatever the embedding application intended (§20). *Fix:* libraries
   use `getLogger(__name__)` and a `NullHandler`; only the top-level
   application configures the root.
10. **Missing traceback.** *Why:* `logger.error("failed")` inside an
    `except` block, instead of `logger.exception(...)`, discards the
    exact information (§7) needed to actually diagnose the failure.
    *Fix:* use `logger.exception()` inside `except` blocks.
11. **Unbounded log files.** *Why:* a plain `FileHandler`, left
    running indefinitely, can eventually exhaust disk space (§17).
    *Fix:* use `RotatingFileHandler` or `TimedRotatingFileHandler` with
    a deliberate retention policy.
12. **Mixing user output and diagnostics.** *Why:* directly breaks
    pipelines and automation (§13–§14). *Fix:* `print()`/stdout for
    results, `logging` (stderr by default) for diagnostics — consistently.
13. **Swallowing exceptions.** *Why:* §15 — a bare `except: pass`
    (with or without a nearby `print`) makes a real failure
    permanently invisible. *Fix:* log (at minimum) before deciding to
    continue, and re-raise when the failure genuinely can't be handled
    safely at that point.

## 24. Progressive Coding Examples

**1. `print()` basics**
```python
print("Result:", 42)
```

**2. Basic logging**
```python
import logging

logging.basicConfig(level=logging.INFO)
logging.info("Application started")
```

**3. Logging levels in action**
```python
import logging

logging.basicConfig(level=logging.WARNING)
logging.debug("won't appear — below WARNING")
logging.info("won't appear — below WARNING")
logging.warning("will appear")
logging.error("will appear")
```

**4. A named logger**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Using a named logger, not the root logger directly")
```

**5. A custom formatter**
```python
import logging

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

logger = logging.getLogger("app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.info("Formatted output")
```

**6. `StreamHandler` explicitly targeting stderr**
```python
import logging
import sys

handler = logging.StreamHandler(sys.stderr)
logger = logging.getLogger("app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.info("This goes to stderr, not stdout")
```

**7. `FileHandler`**
```python
import logging

handler = logging.FileHandler("app.log", encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))

logger = logging.getLogger("app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.info("Written to app.log")
```

**8. Exception logging**
```python
import logging

logger = logging.getLogger(__name__)

try:
    1 / 0
except ZeroDivisionError:
    logger.exception("Division failed")
```

**9. Multiple handlers, different levels**
```python
import logging

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.WARNING)

file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

logger.addHandler(console)
logger.addHandler(file_handler)

logger.debug("only in the file")
logger.warning("in both the console and the file")
```

**10. CLI stdout/stderr separation**
```python
import logging
import sys

logger = logging.getLogger(__name__)

def main() -> int:
    logger.info("Starting")
    print("42")            # the actual result — stdout
    logger.info("Done")    # diagnostic — stderr, by default
    return 0

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(main())
```

**11. A small file-processing program with logging**
```python
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def count_lines(path: Path) -> int:
    logger.info("Reading %s", path)
    with path.open("r", encoding="utf-8") as handle:
        count = sum(1 for _ in handle)
    logger.info("Read %d lines from %s", count, path)
    return count
```

**12. Log rotation**
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler("app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
logger = logging.getLogger("app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**13. Configurable logging via `dictConfig()`**
```python
import logging.config

logging.config.dictConfig({
    "version": 1,
    "formatters": {"default": {"format": "%(asctime)s %(levelname)s: %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default"}},
    "root": {"level": "INFO", "handlers": ["console"]},
})
```

**14. Structured-log-style output**
```python
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        })

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.info("file_processed file=%s records=%d", "data.csv", 1200)
```

## 25. Mini Project — Production-Style File Processing CLI with Logging

**Problem:** build `process_records.py`, a CLI that reads a JSON Lines
file of records, validates each one, produces a clean summary as its
actual output, and reports every diagnostic — progress, warnings,
errors — through logging, with a configurable verbosity level, correct
exit codes, no secrets ever logged, and file logging alongside console
output.

**Architecture:**
```
build_parser()        — argparse: input path, --log-level, --log-file
        ↓
configure_logging()    — one call, at the very top of main(), using dictConfig
        ↓
validate_record()       — pure function, no logging inside it at all
        ↓
process_file()           — business logic; logs progress/warnings via logger
        ↓
main(argv)                 — wires it together; print()s the final summary;
                              returns the exit code
```

**Data flow:** JSON Lines file → `process_file()` reads and validates
each record → valid/invalid counts accumulate → a summary dict is
built → `main()` prints that summary (stdout, the actual result) →
returns `0` (all valid) or `3` (some records invalid), per the
exit-code convention established in
[07-standard-streams-and-exit-codes.md](07-standard-streams-and-exit-codes.md).

**Logging flow:** every processed record that fails validation
produces one `WARNING`, on the logger, at `stderr` (console) *and* in
the configured log file; overall start/finish produces `INFO`; a line
that isn't valid JSON, or is valid JSON but not an object, is expected
invalid input and produces one `WARNING` (no traceback). Reserve
`logger.exception()` for genuinely unexpected exceptions, which
preserves their traceback in the log file without it ever touching
stdout.

**Implementation:**
```python
"""process_records.py — validate a JSON Lines file, with production-style logging."""
from __future__ import annotations

import argparse
import json
import logging
import logging.config
from collections.abc import Sequence
from pathlib import Path

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a JSON Lines file of records.")
    parser.add_argument("input_file", type=Path, help="Path to the JSON Lines input file")
    parser.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Console/file logging verbosity (default: INFO)",
    )
    parser.add_argument(
        "--log-file", type=Path, default=Path("process_records.log"),
        help="Path to the log file (default: process_records.log)",
    )
    return parser


def configure_logging(level: str, log_file: Path) -> None:
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
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
        "root": {"level": "DEBUG", "handlers": ["console", "file"]},
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

            logger.debug("Line %d: parsed record with keys %s", line_number, list(record.keys()))

            errors = validate_record(record)
            if errors:
                logger.warning("Line %d: invalid record (%s)", line_number, "; ".join(errors))
                invalid += 1
                continue

            valid += 1

    logger.info("Finished processing %s: %d valid, %d invalid", path, valid, invalid)
    return {"valid": valid, "invalid": invalid}


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure_logging(args.log_level, args.log_file)

    if not args.input_file.is_file():
        logger.error("Input file not found: %s", args.input_file)
        return 2

    summary = process_file(args.input_file)
    print(json.dumps(summary))   # the actual result — stdout, clean, machine-readable

    return 0 if summary["invalid"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
```

**Testing strategy:**
```python
import json
import logging

from process_records import main, process_file, validate_record


def test_validate_record():
    assert validate_record({"id": 1, "value": "x"}) == []
    assert validate_record({}) == ["missing 'id'", "missing 'value'"]


def test_all_valid_records(tmp_path, capsys):
    input_file = tmp_path / "data.jsonl"
    input_file.write_text('{"id": 1, "value": "a"}\n', encoding="utf-8")
    log_file = tmp_path / "app.log"

    status = main([str(input_file), "--log-file", str(log_file)])
    captured = capsys.readouterr()

    assert status == 0
    assert json.loads(captured.out.strip()) == {"valid": 1, "invalid": 0}
    assert log_file.exists()


def test_invalid_record_logged_as_warning(tmp_path, caplog):
    input_file = tmp_path / "data.jsonl"
    input_file.write_text('{"id": 1}\n', encoding="utf-8")

    # Test process_file() directly: main() calls dictConfig(), which can
    # replace the handlers pytest's caplog fixture relies on.
    with caplog.at_level(logging.WARNING):
        summary = process_file(input_file)

    assert summary == {"valid": 0, "invalid": 1}
    assert any("invalid record" in record.message for record in caplog.records)
```

(`caplog` is pytest's built-in fixture for asserting on logging output
directly — the logging-specific counterpart to `capsys` for stdout/
stderr text.)

**Debugging scenarios:** if the log file never appears, check whether
`configure_logging()` is actually being called before `process_file()`
logs anything (§12's "called too late" pitfall, applied to
`dictConfig()` too — configuration must happen before any logging call
it's meant to affect); if `DEBUG`-level per-record detail is missing
from the console but expected, check `--log-level` was passed as
`DEBUG` explicitly, since `INFO` is the default; if a malformed
line is unexpectedly absent from the log, check that the
`json.JSONDecodeError` branch's `logger.warning()` call is reached and
that the handler's level allows `WARNING`.

**Production improvements worth naming:** structured (JSON) log output
for easier aggregation (§21); a `--fail-fast` flag; a maximum-
invalid-percentage threshold before treating the whole run as failed
outright; and moving `configure_logging()`'s dictionary into an
external, environment-specific configuration file rather than a
hardcoded literal.

## 26. Exercises + Answer Key

**Beginner**

1. Write a script using `print()` for its result and explain, in a
   comment, why `print()` is the right choice there.
2. Write a script that logs one message at each of the five standard
   levels, with `basicConfig(level=logging.DEBUG)`, and predict which
   ones will appear before running it.
3. Create a named logger with `logging.getLogger(__name__)` and use it
   to log an `INFO` message.

**Intermediate**

4. Attach a `StreamHandler` and a `FileHandler` to the same logger,
   each with a different level, and verify (by inspecting both the
   console and the file) that each destination receives only what its
   level permits.
5. Write a `Formatter` that includes `%(asctime)s`, `%(levelname)s`,
   and `%(filename)s`, and explain what each field would show for one
   specific logging call.
6. Trigger an exception inside a `try`/`except` block and log it with
   `logger.exception()`; inspect the output and confirm the traceback
   is present.
7. Write a small program that prints its result to stdout and logs a
   diagnostic to stderr (via the default `StreamHandler`), then verify
   with `python app.py > out.txt` that only the result ends up in
   `out.txt`.
8. Configure a `FileHandler` writing to a specific path, and verify the
   file's contents after running the program twice (confirming append
   behavior).

**Advanced**

9. Configure a logger with both a console handler (`WARNING` and
   above) and a `RotatingFileHandler` (`DEBUG` and above, small
   `maxBytes` for easy testing), and demonstrate rotation actually
   occurring by writing enough log lines to exceed the size limit.
10. Build a `logging.config.dictConfig()` dictionary from scratch that
    reproduces exercise 9's setup declaratively.
11. Write a custom `Filter` that redacts a specific field's value
    before it reaches the formatter, and demonstrate it with a log
    call that includes that field.
12. Design (in comments or a short written explanation, not
    necessarily full code) the logging strategy for a production CLI
    that processes sensitive customer records — specifically, what
    would and would not be safe to log at each level.

**Answer key**

1. `print()` is correct whenever the value is the actual, requested
   result of the program — e.g. `print(total)` at the end of a
   calculation the user asked for — not a diagnostic about how the
   program got there (§2).
2. With `level=logging.DEBUG`, **all five** appear, since `DEBUG` is
   the lowest standard level and nothing is filtered out (§5).
3. `logging.getLogger(__name__)` returns a logger named after the
   current module, positioned correctly in the hierarchy (§8);
   `.info("...")` produces an `INFO`-level record, visible if the
   root logger's effective level allows it.
4. The console handler shows only records at or above its own level;
   the file receives everything at or above *its* level — demonstrating
   that a single set of logging calls can be filtered independently at
   each destination (§9).
5. `%(asctime)s` shows the timestamp of that specific call;
   `%(levelname)s` shows `"INFO"`, `"WARNING"`, etc.; `%(filename)s`
   shows the source file the call was made from — each pulled directly
   from the `LogRecord` (§10).
6. `logger.exception()` should show the log message followed by a full
   Python traceback ending in the actual exception type and message —
   present because it was called from inside the `except` block where
   `sys.exc_info()` had a real exception to report (§7).
7. Because `print()` targets stdout and `StreamHandler()`'s default
   target is stderr, redirecting only stdout (`> out.txt`) leaves the
   log output visible on the terminal, separate from the captured
   result file (§13).
8. Running the program twice should result in a file containing *both*
   runs' log output, one after another — `FileHandler`'s default mode
   appends rather than overwriting (§17).
9. After enough log lines exceed `maxBytes`, the original log file
   should be renamed (e.g. to `app.log.1`) and a new, empty `app.log`
   should start receiving further records — direct, observable
   evidence of size-based rotation (§17).
10. The dictionary should mirror exercise 9's handlers, formatters, and
    levels as data — `"class": "logging.handlers.RotatingFileHandler"`
    with matching `maxBytes`/`backupCount`, and a console handler with
    `"class": "logging.StreamHandler"` and `"level": "WARNING"` (§12).
11. A `Filter` subclass's `filter(record)` method can modify
    `record.msg` (or a specific `args` value) before returning `True`,
    replacing a sensitive value with a masked version consistently,
    for every record that passes through it (§11, §18).
12. `DEBUG`/`INFO` should log identifiers and counts, never raw
    sensitive field values; `WARNING`/`ERROR` should describe *what
    kind* of problem occurred (e.g., "validation failed for record")
    without echoing the sensitive payload itself; any genuinely
    necessary detail for debugging should be masked (§18) rather than
    logged raw.

## 27. Debugging Lab

**1. `basicConfig()` does not work**
```python
logging.info("triggers an implicit default config")
logging.basicConfig(level=logging.DEBUG)
logging.debug("never appears")
```
*Diagnosis:* the first call to `logging.info()` implicitly configured
the root logger with its own default settings before your explicit
`basicConfig()` call ran — and `basicConfig()` does nothing if the
root logger already has a handler (§12). *Fix:* call
`basicConfig()` first, before any other logging call.

**2. Duplicate logs**
```python
logger = logging.getLogger("app")
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.StreamHandler())
logger.info("this appears twice")
```
*Diagnosis:* two identical `StreamHandler` instances were both added
to the same logger — every handler attached processes every record
independently. *Fix:* add each handler exactly once; if this code runs
more than once (e.g. `configure_logging()` called twice), guard
against re-adding handlers, or clear existing handlers first.

**3. Logs on an unexpected stream**
A log message expected on the console instead ends up mixed into a
file that's supposed to contain only `print()`-based program output.
*Diagnosis:* check whether a `StreamHandler` was explicitly constructed
with `sys.stdout` instead of leaving it at its stderr default, or
whether `print()` itself was accidentally given `file=sys.stderr`
somewhere. *Fix:* keep `StreamHandler()` at its default (stderr) unless
there's a specific, deliberate reason to change it (§13).

**4. Missing traceback**
```python
try:
    risky()
except Exception:
    logger.error("risky() failed")
```
*Diagnosis:* `logger.error()` was used instead of `logger.exception()`
— the message is logged, but no traceback is attached (§7). *Fix:*
`logger.exception("risky() failed")`.

**5. Log file not created**
*Diagnosis checklist:* is `configure_logging()` (or the equivalent
`FileHandler`/`dictConfig()` setup) actually being called before any
logging happens? Does the process have write permission to the target
directory? Is the path relative to a working directory different from
what you expect (§07's chapter covered exactly this "relative to the
current working directory, not the script" subtlety for `Path`
arguments)?

**6. `DEBUG` messages missing**
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

for handler in logging.getLogger().handlers:
    handler.setLevel(logging.INFO)

logger.debug("still doesn't appear")
```
*Diagnosis:* the **logger's** level is `DEBUG`, so the record is
created and passed on, but the root logger's *handler* has level
`INFO` and rejects it. Logger-level and handler-level filtering are
separate: a record must pass the relevant logger's level and then the
destination handler's own level to be emitted (§5, §9). (With plain
`basicConfig(level=logging.INFO)` alone, the handler's level is
`NOTSET`, so the child logger's `DEBUG` record would be emitted — the
handler level must have been set explicitly.)

**7. Excessive logging**
A production log file grows enormous within minutes. *Diagnosis:*
check whether `DEBUG`-level logging (or a per-record `INFO` call in a
high-volume loop) is enabled in production by mistake (§19, §23).
*Fix:* set production's default level to `INFO` or `WARNING`; reserve
`DEBUG` for deliberate, temporary diagnosis.

**8. Wrong severity**
A genuine failure was logged at `INFO` and missed entirely by an
alerting system watching for `ERROR`-and-above. *Diagnosis:* re-check
§5's table against what actually happened — did the program continue
normally (arguably `WARNING`), or did an operation genuinely fail
(`ERROR`)? *Fix:* choose the level based on actual severity, not
habit.

**9. Duplicate handlers from repeated configuration**
```python
def configure_logging():
    logger = logging.getLogger("app")
    logger.addHandler(logging.StreamHandler())
    return logger

configure_logging()
configure_logging()   # called again — e.g. from a test, or a re-imported module
```
*Diagnosis:* calling a handler-adding configuration function more than
once (common in tests, or with module re-execution) accumulates
handlers, each duplicating every subsequent log line. *Fix:* check
`logger.handlers` before adding (`if not logger.handlers: ...`), or
explicitly clear (`logger.handlers.clear()`) before reconfiguring.

## 28. Interview + Architecture Questions

1. What is the fundamental difference between `print()` and Python's
   `logging` module?
2. When is `print()` still the correct choice, even in a well-designed
   production program?
3. Why does `StreamHandler()` default to stderr rather than stdout?
4. What is a `Logger`? What is a `LogRecord`? What is the relationship
   between them?
5. What is a `Handler`, and how does it differ from a `Formatter`?
6. What does a `Filter` do that level-based filtering alone cannot?
7. What is the root logger, and why does it matter even if you never
   call `logging.getLogger()` with no arguments yourself?
8. Explain logger hierarchy and propagation, using `"app.io"` as an
   example child of `"app"`.
9. Name the five standard logging levels, in order, and give a
   realistic example use for each.
10. What is `logging.exception()`, and how does it differ from
    `logger.error()`?
11. Why should `logger.exception()` only be called inside an `except`
    block?
12. How does file logging work, and what's the risk of a plain
    `FileHandler` left running indefinitely?
13. What's the difference between `RotatingFileHandler` and
    `TimedRotatingFileHandler`?
14. In a production system, why must logs never contain secrets or raw
    sensitive data?
15. Why is `logger.debug("User %s", user_id)` preferred over an
    f-string for the same message?
16. What is the difference in responsibility between a library's
    logging setup and an application's logging setup?
17. Why should a library never call `basicConfig()` itself?
18. What is structured logging, and why does it matter for log
    aggregation at scale?
19. Where does logging fit relative to metrics and traces in
    observability?
20. Design the logging strategy for a CLI tool that's part of a larger
    automated data pipeline — what goes to stdout, what goes through
    logging, and why?

**Answer key**

1. `print()` is an unconditional, unstructured way to write text to a
   stream; `logging` is a structured, filterable, configurable
   diagnostic system with severity levels, metadata, and pluggable
   destinations (§1–§4).
2. Whenever the value being written is the program's actual,
   user-requested output rather than a diagnostic about the program's
   own behavior (§2).
3. Because logging output is diagnostic by nature, and stderr is the
   conventional destination for diagnostics — keeping it separate from
   whatever a program's actual stdout output might be (§13).
4. A `Logger` is the object application code calls to emit log
   messages; a `LogRecord` is the structured object automatically
   created, once per call that passes the logger's level check,
   carrying the message plus metadata (§4).
5. A `Handler` decides *where* a record goes (console, file, ...); a
   `Formatter` decides what the resulting text actually *looks like*
   (§9–§10).
6. Arbitrary custom logic beyond a simple severity threshold — e.g.
   restricting output to records from one specific module, or
   redacting specific fields (§11).
7. It's the top-level ancestor every other logger ultimately
   propagates records up to; configuring it (via `basicConfig()` or
   `dictConfig()`) is typically sufficient to control output for an
   entire application, including well-behaved library code, without
   needing to configure every individual logger by name (§8, §20).
8. `"app.io"` is treated as a child of `"app"` purely by its dotted
   name; a record logged through `"app.io"` that passes its own level
   check also propagates up to `"app"`'s handlers, then to root's,
   unless propagation is explicitly disabled (§8).
9. `DEBUG` (fine detail), `INFO` (routine status), `WARNING`
   (recoverable problem), `ERROR` (real failure), `CRITICAL` (severe,
   possibly program-ending failure) — with examples per §5's table.
10. Both log at `ERROR` severity; `logger.exception()` additionally
    attaches the currently-handled exception's full traceback, while
    `logger.error()` logs only the message (§7).
11. Because it relies on there being a currently-handled exception
    (via `sys.exc_info()`) to attach; called outside an `except` block,
    there is no such exception, and the resulting output is confusing
    rather than useful (§7).
12. `FileHandler` appends log records to a specific file on disk; left
    running indefinitely with no rotation, that file grows without
    bound and can eventually exhaust available disk space (§17).
13. `RotatingFileHandler` rotates based on file size (`maxBytes`);
    `TimedRotatingFileHandler` rotates based on a time interval
    (`when=`) — the right choice depends on whether size or time is the
    more natural retention unit for a given system (§17).
14. Because logs are commonly persisted, forwarded, and retained far
    longer than the process that produced them, and are frequently
    accessible to more people/systems than the original process's
    memory ever was — a secret logged once can leak indefinitely
    afterward (§18).
15. Because `%`-style lazy formatting only builds the final string if
    the logger actually decides to emit the record; an f-string is
    evaluated unconditionally by Python before the logging call even
    happens, paying the formatting cost even when the message will be
    discarded (§19).
16. A library should log freely through its own `getLogger(__name__)`
    logger but never configure logging globally; an application's
    top-level entry point is the one place that decides levels,
    formats, and handlers for the whole program (§20).
17. Because doing so would silently override or interfere with
    whatever the embedding application has already configured for its
    own logging — an unwanted, hard-to-diagnose global side effect from
    importing a library (§20).
18. Structured logging represents each log entry as machine-parseable
    data (commonly JSON) with named fields rather than a human-oriented
    sentence, making reliable filtering, search, and aggregation across
    millions of log lines from many processes practical, where parsing
    free text would be fragile (§21).
19. Logs describe discrete events with context; metrics describe
    aggregated numeric measurements over time; traces describe a single
    operation's path across components — complementary tools answering
    different questions, together making up "observability" (§22).
20. stdout carries the tool's actual, machine-readable output (so the
    next pipeline stage can consume it cleanly); all progress,
    warnings, and errors go through `logging` (stderr by default, and
    ideally also a durable log file); the exit code reflects overall
    success/failure for the orchestrator to act on — directly combining
    this chapter with
    [06](06-command-line-arguments-with-argparse.md) and
    [07](07-standard-streams-and-exit-codes.md) (§14, §51 of the
    previous chapter).

## 29. Knowledge Check

**Conceptual**
1. In your own words, what specific capability does `logging` have
   that `print()` fundamentally lacks?
2. Why is "log once, at the level that decides what to do" a better
   rule than "log at every layer that sees the exception"?

**Code-reading**
3. What will this print/log, given `basicConfig(level=logging.INFO)`?
```python
logger = logging.getLogger("app")
logger.setLevel(logging.WARNING)
logger.info("info message")
logger.warning("warning message")
```
4. What is wrong with this snippet, specifically?
```python
logger.debug(f"Processing record {expensive_repr(record)}")
```

**Debugging**
5. A `RotatingFileHandler` was configured with `maxBytes=10_000_000`,
   but the log file has grown to 500 MB with no rotation ever having
   occurred. Name two things you'd check first.
6. `logger.exception()` was called, but the resulting log entry shows
   `NoneType: None` where a traceback was expected. What's the likely
   cause?

**Scenario-based**
7. A production CLI's stdout, meant to carry a clean JSON summary, is
   occasionally corrupted by a stray line of text. What's the most
   likely design flaw, and how would you fix it?
8. A library your application depends on is printing warnings directly
   to the console that you can't seem to configure or suppress. What
   design mistake is the library likely making?

**Design**
9. Design the logging level scheme (which events get which level) for
   a CLI that ingests a batch of files, validates each one, and
   uploads valid files to storage.

---

**Answer key**

1. Severity levels with real, built-in filtering — the ability to say
   "only show me WARNING and above" without editing or removing
   individual calls (§3, §5).
2. Logging at every layer produces duplicate entries for the exact same
   underlying failure as it propagates up a call stack, cluttering
   output; logging once, where the decision about how to respond is
   actually made, keeps one clear record per real event (§15, §23).
3. Only `"warning message"` appears — `logger`'s own level is
   `WARNING`, which filters out the `INFO` call regardless of what the
   root's `basicConfig()` level was set to; a logger's own level always
   applies first (§5, §8).
4. The f-string is evaluated (including the `expensive_repr(record)`
   call) unconditionally, every single time this line executes — even
   when `DEBUG` is disabled and the record will be discarded
   immediately. Should be
   `logger.debug("Processing record %s", expensive_repr(record))`
   instead (§19).
5. Whether the handler was actually attached to the logger doing the
   writing (a duplicate, unconfigured logger/handler elsewhere could be
   writing to the same file directly); and whether `maxBytes` was
   actually passed correctly, or whether the file being inspected is a
   *different* file than the one the handler is configured to write to
   (§17, §27).
6. `logger.exception()` was called outside of an `except` block (or
   after the exception context had already ended), so there was no
   current exception for `sys.exc_info()` to report (§7).
7. Almost certainly a stray `print()` call (or a misdirected log
   handler pointed at stdout) mixed into what should be exclusively
   the JSON-producing output path — the fix is auditing every write to
   stdout and ensuring diagnostics exclusively go through `logging`
   (default stderr) instead (§13–§14, §23).
8. The library is very likely calling `print()` directly, or
   configuring/using the root logger/its own handlers directly, rather
   than obtaining its own `getLogger(__name__)` logger and leaving
   configuration entirely to the embedding application (§20).
9. A reasonable scheme: `DEBUG` for per-file internal parsing detail;
   `INFO` for "started/finished processing file X," "uploaded file X";
   `WARNING` for a file that failed validation but was skipped without
   stopping the batch; `ERROR` for a file that should have uploaded but
   the upload itself failed; `CRITICAL` reserved for something
   threatening the whole batch run (e.g. the storage service being
   entirely unreachable) — matching §5's table to this specific
   pipeline's actual failure modes.

## 30. Production Checklist

**Log levels**
- [ ] Every logging call uses a level matching its actual severity
      (§5), not habit or convenience.
- [ ] Production defaults to `INFO` or `WARNING`, with `DEBUG`
      available on demand via configuration, never hardcoded on by
      default.

**Context**
- [ ] Log messages include enough identifying detail (IDs, filenames,
      counts) to actually diagnose an issue from the log alone.
- [ ] Lazy `%`-style formatting is used, not eager f-strings, for
      anything beyond trivially cheap messages (§19).

**stdout/stderr separation**
- [ ] User-facing/machine-readable output goes through `print()` to
      stdout only.
- [ ] All diagnostics go through `logging` (stderr by default), never
      mixed into stdout (§13–§14).

**Traceback preservation**
- [ ] Every `except` block that logs an exception uses
      `logger.exception()`, not `logger.error()`, unless there's a
      specific reason to omit the traceback.
- [ ] No bare `except: pass` (or equivalent) silently swallows a
      failure with no log trace at all (§15, §23).

**Secret protection**
- [ ] No passwords, API keys, tokens, or other secrets ever appear in
      any log message, at any level (§18).
- [ ] Sensitive fields that are useful to partially see are masked
      consistently, ideally via a shared filter or utility (§11, §18).

**Rotation/retention**
- [ ] File logging uses `RotatingFileHandler` or
      `TimedRotatingFileHandler`, not a plain, unbounded `FileHandler`,
      for anything long-running (§17).
- [ ] Retention (`backupCount`, or the rotation interval) is a
      deliberate choice, balancing disk usage against operational
      history needs.

**Configurable logging**
- [ ] Logging level, format, and destinations can be changed via
      configuration (ideally `dictConfig()`, or at minimum CLI flags),
      without editing and redeploying code (§12).
- [ ] `basicConfig()` (or `dictConfig()`) is called exactly once, as
      early as possible, before any other logging call (§12, §27).

**Controlled log volume**
- [ ] High-frequency inner loops don't log at `INFO` or above by
      default; `DEBUG` is reserved for genuinely fine-grained detail
      (§19, §23).

**Library/application separation**
- [ ] Library code uses `getLogger(__name__)` and, ideally, a
      `NullHandler`; it never calls `basicConfig()`/`dictConfig()` or
      configures the root logger itself (§20).
- [ ] Exactly one place in the application — its top-level entry
      point — owns all logging configuration.

**Structured logs where appropriate**
- [ ] For systems at meaningful scale, log output is structured
      (e.g. JSON) rather than purely free-text, to support reliable
      aggregation and search (§21).

**Operational usefulness**
- [ ] A production operator, reading only the logs (no source code
      access), can reconstruct what happened during a specific run —
      what started, what was skipped, what failed, and why (§16,
      §22, §25).
