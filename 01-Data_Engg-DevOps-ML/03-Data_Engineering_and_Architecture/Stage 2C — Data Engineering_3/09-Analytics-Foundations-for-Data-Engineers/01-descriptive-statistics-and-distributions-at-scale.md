# Descriptive Statistics and Distributions at Scale

> **Stage 2C — Data Engineering_3 · Module 09 — Analytics Foundations for Data Engineers · Lesson 01 of 09**
>
> File: `09-Analytics-Foundations-for-Data-Engineers/01-descriptive-statistics-and-distributions-at-scale.md`

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Classify data and choose summaries compatible with its measurement scale.
- Explain centre, spread, quantiles, distributions, skewness, kurtosis, and outliers.
- Interpret correlation carefully and explain confounding and Simpson's paradox.
- Diagnose missingness and choose defensible handling rather than deleting rows automatically.
- Compute exact and approximate statistics with SQL, DuckDB, Polars, and Spark.
- Maintain numerically stable, mergeable summaries across streaming records and partitions.
- Explain why partition averages and percentiles cannot generally be averaged into a global result.
- Profile data in pipelines, detect distribution drift, and communicate p50/p95/p99 and robust summaries.

## 2. Why Data Engineers need this knowledge

Data engineers determine which records exist, how they are typed, when they arrive, which rows are filtered, and how metrics are aggregated. Those decisions shape every downstream analysis. A dashboard can be syntactically correct but misleading because it reports the mean of a heavy-tailed metric, excludes missing values without showing the denominator, or averages daily p95 latency values and labels the result “monthly p95.”

Descriptive statistics **describe observed data**. They do not, by themselves, explain why something happened or establish causal effects. This lesson establishes trustworthy summaries; sampling, formal inference, A/B testing, cohort analysis, time-series modelling, visualization, and stakeholder storytelling are separate lessons in this module.

A useful engineering loop is:

1. Define the unit and metric precisely (event, session, user, order, or partition).
2. Validate types, units, nulls, duplicates, and data freshness.
3. Inspect distributions and robust as well as conventional summaries.
4. Compare the current batch with a suitable baseline.
5. Investigate surprising changes before filtering or transforming data.
6. Store metric definitions, denominators, computation method, and data window with the result.

## 3. Prerequisites and environment setup

You should be comfortable with Python functions, NumPy arrays, SQL grouping and aggregates, and the idea of a partitioned dataset. Spark familiarity helps with the final scale-oriented section.

Use Python 3.12 or newer in an isolated project. One option is:

```bash
mkdir descriptive-stats-lab
cd descriptive-stats-lab
uv init
uv add numpy scipy matplotlib duckdb polars pyspark pandas pyarrow
```

Save the Python examples below in `descriptive_stats_lab.py` and run:

```bash
uv run python descriptive_stats_lab.py
```

Run the DuckDB SQL in the DuckDB CLI, a Python DuckDB connection, or an SQL editor connected to DuckDB. Pandas and PyArrow are only needed for the optional sample comparison in Experiment 6. Spark examples require a working Spark installation and Java runtime; run them in a configured Spark environment rather than assuming the local Python environment already has a cluster.

The lesson deliberately does not claim a 100-million-row benchmark was run. The scale experiment provides a runnable benchmark design and validation checks; observed timings depend on hardware, storage, versions, data types, and execution plans.

## 4. Conceptual foundations

A **population** is the full set of units relevant to a question; a **dataset** is the records actually available. A metric also needs a unit and time window. “Latency” could mean request latency, one value per request, or p95 latency per service per minute. Those are not interchangeable.

Before calculating a statistic, answer:

- What does one row represent?
- What is the measurement unit and valid range?
- Are repeated rows legitimate events or duplicates?
- What do nulls, zeros, and sentinel values mean?
- Is the desired summary across all observations, users, days, or groups?
- Is the result exact, approximate, sampled, or computed after exclusions?

A statistic is only as meaningful as its metric contract and denominator.

## 5. Beginner-level lessons

### 5.1 Data types and measurement scales

| Type | Meaning | Example | Useful summaries / cautions |
|---|---|---|---|
| Continuous numeric | Measured on a continuum, subject to precision | elapsed seconds, temperature | Mean, quantiles, variance; inspect units and precision |
| Discrete numeric | Countable values, often integers | retries, items in cart | Counts, rates, quantiles; fractional averages can still be meaningful |
| Categorical / nominal | Labels without inherent order | country, browser | Counts, proportions, mode; numeric codes are labels, not quantities |
| Ordinal | Ordered categories with uncertain spacing | low/medium/high, star rating | Frequencies, median category, rank methods; differences may not be equal |
| Time / temporal | Instants, dates, durations, intervals | event timestamp, session duration | Timezone, units, censoring, and window definitions matter |
| Text | Strings, documents, event messages | user-agent, error message | Length and category counts may help; raw text needs specialized treatment |

Measurement scales describe what arithmetic is justified:

- **Nominal:** equality and category counts are meaningful; arithmetic on encoded IDs is not.
- **Ordinal:** ordering is meaningful, but equal gaps are not guaranteed.
- **Interval:** differences are meaningful, but zero is arbitrary (for example, Celsius temperature).
- **Ratio:** differences and ratios are meaningful because zero represents absence (for example, duration or bytes transferred).

**Example.** If severity is encoded as `1=low, 2=medium, 3=high`, an average severity of 2.2 assumes a numeric spacing that the labels may not justify. Report category proportions or a median category unless the scoring scheme explicitly defines equal intervals.

**Data Engineering use.** A schema that stores `user_id` as an integer does not make it a numerical measurement. Do not calculate its mean. Preserve timestamps with timezone semantics and durations with explicit units.

**Common errors and trade-offs.** Incorrect types can silently create nonsense aggregates. Numeric casts can fail or coerce malformed values to null; record rejected-value counts rather than silently dropping them. A type system cannot determine business meaning by itself, so document semantics in the data contract.

### 5.2 Measures of centre: mean, median, and mode

For observations \(x_1,\ldots,x_n\):

- **Mean:** \(\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i\). It uses every value and is sensitive to extremes.
- **Median:** the middle ordered value; for even \(n\), commonly the mean of the two middle values. It is robust to a small number of extreme observations.
- **Mode:** the most frequent value or category. There may be ties or no uniquely useful mode for continuous data.

For values `[2, 3, 3, 4, 100]`, mean = 22.4, median = 3, and mode = 3. The mean is mathematically correct, but it is not a good description of a “typical” observation in this highly right-skewed sample.

**When to use which.** Use the mean when totals and additive accounting matter and extremes are valid; median when describing a typical skewed observation; mode for common categories or repeated discrete values. Often report both mean and median, plus quantiles.

**Data Engineering use.** Daily average request latency can hide a small tail of very slow requests. Report p50, p95, and p99 alongside the mean and request count.

**Pitfalls.** Averages of group means are only valid when group weights are equal or the appropriate weights are applied. Medians are not generally mergeable from medians alone. Null-handling conventions differ by API; publish the non-null count with the result.

### 5.3 Measures of spread

Spread describes variability; it is not the same as uncertainty in an estimate.

- **Range:** \(\max(x)-\min(x)\). Easy to explain, but determined by two observations and sensitive to extremes.
- **Population variance:** \(\sigma^2=\frac{1}{N}\sum_i(x_i-\mu)^2\).
- **Sample variance:** \(s^2=\frac{1}{n-1}\sum_i(x_i-\bar{x})^2\), an unbiased estimator of population variance for an i.i.d. sample with finite variance.
- **Standard deviation:** square root of variance; expressed in the original units.
- **Interquartile range (IQR):** \(Q_3-Q_1\), the middle 50% spread; less sensitive to extremes than range or standard deviation.

For `[2, 3, 3, 4, 8]`, range = 6 and median = 3. The sample variance is 5.5 and sample standard deviation is about 2.35; population variance is 4.4 and population standard deviation is about 2.10. State which variance convention is used.

**Why it matters.** Two services can have the same average latency but very different variability and tail behaviour. A narrow IQR with a large maximum may indicate a generally stable service with rare severe incidents.

**Pitfalls and limitations.** Variance is in squared units, and standard deviation can be dominated by outliers. IQR discards information outside the middle half. SQL engines may expose sample and population variants with different names; verify the database dialect.

### 5.4 Quantiles, percentiles, five-number summary, and boxplots

A quantile is a threshold below which a specified fraction of observations lies. The 50th percentile (p50) is a median under the chosen quantile convention; p95 is a value at or below which approximately 95% of observations fall. The exact interpolation convention can differ across libraries and SQL engines, particularly for small datasets.

The **five-number summary** is minimum, Q1 (25th percentile), median, Q3 (75th percentile), and maximum. A boxplot usually shows Q1–Q3 as the box, the median as a line, and whiskers based on a convention; common Tukey boxplots extend whiskers to the most extreme points within 1.5 × IQR of the quartiles and draw more extreme points separately. Whiskers are not necessarily the actual minimum and maximum.

**Example.** If p50 latency is 80 ms, p95 is 240 ms, and p99 is 900 ms, most requests are relatively quick but the tail is much slower. A mean alone cannot communicate this tail structure.

**Engineering use.** Quantiles support SLO reporting, capacity planning, and debugging. Always include population/window, units, filters, and exact-versus-approximate method. Exact quantiles can require substantial memory or sorting; approximate quantile sketches reduce cost but have algorithm-specific error properties.

**Common error.** Averaging daily p95 values does not produce a monthly p95. Percentiles are nonlinear summaries; calculate the percentile over all monthly observations or merge a compatible quantile sketch that represents them.

### 5.5 Common distributions

A distribution describes how values occur. The following are useful models, not promises that real data will match them exactly.

| Distribution | Shape / support | Typical example | Important caveat |
|---|---|---|---|
| Uniform | Equal probability across a bounded interval or finite set | randomized bucket assignment | Real operational data rarely remain uniform without a designed process |
| Normal (Gaussian) | Symmetric bell shape, support on all real numbers | measurement noise under suitable conditions | Negative values may be impossible for metrics such as duration |
| Log-normal | Positive values whose logarithms are approximately normal; right-skewed | multiplicative growth, spend or duration in some systems | Not every positive skewed variable is log-normal |
| Exponential | Non-negative waiting time with constant hazard in the ideal model | inter-arrival times in a Poisson process | Bursty traffic or changing rates violate the assumptions |
| Poisson | Non-negative integer count with rate parameter \(\lambda\) | events per fixed interval under independent constant-rate assumptions | Overdispersion, seasonality, and dependence can invalidate the model |
| Binomial | Number of successes in fixed \(n\) independent Bernoulli trials with probability \(p\) | conversions among a fixed number of eligible users | Requires a defensible trial unit and probability model |
| Heavy-tailed / power-law-like | Tail probability decays slowly; a few values can dominate totals | request sizes, popularity, wealth-like or traffic distributions in some settings | “Heavy-tailed” is broader than “power law”; fitting a power law requires care |

For a power-law-like tail, \(P(X>x)\propto x^{-\alpha}\) over a range for some positive exponent \(\alpha\). A small number of very large observations may account for a large fraction of total volume. Do not infer a power law just because a histogram looks straight on log-log axes.

**Histograms** count observations in bins. Bin width and bin origin affect the picture. **Density plots** estimate a smooth density and can hide multimodality or over-smooth sharp features; their y-axis is density, not count. For discrete values, a bar chart or count plot may be more honest than a continuous density curve.

**Simple interpretation exercise.** A bimodal distribution with peaks near 50 ms and 500 ms may represent two different service paths or client classes. One mean between the peaks might describe neither class well. Segment by a meaningful operational dimension before drawing conclusions.

**Engineering use.** Distribution plots and quantiles can expose schema changes, retries, duplicated events, unit mismatches, and new traffic classes. Do not assume normality just because a tool offers a z-score.

## 6. Intermediate-level lessons

### 6.1 Skewness and kurtosis

**Skewness** describes asymmetry. Positive/right skew often has a long upper tail; negative/left skew has a long lower tail. A common population moment coefficient is \(\gamma_1=E[(X-\mu)^3]/\sigma^3\), but sample estimators apply finite-sample corrections differently.

**Kurtosis** is related to tail weight and extreme observations relative to a normal reference. Pearson kurtosis for a normal distribution is 3; **excess kurtosis** subtracts 3, making the normal reference 0. Definitions and bias corrections differ across libraries. Kurtosis is not simply “peakedness.”

Revenue, latency, and session length are often skewed because they are non-negative, can accumulate multiplicatively, and may have a small fraction of very large values. This is a common pattern, not a universal law: the observed shape depends on product rules, sampling, censoring, segmentation, and measurement.

**Example.** Most sessions may last 1–5 minutes, while a few sessions last several hours. The mean can be pulled upward. Report median and upper quantiles, and investigate whether long sessions are real, bots, background tabs, or instrumentation errors.

**Trade-offs.** Skewness and kurtosis can be unstable for small samples and highly sensitive to outliers. Plot the data and report robust quantiles; do not use a single shape statistic as a complete diagnosis.

### 6.2 Outlier detection and treatment

An outlier is an observation unusual relative to a reference distribution or process. It is not automatically an error.

**IQR rule.** Let \(IQR=Q_3-Q_1\). A common flagging rule marks values below \(Q_1-1.5IQR\) or above \(Q_3+1.5IQR\). This is a screening convention, not a universal deletion rule; it can flag many legitimate values in skewed or large datasets.

**Z-score.** \(z=(x-\bar{x})/s\) expresses distance in standard deviations. A rule such as \(|z|>3\) is a heuristic, not a calibrated error probability unless distributional assumptions are reasonable. Mean and standard deviation themselves can be distorted by extremes.

**Median absolute deviation (MAD).** \(MAD=median(|x_i-median(x)|)\). A robust standardized score for approximately normal data is often \(0.67449(x-median)/MAD\). If MAD is zero (many identical values), this score is undefined; use a domain-specific rule or an alternate robust scale.

**Treatment options:**

1. **Investigate separately:** preserve the raw record and inspect provenance, units, joins, retries, bots, and event semantics. This is often the best first step.
2. **Cap / winsorise:** replace values beyond a chosen boundary with the boundary. This reduces influence but changes the distribution and totals. Record the threshold and retain raw values where possible.
3. **Exclude:** only when a documented validity rule shows the observation is outside the target population (for example, a known test account excluded by a stable policy). Record excluded counts and reasons.
4. **Segment:** report rare but meaningful incidents separately rather than hiding them in an aggregate.

**Example.** A 40-second latency observation in a system whose usual p99 is 800 ms could be a severe incident. Removing it because it is “an outlier” would erase the signal stakeholders need.

**Data Engineering safeguards.** Keep raw and curated layers distinct, emit anomaly flags, log thresholds, and test how summaries change with and without flagged values. Never silently overwrite source measurements.

### 6.3 Correlation is not causation

Correlation describes association, not the causal effect of changing one variable. A third variable can influence both observed variables, selection can create associations, and reverse causality may be possible.

**Pearson correlation** measures linear association between numeric variables:

\[
r=\frac{\sum_i(x_i-\bar{x})(y_i-\bar{y})}{\sqrt{\sum_i(x_i-\bar{x})^2\sum_i(y_i-\bar{y})^2}}.
\]

It ranges from -1 to 1 and is sensitive to outliers. A value near zero means little linear association, not necessarily no relationship.

**Spearman correlation** is Pearson correlation applied to ranks. It measures monotonic association and can capture some nonlinear monotonic relationships, but it does not establish causality and can still be affected by ties and outliers through the ranking structure.

**Confounding example.** Ice-cream sales and swimming incidents may rise together because warm weather increases both. The correlation does not imply ice cream causes incidents. Season or temperature is a plausible confounder.

**Simpson's paradox** occurs when an association in separate groups reverses or changes after aggregation because group sizes and baseline rates differ. It is a warning to understand composition, not a trick that proves one aggregation is always right. Choose the level that matches the business question and causal assumptions.

Reproducible example (conversion rates by group):

```python
# Simpson's paradox: treatment converts better within both groups,
# but is assigned disproportionately to the harder group.
rows = {
    "easy": {"control": (90, 100), "treatment": (19, 20)},
    "hard": {"control": (1, 10), "treatment": (30, 100)},
}
for group, arms in rows.items():
    print(group, {arm: f"{success}/{n} = {success/n:.1%}"
                  for arm, (success, n) in arms.items()})
for arm in ("control", "treatment"):
    success = sum(rows[g][arm][0] for g in rows)
    n = sum(rows[g][arm][1] for g in rows)
    print("overall", arm, f"{success}/{n} = {success/n:.1%}")
```

Expected: treatment is better in `easy` (95% vs 90%) and `hard` (30% vs 10%), but overall treatment is 49/120 = 40.8% while control is 91/110 = 82.7%. The assignment mix differs dramatically. The example demonstrates aggregation reversal; it does **not** mean one should choose a preferred subgroup after seeing the outcome. In real experiments, inspect assignment and prespecified strata and analyse according to the experiment design.

**Engineering use.** Analytics tables should preserve segmentation dimensions and denominators, not only pre-aggregated rates. A single overall rate may obscure mix shifts.

### 6.4 Missing-data mechanisms

- **MCAR (Missing Completely At Random):** missingness is unrelated to observed or unobserved data. This is a strong assumption.
- **MAR (Missing At Random):** conditional on observed variables, missingness does not depend on the missing value itself.
- **MNAR (Missing Not At Random):** missingness depends on the unobserved value or a process not captured by observed variables.

These mechanisms are assumptions about the missingness process; they usually cannot be identified with certainty from observed data alone.

**How summaries are affected.** If expensive purchases are less likely to be reported, the observed mean revenue may be biased downward. If missingness is random, excluding missing observations may be unbiased for some estimands, but reduces sample size. If nulls mean “not applicable,” imputing zero may be semantically wrong.

**Imputation versus exclusion:**

- Exclusion is simple but changes the analysed population and denominator; report missing counts and assess selection bias.
- Imputation can preserve rows but introduces assumptions. Mean imputation reduces observed variance and distorts relationships if used naively.
- For descriptive profiling, often report missingness as its own statistic and compute summaries on observed values with explicit `n_non_null`.
- For operational metrics, distinguish missing, zero, and not-applicable values in the schema and metric contract.

**Example.** A latency field missing for 2% of requests should not automatically be treated as zero latency. Report missing rate and investigate whether failures or timeouts are disproportionately missing.

**Data Engineering practice.** Add per-column null counts/rates, null trends by source/partition, and validity checks. Do not silently coerce parse errors into nulls without a reject counter.

## 7. Advanced and scale-oriented lessons

### 7.1 Exact and approximate computation

An exact statistic is calculated according to a defined convention over all eligible observations. An approximate statistic uses a method designed to reduce time, memory, communication, or cost, with an error profile that depends on the algorithm and configuration. Approximate does not mean inaccurate by definition; exact does not mean useful if the metric definition is wrong.

- Count, sum, and min/max are naturally mergeable with simple operators.
- Mean is recoverable from total sum and count.
- Variance is mergeable if sufficient state is retained (prefer count, mean, and corrected sum of squared deviations, or a numerically safe equivalent).
- Exact quantiles generally cannot be reconstructed from a few partition quantiles. Quantile sketches can be mergeable, but their guarantees and merge requirements depend on the specific sketch.

### 7.2 Welford's online mean and variance

A naive variance formula `mean(x*x) - mean(x)**2` can lose precision when the two terms are large and close together. Welford's method updates a running mean and sum of squared deviations without storing all observations.

For each new value \(x\):

\[
n\leftarrow n+1,\quad \delta=x-\mu,\quad \mu\leftarrow\mu+\delta/n,\quad M_2\leftarrow M_2+\delta(x-\mu).
\]

Population variance is \(M_2/n\); sample variance is \(M_2/(n-1)\) for \(n>1\). This is one-pass and numerically more stable than the raw-sums subtraction in many practical cases.

### 7.3 Mergeable partition statistics

For partitions A and B, with counts \(n_A,n_B\), means \(\mu_A,\mu_B\), and corrected sums of squares \(M_{2,A},M_{2,B}\), define:

\[
\delta=\mu_B-\mu_A,\quad n=n_A+n_B,\quad \mu=\mu_A+\delta\frac{n_B}{n},
\]
\[
M_2=M_{2,A}+M_{2,B}+\delta^2\frac{n_A n_B}{n}.
\]

Then sample variance is \(M_2/(n-1)\), and population variance is \(M_2/n\). Empty partitions need explicit handling. This combination is associative up to floating-point rounding, so it supports parallel aggregation.

**Counts, sums, and sums of squares.** For each partition, count \(n\), sum \(S=\sum x_i\), and raw sum of squares \(Q=\sum x_i^2\) combine by addition. The global mean is \(S/n\), and population variance can be written \(Q/n-(S/n)^2\). This identity is mathematically valid but can suffer catastrophic floating-point cancellation when the values are large and variance is small; use Welford/Chan state (count, mean, and \(M_2\)) for numerically stable merging when possible. An unweighted mean of partition means is wrong when partition sizes differ. Example: partition A `[0, 10]` has mean 5; partition B `[100]` has mean 100. Mean of means = 52.5, but the global mean is 110/3 ≈ 36.67.

**Percentiles.** Daily p95s cannot be averaged to recover a monthly p95. Store underlying observations, or merge a compatible sketch over the observations. A sketch of daily p95 values is not equivalent to a sketch of all daily observations.

### 7.4 Weighted statistics and ratio metrics

For non-negative weights \(w_i\), a weighted mean is \(\bar{x}_w=\sum_i w_i x_i / \sum_i w_i\). The meaning of weights matters: frequency weights, sampling weights, and business weights are not interchangeable. Weighted variance has multiple conventions depending on the weight interpretation and estimator; state the convention instead of applying an unlabelled formula.

A **ratio metric** is a ratio of totals, such as revenue per eligible user: \(R=\sum_i X_i/\sum_i Y_i\), where the denominator must be defined and nonzero. It is not generally the same as the unweighted average of per-row ratios. Example: total revenue / total orders is a weighted average of order-level revenue contributions by order count, not the unweighted average of customer averages unless that is the intended estimand.

The **delta method** approximates variance for a smooth function of random quantities using a first-order Taylor expansion. For a ratio \(R=A/B\), around means \(\mu_A,\mu_B\), a first-order approximation is:

\[
\operatorname{Var}(A/B)\approx\frac{\operatorname{Var}(A)}{\mu_B^2}+\frac{\mu_A^2\operatorname{Var}(B)}{\mu_B^4}-\frac{2\mu_A\operatorname{Cov}(A,B)}{\mu_B^3}.
\]

This is an intuition and approximation, not a substitute for checking assumptions. It can perform poorly when the denominator is near zero, the ratio distribution is highly skewed, or sample sizes are small. Bootstrap and specialized methods are covered in the later inference lesson.

### 7.5 Pipeline profiling, drift, and anomaly thresholds

A profiling step should capture, at minimum:

- Row count and distinct-key counts where feasible.
- Null rate and parse/reject rate for critical columns.
- Min/max and quantiles for numeric/time fields.
- Category frequencies and unexpected categories.
- Duplicate-key rate, freshness/late-arrival counts, and schema version.
- The computation window, source version, and exact/approximate method.

Example daily profile query (adapt date casting and percentile syntax to the target engine):

```sql
SELECT
    event_date,
    COUNT(*) AS row_count,
    COUNT(latency_ms) AS non_null_latency_count,
    COUNT(*) - COUNT(latency_ms) AS null_latency_count,
    AVG(latency_ms) AS mean_latency_ms,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY latency_ms) AS p50_latency_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_latency_ms
FROM request_events
GROUP BY event_date
ORDER BY event_date;
```

Persist the profile with a run ID and compare only equivalent windows and definitions. If the engine does not support this ordered-set syntax, use its documented equivalent or an explicitly approximate function.

**Distribution drift** means the observed distribution changed relative to a reference. A shift can reflect real business change, instrumentation changes, backfill, traffic mix, or a broken join. Compare like with like: same metric definition, units, eligibility, timezone, and sampling procedure.

Thresholds should be calibrated from historical behaviour and operational cost. A fixed rule such as “alert whenever mean changes by 10%” is not universally appropriate. Use robust baselines, minimum-volume guards, segment checks, and severity tiers. A distribution shift is a prompt to investigate, not proof of a defect.

### 7.6 Stakeholder-friendly summaries

A concise operational summary often includes:

- **n**: eligible observations and missing count.
- **p50**: typical experience.
- **p95 / p99**: tail experience and rare slow cases.
- **Mean**: useful for additive cost/total reasoning, with skew caveat.
- **Trimmed mean**: mean after removing a stated fraction from each tail; more robust, but no longer reflects the literal total divided by count.
- A comparison baseline, units, window, and method.

Example: “Across 2.4 million requests yesterday, p50 latency was 72 ms, p95 310 ms, and p99 1.2 s; 0.3% of latency values were missing. The p99 increased from 700 ms in the comparable prior period. We retained extreme values and are investigating the tail.” This is more actionable than “average latency was 110 ms.”

## 8. SQL implementations

SQL aggregate names and quantile APIs vary by engine and version. Verify your target engine's documentation and test on a small known dataset before deploying.

### 8.1 Common aggregation pattern (date syntax is dialect-dependent)

```sql
SELECT
    COUNT(*) AS row_count,
    COUNT(latency_ms) AS non_null_latency_count,
    AVG(latency_ms) AS mean_latency_ms,
    MIN(latency_ms) AS min_latency_ms,
    MAX(latency_ms) AS max_latency_ms
FROM request_events
WHERE event_date >= DATE '2026-10-01'
  AND event_date <  DATE '2026-10-02';
```

`COUNT(*)` includes rows with null latency; `COUNT(latency_ms)` excludes null latency. This difference should be intentional.

### 8.2 DuckDB exact and approximate quantiles

```sql
SELECT
    COUNT(*) AS rows,
    COUNT(latency_ms) AS non_null_rows,
    AVG(latency_ms) AS mean_ms,
    STDDEV_SAMP(latency_ms) AS sample_sd_ms,
    QUANTILE_CONT(latency_ms, 0.50) AS p50_ms,
    QUANTILE_CONT(latency_ms, 0.95) AS p95_ms,
    QUANTILE_CONT(latency_ms, 0.99) AS p99_ms,
    APPROX_QUANTILE(latency_ms, 0.95) AS approx_p95_ms
FROM request_events;
```

DuckDB uses `QUANTILE_CONT` for a continuous/interpolated quantile and supports approximate quantile aggregates such as `APPROX_QUANTILE`; exact names and semantics should be checked against the installed version. `STDDEV_SAMP` is a sample standard deviation.

### 8.3 PostgreSQL-style percentile syntax

```sql
SELECT
    AVG(latency_ms) AS mean_ms,
    STDDEV_SAMP(latency_ms) AS sample_sd_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_ms
FROM request_events;
```

`PERCENTILE_CONT` is an ordered-set aggregate in PostgreSQL-style syntax. It may sort or otherwise process many values and can be expensive for large groups. Some engines implement it differently or do not support the same syntax.

### 8.4 Approximate percentile dialects

Examples of non-portable patterns include `APPROX_PERCENTILE(value, 0.95)` in Trino/Presto-like systems and `APPROX_QUANTILES(value, 100)[OFFSET(95)]` in BigQuery. Names, arguments, output shape, interpolation, and error guarantees differ. Do not paste one dialect's query into another and assume equivalent semantics.

### 8.5 Correct weighted aggregation across partitions

```sql
-- Correct global mean from partition summaries:
SELECT SUM(partition_sum) / NULLIF(SUM(partition_count), 0) AS global_mean
FROM partition_stats;
```

Do **not** use `AVG(partition_mean)` unless each partition has the same eligible count or a justified weighting scheme is applied. Do not calculate a global p95 by applying `AVG()` to partition p95 values.

## 9. Python implementations

The following self-contained program uses fixed seeds, includes expected invariants, and avoids pandas for the large-data path. Save as `descriptive_stats_lab.py`.

```python
from __future__ import annotations

import math
import numpy as np


def welford(values):
    """Return (count, mean, M2) for finite numeric values using Welford's method."""
    n = 0
    mean = 0.0
    m2 = 0.0
    for raw in values:
        x = float(raw)
        if not math.isfinite(x):
            raise ValueError("Welford input must contain only finite values")
        n += 1
        delta = x - mean
        mean += delta / n
        delta2 = x - mean
        m2 += delta * delta2
    return n, mean if n else math.nan, m2


def merge_welford(left, right):
    """Merge (n, mean, M2) states, handling empty states."""
    n_a, mean_a, m2_a = left
    n_b, mean_b, m2_b = right
    if n_a == 0:
        return right
    if n_b == 0:
        return left
    n = n_a + n_b
    delta = mean_b - mean_a
    mean = mean_a + delta * n_b / n
    m2 = m2_a + m2_b + delta * delta * n_a * n_b / n
    return n, mean, m2


def describe(name, values):
    """Describe a non-empty 1-D finite numeric array; sample SD is undefined for n < 2."""
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 1:
        raise ValueError("describe expects a one-dimensional array")
    if values.size == 0:
        raise ValueError("describe requires at least one eligible observation")
    if not np.isfinite(values).all():
        raise ValueError("describe input must contain only finite values; apply an explicit null/invalid policy first")
    q = np.quantile(values, [0.0, 0.25, 0.5, 0.75, 0.95, 0.99, 1.0], method="linear")
    sample_sd = values.std(ddof=1) if values.size >= 2 else math.nan
    print(f"{name}: n={len(values)}, mean={values.mean():.3f}, "
          f"median={np.median(values):.3f}, sample_sd={sample_sd:.3f}")
    print("  min, q1, p50, q3, p95, p99, max =", np.round(q, 3))


def main():
    rng = np.random.default_rng(20261019)
    normal = rng.normal(loc=100, scale=15, size=20_000)
    lognormal = rng.lognormal(mean=3.5, sigma=0.9, size=20_000)
    # Bimodal mixture: two normal populations with separated centres.
    component = rng.random(20_000) < 0.65
    bimodal = np.where(component,
                       rng.normal(50, 5, 20_000),
                       rng.normal(100, 8, 20_000))
    for name, values in (("normal", normal), ("lognormal", lognormal),
                         ("bimodal", bimodal)):
        describe(name, values)

    # Revenue-like example: most values are modest, with a few large values.
    revenue = np.array([10, 12, 12, 15, 18, 20, 22, 25, 30, 5000], dtype=float)
    print("revenue mean:", revenue.mean())
    print("revenue p50/p90/p95/max:", np.quantile(revenue, [0.5, 0.9, 0.95, 1.0]))
    assert revenue.mean() > 10 * np.median(revenue)

    # Explicit edge-case tests: empty input has no mean; singleton M2 is zero,
    # while sample variance is undefined because n - 1 is zero.
    empty = welford([])
    assert empty[0] == 0 and math.isnan(empty[1]) and empty[2] == 0
    singleton = welford([7])
    assert singleton == (1, 7.0, 0.0)
    assert merge_welford(empty, singleton) == singleton
    for invalid in ([float("nan")], [float("inf")], [-float("inf")]):
        try:
            welford(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("Welford must reject non-finite values")

    # Welford agrees with NumPy for sample variance within floating tolerance.
    values = rng.normal(1e8, 3.0, size=100_000)
    n, mean, m2 = welford(values)
    assert n == len(values)
    assert np.isclose(mean, values.mean(), rtol=1e-12, atol=1e-7)
    assert np.isclose(m2 / (n - 1), values.var(ddof=1), rtol=1e-7, atol=1e-7)

    # Partition states merge to the full-data state.
    split = len(values) // 3
    states = [welford(values[:split]), welford(values[split:2*split]),
              welford(values[2*split:])]
    merged = merge_welford(merge_welford(states[0], states[1]), states[2])
    assert merged[0] == n
    assert np.isclose(merged[1], mean, rtol=1e-12, atol=1e-7)
    assert np.isclose(merged[2] / (n - 1), m2 / (n - 1), rtol=1e-7, atol=1e-7)

    # Percentile non-mergeability: average of daily p95s differs from global p95.
    day_a = np.arange(1, 101, dtype=float)
    day_b = np.arange(1001, 1101, dtype=float)
    avg_daily_p95 = np.mean([np.quantile(day_a, .95), np.quantile(day_b, .95)])
    monthly_p95 = np.quantile(np.concatenate([day_a, day_b]), .95)
    print("average daily p95:", avg_daily_p95, "monthly p95:", monthly_p95)
    assert not np.isclose(avg_daily_p95, monthly_p95)

    # Correct mean across unequal partitions: aggregate sums and counts.
    a = np.array([0.0, 10.0])
    b = np.array([100.0])
    wrong = (a.mean() + b.mean()) / 2
    correct = (a.sum() + b.sum()) / (len(a) + len(b))
    assert not np.isclose(wrong, correct)
    assert np.isclose(correct, np.array([0.0, 10.0, 100.0]).mean())
    print("partition means: naive=", wrong, "correct=", correct)

    print("All mathematical assertions passed.")


if __name__ == "__main__":
    main()
```

**Expected behaviour:** the normal sample should have mean and median near 100; the log-normal sample should be strongly right-skewed with mean above median; the bimodal mixture should show a centre between its two modes. Exact values vary only if the seed, generator, library implementation, or inputs change. The program prints computed outputs instead of hard-coding floating-point numbers that may vary slightly by version.

**MAD example:**

```python
import numpy as np
x = np.array([10, 11, 11, 12, 12, 13, 1000], dtype=float)
median = np.median(x)
mad = np.median(np.abs(x - median))
robust_z = np.full(x.shape, np.nan) if mad == 0 else 0.67449 * (x - median) / mad
print("median", median, "MAD", mad, "robust z", robust_z)
```

The extreme value is flagged for investigation; the code does not delete it. If `MAD == 0`, do not interpret the resulting `NaN` scores as “no outliers”; use a documented alternate scale or domain rule.

**Trimmed-mean example:**

```python
from scipy.stats import trim_mean
trimmed = trim_mean(values, proportiontocut=0.10)  # trim 10% from each tail
print('10%-trimmed mean:', trimmed)
```

The exact number trimmed from each tail depends on the sample size and function convention. It is a robust descriptive summary, not the literal total divided by the original count. Report the trimming fraction and sample size.

## 10. DuckDB, Polars, and Spark comparison

### 10.1 DuckDB: analytical SQL on one machine

DuckDB is an embedded analytical database. It is useful for local files, Parquet, SQL transformations, and columnar aggregations. It can process data larger than RAM for many workloads using out-of-core execution, but not every query or operator has identical memory behaviour. Exact quantiles and high-cardinality groupings can be memory-intensive.

```python
import duckdb

con = duckdb.connect("stats_lab.duckdb")
con.execute("""
CREATE OR REPLACE TABLE events AS
SELECT * FROM read_parquet('data/events/*.parquet')
""")
result = con.execute("""
SELECT COUNT(*) AS n,
       AVG(amount) AS mean_amount,
       QUANTILE_CONT(amount, 0.50) AS p50,
       APPROX_QUANTILE(amount, 0.95) AS approx_p95
FROM events
WHERE amount IS NOT NULL
""").df()
print(result)
```

The final `.df()` materializes only the small aggregate result, not the entire input. Ensure the Parquet glob matches the intended files.

### 10.2 Polars lazy execution

Polars lazy queries build a query plan and can optimize projections, predicates, and execution. Lazy does not mean that every operation is streaming or memory-free; inspect plans and test the operators used in your version.

```python
import polars as pl

lf = pl.scan_parquet("data/events/*.parquet")
summary = (
    lf.filter(pl.col("amount").is_not_null())
      .select(
          pl.len().alias("n"),
          pl.col("amount").mean().alias("mean_amount"),
          pl.col("amount").quantile(0.50).alias("p50"),
          pl.col("amount").quantile(0.95).alias("p95"),
      )
      .collect()
)
print(summary)
```

Exact quantile behaviour and streaming support depend on Polars version and operation. Confirm whether the chosen plan can stream and whether it materializes large intermediate data.

### 10.3 Spark for cluster-scale processing

Spark distributes work across partitions and executors. It is appropriate when a workload exceeds a single machine's practical capacity or must integrate with a cluster data platform. It adds shuffle, scheduling, serialization, cluster, and operational overhead; a cluster is not automatically faster for a small dataset.

```python
from pyspark.sql import SparkSession, functions as F

spark = (SparkSession.builder
         .appName("descriptive-stats")
         .getOrCreate())

df = spark.read.parquet("s3a://example-bucket/events/")
summary = df.agg(
    F.count("amount").alias("non_null_n"),
    F.avg("amount").alias("mean_amount"),
    F.stddev_samp("amount").alias("sample_sd"),
    F.expr("percentile_approx(amount, 0.50, 10000)").alias("approx_p50"),
    F.expr("percentile_approx(amount, 0.95, 10000)").alias("approx_p95"),
)
summary.show(truncate=False)
spark.stop()
```

`percentile_approx` is approximate, and its accuracy parameter controls the implementation's approximation/memory trade-off according to Spark's documented semantics. It is not equivalent to a universal fixed error percentage. Use the actual filesystem URI and configure credentials, network, executor resources, and Spark version for your environment.

### 10.4 Scale-aware comparison and benchmark design

| Tool | Strong fit | Memory/runtime considerations | Quantile note |
|---|---|---|---|
| DuckDB | SQL-first local analytics over Parquet/CSV and embedded workflows | Single host; can spill for supported operations; disk bandwidth and query shape matter | Exact and approximate aggregates available; validate semantics |
| Polars lazy | DataFrame pipelines with optimizer and columnar execution | Single host; lazy plan can reduce materialization; not every operation streams | Quantile API and streaming behaviour are version-dependent |
| Spark | Data beyond one host, distributed pipelines, shared lakehouse processing | Shuffle and cluster overhead; partition sizing, skew, and executor memory matter | Often use approximate quantile functions for scalable summaries |

**Runnable benchmark design (not a reported benchmark):**

1. Generate a deterministic dataset in Parquet in batches, rather than building 100M Python objects in RAM.
2. Use the same schema, row count, null rate, and distribution for each engine.
3. Run a warm-up and multiple measured runs; record versions, CPU/RAM, disk, file sizes, parallelism, wall time, peak memory, and spill/shuffle metrics.
4. Compare equivalent semantics: exact against exact, approximate against approximate with documented parameters. Do not compare different quantile definitions as if identical.
5. Validate row count, null count, mean, and selected quantiles against a manageable exact sample or a trusted engine. Sampling validates plausibility, not exact global equality.
6. Report failures and resource limits as results. Do not extrapolate a small sample's timing linearly to 100M rows without caveats.

A 100-million-row benchmark should be attempted only on hardware and storage with enough capacity. Use batch generation and Parquet scans; avoid loading all rows into pandas. The exact feasible row count depends on row width, string columns, operation, concurrency, and available memory.

## 11. Practical lab and experiments

Create an `experiments/01_descriptive/` directory. The exercises below can use the Python program in Section 9 and SQL examples in Section 8.

### Experiment 1 — Compare normal, log-normal, and bimodal data

Run the Section 9 program. Predict the median and mean before inspecting output. Verify:

- Normal data are approximately symmetric at this sample size, but not exactly symmetric.
- Log-normal data are positive and typically have mean greater than median.
- A bimodal mixture can have a mean between modes, which may describe neither component.

Plot histograms with common plotting settings if desired, but remember that bins affect apparent shape. Do not infer a distribution family from one plot alone.

### Experiment 2 — Mean versus percentiles for revenue

The provided revenue example has one large value. Calculate mean, median, p90, p95, and maximum. Write two sentences: one describing the arithmetic mean, and one describing a typical customer/order and the tail. Explain which question each statistic answers. Do not winsorise the value unless a documented data-quality rule justifies it.

### Experiment 3 — Simpson's paradox

Run the code in Section 6.3. Compute subgroup and overall rates manually. Explain the denominator and group mix for each arm. Then change group sizes and observe how aggregation changes. In a real randomized experiment, do not use post hoc subgroup selection to claim a causal effect.

### Experiment 4 — Welford against NumPy

Run Section 9. The assertions compare mean and sample variance against NumPy and compare a merged partition state against the whole-data state. Also test empty input and singleton input:

```python
assert welford([])[0] == 0
one = welford([7])
assert one[0] == 1 and one[1] == 7 and one[2] == 0
```

For a singleton, sample variance is undefined because the denominator is zero; the stored `M2` is zero, not a valid sample variance.

### Experiment 5 — Daily p95 is not monthly p95

The code builds two disjoint daily samples and compares the average of their p95 values with the p95 over all observations. The values are intentionally far apart so the mismatch is visible. The correct exact result is computed from the concatenated observations. For data too large to collect, use a compatible mergeable quantile sketch or compute the percentile in a distributed engine.

### Experiment 6 — DuckDB and Polars on large data

The roadmap exercise targets 100M rows. This is a **reproducible benchmark procedure**, not a claim that this file's author executed it. Confirm that the machine has sufficient disk space and run time before starting.

One option is to generate the data in DuckDB and persist it as Parquet, letting the engine construct the relation rather than creating 100M Python objects. Create the output directory first (`mkdir -p data` on macOS/Linux or create it in your file browser on Windows):

```sql
COPY (
    SELECT
        i AS event_id,
        CAST((i % 100000) AS DOUBLE) / 100.0 AS amount,
        CAST(i % 31 AS INTEGER) AS segment_id
    FROM range(100000000) AS r(i)
) TO 'data/events_100m.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
```

Verify the artifact rather than trusting the requested row count:

```sql
SELECT COUNT(*) AS actual_rows,
       COUNT(amount) AS non_null_amounts,
       MIN(amount) AS min_amount,
       MAX(amount) AS max_amount
FROM read_parquet('data/events_100m.parquet');
```

Then scan the same Parquet file with DuckDB and Polars using equivalent columns and eligibility rules. Record tool versions, hardware, file size, warm-up policy, repeat count, wall time, peak memory, and query plan. Compare exact to exact or approximate to approximate; do not report timings from different operations as a fair comparison.

For the roadmap's “exact pandas on a sample” comparison, explicitly sample a bounded number of rows, such as 1M, and calculate exact NumPy/pandas summaries on that sample. Label them **sample summaries**, not the exact global 100M-row answer. If you need a globally exact result, calculate it over the complete dataset with an exact-capable engine/operator and adequate resources.

Example deterministic sample:

```sql
COPY (
    SELECT event_id, amount
    FROM read_parquet('data/events_100m.parquet')
    WHERE event_id % 100 = 0
) TO 'data/events_sample_1m.parquet' (FORMAT PARQUET);
```

Because `event_id` runs from 0 to 99,999,999, this selects 1,000,000 rows. Compare summaries on the **same sample** with pandas, DuckDB, and Polars. Install pandas and a Parquet engine (for example, `pyarrow`) only if you run this optional comparison. Do not load the 100M-row file into pandas:

```python
import duckdb
import pandas as pd
import polars as pl

sample_path = 'data/events_sample_1m.parquet'
pdf = pd.read_parquet(sample_path)  # sample only, not the 100M-row source
print('pandas', pdf['amount'].count(), pdf['amount'].mean(),
      pdf['amount'].median(), pdf['amount'].quantile([0.50, 0.95]))
print('DuckDB', duckdb.sql(
    f"SELECT COUNT(amount), AVG(amount), QUANTILE_CONT(amount, 0.50), "
    f"QUANTILE_CONT(amount, 0.95) FROM read_parquet('{sample_path}')"
).fetchone())
print('Polars', pl.scan_parquet(sample_path).select(
    pl.col('amount').count().alias('n'),
    pl.col('amount').mean().alias('mean'),
    pl.col('amount').quantile(0.50).alias('p50'),
    pl.col('amount').quantile(0.95).alias('p95'),
).collect())
```

Small differences may occur if quantile interpolation conventions differ. Record each engine's method and compare like-for-like; do not infer that one engine is wrong solely because a quantile differs slightly.

### Experiment 7 — Process beyond one machine with Spark

Point Section 10.3 to the same Parquet dataset in distributed storage. Inspect the physical plan and Spark UI for stages, shuffles, spills, and skewed tasks. Compare results within the expected exact/approximate semantics. If a local Spark session runs on one machine, it demonstrates the API but not cluster-scale performance.

### Experiment 8 — Correct partition statistics

Split a known vector into unequal partitions. Combine counts and sums to calculate the global mean. Use Welford state merging to calculate global sample variance. Assert that the results match a direct calculation on the full vector. Demonstrate that the unweighted mean of partition means fails when partition counts differ, and that the mean of partition p95 values does not equal the global p95.

## 12. Testing and verification of results

Statistics code should be tested with known-answer cases, edge cases, and alternate partitioning. Useful invariants include:

- Count equals the number of eligible observations; null count is tracked separately.
- Minimum ≤ Q1 ≤ median ≤ Q3 ≤ maximum for a non-empty numeric sample under one quantile convention.
- Adding a constant shifts mean and quantiles by that constant but leaves variance unchanged.
- Multiplying observations by a constant multiplies standard deviation by its absolute value and variance by its square.
- Merging partition states yields the same result as a one-pass computation within floating-point tolerance.
- An empty set has no meaningful mean/quantile; do not silently report zero.
- A sample standard deviation requires at least two observations.
- Exact and approximate quantiles should be compared with a stated tolerance and algorithm setting, not expected to be identical.

The assertions in Section 9 verify the central Welford, partition-merge, unequal-partition mean, and percentile examples. They are executable checks, not a proof that every possible input is correct. Add tests for non-finite values, null policy, empty partitions, integer overflow in fixed-width sums, and highly unbalanced partitions before production use.

## 13. Production use cases and failure modes

### Use case A: API latency profiling

Compute request count, missing-latency rate, p50/p95/p99, and error rate by service and time window. Retain extreme latency values; correlate spikes with deploys and infrastructure signals. Avoid averaging per-minute p95s to form a daily p95.

### Use case B: Revenue and order analytics

Report count, total, mean, median, and upper percentiles. Keep refunds, currency conversions, and eligibility rules explicit. A single large enterprise order may be valid and important; inspect it rather than automatically capping it.

### Use case C: Ingestion data quality

Profile null rates, min/max timestamps, duplicate keys, category distributions, and row counts per source partition. Compare with baselines and alert on material shifts after checking sample size and seasonality. Store the profile with a run ID so incidents are reproducible.

### Use case D: Partitioned batch computation

Persist mergeable states such as count, sum, and `(n, mean, M2)` for mean/variance rollups. For quantiles, retain raw data at the required grain or use a supported mergeable sketch. Never merge only daily percentiles as if they represented daily observations.

**Common failure modes:**

- **Silent denominator change:** nulls or invalid rows disappear without counts. Fix by reporting total, eligible, missing, and excluded counts.
- **Metric grain mismatch:** one row per request is mixed with one row per user. Define the grain and aggregate deliberately.
- **Unit mismatch:** milliseconds and seconds are combined. Enforce schema units and ranges.
- **Outlier deletion:** a real incident disappears. Flag and investigate before treatment.
- **Unstable variance:** raw sum-of-squares subtraction loses precision. Use Welford/merge formulas or a trusted stable engine aggregate.
- **Approximation mismatch:** different engines use different quantile definitions or error parameters. Document method and tolerance.
- **Composition drift:** overall averages move because traffic mix changes. Keep segment counts and inspect within-segment summaries.
- **Uncalibrated alert:** a fixed percentage threshold fires constantly or misses meaningful shifts. Calibrate to history and operational impact.

## 14. Exercises with solutions

### Exercise 1: Choose a centre

A metric has mean 240, median 75, p95 900, and maximum 20,000. What should you report as “typical”?

**Solution:** The median (75) is usually a better typical-value summary for this strongly right-skewed metric. Report p95 and maximum for tail visibility, plus mean if total-weighted operational cost matters. Investigate the maximum; do not automatically remove it.

### Exercise 2: Combine two partition means

Partition A has count 1,000 and mean 10. Partition B has count 9,000 and mean 20. What is the global mean?

**Solution:** \((1000\cdot10+9000\cdot20)/(1000+9000)=19\). The unweighted mean of means, 15, is wrong because the partition sizes differ.

### Exercise 3: Interpret an outlier

An IQR rule flags a latency of 8 seconds when the upper fence is 1.2 seconds. Should it be deleted?

**Solution:** Not based on the fence alone. Verify unit, source, request path, timeout/retry semantics, and incident context. Preserve it if it is a valid slow request; exclude only under a documented eligibility rule.

### Exercise 4: Missing revenue

A source omits revenue more often for failed orders. Is complete-case mean revenue automatically unbiased?

**Solution:** No. Missingness is associated with order outcome, so the observed rows may not represent the target population. Investigate the missingness process, define the estimand, report missingness, and consider a justified model or sensitivity analysis rather than blindly imputing or excluding.

### Exercise 5: Pick an engine

A 2 GB Parquet dataset fits comfortably on a workstation and needs several SQL summaries. A 4 TB dataset is already in a Spark lakehouse and exceeds a single host's practical resources. Which is preferable?

**Solution:** DuckDB or Polars may be simpler for the first workload; benchmark the actual query. Spark is a natural candidate for the second because data and compute are distributed already. This is a workload-dependent decision, not a universal size threshold.

### Exercise 6: Percentile rollup

Three daily p95 values are 100 ms, 120 ms, and 900 ms. Is their average the monthly p95?

**Solution:** No. Daily p95s are summaries, not the underlying distribution. Calculate the percentile over all eligible observations in the month or merge a compatible sketch built from those observations.

## 15. Common mistakes

1. Reporting only the mean for a skewed metric.
2. Treating integer identifiers or encoded categories as quantities.
3. Confusing standard deviation with standard error or uncertainty in the mean.
4. Assuming all real data are normally distributed.
5. Treating every flagged outlier as invalid.
6. Assuming a z-score threshold has universal meaning.
7. Treating correlation as causal evidence.
8. Ignoring group composition and denominators when interpreting rates.
9. Treating null as zero or excluding nulls without reporting the count.
10. Averaging partition means without weights or averaging percentiles.
11. Assuming a lazy query or a distributed engine is automatically memory-free or faster.
12. Claiming approximate results are exact or asserting benchmark numbers without measurement.
13. Comparing quantiles from different engines without checking conventions and approximation settings.
14. Using a fixed anomaly threshold without a baseline, minimum volume, or investigation workflow.

## 16. Knowledge checkpoint

Answer these without looking back:

1. Why can a mean be correct but misleading for revenue?
2. What information do p50, p95, and p99 add that a mean does not?
3. Why are median and percentile values not generally mergeable from partition medians/percentiles?
4. How does Welford's method update mean and variance without retaining all values?
5. What assumptions make a z-score-based outlier rule questionable?
6. Distinguish MCAR, MAR, and MNAR.
7. Explain how Simpson's paradox can arise from different group composition.
8. When is an approximate percentile appropriate, and what must be documented?
9. What state is sufficient to combine partition means correctly? What state is useful for stable variance merging?
10. Why is a distribution shift an investigation signal rather than automatic proof of bad data?

You are ready to continue when you can explain the choices, compute the examples, pass the assertions, and describe limitations—not merely repeat definitions.

## 17. Final competency checklist

- [ ] I can classify numeric, categorical, ordinal, time, and text data and choose appropriate summaries.
- [ ] I can calculate and interpret mean, median, mode, range, variance, standard deviation, IQR, quantiles, and five-number summaries.
- [ ] I can distinguish common distribution families and recognize skew and multimodality without overclaiming a fitted model.
- [ ] I can explain IQR, z-score, and MAD outlier rules and preserve potentially meaningful observations.
- [ ] I can distinguish correlation from causation and explain confounding and Simpson's paradox.
- [ ] I can explain MCAR/MAR/MNAR and make missingness visible in reports.
- [ ] I can write dialect-aware SQL summaries and distinguish exact from approximate quantiles.
- [ ] I can implement and verify Welford's algorithm and merge partition states correctly.
- [ ] I understand why partition averages and percentiles cannot generally be averaged into global statistics.
- [ ] I can explain weighted means, ratio metrics, and the delta-method intuition and limitations.
- [ ] I can profile distributions in a pipeline and design calibrated drift checks.
- [ ] I can report a metric with units, time window, denominator, null count, quantiles, and computation method.

## 18. References to authoritative documentation

Consult the documentation for the versions actually deployed; function names and semantics can change.

- NumPy statistics and quantiles: https://numpy.org/doc/stable/reference/routines.statistics.html
- NumPy `quantile`: https://numpy.org/doc/stable/reference/generated/numpy.quantile.html
- SciPy statistical functions: https://docs.scipy.org/doc/scipy/reference/stats.html
- DuckDB aggregate functions: https://duckdb.org/docs/stable/sql/functions/aggregates.html
- DuckDB Python API: https://duckdb.org/docs/stable/clients/python/overview
- Polars lazy API: https://docs.pola.rs/user-guide/lazy/using/
- Polars expressions and aggregations: https://docs.pola.rs/api/python/stable/reference/expressions/index.html
- Apache Spark SQL built-in functions: https://spark.apache.org/docs/latest/api/sql/index.html
- Apache Spark `DataFrameStatFunctions`: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameStatFunctions.html
- PostgreSQL aggregate functions: https://www.postgresql.org/docs/current/functions-aggregate.html
- Trino aggregate functions: https://trino.io/docs/current/functions/aggregate.html
- GoogleSQL approximate aggregate functions: https://cloud.google.com/bigquery/docs/reference/standard-sql/approximate_aggregate_functions

---

**Lesson boundary:** This lesson covers descriptive statistics and distributions at scale. Sampling/sketch families, hypothesis testing, A/B testing, cohort/funnel analysis, time-series forecasting, BI tooling, visualization craft, and data storytelling remain assigned to the subsequent lessons in Module 09.
