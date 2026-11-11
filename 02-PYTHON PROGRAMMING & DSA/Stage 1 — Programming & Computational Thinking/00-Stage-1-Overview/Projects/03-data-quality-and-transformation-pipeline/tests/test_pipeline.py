import csv
import hashlib
import json
from pathlib import Path

import pytest

from dqpipe.config import load_config
from dqpipe.pipeline import run_pipeline, write_outputs

HEADER = "order_id,customer_email,order_date,country,quantity,unit_price,status\n"
GOOD = "A1,Ann@Example.com,2026-02-01,usa,2,10.50,PAID\n"
COUNTRIES = {"usa": "US", "us": "US", "uk": "GB", "india": "IN"}


def write_csv(path: Path, content: str, *, bom: bool = False) -> None:
    encoding = "utf-8-sig" if bom else "utf-8"
    path.write_text(content, encoding=encoding, newline="")


def test_end_to_end_outputs_and_idempotency(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    write_csv(source, HEADER + GOOD + "A2,bad-email,2026-02-02,UK,1,5,new\n")
    out = tmp_path / "out"
    report, outcomes, clean = run_pipeline(source, out, COUNTRIES)
    assert (report["rows_read"], report["rows_clean"], report["rows_rejected"]) == (2, 1, 1)
    assert report["input_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    write_outputs(out, report, outcomes, clean)
    first = {p.name: p.read_bytes() for p in out.iterdir()}
    report2, outcomes2, clean2 = run_pipeline(source, out, COUNTRIES)
    write_outputs(out, report2, outcomes2, clean2)
    assert {p.name: p.read_bytes() for p in out.iterdir()} == first
    with (out / "clean_orders.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["customer_email"] == "ann@example.com"
    assert rows[0]["order_total"] == "21.00"
    assert rows[0]["order_month"] == "2026-02"
    report_json = json.loads((out / "quality_report.json").read_text(encoding="utf-8"))
    assert report_json["order_total_summary"]["sum"] == "21.00"


def test_bom_and_quoted_comma_are_supported(tmp_path: Path) -> None:
    source = tmp_path / "bom.csv"
    write_csv(source, HEADER + 'A1,"ann,ops@example.com",2026-02-01,usa,1,1.00,new\n', bom=True)
    report, _, clean = run_pipeline(source, tmp_path / "out", COUNTRIES)
    assert report["rows_clean"] == 1
    assert clean[0]["customer_email"] == "ann,ops@example.com"


def test_multiple_violations_and_duplicate_policy(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    content = HEADER + (
        "A1,bad,2026-02-30,Mars,0,NaN,lost\n"
        + GOOD
        + " A1 ,ann@example.com,2026-02-01,US,1,1.00,new\n"
    )
    write_csv(source, content)
    report, outcomes, clean = run_pipeline(source, tmp_path / "out", COUNTRIES)
    assert report["rows_read"] == 3
    assert report["rows_clean"] == 1
    assert report["rows_rejected"] == 2
    assert len(outcomes[0].violations) >= 5
    # Invalid first row does not reserve A1; first valid A1 survives, later valid A1 is duplicate.
    assert report["violations_by_rule"]["duplicate_key"] == 1
    assert clean[0]["order_id"] == "A1"


def test_missing_and_extra_columns_fail_fast(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    write_csv(source, "order_id,customer_email\nA1,a@example.com\n")
    with pytest.raises(ValueError, match="missing required columns"):
        run_pipeline(source, tmp_path / "out", COUNTRIES)
    write_csv(source, HEADER.rstrip("\n") + ",extra\n" + GOOD.rstrip("\n") + ",x\n")
    with pytest.raises(ValueError, match="unexpected columns"):
        run_pipeline(source, tmp_path / "out", COUNTRIES)


def test_header_only_file_is_valid_empty_batch(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    write_csv(source, HEADER)
    report, outcomes, clean = run_pipeline(source, tmp_path / "out", COUNTRIES)
    assert report["rows_read"] == report["rows_clean"] == report["rows_rejected"] == 0
    assert report["reject_rate"] == 0.0
    assert outcomes == []
    assert clean == []


def test_too_few_fields_are_rejected_not_crashed(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    write_csv(source, HEADER + "A1,ann@example.com\n")
    report, outcomes, _ = run_pipeline(source, tmp_path / "out", COUNTRIES)
    assert report["rows_rejected"] == 1
    assert outcomes[0].violations[0].rule == "csv_shape"


def test_embedded_newline_in_quoted_field(tmp_path: Path) -> None:
    source = tmp_path / "orders.csv"
    write_csv(source, HEADER + 'A1,"ann\n@example.com",2026-02-01,usa,1,1.00,new\n')
    report, _, _ = run_pipeline(source, tmp_path / "out", COUNTRIES)
    assert report["rows_rejected"] == 1


def test_config_validation(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    config.write_text('[pipeline]\nmax_reject_rate = 1.5\n', encoding="utf-8")
    with pytest.raises(ValueError, match="between 0 and 1"):
        load_config(config)
