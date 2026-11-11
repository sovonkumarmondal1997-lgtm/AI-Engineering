# Distributed ML with Spark MLlib

> **Module:** Stage 2C — Data Engineering_3 → 10-Big-Data-ML-and-MLOps-Handoff  
> **Lesson:** 01 of 05  
> **Level:** Beginner foundations → intermediate implementation → advanced engineering awareness  
> **Primary API:** PySpark DataFrame-based `pyspark.ml` API  
> **Reference environment:** Python 3.11, Java 17, Apache Spark/PySpark 3.5.7

## 1. Learning outcomes

By the end of this lesson, you should be able to:

- Describe the ML workflow: data → features → train → evaluate → predict.
- Distinguish classification, regression, and clustering, and choose defensible evaluation metrics.
- Build temporal train/validation/test splits and explain leakage, overfitting, and generalization.
- Decide whether distributed training is justified by measuring data size, memory, runtime, and operating cost.
- Explain and use Spark MLlib `Transformer`, `Estimator`, `Pipeline`, and `PipelineModel`.
- Apply the required transformers: `StringIndexer`, `OneHotEncoder`, `VectorAssembler`, `StandardScaler`, `Imputer`, `Bucketizer`, `Tokenizer`, `HashingTF`, and `IDF`.
- Select and evaluate `LogisticRegression`, `LinearRegression`, `RandomForest`, `GBTClassifier`, `KMeans`, and ALS for appropriate problems.
- Tune models without contaminating the final test set; understand `ParamGridBuilder` and the limitations of ordinary cross-validation for temporal data.
- Persist a fitted pipeline, reload it in a fresh session, validate its outputs, and score a new batch.
- Recognize the architecture and trade-offs of Spark performance tuning, LightGBM/XGBoost, Dask-ML, Ray Train, and distributed deep-learning data workflows.

This lesson focuses on **the data and pipeline around a model**, not on deriving optimization algorithms or deep-learning architectures. Those belong to later mathematics and ML stages.

## 2. Prerequisites and environment setup

### 2.1 Concepts you should already recognize

You do not need to be a modeling expert yet, but you should recognize Python functions and packages, SQL filters/joins/window functions, DataFrame schemas, Spark partitions, train/test splits, and basic classification terminology. Earlier roadmap modules cover Python, Spark, lakehouse formats, orchestration, data quality, and experiment tracking.

### 2.2 Version and compatibility assumptions

The examples target the Spark 3.5.7 DataFrame ML API (`pyspark.ml`), Python 3.11, and Java 17. Keep the Spark patch version and Python environment fixed. The `applyInPandas` example uses Arrow, so constrain Arrow/NumPy to versions supported by the selected Spark release rather than blindly installing the newest versions. Spark 3.x and 4.x differ in runtime support; consult the versioned installation guide before changing this matrix.

Spark has two similarly named APIs:

- `pyspark.ml`: DataFrame-based API and the primary API for new work.
- `pyspark.mllib`: older RDD-based API, now in maintenance mode.

Do not mix examples from these APIs without checking their types and compatibility.

### 2.3 Create a project

```bash
mkdir -p experiments/01_mllib
cd experiments/01_mllib
uv init --python 3.11
mkdir -p src tests data artifacts
uv add pyspark==3.5.7 "pandas<3" "numpy<2" "pyarrow>=4,<13" scikit-learn lightgbm
uv add --dev pytest ruff
```

`lightgbm` is for the single-machine comparison later. If native LightGBM installation is unavailable on your operating system, keep it as an optional dependency and complete the Spark exercises first. PySpark requires a working Java runtime; verify with `java -version` before launching Spark.

A minimal project layout (the commands above create the directories; create each script from the corresponding code block below):

```text
experiments/01_mllib/
├── pyproject.toml
├── uv.lock
├── data/                  # generated locally; do not commit large raw datasets
├── artifacts/             # saved pipeline models; usually ignored by Git
├── src/
│   ├── generate_data.py
│   ├── train.py
│   ├── score_batch.py
│   └── region_models.py
├── tests/                 # add the boundary/schema tests from Exercise B
└── README.md              # record results produced by your own run
```

For a local learning run, Spark can use `local[*]`. This runs Spark tasks in one machine and is useful for learning, but it does **not** prove that the workload scales across a cluster. Cluster deployment, executor sizing, credentials, and object-store paths are environment-specific.

### 2.4 Start Spark and check it

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("distributed-ml-mllib-lesson")
    .config("spark.sql.session.timeZone", "UTC")
    .master("local[*]")  # local learning only; omit/configure in a cluster
    .config("spark.sql.shuffle.partitions", "8")
    .getOrCreate()
)

print(spark.version)
spark.range(5).show()
```

Expected shape: Spark prints its installed version and a five-row DataFrame containing values `0` through `4`. Do not hard-code `local[*]` in a cluster job; let the platform submit the application with its cluster configuration.

## 3. The machine-learning workflow

A model is only one component in a larger data workflow:

```text
source data
    ↓
validate schema, freshness, and labels
    ↓
construct point-in-time-correct features
    ↓
split into train / validation / test
    ↓
fit preprocessing + model on training data
    ↓
select configuration using validation data
    ↓
final one-time evaluation on test data
    ↓
save model + metadata
    ↓
score new records and validate predictions
```

### 3.1 What is a feature and what is a label?

A **feature** is an input available to the model at prediction time. A **label** (target) is the outcome the model is learning to predict. For churn prediction, an entity might be a customer; the label might be whether that customer cancels within the next 30 days; and features might include the number of support contacts in the previous 30 days.

Always define the **prediction time**. If the system predicts churn on 1 July, it must not use a cancellation event or account status that only became known on 10 July. This is the core of point-in-time correctness, explored more deeply in Topic 02.

### 3.2 Supervised and unsupervised learning

| Task | Target available during training? | Example | Common metric |
|---|---|---|---|
| Binary classification | Yes; two classes | Will a customer churn? | ROC AUC, PR AUC, precision, recall, log loss |
| Multiclass classification | Yes; more than two classes | Which support category will a ticket enter? | Macro F1, per-class recall, log loss |
| Regression | Yes; numeric value | What will next month's spend be? | RMSE, MAE, sometimes R² |
| Clustering | No target label is required | Group customers by behavioral similarity | Silhouette score plus domain validation |
| Collaborative filtering | Implicit/explicit user-item interactions | Recommend products to users | Ranking metrics such as MAP/NDCG, plus offline and online tests |

Metric choice depends on how predictions are used. A fraud model that misses costly fraud may need high recall at an acceptable false-positive rate; a delivery-time model may care more about absolute error than squared error. A clustering score alone cannot establish that clusters are useful to a business.

### 3.3 Generalization and overfitting

**Generalization** means performing well on future, unseen examples drawn from the deployment population. **Overfitting** occurs when a model captures quirks or noise in training data that do not persist in new data. A high training score paired with a substantially worse validation score is a warning, not proof by itself.

Reduce overfitting through a defensible split, simpler models, regularization, sensible feature selection, enough representative data, and validation-guided model selection. Do not keep tuning against the test set: after repeated decisions based on test results, it is no longer an unbiased final estimate.

## 4. Splitting data, temporal integrity, and leakage

### 4.1 Train, validation, and test

- **Training set:** fits model parameters and learned preprocessing state.
- **Validation set:** compares models and hyperparameters, selects thresholds, and supports model decisions.
- **Test set:** held back until decisions are complete; estimates performance on unseen data.

Every learned preprocessing stage—such as an imputer, category indexer, scaler, or IDF model—must be fitted using training data only. Putting learned preprocessing inside a `Pipeline` helps enforce this rule because `Pipeline.fit(train)` fits the stages in order on the training DataFrame.

### 4.2 Why temporal data needs time-based splits

With event streams, churn, fraud, demand, and other time-dependent tasks, random splitting can put future behavior in training while earlier records appear in test. That can exaggerate performance because the model is evaluated under a different information boundary than production. For customer-level tasks, also consider whether the same customer appears across splits; entity leakage may remain even when timestamps are sorted.

A split should mirror deployment. For example:

- Train on prediction dates 1 January–10 March.
- Validate on 11–25 March.
- Test on 26 March–10 April.

The exact boundaries depend on label horizon and business cadence. If the label is “churn in the next 30 days,” ensure labels are mature before assigning the record to a split. Otherwise recent rows may be incorrectly labeled negative simply because the outcome has not arrived yet.

### 4.3 Leakage examples

| Leakage source | Why it is invalid | Safer alternative |
|---|---|---|
| `days_since_cancellation` used to predict cancellation | The feature directly encodes the outcome | Use only events available at prediction time |
| Fit an imputer/scaler/indexer on all rows before splitting | Validation/test distribution influences learned preprocessing | Put the stage inside a pipeline and fit on training rows |
| Randomly split future and past observations | Future patterns can leak into model selection | Use chronological holdouts or rolling-origin validation |
| Same customer/session duplicated across splits | Near-duplicates inflate evaluation | Group split by entity or deduplicate before splitting |
| Label window overlaps the split boundary | Outcome may not be known at the simulated prediction date | Define prediction and label windows explicitly; apply a gap/purge if required |

### 4.4 Small split example

Assume `prediction_ts` represents the time at which the prediction would have been made. Define split boundaries before inspecting test performance:

```python
from pyspark.sql import functions as F

train = df.where(F.col("prediction_ts") < F.lit("2025-03-11"))
valid = df.where(
    (F.col("prediction_ts") >= F.lit("2025-03-11"))
    & (F.col("prediction_ts") < F.lit("2025-03-26"))
)
test = df.where(
    (F.col("prediction_ts") >= F.lit("2025-03-26"))
    & (F.col("prediction_ts") < F.lit("2025-04-11"))
)

assert train.count() > 0 and valid.count() > 0 and test.count() > 0
assert train.agg(F.max("prediction_ts")).first()[0] < valid.agg(F.min("prediction_ts")).first()[0]
assert valid.agg(F.max("prediction_ts")).first()[0] < test.agg(F.min("prediction_ts")).first()[0]
```

This example uses timestamp/date strings that Spark can compare as ISO dates. In production, use a consistent timestamp type and timezone, and test boundary conditions explicitly. Counts trigger Spark jobs; avoid repeated full scans in a large pipeline by persisting validated counts/metrics or using a single aggregation when practical.

## 5. Distributed ML or single-machine ML?

Distribution is an engineering choice, not a badge of sophistication. Spark helps when data and feature preparation already live in a distributed lakehouse, data cannot fit comfortably on one machine, or a distributed pipeline reduces data movement. It may be unnecessary or slower for a small tabular dataset because scheduling, serialization, shuffles, JVM/Python boundaries, and cluster startup have costs.

### 5.1 Decision factors

| Factor | Spark/distributed approach is attractive when… | Single-machine approach is attractive when… |
|---|---|---|
| Data volume | The data exceeds one machine's practical RAM/disk or processing window | A representative dataset fits comfortably in memory or streams efficiently |
| Data locality | Data already resides in Spark-accessible distributed storage | Data must be copied into a cluster just to train a small model |
| Algorithm | A scalable distributed implementation is available | Strong single-node implementations (e.g. LightGBM/XGBoost) are faster or easier |
| Feature computation | Large joins/aggregations benefit from Spark SQL | Features are simple and already materialized locally |
| Iteration speed | Data prep and training are repeated over large tables | Frequent experimentation on samples dominates |
| Operations | A Spark platform already exists and is well operated | A cluster would add disproportionate deployment and on-call burden |

Do not decide from row count alone. Estimate encoded feature width, sparsity, number of passes/iterations, shuffle volume, executor memory, concurrency, and SLA. A 20-million-row dataset with a handful of columns may behave very differently from 20 million rows with thousands of dense features.

### 5.2 Practical approach

1. Establish a simple baseline on a representative sample.
2. Measure quality, wall-clock time, peak memory, and cost.
3. Profile feature generation and data movement separately from model fitting.
4. Increase data volume gradually and observe the bottleneck.
5. Use distributed training only if it improves a meaningful constraint: completion time, capacity, cost at target volume, or operational reliability.

A sample is useful for code development and initial profiling, but a final model-selection decision must be checked on data representative of the deployment distribution.

## 6. Spark MLlib architecture and the DataFrame API

### 6.1 The four core abstractions

- **DataFrame:** a distributed, schema-bearing collection of rows. Spark SQL plans and executes operations across partitions.
- **Transformer:** implements `transform(dataset)` and returns a DataFrame. Examples include `StringIndexerModel`, `VectorAssembler`, and a fitted classifier model.
- **Estimator:** implements `fit(dataset)` and returns a Transformer/model. Examples include `StringIndexer`, `Imputer`, `StandardScaler`, `IDF`, and `GBTClassifier`.
- **Pipeline:** an Estimator that chains stages. Calling `fit(train)` returns a **`PipelineModel`**, which is a Transformer containing fitted models and transformers in stage order.

A `StringIndexer` is an Estimator because it must learn a mapping from category values to numeric indices. Its fitted `StringIndexerModel` is a Transformer because it applies the learned mapping to new rows. `VectorAssembler` is usually a direct Transformer because it concatenates already available columns into a feature vector without learning statistics from the data. In the examples that set `OneHotEncoder(dropLast=False, handleInvalid="keep")`, an invalid/unseen category has its own active indicator. With Spark's default `dropLast=True`, the invalid category is represented by an all-zero vector; do not assume it has a distinct active indicator unless you configure and test that behavior. Keeping all categories adds a feature dimension and can introduce linear dependence for models with an intercept, so choose the representation deliberately.

### 6.2 What happens during `fit()`

Given a pipeline:

```text
raw columns
  → Imputer (Estimator)
  → StringIndexer (Estimator)
  → OneHotEncoder (Estimator)
  → VectorAssembler (Transformer)
  → GBTClassifier (Estimator)
```

`Pipeline.fit(train)` processes stages in order. When a stage is an Estimator, Spark fits it on the current training DataFrame, gets a fitted model/Transformer, and transforms the DataFrame so later stages can consume the resulting columns. The returned `PipelineModel` contains fitted versions of the Estimators and the Transformer stages.

At scoring time, call `pipeline_model.transform(unseen_df)`. It applies the stored mappings/statistics/model; it does not refit them. This makes the training and inference preprocessing path consistent and is a core defense against training-serving skew.

### 6.3 How Spark distributes work

A DataFrame is logically represented by a query plan and physically processed as tasks over partitions. Executors run tasks; the driver coordinates planning and scheduling. Operations such as filters and many column transformations can be pipelined. Operations that require data to be redistributed by key—such as joins, aggregations, repartitioning, and some model-training steps—can trigger a **shuffle**, which writes and transfers intermediate data across executors.

Not every ML algorithm scales equally. Some model fitting work is iterative, and repeated passes over data can make caching useful. A distributed algorithm can still be limited by a large shuffle, skewed partitions, model synchronization, or driver-side metadata.

### 6.4 Minimal pipeline example

```python
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.classification import LogisticRegression

region_indexer = StringIndexer(
    inputCol="region", outputCol="region_idx", handleInvalid="keep"
)
encoder = OneHotEncoder(
    inputCols=["region_idx"], outputCols=["region_vec"],
    handleInvalid="keep", dropLast=False,
)
assembler = VectorAssembler(
    inputCols=["tenure_months", "monthly_spend", "region_vec"],
    outputCol="features",
    handleInvalid="error",
)
classifier = LogisticRegression(featuresCol="features", labelCol="label")

pipeline = Pipeline(stages=[region_indexer, encoder, assembler, classifier])
model = pipeline.fit(train_df)
scored = model.transform(validation_df)
scored.select("label", "probability", "prediction").show(truncate=False)
```

This is a structural example: `train_df` must contain the referenced columns, a numeric label, and no nulls that the assembler cannot handle. The production example below includes explicit imputation and a chronological split.

## 7. Feature transformers: purpose, behavior, and failure modes

Transformers convert raw columns into model-compatible representations. Some are direct Transformers; others are Estimators whose fitted state must be learned from training data. In practice, inspect each API's documentation and input/output schema.

| Component | Type | Input → output | Use it when… | Common mistake |
|---|---|---|---|---|
| `StringIndexer` | Estimator → `StringIndexerModel` | String/category → numeric index | A categorical field must be indexed | Fitting on all data; forgetting unseen categories; treating arbitrary index numbers as meaningful order |
| `OneHotEncoder` | Estimator → model | Indexed category → sparse binary vector | Categories should not imply a numeric order | Not indexing strings first; misinterpreting all-zero/drop-last representation; failing to plan for unseen categories |
| `VectorAssembler` | Transformer | Several numeric/vector columns → one ML vector | An algorithm expects one `features` vector | Passing strings or unhandled nulls; accidentally including label, ID, or future-derived columns |
| `StandardScaler` | Estimator → model | Vector → standardized vector | Scale-sensitive algorithms benefit from comparable scales | Fitting before splitting; assuming trees always need scaling; forgetting zero-variance or sparse-vector trade-offs |
| `Imputer` | Estimator → model | Numeric columns with nulls → imputed numeric columns | Numeric missing values need a defined treatment | Imputing sentinel values such as `-999` as if they were null; not tracking missingness where it is informative |
| `Bucketizer` | Transformer | Numeric scalar → bucket index | Thresholds have business meaning or nonlinear bins are useful | Incorrect split boundaries; not defining handling for out-of-range values; treating bucket IDs as continuous distances |
| `Tokenizer` | Transformer | Text → array of tokens | Basic whitespace tokenization is adequate | Expecting sophisticated language normalization; forgetting punctuation/case/stop-word policy |
| `HashingTF` | Transformer | Tokens → sparse term-frequency vector | Fixed-dimensional text features are needed without a vocabulary fit | Hash collisions; unsuitable `numFeatures`; forgetting consistent tokenization |
| `IDF` | Estimator → model | Term-frequency vector → TF-IDF vector | Common words should be downweighted relative to informative terms | Fitting IDF on validation/test or future corpus; using IDF with incompatible vector dimensions |

### 7.1 Categorical data: index then encode

`StringIndexer` maps categories to indices. By default, category ordering is frequency-based; therefore the numeric index is a code, not a rank. Set `handleInvalid="keep"` when a previously unseen or null category should map to an extra index instead of failing. Confirm exact behavior for your Spark version.

`OneHotEncoder` transforms indexed categories into sparse vectors. It is often paired with `StringIndexer`. `dropLast` affects the representation; do not assume the vector has one slot per category. The fitted mapping and encoding model must be reused at inference time.

### 7.2 Numeric data: impute, optionally scale, assemble

`Imputer` learns replacement statistics such as mean or median from the data passed to `fit`. Put it inside the pipeline and fit on training data only. Spark's `Imputer` handles numeric columns; it is not a universal imputer for strings or nested values.

`StandardScaler` learns vector statistics and can scale to unit standard deviation and optionally center. Centering sparse vectors can make them dense, increasing memory use substantially. Tree-based models such as random forests and gradient-boosted trees generally do not require standardization; linear models and distance-based methods may benefit from it.

`VectorAssembler` combines numeric columns and existing vector columns into a single ML vector. Its `handleInvalid` policy should be deliberate. In this lesson, missing numeric values are imputed first and invalid assembled values are configured to error so unexpected bad data fails visibly.

### 7.3 Bucketizer

`Bucketizer` uses an ordered array of numeric split points to assign values to buckets. For example, splits `[-inf, 0, 10, 30, inf]` define four intervals. Use explicit splits based on domain thresholds or a documented quantile process. Verify how boundary values are assigned and how out-of-range values are handled in the installed version. Do not confuse a bucket index with a measured quantity.

```python
from pyspark.ml.feature import Bucketizer

bucketizer = Bucketizer(
    inputCol="days_past_due", outputCol="days_past_due_bucket",
    splits=[float("-inf"), 0.0, 10.0, 30.0, float("inf")],
    handleInvalid="keep",
)
bucketed = bucketizer.transform(account_df)
bucketed.select("days_past_due", "days_past_due_bucket").show(10)
```

This is a direct Transformer, so it does not learn cut points during `fit()`. If quantile-derived boundaries are desired, calculate them from the training period only, version the boundaries, and then apply them unchanged to validation, test, and scoring data.

### 7.4 Text: Tokenizer, HashingTF, and IDF

A simple text pipeline can tokenize text, optionally remove stop words, convert tokens into a fixed-size sparse term-frequency vector with `HashingTF`, then fit `IDF` to downweight terms common across the training corpus. `HashingTF` is a Transformer; `IDF` is an Estimator because it estimates document frequencies. Keep the tokenization and hashing configuration stable between training and serving. Hash collisions are expected; larger feature dimensions reduce but do not eliminate them.

```python
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, HashingTF, IDF

text_pipeline = Pipeline(stages=[
    Tokenizer(inputCol="comment", outputCol="tokens"),
    HashingTF(inputCol="tokens", outputCol="tf", numFeatures=1 << 16),
    IDF(inputCol="tf", outputCol="tfidf"),
])
text_model = text_pipeline.fit(train_text_df)  # fit only on training corpus
text_features = text_model.transform(new_text_df)
```

For production text systems, define a text normalization policy, language expectations, stop-word policy, privacy controls, and a plan for monitoring vocabulary/feature changes. This basic tokenizer is not a substitute for a language-specific NLP pipeline.

## 8. Algorithms and when to use them

Spark MLlib provides common estimators, but algorithm availability, constraints, and parameters vary by class and Spark release. Check the versioned API docs for exact behavior.

| Algorithm | Problem | Target/features | Strengths | Limitations and metrics |
|---|---|---|---|---|
| `LogisticRegression` | Binary or multiclass classification (depending on configuration) | Numeric label and feature vector | Interpretable baseline, probability estimates, regularization | Linear decision boundary; assess ROC/PR AUC, log loss, precision/recall and calibration |
| `LinearRegression` | Regression | Numeric label and feature vector | Simple baseline, coefficients can be inspected | Linear assumptions and outlier sensitivity; assess RMSE/MAE and residuals |
| `RandomForestClassifier` / `RandomForestRegressor` | Classification/regression | Numeric feature vector | Nonlinear relationships, robust baseline, feature interactions | Larger models and training cost; no extrapolation guarantee; classification metrics or RMSE/MAE |
| `GBTClassifier` / `GBTRegressor` | Gradient-boosted trees | Numeric feature vector | Strong tabular baseline, captures nonlinearities | More tuning, sequential boosting cost; Spark's `GBTClassifier` is for binary classification in Spark 3.5.x; inspect API restrictions |
| `KMeans` | Clustering | Numeric feature vector; no target required | Scalable partition-based clustering | Sensitive to scale, initialization, and chosen K; use silhouette/domain review rather than classification metrics |
| `ALS` | Collaborative filtering/recommendation | User ID, item ID, rating/interaction | Factorizes user-item interactions; supports implicit feedback modes | Cold-start handling, sparse interactions, ID/type requirements; evaluate ranking or rating quality and online impact |

### 8.1 Minimal ALS recommendation example

ALS expects interaction rows with integer-range user and item identifiers plus a numeric rating/strength column; non-integer numeric IDs can be cast to integers and must fit the supported range, so validate identifiers before fitting. Split interactions according to the intended deployment scenario (often by interaction time), not by randomly mixing future interactions into training. This small example assumes `train_interactions` and `test_interactions` have already been prepared with columns `user_id`, `item_id`, and `rating` and that IDs are numeric as required by Spark ALS.

```python
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator

als = ALS(
    userCol="user_id", itemCol="item_id", ratingCol="rating",
    rank=20, maxIter=10, regParam=0.1,
    coldStartStrategy="drop", seed=2025,
)
als_model = als.fit(train_interactions)
als_predictions = als_model.transform(test_interactions)
rmse = RegressionEvaluator(
    labelCol="rating", predictionCol="prediction", metricName="rmse"
).evaluate(als_predictions)
print("ALS test RMSE on scorable interactions:", round(rmse, 4))
```

`coldStartStrategy="drop"` avoids null predictions for users/items unseen during fitting by excluding those rows from this evaluation; report how many rows were dropped because that changes the evaluation population. For recommendation ranking, RMSE may not match the product objective; evaluate ranking metrics such as Recall@K/NDCG@K and, where possible, run online experiments. Do not treat this snippet as a complete recommender evaluation protocol.

### 8.2 Why start with a baseline?

A baseline provides a reference point. For churn, compare the model against a majority-class predictor and a simple rule or logistic regression. For a highly imbalanced label, an always-negative model may have high accuracy but zero recall on churners. Record metrics by important slices (region, customer tenure, acquisition channel) so aggregate scores do not hide failures.

### 8.3 Probability calibration and thresholds

A classifier's predicted probability is not automatically a calibrated estimate. Calibration asks whether examples assigned probability near 0.8 experience the outcome about 80% of the time. Threshold selection depends on the costs of false positives and false negatives; the default threshold of 0.5 is not universally optimal. Choose thresholds on validation data, document the cost assumptions, and do not tune them on the test set.

## 9. Evaluation metrics and model selection

### 9.1 Metrics

- **ROC AUC:** ranks positives above negatives across thresholds; can look reassuring with severe class imbalance.
- **PR AUC / area under precision-recall curve:** often more informative when positives are rare. Spark's built-in evaluator support differs by metric and version; check the API and compute additional metrics when needed.
- **Precision:** among predicted positives, the fraction truly positive. High precision limits unnecessary interventions.
- **Recall:** among actual positives, the fraction found. High recall matters when missing positives is costly.
- **Accuracy:** fraction of all predictions correct. Misleading when the majority class dominates.
- **RMSE:** square root of mean squared error; penalizes large errors more heavily than MAE and is in the target's units.
- **MAE:** mean absolute error; easier to interpret and less sensitive to extreme errors than RMSE.
- **Log loss:** evaluates probabilistic predictions and strongly penalizes confident wrong predictions.
- **Silhouette score:** one possible clustering diagnostic; it does not establish business usefulness.

### 9.2 Spark evaluators

`BinaryClassificationEvaluator` commonly evaluates binary-classification ranking metrics such as `areaUnderROC` and `areaUnderPR` in supported Spark versions. `MulticlassClassificationEvaluator` supports metrics such as accuracy, weighted precision/recall/F1, and log loss depending on version and configuration. For RMSE, use `RegressionEvaluator(metricName="rmse")`.

```python
from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator,
    MulticlassClassificationEvaluator,
    RegressionEvaluator,
)

roc_auc = BinaryClassificationEvaluator(
    labelCol="label", rawPredictionCol="rawPrediction", metricName="areaUnderROC"
)
auc_value = roc_auc.evaluate(scored_validation)

f1 = MulticlassClassificationEvaluator(
    labelCol="label", predictionCol="prediction", metricName="f1"
)
f1_value = f1.evaluate(scored_validation)

rmse = RegressionEvaluator(
    labelCol="label", predictionCol="prediction", metricName="rmse"
)
rmse_value = rmse.evaluate(scored_regression)
```

AUC and F1 answer different questions. If you need a precision/recall point at a chosen threshold, calculate it from predictions and the chosen threshold or use a suitable metric utility. Do not treat a single aggregate metric as sufficient for production acceptance.

### 9.3 `ParamGridBuilder` and cross-validation

`ParamGridBuilder` constructs parameter combinations. `CrossValidator` evaluates combinations across folds and selects a configuration according to an evaluator. This can be expensive: with 3 parameter settings and 5 folds, the pipeline may require roughly 15 fits, plus overhead. If a pipeline includes a costly feature fit, the cost compounds.

**Temporal caution:** ordinary Spark `CrossValidator` creates folds without understanding your prediction timeline. Random folds can violate chronology. For temporal prediction, prefer an explicit rolling-origin/expanding-window evaluation loop with earlier training windows and later validation windows. Use built-in cross-validation when the data are reasonably IID or when the fold assignment is demonstrably valid for the task. If using a random CV example to learn the API, do not mistake it for a production-safe temporal evaluation.

```python
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.classification import LogisticRegression

lr = LogisticRegression(featuresCol="features", labelCol="label")
grid = (
    ParamGridBuilder()
    .addGrid(lr.regParam, [0.01, 0.1])
    .addGrid(lr.elasticNetParam, [0.0, 0.5])
    .build()
)

# Illustrative for IID data only. Do not use random folds blindly for temporal data.
cv = CrossValidator(
    estimator=lr,
    estimatorParamMaps=grid,
    evaluator=BinaryClassificationEvaluator(metricName="areaUnderROC"),
    numFolds=3,
    parallelism=2,
    seed=42,
)
cv_model = cv.fit(iid_training_df)
```

For the temporal churn example below, we use a small explicit grid and validation period. This is easier to reason about and keeps the final test period isolated. For larger grids, implement a reusable rolling-window tuner or use a platform that supports time-aware validation, while preserving the same temporal contract.

## 10. Complete end-to-end PySpark implementation

This section creates a small, reproducible synthetic churn dataset, defines time-based splits, builds an MLlib pipeline, performs validation-based tuning, evaluates once on the test period, and persists the fitted pipeline. The dataset is synthetic and intended to demonstrate the workflow; it is not evidence of real-world model quality.

### 10.1 Generate timestamped data

```python
# src/generate_data.py
from datetime import datetime, timedelta, timezone
import random

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, TimestampType,
    IntegerType, DoubleType,
)

SEED = 2025
N_ROWS = 20_000
START = datetime(2025, 1, 1, tzinfo=timezone.utc)

spark = (
    SparkSession.builder.appName("generate-churn-data")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)
rng = random.Random(SEED)
regions = ["north", "south", "east", "west"]
rows = []

for i in range(N_ROWS):
    prediction_ts = START + timedelta(days=i % 120, seconds=(i * 137) % 86400)
    tenure = max(0, min(120, int(rng.gauss(30, 18))))
    spend = max(5.0, rng.gauss(65.0, 22.0))
    support = max(0, int(rng.expovariate(1 / 1.8)))
    region = regions[(i // 7) % len(regions)]

    # Label probability is deliberately synthetic; later dates introduce mild drift.
    time_shift = 0.35 if prediction_ts.day >= 20 and prediction_ts.month >= 3 else 0.0
    logit = -1.5 - 0.018 * tenure + 0.012 * spend + 0.42 * support + time_shift
    probability = 1.0 / (1.0 + pow(2.718281828, -logit))
    label = int(rng.random() < probability)

    # Missing values exercise Imputer; categories remain strings.
    if rng.random() < 0.03:
        spend_value = None
    else:
        spend_value = float(round(spend, 2))
    if rng.random() < 0.02:
        support_value = None
    else:
        support_value = support

    rows.append((
        f"customer_{i:06d}", prediction_ts.replace(tzinfo=None), tenure,
        spend_value, support_value, region, label,
    ))

schema = StructType([
    StructField("customer_id", StringType(), False),
    StructField("prediction_ts", TimestampType(), False),
    StructField("tenure_months", IntegerType(), True),
    StructField("monthly_spend", DoubleType(), True),
    StructField("support_contacts_30d", IntegerType(), True),
    StructField("region", StringType(), True),
    StructField("label", IntegerType(), False),
])

df = spark.createDataFrame(rows, schema=schema)
# Store locally for repeatable practice. On a cluster, use a durable table/object-store URI.
df.write.mode("overwrite").parquet("data/churn.parquet")
print("Rows:", df.count())
df.printSchema()
spark.stop()
```

Run it from the project root:

```bash
uv run python src/generate_data.py
```

The generator's label is intentionally simple. The timestamp generation spans 120 days by construction. The generator creates UTC timestamps and removes timezone metadata before constructing Spark's `TimestampType` rows; every Spark session in these examples therefore sets `spark.sql.session.timeZone=UTC`. Keep the same UTC contract when writing and reading Parquet or converting timestamps in pandas. Production systems should preserve explicit timezone semantics at ingestion boundaries.

### 10.2 Load, validate, and split

```python
# src/train.py
from pyspark.sql import SparkSession, functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import Imputer, StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.classification import GBTClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.functions import vector_to_array

spark = (
    SparkSession.builder.appName("churn-mllib-training")
    .config("spark.sql.session.timeZone", "UTC")
    .config("spark.sql.shuffle.partitions", "8")
    .getOrCreate()
)

source = spark.read.parquet("data/churn.parquet")
required = {
    "customer_id", "prediction_ts", "tenure_months", "monthly_spend",
    "support_contacts_30d", "region", "label",
}
missing = required - set(source.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")
expected_types = {
    "customer_id": "string", "prediction_ts": "timestamp",
    "tenure_months": "int", "monthly_spend": "double",
    "support_contacts_30d": "int", "region": "string", "label": "int",
}
actual_types = {field.name: field.dataType.simpleString() for field in source.schema.fields}
type_errors = {
    name: {"expected": expected, "actual": actual_types.get(name)}
    for name, expected in expected_types.items()
    if actual_types.get(name) != expected
}
if type_errors:
    raise TypeError(f"Unexpected input schema types: {type_errors}")

# Fail fast on invalid labels and null identifiers/timestamps.
if source.where(F.col("label").isNull() | ~F.col("label").isin(0, 1)).limit(1).count():
    raise ValueError("label must be non-null and in {0, 1}")
if source.where(F.col("customer_id").isNull() | F.col("prediction_ts").isNull()).limit(1).count():
    raise ValueError("customer_id and prediction_ts must be non-null")

# Explicit chronological windows; use half-open intervals to avoid boundary ambiguity.
train = source.where(F.col("prediction_ts") < F.to_timestamp(F.lit("2025-03-12 00:00:00")))
valid = source.where(
    (F.col("prediction_ts") >= F.to_timestamp(F.lit("2025-03-12 00:00:00")))
    & (F.col("prediction_ts") < F.to_timestamp(F.lit("2025-03-27 00:00:00")))
)
test = source.where(
    (F.col("prediction_ts") >= F.to_timestamp(F.lit("2025-03-27 00:00:00")))
    & (F.col("prediction_ts") < F.to_timestamp(F.lit("2025-04-11 00:00:00")))
)

counts = {name: part.count() for name, part in [("train", train), ("valid", valid), ("test", test)]}
print("Split row counts:", counts)
for split_name, split_df in [("train", train), ("validation", valid), ("test", test)]:
    print(f"{split_name} label counts:")
    split_df.groupBy("label").count().orderBy("label").show()
if any(value == 0 for value in counts.values()):
    raise ValueError(f"At least one split is empty: {counts}")

# Verify time order without collecting the dataset to the driver.
train_max = train.agg(F.max("prediction_ts")).first()[0]
valid_min = valid.agg(F.min("prediction_ts")).first()[0]
valid_max = valid.agg(F.max("prediction_ts")).first()[0]
test_min = test.agg(F.min("prediction_ts")).first()[0]
assert train_max < valid_min, (train_max, valid_min)
assert valid_max < test_min, (valid_max, test_min)

numeric_inputs = ["tenure_months", "monthly_spend", "support_contacts_30d"]
numeric_outputs = ["tenure_months_imp", "monthly_spend_imp", "support_contacts_30d_imp"]
imputer = Imputer(
    inputCols=numeric_inputs,
    outputCols=numeric_outputs,
    strategy="median",
)
region_indexer = StringIndexer(
    inputCol="region", outputCol="region_idx", handleInvalid="keep"
)
encoder = OneHotEncoder(
    inputCols=["region_idx"], outputCols=["region_vec"],
    handleInvalid="keep", dropLast=False,
)
assembler = VectorAssembler(
    inputCols=numeric_outputs + ["region_vec"],
    outputCol="features",
    handleInvalid="error",
)

pipeline = Pipeline(stages=[
    imputer,
    region_indexer,
    encoder,
    assembler,
    GBTClassifier(
        labelCol="label", featuresCol="features", maxIter=30,
        maxDepth=4, seed=2025,
    ),
])

evaluator = BinaryClassificationEvaluator(
    labelCol="label", rawPredictionCol="rawPrediction", metricName="areaUnderROC"
)

# Small, explicit validation search. Each candidate is fit on train only and
# evaluated on the later validation window. The test window is untouched here.
candidates = [
    {"maxIter": 20, "maxDepth": 3},
    {"maxIter": 30, "maxDepth": 4},
    {"maxIter": 40, "maxDepth": 5},
]
results = []
for candidate in candidates:
    candidate_pipeline = Pipeline(stages=[
        imputer, region_indexer, encoder, assembler,
        GBTClassifier(
            labelCol="label", featuresCol="features",
            maxIter=candidate["maxIter"], maxDepth=candidate["maxDepth"], seed=2025,
        ),
    ])
    candidate_model = candidate_pipeline.fit(train)
    validation_scored = candidate_model.transform(valid)
    score = evaluator.evaluate(validation_scored)
    results.append((score, candidate, candidate_model))
    print(f"candidate={candidate}, validation ROC AUC={score:.4f}")

best_score, best_params, best_model = max(results, key=lambda item: item[0])
print("Selected params:", best_params, "validation ROC AUC:", round(best_score, 4))

# Illustrative business-cost threshold selection: false negatives cost 5 units,
# false positives cost 1 unit. Replace these assumptions with approved business costs.
FP_COST, FN_COST = 1.0, 5.0

def threshold_metrics(scored_df, threshold):
    positive_score = vector_to_array(F.col("probability"))[1]
    predicted_positive = positive_score >= F.lit(float(threshold))
    row = scored_df.agg(
        F.sum(F.when((F.col("label") == 1) & predicted_positive, 1).otherwise(0)).alias("tp"),
        F.sum(F.when((F.col("label") == 0) & predicted_positive, 1).otherwise(0)).alias("fp"),
        F.sum(F.when((F.col("label") == 1) & (~predicted_positive), 1).otherwise(0)).alias("fn"),
        F.sum(F.when((F.col("label") == 0) & (~predicted_positive), 1).otherwise(0)).alias("tn"),
    ).first()
    tp, fp, fn, tn = (int(row[k] or 0) for k in ("tp", "fp", "fn", "tn"))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "threshold": float(threshold), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": precision, "recall": recall,
        "illustrative_cost": FP_COST * fp + FN_COST * fn,
    }

# Threshold selection uses validation only. Never select it using test outcomes.
best_validation_scored = best_model.transform(valid)
threshold_candidates = [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]
validation_threshold_results = [
    threshold_metrics(best_validation_scored, threshold)
    for threshold in threshold_candidates
]
best_threshold_metrics = min(
    validation_threshold_results, key=lambda item: item["illustrative_cost"]
)
best_threshold = best_threshold_metrics["threshold"]
print("Validation-selected threshold metrics:", best_threshold_metrics)

# Evaluate on the held-out test period only after model and threshold selection;
# do not revise either choice in response to these results.
test_scored = best_model.transform(test)
test_auc = evaluator.evaluate(test_scored)
print("Final test ROC AUC:", round(test_auc, 4))
print("Final test threshold metrics:", threshold_metrics(test_scored, best_threshold))

# A simple majority-class baseline fitted from training labels only.
majority_row = train.groupBy("label").count().orderBy(F.desc("count"), F.asc("label")).first()
majority_label = int(majority_row["label"])
majority_test = test.withColumn("baseline_prediction", F.lit(float(majority_label)))
baseline_stats = majority_test.agg(
    F.avg((F.col("baseline_prediction") == F.col("label")).cast("double")).alias("accuracy"),
    F.sum(F.when((F.col("label") == 1) & (F.col("baseline_prediction") == 1), 1).otherwise(0)).alias("tp"),
    F.sum(F.when((F.col("label") == 0) & (F.col("baseline_prediction") == 1), 1).otherwise(0)).alias("fp"),
    F.sum(F.when(F.col("label") == 1, 1).otherwise(0)).alias("actual_positive"),
).first()
baseline_tp, baseline_fp = int(baseline_stats["tp"] or 0), int(baseline_stats["fp"] or 0)
baseline_actual_positive = int(baseline_stats["actual_positive"] or 0)
print("Majority-class test baseline:", {
    "predicted_label": majority_label,
    "accuracy": float(baseline_stats["accuracy"] or 0.0),
    "precision": baseline_tp / (baseline_tp + baseline_fp) if baseline_tp + baseline_fp else 0.0,
    "recall": baseline_tp / baseline_actual_positive if baseline_actual_positive else 0.0,
})

# Basic output contract checks.
expected_prediction_columns = {"prediction", "probability", "rawPrediction", "features"}
missing_prediction_columns = expected_prediction_columns - set(test_scored.columns)
if missing_prediction_columns:
    raise ValueError(f"Scoring output missing columns: {sorted(missing_prediction_columns)}")
if test_scored.where(F.col("prediction").isNull()).limit(1).count():
    raise ValueError("Scoring generated null predictions")

model_path = "artifacts/churn-pipeline-model"
best_model.write().overwrite().save(model_path)
print("Saved PipelineModel to", model_path)

# Optional: persist predictions with the model path/version and scoring time.
(
    test_scored
    .withColumn("model_artifact", F.lit(model_path))
    .withColumn("scored_at", F.current_timestamp())
    .select("customer_id", "prediction_ts", "label", "prediction", "probability", "model_artifact", "scored_at")
    .write.mode("overwrite").parquet("artifacts/test-predictions")
)
spark.stop()
```

Run:

```bash
uv run python src/train.py
```

The script prints split counts, per-split label counts, each candidate's validation AUC, selected parameters, validation-selected threshold metrics, the majority-class baseline, final test AUC, test threshold metrics, and the model path. **These are expected output fields, not precomputed benchmark claims.** Actual metric values depend on the runtime and generated data; do not copy a value into a report unless your own run produced it. The false-positive/false-negative cost ratio is illustrative and must be replaced with a documented business assumption before it guides a real decision.

**Implementation notes:**

- The input script checks required column names and Spark data types before training. The pipeline's learned imputer, indexer, encoder, and classifier are fit only on `train` for each candidate.
- The validation window selects the hyperparameters; the test window is not used until selection is complete.
- The model's learned category mapping is reused when scoring future data; the scoring script validates required output columns and their expected types before writing.
- The generator's synthetic label formula is intentionally simplistic and not a claim about real churn behavior.
- In a real churn dataset, define the label horizon and ensure labels are fully observed before evaluation. A fixed date split alone cannot repair immature labels or a leaky source table.

### 10.3 Save, reload in a fresh session, and score a new batch

```python
# src/score_batch.py
from pyspark.sql import SparkSession, functions as F
from pyspark.ml import PipelineModel

spark = (
    SparkSession.builder.appName("churn-batch-scoring")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)
model = PipelineModel.load("artifacts/churn-pipeline-model")

new_batch = spark.read.parquet("data/churn.parquet").where(
    F.col("prediction_ts") >= F.to_timestamp(F.lit("2025-04-11 00:00:00"))
)

scored = model.transform(new_batch)
required_output = {"customer_id", "prediction_ts", "prediction", "probability"}
missing = required_output - set(scored.columns)
if missing:
    raise ValueError(f"Unexpected scoring schema; missing {sorted(missing)}")
actual_output_types = {field.name: field.dataType.simpleString() for field in scored.schema.fields}
expected_output_types = {
    "customer_id": "string", "prediction_ts": "timestamp",
    "prediction": "double", "probability": "vector",
}
type_errors = {
    name: {"expected": expected, "actual": actual_output_types.get(name)}
    for name, expected in expected_output_types.items()
    if actual_output_types.get(name) != expected
}
if type_errors:
    raise TypeError(f"Unexpected scoring output types: {type_errors}")

bad_predictions = scored.where(
    F.col("prediction").isNull() | ~F.col("prediction").isin(0.0, 1.0)
)
if bad_predictions.limit(1).count():
    raise ValueError("Predictions must be non-null binary values")

(
    scored.select("customer_id", "prediction_ts", "prediction", "probability")
    .withColumn("model_artifact", F.lit("artifacts/churn-pipeline-model"))
    .withColumn("scored_at", F.current_timestamp())
    .write.mode("overwrite").parquet("artifacts/batch-scored")
)
print("Scored rows:", scored.count())
spark.stop()
```

The generator spans 120 days, so records after 11 April provide a small later scoring batch. The records are still synthetic and are not a substitute for a separately collected production batch. **Do not treat training records as new production data merely to make a demo appear successful**; test the contract with independent fixtures that include unseen timestamps and potentially unseen categories.

For a fresh-process test, run `score_batch.py` after `train.py` exits. A production job should write predictions to an idempotent table/partition, attach an immutable model version or artifact digest, and avoid blind `overwrite` of historical production predictions.

## 11. A correct time-aware tuning pattern

For temporal data, ordinary `CrossValidator` is not time-aware. Use expanding-window folds: each validation window occurs strictly after its training window, and later folds may include earlier validation periods in their training history. The final test period must remain outside every fold. The following is an actionable alternative to the single validation-window search in `src/train.py`; run it after `source`, the transformer objects, `GBTClassifier`, and `evaluator` have been defined in that script.

```python
# Rolling/expanding-window cross-validation; all boundaries are UTC and half-open.
fold_windows = [
    ("2025-01-01", "2025-02-01", "2025-02-01", "2025-02-15"),
    ("2025-01-01", "2025-02-15", "2025-02-15", "2025-03-01"),
    ("2025-01-01", "2025-03-01", "2025-03-01", "2025-03-12"),
]
candidates = [
    {"maxIter": 20, "maxDepth": 3},
    {"maxIter": 30, "maxDepth": 4},
    {"maxIter": 40, "maxDepth": 5},
]

def build_pipeline(params):
    return Pipeline(stages=[
        imputer, region_indexer, encoder, assembler,
        GBTClassifier(
            labelCol="label", featuresCol="features",
            maxIter=params["maxIter"], maxDepth=params["maxDepth"], seed=2025,
        ),
    ])

cv_results = []
for candidate in candidates:
    fold_scores = []
    for train_start, train_end, valid_start, valid_end in fold_windows:
        fold_train = source.where(
            (F.col("prediction_ts") >= F.to_timestamp(F.lit(train_start)))
            & (F.col("prediction_ts") < F.to_timestamp(F.lit(train_end)))
        )
        fold_valid = source.where(
            (F.col("prediction_ts") >= F.to_timestamp(F.lit(valid_start)))
            & (F.col("prediction_ts") < F.to_timestamp(F.lit(valid_end)))
        )
        if fold_train.limit(1).count() == 0 or fold_valid.limit(1).count() == 0:
            raise ValueError(f"Empty temporal fold: {train_start}..{train_end} / {valid_start}..{valid_end}")
        fold_model = build_pipeline(candidate).fit(fold_train)
        fold_score = evaluator.evaluate(fold_model.transform(fold_valid))
        fold_scores.append(fold_score)
    mean_score = sum(fold_scores) / len(fold_scores)
    cv_results.append((mean_score, candidate, fold_scores))
    print({"candidate": candidate, "fold_auc": fold_scores, "mean_auc": mean_score})

best_cv_score, best_cv_params, best_cv_fold_scores = max(cv_results, key=lambda item: item[0])
print("Selected temporal-CV params:", best_cv_params, "mean AUC:", round(best_cv_score, 4))
# After selection, refit on the agreed development period that ends before the final test.
# Keep threshold selection on a separate later validation period or use out-of-fold predictions.
```

This example illustrates the temporal CV loop and parameter selection; it does not replace label-maturity checks, gaps/purges needed for overlapping label horizons, class-presence checks in every fold, or experiment tracking. It also intentionally does not evaluate the final test set. Each fold refits learned preprocessing only on that fold's training data. With `P` candidates and `K` folds, budget approximately `P × K` model fits plus Spark job overhead.

## 12. Single-machine LightGBM comparison

LightGBM is a gradient-boosted tree library that can be highly effective on tabular data using one machine. A comparison is meaningful only if both approaches use the same target definition, feature availability, chronological split, and evaluation metric. Do not compare Spark trained on full data against LightGBM trained on a random/easier sample and call the scores equivalent.

The following is a compact template for a prepared **numeric** feature matrix. Categorical encoding and missing-value handling must be fitted on training data only, and the validation/test rows must remain chronologically later. Adapt the feature preparation to the actual source schema before running.

```python
# src/compare_lightgbm.py
import os
import pandas as pd
import lightgbm as lgb
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# This deliberately collects the small lesson dataset to one machine.
# Do not use this loading pattern for data that cannot comfortably fit in RAM.
pdf = pd.read_parquet("data/churn.parquet")
pdf["prediction_ts"] = pd.to_datetime(pdf["prediction_ts"], utc=True)
train_end = pd.Timestamp("2025-03-12", tz="UTC")
valid_end = pd.Timestamp("2025-03-27", tz="UTC")
test_end = pd.Timestamp("2025-04-11", tz="UTC")
train_pdf = pdf[pdf["prediction_ts"] < train_end].copy()
valid_pdf = pdf[(pdf["prediction_ts"] >= train_end) & (pdf["prediction_ts"] < valid_end)].copy()
test_pdf = pdf[(pdf["prediction_ts"] >= valid_end) & (pdf["prediction_ts"] < test_end)].copy()

# Optional early experiment: SAMPLE_FRAC=0.2; set to 1.0 to use all rows
# only when memory and runtime permit. Sampling is done within each split.
sample_frac = float(os.environ.get("SAMPLE_FRAC", "1.0"))
if not 0 < sample_frac <= 1:
    raise ValueError("SAMPLE_FRAC must be in (0, 1]")
if sample_frac < 1:
    train_pdf = train_pdf.sample(frac=sample_frac, random_state=2025)
    valid_pdf = valid_pdf.sample(frac=sample_frac, random_state=2025)
    # Keep test data full for a stable final evaluation unless the data cannot fit.

numeric_cols = ["tenure_months", "monthly_spend", "support_contacts_30d"]
categorical_cols = ["region"]
feature_cols = numeric_cols + categorical_cols

preprocessor = ColumnTransformer(transformers=[
    ("numeric", SimpleImputer(strategy="median"), numeric_cols),
    ("categorical", Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ]), categorical_cols),
])
model = Pipeline(steps=[
    ("preprocess", preprocessor),
    ("classifier", lgb.LGBMClassifier(
        n_estimators=300, learning_rate=0.05, num_leaves=31, random_state=2025,
    )),
])

X_train, y_train = train_pdf[feature_cols], train_pdf["label"].astype(int)
X_valid, y_valid = valid_pdf[feature_cols], valid_pdf["label"].astype(int)
X_test, y_test = test_pdf[feature_cols], test_pdf["label"].astype(int)
model.fit(X_train, y_train)
valid_auc = roc_auc_score(y_valid, model.predict_proba(X_valid)[:, 1])
test_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
print({
    "sample_frac_for_train_validation": sample_frac,
    "train_rows": len(train_pdf),
    "validation_rows": len(valid_pdf),
    "test_rows": len(test_pdf),
    "validation_roc_auc": valid_auc,
    "test_roc_auc": test_auc,
})
```

Run with all data if it comfortably fits in RAM:

```bash
uv run python src/compare_lightgbm.py
```

Or use a smaller training/validation sample for early iteration:

```bash
SAMPLE_FRAC=0.2 uv run python src/compare_lightgbm.py
```

The sample option intentionally samples only train and validation; test remains full for a stable final evaluation. The pipeline fits imputation and encoding on training rows only. This script evaluates one fixed LightGBM configuration rather than selecting hyperparameters on validation; if you tune it, keep the final test period untouched. This script measures a LightGBM workflow; it does not automatically make its feature matrix identical to Spark's encoded vector, so compare task definitions and splits, and document preprocessing differences.

The feature-matrix preparation is explicit in the script. Run on a representative sample first. Attempt full data only if the resulting matrix and training process fit within available RAM and the time/cost budget. If the full matrix cannot fit, compare Spark on full data with LightGBM on a documented sample as a **capacity/quality trade-off**, not a perfectly controlled same-data comparison.

Record at minimum: dataset row count, feature count and representation, split dates, metric, training time, peak memory, machine size, library versions, and estimated cost. Do not invent benchmark numbers.

## 13. Many models at scale with `applyInPandas`

Sometimes the business requires a separate small model per region, store, or product family. `groupBy(...).applyInPandas()` sends each group to a Python function as a pandas DataFrame and combines the returned pandas DataFrames using an explicit Spark schema. It requires a shuffle, and a whole group may be loaded into Python memory. A highly skewed region can therefore cause executor memory failures. Use it only when per-group modeling is genuinely required and group sizes are bounded.

The example below trains a logistic-regression model per region and returns coefficients as rows. Each group must contain both classes and enough records; production code must define a fallback for small/one-class groups.

```python
# src/region_models.py
import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

spark = (
    SparkSession.builder.appName("region-models")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)
df = spark.read.parquet("data/churn.parquet").select(
    "region", "tenure_months", "monthly_spend", "support_contacts_30d", "label"
).dropna()

output_schema = StructType([
    StructField("region", StringType(), False),
    StructField("n_rows", LongType(), False),
    StructField("feature", StringType(), True),
    StructField("coefficient", DoubleType(), True),
    StructField("model_status", StringType(), False),
])
feature_names = ["tenure_months", "monthly_spend", "support_contacts_30d"]

def fit_region(pdf: pd.DataFrame) -> pd.DataFrame:
    region = str(pdf["region"].iloc[0])
    X = pdf[feature_names].astype(float).to_numpy()
    y = pdf["label"].astype(int).to_numpy()
    if len(pdf) < 20 or np.unique(y).size < 2:
        # Emit one explicit status row so an ineligible region is observable.
        return pd.DataFrame({
            "region": [region], "n_rows": [int(len(pdf))],
            "feature": [None], "coefficient": [None],
            "model_status": ["SKIPPED_INSUFFICIENT_DATA_OR_ONE_CLASS"],
        })
    estimator = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=500, random_state=2025),
    )
    estimator.fit(X, y)
    coefficients = estimator.named_steps["logisticregression"].coef_[0]
    return pd.DataFrame({
        "region": [region] * len(feature_names),
        "n_rows": [int(len(pdf))] * len(feature_names),
        "feature": feature_names,
        "coefficient": coefficients.astype(float),
        "model_status": ["FITTED"] * len(feature_names),
    })

coefficients = df.groupBy("region").applyInPandas(fit_region, schema=output_schema)
coefficients.show(truncate=False)
spark.stop()
```

This demonstrates the pattern, not a complete model registry. Ineligible groups emit a status row instead of disappearing silently. Coefficients from independently standardized regional models are not necessarily directly comparable across regions. The example drops missing rows rather than using Spark's fitted imputer; for production, implement a consistent, versioned per-group preprocessing contract and persist each model plus training metadata. For very large groups, consider iterator-based APIs where supported, or avoid per-group pandas fitting altogether.

## 14. Scaling the exercise to 20 million rows

The roadmap asks for an MLlib pipeline on 20 million rows. Do not start with that scale on a laptop. Begin with 20,000 rows to verify schemas, splits, pipeline stages, and scoring. Then scale deliberately:

1. Generate or load a representative dataset in Parquet/Delta/Iceberg rather than constructing tens of millions of Python tuples on the driver.
2. Partition data by a useful filter such as event date; avoid creating thousands of tiny files.
3. Read only required columns and push filters to the data source.
4. Inspect `df.explain("formatted")` and the Spark UI to identify scans, shuffles, spills, and skew.
5. Estimate storage and memory from measured data. Row count alone is insufficient because feature vectors, strings, nullability, and encoding change the footprint.
6. Size executors and shuffle partitions based on cluster resources and observed task duration; do not copy a universal partition count.
7. Run the training job, record duration and executor metrics, and compare against a baseline on the same split.

For synthetic scale testing, prefer Spark-native generation so the driver does not hold every row in Python memory. This snippet is self-contained; it creates a Spark session and stops it after writing:

```python
from pyspark.sql import SparkSession, functions as F

spark = (
    SparkSession.builder.appName("synthetic-20m-capacity-test")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)
N = 20_000_000
large = (
    spark.range(0, N, numPartitions=200)
    .withColumn("tenure_months", (F.rand(seed=1) * 120).cast("int"))
    .withColumn("monthly_spend", F.rand(seed=2) * 200.0)
    .withColumn("support_contacts_30d", (F.rand(seed=3) * 8).cast("int"))
    .withColumn("region", F.element_at(F.array(
        F.lit("north"), F.lit("south"), F.lit("east"), F.lit("west")
    ), (F.rand(seed=4) * 4 + 1).cast("int")))
    .withColumn("label", (F.rand(seed=5) > 0.8).cast("int"))
)
large.write.mode("overwrite").parquet("data/synthetic-20m")
spark.stop()
```

This creates scale-shaped data but not a realistic churn process, temporal label horizon, or drift. For the actual exercise, extend the generator to assign timestamps, labels, and planted drift without collecting all rows to the driver. The code above is a capacity exercise only. It has a deliberate `numPartitions=200` starting point, not a universal recommendation; benchmark alternatives. Ensure the destination has enough storage, and do not run it without understanding the expected disk and compute cost.

## 15. Performance optimization and troubleshooting

### 15.1 Partitions and task sizing

Too few partitions can underutilize a cluster and create oversized tasks. Too many tiny partitions increase scheduling overhead and can create small-file problems. Choose partitioning based on data volume, cluster parallelism, and operation type; validate with task duration and spill metrics. `repartition()` causes a shuffle; `coalesce()` can reduce partitions without a full shuffle in many cases but may create uneven work if used carelessly.

### 15.2 Shuffle and skew

Shuffles redistribute records between executors. Joins, aggregations, repartitioning, and some feature computations can cause expensive network and disk I/O. **Data skew** occurs when a few keys/partitions contain far more data than others, leaving a small number of tasks to dominate job time. Check task-duration distributions and input sizes, not just average runtime. Possible remedies include pre-aggregation, salting appropriate keys, skew-aware joins, filtering invalid hot keys, or changing the grouping/model design. Each remedy changes semantics or adds complexity and must be tested.

### 15.3 Cache only for reuse

Caching/persisting can save repeated computation when the same expensive DataFrame is reused, such as multiple tuning passes. It consumes memory/disk and can worsen performance if used on a one-off intermediate or if the cluster is memory-constrained. Persist only after measuring reuse, materialize intentionally when useful, and unpersist when finished.

### 15.4 Driver and executors

The driver builds plans, coordinates jobs, and tracks metadata. Executors run tasks over partitions. Avoid `collect()` on large DataFrames, building large Python lists on the driver, or returning a giant result from UDFs. `toPandas()` collects data to one machine and is suitable only for bounded results. The `applyInPandas` group function also moves each group into Python memory, so group size and skew matter.

### 15.5 Cross-validation cost

If there are `P` parameter combinations and `K` folds, expect approximately `P × K` model fits, plus overhead. Large grids on full data can be very expensive. Reduce the grid using domain knowledge, use a representative training sample for early elimination, record every experiment, and run final comparisons at the target scale. A sample-based search is a candidate-screening step, not a substitute for evaluating the selected approach on a representative validation period.

### 15.6 Common failures

| Symptom | Likely cause | First diagnostic action |
|---|---|---|
| `IllegalArgumentException` about a missing column | Wrong `inputCol`, `outputCol`, or schema | Print schema and inspect every stage's column names |
| Assembler fails on null/NaN | Imputation or invalid-value policy is incomplete | Count nulls/NaNs per numeric column; check pipeline stage order |
| Unseen category fails at scoring | Indexer invalid policy is not configured | Set and test `handleInvalid`; verify encoder behavior in the installed version |
| Test metric is suspiciously excellent | Leakage, duplicate entities, or random temporal split | Recheck prediction time, label horizon, joins, split boundaries, and duplicated IDs |
| Job is slow despite many executors | Shuffle, skew, disk spill, or iterative fit | Inspect Spark UI stage/task metrics and physical plan |
| One task runs much longer than others | Skew or oversized partition/group | Compare per-task input size and keys; inspect `applyInPandas` group sizes |
| Executor OOM | Oversized partitions, dense vectors, too much cache, or huge group | Reduce per-task memory pressure; inspect vector sparsity and cache usage |
| Driver OOM | `collect()`, `toPandas()`, or large local object creation | Keep data distributed; collect only bounded aggregates |
| Repeated model results differ | Non-deterministic input/order, changing data snapshot, random seed, or library drift | Pin source snapshot, code/environment, parameters, and seeds; compare artifacts |

## 16. Advanced alternatives: know when they fit

This section is awareness-level, as required by the roadmap. The correct choice depends on data layout, algorithm, platform support, and operational maturity.

| Technology | Role | Consider it when… | Important caveat |
|---|---|---|---|
| XGBoost on Spark (`xgboost.spark`) | Distributed boosted trees integrated with Spark DataFrames | Boosted-tree quality/performance is needed and distributed integration is supported | Package, Spark, cluster manager, and version compatibility must be verified; it is not identical to Spark's GBT implementation |
| SynapseML LightGBM | LightGBM integration for supported Spark environments | A distributed LightGBM workflow is desired inside a compatible Spark deployment | Check active maintenance, runtime matrix, and exact algorithm support; it is not the same implementation as Spark `GBTClassifier` |
| LightGBM single-node | Efficient gradient-boosted trees on one machine | Tabular data fits in RAM and single-node performance is strong | Full feature matrix may exceed memory; compare on consistent splits |
| Dask-ML | Python parallel/distributed machine-learning tools around Dask | The data and Python workflow already fit Dask's execution model | Algorithm coverage and scalability vary; not every scikit-learn estimator becomes distributed automatically |
| Ray Train | Distributed training orchestration for supported ML frameworks | Training uses PyTorch, XGBoost, or another supported framework and requires distributed workers | Adds a separate execution/control plane; choose it for a concrete need |
| `applyInPandas` / pandas UDFs | Execute pandas/Python functions on groups or batches | Group-level logic or Python libraries are essential and groups are bounded | Shuffles and Python memory can dominate; do not use as a default replacement for Spark SQL |
| Many-models-at-scale | Train one model per region/store/entity segment | Segments have distinct dynamics and enough data | Model count, cold-start groups, registry overhead, and monitoring can become large |
| TorchDistributor / Horovod | Launch distributed deep-learning training from Spark-connected environments | A deep-learning workload needs multi-worker training | Deep learning training strategy is beyond this lesson; validate GPU/network/runtime compatibility |
| Petastorm / Mosaic Streaming | Feed columnar/lakehouse data to deep-learning training loops | Large Parquet datasets must be read efficiently by training workers | Ecosystem and API support change; assess current compatibility and avoid assuming a universal loader |

Spark is often valuable even when the model itself is trained elsewhere: use Spark to clean, join, and version data, then export a well-defined dataset to the training framework. The handoff contract—schema, timestamp semantics, split definition, feature lineage, and dataset version—is often more important than which library owns the final estimator.

## 17. Hands-on exercise: `experiments/01_mllib/`

Complete the tasks in order and save code, logs, metrics, and a short README. Do not fabricate results; report what your run measured.

### Exercise A — define the prediction task

Write one paragraph that specifies:

- Entity: customer.
- Prediction event/time: when the system scores the customer.
- Label: whether the customer churns within a precisely defined future horizon.
- Feature cutoff: latest timestamp of information available to the prediction.
- Label maturity: when the outcome can be considered final.
- Business action: what happens after a positive prediction and the relative cost of false positives/negatives.

Draw the pipeline stages from raw columns through preprocessing to classifier.

### Exercise B — build and inspect the pipeline

1. Run the small generator and the end-to-end training script.
2. Print the schema and class balance for each split.
3. Confirm all train dates precede validation dates and all validation dates precede test dates.
4. Inspect the fitted stages and the `features` vector size.
5. Add one new category to the scoring data and verify the invalid-category policy behaves as expected.
6. Save, reload in a fresh process, and score an independent batch.

### Exercise C — tuning and metrics

1. Compare the majority-class baseline, logistic regression, and GBT classifier.
2. Record ROC AUC and precision/recall at a validation-selected threshold; include class balance.
3. Try a small hyperparameter grid and estimate fit count/runtime before launching it.
4. Explain why a random `CrossValidator` is not automatically valid for temporal data.
5. Keep the test window isolated until all model/threshold decisions are complete.

### Exercise D — leakage experiment

Create a deliberately leaky feature that is only known after the prediction time. Show how a random split or leaked feature can inflate offline metrics. Remove it, enforce point-in-time feature rules, and evaluate using the chronological split. Record the difference, but do not claim the synthetic magnitude generalizes to production.

### Exercise E — LightGBM comparison

1. Prepare a numeric matrix using train-fitted preprocessing.
2. Run LightGBM on a manageable sample and then on full data only if the matrix fits in RAM.
3. Compare quality, training time, peak memory, and approximate cost.
4. State whether the comparison used identical data and splits; disclose any sample-size difference.

### Exercise F — one model per region

1. Run the `applyInPandas` example.
2. Add a region with too few rows or only one label class.
3. Verify that the group does not silently produce an invalid fitted model.
4. Measure group sizes and explain the OOM risk from skew.
5. Propose how each regional model would be versioned and monitored.

### Exercise G — 20-million-row scale plan

Do not run at scale until the small workflow is correct. Create a short experiment plan listing the cluster resources, storage format, partition strategy, feature dimensions, number of model fits, expected output paths, runtime budget, and stop conditions. Scale in stages and preserve Spark UI / executor metrics as evidence.

## 18. Knowledge-check questions

Answer without copying the lesson verbatim. Then check your answers against the relevant sections.

1. What is the difference between an Estimator and a Transformer? Give one example of each.
2. Why does `Pipeline.fit(train)` help prevent preprocessing leakage?
3. What does `PipelineModel.transform(new_data)` do, and what must it never do?
4. Why can a random split be invalid for a churn model deployed to predict future churn?
5. What is the difference between a feature and a label? Define the feature cutoff for a 30-day churn label.
6. Why might accuracy be a poor metric for a fraud classifier?
7. When would you prefer Spark MLlib over LightGBM on one machine? When would you not?
8. What costs can a shuffle introduce? How can data skew show up in Spark UI metrics?
9. Why should an imputer, `StringIndexer`, and `IDF` be fit only on training data?
10. What is the difference between ROC AUC and recall at a selected threshold?
11. Why is standardizing sparse vectors potentially expensive?
12. What do `ParamGridBuilder` and `CrossValidator` do, and why does standard cross-validation require caution for temporal data?
13. What metadata would you save so a prediction can be reproduced six months later?
14. What can go wrong when using `applyInPandas` for one model per region?
15. How would you prove that a loaded pipeline produces the expected schema and valid predictions on a new batch?

## 19. Completion checklist

Move to Topic 02 only when you can demonstrate the following, not merely recognize the terms.

- [ ] Explain the ML workflow and a time-based split.
- [ ] Build, tune, save, and reload an MLlib pipeline.
- [ ] Decide whether distributed training is needed.
- [ ] Evaluate with metrics that fit the problem, compare a majority baseline, and select any decision threshold on validation data only.

Evidence to keep in `experiments/01_mllib/README.md`:

- Prediction-task definition and feature cutoff.
- Split boundaries, row counts, class balance, and label maturity assumptions.
- Pipeline stage diagram and schema checks.
- Validation-selected parameters and final test metrics from your own run.
- Model artifact path/version and fresh-process reload result.
- Runtime/cost notes and limitations of the local run.
- LightGBM comparison methodology and per-region model caveats.

## 20. Production engineering checklist

Before promoting this pipeline beyond a learning environment, verify:

- **Data contract:** required columns/types, nullability, ranges, freshness, and label maturity are validated.
- **Point-in-time integrity:** every feature was available at prediction time; joins and label windows have been audited.
- **Split discipline:** test data is untouched during tuning; entity overlap is handled deliberately.
- **Reproducibility:** source snapshot, code commit, dependency lockfile, Spark/runtime version, parameters, random seeds, and model artifact are recorded.
- **Schema contract:** scoring inputs and outputs are checked; unknown categories and nulls have explicit policies.
- **Observability:** job duration, row counts, class balance, feature null rates, task skew, spill, and prediction distributions are monitored.
- **Operational safety:** retries are idempotent, output partitions are written safely, model versions are attached to predictions, and rollback is possible.
- **Governance:** IDs and PII are handled according to policy; access to training data and artifacts is controlled; retention requirements are respected.
- **Cost control:** compute and storage costs are measured; caching, cluster size, and tuning grid are justified.

The next lesson, **Feature engineering at scale**, deepens point-in-time joins, offline/online feature stores, streaming features, training-serving skew tests, freshness SLOs, and feature governance. Do not skip the temporal correctness foundation from this lesson.

## 21. References

Use versioned documentation that matches the runtime you install.

1. Apache Spark 3.5.7 — ML Pipelines: https://downloads.apache.org/spark/docs/3.5.7/ml-pipeline.html
2. Apache Spark 3.5.7 — MLlib guide: https://spark.apache.org/docs/3.5.7/ml-guide.html
3. Apache Spark 3.5.7 — feature extraction and transformation: https://spark.apache.org/docs/3.5.7/ml-features.html
4. Apache Spark 3.5.7 — classification and regression: https://spark.apache.org/docs/3.5.7/ml-classification-regression.html
5. PySpark API reference (`pyspark.ml`): https://spark.apache.org/docs/3.5.7/api/python/reference/pyspark.ml.html
6. PySpark `GroupedData.applyInPandas`: https://spark.apache.org/docs/3.5.7/api/python/reference/pyspark.sql/api/pyspark.sql.GroupedData.applyInPandas.html
7. LightGBM Python documentation: https://lightgbm.readthedocs.io/en/latest/Python-API.html
8. XGBoost distributed training documentation: https://xgboost.readthedocs.io/en/stable/tutorials/dask.html and https://xgboost.readthedocs.io/en/stable/tutorials/spark_estimator.html

Documentation URLs can change. If a version-specific page has moved, navigate from the official Apache Spark documentation for the installed release. Third-party integrations evolve quickly; verify the compatibility matrix before selecting them for production.
