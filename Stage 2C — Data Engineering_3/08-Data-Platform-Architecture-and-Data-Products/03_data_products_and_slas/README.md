# Data Products and SLAs Lab

This is an educational local demonstration for `03-data-products-and-slas.md`.

## Requirements

- Python 3.10+
- Pydantic 2.x
- PyYAML 6.x
- pytest 8.x for tests

## Setup

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

python -m pip install -e ".[test]"
```

## Validate the product spec and run the demonstration

From this directory:

```bash
python product_lab.py
pytest -q
```

The CLI uses a fixed `--now` timestamp by default to make the sample deterministic. In real monitoring, omit that fixed assumption and use the current UTC time or the scheduler's observation time:

```bash
python product_lab.py --now 2026-10-19T09:00:00Z
```

## What this demo does

- Validates `specs/orders.yaml` with Pydantic.
- Evaluates a sample snapshot's freshness, completeness, and basic quality checks.
- Calculates cumulative freshness and completeness error-budget consumption from sample probe history.
- Compares a schema v1 to a breaking v2 and recommends parallel-version migration.
- Writes a local JSON notification outbox.
- Writes a report to `reports/slo_report.json`.

## Explicit limitations

- The snapshot/history are fixtures, not live pipeline metrics.
- The notification mechanism writes JSON only; it does not send email or call a messaging API.
- Catalogue registration is not attempted. No live DataHub/OpenMetadata server or credentials are included.
- This lab uses a custom educational YAML schema validated by Pydantic. It is not claimed to be a complete ODCS implementation. For interoperable contracts, validate an ODCS document using the official standard/tooling.
- The example retention and SLO values are fictional product decisions, not legal requirements or universal benchmarks.
