# Safe and Useful Logging in Python

> **Stage 1 — Programming & Computational Thinking → 10 — Production Habits for Python Programs**
>
> This chapter is a production-oriented foundation for learning Python logging safely and effectively.

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain why production applications need logging;
- explain the difference between `print()` and logging;
- create and use named loggers;
- understand the standard log levels;
- understand the relationship among `Logger`, `LogRecord`, `Handler`, `Formatter`, and `Filter`;
- configure simple logging with `basicConfig()`;
- understand logger hierarchy and propagation;
- log exceptions with useful traceback information;
- use lazy logging formatting correctly;
- include useful operational context without exposing sensitive information;
- recognize secrets and sensitive data that should not be logged;
- understand structured and machine-readable logging conceptually;
- configure logging at the application boundary;
- use logging safely in CLI programs, data pipelines, and Applied AI systems;
- design useful retry and failure logs;
- avoid noisy or duplicated logs;
- test important logging behavior;
- debug production problems using logs;
- design a small production-oriented Python logging architecture;
- reason about security, observability, maintainability, and operational usefulness.

### The learning loop

Use the same engineering loop throughout this chapter:

```text
Understand
    ↓
Predict
    ↓
Implement
    ↓
Test normal case
    ↓
Test edge cases
    ↓
Debug
    ↓
Refactor
    ↓
Document
    ↓
Explain aloud
```

### The central question

Imagine this:

> Your Python application is running on a server. Nobody is watching the process directly. How will you know what happened?

Logging is one answer.

---

## 2. Why Logging Exists

A running program produces events.

For example:

```text
application started
configuration loaded
job started
record validation failed
external request timed out
retry started
job completed
```

Without an operational record of those events, diagnosing a production problem becomes much harder.

### A simple example

Suppose we have:

```python
def process_order(order):
    ...
```

After the program runs, someone asks:

- What happened?
- Which order was processed?
- When did processing start?
- Did validation fail?
- Which step failed?
- Was an external service called?
- How long did the operation take?
- Did the application retry?
- Why did the request fail?

The source code alone cannot answer all of those questions after the fact.

### Why this matters in production

A production process can:

```text
run without a terminal
run for hours or days
serve many users
process thousands of records
call external services
fail intermittently
restart
run concurrently
```

Logging provides operational evidence about what the program was doing.

### Logging is not a database

A log is usually an operational record intended for diagnosis, monitoring, or understanding runtime behavior.

It is not automatically:

```text
source of truth
business database
audit system
event store
transaction ledger
```

Those systems have different requirements.

### A useful distinction

```text
Business data
    = information the application must preserve

Logs
    = operational evidence about what the application did
```

That distinction becomes important later when we discuss safe logging.

---

## 3. What Is Logging?

### Simple explanation

Logging is the practice of recording useful events that happen while software runs.

### Technical explanation

Python's `logging` package provides a structured mechanism for creating log records, applying severity and filtering rules, formatting those records, and sending them through handlers to destinations.

The main building blocks are:

```text
Logger
  ↓
LogRecord
  ↓
Filtering / propagation
  ↓
Handler
  ↓
Formatter
  ↓
Destination
```

### A log event

A useful log event normally has:

```text
when
what happened
where it happened
severity
relevant context
```

For example:

```text
2026-09-24 10:15:32 INFO app.worker job_started job_id=42
```

This is more useful than:

```text
started
```

because it contains context.

### What makes a log useful?

A useful log should be:

- meaningful;
- appropriately leveled;
- understandable;
- contextual;
- safe;
- searchable;
- actionable.

---

## 4. Logging vs `print()`

`print()` and logging both produce output, but their goals are different.

### `print()`

This can be appropriate for:

- a simple CLI's intended user-facing result;
- a quick experiment;
- a temporary debugging session.

Example:

```python
print("Hello, user")
```

That may be exactly what a CLI application should display to the person running it.

### Logging

Logging is more appropriate for operational diagnostics:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Application started")
```

### Comparison

| Concern | `print()` | Logging |
|---|---|---|
| Severity | No built-in levels | `DEBUG` through `CRITICAL` |
| Timestamp | Manual | Available through log records/formatting |
| Logger identity | No | Yes |
| Filtering | Manual | Built in |
| Destinations | Usually explicit output stream | Handlers can target destinations |
| Configuration | Manual | Central logging configuration |
| Exceptions | Manual | `logger.exception()` |
| Hierarchy | No | Yes |
| Production operations | Limited | Designed for it |
| Structured context | Manual | Extensible |

### Bad operational pattern

```python
print("User failed")
```

The message does not tell us:

```text
which user
what operation
severity
component
request/job context
exception details
```

### Better

```python
logger.warning("User validation failed user_id=%s", user_id)
```

This gives an operator more context.

### `print()` is not forbidden

Do not turn this into a dogma.

A CLI may intentionally use:

```python
print("Report generated successfully")
```

as user-facing output.

A useful separation is:

```text
User-facing result
    → CLI output

Operational diagnostics
    → logging
```

---

## 5. The Python `logging` Module

Python provides the `logging` module in the standard library.

Start with:

```python
import logging
```

The most important concepts for this chapter are:

```text
logging
├── Logger
├── LogRecord
├── Handler
├── Formatter
└── Filter
```

### Major entry points

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("debug event")
logger.info("information event")
logger.warning("warning event")
logger.error("error event")
logger.critical("critical event")
```

Inside exception handling:

```python
try:
    int("not-a-number")
except ValueError:
    logger.exception("Parsing failed")
```

### Related functions

The module-level convenience functions also exist:

```python
logging.debug("debug event")
logging.info("information event")
logging.warning("warning event")
logging.error("error event")
logging.critical("critical event")
```

For application code, a named logger is usually the clearer pattern:

```python
logger = logging.getLogger(__name__)
```

### Related classes

You should understand these roles:

```text
Logger
    creates/dispatches log events

LogRecord
    carries event information

Handler
    sends records toward a destination

Formatter
    defines rendered output

Filter
    applies additional filtering rules
```

---

## 6. First Logging Program

Here is the smallest useful example:

```python
import logging

logging.basicConfig(level=logging.INFO)

logging.info("Application started")
logging.warning("Configuration is incomplete")
logging.error("Operation failed")
```

### What happens?

`basicConfig(level=logging.INFO)` establishes basic logging configuration.

The threshold is `INFO`.

Therefore:

```text
DEBUG    → below threshold
INFO     → emitted
WARNING  → emitted
ERROR    → emitted
CRITICAL → emitted
```

### A named logger example

```python
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

logger.debug("Detailed diagnostic information")
logger.info("Application started")
logger.warning("Configuration is incomplete")
logger.error("Operation failed")
```

`DEBUG` normally does not appear because the configured threshold is `INFO`.

### Default behavior

If no logging configuration is explicitly established, the logging package has default behavior for simple module-level logging calls, and the default effective threshold is `WARNING`.

Do not rely on default behavior for an application's production logging policy.

Configure logging intentionally.

### Expected shape of output

A simple default configuration commonly produces output similar to:

```text
INFO:__main__:Application started
WARNING:__main__:Configuration is incomplete
ERROR:__main__:Operation failed
```

Exact output can vary with configuration and execution environment.

---

## 7. Log Levels

Python's standard levels are:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

They increase in severity.

### `DEBUG`

Detailed information useful when diagnosing a problem.

Examples:

```python
logger.debug("Parsed %d records", record_count)
```

```python
logger.debug("Using model=%s", model_name)
```

Be careful with debug data: `DEBUG` does not mean "safe to expose."

### `INFO`

Normal application events that are useful operationally.

```python
logger.info("Job started job_id=%s", job_id)
```

Good candidates include:

```text
startup
shutdown
job start
job completion
important lifecycle transitions
major configuration state
```

### `WARNING`

Something unexpected happened, but the system can continue.

```python
logger.warning(
    "Request timed out; retrying attempt=%d",
    attempt,
)
```

### `ERROR`

An operation failed.

```python
logger.error(
    "Failed to write output path=%s",
    output_path,
)
```

An `ERROR` should generally represent an actual failure or inability to perform an intended operation.

### `CRITICAL`

A severe condition indicating that the application or a major capability may be unable to continue.

```python
logger.critical(
    "Application initialization failed"
)
```

Do not use `CRITICAL` merely because a message sounds dramatic.

### Level table

| Level | Simple meaning | Typical example | Poor use |
|---|---|---|---|
| `DEBUG` | Detailed diagnostic evidence | Parsed item count | High-volume business notification |
| `INFO` | Normal important event | Job started | Every local variable |
| `WARNING` | Unexpected but recoverable | Retry | Normal successful operation |
| `ERROR` | An operation failed | Output write failed | Expected validation branch |
| `CRITICAL` | Severe application/system condition | Cannot initialize required component | Ordinary request failure |

### Operational thinking

Ask:

> What should an operator do when seeing this level?

That question is often more useful than asking:

> "How important is this to me as a programmer?"

---

## 8. Logger Objects

The normal application pattern is:

```python
import logging

logger = logging.getLogger(__name__)
```

### What does `getLogger()` do?

It returns a logger with the requested name.

For example:

```python
import logging

logger = logging.getLogger("app.service")
```

The name becomes part of the logging identity.

### Why `__name__`?

In a Python module, `__name__` identifies that module's import name.

For example:

```text
app/
    service.py
```

may have:

```text
__name__ == "app.service"
```

when imported as that module.

That gives logs useful source context without hard-coding logger names repeatedly.

### Reusing a named logger

Multiple calls with the same name refer to the same logical logger object.

```python
import logging

a = logging.getLogger("app.service")
b = logging.getLogger("app.service")

print(a is b)
```

Expected:

```text
True
```

### Application boundary

A strong pattern is:

```text
Application startup
    ↓
configure logging

Each module
    ↓
get named logger with __name__
```

This separates:

```text
logging use
```

from:

```text
logging configuration
```

---

## 9. Logger Names and Hierarchy

Logger names can form a hierarchy using dots.

Example:

```python
import logging

root = logging.getLogger("app")
service = logging.getLogger("app.service")
payment = logging.getLogger("app.service.payment")
```

Conceptually:

```text
app
├── app.service
│   └── app.service.payment
├── app.config
└── app.storage
```

### Parent and child

`app.service` is a child of `app`.

`app.service.payment` is a child of `app.service`.

### Why hierarchy exists

It gives applications a natural way to group logging behavior.

For example:

```text
app.service.*
```

can be configured as a family.

### Propagation

A child logger can propagate its records to ancestor handlers.

Conceptually:

```text
app.service.payment
        ↓
app.service
        ↓
app
        ↓
root
```

The record can be handled by handlers attached to appropriate ancestors.

### Root logger

The root logger is the top of the hierarchy.

You can access it with:

```python
import logging

root = logging.getLogger()
```

Application code usually benefits from named module loggers rather than putting all application logging directly on the root logger.

### Why duplicate logs appear

A common configuration mistake is:

```text
child logger has handler
+
ancestor logger has handler
+
propagation remains enabled
```

The same record can be emitted more than once.

This is why central configuration and an intentional propagation strategy matter.

---

## 10. Handlers

A handler sends log records toward a destination.

Conceptually:

```text
Logger
   ↓
Handler
   ↓
Destination
```

Common handlers include:

```python
import logging

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("app.log")
```

### `StreamHandler`

A stream handler writes to a file-like stream.

Example:

```python
import logging
import sys

handler = logging.StreamHandler(sys.stderr)
```

This can be useful for console-oriented diagnostics.

### `FileHandler`

A file handler writes log records to a file.

```python
import logging

handler = logging.FileHandler(
    "application.log",
    encoding="utf-8",
)
```

### Why handlers exist

Different destinations may have different operational purposes.

For example:

```text
DEBUG / INFO
    → console

ERROR / CRITICAL
    → another destination
```

A logging system can have multiple handlers.

### Handler level vs logger level

Both can filter messages.

```text
Logger level
    ↓
decides whether logger processes an event

Handler level
    ↓
decides whether that handler emits it
```

For example:

```python
import logging
import sys

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.WARNING)

logger.addHandler(handler)

logger.info("This is processed by the logger")
logger.warning("This is emitted by the handler")
```

The logger can accept `INFO`, while the handler only emits `WARNING` and above.

---

## 11. Formatters

A formatter controls how a `LogRecord` becomes final output.

Example:

```python
import logging

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
)
```

Attach it to a handler:

```python
handler.setFormatter(formatter)
```

### Useful record fields

Common `LogRecord` fields include:

```text
asctime
levelname
name
message
module
funcName
lineno
process
processName
thread
threadName
```

You do not need all of them in every log.

### Example

```python
import logging
import sys

handler = logging.StreamHandler(sys.stderr)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
)

handler.setFormatter(formatter)

logger = logging.getLogger("app.worker")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

logger.info("Processing started")
```

Output will have the general shape:

```text
2026-09-24 10:15:32,000 INFO app.worker Processing started
```

### Why metadata matters

Compare:

```text
Failed
```

with:

```text
2026-09-24 10:15:32 ERROR app.storage Output write failed
```

The second is far more useful during incident investigation.

---

## 12. Filters

A filter provides additional control over whether a logging record should be processed.

Conceptually:

```text
LogRecord
   ↓
Filter
   ↓
allow / reject
```

A basic custom filter:

```python
import logging


class JobFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith("app.job")
```

Use it:

```python
handler.addFilter(JobFilter())
```

### Why filters exist

Level filtering alone may not express every operational rule.

A filter can make a decision based on record information.

### Important distinction

A filter is not a replacement for:

```text
security design
access control
data classification
redaction strategy
```

Do not use a filter as an excuse to log sensitive values and hope that the record will always be removed.

A safer design is:

```text
avoid sensitive data
        ↓
then filter/log as needed
```

### Filters can be attached to logger or handler objects

The relevant APIs include:

```python
logger.addFilter(...)
logger.removeFilter(...)

handler.addFilter(...)
handler.removeFilter(...)
```

---

## 13. How a Log Record Travels Through the System

This simplified flow is one of the most important mental models in the chapter:

```text
Application code
      ↓
Logger method
      ↓
Is event enabled?
      ↓
LogRecord
      ↓
Logger / Handler filters
      ↓
Handlers
      ↓
Formatter
      ↓
Destination
```

Consider:

```python
logger.error("Database connection failed")
```

### Step 1 — logger receives the call

The application calls:

```python
logger.error(...)
```

### Step 2 — level decision

The logger determines whether an event at `ERROR` should be processed under its effective level.

### Step 3 — record creation

The event information becomes a `LogRecord`.

### Step 4 — handlers receive the record

Relevant handlers are considered.

### Step 5 — handler filtering

A handler's own level and filters can reject the event.

### Step 6 — formatting

The record is formatted for output.

### Step 7 — destination

The handler emits the result to its configured destination.

### Why understanding this matters

When something goes wrong, ask:

```text
Did the logger receive the event?
Was its level enabled?
Did a handler exist?
Did the handler allow the level?
Did a filter reject it?
Did propagation route it somewhere unexpected?
Did formatting fail?
Did the destination behave as expected?
```

That is much better than randomly changing log statements.

---

## 14. `basicConfig()`

`basicConfig()` is the convenient entry point for simple applications and scripts.

Example:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
```

### Common arguments

Relevant arguments include:

```text
level=
format=
datefmt=
filename=
filemode=
stream=
handlers=
encoding=
```

### `level=`

Controls the threshold for the basic configuration.

```python
logging.basicConfig(level=logging.DEBUG)
```

### `format=`

Controls message layout.

```python
logging.basicConfig(
    format="%(levelname)s %(name)s %(message)s"
)
```

### `datefmt=`

Controls timestamp rendering when timestamps are included in the format.

```python
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
```

### `filename=`

Can direct logging to a file.

```python
logging.basicConfig(
    filename="application.log",
    level=logging.INFO,
    encoding="utf-8",
)
```

### `filemode=`

For file-based configurations, `filemode="w"` starts a new file rather than appending.

```python
logging.basicConfig(
    filename="application.log",
    filemode="w",
    level=logging.INFO,
)
```

For production services, be cautious with local file logs and consider how a deployment collects and retains them.

### `handlers=`

You can provide explicitly constructed handlers.

```python
import logging
import sys

handler = logging.StreamHandler(sys.stderr)

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
)
```

### `encoding=`

Useful for file output.

```python
logging.basicConfig(
    filename="application.log",
    encoding="utf-8",
)
```

The `encoding` argument was added in Python 3.9.

### An important behavior

`basicConfig()` is intended for simple setup.

If logging is already configured, calling `basicConfig()` again may not change the configuration in the way a beginner expects.

For larger applications, explicit configuration at the application boundary is often clearer.

---

## 15. `getLogger()`

The central API is:

```python
logging.getLogger()
```

or:

```python
logging.getLogger(__name__)
```

### Root logger

```python
import logging

root_logger = logging.getLogger()
```

### Named logger

```python
import logging

logger = logging.getLogger("app.service")
```

### Module logger

```python
import logging

logger = logging.getLogger(__name__)
```

### Why named loggers?

A named logger gives the application:

```text
source identity
hierarchy
filtering opportunities
configuration control
```

### Libraries

A reusable library should not silently take ownership of the application's global logging configuration.

A common pattern is:

```python
import logging

logger = logging.getLogger(__name__)
```

A library may use a `NullHandler` for its own top-level logging namespace when appropriate.

```python
import logging

logging.getLogger("my_library").addHandler(
    logging.NullHandler()
)
```

The application that uses the library should control global logging configuration.

---

## 16. Logging Methods

The major logger methods are:

```python
logger.debug(...)
logger.info(...)
logger.warning(...)
logger.error(...)
logger.exception(...)
logger.critical(...)
```

There is also:

```python
logger.log(...)
```

for logging at an explicitly supplied numeric level.

### `debug()`

```python
logger.debug(
    "Parsed %d records",
    record_count,
)
```

### `info()`

```python
logger.info(
    "Job started job_id=%s",
    job_id,
)
```

### `warning()`

```python
logger.warning(
    "Retrying request attempt=%d",
    attempt,
)
```

### `error()`

```python
logger.error(
    "Output write failed path=%s",
    output_path,
)
```

### `critical()`

```python
logger.critical(
    "Required application component failed to initialize"
)
```

### `exception()`

Normally use it inside an exception handler:

```python
try:
    parse_config()
except ValueError:
    logger.exception("Configuration parsing failed")
```

It records exception information and traceback details.

### `log()`

```python
logger.log(
    logging.INFO,
    "Job %s started",
    job_id,
)
```

Most application code can use the named convenience methods.

### `enabled` checks

When building expensive diagnostic information, you may sometimes see:

```python
if logger.isEnabledFor(logging.DEBUG):
    ...
```

This is useful when the work required to construct the debug message is itself expensive.

---

## 17. Exception Logging

Exceptions and logging have different responsibilities.

```text
Exception
    = a program-level failure signal

Logging
    = operational evidence about what happened
```

A good error-handling structure might be:

```python
import logging

logger = logging.getLogger(__name__)


def parse_port(raw_value: str) -> int:
    try:
        return int(raw_value)
    except ValueError:
        logger.exception("Invalid port configuration")
        raise
```

### Why `raise` matters

Logging does not handle the error.

This:

```python
logger.exception("Something went wrong")
```

records information.

This:

```python
raise
```

preserves error propagation.

Whether you should re-raise depends on the component's recovery boundary.

### Handling and continuing

A recoverable condition may instead be:

```python
try:
    value = int(raw_value)
except ValueError:
    logger.warning("Using fallback for invalid value")
    value = 0
```

This is only correct if the fallback is genuinely valid for the application's semantics.

### Do not swallow exceptions

Avoid:

```python
try:
    process()
except Exception:
    logger.exception("Failed")
```

when there is no recovery plan.

The program may continue in an invalid state.

### Better principle

```text
catch
  ↓
decide whether you can recover
  ↓
log useful context
  ↓
recover or propagate
```

---

## 18. Logging Tracebacks

A traceback provides the execution path that led to an exception.

This is why:

```python
logger.exception("Processing failed")
```

is often more useful than:

```python
logger.error("Processing failed")
```

inside an exception handler.

### Example

```python
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

try:
    number = int("abc")
except ValueError:
    logger.error("Parsing failed")
```

This logs the failure message but not necessarily the traceback.

Compare:

```python
try:
    number = int("abc")
except ValueError:
    logger.exception("Parsing failed")
```

Now the exception traceback is included.

### `exc_info=True`

You can explicitly request exception information:

```python
try:
    risky_operation()
except RuntimeError:
    logger.error(
        "Risky operation failed",
        exc_info=True,
    )
```

This is useful when your chosen logging call is `error()` rather than `exception()`.

### Important rule

Do not log the same exception repeatedly at every layer without purpose.

For example:

```text
low-level function logs
service logs
controller logs
top-level handler logs
```

can produce noisy duplicate records.

A useful design is to choose the right boundary for:

```text
diagnostic detail
recovery
final operational reporting
```

---

## 19. Lazy Formatting

Preferred logging style:

```python
logger.info(
    "Processing user %s",
    user_id,
)
```

instead of:

```python
logger.info(
    f"Processing user {user_id}"
)
```

### Why?

The logging API accepts a message template plus arguments.

The logging machinery can defer message interpolation until the message actually needs to be emitted.

That can avoid unnecessary formatting work when the level is disabled.

### Example

```python
logger.debug(
    "Loaded %d records from %s",
    count,
    path,
)
```

### Avoid eager expensive work

This is more important than f-strings alone:

```python
logger.debug(
    "Large payload=%s",
    expensive_serialization(payload),
)
```

`expensive_serialization(payload)` is evaluated before the logger receives the call.

A better pattern may be:

```python
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(
        "Large payload=%s",
        expensive_serialization(payload),
    )
```

Only use such checks when the diagnostic work is actually expensive.

### Do not overstate the benefit

Logging performance depends on:

```text
enabled level
message construction cost
handler cost
formatter cost
destination cost
volume
```

The important principle is:

> Let logging defer ordinary message interpolation and avoid unnecessary expensive work.

---

## 20. Useful Context in Logs

A log without context is often difficult to use.

Bad:

```text
Request failed
```

Better:

```text
Request failed operation=embedding attempt=2
```

### Useful context

Depending on the application, useful context may include:

```text
job_id
request_id
operation
component
attempt
model name
provider
duration
record count
status
```

### Example

```python
logger.info(
    "Embedding batch completed "
    "batch_id=%s model=%s records=%d duration_ms=%.1f",
    batch_id,
    model_name,
    record_count,
    duration_ms,
)
```

### Context must be safe

Do not add:

```text
password
API token
authorization header
full private prompt
full confidential response
```

just because more context seems useful.

### Identifiers

Even identifiers can be sensitive.

For example:

```text
email address
phone number
customer account number
patient identifier
```

may need redaction, hashing, or omission depending on the application's requirements.

A practical rule:

> Log the minimum identifying information needed to investigate the event.

### Correlation identifiers

A request or job identifier can help connect related events:

```text
request_id=abc123
```

This is powerful because an investigator can find:

```text
request start
validation
external call
retry
failure
completion
```

for the same operation.

---

## 21. Safe Logging

Useful logs must also be safe logs.

The logging system can become a data-leak boundary if developers log everything.

### The central safety principle

> The safest sensitive value to log is often no sensitive value at all.

### Common sensitive categories

Do not casually log:

```text
passwords
API keys
access tokens
authorization headers
private keys
session credentials
payment card details
confidential business information
sensitive personal information
```

The exact requirements depend on the application's security and privacy rules.

### Unsafe example

```python
logger.info(
    "Authorization token=%s",
    token,
)
```

### Safer example

```python
logger.info(
    "Authentication succeeded user_id=%s",
    user_id,
)
```

Even `user_id` may need protection in some systems; the key idea is to log the operational event, not the credential.

### Payload logging

This is risky:

```python
logger.debug(
    "Request payload=%s",
    payload,
)
```

because a payload may contain:

```text
password
token
personal information
confidential text
customer information
```

### Better

Allowlist safe metadata:

```python
logger.debug(
    "Request received operation=%s content_type=%s size=%d",
    operation,
    content_type,
    payload_size,
)
```

---

## 22. What Must Never Be Logged

There is no universal legal list that fits every application, but the following are strong default exclusions.

### Credentials

Do not log:

```text
passwords
API keys
access tokens
refresh tokens
private keys
secret headers
```

### Authentication material

Avoid:

```text
Authorization: Bearer ...
Cookie: ...
session token ...
```

### Sensitive request/response bodies

Do not automatically log:

```text
entire user prompt
entire model response
entire HTTP body
uploaded document
database record
```

These may contain sensitive or confidential information.

### Security-sensitive configuration

Do not print:

```python
print(os.environ)
```

or:

```python
logger.debug("Config=%s", config)
```

when the object includes secrets.

### Financial or personal data

Do not casually log:

```text
full payment card data
password reset links
personal identifiers
private contact information
```

### AI-specific caution

AI systems create additional sensitive-data risks.

Prompts and model responses can contain:

```text
customer data
source documents
internal instructions
credentials
personal information
confidential business information
```

Therefore:

```text
"debug mode"
≠
"safe to log everything"
```

---

## 23. Logging Sensitive and Confidential Data

Sometimes an application needs to reason about a sensitive value without logging its contents.

### Example: redaction helper

```python
def redacted(value: str | None) -> str:
    if value is None:
        return "<missing>"

    return "<configured>"
```

Use it:

```python
logger.info(
    "Model credentials status=%s",
    redacted(api_key),
)
```

Output:

```text
Model credentials status=<configured>
```

### Better than partial secrets

A tempting pattern is:

```python
logger.debug("API key starts with %.4s", api_key)
```

Even partial secrets can create unnecessary disclosure.

A safer default is:

```text
<configured>
```

### Allowlist logging

Instead of:

```python
logger.debug("config=%s", config)
```

select safe fields:

```python
logger.debug(
    "Runtime configuration environment=%s "
    "model=%s timeout=%s",
    config.environment,
    config.model_name,
    config.timeout,
)
```

### Redaction is not magic

A redaction function can itself fail or miss new sensitive fields.

A stronger design is:

```text
avoid collecting sensitive data
        ↓
allowlist operational metadata
        ↓
redact where necessary
        ↓
test logging behavior
```

---

## 24. Structured and Machine-Readable Logging

Traditional logs are often plain text:

```text
INFO app.worker job_started job_id=123
```

Structured logs represent event fields in a machine-readable form.

For example:

```json
{
  "level": "INFO",
  "event": "job_started",
  "job_id": "123"
}
```

### Why structure helps

Machines can more easily:

```text
filter
search
aggregate
group
count
correlate
```

### Simple Python example

Python's standard library can serialize dictionaries as JSON:

```python
import json
import logging

logger = logging.getLogger(__name__)


def log_event(event: str, **fields: object) -> None:
    payload = {
        "event": event,
        **fields,
    }

    logger.info(json.dumps(payload))
```

Usage:

```python
log_event(
    "job_started",
    job_id="123",
    record_count=500,
)
```

This is a simple teaching example, not a complete production structured-logging framework.

### Structured does not mean safe automatically

This is still unsafe:

```python
log_event(
    "request",
    api_key="real-secret",
)
```

JSON does not make secrets safe.

### Human readability vs machine readability

There is often a trade-off:

```text
human-friendly text
        vs
machine-friendly structure
```

Production systems may choose formats that balance both.

---

## 25. Logging Configuration

Logging configuration should normally happen at an application boundary.

Conceptually:

```text
Application startup
       ↓
Configure logging
       ↓
Application components use named loggers
```

### A clean application pattern

```python
import logging


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s %(levelname)s "
            "%(name)s %(message)s"
        ),
    )
```

Then:

```python
def main() -> None:
    configure_logging()

    logger = logging.getLogger(__name__)
    logger.info("Application started")
```

### Why configure centrally?

Without centralized configuration, modules may independently:

```text
choose different levels
create duplicate handlers
change formatting
write to different files
cause duplicate propagation
```

### Configuration and environment

This naturally connects with the previous production-habits chapter.

For example, the application may read:

```text
LOG_LEVEL=INFO
```

and map it to a logging level.

A simple helper:

```python
import logging


def parse_log_level(raw: str) -> int:
    normalized = raw.strip().upper()

    value = getattr(logging, normalized, None)

    if not isinstance(value, int):
        raise ValueError(
            f"Invalid log level: {raw!r}"
        )

    return value
```

Usage:

```python
level = parse_log_level("DEBUG")
logging.basicConfig(level=level)
```

### Be deliberate

Logging configuration is part of application startup behavior.

Do not let random imported modules silently redefine the application's logging policy.

---

## 26. Logging in Modules and Packages

A module should normally obtain its own logger:

```python
import logging

logger = logging.getLogger(__name__)
```

Then use it:

```python
def load_document(path: str) -> str:
    logger.info("Loading document path=%s", path)
    ...
```

### Why this is useful

The module name becomes part of the logger hierarchy.

Example:

```text
app.reader
app.parser
app.embedding
app.storage
```

This lets an operator understand where a message originated.

### Application configuration boundary

An application can configure handlers centrally:

```python
import logging
import sys


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s "
            "%(name)s %(message)s"
        )
    )

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
```

Modules do not need to repeat that configuration.

### Library behavior

A reusable library should generally:

```text
emit log records
avoid owning the application's output policy
```

It should not assume:

```text
"Write logs to my favorite file"
```

without the application asking for that behavior.

---

## 27. Logging in CLI Applications

A CLI often has two communication channels:

```text
user-facing output
operational diagnostics
```

### User-facing output

```python
print("Report generated successfully")
```

### Logging

```python
logger.info(
    "Report generation completed output=%s",
    output_path,
)
```

### Why separate them?

A shell user may need:

```text
Report generated successfully
```

while an operator may need:

```text
job_id=42 processed=10000 failures=7 duration_ms=4210
```

### A small CLI example

```python
import argparse
import logging


logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s %(message)s",
    )

    logger.info("CLI started")

    print("Hello from the CLI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Important distinction

Do not automatically replace every `print()` with logging.

Ask:

> Is this text the user's result, or is it operational evidence for developers/operators?

---

## 28. Logging in Data Pipelines

Consider:

```text
Input
  ↓
Validation
  ↓
Transformation
  ↓
Output
```

A useful data-pipeline log stream might contain:

```text
input detected
validation started
records read
validation failures
transformation completed
output written
job completed
```

### Good pipeline logs

```python
logger.info(
    "Input loaded path=%s records=%d",
    input_path,
    record_count,
)
```

```python
logger.warning(
    "Validation failures count=%d",
    invalid_count,
)
```

```python
logger.info(
    "Output written path=%s records=%d",
    output_path,
    valid_count,
)
```

### Avoid logging the dataset itself

Do not do this:

```python
logger.debug("records=%s", records)
```

when `records` could be large or sensitive.

A better pattern is:

```python
logger.debug(
    "Batch prepared records=%d",
    len(records),
)
```

### Logging stages

Stage-level logs are useful:

```text
extract started
extract completed
transform started
transform completed
load started
load completed
```

Add identifiers and counts where they add operational value.

---

## 29. Logging in Applied AI Systems

AI applications are often long-running multi-step workflows.

Example:

```text
request received
      ↓
validation
      ↓
retrieval
      ↓
model call
      ↓
tool call
      ↓
post-processing
      ↓
response
```

### Useful AI-system logging

Safe operational metadata may include:

```text
request_id
job_id
operation
model name
provider
latency
retry count
tool name
status
record count
token counts when appropriate
```

### Example

```python
logger.info(
    "Inference completed "
    "request_id=%s model=%s latency_ms=%.1f status=%s",
    request_id,
    model_name,
    latency_ms,
    status,
)
```

### Do not automatically log prompts

A prompt can contain:

```text
customer information
private documents
internal instructions
credentials
confidential business data
```

Therefore:

```python
logger.debug("prompt=%s", prompt)
```

should not be a default production habit.

### Do not automatically log model responses

The response may contain equally sensitive data.

Instead, log safe metadata:

```python
logger.info(
    "Model response received "
    "request_id=%s status=%s latency_ms=%.1f",
    request_id,
    status,
    latency_ms,
)
```

### Tool calls

A safe tool log could be:

```python
logger.info(
    "Tool call completed "
    "request_id=%s tool=%s status=%s duration_ms=%.1f",
    request_id,
    tool_name,
    status,
    duration_ms,
)
```

Avoid blindly dumping arguments and outputs.

---

## 30. Logging Failures and Retries

Retries create multiple events for one logical operation.

Suppose:

```text
attempt 1 → timeout
attempt 2 → timeout
attempt 3 → success
```

A useful log sequence is:

```text
WARNING request failed; retrying attempt=1
WARNING request failed; retrying attempt=2
INFO request succeeded attempt=3
```

### Example

```python
for attempt in range(1, max_attempts + 1):
    try:
        call_service()
        logger.info(
            "Request succeeded attempt=%d",
            attempt,
        )
        break
    except TimeoutError:
        if attempt == max_attempts:
            logger.exception(
                "Request failed after final attempt=%d",
                attempt,
            )
            raise

        logger.warning(
            "Request failed; retrying attempt=%d/%d",
            attempt,
            max_attempts,
        )
```

### What should be visible?

At minimum:

```text
what failed
attempt number
maximum attempts
logical operation
safe identifier
final outcome
```

### Avoid duplicate noise

Do not have every low-level layer emit an `ERROR` for the same retry if the upper layer already provides the final operational record.

### Retry storms

Logs can become extremely noisy during a retry storm.

A design should consider:

```text
retry count
concurrency
rate limits
timeouts
backoff
logging volume
```

Logging helps reveal the problem, but it does not itself solve overload.

---

## 31. Logging Without Creating Noise

Good logging is not the same as maximum logging.

### Too little

```text
Failed.
```

### Too much

```text
Entering function
x=1
y=2
z=3
loop iteration 1
loop iteration 2
loop iteration 3
...
```

### Better

Log meaningful events.

```python
logger.info(
    "Batch processed batch_id=%s records=%d",
    batch_id,
    record_count,
)
```

### High-value logs

Good logs often explain:

```text
lifecycle
decision
failure
recovery
result
important state transition
```

### Low-value logs

Avoid flooding logs with:

```text
every loop iteration
every property access
every function entry
huge objects
duplicate success messages
```

### Tight loops

This can generate enormous volume:

```python
for record in records:
    logger.debug("Processing record=%s", record)
```

A safer pattern is to aggregate:

```python
logger.debug(
    "Processing batch batch_size=%d",
    len(records),
)
```

### The right question

Do not ask:

> "Can I log this?"

Ask:

> "Will this log help an operator or developer make a decision?"

---

## 32. Common Logging Anti-Patterns

### Anti-pattern 1 — `print()` for all diagnostics

**Problem**

Operational information becomes unstructured and difficult to control.

**Bad**

```python
print("database failed")
```

**Better**

```python
logger.error("Database operation failed")
```

---

### Anti-pattern 2 — everything is `ERROR`

**Problem**

The logs lose severity meaning.

**Bad**

```python
logger.error("Job started")
logger.error("Retrying")
logger.error("Job completed")
```

**Better**

```python
logger.info("Job started")
logger.warning("Retrying request")
logger.info("Job completed")
```

---

### Anti-pattern 3 — logging secrets

**Problem**

Credentials can leak into logs.

**Bad**

```python
logger.debug("token=%s", token)
```

**Better**

```python
logger.debug("Authentication token configured=%s", bool(token))
```

---

### Anti-pattern 4 — logging entire payloads

**Problem**

Payloads can be huge and sensitive.

**Bad**

```python
logger.debug("payload=%s", payload)
```

**Better**

```python
logger.debug(
    "request received content_type=%s size=%d",
    content_type,
    payload_size,
)
```

---

### Anti-pattern 5 — duplicate logging

**Problem**

The same failure is reported multiple times.

**Better**

Define clear logging boundaries:

```text
low-level function
    → add technical context only when useful

recovery boundary
    → log recovery decision

top-level failure boundary
    → log final failure with traceback
```

---

### Anti-pattern 6 — logging and swallowing exceptions

**Bad**

```python
try:
    process()
except Exception:
    logger.exception("Processing failed")
```

and then silently continuing.

**Problem**

The system may be in an invalid state.

**Better**

Recover intentionally or re-raise.

---

### Anti-pattern 7 — no context

**Bad**

```python
logger.error("Failed")
```

**Better**

```python
logger.error(
    "Embedding request failed model=%s attempt=%d",
    model_name,
    attempt,
)
```

---

### Anti-pattern 8 — configuring handlers repeatedly

**Problem**

Every call that adds another handler can cause duplicate output.

**Bad pattern**

```python
def configure():
    logger = logging.getLogger("app")
    logger.addHandler(logging.StreamHandler())
```

called repeatedly without ownership checks.

**Better**

Configure logging once at the application boundary.

---

### Anti-pattern 9 — noisy loops

**Problem**

Millions of records can produce millions of logs.

**Better**

Log batches, counts, failures, and milestones.

---

### Anti-pattern 10 — logging sensitive identifiers unnecessarily

A user identifier may itself be sensitive.

Prefer the minimum necessary context.

---

### Anti-pattern 11 — meaningless messages

Bad:

```text
here
done
problem
x failed
```

Better:

```text
Batch validation completed invalid_records=7 batch_id=42
```

---

### Anti-pattern 12 — assuming `DEBUG` is invisible

In one environment `DEBUG` may be disabled.

In another environment it may be enabled and collected centrally.

Treat every log statement as potentially observable.

---

## 33. Testing Logging

Logging behavior can be tested, but tests should focus on meaningful behavior rather than fragile formatting.

If the project uses `pytest`, `caplog` is a convenient way to inspect emitted records.

### Example

```python
import logging


logger = logging.getLogger(__name__)


def validate_user(user_id: str) -> bool:
    if not user_id:
        logger.warning("User validation failed")
        return False

    return True
```

Test:

```python
def test_invalid_user_logs_warning(caplog):
    with caplog.at_level(logging.WARNING):
        assert validate_user("") is False

    assert "User validation failed" in caplog.text
```

### What should the test prove?

The important assertion is usually:

```text
a warning occurred
message contains useful event information
```

not:

```text
the exact timestamp is character-for-character identical
```

### Testing level

You can inspect records:

```python
def test_log_level(caplog):
    with caplog.at_level(logging.WARNING):
        logger.warning("Something unexpected happened")

    assert any(
        record.levelno == logging.WARNING
        for record in caplog.records
    )
```

### Testing context

```python
def process_job(job_id: str) -> None:
    logger.info("Job started job_id=%s", job_id)
```

Test the context:

```python
def test_job_id_is_logged(caplog):
    with caplog.at_level(logging.INFO):
        process_job("42")

    assert "job_id=42" in caplog.text
```

### Testing secrets

A strong test can ensure a sensitive value is absent.

```python
def safe_auth_log(api_key: str) -> None:
    logger.info(
        "Authentication configured=%s",
        bool(api_key),
    )
```

```python
def test_secret_not_logged(caplog):
    secret = "not-for-logs"

    with caplog.at_level(logging.INFO):
        safe_auth_log(secret)

    assert secret not in caplog.text
```

### Avoid over-testing formatting

If the application is not contractually dependent on exact text formatting, do not create brittle tests around:

```text
exact timestamp
exact whitespace
exact punctuation
```

Test the semantic properties that matter.

---

## 34. Debugging with Logs

Logs are especially valuable when the problem cannot be reproduced directly.

### A debugging workflow

```text
1. Find the failure
2. Identify when it happened
3. Identify request/job/operation
4. Trace surrounding events
5. Find the first meaningful failure
6. Inspect traceback
7. Reproduce if possible
8. Fix root cause
9. Add regression coverage
```

### Example incident

```text
Job failed.
```

Find:

```text
job_id=42
```

Then locate:

```text
job started
input loaded
validation completed
model request started
retry 1
retry 2
final model failure
job failed
```

Now the log stream reconstructs the operational timeline.

### First failure matters

Suppose you see:

```text
ERROR Database write failed
ERROR Job failed
ERROR Request failed
```

The first meaningful failure may be the database error.

Later errors can be consequences.

### Log context helps

Without:

```text
request_id
job_id
operation
```

it may be impossible to correlate events in a busy service.

### Do not debug by random printing

A better workflow is:

```text
hypothesis
    ↓
targeted instrumentation
    ↓
reproduce
    ↓
inspect evidence
    ↓
fix
```

---

## 35. Production Logging Design

A simple production-oriented architecture is:

```text
Python application
       ↓
Named loggers
       ↓
Logger level / filters
       ↓
Handlers
       ↓
Formatter / structured representation
       ↓
stdout / file / other destination
       ↓
collection system
       ↓
operators / developers / monitoring
```

### Application responsibility

The Python application should:

```text
emit meaningful events
choose sensible levels
include useful context
avoid sensitive data
handle exceptions correctly
```

### Configuration responsibility

The application boundary should define:

```text
levels
handlers
format
destinations
propagation strategy
```

### Collection responsibility

A later-stage platform may collect logs.

This chapter does not teach a specific:

```text
cloud logging product
Kubernetes log stack
ELK deployment
OpenTelemetry deployment
```

Those are separate infrastructure topics.

### Operational properties

Good production logging supports:

```text
debuggability
reliability
maintainability
security
operability
```

### Retention

Log retention is an operational policy.

More logs are not automatically better.

Questions include:

```text
How long should logs be retained?
Who can access them?
What sensitive data do they contain?
How much storage do they consume?
What needs to be searchable?
```

Keep these questions in mind even if the implementation is local.

---

## 36. Complete Production Example

### Production-Style Data Processing CLI

We will build one self-contained example that demonstrates:

- module-level logger;
- centralized logging configuration;
- log levels;
- useful context;
- exception logging;
- retry behavior;
- safe logging;
- user-facing output;
- operational logs;
- final success/failure.

### Scenario

A command-line job processes a list of records.

```text
startup
  ↓
input validation
  ↓
processing
  ↓
recoverable retry
  ↓
output
  ↓
summary
```

### Code

```python
from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class JobConfig:
    job_id: str
    max_retries: int = 2
    delay_seconds: float = 0.01


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)


def process_record(record: str, config: JobConfig) -> str:
    if not record.strip():
        raise ValueError("Record is empty")

    for attempt in range(1, config.max_retries + 2):
        try:
            if record == "retry-me" and attempt == 1:
                raise TimeoutError("Simulated timeout")

            logger.debug(
                "Record processed job_id=%s record=%s attempt=%d",
                config.job_id,
                record,
                attempt,
            )
            return record.upper()

        except TimeoutError:
            if attempt > config.max_retries:
                logger.exception(
                    "Record failed after retries "
                    "job_id=%s attempt=%d",
                    config.job_id,
                    attempt,
                )
                raise

            logger.warning(
                "Record timed out; retrying "
                "job_id=%s attempt=%d/%d",
                config.job_id,
                attempt,
                config.max_retries + 1,
            )
            time.sleep(config.delay_seconds)

    raise RuntimeError("Unreachable")


def run_job(records: list[str], config: JobConfig) -> list[str]:
    logger.info(
        "Job started job_id=%s input_records=%d",
        config.job_id,
        len(records),
    )

    results: list[str] = []

    for record in records:
        try:
            results.append(process_record(record, config))
        except ValueError:
            logger.warning(
                "Invalid record skipped job_id=%s",
                config.job_id,
            )

    logger.info(
        "Job completed job_id=%s output_records=%d",
        config.job_id,
        len(results),
    )

    return results


def main() -> int:
    configure_logging()

    logger.info("Application startup")

    config = JobConfig(job_id="job-42")

    records = [
        "alpha",
        "beta",
        "retry-me",
        "",
        "gamma",
    ]

    try:
        results = run_job(records, config)
    except Exception:
        logger.exception(
            "Job failed job_id=%s",
            config.job_id,
        )
        return 1

    for result in results:
        print(result)

    logger.info(
        "Application shutdown job_id=%s status=success",
        config.job_id,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Important design decisions

#### 1. Module logger

```python
logger = logging.getLogger(__name__)
```

This keeps the logger tied to the module hierarchy.

#### 2. Central configuration

```python
configure_logging()
```

is called once during application startup.

#### 3. Context

Most lifecycle logs contain:

```text
job_id
record count
attempt number
status
```

#### 4. Retry logging

Retries are `WARNING` because a problem occurred but recovery is possible.

#### 5. Final failure

The top-level boundary uses:

```python
logger.exception(...)
```

to preserve traceback information.

#### 6. User-facing output

The processed results are printed with:

```python
print(result)
```

because those are the CLI's intended output.

#### 7. No secret logging

The example does not log:

```text
credentials
tokens
private data
```

### One safety improvement

The example's debug statement includes the record:

```python
logger.debug(
    "Record processed ... record=%s",
    record,
)
```

That is fine only if the records are known to be safe. In a real AI/data pipeline, records may be sensitive.

A safer production design could log:

```python
logger.debug(
    "Record processed job_id=%s attempt=%d",
    config.job_id,
    attempt,
)
```

### What the log stream should tell an operator

An operator should be able to answer:

```text
Did the job start?
Which job?
How many records?
Did a record fail?
Was a retry attempted?
Did the job complete?
How many outputs?
Was the final status successful?
```

That is exactly the kind of information production logging should provide.

---

## 37. Coding Examples Requirements

Every example in this chapter should follow these rules.

### Rule 1 — valid Python

Examples must be syntactically valid Python.

### Rule 2 — understandable

Use:

```python
logger.info("Job started job_id=%s", job_id)
```

before introducing more advanced customization.

### Rule 3 — complete enough to run

Prefer complete examples with imports.

### Rule 4 — explain new APIs

When introducing:

```python
logging.Formatter(...)
```

explain:

```text
what it is
why it exists
how it is attached
what output it changes
```

### Rule 5 — show bad vs good

For important production habits:

```text
Bad
 ↓
Why it is risky
 ↓
Better
 ↓
Why it is better
```

### Rule 6 — avoid secret-containing examples

Use:

```text
fake-secret
```

or:

```text
<configured>
```

never realistic credentials.

---

## 38. Function/API Coverage Requirement

The goal is practical mastery of the important public APIs relevant to this chapter.

### Core module entry points

You should know:

```python
logging.basicConfig(...)
logging.getLogger(...)
logging.debug(...)
logging.info(...)
logging.warning(...)
logging.error(...)
logging.exception(...)
logging.critical(...)
```

### Logger methods

You should know:

```python
logger.debug(...)
logger.info(...)
logger.warning(...)
logger.error(...)
logger.exception(...)
logger.critical(...)
logger.log(...)
```

Relevant configuration methods and attributes include:

```python
logger.setLevel(...)
logger.addHandler(...)
logger.removeHandler(...)
logger.addFilter(...)
logger.removeFilter(...)
logger.propagate
logger.disabled
logger.isEnabledFor(...)
```

### Handler APIs

For common handlers:

```python
handler.setLevel(...)
handler.setFormatter(...)
handler.addFilter(...)
handler.removeFilter(...)
```

### Core classes

You should understand:

```python
logging.Logger
logging.LogRecord
logging.Handler
logging.StreamHandler
logging.FileHandler
logging.Formatter
logging.Filter
```

### `LogRecord`

A `LogRecord` carries event metadata.

A simple diagnostic example:

```python
import logging

logger = logging.getLogger("app")

logger.info(
    "Example event"
)
```

The logging system constructs a record that carries information such as:

```text
logger name
level
message
module
function
line
time
process
thread
```

### `StreamHandler`

```python
import logging
import sys

handler = logging.StreamHandler(sys.stderr)
```

Use when log events should be emitted to a stream.

### `FileHandler`

```python
import logging

handler = logging.FileHandler(
    "app.log",
    encoding="utf-8",
)
```

Use for direct file output when that deployment design is appropriate.

### `Formatter`

```python
formatter = logging.Formatter(
    "%(levelname)s %(name)s %(message)s"
)
```

### `Filter`

```python
class PrefixFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith("app.")
```

### Important parameter idea

For message methods:

```python
logger.info(
    "Records processed=%d",
    count,
)
```

the first argument is the format string and later positional arguments supply values.

### `exc_info`

Relevant to exception information:

```python
logger.error(
    "Operation failed",
    exc_info=True,
)
```

### `extra`

Logging also supports adding extra record attributes:

```python
logger.info(
    "Job started",
    extra={"job_id": "42"},
)
```

A formatter can then use:

```python
"%(job_id)s"
```

However, `extra` introduces schema requirements: any formatter referencing a field must receive that field. Use it deliberately.

Example:

```python
import logging

logger = logging.getLogger("app")

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "%(levelname)s job_id=%(job_id)s %(message)s"
    )
)

logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info(
    "Job started",
    extra={"job_id": "42"},
)
```

### API completeness principle

Do not use an API silently.

For every important logging API introduced, explain:

```text
purpose
arguments
result/behavior
failure behavior
common mistake
production relevance
```

---

## 39. Concept → Internal Mechanics → Practice

Use this pattern for every difficult concept.

### Example: logger hierarchy

**Simple explanation**

A logger can belong to a named family.

**Technical explanation**

Logger names use dot-separated hierarchy.

**Mental model**

```text
app
└── app.service
    └── app.service.payment
```

**Implementation**

```python
import logging

logger = logging.getLogger("app.service.payment")
```

**Runtime behavior**

Records can propagate toward ancestor handlers.

**Common mistake**

Adding handlers to both child and parent and getting duplicates.

**Practice**

Create a parent logger and child logger and predict how propagation behaves.

### Example: handler

**Simple explanation**

A handler decides where a log goes.

**Technical explanation**

A `Handler` dispatches `LogRecord` instances to a destination.

**Practice**

Attach a `StreamHandler` with its own level.

### Example: formatter

**Simple explanation**

A formatter decides what the final log line looks like.

**Practice**

Create a formatter containing:

```text
timestamp
level
logger
message
```

### Example: safe logging

**Simple explanation**

Do not put secrets into logs.

**Technical explanation**

Logs are observable operational outputs and may be stored, collected, copied, or accessed by people and systems you did not expect.

**Practice**

Rewrite a log that exposes a token so it only logs safe metadata.

---

## 40. Exercises

### Beginner Exercise 1 — Create a Logger

**Problem**

Create a module-level named logger and emit:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

**Requirements**

- use `logging.getLogger(__name__)`;
- configure logging;
- observe which levels appear.

**Hint**

Set the basic configuration level to `DEBUG`.

**Solution**

```python
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

logger.debug("Debug event")
logger.info("Info event")
logger.warning("Warning event")
logger.error("Error event")
logger.critical("Critical event")
```

**Explanation**

The threshold is `DEBUG`, so all standard levels from `DEBUG` upward can be emitted.

---

### Beginner Exercise 2 — Logging vs `print()`

**Problem**

Rewrite this:

```python
print("Validation failed")
```

as an operational warning.

**Solution**

```python
import logging

logger = logging.getLogger(__name__)

logger.warning("Validation failed")
```

**Why**

The event now has a severity and can participate in logging configuration.

---

### Beginner Exercise 3 — Add Context

**Problem**

Change:

```python
logger.error("Failed")
```

to include:

```text
job_id
```

**Solution**

```python
logger.error(
    "Job failed job_id=%s",
    job_id,
)
```

---

### Beginner Exercise 4 — Log an Exception

**Problem**

Log a traceback when parsing fails.

**Solution**

```python
import logging

logger = logging.getLogger(__name__)

try:
    int("abc")
except ValueError:
    logger.exception("Failed to parse integer")
```

---

### Intermediate Exercise 5 — Build a Formatter

**Problem**

Create a formatter containing:

```text
timestamp
level
logger name
message
```

**Solution**

```python
import logging

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
)
```

---

### Intermediate Exercise 6 — Create a Stream Handler

**Problem**

Create a handler that writes to standard error and only emits `WARNING` and above.

**Solution**

```python
import logging
import sys

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.WARNING)
```

---

### Intermediate Exercise 7 — Prevent Sensitive Logging

**Problem**

This code is unsafe:

```python
logger.info("token=%s", token)
```

Rewrite it.

**Solution**

```python
logger.info(
    "Authentication configured=%s",
    bool(token),
)
```

The actual token value is not logged.

---

### Intermediate Exercise 8 — Test a Warning

**Problem**

Use `pytest` and `caplog` to verify that a warning is emitted for invalid input.

**Solution**

```python
import logging

logger = logging.getLogger(__name__)


def validate(value: str) -> bool:
    if not value:
        logger.warning("Validation failed")
        return False

    return True
```

```python
def test_validate_logs_warning(caplog):
    with caplog.at_level(logging.WARNING):
        assert validate("") is False

    assert "Validation failed" in caplog.text
```

---

### Advanced Exercise 9 — Find Duplicate Logging

**Problem**

A child logger has a handler and the root logger also has a handler. Messages appear twice.

**Task**

Explain:

```text
why
```

and identify two legitimate fixes.

**Solution**

Potential causes include handler duplication combined with propagation.

Two common fixes are:

```text
1. Configure handlers centrally and allow child loggers to propagate.
2. If a child must have its own destination, control propagation with:
   logger.propagate = False
```

Use the design that matches the application's ownership model.

---

### Advanced Exercise 10 — Safe AI Logging

**Problem**

An LLM service currently logs:

```python
logger.debug(
    "prompt=%s response=%s api_key=%s",
    prompt,
    response,
    api_key,
)
```

Refactor the logging design.

**Solution**

```python
logger.info(
    "Inference completed "
    "request_id=%s model=%s latency_ms=%.1f",
    request_id,
    model_name,
    latency_ms,
)
```

The operational event is preserved without logging the prompt, response, or API key.

---

### Advanced Exercise 11 — Retry Logging

**Problem**

Create logs for:

```text
attempt 1 failed
retrying
attempt 2 failed
final failure
```

**Solution**

```python
for attempt in range(1, 3):
    try:
        call_service()
        logger.info(
            "Request succeeded attempt=%d",
            attempt,
        )
        break
    except TimeoutError:
        if attempt == 2:
            logger.exception(
                "Request failed after final attempt=%d",
                attempt,
            )
            raise

        logger.warning(
            "Request failed; retrying attempt=%d",
            attempt,
        )
```

---

### Production Exercise 12 — Design a Data-Pipeline Log Contract

**Problem**

Define the minimum safe fields you would log for:

```text
job started
batch completed
validation warning
job failed
job completed
```

**Expected answer**

A strong answer might include:

```text
job_id
operation/event
timestamp
status
record count
batch number
duration
attempt
safe error category
```

Avoid:

```text
full records
credentials
full payloads
private documents
```

---

## 41. Mini Project

# Mini-Project — Production-Style Data Processing CLI with Safe Logging

Build a small CLI-oriented processing program.

The project must remain self-contained within this Markdown chapter.

### Project goal

Create:

```text
input
  ↓
validation
  ↓
processing
  ↓
logging
  ↓
error handling
  ↓
output
```

### Requirements

Your program should:

1. create a module-level logger;
2. configure logging at startup;
3. allow the log level to be selected;
4. log job start;
5. log input count;
6. log recoverable validation warnings;
7. log retries;
8. log final failures with traceback;
9. log successful completion;
10. keep user-facing output separate from diagnostics;
11. never log secrets;
12. provide safe contextual identifiers;
13. include tests for important logging behavior.

### Suggested data model

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class JobConfig:
    job_id: str
    log_level: int
    max_retries: int = 2
```

### Suggested logging configuration

```python
import logging
import sys


def configure_logging(level: int) -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s "
        "%(name)s %(message)s"
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
```

### Suggested processing function

```python
def process_record(
    record: str,
    logger: logging.Logger,
) -> str:
    logger.debug(
        "Processing record length=%d",
        len(record),
    )

    if not record.strip():
        raise ValueError("Record is empty")

    return record.upper()
```

### Required operational events

Your logs should make these questions answerable:

```text
Which job?
When did it start?
How many inputs?
How many outputs?
How many invalid records?
Which attempt failed?
Why did it fail?
Did retries occur?
Did the job complete?
```

### Security requirement

Your logs must not contain:

```text
API key
password
authorization token
full user prompt
full private document
full sensitive payload
```

### Test requirements

Test:

```text
job-start log
validation warning
retry warning
final exception log
completion log
absence of secrets
```

### Reference solution

```python
from __future__ import annotations

import logging
import sys
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class JobConfig:
    job_id: str
    log_level: int = logging.INFO
    max_retries: int = 2


def configure_logging(level: int) -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s "
        "%(name)s %(message)s"
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)


def process_record(record: str, config: JobConfig) -> str:
    logger.debug(
        "Processing record job_id=%s length=%d",
        config.job_id,
        len(record),
    )

    if not record.strip():
        raise ValueError("Record is empty")

    return record.upper()


def run_job(records: list[str], config: JobConfig) -> list[str]:
    logger.info(
        "Job started job_id=%s records=%d",
        config.job_id,
        len(records),
    )

    results: list[str] = []
    invalid_count = 0

    for record in records:
        try:
            results.append(process_record(record, config))
        except ValueError:
            invalid_count += 1
            logger.warning(
                "Invalid record skipped job_id=%s",
                config.job_id,
            )

    if invalid_count:
        logger.warning(
            "Validation warnings job_id=%s invalid=%d",
            config.job_id,
            invalid_count,
        )

    logger.info(
        "Job completed job_id=%s outputs=%d",
        config.job_id,
        len(results),
    )

    return results


def main() -> int:
    config = JobConfig(job_id="job-001")

    configure_logging(config.log_level)

    try:
        results = run_job(
            ["alpha", "", "beta"],
            config,
        )
    except Exception:
        logger.exception(
            "Job failed job_id=%s",
            config.job_id,
        )
        return 1

    for result in results:
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Why this is production-oriented

It demonstrates:

```text
centralized configuration
named logger
levels
context
safe fields
exception logging
separation of output from logs
```

It intentionally does not attempt to build:

```text
distributed tracing
cloud log ingestion
Kubernetes log infrastructure
full security compliance system
```

Those belong to later engineering topics.

---

## 42. Interview Questions

### Basic

#### Question 1 — What is logging?

**How to think**

Think of logs as operational evidence.

**Answer**

Logging is recording useful runtime events so developers and operators can understand what a program did and diagnose problems.

**Why it matters**

A process may fail after its interactive session is gone.

---

#### Question 2 — Why use logging instead of `print()`?

**Answer**

Logging provides levels, named loggers, handlers, formatting, filtering, exception support, hierarchy, and centralized configuration.

`print()` can still be appropriate for explicit user-facing CLI output.

---

#### Question 3 — What are the standard log levels?

**Answer**

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

They represent increasing severity.

---

#### Question 4 — What is a logger?

**Answer**

A `Logger` is the interface application code uses to create log events and participate in level/filtering/handler dispatch.

---

### Intermediate

#### Question 5 — What is a handler?

**Answer**

A handler dispatches log records to a destination such as a stream or file.

---

#### Question 6 — What is a formatter?

**Answer**

A formatter determines how a log record is rendered for output.

---

#### Question 7 — What is logger propagation?

**Answer**

A child logger can pass records toward ancestor loggers and their handlers unless propagation is disabled.

---

#### Question 8 — Why use `logging.getLogger(__name__)`?

**Answer**

It creates a logger whose name follows the module's namespace, providing useful source identity and natural hierarchy.

---

### Advanced

#### Question 9 — Why do duplicate log messages appear?

**Answer**

A common cause is multiple relevant handlers combined with propagation, such as a handler on a child logger and another handler on an ancestor.

---

#### Question 10 — Difference between `logger.error()` and `logger.exception()`?

**Answer**

`logger.exception()` is designed for exception handlers and includes traceback/exception information. `logger.error()` logs an error event and does not inherently mean "include the current exception traceback."

---

#### Question 11 — Why is lazy formatting recommended?

**Answer**

The logging API can delay ordinary message interpolation until the event needs to be emitted. This can avoid unnecessary formatting work for disabled levels.

---

#### Question 12 — Should a production AI service log the full prompt?

**Answer**

Not by default. Prompts can contain sensitive or confidential information. Prefer logging safe operational metadata such as request ID, model, status, latency, and error category.

---

#### Question 13 — How would you prevent secrets from appearing in logs?

**Answer**

Do not log secrets in the first place. Use allowlisted fields, safe summaries, redaction where needed, and tests that verify sensitive values do not appear.

---

## 43. Architecture Questions

### Scenario 1 — Python CLI with many scheduled jobs

A CLI is executed by thousands of jobs.

**Questions**

- Where should logging configuration live?
- What belongs in user-facing output?
- What belongs in logs?
- What identifiers should connect related events?

**Reasoning**

Configure logging once at the application boundary.

Use CLI output for intended user-facing results.

Use logging for operational diagnostics.

Include a job ID and event context.

---

### Scenario 2 — LLM inference service

An AI service receives many inference requests.

**Questions**

What would you log?

**Reasoning**

Potentially:

```text
request_id
model
provider
latency
status
retry count
safe error category
```

Avoid automatically logging:

```text
API keys
full prompts
full responses
authorization headers
private documents
```

---

### Scenario 3 — Duplicate logs

Every error appears three times.

**Questions**

What should you inspect?

**Reasoning**

Inspect:

```text
logger handlers
ancestor handlers
propagate
root handlers
repeated configuration calls
```

---

### Scenario 4 — Data pipeline

A data-processing job occasionally drops records.

**Questions**

What should logs help you determine?

**Reasoning**

At minimum:

```text
job
stage
batch
input count
invalid count
output count
failure category
timestamp
```

Do not log the full dataset.

---

### Scenario 5 — Logging during retries

A service is retrying an external operation thousands of times.

**Questions**

How should logging be designed?

**Reasoning**

Use:

```text
WARNING for recoverable retry events
ERROR/exception for final unrecovered failure
```

Include attempt number and operation context.

Avoid one enormous duplicate stream from every layer.

---

### Scenario 6 — Security-sensitive application

A developer wants to log every request and response "for debugging."

**Reasoning**

Do not adopt that policy blindly.

First classify the data.

Use:

```text
safe metadata
allowlisted fields
redaction
```

and consider whether full request/response recording belongs in a separate controlled system rather than ordinary application logs.

---

### Scenario 7 — Multi-module application

Modules independently call:

```python
logging.basicConfig(...)
```

**Problem**

Configuration ownership becomes unclear.

**Better**

```text
application startup
    ↓
configure logging
    ↓
modules call getLogger(__name__)
```

---

## 44. Debugging Scenarios

### Scenario 1 — No `DEBUG` messages

**Symptom**

```python
logger.debug("Parsing details")
```

never appears.

**Diagnosis**

Check the effective logging level.

If configured at `INFO`, `DEBUG` is below the threshold.

**Fix**

For local debugging:

```python
logging.basicConfig(level=logging.DEBUG)
```

Do not automatically enable `DEBUG` in production.

---

### Scenario 2 — Same message appears twice

**Symptom**

```text
ERROR app.service Failed
ERROR app.service Failed
```

**Likely causes**

- multiple handlers;
- child and parent handlers;
- propagation.

**Debug approach**

Inspect:

```python
logger.handlers
logger.propagate
```

and ancestor logger configuration.

---

### Scenario 3 — Traceback is missing

**Code**

```python
try:
    int("abc")
except ValueError:
    logger.error("Parsing failed")
```

**Problem**

The traceback is not included by default.

**Fix**

```python
try:
    int("abc")
except ValueError:
    logger.exception("Parsing failed")
```

---

### Scenario 4 — Secret appears in logs

**Symptom**

A token was found in collected logs.

**Immediate engineering response**

```text
stop logging the value
replace the logging statement
treat exposed credential as potentially compromised
rotate/revoke if appropriate
review where the value was emitted
```

Do not assume deleting the latest log line fixes copies that may already exist.

---

### Scenario 5 — Logging is too noisy

**Symptom**

Millions of records produce huge log volume.

**Diagnosis**

Look for:

```text
tight-loop debug statements
per-item info logs
duplicate errors
unnecessary payloads
```

**Fix**

Aggregate:

```text
records processed
failures
batch counts
timing
milestones
```

---

### Scenario 6 — Application configures logging multiple times

**Symptom**

Each restart or operation adds another handler.

**Diagnosis**

Find functions that call:

```python
logger.addHandler(...)
```

repeatedly.

**Fix**

Move configuration to a single application startup boundary.

---

### Scenario 7 — Logging breaks because `extra` is incomplete

**Code**

```python
formatter = logging.Formatter(
    "%(levelname)s job_id=%(job_id)s %(message)s"
)

logger.info("Started")
```

**Problem**

The formatter expects `job_id`, but the record does not contain it.

**Better**

```python
logger.info(
    "Started",
    extra={"job_id": "42"},
)
```

or remove `job_id` from the formatter if it is not universally available.

**Lesson**

`extra` creates a logging record schema expectation.

---

### Scenario 8 — Error is logged repeatedly

**Symptom**

One failure creates five stack traces.

**Diagnosis**

Multiple layers are logging the same exception.

**Fix**

Choose intentional logging boundaries.

---

## 45. Knowledge Check

Try to answer these before reading the answers.

### Question 1

What is the main purpose of logging?

### Question 2

When is `print()` still appropriate?

### Question 3

Which standard level represents detailed diagnostics?

### Question 4

What does `logging.getLogger(__name__)` accomplish?

### Question 5

What is a handler?

### Question 6

What is a formatter?

### Question 7

What is propagation?

### Question 8

Why can a child logger create duplicate output?

### Question 9

When should `logger.exception()` normally be used?

### Question 10

Why is `logger.info(f"user={user_id}")` often less preferable to:

```python
logger.info("user=%s", user_id)
```

### Question 11

Why can logging an entire payload be dangerous?

### Question 12

Why should API keys not be logged?

### Question 13

What information is useful for correlating events?

### Question 14

Why is `DEBUG` not a guarantee that data is private?

### Question 15

Where should application logging configuration normally live?

### Question 16

How can you test logging with `pytest`?

### Question 17

What should you inspect when messages appear twice?

### Question 18

Why can too much logging itself become a production problem?

### Question 19

What should be logged for an AI inference request?

### Question 20

What is the most important safety rule about sensitive logging?

### Answer Key

**1.** Logging records useful runtime events for diagnosis, operations, and understanding application behavior.

**2.** User-facing CLI output, explicit program results, or temporary experimentation.

**3.** `DEBUG`.

**4.** It returns a named logger associated with the module namespace.

**5.** A destination-oriented component that dispatches log records.

**6.** A component that controls the rendered layout of log records.

**7.** Passing child logger records toward ancestor loggers/handlers.

**8.** Multiple handlers plus propagation can cause the same record to be emitted more than once.

**9.** Inside an exception-handling context when traceback information is useful.

**10.** The logging API can defer ordinary interpolation until output is needed.

**11.** Payloads may be huge and may contain secrets or confidential information.

**12.** Logs may be collected, copied, retained, or accessed by systems and people not intended to possess credentials.

**13.** Request IDs, job IDs, operation names, and other safe correlation identifiers.

**14.** Production may enable or collect debug logs, and debug messages can still expose sensitive data.

**15.** At an application startup/boundary where logging ownership is clear.

**16.** Use a tool such as `caplog` to assert meaningful log behavior.

**17.** Logger hierarchy, handlers, propagation, and repeated configuration.

**18.** Storage, CPU, I/O, searchability, signal-to-noise, and operational workload can all suffer.

**19.** Safe metadata such as request ID, model, status, latency, retry count, and operation.

**20.** Do not log sensitive values unless there is a specific, controlled reason and the application has an approved handling strategy; the safer default is not to log them.

---

## 46. Final Mental Model

Logging is operational evidence produced by software.

```text
Application code
      ↓
Logger
      ↓
Level decision
      ↓
LogRecord
      ↓
Filters / propagation
      ↓
Handlers
      ↓
Formatter
      ↓
Destination
```

### What each layer means

**Application code**

Says:

```text
"Something happened."
```

**Logger**

Identifies the logging source and severity.

**LogRecord**

Carries the event information.

**Filters**

Provide additional rules about which records should continue.

**Handlers**

Decide where records are sent.

**Formatter**

Decides how the records are rendered.

**Destination**

Could be:

```text
console
file
other application-managed destination
```

### Good logging

```text
useful
+
contextual
+
appropriately leveled
+
searchable
+
safe
+
actionable
+
not excessively noisy
```

### Bad logging

```text
huge payloads
+
secrets
+
duplicate events
+
meaningless messages
+
wrong severity
+
missing context
+
unbounded volume
```

### The operational questions a good log should help answer

```text
What happened?
When?
Where?
For which operation?
For which safe identifier?
At what severity?
What was the outcome?
What should the operator do next?
```

### The most important security question

```text
Could this log line reveal something
the log reader does not need to know?
```

If the answer is yes, redesign it.

### The final mental model

```text
Good logs do not describe every internal detail.

Good logs preserve the important operational story.
```

---

## 47. Completion Checklist

### Fundamentals

- [ ] I understand why logging exists.
- [ ] I understand the difference between logging and `print()`.
- [ ] I know when `print()` remains appropriate.
- [ ] I understand log severity levels.
- [ ] I can create a named logger.

### Logging API

- [ ] I understand `getLogger()`.
- [ ] I understand `basicConfig()`.
- [ ] I understand `debug()`.
- [ ] I understand `info()`.
- [ ] I understand `warning()`.
- [ ] I understand `error()`.
- [ ] I understand `exception()`.
- [ ] I understand `critical()`.
- [ ] I understand the role of `Logger`.
- [ ] I understand `LogRecord`.
- [ ] I understand handlers.
- [ ] I understand `StreamHandler`.
- [ ] I understand `FileHandler`.
- [ ] I understand formatters.
- [ ] I understand filters.
- [ ] I understand propagation.

### Exception handling

- [ ] I know when to use `logger.exception()`.
- [ ] I understand traceback logging.
- [ ] I understand that logging does not replace error handling.
- [ ] I understand when exceptions should be propagated.

### Useful context

- [ ] I can include a job or request identifier.
- [ ] I can include attempt counts.
- [ ] I can include operation names.
- [ ] I can include timing and counts where useful.

### Safety

- [ ] I know not to log passwords.
- [ ] I know not to log API keys.
- [ ] I know not to log access tokens.
- [ ] I know not to print the complete environment.
- [ ] I understand why prompts/responses may be sensitive.
- [ ] I can create safe configuration diagnostics.
- [ ] I can avoid unnecessary sensitive identifiers.

### Production practices

- [ ] I can configure logging centrally.
- [ ] I understand logger hierarchy.
- [ ] I can diagnose duplicate logs.
- [ ] I understand log noise.
- [ ] I understand structured logging conceptually.
- [ ] I can test meaningful logging behavior.
- [ ] I can debug an operational problem using logs.

### Applied AI

- [ ] I can design safe inference logs.
- [ ] I understand safe model/tool metadata.
- [ ] I understand why full prompts should not automatically be logged.
- [ ] I understand retry logging.
- [ ] I can separate operational logs from sensitive AI payloads.

### Final capability test

Given a production Python application, I should now be able to answer:

```text
What events matter?
What severity should each event use?
What context is needed?
What data is unsafe?
Where should logs go?
Who configures them?
How will failures be investigated?
How will duplicate logs be prevented?
How will logging volume be controlled?
How will logging behavior be tested?
```

---

## 48. Important Teaching Rules

### Rule 1 — Simple first

Start with:

> "A log is a record of something important that happened."

Only then introduce:

```text
Logger
LogRecord
Handler
Formatter
Filter
Propagation
```

### Rule 2 — No unexplained code

Do not dump:

```python
dictConfig(...)
```

or a large custom handler without first explaining why it exists.

### Rule 3 — Teach the why

Every important API should answer:

```text
Why would an engineer use this?
```

### Rule 4 — Teach internal mechanics

The learner should be able to trace:

```text
logger.info(...)
    ↓
level check
    ↓
LogRecord
    ↓
handlers
    ↓
formatter
    ↓
destination
```

### Rule 5 — Show bad vs good

For production practices:

```text
Bad
 ↓
Why it is bad
 ↓
Better
 ↓
Why it is better
```

### Rule 6 — Treat logs as a data boundary

Logs can contain:

```text
secrets
personal data
confidential data
customer content
AI prompts
AI outputs
```

Therefore logging is part of application safety.

### Rule 7 — Do not overreach

This chapter does not attempt to teach complete:

```text
Kubernetes logging
cloud logging products
distributed tracing
OpenTelemetry implementation
ELK deployment
metrics architecture
```

Those can be learned later.

### Rule 8 — Production mindset

Keep returning to:

```text
debuggability
reliability
maintainability
security
operability
```

---

## 49. Quality Standard

The finished chapter should leave the learner able to reason about logging, not merely repeat method names.

It should be:

- beginner-friendly;
- technically accurate;
- progressive;
- Python-specific;
- detailed;
- production-oriented;
- practical;
- security-aware;
- useful for CLI work;
- useful for data pipelines;
- useful for Applied AI Engineering;
- suitable for future interviews and architecture discussions.

Avoid:

- shallow definitions;
- unexplained jargon;
- insecure examples;
- excessive theory;
- massive unexplained code;
- logging everything at `ERROR`;
- treating `print()` as universally forbidden;
- treating `DEBUG` as a security boundary;
- logging secrets;
- unnecessary payload logging;
- duplicate logging;
- vendor-specific observability implementation.

### Current Python version note

The core APIs in this chapter are from Python's standard `logging` package and are stable across modern Python 3.x versions, but exact defaults and surrounding platform behavior should always be verified against the Python version used by a production application.

---

## 50. Self-Review Before Finishing

### Coverage review

- [x] Logging introduced from the beginner level.
- [x] Logging vs `print()` covered.
- [x] Python `logging` module covered.
- [x] First working example included.
- [x] Log levels explained.
- [x] Logger objects explained.
- [x] Logger hierarchy explained.
- [x] Propagation explained.
- [x] Handlers explained.
- [x] Formatters explained.
- [x] Filters explained.
- [x] Internal flow explained.
- [x] `basicConfig()` explained.
- [x] `getLogger()` explained.
- [x] Major logger methods explained.
- [x] Exception logging explained.
- [x] Traceback logging explained.
- [x] Lazy formatting explained.
- [x] Contextual logging explained.
- [x] Safe logging explained.
- [x] Sensitive data risks explained.
- [x] Structured logging introduced.
- [x] Logging configuration explained.
- [x] Module/package logging explained.
- [x] CLI logging explained.
- [x] Data-pipeline logging explained.
- [x] Applied AI logging explained.
- [x] Retry/failure logging explained.
- [x] Noise reduction explained.
- [x] Anti-patterns explained.
- [x] Testing explained.
- [x] Debugging explained.
- [x] Production design explained.
- [x] Complete example included.
- [x] Exercises included.
- [x] Mini-project included.
- [x] Interview questions included.
- [x] Architecture questions included.
- [x] Debugging scenarios included.
- [x] Knowledge check included.
- [x] Final mental model included.
- [x] Completion checklist included.

### API review

Important APIs introduced in the chapter are explained rather than silently used, including:

```text
logging.basicConfig
logging.getLogger
logging.debug
logging.info
logging.warning
logging.error
logging.exception
logging.critical
Logger
LogRecord
Handler
StreamHandler
FileHandler
Formatter
Filter
Logger.setLevel
Logger.addHandler
Logger.removeHandler
Logger.addFilter
Logger.removeFilter
Logger.propagate
Logger.disabled
Logger.isEnabledFor
Handler.setLevel
Handler.setFormatter
Handler.addFilter
Handler.removeFilter
```

### Safety review

- [x] No real credentials.
- [x] No real API keys.
- [x] No private tokens.
- [x] Unsafe examples are clearly identified.
- [x] AI prompts/responses are treated as potentially sensitive.
- [x] Configuration examples use safe placeholders.
- [x] Sensitive payload logging is discouraged.

### Practicality review

- [x] Runnable examples included.
- [x] Bad-vs-good examples included.
- [x] Exercises include solutions.
- [x] Testing examples included.
- [x] Production scenarios included.
- [x] Applied AI examples included.

### Production review

The learner should be able to move from:

```text
"how do I print a message?"
```

to:

```text
"what operational evidence should this component emit,
at what level, with what safe context, to which handler,
and how will it be used during incident investigation?"
```

That is the intended progression.

---

## 51. Final File-Scope Verification

This chapter is intended to modify only:

```text
10-Production-Habits-for-Python-Programs/02-safe-and-useful-logging.md
```

The source specification explicitly requires:

```text
no other Markdown files
no Python files
no exercise files
no answer-key files
no supporting files
no folder changes
```

The working artifact was written only to the requested target path in the execution environment.

### Final engineering check

Before considering this chapter complete:

```text
Read the file
    ↓
Check the headings
    ↓
Check the examples
    ↓
Check the API coverage
    ↓
Check the safety guidance
    ↓
Check the exercises
    ↓
Check the production example
    ↓
Check the final mental model
```

The core lesson is:

> **Good production logging is not "log everything." It is the deliberate creation of useful operational evidence that is correctly leveled, sufficiently contextual, safe to expose, and valuable during diagnosis.**

### Reference note

For exact API behavior and version-specific details, consult the Python standard-library documentation for `logging`, especially the Logging HOWTO and reference documentation.
