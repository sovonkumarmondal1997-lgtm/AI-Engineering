# Feature Engineering at Scale

> **Stage:** 2C — Data Engineering_3  
> **Module:** 10 — Big Data ML and MLOps Handoff  
> **Lesson:** 02  
> **Audience:** Data engineers moving from batch analytics into production ML data systems  
> **Scope:** Feature definitions, temporal correctness, feature stores, online/streaming computation, quality, and governance

## 1. Learning outcomes

By completing this lesson, you should be able to:

- Define a feature in terms of an entity, value, event/availability time, and transformation.
- Build numerical, categorical, text, time, count, rolling-window, and RFM features.
- Construct historical training features that use only information available at each prediction time.
- Explain and implement as-of joins in pandas, DuckDB, Polars, Snowflake SQL, and Spark SQL while respecting engine differences.
- Diagnose and test training–serving skew.
- Explain offline stores, online stores, feature views, entities, and materialization; implement a small feature-store-style local example and understand Feast's role.
- Design batch, streaming, and request-time feature paths with freshness and latency objectives.
- Apply feature contracts, quality gates, backfill controls, lineage, ownership, privacy, and deprecation practices.
- Understand where embeddings and vector stores fit into feature engineering for retrieval-augmented generation (RAG) systems.

## 2. Prerequisites and environment

This lesson builds on Python, pandas, SQL/window functions, data quality contracts, Spark/streaming fundamentals, and the overview of data services and feature stores. It is part of the handoff from data engineering to ML: correct feature data is as important as the model that consumes it.

### Local learning environment

Use Python 3.12 or a compatible Python version supported by your chosen package releases. Create a project:

```bash
mkdir -p experiments/02_features
cd experiments/02_features
uv init --python 3.12
uv add pandas numpy duckdb polars scikit-learn
uv add --dev pytest
uv lock
# Optional integration dependencies; add only when doing those exercises.
uv add feast redis
uv lock
```

The core temporal examples below use pandas; the leakage demonstration also uses scikit-learn. The DuckDB and Polars exercises require their listed packages. `uv.lock` records the resolved environment for repeatable installs. Feast, Redis, Kafka, and Spark are optional integration exercises: add only the dependencies needed for that exercise, then regenerate and commit the lock file. A lock file improves repeatability but does not make operating-system services or Java/Spark runtimes portable.

A suggested layout:

```text
experiments/02_features/
├── pyproject.toml
├── data/
│   └── generated/                 # deterministic synthetic input
├── features/
│   ├── definitions.py             # shared feature logic
│   └── validation.py              # quality contracts
├── notebooks/                     # optional exploration
├── feast_repo/                    # optional Feast integration
├── streaming/                     # optional Kafka/Spark exercise
└── tests/
    ├── test_point_in_time.py
    ├── test_feature_parity.py
    └── test_feature_quality.py
```

**Important:** a code sample is only a claim about what it does—not evidence that external infrastructure has been run. This lesson separates local runnable examples from optional service-backed exercises.

## 3. Feature engineering fundamentals

### 3.1 What is a feature?

A **feature** is a measurable input supplied to a model for a particular entity at a particular prediction time. The entity might be a customer, account, device, merchant, or product.

A useful feature definition records more than a column name:

| Property | Example |
|---|---|
| Name | `orders_30d_count` |
| Entity key | `customer_id` |
| Meaning | Number of qualifying orders in the prior 30 days |
| Window | `(prediction_time - 30 days, prediction_time]` |
| Source | `orders` event table |
| Event-time field | `event_time` |
| Availability-time field | `available_at` |
| Null policy | Zero only when source completeness is known; otherwise unknown |
| Type / unit | Integer count |
| Freshness objective | 95% of values no more than 5 minutes behind source availability |
| Owner | Customer Data Platform |
| Version | `v1` |

A feature value without its time semantics is incomplete for temporal ML. The value `orders_30d_count = 4` means different things if computed as of Monday versus Friday.

### 3.2 Common feature families

- **Numerical:** account balance, amount, tenure in days.
- **Categorical:** plan, country, device family. Often encoded before model input.
- **Text:** support-ticket text or token counts.
- **Date/time:** hour of day, day of week, days since signup. Use the prediction-time timezone and calendar semantics deliberately.
- **Counts and aggregates:** transactions in a window, mean order value, failed logins.
- **Recency/frequency/monetary (RFM):** time since last purchase, purchase count over a defined period, and total or average spend over that period.
- **Derived:** `log1p(transaction_amount)`, ratios, buckets, and interactions.
- **Embeddings:** dense numeric vectors produced by an embedding model; these require model/version lineage just like other features.

A feature pipeline maps source records to a stable model-input contract:

```text
raw events + entity records
          |
          v
clean / deduplicate / validate
          |
          v
temporal filtering and aggregation
          |
          v
typed feature definitions
          |
          +------> offline historical features for training
          |
          +------> online latest features for low-latency inference
```

### 3.3 Transformations and their trade-offs

| Transformation | Example | Watch out for |
|---|---|---|
| Scaling | Standardize a numeric value | Fit parameters on training data only; keep them consistent in serving |
| Encoding | Map plan category to model representation | Unknown categories and category-map changes |
| Bucketing | Age into bands | Boundary semantics and changing business rules |
| Log transform | `log1p(amount)` | Negative values, units, and zero handling |
| Date parts | Hour/day-of-week | Time zones, daylight-saving transitions, calendar changes |
| Text counts | Token or keyword counts | Tokenization consistency, language, vocabulary drift |
| Aggregation | Count/sum/mean in last 7/30/90 days | Time boundary, late data, duplicate events, missing versus zero |

A transformation should be chosen because it makes the signal useful and operationally reliable—not because it is fashionable. Avoid needless transformations that increase skew risk without improving the model.

## 4. Aggregations and rolling-window features

For an entity \(e\) and prediction time \(t\), a 30-day transaction count is conceptually:

\[
\operatorname{count}_{30d}(e,t)=
\#\{x: x.entity=e,\ t-30d < x.event\_time \le t,\ x.available\_at \le t\}
\]

The `available_at <= t` condition is critical when the historical system knows when an event actually became usable. If an event occurred on Tuesday but was ingested on Friday, a Wednesday prediction could not have used it.

For an amount sum, replace the count with the sum of qualifying amounts. For an average, compute the sum and count with an explicit zero-count policy. Reuse the same semantics for 7-, 30-, and 90-day windows.

### Local runnable temporal aggregation

Save as `features/definitions.py` or run in a notebook:

```python
from __future__ import annotations

import pandas as pd


_REQUIRED_EVENT_COLUMNS = {
    "customer_id", "event_id", "event_time", "available_at", "amount"
}


def _require_aware_datetime(series: pd.Series, name: str) -> None:
    if not isinstance(series.dtype, pd.DatetimeTZDtype):
        raise TypeError(f"{name} must be a timezone-aware pandas datetime column")
    if series.isna().any():
        raise ValueError(f"{name} must not contain null timestamps")


def features_as_of(
    events: pd.DataFrame,
    entity_id: str,
    as_of: pd.Timestamp,
) -> dict[str, float | int]:
    """Compute example transaction features using records knowable at `as_of`.

    Input must contain one or more versions per logical event, keyed by
    (customer_id, event_id). `available_at` is when a version became usable;
    for a repeated event, the latest version available by `as_of` wins.
    Window convention is (as_of - window, as_of].

    This function assumes the upstream source-completeness gate has passed.
    A zero count is not proof of no activity if a source partition is missing.
    """
    missing = _REQUIRED_EVENT_COLUMNS - set(events.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    as_of = pd.Timestamp(as_of)
    if as_of.tzinfo is None:
        raise ValueError("as_of must be timezone-aware")
    as_of = as_of.tz_convert("UTC")

    _require_aware_datetime(events["event_time"], "event_time")
    _require_aware_datetime(events["available_at"], "available_at")
    if events[["customer_id", "event_id"]].isna().any().any():
        raise ValueError("customer_id and event_id must not be null")
    if not pd.api.types.is_numeric_dtype(events["amount"]):
        raise TypeError("amount must be numeric; use null for unknown amounts")

    # Normalize instants to UTC, then select the latest version that was
    # actually available at prediction time. Equal-time versions are ambiguous.
    visible = events.loc[
        (events["customer_id"] == entity_id)
        & (events["available_at"] <= as_of)
    ].copy()
    visible["event_time"] = visible["event_time"].dt.tz_convert("UTC")
    visible["available_at"] = visible["available_at"].dt.tz_convert("UTC")
    if visible.duplicated(["customer_id", "event_id", "available_at"]).any():
        raise ValueError("duplicate event versions share available_at; define a tie-breaker")
    visible = visible.sort_values("available_at").drop_duplicates(
        ["customer_id", "event_id"], keep="last"
    )
    visible = visible.loc[visible["event_time"] <= as_of]

    result: dict[str, float | int] = {}
    for days in (7, 30, 90):
        lower = as_of - pd.Timedelta(days=days)
        window = visible.loc[visible["event_time"] > lower]
        result[f"orders_{days}d_count"] = int(len(window))
        # A partial sum that silently skips unknown amounts would look complete.
        amounts_complete = not window.empty and window["amount"].notna().all()
        if amounts_complete:
            result[f"amount_{days}d_sum"] = float(window["amount"].sum())
            result[f"amount_{days}d_mean"] = float(window["amount"].mean())
        else:
            result[f"amount_{days}d_sum"] = float("nan")
            result[f"amount_{days}d_mean"] = float("nan")

    if visible.empty:
        result["days_since_last_order"] = -1.0  # documented sentinel; add a presence flag in production
    else:
        latest = visible["event_time"].max()
        result["days_since_last_order"] = (as_of - latest).total_seconds() / 86_400
    return result
```

The sentinel `-1.0` is only one possible policy. In a production contract, consider a separate `has_prior_order` indicator or a nullable value, because “no order exists” and “an order happened one day ago” are semantically different. The source completeness contract must also distinguish “no event” from “events not yet ingested.”

### Deterministic synthetic data and assertions

```python
import pandas as pd

events = pd.DataFrame(
    [
        {
            "customer_id": "c1",
            "event_id": "e1",
            "event_time": pd.Timestamp("2026-01-02T10:00:00Z"),
            "available_at": pd.Timestamp("2026-01-02T10:01:00Z"),
            "amount": 20.0,
        },
        {
            "customer_id": "c1",
            "event_id": "e2",
            "event_time": pd.Timestamp("2026-01-20T10:00:00Z"),
            "available_at": pd.Timestamp("2026-01-25T09:00:00Z"),
            "amount": 50.0,
        },
        {
            "customer_id": "c1",
            "event_id": "e3",
            "event_time": pd.Timestamp("2026-02-05T10:00:00Z"),
            "available_at": pd.Timestamp("2026-02-05T10:02:00Z"),
            "amount": 90.0,
        },
    ]
)

as_of = pd.Timestamp("2026-01-22T00:00:00Z")
customer_id = "c1"
f = features_as_of(events, customer_id, as_of)

assert f["orders_30d_count"] == 1
assert f["amount_30d_sum"] == 20.0
assert f["days_since_last_order"] > 0
assert f["orders_7d_count"] == 0
assert pd.isna(f["amount_7d_sum"])  # no eligible amount is unknown, not a measured zero
```

The January 20 event is excluded because it was not available until January 25. The February event is future-dated relative to the prediction. This is the desired historical behavior.

Save the following as `tests/test_point_in_time.py` after placing the function in `features/definitions.py`. These tests check the computed result, not merely the timestamps remaining in the input:

```python
import pandas as pd
import pytest

from features.definitions import features_as_of


@pytest.fixture
def events():
    return pd.DataFrame([
        {"customer_id": "c1", "event_id": "e1",
         "event_time": pd.Timestamp("2026-01-02T10:00:00Z"),
         "available_at": pd.Timestamp("2026-01-02T10:01:00Z"), "amount": 20.0},
        {"customer_id": "c1", "event_id": "e2",
         "event_time": pd.Timestamp("2026-01-20T10:00:00Z"),
         "available_at": pd.Timestamp("2026-01-25T09:00:00Z"), "amount": 50.0},
        {"customer_id": "c1", "event_id": "e3",
         "event_time": pd.Timestamp("2026-02-05T10:00:00Z"),
         "available_at": pd.Timestamp("2026-02-05T10:02:00Z"), "amount": 90.0},
    ])


def test_future_and_late_events_do_not_change_historical_features(events):
    as_of = pd.Timestamp("2026-01-22T00:00:00Z")
    baseline = features_as_of(events, "c1", as_of)
    extra = pd.DataFrame([
        {"customer_id": "c1", "event_id": "future",
         "event_time": as_of + pd.Timedelta(days=1),
         "available_at": as_of + pd.Timedelta(days=1), "amount": 999.0},
        {"customer_id": "c1", "event_id": "late",
         "event_time": as_of - pd.Timedelta(days=1),
         "available_at": as_of + pd.Timedelta(days=2), "amount": 888.0},
    ])
    actual = features_as_of(pd.concat([events, extra], ignore_index=True), "c1", as_of)
    for name, expected in baseline.items():
        if pd.isna(expected):
            assert pd.isna(actual[name]), name
        else:
            assert actual[name] == expected, name


def test_latest_correction_known_at_prediction_time_wins(events):
    correction = pd.DataFrame([{
        "customer_id": "c1", "event_id": "e1",
        "event_time": pd.Timestamp("2026-01-02T10:00:00Z"),
        "available_at": pd.Timestamp("2026-01-21T00:00:00Z"), "amount": 25.0,
    }])
    actual = features_as_of(pd.concat([events, correction], ignore_index=True),
                            "c1", pd.Timestamp("2026-01-22T00:00:00Z"))
    assert actual["orders_30d_count"] == 1
    assert actual["amount_30d_sum"] == 25.0


def test_naive_prediction_time_is_rejected(events):
    with pytest.raises(ValueError, match="timezone-aware"):
        features_as_of(events, "c1", pd.Timestamp("2026-01-22"))


def test_equal_time_is_included_but_lower_window_boundary_is_excluded(events):
    as_of = pd.Timestamp("2026-01-22T00:00:00Z")
    boundary = pd.DataFrame([
        {"customer_id": "c1", "event_id": "lower-bound",
         "event_time": as_of - pd.Timedelta(days=30),
         "available_at": as_of - pd.Timedelta(days=30), "amount": 10.0},
        {"customer_id": "c1", "event_id": "at-as-of",
         "event_time": as_of, "available_at": as_of, "amount": 5.0},
    ])
    actual = features_as_of(boundary, "c1", as_of)
    assert actual["orders_30d_count"] == 1
    assert actual["amount_30d_sum"] == 5.0


def test_unknown_amount_does_not_produce_partial_sum(events):
    events.loc[0, "amount"] = float("nan")
    actual = features_as_of(events, "c1", pd.Timestamp("2026-01-22T00:00:00Z"))
    assert actual["orders_30d_count"] == 1
    assert pd.isna(actual["amount_30d_sum"])
```

Run `uv run pytest -q`. These tests assume the upstream source-completeness gate is evaluated separately; they test temporal eligibility and deterministic correction behavior.

### Scaling to distributed data

At scale, avoid collecting raw events into Python. Use partitioned SQL/Spark jobs, incremental aggregation tables, or streaming state. Partition by a useful date and possibly entity hash; retain enough history to cover the maximum lookback plus lateness/correction policy. Pre-aggregate where semantics permit. Avoid a single hot entity creating an oversized state or partition.

## 5. Point-in-time correctness and leakage

### 5.1 Prediction time is the contract

For each training row, define:

- **Entity:** who or what receives a prediction.
- **Prediction time (`t`):** when the prediction would have been made.
- **Label window:** the future interval used to determine the outcome.
- **Feature availability rule:** which facts were available by `t`.
- **Label maturity:** when the outcome can be considered complete.

For churn, a possible definition is: at each month-end, predict whether an active customer will cancel in the next 30 days. Features may include activity before month-end; “days since cancellation” is invalid because cancellation is the outcome or future knowledge.

### 5.2 Event time versus availability time

- **Event time:** when the business event occurred.
- **Processing/ingestion time:** when a pipeline received or processed it.
- **Availability time:** when the feature system could safely expose it to a prediction.

Availability time is the decisive boundary for replaying historical predictions. Event time alone is insufficient when ingestion is delayed, source data is corrected later, or backfills rewrite history.

### 5.3 Common leakage patterns

1. Joining each historical row to the latest feature value today.
2. Including events with `event_time > prediction_time`.
3. Including late-arriving events that were not available at prediction time.
4. Using post-outcome fields such as cancellation reason to predict cancellation.
5. Computing aggregate statistics over the full dataset before splitting.
6. Using label-derived information in a feature.
7. Treating a missing upstream partition as a genuine zero.

Leakage can make offline metrics look excellent while production performance collapses. The remedy is not just a time-based train/test split: every feature row must itself be point-in-time correct.

### 5.4 Correct and incorrect join logic

**Incorrect:** aggregate all transactions for a customer, join the aggregate to every historical prediction row, and assume the resulting values are historical. This leaks future activity.

**Correct:** for each prediction row, include only qualifying events within the defined window whose event and availability timestamps satisfy the prediction-time contract.

Historical corrections require an explicit policy. If a record was corrected after the original prediction, an exact historical replay normally uses the value known at prediction time. A “latest corrected truth” analysis is a different dataset and must not be confused with online-available history.

## 6. As-of joins across engines

An as-of join attaches the most recent eligible record at or before a timestamp, typically within the same entity. It is useful for state snapshots, account status, device configuration, or slowly changing values. It is **not automatically a replacement for a rolling aggregation**; event aggregates need window filtering and aggregation.

### 6.1 pandas `merge_asof`

Both inputs must be sorted by the merge key (globally sorted by the timestamp key as required by the pandas API). `by` restricts matches to an entity; `direction="backward"` selects the latest right-side timestamp not later than the left-side timestamp. This concise pattern is valid only when `feature_time` is the timestamp at which the snapshot became eligible for use and there is no separate effective-time constraint. If event/effective time and availability time differ, a one-key `merge_asof` can leak a late-arriving record or discard a valid fallback; use the dual-time candidate-and-rank pattern below instead.

```python
import pandas as pd

predictions = pd.DataFrame({
    "customer_id": ["c1", "c1", "c2"],
    "prediction_time": pd.to_datetime([
        "2026-01-10T00:00:00Z",
        "2026-01-20T00:00:00Z",
        "2026-01-12T00:00:00Z",
    ]),
})
snapshots = pd.DataFrame({
    "customer_id": ["c1", "c1", "c2"],
    # In this simplified example, feature_time is the availability/effective
    # timestamp. If those timestamps differ, use the dual-time pattern below.
    "feature_time": pd.to_datetime([
        "2026-01-01T00:00:00Z",
        "2026-01-15T00:00:00Z",
        "2026-01-11T00:00:00Z",
    ]),
    "source_version": [1, 2, 1],
    "risk_band": ["low", "high", "medium"],
})
# If ties exist, keep the highest deterministic source_version per entity/time.
snapshots = (snapshots.sort_values(["customer_id", "feature_time", "source_version"])
             .drop_duplicates(["customer_id", "feature_time"], keep="last"))

left = predictions.sort_values("prediction_time")
right = snapshots.sort_values("feature_time")
joined = pd.merge_asof(
    left,
    right,
    left_on="prediction_time",
    right_on="feature_time",
    by="customer_id",
    direction="backward",
    tolerance=pd.Timedelta("30D"),
)
assert (joined["feature_time"].isna() |
        (joined["feature_time"] <= joined["prediction_time"])).all()
```

Use a tolerance when stale matches should be rejected. Resolve duplicate right-side timestamps deterministically before joining; otherwise the selected record may be ambiguous. Inspect null matches explicitly. The single-clock example above intentionally omits delayed availability.

When `feature_time` (effective time) and `available_at` differ, enforce both constraints. For a small/medium pandas dataset, a candidate join illustrates the correct semantics; for large data, push this logic into the warehouse/Spark engine to avoid a potentially large same-entity candidate expansion:

```python
pred = predictions.assign(prediction_id=range(len(predictions)))
snapshots_dual = pd.DataFrame({
    "customer_id": ["c1", "c1", "c1", "c2"],
    "feature_time": pd.to_datetime([
        "2026-01-01T00:00:00Z", "2026-01-15T00:00:00Z",
        "2026-01-18T00:00:00Z", "2026-01-11T00:00:00Z",
    ]),
    "available_at": pd.to_datetime([
        "2026-01-01T00:01:00Z", "2026-01-25T00:00:00Z",
        "2026-01-18T00:01:00Z", "2026-01-11T00:01:00Z",
    ]),
    "source_version": [1, 2, 3, 1],
    "risk_band": ["low", "high", "medium", "medium"],
})
candidates = pred.merge(snapshots_dual, on="customer_id", how="left")
eligible = candidates.loc[
    (candidates["feature_time"] <= candidates["prediction_time"])
    & (candidates["available_at"] <= candidates["prediction_time"])
    & (candidates["feature_time"] >= candidates["prediction_time"] - pd.Timedelta("30D"))
].copy()
# source_version must be a deterministic, monotonically ordered version key.
latest = (eligible.sort_values(
    ["prediction_id", "feature_time", "available_at", "source_version"]
).drop_duplicates("prediction_id", keep="last"))
# Left-restore predictions with no eligible match; never fill missing values with a future row.
result = pred.merge(
    latest[["prediction_id", "feature_time", "available_at", "risk_band"]],
    on="prediction_id", how="left", validate="one_to_one",
)
assert (result["feature_time"].isna() | (result["feature_time"] <= result["prediction_time"])).all()
assert (result["available_at"].isna() | (result["available_at"] <= result["prediction_time"])).all()
```

### 6.2 DuckDB `ASOF JOIN`

DuckDB supports an as-of join with an inequality condition on the ordered timestamp. This example assumes `feature_time` already means the timestamp at which the row became eligible for use. If `event/effective_time` and `available_at` are separate, enforce both constraints in a candidate join and rank eligible rows; a single ASOF inequality cannot express both independently. Verify syntax against the installed DuckDB release.

```sql
SELECT p.customer_id, p.prediction_time, s.risk_band, s.feature_time
FROM predictions AS p
ASOF LEFT JOIN snapshots AS s
  ON p.customer_id = s.customer_id
 AND p.prediction_time >= s.feature_time;
```

The inequality expresses “latest feature time not after prediction time.” Add an explicit freshness/tolerance filter if old values should not be accepted. Check duplicate timestamps and time-zone consistency before the join.

### 6.3 Polars `join_asof`

Polars supports `join_asof` for DataFrame and LazyFrame workflows. Sort the as-of keys and use a backward strategy for the latest eligible prior state. This example uses the same **single-clock** assumption as the pandas example: `feature_time` already represents eligibility/availability time.

```python
from datetime import datetime, timezone
import polars as pl

predictions_pl = pl.DataFrame({
    "customer_id": ["c1", "c1", "c2"],
    "prediction_time": [
        datetime(2026, 1, 10, tzinfo=timezone.utc),
        datetime(2026, 1, 20, tzinfo=timezone.utc),
        datetime(2026, 1, 12, tzinfo=timezone.utc),
    ],
}).sort("prediction_time")
snapshots_pl = pl.DataFrame({
    "customer_id": ["c1", "c1", "c2"],
    "feature_time": [
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        datetime(2026, 1, 15, tzinfo=timezone.utc),
        datetime(2026, 1, 11, tzinfo=timezone.utc),
    ],
    "risk_band": ["low", "high", "medium"],
}).sort("feature_time")
joined_pl = predictions_pl.join_asof(
    snapshots_pl,
    left_on="prediction_time",
    right_on="feature_time",
    by="customer_id",
    strategy="backward",
    tolerance="30d",
)
assert joined_pl.filter(
    pl.col("feature_time").is_not_null()
    & (pl.col("feature_time") > pl.col("prediction_time"))
).height == 0
```

For separate effective and availability timestamps, use a dual-time candidate-and-rank pattern like the Spark SQL section rather than assuming `join_asof` can enforce both inequalities at once.

### 6.4 Snowflake SQL

Snowflake uses `MATCH_CONDITION` for the ordered inequality and `ON` for entity equality. This example again assumes the right-side timestamp is the timestamp at which the state became eligible for use:

```sql
SELECT
  p.prediction_id,
  p.customer_id,
  p.prediction_time,
  s.feature_time,
  s.risk_band
FROM predictions AS p
ASOF JOIN snapshots AS s
  MATCH_CONDITION (p.prediction_time >= s.feature_time)
  ON p.customer_id = s.customer_id;
```

If `available_at` differs from `feature_time`, a single `ASOF JOIN` inequality is insufficient to enforce both `s.feature_time <= p.prediction_time` and `s.available_at <= p.prediction_time`; use a candidate join plus deterministic ranking, then validate the output. Test ties, no-match rows, tolerance, and timestamp types in the target account/runtime.

### 6.5 Spark SQL window pattern

Where a direct as-of operator is not available or is not appropriate, join candidates and rank them. This pattern can be expensive because it may create many candidate pairs; constrain the time range and inspect the execution plan.

```sql
WITH candidates AS (
  SELECT
    p.prediction_id,
    p.customer_id,
    p.prediction_time,
    s.feature_time,
    s.available_at,
    s.source_version,
    s.risk_band,
    ROW_NUMBER() OVER (
      PARTITION BY p.prediction_id
      ORDER BY s.feature_time DESC, s.available_at DESC, s.source_version DESC
    ) AS rn
  FROM predictions p
  LEFT JOIN snapshots s
    ON p.customer_id = s.customer_id
   AND s.feature_time <= p.prediction_time
   AND s.available_at <= p.prediction_time
   AND s.feature_time >= p.prediction_time - INTERVAL 30 DAYS
)
SELECT prediction_id, customer_id, prediction_time, feature_time, available_at, risk_band
FROM candidates
WHERE rn = 1;
```

A `prediction_id` should uniquely identify a prediction row; partitioning only by customer could incorrectly collapse multiple prediction times. This dual-time pattern requires `available_at` and a deterministic `source_version` tie-breaker in the snapshot source. If no eligible snapshot exists, the left join retains a null-valued candidate. Validate both `feature_time <= prediction_time` and `available_at <= prediction_time` for all matched records. Candidate joins can be expensive; constrain by entity/time and inspect the execution plan.

### Engine-specific checklist

- Confirm sorting requirements and supported data types.
- Standardize timezone representation (prefer UTC for stored instants).
- Define duplicate/tie-breaking behavior.
- Define maximum tolerated staleness.
- Test unmatched entities and null timestamps.
- Distinguish “latest state as of t” from “aggregate events in a rolling window.”
- Compare row counts and matched-row rates before and after joining.

## 7. Training–serving skew and parity testing

**Training–serving skew** occurs when the feature values used to train a model differ systematically from those available at prediction time. Common causes include different null defaults, timezone handling, category encodings, rounding, window boundaries, deduplication, late data, and online-store staleness.

The most reliable mitigation is to share feature definitions and semantics. The offline and online systems may have different physical implementations, but they must implement the same contract. Where sharing code is impossible, parity tests become a required control.

### 7.1 A meaningful parity test

The comparison must use equivalent entities and equivalent logical times. Comparing today's offline aggregate with an online value materialized yesterday does not prove correctness; it measures freshness and parity together.

```python
from math import isclose
from collections.abc import Mapping

import pandas as pd


def assert_feature_parity(
    offline: Mapping[str, object],
    online: Mapping[str, object],
    *,
    numeric_features: tuple[str, ...],
    categorical_features: tuple[str, ...] = (),
    abs_tol: float = 1e-8,
) -> None:
    """Compare values for the same entity and logical as-of time."""
    for name in numeric_features:
        left, right = offline[name], online[name]
        if pd.isna(left) and pd.isna(right):
            continue
        if pd.isna(left) or pd.isna(right) or not isclose(
            float(left), float(right), rel_tol=0.0, abs_tol=abs_tol
        ):
            raise AssertionError(f"{name} mismatch: offline={left}, online={right}")
    for name in categorical_features:
        if offline[name] != online[name]:
            raise AssertionError(
                f"{name} mismatch: offline={offline[name]}, online={online[name]}"
            )

# Call with values for the same entity, feature-definition version, and
# logical as-of time. `pd` is imported by the project fixture/test module.
```

For the required 1,000-entity test:

1. Select 1,000 deterministic entity IDs, including sparse and high-activity entities.
2. Freeze a source snapshot and choose one `as_of` time per test case.
3. Compute offline values with the reference definition.
4. Fetch the online value for the matching materialization/version.
5. Compare numerics with a documented tolerance and categoricals exactly.
6. Report mismatch rate, absolute error distribution, missing-key rate, and feature age.
7. Fail the release if a contract threshold is breached.

A test that merely compares two copies of the same incorrect calculation is not sufficient. Add independent invariants: no future timestamps, count non-negativity, known hand-calculated fixtures, and late-event cases.

### 7.2 Debugging a mismatch

Investigate in this order:

1. Are entity keys and data types identical?
2. Are both values for the same prediction/effective timestamp?
3. Are event-time and availability-time filters identical?
4. Are window boundaries inclusive/exclusive in the same way?
5. Are nulls, missing rows, and zeros distinguished?
6. Are duplicate events and corrections handled consistently?
7. Is the online materialization stale or partially failed?
8. Are versions of transformation code and upstream data aligned?

## 8. Feature-store architecture and concepts

A **feature store** organizes feature definitions, historical/offline retrieval, and low-latency online retrieval. It can improve reuse, discoverability, consistent semantics, governance, and lineage. It does not automatically make features correct; point-in-time logic and quality contracts still belong to the engineering team.

### 8.1 Core concepts

- **Entity:** key representing a thing, such as `customer_id`.
- **Feature definition:** named transformation and semantic contract.
- **Feature view:** a logical group of features with entity keys, source, schema, and freshness expectations.
- **Offline store:** historical data, often in a warehouse/lake, used for training and analysis.
- **Online store:** low-latency latest values, often key-value storage such as Redis or DynamoDB.
- **Materialization:** publishing computed feature values from an offline/source pipeline to the online store.
- **Point-in-time retrieval:** assembling historical feature values as they were available for each training row.

A typical path:

```text
sources -> validated batch/stream computation -> offline feature history
                                           \-> materialization -> online store
training labels + prediction timestamps -> point-in-time feature retrieval
online request -> entity lookup -> online feature fetch -> request-time features
```

Offline and online stores have different access patterns. Offline storage optimizes scans and history; online storage optimizes key-based reads and availability. Online stores commonly keep latest values, not a complete historical timeline. Never assume an online lookup can reconstruct an old training row.

### 8.2 Feast: conceptual and implementation notes

Feast is an open-source feature store with concepts such as entities, feature views, offline retrieval, and online materialization. Exact APIs and supported source/store combinations vary by release. Use the official Feast documentation for the installed version before copying configuration.

A minimal conceptual feature view looks like this (illustrative; adapt source and imports to the chosen Feast version):

```python
from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float64, Int64

# data/customer_features.parquet must contain:
# customer_id, event_timestamp, created_timestamp,
# orders_30d_count, amount_30d_sum
# event_timestamp: business/effective timestamp of this feature row
# created_timestamp: when this version became available to the feature system
customer = Entity(name="customer", join_keys=["customer_id"])

source = FileSource(
    path="data/customer_features.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

customer_activity = FeatureView(
    name="customer_activity",
    entities=[customer],
    ttl=timedelta(days=90),
    schema=[
        Field(name="orders_30d_count", dtype=Int64),
        Field(name="amount_30d_sum", dtype=Float64),
    ],
    source=source,
)
```

A minimal local `feature_store.yaml` for the Feast local provider can be:

```yaml
project: customer_features
registry: data/registry.db
provider: local
online_store:
  type: sqlite
  path: data/online_store.db
```

Place the feature definition in the Feast repository, create the Parquet source with the documented columns, and run `feast apply` from that repository. Then test historical retrieval on entity rows containing `customer_id` and `event_timestamp` before materializing a bounded interval to the online store. In code, use `FeatureStore.get_historical_features(...)`, `FeatureStore.materialize(start_date, end_date)`, and `FeatureStore.get_online_features(...)` for the installed Feast version. The online store serves current eligible values; it is not a historical time-travel API. The exact feature definition and local-store configuration should be checked against the selected Feast release before running.`

This snippet is a conceptual starting point, not a universal drop-in configuration. Feast versions differ in source classes, entity/type APIs, and online-store setup. Before execution, verify the selected release's examples, configure a repository and registry, ensure the source contains entity keys and timestamps, and test offline retrieval before materialization.

A typical workflow is: define entity and feature view → configure source and registry → apply repository changes → retrieve historical features for entity/timestamp rows → materialize a bounded time range → fetch online values. From the repository directory, create the `data/` directory before applying the repo, then run `feast apply`. Example calls (after the source file exists and the repo has been applied):

```python
from datetime import datetime, timezone

import pandas as pd
from feast import FeatureStore

store = FeatureStore(repo_path=".")
entity_df = pd.DataFrame({
    "customer_id": ["c1"],
    "event_timestamp": [pd.Timestamp("2026-01-22T00:00:00Z")],
})
historical = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "customer_activity:orders_30d_count",
        "customer_activity:amount_30d_sum",
    ],
).to_df()

store.materialize(
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    end_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
)
online = store.get_online_features(
    features=[
        "customer_activity:orders_30d_count",
        "customer_activity:amount_30d_sum",
    ],
    entity_rows=[{"customer_id": "c1"}],
).to_dict()
```

Materialization generally populates the online store with latest eligible values; it is not a substitute for historical point-in-time retrieval. This example is a local integration recipe, not evidence that Feast/SQLite was executed in this environment.

### 8.3 Other offerings (awareness level)

- **Databricks Feature Engineering / Unity Catalog:** integrates feature definitions and lineage with the Databricks data/ML platform; exact capabilities depend on platform and runtime.
- **Amazon SageMaker Feature Store:** managed offline/online feature-store capability in AWS.
- **Vertex AI Feature Store:** Google's feature serving and management offerings have evolved; verify current product naming and migration guidance before designing against a specific API.
- **Snowflake feature-store capabilities:** can support feature engineering and ML workflows within the Snowflake ecosystem; validate current feature-store APIs and lifecycle.
- **Redis / DynamoDB:** possible online serving stores, but the application must define key format, TTL, consistency, schema versioning, and write/read failure behavior.

A Redis record should have an explicit entity/version key, feature schema, and freshness metadata. Use a pseudonymous internal entity key rather than putting direct PII into keys. This optional `redis-py` example illustrates an atomic write of one current feature record; it is not a substitute for an offline historical store:

```python
from datetime import datetime, timezone
from math import isfinite


def write_customer_features(
    redis_client,
    entity_key: str,  # stable pseudonymous ID, not email/phone/name
    features: dict[str, float | int],
    *,
    source_complete_through: datetime,
    ttl_seconds: int,
) -> str:
    if source_complete_through.tzinfo is None:
        raise ValueError("source_complete_through must be timezone-aware")
    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be positive")
    if not isfinite(float(features["amount_30d_sum"])):
        raise ValueError("refuse to publish an unknown/non-finite amount sum")
    key = f"feature:customer_activity:v1:{entity_key}"
    payload = {
        "schema_version": "v1",
        "orders_30d_count": str(features["orders_30d_count"]),
        "amount_30d_sum": str(features["amount_30d_sum"]),
        "source_complete_through": source_complete_through.astimezone(timezone.utc).isoformat(),
        "materialized_at": datetime.now(timezone.utc).isoformat(),
    }
    # Apply the hash and TTL together so a crash cannot leave an unexpired key.
    with redis_client.pipeline(transaction=True) as pipe:
        pipe.hset(key, mapping=payload)
        pipe.expire(key, ttl_seconds)
        pipe.execute()
    return key
```

On read, treat a missing key as missing data—not as a vector of zeros—validate `schema_version`, parse the timestamps, and apply a freshness policy before serving. TTL is a retention/cleanup control; it is not a freshness SLO. Configure least-privilege Redis ACLs, TLS where appropriate, and avoid logging raw feature payloads. Add `redis` only for this optional integration; a mocked client can test key construction and schema behavior but cannot prove Redis connectivity or durability.

Do not select a feature store solely by brand. Evaluate temporal retrieval semantics, online latency, operational burden, source integration, access control, cost, portability, and observability.

## 9. Batch, streaming, and on-demand features

### 9.1 Batch features

Batch features are computed on a schedule from warehouse/lake data using SQL, dbt, Spark, or Python. They are appropriate when the prediction cadence tolerates the refresh interval: daily churn scoring, weekly risk summaries, and many recommendation workloads.

Advantages: efficient scans, easy backfills, reproducible snapshots. Trade-offs: freshness delay, potentially large recomputation, and the risk that a late partition silently leaves stale values.

### 9.2 Streaming features: rolling ten-minute event count

A streaming feature counts events in an event-time window such as the preceding ten minutes. Kafka transports events; Spark Structured Streaming or Flink can apply event-time windows and watermarks. A **watermark** expresses how long the engine retains state while waiting for late events; it is a policy, not a guarantee that later events will never arrive.

For a rolling count, define precisely:
- event-time field and timezone,
- window interval and boundary semantics,
- watermark/lateness tolerance,
- deduplication key,
- late-event correction policy,
- online-store key and update semantics,
- freshness SLO and failure alert.

A Spark Structured Streaming sketch:

```python
from pyspark.sql import functions as F

# `events` is a streaming DataFrame with customer_id, event_id, event_time.
# Configure the Kafka source, schema, checkpoint, and sink for your deployment.
deduplicated = (
    events
    .filter(
        F.col("customer_id").isNotNull()
        & F.col("event_id").isNotNull()
        & F.col("event_time").isNotNull()
    )
    .withWatermark("event_time", "2 minutes")
    # Spark 3.5+: bounded event-id deduplication within the watermark horizon.
    .dropDuplicatesWithinWatermark(["customer_id", "event_id"])
)

counts = (
    deduplicated
    .groupBy(
        F.window("event_time", "10 minutes", "1 minute"),
        F.col("customer_id"),
    )
    .agg(F.count("event_id").alias("events_10m_count"))
)
```

This requires Spark 3.5 or later for `dropDuplicatesWithinWatermark`. The watermark bounds deduplication state; it does not guarantee that every later-than-threshold event is dropped at an exact instant. If using an earlier Spark version, use a supported bounded deduplication strategy or deduplicate upstream with a durable event-id store; do not replace it with an unbounded `dropDuplicates` state.

This is a **windowed aggregate output**, not by itself a complete per-request sliding-feature service. For example, start it with a durable checkpoint and a sink/output mode supported by that sink. `update` mode can emit changed window counts only when the sink supports updates/upserts; `append` mode emits final windows after watermark finalization and is therefore delayed. A production online feature needs an idempotent upsert keyed by `(customer_id, window_start, window_end)`, a query that selects the latest valid window, and separate handling for late corrections. Verify output-mode/sink compatibility against the installed Spark version. Late events inside the watermark horizon may update state; events beyond the accepted lateness policy may be dropped or handled separately. Test the deployed behavior.

Measure freshness as:

\[
\text{source freshness age} = \text{observation time} - \text{source-complete-through timestamp}
\]

Store the source completeness/high-watermark timestamp and the online materialization timestamp as separate metadata. Here, `source_complete_through` means the source contract's latest timestamp through which data is considered complete; it is **not** the Structured Streaming event-time watermark. A streaming watermark is a state-management boundary used to handle late events, not a freshness timestamp. Measure at least (1) source freshness age and (2) feature-computation/materialization lag separately. If the source cannot provide a completeness watermark, define an explicit proxy and document its limits.

Track p50/p95/p99 age, late-event rate, processing lag, sink-write errors, missing entity keys, and watermark delay. A healthy streaming job is not enough if the online store is stale.

### 9.3 On-demand features

On-demand features are computed from request inputs plus retrieved stored features, for example:

`requested_amount / max(customer_average_amount_30d, epsilon)`

Use them when the request contributes information unavailable in advance and the computation fits the latency budget. Keep calculations deterministic and bounded. Define behavior for missing inputs, divide-by-zero, invalid values, and timeouts. Avoid expensive scans or network calls on the synchronous request path; precompute when latency or cost is unacceptable.

### 9.4 Choosing a computation mode

| Mode | Best fit | Primary trade-off |
|---|---|---|
| Batch | Scheduled scoring, high-volume offline workloads | Lower cost per row; staler values |
| Streaming | Rapidly changing events and low-latency features | Stateful complexity, late data, operational burden |
| On-demand | Request-specific calculations | Adds synchronous latency and failure dependencies |
| Hybrid | Precompute stable aggregates; compute request-specific deltas online | More components and parity testing |

## 10. Freshness, backfills, validation, and cost

### 10.1 Freshness SLOs

Define freshness per feature based on business use. Example: “For `events_10m_count`, 99% of online reads use a value whose recorded `source_complete_through` timestamp is no more than 90 seconds behind observation time.” This needs a measurable timestamp and a monitoring query—not merely a job-success status. Define how `source_complete_through` is produced and alert if that metadata itself stops advancing.

Track:
- source-to-feature lag,
- feature materialization age,
- null/missing-key rate,
- write failures and retry backlog,
- feature query latency,
- percentage of predictions using fallback values.

A feature can be fresh but wrong; freshness and correctness are separate controls.

### 10.2 Backfills

A backfill recomputes features over historical data, often after introducing a feature or correcting logic. Safe backfills require:

1. Versioned feature definitions and an explicit effective date.
2. A fixed source snapshot or recorded source versions.
3. The same event-time and availability-time rules as training/serving.
4. Idempotent writes and bounded partitions.
5. Validation on a small date range before full execution.
6. Shadow output and reconciliation against known values.
7. A controlled materialization plan; historical backfills must not overwrite current online values with stale historical records.

A historical correction should not silently rewrite the feature values that were available to an old prediction unless the intended dataset explicitly represents corrected truth rather than online history.

### 10.3 Feature quality contracts

Validate at write time and monitor over time:

- **Schema:** names, types, required keys, timestamp columns.
- **Null rate:** overall and by important segment.
- **Ranges:** non-negative counts, allowed enumerations, valid timestamps.
- **Distribution:** mean/quantiles/category frequencies versus a baseline.
- **Uniqueness:** expected key/timestamp grain.
- **Freshness:** age threshold.
- **Completeness:** expected entities/partitions present.
- **Temporal invariants:** no event or availability time after prediction time.
- **Parity:** offline and online values agree under equivalent snapshots.

Example local quality checks (define `AMOUNT_SUM_MUST_BE_NONNEGATIVE` from the feature's approved business contract; do not hard-code this for net-spend features):

```python
import pandas as pd

AMOUNT_SUM_MUST_BE_NONNEGATIVE = False

def validate_customer_features(df):
    required = {
        "customer_id", "orders_30d_count", "amount_30d_sum",
        "feature_timestamp",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    if df["customer_id"].isna().any():
        raise ValueError("customer_id must not be null")
    if df["feature_timestamp"].isna().any():
        raise ValueError("feature_timestamp must not be null")
    if not isinstance(df["feature_timestamp"].dtype, pd.DatetimeTZDtype):
        raise TypeError("feature_timestamp must be timezone-aware")
    if (df["orders_30d_count"].dropna() < 0).any():
        raise ValueError("orders_30d_count cannot be negative")
    # Enable this only if the business definition excludes refunds/chargebacks.
    # A net-spend feature may legitimately be negative.
    if AMOUNT_SUM_MUST_BE_NONNEGATIVE and (df["amount_30d_sum"].dropna() < 0).any():
        raise ValueError("amount_30d_sum cannot be negative under this contract")
    if df["customer_id"].duplicated().any():
        raise ValueError("expected one current feature row per customer")
```

The last assertion is correct only for a current-state table. A historical feature table should instead enforce its declared composite grain, such as `(customer_id, feature_timestamp)`. This example checks that `feature_timestamp` is present and timezone-aware; source-completeness checks remain a separate upstream gate before interpreting zero counts as true no-activity.

Distribution checks should account for expected seasonality and segments; a statistical difference is an alert signal, not automatically a defect. Use severity levels, thresholds, and an owner/runbook to prevent alert fatigue.

### 10.4 Cost control

Cost levers include partition pruning, incremental computation, reusable aggregates, retention policies, limiting online materialization to features used by latency-sensitive models, and measuring feature read/write volume. Avoid rescanning all raw events for each entity request. Monitor both compute cost and online-store cardinality/storage.

## 11. Governance, lineage, PII, ownership, and deprecation

Features are production data products. Each important feature should have:

- an accountable owner and escalation route,
- a definition, unit, entity key, time semantics, null policy, and examples,
- source-to-feature lineage and downstream model/consumer references,
- freshness and quality objectives,
- schema/version history,
- access policy and retention classification,
- deprecation and migration plan.

**PII and sensitive data:** minimize collection, avoid exposing raw identifiers when pseudonymous keys suffice, restrict access, encrypt in transit/at rest, apply retention/deletion requirements, and audit reads. Derived features can still be sensitive even when direct identifiers are removed. Model training and derived feature stores must follow applicable deletion and consent requirements.

Deprecate safely: announce the feature version change, measure consumers, publish a replacement, run both versions where needed, compare values and model impact, migrate consumers, and remove the old feature only after owner sign-off. Do not mutate a feature's meaning in place while retaining the same name.

Lineage should connect:

```text
source table/topic -> transformation code/version -> feature view/table
 -> materialization run -> model training dataset/version -> model version
 -> prediction/consumer
```

This enables incident diagnosis, impact analysis, and reproducibility.

## 12. Embeddings and features for LLM/RAG systems

An embedding is a vector representation produced by an embedding model. It can be treated as a feature, but its meaning depends on the embedding model, input preprocessing, dimensions, and version.

A document-embedding pipeline typically performs: source extraction → normalization/chunking → embedding generation → vector-store write with metadata and source identifiers. A RAG retriever then uses query embeddings to find relevant chunks. Feature-engineering concerns include:
- source-document version and update/delete propagation,
- embedding model and preprocessing version,
- chunking strategy and metadata schema,
- access-control filtering before retrieval,
- stale vectors and duplicate chunks,
- embedding dimension compatibility,
- re-embedding cost and incremental backfills.

A vector store is optimized for similarity search; it is not a substitute for a governed feature store or a transactional source of truth. Keep lineage to the source content and ensure deleted/restricted content is removed from derived indexes as required.

## 13. End-to-end hands-on project

### Exercise A — Point-in-time 30-day aggregates

Use the `features_as_of` function from Section 4. Extend it to generate label rows for multiple customers and monthly prediction times. Add:
- 7/30/90-day count, sum, and average,
- recency/frequency/monetary features,
- explicit empty-window and missing-source behavior,
- a test proving future events and late-arriving events are excluded.

Required invariants:

```python
baseline = features_as_of(events, customer_id, as_of)
mutated = events.copy()
mutated.loc[len(mutated)] = {
    "customer_id": customer_id,
    "event_id": "future-event",
    "event_time": as_of + pd.Timedelta(days=1),
    "available_at": as_of + pd.Timedelta(days=1),
    "amount": 999.0,
}
mutated.loc[len(mutated)] = {
    "customer_id": customer_id,
    "event_id": "late-event",
    "event_time": as_of - pd.Timedelta(days=1),
    "available_at": as_of + pd.Timedelta(days=2),
    "amount": 888.0,
}
after_mutation = features_as_of(mutated, customer_id, as_of)
for name, expected in baseline.items():
    actual = after_mutation[name]
    if pd.isna(expected):
        assert pd.isna(actual), name
    else:
        assert actual == expected, name
```

For a stronger test, compute features once, then append an event with `event_time > as_of`; the historical feature result must remain unchanged. Append an event with old event time but `available_at > as_of`; it must also remain unchanged.

### Exercise B — Deliberately leaky feature

Create a feature `orders_next_30d_count` that counts events in `(prediction_time, prediction_time + 30 days]`. This feature is invalid because it uses information from after the prediction. The following deterministic demonstration deliberately defines the label from future activity so the leakage is obvious; it is a teaching fixture, not a realistic estimate of production AUC.

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

rng = np.random.default_rng(42)
n = 600
rows = pd.DataFrame({
    "prediction_time": pd.date_range("2025-01-01", periods=n, freq="D", tz="UTC"),
    "past_orders_30d_count": rng.poisson(2.0, n),
    "orders_next_30d_count": rng.poisson(1.0, n),
})
# Intentionally artificial: the target is defined using a future-only field.
rows["churn_next_30d"] = (rows["orders_next_30d_count"] == 0).astype(int)
cut = int(n * 0.7)
train, test = rows.iloc[:cut], rows.iloc[cut:]

def temporal_auc(feature: str) -> float:
    model = LogisticRegression(random_state=42)
    model.fit(train[[feature]], train["churn_next_30d"])
    return float(roc_auc_score(
        test["churn_next_30d"], model.predict_proba(test[[feature]])[:, 1]
    ))

leaky_auc = temporal_auc("orders_next_30d_count")
valid_auc = temporal_auc("past_orders_30d_count")
assert leaky_auc > 0.99  # because the synthetic label is directly defined from this field
assert leaky_auc > valid_auc
print({"leaky_auc": leaky_auc, "past_only_auc": valid_auc})
```

The temporal holdout prevents random mixing of dates, but it cannot repair a leaked feature: the future field still exists in both training and test rows. The required control is the point-in-time feature contract plus a test that verifies every source timestamp used by a feature is no later than `prediction_time`. Record the observed metric difference, but do not generalize the synthetic score to real data.

### Exercise C — Feature store

Start with a local Parquet or file source containing:

`customer_id`, `event_timestamp`, `orders_30d_count`, `amount_30d_sum`.

1. Validate schema and key/timestamp grain.
2. Retrieve historical values for entity/timestamp rows using point-in-time semantics.
3. Configure Feast for the version you install.
4. Apply the feature repository.
5. Retrieve offline features for training examples.
6. Materialize a bounded time interval to the configured online store.
7. Fetch online values for known entity keys.
8. Document what history the online store does and does not retain.

For Redis-backed online storage, run Redis locally or use a test double for unit tests. Do not call a mock-based test proof that the real Redis integration works.

### Exercise D — Parity for 1,000 entities

Generate at least 1,000 stable entity IDs and a deterministic source snapshot. For each entity:
- compute offline features at a chosen effective timestamp,
- fetch the corresponding online value or the versioned value represented by that timestamp,
- compare counts exactly and floating-point values with a documented tolerance,
- capture missing keys, mismatches, and feature age.

Release gate example: `mismatch_rate == 0` for deterministic numeric/count features on a frozen fixture; for approximate or independently implemented calculations, set a justified tolerance. Do not weaken the gate to hide systematic differences.

### Exercise E — Kafka ten-minute feature

Optional infrastructure exercise:
1. Run Kafka and create a topic with `customer_id`, unique `event_id`, and UTC `event_time`.
2. Generate events with controlled delay and duplicates.
3. Use Spark Structured Streaming or Flink to compute event-time ten-minute counts.
4. Configure checkpointing and a sink with idempotent upserts.
5. Send an event within the watermark delay and another beyond it; observe and document behavior.
6. Materialize the latest valid feature to an online store.
7. Measure source-to-online feature age and late-event rates.
8. Test restart/replay and duplicate handling.

For a low-cost local path, simulate windows with the pandas event fixture first. The local simulation validates logic, not Kafka delivery semantics or streaming recovery.

### Exercise F — Quality gate

Add schema, null-rate, range, distribution, uniqueness, freshness, and point-in-time checks to the pipeline. Include a test that intentionally violates each contract and confirms the job fails with a useful error. Run checks before materialization and block publication on critical violations.

## 14. Troubleshooting and common mistakes

| Symptom | Likely cause | First investigation |
|---|---|---|
| Offline metric implausibly high | Future data, label leakage, post-outcome field | Trace each feature's maximum source availability time |
| Online value differs from offline | Different null/window/timezone/rounding semantics | Recompute one entity at a frozen timestamp |
| Online values stale | Materialization lag or failed writes | Compare source watermark, job checkpoint, and stored timestamp |
| Counts unexpectedly high | Duplicate events or inclusive boundary mismatch | Check event IDs, dedupe key, and window endpoints |
| Historical rows change on rerun | Mutable sources, unpinned snapshot, late corrections | Record source version and availability-time policy |
| Missing values interpreted as zero | Incomplete partitions mistaken for no activity | Check source completeness and watermark |
| Backfill corrupts online values | Historical rows overwrote current materialization | Separate historical backfill from latest-state publishing |
| Streaming count misses late events | Watermark/lateness policy or sink semantics | Inspect event time, watermark, late-event counters |
| Feature schema change breaks model | Unversioned contract mutation | Compare feature schema/model signature and roll back |
| Alerts fire every day | Baseline ignores seasonality or segment variation | Inspect expected seasonal patterns and alert thresholds |

### 15-item churn feature review

For a task predicting cancellation in the next 30 days, classify each candidate relative to a prediction time before cancellation:

1. Number of logins in prior 7 days — valid if availability rules are enforced.
2. Number of orders in prior 30 days — valid if point-in-time correct.
3. Total spend in prior 90 days — valid if historical window is correct.
4. Days since last successful login — valid if login history is available.
5. Current subscription plan as of prediction time — valid with as-of state.
6. Customer tenure as of prediction time — valid.
7. Support tickets opened in prior 30 days — valid if ticket timestamps/availability are correct.
8. Failed payments before prediction time — valid.
9. Cancellation reason — leaky if recorded after cancellation.
10. Days since cancellation — leaky/post-outcome.
11. Refund issued after cancellation — leaky if after prediction time.
12. Future orders in next 30 days — leaky.
13. Today's lifetime spend joined to historical rows — leaky for old prediction times.
14. Customer segment calculated using the full dataset including future behavior — may leak.
15. A source field populated only after a churn investigation — likely leaky; inspect data lineage and availability.

Validity is determined by the prediction contract and availability timestamps, not by the feature's name alone.

## 15. Practice questions and exercises

1. Why is `event_time <= prediction_time` necessary but sometimes insufficient?
2. Explain the difference between no events and missing source data.
3. Why is an as-of join not equivalent to a rolling 30-day sum?
4. What does a watermark guarantee, and what does it not guarantee?
5. When would batch features be preferable to streaming features?
6. Describe three causes of training–serving skew and how to test each.
7. Why might an online feature store be unable to reproduce an old training row?
8. Design a feature freshness SLO with a measurable timestamp.
9. How should a historical correction affect replayed training features?
10. Explain why changing feature meaning without changing its name is dangerous.
11. What metadata is needed to reproduce an embedding feature?
12. Draw the source-to-feature-to-model lineage for `orders_30d_count`.
13. Implement an as-of join with a 14-day tolerance and test unmatched rows.
14. Add a test that detects duplicate events before aggregation.
15. Define a rollout and rollback plan for `orders_30d_count_v2`.

## 16. Completion checklist

- [ ] Define features in terms of entity, timestamp, meaning, source, and null policy.
- [ ] Implement scaling, encoding, bucketing, log transforms, date parts, text/count, and aggregate feature patterns as appropriate.
- [ ] Compute 7/30/90-day aggregates and RFM features.
- [ ] Build point-in-time-correct historical features.
- [ ] Demonstrate and detect feature/label leakage.
- [ ] Explain as-of joins in pandas, DuckDB, Polars, Snowflake, and Spark SQL, including engine differences.
- [ ] Detect training–serving skew with meaningful parity tests.
- [ ] Explain offline/online stores, entities, feature views, and materialization.
- [ ] Build a local feature-store example and understand Feast's versioned configuration.
- [ ] Explain batch, streaming, and on-demand feature paths.
- [ ] Design a rolling ten-minute streaming feature with event-time and late-data handling.
- [ ] Define freshness SLOs, backfill controls, quality gates, and cost controls.
- [ ] Document ownership, lineage, PII, retention, and deprecation.
- [ ] Explain embeddings/vector stores as a feature pipeline use case.

## 17. Authoritative documentation

Check current versions and platform-specific details before production implementation:

- pandas `merge_asof`: https://pandas.pydata.org/docs/reference/api/pandas.merge_asof.html
- DuckDB `ASOF JOIN`: https://duckdb.org/docs/current/sql/query_syntax/from and https://duckdb.org/docs/lts/guides/sql_features/asof_join
- Polars `join_asof`: https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.join_asof.html
- Polars `join_asof`: https://docs.pola.rs/
- Snowflake `ASOF JOIN`: https://docs.snowflake.com/en/sql-reference/constructs/asof-join
- Apache Spark Structured Streaming: https://spark.apache.org/docs/3.5.8/structured-streaming-programming-guide.html
- Apache Flink event time and watermarks: https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/event-time/
- PySpark `dropDuplicatesWithinWatermark`: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.dropDuplicatesWithinWatermark.html
- Feast quickstart: https://docs.feast.dev/getting-started/quickstart
- Feast feature views: https://docs.feast.dev/getting-started/concepts/feature-view
- Databricks Feature Engineering: https://docs.databricks.com/
- Amazon SageMaker Feature Store: https://docs.aws.amazon.com/sagemaker/
- Vertex AI Feature Store documentation: https://cloud.google.com/vertex-ai/docs
- Redis documentation: https://redis.io/docs/
- Amazon DynamoDB documentation: https://docs.aws.amazon.com/amazondynamodb/
- Great Expectations: https://docs.greatexpectations.io/
- OpenTelemetry concepts for pipeline observability: https://opentelemetry.io/docs/

Documentation and APIs evolve. In particular, validate Feast source/type configuration, Snowflake and Polars temporal join syntax, and Spark streaming output-mode/sink compatibility against the exact versions deployed.

---

## Engineering principle to retain

A production feature is not just a calculated column. It is a versioned, time-defined data product with a known owner, source lineage, quality contract, freshness objective, serving path, and reproducible behavior. If you cannot answer **what was known, for which entity, at what time, under which definition**, the feature is not yet trustworthy for historical ML.
