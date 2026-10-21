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
