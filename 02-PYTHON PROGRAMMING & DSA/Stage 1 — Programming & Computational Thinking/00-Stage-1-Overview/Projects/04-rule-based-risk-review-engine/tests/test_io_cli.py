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


def test_golden_decisions_file(tmp_path: Path) -> None:
    from riskreview.engine import build_engine
    from riskreview.io import read_transactions, write_decisions

    project_root = Path(__file__).resolve().parents[1]
    bundle = build_engine(project_root / "config" / "rules.toml")
    transactions = read_transactions(project_root / "data" / "transactions.csv")
    assessments = bundle.engine.assess_all(transactions)
    actual = tmp_path / "decisions.jsonl"
    write_decisions(actual, assessments, bundle.config_sha256)
    expected = (project_root / "tests" / "golden" / "decisions.jsonl").read_bytes()
    assert actual.read_bytes() == expected
