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
