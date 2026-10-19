# Data Visualization with Matplotlib, Plotly, and Altair

> **Module:** Stage 2C — Data Engineering_3, Module 2C.9: Analytics Foundations for Data Engineers  
> **Lesson:** 08 of 09  
> **Scope:** accurate analytical charts, Python visualisation libraries, scale-aware rendering, uncertainty, accessibility, and reproducible delivery.

## 1. Title and learning objectives

A chart is an analytical interface: it should make a defensible comparison easier, not make weak evidence look persuasive. This lesson follows the roadmap's progression from chart choice and Matplotlib fundamentals to interactive/declarative libraries, large-data visualisation, uncertainty, reusable styles, reports, and code-driven dashboards.

By the end, you should be able to:

- Match a chart to a question and the data grain.
- Build labelled, reproducible figures with Matplotlib, Plotly, and Altair.
- Represent the same estimate and interval consistently in three libraries.
- Choose aggregation, binning, or sampling for large datasets instead of blindly plotting every row.
- Build cohort-retention heatmaps, funnel charts, and pipeline-SLA charts.
- Communicate uncertainty, limitations, and population/time-window definitions.
- Create reusable team styles and a small filtered Streamlit application.
- Test chart data transformations and understand the limits of image-regression testing.

## 2. Why visualisation matters in Data Engineering

Data engineers create tables and pipelines that become charts, reports, alerts, and decisions. A visually polished chart can still be wrong because the source has duplicated joins, late data, inconsistent definitions, or a misleading scale. Visualisation quality therefore depends on both **data correctness** and **visual encoding**.

A reliable chart pipeline is:

1. Define the business question and metric contract.
2. Select the population, grain, time zone, time window, and exclusions.
3. Aggregate at the correct grain and validate totals.
4. Choose an encoding that supports the intended comparison.
5. Label units, filters, population, date range, and uncertainty.
6. Publish a reproducible artifact and monitor its source freshness.

A chart is not a substitute for data-quality checks. Keep metric definitions in a governed semantic/model layer where possible, rather than implementing slightly different formulas inside each chart.

## 3. Prerequisites and environment setup

Prerequisites: Python functions and tests; NumPy and pandas; SQL aggregation; basic probability and confidence intervals; cohort and A/B testing concepts from lessons 03–05.

Use Python 3.12+ and a virtual environment. A `pyproject.toml`/`uv` project is recommended, but plain `pip` works too.

```bash
mkdir visualization-lab && cd visualization-lab
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install numpy pandas matplotlib scipy plotly altair seaborn streamlit pytest
```

For a reproducible environment, pin tested versions in a lockfile (`uv lock`, Poetry, or another dependency manager) and record Python/library versions with the report. Vega-Lite rendering for Altair may require a notebook, browser renderer, or exported HTML; renderer availability depends on the execution environment. Streamlit is optional for the app exercise.

Suggested files:

```text
visualization-lab/
├── viz_style.py
├── viz_transforms.py
├── experiment_comparison.py
├── large_data.py
├── cohort_and_funnel.py
├── app.py
└── tests/
    ├── test_transforms.py
    └── test_chart_images.py  # optional pytest-mpl snapshots
```

## 4. Chart selection and visual perception

Start with the question, not the library.

| Question | Good default | Important caution |
|---|---|---|
| Compare categories | Bar/dot plot | Bars usually need a zero baseline because length encodes magnitude. |
| Show a trend over ordered time | Line chart | Sort timestamps; label timezone and interval; do not connect long gaps without explanation. |
| Show a distribution | Histogram, boxplot, violin | State binning or summary choices; violin shapes can mislead for small samples. |
| Examine a relationship | Scatterplot, hexbin, 2-D histogram | Correlation is not causation; overplotting hides density. |
| Show composition | Stacked bar/area | Compare segments carefully; only the bottom segment shares a baseline. Avoid too many categories. |
| Show a ranking | Sorted horizontal bars or dot plot | State whether rank is based on a complete period and how ties are handled. |
| Show geography | Map only when geography is analytically relevant | Area and projection affect perception; use a suitable projection, disclose the mapped measure and geographic unit, and consider a ranked table if location is incidental. |
| Show a cohort matrix | Heatmap | Fix colour scale and label cohort age; mark immature cells as unavailable, not zero. |
| Show a funnel | Ordered bars or funnel chart | Define whether counts are user-, session-, or event-level and whether order is strict. |
| Show an estimate and uncertainty | Point with interval/error bar; time-series confidence band | Explain what the interval represents; it is not a guarantee. |

### Perceptual principles

- **Position on a common scale** is generally easiest to compare, followed by length; area and colour are less precise for quantitative comparisons.
- Use a zero baseline for bar charts unless there is a clear, explicitly justified reason not to. If a non-zero range is essential for a line chart, make the axis range obvious and avoid suggesting that a small change is enormous.
- Keep the same metric on the same scale when comparing panels. If panels use different scales, label them clearly.
- Use **small multiples** when several related groups need comparison: keep axes aligned when magnitudes are comparable, share scales where possible, and label each panel directly. Annotate known events only when the timing is supported by operational or experimental evidence; an annotation marks context, not causality.
- Reduce chart junk: remove decoration that does not support the comparison, but retain necessary units, context, uncertainty, and data-quality caveats.
- Avoid 3-D effects, decorative gradients, excessive gridlines, and legends that force readers to repeatedly map colour to a series.
- Direct labels can be clearer than legends when there are only a few series.
- Stacked bars work best when the total and a small number of components matter; they are weak for comparing middle segments across many groups.
- A dual-axis chart can imply a relationship through arbitrary scale choices. Prefer aligned small multiples or indexed series with a clear baseline.

## 5. Matplotlib fundamentals

Matplotlib's object model is `Figure` → one or more `Axes` → artists (lines, bars, text, legends). Prefer the explicit object-oriented API for reusable code and multi-panel figures.

```python
import numpy as np
import matplotlib.pyplot as plt

weeks = np.arange(1, 9)
orders = np.array([120, 128, 125, 141, 149, 145, 158, 164])
fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
ax.plot(weeks, orders, marker="o", label="Orders")
ax.set(title="Weekly orders", xlabel="Week", ylabel="Orders (count)")
ax.legend()
ax.grid(axis="y", alpha=0.25)
fig.savefig("weekly-orders.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

Common methods:

```python
ax.bar(categories, values)          # category comparison; zero baseline
ax.hist(values, bins=30, edgecolor="white")
ax.scatter(x, y, alpha=0.25, s=8)
ax.plot(dates, metric)
```

Use `fig, ax = plt.subplots(...)`; avoid depending on implicit global pyplot state in production modules. Specify figure size, labels, units, title, and output format. Close figures in batch/report jobs to avoid accumulating memory. Choose `dpi` and dimensions for the target medium rather than assuming a single export fits notebook, slide, and web contexts.

## 6. Plotly and interactive visualisation

Plotly's graph objects expose chart components explicitly; Plotly Express (`plotly.express`, imported as `px`) provides concise high-level charts. Hover, zoom, selection, and HTML export are useful when users need to inspect points or time ranges.

```python
import pandas as pd
import plotly.express as px

weekly = pd.DataFrame({"week": pd.date_range("2026-01-05", periods=8, freq="W-MON"),
                       "orders": [120, 128, 125, 141, 149, 145, 158, 164]})
fig = px.line(weekly, x="week", y="orders", markers=True,
              title="Weekly orders", labels={"week": "Week starting", "orders": "Orders (count)"})
fig.write_html("weekly-orders.html", include_plotlyjs="cdn")
```

Strengths: interactive exploration, hover detail, browser-friendly HTML, and integration with Dash. Limitations: interactivity can distract from the question; a browser still has finite rendering capacity; large point sets may require aggregation, WebGL where appropriate, or a server-side strategy. A plotly chart is not automatically a governed dashboard—authentication, authorization, deployment, and data access remain application/platform concerns. Dash is a framework for building web apps around Plotly components, not a replacement for data modelling.

## 7. Altair and declarative visualisation

Altair expresses a chart as data plus encodings and marks. It compiles to Vega-Lite specifications, which makes the mapping between fields and visual channels explicit. This is useful for concise, reviewable charts and interactive filters.

```python
import altair as alt
import pandas as pd

weekly = pd.DataFrame({"week": pd.date_range("2026-01-05", periods=8, freq="W-MON"),
                       "orders": [120, 128, 125, 141, 149, 145, 158, 164]})
chart = alt.Chart(weekly).mark_line(point=True).encode(
    x=alt.X("week:T", title="Week starting"),
    y=alt.Y("orders:Q", title="Orders (count)"),
    tooltip=["week:T", "orders:Q"],
).properties(title="Weekly orders", width=650, height=300)
chart.save("weekly-orders.html")
```

Strengths: declarative grammar, concise encodings, and convenient interaction. Limitations: default data-transform limits and browser rendering are version/configuration-dependent; do not assume it is suitable for sending millions of raw records to the browser. Aggregate upstream or use an appropriate data transformer/serving architecture. Altair is particularly good for analytical reports; it is not a warehouse or metric-governance layer.

### Matplotlib vs Plotly vs Altair

| Criterion | Matplotlib | Plotly | Altair |
|---|---|---|---|
| Programming model | Imperative, artist-oriented | High-level Express and lower-level graph objects | Declarative data + mark + encoding specification |
| Default output | Static figures | Interactive browser charts; static export also possible with appropriate dependencies | Browser/Vega-Lite charts; static export depends on renderer setup |
| Strong use cases | Publication-quality static figures, custom layouts, batch reports | Exploratory dashboards, hover/zoom, interactive reports | Concise statistical charts, explicit mappings, report-friendly interactions |
| Main trade-off | More code for some interactions; styling flexibility can be complex | Interactive output adds browser and deployment considerations | Less suited to highly bespoke low-level drawing; renderer and data limits matter |
| Large data | Aggregate, sample, rasterize or use specialized rendering | Aggregate, sample, WebGL/server-side strategies as appropriate | Aggregate or transform before browser delivery; heed row/renderer limits |
| Reproducibility | Save code, inputs, versions, and image | Save code/specification, data snapshot, and HTML/runtime dependencies | Save code/specification, data snapshot, and renderer/dependency versions |

**Decision rule:** choose Matplotlib for static, highly controlled output; Plotly for exploratory browser interaction; Altair when declarative field-to-visual mappings and concise report charts are valuable. Interactivity is not automatically better analytical quality. The same metric, population, time range, and uncertainty method must remain consistent across libraries.

## 8. Seaborn and statistical plots

Seaborn builds on Matplotlib and is useful for distributions, grouped comparisons, regression diagnostics, and heatmaps.

```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

sample = pd.DataFrame({"channel": ["organic"] * 4 + ["paid"] * 4,
                       "revenue": [8, 10, 9, 14, 7, 8, 12, 13]})
fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
sns.boxplot(data=sample, x="channel", y="revenue", ax=ax)
ax.set(title="Revenue distribution by channel", xlabel="Acquisition channel", ylabel="Revenue (currency units)")
```

Seaborn's statistical defaults can make complex charts concise, but inspect the estimator, uncertainty procedure, sample size, and missing-data behavior. A regression line describes an association under a model; it does not establish causal impact. Heatmaps should have labelled rows/columns, meaningful missing-value handling, and a colour scale that does not exaggerate small differences.

## 9. Visualising large datasets

Rendering 10 million points as individual marks is often slow, memory-intensive, and visually misleading because marks overlap. The appropriate representation depends on the question:

- **Aggregate** when the question concerns totals or rates by time/category.
- **Bin** when the question concerns density in two dimensions (`hist2d`, `hexbin`).
- **Sample** when exploring the shape or debugging individual records; state the sampling method and that rare events may be missed.
- **Rasterize/render on the server** for very dense point clouds; Datashader is a purpose-built option to investigate.
- **Query a serving/OLAP engine** to return summaries instead of extracting all raw rows into a notebook.

Do not use a sample to report exact totals. For a uniform random sample without replacement, estimates and uncertainty depend on the sampling design. For stratified or clustered data, use a design-aware estimator rather than pretending observations are independent and identically distributed.

The following chunked example generates ten million synthetic observations without holding all x/y values in memory at once. It accumulates a 2-D histogram. It is an execution recipe, not a claim that a ten-million-row benchmark has been run in this environment.

```python
# large_data.py
import numpy as np
import matplotlib.pyplot as plt

SEED = 20261019
N = 10_000_000
CHUNK = 500_000
BINS = 250
rng = np.random.default_rng(SEED)
counts = np.zeros((BINS, BINS), dtype=np.int64)
# The plotted domain is fixed in advance; out-of-domain values are excluded from bins.
lo, hi = -5.0, 5.0
processed = 0
for start in range(0, N, CHUNK):
    n = min(CHUNK, N - start)
    x = rng.normal(size=n)
    y = 0.65 * x + rng.normal(scale=0.8, size=n)
    chunk_counts, _, _ = np.histogram2d(x, y, bins=BINS, range=[[lo, hi], [lo, hi]])
    counts += chunk_counts.astype(np.int64)
    processed += n

fig, ax = plt.subplots(figsize=(7, 6), layout="constrained")
mesh = ax.imshow(counts.T, origin="lower", extent=[lo, hi, lo, hi],
                 aspect="auto", interpolation="nearest")
fig.colorbar(mesh, ax=ax, label="Observations per bin")
ax.set(title=f"Binned relationship ({processed:,} generated observations)",
       xlabel="x", ylabel="y")
fig.savefig("ten-million-binned.png", dpi=160)
plt.close(fig)
print({"generated": processed, "counted_in_domain": int(counts.sum()), "bins": BINS * BINS})
```

The code's `counts.sum()` can be less than `N` because observations outside the fixed domain are intentionally excluded. To preserve all observations, add underflow/overflow bins or report out-of-domain counts separately. The 2-D histogram preserves density at bin resolution, not individual points. `hexbin` is a simpler single-machine option when the arrays fit memory; chunked histograms are more memory-predictable.

A naïve alternative such as `ax.scatter(x, y, s=1)` after generating both full arrays can allocate substantial memory and render millions of overlapping marks. Do not make the ten-million-point scatter the default lab: memory, rasterisation, and rendering time depend on the environment. The safe comparison below uses the same synthetic distribution at 200,000 points to demonstrate the visual failure mode, while the preceding chunked histogram handles all ten million observations. If you benchmark a ten-million-point scatter, run it separately in a disposable process, record peak memory and wall time, and do not treat that benchmark as portable.

For a visual side-by-side demonstration, use the same synthetic distribution at a manageable scale. The scatter shows individual marks but density is hard to compare in crowded areas; the hexbin summarizes density. This is a teaching illustration, not a performance benchmark.

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(20261019)
n = 200_000
x = rng.normal(size=n)
y = 0.65 * x + rng.normal(scale=0.8, size=n)
fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
axes[0].scatter(x, y, s=1, alpha=0.08, rasterized=True)
axes[0].set(title="Raw points (200,000)", xlabel="x", ylabel="y")
hexes = axes[1].hexbin(x, y, gridsize=55, mincnt=1, bins="log")
fig.colorbar(hexes, ax=axes[1], label="Count per hexagon (log scale)")
axes[1].set(title="Hexbin density", xlabel="x", ylabel="y")
fig.savefig("scatter-vs-hexbin.png", dpi=160)
plt.close(fig)
```

## 10. Uncertainty, colour, accessibility, and ethics

### Uncertainty intervals

- A **confidence interval** is produced by a procedure with a long-run coverage property under its assumptions. It is not the probability that a fixed parameter lies in this particular interval.
- A **prediction interval** concerns a future observation and is generally wider than an interval for the mean.
- A **confidence band** extends uncertainty over a curve; simultaneous and pointwise bands are not the same.
- A **fan chart** can show multiple forecast quantiles over time. State the quantiles and model/forecast vintage.
- Error bars may show standard deviation, standard error, confidence interval, or a range. Label which one.

Use intervals derived from a suitable statistical method. For independent continuous outcomes, a difference in means may use Welch's standard error when unequal variances are plausible. This lab instead uses an unpooled Wald interval for a difference in proportions, which is pedagogically useful at moderate counts but can perform poorly for small samples or rare outcomes and can extend beyond the possible difference range of −1 to 1. Do not silently clip such bounds; use a Wilson/Newcombe or suitable score-based interval for production reporting.

### Colour and accessibility

- Sequential palettes represent ordered magnitude; diverging palettes represent deviation around a meaningful midpoint; categorical palettes distinguish unordered groups.
- Use colour-blind-safe palettes (for example, a tested palette such as `colorblind` in Seaborn) and adequate contrast.
- Do not encode critical status by colour alone. Add text, symbols, patterns, or direct labels.
- Use a consistent mapping for a metric/category across charts.
- For heatmaps, explain whether high values are good or bad and set the midpoint/range intentionally.
- Include alt text or a textual summary when publishing figures; ensure keyboard and screen-reader accessibility in applications.

### Ethics

Avoid truncating bar axes, selectively choosing date ranges, hiding excluded populations, cherry-picking a season, and using dual axes to imply correlation. Disclose uncertainty, sample size, exclusions, data freshness, and material limitations. A chart is misleading if its visual implication exceeds what the data support, even if every plotted number is technically correct.

## 11. Data Engineering-specific visualisations

Common patterns include:

- **Cohort retention heatmap:** rows are signup cohorts; columns are cohort age (day/week); cells are retained users divided by eligible cohort users. Mark immature cohort ages as `NaN`/blank, not zero. Keep denominator definition stable.
- **Funnel chart:** ordered stages and counts/rates. Define strict vs loose ordering, conversion window, and user/session grain. Use a table or bars when a tapered shape would overstate the meaning.
- **Retention curve:** retention by cohort age with sample sizes or uncertainty where feasible. Avoid comparing immature cohorts with mature ones.
- **Time series with intervals:** actual metric and interval bands; annotate deployments, holidays, and known incidents without implying causation automatically.
- **Pipeline SLA chart:** freshness lag, duration, row counts, and SLA threshold; distinguish late/failed data from actual business metric movement.
- **Data-quality chart:** null rate, duplicate rate, schema drift, and reconciliation differences over time.

Always add a data timestamp or freshness status to operational charts. A pipeline-row-count anomaly and a business-demand anomaly are different incidents and need different alert routes.

## 12. Reusable plotting components and report generation

### Team style module

Create `viz_style.py`:

```python
# viz_style.py
import matplotlib as mpl
import seaborn as sns

PALETTE = {
    "control": "#0072B2",   # blue
    "treatment": "#D55E00", # vermillion
    "neutral": "#555555",
    "positive": "#009E73",
    "warning": "#E69F00",
}
FIGSIZE_WIDE = (9, 4.8)
DPI = 160


def apply_matplotlib_style() -> None:
    mpl.rcParams.update({
        "figure.figsize": FIGSIZE_WIDE,
        "figure.dpi": DPI,
        "font.family": "DejaVu Sans",
        "axes.titlesize": 13,
        "axes.labelsize": 10,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })
    sns.set_palette("colorblind")
```

The named colour constants are examples, not a substitute for checking contrast in the actual context. Use the same semantic names across libraries; translate them into each library's supported configuration. Avoid mutating global styles unexpectedly in reusable library code—consider a context manager or explicit `ax`/theme parameters for production packages.

### Shared, testable data transformations

Keep small data transformations in an importable module so tests exercise the same functions used by charts, rather than re-implementing the logic inside the test file. Save the following as `viz_transforms.py`. The interval helper returns rates and bounds in **proportion units**; multiply by 100 only when displaying percentage points. The normal-approximation interval is intentionally limited to teaching use and should be replaced with a score-based interval for small counts or rare outcomes.

```python
# viz_transforms.py
import numpy as np
import pandas as pd


def difference_in_proportions_wald_interval(
    control_successes: int,
    control_n: int,
    treatment_successes: int,
    treatment_n: int,
    *,
    z: float = 1.96,
) -> tuple[float, float, float, float, float]:
    """Return (p_control, p_treatment, delta, lower, upper), in proportions."""
    counts = (control_successes, control_n, treatment_successes, treatment_n)
    if any(isinstance(v, (bool, np.bool_)) or not isinstance(v, (int, np.integer)) for v in counts):
        raise ValueError("Success and sample counts must be integers")
    if control_n <= 0 or treatment_n <= 0:
        raise ValueError("Sample sizes must be positive")
    if not 0 <= control_successes <= control_n or not 0 <= treatment_successes <= treatment_n:
        raise ValueError("Success counts must lie between zero and the corresponding sample size")
    if not np.isfinite(z) or z <= 0:
        raise ValueError("z must be finite and positive")
    p_c = control_successes / control_n
    p_t = treatment_successes / treatment_n
    delta = p_t - p_c
    se = float(np.sqrt(p_t * (1 - p_t) / treatment_n + p_c * (1 - p_c) / control_n))
    return p_c, p_t, delta, delta - z * se, delta + z * se


def retention_rates(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate cohort-age grain and compute retention against original cohort size."""
    required = {"retained_users", "cohort_users", "matured"}
    if frame.empty:
        raise ValueError("Retention input must contain at least one cohort-age row")
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if {"cohort", "age_week"}.issubset(frame.columns) and frame.duplicated(["cohort", "age_week"]).any():
        raise ValueError("Expected one row per cohort and cohort age")
    if frame[["retained_users", "cohort_users", "matured"]].isna().any().any():
        raise ValueError("Retention inputs must not be null")
    if not pd.api.types.is_bool_dtype(frame["matured"]):
        raise ValueError("matured must have boolean dtype")
    out = frame.copy()
    for column in ("retained_users", "cohort_users"):
        numeric = pd.to_numeric(out[column], errors="coerce")
        values = numeric.to_numpy(dtype=float)
        if not np.isfinite(values).all() or not np.equal(values, np.floor(values)).all():
            raise ValueError(f"{column} must contain finite integer counts")
        out[column] = numeric.astype("int64")
    if (out["cohort_users"] <= 0).any():
        raise ValueError("cohort_users must be positive")
    if ((out["retained_users"] < 0) | (out["retained_users"] > out["cohort_users"])).any():
        raise ValueError("retained_users must be between zero and cohort_users")
    out["retention_rate"] = out["retained_users"] / out["cohort_users"]
    out.loc[~out["matured"].astype(bool), "retention_rate"] = np.nan
    return out


def validate_funnel_counts(counts, *, nested_user_stages: bool = True) -> np.ndarray:
    """Validate distinct-user counts; require monotonicity only for nested stages."""
    try:
        values = np.asarray(counts, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("Funnel counts must be numeric") from exc
    if values.ndim != 1 or values.size == 0:
        raise ValueError("Funnel counts must be a non-empty one-dimensional sequence")
    if not np.isfinite(values).all() or (values < 0).any() or not np.equal(values, np.floor(values)).all():
        raise ValueError("Funnel counts must be finite non-negative integers")
    if nested_user_stages and (np.diff(values) > 0).any():
        raise ValueError("Nested user-level funnel counts must be non-increasing")
    return values.astype(np.int64)
```

### Reports and apps

- **Jupyter:** best for exploratory work and teaching; make notebooks restart-and-run-all reproducible, pin dependencies, and keep outputs from becoming stale evidence.
- **Quarto:** renders notebooks/scripts/Markdown to reproducible HTML/PDF/other report formats; execution and deployment configuration must be controlled.
- **Evidence:** code-first BI/reporting approach that compiles queries and visual components into a report/application; verify the current project structure and supported connectors for the version used.
- **Streamlit:** rapid Python data apps with widgets and reruns; suitable for internal analytical tools, but authentication, authorization, caching, and deployment still need design.
- **Dash:** component-based interactive web applications, commonly with Plotly.
- **Panel:** Python app framework that supports multiple plotting ecosystems and dashboard patterns.

These are not interchangeable with governed BI tools. A code app offers flexibility, while BI platforms may offer stronger managed sharing, semantic modelling, auditability, and business-user self-service. Evaluate the security and operations around the framework, not only chart authoring.

### Image-regression testing

Image comparison can catch layout shifts, clipped labels, missing legends, and accidental style changes, but snapshots are brittle across fonts, OSs, renderers, and library versions. Use fixed seeds and pinned renderers; compare with a tolerance; keep semantic/data tests as the primary correctness gate. A chart can pass a pixel comparison while plotting the wrong metric, so test transformations and chart specifications too. For Matplotlib projects, `pytest-mpl` provides an image-comparison marker and baseline workflow; pin fonts and Matplotlib versions in CI and review baseline changes rather than blindly accepting them.

```bash
python -m pip install pytest-mpl
pytest --mpl-generate-path=baseline tests/test_chart_images.py
pytest --mpl tests/test_chart_images.py
```

```python
# tests/test_chart_images.py — requires pytest-mpl and a reviewed baseline image
import matplotlib.pyplot as plt
import pytest

@pytest.mark.mpl_image_compare(baseline_dir="baseline", tolerance=5)
def test_weekly_orders_chart():
    weeks = [1, 2, 3, 4]
    orders = [10, 12, 11, 15]
    fig, ax = plt.subplots(figsize=(6, 3), layout="constrained")
    ax.plot(weeks, orders, marker="o")
    ax.set(title="Weekly orders", xlabel="Week", ylabel="Orders (count)")
    return fig
```

## 13. Hands-on lab

The lab uses one experiment result across three libraries, a synthetic 10-million-observation binned plot, a retention heatmap, a funnel, and a Streamlit filter app. It uses deterministic seeds and states assumptions. Run each code block in the same Python environment described in Section 3.

### 13.1 Same experiment result and interval in three libraries

We generate two independent Bernoulli groups, calculate conversion proportions, and estimate treatment-minus-control difference. The interval is the unpooled normal-approximation 95% interval:

\[
\hat\Delta = \hat p_T - \hat p_C, \qquad
SE(\hat\Delta)=\sqrt{\frac{\hat p_T(1-\hat p_T)}{n_T}+\frac{\hat p_C(1-\hat p_C)}{n_C}},
\quad CI=\hat\Delta\pm1.96SE.
\]

This is an approximate interval; use a score-based method for small counts or rare events. The calculation is in proportion units, and the three plots convert the estimate and both endpoints to percentage points before plotting. We report the observed estimate from the seeded sample, not the data-generating effect as if it were the realised result.

```python
# experiment_comparison.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import altair as alt
from viz_style import PALETTE
from viz_transforms import difference_in_proportions_wald_interval

SEED = 20261019
N_PER_ARM = 20_000
P_CONTROL = 0.10
P_TREATMENT = 0.11  # planted +1 percentage point; +10% relative to 10% baseline
rng = np.random.default_rng(SEED)
control = rng.binomial(1, P_CONTROL, size=N_PER_ARM)
treatment = rng.binomial(1, P_TREATMENT, size=N_PER_ARM)

p_c, p_t, delta, lo, hi = difference_in_proportions_wald_interval(
    int(control.sum()), len(control), int(treatment.sum()), len(treatment)
)
# The helper returns proportions; charts labelled in percentage points must scale all values by 100.
delta_pp, lo_pp, hi_pp = 100 * delta, 100 * lo, 100 * hi
result = pd.DataFrame({"group": ["Treatment"], "estimate_pp": [delta_pp],
                       "lower_pp": [lo_pp], "upper_pp": [hi_pp]})
print({"n_control": len(control), "n_treatment": len(treatment),
       "control_rate": p_c, "treatment_rate": p_t,
       "difference_pp": delta_pp, "ci95_pp": (lo_pp, hi_pp)})
assert len(control) == N_PER_ARM and len(treatment) == N_PER_ARM
assert 0 <= p_c <= 1 and 0 <= p_t <= 1
assert lo <= delta <= hi and lo <= hi
# Every chart below consumes the same estimate and interval, displayed in percentage points.
assert result.loc[0, "estimate_pp"] == delta_pp
assert result.loc[0, "lower_pp"] == lo_pp and result.loc[0, "upper_pp"] == hi_pp

# Matplotlib: explicit axes and error bars
fig, ax = plt.subplots(figsize=(7, 2.8), layout="constrained")
ax.errorbar([delta_pp], [0], xerr=[[delta_pp - lo_pp], [hi_pp - delta_pp]], fmt="o", capsize=5,
            color=PALETTE["treatment"])
ax.axvline(0, color=PALETTE["neutral"], linestyle="--", linewidth=1)
ax.set(yticks=[0], yticklabels=["Treatment − control"],
       xlabel="Absolute conversion-rate difference (percentage points)",
       title="Experiment estimate with approximate 95% confidence interval")
ax.set_xlim(min(lo_pp, 0) - 0.1, max(hi_pp, 0) + 0.1)
fig.savefig("experiment-matplotlib.png", dpi=160, bbox_inches="tight")
plt.close(fig)

# Plotly: same delta/interval values
fig = go.Figure()
fig.add_trace(go.Scatter(x=[delta_pp], y=["Treatment − control"], mode="markers",
                         marker={"color": PALETTE["treatment"], "size": 10},
                         error_x={"type": "data", "symmetric": False,
                                  "array": [hi_pp - delta_pp], "arrayminus": [delta_pp - lo_pp]},
                         name="Estimate"))
fig.add_vline(x=0, line_dash="dash", line_color=PALETTE["neutral"])
fig.update_layout(title="Experiment estimate with approximate 95% confidence interval",
                  xaxis_title="Absolute conversion-rate difference (percentage points)",
                  yaxis_title="", template="plotly_white")
fig.write_html("experiment-plotly.html", include_plotlyjs="cdn")

# Altair: explicit interval endpoints and estimate, same values
alt_data = pd.DataFrame({"label": ["Treatment − control"], "estimate": [delta_pp], "lower": [lo_pp], "upper": [hi_pp]})
base = alt.Chart(alt_data).encode(y=alt.Y("label:N", title=""))
interval = base.mark_rule(color=PALETTE["treatment"], strokeWidth=2).encode(
    x=alt.X("lower:Q", title="Absolute conversion-rate difference (percentage points)"),
    x2="upper:Q")
point = base.mark_point(color=PALETTE["treatment"], filled=True, size=90).encode(x="estimate:Q")
zero = alt.Chart(pd.DataFrame({"zero": [0]})).mark_rule(strokeDash=[5, 4], color=PALETTE["neutral"]).encode(x="zero:Q")
chart = (interval + point + zero).properties(
    title="Experiment estimate with approximate 95% confidence interval", width=650, height=100)
chart.save("experiment-altair.html")
```

**Expected behaviour:** three charts show the same observed difference, the same lower/upper interval, and a vertical zero-reference line. The seeded sample's estimate will generally differ from the planted `0.01` absolute difference. Do not hard-code or invent a measured estimate in the lesson. If the interval crosses zero, the result is inconclusive under this approximate two-sided 5% procedure; if it does not, that still does not establish practical importance or eliminate design/data-quality concerns.

**Comparison:** Matplotlib is compact and highly controllable for static reports; Plotly adds hover/zoom and an HTML artifact; Altair expresses endpoints and point through declarative encodings. The analytical result should not change because the chart library changed.

### 13.2 Cohort retention heatmap

The input should be a validated table with one row per cohort and cohort age, `retained_users`, `cohort_users`, and `matured` flag. The denominator is the original eligible cohort size, not the users still present at the prior age.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from viz_transforms import retention_rates

retention = pd.DataFrame([
    ("2026-W01", 0, 100, 100, True), ("2026-W01", 1, 42, 100, True),
    ("2026-W01", 2, 35, 100, True), ("2026-W01", 3, 30, 100, True),
    ("2026-W02", 0, 120, 120, True), ("2026-W02", 1, 50, 120, True),
    ("2026-W02", 2, 38, 120, True), ("2026-W02", 3, 0, 120, False),
], columns=["cohort", "age_week", "retained_users", "cohort_users", "matured"])
retention = retention_rates(retention)
matrix = retention.pivot(index="cohort", columns="age_week", values="retention_rate")
fig, ax = plt.subplots(figsize=(7, 3), layout="constrained")
sns.heatmap(matrix, annot=True, fmt=".0%", vmin=0, vmax=1, cmap="viridis", ax=ax,
            cbar_kws={"label": "Retained / original cohort users"})
ax.set(title="Weekly cohort retention", xlabel="Weeks since cohort start", ylabel="Signup cohort")
fig.savefig("retention-heatmap.png", dpi=160)
plt.close(fig)
```

The final W02 cell is intentionally unavailable because it is immature; it must render blank, not as 0%. In production, ensure the retention definition (any activity, qualifying event, or rolling active state) and cohort time zone are fixed in the metric contract.

### 13.3 Funnel chart

Example is user-level and uses counts from the same eligible population. The figures below are illustrative data, not measured business results.

```python
import pandas as pd
import matplotlib.pyplot as plt
from viz_transforms import validate_funnel_counts

funnel = pd.DataFrame({"stage": ["Visit", "Signup", "Add to cart", "Purchase"],
                       "users": [10000, 2600, 1400, 700]})
funnel["users"] = validate_funnel_counts(funnel["users"], nested_user_stages=True)
funnel["conversion_from_visit"] = funnel["users"] / funnel["users"].iloc[0]
funnel["step_conversion"] = funnel["users"] / funnel["users"].shift(1)
fig, ax = plt.subplots(figsize=(7, 4), layout="constrained")
ax.barh(funnel["stage"].iloc[::-1], funnel["users"].iloc[::-1], color="#0072B2")
ax.set(title="Example seven-day user funnel", xlabel="Distinct eligible users", ylabel="Funnel step")
for i, value in enumerate(funnel["users"].iloc[::-1]):
    ax.text(value, i, f"  {value:,}", va="center")
fig.savefig("funnel.png", dpi=160)
plt.close(fig)
```

A real funnel must be computed from event timestamps and a stated conversion window. The illustration assumes stage counts already satisfy the intended order/window and should not be used to infer conversion from raw independent event counts.

### 13.4 Streamlit metrics app with filters

Create `app.py`. The sample dataset is intentionally tiny; replace it with a validated aggregate query for production. Do not load a full event table into a user-facing app.

```python
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Analytics overview", layout="wide")
st.title("Analytics overview")
# Illustrative, pre-aggregated daily metrics; replace with a governed gold-layer query.
data = pd.DataFrame({
    "date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-01", "2026-01-02", "2026-01-03"]),
    "region": ["North", "North", "North", "South", "South", "South"],
    "revenue": [1200, 1350, 1280, 900, 950, 1020],
    "orders": [40, 45, 43, 30, 31, 34],
})
regions = st.multiselect("Region", sorted(data["region"].unique()), default=sorted(data["region"].unique()))
selected_range = st.date_input(
    "Date range", value=(data["date"].min().date(), data["date"].max().date())
)
# Streamlit may return a date, a one-item range, a two-item range, or an empty range
# while a user is editing the control; normalize these cases before filtering.
if isinstance(selected_range, (tuple, list)):
    if len(selected_range) == 2:
        start, end = selected_range
    elif len(selected_range) == 1:
        start = end = selected_range[0]
    else:
        st.info("Select at least one date.")
        st.stop()
else:
    start = end = selected_range
if start > end:
    st.warning("The start date must not be after the end date.")
    st.stop()
filtered = data[data["region"].isin(regions) & data["date"].dt.date.between(start, end)]
if filtered.empty:
    st.warning("No data for the selected filters.")
else:
    revenue = filtered["revenue"].sum()
    orders = filtered["orders"].sum()
    st.metric("Revenue", f"{revenue:,.0f}")
    st.metric("Orders", f"{orders:,}")
    daily = filtered.groupby("date", as_index=False)[["revenue", "orders"]].sum()
    st.plotly_chart(px.line(daily, x="date", y="revenue", markers=True, title="Daily revenue"), use_container_width=True)
```

Run with `streamlit run app.py`. This demo does not implement authentication or row-level security. In production, apply authorization at the trusted data/API boundary; hiding a region in a UI filter is not security. Validate the selected date range and handle a single-date selection according to the installed Streamlit version's `date_input` return contract.

### 13.5 Transformation tests and validation

Run these checks in a test file after extracting the metric transformations into functions in a real project. They test the data semantics rather than relying on a pixel snapshot.

```python
# tests/test_transforms.py
import numpy as np
import pandas as pd
import pytest

from viz_transforms import (
    difference_in_proportions_wald_interval,
    retention_rates,
    validate_funnel_counts,
)


def test_retention_denominator_and_maturity():
    frame = pd.DataFrame({
        "cohort": ["W01", "W01"], "age_week": [0, 1],
        "retained_users": [50, 0], "cohort_users": [100, 100],
        "matured": [True, False],
    })
    out = retention_rates(frame)
    assert out.loc[0, "retention_rate"] == 0.5
    assert np.isnan(out.loc[1, "retention_rate"])  # immature is unavailable, not zero


def test_retention_rejects_duplicate_cohort_age_and_invalid_denominator():
    duplicate = pd.DataFrame({
        "cohort": ["W01", "W01"], "age_week": [1, 1],
        "retained_users": [5, 4], "cohort_users": [10, 10], "matured": [True, True],
    })
    with pytest.raises(ValueError, match="one row per cohort"):
        retention_rates(duplicate)
    invalid = duplicate.iloc[:1].copy()
    invalid["cohort_users"] = 0
    with pytest.raises(ValueError, match="positive"):
        retention_rates(invalid)


def test_funnel_validation_enforces_nested_user_counts():
    counts = validate_funnel_counts(pd.Series([1000, 300, 150, 70]))
    assert counts.tolist() == [1000, 300, 150, 70]
    with pytest.raises(ValueError, match="non-increasing"):
        validate_funnel_counts([100, 110, 50])
    # Independently defined/event-count stages need not be nested.
    assert validate_funnel_counts([100, 110, 50], nested_user_stages=False).tolist() == [100, 110, 50]


def test_proportion_interval_is_ordered_and_uses_valid_counts():
    p_c, p_t, delta, lower, upper = difference_in_proportions_wald_interval(100, 1000, 110, 1000)
    assert p_c == 0.1 and p_t == 0.11 and np.isclose(delta, 0.01)
    assert lower <= delta <= upper and lower < upper
    with pytest.raises(ValueError, match="positive"):
        difference_in_proportions_wald_interval(0, 0, 1, 10)
    with pytest.raises(ValueError, match="between zero"):
        difference_in_proportions_wald_interval(11, 10, 1, 10)
```

Run `python -m pytest -q` from the project root. These tests exercise the same functions used by the charts, including cohort-age uniqueness, denominator validity, nested funnel semantics, and proportion-interval inputs. They complement, rather than replace, chart-specification and optional image-regression tests. The funnel monotonicity rule applies only when each later stage is a subset of the same eligible user population within the same conversion window; it is not a universal invariant for event counts or independently defined stages.

Run with `pytest -q`. The funnel monotonicity test is appropriate only when each later stage is a subset of the prior stage under the same user population and conversion window; it is not a universal invariant for event counts or independently defined stages.

### 13.6 Five misleading charts and corrections

1. **Bar chart y-axis starts at 95.** A value of 100 looks dramatically smaller than 105. **Fix:** start at zero for magnitude comparison or use a clearly labelled dot plot with a disclosed range.
2. **Dual axes show revenue and conversion with matching peaks.** Arbitrary scaling can manufacture visual alignment. **Fix:** use aligned small multiples or indexed series, and do not imply causal connection.
3. **Retention heatmap renders immature cells as 0%.** This conflates “not yet observed” with “observed and none retained.” **Fix:** encode immature cells as missing, annotate maturity, and use a fixed colour scale.
4. **Scatterplot of millions of opaque points.** Overplotting hides density and outliers. **Fix:** use hexbin/2-D histogram, density rendering, or a documented sample for point-level investigation.
5. **Only the best two weeks are shown after a product change.** Selective date windows can exaggerate impact and hide seasonality. **Fix:** predefine the comparison window, show adequate context, annotate known interventions, and include uncertainty and relevant guardrails.

## 14. Exercises with solutions

### Exercise 1 — Pick the chart

For each question, choose a default chart and state one caveat:

- Weekly orders over a year.
- Revenue by region.
- Distribution of order value by channel.
- Relationship between basket size and order value.
- Retention by signup cohort and age.

**Solution:** line chart (timezone, missing weeks, seasonal context); sorted bars/dot plot (zero baseline, currency units); box/violin plus sample sizes (distribution and outliers); scatter/hexbin (overplotting, association not causation); cohort heatmap (fixed denominator and maturity masking).

### Exercise 2 — Check the interval

In the experiment lab, verify `lo <= delta <= hi`, `lo <= hi`, and that the same variables are passed to all three chart specifications. Also verify that the values plotted on an axis labelled “percentage points” are multiplied by 100 from the proportion-scale calculation. Explain why a seeded observed difference need not equal the planted difference.

**Solution:** the sample is random even with a fixed seed; a seed makes the result reproducible, not equal to the population parameter. Tests should assert interval ordering and shared data values, not a hard-coded significance result.

### Exercise 3 — Scale-aware visualisation

Why is a 250×250 histogram a defensible summary of ten million observations, and what does it lose?

**Solution:** it summarizes local density using 62,500 bins and avoids drawing ten million marks. It loses within-bin detail, and counts outside the chosen range are excluded unless separately counted. Choose bin count/range based on the question and test sensitivity.

### Exercise 4 — Design a pipeline-SLA chart

Show freshness lag and job duration against SLA thresholds. What should an incident responder see?

**Solution:** a time series with units, threshold line, freshness timestamp, job status, and deployment/incident annotations. Alert on pipeline telemetry separately from business metric anomalies; annotate whether missing points mean no events, late data, or failed jobs.

### Exercise 5 — Explain a chart ethically

A conversion chart has a 2-point increase but a wide interval crossing zero and a changed event definition halfway through the period. Can the team claim improvement?

**Solution:** no defensible causal or directional claim follows without resolving the instrumentation/definition break. Recompute a consistent metric or mark the series discontinuity; show uncertainty and avoid interpreting a point estimate in isolation.

## 15. Common mistakes and production failure modes

- **Wrong grain:** joining event-level rows to user-level outcomes multiplies records. Aggregate to the intended grain before joining and assert key uniqueness.
- **Unclear population:** title says “conversion” but denominator/exclusions are missing. Include the metric contract or link to it.
- **Inconsistent time zones:** daily charts shift around midnight or DST. Define a business timezone and use timezone-aware timestamps before bucketing.
- **Missing values treated as zero:** distinguish unavailable, not applicable, and true zero.
- **Overplotting:** aggregation/bins or sampling may be needed; explain what the summary preserves.
- **Misleading scale:** truncated bars, inconsistent panel axes, arbitrary dual axes, or colour ranges chosen after seeing the result.
- **False precision:** excessive decimals obscure uncertainty and data quality.
- **Bad intervals:** error bars are unlabeled, or standard deviation is presented as a confidence interval.
- **Causal overclaim:** a trend or regression does not by itself prove an intervention caused the change.
- **Stale artifacts:** notebook outputs or cached reports no longer match the code/input snapshot.
- **Visual test overreliance:** pixel tests pass while the query returns the wrong rows; test semantics separately.
- **App security gap:** a filter is mistaken for access control; enforce authorization at trusted boundaries and test with distinct identities.

## 16. Knowledge checkpoint

Before moving on, you should be able to answer:

- [ ] Which chart best answers a category comparison, time trend, distribution, relationship, and cohort question?
- [ ] Why do bars normally require a zero baseline?
- [ ] What are the programming models and trade-offs of Matplotlib, Plotly, and Altair?
- [ ] Why is plotting ten million raw points often a bad design?
- [ ] What is the difference between a confidence interval and a prediction interval?
- [ ] How do sequential, diverging, and categorical palettes differ?
- [ ] How do you represent immature cohort cells and missing timestamps honestly?
- [ ] Why is a UI filter not a security boundary?
- [ ] Which transformations and semantics should be tested beyond image snapshots?

## 17. Final competency checklist

- [ ] I choose charts from analytical questions rather than visual novelty.
- [ ] Every figure has a title, labelled axes, units, population/time scope, and meaningful legend/annotation.
- [ ] I can implement the same result in Matplotlib, Plotly, and Altair without changing the underlying numbers.
- [ ] I understand uncertainty and can explain the procedure behind an interval.
- [ ] I use aggregation, binning, or documented sampling for large datasets.
- [ ] I can build a cohort heatmap, funnel, and pipeline-SLA chart with correct grain and missingness.
- [ ] I apply accessible colour choices and do not encode meaning by colour alone.
- [ ] I can create a reusable style module and reproducible report/app.
- [ ] I test data transformations and specifications as well as appearance.
- [ ] I state limitations and do not claim causality from a chart alone.

## 18. Authoritative documentation references

The roadmap establishes the required concepts and exercises. The following vendor/library documentation is supplemental implementation reference; exact APIs and limits can vary by version.

- Matplotlib documentation: https://matplotlib.org/stable/
- Matplotlib API (`Axes`): https://matplotlib.org/stable/api/axes_api.html
- Plotly Python documentation: https://plotly.com/python/
- Plotly Express: https://plotly.com/python/plotly-express/
- Dash documentation: https://dash.plotly.com/
- Altair documentation: https://altair-viz.github.io/
- Vega-Lite documentation: https://vega.github.io/vega-lite/
- Seaborn documentation: https://seaborn.pydata.org/
- Datashader documentation: https://datashader.org/
- Streamlit documentation: https://docs.streamlit.io/
- Panel documentation: https://panel.holoviz.org/
- Quarto documentation: https://quarto.org/docs/
- Jupyter documentation: https://docs.jupyter.org/
- Evidence documentation: https://docs.evidence.dev/
- W3C Web Content Accessibility Guidelines (WCAG): https://www.w3.org/WAI/standards-guidelines/wcag/

**Source alignment:** This lesson follows Topic 08 in `roadmap-Analytics-Foundations-for-Data-Engineers.md` and the Stage 2C tree in `Roadmap_ptree.md`. It focuses on visualisation; stakeholder narrative and presentation strategy belong primarily to the next lesson, `09-data-storytelling-and-stakeholder-communication.md`.
