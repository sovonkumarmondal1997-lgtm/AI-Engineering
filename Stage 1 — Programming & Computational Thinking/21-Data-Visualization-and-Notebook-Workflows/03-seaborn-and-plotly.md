# Seaborn and Plotly

> **Module 21 · Lesson 03**  
> Target environment: Python 3.12+, Seaborn 0.13+, Plotly 5/6, Matplotlib 3.9+, pandas 2.x (pandas is used for the small tabular examples).

## Learning outcomes

By the end of this lesson, you should be able to:

1. Reshape data into tidy/long form and explain why that structure helps plotting APIs.
2. Choose between Seaborn figure-level and axes-level functions, and select a plot that matches a question.
3. Interpret Seaborn's estimators and uncertainty displays without overstating what they prove.
4. Build common static statistical plots and facets with Seaborn.
5. Build interactive charts with Plotly Express and customize them with `graph_objects`.
6. Export figures safely, understand HTML data exposure and optional static-export dependencies, and make plots reproducible and accessible.
7. Decide when Matplotlib, Seaborn, Plotly, or another visualization grammar is appropriate.

## 1. Why both libraries matter

**Seaborn** is a statistical visualization library built on Matplotlib. It offers concise APIs for distributions, relationships, categories, and facets. It is especially useful when you want sensible statistical defaults and a static figure suitable for a report.

**Plotly** provides interactive figures with hover, zoom, pan, and selection. Plotly Express (`px`) is the high-level starting point; `plotly.graph_objects` (`go`) gives more direct control over traces and layout.

Neither library makes a weak analytical question strong. Start with the question, data grain, units, and intended audience. Matplotlib remains valuable when precise low-level control or a custom static figure is the priority.

## 2. Setup and version assumptions

Use a project environment, for example:

```bash
uv init visualization-lesson
cd visualization-lesson
uv add "matplotlib>=3.9" "seaborn>=0.13" "plotly>=5" "pandas>=2" "numpy>=1.26"
uv add --dev pytest
```

These are version floors aligned to the module roadmap, not a claim that every future release behaves identically. Pin resolved versions in your lock file for reproducible work. Optional packages are only needed for optional workflows:

```bash
# Optional: static Plotly image export; install only if you need write_image().
uv add kaleido

# Optional: widgets and larger-data exploration
uv add ipywidgets anywidget datashader holoviews hvplot
```

Examples below use inline synthetic data and do not download datasets. They assume Seaborn 0.13+ and Plotly 5/6. Seaborn's `errorbar=` interface is the modern API; older Seaborn releases used `ci=` in some functions. Plotly static export depends on a compatible Kaleido setup; Kaleido v1 also requires a compatible Chrome/Chromium installation. Plotly 6 `FigureWidget` workflows require `anywidget` in addition to a compatible Jupyter widget environment. Treat both as optional dependencies and verify them in the target environment.

## 3. Tidy data: start with the grain

Tidy data usually means:
- each **row** is one observation at a clearly stated grain;
- each **column** is one variable;
- each cell contains one value.

For example, one row below is one pipeline run. `duration_s` is seconds, `rows_processed` is rows, and `pipeline` is a category.

```python
import pandas as pd

runs = pd.DataFrame(
    {
        "run_id": ["r01", "r02", "r03", "r04", "r05", "r06", "r07", "r08"],
        "pipeline": ["orders", "orders", "orders", "orders", "events", "events", "events", "events"],
        "day": ["Mon", "Tue", "Wed", "Thu", "Mon", "Tue", "Wed", "Thu"],
        "duration_s": [42, 47, 65, 51, 36, 39, 44, 80],
        "rows_processed": [1000, 990, 995, 1002, 2200, 2180, 2210, 1800],
    }
)
print(runs.head())
```

**Observe:** `pipeline`, `day`, `duration_s`, and `rows_processed` are separate variables. This makes it straightforward to map variables to x, y, colour (`hue`), facets, or hover fields.

A wide table such as one column per pipeline can be useful for human reading, but it is often less convenient for grouping and faceting. Convert it to long form with `melt`:

```python
import pandas as pd

wide = pd.DataFrame(
    {
        "day": ["Mon", "Tue", "Wed"],
        "orders": [42, 47, 65],
        "events": [36, 39, 44],
    }
)
long = wide.melt(id_vars="day", var_name="pipeline", value_name="duration_s")
print(long)
```

**Observe:** the two measurement columns become one `pipeline` column and one `duration_s` column. Confirm the grain before reshaping: melting is not a substitute for deciding what one row represents.

## 4. Seaborn — Basic

### 4.1 Figure-level versus axes-level functions

- **Figure-level:** `relplot`, `displot`, and `catplot` create and manage a figure and can facet with `row=`, `col=`, and `hue=`. They return a `FacetGrid`-style object (or related figure-level object).
- **Axes-level:** `scatterplot`, `histplot`, `kdeplot`, `ecdfplot`, `lineplot`, `barplot`, `boxplot`, `violinplot`, and `heatmap` draw into a Matplotlib `Axes`. Pass `ax=ax` when composing a Matplotlib layout.
- **`pairplot`:** a figure-level convenience for pairwise relationships; it creates a matrix of axes and can be expensive for many variables or rows.

Prefer figure-level functions when faceting is central. Prefer axes-level functions when you need to place a Seaborn plot into a manually designed Matplotlib figure.

### 4.2 Configure a theme

```python
import seaborn as sns

sns.set_theme(style="whitegrid", context="notebook", palette="colorblind")
```

`style` controls elements such as grid and background; `context` scales visual elements for contexts such as notebook, talk, or poster; `palette` sets categorical colours. `set_theme` changes Matplotlib defaults globally for the current process, so use it intentionally in shared libraries and tests.

### 4.3 Core plot families

The following independent examples use the `runs` dataset defined above.

```python
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="colorblind")

fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
sns.histplot(data=runs, x="duration_s", bins=5, color="#0072B2", ax=axes[0, 0])
axes[0, 0].set(title="Run-duration distribution", xlabel="Duration (s)", ylabel="Run count")

sns.ecdfplot(data=runs, x="duration_s", ax=axes[0, 1])
axes[0, 1].set(title="Empirical cumulative distribution", xlabel="Duration (s)", ylabel="Fraction ≤ x")

sns.scatterplot(data=runs, x="rows_processed", y="duration_s", hue="pipeline", style="pipeline", ax=axes[1, 0])
axes[1, 0].set(title="Rows processed vs duration", xlabel="Rows processed (rows)", ylabel="Duration (s)")

sns.boxplot(data=runs, x="pipeline", y="duration_s", ax=axes[1, 1])
axes[1, 1].set(title="Duration by pipeline", xlabel="Pipeline", ylabel="Duration (s)")
plt.show()
```

What to learn from each:
- **Histogram:** distribution shape depends on bin edges and bin count; state the binning when it matters.
- **KDE:** a smoothed density estimate; bandwidth affects smoothness and it can behave poorly with tiny samples or bounded/discrete data.
- **ECDF:** fraction of observations at or below each value; avoids bin-width choices.
- **Scatter:** relationship between two numeric variables; it does not prove causation.
- **Line plot:** ordered x-axis, typically time or another meaningful sequence.
- **Bar plot:** Seaborn's `barplot` estimates a summary (by default the mean) for each category and may show uncertainty; it is not automatically a count plot. Use `countplot` when the question is category frequency.
- **Box plot:** median, quartiles, whiskers and potential outliers according to the chosen convention; not every point is displayed.
- **Violin plot:** smoothed distribution shape; the density is an estimate and can overemphasize shapes with small samples.
- **Heatmap:** values in a matrix encoded by colour; labels and colour scale determine whether it is interpretable.
- **Pair plot:** multiple pairwise views; useful for small feature sets, but cluttered and expensive with many variables.

KDE example:

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, ax = plt.subplots(figsize=(6, 3.5))
sns.kdeplot(data=runs, x="duration_s", fill=True, color="#0072B2", ax=ax)
ax.set(title="Smoothed duration density", xlabel="Duration (s)", ylabel="Density (1/s)")
plt.show()
```

The density's units are inverse seconds; the area under a properly normalized one-dimensional density is approximately one. Do not treat a KDE peak as a direct count.

### 4.4 Figure-level faceting

```python
import seaborn as sns

sns.set_theme(style="whitegrid", context="notebook", palette="colorblind")
grid = sns.displot(
    data=runs,
    x="duration_s",
    hue="pipeline",
    col="pipeline",
    kind="hist",
    bins=5,
    height=3,
    aspect=1.1,
)
grid.set_axis_labels("Duration (s)", "Run count")
```

The `col=` facet gives each pipeline its own panel; `hue=` redundantly identifies the pipeline. In this specific two-panel chart, hue may be unnecessary, but the example demonstrates the API. Avoid redundant encodings when they do not add information. For comparable distributions, keep bins and axis scales consistent.

## 5. Seaborn — Intermediate

### 5.1 Statistical estimation and uncertainty

A statistical plot can summarize many observations into a point. The displayed point is an **estimator**, and its band or bars represent a configured measure of variation or uncertainty. Always state what was estimated and what the interval means.

For Seaborn 0.13+, `lineplot` and `barplot` support `errorbar=`. Common choices include:
- `("ci", 95)`: a 95% confidence interval for the estimator, generally computed using bootstrap resampling for supported estimators;
- `"sd"`: standard deviation around the estimate;
- `"se"`: standard error;
- `"pi"`: a percentile interval spanning a chosen proportion of the observed values in each group, where supported. In Seaborn this is not a model-based forecast interval for future observations.
- `errorbar=None`: omit the uncertainty display.

A confidence interval is not the range containing 95% of individual observations. SD describes spread in the observations; SE describes the standard error of the estimator. Seaborn's `"pi"` interval is a percentile interval over observed values, not a model-based forecast interval for future observations. Do not use these terms interchangeably, and remember that none of these options fixes confounding, dependence, or a poorly chosen unit of analysis.

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

daily = pd.DataFrame(
    {
        "day": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4],
        "duration_s": [40, 44, 48, 45, 49, 55, 52, 57, 61, 43, 50, 59],
    }
)
fig, ax = plt.subplots(figsize=(6, 3.5))
sns.lineplot(
    data=daily,
    x="day",
    y="duration_s",
    estimator="mean",
    errorbar=("ci", 95),
    n_boot=1000,
    seed=7,
    marker="o",
    ax=ax,
)
ax.set(title="Mean duration by day with 95% bootstrap CI", xlabel="Day", ylabel="Duration (s)")
plt.show()
```

For the classic functions covered here, `n_boot` defaults to 1,000 bootstrap resamples in the target Seaborn API; set it explicitly when reproducibility and compute cost matter. `seed` makes resampling reproducible in supported versions. More resamples cost more compute and reduce Monte Carlo noise; they do not repair biased or non-independent data. The synthetic observations are illustrative, not empirical evidence.

### 5.2 Category ordering and reshaping

Use explicit ordering when categories have a natural sequence or when consistent ordering across plots matters.

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

summary = pd.DataFrame(
    {"pipeline": ["orders", "events", "billing"], "p95_s": [65, 80, 54]}
)
order = ["billing", "orders", "events"]
fig, ax = plt.subplots(figsize=(6, 3.5))
sns.barplot(data=summary, x="pipeline", y="p95_s", order=order, errorbar=None, color="#0072B2", ax=ax)
ax.set(title="p95 duration by pipeline", xlabel="Pipeline", ylabel="p95 duration (s)")
plt.show()
```

This table contains already-computed p95 values, not individual observations. `errorbar=None` is appropriate here because the plot is not estimating uncertainty from raw replicates. Do not apply a default mean estimator to a pre-aggregated metric and then imply it is a new distributional estimate.

### 5.3 Combine Seaborn and Matplotlib

Axes-level Seaborn functions accept `ax=`, after which Matplotlib methods can customize the same axes. `sns.despine()` removes selected top/right spines for a cleaner design.

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, ax = plt.subplots(figsize=(6, 3.5))
sns.scatterplot(data=runs, x="rows_processed", y="duration_s", hue="pipeline", ax=ax)
ax.set(
    title="Run duration versus processed rows",
    xlabel="Rows processed (rows)",
    ylabel="Duration (s)",
)
sns.despine(ax=ax)
plt.show()
```

`FacetGrid` and `PairGrid` are figure-level grid objects with customization methods and axes available through the grid. For example, use `grid.set_axis_labels(...)` for facet labels and `grid.map_dataframe(...)` to map an axes-level function over facet subsets. Start with `relplot`/`displot`/`catplot` before building a custom grid manually.

A custom `FacetGrid` is useful when a figure-level convenience function does not provide the mapping you need. This example explicitly defines the facet variable and calls an axes-level function for each subset:

```python
import matplotlib.pyplot as plt
import seaborn as sns

facet = sns.FacetGrid(runs, col="pipeline", col_order=["orders", "events"], sharex=True, sharey=True, height=3)
facet.map_dataframe(sns.histplot, x="duration_s", bins=[30, 40, 50, 60, 70, 80, 90], color="#0072B2")
facet.set_axis_labels("Duration (s)", "Run count")
facet.set_titles("Pipeline: {col_name}")
plt.show()
```

For a small feature set, `PairGrid` allows explicit mapping of the diagonal and off-diagonal panels. Pairwise plots become cluttered quickly as the number of features grows; use only meaningful numeric variables and label the plot as exploratory.

```python
import matplotlib.pyplot as plt
import seaborn as sns

features = runs[["duration_s", "rows_processed"]].copy()
grid = sns.PairGrid(features)
grid.map_diag(sns.histplot, color="#0072B2")
grid.map_offdiag(sns.scatterplot, color="#D55E00", alpha=0.8)
plt.show()
```

### 5.4 Heatmaps: scales, labels, and masks

Use a diverging palette centred at zero when values represent signed deviation around a meaningful zero. Use sequential palettes for magnitude on one side of a reference. Annotate cells when the matrix is small enough to remain readable.

```python
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

corr = pd.DataFrame(
    [[1.0, 0.6, -0.2], [0.6, 1.0, 0.1], [-0.2, 0.1, 1.0]],
    index=["duration", "rows", "retries"],
    columns=["duration", "rows", "retries"],
)
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
fig, ax = plt.subplots(figsize=(5, 4))
sns.heatmap(
    corr,
    mask=mask,
    annot=True,
    fmt=".2f",
    cmap="RdBu_r",
    center=0,
    vmin=-1,
    vmax=1,
    square=True,
    ax=ax,
)
ax.set_title("Illustrative correlation matrix")
plt.show()
```

This is a synthetic, illustrative matrix. Correlation does not imply causation; correlated columns may share a cause, and correlation may be unstable with small samples. `sns.clustermap` can reorder rows/columns by similarity, but clustering choices affect the order and should be explained.

## 6. Plotly — Basic and Intermediate

### 6.1 Plotly Express versus `graph_objects`

- **Plotly Express (`px`)** is a concise, data-frame-friendly API for common charts and faceting. Use it first for line, scatter, bar, histogram, box, image/heatmap, scatter-matrix, and animation charts.
- **`graph_objects` (`go`)** represents lower-level figure objects, traces, and layout. Use it when you need fine-grained trace configuration, custom hover templates, or a chart that is awkward to express through `px`.
- Both return Plotly figures that can be displayed in notebooks and exported.

### 6.2 Interactive chart with Plotly Express

```python
import pandas as pd
import plotly.express as px

runs = pd.DataFrame(
    {
        "run_id": ["r01", "r02", "r03", "r04", "r05", "r06", "r07", "r08"],
        "pipeline": ["orders", "orders", "orders", "orders", "events", "events", "events", "events"],
        "day": ["Mon", "Tue", "Wed", "Thu", "Mon", "Tue", "Wed", "Thu"],
        "duration_s": [42, 47, 65, 51, 36, 39, 44, 80],
        "rows_processed": [1000, 990, 995, 1002, 2200, 2180, 2210, 1800],
    }
)
fig = px.scatter(
    runs,
    x="rows_processed",
    y="duration_s",
    color="pipeline",
    symbol="pipeline",
    hover_data=["run_id", "day"],
    title="Pipeline run duration versus rows processed",
    labels={"rows_processed": "Rows processed (rows)", "duration_s": "Duration (s)"},
    template="plotly_white",
    color_discrete_map={"orders": "#0072B2", "events": "#D55E00"},
)
fig.update_layout(legend_title_text="Pipeline")
fig.show()
```

Hover and zoom help analysts inspect points without crowding the static plot with labels. The explicit colour mapping keeps category colours consistent across figures. Colour is not the only encoding: symbols also differ.

### 6.3 Facets, traces, and layout

```python
import pandas as pd
import plotly.express as px

df = pd.DataFrame(
    {
        "pipeline": ["orders", "orders", "orders", "events", "events", "events"],
        "day": [1, 2, 3, 1, 2, 3],
        "duration_s": [42, 47, 65, 36, 39, 44],
    }
)
fig = px.line(
    df,
    x="day",
    y="duration_s",
    color="pipeline",
    facet_col="pipeline",
    markers=True,
    title="Duration by pipeline",
    labels={"day": "Day index", "duration_s": "Duration (s)"},
    template="plotly_white",
    color_discrete_map={"orders": "#0072B2", "events": "#D55E00"},
)
fig.update_layout(hovermode="x unified")
fig.update_traces(line_width=2)
fig.show()
```

Faceting creates separate panels; do not compare panel heights unless the y-axis scales are comparable. `update_layout` changes figure-level properties; `update_traces` changes trace properties. `animation_frame=` can show changes across a meaningful ordered variable, but animation can make precise comparisons difficult and should not replace small multiples when side-by-side comparison matters.

### 6.4 Use `graph_objects` for custom control

```python
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=[1, 2, 3, 4],
        y=[42, 47, 65, 51],
        mode="lines+markers",
        name="orders",
        line={"color": "#0072B2"},
        customdata=[["r01"], ["r02"], ["r03"], ["r04"]],
        hovertemplate="Day index: %{x}<br>Duration: %{y} s<br>Run: %{customdata[0]}<extra></extra>",
    )
)
fig.update_layout(
    title="Orders pipeline duration",
    xaxis_title="Day index",
    yaxis_title="Duration (s)",
    template="plotly_white",
)
fig.show()
```

`customdata` carries fields for hover templates without plotting them as axes. Only include fields appropriate to the audience. Do not place secrets, personal identifiers, or sensitive raw data into a figure that will be shared.

### 6.5 Export and sharing

```python
# `fig` is a Plotly figure created in a preceding example.
fig.write_html("pipeline_duration.html", include_plotlyjs="cdn")
json_text = fig.to_json()
```

- `fig.show()` displays in supported notebooks or configured renderers.
- `write_html(..., include_plotlyjs="cdn")` makes a smaller HTML file that loads Plotly.js from a CDN; it requires network access when opened.
- `write_html(..., include_plotlyjs=True)` embeds the JavaScript bundle for offline use, creating a larger file. The figure's plotted data, labels, custom data, and hover fields are still embedded; the entire source DataFrame is not necessarily included unless you plot/export it all.
- `fig.to_json()` serializes the figure specification and data. Treat the JSON as a data artifact, not as a secret-safe wrapper.
- `fig.write_image("figure.png")` requires a compatible Kaleido installation and its runtime requirements. Kaleido v1 requires a compatible Chrome/Chromium binary; older Plotly/Kaleido combinations have different requirements. Static export behavior depends on Plotly/Kaleido versions; test it in the target environment. PNG is raster; SVG/PDF may be available depending on the installed export engine.

When the optional export dependencies are installed, run this against a figure created above. It is intentionally separate from the always-available HTML/JSON examples because the Kaleido runtime is not part of the base environment:

```python
# Optional: requires a compatible Kaleido installation; Kaleido v1 also needs Chrome/Chromium.
fig.write_image("pipeline_duration_plotly.png", width=1200, height=800, scale=2)
```

Do not export a figure with sensitive data merely because it is “only a chart.” Inspect hover fields and embedded data before sharing.

## 7. Choosing Matplotlib, Seaborn, or Plotly

| Need | Good starting point | Why | Trade-off |
|---|---|---|---|
| Precise custom static layout | Matplotlib | Low-level control over artists and axes | More code for statistical summaries |
| Statistical distributions and category comparisons | Seaborn | Concise statistical plotting and faceting | Defaults/estimators must be understood |
| Interactive exploration and shareable HTML | Plotly Express | Hover, zoom, facets, animation | HTML can expose embedded data; larger payloads |
| Highly customized interactive traces/layout | Plotly `graph_objects` | Explicit trace and layout control | More verbose |
| Declarative visualization grammar | Altair/Vega-Lite or plotnine | Specify data, encodings, and transformations declaratively | Different grammar and ecosystem |
| Browser-native/custom interactive visualization | Bokeh | Interactive Python visualization model | Different API and deployment considerations |
| Very large rasterized/aggregated data | HoloViz, hvPlot, Datashader | Designed for large-scale aggregation/rendering workflows | Additional ecosystem concepts and dependencies |

No library is universally best. Choose based on audience, chart complexity, data volume, deployment, reproducibility, and security constraints.

## 8. Advanced concepts

### 8.1 Seaborn objects interface

Seaborn's `seaborn.objects` API is a more declarative, grammar-style interface than the classic functions. It composes a plot from data, mappings, marks, statistical transforms, scales, and layout decisions. The classic API remains concise and widely used; the objects API can make complex compositions more systematic. It is available in the Seaborn 0.13+ target range, but specific mark/stat/scale features may evolve across versions.

```python
import pandas as pd
import seaborn.objects as so

df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 5, 4, 7]})
plot = so.Plot(df, x="x", y="y").add(so.Dot())
plot.show()
```

This small example uses a dot mark. Explore `so.Agg()` and other statistical transforms only when you can state what aggregation is being performed. Do not assume the objects API is a drop-in replacement for every classic function.

### 8.2 Large data and performance

A chart should preserve the structure needed for the decision without rendering every raw row.

- **Aggregate first** when the question concerns counts, rates, quantiles, or trends at a defined time window. Document the aggregation window and denominator.
- **Downsample** with a fixed seed when a sample is sufficient for exploratory inspection; do not use sampling to estimate rare-event rates without assessing its consequences.
- **Alpha blending** can reveal density for moderate point counts but may still be slow and opaque.
- **WebGL** traces such as `go.Scattergl` can help with large scatter plots (often around \(10^5\)–\(10^6\) points depending on hardware/browser), but have feature, rendering, and portability trade-offs. In current Plotly Express versions, prefer `px.scatter(..., render_mode="webgl")` when supported; older examples may use `px.scatter_gl`, which is version-sensitive and should not be presented as a universal API. `go.Scattergl` remains an explicit lower-level option.
- **Hexbin/2-D histograms** summarize point density instead of drawing every point.
- **Datashader** with HoloViews/hvPlot is worth considering for very large datasets, including millions of rows, where raster aggregation is more appropriate.
- Use pandas, Polars, or PyArrow deliberately; conversions can copy data and consume memory. Avoid unnecessary conversion chains, and aggregate in SQL/DuckDB or a lazy data engine when it reduces transfer and memory.
- Cache expensive aggregations only with explicit keys/invalidation that include data version and parameters.

For example, with a large table already loaded, Plotly Express can select a WebGL rendering path when the installed version supports it:

```python
import pandas as pd
import plotly.express as px

points = pd.DataFrame({"x": range(10_000), "y": [(i * 17) % 997 for i in range(10_000)]})
fig = px.scatter(points, x="x", y="y", render_mode="webgl", title="Synthetic points rendered with WebGL")
fig.show()
```

This demonstrates the API, not a universal performance guarantee. Benchmark on the target browser and hardware; WebGL can have export, accessibility, and rendering limitations. For very large or dense data, aggregation or rasterization can be more effective than plotting every point.

### 8.3 Widgets and when to build an app

`ipywidgets` sliders and dropdowns are useful for notebook parameter exploration. Plotly `FigureWidget` can support widget-linked interactive figures in compatible notebook environments; for Plotly 6, install `anywidget` as well as a compatible Jupyter widget stack. This optional integration is environment-sensitive and is not required for ordinary `fig.show()` output. Linked brushing can reveal relationships across charts but adds cognitive load and testing needs.

The following optional example links a slider to a `FigureWidget`. Install `ipywidgets` and `anywidget` first, and run it in a supported Jupyter environment; this widget-specific interaction is not required for standard Plotly output.

```python
import ipywidgets as widgets
import plotly.graph_objects as go
from IPython.display import display

slider = widgets.IntSlider(value=1, min=1, max=5, description="Multiplier")
fig_widget = go.FigureWidget(data=[go.Scatter(x=[1, 2, 3], y=[1, 4, 9], mode="lines+markers")])

def update_curve(change):
    if change["name"] == "value":
        with fig_widget.batch_update():
            fig_widget.data[0].y = [change["new"] * x * x for x in [1, 2, 3]]

slider.observe(update_curve, names="value")
display(slider, fig_widget)
```

For linked brushing across multiple charts, share a stable row identifier and coordinate selections explicitly. Avoid sending the full raw table to the browser when server-side filtering or aggregation can meet the interaction need.

A compact animation example shows the Plotly Express API; use an ordered, meaningful frame variable and remember that animation is not a substitute for side-by-side comparison when exact differences matter:

```python
import pandas as pd
import plotly.express as px

trend = pd.DataFrame({
    "year": [2024, 2025, 2026, 2024, 2025, 2026],
    "pipeline": ["orders"] * 3 + ["events"] * 3,
    "duration_s": [48, 45, 43, 61, 55, 50],
})
fig = px.bar(
    trend, x="pipeline", y="duration_s", color="pipeline",
    animation_frame="year", range_y=[0, 70],
    category_orders={"year": [2024, 2025, 2026], "pipeline": ["orders", "events"]},
    color_discrete_map={"orders": "#0072B2", "events": "#D55E00"},
    labels={"duration_s": "Duration (s)", "pipeline": "Pipeline", "year": "Year"},
    title="Illustrative pipeline duration by year", template="plotly_white",
)
fig.show()
```

The synthetic values illustrate the API only. The fixed y-range keeps the frame scale stable; the zero baseline is appropriate for duration.

Move from a notebook to an application when users need durable shared state, authentication, scheduled refreshes, operational ownership, or controlled access. At a high level:
- **Dash** uses callback-driven updates around Plotly figures.
- **Streamlit** typically reruns a script in response to interaction and provides session-state mechanisms.
- **Panel/Gradio** serve other interactive application needs.
A real app introduces deployment, authentication, authorization, observability, dependency management, and data-access control. Never rely on hiding a UI control as access control; authorize data on the server.

### 8.4 Cross-library consistency

Use a shared category palette and stable category ordering so the same category means the same thing in static reports and interactive charts.

```python
PIPELINE_COLORS = {
    "orders": "#0072B2",
    "events": "#D55E00",
    "billing": "#009E73",
}
PIPELINE_ORDER = ["orders", "events", "billing"]
```

In Seaborn, pass `palette=PIPELINE_COLORS` to a categorical `hue` mapping. In Plotly Express, pass `color_discrete_map=PIPELINE_COLORS` and `category_orders={"pipeline": PIPELINE_ORDER}`. Define a small `plotkit.themes` module for these shared choices and common labels. Helpers should accept data and explicit configuration rather than mutate global plotting state unexpectedly.

### 8.5 Reproducibility and visual regression

- Sort categories and time values explicitly.
- Fix random seeds for sampling and bootstrap procedures.
- Record data snapshot/version, aggregation parameters, timezone, and library versions.
- Cache costly aggregation only with explicit invalidation.
- Pin versions because layout and rendering can change between versions.
- Test the data and semantic properties of figures, not only pixels.
- If using golden-image tests, use tolerances for fonts, antialiasing, platform differences, and library changes; review material changes instead of blindly widening tolerances.

### 8.6 Model-evaluation gallery preview

This is a preview of later ML material, not a full evaluation lesson:

| Question | Suitable chart | Static Seaborn/Matplotlib role | Plotly role | Main caution |
|---|---|---|---|---|
| Which classes are confused? | Confusion-matrix heatmap, often normalized | Publication-ready labelled matrix | Hover exact cells and zoom | Show normalization denominator and class order |
| How does discrimination vary by threshold? | ROC or precision-recall curve | Stable static report figure | Hover threshold points | Curves depend on dataset, class prevalence, and evaluation protocol |
| Are predicted probabilities calibrated? | Reliability/calibration plot | Compact static curve with reference line | Interactive bin inspection | State binning and sample count; avoid overinterpreting sparse bins |
| Does training improve generalization? | Learning curves | Side-by-side static runs | Hover training steps/runs | Keep train/validation definitions explicit |
| How do errors vary with prediction? | Residual plot | Clear static diagnostic | Hover unusual cases | Patterns are diagnostics, not automatic proof of a cause |
| What is the quality/cost/latency trade-off? | Scatter/Pareto view | Direct labels for selected candidates | Hover detailed metrics | State units, evaluation set, and which direction is better |

Build the gallery only after the evaluation definitions and data split are established. Do not infer model quality from a chart alone.

## 9. Mini-case: pipeline duration — static and interactive

**Decision:** identify whether one pipeline has a high-duration run worth investigating. The dataset is synthetic and deliberately small. Duration is in seconds; rows processed is a count. With only four runs per pipeline, this chart supports inspection, not a robust population claim.

### Static Seaborn chart

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

runs = pd.DataFrame(
    {
        "run_id": ["o1", "o2", "o3", "o4", "e1", "e2", "e3", "e4"],
        "pipeline": ["orders"] * 4 + ["events"] * 4,
        "duration_s": [42, 47, 65, 51, 36, 39, 44, 80],
        "rows_processed": [1000, 990, 995, 1002, 2200, 2180, 2210, 1800],
    }
)
palette = {"orders": "#0072B2", "events": "#D55E00"}
fig, ax = plt.subplots(figsize=(6.5, 4))
sns.stripplot(
    data=runs,
    x="pipeline",
    y="duration_s",
    hue="pipeline",
    order=["orders", "events"],
    hue_order=["orders", "events"],
    palette=palette,
    jitter=False,
    legend=False,
    ax=ax,
)
ax.set(
    title="Events pipeline has the longest observed run",
    xlabel="Pipeline",
    ylabel="Run duration (s)",
)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig("pipeline_duration.png", dpi=160, bbox_inches="tight")
plt.show()
```

**Observation:** the events pipeline has an observed 80-second run. This is a reason to inspect that run and its context, not proof that the events pipeline is generally slower. A production view should include more history, run status, workload, and comparable time windows.

### Interactive Plotly chart

```python
import pandas as pd
import plotly.express as px

runs = pd.DataFrame(
    {
        "run_id": ["o1", "o2", "o3", "o4", "e1", "e2", "e3", "e4"],
        "pipeline": ["orders"] * 4 + ["events"] * 4,
        "duration_s": [42, 47, 65, 51, 36, 39, 44, 80],
        "rows_processed": [1000, 990, 995, 1002, 2200, 2180, 2210, 1800],
    }
)
fig = px.scatter(
    runs,
    x="rows_processed",
    y="duration_s",
    color="pipeline",
    symbol="pipeline",
    hover_name="run_id",
    labels={"rows_processed": "Rows processed (rows)", "duration_s": "Duration (s)"},
    title="Inspect pipeline runs by workload and duration",
    template="plotly_white",
    color_discrete_map={"orders": "#0072B2", "events": "#D55E00"},
    category_orders={"pipeline": ["orders", "events"]},
)
fig.update_traces(marker={"size": 10, "opacity": 0.85})
fig.show()
```

**Why use each:** Seaborn/Matplotlib gives a compact static comparison for reports and version control. Plotly adds hover detail for exploration. Before sharing the HTML, inspect the serialized data and hover fields; synthetic data is safe for this exercise, but production run identifiers may not be.

## 10. Accessibility, privacy, and export checklist

- **Colour:** use colourblind-aware palettes; preserve a stable category-to-colour mapping. Do not use colour as the only channel—add symbols, line styles, direct labels, or annotations.
- **Contrast and type:** readable font sizes and sufficient contrast matter in both static and interactive charts. Check at the actual size where the figure will be viewed.
- **Grayscale and alt text:** check whether the key comparison survives grayscale printing. Supply meaningful alt text or a long description when publishing figures; state the takeaway and important caveats.
- **Uncertainty and denominators:** label units, sample size, aggregation, interval type, and relevant denominators. Do not imply precision that the data cannot support.
- **Privacy:** exported HTML and JSON may contain all rows actually plotted, custom data, labels, and hover fields; they do not necessarily contain unrelated rows from the source DataFrame. Aggregate/sample appropriately, redact identifiers, inspect generated files, and enforce access control outside the client-side figure.
- **CDN versus offline:** CDN HTML is smaller but needs network access; embedded Plotly.js works offline but increases file size. Both can include figure data.
- **Static output:** PNG is convenient for web and slides; PDF/SVG preserve vector elements where supported. Static Plotly export requires a compatible Kaleido installation. Test export on the deployment machine.
- **Reproducibility:** lock dependencies, record versions and data snapshots, use deterministic category order and seeds, and use image-regression tolerances when comparing rendered figures.

## 11. Exercises

### Exercise 1 — Tidy the dataset
Create a wide table with `day`, `orders`, and `events` duration columns, then use `melt` to produce `day`, `pipeline`, and `duration_s`.

**Acceptance criteria:** each row represents one pipeline/day observation; columns are named explicitly; no values are silently dropped.

### Exercise 2 — Choose a Seaborn API
Build (a) one axes-level scatter plot embedded in a Matplotlib figure and (b) a figure-level faceted histogram by pipeline.

**Acceptance criteria:** both have units and informative titles; shared bins/scales are used where direct comparison is intended; explain why each API fits its layout.

### Exercise 3 — State uncertainty correctly
Plot mean duration by day with `errorbar=("ci", 95)` and then with `errorbar="sd"`.

**Acceptance criteria:** labels/caption distinguish the confidence interval from standard deviation; the report does not describe either as “the range of 95% of runs.”

### Exercise 4 — Static and interactive versions
Recreate the mini-case in Seaborn and Plotly using the same colour mapping and category order.

**Acceptance criteria:** category colours match; axes have units; Plotly hover fields are reviewed; HTML is not described as data-private.

### Exercise 5 — Export review
Export a static PNG and a Plotly HTML file from synthetic data. Inspect the HTML's hover fields and embedded data.

**Acceptance criteria:** static output has adequate dimensions/resolution; CDN/offline trade-off is documented; static Plotly export is attempted only with compatible Kaleido installed.

### Exercise 6 — Model-evaluation gallery preview
Choose two rows from the gallery table and sketch the static and interactive versions.

**Acceptance criteria:** state the evaluation question, sample/split, axes/units, aggregation, and one limitation; do not claim this lesson teaches the underlying ML metric.

## 12. Self-check answer key

### 1. What is the difference between a figure-level and an axes-level Seaborn function, and when can you combine them with Matplotlib?

Figure-level functions such as `relplot`, `displot`, and `catplot` manage a figure and support faceting through `row`, `col`, and `hue`. Axes-level functions such as `scatterplot`, `histplot`, and `boxplot` draw on a given Matplotlib `Axes`. Combine axes-level functions with Matplotlib when composing a custom multi-panel figure or when you need to add Matplotlib annotations and formatting. Use figure-level functions when faceting and automatic layout are the main need.

### 2. What does the shaded band in `sns.lineplot` represent by default and how do you change it?

In the roadmap's target Seaborn 0.13+ API, `lineplot` defaults to an estimator (typically the mean for repeated y-values at x) with a 95% confidence interval (`errorbar=("ci", 95)`) computed using bootstrap resampling. The band is an interval for the estimated statistic, not the range containing 95% of individual observations. Set `errorbar="sd"` for standard deviation, `errorbar="se"` for standard error, `errorbar="pi"` for a percentile interval over observed values where supported, or `errorbar=None` to remove it. Specify `estimator` and `n_boot` to make the aggregation procedure explicit. If observations are already aggregated, choose the estimator and uncertainty display accordingly.

### 3. Produce the same chart in Seaborn (static, PNG) and Plotly (interactive HTML) and list one decision in favour of each.

Use the pipeline-duration mini-case. Choose Seaborn/Matplotlib for a compact report image with controlled typography and stable static output. Choose Plotly for exploration where hover details and zoom help investigate runs. Before sharing the HTML, review embedded data and hover fields; use synthetic or appropriately aggregated data.

## 13. Completion checklist

- [ ] I can explain tidy/long-form data and use `melt`.
- [ ] I can distinguish figure-level from axes-level Seaborn functions.
- [ ] I can choose and interpret histograms, KDE, ECDF, scatter, line, bar, box, violin, heatmap, and pair plots.
- [ ] I can explain estimator, CI, SD, SE, prediction interval, and bootstrap count without conflating them.
- [ ] I can facet, order categories, combine Seaborn with Matplotlib, and style heatmaps.
- [ ] I can distinguish Plotly Express from `graph_objects` and update traces/layout.
- [ ] I can explain HTML/JSON privacy risks and Kaleido's role in static export.
- [ ] I can keep colour mapping, ordering, seeds, versions, and visual-regression expectations reproducible.
- [ ] I can choose between static and interactive charts based on the task and audience.
