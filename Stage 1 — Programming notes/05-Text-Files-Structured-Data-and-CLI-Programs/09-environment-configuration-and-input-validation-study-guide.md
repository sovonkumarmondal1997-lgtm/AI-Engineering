# 09 — Environment Configuration and Input Validation

**Stage 1 · Module 05: Text Files, Structured Data, and CLI Programs**  
**Lesson 09 · Level: beginner progressing toward intermediate**

# Part A — Lesson summary (under 5,000 words)

## 1. Configuration, code, and data

**Code** defines what a program does; **configuration** controls how it behaves in a particular environment or run. Code changes when logic changes. Configuration changes when the same logic must use another host, port, log level, feature flag, or deployment setting.

```python
def connect(host: str, port: int):  # code: behavior
    ...

host = "db.production.example.com"  # configuration: variable values
port = 5432
```

Data is the content the program processes (CSV rows, uploaded documents); configuration is how the program processes it. Production code should not hard-code environment-specific values. A setting is **required** when no safe default exists (e.g. database URL); it is **optional** when a safe default exists (e.g. log level `INFO`).

## 2. Environment variables

An environment variable is a string key/value attached to a process. Names conventionally use uppercase and underscores (`DATABASE_URL`). Child processes normally inherit a copy of their parent's environment.

```bash
export APP_ENV=development
export PORT=8000
python app.py
```

```python
import os
print(os.environ["APP_ENV"])  # KeyError if absent
print(os.getenv("PORT"))      # None if absent
```

`os.environ["NAME"]` raises `KeyError` if missing. `os.getenv("NAME")` returns `None`; `os.getenv("NAME", "8000")` returns the default. Use indexing for required settings and a default only when it is genuinely safe. An empty value is not the same as an unset variable.

## 3. Environment values are always strings

The operating system environment stores text only. `PORT=8000` arrives as `"8000"`, a `str`.

```python
value = os.getenv("PORT")
print(type(value), repr(value))  # <class 'str'> '8000'
```

Convert explicitly and report failures clearly:

```python
def get_port(default: int = 8000) -> int:
    raw = os.getenv("PORT")
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"PORT must be an integer, got {raw!r}") from None

def get_threshold(default: float = 0.5) -> float:
    raw = os.getenv("THRESHOLD")
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        raise ValueError(f"THRESHOLD must be a number, got {raw!r}") from None

def get_allowed_hosts() -> list[str]:
    raw = os.getenv("ALLOWED_HOSTS", "")
    return [item.strip() for item in raw.split(",") if item.strip()]
```

`int("42")` works; `int("42.0")` raises `ValueError`. `int(float("42.0"))` works but truncates, so only use it if that behavior is intended. Never assume an environment value already has the required type.

## 4. Defaults and fail-fast

A default applies only when a setting was not supplied. Safe defaults are unsurprising and harmless (e.g. JSON output, 30-second timeout). Dangerous defaults such as `DEBUG=True` or `verify_ssl=False` can turn a configuration mistake into an incident.

**Fail-fast** means refusing to start/proceed immediately when required configuration is missing or invalid.

```python
def get_database_url() -> str:
    value = os.getenv("DATABASE_URL")
    if not value:
        print("error: DATABASE_URL environment variable is required", file=sys.stderr)
        raise SystemExit(4)
    return value
```

Use a safe default silently; log a warning if an unusual-but-acceptable default is active; fail fast if a required value is missing; reject a provided-but-invalid value instead of silently substituting a default.

## 5. Secrets and `.env`

Secrets include API keys, passwords, database credentials, and tokens. Environment variables keep them out of source code and CLI arguments, but are not a complete secret-management solution: privileged processes, crash reports, dumps, or careless logs may expose them. Production may require a secret manager with auditing, rotation, and fine-grained permissions.

Never hard-code or commit secrets. Version-control history may retain a secret after deletion; rotate a real secret committed accidentally. Never log or echo a secret:

```python
# UNSAFE
logger.info("Connecting with API key %s", api_key)
# SAFE
logger.info("API key configured: %s", "yes" if api_key else "no")
```

A `.env` file is plain text `KEY=value` used mainly for local development:

```dotenv
APP_ENV=development
PORT=8000
DATABASE_URL=postgresql://localhost:5432/dev_db
API_KEY=dev-only-fake-key
```

Python's standard library does not load `.env` automatically. `python-dotenv` is a third-party package:

```python
from dotenv import load_dotenv
load_dotenv()
import os
print(os.getenv("PORT"))
```

Ignore `.env` in version control. Commit `.env.example` with placeholders only:

```dotenv
APP_ENV=development
PORT=8000
DATABASE_URL=postgresql://localhost:5432/dev_db
API_KEY=
```

## 6. Configuration precedence

When several sources provide a setting, define precedence explicitly. Common order from lowest to highest:

`built-in defaults → config file → environment variables → CLI arguments`

CLI commonly wins because it is most specific to this invocation. The lesson explains four sources but runnable examples implement only defaults, environment, and CLI.

```python
def resolve_port(cli_value: int | None) -> int:
    if cli_value is not None:
        return cli_value
    env_value = os.getenv("PORT")
    if env_value is not None:
        return int(env_value)
    return 8000
```

Use `is not None`, not truthiness: `0` is falsy but may have been explicitly supplied and should be rejected as invalid, not treated as absent. Scattered environment reads and undocumented precedence create inconsistent behavior.

## 7. CLI parsing and semantic validation

Parsing asks whether an argument can be interpreted. Semantic validation asks whether the parsed value is meaningful for the application.

```python
def existing_file(value: str) -> Path:
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"not a file: {path}")
    return path

parser = argparse.ArgumentParser()
parser.add_argument("input", type=existing_file)
parser.add_argument("--port", type=int, choices=range(1, 65536), default=8000)
parser.add_argument("--format", choices=["json", "csv"], required=True)
```

`type=` converts and can validate; `choices=` restricts values; `required=` requires an optional argument; `default=` supplies a fallback; `nargs=` controls consumed values. `metavar` and `help` document arguments. Cross-argument rules need post-parse checks (often `parser.error()`).

## 8. Validation, normalization, sanitization

- **Validation:** accept/reject without changing the value.
- **Normalization:** convert equivalent forms to one canonical representation.
- **Sanitization:** remove/transform unwanted content for a specific downstream use.

```python
def is_valid_port(value: int) -> bool:
    return 1 <= value <= 65535

def normalize_environment_name(value: str) -> str:
    return value.strip().lower()

def sanitize_filename(name: str) -> str:
    return "".join(ch for ch in name if ch.isalnum() or ch in "-_.")
```

Often validate, normalize, then sanitize only where context requires it. Sometimes normalize first (trim/lowercase) before comparing to allowed values. Do not silently sanitize an invalid typo that should be rejected. A valid-looking string is not automatically safe in every context.

## 9. Boundary validation and validation categories

**Validate untrusted input once at the boundary**—CLI, environment, files, JSON, CSV, API body, or user prompt. Parse raw text, validate its type/meaning, normalize it, then pass a trusted internal representation to business logic.

```python
@dataclass(frozen=True)
class AppConfig:
    host: str
    port: int

def build_config(raw: dict) -> AppConfig:
    host = raw.get("host", "localhost")
    port_raw = raw.get("port", "8000")
    try:
        port = int(port_raw)
    except (TypeError, ValueError):
        raise ValueError(f"port must be an integer, got {port_raw!r}") from None
    if not 1 <= port <= 65535:
        raise ValueError(f"port must be between 1 and 65535, got {port}")
    return AppConfig(host, port)
```

Validation types: **type** (int not str), **presence** (database URL exists), **range** (port bounds), **length** (username length), **format** (version pattern), **enum/choice** (JSON/CSV), **cross-field** (end date after start), **uniqueness** (ID not duplicated), **path/file** (existing file), **extension** (`.csv`), and **encoding** (UTF-8 decodes).

## 10. String and numeric validation

```python
def validate_name(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("name must not be empty or whitespace-only")
    return value

def validate_username(value: str) -> str:
    value = value.strip()
    if not 3 <= len(value) <= 30:
        raise ValueError(f"username must be 3-30 characters, got {len(value)}")
    return value

def validate_identifier(value: str) -> str:
    if not all(ch.isalnum() or ch == "_" for ch in value):
        raise ValueError("identifier may only contain letters, digits, and underscores")
    return value
```

For allowed environments, normalize with `strip().lower()` then check membership in `{"development", "staging", "production"}`. Use regex only for genuine patterns such as version `X.Y.Z`:

```python
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
def validate_version(value: str) -> str:
    if not VERSION_PATTERN.match(value):
        raise ValueError(f"version must look like X.Y.Z, got {value!r}")
    return value
```

Use simple string methods or set membership when they are clearer than regex. Numeric bounds must specify inclusive/exclusive ends:

```python
def validate_port(value: int) -> int:
    if not 1 <= value <= 65535:
        raise ValueError(f"port must be between 1 and 65535, got {value}")
    return value

def validate_probability(value: float) -> float:
    if not 0.0 <= value < 1.0:
        raise ValueError(f"probability must be in [0.0, 1.0), got {value}")
    return value
```

`float("nan")` and `float("inf")` convert successfully but may be invalid business values. Use `math.isnan()`/`math.isinf()` to reject them where finite numbers are required.

## 11. Boolean configuration

`bool("false")` is `True`: any non-empty string is truthy. Parse conventional spellings explicitly:

```python
def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"expected a boolean value, got {value!r}")

def get_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return parse_bool(raw)
```

## 12. Path, file, JSON, and CSV validation

`Path.exists()`, `.is_file()`, `.is_dir()`, and `.suffix` check path shape. They do not guarantee a later open succeeds: permissions and filesystem changes can intervene.

```python
def validate_input_file(path: Path) -> Path:
    if not path.exists():
        raise ValueError(f"input file does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"input path is not a file: {path}")
    return path

def validate_output_path(path: Path, *, allow_overwrite: bool = False) -> Path:
    if path.exists() and not allow_overwrite:
        raise ValueError(f"output file already exists: {path}")
    if not path.parent.is_dir():
        raise ValueError(f"output directory does not exist: {path.parent}")
    return path

def validate_csv_path(path: Path) -> Path:
    if path.suffix.lower() != ".csv":
        raise ValueError(f"expected .csv, got {path.suffix or '(no extension)'}")
    return path

def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
```

Expect `FileNotFoundError`, `PermissionError`, and `IsADirectoryError` at actual file use. JSON syntax parsing is separate from shape validation:

```python
def parse_json_line(line: str) -> object:
    try:
        return json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc

def validate_record_shape(record: object) -> dict:
    if not isinstance(record, dict):
        raise ValueError(f"expected JSON object, got {type(record).__name__}")
    return record
```

Validate required fields and types. `bool` is a subclass of `int`, so explicitly reject it for numeric fields:

```python
REQUIRED_FIELDS = {"id": int, "name": str, "value": (int, float)}
def validate_record_fields(record: dict) -> dict:
    for field, expected in REQUIRED_FIELDS.items():
        if field not in record:
            raise ValueError(f"missing required field: {field!r}")
        if isinstance(record[field], bool) or not isinstance(record[field], expected):
            raise ValueError(f"field {field!r} has an invalid type")
    return record
```

JSON number `5` becomes `int`; `5.0` becomes `float`. Convert to float afterward if needed. Unknown fields may be rejected (strict schema) or ignored (forward compatibility), a deliberate choice.

CSV fields arrive as strings. `DictReader` fills missing cells in short rows with `None`:

```python
def validate_csv_row(row: dict, line_number: int) -> dict:
    if not row.get("id"):
        raise ValueError(f"line {line_number}: missing 'id'")
    raw = row.get("value")
    if raw is None:
        raise ValueError(f"line {line_number}: invalid or missing 'value'")
    try:
        row["value"] = float(raw)
    except ValueError:
        raise ValueError(f"line {line_number}: invalid or missing 'value'") from None
    return row
```

Use `csv.DictReader` with `path.open("r", newline="", encoding="utf-8")`; enumerate data rows from line 2 because line 1 is the header. This chapter deliberately uses transparent standard-library validation rather than a heavy schema framework.

## 13. Fail-fast, error collection, messages, and exceptions

Fail-fast stops at the first invalid critical input (configuration). Error collection processes independent records and gathers all problems (batch CSV):

```python
def validate_all_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    valid_rows, errors = [], []
    for line_number, row in enumerate(rows, start=2):
        try:
            valid_rows.append(validate_csv_row(row, line_number))
        except ValueError as exc:
            errors.append(str(exc))
    return valid_rows, errors
```

Good errors name the field, expectation, and (when safe) received value. Never include a secret in an error. CLI messages go to stderr; diagnostic detail belongs in logs. Lesson exit convention: `3` input/data issue, `4` configuration issue.

| Exception | Meaning |
|---|---|
| `ValueError` | Right general type, unacceptable value |
| `TypeError` | Wrong type for operation |
| `FileNotFoundError` | Missing path |
| `PermissionError` | No access |
| `KeyError` | Required key missing |
| `json.JSONDecodeError` | Malformed JSON |
| `argparse.ArgumentError` | argparse internal argument error; usually surfaced as `SystemExit` |

Raise specific errors in validators; catch them at a boundary where you can report/skip/exit. Avoid `except Exception:` and bare `except:` because they hide unexpected programming bugs.

## 14. Reusable validators and immutable configuration

A validator should have one responsibility, a predictable return type, and predictable exceptions:

```python
def parse_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise ValueError(f"port must be an integer, got {value!r}") from None
    if not 1 <= port <= 65535:
        raise ValueError(f"port must be between 1 and 65535, got {port}")
    return port
```

Reuse the same validator for CLI, environment, and config-file values. Group validated values in a dataclass:

```python
@dataclass(frozen=True)
class AppConfig:
    environment: str
    port: int
    debug: bool
```

`@dataclass` generates `__init__`, `__repr__`, and `__eq__`. `frozen=True` prevents field reassignment (`FrozenInstanceError`), but is shallow: a list/dict field can still be mutated. Build configuration once (`build_config()`), after parsing/validation/normalization, and pass the object to business logic. Do not read `os.environ` throughout the application.

## 15. Security and injection risks

- **Path traversal:** `../` or absolute paths can escape an allowed directory. Resolve and check containment:

```python
def validate_within_directory(path: Path, allowed_root: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(allowed_root.resolve()):
        raise ValueError(f"path escapes allowed directory: {path}")
    return resolved
```

`Path.is_relative_to()` requires Python 3.9+. Filesystem races/permissions can still affect later operations.
- **Shell injection:** never concatenate untrusted input into a command with `shell=True`. Use argument lists: `subprocess.run(["cat", filename])` (`shell=False` default).
- **SQL injection:** never interpolate input into query text; use parameterized queries such as `cursor.execute("SELECT ... WHERE name = %s", (name,))` (placeholder syntax depends on driver).
- Consider maliciously large fields, log injection (newlines/control characters), and unsafe deserialization. Lazy `%` logging formatting is not log-injection sanitization. Never load untrusted pickle data; JSON yields ordinary data structures rather than executing arbitrary Python code.

## 16. Safe logging

Log selected non-sensitive values:

```python
logger.info(
    "Configuration loaded: environment=%s port=%d debug=%s",
    config.environment, config.port, config.debug,
)
logger.debug("Input file: %s", config.input_file)
```

Never log the whole config object if it may contain a secret. Configuration errors happen at startup; runtime errors occur after logging is configured and should be handled through the logger. Keep stdout for actual machine-readable output and stderr/logging for diagnostics.

## 17. Testing

Test validators with valid, missing, malformed, wrong-type, and boundary values. Test paths and defaults. Use pytest `monkeypatch` to set/clear environment variables and restore them after each test; use `tmp_path` for temporary files and `parametrize` for variants:

```python
def test_port_valid():
    assert parse_port("8000") == 8000

def test_port_invalid():
    with pytest.raises(ValueError):
        parse_port("70000")

@pytest.mark.parametrize("raw,expected", [
    ("true", True), ("yes", True), ("1", True),
    ("false", False), ("no", False), ("0", False),
])
def test_bool(raw, expected):
    assert parse_bool(raw) is expected

def test_env(monkeypatch):
    monkeypatch.setenv("PORT", "9000")
    assert get_port() == 9000
```

Precedence tests must cover CLI wins, environment wins over default, and default applies when neither is supplied.

## 18. Common mistakes

Trusting environment values; forgetting string conversion; using `bool("false")`; hard-coding secrets or committing `.env`; validating too late/inconsistently; mixing config and business logic; broad exception catches; vague messages; dangerous defaults; reading environment variables in many modules; undocumented precedence; arbitrary paths; confusing sanitization with validation.

## 19. Twelve progressive coding examples

1. `os.getenv("APP_ENV")` reads a variable.
2. `os.getenv("APP_ENV", "development")` adds a string default.
3. `int(os.getenv("PORT", "8000"))` converts a string setting.
4. `parse_bool(os.getenv("DEBUG", "false"))` parses Boolean text.
5. Check required `DATABASE_URL`; print error to stderr and `SystemExit(4)` if absent.
6. `argparse` with `type=int`, `choices=range(1, 65536)`, and default 8000 validates a port.
7. Wrap input text in `Path` and validate existence/type.
8. Check required JSON/CSV record keys with a validator.
9. Put `parse_port`, `parse_bool`, and `validate_input_file` in a reusable `validators.py`.
10. Define frozen `AppConfig(environment, port, debug)`.
11. Resolve CLI value first, then environment, then default.
12. `build_config()` parses CLI, validates environment, resolves port, parses debug, and returns `AppConfig`.

## 20. Capstone: configurable CSV processing CLI

The lesson's `process_data.py` combines CLI path and `--port`, environment `APP_ENV`, `PORT`, `LOG_LEVEL`, validation, frozen config, row-level error collection, logging, JSON output, and exit statuses.

**Contract:** `0` all rows valid; `3` missing/not-file/unreadable input or invalid records; `4` invalid `APP_ENV`, `LOG_LEVEL`, or environment `PORT`; argparse usage error `2`. CLI `--port` overrides environment `PORT`, which overrides default 8000. Environments: development/staging/production. Log levels: DEBUG/INFO/WARNING/ERROR/CRITICAL. CSV header is expected to contain `id,value`; `id` must be nonempty and `value` numeric. File/config validation is fail-fast; rows are collected. Empty CSV is accepted as zero records. Missing columns cause rows to be rejected. Config-file loading is not implemented.

The program's stages are raw inputs → parse → validate → normalize → `AppConfig` → business logic → JSON stdout/log diagnostics. The complete core implementation:

```python
from __future__ import annotations
import argparse, csv, json, logging, os, sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

def parse_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise ValueError(f"port must be an integer, got {value!r}") from None
    if not 1 <= port <= 65535:
        raise ValueError(f"port must be between 1 and 65535, got {port}")
    return port

def validate_environment(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in {"development", "staging", "production"}:
        raise ValueError(f"unknown environment {value!r}")
    return normalized

class InputFileError(ValueError):
    """Input-file problem; exit status 3."""

def validate_input_file(path: Path) -> Path:
    if not path.exists():
        raise InputFileError(f"input file does not exist: {path}")
    if not path.is_file():
        raise InputFileError(f"input path is not a file: {path}")
    if path.suffix.lower() != ".csv":
        raise InputFileError(f"expected a .csv file: {path}")
    return path

def validate_row(row: dict, line_number: int) -> dict:
    if not row.get("id"):
        raise ValueError(f"line {line_number}: missing 'id'")
    raw = row.get("value")
    if raw is None:
        raise ValueError(f"line {line_number}: invalid or missing 'value'")
    try:
        row["value"] = float(raw)
    except ValueError:
        raise ValueError(f"line {line_number}: invalid or missing 'value'") from None
    return row

@dataclass(frozen=True)
class AppConfig:
    environment: str
    port: int
    log_level: str
    input_file: Path

def port_arg(value: str) -> int:
    try:
        return parse_port(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from None

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and summarize a CSV file.")
    parser.add_argument("input_file", type=Path)
    parser.add_argument("--port", type=port_arg, default=None)
    return parser

def build_config(argv: Sequence[str] | None = None) -> AppConfig:
    args = build_parser().parse_args(argv)
    environment = validate_environment(os.getenv("APP_ENV", "development"))
    port = args.port if args.port is not None else parse_port(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError(f"LOG_LEVEL must be a valid logging level, got {log_level!r}")
    return AppConfig(environment, port, log_level, validate_input_file(args.input_file))

def process_file(path: Path) -> dict:
    valid, errors = 0, []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            try:
                validate_row(row, line_number)
            except ValueError as exc:
                errors.append(str(exc))
                logger.warning("%s", exc)
                continue
            valid += 1
            logger.debug("Line %d valid: id=%s value=%s", line_number, row["id"], row["value"])
    logger.info("Processed %s: %d valid, %d invalid", path, valid, len(errors))
    return {"valid": valid, "invalid": len(errors), "errors": errors}

def main(argv: Sequence[str] | None = None) -> int:
    try:
        config = build_config(argv)
    except InputFileError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4
    logging.basicConfig(
        level=config.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("Starting: environment=%s port=%d", config.environment, config.port)
    try:
        summary = process_file(config.input_file)
    except (OSError, UnicodeDecodeError) as exc:
        logger.error("Could not read %s: %s", config.input_file, exc)
        return 3
    print(json.dumps(summary))
    return 0 if summary["invalid"] == 0 else 3

if __name__ == "__main__":
    raise SystemExit(main())
```

The source also demonstrates tests for valid port/Boolean/environment normalization; missing path; directory path; simulated permission error; invalid environment returning 4; short CSV row collected while processing continues; all-valid status 0; some-invalid status 3; CLI overriding environment; boundary ports 1 and 65535 accepted; invalid 0, -5, 65536, and text rejected by argparse with status 2. Improvements named by the source: structured JSON logs, maximum error-rate threshold, and external documented configuration schema.

---

# Part B — Project-tree review and current level

Stage 1 — Programming & Computational Thinking has **24 modules, 212 lessons, 282 files**, and four stage projects: Personal Expense Ledger CLI; Log Investigation and Reliability CLI; Data Quality and Transformation Pipeline; Rule-Based Risk Review Engine.

Module 05 contains nine lessons, in this order: text files; pathlib; CSV; JSON; encodings/newlines; argparse; standard streams/exit codes; logging; environment configuration/input validation. This is lesson 09, the next step after the first eight.

Your recorded level is **beginner progressing toward intermediate**. You have studied Python types/collections, control flow, loops, functions, arguments/defaults, scope, side effects, exceptions, and the first eight Module 05 lessons. Therefore the solutions use `os`, `Path`, CSV/JSON, `argparse`, logging, functions, exceptions, and the small pytest features introduced in this lesson. No pandas, NumPy, databases, cloud tools, or later advanced topics are required. Although the dedicated testing module comes later in the roadmap, this lesson itself introduces `pytest`, `monkeypatch`, `tmp_path`, `parametrize`, and `capsys`, so they are used only in that limited scope.

---

# Part C — All 13 exercises with solutions and line-by-line explanations

## Beginner

### 1. Read an environment variable with a default and print value/type

```python
import os
app_env = os.getenv("APP_ENV", "development")
print(app_env)
print(type(app_env))
```

`os` exposes the process environment. `getenv` reads `APP_ENV`; if absent, the string `"development"` is returned. `type` confirms the value is a `str`, not a typed environment value.

### 2. Read a required environment variable

```python
def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ValueError(f"{name} environment variable is required")
    return value
```

The argument makes the helper reusable. `getenv` returns `None` when missing; `strip()` also detects whitespace-only values. Invalid presence raises a clear `ValueError`; only valid text is returned.

### 3. `parse_int(value: str) -> int`

```python
def parse_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"value must be an integer, got {value!r}") from None
```

`int()` converts integer text. The `except` catches only conversion failure and raises a clearer message. `from None` suppresses the lower-level exception context in the displayed traceback.

### 4. Convert `"42"` and explain `"42.0"`

```python
number = int("42")  # 42
# int("42.0") raises ValueError: int() expects integer-form text,
# not decimal-form text; it does not truncate a decimal string.
```

`"42"` is integer-form text. `"42.0"` contains a decimal point; conversion through `float` is possible but truncates when converted to `int`.

## Intermediate

### 5. argparse custom type rejecting negative numbers

```python
def non_negative_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("value must be an integer") from None
    if number < 0:
        raise argparse.ArgumentTypeError("value must not be negative")
    return number

parser = argparse.ArgumentParser()
parser.add_argument("--retries", type=non_negative_int)
args = parser.parse_args()
```

Argparse passes raw text to the function. Convert it, translate malformed text into `ArgumentTypeError`, reject negatives, and return the validated integer. Argparse reports a usage error (status 2).

### 6. Output-path validator and tests

```python
def validate_output_path(path: Path, allow_overwrite: bool = False) -> Path:
    if path.exists() and not allow_overwrite:
        raise ValueError(f"output already exists: {path}")
    if not path.parent.is_dir():
        raise ValueError(f"output directory does not exist: {path.parent}")
    return path
```

```python
def test_existing_output_rejected(tmp_path):
    output = tmp_path / "result.csv"
    output.write_text("old", encoding="utf-8")
    with pytest.raises(ValueError, match="already exists"):
        validate_output_path(output)

def test_existing_output_allowed(tmp_path):
    output = tmp_path / "result.csv"
    output.write_text("old", encoding="utf-8")
    assert validate_output_path(output, allow_overwrite=True) == output
```

The first test proves the default prevents overwriting. The second proves the explicit flag permits it. The parent check rejects a missing output directory. This does not guarantee the process has write permission.

### 7. Three validators and at least two tests each

```python
def validate_code(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("code must not be empty")
    return value

def validate_currency(value: str) -> str:
    value = value.strip().upper()
    if value not in {"INR", "USD", "EUR"}:
        raise ValueError("currency must be INR, USD, or EUR")
    return value

def validate_quantity(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise ValueError("quantity must be an integer") from None
    if number <= 0:
        raise ValueError("quantity must be positive")
    return number
```

```python
def test_code_valid(): assert validate_code(" A12 ") == "A12"
def test_code_invalid():
    with pytest.raises(ValueError): validate_code(" ")

def test_currency_valid(): assert validate_currency("inr") == "INR"
def test_currency_invalid():
    with pytest.raises(ValueError): validate_currency("ABC")

def test_quantity_valid(): assert validate_quantity("5") == 5
def test_quantity_invalid():
    with pytest.raises(ValueError): validate_quantity("0")
```

Each validator performs one job, normalizes/converts its return value, and raises `ValueError` on failure. Each has a success and failure test.

### 8. CLI > environment > default

```python
def resolve_batch_size(cli_value: int | None) -> int:
    if cli_value is not None:
        return cli_value
    raw = os.getenv("BATCH_SIZE")
    if raw is not None:
        try:
            value = int(raw)
        except ValueError:
            raise ValueError(f"BATCH_SIZE must be an integer, got {raw!r}") from None
        if value < 1:
            raise ValueError("BATCH_SIZE must be at least 1")
        return value
    return 100
```

```python
def test_cli_wins(monkeypatch):
    monkeypatch.setenv("BATCH_SIZE", "200")
    assert resolve_batch_size(50) == 50

def test_env_wins(monkeypatch):
    monkeypatch.setenv("BATCH_SIZE", "200")
    assert resolve_batch_size(None) == 200

def test_default_wins_when_unset(monkeypatch):
    monkeypatch.delenv("BATCH_SIZE", raising=False)
    assert resolve_batch_size(None) == 100
```

The highest-priority source is checked first. `None` means the CLI value was omitted. Invalid supplied environment text raises; it is not replaced by the default.

### 9. Collect all missing JSON fields

```python
def missing_required_fields(record: dict, required: set[str]) -> list[str]:
    errors = []
    for field in sorted(required):
        if field not in record:
            errors.append(f"missing required field: {field}")
    return errors
```

The required set defines the schema. The loop checks every field, `sorted` makes order predictable, and the function returns all missing-field messages (or an empty list). This checks presence; type checks are separate.

## Advanced

### 10. Four-field frozen AppConfig

```python
@dataclass(frozen=True)
class AppConfig:
    environment: str
    port: int
    debug: bool
    input_file: Path

def build_config(input_name: str) -> AppConfig:
    environment = validate_environment(os.getenv("APP_ENV", "development"))
    port = parse_port(os.getenv("PORT", "8000"))
    debug = parse_bool(os.getenv("DEBUG", "false"))
    input_file = validate_input_file(Path(input_name))
    return AppConfig(environment, port, debug, input_file)
```

The dataclass groups four settings and prevents field reassignment. Each raw value passes through its validator. The object is created only after all fields pass. Business logic receives trusted values.

### 11. Fail-fast and collection for a list of numbers

```python
def validate_number(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise ValueError(f"not an integer: {value!r}") from None
    if number < 0:
        raise ValueError("number must be non-negative")
    return number

def validate_numbers_fail_fast(values: list[str]) -> list[int]:
    return [validate_number(value) for value in values]

def validate_numbers_collect(values: list[str]) -> tuple[list[int], list[str]]:
    valid, errors = [], []
    for value in values:
        try:
            valid.append(validate_number(value))
        except ValueError as exc:
            errors.append(str(exc))
    return valid, errors
```

Both strategies reuse one validator. Fail-fast is for critical all-or-nothing configuration. Collection is for independent batch items where partial success is useful.

### 12. Path confined to an allowed root

```python
def validate_within_root(path: Path, allowed_root: Path) -> Path:
    candidate = path.resolve()
    root = allowed_root.resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"path escapes allowed root: {path}")
    return candidate
```

```python
def test_safe_path(tmp_path):
    root = tmp_path / "uploads"
    root.mkdir()
    assert validate_within_root(root / "a.csv", root) == (root / "a.csv").resolve()

def test_unsafe_path(tmp_path):
    root = tmp_path / "uploads"
    root.mkdir()
    with pytest.raises(ValueError, match="escapes"):
        validate_within_root(root / ".." / "outside.csv", root)
```

`resolve()` canonicalizes both paths. `is_relative_to()` ensures the candidate is inside the root. The safe path passes; the `..` escape is rejected. Later I/O can still fail due to permissions or filesystem changes.

### 13. Complete config pipeline with a secret

```python
@dataclass(frozen=True)
class UploadConfig:
    environment: str
    port: int
    log_level: str
    api_key: str

def build_upload_config() -> UploadConfig:
    environment = validate_environment(os.getenv("APP_ENV", "development"))
    port = parse_port(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY is required")
    return UploadConfig(environment, port, log_level, api_key)

def log_config(config: UploadConfig) -> None:
    logger.info("Loaded environment=%s port=%d level=%s",
                config.environment, config.port, config.log_level)
```

The required key has no default. The other fields are parsed and validated. The frozen object centralizes the result. Logging explicitly omits `api_key`; never log the object as a whole or include the key in an error.

---

# Part D — Debugging lab: all 11 scenarios

1. **Missing `PORT`:** indexing raises `KeyError`; decide required vs optional and report clearly or provide a deliberate string default.
2. **Wrong environment type:** `getenv("TIMEOUT", 30)` returns int only when unset, string when set. Use a string default and convert (`int(os.getenv("TIMEOUT", "30"))`).
3. **`bool("false")`:** non-empty string is truthy; use `parse_bool`.
4. **Negative CLI port:** `type=int` checks syntax, not port semantics; add a range validator or `choices`.
5. **Wrong precedence:** code checks environment before CLI; check `args.port is not None` first, not truthiness.
6. **`Path(None)`:** missing env value returns `None`; check it or supply a string default before `Path`.
7. **Vague error:** replace `"bad config"` with field, expectation, and safe actual value.
8. **Config read in multiple places:** centralize reads in `build_config()` and pass `AppConfig`.
9. **Secret logged:** do not log full dataclass; select safe fields or mask secret representation.
10. **Overbroad catch:** `except Exception: return 8000` hides invalid input; catch `ValueError` and raise a useful error.
11. **Boundary rejected:** `<` excludes endpoints; align `<`/`<=` with the specification (e.g. `0.0 <= x <= 1.0` if both endpoints are valid).

---

# Part E — Interview and architecture questions: all 28 answers

1. Configuration controls behavior; code implements logic.
2. Environment variable is a process-level string pair; child normally inherits parent's environment copy.
3. `os.environ[]` raises `KeyError`; `getenv()` returns `None` or default.
4. OS environment stores text; convert and validate explicitly.
5. Repository history can retain a secret; repository readers may access it.
6. `.env` is a text file and is not auto-loaded; a tool/custom code must load it.
7. It may contain secrets; ignore it and commit placeholder `.env.example`.
8. CLI > environment > config file > built-in defaults: more specific invocation wins.
9. Parsing converts raw text; validation checks acceptability.
10. Validation accepts/rejects; normalization canonicalizes; sanitization transforms/removes unwanted content.
11. Boundary validation checks data at entry, allowing internal functions to trust it.
12. Examples: presence (DB URL set), range (port bounds), length (username), enum (JSON/CSV), path (file exists); also type, format, cross-field, uniqueness, extension, encoding.
13. `argparse type=` calls a converter/validator; raise `ArgumentTypeError` for unacceptable input.
14. `bool("false")` is `True` because every non-empty string is truthy.
15. Check `is_file()` and `suffix.lower() == ".csv"`; raise a clear error otherwise.
16. Fail-fast for critical config; error collection for independent batch rows.
17. Field + expected rule + actual safe value lets the user fix it.
18. Echoing a secret leaks the sensitive value into an error channel.
19. `ValueError`: wrong value; `TypeError`: wrong type; `FileNotFoundError`: missing path. Also `PermissionError`, `KeyError`, `JSONDecodeError`.
20. `except Exception` catches programming bugs as well as anticipated validation errors.
21. Positive-int validator returns `int`; raises `ValueError` for malformed/non-positive values with clear text.
22. One config object avoids long parameter lists and inconsistent defaults/validation.
23. `frozen=True` prevents accidental mutation after validation.
24. Path traversal uses `../` to escape a directory; resolve and check `is_relative_to(allowed_root)`.
25. Concatenation can turn input into command/query syntax; use argument lists or parameterized queries.
26. Log only selected known-safe config fields.
27. Use `monkeypatch.setenv`/`delenv`, explicit argv, and assert the winning source.
28. Require `DATABASE_URL` and `API_KEY`; default/validate `LOG_LEVEL`; build one frozen config; never log or echo API key.

---

# Part F — Knowledge check: all 9 answers

1. Environment values are strings because the OS environment stores text only; Python must convert them.
2. Boundary validation creates one trusted representation and prevents inconsistent repeated checks.
3. `getenv("TIMEOUT", 30)` has inconsistent types: int default vs str when set. Use `"30"` and convert.
4. It prints `True`: `"false"` is a non-empty string.
5. Add semantic output-path validation for parent directory and intended writability/permissions; handle actual write errors at I/O.
6. A helper probably reads its own default/source instead of receiving central `AppConfig`.
7. Use error collection to process all independent rows and report every invalid row.
8. Full config logging may expose secrets; log only selected non-sensitive fields.
9. Validate input file; resolve destination and check it is relative to allowed root; store validated input/root/destination paths in `AppConfig`; upload only after building config.

---

# Part G — Production checklist

- [ ] Treat CLI, environment, files, JSON, CSV, and user input as untrusted.
- [ ] Validate once at the boundary.
- [ ] Document and centralize precedence.
- [ ] Use safe defaults; fail fast for required settings.
- [ ] Never hard-code, commit, log, or echo secrets.
- [ ] Ignore `.env`; commit placeholder `.env.example`.
- [ ] Convert all environment/CLI values explicitly; parse booleans with `parse_bool`.
- [ ] Build one frozen, validated config object and pass it explicitly.
- [ ] Use actionable errors and catch specific exceptions.
- [ ] Validate paths and constrain untrusted paths to allowed roots when required.
- [ ] Log only safe fields; lazy formatting is not log-injection sanitization.
- [ ] Test valid, missing, malformed, boundary, type, path, default, and precedence cases.
- [ ] Use distinct documented exit codes for configuration and input/data errors.

**Learning checkpoint:** You should now be able to parse, validate, and normalize external inputs; build a trusted immutable configuration object; fail fast on invalid configuration; collect independent record errors; and log safely without exposing secrets.

**Roadmap position:** Stage 1 → Module 05 → Lesson 09 completed. The next roadmap item is Module 05 README/practice material; do not advance until you request it.
