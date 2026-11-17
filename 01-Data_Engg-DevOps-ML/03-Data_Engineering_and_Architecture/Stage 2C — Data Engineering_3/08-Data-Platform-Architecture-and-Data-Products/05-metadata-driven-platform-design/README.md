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
python schema/generate_json_schema.py
python run_lab.py
pytest -q
```

## What runs
- Validates three YAML definitions against the Pydantic v2 schema.
- Generates deterministic JSON execution plans, dbt-style staging SQL, a matching `sources.yml`, governance policy JSON, and an artifact-digest manifest.
- Records `SIMULATED` run history and creates local OpenLineage-shaped `OTHER` events; it does not claim data movement succeeded.
- Demonstrates schema v1-to-v3 and v2-to-v3 migrations in tests. A legacy config without full column metadata is migrated to a minimal key/watermark column list and must be reviewed/enriched before production. Legacy CDC configs require explicit manual mapping to a log cursor.

No Airflow, Dagster, real source, warehouse, masking engine, lifecycle manager, or OpenLineage backend is invoked. The runtime plan and governance artifacts are integration contracts for a future deployment.

## Extension point
`source.connector` is an enum allow-list. To add a connector:
1. Implement a connector adapter that conforms to the platform's source interface.
2. Add a reviewed connector type and configuration schema.
3. Add contract tests and a fixture for its output.
4. Keep secrets in a secret manager; `connection_ref` is only a reference, never a credential.
5. Only add `custom_logic` after review; it is recorded as a request in this lab and never executed. A real runtime must resolve it through an explicit allow-listed plugin registry.

## Metadata schema versioning
`fixtures/legacy_customers_v1.yaml` illustrates the old flat shape. `migrate_v1_to_v3()` converts it to the current nested v3 shape and validates the migrated object with `PipelineSpec`. `migrate_v2_to_v3()` upgrades existing draft v2 configs by adding column and dbt-schema metadata; inferred columns must be reviewed before production. The migration is deterministic but cannot infer a full source schema from the old format.
