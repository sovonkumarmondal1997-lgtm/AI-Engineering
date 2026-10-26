# Time and Anomaly Modeling — ML Specialization Roadmap

**Group 5 (G5)** of the specialization that follows Stage 5D of the [Roadmap](./Roadmap.md). It covers original categories **10 Time-Series Forecasting and 13 Anomaly Detection Engineering**. The group's defining question is: *what happens next, and what is abnormal in a data stream?* It follows G1 to G4: [`01_Classical and Applied ML.md`](./01_Classical%20and%20Applied%20ML.md), [`02_Deep Learning by Modality.md`](./02_Deep%20Learning%20by%20Modality.md), [`03_Generative and Foundation Models.md`](./03_Generative%20and%20Foundation%20Models.md), [`04_Agents and Sequential Decisions.md`](./04_Agents%20and%20Sequential%20Decisions.md).

## G5 summary

| Item | Count |
|---|---|
| Modules (including overview and capstones) | 17 |
| Lesson files | 139 |
| Hands-on project files (module projects, overview project and capstones) | 51 |
| Folders inside the G5 tree | 33 |
| Files inside the G5 tree | 230 |

| Original category | Modules |
|---|---|
| 10 Time-Series Forecasting | 01 to 10 |
| 13 Anomaly Detection Engineering | 11 to 14 |
| Shared operations for both | 15 |

## Scope and how G5 avoids repeating the Roadmap

G5 starts where Stage 5B stops. These are **already learned** and are only referenced, never retaught: trend, seasonality and residuals, naive and seasonal-naive baselines, lag features and rolling statistics, forecast horizons (recursive vs direct), autoregression and moving-average intuition, ARIMA and SARIMA concepts, exponential smoothing and Prophet-style models, regression and gradient boosting for forecasting, global and hierarchical forecasting basics, probabilistic forecasting and intervals, rolling-origin backtesting and basic forecast metrics, missing timestamps, intermittent demand and drift (Stage 5B); anomaly, outlier and novelty definitions, statistical and distance-based detection, isolation forest, LOF, one-class SVM, density and reconstruction-based methods, thresholding with scarce labels and alert quality (Stage 5B); split conformal prediction and conformalized quantile regression (Stage 5B); the introduction to hidden Markov models and Kalman filters (Stage 5B elective); recurrent networks and deep learning for time series and tabular data (Stage 5C); time-aware validation (Stage 5A); event-time processing, watermarks and streaming engines (Stage 2C); and drift monitoring, alerts, runbooks and retraining policy for deployed models (Stage 5D).

**Boundaries with other groups** (so nothing overlaps): Bayesian and Gaussian-process uncertainty and causal impact analysis belong to **G7**; graph-based and spatio-temporal anomaly and forecasting methods belong to **G8**; fraud, predictive maintenance, financial and geospatial domain applications belong to **G9**; model compression and low-latency inference belong to **G10**; MLOps platform design belongs to **G11**; general benchmark design belongs to **G13**; image and sequence models are used as in **G2**.

| Roadmap topic already covered | Where G5 goes further |
|---|---|
| Lag features, horizons, backtesting, basic metrics (5B) | Module 01: data layouts, covariate legality, leakage tests, scaled and probabilistic metrics and statistical comparison |
| ARIMA, SARIMA, exponential smoothing concepts (5B) | Module 02: stationarity tests, diagnostics, MSTL, SARIMAX, TBATS, VAR and GARCH |
| Kalman filter and HMM introduction (5B elective) | Module 03: state-space models, Kalman filter from scratch, structural models and regime switching |
| GBDT forecasting, global and hierarchical basics (5B) | Module 04: reconciliation methods, cold start, intermittent demand, censored demand and scaling |
| Deep learning for time series introduction (5C) | Modules 05 and 06: modern deep forecasters, honest benchmarking and time-series foundation models |
| Probabilistic forecasting and conformal prediction (5B) | Module 07: adaptive conformal inference, scenario generation and decision-making under uncertainty |
| Intermittent demand and drift (5B), watermarks (2C) | Modules 08 and 10: planning applications, changepoint detection and online learning |
| Anomaly detection methods and alert quality (5B) | Modules 11 to 13: time-series evaluation rigor, forecast-based and SPC detectors and deep detectors |
| Reconstruction-based detection (5B, 5C), image models (5C) | Module 14: visual anomaly detection, log and event-sequence anomalies |
| Drift monitoring, alerts and retraining (5D) | Module 15: forecast pipelines, forecast monitoring, alert grouping and root-cause help |

## G5 — Time and Anomaly Modeling

**Defining question:** What happens next, and what is abnormal in a data stream?

```text
ML Specialization/
└── G5 — Time and Anomaly Modeling/
    ├── 00-G5-Overview/
    │   ├── Projects/
    │   │   ├── 01-g5-time-series-environment-and-benchmark-bootstrap.md
    │   │   └── README.md
    │   ├── 01-g5-scope-and-boundaries-with-stage-5b-and-other-groups.md
    │   ├── 02-prerequisite-map-from-the-roadmap.md
    │   ├── 03-dataset-and-tooling-register.md
    │   ├── 04-evaluation-and-reporting-standards.md
    │   ├── 05-completion-gate.md
    │   ├── README.md
    │   └── learning-plan.md
    ├── 01-Forecast-Data-Layout-Covariates-and-Evaluation-Suites/
    │   ├── Projects/
    │   │   ├── 01-forecast-data-contract-and-leakage-tests.md
    │   │   ├── 02-metric-suite-and-metric-failure-demonstration.md
    │   │   ├── 03-benchmark-protocol-with-statistical-comparison.md
    │   │   └── README.md
    │   ├── 01-timestamps-at-scale.md
    │   ├── 02-panel-layouts.md
    │   ├── 03-covariates.md
    │   ├── 04-leakage-patterns-specific-to-forecasting.md
    │   ├── 05-scaled-and-relative-metrics.md
    │   ├── 06-probabilistic-metrics.md
    │   ├── 07-evaluation-across-many-series.md
    │   ├── 08-forecast-value-added.md
    │   ├── 09-comparing-forecasting-methods-statistically.md
    │   ├── 10-benchmark-datasets.md
    │   └── README.md
    ├── 02-Classical-Statistical-Forecasting-in-Depth/
    │   ├── Projects/
    │   │   ├── 01-box-jenkins-by-hand-vs-auto-selection.md
    │   │   ├── 02-multi-seasonality-forecasting.md
    │   │   ├── 03-garch-volatility-forecast-evaluation.md
    │   │   └── README.md
    │   ├── 01-stationarity-testing-and-the-box-jenkins-workflow.md
    │   ├── 02-residual-diagnostics.md
    │   ├── 03-stl-and-mstl-decomposition-for-multiple-seasonalities.md
    │   ├── 04-ets-in-state-space-form.md
    │   ├── 05-regression-with-arima-errors.md
    │   ├── 06-automatic-model-selection-at-scale-with-statsforecast.md
    │   ├── 07-the-theta-method-and-tbats.md
    │   ├── 08-vector-autoregression-and-cointegration-for-related-series.md
    │   ├── 09-volatility-models.md
    │   ├── 10-ensembles-of-statistical-models-and-why-simple-combinations-are-hard-to-beat.md
    │   └── README.md
    ├── 03-State-Space-Models-and-Kalman-Filtering/
    │   ├── Projects/
    │   │   ├── 01-kalman-filter-from-scratch.md
    │   │   ├── 02-structural-model-with-missing-data.md
    │   │   ├── 03-regime-switching-detection-study.md
    │   │   └── README.md
    │   ├── 01-state-space-formulation.md
    │   ├── 02-local-level-and-local-linear-trend-models.md
    │   ├── 03-the-kalman-filter-from-scratch.md
    │   ├── 04-smoothing.md
    │   ├── 05-parameter-estimation.md
    │   ├── 06-missing-observations-and-irregular-spacing-handled-by-the-filter.md
    │   ├── 07-structural-time-series.md
    │   ├── 08-time-varying-regression-coefficients-and-dynamic-linear-models.md
    │   ├── 09-nonlinear-and-non-gaussian-filtering.md
    │   ├── 10-regime-switching-models.md
    │   └── README.md
    ├── 04-Machine-Learning-Forecasting-at-Scale/
    │   ├── Projects/
    │   │   ├── 01-m5-style-global-forecasting-pipeline.md
    │   │   ├── 02-hierarchical-reconciliation-study.md
    │   │   ├── 03-intermittent-demand-benchmark.md
    │   │   └── README.md
    │   ├── 01-feature-design-for-global-models.md
    │   ├── 02-multi-horizon-strategies.md
    │   ├── 03-tooling.md
    │   ├── 04-hierarchical-reconciliation-methods.md
    │   ├── 05-cold-start.md
    │   ├── 06-intermittent-and-lumpy-demand.md
    │   ├── 07-promotions-price-and-cannibalization-effects.md
    │   ├── 08-censored-demand.md
    │   ├── 09-training-on-millions-of-series.md
    │   ├── 10-error-analysis-for-forecasts.md
    │   └── README.md
    ├── 05-Deep-Learning-Forecasting-Architectures/
    │   ├── Projects/
    │   │   ├── 01-deep-vs-statistical-vs-gbdt-benchmark.md
    │   │   ├── 02-temporal-fusion-transformer-with-covariates.md
    │   │   ├── 03-long-horizon-benchmark-audit.md
    │   │   └── README.md
    │   ├── 01-deep-forecasting-landscape-and-the-case-for-strong-statistical-baselines.md
    │   ├── 02-probabilistic-autoregressive-models.md
    │   ├── 03-residual-stack-models.md
    │   ├── 04-attention-based-models.md
    │   ├── 05-patch-and-channel-designs.md
    │   ├── 06-linear-baselines-that-challenge-transformers.md
    │   ├── 07-training-protocol.md
    │   ├── 08-tooling.md
    │   ├── 09-honest-benchmarking.md
    │   ├── 10-when-deep-models-win.md
    │   └── README.md
    ├── 06-Time-Series-Foundation-Models/
    │   ├── Projects/
    │   │   ├── 01-zero-shot-foundation-model-bakeoff.md
    │   │   ├── 02-fine-tuning-vs-zero-shot-study.md
    │   │   ├── 03-licence-and-cost-review.md
    │   │   └── README.md
    │   ├── 01-what-time-series-foundation-models-are.md
    │   ├── 02-the-main-families.md
    │   ├── 03-zero-shot-evaluation-protocol.md
    │   ├── 04-fine-tuning-and-adapting-pretrained-forecasters.md
    │   ├── 05-covariates-and-multivariate-series-in-foundation-models.md
    │   ├── 06-benchmarks.md
    │   ├── 07-cost-latency-and-licence-considerations-for-production-use.md
    │   ├── 08-decision-guide.md
    │   └── README.md
    ├── 07-Probabilistic-Forecasting-and-Decision-Making/
    │   ├── Projects/
    │   │   ├── 01-adaptive-conformal-intervals-under-drift.md
    │   │   ├── 02-newsvendor-with-probabilistic-forecasts.md
    │   │   ├── 03-scenario-generation-for-capacity-planning.md
    │   │   └── README.md
    │   ├── 01-distributional-forecasts.md
    │   ├── 02-calibration-of-forecast-intervals-over-time.md
    │   ├── 03-conformal-prediction-for-time-series.md
    │   ├── 04-quantile-crossing-post-processing-and-monotone-quantile-fixes.md
    │   ├── 05-scenario-generation-and-path-forecasts.md
    │   ├── 06-probabilistic-hierarchical-forecasts-and-reconciliation.md
    │   ├── 07-decisions-under-forecast-uncertainty.md
    │   ├── 08-evaluating-decisions.md
    │   └── README.md
    ├── 08-Demand-and-Planning-Applications/
    │   ├── Projects/
    │   │   ├── 01-indian-festival-calendar-feature-set.md
    │   │   ├── 02-forecast-to-replenishment-simulation.md
    │   │   ├── 03-energy-load-forecasting-system.md
    │   │   └── README.md
    │   ├── 01-retail-and-supply-chain-demand-forecasting-end-to-end.md
    │   ├── 02-calendar-effects-for-india.md
    │   ├── 03-new-product-forecasting.md
    │   ├── 04-from-forecast-to-replenishment.md
    │   ├── 05-energy-load-and-renewable-generation-forecasting.md
    │   ├── 06-capacity-planning-for-compute-and-web-workloads.md
    │   ├── 07-workforce-and-staffing-forecasts.md
    │   ├── 08-forecasting-processes.md
    │   └── README.md
    ├── 09-Time-Series-Classification-Clustering-and-Representation/
    │   ├── Projects/
    │   │   ├── 01-tsc-benchmark-on-ucr-subset.md
    │   │   ├── 02-human-activity-recognition-pipeline.md
    │   │   ├── 03-motif-discovery-and-similarity-search.md
    │   │   └── README.md
    │   ├── 01-time-series-classification-tasks-and-benchmark-archives.md
    │   ├── 02-distance-based-methods.md
    │   ├── 03-interval-and-shapelet-methods.md
    │   ├── 04-convolutional-kernel-methods.md
    │   ├── 05-feature-based-methods.md
    │   ├── 06-deep-classifiers.md
    │   ├── 07-clustering-and-similarity-search.md
    │   ├── 08-motifs-and-discords-with-the-matrix-profile.md
    │   ├── 09-representation-learning-for-time-series.md
    │   ├── 10-human-activity-and-wearable-sensor-recognition.md
    │   └── README.md
    ├── 10-Changepoints-Regimes-and-Streaming-Models/
    │   ├── Projects/
    │   │   ├── 01-changepoint-benchmark.md
    │   │   ├── 02-online-learning-under-drift.md
    │   │   ├── 03-cusum-alarm-design.md
    │   │   └── README.md
    │   ├── 01-changepoint-problem.md
    │   ├── 02-cusum-and-page-hinkley-tests.md
    │   ├── 03-offline-segmentation.md
    │   ├── 04-bayesian-online-changepoint-detection.md
    │   ├── 05-concept-drift-detectors-for-streams.md
    │   ├── 06-online-learning-for-streams-with-the-river-library.md
    │   ├── 07-streaming-forecasting.md
    │   ├── 08-evaluating-changepoint-detection.md
    │   └── README.md
    ├── 11-Time-Series-Anomaly-Problem-Design-and-Evaluation/
    │   ├── Projects/
    │   │   ├── 01-point-adjust-metric-audit.md
    │   │   ├── 02-benchmark-triviality-analysis.md
    │   │   ├── 03-anomaly-labeling-protocol-and-agreement.md
    │   │   └── README.md
    │   ├── 01-anomaly-types-in-sequences.md
    │   ├── 02-problem-framing.md
    │   ├── 03-why-labels-are-scarce-and-noisy-and-how-to-label-time-series-anomalies.md
    │   ├── 04-range-based-precision-and-recall.md
    │   ├── 05-the-point-adjustment-trap.md
    │   ├── 06-threshold-free-and-robust-metrics.md
    │   ├── 07-benchmark-flaws.md
    │   ├── 08-benchmark-archives-and-tools.md
    │   ├── 09-synthetic-anomaly-injection.md
    │   ├── 10-cost-based-alerting.md
    │   └── README.md
    ├── 12-Statistical-and-Forecast-Based-Anomaly-Detection/
    │   ├── Projects/
    │   │   ├── 01-residual-vs-discord-vs-spc-comparison.md
    │   │   ├── 02-kpi-anomaly-detector-with-holiday-effects.md
    │   │   ├── 03-evt-threshold-study.md
    │   │   └── README.md
    │   ├── 01-residual-based-detection.md
    │   ├── 02-robust-seasonal-methods.md
    │   ├── 03-statistical-process-control.md
    │   ├── 04-matrix-profile-discords-for-subsequence-anomalies.md
    │   ├── 05-spectral-residual-and-frequency-domain-detectors.md
    │   ├── 06-multivariate-methods.md
    │   ├── 07-dynamic-thresholds-from-extreme-value-theory.md
    │   ├── 08-seasonality-and-trend-handling-so-periodic-behavior-is-not-flagged.md
    │   ├── 09-business-kpi-anomaly-detection.md
    │   └── README.md
    ├── 13-Deep-and-Self-Supervised-Anomaly-Detection/
    │   ├── Projects/
    │   │   ├── 01-deep-vs-simple-detector-benchmark.md
    │   │   ├── 02-contamination-robustness-study.md
    │   │   ├── 03-foundation-model-anomaly-scoring.md
    │   │   └── README.md
    │   ├── 01-reconstruction-based-sequence-models.md
    │   ├── 02-forecasting-based-deep-detection.md
    │   ├── 03-adversarial-and-adversarially-trained-detectors.md
    │   ├── 04-transformer-detectors-and-the-anomaly-transformer.md
    │   ├── 05-deep-one-class-methods.md
    │   ├── 06-contrastive-and-self-supervised-detectors.md
    │   ├── 07-training-on-contaminated-data.md
    │   ├── 08-foundation-model-based-detection.md
    │   ├── 09-choosing-deep-vs-simple.md
    │   └── README.md
    ├── 14-Anomaly-Detection-for-Images-Logs-and-Event-Sequences/
    │   ├── Projects/
    │   │   ├── 01-visual-defect-detection-on-mvtec-ad.md
    │   │   ├── 02-log-anomaly-detection-pipeline.md
    │   │   ├── 03-normal-data-requirements-study.md
    │   │   └── README.md
    │   ├── 01-industrial-visual-anomaly-detection.md
    │   ├── 02-feature-memory-methods.md
    │   ├── 03-reconstruction-and-student-teacher-approaches-for-images.md
    │   ├── 04-tooling-and-benchmarks.md
    │   ├── 05-evaluating-visual-anomaly-detection.md
    │   ├── 06-log-parsing.md
    │   ├── 07-sequence-based-log-anomaly-detection.md
    │   ├── 08-event-sequence-and-process-anomalies.md
    │   ├── 09-anomaly-detection-in-text-streams-and-metadata.md
    │   └── README.md
    ├── 15-Operating-Forecasting-and-Anomaly-Systems/
    │   ├── Projects/
    │   │   ├── 01-backfill-safe-forecast-pipeline.md
    │   │   ├── 02-alert-quality-and-rca-system.md
    │   │   ├── 03-forecast-monitoring-dashboard-with-retrain-triggers.md
    │   │   └── README.md
    │   ├── 01-forecast-pipelines.md
    │   ├── 02-forecast-versioning-archiving-and-reconciliation-outputs.md
    │   ├── 03-monitoring-forecasts.md
    │   ├── 04-retraining-cadence-for-forecasters-and-handling-structural-breaks.md
    │   ├── 05-scaling-to-millions-of-series.md
    │   ├── 06-alert-design.md
    │   ├── 07-root-cause-help-for-anomalies.md
    │   ├── 08-feedback-loops.md
    │   ├── 09-real-time-scoring.md
    │   ├── 10-runbooks-ownership-and-measuring-business-value-of-alerts.md
    │   └── README.md
    ├── 16-G5-Capstones/
    │   ├── 01-forecasting-system-for-a-planning-problem.md
    │   ├── 02-foundation-model-and-global-model-benchmark.md
    │   ├── 03-anomaly-detection-platform.md
    │   ├── 04-streaming-changepoint-and-forecast-monitor.md
    │   ├── 05-g5-readiness-assessment.md
    │   └── README.md
    └── README.md
```

### 00 — G5 Overview

**Purpose:** the single authoritative plan for G5 with scope, boundaries, prerequisite map, dataset and tooling register, evaluation standards and completion gate.

- `01-g5-scope-and-boundaries-with-stage-5b-and-other-groups.md` — what G5 teaches and what it leaves to other groups.
- `02-prerequisite-map-from-the-roadmap.md` — Roadmap stages and modules assumed for each G5 module.
- `03-dataset-and-tooling-register.md` — every dataset, licence and access condition, library with version and maintenance status, and model licence.
- `04-evaluation-and-reporting-standards.md` — backtest windows, scaled and probabilistic metrics, range-based anomaly metrics, seeds and report template.
- `05-completion-gate.md` — measurable criteria to finish G5.
- `learning-plan.md` — recommended order, forecasting and anomaly tracks and compute budget.

**Project 1: g5 time-series environment and benchmark bootstrap**  
- Data: one small forecasting series and one small anomaly series.  
- Task: build a reproducible workspace with pinned tooling, a backtest harness that enforces forecast-time information limits and an anomaly-evaluation harness with range-based metrics.  
- Deliverables: lockfile, both harnesses and smoke tests.  
- Pass gate: a clean machine reproduces the smoke tests from the lockfile, and a deliberately leaky feature fails the backtest harness.

### 01 — Forecast Data Layout Covariates and Evaluation Suites

**Outcome:** Prepare time-series data and measure forecasts the way forecasting practitioners do. Trend and seasonality, naive baselines, lag features, forecast horizons, rolling-origin backtesting and the basic forecast metrics are covered in Stage 5B and are not repeated.

**Lessons**

- `01-timestamps-at-scale.md` — Timestamps at scale: time zones, daylight saving, irregular sampling, resampling and alignment across sources
- `02-panel-layouts.md` — Panel layouts: long and wide formats, series identifiers and hierarchical keys
- `03-covariates.md` — Covariates: known-in-advance, observed-only and static features, and which are legal at forecast time
- `04-leakage-patterns-specific-to-forecasting.md` — Leakage patterns specific to forecasting: future covariates, rolling features and target-derived calendar effects
- `05-scaled-and-relative-metrics.md` — Scaled and relative metrics: MASE, RMSSE and why percentage errors fail
- `06-probabilistic-metrics.md` — Probabilistic metrics: pinball loss, weighted quantile loss, CRPS and interval coverage
- `07-evaluation-across-many-series.md` — Evaluation across many series: aggregation choices, per-horizon scores and per-segment breakdowns
- `08-forecast-value-added.md` — Forecast value added: proving a model beats the naive baseline in money terms
- `09-comparing-forecasting-methods-statistically.md` — Comparing forecasting methods statistically: rank-based tests and critical-difference diagrams
- `10-benchmark-datasets.md` — Benchmark datasets: M4, M5, Monash archive and their known limits

**Hands-on projects**

- **Project 1: forecast data contract and leakage tests**  
  - Data: A multi-store retail sales dataset such as Rossmann or Favorita from Kaggle (accept competition terms)  
  - Task: Build a validated panel dataset with known-future and unknown-future covariates marked, and write tests that fail when a feature uses information unavailable at forecast time.  
  - Deliverables: Data contract, loader and leakage test suite.  
  - Pass gate: A deliberately leaky feature is caught by the tests.
- **Project 2: metric suite and metric failure demonstration**  
  - Data: M4 subset and a synthetic series with known properties  
  - Task: Implement MASE, RMSSE, sMAPE, WQL and CRPS and demonstrate cases where each metric ranks models misleadingly.  
  - Deliverables: Tested metric library and demonstration notebook.  
  - Pass gate: Metrics validated against a reference implementation on fixed examples.
- **Project 3: benchmark protocol with statistical comparison**  
  - Data: Monash archive datasets  
  - Task: Compare five methods across at least 10 datasets with rank-based tests and a critical-difference diagram.  
  - Deliverables: Benchmark report.  
  - Pass gate: Identical backtest windows for every method.

### 02 — Classical Statistical Forecasting in Depth

**Outcome:** Fit, diagnose and automate statistical forecasting models. ARIMA and SARIMA concepts, exponential smoothing and Prophet-style models are introduced in Stage 5B; this module covers the diagnostics, extensions and tooling.

**Lessons**

- `01-stationarity-testing-and-the-box-jenkins-workflow.md` — Stationarity testing and the Box-Jenkins workflow: ADF and KPSS tests and differencing decisions
- `02-residual-diagnostics.md` — Residual diagnostics: autocorrelation checks, Ljung-Box and what failures mean
- `03-stl-and-mstl-decomposition-for-multiple-seasonalities.md` — STL and MSTL decomposition for multiple seasonalities
- `04-ets-in-state-space-form.md` — ETS in state-space form: model families and information-criterion selection
- `05-regression-with-arima-errors.md` — Regression with ARIMA errors: SARIMAX and dynamic harmonic regression with Fourier terms
- `06-automatic-model-selection-at-scale-with-statsforecast.md` — Automatic model selection at scale with statsforecast
- `07-the-theta-method-and-tbats.md` — The Theta method and TBATS
- `08-vector-autoregression-and-cointegration-for-related-series.md` — Vector autoregression and cointegration for related series
- `09-volatility-models.md` — Volatility models: ARCH and GARCH for variance forecasting
- `10-ensembles-of-statistical-models-and-why-simple-combinations-are-hard-to-beat.md` — Ensembles of statistical models and why simple combinations are hard to beat

**Hands-on projects**

- **Project 1: box jenkins by hand vs auto selection**  
  - Data: Several classic monthly series such as airline passengers and an electricity series  
  - Task: Fit models by hand with full diagnostics and compare with automatic selection across a rolling backtest.  
  - Deliverables: Diagnostic report and backtest comparison.  
  - Pass gate: Every model reported has residual diagnostics shown.
- **Project 2: multi seasonality forecasting**  
  - Data: Hourly electricity load or web traffic  
  - Task: Compare MSTL-based, TBATS, dynamic harmonic regression and a seasonal naive baseline.  
  - Deliverables: Comparison with horizon-wise errors.  
  - Pass gate: Strong seasonal naive baseline included.
- **Project 3: garch volatility forecast evaluation**  
  - Data: Daily returns of a public index or currency pair  
  - Task: Fit GARCH-family models and evaluate variance forecasts against realized volatility proxies.  
  - Deliverables: Evaluation with coverage of predicted ranges.  
  - Pass gate: Out-of-sample evaluation only.

### 03 — State Space Models and Kalman Filtering

**Outcome:** Model time series with latent states, handle missing data naturally and implement the filter yourself. Hidden Markov models and Kalman filters are only introduced as an elective in Stage 5B.

**Lessons**

- `01-state-space-formulation.md` — State-space formulation: observation and transition equations
- `02-local-level-and-local-linear-trend-models.md` — Local level and local linear trend models
- `03-the-kalman-filter-from-scratch.md` — The Kalman filter from scratch: predict and update steps in NumPy
- `04-smoothing.md` — Smoothing: Rauch-Tung-Striebel and using future data for estimation
- `05-parameter-estimation.md` — Parameter estimation: maximum likelihood and EM for state-space models
- `06-missing-observations-and-irregular-spacing-handled-by-the-filter.md` — Missing observations and irregular spacing handled by the filter
- `07-structural-time-series.md` — Structural time series: trend, seasonality and regression components with statsmodels UnobservedComponents
- `08-time-varying-regression-coefficients-and-dynamic-linear-models.md` — Time-varying regression coefficients and dynamic linear models
- `09-nonlinear-and-non-gaussian-filtering.md` — Nonlinear and non-Gaussian filtering: extended Kalman filter and particle filter introduction
- `10-regime-switching-models.md` — Regime-switching models: Markov-switching regression and when regimes are real

**Hands-on projects**

- **Project 1: kalman filter from scratch**  
  - Data: Simulated series with known latent states, plus a real tracking or sensor series  
  - Task: Implement the Kalman filter and smoother and verify against statsmodels.  
  - Deliverables: Tested implementation and comparison.  
  - Pass gate: Estimates match statsmodels within a stated tolerance on simulated data.
- **Project 2: structural model with missing data**  
  - Data: A real series with injected and natural gaps  
  - Task: Fit a structural model and compare against interpolation-then-ARIMA on forecast accuracy.  
  - Deliverables: Comparison across gap patterns.  
  - Pass gate: Gaps injected after a fixed seed and evaluated against held-out true values.
- **Project 3: regime switching detection study**  
  - Data: Economic or load series with known regime changes  
  - Task: Fit Markov-switching models and test whether detected regimes are stable under resampling.  
  - Deliverables: Stability analysis and honest interpretation.  
  - Pass gate: Regime stability measured, not assumed.

### 04 — Machine Learning Forecasting at Scale

**Outcome:** Forecast thousands to millions of series with global machine-learning models. Lag features, GBDT forecasting, global models and the introduction to hierarchical forecasting are covered in Stage 5B; this module covers the engineering at scale.

**Lessons**

- `01-feature-design-for-global-models.md` — Feature design for global models: lags, rolling windows, calendar, price and promotion features
- `02-multi-horizon-strategies.md` — Multi-horizon strategies: direct, recursive, multi-output and hybrid approaches
- `03-tooling.md` — Tooling: mlforecast, skforecast and Darts compared
- `04-hierarchical-reconciliation-methods.md` — Hierarchical reconciliation methods: bottom-up, top-down, MinT and its variants
- `05-cold-start.md` — Cold start: new series, new products and analog-based forecasting
- `06-intermittent-and-lumpy-demand.md` — Intermittent and lumpy demand: Croston, SBA, TSB and Tweedie-objective models
- `07-promotions-price-and-cannibalization-effects.md` — Promotions, price and cannibalization effects
- `08-censored-demand.md` — Censored demand: forecasting when stock-outs hide true demand
- `09-training-on-millions-of-series.md` — Training on millions of series: sampling, sharding and incremental retraining
- `10-error-analysis-for-forecasts.md` — Error analysis for forecasts: bias, horizon decay and worst-series review

**Hands-on projects**

- **Project 1: m5 style global forecasting pipeline**  
  - Data: M5 Forecasting dataset (Kaggle; accept terms)  
  - Task: Build a global LightGBM pipeline with hierarchical features and compare with statistical and naive baselines.  
  - Deliverables: Pipeline and per-level evaluation.  
  - Pass gate: Baselines and the official-style scaled metric included.
- **Project 2: hierarchical reconciliation study**  
  - Data: Tourism or M5 hierarchy  
  - Task: Compare unreconciled, bottom-up, top-down and MinT forecasts and quantify coherence gains.  
  - Deliverables: Reconciliation comparison.  
  - Pass gate: Accuracy reported at every hierarchy level.
- **Project 3: intermittent demand benchmark**  
  - Data: Spare-parts or slow-moving retail items  
  - Task: Compare Croston-family methods, Tweedie GBDT and zero-inflated approaches.  
  - Deliverables: Benchmark with inventory-relevant metrics.  
  - Pass gate: Stock-level metrics reported alongside forecast error.

### 05 — Deep Learning Forecasting Architectures

**Outcome:** Know what deep forecasting models do, when they win and how to benchmark them honestly. Recurrent networks and the introduction to deep learning for time series are covered in Stage 5C.

**Lessons**

- `01-deep-forecasting-landscape-and-the-case-for-strong-statistical-baselines.md` — Deep forecasting landscape and the case for strong statistical baselines
- `02-probabilistic-autoregressive-models.md` — Probabilistic autoregressive models: DeepAR
- `03-residual-stack-models.md` — Residual-stack models: N-BEATS and N-HiTS
- `04-attention-based-models.md` — Attention-based models: Temporal Fusion Transformer and variable selection
- `05-patch-and-channel-designs.md` — Patch and channel designs: PatchTST and iTransformer-style models
- `06-linear-baselines-that-challenge-transformers.md` — Linear baselines that challenge transformers: DLinear and TSMixer
- `07-training-protocol.md` — Training protocol: windowing, scaling per series, loss choice and early stopping
- `08-tooling.md` — Tooling: NeuralForecast, Darts, GluonTS and PyTorch Forecasting
- `09-honest-benchmarking.md` — Honest benchmarking: tuning budgets, datasets and leakage in common long-horizon benchmarks
- `10-when-deep-models-win.md` — When deep models win: data volume, covariate richness and horizon length

**Hands-on projects**

- **Project 1: deep vs statistical vs gbdt benchmark**  
  - Data: Three datasets of different scale, such as M4 hourly, electricity and a retail dataset  
  - Task: Compare N-HiTS, PatchTST, DLinear, a global LightGBM model and tuned statistical baselines under equal tuning budgets.  
  - Deliverables: Benchmark with confidence intervals across seeds.  
  - Pass gate: Equal tuning budgets and multiple seeds for neural models.
- **Project 2: temporal fusion transformer with covariates**  
  - Data: A retail dataset with promotions and prices  
  - Task: Train a TFT, inspect variable-selection weights and compare with a covariate-aware GBDT.  
  - Deliverables: Model, interpretation and comparison.  
  - Pass gate: Interpretation checked against ablations of the covariates.
- **Project 3: long horizon benchmark audit**  
  - Data: A common long-horizon benchmark such as ETT or Electricity  
  - Task: Reproduce published numbers, check scaling and look-ahead handling and test with a simple linear baseline.  
  - Deliverables: Audit report.  
  - Pass gate: Every deviation from the published protocol documented.

### 06 — Time Series Foundation Models

**Outcome:** Evaluate and use pretrained forecasting models without overselling them. This area changes quickly, so every lesson must be checked against current releases and licences.

**Lessons**

- `01-what-time-series-foundation-models-are.md` — What time-series foundation models are: pretraining data, tokenization and objectives
- `02-the-main-families.md` — The main families: Chronos, TimesFM, Moirai, Lag-Llama and commercial APIs such as TimeGPT
- `03-zero-shot-evaluation-protocol.md` — Zero-shot evaluation protocol: contamination, benchmark overlap and fair comparison
- `04-fine-tuning-and-adapting-pretrained-forecasters.md` — Fine-tuning and adapting pretrained forecasters
- `05-covariates-and-multivariate-series-in-foundation-models.md` — Covariates and multivariate series in foundation models
- `06-benchmarks.md` — Benchmarks: GIFT-Eval and fev-bench and what their leaderboards do not show
- `07-cost-latency-and-licence-considerations-for-production-use.md` — Cost, latency and licence considerations for production use
- `08-decision-guide.md` — Decision guide: foundation model vs statistical baseline vs trained global model

**Hands-on projects**

- **Project 1: zero shot foundation model bakeoff**  
  - Data: Five datasets not likely in pretraining, including one you collect from a public source after the models' release  
  - Task: Compare three foundation models with strong statistical and GBDT baselines in zero-shot mode.  
  - Deliverables: Bake-off with probabilistic and point metrics.  
  - Pass gate: At least one dataset postdates the models' training data.
- **Project 2: fine tuning vs zero shot study**  
  - Data: A domain series collection of your choice  
  - Task: Measure the gain from fine-tuning against zero-shot and a trained global model as history length changes.  
  - Deliverables: History-length curves.  
  - Pass gate: Same backtest windows across methods.
- **Project 3: licence and cost review**  
  - Data: The models used in the bake-off  
  - Task: Record licences, weights availability, inference cost and latency and recommend a deployment option.  
  - Deliverables: Review document.  
  - Pass gate: Every licence read from the primary source and dated.

### 07 — Probabilistic Forecasting and Decision Making

**Outcome:** Produce calibrated uncertainty for forecasts and use it to make decisions. The introduction to probabilistic forecasting and split conformal prediction are covered in Stage 5B; Bayesian uncertainty methods are covered later in G7.

**Lessons**

- `01-distributional-forecasts.md` — Distributional forecasts: parametric, quantile and sample-based outputs
- `02-calibration-of-forecast-intervals-over-time.md` — Calibration of forecast intervals over time: coverage drift and monitoring
- `03-conformal-prediction-for-time-series.md` — Conformal prediction for time series: EnbPI and adaptive conformal inference
- `04-quantile-crossing-post-processing-and-monotone-quantile-fixes.md` — Quantile crossing, post-processing and monotone quantile fixes
- `05-scenario-generation-and-path-forecasts.md` — Scenario generation and path forecasts: copulas and sample trajectories
- `06-probabilistic-hierarchical-forecasts-and-reconciliation.md` — Probabilistic hierarchical forecasts and reconciliation
- `07-decisions-under-forecast-uncertainty.md` — Decisions under forecast uncertainty: newsvendor and safety-stock policies
- `08-evaluating-decisions.md` — Evaluating decisions: cost of over- and under-forecasting

**Hands-on projects**

- **Project 1: adaptive conformal intervals under drift**  
  - Data: A series with a known level shift  
  - Task: Compare static, rolling and adaptive conformal intervals on coverage and width after the shift.  
  - Deliverables: Coverage-over-time plots.  
  - Pass gate: Coverage measured over rolling windows, not only overall.
- **Project 2: newsvendor with probabilistic forecasts**  
  - Data: A retail demand dataset with cost and price assumptions  
  - Task: Choose order quantities from point and probabilistic forecasts and compare realized cost.  
  - Deliverables: Decision-cost comparison.  
  - Pass gate: Cost assumptions stated and sensitivity analysis included.
- **Project 3: scenario generation for capacity planning**  
  - Data: A load or traffic series  
  - Task: Generate sample paths and evaluate capacity plans against the scenarios.  
  - Deliverables: Scenario set and plan evaluation.  
  - Pass gate: Paths checked for realistic temporal dependence.

### 08 — Demand and Planning Applications

**Outcome:** Apply forecasting to the recurring business planning problems, including Indian market effects.

**Lessons**

- `01-retail-and-supply-chain-demand-forecasting-end-to-end.md` — Retail and supply-chain demand forecasting end to end
- `02-calendar-effects-for-india.md` — Calendar effects for India: festival dates, regional holidays and moving events such as Diwali and Eid
- `03-new-product-forecasting.md` — New-product forecasting: analogs and attribute-based models
- `04-from-forecast-to-replenishment.md` — From forecast to replenishment: safety stock and reorder policies
- `05-energy-load-and-renewable-generation-forecasting.md` — Energy load and renewable generation forecasting
- `06-capacity-planning-for-compute-and-web-workloads.md` — Capacity planning for compute and web workloads
- `07-workforce-and-staffing-forecasts.md` — Workforce and staffing forecasts
- `08-forecasting-processes.md` — Forecasting processes: sales and operations planning, overrides and bias tracking

**Hands-on projects**

- **Project 1: indian festival calendar feature set**  
  - Data: Public holiday and festival date sources you compile and verify  
  - Task: Build a reusable calendar feature set for Indian regional festivals and measure its lift on a sales forecast.  
  - Deliverables: Calendar library and lift evaluation.  
  - Pass gate: Dates verified against at least two sources.
- **Project 2: forecast to replenishment simulation**  
  - Data: A retail dataset with lead times you assume  
  - Task: Simulate replenishment policies driven by different forecasts and compare service level and inventory cost.  
  - Deliverables: Simulation and policy comparison.  
  - Pass gate: Simulation parameters documented and varied.
- **Project 3: energy load forecasting system**  
  - Data: A public regional electricity load dataset with weather  
  - Task: Build a day-ahead load forecast with weather covariates using only forecast-time-available weather.  
  - Deliverables: Pipeline and evaluation.  
  - Pass gate: Weather inputs limited to what would be forecast at issue time.

### 09 — Time Series Classification Clustering and Representation

**Outcome:** Classify, cluster and search time series rather than forecast them.

**Lessons**

- `01-time-series-classification-tasks-and-benchmark-archives.md` — Time-series classification tasks and benchmark archives: UCR and UEA
- `02-distance-based-methods.md` — Distance-based methods: dynamic time warping and nearest neighbors
- `03-interval-and-shapelet-methods.md` — Interval and shapelet methods
- `04-convolutional-kernel-methods.md` — Convolutional kernel methods: ROCKET and MiniRocket
- `05-feature-based-methods.md` — Feature-based methods: catch22 and tsfresh with selection
- `06-deep-classifiers.md` — Deep classifiers: InceptionTime and ResNet-style models
- `07-clustering-and-similarity-search.md` — Clustering and similarity search: k-means variants, DTW barycenters and indexing
- `08-motifs-and-discords-with-the-matrix-profile.md` — Motifs and discords with the matrix profile
- `09-representation-learning-for-time-series.md` — Representation learning for time series: contrastive methods such as TS2Vec
- `10-human-activity-and-wearable-sensor-recognition.md` — Human activity and wearable sensor recognition

**Hands-on projects**

- **Project 1: tsc benchmark on ucr subset**  
  - Data: A subset of UCR archive datasets  
  - Task: Compare DTW-1NN, MiniRocket, catch22 with GBDT and InceptionTime with critical-difference analysis.  
  - Deliverables: Benchmark report.  
  - Pass gate: Predefined train-test splits respected.
- **Project 2: human activity recognition pipeline**  
  - Data: UCI HAR or PAMAP2  
  - Task: Build a sensor classifier with subject-wise splits and report the gap from random splits.  
  - Deliverables: Pipeline and leakage-gap analysis.  
  - Pass gate: Subjects never shared between train and test.
- **Project 3: motif discovery and similarity search**  
  - Data: A long sensor or ECG-like recording from a public dataset  
  - Task: Find motifs and discords with the matrix profile and build a similarity search tool.  
  - Deliverables: Tool and findings.  
  - Pass gate: Results verified against a brute-force search on a subset.

### 10 — Changepoints Regimes and Streaming Models

**Outcome:** Detect when a series changes and learn from streams. Drift monitoring for deployed models is covered in Stage 5D; event-time processing and streaming engines are covered in Stage 2C; this module covers the detection and online-learning algorithms.

**Lessons**

- `01-changepoint-problem.md` — Changepoint problem: offline vs online detection and what counts as a change
- `02-cusum-and-page-hinkley-tests.md` — CUSUM and Page-Hinkley tests
- `03-offline-segmentation.md` — Offline segmentation: binary segmentation, PELT and penalty selection with ruptures
- `04-bayesian-online-changepoint-detection.md` — Bayesian online changepoint detection
- `05-concept-drift-detectors-for-streams.md` — Concept-drift detectors for streams: ADWIN and DDM
- `06-online-learning-for-streams-with-the-river-library.md` — Online learning for streams with the River library
- `07-streaming-forecasting.md` — Streaming forecasting: incremental updates and forgetting
- `08-evaluating-changepoint-detection.md` — Evaluating changepoint detection: detection delay, margin-of-error F1 and false alarm rate

**Hands-on projects**

- **Project 1: changepoint benchmark**  
  - Data: The TCPDBench datasets or equivalent annotated series  
  - Task: Compare PELT, binary segmentation and Bayesian online detection on delay and F1.  
  - Deliverables: Benchmark with margin-of-error scoring.  
  - Pass gate: Penalty settings tuned on separate series from the test set.
- **Project 2: online learning under drift**  
  - Data: A streaming dataset with abrupt and gradual drift  
  - Task: Compare batch retraining, online learners and drift-triggered retraining.  
  - Deliverables: Prequential error curves.  
  - Pass gate: Prequential evaluation with the test-then-train protocol.
- **Project 3: cusum alarm design**  
  - Data: A process-control series  
  - Task: Tune CUSUM parameters for a stated false-alarm rate and detection delay.  
  - Deliverables: Design analysis.  
  - Pass gate: False-alarm rate measured on in-control data.

### 11 — Time Series Anomaly Problem Design and Evaluation

**Outcome:** Define anomalies precisely and evaluate detectors without fooling yourself. Anomaly, outlier and novelty definitions, isolation forests, LOF, one-class methods and basic thresholding are covered in Stage 5B; this module covers time-series specifics and evaluation rigor.

**Lessons**

- `01-anomaly-types-in-sequences.md` — Anomaly types in sequences: point, contextual and collective anomalies
- `02-problem-framing.md` — Problem framing: what the operator will do with an alert
- `03-why-labels-are-scarce-and-noisy-and-how-to-label-time-series-anomalies.md` — Why labels are scarce and noisy, and how to label time-series anomalies
- `04-range-based-precision-and-recall.md` — Range-based precision and recall
- `05-the-point-adjustment-trap.md` — The point-adjustment trap: why a random scorer can look state of the art
- `06-threshold-free-and-robust-metrics.md` — Threshold-free and robust metrics: VUS-PR and PR-based evaluation
- `07-benchmark-flaws.md` — Benchmark flaws: triviality, mislabeling and run-to-failure bias
- `08-benchmark-archives-and-tools.md` — Benchmark archives and tools: UCR anomaly archive, TSB-AD and TimeEval
- `09-synthetic-anomaly-injection.md` — Synthetic anomaly injection: realistic injection and its limits
- `10-cost-based-alerting.md` — Cost-based alerting: alert budgets, detection delay and operator fatigue

**Hands-on projects**

- **Project 1: point adjust metric audit**  
  - Data: Several public anomaly benchmark series with published scores  
  - Task: Show that a random or trivial scorer reaches strong point-adjusted F1 and compare with range-based and VUS-PR metrics.  
  - Deliverables: Metric audit.  
  - Pass gate: Random baseline run many times with the spread reported.
- **Project 2: benchmark triviality analysis**  
  - Data: UCR anomaly archive and one older benchmark  
  - Task: Test how often a one-line detector solves benchmark series and document flaws.  
  - Deliverables: Analysis with examples.  
  - Pass gate: Detectors fixed before looking at labels.
- **Project 3: anomaly labeling protocol and agreement**  
  - Data: A real sensor or KPI series  
  - Task: Have two annotators label anomalies independently with written guidelines and measure agreement.  
  - Deliverables: Protocol, agreement and disagreement analysis.  
  - Pass gate: Agreement computed at range level.

### 12 — Statistical and Forecast Based Anomaly Detection

**Outcome:** Build strong non-deep detectors for time series and metrics, which are the baselines every deep method must beat.

**Lessons**

- `01-residual-based-detection.md` — Residual-based detection: forecast a series and flag unexpected errors
- `02-robust-seasonal-methods.md` — Robust seasonal methods: STL residuals, generalized ESD and seasonal hybrid ESD
- `03-statistical-process-control.md` — Statistical process control: Shewhart, EWMA and CUSUM charts
- `04-matrix-profile-discords-for-subsequence-anomalies.md` — Matrix-profile discords for subsequence anomalies
- `05-spectral-residual-and-frequency-domain-detectors.md` — Spectral residual and frequency-domain detectors
- `06-multivariate-methods.md` — Multivariate methods: Mahalanobis distance and PCA with T-squared and Q statistics
- `07-dynamic-thresholds-from-extreme-value-theory.md` — Dynamic thresholds from extreme value theory: SPOT and DSPOT
- `08-seasonality-and-trend-handling-so-periodic-behavior-is-not-flagged.md` — Seasonality and trend handling so periodic behavior is not flagged
- `09-business-kpi-anomaly-detection.md` — Business KPI anomaly detection: metrics with day-of-week and holiday effects

**Hands-on projects**

- **Project 1: residual vs discord vs spc comparison**  
  - Data: UCR anomaly archive subset and a KPI dataset  
  - Task: Compare forecast-residual, matrix-profile and control-chart detectors with proper range-based evaluation.  
  - Deliverables: Comparison report.  
  - Pass gate: Evaluation uses the metrics from the previous module.
- **Project 2: kpi anomaly detector with holiday effects**  
  - Data: A daily business metric series with known holidays  
  - Task: Build a detector that models weekly and holiday effects and measure false alarms on holiday weeks.  
  - Deliverables: Detector and false-alarm analysis.  
  - Pass gate: False alarms counted separately on holiday periods.
- **Project 3: evt threshold study**  
  - Data: Multivariate sensor series  
  - Task: Compare fixed thresholds with SPOT-style thresholds as data drifts.  
  - Deliverables: Threshold stability analysis.  
  - Pass gate: Drift injected with known timing.

### 13 — Deep and Self Supervised Anomaly Detection

**Outcome:** Use deep detectors where they earn their cost, and prove it against simple baselines. Autoencoders and basic reconstruction-based detection are introduced in Stages 5B and 5C.

**Lessons**

- `01-reconstruction-based-sequence-models.md` — Reconstruction-based sequence models: LSTM autoencoders and variational autoencoders
- `02-forecasting-based-deep-detection.md` — Forecasting-based deep detection
- `03-adversarial-and-adversarially-trained-detectors.md` — Adversarial and adversarially trained detectors: USAD and TranAD
- `04-transformer-detectors-and-the-anomaly-transformer.md` — Transformer detectors and the Anomaly Transformer
- `05-deep-one-class-methods.md` — Deep one-class methods: Deep SVDD and flow-based density models
- `06-contrastive-and-self-supervised-detectors.md` — Contrastive and self-supervised detectors
- `07-training-on-contaminated-data.md` — Training on contaminated data: robustness to anomalies in the training set
- `08-foundation-model-based-detection.md` — Foundation-model-based detection: using pretrained forecasters
- `09-choosing-deep-vs-simple.md` — Choosing deep vs simple: results from recent benchmarks

**Hands-on projects**

- **Project 1: deep vs simple detector benchmark**  
  - Data: TSB-AD or UCR anomaly archive subsets and one multivariate dataset  
  - Task: Compare LSTM-AE, USAD, TranAD, Anomaly Transformer and simple baselines under range-based and VUS-PR metrics with many series.  
  - Deliverables: Benchmark with rank analysis.  
  - Pass gate: Simple baselines and a random baseline included and hyperparameter budgets matched.
- **Project 2: contamination robustness study**  
  - Data: A dataset with controllable anomaly rate  
  - Task: Vary the anomaly fraction in the training set and measure each detector's degradation.  
  - Deliverables: Degradation curves.  
  - Pass gate: Contamination injected with a documented procedure.
- **Project 3: foundation model anomaly scoring**  
  - Data: A univariate series set  
  - Task: Score anomalies using forecast errors from a pretrained forecaster and compare with trained detectors.  
  - Deliverables: Comparison with cost.  
  - Pass gate: Dataset postdates the model where possible.

### 14 — Anomaly Detection for Images Logs and Event Sequences

**Outcome:** Detect abnormal images, log lines and event traces. Image models are used as in G2; graph-based anomaly detection is covered later in G8.

**Lessons**

- `01-industrial-visual-anomaly-detection.md` — Industrial visual anomaly detection: the one-class setting with only normal images
- `02-feature-memory-methods.md` — Feature-memory methods: PatchCore and PaDiM
- `03-reconstruction-and-student-teacher-approaches-for-images.md` — Reconstruction and student-teacher approaches for images
- `04-tooling-and-benchmarks.md` — Tooling and benchmarks: anomalib, MVTec AD and VisA
- `05-evaluating-visual-anomaly-detection.md` — Evaluating visual anomaly detection: image-level and pixel-level metrics
- `06-log-parsing.md` — Log parsing: templates and the Drain algorithm
- `07-sequence-based-log-anomaly-detection.md` — Sequence-based log anomaly detection: DeepLog-style models
- `08-event-sequence-and-process-anomalies.md` — Event-sequence and process anomalies
- `09-anomaly-detection-in-text-streams-and-metadata.md` — Anomaly detection in text streams and metadata

**Hands-on projects**

- **Project 1: visual defect detection on mvtec ad**  
  - Data: MVTec AD (check licence terms)  
  - Task: Compare PatchCore, PaDiM and a reconstruction baseline on image-level and pixel-level scores across categories.  
  - Deliverables: Per-category results and failure gallery.  
  - Pass gate: Per-category results reported, not only the mean.
- **Project 2: log anomaly detection pipeline**  
  - Data: HDFS and BGL logs from the Loghub collection  
  - Task: Parse logs with Drain and compare count-vector, PCA and sequence-model detectors.  
  - Deliverables: Pipeline and evaluation.  
  - Pass gate: Training windows precede test windows in time.
- **Project 3: normal data requirements study**  
  - Data: One visual category  
  - Task: Measure detection quality against the number of normal training images and against normal-set contamination.  
  - Deliverables: Data-requirement curves.  
  - Pass gate: Contamination injected with known defect images.

### 15 — Operating Forecasting and Anomaly Systems

**Outcome:** Run forecasts and alerts as dependable services. General MLOps, monitoring, orchestration and streaming are covered in Stages 5D and 2C; this module covers what is specific to time-based systems.

**Lessons**

- `01-forecast-pipelines.md` — Forecast pipelines: scheduling, backfills and point-in-time reproducibility
- `02-forecast-versioning-archiving-and-reconciliation-outputs.md` — Forecast versioning, archiving and reconciliation outputs
- `03-monitoring-forecasts.md` — Monitoring forecasts: bias, tracking signal and horizon-wise error in production
- `04-retraining-cadence-for-forecasters-and-handling-structural-breaks.md` — Retraining cadence for forecasters and handling structural breaks
- `05-scaling-to-millions-of-series.md` — Scaling to millions of series: batch design and cost
- `06-alert-design.md` — Alert design: grouping, deduplication, severity and suppression
- `07-root-cause-help-for-anomalies.md` — Root-cause help for anomalies: dimension drill-down and contributor analysis
- `08-feedback-loops.md` — Feedback loops: collecting operator labels and tuning thresholds safely
- `09-real-time-scoring.md` — Real-time scoring: online detectors on streams with latency budgets
- `10-runbooks-ownership-and-measuring-business-value-of-alerts.md` — Runbooks, ownership and measuring business value of alerts

**Hands-on projects**

- **Project 1: backfill safe forecast pipeline**  
  - Data: A forecasting pipeline from earlier modules  
  - Task: Make the pipeline reproducible for any historical date with point-in-time data and archived forecasts.  
  - Deliverables: Pipeline and reproducibility tests.  
  - Pass gate: Re-running a past date reproduces the archived forecast.
- **Project 2: alert quality and rca system**  
  - Data: A multi-dimensional metric dataset such as sales by region and product  
  - Task: Build alerting with grouping and a contributor analysis that points to the responsible segment, and evaluate on injected anomalies.  
  - Deliverables: System and evaluation.  
  - Pass gate: Injected root causes found within top-3 contributors at a measured rate.
- **Project 3: forecast monitoring dashboard with retrain triggers**  
  - Data: Production-style forecast logs you simulate  
  - Task: Build monitoring for bias and error drift with retraining triggers and test with injected structural breaks.  
  - Deliverables: Dashboard and trigger tests.  
  - Pass gate: Injected breaks trigger alerts within a stated delay.

### 16 — G5 Capstones

**Outcome:** integrate the forecasting and anomaly tracks in assessed, portfolio-quality work.

- **Capstone 1: forecasting system for a planning problem** (uses Modules 01, 02, 04, 05, 07, 08)  
  Build an end-to-end forecasting system for a planning problem with statistical, GBDT and deep baselines, probabilistic output, a decision simulation and a forecast-value-added report.
- **Capstone 2: foundation model and global model benchmark** (uses Modules 04, 05, 06)  
  Run a rigorous benchmark of foundation models, global models and statistical baselines with contamination checks and licence review.
- **Capstone 3: anomaly detection platform** (uses Modules 11 to 15)  
  Build an anomaly detection service with a rigorously evaluated detector set, alert design, root-cause help, a feedback loop and an operations runbook.
- **Capstone 4: streaming changepoint and forecast monitor** (uses Modules 03, 10, 15)  
  Build a streaming monitor combining online forecasting, changepoint detection and drift-triggered retraining and evaluate it on injected events.
- **Capstone 5: g5 readiness assessment** (uses All modules)  
  Written and practical assessment against the G5 completion gate.

## G5 completion gate

- Every forecasting result uses rolling-origin backtests that respect forecast-time information, with naive and strong statistical baselines included.
- Every anomaly result uses range-based or threshold-free metrics, includes a random baseline and a simple baseline, and never relies on point-adjusted scores alone.
- Every comparison across methods uses matched tuning budgets, many series or datasets, and reports intervals or rank statistics.
- All results reproduce from a lockfile, configs and logged seeds, with library versions, model versions and licences recorded.
- Every dataset used has its licence and access conditions recorded before use.
- At least one negative or inconclusive result per track is reported honestly, including a case where a simple baseline wins.
- The four specialist capstones are complete and the readiness assessment is passed.

## Audit and verification

**What was checked and the result**

- Structure: 15 specialist modules each have 6 to 12 lessons and at least one project; the tree contains 230 files and 33 folders, and these counts equal the counts computed from the curriculum data.
- Overlap with the Roadmap: all 139 lesson file names were compared against every lesson file name in `Roadmap.md`. Exact matches: 0. Near matches (similarity 0.80 or higher): 0.
- Structural problems found by the build script: 0.
- Topic-level overlap check: the Roadmap text was searched for state-space models, tsfresh, sktime, statsforecast, N-BEATS, Temporal Fusion Transformer, PatchTST, Chronos, TimesFM, changepoint, STL, wavelet, dynamic time warping, matrix profile, CUSUM, GARCH, Croston, ADWIN and Page-Hinkley. None appear as lessons, so G5 teaches them for the first time. The Roadmap does contain a Kalman filter elective (one lesson), forecast reconciliation in the Stage 5B hierarchical lesson, and the Stage 5B forecasting and anomaly lessons, which G5 references and extends and does not reteach.
- Verified by web search on the build date (2026-10-26): Wu and Keogh argue that popular anomaly benchmarks are flawed and introduced the UCR anomaly archive; Kim et al. showed that point-adjusted scoring lets random scorers look state of the art; the TSB-AD benchmark (Liu and Paparrizos) recommends VUS-PR as a headline measure; Chronos-2, TimesFM and Moirai are the main time-series foundation models and GIFT-Eval and fev-bench are the common benchmarks; Nixtla maintains StatsForecast, MLForecast, NeuralForecast and HierarchicalForecast.
- Reported but not confirmed: leaderboard rankings between Chronos-2, TimesFM and Moirai differ by metric, benchmark version and source, and vendor claims (including a reported newer TimesFM release) were not independently confirmed, so no ranking is asserted; one source says Moirai weights carry a non-commercial licence, which was not checked against the primary licence; the maintenance status of Darts, sktime, aeon, anomalib and River was not confirmed and is required in the register; the last-updated dates seen for some Nixtla packages were old and may be stale.
- Not verified: library, model and benchmark versions, which change quickly (especially in module 06); dataset availability and licences (Kaggle competition terms, MVTec AD, SWaT-style datasets that require applications); festival and holiday dates, which must be checked against at least two sources.
- Not verified by execution: no code in this plan has been run. Project pass gates are acceptance criteria to be met when the projects are built.
- Repository safety: this build created only this file; no existing file or folder was created, changed or deleted by it.
