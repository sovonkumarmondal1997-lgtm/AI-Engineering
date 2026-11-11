# Time-Series Analysis and Forecasting Basics

> **Audience:** Data engineers and analytics engineers moving from reliable temporal data to trustworthy forecasts.  
> **Scope:** Stage 2C, `09-Analytics-Foundations-for-Data-Engineers`, Topic 06. This lesson builds on descriptive statistics and inference, and prepares for BI, visualization, and data storytelling. It does not replace a dedicated forecasting or causal-inference course.

## 1. Title and learning objectives

By the end, you should be able to:

- distinguish trend, seasonal patterns, longer cycles, and noise;
- create a complete, correctly indexed time series despite missing observations, time zones, and daylight-saving transitions;
- interpret additive/multiplicative decomposition, STL, stationarity, differencing, ACF, and PACF;
- establish naive, seasonal-naive, moving-average, and Holt–Winters baselines;
- evaluate models with chronological holdouts and rolling-origin backtests using MAE, RMSE, MAPE, sMAPE, and MASE;
- separate business forecasting from pipeline-anomaly detection;
- design a reproducible forecast pipeline with lag/holiday features, versioned predictions, scheduled backtests, and error monitoring;
- identify leakage, immature evidence, intervention effects, and inappropriate model comparisons.

## 2. Why Data Engineers need time-series fundamentals

A time series is an ordered set of observations indexed by time. Data engineering determines whether the sequence is meaningful before a model sees it: event time versus ingestion time, duplicate events, delayed data, missing partitions, changing schemas, time-zone policy, and reproducible historical snapshots can all alter the apparent signal.

Typical questions include:

- **Business forecast:** How many orders should operations expect next week, and how uncertain is that forecast?
- **Capacity forecast:** What volume will a pipeline or service receive over the next 30 days?
- **Anomaly detection:** Is today's row count unusually low relative to the expected weekday pattern?
- **Causal intervention:** Did a campaign change outcomes relative to a credible counterfactual? A forecast alone does not establish causality.

Forecasting and anomaly detection are related but distinct. Forecasting estimates future values conditional on information available at forecast time. Anomaly detection flags observations that are surprising under an expected-data model. A low row count may mean a real business decline, a late upstream partition, or a broken ingestion job; alert routing should distinguish these possibilities.

## 3. Prerequisites and environment setup

The lab uses Python, pandas, NumPy, Matplotlib, scikit-learn, and statsmodels. Use a pinned environment in a real project; API details can vary by version.

```bash
python -m pip install numpy pandas matplotlib scikit-learn statsmodels
```

The code is designed for Python 3.10+ and current stable versions of these libraries. It uses `statsmodels.tsa.seasonal.STL` and `statsmodels.tsa.holtwinters.ExponentialSmoothing`.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
```

The later lab is a self-contained script. No live external data is required. Synthetic results are illustrative; do not present them as measured business performance.

## 4. Time-series data and temporal correctness

### 4.1 Define the series contract first

A series should have a declared:

- **Entity/key:** for example, `store_id`, `sku_id`, `pipeline_name`, or the single series `daily_orders`;
- **event/measurement time:** when the business event happened or the metric applies;
- **frequency:** daily, hourly, weekly, etc.;
- **calendar and timezone:** UTC for stored instants, with a named business timezone for business-day boundaries when needed;
- **aggregation rule:** sum, count, average, end-of-period snapshot, distinct entities, or another explicit measure;
- **completeness policy:** when a date is considered final, how late data is handled, and whether absent rows mean zero or unknown;
- **revision policy:** whether past values can change after corrections and how forecasts are versioned.

For event data, store timestamps as timezone-aware instants (usually UTC). Convert to a declared business timezone before deriving a local business date. Do not strip timezone information and assume local timestamps are UTC. A local day can contain 23 or 25 hours around daylight-saving transitions; that is expected. UTC hourly grids avoid duplicated/nonexistent local clock hours, while business reporting may still require local-day aggregation.

### 4.2 Missing timestamps are not automatically zero

A missing row can mean zero activity, delayed ingestion, a failed partition, an outage, or a source that did not report. Decide from source semantics:

- If the feed is complete and absence truly means no events, reindex to a complete grid and fill the measure with zero.
- If the feed is incomplete or missingness is unknown, preserve a missing value and raise a data-quality signal. Filling with zero would fabricate a business collapse.
- Keep an `is_observed` or `is_imputed` flag so models and consumers can distinguish observed from filled values.

### 4.3 Resampling to a fixed grid

For a timestamped event stream, first choose the timezone and bucket boundary, then aggregate to the target frequency. In pandas, `resample('D')` uses the index timezone and its day boundaries; set the index and timezone intentionally. For a UTC series:

```python
# events: columns event_ts, order_id. delivery_status has one row per UTC day
# with columns bucket_date (UTC midnight) and is_complete (source SLA/watermark check).
events['event_ts'] = pd.to_datetime(events['event_ts'], utc=True)
counts = (events.set_index('event_ts')
          .resample('D').agg(orders=('order_id', 'nunique'),
                             source_rows=('order_id', 'size')))
# delivery_status defines the full expected monitoring grid, including leading/trailing gaps.
status = delivery_status.set_index('bucket_date').sort_index()  # UTC-midnight index, unique by contract
expected_days = status.index
daily = counts.reindex(expected_days)
daily['source_rows'] = daily['source_rows'].fillna(0).astype('int64')
daily['orders'] = daily['orders'].fillna(0)
daily['is_complete'] = status['is_complete']
# Missing/false completeness means unknown; zero is trusted only for confirmed-complete buckets.
daily.loc[daily['is_complete'].ne(True).fillna(True), 'orders'] = np.nan
daily['has_event_rows'] = daily['source_rows'].gt(0)
```

If the source is a complete event log but there are no rows on a date, `nunique` yields zero after reindexing to a full date range. If source delivery is incomplete, build the expected grid separately and join a delivery-completeness table rather than treating all absent buckets as zero.

### 4.4 Rolling and expanding windows

A rolling mean uses a fixed-width trailing window; an expanding mean uses all observations available so far. They are useful for smoothing and monitoring, but they lag abrupt changes and must not include future observations in historical features.

```python
series.rolling(window=7, min_periods=7).mean()  # trailing 7 observed grid rows
series.expanding(min_periods=7).mean()          # all rows from the beginning
```

These are seven rows, not necessarily seven calendar days if the index is irregular. Reindex first when calendar-day meaning is required. `center=True` uses observations on both sides and is generally inappropriate for real-time features because it leaks future data.

### 4.5 Week-over-week and year-over-year

For daily data, `yesterday` is often `shift(1)`, week-over-week is `shift(7)` only when the series is daily and aligned, and year-over-year comparisons need a calendar-aware policy. `shift(365)` is not the same as “same calendar day last year” across leap years. Prefer a calendar join on business date and an explicit rule for Feb 29 and retail calendars. Compare like-for-like weekday or trading-day positions when appropriate.

## 5. Trend, seasonality, and decomposition

### 5.1 Components

A useful conceptual model is:

\[
y_t = T_t + S_t + R_t\]

for additive components, where trend `T` changes slowly, seasonality `S` repeats with a known calendar period, and residual `R` contains irregular variation and unexplained structure. Cycles are recurring movements without a fixed, stable period; noise is unpredictable variation at the chosen resolution. Real series may also contain level shifts, holidays, promotions, outages, and measurement changes.

Daily orders may have a weekly pattern (period 7), yearly seasonality (roughly 365.242 days, with calendar effects), and holiday spikes. Hourly service traffic may have daily and weekly seasonality. Do not assume one seasonal period captures every pattern.

### 5.2 Additive versus multiplicative

- **Additive:** seasonal amplitude is approximately constant in absolute units: `y = trend + seasonality + residual`.
- **Multiplicative:** seasonal swings scale with the series level: `y = trend × seasonality × residual`, usually requiring positive values. A log transform converts multiplicative relationships into additive ones approximately.

Use additive decomposition when a Monday effect is roughly +100 orders at both low and high levels; consider multiplicative when the same weekday is consistently about 15% above baseline. Zero or negative values make direct multiplicative decomposition problematic.

### 5.3 STL decomposition

STL (Seasonal-Trend decomposition using LOESS) estimates smooth trend and seasonal components. It is flexible and robust variants can reduce outlier influence, but decomposition is descriptive, not a forecast by itself. The chosen period and smoothing parameters matter; edge estimates are less stable and multiple seasonalities need additional methods.

```python
stl = STL(daily_orders.asfreq('D'), period=7, robust=True).fit()
stl.trend       # estimated trend
stl.seasonal    # estimated weekly component
stl.resid       # remainder
```

Input must be regularly spaced and handle missingness deliberately. Do not silently interpolate an outage and then claim the imputed values were observed. For a series with yearly seasonality, enough history is required to estimate it credibly; one annual cycle is weak evidence for a stable yearly pattern.

## 6. Stationarity, differencing, ACF, and PACF

### 6.1 Stationarity

A weakly stationary process has stable mean and variance over time and autocovariance that depends on lag rather than calendar time. Trend, changing variance, structural breaks, and seasonality often violate this assumption. Many classical ARMA-style models are formulated for stationary series, while ARIMA applies differencing to help make the series stationary.

Stationarity is a modelling property, not a guarantee that the business process is stable forever. A stationarity test can have low power, and a structural break can make one test window misleading.

### 6.2 Differencing

First differencing is `Δy_t = y_t - y_(t-1)`. Seasonal differencing is `y_t - y_(t-s)` for seasonal period `s`. Differencing can remove a stochastic trend or seasonal persistence, but over-differencing amplifies noise and complicates interpretation. Never difference merely because a library accepts it; inspect the series and evaluate out of sample.

### 6.3 ACF and PACF

- **ACF:** correlation between observations separated by lag `k`, including indirect relationships through shorter lags.
- **PACF:** correlation at lag `k` after accounting for intermediate lags.

ACF/PACF plots can guide ARIMA order selection: an AR process often has a PACF cutoff-like pattern; an MA process often has an ACF cutoff-like pattern. Real data rarely match textbook patterns perfectly. Use these as diagnostics and candidate-generation aids, then select using chronological backtesting rather than a plot alone.

```python
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
plot_acf(series.dropna(), lags=28)
plot_pacf(series.dropna(), lags=28, method='ywm')
```

## 7. Forecasting baselines

Every advanced model must be compared against baselines evaluated on the same forecast origins and horizons.

| Method | How it forecasts | Useful when | Main limitation |
|---|---|---|---|
| Naive | Every future value equals the latest observed value | Random-walk-like level, short horizon | Ignores seasonality and trend |
| Seasonal naive | Repeats the value from the same season last cycle (`y[t-s]`) | Stable weekly/yearly seasonal series | Cannot adapt quickly to trend or changing seasonality |
| Moving average | Uses a trailing average, often repeated across horizon | Noisy, slowly changing level | Lags trend; flat multi-step path |
| Holt–Winters | Exponential smoothing of level, trend, and optionally seasonality | Regular series with stable trend/seasonal structure | Sensitive to configuration, history length, outliers, and structural changes |
| Lag-feature regression/boosting | Predicts from past lags and calendar/features | Nonlinear effects, holidays, many related series | Leakage risk; recursive/direct strategy and future-known features must be explicit |
| ARIMA/SARIMA | Autoregressive and moving-average terms on differenced series, with seasonal extensions | Autocorrelated regular series | Order selection and maintenance; exogenous variables need careful handling |

A baseline can be the best production choice if it is accurate enough, cheap, explainable, and robust. Model choice depends on the data and operational constraints, not a universal ranking.

## 8. Evaluation and backtesting

### 8.1 Define the evaluation contract

Before training, state:

- forecast origin time and data cutoff;
- horizon (for this lesson: 14 days);
- frequency (daily);
- target definition and timezone;
- backtest origins and evaluation dates;
- whether future-known covariates (calendar/holidays) are permitted;
- how incomplete target periods and revisions are excluded or handled.

A single chronological holdout is a minimum. Rolling-origin backtesting repeatedly trains only on history available at each origin and evaluates the next horizon. It reveals how performance changes across seasons and regimes. Do not randomly split rows from a time series: it leaks temporal structure and evaluates a deployment scenario that cannot occur.

### 8.2 Metrics

For actuals `y_i` and forecasts `ŷ_i`:

- **MAE:** `mean(|y - ŷ|)`. Easy to interpret in target units; robust to outliers compared with squared error.
- **RMSE:** `sqrt(mean((y - ŷ)^2))`. Penalizes large misses more strongly.
- **MAPE:** `mean(|(y - ŷ)/y|) × 100%`. Undefined at zero and unstable near zero; exclude-zero policies can bias comparisons.
- **sMAPE:** commonly `mean(2|y-ŷ|/(|y|+|ŷ|)) × 100%`. Still has edge cases when both values are zero and is not a universal cure for MAPE's problems. Some literature uses slightly different denominators; document the convention.
- **MASE:** MAE divided by the in-sample naive seasonal scaling error. For seasonal period `s`, scale is `mean(|y_t-y_(t-s)|)` computed from training data only. MASE below 1 means better than the corresponding seasonal-naive in-sample scale, not automatically better than every test-period seasonal-naive forecast.

When the MASE denominator is zero (constant training series), MASE is undefined; report `NaN` and use MAE/other appropriate metrics. Never calculate the scale using test observations.

### 8.3 Prediction intervals

A prediction interval describes uncertainty about a future observation under a model and its assumptions. It is not a guaranteed bound and can be miscalibrated after structural change, unusual promotions, or distribution shift. Prophet-style models provide trend/seasonality forecasts and interval estimates, but intervals depend on model specification and uncertainty assumptions; validate empirical coverage on rolling backtests.

## 9. Anomaly detection

### 9.1 Residual-based detection

Fit an expected-value model using only information available before the observation. Define residual `e_t = y_t - ŷ_t`. A simple detector flags a point when the absolute residual exceeds `k × robust_scale`, where robust scale may be `1.4826 × MAD` (median absolute deviation around the residual median). The scale should be estimated from a historical calibration window and not include the point being scored. A fixed threshold such as 3 is a starting heuristic, not a universal false-positive guarantee.

### 9.2 Seasonal thresholds

Compare Monday with historical Mondays, or use a forecast interval conditioned on weekday, holidays, and known operating schedules. A global threshold often flags normal weekly peaks as anomalies. For low-volume count series, Gaussian residual assumptions may be poor; consider count models or empirical quantiles.

### 9.3 Business anomalies versus pipeline anomalies

A business series can genuinely drop. A pipeline row-count series can drop because the source was late, a partition was skipped, a schema changed, or the upstream business volume fell. Monitor both:

- **data health:** source freshness, partition completeness, row counts, duplicate rate, null rate, schema drift;
- **business signal:** observed orders versus a forecast conditional on calendar and business drivers.

Correlate alerts with lineage, ingestion lag, and upstream SLA state before automatically labelling a business anomaly.

## 10. Advanced methods and forecasting-platform awareness

### 10.1 ARIMA/SARIMA

ARIMA(p,d,q) combines autoregressive terms (`p`), differencing (`d`), and moving-average error terms (`q`). SARIMA adds seasonal terms `(P,D,Q,s)`. It can model serial dependence but does not automatically understand holidays, promotions, or business causes. Compare candidate orders with simple baselines and rolling-origin metrics; fit only on data available at each origin.

### 10.2 Feature-based and global models

Gradient-boosted trees can use lag features, rolling statistics, day-of-week, month, holiday, price, promotion, and known future covariates. Every lag/rolling feature must be shifted so it contains only observations available at prediction time. A target-derived rolling average should use `shift(1).rolling(...)`, not a window including the target row.

For many series (store/SKU/country), **local models** fit one model per series; **global models** learn shared patterns across series and can help sparse series borrow strength. Hierarchical forecasts must reconcile totals and children when coherent reporting is required. Evaluate by series and aggregate; a high-volume series can dominate an overall score and hide poor performance for small groups.

### 10.3 Holiday and intervention effects

Holiday calendars, promotions, stock-outs, price changes, outages, and product launches may change the data-generating process. Add known future features only when those features really are known at forecast time. Promotions planned after the forecast origin are leakage. One observed holiday spike is not enough to estimate a stable holiday effect. Avoid tuning to one season and calling it generalization.

### 10.4 Tool awareness and caveats

- **statsforecast:** efficient statistical forecasting across many series; confirm model support, input schema, frequency, and package version.
- **Prophet:** trend, seasonality, holidays, and interval-oriented workflow; not automatically superior and can struggle with sparse data or abrupt regime shifts.
- **BigQuery ML `ARIMA_PLUS`:** managed in-warehouse time-series forecasting with preprocessing and model-specific features. Check current Google Cloud documentation for supported options, automatic adjustments, limitations, pricing, and region availability before relying on them.
- **Snowflake forecasting capabilities:** product names, SQL APIs, and supported features change. Confirm the current Snowflake documentation, edition/region availability, permissions, and cost model.
- **Databricks AI functions / forecasting features:** capabilities depend on the current Databricks product surface, runtime, and workspace. Verify the exact API and availability instead of assuming an “AI function” provides a specific forecasting estimator.

These are awareness-level options, not endorsements. Managed services reduce operational burden but do not eliminate the need for correct time grains, backtests, leakage controls, data quality, versioning, and ownership.

### 10.5 Causal impact awareness

A forecast is not a causal effect. Intervention analysis asks what would have happened without a campaign, outage, policy, or product change. Difference-in-differences, synthetic control, or Bayesian structural time-series/causal-impact approaches construct a counterfactual under assumptions about controls, pre-intervention fit, and absence of confounding changes. A holiday spike in a time series alone does not identify the holiday's causal effect.

## 11. Forecast pipeline architecture and monitoring

A production pipeline commonly has these stages:

1. **Ingest and validate:** land event/metric records with event time, ingestion time, source ID, and schema version.
2. **Canonicalize time:** convert instants to UTC, apply named business calendars for aggregates, deduplicate by source event key, and document lateness.
3. **Build the grid:** aggregate to one row per series key and frequency bucket; keep missingness/completeness indicators.
4. **Create features:** lags, rolling features, calendar/holiday variables, and exogenous variables with point-in-time correctness.
5. **Backtest and select:** scheduled rolling-origin evaluation against baselines; record code/config/data snapshot and metrics.
6. **Fit and forecast:** train at a declared cutoff and generate a fixed horizon.
7. **Persist immutable forecast versions:** write `forecast_run_id`, model/version, created time, origin, target timestamp, horizon, point forecast, lower/upper interval, and feature/data snapshot IDs.
8. **Score later:** join actuals only when mature, retain the forecast vintage used at the time, and calculate error by horizon and series.
9. **Monitor:** freshness, missing buckets, row counts, feature drift, forecast error, interval coverage, model runtime, and cost.

### 11.1 Example storage contract

| Table | Grain / key | Important fields |
|---|---|---|
| `fact_daily_metric` | one row per `series_id, metric_date` | actual value, observed flag, source watermark, revision/version |
| `forecast_runs` | one row per `forecast_run_id` | model name/version, code version, training cutoff, frequency, horizon, feature snapshot, created_at |
| `forecast_values` | one row per `forecast_run_id, series_id, target_ts` | point forecast, lower/upper interval, target time, horizon |
| `forecast_backtest_metrics` | one row per run/model/series/horizon/window | MAE, RMSE, MASE, sample count, metric version |
| `forecast_actual_scores` | one row per forecast vintage and target key | actual revision used, absolute error, signed error, scored_at |
| `pipeline_health_metrics` | one row per pipeline and bucket | input/output rows, freshness lag, null/duplicate rates, status |

Use immutable run IDs. If actuals are revised, either preserve score vintages or explicitly rescore with a revision identifier. Never overwrite the original forecast and thereby erase what the system knew at decision time.

## 12. End-to-end hands-on lab

This lab creates 800 days of synthetic daily orders. The true process contains linear trend, weekly seasonality, random noise, and a known intervention spike. The generated series is not meant to mimic a particular business. The final 56 days are held out; rolling-origin evaluation uses 14-day horizons and 28-day origin steps. The model comparison must use the same origins and target dates.

Save the following as `time_series_lab.py` and run it. It prints metrics; this document does not claim specific accuracy values from an execution.

```python
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

SEED = 20261019
HORIZON = 14
SEASON = 7
rng = np.random.default_rng(SEED)

# 1) Synthetic data-generating process: known components and intervention.
n = 800
dates = pd.date_range('2024-01-01', periods=n, freq='D', tz='UTC')
t = np.arange(n)
weekly_pattern = np.array([-18, -12, -5, 2, 8, 25, 10], dtype=float)  # Mon..Sun-like fixed 7-day cycle
weekly = weekly_pattern[t % 7]
trend = 120 + 0.12 * t
noise = rng.normal(0, 8, n)
intervention_day = 620
intervention = np.zeros(n)
intervention[intervention_day:intervention_day + 3] = [55, 35, 15]
orders = np.maximum(0, np.round(trend + weekly + noise + intervention)).astype(float)
series = pd.Series(orders, index=dates, name='orders').asfreq('D')
assert series.index.is_monotonic_increasing and series.index.is_unique
assert series.notna().all() and len(series) == n

# 2) Plot series and STL components. Period=7 targets weekly seasonality.
fig, ax = plt.subplots(figsize=(12, 4))
series.plot(ax=ax, title='Synthetic daily orders: trend + weekly seasonality + noise + intervention')
ax.axvline(dates[intervention_day], linestyle='--', label='intervention begins')
ax.legend(); plt.tight_layout(); plt.show()
stl = STL(series, period=7, robust=True).fit()
fig = stl.plot(); fig.set_size_inches(12, 7); plt.tight_layout(); plt.show()

# 3) Metric definitions. MASE scale is calculated from training data only.
def metric_row(y_true, y_pred, train, season=SEASON):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    train = np.asarray(train, dtype=float)
    if y_true.ndim != 1 or y_pred.ndim != 1 or len(y_true) == 0 or len(y_true) != len(y_pred):
        raise ValueError('y_true and y_pred must be non-empty 1D arrays of equal length')
    if not np.isfinite(y_true).all() or not np.isfinite(y_pred).all():
        raise ValueError('Evaluation actuals and predictions must be finite; resolve missing values first')
    if train.ndim != 1 or len(train) == 0 or not np.isfinite(train).all():
        raise ValueError('Training history for metric scaling must be a non-empty finite 1D array')
    if season < 1:
        raise ValueError('season must be a positive integer')
    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    nonzero = np.abs(y_true) > 1e-12
    mape = float(np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100) if nonzero.any() else np.nan
    denom = np.abs(y_true) + np.abs(y_pred)
    smape_terms = np.divide(2 * np.abs(y_true - y_pred), denom,
                            out=np.zeros_like(denom), where=denom > 1e-12)
    smape = float(np.mean(smape_terms) * 100)
    scale = float(np.mean(np.abs(train[season:] - train[:-season]))) if len(train) > season else np.nan
    mase = float(mae / scale) if np.isfinite(scale) and scale > 1e-12 else np.nan
    return {'MAE': float(mae), 'RMSE': rmse, 'MAPE_pct_nonzero_actuals': mape,
            'sMAPE_pct': smape, 'MASE': mase}

def naive_forecast(train, horizon):
    return np.repeat(float(train.iloc[-1]), horizon)

def seasonal_naive_forecast(train, horizon, season=SEASON):
    if len(train) < season:
        raise ValueError('Need at least one complete seasonal cycle')
    return np.resize(train.iloc[-season:].to_numpy(dtype=float), horizon)

def moving_average_forecast(train, horizon, window=7):
    if len(train) < window:
        raise ValueError('Training history shorter than moving-average window')
    return np.repeat(float(train.iloc[-window:].mean()), horizon)

def hw_forecast(train, horizon):
    model = ExponentialSmoothing(train, trend='add', seasonal='add',
                                 seasonal_periods=SEASON,
                                 initialization_method='estimated')
    return np.asarray(model.fit(optimized=True).forecast(horizon), dtype=float)

def make_lag_frame(s):
    # All predictors are from prior observations; target is the current day's value.
    frame = pd.DataFrame(index=s.index)
    frame['lag_1'] = s.shift(1)
    frame['lag_7'] = s.shift(7)
    frame['lag_14'] = s.shift(14)
    frame['mean_prev_7'] = s.shift(1).rolling(7).mean()
    frame['dow'] = s.index.dayofweek
    frame['day_of_year_sin'] = np.sin(2 * np.pi * s.index.dayofyear / 365.25)
    frame['day_of_year_cos'] = np.cos(2 * np.pi * s.index.dayofyear / 365.25)
    frame['target'] = s
    return frame.dropna()

def lag_feature_forecast(train, horizon, seed=SEED):
    # Recursive multi-step forecast: each future lag uses predictions, never held-out actuals.
    frame = make_lag_frame(train)
    features = ['lag_1', 'lag_7', 'lag_14', 'mean_prev_7', 'dow', 'day_of_year_sin', 'day_of_year_cos']
    model = HistGradientBoostingRegressor(max_iter=100, max_leaf_nodes=15,
                                          learning_rate=0.06, l2_regularization=1.0,
                                          random_state=seed)
    model.fit(frame[features], frame['target'])
    history = train.copy()
    preds = []
    for _ in range(horizon):
        ts = history.index[-1] + pd.Timedelta(days=1)
        x = pd.DataFrame([{
            'lag_1': history.iloc[-1], 'lag_7': history.iloc[-7],
            'lag_14': history.iloc[-14], 'mean_prev_7': history.iloc[-7:].mean(),
            'dow': ts.dayofweek,
            'day_of_year_sin': np.sin(2 * np.pi * ts.dayofyear / 365.25),
            'day_of_year_cos': np.cos(2 * np.pi * ts.dayofyear / 365.25),
        }], columns=features)
        pred = float(model.predict(x)[0])
        preds.append(pred)
        history.loc[ts] = pred
    return np.asarray(preds)

FORECASTERS = {
    'naive': naive_forecast,
    'seasonal_naive': seasonal_naive_forecast,
    'moving_average_7': moving_average_forecast,
    'holt_winters': hw_forecast,
    'lag_feature_recursive': lag_feature_forecast,
}

# 4) Rolling-origin backtest. At every origin, train only on data before origin.
def rolling_origin_backtest(s, forecasters, horizon=HORIZON, initial_train=500, step=28):
    rows = []
    # Require a complete horizon and avoid evaluating beyond the series.
    for origin in range(initial_train, len(s) - horizon + 1, step):
        train = s.iloc[:origin]
        test = s.iloc[origin:origin + horizon]
        for name, fn in forecasters.items():
            pred = fn(train, horizon)
            assert len(pred) == len(test)
            assert np.isfinite(pred).all()
            metrics = metric_row(test.to_numpy(), pred, train.to_numpy())
            rows.append({'model': name, 'origin': s.index[origin],
                         'train_end': train.index[-1], 'test_start': test.index[0],
                         'test_end': test.index[-1], 'n_test': len(test), **metrics})
    return pd.DataFrame(rows)

# Hold out the final 56 days as a final untouched evaluation window.
train_dev = series.iloc[:-56]
final_test = series.iloc[-56:]
backtest = rolling_origin_backtest(train_dev, FORECASTERS, horizon=HORIZON,
                                   initial_train=500, step=28)
summary = backtest.groupby('model')[['MAE', 'RMSE', 'MASE']].mean().sort_values('MAE')
print('\nRolling-origin mean metrics (per-origin scores averaged):')
print(summary.to_string())

# Choose a model by backtest MAE only; final test remains untouched until this point.
chosen_name = summary.index[0]
chosen_fn = FORECASTERS[chosen_name]
final_pred = chosen_fn(train_dev, len(final_test))
final_metrics = metric_row(final_test.to_numpy(), final_pred, train_dev.to_numpy())
print(f'\nSelected using rolling backtest only: {chosen_name}')
print('Final 56-day holdout metrics:', final_metrics)

# 5) Residual anomaly detector: use one-step seasonal-naive errors on pre-intervention data
# to establish a robust historical threshold; score the entire series retrospectively only
# for demonstration. In production, score each point using a model trained before it.
seasonal_one_step = series.shift(SEASON)
residual = series - seasonal_one_step
calibration = residual.iloc[SEASON:intervention_day]
med = float(calibration.median())
mad = float(np.median(np.abs(calibration.to_numpy() - med)))
robust_sigma = 1.4826 * mad
threshold = 3.0 * robust_sigma
if threshold <= 0:
    raise ValueError('Residual calibration scale is zero; use a fallback or count model')
flags = (residual - med).abs() > threshold
print('\nLargest residual flags (date, observed, residual):')
print(pd.DataFrame({'observed': series, 'residual': residual, 'flag': flags})
      .loc[flags].head(10).to_string())

# 6) Separate pipeline-health example: expected daily row counts with weekday pattern,
# a synthetic missing-load incident, and a one-day spike. This is not business forecasting.
pipeline_rng = np.random.default_rng(SEED + 1)
pipe_dates = pd.date_range('2026-01-01', periods=120, freq='D', tz='UTC')
pipe_expected = 10000 + np.array([0, 100, -50, 80, 30, -200, -300])[np.arange(120) % 7]
pipe_rows = np.maximum(0, pipe_expected + pipeline_rng.normal(0, 90, 120)).round().astype(int)
pipe_rows[95] = 3500  # deliberately injected ingestion failure
pipe_rows[108] = 16000  # deliberate spike
pipe = pd.Series(pipe_rows, index=pipe_dates, name='rows_written')
pipe_baseline = pipe.shift(7)
pipe_resid = pipe - pipe_baseline
pipe_cal = pipe_resid.iloc[7:90]
pipe_med = float(pipe_cal.median())
pipe_mad = float(np.median(np.abs(pipe_cal.to_numpy() - pipe_med)))
pipe_sigma = 1.4826 * pipe_mad
pipe_flags = (pipe_resid - pipe_med).abs() > 3 * pipe_sigma
assert bool(pipe_flags.iloc[95]), 'Injected row-count drop should be detected by seasonal residual threshold'
print('\nPipeline anomaly candidates:')
print(pd.DataFrame({'rows_written': pipe, 'seasonal_residual': pipe_resid,
                    'anomaly': pipe_flags}).loc[pipe_flags].to_string())

# 7) A small scheduled-run storage example. In production, persist transactionally to a table.
# The immutable run ID is based on model/config/code version + forecast origin, not current time.
forecast_origin = train_dev.index[-1]
run_id = f'orders-v1-{forecast_origin.strftime("%Y%m%d")}-h{len(final_test)}'
forecast_table = pd.DataFrame({
    'forecast_run_id': run_id,
    'model_name': chosen_name,
    'forecast_origin': forecast_origin,
    'target_ts': final_test.index,
    'horizon_step': np.arange(1, len(final_test) + 1),
    'yhat': final_pred,
})
print('\nForecast output sample:')
print(forecast_table.head().to_string(index=False))

# 8) Tests of data contract, no leakage in lag features, and metric properties.
assert series.index.tz is not None
assert (make_lag_frame(series)['lag_1'] == series.shift(1).reindex(make_lag_frame(series).index)).all()
assert metric_row([10, 20], [10, 20], [1, 2, 3, 4, 5, 6, 7, 8])['MAE'] == 0
assert np.isfinite(metric_row([10, 20], [11, 18], np.arange(1, 20))['MASE'])
assert backtest.groupby('model').size().nunique() == 1, 'All models must use identical backtest origin counts'
origin_sets = {name: tuple(group['origin']) for name, group in backtest.groupby('model')}
assert len(set(origin_sets.values())) == 1, 'All models must use exactly the same origins'
assert (backtest['train_end'] < backtest['test_start']).all()
assert (backtest['n_test'] == HORIZON).all()
assert (backtest['test_end'] - backtest['test_start']).eq(pd.Timedelta(days=HORIZON - 1)).all()
assert len(forecast_table) == len(final_test) and forecast_table['target_ts'].is_unique
# Edge-case tests: all-zero actuals make MAPE undefined; constant training history makes MASE undefined.
zero_actual_metrics = metric_row([0, 0], [0, 1], [0, 0, 0, 0, 0, 0, 0, 0])
assert np.isnan(zero_actual_metrics['MAPE_pct_nonzero_actuals'])
assert np.isnan(zero_actual_metrics['MASE'])
try:
    metric_row([1, np.nan], [1, 2], [1, 2, 3, 4, 5, 6, 7, 8])
except ValueError:
    pass
else:
    raise AssertionError('Non-finite evaluation inputs must be rejected')
print('\nAll lab assertions passed.')
```

### 12.1 Interpret the lab correctly

- The trend and weekly pattern are planted by construction; noise is random but reproducible under the fixed seed and library versions.
- The three-day intervention is deliberately unusual. STL may distribute some of its effect across trend and residual; decomposition is not a causal estimator.
- Every rolling origin has the same horizon for every model. The lag-feature model predicts recursively: after the first future day, its own prediction becomes a lag. It never uses actual future target values.
- The final 56 days are not used to select the model. After choosing from rolling-origin MAE, evaluate once on that final window.
- MAPE is reported only over nonzero actual values; the output names that convention. sMAPE defines a zero/zero term as zero. MASE scale is computed from training history only.
- Residual flags are candidates for investigation, not proof of cause. The pipeline-health example deliberately injects a row-count failure and asserts that it is flagged. The business-series detector uses a seasonal-naive reference and a pre-intervention calibration window for illustration.
- A fixed seed makes the generator reproducible in a fixed software environment, but exact model scores can change with package versions and implementation changes.

## 13. Tests and validation

A production forecasting pipeline should test at least:

1. **Temporal contract:** timezone-aware timestamps, unique series/time key, monotonic ordering, expected frequency, explicit duplicate policy.
2. **Grid completeness:** missing buckets are counted and classified; no silent conversion of unknown to zero.
3. **Leakage:** each feature's maximum source timestamp is no later than the forecast origin; training labels are strictly before the origin.
4. **Backtest fairness:** same origins, horizon, target, and scoring rules across candidate models; baselines are included.
5. **Metric edge cases:** all-zero actuals, zero MASE scale, negative forecasts, near-zero actuals, and missing predictions have documented behavior.
6. **Forecast schema:** one row per run/series/target timestamp; finite point forecasts; interval lower ≤ upper if intervals are emitted.
7. **Versioning:** rerunning an identical run is idempotent; a new model/code/data snapshot creates a new run version.
8. **Delayed actuals:** do not score a target until its data is mature under the source SLA; preserve actual revision IDs.
9. **Anomaly calibration:** threshold is fitted without using the point being scored; measure false-alert rate on historical periods and inspect seasonal segments.
10. **Operational SLOs:** runtime, freshness, completeness, failure retries, and cost are monitored separately from forecast accuracy.

Example SQL-like integrity check for a warehouse table:

```sql
-- Generic SQL; adapt date/time and QUALIFY syntax to your warehouse.
SELECT series_id, target_ts, COUNT(*) AS n
FROM forecast_values
WHERE forecast_run_id = :run_id
GROUP BY series_id, target_ts
HAVING COUNT(*) <> 1;
```

This query should return no rows. A second check should compare expected series × horizon rows to actual persisted rows; counts alone do not prove the values are correct.

## 14. Exercises with solutions

### Exercise 1 — Choose the baseline

A daily metric has a stable weekday pattern and modest trend. Which baseline should you try first?

**Solution:** Seasonal naive with period 7, compared with naive and a trend/seasonal smoothing model. Evaluate all at the same origins and horizon. If seasonal naive is already strong, any more complex model must demonstrate repeatable out-of-sample improvement.

### Exercise 2 — Missing day

An order-count table has no row for Tuesday. Should you fill it with zero?

**Solution:** Only if source completeness is confirmed and no events means zero orders. If ingestion was delayed or a partition failed, mark the value unknown, monitor freshness, and avoid training as if the zero were observed.

### Exercise 3 — Leakage review

A feature table computes `rolling(7).mean()` on the target series and joins it to the same date's target.

**Solution:** It includes the current target and leaks information. Use `series.shift(1).rolling(7).mean()` for a one-step-ahead feature, and verify point-in-time availability at each forecast origin.

### Exercise 4 — MAPE near zero

A series contains values `[0, 1, 100]`. Why is MAPE a poor sole metric?

**Solution:** Division by zero makes the first term undefined; the value 1 can dominate percentage error. Report MAE/RMSE and a scale-based metric such as MASE when its scale is defined, and document any MAPE exclusion policy.

### Exercise 5 — Forecast versus causal effect

Orders rise immediately after a marketing campaign. Does a time-series forecast establish campaign lift?

**Solution:** No. It measures deviation from a predictive baseline. A causal claim needs a credible counterfactual design and assumptions, such as a suitable control series, difference-in-differences, or synthetic control.

### Exercise 6 — Production row-count alert

A pipeline's Monday count is 30% lower than Sunday. Is that anomalous?

**Solution:** Not necessarily. Compare with expected Mondays, the source freshness watermark, upstream partition status, and the pipeline's historical weekday distribution. Alert on evidence of a data-quality failure separately from a legitimate business shift.

## 15. Common mistakes and production failure modes

- Randomly splitting time-series rows into train and test.
- Comparing a 1-day naive forecast with a 14-day model forecast.
- Using a rolling window that includes the target or future values.
- Treating missing rows as zero without source-completeness evidence.
- Aggregating local business dates in UTC or dropping timezone offsets.
- Ignoring daylight-saving transitions in hourly local-time series.
- Reporting MAPE when actuals include zero or values near zero without a policy.
- Computing MASE's scale from the test set or comparing scales across incompatible series without care.
- Tuning on the final holdout repeatedly until it is no longer a holdout.
- Fitting yearly seasonality from too little history or overfitting one holiday/season.
- Treating a forecast interval as a guarantee.
- Confusing a business decline with an ingestion failure.
- Overwriting old forecasts and losing the vintage available to decision-makers.
- Scoring immature target dates before late data arrives.
- Optimizing aggregate metrics while hiding poor accuracy on low-volume series.
- Assuming managed forecasting platforms remove the need for validation, lineage, and monitoring.

## 16. Knowledge checkpoint

You should be able to answer without looking up the earlier sections:

1. What is the difference between trend, seasonality, cycle, and noise?
2. Why can a missing date not always be filled with zero?
3. When is additive decomposition preferable to multiplicative decomposition?
4. What does differencing do, and what is over-differencing?
5. How do ACF and PACF differ?
6. Why must a seasonal-naive baseline be included for weekly data?
7. What information is available at a rolling forecast origin?
8. Why is MAPE unstable near zero, and how is MASE scaled?
9. Why are forecast intervals not guaranteed bounds?
10. How would you distinguish a real order-volume drop from a pipeline outage?
11. What makes a lag feature leak future information?
12. What belongs in a versioned forecast record?

## 17. Final competency checklist

- [ ] I can define the series key, frequency, timezone, aggregation, and completeness contract.
- [ ] I can build a fixed temporal grid without silently inventing zeros.
- [ ] I can explain trend, seasonal patterns, cycles, noise, STL, stationarity, differencing, ACF, and PACF.
- [ ] I can implement naive, seasonal-naive, moving-average, Holt–Winters, and lag-feature forecasts.
- [ ] I can run chronological rolling-origin backtests with a fixed horizon and fair model comparisons.
- [ ] I can interpret MAE, RMSE, MAPE, sMAPE, and MASE, including edge cases.
- [ ] I can separate forecast residual anomalies from pipeline-health incidents.
- [ ] I can prevent future-data leakage and handle known-future calendar features responsibly.
- [ ] I can design versioned forecast storage, delayed scoring, and idempotent scheduled runs.
- [ ] I can state the assumptions and limits of an intervention/causal-impact analysis.

## 18. Authoritative references

1. Hyndman, R. J., & Athanasopoulos, G. *Forecasting: Principles and Practice* (3rd ed.), free online textbook: <https://otexts.com/fpp3/>. Covers time-series features, decomposition, ARIMA, forecast accuracy, and hierarchical forecasting.
2. `statsmodels` time-series analysis documentation: <https://www.statsmodels.org/stable/tsa.html>.
3. `statsmodels` STL documentation: <https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html>.
4. `statsmodels` Holt–Winters `ExponentialSmoothing` documentation: <https://www.statsmodels.org/stable/generated/statsmodels.tsa.holtwinters.ExponentialSmoothing.html>.
5. pandas time-series / date functionality: <https://pandas.pydata.org/docs/user_guide/timeseries.html>.
6. Google Cloud BigQuery ML time-series forecasting (`ARIMA_PLUS`): <https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-create-time-series>.
7. Snowflake documentation: <https://docs.snowflake.com/>; consult current forecasting/ML documentation for product and API details.
8. Databricks documentation: <https://docs.databricks.com/>; consult current AI/ML and forecasting capabilities for workspace/runtime-specific support.
9. Makridakis, S., Spiliotis, E., & Assimakopoulos, V. “The M5 accuracy competition: Results, findings, and conclusions.” *International Journal of Forecasting* (2022), for large-scale retail forecasting and evaluation considerations.
10. Bernal, J. L., Cummins, S., & Gasparrini, A. “Interrupted time series regression for the evaluation of public health interventions: a tutorial.” *International Journal of Epidemiology* (2017), for intervention-analysis assumptions and design.

**Scope boundary:** This lesson teaches fundamentals and production hygiene. Deep ARIMA identification, advanced probabilistic forecasting, hierarchical reconciliation, and causal inference warrant dedicated follow-on study.
