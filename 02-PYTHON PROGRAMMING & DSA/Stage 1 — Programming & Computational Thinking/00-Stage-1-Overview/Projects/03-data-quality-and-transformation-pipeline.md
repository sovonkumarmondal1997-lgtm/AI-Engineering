# Project 03 — Data Quality & Transformation Pipeline

**Stage:** Stage 1 — Programming & Computational Thinking  
**Estimated effort:** 20–30 hours  
**Runtime:** Python 3.12+  
**Runtime dependencies:** Python standard library only  
**Development tools:** `uv`, `pytest`, `ruff`, `mypy`

## 1. Source alignment and purpose

The Stage 1 `learning-plan.md` defines this project as a batch pipeline over a messy customer-orders CSV. It must produce a clean dataset, a reject file that explains row-level problems, and a JSON quality report. The required concepts are validation rules, pure functions, reject files, quality reports, idempotency, and hashing. The plan estimates 20–30 hours and explicitly makes the four Stage 1 projects cumulative.

The roadmap tree places this project at:

```text
Stage 1 — Programming & Computational Thinking/
└── 00-Stage-1-Overview/
    └── Projects/
        └── 03-data-quality-and-transformation-pipeline.md
```

Reuse the Stage 1 conventions: `uv`, `src/` package layout, typed Python, `argparse`, pytest, Ruff, mypy, deterministic behavior, and atomic writes. Do not introduce pandas, databases, orchestration frameworks, distributed compute, or ML into the core project.

## 2. Project outcome

Build a command-line application called `dqpipe` that:

1. Reads CSV safely, including UTF-8 BOM and quoted fields.
2. Fails clearly on a schema/header contract error.
3. Validates every field and collects multiple violations per row.
4. Normalises only documented values.
5. Deduplicates valid rows according to an explicit policy.
6. Derives `order_total` and `order_month` only after validation.
7. Writes `clean_orders.csv`, `rejects.csv`, and `quality_report.json`.
8. Records SHA-256 of the original input bytes.
9. Applies a configurable reject-rate threshold and supports `--dry-run`.
10. Produces deterministic, byte-identical output on reruns.

## 3. Define the data contract before coding

| Field | Validation | Canonical value |
|---|---|---|
| `order_id` | required; unique among valid rows | trimmed, case-sensitive text |
| `customer_email` | required; basic email shape | trimmed lowercase |
| `order_date` | real canonical `YYYY-MM-DD` date | `date` |
| `country` | key exists in configured mapping | uppercase two-letter code |
| `quantity` | integer greater than zero; reject `2.0` | `int` |
| `unit_price` | finite decimal, non-negative, at most 2 fractional digits | `Decimal` with two places |
| `status` | `new`, `paid`, `shipped`, or `cancelled` | lowercase |

Derived fields are `order_total = quantity × unit_price` and `order_month = YYYY-MM`.

Policy decisions to document and test:

- Collect every field-level violation in a row.
- Missing, duplicate, or unexpected header columns fail the batch.
- Wrong-width CSV records are row-level rejects.
- First *valid* occurrence of a normalized `order_id` wins; invalid rows do not reserve keys.
- `A1` and `a1` are distinct IDs.
- Reject rate is rejected rows / all data rows, not violation count / rows.
- Header-only input is a valid empty batch with reject rate `0.0`.
- `10.999` is rejected rather than silently rounded; `-0` becomes `0.00`.
- SHA-256 covers the original input bytes, including any BOM.
- Do not put timestamps or random IDs in deterministic output files.

## 4. Architecture

```text
orders.csv
   ↓
extract() → validate_row() → dedupe() → transform()
   ↓                    ↓
clean_orders.csv     rejects.csv
                       ↓
                 quality_report.json
```

Responsibilities:

- `rules.py`: pure field validation and typed `RuleError`; no I/O.
- `config.py`: TOML loading and validation.
- `pipeline.py`: extraction, row validation, dedupe, transformation, hashing, output serialization.
- `cli.py`: arguments, orchestration, stderr diagnostics, exit codes.
- `data-contract.md`: field definitions and policy.
- `learning-notes.md`: three actual mistakes, causes, fixes, and regression tests.

## 5. Required project tree

```text
data-quality-and-transformation-pipeline/
├── .gitignore
├── README.md
├── pyproject.toml
├── uv.lock
├── config.toml
├── data/
│   └── orders.csv
├── data-contract.md
├── learning-notes.md
├── src/dqpipe/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── pipeline.py
│   └── rules.py
└── tests/
    ├── test_cli.py
    ├── test_pipeline.py
    └── test_rules.py
```

## 6. Build milestones (20–30 hours)

| Milestone | Time | Deliverable | Exit gate |
|---|---:|---|---|
| M1 — Contract | 2–3 h | schema, normalization, duplicate/reject policies | unambiguous to another engineer |
| M2 — Rules | 3–4 h | pure validators and parameterized tests | valid, invalid, empty, whitespace, and boundary cases covered |
| M3 — Row pipeline | 3–4 h | extraction, schema checks, multi-violation validation | one row reports all its faults |
| M4 — Dedupe + outputs | 3–4 h | duplicate policy and three output files | output contracts pass |
| M5 — Reproducibility | 2–3 h | SHA-256 and repeat-run tests | byte-identical rerun |
| M6 — CLI + config | 3–4 h | TOML, threshold, dry-run, exit codes | CLI tests pass |
| M7 — Scale + docs | 4–6 h | 200k-row experiment, README, audit | acceptance checklist passes |

## 7. Setup

Use Python 3.12+ and `uv`. If the package already exists, do not initialize it twice.

```bash
uv init --package dqpipe
uv add --dev pytest ruff mypy
uv lock
uv sync
```

Add the files below, then run:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src
uv run dqpipe run --input data/orders.csv --out-dir out --config config.toml
```

Commit `uv.lock`. Verify a clean setup with `uv sync --locked` and a runtime-only install with `uv sync --locked --no-dev`.

## 8. Reference implementation

Copy each file to the exact path shown. Build in order: configuration and rules, pipeline, CLI, tests, documentation. The complete companion project directory is also provided alongside this Markdown guide.


### `pyproject.toml`

```toml
[project]
name = "dqpipe"
version = "0.1.0"
description = "A deterministic CSV data-quality and transformation pipeline"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
dqpipe = "dqpipe.cli:main"

[dependency-groups]
dev = ["pytest>=8.0", "ruff>=0.6", "mypy>=1.11"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/dqpipe"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.12"
strict = true
mypy_path = "src"
```


### `.gitignore`

```text
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
*.egg-info/
out/
*.tmp
```


### `config.toml`

```toml
[pipeline]
max_reject_rate = 0.40

[countries]
usa = "US"
"united states" = "US"
us = "US"
uk = "GB"
gb = "GB"
india = "IN"
in = "IN"
```


### `src/dqpipe/__init__.py`

```python
"""Data quality and transformation pipeline."""

__version__ = "0.1.0"
```


### `src/dqpipe/rules.py`

```python
"""Pure field-level validation and normalisation rules."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
from typing import TypeVar

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CENT = Decimal("0.01")
T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Violation:
    field: str
    rule: str
    message: str


class RuleError(ValueError):
    """A validation failure with a stable machine-readable rule identifier."""

    def __init__(self, rule: str, message: str) -> None:
        super().__init__(message)
        self.rule = rule


def required(value: str | None) -> str:
    if value is None or not value.strip():
        raise RuleError("required", "value is missing")
    return value.strip()


def email(value: str | None) -> str:
    normalised = required(value).lower()
    if not EMAIL_RE.fullmatch(normalised):
        raise RuleError("email_format", "expected a basic name@domain.tld email shape")
    return normalised


def iso_date(value: str | None) -> date:
    text = required(value)
    try:
        parsed = date.fromisoformat(text)
    except ValueError:
        raise RuleError("date_format", "expected a real date in YYYY-MM-DD format") from None
    if parsed.isoformat() != text:
        raise RuleError("date_format", "expected canonical YYYY-MM-DD format")
    return parsed


def positive_int(value: str | None) -> int:
    text = required(value)
    if not re.fullmatch(r"[+-]?\d+", text):
        raise RuleError("int_format", "expected an integer written without a decimal point")
    try:
        number = int(text)
    except ValueError:
        raise RuleError("int_format", "expected an integer") from None
    if number <= 0:
        raise RuleError("range", "quantity must be greater than zero")
    return number


def price(value: str | None) -> Decimal:
    text = required(value)
    try:
        amount = Decimal(text)
    except (InvalidOperation, ValueError):
        raise RuleError("decimal_format", "expected a decimal amount") from None
    if not amount.is_finite():
        raise RuleError("range", "unit_price must be finite")
    if amount < 0:
        raise RuleError("range", "unit_price must be greater than or equal to zero")
    with localcontext() as context:
        context.prec = max(28, len(amount.as_tuple().digits) + abs(amount.as_tuple().exponent) + 4)
        rounded = amount.quantize(CENT)
    if amount != rounded:
        raise RuleError("scale", "unit_price must have no more than two fractional digits")
    # Canonicalise negative zero to positive zero and ensure two decimal places.
    return Decimal("0.00") if amount == 0 else rounded


def country(value: str | None, mapping: dict[str, str]) -> str:
    key = required(value).casefold()
    if key not in mapping:
        raise RuleError("country_unknown", "country is not present in the configured mapping")
    return mapping[key]


VALID_STATUS = frozenset({"new", "paid", "shipped", "cancelled"})


def status(value: str | None) -> str:
    normalised = required(value).lower()
    if normalised not in VALID_STATUS:
        raise RuleError("status_domain", "status must be new, paid, shipped, or cancelled")
    return normalised
```


### `src/dqpipe/config.py`

```python
"""Configuration loading and validation."""

from __future__ import annotations

import math
import tomllib
from pathlib import Path
from typing import Any


DEFAULT_COUNTRIES = {
    "usa": "US",
    "united states": "US",
    "us": "US",
    "uk": "GB",
    "gb": "GB",
    "india": "IN",
    "in": "IN",
}
DEFAULT_MAX_REJECT_RATE = 0.20


def load_config(path: Path | None) -> tuple[float, dict[str, str]]:
    """Load TOML configuration, or return documented defaults when no file is given."""
    if path is None:
        return DEFAULT_MAX_REJECT_RATE, dict(DEFAULT_COUNTRIES)

    try:
        with path.open("rb") as handle:
            raw: dict[str, Any] = tomllib.load(handle)
    except OSError as exc:
        raise ValueError(f"cannot read config {path}: {exc}") from None
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"invalid TOML config {path}: {exc}") from None

    pipeline = raw.get("pipeline", {})
    if not isinstance(pipeline, dict):
        raise ValueError("config [pipeline] must be a TOML table")
    threshold = pipeline.get("max_reject_rate", DEFAULT_MAX_REJECT_RATE)
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise ValueError("pipeline.max_reject_rate must be a number between 0 and 1")
    threshold = float(threshold)
    if not math.isfinite(threshold) or not 0.0 <= threshold <= 1.0:
        raise ValueError("pipeline.max_reject_rate must be a finite number between 0 and 1")

    raw_countries = raw.get("countries", DEFAULT_COUNTRIES)
    if not isinstance(raw_countries, dict) or not raw_countries:
        raise ValueError("config [countries] must be a non-empty TOML table")
    countries: dict[str, str] = {}
    for key, code in raw_countries.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("country mapping keys must be non-empty strings")
        if not isinstance(code, str) or len(code) != 2 or not code.isalpha():
            raise ValueError(f"country mapping for {key!r} must be a two-letter code")
        countries[key.strip().casefold()] = code.upper()
    return threshold, countries
```


### `src/dqpipe/pipeline.py`

```python
"""CSV extraction, validation, deduplication, transformation, and atomic outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from . import rules
from .rules import RuleError, Violation

INPUT_COLUMNS = (
    "order_id",
    "customer_email",
    "order_date",
    "country",
    "quantity",
    "unit_price",
    "status",
)
OUTPUT_COLUMNS = (*INPUT_COLUMNS, "order_total", "order_month")
REJECT_COLUMNS = ("record_number", "field", "rule", "message", "raw_row_json")


@dataclass(slots=True)
class RowOutcome:
    record_number: int
    raw: dict[str, str]
    clean: dict[str, Any] | None = None
    violations: list[Violation] = field(default_factory=list)


def extract(path: Path) -> Iterator[tuple[int, dict[str, str]]]:
    """Yield logical CSV record numbers and raw rows; accept UTF-8 BOMs."""
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, strict=True)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise ValueError("input CSV is empty and has no header")
        if len(fieldnames) != len(set(fieldnames)):
            raise ValueError("input CSV has duplicate column names")
        missing = sorted(set(INPUT_COLUMNS) - set(fieldnames))
        extra = sorted(set(fieldnames) - set(INPUT_COLUMNS))
        if missing:
            raise ValueError(f"input is missing required columns: {', '.join(missing)}")
        if extra:
            raise ValueError(f"input has unexpected columns: {', '.join(extra)}")

        for record_number, row in enumerate(reader, start=2):
            # DictReader uses key None when a record has extra values and value None
            # when a record has too few values. Preserve both as a row-level reject.
            if None in row or any(value is None for value in row.values()):
                raw = {key: "" if value is None else str(value) for key, value in row.items()
                       if key is not None}
                raw["__csv_shape_error__"] = "row has a different number of fields than header"
                yield record_number, raw
                continue
            yield record_number, {key: str(value) for key, value in row.items() if key is not None}


def validate_row(
    record_number: int,
    raw: dict[str, str],
    countries: dict[str, str],
) -> RowOutcome:
    outcome = RowOutcome(record_number=record_number, raw=raw)
    if "__csv_shape_error__" in raw:
        outcome.violations.append(
            Violation("_row", "csv_shape", raw["__csv_shape_error__"])
        )
        return outcome

    clean: dict[str, Any] = {}
    validators = {
        "order_id": rules.required,
        "customer_email": rules.email,
        "order_date": rules.iso_date,
        "country": lambda value: rules.country(value, countries),
        "quantity": rules.positive_int,
        "unit_price": rules.price,
        "status": rules.status,
    }
    for field_name in INPUT_COLUMNS:
        try:
            clean[field_name] = validators[field_name](raw.get(field_name))
        except RuleError as exc:
            outcome.violations.append(Violation(field_name, exc.rule, str(exc)))

    # Example cross-field business rule. Keep it explicit and explainable.
    if not outcome.violations and clean["status"] == "cancelled":
        # A cancelled order is valid regardless of its date/amount; this rule is
        # intentionally not conflated with status-domain validation.
        pass

    if not outcome.violations:
        outcome.clean = clean
    return outcome


def dedupe(outcomes: list[RowOutcome]) -> None:
    """Keep the first valid row for each normalised order_id; invalid rows do not reserve keys."""
    seen: set[str] = set()
    for outcome in outcomes:
        if outcome.clean is None:
            continue
        order_id = outcome.clean["order_id"]
        if order_id in seen:
            outcome.violations.append(
                Violation("order_id", "duplicate_key", f"duplicate order_id {order_id!r}")
            )
            outcome.clean = None
        else:
            seen.add(order_id)


def transform(clean: dict[str, Any]) -> dict[str, Any]:
    """Derive columns only from a validated row."""
    result = dict(clean)
    result["order_total"] = (clean["unit_price"] * clean["quantity"]).quantize(Decimal("0.01"))
    result["order_month"] = clean["order_date"].strftime("%Y-%m")
    return result


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv_value(value: Any) -> str | int:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, ".2f")
    return value


def _atomic_write_csv(path: Path, header: tuple[str, ...], rows: Iterable[Iterable[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", newline="", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            temporary = handle.name
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(header)
            for row in rows:
                writer.writerow([_csv_value(value) for value in row])
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            temporary = handle.name
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def run_pipeline(
    input_path: Path,
    out_dir: Path,
    countries: dict[str, str],
) -> tuple[dict[str, Any], list[RowOutcome], list[dict[str, Any]]]:
    """Run the deterministic batch pipeline and return report, outcomes, and clean rows."""
    outcomes = [validate_row(number, raw, countries) for number, raw in extract(input_path)]
    dedupe(outcomes)
    clean_rows = [transform(row.clean) for row in outcomes if row.clean is not None]
    rejected = [row for row in outcomes if row.clean is None]
    violation_counts = Counter(
        violation.rule for row in rejected for violation in row.violations
    )
    examples: dict[str, list[dict[str, Any]]] = {}
    for row in rejected:
        for violation in row.violations:
            bucket = examples.setdefault(violation.rule, [])
            if len(bucket) < 5:
                bucket.append({
                    "record_number": row.record_number,
                    "field": violation.field,
                    "message": violation.message,
                })

    totals = [row["order_total"] for row in clean_rows]
    report: dict[str, Any] = {
        "input_sha256": sha256_of(input_path),
        "rows_read": len(outcomes),
        "rows_clean": len(clean_rows),
        "rows_rejected": len(rejected),
        "reject_rate": round(len(rejected) / len(outcomes), 6) if outcomes else 0.0,
        "violations_by_rule": dict(sorted(violation_counts.items())),
        "examples_by_rule": {key: examples[key] for key in sorted(examples)},
        "order_total_summary": {
            "count": len(totals),
            "sum": format(sum(totals, Decimal("0.00")), ".2f"),
            "min": format(min(totals), ".2f") if totals else None,
            "max": format(max(totals), ".2f") if totals else None,
        },
    }
    return report, outcomes, clean_rows


def write_outputs(out_dir: Path, report: dict[str, Any], outcomes: list[RowOutcome],
                  clean_rows: list[dict[str, Any]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write_csv(
        out_dir / "clean_orders.csv",
        OUTPUT_COLUMNS,
        ([row[column] for column in OUTPUT_COLUMNS] for row in clean_rows),
    )
    _atomic_write_csv(
        out_dir / "rejects.csv",
        REJECT_COLUMNS,
        (
            (
                row.record_number,
                violation.field,
                violation.rule,
                violation.message,
                json.dumps(row.raw, sort_keys=True, ensure_ascii=False),
            )
            for row in outcomes if row.clean is None
            for violation in row.violations
        ),
    )
    _atomic_write_text(
        out_dir / "quality_report.json",
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
    )
```


### `src/dqpipe/cli.py`

```python
"""Command-line interface for dqpipe."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .config import load_config
from .pipeline import run_pipeline, write_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dqpipe",
        description="Validate, normalise, deduplicate, and audit an orders CSV.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="run the batch quality pipeline")
    run.add_argument("--input", required=True, type=Path)
    run.add_argument("--out-dir", type=Path, default=Path("out"))
    run.add_argument("--config", type=Path, default=None)
    run.add_argument("--max-reject-rate", type=float, default=None)
    run.add_argument("--dry-run", action="store_true", help="validate and report without writing outputs")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "run":
        parser.error("unsupported command")

    input_path: Path = args.input
    out_dir: Path = args.out_dir
    try:
        if not input_path.is_file():
            raise ValueError(f"input file does not exist or is not a file: {input_path}")
        threshold_from_config, countries = load_config(args.config)
        threshold = threshold_from_config if args.max_reject_rate is None else args.max_reject_rate
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("--max-reject-rate must be between 0 and 1")
        if not __import__("math").isfinite(threshold):
            raise ValueError("--max-reject-rate must be finite")
        report, outcomes, clean_rows = run_pipeline(input_path, out_dir, countries)
        if not args.dry_run:
            output_paths = {
                (out_dir / "clean_orders.csv").resolve(),
                (out_dir / "rejects.csv").resolve(),
                (out_dir / "quality_report.json").resolve(),
            }
            if input_path.resolve() in output_paths:
                raise ValueError("input file must not be one of the pipeline output files")
            write_outputs(out_dir, report, outcomes, clean_rows)
        print(json.dumps(report, indent=2, sort_keys=True))
        if report["reject_rate"] > threshold:
            print(
                f"dqpipe: reject rate {report['reject_rate']:.2%} exceeds threshold "
                f"{threshold:.2%}",
                file=sys.stderr,
            )
            return 1
        return 0
    except (OSError, ValueError, csv.Error) as exc:
        print(f"dqpipe: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```


### `tests/test_rules.py`

```python
from datetime import date
from decimal import Decimal

import pytest

from dqpipe import rules


@pytest.mark.parametrize(("raw", "expected"), [
    (" Ann@Example.COM ", "ann@example.com"),
    ("a+b@example.co.in", "a+b@example.co.in"),
])
def test_email_normalises(raw: str, expected: str) -> None:
    assert rules.email(raw) == expected


@pytest.mark.parametrize("raw", ["", "  ", "no-at-sign", "a@b", "a b@example.com"])
def test_email_rejects_invalid(raw: str) -> None:
    with pytest.raises(rules.RuleError):
        rules.email(raw)


@pytest.mark.parametrize(("raw", "expected"), [
    ("2026-02-28", date(2026, 2, 28)),
    ("2024-02-29", date(2024, 2, 29)),
])
def test_iso_date_valid(raw: str, expected: date) -> None:
    assert rules.iso_date(raw) == expected


@pytest.mark.parametrize("raw", ["2026-02-30", "2026-13-01", "2026-2-01", ""])
def test_iso_date_invalid(raw: str) -> None:
    with pytest.raises(rules.RuleError):
        rules.iso_date(raw)


@pytest.mark.parametrize(("raw", "expected"), [("1", 1), ("+3", 3)])
def test_quantity_valid(raw: str, expected: int) -> None:
    assert rules.positive_int(raw) == expected


@pytest.mark.parametrize("raw", ["0", "-1", "2.0", "1.5", "abc", ""])
def test_quantity_invalid(raw: str) -> None:
    with pytest.raises(rules.RuleError):
        rules.positive_int(raw)


@pytest.mark.parametrize(("raw", "expected"), [
    ("10", Decimal("10.00")),
    ("10.50", Decimal("10.50")),
    ("0", Decimal("0.00")),
    ("-0", Decimal("0.00")),
    ("1e3", Decimal("1000.00")),
])
def test_price_valid(raw: str, expected: Decimal) -> None:
    assert rules.price(raw) == expected


@pytest.mark.parametrize("raw", ["NaN", "Infinity", "-1", "10.999", "bad", ""])
def test_price_invalid(raw: str) -> None:
    with pytest.raises(rules.RuleError):
        rules.price(raw)


def test_country_and_status() -> None:
    mapping = {"usa": "US", "india": "IN"}
    assert rules.country(" USA ", mapping) == "US"
    assert rules.status("PAID") == "paid"
    with pytest.raises(rules.RuleError):
        rules.country("Mars", mapping)
    with pytest.raises(rules.RuleError):
        rules.status("lost")
```


### `tests/test_pipeline.py`

```python
import csv
import hashlib
import json
from pathlib import Path

import pytest

from dqpipe.config import load_config
from dqpipe.pipeline import run_pipeline, write_outputs

HEADER = "order_id,customer_email,order_date,country,quantity,unit_price,status\n"
GOOD = "A1,Ann@Example.com,2026-02-01,usa,2,10.50,PAID\n"
COUNTRIES = {"usa": "US", "us": "US", "uk": "GB", "india": "IN"}


def write_csv(path: Path, content: str, *, bom: bool = False) -> None:
    encoding = "utf-8-sig" if bom else "utf-8"
    path.write_text(content, encoding=encoding, newline="")


def test_end_to_end_outputs_and_idempotency(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    write_csv(source, HEADER + GOOD + "A2,bad-email,2026-02-02,UK,1,5,new\n")
    out = tmp_path / "out"
    report, outcomes, clean = run_pipeline(source, out, COUNTRIES)
    assert (report["rows_read"], report["rows_clean"], report["rows_rejected"]) == (2, 1, 1)
    assert report["input_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    write_outputs(out, report, outcomes, clean)
    first = {p.name: p.read_bytes() for p in out.iterdir()}
    report2, outcomes2, clean2 = run_pipeline(source, out, COUNTRIES)
    write_outputs(out, report2, outcomes2, clean2)
    assert {p.name: p.read_bytes() for p in out.iterdir()} == first
    with (out / "clean_orders.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["customer_email"] == "ann@example.com"
    assert rows[0]["order_total"] == "21.00"
    assert rows[0]["order_month"] == "2026-02"
    report_json = json.loads((out / "quality_report.json").read_text(encoding="utf-8"))
    assert report_json["order_total_summary"]["sum"] == "21.00"


def test_bom_and_quoted_comma_are_supported(tmp_path: Path) -> None:
    source = tmp_path / "bom.csv"
    write_csv(source, HEADER + 'A1,"ann,ops@example.com",2026-02-01,usa,1,1.00,new\n', bom=True)
    report, _, clean = run_pipeline(source, tmp_path / "out", COUNTRIES)
    assert report["rows_clean"] == 1
    assert clean[0]["customer_email"] == "ann,ops@example.com"


def test_multiple_violations_and_duplicate_policy(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    content = HEADER + (
        "A1,bad,2026-02-30,Mars,0,NaN,lost\n"
        + GOOD
        + " A1 ,ann@example.com,2026-02-01,US,1,1.00,new\n"
    )
    write_csv(source, content)
    report, outcomes, clean = run_pipeline(source, tmp_path / "out", COUNTRIES)
    assert report["rows_read"] == 3
    assert report["rows_clean"] == 1
    assert report["rows_rejected"] == 2
    assert len(outcomes[0].violations) >= 5
    # Invalid first row does not reserve A1; first valid A1 survives, later valid A1 is duplicate.
    assert report["violations_by_rule"]["duplicate_key"] == 1
    assert clean[0]["order_id"] == "A1"


def test_missing_and_extra_columns_fail_fast(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    write_csv(source, "order_id,customer_email\nA1,a@example.com\n")
    with pytest.raises(ValueError, match="missing required columns"):
        run_pipeline(source, tmp_path / "out", COUNTRIES)
    write_csv(source, HEADER.rstrip("\n") + ",extra\n" + GOOD.rstrip("\n") + ",x\n")
    with pytest.raises(ValueError, match="unexpected columns"):
        run_pipeline(source, tmp_path / "out", COUNTRIES)


def test_header_only_file_is_valid_empty_batch(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    write_csv(source, HEADER)
    report, outcomes, clean = run_pipeline(source, tmp_path / "out", COUNTRIES)
    assert report["rows_read"] == report["rows_clean"] == report["rows_rejected"] == 0
    assert report["reject_rate"] == 0.0
    assert outcomes == []
    assert clean == []


def test_too_few_fields_are_rejected_not_crashed(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    write_csv(source, HEADER + "A1,ann@example.com\n")
    report, outcomes, _ = run_pipeline(source, tmp_path / "out", COUNTRIES)
    assert report["rows_rejected"] == 1
    assert outcomes[0].violations[0].rule == "csv_shape"


def test_embedded_newline_in_quoted_field(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    write_csv(source, HEADER + 'A1,"ann\n@example.com",2026-02-01,usa,1,1.00,new\n')
    report, _, _ = run_pipeline(source, tmp_path / "out", COUNTRIES)
    assert report["rows_rejected"] == 1


def test_config_validation(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    config.write_text('[pipeline]\nmax_reject_rate = 1.5\n', encoding="utf-8")
    with pytest.raises(ValueError, match="between 0 and 1"):
        load_config(config)
```


### `tests/test_cli.py`

```python
import json
from pathlib import Path

from dqpipe.cli import main

HEADER = "order_id,customer_email,order_date,country,quantity,unit_price,status\n"
GOOD = "A1,ann@example.com,2026-02-01,usa,1,1.00,new\n"


def test_cli_success_and_threshold_failure(tmp_path: Path, capsys) -> None:
    source = tmp_path / "orders.csv"
    source.write_text(HEADER + GOOD + "A2,bad,2026-02-30,usa,1,1.00,new\n", encoding="utf-8")
    out = tmp_path / "out"
    assert main(["run", "--input", str(source), "--out-dir", str(out),
                 "--max-reject-rate", "0.5"]) == 0
    stdout = capsys.readouterr().out
    assert json.loads(stdout)["rows_rejected"] == 1
    assert main(["run", "--input", str(source), "--out-dir", str(out),
                 "--max-reject-rate", "0.1"]) == 1
    captured = capsys.readouterr()
    assert "exceeds threshold" in captured.err
    assert (out / "quality_report.json").exists()


def test_dry_run_does_not_write_outputs(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    source.write_text(HEADER + GOOD, encoding="utf-8")
    out = tmp_path / "out"
    assert main(["run", "--input", str(source), "--out-dir", str(out), "--dry-run"]) == 0
    assert not out.exists()


def test_missing_input_is_clear_error(tmp_path: Path, capsys) -> None:
    result = main(["run", "--input", str(tmp_path / "missing.csv")])
    assert result == 1
    assert "does not exist" in capsys.readouterr().err
```


### `data/orders.csv`

```csv
order_id,customer_email,order_date,country,quantity,unit_price,status
A1,Ann@Example.com,2026-02-01,usa,2,10.50,PAID
A2,bob@example.com,2026-02-02,United Kingdom,1,5.00,shipped
A3,not-an-email,2026-02-30,India,0,10.999,new
A1,ann@example.com,2026-02-01,US,1,1.00,new
```


### `data-contract.md`

```markdown
# Data Contract — Orders CSV

The input header must contain exactly these fields, in any order: `order_id`, `customer_email`, `order_date`, `country`, `quantity`, `unit_price`, `status`.

- `order_id`: non-empty after trim; case-sensitive identity; first valid occurrence wins.
- `customer_email`: basic email shape; trim and lowercase.
- `order_date`: canonical real date `YYYY-MM-DD`.
- `country`: must exist in configured country mapping; output uppercase ISO-2 code.
- `quantity`: base-10 integer greater than zero; `2.0` is rejected.
- `unit_price`: finite, non-negative decimal with at most two fractional digits; `10.999` is rejected.
- `status`: one of `new`, `paid`, `shipped`, `cancelled`, lowercased.
- Derived fields: `order_total = quantity × unit_price`, `order_month = YYYY-MM`.

Missing, duplicate, or unexpected header columns fail the batch. A row with a field count different from the header is rejected. All field-level violations are collected. Reject rate is rejected input rows divided by all input data rows. A valid header-only file has zero rows and a zero reject rate. Invalid rows do not reserve duplicate IDs. Each reject entry contains a JSON-encoded copy of the raw row.
```


### `learning-notes.md`

```markdown
# Learning Notes — Project 03

Complete this during implementation; do not invent reflections before encountering real issues.

## Mistakes and fixes

1. **Mistake:** [What failed? Include test/command.]  
   **Root cause:** [...]  
   **Fix:** [...]  
   **Regression test:** [...]

2. **Mistake:** [...]  
   **Root cause:** [...]  
   **Fix:** [...]  
   **Regression test:** [...]

3. **Mistake:** [...]  
   **Root cause:** [...]  
   **Fix:** [...]  
   **Regression test:** [...]

## Design trade-offs

- Why does the baseline keep row outcomes in memory?
- What is the memory cost of the seen-order-ID set?
- How would deterministic output be preserved while streaming?
- Why do per-file atomic replacements not make the output set transactional?
```


### `README.md`

```markdown
# dqpipe — Data Quality & Transformation Pipeline

A deterministic batch pipeline using Python's standard library. It validates an orders CSV, normalises documented values, rejects invalid or duplicate rows with explanations, writes clean data, and emits a JSON quality report.

## Requirements

- Python 3.12+
- `uv`

## Setup and run

```bash
uv sync
uv run dqpipe run --input data/orders.csv --out-dir out --config config.toml
```

The command returns exit code `1` if the reject rate exceeds the configured threshold. Outputs are still written for investigation. Use `--dry-run` to report without writing output files.

## Quality gates

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src
```

## Outputs

- `clean_orders.csv`: validated, normalised, deduplicated rows plus derived columns.
- `rejects.csv`: one record per violation, including record number and raw row JSON.
- `quality_report.json`: counts, reject rate, rule counts/examples, totals summary, input SHA-256.

## Semantics and limitations

- Header must contain exactly the seven documented columns.
- UTF-8 and UTF-8 BOM are supported.
- The first valid occurrence of a normalised order ID wins; invalid rows do not reserve keys.
- Money is represented by `Decimal`; over-precision is rejected, not silently rounded.
- Each output is atomically replaced individually; the three files are not one transaction.
- Baseline materializes row outcomes in memory; it is not a constant-memory streaming pipeline.
- Reject files contain raw values. Use synthetic data only and do not commit private records.
```


## 9. CLI contract

```bash
uv run dqpipe run --input data/orders.csv --out-dir out --config config.toml
uv run dqpipe run --input data/orders.csv --out-dir out --max-reject-rate 0.10
uv run dqpipe run --input data/orders.csv --out-dir out --dry-run
```

- `0`: processing completed and reject rate is within the inclusive threshold.
- `1`: threshold exceeded, input/config/output failure, or invalid threshold.
- `2`: `argparse` usage error.
- JSON report is written to stdout; diagnostics are written to stderr.
- Threshold failure still writes outputs so source data can be investigated.
- `--dry-run` must not create or modify output files.

## 10. Test strategy and edge cases

The included tests cover validation rules, BOM input, quoted fields, multiple row violations, invalid-first/valid-second duplicate behavior, missing/extra headers, malformed row width, empty batches, TOML threshold validation, output contents, hash correctness, idempotency, CLI threshold behavior, dry-run, and missing input.

Before completion, add tests for duplicate header names, too many fields, an empty file without a header, unreadable input, unwritable output directory, threshold equality, `NaN`/infinite thresholds, and CLI usage errors. Golden-file tests are recommended. Do not enforce a universal wall-clock threshold in CI; record local measurements with environment details.

## 11. Scale and memory experiment

The learning plan asks for 200,000 synthetic rows and a time/memory check. Generate deterministic synthetic input (fixed seed or formula) and record Python version, OS, row count, input size, elapsed seconds, rows/second, peak memory, output counts, and reject rate in README.

The baseline intentionally materializes row outcomes and clean rows, so memory is O(n) in rows plus O(u) for the unique-key set. Do not call it streaming or constant-memory. A streaming rewrite is an extension; deduplication still needs O(u) key state unless using an alternative such as external sorting or a persistent index.

## 12. Engineering notes

### Determinism and idempotency
Same input bytes and configuration should produce identical output bytes. CSV column order and line endings are fixed, JSON keys are sorted, timestamps are omitted, and the input SHA-256 is included. The hash proves input identity, not configuration identity; adding a configuration hash is a reasonable extension.

### Atomic output writes
Each output is written to a temporary file in the destination directory, flushed, and replaced with `os.replace`. This protects an individual file from partial writes. It is **not** a transaction across all three outputs: a crash between replacements can leave a mixed set. A production extension would write to a versioned staging directory and atomically publish a manifest/pointer after all files succeed.

### Data privacy
Rejects include raw row values and therefore can contain email addresses. Use synthetic data only, do not commit real customer records, and restrict access to rejects in real systems.

### Honest scope
This is a production-minded learning project, not a production platform. It does not provide database transactions, scheduling, orchestration, distributed processing, full RFC email validation, or constant-memory streaming.

## 13. Common mistakes

- Dropping invalid rows silently instead of producing rejects.
- Deriving totals before validation.
- Using `float` for money.
- Stopping at the first invalid field.
- Calculating reject rate from violation count.
- Letting an invalid row reserve a duplicate key without deciding that policy.
- Manually joining CSV strings instead of using `csv`.
- Ignoring UTF-8 BOMs.
- Adding timestamps/random IDs that break deterministic reruns.
- Claiming streaming while retaining all rows in memory.
- Treating per-file atomic replacement as a multi-file transaction.

## 14. Git workflow

```bash
git status --short
git add pyproject.toml uv.lock config.toml data-contract.md README.md learning-notes.md src tests
git commit -m "Build deterministic data quality pipeline"
git status --short
```

Do not commit `.venv/`, caches, temporary files, or real customer data.

## 15. Acceptance checklist

- [ ] Contract agrees with code and tests.
- [ ] Python 3.12+, `uv`, `src/` package layout.
- [ ] Standard library only at runtime.
- [ ] All field rules and boundaries tested.
- [ ] Multiple violations collected per row.
- [ ] Header failures and row-shape rejects are explicit.
- [ ] Duplicate policy documented and tested.
- [ ] Derived columns only exist for valid rows.
- [ ] Clean CSV, rejects CSV, and JSON report match contract.
- [ ] Raw row evidence appears in rejects.
- [ ] SHA-256 matches original bytes.
- [ ] Rerunning yields byte-identical outputs.
- [ ] Threshold gate and dry-run work.
- [ ] stdout/stderr separation and exit codes verified.
- [ ] Ruff, format check, mypy strict, pytest, and locked clean install pass.
- [ ] 200,000-row time/memory experiment documented honestly.
- [ ] `learning-notes.md` has three real mistakes, root causes, fixes, and regression tests.
- [ ] Git working tree clean after commit.

## 16. Interview preparation

Be ready to explain: validation versus transformation; why `Decimal` is used; why row and violation counts differ; duplicate-key policy; what SHA-256 proves; why deterministic bytes matter; per-file atomic replacement versus a multi-file transaction; O(n) row memory and O(u) key memory; and why the baseline is batch rather than streaming.

## 17. Audit report

### Findings and corrections applied

1. **Money rounding ambiguity:** values with more than two fractional digits are rejected instead of silently rounded.
2. **Duplicate behavior:** the first valid occurrence wins; an invalid earlier row does not reserve the key.
3. **Reject-rate definition:** rejected rows divided by input rows, not violations divided by rows.
4. **Audit evidence:** rejects include the raw row as JSON.
5. **Schema drift:** missing, duplicate, and unexpected header fields fail clearly.
6. **Malformed record width:** rows with the wrong number of fields become rejects rather than crashing.
7. **Idempotency:** fixed column ordering, line endings, sorted JSON, no timestamps, and source SHA-256.
8. **Atomicity wording:** per-file atomic writes are distinguished from all-files transactional commit.
9. **Memory wording:** baseline explicitly documents O(n) row materialization; it does not claim streaming.
10. **CLI behavior:** dry-run avoids output writes; threshold failure preserves outputs for investigation.

### Actual execution record


- TOML parsing: **PASS** for `pyproject.toml` and `config.toml`.
- CLI smoke test: **PASS (expected quality-gate failure)** — the intentionally dirty sample produced 4 rows read, 1 clean, 3 rejected, a 75% reject rate, exit code 1, and all three output files. The configured threshold is 40%, so exit code 1 is correct.

- Python syntax parsing: **PASS** for all 8 Python source/test files.
- pytest: **PASS — 44 tests passed in 0.20 seconds** in the artifact-generation environment.
- Ruff lint: **NOT RUN** — Ruff executable unavailable in this environment.
- Ruff formatter check: **NOT RUN** — Ruff executable unavailable in this environment.
- mypy strict: **NOT RUN** — mypy executable unavailable in this environment.
- Clean `uv sync --locked`: **NOT RUN** — a fresh repository clone/install was not available in this execution.

The test suite and syntax checks are real executed results. Static-analysis and clean-install gates are not claimed as passing.

### Validation still required in the target repository

- `uv sync --locked` from a clean clone.
- `uv run pytest`.
- `uv run ruff check .`.
- `uv run ruff format --check .`.
- `uv run mypy --strict src`.
- Console-script behavior on the target operating system.
- A real 200,000-row timing/memory measurement.
- Manual review of `git status` and confirmation that no private data is committed.

This guide is designed to a production-minded Stage 1 standard, but it is still a learning project. It does not claim database transactions, orchestration, distributed execution, full email validation, or constant-memory streaming.
