# Matplotlib Figure and Axes Model

**Stage 1 — Programming & Computational Thinking · Module 21 — Data Visualization and Notebook Workflows · Lesson 01**

> Target environment: Python 3.12+, Matplotlib 3.9+. Examples use APIs available in that target range. The examples use small deterministic datasets and do not download data.

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain the `pyplot` state machine and the object-oriented (OO) API, and choose the OO API for reusable code.
- Distinguish `Figure`, `Axes`, `Axis`, and `Artist` accurately.
- Create and label common plots, compose multi-panel figures, control scales/ticks/annotations/styles, and export figures safely.
- Select plotting techniques for uncertainty, dense data, and time series without obscuring the underlying data.
- Write reusable plotting helpers, test their artist data, and understand server-side rendering and export trade-offs.
- Diagnose wrong-axes bugs, figure leaks, and opaque overplotting.

## 1. Why this matters in data engineering and AI engineering

A plot is a diagnostic instrument, not decoration. Data and AI engineers use figures to spot pipeline latency regressions, missing-data patterns, row-count drops, model-evaluation changes, cost spikes, and operational incidents. Matplotlib is also the foundation beneath many higher-level plotting APIs, including pandas plotting and Seaborn.

A quick `plt.plot(...)` is fine for a throw-away exploration. Production reports, functions, notebooks with multiple panels, and batch jobs need explicit control over which figure and axes receive each mark. Understanding the object model makes those operations predictable, testable, and easier to maintain.

This lesson focuses on Matplotlib mechanics. It does not attempt to teach experiment statistics, dashboard engineering, or heavy ML-specific plots.

## 2. Prerequisites and setup

You should know basic Python functions, lists, dictionaries, imports, files/paths, and tests. NumPy is used for numeric arrays; the core Matplotlib concepts also work with Python sequences and pandas Series.

### Required and optional dependencies

- **Required for the examples:** Python 3.12+, `matplotlib` 3.9+, `numpy`.
- **For tests:** `pytest`.
- **Optional for the wider module:** `pandas`, JupyterLab, `ipywidgets`, and `pytest-mpl` for image-comparison tests.
- **Optional animation exporters:** Pillow for GIF; `ffmpeg` for MP4.
- **Optional large-data companion:** Datashader. It is awareness-level here, not required.

Create a project and install only what this lesson needs:

```bash
uv init matplotlib-lesson
cd matplotlib-lesson
uv add "matplotlib>=3.9" "numpy>=1.26"
uv add --dev pytest
```

If `uv` is not available, use an activated virtual environment and `python -m pip install "matplotlib>=3.9" numpy pytest`. Pin exact versions in a lock file when reproducible visual output matters. The roadmap's broader module environment may also install Seaborn, Plotly, pandas, JupyterLab, and notebook tooling; those are not needed for this lesson's examples.

### Output directory

Examples save into `outputs/`. Create it first, or adapt paths to your project:

```bash
mkdir -p outputs
```

On Windows PowerShell, use `New-Item -ItemType Directory -Force outputs`.

## 3. The mental model: a canvas, plot areas, and drawable objects

Think of a **Figure** as the whole page or canvas. It contains one or more **Axes**, each of which is a plot area with its own data limits, scales, labels, ticks, and plotted content. Each Axes usually has two coordinate-bearing **Axis** objects: the x-axis and y-axis. Lines, text, tick labels, patches, images, collections, and legends are **Artist** objects that Matplotlib draws.

The roadmap's useful conceptual hierarchy is:

`Figure → Axes → Axis (x/y) → Artist`

This is a teaching hierarchy, not a literal ownership tree for every Artist. In the actual object model, an `Axes` contains many Artists directly (for example, lines, patches, texts, collections, images, and legends), while its x/y `Axis` objects manage ticks, tick labels, scale, and units. The `Figure` also contains figure-level Artists such as a suptitle. Not every Artist is a child of an `Axis`.

| Object | Responsibility | Common access | Example |
|---|---|---|---|
| `Figure` | Overall canvas, layout, figure-level text, export | `fig` | `fig.savefig("out.png")` |
| `Axes` | One plotting area and most plot commands | `ax` | `ax.plot(x, y)` |
| `Axis` | One dimension's scale, ticks, tick labels, units | `ax.xaxis`, `ax.yaxis` | `ax.xaxis.set_major_locator(...)` |
| `Artist` | A drawable element | returned object, `ax.lines`, `ax.texts` | `Line2D`, `Text`, `Rectangle` |

### 3.1 `pyplot` state machine versus OO API

`matplotlib.pyplot` (`plt`) provides a state-machine interface. Calls such as `plt.plot(...)`, `plt.title(...)`, and `plt.savefig(...)` act on the *current* Axes or Figure. The current target can change when a new subplot is selected or created, which makes state convenient interactively but risky in reusable functions and loops.

The OO API holds explicit references:

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.plot([0, 1, 2], [2, 1, 3], label="pipeline A")
ax.set(title="Example run metric", xlabel="Run index", ylabel="Duration (s)")
ax.legend()
fig.savefig("outputs/one-panel.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

`plt.subplots()` returns a Figure and an Axes (or an array of Axes when there are multiple panels). This explicit reference is preferred for reusable or multi-axes code because each plotting call names its destination, the helper can compose into an existing panel, and the caller controls saving and cleanup. `plt` is still useful for creating figures and closing them; the goal is not to ban `pyplot`, but to avoid relying on its implicit current-axes state.

**Expected observation:** a labelled line chart is saved to `outputs/one-panel.png`. `plt.close(fig)` releases pyplot's manager reference after saving; it does not invalidate the saved file or immediately guarantee every Python object is garbage-collected.

## 4. Basic: make and label plots

### 4.1 A small line plot

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 200)
fig, ax = plt.subplots(figsize=(6, 3.5))
ax.plot(x, np.sin(x), label="sin(x)")
ax.plot(x, np.cos(x), label="cos(x)", linestyle="--")
ax.set(xlabel="x (radians)", ylabel="Value (unitless)", title="Trigonometric functions")
ax.grid(True, alpha=0.3)
ax.legend()
fig.savefig("outputs/trig.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

- `figsize` is in inches, not pixels.
- `label` supplies legend text; `ax.legend()` displays it.
- Axis labels should include units where meaningful. Do not label a duration simply “value” if it is measured in milliseconds.
- `dpi=200` controls raster resolution; `bbox_inches="tight"` trims surrounding whitespace. Tight bounding boxes can change final pixel dimensions slightly.
- `ax.grid(...)` supports reading values. Keep gridlines subtle enough not to compete with data.

### 4.2 Core Axes plotting methods

These are independent mini-examples. Each starts with its own Figure/Axes; run one at a time or put the code into separate cells. Each closes its Figure after saving.

**Line — ordered measurements, often time series:**

```python
import matplotlib.pyplot as plt

x = [0, 1, 2, 3]
y = [10, 12, 11, 15]
fig, ax = plt.subplots()
ax.plot(x, y, marker="o", label="records processed")
ax.set(xlabel="Batch index", ylabel="Records", title="Throughput by batch")
ax.legend()
fig.savefig("outputs/line.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

**Scatter — relationship between two numeric variables:**

```python
import matplotlib.pyplot as plt

runtime_s = [2.1, 2.4, 3.0, 4.2, 5.1]
rows = [1000, 1300, 1200, 2500, 3100]
fig, ax = plt.subplots()
ax.scatter(runtime_s, rows, alpha=0.75, s=35)
ax.set(xlabel="Runtime (s)", ylabel="Rows processed", title="Runtime versus input size")
fig.savefig("outputs/scatter.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

**Bars — category comparison; use horizontal bars for long labels:**

```python
import matplotlib.pyplot as plt

stages = ["Extract", "Validate", "Transform"]
seconds = [4.2, 1.7, 6.3]
fig, axes = plt.subplots(1, 2, figsize=(8, 3), constrained_layout=True)
axes[0].bar(stages, seconds)
axes[0].set(title="Vertical bars", ylabel="Duration (s)")
axes[1].barh(stages, seconds)
axes[1].set(title="Horizontal bars", xlabel="Duration (s)")
fig.savefig("outputs/bars.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

**Histogram — distribution of one numeric variable:**

```python
import matplotlib.pyplot as plt

latency_ms = [18, 20, 21, 21, 22, 24, 27, 30, 34, 45, 61]
fig, ax = plt.subplots()
ax.hist(latency_ms, bins=6, edgecolor="white")
ax.set(xlabel="Latency (ms)", ylabel="Number of requests", title="Request latency distribution")
fig.savefig("outputs/histogram.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

**Box plot — compact distribution summary across groups:**

```python
import matplotlib.pyplot as plt

before = [18, 19, 20, 21, 22, 24, 35]
after = [19, 20, 22, 23, 24, 26, 42]
fig, ax = plt.subplots()
ax.boxplot([before, after], tick_labels=["Before", "After"])
ax.set(ylabel="Latency (ms)", title="Latency before and after a change")
fig.savefig("outputs/boxplot.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

`tick_labels` is supported by the target Matplotlib 3.9+ version. If maintaining code for older Matplotlib releases, check that release's `boxplot` signature (older versions commonly used `labels`). A box plot hides individual observations unless you add a strip/scatter layer; sample size and outlier semantics should be clear.

**Image — 2-D numeric grid, such as a small heatmap:**

```python
import numpy as np
import matplotlib.pyplot as plt

values = np.array([[2, 4, 1], [3, 7, 5], [1, 2, 6]])
fig, ax = plt.subplots()
image = ax.imshow(values, cmap="viridis", aspect="auto")
ax.set(title="Stage-by-day measurements", xlabel="Day index", ylabel="Stage index")
fig.colorbar(image, ax=ax, label="Measurement (units)")
fig.savefig("outputs/image.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

`imshow` maps array values to colours. Use a colourbar and state what values mean; choose `origin`, `extent`, and aspect deliberately when array indices are not the intended coordinates.

### 4.3 The `Artist` return value is useful

Most plotting calls return Artist objects or containers of Artists. Keep those references when you need to update, inspect, or test the result.

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
(line,) = ax.plot([0, 1, 2], [2, 1, 3], marker="o")
print(line.get_xdata())  # [0 1 2] (array-like output)
print(line.get_ydata())  # [2 1 3]
plt.close(fig)
```

The comma in `(line,)` unpacks the one-element list returned by `plot`. This explicit Artist reference is more robust than assuming a particular item remains at `ax.lines[0]` after other code adds lines.

## 5. Intermediate: compose figures and control scales

### 5.1 Multiple Axes, shared scales, and layout

```python
import numpy as np
import matplotlib.pyplot as plt

latency_ms = np.array([12, 14, 15, 16, 18, 19, 21, 24, 28, 35, 52, 90], dtype=float)
fig, axes = plt.subplots(
    1, 2, figsize=(9, 3.4), sharey=True, constrained_layout=True
)
axes[0].hist(latency_ms, bins=6, edgecolor="white")
axes[0].set(title="Latency", xlabel="Latency (ms)", ylabel="Request count")
axes[1].hist(np.log10(latency_ms), bins=6, edgecolor="white")
axes[1].set(title="Log-transformed latency", xlabel="log10(latency / ms)")
p95_ms = float(np.percentile(latency_ms, 95))
axes[0].axvline(p95_ms, color="crimson", linestyle=":", label="p95")
axes[1].axvline(np.log10(p95_ms), color="crimson", linestyle=":", label="p95")
axes[0].legend()
axes[1].legend()
fig.savefig("outputs/two-histograms.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

The percentile is expressed in milliseconds on the raw histogram and in `log10(milliseconds)` on the transformed histogram. This illustrates why every panel's coordinate system must be considered independently.

- With `sharex=True` or `sharey=True`, Matplotlib links the corresponding axes, making comparisons easier and reducing inconsistent scales. Shared axes can also hide meaningful local variation, so choose intentionally.
- `constrained_layout=True` asks Matplotlib to arrange labels and panels to reduce overlap. It is usually a good starting point; manually calling `tight_layout()` as well is generally unnecessary.
- For a 1×N or N×1 layout, `axes` is typically a NumPy array; for a single subplot it is a single Axes unless `squeeze=False` is passed. If you want a stable 2-D array, use `plt.subplots(..., squeeze=False)`.

For a non-grid layout, `fig.subplot_mosaic("AB;CC")` creates two top panels (`A`, `B`) and a bottom panel spanning two columns (`C`):

```python
import matplotlib.pyplot as plt

fig, axd = plt.subplot_mosaic("AB;CC", figsize=(8, 5), constrained_layout=True)
axd["A"].plot([1, 2, 3], [2, 4, 3])
axd["A"].set(title="Throughput", ylabel="Rows/s")
axd["B"].bar(["A", "B"], [4, 6])
axd["B"].set(title="Failures", ylabel="Count")
axd["C"].plot([1, 2, 3, 4], [10, 9, 12, 11])
axd["C"].set(title="End-to-end duration", xlabel="Run", ylabel="Seconds")
fig.savefig("outputs/mosaic.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

### 5.2 Twin axes: use sparingly

`ax.twinx()` adds another Axes sharing the x-axis but with an independent y-axis on the right. It can be appropriate when two measurements share x coordinates but have different units; it can also imply a relationship that is an artefact of arbitrary axis limits. Prefer separate panels with aligned x axes in most analytical reports. If twin axes are necessary, label both units clearly, distinguish lines without relying on colour alone, and explain why separate panels are inadequate.

```python
import matplotlib.pyplot as plt

runs = [1, 2, 3, 4, 5]
latency_ms = [80, 82, 95, 110, 108]
cost_usd = [0.12, 0.13, 0.14, 0.19, 0.18]
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
line1, = ax1.plot(runs, latency_ms, marker="o", label="Latency")
line2, = ax2.plot(runs, cost_usd, marker="s", linestyle="--", label="Cost")
ax1.set(xlabel="Pipeline run", ylabel="Latency (ms)", title="Latency and cost (different units)")
ax2.set_ylabel("Cost (USD)")
ax1.legend([line1, line2], [line1.get_label(), line2.get_label()], loc="upper left")
fig.savefig("outputs/twin-axes.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

### 5.3 Linear, logarithmic, and symmetric-log scales

- **Linear:** equal distances represent equal additive differences. Default and usually easiest to interpret.
- **Log:** equal distances represent equal multiplicative ratios. All plotted values on that axis must be positive; zero and negative values cannot be displayed normally.
- **Symlog:** supports negative, zero, and positive values while using a linear region near zero and logarithmic behaviour farther away. It is useful for signed values spanning orders of magnitude, but the linear threshold must be understood and labelled.

```python
import matplotlib.pyplot as plt

values = [0.01, 0.1, 1, 10, 100]
fig, axes = plt.subplots(1, 3, figsize=(10, 3), constrained_layout=True)
for ax, scale in zip(axes, ["linear", "log", "symlog"]):
    ax.plot(values, marker="o")
    ax.set_yscale(scale)
    ax.set(title=f"{scale} y-scale", xlabel="Observation index", ylabel="Value")
fig.savefig("outputs/scales.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

For a true symlog demonstration including negative values, use `values = [-100, -10, -1, 0, 1, 10, 100]` and plot those values directly. Do not silently drop zeros or negatives merely to make a log chart work; document any filtering or transformation.

### 5.4 Tick locators and formatters

A **locator** chooses tick positions; a **formatter** chooses their displayed labels. Avoid manually setting every tick for a long axis unless the data has a small, fixed set of meaningful categories.

```python
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

batches = [0, 1, 2, 3, 4, 5]
rows = [125_000, 250_000, 375_000, 500_000, 625_000, 750_000]
fig, ax = plt.subplots()
ax.plot(batches, rows, marker="o")
ax.xaxis.set_major_locator(MultipleLocator(1))
ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value / 1_000:.0f}k"))
ax.set(xlabel="Batch", ylabel="Rows", title="Rows processed per batch")
fig.savefig("outputs/ticks.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

For large-number labels such as `1.2M`, use a formatter with an explicit unit convention. Do not format away precision needed by the reader. `FuncFormatter` callbacks receive the tick value and tick position; the second parameter is often unused.

### 5.5 Date axes and tick rotation

Matplotlib understands Python `datetime` values. `matplotlib.dates.AutoDateLocator` selects suitable date ticks and `ConciseDateFormatter` avoids repeating the same date components on every label.

```python
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

start = datetime(2026, 10, 1)
times = [start + timedelta(hours=6 * i) for i in range(20)]
durations_s = [42 + (i % 5) * 3 + (8 if 8 <= i <= 10 else 0) for i in range(20)]
fig, ax = plt.subplots(figsize=(8, 3.5), constrained_layout=True)
ax.plot(times, durations_s, marker=".")
locator = mdates.AutoDateLocator()
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
ax.tick_params(axis="x", labelrotation=25)
ax.set(xlabel="Run time", ylabel="Duration (s)", title="Pipeline run duration")
fig.savefig("outputs/date-axis.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

Real systems should normalise timestamps and explicitly decide on the reporting timezone. Naive datetimes do not carry timezone information. Rotating labels can help, but reducing tick density is often better than rotating labels until they overlap.

### 5.6 Annotations and incident highlighting

- `ax.annotate(...)` adds explanatory text and can draw an arrow to a data point.
- `axhline(y=...)` and `axvline(x=...)` mark thresholds or events.
- `axvspan(start, end, ...)` shades an x-range, such as an incident window.

```python
import matplotlib.pyplot as plt

runs = list(range(1, 11))
duration_s = [40, 42, 41, 43, 44, 78, 82, 47, 45, 44]
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.plot(runs, duration_s, marker="o", label="duration")
ax.axhline(60, color="crimson", linestyle="--", label="60 s threshold")
ax.axvspan(5.5, 7.5, color="orange", alpha=0.18, label="incident window (runs 6–7)")
ax.annotate("retry storm", xy=(7, 82), xytext=(7.8, 72), arrowprops={"arrowstyle": "->"})
ax.set(xlabel="Pipeline run", ylabel="Duration (s)", title="Incident-associated duration spike")
ax.legend()
fig.savefig("outputs/incident.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

The shaded span uses the x-axis's data coordinates. If the x-axis is dates, pass datetime boundaries. Make annotation text concise and avoid covering the point being explained.

### 5.7 Colours, colormaps, styles, and property cycles

- Named colours such as `"steelblue"`, `"crimson"`, and `"black"` are readable alternatives to unexplained RGB values.
- A **sequential** colormap (for example, `viridis`) represents low-to-high magnitude.
- A **diverging** colormap (for example, `RdBu_r`) is useful when values have a meaningful centre such as zero.
- A **qualitative** palette (for example, `tab10`) distinguishes categories without implying numeric order.
- Avoid rainbow-like maps when colour order could imply misleading magnitude. Do not rely on colour alone: add markers, line styles, labels, or texture when appropriate.

Styles can be applied locally with `plt.style.context(...)`, avoiding a persistent global style change:

```python
import matplotlib.pyplot as plt
from cycler import cycler

with plt.style.context("seaborn-v0_8-whitegrid"):
    fig, ax = plt.subplots()
    ax.set_prop_cycle(cycler(color=["#0072B2", "#D55E00"]) + cycler(linestyle=["-", "--"]))
    ax.plot([1, 2, 3], [3, 4, 2], label="baseline")
    ax.plot([1, 2, 3], [2, 3, 4], label="new version")
    ax.set(xlabel="Run", ylabel="Duration (s)", title="Version comparison")
    ax.legend()
    fig.savefig("outputs/style-cycle.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
```

The style name above is a Matplotlib 3.9-compatible bundled style name. Available styles can be inspected with `plt.style.available`. `rcParams` controls defaults such as font sizes and save settings; global mutation can leak into later plots, so prefer a scoped `plt.rc_context({...})` or style context for library code.

```python
import matplotlib.pyplot as plt

with plt.rc_context({"font.size": 10, "axes.titlesize": 12, "figure.dpi": 100}):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 2, 5])
    ax.set(title="Scoped defaults", xlabel="Run", ylabel="Value")
    fig.savefig("outputs/rc-context.png", bbox_inches="tight")
    plt.close(fig)
```

### 5.8 Scatter encodings, colourbars, density, and uncertainty

Scatter plots can encode a third numeric variable through colour (`c=`) or size (`s=`). The legend/colourbar must explain the encoding. Size is interpreted as marker area in points squared, so a numeric mapping should be chosen carefully.

```python
import numpy as np
import matplotlib.pyplot as plt

rows = np.array([100, 180, 260, 400, 520])
runtime_s = np.array([2.0, 2.4, 3.1, 4.2, 5.8])
error_count = np.array([0, 1, 2, 4, 7])
fig, ax = plt.subplots()
points = ax.scatter(rows, runtime_s, c=error_count, s=45 + 12 * error_count, cmap="viridis", alpha=0.85)
fig.colorbar(points, ax=ax, label="Error count")
ax.set(xlabel="Rows processed", ylabel="Runtime (s)", title="Runtime and errors by batch")
fig.savefig("outputs/scatter-encoding.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

For a histogram, `density=True` normalises the total area under the histogram to approximately 1 (for the displayed bins); it does **not** make the bar heights sum to 1 in general. This is useful when comparing distributions with different sample sizes.

```python
import numpy as np
import matplotlib.pyplot as plt

latency_ms = np.array([12, 13, 15, 16, 17, 18, 20, 22, 24, 28, 31, 45, 60], dtype=float)
fig, ax = plt.subplots()
ax.hist(latency_ms, bins=7, density=True, alpha=0.8, edgecolor="white")
ax.set(xlabel="Latency (ms)", ylabel="Density (1/ms)", title="Latency density")
fig.savefig("outputs/density.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

Use `fill_between` for a range or uncertainty band. State what the bounds represent; the API itself does not know whether they are percentiles, confidence intervals, measurement ranges, or something else.

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.arange(1, 8)
mean = np.array([40, 42, 41, 45, 46, 48, 47], dtype=float)
low = mean - np.array([3, 4, 2, 3, 3, 5, 4])
high = mean + np.array([4, 3, 4, 5, 4, 4, 3])
fig, ax = plt.subplots()
ax.plot(x, mean, marker="o", label="mean duration")
ax.fill_between(x, low, high, alpha=0.2, label="observed range")
ax.set(xlabel="Day", ylabel="Duration (s)", title="Daily duration with observed range")
ax.legend()
fig.savefig("outputs/range-band.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

### 5.9 Practical figure recipes

These recipes are small reusable patterns. They use only inline data.

#### Recipe A — time series with rolling mean, incident window, and p95

```python
from datetime import datetime, timedelta, timezone
import numpy as np
import matplotlib.pyplot as plt

start = datetime(2026, 10, 1, tzinfo=timezone.utc)
times = [start + timedelta(hours=i) for i in range(24)]
# Deterministic synthetic hourly pipeline durations, in seconds.
durations_s = np.array([42 + (i % 4) * 2 + (15 if 12 <= i <= 14 else 0) for i in range(24)], dtype=float)
window = 3
rolling_mean = np.convolve(durations_s, np.ones(window) / window, mode="valid")
rolling_times = times[window - 1:]
p95 = float(np.percentile(durations_s, 95))

fig, ax = plt.subplots(figsize=(9, 4), constrained_layout=True)
ax.plot(times, durations_s, marker=".", alpha=0.65, label="Hourly duration")
ax.plot(rolling_times, rolling_mean, linewidth=2, label="3-hour rolling mean")
ax.axhline(p95, linestyle="--", color="crimson", label=f"p95 = {p95:.1f} s")
ax.axvspan(times[12], times[15], color="orange", alpha=0.18, label="Incident window")
ax.set(xlabel="Time (UTC)", ylabel="Duration (s)", title="Pipeline duration and incident window")
ax.legend(ncols=2)
fig.savefig("outputs/pipeline-time-series.svg", bbox_inches="tight")
fig.savefig("outputs/pipeline-time-series.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

The timestamps above are timezone-aware synthetic UTC datetimes. The incident samples are at indices 12–14, so the shaded interval ends at `times[15]`, the next hourly boundary; this covers the full three-hour interval. `np.convolve(..., mode="valid")` returns a rolling average only where a full window exists; the timestamps are sliced to align with those values.

#### Recipe B — histogram with percentile markers

```python
import numpy as np
import matplotlib.pyplot as plt

latency_ms = np.array([18, 20, 21, 21, 22, 24, 27, 30, 34, 45, 61, 70, 85], dtype=float)
p50, p95 = np.percentile(latency_ms, [50, 95])
fig, ax = plt.subplots()
ax.hist(latency_ms, bins="auto", edgecolor="white")
ax.axvline(p50, color="black", linestyle="--", label=f"p50 = {p50:.1f} ms")
ax.axvline(p95, color="crimson", linestyle=":", label=f"p95 = {p95:.1f} ms")
ax.set(xlabel="Latency (ms)", ylabel="Request count", title="Latency distribution with percentiles")
ax.legend()
fig.savefig("outputs/percentiles.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

#### Recipe C — sorted, labelled horizontal bar chart

```python
import matplotlib.pyplot as plt

stage_seconds = {"Extract source": 4.2, "Validate schema": 1.7, "Transform rows": 6.3, "Write output": 2.9}
ordered = sorted(stage_seconds.items(), key=lambda item: item[1])
labels = [item[0] for item in ordered]
values = [item[1] for item in ordered]
fig, ax = plt.subplots(figsize=(7, 3.5), constrained_layout=True)
bars = ax.barh(labels, values, color="steelblue")
ax.bar_label(bars, fmt="%.1f s", padding=3)
ax.set(xlabel="Duration (s)", title="Pipeline stage duration (sorted)", xlim=(0, max(values) * 1.2))
fig.savefig("outputs/sorted-stages.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

#### Recipe D — annotated heatmap

```python
import numpy as np
import matplotlib.pyplot as plt

matrix = np.array([[0.2, 0.1, 0.0], [0.4, 0.3, 0.1], [0.8, 0.6, 0.2]])
rows = ["Extract", "Validate", "Transform"]
columns = ["Mon", "Tue", "Wed"]
fig, ax = plt.subplots()
image = ax.imshow(matrix, cmap="viridis", vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(len(columns)), labels=columns)
ax.set_yticks(range(len(rows)), labels=rows)
for row in range(matrix.shape[0]):
    for col in range(matrix.shape[1]):
        ax.text(col, row, f"{matrix[row, col]:.1f}", ha="center", va="center", color="white" if matrix[row, col] < 0.55 else "black")
fig.colorbar(image, ax=ax, label="Null rate (fraction)")
ax.set(title="Null rate by stage and day")
fig.savefig("outputs/annotated-heatmap.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

Fix `vmin`/`vmax` across comparable heatmaps so the same colour means the same value. A colourbar and cell labels provide complementary interpretation; for large matrices, label only useful cells or use a different presentation.

#### Recipe E — small multiples

```python
import matplotlib.pyplot as plt

series = {
    "Extract": [4, 5, 4, 6, 5],
    "Validate": [2, 2, 3, 2, 2],
    "Transform": [6, 7, 8, 7, 6],
}
fig, axes = plt.subplots(3, 1, figsize=(7, 6), sharex=True, constrained_layout=True)
for ax, (name, values) in zip(axes, series.items()):
    ax.plot(range(1, len(values) + 1), values, marker="o")
    ax.set_ylabel("Seconds")
    ax.set_title(name, loc="left")
axes[-1].set_xlabel("Pipeline run")
fig.suptitle("Stage durations across runs")
fig.savefig("outputs/small-multiples.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

Small multiples often make comparisons clearer than a single overloaded chart. If values should be compared directly, share axes; if magnitudes differ dramatically, explain any decision not to share them.

## 6. Backends and headless rendering

A **backend** connects Matplotlib's plotting model to an output/rendering environment. Interactive GUI backends support windows and interaction; notebook backends render output in notebook cells; non-interactive backends render files without opening a window.

- In classic notebook workflows, `%matplotlib inline` renders static output. `%matplotlib widget` provides interactive figures when the compatible `ipympl` package is installed. These are IPython magics, not Python statements; run them in a notebook cell only.
- On servers and in CI, `Agg` is a non-interactive raster backend suitable for PNG rendering. Select it before importing `matplotlib.pyplot` and before another backend has been initialised.

```python
import matplotlib
matplotlib.use("Agg")  # Must be before importing pyplot.
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [3, 2, 4])
ax.set(title="Headless render", xlabel="Index", ylabel="Value")
fig.savefig("outputs/headless.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

If a GUI or notebook environment has already imported/initialised a backend, changing it late may fail or be unsafe. Do not force `Agg` in a library that users may run interactively; make backend choice an application/entry-point decision.

## 7. Advanced: Artists, coordinate transforms, and draw order

### 7.1 Artist objects

`ax.plot` creates and returns `Line2D` Artists; `ax.text` creates a `Text`; `ax.bar` creates a `BarContainer` containing rectangle patches; `ax.imshow` creates an image Artist. You can inspect or update returned objects instead of recreating the whole figure.

```python
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text

fig, ax = plt.subplots()
line = Line2D([0, 1, 2], [1, 3, 2], color="steelblue", label="line")
ax.add_line(line)
patch = Rectangle((0.2, 0.2), 0.2, 0.25, transform=ax.transAxes, facecolor="orange", alpha=0.5)
ax.add_patch(patch)
note = Text(0.02, 0.95, "Axes-relative note", transform=ax.transAxes, va="top")
ax.add_artist(note)
ax.set(xlim=(0, 2), ylim=(0, 4), xlabel="X", ylabel="Y", title="Direct Artist construction")
fig.savefig("outputs/artists.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

`Line2D` and `Rectangle` can be constructed directly and attached with `add_line`/`add_patch`. For most ordinary charts, `ax.plot`/`ax.bar` are clearer; direct construction is useful for custom components or detailed Artist control.

### 7.2 Coordinate systems and transforms

- **Data coordinates:** values in the plot's data domain; e.g. `(run_number, duration_s)`.
- **Axes coordinates:** normalised coordinates relative to one Axes, usually `(0, 0)` bottom-left and `(1, 1)` top-right, independent of data limits.
- **Figure coordinates:** normalised coordinates across the full Figure.
- **Display coordinates:** rendered pixel/display coordinates, generally not appropriate to hard-code because output size and DPI can change.

`transform=ax.transAxes` is useful for a note anchored to a panel corner regardless of data limits. Default text and most plotting methods use data coordinates unless documented otherwise. `fig.transFigure` expresses figure-relative placement. `ax.transData` maps data coordinates to display space.

### 7.3 Z-order and clipping

Artists with higher `zorder` are generally drawn above those with lower values. Use this to keep a threshold line or annotation visible. Clipping constrains an Artist to a region (commonly the Axes patch). For example, `ax.text(1.02, 0.5, "outside", transform=ax.transAxes, clip_on=False)` places text just beyond the right edge of an Axes; reserve figure margin for it and inspect the export because `clip_on=False` can still overlap neighbouring content or be cropped by the Figure boundary.

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [2, 4, 3], linewidth=3, zorder=2)
ax.axhline(3, color="crimson", linestyle="--", zorder=3)
ax.text(0.02, 0.96, "threshold = 3", transform=ax.transAxes, va="top", zorder=4)
ax.text(1.02, 0.5, "outside Axes", transform=ax.transAxes, clip_on=False, va="center")
ax.set(xlabel="Run", ylabel="Metric", title="Draw order")
fig.subplots_adjust(right=0.78)  # Leave room for the unclipped annotation.
fig.savefig("outputs/zorder.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

## 8. Large-data performance and animation

Rendering is not free. Ten million opaque vector markers can produce huge output files, long render times, and an unreadable dark mass. Optimise the visual representation before micro-optimising Python.

1. **Aggregate** when the question concerns counts, rates, or summaries rather than individual observations.
2. **Downsample** deterministically when displaying a representative subset; record the sampling rule and seed.
3. **Use `hexbin`** or 2-D histograms to show point density without drawing every point separately.
4. **Use alpha** to reveal overlap, while recognising that transparency does not fix every overplotting problem.
5. **Rasterize dense layers** in a PDF/SVG while keeping labels and axes vector-based.
6. **Use `LineCollection`** for many independent line segments; it can reduce per-object overhead compared with creating many separate line Artists.
7. For very large interactive exploration, know that **Datashader** aggregates data into a pixel grid; it is a separate library and is not required here.

Example: hexbin and a rasterized scatter layer.

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)
x = rng.normal(size=30_000)
y = 0.6 * x + rng.normal(scale=0.8, size=30_000)
fig, axes = plt.subplots(1, 2, figsize=(9, 3.5), constrained_layout=True)
axes[0].scatter(x, y, s=4, alpha=0.12, rasterized=True)
axes[0].set(title="Sampled marks with transparency", xlabel="x", ylabel="y")
hexes = axes[1].hexbin(x, y, gridsize=35, mincnt=1, cmap="viridis")
axes[1].set(title="Hexagonal aggregation", xlabel="x", ylabel="y")
fig.colorbar(hexes, ax=axes[1], label="Points per hexagon")
fig.savefig("outputs/dense-data.pdf", bbox_inches="tight")
plt.close(fig)
```

`rasterized=True` is particularly useful for dense layers in vector output. It does not magically reduce the cost of generating all data points in the first place. If the source data is huge, aggregate or sample before constructing Artists.

A `LineCollection` is useful when many line segments share styling and should be managed as one collection rather than as thousands of separate `Line2D` objects:

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

x = np.linspace(0, 10, 250)
y = np.sin(x) + 0.08 * np.cos(7 * x)
points = np.column_stack((x, y))
segments = np.stack((points[:-1], points[1:]), axis=1)

fig, ax = plt.subplots()
collection = LineCollection(segments, colors="steelblue", linewidths=1.4, alpha=0.9)
ax.add_collection(collection)
ax.autoscale_view()
ax.set(xlabel="Time (s)", ylabel="Signal (unitless)", title="Signal drawn with LineCollection")
fig.savefig("outputs/line-collection.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

The segment array has shape `(number_of_segments, 2, 2)`: each segment contains two `(x, y)` points. Because the collection is added as one Artist, call `ax.autoscale_view()` after adding it (or set explicit limits) so the view reflects its data. `LineCollection` is a performance-oriented representation, not a substitute for aggregation when individual segments are not analytically necessary.

### 8.1 Animation and blitting

`matplotlib.animation.FuncAnimation` repeatedly updates Artists. Blitting redraws only changed regions and can improve interactive animation performance, but backend support and animated Artist configuration matter. Animation is useful for temporal evolution, but static small multiples are often easier to compare, inspect, export, and test.

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

x = np.linspace(0, 2 * np.pi, 200)
fig, ax = plt.subplots()
(line,) = ax.plot(x, np.sin(x))
ax.set(xlim=(0, 2 * np.pi), ylim=(-1.1, 1.1), xlabel="x", ylabel="Amplitude", title="Sine wave animation")

def update(frame: int):
    line.set_ydata(np.sin(x + frame / 10))
    return (line,)

animation = FuncAnimation(fig, update, frames=60, interval=40, blit=True)
# Optional export: install Pillow for GIF or ffmpeg for MP4, then uncomment one:
# animation.save("outputs/sine.gif", writer="pillow", fps=25)
# animation.save("outputs/sine.mp4", writer="ffmpeg", fps=25)
# Keep `animation` referenced until display/export is complete to prevent collection.
plt.close(fig)  # This example builds but does not display or export the animation.
```

This snippet constructs an animation but does not export it by default. For a notebook display, keep the animation object alive and display it with the notebook's supported HTML representation; for a file, uncomment an export line after installing the relevant writer. `ffmpeg` is an external executable, not merely a Python import. In an interactive workflow, close the Figure only after display/export is complete. For a static comparison, prefer small multiples when the main task is to compare several time points rather than watch motion.

## 9. Reusable helpers and a small plotting library

A reusable helper should accept an explicit `ax`, avoid relying on the current pyplot axes, validate its input assumptions, document units, and return useful Artists or results. If `ax=None` is supported, it may create a Figure/Axes for convenience, but the caller must know who owns and closes that Figure.

### 9.1 A helper that returns its Artist

```python
from collections.abc import Sequence
from typing import Any
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.container import BarContainer


def plot_stage_durations(
    labels: Sequence[str],
    seconds: Sequence[float],
    *,
    ax: Axes,
    **bar_kwargs: Any,
) -> BarContainer:
    """Draw pipeline stage durations on `ax` and return the bar container.

    Args:
        labels: Stage names, one per duration.
        seconds: Non-negative durations measured in seconds.
        ax: Axes owned by the calling code.
        **bar_kwargs: Additional keyword arguments passed to `Axes.barh`.

    Returns:
        The BarContainer, useful for adding labels or inspecting bar patches.
    """
    if len(labels) != len(seconds):
        raise ValueError("labels and seconds must have the same length")
    if any(value < 0 for value in seconds):
        raise ValueError("durations must be non-negative")
    bars = ax.barh(labels, seconds, **bar_kwargs)
    ax.set(xlabel="Duration (s)", title="Pipeline stage durations")
    return bars


fig, ax = plt.subplots(figsize=(7, 3))
bars = plot_stage_durations(["Extract", "Transform"], [4.2, 6.3], ax=ax, color="steelblue")
ax.bar_label(bars, fmt="%.1f s", padding=3)
fig.savefig("outputs/helper.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

The helper does not create a Figure, save files, close figures, or mutate global styles. Those are caller responsibilities. This separation lets it work inside a dashboard panel, a notebook, a report, or a test.

### 9.2 Testing Artist data and smoke-testing creation

Create `plotkit.py`:

```python
from collections.abc import Sequence
from matplotlib.axes import Axes
from matplotlib.container import BarContainer


def plot_stage_durations(labels: Sequence[str], seconds: Sequence[float], *, ax: Axes) -> BarContainer:
    """Plot stage durations in seconds and return the created bars."""
    if len(labels) != len(seconds):
        raise ValueError("labels and seconds must have the same length")
    if any(value < 0 for value in seconds):
        raise ValueError("durations must be non-negative")
    bars = ax.barh(labels, seconds)
    ax.set(xlabel="Duration (s)", title="Pipeline stage durations")
    return bars
```

Create `test_plotkit.py`:

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from plotkit import plot_stage_durations


def test_stage_duration_bars_and_labels():
    fig, ax = plt.subplots()
    try:
        bars = plot_stage_durations(["Extract", "Transform"], [4.2, 6.3], ax=ax)
        assert len(bars.patches) == 2
        assert [patch.get_width() for patch in bars.patches] == pytest.approx([4.2, 6.3])
        assert ax.get_xlabel() == "Duration (s)"
        assert ax.get_title() == "Pipeline stage durations"
    finally:
        plt.close(fig)


def test_mismatched_input_is_rejected():
    fig, ax = plt.subplots()
    try:
        with pytest.raises(ValueError, match="same length"):
            plot_stage_durations(["Extract"], [1.0, 2.0], ax=ax)
    finally:
        plt.close(fig)
```

Run with `uv run pytest -q`. The tests inspect semantic properties (bar count, bar values, labels) and verify figure creation. The `try/finally` guarantees cleanup even if an assertion fails. This is generally more robust than testing the exact internal order of unrelated Artists.

### 9.3 Image-comparison and golden-image tests

Artist assertions verify data and structure but cannot detect every visual regression (overlapping labels, clipped legends, unexpected font changes). Image-comparison tools such as `pytest-mpl` can compare a rendered figure against a baseline image with a tolerance. Golden images are sensitive to Matplotlib version, fonts, backend, and operating system; pin the rendering environment where possible and choose tolerances based on acceptable differences rather than requiring bit-for-bit identity everywhere.

Use both layers:

- **Semantic tests:** assert data, labels, limits, and Artist properties.
- **Smoke tests:** build and render the figure without raising.
- **Image regression tests:** compare rendered output with a reviewed baseline and an explicit tolerance.

A failing image test is a review signal, not automatic proof that the new image is wrong; inspect the diff.

## 10. Server-side plotting, cleanup, and concurrency

`pyplot` maintains global registries of figures and current-axes state. In a long-running batch process, repeatedly creating figures without closing them can retain managers and memory. Always close figures created by batch tasks after saving or display is complete. Avoid caching entire Figure objects indefinitely unless that is a deliberate, bounded design.

Matplotlib is not generally thread-safe. Do not assume independent `pyplot` calls can safely render concurrently in arbitrary threads. Prefer serial rendering, process isolation, or a carefully controlled rendering service. If a service needs direct OO construction without pyplot's global figure manager, use `Figure` and `FigureCanvasAgg`:

```python
from pathlib import Path
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure


def render_metric_png(output: Path) -> None:
    """Render a small metric figure without pyplot's global figure registry."""
    fig = Figure(figsize=(6, 3.5), dpi=160)
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    ax.plot([1, 2, 3], [10, 12, 11], marker="o")
    ax.set(title="Metric snapshot", xlabel="Run", ylabel="Value")
    fig.savefig(output, bbox_inches="tight")


render_metric_png(Path("outputs/server-metric.png"))
```

This direct Figure/Canvas approach avoids pyplot's global manager, but does **not** make every Matplotlib component thread-safe or remove the need to manage memory. Review backend, font/cache behaviour, and concurrency strategy in the context of the service. `FigureCanvasAgg` is a non-interactive raster canvas.

## 11. Export: vector/raster, size, DPI, fonts, and reproducibility

- **PNG:** raster pixels; broadly supported for web, notebooks, and reports. Pixel dimensions are approximately figure inches × DPI (tight bounding boxes can adjust them).
- **SVG:** vector geometry and text; useful for web and scalable diagrams. Some embedded raster layers remain raster.
- **PDF:** vector-friendly report/paper format; can include raster images for dense layers.
- **DPI:** affects raster outputs and rasterized layers in vector formats. A 6×3 inch Figure at 200 DPI is nominally 1200×600 pixels before tight-bbox adjustments.
- **Figure size:** specify dimensions in inches to target report-column or slide sizes. Increasing DPI is not a fix for bad layout or tiny text.
- **Fonts:** font availability changes glyph metrics and layout. For portable outputs, use widely available fonts and verify embedded-font behaviour for the target format/viewer. Matplotlib PDF/SVG font settings can be configured through `rcParams`; for example, `pdf.fonttype=42` and `ps.fonttype=42` request TrueType embedding in relevant vector outputs where supported. SVG has its own text/font options.
- **Colour:** RGB/alpha behaviour varies by viewer and output pipeline; confirm contrast and printing needs. Matplotlib is not a full colour-management workflow.
- **Reproducibility:** pin Matplotlib/NumPy and fonts where visual regression matters; fix random seeds; use stable data ordering and explicit labels/limits; record the dataset version and export parameters.

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.5, 3.2), constrained_layout=True)
ax.plot([1, 2, 3], [2.2, 2.5, 2.1], marker="o")
ax.set(title="Report-ready metric", xlabel="Run number", ylabel="Duration (s)")
fig.savefig("outputs/report.png", dpi=220, bbox_inches="tight")
fig.savefig("outputs/report.svg", bbox_inches="tight")
fig.savefig("outputs/report.pdf", bbox_inches="tight")
plt.close(fig)
```

Do not assume PNG and SVG have identical text metrics or that every downstream application renders SVG identically. Inspect the actual artifact at its intended display size.

## 12. A small reusable plotting library: `plotkit`

A tiny library can standardise style and remove duplicated plotting logic. Keep the public API small, document units and expected inputs, and keep I/O separate from drawing.

A sensible first design:

```text
plotkit/
├── __init__.py
├── style.py          # apply_style(ax or scoped defaults; no hidden global mutation)
├── time_series.py    # time_series(..., ax=...) -> line/band Artists
├── distribution.py   # distribution(..., ax=...) -> histogram/percentile Artists
└── heatmap.py        # heatmap(..., ax=...) -> image Artist and optional colorbar
```

The helper in Section 9 is the initial `plotkit` pattern. Add functions only when a repeated use case exists. Each helper should accept an `ax` (or have an explicit, documented creation mode), return the created Artist(s) or a structured result, validate shape/length assumptions, use type hints and docstrings, and avoid calling `plt.gca()`, changing global `rcParams`, saving files, or closing caller-owned figures. Put shared style choices in one module and test each public helper with semantic assertions plus selected image-regression tests.

## 13. End-to-end example: pipeline reliability report

This example combines deterministic synthetic data, time-series analysis, annotations, a distribution, a sorted bar chart, and SVG/PNG export. It requires no external file or network. Save as `pipeline_report.py` and run it after creating `outputs/`.

```python
from datetime import datetime, timedelta, timezone
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 36 hourly pipeline runs. Synthetic but deterministic; no network access.
rng = np.random.default_rng(2026)
start = datetime(2026, 10, 1, tzinfo=timezone.utc)
timestamps = [start + timedelta(hours=i) for i in range(36)]
duration_s = 40 + rng.normal(0, 3, size=36)
duration_s[18:21] += 24  # a simulated incident window
row_counts = 100_000 + np.arange(36) * 1_250
stage_seconds = {"Extract": 18.2, "Validate": 6.4, "Transform": 25.1, "Write": 10.3}

window = 3
rolling_mean = np.convolve(duration_s, np.ones(window) / window, mode="valid")
rolling_times = timestamps[window - 1:]
p95 = float(np.percentile(duration_s, 95))

fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
ax_time, ax_hist, ax_stages, ax_rows = axes.ravel()

# 1. Trend, rolling mean, p95 and incident shading.
ax_time.plot(timestamps, duration_s, marker=".", alpha=0.65, label="Hourly duration")
ax_time.plot(rolling_times, rolling_mean, linewidth=2, label="3-hour rolling mean")
ax_time.axhline(p95, color="crimson", linestyle="--", label=f"p95 = {p95:.1f} s")
ax_time.axvspan(timestamps[18], timestamps[21], color="orange", alpha=0.18, label="Incident window")
ax_time.set(title="Pipeline duration", ylabel="Seconds")
ax_time.legend(fontsize=8)

# 2. Distribution and percentile marker.
ax_hist.hist(duration_s, bins="auto", edgecolor="white")
ax_hist.axvline(p95, color="crimson", linestyle="--", label=f"p95 = {p95:.1f} s")
ax_hist.set(title="Run-duration distribution", xlabel="Duration (s)", ylabel="Run count")
ax_hist.legend(fontsize=8)

# 3. Sorted stage durations.
ordered_stages = sorted(stage_seconds.items(), key=lambda item: item[1])
stage_labels = [item[0] for item in ordered_stages]
stage_values = [item[1] for item in ordered_stages]
bars = ax_stages.barh(stage_labels, stage_values, color="steelblue")
ax_stages.bar_label(bars, fmt="%.1f s", padding=3)
ax_stages.set(title="Stage durations", xlabel="Seconds", xlim=(0, max(stage_values) * 1.25))

# 4. Row counts on the same time index.
ax_rows.plot(timestamps, row_counts, color="darkgreen", marker=".")
ax_rows.set(title="Rows processed", xlabel="Time (UTC)", ylabel="Rows")

for ax in (ax_time, ax_rows):
    ax.tick_params(axis="x", labelrotation=20)

fig.suptitle("Pipeline reliability snapshot — synthetic data")
fig.savefig(OUTPUT_DIR / "pipeline-reliability.png", dpi=200, bbox_inches="tight")
fig.savefig(OUTPUT_DIR / "pipeline-reliability.svg", bbox_inches="tight")
plt.close(fig)

print(f"Runs: {len(duration_s)}")
print(f"p95 duration: {p95:.2f} s")
print(f"Saved figures in: {OUTPUT_DIR.resolve()}")
```

### Expected observations

- The time-series panel shows an obvious spike during the simulated incident, with the rolling mean smoothing short-term variation. The shaded interval runs from timestamp 18 to timestamp 21, covering the three hourly samples at indices 18–20 through the next-hour boundary.
- The dashed horizontal line marks the p95 across the 36 run durations; it is a threshold summary, not a causal explanation.
- The histogram shows the distribution and tail; bin choices affect its appearance, so inspect them rather than treating one histogram as uniquely correct.
- The stage chart is sorted from shortest to longest and labelled with units.
- Row counts rise steadily because the synthetic input was constructed that way; this is not evidence that a real pipeline is healthy.
- Both PNG and SVG are written. The script prints the computed p95 and output directory.

The code intentionally creates a single Figure and closes it after both exports. For real operational reporting, include missing runs explicitly, document the aggregation window and timezone, and avoid connecting across data gaps as though measurements existed.

## 14. Troubleshooting and common mistakes

### Mistake 1 — mixing pyplot state with OO calls

**Symptom:** a line or title appears in the wrong panel, especially inside a loop.

**Cause:** `plt.plot(...)` targets whichever Axes is current, while the code assumes it targets a particular `ax` variable.

**Fragile pattern:**

```python
# Illustrative anti-pattern: do not use in reusable multi-axes code.
for ax in axes:
    plt.plot(x, y)  # Uses current pyplot Axes, not necessarily this loop's `ax`.
```

**Correction:** call `ax.plot(x, y)` and `ax.set_title(...)` on the loop variable. Reserve `plt` for top-level setup/close and deliberate interactive operations.

### Mistake 2 — plotting on the wrong Axes

**Symptom:** one panel is empty and another has duplicate lines, or annotations refer to the wrong data.

**Diagnosis:** inspect the object returned by `plt.subplots`, check loop unpacking and whether `axes` is a scalar or array, and confirm every plotting call uses the intended Axes reference.

**Correction:** use meaningful names (`ax_latency`, `ax_cost`) or a mosaic dictionary (`axd["latency"]`). For code that should always receive an array, use `squeeze=False`. Avoid assuming `plt.subplot(...)` silently changes the target you expect.

### Mistake 3 — failing to close figures in batch jobs

**Symptom:** memory use grows across hundreds or thousands of generated plots, or Matplotlib warns that many figures are open.

**Cause:** pyplot retains references to managed figures until they are closed. A loop can accumulate many figures even after saving.

**Correction:** close each figure after saving or displaying it. Use `try/finally` when errors could occur between creation and cleanup. Do not close a figure before an interactive display or animation export that still needs it.

```python
from pathlib import Path
import matplotlib.pyplot as plt

output_dir = Path("outputs/batch")
output_dir.mkdir(parents=True, exist_ok=True)
for index, value in enumerate([3, 1, 4, 2]):
    fig, ax = plt.subplots()
    try:
        ax.bar(["metric"], [value])
        ax.set(title=f"Batch item {index}", ylabel="Value")
        fig.savefig(output_dir / f"item-{index}.png", dpi=120)
    finally:
        plt.close(fig)
```

### Mistake 4 — opaque overplotting

**Symptom:** dense scatter points form a solid block and hide density structure.

**Cause:** too many opaque marks occupy the same pixels. Raising DPI alone will not reveal the distribution reliably.

**Correction:** use alpha, smaller markers, deterministic sampling, aggregation, `hexbin`, a 2-D histogram, or Datashader when appropriate. State whether the plot shows all observations or a sample. Do not use a sample if rare events are the core question unless the sampling design preserves them.

### Additional quick checks

- **`ValueError` on log scale:** inspect for zero/negative values and document any transform/filter; use symlog if signed values are meaningful.
- **Clipped labels:** try `constrained_layout=True`, `bbox_inches="tight"`, a larger Figure, fewer ticks, or shorter labels. Tight export is not a substitute for sensible layout.
- **Unreadable heatmap:** check colourbar, sequential/diverging palette choice, fixed limits across comparable panels, and annotation contrast.
- **Different-looking golden image:** compare versions, fonts, backend, figure size, DPI, and data ordering before assuming the plot logic changed.
- **Animation not saved:** check whether Pillow or the `ffmpeg` executable is installed and whether the selected writer is available.

## 15. Production, accessibility, and communication checklist

- **Honesty:** label units, identify transformations and scales, show meaningful baselines, and avoid axis choices that exaggerate changes.
- **Accessibility:** use readable text sizes and sufficient contrast; choose colourblind-aware palettes; don't encode the only distinction in colour; check grayscale legibility and provide a caption or alt text when figures are published.
- **Data hygiene:** aggregate or redact PII before export; chart labels, annotations, and embedded images can disclose identifiers. Synthetic data is suitable for examples and tests.
- **Reproducibility:** deterministic seeds, stable ordering, pinned dependencies/fonts where needed, explicit timezone and data version, and tested export paths.
- **Ownership:** caller owns Figures created by helpers; batch code closes them. Helpers should not mutate global `rcParams` or the current pyplot Axes.
- **Performance:** measure rendering and output size; aggregate before plotting at scale; rasterize dense layers in vector documents.
- **Export review:** inspect PNG/SVG/PDF at the actual destination size and in the target viewer. DPI does not fix clutter, misleading scales, or poor annotations.

## 16. Hands-on exercises

Save finished figures in a `gallery/` folder and write a one-sentence takeaway for each, following the module roadmap.

### Exercise 1 — inspect the object model

**Task:** create a Figure with two Axes; draw one line and one text annotation. Print the line's x/y data and inspect `ax.lines`, `ax.texts`, `fig.axes`, `ax.xaxis`, and `ax.yaxis`.

**Acceptance criteria:** explain which objects represent the canvas, plotting area, dimensional tick machinery, and drawable elements; no reliance on the current pyplot Axes for plotting.

### Exercise 2 — multiple panels and scales

**Task:** use `plt.subplots` with shared x-axis and `constrained_layout=True` to compare pipeline duration and row count. Include one linear panel and one log-scale panel only if the values and question justify it.

**Acceptance criteria:** units and scales are labelled; panels do not have overlapping titles/ticks; any log transform is explained; the figure is saved and closed.

### Exercise 3 — distribution and percentiles

**Task:** plot a latency histogram with p50 and p95 lines. Try both count and `density=True` variants.

**Acceptance criteria:** percentile lines are calculated from the same data and plotted in the same coordinate units as the histogram; the y-axis label changes appropriately between count and density; bins are stated or chosen intentionally.

### Exercise 4 — annotated heatmap

**Task:** construct a 3×4 synthetic null-rate matrix, label rows and columns, annotate cells, and add a colourbar.

**Acceptance criteria:** fixed `vmin`/`vmax` between 0 and 1; text is legible; the colourbar explains that values are fractions or percentages; colour is not the only source of exact values.

### Exercise 5 — reusable helper and tests

**Task:** write `plotkit.distribution(data, *, ax, bins=...)` that returns the histogram result and rejects empty input. Add tests for bin counts, labels, and invalid data.

**Acceptance criteria:** type hints and docstring; no global pyplot plotting inside the helper; caller owns save/close; tests assert Artist/data properties and always clean up figures.

### Exercise 6 — performance review

**Task:** compare a 30,000-point scatter with a hexbin view. Save one PNG and one PDF with the dense layer rasterized.

**Acceptance criteria:** describe legibility, render/file-size trade-offs, and whether individual points or density is the correct visual answer. Do not claim a speed improvement without measuring it.

### Exercise 7 — end-to-end reliability figure

**Task:** adapt Section 13 to add a clearly labelled incident, a p95 line, a rolling mean, and both SVG and PNG export.

**Acceptance criteria:** deterministic data; correct timestamp alignment for the rolling mean; meaningful units; saved files; figure cleanup; one-sentence takeaway; no external data or network dependency.

## 17. Self-check and answer key

Answer the questions before reading the solutions.

### Questions

1. What is the difference between a `Figure`, an `Axes`, and an `Axis`?
2. Why is `fig, ax = plt.subplots()` preferred in functions you reuse?
3. Plot a pipeline-run duration time series with a rolling mean, an incident shaded region and a p95 line; export as SVG and PNG.

### Solutions

**1. Figure, Axes, Axis.** A `Figure` is the whole canvas. An `Axes` is a plotting area with its own data limits, coordinate system, labels, and plotted Artists. An `Axis` is the x- or y-dimension object managing scale, ticks, tick labels, and units. Artists are drawable objects such as lines, text, patches, images, and collections. The conceptual hierarchy is helpful, but not every Artist is literally owned by an Axis; many are contained directly by an Axes or Figure.

**2. Why the OO API?** It makes the target explicit, avoids depending on pyplot's mutable current-Axes state, supports composition into caller-created panels, and makes reusable functions easier to test. The caller can control layout, saving, and cleanup. A helper that receives `ax` can be combined with other plots without creating an unexpected Figure.

**3. Example implementation.** Run the complete code in Section 5.9, Recipe A. It creates deterministic hourly data, computes a three-observation rolling mean and p95, shades the incident interval, and saves `outputs/pipeline-time-series.svg` and `outputs/pipeline-time-series.png`. The time array is sliced to match the rolling mean's `valid` output; the p95 is drawn in seconds on the same y-axis; and the Figure is closed after both exports. For production timestamps, make timezone handling explicit.

## 18. Lesson summary

- A Figure is the page; an Axes is a plotting area; Axis objects manage each dimension; Artists are the drawable elements.
- Use `fig, ax = plt.subplots()` and call methods on explicit Axes references for reusable, multi-panel, and production code.
- Treat scales, units, tick formatting, colours, annotations, and legends as part of the data's interpretation—not decoration.
- Close pyplot-managed Figures after batch rendering. Use headless `Agg` where appropriate, and avoid assuming Matplotlib is thread-safe.
- For dense data, aggregate or downsample before rendering; use hexbin, rasterization, or specialised tools when the analytical question calls for them.
- Test both semantic Artist properties and rendered appearance. Pin versions and inspect output artifacts when reproducibility matters.

### Completion checklist

- [ ] I can explain `Figure`, `Axes`, `Axis`, and `Artist` without conflating their responsibilities.
- [ ] I can build and label all six core plot types on an explicit Axes.
- [ ] I can create shared-axis panels, a mosaic, annotations, date axes, and formatted ticks.
- [ ] I can choose appropriate scales, palettes, density encodings, and range bands.
- [ ] I can export PNG and SVG, explain DPI/figure-size trade-offs, and close figures safely.
- [ ] I can write and test an `ax`-accepting plotting helper.
- [ ] I can diagnose wrong-Axes bugs, figure leaks, and overplotting.
- [ ] I completed the pipeline reliability example and saved a labelled figure plus a one-sentence takeaway in `gallery/`.
