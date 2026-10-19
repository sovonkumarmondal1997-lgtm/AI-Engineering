# Build vs Buy Vendor Evaluation Lab

A reproducible educational exercise for choosing ingestion for 40 SaaS sources. The illustrative scorecard names Fivetran managed ingestion, Airbyte Core self-managed, and custom dlt-based ingestion; scores are hypotheses, not measured vendor facts.

## Contents
- `assumptions.json`: all illustrative USD and labour assumptions.
- `model.py`: TCO and weighted-score calculation, CSV outputs.
- `scorecard.json`: criteria, weights, candidate scores, and evidence status.
- `poc_plan.md`: 10-business-day plan, success criteria, and unrun results template.
- `docs/adr/ADR-007.md`: complete sample ADR.
- `tests/test_model.py`: calculation and invariant tests.

## Run

Python 3.10+; no third-party dependencies.

```bash
python model.py
python -m unittest discover -s tests -v
```

Outputs are written to `outputs/tco_results.csv` and `outputs/scorecard_results.csv`.

All monetary figures are generic cost-archetype assumptions, not named-vendor quotes. Scores are illustrative hypotheses, and all hard gates remain NOT_ASSESSED. No POC has been executed. Replace the assumptions with written quotes and actual measurements, then clear security/legal and correctness gates before making a procurement decision.
