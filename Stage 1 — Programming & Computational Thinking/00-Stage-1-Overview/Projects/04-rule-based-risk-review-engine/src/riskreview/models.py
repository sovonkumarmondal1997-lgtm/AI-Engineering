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
