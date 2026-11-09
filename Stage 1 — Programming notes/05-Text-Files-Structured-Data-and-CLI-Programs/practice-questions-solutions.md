# Module 1.5 — Cumulative Practice Questions: Complete Solutions

**Scope:** Stage 1 → Module 1.5 — Text Files, Structured Data, and CLI Programs  
**Coverage:** Questions 1–36 (Basic 1–9, Moderate 10–18, Hard 19–27, Advanced 28–36)  
**Solution policy:** Standard library only, except Question 35, which uses the lesson's `pytest` examples.

---

## 1. Learning-level and project-tree review

The roadmap context available from the earlier Module 05 lesson guides records Stage 1 — Programming & Computational Thinking — as **24 modules, 212 numbered lessons, and 282 files**. Its four stage-level projects are:

1. **Personal Expense Ledger CLI** — command-line expense tracking and reporting.
2. **Log Investigation and Reliability CLI** — operational log inspection and reliability reporting.
3. **Data Quality and Transformation Pipeline** — `orders.csv`, a `dqpipe` package (`cli.py`, `config.py`, `pipeline.py`, `rules.py`), tests, configuration, and a data contract.
4. **Rule-Based Risk Review Engine** — `transactions.csv`, `rules.toml`, a `riskreview` package (`cli.py`, `engine.py`, `io.py`, `models.py`, `rules.py`), tests, and golden decision data.

Module 05 contains these nine lessons, all recorded as completed before this cumulative practice set:

1. Reading and Writing Text Files.
2. `pathlib` and Portable Paths.
3. CSV Files.
4. JSON and Serialization.
5. Encodings and Newlines.
6. Command-Line Arguments with `argparse`.
7. Standard Streams and Exit Codes.
8. Logging versus `print()`.
9. Environment Configuration and Input Validation.

Your recorded level is **beginner progressing toward intermediate**. You have studied Python fundamentals, functions, collections, exceptions, basic algorithms, and all nine Module 05 topics. Solutions stay within those foundations and the standard library; `pytest` is used only where Question 35 requires it.

---

# BASIC — Questions 1–9

## Question 1 — Read a text file safely

```python
def read_notes(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError:
        return f"No notes found at {path}."
```

**Line-by-line:** Define the function and enter `try`. `with open(...)` reads UTF-8 and guarantees closure. `.read()` returns the full text. Catch only `FileNotFoundError` and return a friendly message; other errors remain visible.

## Question 2 — Build a portable path

```python
from pathlib import Path

report_path = Path("data") / "report.csv"
print("Exists:", report_path.exists())
print("Is a file:", report_path.is_file())
print("Suffix:", report_path.suffix)
```

**Line-by-line:** Import `Path`; join path components with `/`, which is portable. `.exists()` checks for any filesystem entry, `.is_file()` checks for a regular file, and `.suffix` returns `.csv`.

## Question 3 — Read CSV rows as dictionaries

```python
import csv
from pathlib import Path

def load_employees(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)
```

**Line-by-line:** Import CSV and `Path`; define the function. Open UTF-8 with `newline=""`, letting the CSV parser handle embedded newlines. `DictReader` maps header names to values; `list()` returns all rows. Manual `split(",")` fails on quoted commas and multiline fields.

## Question 4 — Safely access an optional JSON field

```python
import json

raw = '{"name": "Alice", "age": 30, "active": true}'
record = json.loads(raw)
email = record.get("email", "no email on file")
print(email)
```

**Line-by-line:** Import JSON and store the text. `loads()` parses an in-memory string into a dictionary (`true` becomes `True`). `.get()` supplies a default for a missing key, avoiding `KeyError`; print the result.

## Question 5 — Read UTF-8 explicitly

```python
# Omitting encoding uses a machine-dependent default. A mismatch can
# raise UnicodeDecodeError or produce incorrect characters (mojibake).
with open("report.txt", "r", encoding="utf-8") as handle:
    text = handle.read()

print(text)
```

**Line-by-line:** The comment explains why relying on the machine's default encoding is unsafe. `open()` reads the file as UTF-8. `read()` decodes and returns the full text. `print()` displays it. An explicit encoding makes behavior predictable across machines, assuming the file really is UTF-8.

## Question 6 — Required positional CLI argument

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

**Line-by-line:** Import `argparse`. Create a parser with a description. Adding `"name"` without dashes creates a required positional argument. Return the parser. `main()` parses command-line arguments; if `name` is missing, `argparse` prints usage to stderr and exits with status 2. Otherwise print the greeting. The `__main__` guard runs the CLI only when this file is executed directly.

## Question 7 — Separate result and diagnostic streams

```python
import sys

print("Calculating...", file=sys.stderr)  # diagnostic
print("42")                               # result; stdout is print's default
```

**Line-by-line:** Import `sys` to access standard streams. The first `print()` explicitly writes the status message to stderr. The second writes the actual result to stdout by default. Shell `>` redirects stdout, so `result.txt` receives only `42`; the status message remains on stderr.

## Question 8 — Replace diagnostic prints with logging

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

**Line-by-line:** Import and configure logging at INFO. Get a named module logger. Define `process`, log routine progress with deferred `%s` formatting, log unusually large values as WARNING, and return twice the input.

## Question 9 — Read an integer environment setting

```python
import os

max_retries = int(os.getenv("MAX_RETRIES", "3"))
print(max_retries, type(max_retries))
```

**Line-by-line:** Import `os`. `getenv()` returns the environment value or the string default `"3"`; environment values are strings. `int()` converts that text into an integer. Print the value and its type to verify the conversion.

---

# MODERATE — Questions 10–18

## Question 10 — Count CSV data rows with a CLI

```python
import argparse
import csv
import sys
from pathlib import Path

def build_parser():
    parser = argparse.ArgumentParser(description="Count CSV data rows.")
    parser.add_argument("csv_file", type=Path)
    return parser

def main() -> int:
    path = build_parser().parse_args().csv_file
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2
    try:
        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            next(reader, None)
            count = sum(1 for _ in reader)
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 2
    print(count)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

**Line-by-line:** Imports support parsing, CSV, stderr, and paths. `type=Path` converts the argument. `main()` checks `.is_file()`, then opens with CSV-safe newlines and UTF-8; the `try` handles failures that occur after the check. `next(..., None)` skips the header safely. The generator counts remaining rows without storing them. Print the count; return 0, or stderr plus 2 on error. `SystemExit` exposes the status.

## Question 11 — Collect missing-price errors

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

**Line-by-line:** Parse the JSON string. Initialize a numeric total and an error list. Iterate through `items`, defaulting to an empty list if the key is absent. If an item lacks `price`, append an identifying message and `continue` to the next item. Otherwise add its price. Return both results; unpack and print them. This is error collection: independent records are all checked instead of stopping at the first problem. The input contract assumes `items` contains dictionaries and valid numeric prices; broader type validation would be an additional requirement.

## Question 12 — Compare a line without its newline

```python
with open("commands.txt", "r", encoding="utf-8") as handle:
    for line in handle:
        if line.rstrip("\r\n") == "END":
            print("Found the end marker")
```

**Line-by-line:** Open the text file as UTF-8. Iterate one line at a time; the yielded string includes its newline. `rstrip("\r\n")` removes only trailing CR/LF characters, leaving other whitespace untouched. Compare the remaining content with `"END"`. Text mode normally translates CRLF to LF, but the LF still makes `"END\n" != "END"`; removing the terminator fixes it.

## Question 13 — Add a Boolean `--shout` flag

```python
import argparse

def build_parser():
    parser = argparse.ArgumentParser(description="Greet someone by name.")
    parser.add_argument("name")
    parser.add_argument("--shout", action="store_true")
    return parser

def main() -> int:
    args = build_parser().parse_args()
    message = f"Hello, {args.name}!"
    print(message.upper() if args.shout else message)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

**Line-by-line:** Create a parser. `"name"` is a required positional argument. `store_true` makes `--shout` true when present and false otherwise. Parse arguments, build the greeting, and select uppercase or normal text with a conditional expression. Return 0 on success. Missing `name` is rejected automatically by argparse with status 2. The main guard converts the return code into the process status.

## Question 14 — Normalize and validate `APP_ENV`

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

**Line-by-line:** Import `os` and define the allowed values. Read the setting, using `"development"` when absent. `strip()` removes surrounding whitespace and `lower()` standardizes case. Check the normalized value against the allowed set. Raise a clear `ValueError` containing the original value and allowed choices if invalid. Return the normalized value when valid. Normalization changes representation; validation decides whether the result is allowed.

## Question 15 — Log to console and file, print only the result

```python
import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def configure_logging() -> None:
    logger.setLevel(logging.INFO)
    for handler in (
        logging.StreamHandler(),
        logging.FileHandler("process.log", encoding="utf-8"),
    ):
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s"
        ))
        logger.addHandler(handler)

def process(path: Path) -> int:
    valid = 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        for line_number, row in enumerate(csv.DictReader(handle), start=2):
            if not row.get("id"):
                logger.warning("Line %d: missing id; skipping", line_number)
                continue
            valid += 1
    logger.info("Finished %s: %d valid rows", path, valid)
    return valid

if __name__ == "__main__":
    configure_logging()
    print(process(Path("data.csv")))
```

**Line-by-line:** Import CSV, logging, and `Path`; create a named logger. Configure its INFO threshold. Create a console handler and UTF-8 file handler. Give each the same formatter and attach both. `process()` opens the CSV correctly and uses `DictReader`. Enumerate from 2 because row 1 is the header. A missing ID produces a WARNING and skips the row; otherwise increment the valid count. Log the summary and return the count. The final `print()` writes only the result to stdout; default `StreamHandler` diagnostics go to stderr. Call configuration once per process to avoid duplicate handlers.

## Question 16 — Convert CSV products to JSON

```python
import csv
import json
from pathlib import Path

def csv_to_json(csv_path: Path, json_path: Path) -> None:
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        products = [
            {"name": row["name"], "price": float(row["price"])}
            for row in csv.DictReader(handle)
        ]
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(products, handle, indent=2)
```

**Line-by-line:** Import the required modules. Define source and destination paths. Open the CSV with `newline=""` and UTF-8. `DictReader` produces string values; the comprehension creates dictionaries and explicitly converts price to `float`. Close the input before opening the output. Open the JSON destination in write mode and `json.dump()` serializes the Python list directly to the file with two-space indentation.

## Question 17 — Write safely without accidental overwrite

```python
from pathlib import Path

def safe_write(path: Path, content: str, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if overwrite else "x"
    try:
        with path.open(mode, encoding="utf-8") as handle:
            handle.write(content)
    except FileExistsError:
        raise FileExistsError(
            f"refusing to overwrite existing file: {path} (pass overwrite=True)"
        ) from None
```

**Line-by-line:** Define the function and default to refusing overwrite. Create all missing parent directories; existing directories are acceptable. Choose `"w"` only when overwrite is explicitly allowed; otherwise choose `"x"`, exclusive creation. Open with UTF-8 and write the content. If exclusive creation finds an existing file, raise a clearer `FileExistsError`. Using `"x"` avoids the race in a separate `exists()` check followed by `"w"`.

## Question 18 — Stream stdin to uppercase stdout

```python
import sys

def main() -> int:
    for line in sys.stdin:
        sys.stdout.write(line.upper())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

**Line-by-line:** Import `sys`. Define the CLI entry point. Iterate directly over stdin, yielding one line at a time instead of loading all input. Uppercase each line and write it to stdout. The newline is already part of the line, so `write()` preserves it without adding another. Return success and convert it to the process exit status.

---

# HARD — Questions 19–27

## Question 19 — Fix CSV encoding and newline handling

```python
import csv
from pathlib import Path

def load_csv(path: Path) -> list[list[str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle))
```

**Line-by-line:** Import CSV and `Path`. Accept a path. Open explicitly as UTF-8 and use `newline=""`, required for correct CSV newline handling, including quoted embedded newlines. `csv.reader` parses fields according to CSV rules. `list()` returns all rows. The original omitted encoding, so behavior depended on the machine's locale; it also omitted CSV's recommended newline setting. If a file is truly Windows-1252 rather than UTF-8, this version raises `UnicodeDecodeError`. Detect that through the decoding failure and apply a documented, known fallback encoding; do not silently guess or ignore decoding errors.

## Question 20 — Fix `argparse type=bool`

```python
# Option A: presence-only flag
parser.add_argument("--verbose", action="store_true")

# Option B: accept explicit true/false text
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

**Line-by-line:** Option A uses a flag: presence means `True`; absence means `False`; no value follows it. Option B imports argparse and defines a parser. Normalize the supplied text. Recognized true spellings return `True`; recognized false spellings return `False`; anything else raises `ArgumentTypeError`, which argparse formats as a usage error. `type=bool` is wrong because `bool("false")` is `True`: Python tests whether the string is empty, not whether its text means false.

## Question 21 — Configure logging before any module logs

```python
# app.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(message)s",
)

import helper  # helper may call logging.warning() during import

def main():
    logging.debug("debug message now uses the intended configuration")
```

**Line-by-line:** Import logging. Configure the root logger immediately, before importing modules that might emit log messages. Importing `helper` now occurs after configuration. `main()` emits DEBUG, which is enabled by the configured threshold. The bug occurs because a module-level convenience call such as `logging.warning()` can trigger default logging configuration; a later `basicConfig()` does nothing if the root already has a handler. A cleaner long-term design is to avoid logging at import time, but this ordering fixes the stated scenario.

## Question 22 — Convert malformed JSON into an actionable error

```python
import json
from pathlib import Path

def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON in {path}: {exc}") from exc
```

**Line-by-line:** Import JSON and `Path`. Open the file as UTF-8. `json.load()` parses from the file object. Catch only `JSONDecodeError`, the expected malformed-JSON exception. Raise a `ValueError` that identifies the file and includes the parser's message. `from exc` preserves the original cause. `FileNotFoundError` is intentionally not caught: a missing file is a separate failure the caller can report with its own context.

## Question 23 — Prevent path traversal

```python
from pathlib import Path

def resolve_upload_path(base: Path, user_supplied_subpath: str) -> Path:
    allowed_base = base.resolve()
    candidate = (allowed_base / user_supplied_subpath).resolve()
    if not candidate.is_relative_to(allowed_base):
        raise ValueError(
            f"path escapes the allowed upload directory: {user_supplied_subpath!r}"
        )
    return candidate
```

**Line-by-line:** Import `Path`. Resolve the trusted base to an absolute normalized path. Join the untrusted subpath and resolve it too, removing `..` traversal components and resolving symlinks according to filesystem behavior. `is_relative_to()` checks that the candidate remains beneath the allowed base. Reject an escaping path before writing; otherwise return the safe candidate. This is path traversal prevention, but it does not eliminate every filesystem race or permission risk.

## Question 24 — Validate JSONL with error collection

```python
import json
import sys
from pathlib import Path

def validate_records(path: Path) -> tuple[int, list[str]]:
    valid = 0
    errors = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"line {line_number}: invalid JSON")
                continue
            if not isinstance(record, dict):
                errors.append(f"line {line_number}: expected a JSON object")
                continue
            if "customer_id" not in record:
                errors.append(f"line {line_number}: missing customer_id")
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

**Line-by-line:** Initialize counters, open UTF-8, and stream numbered JSONL lines. Skip blanks; record malformed JSON, non-object records, and missing IDs, continuing after each error. Count valid records and return the count plus errors. `main()` sends details to stderr, prints a summary, and returns 0 only when no errors exist; otherwise 3. Fail-fast suits critical configuration, while independent rows benefit from error collection.

## Question 25 — Keep pipeline diagnostics off stdout

```python
import sys

def main() -> int:
    print("Loading rows...", file=sys.stderr)
    for line in sys.stdin:
        sys.stdout.write(line.strip().upper() + "\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

**Line-by-line:** Import `sys`. Define the filter. Send the progress message to stderr, not stdout. Read stdin one line at a time. Transform each data line and write it to stdout. Return success and expose it as the process status. The original bug was that the progress message went to stdout and therefore became input to the next process in the pipeline.

## Question 26 — Correct environment type conversion

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

**Line-by-line:** Import `os`. Define a Boolean parser and normalize the text. Return true or false for recognized spellings; reject unknown text. Convert the retry limit explicitly to `int` and use a string default so the input type is consistent. Parse `DRY_RUN` by meaning, not with `bool()`. The two original bugs were an integer default mixed with environment strings, and `bool("false")` evaluating to `True`.

## Question 27 — Centralize configuration precedence

```python
import os

def resolve_port(cli_value: int | None) -> int:
    if cli_value is not None:
        return cli_value
    return int(os.getenv("PORT", "8000"))
```

```python
def test_cli_wins(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    assert resolve_port(8080) == 8080

def test_environment_used_without_cli(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    assert resolve_port(None) == 9000

def test_default_used_when_unset(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    assert resolve_port(None) == 8000
```

**Line-by-line:** `resolve_port()` is the single authority for precedence. An explicitly supplied CLI value wins; otherwise read and convert the environment value, defaulting to 8000. The tests set or remove environment variables in isolation. Each assertion verifies one precedence rule. The architectural bug was reading configuration in multiple places with inconsistent precedence. Resolve once at startup and pass the resulting value to other functions. These tests use pytest's `monkeypatch` fixture, which restores environment changes after each test.

---

# ADVANCED — Questions 28–36

## Question 28 — Complete orders-report CLI

```python
import argparse, csv, json, logging, sys
from pathlib import Path

logger = logging.getLogger(__name__)

def build_parser():
    parser = argparse.ArgumentParser(description="Validate and summarize orders.")
    parser.add_argument("orders_file", type=Path)
    return parser

def process_orders(path: Path) -> dict:
    valid = invalid = 0
    total_amount = 0.0
    with path.open("r", newline="", encoding="utf-8") as handle:
        for number, row in enumerate(csv.DictReader(handle), start=2):
            if not row.get("order_id"):
                logger.warning("Line %d: missing order_id", number)
                invalid += 1
                continue
            raw = row.get("amount")
            if raw is None or not raw.strip():
                logger.warning("Line %d: missing amount", number)
                invalid += 1
                continue
            try:
                amount = float(raw)
            except ValueError:
                logger.warning("Line %d: invalid amount", number)
                invalid += 1
                continue
            valid += 1
            total_amount += amount
    logger.info("Processed %s: %d valid, %d invalid", path, valid, invalid)
    return {"total_orders": valid, "total_amount": round(total_amount, 2),
            "invalid_rows": invalid}

def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    path = build_parser().parse_args(argv).orders_file
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 4
    try:
        summary = process_orders(path)
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 4
    print(json.dumps(summary))
    return 0 if summary["invalid_rows"] == 0 else 3

if __name__ == "__main__":
    raise SystemExit(main())
```

**Line-by-line:** Imports provide CLI parsing, CSV/JSON, logging, stderr, and paths. Create a named logger. The parser defines one required path converted to `Path`. `process_orders()` initializes valid/invalid counts and amount total. Open the CSV correctly and enumerate data rows from line 2. Validate only `order_id` and `amount`, as required; `customer` is deliberately not validated. Missing, empty, or non-numeric amounts are logged and counted, then processing continues. Valid rows increment the count and amount. Log the summary and return the three requested metrics. `main()` configures logging, parses the path, returns 4 for missing or unreadable input, prints only JSON to stdout, and returns 3 if any row was invalid, otherwise 0. The guard exposes the exit status.

## Question 29 — Immutable configuration with a secret

```python
import argparse, os, sys
from dataclasses import dataclass, field

@dataclass(frozen=True)
class AppConfig:
    port: int
    log_level: str
    api_key: str = field(repr=False)

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=None)
    return parser

def build_config(argv=None) -> AppConfig:
    args = build_parser().parse_args(argv)
    port = args.port if args.port is not None else int(os.getenv("PORT", "8000"))
    level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    api_key = os.environ.get("API_KEY")
    if not api_key:
        print("error: API_KEY environment variable is required", file=sys.stderr)
        raise SystemExit(4)
    return AppConfig(port=port, log_level=level, api_key=api_key)

def main(argv=None) -> int:
    config = build_config(argv)
    print(f"Starting on port {config.port}; log level {config.log_level}")
    return 0
```

**Line-by-line:** Import configuration dependencies and dataclass helpers. Define a frozen dataclass so its fields cannot be reassigned; `repr=False` excludes the API key from the generated representation. The parser accepts optional `--port`, defaulting to `None` so the code can distinguish absence from a supplied value. `build_config()` parses the explicit argument list. CLI port wins; otherwise the environment value or 8000 is used. Normalize the log level. Read the required secret from the environment only. If absent or empty, report the variable name to stderr and exit 4. Return the configuration object. `main()` prints only non-secret fields. Never log the key or the entire config object.

## Question 30 — Streaming JSONL validator

```python
import json, logging, sys

logger = logging.getLogger(__name__)

def main() -> int:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    dropped = 0
    for number, line in enumerate(sys.stdin, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            logger.warning("Line %d: invalid JSON; dropped", number)
            dropped += 1
            continue
        if not isinstance(record, dict):
            logger.warning("Line %d: expected JSON object; dropped", number)
            dropped += 1
            continue
        if "id" not in record:
            logger.warning("Line %d: missing id; dropped", number)
            dropped += 1
            continue
        sys.stdout.write(line)
    return 0 if dropped == 0 else 3

if __name__ == "__main__":
    raise SystemExit(main())
```

**Line-by-line:** Import JSON, logging, and streams. Create a named logger and configure WARNING output. Initialize the dropped count. Iterate over stdin one line at a time, skipping blank lines. Parse JSON and catch malformed syntax. Require a dictionary before using dictionary membership. Require the `id` key. Each invalid record is logged to stderr, counted, and skipped. Write each valid original line unchanged to stdout. Return 0 when none were dropped, otherwise 3. Memory use is bounded to the current line and parsed record, not the entire input.

## Question 31 — CSV data-quality gate

```python
import argparse, csv, json, logging
from pathlib import Path

logger = logging.getLogger(__name__)

def percent(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    if not 0.0 <= number <= 100.0:
        raise argparse.ArgumentTypeError("must be between 0 and 100")
    return number

def validate_row(row: dict, number: int):
    if not row.get("id"):
        return f"line {number}: missing id"
    try:
        confidence = float(row["confidence"])
    except (KeyError, ValueError, TypeError):
        return f"line {number}: invalid confidence"
    if not 0.0 <= confidence <= 1.0:
        return f"line {number}: confidence outside [0, 1]"
    return None

def main(argv=None) -> int:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="CSV data-quality gate.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--max-invalid-percent", type=percent, default=5.0)
    args = parser.parse_args(argv)
    total = invalid = 0
    with args.dataset.open("r", newline="", encoding="utf-8") as handle:
        for number, row in enumerate(csv.DictReader(handle), start=2):
            total += 1
            error = validate_row(row, number)
            if error:
                logger.warning(error)
                invalid += 1
    rate = invalid / total * 100 if total else 0.0
    passed = rate <= args.max_invalid_percent
    print(json.dumps({"total_rows": total, "invalid_rows": invalid,
                      "invalid_percent": round(rate, 2),
                      "threshold_percent": args.max_invalid_percent,
                      "passed": passed}))
    return 0 if passed else 3

if __name__ == "__main__":
    raise SystemExit(main())
```

**Line-by-line:** Import the CLI, CSV, JSON, logging, and path tools. `percent()` converts the CLI text to float and rejects values outside the inclusive 0–100 range with argparse's expected exception. `validate_row()` checks a non-empty ID, converts confidence, and checks the inclusive 0–1 range; it returns an error string or `None`. `main()` configures warnings, declares the path and threshold arguments, and parses them. It streams the CSV, counts every row, logs invalid-row details, and continues. Calculate the invalid percentage safely for an empty file. Compare it with the threshold; equality passes because the requirement says fail when the percentage exceeds the threshold. Print a machine-readable JSON summary and return 0 or 3.

## Question 32 — Prevent secrets leaking through logs

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PaymentConfig:
    merchant_id: str
    api_secret: str
    currency: str

    def __repr__(self) -> str:
        return (
            f"PaymentConfig(merchant_id={self.merchant_id!r}, "
            f"api_secret='***', currency={self.currency!r})"
        )

# Log an explicit allowlist of safe fields, never vars(config).
logger.debug(
    "Processing payment: merchant_id=%s currency=%s",
    payment_config.merchant_id,
    payment_config.currency,
)
```

**Line-by-line:** Import `dataclass`. Define an immutable configuration with merchant ID, secret, and currency. Override `__repr__()` with an allowlist: show approved fields and mask the secret. The logging call names only the two safe fields; it does not serialize the whole object. `vars(payment_config)` is dangerous because it exposes every attribute, including the secret. Important limitation: a custom `repr` does not protect `vars()`, `dataclasses.asdict()`, or direct access to `api_secret`; never pass the object to those logging/serialization paths.

## Question 33 — Read UTF-8/BOM with a documented fallback

```python
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def read_report(path: Path, fallback_encoding: str = "cp1252") -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        logger.warning("%s is not UTF-8; retrying with %s", path, fallback_encoding)
        try:
            return path.read_text(encoding=fallback_encoding)
        except UnicodeDecodeError as exc:
            raise ValueError(
                f"could not decode {path} as UTF-8 or {fallback_encoding}"
            ) from exc

def process_reports(directory: Path) -> list[str]:
    contents = []
    for path in sorted(directory.glob("*.txt")):
        if path.is_file():
            contents.append(read_report(path))
    return contents
```

**Line-by-line:** Import logging and `Path`; create a named logger. `read_report()` first reads as `utf-8-sig`, which accepts UTF-8 and removes a UTF-8 BOM. If UTF-8 decoding fails, log a WARNING and retry with the explicitly chosen fallback, defaulting to Windows-1252. If fallback decoding also fails, raise an actionable `ValueError` chained from the decode error. `process_reports()` initializes results, finds `.txt` files, sorts them for deterministic order, checks each is a file, and appends decoded content. Newline conventions are handled by text-mode reading; CRLF does not require a different character encoding. The fallback must match the source data contract; do not treat it as automatic encoding detection.

## Question 34 — Streaming regex redaction filter

```python
import argparse, logging, re, sys

logger = logging.getLogger(__name__)

def build_parser():
    parser = argparse.ArgumentParser(description="Redact matching text from stdin.")
    parser.add_argument("--pattern", required=True)
    return parser

def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = build_parser().parse_args(argv)
    pattern = re.compile(args.pattern)
    replacements = 0
    for line in sys.stdin:
        redacted, count = pattern.subn("***", line)
        replacements += count
        sys.stdout.write(redacted)
    logger.info("Redacted %d occurrence(s)", replacements)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

**Line-by-line:** Import argparse, logging, regex, and streams. Create a named logger. The parser requires `--pattern`. `main()` configures INFO logging and parses the arguments. Compile the regex once, before reading input. Initialize the replacement counter. Stream each stdin line, use `subn()` to obtain both redacted text and replacement count, add the count, and write the transformed line to stdout. After EOF, log the total; the default logging stream is stderr, so the count does not contaminate pipeline data. Return 0 whether or not a match occurred.

## Question 35 — Test configuration behavior with pytest

```python
import pytest
from myapp.config import build_config

def test_cli_port_overrides_environment(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("API_KEY", "test-key-not-a-real-secret")
    config = build_config(["--port", "1234"])
    assert config.port == 1234

def test_environment_port_is_used(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("API_KEY", "test-key-not-a-real-secret")
    config = build_config([])
    assert config.port == 9000

def test_default_port_is_used(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.setenv("API_KEY", "test-key-not-a-real-secret")
    config = build_config([])
    assert config.port == 8000

def test_missing_api_key_exits_four(monkeypatch, capsys):
    monkeypatch.delenv("API_KEY", raising=False)
    with pytest.raises(SystemExit) as result:
        build_config([])
    assert result.value.code == 4
    assert "API_KEY" in capsys.readouterr().err

def test_default_log_level(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.setenv("API_KEY", "test-key-not-a-real-secret")
    config = build_config([])
    assert config.log_level == "INFO"
```

**Line-by-line:** Import pytest and the function under test. Each test receives `monkeypatch`, which safely changes the environment and restores it afterward. Set `PORT` and a fake API key, call `build_config()` with an explicit argument list, and assert CLI precedence. The next test omits CLI port and asserts environment precedence. The third removes `PORT` and checks the default. The missing-key test removes `API_KEY`, expects `SystemExit`, checks exit code 4, and checks only that stderr names the missing setting. The final test removes `LOG_LEVEL` and checks INFO default. Use only a fake placeholder secret; never print it or assert its literal value. Install pytest to run this file: `python -m pytest -q`.

## Question 36 — Production pipeline gate architecture

**Layer responsibilities**

- **CLI:** `argparse` defines arguments and converts input types.
- **Configuration:** `build_config()` resolves CLI/environment/default precedence once and returns a frozen `AppConfig`.
- **Input/row validation:** `pathlib` checks the input; CSV row checks collect independent data errors.
- **Business processing:** reads and cleans records without reading CLI arguments or environment variables.
- **I/O:** CSV input/output and JSON summary are handled explicitly.
- **Logging:** configure console and rotating-file handlers once; log diagnostics, never secrets.
- **Process contract:** JSON summary goes to stdout; diagnostics go to stderr/log file; exit codes are stable.

```python
import argparse, csv, json, logging, logging.handlers, os, sys
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)
LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

@dataclass(frozen=True)
class AppConfig:
    input_path: Path
    output_path: Path
    max_invalid_percent: float
    log_level: str

def build_config(argv=None) -> AppConfig:
    parser = argparse.ArgumentParser(description="Sensor data pipeline gate.")
    parser.add_argument("input_path", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--max-invalid-percent", type=float, default=None)
    args = parser.parse_args(argv)

    if not args.input_path.is_file():
        raise ValueError(f"input file not found: {args.input_path}")

    threshold = (args.max_invalid_percent if args.max_invalid_percent is not None
                 else float(os.getenv("MAX_INVALID_PERCENT", "5.0")))
    if not 0 <= threshold <= 100:
        raise ValueError("MAX_INVALID_PERCENT must be between 0 and 100")

    output = args.output if args.output is not None else Path(
        os.getenv("OUTPUT_PATH", "cleaned.csv")
    )
    level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    if level not in LEVELS:
        raise ValueError(f"invalid LOG_LEVEL: {level}")
    return AppConfig(args.input_path, output, threshold, level)

def configure_logging(level: str) -> None:
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    file_handler = logging.handlers.RotatingFileHandler(
        "pipeline_gate.log", maxBytes=1_000_000, backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)
    logger.addHandler(file_handler)

def process_readings(config: AppConfig) -> dict:
    valid_rows, invalid, total = [], 0, 0
    with config.input_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for number, row in enumerate(reader, start=2):
            total += 1
            raw = row.get("value")
            try:
                if raw is None or not raw.strip():
                    raise ValueError
                row["value"] = float(raw)
            except ValueError:
                logger.warning("Line %d: invalid or missing value", number)
                invalid += 1
                continue
            valid_rows.append(row)

    if valid_rows:
        with config.output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(valid_rows[0]))
            writer.writeheader()
            writer.writerows(valid_rows)

    rate = invalid / total * 100 if total else 0.0
    return {"total": total, "valid": len(valid_rows), "invalid": invalid,
            "invalid_percent": round(rate, 2),
            "passed": rate <= config.max_invalid_percent}

def main(argv=None) -> int:
    try:
        config = build_config(argv)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4

    configure_logging(config.log_level)
    try:
        summary = process_readings(config)
    except OSError as exc:
        logger.error("I/O failure: %s", exc)
        return 4

    logger.info("Pipeline gate completed: %s", summary)
    print(json.dumps(summary))
    return 0 if summary["passed"] else 3

if __name__ == "__main__":
    raise SystemExit(main())
```

**Line-by-line walkthrough:** Imports supply CLI, CSV/JSON, logging rotation, environment, dataclasses, streams, and paths. `AppConfig` is frozen. `build_config()` parses arguments, checks the input, resolves threshold precedence (CLI → environment → default), validates its range, resolves output precedence, validates the log level, and returns one config object. `configure_logging()` attaches console and rotating UTF-8 file handlers with a shared formatter. `process_readings()` streams rows, validates values, logs/counts invalid rows, writes valid rows, and returns metrics plus the threshold decision. `main()` maps configuration and I/O failures to exit 4, prints JSON to stdout, and returns 0 for pass or 3 for a quality failure. The guard exposes the process status.

**Exit-code contract:** `0` = data-quality gate passed; `3` = processing completed but invalid-row percentage exceeded the threshold; `4` = input/configuration/I/O failure. Downstream orchestration can make decisions from the exit status without parsing log text.

---

## Final coverage and study checklist

| Lesson area | Questions |
|---|---|
| Text files and safe file operations | 1, 5, 17, 22, 33 |
| `pathlib` and path safety | 2, 10, 17, 23, 28, 33, 36 |
| CSV processing | 3, 10, 15, 16, 19, 24, 28, 31, 36 |
| JSON and JSON Lines | 4, 11, 16, 22, 24, 28, 30 |
| Encodings and newlines | 5, 12, 19, 33 |
| `argparse` | 6, 10, 13, 20, 28, 29, 31, 34, 36 |
| Streams and exit codes | 7, 10, 13, 18, 24, 25, 28, 30, 34, 35, 36 |
| Logging | 8, 15, 21, 28, 30, 32, 33, 34, 36 |
| Environment and validation | 9, 11, 14, 20, 23, 26, 27, 29, 31, 32, 35, 36 |

Before considering this practice set complete, make sure you can explain why: `newline=""` is used for CSV; environment values need conversion; `bool("false")` is true; `stdout` carries pipeline data while diagnostics belong on `stderr`; logging levels and handlers are separate; error collection is appropriate for independent rows; configuration precedence should be centralized; and exit codes form a stable contract with downstream automation.
