# Model Registry and Batch vs Online Inference

> **Stage 2C — Data Engineering_3 · Module 10: Big Data ML and MLOps Handoff · Topic 04**
>
> Target path: `Stage 2C — Data Engineering_3/10-Big-Data-ML-and-MLOps-Handoff/04-model-registry-and-batch-vs-online-inference.md`
>
> **Scope:** production data engineering around trained models: packaging, versioning, promotion, inference data flows, prediction logging, rollback, observability, and governance. The model itself is deliberately a simple churn classifier; the engineering around it is the focus.

---

## 1. Learning outcomes

By completing this lesson, you should be able to:

1. Explain the lifecycle **training → evaluation → registration → staging → deployment → monitoring → retirement** and identify the artifacts and controls at each step.
2. Distinguish a model artifact, a registered model, a model version, a deployment, and a mutable alias such as `champion`.
3. Describe MLflow Model Registry and Unity Catalog models, and recognize the corresponding registry concepts in Amazon SageMaker, Vertex AI, and Azure Machine Learning.
4. Package a model through MLflow's `pyfunc` interface with an explicit input/output signature, example input, and pinned dependencies.
5. Build an idempotent batch scoring job that processes a bounded input window, records the exact model version used, and supports safe retry/recovery.
6. Build a request/response API that validates inputs, fetches online features, enforces a latency budget, and records safe prediction telemetry.
7. Choose batch, online, streaming, or precompute-and-serve inference from business freshness and latency requirements rather than fashion.
8. Explain shadow, canary, blue/green, A/B, and champion/challenger patterns; design promotion gates and rollback.
9. Measure inference latency, errors, freshness, throughput, and cost without fabricating performance results.
10. Apply model governance: lineage, approvals, access controls, model cards, privacy-aware logs, retirement, and audit trails.

### How this lesson fits the module

Topic 01 introduces distributed training with Spark MLlib. Topic 02 develops features and feature stores. Topic 03 makes training data reproducible and versioned. This topic connects those assets to model registration and production inference. Topic 05 then uses prediction logs and delayed outcomes for drift and performance monitoring.

The central engineering question is not only, “Can the model predict?” It is: **Can we identify exactly which model predicted, what information it saw, how it was promoted, whether the result met the service contract, and how to recover safely if it does not?**

---

## 2. Prerequisites and environment setup

### 2.1 Prerequisites

You should be comfortable with:

- Python, virtual environments, packaging, and automated tests.
- pandas and scikit-learn basics.
- SQL tables, incremental processing, primary keys, and idempotent jobs.
- HTTP request/response concepts and FastAPI fundamentals.
- MLflow experiment tracking and model logging from the earlier MLflow module.
- Feature timestamps and point-in-time correctness from Topic 02.
- Dataset versions, code commits, and reproducibility from Topic 03.

You do **not** need to derive optimization algorithms. We use logistic regression to keep the focus on the lifecycle and serving system.

### 2.2 Local lab versus production

The hands-on project is designed for local development. It uses:

- a local MLflow tracking server with a database-backed registry;
- a small, deterministic synthetic churn dataset;
- scikit-learn and MLflow `pyfunc` packaging;
- SQLite for an illustrative batch prediction table and local feature store;
- FastAPI for online inference;
- a local file-based prediction log.

This is a learning setup, **not** a production reference architecture. SQLite and a local filesystem are not substitutes for a highly available production database, object store, Redis cluster, secrets manager, or managed inference platform. The code intentionally keeps the feature-store interface replaceable.

### 2.3 Suggested project tree

Create the following directory:

```text
experiments/
└── 04_registry_inference/
    ├── README.md
    ├── requirements.txt
    ├── .env.example
    ├── src/
    │   ├── __init__.py
    │   ├── common.py
    │   ├── train_register.py
    │   ├── promote.py
    │   ├── batch_score.py
    │   ├── feature_store.py
    │   ├── api.py
    │   └── shadow_compare.py
    ├── tests/
    │   ├── test_contracts.py
    │   └── test_batch_idempotency.py
    └── data/
        └── .gitkeep
```

The lesson includes the core files below. In your own repository, keep each code block in the matching file.

### 2.4 Environment

Use a supported Python version shared by your pinned dependencies (Python 3.11 is a reasonable baseline for this example). Create a virtual environment:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
```

`requirements.txt`:

```text
mlflow==3.5.0
scikit-learn==1.7.2
pandas==2.3.3
numpy==2.3.4
fastapi==0.119.0
uvicorn[standard]==0.38.0
pydantic==2.12.3
httpx==0.28.1
pytest==8.4.2
```

These are reproducibility pins for the teaching example, not a promise that these are the newest versions or the right versions for every operating system. Before adopting them, check package availability for your Python and platform, then resolve and commit a lock file. Production builds should use a tested lock file, vulnerability scanning, and a controlled artifact build process.

Install:

```bash
python -m pip install -r requirements.txt
```

For repeatable shell commands, run commands from the `experiments/04_registry_inference/` directory and set the import path if needed:

```bash
# macOS/Linux
export PYTHONPATH=.
# Windows PowerShell
# $env:PYTHONPATH = "."
```

### 2.5 Start a local MLflow tracking server

Use a persistent local SQLite backend and a separate artifact directory. The registry is backed by the tracking database in this lab; in production, choose a supported backend and durable artifact store appropriate to your MLflow deployment.

```bash
mkdir -p data/mlflow-artifacts
mlflow server \
  --backend-store-uri sqlite:///data/mlflow.db \
  --default-artifact-root ./data/mlflow-artifacts \
  --host 127.0.0.1 \
  --port 5000
```

Keep this process running in one terminal. In a second terminal:

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
export MLFLOW_REGISTRY_URI=http://127.0.0.1:5000
```

On PowerShell, use `$env:MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"` and the equivalent registry URI.

> **Registry backend note:** MLflow's registry capabilities depend on the tracking/registry backend and deployment mode. Workspace-managed registries such as Unity Catalog have different naming, permissions, and lifecycle semantics from a local MLflow registry. This lesson uses a local registry for a runnable teaching path and identifies where those assumptions matter.

---

## 3. Model lifecycle fundamentals

### 3.1 The lifecycle at a glance

```text
Training
   ↓ candidate artifact + run metadata
Evaluation
   ↓ metrics, slices, validation evidence
Registration
   ↓ immutable model version + lineage
Staging / Challenger
   ↓ compatibility, safety, and approval gates
Deployment / Champion
   ↓ serving or scoring system loads a version
Monitoring
   ↓ operational signals + eventual outcome labels
Retirement
   ↓ traffic stopped, references archived, access and retention reviewed
```

A lifecycle is a set of controlled transitions, not necessarily a vendor-specific sequence of status fields. Some platforms implement stages directly; others use tags, aliases, deployment records, or separate endpoint resources.

| Step | Purpose | Typical artifacts and evidence | Gate or control |
|---|---|---|---|
| Training | Fit a candidate model | Dataset version, feature definitions, code commit, environment lock, parameters, run ID | Reproducible inputs and successful run |
| Evaluation | Estimate quality and risk | Metrics, baseline comparison, slice metrics, calibration, fairness assessment | Predefined thresholds and review |
| Registration | Give the artifact a durable identity | Registered model name, immutable version, model files, signature, dependencies | Artifact loads and schema is compatible |
| Staging | Test the candidate in a controlled environment | Staging deployment, smoke tests, test predictions, approval record | Security, contract, quality, and operational checks |
| Deployment | Direct some or all traffic or jobs to the candidate | Endpoint revision, batch job configuration, alias assignment, rollout record | Rollout plan and rollback path |
| Monitoring | Detect failures and degradation | Request/prediction logs, latency, error rate, freshness, outcome labels | SLO alerts, ownership, incident runbook |
| Retirement | Stop use safely | End-of-life record, remaining consumers, retained metadata/artifacts | No active consumer; retention and audit requirements satisfied |

### 3.2 Core terms

- **Model artifact:** serialized model plus metadata, environment requirements, and possibly code or auxiliary artifacts.
- **Run:** a record of one experiment or training execution. It can contain parameters, metrics, tags, and artifacts.
- **Registered model:** a named registry entry grouping model versions, such as `churn`.
- **Model version:** an immutable numbered artifact reference within that registered model. A new registration normally creates a new version rather than overwriting an existing one.
- **Alias:** a mutable human-readable pointer to a model version, such as `champion` or `challenger`. It can be reassigned.
- **Deployment:** a runtime instance or endpoint revision that serves predictions. Registry alias movement does not guarantee that an already-running process reloads its model.
- **Prediction record:** a record of one scoring result, ideally including request or entity identity, exact model version, timestamps, and safe lineage.

### 3.3 Why aliases do not equal deployments

Suppose `models:/churn@champion` points to version `7` at 10:00. A batch job resolves that alias and loads version `7`. At 10:05 an operator points `champion` to version `8`. The batch job that already loaded version `7` may continue using version `7` until it exits or reloads.

Therefore:

1. Resolve the alias once at the start of a batch run.
2. Capture the resolved immutable version number.
3. Load that exact version for the run.
4. Write that version into every output row and the run manifest.
5. For online serving, record the loaded version at process startup and expose it in health/diagnostic metadata.
6. Treat a rollout as complete only after the serving system confirms which artifact is loaded and health checks pass.

A registry alias is a **control-plane pointer**. It is not a magic instruction that atomically replaces all processes or already-running jobs.

### 3.4 Reproducibility is a bundle

To reproduce a historical prediction or training run, preserve more than the model file:

- registered model name and immutable version;
- model artifact URI and checksum where supported;
- training run ID, code commit, dependency lock, and container image digest;
- dataset snapshot/version and feature definition/version;
- schema/signature and preprocessing logic;
- relevant inference parameters and random seeds;
- serving configuration and the model version actually loaded;
- request/prediction ID and privacy-approved input references;
- the outcome label when it becomes available.

Exact bit-for-bit reproduction can be limited by nondeterministic kernels, hardware, library versions, and distributed execution. Define whether your requirement is **artifact identity**, **same inputs and equivalent predictions**, or **bitwise identical output**.

---

## 4. Model registries and version management

### 4.1 What a registry provides

A model registry is the controlled catalog and lifecycle interface for model artifacts. It helps answer:

- Which candidate is approved for production?
- Which training run and dataset produced this version?
- What schema does the model accept?
- Which version is deployed or being evaluated?
- Who approved a promotion, when, and based on what evidence?
- Which consumers still use a model that is scheduled for retirement?

A registry does not automatically make a model good, secure, fair, or operationally healthy. Those outcomes require automated checks, human approval where required, and runtime controls.

### 4.2 Version, alias, tag, stage, endpoint: keep them distinct

| Concept | Meaning | Example |
|---|---|---|
| Version | Immutable identity of one registered artifact | `churn` version `8` |
| Alias | Mutable name pointing at a version | `champion → version 8` |
| Tag/metadata | Searchable descriptive key/value data | `evaluation_status=passed` |
| Logical stage | Lifecycle concept used by an organization | candidate, staging, production, retired |
| Endpoint revision | Runtime deployment revision | API deployment `rev-2026-10-19-03` |
| Approval record | Auditable decision by a gate or person | approval ticket and evidence URI |

Older MLflow workflows used model stages such as `Staging` and `Production`. In modern MLflow workflows, aliases and tags are the more flexible pattern; stage support differs by registry setup and version. Do not assume every MLflow installation supports identical lifecycle operations. In particular, **do not write a new tutorial around `transition_model_version_stage()` without checking the deployed MLflow version and registry backend**. This lesson uses aliases in the runnable project.

### 4.3 Champion/challenger

- **Champion:** current approved model that owns production decisions.
- **Challenger:** candidate being evaluated against the champion, often offline or in shadow mode.
- **Promotion gate:** a deterministic set of criteria that must pass before the challenger may become champion.

A challenger should not become champion just because its aggregate metric is slightly better. A gate should include minimum data/metric sample sizes, comparison to the current baseline, important segment checks, calibration or business constraints, fairness assessment where appropriate, input/output compatibility, operational tests, and an approval record.

An illustrative gate might require:

```text
candidate_auc >= baseline_auc - 0.002
candidate_recall_at_fixed_precision >= baseline_recall
no critical segment regression > 0.03
schema and load tests pass
fairness review status = approved
owner approval recorded
```

The thresholds above are examples only. A real threshold must be selected from business impact, statistical uncertainty, and model-risk requirements. Do not copy these values blindly.

### 4.4 MLflow Model Registry

MLflow organizes registered models, versions, aliases, tags, and lineage to runs. Typical URI forms include:

```text
runs:/<run_id>/model                 # artifact logged in a run
models:/churn/8                      # immutable registered version
models:/churn@champion               # mutable alias resolved at load time
```

The alias URI form is `models:/<model-name>@<alias>`. The slash-before-alias form `models:/churn@champion` is correct; `models:/churn/champion` is not the alias form.

The registry client can set aliases on a registered model version. Use the `MlflowClient` API and validate the selected version before assigning an alias. The runnable example below creates a registered model if necessary, registers a candidate version, then changes aliases only after a promotion gate.

### 4.5 Unity Catalog models and cloud registries

The **logical concepts**—versions, lineage, permissions, approvals, deployment references, and audit history—are portable. API names, URI syntax, lifecycle transitions, and permission models are not.

| Platform | Awareness-level view | Important implementation distinction |
|---|---|---|
| MLflow Model Registry | Registry linked to MLflow runs and artifacts; versions, tags, aliases depending on backend | Local/OSS setup and managed registry setups may differ; legacy stages are not universal |
| Unity Catalog models | Governed model objects with centralized permissions and lineage in Databricks/Unity Catalog environments | Use fully qualified names such as `catalog.schema.model`; configure the appropriate registry URI and privileges; do not assume local registry naming works unchanged |
| Amazon SageMaker Model Registry | Model packages and package groups, approval status, deployment workflows | Package approval and endpoint deployment are distinct resources and actions |
| Vertex AI Model Registry | Model resources and versions, evaluation/deployment integrations | Registry resource management and endpoint traffic configuration are separate concerns |
| Azure Machine Learning registry | Model assets and versions with workspace/registry governance | Permissions, asset references, and deployment resources are Azure-specific |

Do not attempt to hide platform differences behind a false universal API. Build a small internal lifecycle interface if your organization needs portability, and keep platform-specific behavior behind that interface.

### 4.6 Metadata and lineage contract

At registration, attach or retain metadata such as:

```text
model_family: churn
task: binary_classification
training_run_id: <MLflow run ID>
dataset_version: <immutable snapshot/hash>
feature_definition_version: <commit or version>
code_commit: <git SHA>
environment_lock_hash: <hash>
evaluation_report_uri: <durable report reference>
owner: <team>
approval_ticket: <ticket ID>
data_classification: <classification>
retirement_review_date: <date>
```

Avoid putting credentials, raw personal data, or sensitive values in tags. Metadata should be searchable but not become an uncontrolled second copy of confidential data.

### 4.7 Access control and audit

Separate permissions for:

- registering new versions;
- changing aliases or approval states;
- reading model artifacts;
- deploying to production;
- reading prediction logs;
- deleting or retiring models.

The ability to create a candidate should not automatically grant the ability to promote it. Log actor identity, timestamp, previous and new references, reason, approval evidence, and rollout outcome. In managed systems, use platform identity and authorization rather than embedding long-lived tokens in notebooks or source code.

### 4.8 Retirement

Retirement is not simply deleting a registry entry. First identify active batch jobs, endpoints, scheduled workflows, downstream consumers, rollback requirements, and audit/retention obligations. Stop new traffic, verify that no consumer references the version, preserve required evidence, then disable or archive it according to policy. Retain enough lineage to explain historical predictions even when the artifact itself is eventually deleted under retention rules.

---

## 5. Packaging, signatures, and environments

### 5.1 Why packaging matters

A model that works in a notebook may fail in production because its preprocessing code, dependency versions, input types, or feature order differ. Packaging makes the model consumable through a documented interface and gives deployment automation something to validate.

### 5.2 MLflow `pyfunc`

MLflow's Python function (`pyfunc`) flavor provides a general prediction interface. A loaded `PyFuncModel` exposes `predict(...)` for supported input types. Native flavors (for example, scikit-learn) may also be logged; the pyfunc interface helps consumers use a consistent loading pattern.

### 5.3 Signatures and input examples

A **model signature** describes expected input and output schema. It is a contract, not a substitute for business validation. A signature can catch missing columns or incompatible types, while the application must still check semantic rules such as allowed ranges, freshness, and entity authorization.

For this lesson, the model consumes these four numeric features:

| Feature | Type | Meaning | Example constraint |
|---|---|---|---|
| `tenure_months` | numeric | Months as a customer | nonnegative |
| `monthly_charges` | numeric | Current monthly charges | nonnegative and within domain limit |
| `support_tickets_90d` | numeric | Support tickets in last 90 days | nonnegative count |
| `usage_ratio_30d` | numeric | Recent usage divided by expected usage | finite; domain-specific range |

The model output is a churn probability in the interval `[0, 1]`. The API applies a documented decision threshold separately. Keeping a probability and a decision separate makes threshold changes auditable without silently changing the model artifact.

### 5.4 Environment and container reproducibility

Capture:

- Python and dependency versions;
- model artifact and code;
- operating-system and native library dependencies where relevant;
- container image digest, not only a mutable tag;
- CPU/GPU and runtime settings where they can affect behavior;
- configuration values that affect prediction semantics.

A container improves consistency but does not guarantee reproducibility by itself. Pin dependencies, scan images, run as a non-root user, avoid secrets in image layers, and validate the built image with the same contract tests used in staging.

### 5.5 Compatibility checks before promotion

Before a model can be promoted, run at least:

1. Artifact can be downloaded and loaded.
2. Signature and input example are present and match the expected contract.
3. Golden test inputs produce acceptable outputs.
4. Output is finite and within expected bounds.
5. Batch and online paths agree within a defined tolerance for the same feature vector.
6. Dependency and security scans pass.
7. Baseline, slice, and fairness checks pass according to the task's risk level.
8. Resource and latency tests meet the intended service tier.
9. Rollback target is still available and known.
10. Approval metadata is recorded.

---

## 6. Batch inference architecture and implementation

### 6.1 What batch inference is

Batch inference scores a bounded set of records on a schedule or in response to a data availability event. Inputs may come from a lakehouse table, warehouse query, Parquet files, or a Spark DataFrame. Outputs are written to a durable prediction table or partition.

Use batch when the business can tolerate a defined delay, such as nightly churn risk scores used for daily email campaigns. Batch is often cheaper and simpler than maintaining a low-latency endpoint for a workload that does not need one.

### 6.2 Batch architecture

```text
Scheduler / orchestrator
       ↓
Resolve champion alias once
       ↓
Record immutable model version + input window
       ↓
Read eligible records / incremental watermark
       ↓
Validate schema, keys, and feature freshness
       ↓
Score with pinned model version
       ↓
Write predictions idempotently
       ↓
Record manifest, counts, checksums, metrics
       ↓
Publish successful watermark / notify consumers
```

### 6.3 Batch design requirements

- **Bounded input:** specify a date window, snapshot, or source watermark.
- **Deterministic model reference:** resolve alias once and pin the version for the run.
- **Idempotent output:** a retry must not create a second authoritative prediction for the same logical scoring key.
- **Explicit scoring key:** often `(entity_id, scoring_date, model_version)` or a business-defined prediction key.
- **Transactional publication:** write to a staging partition/table, validate, then atomically publish where the storage system supports it.
- **Recovery:** record run status and input bounds; retry failed partitions safely.
- **Traceability:** write exact model version, scoring timestamp, source snapshot or watermark, and pipeline run ID.
- **Incremental logic:** only score new or intentionally re-scored records, with explicit backfill semantics.
- **Quality checks:** row counts, duplicate keys, null/invalid predictions, feature freshness, and expected coverage.
- **Monitoring:** duration, throughput, input/output counts, failure rate, and lag behind source data.

### 6.4 Shared utilities: `src/common.py`

```python
"""Shared constants and helpers for the local registry/inference lab."""
from __future__ import annotations

import os
from typing import Any

import mlflow
from mlflow import MlflowClient

MODEL_NAME = os.getenv("MODEL_NAME", "churn")
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
REGISTRY_URI = os.getenv("MLFLOW_REGISTRY_URI", TRACKING_URI)
FEATURE_COLUMNS = [
    "tenure_months",
    "monthly_charges",
    "support_tickets_90d",
    "usage_ratio_30d",
]

def configure_mlflow() -> MlflowClient:
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_registry_uri(REGISTRY_URI)
    return MlflowClient(tracking_uri=TRACKING_URI, registry_uri=REGISTRY_URI)

def resolve_alias_version(client: MlflowClient, model_name: str, alias: str) -> str:
    """Resolve an alias once and return the immutable version number as a string."""
    mv = client.get_model_version_by_alias(model_name, alias)
    return str(mv.version)

def model_uri_for_version(model_name: str, version: str) -> str:
    return f"models:/{model_name}/{version}"

def require_finite_probability(value: Any) -> float:
    """Convert one scalar probability and reject invalid outputs."""
    import math

    result = float(value)
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise ValueError(f"Model returned invalid probability: {result!r}")
    return result
```

This helper intentionally resolves the alias through the client and then constructs an immutable version URI. It does not assume that a long-running process automatically follows alias changes.

### 6.5 Train, evaluate, and register: `src/train_register.py`

This script creates a small deterministic synthetic dataset, fits a baseline logistic regression, logs the run and model with a signature, and registers the model under `churn`. Synthetic data is useful for a runnable lab; it is not evidence of real-world predictive quality.

```python
from __future__ import annotations

import hashlib
import json
import os

import mlflow
import numpy as np
import pandas as pd
from mlflow.models import infer_signature
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.common import FEATURE_COLUMNS, MODEL_NAME, configure_mlflow

RANDOM_STATE = 41
ARTIFACT_NAME = "model"

class ChurnProbabilityModel(mlflow.pyfunc.PythonModel):
    """Expose positive-class probability, not sklearn Pipeline.predict labels."""
    def __init__(self, fitted_pipeline):
        self.fitted_pipeline = fitted_pipeline

    def predict(self, context, model_input, params=None):
        return self.fitted_pipeline.predict_proba(model_input[FEATURE_COLUMNS])[:, 1]

def make_dataset(n: int = 3000) -> tuple[pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(RANDOM_STATE)
    x = pd.DataFrame({
        "tenure_months": rng.integers(1, 73, size=n).astype(float),
        "monthly_charges": rng.normal(72, 22, size=n).clip(15, 180),
        "support_tickets_90d": rng.poisson(1.4, size=n).astype(float),
        "usage_ratio_30d": rng.normal(0.78, 0.22, size=n).clip(0, 1.8),
    })
    logit = (
        0.9 - 0.035 * x["tenure_months"]
        + 0.012 * x["monthly_charges"]
        + 0.34 * x["support_tickets_90d"]
        - 0.85 * x["usage_ratio_30d"]
    )
    probability = 1 / (1 + np.exp(-logit))
    y = pd.Series(rng.binomial(1, probability), name="churned")
    return x, y

def dataset_fingerprint(x: pd.DataFrame, y: pd.Series) -> str:
    """Logical fingerprint of canonical columns/rows for this deterministic pandas fixture.

    This is not a checksum of a serialized dataset file and does not prove
    byte-identical Parquet reproduction across writers or library versions.
    """
    frame = x.loc[:, FEATURE_COLUMNS].copy()
    frame["churned"] = y.to_numpy()
    schema = json.dumps({"columns": [(c, str(frame[c].dtype)) for c in frame.columns], "pandas_version": pd.__version__}, separators=(",", ":"))
    row_hashes = pd.util.hash_pandas_object(frame, index=False, categorize=True).to_numpy().tobytes()
    return hashlib.sha256(schema.encode("utf-8") + b"\0" + row_hashes).hexdigest()

def main() -> None:
    client = configure_mlflow()
    mlflow.set_experiment("04-registry-inference")
    x, y = make_dataset()
    dataset_hash = dataset_fingerprint(x, y)

    # Keep a final holdout isolated from candidate selection and promotion.
    x_dev, _x_final_test, y_dev, _y_final_test = train_test_split(
        x, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    x_train, x_validation, y_train, y_validation = train_test_split(
        x_dev, y_dev, test_size=0.25, random_state=RANDOM_STATE + 1, stratify=y_dev
    )
    pipeline = Pipeline([
        ("scale", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
    ])
    with mlflow.start_run() as run:
        pipeline.fit(x_train[FEATURE_COLUMNS], y_train)
        probability = pipeline.predict_proba(x_validation[FEATURE_COLUMNS])[:, 1]
        predicted = (probability >= 0.5).astype(int)
        validation_auc = float(roc_auc_score(y_validation, probability))
        validation_precision = float(precision_score(y_validation, predicted, zero_division=0))
        validation_recall = float(recall_score(y_validation, predicted, zero_division=0))
        mlflow.log_params({
            "algorithm": "logistic_regression",
            "random_state": RANDOM_STATE,
            "threshold": 0.5,
            "dataset_rows": len(x),
            "train_rows": len(x_train),
            "validation_rows": len(x_validation),
            "final_test_rows_reserved": len(_x_final_test),
        })
        mlflow.log_metrics({
            "validation_auc": validation_auc,
            "validation_precision": validation_precision,
            "validation_recall": validation_recall,
        })
        code_commit = os.getenv("GIT_COMMIT", "local-unversioned")
        mlflow.set_tags({
            "task": "binary_classification",
            "dataset_version": f"synthetic-v1-seed-{RANDOM_STATE}",
            "dataset_fingerprint": dataset_hash,
            "code_commit": code_commit,
            "owner": "ml-platform-learning-lab",
            "evaluation_split": "validation",
            "final_test_used_for_promotion": "false",
        })

        input_example = x_train[FEATURE_COLUMNS].head(5)
        output_example = pipeline.predict_proba(input_example)[:, 1]
        signature = infer_signature(input_example, output_example)
        model_info = mlflow.pyfunc.log_model(
            python_model=ChurnProbabilityModel(pipeline),
            name=ARTIFACT_NAME,
            signature=signature,
            input_example=input_example,
            code_paths=["src"],
            pip_requirements=[
                "mlflow==3.5.0", "scikit-learn==1.7.2",
                "pandas==2.3.3", "numpy==2.3.4",
            ],
        )
        registered = mlflow.register_model(model_info.model_uri, MODEL_NAME)
        for key, value in {
            "evaluation_status": "candidate",
            "training_run_id": run.info.run_id,
            "validation_auc": f"{validation_auc:.8f}",
            "dataset_version": f"synthetic-v1-seed-{RANDOM_STATE}",
            "dataset_fingerprint": dataset_hash,
            "code_commit": code_commit,
        }.items():
            client.set_model_version_tag(MODEL_NAME, registered.version, key, value)
        print(json.dumps({
            "registered_model": MODEL_NAME,
            "version": registered.version,
            "run_id": run.info.run_id,
            "model_uri": model_info.model_uri,
            "validation_auc": validation_auc,
            "validation_precision": validation_precision,
            "validation_recall": validation_recall,
            "dataset_fingerprint": dataset_hash,
            "code_commit": code_commit,
            "final_test_evaluated": False,
        }, indent=2))

if __name__ == "__main__":
    main()
```

**Implementation notes**

- `infer_signature()` sees the same input columns the model consumes and the model's probability output.
- The model artifact includes the scikit-learn pipeline, so scaling is not accidentally reimplemented differently by the API.
- `dataset_fingerprint` is a logical fingerprint for this deterministic pandas fixture (canonical column order, dtype/schema description, and row hashes). It is not a file checksum and does not establish byte-identical Parquet serialization.
- The final holdout is reserved and never evaluated by this candidate-registration script. Select/promote with validation data; evaluate the locked final test set once after model selection in a separate controlled workflow.
- CI should set `GIT_COMMIT` to the actual immutable commit SHA. The local demo defaults to `local-unversioned`; promotion requires an explicit `--allow-unversioned-local` opt-in for that teaching-only state.
- A registered version may take time to become ready in some backends. Check readiness and artifact loadability before promotion. Synthetic metrics are not evidence of real-world quality.

### 6.6 Promotion gate and alias movement: `src/promote.py`

This script demonstrates a deliberately limited gate using **validation AUC**, never the final holdout. It validates metric range, loads and smoke-tests the candidate artifact, compares against the current champion only when both versions share the same validation-dataset fingerprint, requires dataset fingerprint and code-commit metadata, and requires an approval ID before moving `champion`. The sample still reads registry tags, which are mutable metadata and not a cryptographically trusted evaluation record; production CI/CD should consume signed/immutable evaluation artifacts and enforce slice, fairness, compatibility, security, operational, and human-approval gates.

```python
from __future__ import annotations

import argparse
import math

import mlflow.pyfunc
import pandas as pd
from mlflow.exceptions import MlflowException
from src.common import (FEATURE_COLUMNS, MODEL_NAME, configure_mlflow,
                        model_uri_for_version, require_finite_probability)

def parse_validation_auc(client, model_name: str, version: str) -> float:
    mv = client.get_model_version(model_name, version)
    raw = (mv.tags or {}).get("validation_auc")
    if raw is None:
        raise ValueError(f"Version {version} has no validation_auc metadata")
    value = float(raw)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"Version {version} has invalid validation_auc={raw!r}")
    return value

def gate_passes(candidate_auc: float, champion_auc: float | None,
                min_auc: float, max_regression: float) -> bool:
    if not math.isfinite(candidate_auc) or not 0.0 <= candidate_auc <= 1.0:
        return False
    if champion_auc is not None and not math.isfinite(champion_auc):
        return False
    return candidate_auc >= min_auc and (
        champion_auc is None or candidate_auc >= champion_auc - max_regression
    )

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True, help="Registered candidate version")
    parser.add_argument("--min-auc", type=float, default=0.70)
    parser.add_argument("--max-regression", type=float, default=0.002)
    parser.add_argument("--promote-to-champion", action="store_true")
    parser.add_argument("--approval-id", help="Required review/approval record when moving champion")
    parser.add_argument("--allow-unversioned-local", action="store_true",
                        help="Teaching-lab only; allow code_commit=local-unversioned")
    args = parser.parse_args()
    if args.min_auc < 0 or args.min_auc > 1 or args.max_regression < 0:
        raise ValueError("--min-auc must be [0,1] and --max-regression must be non-negative")
    if args.promote_to_champion and not args.approval_id:
        raise SystemExit("Champion promotion requires --approval-id; record an actual approval in production.")

    client = configure_mlflow()
    candidate = client.get_model_version(MODEL_NAME, args.version)
    if candidate.status != "READY":
        raise RuntimeError(f"Candidate is not READY: {candidate.status}")
    tags = candidate.tags or {}
    commit = tags.get("code_commit", "")
    if not commit or (commit == "local-unversioned" and not args.allow_unversioned_local):
        raise SystemExit("Missing immutable code commit; set GIT_COMMIT or explicitly opt in for the local lab.")
    if not tags.get("dataset_fingerprint"):
        raise SystemExit("Missing dataset_fingerprint; candidate is not traceable enough to promote.")
    candidate_auc = parse_validation_auc(client, MODEL_NAME, args.version)
    candidate_fingerprint = tags["dataset_fingerprint"]

    # Load and smoke-test the immutable artifact before changing any alias.
    candidate_model = mlflow.pyfunc.load_model(model_uri_for_version(MODEL_NAME, str(args.version)))
    probe = pd.DataFrame([{
        "tenure_months": 18.0, "monthly_charges": 89.0,
        "support_tickets_90d": 2.0, "usage_ratio_30d": 0.72,
    }], columns=FEATURE_COLUMNS)
    probe_probability = require_finite_probability(candidate_model.predict(probe)[0])

    try:
        champion = client.get_model_version_by_alias(MODEL_NAME, "champion")
        champion_auc = parse_validation_auc(client, MODEL_NAME, str(champion.version))
        champion_tags = champion.tags or {}
        if champion_tags.get("dataset_fingerprint") != candidate_fingerprint:
            raise SystemExit("Cannot compare candidate and champion AUC: validation dataset fingerprints differ. Re-evaluate both on the same frozen validation set.")
    except MlflowException as exc:
        # First promotion only: do not mask authentication, network, or server failures.
        if getattr(exc, "error_code", None) != "RESOURCE_DOES_NOT_EXIST":
            raise
        champion, champion_auc = None, None

    # challenger is a mutable pointer; candidate version remains immutable.
    client.set_registered_model_alias(MODEL_NAME, "challenger", str(args.version))
    passed = gate_passes(candidate_auc, champion_auc, args.min_auc, args.max_regression)
    client.set_model_version_tag(MODEL_NAME, args.version, "artifact_smoke_test", "passed")
    print({"candidate_version": str(candidate.version), "candidate_validation_auc": candidate_auc,
           "champion_validation_auc": champion_auc, "validation_dataset_fingerprint": candidate_fingerprint,
           "artifact_smoke_probability": probe_probability, "gate_passes": passed})
    if not passed:
        raise SystemExit("Promotion gate failed; champion remains unchanged.")

    client.set_model_version_tag(MODEL_NAME, args.version, "evaluation_status", "passed")
    if args.promote_to_champion:
        client.set_model_version_tag(MODEL_NAME, args.version, "approval_id", args.approval_id)
        client.set_registered_model_alias(MODEL_NAME, "champion", str(args.version))
        client.set_model_version_tag(MODEL_NAME, args.version, "promotion_status", "champion")
        print(f"Champion alias now points to immutable version {args.version}; approval_id={args.approval_id}")

if __name__ == "__main__":
    main()
```

Run the training script and capture the printed version:

```bash
python -m src.train_register
# Copy the reported version number, then:
python -m src.promote --version 1 --min-auc 0.70 --allow-unversioned-local
```

Use the actual version printed by the script; never assume it is `1` after prior registrations. `LOCAL-REVIEW-001` is an exercise placeholder only, not evidence of a real approval. For an unversioned local checkout, the explicit `--allow-unversioned-local` flag is a teaching-only escape hatch; production pipelines should reject it.

```bash
python -m src.promote --version <VERSION> --min-auc 0.70 --allow-unversioned-local --promote-to-champion --approval-id LOCAL-REVIEW-001
```

If the registry API or server rejects aliases, verify the installed MLflow version, registry backend, registry URI, and permissions rather than silently switching to legacy stages. Do not catch broad exceptions in production and treat all failures as “no champion”; distinguish “alias not found” from network, authentication, and server errors.

### 6.7 Idempotent batch scoring: `src/batch_score.py`

This local job demonstrates an important invariant: resolve the alias once, then use the immutable version for every prediction in the run. SQLite uses a primary key and `INSERT ... ON CONFLICT DO UPDATE` so retrying the same logical scoring key replaces the result rather than creating duplicate rows. The job uses a generated source dataset; `--source-ref` records the immutable logical source identifier but does not itself read that source snapshot. Replace the fixture generator with a reader that enforces the recorded snapshot/watermark in a real pipeline. `pipeline_run_id` is a stable logical batch key; `execution_id` identifies each attempt. This demo uses upsert semantics so the newest successful attempt replaces the same logical prediction key.

```python
from __future__ import annotations

import argparse
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

import mlflow.pyfunc
import pandas as pd

from src.common import (
    FEATURE_COLUMNS,
    MODEL_NAME,
    configure_mlflow,
    model_uri_for_version,
    resolve_alias_version,
    require_finite_probability,
)
from src.train_register import make_dataset

DB_PATH = Path("data/predictions.db")

def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            entity_id TEXT NOT NULL,
            scoring_date TEXT NOT NULL,
            model_name TEXT NOT NULL,
            model_version TEXT NOT NULL,
            prediction_probability REAL NOT NULL,
            prediction_label INTEGER NOT NULL,
            scored_at_utc TEXT NOT NULL,
            pipeline_run_id TEXT NOT NULL,
            source_ref TEXT NOT NULL DEFAULT 'legacy-unknown',
            execution_id TEXT NOT NULL DEFAULT 'legacy-unknown',
            PRIMARY KEY (entity_id, scoring_date, model_name, model_version)
        )
    """)
    # SQLite CREATE TABLE IF NOT EXISTS does not add columns to an older lab DB.
    # Apply additive migrations for learners who rerun after updating this lesson.
    columns = {row[1] for row in conn.execute("PRAGMA table_info(predictions)")}
    if "source_ref" not in columns:
        conn.execute("ALTER TABLE predictions ADD COLUMN source_ref TEXT NOT NULL DEFAULT 'legacy-unknown'")
    if "execution_id" not in columns:
        conn.execute("ALTER TABLE predictions ADD COLUMN execution_id TEXT NOT NULL DEFAULT 'legacy-unknown'")
    conn.commit()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scoring-date", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--alias", default="champion")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--source-ref", default="synthetic-v1-seed-41",
                        help="Immutable source snapshot/version identifier for this demo run")
    args = parser.parse_args()

    if args.limit <= 0:
        raise ValueError("--limit must be positive")

    client = configure_mlflow()
    # Resolve the mutable alias once; the remainder of the run is pinned.
    version = resolve_alias_version(client, MODEL_NAME, args.alias)
    uri = model_uri_for_version(MODEL_NAME, version)
    model = mlflow.pyfunc.load_model(uri)

    features, _ = make_dataset(max(args.limit, 500))
    features = features.head(args.limit).copy()
    features.insert(0, "entity_id", [f"customer-{i:06d}" for i in range(len(features))])
    features["scoring_date"] = args.scoring_date

    raw = model.predict(features[FEATURE_COLUMNS])
    probabilities = [require_finite_probability(value) for value in raw]

    scored_at = datetime.now(timezone.utc).isoformat()
    logical_batch_id = f"batch-{args.scoring_date}-{version}-{args.source_ref}"
    execution_id = str(uuid.uuid4())
    rows = [
        (
            str(entity_id), args.scoring_date, MODEL_NAME, version,
            prob, int(prob >= 0.5), scored_at, logical_batch_id,
            args.source_ref, execution_id,
        )
        for entity_id, prob in zip(features["entity_id"], probabilities, strict=True)
    ]

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        ensure_schema(conn)
        conn.executemany("""
            INSERT INTO predictions (
                entity_id, scoring_date, model_name, model_version,
                prediction_probability, prediction_label, scored_at_utc,
                pipeline_run_id, source_ref, execution_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(entity_id, scoring_date, model_name, model_version)
            DO UPDATE SET
                prediction_probability=excluded.prediction_probability,
                prediction_label=excluded.prediction_label,
                scored_at_utc=excluded.scored_at_utc,
                pipeline_run_id=excluded.pipeline_run_id,
                source_ref=excluded.source_ref,
                execution_id=excluded.execution_id
        """, rows)
        conn.commit()

    print({
        "model_name": MODEL_NAME,
        "model_version": version,
        "scoring_date": args.scoring_date,
        "input_rows": len(features),
        "written_rows": len(rows),
        "scored_at_utc": scored_at,
        "logical_batch_id": logical_batch_id,
        "execution_id": execution_id,
        "source_ref": args.source_ref,
        "output_table": str(DB_PATH),
    })

if __name__ == "__main__":
    main()
```

Run after promoting a champion:

```bash
python -m src.batch_score --scoring-date 2026-10-19 --alias champion --limit 500
```

Query the output using Python or a SQLite client. Confirm that all rows in one run contain the same immutable version. Run the same command twice and verify that the logical key remains unique.

**Production caveats**

- The example's source rows are synthetic and the scoring key is pedagogical. Choose keys that reflect your business's intended semantics.
- If the business requires exactly one authoritative prediction per entity/date regardless of model version, model version should not be part of the uniqueness key; instead, define a replacement policy and store history in a separate append-only audit table. This is a business data-model decision, not a universal rule.
- `INSERT ... ON CONFLICT` is SQLite-specific. Use your warehouse/lakehouse's supported merge/upsert/transaction semantics in production.
- At scale, process in partitions and publish only after all partitions pass validation. Do not load a huge table into a single pandas DataFrame.
- Store the source snapshot/watermark, code commit, model URI, resolved version, input/output counts, and status in a run manifest.
- Late-arriving input requires an explicit backfill policy. A rerun should be distinguishable from a new scoring date.
- An alias can move during the job, but this job has already pinned its version. That is intentional.

### Incremental scoring pattern (warehouse/lakehouse)

The SQLite lab scores a deterministic synthetic fixture and is **not** a complete incremental source reader. In a real job, select only rows beyond a committed watermark, pin the source snapshot, and publish the watermark only after all output partitions validate. Example SQL shape (adapt syntax and transaction guarantees to the platform):

```sql
-- Read from an immutable source snapshot where the platform supports it.
-- :last_successful_watermark and :run_watermark are run-manifest values.
SELECT entity_id, scoring_date, feature_1, feature_2
FROM feature_snapshot
WHERE updated_at > :last_successful_watermark
  AND updated_at <= :run_watermark;
```

Store the source snapshot/watermark and model version in a run manifest. If a partition fails, do not advance the committed watermark; retry using the same source boundary and immutable model version. Corrections and late-arriving data require an explicit re-score/backfill policy, not just `updated_at > last_watermark`.

### 6.8 Spark/SQL scaling pattern

For large datasets, use Spark or warehouse SQL to read, validate, and partition data; use a supported model scoring integration or distributed pandas/partition processing as appropriate. The conceptual flow is:

```sql
-- Pseudocode: adapt syntax to your warehouse/lakehouse.
SELECT entity_id, feature_snapshot_id, feature_timestamp, ...
FROM features
WHERE feature_timestamp >= :window_start
  AND feature_timestamp <  :window_end
  AND scoring_status = 'eligible';
```

Then score each bounded partition with a pinned model version, and write output rows with:

```text
entity_id
prediction_id
model_name
model_version
scoring_timestamp_utc
source_snapshot_or_watermark
pipeline_run_id
prediction_probability
prediction_label
```

Do not use an alias independently in every partition if the alias can move mid-run. Resolve it once and pass the immutable version to all workers.

---

## 7. Online inference architecture and implementation

### 7.1 What online inference is

Online inference serves a prediction in response to a request, often with a tight end-to-end latency objective. The endpoint must receive or retrieve features, validate them, run the model, and return a response before the caller's deadline.

Online inference is justified when the decision needs current information at request time. Common serving choices include FastAPI for a custom Python service, BentoML for packaging/serving workflows, KServe for Kubernetes-based model serving, and managed endpoints in SageMaker or Vertex AI; Azure ML managed online endpoints are another option. These platforms differ in deployment primitives, identity, networking, autoscaling, and billing, so treat the names as architecture options rather than interchangeable APIs. Online serving introduces operational responsibilities that batch jobs may not have: concurrency, tail latency, request spikes, timeouts, network dependencies, service availability, feature freshness, and endpoint security.

### 7.2 Request path

```text
Caller
  ↓ request ID + entity ID
API gateway / authentication / rate limit
  ↓
Request validation
  ↓
Online feature lookup (Redis or equivalent)
  ↓ feature freshness + schema checks
Loaded immutable model version
  ↓
Prediction + output validation
  ↓
Safe structured log / metrics
  ↓
Response: prediction, model version, request ID
```

### 7.3 Latency budget

End-to-end latency is the sum of components:

```text
T_total = T_network + T_auth + T_validation + T_feature_lookup
          + T_model + T_logging + T_serialization + T_queueing
```

For a 50 ms fraud decision, a model that predicts in 2 ms can still miss the objective if feature lookup takes 35 ms, queueing takes 15 ms, or network hops add delay. Measure p50, p95, p99, timeout rate, and end-to-end latency—not only the model's average execution time.

Set explicit timeouts for feature-store and model calls. Define what happens on failure: reject the request, return a safe fallback, or route to a deterministic policy. A fallback must be approved and observable; never silently fabricate a model prediction.

### 7.4 Local feature-store substitute: `src/feature_store.py`

For a self-contained local lab, use SQLite as the feature store. The interface isolates storage so it can later be replaced by Redis or another online store.

```python
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


from src.common import FEATURE_COLUMNS

DB_PATH = Path("data/features.db")

def initialize_features() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ("customer-000001", 18.0, 89.0, 2.0, 0.72),
        ("customer-000002", 54.0, 61.0, 0.0, 1.05),
        ("customer-000003", 3.0, 112.0, 5.0, 0.31),
    ]
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS online_features (
                entity_id TEXT PRIMARY KEY,
                tenure_months REAL NOT NULL,
                monthly_charges REAL NOT NULL,
                support_tickets_90d REAL NOT NULL,
                usage_ratio_30d REAL NOT NULL,
                feature_timestamp_utc TEXT NOT NULL
            )
        """)
        now = datetime.now(timezone.utc).isoformat()
        conn.executemany("""
            INSERT OR IGNORE INTO online_features (
                entity_id, tenure_months, monthly_charges,
                support_tickets_90d, usage_ratio_30d, feature_timestamp_utc
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, [(*row, now) for row in rows])
        conn.commit()

def get_features(entity_id: str, max_age_seconds: int = 3600) -> tuple[dict[str, float], str]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM online_features WHERE entity_id = ?", (entity_id,)
        ).fetchone()
    if row is None:
        raise KeyError("Features not found for entity")
    timestamp = datetime.fromisoformat(row["feature_timestamp_utc"])
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("Feature timestamp must include a timezone")
    age = (datetime.now(timezone.utc) - timestamp).total_seconds()
    if age < 0 or age > max_age_seconds:
        raise ValueError(f"Feature record is stale (age_seconds={age:.1f})")
    values: dict[str, float] = {name: float(row[name]) for name in FEATURE_COLUMNS}
    return values, row["feature_timestamp_utc"]
```

The sample initializer inserts three fictional entities only when they do not already exist. Restarting the API must not refresh feature timestamps and disguise stale features. To simulate a real refresh, update the row through a separate feature pipeline. A real system should define freshness requirements per feature group. Avoid returning different stale/freshness errors to unauthorized callers if doing so would leak entity existence.

### 7.5 FastAPI endpoint: `src/api.py`

The API loads a specific immutable model version at process startup. For the learning example, set `MODEL_VERSION` explicitly after registration/promotion. This avoids silently changing the model under a process because a mutable alias moved. A deployment controller can roll out a new process with a new pinned version after approval.

```python
from __future__ import annotations

import json
import logging
import math
import os
import time
from contextlib import asynccontextmanager
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from src.common import FEATURE_COLUMNS, MODEL_NAME, configure_mlflow, model_uri_for_version, require_finite_probability
from src.feature_store import get_features, initialize_features

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("churn-inference")
PREDICTION_LOG = Path(os.getenv("PREDICTION_LOG", "data/predictions_online.jsonl"))
MODEL_VERSION = os.getenv("MODEL_VERSION", "")
DECISION_THRESHOLD = float(os.getenv("DECISION_THRESHOLD", "0.5"))
MAX_FEATURE_AGE_SECONDS = int(os.getenv("MAX_FEATURE_AGE_SECONDS", "3600"))
if not math.isfinite(DECISION_THRESHOLD) or not 0.0 <= DECISION_THRESHOLD <= 1.0:
    raise ValueError("DECISION_THRESHOLD must be finite and between 0 and 1")
if MAX_FEATURE_AGE_SECONDS <= 0:
    raise ValueError("MAX_FEATURE_AGE_SECONDS must be positive")

class ScoreRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entity_id: str = Field(min_length=1, max_length=128)
    request_id: str | None = Field(default=None, min_length=1, max_length=128)

class ScoreResponse(BaseModel):
    request_id: str
    entity_id: str
    model_name: str
    model_version: str
    probability: float = Field(ge=0.0, le=1.0)
    decision: Literal["churn_risk", "not_churn_risk"]
    feature_timestamp_utc: str
    latency_ms: float = Field(ge=0.0)

model = None
loaded_version = MODEL_VERSION

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, loaded_version
    if not MODEL_VERSION:
        raise RuntimeError("Set MODEL_VERSION to an immutable registered version before startup")
    client = configure_mlflow()
    # Ensure the requested version exists, then load that exact version.
    client.get_model_version(MODEL_NAME, MODEL_VERSION)
    model = mlflow.pyfunc.load_model(model_uri_for_version(MODEL_NAME, MODEL_VERSION))
    # Idempotent fixture initialization inserts only missing rows; it does not
    # make old feature records appear fresh on every restart.
    initialize_features()
    loaded_version = str(MODEL_VERSION)
    logger.info(json.dumps({"event": "model_loaded", "model_name": MODEL_NAME,
                            "model_version": loaded_version}))
    try:
        yield
    finally:
        model = None

app = FastAPI(title="Churn scoring API", version="1.0.0", lifespan=lifespan)

@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "alive"}

@app.get("/health/ready")
def ready() -> dict[str, str]:
    if model is None:
        raise HTTPException(status_code=503, detail="model_not_loaded")
    return {"status": "ready", "model_name": MODEL_NAME, "model_version": loaded_version}

@app.post("/v1/score", response_model=ScoreResponse)
def score(request: ScoreRequest) -> ScoreResponse:
    started = time.perf_counter()
    request_id = request.request_id or str(uuid.uuid4())
    if model is None:
        raise HTTPException(status_code=503, detail="model_not_ready")

    try:
        features, feature_timestamp = get_features(
            request.entity_id, max_age_seconds=MAX_FEATURE_AGE_SECONDS
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="features_not_found") from None
    except ValueError:
        raise HTTPException(status_code=503, detail="features_stale") from None

    # Basic semantic validation in addition to the model signature.
    if features["tenure_months"] < 0 or features["monthly_charges"] < 0:
        raise HTTPException(status_code=422, detail="invalid_feature_range")
    if features["support_tickets_90d"] < 0:
        raise HTTPException(status_code=422, detail="invalid_feature_range")

    try:
        input_df = pd.DataFrame([features], columns=FEATURE_COLUMNS)
        output = model.predict(input_df)
        probability = require_finite_probability(output[0])
    except Exception:
        logger.exception(json.dumps({
            "event": "prediction_error",
            "request_id": request_id,
            "model_name": MODEL_NAME,
            "model_version": loaded_version,
        }))
        raise HTTPException(status_code=500, detail="prediction_failed") from None

    latency_ms = (time.perf_counter() - started) * 1000.0
    response = ScoreResponse(
        request_id=request_id,
        entity_id=request.entity_id,
        model_name=MODEL_NAME,
        model_version=loaded_version,
        probability=probability,
        decision="churn_risk" if probability >= DECISION_THRESHOLD else "not_churn_risk",
        feature_timestamp_utc=feature_timestamp,
        latency_ms=latency_ms,
    )
    PREDICTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    # Local demo only. Production systems should use structured, access-controlled
    # logs/queues and avoid raw features or identifiers unless policy permits.
    event = {
        "event": "prediction",
        "request_id": request_id,
        "model_name": MODEL_NAME,
        "model_version": loaded_version,
        "entity_id": request.entity_id,
        "probability": probability,
        "decision": response.decision,
        "feature_timestamp_utc": feature_timestamp,
        "prediction_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "latency_ms": latency_ms,
    }
    try:
        with PREDICTION_LOG.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")
    except OSError:
        # Local demo policy: prediction remains valid, but telemetry failure is
        # visible and must be monitored. Production should use a durable queue.
        logger.exception(json.dumps({"event": "prediction_telemetry_write_failed",
                                     "request_id": request_id,
                                     "model_version": loaded_version}))
    logger.info(json.dumps({
        "event": "prediction_complete",
        "request_id": request_id,
        "model_version": loaded_version,
        "latency_ms": round(latency_ms, 3),
    }))
    return response
```

**Operational notes**

- This sample uses FastAPI's Pydantic validation and a response model. The feature values themselves are returned from a trusted feature store, not accepted directly from arbitrary clients.
- The local file append is for demonstration. Multiple worker processes, concurrent writers, rotation, retention, and durability require a proper logging/queue/storage design.
- The example uses FastAPI lifespan management, the recommended mechanism for loading and releasing shared model resources. The pinned FastAPI version supports this pattern.
- In production, do not expose stack traces, credentials, or raw feature values in client errors.
- Health endpoints should distinguish liveness from readiness. Readiness should fail until the intended model is loaded and critical dependencies are available.
- Set `MODEL_VERSION` to the immutable version. If you choose to resolve `champion` during startup instead, log the resolved version and still keep the running process pinned until a controlled reload/redeployment.
- A production service should use authentication, authorization, request-size limits, rate limiting, network controls, secrets management, and a proper telemetry backend.

Start the API in a terminal after choosing a registered version:

```bash
export MODEL_VERSION=1
uvicorn src.api:app --host 127.0.0.1 --port 8000
```

Initialize the local features database before the first request if your environment does not run the startup handler yet:

```bash
python -c "from src.feature_store import initialize_features; initialize_features()"
```

Test a request:

```bash
curl -X POST http://127.0.0.1:8000/v1/score \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"customer-000001"}'
```

The response contains a request ID, model name/version, probability, decision, feature timestamp, and latency measured by the application. **The code does not claim any specific latency percentile.** Measure it in your environment.

### 7.6 Redis in production

A Redis-backed online store is a common option when feature lookups need low latency. A robust design should include:

- entity or entity-plus-feature-group keys;
- a schema/version identifier;
- event-time and materialization-time metadata;
- TTL and freshness policy;
- atomic updates or versioned writes;
- timeouts and connection pooling;
- handling for missing or stale features;
- authentication, TLS, network policy, and secret rotation;
- metrics for lookup latency, hit/miss ratio, stale records, and errors.

Do not assume Redis is always the right store. A managed key-value store, embedded cache, online feature store, or request-provided feature set may fit better. The feature-store contract matters more than the brand.

### 7.7 Caching trade-offs

Caching can lower repeated lookup cost, but a cache introduces staleness and invalidation problems. Cache only when:

- the feature definition allows a known freshness window;
- the cache key includes all inputs that affect the result;
- authorization is checked before serving cached data;
- model or feature version changes invalidate or namespace affected entries;
- cache hit rate, staleness, and error behavior are measured.

For highly time-sensitive fraud features, a stale cache may be worse than a slower source of truth. Define a freshness budget per feature, not one arbitrary TTL for all features.

### 7.8 Shadow predictions: `src/shadow_compare.py`

A shadow deployment sends the same eligible input to the champion and challenger, but **only the champion's result controls the production response or business action**. The challenger prediction is recorded separately for comparison.

```python
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import mlflow.pyfunc
import pandas as pd

from src.common import (
    FEATURE_COLUMNS,
    MODEL_NAME,
    configure_mlflow,
    model_uri_for_version,
    resolve_alias_version,
    require_finite_probability,
)

OUT = Path("data/shadow_predictions.jsonl")

def main() -> None:
    client = configure_mlflow()
    champion_version = resolve_alias_version(client, MODEL_NAME, "champion")
    challenger_version = resolve_alias_version(client, MODEL_NAME, "challenger")
    champion = mlflow.pyfunc.load_model(model_uri_for_version(MODEL_NAME, champion_version))
    challenger = mlflow.pyfunc.load_model(model_uri_for_version(MODEL_NAME, challenger_version))

    sample = pd.DataFrame([{
        "tenure_months": 18.0,
        "monthly_charges": 89.0,
        "support_tickets_90d": 2.0,
        "usage_ratio_30d": 0.72,
    }], columns=FEATURE_COLUMNS)

    champion_probability = float(champion.predict(sample)[0])
    challenger_probability = float(challenger.predict(sample)[0])
    # Only this value is authoritative for the production decision.
    authoritative_probability = champion_probability

    record = {
        "request_id": "shadow-demo-001",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "champion_version": champion_version,
        "challenger_version": challenger_version,
        "champion_probability": champion_probability,
        "challenger_probability": challenger_probability,
        "absolute_probability_delta": abs(champion_probability - challenger_probability),
        "authoritative_probability": authoritative_probability,
        "shadow_output_used_for_decision": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    print(record)

if __name__ == "__main__":
    main()
```

This is a minimal offline shadow demonstration, not a traffic router. A production shadow system needs sampling rules, asynchronous dispatch, separate failure isolation, privacy controls, capacity protection, duplicate request correlation, and a policy that prevents challenger outputs from causing side effects. Do not send shadow traffic to downstream systems that charge customers or mutate state.

### 7.9 Rollback

In the alias-based lab, rollback means assigning `champion` to a previously approved immutable version:

```python
from mlflow.exceptions import MlflowException

from src.common import MODEL_NAME, configure_mlflow

client = configure_mlflow()
client.set_registered_model_alias(MODEL_NAME, "champion", "<KNOWN_GOOD_VERSION>")
```

Before rollback, verify the target version is still loadable and compatible with current inputs. Then confirm that the serving fleet or next batch run actually loaded the intended version. Alias movement alone does not reload an existing process. The roadmap phrase “rollback by moving the alias, with no code redeploy” is true only for a consumer that resolves the alias dynamically for each new scoring unit or a deployment controller that watches alias changes and safely reloads. This lab API pins `MODEL_VERSION` at startup, so its rollback requires a controlled process restart/redeployment (or a separately implemented reload controller); never imply that moving `champion` changes an already loaded model.

For a deployment platform, rollback may instead mean routing traffic to a previous endpoint revision or deployment package. Maintain a tested rollback target, deployment configuration, compatible feature contract, and a clear decision owner. If the feature schema has changed incompatibly, rolling back only the model may not be sufficient.

---

## 8. Batch vs online vs streaming decision framework

### 8.1 Definitions

- **Batch inference:** score a bounded set of records on a schedule or data event.
- **Online inference:** score an individual request synchronously within a latency budget.
- **Streaming inference:** continuously process events or micro-batches as they arrive, often with state/windowing and event-time semantics.
- **Precompute-and-serve hybrid:** compute expensive or reusable features/predictions ahead of time, then retrieve them at request time and optionally combine them with fresh features or a lightweight model.

These patterns can coexist. A system may precompute most recommendation candidates hourly, then rank a short list online using current context.

### 8.2 Decision table

| Requirement | Likely starting pattern | Why | Key risk |
|---|---|---|---|
| Fraud decision with a 50 ms end-to-end requirement | Online, often with precomputed features and a carefully budgeted feature lookup | Decision must arrive before transaction authorization | Tail latency, stale features, dependency timeout, safe fallback |
| Daily churn emails | Batch | A daily score is sufficient; large cohorts can be scored efficiently | Late source data, duplicate sends, missed cohort |
| Hourly recommendations | Hourly batch or streaming precompute plus online retrieval/reranking | Candidate generation can be expensive; serving needs reasonably fresh results | Stale recommendations, cache invalidation, feedback loops |
| Real-time sensor alert | Streaming or online depending on event and request semantics | Events must be evaluated continuously | Late/out-of-order events, state recovery, exactly-once assumptions |
| High-volume offline risk portfolio | Batch | Throughput and cost per row matter more than per-request latency | Backfill, reproducibility, partial failures |

### 8.3 Decision variables

Evaluate these explicitly:

1. **Freshness:** How old may a feature or prediction be before the business decision is wrong?
2. **Latency:** What is the end-to-end deadline at p95/p99, not just average model runtime?
3. **Throughput:** How many rows/events/requests arrive at peak?
4. **Cost:** What are the compute, storage, endpoint, network, and operational costs?
5. **Complexity:** Can the team operate caches, online feature stores, streaming state, autoscaling, and on-call reliably?
6. **Consistency:** Must a prediction be reproducible from a fixed snapshot, or must it reflect latest state?
7. **Failure behavior:** Is it safe to defer, reject, use a fallback, or return the last known prediction?
8. **Audit needs:** Must the system prove which features and model version led to a decision?

### 8.4 Worked choices

**Fraud scoring, 50 ms.** Start with online inference if the decision is required before authorizing a transaction. Precompute slower aggregates and materialize them to an online store; calculate only truly request-time features in the request path. Set a total deadline and allocate it across network, feature lookup, model, and response. Test p99 under realistic peak concurrency. If a feature dependency cannot meet the budget, define an approved fallback or fail-closed policy with the risk owner.

**Daily churn emails.** Use batch scoring over a stable daily cohort. Record the source snapshot, scoring date, and model version. Use an idempotent send key so retries do not email the same customer twice. Keep the scoring table separate from the email-delivery status table so a failed delivery can retry without rescoring or changing the model result.

**Hourly recommendations.** Consider hourly batch candidate generation and feature materialization, with online retrieval and optional lightweight reranking. This avoids running an expensive full model for every page view while preserving some freshness. Monitor recommendation freshness, coverage, click/conversion outcomes, and the effects of feedback loops.

### 8.5 Streaming-specific concerns

Streaming inference adds event-time and state concerns: event-time versus processing-time, watermarks, late events, state TTL, duplicate delivery, checkpoint recovery, and output semantics. “Exactly once” is end-to-end only if source, processing, and sink semantics support it; do not assume it from a framework label alone. If the business can accept hourly freshness, batch or micro-batch may be simpler and cheaper.

---

## 9. Prediction logging and observability

### 9.1 What to record

A prediction log is the raw material for incident investigation, drift analysis, and later joining predictions to outcomes. A useful record may include:

| Field | Purpose |
|---|---|
| `prediction_id` / `request_id` | Correlate request, response, and retries |
| Entity or business key reference | Join to authorized outcomes; use pseudonymous or tokenized IDs where possible |
| Model name and immutable version | Identify the exact artifact used |
| Model alias at resolution time (optional) | Explain which deployment reference was resolved |
| Prediction timestamp | Define when the output was produced |
| Feature timestamp / source snapshot | Assess freshness and reconstruct the input state |
| Prediction output and decision | Analyze score distribution and decisions |
| Latency and status | Operational observability |
| Error category | Separate schema, feature-store, model, and downstream failures |
| Outcome/label reference and label-available timestamp | Evaluate performance when ground truth arrives |
| Pipeline run ID / deployment revision | Trace to batch job or online deployment |
| Code/configuration version | Explain runtime behavior |

### 9.2 Log references, not unnecessary raw features

Input logging can create privacy and security risks. Prefer logging feature-definition version, source snapshot, safe feature references, and a minimal set of approved diagnostics. If raw feature values are needed for debugging, apply data minimization, access controls, encryption, retention limits, and redaction. Never log credentials, authorization headers, secrets, or unnecessary direct identifiers.

Prediction logs should have a documented schema, retention period, owner, and access policy. Treat them as governed data products, not arbitrary application text files.

### 9.3 Operational versus model-quality signals

**Operational signals** can usually be measured immediately:

- request rate, concurrency, and queue depth;
- p50/p95/p99 latency;
- timeout and error rates;
- feature lookup latency, missingness, and staleness;
- model load failures and version distribution across instances;
- batch duration, input/output counts, retries, and source lag;
- CPU, memory, GPU utilization, and cost.

**Model-quality signals** often need labels that arrive later:

- precision/recall, AUC, calibration, loss, and business outcomes;
- slice-level performance by relevant cohorts;
- drift in inputs, scores, and outcomes;
- false positive/false negative costs;
- fairness and adverse impact measures where appropriate.

Do not confuse a healthy endpoint with a good model. A service can have 99.99% availability while its predictions are no longer useful.

### 9.4 Outcome joining

When outcomes arrive later, join them to predictions using a stable prediction/entity key and a defined outcome window. Track label availability time to avoid evaluating only the cases whose labels arrive quickly. Handle corrections and censored observations explicitly. Topic 05 develops drift and delayed-label monitoring in detail.

---

## 10. Deployment strategies and promotion gates

### 10.1 Shadow deployment

**Purpose:** compare a candidate on real or representative inputs without allowing it to control production actions.

**How:** send eligible input to the champion and challenger; return or act on the champion output; log both with correlated IDs; compare quality, latency, errors, and slice differences.

**Trade-off:** lower risk than switching traffic, but shadow results may not reveal user behavior changes caused by the challenger because users never experience its output. Protect capacity and isolate side effects.

### 10.2 Canary deployment

Route a small, controlled percentage or cohort to the new deployment. Increase traffic only after predefined checks pass. Canary analysis must account for sample size, time-of-day effects, cohort mix, and guardrail metrics. A tiny canary may be too small to detect rare but severe failures.

### 10.3 Blue/green deployment

Maintain two deployment environments. Deploy and validate the new version in the inactive environment, then switch routing. Rollback can be fast if the old environment remains healthy and compatible. Costs more because two environments may run simultaneously; data and schema compatibility still matter.

### 10.4 A/B testing

Randomly assign eligible users or units to variants and evaluate a predeclared outcome. Define randomization unit, exposure logging, experiment duration, guardrails, and statistical analysis before launch. Avoid switching models mid-experiment without recording assignment and version; otherwise treatment contamination can make results uninterpretable.

### 10.5 Champion/challenger is a comparison pattern

Champion/challenger describes roles, not a traffic strategy by itself. A challenger may be evaluated offline, in shadow, in a canary, or in a formal A/B test. Define which pattern is used and which outputs are authoritative.

### 10.6 Automated promotion gates

A production gate should be executable, versioned, and auditable. A robust sequence:

```text
Build artifact
  → load and signature tests
  → offline evaluation against baseline
  → slice and fairness checks
  → security/dependency checks
  → batch/online parity checks
  → staging smoke and load tests
  → approval record
  → controlled rollout
  → post-deploy health and quality checks
  → complete rollout or rollback
```

Gate requirements should be risk-tiered. A low-risk ranking model may use automated approval after all checks; a high-impact financial or eligibility model may require documented human review and additional controls. Record failed gates and reasons rather than silently overwriting them.

### 10.7 Baseline and slice metrics

Aggregate metrics can hide harm to smaller groups. Compare candidate and baseline on predefined slices such as region, product, device type, customer tenure, or other legitimate business segments. Avoid unplanned, tiny slices that produce noisy results or expose sensitive data. For fairness checks, use legally and contextually appropriate definitions, governance, and expertise; a single metric is not a universal proof of fairness.

### 10.8 Rollback runbook

A rollback runbook should specify:

1. Trigger thresholds and decision owner.
2. Last known-good immutable model version and compatible schema.
3. How to restore alias or endpoint traffic.
4. How to confirm the fleet has loaded the old version.
5. How to pause batch jobs or stop publishing candidate outputs.
6. How to preserve prediction logs and incident evidence.
7. How to communicate to downstream consumers.
8. How to prevent duplicate side effects during retries.
9. How to decide whether a data/schema rollback is also needed.
10. Post-incident review and corrective actions.

A rollback is not complete when the alias changes; it is complete when the serving path is verified, business decisions are back under the approved model, and downstream effects are understood.

---

## 11. Scaling, cost, SLOs, and model governance

### 11.1 Autoscaling and batching

Autoscaling can improve resilience to demand spikes, but scale-out may add model load time, cold-start latency, and registry/artifact traffic. Test scale-from-zero and scale-out behavior, not only steady state. Request batching can increase throughput on suitable runtimes, but may increase individual request latency due to waiting for a batch to fill.

Set limits on concurrency, queue size, payload size, and maximum in-flight feature lookups. Backpressure is preferable to unbounded queues that turn a short spike into a long latency collapse.

### 11.2 CPU versus GPU

Choose hardware from measured end-to-end workload characteristics:

- CPU is often simpler and more cost-effective for small tabular models and moderate request rates.
- GPU may help large neural models or batched tensor workloads, but has utilization, memory, scheduling, and cold-start costs.
- Benchmark at realistic batch sizes, concurrency, payloads, and tail-latency targets.
- Include model loading, preprocessing, feature lookup, networking, and idle time in cost comparisons.

Do not choose GPU merely because the model is “machine learning.” Measure throughput per dollar and latency under the actual service objective.

### 11.3 ONNX and quantization (awareness)

ONNX can provide a portable inference representation for supported models and runtimes. Quantization reduces numeric precision to improve performance or memory use on compatible workloads. Both require compatibility and accuracy testing; conversion may not support every operator or preprocessing step. Compare predictions against a golden set and measure task metrics, numerical deviations, latency, memory, and hardware behavior before promotion. This lesson does not attempt to optimize model internals; that belongs in the roadmap's later optimization stage.

### 11.4 Serverless endpoints

Serverless inference can reduce infrastructure management and scale to intermittent traffic, but consider cold starts, execution limits, concurrency, network access, model size, and cost at sustained volume. Always compare total cost and latency at realistic traffic levels rather than assuming serverless is automatically cheaper.

### 11.5 SLOs and error budgets

Define service-level objectives such as:

- request success rate over a rolling window;
- p95 and p99 end-to-end latency;
- feature freshness or maximum staleness;
- batch completion deadline and data coverage;
- model-version consistency across serving instances;
- recovery time after deployment failure.

A metric is not an SLO until it has a target, measurement window, owner, and response policy. An error budget helps balance reliability work against deployment velocity. Model-quality SLOs are distinct from service availability SLOs and may depend on delayed labels.

### 11.6 Cost per million predictions

A useful estimate:

```text
cost_per_million =
  (compute_cost + endpoint_cost + feature_store_cost
   + network_cost + storage_and_logging_cost + allocated_platform_cost)
  / successful_predictions
  * 1,000,000
```

Keep the units consistent. If compute is measured hourly, multiply by the actual hours used. For a batch job, include orchestration and storage costs. For an online endpoint, include provisioned idle capacity, autoscaling overhead, feature store, network, logging, and any GPU reservation. State whether failed requests are included in the denominator; for business cost per successful prediction, use successful predictions and report failures separately.

**Illustration only:** if a measured workload costs $120 for 2,000,000 successful predictions, then the measured cost is `$60 per million`. This is arithmetic, not a benchmark or a claim about any cloud provider. Replace the inputs with invoices and observed successful counts from your own workload.

### 11.7 Load testing and percentiles

A load test should specify:

- hardware and deployment configuration;
- model version and input distribution;
- warm-up period;
- request rate and concurrency;
- duration and test tool/version;
- payload sizes and feature-store behavior;
- whether the test is closed-loop or open-loop;
- number of successful, failed, and timed-out requests;
- p50, p95, p99 latency and throughput;
- CPU, memory, GPU, queue, and dependency metrics.

Average latency can conceal a poor tail. If p99 is 200 ms, at least roughly 1% of requests in the measurement distribution are at or above that tail boundary, subject to quantile estimation and sample size. Do not invent results in a report; run the test, save raw results, and include enough context to reproduce it.

A simple procedure using a tool such as `hey`, `wrk`, Locust, or k6:

```bash
# Start the API first, then run a representative load test.
# Example with hey; install and verify the tool separately.
hey -n 10000 -c 50 \
  -m POST \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"customer-000001"}' \
  http://127.0.0.1:8000/v1/score
```

This command is a procedure, not a claim that it will meet any target. A single fixed entity may exaggerate cache hit rates; include a representative entity distribution and realistic feature-store load in a proper test.

### 11.8 Model cards and governance

A model card should summarize intended use, excluded use, training data provenance at an appropriate level, evaluation methodology, aggregate and slice performance, limitations, risks, monitoring plan, owner, and contact/escalation path. It should be updated when intended use or material behavior changes.

Governance also includes:

- approval records and model-risk classification;
- access control for registry, artifacts, endpoints, and logs;
- audit trails for alias changes and deployment operations;
- data lineage and retention;
- incident ownership and retirement;
- controls for foundation models, prompts, and evaluation artifacts where relevant.

### 11.9 Foundation models and prompt versions (awareness)

For foundation-model systems, the deployable behavior may depend on model provider/version, prompt template, system instructions, retrieval index, tools, safety configuration, and evaluation harness—not just a weight file. Version prompts and evaluation datasets, record the provider/model identifier, and run regression evaluations before changing a prompt or model. Avoid logging secrets or sensitive user content by default. Detailed LLM architecture and evaluation design are outside this topic's scope and are covered in later roadmap stages.

---

## 12. End-to-end hands-on project

### 12.1 Project objective

Build a small but coherent model lifecycle and inference system under `experiments/04_registry_inference/`. The goal is to demonstrate the **control flow** from experiment to registered version, automated gate, batch scoring, online scoring, shadow comparison, and rollback. Local storage is used only to make the project runnable without cloud credentials.

### 12.2 Recommended run order

1. Create the environment and start the MLflow server.
2. Train and register a baseline candidate.
3. Inspect the registered model version, run metadata, signature, and artifacts.
4. Assign `challenger` after the minimum gate passes.
5. Promote a version to `champion` only after review.
6. Run batch scoring with an explicit scoring date.
7. Initialize local feature records and start the API with a pinned `MODEL_VERSION`.
8. Call `/health/ready`, then send a prediction request.
9. Register a second candidate, run the gate, and assign `challenger`.
10. Run shadow comparison; confirm the champion probability remains authoritative.
11. Load-test and record observed percentiles and errors.
12. Move `champion` back to the known-good version. Because the lab API pins `MODEL_VERSION` at startup, restart/redeploy it with that immutable version and verify readiness; alias movement alone does not change a running process. A separate alias-aware controller would be required for rollback without a process redeploy.
13. Run tests and document the run evidence.

### 12.2.1 Minimal `README.md` runbook

From `experiments/04_registry_inference/`, after creating the files exactly as shown:

```bash
python -m venv .venv
# activate the environment, then:
python -m pip install -r requirements.txt
export PYTHONPATH=.
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
export MLFLOW_REGISTRY_URI=http://127.0.0.1:5000
# In a version-controlled repository, use the actual commit SHA:
export GIT_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo local-unversioned)"
python -m src.train_register
# Copy the printed version and use it below; promotion reads validation_auc.
python -m src.promote --version <VERSION> --allow-unversioned-local
# Only after review, provide a real approval record in your environment:
python -m src.promote --version <VERSION> --allow-unversioned-local --promote-to-champion --approval-id <APPROVAL_ID>
python -m src.batch_score --scoring-date 2026-10-19 --alias champion --limit 500
export MODEL_VERSION=<VERSION>
uvicorn src.api:app --host 127.0.0.1 --port 8000
```

Run tests with `pytest -q`. In a shell without Git metadata, `GIT_COMMIT` is not set and the lab tags the run `local-unversioned`; use `--allow-unversioned-local` only for the local exercise. The example commands are instructions, not claimed execution results. `README.md` should also record the actual dependency lock, Python version, observed test output, registered version IDs, and environment-specific limitations.

### 12.3 Environment variables

`.env.example`:

```text
MLFLOW_TRACKING_URI=http://127.0.0.1:5000
MLFLOW_REGISTRY_URI=http://127.0.0.1:5000
MODEL_NAME=churn
MODEL_VERSION=1
DECISION_THRESHOLD=0.5
MAX_FEATURE_AGE_SECONDS=3600
PREDICTION_LOG=data/predictions_online.jsonl
LOG_LEVEL=INFO
```

This is an example file only; do not commit secrets. The code shown reads environment variables but does not automatically load `.env`. Export the variables in the shell or deliberately add a dotenv loader and pin it.

### 12.4 Contract tests: `tests/test_contracts.py`

```python
import math

import pandas as pd
import pytest
from fastapi.testclient import TestClient

import src.api as api

from src.common import FEATURE_COLUMNS, require_finite_probability
from src.feature_store import initialize_features, get_features
from src.promote import gate_passes
from src.train_register import make_dataset, dataset_fingerprint
from src.batch_score import ensure_schema

def test_feature_contract_columns_and_order():
    example = pd.DataFrame([{
        "tenure_months": 18.0,
        "monthly_charges": 89.0,
        "support_tickets_90d": 2.0,
        "usage_ratio_30d": 0.72,
    }])
    assert list(example.columns) == FEATURE_COLUMNS
    assert all(pd.api.types.is_numeric_dtype(example[c]) for c in FEATURE_COLUMNS)

@pytest.mark.parametrize("value", [0.0, 0.4, 1.0])
def test_valid_probability(value):
    assert require_finite_probability(value) == value

@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan"), float("inf"), -float("inf")])
def test_invalid_probability(value):
    with pytest.raises(ValueError):
        require_finite_probability(value)

def test_gate_requires_minimum_and_limits_regression():
    assert gate_passes(0.82, 0.81, 0.70, 0.002)
    assert not gate_passes(0.79, 0.81, 0.70, 0.002)
    assert not gate_passes(0.69, None, 0.70, 0.002)
    assert not gate_passes(float("nan"), None, 0.70, 0.002)

def test_local_feature_store_contract_and_restart_freshness(monkeypatch, tmp_path):
    import src.feature_store as fs
    monkeypatch.setattr(fs, "DB_PATH", tmp_path / "features.db")
    initialize_features()
    values, timestamp_before = get_features("customer-000001")
    initialize_features()  # must not rewrite the feature timestamp on restart
    values_after, timestamp_after = get_features("customer-000001")
    assert set(values) == set(FEATURE_COLUMNS)
    assert all(math.isfinite(v) for v in values.values())
    assert values_after == values
    assert timestamp_after == timestamp_before

def test_api_returns_prediction_with_pinned_model_version(monkeypatch, tmp_path):
    class FakeClient:
        def get_model_version(self, name, version):
            assert name == "churn"
            assert version == "7"

    class FakeModel:
        def predict(self, frame):
            assert list(frame.columns) == FEATURE_COLUMNS
            return [0.73]

    monkeypatch.setattr(api, "MODEL_VERSION", "7")
    monkeypatch.setattr(api, "configure_mlflow", lambda: FakeClient())
    monkeypatch.setattr(api.mlflow.pyfunc, "load_model", lambda uri: FakeModel())
    monkeypatch.setattr(api, "initialize_features", lambda: None)
    monkeypatch.setattr(api, "get_features", lambda entity_id, max_age_seconds: (
        {"tenure_months": 18.0, "monthly_charges": 89.0,
         "support_tickets_90d": 2.0, "usage_ratio_30d": 0.72},
        "2026-10-19T12:00:00+00:00",
    ))
    monkeypatch.setattr(api, "PREDICTION_LOG", tmp_path / "predictions.jsonl")
    with TestClient(api.app) as client:
        response = client.post("/v1/score", json={"entity_id": "customer-test", "request_id": "req-test"})
        assert response.status_code == 200
        body = response.json()
        assert body["model_version"] == "7"
        assert body["probability"] == pytest.approx(0.73)
        assert body["request_id"] == "req-test"
        assert (tmp_path / "predictions.jsonl").exists()


def test_api_rejects_nonfinite_model_output(monkeypatch, tmp_path):
    class FakeClient:
        def get_model_version(self, name, version):
            return None

    class FakeModel:
        def predict(self, frame):
            return [float("nan")]

    monkeypatch.setattr(api, "MODEL_VERSION", "8")
    monkeypatch.setattr(api, "configure_mlflow", lambda: FakeClient())
    monkeypatch.setattr(api.mlflow.pyfunc, "load_model", lambda uri: FakeModel())
    monkeypatch.setattr(api, "initialize_features", lambda: None)
    monkeypatch.setattr(api, "get_features", lambda entity_id, max_age_seconds: (
        {"tenure_months": 18.0, "monthly_charges": 89.0,
         "support_tickets_90d": 2.0, "usage_ratio_30d": 0.72},
        "2026-10-19T12:00:00+00:00",
    ))
    monkeypatch.setattr(api, "PREDICTION_LOG", tmp_path / "predictions.jsonl")
    with TestClient(api.app) as client:
        response = client.post("/v1/score", json={"entity_id": "customer-test"})
        assert response.status_code == 500
        assert not (tmp_path / "predictions.jsonl").exists()


def test_synthetic_dataset_fingerprint_is_deterministic_and_order_sensitive():
    x1, y1 = make_dataset(100)
    x2, y2 = make_dataset(100)
    assert dataset_fingerprint(x1, y1) == dataset_fingerprint(x2, y2)
    assert dataset_fingerprint(x1.iloc[::-1].reset_index(drop=True),
                               y1.iloc[::-1].reset_index(drop=True)) != dataset_fingerprint(x1, y1)


def test_batch_schema_adds_new_columns_to_existing_local_database():
    import sqlite3
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE predictions (
            entity_id TEXT NOT NULL, scoring_date TEXT NOT NULL,
            model_name TEXT NOT NULL, model_version TEXT NOT NULL,
            prediction_probability REAL NOT NULL, prediction_label INTEGER NOT NULL,
            scored_at_utc TEXT NOT NULL, pipeline_run_id TEXT NOT NULL,
            PRIMARY KEY(entity_id, scoring_date, model_name, model_version)
        )
    """)
    ensure_schema(conn)
    columns = {row[1] for row in conn.execute("PRAGMA table_info(predictions)")}
    assert {"source_ref", "execution_id"}.issubset(columns)
    conn.close()

```

These tests cover finite outputs, gate logic, schema invariants, and feature-store initialization without requiring a live MLflow server. The API contract is also tested manually below because startup needs a registered model. Add integration tests that start MLflow, register a model, load it by immutable version, and compare golden outputs; do not rely on mocked behavior alone for a promotion gate.

### 12.5 Batch idempotency test: `tests/test_batch_idempotency.py`

This test checks the database key behavior independently of the MLflow server:

```python
import sqlite3

def test_prediction_primary_key_prevents_duplicate_logical_rows():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE predictions (
            entity_id TEXT NOT NULL,
            scoring_date TEXT NOT NULL,
            model_name TEXT NOT NULL,
            model_version TEXT NOT NULL,
            probability REAL NOT NULL,
            PRIMARY KEY(entity_id, scoring_date, model_name, model_version)
        )
    """)
    row = ("customer-1", "2026-10-19", "churn", "3", 0.4)
    conn.execute("INSERT INTO predictions VALUES (?, ?, ?, ?, ?)", row)
    conn.execute("""
        INSERT INTO predictions VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(entity_id, scoring_date, model_name, model_version)
        DO UPDATE SET probability=excluded.probability
    """, ("customer-1", "2026-10-19", "churn", "3", 0.45))
    count = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    probability = conn.execute("SELECT probability FROM predictions").fetchone()[0]
    assert count == 1
    assert probability == 0.45
```

Run:

```bash
pytest -q
```

Then run the full lifecycle manually. Keep test output and registry version numbers as project evidence; do not paste fake outputs into your report.

### 12.6 Integration checklist

- [ ] `mlflow server` starts and persists tracking metadata.
- [ ] A training run logs parameters, metrics, tags, and model artifact.
- [ ] The registered model has a version, signature, and input example.
- [ ] `challenger` points to the candidate version after gate execution.
- [ ] A failed gate leaves `champion` unchanged.
- [ ] A successful, approved gate can move `champion`.
- [ ] Batch job resolves the alias once and logs the immutable version.
- [ ] Batch retries do not duplicate the logical scoring key.
- [ ] Online endpoint validates the request and returns schema-valid output.
- [ ] Online logs include request ID, model version, feature timestamp, and latency.
- [ ] Shadow output is logged but does not control the authoritative response.
- [ ] Rollback moves the deployment reference and the running service is verified.
- [ ] Load-test percentiles and cost calculations are based on actual observations.
- [ ] Privacy, access, retention, and approval requirements are documented.

### 12.7 From local lab to production

Replace each local component deliberately:

| Local lab | Production concern |
|---|---|
| SQLite MLflow backend | Supported managed or database-backed registry with backups and permissions |
| Local artifact directory | Durable object store with encryption, lifecycle policy, and restricted access |
| Synthetic dataset | Versioned, validated production dataset with lineage and approved use |
| SQLite feature store | Redis/managed online store/feature platform with freshness and consistency controls |
| SQLite prediction table | Warehouse/lakehouse table with transaction/upsert strategy and retention policy |
| Local JSONL log | Structured telemetry pipeline with access control, redaction, durability, and alerting |
| Local `uvicorn` process | Containerized deployment, orchestrator, health probes, autoscaling, secrets, and network policy |
| Manual shell promotion | CI/CD workflow with test evidence, approval record, audit, and controlled rollout |

---

## 13. Troubleshooting and common mistakes

| Symptom | Likely cause | Investigation and fix |
|---|---|---|
| Model registration fails | Registry backend or permissions unsupported/misconfigured | Verify MLflow version, tracking URI, registry URI, server logs, and required privileges |
| Alias operation fails | Backend/version does not support aliases or model/version missing | Check selected registry docs and client API; do not silently assume legacy stages are equivalent |
| `models:/churn@champion` cannot load | Alias absent, version not ready, artifact access failure | Inspect registered model/version, alias assignment, readiness, and artifact permissions |
| Model loads in notebook but not service | Environment mismatch or missing dependency/code artifact | Test the packaged model in a clean environment/container with pinned requirements |
| Signature mismatch | Input columns, types, order, or output shape changed | Compare API schema, signature, input example, and feature pipeline contract |
| Batch rows have different versions | Alias resolved repeatedly or workers used different configuration | Resolve once per run and pass immutable version to all partitions |
| Batch retry duplicates rows | No unique scoring key or non-idempotent write | Define logical key, use supported merge/upsert/transaction semantics, and test retries |
| Scores change unexpectedly | Data snapshot, feature definition, model version, or threshold changed | Compare input lineage, model version, environment, feature timestamp, and configuration |
| Online endpoint is slow | Feature-store latency, queueing, cold start, serialization, or logging | Instrument each stage and inspect p95/p99 under realistic load |
| Feature lookup returns stale data | Materialization lag, bad TTL, delayed event, or clock issue | Monitor event/materialization timestamps and enforce feature-specific freshness rules |
| Shadow traffic affects users | Challenger path has side effects or output is used downstream | Isolate shadow path and make its output non-authoritative by construction |
| Rollback did not restore behavior | Running process still has new model loaded or schema incompatible | Verify loaded version and endpoint revision; reload/redeploy and check feature compatibility |
| A/B result is uninterpretable | Assignment not stable or model versions changed mid-experiment | Log assignment, exposure, model version, and experiment configuration |
| High availability but low quality | Only service metrics monitored | Join delayed labels, track business outcomes and slice-level quality |
| Logs expose sensitive data | Raw inputs or identifiers logged without a policy | Minimize, redact/tokenize, restrict access, and apply retention controls |
| Load-test report claims unsupported results | No raw output or environment context | Re-run, preserve raw measurements, specify setup and sample size; never fabricate percentiles |

### Common anti-patterns to avoid

1. Deploying straight from a notebook without a registered immutable artifact.
2. Treating a mutable alias as the version identity in historical prediction rows.
3. Moving `champion` and assuming running processes reload automatically.
4. Promoting on one aggregate metric without slice or operational gates.
5. Using online inference for a workload that only needs daily results.
6. Using the latest feature values for a historical batch score without checking time semantics.
7. Logging raw personal data to debug an issue when a version reference or feature hash would suffice.
8. Calling a prediction “reproducible” without retaining model, data, feature, code, and environment lineage.
9. Using average latency as the only service metric.
10. Treating rollback as an alias update without verifying the runtime and downstream side effects.

---

## 14. Practice questions and exercises

### 14.1 Concept checks

1. What is the difference between a model artifact, a registered model, a model version, an alias, and a deployment?
2. Why is a model version a stronger audit reference than an alias?
3. Which lifecycle stages are logical concepts and which may be vendor-specific states?
4. What does an MLflow model signature validate, and what semantic rules remain the application's responsibility?
5. Why should a batch job resolve an alias once rather than in each partition?
6. Why does changing an alias not guarantee an online process changes its loaded model?
7. When is batch inference preferable to online inference?
8. What new failure modes appear when inference depends on an online feature store?
9. What is the difference between shadow deployment and A/B testing?
10. Which prediction fields are necessary to join delayed outcomes and investigate an incident?
11. Why can a model service be operationally healthy but produce poor business results?
12. Why should logs minimize raw input data?

### 14.2 Architecture exercises

**Exercise A — Fraud scoring at 50 ms**

Draw the request path and allocate a latency budget to network, authentication, feature lookup, model, logging, and response. Identify the p99 target, fallback policy, and one failure mode per component. Explain which features should be precomputed.

**Exercise B — Daily churn emails**

Design a batch scoring table and idempotent email delivery flow. Specify scoring keys, model version columns, watermark behavior, retry policy, late-arriving data behavior, and how to prevent duplicate emails.

**Exercise C — Hourly recommendations**

Design an hourly candidate-generation job with an online retrieval or reranking stage. Explain what is precomputed, what is request-time, how freshness is measured, and how you would compare recommendations with a baseline.

**Exercise D — Promotion gate**

Define a gate with aggregate metric thresholds, slice-level constraints, fairness review, schema compatibility, dependency scan, load test, and approval record. Explain which checks are automatic and which require human approval.

**Exercise E — Rollback drill**

Deploy version N+1 to a staging or canary environment, trigger a simulated failure, restore version N, and prove which version each request used. Include logs and the time taken to restore service. Do not claim the drill succeeded until you have observed the evidence.

### 14.3 Implementation extensions

1. Replace the SQLite feature store with Redis while keeping the same `get_features()` contract.
2. Replace the SQLite prediction table with a warehouse/lakehouse table and define the upsert transaction boundary.
3. Store a durable batch run manifest with source watermark, model version, code SHA, input/output counts, and status.
4. Add golden-input tests that compare batch and online predictions within a justified tolerance.
5. Add slice metrics to the promotion gate and fail on an intentionally regressed slice.
6. Implement a canary percentage with stable entity hashing and a kill switch.
7. Add a `/metrics` endpoint or metrics exporter and define alert thresholds.
8. Write a model card for the synthetic model, explicitly noting that its performance is not validated for real use.
9. Add artifact checksum verification and container image digest to the deployment record.
10. Document retirement: identify consumers, stop traffic, preserve evidence, and confirm no active references remain.

### 14.4 Checkpoint

You are ready to move to Topic 05 when you can demonstrate that you can:

- [ ] Register, version, and promote models with gates.
- [ ] Build batch and online inference paths.
- [ ] Choose among batch, online, and streaming inference and justify the trade-off.
- [ ] Log predictions and deploy with rollback.
- [ ] Explain how prediction logs and delayed outcomes feed drift monitoring.
- [ ] Reconstruct the model version and feature state behind a historical prediction.
- [ ] Distinguish a local learning lab from production infrastructure.

---

## 15. Completion checklist matching Topic 04

### Model registry and lifecycle

- [ ] Explain training → evaluation → registration → staging → deployment → monitoring → retirement.
- [ ] Distinguish versions, aliases, stages, tags, endpoints, and approval records.
- [ ] Register a model in MLflow with signature and metadata.
- [ ] Explain Unity Catalog models and the awareness-level registry concepts in SageMaker, Vertex AI, and Azure ML.
- [ ] Explain alias behavior and registry-backend differences without assuming universal stage support.
- [ ] Record lineage from model to run, dataset, feature definitions, code, and environment.
- [ ] Define access controls, audit trails, and retirement procedure.

### Packaging and validation

- [ ] Use MLflow `pyfunc` or a native flavor with a consistent loading interface.
- [ ] Attach a model signature and valid input example.
- [ ] Pin dependencies and describe container/environment reproducibility.
- [ ] Test artifact load, schema compatibility, output validity, and golden inputs before promotion.

### Batch inference

- [ ] Score a bounded set of records using an immutable model version.
- [ ] Record model version, scoring timestamp, identifiers, and run metadata.
- [ ] Make retries idempotent and define a recovery/backfill strategy.
- [ ] Write predictions to a table and validate counts, keys, and outputs.
- [ ] Monitor completion time, lag, failures, retries, and output quality.

### Online inference and decision patterns

- [ ] Build a validated request/response endpoint using FastAPI and explain BentoML, KServe, SageMaker, Vertex AI, and Azure ML endpoint options.
- [ ] Fetch features from Redis or a documented local substitute.
- [ ] Enforce feature freshness and request/output schema rules.
- [ ] Measure end-to-end latency and report p50/p95/p99 from actual tests.
- [ ] Compare batch, online, streaming, and precompute-and-serve hybrids.
- [ ] Justify the 50 ms fraud, daily churn, and hourly recommendation architectures.

### Deployment, monitoring, and rollback

- [ ] Demonstrate champion/challenger and shadow prediction isolation.
- [ ] Explain canary, blue/green, and A/B strategies and their trade-offs.
- [ ] Use aggregate, slice, fairness, compatibility, and operational gates as appropriate.
- [ ] Roll back to a known-good version and verify the runtime actually loaded it.
- [ ] Record request/prediction ID, version, timestamp, output, latency/error, and approved lineage references; join delayed outcomes/labels by stable keys and label-availability time.
- [ ] Define cost per million predictions and a reproducible load-test procedure.
- [ ] Document SLOs, model card, permissions, auditability, and retirement.
- [ ] Explain the awareness-level relationship between model/prompt versioning and later foundation-model topics.

---

## 16. Authoritative documentation references

Documentation and API behavior evolve. Check the documentation for the exact installed version and the registry backend you use before applying examples to production.

### MLflow

- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry/) — registered models, versions, aliases, and registry concepts.
- [Model Registry Workflows](https://mlflow.org/docs/latest/ml/model-registry/workflow/) — registering models, aliases, and loading a version by alias.
- [MLflow `pyfunc` API reference](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.pyfunc.html) — logging/loading Python function models and dependency options.
- [Model signatures and input examples](https://mlflow.org/docs/latest/ml/model/signatures/) — input/output schemas and serving-compatible examples.
- [MLflow Tracking API](https://mlflow.org/docs/latest/tracking.html) — experiments, runs, metrics, parameters, and artifacts.

### Serving and API contracts

- [FastAPI request bodies](https://fastapi.tiangolo.com/tutorial/body/) — Pydantic request validation.
- [FastAPI response models](https://fastapi.tiangolo.com/tutorial/response-model/) — response validation and serialization.
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/) — schema and validation behavior.

### Platform awareness

- [Databricks Unity Catalog models](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/index.html) — governed model lifecycle in Databricks; verify workspace and UC-specific requirements.
- [Amazon SageMaker Model Registry](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html) — model package groups, versions, approval, and deployment workflow.
- [Vertex AI Model Registry](https://cloud.google.com/vertex-ai/docs/model-registry/introduction) — model resources, versions, and registry concepts.
- [Azure Machine Learning model management](https://learn.microsoft.com/en-us/azure/machine-learning/concept-model-management-and-deployment?view=azureml-api-2) — model assets and deployment lifecycle.

---

## Final engineering principle

A production model is not just a serialized estimator. It is a versioned artifact with data and code lineage, a documented input/output contract, an approved deployment reference, an observable inference path, and a tested rollback plan. Choose batch, online, streaming, or hybrid from the actual freshness and latency requirement. Make the exact model version visible in every important prediction record, and never confuse a registry pointer with proof of what a running service actually used.
