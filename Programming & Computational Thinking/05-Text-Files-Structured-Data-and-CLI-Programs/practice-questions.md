# Practice Questions

## How to Use This Practice Set

This is a cumulative practice set for Module 1.5 — Text Files,
Structured Data, and CLI Programs, covering all nine chapters in this
folder: text files, pathlib, CSV, JSON, encodings/newlines, argparse,
standard streams/exit codes, logging, and environment configuration/
input validation.

- **Solve the problem first.** Read the problem and requirements, then
  write your own solution before looking at the one provided — even a
  rough attempt is more valuable than reading the answer cold.
- **Inspect the solution afterward**, and compare it to what you wrote
  — differences are often more instructive than matches.
- **Understand the reasoning**, not just the code. Every solution
  includes an explanation of *why* it works and *why* it's designed
  that way — that reasoning is the actual point of the exercise.
- **Modify the examples and run them locally.** Change a value, break
  something on purpose, add a case the original didn't cover. Every
  code sample here is runnable Python (standard library only) — copy
  it into a file and experiment.

Questions progress from **Basic** (1–9) through **Moderate** (10–18)
and **Hard** (19–27) to **Advanced** (28–36). Difficulty increases
through the number of concepts combined, the reasoning and debugging
required, and how production-oriented the scenario is — not through
sheer code length.

---

# BASIC — 9 Questions

## Question 1

### Problem

You're writing a small script that reads a configuration note left by
a teammate in `notes.txt` and prints its contents. The file might not
exist yet (a new teammate hasn't created it). Write a function
`read_notes(path)` that reads the file's full text using a context
manager and explicit UTF-8 encoding, and returns a friendly message
instead of crashing if the file is missing.

### Requirements

- Use `open()` as a context manager (`with`), not a manual
  `open()`/`close()` pair.
- Specify `encoding="utf-8"` explicitly.
- Handle the case where the file does not exist without letting an
  unhandled traceback reach the caller.
- Return the file's contents as a string on success.

### Solution

```python
def read_notes(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError:
        return f"No notes found at {path}."
```

### Explanation

The `with` statement is a context manager: it guarantees the file is
closed automatically, even if an exception occurs while reading —
without it, a raised exception between `open()` and a manual
`.close()` would leak the open file handle. `encoding="utf-8"` is set
explicitly rather than left to the platform default, since the correct
encoding for a text file is a property of the file's contents, not a
guess based on what OS happens to run the script. The `try`/`except`
catches specifically `FileNotFoundError` — the one, anticipated failure
mode this function is designed to handle — rather than a broad
`except Exception`, which would also hide genuinely unexpected bugs.

### Concepts Tested

Context managers, `open()`, explicit encoding, `FileNotFoundError`
handling (from 01-reading-and-writing-text-files.md).

---

## Question 2

### Problem

You need to build a path to a file named `report.csv` inside a
`data` subdirectory of the current working directory, in a way that
works identically on Linux, WSL2, and Windows. Then check whether that
file exists and is a regular file (not a directory) before trying to
open it, and print its extension.

### Requirements

- Do not hard-code a `/` or `\` path separator anywhere.
- Use `pathlib.Path`.
- Print `True`/`False` for existence and file-type checks separately.
- Print the file's suffix.

### Solution

```python
from pathlib import Path

report_path = Path("data") / "report.csv"

print("Exists:", report_path.exists())
print("Is a file:", report_path.is_file())
print("Suffix:", report_path.suffix)
```

### Explanation

`Path("data") / "report.csv"` uses the `/` operator, which `pathlib`
overloads to join path components using whatever separator is correct
for the current operating system — this is what makes the code
portable without any manual separator handling. `.exists()` checks
whether *anything* is at that path at all; `.is_file()` checks
additionally that it's a regular file rather than, say, a directory
that happens to be named `report.csv` — the two checks answer
genuinely different questions, which is why both are shown separately
rather than assuming one implies the other. `.suffix` returns
`".csv"`, including the leading dot.

### Expected Result

If `data/report.csv` does not exist in the current directory:
```
Exists: False
Is a file: False
Suffix: .csv
```

### Concepts Tested

`Path` construction with `/`, `.exists()`, `.is_file()`, `.suffix`,
cross-platform portability (from 02-pathlib-and-portable-paths.md).

---

## Question 3

### Problem

You have a CSV file `employees.csv` with a header row (`name,department,salary`)
and several data rows. Write a function that reads the file and returns
a list of dictionaries, one per employee, using the column names as
keys.

### Requirements

- Use the `csv` module — do not use `str.split(",")`.
- Use `csv.DictReader`.
- Open the file with `newline=""` and explicit UTF-8 encoding, as
  required for correct CSV parsing.
- Return a `list[dict]`.

### Solution

```python
import csv
from pathlib import Path


def load_employees(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)
```

### Explanation

`csv.DictReader` automatically reads the first row as field names and
returns each subsequent row as an `OrderedDict`-like mapping from those
names to that row's values — this is why the CSV module is used
instead of manually splitting each line on commas: a naive `split(",")`
breaks the moment any field legitimately contains a comma inside
quotes, or a value spans multiple lines, both of which the `csv`
module handles correctly and `split(",")` does not. `newline=""` is
required specifically for CSV files opened in text mode, so that the
`csv` module — not Python's own universal-newline translation — is the
one component responsible for interpreting embedded newlines inside
quoted fields correctly.

### Concepts Tested

`csv.DictReader`, headers/rows, `newline=""`, why not `split(",")`
(from 03-csv-files.md).

---

## Question 4

### Problem

You receive a JSON string representing a single user record:
`'{"name": "Alice", "age": 30, "active": true}'`. Parse it into a
Python object and safely print the user's `email` field if present, or
`"no email on file"` if the field is missing — without raising a
`KeyError`.

### Requirements

- Use `json.loads()`, not `json.load()` (this is a string, not a file).
- Do not let a missing `"email"` key crash the program.

### Solution

```python
import json

raw = '{"name": "Alice", "age": 30, "active": true}'
record = json.loads(raw)

email = record.get("email", "no email on file")
print(email)
```

### Explanation

`json.loads()` (with an "s", for "string") parses JSON text already
held in memory as a Python `str`; `json.load()` (no "s") instead reads
directly from an open file object — the right choice depends on
whether you already have the text or a file to read it from. JSON's
`true`/`false`/`null` become Python's `True`/`False`/`None` and a JSON
object becomes a Python `dict` automatically. `dict.get("email",
default)` returns the default value instead of raising `KeyError` when
the key is absent — the correct way to access a field that might
legitimately be missing from a JSON record, rather than assuming every
document has every field.

### Expected Result

```
no email on file
```

### Concepts Tested

`json.loads()`, JSON-to-Python type mapping, safe dictionary access
with `.get()` (from 04-json-and-serialization.md).

---

## Question 5

### Problem

A file `report.txt` was created on a different machine and contains
non-ASCII characters (accented letters, currency symbols). Write code
that opens and reads it correctly, and explain, in a code comment,
what would go wrong if the encoding were omitted or wrong.

### Requirements

- Open the file for reading with an explicit encoding.
- Add a comment explaining the risk of *not* specifying one.

### Solution

```python
# If we don't specify encoding= explicitly, Python falls back to a
# platform/locale-dependent default, which may not match the encoding
# the file was actually written in. That mismatch can either raise a
# UnicodeDecodeError, or — more dangerously — silently succeed while
# producing subtly wrong (mojibake) characters, with no error raised
# at all.
with open("report.txt", "r", encoding="utf-8") as handle:
    text = handle.read()

print(text)
```

### Explanation

Encoding is the rule that maps bytes on disk to characters in memory;
if the reader assumes a different rule than the writer used, either an
explicit decode error occurs (if the byte sequence isn't valid under
the assumed encoding) or, worse, decoding "succeeds" while producing
the wrong characters entirely, since many encodings can technically
decode arbitrary byte sequences into *some* text — just not the
correct text. UTF-8 is the standard, correct default for new text files
in this course; specifying it explicitly (rather than relying on
whatever the operating system happens to default to) makes the
program's behavior the same regardless of which machine runs it.

### Concepts Tested

Encoding as an explicit `open()` parameter, mojibake/UnicodeDecodeError
risk, portability (from 05-encodings-and-newlines.md).

---

## Question 6

### Problem

Build a CLI tool, `greet.py`, that takes one required positional
argument, a person's name, and prints a greeting. Running
`python greet.py` with no arguments should show a clear usage error,
not a Python traceback.

### Requirements

- Use `argparse.ArgumentParser`.
- The name must be a required positional argument.
- Use `parser.parse_args()`.

### Solution

```python
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Greet someone by name.")
    parser.add_argument("name", help="The name of the person to greet")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    print(f"Hello, {args.name}!")


if __name__ == "__main__":
    main()
```

### Explanation

`add_argument("name")` — no leading dashes — declares a **positional**
argument, which argparse treats as required by default; omitting it
causes `parse_args()` to print a usage message to stderr and exit with
status `2`, entirely on its own, with no manual error-handling code
needed. This is exactly why argparse is preferred over manually
inspecting `sys.argv`: the missing-argument case, the usage message,
and the exit status are all handled consistently and automatically.

### Expected Result

```bash
$ python greet.py Alice
Hello, Alice!

$ python greet.py
usage: greet.py [-h] name
greet.py: error: the following arguments are required: name
```

### Concepts Tested

`ArgumentParser`, positional arguments, automatic usage/error handling
(from 06-command-line-arguments-with-argparse.md).

---

## Question 7

### Problem

Write a tiny program that prints its actual result (`"42"`) to one
stream and a status message (`"Calculating..."`) to a *different*
stream, so that redirecting the result to a file with
`python calc.py > result.txt` captures only the result — not the
status message.

### Requirements

- Use `print()` with an explicit `file=` argument for the status
  message.
- Explain, in a comment, which stream each line goes to by default.

### Solution

```python
import sys

print("Calculating...", file=sys.stderr)  # diagnostic — goes to stderr
print("42")                                # the actual result — goes to stdout (the default)
```

### Explanation

`print()` writes to `sys.stdout` by default; passing `file=sys.stderr`
sends that specific call to the standard error stream instead. Because
shell redirection (`>`) only redirects stdout, running
`python calc.py > result.txt` writes only `"42"` into `result.txt`,
while `"Calculating..."` still appears on the terminal screen. This
separation — actual output on stdout, diagnostics on stderr — is what
allows a program's real result to be captured or piped cleanly, without
status messages contaminating it.

### Expected Result

```bash
$ python calc.py > result.txt
Calculating...
$ cat result.txt
42
```

### Concepts Tested

stdout vs. stderr, `print(..., file=...)`, shell redirection (from
07-standard-streams-and-exit-codes.md).

---

## Question 8

### Problem

Replace this script's `print()`-based diagnostics with proper logging,
using `INFO` level for routine progress and `WARNING` for a specific
condition (a value that's unusually large).

```python
def process(value):
    print("Processing value:", value)
    if value > 1000:
        print("Value seems unusually large:", value)
    return value * 2
```

### Requirements

- Use the standard `logging` module.
- Use a named logger, not the root logger directly.
- Use `INFO` for the routine message and `WARNING` for the large-value
  case.

### Solution

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process(value: int) -> int:
    logger.info("Processing value: %s", value)
    if value > 1000:
        logger.warning("Value seems unusually large: %s", value)
    return value * 2
```

### Explanation

`logging.getLogger(__name__)` gives this module its own logger,
positioned correctly in Python's logger hierarchy — the standard
pattern, rather than calling `logging.info(...)` directly (which
implicitly uses the root logger). `logger.info(...)` and
`logger.warning(...)` are used instead of `print()` because they carry
real severity levels: with `basicConfig(level=logging.WARNING)`
instead, the routine `INFO` message could be silenced entirely without
touching this function's code — something a `print()`-only version has
no built-in way to do. The `%s`-style placeholder (rather than an
f-string) means the message is only actually formatted if this log
call's level is enabled.

### Concepts Tested

`logging.getLogger(__name__)`, `INFO`/`WARNING` levels, lazy `%`
formatting, replacing `print()` with logging (from
08-logging-versus-print.md).

---

## Question 9

### Problem

Your program needs to read a `MAX_RETRIES` setting from the
environment, defaulting to `3` if it's not set, and use it as an
integer.

### Requirements

- Use `os.getenv()`, not `os.environ[...]`.
- Convert the value to `int` explicitly.
- Do not assume the environment variable is already an integer.

### Solution

```python
import os

max_retries = int(os.getenv("MAX_RETRIES", "3"))
print(max_retries, type(max_retries))
```

### Explanation

`os.getenv("MAX_RETRIES", "3")` returns `"3"` (a string default) if the
variable isn't set at all, or whatever string was actually assigned to
`MAX_RETRIES` in the environment if it is set — every environment
variable value, in either case, arrives as a `str`. Wrapping the whole
expression in `int(...)` converts it explicitly, and using a *string*
default (`"3"`, not the integer `3`) keeps the type consistent between
the "set" and "not set" cases, so `int(...)` always receives a string
to convert either way.

### Expected Result

```
3 <class 'int'>
```

### Concepts Tested

`os.getenv()` with a default, environment variables as strings,
explicit type conversion (from
09-environment-configuration-and-input-validation.md).

---

# MODERATE — 9 Questions

## Question 10

### Problem

Build a CLI tool, `row_count.py`, that takes one required argument —
a path to a CSV file — and prints how many data rows (excluding the
header) it contains. If the file doesn't exist, print a clear error to
stderr and exit with status `2` instead of crashing.

### Requirements

- Use `argparse` with `type=Path` for the argument.
- Validate the file exists before opening it.
- Use `csv.reader` (or `DictReader`) to count rows.
- Use `sys.exit()` (or `raise SystemExit`) with a non-zero code on
  failure.

### Solution

```python
import argparse
import csv
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Count data rows in a CSV file.")
    parser.add_argument("csv_file", type=Path, help="Path to the CSV file")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if not args.csv_file.is_file():
        print(f"error: file not found: {args.csv_file}", file=sys.stderr)
        return 2

    with args.csv_file.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader, None)          # skip the header row
        row_count = sum(1 for _ in reader)

    print(row_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Explanation

`type=Path` converts the raw CLI string directly into a `pathlib.Path`
object, ready for the `.is_file()` check — this combines argparse's
type conversion (06) with pathlib's filesystem inspection (02).
`next(reader, None)` consumes and discards the header row so it isn't
counted as data; `sum(1 for _ in reader)` then counts the remaining
rows without holding the whole file in memory. `main()` returns an
`int` status, and `raise SystemExit(main())` is the boundary that
turns that return value into the process's actual exit status —
keeping `main()` itself trivially callable and testable, per the
pattern from 07.

### Concepts Tested

argparse `type=Path`, path validation, `csv.reader`, `main() -> int`
+ `SystemExit`, meaningful exit codes.

---

## Question 11

### Problem

You receive JSON like `{"items": [{"id": 1, "price": 10.5}, {"id": 2}]}`
— note that the second item is missing `"price"`. Write a function
that computes the total price across all items, treating a missing
`"price"` as a validation problem rather than crashing or silently
treating it as `0`.

### Requirements

- Parse the JSON with `json.loads()`.
- Collect (don't fail on the first one) a list of error messages for
  items missing `"price"`.
- Return both the total (of valid items) and the list of errors.

### Solution

```python
import json


def compute_total(raw_json: str) -> tuple[float, list[str]]:
    data = json.loads(raw_json)
    total = 0.0
    errors = []

    for item in data.get("items", []):
        if "price" not in item:
            errors.append(f"item {item.get('id', '?')}: missing 'price'")
            continue
        total += item["price"]

    return total, errors


raw = '{"items": [{"id": 1, "price": 10.5}, {"id": 2}]}'
total, errors = compute_total(raw)
print(total, errors)
```

### Explanation

This is an **error-collection** strategy, not fail-fast: rather than
raising on the very first item missing `"price"`, every item is
checked, valid ones contribute to `total`, and invalid ones produce a
descriptive error message appended to a list — appropriate here
because the items are independent records, and a user benefits from
seeing every problem at once rather than fixing one missing field at a
time. `data.get("items", [])` safely handles a document that might not
even have an `"items"` key at all.

### Expected Result

```
10.5 ["item 2: missing 'price'"]
```

### Concepts Tested

`json.loads()`, safe nested access, error-collection validation
strategy (JSON from 04, error collection also introduced conceptually
in 09).

---

## Question 12

### Problem

A teammate's script reads a text file that was created on Windows and
contains `\r\n` line endings. When they process it line by line and
compare each line against `"END"`, the comparison never matches, even
though the file visibly contains a line that says `END`. Explain why,
and fix the code.

```python
with open("commands.txt", "r", encoding="utf-8") as handle:
    for line in handle:
        if line == "END":
            print("Found the end marker")
```

### Requirements

- Explain the root cause referencing newline handling.
- Provide a corrected version.

### Solution

```python
with open("commands.txt", "r", encoding="utf-8") as handle:
    for line in handle:
        if line.strip() == "END":
            print("Found the end marker")
```

### Explanation

**Root cause:** iterating over a text-mode file yields each line
*including* its trailing newline character. Python's text mode applies
universal-newline translation, meaning both `\n` and `\r\n` in the
underlying file are translated to a single `\n` when read — so the
line isn't `"END\r\n"` literally, but it *is* `"END\n"`, which still
does not equal the bare string `"END"`. The original comparison fails
regardless of which platform wrote the file, for exactly this reason.
**Fix:** `.strip()` removes leading/trailing whitespace, including the
trailing newline, before the comparison — a small but essential habit
whenever comparing a line's content rather than its exact bytes.

### Concepts Tested

Universal newline handling, line iteration, `.strip()`, a realistic
cross-platform newline bug (from 01 and 05).

---

## Question 13

### Problem

Extend `greet.py` from Question 6 so that it accepts an optional
`--shout` flag. When present, the greeting should be printed in
uppercase. The program should exit with status `0` on success and
status `2` if no name is supplied (relying on argparse's own behavior).

### Requirements

- Add `--shout` as a boolean flag using `action="store_true"`.
- Keep `name` as a required positional argument.
- Return an explicit exit status from `main()`.

### Solution

```python
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Greet someone by name.")
    parser.add_argument("name", help="The name of the person to greet")
    parser.add_argument("--shout", action="store_true", help="Print the greeting in uppercase")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    message = f"Hello, {args.name}!"
    print(message.upper() if args.shout else message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Explanation

`action="store_true"` makes `--shout` a boolean flag: its mere
presence sets `args.shout` to `True`, and its absence defaults it to
`False`, with no value needing to follow it on the command line. If
`name` is omitted, argparse's own `parse_args()` prints a usage error
and calls `sys.exit(2)` before `main()`'s own body ever runs — this is
why status `2` requires no explicit code here: it's argparse's
established convention for a CLI usage error, and this program simply
inherits it.

### Expected Result

```bash
$ python greet.py alice --shout
HELLO, ALICE!
$ echo $?
0
```

### Concepts Tested

`action="store_true"` flags, argparse's built-in exit-code convention,
`main() -> int` (from 06 and 07).

---

## Question 14

### Problem

Write a function `get_environment_name()` that reads an `APP_ENV`
environment variable, normalizes it to lowercase, and validates it's
one of `"development"`, `"staging"`, or `"production"` — raising a
clear `ValueError` otherwise. Default to `"development"` if the
variable isn't set at all.

### Requirements

- Use `os.getenv()` with a default.
- Normalize (don't just validate) the case.
- Raise `ValueError` with a message naming the invalid value and the
  valid options.

### Solution

```python
import os

VALID_ENVIRONMENTS = {"development", "staging", "production"}


def get_environment_name() -> str:
    raw = os.getenv("APP_ENV", "development")
    normalized = raw.strip().lower()
    if normalized not in VALID_ENVIRONMENTS:
        raise ValueError(
            f"unknown APP_ENV {raw!r}; expected one of {sorted(VALID_ENVIRONMENTS)}"
        )
    return normalized
```

### Explanation

Reading `os.getenv("APP_ENV", "development")` supplies the default
*before* any processing happens, so a missing variable and an
explicitly-set `"development"` are handled identically from that point
on. `.strip().lower()` is **normalization** — converting equivalent
representations (`"Production"`, `" PRODUCTION "`, `"production"`)
into one consistent internal form — performed *before* the validation
check, so the check only has to compare against the canonical,
lowercase set. The error message names both the actual (un-normalized)
value received and the full set of valid options, making the mistake
immediately fixable.

### Concepts Tested

`os.getenv()` with defaults, normalization vs. validation, clear
`ValueError` messages (from 09).

---

## Question 15

### Problem

A CSV-processing script currently prints progress and errors directly
to the console with `print()`. Update it to log progress at `INFO` and
per-row errors at `WARNING`, writing everything to a log file
`process.log` in addition to the console, while keeping the actual row
count as the script's printed result.

### Requirements

- Configure logging with both a console handler and a `FileHandler`.
- Use `logger.info()` for the summary and `logger.warning()` for a
  per-row problem.
- Print only the final row count to stdout, via `print()`.

### Solution

```python
import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logger.setLevel(logging.INFO)
    console = logging.StreamHandler()
    file_handler = logging.FileHandler("process.log", encoding="utf-8")
    for handler in (console, file_handler):
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
        logger.addHandler(handler)


def process(path: Path) -> int:
    valid = 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            if not row.get("id"):
                logger.warning("Line %d: missing 'id', skipping", line_number)
                continue
            valid += 1

    logger.info("Finished processing %s: %d valid rows", path, valid)
    return valid


if __name__ == "__main__":
    configure_logging()
    count = process(Path("data.csv"))
    print(count)
```

### Explanation

Two handlers are attached to the same logger — a `StreamHandler`
(console, defaulting to stderr) and a `FileHandler` (`process.log`) —
so every `logger` call is delivered to both destinations at once,
without the calling code needing to know either destination exists.
The actual program *result* (the row count) is still delivered via
`print()` to stdout, kept completely separate from the logging output
— exactly the stdout-for-results, logging-for-diagnostics separation
this module has built up since 07 and 08.

### Concepts Tested

Multiple handlers, `FileHandler`, `logger.info()`/`warning()`, stdout
vs. logging output separation (from 08, combined with CSV from 03).

---

## Question 16

### Problem

Write a function that reads a CSV file of products (`name,price`) and
writes an equivalent JSON file — a JSON array of objects, each with
`"name"` (string) and `"price"` (float, not string).

### Requirements

- Read with `csv.DictReader`.
- Convert `"price"` from `str` to `float` explicitly.
- Write with `json.dump()`, not `json.dumps()`, directly to a file.
- Use `indent=2` for readability.

### Solution

```python
import csv
import json
from pathlib import Path


def csv_to_json(csv_path: Path, json_path: Path) -> None:
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        products = [{"name": row["name"], "price": float(row["price"])} for row in reader]

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(products, handle, indent=2)
```

### Explanation

Every value `csv.DictReader` produces is a string, regardless of what
it "looks like" — `row["price"]` is `"9.99"`, not `9.99`, so it must be
converted with `float(...)` explicitly before it's placed into the
`products` list; skipping this would produce a JSON file with prices
stored as strings (`"9.99"` instead of `9.99`), silently changing the
data's type. `json.dump()` (no "s") writes directly to the already-open
file handle, which is why the file is opened with `"w"` first, in
contrast to `json.dumps()`, which would build a string in memory that
would then need a separate `.write()` call.

### Concepts Tested

`csv.DictReader`, explicit type conversion, `json.dump()`, CSV-to-JSON
transformation (from 03 and 04).

---

## Question 17

### Problem

Write a function `safe_write(path, content)` that writes text content
to a file inside a `reports/` directory, creating that directory if it
doesn't already exist, and refusing to overwrite an existing file
unless an `overwrite=True` flag is passed.

### Requirements

- Use `pathlib.Path.mkdir(parents=True, exist_ok=True)`.
- Raise `FileExistsError` (with a clear message) if the file exists and
  `overwrite` is `False`.
- Use `encoding="utf-8"` when writing.

### Solution

```python
from pathlib import Path


def safe_write(path: Path, content: str, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing file: {path} (pass overwrite=True)")

    with path.open("w", encoding="utf-8") as handle:
        handle.write(content)
```

### Explanation

`path.parent.mkdir(parents=True, exist_ok=True)` ensures the target
directory (and any missing parent directories) exists before an
attempt to write into it — `exist_ok=True` means this doesn't raise if
the directory is already there, which is the common, desired case.
Checking `path.exists()` *before* opening for writing is what prevents
an accidental silent overwrite — opening in `"w"` mode truncates an
existing file immediately, with no warning, so the check has to happen
first, as a deliberate gate, rather than relying on the write itself to
somehow protect the existing content.

### Concepts Tested

`Path.mkdir(parents=True, exist_ok=True)`, avoiding accidental
overwrite, explicit encoding on write (from 02 and 01).

---

## Question 18

### Problem

Write a simple filter program, `to_upper.py`, that reads text
line-by-line from stdin and writes each line, upper-cased, to stdout —
so it can be used in a pipeline like
`cat notes.txt | python to_upper.py`. It should not load the whole
input into memory at once.

### Requirements

- Iterate over `sys.stdin` directly (do not use `.read()` or
  `.readlines()`).
- Preserve each line's own newline when writing.
- Exit with status `0` when finished.

### Solution

```python
import sys


def main() -> int:
    for line in sys.stdin:
        sys.stdout.write(line.upper())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Explanation

`for line in sys.stdin:` reads and yields one line at a time,
including its trailing newline, until EOF — the memory-efficient,
streaming approach, in contrast to `sys.stdin.read()`, which would
block until EOF and hold the entire input in memory as one string
first. `.upper()` is applied to the whole line including its newline
(upper-casing a newline character has no effect on it), so
`sys.stdout.write(...)` doesn't need to re-add anything. Because this
program reads only from stdin and writes only to stdout, it composes
directly into a shell pipeline without any special accommodation.

### Expected Result

```bash
$ printf "hello\nworld\n" | python to_upper.py
HELLO
WORLD
```

### Concepts Tested

Streaming stdin iteration, pipeline composability, `sys.stdout.write()`
(from 07).

---

# HARD — 9 Questions

## Question 19

### Problem

The following CSV-loading function occasionally raises
`UnicodeDecodeError` on files from certain teammates, but works fine on
others. Diagnose the likely cause and fix it defensively.

```python
def load_csv(path):
    with open(path, "r") as handle:
        return list(csv.reader(handle))
```

### Requirements

- Identify the root cause(s), referencing both encoding and CSV-specific
  newline handling.
- Provide a corrected version.
- Explain what would still go wrong for a file in a genuinely different
  encoding, and how you'd detect that case rather than silently
  producing wrong data.

### Solution

```python
import csv
from pathlib import Path


def load_csv(path: Path) -> list[list[str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle))
```

### Explanation

**Root cause 1 (encoding):** `open(path, "r")` with no `encoding=`
falls back to a platform/locale-dependent default encoding — on some
machines this might not be UTF-8, so a file written in UTF-8 (e.g.,
containing accented characters) can fail to decode, or decode
incorrectly, depending on which machine runs the script. **Root cause
2 (newline):** the CSV module's own documentation specifically requires
opening the file with `newline=""` in text mode, so that the `csv`
module — not Python's own universal-newline translation — handles
newlines correctly, particularly for any field that legitimately
contains an embedded newline inside quotes. **Remaining risk:** if a
file is genuinely encoded in something other than UTF-8 (e.g.
Windows-1252), even this fixed version will raise `UnicodeDecodeError`
rather than silently succeeding — which is actually the *safer* failure
mode, since an explicit error is far easier to notice and diagnose than
mojibake produced by guessing the wrong encoding and having it decode
"successfully" anyway.

### Concepts Tested

Explicit encoding, `newline=""` for CSV, distinguishing "wrong
encoding raises an error" from "wrong encoding silently corrupts data"
(from 03 and 05).

---

## Question 20

### Problem

A teammate wrote this argparse setup for a `--verbose` flag meant to
default to off and be turned on with `--verbose true` or
`--verbose false`:

```python
parser.add_argument("--verbose", type=bool, default=False)
```

Running `python app.py --verbose false` still enables verbose mode.
Explain exactly why, and fix it two different ways.

### Requirements

- Explain the root cause precisely (don't just say "it's buggy").
- Provide one fix using `action="store_true"`.
- Provide a second fix that still accepts explicit `true`/`false` text.

### Solution

```python
# Fix 1 — a plain boolean flag: presence means True, absence means False
parser.add_argument("--verbose", action="store_true")
# usage: --verbose         (no value follows)

# Fix 2 — a custom parser function, for genuine `--verbose true/false` syntax
import argparse

def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"expected a boolean value, got {value!r}")

parser.add_argument("--verbose", type=parse_bool, default=False)
```

### Explanation

**Root cause:** `type=bool` calls Python's built-in `bool("false")`,
and in Python, *any non-empty string is truthy* — `bool("false")` is
`True`, exactly like `bool("true")`, because `bool()` on a string only
checks whether the string is empty, not what it says. `type=` never
actually parses the *meaning* of "true"/"false" text at all in this
setup. **Fix 1** sidesteps the whole problem by making `--verbose` a
bare flag — no value follows it at all, so there's nothing to
misinterpret. **Fix 2** is appropriate when explicit `--verbose true`/
`--verbose false` syntax is genuinely required; it replaces `bool()`
with a real parser function that checks the string's actual content
and raises a clear `argparse.ArgumentTypeError` for anything it
doesn't recognize.

### Concepts Tested

The `type=bool` trap, `action="store_true"`, custom `type=` functions
with `ArgumentTypeError` (from 06, reinforced in 09).

---

## Question 21

### Problem

A script calls `logging.basicConfig(level=logging.DEBUG, ...)` at the
top of `main()`, but `DEBUG`-level messages never appear, even though
`INFO` and above work fine. The script also imports a small internal
helper module that happens to call `logging.warning(...)` once, at
import time, before `main()` runs. Diagnose why `basicConfig()`
appears to have no effect on the level, and fix it.

### Requirements

- Identify why `basicConfig()`'s settings were silently ignored.
- Provide a fix that doesn't require removing the helper module's
  logging call.

### Solution

```python
# helper.py
import logging
logging.warning("helper module loaded")   # this runs at import time


# app.py — BROKEN order
import helper                              # <-- implicitly configures the root logger first!
import logging

def main():
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    logging.debug("this never appears")


# app.py — FIXED
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")  # configure FIRST

import helper   # now this call is captured under the DEBUG-level config
import logging

def main():
    logging.debug("this now appears correctly")
```

### Explanation

**Root cause:** any call to a module-level logging convenience
function (`logging.warning(...)`, `logging.info(...)`, etc.) implicitly
triggers a *default* `basicConfig()` call internally, the very first
time logging is used at all — and `basicConfig()` **does nothing** if
the root logger already has a handler attached. Because `helper`'s
`logging.warning(...)` runs at import time — before `main()`'s own
explicit `basicConfig()` call — it silently consumes the one chance
`basicConfig()` had to configure anything. **Fix:** call
`basicConfig()` as the very first logging-related statement in the
program, before importing anything that might log at import time.

### Concepts Tested

`basicConfig()`'s "does nothing if already configured" behavior,
import-time side effects, configuration ordering (from 08).

---

## Question 22

### Problem

This function is meant to safely load a JSON config file, but it
raises an unhandled `json.JSONDecodeError` traceback whenever the file
contains a trailing comma (a common hand-editing mistake) or is
otherwise malformed. Fix it so it raises a clear, actionable
`ValueError` instead.

```python
def load_config(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)
```

### Requirements

- Catch `json.JSONDecodeError` specifically (not a bare `except:`).
- Re-raise as `ValueError` including the file path and the original
  error's message.
- Keep the "file not found" case (`FileNotFoundError`) unhandled here —
  explain, in a comment, why that's a reasonable choice for this
  function specifically.

### Solution

```python
import json
from pathlib import Path


def load_config(path: Path) -> dict:
    # FileNotFoundError is intentionally left to propagate — a missing
    # config file is a different, equally clear failure that the
    # caller (or argparse's own path validation) is better positioned
    # to report with full context about what was expected.
    with path.open(encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON in {path}: {exc}") from exc
```

### Explanation

`json.JSONDecodeError` is a subclass of `ValueError` raised specifically
when text that was expected to be valid JSON cannot be parsed — catching
it *specifically*, rather than a bare `except:`, means only this
anticipated failure mode is intercepted, while genuinely unexpected
bugs elsewhere in the function would still propagate normally. Re-
raising as a new `ValueError` with `from exc` converts a low-level
parsing detail into a clear, boundary-appropriate error that names
*which file* was the problem, while `from exc` preserves the original
exception as the visible "caused by" context for anyone debugging
later, rather than silently discarding it.

### Concepts Tested

`json.JSONDecodeError`, converting low-level errors into
boundary-appropriate ones, `raise ... from ...`, deciding what *not* to
catch (from 04 and 09).

---

## Question 23

### Problem

A file-upload CLI accepts a `--destination` argument and joins it with
a fixed base directory to decide where to save an uploaded file:

```python
base = Path("/var/app/uploads")
destination = base / user_supplied_subpath
destination.write_bytes(data)
```

Explain the security problem if `user_supplied_subpath` is something
like `"../../etc/cron.d/malicious"`, and fix the code to reject any
path that would escape the intended base directory.

### Requirements

- Explain the vulnerability class by name.
- Use `Path.resolve()` and `Path.is_relative_to()` in the fix.
- Raise a clear `ValueError` for a path that escapes the base
  directory.

### Solution

```python
from pathlib import Path


def resolve_upload_path(base: Path, user_supplied_subpath: str) -> Path:
    candidate = (base / user_supplied_subpath).resolve()
    if not candidate.is_relative_to(base.resolve()):
        raise ValueError(f"path escapes the allowed upload directory: {user_supplied_subpath!r}")
    return candidate
```

### Explanation

This is a **path traversal** vulnerability: joining a fixed base
directory with an *untrusted* relative path using `/` does not confine
the result to that base directory at all — `..` segments in the
supplied subpath can walk back out of it entirely, letting an attacker
write to (or read from) arbitrary locations the program was never
meant to touch, using nothing but ordinary path syntax. The fix
resolves the joined path to its absolute, `..`-free form with
`.resolve()`, then checks with `.is_relative_to()` (available from
Python 3.9) whether that resolved path is still actually inside the
resolved base directory — rejecting it with a clear error if not,
*before* any file operation is attempted.

### Concepts Tested

Path traversal, `Path.resolve()`, `Path.is_relative_to()`, treating
user-supplied paths as untrusted input (from 02 and 09).

---

## Question 24

### Problem

You're building a batch validator for a directory of 10,000 customer
records in JSON Lines format. A junior developer wrote it to raise and
stop on the very first invalid record. Explain why that's the wrong
strategy here, and redesign it to report every problem in one pass —
while still failing the whole run (non-zero exit code) if *any* record
was invalid.

### Requirements

- Explain, in your own words, when fail-fast is appropriate and when
  error collection is appropriate, applied to this scenario.
- Implement the error-collection version.
- Return a specific exit code convention distinguishing "all valid"
  from "some invalid."

### Solution

```python
import json
import sys
from pathlib import Path


def validate_records(path: Path) -> tuple[int, list[str]]:
    valid = 0
    errors = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"line {line_number}: invalid JSON")
                continue
            if "customer_id" not in record:
                errors.append(f"line {line_number}: missing 'customer_id'")
                continue
            valid += 1
    return valid, errors


def main() -> int:
    valid, errors = validate_records(Path("customers.jsonl"))
    for error in errors:
        print(error, file=sys.stderr)
    print(f"valid: {valid}, invalid: {len(errors)}")
    return 0 if not errors else 3


if __name__ == "__main__":
    raise SystemExit(main())
```

### Explanation

**Fail-fast** is appropriate for a small number of critical,
all-or-nothing settings — a missing database URL, for instance, where
continuing at all would be meaningless. **Error collection** is
appropriate here because the 10,000 records are *independent*: a
customer with a typo in record #4,982 has nothing to do with whether
record #1 is valid, so stopping at the first failure would force the
team to fix and re-run the whole batch one error at a time, when they
could instead see every problem in a single pass. The function still
distinguishes "0 errors" from "1+ errors" through its return value, and
`main()` translates that into exit code `0` versus `3` — so automation
downstream can still treat this as pass/fail, even though the
*validation itself* processed everything rather than stopping early.

### Concepts Tested

Fail-fast vs. error-collection strategy selection and justification,
JSON Lines processing, meaningful exit codes (from 07 and 09).

---

## Question 25

### Problem

A data-cleaning tool is meant to be used in a pipeline:
`cat raw.csv | python clean.py | python load.py`. Users report that
`load.py` sometimes crashes trying to parse a line that says
`"Loading rows..."`. Diagnose the bug in `clean.py` and fix it.

```python
import sys

def main():
    print("Loading rows...")
    for line in sys.stdin:
        sys.stdout.write(line.strip().upper() + "\n")

if __name__ == "__main__":
    main()
```

### Requirements

- Identify exactly which stream the problem is on.
- Fix it so the pipeline only ever receives actual data on stdout.

### Solution

```python
import sys


def main() -> int:
    print("Loading rows...", file=sys.stderr)   # diagnostic — now goes to stderr
    for line in sys.stdin:
        sys.stdout.write(line.strip().upper() + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Explanation

`print("Loading rows...")` with no `file=` writes to **stdout** by
default — which, in the pipeline `cat raw.csv | python clean.py |
python load.py`, is exactly the channel `load.py` reads as its own
stdin. `load.py` has no way to distinguish that status line from real
data — it simply receives it as one more line to parse, and fails
because `"Loading rows..."` isn't valid data. The fix routes that
message to stderr, which is *not* connected by a plain pipe to the next
stage — it remains visible on the terminal (or wherever stderr is
separately redirected) without ever reaching `load.py`'s input at all.

### Concepts Tested

stdout/stderr separation, pipeline safety, diagnosing corrupted
pipeline data (from 07).

---

## Question 26

### Problem

A deployment script reads a `RETRY_LIMIT` environment variable and a
`DRY_RUN` flag, but production keeps behaving as if `DRY_RUN` is
enabled even though ops insists they set `DRY_RUN=false`. Diagnose the
bug and fix the configuration-reading code.

```python
retry_limit = os.getenv("RETRY_LIMIT", 3)
dry_run = bool(os.getenv("DRY_RUN", "false"))
```

### Requirements

- Identify **two** separate bugs in this snippet (not just the
  boolean one).
- Provide corrected code for both.

### Solution

```python
import os


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"expected a boolean value, got {value!r}")


retry_limit = int(os.getenv("RETRY_LIMIT", "3"))
dry_run = parse_bool(os.getenv("DRY_RUN", "false"))
```

### Explanation

**Bug 1:** `os.getenv("RETRY_LIMIT", 3)` uses an *integer* default
(`3`), but if `RETRY_LIMIT` *is* set in the environment, `os.getenv()`
always returns a `str` — meaning `retry_limit`'s type is inconsistent
depending on whether the variable was set at all, and any later code
doing arithmetic on it would break the moment someone actually sets
the environment variable. **Bug 2 (the reported one):** `bool(some_string)`
is truthy for any non-empty string, including `"false"` — so
`DRY_RUN=false` is silently read as `True`, exactly the opposite of
what ops intended, and exactly why production behaves as if dry-run is
always on. The fix converts `RETRY_LIMIT` with `int(...)` (using a
*string* default, `"3"`, to keep types consistent) and reads `DRY_RUN`
through a real `parse_bool()` function that checks the string's actual
content.

### Concepts Tested

Consistent default types, the `bool(string)` trap applied to
environment variables specifically, `parse_bool()` (from 09).

---

## Question 27

### Problem

Two configuration-reading functions in the same codebase disagree
about `PORT`'s precedence: one checks the CLI argument first, the
other checks the environment variable first, with no test covering
either. As a result, running the same command sometimes uses port
`8080` and sometimes `9000`, depending on which function happened to
run first. Diagnose the underlying design flaw (not just "fix the
order") and propose the correct fix.

### Requirements

- Identify the root architectural problem, not just the immediate
  symptom.
- Describe (and briefly implement) the fix.
- Explain how you'd test it to prevent regression.

### Solution

```python
def resolve_port(cli_value: int | None) -> int:
    if cli_value is not None:
        return cli_value
    return int(os.getenv("PORT", "8000"))


# Every part of the codebase that needs the port calls resolve_port()
# exactly once, at startup, and passes the resulting AppConfig value
# down explicitly — no other function reads PORT or args.port directly.
```

```python
def test_precedence_cli_wins(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    assert resolve_port(cli_value=8080) == 8080

def test_precedence_env_when_no_cli(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    assert resolve_port(cli_value=None) == 9000

def test_precedence_default(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    assert resolve_port(cli_value=None) == 8000
```

### Explanation

**Root cause:** the codebase reads `PORT` (and CLI `--port`) in more
than one place, each with its own, independently-written, undocumented
idea of precedence — a direct instance of "configuration read from
multiple places" rather than a single, agreed-upon rule. The immediate
symptom (inconsistent port) is just evidence of that deeper structural
problem; fixing one function's order without addressing the other
would only hide the bug until the *other* function runs first in some
future code path. **Fix:** define precedence in exactly **one**
function (`resolve_port()`), call it exactly once at startup, and pass
the resulting value explicitly to everything else — eliminating the
possibility of two different answers entirely, rather than merely
making today's two functions agree by coincidence. The three
parameterized-style tests each pin down one precedence case explicitly,
so a future edit that reverses the order again would fail a test
immediately instead of silently reintroducing the bug.

### Concepts Tested

Configuration precedence as an explicit, centralized design (not an
implicit convention), regression testing with `monkeypatch` (from 09).

---

# ADVANCED — 9 Questions

## Question 28

### Problem

Build a complete CLI tool, `orders_report.py`, that reads an
`orders.csv` file (`order_id,customer,amount`), validates each row,
writes a JSON summary (`total_orders`, `total_amount`, `invalid_rows`)
to stdout, logs per-row problems via the `logging` module (not
`print()`), and exits with a status code that distinguishes "all rows
valid" from "some rows invalid" from "input file not found."

### Requirements

- Use `argparse` for the file path argument.
- Validate the file's existence with `pathlib` before opening it.
- Use `csv.DictReader` and validate `amount` converts to `float`.
- Collect (don't fail fast on) row-level errors.
- Log warnings for invalid rows; log an info-level summary.
- Print only the JSON summary to stdout.
- Exit `4` if the file is missing, `3` if any row is invalid, `0`
  otherwise.

### Solution

```python
"""orders_report.py — validate orders.csv and report a JSON summary."""
import argparse
import csv
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize and validate an orders CSV file.")
    parser.add_argument("orders_file", type=Path, help="Path to orders.csv")
    return parser


def process_orders(path: Path) -> dict:
    total_orders = 0
    total_amount = 0.0
    invalid_rows = 0

    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            if not row.get("order_id"):
                logger.warning("Line %d: missing 'order_id'", line_number)
                invalid_rows += 1
                continue
            try:
                amount = float(row["amount"])
            except (KeyError, ValueError):
                logger.warning("Line %d: invalid 'amount' for order %s", line_number, row.get("order_id"))
                invalid_rows += 1
                continue
            total_orders += 1
            total_amount += amount

    logger.info("Processed %s: %d valid, %d invalid", path, total_orders, invalid_rows)
    return {"total_orders": total_orders, "total_amount": round(total_amount, 2), "invalid_rows": invalid_rows}


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

    args = build_parser().parse_args(argv)

    if not args.orders_file.is_file():
        print(f"error: file not found: {args.orders_file}", file=sys.stderr)
        return 4

    summary = process_orders(args.orders_file)
    print(json.dumps(summary))

    return 0 if summary["invalid_rows"] == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
```

### Explanation

Every layer of this module comes together here: `argparse` (06) with
`type=Path` for the input; `pathlib` (02) for the existence check;
`csv.DictReader` (03) with `newline=""` and UTF-8 for correct parsing;
error-collection validation (per-row problems are logged and counted,
not fatal — 09); `logging` (08), not `print()`, for every diagnostic,
using `WARNING` for skippable row problems and `INFO` for the run
summary; and the stdout/stderr/exit-code discipline from 07 — the JSON
result goes to stdout exclusively, the missing-file error goes to
stderr with exit `4`, and the function distinguishes "ran successfully
but found bad data" (`3`) from complete success (`0`). This distinction
matters for automation: a pipeline stage downstream can react
differently to "the file wasn't there at all" versus "the file was
there but some rows were bad."

### Concepts Tested

Full-module integration: argparse, pathlib, CSV, JSON, logging,
exit codes, error collection.

---

## Question 29

### Problem

Design a configuration loader for a CLI tool that needs a `PORT`
(optional, default `8000`, overridable by `--port`), a `LOG_LEVEL`
(optional, default `INFO`), and a required `API_KEY` (from the
environment only — never a CLI flag, and never logged). Represent the
result as an immutable configuration object.

### Requirements

- Use `os.getenv()`/`os.environ` appropriately for each setting.
- CLI `--port`, if given, must override the `PORT` environment
  variable.
- `API_KEY` missing should fail fast with a clear message and exit
  code `4`.
- Use a frozen `dataclass` for the resulting configuration object.
- Never print or log `API_KEY`'s actual value anywhere.

### Solution

```python
import argparse
import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    port: int
    log_level: str
    api_key: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=None)
    return parser


def build_config(argv: list[str] | None = None) -> AppConfig:
    args = build_parser().parse_args(argv)

    port = args.port if args.port is not None else int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()

    api_key = os.environ.get("API_KEY")
    if not api_key:
        print("error: API_KEY environment variable is required", file=sys.stderr)
        raise SystemExit(4)

    return AppConfig(port=port, log_level=log_level, api_key=api_key)


def main(argv: list[str] | None = None) -> int:
    config = build_config(argv)
    # SAFE: only non-sensitive fields are ever printed or logged
    print(f"Starting on port {config.port} (log level: {config.log_level})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Explanation

`args.port if args.port is not None else ...` implements precedence
correctly: it checks explicitly for `None` rather than falsy-ness, so
a genuinely-intended `--port 0` (unlikely here, but a general
principle) wouldn't be incorrectly treated as "not given." `API_KEY` is
read only from the environment — never exposed as a CLI flag at all —
directly following the principle that secrets shouldn't be passed as
command-line arguments (visible to other users inspecting running
processes). Its absence triggers an immediate, fail-fast exit with a
specific code (`4`, this module's "configuration problem" convention),
rather than letting the program start in a broken state. `AppConfig`
is `frozen=True` so nothing downstream can accidentally mutate it, and
every `print`/log call in the rest of the program only ever references
specific, named, non-sensitive fields — never `config` as a whole,
which would risk exposing `api_key` if the dataclass's default `repr`
were ever logged.

### Concepts Tested

Configuration precedence, fail-fast required secrets, frozen
`dataclass` configuration objects, safe logging of configuration (09,
plus 06 and 07 for CLI/exit-code integration).

---

## Question 30

### Problem

Build a streaming JSON Lines validator, `validate_stream.py`, that
reads records from stdin (not a file), so it works both as
`python validate_stream.py < data.jsonl` and inside a pipeline like
`producer | python validate_stream.py | consumer`. Valid records should
pass through to stdout unchanged; invalid ones should be logged as
warnings and dropped. It must never load the whole input into memory.

### Requirements

- Iterate over `sys.stdin` line by line.
- Use `logging` for warnings, not `print()`.
- Print only valid, passed-through records to stdout.
- Exit `0` if every record was valid, `3` if any were dropped.

### Solution

```python
"""validate_stream.py — a streaming JSON Lines pass-through validator."""
import json
import logging
import sys

logger = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    total = 0
    dropped = 0

    for line_number, raw_line in enumerate(sys.stdin, start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        total += 1
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError:
            logger.warning("Line %d: invalid JSON, dropping", line_number)
            dropped += 1
            continue

        if "id" not in record:
            logger.warning("Line %d: missing 'id', dropping", line_number)
            dropped += 1
            continue

        print(stripped)   # pass the valid record through, unchanged, on stdout

    logger.info("Processed %d records, dropped %d", total, dropped) if False else None
    return 0 if dropped == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
```

### Explanation

`for line_number, raw_line in enumerate(sys.stdin, start=1):` streams
one line at a time — the program's memory usage stays proportional to
one record, regardless of whether the input is ten lines or ten
million, which is exactly why it works safely inside a long-running
pipeline. Every warning goes through `logger.warning(...)`, which
defaults to stderr — a plain pipe (`producer | python validate_stream.py
| consumer`) only connects stdout to the next stage, so these warnings
never contaminate the data `consumer` receives, even though a human
watching the terminal still sees them. Only genuinely valid records are
`print()`ed, preserving the "clean stdout" contract the next pipeline
stage depends on. The distinct exit code (`3` for "some records
dropped") lets an orchestrator distinguish a fully clean run from one
that silently lost data, purely from the process's exit status.

### Concepts Tested

Streaming stdin, JSON Lines processing, logging vs. print separation in
a pipeline context, meaningful exit codes (07, 08, and 04 combined).

---

## Question 31

### Problem

Design and implement a "data quality gate" CLI, `dq_gate.py`, used in a
CI pipeline before a CSV dataset is allowed to proceed to a downstream
ML training job. It must accept `--max-invalid-percent` (default `5.0`)
as a CLI option, validate every row of a CSV file
(`id,label,confidence`, where `confidence` must be a float between 0
and 1 inclusive), and fail the whole build (non-zero exit) if the
percentage of invalid rows exceeds the threshold — even if most rows
are fine.

### Requirements

- Validate `confidence` with an inclusive range check.
- Use error collection for individual rows, but a fail/pass threshold
  decision at the end.
- Use `argparse` `type=float` with a custom validator rejecting values
  outside `[0.0, 100.0]` for `--max-invalid-percent`.
- Print a JSON summary to stdout; log details to stderr.
- Exit `0` if under threshold, `3` if over.

### Solution

```python
"""dq_gate.py — a CI data-quality gate for a CSV dataset."""
import argparse
import csv
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def percent(value: str) -> float:
    number = float(value)
    if not (0.0 <= number <= 100.0):
        raise argparse.ArgumentTypeError(f"must be between 0 and 100, got {number}")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CI data-quality gate for a CSV dataset.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--max-invalid-percent", type=percent, default=5.0)
    return parser


def validate_row(row: dict, line_number: int) -> str | None:
    if not row.get("id"):
        return f"line {line_number}: missing 'id'"
    try:
        confidence = float(row["confidence"])
    except (KeyError, ValueError):
        return f"line {line_number}: invalid 'confidence'"
    if not (0.0 <= confidence <= 1.0):
        return f"line {line_number}: confidence {confidence} out of range [0, 1]"
    return None


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    args = build_parser().parse_args(argv)

    total = 0
    invalid = 0
    with args.dataset.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            total += 1
            error = validate_row(row, line_number)
            if error:
                logger.warning(error)
                invalid += 1

    invalid_percent = (invalid / total * 100) if total else 0.0
    passed = invalid_percent <= args.max_invalid_percent

    print(json.dumps({
        "total_rows": total,
        "invalid_rows": invalid,
        "invalid_percent": round(invalid_percent, 2),
        "threshold_percent": args.max_invalid_percent,
        "passed": passed,
    }))

    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
```

### Explanation

This design deliberately separates two different validation
*strategies* used together: **per-row** validation is error-collection
(every row is checked; a bad row doesn't stop the scan) because
individual rows are independent, but the **overall build decision** is
effectively fail-fast against a computed threshold — the whole gate
either passes or fails as one unit, since a CI pipeline needs a single
yes/no answer, not a partial one. `percent()` is a custom argparse
`type=` validator combining conversion and range-checking in one
reusable function, raising `ArgumentTypeError` for a syntactically
valid float that's still out of range — exactly the "type= handles
conversion *and* validation" pattern from 06 and 09. The JSON summary
on stdout gives a downstream CI step (or a human) the exact numbers
behind the pass/fail decision, while the row-level detail lives only in
the logged warnings, keeping the two audiences (machine-readable
summary vs. human-readable diagnostic detail) cleanly separated.

### Concepts Tested

Custom argparse validators, inclusive range validation, combining
per-item error collection with an aggregate fail-fast decision,
CI-oriented exit-code design (06, 09, 07, 03 combined).

---

## Question 32

### Problem

A security review flagged this logging call in a payment-processing
CLI:

```python
logger.debug("Processing payment: %s", vars(payment_config))
```

where `payment_config` is a dataclass containing `merchant_id`,
`api_secret`, and `currency`. Explain what's wrong, and redesign both
the logging call and the configuration object to prevent this class of
mistake from recurring, even if a future field is added carelessly.

### Requirements

- Explain the specific risk.
- Fix the immediate logging call.
- Propose a structural fix that protects against the *next* person
  making the same mistake.

### Solution

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentConfig:
    merchant_id: str
    api_secret: str
    currency: str

    def __repr__(self) -> str:
        return f"PaymentConfig(merchant_id={self.merchant_id!r}, api_secret='***', currency={self.currency!r})"


# Immediate fix: log only specific, known-safe fields — never the whole object
logger.debug("Processing payment: merchant_id=%s currency=%s", payment_config.merchant_id, payment_config.currency)
```

### Explanation

**The risk:** `vars(payment_config)` (or logging the object directly,
relying on its default `repr`) dumps *every* field, including
`api_secret` — a real secret ends up in plain text in the log output,
which is durable, frequently forwarded to other systems, and often
retained far longer than anyone expects. This is precisely the "never
log secrets" rule this module emphasizes repeatedly, violated by a
single careless logging call. **Immediate fix:** log only the specific
fields already known to be safe, by name — never the object as a
whole. **Structural fix:** overriding `__repr__` on `PaymentConfig`
itself to always mask `api_secret` means that *any* future code that
logs, prints, or otherwise reprs the whole object — including code a
teammate writes later without knowing this history — is protected by
default, rather than depending on every future call site remembering
to cherry-pick safe fields individually. This is a stronger guarantee
than "remember not to log the secret," because it doesn't rely on
memory or code review catching every future instance.

### Concepts Tested

Secrets in logs, safe logging design, defensive/structural protection
against a recurring mistake class (08 and 09's security sections
combined).

---

## Question 33

### Problem

A batch job processes a folder of `.txt` reports, some written on
Linux (UTF-8, `\n`) and some on Windows (likely UTF-8 or Windows-1252,
`\r\n`), and some containing a UTF-8 byte-order mark (BOM). Design a
robust reader function that handles all three cases without crashing,
logs a warning (not an error) when it has to fall back from UTF-8, and
never silently produces corrupted text without at least logging that
something unusual happened.

### Requirements

- Try UTF-8 (with BOM handling) first.
- Fall back to a specified secondary encoding if UTF-8 decoding fails,
  logging a `WARNING` when this happens.
- Use `pathlib.Path` for iteration and file checks.
- Return the decoded text, or raise a clear error if even the fallback
  fails.

### Solution

```python
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def read_report(path: Path, fallback_encoding: str = "cp1252") -> str:
    try:
        return path.read_text(encoding="utf-8-sig")   # handles a UTF-8 BOM if present, transparently
    except UnicodeDecodeError:
        logger.warning("%s is not valid UTF-8; retrying with %s", path, fallback_encoding)
        try:
            return path.read_text(encoding=fallback_encoding)
        except UnicodeDecodeError as exc:
            raise ValueError(f"could not decode {path} with utf-8 or {fallback_encoding}") from exc


def process_reports(directory: Path) -> list[str]:
    contents = []
    for path in sorted(directory.glob("*.txt")):
        contents.append(read_report(path))
    return contents
```

### Explanation

`encoding="utf-8-sig"` is used instead of plain `"utf-8"` specifically
because it transparently strips a leading byte-order mark if one is
present, while still decoding correctly for UTF-8 files that have no
BOM at all — a single choice that safely covers both common UTF-8
variants without needing to detect the BOM manually first. When UTF-8
decoding genuinely fails (the file is in some other encoding
entirely), the function does not silently guess and possibly produce
mojibake — it explicitly retries with a named fallback encoding
(`cp1252`, a common legacy Windows encoding), and — critically — logs a
`WARNING` when this happens, so the fact that a fallback was needed at
all is visible to whoever operates this batch job, rather than
disappearing invisibly into "it worked." If even the fallback fails,
the function raises a clear `ValueError` naming the file and both
encodings attempted, rather than letting a raw `UnicodeDecodeError`
propagate with no context about what was already tried.

### Concepts Tested

BOM handling with `utf-8-sig`, encoding fallback strategy, logging a
`WARNING` for a recovered-but-notable condition, `pathlib.Path.glob()`
(05, 08, and 02 combined).

---

## Question 34

### Problem

Design (and implement) a small composable CLI filter, `redact.py`,
meant to sit inside a larger pipeline processing log lines:
`cat app.log | python redact.py --pattern "sk_live_\w+" | tee scrubbed.log`.
It should replace any text matching a given regex pattern with `***`,
streaming line by line, while logging (at `INFO`, to stderr) how many
replacements were made in total once processing finishes — without
that count ever touching stdout.

### Requirements

- Accept `--pattern` as a required CLI argument.
- Use the `re` module (introduced in this module only as needed for
  format-shaped checks) to compile the pattern once, not per line.
- Stream stdin to stdout line by line.
- Log a final `INFO` summary to stderr after EOF.
- Exit `0` regardless of whether any replacements were made (this is a
  filter, not a validator).

### Solution

```python
"""redact.py — a streaming, pipeline-safe log redaction filter."""
import argparse
import logging
import re
import sys

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Redact text matching a pattern from stdin.")
    parser.add_argument("--pattern", required=True, help="Regular expression to redact")
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    args = build_parser().parse_args(argv)
    compiled = re.compile(args.pattern)

    total_replacements = 0
    for line in sys.stdin:
        redacted, count = compiled.subn("***", line)
        total_replacements += count
        sys.stdout.write(redacted)

    logger.info("Redacted %d occurrence(s) of pattern %r", total_replacements, args.pattern)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Explanation

`re.compile(args.pattern)` compiles the pattern exactly **once**,
before the streaming loop begins — compiling inside the loop would
re-parse the same regex on every single line, wasted work that scales
badly on a large log file. `compiled.subn(...)` (rather than `.sub()`)
returns both the replaced text *and* the number of replacements made,
which is what allows the running total to be tracked without a separate
counting pass. Every line is written to `sys.stdout` immediately as
it's processed — this is a true streaming filter, composable with `tee`
or any other pipeline stage, and never buffers the whole log in memory.
The summary count is deliberately routed through `logger.info(...)`
(stderr) rather than `print()`, so it never becomes part of the
scrubbed log data `tee scrubbed.log` captures — exactly the same
stdout/stderr discipline this module has emphasized since 07, now
combined with a genuinely reusable, standard-library-only text-
processing filter.

### Concepts Tested

argparse `required=True`, `re` module for pattern-shaped text
processing, streaming pipeline design, logging a summary without
polluting stdout (06, 07, 08 combined; `re` introduced narrowly per
09's guidance on when regex is appropriate).

---

## Question 35

### Problem

Design a pytest test suite for the `build_config()` function from
Question 29 (`PORT`/`--port` precedence, required `API_KEY`, optional
`LOG_LEVEL`). Your tests must cover: the CLI-overrides-environment
case, the environment-only case, the default-port case, the missing-
`API_KEY` fail-fast case (and its exit code), and confirm that no test
ever asserts on or prints the actual `API_KEY` value.

### Requirements

- Use `monkeypatch.setenv`/`delenv` to control the environment per
  test.
- Use `pytest.raises(SystemExit)` for the missing-`API_KEY` case, and
  check its `.value.code`.
- Use an explicit `argv` list in every call to `build_config()`.
- Explain, in a comment, why none of the tests print or assert the
  literal secret value.

### Solution

```python
import pytest

from myapp.config import build_config


def test_cli_port_overrides_environment(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("API_KEY", "test-key-not-a-real-secret")

    config = build_config(["--port", "1234"])

    assert config.port == 1234


def test_environment_port_used_when_no_cli(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("API_KEY", "test-key-not-a-real-secret")

    config = build_config([])

    assert config.port == 9000


def test_default_port_when_nothing_set(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.setenv("API_KEY", "test-key-not-a-real-secret")

    config = build_config([])

    assert config.port == 8000


def test_missing_api_key_fails_fast(monkeypatch, capsys):
    monkeypatch.delenv("API_KEY", raising=False)

    with pytest.raises(SystemExit) as exc_info:
        build_config([])

    assert exc_info.value.code == 4
    # We assert only that an error message EXISTS on stderr — never that
    # it contains any specific secret value, since there is none to leak here.
    assert "API_KEY" in capsys.readouterr().err


def test_default_log_level(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.setenv("API_KEY", "test-key-not-a-real-secret")

    config = build_config([])

    assert config.log_level == "INFO"
```

### Explanation

Each test uses `monkeypatch.setenv`/`delenv`, which automatically
restores the real environment after the test finishes — this is what
makes it safe to freely set and unset `PORT`, `API_KEY`, and
`LOG_LEVEL` per test without any test leaking its environment changes
into the next one. Passing an explicit `argv` list (e.g. `["--port",
"1234"]`, or `[]`) to `build_config()` — rather than relying on the
real `sys.argv` — is what makes each precedence case independently
controllable and deterministic. `pytest.raises(SystemExit)` catches the
`SystemExit` raised for a missing `API_KEY`, and `exc_info.value.code`
confirms it's specifically `4`, not just "some failure." Note that
every test uses an obviously-fake placeholder value
(`"test-key-not-a-real-secret"`) for `API_KEY` rather than any value
resembling a real secret, and no test ever asserts on or prints the
secret's actual contents — only whether it was *present* or *absent* —
which is the correct testing discipline for secret-bearing
configuration: test the *behavior* around a secret, never the secret
value itself.

### Concepts Tested

pytest `monkeypatch` for environment variables, `pytest.raises(SystemExit)`
and exit-code assertions, explicit `argv` testing, safe testing
practices around secrets (09 and 07's testing sections combined).

---

## Question 36

### Problem

You are asked to design (not necessarily fully implement) the
architecture for a production CLI, `pipeline_gate.py`, used as one
step in an automated data pipeline. It reads a CSV of sensor readings,
validates and cleans them, writes a cleaned CSV and a JSON summary,
reads its behavior (thresholds, output paths, log level) from a
combination of environment variables and CLI flags, logs safely to
both console and a rotating file, and must produce an exit code an
orchestrator can rely on to decide whether to proceed, retry, or alert.
Describe the architecture, then implement the top-level `main()` and
`build_config()` functions (the full row-processing logic can be a
short illustrative stub).

### Requirements

- Describe the layered architecture: CLI layer, configuration layer,
  validation layer, business logic, I/O, logging — in your own words,
  referencing which module concepts belong in each layer.
- Implement `build_config()` producing a frozen `AppConfig`.
- Implement `main(argv) -> int` wiring the layers together, using a
  documented exit-code scheme.
- Explain, explicitly, why each major design decision was made.

### Solution

**Architecture:**

```
CLI arguments (argparse)          }
Environment variables (os.getenv) } → build_config() → AppConfig (frozen dataclass)
                                                              ↓
                                                    configure_logging(config.log_level)
                                                              ↓
                                              validate_input_file(config.input_path)  [pathlib]
                                                              ↓
                                    process_readings(config)  — CSV read/validate/clean [csv]
                                                              ↓
                              write_outputs(config, cleaned_rows, summary)  — CSV + JSON out
                                                              ↓
                                                  logger.info(summary)  [stderr + rotating file]
                                                              ↓
                                          print(json.dumps(summary))  [stdout — the actual result]
                                                              ↓
                                                    return exit_code   [0 / 3 / 4]
```

The **CLI layer** (argparse) is responsible only for syntax: what
flags exist, their types, and basic per-argument constraints (choices,
required-ness) — nothing about business rules lives here. The
**configuration layer** (`build_config()`) is the single place CLI
values and environment variables are merged according to an explicit
precedence, validated, and normalized into one immutable `AppConfig` —
no other function reads `os.environ` or `args` directly. The
**validation layer** operates on `AppConfig`'s fields (e.g. checking
`input_path` exists) and, separately, on each CSV row (error
collection, since rows are independent). **Business logic**
(`process_readings`) takes only already-validated inputs and knows
nothing about CLI, environment, or logging configuration — it could be
unit-tested with plain Python values and no CLI involved at all.
**I/O** (reading/writing the CSV and JSON files) is kept in thin
functions separate from the validation/cleaning logic itself, so each
can be tested independently. **Logging** is configured once, at
startup, with both a console handler and a `RotatingFileHandler` so
the file doesn't grow unbounded across repeated runs; only specific,
non-sensitive fields of `AppConfig` are ever logged.

```python
"""pipeline_gate.py — production-style sensor data validation gate."""
import argparse
import csv
import json
import logging
import logging.config
import os
import sys
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AppConfig:
    input_path: Path
    output_path: Path
    max_invalid_percent: float
    log_level: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and clean sensor readings.")
    parser.add_argument("input_path", type=Path)
    parser.add_argument("--output", type=Path, default=Path("cleaned.csv"))
    parser.add_argument("--max-invalid-percent", type=float, default=None)
    return parser


def build_config(argv: list[str] | None = None) -> AppConfig:
    args = build_parser().parse_args(argv)

    if not args.input_path.is_file():
        print(f"error: input file not found: {args.input_path}", file=sys.stderr)
        raise SystemExit(4)

    max_invalid = (
        args.max_invalid_percent
        if args.max_invalid_percent is not None
        else float(os.getenv("MAX_INVALID_PERCENT", "5.0"))
    )
    if not (0.0 <= max_invalid <= 100.0):
        print(f"error: max-invalid-percent must be between 0 and 100, got {max_invalid}", file=sys.stderr)
        raise SystemExit(4)

    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()

    return AppConfig(
        input_path=args.input_path,
        output_path=args.output,
        max_invalid_percent=max_invalid,
        log_level=log_level,
    )


def configure_logging(level: str) -> None:
    logging.config.dictConfig({
        "version": 1,
        "formatters": {"default": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}},
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "default", "level": level},
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": "pipeline_gate.log",
                "maxBytes": 1_000_000,
                "backupCount": 3,
                "encoding": "utf-8",
                "level": "DEBUG",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console", "file"]},
    })


def process_readings(config: AppConfig) -> dict:
    valid_rows = []
    invalid = 0
    total = 0

    with config.input_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            total += 1
            try:
                row["value"] = float(row["value"])
            except (KeyError, ValueError):
                logger.warning("Line %d: invalid 'value', dropping", line_number)
                invalid += 1
                continue
            valid_rows.append(row)

    with config.output_path.open("w", newline="", encoding="utf-8") as handle:
        if valid_rows:
            writer = csv.DictWriter(handle, fieldnames=valid_rows[0].keys())
            writer.writeheader()
            writer.writerows(valid_rows)

    invalid_percent = (invalid / total * 100) if total else 0.0
    logger.info("Processed %s: %d valid, %d invalid (%.2f%%)", config.input_path, len(valid_rows), invalid, invalid_percent)

    return {
        "total": total,
        "valid": len(valid_rows),
        "invalid": invalid,
        "invalid_percent": round(invalid_percent, 2),
        "passed": invalid_percent <= config.max_invalid_percent,
    }


def main(argv: list[str] | None = None) -> int:
    try:
        config = build_config(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 4

    configure_logging(config.log_level)
    logger.info("Starting pipeline_gate: max_invalid_percent=%s", config.max_invalid_percent)

    summary = process_readings(config)
    print(json.dumps(summary))

    return 0 if summary["passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
```

### Explanation

**Why this layering:** each layer has exactly one job and depends only
on the layer(s) below it in the diagram — `process_readings()` never
touches `argparse` or `os.environ` directly, which means it can be
unit-tested by constructing an `AppConfig` by hand, with no CLI
invocation needed at all. **Why one `build_config()`:** every setting
this program needs — from three different sources (CLI, environment,
built-in default) — is resolved in exactly one place, with an explicit
precedence (`args.max_invalid_percent if ... is not None else
os.getenv(...)`), eliminating the "configuration read from multiple
places" bug class from earlier in this set. **Why a frozen
`AppConfig`:** once built and validated, nothing later in the run
should be able to silently change it. **Why `RotatingFileHandler`:**
this is a pipeline step expected to run repeatedly (once per pipeline
invocation) — a plain, non-rotating log file would grow without bound
across many runs. **Why three distinct exit codes:** `4` (configuration
or input problem — the gate never even got to evaluate data quality),
`3` (the gate ran successfully but the data failed the quality
threshold), and `0` (everything passed) — giving the orchestrator
enough information to decide, automatically, whether to retry (a
config problem might be fixable and worth retrying), alert a human (a
genuine data-quality failure), or simply proceed (success) — without
ever needing to parse this program's printed output to make that
decision.

### Concepts Tested

Full-module capstone: layered CLI architecture, configuration
precedence and centralization, frozen dataclass configuration,
`RotatingFileHandler`, error-collection row validation with an
aggregate threshold decision, a documented multi-way exit-code scheme,
and safe, structured logging — drawing on all nine source files.

---

# Coverage Matrix

| Topic / File | Basic | Moderate | Hard | Advanced | Question Numbers |
|---|---|---|---|---|---|
| 01 — Text Files | ✓ | ✓ | | ✓ | 1, 12, 17, 33 |
| 02 — pathlib | ✓ | ✓ | ✓ | ✓ | 2, 10, 17, 23, 28, 33, 36 |
| 03 — CSV | ✓ | ✓ | ✓ | ✓ | 3, 10, 15, 16, 19, 24, 28, 31, 36 |
| 04 — JSON and Serialization | ✓ | ✓ | ✓ | ✓ | 4, 11, 16, 22, 24, 28, 30 |
| 05 — Encodings and Newlines | ✓ | ✓ | ✓ | ✓ | 5, 12, 19, 33 |
| 06 — argparse | ✓ | ✓ | ✓ | ✓ | 6, 10, 13, 20, 28, 29, 31, 34, 36 |
| 07 — Standard Streams and Exit Codes | ✓ | ✓ | ✓ | ✓ | 7, 13, 18, 24, 25, 28, 30, 34, 35, 36 |
| 08 — Logging vs. print | ✓ | ✓ | ✓ | ✓ | 8, 15, 21, 28, 30, 32, 33, 34, 36 |
| 09 — Environment Configuration and Input Validation | ✓ | ✓ | ✓ | ✓ | 9, 11, 14, 20, 23, 26, 27, 29, 31, 32, 35, 36 |

Every source file is represented at all four difficulty levels, and
every question after Question 9 combines at least two of the module's
nine chapters, with the nine Advanced questions each drawing on
multiple chapters to simulate realistic, production-oriented CLI and
data-processing systems.
