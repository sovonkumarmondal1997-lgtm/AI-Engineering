from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from riskreview.engine import ConfigError, Thresholds, build_engine
from riskreview.models import Decision, Transaction

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
