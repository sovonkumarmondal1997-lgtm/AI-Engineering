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
