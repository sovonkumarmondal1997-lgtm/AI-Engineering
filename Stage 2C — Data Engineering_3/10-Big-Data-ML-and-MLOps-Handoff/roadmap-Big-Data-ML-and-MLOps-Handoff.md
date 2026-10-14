# Roadmap — Module 2C.10: Big Data ML and MLOps Handoff

This is the learning roadmap for the tenth and final module of Stage 2C,
**Data Engineering_3**. It tells you **what** to learn about the handoff
from data engineering to machine learning, **in what order**, **how** to
learn each topic, and **how to prove to yourself** that you have learned it
before you move on.

Everything in Stages 2 and 2B and Modules 2C.1–2C.9 prepares data. At some
point, a machine learning model must learn from that data and then serve
predictions on new data. The seam between the two is where most ML
projects fail: features computed one way in training and another way in
production (**training–serving skew**), datasets nobody can reproduce,
models without lineage, and silent decay when the world changes (**drift**).

A data engineer does not usually research new model architectures. A data
engineer **builds the data foundations of ML**: scalable feature pipelines,
point-in-time-correct training sets, dataset versioning, model registries,
batch and online inference plumbing, and drift monitoring. These are
increasingly the highest-leverage skills on any ML team, and they lead
directly into Stages 5–8 and 13–14 of this roadmap.

This module is deliberately about the **data side** of ML. Model theory
(optimisation, loss functions, architectures) is covered in Stages 4–6.

---

## 1. Module outcome

By the end of this module you will be able to:

- Train and score models on large data with **Spark MLlib** pipelines, and
  know when distributed training is (and is not) needed.
- Build **feature pipelines at scale**: batch, streaming, and on-demand,
  with a **feature store** and **point-in-time correct** joins.
- Create **reproducible training datasets** with dataset versioning and
  lineage (Delta/Iceberg time travel, DVC, lakeFS).
- Use a **model registry** (MLflow, Unity Catalog) to version, stage, and
  promote models.
- Design **batch inference** and **online inference** paths and choose
  between them.
- Monitor **data drift, concept drift, and prediction quality**, and
  trigger retraining safely.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Python, packaging, testing | Stage 1 | All ML code |
| pandas, NumPy, Polars, DuckDB | Stage 2 — Modules 2.2–2.4 | Feature computation |
| SQL and window functions | Stage 2 — Module 2.6 | Point-in-time joins, aggregates |
| Spark and PySpark | Stage 2 — Module 2.14 | MLlib, distributed features |
| Lakehouse formats and time travel | Stage 2 — Module 2.15 | Dataset versioning |
| Streaming | Stage 2 — Module 2.16 | Real-time features |
| Orchestration | Stage 2 — Module 2.13 | Training and scoring pipelines |
| Data quality and contracts | Stage 2 — Module 2.11 | Feature and training-data validation |
| FastAPI data services, feature stores overview | Stage 2 — Module 2.22 | Serving; this module goes deeper |
| Databricks and MLflow introduction | Stage 2B — Module 2B.4 Topic 14 | Registry and tracking basics |
| Sketches, time series, experiments | Module 2C.9 | Evaluation and drift statistics |
| Data products and SLAs | Module 2C.8 | Features and models as products |
| Redis, OLAP serving | Modules 2C.1, 2C.7 | Online feature stores and serving |
| Basic ML concepts (supervised learning, train/test split) | Introduced here; deepened in Stage 5 | You need a working vocabulary |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add pyspark scikit-learn pandas
  polars mlflow feast evidently great-expectations dvc fastapi uvicorn
  redis pytest`.
- Docker Compose with: **MLflow tracking server** (with MinIO artifact
  store and PostgreSQL), **Redis** (online store), **Kafka** (optional,
  streaming features), and a **local Spark** setup.
- A sample dataset suitable for a prediction task with timestamps (e.g.,
  churn or fraud with transactions), generated with built-in drift.

**A note on scope:** you will use simple models (logistic regression,
gradient boosting). The goal is the **pipeline around the model**, not the
model's cleverness.

---

## 3. How the module is organised

The five topics are grouped into three phases. Work through them **in
order**.

```text
Phase A — Data for ML at Scale                       (Intermediate)
  01 Distributed ML with Spark MLlib
  02 Feature engineering at scale

Phase B — Reproducibility and Lifecycle              (Intermediate → Advanced)
  03 Training data pipelines and dataset versioning
  04 Model registry and batch vs online inference

Phase C — Staying Healthy in Production              (Advanced)
  05 Data drift monitoring for ML pipelines

Consolidate
  Module mini-project: an end-to-end ML data pipeline
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05
train  feed  repro- ship   keep it
at     it    duce  & use   healthy
scale  good  it    it
       data
```

Why this order:

- MLlib (01) shows what training at scale needs from data; features (02)
  are what the model consumes.
- Training sets and versions (03) make results reproducible.
- The registry and inference paths (04) put models into use.
- Drift monitoring (05) closes the loop and triggers retraining.

---

## 4. Suggested schedule

About **4 weeks at 8 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — Spark MLlib · Topic 02 — feature engineering (batch) |
| 2 | Topic 02 — feature stores and streaming features · Topic 03 — training data and versioning |
| 3 | Topic 04 — registry and inference |
| 4 | Topic 05 — drift monitoring · mini-project |

---

## 5. How to study every topic (the ML pipeline loop)

```text
Read → Define the prediction task and the "as of" time → Build the data
path → Train → Check for leakage and skew → Version everything → Serve
→ Monitor → Break it (drift, late data) → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Define the prediction task and the "as of" time**: what is predicted,
   for whom, when, with what information available *at that moment*.
3. **Build the data path** from raw tables to features to training set.
4. **Train** a simple baseline model.
5. **Check for leakage and skew**: does any feature use future
   information? Is it computed identically in training and serving?
6. **Version everything**: data snapshot, feature definitions, code,
   parameters, and model.
7. **Serve** the model in batch and online form.
8. **Monitor** inputs, outputs, and quality over time.
9. **Break it**: inject drift, late data, and a schema change; observe the
   alarms.
10. **Write it down** in `module-2c10-notes.md`.
11. **Explain aloud** how a prediction could be reproduced six months
    later.

Keep one `ml_data_lab/` project:

```text
ml_data_lab/
├── docker-compose.yml     # MLflow + MinIO + Postgres, Redis, (Kafka), Spark
├── data/                  # generators with controlled drift and leakage traps
├── features/              # feature definitions (Feast repo or equivalent)
├── pipelines/             # Spark/Polars feature and training jobs
├── training/              # training scripts, MLflow tracking
├── serving/               # batch scoring job and FastAPI online service
├── monitoring/            # drift reports and alerts
├── dags/                  # orchestration for retraining and scoring
└── tests/                 # point-in-time, skew, and reproducibility tests
```

---

## 6. Phase A — Data for ML at Scale (Intermediate)

### Topic 01 — [Distributed ML with Spark MLlib](01-distributed-ml-with-spark-mllib.md)

**Why it comes first:** many organisations already hold their data in
Spark. MLlib lets you train and score on that data without moving it — and
teaches how ML pipelines are structured as data workflows.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The ML workflow in plain words: data → features → train → evaluate → predict; supervised (classification/regression) vs unsupervised (clustering) |
| Basics | Train/validation/test splits; overfitting; why **time-based** splits are needed for temporal data |
| Basics | When distributed training is needed (data too big for one machine) and when it is not (most tabular problems fit on one big machine; sample or use XGBoost/LightGBM single-node) |
| Intermediate | **Spark MLlib DataFrame API**: `Transformer`, `Estimator`, `Pipeline`, `PipelineModel` |
| Intermediate | Feature transformers: `StringIndexer`, `OneHotEncoder`, `VectorAssembler`, `StandardScaler`, `Imputer`, `Bucketizer`, `Tokenizer`/`HashingTF`/`IDF` |
| Intermediate | Algorithms: `LogisticRegression`, `LinearRegression`, `RandomForest`, `GBTClassifier`, `KMeans`, ALS recommendations |
| Intermediate | Evaluation: `BinaryClassificationEvaluator`, `MulticlassClassificationEvaluator`; AUC, precision/recall, RMSE; cross-validation and `ParamGridBuilder` |
| Intermediate | Saving and loading pipelines; applying a `PipelineModel` for batch scoring |
| Advanced | Distributed alternatives: XGBoost/LightGBM on Spark (`xgboost.spark`, SynapseML), Dask-ML, Ray Train — awareness and when each fits (links to Module 2.21) |
| Advanced | Performance: partitioning for training, caching, data skew in features, and the cost of shuffles in iterative algorithms |
| Advanced | Deep learning on big data: Spark with TorchDistributor, Horovod, Petastorm/Mosaic Streaming for loading Parquet into training loops — awareness (links to Stages 6 and 13) |
| Advanced | Beyond MLlib: scikit-learn pipelines, pandas UDFs / `applyInPandas` for per-group models, and many-models-at-scale patterns |
| Advanced | Honest evaluation: baselines, calibration, class imbalance, and metrics that match business cost |

**How to learn it**

1. Read the topic file.
2. Write a one-paragraph description of a churn prediction task: label,
   entity, prediction time, features available at that time.
3. Draw the MLlib `Pipeline` stages for it.

**Hands-on exercise — `experiments/01_mllib/`**

1. Build a Spark `Pipeline` (indexing, encoding, assembling, a GBT
   classifier) on 20M rows with a time-based split.
2. Tune with cross-validation on a grid; record metrics.
3. Save the `PipelineModel`; reload it in a fresh session and score a new
   batch.
4. Train the same problem with LightGBM on a single machine using a sample
   and on the full data; compare quality, time, and cost.
5. Use `applyInPandas` to train one small model per region.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain the ML workflow and a time-based split.
- [ ] Build, tune, save, and reload an MLlib pipeline.
- [ ] Decide whether distributed training is needed.
- [ ] Evaluate with metrics that fit the problem.

**Common mistakes:** random splits on temporal data; fitting scalers or
encoders on the full dataset before splitting; distributing a problem that
fits on one machine; judging by accuracy on imbalanced classes.

---

### Topic 02 — [Feature engineering at scale](02-feature-engineering-at-scale.md)

**Why here:** features are the largest lever on model quality and the
biggest source of production bugs. Data engineers own their correctness,
freshness, and reuse.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What a feature is: a measurable input about an **entity** (user, account, device, product) at a point in time |
| Basics | Common transformations: scaling, encoding categoricals, bucketing, log transforms, date parts, text and count features |
| Basics | Aggregation features: counts, sums, averages over windows (last 7/30/90 days), recency/frequency/monetary (RFM) |
| Intermediate | **Point-in-time correctness**: for each training row with label time *t*, features must use only data available at *t*; leakage and how it hides |
| Intermediate | **As-of joins** (`ASOF JOIN` in DuckDB/Polars/Snowflake; `merge_asof` in pandas; window-based patterns in Spark SQL) |
| Intermediate | **Training–serving skew**: the same logic must run in training and serving; sharing code or a single definition; testing for skew |
| Intermediate | **Feature stores**: purpose (reuse, consistency, discovery, governance), offline vs online stores, entities, feature views, materialisation; **Feast**, Databricks Feature Engineering, SageMaker/Vertex/Snowflake feature stores |
| Intermediate | Batch features computed in Spark/dbt/SQL and written to the offline store; materialising the latest values into an online store (Redis, DynamoDB — Module 2C.1) |
| Advanced | **Streaming features**: windowed aggregates computed from Kafka with Flink/Spark Structured Streaming (Module 2.16) written to the online store; event-time correctness and late data |
| Advanced | **On-demand features** computed at request time from the request and fetched features; latency budgets |
| Advanced | Feature freshness SLOs, backfills of new features over history, and cost control (Module 2C.8 data products) |
| Advanced | Feature validation and quality: null rates, range checks, distribution checks at write time (Module 2.11); contract tests |
| Advanced | Embeddings as features, vector stores, and feature pipelines for LLM/RAG systems (links to Module 2.22 Topic 05 and Stages 8–9) |
| Advanced | Governance: PII in features, lineage from source to feature to model, ownership and deprecation |

**How to learn it**

1. Read the topic file.
2. For churn, list 15 candidate features and mark which are leaky (for
   example "days since cancellation").
3. Draw offline and online paths for the same feature, and where skew
   could creep in.

**Hands-on exercise — `experiments/02_features/`**

1. Compute 30-day rolling aggregates per customer for every label date
   using an as-of/window approach; verify there is no future information.
2. Deliberately add a leaky feature, show the inflated offline AUC, and
   show the collapse in a time-split evaluation.
3. Create a Feast (or equivalent) repo with entities and feature views;
   materialise to Redis; fetch features online and offline.
4. Write a **skew test**: for 1,000 entities compare online-fetched values
   with offline recomputed values at the same timestamp.
5. Add a streaming feature (rolling 10-minute event count) from Kafka to
   the online store; measure freshness.
6. Add feature validation (nulls, ranges, drift) as a pipeline gate.

**Checkpoint:**

- [ ] Build point-in-time-correct features.
- [ ] Detect leakage and training–serving skew.
- [ ] Explain offline and online stores and materialisation.
- [ ] Add streaming and on-demand features appropriately.
- [ ] Validate features automatically.

**Common mistakes:** joining on the latest feature value instead of the
value as of label time; separate code for training and serving; features
with no owner or documentation; backfilling without respecting time.

---

## 7. Phase B — Reproducibility and Lifecycle (Intermediate → Advanced)

### Topic 03 — [Training data pipelines and dataset versioning](03-training-data-pipelines-and-dataset-versioning.md)

**Why here:** "Which exact data was this model trained on?" must be
answerable months later — for debugging, audits, and trust.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why reproducibility matters in ML: debugging, comparing experiments, audits, regulations, and rollback |
| Basics | The elements to version: **data**, **features**, **code**, **configuration/parameters**, **environment**, and **model artifacts** |
| Basics | Building a training set: entity table (labels with timestamps) joined with features as of those timestamps; splits assigned deterministically |
| Intermediate | **Dataset versioning options**: table snapshots/time travel (Delta `VERSION AS OF`, Iceberg snapshot IDs — Module 2.15), immutable dated Parquet snapshots, **DVC**, **lakeFS** (git-like branches for data), and dataset registries in MLflow |
| Intermediate | **Experiment tracking** with **MLflow**: runs, parameters, metrics, artifacts, tags, and logging dataset references/hashes |
| Intermediate | Deterministic splits: hashing entity ids so the same entity always lands in the same split; avoiding leakage between train and test (same user, same session, near-duplicates) |
| Intermediate | Label quality: label delay, label leakage, noisy or censored labels, and negative sampling |
| Advanced | Data validation for training sets: schema, distributions, label balance, and comparison with the previous version (Great Expectations, Evidently, TFDV) |
| Advanced | Orchestrating training pipelines: Airflow/Dagster/Databricks Workflows/Kubeflow/SageMaker Pipelines; parametrised and idempotent runs |
| Advanced | Reproducing a past model end to end: re-run with pinned data version + code commit + environment (Docker/uv lock) and compare metrics |
| Advanced | Handling class imbalance and sampling in pipelines without breaking evaluation; stratified and time-based sampling |
| Advanced | Governance: lineage from model to data to source, consent and retention for training data, and deleting a user's data across datasets and models (links to Module 2.20 Topic 09) |
| Advanced | Data-centric workflows: error analysis, dataset slicing, and curated evaluation sets |

**How to learn it**

1. Read the topic file.
2. List what you would need to reproduce last quarter's fraud model
   exactly.
3. Decide for each item where it is stored and how it is identified.

**Hands-on exercise — `experiments/03_training_data/`**

1. Build a training-set job that outputs an immutable, versioned table
   (Delta/Iceberg snapshot id recorded) from labels and as-of features.
2. Log to MLflow: data version, git commit, parameters, metrics, and the
   model; tag the dataset hash.
3. Re-run the job at a later date with the pinned version and prove the
   dataset is byte-identical (hash comparison) and the metrics match.
4. Use DVC or lakeFS to branch data, change a cleaning rule, and compare
   model quality between branches.
5. Implement hash-based train/validation/test splits and show a user never
   crosses splits.
6. Add training-set validation (distribution comparison with the previous
   version) and fail the pipeline on unexpected shifts.

**Checkpoint:**

- [ ] Build a point-in-time training set and version it.
- [ ] Track experiments with data and code lineage.
- [ ] Reproduce a past training run exactly.
- [ ] Make deterministic, leak-free splits.
- [ ] Validate training sets automatically.

**Common mistakes:** training on "the table as it is today"; tracking
metrics but not data versions; random splits that leak users; no way to
delete a person's data from derived datasets.

---

### Topic 04 — [Model registry and batch vs online inference](04-model-registry-and-batch-vs-online-inference.md)

**Why here:** a trained model is only useful when it is stored,
versioned, promoted, and used — either on schedule over many rows (batch)
or per request in milliseconds (online).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The model lifecycle: train → evaluate → register → stage → deploy → monitor → retire |
| Basics | A **model registry**: versions, stages/aliases (staging, production, champion/challenger), metadata, lineage, and approval workflows |
| Basics | **MLflow Model Registry** and **Unity Catalog models** (Module 2B.4 Topic 14); SageMaker/Vertex/Azure ML registries — awareness |
| Intermediate | Model packaging: the MLflow `pyfunc` flavour, signatures (input/output schema), environments, and containers |
| Intermediate | **Batch inference**: scheduled scoring of tables with Spark/SQL/Python; writing predictions to a table with model version and timestamp; incremental scoring |
| Intermediate | **Online inference**: a FastAPI/BentoML/KServe/SageMaker/Vertex endpoint; fetching features from the online store; latency budgets and caching |
| Intermediate | **Choosing batch vs online vs streaming inference** by freshness need, cost, and complexity; precompute-and-serve hybrids |
| Intermediate | Prediction logging: inputs, outputs, model version, and request id — the raw material for monitoring and retraining |
| Advanced | **Deployment strategies**: shadow, canary, blue/green, A/B (using Module 2C.9 Topic 04), and rollback; champion/challenger evaluation |
| Advanced | Promotion gates in CI/CD: automated evaluation against baselines and slice metrics, bias/fairness checks, and approval records (Module 2.18) |
| Advanced | Scaling online serving: autoscaling, batching requests, model optimisation (ONNX, quantisation) — awareness (links to Stage 13) |
| Advanced | Cost and SLOs for inference; GPU vs CPU decisions; serverless endpoints |
| Advanced | Model governance: documentation (model cards), access control, audit trails, and retirement |
| Advanced | LLM-era note: registries and serving for foundation models, prompt versions, and evaluation harnesses (links to Stages 8, 10, 14) |

**How to learn it**

1. Read the topic file.
2. For fraud scoring (50 ms), churn emails (daily), and recommendations
   (hourly), choose batch, online, or hybrid and justify.
3. Draw the path from `mlflow.log_model` to a production endpoint.

**Hands-on exercise — `experiments/04_registry_inference/`**

1. Register a model in MLflow with a signature; promote it with aliases
   (`challenger` → `champion`) after an automated evaluation gate.
2. Write a batch scoring job that loads `models:/churn@champion`, scores a
   table incrementally, and records the model version in each row.
3. Build a FastAPI online endpoint that fetches features from Redis and
   returns predictions with latency metrics.
4. Run a shadow deployment: send traffic to both models, log both
   predictions, compare.
5. Roll back by moving the alias, with no code redeploy.
6. Load-test the endpoint and write down its latency percentiles and cost
   per million predictions.

**Checkpoint:**

- [ ] Register, version, and promote models with gates.
- [ ] Build batch and online inference paths.
- [ ] Choose among batch, online, and streaming inference.
- [ ] Log predictions and deploy with rollback.

**Common mistakes:** models deployed straight from notebooks; no model
version in prediction tables; online inference where daily batch would do;
no rollback path.

---

## 8. Phase C — Staying Healthy in Production (Advanced)

### Topic 05 — [Data drift monitoring for ML pipelines](05-data-drift-monitoring-for-ml-pipelines.md)

**Why it comes last:** models decay silently because the world changes.
Monitoring turns that silent failure into an alert and a retraining
decision, and ties together quality checks, statistics, and orchestration.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why models degrade: data drift, concept drift, label drift, upstream pipeline changes, seasonality, and feedback loops |
| Basics | What to monitor: input data quality (nulls, ranges, schema), feature distributions, prediction distributions, and business outcomes |
| Basics | Reference vs current windows: training data, recent production, and rolling baselines |
| Intermediate | **Drift statistics**: PSI (population stability index), KS test, chi-square for categoricals, Jensen–Shannon / Wasserstein distance; thresholds and their false-alarm rates (links to Module 2C.9 Topic 03) |
| Intermediate | **Data quality vs drift**: a broken pipeline looks like drift; check quality first |
| Intermediate | **Performance monitoring** when labels arrive late: delayed ground truth joins, proxy metrics, and estimating performance without labels |
| Intermediate | Tools: **Evidently**, whylogs, Great Expectations, NannyML, cloud monitors (SageMaker Model Monitor, Vertex Model Monitoring, Databricks Lakehouse Monitoring) |
| Intermediate | Computing drift at scale: summaries and sketches (Module 2C.9 Topic 02) per window, stored in a monitoring table instead of rescanning raw data |
| Advanced | Slicing: monitoring by segment (region, device, cohort) to catch localised drift; avoiding alert floods with multiple-comparison thinking |
| Advanced | Alerting and response: severity levels, runbooks, ownership, and on-call (Module 2.20 Topic 03) |
| Advanced | **Retraining strategies**: scheduled, drift-triggered, and performance-triggered; automated retraining with human or automated approval gates; challenger evaluation before promotion (Topic 04) |
| Advanced | Closing the loop: logging predictions and outcomes, building labelled datasets from production, and avoiding feedback-loop bias |
| Advanced | Monitoring generative AI systems: input/output quality, toxicity, groundedness, cost, and latency — awareness (links to Stages 10 and 14) |
| Advanced | Governance and audit: retaining monitoring evidence, fairness drift, and model-risk documentation |

**How to learn it**

1. Read the topic file.
2. For a churn model, list five things that could drift and what each
   would look like in the data.
3. Decide which drift signals should page someone and which should only
   create a ticket.

**Hands-on exercise — `experiments/05_drift/`**

1. Generate production data in weekly batches with controlled drift:
   a gradual shift in one feature, a sudden schema/unit change in another,
   and a concept change (label relationship) in a third.
2. Compute PSI, KS, and chi-square per feature per week; store results in
   a monitoring table.
3. Build an Evidently report and an automated check in the pipeline that
   separates data-quality failures from drift.
4. Join delayed labels, compute performance over time, and show the
   lag between drift and visible performance loss.
5. Wire an alert, a runbook, and an automated retraining DAG with a
   challenger-vs-champion gate.
6. Demonstrate a false alarm caused by seasonality, and fix the baseline.

**Checkpoint:**

- [ ] Distinguish data drift, concept drift, and data-quality failure.
- [ ] Compute and interpret drift statistics at scale.
- [ ] Monitor performance with delayed labels.
- [ ] Design alerting and retraining policies.

**Common mistakes:** alerting on every feature at p < 0.05; treating a
pipeline bug as drift; retraining automatically with no evaluation gate;
no stored reference baseline.

---

## 9. Module mini-project — an end-to-end ML data pipeline

**Goal:** take one prediction problem from raw tables to a monitored,
versioned production model, with the data engineering rigor of the earlier
modules.

**Requirements**

1. **Data and labels:** a generator (or real public dataset) for churn or
   fraud with timestamps, delayed labels, and planted drift and leakage
   traps.
2. **Features:** batch features in Spark/dbt and one streaming feature via
   Kafka; a Feast (or equivalent) feature store with offline and online
   stores; a point-in-time test and a training–serving skew test.
3. **Training data:** an immutable, versioned training set (snapshot id +
   hash), deterministic splits, validation gates, and an orchestrated
   training DAG.
4. **Models:** a Spark MLlib or LightGBM model tracked in MLflow with data
   version and git commit; registered with `challenger`/`champion`
   aliases and an automated promotion gate.
5. **Inference:** daily batch scoring writing predictions with model
   version, and a FastAPI online endpoint with Redis features; latency and
   cost measurements.
6. **Monitoring:** quality checks, drift metrics in a monitoring table,
   delayed-label performance tracking, alerts, a runbook, and a
   drift-triggered retraining run.
7. **Reproducibility proof:** re-create a model from three months ago with
   identical data and metrics.
8. **Documentation:** architecture diagram, data lineage from source to
   prediction, model card, and an ADR on batch vs online serving.

**Done when** you can reproduce any past model exactly, planted leakage is
caught by tests, planted drift raises the right alerts, a bad model can be
rolled back by changing one alias, and a reviewer can trace any prediction
to its model, features, and source data.

---

## 10. Module self-assessment — exit criteria

You have completed this module when you can do all of the following
**without notes**:

- [ ] Build and evaluate an MLlib pipeline with time-based splits and
      decide when distribution is needed.
- [ ] Create point-in-time-correct features and detect leakage and
      training–serving skew.
- [ ] Operate a feature store with offline, online, streaming, and
      on-demand features.
- [ ] Build versioned, reproducible training datasets and reproduce a past
      run exactly.
- [ ] Register, promote, and roll back models with gates.
- [ ] Choose and build batch and online inference paths.
- [ ] Monitor data quality, drift, and performance, and trigger retraining
      safely.

---

## 11. Recommended reading and references

- *Designing Machine Learning Systems* — Chip Huyen (the best single book
  for this module).
- *Machine Learning Design Patterns* — Lakshmanan, Robinson, Munn.
- *Feature Store for Machine Learning* and the Feast documentation;
  tecton.ai/feast blog posts on point-in-time correctness.
- MLflow documentation (tracking, registry, models); Evidently and
  NannyML documentation.
- "Hidden Technical Debt in Machine Learning Systems" (Sculley et al.) and
  Google's "Rules of Machine Learning".
- Apache Spark MLlib guide; DVC and lakeFS documentation.

---

## 12. Where this module leads

This module completes **Stage 2C** and the data engineering track.

- **Stage 3 (Data Structures and Algorithms)** and **Stage 4
  (Mathematics for Machine Learning)** deepen the computer science and
  maths behind everything here.
- **Stage 5 (Machine Learning Foundations)** teaches the models whose
  pipelines you now know how to build.
- **Stages 8–9 (LLM Applications, Retrieval and RAG)** reuse feature,
  embedding, and vector-pipeline ideas.
- **Stages 10 and 14 (Evaluation, LLMOps and AI System Design)** extend
  experimentation, registries, deployment, and monitoring to LLM systems.
