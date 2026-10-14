# Volume, Freshness, and Distribution Anomaly Checks

> **Stage 2 — Python for Data Engineering**  
> **Module 2.11 — Data Validation, Contracts, and Quality**  
> **Topic 08 — Volume, Freshness, and Distribution Anomaly Checks**

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain why structural validation alone cannot prove that a dataset is healthy;
- distinguish **validity, completeness, volume, freshness, distribution, consistency, anomaly, drift, failure, and incident**;
- build volume checks using absolute and relative thresholds;
- calculate percentage deviation safely, including zero-baseline cases;
- reason about freshness using event time, ingestion time, processing time, and publication time;
- calculate freshness lag with timezone-aware Python datetimes;
- distinguish freshness from completeness;
- understand watermarks, late-arriving data, freshness SLAs, SLOs, and acceptable lateness;
- inspect numeric and categorical distributions;
- monitor null rates and cardinality;
- construct historical baselines;
- account for daily, weekly, hourly, weekday/weekend, and business-event seasonality;
- detect anomalies with fixed thresholds, relative deviation, rolling statistics, z-scores, IQR, MAD, and percentiles;
- understand distribution-shift techniques such as PSI, KL divergence, Jensen-Shannon divergence, and KS-test concepts;
- understand the difference between a statistical anomaly and a business anomaly;
- control false positives, false negatives, alert fatigue, and maintenance-window noise;
- map anomaly results to severity and pipeline actions;
- implement checks in standard Python and pandas;
- design batch and streaming anomaly monitoring;
- reason about performance, sampling, approximate statistics, and incremental metrics;
- integrate anomaly checks with Pandera, Great Expectations, Soda, SQL, and orchestration/observability systems;
- debug real production anomalies systematically;
- test anomaly detection with synthetic defects;
- build a production-oriented anomaly monitor;
- answer Data Engineering interview and system-design questions about anomaly detection.

The progression is:

```text
basic intuition
    ↓
terminology
    ↓
why it exists
    ↓
internal mechanics
    ↓
small examples
    ↓
Python
    ↓
pandas
    ↓
historical baselines
    ↓
anomaly detection
    ↓
production rules
    ↓
false-positive control
    ↓
advanced techniques
    ↓
architecture
    ↓
testing
    ↓
debugging
    ↓
mini-project
    ↓
interview / architecture
```

---

# 2. Why Structural Validation Is Not Enough

A common beginner assumption is:

> "If the schema is correct and every row passes validation, the dataset is healthy."

That is false.

A dataset can be structurally valid and still be operationally wrong.

For example:

```text
schema: valid
types: valid
row-level validation: valid
volume: wrong
freshness: wrong
distribution: wrong
```

Consider an orders table expected to receive approximately one million records every day.

The pipeline reports:

```text
job status = SUCCESS
schema check = PASS
record validation = PASS
rows written = 0
```

Technically, the pipeline may have completed successfully.

Operationally, the dataset is broken.

Another example:

```text
yesterday:
customer_age median = 34
customer_age p95 = 67

today:
customer_age median = 34
customer_age p95 = 67
```

But the source only delivered 20% of the expected records.

The distribution looks normal because the missing data happens to resemble the remaining population.

This is why production data-quality monitoring needs multiple signals:

1. **Volume**
2. **Freshness**
3. **Distribution**
4. **Historical baselines**
5. **Thresholds**
6. **Anomaly detection**
7. **Severity/action policies**
8. **Alerting and observability**
9. **Investigation and debugging**
10. **Production feedback loops**

---

# 3. The Three Operational Quality Signals

## 3.1 Volume

Volume asks:

> **Did approximately the expected amount of data arrive?**

Examples:

```text
rows today
events per hour
orders per region
customers per source
```

---

## 3.2 Freshness

Freshness asks:

> **Did the data arrive on time?**

A dataset can have one million records and still be stale.

---

## 3.3 Distribution

Distribution asks:

> **Does the data still behave like expected?**

For example:

```text
payment_status:
success = 95%
failed  = 4%
pending = 1%
```

If this suddenly becomes:

```text
success = 50%
failed  = 48%
pending = 2%
```

the schema may still be perfectly valid.

The population has changed dramatically.

---

# 4. Fundamental Terminology

Before learning anomaly detection, distinguish these terms.

| Concept | Core Question |
|---|---|
| Validity | Does data obey defined rules? |
| Completeness | Is required data present? |
| Volume | Did the expected amount arrive? |
| Freshness | Did data arrive on time? |
| Distribution | What statistical/value pattern does the data have? |
| Consistency | Does data agree across representations/systems? |
| Anomaly | Is an observation unusual relative to a reference? |
| Drift | Is behavior changing over time? |
| Failure | Did a technical or data-quality condition violate a requirement? |
| Incident | Does a failure require operational response? |

These concepts overlap but are not interchangeable.

---

# 5. A Simple Example

Suppose the pipeline expects:

```text
1,000,000 orders
```

It receives:

```text
420,000 orders
```

The records that did arrive may all be valid.

Therefore:

```text
record validity = good
volume = bad
```

Possible causes include:

- source failure;
- extraction truncation;
- API pagination bug;
- upstream filtering;
- partition loss;
- duplicate handling;
- business event reduction;
- legitimate demand change.

The monitoring system should detect the deviation.

It should not automatically claim to know the root cause.

---

# 6. Volume Checks

## 6.1 What Is Data Volume?

Data volume is the amount of data observed for a defined scope.

The scope could be:

- total row count;
- records per partition;
- records per hour;
- records per day;
- records per source;
- records per customer;
- records per region;
- records per event type.

Example:

```text
daily orders = 1,250,000
```

is one volume metric.

But:

```text
orders by region
```

may reveal that:

```text
US       = 900,000
EU       = 300,000
APAC     = 50,000
```

while historically APAC normally contributes 200,000.

Total volume might appear acceptable while one business segment is broken.

---

# 7. Row Count Checks

The simplest volume check is:

```python
row_count = len(records)
```

For pandas:

```python
row_count = len(df)
```

or:

```python
row_count = df.shape[0]
```

A basic rule might be:

```python
def check_minimum_volume(
    row_count: int,
    minimum_rows: int,
) -> bool:
    return row_count >= minimum_rows
```

Example:

```python
actual = 420_000
minimum = 500_000

print(check_minimum_volume(actual, minimum))
# False
```

This tells you that the observed count is below policy.

It does not tell you why.

---

# 8. Minimum and Maximum Volume

A minimum rule:

```text
rows >= minimum
```

A maximum rule:

```text
rows <= maximum
```

Example:

```python
def check_volume_bounds(
    row_count: int,
    minimum_rows: int,
    maximum_rows: int,
) -> bool:
    return minimum_rows <= row_count <= maximum_rows
```

Maximum-volume checks are useful because an unexpected spike can also indicate:

- duplicated extraction;
- pagination loops;
- replayed files;
- upstream filtering removal;
- duplicate events;
- source-system failure;
- legitimate demand growth.

A volume spike can be as important as a volume drop.

---

# 9. Expected Volume

Instead of using only hard-coded bounds, compare current volume with an expected value.

Example:

```text
expected = 1,000,000
actual   =   920,000
```

Deviation:

```text
-80,000
```

Percentage deviation:

```text
(920,000 - 1,000,000) / 1,000,000 × 100
= -8%
```

This provides more context than a simple minimum rule.

---

# 10. Absolute Thresholds

An absolute threshold is a fixed limit.

Example:

```text
row_count >= 500,000
```

Python:

```python
def passes_absolute_minimum(
    current_rows: int,
    minimum_rows: int,
) -> bool:
    return current_rows >= minimum_rows
```

Absolute thresholds are easy to understand and operate.

They work well when:

- volume is naturally stable;
- a hard minimum is meaningful;
- business requirements define a concrete floor.

They can become brittle when volume naturally changes.

---

# 11. Relative Thresholds

A relative rule compares current volume with a baseline.

Example:

```text
current >= 80% of baseline
```

Python:

```python
def passes_relative_threshold(
    current: float,
    baseline: float,
    minimum_ratio: float,
) -> bool:
    if baseline <= 0:
        raise ValueError("baseline must be positive")

    return current / baseline >= minimum_ratio
```

Example:

```python
current = 920_000
baseline = 1_000_000

print(
    passes_relative_threshold(
        current,
        baseline,
        minimum_ratio=0.80,
    )
)
# True
```

This is usually more adaptable than one fixed row count.

---

# 12. Percentage Change

The standard formula is:

```text
change_pct =
    (current - baseline)
    / baseline
    × 100
```

Python:

```python
def percentage_change(
    current: float,
    baseline: float,
) -> float:
    if baseline == 0:
        raise ValueError(
            "percentage change is undefined when baseline is zero"
        )

    return (current - baseline) / baseline * 100.0
```

Example:

```python
print(percentage_change(900, 1_000))
# -10.0
```

A negative value means a decrease.

A positive value means an increase.

---

# 13. The Zero-Baseline Problem

This is an important edge case.

Suppose:

```text
baseline = 0
current = 0
```

The standard percentage formula divides by zero.

But operationally:

```text
0 → 0
```

may be perfectly normal.

Now:

```text
baseline = 0
current = 500
```

means something very different.

There is no meaningful ordinary percentage change from zero.

A practical policy can classify the cases explicitly:

```python
from typing import Literal


def compare_to_baseline(
    current: float,
    baseline: float,
) -> Literal[
    "unchanged_zero",
    "emerged_from_zero",
    "normal",
]:
    if baseline == 0 and current == 0:
        return "unchanged_zero"

    if baseline == 0 and current > 0:
        return "emerged_from_zero"

    return "normal"
```

For production systems, define what "zero baseline" means for the specific metric.

---

# 14. Volume by Partition

A total row count can hide a broken partition.

Example:

```text
total = 1,000,000
```

But:

```text
2026-10-01/hour=10 → 100,000
2026-10-01/hour=11 → 0
2026-10-01/hour=12 → 110,000
```

The total might look acceptable while one hour is missing.

Monitor at useful partition levels:

```text
date
hour
region
source
event_type
```

Choose dimensions based on actual business and pipeline behavior.

---

# 15. Volume by Time Window

Instead of daily volume alone, inspect:

```text
records per hour
records per 15 minutes
events per minute
```

This can detect:

- delayed ingestion;
- partial extraction;
- outages;
- traffic spikes;
- scheduler failures.

The right time window depends on the system.

A daily batch does not need second-level volume monitoring.

A real-time event stream may.

---

# 16. Volume by Business Dimension

Suppose total orders remain stable:

```text
1,000,000
```

But:

```text
APAC orders
historical = 200,000
current    = 20,000
```

A global row-count check may pass.

A business-dimension check reveals a major anomaly.

Possible dimensions include:

- region;
- product category;
- source;
- customer segment;
- event type;
- payment method.

Do not monitor every possible dimension blindly. High-cardinality grouping can become expensive and noisy.

---

# 17. Freshness from First Principles

Freshness asks:

> **How current is the data relative to when it was expected to be available?**

A timestamped event may pass through several times:

```text
event_time
    ↓
ingestion_time
    ↓
processing_time
    ↓
publication_time
```

These are not the same.

---

# 18. Event Time

**Event time** is when the underlying business event occurred.

Example:

```text
order placed:
2026-10-01 09:00 UTC
```

---

# 19. Ingestion Time

**Ingestion time** is when the data platform received the event.

Example:

```text
received:
2026-10-01 09:08 UTC
```

---

# 20. Processing Time

**Processing time** is when the pipeline processed the record.

Example:

```text
processed:
2026-10-01 09:10 UTC
```

---

# 21. Publication Time

**Publication time** is when the processed result became available to consumers.

Example:

```text
published:
2026-10-01 09:12 UTC
```

A single record can therefore have:

```text
event_time       = 09:00
ingestion_time   = 09:08
processing_time  = 09:10
publication_time = 09:12
```

These timestamps answer different operational questions.

---

# 22. Freshness Lag

A simple ingestion-lag calculation is:

```text
ingestion_time - event_time
```

Python:

```python
from datetime import datetime


def freshness_lag_seconds(
    event_time: datetime,
    ingestion_time: datetime,
) -> float:
    if event_time.tzinfo is None:
        raise ValueError("event_time must be timezone-aware")

    if ingestion_time.tzinfo is None:
        raise ValueError("ingestion_time must be timezone-aware")

    return (ingestion_time - event_time).total_seconds()
```

Example:

```python
from datetime import datetime, timezone

event_time = datetime(
    2026,
    10,
    1,
    9,
    0,
    tzinfo=timezone.utc,
)

ingestion_time = datetime(
    2026,
    10,
    1,
    9,
    8,
    tzinfo=timezone.utc,
)

print(freshness_lag_seconds(event_time, ingestion_time))
# 480.0
```

That is:

```text
8 minutes
```

Use timezone-aware timestamps in production examples.

UTC is a strong operational convention because it avoids many timezone ambiguities.

---

# 23. Freshness SLA and SLO

A freshness requirement might say:

```text
orders data must be available within 30 minutes
```

This is a service-level expectation.

A monitoring rule can calculate:

```text
observed freshness lag
```

and compare it with the policy.

For example:

```python
def freshness_within_limit(
    lag_seconds: float,
    max_lag_seconds: float,
) -> bool:
    return lag_seconds <= max_lag_seconds
```

Do not confuse a technical metric with the business requirement.

The business may care about:

```text
"data available to analysts by 09:30"
```

rather than only:

```text
"event-to-ingestion lag <= 30 minutes"
```

---

# 24. Freshness vs Completeness

This distinction is mandatory.

## Fresh but Incomplete

Data arrives quickly:

```text
09:05
```

but only half the expected records are present.

```text
fresh = good
complete = bad
```

## Complete but Stale

All expected records eventually arrive:

```text
14:00
```

when consumers needed them by:

```text
10:00
```

Then:

```text
fresh = bad
complete = good
```

## Fresh and Complete

Both requirements are satisfied.

### Matrix

| Freshness | Completeness | Interpretation |
|---|---|---|
| Good | Good | Healthy |
| Good | Bad | Timely but incomplete |
| Bad | Good | Complete but late |
| Bad | Bad | Severe quality problem |

---

# 25. Late-Arriving Data

Real systems often receive events after their expected time.

Reasons include:

- network delays;
- mobile devices reconnecting;
- source outages;
- retries;
- clock differences;
- offline processing;
- upstream batch behavior.

Do not automatically classify every late event as bad.

Instead define **acceptable lateness**.

For example:

```text
events may arrive up to 2 hours late
```

The policy depends on the dataset.

---

# 26. Watermarks

A watermark is a progress indicator used by event-time processing to reason about how far the system believes event time has advanced.

Conceptually:

```text
events:
09:01
09:03
09:04
09:02
```

The event at 09:02 is late relative to the processing order.

A watermark helps a streaming system decide when it has seen enough event-time progress to finalize a window.

Exact watermark semantics depend on the streaming engine.

The important beginner mental model is:

> A watermark is a statement about event-time progress, not simply "the latest message received."

---

# 27. Freshness by Partition

A dataset can have:

```text
partition=US
latest event = 10:00

partition=EU
latest event = 10:00

partition=APAC
latest event = 05:00
```

Global freshness may look acceptable if the newest record is 10:00.

Partition-level freshness reveals that APAC is stale.

For partitioned data, monitor the partitions that matter to consumers.

---

# 28. Distribution Checks

A distribution describes how values are spread.

Suppose:

```text
customer_age

22
23
24
24
25
26
27
28
29
30
```

Useful summary statistics include:

- minimum;
- maximum;
- mean;
- median;
- standard deviation;
- quantiles;
- frequency;
- null rate;
- cardinality.

A distribution check asks:

> Has the shape or composition of the data changed in a meaningful way?

---

# 29. Minimum and Maximum

For a numeric column:

```python
minimum = df["amount"].min()
maximum = df["amount"].max()
```

These can detect:

```text
negative amount
impossibly large amount
unit conversion bug
overflow
```

But min/max alone can be noisy.

One extreme outlier can change the maximum without changing the rest of the distribution.

---

# 30. Mean

The mean is:

```text
sum(values) / number_of_values
```

Python:

```python
mean_value = df["amount"].mean()
```

The mean is useful but sensitive to extreme values.

Example:

```text
10
11
12
13
14
1,000,000
```

The mean is heavily influenced by the final value.

---

# 31. Median

The median is the middle value after sorting.

For:

```text
10, 11, 12, 13, 14
```

the median is:

```text
12
```

The median is more robust to extreme values than the mean.

In pandas:

```python
median_value = df["amount"].median()
```

---

# 32. Percentiles

A percentile answers:

> What value is at or below approximately a given percentage of observations?

For example:

```python
p95 = df["amount"].quantile(0.95)
```

The p95 is useful when you care about the upper tail.

Other common statistics include:

```text
p50
p90
p95
p99
```

Percentiles are often more informative than averages for operational distributions.

---

# 33. Standard Deviation

Standard deviation describes the typical spread around the mean under the assumptions of the chosen statistic.

A simplified interpretation:

```text
small standard deviation
    → values clustered more tightly

large standard deviation
    → values more dispersed
```

Python:

```python
std_value = df["amount"].std()
```

Do not interpret standard deviation as a universal "error bar."

Its usefulness depends on the data distribution and the detection method.

---

# 34. Null Distribution

Null rate:

```text
null_rate =
    null_count / total_count
```

Pandas:

```python
null_rate = df["customer_email"].isna().mean()
```

Example:

```text
historical null rate = 1%
current null rate    = 27%
```

Potential causes include:

- broken upstream field;
- schema change;
- missing transformation;
- failed join;
- API response change.

The anomaly detector identifies the unusual behavior.

Investigation identifies the cause.

---

# 35. Categorical Distributions

Consider:

```text
payment_status

success
success
success
failed
success
pending
```

Pandas:

```python
distribution = (
    df["payment_status"]
    .value_counts(normalize=True)
)
```

Example historical distribution:

```text
success = 90%
failed  = 5%
pending = 5%
```

Current:

```text
success = 40%
failed  = 50%
pending = 10%
```

This is a large distribution change.

Possible causes include:

- application bug;
- payment provider issue;
- deployment issue;
- business change;
- legitimate event.

The monitoring system should not assume the root cause.

---

# 36. Cardinality

Cardinality is the number of distinct values.

```python
distinct_users = df["user_id"].nunique()
```

Sudden changes can reveal:

- corrupted identifiers;
- unexpected new categories;
- duplication;
- parsing problems;
- new source systems;
- semantic changes.

Example:

```text
historical distinct customer IDs = 950,000
current distinct customer IDs    = 20,000
```

This deserves investigation.

Cardinality is especially useful for identifiers and categorical columns.

---

# 37. Historical Baselines

A current value has little meaning without context.

Suppose:

```text
current row count = 1,000,000
```

If the normal baseline is:

```text
950,000
```

the value may be normal.

If the normal baseline is:

```text
2,000,000
```

the same one million rows may be a severe drop.

A **baseline** is a reference representation of expected behavior.

Possible baselines include:

- previous run;
- rolling mean;
- rolling median;
- rolling percentile;
- daily baseline;
- weekly baseline;
- hourly baseline;
- weekday/weekend baseline;
- seasonal baseline.

---

# 38. Previous-Run Baseline

The simplest baseline is:

```text
today vs yesterday
```

It is easy to implement.

But it can be misleading when:

- yesterday was abnormal;
- weekends differ from weekdays;
- holidays differ from ordinary days;
- business activity is seasonal.

---

# 39. Rolling Baseline

A rolling baseline uses a recent historical window.

Example:

```text
last 7 observations
```

Pandas:

```python
rolling_mean = (
    history["row_count"]
    .rolling(window=7)
    .mean()
)
```

The rolling window should contain enough data to represent expected behavior without becoming so old that it no longer reflects the current system.

---

# 40. Rolling Median

Median-based baselines can be more robust to outliers.

```python
rolling_median = (
    history["row_count"]
    .rolling(window=7)
    .median()
)
```

Suppose the history is:

```text
1,000,000
1,010,000
995,000
3,500,000   ← unusual
1,005,000
990,000
1,020,000
```

A mean baseline can be pulled upward by the abnormal spike.

A median baseline is less affected.

---

# 41. Daily and Weekly Baselines

A daily baseline can compare:

```text
Monday vs previous Mondays
Tuesday vs previous Tuesdays
```

rather than:

```text
Monday vs Sunday
```

This matters when weekday behavior differs significantly.

---

# 42. Hourly Seasonality

For an hourly stream:

```text
09:00
10:00
11:00
...
```

the normal volume at:

```text
02:00
```

may be very different from:

```text
14:00
```

A single global threshold can therefore generate unnecessary alerts.

Use time-aware baselines when the business exhibits stable time patterns.

---

# 43. Weekday vs Weekend Behavior

Example:

```text
Monday    1.2M
Tuesday   1.1M
Wednesday 1.15M
Saturday  0.50M
Sunday    0.45M
```

Comparing Sunday directly with Monday can create a false anomaly.

Seasonality-aware monitoring compares observations with appropriate peers.

---

# 44. Business Events and Seasonality

Seasonality can come from:

- weekends;
- holidays;
- month-end;
- quarter-end;
- product launches;
- marketing campaigns;
- billing cycles.

A statistical anomaly detector may correctly identify a large deviation while being operationally wrong about whether that deviation is problematic.

Context must be part of production monitoring.

---

# 45. Baseline Contamination

A baseline can become contaminated.

Suppose:

```text
normal:
1.0M
1.1M
1.0M

abnormal:
4.0M
4.2M
4.1M
```

If the abnormal period is included in the baseline window, future detection can become less sensitive.

Therefore investigate whether historical observations used for a baseline were themselves healthy.

A mature monitoring system may:

- exclude known incidents;
- exclude maintenance windows;
- exclude deployment windows;
- tag historical runs by quality status.

---

# 46. Threshold-Based Anomaly Detection

Start with simple methods.

### Fixed threshold

```text
row_count < 500,000
```

### Percentage threshold

```text
current < 80% of baseline
```

### Relative deviation

```text
abs(current - baseline) / baseline
```

### Moving average

Compare current value with a recent rolling mean.

### Rolling statistics

Use historical mean, median, standard deviation, quantiles, or robust measures.

Thresholds are understandable and operationally easy.

They are also easy to misuse.

---

# 47. Why Thresholds Are Not Universal

A rule such as:

```python
if current_rows < baseline_rows * 0.8:
    alert()
```

may work for one dataset and fail badly for another.

Why?

Because:

- one dataset may have predictable volume;
- another may be highly seasonal;
- one may tolerate a 20% deviation;
- another may treat a 5% deviation as critical;
- business impact differs;
- source behavior differs.

Thresholds should be calibrated to:

- historical behavior;
- business impact;
- dataset criticality;
- consumer requirements;
- known seasonality.

---

# 48. Moving Average

A moving average smooths recent observations.

Example:

```python
history["moving_average"] = (
    history["row_count"]
    .rolling(window=7)
    .mean()
)
```

Then compare:

```text
current
vs
moving_average
```

Moving averages are useful when:

- the signal is noisy;
- recent history matters;
- there is no strong seasonal pattern.

They can lag behind sudden legitimate changes.

---

# 49. Z-Score

A z-score expresses how far an observation is from a mean in standard-deviation units.

Formula:

```text
z = (x - μ) / σ
```

where:

- `x` = observed value;
- `μ` = mean;
- `σ` = standard deviation.

Suppose:

```text
mean = 100
standard deviation = 10
current = 130
```

Then:

```text
z = (130 - 100) / 10
  = 3
```

The observation is three standard deviations above the mean.

The important intuition:

```text
z > 0
    → above the mean

z < 0
    → below the mean

large |z|
    → far from the historical mean
```

---

# 50. Z-Score in Python

```python
def z_score(
    value: float,
    mean: float,
    standard_deviation: float,
) -> float:
    if standard_deviation <= 0:
        raise ValueError(
            "standard deviation must be positive"
        )

    return (
        (value - mean)
        / standard_deviation
    )
```

Example:

```python
z = z_score(
    value=130,
    mean=100,
    standard_deviation=10,
)

print(z)
# 3.0
```

Do not present a particular z-score cutoff as a universal production rule.

The appropriate policy depends on the data and consequences.

---

# 51. Why Mean and Standard Deviation Can Fail

Suppose historical values are:

```text
100
101
99
102
98
100
10,000
```

The outlier can distort:

```text
mean
standard deviation
```

making ordinary values appear less unusual.

This is why robust methods can be useful.

---

# 52. Median Absolute Deviation (MAD)

MAD is based on the median rather than the mean.

First find the median:

```text
m = median(x)
```

Then compute absolute deviations:

```text
|x - m|
```

and take their median.

The core intuition:

> Measure typical distance from the median without allowing one extreme observation to dominate the reference as easily as mean/std methods can.

MAD can be useful for noisy distributions with outliers.

---

# 53. Interquartile Range (IQR)

IQR is:

```text
IQR = Q3 - Q1
```

where:

- `Q1` = 25th percentile;
- `Q3` = 75th percentile.

A common exploratory rule flags observations beyond:

```text
Q1 - 1.5 × IQR
```

or:

```text
Q3 + 1.5 × IQR
```

The multiplier is a conventional statistical heuristic, not a universal production policy.

Python:

```python
def iqr_bounds(values):
    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return lower, upper
```

---

# 54. IQR Example

Suppose:

```text
10, 11, 12, 13, 14, 15, 100
```

The value `100` may be far outside the central distribution.

IQR-based detection is less sensitive to extreme values than mean/std-based detection.

But it is still only a statistical signal.

A legitimate promotion could create exactly such a spike.

---

# 55. Percentile-Based Detection

Instead of modeling a distribution parametrically, use historical percentiles.

For example:

```python
p05 = history["row_count"].quantile(0.05)
p95 = history["row_count"].quantile(0.95)
```

Then:

```text
current < p05
or
current > p95
```

may be flagged.

This approach is intuitive and often useful when the historical distribution is not well represented by a simple mean/std model.

---

# 56. Point Anomaly vs Distribution Shift

A **point anomaly** is an unusual observation.

Example:

```text
today's row count = 10M
normal = 1M
```

A **distribution shift** occurs when the population itself changes.

Example:

```text
historical:
amount median = 50
amount p95 = 200

current:
amount median = 120
amount p95 = 600
```

Individual values may all be valid.

The population has nevertheless changed.

This distinction matters.

---

# 57. Statistical Anomaly vs Business Anomaly

A statistical anomaly means:

> The observation is unusual relative to the statistical reference.

A business anomaly means:

> The observation represents unexpected or problematic business behavior.

These are not identical.

A statistically unusual event may be legitimate:

- product launch;
- marketing campaign;
- holiday;
- pricing change;
- new customer segment;
- source migration.

Therefore:

```text
statistical detector
    ≠
root-cause detector
```

A detector should identify unusual behavior and provide context for investigation.

---

# 58. Population Stability Index (PSI)

PSI compares the distribution of a population with a reference distribution.

Conceptually:

```text
reference population
        vs
current population
```

The intuition is:

> How much did the population's distribution move across defined bins?

A conceptual formula is:

```text
PSI = Σ
      (current_i - reference_i)
      ×
      ln(current_i / reference_i)
```

where `i` represents a bin.

The exact implementation requires careful binning and handling of zero proportions.

PSI is often used in population monitoring and drift analysis.

It should not be treated as a universal anomaly score with one globally correct cutoff.

---

# 59. KL Divergence

KL divergence compares probability distributions.

Conceptually:

```text
KL(P || Q)
```

asks how different distribution `Q` is from a reference `P` under the chosen direction.

For discrete distributions:

```text
KL(P || Q)
=
Σ P(x) log(P(x) / Q(x))
```

Important properties:

- it is directional;
- it is not generally symmetric;
- it can become problematic when probabilities are zero;
- interpretation depends on how the distributions were constructed.

Use it when you have a meaningful probability representation and understand the numerical handling.

---

# 60. Jensen-Shannon Divergence

Jensen-Shannon divergence provides a more symmetric comparison between two distributions.

Conceptually:

```text
P
Q
↓
shared midpoint distribution
↓
compare P and Q to midpoint
```

It is often easier to interpret symmetrically than KL divergence.

Again, the result is a statistical signal, not an automatic business conclusion.

---

# 61. Kolmogorov-Smirnov Test Concepts

The two-sample KS test compares two empirical distributions.

Intuition:

> How far apart are the cumulative distribution functions of the two samples?

It is useful for detecting changes in continuous numeric distributions.

Important limitations include:

- sample size affects statistical significance;
- repeated monitoring creates multiple-testing considerations;
- practical significance and statistical significance are not identical;
- categorical data requires different treatment;
- business context still matters.

---

# 62. Choosing a Distribution-Shift Method

| Method | Useful For | Main Consideration |
|---|---|---|
| Percentage/range checks | Simple operational rules | Easy but limited |
| Percentiles | Non-parametric operational monitoring | Requires representative history |
| Z-score | Roughly stable numeric signals | Sensitive to outliers |
| IQR | Robust numeric screening | Heuristic |
| MAD | Robust anomaly detection | Requires enough useful history |
| PSI | Binned population comparison | Depends on binning |
| KL divergence | Probability distributions | Directional and zero-sensitive |
| Jensen-Shannon | Symmetric distribution comparison | Requires probability distributions |
| KS test | Numeric empirical distributions | Statistical significance vs practical significance |

Tool selection should match the data and operational objective.

---

# 63. Anomaly Detection by Data Type

## Numeric

Monitor:

- min;
- max;
- mean;
- median;
- standard deviation;
- quantiles;
- distribution shape.

## Categorical

Monitor:

- category frequencies;
- new categories;
- category disappearance;
- distribution proportions.

## Boolean

Monitor:

```text
true_rate
false_rate
null_rate
```

## Timestamp

Monitor:

- freshness;
- lag;
- event-time distribution;
- future timestamps;
- stale partitions.

## Nullability

Monitor:

```text
null_count
null_rate
```

## Cardinality

Monitor:

```text
distinct_count
```

## Rates and Ratios

Examples:

```text
conversion_rate
error_rate
null_rate
success_rate
```

Rates are especially useful because absolute counts can grow while the underlying behavior remains stable.

---

# 64. Real-World Failure Modes

## Zero-Row Load

```text
expected = 1,000,000
actual = 0
```

Possible causes:

- upstream outage;
- scheduler failure;
- empty extraction;
- filter bug.

Potential action:

```text
critical / block publication
```

depending on policy.

---

## Sudden Volume Drop

```text
baseline = 1,000,000
actual = 420,000
```

Investigate:

- extraction;
- partitions;
- filters;
- pagination;
- source availability.

---

## Sudden Volume Spike

```text
baseline = 1,000,000
actual = 4,000,000
```

Possible causes:

- duplicate load;
- pagination loop;
- replay;
- legitimate demand;
- upstream filter removal.

---

## Delayed Pipeline

Volume may eventually be correct, but freshness is violated.

```text
expected publication = 10:00
actual publication = 14:00
```

---

## Stale Data

The pipeline may technically succeed but continue exposing yesterday's partition.

Monitor:

```text
latest expected partition
vs
latest available partition
```

---

## Missing Partition

Example:

```text
2026-10-01
2026-10-02
2026-10-04
```

Missing:

```text
2026-10-03
```

A global row count may not immediately reveal this.

---

## Duplicate Load

A rerun may create:

```text
2 × expected volume
```

or duplicate records without doubling total rows if downstream deduplication occurs.

---

## Broken Upstream Filter

A source change can unexpectedly remove or include a population.

Volume and categorical distribution can both move.

---

## Partial Extraction

API pagination may stop after page 25 instead of page 100.

The pipeline can still report success.

Volume monitoring is a useful independent signal.

---

## Upstream Business Change

A new product may legitimately increase events by 400%.

The anomaly is real statistically.

The system still needs business context before blocking production.

---

## Seasonal Change

Weekend behavior may differ substantially from weekdays.

A seasonality-aware baseline prevents unnecessary alerts.

---

## Legitimate Large Spike

A major launch may create an expected spike.

A monitoring system should support:

- annotations;
- suppression windows;
- known-event metadata;
- maintenance windows.

---

# 65. False Positives

A false positive occurs when the system reports a problem but the data is actually acceptable.

Example:

```text
Saturday volume = 500K
weekday baseline = 1M
```

A naive rule:

```text
volume < 800K
```

fires an alert.

But Saturday may normally have 500K records.

The detector is wrong because its reference model is wrong.

---

# 66. False Negatives

A false negative occurs when the system fails to detect a real problem.

Example:

```text
expected volume = 1M
actual volume = 600K
```

but a wide threshold accepts anything above:

```text
500K
```

The pipeline may continue despite a meaningful failure.

False negatives are dangerous because they create false confidence.

---

# 67. Alert Fatigue

If engineers receive:

```text
500 alerts/day
```

for harmless fluctuations, they may begin ignoring alerts.

Alert fatigue reduces the operational value of monitoring.

Prefer:

```text
aggregate related failures
+
severity
+
thresholds
+
rate changes
+
business context
```

rather than one alert for every small deviation.

---

# 68. Suppression and Maintenance Windows

Known events can create expected anomalies.

Examples:

```text
planned migration
maintenance
marketing launch
holiday
schema transition
```

Monitoring systems can support controlled suppression windows.

A suppression policy should be:

- explicit;
- time-bounded;
- owned;
- auditable.

Do not permanently disable checks to eliminate noisy alerts.

---

# 69. Severity and Action Policies

A useful conceptual model:

```text
NORMAL
WARNING
CRITICAL
BLOCK
```

Example only:

```text
volume -5%   → informational
volume -15%  → warning
volume -40%  → critical
volume = 0   → potentially blocking
```

These values are examples, not universal recommendations.

The policy must be calibrated to the dataset.

Possible actions:

- pass;
- warn and continue;
- alert only;
- stop publication;
- fail pipeline;
- quarantine affected output;
- open a circuit breaker.

---

# 70. Quality Gate

A quality gate converts metrics into an operational decision.

```text
extract
  ↓
load
  ↓
compute quality metrics
  ↓
volume check
  ↓
freshness check
  ↓
distribution checks
  ↓
severity classification
  ↓
publish / warn / block
```

The gate should have explicit policies.

---

# 71. Python: A Simple Volume Monitor

```python
from dataclasses import dataclass


@dataclass
class VolumeResult:
    current: int
    baseline: int
    deviation_pct: float
    status: str


def check_volume(
    current: int,
    baseline: int,
    warning_ratio: float,
    critical_ratio: float,
) -> VolumeResult:
    if baseline <= 0:
        raise ValueError("baseline must be positive")

    ratio = current / baseline
    deviation_pct = (ratio - 1.0) * 100.0

    if ratio <= critical_ratio:
        status = "CRITICAL"
    elif ratio <= warning_ratio:
        status = "WARNING"
    else:
        status = "NORMAL"

    return VolumeResult(
        current=current,
        baseline=baseline,
        deviation_pct=deviation_pct,
        status=status,
    )
```

Example:

```python
result = check_volume(
    current=420_000,
    baseline=1_000_000,
    warning_ratio=0.85,
    critical_ratio=0.60,
)

print(result)
```

The thresholds are configuration, not universal truth.

---

# 72. Python: Freshness Check

```python
from datetime import datetime


def calculate_freshness_minutes(
    event_time: datetime,
    reference_time: datetime,
) -> float:
    if event_time.tzinfo is None:
        raise ValueError("event_time must be timezone-aware")

    if reference_time.tzinfo is None:
        raise ValueError("reference_time must be timezone-aware")

    return (
        reference_time - event_time
    ).total_seconds() / 60.0
```

Example:

```python
from datetime import datetime, timezone

event_time = datetime(
    2026, 10, 1, 9, 0,
    tzinfo=timezone.utc,
)

ingestion_time = datetime(
    2026, 10, 1, 9, 20,
    tzinfo=timezone.utc,
)

lag = calculate_freshness_minutes(
    event_time,
    ingestion_time,
)

print(lag)
# 20.0
```

---

# 73. Python: Null Rate

```python
def null_rate(
    null_count: int,
    total_count: int,
) -> float:
    if total_count <= 0:
        raise ValueError("total_count must be positive")

    return null_count / total_count
```

Example:

```python
rate = null_rate(
    null_count=27,
    total_count=100,
)

print(rate)
# 0.27
```

---

# 74. Python: Distinct Count

```python
def distinct_count(values: list[object]) -> int:
    return len(set(values))
```

Example:

```python
values = [
    "customer-1",
    "customer-1",
    "customer-2",
    "customer-3",
]

print(distinct_count(values))
# 3
```

For very large datasets, exact distinct counting can be expensive. Approximate methods may be appropriate depending on the platform.

---

# 75. Python: Distribution Summary

```python
from statistics import mean, median


def summarize_numeric(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("values must not be empty")

    ordered = sorted(values)

    return {
        "min": min(values),
        "max": max(values),
        "mean": mean(values),
        "median": median(values),
        "p95": ordered[
            min(
                len(ordered) - 1,
                int(0.95 * len(ordered)),
            )
        ],
    }
```

For serious statistical work, prefer well-tested numerical libraries rather than hand-implementing every statistic.

The educational purpose here is to expose the concepts.

---

# 76. Python: IQR

```python
def iqr_bounds(values: list[float]) -> tuple[float, float]:
    if not values:
        raise ValueError("values must not be empty")

    ordered = sorted(values)

    midpoint = len(ordered) // 2

    if len(ordered) % 2 == 0:
        lower_half = ordered[:midpoint]
        upper_half = ordered[midpoint:]
    else:
        lower_half = ordered[:midpoint]
        upper_half = ordered[midpoint + 1:]

    def median(items: list[float]) -> float:
        middle = len(items) // 2
        if len(items) % 2 == 0:
            return (items[middle - 1] + items[middle]) / 2
        return items[middle]

    q1 = median(lower_half)
    q3 = median(upper_half)
    iqr = q3 - q1

    return (
        q1 - 1.5 * iqr,
        q3 + 1.5 * iqr,
    )
```

For production code, using a tested statistical library is usually preferable.

---

# 77. Python: Categorical Distribution

```python
from collections import Counter


def categorical_distribution(
    values: list[str],
) -> dict[str, float]:
    if not values:
        raise ValueError("values must not be empty")

    counts = Counter(values)
    total = len(values)

    return {
        key: count / total
        for key, count in counts.items()
    }
```

Example:

```python
values = [
    "success",
    "success",
    "failed",
    "success",
]

print(categorical_distribution(values))
```

---

# 78. Python: Rolling Baseline with pandas

```python
import pandas as pd


history = pd.DataFrame(
    {
        "date": pd.date_range(
            "2026-09-20",
            periods=10,
            freq="D",
        ),
        "row_count": [
            990_000,
            1_010_000,
            995_000,
            1_005_000,
            1_000_000,
            1_020_000,
            980_000,
            1_015_000,
            1_005_000,
            600_000,
        ],
    }
)

history["rolling_mean"] = (
    history["row_count"]
    .rolling(window=7)
    .mean()
)
```

The last observation is unusually low relative to recent history.

But whether it should trigger a production incident depends on the policy and context.

---

# 79. Python: Rolling Median

```python
history["rolling_median"] = (
    history["row_count"]
    .rolling(window=7)
    .median()
)
```

Compare mean and median when historical observations contain large spikes.

A median baseline may be more robust.

---

# 80. Python: Z-Score with pandas

```python
history["mean"] = (
    history["row_count"]
    .rolling(window=7)
    .mean()
)

history["std"] = (
    history["row_count"]
    .rolling(window=7)
    .std()
)

history["z_score"] = (
    history["row_count"]
    - history["mean"]
) / history["std"]
```

Important production considerations:

- insufficient historical observations;
- zero standard deviation;
- contaminated history;
- seasonality;
- outliers;
- changing business behavior.

---

# 81. Python: Anomaly Classification

A simple educational classifier:

```python
def classify_anomaly(
    deviation_pct: float,
    warning_pct: float,
    critical_pct: float,
) -> str:
    magnitude = abs(deviation_pct)

    if magnitude >= critical_pct:
        return "CRITICAL"

    if magnitude >= warning_pct:
        return "WARNING"

    return "NORMAL"
```

Again, the threshold values are policy configuration.

---

# 82. pandas: Core Metrics

Given:

```python
import pandas as pd

df = pd.DataFrame(
    {
        "order_id": [1, 2, 3, 4, 5],
        "amount": [10, 20, 30, 40, 50],
        "currency": ["USD", "USD", "EUR", "USD", "EUR"],
        "customer_id": ["A", "B", "A", "C", "D"],
    }
)
```

Basic volume:

```python
row_count = df.shape[0]
```

Null rate:

```python
null_rate = df["amount"].isna().mean()
```

Distinct count:

```python
customer_count = df["customer_id"].nunique()
```

Quantiles:

```python
p95 = df["amount"].quantile(0.95)
```

Categorical distribution:

```python
currency_distribution = (
    df["currency"]
    .value_counts(normalize=True)
)
```

Grouped volume:

```python
orders_by_currency = (
    df.groupby("currency")
    .size()
)
```

---

# 83. pandas: Historical Comparison

Suppose:

```python
history = pd.DataFrame(
    {
        "date": pd.date_range(
            "2026-09-20",
            periods=10,
            freq="D",
        ),
        "row_count": [
            1_000_000,
            1_020_000,
            990_000,
            1_010_000,
            995_000,
            1_005_000,
            1_015_000,
            1_000_000,
            980_000,
            420_000,
        ],
    }
)
```

You can calculate:

```python
history["baseline"] = (
    history["row_count"]
    .shift(1)
    .rolling(window=7)
    .median()
)
```

The exact baseline construction should match the business cadence.

---

# 84. Time-Series Quality Metrics

A historical quality-metrics table might contain:

```text
date
row_count
null_rate
freshness_minutes
mean_value
p95_value
distinct_users
```

Example:

```python
metrics = pd.DataFrame(
    {
        "date": pd.date_range(
            "2026-09-20",
            periods=5,
            freq="D",
        ),
        "row_count": [
            1_000_000,
            1_020_000,
            980_000,
            1_010_000,
            420_000,
        ],
        "null_rate": [
            0.01,
            0.012,
            0.011,
            0.010,
            0.30,
        ],
        "freshness_minutes": [
            12,
            10,
            11,
            13,
            240,
        ],
    }
)
```

Now multiple independent signals indicate trouble:

```text
volume ↓
null rate ↑
freshness lag ↑
```

This is stronger evidence than any single metric.

---

# 85. Multi-Signal Detection

A mature system should avoid treating every metric independently.

Example:

```text
volume drop
+
freshness delay
+
null-rate increase
```

may indicate an upstream extraction or transformation failure.

Whereas:

```text
volume spike
+
normal freshness
+
normal null rate
```

may be consistent with a legitimate traffic event.

Multi-signal evidence can reduce noisy decisions.

---

# 86. Production Quality Event

A quality check should produce structured output.

Example:

```json
{
  "dataset": "orders",
  "run_id": "2026-10-01T12:00:00Z",
  "check": "volume",
  "metric": "row_count",
  "observed": 420000,
  "baseline": 1000000,
  "status": "critical",
  "severity": "high"
}
```

This structure can support:

- dashboards;
- alerting;
- incident investigation;
- auditability;
- historical analysis.

A production event can include additional fields:

```text
dataset
run_id
check
metric
observed
baseline
deviation
status
severity
timestamp
owner
policy_version
```

---

# 87. Production Monitoring Architecture

A conceptual architecture:

```text
Data Source
    ↓
Ingestion
    ↓
Transformation
    ↓
Quality Metrics
    ↓
Baseline Store
    ↓
Anomaly Detection
    ↓
Quality Decision
    ↓
Metrics / Logs
    ↓
Alerting
    ↓
Dashboard
    ↓
Engineer Investigation
```

Supporting metadata may include:

```text
run metadata
baseline history
quality-event history
alert metadata
ownership metadata
incident references
```

---

# 88. Baseline Store

A baseline store preserves historical quality metrics.

Possible fields:

```text
dataset
metric
timestamp
observed_value
baseline_value
baseline_method
seasonality_key
quality_status
```

This makes the monitoring system itself auditable.

You can answer:

```text
What did the monitor believe was normal last Tuesday?
```

That matters during incident investigation.

---

# 89. Alert Metadata

An alert should contain enough context to act.

Example:

```text
dataset: orders
metric: row_count
current: 420,000
baseline: 1,000,000
deviation: -58%
severity: critical
run_id: run-2026-10-01-001
owner: orders-data-product
```

"Anomaly detected" is not sufficient operational information.

---

# 90. Batch vs Streaming

## Batch Monitoring

Typical metrics:

```text
daily volume
daily freshness
daily distribution
```

A daily orders dataset may be evaluated after the batch finishes.

## Streaming Monitoring

Typical metrics:

```text
events/minute
events/second
rolling error rate
watermark progress
event-time lag
window volume
```

The monitoring model must account for:

- windows;
- state;
- late events;
- watermarks;
- rolling metrics.

---

# 91. Streaming Windows

A streaming monitor might evaluate:

```text
last 5 minutes
```

or:

```text
last 1 hour
```

For example:

```text
events in current 5-minute window
vs
historical 5-minute baseline
```

The window definition becomes part of the metric.

A spike at 10:02 may look normal over a full day but extreme within a five-minute operational window.

---

# 92. Late Events in Streaming

Suppose an event has:

```text
event_time = 09:00
```

but arrives:

```text
10:30
```

If monitoring uses only ingestion time, it may appear as a new event.

If monitoring uses event time, it belongs to the 09:00 period.

Production streaming monitoring therefore needs an explicit time model.

---

# 93. Performance: Full Dataset Scans

Monitoring itself costs resources.

A naive implementation may scan a multi-terabyte dataset repeatedly for every metric.

That can become expensive.

Potential strategies:

- partition scans;
- sampling;
- incremental metrics;
- precomputed statistics;
- metadata-based checks;
- approximate distinct counts;
- partition pruning.

---

# 94. Sampling

Instead of scanning every record, sample a subset.

Advantages:

- cheaper;
- faster;
- useful for exploratory distribution monitoring.

Risks:

- rare events may be missed;
- small populations may be poorly represented;
- sampling bias can distort conclusions.

Sampling is a trade-off, not an automatic replacement for full checks.

---

# 95. Approximate Statistics

For large datasets, exact statistics can be expensive.

Approximate methods can estimate:

- distinct counts;
- quantiles;
- distribution characteristics.

The right approximation depends on the storage engine and workload.

Do not claim a specific algorithm provides a universal accuracy guarantee without validating the implementation.

---

# 96. Partition-Level Checks

Instead of scanning an entire dataset:

```text
dataset
 ├── partition A
 ├── partition B
 ├── partition C
```

compute metrics per partition.

This can enable:

- parallel processing;
- cheaper investigation;
- localized anomaly detection.

Partition-level checks are particularly useful when the dataset is naturally partitioned by time or business dimension.

---

# 97. Incremental Metrics

If yesterday's metrics are already known, do not necessarily recompute everything.

Store:

```text
historical metric
```

and update:

```text
current metric
```

incrementally where the data platform supports reliable incremental computation.

This reduces monitoring overhead.

---

# 98. Cost vs Detection Accuracy

A fundamental production trade-off:

```text
more accurate check
        vs
more expensive check
```

Examples:

### Cheap

```text
partition row count
latest timestamp
file metadata
```

### More expensive

```text
full numeric distribution
exact distinct count
full pairwise distribution comparison
```

A practical monitoring architecture uses multiple layers.

---

# 99. Tool Integration

This topic connects to:

- Python;
- pandas;
- Pandera;
- Great Expectations;
- Soda;
- SQL;
- orchestration systems;
- observability systems.

The question is:

> **Where should the check live?**

---

# 100. Python-Based Checks

Python is useful when:

- custom logic is required;
- metrics come from APIs;
- statistical calculations are needed;
- a pipeline already has a Python validation layer.

Advantages:

- flexible;
- testable;
- expressive.

Trade-offs:

- custom operational infrastructure may be required;
- consistency across many pipelines can become harder.

---

# 101. SQL-Based Checks

SQL is useful when the data is already in a warehouse/database.

Examples:

```sql
SELECT COUNT(*)
FROM orders;
```

Null rate:

```sql
SELECT
    AVG(
        CASE
            WHEN customer_id IS NULL THEN 1.0
            ELSE 0.0
        END
    ) AS null_rate
FROM orders;
```

Grouped volume:

```sql
SELECT
    region,
    COUNT(*) AS row_count
FROM orders
GROUP BY region;
```

SQL is often close to the data, reducing unnecessary extraction.

---

# 102. Pandera

Pandera is useful for DataFrame-level validation.

For this topic, use it when anomaly-related checks need to coexist with DataFrame validation.

The distinction is:

```text
schema/rule validation
    +
volume/distribution/anomaly monitoring
```

A DataFrame can satisfy a schema while its statistical behavior changes.

---

# 103. Great Expectations and Soda

Great Expectations and Soda can express quality checks and produce structured quality results.

A useful architecture is:

```text
check
 ↓
quality result
 ↓
policy
 ↓
warn / alert / block / continue
```

Do not treat the tool's failed check as an automatic root-cause diagnosis.

---

# 104. Orchestrator-Level Checks

An orchestration layer can evaluate:

```text
upstream completed?
volume acceptable?
freshness acceptable?
quality gate passed?
```

This is useful for deciding whether downstream tasks should run.

The exact implementation depends on the orchestration platform.

---

# 105. Choosing the Right Layer

| Layer | Good Fit |
|---|---|
| Python | Custom statistical logic |
| SQL | Warehouse-native metrics |
| pandas | DataFrame analysis |
| Pandera | DataFrame schema/constraint validation |
| Great Expectations | Declarative validation/reporting |
| Soda | Declarative data-quality checks |
| Orchestrator | Pipeline gating and dependency decisions |
| Observability system | Metrics, alerts, dashboards |

A production system can use multiple layers.

---

# 106. Defect Injection Lab

A good monitoring system must be tested with synthetic failures.

## Defect 1 — Volume Drops by 50%

```text
baseline = 1,000,000
current = 500,000
```

Expected:

```text
large negative deviation
```

---

## Defect 2 — Volume Increases by 300%

```text
baseline = 1,000,000
current = 4,000,000
```

Expected:

```text
large positive deviation
```

---

## Defect 3 — Freshness Lag

```text
normal = 10 minutes
current = 4 hours
```

Expected:

```text
freshness anomaly
```

---

## Defect 4 — Null Rate

```text
historical = 1%
current = 30%
```

Expected:

```text
null-rate anomaly
```

---

## Defect 5 — Categorical Distribution

Historical:

```text
success = 90%
failed  = 5%
pending = 5%
```

Current:

```text
success = 40%
failed  = 50%
pending = 10%
```

Expected:

```text
distribution anomaly
```

---

## Defect 6 — Cardinality

```text
historical distinct users = 950,000
current distinct users    = 20,000
```

Expected:

```text
cardinality anomaly
```

---

## Defect 7 — Legitimate Seasonal Change

```text
weekday = 1.2M
weekend = 500K
```

A seasonality-aware monitor should avoid treating the weekend pattern as an unexpected failure.

---

# 107. Debugging Workflow

When an anomaly fires:

```text
1. Observe anomaly
2. Confirm metric calculation
3. Compare with baseline
4. Check seasonality
5. Inspect upstream source
6. Inspect recent code/config changes
7. Inspect partitions
8. Inspect timestamps
9. Compare source vs destination
10. Determine root cause
11. Decide recovery
12. Document incident
```

---

# 108. Step 1 — Confirm the Metric

Before debugging the pipeline, confirm the monitor itself is correct.

Questions:

- Did the query include the correct partition?
- Is the timezone correct?
- Is the baseline correct?
- Was a duplicate counted?
- Did the query accidentally exclude rows?
- Is the denominator correct?

A broken monitoring query can create a false incident.

---

# 109. Step 2 — Check Historical Context

Compare:

```text
current
previous run
rolling baseline
same weekday
same hour
known events
```

A metric that looks abnormal against yesterday may be normal against the same weekday.

---

# 110. Step 3 — Inspect Upstream

If volume dropped:

```text
source count
→ extraction count
→ landing count
→ transformed count
→ published count
```

Find where the drop occurred.

This localizes the failure.

---

# 111. Step 4 — Inspect Recent Changes

Look for:

- deployment;
- configuration change;
- query change;
- schema change;
- source API change;
- feature release;
- filter modification.

Many data anomalies are change-related.

---

# 112. Step 5 — Inspect Partitions and Timestamps

Look for:

```text
missing partition
stale timestamp
future timestamp
timezone mismatch
late events
```

A global metric can hide a localized failure.

---

# 113. Step 6 — Determine Root Cause

Possible root causes:

```text
technical failure
data-quality failure
source-system change
business event
monitoring defect
```

Do not automatically classify every anomaly as an upstream defect.

---

# 114. Step 7 — Recover Safely

Recovery depends on the cause.

Possible actions:

- rerun extraction;
- backfill missing partition;
- replay events;
- repair transformation;
- update monitoring configuration;
- document a legitimate business event;
- adjust a baseline after evidence supports the change.

Recovery should be auditable.

---

# 115. Production Design Patterns

## Quality Gate

```text
metrics
 ↓
checks
 ↓
decision
 ↓
publish / block
```

## Soft Gate

```text
anomaly
 ↓
warning
 ↓
continue
```

## Hard Gate

```text
anomaly
 ↓
block publication
```

## Circuit Breaker

```text
repeated/systemic anomaly
 ↓
stop unsafe processing
 ↓
investigate
 ↓
recover
```

## Baseline Registry

Store:

```text
dataset
metric
baseline method
window
seasonality
thresholds
version
```

## Quality Event

Emit structured quality results for downstream monitoring.

## Alert Deduplication

Aggregate repeated alerts for the same underlying issue.

---

# 116. Testing Strategy

Anomaly detection requires more than happy-path tests.

Test:

- normal data;
- zero rows;
- very low volume;
- very high volume;
- stale data;
- fresh data;
- high null rate;
- low null rate;
- unexpected cardinality;
- distribution shift;
- legitimate seasonality;
- zero baseline;
- missing baseline;
- insufficient history;
- extreme outliers.

---

# 117. Example pytest-Style Tests

```python
def test_percentage_change_for_drop():
    assert percentage_change(900, 1_000) == -10.0
```

Zero baseline:

```python
import pytest


def test_percentage_change_rejects_zero_baseline():
    with pytest.raises(ValueError):
        percentage_change(10, 0)
```

Freshness:

```python
from datetime import datetime, timezone


def test_freshness_lag():
    event_time = datetime(
        2026, 10, 1, 9, 0,
        tzinfo=timezone.utc,
    )

    ingestion_time = datetime(
        2026, 10, 1, 9, 15,
        tzinfo=timezone.utc,
    )

    assert (
        freshness_lag_seconds(
            event_time,
            ingestion_time,
        )
        == 900
    )
```

The purpose is to test the monitoring logic itself.

---

# 118. Regression Tests for False Positives

Create a known seasonal dataset.

Example:

```text
Monday    1.2M
Tuesday   1.1M
Wednesday 1.15M
Thursday  1.1M
Friday    1.0M
Saturday  0.5M
Sunday    0.45M
```

A seasonality-aware monitor should not fail merely because Sunday is much lower than Monday.

This test protects against future monitoring changes that accidentally reintroduce noisy alerts.

---

# 119. Insufficient Historical Data

A baseline should not pretend to be reliable when history is missing.

Example:

```text
new dataset
history = 1 day
```

A seven-day baseline cannot be computed meaningfully.

Possible policy:

```text
status = INSUFFICIENT_HISTORY
```

rather than:

```text
status = NORMAL
```

This distinction prevents false confidence.

---

# 120. Missing Baseline

If the baseline store is unavailable, do not silently treat:

```text
baseline = 0
```

as the correct baseline.

Possible states include:

```text
BASELINE_UNAVAILABLE
INSUFFICIENT_HISTORY
CHECK_SKIPPED
```

The action should be explicit.

---

# 121. Mini-Project: Production Data Quality Anomaly Monitor

## Objective

Build a synthetic monitoring system that calculates:

- row count;
- expected row count;
- volume deviation;
- freshness lag;
- null rate;
- distinct count;
- mean;
- median;
- p95;
- categorical distribution;
- historical baseline;
- anomaly status;
- severity.

The project should produce structured quality results.

---

# 122. Mini-Project Dataset

Use synthetic order data:

```python
import pandas as pd


orders = pd.DataFrame(
    {
        "order_id": range(1, 11),
        "amount": [
            25.0,
            40.0,
            31.0,
            29.0,
            100.0,
            42.0,
            55.0,
            38.0,
            44.0,
            60.0,
        ],
        "currency": [
            "USD",
            "USD",
            "USD",
            "EUR",
            "USD",
            "USD",
            "EUR",
            "USD",
            "USD",
            "USD",
        ],
        "customer_id": [
            "C1",
            "C2",
            "C1",
            "C3",
            "C4",
            "C5",
            "C6",
            "C7",
            "C8",
            "C9",
        ],
    }
)
```

This is intentionally small so the learner can inspect it manually.

---

# 123. Mini-Project Metrics

```python
def calculate_metrics(
    df: pd.DataFrame,
) -> dict[str, float]:
    if df.empty:
        return {
            "row_count": 0,
            "null_rate_amount": 0.0,
            "distinct_customers": 0,
        }

    return {
        "row_count": float(len(df)),
        "null_rate_amount": float(
            df["amount"].isna().mean()
        ),
        "distinct_customers": float(
            df["customer_id"].nunique()
        ),
        "mean_amount": float(
            df["amount"].mean()
        ),
        "median_amount": float(
            df["amount"].median()
        ),
        "p95_amount": float(
            df["amount"].quantile(0.95)
        ),
    }
```

A production implementation would normally define metric types more precisely rather than converting every metric to `float`.

---

# 124. Mini-Project Baseline

Create synthetic historical metrics:

```python
historical_metrics = pd.DataFrame(
    {
        "date": pd.date_range(
            "2026-09-20",
            periods=10,
            freq="D",
        ),
        "row_count": [
            1_000,
            1_020,
            990,
            1_010,
            1_005,
            995,
            1_015,
            1_008,
            1_012,
            1_000,
        ],
        "null_rate": [
            0.01,
            0.012,
            0.011,
            0.010,
            0.013,
            0.009,
            0.011,
            0.010,
            0.012,
            0.010,
        ],
    }
)
```

Compute:

```python
baseline_rows = (
    historical_metrics["row_count"]
    .median()
)
```

---

# 125. Mini-Project Anomaly Detection

```python
def detect_volume_anomaly(
    current: float,
    baseline: float,
    warning_ratio: float,
    critical_ratio: float,
) -> str:
    if baseline <= 0:
        return "BASELINE_UNAVAILABLE"

    ratio = current / baseline

    if ratio <= critical_ratio:
        return "CRITICAL"

    if ratio <= warning_ratio:
        return "WARNING"

    return "NORMAL"
```

Then:

```python
status = detect_volume_anomaly(
    current=420,
    baseline=baseline_rows,
    warning_ratio=0.85,
    critical_ratio=0.60,
)
```

---

# 126. Mini-Project Quality Event

Produce:

```python
quality_event = {
    "dataset": "orders",
    "run_id": "run-2026-10-01-001",
    "check": "volume",
    "metric": "row_count",
    "observed": 420,
    "baseline": baseline_rows,
    "status": status,
}
```

This event can later be sent to:

- a metrics store;
- an observability platform;
- an alerting system;
- a dashboard;
- an audit repository.

---

# 127. Mini-Project Defect Injection

Inject:

### Volume Drop

```python
current_rows = int(baseline_rows * 0.50)
```

### Volume Spike

```python
current_rows = int(baseline_rows * 4.00)
```

### Null Spike

```text
null_rate = 0.30
```

### Freshness Failure

```text
freshness = 240 minutes
```

### Distribution Shift

Change the synthetic amount population so that:

```text
median
p95
```

move substantially.

The learner should determine which signals detect which defect.

---

# 128. Mini-Project Expected Reasoning

A strong solution should not say:

```text
anomaly = true
therefore pipeline = broken
```

Instead:

```text
metric deviated
    ↓
compare with baseline
    ↓
check seasonality
    ↓
check related metrics
    ↓
inspect upstream
    ↓
classify severity
    ↓
choose operational action
```

The goal is to teach investigation, not merely threshold calculation.

---

# 129. Advanced Mini-Project Extension

Add:

- rolling baselines;
- weekday-aware baselines;
- configurable thresholds;
- multiple severity levels;
- anomaly history;
- quality-event records;
- alert deduplication;
- suppression windows;
- unit tests;
- defect injection;
- performance measurement.

Then design how the monitor would integrate into an orchestrated pipeline:

```text
pipeline run
   ↓
metrics
   ↓
anomaly detection
   ↓
quality event
   ↓
quality gate
   ↓
publish / warn / block
```

---

# 130. Production Scenarios

## Scenario 1 — API Pagination Bug

Expected:

```text
1,000,000 rows
```

Received:

```text
250,000 rows
```

Investigation:

```text
volume anomaly
 ↓
inspect page count
 ↓
inspect API responses
 ↓
identify pagination truncation
```

The volume monitor detects the symptom; source inspection identifies the cause.

---

## Scenario 2 — Weekend Traffic

Saturday volume:

```text
45% lower
```

If Saturday is historically low, a weekday baseline is inappropriate.

Use:

```text
Saturday vs historical Saturdays
```

---

## Scenario 3 — Broken Transformation

Null rate:

```text
1% → 35%
```

Investigate:

- transformation code;
- join behavior;
- source fields;
- deployment;
- schema changes.

---

## Scenario 4 — Product Launch

Volume:

```text
+400%
```

This is statistically unusual.

It may nevertheless be legitimate.

Use:

- deployment/product-event context;
- known-event annotations;
- business confirmation.

---

## Scenario 5 — Late Data

Data arrives three hours late but eventually becomes complete.

This is primarily a freshness problem, not necessarily a completeness problem.

---

## Scenario 6 — Distribution Shift

Schema remains unchanged, but:

```text
median ↑
p95 ↑
```

Investigate:

- product mix;
- customer mix;
- pricing;
- transformation;
- source changes.

---

# 131. System Design Question: 5 TB Daily Dataset

Requirements:

```text
5 TB/day
volume monitoring
freshness monitoring
distribution monitoring
low operational overhead
```

A reasonable architecture may use:

```text
source
 ↓
partitioned ingestion
 ↓
metadata/partition metrics
 ↓
incremental distribution statistics
 ↓
baseline store
 ↓
anomaly engine
 ↓
quality event
 ↓
alert/dashboard
```

Do not scan the full five-terabyte dataset for every metric if metadata or incremental statistics can answer the question safely.

---

# 132. System Design: Millions of Partitions

For millions of partitions:

- avoid one expensive full scan per partition;
- use partition metadata;
- prioritize critical partitions;
- aggregate metrics;
- sample where appropriate;
- use incremental statistics;
- avoid high-cardinality alerts;
- aggregate failures.

The architecture should scale the monitoring system itself.

---

# 133. System Design: Low-Cost Monitoring

A layered approach:

```text
cheap checks
   ↓
identify suspicious partitions/runs
   ↓
expensive statistical checks
   ↓
detailed investigation
```

For example:

```text
row count
latest timestamp
metadata
```

first.

Then:

```text
distribution analysis
```

only when warranted.

---

# 134. System Design: Hundreds of Datasets

Do not create unique hand-written monitoring logic for every dataset.

Prefer configuration:

```text
dataset
metric
baseline method
window
threshold
severity
owner
```

Then use a shared monitoring engine.

This makes monitoring more consistent and maintainable.

---

# 135. Common Production Mistakes

## 1. One Static Threshold Forever

Business behavior changes.

**Better:** calibrate against historical behavior and review policies.

---

## 2. Ignoring Seasonality

Weekends, holidays, and business cycles can make valid data look abnormal.

**Better:** use seasonality-aware baselines.

---

## 3. Treating Every Anomaly as an Incident

A statistical anomaly may be legitimate.

**Better:** separate detection from incident classification.

---

## 4. Alerting on Every Fluctuation

Creates alert fatigue.

**Better:** aggregate, threshold, classify, and suppress known noise.

---

## 5. Not Storing Historical Metrics

Without history, baselines and debugging become difficult.

**Better:** persist quality metrics.

---

## 6. Contaminated Baselines

Known incidents become part of the "normal" reference.

**Better:** tag or exclude abnormal historical periods.

---

## 7. Confusing Freshness with Completeness

Data can be fresh but incomplete.

**Better:** monitor both.

---

## 8. Ignoring Timezones

Timezone mistakes can create false freshness failures.

**Better:** define timestamp semantics and use timezone-aware timestamps.

---

## 9. Using Naive Datetimes

Naive datetimes make cross-system comparisons ambiguous.

**Better:** use timezone-aware datetimes.

---

## 10. Failing on Zero Baselines

Percentage-change calculations can divide by zero.

**Better:** define explicit zero-baseline policy.

---

## 11. Scanning Huge Datasets Unnecessarily

Monitoring becomes expensive.

**Better:** use metadata, partitions, sampling, incremental metrics, and approximate statistics where appropriate.

---

## 12. Monitoring Only Row Counts

A dataset can have normal volume and wrong distributions.

**Better:** monitor volume + freshness + distribution.

---

## 13. Ignoring Distribution Changes

Every value can pass validation while the population shifts.

**Better:** monitor statistical behavior.

---

## 14. Undocumented Thresholds

Nobody knows why a check uses 20%.

**Better:** document rationale and ownership.

---

## 15. No Alert Owner

Alerts become operational orphans.

**Better:** every important check has an owner.

---

## 16. No Investigation Workflow

Alerting without diagnosis slows recovery.

**Better:** document investigation steps.

---

## 17. No Defect-Injection Tests

The monitor looks good but has never seen a failure.

**Better:** inject synthetic anomalies.

---

## 18. No False-Positive Testing

A detector may be mathematically correct but operationally noisy.

**Better:** test known seasonal and legitimate changes.

---

## 19. No Recovery Strategy

Detection without response does not improve reliability.

**Better:** define warn, block, retry, backfill, and escalation actions.

---

## 20. No Audit Trail

It becomes difficult to explain why a pipeline was blocked or allowed.

**Better:** store structured quality events and decisions.

---

# 136. Practical Production Checklist

## Volume

- [ ] Expected volume is defined.
- [ ] Minimum/maximum thresholds are defined where appropriate.
- [ ] Historical baseline is available.
- [ ] Seasonality is considered.
- [ ] Important partitions are monitored.
- [ ] Important business dimensions are monitored.

## Freshness

- [ ] Event time is defined.
- [ ] Ingestion time is defined.
- [ ] Processing/publication semantics are defined.
- [ ] Freshness SLA/SLO is defined.
- [ ] Timezone policy is defined.
- [ ] Late-arriving data policy is defined.
- [ ] Watermark semantics are understood where streaming is involved.

## Distribution

- [ ] Important numeric columns are identified.
- [ ] Important categorical columns are identified.
- [ ] Null rates are monitored.
- [ ] Cardinality is monitored.
- [ ] Quantiles are monitored.
- [ ] Historical distributions are stored.
- [ ] Distribution-shift methodology is documented.

## Anomaly Detection

- [ ] Thresholds are documented.
- [ ] Baseline method is documented.
- [ ] Seasonality is documented.
- [ ] False positives are measured.
- [ ] Severity policy is defined.
- [ ] Alerts have owners.
- [ ] Defect injection is tested.
- [ ] Insufficient-history behavior is defined.
- [ ] Baseline-unavailable behavior is defined.

## Operations

- [ ] Quality events are stored.
- [ ] Dashboards exist.
- [ ] Alerts contain actionable context.
- [ ] Alert deduplication exists where needed.
- [ ] Suppression windows are controlled and auditable.
- [ ] Investigation workflow is documented.
- [ ] Recovery workflow is documented.

## Performance

- [ ] Full scans are justified.
- [ ] Partition pruning is used where appropriate.
- [ ] Sampling is evaluated.
- [ ] Incremental metrics are considered.
- [ ] Approximate statistics are evaluated where appropriate.
- [ ] Monitoring cost is measured.

---

# 137. Interview Questions

## Basic — 10 Questions

### 1. What is a volume check?

A check that determines whether the observed amount of data is consistent with an expected value or range.

### 2. Why is row count useful?

It is simple and can reveal missing, duplicated, or unexpectedly increased data.

### 3. What is data freshness?

Freshness measures how current data is relative to its expected availability or event timing.

### 4. What is a data distribution?

It describes how values are spread across numeric or categorical outcomes.

### 5. What is a baseline?

A reference representation of expected historical behavior.

### 6. What is an anomaly?

An observation that is unusual relative to a chosen reference.

### 7. What is seasonality?

A recurring pattern related to time, such as weekday/weekend or hourly behavior.

### 8. What is a false positive?

A monitor reports a problem when the data is actually acceptable.

### 9. What is a false negative?

A monitor fails to detect a real problem.

### 10. Why are row counts alone insufficient?

A dataset can have normal volume while freshness, null rates, or distributions are wrong.

---

# 138. Moderate — 10 Questions

### 1. Absolute vs relative volume threshold?

An absolute threshold uses a fixed value. A relative threshold compares current behavior with a baseline.

### 2. Why can yesterday's row count be a bad baseline?

Yesterday may itself be abnormal or have different seasonal behavior.

### 3. Freshness vs completeness?

Freshness concerns timing; completeness concerns whether expected data is present.

### 4. Why use timezone-aware datetimes?

Because timestamps from different systems may represent different timezone contexts.

### 5. Why monitor null rate?

A sudden increase can reveal upstream, transformation, join, or schema problems.

### 6. What is cardinality?

The number of distinct values in a field.

### 7. Why use median instead of mean?

Median is generally less sensitive to extreme values.

### 8. Why can thresholds generate alert fatigue?

Natural fluctuations can repeatedly cross rigid boundaries.

### 9. What is a rolling baseline?

A reference calculated from a recent historical window.

### 10. Why test zero baselines?

Because percentage-change calculations are undefined when dividing by zero.

---

# 139. Hard — 10 Questions

### 1. When would z-score detection be inappropriate?

When assumptions around the reference distribution are poor, outliers dominate, seasonality is ignored, or the metric is not well modeled by mean/std behavior.

### 2. Why are robust statistics useful?

They can reduce sensitivity to extreme observations.

### 3. Point anomaly vs distribution shift?

A point anomaly concerns an individual unusual observation. Distribution shift concerns a broader change in population behavior.

### 4. Why might a statistically significant change be legitimate?

Business events can intentionally change the data distribution.

### 5. How would you monitor categorical distributions?

Track category frequencies/proportions and compare them with an appropriate historical reference.

### 6. How would you detect a stale partition?

Compare its latest relevant timestamp or publication state with the expected freshness window.

### 7. How do you prevent baseline contamination?

Exclude or tag periods known to be abnormal.

### 8. How do you reduce false positives?

Use appropriate baselines, seasonality, suppression windows, aggregation, severity, and business context.

### 9. Why can full scans be problematic?

They consume storage and compute resources and can increase monitoring latency.

### 10. How would you monitor a large dataset cheaply?

Use metadata, partition-level checks, incremental metrics, sampling, and targeted expensive checks.

---

# 140. Advanced — 10 Questions

### 1. Design anomaly monitoring for a 5 TB daily dataset.

Use layered monitoring, partition metadata, incremental metrics, baseline storage, targeted distribution analysis, and structured quality events.

### 2. Detect a 40% daily volume drop without excessive alerts.

Use historical and seasonality-aware baselines, severity thresholds, context, and aggregated alerts.

### 3. Monitor freshness for streaming data.

Define event-time semantics, ingestion lag, windows, watermarks, late-event policy, and rolling freshness metrics.

### 4. Detect categorical distribution changes.

Compare normalized frequency distributions against a suitable historical reference and combine the result with business context.

### 5. Detect data drift in a customer dataset.

Track numeric distributions, categorical proportions, null rates, cardinality, and relevant business dimensions over time.

### 6. Design a weekday-aware baseline.

Group historical observations by comparable weekday/time-of-day periods and exclude known abnormal periods.

### 7. Design anomaly detection for millions of partitions.

Use partition metadata, incremental aggregation, prioritization, scalable storage, and alert aggregation.

### 8. Design a low-cost monitoring system.

Use cheap metadata checks first and reserve expensive statistical checks for suspicious datasets/partitions.

### 9. Design a quality gate for a critical dataset.

Combine volume, freshness, and distribution checks into a structured decision with explicit block/warn policies.

### 10. Design anomaly monitoring across hundreds of datasets.

Use a shared configuration-driven monitoring framework with dataset-specific policies, baseline methods, ownership, and severity.

---

# 141. System Design / Architecture Questions

## Question 1 — 5 TB Daily Dataset

Requirements:

- volume;
- freshness;
- distribution;
- low monitoring cost.

Discuss:

```text
partition metadata
→ incremental metrics
→ baseline store
→ anomaly engine
→ quality event
→ alerting/dashboard
```

---

## Question 2 — 40% Daily Volume Drop

Design:

```text
current metric
→ seasonality-aware baseline
→ deviation
→ severity
→ owner alert
→ investigation
```

Do not immediately block all datasets based on a single universal threshold.

---

## Question 3 — Streaming Freshness

Include:

```text
event time
ingestion time
watermark
late events
window metrics
alert policy
```

---

## Question 4 — Distribution Monitoring

Explain how you would choose between:

```text
percentiles
z-score
IQR
PSI
KS
```

based on:

- data type;
- distribution shape;
- scale;
- cost;
- business meaning.

---

## Question 5 — Hundreds of Datasets

Design a configuration model:

```text
dataset
owner
metric
baseline
seasonality
threshold
severity
action
```

Then implement a shared monitoring engine.

---

# 142. Final Practical Challenge

You receive a synthetic historical dataset containing:

- normal periods;
- volume spikes;
- volume drops;
- freshness problems;
- null-rate changes;
- cardinality changes;
- distribution shifts;
- legitimate seasonal changes.

Your task:

1. calculate metrics;
2. establish baselines;
3. detect anomalies;
4. classify severity;
5. identify likely failure types;
6. investigate false positives;
7. explain reasoning;
8. design production improvements.

Your answer should explicitly distinguish:

```text
unusual
```

from:

```text
incorrect
```

and:

```text
incident
```

---

# 143. Suggested Challenge Structure

For each detected anomaly, produce:

```text
Metric
Current value
Reference value
Deviation
Baseline method
Seasonality context
Anomaly status
Severity
Likely explanations
Investigation steps
Operational action
Confidence / limitations
```

This forces the learner to reason like a Data Engineer rather than merely calculate a statistic.

---

# 144. Final Mental Model

Schema validation asks:

> **Is the structure valid?**

Record validation asks:

> **Is this record valid?**

Volume validation asks:

> **Did approximately the expected amount of data arrive?**

Freshness validation asks:

> **Did the data arrive on time?**

Distribution validation asks:

> **Does the data still behave like expected?**

Anomaly detection asks:

> **Is the observed behavior unusual relative to an appropriate baseline?**

Production quality asks:

> **What should we do about the anomaly?**

The complete model is:

```text
                DATA QUALITY
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
    Volume        Freshness    Distribution
       │             │             │
       └─────────────┼─────────────┘
                     ↓
              Historical Context
                     ↓
                  Baseline
                     ↓
              Anomaly Detection
                     ↓
              Severity / Policy
                     ↓
          ┌──────────┼──────────┐
          ↓          ↓          ↓
        Pass       Warn       Block
          │          │          │
          └──────────┼──────────┘
                     ↓
             Investigation
                     ↓
               Root Cause
                     ↓
                Recovery
                     ↓
             Prevent Recurrence
```

The production principle is:

> **A production data-quality system does not merely detect unusual numbers. It establishes context, detects meaningful deviations, controls false alarms, assigns severity, supports investigation, and turns anomalies into actionable operational signals.**

The most important mental distinction is:

```text
unusual
    ≠
wrong
```

and:

```text
statistical anomaly
    ≠
business incident
```

A strong Data Engineer builds monitoring that can detect unusual behavior while preserving enough context for humans and downstream systems to decide what it means.

---

# 145. Final Self-Review

- [x] Topic 08 is taught from beginner level.
- [x] Volume is explained deeply.
- [x] Freshness is explained deeply.
- [x] Distribution is explained deeply.
- [x] Historical baselines are explained.
- [x] Seasonality is explained.
- [x] Thresholds are explained.
- [x] Statistical anomaly detection is explained.
- [x] Robust statistics are explained.
- [x] Distribution shift is explained.
- [x] False positives are explained.
- [x] False negatives are explained.
- [x] Alert fatigue is explained.
- [x] Severity/action policies are explained.
- [x] Python examples are included.
- [x] pandas examples are included.
- [x] Time-series examples are included.
- [x] Batch monitoring is covered.
- [x] Streaming monitoring is covered.
- [x] Performance/cost trade-offs are covered.
- [x] Pandera/GX/Soda/SQL integration is discussed.
- [x] Defect injection is included.
- [x] Debugging workflow is included.
- [x] Mini-project is included.
- [x] Advanced project extension is included.
- [x] Testing is included.
- [x] Production architecture is included.
- [x] Common mistakes are included.
- [x] Practical checklist is included.
- [x] 40 interview questions are included.
- [x] Architecture questions are included.
- [x] Production scenarios are included.
- [x] Final practical challenge is included.
- [x] Final mental model is included.
- [x] The chapter remains focused on Topic 08 rather than reproducing the entire Module 2.11.

---

## Completion Criteria

You have completed this topic when you can:

- explain why schema correctness does not prove operational data quality;
- build volume checks;
- calculate safe relative deviation;
- explain zero-baseline handling;
- define freshness;
- distinguish event, ingestion, processing, and publication time;
- calculate timezone-aware freshness lag;
- distinguish freshness from completeness;
- explain watermarks and late data;
- calculate and interpret distribution statistics;
- monitor null rates and cardinality;
- build historical baselines;
- account for seasonality;
- detect anomalies with simple thresholds;
- explain z-scores;
- use robust statistics appropriately;
- explain distribution-shift methods;
- distinguish statistical anomalies from business anomalies;
- control false positives and alert fatigue;
- map anomalies to operational actions;
- implement checks in Python and pandas;
- design batch and streaming monitoring;
- control monitoring cost;
- integrate checks with common data-quality layers;
- debug an anomaly from metric to root cause;
- test detection with synthetic defects;
- design a production monitoring architecture;
- explain the trade-offs behind your anomaly-detection choices.

The objective is not to memorize one anomaly algorithm.

The objective is to learn how a production Data Engineer determines:

```text
What should normal look like?
        ↓
What changed?
        ↓
Is the change statistically unusual?
        ↓
Is it operationally meaningful?
        ↓
What evidence supports that conclusion?
        ↓
What should the pipeline do?
```

That is the foundation of production-grade volume, freshness, and distribution anomaly monitoring.
