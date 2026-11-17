# MLflow and Feature Engineering Handoff

## Databricks Lakehouse Platform Deep Dive — Gap Module G4

**Audience:** Senior Data Engineer / ML Data Platform Engineer  
**Position:** Final technical learning module of G4  
**Primary discipline:** Data Engineering for production ML systems

> **Central principle:** The Data Engineer does not merely hand an ML team a table. The Data Engineer hands over governed, reproducible, temporally correct, observable, versioned, quality-controlled data and features with explicit ownership and operational contracts.

---

# 1. Module Purpose

On a modern lakehouse, Data Engineering and ML are part of the same production system:

```text
Source Data
    ↓
Bronze
    ↓
Silver
    ↓
Gold
    ↓
Feature Engineering
    ↓
Feature Tables
    ↓
Point-in-Time Training Set
    ↓
MLflow Training Run
    ↓
Model
    ↓
Unity Catalog Model Governance
    ↓
Batch / Online Inference
    ↓
Predictions
    ↓
Gold Prediction Tables
```

The Data Engineer's responsibility is to make the data side of that system:

- governed
- reproducible
- point-in-time correct
- well defined
- fresh enough for the use case
- observable
- traceable
- versioned
- owned
- safe to change

This module is therefore **not a machine-learning theory course**. It teaches enough ML concepts to understand the interfaces between data, features, training, models, inference, and production operations.

---

# 2. Learning Progression

The module follows the required progression:

```text
Phase 1  ML + Data Engineering Fundamentals
    ↓
Phase 2  MLflow Basics
    ↓
Phase 3  Unity Catalog Model Governance
    ↓
Phase 4  Feature Engineering
    ↓
Phase 5  Temporal Data and Point-in-Time Correctness
    ↓
Phase 6  Reproducible Training Data
    ↓
Phase 7  Batch Inference
    ↓
Phase 8  Online Serving / AI Search / Drift Awareness
    ↓
Phase 9  ML Handoff Contracts
    ↓
Phase 10 Production Operations
    ↓
Phase 11 Capstone
    ↓
Phase 12 Interview + Architecture Preparation
```

## Build loop

Apply the G4 operating loop specifically to ML handoff:

```text
Read
→ Build feature
→ Govern feature
→ Validate temporal correctness
→ Version data
→ Train model
→ Track with MLflow
→ Register model
→ Run inference
→ Observe predictions
→ Break feature/data contract
→ Recover
→ Document handoff
```

---

# 3. Scope Boundary

## This module teaches

- MLflow experiments, runs, parameters, metrics, artifacts, and models
- Unity Catalog model governance
- model versions and aliases
- feature-table design
- feature ownership and quality
- temporal semantics
- point-in-time correctness
- training-data leakage
- reproducibility
- Delta versioning as applied to ML
- lineage
- batch inference
- prediction tables
- Lakeflow Jobs integration
- online serving awareness
- Databricks AI Search / formerly Vector Search awareness
- data, feature, and prediction drift
- production ML handoff contracts
- operational troubleshooting and runbooks

## This module does not teach

- linear algebra
- calculus
- probability theory
- deep neural-network architecture
- gradient descent theory
- CNN architecture
- transformer architecture
- advanced hyperparameter optimization theory
- complete RAG implementation
- complete model-serving specialization

The required mental model is:

```text
Data
→ Features
→ Training Dataset
→ Model
→ Prediction
→ Production
```

---

# 4. ML Fundamentals for Data Engineers

## 4.1 Feature

A **feature** is a measurable input used by a model.

Example:

```text
customer_id
orders_last_30_days
avg_order_value
days_since_last_order
support_tickets_last_90_days
```

The Data Engineer cares about more than the value:

```text
Feature
+ Definition
+ Grain
+ Timestamp
+ Source
+ Transformation
+ Freshness
+ Owner
+ Version
+ Quality
```

## 4.2 Label

A **label** is the outcome the model is trying to predict.

Example:

```text
churned = 1
```

## 4.3 Training dataset

```text
Features + Label
```

But a production training dataset also needs:

```text
Entity
+ Label timestamp
+ Feature timestamps
+ Dataset version
+ Lineage
+ Quality evidence
```

## 4.4 Prediction

A prediction is the model's output.

For churn:

```text
customer_id
churn_probability
predicted_label
prediction_date
model_version
```

## 4.5 Training versus inference

Training asks:

> What relationship can the model learn from historical information?

Inference asks:

> Given information available now, what should the model predict?

This distinction is the foundation for avoiding training-serving skew and temporal leakage.

---

# 5. ML Data Platform Architecture

A practical architecture is:

```text
                  ┌────────────────────┐
                  │   Source Systems   │
                  └─────────┬──────────┘
                            ↓
                       Bronze / Raw
                            ↓
                       Silver / Clean
                            ↓
                        Gold / Curated
                            ↓
                  ┌─────────┴─────────┐
                  ↓                   ↓
          Feature Engineering    Analytical Gold
                  ↓
       features.customer_daily
                  ↓
       Point-in-Time Training Set
                  ↓
             MLflow Run
       ┌──────────┼──────────┐
       ↓          ↓          ↓
   Params      Metrics    Artifacts
                  ↓
                Model
                  ↓
        Unity Catalog Model
             Governance
                  ↓
        ┌─────────┴─────────┐
        ↓                   ↓
   Batch Inference      Online Serving
        ↓
  gold.churn_scores
```

## Where the Data Engineer fits

The Data Engineer owns or co-owns:

- ingestion dependencies
- curated datasets
- feature pipelines
- feature contracts
- temporal correctness
- data quality
- feature freshness
- lineage
- access controls
- batch inference infrastructure
- prediction storage
- operational monitoring
- change management

Ownership varies by organization, but the interfaces must be explicit.

---

# 6. MLflow Fundamentals

## 6.1 What problem does MLflow solve?

A model without experiment context is difficult to operate.

Suppose an ML Engineer says:

> "Model version 17 is better."

A Data Engineer should be able to ask:

- Which training data?
- Which feature version?
- Which code?
- Which parameters?
- Which metrics?
- Which run?
- Which model artifact?
- Which environment?
- Which source data?
- Which validation evidence?

MLflow provides the experiment/run tracking layer that helps answer these questions.

## 6.2 Experiment

An experiment groups related training runs.

Conceptual structure:

```text
Experiment: churn-model
    ├── Run 001
    ├── Run 002
    ├── Run 003
    └── Run 004
```

A Databricks-style example:

```python
import mlflow

mlflow.set_experiment("/Shared/churn-experiment")
```

**Input:** an experiment path/name.  
**Output:** subsequent runs are associated with that experiment.  
**Production implication:** establish naming and ownership conventions instead of creating unmanaged experiments.

## 6.3 Run

A run represents one tracked execution.

```python
with mlflow.start_run():
    # training work
    ...
```

Think:

```text
One run
=
One tracked training attempt
```

A run can contain:

- run ID
- start/end time
- status
- parameters
- metrics
- artifacts
- model information
- tags
- input/dataset metadata

## 6.4 Parameters

Parameters describe configuration chosen before or during training.

```python
mlflow.log_param("max_depth", 6)
mlflow.log_param("learning_rate", 0.05)
```

Parameters answer:

> What configuration produced this result?

They are useful for run comparison and reproducibility.

## 6.5 Metrics

Metrics quantify an evaluation result.

```python
mlflow.log_metric("accuracy", accuracy)
mlflow.log_metric("roc_auc", roc_auc)
```

Good production tracking ties metrics to a dataset/version and evaluation protocol.

Do not treat a metric as meaningful without knowing:

```text
Metric
+ Dataset
+ Population
+ Evaluation window
+ Model version
```

## 6.6 Artifacts

Artifacts are files or directories associated with a run.

Examples:

- model files
- evaluation reports
- plots
- feature statistics
- configuration
- schema evidence
- confusion matrices
- validation reports

Example:

```python
mlflow.log_artifact("evaluation_report.json")
```

## 6.7 Models

An MLflow Model is a standardized packaging format that can be consumed by downstream tooling.

A production model should be associated with:

```text
Model
+ Signature
+ Input example
+ Dependencies
+ Source run
+ Dataset metadata
+ Version
+ Governance
```

Do not confuse:

```text
model artifact
≠
registered model
≠
deployed model
```

---

# 7. Current MLflow API Guidance

Current MLflow documentation supports tracking APIs such as:

```python
mlflow.log_param(...)
mlflow.log_params(...)
mlflow.log_metric(...)
mlflow.log_metrics(...)
mlflow.log_input(...)
mlflow.log_artifact(...)
```

For model registration, current MLflow documentation supports registering during model logging with a `registered_model_name` argument or registering a logged model afterward. For Unity Catalog workflows, model signatures are important and should be treated as part of the production interface.

Example pattern:

```python
import mlflow
import mlflow.sklearn

with mlflow.start_run():
    model.fit(X_train, y_train)

    mlflow.log_params(params)
    mlflow.log_metrics(metrics)

    mlflow.sklearn.log_model(
        model,
        name="churn_model",
        input_example=X_train.head(3),
        registered_model_name="prod_ml.churn.churn_model",
    )
```

**Important:** exact model flavors, Databricks runtime behavior, permissions, and registration requirements depend on the current workspace and MLflow/Databricks version. Verify the current documentation before production deployment.

---

# 8. Unity Catalog Model Governance

## 8.1 Namespace

A governed model can be organized using the Unity Catalog namespace:

```text
catalog
  ↓
schema
  ↓
registered model
  ↓
model versions
```

Example:

```text
ml_prod.churn.churn_model
```

## 8.2 Model registration

Registration turns a model artifact into a governed model asset.

A registered model can have:

- versions
- aliases
- tags
- descriptions
- permissions
- ownership
- lineage

## 8.3 Model versions

Example:

```text
churn_model
├── v1
├── v2
└── v3
```

Each version should be traceable to:

```text
training dataset
feature version
code version
MLflow run
model artifact
evaluation metrics
```

## 8.4 Model aliases

An alias is a mutable named reference to a model version.

Conceptually:

```text
churn_model
    ├── v12
    ├── v13  ← champion
    └── v14  ← candidate
```

Production code can reference a semantic alias rather than hard-coding a numeric version.

The advantage:

```text
Inference code
     ↓
@champion
     ↓
Current approved model version
```

Promotion can change the alias without rewriting the inference application.

Do not assume older MLflow "stage" workflows are the current preferred Databricks terminology; current MLflow guidance emphasizes model versions and aliases.

## 8.5 Permissions

Model governance should align with table governance:

```text
Data access
+
Feature access
+
Model access
+
Prediction access
```

The same organization that controls sensitive source tables must also control which identities can:

- read training data
- read feature tables
- register models
- update model metadata
- promote aliases
- run inference
- read predictions

## 8.6 Table governance versus model governance

| Asset | Governance question |
|---|---|
| Source table | Who can read or modify source data? |
| Feature table | Who can consume this feature and for what purpose? |
| Training dataset | Who can reproduce or inspect training data? |
| Registered model | Who can read, update, or promote the model? |
| Prediction table | Who can consume model outputs? |

Model governance does not replace data governance.

---

# 9. Feature Engineering in Unity Catalog

## 9.1 What is a feature table?

Use:

```text
features.customer_daily
```

as the primary example.

The roadmap defines:

```text
primary key  = customer_id
timestamp key = as_of_date
```

Example:

```text
customer_id
as_of_date
orders_7d
orders_30d
revenue_30d
avg_order_value_30d
days_since_last_order
support_tickets_30d
```

## 9.2 Feature table versus ordinary Delta table

Physically, a feature table may be represented using Delta storage.

But production feature engineering adds semantics:

```text
Physical storage
+
Feature definition
+
Entity identity
+
Temporal semantics
+
Lineage
+
Quality
+
Freshness
+
Training-set retrieval
+
Serving integration
+
Governance
```

Therefore:

> A feature table can be a Delta table, but a production feature system is more than storage.

## 9.3 Primary key

For:

```text
features.customer_daily
```

the entity key is:

```text
customer_id
```

If the feature table represents one row per customer per day, uniqueness is closer to:

```text
(customer_id, as_of_date)
```

The exact key semantics must be documented.

## 9.4 Timestamp key

The timestamp key establishes the temporal meaning of a feature row.

```text
as_of_date
```

means:

> This row represents the feature state as of this date/time under the documented computation and availability semantics.

Do not treat a timestamp column as a decorative column.

---

# 10. Feature Table Quality

Minimum quality controls:

- entity-key uniqueness
- timestamp validity
- unexpected-null detection
- value-range validation
- completeness
- freshness
- duplicate detection
- schema stability
- upstream availability
- transformation correctness

Duplicate detection:

```sql
SELECT
    customer_id,
    as_of_date,
    COUNT(*) AS row_count
FROM features.customer_daily
GROUP BY customer_id, as_of_date
HAVING COUNT(*) > 1;
```

### Grain

Always state the grain:

```text
One row
=
One customer
at
One feature-as-of date
```

If the grain is ambiguous, every downstream operation becomes risky.

---

# 11. Feature Freshness

Separate:

```text
Event time
    ↓
Feature computation time
    ↓
Feature availability time
    ↓
Consumer retrieval time
```

A valid feature can still be operationally unusable if it arrives late.

Example:

```text
Required freshness: < 24 hours
Actual freshness:   48 hours
```

The value may be correct, but the feature contract is violated.

## Freshness metrics

Track:

```text
max(as_of_date)
current_time - max(available_feature_time)
```

Also track:

- last successful refresh
- row count
- input freshness
- pipeline duration
- failed runs
- late-arriving data
- quality-gate failures

---

# 12. Feature Ownership

Every production feature should have:

```text
Feature owner
Business definition
Technical definition
Source tables
Transformation
Entity key
Timestamp key
Refresh cadence
Freshness SLA
Quality checks
Consumers
Access policy
Escalation path
Deprecation policy
```

A feature without an owner is an operational liability.

---

# 13. Temporal Semantics

This is one of the most important concepts in the module.

Distinguish:

```text
event_time
processing_time
feature_as_of_time
label_time
prediction_time
availability_time
```

Example timeline:

```text
Jan 01        Jan 10        Jan 20        Jan 30
  │             │             │             │
event       feature row     label          future
  │             │             │
  └─────────────┴─────────────┘
       information available
```

A feature can be:

- generated on Jan 20
- based on events through Jan 10
- made available on Jan 21

Those timestamps have different meanings.

### Mental model

```text
Feature value
+
Timestamp
=
Meaning
```

---

# 14. Point-in-Time Correctness

## 14.1 Core rule

For a prediction/label timestamp:

```text
feature_timestamp <= prediction_timestamp
```

The feature must represent information that could have been known at that point.

The critical distinction is:

```text
Current feature value
≠
Feature value known when the label occurred
```

## 14.2 Churn example

Suppose:

```text
Customer churn label:
2026-06-30
```

A feature row from:

```text
2026-07-15
```

is not valid for a training example whose cutoff is June 30.

Even if the July 15 row gives a better predictor, it is future information.

---

# 15. Data Leakage

Leakage occurs when information unavailable at prediction time enters the training example.

Bad:

```text
Label date: June 30

Feature:
orders_last_30_days computed using July data
```

The model can appear unusually accurate because it has been given information from the future.

Production symptom:

```text
Offline metric: excellent
Production performance: poor
```

### Leakage categories

1. future event leakage
2. post-label aggregation leakage
3. target leakage
4. current-snapshot leakage
5. preprocessing leakage
6. population-selection leakage
7. train/test temporal contamination

---

# 16. Incorrect Current-Value Join

This is intentionally wrong:

```sql
SELECT
    l.customer_id,
    l.label_date,
    f.orders_30d,
    l.churned
FROM labels l
JOIN features.customer_daily f
  ON l.customer_id = f.customer_id;
```

Why it fails:

- multiple historical rows can match
- future rows can match
- current feature values can replace historical truth
- row counts can multiply
- the selected feature may not have existed at label time

---

# 17. Point-in-Time Join

Conceptual rule:

```text
Same entity
AND
feature timestamp <= label timestamp
```

Then select the latest valid feature row.

A window pattern:

```sql
SELECT *
FROM (
    SELECT
        l.customer_id,
        l.label_date,
        l.churned,
        f.as_of_date,
        f.orders_30d,
        f.revenue_30d,
        ROW_NUMBER() OVER (
            PARTITION BY l.customer_id, l.label_date
            ORDER BY f.as_of_date DESC
        ) AS rn
    FROM labels l
    JOIN features.customer_daily f
      ON l.customer_id = f.customer_id
     AND f.as_of_date <= l.label_date
) x
WHERE rn = 1;
```

### Explanation

- **Grain:** one output row per customer/label event.
- **Join:** same customer.
- **Temporal filter:** feature row must not be after the label timestamp.
- **Ordering:** newest valid historical feature row first.
- **`ROW_NUMBER()`:** selects one winning historical row.
- **Production implication:** this prevents current/future feature values from entering the training example.

---

# 18. Point-in-Time Training Dataset

The target relationship is:

```text
Labels
+
Historical Features
=
Point-in-Time Training Dataset
```

Example:

```text
customer_id
label_date
churned
orders_7d
orders_30d
revenue_30d
avg_order_value_30d
days_since_last_order
support_tickets_30d
```

The invariant is:

```text
Every feature value
must be valid at the prediction/label cutoff.
```

---

# 19. Manual Leakage Proof

Automated tests are necessary but not sufficient.

For at least five customers:

1. select a customer
2. select a label timestamp
3. inspect feature history
4. identify the latest valid feature row
5. manually recompute the feature
6. compare the expected value with the generated training dataset
7. record evidence
8. document whether leakage exists

Example evidence table:

| Customer | Label date | Selected feature date | Expected | Actual | Leakage |
|---|---|---|---:|---:|---|
| C001 | 2026-06-30 | 2026-06-29 | 4 | 4 | No |
| C014 | 2026-06-30 | 2026-06-30 | 7 | 7 | No |
| C021 | 2026-06-30 | 2026-06-30 | 2 | 2 | No |

This is a powerful audit artifact.

---

# 20. Reproducible Training Data

A reproducible model requires more than:

```text
model.pkl
```

Use:

```text
Model
 ↓
Training Dataset
 ↓
Feature Table Version
 ↓
Delta Version
 ↓
Source Data
```

Track:

- source version
- feature table version
- training dataset identifier
- dataset snapshot
- code version
- environment
- MLflow run
- parameters
- metrics
- artifacts
- model version

The goal is to answer:

> Exactly what data was used to train this model?

---

# 21. Delta Versioning Applied to ML

Example:

```text
features.customer_daily
Delta version 184
```

The training record should be able to say:

```text
Feature table:
features.customer_daily

Version:
184
```

This allows an investigation months later to distinguish:

```text
What the feature table contains today
```

from:

```text
What the feature table contained when the model was trained
```

Do not re-teach Delta internals here. Apply the existing G4 Delta knowledge to reproducibility.

---

# 22. MLflow Dataset Tracking

Current MLflow tracking APIs include `mlflow.log_input()` for dataset information.

Conceptual pattern:

```python
import mlflow

# `dataset` should be constructed using the current MLflow dataset API
# appropriate to the workspace and source.
mlflow.log_input(dataset, context="training")
```

Use the tracked input to connect:

```text
Run
→ Input dataset
→ Feature/data source
→ Model
```

If a workspace uses a different current integration, document the exact environment rather than inventing a custom API.

---

# 23. Lineage

The production lineage graph should conceptually be:

```text
Source Tables
     ↓
Feature Tables
     ↓
Training Dataset
     ↓
MLflow Run
     ↓
Registered Model
     ↓
Inference
     ↓
Prediction Table
```

Lineage helps with:

- debugging
- audits
- governance
- reproducibility
- impact analysis
- incident response
- retirement
- compliance investigations

A model without data lineage is difficult to operate safely.

---

# 24. Training Data Contract

A production training-data contract should contain:

```text
Dataset name
Owner
Purpose
Entity key
Label definition
Feature definitions
Timestamp semantics
Point-in-time rule
Freshness SLA
Quality rules
Schema
Versioning strategy
Lineage
Access permissions
Retention
Change policy
```

The contract must be executable where practical through:

- schema tests
- data-quality tests
- freshness checks
- temporal checks
- CI gates
- pipeline expectations
- monitoring

---

# 25. Batch Inference

The target production flow is:

```text
Gold / Feature Tables
        ↓
Feature Retrieval
        ↓
Registered Model
        ↓
Prediction
        ↓
gold.churn_scores
```

Batch inference is usually appropriate when:

- predictions can be produced on a schedule
- latency requirements are minutes/hours rather than milliseconds
- large populations need scoring
- throughput matters more than per-request latency
- operational simplicity is valuable

---

# 26. Prediction Table Design

Example:

```text
gold.churn_scores

customer_id
prediction_date
churn_probability
predicted_label
model_version
feature_snapshot
batch_id
prediction_generated_at
```

Good prediction records answer:

```text
Who was scored?
When?
Using which model?
Using which feature snapshot?
As part of which batch?
What was the result?
```

---

# 27. Batch Inference Idempotency

Bad pattern:

```text
INSERT predictions
```

on every retry without a deterministic key.

Potential result:

```text
same customer
same date
same batch
multiple prediction rows
```

Better approaches include:

```text
MERGE
```

or:

```text
overwrite a deterministic partition
```

or:

```text
deterministic batch key + uniqueness enforcement
```

Choice depends on table size, partitioning, retry behavior, and downstream requirements.

The invariant is:

```text
Retrying the same logical inference run
must not silently create duplicate business results.
```

---

# 28. Lakeflow Jobs Integration

Do not re-teach Topic 08. Apply it.

```text
Lakeflow Job
    ↓
Feature refresh
    ↓
Quality check
    ↓
Model inference
    ↓
Prediction validation
    ↓
gold.churn_scores
    ↓
Monitoring
```

Production controls:

- schedule
- retries
- timeouts
- failure notifications
- idempotency
- backfill strategy
- dependency management
- service identity
- auditability

---

# 29. Batch Inference Monitoring

Track:

- prediction count
- null prediction rate
- prediction distribution
- model version
- feature freshness
- runtime
- failure rate
- output freshness
- duplicate rate
- batch completion time

Example SLO:

```text
99% of daily scoring runs complete
before 06:00 UTC.
```

---

# 30. Batch vs Online Inference

| Dimension | Batch | Online |
|---|---|---|
| Latency | Seconds to hours | Milliseconds to seconds |
| Throughput | High | Request-oriented |
| Freshness | Scheduled | Near-real-time |
| Cost | Often lower | Often higher |
| Complexity | Lower | Higher |
| Typical use | Daily scoring | Real-time decisions |
| Operational burden | Moderate | High |
| Feature serving | Offline/batch | Online |
| Failure mode | Delayed batch | Per-request outage |

> Do not use an online architecture when batch is sufficient.

---

# 31. Online Feature Serving — Awareness

Online serving exists for workloads requiring low-latency feature retrieval and prediction.

Conceptual architecture:

```text
Offline Feature Table
       ↓
Online Feature Serving
       ↓
Application
       ↓
Model
```

Important concerns:

- synchronization
- freshness
- low latency
- serving consistency
- availability
- backfill behavior
- access control
- cost
- operational complexity

The learner does **not** need to become an expert in every serving product.

The Data Engineer should instead be able to ask:

```text
Does this workload actually require online features?
What is the latency SLO?
What freshness is required?
How will offline and online values stay consistent?
What is the operational cost?
Who owns failures?
```

---

# 32. Training-Serving Skew

Training-serving skew occurs when the feature computation used for training differs from the feature computation used in inference.

Example:

```text
Training:
orders_last_30_days
    ↓
calculated from one transformation

Serving:
orders_last_30_days
    ↓
calculated using a different transformation
```

The feature has the same name but different semantics.

Prevent skew through:

```text
Feature definition
+
Transformation logic
+
Time semantics
+
Data source
+
Version
```

---

# 33. Databricks AI Search / Formerly Vector Search — Awareness

Current Databricks documentation uses **AI Search** terminology for the capability formerly known as Vector Search.

At a high level:

```text
Documents / Source Data
        ↓
Ingestion
        ↓
Chunking / preprocessing
        ↓
Embeddings
        ↓
AI Search Index
        ↓
Similarity Retrieval
        ↓
RAG / Search / Recommendation Application
```

A Data Engineer may own:

- source ingestion
- document normalization
- chunk pipelines
- metadata
- permissions
- refresh
- quality
- lineage
- deletion handling

The Data Engineer does not need to become a complete RAG specialist in this module.

### Governance matters

Retrieval systems should not bypass lakehouse governance.

Ask:

```text
Who can access the source?
Who can access the index?
What metadata is retained?
How are deletions propagated?
How quickly do updates appear?
Can unauthorized content be retrieved?
```

---

# 34. Drift Monitoring

## Data drift

Input distribution changes.

Example:

```text
customer_age
training mean: 36
current mean:  51
```

## Feature drift

A feature distribution changes.

Example:

```text
orders_30d
historical median: 4
current median:    0
```

## Prediction drift

Model output distribution changes.

Example:

```text
Typical churn probability: 8%
Current churn probability: 21%
```

Mental model:

```text
Data
  ↓
Features
  ↓
Model
  ↓
Predictions
```

Monitor each layer.

---

# 35. Drift Investigation

Scenario:

> Churn predictions suddenly increase from 8% to 21%.

Investigation:

```text
1. Check prediction distribution
2. Check feature distributions
3. Check feature freshness
4. Check upstream data
5. Check schema changes
6. Check training/serving logic
7. Check model version
8. Check recent deployments
9. Check population changes
10. Determine root cause
```

The Data Engineer should distinguish:

```text
Data problem
Feature problem
Pipeline problem
Model problem
Population problem
Deployment problem
```

Do not automatically blame the model.

---

# 36. ML Handoff Contract

The handoff contract is a production interface.

## Schema

- column names
- data types
- nullability
- constraints

## Keys

- entity key
- primary key
- timestamp key

## Freshness

- refresh cadence
- SLA
- acceptable delay

## Point-in-time rules

- timestamp semantics
- cutoff logic
- allowed data
- historical availability

## Ownership

- Data Engineering owner
- ML owner
- business owner
- incident escalation

## Quality

- completeness
- uniqueness
- validity
- freshness
- drift
- reconciliation

## Change management

- schema evolution
- deprecation
- backward compatibility
- notification
- version increments

## Security

- Unity Catalog permissions
- PII classification
- access control
- least privilege

---

# 37. Feature Handoff Template

```text
Feature Name:
Business Definition:
Technical Definition:
Owner:
Source Tables:
Transformation:
Entity Key:
Timestamp Key:
Freshness SLA:
Point-in-Time Rule:
Data Quality Rules:
Expected Range:
Nullability:
Version:
Consumers:
Access Policy:
Incident Contact:
Deprecation Policy:
```

### Example

```text
Feature Name:
orders_last_30d

Business Definition:
Number of completed customer orders in the preceding 30-day window.

Technical Definition:
Count of qualifying completed-order events available as of the feature cutoff.

Owner:
Data Platform

Source:
gold.orders

Entity Key:
customer_id

Timestamp Key:
as_of_date

Freshness SLA:
< 24 hours

Quality:
No negative values.
No duplicate customer_id/as_of_date keys.
No null customer_id.

Version:
v1

Consumers:
Churn ML team

Change Policy:
Breaking changes require notification and version increment.
```

---

# 38. Feature Lifecycle

Use:

```text
Proposed
→ Development
→ Validated
→ Published
→ Adopted
→ Monitored
→ Deprecated
→ Retired
```

A feature should not be retired silently.

Before retirement:

```text
Identify consumers
→ notify owners
→ define migration path
→ provide overlap period
→ monitor migration
→ remove dependency
→ retire
```

---

# 39. Feature Reuse

Centralized feature engineering can reduce:

- duplicated transformations
- inconsistent definitions
- training-serving skew
- maintenance
- governance problems

But centralization introduces trade-offs:

- platform complexity
- ownership complexity
- stale-feature risk
- feature proliferation
- coupling
- difficult deprecation

The correct design depends on organizational scale and reuse value.

---

# 40. Feature Engineering Design Patterns

## Pattern 1 — Daily customer features

```text
customer_id
as_of_date
orders_30d
revenue_30d
```

Good for scheduled batch models.

## Pattern 2 — Rolling-window features

```text
orders_7d
orders_30d
orders_90d
```

Useful when recency matters.

## Pattern 3 — Aggregated transaction features

```text
avg_order_value
max_order_value
transaction_count
```

## Pattern 4 — Time-aware features

```text
days_since_last_order
hours_since_last_login
```

## Pattern 5 — Slowly changing features

Useful where business attributes change over time and historical correctness matters.

## Pattern 6 — Snapshot features

Useful where an entire population is scored at a known cutoff.

---

# 41. Feature Store vs Delta Table

A Delta-backed feature table may physically be stored as a Delta table.

The difference is the management layer:

```text
Delta storage
+
Feature metadata
+
Feature definitions
+
Temporal semantics
+
Point-in-time retrieval
+
Training-set construction
+
Serving integration
+
Governance
```

Think:

```text
Physical storage
vs
Feature-management capabilities
```

Do not assume every Delta table is automatically a governed feature.

---

# 42. Training Data Contract Example

```text
Dataset:
churn_training_v1

Owner:
ML Data Platform

Purpose:
Train customer churn model.

Entity:
customer_id

Label:
churned

Label timestamp:
label_date

Features:
orders_7d
orders_30d
revenue_30d
avg_order_value_30d
days_since_last_order
support_tickets_30d

Point-in-time rule:
feature.as_of_date <= label_date

Freshness:
Feature table refreshed daily.

Quality:
No duplicate entity/time keys.
No unexpected null entity keys.
Range checks enabled.

Versioning:
Feature table version and training dataset identifier recorded.

Lineage:
Source → feature → training dataset → MLflow run → model.

Change policy:
Breaking changes require a new contract version.
```

---

# 43. Data Engineer vs ML Engineer Responsibilities

| Responsibility | Data Engineer | ML Engineer | Shared |
|---|---:|---:|---:|
| Source ingestion | Primary |  |  |
| Feature pipelines | Primary | Contribute | Yes |
| Feature quality | Primary | Validate | Yes |
| Model training |  | Primary | Yes |
| Experiment tracking |  | Primary | Yes |
| Model governance | Primary | Primary | Yes |
| Inference pipeline | Primary | Primary | Yes |
| Drift monitoring | Primary data signals | Primary model signals | Yes |
| Feature definitions | Primary implementation | Primary usage | Yes |
| Data contract | Primary | Consumer | Yes |
| Incident response | Primary for data | Primary for model | Yes |

Actual ownership varies by organization. What matters is that every production interface has an explicit owner.

---

# 44. ML Handoff Failure Modes

## Failure 1 — Feature schema changes unexpectedly

```text
Symptom
→ ML job fails

Root cause
→ breaking column/type change

Evidence
→ schema diff

Fix
→ restore compatible schema or publish a new version

Prevention
→ schema contract + change gate
```

## Failure 2 — Freshness SLA violated

```text
Symptom
→ predictions use stale features

Root cause
→ upstream or feature pipeline delay

Evidence
→ freshness metric

Fix
→ recover upstream pipeline and recompute

Prevention
→ freshness SLO + alert
```

## Failure 3 — Future data enters training

```text
Symptom
→ suspiciously high AUC

Root cause
→ temporal leakage

Evidence
→ feature timestamp > label timestamp

Fix
→ rebuild training set

Prevention
→ temporal validation + manual leakage proof
```

## Failure 4 — Feature logic changes without notification

```text
Symptom
→ model behavior changes

Root cause
→ undocumented transformation change

Evidence
→ feature version/code diff

Fix
→ restore or publish a compatible version

Prevention
→ feature lifecycle + change management
```

## Failure 5 — Model trained on unversioned data

```text
Symptom
→ six-month-old model cannot be reproduced

Root cause
→ no dataset/feature version

Evidence
→ missing input metadata

Fix
→ recover from available snapshots if possible

Prevention
→ mandatory input tracking
```

## Failure 6 — Duplicate predictions

```text
Symptom
→ multiple rows per customer/date

Root cause
→ non-idempotent retry

Evidence
→ duplicate-key query

Fix
→ deduplicate and correct batch

Prevention
→ deterministic batch key + MERGE/partition strategy
```

## Failure 7 — Online value differs from offline value

```text
Symptom
→ training metrics do not translate to production

Root cause
→ training-serving skew

Evidence
→ offline/online comparison

Fix
→ unify feature definition or transformation

Prevention
→ shared feature definitions + reconciliation
```

## Failure 8 — Model version unclear

```text
Symptom
→ nobody knows what produced predictions

Root cause
→ missing model metadata

Fix
→ include model version/alias in prediction records

Prevention
→ prediction contract
```

## Failure 9 — Feature owner unknown

```text
Symptom
→ incident cannot be escalated

Root cause
→ no ownership metadata

Fix
→ assign owner

Prevention
→ feature registry/contract requirement
```

## Failure 10 — Training and inference transformations diverge

```text
Symptom
→ production performance degrades

Root cause
→ duplicated transformation logic

Fix
→ unify or formally version transformations

Prevention
→ reusable feature definitions
```

---

# 45. Production Troubleshooting

## 45.1 MLflow run missing

### Likely causes

- training failed before run creation
- wrong experiment
- wrong workspace
- run was not started
- permissions issue

### Diagnostic sequence

```text
Check experiment
→ check run creation
→ check job logs
→ check identity
→ check tracking URI
→ check workspace/environment
```

## 45.2 Metrics missing

Check:

```text
Was the metric calculated?
Was log_metric executed?
Did execution reach the logging statement?
Did the run finish successfully?
```

## 45.3 Artifacts missing

Check:

```text
Path exists?
Correct run?
Correct artifact call?
Permissions?
Workspace tracking configuration?
```

## 45.4 Model registration failure

Check:

```text
Model logged?
Model URI valid?
Target UC namespace correct?
Identity authorized?
Model signature available where required?
Current MLflow/Databricks version compatible?
```

## 45.5 Unity Catalog permission failure

Separate:

```text
Identity authentication
vs
Unity Catalog authorization
vs
Cloud storage authorization
vs
Network access
```

Never assume a successful login implies table/model access.

## 45.6 Feature duplicate keys

Run:

```sql
SELECT
    customer_id,
    as_of_date,
    COUNT(*) AS n
FROM features.customer_daily
GROUP BY customer_id, as_of_date
HAVING COUNT(*) > 1;
```

Then investigate:

```text
Source duplicates
→ join multiplication
→ aggregation bug
→ rerun overlap
→ late-arriving data
```

## 45.7 Stale feature table

Check:

```text
Last successful run
→ source freshness
→ pipeline duration
→ failed quality gate
→ scheduling
→ upstream dependency
```

## 45.8 Point-in-time leakage

Check:

```sql
SELECT COUNT(*) AS invalid_rows
FROM training_dataset
WHERE feature_as_of_date > label_date;
```

Expected:

```text
0
```

## 45.9 Training-serving skew

Compare:

```text
same entity
same timestamp
same feature definition
offline value
online value
```

Quantify mismatch instead of relying on anecdotal samples.

## 45.10 Wrong model version

Check:

```text
prediction table
→ model_version/model alias
→ job configuration
→ registry metadata
→ deployment configuration
```

## 45.11 Batch inference duplication

Check the deterministic key:

```text
(customer_id, prediction_date, model_version, batch_id)
```

Then reconcile output count against expected population.

## 45.12 Prediction freshness failure

Check:

```text
last successful batch
→ feature freshness
→ inference runtime
→ output write
→ downstream dependency
```

## 45.13 Drift alert

Use:

```text
prediction distribution
→ feature distributions
→ upstream data
→ freshness
→ schema
→ model version
→ deployment changes
```

## 45.14 Missing lineage

Check whether:

```text
source
→ feature
→ training input
→ MLflow run
→ model
→ prediction
```

is represented by the current governance/tracking configuration.

## 45.15 Schema change

Compare:

```text
expected schema
vs
actual schema
```

Classify:

```text
Backward compatible
vs
Potentially breaking
vs
Breaking
```

---

# 46. SQL Validation Library

## Query 1 — Duplicate feature keys

```sql
SELECT
    customer_id,
    as_of_date,
    COUNT(*) AS row_count
FROM features.customer_daily
GROUP BY customer_id, as_of_date
HAVING COUNT(*) > 1;
```

**Grain:** customer/day.  
**Expected result:** zero rows.  
**Production implication:** duplicate feature keys can create ambiguous training and serving behavior.

## Query 2 — Feature freshness

```sql
SELECT
    MAX(as_of_date) AS latest_feature_date,
    current_date() AS today,
    datediff(current_date(), MAX(as_of_date)) AS age_days
FROM features.customer_daily;
```

**Grain:** one summary row.  
**Expected result:** age within SLA.

## Query 3 — Null rate

```sql
SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_ids,
    SUM(CASE WHEN orders_30d IS NULL THEN 1 ELSE 0 END) AS null_orders_30d
FROM features.customer_daily;
```

**Production implication:** null rates should be compared against the contract, not merely observed.

## Query 4 — Range validation

```sql
SELECT
    MIN(orders_30d) AS min_orders,
    MAX(orders_30d) AS max_orders,
    MIN(revenue_30d) AS min_revenue
FROM features.customer_daily;
```

For count/revenue features, negative values usually require investigation.

## Query 5 — Historical feature lookup

```sql
SELECT *
FROM features.customer_daily
WHERE customer_id = 'C001'
  AND as_of_date <= DATE '2026-06-30'
ORDER BY as_of_date DESC;
```

Use this to inspect the candidate history before selecting a training value.

## Query 6 — Point-in-time join

```sql
WITH candidates AS (
    SELECT
        l.customer_id,
        l.label_date,
        l.churned,
        f.as_of_date,
        f.orders_30d,
        f.revenue_30d,
        ROW_NUMBER() OVER (
            PARTITION BY l.customer_id, l.label_date
            ORDER BY f.as_of_date DESC
        ) AS rn
    FROM labels l
    JOIN features.customer_daily f
      ON l.customer_id = f.customer_id
     AND f.as_of_date <= l.label_date
)
SELECT *
FROM candidates
WHERE rn = 1;
```

## Query 7 — Training validation

```sql
SELECT COUNT(*) AS invalid_training_rows
FROM training_dataset
WHERE feature_as_of_date > label_date;
```

Expected:

```text
0
```

## Query 8 — Prediction duplicates

```sql
SELECT
    customer_id,
    prediction_date,
    COUNT(*) AS n
FROM gold.churn_scores
GROUP BY customer_id, prediction_date
HAVING COUNT(*) > 1;
```

## Query 9 — Prediction freshness

```sql
SELECT
    MAX(prediction_date) AS latest_prediction_date,
    current_date() AS today
FROM gold.churn_scores;
```

## Query 10 — Feature distribution comparison

```sql
SELECT
    as_of_date,
    AVG(orders_30d) AS avg_orders_30d,
    percentile_approx(orders_30d, 0.5) AS median_orders_30d,
    MAX(orders_30d) AS max_orders_30d
FROM features.customer_daily
GROUP BY as_of_date
ORDER BY as_of_date DESC;
```

Use this as a starting point for drift investigation.

---

# 47. Python Examples

## 47.1 Experiment and run

```python
import mlflow

mlflow.set_experiment("/Shared/churn-experiment")

with mlflow.start_run():
    mlflow.log_param("feature_version", "v1")
    mlflow.log_param("training_dataset", "churn_training_v1")
```

**What is tracked:** experiment, run, parameters.  
**Production implication:** metadata should be stable enough to reconstruct the training context.

## 47.2 Metrics and artifacts

```python
with mlflow.start_run():
    mlflow.log_metrics({
        "accuracy": accuracy,
        "roc_auc": roc_auc,
    })

    mlflow.log_artifact("evaluation_report.json")
```

## 47.3 Dataset metadata

Prefer current MLflow dataset/input tracking where supported:

```python
# Pseudocode for the dataset construction step:
dataset = build_current_mlflow_dataset_reference(...)

with mlflow.start_run():
    mlflow.log_input(dataset, context="training")
```

If the exact dataset-construction API differs in the learner's installed MLflow version, verify the version-specific documentation rather than copying an outdated snippet.

## 47.4 Model loading by version

Current MLflow model registry workflows support model URIs such as:

```python
import mlflow.pyfunc

model = mlflow.pyfunc.load_model(
    "models:/ml_prod.churn.churn_model/17"
)
```

## 47.5 Model loading by alias

```python
import mlflow.pyfunc

model = mlflow.pyfunc.load_model(
    "models:/ml_prod.churn.churn_model@champion"
)
```

The alias approach decouples inference code from a specific numeric version.

---

# 48. Hands-on Project — `src/lab/features/`

The required practical project is:

```text
src/lab/features/
```

The learner must build:

```text
features.customer_daily
```

with:

```text
primary key = customer_id
timestamp key = as_of_date
```

and churn-related features.

Suggested repository structure:

```text
src/lab/features/
├── README.md
├── feature_pipeline.py
├── training_set.py
├── leakage_test.py
├── train_model.py
├── batch_inference.py
├── quality_checks.py
├── contracts/
│   └── churn_features.md
├── sql/
│   ├── feature_quality.sql
│   ├── point_in_time.sql
│   └── prediction_quality.sql
└── tests/
    ├── test_features.py
    ├── test_temporal_correctness.py
    └── test_inference.py
```

---

# 49. Hands-on Exercise 1 — Feature Table

Build:

```text
features.customer_daily
```

Columns:

```text
customer_id
as_of_date
orders_7d
orders_30d
revenue_30d
avg_order_value_30d
days_since_last_order
support_tickets_30d
```

Document:

- source tables
- transformations
- grain
- keys
- freshness
- quality rules
- ownership

The table must be produced by a scheduled pipeline.

---

# 50. Hands-on Exercise 2 — Training Set

Create labels:

```text
customer_id
label_date
churned
```

Construct the point-in-time training dataset.

Required invariant:

```text
feature.as_of_date <= label.label_date
```

For each label, choose the latest valid historical feature row.

---

# 51. Hands-on Exercise 3 — Leakage Test

Create a deliberately incorrect implementation:

```text
label
JOIN
current feature snapshot
```

Observe:

- row multiplication
- future data
- changed feature values
- artificially strong metrics

Then replace it with the point-in-time implementation.

Document:

```text
Incorrect approach
→ Why it leaks
→ Evidence
→ Correct approach
→ Validation
```

---

# 52. Hands-on Exercise 4 — Manual Recalculation

Select at least five customers.

For each:

1. inspect source data
2. calculate features manually
3. identify historical cutoff
4. select latest valid feature row
5. compare against training dataset
6. document evidence

This is mandatory.

---

# 53. Hands-on Exercise 5 — MLflow

Train a tiny baseline model.

The model can be simple. The learning objective is:

```text
Training Dataset
→ MLflow Run
→ Parameters
→ Metrics
→ Artifacts
→ Model
```

Log:

- training dataset identifier
- feature table version
- parameters
- metrics
- model
- relevant code/version metadata

---

# 54. Hands-on Exercise 6 — Unity Catalog Model

Register the model in Unity Catalog.

Demonstrate:

```text
model
→ version
→ alias
→ permissions
→ lineage
```

The learner must be able to answer:

> Which training data produced this model?

---

# 55. Hands-on Exercise 7 — Batch Inference

Create:

```text
gold.churn_scores
```

Required fields:

```text
customer_id
prediction_date
churn_probability
predicted_label
model_version
```

Recommended operational metadata:

```text
feature_snapshot
batch_id
prediction_generated_at
```

Implement idempotency.

---

# 56. Hands-on Exercise 8 — Lakeflow Job

Connect:

```text
Feature refresh
      ↓
Quality check
      ↓
Model inference
      ↓
Prediction validation
      ↓
gold.churn_scores
```

Use Topic 08 knowledge rather than re-learning orchestration.

---

# 57. Hands-on Exercise 9 — Lineage

Verify:

```text
Source
 ↓
Gold
 ↓
Feature table
 ↓
Training dataset
 ↓
Model
 ↓
Prediction table
```

Document what the lineage graph proves and what it does not prove.

---

# 58. Hands-on Exercise 10 — ML Handoff

Produce the final handoff document:

```text
Feature schema
Feature definitions
Keys
Timestamp semantics
Freshness
Quality
Point-in-time rules
Ownership
Lineage
Versioning
Access
SLA
Incident procedure
```

This is the final interface between Data Engineering and ML.

---

# 59. Progressive Labs

Every lab must contain:

```text
Objective
Prerequisites
Scenario
Step-by-step instructions
SQL/Python
Expected output
Validation
Common mistakes
Troubleshooting
Production takeaway
Checkpoint
```

## Lab 01 — Understand MLflow architecture

**Objective:** map experiment → run → metadata → model.  
**Scenario:** inspect a completed training run.  
**Validation:** explain where parameters, metrics, artifacts, and model metadata live.  
**Checkpoint:** explain why a model file alone is insufficient.

## Lab 02 — Create an experiment

Create a dedicated experiment and document naming/ownership.

## Lab 03 — Create a run

Execute a tiny tracked training attempt and record the run ID.

## Lab 04 — Log parameters

Log model configuration and explain how it supports comparison.

## Lab 05 — Log metrics

Log training and validation metrics and associate them with the dataset context.

## Lab 06 — Log artifacts

Store an evaluation report and feature statistics.

## Lab 07 — Track a model

Log a model with an input example/signature where supported.

## Lab 08 — Register a model in Unity Catalog

Register the model and verify permissions.

## Lab 09 — Explore model versions and aliases

Create candidate/champion semantics and explain promotion.

## Lab 10 — Create a feature table

Build `features.customer_daily`.

## Lab 11 — Validate feature-table keys

Find and fix duplicate entity/time keys.

## Lab 12 — Validate feature freshness

Create a freshness query and alert threshold.

## Lab 13 — Build historical feature data

Generate multiple historical feature rows per customer.

## Lab 14 — Build a point-in-time training set

Implement the temporal join and validate one row per label.

## Lab 15 — Detect and fix leakage

Compare bad current-value join versus correct historical join.

## Lab 16 — Track dataset/feature versions

Record feature and Delta versions and associate them with the MLflow run.

## Lab 17 — Train and register a baseline model

Produce a governed model version.

## Lab 18 — Build batch inference

Load the approved model and write `gold.churn_scores`.

## Lab 19 — Monitor predictions

Monitor count, freshness, nulls, distribution, and duplicates.

## Lab 20 — Complete the full ML handoff

Produce the contract, evidence, runbook, ADR, and architecture diagram.

---

# 60. Break/Fix Scenarios

Every incident follows:

```text
Symptom
→ Investigation
→ Evidence
→ Root Cause
→ Fix
→ Prevention
```

## Incident 1 — Duplicate feature keys

Expected investigation:

```text
Check key duplicates
→ inspect upstream grain
→ inspect joins
→ inspect reruns
→ correct pipeline
→ add uniqueness gate
```

## Incident 2 — Feature freshness is 48 hours behind

Investigate upstream freshness, scheduler, pipeline failures, and quality gates.

## Incident 3 — Training accuracy is suspiciously high

Investigate leakage before tuning the model.

## Incident 4 — Point-in-time leakage discovered

Identify offending timestamps, rebuild the training dataset, invalidate affected model versions, and document impact.

## Incident 5 — Model cannot be reproduced

Identify missing source, feature, dataset, code, environment, or run metadata.

## Incident 6 — Registered model points to wrong version

Inspect alias, model metadata, job configuration, and deployment history.

## Incident 7 — Batch inference creates duplicates

Inspect retry semantics and deterministic batch keys.

## Incident 8 — Prediction distribution suddenly changes

Compare feature distribution, model version, population, upstream source, and freshness.

## Incident 9 — Feature transformation differs between training and inference

Run offline/online comparison and identify semantic divergence.

## Incident 10 — Feature schema changes without notification

Perform schema diff, determine compatibility, restore/version appropriately, and update the contract.

## Incident 11 — ML team cannot determine feature ownership

Treat ownership metadata as a production-control failure.

## Incident 12 — Prediction pipeline fails after feature-table change

Investigate schema compatibility, contract version, job dependency, and model signature.

---

# 61. Production Runbooks

## Runbook 1 — Feature Freshness Incident

### Purpose

Restore feature freshness within the agreed SLA.

### Trigger

```text
current_time - latest_available_feature_time > SLA
```

### Inputs

- feature table
- pipeline run history
- upstream tables
- scheduler
- freshness SLA

### Diagnostic queries

```sql
SELECT MAX(as_of_date)
FROM features.customer_daily;
```

### Steps

1. Confirm the SLA violation.
2. Check latest successful pipeline run.
3. Check upstream freshness.
4. Check pipeline failure logs.
5. Check quality gates.
6. Recover the failing stage.
7. Recompute affected partitions.
8. validate freshness.
9. notify consumers if the SLO was breached.

### Prevention

- freshness metric
- alert
- dependency monitoring
- replay procedure

## Runbook 2 — Feature Quality Incident

1. Identify failed rule.
2. Determine affected partition.
3. Compare current versus previous valid output.
4. identify upstream cause.
5. quarantine or block invalid data.
6. repair and recompute.
7. validate.
8. release only after quality gates pass.

## Runbook 3 — Training-Data Leakage Investigation

1. freeze affected model training.
2. identify training dataset version.
3. query feature timestamps.
4. find rows where feature time > label time.
5. quantify affected rows.
6. identify model versions trained from the dataset.
7. rebuild training data.
8. rerun validation.
9. invalidate affected model versions where required.
10. document incident.

## Runbook 4 — Model Reproducibility Investigation

Reconstruct:

```text
Model version
→ MLflow run
→ input dataset
→ feature version
→ Delta version
→ code version
→ environment
→ parameters
→ metrics
→ artifact
```

If a link is missing, mark reproducibility as degraded.

## Runbook 5 — Batch Prediction Failure

Check:

```text
feature freshness
→ model availability
→ model version/alias
→ permissions
→ compute
→ input schema
→ prediction code
→ target write
```

Recover idempotently.

## Runbook 6 — Training-Serving Skew Investigation

Compare the same entities and timestamps across:

```text
offline feature
online feature
transformation version
source
availability time
```

Quantify differences.

## Runbook 7 — Prediction Drift Investigation

```text
Prediction distribution
→ Feature distributions
→ Freshness
→ Upstream data
→ Model version
→ Population
→ Deployment
```

Classify root cause.

## Runbook 8 — ML Schema-Change Incident

1. capture actual schema.
2. compare to contract.
3. classify compatibility.
4. identify affected consumers.
5. restore or publish new version.
6. update contract.
7. notify consumers.
8. add regression test.

---

# 62. Decision Matrices

## 62.1 Feature storage

| Option | Best fit | Freshness | Complexity | Cost | Governance |
|---|---|---|---|---|---|
| Gold table | General analytics/batch ML | Hour/day | Low | Low | Strong |
| Feature table | Reusable governed features | Hour/day | Medium | Medium | Strong |
| Online feature store | Low-latency serving | Seconds/minutes | High | Higher | Strong if designed well |

## 62.2 Inference

| Option | Choose when | Reject when |
|---|---|---|
| Batch | Scheduled predictions are acceptable | Millisecond decisions required |
| Online | Low latency is a hard requirement | Batch meets business need |

## 62.3 Training data

| Option | Use |
|---|---|
| Current snapshot | Non-temporal/static features |
| Historical snapshot | Reproducibility and retrospective analysis |
| Point-in-time dataset | Time-dependent ML training |

## 62.4 Model deployment

| State | Purpose |
|---|---|
| Development | experimentation |
| Candidate | validation |
| Production | approved inference |

Use semantic aliases where appropriate instead of embedding numeric versions into application code.

## 62.5 Feature computation

| Mode | Best fit |
|---|---|
| Scheduled | daily/hourly batch |
| Streaming | continuously changing features |
| Online | request-time low-latency feature computation |

Every decision should consider:

```text
Latency
Cost
Freshness
Complexity
Governance
Operational burden
```

---

# 63. Architecture Decision Records

Each ADR uses:

```text
Context
Problem
Options
Decision
Trade-offs
Consequences
Operational implications
```

## ADR 1 — Feature table design

**Decision:** use a governed Delta-backed feature table for reusable daily customer features.

**Trade-off:** centralized reuse versus platform complexity.

## ADR 2 — Batch vs online inference

**Decision:** choose batch unless the business SLO requires request-time latency.

**Trade-off:** lower complexity versus lower freshness.

## ADR 3 — Feature freshness SLA

**Decision:** define a measurable freshness SLA based on business decision latency.

**Trade-off:** tighter SLA increases compute and operational burden.

## ADR 4 — Point-in-time training architecture

**Decision:** require temporal joins for time-varying features.

**Trade-off:** more complex training-set construction, substantially lower leakage risk.

## ADR 5 — Feature ownership and governance

**Decision:** every published feature requires an owner, contract, and quality/freshness rules.

**Trade-off:** additional governance work prevents unmanaged feature sprawl.

## ADR 6 — Model/data versioning

**Decision:** record model, feature, dataset, code, and MLflow run identity.

**Trade-off:** additional metadata management enables reproducibility.

---

# 64. Production Case Studies

## Case Study 1 — Customer churn

```text
Business problem:
Predict customer churn.

Features:
orders_30d
revenue_30d
support_tickets_30d

Temporal requirement:
No information after label cutoff.

Inference:
Daily batch.

Output:
gold.churn_scores
```

Failure mode: future feature leakage.

## Case Study 2 — Fraud detection

Features update frequently. Point-in-time correctness and late-arriving transaction handling are critical.

Failure mode: fraud investigation fields accidentally become training features.

## Case Study 3 — Recommendation features

High reuse can justify a feature platform.

Failure mode: online/offline definitions diverge.

## Case Study 4 — Credit-risk feature pipeline

Governance and reproducibility are critical.

Failure mode: training dataset cannot be reconstructed for audit.

## Case Study 5 — RAG / AI Search data pipeline

Data Engineer owns:

```text
source ingestion
→ chunk/update pipeline
→ metadata
→ permissions
→ index refresh
→ deletion propagation
→ lineage
```

Failure mode: stale or unauthorized source content becomes retrievable.

---

# 65. Senior Data Engineer Scenarios

## Scenario 1

> AUC increased from 0.78 to 0.96 overnight. What do you investigate?

Strong reasoning:

```text
Check leakage
→ compare training dataset version
→ compare feature distributions
→ inspect label changes
→ inspect population
→ inspect train/test split
→ inspect recent feature logic
→ inspect source anomalies
```

Do not celebrate the metric before validating the data.

## Scenario 2

> The feature table is fresh, but production predictions are stale.

Investigate:

```text
Feature availability
→ inference schedule
→ inference input snapshot
→ model version
→ target write
→ downstream consumers
```

Feature freshness alone does not prove prediction freshness.

## Scenario 3

> A model cannot be reproduced six months later.

Missing metadata may include:

```text
source version
feature version
dataset version
code version
environment
MLflow run
parameters
model version
```

## Scenario 4

> Training uses historical features but online serving uses current values.

Risk:

```text
training-serving skew
```

The model learns one semantic process and receives another in production.

## Scenario 5

> A feature definition must change without breaking three models.

Prefer:

```text
new feature version
→ compatibility period
→ migrate consumers
→ deprecate old feature
```

Avoid silent semantic mutation.

## Scenario 6

> The ML team wants online features. When should you reject it?

Reject or challenge the architecture when:

- batch meets the business SLO
- latency is not truly critical
- online freshness is not required
- operational complexity is unjustified
- ownership is unclear
- cost is disproportionate

## Scenario 7

> Design point-in-time training data for 500 features.

Senior approach:

```text
Standardize entity/time semantics
→ centralize feature definitions
→ enforce temporal keys
→ build scalable as-of retrieval
→ validate leakage
→ version feature inputs
→ log training inputs
→ test representative samples
→ monitor quality
```

---

# 66. Interview Preparation

For every interview question, answer using:

```text
What interviewer is testing
→ Strong reasoning
→ Expected architecture
→ Common weak answer
→ Senior-level answer
```

## Beginner

1. What is MLflow?
2. What is an experiment?
3. What is a run?
4. What is a feature?
5. What is a feature table?
6. What is a model registry?
7. Why log parameters?
8. Why log metrics?
9. What is an artifact?
10. Why version models?
11. What is a model alias?
12. What is feature freshness?
13. What is a label?
14. What is batch inference?
15. What is lineage?

## Intermediate

1. What is point-in-time correctness?
2. What is feature leakage?
3. Why version training data?
4. How do you build feature tables?
5. How do you guarantee feature freshness?
6. How do you run batch inference?
7. Why are timestamp semantics important?
8. How do you detect duplicate feature keys?
9. How do you make batch inference idempotent?
10. How do you track a dataset in MLflow?
11. Why is model governance connected to table governance?
12. What is training-serving skew?
13. Why are current feature values dangerous for historical training?
14. How do aliases help deployment?
15. What belongs in a feature contract?
16. How do you validate predictions?
17. How do you monitor drift?
18. What should a prediction table contain?
19. When is online inference unnecessary?
20. What does reproducibility mean?

## Advanced

1. How do you prevent training-serving skew?
2. How do you design a feature platform?
3. How do you guarantee reproducibility?
4. How do you design ML data lineage?
5. Batch versus online features?
6. How do you design temporal joins at scale?
7. How do you handle late-arriving events?
8. How do you version feature definitions?
9. How do you deprecate a feature safely?
10. How do you handle 500 features?
11. How do you prove no leakage?
12. How do you monitor prediction drift?
13. How do you design model promotion?
14. How do you separate model and data governance?
15. How do you recover a failed inference run?
16. How do you audit a model six months later?
17. How do you reconcile online/offline features?
18. How do you design prediction-table idempotency?
19. How do you control PII in ML features?
20. How does lineage support incident response?

## Senior / Staff

1. Design an enterprise feature platform.
2. Design a point-in-time training system.
3. Design a Data Engineer → ML Engineer handoff.
4. Design feature governance for hundreds of features.
5. Investigate a production prediction anomaly.
6. Design a model/data reproducibility architecture.
7. Design feature lifecycle governance.
8. Design multi-team feature ownership.
9. Design batch inference for 100 million customers.
10. Design temporal feature storage for multiple model horizons.
11. Design a drift investigation platform.
12. Design online/offline feature consistency.
13. Design model promotion with governed aliases.
14. Design ML data contracts.
15. Design safe feature schema evolution.
16. Design lineage for training and inference.
17. Design recovery after leakage discovery.
18. Design cost controls for feature and inference pipelines.
19. Decide whether to build or buy a feature platform.
20. Design an enterprise ML data platform operating model.

---

# 67. Practice Questions

## Beginner — 15

1. Define experiment, run, parameter, metric, artifact, and model.
2. Why is a run different from an experiment?
3. Why log feature version metadata?
4. What is a feature table?
5. What is an entity key?
6. What is a timestamp key?
7. What is point-in-time correctness?
8. What is a model alias?
9. What is batch inference?
10. Why should predictions include model metadata?
11. What is feature freshness?
12. What is data drift?
13. What is feature drift?
14. What is prediction drift?
15. What belongs in an ML handoff contract?

## Intermediate — 20

1. Explain why current feature values can leak future information.
2. Design a uniqueness test for `features.customer_daily`.
3. Design a freshness SLA.
4. Explain why MLflow alone does not guarantee reproducibility.
5. Explain Delta versioning in an ML context.
6. Explain model version versus model alias.
7. Design a batch inference idempotency key.
8. Design a feature owner metadata record.
9. Explain training-serving skew.
10. Design a prediction table.
11. Explain temporal semantics.
12. Explain the difference between event time and availability time.
13. Design a feature schema change policy.
14. Explain lineage requirements.
15. Explain when online serving is justified.
16. Design a drift investigation.
17. Explain feature deprecation.
18. Design a training-data contract.
19. Explain why a feature table is more than storage.
20. Design a batch inference recovery strategy.

## Advanced — 20

1. Design a point-in-time join for multiple labels per customer.
2. Design a feature platform for 500 features.
3. Handle late-arriving events without corrupting historical training data.
4. Design model reproducibility for six years of model history.
5. Design feature version migration across three models.
6. Design offline/online consistency checks.
7. Design a feature freshness monitoring system.
8. Design drift monitoring at scale.
9. Design governed model promotion.
10. Design prediction-table reconciliation.
11. Design training-data snapshots.
12. Design data-quality gates before model training.
13. Design a model/data incident response workflow.
14. Design feature access controls.
15. Design PII handling for ML features.
16. Design a feature retirement process.
17. Design a lineage graph for training and inference.
18. Design a batch scoring platform with backfills.
19. Design a cost-aware feature architecture.
20. Decide when centralized features create more complexity than value.

## SQL — 10

1. Write duplicate-key detection.
2. Write feature freshness validation.
3. Write null-rate validation.
4. Write range validation.
5. Write a historical feature lookup.
6. Write a point-in-time join.
7. Write a leakage detection query.
8. Write prediction duplicate detection.
9. Write prediction freshness validation.
10. Write a feature-distribution comparison query.

## Python / MLflow — 10

1. Create an MLflow experiment.
2. Create a run.
3. Log parameters.
4. Log metrics.
5. Log an artifact.
6. Log dataset metadata.
7. Log a model.
8. Register a model.
9. Load a model by version.
10. Load a model by alias.

## Feature-engineering scenarios — 10

1. Design daily customer features.
2. Design a rolling 30-day feature.
3. Design feature freshness monitoring.
4. Design feature ownership.
5. Design feature deprecation.
6. Design a feature schema contract.
7. Design online/offline consistency.
8. Design feature reuse.
9. Design a historical snapshot.
10. Design a feature lifecycle.

## Point-in-time correctness — 10

1. Explain leakage.
2. Identify a future feature.
3. Correct a current-value join.
4. Choose the latest valid feature row.
5. Handle multiple labels.
6. Handle late-arriving events.
7. Prove no leakage manually.
8. Design a temporal test.
9. Design a temporal data contract.
10. Explain training versus serving timestamps.

## Production troubleshooting — 10

1. Duplicate features.
2. Stale features.
3. Missing MLflow run.
4. Missing model registration.
5. Wrong model alias.
6. Duplicate predictions.
7. Drift alert.
8. Schema change.
9. Missing lineage.
10. Reproducibility failure.

## Architecture — 10

1. Enterprise feature platform.
2. Point-in-time training service.
3. Batch inference platform.
4. Online feature architecture.
5. Drift monitoring platform.
6. ML handoff contract platform.
7. Feature governance model.
8. Model/data lineage architecture.
9. Cost-aware feature platform.
10. ML data platform operating model.

---

# 68. Mental Models

## Mental Model 1

```text
Data → Features → Training → Model → Prediction
```

## Mental Model 2

```text
Feature value
+
Timestamp
=
Meaning
```

## Mental Model 3

```text
Historical truth
≠
Current truth
```

## Mental Model 4

```text
Model reproducibility
=
Code
+
Data
+
Features
+
Parameters
+
Environment
+
Version
```

## Mental Model 5

```text
Training correctness
=
No future information
```

## Mental Model 6

```text
Feature platform
=
Data
+
Metadata
+
Governance
+
Temporal semantics
+
Serving
```

## Mental Model 7

```text
Good ML handoff
=
Schema
+
Freshness
+
Ownership
+
Lineage
+
Versioning
+
Quality
```

---

# 69. Common Misconceptions

## "Feature table = normal table"

Incomplete.

A production feature table has temporal, ownership, quality, governance, and reuse semantics.

## "Current feature values are fine for training"

Dangerous.

Historical training requires historical truth.

## "MLflow alone makes a model reproducible"

False.

Reproducibility also requires data, feature, code, environment, and version metadata.

## "Model registry solves data lineage"

False.

Model lineage is only one part of the data-to-prediction lineage chain.

## "Online features are always better"

False.

Online serving increases latency capability but also increases complexity and cost.

## "More recent features are always better"

False.

The correct feature is the feature that was valid and available at the prediction cutoff.

---

# 70. Glossary

| Term | Definition |
|---|---|
| MLflow | Platform for tracking ML development and packaging/managing ML assets. |
| Experiment | Group of related MLflow runs. |
| Run | One tracked execution. |
| Parameter | Training/configuration value recorded for a run. |
| Metric | Measured evaluation value. |
| Artifact | File or directory logged to a run. |
| Model | Packaged ML model artifact. |
| Model Registry | Centralized model lifecycle and version management system. |
| Model Version | Specific version of a registered model. |
| Model Alias | Mutable named reference to a model version. |
| Feature | Input variable used by a model. |
| Feature Table | Governed data asset containing feature values and associated feature semantics. |
| Feature Store | System/capability for managing, discovering, retrieving, and serving features. |
| Entity Key | Identifier for the entity represented by a feature. |
| Timestamp Key | Time field used to express feature temporal meaning. |
| Label | Target outcome for supervised learning. |
| Point-in-Time Correctness | Ensuring features reflect information available at the prediction cutoff. |
| Leakage | Future or otherwise invalid information entering training. |
| Training-Serving Skew | Difference between feature logic or values used during training and inference. |
| Batch Inference | Scheduled scoring of a population. |
| Online Inference | Request-time model prediction. |
| Feature Freshness | How recently a usable feature value was produced and made available. |
| Data Drift | Change in input data distribution. |
| Feature Drift | Change in feature distribution. |
| Prediction Drift | Change in model-output distribution. |
| Lineage | Traceability from upstream data through features, models, and predictions. |
| Reproducibility | Ability to reconstruct a prior training/model result. |
| Data Contract | Explicit agreement defining data semantics and operational expectations. |
| Model Contract | Interface defining model input/output expectations and governance. |
| Feature SLA | Operational freshness/availability target for a feature. |
| AI Search | Current Databricks terminology for the capability formerly known as Vector Search. |
| Embedding | Numerical representation used for similarity-based retrieval. |
| Online Serving | Low-latency delivery of features and/or model predictions. |

---

# 71. Production Safety and Cost Awareness

Use:

- small datasets
- minimal compute
- serverless/free learning options where appropriate
- auto-termination
- short experiments
- explicit cleanup
- no production-sized training experiments in a learning workspace

The goal is to learn ML data engineering without unnecessary cloud spending.

---

# 72. Current Product and API Safety

Databricks and MLflow change rapidly.

Before using concrete production syntax, verify:

- current MLflow tracking APIs
- current Unity Catalog model-registration workflow
- current feature-engineering APIs
- current online-serving terminology
- current AI Search terminology
- current monitoring capabilities
- current Databricks Runtime behavior
- current serverless/classic differences

Capabilities may vary by:

- AWS
- Azure
- GCP
- workspace configuration
- Databricks edition
- serverless availability
- Runtime version
- MLflow version
- product generation

### No fake APIs

If exact syntax is uncertain:

1. verify official documentation
2. use a clearly labeled conceptual example
3. state what must be verified in the learner's workspace

Do not fabricate an API merely to make an example look complete.

---

# 73. Cross-Topic Connections

## Topic 04 — Unity Catalog

Use governance, permissions, ownership, lineage, and catalog structure for ML assets.

## Topic 07 — Lakeflow Declarative Pipelines

Use declarative data-quality and pipeline concepts for feature production.

## Topic 08 — Lakeflow Jobs

Use orchestration for feature refresh, inference, validation, retries, and backfills.

## Topic 09 — Performance

Apply performance principles to feature computation and batch inference.

## Topic 12 — Asset Bundles and CI/CD

Package ML data pipelines, jobs, tests, and configuration into repeatable deployments.

## Topic 13 — Cost Management and System Tables

Measure feature/inference compute and attribute cost.

## Module 2.20 — Governance, lineage, PII

Apply governance to ML data and model interfaces.

## Module 2.21 — Performance and cost

Optimize feature and inference workloads.

## Module 2.22 — Semantic layers and feature stores

Apply earlier feature-platform concepts to governed ML handoff.

Do not re-teach these modules. Apply them.

---

# 74. Final Capstone — Customer Churn ML Data Platform and Handoff

## Architecture

```text
Source Orders
Source Customers
Source Support Tickets
        ↓
Bronze
        ↓
Silver
        ↓
Gold
        ↓
features.customer_daily
        ↓
Point-in-Time Training Dataset
        ↓
MLflow Experiment
        ↓
Model
        ↓
Unity Catalog Model Registry
        ↓
Batch Inference
        ↓
gold.churn_scores
```

## Required deliverables

1. Feature engineering.
2. Feature table.
3. Feature keys.
4. Feature timestamps.
5. Quality validation.
6. Feature freshness.
7. Churn labels.
8. Point-in-time training set.
9. Leakage testing.
10. Manual leakage proof.
11. MLflow tracking.
12. Parameters.
13. Metrics.
14. Artifacts.
15. Dataset/version metadata.
16. Model registration.
17. Model version.
18. Model alias/current promotion mechanism.
19. Lineage.
20. Batch inference.
21. Idempotency.
22. Prediction validation.
23. Prediction table.
24. Lakeflow Job orchestration.
25. Monitoring.
26. ML handoff contract.
27. Feature ownership.
28. Production runbook.
29. Architecture decision record.
30. Final technical documentation.

## Capstone repository target

```text
src/lab/features/
├── feature_pipeline.py
├── training_set.py
├── leakage_test.py
├── train_model.py
├── batch_inference.py
├── quality_checks.py
├── contracts/
│   └── churn_features.md
├── sql/
│   ├── feature_quality.sql
│   ├── point_in_time.sql
│   └── prediction_quality.sql
└── tests/
    ├── test_features.py
    ├── test_temporal_correctness.py
    └── test_inference.py
```

## Capstone questions

The learner must be able to answer:

```text
What features were used?
When were they valid?
What data produced them?
What version of the feature table was used?
What training dataset was used?
What MLflow run produced the model?
What model version is deployed?
What features does inference use?
Where are predictions stored?
Who owns the feature?
What happens if the feature becomes stale?
What happens if the schema changes?
How do we prove there was no leakage?
How do we reproduce the model?
```

If the learner cannot answer these questions, the capstone is incomplete.

---

# 75. Production Quality Gate

The learner must demonstrate:

```text
[ ] Explain MLflow experiments
[ ] Explain MLflow runs
[ ] Log parameters
[ ] Log metrics
[ ] Log artifacts
[ ] Track models
[ ] Register models in Unity Catalog
[ ] Explain model versions
[ ] Explain model aliases
[ ] Explain model governance
[ ] Design feature tables
[ ] Define feature keys
[ ] Define timestamp semantics
[ ] Validate feature quality
[ ] Validate feature freshness
[ ] Build historical features
[ ] Build point-in-time training sets
[ ] Detect leakage
[ ] Prove no leakage manually
[ ] Version training data
[ ] Track Delta table versions
[ ] Understand lineage
[ ] Build batch inference
[ ] Write predictions to gold
[ ] Make inference idempotent
[ ] Orchestrate inference
[ ] Monitor predictions
[ ] Explain online feature serving
[ ] Explain model serving
[ ] Explain AI Search / Vector Search awareness
[ ] Explain drift monitoring
[ ] Design ML handoff contract
[ ] Define ownership
[ ] Define freshness SLA
[ ] Define schema/change policy
[ ] Troubleshoot feature incidents
[ ] Troubleshoot inference incidents
[ ] Build production capstone
```

---

# 76. Reproducibility Checklist

```text
[ ] Source version known
[ ] Feature version known
[ ] Training dataset version known
[ ] Code version known
[ ] Environment known
[ ] MLflow run known
[ ] Parameters known
[ ] Metrics known
[ ] Model version known
[ ] Prediction version known
```

A reproducibility review should fail closed when critical metadata is missing.

---

# 77. Final Operating Standard

Use this operating standard for every ML data handoff:

```text
SOURCE
  ↓
CURATE
  ↓
DEFINE FEATURE
  ↓
GOVERN
  ↓
VALIDATE GRAIN
  ↓
VALIDATE TEMPORAL SEMANTICS
  ↓
VALIDATE FRESHNESS
  ↓
BUILD POINT-IN-TIME TRAINING DATA
  ↓
VERSION DATA
  ↓
TRACK WITH MLFLOW
  ↓
REGISTER MODEL
  ↓
PRESERVE LINEAGE
  ↓
RUN IDEMPOTENT INFERENCE
  ↓
VALIDATE PREDICTIONS
  ↓
MONITOR DRIFT
  ↓
HAND OFF THROUGH CONTRACT
  ↓
AUDIT
  ↓
CHANGE SAFELY
```

The central rule is:

> **Govern → Define → Version → Validate time → Track → Register → Infer → Observe → Contract → Operate.**

---

# 78. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Where Taught | Hands-on Evidence |
|---|---|---|---|
| MLflow experiments | YES | Sections 6–7 | Labs 01–02 |
| MLflow runs | YES | Section 6 | Lab 03 |
| Parameters | YES | Section 6 | Lab 04 |
| Metrics | YES | Section 6 | Lab 05 |
| Artifacts | YES | Section 6 | Lab 06 |
| Models | YES | Sections 6–7 | Lab 07 |
| Unity Catalog model registration | YES | Section 8 | Lab 08 |
| Model versions | YES | Section 8 | Lab 09 |
| Model aliases | YES | Section 8 | Lab 09 |
| Feature tables | YES | Sections 9–11 | Lab 10 |
| Primary keys | YES | Sections 9–10 | Lab 11 |
| Timestamp keys | YES | Sections 9, 13 | Labs 10–14 |
| Feature governance | YES | Sections 8–12, 36 | Labs 10, 20 |
| Point-in-time lookups | YES | Sections 14–18 | Lab 14 |
| Training-data correctness | YES | Sections 14–19 | Labs 14–16 |
| Reproducible training data | YES | Sections 20–23 | Lab 16 |
| Delta table versions | YES | Section 21 | Lab 16 |
| Dataset/model lineage | YES | Section 23 | Lab 09, Lab 16, Lab 19 |
| Batch inference | YES | Sections 25–29 | Lab 18 |
| Gold prediction tables | YES | Sections 26–29 | Lab 18 |
| Online feature serving awareness | YES | Sections 30–31 | Architecture exercises |
| Model serving awareness | YES | Sections 30–31 | Architecture exercises |
| Vector Search / AI Search awareness | YES | Section 33 | Case Study 5 |
| Data drift | YES | Section 34 | Lab 19 |
| Feature drift | YES | Section 34 | Lab 19 |
| Prediction drift | YES | Section 34 | Lab 19 |
| ML handoff contract | YES | Sections 36–37 | Lab 20 |
| Schemas | YES | Sections 36–37 | Lab 20 |
| Freshness | YES | Sections 11, 36 | Lab 12 |
| Point-in-time rules | YES | Sections 14–19 | Labs 14–16 |
| Ownership | YES | Section 12 | Lab 20 |
| `features.customer_daily` | YES | Sections 9, 48–50 | Labs 10–14 |
| Point-in-time churn training set | YES | Sections 17–19 | Labs 14–15 |
| Manual leakage proof | YES | Section 19 | Lab 20 / Exercise 4 |
| MLflow model registration | YES | Section 8 | Lab 08 / 17 |
| `gold.churn_scores` | YES | Sections 25–29 | Lab 18 |
| ML handoff document | YES | Sections 36–37 | Lab 20 |
| Progressive labs | YES | Section 59 | Labs 01–20 |
| Break/fix scenarios | YES | Section 60 | Incidents 1–12 |
| Production runbooks | YES | Section 61 | Runbooks 1–8 |
| Decision matrices | YES | Section 62 | Architecture exercises |
| ADRs | YES | Section 63 | ADRs 1–6 |
| Interview preparation | YES | Section 66 | 55+ interview prompts |
| Practice questions | YES | Section 67 | 115+ reasoning exercises |
| Mental models | YES | Section 68 | Seven models |
| Common misconceptions | YES | Section 69 | Six core misconceptions |
| Glossary | YES | Section 70 | Production glossary |
| Final capstone | YES | Section 74 | Customer Churn ML Data Platform |
| Production quality gate | YES | Section 75 | 39-point gate |
| Reproducibility checklist | YES | Section 76 | Audit checklist |
| Current API/version safety | YES | Section 72 | Current-doc verification rule |
| Cost/safety awareness | YES | Section 71 | Capstone and labs |
| Cross-topic connections | YES | Section 73 | Topics 04/07/08/09/12/13 + Modules 2.20–2.22 |
| G4 build-loop alignment | YES | Sections 2, 77 | Full capstone loop |

**Coverage status: YES for every mandatory roadmap requirement.**

---

# 79. Current Documentation References

The module was validated against current official documentation available at build time:

- MLflow Model Registry: https://mlflow.org/docs/latest/model-registry/
- MLflow Model Registry tutorials: https://mlflow.org/docs/latest/ml/model-registry/tutorial
- MLflow Tracking APIs: https://mlflow.org/docs/latest/ml/tracking/tracking-api
- MLflow Models: https://mlflow.org/docs/latest/models/
- Databricks Feature Store concepts: https://docs.databricks.com/aws/en/machine-learning/feature-store/concepts
- Databricks Feature Store overview: https://docs.databricks.com/aws/en/machine-learning/feature-store
- Databricks AI Search / formerly Vector Search: https://docs.databricks.com/gcp/en/dev-tools/databricks-apps/vector-search

Because Databricks and MLflow evolve rapidly, these references are starting points for current syntax and capabilities, not a substitute for checking the learner's exact workspace/runtime/version.

---

# 80. Final Learning Outcome

The learner should finish this module able to operate as a strong **Data Engineer working alongside ML Engineers**, not as a beginner ML practitioner.

They should be able to explain:

> **How data becomes features, how features become reproducible training data, how MLflow tracks the experiment and model, how Unity Catalog governs the model, how point-in-time correctness prevents leakage, how batch inference produces governed prediction tables, and how Data Engineering hands reliable features and datasets to ML teams through a production contract.**

That is the central competency of this final G4 module.

---

# Artifact Validation Record

- Target filename: `14-mlflow-and-feature-engineering-handoff.md`
- Required progression: beginner → production ML handoff
- Required hands-on labs: 20
- Required break/fix incidents: 12
- Required production runbooks: 8
- Required ADR exercises: 6
- Required capstone: Customer Churn ML Data Platform and Handoff
- Required prediction target: `gold.churn_scores`
- Required feature table: `features.customer_daily`
- Required feature keys: `customer_id`, `as_of_date`
- Required manual leakage proof: included
- Required roadmap coverage audit: included
- Required production quality gate: included
- Required current-API safety guidance: included
- Required scope boundary against full ML theory course: included

