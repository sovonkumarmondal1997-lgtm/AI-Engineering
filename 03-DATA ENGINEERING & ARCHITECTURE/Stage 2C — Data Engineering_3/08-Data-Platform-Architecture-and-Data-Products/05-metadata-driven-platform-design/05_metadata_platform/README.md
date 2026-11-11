# Metadata-driven platform lab

This is a local educational framework, not a deployed scheduler or ingestion service.

## Requirements
- Python 3.10+
- Pydantic 2, PyYAML, Jinja2
- pytest for tests

## Setup
```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python run_lab.py
pytest -q
```

## What runs
- Validates three YAML definitions against the Pydantic v2 schema.
- Generates JSON execution plans, governance policy JSON, and dbt-style staging SQL.
- Simulates run history and creates OpenLineage-shaped JSON events locally.
- Demonstrates schema v1-to-v2 migration in tests.

No Airflow, Dagster, real source, warehouse, masking engine, lifecycle manager, or OpenLineage backend is invoked. The runtime plan and governance artifacts are integration contracts for a future deployment.

## Extension point
`source.connector` is an enum allow-list. To add a connector:
1. Implement a connector adapter that conforms to the platform's source interface.
2. Add a reviewed connector type and configuration schema.
3. Add contract tests and a fixture for its output.
4. Keep secrets in a secret manager; `connection_ref` is only a reference, never a credential.
5. Only add `custom_logic` after review; it must resolve to an allow-listed plugin, not arbitrary Python evaluated from YAML.

## Metadata schema versioning
`fixtures/legacy_customers_v1.yaml` illustrates the old flat shape. `migrate_v1_to_v2()` converts it to the nested v2 shape and the resulting object is validated by `PipelineSpec`.
