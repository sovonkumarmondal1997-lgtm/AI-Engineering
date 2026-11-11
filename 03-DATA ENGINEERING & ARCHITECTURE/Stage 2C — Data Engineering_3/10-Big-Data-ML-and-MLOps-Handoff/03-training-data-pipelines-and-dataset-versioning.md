# Training Data Pipelines and Dataset Versioning

> **Roadmap position:** Stage 2C — Data Engineering_3 → Module 10, Big Data ML and MLOps Handoff → Topic 03  
> **Primary responsibility:** Build training datasets whose contents, semantics, lineage, and validation outcomes can be identified and reproduced later.

## 1. Learning outcomes

By the end of this lesson, you should be able to:

- Explain why model metrics alone cannot reproduce a training run.
- Track the six reproducibility elements: data, feature definitions, code, configuration/parameters, execution environment, and model artifacts.
- Build a timestamped fraud/churn training set from labels and historical features without using future information.
- Distinguish a table snapshot, dataset fingerprint, immutable dataset artifact, logical dataset version, and full run manifest.
- Compare Delta Lake time travel, Iceberg snapshot IDs, immutable Parquet snapshots, DVC, lakeFS, and MLflow dataset/run metadata.
- Create deterministic entity-level splits and identify group, temporal, session, and near-duplicate leakage.
- Handle delayed, noisy, censored, and leaked labels; negative sampling; and class imbalance without corrupting evaluation.
- Validate schemas, distributions, label balance, and changes from the prior dataset version.
- Orchestrate parameterized, idempotent data pipelines with failure gates.
- Reconstruct a past run from pinned data, code, environment, parameters, features, and model artifacts.
- Apply lineage, retention, consent, deletion, dataset slicing, and curated evaluation-set practices.

## 2. Prerequisites and environment

This lesson assumes familiarity with Python, pandas, SQL joins/window functions, data-quality checks, version control, and basic ML training. It follows Topic 02, Feature Engineering at Scale: feature values must already have documented entity keys and temporal semantics.

### 2.1 Local learning environment

Create the local lab:

```bash
mkdir -p experiments/03_training_data/{src,tests,data,artifacts}
cd experiments/03_training_data
uv init
uv add pandas numpy pyarrow scikit-learn joblib mlflow
uv add --dev pytest
# Initialize/version the code before running the MLflow example:
git init
uv lock
```

Commit the source code, `pyproject.toml`, `uv.lock`, and the tests before a tracked training run; the example intentionally rejects an uncommitted worktree. Use the lockfile produced by your package manager and commit it. The exact Python/package versions depend on your platform; a reproducible project pins compatible versions rather than copying a floating `latest` environment.

Suggested structure:

```text
experiments/03_training_data/
├── pyproject.toml
├── uv.lock
├── README.md
├── data/
│   ├── raw/                  # generated or governed source fixtures
│   └── snapshots/            # immutable training outputs
├── src/
│   ├── build_dataset.py      # point-in-time join + deterministic splits
│   ├── fingerprint.py        # canonical row-level dataset identity
│   ├── validate.py           # schema and distribution gates
│   └── train.py              # MLflow-tracked baseline
├── artifacts/                # manifests and model outputs
└── tests/
    ├── test_point_in_time.py
    ├── test_splits.py
    ├── test_fingerprint.py
    └── test_validation.py
```

The core project below is local and does not require a cloud account. Delta Lake, Iceberg, DVC remote storage, lakeFS, and managed orchestrators are optional integrations that require their own compatible dependencies and/or services. Do not treat a local unit test as proof that an external integration has been exercised.

## 3. Reproducibility fundamentals

### 3.1 What reproducibility means

A training run is reproducible when you can identify the inputs and process that produced it, re-run that process under documented assumptions, and compare the resulting dataset, model, and metrics.

It matters for:

- **Debugging:** distinguish a code regression from an upstream data change.
- **Experiment comparison:** attribute a metric change to a known input or configuration difference.
- **Audit and accountability:** show what data and transformation logic were used.
- **Rollback and incidents:** return to a known model/data combination while investigating a failure.
- **Trust:** make a prediction or model behavior explainable through traceable inputs.

“Run the script again” is not enough. The same script can read a table that has changed, use a different dependency version, resolve a different feature definition, or pull a different source partition.

### 3.2 The six elements to track

| Element | Record | Why it matters |
|---|---|---|
| Data | Source table versions/snapshots, partition bounds, immutable output URI, dataset fingerprint | Identifies the actual training examples |
| Feature definitions | Code/version, feature names, units, windows, point-in-time policy, null semantics | Identifies how raw values became model inputs |
| Code | Git commit, dirty-worktree state, build/package version | Identifies implementation |
| Configuration and parameters | Split policy, date ranges, filters, seed, model parameters, thresholds | Identifies runtime choices |
| Execution environment | Python/runtime version, lockfile hash, container image digest, relevant hardware/library details | Reduces environmental variation |
| Model artifacts | Model file/registry version, artifact checksum, preprocessing pipeline | Identifies the produced model |

Link these elements with a unique `run_id` and a machine-readable manifest. The model artifact should point back to the dataset fingerprint and code commit; the dataset manifest should point back to source versions and feature definitions.

Tracking only AUC, accuracy, or loss is insufficient. Two runs can produce the same metric from different data, and a metric cannot reconstruct the rows that were used.

### 3.3 A vocabulary that must not be conflated

- **Table snapshot/version:** a storage-system reference to a table state at a point in its transaction history.
- **Iceberg snapshot ID:** identifier for a table snapshot in Iceberg metadata.
- **Dataset artifact:** a concrete set of rows/files published for downstream use.
- **Dataset fingerprint:** a digest computed according to a declared canonicalization algorithm.
- **Logical dataset version:** a human-meaningful release such as `fraud-training-2026-10-v3`.
- **Run manifest:** the record linking data, feature/code versions, parameters, environment, model artifact, and metrics.
- **Model identity:** a model artifact plus its model configuration/version; it is not the same as dataset identity.

A snapshot ID does not guarantee that the snapshot will be retained forever. A hash identifies bytes or canonicalized content under a specified algorithm; it does not prove the data was correctly constructed. A logical version is only useful if it resolves to immutable references. None of these alone guarantees full reproducibility.

## 4. Constructing point-in-time training datasets

### 4.1 Define the prediction problem before writing SQL

Example: at each transaction authorization time, predict whether the transaction is fraudulent after an outcome-maturation period.

Define:

- **Entity:** `transaction_id`, with `customer_id` as a grouping key.
- **Prediction time:** `prediction_time`, when the model would have scored the transaction.
- **Label:** `is_fraud`, determined by a defined investigation/chargeback process.
- **Label maturity:** only include examples whose outcome observation window has elapsed and whose label source is sufficiently complete.
- **Features:** customer behavior and transaction context that were available at prediction time.
- **Split policy:** entity grouping and/or temporal cutoff, according to the evaluation goal.

Labels and features have different temporal rules. A future outcome may be used to construct the label, but it must not leak into features.

### 4.2 Source schemas

A simple training pipeline can use these tables.

**Labels table**

| Column | Meaning |
|---|---|
| `transaction_id` | Unique prediction/example ID |
| `customer_id` | Grouping entity |
| `prediction_time` | Time the prediction would have been made |
| `label` | `0` or `1` |
| `label_observed_at` | When the label became available |
| `label_status` | `mature`, `pending`, `censored`, or `unknown` |

**Feature history table**

| Column | Meaning |
|---|---|
| `customer_id` | Entity key |
| `feature_record_id` | Stable unique source-row identifier for diagnostics and duplicate checks |
| `feature_time` | Business/effective time of the feature state |
| `available_at` | When this value was actually available to the pipeline |
| `orders_30d_count` | Historical count with documented window semantics |
| `amount_30d_sum` | Historical amount aggregate |
| `account_age_days` | Account age as of the recorded state |

For a historical row at time `t`, select only feature records whose effective time and availability time do not exceed `t`. The feature-history grain in this example is one complete feature state per `(customer_id, feature_time, available_at)`; reject duplicate keys before joining rather than selecting an arbitrary tied row. If corrections overwrite old values without retaining availability history, exact replay of what was known at `t` may be impossible; document that limitation instead of claiming perfect point-in-time correctness. A mature label must also have `prediction_time <= label_observed_at <= label_cutoff`; otherwise reject the malformed row or keep it out of the mature training population.

### 4.3 Point-in-time join

Conceptual SQL pattern for state features:

```sql
WITH eligible AS (
  SELECT
    l.transaction_id,
    l.customer_id,
    l.prediction_time,
    l.label,
    f.feature_time,
    f.available_at,
    f.orders_30d_count,
    f.amount_30d_sum,
    f.account_age_days,
    ROW_NUMBER() OVER (
      PARTITION BY l.transaction_id
      ORDER BY f.feature_time DESC, f.available_at DESC
    ) AS rn
  FROM labels l
  LEFT JOIN feature_history f
    ON l.customer_id = f.customer_id
   AND f.feature_time <= l.prediction_time
   AND f.available_at <= l.prediction_time
  WHERE l.label_status = 'mature'
    AND l.prediction_time <= l.label_observed_at
    AND l.label_observed_at <= :label_cutoff
)
SELECT *
FROM eligible
WHERE rn = 1;
```

This example chooses the latest eligible state per transaction. Before running it, assert that `feature_record_id` is unique and `(customer_id, feature_time, available_at)` has no duplicates; otherwise fail the build rather than relying on a nondeterministic `ROW_NUMBER()` tie. Add a maximum lookback if stale state should not be accepted. For rolling event aggregates, calculate the events inside the window; do not replace the aggregation with a latest-state join.

**Leakage assertion:** for every matched feature record, `feature_time <= prediction_time` and `available_at <= prediction_time`. A test should fail if either condition is violated.

### 4.4 Build an immutable local dataset

The following local implementation uses synthetic, timestamped data. It is a runnable teaching baseline, not a replacement for a distributed table engine on large data.

Save as `src/build_dataset.py`:

```python
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
import unicodedata

import numpy as np
import pandas as pd


def hash_split(entity_id: str, *, salt: str = "fraud-split-v1") -> str:
    """Stable entity split; version the salt and entity normalization policy."""
    if pd.isna(entity_id):
        raise ValueError("entity_id must not be null")
    normalized = str(entity_id).strip()
    if not normalized:
        raise ValueError("entity_id must not be empty")
    digest = hashlib.sha256(f"{salt}|{normalized}".encode("utf-8")).digest()
    bucket = int.from_bytes(digest[:8], "big") % 10_000
    if bucket < 8_000:
        return "train"
    if bucket < 9_000:
        return "validation"
    return "test"


def _utc_series(frame: pd.DataFrame, columns: list[str]) -> None:
    for column in columns:
        frame[column] = pd.to_datetime(frame[column], utc=True, errors="raise")


def build_training_set(
    labels: pd.DataFrame,
    feature_history: pd.DataFrame,
    *,
    label_cutoff: pd.Timestamp,
) -> pd.DataFrame:
    required_labels = {
        "transaction_id", "customer_id", "prediction_time", "label",
        "label_observed_at", "label_status",
    }
    required_features = {
        "feature_record_id", "customer_id", "feature_time", "available_at",
        "orders_30d_count", "amount_30d_sum", "account_age_days",
    }
    if missing := required_labels - set(labels.columns):
        raise ValueError(f"labels missing {sorted(missing)}")
    if missing := required_features - set(feature_history.columns):
        raise ValueError(f"features missing {sorted(missing)}")

    labels = labels.copy()
    features = feature_history.copy()
    _utc_series(labels, ["prediction_time", "label_observed_at"])
    _utc_series(features, ["feature_time", "available_at"])
    cutoff = pd.to_datetime(label_cutoff, utc=True, errors="raise")

    if labels[["transaction_id", "customer_id", "prediction_time"]].isna().any().any():
        raise ValueError("transaction_id, customer_id, and prediction_time must be non-null")
    if labels["transaction_id"].duplicated().any():
        raise ValueError("transaction_id must be unique per prediction row")
    if features[["customer_id", "feature_time", "available_at"]].isna().any().any():
        raise ValueError("feature customer_id, feature_time, and available_at must be non-null")
    allowed_statuses = {"mature", "pending", "censored", "unknown"}
    if not set(labels["label_status"].dropna().unique()).issubset(allowed_statuses):
        raise ValueError("Unexpected label_status value")
    if labels["label_status"].isna().any():
        raise ValueError("label_status must not be null")
    malformed_time = labels["label_observed_at"].notna() & (
        labels["label_observed_at"] < labels["prediction_time"]
    )
    if malformed_time.any():
        raise ValueError("label_observed_at cannot precede prediction_time")
    mature = labels["label_status"].eq("mature")
    if labels.loc[mature, "label_observed_at"].isna().any():
        raise ValueError("mature labels must have label_observed_at")
    if labels.loc[mature, "label"].isna().any() or not set(
        labels.loc[mature, "label"].unique()
    ).issubset({0, 1}):
        raise ValueError("mature labels must be non-null binary 0/1 values")

    if features["feature_record_id"].isna().any() or features["feature_record_id"].duplicated().any():
        raise ValueError("feature_record_id must be non-null and unique")
    temporal_key = ["customer_id", "feature_time", "available_at"]
    if features.duplicated(temporal_key).any():
        raise ValueError(
            "Ambiguous feature history: duplicate customer_id/feature_time/available_at"
        )

    eligible_labels = labels.loc[
        mature
        & labels["label_observed_at"].le(cutoff)
        & labels["prediction_time"].le(cutoff)
    ].copy()

    # A left join retains label rows with no historical feature state.
    candidates = eligible_labels.merge(features, on="customer_id", how="left", validate="many_to_many")
    eligible = candidates.loc[
        candidates["feature_time"].le(candidates["prediction_time"])
        & candidates["available_at"].le(candidates["prediction_time"])
    ].copy()
    eligible = eligible.sort_values(
        ["transaction_id", "feature_time", "available_at"], kind="mergesort"
    )
    latest = eligible.drop_duplicates("transaction_id", keep="last")

    feature_columns = [
        "transaction_id", "customer_id", "prediction_time", "label",
        "feature_time", "available_at", "orders_30d_count",
        "amount_30d_sum", "account_age_days",
    ]
    result = latest[feature_columns].copy()
    missing_ids = set(eligible_labels["transaction_id"]) - set(result["transaction_id"])
    if missing_ids:
        missing = eligible_labels.loc[
            eligible_labels["transaction_id"].isin(missing_ids),
            ["transaction_id", "customer_id", "prediction_time", "label"],
        ].copy()
        for col in ["feature_time", "available_at", "orders_30d_count", "amount_30d_sum", "account_age_days"]:
            missing[col] = pd.NA
        result = pd.concat([result, missing[feature_columns]], ignore_index=True)

    result["split"] = result["customer_id"].astype(str).map(hash_split)
    matched = result["feature_time"].notna()
    if not (result.loc[matched, "feature_time"] <= result.loc[matched, "prediction_time"]).all():
        raise AssertionError("Future effective-time feature detected")
    if not (result.loc[matched, "available_at"] <= result.loc[matched, "prediction_time"]).all():
        raise AssertionError("Feature unavailable at prediction time")
    return result.sort_values(
        ["prediction_time", "transaction_id"], kind="mergesort"
    ).reset_index(drop=True)


def _canonical_value(value: Any) -> dict[str, Any]:
    """Typed scalar encoding; explicit tags avoid string/null sentinel collisions."""
    if value is None or value is pd.NA or value is pd.NaT:
        return {"type": "null"}
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, (pd.Timestamp, datetime)):
        ts = pd.Timestamp(value)
        if ts.tzinfo is None:
            raise ValueError("Naive timestamps are not allowed in canonical fingerprints")
        return {"type": "timestamp_utc", "value": ts.tz_convert("UTC").isoformat()}
    if isinstance(value, date):
        return {"type": "date", "value": value.isoformat()}
    if isinstance(value, bool):
        return {"type": "bool", "value": value}
    if isinstance(value, int):
        return {"type": "int", "value": str(value)}
    if isinstance(value, float):
        if np.isnan(value):
            return {"type": "float_nan"}
        if np.isposinf(value):
            return {"type": "float_pos_inf"}
        if np.isneginf(value):
            return {"type": "float_neg_inf"}
        return {"type": "float_hex", "value": value.hex()}
    if isinstance(value, Decimal):
        return {"type": "decimal", "value": str(value)}
    if isinstance(value, str):
        return {"type": "str_nfc", "value": unicodedata.normalize("NFC", value)}
    raise TypeError(f"Unsupported fingerprint value type: {type(value).__name__}")


def canonical_fingerprint(df: pd.DataFrame, columns: list[str]) -> str:
    """Fingerprint typed scalar rows; duplicate row multiplicity is preserved."""
    if len(columns) != len(set(columns)) or set(columns) - set(df.columns):
        raise ValueError("columns must be unique names present in the DataFrame")
    schema = [{"name": col, "dtype": str(df[col].dtype)} for col in columns]
    encoded_rows = []
    for values in df[columns].itertuples(index=False, name=None):
        encoded = [ _canonical_value(value) for value in values ]
        encoded_rows.append(json.dumps(encoded, sort_keys=True, separators=(",", ":")))
    encoded_rows.sort()  # preserves duplicate multiplicity while ignoring input row order
    payload = json.dumps(
        {"schema": schema, "rows": encoded_rows},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def publish_snapshot(
    df: pd.DataFrame,
    root: Path,
    dataset_version: str,
    *,
    metadata: dict[str, Any],
) -> dict:
    """Publish a write-once directory with required provenance metadata."""
    if not dataset_version or dataset_version in {".", ".."} or Path(dataset_version).name != dataset_version:
        raise ValueError("dataset_version must be a single path-safe directory name")
    required_metadata = {
        "source_refs", "feature_definition_commit", "dataset_build_code_commit",
        "label_cutoff", "split_policy", "schema_version", "python_version",
        "environment_lockfile_sha256",
    }
    if missing := required_metadata - set(metadata):
        raise ValueError(f"manifest metadata missing {sorted(missing)}")
    if not isinstance(metadata["source_refs"], dict) or not metadata["source_refs"]:
        raise ValueError("source_refs must identify at least one pinned source")
    root.mkdir(parents=True, exist_ok=True)
    destination = root / dataset_version
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite immutable snapshot: {destination}")
    staging = Path(tempfile.mkdtemp(prefix=f".{dataset_version}.staging-", dir=root))
    try:
        output = staging / "training.parquet"
        df.to_parquet(output, index=False)
        # Fingerprint the serialized-and-read-back artifact so the verifier uses
        # the same schema/value representation that downstream consumers read.
        stored_df = pd.read_parquet(output)
        manifest = {
            **metadata,
            "dataset_version": dataset_version,
            "artifact_uri": str(destination.resolve()),
            "row_count": int(len(stored_df)),
            "columns": list(stored_df.columns),
            "dtypes": {col: str(dtype) for col, dtype in stored_df.dtypes.items()},
            "canonical_content_sha256": canonical_fingerprint(stored_df, list(stored_df.columns)),
            "parquet_file_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "fingerprint_algorithm": "SHA-256 over canonical typed scalar rows + schema; sorted row encodings",
        }
        manifest_path = staging / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        # Atomic directory rename on the same filesystem; destination must remain absent.
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite immutable snapshot: {destination}")
        os.rename(staging, destination)
        return manifest
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
```

Example call (run after building `dataset` and resolving the pinned source references):

```python
manifest = publish_snapshot(
    dataset,
    Path("data/snapshots"),
    "fraud-training-2026-10-19-v1",
    metadata={
        "source_refs": {
            "labels": "synthetic-fixture:labels-v1",
            "features": "synthetic-fixture:feature-history-v1",
        },
        "feature_definition_commit": "<actual-git-commit>",
        "dataset_build_code_commit": "<actual-git-commit>",
        "label_cutoff": "2026-10-01T00:00:00Z",
        "split_policy": "sha256(customer_id, salt=fraud-split-v1)",
        "schema_version": "fraud-training-schema-v2",
        "python_version": "<actual-python-version>",
        "environment_lockfile_sha256": "<sha256-of-uv.lock>",
    },
)
```

Replace placeholders with real identifiers before treating this as an auditable run; do not publish the angle-bracket placeholders to a production manifest.

A minimum regression test suite for the temporal join and canonicalizer (place in `tests/test_dataset_core.py`) is:

```python
import pandas as pd
import pytest

from src.build_dataset import build_training_set, canonical_fingerprint


def fixtures():
    labels = pd.DataFrame([
        {"transaction_id": "t1", "customer_id": "c1", "prediction_time": "2026-01-10T12:00:00Z",
         "label": 1, "label_observed_at": "2026-03-15T00:00:00Z", "label_status": "mature"},
    ])
    features = pd.DataFrame([
        {"feature_record_id": "r1", "customer_id": "c1", "feature_time": "2026-01-10T11:00:00Z",
         "available_at": "2026-01-10T11:05:00Z", "orders_30d_count": 2,
         "amount_30d_sum": 10.0, "account_age_days": 90},
        # Effective time is old enough, but this record arrived after prediction.
        {"feature_record_id": "r2", "customer_id": "c1", "feature_time": "2026-01-10T11:30:00Z",
         "available_at": "2026-01-10T12:30:00Z", "orders_30d_count": 99,
         "amount_30d_sum": 999.0, "account_age_days": 90},
        # Both effective time and availability are in the future.
        {"feature_record_id": "r3", "customer_id": "c1", "feature_time": "2026-01-10T13:00:00Z",
         "available_at": "2026-01-10T13:00:00Z", "orders_30d_count": 100,
         "amount_30d_sum": 1000.0, "account_age_days": 90},
    ])
    return labels, features


def test_late_and_future_features_are_excluded():
    labels, features = fixtures()
    result = build_training_set(labels, features, label_cutoff=pd.Timestamp("2026-04-01T00:00:00Z"))
    assert len(result) == 1
    assert result.loc[0, "orders_30d_count"] == 2
    assert result.loc[0, "available_at"] <= result.loc[0, "prediction_time"]


def test_fingerprint_is_order_invariant_and_type_sensitive():
    left = pd.DataFrame({"x": pd.Series([1, 2], dtype="int64")})
    reordered = left.iloc[::-1].reset_index(drop=True)
    as_strings = pd.DataFrame({"x": pd.Series(["1", "2"], dtype="string")})
    assert canonical_fingerprint(left, ["x"]) == canonical_fingerprint(reordered, ["x"])
    assert canonical_fingerprint(left, ["x"]) != canonical_fingerprint(as_strings, ["x"])


def test_ambiguous_feature_history_fails_closed():
    labels, features = fixtures()
    duplicate = features.iloc[[0]].copy()
    duplicate["feature_record_id"] = "r1-duplicate"
    features = pd.concat([features, duplicate], ignore_index=True)
    with pytest.raises(ValueError, match="Ambiguous feature history"):
        build_training_set(labels, features, label_cutoff=pd.Timestamp("2026-04-01T00:00:00Z"))
```

These tests do not exercise Parquet writing or atomic directory publication; that path requires a Parquet engine such as PyArrow and should have a separate integration test.

The implementation preserves labels that have no eligible feature state and leaves the feature columns null. Production policy may reject these rows, apply a documented default, or retain them with a missing-history indicator; do not silently convert missing history to zero. For a large dataset, replace the many-to-many local candidate join with an engine-native temporal join, but keep the same invariants.

### 4.5 Deterministic train/validation/test splits

The `hash_split` function maps an entity ID to a stable bucket using SHA-256 and a documented salt. It does not use Python's built-in `hash()`, whose output is intentionally randomized across processes by default. The builder's default split is specifically an **entity-isolation split**, not a chronological split.

This guarantees stable entity assignment under the stated algorithm, salt, and entity normalization. It does **not** guarantee temporal independence or prevent near-duplicate leakage automatically. For a future-time prediction objective, use `assign_time_split` in Section 8.2 and record the cutoffs in the manifest; do not report the entity-hash result as a temporal holdout.

- Use **entity-level hash splits** when the intended evaluation is on unseen entities or when repeated rows for one entity must never cross splits.
- Use **time-based splits** when production predicts future outcomes and temporal generalization is the goal.
- Use **group-aware splits** for sessions, households, devices, merchants, or other correlated units.
- Use **stratification** when appropriate to preserve label proportions, but do not let stratification override a required time boundary.
- Use a combined policy when needed: first define a time cutoff, then group/hash within the eligible time range.

To prevent leakage, check all relevant grouping keys and deduplicate/cluster near-identical examples before splitting. Entity hashing alone cannot detect two different IDs that refer to the same real-world entity or near-duplicate records copied across IDs.

## 5. Dataset versioning strategies

No single versioning tool solves every problem. Choose the layer that fits the source and required recovery path.

### 5.1 Delta Lake time travel

Delta Lake records table versions through its transaction log. A version can be queried using SQL syntax such as:

```sql
SELECT *
FROM fraud_features VERSION AS OF 42;
```

Exact syntax and support depend on the Delta Lake/Spark/Databricks environment. Record the table identifier, version number, relevant source table versions, and query/code commit. The output dataset should also have its own immutable identity.

**Strengths:** transactional table history, convenient replay/debugging, and consistent table reads.

**Limitations:** retention and log/data-file cleanup can make old versions unavailable; time travel does not freeze external sources or feature code. A version number without table identity is ambiguous.

Use when the training data is produced from Delta tables and the required versions remain retained. Before snapshot expiration or vacuum operations, verify whether any registered training run still depends on those files.

### 5.2 Apache Iceberg snapshot IDs

Iceberg commits table snapshots with snapshot IDs and metadata. Record the catalog/table identity and exact snapshot ID, not merely a human timestamp. Query and time-travel syntax depends on the engine/catalog integration.

**Strengths:** table snapshots and metadata-driven evolution, useful in open lakehouse environments.

**Limitations:** snapshot expiration and orphan-file cleanup can remove historical data; engine support and SQL syntax differ. A snapshot of one table does not automatically pin all upstream tables.

Use when Iceberg is the table format, and record snapshot IDs for every input table needed to reproduce the dataset.

### 5.3 Immutable dated Parquet snapshots

Write the training dataset to a unique versioned path, such as:

```text
data/snapshots/fraud-training-2026-10-19-v1/training.parquet
data/snapshots/fraud-training-2026-10-19-v1/manifest.json
```

**Strengths:** simple to inspect, portable, and easy to retain independently of source table history.

**Limitations:** storage duplication, metadata management, multi-file consistency, access control, and lifecycle policies. A directory date alone does not make files immutable; enforce write-once publishing and permissions.

For partitioned/multi-file datasets, hash a manifest containing sorted relative paths, file sizes, and file checksums; separately compute a logical row/content fingerprint if you need to compare equivalent data despite different file layouts.

### 5.4 DVC

DVC tracks data artifacts and pipeline stages alongside Git while large data can live in configured storage. Git commits identify the DVC metadata version; the metadata points to content-addressed artifacts.

**Strengths:** Git-friendly workflows, local experimentation, pipeline dependency tracking, remote artifact storage.

**Limitations:** requires disciplined commits and remote retention; data access and collaboration need setup. A DVC-tracked pointer is not useful if the remote object has been deleted or is inaccessible.

Typical workflow (run from the Git project root; verify command options against the installed DVC release):

```bash
dvc init
# Configure a durable remote once; use your platform's credential mechanism.
dvc remote add --default storage s3://YOUR-BUCKET/YOUR-PREFIX
dvc add data/snapshots/fraud-training-2026-10-19-v1
git add data/snapshots/fraud-training-2026-10-19-v1.dvc .gitignore .dvc/config
# Keep credentials out of Git; DVC supports local/ignored configuration for secrets.
git commit -m "Track fraud training dataset v1"
dvc push
```

To compare cleaning rules, create a Git branch, change the transformation, rebuild the output, track the new artifact, and compare both the dataset validation report and model evaluation.

### 5.5 lakeFS

lakeFS provides Git-like branches, commits, and merges for object-store data. It supports isolated data changes and reproducible references to committed state when configured and retained correctly.

**Strengths:** branching/commit workflows for data, useful for testing transformation changes without mutating the main branch.

**Limitations:** requires lakeFS and object storage setup; semantics and integrations depend on deployment. A branch name can move; use a committed reference/hash for a reproducible run, and protect the objects from lifecycle deletion.

Example workflow, expressed conceptually:

1. Create a branch from a known committed data state.
2. Run the cleaning-rule change against that branch.
3. Validate and build a training dataset.
4. Commit the changed data state.
5. record the commit/reference in the run manifest.
6. Compare dataset hashes, slices, and model metrics against the base commit.

### 5.6 MLflow dataset references and registries

MLflow tracks experiments/runs, parameters, metrics, tags, and artifacts. Depending on MLflow version and API, dataset inputs can be logged with source/name/digest/schema/profile metadata. This metadata improves traceability but does not itself preserve every source row forever.

Log both:
- MLflow dataset input metadata, where supported;
- explicit stable identifiers such as source table + Delta version/Iceberg snapshot, immutable output URI, logical dataset version, and content fingerprint.

A registered model/version and a training dataset reference are related through lineage but are not interchangeable. Core MLflow Tracking dataset inputs are metadata, not a universal standalone dataset registry with guaranteed retention and approval semantics. If your platform exposes a dataset registry/catalog, record its immutable dataset ID; otherwise implement a governed release index over immutable artifacts/manifests and link it to MLflow runs. The MLflow Model Registry stores model lifecycle metadata/artifacts; it is not a replacement for durable dataset storage.

### 5.7 Comparison

| Strategy | Primary identity | Best fit | Main risk |
|---|---|---|---|
| Delta time travel | Table ID + Delta version | Delta-backed tables | Historical files/logs expired |
| Iceberg | Catalog/table + snapshot ID | Iceberg tables | Snapshot/metadata retention |
| Parquet snapshot | Immutable URI + manifest + hashes | Portable dataset releases | Accidental overwrite or missing files |
| DVC | Git commit + DVC-tracked artifact hashes | Versioned local/remote datasets | Remote objects unavailable |
| lakeFS | Repository + committed data reference | Branching data workflows | Mutable branch refs / retention |
| MLflow | Experiment/run + dataset metadata + artifact refs | Experiment lineage | Metadata does not guarantee source retention |

Use multiple layers when appropriate: table snapshots to read consistent source state, an immutable training output for downstream reuse, a canonical fingerprint to compare content, and a run manifest to link it to the model.

## 6. Dataset fingerprints and manifests

### 6.1 What a hash proves

A cryptographic hash such as SHA-256 gives a compact digest of the bytes supplied to it. If the same bytes are hashed with the same algorithm, the digest should match. It does not prove the data is true, unbiased, complete, legally usable, or point-in-time correct.

A **file hash** changes if serialization metadata, compression, row order, or Parquet layout changes, even when logical rows are the same.

A **logical content fingerprint** requires a canonicalization contract:
- fixed column order and schema (the implementation below includes both in the digest);
- deterministic row encoding and sorting, with duplicate row multiplicity preserved;
- consistent timestamp timezone/format;
- explicit decimal/float/NaN/null semantics and type tags;
- stable Unicode normalization where relevant;
- consistent treatment of nested structures;
- documented encoding and line endings.

The implementation in Section 4 is a teaching canonicalizer for scalar values, not a universal cross-engine standard. It deliberately rejects unsupported nested types and naive timestamps; production systems should define canonicalization for every supported type and test cross-version compatibility. A file checksum still identifies the exact serialized file, not logical equivalence.

### 6.2 Example manifest

```json
{
  "dataset_name": "fraud_training",
  "dataset_version": "fraud-training-2026-10-19-v1",
  "source_refs": {
    "labels": "catalog.labels@version-or-snapshot",
    "features": "catalog.feature_history@version-or-snapshot"
  },
  "feature_definition_commit": "git-sha",
  "dataset_build_code_commit": "git-sha",
  "label_cutoff": "2026-10-01T00:00:00Z",
  "split_policy": "sha256(customer_id, salt=fraud-split-v1)",
  "row_count": 125000,
  "schema_version": "fraud-training-schema-v2",
  "canonical_content_sha256": "...",
  "artifact_uri": "s3://.../fraud-training/fraud-training-2026-10-19-v1/",
  "python_version": "3.12.x",
  "environment_lockfile_sha256": "<sha256-of-uv.lock>",
  "created_by_pipeline_run_id": "..."
}
```

The values above are illustrative placeholders, not real source identifiers. Do not write fake values into a production manifest; populate them from the actual job execution.

## 7. Experiment tracking with MLflow

### 7.1 Concepts

- **Experiment:** grouping of related runs.
- **Run:** one execution of training/evaluation with a unique run ID.
- **Parameters:** settings such as model type, regularization, split policy, and cutoff.
- **Metrics:** evaluation outputs with explicit evaluation dataset identity.
- **Artifacts:** model, validation report, plots, manifest, and diagnostic outputs.
- **Tags:** searchable metadata such as Git commit, dataset version, environment digest, and pipeline version.
- **Dataset input metadata:** records source/name/digest/schema/profile where supported by the installed API.

### 7.2 Example tracking code

Save this as `src/train.py` and run it from the project root after the dataset snapshot has been published and validated: `uv run python -m src.train`.

This example logs a model, metrics, parameters, tags, and a manifest. It assumes the dataset has already passed validation and contains the selected feature columns and a binary `label`. It is a minimal local example; MLflow model APIs can evolve, so verify against your pinned release.

```python
import hashlib
import json
import os
import platform
import subprocess
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.build_dataset import canonical_fingerprint


DATASET_VERSION = os.environ.get("DATASET_VERSION", "fraud-training-2026-10-19-v1")
DATASET_DIR = Path("data/snapshots") / DATASET_VERSION
DATA_PATH = DATASET_DIR / "training.parquet"
MANIFEST_PATH = DATASET_DIR / "manifest.json"
FEATURES = ["orders_30d_count", "amount_30d_sum", "account_age_days"]


def required_git_metadata() -> tuple[str, bool]:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    # Ignore generated data/model outputs; only source and environment files
    # must be committed for this local example.
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--", "pyproject.toml", "uv.lock", "src", "tests"],
        text=True,
    )
    return commit, bool(status.strip())


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if not DATA_PATH.is_file() or not MANIFEST_PATH.is_file():
    raise FileNotFoundError(f"Expected immutable dataset and manifest under {DATASET_DIR}")
if not Path("uv.lock").is_file():
    raise FileNotFoundError("uv.lock is required; run `uv lock` and commit it first")

manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
df = pd.read_parquet(DATA_PATH)
if manifest.get("dataset_version") != DATASET_VERSION:
    raise ValueError("Dataset version does not match its manifest")
if manifest.get("row_count") != len(df):
    raise ValueError("Dataset row count differs from its manifest")
if manifest.get("parquet_file_sha256") != sha256_file(DATA_PATH):
    raise ValueError("Parquet file checksum does not match its manifest")
if manifest.get("canonical_content_sha256") != canonical_fingerprint(df, list(df.columns)):
    raise ValueError("Canonical dataset fingerprint does not match its manifest")

required = set(FEATURES + ["label", "split", "customer_id", "prediction_time"])
if required - set(df.columns):
    raise ValueError(f"Dataset missing columns: {sorted(required - set(df.columns))}")
df["prediction_time"] = pd.to_datetime(df["prediction_time"], utc=True, errors="raise")
if df["label"].isna().any() or not set(df["label"].unique()).issubset({0, 1}):
    raise ValueError("Labels must be non-null binary 0/1 values")
if df["split"].isna().any() or set(df["split"].unique()) != {"train", "validation", "test"}:
    raise ValueError("All three non-null splits must be present")
split_policy = manifest["split_policy"]
if split_policy.startswith("sha256(customer_id"):
    if df.groupby("customer_id")["split"].nunique().max() != 1:
        raise ValueError("Customer appears in more than one split under entity-hash policy")
elif split_policy.startswith("time:"):
    max_train = df.loc[df["split"].eq("train"), "prediction_time"].max()
    min_valid = df.loc[df["split"].eq("validation"), "prediction_time"].min()
    max_valid = df.loc[df["split"].eq("validation"), "prediction_time"].max()
    min_test = df.loc[df["split"].eq("test"), "prediction_time"].min()
    if not max_train < min_valid or not max_valid < min_test:
        raise ValueError("Time-based split boundaries overlap or are out of order")
else:
    raise ValueError(f"Unsupported split policy in manifest: {split_policy}")

train = df.loc[df["split"].eq("train"), FEATURES + ["label"]].copy()
valid = df.loc[df["split"].eq("validation"), FEATURES + ["label"]].copy()
if train.empty or valid.empty or train["label"].nunique() != 2 or valid["label"].nunique() != 2:
    raise ValueError("Train and validation must be non-empty and each contain both classes for ROC AUC")
train_values = train[FEATURES].to_numpy(dtype=float, na_value=np.nan)
valid_values = valid[FEATURES].to_numpy(dtype=float, na_value=np.nan)
if np.isinf(train_values).any() or np.isinf(valid_values).any():
    raise ValueError("Features contain +/- infinity; normalize or reject them before training")
if not np.isfinite(train_values).any(axis=0).all():
    raise ValueError("Every feature must have at least one finite training value")

# Imputation/scaling are fitted only on training rows because they live inside the pipeline.
model = make_pipeline(
    SimpleImputer(strategy="median"),
    StandardScaler(),
    LogisticRegression(max_iter=1000, class_weight="balanced", random_state=17),
)

train_input = mlflow.data.from_pandas(
    train, source=str(DATA_PATH), name=f"{DATASET_VERSION}-train", targets="label"
)
valid_input = mlflow.data.from_pandas(
    valid, source=str(DATA_PATH), name=f"{DATASET_VERSION}-validation", targets="label"
)
commit, dirty_worktree = required_git_metadata()
if dirty_worktree:
    raise RuntimeError("Commit the code/configuration before training, or version the dirty diff explicitly")
lockfile_sha256 = sha256_file(Path("uv.lock"))
if manifest.get("environment_lockfile_sha256") != lockfile_sha256:
    raise ValueError("Current uv.lock differs from the environment lock recorded in the dataset manifest")
if manifest.get("python_version") != platform.python_version():
    raise ValueError("Current Python version differs from the dataset-build environment in the manifest")

model_params = {
    "model": "LogisticRegression",
    "max_iter": 1000,
    "class_weight": "balanced",
    "seed": 17,
    "split_policy": split_policy,
    "dataset_version": DATASET_VERSION,
}
mlflow.set_experiment("fraud-training-data-lineage")
with mlflow.start_run() as run:
    mlflow.log_input(train_input, context="training")
    mlflow.log_input(valid_input, context="validation")
    mlflow.log_params(model_params)
    mlflow.set_tags({
        "git_commit": commit,
        "git_dirty_worktree": str(dirty_worktree).lower(),
        "dataset_version": DATASET_VERSION,
        "dataset_fingerprint": manifest["canonical_content_sha256"],
        "dataset_manifest_uri": str(MANIFEST_PATH),
        "parquet_file_sha256": manifest["parquet_file_sha256"],
        "uv_lock_sha256": lockfile_sha256,
        "python_version": platform.python_version(),
        "validation_split": "validation",
    })

    model.fit(train[FEATURES], train["label"])
    probabilities = model.predict_proba(valid[FEATURES])[:, 1]
    auc = float(roc_auc_score(valid["label"], probabilities))
    mlflow.log_metric("validation_auc", auc)
    model_info = mlflow.sklearn.log_model(model, name="fraud_model")
    # A checksum identifies this serialized file's bytes; it is not a guarantee
    # that a future joblib serialization will be byte-identical.
    import joblib
    run_artifact_dir = Path("artifacts") / run.info.run_id
    run_artifact_dir.mkdir(parents=True, exist_ok=True)
    local_model_path = run_artifact_dir / "model.joblib"
    joblib.dump(model, local_model_path)
    model_joblib_sha256 = sha256_file(local_model_path)
    mlflow.log_artifact(str(local_model_path))

    run_manifest = {
        "mlflow_run_id": run.info.run_id,
        "dataset_version": DATASET_VERSION,
        "dataset_fingerprint": manifest["canonical_content_sha256"],
        "dataset_manifest_uri": str(MANIFEST_PATH),
        "source_refs": manifest["source_refs"],
        "feature_definition_commit": manifest["feature_definition_commit"],
        "dataset_build_code_commit": manifest["dataset_build_code_commit"],
        "training_code_commit": commit,
        "git_dirty_worktree": dirty_worktree,
        "label_cutoff": manifest["label_cutoff"],
        "split_policy": manifest["split_policy"],
        "schema_version": manifest["schema_version"],
        "uv_lock_sha256": lockfile_sha256,
        "python_version": platform.python_version(),
        "feature_columns": FEATURES,
        "train_rows": int(len(train)),
        "validation_rows": int(len(valid)),
        "train_split_fingerprint": canonical_fingerprint(train, FEATURES + ["label"]),
        "validation_split_fingerprint": canonical_fingerprint(valid, FEATURES + ["label"]),
        "validation_time_min": str(df.loc[df["split"].eq("validation"), "prediction_time"].min()),
        "validation_time_max": str(df.loc[df["split"].eq("validation"), "prediction_time"].max()),
        "validation_auc": auc,
        "evaluation_metric": "sklearn.metrics.roc_auc_score",
        "model_uri": model_info.model_uri,
        "model_parameters": model_params,
        "model_joblib_artifact": str(local_model_path),
        "model_joblib_sha256": model_joblib_sha256,
    }
    manifest_out = run_artifact_dir / "run_manifest.json"
    manifest_out.write_text(json.dumps(run_manifest, indent=2, sort_keys=True), encoding="utf-8")
    mlflow.log_artifact(str(manifest_out))
```

This example deliberately fails closed when the immutable artifact, manifest, lockfile, or Git metadata is missing. It uses the precomputed `split` column rather than silently re-splitting rows, verifies the stored hashes before training, and keeps imputation inside the sklearn pipeline so its statistics are learned from training rows only. The sample manifest carries source table/snapshot IDs, feature-definition and dataset-build code commits, label cutoff, split-policy version, Python version, and lockfile digest; the training example rejects an environment mismatch before fitting. Add a container image digest when applicable. For a time-based evaluation, set the manifest policy to `time:<recorded-boundaries>` and record the actual train/validation/test cutoffs; the example checks chronological ordering rather than incorrectly requiring customers to be isolated across time. The model is logged both as an MLflow model and as a local joblib artifact with a byte checksum. That checksum identifies the serialized artifact produced in this run, but does not promise that a future serialization will produce identical bytes.

The example targets current MLflow APIs (`mlflow.data.from_pandas`, `mlflow.log_input`, and `mlflow.sklearn.log_model(..., name=...)`). Pin MLflow in `uv.lock` and verify the installed release's API. The code is a local pattern, not evidence that an MLflow server or remote artifact store was started in this environment.

## 8. Deterministic splits and leakage prevention

### 8.1 Stable entity assignment

Use a stable hash function and versioned salt. Normalize entity identifiers before hashing (for example, trim whitespace and apply a documented case policy where identifiers are case-insensitive). Changing the salt or thresholds changes assignments and should be treated as a split-policy version change.

Test that each grouping entity maps to exactly one split:

```python
assert dataset.groupby("customer_id")["split"].nunique().max() == 1
```

If sessions or households can link multiple customers, validate those group keys too. Near-duplicates need a separate duplicate-detection or clustering step; stable entity hashing cannot detect all duplicates.

### 8.2 When time-based splits are required

The `build_training_set` example above uses **entity-hash splits**, which answer “how well do we generalize to unseen customers?” They are not a substitute for future-time evaluation. For production forecasting or fraud/churn decisions on future examples, use chronological cutoffs. A minimal implementation for an already-built dataset is:

```python
import pandas as pd


def assign_time_split(
    df: pd.DataFrame,
    *,
    train_end: str,
    validation_end: str,
    test_end: str,
) -> pd.DataFrame:
    result = df.copy()
    times = pd.to_datetime(result["prediction_time"], utc=True, errors="raise")
    if times.isna().any():
        raise ValueError("prediction_time must be non-null for time-based splitting")
    t1, t2, t3 = [pd.to_datetime(x, utc=True, errors="raise") for x in
                  (train_end, validation_end, test_end)]
    if not t1 < t2 < t3:
        raise ValueError("Require train_end < validation_end < test_end")
    result["split"] = pd.NA
    result.loc[times < t1, "split"] = "train"
    result.loc[(times >= t1) & (times < t2), "split"] = "validation"
    result.loc[(times >= t2) & (times < t3), "split"] = "test"
    result = result.loc[result["split"].notna()].copy()
    if result.empty or set(result["split"].unique()) != {"train", "validation", "test"}:
        raise ValueError("Each time split must contain rows; revise cutoffs or data range")
    return result
```

This assumes all labels in the chosen evaluation window have matured by the declared label cutoff. Check maturity completeness before comparing models; otherwise recent test examples can be selectively missing labels. Ensure future outcomes and post-cutoff data never enter feature construction. The same customer may legitimately appear in different time periods when that reflects deployment, but it changes the evaluation question. If the goal is unseen-customer generalization, combine time boundaries with group separation and explicitly define what happens to entities spanning boundaries.

### 8.3 Leakage checklist

- [ ] Features were available at the prediction time.
- [ ] Label fields and post-outcome fields are excluded from model inputs.
- [ ] No customer/session/group is split across partitions when the evaluation requires group independence.
- [ ] Near-duplicate records do not cross partitions.
- [ ] Scalers, imputers, encoders, and feature selection are fitted on training data only.
- [ ] Sampling happens after defining the evaluation population, with a separate policy for training-only balancing.
- [ ] Time windows and label-maturation cutoffs are documented.
- [ ] Test data is not repeatedly used to choose transformations or hyperparameters.

## 9. Label quality, sampling, and class imbalance

### 9.1 Delayed labels

Fraud chargebacks and churn confirmations can arrive weeks later. A label that is still pending should not be treated as a negative. Define a maturity rule, such as “include only examples whose 60-day outcome window has elapsed and whose source has completed processing.” The correct delay depends on the business process and observed label latency.

### 9.2 Label leakage

Label leakage occurs when an input includes the target itself or information only known after the prediction. Examples include a fraud-investigation status populated after review, a chargeback reason, or cancellation date used to predict cancellation. Validate feature lineage and availability timestamps, not just column names.

### 9.3 Noisy and censored labels

- **Noisy labels:** false positives/negatives from imperfect review or weak heuristics. Track source, confidence, and adjudication policy where possible.
- **Censored labels:** outcome is not yet observable or observation ends before the outcome window. Do not automatically label these as negatives.
- **Delayed labels:** label becomes available after the prediction; apply maturity cutoffs and track label latency.
- **Negative sampling:** reducing the number of negative examples to control cost or class balance. Record sampling probabilities/rules and understand that sampled training prevalence differs from deployment prevalence.

### 9.4 Class imbalance and evaluation integrity

Training-only oversampling, undersampling, or class weighting may be useful, but keep validation/test representative of the intended deployment population unless the evaluation explicitly corrects for sampling. Accuracy can be misleading for rare fraud; consider precision, recall, PR-AUC, calibration, and cost-weighted metrics. Do not use a sampled evaluation set to claim production precision without correcting for its sampling design.

Stratification can preserve label proportions for independent, non-temporal rows. It must not break entity grouping or time ordering. For temporal datasets, use time boundaries first and report class prevalence by time slice.

## 10. Training-data validation

Validation is a release gate, not a report that nobody reads. Run it before training and before publishing a new dataset version.

### 10.1 Minimum contract

- Schema: required columns, types, nullability, schema version.
- Uniqueness/grain: one row per declared example key.
- Temporal correctness: no selected feature timestamps after prediction time.
- Label quality: only permitted label states and maturity cutoffs.
- Label balance: counts and prevalence by split and time period.
- Distributions: null rates, ranges, quantiles, category frequencies.
- Completeness: expected time partitions and entity coverage.
- Prior-version comparison: row count, schema, null rate, prevalence, and key feature distributions.
- Reproducibility: source references, code commit, parameters, and fingerprints present.

### 10.2 Simple local gate

```python
import numpy as np
import pandas as pd


def validate_training_dataset(df, *, require_group_isolation=True, min_rows_per_split=1):
    required = {
        "transaction_id", "customer_id", "prediction_time", "label",
        "feature_time", "available_at", "orders_30d_count",
        "amount_30d_sum", "account_age_days", "split",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df = df.copy()
    for column in ["prediction_time", "feature_time", "available_at"]:
        df[column] = pd.to_datetime(df[column], utc=True, errors="raise")
    if df["transaction_id"].isna().any() or df["customer_id"].isna().any():
        raise ValueError("transaction_id and customer_id must be non-null")
    if df["prediction_time"].isna().any():
        raise ValueError("prediction_time must be present for every training row")
    if df["feature_time"].isna().ne(df["available_at"].isna()).any():
        raise ValueError("feature_time and available_at must both be present or both be null")
    if df["transaction_id"].duplicated().any():
        raise ValueError("Expected one row per transaction_id")
    if df["label"].isna().any() or not set(df["label"].unique()).issubset({0, 1}):
        raise ValueError("label must be non-null binary 0/1")
    expected_splits = {"train", "validation", "test"}
    if df["split"].isna().any() or not set(df["split"].unique()).issubset(expected_splits):
        raise ValueError("split must be non-null and one of train/validation/test")
    counts = df["split"].value_counts()
    if any(int(counts.get(split, 0)) < min_rows_per_split for split in expected_splits):
        raise ValueError("One or more splits have fewer than min_rows_per_split rows")
    if require_group_isolation and df.groupby("customer_id")["split"].nunique().max() > 1:
        raise ValueError("customer_id crosses splits under a group-isolated split policy")

    numeric = df[["orders_30d_count", "amount_30d_sum", "account_age_days"]].to_numpy(
        dtype=float, na_value=np.nan
    )
    if np.isinf(numeric).any():
        raise ValueError("Feature values contain infinity")
    matched = df["feature_time"].notna()
    if (df.loc[matched, "feature_time"] >
            df.loc[matched, "prediction_time"]).any():
        raise ValueError("Future feature_time detected")
    if (df.loc[matched, "available_at"] >
            df.loc[matched, "prediction_time"]).any():
        raise ValueError("Feature unavailable at prediction time")
    feature_cols = ["orders_30d_count", "amount_30d_sum", "account_age_days"]
    no_history = df["feature_time"].isna()
    if df.loc[no_history, feature_cols].notna().any().any():
        raise ValueError("Rows without feature history must not contain feature values")

    if (df["orders_30d_count"].dropna() < 0).any():
        raise ValueError("orders_30d_count must be non-negative")
    if (df["amount_30d_sum"].dropna() < 0).any():
        raise ValueError("amount_30d_sum violates this example's contract")

    train_labels = df.loc[df["split"].eq("train"), "label"].dropna()
    if train_labels.nunique() < 2:
        raise ValueError("Training split must contain both classes for this exercise")
```

The last rule is task-specific and may be inappropriate for a very small sample or certain algorithms. For a chronological split where the same customer may legitimately appear in multiple time periods, call `validate_training_dataset(df, require_group_isolation=False)` and retain the separate chronological-order assertions. In production, make thresholds configurable and report label counts and prevalence per split. Avoid universal thresholds that ignore seasonality or legitimate business changes.

### 10.3 Comparing with a prior dataset

A validation report should compare the current version with the prior approved version. Example gates:
- schema breaking change: fail;
- row count change beyond a justified tolerance: warn/fail;
- null-rate increase beyond threshold: fail;
- label prevalence change beyond threshold: investigate/fail;
- key feature quantile shift: warn or fail depending on the feature and use case.

Distribution shift is not automatically bad data; it may reflect a real population change. The gate should route the change for review and prevent silent promotion, rather than forcing all distributions to remain identical forever.

A small version-to-version gate can make the checks concrete. It should compare approved summaries, not blindly require every feature distribution to remain constant:

```python
import numpy as np
import pandas as pd


def dataset_summary(df: pd.DataFrame) -> dict:
    numeric = [c for c in ["orders_30d_count", "amount_30d_sum", "account_age_days"] if c in df]
    return {
        "row_count": int(len(df)),
        "schema": [(c, str(df[c].dtype)) for c in df.columns],
        "null_rates": {c: float(df[c].isna().mean()) for c in df.columns},
        "label_prevalence": float(df["label"].mean()) if len(df) else None,
        "numeric_medians": {c: (float(df[c].median()) if df[c].notna().any() else None) for c in numeric},
    }


def compare_dataset_versions(current: dict, previous: dict, *,
                             max_row_relative_change=0.20,
                             max_null_rate_increase=0.05,
                             max_label_prevalence_change=0.05,
                             max_numeric_median_relative_change=0.50) -> list[str]:
    failures = []
    if current["schema"] != previous["schema"]:
        failures.append("schema changed")
    old_rows = previous["row_count"]
    relative_change = abs(current["row_count"] - old_rows) / max(old_rows, 1)
    if relative_change > max_row_relative_change:
        failures.append(f"row count changed by {relative_change:.1%}")
    for column, null_rate in current["null_rates"].items():
        old_rate = previous["null_rates"].get(column)
        if old_rate is None:
            failures.append(f"new column has no baseline: {column}")
        elif null_rate - old_rate > max_null_rate_increase:
            failures.append(f"null rate increased for {column}")
    old_prev, new_prev = previous["label_prevalence"], current["label_prevalence"]
    if old_prev is not None and new_prev is not None and abs(new_prev - old_prev) > max_label_prevalence_change:
        failures.append("label prevalence changed beyond threshold")
    for column, new_median in current["numeric_medians"].items():
        old_median = previous["numeric_medians"].get(column)
        if old_median is None or new_median is None:
            failures.append(f"missing numeric median baseline for {column}")
            continue
        scale = max(abs(old_median), abs(new_median), 1.0)
        relative_shift = abs(new_median - old_median) / scale
        if relative_shift > max_numeric_median_relative_change:
            failures.append(f"numeric median shifted for {column}: {relative_shift:.1%}")
    return failures
```

The thresholds above are illustrative and should be configured by dataset owner and use case. Treat a failure as a release decision requiring investigation; a real prevalence shift can be valid, but should not pass silently. Add explicit quantile/segment checks for features where median alone cannot detect the failure mode.

### 10.4 Tools at the appropriate level

- **Great Expectations:** define expectations about schema, ranges, completeness, and distributions; integrate validation results into the pipeline.
- **Evidently:** compare data quality and distribution/drift reports between datasets; use thresholds and segments appropriate to the task.
- **TensorFlow Data Validation (TFDV):** schema inference/validation and distribution/skew analysis in TensorFlow-oriented data pipelines.

These tools have different APIs and integration patterns. Pin the installed version and verify current documentation. The core principles—contracts, comparison baselines, failure gates, and actionable reports—remain the same.

## 11. Orchestrating repeatable pipelines

A training-data pipeline should be parameterized, idempotent, observable, and safe to retry.

### 11.1 Logical stages

```text
resolve pinned source refs
        |
extract labels and historical features
        |
build point-in-time training examples
        |
assign documented splits
        |
validate schema, labels, time, distributions
        |
publish immutable dataset + manifest
        |
train/evaluate model against dataset version
        |
log metrics, model artifact, and lineage
```

### 11.2 Idempotence and failure handling

A job is idempotent when rerunning the same declared inputs does not create conflicting outputs or silently change an already published version.

- Derive the output version from explicit input references/configuration or allocate a new version intentionally.
- Write to a staging path, validate it, then publish atomically where the storage system supports it.
- Refuse to overwrite a published immutable version.
- Make retries safe and record run attempts.
- Keep a manifest even for failed attempts, with failure stage and diagnostics.
- Never publish a dataset if validation fails.
- Do not advance a “latest” pointer until the new artifact passes all gates.
- For backfills, partition the range, pin source state, and reconcile counts/checksums before promotion.

### 11.3 Orchestrator options

| Tool | Typical role | Engineering concern |
|---|---|---|
| Airflow | Schedule and coordinate tasks/DAGs | Retries, task idempotency, data-aware dependencies |
| Dagster | Asset-oriented orchestration and lineage | Asset versioning, materialization metadata, checks |
| Databricks Workflows | Coordinate lakehouse jobs | Runtime pinning, permissions, job parameters |
| Kubeflow Pipelines | Containerized ML/data workflows on Kubernetes | Image reproducibility, artifact passing, cluster operations |
| SageMaker Pipelines | AWS-managed ML workflow orchestration | IAM, service integration, parameter/artifact lineage |

Pick the orchestrator already supported by the platform unless there is a strong reason to add another. The orchestration system records execution state; it does not replace data versioning or validation.

## 12. Reproducing a historical training run

### 12.1 Run manifest checklist

For a past fraud model, record:

1. Training dataset artifact URI and logical version.
2. Dataset canonical fingerprint and file/manifest checksums.
3. Every source table version or Iceberg snapshot ID and retention requirement.
4. Feature definition/code commit and point-in-time policy.
5. Training code commit and clean/dirty Git state.
6. Configuration file and model parameters.
7. Split policy, salt/seed, date cutoffs, and sampling design.
8. Python/runtime and dependency lockfile/container image digest.
9. Hardware/runtime settings relevant to nondeterministic operations.
10. Model artifact URI/version and checksum.
11. Evaluation dataset version, metrics, and metric implementation version.
12. Validation reports and pipeline execution metadata.

### 12.2 Bit-for-bit versus equivalent reproduction

- **Bit-for-bit reproducibility:** output bytes match exactly. This can be realistic for canonicalized deterministic data artifacts, but may be defeated by serialization metadata, nondeterministic file ordering, or environment-dependent output.
- **Logical data reproducibility:** same rows and values under a defined canonicalization, even if Parquet bytes differ.
- **Metric equivalence:** metrics match within a justified tolerance. Distributed reduction order, nondeterministic kernels, hardware, and library implementations can change floating-point results.
- **Scientific/operational reproducibility:** the run can be reconstructed and yields materially equivalent conclusions under documented criteria.

Do not claim exact model bytes for stochastic or nondeterministic training unless the runtime guarantees it and this has been verified. Seed every supported random generator, but recognize that a seed alone cannot make every distributed operation deterministic.

### 12.3 Replay procedure

1. Resolve the recorded immutable dataset artifact and verify its fingerprint.
2. Restore the exact code commit.
3. restore the pinned dependency environment/container.
4. Load the recorded configuration and split policy.
5. Re-run validation and compare the report with the original.
6. Re-run training and evaluation.
7. Compare dataset identity, model artifact checksum where meaningful, and metrics within declared tolerances.
8. Store a replay report linked to the original run; record every difference instead of overwriting history.

If a source snapshot expired, a container image was deleted, or a feature definition was not versioned, mark the reproduction as incomplete and state the missing evidence. Do not silently substitute current data.

## 13. Governance, lineage, and data-centric workflows

### 13.1 Lineage

Maintain the chain:

```text
source system/table/version
    -> extraction query/code commit
    -> feature definition/version
    -> training dataset artifact + fingerprint
    -> validation report
    -> MLflow run + parameters + metrics
    -> model artifact/version
    -> downstream prediction/evaluation
```

Lineage makes it possible to answer which models used a source field and which runs must be re-evaluated after a source correction.

### 13.2 Consent, retention, and deletion

Data governance is an engineering responsibility, but exact legal duties depend on jurisdiction, contract, purpose, and organizational policy. Do not assume a universal retention period or a universal model-deletion rule.

Operational controls should include:
- purpose/consent metadata where applicable;
- access controls and audit logs;
- retention policies for raw, derived, sampled, and cached datasets;
- a lineage query to find derived datasets and model-training runs affected by a deletion request;
- a documented deletion/retraining review process;
- evidence of deletion or an explicitly documented legal/technical exception.

Deleting a user's source row does not automatically remove it from every Parquet snapshot, DVC/lakeFS object, cache, backup, or previously trained model. Define how to invalidate/rebuild affected datasets and evaluate whether retraining, model retirement, or another mitigation is required under the applicable policy. Retention and snapshot expiration must be coordinated with reproducibility obligations and data-deletion requirements.

### 13.3 Dataset slicing and error analysis

A global metric can hide failures for important segments. Slice evaluation by meaningful dimensions such as time period, region, transaction amount band, device type, or label source—subject to privacy and sample-size constraints.

For each slice, record sample size, prevalence, relevant metrics, and confidence/uncertainty. Avoid overinterpreting tiny slices. Use findings to improve labeling, coverage, feature definitions, or sampling—not only to tune the model.

### 13.4 Curated evaluation sets

Maintain a versioned evaluation set with a documented purpose, inclusion criteria, label provenance, time range, and access policy. Protect it from accidental training use and repeated tuning. A stable benchmark supports comparison, while a separate recent/time-based holdout tests whether performance generalizes to current conditions.

## 14. End-to-end hands-on project

Implement this exercise in `experiments/03_training_data/`.

### Exercise 1 — Build a point-in-time training set

- Create synthetic labels and feature history with UTC timestamps.
- Include an event that occurs before prediction time but arrives afterward.
- Include a feature state after prediction time.
- Build the dataset using Section 4's algorithm.
- Assert both future and late-arriving records are excluded.
- Preserve and report examples with no eligible historical features.

**Expected behavior:** every selected feature is no later than prediction time and was available by prediction time. Labels are filtered by a declared maturity cutoff.

### Exercise 2 — Publish and fingerprint a dataset

- Publish a unique version path.
- Write the Parquet artifact and manifest.
- Record row count, schema, canonical fingerprint, and file hash.
- Attempt to publish the same version again; it must fail rather than overwrite.
- Re-run from the same inputs and compare logical fingerprints.

**Expected behavior:** the logical fingerprint remains stable if logical content and canonicalization are unchanged. The Parquet file hash may change if serialization/layout differs; explain why.

### Exercise 3 — Track an MLflow run

- Train a baseline on the pinned dataset.
- Log parameters, metrics, dataset version/fingerprint, Git commit, lockfile/container information, feature list, and model artifact.
- Log the validation report and run manifest.
- Verify that a run can be navigated from model artifact to dataset identity and source references.

**Expected behavior:** metrics and artifacts are linked to the exact declared dataset and code version. Do not claim an MLflow remote service was tested unless one is configured and run.

### Exercise 4 — Reproduce a run

- Pin dataset artifact, code commit, dependency lock, configuration, and seeds.
- Re-run the build and training process.
- Compare row count, schema, logical fingerprint, validation report, and model metrics.
- Record any difference and whether it falls within a predefined tolerance.

**Expected behavior:** compare both the Parquet file SHA-256 and the canonical logical fingerprint. Equal file hashes establish byte-identical Parquet bytes for those artifacts; different file hashes mean the byte-identical objective was not met, even if the logical fingerprints match. In that case, record the difference rather than silently substituting logical equivalence. Model metrics may be equal or within a justified tolerance depending on the model/runtime.

### Exercise 5 — Branch a cleaning rule with DVC or lakeFS

- Track a baseline dataset.
- Create a branch.
- Change a cleaning rule (for example, reject invalid negative transaction amounts).
- Rebuild, validate, and track the new dataset.
- Compare row counts, affected slices, fingerprints, and model metrics.
- Record the exact branch commit/reference.

**Expected behavior:** the new version is distinct, the changed rule is documented, and the base dataset remains available.

### Exercise 6 — Verify group leakage prevention

- Generate multiple transactions per customer.
- Apply hash-based splitting.
- Assert every customer has exactly one split.
- Add a session/group key and verify that it does not cross splits when group independence is required.
- Create a pair of near-duplicate records with different IDs and demonstrate why hashing alone does not detect them.

**Expected behavior:** deterministic group assignment passes; the near-duplicate test requires explicit deduplication/clustering policy.

### Exercise 7 — Fail a validation gate

- Compare current dataset with a prior baseline.
- Inject a schema change, a future feature timestamp, or an unexpected label-prevalence shift.
- Confirm the validation task fails and the publish/train task does not run.
- Restore valid data and confirm the pipeline can succeed.

**Expected behavior:** validation failures block publication; failed runs retain diagnostics and do not mutate the last approved dataset.

### Exercise 8 — Write a reproducibility inventory

For “last quarter's fraud model,” create a table listing each of the six reproducibility elements, the system that stores it, its immutable identifier, retention owner, and verification command. Identify any gap that prevents exact replay.

## 15. Troubleshooting and common mistakes

| Symptom | Likely cause | Corrective action |
|---|---|---|
| Metrics tracked but run cannot be reproduced | Data/code/environment refs missing | Add a run manifest and immutable source/artifact references |
| Old training dataset cannot be read | Snapshot expired or object deleted | Set retention policy from model/run dependencies; verify recoverability |
| Hash changes despite same logical rows | File layout/order/serialization changed | Compare canonical logical fingerprint and file hash separately |
| Dataset hash matches but model metrics differ | Model randomness, environment, evaluation or training config differs | Compare full manifest and use a declared tolerance |
| Future feature values in training | Incorrect temporal join or missing availability timestamp | Add temporal assertions and source availability history |
| Same customer in train and test | Row-level random split | Split by customer/group or use a justified temporal design |
| Class prevalence unexpectedly changes | Label maturity, sampling, source shift, or filtering change | Compare label source/status and slice counts with prior version |
| Retries create conflicting outputs | Mutable destination or non-idempotent writes | Write staging outputs and publish immutable version atomically |
| Validation report exists but bad data trains | Orchestration does not enforce gate dependency | Make training depend on successful validation status |
| User deletion does not affect derived data | Incomplete lineage and inventory | Trace all snapshots, derived datasets, caches, and affected model runs |
| Backfill changes old results | Source state/feature code not pinned | Pin snapshots and version transformations |
| Evaluation improves after undersampling | Evaluation population also sampled | Keep evaluation representative or correct for sampling design |

### Common mistakes to avoid

- Training on “the table as it is today” rather than pinned historical state.
- Recording metrics without data versions.
- Treating a table snapshot, a file hash, and a run manifest as equivalent.
- Using Python's built-in `hash()` for stable split assignment.
- Splitting rows while the same user/session/near-duplicate appears in multiple sets.
- Treating pending/censored labels as negatives.
- Fitting preprocessing on the full dataset before splitting.
- Sampling the evaluation set without accounting for the sampling design.
- Assuming a Git commit preserves data objects without a durable remote/retention policy.
- Claiming exact model reproducibility from a random seed alone.
- Letting a validation warning go unnoticed while training continues.
- Ignoring consent/deletion impact on derived datasets and model lifecycle.

## 16. Practice questions and exercises

1. Why are metrics insufficient to reproduce a training run?
2. Explain the difference between a Delta version, Iceberg snapshot ID, logical dataset version, and content fingerprint.
3. What does a SHA-256 dataset hash prove, and what does it not prove?
4. Why can two Parquet snapshots contain equivalent rows but have different file hashes?
5. Design a point-in-time join for fraud labels and account features.
6. How should a late-arriving event be treated when reconstructing a past prediction?
7. When should you prefer hash-based entity splits, time-based splits, or a combination?
8. How would you prevent sessions and near-duplicates from crossing train/test?
9. Explain label delay, noisy labels, and censored labels with examples.
10. Why should negative sampling normally be isolated from the evaluation-set construction?
11. Design a label-balance gate and explain how it would respond to a real population shift.
12. What should a run manifest contain beyond the Git commit and dataset hash?
13. Describe how DVC and lakeFS support data branching and what each still depends on.
14. How do you recover if a historical table snapshot has expired?
15. Explain bit-for-bit reproducibility versus metric equivalence.
16. What should happen when a validation gate fails after a successful build?
17. How would you trace a deletion request through source data, snapshots, derived datasets, and models?
18. Design a curated evaluation set and explain how you prevent it from becoming a repeatedly tuned training target.
19. List the evidence required to claim last quarter's fraud model has been reproduced.
20. Which parts of your local project are unit-tested, and which external integrations remain unverified?

## 17. Completion checklist

- [ ] Build a point-in-time-correct training set from labels and historical features.
- [ ] Record source references, feature definitions, and dataset identity.
- [ ] Explain the six reproducibility elements and link them through a run manifest.
- [ ] Compare Delta `VERSION AS OF`, Iceberg snapshots, Parquet snapshots, DVC, lakeFS, and MLflow metadata.
- [ ] Log dataset references/hashes, Git commit, parameters, metrics, environment, and model artifacts in MLflow.
- [ ] Re-run with pinned inputs and compare data identity and model metrics.
- [ ] Implement deterministic hash-based splits and test group isolation.
- [ ] Explain when time-based splits are required.
- [ ] Handle delayed, noisy, censored, and leaky labels; explain negative sampling and class imbalance.
- [ ] Validate schema, temporal invariants, distributions, label balance, and changes from the prior version.
- [ ] Make validation a pipeline gate before publication/training.
- [ ] Explain idempotence, retries, backfills, and snapshot retention.
- [ ] Reproduce a past run as far as available data/environment guarantees permit.
- [ ] Trace lineage from source through dataset and model.
- [ ] Document consent, retention, deletion, dataset slicing, and curated evaluation sets.
- [ ] Distinguish verified local tests from optional integrations that need external services.

## 18. Authoritative documentation

Use the documentation for the exact versions deployed. The following are starting points, not a claim that one syntax/API works across every engine or release.

- Delta Lake documentation: https://docs.delta.io/
- Databricks Delta Lake time travel: https://docs.databricks.com/en/delta/history.html
- Apache Iceberg documentation: https://iceberg.apache.org/docs/latest/
- DVC documentation: https://dvc.org/doc
- lakeFS documentation: https://docs.lakefs.io/
- MLflow tracking: https://mlflow.org/docs/latest/ml/tracking/
- MLflow dataset tracking: https://mlflow.org/docs/latest/ml/dataset/
- MLflow dataset Python API (`from_pandas`, `log_input`): https://mlflow.org/docs/latest/api_reference/python_api/mlflow.data.html
- MLflow scikit-learn model logging API: https://mlflow.org/docs/latest/api_reference/python_api/mlflow.sklearn.html
- pandas documentation: https://pandas.pydata.org/docs/
- scikit-learn model selection and evaluation: https://scikit-learn.org/stable/model_selection.html
- Great Expectations documentation: https://docs.greatexpectations.io/
- Evidently documentation: https://docs.evidentlyai.com/
- TensorFlow Data Validation: https://www.tensorflow.org/tfx/data_validation/get_started
- Apache Airflow: https://airflow.apache.org/docs/
- Dagster: https://docs.dagster.io/
- Kubeflow Pipelines: https://www.kubeflow.org/docs/components/pipelines/
- Amazon SageMaker Pipelines: https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines.html

---

## Engineering principle to retain

A reproducible training run is a linked, durable record of **which data**, **which feature definitions**, **which code**, **which configuration**, **which environment**, and **which model artifact** were used. Point-in-time correctness and validation establish whether the data is fit for the prediction task; versioning and lineage establish whether that exact dataset can be identified later. Neither is optional in a trustworthy ML data pipeline.
