# Entity Resolution and MDM Lab

## Requirements
- Python 3.10+
- Core implementation uses only the standard library.
- Optional: `rapidfuzz` for faster similarity; Splink 4 + DuckDB + pandas for a separate probabilistic linkage demonstration.
- pytest for tests.

## Setup
```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

Optional fuzzy package:
```bash
python -m pip install -e ".[fuzzy,test]"
```

Run core demo:
```bash
python run_lab.py
pytest -q
```

Optional Splink path:
```bash
python -m pip install -e ".[splink]"
python splink_runner.py
```
Splink API is version-sensitive. The optional script is not part of the core test suite. It is included as an integration starting point, not represented as executed in environments without Splink and DuckDB.

## Ground truth
`data/source_records.json` has synthetic source records with `entity_id` labels used only for evaluation. Do not expose ground-truth labels to the matcher in production. `entity_id` is dropped by the optional Splink runner.

## Scope and caveats
The core probabilistic scorer is Fellegi–Sunter-inspired but uses explicit pedagogical weights rather than estimated m/u probabilities. It demonstrates feature agreement, candidate generation, threshold bands, review queues, clustering, survivorship, and ID stability. It is not a trained statistical model and should not be presented as production-calibrated.
