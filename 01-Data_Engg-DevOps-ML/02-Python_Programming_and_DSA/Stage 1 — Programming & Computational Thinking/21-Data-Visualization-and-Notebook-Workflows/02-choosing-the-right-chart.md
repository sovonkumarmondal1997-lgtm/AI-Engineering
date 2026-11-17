# Choosing the Right Chart

**Stage 1 — Programming & Computational Thinking · Module 21 — Data Visualization and Notebook Workflows · Lesson 02**

> **Core principle:** choose a chart to answer a question about data—not because a plotting library makes a chart easy to produce.

## Learning outcomes

By the end of this lesson, you should be able to:

1. Translate a decision or analytical question into a visual comparison task before choosing a chart type.
2. Distinguish nominal and ordinal categories, discrete and continuous measurements, and temporal observations.
3. Select and justify charts for comparison, distribution, relationship, time trend, composition, geography, ranking, many measures, and uncertainty.
4. Detect misleading scales, missing denominators, incompatible panels, overplotting, misleading smoothing, and other integrity failures.
5. Choose colour, labels, annotations, layout, and accessibility features that preserve meaning for different audiences.
6. Produce and critique a small pipeline-health chart set, explaining the decision each chart supports.
7. Recognise where advanced statistical or high-dimensional techniques are useful—and where their interpretation exceeds this lesson's scope.

## 1. Why chart selection is an analytical decision

A chart is an argument about what matters in a dataset. The choice of mark, axis, scale, aggregation, and annotation determines which comparisons are easy to see and which are hidden. A technically valid figure can still be analytically misleading: a truncated bar chart can exaggerate a small difference, a line can imply continuity between missing observations, and a dual-axis chart can manufacture a visual relationship between unrelated series.

In data engineering, visualisation helps answer questions such as:

- At which pipeline stage did row counts fall unexpectedly?
- Is job duration becoming slower, or are a few outliers driving the mean?
- Which columns have rising null rates, and on which days?
- Is data freshness lag increasing after a deployment?
- Which pipelines account for the most cost, and are the units comparable?

In AI engineering, the same habits later support model evaluation: learning curves, normalised confusion matrices, calibration plots, ROC/PR curves, embedding projections, token/cost distributions, and latency-versus-quality trade-offs. These are previews here, not a substitute for the later statistics and ML-evaluation modules.

A chart should make a defensible statement. Before plotting, complete this sentence:

> “I need to compare/understand **___** so that **___** can decide **___**.”

If the sentence is unclear, the chart choice is premature.

## 2. A decision framework

Use the following sequence every time.

1. **Question:** What decision, comparison, or uncertainty must the viewer understand?
2. **Data type:** Are the variables nominal, ordinal, discrete, continuous, temporal, or geographic? What is one row?
3. **Comparison task:** Are you comparing categories, inspecting a distribution, studying a relationship, showing a trend, decomposing a total, ranking, mapping, or communicating uncertainty?
4. **Candidate chart:** Choose the simplest visual encoding that makes the intended comparison easy.
5. **Integrity checks:** Verify denominators, units, aggregation windows, axis baselines/scales, missing data, sample sizes, and whether the chart implies unsupported continuity or causation.
6. **Communication checks:** Make the title informative, order categories intentionally, label directly where useful, use accessible colours and typography, and provide context or a companion table when precision matters.
7. **Review:** Ask what a reasonable reader might conclude—and whether the data actually support it.

### 2.1 Understand the data types

- **Nominal categorical:** labels without an inherent order, such as pipeline name or cloud region. Choose an order based on the question (often value, alphabetic order, or a stable business-defined order).
- **Ordinal categorical:** categories with a meaningful order, such as low/medium/high severity. Preserve that order rather than sorting arbitrarily.
- **Discrete numerical:** countable values, often integers, such as failed tasks or rows rejected. A count may be plotted as a bar, histogram, or time series depending on the question.
- **Continuous numerical:** measurements on a scale, such as duration in seconds, memory in MiB, or cost in currency. Distributions and relationships are common tasks.
- **Temporal:** timestamps or intervals. A line chart is often suitable when x is ordered time, but sampling cadence, missing intervals, timezone, and aggregation must be understood.
- **Geographic:** locations or regions with spatial meaning. A map is useful only when geography is part of the question; a ranked bar chart may be clearer if the task is simply to compare regional values.

A variable's storage type is not always its analytical type. An integer column containing pipeline IDs is categorical, not a measurement. A timestamp converted to a string is still temporal in meaning.

## 3. Chart-choice matrix

Treat this as a starting point, not a law. The correct choice depends on the question, data volume, audience, and error costs.

| Question / task | Typical chart | Data shape and useful encoding | Strengths | Limitations and checks | Misleading alternative to avoid |
|---|---|---|---|---|---|
| Compare values across categories | Bar chart; dot plot | Category + one numeric measure; position/length | Direct magnitude comparison; horizontal bars fit long labels | Bar length should normally start at zero; show denominator and units | 3-D bars; truncated bar baseline; pie with many slices |
| Understand one variable's distribution | Histogram, KDE, ECDF, box plot, violin plot | Many observations of one numeric variable | Reveals spread, skew, tails, quantiles, and multimodality (depending on display) | Histogram depends on bins; KDE depends on bandwidth; box plots hide detail; show sample size | Bar chart of means only; a smoothed density presented as raw observations |
| Understand a relationship between two numeric variables | Scatter plot; hexbin; 2-D histogram | Paired x/y observations | Shows association, clusters, outliers, and non-linear structure | Overplotting; association is not causation; density views hide individual points | Dual-axis lines implying a relationship; a fitted line without context |
| Change over time | Line chart; area chart for cumulative/part-to-whole over time | Time-ordered observations and a measure | Shows direction, cycles, step changes, and event timing | Respect gaps and irregular cadence; explain aggregation and timezone | Dense bars for a long high-frequency series; connecting across unknown gaps |
| Part-to-whole composition | Stacked bar; 100% stacked bar; treemap | Components within totals, possibly across groups | Stacked bar shows totals and composition; 100% bar compares shares; treemap handles hierarchy | Only first stack segment shares a common baseline; small segments are hard to compare | Pie/donut with many slices; comparing areas with no clear labels |
| Rank categories | Sorted bar; lollipop | Category + numeric measure | Makes top/bottom and ordering explicit | Decide whether ties and negative values matter; label units | Unsorted bars that force visual searching |
| Many categories × many measures | Heatmap; small multiples | Matrix of categories × measures/time | Shows patterns and outliers without a spaghetti plot | Heatmap needs a meaningful colour scale; panels need comparable scales where comparisons are intended | Overloaded multi-series line chart; inconsistent panel scales without disclosure |
| Show uncertainty or ranges | Error bars; confidence-interval band; forecast fan | Estimate plus interval/range and a defined uncertainty meaning | Prevents point estimates from appearing exact | State what interval means and how it was obtained; do not imply certainty beyond data | Point estimates alone when uncertainty changes the decision |
| Compare geographic values | Choropleth or symbol map; sometimes ranked bar | Region/location + measure | Reveals spatial clustering when location matters | Area distorts perception; population/denominator matters; map projections and missing regions matter | Map for a non-spatial ranking; colour map without legend or denominator |

### 3.1 Fast decision guide

- **“Which is larger?”** Use a bar or dot plot; sort when rank matters.
- **“What values are typical, and how variable are they?”** Use a histogram, ECDF, box plot, or violin plot; include sample size.
- **“Do two measurements move together?”** Start with scatter or hexbin; avoid implying causality.
- **“How did this change over time?”** Use a line chart with explicit time semantics and visible gaps.
- **“What makes up the total?”** Use stacked bars or 100% stacked bars when component comparisons are meaningful.
- **“Which categories have the highest values?”** Use a sorted bar/lollipop.
- **“Where do many categories and measures differ?”** Use a heatmap or small multiples.
- **“How uncertain is the estimate?”** Use a clearly defined interval, band, or fan chart—not only a point.

## 4. Basic: match the chart to the question

### 4.1 Comparison: bars and dots

Bars are effective because viewers compare position and length. A dot plot can be less visually heavy and often works well when exact comparisons across many categories matter. For bar charts, start the quantitative axis at zero unless there is a carefully explained, exceptional reason not to; bar length encodes magnitude from its baseline.

```python
import matplotlib.pyplot as plt

pipelines = ["orders", "events", "billing", "catalog"]
failed_runs = [8, 3, 12, 5]  # synthetic count; 30 runs observed per pipeline

fig, ax = plt.subplots(figsize=(7, 4))
order = sorted(zip(failed_runs, pipelines))
values = [item[0] for item in order]
names = [item[1] for item in order]
ax.barh(names, values, color="steelblue")
ax.set(xlabel="Failed runs (count)", ylabel="Pipeline",
       title="Billing has the most failed runs in this sample")
ax.set_xlim(0, max(values) * 1.15)  # preserve zero baseline
for y, value in enumerate(values):
    ax.text(value + 0.15, y, str(value), va="center")
fig.tight_layout()
plt.show()
plt.close(fig)
```

**Observe:** billing ranks highest, and the zero baseline makes the magnitude differences visible without exaggerating them. The denominator (30 runs per pipeline) is stated in the surrounding context; for a report, include it in a subtitle or data note. If pipelines had different numbers of runs, compare failure rates as well as counts.

### 4.2 Distribution: histogram, KDE, ECDF, box, and violin

A distribution chart answers more than “what is the average?” It can reveal skew, multiple modes, long tails, and unusual values.

- **Histogram:** bins observations into intervals. Explicitly choose or document bins because bin width can change the apparent shape.
- **KDE (kernel density estimate):** a smoothed estimate of density, not a count of observations. Bandwidth controls smoothness and can hide or invent apparent modes.
- **ECDF:** empirical cumulative distribution function. At x, the y-value is the fraction of observations at or below x. It avoids histogram bins and is useful for percentile questions.
- **Box plot:** compactly summarises median, quartiles, and whisker/outlier convention; it does not show every feature of the distribution.
- **Violin plot:** combines a mirrored density shape with summary cues; density can be hard to interpret for small samples.

```python
import numpy as np
import matplotlib.pyplot as plt

# Deterministic synthetic pipeline durations (seconds); right-skewed by construction.
rng = np.random.default_rng(17)
duration_s = rng.lognormal(mean=2.5, sigma=0.45, size=240)

fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
axes[0].hist(duration_s, bins=20, color="slateblue", edgecolor="white")
axes[0].set(title="Duration distribution", xlabel="Duration (s)", ylabel="Runs")

sorted_values = np.sort(duration_s)
ecdf_y = np.arange(1, len(sorted_values) + 1) / len(sorted_values)
axes[1].step(sorted_values, ecdf_y, where="post", color="darkgreen")
axes[1].set(title="Empirical cumulative distribution", xlabel="Duration (s)", ylabel="Fraction of runs")
axes[1].set_ylim(0, 1.02)
plt.show()
plt.close(fig)
```

**Observe:** the histogram shows how observations are distributed across intervals; the ECDF answers questions such as “what fraction completed within 20 seconds?” Do not call this data real production telemetry: it is generated synthetically.

### 4.3 Relationship: scatter and hexbin

A scatter plot shows paired observations. Use position for x and y; colour, marker, or size can encode another variable if the legend explains it. When points overlap heavily, opacity can help, but a dense cloud may remain unreadable. Hexbin or a 2-D histogram summarises the number of observations in spatial cells.

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(21)
input_rows = rng.integers(1_000, 50_000, size=900)
duration_s = 4 + input_rows / 5_000 + rng.normal(0, 1.8, size=input_rows.size)

fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
axes[0].scatter(input_rows, duration_s, s=15, alpha=0.25, color="teal")
axes[0].set(title="Scatter with transparency", xlabel="Input rows (count)", ylabel="Duration (s)")
axes[1].hexbin(input_rows, duration_s, gridsize=28, mincnt=1, cmap="viridis")
axes[1].set(title="Hexbin density", xlabel="Input rows (count)", ylabel="Duration (s)")
plt.show()
plt.close(fig)
```

**Observe:** alpha reveals some overlap; hexbin makes dense regions easier to locate. The synthetic relationship does not prove that input rows alone cause duration—the noise and any omitted variables are part of the example's limitations.

### 4.4 Trend, composition, ranking, and uncertainty

- Use a **line** when the x-axis has a meaningful order, especially time. Use an **area** chart when cumulative magnitude or composition over time is the question and filled regions remain legible.
- Use **stacked bars** to show total and components; use **100% stacked bars** to compare proportions while deliberately discarding differences in total size. If precise comparison of middle segments matters, a grouped bar or table may be better.
- Use a **sorted bar/lollipop** for ranking. Keep the sort order consistent across repeated reports.
- Use **error bars or confidence bands** only after defining what the interval represents. It might be a standard deviation, standard error, confidence interval, prediction interval, or operational range; these are not interchangeable.

### 4.5 Geography and many measures

Use maps when location itself is analytically meaningful (for example, regional freshness lag). A map can be poor for simple ranking because geographic area and shape distract from precise magnitude. Consider a sorted bar chart instead. For many measures across categories, a heatmap or small multiples can reduce clutter, but a heatmap's colour scale must have a clear meaning and comparable panels should use comparable scales.

## 5. Intermediate: chart integrity and visual perception

### 5.1 Integrity rules

1. **Bar baselines:** start at zero for bars encoding magnitude. A dot plot can use a narrower axis when the displayed position is clearly labelled and does not pretend to encode bar length.
2. **Comparable panels:** use the same scale when the reader is expected to compare magnitude across panels. If panels use different scales for local pattern detection, disclose it clearly.
3. **Avoid exaggerating axes:** truncation is not inherently forbidden for every line chart, but it must not conceal the baseline or exaggerate change. Show context, labels, and full range where relevant.
4. **Show denominators:** “12 failures” is not comparable to “12 failures” if one pipeline ran 20 times and another 2,000 times. Report counts and rates with denominators when both matter.
5. **Label units:** seconds vs milliseconds, dollars vs thousands of dollars, rows vs millions of rows. Never force the audience to infer units.
6. **Use dual axes cautiously:** separate scales can create visual correlations. Prefer separate aligned panels, indexed values with explicit definitions, or direct comparisons after justified normalisation. If a twin axis is unavoidable, label both axes conspicuously and explain the scales.
7. **Label log scales explicitly:** a logarithmic axis changes the meaning of visual distance. State “log scale” and use readable ticks. Never silently switch scales to make values appear closer or farther apart.
8. **State aggregation:** hourly mean, daily p95, and total cost are different summaries. Include the aggregation window and percentile/statistic.
9. **Represent missingness honestly:** a missing observation is not zero. Do not connect a line across gaps unless interpolation is justified and explicitly marked.

### 5.2 Perceptual accuracy

For precise comparisons, **position on a common scale** is generally easiest to compare, followed by length. Angle and area are less precise, and colour intensity is best for broad pattern recognition rather than exact value reading. Use a chart's visual channels according to their perceptual strengths:

- position: primary numeric comparison;
- length: magnitude with a clear baseline;
- colour intensity: ordered numeric magnitude;
- hue: category, not magnitude;
- size/area: secondary magnitude only when needed and carefully scaled;
- shape/line style: redundant category encoding when it remains legible.

A bubble's **area**, not radius, should represent the value if bubble area is intended to encode magnitude. Doubling the radius quadruples area and can greatly exaggerate differences.

### 5.3 Overplotting remedies

Use the least lossy remedy that makes the question answerable:

- **Alpha transparency:** helps reveal density but does not remove overlap.
- **Jitter:** adds small random offsets to discrete/near-identical positions to reveal overlapping observations. Explain it; jitter changes displayed positions and is not suitable for every task.
- **Hexbin / 2-D histogram:** aggregate counts into cells for large point clouds.
- **Sampling:** draw a reproducible subset when individual points are still useful. State the sample strategy and size; sampling may omit rare outliers.
- **ECDF:** summarises a univariate distribution without bins and supports percentile comparisons.
- **Small multiples/facets:** separate groups into panels rather than drawing dozens of lines on one axis.

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(9)
x = rng.normal(size=8_000)
y = 0.6 * x + rng.normal(size=8_000)

fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), constrained_layout=True)
axes[0].scatter(x, y, s=5, alpha=0.12)
axes[0].set_title("Alpha scatter")
axes[1].hexbin(x, y, gridsize=30, mincnt=1, cmap="viridis")
axes[1].set_title("Hexbin")
axes[2].hist2d(x, y, bins=35, cmap="viridis")
axes[2].set_title("2-D histogram")
for ax in axes:
    ax.set_xlabel("x (synthetic units)")
    ax.set_ylabel("y (synthetic units)")
plt.show()
plt.close(fig)
```

**Observe:** the panels encode the same observations in different ways. The density displays make concentration easier to see; they do not show every individual point. The best choice depends on whether the task is finding clusters, estimating density, or inspecting outliers.

### 5.4 Colour semantics and accessibility

Choose a palette by the meaning of the data:

- **Sequential:** low-to-high ordered values, such as null rate; examples include `viridis` and `cividis`.
- **Diverging:** values around a meaningful centre such as zero or a target; use two contrasting directions and a neutral centre (for example, `RdBu` with a justified centre).
- **Qualitative:** distinct categories with no numerical order; examples include `tab10` or ColorBrewer's `Set2` when the number of categories is appropriate.

Avoid rainbow/`jet` palettes for ordered values: uneven perceived changes and confusing hue transitions can create false boundaries. Keep category-to-colour mapping stable across charts. Do not rely on colour alone; add labels, marker shapes, line styles, or direct annotations. Check contrast, colour-vision accessibility, readability in grayscale, and whether the figure remains understandable when printed.

### 5.5 Distribution integrity and sample sizes

Every distribution summary hides some information. Histograms depend on bin edges; KDEs depend on bandwidth; box plots suppress multimodality; violins can suggest precision unsupported by a small sample. Display sample sizes, state filtering rules, and use the same bins or scale when distributions are compared directly. If a sample is drawn from a large dataset, state how and why it was sampled.

### 5.6 Time-series integrity

Before connecting points, ask:

- **Cadence:** are timestamps regularly spaced, or do some intervals contain more observations?
- **Aggregation window:** are values raw, hourly totals, daily means, or percentiles? The choice changes the story.
- **Timezone:** are timestamps UTC or local time? Daylight-saving changes can produce duplicate or missing local hours. Normalize consistently and label the timezone.
- **Missing gaps:** missing means unknown, not zero. Break the line at missing intervals unless an explicitly justified interpolation is shown.
- **Seasonality:** day-of-week or time-of-day patterns may explain apparent trends. Do not attribute a seasonal pattern to a release without examining context.

### 5.7 Titles, annotations, and context

Prefer a title that states a finding or decision-relevant question, not just the chart type. “p95 job duration rose after deployment” is more useful than “Job duration.” The finding must be supported by the chart and its uncertainty; do not state causality from temporal coincidence alone. Annotate relevant releases, incidents, thresholds, or data-quality events. Include source, date range, filters, and aggregation in a subtitle or note when needed.

## 6. Data-engineering and AI-engineering chart patterns

| Operational question | Candidate chart | Decision supported | Integrity notes |
|---|---|---|---|
| Where did rows disappear? | Row-count funnel or stage-by-stage bars | Find the stage requiring investigation | Label stage counts and retention rates; funnel widths can mislead if not proportional |
| Is data getting stale? | Freshness/lag line chart with threshold | Alert, investigate source, or adjust SLA | Define lag as `now - latest_event_time`; clarify UTC and late-arriving data |
| Which columns have rising null rates? | Column × day heatmap | Prioritise schema/source investigation | Sequential palette from 0%; show sample denominator and missing days |
| When did schema drift occur? | Timeline/event annotations | Correlate change with deploys and pipeline runs | Distinguish detected time from effective time; don't imply causality without evidence |
| Are job durations becoming less reliable? | Box plots by job or time window | Investigate variance and tail latency | Show n; use same units/scales; supplement with p95/p99 when operationally relevant |
| Which pipelines drive spend? | Sorted bar or time series by pipeline | Prioritise cost review | State currency, billing period, allocation method, and whether shared costs are apportioned |
| Is a model learning? | Learning curves | Diagnose under/over-fitting patterns | Later ML module: specify train/validation metric and split methodology |
| Which classes are confused? | Normalised confusion matrix | Identify class-specific error patterns | State row/column normalisation and support counts; raw counts may also matter |
| Are predicted probabilities calibrated? | Reliability/calibration plot | Assess probability quality | Later evaluation module: include binning, sample size, and uncertainty |
| How does a classifier trade off detection and false positives? | ROC or precision-recall curve | Compare thresholds/models in context | Later evaluation module: metric choice depends on class balance and decision costs |
| Are embeddings separated? | PCA/UMAP projection | Explore possible structure | Projection can distort distances and clusters; not proof of semantic separation |
| What drives token or inference cost? | Histogram/ECDF and cost-over-time line | Set budgets or investigate outliers | Define token accounting, currency, sample window, and tail quantiles |
| Which model setting balances latency and quality? | Latency-quality scatter with Pareto frontier | Choose a feasible trade-off | Define quality metric and workload; distinguish observed points from frontier estimates |

These are chart patterns, not conclusions. A chart identifies a pattern worth investigating; causal attribution usually needs additional evidence.

## 7. Advanced: visualisation grammar and design

### 7.1 Marks, encodings, scales, and facets

A useful mental model is a small visual grammar:

- **Marks:** points, lines, bars, areas, text, cells.
- **Channels/encodings:** x, y, colour, size, shape, opacity, and facet/panel.
- **Scales:** map data values to positions, lengths, colours, or sizes; examples include linear, logarithmic, and categorical scales.
- **Facets:** repeat a chart by category or condition to compare patterns without overloading a single panel.

For example, a pipeline-duration scatter plot might use x = input rows, y = duration seconds, colour = pipeline category, and facet = region. Each added channel increases cognitive load. Use only encodings that serve the question and can be decoded accurately.

The Grammar of Graphics informs tools such as **Altair/Vega-Lite** and **plotnine**. This lesson does not teach those APIs; the transferable skill is to reason explicitly about marks, channels, scales, and facets regardless of library.

### 7.2 Cognitive load, data-ink, and layout

Remove decoration that does not help interpretation, but do not treat “less ink” as an absolute goal. Gridlines can help estimate values; annotations can provide essential context. Prioritise:

- one clear takeaway per figure;
- consistent category order and colour mapping;
- direct labels where they reduce legend searching;
- whitespace between groups and panels;
- readable typography and a clear hierarchy between title, axes, annotations, and notes;
- small multiples with shared scales when magnitude comparisons matter;
- sparklines for compact trend context, not for precise value reading;
- event annotations at the time they occurred, with a legend/note explaining event symbols.

Do not put every available metric into one dashboard-like figure. Use a small set of charts where each one answers a distinct question.

### 7.3 Misleading-chart catalogue: diagnose and repair

#### A. Truncated bar axis

**Problem:** bars visually encode length from a baseline; a y-axis beginning at 90 makes 91 and 99 look dramatically different.

**Repair:** start bars at zero and label units. If the decision is about small differences, use a dot plot with a clearly marked scale or pair the chart with a table—do not silently crop bars.

```python
import matplotlib.pyplot as plt

labels = ["A", "B", "C"]
values = [91, 95, 99]
fig, axes = plt.subplots(1, 2, figsize=(8, 3.5), constrained_layout=True)
axes[0].bar(labels, values)
axes[0].set_ylim(90, 100)
axes[0].set_title("Misleading: baseline truncated")
axes[1].bar(labels, values)
axes[1].set_ylim(0, 105)
axes[1].set_title("Corrected: zero baseline")
for ax in axes:
    ax.set_ylabel("Score (points)")
plt.show()
plt.close(fig)
```

The left chart exaggerates differences because the bars begin at 90. The right chart preserves the magnitude context. The first chart is shown only as a deliberately misleading example.

#### B. Cherry-picked time range

**Problem:** showing only the final few days can make normal variation look like a sustained collapse or recovery.

**Repair:** show the decision-relevant period and provide the selected range in the title/note. If a zoom is useful, pair it with a wider-context panel. Do not choose the window only because it supports the desired narrative.

#### C. Inconsistent histogram bins

**Problem:** comparing histograms with different bin widths or edges makes shapes and heights incomparable.

**Repair:** use common bin edges for the groups being compared and state whether y represents counts, proportions, or density. If sample sizes differ, consider ECDFs or density-normalised histograms, while still reporting n.

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(4)
control = rng.normal(10, 2, 500)
variant = rng.normal(10.5, 2.2, 420)
# Shared edges span both samples, so observations are not silently dropped.
low = min(control.min(), variant.min())
high = max(control.max(), variant.max())
padding = 0.02 * (high - low)
common_bins = np.linspace(low - padding, high + padding, 19)
fig, ax = plt.subplots(figsize=(7, 4))
# Density normalisation makes shapes comparable despite unequal sample sizes.
ax.hist(control, bins=common_bins, density=True, alpha=0.55, label="Control (n=500)")
ax.hist(variant, bins=common_bins, density=True, alpha=0.55, label="Variant (n=420)")
ax.set(xlabel="Duration (s)", ylabel="Probability density (1/s)",
       title="Duration distributions: shared bins and density scale")
ax.legend()
plt.show()
plt.close(fig)
```

#### D. Incorrect area scaling

**Problem:** a bubble's radius is set proportional to a value, so its area grows with the square of that value and exaggerates the difference.

**Repair:** if using bubbles, scale area to the value (radius proportional to square root of value) and provide a size legend. If exact comparison matters, use bars or dots.

#### E. Dual-axis spurious correlation

**Problem:** two unrelated series can be made to rise together by independently choosing left and right axis ranges.

**Repair:** use aligned panels with explicit units, or normalise both series to a stated baseline only when indexed change is the actual question. Do not infer correlation from matching shapes created by arbitrary axes.

#### F. Smoothing hides spikes

**Problem:** a rolling mean makes a noisy series easier to read but can hide a short operational incident.

**Repair:** show raw values faintly with the smoothed series, report the window, and mark incidents/thresholds. For alerting decisions, do not rely on a smoothed line alone.

#### G. Survivorship bias

**Problem:** only successful pipelines, retained users, or models that completed are plotted. Failed or dropped cases vanish from the view.

**Repair:** state inclusion/exclusion rules, show counts excluded, and compare completion/failure rates. Ask who or what is missing from the dataset.

#### H. Simpson's paradox

**Problem:** an aggregate comparison reverses after stratifying by a relevant group because the groups have different weights or base rates.

**Repair:** inspect group-level rates and denominators; show stratified small multiples or a table alongside the aggregate. Do not assume aggregation preserves every relationship. The pattern requires careful analysis; a chart alone does not explain its cause.

#### I. Ecological fallacy

**Problem:** a relationship between group-level aggregates is assumed to hold for individuals within those groups.

**Repair:** distinguish group-level from individual-level claims and use data at the level that matches the question. Aggregate regional latency and regional traffic volume do not prove that individual high-volume requests are slower.

#### J. 3-D effects

**Problem:** perspective and occlusion distort lengths and make comparison harder.

**Repair:** use 2-D bars, dots, or small multiples. Use a 3-D view only when the third spatial dimension is real and necessary to the analysis, not as decoration.

### 7.4 Uncertainty without false precision

An estimate is not the whole result. A point estimate with no uncertainty can suggest that a small difference is definitive. Use error bars, confidence bands, quantile dot plots, or forecast fans only after stating what the interval represents and what population/process it refers to.

- **Confidence interval:** describes uncertainty from a specified estimation procedure under its assumptions; it is not automatically a range containing 95% of individual observations.
- **Prediction interval:** concerns a future/new observation and is typically wider than an interval for a mean.
- **Operational range:** may be a threshold or observed min–max range, not a statistical interval.
- **Forecast fan:** shows multiple forecast quantiles or scenarios over time; label quantiles and distinguish observed from forecast data.

Bootstrap confidence bands, quantile dot plots, and A/B-test effect-size intervals belong with the later statistics/evaluation stages. Here, the key lesson is to label uncertainty honestly and avoid false precision.

### 7.5 High-dimensional displays and interpretation limits

- **PCA/UMAP projections:** reduce many dimensions to two or three for exploration. Distances and clusters can be distorted by the projection; UMAP parameters and random seeds can change the display. Do not interpret apparent separation as proof without domain checks and validation.
- **Parallel coordinates:** show multiple numeric dimensions as parallel axes; many lines quickly clutter and require scaling choices. Normalize only with a clear explanation because normalization changes comparisons.
- **Pair plots:** show pairwise relationships among several variables; useful for exploration but expensive and visually crowded as feature count grows.
- **Correlation heatmaps with clustering:** reveal patterns in pairwise correlations, but correlation is not causation, colour scales can exaggerate small differences, and clustering depends on distance/linkage choices. Use a diverging palette centred at zero when zero is meaningful.

These are exploratory aids. Feature engineering, dimensionality reduction, and formal interpretation belong to their appropriate later modules.

### 7.6 Accessibility and inclusive communication

Accessibility is part of correctness: a result that a reader cannot decode is not communicated reliably.

- Use readable font sizes and sufficient foreground/background contrast.
- Check palettes for common colour-vision deficiencies; tools such as `colorspacious` or browser-based simulators can help, but no palette replaces human review.
- Do not encode categories using colour alone; use direct labels, markers, line styles, or patterns as redundant cues.
- Use colour scales with perceptually sensible ordering for numeric values; avoid rainbow palettes.
- Check grayscale and print output.
- Provide alt text and, for complex charts, a longer description of the main finding, axes, scale, caveats, and important outliers.
- Avoid tiny labels and legends with many nearly indistinguishable categories.
- Provide an accessible data table or downloadable summary when exact values matter.

### 7.7 Design for the audience

- **Executive:** one decision-relevant takeaway, a clear headline, minimal clutter, key risk/impact, and a next action. Keep supporting detail available.
- **Engineer:** exact units, date range, aggregation, thresholds, failure counts, event annotations, and access to underlying values or a table.
- **Analyst:** enough methodological detail to inspect filters, sample sizes, uncertainty, and alternative views; interactivity may help, but should not conceal the static takeaway.

Pair a chart with a table when the chart reveals the pattern and the table is needed for exact lookup. A “so what?” sentence should state what decision the chart supports and what it cannot establish.

## 8. Practical scenario: a pipeline-health review

Suppose a team needs to decide what to investigate first after a scheduled data pipeline run. Use a compact set of charts, each with a distinct operational decision. The following numbers are **illustrative synthetic values**, not measured production facts.

| Chart | Example design | Decision it supports | Important context |
|---|---|---|---|
| Row-count funnel | Bars for source → parsed → validated → loaded counts | Find the stage with the largest loss | Show both counts and retention percentages; define whether rejected rows are expected |
| Freshness/lag over time | Line of lag in minutes with an SLA threshold | Investigate stale inputs or adjust escalation | UTC, calculation of lag, late events, and threshold definition |
| Null-rate heatmap | Columns × days, sequential palette | Prioritise columns and days for data-quality triage | Denominator per cell, missing days, consistent 0–100% scale |
| Schema-drift timeline | Event marks for detected changes and deployments | Correlate drift with source or release changes | Detection time vs effective time; correlation is not causation |
| Job-duration distribution | ECDF or box plot by job with n and p95 | Identify long-tail jobs and regression candidates | Same units and time window; state filters and sample size |
| Cost by pipeline | Sorted bar by currency for a billing period | Prioritise cost investigation | Allocation rules, shared costs, billing period, and currency |

Do not combine all six into one overloaded chart. A practical report might show the row-count funnel and freshness trend first because they support immediate triage, followed by null-rate and schema-drift views for diagnosis, and duration/cost views for reliability and efficiency work.

### Example: create a compact row-count chart

```python
import matplotlib.pyplot as plt

stages = ["Source", "Parsed", "Validated", "Loaded"]
rows = [100_000, 98_500, 96_200, 95_900]  # synthetic counts from one run
retention_pct = [100 * value / rows[0] for value in rows]

fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar(stages, rows, color="steelblue")
ax.set(title="Loaded rows are 95.9% of source rows",
       xlabel="Pipeline stage", ylabel="Rows (count)")
ax.set_ylim(0, 110_000)
for bar, count, retention in zip(bars, rows, retention_pct):
    ax.annotate(f"{count:,}\n{retention:.1f}% retained",
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8)
fig.tight_layout()
plt.show()
plt.close(fig)
```

**Observe:** the chart makes stage counts and source-relative retention explicit. The 4.1% difference between source and loaded rows is a prompt to investigate, not proof of a defect: some rows may be intentionally filtered. The next step is to inspect expected rejects, row-level reason codes, and denominators.

## 9. Runnable example: a small chart review in code

This independent example demonstrates a sorted ranking and an honest denominator. It intentionally compares failure **rates** from different run counts rather than only comparing raw failure counts.

```python
import matplotlib.pyplot as plt

# Synthetic observation window. Values are counts, not rates.
run_counts = {"orders": 100, "events": 500, "billing": 80, "catalog": 200}
failed_counts = {"orders": 4, "events": 15, "billing": 8, "catalog": 4}

rate_pct = {
    name: 100 * failed_counts[name] / run_counts[name]
    for name in run_counts
}
ordered = sorted(rate_pct.items(), key=lambda item: item[1])
labels = [name for name, _ in ordered]
values = [rate for _, rate in ordered]

fig, ax = plt.subplots(figsize=(7, 4))
ax.barh(labels, values, color="slateblue")
ax.set(title="Billing has the highest failure rate in this sample",
       xlabel="Failed runs (%)", ylabel="Pipeline")
ax.set_xlim(0, max(values) * 1.2)
for index, name in enumerate(labels):
    ax.text(values[index] + 0.1, index,
            f"{failed_counts[name]}/{run_counts[name]} runs",
            va="center", fontsize=8)
fig.tight_layout()
plt.show()
plt.close(fig)
```

The chart supports prioritising billing for investigation during this observation window. It does not establish the cause, nor does it show uncertainty around the rates. If decisions are high-impact or the counts are small, inspect the underlying runs and quantify uncertainty in the appropriate later statistics module.

## 10. Exercises

Complete these before reading the answer key. Use synthetic data or a public dataset whose provenance and licence you understand. For each figure, include a one-sentence takeaway and a note about the limits of the conclusion.

### Exercise 1 — choose for six questions

For each question, choose a chart, explain the data shape/encoding, and name one misleading alternative:

1. Which of eight pipelines has the highest failure rate when run counts differ?
2. What does the distribution of job duration look like, including its tail?
3. Does input row count relate to run duration when there are 100,000 observations?
4. Did freshness lag rise after a deployment, and are there missing measurements?
5. Which columns have the highest null rates over the last 14 days?
6. How uncertain is the estimated difference in mean duration between two variants?

**Acceptance criteria:** every choice follows the question; rates include denominators; time-series gaps and event context are addressed; the large scatter uses a density or sampling strategy; uncertainty is labelled rather than guessed.

### Exercise 2 — repair a truncated y-axis

Create a bar chart for values 91, 95, and 99 with an axis starting at 90. Explain why it misleads, redraw with a zero baseline, and choose a dot plot or table if fine differences need more visual resolution.

**Acceptance criteria:** the flawed version is explicitly marked as misleading; the corrected bar chart starts at zero; units and a finding-oriented title are present.

### Exercise 3 — replace a rainbow heatmap

Create a 5 × 7 synthetic null-rate matrix with values between 0 and 1. Plot it using a sequential palette such as `viridis` or `cividis`, label columns and dates, and add a colourbar labelled “Null rate (%)”. Include a data note describing the denominator.

**Acceptance criteria:** no rainbow palette; a clear sequential scale; units, cell meaning, and denominator are documented; colour is not the only way to identify a critical cell (for example, annotate or tabulate the maximum).

### Exercise 4 — audit a dual-axis chart

Find or construct two series that look correlated when each gets its own y-axis. Redraw as aligned panels with clear units, or index both series to 100 at a stated baseline if relative change is the intended comparison. Explain what the original chart cannot prove.

**Acceptance criteria:** both axes/units are explicit in the flawed version; the repair removes arbitrary scale coupling; the explanation does not infer causation from visual alignment.

### Exercise 5 — pipeline-health page

Design five charts for a “pipeline health” page. Choose from row-count funnel, freshness/lag, null-rate heatmap, schema-drift timeline, job-duration distribution, and cost by pipeline. State the decision each supports and the context/denominator needed.

**Acceptance criteria:** no redundant charts; every chart has a distinct decision; counts and rates are not confused; date ranges, units, and aggregation are documented; at least one chart addresses freshness and one addresses data quality.

### Exercise 6 — critique and redraw ten published charts

Select ten charts from news articles, research papers, or vendor dashboards. For each, record the question, audience, data/denominator, mark and encoding, scale/baseline, aggregation, uncertainty, accessibility, likely misleading interpretation, and a proposed repair. Redraw three of the ten.

**Acceptance criteria:** critique is specific rather than “looks bad”; each chart is assessed for question, encoding, honesty, clarity, and accessibility; three redraws materially improve interpretability; source and context are recorded; do not reproduce proprietary or copyrighted graphics beyond what is needed for critique.

### Exercise 7 — create a work-focused chart-choice cheat sheet

Build a one-page reference for your future work covering pipelines, model evaluation, and costs. For each question, include a chart, a small code pattern, required context, a common failure mode, and a decision supported.

**Acceptance criteria:** includes pipeline row counts/freshness/nulls/durations, AI evaluation previews, and cost/latency trade-offs; notes later-stage statistical dependencies; includes units, denominators, accessibility, and integrity checks.

## 11. Self-check answer key

### 1. For each of six questions, pick a chart and justify, then name one misleading alternative.

For the six questions in Exercise 1, a defensible answer set is:

| Question | Good choice and why | Misleading alternative |
|---|---|---|
| Which pipeline has the highest failure rate when run counts differ? | Sorted horizontal bar or dot plot of failure percentage, with failed/total counts and the observation window | Ranking raw failure counts without showing unequal denominators |
| What does job-duration distribution look like, including its tail? | ECDF plus histogram, or box plot with n and a tail percentile; state units and filters | Comparing means only or using a KDE whose bandwidth hides the tail |
| Does input row count relate to duration at 100,000 observations? | Hexbin or 2-D histogram; optionally a reproducible sample overlay for individual outliers | A fully opaque scatter cloud or a causal claim from association |
| Did freshness lag rise after deployment, and are measurements missing? | Time-ordered line with explicit gaps, deployment annotation, UTC/local-time definition, and a wider-context window | Connecting across missing intervals or attributing the change to deployment from timing alone |
| Which columns have the highest null rates over 14 days? | Column-by-day heatmap with a sequential scale, percentages, denominators, and missing-day distinction | Rainbow palette, unlabelled colour scale, or comparing percentages with very different denominators without context |
| How uncertain is the estimated mean-duration difference between variants? | Difference estimate with a clearly defined confidence interval and sample sizes; method belongs to the later statistics module | Point estimates alone or treating a confidence interval as the range of individual durations |

Other choices can be valid when they answer the same question and state their trade-offs. Explain the encoding and limitation rather than memorising a chart-name mapping.

### 2. Fix a chart with a truncated y-axis, rainbow colormap, and dual axes.

Treat this as one review of a figure with three independent failure modes; Exercises 2–4 let you practise each repair in isolation.

- **Truncated bars:** set a zero baseline and label the units. If only small differences matter, use a dot plot with an explicit axis and contextual reference.
- **Rainbow colormap:** replace with a sequential palette for low-to-high values or a diverging palette centred on a meaningful midpoint such as zero. Add a labelled colourbar and redundant labels for important cells.
- **Dual axes:** split into aligned panels with labelled units and comparable time windows. If relative change is the question, index each series to a clearly stated baseline; do not imply a shared numeric scale or causality.
- **Recheck all three together:** titles state supported findings rather than causal claims; denominators and aggregation are present; scales and units are explicit; accessibility and missing data are addressed.

### 3. Design five charts for a pipeline-health page and name the decision each supports.

One reasonable design:

1. **Row-count funnel:** locate row loss by stage; show counts and source-relative retention, and distinguish expected filtering from unexpected loss.
2. **Freshness lag line:** detect stale inputs; show lag in minutes, UTC timestamps, SLA threshold, and gaps.
3. **Null-rate heatmap:** prioritise column/day data-quality investigations; show percentages, denominators, and a sequential colour scale.
4. **Job-duration ECDF or box plots:** identify slow tails and jobs needing performance review; show n, time window, and units.
5. **Sorted cost-by-pipeline bar:** prioritise cost analysis; show currency, billing period, and allocation method.

A schema-drift timeline can replace or complement one of these if schema changes are the immediate operational concern. There is no universally correct set; each chart must support a distinct decision.

## 12. Pre-publication chart review checklist

### Question and evidence

- [ ] The analytical question and intended decision are stated.
- [ ] The title states a supported finding or clearly framed question.
- [ ] The displayed data match the claim; association is not described as causation.
- [ ] Source, date range, filters, and relevant exclusions are documented.

### Data semantics

- [ ] Variable types and units are correct.
- [ ] Counts, rates, percentages, and denominators are not confused.
- [ ] Aggregation window and statistic (mean, median, p95, total, etc.) are explicit.
- [ ] Missing data are distinguished from zero; time gaps are visible where relevant.
- [ ] Sample size and sampling method are disclosed when they affect interpretation.
- [ ] Uncertainty intervals are named and interpreted correctly.

### Chart and scale integrity

- [ ] The chart type matches the comparison task.
- [ ] Bars use a zero baseline; other axis choices are justified and clearly labelled.
- [ ] Comparable panels use comparable scales, or scale differences are disclosed.
- [ ] Log scales are explicitly labelled.
- [ ] Histogram bins and normalisation are appropriate and consistent across comparisons.
- [ ] Dual axes, smoothing, area encodings, and geographic areas do not create false impressions.
- [ ] Overplotting and excessive categories have been addressed.

### Design and accessibility

- [ ] Category ordering and colour mappings are intentional and consistent.
- [ ] Palette semantics match the data; no rainbow palette for ordered values.
- [ ] Colour is not the sole carrier of meaning; contrast and grayscale are checked.
- [ ] Typography, labels, legends, and annotations are readable.
- [ ] Alt text or a longer description is available for complex figures.
- [ ] The chart is not overloaded; a table is provided when exact lookup matters.

### Audience and action

- [ ] The intended audience can interpret the chart without guessing.
- [ ] A one-sentence “so what?” takeaway is included.
- [ ] The chart's limitations and next investigative step are clear.
- [ ] The figure supports a decision rather than merely decorating a report.

## 13. Summary

Choose charts by analytical task and data semantics. Bars and dots support comparison; histograms, ECDFs, box plots, and violins reveal different aspects of distributions; scatter and density plots expose relationships; lines show ordered change; stacked charts communicate composition; sorted bars communicate ranking; heatmaps and small multiples manage many measures; and intervals make uncertainty visible. No chart is automatically honest: baselines, bins, denominators, scales, missingness, smoothing, aggregation, and selection rules all influence interpretation.

Treat colour and accessibility as semantic decisions, not finishing touches. Use a finding-oriented title, enough context to reproduce the interpretation, and a clear statement of what the figure can and cannot establish. For operational work, make each chart support a named decision and retain access to the underlying values.

**Lesson completion checklist**

- [ ] I can map a question and data types to a chart and explain a misleading alternative.
- [ ] I can identify and repair truncated bars, rainbow scales, inconsistent bins, and dual-axis illusions.
- [ ] I can address overplotting, missing time intervals, denominators, and uncertainty.
- [ ] I can design five distinct charts for pipeline health with explicit decisions.
- [ ] I completed at least one critique/redraw and created a pipeline/evaluation/cost chart-choice cheat sheet.
- [ ] I reviewed my figures against the pre-publication checklist.
