# Project 01 — Personal Expense Ledger CLI

**Stage:** Stage 1 — Programming & Computational Thinking  
**Prerequisite modules:** 01–07 (computational thinking, core types, control flow, collections, files/CSV/CLI, packaging/tooling, testing/debugging)  
**Estimated effort:** 15–25 focused hours  
**Project type:** Single-user local CLI; standard library at runtime, `pytest`/`ruff`/`mypy` for development  
**Status:** Reference implementation and audit notes; run the complete quality gate in your own environment before marking complete.

> **Source alignment.** This guide follows the supplied Stage 1 `learning-plan.md`: `src/` package layout, Python 3.12+, `uv`, `argparse`, integer minor units for money, UTF-8 CSV, pure domain logic, atomic writes, deterministic output, meaningful exit codes, tests with `pytest`, and synthetic data only. The supplied `Roadmap_ptree.md` confirms this project lives at `Stage 1 — Programming & Computational Thinking/00-Stage-1-Overview/Projects/01-personal-expense-ledger-cli.md`.
>
> **Repository-access note.** The two supplied references were available in this conversation, but the actual repository directory and its pre-existing project brief were not attached or mounted. Therefore this is a complete replacement guide based on the supplied learning plan and project-tree reference; it has not been written back into your remote/local repository. Copy this file to the requested repository path when ready.

---

## 1. Project objective

Build an installable command-line application that records personal expenses in a local CSV file and can list, summarize, import, and export those expenses. The project is deliberately small: it exercises the engineering habits that later data pipelines depend on—strict input validation, exact numeric representation, safe persistence, deterministic processing, explicit failure behavior, and tests.

### Learning outcomes

By completion, you should be able to:

- decompose requirements into inputs, invariants, outputs, failure modes, and tests;
- explain why `float` is unsuitable for money and why integer cents are used;
- model an expense as an immutable dataclass with a deterministic identity;
- validate both user input and existing persisted data;
- keep domain logic separate from filesystem and terminal I/O;
- implement CSV handling with explicit UTF-8 and `newline=""`;
- perform atomic file replacement and explain its limits;
- implement a CLI with `argparse`, `stdout`, `stderr`, and documented exit codes;
- test boundary conditions, corrupt data, duplicates, Unicode, and round trips;
- document the architecture and known limitations honestly.

### Explicit non-goals

No database, web interface, authentication, multi-user access, concurrent-writer coordination, currency conversion, bank integration, encryption, pandas, or external runtime dependency. This is a learning project, not a financial product. Do not commit real bank statements or personal financial records.

## 2. Requirements and contract

| Area | Required behavior |
|---|---|
| Add | `ledger add 12.50 food --date 2026-01-05 --note "lunch"`; date defaults to the local system date when omitted. |
| Money | Positive finite amount; at most two decimal places; maximum `10,000,000.00` ledger units; no binary floating-point arithmetic. |
| Category | Trim whitespace and normalize to lowercase; reject empty values. |
| Identity | Deterministic ID from date, integer cents, normalized category, and description. |
| Duplicate handling | Exact duplicate is ignored, message goes to `stderr`, exit code is `0`. |
| List | Stable chronological order; optional category and inclusive `--from`/`--to` filters. |
| Summary | Totals per category and grand total; optional `--month YYYY-MM`; deterministic category ordering; text or JSON output. |
| Import | Import CSV columns `date,amount,category,description`; valid rows are kept when other rows are invalid; report each rejected row with line number. Re-importing does not add duplicates. |
| Export | CSV or JSON; deterministic ordering; atomic destination replacement. |
| Storage | One UTF-8 CSV ledger with a fixed header; validate the header, row fields, IDs, dates, amounts, and duplicates while loading. |
| Errors | CLI syntax errors use `argparse` exit `2`; data/domain/setup errors print a concise message to `stderr` and return `1`; success returns `0`. Unexpected programming defects are not swallowed by a catch-all. |
| Repeatability | Re-running the same operation does not duplicate entries; serialized ledger order and bytes are stable for the same logical input. |

### Exit-code contract

- `0` — successful operation, including an ignored duplicate.
- `1` — invalid amount/domain value, malformed ledger, unreadable file, or import completed with rejected rows.
- `2` — invalid CLI syntax or argument parsing failure (provided by `argparse`).

For import, valid rows are persisted even if other rows are rejected; the process returns `1` if at least one row was rejected. This is intentional so scripts can detect partial-quality input.

## 3. Design before coding (Milestone 1)

Create `design-notes.md` before implementing. Use the following checklist and pseudocode as your starting point; rewrite it in your own words.

### Inputs, outputs, invariants

- **Inputs:** command-line arguments, optional ledger CSV, optional import CSV.
- **Outputs:** ledger CSV, optional export file, human-readable terminal output, errors on `stderr`, exit status.
- **Money invariant:** stored as a positive integer number of minor units; no `float` enters the money path.
- **Category invariant:** non-empty, trimmed, lowercase string.
- **Identity invariant:** ID is derived from normalized business fields, not from row number or current time.
- **Storage invariant:** one exact header; each row is valid and ID matches its contents.
- **Ordering invariant:** date ascending, then stable ID ascending.
- **Atomicity invariant:** write to a temporary file in the destination directory and replace the destination only after successful flush and `fsync`.
- **Import invariant:** one bad data row must not discard other valid rows.

### Core pseudocode: `add`

```text
parse CLI arguments
load and validate current ledger
parse amount into integer cents
normalize category and description
construct validated Expense
if its deterministic ID already exists:
    report duplicate on stderr; return success
save all entries using atomic replacement
print new ID; return success
```

### Core pseudocode: `summary`

```text
parse and validate optional YYYY-MM month
load and validate ledger
for each entry matching the month (or all entries):
    add integer cents to its category total and grand total
sort category keys
render text or JSON with stable ordering
return success
```

### Edge-case matrix to expand

| Input case | Expected behavior | Evidence/test |
|---|---|---|
| Empty or whitespace amount | Reject with clear error | `test_parse_amount_invalid` |
| `0`, negative amount, `NaN`, infinity | Reject | `test_parse_amount_invalid` |
| More than two decimal places | Reject, even if extra digits are zero | `test_parse_amount_invalid` |
| Valid thousands grouping `1,200.00` | Parse to `120000` cents | `test_parse_amount_valid` |
| Invalid grouping `12,00` | Reject | `test_parse_amount_invalid` |
| Leap day `2028-02-29` / invalid `2026-02-29` | Accept valid date; reject invalid date | Add a focused CLI date test as an extension |
| Missing ledger file | Treat as empty ledger | `test_missing_file_is_empty` |
| Header-only ledger | Treat as empty ledger | `test_header_only_is_empty` |
| Corrupt date/cents/ID/header | Error with path and line where applicable; no traceback | `test_corrupt_row_has_path_and_line` plus extensions |
| Notes with commas, quotes, Unicode, or newlines | Round-trip via CSV quoting | `test_round_trip_and_deterministic_order` |
| Duplicate entry | No second row written | `test_duplicate_is_idempotent`, CLI test |
| Two entries on same date | Stable ID tie-break ordering | storage round-trip test |
| Import with mixed valid/invalid rows | Keep valid rows, report bad line, return `1` | `test_import_keeps_good_rows_and_reports_bad_rows` |
| Start date after end date | Report data/domain error | Add a focused CLI test as an extension |
| Two concurrent writers | Known limitation: last replacement may win | Document; do not claim locking support |

## 4. Project folder layout

Create this project inside the separate Stage 1 practice repository described in the learning plan. The expected repository-level layout is:

```text
stage-1-projects/
├── README.md
├── .gitignore
├── 01-expense-ledger/
│   ├── pyproject.toml
│   ├── uv.lock                  # generate and commit with `uv lock`
│   ├── README.md
│   ├── design-notes.md          # write in Milestone 1
│   ├── learning-notes.md        # expected / actual / evidence / root cause / fix / next time
│   ├── src/
│   │   └── ledger/
│   │       ├── __init__.py
│   │       ├── money.py
│   │       ├── models.py
│   │       ├── storage.py
│   │       ├── service.py
│   │       └── cli.py
│   ├── tests/
│   │   ├── test_money.py
│   │   ├── test_storage.py
│   │   ├── test_service.py
│   │   └── test_cli.py
│   └── data/
│       └── sample-import.csv     # synthetic fixture only
├── 02-logscope/
├── 03-dqpipe/
└── 04-riskreview/
```

The full code for every project file used in this guide is included in Section 8. `design-notes.md` and `learning-notes.md` are learner-authored evidence, not source modules; templates are provided in Section 6.

## 5. Tooling and setup

Use Python 3.12+ and `uv`. Run commands from the `01-expense-ledger/` directory.

```bash
uv init --package ledger-cli
# If starting from the generated skeleton, rename src/ledger_cli/ to src/ledger/
# and update imports / package name as needed. Alternatively, create the layout in Section 4 directly.
uv add --dev pytest ruff mypy
```

Use the `pyproject.toml` in Section 8 as the target configuration. It includes an explicit build system and package mode so the `ledger` console entry point is installed. After saving all files, generate and commit the lock file, then install from it:

```bash
uv lock
uv sync
uv run ledger --help
```

**Lock-file rule:** commit the generated `uv.lock`. Do not hand-author a fake lock file or omit it from the real repository. A lock file could not be generated in the preparation environment because package-index network access was unavailable; generate it on your machine with working package-index access.

## 6. Step-by-step implementation plan

Do the milestones in order. Do not copy all code blindly: type it, explain it, and add tests before implementing each behavior.

### M1 — Decompose and specify (1–2 hours)

1. Read the requirements in Section 2.
2. Create `design-notes.md` using the inputs/outputs/invariants and edge-case matrix from Section 3.
3. Draw the data flow: `argv → cli → domain/service → storage → filesystem`; for reports, `storage.load → pure aggregation → cli output`.
4. Write pseudocode for `add`, `list`, `summary`, and import.
5. Identify which errors are argument syntax (`2`) versus data/domain errors (`1`).
6. Commit: `docs(ledger): define requirements and edge cases`.

**Gate:** explain how a duplicate is recognized, why money uses integer cents, and what atomic replacement does and does not guarantee.

### M2 — Money boundary (2–3 hours)

1. Implement `MoneyError`, `parse_amount`, and `format_cents` in `money.py`.
2. Use `Decimal` only at the text parsing boundary; never construct it from a float.
3. Reject non-finite values, invalid grouping, scientific notation, signs, non-positive values, excess precision, and values over the ceiling.
4. Write parametrized valid/invalid tests before adding the next feature.
5. Run `uv run pytest tests/test_money.py -q` and the quality gate.
6. Commit: `feat(ledger): parse money exactly in integer cents`.

**Gate:** demonstrate why `0.1 + 0.2` is not an acceptable money representation and explain how the parser avoids that problem.

### M3 — Domain model and persistence (3–4 hours)

1. Implement immutable `Expense` and deterministic `expense_id` in `models.py`.
2. Implement `load` and `save` in `storage.py`.
3. Validate the fixed header, row field count, date, integer cents, category invariant, deterministic ID, and duplicate IDs on read.
4. Write UTF-8 CSV with `newline=""`, explicit `lineterminator`, sorted rows, a same-directory temporary file, flush, `fsync`, and `os.replace`.
5. Test missing file, header-only file, round-trip, embedded commas/quotes/newlines, deterministic bytes, and corrupted rows.
6. Commit: `feat(ledger): add validated atomic CSV storage`.

**Gate:** explain why a temporary file must be in the same directory and why atomic replacement is not a concurrency lock.

### M4 — CLI core (3–4 hours)

1. Implement `build_parser()` and `main(argv)` in `cli.py`.
2. Add `add`, `list`, and `summary` commands.
3. Put parsing and presentation in the CLI; keep aggregation and duplicate handling in `service.py`.
4. Route expected data/domain failures to concise `stderr` messages and return `1`.
5. Use `argparse` for invalid syntax (`2`); do not catch every exception.
6. Test commands using `main([...])`, `capsys`, and `tmp_path` rather than spawning subprocesses unnecessarily.
7. Commit: `feat(ledger): implement add list and summary commands`.

**Gate:** show that CLI tests can run without touching the real working directory or real ledger.

### M5 — Filters, import, export (3–5 hours)

1. Implement category and inclusive date filters in `service.py`.
2. Validate `--month` as a real `YYYY-MM` value.
3. Implement import from `date,amount,category,description`; report malformed rows with line numbers while retaining valid rows.
4. Deduplicate imported rows against both the existing ledger and earlier rows in the same import.
5. Implement CSV and JSON export using a temporary sibling and atomic replacement.
6. Test mixed-quality imports, re-import idempotency, JSON validity, and CSV quoting.
7. Commit: `feat(ledger): add filters and idempotent CSV import export`.

**Gate:** importing the same file twice does not add duplicate expenses; malformed rows are visible and the process exits `1`.

### M6 — Hardening and regression (2–4 hours)

1. Add regression tests for any discovered bug before applying the fix.
2. Verify invalid ledger headers, bad dates, non-integer cents, ID mismatch, duplicate stored IDs, malformed UTF-8, empty/header-only files, Unicode descriptions, and date-range inversion.
3. Check all filesystem errors become concise CLI errors without hiding unexpected programming errors.
4. Review deterministic sorting and output; verify writes do not leave temp files on failure where practical.
5. Run all tests and inspect the diff.
6. Commit: `test(ledger): cover corrupt data and edge cases`.

**Gate:** each bug fixed has a regression test and no expected data error leaks a traceback.

### M7 — Package, documentation, audit (2–3 hours)

1. Generate `uv.lock` and commit it.
2. Install with `uv sync`; verify the console script `uv run ledger` works.
3. Complete README examples with actual output generated from synthetic data.
4. Complete `learning-notes.md` with expected/actual/evidence/root cause/fix/next time.
5. Run the complete quality gate in Section 9.
6. Review every acceptance criterion in Section 10 and commit: `docs(ledger): document usage and limitations`.
7. Tag completion only after every gate passes: `git tag project-1-done`.

## 7. Architecture and design decisions

### Responsibilities

- `money.py`: parsing and formatting monetary values; no file I/O or printing.
- `models.py`: domain invariants and stable identity.
- `storage.py`: CSV schema, validation of persisted records, load/save, atomic replacement.
- `service.py`: pure duplicate, filtering, and aggregation functions.
- `cli.py`: argument parsing, orchestration, terminal output, and exit-code mapping.

### Key decisions and trade-offs

1. **Integer cents rather than float:** binary floating point cannot represent many decimal fractions exactly. Integer cents make addition and equality exact for a two-decimal currency. The current design assumes a single currency and does not encode currency metadata.
2. **`Decimal` only at input:** text is parsed directly as `Decimal`; no float conversion occurs. The domain and CSV use integer cents.
3. **Frozen dataclass:** entries cannot be mutated after construction; equality is value-based and the model validates its own invariants.
4. **Content-derived ID:** identical normalized fields produce the same ID, which supports idempotent import. This is not a security signature and should not be used as an authorization mechanism.
5. **Full-file rewrite:** appropriate for a small personal ledger and simpler than in-place mutation. Cost grows with file size.
6. **Atomic replacement:** prevents readers from observing a partially written target file under normal local-filesystem semantics. It does not prevent lost updates from concurrent writers and does not guarantee durability of directory metadata on every filesystem/platform.
7. **CSV storage:** human-readable and easy to inspect. `storage.py` isolates persistence so a later project can replace it with SQLite/PostgreSQL.
8. **Functional core, imperative shell:** service functions can be tested without the filesystem or terminal; the CLI is the side-effect boundary.
9. **No catch-all exception handling:** known data/domain errors are mapped to exit `1`; programming defects remain visible during development rather than being silently hidden.
10. **No real data:** synthetic fixtures protect privacy and keep the repository safe to share.

## 8. Complete reference implementation

Create each file at the path shown. These snippets form one coherent implementation.

### `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
package = true

[project]
name = "ledger-cli"
version = "0.1.0"
description = "A reliable local personal expense ledger CLI"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
ledger = "ledger.cli:main"

[dependency-groups]
dev = ["pytest", "ruff", "mypy"]

[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "C4", "RUF"]

[tool.mypy]
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### `.gitignore`

```gitignore
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.py[cod]
*.tmp
.env
ledger.csv
```

### `src/ledger/__init__.py`

```python
"""Personal expense ledger package."""

__version__ = "0.1.0"
```

### `src/ledger/money.py`

```python
"""Exact money parsing and formatting using integer minor units."""

from decimal import Decimal, InvalidOperation

MAX_CENTS = 1_000_000_000  # 10,000,000.00 in the chosen ledger currency


class MoneyError(ValueError):
    """Raised when an amount is not a valid positive monetary value."""


def parse_amount(text: str) -> int:
    """Parse a positive amount with at most two decimal places into integer cents.

    Commas are accepted only as thousands separators in groups of three. Scientific
    notation and signed values are rejected to keep the CLI input unambiguous.
    """
    cleaned = text.strip()
    if not cleaned:
        raise MoneyError("amount is required")
    if cleaned.startswith(("+", "-")) or "e" in cleaned.lower():
        raise MoneyError(f"invalid amount: {text!r}")
    if "," in cleaned:
        import re

        if re.fullmatch(r"\d{1,3}(,\d{3})+(\.\d{1,2})?", cleaned) is None:
            raise MoneyError(f"invalid comma grouping: {text!r}")
        cleaned = cleaned.replace(",", "")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise MoneyError(f"not a number: {text!r}") from None
    if not value.is_finite():
        raise MoneyError(f"amount must be finite: {text!r}")
    if value <= 0:
        raise MoneyError("amount must be greater than zero")
    fractional = value.as_tuple().exponent
    if fractional < -2:
        raise MoneyError("amount must have no more than two decimal places")
    cents_decimal = value * 100
    if cents_decimal != cents_decimal.to_integral_value():
        raise MoneyError("amount must have no more than two decimal places")
    cents = int(cents_decimal)
    if cents > MAX_CENTS:
        raise MoneyError(f"amount exceeds the maximum of {format_cents(MAX_CENTS)}")
    return cents


def format_cents(cents: int) -> str:
    """Format integer cents as a comma-grouped decimal string."""
    sign = "-" if cents < 0 else ""
    whole, fraction = divmod(abs(cents), 100)
    return f"{sign}{whole:,}.{fraction:02d}"
```

### `src/ledger/models.py`

```python
"""Validated, immutable domain model for ledger entries."""

import hashlib
import json
from dataclasses import dataclass
from datetime import date


class ExpenseError(ValueError):
    """Raised when an expense violates domain invariants."""


@dataclass(frozen=True, slots=True)
class Expense:
    """One expense in a single, user-defined currency."""

    expense_date: date
    amount_cents: int
    category: str
    description: str = ""

    def __post_init__(self) -> None:
        if self.amount_cents <= 0:
            raise ExpenseError("amount_cents must be positive")
        if self.amount_cents > 1_000_000_000:
            raise ExpenseError("amount_cents exceeds the supported maximum")
        if not self.category or self.category != self.category.strip().lower():
            raise ExpenseError("category must be non-empty, trimmed, and lowercase")
        if "\x00" in self.category or "\x00" in self.description:
            raise ExpenseError("category and description must not contain NUL characters")

    @property
    def expense_id(self) -> str:
        """Return a stable digest derived from the normalized business fields."""
        canonical = json.dumps(
            [self.expense_date.isoformat(), self.amount_cents, self.category, self.description],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
```

### `src/ledger/storage.py`

```python
"""CSV persistence with validation and atomic replacement."""

import csv
import os
import tempfile
from datetime import date
from pathlib import Path

from .models import Expense, ExpenseError

FIELDS = ["expense_id", "date", "amount_cents", "category", "description"]


class LedgerDataError(ValueError):
    """Raised when the on-disk ledger is malformed or violates invariants."""


def load(path: Path) -> list[Expense]:
    """Load and validate a ledger. A missing file means an empty ledger."""
    if not path.exists():
        return []
    try:
        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise LedgerDataError(f"{path}: missing CSV header")
            if reader.fieldnames != FIELDS:
                raise LedgerDataError(
                    f"{path}: expected header {','.join(FIELDS)!r}, "
                    f"found {','.join(reader.fieldnames)!r}"
                )
            expenses: list[Expense] = []
            seen_ids: set[str] = set()
            for line_number, row in enumerate(reader, start=2):
                try:
                    if None in row:
                        raise ValueError("wrong number of columns")
                    expense_id = row.get("expense_id")
                    row_date = row.get("date")
                    amount_cents = row.get("amount_cents")
                    category = row.get("category")
                    description = row.get("description")
                    if any(value is None for value in (expense_id, row_date, amount_cents, category, description)):
                        raise ValueError("missing required column value")
                    assert expense_id is not None
                    assert row_date is not None
                    assert amount_cents is not None
                    assert category is not None
                    assert description is not None
                    expense = Expense(
                        expense_date=date.fromisoformat(row_date),
                        amount_cents=int(amount_cents),
                        category=category,
                        description=description,
                    )
                    if expense_id != expense.expense_id:
                        raise ValueError("expense_id does not match row contents")
                    if expense.expense_id in seen_ids:
                        raise ValueError("duplicate expense_id")
                    seen_ids.add(expense.expense_id)
                    expenses.append(expense)
                except (ValueError, TypeError, ExpenseError) as exc:
                    raise LedgerDataError(f"{path}:{line_number}: invalid row: {exc}") from exc
            return expenses
    except UnicodeDecodeError as exc:
        raise LedgerDataError(f"{path}: file is not valid UTF-8") from exc
    except csv.Error as exc:
        raise LedgerDataError(f"{path}: invalid CSV: {exc}") from exc
    except OSError as exc:
        raise LedgerDataError(f"cannot read {path}: {exc}") from exc


def save(path: Path, expenses: list[Expense]) -> None:
    """Write a deterministic CSV atomically; clean up temporary files on failure."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            for expense in sorted(expenses, key=lambda item: (item.expense_date, item.expense_id)):
                writer.writerow(
                    {
                        "expense_id": expense.expense_id,
                        "date": expense.expense_date.isoformat(),
                        "amount_cents": expense.amount_cents,
                        "category": expense.category,
                        "description": expense.description,
                    }
                )
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
```

### `src/ledger/service.py`

```python
"""Pure filtering, duplicate detection, and aggregation operations."""

from collections import defaultdict
from datetime import date

from .models import Expense


def add_if_new(expenses: list[Expense], candidate: Expense) -> tuple[list[Expense], bool]:
    """Return a new list and whether candidate was inserted."""
    if any(item.expense_id == candidate.expense_id for item in expenses):
        return list(expenses), False
    return [*expenses, candidate], True


def filter_expenses(
    expenses: list[Expense],
    *,
    category: str | None = None,
    start: date | None = None,
    end: date | None = None,
) -> list[Expense]:
    """Filter entries inclusively by category and date bounds, in stable order."""
    normalized_category = category.strip().lower() if category is not None else None
    selected = [
        item
        for item in expenses
        if (normalized_category is None or item.category == normalized_category)
        and (start is None or item.expense_date >= start)
        and (end is None or item.expense_date <= end)
    ]
    return sorted(selected, key=lambda item: (item.expense_date, item.expense_id))


def summarize(expenses: list[Expense], month: str | None = None) -> tuple[dict[str, int], int]:
    """Return sorted category totals and grand total, optionally for YYYY-MM."""
    totals: dict[str, int] = defaultdict(int)
    grand_total = 0
    for item in expenses:
        if month is None or item.expense_date.strftime("%Y-%m") == month:
            totals[item.category] += item.amount_cents
            grand_total += item.amount_cents
    return dict(sorted(totals.items())), grand_total
```

### `src/ledger/cli.py`

```python
"""Argument parsing and command-line presentation for the ledger."""

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path
from collections.abc import Sequence

from . import storage
from .models import Expense
from .money import format_cents, parse_amount
from .service import add_if_new, filter_expenses, summarize

EXIT_OK = 0
EXIT_DATA = 1


def _date_arg(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must be a real date in YYYY-MM-DD format") from exc


def _month_arg(value: str) -> str:
    try:
        parsed = date.fromisoformat(f"{value}-01")
    except ValueError as exc:
        raise argparse.ArgumentTypeError("month must use YYYY-MM format") from exc
    if parsed.strftime("%Y-%m") != value:
        raise argparse.ArgumentTypeError("month must use YYYY-MM format")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ledger", description="Personal expense ledger")
    parser.add_argument("--file", type=Path, default=Path("ledger.csv"), help="ledger CSV path")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="record an expense")
    add.add_argument("amount", help="positive amount, up to two decimal places")
    add.add_argument("category")
    add.add_argument("--date", type=_date_arg, default=None)
    add.add_argument("--note", default="", help="optional description")

    listing = commands.add_parser("list", help="list expenses")
    listing.add_argument("--category")
    listing.add_argument("--from", dest="start", type=_date_arg)
    listing.add_argument("--to", dest="end", type=_date_arg)

    summary = commands.add_parser("summary", help="summarize expenses by category")
    summary.add_argument("--month", type=_month_arg)
    summary.add_argument("--format", choices=("text", "json"), default="text")

    importer = commands.add_parser("import-csv", help="import expenses from a CSV file")
    importer.add_argument("source", type=Path)

    exporter = commands.add_parser("export", help="export the ledger")
    exporter.add_argument("destination", type=Path)
    exporter.add_argument("--format", choices=("csv", "json"), default="csv")
    return parser


def _import_rows(source: Path) -> tuple[list[Expense], list[str]]:
    """Parse an import CSV with date, amount, category, description columns."""
    accepted: list[Expense] = []
    rejected: list[str] = []
    required = {"date", "amount", "category", "description"}
    try:
        with source.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise storage.LedgerDataError(
                    f"{source}: import header must contain date,amount,category,description"
                )
            for line_number, row in enumerate(reader, start=2):
                try:
                    if None in row or any(row.get(key) is None for key in required):
                        raise ValueError("wrong number of columns")
                    category = (row["category"] or "").strip().lower()
                    if not category:
                        raise ValueError("category is required")
                    accepted.append(
                        Expense(
                            expense_date=date.fromisoformat((row["date"] or "").strip()),
                            amount_cents=parse_amount(row["amount"] or ""),
                            category=category,
                            description=(row["description"] or "").strip(),
                        )
                    )
                except ValueError as exc:
                    rejected.append(f"line {line_number}: {exc}")
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise storage.LedgerDataError(f"cannot import {source}: {exc}") from exc
    return accepted, rejected


def _write_export(destination: Path, expenses: list[Expense], output_format: str) -> None:
    """Export to a temporary sibling then atomically replace the destination."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        payload = [
            {
                "expense_id": item.expense_id,
                "date": item.expense_date.isoformat(),
                "amount_cents": item.amount_cents,
                "amount": format_cents(item.amount_cents),
                "category": item.category,
                "description": item.description,
            }
            for item in sorted(expenses, key=lambda item: (item.expense_date, item.expense_id))
        ]
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        _atomic_text(destination, text)
        return
    # Reuse storage's schema and deterministic ordering via an isolated temporary ledger.
    _atomic_csv_export(destination, expenses)


def _atomic_text(destination: Path, content: str) -> None:
    import os
    import tempfile

    fd, temp_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, destination)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _atomic_csv_export(destination: Path, expenses: list[Expense]) -> None:
    import os
    import tempfile

    fd, temp_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=storage.FIELDS, lineterminator="\n")
            writer.writeheader()
            for item in sorted(expenses, key=lambda item: (item.expense_date, item.expense_id)):
                writer.writerow({
                    "expense_id": item.expense_id,
                    "date": item.expense_date.isoformat(),
                    "amount_cents": item.amount_cents,
                    "category": item.category,
                    "description": item.description,
                })
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, destination)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _print_expenses(expenses: list[Expense]) -> None:
    print("DATE        AMOUNT       CATEGORY       DESCRIPTION")
    for item in expenses:
        print(f"{item.expense_date.isoformat()}  {format_cents(item.amount_cents):>10}  {item.category:<14} {item.description}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        expenses = storage.load(args.file)
        if args.command == "add":
            category = args.category.strip().lower()
            if not category:
                raise ExpenseError("category must not be empty")
            candidate = Expense(
                expense_date=args.date or date.today(),
                amount_cents=parse_amount(args.amount),
                category=category,
                description=args.note.strip(),
            )
            updated, inserted = add_if_new(expenses, candidate)
            if not inserted:
                print(f"duplicate ignored: {candidate.expense_id}", file=sys.stderr)
                return EXIT_OK
            storage.save(args.file, updated)
            print(f"added {candidate.expense_id}")
            return EXIT_OK
        if args.command == "list":
            if args.start is not None and args.end is not None and args.start > args.end:
                raise ValueError("--from must be on or before --to")
            _print_expenses(filter_expenses(expenses, category=args.category, start=args.start, end=args.end))
            return EXIT_OK
        if args.command == "summary":
            totals, grand_total = summarize(expenses, args.month)
            if args.format == "json":
                print(json.dumps({"month": args.month, "categories": {k: format_cents(v) for k, v in totals.items()}, "grand_total": format_cents(grand_total)}, ensure_ascii=False, sort_keys=True))
            else:
                for category, cents in totals.items():
                    print(f"{category:<15}{format_cents(cents):>12}")
                print(f"{'GRAND TOTAL':<15}{format_cents(grand_total):>12}")
            return EXIT_OK
        if args.command == "import-csv":
            imported, rejected = _import_rows(args.source)
            updated = list(expenses)
            seen = {item.expense_id for item in updated}
            added_count = 0
            for item in imported:
                if item.expense_id not in seen:
                    updated.append(item)
                    seen.add(item.expense_id)
                    added_count += 1
            if added_count:
                storage.save(args.file, updated)
            print(f"imported {added_count} new expense(s); rejected {len(rejected)} row(s)")
            for message in rejected:
                print(message, file=sys.stderr)
            return EXIT_DATA if rejected else EXIT_OK
        if args.command == "export":
            _write_export(args.destination, expenses, args.format)
            print(f"exported {len(expenses)} expense(s) to {args.destination}")
            return EXIT_OK
        parser.error("unsupported command")
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_DATA
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
```

### `tests/test_money.py`

```python
import pytest

from ledger.money import MoneyError, format_cents, parse_amount


@pytest.mark.parametrize(
    ("text", "expected"),
    [("12.5", 1250), ("0.01", 1), ("1,200.00", 120000), (" 3 ", 300), ("5.", 500), (".5", 50)],
)
def test_parse_amount_valid(text: str, expected: int) -> None:
    assert parse_amount(text) == expected


@pytest.mark.parametrize(
    "text",
    ["", "abc", "NaN", "Infinity", "-5", "+5", "0", "1.234", "1e3", "12,00", "10000000.01"],
)
def test_parse_amount_invalid(text: str) -> None:
    with pytest.raises(MoneyError):
        parse_amount(text)


def test_format_cents() -> None:
    assert format_cents(123456) == "1,234.56"
    assert format_cents(5) == "0.05"
    assert format_cents(-5) == "-0.05"
```

### `tests/test_storage.py`

```python
from datetime import date

import pytest

from ledger.models import Expense
from ledger.storage import LedgerDataError, load, save


def test_round_trip_and_deterministic_order(tmp_path) -> None:
    path = tmp_path / "nested" / "ledger.csv"
    late = Expense(date(2026, 2, 1), 250, "food", "tea, coffee")
    early = Expense(date(2026, 1, 1), 125, "transport", 'quote " test\nnext line')
    save(path, [late, early])
    assert load(path) == [early, late]
    first_bytes = path.read_bytes()
    save(path, [late, early])
    assert path.read_bytes() == first_bytes


def test_missing_file_is_empty(tmp_path) -> None:
    assert load(tmp_path / "missing.csv") == []


def test_header_only_is_empty(tmp_path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("expense_id,date,amount_cents,category,description\n", encoding="utf-8")
    assert load(path) == []


def test_corrupt_row_has_path_and_line(tmp_path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("expense_id,date,amount_cents,category,description\nbad,not-a-date,x,food,\n", encoding="utf-8")
    with pytest.raises(LedgerDataError, match=r"bad.csv:2"):
        load(path)
```

### `tests/test_service.py`

```python
from datetime import date

from ledger.models import Expense
from ledger.service import add_if_new, filter_expenses, summarize


def test_duplicate_is_idempotent() -> None:
    expense = Expense(date(2026, 1, 1), 100, "food", "lunch")
    same = Expense(date(2026, 1, 1), 100, "food", "lunch")
    updated, inserted = add_if_new([expense], same)
    assert not inserted
    assert updated == [expense]


def test_filter_and_summary() -> None:
    expenses = [
        Expense(date(2026, 1, 1), 100, "food"),
        Expense(date(2026, 1, 2), 200, "transport"),
        Expense(date(2026, 2, 1), 300, "food"),
    ]
    assert len(filter_expenses(expenses, category=" FOOD ", start=date(2026, 1, 1), end=date(2026, 1, 31))) == 1
    totals, grand = summarize(expenses, "2026-01")
    assert totals == {"food": 100, "transport": 200}
    assert grand == 300
```

### `tests/test_cli.py`

```python
import csv
import json

from ledger.cli import main


def test_add_duplicate_and_summary(tmp_path, capsys) -> None:
    path = tmp_path / "ledger.csv"
    assert main(["--file", str(path), "add", "12.50", "Food", "--date", "2026-01-05", "--note", "lunch"]) == 0
    assert main(["--file", str(path), "add", "12.50", "food", "--date", "2026-01-05", "--note", "lunch"]) == 0
    captured = capsys.readouterr()
    assert "duplicate ignored" in captured.err
    assert main(["--file", str(path), "summary", "--month", "2026-01"]) == 0
    assert "12.50" in capsys.readouterr().out


def test_bad_amount_is_data_error(tmp_path, capsys) -> None:
    assert main(["--file", str(tmp_path / "ledger.csv"), "add", "abc", "food"]) == 1
    assert "error:" in capsys.readouterr().err


def test_import_keeps_good_rows_and_reports_bad_rows(tmp_path, capsys) -> None:
    source = tmp_path / "input.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "amount", "category", "description"])
        writer.writeheader()
        writer.writerow({"date": "2026-01-01", "amount": "2.50", "category": "Food", "description": "lunch, tea"})
        writer.writerow({"date": "bad", "amount": "3.00", "category": "food", "description": "invalid date"})
    ledger = tmp_path / "ledger.csv"
    assert main(["--file", str(ledger), "import-csv", str(source)]) == 1
    captured = capsys.readouterr()
    assert "imported 1 new" in captured.out
    assert "line 3" in captured.err
    assert main(["--file", str(ledger), "list"]) == 0
    assert "lunch, tea" in capsys.readouterr().out


def test_json_summary_and_export(tmp_path, capsys) -> None:
    ledger = tmp_path / "ledger.csv"
    main(["--file", str(ledger), "add", "4.25", "food", "--date", "2026-01-01"])
    capsys.readouterr()
    assert main(["--file", str(ledger), "summary", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["grand_total"] == "4.25"
    output = tmp_path / "out.json"
    assert main(["--file", str(ledger), "export", str(output), "--format", "json"]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))[0]["amount"] == "4.25"
```

### `data/sample-import.csv`

```csv
date,amount,category,description
2026-01-05,12.50,Food,lunch
2026-01-06,3.25,transport,metro
not-a-date,4.00,food,intentionally invalid row
```

### `README.md`

```markdown
# Personal Expense Ledger CLI

A small local command-line ledger for learning reliable Python engineering. It stores synthetic/local entries in UTF-8 CSV, uses integer cents, validates persisted rows, and writes atomically.

## Requirements and setup

Python 3.12+ and `uv` are required.

```bash
uv sync
uv run ledger --help
uv run pytest -q
uv run ruff format --check .
uv run ruff check .
uv run mypy --strict src
```

## Examples

```bash
uv run ledger --file data/ledger.csv add 12.50 food --date 2026-01-05 --note "lunch"
uv run ledger --file data/ledger.csv list --category food --from 2026-01-01 --to 2026-01-31
uv run ledger --file data/ledger.csv summary --month 2026-01
uv run ledger --file data/ledger.csv export data/export.json --format json
```

## Data format

The ledger CSV header is `expense_id,date,amount_cents,category,description`. Import CSV expects `date,amount,category,description`. The amount is assumed to use one configured-but-not-enforced currency; currency conversion and currency metadata are out of scope.

## Architecture

- `money.py`: strict decimal parsing and integer-cent formatting.
- `models.py`: immutable domain object and deterministic ID.
- `storage.py`: CSV schema validation and atomic persistence.
- `service.py`: pure duplicate, filtering, and summary logic.
- `cli.py`: argument parsing, output, exit codes, import/export wiring.

## Exit codes

- `0`: success (including duplicate ignored).
- `1`: malformed data or domain/input error discovered after parsing arguments.
- `2`: invalid CLI syntax/arguments (`argparse`).

## Limitations

No multi-writer locking: concurrent writers can overwrite each other's changes. Atomic replacement protects against partially written files, not lost updates. No authentication, database, currency conversion, or encrypted storage. Treat local ledger files as sensitive and do not commit real financial data.
```

## 9. Quality gate and practical commands

Run from the project directory:

```bash
uv lock                         # generate/update the reproducible lock file
uv sync                         # install exact locked dependencies
uv run ruff format .            # format source and tests
uv run ruff check .             # lint
uv run mypy --strict src        # strict static type check
uv run pytest -q                # tests
uv run ledger --help            # installed console script
```

Useful end-to-end examples (all use synthetic data):

```bash
uv run ledger --file data/ledger.csv add 12.50 food --date 2026-01-05 --note "lunch"
uv run ledger --file data/ledger.csv add 3.25 transport --date 2026-01-06 --note "metro"
uv run ledger --file data/ledger.csv list --from 2026-01-01 --to 2026-01-31
uv run ledger --file data/ledger.csv list --category food
uv run ledger --file data/ledger.csv summary --month 2026-01
uv run ledger --file data/ledger.csv summary --month 2026-01 --format json
uv run ledger --file data/ledger.csv import-csv data/sample-import.csv
uv run ledger --file data/ledger.csv export data/export.csv --format csv
uv run ledger --file data/ledger.csv export data/export.json --format json
```

For a malformed input check, pass an amount such as `abc` or import `data/sample-import.csv` (which deliberately contains an invalid date). Do not interpret the sample fixture as real financial data.

## 10. Universal acceptance checklist (adapted from the learning plan)

- [ ] `uv lock` has generated a real `uv.lock`, and it is committed.
- [ ] `uv sync` succeeds from a clean checkout.
- [ ] The documented `uv run ledger ...` console-script commands work exactly as written.
- [ ] `uv run ruff format --check .` passes after formatting.
- [ ] `uv run ruff check .` passes with no unexplained suppressions.
- [ ] `uv run mypy --strict src` passes.
- [ ] `uv run pytest -q` passes.
- [ ] Invalid CLI syntax returns `2`; malformed data/domain input returns `1` with a concise `stderr` message and no traceback.
- [ ] Duplicate add and repeated import have no duplicate side effects.
- [ ] Storage rejects invalid headers/rows rather than silently skipping corruption.
- [ ] Round-trip tests cover CSV commas, quotes, embedded newlines, Unicode, and deterministic ordering.
- [ ] Summary totals use integers and are sorted deterministically.
- [ ] Atomic write behavior is implemented and the concurrent-writer limitation is documented.
- [ ] README has actual output copied from a run against synthetic data.
- [ ] `design-notes.md` and `learning-notes.md` contain learner-authored reasoning and evidence.
- [ ] No real personal or financial data is committed.
- [ ] A final review confirms every module has one clear responsibility.

## 11. Detailed engineering audit report

### 11.1 Audit scope

The audit compared this implementation against the supplied Stage 1 learning-plan standards: package layout, Python 3.12+, standard-library runtime, integer cents, dataclasses, deterministic identity and output, validated CSV, atomic writes, functional-core/imperative-shell separation, meaningful exit codes, CLI tests, and synthetic data. It also executed the available tests and Python bytecode compilation in the preparation environment.

### 11.2 Findings and remediation

| Severity | Finding/risk | Resolution in this guide | Verification status |
|---|---|---|---|
| High | Floating-point money can introduce rounding errors | Domain storage uses integer cents; input parsing uses `Decimal` from text | Unit tests passed for accepted/rejected values |
| High | Corrupt persisted rows could leak raw `ValueError`/`KeyError` | `LedgerDataError` includes file path and row number; fixed header and ID checks are enforced | Corrupt-row test passed; add more header/UTF-8 regression tests before release |
| High | Direct writes can truncate the ledger if interrupted | Storage and export write a same-directory temp file, flush, `fsync`, then `os.replace` | Code reviewed; no crash-injection test executed |
| High | Import may abort at first bad row or partially duplicate records | Import records rejected lines, retains valid rows, and deduplicates by deterministic ID | Mixed valid/invalid import test passed |
| Medium | A monolithic CLI mixes business logic and I/O | Domain model, money, storage, service, and CLI responsibilities are separated | Structure reviewed; tests exercise service and CLI |
| Medium | Output order may vary and make diffs/tests flaky | Entries sort by date/ID; categories sort lexically; CSV uses explicit line terminators | Deterministic storage byte test passed |
| Medium | CLI failures may have ambiguous status | Exit-code contract is documented; `argparse` handles syntax errors; known data/domain errors return `1` | Bad amount test passed; argument exit code should also be tested via subprocess as an extension |
| Medium | Packaging script may not install if build configuration is missing | Explicit build-system and `[tool.uv] package = true` are included | Packaging could not be installed in this environment due package-index network failure |
| Medium | A generated lock file is needed for reproducible clean installs | Instructions explicitly require generating and committing `uv.lock` | Not generated: `mypy`/`ruff` were not cached and package-index network access was unavailable |
| Medium | Two concurrent writers can lose updates | Limitation is explicitly documented; concurrency is out of scope per the learning plan | Known limitation, not a defect against project scope |
| Low | Date range inversion could otherwise silently return no rows | CLI detects `--from` later than `--to` and reports a domain error | Code path reviewed; add a dedicated test |
| Low | CSV schema is implicit unless documented | Ledger and import headers are specified in code and README | Code reviewed |

### 11.3 Executed checks in the preparation environment

- **Python syntax/bytecode compilation:** passed (`python -m compileall -q src tests`).
- **Pytest:** passed, **28 tests** (`PYTHONPATH=src python -m pytest -q`).
- **Ruff:** not executed; Ruff was not installed in the environment and network access to package indexes failed.
- **Mypy strict:** not executed; mypy was not installed/cached and network access to package indexes failed.
- **`uv sync` / installed console entry point / lockfile:** not fully verified because the environment could not fetch development/build dependencies. The project configuration includes a build system and package mode, but the clean-install acceptance item remains open until run in a network-enabled environment.

Do not report the project as fully release-verified until Ruff, mypy, lockfile generation, clean `uv sync`, and the installed console script have all passed on your machine.

### 11.4 Remaining known limitations and recommended next fixes

1. **Single-writer only:** atomic replacement is not a lock. If concurrent use becomes a requirement, add cross-platform file locking or move to SQLite with transactions.
2. **Currency is implicit:** all amounts are assumed to be in one currency. Do not mix currencies until the model and reports include an explicit currency code.
3. **Date default uses local system date:** this is appropriate for this personal CLI; for scheduled services, inject a clock and define timezone behavior explicitly.
4. **Filesystem durability is platform-dependent:** `fsync` is applied to the temporary file; directory metadata durability is not guaranteed uniformly across operating systems.
5. **More tests recommended:** malformed header, invalid UTF-8, duplicate ID in stored file, missing amount/category columns in import, date-range inversion, invalid month, invalid CLI syntax exit code, and temp-file cleanup after a simulated write failure should receive focused regression tests before calling the project production-ready.
6. **Scale:** every mutation rewrites the full ledger. This is intentionally acceptable for a small personal file; measure before optimizing and use a transactional store if scale/concurrency changes.

### 11.5 Audit conclusion

The architecture and implementation align with the learning plan's intended engineering practices, and the available test suite plus syntax compilation passed. The code is a strong educational baseline, but it should be described as **validated in part**, not fully production-certified, until the unavailable static-analysis and packaging checks are run and the remaining focused tests are added. The project is intentionally not a multi-user financial system.

## 12. Git workflow and learning evidence

Suggested commits:

```text
docs(ledger): define requirements and edge cases
feat(ledger): parse money exactly in integer cents
feat(ledger): add validated atomic CSV storage
feat(ledger): implement add list and summary commands
feat(ledger): add filters and idempotent CSV import export
test(ledger): cover corrupt data and edge cases
docs(ledger): document usage and limitations
```

Create `learning-notes.md` with one entry for each meaningful issue:

```markdown
## YYYY-MM-DD — Short issue title
- Expected:
- Actual:
- Evidence (command/test/output):
- Root cause:
- Fix:
- Regression test:
- What I will do differently next time:
```

Before tagging, inspect `git status`, review the diff, confirm only synthetic sample data is tracked, run the quality gate, and then tag `project-1-done`.

## 13. Definition of completion

The project is complete when Section 10 is fully checked, the code is understood well enough to explain the major trade-offs without reading the guide, and the audit report's open checks have been resolved or explicitly accepted. Then proceed to Project 02 — Log Investigation & Reliability CLI; do not skip the acceptance gate.
