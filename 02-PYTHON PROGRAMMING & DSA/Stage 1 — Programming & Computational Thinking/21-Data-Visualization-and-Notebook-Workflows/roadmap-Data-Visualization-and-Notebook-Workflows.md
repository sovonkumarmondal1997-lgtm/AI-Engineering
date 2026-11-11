# Roadmap — Module 1.21: Data Visualization and Notebook Workflows

This is the learning roadmap for the twenty-first module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
about plotting, communicating with charts and working in notebooks, **in what
order**, **how** to practise each topic, and **how to prove to yourself**
that you have learned it.

Data engineers and AI engineers look at data constantly: data-quality
profiles, pipeline run durations, drift, class balance, learning curves,
confusion matrices, latency histograms, evaluation results, cost over time.
A chart is often the fastest way to see that a pipeline silently dropped 30 %
of rows, a model overfits, or a prompt change moved a metric. Notebooks are
the dominant medium for that exploration — and, used carelessly, the source
of irreproducible results, hidden state and leaked secrets.

This module teaches enough Matplotlib, Seaborn and Plotly to explore and
communicate honestly, plus disciplined, reproducible notebook workflows.
It deliberately **stops short of** statistics for experiments (Stage 4),
dashboards and BI tools (Stage 2 serving, Stage 14 observability), and
heavy ML-specific plotting (Stages 5–6), which will reuse these skills.

> Target: **Python 3.12+**, Matplotlib 3.9+, Seaborn 0.13+, Plotly 5/6, JupyterLab 4, `pandas`/`polars` (Stage 2) for data frames.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain Matplotlib's object model (Figure, Axes, Artist) and use the **object-oriented API** fluently.
- Choose an appropriate chart type for a question and avoid misleading designs.
- Build statistical plots with Seaborn and interactive plots with Plotly.
- Style plots consistently (colour, accessibility, typography, annotations) and export publication-quality figures.
- Work in Jupyter notebooks productively **and** reproducibly: ordered execution, parameterisation, clean outputs, version control.
- Refactor notebook code into tested modules; run notebooks in CI with `papermill`/`nbconvert`/`jupytext`.
- Create figures for reports and lightweight dashboards, and publish them safely (no secrets, no PII).

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Python functions, modules, tests | Modules 1.3, 1.6, 1.7 | Notebook code gets refactored into modules |
| Lists, dicts, comprehensions | Modules 1.2, 1.4 | Preparing data for plots |
| Files, CSV, JSON, `pathlib` | Module 1.5 | Loading and saving data and figures |
| Project layout, `uv`, `pyproject.toml` | Module 1.6 | Reproducible environments for notebooks |
| Reproducibility, config, secrets hygiene | Modules 1.10, 1.22 (preview), Stage 0 | Notebook hygiene |
| Packaging, entry points | Module 1.18 | Packaging shared plotting helpers |
| Stage 2 data stack (NumPy, pandas, Polars) | `Python for Data Engineering_1` modules 02–04 | Plot data comes from DataFrames |

**Note on order:** Matplotlib and notebooks need only basic Python. For lessons 02–06 it helps (but is not required)
to have started pandas; every example ships with a tiny inline dataset so you can work without it, then redo
the exercises on pandas data when you reach Stage 2.

**Tools:** `uv add matplotlib seaborn plotly pandas numpy jupyterlab ipywidgets`;
`uv add --dev papermill nbstripout nbconvert jupytext nbqa nbmake`; a browser; optional `kaleido` (static export of Plotly).

---

## 3. How the module is organised

```text
Phase A — Plot Mechanics and Chart Choice        (Basics)
  01 Matplotlib figure and axes model
  02 choosing the right chart
Phase B — Higher-Level Libraries                 (Intermediate)
  03 Seaborn and Plotly
Phase C — Notebook Craft                         (Intermediate → Advanced)
  04 Jupyter notebook workflows
  05 reproducible notebooks with papermill and nbstripout
Phase D — Communication                          (Advanced)
  06 figures for reports and dashboards
```

Pace: about 2 weeks part-time. Keep a `gallery/` folder where every exercise
produces one finished, well-labelled figure plus a one-sentence takeaway.

---

## Lesson 01 — `01-matplotlib-figure-and-axes-model.md`

**Why it matters.** Matplotlib is the foundation of Python plotting
(Seaborn, pandas `.plot`, many ML libraries sit on top of it). People who
only know `plt.plot(...)` hit a wall as soon as they need subplots, shared
axes or precise control. The object-oriented model removes the mystery.

### Basic — what to learn

- Two interfaces: **pyplot state machine** (`plt.plot`) vs **object-oriented** (`fig, ax = plt.subplots()`); prefer OO for anything beyond a throw-away plot.
- The hierarchy: `Figure` → `Axes` (one plot area) → `Axis` (x/y) → `Artist` (lines, text, patches).
- Basic plots on an `Axes`: `plot`, `scatter`, `bar`/`barh`, `hist`, `boxplot`, `imshow`.
- Labels and titles: `ax.set_xlabel`, `set_ylabel`, `set_title`, `legend`, `grid`; units in labels.
- Saving: `fig.savefig("out.png", dpi=200, bbox_inches="tight")`; `plt.close(fig)` to free memory.

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 200)
fig, ax = plt.subplots(figsize=(6, 3.5))
ax.plot(x, np.sin(x), label="sin(x)")
ax.plot(x, np.cos(x), label="cos(x)", linestyle="--")
ax.set(xlabel="x (radians)", ylabel="value", title="Trigonometric functions")
ax.legend()
fig.savefig("trig.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

### Intermediate — what to learn

- Multiple axes: `plt.subplots(nrows, ncols, sharex=True, sharey=True)`, `constrained_layout=True`, `fig.subplot_mosaic("AB;CC")` for flexible layouts; twin axes (`ax.twinx()`) and when to avoid them.
- Scales and ticks: `set_xscale("log")`, `symlog`, `MultipleLocator`, `FuncFormatter`, date axes (`matplotlib.dates`, `AutoDateLocator`, `ConciseDateFormatter`), tick rotation, formatting large numbers (`1.2M`).
- Annotations: `ax.annotate`, `axhline`/`axvline`, `axvspan` (highlight incidents), text placement, arrows.
- Colour and style: named colours, colormaps (sequential `viridis`, diverging `RdBu`, qualitative `tab10`), `plt.style.use`, `rcParams`, style sheets, `cycler`.
- Plotting from data: pass arrays/Series; `ax.scatter(c=..., s=..., alpha=...)`, colourbars (`fig.colorbar`), `ax.hist(bins=..., density=True)`, `ax.fill_between` for ranges/uncertainty.
- Backends & environments: inline in notebooks (`%matplotlib inline`/`widget`), non-interactive `Agg` for servers and CI (`matplotlib.use("Agg")`), headless rendering.
- Common figure recipes: time series with rolling mean, histogram with percentile lines, bar chart sorted with value labels, heatmap with annotated cells, small multiples.

```python
fig, axes = plt.subplots(1, 2, figsize=(9, 3.2), sharey=True, constrained_layout=True)
axes[0].hist(latency_ms, bins=40); axes[0].set(title="Latency", xlabel="ms", ylabel="requests")
axes[1].hist(np.log10(latency_ms), bins=40); axes[1].set(title="log10 latency", xlabel="log10(ms)")
for ax in axes: ax.axvline(np.percentile(latency_ms, 99), color="crimson", ls=":")
```

### Advanced — what to learn

- The Artist layer: creating `Line2D`, `Rectangle`, `Text` objects directly; transforms (data, axes, figure, display coordinates) and why annotations use `transform=ax.transAxes`; z-order; clipping.
- Performance with large data: downsample/aggregate (hexbin, `datashader` awareness), `rasterized=True`, avoid plotting 10⁷ points as vectors, `LineCollection`, blitting for animation; memory leaks from unclosed figures in loops/servers.
- Animation: `FuncAnimation`, saving GIF/MP4 (needs `ffmpeg`/`pillow`); when a static small multiple is better.
- Custom components: reusable plotting functions that accept an `ax` and return the artist (`def plot_hist(data, *, ax=None, **kwargs)`), consistent theming through a shared style module; no global state mutation; type hints for plotting helpers.
- Testing plots: image comparison (`pytest-mpl`), asserting on artist data (`ax.lines[0].get_ydata()`), smoke tests that figures build without error, golden images in CI (Module 1.16 lesson 04) with tolerance.
- Matplotlib in servers: thread-safety (pyplot is not thread-safe → use OO API with `Figure()` directly and `FigureCanvasAgg`), caching, avoid global `plt` state.
- Vector vs raster export: PDF/SVG for papers, PNG for web; fonts (embed TrueType), DPI, figure size in inches matched to column width, colour spaces.
- Writing a small plotting library: `plotkit` with `apply_style()`, `time_series()`, `distribution()`, `heatmap()`, docstrings and tests.

### Common mistakes

- Mixing pyplot state with OO calls in loops (drawing on the wrong axes).
- Forgetting `plt.close(fig)` in batch jobs → memory growth.
- Overplotting large data as opaque points.

### Self-check

1. What is the difference between a `Figure`, an `Axes` and an `Axis`?
2. Why is `fig, ax = plt.subplots()` preferred in functions you reuse?
3. Plot a pipeline-run duration time series with a rolling mean, an incident shaded region and a p95 line; export as SVG and PNG.

---

## Lesson 02 — `02-choosing-the-right-chart.md`

**Why it matters.** The most common visualization failure is not technical;
it's choosing a chart that hides or distorts the answer. Good chart choice
starts from the **question** and the **data types**, not the library.

### Basic — what to learn

- Start with the question: comparison, distribution, relationship, composition, trend over time, geography, ranking, uncertainty.
- Data types: categorical (nominal/ordinal), numerical (discrete/continuous), temporal.
- Chart-to-question guide:

| Question | Typical chart | Avoid |
| --- | --- | --- |
| Compare values across categories | Bar (horizontal when labels are long), dot plot | 3-D bars, pie with > 5 slices |
| Distribution of one variable | Histogram, KDE, ECDF, box/violin | Bar chart of means only |
| Relationship of two numeric variables | Scatter (+ trend line), hexbin | Dual-axis lines implying correlation |
| Change over time | Line (ordered x), area for cumulative | Bars for dense time series |
| Part-to-whole | Stacked bar, 100 % bar, treemap | Pie/donut for fine comparison |
| Ranking | Sorted bar/lollipop | Unsorted bars |
| Many categories × many measures | Heatmap, small multiples | Overloaded multi-series line chart |
| Uncertainty | Error bars, CI bands, fan chart | Point estimates alone |

```python
# sorted horizontal bar for a ranking
order = counts.sort_values()
ax.barh(order.index, order.values)
```

### Intermediate — what to learn

- **Integrity rules**: bar charts start at zero; consistent axis scales across comparable panels; don't truncate to exaggerate; show denominators; label units; avoid dual axes unless clearly indicated; log scale labelled explicitly.
- **Perception**: position on a common scale > length > angle/area > colour intensity; use position wherever precision matters.
- Overplotting remedies: alpha, jitter, hexbin, 2-D histogram, sampling, ECDF; small multiples (facets) instead of spaghetti plots.
- Colour: sequential vs diverging vs qualitative palettes, colourblind-safe palettes (`viridis`, `cividis`, ColorBrewer `Set2`), contrast, avoid rainbow (`jet`), consistent colour-to-category mapping across figures, don't rely on colour alone (markers, line styles, direct labels).
- Showing distributions honestly: histograms with explicit bins, ECDF, violin vs box; show sample sizes.
- Time-series pitfalls: irregular sampling, aggregation windows, time zones (UTC; Module 1.9 lesson 07), missing data gaps (don't connect across gaps), seasonality.
- Annotation & titles that state the takeaway ("p99 latency doubled after release 4.2") rather than just "Latency".
- Data-engineering charts: row counts per stage (funnel), freshness/lag over time, null-rate heatmap per column per day, schema drift timeline, job duration box plots, cost per pipeline.
- AI-engineering charts (preview): learning curves, confusion matrices (normalised), calibration (reliability) plots, ROC/PR curves, embedding projections, token/cost distributions, latency vs quality scatter (Pareto front).

### Advanced — what to learn

- Visualization grammar: marks + encodings + scales (Grammar of Graphics; Altair/Vega-Lite, plotnine) — think in channels (x, y, colour, size, shape, facet) to design charts systematically.
- Cognitive load & design: data-ink ratio (Tufte) with judgement; direct labelling instead of legends; consistent ordering; whitespace; typography and hierarchy; small multiples with shared scales; sparklines; annotation of events.
- **Misleading charts catalogue** and how to detect/fix: truncated axes, cherry-picked ranges, inconsistent bins, area scaling by radius, dual-axis spurious correlation, smoothing hiding spikes, survivorship bias, Simpson's paradox visualised, ecological fallacy, 3-D effects.
- Uncertainty visualization: bootstrap confidence bands, quantile dot plots, forecast fans; communicating effect sizes with intervals for A/B tests (Stage 4 statistics, Stage 10 evals).
- High-dimensional data: PCA/UMAP projections (and why distances/clusters can mislead), parallel coordinates, pair plots, correlation heatmaps with clustering; avoid over-interpreting.
- Accessibility & inclusivity: colourblind simulation (`colorspacious`, browser tools), contrast ratios, alt text/long descriptions, readable font sizes, not encoding meaning in colour alone, grayscale printing.
- Audience design: executive (one takeaway), engineer (details + raw data access), analyst (interactivity); chart + table pairing; "so what" statements.
- Review exercise: critique 10 published charts (news, papers, vendor dashboards) with a checklist (question, encoding, honesty, clarity, accessibility) and redraw three.
- Build a **chart-choice cheat sheet** tailored to your future work (pipelines, evals, costs) with code snippets for each.

### Common mistakes

- Pie charts for many categories.
- Rainbow colormaps.
- Titles describing the chart instead of the finding.

### Self-check

1. For each of six given questions, pick a chart type and justify, then name one misleading alternative.
2. Fix a chart with a truncated y-axis, rainbow colormap and dual axes.
3. Design the five charts you would put on a "pipeline health" page and what decision each supports.

---

## Lesson 03 — `03-seaborn-and-plotly.md`

**Why it matters.** Seaborn gives statistically-aware plots with a few lines
(distributions, relationships, categorical comparisons, facets). Plotly gives
interactive, shareable charts (hover, zoom, filter) for exploration and web
dashboards. Knowing both — and when plain Matplotlib is best — covers 95 % of
needs.

### Basic — what to learn

- **Seaborn** works best with *tidy (long-form)* data: one row per observation, one column per variable.
- Figure-level functions (`relplot`, `displot`, `catplot`) with `col=`/`row=`/`hue=` faceting vs axes-level functions (`scatterplot`, `histplot`, `boxplot`) that draw on a given `ax`.
- Core plots: `histplot`, `kdeplot`, `ecdfplot`, `scatterplot`, `lineplot` (automatic CI), `barplot`, `boxplot`, `violinplot`, `heatmap`, `pairplot`.
- Themes: `sns.set_theme(style="whitegrid", context="notebook", palette="colorblind")`.

```python
import seaborn as sns
sns.set_theme(style="whitegrid", palette="colorblind")
tips = sns.load_dataset("tips")                      # tiny built-in dataset
sns.displot(tips, x="total_bill", hue="time", col="day", col_wrap=2, kind="hist", height=2.6)
```

### Intermediate — what to learn

- Statistical aggregation in Seaborn: what error bars mean (`errorbar=("ci", 95)`, `"sd"`, `"se"`, `"pi"`), bootstrap defaults, `estimator`, `n_boot`; document what you plot.
- Wide vs long data: `DataFrame.melt` to reshape for Seaborn (pandas, Stage 2); ordering categories (`order=`, `pd.Categorical`).
- Combining Seaborn with Matplotlib: draw on a given `ax`, customise with `ax.set(...)`, `sns.despine()`, `FacetGrid.map_dataframe`, `PairGrid` customisation.
- Heatmaps done well: annotated cells, diverging palette centred at 0 (`center=0`), mask upper triangle for correlation matrices, clustermap for ordering.
- **Plotly**: `plotly.express` (px) for quick interactive charts (`px.line`, `px.scatter`, `px.bar`, `px.histogram`, `px.box`, `px.imshow`, `px.scatter_matrix`), `graph_objects` (go) for fine control, `fig.update_layout`, `update_traces`, hover templates, facets, animations (`animation_frame`).
- Output & sharing: `fig.show()` in notebooks, `fig.write_html("report.html", include_plotlyjs="cdn")` for standalone interactive files, `fig.write_image("fig.png")` (needs `kaleido`), JSON (`fig.to_json()`).
- Plotly dark/light themes (`template="plotly_white"`), accessible colour sequences.

```python
import plotly.express as px
df = px.data.gapminder().query("year == 2007")
fig = px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", color="continent",
                 hover_name="country", log_x=True, title="Life expectancy vs income (2007)")
fig.write_html("gapminder.html", include_plotlyjs="cdn")
```

### Advanced — what to learn

- Seaborn objects interface (`seaborn.objects`, declarative Grammar-of-Graphics style): `so.Plot(...).add(so.Dot(), so.Agg())`, scales, stats, moves — compare with classic functions.
- Big data & interactivity: Plotly with WebGL (`px.scatter_gl`, `Scattergl`) for 10⁵–10⁶ points; aggregation before plotting; `datashader` + `holoviews`/`hvplot` for 10⁷+ points; `polars`/`pyarrow` as input to avoid copies; server-side aggregation in DuckDB/SQL for dashboards (Stage 2).
- Interactivity beyond static: `ipywidgets` (`interact`, sliders, dropdowns) for parameter exploration, Plotly `FigureWidget`, linked brushing; when to move to a real app (Streamlit/Dash/Panel/Gradio — Stage 7 minimal frontends).
- **Dash / Streamlit** awareness: callbacks vs script reruns, state management, deployment caveats, authentication and data access control; do not expose raw data unintentionally in a client-side figure (the full dataset is embedded in the HTML!).
- Security & privacy: shared HTML files embed data and possibly PII/secrets; sample or aggregate before export; redact identifiers; review hover text; CDN scripts vs offline bundles (`include_plotlyjs=True`) for air-gapped environments.
- Consistency across libraries: shared colour mapping dictionaries, helper functions that render the same logical chart in Matplotlib (static report) and Plotly (interactive), template modules (`plotkit.themes`).
- Altair/Vega-Lite, Bokeh, HoloViz and plotnine as alternatives — comparison table (declarative grammar, interactivity, ecosystem) and when to choose.
- Performance & reproducibility: deterministic ordering and colour assignment, seeds for sampled plots, caching expensive aggregations, versions pinned (visual outputs change across versions → golden-image tolerances).
- Build a **model-evaluation gallery** (preview of Stages 5–6): confusion matrix heatmap, ROC/PR curves, calibration plot, learning curves, residual plots using Matplotlib/Seaborn/Plotly versions of each; note strengths/weaknesses.

### Common mistakes

- Passing wide, untidy data to Seaborn and fighting the API.
- Not stating what the error band represents.
- Sharing interactive HTML containing the entire raw dataset.

### Self-check

1. Difference between a figure-level and an axes-level Seaborn function, and when you can combine them with Matplotlib?
2. What does the shaded band in `sns.lineplot` represent by default and how do you change it?
3. Produce the same chart in Seaborn (static, PNG) and Plotly (interactive HTML) and list one decision in favour of each.

---

## Lesson 04 — `04-jupyter-notebook-workflows.md`

**Why it matters.** Notebooks are the lingua franca of exploration — and a
leading cause of "works on my machine", hidden state bugs (cells run out of
order), unreviewable diffs and leaked credentials. A disciplined workflow
keeps their speed and removes the risks.

### Basic — what to learn

- Concepts: kernel, cells (code/markdown/raw), execution counter, outputs, `.ipynb` JSON format.
- JupyterLab and VS Code notebooks; kernels tied to environments (`uv run --with ipykernel`, `python -m ipykernel install --user --name myproj`), selecting the right interpreter.
- Productive features: markdown with LaTeX, magics (`%timeit`, `%%time`, `%load_ext autoreload`, `%autoreload 2`, `%matplotlib inline`), `!shell` commands (careful), `?`/`??` help, tab completion, variable inspector, debugger, outline/TOC.
- Structure of a good notebook: title + purpose, data sources, parameters cell, setup/imports, load, clean, analyse, visualise, conclusions, next steps.
- The **hidden state problem**: cells executed out of order, deleted cells whose variables persist; always **Restart & Run All** before trusting or sharing.

```python
# cell 1 — parameters (tagged "parameters" for papermill; see lesson 05)
DATA_PATH = "data/orders.parquet"
START_DATE = "2026-01-01"
SAMPLE_FRAC = 1.0

# cell 2 — setup
%load_ext autoreload
%autoreload 2
import pandas as pd, numpy as np, matplotlib.pyplot as plt
```

### Intermediate — what to learn

- **Notebook as thin layer over code**: put logic in an importable package (`src/yourpkg/`), install it editable (`uv pip install -e .`), use `%autoreload`; notebooks call functions and show results; this keeps code testable (Module 1.7) and diffs small.
- Version control: `.ipynb` diffs are noisy (outputs, execution counts, metadata). Practices: strip outputs before commit (`nbstripout` as a git filter/pre-commit hook), or pair with text (`jupytext --set-formats ipynb,py:percent`), review with `nbdime` or rendered previews (GitHub), keep notebooks small and focused.
- Kernels & environments: one environment per project, lock files (Module 1.6), record versions in the notebook (`%pip freeze` is discouraged inside notebooks; print versions of key libs), avoid `!pip install` in shared notebooks.
- Data handling: don't embed data in the repo; use relative paths from project root (`pathlib`), config/env vars for locations, sample data for tests; large outputs (display only `head`), memory hygiene (`del`, `gc.collect()`, reading in chunks), caching expensive steps (`joblib.Memory`, parquet checkpoints) with explicit invalidation.
- Secrets & PII: never print or store tokens, connection strings or personal data in outputs (outputs are saved in the file!); load secrets from environment variables; use `getpass` for interactive input; clear outputs before sharing.
- Collaboration patterns: notebook review checklist, naming conventions (`01_explore_orders.ipynb`), numbering, `README` in notebooks folder, linking to figures/exports, using `jupyter-collaboration` or sharing through VS Code Live Share (optional).
- Linting & formatting notebooks: `ruff` supports `.ipynb`; `nbqa` for other tools (mypy); keep imports at top; no unused variables.

```bash
uv add --dev nbstripout ruff jupytext
uv run nbstripout --install              # git filter strips outputs on commit
uv run jupytext --set-formats ipynb,py:percent analysis.ipynb
uv run ruff check --select I,F analysis.ipynb
```

### Advanced — what to learn

- Notebooks vs scripts vs apps: decision framework — exploration & teaching (notebook), repeatable batch (script/package + orchestrator, Stage 2), interactive tool (app), reporting (rendered notebook/Quarto). Promote notebook code to a package when reused twice.
- **Reproducibility checklist**: pinned environment, deterministic seeds (`random`, `numpy`, framework seeds; Module 1.13 lesson 07), fixed data snapshot/version (hash/path/commit), parameters recorded in the output, tests for functions, "Restart & Run All" in CI, no dependence on current time without recording it.
- Performance & scale: avoid loading full datasets into the browser kernel; use DuckDB/Polars lazy scans (Stage 2), remote kernels (SSH/JupyterHub/cloud notebooks — Stage 2 Linux/AWS/Databricks), resource limits, long-running jobs belong in orchestrated jobs not notebooks.
- Debugging notebooks: `%debug`, `%pdb on`, `breakpoint()`, VS Code debugger, inspecting tracebacks (frames in cells), memory (`%memit` via `memory_profiler`, `tracemalloc`), profiling cells (`%prun`, `%lprun`, `%%timeit`).
- Alternative notebook systems: **marimo** (reactive, pure `.py` files, deterministic execution order), **Quarto** (`.qmd`, multi-language publishing), **Observable**, Databricks/Colab/Kaggle notebooks (platform quirks: ephemeral disks, secrets management, library installs), **Pluto.jl** — compare hidden-state handling.
- Security: untrusted notebooks execute arbitrary code (open in sandbox/trusted-state aware tools; don't "Trust" unknown notebooks); JupyterLab server exposure (token auth, no public ports, TLS, reverse proxy), extension supply-chain risk; sandboxing for LLM-generated code execution (Agents stage).
- Notebook testing: `nbmake`/`pytest --nbmake` run all notebooks; `nbval` validate outputs; test functions extracted from notebooks; smoke test that the notebook executes with sample data.
- Teaching & documentation: narrative flow, assertions as checks (`assert df.id.is_unique`), visible data-quality checks, "key findings" cell at the top with date and data version.
- Exercise: take a messy exploratory notebook (provided or your own), apply the full workflow — parameters cell, restart/run-all fix, extract functions into a package with tests, strip outputs, jupytext pairing, pre-commit config, CI execution — and document before/after.

### Common mistakes

- Trusting results from a notebook that was never run top-to-bottom.
- Committing outputs containing data or secrets.
- Long, monolithic notebooks with copy-pasted code.

### Self-check

1. What is hidden state and how do you eliminate it?
2. Describe two ways to make notebook diffs reviewable.
3. Convert an exploratory notebook into: a package function with tests + a thin notebook + a CI check that executes it.

---

## Lesson 05 — `05-reproducible-notebooks-with-papermill-and-nbstripout.md`

**Why it matters.** A notebook that can run unattended with parameters
becomes a repeatable report or job; one that can't be re-executed cleanly is
a liability. Papermill, nbconvert, nbstripout and friends turn notebooks
into controlled, auditable artifacts.

### Basic — what to learn

- **Papermill** parametrised execution: tag one cell `parameters`; run `papermill input.ipynb output.ipynb -p start_date 2026-01-01 -p sample_frac 0.1`; Papermill injects a new cell after the parameters cell with overrides.
- Output notebook = **record of the run** (inputs, outputs, errors); keep inputs under version control and outputs as artifacts.
- **nbconvert**: `jupyter nbconvert --to html --no-input report.ipynb` (executive report without code), `--to markdown/pdf/script`, `--execute`.
- **nbstripout**: strip outputs/metadata from committed notebooks; `nbstripout --install` sets a git filter; `--keep-output` options per project policy.

```bash
uv run papermill notebooks/daily_report.ipynb out/daily_2026-10-14.ipynb \
    -p run_date 2026-10-14 -p data_path data/orders.parquet
uv run jupyter nbconvert --to html --no-input --execute out/daily_2026-10-14.ipynb
```

### Intermediate — what to learn

- Designing a parametrised notebook: parameters with safe defaults, validation cell (assert parameter types/ranges), deterministic seeds, data snapshot version as a parameter, output directory as a parameter.
- Return values from notebooks: `scrapbook` (`sb.glue("rows", n)`) to record metrics/figures/dataframes as notebook-attached data readable by downstream code (`sb.read_notebook`), or write explicit output files.
- Error handling: Papermill fails the run and keeps the output notebook with the traceback (`--log-output`, `--progress-bar`); retries only for idempotent notebooks; timeouts (`--execution-timeout`); working directory and kernel selection (`-k`), `--cwd`.
- **Jupytext** paired scripts (`py:percent`) for readable diffs and code review; `jupytext --sync`; `.pre-commit-config.yaml` hooks for `nbstripout`, `ruff`, `jupytext`.
- Quarto / `nbconvert` templates for professional reports; embedding figures/tables, hiding code cells with tags (`remove-input`, `remove-cell`), table of contents.
- Scheduling notebooks: cron/systemd timers, CI schedule, orchestrators (Airflow `PapermillOperator`, Dagster, Databricks Jobs — Stage 2 orchestration); convert to scripts when logic stabilises.
- Environment capture: record `sys.version`, key library versions, git commit SHA, parameter values and data version into the output (a "provenance" cell) — e.g. 

```python
import sys, platform, subprocess, json, importlib.metadata as md
prov = {
  "python": sys.version.split()[0], "platform": platform.platform(),
  "git": subprocess.run(["git","rev-parse","--short","HEAD"], capture_output=True, text=True).stdout.strip(),
  "libs": {p: md.version(p) for p in ("pandas","numpy","matplotlib")},
  "params": {"run_date": run_date, "data_path": data_path},
}
print(json.dumps(prov, indent=2))
```

### Advanced — what to learn

- Notebook execution in CI/CD: `pytest --nbmake notebooks/` in a matrix, caching environments, artifacts upload (HTML/ipynb), failing builds on warnings, executing with sample data and a time budget, `nbval` for output regression with tolerance and output sanitisation regexes.
- Idempotency and determinism (Module 1.10 lesson 04): same parameters + same data version → same outputs (or documented non-determinism); atomic writes of outputs; run IDs; avoid overwriting; naming conventions with dates/hashes.
- Governance: who can run which notebooks on which data (access control); audit trail (stored output notebooks + logs); PII redaction in outputs (`remove-output` tags, programmatic scrubbing with `nbformat` before sharing); data retention for executed notebooks.
- Programmatic notebook manipulation: `nbformat` read/modify/write (inject cells, strip outputs, add tags, validate schema), `nbclient` for execution with custom hooks/timeouts, `nbconvert` preprocessors/exporters to enforce policies (e.g. fail if outputs exceed N MB or contain patterns like `AKIA…`/`Bearer`).
- Secret-scanning of notebooks (`gitleaks`, `detect-secrets`) in pre-commit and CI; treat `.ipynb` as code *and* data for scanning.
- Scaling: parallel parameter sweeps (`papermill` in a pool/array job), cloud execution (Databricks, SageMaker, Vertex), containerised notebook runners with pinned images (Stage 2 Docker), resource requests, cleanup of kernels.
- From notebook to pipeline: criteria for promoting (stable inputs/outputs, needed schedule, SLAs, tests), refactor steps (functions → module → CLI → orchestrated task), keeping the notebook as the **report layer**.
- Data & model lineage: link notebook runs to experiment trackers (MLflow, Stage 5) — log params/metrics/artifacts from notebooks (`mlflow.log_*`), record dataset versions.
- Alternative executors: `marimo export`/`marimo run` scripts, `Quarto render --execute-params`, `jupyter execute`, `ploomber` pipelines — compare.
- Exercise: build a **daily data-quality report** notebook parameterised by date; schedule it via CI/cron; outputs HTML + metrics JSON; fail loudly on threshold breach; strip outputs from committed notebooks; add secret scanning and a provenance cell; document the runbook.

### Common mistakes

- Parameters cell missing the `parameters` tag (Papermill can't inject).
- Executing notebooks against production data from a laptop with no audit trail.
- Committing executed notebooks with sensitive outputs.

### Self-check

1. How does Papermill inject parameters and where do results go?
2. Which controls prevent secrets and PII from leaking through `.ipynb` files?
3. Build a parameterised report notebook, execute it for three dates in CI and attach HTML artifacts.

---

## Lesson 06 — `06-figures-for-reports-and-dashboards.md`

**Why it matters.** Analysis only matters if the audience understands and
trusts it. Figures for reports, papers, slide decks, READMEs and dashboards
have different requirements — and need to be reproducible, accessible and
safe to share.

### Basic — what to learn

- Start from the message: one figure = one takeaway; title states the finding; subtitle gives scope (dates, filters, n); source/footnote with data version.
- Layout & typography: readable font sizes at final size (≥ 8–10 pt), consistent fonts, limited palette, direct labels, minimal gridlines, aligned axes in small multiples.
- Sizing and export: set `figsize` to the final column/slide width, DPI 150–300 for raster, **SVG/PDF for vector**, transparent backgrounds when needed, consistent aspect ratio, `bbox_inches="tight"`, embed fonts.
- File naming and organisation: `reports/figures/2026-10-14_latency_p99.svg`; generated by code, not saved by hand; the figure script/notebook path in the caption or metadata.
- Tables vs charts: use a table for precise lookup, chart for pattern; format numbers (thousand separators, units, rounding, % vs pp).

```python
fig.suptitle("p99 latency doubled after release 4.2", x=0.01, ha="left", fontsize=13, weight="bold")
fig.text(0.01, 0.01, "Source: api_gateway_logs v2026-10-14 · n = 1.2M requests", fontsize=8, color="0.4")
fig.savefig("reports/figures/latency_p99.svg", bbox_inches="tight")
```

### Intermediate — what to learn

- A **house style**: a shared `style.mplstyle`/`plotkit.themes` with palette, fonts, grid, spine rules; Plotly `pio.templates` default; documented colour semantics (e.g. red = error, blue = baseline); dark-mode variants.
- Annotated storytelling: highlight the key series (colour) and mute the rest (grey), annotate events (releases, incidents), show baselines/targets (SLO lines), before/after panels, consistent time windows.
- Reports: assemble figures into documents — Markdown/Quarto/Jupyter Book/Sphinx, LaTeX/PDF, HTML (`nbconvert`), slide decks (`reveal.js`, PowerPoint via `python-pptx`); keep figures generated by a single reproducible command (`make report` / `uv run python -m reports.build`).
- **Lightweight dashboards**: Plotly Dash, Streamlit, Panel, Gradio, Evidence, Grafana (metrics), Superset/Metabase/Looker (BI; Stage 2 serving). Choose by audience, data size, refresh rate, authentication.
- Dashboard design: top-line KPIs → trends → breakdowns → details; filters that are obvious; default time range; units; last-updated timestamp; links to source/runbook; avoid more than ~6–8 visuals per page.
- Data prep for dashboards: pre-aggregate (DuckDB/SQL/materialised tables), cache queries with TTL, avoid shipping raw rows to the browser, handle empty/error states, paginate tables.
- Accessibility: colourblind-safe palettes, text alternatives (alt text & data tables), keyboard navigation in web dashboards, sufficient contrast, avoid flashing animations.

### Advanced — what to learn

- **Reproducible reporting pipeline**: data version → analysis code → figures → report; Makefile/`nox`/`just`/orchestrator; deterministic outputs; golden-image tests with tolerance (`pytest-mpl`); CI builds the report on every merge; artifacts retained; reports versioned with git tags or run IDs; changelog of metric definitions.
- **Metric definitions & trust**: a metrics dictionary (name, definition, owner, source, refresh); consistent definitions across dashboards; showing data freshness, completeness and known caveats; handling late-arriving data/restatements; annotate when definitions change.
- Dashboards for AI systems (preview of Stages 10, 14): quality evals over time with confidence intervals, regression gates, cost/latency/token usage breakdowns by model and route, retrieval metrics, guardrail triggers, drift monitors, human-feedback rates; drill-down from aggregate to example traces; privacy-aware sampling of prompts/outputs.
- Operational concerns: authentication/authorisation (SSO), row-level security, PII masking, audit logs, rate limits and query cost controls, caching layers, deployment (container, serverless), monitoring of the dashboard itself, and graceful degradation when data sources fail.
- Performance: server-side aggregation, WebGL for large scatterplots, downsampling strategies (LTTB for time series), lazy loading, pagination; measure page load and query times; avoid recomputing on each interaction (callback caching/memoisation).
- Communicating uncertainty and limitations: ranges not just means, sample sizes, caveats panel, methodology links; avoid false precision; flag provisional data; guard against p-hacking by dashboards offering endless slices (pre-register key views).
- Visual QA checklist: correct data (spot-check against raw numbers), axis starts/scales, labels/units, legend order, colour consistency, overlapping text, rounding, time zone, empty states, mobile/print rendering, dark mode, export formats.
- Ethical considerations: avoid misleading framing, show denominators for rates, represent groups responsibly, respect privacy (small-cell suppression/k-anonymity thresholds), disclose model limitations.
- Portfolio project guidance (Stage 16): README with screenshots/GIFs, live demo or recorded walkthrough, reproducible `make report`, clear narrative of problem → data → method → findings → limitations.
- Exercise: build a **Pipeline Health report + mini-dashboard** from synthetic run logs: KPIs (success rate, p95 duration, freshness, row-count anomaly), trend charts with SLO lines, a failure breakdown, and a downloadable HTML report; add golden-image tests and an automated build; write a one-page metric dictionary.

### Common mistakes

- Dashboards with 20 unrelated charts and no hierarchy.
- Figures saved by hand from a notebook with no way to regenerate.
- Presenting a metric without definition, freshness or sample size.

### Self-check

1. What elements make a figure self-contained for a report reader?
2. How do you make sure a dashboard number matches the source of truth?
3. Automate the generation of a report with figures from versioned data, including a visual regression test and an artifact upload.

---

## 4. Practice questions (`practice-questions.md`)

About **30 questions**:

| Phase | Question types |
| --- | --- |
| A | Fix a broken Matplotlib script (wrong axes); pick the chart for a given question; critique misleading charts |
| B | Tidy vs wide data and Seaborn function choice; interpret error bands; Plotly vs Seaborn trade-offs |
| C | Spot hidden-state bugs in a notebook; design a parameters cell; strip outputs/secrets; Papermill command design |
| D | Design a one-page dashboard; metric dictionary entries; accessibility fixes |

Include 5 **"what is misleading here?"** items and 5 **"what could leak?"** notebook/HTML-export items.

---

## 5. Module mini-project

**Build `datalens`**, a small analysis-and-reporting toolkit:

1. `datalens.plots`: reusable, tested plotting helpers (time series with rolling stats and event markers, distribution with percentiles, annotated heatmap, ranked bar) that accept an `ax`, follow a house style, and have image-comparison tests.
2. `notebooks/01_explore.ipynb`: exploration of a synthetic or public dataset using only package functions; parameters cell; provenance cell; restart-and-run-all clean.
3. `notebooks/02_daily_report.ipynb`: parameterised report executed via Papermill for three dates; exported to HTML (no code) and metrics JSON; CI job with `nbmake`.
4. Git hygiene: `nbstripout` filter, `jupytext` pairing, pre-commit with `ruff`/secret scan.
5. A Plotly interactive version of two figures exported as standalone HTML, with data aggregated/sampled and reviewed for PII.
6. `REPORT.md` or a Quarto page assembling the figures with captions stating takeaways, sources and data versions.
7. A `metrics.md` dictionary and a short `STYLEGUIDE.md` (palette, fonts, chart rules, accessibility checklist).

Acceptance: `make report` regenerates all figures/HTML from scratch, CI passes (tests + notebook execution), no outputs/secrets in committed notebooks, accessibility checklist completed, README with screenshots.

---

## 6. Completion checklist

- [ ] I use Matplotlib's object-oriented API and can build complex multi-axes layouts.
- [ ] I choose charts from questions and data types and can spot misleading designs.
- [ ] I can build statistical plots with Seaborn and interactive plots with Plotly, knowing what error bands mean.
- [ ] I work in notebooks without hidden state and keep logic in tested modules.
- [ ] I make notebooks reproducible and reviewable (parameters, provenance, nbstripout, jupytext).
- [ ] I run notebooks unattended with Papermill/nbconvert and in CI.
- [ ] I keep secrets and PII out of notebooks and shared figures.
- [ ] I produce accessible, consistent, publication-quality figures and simple dashboards.
- [ ] I document metrics, data versions and limitations alongside visuals.
- [ ] I completed the `datalens` mini-project.

**Next:** Module 1.22 — Secure Python Coding.
