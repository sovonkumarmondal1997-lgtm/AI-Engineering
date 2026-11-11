# BigQuery ML and Scheduled Queries

**Target path:** `Stage 2C — Data Engineering_3/04-Google-Cloud-BigQuery-and-GCP-Data-Engineering/05-bigquery-ml-and-scheduled-queries.md`  
**Level:** Beginner → Intermediate → Advanced  
**Primary language:** BigQuery GoogleSQL; Dataform SQLX for managed SQL workflows  
**Lab directory:** `experiments/05_bqml_scheduling/`

> **Version and execution note:** This lesson was statically reviewed against the official Google Cloud documentation linked at the end. The SQL is written for BigQuery GoogleSQL and is intended to be reproducible after replacing project and dataset identifiers. It has **not** been executed against a live Google Cloud project in this environment. Generative AI model names, regions, permissions, quotas, pricing, and preview/GA status can change; verify them immediately before use.

---

## 1. Learning objectives and prerequisites

### Learning objectives

By the end of this lesson, you should be able to:

- Create scheduled queries using BigQuery Data Transfer Service (DTS), understand `@run_date` and `@run_time`, configure notifications, and monitor failed runs.
- Design idempotent date-parameterized SQL workflows, safely backfill historical dates, and avoid duplicate rows or destructive overwrites.
- Write SQL UDFs, JavaScript UDFs, table functions, stored procedures, and BigQuery scripts using variables, conditionals, loops, temporary tables, and `EXECUTE IMMEDIATE`.
- Train and evaluate BigQuery ML models using `CREATE MODEL`, `ML.EVALUATE`, and `ML.PREDICT`.
- Explain the intended use of linear/logistic regression, boosted trees, k-means, matrix factorization, and `ARIMA_PLUS`.
- Apply feature preprocessing with `TRANSFORM`, use appropriate evaluation metrics, and avoid data leakage.
- Distinguish built-in BigQuery ML models from imported models and remote models that call Vertex AI.
- Understand Dataform dependencies, assertions, incremental tables, and workflow execution.
- Recognize supported generative AI, embedding, and vector-search capabilities without treating version-sensitive examples as universal.
- Decide when a SQL-centric BQML workflow is sufficient and when to use Vertex AI Pipelines or a broader ML platform.
- Govern model artifacts, evaluation results, data access, cost, lineage, and retraining.

### Prerequisites

You should already be comfortable with:

- BigQuery Standard SQL: joins, aggregates, CTEs, window functions, `MERGE`, dates, and NULL semantics.
- Partitioned tables, partition pruning, clustering, dry runs, `maximum_bytes_billed`, and `INFORMATION_SCHEMA.JOBS_BY_PROJECT` from Topic 03.
- Raw/curated data layers, schemas, data-quality checks, batch loads, and CDC concepts from Topic 04.
- GCP projects, datasets, IAM, service accounts, and basic billing controls.
- Basic classification/regression vocabulary: features, label, training set, evaluation set, prediction, overfitting, and leakage.

### Set up a low-cost lab

Use a dedicated non-production project and a dataset in one region. Replace `YOUR_PROJECT_ID` with your project ID and choose a dataset location. Model, source tables, destination tables, and remote model resources may have location constraints.

```sql
CREATE SCHEMA IF NOT EXISTS `YOUR_PROJECT_ID.bqml_lab`
OPTIONS(location = 'US');
```

The `US` location is only an example. Choose a location permitted by your organization and supported by every service you plan to use. Do not move regulated data to another location simply to make a demo work.

Before running jobs:

1. Create a budget alert and review quotas.
2. Use dry runs and inspect estimated bytes processed.
3. Filter partitioned source tables by partition columns.
4. Avoid `SELECT *` on large production tables.
5. Use small lab tables and delete lab objects when finished.
6. Remember that budgets alert; they do not automatically cap every cost.

---

## 2. Scheduled-query architecture

### What a scheduled query is

A BigQuery scheduled query is a recurring GoogleSQL query managed through BigQuery Data Transfer Service. At each scheduled run, DTS starts a transfer run, which submits a BigQuery job using the configured identity and query configuration. The query may write to a table, call a stored procedure, or perform DML/DDL if the selected query and configuration support it.

Conceptually:

```text
Cloud Scheduler-like schedule managed by BigQuery DTS
                 |
                 v
        Transfer configuration
        - query / procedure call
        - schedule and time zone
        - destination / write settings
        - service identity and notifications
                 |
                 v
           Transfer run
                 |
                 v
        BigQuery query job
                 |
                 v
      curated table / audit table
                 |
                 v
    monitoring, alerts, recovery runbook
```

Scheduled execution is **not** a guarantee that every run will finish successfully at the intended instant. A run can fail or be delayed because of IAM changes, quota or capacity constraints, invalid SQL, unavailable upstream data, region mismatches, service incidents, or downstream permission problems. Treat the schedule as a trigger, not as an SLA by itself.

### `@run_date` and `@run_time`

BigQuery scheduled queries expose two system parameters:

| Parameter | Type | Meaning |
|---|---|---|
| `@run_date` | `DATE` | Logical calendar date for the scheduled run |
| `@run_time` | `TIMESTAMP` | Intended scheduled execution time in UTC |

For a daily schedule, the intended `run_time` advances by the schedule interval even if actual execution starts a little later. Use `@run_date` to select a logical date partition. Do not assume it is automatically the local business date. If the business day is defined in a time zone such as `Asia/Kolkata`, derive that explicitly from `@run_time` and document the rule.

Example query to test in the editor:

```sql
SELECT
  @run_date AS logical_run_date,
  @run_time AS intended_run_time_utc,
  CURRENT_TIMESTAMP() AS actual_query_start_time;
```

The editor does not automatically supply these parameters in an ordinary ad hoc query. For local testing, supply query parameters with the `bq` CLI or replace them with declared variables in a script; do not assume a scheduled-query parameter is available to a manually run query. The `@run_date` parameter is distinct from destination-table templating such as `{run_date}`; the latter is a DTS configuration template, not GoogleSQL parameter syntax. For backfills, pass an explicit date to the same idempotent procedure rather than trying to change the schedule's historical run date implicitly.

### Create a scheduled query

In the BigQuery console:

1. Open **Scheduled queries** / **Data transfers** for the project.
2. Create a transfer configuration with source type **Scheduled query**.
3. Paste a parameterized query or a `CALL` statement.
4. Select the schedule, time zone where applicable, destination and write behavior where relevant.
5. Configure the execution identity and notification options supported by your environment.
6. Save, then inspect the transfer configuration and first run.
7. Verify the destination data and job metadata rather than relying only on a “successful” UI state.

A typical daily query can use `@run_date`:

```sql
SELECT
  @run_date AS summary_date,
  event_type,
  COUNT(*) AS event_count
FROM `YOUR_PROJECT_ID.bqml_lab.events`
WHERE event_date = @run_date
GROUP BY summary_date, event_type;
```

If this is configured as a destination-table query, confirm whether the configured write disposition is appropriate. A destination table setting does not replace a sound idempotency design.

### Notifications and monitoring

Configure failure notifications to an appropriate email or supported notification destination. Then add operational monitoring:

- Inspect transfer runs and their error messages.
- Inspect BigQuery job history and `INFORMATION_SCHEMA.JOBS_BY_PROJECT`.
- Track expected completion time, freshness, row counts, and data-quality assertions.
- Alert on missing partitions, late-arriving data, unexpected zero-row outputs, row-count changes, or failed assertions.
- Record the logical date processed, execution/job identifiers, source watermark, row counts, and status in an audit table.
- Keep a runbook with retry and backfill instructions.

An email notification alone is not observability. It will not prove that the data is complete, correct, or fresh.

### Identity and permissions

Use least privilege. The identity used by the scheduled transfer must be able to create query jobs and read source objects, and must have the required permissions to write destination tables or create/replace models. If a remote model is used, the connection's service account needs the appropriate Vertex AI access in the endpoint project. If GCS or other services are involved, grant access to the relevant service identity, not broadly to all users.

Exact roles depend on whether the workflow reads tables, writes tables, creates models, uses a connection, or accesses other services. Validate the current IAM documentation rather than granting Owner or Editor as a shortcut.

---

## 3. Parameterization, retries, idempotency, and backfills

### Idempotency is a design property

A job is idempotent when repeating the same logical operation for the same input produces the same intended state, without accumulating duplicate rows or damaging unrelated dates.

Common patterns:

- **Daily aggregate:** replace exactly one logical date partition atomically, or `MERGE` by a stable unique key.
- **Event ingestion:** deduplicate using stable event IDs and a deterministic tie-breaker.
- **Model training:** use a versioned model name or an explicit promotion process; do not overwrite a production model silently.
- **Backfill:** pass explicit dates, record the requested range, and ensure each date is independently safe to retry.

Blind `INSERT` into a daily summary is not idempotent. Blind `CREATE OR REPLACE TABLE` on a shared production table can erase unrelated history.

### Build a small deterministic source dataset

The labs use a deliberately small, synthetic dataset. It is designed to teach mechanics, not represent real customer behavior. The table has one row per event and an explicit `event_date` partition column.

Save as `experiments/05_bqml_scheduling/01_setup_lab.sql`:

```sql
CREATE SCHEMA IF NOT EXISTS `YOUR_PROJECT_ID.bqml_lab`
OPTIONS(location = 'US');

CREATE OR REPLACE TABLE `YOUR_PROJECT_ID.bqml_lab.events`
PARTITION BY event_date
CLUSTER BY event_type AS
SELECT
  event_id,
  event_date,
  event_type,
  channel,
  amount
FROM UNNEST([
  STRUCT('e001' AS event_id, DATE '2026-01-01' AS event_date,
         'purchase' AS event_type, 'web' AS channel, NUMERIC '19.99' AS amount),
  STRUCT('e002', DATE '2026-01-01', 'view', 'web', NUMERIC '0'),
  STRUCT('e003', DATE '2026-01-01', 'purchase', 'app', NUMERIC '35.00'),
  STRUCT('e004', DATE '2026-01-02', 'view', 'app', NUMERIC '0'),
  STRUCT('e005', DATE '2026-01-02', 'purchase', 'web', NUMERIC '12.50'),
  STRUCT('e006', DATE '2026-01-03', 'cart', 'web', NUMERIC '0'),
  STRUCT('e007', DATE '2026-01-03', 'purchase', 'app', NUMERIC '49.00'),
  STRUCT('e008', DATE '2026-01-04', 'view', 'web', NUMERIC '0'),
  STRUCT('e009', DATE '2026-01-04', 'purchase', 'web', NUMERIC '21.00'),
  STRUCT('e010', DATE '2026-01-05', 'cart', 'app', NUMERIC '0'),
  STRUCT('e011', DATE '2026-01-05', 'purchase', 'app', NUMERIC '18.00'),
  STRUCT('e012', DATE '2026-01-06', 'view', 'web', NUMERIC '0'),
  STRUCT('e013', DATE '2026-01-06', 'purchase', 'web', NUMERIC '80.00'),
  STRUCT('e014', DATE '2026-01-07', 'purchase', 'app', NUMERIC '27.00')
]);
```

The dates are fixed to keep the exercise reproducible. When you adapt this to current data, do not assume the demo dates match your schedule.

### Create a daily summary table

Save as `experiments/05_bqml_scheduling/02_daily_summary.sql`:

```sql
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT_ID.bqml_lab.daily_summary` (
  summary_date DATE NOT NULL,
  event_type STRING NOT NULL,
  channel STRING NOT NULL,
  event_count INT64 NOT NULL,
  revenue NUMERIC NOT NULL,
  refreshed_at TIMESTAMP NOT NULL
)
PARTITION BY summary_date
CLUSTER BY event_type, channel;
```

For a scheduled query, the simplest idempotent pattern for this small daily aggregate is a transaction that deletes the target date and reinserts its aggregate. The delete and insert are in one transaction so readers do not observe a committed half-refresh.

Save as `experiments/05_bqml_scheduling/03_refresh_daily_summary.sql`:

```sql
DECLARE p_run_date DATE DEFAULT @run_date;

BEGIN TRANSACTION;

DELETE FROM `YOUR_PROJECT_ID.bqml_lab.daily_summary`
WHERE summary_date = p_run_date;

INSERT INTO `YOUR_PROJECT_ID.bqml_lab.daily_summary`
  (summary_date, event_type, channel, event_count, revenue, refreshed_at)
SELECT
  p_run_date AS summary_date,
  event_type,
  channel,
  COUNT(*) AS event_count,
  SUM(amount) AS revenue,
  CURRENT_TIMESTAMP() AS refreshed_at
FROM `YOUR_PROJECT_ID.bqml_lab.events`
WHERE event_date = p_run_date
GROUP BY event_type, channel;

COMMIT TRANSACTION;
```

**Important:** `@run_date` is a scheduled-query system parameter. The statement above is intended for a scheduled-query configuration. For an ad hoc test, replace the declaration with a fixed `DATE`, or use a stored procedure that accepts a date argument. If the source date is empty, the transaction leaves that target date empty; this is intentional for a complete refresh, but you should decide whether an empty source date means “zero events” or “upstream data is missing” in your real system. Add a source completeness gate before deleting if an empty partition could indicate a late or failed load.

For higher-volume workloads, evaluate the cost of delete/insert versus `MERGE`, partition replacement, and table design. The transaction is a correctness pattern, not a universal performance optimum.

### Validate the daily output

```sql
SELECT *
FROM `YOUR_PROJECT_ID.bqml_lab.daily_summary`
WHERE summary_date BETWEEN DATE '2026-01-01' AND DATE '2026-01-07'
ORDER BY summary_date, event_type, channel;
```

Expected interpretation: each row represents one date, event type, and channel combination; `event_count` is the count of source events and `revenue` is the sum of `amount`. Dates with no source events produce no summary rows. Do not infer real business performance from the tiny sample.

### Backfill seven dates safely

The best backfill design is to call a date-parameterized procedure once for each logical date. That keeps the same business logic for scheduled runs and backfills. Do not copy-paste a query seven times with different dates.

Create a stored procedure that owns the refresh transaction:

Save as `experiments/05_bqml_scheduling/04_create_refresh_procedure.sql`:

```sql
CREATE OR REPLACE PROCEDURE
  `YOUR_PROJECT_ID.bqml_lab.refresh_daily_summary`(p_run_date DATE)
BEGIN
  BEGIN TRANSACTION;

  DELETE FROM `YOUR_PROJECT_ID.bqml_lab.daily_summary`
  WHERE summary_date = p_run_date;

  INSERT INTO `YOUR_PROJECT_ID.bqml_lab.daily_summary`
    (summary_date, event_type, channel, event_count, revenue, refreshed_at)
  SELECT
    p_run_date,
    event_type,
    channel,
    COUNT(*),
    SUM(amount),
    CURRENT_TIMESTAMP()
  FROM `YOUR_PROJECT_ID.bqml_lab.events`
  WHERE event_date = p_run_date
  GROUP BY event_type, channel;

  COMMIT TRANSACTION;
END;
```

Backfill the seven dates in a script:

Save as `experiments/05_bqml_scheduling/05_backfill_seven_days.sql`:

```sql
DECLARE d DATE DEFAULT DATE '2026-01-01';
DECLARE last_date DATE DEFAULT DATE '2026-01-07';

WHILE d <= last_date DO
  CALL `YOUR_PROJECT_ID.bqml_lab.refresh_daily_summary`(d);
  SET d = DATE_ADD(d, INTERVAL 1 DAY);
END WHILE;
```

This script is sequential and repeatable for the same seven dates. Re-running it refreshes those dates rather than appending duplicates. For larger ranges, use a controlled orchestration process, log each date and status, and retry failed dates independently. Never run a large backfill without a cost estimate and a plan for concurrency and quotas.

### Verify no duplicates and no missing dates

```sql
-- There should be no duplicate date/type/channel grain.
SELECT summary_date, event_type, channel, COUNT(*) AS rows_at_grain
FROM `YOUR_PROJECT_ID.bqml_lab.daily_summary`
WHERE summary_date BETWEEN DATE '2026-01-01' AND DATE '2026-01-07'
GROUP BY summary_date, event_type, channel
HAVING COUNT(*) > 1;

-- Compare event counts in source and aggregate by date.
WITH source_counts AS (
  SELECT event_date, COUNT(*) AS source_count
  FROM `YOUR_PROJECT_ID.bqml_lab.events`
  WHERE event_date BETWEEN DATE '2026-01-01' AND DATE '2026-01-07'
  GROUP BY event_date
),
summary_counts AS (
  SELECT summary_date, SUM(event_count) AS summary_count
  FROM `YOUR_PROJECT_ID.bqml_lab.daily_summary`
  WHERE summary_date BETWEEN DATE '2026-01-01' AND DATE '2026-01-07'
  GROUP BY summary_date
)
SELECT
  COALESCE(s.event_date, t.summary_date) AS event_date,
  s.source_count,
  t.summary_count,
  s.source_count - t.summary_count AS difference
FROM source_counts s
FULL OUTER JOIN summary_counts t
  ON s.event_date = t.summary_date
WHERE COALESCE(s.source_count, 0) != COALESCE(t.summary_count, 0);
```

Both validation queries should return zero rows when the summary is correct for the provided source dates.

### Failure recovery pattern

1. Identify the failed logical date and the BigQuery job/transfer error.
2. Confirm the source partition is complete and stable.
3. Check whether the transaction committed; query the target grain and compare source counts.
4. Re-run only the failed logical date with the same idempotent procedure.
5. Validate row counts and quality assertions.
6. Record the retry and cause in an audit table/runbook.

A retry is safe only because the operation is designed to be idempotent. “Retry on every error” without classifying permission, syntax, quota, and data-completeness failures can repeat the same failure or corrupt results.

---

## 4. BigQuery scripting and reusable routines

### SQL UDF

A SQL UDF returns a scalar expression and is useful for reusable deterministic logic.

```sql
CREATE OR REPLACE FUNCTION `YOUR_PROJECT_ID.bqml_lab.net_amount`(
  gross NUMERIC,
  discount NUMERIC
)
RETURNS NUMERIC
AS (gross - COALESCE(discount, 0));
```

Example:

```sql
SELECT
  `YOUR_PROJECT_ID.bqml_lab.net_amount`(NUMERIC '100', NUMERIC '12.5')
    AS net_amount;
```

Prefer SQL UDFs for simple logic that can be expressed in GoogleSQL. Version and test the function like other production code.

### JavaScript UDF

JavaScript UDFs are useful only when SQL does not express the required transformation cleanly. They have runtime, scalability, and optimization trade-offs; they are not the default choice for large transformations.

```sql
CREATE OR REPLACE FUNCTION `YOUR_PROJECT_ID.bqml_lab.normalize_code`(value STRING)
RETURNS STRING
LANGUAGE js AS r'''
  if (value === null) return null;
  return value.trim().toLowerCase();
''';
```

Example:

```sql
SELECT `YOUR_PROJECT_ID.bqml_lab.normalize_code`('  WEB  ') AS normalized;
```

Do not place secrets in JavaScript source, and do not use JavaScript UDFs to bypass access controls. Test edge cases such as NULLs, malformed inputs, Unicode, and unusually long values.

### Table function

A table function returns a table and can package a parameterized query.

```sql
CREATE OR REPLACE TABLE FUNCTION
  `YOUR_PROJECT_ID.bqml_lab.summary_for_date`(p_date DATE)
AS (
  SELECT
    event_type,
    channel,
    COUNT(*) AS event_count,
    SUM(amount) AS revenue
  FROM `YOUR_PROJECT_ID.bqml_lab.events`
  WHERE event_date = p_date
  GROUP BY event_type, channel
);
```

Use it:

```sql
SELECT *
FROM `YOUR_PROJECT_ID.bqml_lab.summary_for_date`(DATE '2026-01-03');
```

Table functions are good for reusable read logic. Use a stored procedure when you need to perform multiple statements or mutate tables.

### Stored procedure

A stored procedure is a named multi-statement routine. It can accept parameters and run DML, DDL, and scripts subject to BigQuery's procedural and transaction rules.

The `refresh_daily_summary` procedure from Section 3 is the core example. Schedule it by configuring the scheduled query to call it with the appropriate date parameter, for example:

```sql
CALL `YOUR_PROJECT_ID.bqml_lab.refresh_daily_summary`(@run_date);
```

Confirm the scheduled-query UI supports the intended query and parameter configuration in your project. Test the `CALL` manually first, then test one scheduled run, then enable the regular cadence. Keep the procedure and the schedule in version control / infrastructure documentation.

### Scripting: variables, `IF`, loops, temporary tables

```sql
DECLARE target_date DATE DEFAULT DATE '2026-01-03';
DECLARE source_rows INT64;

SET source_rows = (
  SELECT COUNT(*)
  FROM `YOUR_PROJECT_ID.bqml_lab.events`
  WHERE event_date = target_date
);

IF source_rows = 0 THEN
  SELECT 'No source rows; verify upstream completeness' AS status;
ELSE
  CREATE TEMP TABLE date_events AS
  SELECT event_id, event_type, channel, amount
  FROM `YOUR_PROJECT_ID.bqml_lab.events`
  WHERE event_date = target_date;

  SELECT event_type, COUNT(*) AS n
  FROM date_events
  GROUP BY event_type;
END IF;
```

A loop is useful for a small controlled date range or orchestration script. Avoid loops that execute hundreds or thousands of independent queries when a set-based query or dedicated orchestrator is more appropriate.

### Dynamic SQL with `EXECUTE IMMEDIATE`

Use dynamic SQL only when the SQL structure must vary, such as selecting a table from a controlled allowlist. Query parameters bind values; they do **not** bind table identifiers. Never concatenate untrusted user input into SQL.

```sql
DECLARE allowed_table STRING DEFAULT 'events';
DECLARE sql_text STRING;

IF allowed_table NOT IN ('events') THEN
  RAISE USING MESSAGE = 'Table is not allowlisted';
END IF;

SET sql_text = FORMAT(
  'SELECT COUNT(*) AS row_count FROM `YOUR_PROJECT_ID.bqml_lab.%s`',
  allowed_table
);

EXECUTE IMMEDIATE sql_text;
```

The identifier is safe here only because it is selected from a fixed allowlist. For values, use `USING` parameters instead of string concatenation:

```sql
DECLARE target_date DATE DEFAULT DATE '2026-01-03';

EXECUTE IMMEDIATE '''
  SELECT COUNT(*) AS row_count
  FROM `YOUR_PROJECT_ID.bqml_lab.events`
  WHERE event_date = @d
'''
USING target_date AS d;
```

### Routine design checklist

- Keep one responsibility per routine.
- Use explicit parameter types and document timezone semantics.
- Use stable grains and keys.
- Add assertions for preconditions and postconditions.
- Do not swallow errors without recording them.
- Ensure retries are safe.
- Keep dynamic SQL identifiers allowlisted.
- Grant routine and underlying data access according to current BigQuery authorization rules.
- Test the routine with empty dates, duplicate input, NULLs, and repeated invocation.

---

## 5. BigQuery ML fundamentals and model families

BigQuery ML (BQML) lets you create and use supported models through SQL. It is valuable when data is already in BigQuery and a model can be trained or served with the supported model family, data types, scale, and operational requirements. It does not remove the need for statistical reasoning, careful validation, monitoring, or governance.

### Model-family selection

| Model family | BQML model type | Typical use | Key caution |
|---|---|---|---|
| Linear regression | `LINEAR_REG` | Predict a numeric outcome | Check residuals, scale, outliers, and assumptions |
| Logistic regression | `LOGISTIC_REG` | Binary or multiclass classification | Accuracy can mislead with imbalanced labels; inspect precision/recall and thresholds |
| Boosted trees | `BOOSTED_TREE_CLASSIFIER` / `BOOSTED_TREE_REGRESSOR` | Nonlinear tabular prediction | Tune carefully; monitor overfitting and training cost |
| K-means | `KMEANS` | Unsupervised segmentation | Clusters are not automatically meaningful business segments |
| Matrix factorization | `MATRIX_FACTORIZATION` | Collaborative filtering / recommendations | Sparse interaction data, cold start, and evaluation design matter |
| Time series | `ARIMA_PLUS` | Univariate forecasting and anomaly detection | Validate time frequency, missing periods, duplicates, seasonality, and forecast horizon |
| Time series with regressors | `ARIMA_PLUS_XREG` | Forecasting with explanatory covariates | Future covariate values must be available or forecast separately |
| Imported models | e.g. `TENSORFLOW`, `TENSORFLOW_LITE`, `ONNX`, `XGBOOST` where supported | Inference with a compatible pre-trained artifact | Format, size, location, pricing model, and supported input/output types vary |
| Remote models | `REMOTE WITH CONNECTION` | Call supported Vertex AI-hosted models from SQL | Connection, IAM, model availability, latency, quotas, and per-call cost matter |

Model support and options vary by model type. Do not assume every `CREATE MODEL` option applies to every family. Use the specific official syntax page for the exact model.

### Minimal `CREATE MODEL` patterns for the other required families

The following are **schema-dependent templates**, not runnable against the preceding `events` table without adapting the source. Replace each table name and column with a real, authorized training relation, and dry-run/estimate cost before training.

**Linear regression** — the label must be numeric (`FLOAT64`, `INT64`, `NUMERIC`, or another supported numeric type):

```sql
CREATE OR REPLACE MODEL `YOUR_PROJECT_ID.bqml_lab.sales_linear_v1`
OPTIONS (
  MODEL_TYPE = 'LINEAR_REG',
  INPUT_LABEL_COLS = ['sales_amount']
) AS
SELECT feature_1, feature_2, sales_amount
FROM `YOUR_PROJECT_ID.bqml_lab.regression_training`;
```

**Boosted-tree classification** — use a classification label and hold out evaluation data rather than reporting training performance as generalization:

```sql
CREATE OR REPLACE MODEL `YOUR_PROJECT_ID.bqml_lab.churn_boosted_v1`
OPTIONS (
  MODEL_TYPE = 'BOOSTED_TREE_CLASSIFIER',
  INPUT_LABEL_COLS = ['churned'],
  DATA_SPLIT_METHOD = 'CUSTOM',
  DATA_SPLIT_COL = 'is_eval',
  MAX_ITERATIONS = 30
) AS
SELECT tenure_months, monthly_tickets, plan_tier, churned, is_eval
FROM `YOUR_PROJECT_ID.bqml_lab.churn_demo`;
```

**K-means clustering** — provide numeric or otherwise supported feature columns and exclude identifiers that would create meaningless distance:

```sql
CREATE OR REPLACE MODEL `YOUR_PROJECT_ID.bqml_lab.customer_segments_v1`
OPTIONS (
  MODEL_TYPE = 'KMEANS',
  NUM_CLUSTERS = 4,
  STANDARDIZE_FEATURES = TRUE
) AS
SELECT tenure_months, monthly_tickets
FROM `YOUR_PROJECT_ID.bqml_lab.churn_demo`;
```

The chosen cluster count is a starting hypothesis, not evidence that four useful business segments exist. Inspect cluster centroids, sizes, stability, and business interpretability.

**Matrix factorization** — the source must contain user/item interactions and a supported numeric rating/strength column:

```sql
CREATE OR REPLACE MODEL `YOUR_PROJECT_ID.bqml_lab.recommender_v1`
OPTIONS (
  MODEL_TYPE = 'MATRIX_FACTORIZATION',
  USER_COL = 'user_id',
  ITEM_COL = 'item_id',
  RATING_COL = 'rating'
) AS
SELECT user_id, item_id, rating
FROM `YOUR_PROJECT_ID.bqml_lab.user_item_ratings`;
```

This requires `user_item_ratings` to exist with appropriate types and meaningful interactions. Evaluate recommendation quality with a leakage-safe holdout and suitable ranking/recommendation metrics; a successful training job alone does not validate recommendation quality. For all families, consult the current model-specific syntax page for options and supported evaluation functions before adapting the template.

### Classification problem: churn demonstration

The lab creates a synthetic customer table with a numeric label and a deterministic split. The generated label intentionally depends on the features, making it suitable for a mechanics demo but unrealistic as a benchmark. A production churn model needs a well-defined prediction timestamp, an outcome window, representative customers, and a leakage-safe feature snapshot.

Save as `experiments/05_bqml_scheduling/06_create_churn_demo.sql`:

```sql
CREATE OR REPLACE TABLE `YOUR_PROJECT_ID.bqml_lab.churn_demo` AS
WITH generated AS (
  SELECT
    customer_id,
    CAST(MOD(customer_id * 7, 48) + 1 AS INT64) AS tenure_months,
    CAST(MOD(customer_id * 11, 10) AS INT64) AS monthly_tickets,
    CAST(MOD(customer_id * 13, 3) AS INT64) AS plan_tier_num
  FROM UNNEST(GENERATE_ARRAY(1, 600)) AS customer_id
)
SELECT
  customer_id,
  tenure_months,
  monthly_tickets,
  CASE plan_tier_num
    WHEN 0 THEN 'basic'
    WHEN 1 THEN 'standard'
    ELSE 'premium'
  END AS plan_tier,
  CAST(
    CASE
      WHEN tenure_months <= 8 OR monthly_tickets >= 8 THEN 1
      ELSE 0
    END AS INT64
  ) AS churned,
  MOD(customer_id, 5) = 0 AS is_eval
FROM generated;
```

Inspect label balance and the split:

```sql
SELECT is_eval, churned, COUNT(*) AS rows
FROM `YOUR_PROJECT_ID.bqml_lab.churn_demo`
GROUP BY is_eval, churned
ORDER BY is_eval, churned;
```

A real evaluation set should be large and representative enough to estimate performance. A 20% split of a small synthetic table is only a demonstration. The synthetic label is deterministically defined from two input features, so very high metrics would only show that the model learned the artificial rule; they are not evidence of real churn performance. For temporal churn data, use a chronological split that respects the prediction timestamp and outcome window when that better reflects production. Keep post-outcome fields and features unavailable at prediction time out of training.

### Train logistic regression

Save as `experiments/05_bqml_scheduling/07_train_logistic_regression.sql`:

```sql
CREATE OR REPLACE MODEL `YOUR_PROJECT_ID.bqml_lab.churn_logistic_v1`
OPTIONS (
  MODEL_TYPE = 'LOGISTIC_REG',
  INPUT_LABEL_COLS = ['churned'],
  DATA_SPLIT_METHOD = 'CUSTOM',
  DATA_SPLIT_COL = 'is_eval',
  MAX_ITERATIONS = 20
) AS
SELECT
  tenure_months,
  monthly_tickets,
  plan_tier,
  churned,
  is_eval
FROM `YOUR_PROJECT_ID.bqml_lab.churn_demo`;
```

For `DATA_SPLIT_METHOD = 'CUSTOM'` without hyperparameter tuning, BigQuery ML requires a BOOL split column: `FALSE` rows are used for training and `TRUE` or `NULL` rows for evaluation. The split column is excluded from model features. Do not use the `TRAIN`/`EVAL` string convention unless the model is configured for hyperparameter tuning, where that convention applies. The `CREATE OR REPLACE MODEL` form is convenient for a disposable lab but can overwrite an existing model. In production, use versioned model names and a promotion process instead of replacing the current production model in place.

### Evaluate the model

```sql
-- Because the model was trained with a CUSTOM Boolean split, the
-- default evaluation uses the held-out evaluation rows from training.
SELECT *
FROM ML.EVALUATE(
  MODEL `YOUR_PROJECT_ID.bqml_lab.churn_logistic_v1`
);
```

For classification, inspect metrics such as precision, recall, accuracy, F1 score, log loss, and ROC AUC where returned by the model and function. Interpret them in context:

- **Precision:** among predicted positives, how many were truly positive?
- **Recall:** among actual positives, how many did the model identify?
- **F1:** harmonic mean of precision and recall at the chosen threshold.
- **ROC AUC:** ranking quality across thresholds; it does not choose the business threshold.
- **Log loss:** quality of predicted probabilities, penalizing confident wrong predictions.

Which metric matters depends on the cost of false positives and false negatives. A fraud model, a churn intervention, and a medical alert do not have the same error costs. Do not select a model by accuracy alone.

### Generate predictions

```sql
WITH eval_rows AS (
  SELECT customer_id, tenure_months, monthly_tickets, plan_tier, churned
  FROM `YOUR_PROJECT_ID.bqml_lab.churn_demo`
  WHERE is_eval = TRUE
), predictions AS (
  SELECT *
  FROM ML.PREDICT(
    MODEL `YOUR_PROJECT_ID.bqml_lab.churn_logistic_v1`,
    (
      SELECT customer_id, tenure_months, monthly_tickets, plan_tier
      FROM eval_rows
    )
  )
)
SELECT
  e.customer_id,
  e.churned AS observed_label,
  p.predicted_churned,
  p.predicted_churned_probs
FROM eval_rows AS e
JOIN predictions AS p USING (customer_id)
ORDER BY e.customer_id;
```

`ML.PREDICT` returns prediction columns alongside input columns. The example deliberately supplies only features and the identifier to `ML.PREDICT`, then joins the known labels afterward for evaluation; a production inference query should not depend on labels that are unavailable at prediction time.

### Feature preprocessing with `TRANSFORM`

Preprocessing must be fit on training data and reused unchanged at evaluation and inference time. BQML's `TRANSFORM` clause stores supported transformation logic with the model so that prediction can apply the same transformations.

Example with numeric scaling:

```sql
CREATE OR REPLACE MODEL `YOUR_PROJECT_ID.bqml_lab.churn_logistic_scaled_v1`
TRANSFORM (
  ML.STANDARD_SCALER(tenure_months) OVER() AS tenure_scaled,
  ML.STANDARD_SCALER(monthly_tickets) OVER() AS tickets_scaled,
  plan_tier,
  churned,
  is_eval
)
OPTIONS (
  MODEL_TYPE = 'LOGISTIC_REG',
  INPUT_LABEL_COLS = ['churned'],
  DATA_SPLIT_METHOD = 'CUSTOM',
  DATA_SPLIT_COL = 'is_eval',
  MAX_ITERATIONS = 20
) AS
SELECT
  tenure_months,
  monthly_tickets,
  plan_tier,
  churned,
  is_eval
FROM `YOUR_PROJECT_ID.bqml_lab.churn_demo`;
```

`ML.STANDARD_SCALER` computes scaling statistics for the model transformation. Do not manually calculate scaling statistics using the full dataset before the split: that can leak evaluation-set information into training. The exact transformation functions available depend on the model family; consult the current feature-preprocessing documentation before adding encoders, buckets, crosses, or text transformations.

### Explainability and feature importance

For supported models, use the relevant BQML functions, for example `ML.EXPLAIN_PREDICT` for supported model types or model-specific global feature-importance functions. The output and support differ by model family. Explainability outputs are not causal explanations: a feature contribution does not prove that changing the feature will cause the prediction to change in the same way.

For production review, preserve:

- Model name/version and training query version.
- Training time window and source snapshot or data version.
- Feature definitions and label/outcome window.
- Evaluation metrics and chosen operating threshold.
- Baseline comparison, segment-level performance, and known limitations.
- Approver, deployment date, rollback model, and monitoring owner.

---

## 6. Time-series forecasting with `ARIMA_PLUS`

`ARIMA_PLUS` is a univariate time-series forecasting model. It models a single numeric series over time and supports features such as automatic frequency inference and automated modeling components. It is not a general-purpose causal model and it cannot know future events that are absent from the inputs.

### Create a daily time-series dataset

Save as `experiments/05_bqml_scheduling/08_create_daily_sales.sql`:

```sql
CREATE OR REPLACE TABLE `YOUR_PROJECT_ID.bqml_lab.daily_sales` AS
SELECT
  DATE_ADD(DATE '2025-01-01', INTERVAL day_offset DAY) AS sale_date,
  CAST(
    100
    + 0.7 * day_offset
    + 15 * SIN(2 * ACOS(-1) * day_offset / 7)
    + MOD(day_offset * 17, 11)
    AS FLOAT64
  ) AS sales
FROM UNNEST(GENERATE_ARRAY(0, 179)) AS day_offset;
```

This synthetic series includes trend, a weekly-like seasonal component, and a deterministic perturbation. It is not a real demand series and should not be used to compare forecasting systems.

### Train the model

```sql
CREATE OR REPLACE MODEL `YOUR_PROJECT_ID.bqml_lab.daily_sales_arima_v1`
OPTIONS (
  MODEL_TYPE = 'ARIMA_PLUS',
  TIME_SERIES_TIMESTAMP_COL = 'sale_date',
  TIME_SERIES_DATA_COL = 'sales',
  DATA_FREQUENCY = 'DAILY',
  HORIZON = 14,
  AUTO_ARIMA = TRUE,
  DECOMPOSE_TIME_SERIES = TRUE
) AS
SELECT sale_date, sales
FROM `YOUR_PROJECT_ID.bqml_lab.daily_sales`
WHERE sale_date < DATE '2025-06-20';
```

The cutoff above intentionally leaves the final 10 days of the generated series outside the training window. For a real forecasting exercise, score those later observations against forecasts using a chronological backtest. Do not shuffle time-series rows into random train/evaluation sets.

### Forecast the next 14 points

```sql
SELECT *
FROM ML.FORECAST(
  MODEL `YOUR_PROJECT_ID.bqml_lab.daily_sales_arima_v1`,
  STRUCT(14 AS horizon, 0.90 AS confidence_level)
)
ORDER BY forecast_timestamp;
```

Interpret the forecast as an estimate plus an uncertainty interval, not as a guaranteed outcome. `confidence_level` controls the reported prediction interval level. Check the actual result schema in the current function documentation before building downstream code that relies on column names.

### Evaluate and explain the forecast

```sql
SELECT *
FROM ML.ARIMA_EVALUATE(
  MODEL `YOUR_PROJECT_ID.bqml_lab.daily_sales_arima_v1`
);
```

For decomposition and prediction intervals, explore `ML.EXPLAIN_FORECAST` using the documented syntax for the model. Compare forecasts to a naive baseline (for example, last-week's value for weekly data) using a rolling-origin backtest. A single in-sample metric is not enough.

### Forecasting checks

- Are timestamps unique and correctly typed?
- Is the series frequency regular, or is irregularity intentional?
- Are there gaps, duplicate timestamps, outliers, or structural breaks?
- Is the target non-negative or bounded? Should forecasts be constrained?
- Is the horizon aligned with the operational decision?
- Are holidays and business calendars relevant?
- Is the evaluation window strictly after the training window?
- Is a known future covariate available at prediction time? If not, do not use it as though it were known.
- Is the forecast better than a simple baseline?
- Does the uncertainty interval cover actual outcomes at a useful rate?

---

## 7. External and remote model integration

These are different patterns and should not be conflated.

### Imported model

An imported model is a compatible model artifact stored in Cloud Storage and imported into BigQuery ML. Documented families include formats such as TensorFlow, TensorFlow Lite, ONNX, and XGBoost, subject to current compatibility constraints. Imported models are generally used for inference with `ML.PREDICT`; they are not equivalent to training an arbitrary model inside BigQuery.

Illustrative ONNX import:

```sql
CREATE MODEL `YOUR_PROJECT_ID.bqml_lab.imported_onnx_model`
OPTIONS (
  MODEL_TYPE = 'ONNX',
  MODEL_PATH = 'gs://YOUR_BUCKET/path/to/model.onnx'
);
```

Prerequisites and limitations to verify before attempting this:

- The artifact format and runtime version must be supported.
- Input/output tensor types and shapes must be compatible.
- Object-table and pricing-mode restrictions may apply to particular formats.
- The executing identity must be able to read the artifact.
- The model's region and supported BigQuery location must be compatible.
- Model size limits and exact `CREATE MODEL` options vary by format.

This example is a template, not a runnable command until a real compatible artifact exists at the specified Cloud Storage URI.

### Remote model using Vertex AI

A remote model is a BigQuery model object that references a supported external model endpoint. BigQuery calls the endpoint through a BigQuery connection. This can make inference available through SQL, but it introduces external service permissions, quotas, latency, model-specific costs, and region constraints.

Conceptual template:

```sql
CREATE OR REPLACE MODEL `YOUR_PROJECT_ID.bqml_lab.remote_text_model`
REMOTE WITH CONNECTION `YOUR_PROJECT_ID.US.YOUR_CONNECTION`
OPTIONS (
  ENDPOINT = 'YOUR_SUPPORTED_VERTEX_AI_MODEL_ENDPOINT'
);
```

The exact `ENDPOINT` value and `OPTIONS` depend on the supported model and remote-model type. Do not paste a model name from an old tutorial and assume it is still available. Check the current remote-model guide and model catalog first.

Typical prerequisites:

1. Enable the required BigQuery and Vertex AI APIs.
2. Create a BigQuery Cloud Resource connection in a supported location.
3. Grant the connection service account the minimum required Vertex AI role on the endpoint project.
4. Grant the user permissions to create/use models and delegate connection access as required.
5. Verify model, dataset, connection, and endpoint location compatibility.
6. Estimate both BigQuery processing and Vertex AI inference costs.
7. Test with a small input, inspect errors and latency, and set quotas/monitoring.

### Generative AI SQL functions: version-sensitive

The roadmap names `ML.GENERATE_TEXT`, embeddings, and vector search as awareness topics. Current documentation also provides newer `AI.GENERATE_TEXT` and `AI.GENERATE_EMBEDDING` interfaces for supported remote models. Google recommends `AI.GENERATE_TEXT` for new queries where applicable. Function availability, supported model families, output columns, IAM roles, locations, and billing can change; use the current reference docs.

Example concept for generation, only after a supported remote model has been created:

```sql
-- Illustrative pattern; adapt to the current function signature and model.
SELECT *
FROM AI.GENERATE_TEXT(
  MODEL `YOUR_PROJECT_ID.bqml_lab.remote_text_model`,
  (SELECT 'Summarize this approved text: ...' AS prompt)
);
```

Example concept for embeddings:

```sql
-- Illustrative pattern; verify the current function signature and model type.
SELECT *
FROM AI.GENERATE_EMBEDDING(
  MODEL `YOUR_PROJECT_ID.bqml_lab.remote_embedding_model`,
  (SELECT 'A short document to embed' AS content)
);
```

Do not run generation across an entire large table without sampling, quotas, retry controls, and cost estimates. Model calls may be billed separately from BigQuery bytes processed. Do not send secrets, personal data, or regulated text to an external model unless the organization's privacy, residency, retention, and contractual controls permit it.

### Vector search

A typical semantic retrieval workflow is:

1. Generate embeddings for documents with a supported embedding model.
2. Store document IDs, access-control metadata, content references, and embeddings.
3. Optionally create a vector index when the scale and query pattern justify it.
4. Use `VECTOR_SEARCH` with a query embedding to retrieve nearest neighbors.
5. Apply tenant/security filters and validate access before returning retrieved content.
6. Optionally pass selected context to a generative model.

A vector index is an optimization, not a substitute for authorization or relevance evaluation. Measure recall/latency and index maintenance costs. Verify current supported vector types, index options, region availability, and exact `VECTOR_SEARCH` syntax before deploying.

---

## 8. Dataform and SQL pipeline management

Dataform is a SQL workflow tool for BigQuery. It adds dependency management, compilation, assertions, documentation, and incremental table patterns. It does not replace every orchestration need; use Composer, Workflows, or another orchestrator when the pipeline spans services, requires complex branching, or needs broader operational coordination.

### Minimal Dataform project layout

```text
definitions/
├── sources.js
├── daily_summary.sqlx
└── assertions/
    ├── daily_summary_no_nulls.sqlx
    └── daily_summary_grain_unique.sqlx
workflow_settings.yaml
```

Configure project, default dataset/schema, and default location in the workspace's current Dataform settings. The precise fields in `workflow_settings.yaml` depend on the Dataform project generation and current tooling; use the current Dataform project setup guide rather than copying a legacy configuration blindly.

### Declare a source

`definitions/sources.js`:

```javascript
declare({
  database: "YOUR_PROJECT_ID",
  schema: "bqml_lab",
  name: "events"
});
```

### Create a dependent table

`definitions/daily_summary.sqlx`:

```sql
config {
  type: "table",
  schema: "bqml_lab",
  description: "Daily event counts and revenue by event type and channel."
}

SELECT
  event_date AS summary_date,
  event_type,
  channel,
  COUNT(*) AS event_count,
  SUM(amount) AS revenue
FROM ${ref("events")}
GROUP BY summary_date, event_type, channel
```

This is a full-refresh table example, suitable for the tiny lab. It recreates the table on each successful workflow execution. For production, choose a table type and incremental strategy based on source mutation, late-arriving data, retention, and cost.

### Assertions

`definitions/assertions/daily_summary_no_nulls.sqlx`:

```sql
config {
  type: "assertion",
  description: "Summary grain and measures must not be NULL."
}

SELECT *
FROM ${ref("daily_summary")}
WHERE summary_date IS NULL
   OR event_type IS NULL
   OR channel IS NULL
   OR event_count IS NULL
   OR revenue IS NULL
```

An assertion fails when its query returns rows. A successful assertion returns zero rows.

`definitions/assertions/daily_summary_grain_unique.sqlx`:

```sql
config {
  type: "assertion",
  description: "There must be one row per date, event type, and channel."
}

SELECT
  summary_date, event_type, channel, COUNT(*) AS row_count
FROM ${ref("daily_summary")}
GROUP BY summary_date, event_type, channel
HAVING COUNT(*) > 1
```

Dataform automatically uses references to infer dependencies. Assertions can be wired into workflow execution; verify the workflow's assertion settings and make sure critical checks actually gate downstream publishing.

### Incremental tables

Incremental tables can reduce repeated processing, but the incremental predicate is a correctness boundary. A naive `WHERE event_date > MAX(event_date)` can miss updates to existing dates or late-arriving events. For mutable data, consider a rolling reprocessing window, `uniqueKey`/merge behavior where appropriate, and periodic reconciliation.

Illustrative SQLX:

```sql
config {
  type: "incremental",
  schema: "bqml_lab",
  uniqueKey: ["summary_date", "event_type", "channel"],
  bigquery: {
    partitionBy: "summary_date",
    clusterBy: ["event_type", "channel"]
  }
}

SELECT
  event_date AS summary_date,
  event_type,
  channel,
  COUNT(*) AS event_count,
  SUM(amount) AS revenue
FROM ${ref("events")}
${when(incremental(), `
  WHERE event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
`, ``)}
GROUP BY summary_date, event_type, channel
```

This snippet illustrates an incremental processing window; do not assume the exact SQLX config or merge behavior is appropriate for every project. With `uniqueKey`, Dataform merges rows at the configured grain; each reprocessed date must therefore be aggregated from the complete source history for that date, not only from newly arrived rows. Validate the compiled SQL and merge behavior in a lab workspace. The three-day window must match the upstream lateness/update contract. If source events can change outside the window, this design can silently become stale. A production design should specify how the target is reconciled for historical corrections and test full-refresh behavior separately.

### Dataform operating checklist

- Compile before release; inspect generated SQL.
- Declare sources and use `ref()` for dependency tracking.
- Add assertions for grain, nullability, accepted values, and reconciliation.
- Use incremental tables only when the update semantics are understood.
- Keep SQLX and workflow settings in version control.
- Separate development and production release configurations.
- Record the Git revision, workflow invocation, row counts, and assertion outcomes.
- Use BigQuery job metadata and dry-run/cost controls.
- Do not treat a successful compile as proof of correct runtime results.

---

## 9. Generative AI and vector capabilities: boundaries and costs

Use these capabilities as targeted extensions of a governed SQL pipeline, not as magic SQL operators.

### When these capabilities fit

- Summarizing or classifying a small set of approved text records.
- Generating embeddings for semantic search or retrieval-augmented generation (RAG).
- Combining BigQuery data with supported remote models when the request/response workload fits the documented integration.
- Exploring semantic retrieval without standing up a separate serving stack for a modest workload.

### When to consider another platform or architecture

- Low-latency, high-QPS online inference with strict tail-latency requirements.
- Custom model architectures, training loops, specialized accelerators, or complex distributed training.
- Fine-grained model-serving controls, canary deployments, autoscaling policies, or complex online feature retrieval.
- Multi-step evaluation pipelines, data/model lineage, artifact promotion, approval gates, and recurring retraining across multiple services.
- Agentic workflows requiring tools, state, policy enforcement, and observability beyond a single model call.

### Cost and safety controls

- Estimate BigQuery query bytes and external model calls separately.
- Start with a sample and set quotas.
- Avoid generating embeddings repeatedly for unchanged documents; persist and version them.
- Cache results only when data freshness and privacy allow it.
- Filter and authorize retrieved documents before model prompting.
- Evaluate hallucination, retrieval relevance, prompt injection, and sensitive-data exposure.
- Track model identifier/version, prompt template version, input record ID, timestamp, status, token/call metrics where available, and cost attribution.
- Recheck current model availability and pricing before each rollout.

---

## 10. Model governance and lifecycle boundaries

### Model versioning

Avoid using `CREATE OR REPLACE MODEL production_model` as an unreviewed deployment strategy. A safer pattern is:

```text
churn_logistic_2026_10_01   -> candidate
churn_logistic_2026_10_15   -> candidate
churn_logistic_prod         -> controlled production alias/name or release target
```

BigQuery model naming and aliasing capabilities are not identical to a full model registry. Choose a versioning convention and promotion mechanism that your deployment system can enforce. Preserve the training SQL, source snapshot/version, feature contract, model options, evaluation results, approval, and rollback plan.

### Evaluation tables

Store evaluation results as durable records with:

- Model version and training run ID.
- Dataset/table snapshot or date range.
- Evaluation window and split strategy.
- Metric name/value, threshold, segment, and sample count.
- Baseline metric and release acceptance decision.
- Evaluation timestamp and code revision.

Do not overwrite historical evaluation evidence when retraining.

### Access control and governance

- Separate source-data read access, model creation, model usage, connection delegation, and production promotion.
- Restrict access to raw identifiers and sensitive features.
- Use policy tags, row-level security, and authorized views where appropriate.
- Do not expose prediction outputs broadly if they reveal sensitive inferred attributes.
- Restrict remote model connections and grant endpoint access to the connection service account only as required.
- Keep secrets out of SQL, model prompts, UDF source, and Git.
- Document data location, retention, lineage, and any external model processing.
- Apply organization policies and compliance reviews to remote inference and vector retrieval.

### Data leakage: critical failure mode

Leakage occurs when training features contain information unavailable at the moment the prediction would be made, or when the evaluation set influences preprocessing/model selection. Examples:

- A churn feature records a cancellation reason entered after the customer has churned.
- A “last 30 days” feature includes events after the prediction timestamp.
- Scaling, imputation, feature selection, or target encoding is fit using evaluation/test rows.
- Duplicate customers appear across train and evaluation in a way that leaks identity-specific information.
- Time-series evaluation uses dates earlier than the training cutoff or includes future covariates unavailable in production.

Define a prediction timestamp and label horizon first. Build point-in-time correct features. Split by time or entity when the deployment scenario requires it. Keep a final untouched test set for model selection workflows that need one. A small demo with a clear synthetic rule can demonstrate SQL mechanics, but its metrics do not establish production value.

### When BQML is enough vs Vertex AI

| Stay primarily in BigQuery ML when… | Consider Vertex AI / broader ML platform when… |
|---|---|
| Data is already in BigQuery and transformations are SQL-centric | Training needs custom Python frameworks, GPUs/TPUs, or specialized distributed training |
| A supported model family meets the quality and latency needs | Custom architectures, complex hyperparameter search, or bespoke training loops are required |
| Batch prediction or SQL-integrated inference is sufficient | Online serving needs autoscaling, traffic splitting, canaries, or strict latency control |
| Small-to-medium workflows can be operated with SQL, Dataform, and existing orchestration | The lifecycle needs managed pipelines, artifact lineage, repeatable component execution, and approval gates across services |
| The team can monitor and govern the model within existing data workflows | Feature store, model registry/monitoring, advanced deployment, or cross-system controls are material requirements |

This is a decision guide, not a product boundary that never changes. Verify current Vertex AI features and supported integrations before committing to an architecture. Some BigQuery ML remote-model workflows call Vertex AI without requiring the whole training and serving lifecycle to move out of BigQuery.

---

## 11. Hands-on exercises and lab checklist

The following lab artifacts are organized under `experiments/05_bqml_scheduling/`. Replace every `YOUR_PROJECT_ID`, bucket, connection, and location placeholder. Run in a disposable lab dataset.

| Lab | Artifact | Evidence of completion |
|---|---|---|
| 1. Setup | `01_setup_lab.sql` | Source table exists, partitioning/clustering confirmed |
| 2. Daily summary | `02_daily_summary.sql`, `03_refresh_daily_summary.sql` | One row per date/type/channel; validation queries pass |
| 3. Procedure and backfill | `04_create_refresh_procedure.sql`, `05_backfill_seven_days.sql` | Seven dates refresh without duplicate grain |
| 4. Logistic regression | `06_create_churn_demo.sql`, `07_train_logistic_regression.sql` | Model trains, evaluation metrics saved, predictions inspected |
| 5. ARIMA_PLUS | `08_create_daily_sales.sql` plus model/forecast SQL in Section 6 | Forecast returns 14 future points; evaluation approach documented |
| 6. Scheduled procedure | Configure scheduled query calling `refresh_daily_summary(@run_date)` | Transfer configuration, successful run, job metadata, and alert tested |
| 7. Dataform | `definitions/` SQLX files in Section 8 | Compile succeeds, dependency graph is correct, assertions return no rows |

### Exercise 1 — schedule the daily aggregate

- Configure a daily scheduled query using `CALL ...refresh_daily_summary(@run_date)`.
- Select the intended schedule time and time zone; document how logical date relates to business date.
- Configure notifications and verify the execution identity has least privilege.
- Validate output rows and query job metadata.
- Intentionally test a missing permission in a non-production lab and document the failure signal and recovery.

### Exercise 2 — backfill seven days

- Run the seven-day script twice.
- Confirm the second run does not create duplicates.
- Compare source and summary counts by date.
- Test one empty source date and decide how production completeness checks should behave.
- Explain why a blind append or whole-table overwrite would be unsafe.

### Exercise 3 — train and evaluate a classifier

- Create the synthetic churn table and inspect label balance.
- Train `LOGISTIC_REG` with the explicit Boolean custom split.
- Save evaluation metrics and prediction rows.
- Compare at least precision, recall, F1, ROC AUC (if returned), and log loss.
- Explain why this dataset cannot support a claim of real churn-model quality.
- Identify two leakage risks in a real churn feature table.

### Exercise 4 — forecast a time series

- Train `ARIMA_PLUS` on a time-indexed series.
- Forecast 14 points and inspect uncertainty intervals.
- Compare to a naive baseline and outline a rolling-origin backtest.
- Explain how missing dates, duplicate timestamps, outliers, and future covariates could change results.

### Exercise 5 — wrap the daily workflow

- Create the stored procedure.
- Test it manually for one date.
- Schedule a `CALL` using `@run_date`.
- Test alerting and failed-run recovery.
- Document the source readiness check and what constitutes a successful run beyond query completion.

### Exercise 6 — recreate in Dataform

- Declare the source.
- Create the daily summary table with `ref()`.
- Add null and uniqueness assertions.
- Compile and inspect the dependency graph.
- Run against the lab dataset.
- Confirm assertions are included as required actions in the workflow invocation and block publication when they fail.
- Decide whether full refresh or incremental processing is correct for the real update contract.

### Exercise 7 — platform decision memo

Write a one-page recommendation for a customer-churn workload. Include:

- Data size, freshness, inference latency, and serving pattern.
- Whether BigQuery ML logistic regression / boosted trees are sufficient.
- How model evaluation and promotion will work.
- What triggers a move to Vertex AI Pipelines or online serving.
- Security, privacy, model monitoring, cost, and rollback requirements.

### Cleanup

Delete lab objects when finished. Check dependencies before dropping a dataset.

```sql
DROP SCHEMA IF EXISTS `YOUR_PROJECT_ID.bqml_lab` CASCADE;
```

If you created a remote model connection, Vertex AI endpoint, GCS artifact, or other external resource, remove it separately according to your organization's change-control process. The SQL cleanup above only removes the dataset and its contents.

---

## 12. Troubleshooting and common mistakes

| Symptom / mistake | Likely cause | Corrective action |
|---|---|---|
| Scheduled query fails at runtime | Identity lacks source/destination permissions; API disabled; invalid query or region issue | Inspect transfer error and BigQuery job; fix the narrow missing permission or configuration |
| `@run_date` is unresolved in editor | Ad hoc query is not a scheduled transfer run | Supply a query parameter or test with a declared variable |
| A daily run creates duplicates | Append-only insert without stable key or replacement strategy | Use a transaction to refresh a single date or `MERGE` on a stable grain |
| Backfill overwrites history | Whole-table `WRITE_TRUNCATE` or table replacement | Scope the operation to requested dates and test the recovery plan |
| A successful query produces stale data | Upstream load late/incomplete; schedule dependency missing | Gate on source readiness and add freshness/reconciliation checks |
| Model training fails | Unsupported options, wrong label type, NULLs, incompatible feature types, or permissions | Check model-specific syntax and inspect feature schema before retraining |
| Accuracy looks unrealistically high | Synthetic target rule, leakage, duplicates, or bad split | Audit feature timestamps and split design; compare to a baseline and untouched holdout |
| Model performs well on random split but fails in production | Temporal/entity distribution shift | Use time-based or entity-aware validation aligned to deployment |
| Evaluation metric is misleading | Class imbalance or threshold mismatch | Inspect precision/recall, F1, ROC AUC, log loss, calibration and business costs |
| Feature transformation differs at inference | Preprocessing is not versioned or `TRANSFORM` is not used consistently | Store preprocessing with model where supported; test training and prediction parity |
| Forecast is implausible | Irregular timestamps, structural breaks, wrong frequency, or poor horizon | Inspect data quality, baseline, decomposition, and rolling-origin errors |
| Remote model permission denied | Connection service account lacks endpoint role or user lacks delegation permissions | Check connection identity, endpoint project IAM, and current remote-model guide |
| Remote call is expensive or slow | Per-row inference, large inputs, quota pressure, model latency | Sample, batch, cache where appropriate, set quotas, and measure end-to-end cost |
| Vector search returns unauthorized documents | ACL metadata not applied before results are returned | Filter by tenant/access policy and validate authorization before exposing content |
| Dataform incremental table misses corrections | Predicate excludes late-arriving or updated rows | Reprocess a rolling window, merge by unique key, and reconcile historical changes |
| Dataform compiles but results are wrong | Compilation validates generated workflow, not business correctness | Run assertions, compare counts, inspect generated SQL and lineage |
| `EXECUTE IMMEDIATE` creates injection risk | Untrusted string concatenated into identifiers or SQL | Use allowlisted identifiers and `USING` for values |
| Cost rises unexpectedly | Unbounded scans, model retraining, external model calls, repeated embeddings | Dry-run, partition filter, inspect jobs and model-call usage, version/calculate embeddings once |

### Common mistakes to avoid

- Treating a schedule as a successful-delivery guarantee.
- Assuming scheduled query system parameters are ordinary SQL variables.
- Retrying a non-idempotent operation without checking its prior effects.
- Backfilling by appending duplicates or truncating a shared table.
- Training on features that would not exist at prediction time.
- Choosing a metric without understanding business error costs.
- Believing high scores on a tiny synthetic dataset demonstrate business value.
- Assuming every BQML model supports every option or preprocessing function.
- Confusing imported models with remote models.
- Assuming every model endpoint, function, or vector index is available in every region.
- Sending sensitive data to a remote model without security/privacy review.
- Using Dataform incremental logic without defining late-arrival semantics.
- Granting broad IAM roles just to make a lab pass.
- Failing to record model version, training window, feature definitions, evaluation evidence, and rollback plan.

---

## 13. Knowledge checks with explained answers

### Questions

1. What is the difference between `@run_date` and `{run_date}`?
2. Why is a scheduled query not an execution guarantee?
3. What makes the daily refresh procedure idempotent?
4. Why is a transaction used around the date-specific delete and insert?
5. When would you choose a SQL UDF over a stored procedure?
6. What is the purpose of the custom train/evaluation split in the churn example?
7. Why can accuracy be misleading for an imbalanced churn label?
8. Give two examples of data leakage.
9. When is `ARIMA_PLUS` an appropriate model family?
10. How do imported models differ from remote models?
11. What does Dataform `ref()` provide?
12. Why can an incremental table miss late-arriving updates?
13. Name two signals that might justify moving from BQML to Vertex AI.
14. What must be checked before using generative AI functions or vector search?
15. Why is a model version plus an evaluation table important?

### Answers

1. `@run_date` is a GoogleSQL query parameter supplied to a scheduled query as a `DATE`. `{run_date}` is a DTS templating token used in supported transfer configuration fields, such as destination table naming. They are not interchangeable.
2. Runs can fail or be delayed due to IAM, quota, invalid SQL, upstream data readiness, region/service issues, or downstream dependencies. Monitor transfer runs, jobs, freshness, and quality.
3. For a given date, it deletes that date's old aggregate and inserts the recomputed aggregate in one transaction. Re-running the same date replaces that date's result rather than appending duplicates.
4. It prevents a committed intermediate state where the target date has been deleted but not yet repopulated. Transaction support and constraints should be verified for the exact statements used.
5. A SQL UDF is for reusable scalar expression logic; a stored procedure orchestrates multiple statements and can perform mutations.
6. It ensures evaluation examples are not used for training. A held-out evaluation set gives a more honest estimate than evaluating only on training rows.
7. If positives are rare, a model predicting “no churn” for everyone can have high accuracy and zero recall for churn. Inspect class-sensitive metrics and the business threshold.
8. Using a post-churn cancellation reason to predict churn; fitting scaling/imputation on the evaluation set; using future events in a historical feature; placing duplicates across splits.
9. For a numeric series with a meaningful time index when univariate forecasting fits the problem and there is sufficient history to validate. Compare it to a naive baseline and backtest chronologically.
10. Imported models bring a compatible artifact into BigQuery for supported inference; remote models reference supported external endpoints through a connection and invoke them from BigQuery. Their constraints and costs differ.
11. It declares a dependency/reference so Dataform can build the upstream relation before the downstream action and track the workflow graph.
12. If the incremental predicate only processes rows newer than the maximum existing timestamp, an update to an older row or late event can fall outside the predicate. Reprocessing and reconciliation policies are needed.
13. Need for custom training frameworks/accelerators; sophisticated managed pipelines and artifact lineage; strict online serving/canary/autoscaling; advanced model monitoring or multi-system lifecycle controls.
14. Current function/model support, syntax, region, permissions, connection identity, data location, quotas, and costs. Also verify privacy and access filtering.
15. It allows reviewers to tie a prediction system to its training data/code and to compare candidate models over time, support release approval, investigate regressions, and roll back.

---

## 14. Syllabus checkpoint

Mark each item only after you can demonstrate it in your lab.

- [ ] Explain scheduled-query architecture and distinguish transfer runs from BigQuery query jobs.
- [ ] Use `@run_date` and `@run_time` correctly and document timezone semantics.
- [ ] Configure a scheduled query, execution identity, and notifications.
- [ ] Demonstrate idempotent daily refresh and a seven-day backfill without duplicate grain.
- [ ] Monitor run status, query jobs, freshness, and reconciliation.
- [ ] Create and use a SQL UDF, JavaScript UDF, table function, and stored procedure.
- [ ] Use scripting variables, `IF`, loops, temporary tables, and safe `EXECUTE IMMEDIATE`.
- [ ] Train a `LOGISTIC_REG` model and explain its split strategy.
- [ ] Use `ML.EVALUATE` and `ML.PREDICT` and interpret appropriate metrics.
- [ ] Explain data leakage and point-in-time feature correctness.
- [ ] Use `TRANSFORM` where supported and preserve training/inference preprocessing parity.
- [ ] Train an `ARIMA_PLUS` model, forecast, and explain the need for chronological backtesting.
- [ ] Explain boosted trees, k-means, matrix factorization, and supported imported model families.
- [ ] Distinguish imported models, remote models, and built-in BQML models.
- [ ] Explain current generative AI, embeddings, and vector-search capabilities and their version-sensitive requirements.
- [ ] Build a Dataform dependency graph and assertions; explain incremental table risks.
- [ ] Document model versioning, evaluation evidence, access control, costs, and rollback.
- [ ] Justify when BQML is enough and when Vertex AI Pipelines or online serving is warranted.

**Pass condition:** every checkbox is supported by a working lab result, query/job metadata, or a short written design decision—not just by having read the lesson.

---

## 15. Summary and transition to Topic 06

BigQuery scheduled queries are a practical way to run recurring SQL, while BQML brings selected training, evaluation, prediction, and forecasting workflows into the warehouse. Production reliability comes from explicit date semantics, idempotent writes, safe backfills, least-privilege identity, source-readiness checks, failure monitoring, data-quality assertions, and model governance—not from scheduling alone.

Keep the model choice tied to the workload. Use SQL-centric BQML when the supported model family and batch/SQL inference fit. Use imported models for compatible artifacts and remote models when the supported endpoint integration is appropriate. Move to Vertex AI or a broader ML platform when custom training, managed pipeline stages, model promotion, or online-serving controls become important.

**Transition to Topic 06 — Pub/Sub and Dataflow (Apache Beam):** Topic 06 extends this foundation from scheduled batch SQL to event-driven and streaming pipelines. The same reliability principles still apply: define event-time semantics, handle duplicates, monitor lag and dead letters, enforce schemas, and make downstream writes safe to retry.

---

## 16. Official documentation references

These are the primary references used for syntax and capability checks. Documentation and service capabilities change; re-open the relevant reference before using a version-sensitive feature.

1. [Scheduling queries in BigQuery](https://cloud.google.com/bigquery/docs/scheduling-queries) — scheduled queries, `@run_date`, `@run_time`, templating, and configuration.
2. [BigQuery Data Transfer Service](https://cloud.google.com/bigquery/docs/dts-introduction) — transfer architecture and run monitoring.
3. [BigQuery scripting](https://cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language) — variables, loops, conditionals, dynamic SQL, and transactions.
4. [User-defined functions](https://cloud.google.com/bigquery/docs/user-defined-functions) — SQL and JavaScript UDFs.
5. [Table functions](https://cloud.google.com/bigquery/docs/table-functions) — parameterized table-valued queries.
6. [Stored procedures](https://cloud.google.com/bigquery/docs/procedures) — procedure creation and execution.
7. [BigQuery ML `CREATE MODEL` syntax](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-create) — model families and general options.
8. [Generalized linear models](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-create-glm) — linear/logistic regression options and data splits.
9. [BigQuery ML evaluation](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-evaluate) — evaluation functions and outputs.
10. [BigQuery ML prediction](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-predict) — prediction syntax.
11. [Feature preprocessing](https://cloud.google.com/bigquery/docs/bigqueryml-transform) — `TRANSFORM` and preprocessing behavior.
12. [Standard scaler](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-standard-scaler) — scaler syntax and persisted transformation behavior.
13. [ARIMA_PLUS model syntax](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-create-time-series) — model options, forecast and evaluation workflow.
14. [Imported model journeys](https://cloud.google.com/bigquery/docs/e2e-journey-import) — supported imported model formats and inference workflows.
15. [ONNX import syntax and limitations](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-create-onnx) — format-specific restrictions.
16. [Remote models](https://cloud.google.com/bigquery/docs/bigqueryml-remote-model) — connections, supported endpoints, IAM, and locations.
17. [Generate text with AI in BigQuery](https://cloud.google.com/bigquery/docs/generate-text) — current `AI.GENERATE_TEXT` interface and supported remote models.
18. [Generate text embeddings](https://cloud.google.com/bigquery/docs/generate-text-embedding) — embedding model integration and IAM.
19. [Vector search tutorial](https://cloud.google.com/bigquery/docs/vector-index-text-search-tutorial) — embeddings, vector indexes, `VECTOR_SEARCH`, and RAG.
20. [Dataform overview](https://cloud.google.com/dataform/docs/overview) — SQLX workflows, dependencies, assertions, and documentation.
21. [Dataform dependencies](https://cloud.google.com/dataform/docs/dependencies) — dependency graph and assertion behavior.
22. [Dataform tables and incremental tables](https://cloud.google.com/dataform/docs/create-tables) — table types and incremental configuration.
23. [BigQuery pricing](https://cloud.google.com/bigquery/pricing) and [Vertex AI pricing](https://cloud.google.com/vertex-ai/pricing) — verify current pricing for your region and workload.
24. [BigQuery IAM](https://cloud.google.com/bigquery/docs/access-control) — current roles and permissions.

---

## Validation notes

- **Roadmap alignment:** covers Topic 05 basics, intermediate, and advanced concepts; includes the prescribed scheduled daily aggregate, seven-day backfill, logistic regression, `ARIMA_PLUS`, stored procedure scheduling, and Dataform reconstruction.
- **Topic 03 dependency:** uses partition filters, dry-run/cost guardrails, targeted date refresh, and query/job monitoring.
- **Topic 04 dependency:** assumes explicit schemas, source readiness, raw-to-curated processing, reconciliation, and late-arriving-data controls.
- **Static review:** headings, examples, parameter semantics, model-family distinctions, safety cautions, and documentation links were reviewed. Model-family examples that reference `regression_training` or `user_item_ratings` are schema-dependent templates; those source tables must be created and validated before execution. The code includes project/location/model placeholders that must be replaced.
- **Live execution:** **not executed** in a live BigQuery project. No claim is made that the SQL, transfer configuration, remote model, or Dataform workflow has been run end to end.
- **Unresolved environment-specific items:** project/dataset IDs, location compatibility, organization IAM policy, APIs, model endpoint availability, quotas, current pricing, Dataform project-generation settings, and any preview/GA changes must be verified in the target GCP environment.
