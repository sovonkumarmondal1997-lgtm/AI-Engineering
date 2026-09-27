# Validation, Errors, and Exit Codes in Python

> Stage 1 — Programming & Computational Thinking  
> Module 10 — Production Habits for Python Programs  
> Lesson 03 — Validation, Errors, and Exit Codes

This chapter teaches validation, exceptions, error communication, and CLI exit behavior from beginner level to production-oriented Python practice. The goal is to understand not only how to raise an exception, but how to design predictable boundaries, preserve useful failure information, test failure paths, and communicate outcomes safely to both humans and automation.

A useful learning loop for this chapter is:

```text
Understand
→ Predict
→ Implement
→ Test normal case
→ Test edge cases
→ Debug
→ Refactor
→ Document
→ Explain aloud
```

---

# 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain what validation is and why it belongs at input boundaries;
- distinguish parsing from validation;
- distinguish missing input, malformed input, invalid values, domain-rule violations, operational failures, and programmer defects;
- use validation for types, presence, formats, ranges, allowed values, relationships, files, and configuration;
- use explicit checks instead of `assert` for external input;
- raise and catch appropriate Python exceptions;
- use `try`, `except`, `else`, and `finally` deliberately;
- explain exception propagation through function calls;
- define custom exception classes and use exception chaining;
- design useful and safe error messages;
- validate command-line input with `argparse`;
- understand `sys.exit()` and `SystemExit`;
- design application-specific exit codes;
- distinguish stdout from stderr;
- make a CLI predictable for humans and automation;
- test validation failures with `pytest.raises()`;
- test a real CLI with `subprocess.run()` and inspect `returncode`, `stdout`, and `stderr`;
- design basic validation for data pipelines and Applied AI/tool boundaries;
- combine error handling, safe logging, and exit-code communication;
- debug failures by first classifying the boundary, exception, and expected behavior.

The production-level question to keep asking is:

> What should happen when the input, environment, dependency, or program state does not satisfy the assumptions needed by the next step?

---

# 2. Why Validation and Error Handling Matter

Imagine a bank teller asking for an account number. A production system does not immediately execute a transaction against whatever text was entered. It first checks the input contract.

```text
Account number entered
        ↓
Is it present?
        ↓
Is the format acceptable?
        ↓
Does it satisfy application rules?
        ↓
Only then perform the transaction
```

Python programs have the same structure.

```text
External Input
      ↓
Validation
      ↓
Program / Business Logic
      ↓
Result
```

Without validation, an invalid value can travel through many functions before it fails. That usually makes the error harder to interpret.

Consider:

```python
age = input("Enter your age: ")
years_until_retirement = 65 - int(age)
print(years_until_retirement)
```

Questions immediately appear:

- What if the user enters `"abc"`?
- What if the user enters `"-10"`?
- What if the user enters `"999"`?
- What if they enter only spaces?
- What if the application has a stricter business rule than Python's `int()` conversion?

Error handling matters for the same reason. A program can encounter:

- invalid user input;
- missing or malformed files;
- invalid configuration;
- unsupported states;
- permission failures;
- unavailable resources;
- unexpected programming defects.

A robust program makes the response to those conditions explicit.

---

# 3. What Is Validation?

In simple terms:

> Validation is checking whether data satisfies the rules required before the program uses it.

A technical definition is:

> Validation checks a value or collection of values against a defined contract, which can include type, presence, format, range, allowed-value, relationship, and domain-specific rules.

Examples:

```python
age >= 0
```

```python
amount > 0
```

```python
environment in {"dev", "test", "prod"}
```

```python
filename.exists()
```

```python
model_name != ""
```

Validation has several common categories.

| Category | Example | Typical question |
|---|---|---|
| Type | `workers` must be an integer | Is the value of the expected type? |
| Presence | `--input` is required | Was a value supplied? |
| Format | date must match an accepted representation | Can the representation be parsed? |
| Range | timeout must be 1–300 | Is the value within bounds? |
| Allowed value | environment must be `dev/test/prod` | Is the value one of the supported options? |
| Relationship | start must not exceed end | Are multiple fields valid together? |
| Business/domain rule | amount cannot be negative | Does the value make sense to the application? |

The distinction between **parsing** and **validation** is useful:

```text
Parse
= turn external representation into a Python value

Validate
= determine whether that value satisfies the application's contract
```

They can be implemented in separate functions or together at a boundary when that makes the contract clearer.

---

# 4. Input Boundaries

An input boundary is where data enters a component from a context that the component does not fully control.

Examples include:

```text
CLI arguments
Environment variables
Files
stdin
CSV rows
JSON input
Database records
External service responses
User input
Model-generated output
Tool arguments
```

A useful architecture is:

```text
External / uncertain data
          ↓
        Parse
          ↓
       Validate
          ↓
Trusted internal representation
          ↓
     Business logic
```

## Why boundary validation matters

If a CLI argument is invalid, it is better to reject it before a networking library receives it.

Poor:

```text
CLI
 ↓
configuration
 ↓
network client
 ↓
server setup
 ↓
failure deep in stack
```

Better:

```text
CLI
 ↓
parse
 ↓
validate
 ↓
validated configuration
 ↓
network client
```

The phrase **as close as possible to the boundary** does not mean every rule must be duplicated everywhere. It means external uncertainty should not be allowed to leak deep into code that assumes a stronger contract.

---

# 5. Valid, Invalid, Missing, and Unexpected Input

These categories should not be collapsed into one generic "bad input" concept.

| Situation | Example | What it means |
|---|---|---|
| Valid | `age = 42` | Satisfies the contract |
| Missing | no age supplied | Required value is absent |
| Invalid format | `"abc"` for integer | Cannot be parsed as expected |
| Invalid value | `-5` for non-negative age | Parsed, but violates a rule |
| Unsupported value | `"sandbox"` when only `dev/test/prod` exist | Outside accepted domain |
| Operational failure | file permission denied | Environment/dependency problem |
| Programmer defect | unexpected `AttributeError` | Program bug or unforeseen defect |

For example:

```python
age = "abc"
```

has a format/conversion problem.

But:

```python
age = -5
```

can be converted to an integer while still violating the application's domain rule.

And:

```text
database connection failed
```

is not user-input validation at all.

A strong mental model is:

```text
Input contract violation
→ validation error

Runtime operational condition
→ operational error

Unexpected code/state defect
→ unexpected failure / bug
```

---

# 6. Validation Strategies

Practical validation should be explicit, readable, and aligned with the actual contract.

## Type checks

```python
def require_text(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("value must be a string")
    return value
```

## Presence checks

```python
def require_text(value: str | None) -> str:
    if value is None:
        raise ValueError("value is required")

    cleaned = value.strip()
    if not cleaned:
        raise ValueError("value is required")

    return cleaned
```

Do not use `if not value` unless the contract really says every falsey value is invalid. `0` and `False` may be legitimate values.

## Range checks

```python
def validate_timeout(timeout_seconds: int) -> int:
    if not 1 <= timeout_seconds <= 300:
        raise ValueError("timeout must be between 1 and 300 seconds")
    return timeout_seconds
```

## Membership checks

```python
ALLOWED_ENVIRONMENTS = {"dev", "test", "prod"}


def validate_environment(value: str) -> str:
    if value not in ALLOWED_ENVIRONMENTS:
        raise ValueError("environment must be one of: dev, test, prod")
    return value
```

## String checks

```python
def validate_name(value: str) -> str:
    cleaned = value.strip()

    if not cleaned:
        raise ValueError("name is required")

    if len(cleaned) > 100:
        raise ValueError("name must be 100 characters or fewer")

    return cleaned
```

## Path checks

```python
from pathlib import Path


def validate_input_file(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"input file does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"input path is not a regular file: {path}")

    return path
```

## Relationship checks

```python
def validate_window(start: int, end: int) -> tuple[int, int]:
    if start < 0 or end < 0:
        raise ValueError("start and end must be non-negative")

    if start > end:
        raise ValueError("start must be less than or equal to end")

    return start, end
```

Keep multiple rules readable rather than squeezing them into one boolean expression.

---

# 7. Basic Python Validation

A simple validation function often has this shape:

```python
def validate_age(age: int) -> int:
    if age < 0:
        raise ValueError("age must be non-negative")
    return age
```

The function establishes a postcondition:

```text
If validate_age() returns normally,
then the returned value is >= 0.
```

That is a small example of a **trusted internal representation**.

A parse-and-validate function can combine representation conversion with domain rules:

```python
def parse_age(raw_age: str) -> int:
    raw_age = raw_age.strip()

    if not raw_age:
        raise ValueError("age is required")

    try:
        age = int(raw_age)
    except ValueError as exc:
        raise ValueError("age must be an integer") from exc

    if not 0 <= age <= 120:
        raise ValueError("age must be between 0 and 120")

    return age
```

The flow is:

```text
presence
→ parsing
→ range validation
→ trusted int
```

For valid input:

```text
"42"
→ strip
→ int("42")
→ 0 <= 42 <= 120
→ return 42
```

For invalid input:

```text
"abc"
→ int("abc")
→ ValueError
```

For an invalid value:

```text
"-1"
→ int("-1")
→ -1
→ range check fails
→ ValueError
```

---

# 8. Assertions vs Validation

Python supports assertions:

```python
assert condition
```

Assertions primarily express programmer assumptions or invariants.

Example:

```python
def calculate_average(total: float, count: int) -> float:
    assert count > 0
    return total / count
```

The assumption is:

> The code reaching this point expects `count` to be positive.

External-input validation is a different responsibility.

Bad use of `assert`:

```python
def create_user(username: str) -> None:
    assert username.strip(), "username is required"
```

Better:

```python
def create_user(username: str) -> None:
    username = username.strip()

    if not username:
        raise ValueError("username is required")
```

Assertions should not be the primary safety mechanism for external input because Python can run with optimization settings that disable assertion checks.

Use this mental model:

```text
assert
= "This should already be true."

explicit validation
= "This must be checked before I accept this input."
```

---

# 9. Exceptions and Errors

An exception is Python's mechanism for signaling that normal execution cannot continue in the current way.

A simple example:

```python
result = 10 / 0
```

raises:

```text
ZeroDivisionError
```

The important idea is that the exception is an object.

```python
try:
    10 / 0
except ZeroDivisionError as exc:
    print(type(exc).__name__)
    print(str(exc))
```

A simplified flow is:

```text
normal execution
      ↓
operation fails
      ↓
exception object
      ↓
Python looks for matching handler
      ↓
handler found? ── yes → except block
      │
      └── no → propagate outward
```

An exception is therefore both:

- a signal that normal execution was interrupted;
- an object carrying information about the failure.

---

# 10. Exception Types

A simplified view of the relevant hierarchy is:

```text
BaseException
└── Exception
    ├── ValueError
    ├── TypeError
    ├── KeyError
    ├── IndexError
    ├── FileNotFoundError
    ├── PermissionError
    └── OSError
```

The complete hierarchy is larger.

## `ValueError`

The value is inappropriate for the operation.

```python
int("abc")
```

## `TypeError`

The operation receives an inappropriate type.

```python
"total" + 10
```

## `KeyError`

A dictionary lookup requests a missing key.

```python
record = {"name": "Ada"}
record["age"]
```

## `IndexError`

A sequence index is outside its valid range.

```python
items = ["a", "b"]
items[5]
```

## `FileNotFoundError`

A file or path expected by an operation does not exist.

```python
from pathlib import Path

Path("missing.txt").read_text()
```

## `PermissionError`

An operation is denied by the operating system's permission model.

## `OSError`

A broad family for operating-system-related errors. Specific subclasses are often better when you need different handling.

## `Exception`

The superclass for ordinary application-level exceptions.

This can be appropriate at a deliberate top-level boundary:

```python
try:
    run_application()
except Exception:
    logger.exception("unexpected application failure")
```

It is usually not a good default for every local function because it can hide defects.

Do not use `except BaseException:` as ordinary application error handling. `BaseException` also includes exceptions such as `SystemExit` and `KeyboardInterrupt` whose semantics are not ordinary application errors.

---

# 11. Raising Exceptions

The `raise` statement explicitly signals failure.

```python
def validate_age(age: int) -> int:
    if age < 0:
        raise ValueError("age must be non-negative")
    return age
```

When `raise` executes:

1. normal execution of the current block stops;
2. an exception is active;
3. Python searches for a matching exception handler;
4. if no handler exists locally, the exception propagates outward.

## Bare `raise` and re-raising

A bare `raise` inside an exception handler re-raises the currently handled exception.

```python
import logging

logger = logging.getLogger(__name__)


def run_task() -> None:
    try:
        do_work()
    except ValueError:
        logger.exception("operation failed")
        raise
```

This says:

> I recorded useful context, but I did not recover from the failure.

## Raising an exception object

```python
error = ValueError("invalid value")
raise error
```

Usually, raising at the point the rule is detected is clearer.

---

# 12. Catching Exceptions

Basic exception handling uses `try` and `except`.

```python
try:
    value = int(raw_value)
except ValueError:
    print("Please provide an integer.")
```

Catch the specific exception you understand.

Multiple types can be grouped when they truly share the same recovery path:

```python
try:
    result = parse_record(record)
except (ValueError, TypeError):
    reject_record(record)
```

Capture the exception object when you need its details:

```python
try:
    value = int(raw_value)
except ValueError as exc:
    print(f"Could not parse value: {exc}")
```

A broad catch is often misleading:

```python
try:
    process()
except Exception:
    print("Invalid input")
```

What if the real problem is a programmer bug? The message would misclassify it.

Prefer:

```python
try:
    value = parse_input()
except ValueError as exc:
    report_input_error(exc)
```

and let unrelated failures propagate.

---

# 13. try / except / else / finally

Python supports four related blocks:

```python
try:
    ...
except SomeError:
    ...
else:
    ...
finally:
    ...
```

## `try`

Contains the operation that may raise an exception you intend to handle.

## `except`

Contains the corresponding recovery, translation, or reporting logic.

## `else`

Runs only when the `try` block completes successfully.

```python
def parse_and_report(raw_value: str) -> int:
    try:
        value = int(raw_value)
    except ValueError:
        print("Input is not an integer.")
        return 0
    else:
        print("Input parsed successfully.")
        return value
```

Keeping success-only work in `else` can reduce accidental catching of unrelated exceptions.

## `finally`

Runs whether the operation succeeds or raises.

```python
resource_open = False

try:
    open_resource()
    resource_open = True
    perform_work()
except OSError:
    print("Resource operation failed.")
finally:
    if resource_open:
        close_resource()
```

The key roles are:

```text
try     → attempt
except  → handle a matching failure
else    → success-only work
finally → cleanup / final action
```

This chapter uses `finally` conceptually; full context-manager design belongs elsewhere in the roadmap.

---

# 14. Exception Propagation

Suppose:

```text
function A
    ↓
function B
    ↓
function C
    ↓
raise ValueError
```

If `C` does not catch the exception, it propagates outward:

```text
C
↓
B
↓
A
↓
caller
```

Example:

```python
def parse() -> int:
    raise ValueError("invalid number")


def transform() -> int:
    return parse()


def run() -> None:
    transform()


run()
```

There is no handler, so the exception reaches the top level.

Now handle it where the application can communicate it meaningfully:

```python
def parse() -> int:
    raise ValueError("invalid number")


def transform() -> int:
    return parse()


def run() -> None:
    try:
        transform()
    except ValueError as exc:
        print(f"Input error: {exc}")
```

Production principle:

> Handle an exception where the program can meaningfully recover, translate, or communicate it.

Do not catch exceptions in every function merely because exceptions exist.

---

# 15. Useful Error Messages

Compare:

```python
raise ValueError("Invalid")
```

with:

```python
raise ValueError("age must be between 0 and 120")
```

A useful error message should usually communicate:

```text
What failed?
Why did it fail?
What rule was involved?
What can the caller do?
```

Example:

```python
raise ValueError("workers must be a positive integer")
```

Adding the received value can improve diagnostics:

```python
raise ValueError(
    f"workers must be a positive integer; received {workers!r}"
)
```

But do not automatically include raw input. Ask whether it is safe and necessary.

Bad:

```python
raise ValueError(f"token is invalid: {token}")
```

Better:

```python
raise ValueError("authentication configuration is invalid")
```

Error messages are part of a user/operator interface. Optimize them for clarity, specificity, safety, and consistency.

---

# 16. Custom Exceptions

Custom exceptions give an application a domain-specific failure type.

```python
class ConfigurationError(Exception):
    """Raised when application configuration is invalid."""
```

Use it:

```python
def load_configuration() -> dict[str, str]:
    raise ConfigurationError("API endpoint is missing")
```

Handle it specifically:

```python
try:
    config = load_configuration()
except ConfigurationError as exc:
    print(f"Configuration error: {exc}")
```

A small hierarchy can be useful:

```python
class ApplicationError(Exception):
    """Base class for expected application failures."""


class ConfigurationError(ApplicationError):
    """Configuration is invalid."""


class InputDataError(ApplicationError):
    """Input data violates the application contract."""
```

Now a caller can catch at the level of detail it needs.

Do not create a separate exception class for every sentence an application can print. A custom exception is useful when the **type itself carries meaningful domain information**.

---

# 17. Exception Chaining

Exception chaining lets a high-level exception preserve its lower-level cause.

Use:

```python
raise NewError("higher-level explanation") from exc
```

Example:

```python
class ConfigurationError(Exception):
    """Raised when configuration is invalid."""


def parse_port(raw_value: str) -> int:
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ConfigurationError(
            "PORT must be an integer"
        ) from exc

    if not 1 <= value <= 65_535:
        raise ConfigurationError(
            "PORT must be between 1 and 65535"
        )

    return value
```

The higher-level meaning is:

```text
ConfigurationError
        caused by
ValueError
```

This preserves diagnostic context while giving the caller a domain-level exception.

Python also supports:

```python
raise ConfigurationError("invalid configuration") from None
```

which suppresses the displayed automatic context. Use this deliberately when the lower-level implementation detail is not useful at the boundary.

General rule:

> Translate low-level failures only when the higher-level layer has a meaningful domain abstraction to communicate.

---

# 18. Expected vs Unexpected Errors

Not every exception has the same operational meaning.

## Expected/input-related failure

```text
User entered an unsupported environment.
```

This is a normal possibility of using the application. A clear validation message is usually appropriate.

## Recoverable operational failure

```text
A temporary file is unavailable.
```

The application may be able to recover, choose a different resource, or stop with a useful operational error.

## Unexpected programmer/system defect

```text
AttributeError caused by an incorrect object assumption.
```

This should not automatically become:

```text
Invalid input
```

The classification affects what you do next:

```text
Expected input failure
→ explain/reject

Operational failure
→ recover/report according to policy

Unexpected defect
→ diagnose, preserve evidence, fail safely
```

The precise policy is application-specific, but the categories should remain conceptually distinct.

---

# 19. Validation at System Boundaries

Boundary validation produces a useful invariant:

```text
Outside
= uncertain / untrusted

Inside after validation
= stronger contract
```

For a file pipeline:

```text
file
 ↓
open
 ↓
validate structure
 ↓
validate rows
 ↓
trusted record
 ↓
process
```

For a CLI:

```text
raw CLI text
 ↓
argparse conversion
 ↓
application validation
 ↓
validated configuration
 ↓
main logic
```

For AI tool use:

```text
model-generated arguments
 ↓
parse
 ↓
validate
 ↓
authorize / apply domain rules
 ↓
execute tool
```

### Why delayed validation is expensive

Suppose a malformed value reaches several layers before failing:

```text
CLI
 ↓
service config
 ↓
worker
 ↓
network client
 ↓
library
 ↓
TypeError
```

The final exception may be technically correct but operationally unhelpful.

Boundary validation narrows the distance between cause and diagnosis.

---

# 20. CLI Validation

Command-line input is external input.

Common CLI sources are:

```text
command-line arguments
environment variables
files
stdin
```

A CLI should validate before doing expensive or irreversible work.

Example:

```bash
python app.py --port abc
```

The application should not wait until server startup to discover that `abc` is not a valid numeric port.

A useful flow is:

```text
CLI argument
 ↓
parse
 ↓
convert type
 ↓
validate domain rule
 ↓
run
```

`argparse` can handle common parsing and conversion rules. Application code should handle rules that belong to the business/domain contract.

---

# 21. sys.argv and argparse Validation

`sys.argv` contains the command-line argument list as provided to Python.

For:

```bash
python app.py --age 42
```

a simple program can inspect:

```python
import sys

print(sys.argv)
```

Typical shape:

```text
["app.py", "--age", "42"]
```

For a real CLI, `argparse` is generally clearer.

## `argparse.ArgumentParser`

```python
import argparse

parser = argparse.ArgumentParser(
    description="Process one input record."
)
```

## `parser.add_argument()`

```python
parser.add_argument(
    "--environment",
    choices=["dev", "test", "prod"],
    required=True,
)
```

## `parser.parse_args()`

```python
args = parser.parse_args()
```

## `type=`

```python
parser.add_argument("--workers", type=int)
```

The argument parser attempts the conversion before returning the parsed value.

## `choices=`

```python
parser.add_argument(
    "--environment",
    choices=["dev", "test", "prod"],
)
```

## `required=`

```python
parser.add_argument("--input", required=True)
```

## `default=`

```python
parser.add_argument("--workers", type=int, default=1)
```

The important distinction is:

```text
type=
→ parsing / conversion

choices=, required=
→ CLI-level contract

custom validation
→ application/domain rules
```

---

# 22. Custom argparse Validation

Built-in `argparse` features do not express every domain rule.

Suppose the application needs a positive integer.

```python
import argparse


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "must be an integer"
        ) from exc

    if number <= 0:
        raise argparse.ArgumentTypeError(
            "must be positive"
        )

    return number
```

Use it:

```python
parser = argparse.ArgumentParser()
parser.add_argument("--workers", type=positive_int, required=True)
args = parser.parse_args()
```

The function combines parsing and validation specifically for this CLI argument.

For more complex applications, another useful design is to parse first and validate later:

```python
args = parser.parse_args()
validate_application_arguments(args)
```

That is often easier to test because the domain validation is not tightly coupled to CLI formatting.

Choose the boundary that produces the clearest contract.

---

# 23. sys.exit()

`sys.exit()` requests termination of the Python interpreter with a status.

```python
import sys

sys.exit(0)
```

and:

```python
sys.exit(1)
```

Conventionally:

```text
0       → success
non-zero → failure
```

The exact non-zero meanings are not universal Python rules.

For example:

```python
sys.exit(3)
```

could mean "input validation failure" in one application.

Conceptually:

```text
sys.exit(value)
      ↓
raise SystemExit(value)
      ↓
uncaught at top level?
      ↓
interpreter terminates
      ↓
process reports status
```

A useful testable design is often:

```python
def main() -> int:
    ...
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
```

This separates application decisions from process termination.

---

# 24. SystemExit

`SystemExit` is the exception class used when Python is asked to terminate normally.

You can demonstrate the relationship:

```python
import sys

try:
    sys.exit(7)
except SystemExit as exc:
    print("SystemExit caught")
    print("requested code:", exc.code)
```

This is useful for understanding and testing.

The key equivalence is:

```text
sys.exit(7)
≈
raise SystemExit(7)
```

Do not normally catch `SystemExit` in application logic just to prevent termination. Doing so can change expected CLI behavior.

Where it matters:

```text
tests
control-flow understanding
CLI design
```

---

# 25. Exit Codes

An exit code is a numeric result reported by a CLI process to its caller.

The most important convention is:

```text
0       → success
non-zero → failure
```

Beyond that, the exact numeric meaning is determined by the application or a surrounding convention.

Example design:

```text
0 → success
1 → general application failure
2 → CLI usage error
3 → input validation failure
4 → configuration failure
```

These numbers are an **example application design**, not universal Python semantics.

Exit codes matter because automation may need to know:

```text
Did the job succeed?
```

without parsing human prose.

Relevant consumers include:

```text
shell scripts
CI/CD
cron jobs
batch pipelines
workflow automation
orchestration
```

A small, stable taxonomy is generally easier to maintain than many undocumented values.

---

# 26. Default Exit Behavior

Three important cases are:

```text
normal completion
uncaught exception
sys.exit(...)
```

## Normal completion

Consider:

```python
def main() -> None:
    print("done")


main()
```

When the process completes normally without requesting a non-zero status, the usual process result is success.

A more explicit CLI pattern is:

```python
def main() -> int:
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Uncaught exception

```python
def main() -> None:
    raise RuntimeError("unexpected failure")


main()
```

An uncaught ordinary exception terminates the program abnormally and normally yields a non-zero process status.

## Explicit exit

```python
import sys

sys.exit(5)
```

The process terminates with the requested status unless the `SystemExit` is intercepted.

The exact behavior of the surrounding shell is a separate concern, but the CLI design principle remains:

```text
normal completion → success
failure → non-zero
```

---

# 27. stdout vs stderr

CLI programs have two primary output streams:

```text
stdout
stderr
```

A useful convention is:

```text
stdout → primary command output
stderr → diagnostics / errors / warnings
```

Normal output:

```python
print("processed 100 records")
```

Diagnostic output:

```python
import sys

print("input file was not found", file=sys.stderr)
```

Why separate them?

Suppose stdout is piped into another command:

```bash
python app.py | another_command
```

Diagnostic text written to stdout can contaminate the data stream.

Redirection demonstrates the distinction:

```bash
python app.py > result.txt
```

```bash
python app.py 2> errors.txt
```

Both streams can be redirected independently:

```bash
python app.py > result.txt 2> errors.txt
```

Do not define the distinction as "stdout is good and stderr is bad." A better mental model is:

```text
stdout
= primary program output

stderr
= diagnostic / secondary output
```

---

# 28. Predictable CLI Behavior

A production CLI should be predictable for both a person and a machine.

Use this model:

```text
Valid input
   ↓
useful output
   ↓
exit 0
```

Invalid input:

```text
invalid input
   ↓
clear error message
   ↓
non-zero exit
```

Unexpected failure:

```text
unexpected failure
   ↓
useful diagnostic evidence
   ↓
non-zero exit
```

A common structure is:

```python
import sys


def main() -> int:
    try:
        run_application()
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

This design gives the caller a simple contract:

```text
return 0 → success
return non-zero → failure
```

For more error classes, use a documented taxonomy.

---

# 29. Validation and Configuration

Configuration values are external input even when they come from an environment variable or a local file.

Common values include:

```text
PORT
TIMEOUT
ENVIRONMENT
LOG_LEVEL
DATA_PATH
MODEL_NAME
```

Validate them before starting expensive work.

Example:

```python
def validate_port(port: int) -> int:
    if isinstance(port, bool) or not isinstance(port, int):
        raise TypeError("port must be an integer")

    if not 1 <= port <= 65_535:
        raise ValueError("port must be between 1 and 65535")

    return port
```

Environment values are often strings.

```python
def parse_port_from_env(raw_value: str) -> int:
    raw_value = raw_value.strip()

    if not raw_value:
        raise ValueError("PORT is required")

    try:
        port = int(raw_value)
    except ValueError as exc:
        raise ValueError("PORT must be an integer") from exc

    return validate_port(port)
```

The startup sequence becomes:

```text
raw configuration
 ↓
parse
 ↓
validate
 ↓
trusted configuration
 ↓
application startup
```

This lesson connects to `01-configuration-and-env-files.md` but does not modify that file.

---

# 30. Validation and File Processing

File processing commonly has multiple validation points.

```text
CSV path
 ↓
file existence validation
 ↓
file type/path validation
 ↓
open/read
 ↓
header/schema validation
 ↓
row validation
 ↓
processing
```

## Missing file

```python
from pathlib import Path


def require_file(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"input file does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"input path is not a regular file: {path}")

    return path
```

## Extension rule

```python
def require_csv(path: Path) -> Path:
    if path.suffix.lower() != ".csv":
        raise ValueError("input file must use the .csv extension")
    return path
```

An extension is only one signal; it is not proof that the file content is actually CSV.

## Header validation

```python
REQUIRED_COLUMNS = {"id", "amount"}


def validate_headers(headers: list[str]) -> None:
    missing = REQUIRED_COLUMNS - set(headers)

    if missing:
        raise ValueError(
            f"missing required columns: {sorted(missing)}"
        )
```

## Row validation

```python
def validate_row(row: dict[str, str], row_number: int) -> None:
    record_id = row.get("id", "").strip()

    if not record_id:
        raise ValueError(f"row {row_number}: id is required")

    raw_amount = row.get("amount", "").strip()

    if not raw_amount:
        raise ValueError(f"row {row_number}: amount is required")

    try:
        amount = float(raw_amount)
    except ValueError as exc:
        raise ValueError(
            f"row {row_number}: amount must be numeric"
        ) from exc

    if amount < 0:
        raise ValueError(
            f"row {row_number}: amount must be non-negative"
        )
```

Notice how the error identifies the row number without dumping the entire row.

---

# 31. Validation in Data Pipelines

A practical data pipeline may look like:

```text
Raw input
   ↓
schema validation
   ↓
row validation
   ↓
transformation
   ↓
output
```

## Fail-fast validation

Use when any critical invalid data should stop processing.

```python
def process_rows(rows):
    for row_number, row in enumerate(rows, start=1):
        validate_row(row, row_number)
        process_row(row)
```

## Collecting multiple validation errors

Sometimes operators need to see all errors in one run.

```python
def collect_errors(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []

    for row_number, row in enumerate(rows, start=1):
        try:
            validate_row(row, row_number)
        except ValueError as exc:
            errors.append(str(exc))

    return errors
```

Then:

```python
errors = collect_errors(rows)

if errors:
    for error in errors:
        print(error, file=sys.stderr)

    raise ValueError(f"{len(errors)} invalid row(s)")
```

## Skip invalid rows

A pipeline may deliberately reject individual rows and continue.

That is acceptable only when the contract explicitly allows it. Record useful counts:

```text
total rows
accepted rows
rejected rows
```

Do not silently skip bad records.

## Critical failures

Examples that may justify stopping the entire job:

```text
missing required schema column
unreadable input file
invalid configuration
corrupt file format
```

The correct policy depends on the application's data contract.

---

# 32. Validation in Applied AI Systems

Applied AI systems introduce several important boundaries.

```text
User input
    ↓
validation
    ↓
configuration validation
    ↓
model request
    ↓
model output
    ↓
parse
    ↓
validate structured result
    ↓
tool arguments / downstream code
```

Examples of validation targets:

- empty or excessive user input;
- unsupported model name;
- invalid numeric parameters;
- malformed structured output;
- missing tool argument;
- wrong tool-argument type;
- values outside business rules.

A basic example:

```python
def validate_tool_arguments(arguments: dict[str, object]) -> dict[str, str]:
    if "path" not in arguments:
        raise ValueError("tool argument 'path' is required")

    path = arguments["path"]

    if not isinstance(path, str):
        raise TypeError("tool argument 'path' must be a string")

    path = path.strip()

    if not path:
        raise ValueError("tool argument 'path' cannot be empty")

    return {"path": path}
```

A key engineering principle is:

> Model-generated output is still untrusted input when downstream application code is going to act on it.

That means:

```text
model output
 ↓
parse
 ↓
validate
 ↓
authorize / apply domain rules
 ↓
execute
```

The model's source does not replace application validation.

---

# 33. Error Handling in AI/Data Systems

A simple failure taxonomy is:

```text
User / input error
→ clear validation message

External dependency failure
→ operational error

Programmer bug
→ unexpected failure + diagnostic evidence
```

For a data system:

```text
Malformed row
→ data validation failure
```

For an AI tool boundary:

```text
missing required tool argument
→ validation failure
```

For an external service:

```text
connection unavailable
→ operational failure
```

For internal code:

```text
unexpected AttributeError
→ programmer/system defect
```

Different failure classes may require different handling. Do not claim every exception should be presented to end users in the same way.

This chapter deliberately avoids provider-specific AI API behavior; the validation principle is provider-independent.

---

# 34. Logging + Errors

The previous lesson, `02-safe-and-useful-logging.md`, covers logging in greater depth. Here, focus on the relationship between three mechanisms.

```text
Exception
→ failure signal inside Python

Logging
→ operational evidence

Exit code
→ final result for the process caller
```

Example:

```python
import logging
import sys

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when application configuration is invalid."""


def load_config():
    raise ConfigurationError("MODEL_NAME is missing")


def main() -> int:
    try:
        load_config()
    except ConfigurationError as exc:
        logger.error("configuration validation failed: %s", exc)
        print("Configuration error. Check your settings.", file=sys.stderr)
        return 4

    return 0
```

The three-part model is:

```text
Handle
+
Log
+
Communicate
```

Do not log secrets merely because a failure occurred.

Bad:

```python
logger.exception(
    "request failed token=%s payload=%r",
    token,
    payload,
)
```

Better:

```python
logger.exception(
    "request failed operation=%s",
    "create-job",
)
```

Use the previous logging lesson for broader logger, handler, and formatter design.

---

# 35. Error Message Design

Good error messages tend to be:

- clear;
- specific;
- concise;
- actionable when appropriate;
- safe;
- consistent.

Bad:

```text
Error
```

Better:

```text
Input file not found: data/input.csv
```

Potentially safer in some environments:

```text
Input file could not be opened.
```

Which is better depends on whether revealing the path is useful and appropriate.

A function can communicate a domain rule precisely:

```python
raise ValueError(
    "timeout must be between 1 and 300 seconds"
)
```

An operator-facing CLI can add a prefix:

```python
print(
    "Input error: timeout must be between 1 and 300 seconds",
    file=sys.stderr,
)
```

Avoid duplicate noise such as:

```text
ERROR ERROR ERROR: ERROR: INVALID INPUT
```

The exception, log entry, and CLI message should each contribute useful information rather than copy every detail into every channel.

---

# 36. Error Taxonomy

A practical error classification is:

| Error category | Example | Typical response |
|---|---|---|
| Missing input | required argument absent | reject input |
| Invalid input | malformed value | validation error |
| Domain/business rule | unsupported state | domain error |
| External dependency | service unavailable | recover/retry/report according to policy |
| File/system problem | permission denied | report/fail |
| Programmer defect | unexpected `AttributeError` | surface/diagnose |

The exact response is application-specific.

The important architectural distinction is:

```text
What happened?
+
Who owns the recovery decision?
+
How should the caller be informed?
```

For example, a `FileNotFoundError` can be a normal validation failure when a required input file is missing, while another `OSError` may represent an operational failure that deserves a different response.

Do not classify purely from the class name. Classify from the **meaning of the failure in the current contract**.

---

# 37. Anti-Patterns

This section gives a production review format for common mistakes.

## Anti-pattern 1 — No validation

**Problem**

External input is used directly.

**Why it is harmful**

Invalid assumptions move deeper into the system.

**Bad example**

```python
def start(raw_port: str) -> None:
    start_server(int(raw_port))
```

**Better approach**

```python
def parse_port(raw_port: str) -> int:
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ValueError("port must be an integer") from exc

    if not 1 <= port <= 65_535:
        raise ValueError("port must be between 1 and 65535")

    return port
```

**Production lesson**

Validate before deeper processing.

## Anti-pattern 2 — Validation too late

**Problem**

A bad configuration value travels through multiple functions.

**Why it is harmful**

The failure becomes harder to associate with the original boundary.

**Bad example**

```python
config = load_config()
run_workers(config)
```

where `run_workers()` is the first place that checks the value.

**Better approach**

Validate during configuration loading or startup.

**Production lesson**

Fail near the source of the contract violation.

## Anti-pattern 3 — `assert` for user input

**Problem**

The application relies on assertions for durable input validation.

**Why it is harmful**

Assertions are designed for programmer assumptions and may be disabled in optimized execution.

**Bad example**

```python
assert workers > 0
```

**Better approach**

```python
if workers <= 0:
    raise ValueError("workers must be positive")
```

**Production lesson**

Use explicit validation for external data.

## Anti-pattern 4 — Catching every exception

**Problem**

Every failure is caught with `except Exception`.

**Why it is harmful**

Expected failures and programmer defects become indistinguishable.

**Bad example**

```python
try:
    process()
except Exception:
    print("invalid input")
```

**Better approach**

Catch expected exceptions specifically and use a deliberate top-level handler for unexpected failures.

**Production lesson**

Broad handling belongs at clearly chosen boundaries, not everywhere.

## Anti-pattern 5 — Swallowing exceptions

**Problem**

A failure is ignored.

**Why it is harmful**

The program can continue with incorrect assumptions.

**Bad example**

```python
try:
    save_output()
except OSError:
    pass
```

**Better approach**

Recover, translate, report, or propagate.

```python
try:
    save_output()
except OSError as exc:
    raise RuntimeError("output could not be saved") from exc
```

**Production lesson**

Every failure needs a deliberate disposition.

## Anti-pattern 6 — Returning `None` for every error

**Problem**

`None` means missing value, invalid input, dependency failure, and unexpected bug.

**Why it is harmful**

The caller cannot distinguish meanings.

**Bad example**

```python
def load_config():
    try:
        return read_config()
    except Exception:
        return None
```

**Better approach**

Use specific exceptions or an explicit result contract.

**Production lesson**

Do not overload one sentinel with unrelated meanings.

## Anti-pattern 7 — Generic error messages

**Problem**

The message communicates nothing.

**Why it is harmful**

Users and operators cannot act on it.

**Bad example**

```python
raise ValueError("Invalid")
```

**Better approach**

```python
raise ValueError("timeout must be between 1 and 300 seconds")
```

**Production lesson**

Error messages are part of the interface.

## Anti-pattern 8 — Logging an error but pretending success

**Problem**

The log says failure while the process returns success.

**Why it is harmful**

Automation trusts the wrong result.

**Bad example**

```python
def main() -> int:
    try:
        run_job()
    except OSError as exc:
        logger.error("job failed: %s", exc)
    return 0
```

**Better approach**

```python
def main() -> int:
    try:
        run_job()
    except OSError as exc:
        logger.error("job failed: %s", exc)
        return 1
    return 0
```

**Production lesson**

Outcome and exit status must agree.

## Anti-pattern 9 — Returning exit code 0 after failure

**Problem**

A failure path falls through to success.

**Why it is harmful**

CI/CD and shell scripts may continue incorrectly.

**Better approach**

Return a deliberate non-zero status.

**Production lesson**

Exit status is machine-readable outcome.

## Anti-pattern 10 — Random exit codes without meaning

**Problem**

Every branch invents a number.

**Why it is harmful**

Operators cannot interpret the contract.

**Better approach**

Use a small documented taxonomy.

**Production lesson**

Exit codes are an interface.

## Anti-pattern 11 — Exposing sensitive details in errors

**Problem**

Secrets appear in exceptions or stderr.

**Why it is harmful**

Error output may be copied into CI logs, tickets, files, or monitoring systems.

**Bad example**

```python
raise ValueError(f"API key is invalid: {api_key}")
```

**Better approach**

```python
raise ValueError("API authentication configuration is invalid")
```

**Production lesson**

Diagnostics must be safe to expose to their intended audience.

## Anti-pattern 12 — Catching `BaseException`

**Problem**

The application treats interpreter control-flow exceptions as ordinary application failures.

**Why it is harmful**

It can interfere with termination and interruption semantics.

**Bad example**

```python
try:
    run()
except BaseException:
    return 1
```

**Better approach**

Catch specific ordinary exceptions, and use `Exception` only at a deliberate top-level boundary when needed.

**Production lesson**

Do not collapse all interpreter control flow into one error bucket.

## Anti-pattern 13 — Deeply nested exception handling

**Problem**

Every layer catches and re-wraps the previous layer.

**Why it is harmful**

The failure path becomes hard to understand.

**Better approach**

Let errors propagate until a layer has meaningful responsibility.

**Production lesson**

Exception ownership should follow recovery responsibility.

## Anti-pattern 14 — Mixing user output and diagnostics carelessly

**Problem**

Machine-readable output and diagnostics share stdout.

**Why it is harmful**

Pipelines can misinterpret diagnostic text as data.

**Better approach**

Use stdout for primary output and stderr for diagnostics when the CLI contract calls for that separation.

**Production lesson**

Output streams are part of CLI design.

---

# 38. Testing Validation and Errors

Validation is executable behavior and should be tested as a contract.

At minimum test:

```text
valid input
invalid input
missing input
boundary values
wrong types
malformed values
custom exceptions
```

With pytest:

```python
import pytest


def parse_age(raw_age: str) -> int:
    if not raw_age.strip():
        raise ValueError("age is required")

    try:
        age = int(raw_age)
    except ValueError as exc:
        raise ValueError("age must be an integer") from exc

    if age < 0:
        raise ValueError("age must be non-negative")

    return age


def test_negative_age_is_rejected():
    with pytest.raises(ValueError):
        parse_age("-1")
```

Test success too:

```python
def test_valid_age_is_returned():
    assert parse_age("42") == 42
```

Test boundaries:

```python
def test_zero_is_valid():
    assert parse_age("0") == 0
```

Test malformed input:

```python
def test_non_integer_is_rejected():
    with pytest.raises(ValueError):
        parse_age("abc")
```

Failure tests are not second-class tests. They define how the program is expected to behave when a contract is violated.

---

# 39. Testing Error Messages

Sometimes the exception type is enough:

```python
with pytest.raises(ValueError):
    parse_age("abc")
```

Sometimes the message is part of the contract:

```python
with pytest.raises(ValueError, match="age must be non-negative"):
    parse_age("-1")
```

The `match=` value is a regular expression pattern.

Use message matching when it protects something meaningful, such as:

```text
important operator guidance
stable public contract
critical diagnosis
```

Avoid unnecessarily brittle tests that depend on every word.

Prefer:

```python
with pytest.raises(ValueError, match="age must be non-negative"):
    parse_age("-1")
```

rather than asserting a very long sentence word-for-word when that exact text is not part of the contract.

A good rule is:

> Test the contract, not every punctuation mark.

---

# 40. Testing Exit Codes

For a real CLI process, use `subprocess.run()`.

Example:

```python
import subprocess
import sys


def test_cli_returns_non_zero_for_invalid_input(tmp_path):
    app = tmp_path / "app.py"
    app.write_text(
        """
import sys


def main():
    try:
        int("not-a-number")
    except ValueError:
        print("invalid integer", file=sys.stderr)
        return 3
    return 0


raise SystemExit(main())
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(app)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 3
    assert "invalid integer" in result.stderr
```

The important `CompletedProcess` attributes are:

```python
result.returncode
result.stdout
result.stderr
```

A unit test may verify:

```python
assert main() == 3
```

A subprocess test verifies the behavior of the actual process boundary.

That is valuable when the command is consumed by:

```text
shell
CI/CD
cron
other programs
batch automation
```

---

# 41. Debugging Validation Failures

Use a repeatable process:

```text
1. Identify the boundary
2. Inspect raw input safely
3. Identify the validation rule
4. Reproduce the failure
5. Check the exception type
6. Read the traceback
7. Decide whether the failure is expected
8. Fix validation or input handling
9. Add a regression test
```

## Boundary

Where did the value first enter the system?

## Raw input

Inspect representations safely.

```python
print(repr(raw_value))
```

Do not inspect secrets this way.

## Rule

Write the intended contract down:

```text
workers must be an integer from 1 through 64
```

## Reproduce

Find the smallest input that reliably triggers the problem.

## Exception type

The type gives a first clue:

```text
ValueError
TypeError
KeyError
OSError
```

## Traceback

A traceback shows where the failure occurred and how execution reached it.

> Read the traceback before searching for an answer.

## Classify

Ask:

```text
Input problem?
Operational problem?
Programmer defect?
```

## Fix and regress

Fix the correct boundary and add a test so the same bug is less likely to return.

---

# 42. Complete Production Example

## Production-Style Data Processing CLI

The example below is self-contained and demonstrates:

- `argparse`;
- validation;
- `ValueError` and custom exceptions;
- exception propagation;
- logging;
- stderr;
- `sys.exit()`;
- application-specific exit codes;
- expected error handling;
- unexpected error handling.

The input contract is:

```text
id,amount
A100,12.50
A101,4.25
```

The program calculates the total amount and prints the primary result to stdout.

## Full code

```python
from __future__ import annotations

import argparse
import csv
import logging
import sys
from enum import IntEnum
from pathlib import Path


logger = logging.getLogger("data_processor")


class ExitCode(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    USAGE_ERROR = 2
    VALIDATION_ERROR = 3
    CONFIGURATION_ERROR = 4


class InputDataError(Exception):
    """Raised when input data violates the application contract."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Process a CSV file containing id and amount columns."
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="path to the input CSV file",
    )
    parser.add_argument(
        "--minimum-total",
        type=float,
        default=0.0,
        help="minimum accepted total amount",
    )
    return parser


def validate_args(args: argparse.Namespace) -> None:
    if args.minimum_total < 0:
        raise ValueError("minimum total must be non-negative")

    if args.input.suffix.lower() != ".csv":
        raise ValueError("input file must use the .csv extension")

    if not args.input.exists():
        raise FileNotFoundError(
            f"input file does not exist: {args.input}"
        )

    if not args.input.is_file():
        raise ValueError(
            f"input path is not a regular file: {args.input}"
        )


def load_rows(path: Path) -> list[dict[str, str]]:
    required_columns = {"id", "amount"}

    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)

            if reader.fieldnames is None:
                raise InputDataError("input CSV has no header row")

            missing = required_columns - set(reader.fieldnames)
            if missing:
                raise InputDataError(
                    f"missing required columns: {sorted(missing)}"
                )

            return list(reader)

    except UnicodeDecodeError as exc:
        raise InputDataError(
            "input file is not valid UTF-8 text"
        ) from exc
    except OSError as exc:
        raise InputDataError(
            "input file could not be read"
        ) from exc


def process_rows(rows: list[dict[str, str]]) -> float:
    total = 0.0

    for row_number, row in enumerate(rows, start=2):
        record_id = row.get("id", "").strip()
        if not record_id:
            raise InputDataError(
                f"row {row_number}: id is required"
            )

        raw_amount = row.get("amount", "").strip()
        if not raw_amount:
            raise InputDataError(
                f"row {row_number}: amount is required"
            )

        try:
            amount = float(raw_amount)
        except ValueError as exc:
            raise InputDataError(
                f"row {row_number}: amount must be numeric"
            ) from exc

        if amount < 0:
            raise InputDataError(
                f"row {row_number}: amount must be non-negative"
            )

        total += amount

    return total


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )


def main() -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args()

    try:
        validate_args(args)
        rows = load_rows(args.input)
        logger.info("loaded %d rows", len(rows))

        total = process_rows(rows)

        if total < args.minimum_total:
            raise InputDataError(
                "processed total is below the required minimum"
            )

    except InputDataError as exc:
        logger.error("input validation failed: %s", exc)
        print(f"Input error: {exc}", file=sys.stderr)
        return int(ExitCode.VALIDATION_ERROR)

    except FileNotFoundError as exc:
        logger.error("input file is unavailable: %s", exc)
        print(f"Input file error: {exc}", file=sys.stderr)
        return int(ExitCode.VALIDATION_ERROR)

    except ValueError as exc:
        logger.error("argument validation failed: %s", exc)
        print(f"Argument error: {exc}", file=sys.stderr)
        return int(ExitCode.USAGE_ERROR)

    except OSError as exc:
        logger.error("operating-system error: %s", exc)
        print(
            "Operating-system error while processing input.",
            file=sys.stderr,
        )
        return int(ExitCode.GENERAL_ERROR)

    except Exception:
        logger.exception("unexpected application failure")
        print("Application failed unexpectedly.", file=sys.stderr)
        return int(ExitCode.GENERAL_ERROR)

    print(f"total={total:.2f}")
    logger.info("processing completed successfully")
    return int(ExitCode.SUCCESS)


if __name__ == "__main__":
    sys.exit(main())
```

## Walkthrough

### Imports

```python
import argparse
import csv
import logging
import sys
from enum import IntEnum
from pathlib import Path
```

These correspond to concrete concerns:

```text
argparse → command-line parsing
csv      → CSV input
logging  → operational evidence
sys      → stderr and process exit
IntEnum  → named exit codes
Path     → filesystem paths
```

### Exit-code design

```python
class ExitCode(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    USAGE_ERROR = 2
    VALIDATION_ERROR = 3
    CONFIGURATION_ERROR = 4
```

The values are application-specific.

### Parsing versus validation

`argparse` handles:

```python
parser.add_argument("--input", type=Path, required=True)
```

That converts the representation into a `Path` and checks that the option was supplied.

`validate_args()` then checks domain rules such as:

```text
CSV suffix
file exists
input path is a file
minimum total is non-negative
```

### File handling

`load_rows()` catches low-level input problems and translates them to `InputDataError` when that creates a useful domain abstraction.

### Row handling

`process_rows()` validates each row and includes the row number in the error, which is useful for diagnosis.

### Top-level ownership

`main()` owns the final decision about:

```text
what gets logged
what the user sees on stderr
which exit code is returned
```

That is why it is an appropriate boundary for the broad `Exception` handler.

### Why specific handlers precede broad handlers

`FileNotFoundError` is an `OSError` subclass. Therefore the more specific handler must come before `OSError`.

Likewise, `Exception` is broad and should come last.

## Success path

```text
parse
→ validate
→ load
→ row validation
→ process
→ print result
→ return 0
```

## Expected failure path

```text
invalid input
→ specific exception
→ log
→ stderr
→ non-zero exit
```

## Unexpected failure path

```text
unexpected defect
→ logger.exception()
→ concise stderr message
→ non-zero exit
```

This avoids pretending the program succeeded.

---

# 43. Exit Code Design Example

A simple application-specific scheme is:

```text
0 → success
1 → general application failure
2 → invalid command-line usage
3 → input data validation failure
4 → configuration failure
```

Again, these are example design choices.

Use named constants:

```python
from enum import IntEnum


class ExitCode(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    USAGE_ERROR = 2
    VALIDATION_ERROR = 3
    CONFIGURATION_ERROR = 4
```

Then:

```python
def main() -> int:
    try:
        validate_input()
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return int(ExitCode.VALIDATION_ERROR)

    return int(ExitCode.SUCCESS)
```

and:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

## Design rules

1. Reserve `0` for success unless a surrounding convention requires otherwise.
2. Keep non-zero meanings documented.
3. Avoid unnecessary categories.
4. Make automation behavior stable.
5. Keep the mapping close to the CLI contract.

An enum is optional. Simple constants can also be sufficient for a small script.

---

# 44. Coding Example Requirements

Every significant concept should be accompanied by an example when code makes the idea clearer.

Good examples are:

- syntactically valid;
- runnable or easily adapted to run;
- progressively more advanced;
- focused on one idea;
- explained before or after the code;
- explicit about expected and failure behavior.

For a major example, answer:

```text
What problem are we solving?
Why is this approach used?
What happens internally?
What happens for valid input?
What happens for invalid input?
What happens for unexpected failure?
What exit code is returned?
```

A useful sequence is:

```text
small validation check
→ reusable validation function
→ custom exception
→ propagation
→ CLI parsing
→ top-level error handling
→ exit-code testing
→ complete production example
```

Avoid unexplained large code blocks. A production example should be read in pieces.

---

# 45. Function/API Coverage Requirement

The goal is practical mastery, not an exhaustive catalog.

## Built-in validation helpers

### `isinstance()`

```python
isinstance(value, str)
```

Useful when runtime type membership is part of the contract.

### `type()`

```python
type(value)
```

Useful for inspection and for cases where exact type identity is truly required.

### `len()`

```python
len(value)
```

Useful for size or length constraints.

## Exception mechanisms

```text
raise
try
except
else
finally
```

## Relevant exceptions

```text
ValueError
TypeError
KeyError
IndexError
FileNotFoundError
PermissionError
OSError
Exception
SystemExit
```

## CLI APIs

```python
argparse.ArgumentParser(...)
parser.add_argument(...)
parser.parse_args()
```

Relevant options:

```text
type=
choices=
required=
default=
```

## Exit handling

```python
sys.exit()
SystemExit
```

## Testing

```python
pytest.raises()
subprocess.run()
```

and:

```python
CompletedProcess.returncode
CompletedProcess.stdout
CompletedProcess.stderr
```

The learner should be able to use these APIs to build a practical CLI without memorizing unrelated details.

---

# 46. Concept → Internal Mechanics → Practice

For every major idea, use this sequence:

```text
1. What is it?
2. Why does it exist?
3. Simple analogy
4. Technical definition
5. How Python handles it
6. Small code example
7. Expected behavior
8. Common mistake
9. Production use
10. Practice exercise
```

## Validation

```text
What?
= check a contract

Why?
= establish trusted input before deeper logic

Analogy
= checkpoint at a system entrance

Mechanics
= explicit checks, parsing, and rejection

Practice
= parse-and-validate functions
```

## Exceptions

```text
What?
= Python failure signaling

Why?
= separate failures from ordinary return values

Mechanics
= raise → search outward for handler

Practice
= catch specific exceptions
```

## Propagation

```text
What?
= unhandled exception travels outward

Why?
= a higher layer may own recovery/communication

Mechanics
= handlers are searched through caller contexts

Practice
= trace a failure through three functions
```

## Custom exceptions

```text
What?
= application-specific exception type

Why?
= meaningful domain-level handling

Mechanics
= subclass Exception or an application base

Practice
= ConfigurationError
```

## `sys.exit()`

```text
What?
= request interpreter termination

Why?
= communicate CLI result

Mechanics
= raises SystemExit

Practice
= test process status
```

## Exit codes

```text
What?
= numeric process result

Why?
= automation needs machine-readable status

Mechanics
= process reports status

Practice
= documented 0/non-zero contract
```

---

# 47. Exercises

The following exercises move from basic checks to production-oriented design.

## Exercise 1 — Validate an integer

### Problem

Write `validate_count()`.

### Requirements

- accept an integer;
- reject negative values with `ValueError`;
- return valid values unchanged.

### Hints

Use an explicit range check.

### Expected behavior

```text
0  → valid
5  → valid
-1 → ValueError
```

### Solution

```python
def validate_count(count: int) -> int:
    if count < 0:
        raise ValueError("count must be non-negative")
    return count
```

### Explanation

The function establishes a simple postcondition: a normal return means the count is non-negative.

---

## Exercise 2 — Reject empty text

### Problem

Validate a user-provided name.

### Requirements

- strip surrounding whitespace;
- reject an empty result;
- return the cleaned string.

### Hints

Use `strip()` before checking presence.

### Expected behavior

```text
" Alice " → "Alice"
"   "     → ValueError
```

### Solution

```python
def validate_name(value: str) -> str:
    value = value.strip()

    if not value:
        raise ValueError("name is required")

    return value
```

### Explanation

The boundary converts a messy external string into a cleaner internal string.

---

## Exercise 3 — Range validation

### Problem

Validate a percentage.

### Requirements

Accept only integers from 0 through 100 inclusive.

### Hints

Use a chained comparison.

### Expected behavior

```text
0   → valid
50  → valid
100 → valid
-1  → invalid
101 → invalid
```

### Solution

```python
def validate_percentage(value: int) -> int:
    if not 0 <= value <= 100:
        raise ValueError("percentage must be between 0 and 100")
    return value
```

### Explanation

Both endpoints are allowed because the rule uses `<=`.

---

## Exercise 4 — Parse and validate an age

### Problem

Create `parse_age()`.

### Requirements

- reject blank text;
- convert to integer;
- reject negative values.

### Hints

Use `int()` inside a narrow `try` block.

### Expected behavior

```text
"42"  → 42
"abc" → ValueError
"-1"  → ValueError
" "   → ValueError
```

### Solution

```python
def parse_age(raw_age: str) -> int:
    raw_age = raw_age.strip()

    if not raw_age:
        raise ValueError("age is required")

    try:
        age = int(raw_age)
    except ValueError as exc:
        raise ValueError("age must be an integer") from exc

    if age < 0:
        raise ValueError("age must be non-negative")

    return age
```

### Explanation

This function follows:

```text
presence
→ parse
→ validate
→ return trusted value
```

---

## Exercise 5 — Catch a specific exception

### Problem

Return a simple status after attempting integer parsing.

### Requirements

- catch `ValueError`;
- do not catch unrelated exceptions;
- return `"invalid"` for malformed numbers.

### Hints

Use `except ValueError`.

### Expected behavior

```text
"42"  → "valid"
"abc" → "invalid"
```

### Solution

```python
def parse_or_report(raw_value: str) -> str:
    try:
        int(raw_value)
    except ValueError:
        return "invalid"

    return "valid"
```

### Explanation

Only the expected parsing failure is handled.

---

## Exercise 6 — Type and range validation

### Problem

Validate a worker count.

### Requirements

- input must be an integer;
- `True` and `False` must be rejected;
- valid range is 1 through 64.

### Hints

Remember that `bool` is a subclass of `int`.

### Expected behavior

```text
1     → valid
64    → valid
0     → invalid
65    → invalid
True  → invalid
```

### Solution

```python
def validate_workers(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("workers must be an integer")

    if not 1 <= value <= 64:
        raise ValueError("workers must be between 1 and 64")

    return value
```

### Explanation

This example demonstrates why a type rule may require more than one `isinstance()` check.

---

## Exercise 7 — Custom exception

### Problem

Create `ConfigurationError` and use it for missing configuration.

### Requirements

- inherit from `Exception`;
- reject missing/blank model names.

### Hints

Keep the exception class small.

### Expected behavior

Blank or missing model name raises `ConfigurationError`.

### Solution

```python
class ConfigurationError(Exception):
    """Raised when required configuration is invalid."""


def require_model_name(model_name: str | None) -> str:
    if model_name is None or not model_name.strip():
        raise ConfigurationError("MODEL_NAME is required")
    return model_name.strip()
```

### Explanation

The caller now has a stable domain-level exception type to catch.

---

## Exercise 8 — `argparse` choices

### Problem

Create a CLI environment option.

### Requirements

Accept only `dev`, `test`, and `prod`.

### Hints

Use `choices=` and `required=`.

### Expected behavior

Unsupported values should be rejected by the parser.

### Solution

```python
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    "--environment",
    choices=["dev", "test", "prod"],
    required=True,
)

args = parser.parse_args()
print(args.environment)
```

### Explanation

`argparse` can own fixed CLI-level value constraints.

---

## Exercise 9 — Custom `argparse` validation

### Problem

Build `positive_int()` for `--workers`.

### Requirements

- parse integers;
- reject zero and negatives;
- use `argparse.ArgumentTypeError`.

### Hints

Catch conversion failure narrowly.

### Expected behavior

```text
"4" → 4
"0" → parser error
"abc" → parser error
```

### Solution

```python
import argparse


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "must be an integer"
        ) from exc

    if number <= 0:
        raise argparse.ArgumentTypeError("must be positive")

    return number
```

### Explanation

The function is both a parser and validator for one CLI argument.

---

## Exercise 10 — `pytest.raises()`

### Problem

Test rejection of a negative age.

### Requirements

Use `pytest.raises()`.

### Hints

Call the function inside the context manager.

### Expected behavior

The test passes only when `ValueError` is raised.

### Solution

```python
import pytest


def test_negative_age_is_rejected():
    with pytest.raises(ValueError):
        parse_age("-1")
```

### Explanation

The test records failure behavior as a deliberate contract.

---

## Exercise 11 — Test the error message

### Problem

Verify the negative-age error message.

### Requirements

Use `match=`.

### Solution

```python
def test_negative_age_message():
    with pytest.raises(
        ValueError,
        match="age must be non-negative",
    ):
        parse_age("-1")
```

### Explanation

This protects a meaningful part of the error contract without requiring exact punctuation for the entire exception string.

---

## Exercise 12 — Return a non-zero exit status

### Problem

Create `main()` that validates an age string.

### Requirements

- return `0` when valid;
- write the error to stderr;
- return `3` when invalid.

### Solution

```python
import sys


def main(raw_age: str) -> int:
    try:
        age = int(raw_age)
    except ValueError:
        print("age must be an integer", file=sys.stderr)
        return 3

    if age < 0:
        print("age must be non-negative", file=sys.stderr)
        return 3

    print(age)
    return 0
```

### Explanation

Returning an integer from `main()` keeps the function easy to unit test.

---

## Exercise 13 — Test CLI status with subprocess

### Problem

Test the real process result.

### Requirements

Inspect `returncode` and `stderr`.

### Solution

```python
import subprocess
import sys


def test_cli_failure(tmp_path):
    app = tmp_path / "app.py"
    app.write_text(
        """
import sys


def main():
    print("invalid input", file=sys.stderr)
    return 3


raise SystemExit(main())
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(app)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 3
    assert "invalid input" in result.stderr
```

### Explanation

This tests the actual process boundary, not only a Python function return value.

---

## Exercise 14 — Distinguish input error from bug

### Problem

Create a top-level error handler.

### Requirements

- `ValueError` returns `3`;
- unexpected `Exception` returns `1`;
- unexpected failure must not be labeled "invalid input".

### Solution

```python
import sys


def main() -> int:
    try:
        run_application()
    except ValueError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 3
    except Exception:
        print("unexpected application failure", file=sys.stderr)
        return 1

    return 0
```

### Explanation

The failure classes remain distinct at the CLI boundary.

---

## Exercise 15 — Validate an AI tool request

### Problem

Validate a model-generated tool argument dictionary.

### Requirements

- require `path`;
- require a string;
- reject blank strings;
- return cleaned path.

### Solution

```python
def validate_tool_call(arguments: dict[str, object]) -> str:
    if "path" not in arguments:
        raise ValueError("tool argument 'path' is required")

    raw_path = arguments["path"]

    if not isinstance(raw_path, str):
        raise TypeError("tool argument 'path' must be a string")

    path = raw_path.strip()

    if not path:
        raise ValueError("tool argument 'path' cannot be empty")

    return path
```

### Explanation

The model output is treated as external data until validation establishes a stronger internal contract.

---

# 48. Mini Project

# Production-Style Validated Data Processing CLI

## Project Goal

Build a self-contained CLI that reads a CSV file, validates configuration and data, processes valid input, logs safely, reports errors on stderr, and returns meaningful exit codes.

## Required flow

```text
CLI arguments
    ↓
input validation
    ↓
configuration validation
    ↓
file validation
    ↓
data validation
    ↓
processing
    ↓
safe logging
    ↓
error handling
    ↓
exit code
```

## Requirements

The mini project must:

- accept an input file;
- accept an environment (`dev`, `test`, or `prod`);
- validate the environment;
- validate file existence;
- validate file type;
- validate required CSV headers;
- validate every row;
- process numeric amounts;
- print the primary result to stdout;
- send diagnostic errors to stderr;
- use safe logging;
- avoid exposing credentials or unnecessary sensitive data;
- return `0` on success;
- return non-zero on failure;
- avoid silently swallowing unexpected errors;
- include tests for success and failure paths.

## Architecture

```text
                   ┌─────────────────────┐
                   │    CLI Arguments    │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │       Parsing       │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │ Configuration Rules │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │   File Boundary     │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │ Schema + Row Rules  │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │      Processing     │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │ Log + Communicate   │
                   └──────────┬──────────┘
                              ↓
                   ┌─────────────────────┐
                   │     Exit Status     │
                   └─────────────────────┘
```

## Step-by-Step Tasks

### Task 1 — Exit-code model

Use an `IntEnum` or constants.

### Task 2 — CLI parser

Use `ArgumentParser`, `add_argument`, and `parse_args`.

### Task 3 — Environment validation

Accept only:

```text
dev
test
prod
```

### Task 4 — Path validation

Check existence and file type.

### Task 5 — Header validation

Require:

```text
id
amount
```

### Task 6 — Row validation

Require:

```text
non-empty id
present amount
numeric amount
non-negative amount
```

### Task 7 — Processing

Calculate a total.

### Task 8 — Logging

Log important lifecycle events without secrets.

### Task 9 — Expected failures

Translate known validation and operational conditions into useful stderr messages and non-zero statuses.

### Task 10 — Unexpected failures

Preserve diagnostics through top-level logging and return failure.

## Expected behavior

Valid input:

```text
id,amount
A100,12.50
A101,4.25
```

produces:

```text
total=16.75
```

and exit code `0`.

Malformed input should produce a row-specific error on stderr and a non-zero code.

Missing input should produce a clear failure and a non-zero code.

Unexpected failures should not be silently converted into success.

## Reference solution

```python
from __future__ import annotations

import argparse
import csv
import logging
import sys
from enum import IntEnum
from pathlib import Path


logger = logging.getLogger("validated_processor")


class ExitCode(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    USAGE_ERROR = 2
    VALIDATION_ERROR = 3
    CONFIGURATION_ERROR = 4


class ConfigurationError(Exception):
    """Raised when application configuration is invalid."""


class InputDataError(Exception):
    """Raised when input data violates the processing contract."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process a validated CSV dataset."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--environment",
        choices=["dev", "test", "prod"],
        required=True,
    )
    return parser.parse_args()


def validate_configuration(args: argparse.Namespace) -> None:
    if args.environment not in {"dev", "test", "prod"}:
        raise ConfigurationError(
            "environment must be dev, test, or prod"
        )


def load_and_validate(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise InputDataError(
            f"input file does not exist: {path}"
        )

    if not path.is_file():
        raise InputDataError(
            f"input path is not a regular file: {path}"
        )

    if path.suffix.lower() != ".csv":
        raise InputDataError(
            "input file must use the .csv extension"
        )

    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)

            if reader.fieldnames is None:
                raise InputDataError(
                    "input CSV has no header row"
                )

            required = {"id", "amount"}
            missing = required - set(reader.fieldnames)

            if missing:
                raise InputDataError(
                    f"missing required columns: {sorted(missing)}"
                )

            return list(reader)

    except UnicodeDecodeError as exc:
        raise InputDataError(
            "input file is not valid UTF-8"
        ) from exc
    except OSError as exc:
        raise InputDataError(
            "input file could not be read"
        ) from exc


def process_rows(rows: list[dict[str, str]]) -> float:
    total = 0.0

    for row_number, row in enumerate(rows, start=2):
        record_id = row.get("id", "").strip()

        if not record_id:
            raise InputDataError(
                f"row {row_number}: id is required"
            )

        raw_amount = row.get("amount", "").strip()

        if not raw_amount:
            raise InputDataError(
                f"row {row_number}: amount is required"
            )

        try:
            amount = float(raw_amount)
        except ValueError as exc:
            raise InputDataError(
                f"row {row_number}: amount must be numeric"
            ) from exc

        if amount < 0:
            raise InputDataError(
                f"row {row_number}: amount must be non-negative"
            )

        total += amount

    return total


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )


def main() -> int:
    configure_logging()

    try:
        args = parse_args()
        validate_configuration(args)

        logger.info("starting input processing")
        rows = load_and_validate(args.input)
        logger.info("loaded %d rows", len(rows))

        total = process_rows(rows)

    except ConfigurationError as exc:
        logger.error("configuration failed: %s", exc)
        print(f"Configuration error: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIGURATION_ERROR)

    except InputDataError as exc:
        logger.error("input validation failed: %s", exc)
        print(f"Input error: {exc}", file=sys.stderr)
        return int(ExitCode.VALIDATION_ERROR)

    except Exception:
        logger.exception("unexpected processing failure")
        print(
            "Processing failed unexpectedly.",
            file=sys.stderr,
        )
        return int(ExitCode.GENERAL_ERROR)

    print(f"total={total:.2f}")
    logger.info("processing completed successfully")
    return int(ExitCode.SUCCESS)


if __name__ == "__main__":
    sys.exit(main())
```

## Explanation

The entry-point design is:

```text
main()
→ returns integer
→ sys.exit(main())
→ process receives status
```

The code separates responsibilities:

```text
parse
→ CLI syntax

validate_configuration
→ configuration contract

load_and_validate
→ file + schema contract

process_rows
→ row + domain contract

main
→ final communication and exit status
```

## Testing strategy

Test unit-level rules:

```python
import pytest


def test_negative_amount_is_rejected():
    rows = [{"id": "A100", "amount": "-1"}]

    with pytest.raises(InputDataError, match="non-negative"):
        process_rows(rows)
```

Test success:

```python
def test_valid_rows_are_processed():
    rows = [
        {"id": "A100", "amount": "2.5"},
        {"id": "A101", "amount": "1.5"},
    ]

    assert process_rows(rows) == 4.0
```

Test CLI behavior separately with subprocess.

## Production improvements

A larger production implementation may add:

- typed domain objects;
- more precise numeric handling when money is involved;
- richer configuration management;
- structured logs;
- metrics;
- input-size limits;
- stronger authorization around AI/tool inputs;
- operational documentation.

The core boundary and error principles remain the same.

---

# 49. Interview Questions

Each question includes:

```text
Question
How to Think
Answer
Why It Matters
```

## Basic

### 1. What is input validation?

**How to Think**

Think in terms of an input contract.

**Answer**

Input validation checks whether data satisfies the rules required before the program uses it.

**Why It Matters**

It prevents invalid assumptions from entering deeper code.

### 2. Why validate input?

**How to Think**

Ask what happens if later code assumes the input is correct.

**Answer**

Validation rejects contract violations near their source and helps create trusted internal representations.

**Why It Matters**

Early failures are generally easier to understand and test.

### 3. What is an exception?

**How to Think**

Compare failure signaling with normal returns.

**Answer**

An exception is Python's mechanism for reporting that normal execution cannot continue in the current way.

**Why It Matters**

It lets failure information propagate to a layer that can handle it.

### 4. What does `raise` do?

**How to Think**

Think about control flow.

**Answer**

It signals an exception and interrupts normal execution of the current block.

**Why It Matters**

It is the main explicit failure mechanism in Python.

### 5. What is `ValueError`?

**How to Think**

Distinguish value from type.

**Answer**

It commonly indicates that an operation received a value that is inappropriate even though the general type is acceptable.

**Why It Matters**

Exception types communicate intent.

### 6. What is an exit code?

**How to Think**

Ask what the operating system or shell receives.

**Answer**

An exit code is the numeric status a CLI process reports when it terminates.

**Why It Matters**

Automation can use it without parsing human prose.

## Intermediate

### 7. Difference between `ValueError` and `TypeError`?

**How to Think**

Ask whether the type itself violates the contract.

**Answer**

`TypeError` commonly concerns an inappropriate type; `ValueError` commonly concerns an inappropriate value for an otherwise acceptable type.

**Why It Matters**

The distinction improves handling and diagnosis.

### 8. What is exception propagation?

**How to Think**

Visualize the call stack.

**Answer**

When a matching handler is not found in the current context, the exception moves outward through callers until handled or uncaught.

**Why It Matters**

Lower layers can signal failure without knowing the final communication policy.

### 9. Why use `else` in `try/except/else`?

**How to Think**

Separate the risky operation from success-only work.

**Answer**

`else` runs only when `try` succeeds.

**Why It Matters**

It reduces accidental catching of exceptions from unrelated success-path code.

### 10. What is `finally` for?

**How to Think**

Think cleanup that should happen regardless of success/failure.

**Answer**

`finally` runs after the `try`/`except` processing whether or not an exception occurred.

**Why It Matters**

It supports reliable cleanup.

### 11. What is a custom exception?

**How to Think**

Ask whether the failure has domain meaning.

**Answer**

It is an application-defined exception class that represents a meaningful domain failure.

**Why It Matters**

Callers can catch a meaningful type instead of inspecting strings.

### 12. Why validate external input at the boundary?

**How to Think**

Find where uncertainty enters.

**Answer**

Boundary validation establishes stronger internal assumptions before deeper logic relies on them.

**Why It Matters**

It localizes errors and reduces hidden assumptions.

### 13. What does `sys.exit()` do?

**How to Think**

Connect it to `SystemExit`.

**Answer**

`sys.exit()` raises `SystemExit` with a requested status; when uncaught at the top level, the interpreter terminates with that status.

**Why It Matters**

That is how Python CLIs communicate process results.

## Advanced

### 14. When should an exception be handled versus propagated?

**How to Think**

Who can recover or communicate it meaningfully?

**Answer**

Handle where recovery, translation, or communication is meaningful. Otherwise, propagate.

**Why It Matters**

It prevents both swallowing failures and overcomplicated local handling.

### 15. Why is indiscriminate `except Exception:` dangerous?

**How to Think**

Ask what information gets collapsed.

**Answer**

It can catch expected errors and programmer defects together, hide tracebacks, and cause misleading success or error messages.

**Why It Matters**

A top-level boundary can use it deliberately, but local blanket catches are risky.

### 16. How should a CLI distinguish validation failures from unexpected failures?

**How to Think**

Start with error classification.

**Answer**

Handle known validation errors with clear diagnostics and documented non-zero codes; unexpected failures should remain diagnosable and also return non-zero.

**Why It Matters**

Automation and operators need accurate outcomes.

### 17. Why are exit codes important in automation?

**How to Think**

Automation needs a machine-readable status.

**Answer**

Exit codes provide a compact process result that shells and workflow tools can evaluate.

**Why It Matters**

Human-readable messages are not a reliable control signal for automation.

### 18. How would you design error handling for a data pipeline?

**How to Think**

Begin at the data boundary.

**Answer**

Validate structure and rows early, classify failures, decide which errors stop the job, record safe diagnostics, and return non-zero when the job fails according to its contract.

**Why It Matters**

Invalid data can otherwise propagate into downstream outputs.

### 19. How would you validate model-generated tool arguments?

**How to Think**

Treat them as external input.

**Answer**

Parse the result, validate fields and types, apply domain/security/authorization rules, and only then execute the tool.

**Why It Matters**

Model output is not automatically trusted application data.

### 20. Why use exception chaining?

**How to Think**

Separate low-level cause from high-level meaning.

**Answer**

Chaining preserves the original cause while presenting a higher-level domain exception.

**Why It Matters**

It improves diagnosis without exposing lower-level details to every caller.

---

# 50. Architecture Questions

## 1. How would you design validation for a Python data-processing CLI?

**Structured answer**

Use layered boundaries:

```text
CLI parse
→ configuration validation
→ filesystem validation
→ schema validation
→ row validation
→ processing
→ top-level error translation
→ exit code
```

Keep the rules near the boundary that owns them.

## 2. Where should validation happen?

**Structured answer**

As close as practical to the boundary where external data enters a trusted internal layer. Separate parsing, validation, and domain logic where that improves testability and clarity.

## 3. How do you distinguish invalid user input from a programmer bug?

**Structured answer**

Use the contract and failure cause. A documented input rule violation is a validation failure. An unexpected internal exception such as an impossible-state `AttributeError` is generally a defect. Do not relabel defects as input errors.

## 4. How would you design a CLI exit-code strategy?

**Structured answer**

Reserve `0` for success, choose a small set of documented non-zero codes, map them to meaningful categories, and test the real process behavior.

## 5. How should errors flow through multiple layers?

**Structured answer**

Lower layers raise accurate exceptions. Intermediate layers may translate them to domain exceptions with chaining. The top-level layer decides user-facing messaging and exit status.

## 6. Where should exceptions be caught?

**Structured answer**

Catch where the application can meaningfully recover, translate, or communicate the failure. Do not catch merely to stop propagation.

## 7. How would you prevent unexpected exceptions from being silently swallowed?

**Structured answer**

Use specific handlers, avoid blanket catches in local code, test failure paths, log unexpected failures at the top boundary, and return non-zero on failure.

## 8. How would you design validation for configuration?

**Structured answer**

Parse raw settings, validate presence/type/range/allowed values, build a validated configuration object, and fail before expensive startup or processing.

## 9. How would you design validation for an AI tool invocation?

**Structured answer**

Parse model output, validate schema and type, apply business/security/authorization rules, reject unsupported values, then execute.

## 10. How would you make a CLI safe for CI/CD automation?

**Structured answer**

Define deterministic CLI syntax, stable exit codes, clean stdout/stderr separation, non-zero failure status, and subprocess tests.

## 11. How do logging, exceptions, and exit codes work together?

**Structured answer**

```text
Exception
= internal failure signal

Logging
= operational evidence

Exit code
= external process result
```

They complement one another rather than substitute for one another.

---

# 51. Debugging Scenarios

## Scenario 1 — Program reports success despite failure

**Problem**

The program prints an error but returns code `0`.

**How to Think**

Trace every return path from the failure handler to the entry point.

**Diagnosis**

Likely code such as:

```python
def main() -> int:
    try:
        run_job()
    except Exception:
        print("failed")
        return 1

    return 0
```

**Solution**

Return a non-zero status on failure.

**Production Lesson**

Human-readable failure and machine-readable success must not disagree.

## Scenario 2 — CLI always returns exit code 0

**Problem**

Automation reports success for every invocation.

**How to Think**

Inspect `main()`, exception handlers, and the `sys.exit(main())` entry point.

**Diagnosis**

A failure path may fall through to a final `return 0`, or `SystemExit` may not be used as intended.

**Solution**

Make every terminal failure path return a documented non-zero code.

**Production Lesson**

Test process status explicitly.

## Scenario 3 — Invalid input causes an ugly traceback

**Problem**

An expected CLI validation failure produces a full traceback to the user.

**How to Think**

Ask whether the failure is expected and whether the CLI boundary owns the communication.

**Diagnosis**

The expected exception is propagating out of the CLI without a user-facing handler.

**Solution**

Catch the specific expected exception at the boundary and print a concise stderr message.

**Production Lesson**

User errors can be friendly without hiding unexpected defects.

## Scenario 4 — Programmer bug is reported as invalid input

**Problem**

An `AttributeError` is shown as "invalid input".

**How to Think**

Search for blanket exception handlers.

**Diagnosis**

Likely `except Exception:` is converting unrelated failures into input errors.

**Solution**

Catch known validation exceptions specifically and handle unexpected `Exception` separately at a deliberate top-level boundary.

**Production Lesson**

Misclassification sends debugging effort to the wrong layer.

## Scenario 5 — Validation happens deep inside the application

**Problem**

A bad CLI argument fails inside business logic.

**How to Think**

Identify the original boundary.

**Diagnosis**

The boundary did not establish a sufficient contract before calling deeper code.

**Solution**

Move appropriate parse/validation checks toward the CLI or configuration boundary.

**Production Lesson**

Trusted internal representations simplify deeper code.

## Scenario 6 — All exceptions become `None`

**Problem**

The caller cannot distinguish missing data from failure.

**How to Think**

List every meaning `None` currently carries.

**Diagnosis**

The API has an ambiguous failure contract.

**Solution**

Use specific exceptions or a clearly documented result representation.

**Production Lesson**

Ambiguous signals create downstream bugs.

## Scenario 7 — CLI error output contaminates stdout

**Problem**

A command outputs JSON on stdout but also prints validation errors on stdout.

**How to Think**

Ask what the next program in a pipeline will parse.

**Diagnosis**

Diagnostic data is mixed with primary data.

**Solution**

Send diagnostics to stderr.

**Production Lesson**

Stream semantics are part of the CLI contract.

---

# 52. Knowledge Check

Answer each question before reading the answer.

## 1. What should happen if a user enters an invalid integer?

**Answer**

Reject it with a clear validation error. In a CLI, report the error on stderr and return a non-zero status.

## 2. Why should user input generally not be validated with `assert`?

**Answer**

Assertions are mainly for programmer assumptions/invariants and can be disabled in optimized execution. External validation should be explicit.

## 3. What is the difference between raising an exception and calling `sys.exit()`?

**Answer**

A regular exception signals a failure through Python's exception mechanism. `sys.exit()` raises `SystemExit` to request interpreter termination with a process status.

## 4. What happens when an exception is not caught?

**Answer**

It propagates outward through callers. If it remains uncaught at the top level, the process terminates and normally reports non-zero status.

## 5. Why might a CLI return a non-zero exit code?

**Answer**

Because the command did not complete successfully, such as due to invalid input, configuration failure, operational failure, or unexpected failure.

## 6. When should an exception propagate rather than be caught?

**Answer**

When the current layer cannot meaningfully recover, translate, or communicate it.

## 7. Why is catching `Exception` and returning `None` often dangerous?

**Answer**

It can hide bugs and make multiple unrelated failure states indistinguishable to the caller.

## 8. Why validate model-generated tool arguments?

**Answer**

Because they are external data from the application's perspective and must satisfy application-defined type, schema, security, and domain rules before action.

---

# 53. Production Principles

## Principle 1

> Validate external input at the boundary.

This reduces the distance between a contract violation and its diagnosis.

## Principle 2

> Make invalid states fail clearly.

A clear failure is better than allowing an invalid state to produce a confusing downstream symptom.

## Principle 3

> Catch exceptions where you can meaningfully handle them.

The right handling layer is the layer with recovery or communication responsibility.

## Principle 4

> Do not hide unexpected failures.

Unexpected failures contain information engineers need for diagnosis.

## Principle 5

> Error messages should be useful and safe.

Explain enough to act, but do not leak secrets or unnecessary sensitive details.

## Principle 6

> CLI programs should communicate success/failure predictably.

Stable syntax, streams, and exit behavior are part of the CLI contract.

## Principle 7

> Exit code `0` conventionally means success; non-zero indicates failure.

That convention allows simple machine-readable process checks.

## Principle 8

> Exit-code meanings beyond success/failure should be deliberately designed.

Use documented application-specific semantics rather than random numbers.

## Principle 9

> Logging, exception handling, and exit codes solve different problems.

Keep this separation explicit:

```text
exception
→ internal failure signal

handling
→ decision / recovery / translation

logging
→ evidence

exit code
→ process outcome
```

---

# 54. Final Mental Model

The normal program flow is:

```text
External Input
      ↓
     Parse
      ↓
   Validate
      ↓
Trusted Internal Data
      ↓
 Business Logic
      ↓
    Result
```

Expected/input failure:

```text
Expected / Input Error
      ↓
   Clear Error
      ↓
Appropriate Handling
      ↓
 Non-zero Exit Code
```

Unexpected failure:

```text
Unexpected Failure
      ↓
Useful Diagnostic Logging
      ↓
Exception Propagates / Controlled Top-Level Handling
      ↓
Non-zero Exit Code
```

The key definitions are:

```text
Validation
= "Is this input acceptable?"

Exception
= "Something prevented normal execution."

Error handling
= "What should the program do about the failure?"

Logging
= "What operational evidence should we record?"

Exit code
= "What result should the operating system/caller receive?"
```

Do not confuse these mechanisms.

```text
Validation
→ checks contract

Exception
→ signals failure

Handling
→ decides what to do

Logging
→ records evidence

Exit code
→ communicates process result
```

A production-oriented CLI turns those concepts into a stable boundary.

---

# 55. Completion Checklist

## Validation Fundamentals

- [ ] I understand what validation means.
- [ ] I understand input boundaries.
- [ ] I can distinguish valid, missing, malformed, and invalid data.
- [ ] I can validate types.
- [ ] I can validate presence.
- [ ] I can validate formats.
- [ ] I can validate ranges.
- [ ] I can validate allowed values.
- [ ] I can validate relationships between fields.
- [ ] I understand parse versus validate.
- [ ] I know why validation should happen at the boundary.

## Assertions and Exceptions

- [ ] I understand assertions versus validation.
- [ ] I know why `assert` is not a durable external-input validation mechanism.
- [ ] I understand what an exception is.
- [ ] I can use `raise`.
- [ ] I can catch specific exceptions.
- [ ] I understand `try`.
- [ ] I understand `except`.
- [ ] I understand `else`.
- [ ] I understand `finally`.
- [ ] I understand exception propagation.
- [ ] I can explain `ValueError`.
- [ ] I can explain `TypeError`.
- [ ] I can explain `KeyError`.
- [ ] I can explain `IndexError`.
- [ ] I can explain `FileNotFoundError`.
- [ ] I can explain `PermissionError`.
- [ ] I can explain `OSError`.
- [ ] I understand why broad exception handling can be dangerous.
- [ ] I know why ordinary application code should not catch `BaseException` indiscriminately.
- [ ] I can define custom exceptions.
- [ ] I understand exception chaining.

## CLI

- [ ] I understand `sys.argv`.
- [ ] I can use `argparse.ArgumentParser`.
- [ ] I can use `parser.add_argument`.
- [ ] I can use `parser.parse_args`.
- [ ] I understand `type=`.
- [ ] I understand `choices=`.
- [ ] I understand `required=`.
- [ ] I understand `default=`.
- [ ] I can implement custom CLI validation.
- [ ] I understand `sys.exit()`.
- [ ] I understand `SystemExit`.
- [ ] I understand exit codes.
- [ ] I understand stdout versus stderr.
- [ ] I can design predictable CLI behavior.

## Configuration and Files

- [ ] I can validate configuration early.
- [ ] I can validate required configuration.
- [ ] I can validate file existence.
- [ ] I can validate file/path constraints.
- [ ] I can validate headers/schema.
- [ ] I can validate rows.

## Data and Applied AI

- [ ] I understand fail-fast validation for critical data errors.
- [ ] I understand when collecting multiple errors is useful.
- [ ] I understand why skipped invalid rows should be explicit.
- [ ] I can validate AI tool arguments.
- [ ] I treat model-generated output as untrusted downstream input.
- [ ] I can distinguish input errors, operational errors, and defects.

## Logging and Communication

- [ ] I understand handle + log + communicate.
- [ ] I can log errors safely.
- [ ] I can avoid logging sensitive information.
- [ ] I understand why stderr is useful for diagnostics.

## Testing

- [ ] I can test valid input.
- [ ] I can test invalid input.
- [ ] I can test boundary values.
- [ ] I can use `pytest.raises()`.
- [ ] I can test useful error messages.
- [ ] I can use `subprocess.run()`.
- [ ] I can inspect `returncode`.
- [ ] I can inspect `stdout` and `stderr`.

## Production

- [ ] I can distinguish expected errors from unexpected failures.
- [ ] I can design useful error messages.
- [ ] I avoid swallowing exceptions.
- [ ] I avoid returning `None` for unrelated failure states.
- [ ] I can design a small exit-code taxonomy.
- [ ] I can explain boundary validation aloud.
- [ ] I can debug validation failures by reading the traceback first.
- [ ] I add regression tests after fixing bugs.

---

# 56. Final Self-Review

## Coverage

This chapter teaches:

- validation;
- input boundaries;
- valid versus invalid data;
- missing versus unexpected input;
- validation strategies;
- assertions versus validation;
- exceptions;
- relevant exception types;
- `raise`;
- `try`;
- `except`;
- `else`;
- `finally`;
- exception propagation;
- custom exceptions;
- exception chaining;
- expected versus unexpected failures;
- CLI validation;
- `sys.argv`;
- `argparse`;
- `sys.exit()`;
- `SystemExit`;
- exit codes;
- stdout;
- stderr;
- predictable CLI behavior;
- configuration validation;
- file validation;
- data pipeline validation;
- Applied AI validation;
- logging/error relationship;
- testing;
- debugging;
- production error handling.

## API Coverage

Relevant APIs are present and demonstrated where appropriate:

```text
isinstance()
type()
len()

raise
try
except
else
finally

ValueError
TypeError
KeyError
IndexError
FileNotFoundError
PermissionError
OSError
Exception
SystemExit

argparse.ArgumentParser
parser.add_argument
parser.parse_args

type=
choices=
required=
default=

sys.exit()

pytest.raises()
subprocess.run()

CompletedProcess.returncode
CompletedProcess.stdout
CompletedProcess.stderr
```

## Practicality

The file includes:

- beginner examples;
- intermediate examples;
- advanced examples;
- bad versus better patterns;
- progressive exercises;
- solutions and explanations;
- a production-style mini-project;
- interview questions;
- architecture questions;
- debugging scenarios;
- knowledge checks;
- production principles;
- completion checklist.

## Production quality

The chapter emphasizes:

```text
boundary validation
explicit errors
useful and safe messages
predictable CLI behavior
meaningful exit codes
no silent failures
no indiscriminate exception swallowing
```

## Beginner accessibility

The chapter introduces the concepts from first principles, then progressively adds exception hierarchy, propagation, CLI design, process behavior, testing, and architecture considerations.

---

# 57. File-Scope Verification

The intended lesson artifact is only:

```text
10-Production-Habits-for-Python-Programs/03-validation-errors-and-exit-codes.md
```

Within the working sandbox, the output is provided as the single requested Markdown artifact:

```text
03-validation-errors-and-exit-codes.md
```

The content contains:

- explanations;
- examples;
- exercises;
- solutions;
- mini-project;
- interview questions;
- architecture questions;
- debugging scenarios;
- knowledge checks;
- completion checklist;
- self-review and scope verification.

No separate exercise file, answer-key file, Python file, configuration file, or companion Markdown artifact is required for this lesson.

---

# 58. Production Review: Validation Boundary Checklist

Before calling a validation boundary complete, ask:

```text
Where does the input enter?
What representation does it have at entry?
What assumptions will downstream code make?
Which assumptions are structural?
Which are domain rules?
Which failures are expected?
Which failures are operational?
Which failures are unexpected defects?
What exception type represents each expected failure?
Where should the exception be handled?
What should the user see?
What should be logged?
What should the process exit code be?
How will the behavior be tested?
```

A good boundary answer should be specific enough that another engineer could implement and test it without guessing.

---

# 59. Production Review: Exception Ownership

A useful question is:

> Which layer owns the decision about this failure?

For example:

```text
Low-level parser
→ knows conversion failed

Domain layer
→ knows the configuration contract failed

CLI boundary
→ knows how to communicate to user + process caller
```

This can lead to a clean flow:

```text
ValueError
   ↓
ConfigurationError
   ↓
CLI error message
   ↓
exit code 4
```

Notice that not every layer must catch the exception. A layer can **translate** the exception and let it continue upward.

Avoid this pattern:

```text
catch
→ log
→ ignore
→ return None
→ caller guesses
```

Prefer:

```text
raise accurate failure
→ propagate
→ handle at responsible boundary
```

---

# 60. Production Review: Failure-Path Matrix

A simple matrix helps make behavior explicit.

| Failure | Exception | User/Operator output | Log | Exit code |
|---|---|---|---|---:|
| Missing CLI input | parser/usage handling | parser diagnostic | optional | non-zero |
| Invalid CLI value | validation exception | concise stderr | optional | non-zero |
| Missing required file | `FileNotFoundError` or domain error | file diagnostic | useful | non-zero |
| Malformed row | `InputDataError` | row-specific stderr | useful | non-zero |
| Invalid configuration | `ConfigurationError` | configuration diagnostic | useful | non-zero |
| Unexpected bug | `Exception` at top boundary | safe generic message | traceback | non-zero |
| Successful run | none | primary result | lifecycle log if configured | 0 |

The exact numbers are application-specific. The important thing is that the behavior is deliberate rather than accidental.

---

# 61. Production Review: Final Learning Test

Before moving on, explain the following aloud without looking at the chapter.

## Scenario A

A user runs:

```bash
python app.py --workers abc
```

Explain:

```text
where parsing occurs
what validation layer is involved
what failure type is expected
where it should be handled
which stream receives the error
why the process should fail
```

## Scenario B

A CSV has:

```text
id,amount
A100,-10
```

Explain why this is not the same problem as a missing CSV file.

## Scenario C

An internal function raises an unexpected `AttributeError`.

Explain why it should not automatically be labeled "invalid input".

## Scenario D

The program logs:

```text
job failed
```

but exits with `0`.

Explain why this is unsafe for automation.

## Scenario E

A model returns:

```json
{"path": "important.txt"}
```

Explain why downstream code should still validate the structure and apply domain/security rules before opening the file.

If you can explain these five scenarios clearly, you have moved beyond syntax and into production reasoning.

---

# 62. Final File-Scope Verification

The only intended lesson change is:

```text
10-Production-Habits-for-Python-Programs/03-validation-errors-and-exit-codes.md
```

No related lesson should be changed as part of this chapter.

The chapter does not require modifications to:

```text
README.md
practice-questions.md
01-configuration-and-env-files.md
02-safe-and-useful-logging.md
04-idempotency-and-repeatable-jobs.md
```

It also does not require separate Python files, answer-key files, exercise files, configuration files, or new folders.

Final mental model:

```text
External Input
      ↓
     Parse
      ↓
   Validate
      ↓
Trusted Internal Data
      ↓
 Business Logic
      ↓
    Result
```

And when something goes wrong:

```text
Expected input failure
→ clear handling
→ safe diagnostics
→ non-zero exit
```

```text
Unexpected failure
→ preserve diagnostic evidence
→ controlled top-level handling
→ non-zero exit
```

Remember the five-way distinction:

```text
Validation
= Is this input acceptable?

Exception
= Something prevented normal execution.

Error handling
= What should the program do about the failure?

Logging
= What evidence should be recorded?

Exit code
= What process result should the caller receive?
```

That distinction is the foundation for predictable, production-oriented Python programs.
