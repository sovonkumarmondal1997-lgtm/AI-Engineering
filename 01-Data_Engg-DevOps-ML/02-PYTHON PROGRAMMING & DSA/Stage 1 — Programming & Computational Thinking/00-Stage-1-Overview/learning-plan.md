# Stage 1 Learning Plan — Programming & Computational Thinking

**Status:** Not Started
**Roadmap position:** Stage 1 of the Applied AI / Agentic AI Engineering roadmap.
**Starting point:** The 24 module folders of this stage (`01-` … `24-`), built on the Stage 0 developer
environment (Linux/WSL2, Git, `uv`).
**Purpose:** Turn Python knowledge into *engineering evidence*. You do this by building four small but
production-minded command-line programs, each one stretching the skills of the modules before it.

> Stage 1 is not about collecting syntax. A data or AI engineer is trusted because their programs read
> messy input, fail loudly and clearly, can be re-run safely, and are covered by tests. The four
> projects below are the proof. Every later stage (pandas, SQL, pipelines, APIs, LLM tooling) reuses the
> habits you form here.

---

## 1. Stage outcome

By the end of this stage you can:

- decompose a vague requirement into inputs, rules, outputs, edge cases and tests **before** coding;
- write idiomatic, typed, linted Python 3.12+ in a `src/` package layout managed by `uv`;
- parse and validate untrusted text (CSV, JSON, TOML, log lines) without crashing on bad rows;
- represent money, time and identity correctly (`Decimal`/integer cents, timezone-aware UTC, stable IDs);
- build CLIs with `argparse` that use `stdout`, `stderr`, and meaningful exit codes;
- separate pure domain logic from I/O so the logic can be unit-tested without touching the disk;
- write `pytest` suites with parametrization, fixtures, `tmp_path`, boundary and regression tests;
- make jobs repeatable (idempotent), and write files safely (temp file + atomic replace);
- explain a design decision, a trade-off and a bug you fixed in a short technical interview.

You are **not** expected to know pandas, SQL databases, web frameworks, async programming, Docker, or ML
yet. Using them in these projects would defeat their purpose: the standard library plus `pytest`,
`ruff` and `mypy` is enough.

---

## 2. The four projects at a glance

| # | Project | What it proves | Core skills | Prerequisite modules | Effort |
|---|---|---|---|---|---|
| 1 | [Personal Expense Ledger CLI](./Projects/01-personal-expense-ledger-cli.md) | You can build a complete, tested, installable CLI over a small data store | types, dicts, files, CSV, `argparse`, `Decimal`, dataclasses, `pytest`, atomic writes | 01–07 | 15–25 h |
| 2 | [Log Investigation & Reliability CLI](./Projects/02-log-investigation-and-reliability-cli.md) | You can analyse large, dirty text streams and surface incidents | regex, generators, `Counter`, `deque`, datetimes, streaming, exit codes | 01–07, 09 (iterators, datetime, collections) | 15–25 h |
| 3 | [Data Quality & Transformation Pipeline](./Projects/03-data-quality-and-transformation-pipeline.md) | You can validate, clean, transform and audit tabular data repeatably | validation rules, pure functions, reject files, quality reports, idempotency, hashing | 01–08, 10 | 20–30 h |
| 4 | [Rule-Based Risk Review Engine](./Projects/04-rule-based-risk-review-engine.md) | You can design an explainable, configurable decision system | OOP/Protocols, enums, TOML config, stateful rules, golden-file tests, layered design | 01–11 | 25–35 h |

The projects are **cumulative**: Project 2 reuses the CLI skeleton and test habits of Project 1,
Project 3 reuses Project 1's atomic-write and Project 2's reporting, and Project 4 reuses the
configuration, validation and report patterns of all three. Do them **in order**.

> The files under `Projects/` are the *brief and rubric* for each project. This plan is the *how*:
> the design, the build order, verified starter code, and the quality bar. If a brief and this plan
> ever disagree, keep the brief's requirements and this plan's engineering approach, and note the
> difference in your project README.

---

## 3. Suggested sequencing with the 24 modules

Do not wait until all 24 modules are finished. Learn a block, then immediately apply it in a project.
This is the single most effective pacing choice in the stage.

| Phase | Study these modules | Then build | Gate to leave the phase |
|---|---|---|---|
| A. Foundations | 01 Computational thinking → 02 Core types → 03 Control flow, functions, errors | Warm-up exercises from each `practice-questions.md` | You can write and dry-run a function with its pre/postconditions on paper |
| B. Data handling | 04 Problem solving & collections → 05 Files, CSV/JSON, CLI → 06 Packages, `uv`, `ruff`, types → 07 Testing & debugging | **Project 1** | Project 1 acceptance checklist (Section 4.9) passes |
| C. Streams & modelling | 08 OOP & dataclasses → 09 Iterators, datetime, `Counter`/`deque` → 10 Production habits | **Projects 2 and 3** (do 2 as soon as 09 is read) | Projects 2–3 checklists pass; both are idempotent and tested |
| D. Design | 11 Data model → 24 Functions & OOP gap lessons (as needed) → 08 re-read | **Project 4** | Project 4 checklist passes; you can defend the design verbally |
| E. Depth (parallel, optional) | 12–23 as reference: stdlib (13), modern features (15), advanced testing (16), profiling (17), packaging (18), security (22), refactoring (23) | Stretch goals of each project | Use as a reading list, not a blocker |

**Modules 12–23 are enrichment.** The four projects must be completable with modules 01–11 plus
Module 24 as a gap-filler. Where a project suggests a later module, it is explicitly marked as a
stretch goal.

**Cadence.** Rough guide for a learner with ~10 focused hours a week: Phase A 2 weeks, Project 1 in
2 weeks, Project 2 in 2 weeks, Project 3 in 2–3 weeks, Project 4 in 3 weeks. Adjust to your pace,
but never skip the acceptance checklists.

---

## 4. Shared engineering standard (applies to all four projects)

### 4.1 Repository layout

Keep your practice code in its own Git repository (suggested name: `stage-1-projects`), separate from
these notes. One repository, four independent `uv` projects:

```text
stage-1-projects/
├── README.md                  # index of the four projects + how to run each
├── .gitignore                 # .venv/, __pycache__/, .pytest_cache/, .mypy_cache/, .ruff_cache/, .env, *.tmp
├── 01-expense-ledger/
├── 02-logscope/
├── 03-dqpipe/
└── 04-riskreview/
```

Each project folder is a self-contained package:

```text
01-expense-ledger/
├── pyproject.toml
├── uv.lock                    # commit this: it makes installs reproducible
├── README.md                  # purpose, install, usage examples with real output, design notes, limits
├── src/ledger/                # importable package (src layout prevents accidental imports from cwd)
│   ├── __init__.py
│   └── ...
├── tests/
│   └── test_*.py
└── data/                      # SYNTHETIC sample data only; never real financial data
```

### 4.2 Toolchain and `pyproject.toml`

Create each project with `uv`, then add the dev tools:

```bash
uv init --package ledger-cli      # creates pyproject.toml and src/ layout; rename the package to `ledger`
cd ledger-cli
uv add --dev pytest ruff mypy
uv run pytest                     # run tests inside the project environment
uv run ruff check . && uv run ruff format --check .
uv run mypy --strict src
```

> `uv init --package` generates a `src/<name>/` package and a `[build-system]` table. Keep the
> generated `[build-system]` as it is (do not hand-edit its version pins), and make sure the import
> name used in `[project.scripts]` matches your package folder (a hyphenated project name such as
> `ledger-cli` maps to an import package such as `ledger`; rename the generated folder if needed).

A reasonable `pyproject.toml` (the `[build-system]` table generated by `uv` stays untouched):

```toml
[project]
name = "ledger-cli"
version = "0.1.0"
description = "Personal expense ledger on the command line"
requires-python = ">=3.12"
dependencies = []                 # standard library only for all four projects

[project.scripts]
ledger = "ledger.cli:main"        # `uv run ledger add ...` after `uv sync`

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

### 4.3 Quality gate — "definition of done" for every milestone

Run all four before every commit. A milestone is not finished until they pass:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy --strict src
uv run pytest -q
```

### 4.4 Design rules (the senior-engineer checklist)

1. **Functional core, imperative shell.** Parsing, validation, scoring and aggregation are pure functions
   or small classes with no file/print calls. `cli.py` is the only place that touches `argv`,
   `stdout`, `stderr` and exit codes. This is what makes the logic testable.
2. **Fail fast on programmer and configuration errors; fail gracefully on data errors.** A malformed
   row is *data*: count it, report it, continue. A missing required column or a broken config is a
   *setup problem*: stop with a clear message and a non-zero exit code.
3. **Never use `float` for money.** Use integer minor units (cents) or `Decimal`. Never build
   `Decimal` from a float.
4. **Time is timezone-aware UTC.** Parse to aware `datetime`, compare aware with aware, format as ISO 8601.
5. **Explicit encodings.** `open(..., encoding="utf-8")` always; `newline=""` for CSV files.
6. **No silent failure.** No bare `except:`; no `except Exception: pass`. Catch the narrowest
   exception you can name, and keep the original cause (`raise ... from exc`).
7. **No `eval`/`exec`/`pickle` on input**, no shell-string subprocesses, no secrets in code.
8. **Write files atomically**: write to a temp file in the *same directory*, flush, `fsync`, then
   `os.replace`. A crash must never leave a half-written output.
9. **Determinism.** Same input → byte-identical output. Sort anything that comes from a `set` or
   `dict` of unknown order before writing; seed any randomness; inject "now" instead of calling
   `datetime.now()` deep in logic.
10. **Exit codes mean something.** `0` success, `1` the run completed but found data problems
    (or an expected domain failure), `2` bad usage/arguments (`argparse` does this itself),
    and any unexpected exception is a bug that must not be hidden.
11. **Every bug becomes a regression test** before it is fixed.
12. **Synthetic data only.** Never put real bank statements, real logs or personal data in the repository.

### 4.5 Testing standard

- Test the pure core with plain unit tests; test the CLI with `main(argv)` and `capsys`/`tmp_path`
  (no subprocess needed for most tests).
- Use `pytest.mark.parametrize` for tables of inputs. Cover: normal case, **boundary** (exactly
  at a threshold), empty input, invalid input, duplicate input, and unicode/whitespace oddities.
- Name tests as behaviours: `test_rejects_amount_with_three_decimals`.
- Aim for meaningful coverage of branches in the core logic; do not chase a percentage number.
- Keep tests independent: no shared mutable state, no dependence on the current directory or the
  current date.

### 4.6 Git workflow

- One repository, small commits, Conventional-Commit-style messages: `feat(ledger): add summary command`,
  `test(logscope): cover malformed lines`, `fix(dqpipe): reject duplicate order ids`.
- Commit the lock file and sample *synthetic* data. Never commit `.env`, real data or caches.
- Tag each finished project: `git tag project-1-done`.

### 4.7 Documentation standard (each project README)

Purpose and non-goals · install and run commands · 3–5 real usage examples with actual output ·
data format and assumptions · design overview (modules and their responsibilities) · testing
instructions · known limitations · "what I would do next".

### 4.8 The learning loop for each project

```text
Understand → decompose → define data + edge cases → write failing test → smallest implementation
→ run quality gate → commit → refactor → document → review against the checklist
```

Keep a `learning-notes.md` per project (expected / actual / evidence / root cause / fix / next time),
the same habit as Stage 0.

### 4.9 Universal acceptance checklist

Before declaring any project done, every box must be ticked:

- [ ] `uv sync` on a clean clone, then the README's commands work exactly as written.
- [ ] The quality gate (4.3) passes with no warnings suppressed without a comment explaining why.
- [ ] Bad input produces a clear message on `stderr` and the documented exit code — never a traceback.
- [ ] Re-running with the same input gives identical output and no duplicated side effects.
- [ ] A reviewer can read each module in under five minutes and say what it is responsible for.
- [ ] There are tests for the boundary conditions you listed in your design notes.
- [ ] The README contains real sample output generated from synthetic data.

---

## 5. Project 1 — Personal Expense Ledger CLI

Brief: [`Projects/01-personal-expense-ledger-cli.md`](./Projects/01-personal-expense-ledger-cli.md)

### 5.1 What it is and why it matters

A command-line tool that records personal expenses in a local file and reports on them
(`add`, `list`, `summary`, later `import`/`export`). It looks trivial — that is the point. It forces
you to get the *fundamentals of every data program* right: validated input, a correct money type, a
stable storage format, safe writes, and a CLI that behaves like a real tool. If you cannot make this
reliable, a pipeline over millions of rows will not be reliable either.

**Real-world analogue:** a tiny transactional store with an ingestion API, a query layer and a report —
the same shape as a data-platform service, at 1/1000 of the size.

### 5.2 Scope

In scope: add, list (with filters), monthly category summary, CSV import/export, duplicate
protection, validation, atomic persistence, packaging as a console script, tests.
Out of scope: databases, web UI, currencies/exchange rates, authentication, concurrency between
multiple writers (document this limit instead).

### 5.3 Requirements to turn into your own test list

| Area | Requirement |
|---|---|
| Add | `ledger add 12.50 food --date 2026-01-05 --note "lunch"`; date defaults to today; category is normalised (trimmed, lower-case) |
| Validation | amount > 0, ≤ 2 decimal places, finite, below a sanity ceiling; date is a real calendar date; category not empty |
| List | sorted by date; optional `--category`, `--from`, `--to` filters |
| Summary | totals per category, optional `--month YYYY-MM`; grand total; deterministic order |
| Import / export | `import-csv` skips and reports bad rows, never aborts the whole file for one bad row; `export` writes CSV or JSON |
| Duplicates | re-adding the identical expense (same date, amount, category, note) is ignored with a message on `stderr`, exit code 0 |
| Storage | one CSV file; header row; UTF-8; never half-written (atomic replace) |
| Errors | invalid usage → exit 2 (argparse); invalid data → message on `stderr`, exit 1 |

### 5.4 Architecture

```text
src/ledger/
├── money.py     # parse_amount / format_cents  — pure, the only place money rules live
├── models.py    # Expense (frozen dataclass) + deterministic expense_id
├── storage.py   # load() / save() — CSV file, atomic write; no business rules
├── cli.py       # argparse + wiring + exit codes; no business rules
└── (later) report.py  # summary/filters as pure functions over list[Expense]
```

Data flow: `argv → cli → money/models (validate) → storage (persist)`; reporting is
`storage.load → pure report functions → cli (print)`.

**Key decisions to be able to defend**

- *Integer cents, not float or even raw `Decimal` in the file.* `0.1 + 0.2 != 0.3` in binary floating
  point; integers are exact, compact and trivially comparable. `Decimal` is used only at the parsing
  boundary, where we also reject `NaN`/`Infinity` and extra decimals.
- *Frozen dataclass.* Immutable values are hashable, safe to share and compare by value, which is
  what makes duplicate detection a one-liner (`new in expenses`).
- *Deterministic ID from content.* The same expense always hashes to the same `expense_id`, so
  import is naturally idempotent.
- *Full-file atomic rewrite.* For a personal ledger the data is small, and rewriting the whole file
  via temp-file + `os.replace` is simpler and safer than in-place appends.
- *Why CSV and not a database?* Human-readable and Git-diffable. A later stage replaces it with
  SQLite/Postgres; keeping `storage.py` as the only I/O module makes that swap easy.

### 5.5 Starter code (verified: passes `ruff`, `mypy --strict`, `pytest`)

Treat these as a *reference skeleton to read, type out and understand* — not to paste. Then extend it
with the missing features from 5.3 yourself.

**`src/ledger/money.py`**

```python
"""Money is stored as integer minor units (cents); floats never touch it."""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

MAX_CENTS = 10_000_000_00  # 10 million, a sanity ceiling


class MoneyError(ValueError):
    """Raised when text cannot be read as a valid amount."""


def parse_amount(text: str) -> int:
    """Convert '12.5' or '1,200.00' to integer cents. Reject NaN, Infinity, > 2 decimals."""
    cleaned = text.strip().replace(",", "")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise MoneyError(f"not a number: {text!r}") from None
    if not value.is_finite():
        raise MoneyError(f"not a finite number: {text!r}")
    cents = (value * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    if cents != value * 100:
        raise MoneyError(f"more than 2 decimal places: {text!r}")
    if cents <= 0:
        raise MoneyError(f"amount must be positive: {text!r}")
    if cents > MAX_CENTS:
        raise MoneyError(f"amount too large: {text!r}")
    return int(cents)


def format_cents(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    whole, frac = divmod(abs(cents), 100)
    return f"{sign}{whole:,}.{frac:02d}"
```

**`src/ledger/models.py`**

```python
import hashlib
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class Expense:
    expense_date: date
    amount_cents: int
    category: str
    description: str = ""

    @property
    def expense_id(self) -> str:
        """Deterministic ID: re-importing the same row cannot create a duplicate."""
        parts = (
            self.expense_date.isoformat(),
            str(self.amount_cents),
            self.category,
            self.description,
        )
        raw = "|".join(parts)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
```

**`src/ledger/storage.py`**

```python
import csv
import os
import tempfile
from datetime import date
from pathlib import Path

from .models import Expense

FIELDS = ["expense_id", "date", "amount_cents", "category", "description"]


def load(path: Path) -> list[Expense]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return [
            Expense(
                expense_date=date.fromisoformat(row["date"]),
                amount_cents=int(row["amount_cents"]),
                category=row["category"],
                description=row["description"],
            )
            for row in csv.DictReader(fh)
        ]


def save(path: Path, expenses: list[Expense]) -> None:
    """Write to a temp file in the same directory, then atomically replace the target."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            writer.writeheader()
            for e in sorted(expenses, key=lambda x: (x.expense_date, x.expense_id)):
                writer.writerow(
                    {
                        "expense_id": e.expense_id,
                        "date": e.expense_date.isoformat(),
                        "amount_cents": e.amount_cents,
                        "category": e.category,
                        "description": e.description,
                    }
                )
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
```

**`src/ledger/cli.py`**

```python
import argparse
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from . import storage
from .models import Expense
from .money import MoneyError, format_cents, parse_amount

EXIT_OK, EXIT_DATA = 0, 1  # argparse itself exits with 2 on bad usage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ledger", description="Personal expense ledger")
    parser.add_argument("--file", type=Path, default=Path("ledger.csv"))
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="record one expense")
    add.add_argument("amount")
    add.add_argument("category")
    add.add_argument("--date", type=date.fromisoformat, default=None)
    add.add_argument("--note", default="")

    sub.add_parser("list", help="show all expenses")
    summary = sub.add_parser("summary", help="totals per category")
    summary.add_argument("--month", help="YYYY-MM")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        expenses = storage.load(args.file)
        if args.command == "add":
            new = Expense(
                args.date or date.today(),
                parse_amount(args.amount),
                args.category.strip().lower(),
                args.note.strip(),
            )
            if new in expenses:
                print(f"duplicate ignored: {new.expense_id}", file=sys.stderr)
                return EXIT_OK
            storage.save(args.file, [*expenses, new])
            print(f"added {new.expense_id}")
        elif args.command == "list":
            for e in sorted(expenses, key=lambda x: x.expense_date):
                amount = format_cents(e.amount_cents)
                print(f"{e.expense_date}  {amount:>12}  {e.category}  {e.description}")
        elif args.command == "summary":
            totals: dict[str, int] = defaultdict(int)
            for e in expenses:
                if args.month is None or e.expense_date.strftime("%Y-%m") == args.month:
                    totals[e.category] += e.amount_cents
            for category, cents in sorted(totals.items()):
                print(f"{category:<15}{format_cents(cents):>12}")
        return EXIT_OK
    except MoneyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_DATA


if __name__ == "__main__":
    raise SystemExit(main())
```

**Tests that pin the behaviour**

**`tests/test_money.py`**

```python
import pytest

from ledger.money import MoneyError, format_cents, parse_amount


@pytest.mark.parametrize(
    ("text", "cents"),
    [("12.5", 1250), ("0.01", 1), ("1,200.00", 120000), (" 3 ", 300)],
)
def test_parse_amount_valid(text, cents):
    assert parse_amount(text) == cents


@pytest.mark.parametrize("text", ["", "abc", "NaN", "Infinity", "-5", "0", "1.234", "99999999999"])
def test_parse_amount_invalid(text):
    with pytest.raises(MoneyError):
        parse_amount(text)


def test_format_cents():
    assert format_cents(123456) == "1,234.56"
    assert format_cents(5) == "0.05"
```

**`tests/test_cli.py`**

```python
from ledger.cli import main


def test_add_then_summary(tmp_path, capsys):
    ledger = tmp_path / "l.csv"
    assert main(["--file", str(ledger), "add", "12.50", "Food", "--date", "2026-01-05"]) == 0
    assert (
        main(["--file", str(ledger), "add", "12.50", "food", "--date", "2026-01-05"]) == 0
    )  # duplicate
    capsys.readouterr()
    assert main(["--file", str(ledger), "summary", "--month", "2026-01"]) == 0
    assert capsys.readouterr().out.split() == ["food", "12.50"]


def test_bad_amount_returns_error_code(tmp_path, capsys):
    assert main(["--file", str(tmp_path / "l.csv"), "add", "abc", "food"]) == 1
    assert "error:" in capsys.readouterr().err
```

**What the skeleton deliberately leaves for you** (these are the real learning):

1. A corrupted ledger file (bad date, non-integer cents, missing column) currently raises a raw
   `ValueError`/`KeyError`. Introduce a `LedgerDataError`, raise it from `storage.load` with the file
   path and line number, and map it to exit code 1 in `cli.main`.
2. Filters (`--category`, `--from`, `--to`) and the `import-csv` / `export` subcommands.
3. A grand-total line in `summary` and a `--format json` option.
4. `cli.main` is one long function. Refactor each subcommand into its own `cmd_add(args)` /
   `cmd_list(args)` / `cmd_summary(args)` function and dispatch through `set_defaults(func=...)`.
5. Concurrency limit: two simultaneous `add` runs can lose an update (last writer wins). Document this
   in the README as a known limitation; mention file locking as a later improvement.

### 5.6 Build order (milestones)

| Milestone | Deliverable | Done when |
|---|---|---|
| M1 Decompose | `design-notes.md`: inputs, outputs, rules, edge-case table, CLI sketch, pseudocode for `add` and `summary` | You can dry-run `add` on paper |
| M2 Money | `money.py` + `test_money.py` | All valid/invalid amount cases pass |
| M3 Model + storage | `models.py`, `storage.py`, round-trip test (`save` then `load` equals input) | Round-trip and atomic-write tests pass |
| M4 CLI core | `add`, `list`, `summary`; exit codes; `stderr` messages | CLI tests pass |
| M5 Import/export + filters | `import-csv` with a reject report, `export --format csv` or `--format json` | Mixed good/bad file imports the good rows and reports the bad ones |
| M6 Hardening | `LedgerDataError`, unicode notes, very large amounts, empty file, header-only file | Regression tests added for each |
| M7 Package + docs | console script works via `uv run ledger ...`; README with real output | Acceptance checklist 4.9 passes |

### 5.7 Edge cases to test (write these down in M1)

Empty file · header-only file · amounts `0`, `0.00`, `-5`, `.5`, `5.`, `1e3`, `1,000.50`, `NaN`, `inf`,
`12.345`, ` 7 ` · leap day `2028-02-29` vs invalid `2026-02-29` · category with spaces/upper-case/unicode ·
notes containing commas, quotes and newlines (CSV quoting!) · duplicate entry · two expenses on the same
date (stable ordering) · ledger path in a directory that does not exist · read-only file.

### 5.8 Common mistakes to avoid

- `float` arithmetic anywhere in the money path.
- Opening CSV files without `newline=""` (blank lines appear on Windows; embedded newlines break).
- Writing the ledger directly with `open(path, "w")` — a crash mid-write destroys the data.
- Putting `print` and `sys.exit` inside parsing or storage functions (untestable).
- Catching `Exception` in `main` to "keep the program running" and hiding real bugs.
- Mutable default arguments, and sorting with a key that is not total (ties produce unstable output).

### 5.9 Stretch goals

Monthly budgets with an over-budget warning (Module 03) · recurring expenses · `--format table` using
plain string formatting · property-style randomised tests with a seeded `random.Random` (Module 13) ·
SQLite backend behind the same storage interface (Module 13).

### 5.10 Interview talking points

"I stored money as integer cents and used `Decimal` only to parse, because …" · "I made import
idempotent with a content hash so …" · "Writes are atomic because …" · "The CLI is a thin shell over a pure core,
so I tested the logic without touching the filesystem."

---

## 6. Project 2 — Log Investigation & Reliability CLI

Brief: [`Projects/02-log-investigation-and-reliability-cli.md`](./Projects/02-log-investigation-and-reliability-cli.md)

### 6.1 What it is and why it matters

A CLI that reads application log files, tolerates garbage, and answers the questions an on-call
engineer asks: *How many errors? Which messages repeat? Which service is failing? When did it start?
What happened to request `r002001`?* This is Stage 0's shell investigation lab rebuilt as a reliable,
tested Python tool. In data engineering you spend a large part of your career reading logs of jobs that
failed at 3 a.m.; in AI engineering the same skill applies to model-serving, agent and evaluation logs.

### 6.2 Scope

In scope: multi-file input, a defined line format, malformed-line accounting, level counts, top
repeated errors, per-service error rate, error-burst detection, request tracing, time-range filters,
text and JSON reports, meaningful exit codes. Out of scope: real-time tailing, distributed logs,
dashboards, log shipping.

**Log format used by this project** (document it in the README and keep the regex in one place):

```text
2026-03-01T08:00:01Z INFO api req=r000001 request ok
2026-03-01T08:00:02Z ERROR payments req=r000002 db timeout
2026-03-01T08:00:03Z WARN worker started                      # request id is optional
```

### 6.3 Requirements

| Area | Requirement |
|---|---|
| Parsing | one regex with named groups; timezone-aware UTC timestamp; malformed lines are *counted*, never fatal; blank lines ignored |
| Streaming | files are read line by line through a generator; memory use does not grow with file size |
| Reports | `summary` (levels, top-N errors, per-service error counts/rate), `bursts` (N errors within a window), `trace <request-id>` (all lines for one request, in time order), `--since/--until` filters |
| Reliability | missing file → clear error, exit 1; undecodable bytes are replaced and counted rather than crashing; if the malformed-line rate exceeds a threshold (`--max-malformed-rate`, default 5 %), the run exits 1 with a warning even though a report was produced |
| Output | human-readable text by default, `--format json` for machines; reports go to `stdout`, warnings and diagnostics go to `stderr` |

### 6.4 Architecture

```text
src/logscope/
├── parser.py     # LINE_RE, parse_line(), read_events() generator, ParseStats
├── analysis.py   # level_counts, top_error_messages, find_error_bursts, error_rate_by_service (pure)
├── report.py     # format_text(), format_json()                               (pure formatting)
└── cli.py        # argparse subcommands: summary | bursts | trace; exit codes
tools/make_logs.py  # seeded synthetic log generator (planted incident + malformed lines)
```

**Key decisions to be able to defend**

- *Generator pipeline.* `read_events` yields events one at a time. A summary needs one pass; do not
  `list()` the whole file unless a command truly needs sorting (and say so in a comment).
- *`ParseStats` as an explicit out-parameter.* Counting malformed lines is part of the result, not a
  side effect hidden in a logger. The caller decides what rate is acceptable.
- *Sliding-window with `deque`.* Finding "N errors within M seconds" naively is O(n²); a `deque` of
  recent timestamps makes it O(n) because each timestamp is appended and popped at most once.
- *UTC-aware datetimes.* Mixing naive and aware datetimes raises `TypeError`; parsing to aware UTC
  at the boundary removes a whole class of bugs.
- *Sorted input assumption.* Real logs from multiple files interleave. State this assumption in the
  docstring and either sort (memory cost) or use `heapq.merge` over per-file streams (stretch goal).

### 6.5 Starter code (verified)

**Reproducible synthetic data** — always generate test logs, never use real ones. Same seed, same bytes.

**`tools/make_logs.py`**

```python
"""Generate a reproducible synthetic log file: python tools/make_logs.py logs/app.log 5000"""

import random
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

SERVICES = ["api", "auth", "worker", "payments"]
ERRORS = ["db timeout", "upstream 503", "invalid token", "disk quota exceeded"]
INFOS = ["request ok", "cache hit", "job started", "job finished"]


def main(out: Path, n: int, seed: int = 42) -> None:
    rng = random.Random(seed)  # own RNG instance: same seed => byte-identical file
    now = datetime(2026, 3, 1, 8, 0, 0, tzinfo=UTC)
    lines = []
    for i in range(n):
        now += timedelta(seconds=rng.randint(0, 3))
        level = rng.choices(["INFO", "WARN", "ERROR"], weights=[85, 10, 5])[0]
        if 2000 <= i < 2040:  # planted incident: an error burst on one service
            level, svc = "ERROR", "payments"
        else:
            svc = rng.choice(SERVICES)
        msg = rng.choice(ERRORS if level == "ERROR" else INFOS)
        lines.append(f"{now:%Y-%m-%dT%H:%M:%S}Z {level} {svc} req=r{i:06d} {msg}")
        if i % 997 == 0:
            lines.append("### corrupted line ###")  # planted malformed input
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]), int(sys.argv[2]))
```

```bash
python tools/make_logs.py data/app.log 5000     # 5 000 events, one planted payments incident, some corrupt lines
```

**`src/logscope/parser.py`**

```python
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

LINE_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+"
    r"(?P<level>DEBUG|INFO|WARN|ERROR|CRITICAL)\s+"
    r"(?P<service>[\w.-]+)\s+"
    r"(?:req=(?P<request_id>[\w-]+)\s+)?"
    r"(?P<message>.*)$"
)


@dataclass(frozen=True, slots=True)
class LogEvent:
    timestamp: datetime  # timezone-aware, UTC
    level: str
    service: str
    request_id: str | None
    message: str


def parse_line(line: str) -> LogEvent | None:
    """Return an event, or None when the line is malformed."""
    match = LINE_RE.match(line.rstrip("\n"))
    if match is None:
        return None
    ts = datetime.strptime(match["ts"], "%Y-%m-%dT%H:%M:%SZ")
    # strptime gives a naive datetime; attach UTC explicitly
    return LogEvent(
        ts.replace(tzinfo=UTC),
        match["level"],
        match["service"],
        match["request_id"],
        match["message"],
    )


@dataclass
class ParseStats:
    total: int = 0
    malformed: int = 0


def read_events(paths: Iterable[Path], stats: ParseStats) -> Iterator[LogEvent]:
    """Stream events lazily; a 5 GB log never has to fit in memory."""
    for path in paths:
        with path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if not line.strip():
                    continue
                stats.total += 1
                event = parse_line(line)
                if event is None:
                    stats.malformed += 1
                    continue
                yield event
```

**`src/logscope/analysis.py`**

```python
from collections import Counter, deque
from collections.abc import Iterable
from datetime import datetime, timedelta

from .parser import LogEvent


def level_counts(events: Iterable[LogEvent]) -> Counter[str]:
    return Counter(e.level for e in events)


def top_error_messages(events: Iterable[LogEvent], n: int = 5) -> list[tuple[str, int]]:
    return Counter(e.message for e in events if e.level in {"ERROR", "CRITICAL"}).most_common(n)


def find_error_bursts(
    events: Iterable[LogEvent], window: timedelta, threshold: int
) -> list[tuple[datetime, datetime, int]]:
    """Report windows where `threshold` or more errors landed within `window`.

    Expects events sorted by timestamp. Uses a sliding deque: O(n) overall.
    """
    recent: deque[datetime] = deque()
    bursts: list[tuple[datetime, datetime, int]] = []
    in_burst = False
    for event in events:
        if event.level not in {"ERROR", "CRITICAL"}:
            continue
        recent.append(event.timestamp)
        while recent and event.timestamp - recent[0] > window:
            recent.popleft()
        if len(recent) >= threshold and not in_burst:
            bursts.append((recent[0], event.timestamp, len(recent)))
            in_burst = True
        elif len(recent) < threshold:
            in_burst = False
    return bursts
```

**`tests/test_logscope.py`**

```python
from datetime import timedelta
from pathlib import Path

from logscope.analysis import find_error_bursts, level_counts, top_error_messages
from logscope.parser import ParseStats, parse_line, read_events


def test_parse_line_with_and_without_request_id():
    a = parse_line("2026-03-01T10:00:00Z ERROR api req=abc-1 db timeout")
    b = parse_line("2026-03-01T10:00:01Z INFO worker started")
    assert (a.request_id, a.message) == ("abc-1", "db timeout")
    assert b.request_id is None and b.message == "started"
    assert a.timestamp.utcoffset() == timedelta(0)


def test_malformed_lines_are_counted_not_fatal(tmp_path: Path):
    log = tmp_path / "a.log"
    log.write_text("garbage line\n2026-03-01T10:00:00Z INFO api ok\n\n", encoding="utf-8")
    stats = ParseStats()
    events = list(read_events([log], stats))
    assert len(events) == 1 and (stats.total, stats.malformed) == (2, 1)


def test_bursts_and_counts(tmp_path: Path):
    lines = [f"2026-03-01T10:00:{s:02d}Z ERROR api boom" for s in (0, 5, 10, 50)]
    lines.append("2026-03-01T10:01:00Z INFO api fine")
    events = [parse_line(line) for line in lines]
    assert level_counts(events) == {"ERROR": 4, "INFO": 1}
    assert top_error_messages(events) == [("boom", 4)]
    bursts = find_error_bursts(events, timedelta(seconds=15), threshold=3)
    assert len(bursts) == 1 and bursts[0][2] == 3
```

**What the skeleton deliberately leaves for you**

1. `cli.py` with `summary`, `bursts`, `trace`, `--since/--until`, `--format json`, and exit codes.
2. `error_rate_by_service`: `errors / total` per service, guarding against division by zero.
3. The `--max-malformed-rate` check (use `ParseStats`).
4. `report.py` so that text and JSON output are produced from the *same* result dictionary.
5. Multi-file merge ordering and a test for it.
6. An analysis-level regression test: run the generator with seed 42 and assert that the planted
   incident (payments errors around the 2000th event) is detected as a burst — this is your end-to-end proof.

### 6.6 Build order

| Milestone | Deliverable | Done when |
|---|---|---|
| M1 Decompose | `design-notes.md` with the log grammar, the investigation questions, and edge cases | Each question maps to a function |
| M2 Parser | `parser.py` + tests (valid, no request id, malformed, blank, bad date like `2026-13-45`) | Malformed lines never raise |
| M3 Generator | `make_logs.py`; determinism test (two runs → identical bytes) | Planted incident exists |
| M4 Analysis | counts, top-N, error rate, bursts, trace + unit tests | All pass on small hand-written inputs |
| M5 CLI + reports | three subcommands, text/JSON output, filters | CLI tests via `main(argv)` pass |
| M6 Reliability | malformed-rate gate, missing file, invalid UTF-8 test, 1M-line smoke test | Memory stays flat (check with `/usr/bin/time -v`) |
| M7 Docs | README with an *investigation walk-through* using the planted incident | Acceptance checklist passes |

### 6.7 Edge cases to test

Empty file · only malformed lines · timestamp valid by regex but invalid as a date (`2026-13-45T…`) ·
two events at the same second · single error (threshold 1) · burst exactly at threshold · burst that straddles
two files · window boundary (`> window` vs `>= window`: decide, document, and test it) · lower-case level
(`error`) — is it malformed or normalised? · a request id that appears in several services ·
Windows line endings (`\r\n`) · a 200-KB single line · bytes that are not UTF-8.

### 6.8 Common mistakes

- Loading the whole file with `read().splitlines()`, then claiming it "streams".
- Naive `datetime.strptime` results compared with aware ones, or `datetime.now()` inside analysis.
- Using a list as a queue (`pop(0)` is O(n)); use `deque`.
- Counting with a hand-rolled dict when `Counter` states the intent.
- Letting one malformed line crash the run, or — the opposite — silently dropping malformed lines
  without reporting how many.
- Printing diagnostics to `stdout`, which corrupts JSON output piped into another tool.
- Regex that backtracks catastrophically on long lines; keep patterns anchored and simple.

### 6.9 Stretch goals

`--follow` mode that tails a growing file · percentile latency if a duration field is added (Module 13
`statistics`) · gzip input transparently (Module 14) · `heapq.merge` across files · a simple
"error budget" calculation against a stated availability target · compare two time windows
("before/after deploy").

### 6.10 Interview talking points

"I process logs as a stream so memory is O(1) in file size." · "Bursts are found with a sliding window in
O(n) instead of comparing every pair." · "Malformed input is counted and gated by a threshold — I
neither crash nor hide it." · "Synthetic seeded data gives a reproducible incident to test detection."

---

## 7. Project 3 — Data Quality & Transformation Pipeline

Brief: [`Projects/03-data-quality-and-transformation-pipeline.md`](./Projects/03-data-quality-and-transformation-pipeline.md)

### 7.1 What it is and why it matters

A batch pipeline that takes a messy CSV of customer orders and produces three things: a **clean dataset**,
a **reject file** that says exactly which row broke which rule and why, and a **quality report**
(counts, reject rate, violations by rule). It is the smallest honest version of what data engineers get
paid for: *extract → validate → transform → load → report*, repeatably, with an audit trail.

You do this with the standard library only. In Stage 2 you will recognise every idea when it reappears
as pandas, schema validation libraries, data contracts and orchestrated pipelines — but you will understand
what those tools are doing for you.

### 7.2 Scope

In scope: CSV input with a BOM or dirty values, field-level validation rules, normalisation, derived
columns, duplicate-key handling, reject file with reasons, quality report as JSON, idempotent reruns,
config-driven thresholds (fail the run if the reject rate is too high). Out of scope: databases,
scheduling, streaming, distributed processing.

**Input contract** (`orders.csv`):

| Column | Rule | Normalisation |
|---|---|---|
| `order_id` | required, unique | trimmed |
| `customer_email` | required, matches basic email shape | trimmed, lower-cased |
| `order_date` | ISO `YYYY-MM-DD`, real calendar date | → `date` |
| `country` | in the known mapping | → ISO-2 code (`usa` → `US`) |
| `quantity` | integer > 0 | → `int` |
| `unit_price` | decimal ≥ 0, finite | → `Decimal` quantised to 2 places |
| `status` | in `{new, paid, shipped, cancelled}` | lower-cased |

Derived columns (only for rows that passed validation): `order_total = quantity × unit_price`,
`order_month = YYYY-MM`.

### 7.3 Architecture — the stages are separate functions

```text
src/dqpipe/
├── rules.py      # pure field rules: raise RuleError(rule_id, message) or return the normalised value
├── pipeline.py   # extract() → validate() → dedupe() → transform() → load() + run() orchestration
├── report.py     # (your task) build/format the quality report; threshold checks
├── config.py     # (your task) read thresholds/mappings from TOML via tomllib
└── cli.py        # `dqpipe run --input orders.csv --out-dir out/ --max-reject-rate 0.2`
```

```text
orders.csv ─► extract ─► validate ─► dedupe ─► transform ─► load ─► out/clean_orders.csv
(lines)      (rows)     (clean | violations)                    ├─► out/rejects.csv
                                                                 └─► out/quality_report.json
```

**Key decisions to be able to defend**

- *Validate, then transform.* Derived values (like `order_total`) are only computed from validated
  inputs, so they are always trustworthy.
- *Collect all violations per row, don't stop at the first.* A reject file that lists every problem lets
  the data owner fix the source once instead of re-running five times.
- *Rules are small pure functions that raise a typed `RuleError`.* One rule = one test table. New
  rules don't touch the pipeline.
- *Reject, don't "fix" silently.* Normalisation (trim, lower-case, map `usa` → `US`) is fine and
  documented. Guessing a value (a missing price → 0) is data corruption.
- *Idempotency.* Output depends only on the input bytes: sorted/deterministic writing, no timestamps
  inside data files, and the input's SHA-256 recorded in the report so you can prove which input
  produced which output. Running twice yields byte-identical files.
- *Atomic outputs.* Each output file is written to a temp name and `os.replace`d. A crash leaves the
  previous good output intact.
- *Duplicates are a pipeline decision, not a rule on one row.* They need state across rows, so they are
  handled in a separate `dedupe` step: keep first, flag later ones as `duplicate_key`.

### 7.4 Starter code (verified)

**`src/dqpipe/rules.py`**

```python
"""Field-level validation and normalisation. Pure functions: no I/O, no globals."""

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
COUNTRY_MAP = {
    "usa": "US",
    "united states": "US",
    "us": "US",
    "uk": "GB",
    "gb": "GB",
    "india": "IN",
    "in": "IN",
}
VALID_STATUS = {"new", "paid", "shipped", "cancelled"}


@dataclass(frozen=True, slots=True)
class Violation:
    field: str
    rule: str
    message: str


class RuleError(ValueError):
    def __init__(self, rule: str, message: str) -> None:
        super().__init__(message)
        self.rule = rule


def required(value: str | None) -> str:
    if value is None or not value.strip():
        raise RuleError("required", "value is missing")
    return value.strip()


def email(value: str) -> str:
    v = required(value).lower()
    if not EMAIL_RE.match(v):
        raise RuleError("email_format", f"invalid email: {value!r}")
    return v


def iso_date(value: str) -> date:
    try:
        return date.fromisoformat(required(value))
    except ValueError:
        raise RuleError("date_format", f"expected YYYY-MM-DD, got {value!r}") from None


def positive_int(value: str) -> int:
    try:
        n = int(required(value))
    except ValueError:
        raise RuleError("int_format", f"not an integer: {value!r}") from None
    if n <= 0:
        raise RuleError("range", f"must be > 0, got {n}")
    return n


def price(value: str) -> Decimal:
    try:
        d = Decimal(required(value))
    except InvalidOperation:
        raise RuleError("decimal_format", f"not a decimal: {value!r}") from None
    if not d.is_finite() or d < 0:
        raise RuleError("range", f"must be a finite number >= 0, got {value!r}")
    return d.quantize(Decimal("0.01"))


def country(value: str) -> str:
    key = required(value).lower()
    if key not in COUNTRY_MAP:
        raise RuleError("country_unknown", f"unmapped country: {value!r}")
    return COUNTRY_MAP[key]


def status(value: str) -> str:
    v = required(value).lower()
    if v not in VALID_STATUS:
        raise RuleError("status_domain", f"unexpected status: {value!r}")
    return v
```

**`src/dqpipe/pipeline.py`**

```python
import csv
import hashlib
import json
import os
from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any

from . import rules
from .rules import RuleError, Violation

SCHEMA: dict[str, Callable[[str], Any]] = {
    "order_id": rules.required,
    "customer_email": rules.email,
    "order_date": rules.iso_date,
    "country": rules.country,
    "quantity": rules.positive_int,
    "unit_price": rules.price,
    "status": rules.status,
}


@dataclass
class RowOutcome:
    line_no: int
    raw: dict[str, str]
    clean: dict[str, Any] | None = None
    violations: list[Violation] = field(default_factory=list)


def extract(path: Path) -> Iterator[tuple[int, dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as fh:  # utf-8-sig tolerates an Excel BOM
        reader = csv.DictReader(fh)
        missing = set(SCHEMA) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"input is missing columns: {sorted(missing)}")
        for line_no, row in enumerate(reader, start=2):  # header is line 1
            yield line_no, {k: (v or "") for k, v in row.items() if k is not None}


def validate(line_no: int, raw: dict[str, str]) -> RowOutcome:
    outcome = RowOutcome(line_no, raw)
    clean: dict[str, Any] = {}
    for name, rule in SCHEMA.items():
        try:
            clean[name] = rule(raw.get(name, ""))
        except RuleError as exc:
            outcome.violations.append(Violation(name, exc.rule, str(exc)))
    if not outcome.violations:
        outcome.clean = clean
    return outcome


def transform(clean: dict[str, Any]) -> dict[str, Any]:
    """Derive columns after validation, so derived values are always trustworthy."""
    out = dict(clean)
    out["order_total"] = (clean["unit_price"] * clean["quantity"]).quantize(Decimal("0.01"))
    out["order_month"] = clean["order_date"].strftime("%Y-%m")
    return out


def dedupe(outcomes: list[RowOutcome]) -> None:
    """Keep the first valid occurrence of each order_id; flag later ones as violations."""
    seen: set[str] = set()
    for o in outcomes:
        if o.clean is None:
            continue
        oid = o.clean["order_id"]
        if oid in seen:
            o.violations.append(Violation("order_id", "duplicate_key", f"duplicate order_id {oid}"))
            o.clean = None
        else:
            seen.add(oid)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_write_csv(path: Path, header: list[str], rows: Iterable[Iterable[Any]]) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    os.replace(tmp, path)


def _atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="")
    os.replace(tmp, path)


def run(input_path: Path, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    outcomes = [validate(n, r) for n, r in extract(input_path)]
    dedupe(outcomes)

    good = [transform(o.clean) for o in outcomes if o.clean is not None]
    bad = [o for o in outcomes if o.clean is None]

    cols = [*SCHEMA, "order_total", "order_month"]
    _atomic_write_csv(out_dir / "clean_orders.csv", cols, ([r[c] for c in cols] for r in good))
    _atomic_write_csv(
        out_dir / "rejects.csv",
        ["line_no", "field", "rule", "message"],
        ((o.line_no, v.field, v.rule, v.message) for o in bad for v in o.violations),
    )

    report = {
        "input_sha256": sha256_of(input_path),  # same input hash => same outputs (idempotent)
        "rows_read": len(outcomes),
        "rows_clean": len(good),
        "rows_rejected": len(bad),
        "reject_rate": round(len(bad) / len(outcomes), 4) if outcomes else 0.0,
        "violations_by_rule": dict(
            sorted(Counter(v.rule for o in bad for v in o.violations).items())
        ),
    }
    _atomic_write_text(
        out_dir / "quality_report.json", json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    return report
```

**`tests/test_pipeline.py`**

```python
from pathlib import Path

import pytest

from dqpipe import pipeline, rules

SAMPLE = """order_id,customer_email,order_date,country,quantity,unit_price,status
A1,Ann@Example.com,2026-02-01,usa,2,10.50,PAID
A2,bad-email,2026-02-02,UK,1,5,new
A3,bob@example.com,2026-13-40,India,1,5,new
A1,ann@example.com,2026-02-01,US,2,10.50,paid
A4,cy@example.com,2026-02-03,Mars,0,-1,lost
"""


def test_rules_normalise():
    assert rules.email(" Ann@Example.COM ") == "ann@example.com"
    assert rules.country("United States") == "US"
    with pytest.raises(rules.RuleError):
        rules.positive_int("0")


def test_run_end_to_end_and_idempotent(tmp_path: Path):
    src = tmp_path / "orders.csv"
    src.write_text(SAMPLE, encoding="utf-8")
    out = tmp_path / "out"
    report = pipeline.run(src, out)
    assert (report["rows_read"], report["rows_clean"], report["rows_rejected"]) == (5, 1, 4)
    first = (out / "clean_orders.csv").read_bytes()
    assert b"A1,ann@example.com,2026-02-01,US,2,10.50,paid,21.00,2026-02" in first
    assert report["violations_by_rule"]["duplicate_key"] == 1
    pipeline.run(src, out)  # second run must not change anything
    assert (out / "clean_orders.csv").read_bytes() == first
```

**What the skeleton deliberately leaves for you**

1. `cli.py` with `run`; exit `0` when the reject rate is within `--max-reject-rate`, `1` when it
   is exceeded (outputs are still written so a human can inspect them), `2` for usage errors, and a
   clear exit-1 message for a missing column or an unreadable file.
2. Move thresholds and the country mapping into a TOML config loaded with `tomllib` (`rb` mode) and
   validate that config at startup.
3. `report.py`: add the reject rate per rule, the first 5 example rejects per rule, and min/max/sum of `order_total`
   for the clean set.
4. A `--dry-run` mode that validates and reports without writing outputs.
5. A `rejects.csv` that also contains the *raw row* so analysts can see the original value.
6. Cross-field rules, e.g. a `cancelled` order must not be marked `paid` — and decide whether
   that is a row rule or a pipeline rule.
7. Replace the in-memory list with a streaming variant for the validate step and discuss what
   `dedupe` then costs (a `set` of seen keys is O(unique keys) memory).

### 7.5 Build order

| Milestone | Deliverable | Done when |
|---|---|---|
| M1 Contract | `data-contract.md`: columns, types, rules, normalisations, reject policy, sample good/bad rows | A teammate could implement it without asking you |
| M2 Rules | `rules.py` + parametrized test table per rule | Every rule has valid, invalid, empty and whitespace cases |
| M3 Row pipeline | `extract`, `validate`, `transform` + tests on 10-row fixtures | A row with 3 problems yields 3 violations |
| M4 Dedupe + outputs | `dedupe`, three output files, atomic writes | Golden-file comparison passes |
| M5 Idempotency | Run twice → identical bytes (test); report includes `input_sha256` | Test passes |
| M6 CLI + thresholds | `run`, `--max-reject-rate`, `--dry-run`, exit codes, TOML config | CLI tests pass |
| M7 Scale + docs | Generate 200k synthetic rows; time and memory check; README with before/after sample | Acceptance checklist passes |

### 7.6 Edge cases to test

UTF-8 BOM at file start (Excel) · extra whitespace everywhere · missing column vs extra column · empty input
(header only) · row with fewer fields than the header (`csv` pads with `None`) · quoted commas and embedded newlines ·
`unit_price` of `1e3`, `NaN`, `-0`, `10.999` (rounding! decide: reject or round, and write it in the contract) ·
quantity `2.0` · the same `order_id` differing only by case or surrounding space · impossible dates
(`2026-02-30`) · unknown country · the first duplicate is invalid but the second is valid
(which one wins? your `dedupe` currently skips invalid rows — is that right? document it).

### 7.7 Common mistakes

- Dropping bad rows without a reject file ("silent data loss").
- Computing derived columns before validating inputs.
- Using `float` for prices, or `Decimal(0.1)` instead of `Decimal("0.1")`.
- Stopping at the first error in a row.
- Writing a timestamp or a random run ID into the data, which makes reruns non-reproducible.
- Reading the whole file in memory and not saying so, or opening it without `utf-8-sig`.
- Hand-building CSV lines with `",".join(...)` — quoting breaks on commas and quotes. Always use the `csv` module.
- Putting `print` and file paths inside `rules.py`.

### 7.8 Stretch goals

Pluggable rule registry via a dict/decorator (Module 09/12) · per-column profiling (null %, distinct count,
min/max) · schema drift detection against the previous run's report · JSON Lines output · load the clean
file into SQLite and run three SQL sanity queries (Module 13) · compare quality reports between two runs and exit
non-zero if quality regressed.

### 7.9 Interview talking points

"I separate validation from transformation, keep rules as pure functions, and emit a reject file with
reasons so data owners can fix upstream." · "Reruns are idempotent: same input bytes, same output bytes,
and the report records the input hash." · "A reject-rate threshold turns data quality into an
enforceable gate rather than a hope."

---

## 8. Project 4 — Rule-Based Risk Review Engine

Brief: [`Projects/04-rule-based-risk-review-engine.md`](./Projects/04-rule-based-risk-review-engine.md)

### 8.1 What it is and why it matters

A small decision engine that reads transactions, applies a configurable set of risk rules, and
produces for each transaction a **score**, a **decision** (`approve` / `review` / `reject`) and the
**list of reasons** that led to it. Rule-based systems still sit in front of or beside ML models in
fraud, trust-and-safety, compliance and LLM-guardrail systems: they are cheap, deterministic and,
critically, *explainable and auditable*. Understanding them also teaches you what an ML model must
beat and how to design a baseline.

This is the capstone of Stage 1: it asks for design judgment (interfaces, configuration, state,
testing strategy) rather than just correctness.

### 8.2 Scope

In scope: transactions as a dataclass, a `Rule` protocol, three rule types (high amount, watch-list
country, velocity), scores and thresholds from a TOML file, decisions with reasons, an audit log of
decisions as JSON Lines, a CLI that reads a transactions CSV and writes a decisions file and a summary,
deterministic processing, golden-file tests. Out of scope: machine learning, real customer data,
databases, web services.

### 8.3 Requirements

| Area | Requirement |
|---|---|
| Rules | each rule returns a `RuleHit(rule_id, points, reason)` or `None`; rules are independent classes behind one `Protocol` |
| Scoring | score = sum of hit points; thresholds `review_at` and `reject_at` map the score to a decision; boundaries are **inclusive** (score == threshold triggers the higher decision) |
| Explainability | every decision lists all rules that fired with human-readable reasons |
| Configuration | rules, points and thresholds come from TOML; invalid config (duplicate rule IDs, unknown rule type, `review_at >= reject_at`, missing keys) fails at start-up with a clear error |
| State | the velocity rule keeps per-account state in a sliding window; input is processed in `(timestamp, txn_id)` order for determinism |
| Audit | one JSON Lines record per transaction: id, score, decision, hits, `config_sha256` |
| CLI | `riskreview assess --transactions t.csv --rules rules.toml --out decisions.jsonl` and a printed summary (counts by decision, top rules fired); exit 0, or 1 when any transaction was rejected if `--fail-on-reject` is given |

### 8.4 Architecture

```text
src/riskreview/
├── models.py   # Transaction, RuleHit, Assessment (frozen dataclasses) + Decision (Enum)
├── rules.py    # Rule Protocol + HighAmountRule, HighRiskCountryRule, VelocityRule
├── engine.py   # Thresholds, RiskEngine, build_engine(config) — the only place that knows concrete rule classes
├── io.py       # (your task) read transactions CSV → Transaction (validation) ; write decisions JSONL atomically
└── cli.py      # (your task) argparse wiring and exit codes
```

Layering (dependencies point **downwards only**; `models` imports nothing from the project):

```text
cli ──► io ──► models
 └────► engine ──► rules ──► models
```

**Key decisions to be able to defend**

- *`Protocol` instead of an abstract base class.* Rules need only `rule_id` and `evaluate`;
  structural typing keeps rules decoupled and trivial to fake in tests.
- *Immutable models, mutable rule state.* Values (`Transaction`, `RuleHit`) never change. The only
  mutable thing — the velocity window — is private to the rule instance, which makes the stateful
  part easy to find and reason about. Corollary: **a stateful engine is not re-runnable**; build a new
  engine per run (or give rules a `reset()`), and say so in the README.
- *Configuration over code, but no `eval`.* Rules are selected by a `type` string through an explicit
  `if/elif` factory. Arbitrary expressions in config (`eval`) would be a code-injection vulnerability and
  are unnecessary here. The factory is the extension point; registering types in a dict is the stretch
  version.
- *Determinism.* Sort the input by `(timestamp, txn_id)`, apply rules in configuration order, never
  consult wall-clock time.
- *Explainability is a requirement, not a feature.* The `Assessment` carries every hit; the audit log
  is the evidence for later disputes.
- *Fail fast on configuration.* `Thresholds.__post_init__` and the duplicate-ID check make an invalid
  config impossible to run with.

### 8.5 Starter code (verified)

**`src/riskreview/models.py`**

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Decision(Enum):
    APPROVE = "approve"
    REVIEW = "review"
    REJECT = "reject"


@dataclass(frozen=True, slots=True)
class Transaction:
    txn_id: str
    account_id: str
    amount_cents: int
    country: str
    timestamp: datetime  # timezone-aware UTC
    merchant_category: str = "general"


@dataclass(frozen=True, slots=True)
class RuleHit:
    rule_id: str
    points: int
    reason: str


@dataclass(frozen=True, slots=True)
class Assessment:
    txn_id: str
    score: int
    decision: Decision
    hits: tuple[RuleHit, ...] = field(default_factory=tuple)
```

**`src/riskreview/rules.py`**

```python
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from .models import RuleHit, Transaction


class Rule(Protocol):
    rule_id: str

    def evaluate(self, txn: Transaction) -> RuleHit | None: ...


@dataclass
class HighAmountRule:
    rule_id: str
    threshold_cents: int
    points: int

    def evaluate(self, txn: Transaction) -> RuleHit | None:
        if txn.amount_cents >= self.threshold_cents:
            return RuleHit(
                self.rule_id, self.points, f"amount {txn.amount_cents} >= {self.threshold_cents}"
            )
        return None


@dataclass
class HighRiskCountryRule:
    rule_id: str
    countries: frozenset[str]
    points: int

    def evaluate(self, txn: Transaction) -> RuleHit | None:
        if txn.country in self.countries:
            return RuleHit(self.rule_id, self.points, f"country {txn.country} is on the watch list")
        return None


class VelocityRule:
    """Stateful: too many transactions on one account inside a sliding window.

    Assumes transactions arrive in timestamp order. State lives in the rule instance,
    so build a fresh engine per run to keep results reproducible.
    """

    def __init__(self, rule_id: str, max_count: int, window_seconds: int, points: int) -> None:
        self.rule_id = rule_id
        self.max_count = max_count
        self.window = timedelta(seconds=window_seconds)
        self.points = points
        self._seen: dict[str, deque[datetime]] = defaultdict(deque)

    def evaluate(self, txn: Transaction) -> RuleHit | None:
        q = self._seen[txn.account_id]
        q.append(txn.timestamp)
        while txn.timestamp - q[0] > self.window:
            q.popleft()
        if len(q) > self.max_count:
            return RuleHit(
                self.rule_id, self.points, f"{len(q)} transactions within {self.window.seconds}s"
            )
        return None
```

**`src/riskreview/engine.py`**

```python
import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .models import Assessment, Decision, Transaction
from .rules import HighAmountRule, HighRiskCountryRule, Rule, VelocityRule


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Thresholds:
    review_at: int
    reject_at: int

    def __post_init__(self) -> None:
        if not 0 < self.review_at < self.reject_at:
            raise ConfigError("need 0 < review_at < reject_at")

    def decide(self, score: int) -> Decision:
        if score >= self.reject_at:
            return Decision.REJECT
        if score >= self.review_at:
            return Decision.REVIEW
        return Decision.APPROVE


class RiskEngine:
    def __init__(self, rules: list[Rule], thresholds: Thresholds) -> None:
        ids = [r.rule_id for r in rules]
        if len(ids) != len(set(ids)):
            raise ConfigError("duplicate rule_id in configuration")
        self._rules = rules
        self._thresholds = thresholds

    def assess(self, txn: Transaction) -> Assessment:
        hits = tuple(h for rule in self._rules if (h := rule.evaluate(txn)) is not None)
        score = sum(h.points for h in hits)
        return Assessment(txn.txn_id, score, self._thresholds.decide(score), hits)

    def assess_all(self, txns: Iterable[Transaction]) -> list[Assessment]:
        return [self.assess(t) for t in sorted(txns, key=lambda t: (t.timestamp, t.txn_id))]


def build_engine(config_path: Path) -> RiskEngine:
    with config_path.open("rb") as fh:  # tomllib requires binary mode
        cfg = tomllib.load(fh)
    rules: list[Rule] = []
    try:
        for entry in cfg["rules"]:
            kind = entry["type"]
            if kind == "high_amount":
                rules.append(HighAmountRule(entry["id"], entry["threshold_cents"], entry["points"]))
            elif kind == "country":
                rules.append(
                    HighRiskCountryRule(entry["id"], frozenset(entry["countries"]), entry["points"])
                )
            elif kind == "velocity":
                rules.append(
                    VelocityRule(
                        entry["id"], entry["max_count"], entry["window_seconds"], entry["points"]
                    )
                )
            else:
                raise ConfigError(f"unknown rule type: {kind!r}")
        t = cfg["thresholds"]
        return RiskEngine(rules, Thresholds(t["review_at"], t["reject_at"]))
    except KeyError as exc:
        raise ConfigError(f"missing config key: {exc}") from None
```

**`tests/test_engine.py`**

```python
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from riskreview.engine import ConfigError, build_engine
from riskreview.models import Decision, Transaction

CONFIG = """
[thresholds]
review_at = 40
reject_at = 80

[[rules]]
id = "R1_HIGH_AMOUNT"
type = "high_amount"
threshold_cents = 500000
points = 40

[[rules]]
id = "R2_WATCH_COUNTRY"
type = "country"
countries = ["XX", "YY"]
points = 30

[[rules]]
id = "R3_VELOCITY"
type = "velocity"
max_count = 2
window_seconds = 60
points = 50
"""
T0 = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)


def txn(i, amount=1000, country="US", secs=0, account="acc1"):
    return Transaction(f"t{i}", account, amount, country, T0 + timedelta(seconds=secs))


@pytest.fixture
def engine(tmp_path: Path):
    cfg = tmp_path / "rules.toml"
    cfg.write_text(CONFIG, encoding="utf-8")
    return build_engine(cfg)


def test_boundaries_and_reasons(engine):
    ok = engine.assess(txn(1, account="a1"))
    assert (ok.score, ok.decision) == (0, Decision.APPROVE)
    big = engine.assess(txn(2, amount=500000, account="a2"))  # exactly on the threshold counts
    assert (big.score, big.decision) == (40, Decision.REVIEW)
    both = engine.assess(txn(3, amount=500000, country="XX", account="a3"))
    assert [h.rule_id for h in both.hits] == ["R1_HIGH_AMOUNT", "R2_WATCH_COUNTRY"]
    assert both.decision is Decision.REVIEW  # 70 < 80


def test_velocity_is_stateful_and_deterministic(engine):
    results = engine.assess_all([txn(i, secs=i * 10) for i in range(4)])
    assert [r.score for r in results] == [0, 0, 50, 50]


def test_bad_config_fails_fast(tmp_path):
    bad = tmp_path / "bad.toml"
    bad.write_text(
        '[thresholds]\nreview_at = 90\nreject_at = 10\n[[rules]]\nid="a"\ntype="nope"\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError):
        build_engine(bad)
```

A matching `rules.toml` (this is the exact configuration the tests use):

```toml
[thresholds]
review_at = 40
reject_at = 80

[[rules]]
id = "R1_HIGH_AMOUNT"
type = "high_amount"
threshold_cents = 500000      # 5,000.00
points = 40

[[rules]]
id = "R2_WATCH_COUNTRY"
type = "country"
countries = ["XX", "YY"]      # placeholder codes; use synthetic ones
points = 30

[[rules]]
id = "R3_VELOCITY"
type = "velocity"
max_count = 2
window_seconds = 60
points = 50
```

**What the skeleton deliberately leaves for you**

1. `io.py`: read a transactions CSV with the Project 1/3 habits (validate every row, reject-and-report
   bad rows, integer cents, aware-UTC timestamps) and write `decisions.jsonl` atomically, one JSON
   object per line with `sort_keys=True`.
2. `cli.py` with the `assess` command, the summary, `--fail-on-reject`, and exit codes.
3. `config_sha256` in each audit record (hash the TOML bytes) so every decision can be traced to the exact
   configuration that produced it.
4. A fourth rule you design yourself, for example *amount just under a reporting limit* ("structuring"),
   *first transaction on a new account*, or *merchant-category risk*. Write its tests first.
5. **Golden-file test:** a 30-row synthetic transactions file with a hand-computed
   `expected_decisions.jsonl`; the test runs the engine and compares text. Update the golden file only
   deliberately, with a commit message that explains why a decision changed.
6. Unordered-input guard: `VelocityRule` assumes timestamps never go backwards, which `assess_all`
   guarantees by sorting. Add a test showing what would go wrong without that sort, and decide whether `assess`
   should raise on out-of-order input.
7. Memory: the velocity state grows with the number of accounts. Evict empty queues and discuss the trade-off.

### 8.6 Build order

| Milestone | Deliverable | Done when |
|---|---|---|
| M1 Design | `design.md`: rule catalogue (id, intent, formula, points, boundary behaviour), decision table, class diagram in text | Every rule has an explicit boundary statement |
| M2 Models + rules | `models.py`, three rules, per-rule parametrized tests incl. exact-threshold cases | Boundary tests pass |
| M3 Engine | `Thresholds`, `RiskEngine`, hit ordering, decision mapping | Score → decision table fully tested |
| M4 Configuration | `build_engine` with all failure modes tested (missing key, unknown type, duplicate ids, bad thresholds, bad TOML syntax) | Every error is a `ConfigError` with a clear message |
| M5 I/O + CLI | `io.py`, `cli.py`, JSONL audit log with `config_sha256` | End-to-end CLI test passes |
| M6 Golden + regression tests | 30-row golden file, determinism test (run twice → same bytes), shuffled-input test (same result) | All pass |
| M7 Review + docs | Your own review pass (see 9.4), README with rule catalogue and an example decision explained line by line | Acceptance checklist passes |

### 8.7 Edge cases to test

Score exactly equal to each threshold · zero rules fired · all rules fired · amount exactly on the threshold ·
velocity: `max_count` events vs `max_count + 1`, events exactly `window` apart, events from two accounts interleaved ·
same timestamp for several transactions (tie-break by `txn_id`) · a country in lower case or with whitespace
(normalise at input, not inside the rule) · negative or zero amount (reject at input) · empty rules list
(everything approved — valid?) · empty `countries` list · points of zero or negative · extremely large point values.

### 8.8 Common mistakes

- Leaving the concrete rule classes scattered through the code instead of confining them to the factory.
- Rules that mutate the transaction or read global state or the system clock.
- Off-by-one on boundaries (`>` versus `>=`) with no test that pins it.
- A stateful rule with a shared module-level dictionary: tests then pass or fail depending on order.
- Returning only a score, with no reasons — the decision cannot be explained to a customer or auditor.
- Using `eval` for "flexible" rule expressions.
- Using a float for amounts, or comparing aware to naive datetimes.
- Changing a rule's points and not noticing which historical decisions change — hence golden files and `config_sha256`.

### 8.9 Stretch goals

A rule registry using `__init_subclass__` or a decorator (Modules 12, 20) · `Enum`-based severity
(Module 09) · what-if comparison of two configurations over the same transactions (how many decisions
change?) · precision/recall style evaluation against a labelled synthetic set (a first look at
how ML evaluation works in Stage 5) · a `--explain <txn_id>` command · property-based or fuzz-style test
that the engine never raises on random valid transactions (Module 16).

### 8.10 Interview talking points

"Each rule is an independent unit behind a Protocol, the engine only composes them, and a factory
builds them from validated TOML — so adding a rule never touches the engine." · "Decisions are
deterministic and carry reasons plus the config hash, which makes them auditable." · "Velocity is a
sliding window held in a deque per account; it is the only mutable state and I isolated it." · "Golden-file
tests tell me exactly which decisions changed when someone edits a threshold."

---

## 9. Cross-project practices

### 9.1 How the four projects connect

| Concept | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| Validated input at the boundary | `money.py` | `parse_line` | `rules.py` | `io.py`, `Thresholds` |
| Pure core, thin CLI | ✔ | ✔ | ✔ | ✔ |
| Atomic file writes | ledger CSV | report files | all outputs | `decisions.jsonl` |
| Idempotency / determinism | content-hash ID | seeded generator | input hash, sorted output | sorted input, config hash |
| Errors as data (counted/reported) | import rejects | malformed lines | reject file | rejected config / rows |
| Time handling | dates | aware-UTC timestamps, windows | order dates | aware-UTC, velocity window |
| Test style | unit + CLI | unit + planted incident | table-driven + golden | boundary + golden |

### 9.2 Debugging protocol (Module 07 in practice)

When something fails: reproduce with the smallest input → read the traceback bottom to top → state a
hypothesis → test it with one change (`print`/logging or the debugger with a breakpoint) → write the
regression test → fix → run the quality gate → record it in `learning-notes.md`. Never "fix" by
re-running or by wrapping the failing line in `try/except`.

### 9.3 Performance sanity (measure, don't guess)

Each project gets one scale check, using synthetic data: P1 10 000 expenses, P2 1 M log lines, P3 200 k
rows, P4 100 k transactions. Record wall time and peak memory (`/usr/bin/time -v`). If a number looks
bad, profile with `cProfile` (Module 17) **before** changing code. Write down what you measured and
what you concluded.

### 9.4 Self code-review checklist (do this before marking a project finished)

- Does every function do one thing, and can I name it with a verb phrase?
- Is any function longer than ~30 lines or nested deeper than three levels? Split it.
- Are all inputs validated at the boundary, and all outputs deterministic?
- Is there any `float` money, naive datetime, bare `except`, mutable default, or global state?
- Does every public function have a type signature and a one-line docstring saying what, not how?
- Do the error messages tell a user what to do next?
- Are there tests for each boundary I named in my design notes?
- Could I explain this project's three most important design decisions in two minutes?

### 9.5 Security and privacy hygiene

Synthetic data only. No secrets or personal data in Git. Treat every input file as untrusted:
size-limit and validate it, never `eval`/`exec`/`pickle.load` it, and build file paths with `pathlib`
(do not concatenate user text into paths or shell commands). See Module 22 for depth.

---

## 10. Parallel interview preparation

Do not grind algorithm puzzles yet (Stage 3). Practise explaining engineering decisions in 60–90 seconds:

1. Why not `float` for money, and what do you use instead?
2. What does "idempotent" mean for a batch job, and how did you achieve it?
3. How do you process a file larger than memory?
4. What is the difference between a unit test and an integration test, and where did you use each?
5. Why does the CLI return different exit codes?
6. How do you handle a malformed row — and when should you stop the whole run?
7. Why write to a temp file and then `os.replace`?
8. How would you add a new rule/validation to your pipeline without editing existing code?
9. What breaks if two instances run at the same time? How would you fix it?
10. Walk me through the last bug you found, how you reproduced it and what test now guards it.

For each project, prepare a **Problem → approach → evidence → result → what I learned** summary and keep
one diagram (the data-flow sketches in this plan are a good start).

---

## 11. Stage 1 completion gate

You have completed Stage 1 when all statements are true:

- [ ] I studied modules 01–11 and used 24 as a gap-filler; the remaining modules are bookmarked for reference.
- [ ] **Project 1:** the ledger CLI is installable, validated, atomic, tested and documented.
- [ ] **Project 2:** the log tool streams large files, reports malformed input, finds the planted incident, and has JSON + text output.
- [ ] **Project 3:** the pipeline produces clean/reject/report outputs, is byte-for-byte idempotent, and enforces a reject-rate gate.
- [ ] **Project 4:** the engine is config-driven, explainable, deterministic, covered by golden-file tests, and has a rule I designed myself.
- [ ] For every project the quality gate (ruff, mypy `--strict`, pytest) passes on a clean clone.
- [ ] Every project README has real sample output and honest limitations.
- [ ] Each project has a `learning-notes.md` with at least three recorded mistakes and their fixes.
- [ ] I can explain each project's design in two minutes without notes and answer the ten questions in Section 10.
- [ ] All four projects are committed to Git, tagged, and pushed to a GitHub repository.

If a box is unchecked, practise that specific item. When the gate is met, proceed to
**Stage 2 — Python for Data Engineering**, where pandas, SQL, Arrow and orchestration build directly on
the habits you formed here.

## Notes

- Do not skip ahead: each project assumes the habits (tests, atomic writes, validation, exit codes) of
  the previous one.
- The starter code is a *reference skeleton*. Type it out, run it, break it on purpose, then extend it.
  Copy-pasting it and moving on gives you no learning and no interview material.
- The files in `Projects/` define what to deliver; this plan defines how to build and check it.
- Keep scope small. A smaller project that is correct, tested and documented is worth more than a
  large one that is not.
