# Data Drift Monitoring for ML Pipelines

> **Stage 2C — Data Engineering_3 · Module 10: Big Data ML and MLOps Handoff · Topic 05**
>
> Target: `Stage 2C — Data Engineering_3/10-Big-Data-ML-and-MLOps-Handoff/05-data-drift-monitoring-for-ml-pipelines.md`
>
> This lesson focuses on the data engineering side of production ML: validating incoming data, comparing reference and current windows, detecting meaningful distribution changes, measuring performance when labels arrive late, and operating safe alert/retraining workflows.

---

## 1. Learning outcomes

By the end of this lesson, you should be able to:

1. Distinguish **data drift**, **concept drift**, **label drift**, seasonality, upstream pipeline failures, and feedback-loop effects.
2. Monitor schema, freshness, null rates, ranges, feature distributions, prediction distributions, and business outcomes.
3. Select and interpret PSI, Kolmogorov–Smirnov (KS), chi-square, Jensen–Shannon (JS), and Wasserstein statistics.
4. Explain why statistical significance, drift magnitude, model-performance degradation, and business impact are different things.
5. Validate data quality before interpreting distribution metrics.
6. Join delayed labels to logged predictions using stable identifiers and correct time semantics.
7. Use reference windows, rolling baselines, and seasonality-aware comparisons.
8. Understand the roles and limitations of Evidently, whylogs, Great Expectations, NannyML, and cloud monitoring services.
9. Reduce raw-data scans by retaining per-window summaries and appropriate sketches.
10. Monitor segments while controlling multiple-comparison risk and alert floods.
11. Design severity levels, runbooks, escalation, retraining triggers, and champion-versus-challenger promotion gates.
12. Close the loop with prediction/outcome logging, lineage, fairness monitoring, audit evidence, and awareness-level generative-AI monitoring.

### The core distinction

A drift detector answers a narrow question: **“Does this observed data look different from the chosen reference under this measurement?”** It does not, by itself, answer whether the model is less accurate, whether the difference is caused by a pipeline bug, or whether retraining is the correct response.

A defensible monitoring system proceeds in this order:

```text
Observe → validate data quality → classify the change → quantify drift
        → assess business/model risk → alert or investigate
        → evaluate with labels when available → consider retraining
        → compare candidate with champion → promote or reject
```

---

## 2. Prerequisites and environment setup

### 2.1 Prerequisites

You should understand:

- Python, pandas, NumPy, automated tests, and basic statistical summaries.
- SQL tables, windowing, timestamps, joins, and incremental pipelines.
- Classification predictions, probability scores, labels, precision/recall, and AUC.
- Dataset snapshots, feature lineage, model versions, and prediction logs from Topics 02–04.
- Basic hypothesis testing and confidence intervals from Module 2C.9 Topic 03.
- Sampling and sketches from Module 2C.9 Topic 02.
- Alert ownership and incident-response concepts.

### 2.2 Project layout

The hands-on project is `experiments/05_drift/`:

```text
experiments/05_drift/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── generate_data.py
│   ├── drift_metrics.py
│   ├── monitor.py
│   ├── delayed_labels.py
│   ├── policy.py
│   └── retraining_gate.py
├── tests/
│   ├── test_drift_metrics.py
│   └── test_quality_gate.py
└── data/
    └── .gitkeep
```

This local lab generates controlled synthetic weekly datasets. It does not connect to a cloud monitoring service, page an on-call engineer, or train a production-ready model. It provides runnable building blocks and deliberately records decisions as data.

### 2.3 Environment

Use a Python version supported by the chosen package releases (Python 3.11 is a reasonable baseline). Create and activate a virtual environment:

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
numpy==2.3.4
pandas==2.3.3
scipy==1.16.2
scikit-learn==1.7.2
pyarrow==21.0.0
pytest==8.4.2
evidently==0.7.14
```

These are example pins, not a claim that they are the latest versions or compatible with every Python/platform combination. Install in a clean Python 3.11 environment and retain the resolved lock file for repeatability; validate package metadata on your platform. The Evidently example uses the 0.7-era `Report`/`DataDriftPreset` API pattern: `Report.run(...)` returns a snapshot, and HTML export is performed on that returned snapshot. Re-check this against the exact installed release before deployment.

Install and set the import path from the project root:

```bash
python -m pip install -r requirements.txt
# macOS/Linux
export PYTHONPATH=.
# Windows PowerShell
# $env:PYTHONPATH = "."
```

### 2.4 Monitoring is not just a chart

A production monitoring record should preserve enough context to interpret a metric later:

```text
model_name, model_version, feature_name, segment, window_start, window_end,
reference_id, current_data_id, metric_name, metric_value, p_value,
sample_size_reference, sample_size_current, quality_status, alert_status,
monitor_version, computed_at_utc, pipeline_run_id
```

Do not store only “drift = true.” Record the statistic, inputs/windows, sample sizes, quality-gate outcome, and policy version. Without this context, an alert cannot be reproduced or audited.

---

## 3. Why models degrade: types of change

### 3.1 Data drift / covariate shift

**Data drift** means the distribution of observed model inputs changes over time, often written as \(P_t(X) \ne P_{ref}(X)\).

Examples:

- Customer tenure shifts because a new acquisition channel brings more new customers.
- Average transaction amount rises during a holiday period.
- Mobile traffic becomes a larger share of requests.
- A new device type appears.

Input-only monitoring can detect changes in \(P(X)\), assuming the input data is correctly collected and represented. It cannot establish that model accuracy has fallen. A change can be harmless if the model remains valid over the new region of feature space; conversely, a subtle change may be important even if an aggregate distribution metric is small.

### 3.2 Concept drift

**Concept drift** means the relationship between inputs and the target changes, often expressed as \(P_t(Y \mid X) \ne P_{ref}(Y \mid X)\).

Examples:

- Fraudsters change tactics, so the same transaction pattern has a different fraud probability.
- Customers react differently to a pricing policy.
- A product change alters which behavior predicts churn.

Concept drift usually requires outcome labels or additional assumptions to verify. Input distribution metrics alone cannot directly establish a changed \(P(Y \mid X)\). If labels are delayed, use input drift as an early investigation signal, not as proof of concept drift.

### 3.3 Label drift / prior probability shift

**Label drift** usually refers to a change in the target prevalence \(P(Y)\), such as the fraud rate rising from one period to another. Terminology varies across literature and tools, so document the definition used by your team.

A change in \(P(Y)\) may alter precision, calibration, or the optimal decision threshold even if \(P(X \mid Y)\) remains stable. Label drift cannot generally be confirmed without labels or a defensible estimate of the label distribution.

### 3.4 Upstream data-pipeline failure

A broken pipeline can mimic drift:

- a currency field changes from dollars to cents;
- a timestamp parser changes timezone;
- nulls are replaced with zero;
- a join begins duplicating rows;
- a categorical encoding changes;
- an upstream schema renames or drops a column;
- a source sends only one region due to a filter bug.

These are first data-quality or contract incidents. A drift score computed over corrupted values may be mathematically valid but operationally misleading. Validate the data contract and source lineage before classifying the change as natural drift.

### 3.5 Seasonality

Seasonality is a repeatable time pattern: day of week, month, holidays, school calendars, billing cycles, or annual events. Comparing a holiday week only to an ordinary week can produce a recurring false alarm.

Possible controls:

- compare like-for-like seasonal periods;
- include known calendar variables in analysis;
- maintain a rolling baseline plus a seasonal reference;
- model expected seasonal ranges;
- distinguish an expected seasonal alert from an unexpected deviation.

Do not automatically suppress every recurring change. A seasonal shift may still harm a model if the model was not trained or validated for that regime.

### 3.6 Feedback loops and selective labels

Predictions influence the data later observed. Examples:

- a recommender displays items it already predicts users will click, reducing exposure to alternatives;
- a fraud model blocks transactions, so blocked transactions never produce the same outcome labels as approved transactions;
- a churn intervention changes the probability that a customer leaves.

The observed labels are then **policy-dependent**. A model trained only on outcomes for the cases it allowed through may learn a biased view of reality. Record the decision policy, exposure, action, and outcome; use controlled experiments, review samples, or appropriate causal methods when justified. Do not assume the production label stream is an unbiased sample of all possible outcomes.

### 3.7 What can be observed without labels?

| Signal | Usually observable from inputs/predictions alone? | What it can establish |
|---|---|---|
| Schema, missingness, ranges, freshness | Yes | Contract/quality status |
| Feature distribution drift | Yes | Distribution changed relative to a chosen baseline |
| Prediction score distribution | Yes | Model outputs changed; cause remains uncertain |
| Actual accuracy, recall, AUC, calibration against outcomes | No, labels needed | Realized model performance on labeled cases |
| Label prevalence | Labels or a defensible estimate needed | Target mix changed |
| Concept drift | Usually requires labels or assumptions | Input-target relationship changed |
| Business impact | Outcome/business data needed | Changes in value, cost, risk, or customer behavior |
| Estimated performance without labels | Sometimes | Model-dependent estimate under explicit assumptions, not ground truth |

---

## 4. What to monitor and how to choose baselines

### 4.1 Monitoring layers

Use layered checks instead of one all-purpose drift score.

| Layer | Signals | Typical failure detected |
|---|---|---|
| Ingestion and pipeline | Freshness, row counts, duplicate rate, source lag, job status | Pipeline stopped, partial load, duplicate replay |
| Schema and contracts | Missing/extra columns, types, nullability, categorical domain | Breaking schema or encoding change |
| Value quality | Null/invalid rate, min/max, finite values, impossible combinations | Unit error, malformed records, default-value bug |
| Feature distributions | Quantiles, histograms, PSI/KS/JS/Wasserstein | Population or feature mix changed |
| Prediction distributions | Score quantiles, positive-rate, entropy/confidence where meaningful | Model output behavior changed |
| Outcomes and performance | Label prevalence, loss, precision/recall, AUC, calibration, business KPIs | Realized quality or business impact changed |
| Slices | Same metrics by region, device, cohort, product, channel | Localized failure hidden by aggregate metrics |
| Operations | Alert lag, monitoring job failures, metric freshness, cost | Monitoring itself is broken or too late |

### 4.2 Reference and current windows

- **Reference window:** a stable period chosen to represent expected behavior. It might be a curated training/validation set, a recent stable production period, or a seasonal counterpart.
- **Current window:** the production records being evaluated now.
- **Rolling baseline:** a moving reference updated over time.
- **Seasonal baseline:** comparable historical windows, such as the same weekday or month.
- **Training baseline:** useful for measuring how production differs from training, but not always the right baseline for current expected behavior.

Record baseline identity and dates. If the baseline is refreshed every week without governance, gradual drift can be absorbed into the baseline and become invisible. Conversely, a very old training baseline may produce constant alerts for harmless changes in product mix.

### 4.3 Baseline refresh policy

A defensible policy specifies:

1. Which dataset/version qualifies as the baseline.
2. Minimum sample size and required quality checks.
3. Whether the baseline is fixed, rolling, or seasonal.
4. Who approves a refresh and why.
5. How old baselines are retained for historical comparison.
6. How the new baseline is evaluated for contamination or drift.
7. How monitoring results are versioned when bin edges or feature definitions change.

Do not refresh a baseline automatically from a known-bad period. A baseline should be promoted as a governed artifact, with lineage and approval.

### 4.4 Monitoring frequency

Choose frequency from the business's detection deadline and the rate at which data accumulates. A daily batch model may be monitored daily; a high-risk online fraud model may need near-real-time quality signals and frequent aggregates. Label-based performance may only be meaningful weekly or monthly if labels mature slowly.

The monitoring window must contain enough observations for stable estimates. Very small windows can make statistics noisy; very large windows can hide a sudden incident. Track sample size and window duration alongside every metric.

---

## 5. Drift statistics and interpretation

No statistic is a universal drift detector. The choice depends on data type, sample size, scale, assumptions, and operational purpose. Use more than one view when appropriate: a test statistic, a magnitude/effect-size metric, and domain-specific quality checks.

### 5.1 Population Stability Index (PSI)

PSI compares the proportion of observations in bins between a reference and current distribution. For bins \(i=1,\dots,k\):

\[
\operatorname{PSI}=\sum_{i=1}^{k}(p_i-q_i)\ln\left(\frac{p_i}{q_i}\right)
\]

where \(p_i\) and \(q_i\) are the reference and current bin proportions. Practical implementations add a small smoothing constant to avoid \(\log(0)\).

**Data types:** numeric features after binning; categorical features after defining stable categories/bins.

**Interpretation:** PSI is non-negative and zero when bin proportions match. Larger values mean more binned distribution difference. Common rules of thumb such as 0.1 or 0.25 are heuristics, not universal statistical laws. Calibrate thresholds against historical noise and business impact.

**Important choices and limitations:**

- Prefer bin edges fixed from the reference window; recomputing quantile bins independently each week can conceal changes.
- Too few bins can hide local differences; too many bins can create sparse cells.
- PSI discards within-bin detail and depends on binning.
- Very large samples can make small differences yield noticeable PSI; very small samples make estimates unstable.
- Smooth zero counts carefully and record the smoothing rule.
- PSI is a magnitude-style comparison, not a p-value and not a direct measure of model-performance loss.

### 5.2 Kolmogorov–Smirnov (KS) two-sample test

For two samples of a numeric variable, the two-sample KS statistic is the largest absolute difference between empirical cumulative distribution functions:

\[
D_{n,m}=\sup_x |F_n(x)-G_m(x)|
\]

The test evaluates a null hypothesis that the samples come from the same continuous distribution under the test's assumptions. SciPy's `ks_2samp` returns a statistic and p-value.

**Data types:** continuous/numeric observations. The classical distribution-free interpretation assumes independent samples from continuous distributions. Ties, heavy discreteness, dependence, or time-series autocorrelation require care.

**Interpretation:** the statistic \(D\) is an effect-size-like maximum CDF gap; the p-value reflects evidence against the null under assumptions. Do not use the p-value alone to choose operational severity.

**Limitations:** with huge samples, tiny and irrelevant changes can be significant; with small samples, meaningful changes may not be detected. Repeated weekly tests inflate false positives unless monitoring policy accounts for repeated looks.

### 5.3 Chi-square test for categorical distributions

For categorical counts, compare observed frequencies to expected frequencies. A two-sample distribution comparison can be represented as a contingency table with rows `reference/current` and columns for categories. The chi-square test evaluates independence between period and category.

\[
\chi^2=\sum_{i}\frac{(O_i-E_i)^2}{E_i}
\]

where \(O_i\) and \(E_i\) are observed and expected counts.

**Data types:** categorical counts. Use a consistent category vocabulary and explicitly handle new/unseen categories.

**Assumptions and limitations:**

- Expected cell counts should be adequate for the asymptotic approximation; sparse tables may require category grouping or an exact/Monte Carlo alternative where available.
- Do not feed raw category strings to a numeric test.
- Rare categories can produce unstable results and privacy issues in segmented reporting.
- A significant result says category proportions differ; it does not identify the cause or prove model degradation.

### 5.4 Jensen–Shannon divergence and distance

Jensen–Shannon (JS) divergence symmetrizes Kullback–Leibler divergence using the midpoint distribution \(M=(P+Q)/2\):

\[
\operatorname{JSD}(P,Q)=\frac12 D_{KL}(P\|M)+\frac12 D_{KL}(Q\|M)
\]

JS **distance** is the square root of JS divergence. Libraries may return the distance rather than divergence; check the API. SciPy's `scipy.spatial.distance.jensenshannon` returns the distance and normalizes probability vectors if needed.

**Data types:** probability vectors, commonly histogram or categorical proportions. Numeric features need a shared binning scheme or density representation.

**Interpretation:** with logarithm base 2, JS divergence lies in \([0,1]\); JS distance then lies in \([0,1]\). With another logarithm base, scaling differs. Always document the base and whether the stored metric is distance or divergence.

**Limitations:** histogram binning matters; it does not preserve numeric distances between bins; and a value has no universal “bad drift” threshold independent of context.

### 5.5 Wasserstein-1 distance

The one-dimensional Wasserstein-1 distance (earth mover's distance) measures the minimum cost of transporting probability mass to transform one distribution into another. Intuitively, it accounts for how far probability mass must move along the numeric axis.

**Data types:** numeric values, especially useful when scale and magnitude are meaningful. SciPy provides `scipy.stats.wasserstein_distance`.

**Interpretation:** the result is in the same units as the variable for a one-dimensional feature. A distance of 5 means different things for dollars, days, and normalized ratios; scale features or normalize the metric when comparisons across features are needed.

**Limitations:** it is scale-sensitive, requires careful treatment of units, and is not a significance test. It can be affected by outliers. For categorical features, arbitrary numeric category codes do not give meaningful distances.

### 5.6 Which method should I use?

| Method | Suitable input | Main output | Strength | Main caution |
|---|---|---|---|---|
| PSI | Binned numeric or categorical proportions | Non-negative scalar | Simple, interpretable monitoring convention | Bin-sensitive; heuristic thresholds |
| KS two-sample | Numeric samples | Statistic \(D\), p-value | Detects CDF differences | Assumptions, sample-size sensitivity, repeated testing |
| Chi-square | Categorical counts/contingency table | \(\chi^2\), p-value | Tests category-mix changes | Sparse expected counts; category vocabulary |
| JS divergence/distance | Shared histogram/categorical distributions | Bounded divergence/distance depending on base | Symmetric; handles zero-probability bins robustly with midpoint | Must distinguish distance from divergence; bin-sensitive |
| Wasserstein-1 | Numeric samples | Distance in feature units | Captures magnitude/distance of shifts | Unit-sensitive; not a significance test |

### 5.7 Practical calculations: `src/drift_metrics.py`

The following implementation uses fixed reference-derived bins for PSI and JS, SciPy for KS, chi-square, and Wasserstein, and explicit metadata for sample sizes. It is a small-data reference implementation; do not apply it to millions of raw rows in every monitoring run without a cost plan.

```python
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import chi2_contingency, ks_2samp, wasserstein_distance


def _numeric_clean(series: pd.Series) -> np.ndarray:
    values = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float)
    return values[np.isfinite(values)]


def fixed_reference_edges(reference: pd.Series, bins: int = 10) -> np.ndarray:
    """Create shared edges from reference quantiles, then freeze for comparisons."""
    if bins < 2:
        raise ValueError("bins must be at least 2")
    values = _numeric_clean(reference)
    if len(values) < 2:
        raise ValueError("Need at least two finite reference values")
    quantiles = np.linspace(0, 1, bins + 1)
    edges = np.unique(np.quantile(values, quantiles))
    if len(edges) < 2:
        # Constant reference: create a narrow interval; out-of-range current values
        # are captured by infinite outer edges below.
        value = float(values[0])
        edges = np.array([value - 0.5, value + 0.5])
    edges[0] = -np.inf
    edges[-1] = np.inf
    return edges


def _proportions(values: np.ndarray, edges: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    counts, _ = np.histogram(values, bins=edges)
    p = counts.astype(float) + eps
    return p / p.sum()


def psi_numeric(reference: pd.Series, current: pd.Series, bins: int = 10) -> float:
    ref = _numeric_clean(reference)
    cur = _numeric_clean(current)
    if len(ref) == 0 or len(cur) == 0:
        raise ValueError("PSI requires non-empty finite samples")
    edges = fixed_reference_edges(pd.Series(ref), bins=bins)
    p = _proportions(ref, edges)
    q = _proportions(cur, edges)
    return float(np.sum((p - q) * np.log(p / q)))


def numeric_drift(reference: pd.Series, current: pd.Series) -> dict[str, Any]:
    ref_raw = pd.to_numeric(reference, errors="coerce").to_numpy(dtype=float)
    cur_raw = pd.to_numeric(current, errors="coerce").to_numpy(dtype=float)
    ref = ref_raw[np.isfinite(ref_raw)]
    cur = cur_raw[np.isfinite(cur_raw)]
    if len(ref) < 2 or len(cur) < 2:
        raise ValueError("Need at least two finite observations in each window")
    edges = fixed_reference_edges(pd.Series(ref), bins=10)
    p = _proportions(ref, edges)
    q = _proportions(cur, edges)
    return {
        "n_reference": int(len(ref)),
        "n_current": int(len(cur)),
        "n_reference_raw": int(len(ref_raw)),
        "n_current_raw": int(len(cur_raw)),
        "n_reference_invalid_or_missing": int(len(ref_raw) - len(ref)),
        "n_current_invalid_or_missing": int(len(cur_raw) - len(cur)),
        "psi": psi_numeric(pd.Series(ref), pd.Series(cur)),
        "ks_statistic": float(ks_2samp(ref, cur, alternative="two-sided", method="auto").statistic),
        "ks_p_value": float(ks_2samp(ref, cur, alternative="two-sided", method="auto").pvalue),
        # SciPy returns JS distance, i.e. sqrt(JS divergence).
        "js_distance": float(jensenshannon(p, q, base=2)),
        "wasserstein_1": float(wasserstein_distance(ref, cur)),
    }


def categorical_drift(reference: pd.Series, current: pd.Series) -> dict[str, Any]:
    ref = reference.astype("string").fillna("<MISSING>")
    cur = current.astype("string").fillna("<MISSING>")
    categories = sorted(set(ref.unique()) | set(cur.unique()))
    ref_counts = ref.value_counts().reindex(categories, fill_value=0)
    cur_counts = cur.value_counts().reindex(categories, fill_value=0)
    table = np.vstack([ref_counts.to_numpy(), cur_counts.to_numpy()])
    if table.shape[1] < 2:
        # No distribution comparison is meaningful if only one category exists
        # across both windows; record the identical/constant case explicitly.
        return {
            "n_reference": int(len(ref)),
            "n_current": int(len(cur)),
            "chi2_statistic": 0.0,
            "chi2_p_value": 1.0,
            "categories": categories,
            "expected_min_count": float(min(len(ref), len(cur))),
            "warning": "Only one category across both windows",
        }
    chi2, p_value, dof, expected = chi2_contingency(table, correction=False)
    return {
        "n_reference": int(len(ref)),
        "n_current": int(len(cur)),
        "chi2_statistic": float(chi2),
        "chi2_p_value": float(p_value),
        "degrees_of_freedom": int(dof),
        "expected_min_count": float(expected.min()),
        "categories": categories,
        "warning": (
            "Sparse expected counts: consider grouping rare categories or an "
            "appropriate exact/Monte Carlo method"
            if expected.min() < 5 else None
        ),
    }
```

**Interpretation rules:**

- This code drops non-finite numeric values for statistical calculations; the monitor must separately report how many were dropped. Otherwise a quality failure could disappear from the drift metric.
- The PSI bin edges come from the reference and are reused for the current sample. Store those edges or their version in production.
- Quantile-derived edges may be duplicated for discrete/constant data. The helper removes duplicates; this changes the effective number of bins and should be recorded in production metadata.
- The categorical test includes missingness as a category, but missingness should also have its own quality metric.
- `expected_min_count < 5` is a common diagnostic heuristic, not an absolute law. For sparse tables, use a suitable exact/Monte Carlo approach or combine rare categories only when the business meaning supports it.
- The functions return measurements; they do not decide whether to page, retrain, or promote a model.

### 5.8 Sample size, repeated tests, and false alarms

If you test 100 independent features at a nominal 5% significance level, under a global null you expect about 5 false-positive tests on average. Repeating those tests weekly increases the chance of at least one alert over time. Features and windows are often correlated, so the exact probability differs, but the core operational problem remains.

Controls include:

- use p-values together with effect sizes and minimum sample sizes;
- define a family of tests and consider false-discovery-rate control (for example, Benjamini–Hochberg) when appropriate;
- require persistence across multiple windows for low-risk signals;
- use control charts or calibrated historical limits for stable metrics;
- alert on business-relevant combinations rather than every raw feature;
- separate warning/ticket thresholds from paging thresholds;
- record the policy version and alert reason.

Do not use a blanket rule like “page when any p-value is below 0.05.” Statistical significance is not business significance, and a drift statistic is not a model-performance metric.

---

## 6. Data quality versus genuine drift

### 6.1 Validate first, compare second

A recommended sequence:

1. **Pipeline health:** did the job complete, arrive on time, and read the expected source partitions?
2. **Schema contract:** are required columns present with compatible types and allowed schema versions?
3. **Structural quality:** row counts, duplicate keys, missingness, invalid formats, unexpected categories.
4. **Semantic quality:** units, ranges, timezone conventions, valid combinations, denominator behavior.
5. **Coverage and composition:** expected regions/channels/cohorts are represented.
6. **Drift metrics:** compare only after the data-quality status is known.
7. **Interpretation:** compare multiple metrics, inspect feature slices, and consult upstream lineage.
8. **Action:** repair the pipeline, investigate the population change, or escalate according to policy.

### 6.2 Example diagnostic patterns

| Observation | Likely first hypothesis | Next check |
|---|---|---|
| Null rate suddenly rises from 1% to 80% | Source or parsing failure | Upstream schema, ingestion logs, join coverage |
| Currency median changes from 70 to 7,000 | Unit conversion or cents/dollars error | Source contract and raw values |
| One category disappears entirely | Filter/join issue or real population change | Source counts and segment coverage |
| Numeric feature changes gradually with stable quality | Possible genuine data drift | Compare segments, seasonality, upstream product changes |
| Input distributions stable but measured AUC falls | Concept drift, label issue, or evaluation mismatch | Label quality/delay, calibration, outcome joins |
| Score distribution changes but input features do not | Model/config/threshold change or hidden feature change | Loaded model version, preprocessing, request path |
| Drift appears only for one device type | Localized change or instrumentation defect | Device-specific pipeline and sample size |
| Every feature changes on the same day | Shared upstream transformation, schema, or source shift | Pipeline release history and data lineage |

### 6.3 Quality gates must be distinct from drift warnings

A quality gate can block downstream interpretation or publication. A drift warning typically asks for investigation and does not automatically imply the input is invalid.

Example policy:

```text
if schema_contract_failed or critical_quality_check_failed:
    mark_window = "INVALID_DATA"
    block drift-based retraining decision
    page data pipeline owner if severity is critical
elif drift_effect_is_large and persists and business_risk_is_high:
    mark_window = "DRIFT_WARNING" or "DRIFT_CRITICAL"
    create an investigation ticket / page per policy
else:
    mark_window = "HEALTHY" or "WATCH"
```

Do not suppress the fact that data changed; classify it as an upstream data-quality incident when appropriate. Also avoid calculating drift on corrupted values and then presenting it as evidence that the business population changed.

---

## 7. Delayed labels and model-performance monitoring

### 7.1 Why labels arrive late

Many labels are not available at prediction time:

- churn may require a 30- or 90-day observation window;
- fraud chargebacks may arrive weeks later;
- loan defaults can take months;
- support outcomes may require a resolution and customer response.

This creates a lag between an input shift and measurable model-performance change. Monitor inputs and predictions early, then measure realized performance when labels mature.

### 7.2 Prediction and outcome data model

At prediction time, record a durable prediction row:

```text
prediction_id (unique)
entity_id or privacy-approved key
prediction_timestamp_utc
model_name
model_version
feature_snapshot_id or feature_timestamp
prediction_score
decision_threshold/version
prediction
segment attributes as allowed
```

When ground truth becomes available, store it separately:

```text
outcome_id
prediction_id or stable join key
label
label_available_timestamp_utc
outcome_window_start
outcome_window_end
label_version/source
```

Use `prediction_id` as the preferred join key when one prediction corresponds to one outcome. If the join is based on entity and time, define the exact prediction horizon and resolve multiple predictions explicitly. Joining an outcome to the latest prediction by accident can create label leakage or incorrect metrics.

### 7.3 Join semantics

For a churn prediction made at time \(t\), a label might be “cancelled within the next 30 days.” The label is not mature until the 30-day outcome window has elapsed and source systems have finalized the result. Exclude immature predictions from realized performance calculations rather than treating missing labels as negatives.

A simplified SQL pattern:

```sql
SELECT
    p.prediction_id,
    p.prediction_timestamp_utc,
    p.model_version,
    p.prediction_score,
    o.label,
    o.label_available_timestamp_utc
FROM prediction_log AS p
JOIN outcomes AS o
  ON p.prediction_id = o.prediction_id
WHERE o.label_available_timestamp_utc <= :evaluation_as_of_utc
  AND o.outcome_window_end <= :evaluation_as_of_utc;
```

In a real system, account for corrected labels, duplicate outcome events, censored cases, opt-outs, and label-specific maturity rules.

### 7.4 Performance metrics over time

For binary classification, common measures include:

- precision and recall at a fixed decision threshold;
- ROC AUC or PR AUC when ranking quality matters;
- calibration (whether predicted probabilities match observed frequencies);
- confusion matrix and false-positive/false-negative cost;
- business outcomes, such as prevented loss or retained customers.

Always state the evaluation cohort, model version, label maturity cutoff, sample size, and metric definition. AUC can be undefined if only one class appears in a window; tiny segments can produce unstable estimates. Compare like-for-like cohorts when possible.

### 7.5 Proxy metrics and estimated performance

Without labels, you can monitor feature drift, score distributions, prediction rates, model confidence, and business process indicators. These are **proxies**, not proof of predictive accuracy.

Some tools estimate performance without ground truth. For example, confidence-based performance estimation for classification relies on assumptions about probability calibration and the relationship between predicted confidence and correctness. Direct-loss estimation approaches use a separately trained estimator. These can be useful early-warning signals, but their assumptions must be validated against labeled periods and estimates must be labeled as estimates.

Do not report an estimated AUC or estimated error rate as measured truth. Keep separate fields such as `metric_kind = measured | estimated | proxy`, and back-test the estimator when labels eventually arrive.

### 7.6 Monitoring the delay itself

Track label coverage and delay:

- percentage of predictions with mature labels;
- label-arrival delay distribution;
- percentage of outcomes missing beyond the expected SLA;
- outcome source freshness;
- performance by prediction cohort and model version.

A drop in label coverage may be a label pipeline failure rather than improved model performance. Avoid evaluating only early-arriving labels if label delay is correlated with outcome class.

---

## 8. Monitoring tools and their roles

Tool capabilities and APIs change; verify the selected version and deployment mode before implementation. These tools overlap but are not interchangeable.

| Tool | Main role | Typical use | Important boundary |
|---|---|---|---|
| Evidently | Data/model evaluation reports and monitoring metrics | Compare reference/current data; create HTML reports; integrate checks into pipelines | A report is not a complete alerting, ownership, or incident-response system |
| whylogs | Data profiling and compact profile representations | Capture statistical summaries over windows; compare profiles and visualize drift | Profile metrics can lose detail; configure columns, types, and sampling appropriately |
| Great Expectations | Data contracts and expectation-based validation | Assert schema, ranges, null rates, uniqueness, and other quality rules | Primarily a validation layer; distribution monitoring and model-performance logic may need additional design |
| NannyML | Drift analysis and performance estimation without immediate labels | Monitor input shift and estimate performance under documented assumptions | Estimates are not ground truth; support differs by algorithm and model task |
| SageMaker Model Monitor | Managed monitoring for supported SageMaker inference workflows | Baselines, captured inference data, quality/model-quality checks, reports and CloudWatch integration | AWS currently documents an availability change: no longer open to new customers; existing customers may continue using it. Verify current service status before choosing it |
| Vertex AI Model Monitoring | Managed monitoring integrated with Vertex AI prediction workflows | Feature skew/drift and platform-specific monitoring | Capabilities and supported prediction modes vary by generation/configuration; check current docs and region availability |
| Databricks Data Quality Monitoring / Data Profiling (formerly Lakehouse Monitoring) | Table profiling, time-series/snapshot metrics, drift metric tables and dashboards | Monitor lakehouse tables and inference logs at scale | Product naming, API surface, and supported monitor types evolve; verify the current workspace/runtime |

### 8.1 Evidently report example

The project below uses Evidently as an optional report generator. The current API can change; use the documentation corresponding to the installed version. A common recent pattern is:

```python
import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

reference = pd.read_parquet("data/reference.parquet")
current = pd.read_parquet("data/current_week.parquet")

report = Report(metrics=[DataDriftPreset()])
snapshot = report.run(current_data=current, reference_data=reference)
snapshot.save_html("data/evidently_drift_report.html")
```

Before running, check the installed version's report and preset imports. Do not treat the report's default drift decision as your organization's production policy without reviewing the method, thresholds, data typing, and quality status. The report should be an evidence artifact in a broader workflow.

### 8.2 Tool selection

- Use a **data validation tool** for schema and domain contracts.
- Use a **statistics layer** for versioned reference/current metrics.
- Use a **reporting tool** for human inspection and triage.
- Use an **alerting/on-call system** for routing and escalation.
- Use a **performance monitoring layer** for realized metrics and carefully labeled estimates.
- Use the orchestration/registry layer for retraining, evaluation, approval, and promotion.

A vendor product may cover several layers, but still define the interfaces and operational ownership.

---

## 9. Scalable monitoring with summaries and sketches

### 9.1 Why repeated raw scans are expensive

If a table contains billions of inference rows and dozens or hundreds of features, rescanning all historical raw data for every dashboard refresh is wasteful. Instead, compute compact summaries at ingestion or by window, retain raw data according to policy, and compute detailed analyses only when needed.

### 9.2 Per-window profile

For each `model_version × feature × time_window × segment`, retain relevant summaries:

- count, null count, invalid count;
- min, max, mean, standard deviation;
- quantiles or a quantile sketch;
- fixed-bin histograms for PSI/JS;
- category counts for selected categorical columns;
- prediction-score histogram and positive rate;
- source watermark, snapshot ID, schema version, and profile version.

Store drift metrics separately from profile metrics so you can recompute comparisons without rescanning all raw observations, provided the retained summaries preserve the information required by the metric.

### 9.3 Sketches and approximate algorithms

A **sketch** is a compact data structure that summarizes a large stream or dataset with bounded or characterized approximation error.

Examples:

- **Quantile sketches** approximate percentiles without storing every value.
- **HyperLogLog** estimates distinct counts; it is not a general-purpose distribution-drift detector.
- **Count-Min Sketch** estimates item frequencies and may help with high-cardinality categorical monitoring.
- Fixed-bin histograms support cheap comparison but cannot recover within-bin numeric detail.
- Reservoir or stratified sampling supports inspection of representative records, but samples must be designed for the question.

Approximation is a trade-off: less memory and compute in exchange for bounded or empirical error. Track sketch type, parameters, implementation version, and merge compatibility. Do not merge incompatible sketches or compare histograms with different bin definitions as though they were identical.

### 9.4 Scale architecture

```text
Inference logs / feature tables
       ↓ incremental windowing
Quality checks + compact profiles
       ↓
Profile metrics table
       ↓ reference/current comparison
Drift metrics table
       ↓ policy engine
Alert events + report links + runbook
       ↓
Triage / label-based performance evaluation / retraining decision
```

A drift metrics table might have one row per feature and window, with `metric_name`, `metric_value`, `p_value` when applicable, sample sizes, baseline ID, current window ID, quality status, segment, and monitor version. Partition by time and model if useful; avoid high-cardinality dimensions that make the table expensive or leak small-group information.

### 9.5 Accuracy and compute trade-offs

- Use exact calculations on manageable windows or when risk demands it.
- Use sketches for high-volume summaries and monitor approximation error.
- Sample for deeper diagnostics, but retain full-population quality counts where feasible.
- Keep a raw-data path for incident investigations subject to privacy and retention policy.
- Validate approximate metrics against exact results on representative windows before relying on them for alert thresholds.

---

## 10. Segment monitoring and multiple comparisons

### 10.1 Why aggregate metrics hide local failures

An overall feature distribution can look stable while one region, device, product, or customer cohort changes sharply. Segment-level monitoring helps identify these localized changes and can reveal fairness-related risk. But every extra slice creates more tests, sparse samples, and more alerts.

### 10.2 Segment design

Start with a small, justified set of segments:

- region or market;
- device/platform;
- acquisition channel;
- product tier;
- tenure cohort;
- model decision or risk band.

For each segment, define minimum sample size, privacy rules, and whether the metric is eligible for a page, ticket, or dashboard-only review. Avoid arbitrary combinatorial slicing across every available column.

### 10.3 Multiple-comparison controls

Use a combination of:

1. **Predeclared families:** define which features and segments are primary monitoring tests.
2. **False discovery rate:** apply a correction such as Benjamini–Hochberg when its assumptions and objective fit the monitoring problem.
3. **Persistence:** require a warning to repeat over multiple windows for low-risk changes.
4. **Effect-size floors:** require a meaningful PSI/JS/Wasserstein change, not only a low p-value.
5. **Minimum sample sizes:** do not interpret sparse cells as stable estimates.
6. **Hierarchical triage:** aggregate alerting at model/window level while keeping feature details in the report.
7. **Operational deduplication:** suppress repeated notifications for the same unresolved incident while retaining each measurement.

Do not over-correct so aggressively that severe local failures disappear. High-risk, predefined safety signals may warrant immediate alerting regardless of a general multiple-testing policy.

### 10.4 Fairness-related monitoring

Monitor outcome quality and error rates by legitimate, approved segments when labels and legal policy permit. A change in group composition is not the same as a change in model fairness. Assess data coverage, label quality, performance, calibration, and decision impact; document limitations and consult the appropriate governance owners. Do not infer sensitive attributes casually or expose small-cell data in dashboards.

---

## 11. Alerts, runbooks, and incident response

### 11.1 Severity levels

Define severity from data validity, potential impact, persistence, and service criticality—not only from a single statistic.

| Severity | Example trigger | Response |
|---|---|---|
| SEV-1 / page | Critical schema/quality failure affecting live decisions; severe validated performance degradation; monitoring blind spot for high-risk model | On-call response now; protect downstream decisions; incident channel |
| SEV-2 / urgent ticket or page by policy | Large, persistent drift in high-impact feature/segment; label-based metric breach | Investigate promptly; involve model and data owners |
| SEV-3 / ticket | Moderate shift or isolated low-risk segment warning | Review during business hours; trend and diagnose |
| INFO / dashboard | Expected seasonal change, low effect size, or exploratory metric | Record for trend analysis; no immediate action |

A quality failure may be more urgent than a drift alert because the system may be scoring corrupted data. Conversely, a statistically significant but tiny shift on a low-risk feature may need no page.

### 11.2 Example alert policy

The policy below is illustrative; calibrate it with historical data and business owners.

```text
IF required_schema_missing OR critical_quality_check_failed:
    severity = SEV-1
    action = stop_or_quarantine_affected_window
    owner = data_pipeline_on_call
ELIF measured_performance_below_slo AND label_maturity_is_sufficient:
    severity = SEV-1 or SEV-2 according to impact
    action = incident + evaluate rollback/fallback
    owner = model_on_call
ELIF drift_effect_exceeds_calibrated_limit
     AND minimum_sample_size_met
     AND signal_persists
     AND quality_gate_passed:
    severity = SEV-2 or SEV-3 according to risk
    action = investigate + compare segments + inspect lineage
ELSE:
    record metrics; do not page
```

A drift signal may create a retraining candidate, but must not automatically promote it. A quality failure should usually block a drift-triggered retraining decision until the input pipeline is trusted.

### 11.3 Alert record and deduplication

Store:

```text
alert_id, model_name, model_version, window_id, alert_policy_version,
severity, reason_codes, evidence_uri, first_seen_utc, last_seen_utc,
occurrence_count, owner, status, acknowledgement_utc, resolution_utc
```

Deduplicate by stable keys such as `(model, signal family, segment, window family)` while keeping repeated observations in the metrics table. Escalate if the condition worsens, persists beyond its SLA, or has no owner acknowledgement. Do not discard evidence just because a notification was suppressed.

### 11.4 Runbook template

For each alert, document:

1. **Meaning:** what exactly triggered the alert, with metric definition and baseline.
2. **Impact:** which model versions, segments, regions, and downstream decisions are affected.
3. **First checks:** quality gate, source freshness, schema changes, pipeline deploys, model-version changes.
4. **Containment:** quarantine bad data, pause publishing, switch to an approved fallback, or roll back if justified.
5. **Diagnosis:** compare reference/current profiles; inspect segment breakdown and lineage; verify label maturity.
6. **Decision:** repair pipeline, accept expected seasonal shift, monitor, schedule retraining, or rollback.
7. **Owner and escalation:** primary, secondary, and business-risk owner.
8. **Evidence:** metric rows, report URI, query/version, incident ID, and timeline.
9. **Recovery verification:** quality restored, data backfill complete, model/version confirmed.
10. **Post-incident action:** tests, baseline policy changes, alert tuning, and documented lessons.

### 11.5 Who owns what?

- Data platform/on-call: source freshness, schema, ingestion, quality contracts, data lineage.
- ML platform/on-call: model version, endpoint health, prediction logging, registry and deployment.
- Model owner: evaluation, label quality, performance interpretation, retraining decision.
- Business/risk owner: impact tolerance, acceptable trade-offs, fallback policy.
- Governance/privacy owner: permitted segments, retention, access, fairness and audit requirements.

Ownership must be explicit. A drift dashboard with no responsible team is not an operational control.

---

## 12. Retraining policies and safe promotion gates

### 12.1 Three retraining triggers

**Scheduled retraining** runs at a defined cadence. It is predictable and can incorporate newly matured labels, but may retrain when nothing meaningful changed or miss sudden failures between runs.

**Drift-triggered retraining** begins investigation or candidate training when input or prediction drift meets a policy. Drift alone does not prove new data are better training data, nor that retraining fixes the issue. A unit error or corrupted source must be repaired first.

**Performance-triggered retraining** is based on measured or carefully estimated model-quality degradation. It is more directly related to usefulness, but delayed labels mean it may react later. Distinguish measured outcomes from estimates.

A robust system can combine scheduled refresh with event-triggered investigations and performance-based urgency.

### 12.2 Safe workflow

```text
Monitoring signal
    ↓
Validate data quality and alert evidence
    ↓
Classify: pipeline incident / expected seasonality / population shift / unknown
    ↓
If justified, launch candidate training with versioned data and code
    ↓
Evaluate against current champion on a fixed, appropriate evaluation set
    ↓
Check aggregate + segment metrics, calibration, fairness, contracts, and operations
    ↓
Human/automated approval gate
    ↓
Shadow or canary rollout
    ↓
Promote only if gates pass; otherwise reject candidate
    ↓
Retain evidence and a tested rollback target
```

### 12.3 Champion-versus-challenger gate

The candidate should be evaluated on:

- the same well-defined evaluation cohort where comparison is appropriate;
- time-based or otherwise leakage-safe splits;
- predeclared primary and guardrail metrics;
- segment-level regression checks;
- calibration and threshold behavior;
- fairness/risk checks appropriate to the use case;
- input/output contract compatibility;
- reproducibility, artifact loading, latency/cost, and security checks;
- approval and lineage records.

A candidate that improves AUC but worsens a high-cost false-negative rate may be unacceptable. Use confidence intervals or statistical comparison where appropriate, and require minimum sample sizes. Do not select a model from a single noisy week. Use a validation/challenger evaluation set for repeated decisions; reserve a final holdout for infrequent, predeclared confirmation rather than repeatedly tuning or promoting against it.

### 12.4 Preventing uncontrolled retraining loops

A dangerous loop is:

```text
noisy drift alert → retrain → candidate changes score distribution
→ drift alert again → retrain again ...
```

Controls:

- separate `drift detected`, `candidate training requested`, `candidate passed`, and `candidate promoted` states;
- use idempotency keys and cooldown windows;
- require quality gates and sufficient label maturity;
- retain the baseline and monitor-policy version used for the decision;
- cap automatic retries and candidate frequency;
- require approval for high-risk models;
- never automatically promote based only on the drift metric that triggered training;
- keep rollback to a known-good version and verify runtime state after rollback.

### 12.5 Minimal policy implementation: `src/policy.py`

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WindowEvidence:
    quality_passed: bool
    sample_size: int
    psi: float
    ks_p_value: float
    persisted_windows: int
    measured_performance_breach: bool = False
    labels_mature: bool = False


def decide(e: WindowEvidence) -> tuple[str, str]:
    """Return (decision, reason); example thresholds are policy placeholders."""
    if not e.quality_passed:
        return "BLOCK_AND_PAGE_DATA_OWNER", "quality_gate_failed"
    if e.sample_size < 200:
        return "WATCH", "insufficient_sample"
    if e.measured_performance_breach and e.labels_mature:
        return "PERFORMANCE_INCIDENT", "measured_performance_breach"
    if e.psi >= 0.20 and e.ks_p_value < 0.01 and e.persisted_windows >= 2:
        return "INVESTIGATE_DRIFT", "persistent_effect_and_test_signal"
    return "RECORD_ONLY", "no_actionable_trigger"
```

The values `200`, `0.20`, `0.01`, and `2` are intentionally illustrative. Calibrate them with historical behavior, data volume, model risk, and expected business cost. The function does not train or promote a model; it produces an auditable triage decision.

### 12.6 Minimal challenger-versus-champion gate: `src/retraining_gate.py`

This gate deliberately stops at `APPROVED_FOR_SHADOW`. It does not switch production traffic. Guardrail regressions are supplied as non-negative, direction-normalized deltas (for example, an increase in false-negative rate is a regression); each must remain within its predeclared maximum. This keeps metric direction explicit and makes the decision testable.

```python
from __future__ import annotations

from dataclasses import dataclass, field
import math


@dataclass(frozen=True)
class CandidateEvidence:
    champion_version: str
    challenger_version: str
    quality_passed: bool
    sample_size: int
    minimum_sample_size: int
    champion_primary_metric: float
    challenger_primary_metric: float
    primary_metric_higher_is_better: bool
    minimum_improvement: float = 0.01
    guardrail_regressions: dict[str, float] = field(default_factory=dict)
    maximum_guardrail_regressions: dict[str, float] = field(default_factory=dict)
    fairness_passed: bool = False
    calibration_passed: bool = False
    artifact_load_passed: bool = False
    approval_recorded: bool = False


def evaluate_candidate(e: CandidateEvidence) -> tuple[str, str]:
    """Return a decision; this function never promotes or changes production traffic."""
    if not e.champion_version or not e.challenger_version or e.champion_version == e.challenger_version:
        return "REJECTED", "invalid_or_identical_model_versions"
    if not e.quality_passed:
        return "REJECTED", "training_or_evaluation_quality_gate_failed"
    if e.sample_size < e.minimum_sample_size or e.minimum_sample_size <= 0:
        return "REJECTED", "insufficient_evaluation_sample"
    if not all(math.isfinite(x) for x in (e.champion_primary_metric, e.challenger_primary_metric,
                                           e.minimum_improvement)):
        return "REJECTED", "non_finite_primary_metric_or_threshold"
    improvement = (e.challenger_primary_metric - e.champion_primary_metric
                   if e.primary_metric_higher_is_better
                   else e.champion_primary_metric - e.challenger_primary_metric)
    if improvement < e.minimum_improvement:
        return "REJECTED", "primary_metric_improvement_below_predeclared_minimum"
    if set(e.guardrail_regressions) != set(e.maximum_guardrail_regressions):
        return "REJECTED", "guardrail_evidence_or_threshold_missing"
    for name, regression in e.guardrail_regressions.items():
        limit = e.maximum_guardrail_regressions[name]
        if not math.isfinite(regression) or not math.isfinite(limit) or regression < 0 or limit < 0:
            return "REJECTED", f"invalid_guardrail_value:{name}"
        if regression > limit:
            return "REJECTED", f"guardrail_regression_exceeded:{name}"
    if not e.fairness_passed:
        return "REJECTED", "fairness_or_risk_gate_failed"
    if not e.calibration_passed:
        return "REJECTED", "calibration_gate_failed"
    if not e.artifact_load_passed:
        return "REJECTED", "artifact_load_or_contract_test_failed"
    if not e.approval_recorded:
        return "NEEDS_APPROVAL", "technical_gates_passed_approval_missing"
    return "APPROVED_FOR_SHADOW", "all_predeclared_gates_passed_shadow_only"
```

The metric thresholds are supplied by a versioned policy and must be calibrated to the use case. Statistical uncertainty, slice-level minimums, latency/cost checks, and model-risk requirements should be included in the evaluation evidence before calling this gate. A shadow run must not control the user-facing response; canary and promotion remain separate decisions.

### 12.7 Retraining workflow record

Persist each run's state:

```text
trigger_id
trigger_type: scheduled | drift | performance
evidence_window_ids
quality_gate_result
training_dataset_version
feature_definition_version
code_commit
environment_lock_hash
candidate_model_version
evaluation_report_uri
gate_results
approver
decision: rejected | approved_for_shadow | approved_for_canary | promoted
rollback_target
timestamps and run IDs
```

This is the bridge from monitoring to the registry and inference lifecycle in Topic 04.

---

## 13. End-to-end hands-on project: `experiments/05_drift/`

### 13.1 Scenario and planted changes

We simulate a weekly churn-like dataset with:

- `usage_ratio`: gradual numeric distribution shift;
- `monthly_charges`: a sudden unit change in week 5 (dollars become cents), which should fail a quality gate;
- `support_tickets_90d`: the relationship between this feature and the target changes in week 7, creating a concept-change scenario;
- `weekly_activity_index`: a four-week seasonal pattern that can create a false alarm if compared with a non-matching phase;
- labels that become available after a delay.

The synthetic target is not a realistic business model. It is a controlled fixture to test whether monitoring code detects the planted changes and separates quality failure from drift.

### 13.2 Deterministic generator: `src/generate_data.py`

```python
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261019
OUT = Path("data")
N_PER_WEEK = 1200


def generate_week(week: int, n: int = N_PER_WEEK) -> pd.DataFrame:
    rng = np.random.default_rng(SEED + week)
    week_start = pd.Timestamp("2026-08-03", tz="UTC") + pd.Timedelta(weeks=week)
    usage_mean = 0.85 + 0.045 * week  # gradual drift
    usage = rng.normal(usage_mean, 0.18, size=n).clip(0.0, 1.8)
    tenure = rng.integers(1, 73, size=n).astype(float)
    support = rng.poisson(1.2, size=n).astype(float)
    monthly_charges_dollars = rng.normal(72.0, 18.0, size=n).clip(15.0, 160.0)

    # Four-week seasonal pattern repeats at week 4, allowing a like-for-like
    # comparison (week 0 versus week 4) inside this eight-week fixture.
    season = np.sin(2 * np.pi * ((week % 4) / 4))
    monthly_charges_dollars = monthly_charges_dollars + 4.0 * season
    # Independent seasonal feature is not affected by the planted unit fault.
    weekly_activity_index = rng.normal(100.0 + 12.0 * season, 5.0, size=n).clip(0.0, 200.0)

    # Intentional unit/schema-semantic failure in week 5:
    # dollars are emitted as cents, but the column name stays unchanged.
    monthly_charges = monthly_charges_dollars * (100.0 if week >= 5 else 1.0)

    # Concept change in week 7: the true relationship between support and churn flips.
    # The deployed model score keeps the original relationship, so labels can
    # worsen relative to predictions even when input drift alone is inconclusive.
    deployed_support_effect = 0.42
    true_support_effect = 0.42 if week < 7 else -0.55

    def probability(effect: float) -> np.ndarray:
        logit = (
            -1.0
            - 0.025 * tenure
            + 0.012 * monthly_charges_dollars
            + effect * support
            - 0.75 * usage
        )
        return 1.0 / (1.0 + np.exp(-logit))

    deployed_probability = probability(deployed_support_effect)
    true_probability = probability(true_support_effect)
    label = rng.binomial(1, true_probability, size=n)

    prediction_timestamp = week_start + pd.to_timedelta(
        rng.integers(0, 7 * 24 * 60, size=n), unit="m"
    )
    # The outcome window ends 7 days after prediction. The label is only
    # published after an additional 0–14 days of source/processing delay.
    outcome_window_end = prediction_timestamp + pd.Timedelta(days=7)
    label_delay_days = rng.integers(7, 22, size=n)
    label_available = prediction_timestamp + pd.to_timedelta(label_delay_days, unit="D")

    df = pd.DataFrame({
        "prediction_id": [f"w{week:02d}-{i:06d}" for i in range(n)],
        "week": week,
        "prediction_timestamp_utc": prediction_timestamp,
        "outcome_window_end_utc": outcome_window_end,
        "label_available_timestamp_utc": label_available,
        "tenure_months": tenure,
        "usage_ratio": usage,
        "weekly_activity_index": weekly_activity_index,
        "support_tickets_90d": support,
        "monthly_charges": monthly_charges,
        "region": rng.choice(["north", "south", "east", "west"], size=n, p=[0.30, 0.25, 0.25, 0.20]),
        "prediction_score": np.clip(deployed_probability + rng.normal(0, 0.05, size=n), 0.001, 0.999),
        "label": label.astype(int),
        "source_schema_version": "v1",
    })
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frames = [generate_week(week) for week in range(8)]
    all_data = pd.concat(frames, ignore_index=True)
    all_data.to_parquet(OUT / "weekly_production.parquet", index=False)
    for week, frame in enumerate(frames):
        frame.to_parquet(OUT / f"week_{week:02d}.parquet", index=False)
    print(f"Wrote {len(all_data):,} synthetic rows to {OUT}/")


if __name__ == "__main__":
    main()
```

**Important design note:** the generator keeps the column name and schema version unchanged during the unit change to simulate a semantic contract failure; the numeric range contract catches it. The prediction score is calculated from the pre-corruption synthetic source value and the unit fault is then injected into the monitored `monthly_charges` field. This isolates quality-gate behavior; it is not a faithful simulation of a deployed model consuming malformed units. The independent `weekly_activity_index` is not affected by the unit fault. Its four-week period allows week 0 and week 4 to serve as matching seasonal phases. The seasonal component is intentionally simplistic; the lesson is about baseline design, not forecasting.

### 13.3 Quality checks and monitoring runner: `src/monitor.py`

```python
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.drift_metrics import categorical_drift, numeric_drift

DATA = Path("data")
MODEL_NAME = "churn-demo"
MODEL_VERSION = "synthetic-v1"
POLICY_VERSION = "drift-policy-v2"
REFERENCE_WEEK = 0
NUMERIC_FEATURES = [
    "usage_ratio",
    "support_tickets_90d",
    "monthly_charges",
    "tenure_months",
    "weekly_activity_index",
    "prediction_score",  # prediction-distribution monitoring, not performance
]
CATEGORICAL_FEATURES = ["region"]
EXPECTED_COLUMNS = {
    "prediction_id", "week", "prediction_timestamp_utc", "outcome_window_end_utc",
    "label_available_timestamp_utc", "tenure_months", "usage_ratio",
    "weekly_activity_index", "support_tickets_90d", "monthly_charges", "region",
    "prediction_score", "label", "source_schema_version",
}


def quality_checks(df: pd.DataFrame) -> list[dict]:
    findings: list[dict] = []
    missing_columns = sorted(EXPECTED_COLUMNS - set(df.columns))
    unexpected_columns = sorted(set(df.columns) - EXPECTED_COLUMNS)
    if missing_columns:
        findings.append({"check": "required_schema", "status": "FAIL",
                         "detail": f"missing columns: {missing_columns}"})
    if unexpected_columns:
        findings.append({"check": "unexpected_schema_columns", "status": "FAIL",
                         "detail": f"unexpected columns: {unexpected_columns}"})
    if missing_columns:
        # Do not index absent fields below; the caller records the failure and
        # blocks all comparisons for this window.
        return findings

    if len(df) == 0:
        findings.append({"check": "non_empty_window", "status": "FAIL", "detail": "zero rows"})
    if df["prediction_id"].isna().any() or df["prediction_id"].duplicated().any():
        findings.append({"check": "prediction_id_unique", "status": "FAIL",
                         "detail": "null or duplicate prediction IDs"})
    else:
        findings.append({"check": "prediction_id_unique", "status": "PASS", "detail": "unique IDs"})

    for column in NUMERIC_FEATURES + ["label"]:
        numeric = pd.to_numeric(df[column], errors="coerce")
        bad = int((numeric.isna() | ~np.isfinite(numeric.fillna(0).to_numpy(dtype=float))).sum())
        findings.append({"check": f"{column}_numeric_finite", "status": "FAIL" if bad else "PASS",
                         "detail": f"invalid_or_missing={bad}"})

    parsed_times = {}
    for column in ["prediction_timestamp_utc", "outcome_window_end_utc", "label_available_timestamp_utc"]:
        parsed = pd.to_datetime(df[column], errors="coerce", utc=True, format="mixed")
        parsed_times[column] = parsed
        bad = int(parsed.isna().sum())
        findings.append({"check": f"{column}_valid_utc", "status": "FAIL" if bad else "PASS",
                         "detail": f"unparseable_or_missing={bad}"})
    invalid_order = (
        (parsed_times["outcome_window_end_utc"] < parsed_times["prediction_timestamp_utc"])
        | (parsed_times["label_available_timestamp_utc"] < parsed_times["outcome_window_end_utc"])
    )
    invalid_order = invalid_order.fillna(False)
    bad_order = int(invalid_order.sum())
    findings.append({"check": "outcome_timestamp_order", "status": "FAIL" if bad_order else "PASS",
                     "detail": f"invalid_prediction_outcome_label_order={bad_order}"})

    ranges = {
        "usage_ratio": (0.0, 2.0),
        "support_tickets_90d": (0.0, 100.0),
        "monthly_charges": (0.0, 500.0),  # catches dollars-to-cents change
        "tenure_months": (0.0, 120.0),
        "weekly_activity_index": (0.0, 200.0),
        "prediction_score": (0.0, 1.0),
    }
    for column, (low, high) in ranges.items():
        numeric = pd.to_numeric(df[column], errors="coerce")
        bad = int(((numeric < low) | (numeric > high)).sum())
        findings.append({"check": f"{column}_range", "status": "FAIL" if bad else "PASS",
                         "detail": f"outside_[{low},{high}]={bad}"})

    labels = pd.to_numeric(df["label"], errors="coerce")
    bad_labels = int((~labels.isin([0, 1])).sum())
    findings.append({"check": "label_binary", "status": "FAIL" if bad_labels else "PASS",
                     "detail": f"non_binary_labels={bad_labels}"})
    if df["region"].isna().any() or not set(df["region"].dropna().astype(str)).issubset(
        {"north", "south", "east", "west"}
    ):
        findings.append({"check": "region_domain", "status": "FAIL",
                         "detail": "missing or unexpected region category"})
    else:
        findings.append({"check": "region_domain", "status": "PASS", "detail": "allowed categories"})
    schema_versions = set(df["source_schema_version"].dropna().astype(str))
    if schema_versions != {"v1"} or df["source_schema_version"].isna().any():
        findings.append({"check": "source_schema_version", "status": "FAIL",
                         "detail": f"expected only v1; observed={sorted(schema_versions)}"})
    else:
        findings.append({"check": "source_schema_version", "status": "PASS", "detail": "v1"})
    return findings


def _window_bounds(df: pd.DataFrame) -> tuple[str | None, str | None]:
    ts = pd.to_datetime(df.get("prediction_timestamp_utc", pd.Series(dtype="datetime64[ns, UTC]")),
                        errors="coerce", utc=True, format="mixed").dropna()
    if ts.empty:
        return None, None
    return ts.min().isoformat(), ts.max().isoformat()


def main() -> None:
    all_data = pd.read_parquet(DATA / "weekly_production.parquet")
    if "week" not in all_data.columns:
        raise ValueError("Input dataset lacks required partition key 'week'")
    if all_data["week"].isna().any() or not pd.to_numeric(all_data["week"], errors="coerce").dropna().mod(1).eq(0).all():
        raise ValueError("Input contains missing or non-integer week partition keys; quarantine before monitoring")
    reference = all_data.loc[all_data["week"] == REFERENCE_WEEK].copy()
    if reference.empty:
        raise ValueError(f"Reference week {REFERENCE_WEEK} is missing")
    generated_at = pd.Timestamp.now(tz="UTC").isoformat()
    baseline_findings = quality_checks(reference)
    baseline_passed = bool(baseline_findings) and all(x["status"] == "PASS" for x in baseline_findings)
    metric_rows: list[dict] = []
    quality_rows: list[dict] = []
    skipped_windows: list[int] = []

    for week_value in sorted(all_data["week"].dropna().unique()):
        week = int(week_value)
        current = all_data.loc[all_data["week"] == week_value].copy()
        findings = quality_checks(current)
        quality_passed = bool(findings) and all(f["status"] == "PASS" for f in findings)
        for finding in findings:
            quality_rows.append({"window_id": f"week-{week:02d}", "week": week,
                                 "model_name": MODEL_NAME, "model_version": MODEL_VERSION,
                                 "policy_version": POLICY_VERSION, "monitor_run_timestamp_utc": generated_at,
                                 "quality_passed": quality_passed, **finding})

        start, end = _window_bounds(current)
        common = {
            "window_id": f"week-{week:02d}", "week": week,
            "window_start_utc": start, "window_end_utc": end,
            "reference_id": f"week-{REFERENCE_WEEK:02d}-v1",
            "reference_week": REFERENCE_WEEK, "model_name": MODEL_NAME,
            "model_version": MODEL_VERSION, "policy_version": POLICY_VERSION,
            "monitor_run_timestamp_utc": generated_at,
            "quality_passed": quality_passed,
        }
        if week == REFERENCE_WEEK:
            baseline_status = "BASELINE" if baseline_passed else "BASELINE_INVALID"
            for feature in NUMERIC_FEATURES + CATEGORICAL_FEATURES:
                metric_rows.append({**common, "feature": feature, "metric_status": baseline_status,
                                    "feature_quality_passed": quality_passed,
                                    "note": "Reference window; not compared with itself" if baseline_passed
                                    else "Reference window failed quality validation; all comparisons are blocked"})
            continue

        schema_failed = any(f["check"] == "required_schema" and f["status"] == "FAIL" for f in findings)
        if not baseline_passed or schema_failed:
            skipped_windows.append(week)
            for feature in NUMERIC_FEATURES + CATEGORICAL_FEATURES:
                metric_rows.append({**common, "feature": feature,
                                    "metric_status": "BLOCKED_BASELINE_OR_SCHEMA_FAILURE",
                                    "feature_quality_passed": False})
            continue

        # Global quality failure blocks automated drift actions. Per-feature
        # validity remains visible so valid features can be inspected diagnostically.
        failed_checks = {f["check"] for f in findings if f["status"] == "FAIL"}
        for feature in NUMERIC_FEATURES:
            feature_bad = (f"{feature}_numeric_finite" in failed_checks or f"{feature}_range" in failed_checks)
            row = {**common, "feature": feature,
                   "metric_status": "DIAGNOSTIC_ONLY_QUALITY_FAILED" if not quality_passed else "COMPUTED",
                   "feature_quality_passed": not feature_bad}
            try:
                row.update(numeric_drift(reference[feature], current[feature]))
            except ValueError as exc:
                row["metric_error"] = str(exc)
                row["metric_status"] = "NOT_COMPUTABLE"
            metric_rows.append(row)

        for feature in CATEGORICAL_FEATURES:
            feature_bad = ("region_domain" in failed_checks)
            row = {**common, "feature": feature,
                   "metric_status": "DIAGNOSTIC_ONLY_QUALITY_FAILED" if not quality_passed else "COMPUTED",
                   "feature_quality_passed": not feature_bad}
            row.update(categorical_drift(reference[feature], current[feature]))
            metric_rows.append(row)

    DATA.mkdir(exist_ok=True)
    pd.DataFrame(metric_rows).to_parquet(DATA / "drift_metrics.parquet", index=False)
    pd.DataFrame(quality_rows).to_parquet(DATA / "quality_metrics.parquet", index=False)
    (DATA / "monitor_run.json").write_text(json.dumps({
        "reference_week": REFERENCE_WEEK, "reference_id": f"week-{REFERENCE_WEEK:02d}-v1",
        "model_name": MODEL_NAME, "model_version": MODEL_VERSION,
        "policy_version": POLICY_VERSION, "monitor_run_timestamp_utc": generated_at,
        "weeks_processed": sorted(int(x) for x in all_data["week"].dropna().unique()),
        "skipped_windows": skipped_windows,
        "baseline_quality_passed": baseline_passed,
        "metric_rows": len(metric_rows), "quality_rows": len(quality_rows),
        "note": "Synthetic data; inspect stored values. Drift metrics from any quality-failed window are diagnostic only.",
    }, indent=2), encoding="utf-8")
    print(f"Wrote {len(metric_rows)} drift metric rows and {len(quality_rows)} quality rows; skipped windows={skipped_windows}.")


if __name__ == "__main__":
    main()
```

The runner marks the reference week as `BASELINE` rather than comparing it to itself. Each row records stable window/baseline IDs, window bounds, model and policy versions, and monitor-run time. Any global quality failure blocks automated drift action; metrics are retained only as diagnostic evidence, with feature-level validity exposed separately. A missing required schema or invalid baseline blocks comparison rather than crashing or producing misleading metrics.

### 13.4 Delayed-label joining and performance: `src/delayed_labels.py`

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, brier_score_loss, roc_auc_score

DATA = Path("data")


def evaluate_as_of(
    as_of_utc: str,
    predictions: pd.DataFrame | None = None,
    outcomes: pd.DataFrame | None = None,
    output_path: Path | None = DATA / "performance_metrics.parquet",
) -> pd.DataFrame:
    """Evaluate only outcomes mature and available at the supplied UTC cutoff.

    Optional frames make the time semantics testable without Parquet services.
    In the synthetic lab, outcomes are derived from the generator output, but
    the prediction view explicitly excludes labels and outcome timestamps.
    Production systems should read predictions and outcomes from separate logs.
    """
    if predictions is None or outcomes is None:
        raw = pd.read_parquet(DATA / "weekly_production.parquet")
        if predictions is None:
            predictions = raw.drop(columns=["label", "label_available_timestamp_utc", "outcome_window_end_utc"]).copy()
        if outcomes is None:
            outcomes = raw[[
                "prediction_id", "label", "outcome_window_end_utc", "label_available_timestamp_utc"
            ]].rename(columns={"label": "ground_truth"}).copy()

    required_predictions = {"prediction_id", "prediction_timestamp_utc", "week", "prediction_score"}
    required_outcomes = {"prediction_id", "ground_truth", "outcome_window_end_utc", "label_available_timestamp_utc"}
    if missing := sorted(required_predictions - set(predictions.columns)):
        raise ValueError(f"Prediction log missing columns: {missing}")
    if missing := sorted(required_outcomes - set(outcomes.columns)):
        raise ValueError(f"Outcome table missing columns: {missing}")
    if predictions["prediction_id"].isna().any() or predictions["prediction_id"].duplicated().any():
        raise ValueError("prediction_id must be non-null and unique in prediction log")
    if outcomes["prediction_id"].isna().any() or outcomes["prediction_id"].duplicated().any():
        raise ValueError("prediction_id must be non-null and unique in outcome table")

    as_of = pd.to_datetime(as_of_utc, utc=True)
    pred = predictions.copy()
    out = outcomes.copy()
    pred["prediction_timestamp_utc"] = pd.to_datetime(pred["prediction_timestamp_utc"], errors="coerce", utc=True)
    out["outcome_window_end_utc"] = pd.to_datetime(out["outcome_window_end_utc"], errors="coerce", utc=True)
    out["label_available_timestamp_utc"] = pd.to_datetime(out["label_available_timestamp_utc"], errors="coerce", utc=True)

    # Do not count predictions made after the as-of cutoff in the coverage denominator.
    eligible = pred.loc[pred["prediction_timestamp_utc"].notna() &
                        (pred["prediction_timestamp_utc"] <= as_of)].copy()
    joined = eligible.merge(out, on="prediction_id", how="left", validate="one_to_one")
    rows: list[dict] = []
    for week, group in joined.groupby("week", dropna=False):
        mature_mask = (
            group["ground_truth"].notna()
            & group["outcome_window_end_utc"].notna()
            & (group["outcome_window_end_utc"] <= as_of)
            & group["label_available_timestamp_utc"].notna()
            & (group["label_available_timestamp_utc"] <= as_of)
        )
        mature = group.loc[mature_mask].copy()
        mature_label_count = len(mature)
        coverage = float(mature_label_count / len(group)) if len(group) else 0.0
        base = {
            "week": int(week), "as_of_utc": as_of.isoformat(),
            "eligible_predictions": int(len(group)), "mature_labels": int(mature_label_count),
            "label_coverage_in_eligible_cohort": coverage,
        }
        if mature.empty:
            rows.append({**base, "metric_sample_size": 0, "accuracy_at_0_5": None,
                         "brier_score": None, "auc": None,
                         "metric_kind": "NOT_COMPUTABLE_NO_MATURE_LABELS"})
            continue
        y = pd.to_numeric(mature["ground_truth"], errors="coerce")
        valid = y.isin([0, 1]) & pd.to_numeric(mature["prediction_score"], errors="coerce").between(0, 1)
        mature = mature.loc[valid].copy()
        y = pd.to_numeric(mature["ground_truth"], errors="coerce").astype(int)
        score = pd.to_numeric(mature["prediction_score"], errors="coerce").astype(float)
        if mature.empty:
            rows.append({**base, "metric_sample_size": 0, "accuracy_at_0_5": None,
                         "brier_score": None, "auc": None,
                         "metric_kind": "NOT_COMPUTABLE_INVALID_LABEL_OR_SCORE"})
            continue
        rows.append({
            **base,
            "metric_sample_size": int(len(mature)),
            "accuracy_at_0_5": float(accuracy_score(y, score >= 0.5)),
            "brier_score": float(brier_score_loss(y, score)),
            "auc": float(roc_auc_score(y, score)) if y.nunique() == 2 else None,
            "metric_kind": "MEASURED_ON_MATURE_SYNTHETIC_LABELS",
        })
    result = pd.DataFrame(rows)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.to_parquet(output_path, index=False)
    return result


if __name__ == "__main__":
    print(evaluate_as_of("2026-10-19T00:00:00Z").to_string(index=False))
```

**Important:** the score uses a fixed deployed relationship while the true label-generating relationship changes in week 7. This creates a controlled mismatch for the lab, not a realistic independent business evaluation. In production, join actual outcome events to a prediction-time log that contains no future labels. The `as_of` cutoff requires both the outcome window and label-availability timestamp to have passed; label maturity and coverage are calculated against predictions observed by that cutoff, by cohort.

### 13.5 Tests: `tests/test_drift_metrics.py`

```python
import numpy as np
import pandas as pd
import pytest

from src.drift_metrics import categorical_drift, numeric_drift, psi_numeric


def test_identical_numeric_samples_have_near_zero_psi():
    rng = np.random.default_rng(12)
    sample = pd.Series(rng.normal(size=1000))
    assert psi_numeric(sample, sample) < 1e-9


def test_shifted_numeric_sample_has_positive_effect_metrics():
    rng = np.random.default_rng(13)
    reference = pd.Series(rng.normal(0, 1, size=2000))
    current = pd.Series(rng.normal(1.5, 1, size=2000))
    assert psi_numeric(reference, current) > 0.1
    result = numeric_drift(reference, current)
    assert result["ks_statistic"] > 0
    assert result["wasserstein_1"] > 0
    assert 0 <= result["js_distance"] <= 1


def test_invalid_numeric_values_are_counted_not_silently_lost():
    result = numeric_drift(pd.Series([1, 2, np.nan, np.inf]), pd.Series([1, 2, 3, None]))
    assert result["n_reference_raw"] == 4
    assert result["n_reference_invalid_or_missing"] == 2
    assert result["n_current_invalid_or_missing"] == 1


def test_identical_categories_have_no_chi_square_evidence():
    reference = pd.Series(["a", "b", "c"] * 100)
    current = pd.Series(["a", "b", "c"] * 100)
    result = categorical_drift(reference, current)
    assert result["chi2_statistic"] == 0
    assert result["chi2_p_value"] == 1


def test_one_category_is_reported_as_degenerate_not_as_drift():
    result = categorical_drift(pd.Series(["a"] * 10), pd.Series(["a"] * 12))
    assert result["chi2_p_value"] == 1
    assert "Only one category" in result["warning"]


def test_psi_rejects_invalid_bin_count():
    with pytest.raises(ValueError):
        from src.drift_metrics import fixed_reference_edges
        fixed_reference_edges(pd.Series([1, 2, 3]), bins=1)
```

### 13.6 Quality-gate tests: `tests/test_quality_gate.py`

```python
import pandas as pd

from src.monitor import quality_checks
from src.generate_data import generate_week
from src.retraining_gate import CandidateEvidence, evaluate_candidate


def test_challenger_gate_requires_approval_and_never_promotes_directly():
    evidence = CandidateEvidence(
        champion_version="17", challenger_version="18", quality_passed=True,
        sample_size=5000, minimum_sample_size=1000,
        champion_primary_metric=0.70, challenger_primary_metric=0.73,
        primary_metric_higher_is_better=True, minimum_improvement=0.01,
        guardrail_regressions={"false_negative_rate": 0.01},
        maximum_guardrail_regressions={"false_negative_rate": 0.02},
        fairness_passed=True, calibration_passed=True, artifact_load_passed=True,
        approval_recorded=False,
    )
    assert evaluate_candidate(evidence) == ("NEEDS_APPROVAL", "technical_gates_passed_approval_missing")
    approved = CandidateEvidence(**{**evidence.__dict__, "approval_recorded": True})
    assert evaluate_candidate(approved)[0] == "APPROVED_FOR_SHADOW"


def test_challenger_gate_rejects_guardrail_regression():
    evidence = CandidateEvidence(
        champion_version="17", challenger_version="18", quality_passed=True,
        sample_size=5000, minimum_sample_size=1000,
        champion_primary_metric=0.70, challenger_primary_metric=0.73,
        primary_metric_higher_is_better=True, minimum_improvement=0.01,
        guardrail_regressions={"false_negative_rate": 0.05},
        maximum_guardrail_regressions={"false_negative_rate": 0.02},
        fairness_passed=True, calibration_passed=True, artifact_load_passed=True,
        approval_recorded=True,
    )
    assert evaluate_candidate(evidence) == ("REJECTED", "guardrail_regression_exceeded:false_negative_rate")


def test_unit_change_fails_monthly_charges_range():
    findings = quality_checks(generate_week(week=5, n=100))
    range_check = next(x for x in findings if x["check"] == "monthly_charges_range")
    assert range_check["status"] == "FAIL"


def test_reference_week_passes_quality_contract():
    findings = quality_checks(generate_week(week=0, n=100))
    assert findings
    assert all(x["status"] == "PASS" for x in findings)


def test_missing_required_column_is_reported_without_indexing_error():
    frame = generate_week(week=0, n=20).drop(columns=["weekly_activity_index"])
    findings = quality_checks(frame)
    schema = next(x for x in findings if x["check"] == "required_schema")
    assert schema["status"] == "FAIL"


def test_invalid_timestamp_label_and_category_are_rejected():
    frame = generate_week(week=0, n=20)
    frame["prediction_timestamp_utc"] = frame["prediction_timestamp_utc"].astype(str)
    frame.loc[0, "prediction_timestamp_utc"] = "not-a-time"
    frame.loc[1, "label"] = 2
    frame.loc[2, "region"] = "UNKNOWN"
    frame.loc[3, "label_available_timestamp_utc"] = pd.Timestamp("2026-01-01T00:00:00Z")
    findings = quality_checks(frame)
    statuses = {x["check"]: x["status"] for x in findings}
    assert statuses["prediction_timestamp_utc_valid_utc"] == "FAIL"
    assert statuses["label_binary"] == "FAIL"
    assert statuses["region_domain"] == "FAIL"
    assert statuses["outcome_timestamp_order"] == "FAIL"


def test_independent_seasonal_feature_repeats_at_week_four():
    from src.drift_metrics import numeric_drift
    week0 = generate_week(week=0, n=1200)
    week1 = generate_week(week=1, n=1200)
    week4 = generate_week(week=4, n=1200)
    # Same phase at week 4 should look much closer to week 0 than week 1 does.
    mismatched = numeric_drift(week0["weekly_activity_index"], week1["weekly_activity_index"])
    matched = numeric_drift(week0["weekly_activity_index"], week4["weekly_activity_index"])
    assert mismatched["psi"] > matched["psi"]
    assert matched["psi"] < 0.1


def test_concept_change_is_visible_only_when_mature_labels_are_evaluated():
    from src.delayed_labels import evaluate_as_of
    from src.generate_data import generate_week
    frames = [generate_week(week=week, n=1200) for week in (0, 7)]
    raw = pd.concat(frames, ignore_index=True)
    predictions = raw.drop(columns=["label", "label_available_timestamp_utc", "outcome_window_end_utc"])
    outcomes = raw[["prediction_id", "label", "outcome_window_end_utc", "label_available_timestamp_utc"]].rename(
        columns={"label": "ground_truth"}
    )
    metrics = evaluate_as_of("2026-10-19T00:00:00Z", predictions, outcomes, output_path=None)
    auc0 = metrics.loc[metrics["week"] == 0, "auc"].iloc[0]
    auc7 = metrics.loc[metrics["week"] == 7, "auc"].iloc[0]
    assert auc0 is not None and auc7 is not None
    assert auc7 < auc0 - 0.08


def test_prediction_score_is_in_the_numeric_monitor_feature_list():
    from src.monitor import NUMERIC_FEATURES
    assert "prediction_score" in NUMERIC_FEATURES


def test_monitor_runner_marks_baseline_and_blocks_unit_fault_actions(monkeypatch, tmp_path):
    from pathlib import Path
    from src import monitor
    from src.generate_data import generate_week

    all_data = pd.concat([generate_week(week, n=100) for week in range(8)], ignore_index=True)
    written = {}
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(pd, "read_parquet", lambda *args, **kwargs: all_data.copy())
    monkeypatch.setattr(
        pd.DataFrame, "to_parquet",
        lambda self, path, index=False: written.__setitem__(Path(path).name, self.copy()),
    )
    monitor.main()
    metrics = written["drift_metrics.parquet"]
    baseline = metrics.loc[metrics["week"] == 0]
    assert set(baseline["metric_status"]) == {"BASELINE"}
    bad_charge = metrics.loc[(metrics["week"] == 5) & (metrics["feature"] == "monthly_charges")].iloc[0]
    assert bad_charge["metric_status"] == "DIAGNOSTIC_ONLY_QUALITY_FAILED"
    assert not bool(bad_charge["feature_quality_passed"])
    assert "prediction_score" in set(metrics["feature"])


def test_monitor_runner_blocks_all_comparisons_when_reference_schema_is_invalid(monkeypatch, tmp_path):
    from pathlib import Path
    from src import monitor
    from src.generate_data import generate_week

    all_data = pd.concat([generate_week(week, n=40) for week in range(3)], ignore_index=True)
    all_data = all_data.drop(columns=["weekly_activity_index"])
    written = {}
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(pd, "read_parquet", lambda *args, **kwargs: all_data.copy())
    monkeypatch.setattr(
        pd.DataFrame, "to_parquet",
        lambda self, path, index=False: written.__setitem__(Path(path).name, self.copy()),
    )
    monitor.main()
    metrics = written["drift_metrics.parquet"]
    assert set(metrics.loc[metrics["week"] == 0, "metric_status"]) == {"BASELINE_INVALID"}
    assert set(metrics.loc[metrics["week"] == 1, "metric_status"]) == {"BLOCKED_BASELINE_OR_SCHEMA_FAILURE"}


def test_delayed_label_join_handles_maturity_and_eligible_denominator():
    from src.delayed_labels import evaluate_as_of
    predictions = pd.DataFrame({
        "prediction_id": ["a", "b", "future"],
        "prediction_timestamp_utc": pd.to_datetime([
            "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", "2026-02-01T00:00:00Z"
        ], utc=True),
        "week": [0, 0, 1], "prediction_score": [0.2, 0.8, 0.4],
    })
    outcomes = pd.DataFrame({
        "prediction_id": ["a", "b", "future"], "ground_truth": [0, 1, 1],
        "outcome_window_end_utc": pd.to_datetime([
            "2026-01-08T00:00:00Z", "2026-01-09T00:00:00Z", "2026-02-08T00:00:00Z"
        ], utc=True),
        "label_available_timestamp_utc": pd.to_datetime([
            "2026-01-10T00:00:00Z", "2026-02-10T00:00:00Z", "2026-02-10T00:00:00Z"
        ], utc=True),
    })
    result = evaluate_as_of("2026-01-15T00:00:00Z", predictions, outcomes, output_path=None)
    row = result.loc[result["week"] == 0].iloc[0]
    assert row["eligible_predictions"] == 2
    assert row["mature_labels"] == 1
    assert row["label_coverage_in_eligible_cohort"] == 0.5
    assert row["metric_kind"] == "MEASURED_ON_MATURE_SYNTHETIC_LABELS"
```

Run from the project root:

```bash
python -m src.generate_data
python -m src.monitor
python -m src.delayed_labels
pytest -q
```

These are commands to execute locally; no execution results are claimed by this lesson. If a command fails, inspect dependency versions and file paths, then retain the actual output as project evidence.

### 13.7 Evidently report script

Create `src/evidently_report.py`:

```python
from pathlib import Path

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

data = Path("data")
reference = pd.read_parquet(data / "week_00.parquet")
current = pd.read_parquet(data / "week_04.parquet")
quality = pd.read_parquet(data / "quality_metrics.parquet")
week_quality = quality.loc[quality["week"] == 4]
if week_quality.empty or not bool(week_quality["quality_passed"].all()):
    raise RuntimeError("Refusing to create an actionable drift report: week 4 quality gate did not pass")

# Current Evidently API: Report.run returns a Snapshot; save HTML on that result.
report = Report(metrics=[DataDriftPreset()])
snapshot = report.run(current_data=current, reference_data=reference)
snapshot.save_html(str(data / "evidently_drift_report.html"))
print(f"Saved {data / 'evidently_drift_report.html'} after quality validation.")
```

Run only after installing and validating the API for your pinned Evidently version. This script does not override the quality gate: the week with a unit change should be classified as a quality incident even if the report also displays distribution differences.

### 13.8 Example monitoring records: shape, not fabricated values

The generated metrics are data-dependent. The following is a **schema example only**; its numbers are placeholders and must not be mistaken for actual output:

```json
{
  "model_name": "churn-demo",
  "model_version": "synthetic",
  "feature": "usage_ratio",
  "reference_week": 0,
  "current_week": 3,
  "metric_name": "psi",
  "metric_value": "<computed value>",
  "sample_size_reference": 1200,
  "sample_size_current": 1200,
  "quality_status": "PASS",
  "metric_status": "COMPUTED",
  "policy_version": "example-v1"
}
```

For week 5 and later, `monthly_charges` should fail the example's allowed range check because values are in cents while the contract expects dollars. The drift metrics are retained as `DIAGNOSTIC_ONLY_QUALITY_FAILED`; they must not be used as evidence of genuine population drift until the unit issue is resolved.

The gradual `usage_ratio` change should produce an increasingly different distribution as the generator's mean shifts. `prediction_score` is monitored as an output-distribution signal, but it is not a realized performance metric. The concept-change scenario affects the relationship between support tickets and labels; it may not be detected by input-only drift statistics. The correct demonstration is a lagging change in measured performance on mature labels, not a claim that KS alone detected concept drift.

### 13.9 Seasonality false-alarm exercise

1. Compare `weekly_activity_index` in week 0 against week 1 (different seasonal phase) and record the metric/initial alert.
2. Compare week 0 against week 4, which has the same four-week seasonal phase; use the same frozen reference-derived bins.
3. Compare the two results and explain why the matched-phase baseline reduces the expected seasonal false alarm.
4. Separately inspect `monthly_charges`: weeks 5–7 contain the planted unit fault and must fail the quality gate, so do not use their drift values as a natural seasonal signal.
5. Document whether the apparent drift remains after seasonal matching. Do not automatically suppress a signal if quality or mature-label performance evidence indicates risk.

### 13.10 Actionable alert and retraining workflow exercise

Implement the following states in an orchestration DAG or local script:

```text
WINDOW_RECEIVED
  → QUALITY_VALIDATED
      ├─ failed → QUARANTINED + DATA_OWNER_ALERT
      └─ passed → DRIFT_COMPUTED
                    → POLICY_EVALUATED
                        ├─ no trigger → RECORDED
                        └─ trigger → INVESTIGATION
                                      → CANDIDATE_TRAINED
                                      → CHALLENGER_EVALUATED
                                          ├─ failed → REJECTED
                                          └─ passed → APPROVAL
                                                        → SHADOW/CANARY
                                                        → PROMOTED or ROLLED_BACK
```

For each transition, persist input window IDs, run ID, monitor policy version, data-quality result, candidate model version, evaluation report, decision owner, and timestamps. A retraining request should be idempotent: repeated alerts for the same unresolved condition must not create an uncontrolled training storm.

### 13.11 What to prove in the project

- [ ] The gradual feature shift is visible in stored per-week metrics.
- [ ] The unit change is caught by a quality contract before drift metrics drive action.
- [ ] The concept-change scenario is not falsely claimed to be detectable from \(P(X)\) alone.
- [ ] Labels are joined to predictions and only mature outcomes enter realized performance metrics.
- [ ] Label coverage and delay are visible.
- [ ] A seasonal comparison creates a false alarm under one baseline and is improved by a more appropriate baseline.
- [ ] A quality failure blocks drift-based retraining decisions.
- [ ] Candidate training does not equal model promotion.
- [ ] The champion remains unchanged if a challenger fails any required gate.
- [ ] Actual report and test outputs are saved as evidence after local execution.

---

## 14. Troubleshooting and common mistakes

| Symptom | Likely cause | Corrective action |
|---|---|---|
| Every feature alerts at once | Upstream pipeline change, unit/schema issue, baseline mismatch | Run quality gates and inspect source/transform deploy history first |
| p-values are tiny for harmless changes | Large sample size and repeated testing | Use effect sizes, calibrated thresholds, and multiple-testing policy |
| No alerts despite obvious change | Wrong feature typing, recomputed bins, too-small sample, stale monitor | Validate the metric implementation and baseline/version metadata |
| PSI changes unpredictably | Bins changed between windows, sparse bins, zero-count handling | Freeze reference bin edges and record smoothing/version |
| KS p-value changes from run to run | Sampling variation, sample size, dependence, or changing windows | Fix window definitions, report sample sizes, and account for repeated testing |
| Chi-square warnings | Sparse expected cell counts or rare categories | Group meaningful rare categories or use an appropriate exact/Monte Carlo method |
| Drift alert caused by dollars/cents | Semantic contract does not specify units | Add unit metadata and range/semantic checks; quarantine bad window |
| Feature drift but performance stable | Shift is benign or model is robust in the affected region | Validate with outcomes and business impact; do not retrain automatically |
| Performance degrades but input drift is small | Concept drift, label/data issue, threshold/config change | Inspect mature labels, calibration, policy, and outcome pipeline |
| Performance appears to improve suddenly | Label coverage changed or hard cases are delayed/missing | Audit label maturity and missingness by cohort/class |
| Alert floods on segments | Too many slices/tests and no deduplication | Predefine segment families, minimum sample sizes, FDR/persistence, hierarchical alerting |
| Repeated retraining starts continuously | No cooldown, idempotency, or separate promotion state | Add trigger deduplication, bounded retries, and explicit gates |
| New model is promoted after a metric improvement | No guardrails or champion comparison | Add baseline, slice, calibration, quality, and operational gates |
| Evidently report fails | API changed or wrong installed version | Pin and verify version-specific imports/API; isolate optional report dependency |
| Monitoring table grows without bound | Unbounded dimensions or retention | Partition by time, cap segment cardinality, aggregate, and apply retention |
| Fairness dashboard exposes tiny cohorts | Small-cell privacy risk | Suppress or aggregate low-count cells and enforce access controls |

### Common anti-patterns

1. Alerting on every feature at `p < 0.05`.
2. Treating a pipeline bug as natural drift.
3. Using a single old training snapshot as the only baseline forever.
4. Refreshing the baseline from a known-bad period.
5. Claiming model performance fell because feature distributions changed.
6. Treating proxy or estimated performance as measured ground truth.
7. Joining delayed labels to the wrong prediction or using immature labels.
8. Monitoring only aggregate data and missing a localized failure.
9. Triggering retraining without quality checks or a challenger gate.
10. Failing to preserve the monitoring policy, baseline, and evidence used for a decision.

---

## 15. Practice questions and exercises

### 15.1 Concept checks

1. Define data drift and concept drift. Why can one occur without the other?
2. What is label drift, and what data do you need to observe it?
3. Give three pipeline failures that can imitate natural drift.
4. Why is a significant KS p-value not sufficient evidence to page an on-call engineer?
5. What does PSI depend on besides the underlying distributions?
6. Why must reference bin edges remain fixed across comparisons?
7. When is chi-square a poor choice for categorical data?
8. What is the difference between Jensen–Shannon divergence and JS distance?
9. Why does Wasserstein distance have feature units?
10. Why should data-quality checks precede drift calculations?
11. What is a delayed label, and how can immature labels bias measured performance?
12. Explain a proxy metric versus an estimated metric versus measured performance.
13. How can a feedback loop bias the labels collected from production?
14. Why do many segment tests create alert floods?
15. What evidence should be stored with a retraining decision?
16. Why should a drift alert not automatically promote a newly trained model?

### 15.2 Churn-model exercise: five things that could drift

For a churn model, list five variables or relationships and specify the observable signal and likely response. Example categories:

- `tenure_months`: new acquisition channel changes the customer mix; inspect channel slices and performance.
- `usage_ratio`: product instrumentation changed; check event coverage and feature freshness before interpreting drift.
- `support_tickets_90d`: support system migration causes duplicates; inspect uniqueness and source lineage.
- `prediction_score`: model version or threshold changed; verify deployment configuration.
- `P(churn | X)`: pricing policy changes; requires mature churn outcomes to confirm relationship/performance changes.

For each signal, decide whether it should page, create a ticket, or only appear on a dashboard. Justify the decision from business impact and quality status.

### 15.3 Architecture exercises

**Exercise A — Monitoring design.** Choose the reference window, current window, metrics, minimum sample sizes, and baseline refresh policy for a daily churn model. Explain how seasonality changes your design.

**Exercise B — False alarm analysis.** Use the weekly generator to compare a seasonal feature against a non-matching period. Improve the baseline and show whether the alert policy changes.

**Exercise C — Delayed labels.** Design a 30-day churn label pipeline. Define prediction ID, outcome window, label maturity, corrections, and performance calculation cutoff.

**Exercise D — Alert routing.** Write severity rules for a schema break, a large persistent feature shift, a small p-value with negligible effect size, and a measured recall breach.

**Exercise E — Safe retraining.** Define a challenger gate, rollback target, and cooldown/idempotency strategy. Explain how you prevent a drift alert from starting repeated training runs.

### 15.4 Advanced extensions

1. Add Benjamini–Hochberg false-discovery-rate adjustment across the predefined feature family.
2. Add a minimum effect-size threshold and persistence policy to `src/policy.py`.
3. Compare exact histogram metrics with a quantile sketch or sampled approximation on a large synthetic dataset.
4. Store reference bin edges and a baseline version in a versioned monitoring table.
5. Add per-region metrics and suppress alerts below a minimum segment count.
6. Add label coverage and label-delay quantiles by class and cohort.
7. Compare estimated performance from a tool such as NannyML with realized metrics once labels mature.
8. Add an alert-deduplication table and a simple incident state machine.
9. Write a model-risk note describing the consequences of false negatives, false positives, and delayed detection.
10. Extend monitoring awareness to LLM applications: input distribution, output quality, groundedness, toxicity, latency, token usage, and cost.

---

## 16. Completion checklist matching Topic 05

### Drift concepts and signals

- [ ] Distinguish data drift, concept drift, label drift, pipeline failure, seasonality, and feedback loops.
- [ ] Explain which signals are observable without labels.
- [ ] Monitor input quality, schema, ranges, nulls, feature distributions, prediction distributions, and business outcomes.
- [ ] Define reference/current windows, rolling baselines, and baseline refresh governance.

### Statistics

- [ ] Calculate and interpret PSI using fixed reference bins.
- [ ] Calculate and interpret KS statistic and p-value for numeric samples.
- [ ] Use chi-square for categorical counts and inspect expected cell counts.
- [ ] Explain Jensen–Shannon divergence versus distance.
- [ ] Calculate Wasserstein-1 distance and interpret its feature units.
- [ ] Explain sample-size effects, thresholds, false alarms, repeated tests, and effect size.
- [ ] Avoid treating one p-value or arbitrary threshold as a complete operational decision.

### Quality and delayed labels

- [ ] Validate schema, missingness, ranges, units, freshness, and coverage before interpreting drift.
- [ ] Separate invalid data from genuine population changes.
- [ ] Join labels to predictions with correct IDs and time semantics.
- [ ] Track label maturity and coverage.
- [ ] Distinguish measured performance from proxy and estimated performance.
- [ ] Explain the delay between input drift and visible performance degradation.

### Tools and scale

- [ ] Describe the roles of Evidently, whylogs, Great Expectations, NannyML, SageMaker Model Monitor, Vertex AI Model Monitoring, and Databricks Lakehouse Monitoring.
- [ ] Store per-window metrics and baseline identifiers.
- [ ] Explain summaries/sketches and their approximation trade-offs.
- [ ] Monitor justified segments while controlling multiple-comparison risk and alert floods.

### Operations and retraining

- [ ] Define severity levels, owners, escalation, deduplication, and runbooks.
- [ ] Distinguish scheduled, drift-triggered, and performance-triggered retraining.
- [ ] Require quality validation and challenger-versus-champion evaluation.
- [ ] Keep a rollback target and verify runtime state after rollback.
- [ ] Retain monitoring evidence, lineage, fairness checks, and model-risk documentation.
- [ ] Explain awareness-level monitoring for generative-AI input/output quality, groundedness, toxicity, latency, and cost.

---

## 17. Authoritative documentation references

Check the current documentation for the exact installed version and service configuration. The tool APIs and managed-service capabilities evolve.

### Statistical methods

- [SciPy `ks_2samp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html) — two-sample KS test.
- [SciPy `chi2_contingency`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html) — chi-square test for contingency tables and expected counts.
- [SciPy `jensenshannon`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jensenshannon.html) — Jensen–Shannon distance (square root of divergence).
- [SciPy `wasserstein_distance`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wasserstein_distance.html) — one-dimensional Wasserstein-1 distance.

### Monitoring and validation tools

- [Evidently documentation](https://docs.evidentlyai.com/) — data and ML evaluation, drift reports, and monitoring.
- [whylogs documentation](https://docs.whylogs.com/en/latest/) — profiles, profile comparison, and drift visualization.
- [Great Expectations documentation](https://docs.greatexpectations.io/) — expectation-based data validation and data quality.
- [NannyML documentation](https://nannyml.readthedocs.io/en/stable/) — drift analysis and performance estimation with delayed/absent labels.

### Managed monitoring

- [Amazon SageMaker Model Monitor](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html) — data/model quality and monitoring workflows. AWS currently notes that the service is no longer open to new customers; existing customers can continue to use it, so verify availability before choosing it.
- [Vertex AI Model Monitoring](https://cloud.google.com/vertex-ai/docs/model-monitoring/overview) — managed prediction monitoring; check current supported modes and configuration.
- [Databricks Data Quality Monitoring](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-quality-monitoring) — current umbrella name for anomaly detection and Data Profiling (formerly Lakehouse Monitoring); profiling metric tables include profile and drift metrics.

### Related topics in this roadmap

- Module 2C.9 Topic 02 — sampling and approximate algorithms/sketches.
- Module 2C.9 Topic 03 — hypothesis testing and confidence intervals.
- Topic 03 — training data pipelines and dataset versioning.
- Topic 04 — model registry, batch/online inference, prediction logging, champion/challenger, and rollback.
- Module 2.20 Topic 03 — alerting, ownership, and incident response.

---

## Final engineering principle

**Drift is evidence of change, not a verdict on model quality.** Validate the data contract first, quantify changes with methods appropriate to the feature type, compare against a governed and seasonality-aware baseline, and use mature outcomes to measure realized performance. Treat alerts as inputs to a controlled decision process. Retraining should produce a challenger; only validated evaluation, approval, and rollout controls should make it the new champion.
