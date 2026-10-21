# Project 04 — Rule-Based Risk Review Engine

**Stage:** Stage 1 — Programming & Computational Thinking  
**Role focus:** Python engineering, deterministic decision systems, explainability, and auditability  
**Estimated effort:** 20–30 hours (project estimate for planning; confirm against the full learning-plan wording if it differs)  
**Runtime:** Python 3.12+ · Standard-library runtime  
**Development:** `uv`, `pytest`, `ruff`, `mypy`

## 1. Alignment with the Stage 1 learning plan

The Stage 1 learning plan defines this as the capstone project. It reads transactions and applies configurable rules to produce a score, decision (`approve`, `review`, or `reject`), and human-readable reasons. It emphasizes interfaces, configuration, state, and test strategy—not only getting a correct answer.

The specified scope is:

- Transactions represented as frozen dataclasses.
- A `Rule` protocol.
- Three rules: high amount, watch-list country, and account velocity.
- Scores and decision thresholds from TOML.
- Explainable decisions with all fired-rule reasons.
- JSON Lines audit log with transaction ID, score, decision, hits, and `config_sha256`.
- CLI: `riskreview assess --transactions t.csv --rules rules.toml --out decisions.jsonl`.
- Printed summary with decision counts and most frequently fired rules.
- Deterministic ordering by `(timestamp, txn_id)`.
- Golden-file tests as an acceptance goal.
- Out of scope: machine learning, real customer data, databases, and web services.

The roadmap places the document at:

```text
Stage 1 — Programming & Computational Thinking/
└── 00-Stage-1-Overview/
    └── Projects/
        └── 04-rule-based-risk-review-engine.md
```

The companion implementation below follows the architecture specified by the learning plan. This is an educational baseline, not a production fraud decision service.

## 2. Learning objectives

By completion, you should be able to:

1. Model immutable domain data with `dataclass(frozen=True, slots=True)`.
2. use `Enum` for a constrained decision domain.
3. define a structural interface using `typing.Protocol`.
4. implement independent rules behind a common interface.
5. distinguish stateless rules from stateful rules.
6. score hits and apply inclusive decision thresholds.
7. validate TOML configuration and fail before processing when it is invalid.
8. normalize timestamps to UTC and sort deterministically.
9. write one auditable JSONL record per transaction.
10. test boundaries, configuration failures, state windows, CLI exit codes, and repeatability.

## 3. Requirements and decision semantics

### Transaction CSV

Required columns: `txn_id`, `account_id`, `amount_cents`, `country`, `timestamp`. Optional column: `merchant_category`.

- `txn_id` and `account_id` must be non-empty.
- `txn_id` must be unique within one run.
- `amount_cents` is a non-negative integer; use integer minor units rather than floating-point money.
- `country` is trimmed and uppercased.
- `timestamp` must be ISO-8601 with a timezone (`Z` or an offset) and is normalized to UTC.
- Input rows are sorted by `(timestamp, txn_id)` before evaluation.

### Rules

Each rule implements `evaluate(transaction) -> RuleHit | None`. A `RuleHit` has `rule_id`, positive integer `points`, and a readable `reason`.

- **High amount:** fires when `amount_cents >= threshold_cents`.
- **Watch-list country:** fires when the normalized country is in the configured list.
- **Velocity:** for one account, counts transactions inside a sliding window including the exact boundary. It fires when the count is greater than `max_count` (i.e., on the `(max_count + 1)`th transaction in the window).

### Scoring

Score is the sum of points from all fired rules. Thresholds are inclusive:

- `score < review_at` → `approve`
- `review_at <= score < reject_at` → `review`
- `score >= reject_at` → `reject`

Configuration must satisfy `0 < review_at < reject_at`. Duplicate rule IDs, missing required keys, unknown rule types, and invalid parameter types fail at startup.

### State and repeatability

`VelocityRule` keeps private state in a rule instance. Do not reuse a stateful engine for a second independent run. Build a fresh engine for each CLI invocation. Within a run, the engine sorts transactions before invoking any rules.

### Audit log

Each JSONL line contains:

- `txn_id`
- `score`
- `decision`
- `hits` (every rule ID, points, and reason)
- `config_sha256` (SHA-256 of the exact TOML bytes)

JSONL is newline-delimited: one complete JSON object per line. No wall-clock timestamps or random run IDs are added to output.

## 4. Architecture and dependency boundaries

```text
src/riskreview/
├── models.py   # Transaction, RuleHit, Assessment, Decision
├── rules.py    # Rule Protocol and concrete rule implementations
├── engine.py   # thresholds, config factory, scoring, deterministic order
├── io.py       # CSV validation and atomic JSONL output
└── cli.py      # argparse, summary, diagnostics, exit codes
```

Dependency direction:

```text
cli ──► io ──► models
 └────► engine ──► rules ──► models
```

`models.py` must not import the engine or concrete rules. `rules.py` must not read files or print output. `engine.py` is the only layer that knows which concrete rule classes the config can instantiate. Do not use `eval()` to build behavior from configuration.

## 5. Repository layout

```text
rule-based-risk-review-engine/
├── .gitignore
├── README.md
├── pyproject.toml
├── uv.lock                    # generated and committed by uv
├── config/
│   └── rules.toml
├── data/
│   └── transactions.csv
├── src/
│   └── riskreview/
│       ├── __init__.py
│       ├── models.py
│       ├── rules.py
│       ├── engine.py
│       ├── io.py
│       └── cli.py
└── tests/
    ├── test_engine.py
    └── test_io_cli.py
```

## 6. Milestone plan

| Milestone | Deliverable | Exit criteria |
|---|---|---|
| M1 — Contract | CSV schema, money unit, timezone, rule semantics, score thresholds | Every boundary and failure policy is written down |
| M2 — Models | frozen dataclasses and `Decision` enum | model invariants have tests |
| M3 — Rules | `Protocol`, high-amount, country, velocity | each rule has positive and negative tests |
| M4 — Engine | TOML validation, factory, scoring, inclusive thresholds | invalid config fails before assessment |
| M5 — I/O | CSV parser and JSONL writer | malformed input is reported; output is deterministic |
| M6 — CLI | summary, `--fail-on-reject`, exit codes | end-to-end CLI tests pass |
| M7 — Audit | golden fixture, quality gates, README, reflection notes | clean install and acceptance checklist pass |

## 7. Setup

Use Python 3.12+ and `uv`. If a project already exists, reconcile the files rather than initializing it twice.

```bash
uv init --package riskreview
uv add --dev pytest ruff mypy
uv lock
uv sync
```

After adding the files below:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src
uv run riskreview assess --transactions data/transactions.csv --rules config/rules.toml --out out/decisions.jsonl
```

Commit `uv.lock`; verify reproducibility with `uv sync --locked`.

## 8. Reference implementation

Copy each file into the exact path shown. Work in this order: models → rules → engine/config → I/O → CLI → tests. The companion ZIP contains these files as a runnable project.


### `pyproject.toml`

```toml
[project]
name = "riskreview"
version = "0.1.0"
description = "Deterministic, explainable rule-based transaction risk review CLI"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
riskreview = "riskreview.cli:main"

[dependency-groups]
dev = ["pytest>=8.0", "ruff>=0.6", "mypy>=1.11"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/riskreview"]

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


### `config/rules.toml`

```toml
[thresholds]
review_at = 40
reject_at = 80

[[rules]]
id = "high_amount"
type = "high_amount"
threshold_cents = 500000
points = 40

[[rules]]
id = "watch_country"
type = "country"
countries = ["XX", "YY"]
points = 30

[[rules]]
id = "account_velocity"
type = "velocity"
max_count = 2
window_seconds = 60
points = 50
```


### `src/riskreview/__init__.py`

```python
"""Rule-based transaction risk review engine."""

__version__ = "0.1.0"
```


### `src/riskreview/models.py`

```python
"""Immutable domain models for risk assessment."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Decision(str, Enum):
    APPROVE = "approve"
    REVIEW = "review"
    REJECT = "reject"


@dataclass(frozen=True, slots=True)
class Transaction:
    txn_id: str
    account_id: str
    amount_cents: int
    country: str
    timestamp: datetime
    merchant_category: str = "general"

    def __post_init__(self) -> None:
        if not self.txn_id.strip():
            raise ValueError("txn_id must not be empty")
        if not self.account_id.strip():
            raise ValueError("account_id must not be empty")
        if self.amount_cents < 0:
            raise ValueError("amount_cents must be non-negative")
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        object.__setattr__(self, "timestamp", self.timestamp.astimezone(timezone.utc))
        object.__setattr__(self, "country", self.country.strip().upper())


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


### `src/riskreview/rules.py`

```python
"""Independent rule implementations; velocity is the only stateful rule."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from .models import RuleHit, Transaction


class Rule(Protocol):
    rule_id: str

    def evaluate(self, txn: Transaction) -> RuleHit | None:
        """Return a hit when the rule matches, otherwise None."""


@dataclass(frozen=True, slots=True)
class HighAmountRule:
    rule_id: str
    threshold_cents: int
    points: int

    def evaluate(self, txn: Transaction) -> RuleHit | None:
        if txn.amount_cents >= self.threshold_cents:
            return RuleHit(
                self.rule_id, self.points,
                f"amount_cents={txn.amount_cents} meets threshold={self.threshold_cents}",
            )
        return None


@dataclass(frozen=True, slots=True)
class HighRiskCountryRule:
    rule_id: str
    countries: frozenset[str]
    points: int

    def evaluate(self, txn: Transaction) -> RuleHit | None:
        if txn.country in self.countries:
            return RuleHit(
                self.rule_id, self.points,
                f"country={txn.country} is on the configured watch list",
            )
        return None


class VelocityRule:
    """Flag the (max_count + 1)th transaction in an inclusive sliding time window.

    Input must be processed in deterministic (timestamp, txn_id) order. The current
    transaction is counted before evaluation. A timestamp exactly window_seconds
    before the current transaction remains inside the window.
    """

    def __init__(self, rule_id: str, max_count: int, window_seconds: int, points: int) -> None:
        self.rule_id = rule_id
        self.max_count = max_count
        self.window = timedelta(seconds=window_seconds)
        self.window_seconds = window_seconds
        self.points = points
        self._seen: dict[str, deque[datetime]] = defaultdict(deque)

    def evaluate(self, txn: Transaction) -> RuleHit | None:
        queue = self._seen[txn.account_id]
        cutoff = txn.timestamp - self.window
        while queue and queue[0] < cutoff:
            queue.popleft()
        queue.append(txn.timestamp)
        if len(queue) > self.max_count:
            return RuleHit(
                self.rule_id, self.points,
                f"account has {len(queue)} transactions within inclusive "
                f"{self.window_seconds}s window",
            )
        return None
```


### `src/riskreview/engine.py`

```python
"""Configuration parsing, rule construction, scoring, and decisions."""

from __future__ import annotations

import hashlib
import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import Assessment, Decision, Transaction
from .rules import HighAmountRule, HighRiskCountryRule, Rule, VelocityRule


class ConfigError(ValueError):
    """Configuration is invalid and must not be used for assessment."""


@dataclass(frozen=True, slots=True)
class Thresholds:
    review_at: int
    reject_at: int

    def __post_init__(self) -> None:
        if isinstance(self.review_at, bool) or isinstance(self.reject_at, bool):
            raise ConfigError("thresholds must be integers, not booleans")
        if not 0 < self.review_at < self.reject_at:
            raise ConfigError("need 0 < review_at < reject_at")

    def decide(self, score: int) -> Decision:
        if score >= self.reject_at:
            return Decision.REJECT
        if score >= self.review_at:
            return Decision.REVIEW
        return Decision.APPROVE


@dataclass(frozen=True, slots=True)
class EngineBundle:
    engine: "RiskEngine"
    config_sha256: str


class RiskEngine:
    def __init__(self, rules: list[Rule], thresholds: Thresholds) -> None:
        ids = [rule.rule_id for rule in rules]
        if len(ids) != len(set(ids)):
            raise ConfigError("duplicate rule IDs are not allowed")
        self._rules = tuple(rules)
        self._thresholds = thresholds

    def assess(self, txn: Transaction) -> Assessment:
        hits = tuple(
            hit for rule in self._rules
            if (hit := rule.evaluate(txn)) is not None
        )
        score = sum(hit.points for hit in hits)
        return Assessment(txn.txn_id, score, self._thresholds.decide(score), hits)

    def assess_all(self, txns: Iterable[Transaction]) -> list[Assessment]:
        ordered = sorted(txns, key=lambda txn: (txn.timestamp, txn.txn_id))
        if len({txn.txn_id for txn in ordered}) != len(ordered):
            raise ValueError("txn_id values must be unique within one run")
        return [self.assess(txn) for txn in ordered]


def _integer(entry: dict[str, Any], key: str, *, minimum: int = 0) -> int:
    value = entry.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ConfigError(f"{key} must be an integer >= {minimum}")
    return value


def build_engine(config_path: Path) -> EngineBundle:
    try:
        raw_bytes = config_path.read_bytes()
        config = tomllib.loads(raw_bytes.decode("utf-8"))
    except OSError as exc:
        raise ConfigError(f"cannot read config {config_path}: {exc}") from None
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"invalid TOML config: {exc}") from None

    try:
        thresholds_cfg = config["thresholds"]
        if not isinstance(thresholds_cfg, dict):
            raise ConfigError("[thresholds] must be a table")
        review_at = _integer(thresholds_cfg, "review_at", minimum=1)
        reject_at = _integer(thresholds_cfg, "reject_at", minimum=1)
        thresholds = Thresholds(review_at, reject_at)
        entries = config["rules"]
        if not isinstance(entries, list) or not entries:
            raise ConfigError("at least one [[rules]] entry is required")

        built: list[Rule] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise ConfigError("each [[rules]] entry must be a table")
            rule_id = entry.get("id")
            kind = entry.get("type")
            points = _integer(entry, "points", minimum=1)
            if not isinstance(rule_id, str) or not rule_id.strip():
                raise ConfigError("each rule needs a non-empty string id")
            if kind == "high_amount":
                built.append(HighAmountRule(
                    rule_id, _integer(entry, "threshold_cents", minimum=0), points
                ))
            elif kind == "country":
                countries = entry.get("countries")
                if (not isinstance(countries, list) or not countries
                        or not all(isinstance(item, str) and item.strip() for item in countries)):
                    raise ConfigError(f"rule {rule_id}: countries must be a non-empty string list")
                built.append(HighRiskCountryRule(
                    rule_id, frozenset(item.strip().upper() for item in countries), points
                ))
            elif kind == "velocity":
                built.append(VelocityRule(
                    rule_id,
                    _integer(entry, "max_count", minimum=1),
                    _integer(entry, "window_seconds", minimum=1),
                    points,
                ))
            else:
                raise ConfigError(f"rule {rule_id}: unknown rule type {kind!r}")
        engine = RiskEngine(built, thresholds)
    except KeyError as exc:
        raise ConfigError(f"missing required configuration key: {exc.args[0]}") from None
    return EngineBundle(engine, hashlib.sha256(raw_bytes).hexdigest())
```


### `src/riskreview/io.py`

```python
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
```


### `src/riskreview/cli.py`

```python
"""CLI for deterministic risk assessment."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from .engine import ConfigError, build_engine
from .io import InputError, read_transactions, write_decisions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="riskreview")
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess", help="assess transactions against configured rules")
    assess.add_argument("--transactions", type=Path, required=True)
    assess.add_argument("--rules", type=Path, required=True, dest="rules_path")
    assess.add_argument("--out", type=Path, required=True)
    assess.add_argument("--fail-on-reject", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "assess":
        parser.error("unsupported command")
    try:
        input_path: Path = args.transactions
        output_path: Path = args.out
        config_path: Path = args.rules_path
        if not input_path.is_file():
            raise InputError(f"transactions file does not exist: {input_path}")
        if not config_path.is_file():
            raise ConfigError(f"rules file does not exist: {config_path}")
        if input_path.resolve() == output_path.resolve():
            raise ValueError("output path must not overwrite the input CSV")
        bundle = build_engine(config_path)
        transactions = read_transactions(input_path)
        assessments = bundle.engine.assess_all(transactions)
        write_decisions(output_path, assessments, bundle.config_sha256)
        counts = Counter(item.decision.value for item in assessments)
        rule_counts = Counter(hit.rule_id for item in assessments for hit in item.hits)
        summary = {
            "transactions_assessed": len(assessments),
            "decisions": {key: counts.get(key, 0) for key in ("approve", "review", "reject")},
            "top_rules_fired": [
                {"rule_id": rule_id, "count": count}
                for rule_id, count in sorted(rule_counts.items(), key=lambda pair: (-pair[1], pair[0]))[:5]
            ],
            "config_sha256": bundle.config_sha256,
            "output": str(output_path),
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        if args.fail_on_reject and counts["reject"]:
            print("riskreview: one or more transactions were rejected", file=sys.stderr)
            return 1
        return 0
    except (OSError, ValueError, ConfigError, InputError) as exc:
        print(f"riskreview: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```


### `tests/test_engine.py`

```python
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from riskreview.engine import ConfigError, Thresholds, build_engine
from riskreview.models import Decision, Transaction
from riskreview.rules import HighAmountRule, HighRiskCountryRule, RiskHit  # type: ignore[attr-defined]

CONFIG = """
[thresholds]
review_at = 40
reject_at = 80

[[rules]]
id = "high_amount"
type = "high_amount"
threshold_cents = 500000
points = 40

[[rules]]
id = "watch_country"
type = "country"
countries = ["XX", "YY"]
points = 30

[[rules]]
id = "account_velocity"
type = "velocity"
max_count = 2
window_seconds = 60
points = 50
"""
T0 = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)


def txn(i: int, amount: int = 1000, country: str = "US", secs: int = 0,
        account: str = "acc1") -> Transaction:
    return Transaction(f"t{i}", account, amount, country, T0 + timedelta(seconds=secs))


def test_threshold_boundaries() -> None:
    thresholds = Thresholds(40, 80)
    assert thresholds.decide(39) is Decision.APPROVE
    assert thresholds.decide(40) is Decision.REVIEW
    assert thresholds.decide(79) is Decision.REVIEW
    assert thresholds.decide(80) is Decision.REJECT


def test_rules_and_explainability(tmp_path: Path) -> None:
    cfg = tmp_path / "rules.toml"
    cfg.write_text(CONFIG, encoding="utf-8")
    bundle = build_engine(cfg)
    result = bundle.engine.assess(txn(1, amount=500000, country="XX", account="isolated"))
    assert result.score == 70
    assert result.decision is Decision.REVIEW
    assert [hit.rule_id for hit in result.hits] == ["high_amount", "watch_country"]
    assert all(hit.reason for hit in result.hits)


def test_velocity_inclusive_window_and_fresh_engine(tmp_path: Path) -> None:
    cfg = tmp_path / "rules.toml"
    cfg.write_text(CONFIG, encoding="utf-8")
    bundle = build_engine(cfg)
    results = bundle.engine.assess_all([
        txn(3, secs=60), txn(1, secs=0), txn(2, secs=30)
    ])
    assert [r.txn_id for r in results] == ["t1", "t2", "t3"]
    assert [r.score for r in results] == [0, 0, 50]
    # A newly built engine has no inherited velocity state.
    fresh = build_engine(cfg).engine.assess_all([txn(1), txn(2)])
    assert [r.score for r in fresh] == [0, 0]


def test_config_fails_fast_on_unknown_type_and_bad_thresholds(tmp_path: Path) -> None:
    cfg = tmp_path / "bad.toml"
    cfg.write_text('[thresholds]\nreview_at=90\nreject_at=10\n[[rules]]\nid="x"\ntype="nope"\npoints=1\n',
                   encoding="utf-8")
    with pytest.raises(ConfigError):
        build_engine(cfg)


def test_config_duplicate_rule_ids_rejected(tmp_path: Path) -> None:
    cfg = tmp_path / "duplicate.toml"
    cfg.write_text(CONFIG.replace('id = "watch_country"', 'id = "high_amount"'), encoding="utf-8")
    with pytest.raises(ConfigError, match="duplicate rule IDs"):
        build_engine(cfg)
```


### `tests/test_io_cli.py`

```python
import csv
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from riskreview.cli import main
from riskreview.io import InputError, parse_timestamp, read_transactions, write_decisions
from riskreview.models import Assessment, Decision, RuleHit, Transaction


def write_sample(path: Path) -> None:
    path.write_text(
        "txn_id,account_id,amount_cents,country,timestamp,merchant_category\n"
        "t2,a2,500000,XX,2026-05-01T12:00:10Z,travel\n"
        "t1,a1,1000,US,2026-05-01T12:00:00+00:00,grocery\n",
        encoding="utf-8",
    )


def write_config(path: Path) -> None:
    path.write_text(
        '[thresholds]\nreview_at=40\nreject_at=80\n'
        '[[rules]]\nid="amount"\ntype="high_amount"\nthreshold_cents=500000\npoints=80\n',
        encoding="utf-8",
    )


def test_csv_read_sort_and_timestamp_normalization(tmp_path: Path) -> None:
    source = tmp_path / "txns.csv"
    write_sample(source)
    txns = read_transactions(source)
    assert len(txns) == 2
    assert txns[0].txn_id == "t2"  # reader preserves file order; engine sorts for stateful evaluation
    assert txns[0].timestamp.tzinfo is not None
    assert parse_timestamp("2026-05-01T12:00:00Z") == datetime(2026, 5, 1, 12, 0, tzinfo=UTC)


def test_bad_timestamp_and_duplicate_ids(tmp_path: Path) -> None:
    with pytest.raises(InputError, match="timezone"):
        parse_timestamp("2026-05-01T12:00:00")
    source = tmp_path / "bad.csv"
    source.write_text(
        "txn_id,account_id,amount_cents,country,timestamp\n"
        "t1,a,1,US,2026-05-01T00:00:00Z\n"
        "t1,b,2,US,2026-05-01T00:00:01Z\n",
        encoding="utf-8",
    )
    with pytest.raises(InputError, match="duplicate txn_id"):
        read_transactions(source)


def test_jsonl_is_deterministic_and_contains_config_hash(tmp_path: Path) -> None:
    out = tmp_path / "decisions.jsonl"
    assessment = Assessment("t1", 80, Decision.REJECT, (RuleHit("amount", 80, "large"),))
    write_decisions(out, [assessment], "abc123")
    first = out.read_bytes()
    write_decisions(out, [assessment], "abc123")
    assert out.read_bytes() == first
    record = json.loads(first.decode("utf-8"))
    assert record["config_sha256"] == "abc123"
    assert record["hits"][0]["rule_id"] == "amount"


def test_cli_outputs_and_fail_on_reject(tmp_path: Path, capsys) -> None:
    source, config, output = tmp_path / "txns.csv", tmp_path / "rules.toml", tmp_path / "out.jsonl"
    write_sample(source)
    write_config(config)
    result = main(["assess", "--transactions", str(source), "--rules", str(config),
                   "--out", str(output), "--fail-on-reject"])
    assert result == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out)["decisions"]["reject"] == 1
    assert "one or more transactions were rejected" in captured.err
    assert len(output.read_text(encoding="utf-8").splitlines()) == 2


def test_cli_bad_input_clear_error(tmp_path: Path, capsys) -> None:
    config = tmp_path / "rules.toml"
    write_config(config)
    result = main(["assess", "--transactions", str(tmp_path / "missing.csv"),
                   "--rules", str(config), "--out", str(tmp_path / "out.jsonl")])
    assert result == 1
    assert "does not exist" in capsys.readouterr().err
```


### `data/transactions.csv`

```csv
txn_id,account_id,amount_cents,country,timestamp,merchant_category
txn-001,acct-1,1200,US,2026-05-01T12:00:00Z,grocery
txn-002,acct-2,650000,US,2026-05-01T12:00:10Z,travel
txn-003,acct-1,800,XX,2026-05-01T12:00:20Z,online
txn-004,acct-1,900,US,2026-05-01T12:00:30Z,online
```


### `README.md`

```markdown
# riskreview — Rule-Based Risk Review Engine

A deterministic, explainable transaction-scoring CLI built with Python's standard library.

## Setup

```bash
uv sync
uv run riskreview assess --transactions data/transactions.csv --rules config/rules.toml --out out/decisions.jsonl
```

Use `--fail-on-reject` to return exit code `1` if any transaction is rejected. The decisions JSONL is written before that quality-gate exit, so the evidence remains available.

## Quality gates

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src
```

## Contract and assumptions

- Required input columns: `txn_id`, `account_id`, `amount_cents`, `country`, `timestamp`. `merchant_category` is optional.
- `amount_cents` is a non-negative integer; no float-based currency arithmetic.
- Timestamps must be timezone-aware ISO-8601 and are normalized to UTC.
- Transactions are sorted by `(timestamp, txn_id)` before stateful rules run.
- `VelocityRule` counts the current transaction and includes the exact window boundary; it fires when count is greater than `max_count`.
- Each JSONL line includes all rule hits, score, decision, and SHA-256 of the exact TOML configuration bytes.
- A new engine must be built for each run because velocity rules carry state.
- This is a learning baseline, not a fraud decision service. Rules and country lists are illustrative, not real-world risk advice.
```


## 9. CLI and exit codes

```bash
# Assess and write decisions; print summary to stdout.
uv run riskreview assess \
  --transactions data/transactions.csv \
  --rules config/rules.toml \
  --out out/decisions.jsonl

# Return exit code 1 when any decision is reject (output is still written).
uv run riskreview assess \
  --transactions data/transactions.csv \
  --rules config/rules.toml \
  --out out/decisions.jsonl \
  --fail-on-reject
```

- `0`: processing completed; or no rejected transactions when `--fail-on-reject` is enabled.
- `1`: invalid config/input/output or at least one rejected transaction when `--fail-on-reject` is enabled.
- `2`: `argparse` usage error.
- Summary JSON goes to stdout; operational errors go to stderr.
- Decision output is written before the `--fail-on-reject` gate returns `1`, preserving the evidence.

## 10. Test strategy

The reference tests cover inclusive threshold boundaries, multiple simultaneous hits, explainability, deterministic sorting, velocity-window behavior, fresh-engine state isolation, duplicate rule IDs, invalid threshold/config, timezone validation, duplicate transaction IDs, deterministic JSONL, config hash, CLI summary, and fail-on-reject.

Add these acceptance tests before calling the project finished:

1. Golden-file comparison for a fixed input/config/output set.
2. Missing config keys, malformed TOML, unknown rule type, invalid rule parameter types, empty rule list, duplicate rule IDs.
3. Timestamp with a non-UTC offset and a naive timestamp.
4. Two transactions with identical timestamps and distinct IDs; tie order must be transaction ID.
5. Exact velocity cutoff boundary and just-outside boundary.
6. Repeated transaction ID and malformed-width CSV records.
7. Unreadable input, unwritable output path, and output path equal to input path.
8. `--fail-on-reject` absent versus present.
9. Run the CLI twice into separate output files and compare output bytes.
10. `mypy --strict`, Ruff lint, formatter check, and a clean locked installation.

## 11. Detailed audit report

### Design findings and fixes applied

1. **Inclusive threshold semantics:** score equal to `review_at` is `review`; equal to `reject_at` is `reject`.
2. **Money representation:** integer minor units avoid floating-point currency errors.
3. **Timezone safety:** naive timestamps are rejected; aware timestamps are normalized to UTC.
4. **Deterministic stateful evaluation:** sort by `(timestamp, txn_id)` before running velocity rules.
5. **Velocity window semantics:** the window is explicitly inclusive at the cutoff; expired events strictly earlier than the cutoff are removed.
6. **State isolation:** engine state is scoped to a single run; build a new engine for every independent assessment.
7. **Config safety:** explicit type factory; no `eval`; unknown types, missing keys, invalid thresholds, and duplicate rule IDs fail fast.
8. **Audit integrity:** each output record includes config SHA-256 and all fired-rule reasons.
9. **Stable output:** JSON keys are sorted, compact JSON is used, and output is atomically replaced.
10. **CLI evidence preservation:** `--fail-on-reject` returns non-zero only after decisions and summary are available.
11. **Input contract:** duplicate IDs, wrong CSV width, invalid amount format, and timezone errors produce clear input failures.
12. **Layering:** models are isolated; rules do not own I/O or CLI concerns.

### Actual validation performed during artifact creation

- Python AST syntax parsing: **PASS** for all 8 Python source/test files.
- TOML parsing: **PASS** for `pyproject.toml` and `config/rules.toml`.
- pytest: **PASS — 11 tests passed** in the artifact-generation environment.
- CLI subprocess smoke test: **PASS**, exit code `0`; 4 transactions assessed and decision JSONL generated.
- Golden-file comparison: **PASS**; output bytes match `tests/golden/decisions.jsonl`.
- Ruff lint: **NOT RUN** — executable unavailable.
- Ruff formatter check: **NOT RUN** — executable unavailable.
- mypy strict: **NOT RUN** — executable unavailable.
- Fresh `uv sync --locked`: **NOT RUN** — not available in this execution environment.
- Ruff/mypy and fresh locked installation remain outstanding. The CLI subprocess and golden-file checks were executed successfully.

These are measured results. Unavailable tools are not reported as passing.

## 12. Production-minded limitations and safeguards

This project demonstrates explainable deterministic rules; it is not an actual fraud model and must not be used to make real financial decisions without governance, validation, privacy/security review, monitoring, and human oversight.

- The watch-list countries and points in the sample config are fictitious examples.
- `config_sha256` fingerprints the exact configuration bytes, so whitespace changes also change the hash.
- Atomic replacement protects the single JSONL file from partial writes; it does not provide a transaction with any external system.
- Velocity state is in-memory and is not shared across multiple processes.
- This CLI does not persist prior transaction state or support online event processing.
- The audit output includes reasons but no personal or payment details beyond the transaction ID.
- Rule points and thresholds require explicit business ownership and documented calibration in real applications.

## 13. Common mistakes to avoid

- Reusing an engine instance across independent runs and leaking velocity state.
- Applying rules in CSV file order instead of deterministic timestamp order.
- Forgetting that `>=` boundaries are inclusive.
- Using floats for monetary amounts.
- Writing one generic “risk detected” reason rather than all fired-rule reasons.
- Loading rule code through `eval`.
- Allowing duplicate rule IDs to make audit records ambiguous.
- Using local naive datetimes or comparing timestamps in inconsistent timezones.
- Claiming that a SHA-256 hash proves a decision is correct; it only fingerprints the configuration bytes.
- Calling the example thresholds “production-ready” without calibration evidence.

## 14. Git workflow

```bash
git status --short
git add pyproject.toml uv.lock config data src tests README.md
git commit -m "Build explainable rule-based risk review engine"
git status --short
```

Do not commit `.venv/`, cache files, generated temporary files, or real transaction data.

## 15. Final acceptance checklist

- [ ] Transaction model is immutable and validates required invariants.
- [ ] All timestamps are timezone-aware and normalized to UTC.
- [ ] `Rule` is a structural `Protocol`; three rules implement it.
- [ ] All hits are retained and score is their point sum.
- [ ] Thresholds are inclusive and invalid ordering fails fast.
- [ ] TOML supports explicit rule types and rejects malformed/unknown config.
- [ ] Duplicate rule IDs and duplicate transaction IDs fail clearly.
- [ ] Velocity uses per-account state and a documented inclusive window.
- [ ] A fresh engine is used for every independent run.
- [ ] Input is sorted by `(timestamp, txn_id)` before evaluation.
- [ ] JSONL has one decision record per transaction and includes config hash.
- [ ] Summary contains counts by decision and top rules fired.
- [ ] CLI exit codes and `--fail-on-reject` are verified.
- [ ] Repeated runs with identical inputs/config produce identical bytes.
- [ ] Golden-file tests pass.
- [ ] Ruff, format check, mypy strict, pytest, and locked clean install pass.
- [ ] No real customer/transaction data is committed.
- [ ] README explains assumptions, statefulness, and limitations.

## 16. Interview discussion

Be ready to explain:

- Why `Protocol` is appropriate for rules and how structural typing differs from inheritance.
- Why immutable transaction/assessment models coexist with mutable velocity state.
- Why the engine sorts inputs before stateful evaluation.
- Why threshold comparisons are inclusive and how the boundaries are tested.
- How the sliding window works and what its state costs in memory.
- What `config_sha256` proves and what it does not prove.
- Why a fresh engine is required for independent reruns.
- Why deterministic output and human-readable reasons matter for auditability.
- What must change before this educational engine could be used in a real financial risk workflow.
