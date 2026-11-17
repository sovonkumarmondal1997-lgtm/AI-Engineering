import json
from pathlib import Path

from dqpipe.cli import main

HEADER = "order_id,customer_email,order_date,country,quantity,unit_price,status\n"
GOOD = "A1,ann@example.com,2026-02-01,usa,1,1.00,new\n"


def test_cli_success_and_threshold_failure(tmp_path: Path, capsys) -> None:
    source = tmp_path / "orders.csv"
    source.write_text(HEADER + GOOD + "A2,bad,2026-02-30,usa,1,1.00,new\n", encoding="utf-8")
    out = tmp_path / "out"
    assert main(["run", "--input", str(source), "--out-dir", str(out),
                 "--max-reject-rate", "0.5"]) == 0
    stdout = capsys.readouterr().out
    assert json.loads(stdout)["rows_rejected"] == 1
    assert main(["run", "--input", str(source), "--out-dir", str(out),
                 "--max-reject-rate", "0.1"]) == 1
    captured = capsys.readouterr()
    assert "exceeds threshold" in captured.err
    assert (out / "quality_report.json").exists()


def test_dry_run_does_not_write_outputs(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    source.write_text(HEADER + GOOD, encoding="utf-8")
    out = tmp_path / "out"
    assert main(["run", "--input", str(source), "--out-dir", str(out), "--dry-run"]) == 0
    assert not out.exists()


def test_missing_input_is_clear_error(tmp_path: Path, capsys) -> None:
    result = main(["run", "--input", str(tmp_path / "missing.csv")])
    assert result == 1
    assert "does not exist" in capsys.readouterr().err
