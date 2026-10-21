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
