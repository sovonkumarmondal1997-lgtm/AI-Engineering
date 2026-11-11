# dqpipe — Data Quality & Transformation Pipeline

A deterministic batch pipeline using Python's standard library. It validates an orders CSV, normalises documented values, rejects invalid or duplicate rows with explanations, writes clean data, and emits a JSON quality report.

## Requirements

- Python 3.12+
- `uv`

## Setup and run

```bash
uv sync
uv run dqpipe run --input data/orders.csv --out-dir out --config config.toml
```

The command returns exit code `1` if the reject rate exceeds the configured threshold. Outputs are still written for investigation. Use `--dry-run` to report without writing output files.

## Quality gates

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src
```

## Outputs

- `clean_orders.csv`: validated, normalised, deduplicated rows plus derived columns.
- `rejects.csv`: one record per violation, including record number and raw row JSON.
- `quality_report.json`: counts, reject rate, rule counts/examples, totals summary, input SHA-256.

## Semantics and limitations

- Header must contain exactly the seven documented columns.
- UTF-8 and UTF-8 BOM are supported.
- The first valid occurrence of a normalised order ID wins; invalid rows do not reserve keys.
- Money is represented by `Decimal`; over-precision is rejected, not silently rounded.
- Each output is atomically replaced individually; the three files are not one transaction.
- Baseline materializes row outcomes in memory; it is not a constant-memory streaming pipeline.
- Reject files contain raw values. Use synthetic data only and do not commit private records.
