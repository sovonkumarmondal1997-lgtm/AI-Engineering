"""Input validation and deterministic, atomic decision output."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import Assessment, Transaction

REQUIRED_COLUMNS = ("txn_id", "account_id", "amount_cents", "country", "timestamp")
OPTIONAL_COLUMNS = ("merchant_category",)
ALL_COLUMNS = set(REQUIRED_COLUMNS) | set(OPTIONAL_COLUMNS)


class InputError(ValueError):
    """Input CSV violates the transaction contract."""


def parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        raise InputError(f"invalid ISO-8601 timestamp {value!r}") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise InputError("timestamp must include a timezone offset or Z")
    return parsed.astimezone(timezone.utc)


def read_transactions(path: Path) -> list[Transaction]:
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle, strict=True)
            header = reader.fieldnames
            if header is None:
                raise InputError("transactions CSV is empty and has no header")
            if len(header) != len(set(header)):
                raise InputError("duplicate CSV column names")
            missing = sorted(set(REQUIRED_COLUMNS) - set(header))
            extra = sorted(set(header) - ALL_COLUMNS)
            if missing:
                raise InputError(f"missing required columns: {', '.join(missing)}")
            if extra:
                raise InputError(f"unexpected columns: {', '.join(extra)}")
            txns: list[Transaction] = []
            ids: set[str] = set()
            for row_number, row in enumerate(reader, start=2):
                if None in row or any(value is None for value in row.values()):
                    raise InputError(f"record {row_number}: wrong number of CSV fields")
                txn_id = (row.get("txn_id") or "").strip()
                if txn_id in ids:
                    raise InputError(f"record {row_number}: duplicate txn_id {txn_id!r}")
                ids.add(txn_id)
                amount_text = (row.get("amount_cents") or "").strip()
                if not amount_text.isascii() or not amount_text.isdigit():
                    raise InputError(f"record {row_number}: amount_cents must be a non-negative integer")
                amount = int(amount_text)
                txns.append(Transaction(
                    txn_id=txn_id,
                    account_id=(row.get("account_id") or "").strip(),
                    amount_cents=amount,
                    country=(row.get("country") or "").strip(),
                    timestamp=parse_timestamp(row.get("timestamp") or ""),
                    merchant_category=(row.get("merchant_category") or "general").strip() or "general",
                ))
            return txns
    except csv.Error as exc:
        raise InputError(f"malformed CSV: {exc}") from None
    except OSError as exc:
        raise InputError(f"cannot read input {path}: {exc}") from None


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
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


def write_decisions(path: Path, assessments: Iterable[Assessment], config_sha256: str) -> None:
    lines: list[str] = []
    for assessment in assessments:
        record: dict[str, Any] = {
            "txn_id": assessment.txn_id,
            "score": assessment.score,
            "decision": assessment.decision.value,
            "hits": [
                {"rule_id": hit.rule_id, "points": hit.points, "reason": hit.reason}
                for hit in assessment.hits
            ],
            "config_sha256": config_sha256,
        }
        lines.append(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    _atomic_write(path, "".join(line + "\n" for line in lines))
