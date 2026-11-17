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
