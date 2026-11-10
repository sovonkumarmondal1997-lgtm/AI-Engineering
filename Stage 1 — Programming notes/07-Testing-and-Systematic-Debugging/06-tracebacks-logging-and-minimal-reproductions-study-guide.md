# Tracebacks, Logging, and Minimal Reproductions — Complete Study Guide

**Stage 1 — Programming & Computational Thinking**  
**Module 07 — Testing and Systematic Debugging**  
**Lesson 06**

This guide follows the attached `06-tracebacks-logging-and-minimal-reproductions(1).md`. It teaches the chapter's concepts and representative code examples, reviews the roadmap and current learning level, solves all 20 coding exercises, covers all 12 debugging labs, and includes the mini-project, interview/architecture review, checklist, and knowledge checks.

---

# Part A — Complete Lesson Summary and Teaching Notes

## 1. Errors, bugs, exceptions, failures, and crashes

These terms are related but not interchangeable:

- **Error:** broad term for software not behaving as intended.
- **Bug:** defect in the software.
- **Exception:** Python object representing an exceptional runtime condition.
- **Failure:** observable behavior that violates an expectation.
- **Crash:** process/application terminates unexpectedly or cannot continue its intended work.

Example:

```python
def divide(a: int, b: int) -> float:
    return a / b

divide(10, 0)  # raises ZeroDivisionError
```

The exception signals the problem. The underlying bug may be that the caller failed to validate the divisor. Not every bug raises an exception:

```python
def discount(price: int) -> int:
    return price * 2  # wrong business logic, but no exception
```

Likewise, a business operation may fail by returning a rejection result rather than raising. In production, failures may be detected through exceptions, failed requests, incorrect outputs, timeouts, health checks, metrics, logs, traces, and data-quality alerts.

Ask four separate questions: **What happened? Why? What was expected? What evidence supports the explanation?**

## 2. Python exception handling

An exception tells Python that normal execution cannot continue in the current way. Python searches outward for a matching handler. If none is found, the exception remains uncaught and may terminate the program.

The main constructs are:

```python
def parse_age(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise ValueError("age must be numeric")
    else:
        return number
```

- `try`: code that may raise.
- `except`: handles a matching exception.
- `else`: runs only if the `try` block completed without an exception.
- `finally`: cleanup that should run whether execution succeeds or raises.
- `raise`: explicitly raises or re-raises an exception.

Example of cleanup:

```python
def use_resource(resource):
    try:
        resource.open()
        return resource.read()
    finally:
        resource.close()
```

Do not hide defects with `except Exception: pass`. Catch an exception where the code can make a meaningful decision: recover, translate, retry, report, or terminate. A low-level function should normally raise a useful exception; a service may translate it into a domain exception; an application boundary decides how to report it.

## 3. Common built-in exceptions

| Exception | Meaning | Example / investigation |
|---|---|---|
| `ValueError` | Correct type, invalid value | `int("abc")`; inspect value and validation |
| `TypeError` | Inappropriate type for operation | `1 + "2"`; inspect types |
| `KeyError` | Missing dictionary key | `data["id"]`; inspect schema |
| `IndexError` | Sequence index out of range | `[1][2]`; inspect length/index |
| `AttributeError` | Object lacks attribute | `None.name`; inspect object type |
| `NameError` | Name not defined | misspelled/unavailable variable; inspect scope |
| `FileNotFoundError` | Path does not exist | inspect path and working directory |
| `PermissionError` | OS denies operation | inspect permissions/identity |
| `ZeroDivisionError` | Division by zero | inspect input constraints |
| `ImportError` | Import operation failed | inspect symbol/package version |
| `ModuleNotFoundError` | Module cannot be found | inspect environment/dependencies |
| `RuntimeError` | Other runtime problem | inspect state and API contract |
| `OSError` | OS-level failure | inspect resource and OS context |

An exception type is a clue, not a complete diagnosis. For `ValueError`, ask which value, where it came from, which function received it, and why it was invalid.

## 4. Tracebacks: what they contain and how to read them

A **traceback** is Python's diagnostic representation of the function-call path associated with an exception. It commonly shows filenames, line numbers, function names, source lines, and the final exception type/message.

Example:

```text
Traceback (most recent call last):
  File "main.py", line 20, in <module>
    process_order(order)
  File "service.py", line 14, in process_order
    total = calculate_total(order)
  File "pricing.py", line 9, in calculate_total
    return parse_price(order["price"])
  File "pricing.py", line 4, in parse_price
    return int(value)
ValueError: invalid literal for int() with base 10: 'free'
```

Read it systematically:

1. Identify the final exception type: `ValueError`.
2. Read the message: `int()` could not parse the supplied value.
3. Identify the immediate failure frame: `parse_price`, at `int(value)`.
4. Follow callers: `calculate_total → process_order → main`.
5. Identify the bad input: `"free"`.
6. Investigate why it reached the parser: missing validation, malformed source data, database corruption, changed API schema, or transformation defect.

“Most recent call last” means the most recent frame is near the bottom of the frame list. The final exception line gives the category/message; the frames show how execution arrived there. Do not inspect only the bottom line.

A traceback and live debugger call stack are related but different:

- **Live call stack:** active frames while execution is paused; a debugger lets you inspect local variables in those frames.
- **Traceback:** record of the call path associated with an exception.

A traceback identifies where execution failed, not necessarily the root cause. The bad value may have been created much earlier.

## 5. Exception propagation, chaining, context, and cause

If a function raises an exception and does not handle it, Python unwinds outward through its callers until it finds a matching handler or the exception becomes uncaught.

```python
def a():
    b()

def b():
    c()

def c():
    raise ValueError("bad value")

a()
```

If `b()` catches `ValueError`, propagation stops and the function may recover. A handler can recover, transform, add context, log, re-raise, or accidentally hide the failure.

**Exception chaining** preserves a lower-level failure while adding a higher-level meaning:

```python
def load_transaction(value: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError("could not load transaction amount") from exc
```

`raise NewError(...) from exc` sets an explicit cause. If a new exception is raised while another is being handled without `from`, Python records the earlier exception as context. These relationships help engineers understand both the low-level failure and the domain-level failure.

`raise ... from None` suppresses display of the automatically chained context:

```python
try:
    int("abc")
except ValueError:
    raise ValueError("invalid transaction amount") from None
```

Use this only when intentionally hiding an implementation detail at an abstraction boundary. Do not suppress diagnostic evidence engineers will need.

## 6. Traceback objects and the `traceback` module

An exception can reference a traceback object, which in turn references frames. Traceback objects retain runtime references; keeping them for a long time can keep frame-local objects alive. If you need a durable report rather than live runtime state, prefer extracted summaries.

Important standard-library APIs:

```python
import traceback

try:
    int("abc")
except ValueError:
    traceback.print_exc()
```

- `traceback.print_exc()` prints the currently handled exception and its traceback. More useful than `print(exc)` when you need the call path.
- `traceback.format_exc()` returns the current handled exception traceback as formatted text:

```python
try:
    int("abc")
except ValueError:
    text = traceback.format_exc()
```

- `traceback.format_exception(exc)` formats exception information and returns an iterable/list of strings in current Python versions:

```python
try:
    int("abc")
except ValueError as exc:
    text = "".join(traceback.format_exception(exc))
```

- `traceback.extract_tb(exc.__traceback__)` extracts exception traceback entries as a `StackSummary` of `FrameSummary` objects:

```python
try:
    int("abc")
except ValueError as exc:
    summary = traceback.extract_tb(exc.__traceback__)
    for frame in summary:
        print(frame.filename, frame.lineno, frame.name, frame.line)
```

- `traceback.extract_stack()` extracts the **current** execution stack, even without an exception.
- `traceback.print_tb(exc.__traceback__)` prints traceback entries only, a lower-level view than printing the full exception.

Do not confuse `extract_tb()` (exception traceback) with `extract_stack()` (current stack). Formatted traceback strings are presentation text, not a stable machine-readable API. For machine processing, retain structured fields such as exception type, message, filename, line, request ID, service, and version.

## 7. Custom exceptions and exception design

A custom exception communicates a meaningful application/domain failure:

```python
class TransactionError(Exception):
    pass

class InvalidTransactionError(TransactionError):
    pass

class InsufficientFundsError(TransactionError):
    pass
```

A caller can catch a specific subclass or the shared `TransactionError` base. Create custom exception types when callers, tests, logs, or API behavior need to distinguish the failure. Do not create many classes with no semantic distinction.

Prefer:

```python
raise InsufficientFundsError(
    "transfer amount exceeds available balance"
)
```

over `raise Exception("failed")`.

Custom exceptions can carry structured context:

```python
class InsufficientFundsError(Exception):
    def __init__(self, available: int, requested: int):
        super().__init__("insufficient funds")
        self.available = available
        self.requested = requested
```

Never put passwords, tokens, full request payloads, or other secrets into exception messages. Prefer safe identifiers such as transaction ID, request ID, field name, or business error code.

## 8. Logging: purpose and architecture

Logging systematically records application events and diagnostic context. `print()` remains useful for small scripts, experiments, education, and quick local investigation. Logging is preferable for long-lived operational diagnostics because it supports severity levels, named sources, filtering, multiple destinations, formatting, configuration, exception information, and context.

The logging pipeline is:

```text
application code → Logger → LogRecord → Handler → destination
                                      ↘ Formatter controls presentation
```

Import and create a module-level named logger:

```python
import logging
logger = logging.getLogger(__name__)
```

`__name__` gives the logger a name aligned with the module/package. Obtain loggers through `getLogger()` rather than directly instantiating `Logger`. Repeated requests for the same name return the same logger.

Standard severity levels:

| Level | Intended use |
|---|---|
| `DEBUG` | detailed developer diagnostics |
| `INFO` | normal operation and meaningful milestones |
| `WARNING` | unexpected but recoverable condition |
| `ERROR` | an operation failed |
| `CRITICAL` | severe issue threatening continued operation |

Example:

```python
logger.debug("validated %d records", len(records))
logger.info("transaction accepted")
logger.warning("retrying external service")
logger.error("transaction processing failed")
logger.critical("required configuration is unavailable")
```

Choose a level by operational meaning; do not label every event `ERROR`.

## 9. Logger hierarchy, root logger, handlers, formatters, and LogRecord

Logger names form a hierarchy:

```text
root
└── app
    ├── app.api
    ├── app.database
    └── app.pipeline
```

Child records can propagate to ancestor handlers. `logger.propagate` controls this and defaults to `True`. Logger levels and handler levels both matter: the logger's effective level filters records before they are passed to handlers; each receiving handler then applies its own level. Attaching handlers to both child and ancestor loggers without understanding propagation can duplicate output.

The **root logger** is the top-level logger. A common application pattern is to configure logging at the application entry point and use named loggers in modules.

A **handler** selects a destination:
- `StreamHandler` writes to a stream (normally stderr by default).
- `FileHandler` writes to a file.
- `logging.handlers` provides rotating handlers.

A **formatter** controls output layout:

```python
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
)
handler.setFormatter(formatter)
```

Useful fields include `asctime`, `levelname`, `name`, `message`, `module`, `funcName`, and `lineno`.

A **LogRecord** represents one event and carries logger name, level, message, source file/line/function, timestamp, exception details, and custom fields. Add context with `extra`:

```python
logger.info(
    "transaction accepted",
    extra={"transaction_id": "tx-123"},
)
```

Custom keys must not collide with built-in LogRecord attributes, and formatter fields must exist on records.

## 10. Logging exceptions: `logger.exception`, `exc_info`, and `stack_info`

Inside an exception handler:

```python
try:
    process_transaction()
except Exception:
    logger.exception("transaction processing failed")
    raise
```

`logger.exception()` logs at `ERROR` and includes the currently handled exception information. Logging alone is not handling: deliberately decide whether to handle, re-raise, translate, retry, or terminate.

`exc_info=True` is an explicit option for attaching exception information, useful when you need another level:

```python
try:
    parse()
except ValueError:
    logger.warning("invalid input", exc_info=True)
```

`stack_info=True` is different. It records the **current stack leading to the logging call**, even if no exception occurred:

```python
logger.debug("checkpoint reached", stack_info=True)
```

Mental model:

```text
exc_info=True  → what exception happened and its traceback?
stack_info=True → how did execution reach this logging call?
```

Stack information can increase log volume; use it only when useful.

## 11. Logging context and structured logging

Useful safe context includes `request_id`, `transaction_id`, `job_id`, `batch_id`, service/version, operation, and resource identifier. Context lets engineers identify which request, transaction, job, or subsystem is involved.

Do not casually log passwords, API keys, access tokens, private keys, session tokens, authorization headers, unnecessary personal data, or unnecessary financial details. Avoid dumping complete headers or payloads. User-controlled newlines, control characters, and unbounded text can cause log injection or misleading output. Structured logging reduces ambiguity but does not automatically make sensitive content safe.

**Structured logging** stores explicit machine-queryable fields rather than relying only on prose:

```text
event=transaction_failed
transaction_id=tx-900
reason=insufficient_funds
```

Conceptually, the same event might be JSON:

```json
{
  "event": "transaction_failed",
  "transaction_id": "tx-900",
  "reason": "insufficient_funds"
}
```

Structured fields help centralized search, dashboards, alerting, correlation, and incident analysis. A diagnostic record should be useful, minimal, and safe.

## 12. Logging configuration and application/module separation

`logging.basicConfig()` is a simple root-logger configuration mechanism:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
```

Important nuance: `basicConfig()` normally does nothing if the root logger already has handlers, unless the relevant reconfiguration option is used. Do not assume it always overwrites existing setup.

In modules:

```python
logger = logging.getLogger(__name__)
logger.info("processing started")
```

At the application boundary, configure levels, handlers, destinations, filters, and format. Reusable libraries should emit records, not unexpectedly call `basicConfig()` and reconfigure the host application.

A basic complete example:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

logger.debug("debug details")
logger.info("application started")
logger.warning("cache miss")
logger.error("operation failed")
logger.critical("critical subsystem unavailable")
```

With `INFO` configured, `DEBUG` is normally filtered out in this simple setup.

## 13. File logging, rotation, performance, and level strategy

A file handler writes to a file:

```python
handler = logging.FileHandler("application.log", encoding="utf-8")
logger = logging.getLogger("app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
))
```

Consider file location, permissions, disk capacity, rotation, retention, encoding, and deployment environment. Production systems often ship logs to centralized collection rather than relying only on ephemeral local files.

Size-based rotation:

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "application.log",
    maxBytes=1_000_000,
    backupCount=3,
)
```

`TimedRotatingFileHandler` rotates by time. Rotation prevents unbounded growth but must be paired with retention, archival, access control, central collection, and cost policies.

Logging costs CPU, I/O, and storage. Prefer lazy formatting:

```python
logger.debug("User %s processed", user_id)
```

rather than eager f-strings:

```python
logger.debug(f"User {user_id} processed")
```

Lazy formatting can avoid message formatting when disabled, but function arguments are still evaluated before the logging call. For expensive diagnostics:

```python
if logger.isEnabledFor(logging.DEBUG):
    payload_summary = expensive_summary(payload)
    logger.debug("payload=%s", payload_summary)
```

Use selectively. Typical strategy: DEBUG for detailed diagnostics, INFO for milestones, WARNING for recoverable unexpected conditions, ERROR for failed operations, CRITICAL for severe system-level problems.

## 14. Logging and exception-handling patterns; duplicate logs

Three patterns:

**Log and re-raise** when this layer adds meaningful context but the caller still owns handling:

```python
try:
    process()
except SpecificError:
    logger.warning("processing failed; caller will handle it")
    raise
```

**Log and handle** only when recovery is deliberate:

```python
try:
    optional_operation()
except SpecificError:
    logger.warning("optional operation failed")
```

**Translate** when a lower-level exception should become a domain-level exception:

```python
try:
    process()
except ValueError as exc:
    raise DomainError("invalid transaction") from exc
```

Avoid logging the same propagated exception at repository, service, API, and gateway layers without adding new information. Duplicate tracebacks inflate log volume, storage cost, error counts, and incident noise. Let lower layers raise; translate where appropriate; log at a suitable handling/reporting boundary. This is a design principle, not an absolute one-log-only rule.

Combine traceback and logging at the appropriate boundary:

```python
try:
    process_transaction()
except Exception:
    logger.exception("transaction processing failed")
    raise
```

A useful record may contain timestamp, level, logger, request ID, transaction ID, exception type/traceback, and application version.

## 15. Minimal Reproducible Examples (MREs)

A **Minimal Reproducible Example** is the smallest practical program, input, and environment that still demonstrates the defect. Minimal does not mean forcing everything into one line. Remove everything that does not contribute to reproducing the failure.

For example, a large service may reduce to:

```python
record = {"amount": "INVALID"}
parse_amount(record["amount"])
```

Do not remove so much that the defect disappears. Every successful reduction gives evidence that the removed component was not necessary.

A systematic reduction:

```text
capture symptom → input → environment → failing boundary
→ remove unrelated modules/data/dependencies
→ control time/randomness
→ reproduce with smallest practical case
```

Example: HTTP → auth → middleware → service → database → queue → pricing → parser may reduce to `parse_amount("bad-value")`. If the parser alone does not reproduce it, restore layers until the necessary condition returns. An MRE is a diagnostic laboratory, not necessarily the final fix.

### MREs by problem type

- **Traceback:** first test whether the function at the failure frame reproduces the defect; restore callers only if needed.
- **Logging:** remove concurrent requests, retry storms, unrelated jobs, and noisy dependencies. More log lines do not equal more signal.
- **Test failure:** whole suite → one file → one test → one parameter → one fixture path → minimal input. Example: `pytest tests/test_parser.py::test_parse_transaction -q`.
- **Data pipeline:** identify affected output/partition, extract representative records, create a small fixture, then reproduce parse → validate → transform. Do not step through millions of records.
- **API:** one endpoint → one request → minimal payload. Capture method, path, safe headers, query, body, status, response, version. Never copy production credentials into tickets or shell history.
- **AI/LLM:** minimal prompt/input/context, controlled settings, minimal tools, model/provider/version, application version, retrieved context, tool responses, raw response only if safe. Exact replay may not be guaranteed.
- **Agentic AI:** minimal request/state/tool set with controlled tool responses. Capture tool selected, safe arguments, response, state before/after, iteration count, final result—not hidden chain-of-thought.

## 16. Reproducibility, environment capture, and bug reports

A failure may depend on input, code version, dependency versions, configuration, OS, Python version, locale, timezone, database state, network, time, randomness, and external services. “Works on my machine” often means one or more of these differ.

Capture safe, relevant information:

```text
Python version
OS
package versions
application version/commit
configuration identifiers
command used
input
expected output
actual output
traceback
relevant logs
```

`python --version` is a simple starting point. Do not paste all environment variables (`env`) into a public issue: they often contain credentials. Select safe variables only. Version identifiers such as Git commit, container image, dependency lock, and model/configuration version are valuable.

A high-quality bug report includes a precise title, environment, reproducible steps, expected result, actual result, traceback, relevant logs, suspected regression window, and MRE. “It doesn't work” is not actionable. A good report lets another engineer answer what happened, where, how to reproduce it, and what should have happened.

## 17. Integrated workflow, decision tree, observability, and production debugging

Combined workflow:

```text
symptom → reproduce → traceback → logs → identify code path
→ minimize → debugger if useful → root cause → fix → regression test
```

Use the right tool:
- Traceback when an exception occurred.
- Logging for historical context and intermittent/out-of-session failures.
- MRE when the application is too large to reason about.
- Debugger when the problem reproduces locally and live state matters.
- Tests for repeatable verification and regression protection.

Decision tree:

```text
Exception?
├─ Yes → read traceback → identify failure frame/call chain
└─ No → is behavior wrong?
         ├─ Yes → reproduce
         │        ├─ reproducible → debugger/test
         │        └─ not reproducible → logs/environment
         └─ No → continue observing
Too complex? → create MRE
Fixed? → add regression protection
```

**Observability** makes internal behavior inferable from external signals:
- Logs = discrete events.
- Metrics = numerical measurements/trends.
- Traces = request/workflow path across components.
- Tracebacks = detailed exception path.
- Debugger = interactive local inspection.

A log is not automatically a distributed trace; a traceback is not a production trace.

In production, prefer structured/centralized logs, metrics, distributed traces, correlation IDs, deployment metadata, exception monitoring, and safe snapshots/fixtures. Do not casually attach an interactive debugger: it can pause traffic, expose sensitive memory, execute arbitrary code, mutate state, and change timing. Use access controls, redaction, retention, auditability, and reproduce outside production where possible.

## 18. Complete realistic order-processing example

The lesson deliberately creates a bug by subtracting the discount twice:

```python
import logging
logger = logging.getLogger(__name__)

class Order:
    def __init__(self, order_id: str, price: int, quantity: int):
        self.order_id = order_id
        self.price = price
        self.quantity = quantity

def calculate_total(order: Order) -> int:
    subtotal = order.price * order.quantity
    discount = 10
    total = subtotal - discount
    total = total - discount  # deliberate defect
    logger.debug("calculated total for order %s", order.order_id)
    return total
```

For price 50 and quantity 2, subtotal is 100; discount is 10; expected total is 90 but actual is 80.

Diagnostic process:
1. Reproduce with an assertion.
2. Add a temporary `breakpoint()` before the subtraction.
3. Inspect `subtotal=100`, `discount=10`.
4. Step over the first subtraction: `total=90`.
5. Step over the second: `total=80`.
6. Hypothesis: discount is applied twice.
7. Verify by reading both subtraction lines.
8. Fix by subtracting once: `return subtotal - discount`.
9. Add a regression test expecting 90.
10. Add safe contextual logging with `order_id`; do not log a full order payload if it contains customer data.

## 19. Complete transaction diagnostics mini-project

Project layout:

```text
transaction_lab/
├── transaction.py
├── processor.py
├── main.py
└── tests/
    └── test_transaction.py
```

`transaction.py`:

```python
class InvalidTransactionError(Exception):
    pass

def parse_amount(value: str) -> int:
    try:
        return int(value.strip())
    except ValueError as exc:
        raise InvalidTransactionError(
            "transaction amount is invalid"
        ) from exc
```

This translates low-level `ValueError` into a domain exception while preserving the cause.

`processor.py`:

```python
import logging
from transaction import parse_amount

logger = logging.getLogger(__name__)

def process_transaction(transaction_id: str, amount_text: str) -> int:
    logger.info(
        "processing transaction %s",
        transaction_id,
        extra={"transaction_id": transaction_id},
    )
    amount = parse_amount(amount_text)
    if amount <= 0:
        raise ValueError("amount must be positive")
    logger.info(
        "transaction accepted %s",
        transaction_id,
        extra={"transaction_id": transaction_id},
    )
    return amount
```

It logs safe transaction context, parses, validates positivity, and returns the amount.

`main.py`:

```python
import logging
from processor import process_transaction

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

def main() -> None:
    try:
        process_transaction("tx-1", "not-a-number")
    except Exception:
        logging.getLogger(__name__).exception(
            "transaction processing failed"
        )
        raise

if __name__ == "__main__":
    main()
```

Run from the `transaction_lab/` directory because imports are plain module imports:

```bash
cd transaction_lab
python main.py
python -m pytest
```

`python -m pytest` adds the current directory to the import path; a bare `pytest` may fail to import `transaction` without project configuration. The program logs INFO events, then an ERROR record with the chained traceback (`InvalidTransactionError` caused by `ValueError`), and exits non-zero because `main()` re-raises.

Minimal reproduction:

```python
from transaction import parse_amount
parse_amount("not-a-number")
```

Regression test:

```python
import pytest
from transaction import InvalidTransactionError, parse_amount

def test_parse_amount_rejects_invalid_text():
    with pytest.raises(InvalidTransactionError):
        parse_amount("not-a-number")
```

The project deliberately asks you to consider `"1,000"`. Python `int()` does not accept a thousands separator. If the business contract says it should, write the test first:

```python
def test_parse_amount_accepts_thousands_separator():
    assert parse_amount("1,000") == 1000
```

Then implement the behavior. Suggested extensions: request IDs, structured context, API boundary, pipeline adapter, parametrized regression suite, deliberate logging bug, swallowed exception, and an MRE document.

## 20. Technical references and final mental model

The chapter aligns standard-library details with Python 3.14 documentation for `traceback`, `logging`, and `pdb`. Check official documentation for exact signatures and version-specific behavior.

Final workflow:

```text
error → exception? → traceback → read call chain
→ identify failure location → inspect state
→ collect safe log context → reproduce → minimize
→ debugger/experiment → hypothesis → verify root cause
→ fix → tests → regression protection → improve diagnostics
```

Three complementary tools:
- Traceback: how did execution reach the exception?
- Logging: what important events and context happened?
- MRE: what is the smallest environment in which the problem still exists?

A debugger, traceback, large volume of logs, or tiny example does not magically reveal the root cause. The engineer turns evidence into a verified explanation.

---

# Part B — Project Tree and Current-Level Assessment

## 1. Roadmap placement

The uploaded file is **Module 07, Lesson 06 — Tracebacks, Logging, and Minimal Reproductions**:

`Stage 1 — Programming & Computational Thinking / 07-Testing-and-Systematic-Debugging/06-tracebacks-logging-and-minimal-reproductions.md`

The Stage 1 roadmap progresses through computational thinking; Python core language and data types; control flow/functions/scope/errors; problem-solving/collections/algorithmic habits; text files/structured data/CLI; modules/packages/dependencies/code quality; testing and systematic debugging; OOP/data modelling/functional style; advanced production-oriented Python; production habits; advanced data model/object design; metaprogramming; standard library; bytes/binary/advanced text; modern Python; advanced testing; profiling/performance; packaging/distribution; CPython internals; design patterns/API design; visualization/notebooks; secure Python; code reading/refactoring/review; and functions/OOP gap lessons.

Within Module 07:

1. Test Levels: Unit, Integration, and End-to-End — completed.
2. Pytest: Assertions, Fixtures, and Parametrization — completed.
3. Arrange–Act–Assert and Test Design — completed.
4. Boundary, Invalid, and Regression Tests — completed.
5. Debuggers, Breakpoints, and Call Stacks — completed.
6. Tracebacks, Logging, and Minimal Reproductions — current lesson.
7. Mocking and Test Doubles — not started.
8. Module README and practice questions.

## 2. Stage 1 project relevance

The four cumulative projects are:

1. **Personal Expense Ledger CLI** — exercises input validation, calculations, persistence, CLI behavior, and tests.
2. **Log Investigation and Reliability CLI** — directly reinforces log parsing, diagnostic reporting, and reliability investigation.
3. **Data Quality and Transformation Pipeline** — `orders.csv`, `dqpipe` package (`cli.py`, `config.py`, `pipeline.py`, `rules.py`), tests, configuration, and data contract. MREs help isolate malformed records and transformation defects.
4. **Rule-Based Risk Review Engine** — `transactions.csv`, `rules.toml`, `riskreview` package (`cli.py`, `engine.py`, `io.py`, `models.py`, `rules.py`), tests, and golden decision data. Tracebacks, structured logs, safe identifiers, and regression tests help diagnose rule and input failures.

## 3. Current level and scope discipline

You have completed the Python foundations needed here: variables, types, collections, control flow, functions, scope, exceptions, files, paths, CSV/JSON, CLI, streams/exit codes, logging, environment configuration, imports/packages, dependency management, Ruff, type hints, and documentation. In Module 07 you have completed Lessons 01–05, including pytest, fixtures, parametrization, test design, boundaries, regression, breakpoints, stepping, and call stacks.

Your current level is **beginner progressing toward intermediate Python engineering**. This lesson is the natural continuation: it reuses exceptions, functions, modules, logging, pytest, and debugger knowledge rather than requiring a new advanced framework.

The solutions below stay within Python's standard library and pytest already covered. Concepts such as distributed tracing, production observability, async, and agentic AI appear as architecture context, not as a requirement to implement a production observability platform now.

**Current position:** Lesson 06 is being studied. Lesson 07 — Mocking and Test Doubles — is not started and will not be advanced into by this guide.

---

# Part C — All 20 Coding Exercises with Step-by-Step Solutions

## Level 1 — Basic

### 1. Identify the exception

```python
int("abc")
```

**Answer:** `ValueError`.

`int()` accepts a string, so the type is acceptable; `"abc"` is not a valid integer representation. `TypeError` would describe an inappropriate type for the operation.

### 2. Read a traceback

Given `main() → run() → int("abc") → ValueError`, the immediate failure function is `run()` at the line calling `int("abc")`. `main()` is a caller, not the direct failure location. The traceback frames show both.

### 3. `print()` versus traceback

```python
try:
    int("abc")
except ValueError as exc:
    print(exc)
```

This prints mainly the exception message. Better:

```python
import traceback

try:
    int("abc")
except ValueError:
    traceback.print_exc()
```

`print_exc()` includes the call path for the currently handled exception, which helps identify how execution arrived at the failure.

### 4. Create a module-level logger

```python
import logging
logger = logging.getLogger(__name__)
```

`import logging` imports the standard library. `getLogger(__name__)` retrieves a named logger for this module and connects it to the hierarchy. Do not instantiate `Logger` directly.

### 5. Create a minimal reproduction

```python
def parse_amount(value: str) -> int:
    return int(value)

parse_amount("abc")
```

The function preserves the suspected conversion behavior and one failing input. It removes unrelated application modules. Keep only what is necessary to reproduce the same failure.

## Level 2 — Intermediate

### 6. Log an exception and propagate it

```python
try:
    process()
except Exception:
    logger.exception("processing failed")
    raise
```

`try` runs the operation. `except` handles the exception temporarily. `logger.exception()` logs at ERROR with exception information. Bare `raise` re-raises the original exception; it does not silently convert failure into success.

### 7. Explain logger hierarchy

```text
app
├── app.api
└── app.database
```

`app.api` and `app.database` are child loggers under `app`. Their records can propagate to ancestor handlers. This makes centralized configuration possible, but duplicate handler attachment can duplicate output.

### 8. Preserve exception cause

```python
try:
    int("abc")
except ValueError as exc:
    raise RuntimeError("could not parse value") from exc
```

The conversion raises `ValueError`. The handler binds it to `exc`. The new `RuntimeError` adds higher-level meaning. `from exc` explicitly preserves the original cause.

### 9. Log a handled exception at WARNING

```python
try:
    int("abc")
except ValueError:
    logger.warning(
        "invalid numeric input",
        exc_info=True,
    )
```

The `except` catches the conversion error. `warning()` selects WARNING level. `exc_info=True` adds exception/traceback information. Use this when WARNING is the intended severity; `logger.exception()` always uses ERROR.

### 10. Choose safe diagnostic context

Log `transaction_id` and only non-sensitive amount metadata when justified. Do not log `password`. A full request dump may expose credentials or personal/financial data. A stable identifier usually provides enough correlation without disclosing secrets.

## Level 3 — Advanced

### 11. Identify root-cause candidates

For `main → service → repository → int("abc") → ValueError`, plausible causes include:
1. input validation is missing;
2. the database contains malformed data;
3. an upstream API changed its schema or field representation.

The traceback identifies the failure path, not which upstream cause is correct. Logs, source data, and reproduction evidence distinguish them.

### 12. Reduce a pipeline failure

For a 10-million-row ETL job failing on one amount:

1. Identify the failing record.
2. Capture its input representation safely.
3. Extract a tiny fixture.
4. Reproduce the parse/transform path.
5. Remove unrelated pipeline stages.
6. Turn the reproduction into a regression test.

Do not step through millions of rows. The small fixture preserves the failing condition while removing irrelevant volume.

### 13. Detect duplicate logging

If repository, service, and API layers all call `logger.exception()` and re-raise, one failure may create duplicate tracebacks, inflated error counts, noisy incident timelines, and higher storage costs. Let lower layers raise; log at a suitable boundary, unless a layer adds materially different diagnostic context.

### 14. Distinguish `stack_info` and `exc_info`

```python
logger.debug(
    "checkpoint reached",
    stack_info=True,
)
```

There is no exception here. `stack_info=True` records the current call stack leading to the logging call. `exc_info=True` is for exception information and its traceback.

### 15. Convert an MRE into a regression test

```python
def test_parse_amount_accepts_thousands_separator():
    assert parse_amount("1,000") == 1000
```

The test captures the formerly failing input and the required output. It becomes durable protection. Add it before changing the parser so the defect is represented explicitly.

## Level 4 — Production-oriented

### 16. Design safe production log context

Useful fields: `request_id`, `transaction_id`, `service_name`, `application_version`, timestamp, operation, and result. Do not log card number, CVV, access token, password, or secret. Correlation requires safe identifiers, not the full payment payload.

### 17. Diagnose a rare production error

1. Improve safe contextual logging.
2. Include request/correlation ID.
3. Capture traceback when an exception occurs.
4. Record application version.
5. Record safe configuration identifiers.
6. Correlate with metrics/traces.
7. Compare environment and timing.
8. Build an MRE from safe captured inputs.
9. Add regression protection.

An intermittent issue needs historical evidence; attaching a debugger to production immediately is not the default solution.

### 18. Diagnose a pipeline incident

For records dropped only when `amount="-"`:

```text
production evidence
→ failing input record shape
→ small fixture containing "-"
→ traceback/logs if an exception exists
→ minimal transformation reproduction
→ regression test
→ fix
```

This isolates the specific malformed value rather than rerunning the entire production dataset repeatedly.

### 19. Reproduce an LLM application failure

Preserve application version, prompt/template, input, relevant retrieved context, model/provider identifier, model settings, raw response only if safe to store, parser error, timestamp, and request ID. Do not capture secrets or unnecessary private data. Model behavior may not replay exactly, so test stable schemas and application contracts.

### 20. Diagnose an agent workflow failure

Capture request ID, agent/application version, input, relevant state, tool availability, tool calls and safe arguments, tool responses, iteration count, termination state, and final result. This reproduces observable workflow behavior. Do not rely on hidden reasoning traces or diagnose only from the final natural-language answer.

---

# Part D — All 12 Debugging Labs: Diagnosis and Correction

1. **Unreadable traceback:** `print("failed")` loses exception type, message, and call path. Use `logger.exception("processing failed")` inside the handler and re-raise if the caller still needs to handle it.
2. **Swallowed exception:** `except Exception: return None` hides configuration failure. Catch the expected `FileNotFoundError` and translate it to `ConfigurationError(...) from exc`, or handle it only if a safe fallback is defined.
3. **Wrong exception type:** if a wrong input type must raise `TypeError`, change the implementation from `ValueError` to `TypeError`; test with `pytest.raises(TypeError)`.
4. **Lost exception context:** use `raise RuntimeError("processing failed") from exc` rather than raising a new exception without explicitly preserving the conversion failure.
5. **Duplicate logging:** repository and service both log/re-raise the same exception. Let lower-level code raise and log once at a boundary with sufficient context.
6. **Incorrect log level:** a normal recoverable cache miss should generally be INFO or DEBUG, not ERROR; choose level based on operational significance.
7. **Missing context:** change `logger.error("transaction failed")` to include a safe `transaction_id` using `extra`, so the event can be correlated.
8. **Secret leakage:** never log all request headers; log approved metadata such as `request_id`, excluding authorization tokens.
9. **Excessive logging:** avoid one INFO event per row across a million records. Log aggregated progress, e.g. every 10,000 processed rows.
10. **Impossible-to-reproduce bug:** replace vague “sometimes the order total is wrong” with order ID, request ID, application version, input summary, business configuration, timestamp, relevant logs, and traceback if present.
11. **Oversized reproduction:** reduce five million rows to the affected partition and smallest record set that preserves the failure; create a fixture.
12. **Failing parametrized test:** separate valid cases from invalid cases. Valid cases can assert exact output:

```python
@pytest.mark.parametrize(
    "value,expected",
    [("100", 100), (" 100 ", 100)],
)
def test_parse_valid_values(value, expected):
    assert parse_amount(value) == expected
```

`"abc"` and `""` should have explicit expected exception tests if the contract rejects them. Identify and rerun the exact failing parameter rather than using a weak assertion that obscures expected behavior.

---

# Part E — Interview and Architecture Review

## 20 interview questions — concise model answers

1. **Traceback?** Diagnostic representation of the call path associated with an exception.
2. **Bug vs exception?** Bug is a software defect; exception is Python's runtime mechanism. Bugs can exist without exceptions.
3. **Why not only `print(exc)`?** It omits the call path.
4. **`traceback.print_exc()`?** Prints the currently handled exception with traceback.
5. **Logging?** Systematic event recording for diagnostic/operational information.
6. **Exception propagation?** Unhandled exception unwinds outward until a matching handler or program boundary.
7. **Exception chaining?** Links higher-level exception to lower-level cause, often with `raise ... from ...`.
8. **`getLogger(__name__)`?** Creates/retrieves a named module logger in the hierarchy.
9. **Handler?** Sends records to a destination such as stream or file.
10. **Formatter?** Controls how record fields are rendered.
11. **`logger.exception()`?** ERROR-level log with exception information, normally inside an exception handler.
12. **`exc_info` vs `stack_info`?** Exception traceback vs current stack leading to log call.
13. **MRE?** Smallest practical program/input/environment that still demonstrates a defect.
14. **Why minimize?** Reduce search space, improve communication, simplify tests and fixes.
15. **Does traceback prove root cause?** No; it shows exception path and immediate failure location.
16. **Catch every exception?** No; catch where meaningful recovery, translation, or reporting is possible.
17. **Why duplicate logging harmful?** Inflates volume and obscures incident timelines.
18. **Why not parse traceback strings?** They are presentation text and can vary; use structured exception/frame data.
19. **Intermittent production issue?** Add safe context/correlation, capture versions, use metrics/traces, then reproduce outside production.
20. **LLM application failure?** Separate deterministic application defects from probabilistic output; preserve safe context and test stable contracts.

## 12 architecture questions — model approaches

1. **Large Python backend logging:** module-level named loggers, application-boundary configuration, appropriate levels/handlers/formatters, safe context, centralized collection.
2. **Logger hierarchy:** align names with package hierarchy (`app`, `app.api`, `app.database`, `app.pipeline`); control propagation and avoid duplicate handlers.
3. **Where configure logging?** Application entry point; reusable libraries emit records without imposing global configuration.
4. **Prevent duplicate logs:** understand logger hierarchy, handler attachment, and propagation; place handlers deliberately.
5. **Safely log exceptions:** log at appropriate reporting boundary with safe context and traceback; avoid repeated logs at every layer.
6. **Distributed backend debugging:** correlation ID, structured logs, distributed traces, metrics, exception data, deployment/version metadata; reproduce outside production.
7. **Millions of pipeline rows:** identify partition/batch/record class/stage using logs and metrics, then build a small fixture.
8. **API reproduction:** method, path, safe headers, query, minimal body, status, response, environment/version.
9. **AI/LLM reproduction:** application/model version, prompt/template, minimal input, relevant retrieval context, tool inputs/results, settings; account for nondeterminism.
10. **Agentic AI diagnosis:** observable state → tool call → result → state transitions; do not depend on hidden reasoning.
11. **Connect telemetry:** correlation ID joins request trace, multiple logs, and exception event so an aggregate alert can lead to one failing request.
12. **Manage logging cost:** control volume, levels, retention, sampling, payload size, duplicate events, and routine DEBUG output. Optimize for sufficient signal, not maximum logs.

---

# Part F — Production Diagnostic Checklist

- [ ] Identify exception type and understand message.
- [ ] Capture traceback and identify relevant frame/call chain.
- [ ] Understand propagation and preserve cause/context where useful.
- [ ] Avoid exposing traceback internals to end users unnecessarily.
- [ ] Use named loggers and appropriate levels.
- [ ] Add safe context and request/correlation IDs.
- [ ] Capture exception information where appropriate.
- [ ] Use `stack_info` only when useful.
- [ ] Avoid duplicate logging and control volume.
- [ ] Configure logging centrally at the application boundary.
- [ ] Never log secrets; minimize/redact personal data.
- [ ] Record exact symptom, expected and actual behavior.
- [ ] Capture safe input, environment, app/dependency versions.
- [ ] Control time/randomness and identify external dependencies.
- [ ] Create an MRE where practical.
- [ ] Form and verify a root-cause hypothesis.
- [ ] Fix the root cause, run tests, add regression coverage.
- [ ] Improve observability if the incident exposed a diagnostic gap.

---

# Part G — Knowledge Check Answers

1. **Traceback path:** `main` called `run`, `run` called `parse`, and `int("abc")` raised `ValueError`; it does not explain why `"abc"` reached the parser.
2. **Bug without exception?** Yes. A wrong calculation can return a normal but incorrect value.
3. **Why `print("failed")` insufficient?** It lacks severity, source identity, configurable destinations, context, and exception information.
4. **Where `logger.exception()`?** Inside an exception handler when logging exception and traceback.
5. **No exception, need current call path?** Use `stack_info=True`.
6. **Why MRE?** It removes unrelated complexity while preserving the failure.
7. **Is `int()` root cause?** Not necessarily; upstream validation, parsing, database, or API may have supplied bad input.
8. **Why not log everything?** Cost, overhead, noise, and sensitive-data leakage; important events become harder to find.
9. **No regression test?** A later change can reintroduce the defect unnoticed.
10. **Why LLM reproduction difficult?** Outputs can be probabilistic and context/configuration dependent.
11. **Agent diagnostic data?** Observable input, state, tool calls/arguments/results, iterations, errors, and final output—not hidden chain-of-thought.
12. **Intermittent issue without exception?** Improve safe contextual logs, correlation IDs, version/environment metadata, metrics, and traces before designing a controlled reproduction.

---

# Part H — Glossary and Completion Status

| Term | Meaning |
|---|---|
| Bug | Defect in software |
| Exception | Python object representing exceptional runtime condition |
| Failure | Observable behavior that violates expectation |
| Crash | Unexpected process/application termination |
| Traceback | Call-path information associated with an exception |
| Call stack | Active chain of function calls |
| Stack frame | Runtime context for one active function call |
| Exception propagation | Unhandled exception moving outward through callers |
| Exception chaining | Linking a higher-level exception to its underlying cause |
| Exception context | Automatically recorded relation to an earlier handled exception |
| Logger | Named object used to emit log events |
| Root logger | Highest-level logger |
| Logger hierarchy | Parent/child naming structure |
| Handler | Sends log records to destination |
| Formatter | Controls record presentation |
| LogRecord | One event plus its metadata |
| Log level | Severity used to filter/interpret events |
| `exc_info` | Logging option for exception information |
| `stack_info` | Logging option for current call stack |
| Structured logging | Explicit machine-queryable fields |
| Log propagation | Forwarding records to ancestor handlers |
| Log rotation | Rolling files based on size/time |
| Log injection | Manipulation of logs through unsafe user-controlled content |
| MRE | Minimal Reproducible Example |
| Reproducibility | Ability to trigger same behavior under controlled conditions |
| Root cause | Underlying reason for failure |
| Regression | Previously correct behavior becoming incorrect |
| Observability | Inferring system behavior from telemetry |
| Correlation ID | Identifier linking events for one request/workflow |
| Metric | Numeric measurement of system behavior |
| Trace | Request/workflow path across components |
| Incident | Production event requiring investigation/response |

**Completion status:** Module 07, Lesson 06 — Tracebacks, Logging, and Minimal Reproductions — is covered. Lesson 07 — Mocking and Test Doubles — remains unstarted until you explicitly request it.
