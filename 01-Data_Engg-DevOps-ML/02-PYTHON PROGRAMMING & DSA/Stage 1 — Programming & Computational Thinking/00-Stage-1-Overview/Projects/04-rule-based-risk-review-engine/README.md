# riskreview — Rule-Based Risk Review Engine

A deterministic, explainable transaction-scoring CLI built with Python's standard library.

## Setup

```bash
uv sync
uv run riskreview assess --transactions data/transactions.csv --rules config/rules.toml --out out/decisions.jsonl
```

Use `--fail-on-reject` to return exit code `1` if any transaction is rejected. The decisions JSONL is written before that quality-gate exit, so the evidence remains available.

## Quality gates

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src
```

## Contract and assumptions

- Required input columns: `txn_id`, `account_id`, `amount_cents`, `country`, `timestamp`. `merchant_category` is optional.
- `amount_cents` is a non-negative integer; no float-based currency arithmetic.
- Timestamps must be timezone-aware ISO-8601 and are normalized to UTC.
- Transactions are sorted by `(timestamp, txn_id)` before stateful rules run.
- `VelocityRule` counts the current transaction and includes the exact window boundary; it fires when count is greater than `max_count`.
- Each JSONL line includes all rule hits, score, decision, and SHA-256 of the exact TOML configuration bytes.
- A new engine must be built for each run because velocity rules carry state.
- This is a learning baseline, not a fraud decision service. Rules and country lists are illustrative, not real-world risk advice.
