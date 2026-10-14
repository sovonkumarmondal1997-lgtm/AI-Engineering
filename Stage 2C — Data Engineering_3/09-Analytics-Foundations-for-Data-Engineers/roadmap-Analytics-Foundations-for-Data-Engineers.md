# Roadmap — Module 2C.9: Analytics Foundations for Data Engineers

This is the learning roadmap for the ninth module of Stage 2C, **Data
Engineering_3**. It tells you **what** to learn about analysis, statistics,
experimentation, and visualization, **in what order**, **how** to learn
each topic, and **how to prove to yourself** that you have learned it
before you move on.

A data engineer builds the platform that delivers trustworthy data. But the
person who consumes it — an analyst, a data scientist, a product manager —
asks questions such as: "Did the new checkout increase conversion, or was
it noise?", "How many unique users did we have last month, to within 1%?",
"Why did retention drop in the March cohort?" Data engineers who understand
**how those questions are answered** build better tables, better pipelines,
and better metrics, and are far more valuable in design discussions,
incident reviews, and experimentation platforms.

This module is **not** a full statistics or data science degree (that is
Stage 4 and Stage 5). It teaches the part of analytics that a data engineer
must know to build for analysts correctly: distributions and summary
statistics **at scale**, sampling and approximation, hypothesis testing,
A/B test data pipelines, cohort and funnel analysis, time-series basics,
BI tools, visualization, and communicating results.

---

## 1. Module outcome

By the end of this module you will be able to:

- Compute and interpret descriptive statistics and distributions on data too
  large for memory, using SQL, DuckDB, Polars, and Spark.
- Use **sampling** and **approximate algorithms** (HyperLogLog, quantile
  sketches, Bloom filters, count-min) and know their error trade-offs.
- Run and interpret **hypothesis tests** and **confidence intervals**, and
  avoid the common statistical traps.
- Design the **data pipeline behind A/B tests**: assignment, exposure,
  metrics, guardrails, and result tables.
- Perform **cohort, funnel, and retention** analysis with SQL.
- Do basic **time-series** analysis: decomposition, seasonality, and simple
  forecasting baselines.
- Choose and operate **BI tools** (Metabase, Superset, Tableau, Power BI)
  and design effective dashboards.
- Create clear **visualizations** in Python (matplotlib, Plotly, Altair).
- Communicate findings to stakeholders with a clear narrative.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Python, functions, testing | Stage 1 | All analysis code |
| NumPy: vectorisation, aggregations | Stage 2 — Module 2.2 | Fast numeric computation |
| pandas: groupby, resample, rolling | Stage 2 — Module 2.3 | Analysis workhorse |
| Polars / DuckDB / Arrow | Stage 2 — Module 2.4 | Large-data analysis on one machine |
| SQL: windows, CTEs, aggregates | Stage 2 — Module 2.6 | Cohorts, funnels, retention |
| Event modelling, sessions, identity | Stage 2 — Module 2.8 | Clean event data is the base of all analysis |
| Spark | Stage 2 — Module 2.14 | Statistics at cluster scale |
| Semantic layers and metric definitions | Stage 2 — Module 2.22; Module 2C.6 | Consistent metrics |
| OLAP / serving engines | Module 2C.7 | Where dashboards query |
| Data products and SLAs | Module 2C.8 | What the analysts consume |
| Basic algebra and probability | School level; deepened in Stage 4 | Reading formulas |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add numpy pandas polars duckdb scipy
  statsmodels matplotlib plotly altair datasketches seaborn jupyter pytest`.
- Docker Compose with **Metabase** and/or **Apache Superset** (plus
  PostgreSQL or DuckDB as the data source).
- A sample dataset: web events (users, sessions, orders) with a built-in
  A/B experiment you generate yourself so you know the true effect.

**A note on rigour:** statistics is easy to do wrong silently. Always
simulate data with a known answer first and check that your method
recovers it.

---

## 3. How the module is organised

The nine topics are grouped into four phases. Work through them **in order**.

```text
Phase A — Describing Data at Scale                   (Basics → Intermediate)
  01 Descriptive statistics and distributions at scale
  02 Sampling and approximate algorithms

Phase B — Inference and Experiments                  (Intermediate → Advanced)
  03 Hypothesis testing and confidence intervals
  04 A/B testing and experiment data pipelines

Phase C — Behavioural and Temporal Analysis          (Intermediate → Advanced)
  05 Cohort, funnel, and retention analysis
  06 Time-series analysis and forecasting basics

Phase D — Presenting Results                         (Intermediate)
  07 BI tools and dashboard design
  08 Data visualization in Python
  09 Data storytelling and stakeholder communication

Consolidate
  Module mini-project: an experiment and product-analytics report
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09
describe  shrink  decide experi- behave- over    dash-  charts  tell
the data  it      if it's ments    iour   time   boards         the
                  real                                           story
```

Why this order:

- You must describe data (01) before you test it (03).
- Sampling and sketches (02) make description and testing feasible at big
  scale.
- A/B testing (04) applies testing to a real engineering problem.
- Cohorts, funnels, and time (05–06) are the most common product analyses.
- Dashboards, charts, and storytelling (07–09) are how results reach
  decision makers.

---

## 4. Suggested schedule

About **5 weeks at 8 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — descriptive statistics · Topic 02 — sampling and sketches |
| 2 | Topic 03 — hypothesis testing and confidence intervals |
| 3 | Topic 04 — A/B test pipelines · Topic 05 — cohorts, funnels, retention |
| 4 | Topic 06 — time series · Topic 07 — BI tools |
| 5 | Topic 08 — visualization · Topic 09 — storytelling · mini-project |

---

## 5. How to study every topic (the analyst's loop)

```text
Read → Ask the business question → Simulate data with a known answer
→ Compute → Check against the truth → Try to break it (bias, outliers,
peeking) → Visualise → Write the conclusion in one paragraph → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Ask the business question** in plain words before touching code.
3. **Simulate** data where you know the true effect, rate, or trend.
4. **Compute** with SQL and Python; do the small case by hand once.
5. **Check** the result against the known truth.
6. **Try to break it**: add outliers, skew, missing values, peeking, and
   multiple comparisons.
7. **Visualise** the data and the result.
8. **Write the conclusion** in one paragraph a non-technical person can
   act on.
9. **Write it down** in `module-2c9-notes.md`.
10. **Explain aloud** what you know, how sure you are, and what you would
    check next.

Keep one `analytics_lab/` project:

```text
analytics_lab/
├── data/                  # generators and sample datasets
├── sql/                   # cohort, funnel, retention, experiment queries
├── src/analytics_lab/     # stats helpers, sketches, plotting utilities
├── notebooks/             # exploration and reports
├── dashboards/            # Metabase/Superset exports
├── reports/               # written conclusions
└── tests/                 # tests that recover known simulated effects
```

---

## 6. Phase A — Describing Data at Scale (Basics → Intermediate)

### Topic 01 — [Descriptive statistics and distributions at scale](01-descriptive-statistics-and-distributions-at-scale.md)

**Why it comes first:** before any model or test, you must describe your
data honestly. Wrong summaries (a mean of a skewed variable, a percentile
of aggregated percentiles) are among the most common analytical errors.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Types of data: numeric (continuous/discrete), categorical, ordinal, time, text; measurement scales |
| Basics | Measures of centre (mean, median, mode) and spread (range, variance, standard deviation, IQR); when each misleads |
| Basics | Percentiles/quantiles and the five-number summary; boxplots |
| Basics | Distributions: uniform, normal, log-normal, exponential, Poisson, binomial, heavy-tailed (power-law); histograms and density plots |
| Intermediate | Skewness and kurtosis; why revenue, latency, and session length are rarely normal |
| Intermediate | Outliers: detection (IQR, z-score, MAD), treatment (winsorise, cap, separate), and when outliers are the signal |
| Intermediate | Correlation vs causation; Pearson, Spearman; confounders and Simpson's paradox |
| Intermediate | Missing data: MCAR, MAR, MNAR; effect on summaries; imputation vs exclusion |
| Intermediate | Computing stats **at scale**: SQL (`AVG`, `STDDEV`, `PERCENTILE_CONT`, `APPROX_PERCENTILE`), DuckDB, Polars lazy, Spark; streaming algorithms (Welford's online mean/variance) |
| Advanced | **Mergeable statistics**: summing counts, sums, and sums of squares to combine partitions correctly; why you cannot average percentiles or averages-of-averages |
| Advanced | Weighted statistics, ratio metrics, and the delta method idea for variance of ratios |
| Advanced | Data profiling as a pipeline step: distribution drift checks and anomaly thresholds (links to Module 2.11) |
| Advanced | Interpretable summaries for stakeholders: medians, percentiles (p50/p95/p99), and trimmed means |

**How to learn it**

1. Read the topic file.
2. Generate three variables (normal, log-normal, bimodal); compute all
   summaries and predict which will mislead.
3. Compute the same summary over partitions and verify which combine
   correctly.

**Hands-on exercise — `experiments/01_descriptive/`**

1. Compute summary statistics on 100M rows with DuckDB and Polars; compare
   with exact pandas on a sample.
2. Show a case where the mean hides the story (log-normal revenue) and fix
   the report with percentiles.
3. Demonstrate Simpson's paradox with a generated dataset.
4. Implement Welford's algorithm and verify against NumPy.
5. Show that the average of daily p95s is not the monthly p95; compute it
   properly.

**Checkpoint — you are ready to move on when you can:**

- [ ] Choose the right summary for a distribution.
- [ ] Detect and handle outliers and missing data.
- [ ] Compute mergeable statistics across partitions.
- [ ] Explain why percentiles and ratios need care.

**Common mistakes:** reporting means of skewed data; averaging averages
and percentiles; dropping outliers without asking what they are; assuming
normality.

---

### Topic 02 — [Sampling and approximate algorithms: HyperLogLog and sketches](02-sampling-and-approximate-algorithms-hyperloglog-and-sketches.md)

**Why here:** exact answers at billion-row scale are often slow or
expensive. Sampling and sketches give answers that are good enough, fast,
and **mergeable** — a core data engineering tool.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Population vs sample; random vs systematic vs stratified sampling; sampling bias |
| Basics | Sampling in practice: `TABLESAMPLE`, `USING SAMPLE` (DuckDB), `df.sample`, hash-based deterministic sampling (`hash(user_id) % 100 < 5`) |
| Basics | Sampling error and sample size: how error shrinks with √n |
| Intermediate | Why approximate: the cost of exact `COUNT(DISTINCT)`, exact quantiles, and exact heavy hitters at scale |
| Intermediate | **HyperLogLog (HLL)**: approximate distinct counts; error ~1–2%; mergeable across partitions; `APPROX_COUNT_DISTINCT`, `hll` functions in BigQuery/Snowflake/ClickHouse/Spark |
| Intermediate | **Quantile sketches**: t-digest, KLL, DDSketch; `APPROX_PERCENTILE`; mergeability and error guarantees |
| Intermediate | **Bloom filters** (set membership, no false negatives) and **count-min sketch** (frequency estimates, heavy hitters) |
| Intermediate | Reservoir sampling for streams; weighted sampling |
| Advanced | Apache DataSketches (theta, HLL, KLL, frequent items) in Python/Java/Spark; set operations on theta sketches (union, intersection) |
| Advanced | Using sketches in pipelines: storing sketch columns in aggregate tables to enable rollups across any grouping (links to Module 2C.7 Topic 05) |
| Advanced | Error budgeting: choosing precision parameters; validating sketch error against exact on a sample |
| Advanced | Stratified sampling for rare events, importance sampling, and bias correction |
| Advanced | Privacy-flavoured approximation: differential privacy basics — awareness |

**How to learn it**

1. Read the topic file.
2. By hand, simulate a tiny HyperLogLog with 4 registers on 10 values.
3. List five questions in your platform that could use a sketch.

**Hands-on exercise — `experiments/02_sketches/`**

1. Compute exact vs HLL distinct users on 100M events; compare time,
   memory, and error across precision levels.
2. Store daily HLL sketches in a table; compute weekly and monthly unique
   users by merging, and compare with the exact monthly count.
3. Compute p50/p95/p99 with t-digest or KLL; merge per-partition sketches
   and compare with exact.
4. Build a Bloom filter for deduplication; measure the false-positive rate
   vs size.
5. Find heavy hitters in a Zipfian stream with a count-min sketch.
6. Implement deterministic hash sampling and prove it is stable across
   runs.

**Checkpoint:**

- [ ] Choose between exact, sampled, and sketch-based answers.
- [ ] Use HLL and quantile sketches and merge them.
- [ ] State the error properties of each structure.
- [ ] Sample deterministically and without bias.

**Common mistakes:** summing daily distinct counts to get weekly distinct;
using a different hash per run; trusting a sketch without measuring its
error on your data.

---

## 7. Phase B — Inference and Experiments (Intermediate → Advanced)

### Topic 03 — [Hypothesis testing and confidence intervals](03-hypothesis-testing-and-confidence-intervals.md)

**Why here:** this is how we decide whether an observed difference is real
or noise. It underlies A/B testing, anomaly detection, and quality
monitoring.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The logic: null and alternative hypotheses, test statistic, **p-value** (what it is and is not), significance level α, and decision |
| Basics | Type I error (false positive), Type II error (false negative), **power**, and effect size |
| Basics | **Confidence intervals**: meaning, construction for a mean and a proportion; interval width and sample size |
| Intermediate | Common tests: one- and two-sample **t-test**, **Welch's** t-test, **z-test for proportions**, **chi-square**, Mann–Whitney U (non-parametric) |
| Intermediate | Assumptions: independence, normality (and the central limit theorem), equal variance; checking them |
| Intermediate | **Bootstrap** confidence intervals and permutation tests for anything without a formula (medians, ratios) |
| Intermediate | **Power analysis and sample size** before running: minimum detectable effect (MDE) |
| Intermediate | Python: `scipy.stats`, `statsmodels` (`proportions_ztest`, `ttest_ind`, power calculators) |
| Advanced | **Multiple comparisons**: Bonferroni, Holm, Benjamini–Hochberg (FDR); why testing 20 metrics finds a "winner" by chance |
| Advanced | Practical vs statistical significance; reporting effect sizes and intervals instead of "p < 0.05" |
| Advanced | Bayesian alternative: priors, posteriors, credible intervals, and probability-to-beat-control — awareness |
| Advanced | Non-independence: clustered data (users with many events), the unit of analysis, and robust (cluster) standard errors |
| Advanced | Ratio metrics and the delta method; variance reduction (CUPED) — awareness |
| Advanced | Common abuses: p-hacking, optional stopping, HARKing, and survivorship bias |

**How to learn it**

1. Read the topic file.
2. Simulate two groups with a known difference; run the right test; count
   how often it detects the effect over 1,000 simulations (power).
3. Run the same with no true difference and count false positives
   (should be about α).

**Hands-on exercise — `experiments/03_hypothesis_testing/`**

1. Test a conversion-rate difference with a z-test and a bootstrap; compare
   intervals.
2. Compute the required sample size for an MDE of 1 percentage point at
   80% power.
3. Run 20 metric tests on pure noise and see how many are "significant";
   apply Holm and BH corrections.
4. Demonstrate that peeking daily and stopping at the first p < 0.05
   inflates false positives.
5. Analyse clustered data both naively and with user-level aggregation;
   compare the standard errors.

**Checkpoint:**

- [ ] Explain p-values and confidence intervals correctly.
- [ ] Choose a test for a metric type.
- [ ] Compute sample size and power.
- [ ] Correct for multiple comparisons.
- [ ] Spot peeking and clustering problems.

**Common mistakes:** "p = 0.04 means 96% chance the effect is real";
ignoring power; testing many metrics uncorrected; treating events as
independent when users are the unit.

---

### Topic 04 — [A/B testing and experiment data pipelines](04-ab-testing-and-experiment-data-pipelines.md)

**Why here:** experimentation is where data engineering and statistics
meet. The pipeline — assignment, exposure logging, metric computation,
results — is the data engineer's responsibility, and most failed
experiments fail in the data.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What an experiment is: randomised assignment to control/treatment, a primary metric, and a decision rule; why randomisation enables causal claims |
| Basics | The unit of randomisation (user, session, device, account, cluster) and why it matters |
| Basics | The experiment lifecycle: hypothesis → design (MDE, duration) → launch → monitor → analyse → decide → document |
| Intermediate | **Assignment**: deterministic hashing (`hash(experiment_id + user_id)`), buckets, traffic allocation, ramp-up, mutual exclusion layers, and holdouts |
| Intermediate | **Exposure logging**: log when a user actually saw the treatment; **intent-to-treat** vs exposed-only analysis |
| Intermediate | **Metrics**: primary, secondary, **guardrail** (latency, errors, revenue), and diagnostic; metric definitions via the semantic layer (Module 2C.6) |
| Intermediate | **Sample Ratio Mismatch (SRM)**: chi-square check that the observed split matches the design; the first thing to check, and a data-quality alarm |
| Intermediate | Experiment tables: assignments, exposures, events, per-user daily metrics, and results; SQL for conversion and revenue-per-user analysis |
| Advanced | Common pitfalls: novelty and primacy effects, seasonality, interference/network effects, Simpson's paradox across segments, bot traffic, and instrumentation bugs |
| Advanced | **Variance reduction**: CUPED/CUPAC using pre-experiment covariates; stratification; sequential testing and always-valid inference |
| Advanced | Heterogeneous effects and segment analysis (and the multiple comparison danger); long-term holdouts |
| Advanced | Experimentation platforms: build vs buy (Statsig, Optimizely, Eppo, GrowthBook, LaunchDarkly experiments) — links to Module 2C.8 Topic 07 |
| Advanced | Pipeline engineering: idempotent daily recomputation, late events, identity stitching across devices, and reproducibility of results |
| Advanced | Beyond A/B: multi-armed bandits, quasi-experiments (diff-in-diff, synthetic control), and switchback tests — awareness |

**How to learn it**

1. Read the topic file.
2. Design an experiment for "new checkout button": unit, primary metric,
   guardrails, MDE, and duration.
3. Sketch the tables and the SQL path from raw events to a result row.

**Hands-on exercise — `experiments/04_ab_testing/`**

1. Simulate 500,000 users with a true +2% relative lift; implement
   hash-based assignment and exposure/event logs, including some users
   never exposed and some bots.
2. Build the experiment tables with DuckDB/dbt: assignments, exposures,
   daily per-user metrics, and a results table.
3. Run the SRM check; then inject an assignment bug and detect it.
4. Analyse with a two-sample test, a bootstrap, and CUPED; compare
   confidence-interval widths.
5. Add two guardrail metrics and a decision rule.
6. Write an automated, idempotent daily job producing a results report;
   test that it recovers the simulated lift.

**Checkpoint:**

- [ ] Design an experiment with unit, metrics, MDE, and duration.
- [ ] Build assignment, exposure, and result pipelines.
- [ ] Detect SRM and other data-quality problems.
- [ ] Apply variance reduction and corrections.
- [ ] Explain when A/B testing is the wrong tool.

**Common mistakes:** assigning on a different key than the analysis unit;
ignoring SRM; analysing all assigned users as if all were exposed without
knowing it; stopping early on a good-looking interval.

---

## 8. Phase C — Behavioural and Temporal Analysis (Intermediate → Advanced)

### Topic 05 — [Cohort, funnel, and retention analysis](05-cohort-funnel-and-retention-analysis.md)

**Why here:** these are the bread-and-butter analyses of product teams —
and mostly SQL on event tables that data engineers design.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Key product metrics: DAU/WAU/MAU, conversion rate, churn, ARPU, LTV, activation |
| Basics | **Funnels**: ordered steps, step-to-step conversion, drop-off, and time to convert |
| Basics | **Cohorts**: grouping users by a shared start (signup week, first purchase, acquisition channel) |
| Intermediate | **Retention**: N-day retention (day 1/7/30), unbounded vs bounded retention, rolling retention; the cohort triangle table |
| Intermediate | SQL implementations: first-event CTEs, self-joins vs window functions, `DATE_TRUNC`, cohort-age arithmetic, and `LEAD`/`LAG` for step order |
| Intermediate | Funnel variants: strict vs loose ordering, windowed funnels (convert within 7 days), and per-session vs per-user funnels |
| Intermediate | **Sessionisation** and activity definitions (what counts as "active") — the data engineering decision with the biggest effect on metrics |
| Intermediate | Segmentation: by channel, device, geography, plan; avoiding tiny segments |
| Advanced | **Survival analysis** basics: Kaplan–Meier curves, hazard rates, and censoring (users who haven't churned *yet*) — awareness |
| Advanced | LTV and revenue cohorts; payback period; discounting; predicting LTV from early behaviour |
| Advanced | Stickiness ratios, resurrection/churn decomposition (new, retained, resurrected, churned users) |
| Advanced | Performance at scale: precomputed user-day activity tables (the "active days" bitmap/array pattern), incremental updates, and approximate approaches |
| Advanced | Metric definitions and governance: one retention definition in the semantic layer; documenting windows and time zones |
| Advanced | Pitfalls: survivorship bias, cohort size drift, mixing time zones, and comparing immature cohorts |

**How to learn it**

1. Read the topic file.
2. Define "active" for your sample app and justify it.
3. Sketch the retention triangle for four weekly cohorts by hand with
   made-up numbers.

**Hands-on exercise — `experiments/05_cohorts_funnels/`**

1. From a raw `events` table, build a `user_daily_activity` table (one row
   per user per active day).
2. Compute weekly signup cohorts and day-1/7/30 retention with SQL; render
   the cohort triangle as a heatmap.
3. Build a 4-step funnel (visit → signup → add to cart → purchase) with a
   7-day window and per-step conversion; test both strict and loose
   ordering.
4. Decompose MAU growth into new, retained, resurrected, and churned.
5. Show how changing the "active" definition changes retention.
6. Make the pipeline incremental and verify equality with a full rebuild.

**Checkpoint:**

- [ ] Write cohort, retention, and funnel SQL from scratch.
- [ ] Explain how definitions change results.
- [ ] Build efficient activity tables for scale.
- [ ] Avoid immature-cohort and time-zone errors.

**Common mistakes:** inconsistent definitions across dashboards; counting
users active in a window as retained when they were not in the first
period; comparing cohorts of different ages.

---

### Topic 06 — [Time-series analysis and forecasting basics](06-time-series-analysis-and-forecasting-basics.md)

**Why here:** capacity planning, anomaly detection on pipeline metrics, and
business forecasting all depend on time-series fundamentals. Data
engineers also build the pipelines that feed forecasting models.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Time-series components: **trend**, **seasonality** (daily, weekly, yearly), cycles, and noise |
| Basics | Handling time: time zones, daylight saving, irregular intervals, missing timestamps, and resampling to a fixed grid (links to Module 2.3 Topic 09) |
| Basics | Rolling and expanding windows; moving averages; year-over-year and week-over-week comparisons |
| Intermediate | **Decomposition**: additive vs multiplicative; STL decomposition (`statsmodels`) |
| Intermediate | **Stationarity**, differencing, autocorrelation (ACF/PACF), and why they matter |
| Intermediate | **Baseline forecasts**: naive, seasonal naive, moving average, exponential smoothing (Holt–Winters); the bar any fancy model must beat |
| Intermediate | **Evaluation**: train/test split by time (never random), rolling-origin backtesting, and metrics (MAE, RMSE, MAPE/sMAPE, MASE) |
| Intermediate | **Anomaly detection on time series**: z-score on residuals, seasonal thresholds, prophet-style intervals; use for pipeline volume/freshness monitoring (Module 2.11) |
| Advanced | ARIMA/SARIMA basics; `statsforecast`, `Prophet`, and gradient-boosted models with lag features — awareness of when each is used |
| Advanced | Hierarchical and many-series forecasting (per SKU/store), and global models |
| Advanced | Forecast pipelines: feature tables with lags/holidays, scheduled backtests, forecast storage with versioning, and monitoring forecast error |
| Advanced | In-warehouse forecasting: BigQuery ML `ARIMA_PLUS` (Module 2C.4), Snowflake ML forecasting, Databricks AI functions — awareness |
| Advanced | Pitfalls: leakage from future data, ignoring holidays and promotions, and over-fitting to one season |
| Advanced | Causal impact and intervention analysis — awareness |

**How to learn it**

1. Read the topic file.
2. Plot a daily series with trend and weekly seasonality; mark the
   components by eye.
3. Predict which baseline will win on it.

**Hands-on exercise — `experiments/06_time_series/`**

1. Generate daily orders with trend, weekly seasonality, noise, and a
   holiday spike.
2. Decompose with STL; interpret each component.
3. Build naive, seasonal-naive, Holt–Winters, and a lag-feature model;
   backtest with a rolling origin and compare MAE/MASE.
4. Build an anomaly detector on residuals and apply it to pipeline row
   counts from your earlier labs.
5. Wrap forecasting in a scheduled job that writes versioned forecasts and
   tracks error over time.

**Checkpoint:**

- [ ] Decompose a series and explain its components.
- [ ] Beat or fail to beat a seasonal-naive baseline honestly.
- [ ] Backtest correctly without leakage.
- [ ] Use time-series methods for pipeline anomaly detection.

**Common mistakes:** random train/test splits; no baseline; forgetting
time zones and DST; trusting a single backtest window.

---

## 9. Phase D — Presenting Results (Intermediate)

### Topic 07 — [BI tools and dashboard design: Metabase, Superset, Tableau](07-bi-tools-and-dashboard-design-metabase-superset-tableau.md)

**Why here:** most stakeholders never see your SQL; they see dashboards.
A data engineer must understand how BI tools query the platform, what makes
dashboards fast and trustworthy, and which tool fits which team.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What BI tools do: connect to a data source, model data, build charts, assemble dashboards, share, and schedule |
| Basics | The landscape: open source (**Metabase**, **Apache Superset**), commercial (**Tableau**, **Power BI**, **Looker**, **Mode**, ThoughtSpot), and notebook-style (Hex, Observable) |
| Basics | Connecting to warehouses/engines; read-only users; schemas exposed to BI; the "gold layer" principle |
| Intermediate | Modelling in BI: datasets, joins, calculated fields, metrics, semantic layers (LookML, dbt Semantic Layer, Power BI models) and where logic should live (warehouse > semantic layer > BI) |
| Intermediate | **Dashboard design principles**: one question per dashboard, hierarchy of information, KPI tiles, appropriate chart types, filters, and avoiding clutter |
| Intermediate | Performance: pre-aggregated tables, extracts vs live queries, caching, query limits, and slow-dashboard debugging (query logs, EXPLAIN) |
| Intermediate | Running Metabase and Superset in Docker; users, groups, and collections; embedding and parameters |
| Advanced | Governance: row-level security, permissions on collections/workspaces, certified dashboards, and metric ownership |
| Advanced | Operating BI: version control (Superset export, Metabase serialisation, Tableau/Power BI deployment pipelines), environments, and usage analytics to retire unused dashboards |
| Advanced | Cost: per-seat licensing vs warehouse query cost; extract refresh schedules; capacity (Power BI Premium/Fabric, Tableau Server) |
| Advanced | Embedded analytics for customers (multi-tenant considerations from Module 2C.8) |
| Advanced | Choosing a BI tool: team skills, governance needs, cost, ecosystem fit (Fabric ↔ Power BI, Looker ↔ BigQuery) |

**How to learn it**

1. Read the topic file.
2. Take one analytical question and sketch the dashboard on paper before
   opening any tool.
3. List which dashboard queries should hit pre-aggregated tables.

**Hands-on exercise — `experiments/07_bi_tools/`**

1. Run Metabase and Superset in Docker connected to your analytics
   database (gold tables only).
2. Build the same executive dashboard (revenue, conversion, retention
   heatmap, top products) in both; compare effort and features.
3. Find the three slowest cards; fix them with pre-aggregated tables or
   caching.
4. Set up groups with row-level restrictions (region) and verify them.
5. Export dashboards as code and restore them into a fresh instance.
6. Review usage statistics and propose which dashboards to retire.

**Checkpoint:**

- [ ] Choose a BI tool for a team and justify it.
- [ ] Design a focused dashboard.
- [ ] Make dashboards fast and governed.
- [ ] Keep metric logic out of the BI layer where possible.

**Common mistakes:** business logic duplicated in many cards; dashboards
querying raw tables; no ownership; 40-chart dashboards nobody reads.

---

### Topic 08 — [Data visualization with matplotlib, Plotly, and Altair](08-data-visualization-with-matplotlib-plotly-and-altair.md)

**Why here:** when BI tools are too limited, or for reports, notebooks,
and monitoring, you need to create charts in code. Good visualisation is a
skill, not a decoration.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Choosing a chart for a question: comparison (bar), trend (line), distribution (histogram, box, violin), relationship (scatter), composition (stacked bar; avoid most pie charts), ranking, and geographic maps |
| Basics | **matplotlib**: figure/axes model, `plot`, `bar`, `hist`, `scatter`, labels, titles, legends, saving figures |
| Basics | Perceptual principles: position beats length beats area beats colour; zero baselines for bars; consistent scales |
| Intermediate | **Plotly** (interactive: hover, zoom, `plotly.express`, dashboards with Dash) and **Altair** (declarative grammar of graphics, Vega-Lite) |
| Intermediate | **seaborn** for statistical plots (distributions, regressions, heatmaps) |
| Intermediate | Plotting large data: aggregate first, bin (2D histograms, hexbin, datashader), sample, and avoid overplotting |
| Intermediate | Colour: sequential, diverging, and categorical palettes; colour-blind-safe choices; consistent encodings |
| Intermediate | Specific data-engineering charts: cohort heatmaps, funnel charts, retention curves, time series with intervals, pipeline SLA charts |
| Advanced | Showing uncertainty: error bars, confidence bands, and fan charts |
| Advanced | Small multiples, annotation, direct labelling, and reducing chart junk (Tufte) |
| Advanced | Reusable plotting libraries/themes for your team; testing plots (image regression); generating reports (Quarto, Jupyter, Evidence) |
| Advanced | Dashboards in code: Streamlit, Dash, Panel, Evidence — when to use them rather than BI tools |
| Advanced | Accessibility and ethics: truncated axes, cherry-picked ranges, and misleading dual axes |

**How to learn it**

1. Read the topic file.
2. Take one dataset and draw three different charts for the same question;
   pick the clearest and explain why.
3. Redraw a cluttered chart from a real report with fewer, clearer
   elements.

**Hands-on exercise — `experiments/08_visualization/`**

1. Recreate the same insight (experiment result with interval) in
   matplotlib, Plotly, and Altair; compare code and results.
2. Plot 10 million points correctly (aggregation/binning) and show what
   naive plotting does.
3. Build a cohort retention heatmap and a funnel chart from your earlier
   outputs.
4. Create a small Streamlit or Evidence app showing key metrics with
   filters.
5. Write a team style module (palette, fonts, sizes) and apply it across
   charts.
6. Critique five misleading charts and fix them.

**Checkpoint:**

- [ ] Choose a chart type for a question.
- [ ] Produce clear charts in all three libraries.
- [ ] Plot large data and show uncertainty.
- [ ] Spot and fix misleading visualisations.

**Common mistakes:** pie charts with ten slices; truncated bar axes;
dual axes that imply false correlations; plotting millions of raw points.

---

### Topic 09 — [Data storytelling and stakeholder communication](09-data-storytelling-and-stakeholder-communication.md)

**Why it comes last:** an analysis nobody understands or acts upon has no
value. Communication is the multiplier on everything else in the module
and a key senior skill.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Start from the decision: who is the audience, what do they need to decide, and by when? |
| Basics | The structure: question → answer first → evidence → caveats → recommendation (the pyramid principle) |
| Basics | Writing a clear one-paragraph conclusion: what we found, how sure we are, what we recommend |
| Intermediate | Choosing the right level of detail for executives, product managers, engineers, and analysts |
| Intermediate | Presenting uncertainty honestly: intervals, ranges, scenarios, and "what would change my mind" |
| Intermediate | Data narratives: context, tension, resolution; using a few charts well; annotating charts with the point |
| Intermediate | Written artefacts: analysis docs, experiment readouts, incident postmortems (links to Module 2.20 Topic 10), and ADRs (Module 2C.8) |
| Intermediate | Presentations: slides vs notebooks vs docs; walking through a chart; handling questions and pushback |
| Advanced | Working with stakeholders: clarifying vague requests, scoping, saying "no" or "not yet", managing expectations on data quality and timelines |
| Advanced | Communicating data-quality issues and incidents without hiding or panicking: impact, cause, fix, prevention |
| Advanced | Influencing without authority: building trust with consistent metrics and reliable delivery; data literacy programs |
| Advanced | Ethics: privacy, fairness, and the responsibility not to over-claim; recognising when data cannot answer the question |
| Advanced | Reproducibility: versioned notebooks/queries, data snapshots, and making results auditable |
| Advanced | Tools: Quarto, Jupyter, Evidence, slide decks, and internal data portals |

**How to learn it**

1. Read the topic file.
2. Take an analysis from this module and write the answer-first summary in
   three sentences.
3. Rehearse presenting it to someone non-technical in three minutes.

**Hands-on exercise — `experiments/09_storytelling/`**

1. Write an experiment readout (one page): decision, result with
   interval, guardrails, caveats, recommendation, next steps.
2. Turn the same material into a five-slide deck for executives.
3. Write a short incident note to stakeholders about a data-quality
   issue: what happened, impact, fix, prevention.
4. Practise a mock Q&A with someone who challenges your result; record
   what questions you could not answer and close the gaps.
5. Review one of your old dashboards and rewrite its title, subtitles, and
   annotations so it states its point.

**Checkpoint:**

- [ ] Structure a clear, answer-first analysis.
- [ ] Present uncertainty honestly.
- [ ] Communicate data issues calmly and clearly.
- [ ] Tailor the message to the audience.

**Common mistakes:** burying the answer; showing every chart you made;
hiding caveats or drowning the reader in them; speaking in jargon.

---

## 10. Module mini-project — an experiment and product-analytics report

**Goal:** deliver, end to end, the data pipeline and written analysis a
product team would use to make a launch decision.

**Requirements**

1. A generator produces 1M+ users and event data with a built-in A/B
   experiment (known true lift), bots, late events, and a sample-ratio
   bug in one run.
2. Pipelines in DuckDB/dbt (or Spark) produce: assignment, exposure, daily
   user metrics, cohort retention, a funnel, and a results table —
   incremental and idempotent.
3. Statistical analysis: sample-size plan, SRM check, test with interval,
   multiple-comparison handling, CUPED, and a bootstrap check; tests
   verifying that your code recovers the true lift.
4. Sketches: unique users and latency percentiles via HLL/t-digest stored
   in aggregate tables.
5. A forecast with backtests for expected daily orders and an anomaly
   alert on pipeline volume.
6. A BI dashboard (Metabase or Superset) with focused cards and governed
   access, plus three code-made charts.
7. A one-page readout and a five-slide executive summary with a clear
   recommendation.

**Done when** your code recovers the planted effect, the SRM check catches
the planted bug, the dashboard loads in seconds, and a non-technical
reviewer can state the decision and the uncertainty after reading your
report.

---

## 11. Module self-assessment — exit criteria

You have completed this module when you can do all of the following
**without notes**:

- [ ] Summarise large data honestly with mergeable statistics.
- [ ] Choose among exact, sampled, and sketch-based computation.
- [ ] Run hypothesis tests, intervals, power analysis, and corrections.
- [ ] Build an A/B testing pipeline and detect SRM.
- [ ] Write cohort, funnel, and retention SQL.
- [ ] Decompose, forecast, and backtest a time series.
- [ ] Build fast, governed dashboards.
- [ ] Create clear charts and present findings with calibrated confidence.

---

## 12. Recommended reading and references

- *Trustworthy Online Controlled Experiments* — Kohavi, Tang, Xu (the A/B
  testing reference).
- *Statistics Done Wrong* — Alex Reinhart; *Think Stats* — Allen Downey.
- *Forecasting: Principles and Practice* — Hyndman and Athanasopoulos
  (free online).
- *Storytelling with Data* — Cole Nussbaumer Knaflic; *The Visual Display
  of Quantitative Information* — Edward Tufte.
- Apache DataSketches documentation; the HyperLogLog paper.
- Documentation for scipy.stats, statsmodels, Plotly, Altair, Metabase,
  and Superset.

---

## 13. Where this module leads

- **Stage 4 (Mathematics for Machine Learning)** deepens probability,
  statistics, and linear algebra.
- **Stage 5 (Machine Learning Foundations)** moves from description and
  inference to prediction.
- **Stage 10 (Evaluation and Experimentation)** reuses A/B testing and
  statistical rigour for AI systems.
- **Module 2C.10** continues from analysis to ML feature and training data
  pipelines.
