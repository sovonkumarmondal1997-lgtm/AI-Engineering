# Module 1.21 --- Data Visualization and Notebook Workflows: Practice Questions

## Purpose

This assessment checks whether you can create accurate, interpretable
figures and build notebook-based analysis that is reproducible,
reviewable, and safe to share. It follows the module roadmap's four
phases and stays within its stated scope: Matplotlib, chart integrity,
Seaborn, Plotly, Jupyter, Papermill, `nbstripout`, CI, report figures,
and lightweight dashboards.

## Instructions for the learner

-   There are **30 questions**, grouped by phase and numbered
    continuously. Suggested time: 2--3 hours, or split across four
    sessions.
-   Unless a question says otherwise, use Python 3.12+, Matplotlib 3.9+,
    Seaborn 0.13+, Plotly 5/6, JupyterLab 4, and Papermill/nbstripout
    concepts described in this module.
-   Use only the data and assumptions stated in each question. Small
    synthetic datasets are supplied where needed.
-   For design questions, explain your reasoning. More than one answer
    may be valid if you identify trade-offs and preserve the analytical
    meaning.
-   Do the questions before consulting the **Answer key**. The answer
    key is intentionally included in this file for self-study;
    instructors may distribute a learner copy with that section removed.
-   Code questions should be answered with complete, runnable snippets
    where requested. Do not rely on hidden files, notebook execution
    history, production data, or network access.
-   Security questions ask you to identify plausible disclosure paths,
    not to assume that every exported artifact contains every type of
    data.

## Coverage map

  ----------------------------------------------------------------------------------------
  Phase                          Questions        Approx. count Primary coverage
  ------------------- -------------------- -------------------- --------------------------
  **A --- Plot                        1--8                    8 Figure/Axes/Axis/Artist;
  mechanics and chart                                           object-oriented API; chart
  choice**                                                      choice; chart integrity;
                                                                reusable plotting helpers

  **B --- Seaborn and                9--14                    6 Tidy/wide data;
  Plotly**                                                      figure-level vs
                                                                axes-level; error bands;
                                                                static vs interactive
                                                                trade-offs; interpretation

  **C --- Notebook                  15--22                    8 Hidden state; refactoring
  workflows and                                                 and tests; Papermill
  reproducibility**                                             parameters; CI; output
                                                                stripping; five leakage
                                                                reviews

  **D ---                           23--30                    8 Self-contained figures;
  Communication,                                                exports; metric
  reports, and                                                  dictionary; dashboard
  dashboards**                                                  hierarchy; accessibility;
                                                                data lineage and
                                                                operational judgement
  ----------------------------------------------------------------------------------------

------------------------------------------------------------------------

# Phase A --- Plot mechanics and chart choice

## Q1. Figure, Axes, Axis, and Artist (Conceptual · Basic · 4 points)

Explain the difference between a Matplotlib `Figure`, an `Axes`, an
`Axis`, and an `Artist`. Give one concrete example of an Artist. Then
explain why `fig, ax = plt.subplots()` is usually preferable to relying
on implicit `pyplot` state in a reusable plotting function.

## Q2. Debug the wrong-axes bug (Debugging · Intermediate · 4 points)

The intention is to put latency on the left panel and throughput on the
right panel. Instead, the second line is drawn on the wrong axes.

``` python
import matplotlib.pyplot as plt

latency_ms = [20, 24, 22]
throughput_rps = [100, 120, 115]
minute = [1, 2, 3]

fig, axes = plt.subplots(1, 2, figsize=(8, 3))
axes[0].plot(minute, latency_ms, marker="o", label="latency")
plt.sca(axes[0])  # simulate a prior helper leaving the left Axes current
plt.plot(minute, throughput_rps, marker="s", label="throughput")
axes[0].set(title="Latency", xlabel="minute", ylabel="ms")
axes[1].set(title="Throughput", xlabel="minute", ylabel="requests/s")
fig.tight_layout()
```

**Tasks:** (a) Identify the defect and explain why the result depends on
implicit state. (b) Rewrite the plotting calls so each series is drawn
on its intended axes. (c) Name one sensible cleanup step when this code
runs repeatedly in a batch job.

## Q3. Design a reusable plotting helper (Code writing · Intermediate · 4 points)

Write a function `plot_duration(minutes, duration_ms, *, ax=None)` that
plots duration over time, labels both axes with units, and returns the
`Axes`. If `ax` is omitted, create a figure and axes. The function must
not call `plt.show()` or save a file. Briefly explain why accepting an
existing `Axes` helps callers build subplots and tests. Then describe
write a small caller example using a synthetic, equally spaced pipeline-
run duration series to add a trailing rolling mean, an incident shaded
interval, and an overall p95 reference line, then export the finished
figure as both SVG and PNG. State how you would avoid a misleading
rolling window when observations are irregularly spaced.

## Q4. What is misleading here? --- truncated bar axis (Chart critique · Basic · 4 points)

A report compares job success rates: Service A = 96%, Service B = 98%.
The bar chart's y-axis runs from 95% to 100%, and the bars are shown as
if B is several times taller than A. The title says "Service B
dramatically outperforms Service A."

Identify at least two problems and propose a more honest design. Is a
truncated axis always forbidden? Explain the condition under which it
may be acceptable.

## Q5. What is misleading here? --- wrong chart and aggregation (Chart selection · Intermediate · 4 points)

A team wants to answer: **"Did the daily p95 pipeline duration change
after a deployment on 12 October?"** It plots a pie chart with one slice
for each date, where slice size equals that day's p95 duration. The data
are:

  Date       p95 duration (seconds)
  -------- ------------------------
  10 Oct                         42
  11 Oct                         43
  12 Oct                         61
  13 Oct                         64
  14 Oct                         59

Explain why the chart is a poor fit, recommend a chart that directly
answers the question, and name two context elements that would make the
result easier to interpret.

## Q6. Select a chart for the question (Scenario · Intermediate · 4 points)

For each question, choose a chart and give a one-sentence justification.
A different chart is acceptable if justified.

1.  Compare failure counts across eight pipeline stages.
2.  Inspect the distribution and long tail of request latency for 2,000
    requests.
3.  Show daily ingestion volume over 30 days and mark an incident
    window.
4.  Compare the relationship between file size and processing duration
    for 300 runs.
5.  Compare incident rates across six countries when country population
    sizes differ.
6.  Show uncertainty around a daily estimated metric without implying
    that the interval is the range of individual observations.

For at least two items, name a plausible but less suitable alternative
and explain why it is less suitable.

## Q7. Code reading: layout and shared axes (Conceptual/code reading · Intermediate · 4 points)

``` python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, sharey=True, constrained_layout=True)
region_a_ms = [10, 11, 12, 12, 13]
region_b_ms = [10, 12, 14, 16, 25]
axes[0].hist(region_a_ms, bins=5)
axes[1].hist(region_b_ms, bins=5)
axes[0].set(title="Region A", xlabel="latency (ms)", ylabel="request count")
axes[1].set(title="Region B", xlabel="latency (ms)")
```

What does `sharey=True` make comparable? Identify one limitation of
comparing these two histograms as written and suggest a repair. You may
assume the values are raw latency observations in milliseconds.

## Q8. What is misleading here? --- colour and dual axes (Chart critique · Advanced · 4 points)

A time-series figure uses a rainbow colour map to encode a nominal
category (`healthy`, `delayed`, `failed`). It also places success rate
on the left y-axis and duration on a right y-axis; the author adjusts
both axis limits until the lines overlap and claims "duration and
success rate are strongly linked."

Explain why the visual evidence does not support the claim. Give two
design changes that improve interpretability without pretending to
establish causation.

------------------------------------------------------------------------

# Phase B --- Seaborn and Plotly

## Q9. Tidy versus wide data (Data modelling · Basic · 4 points)

Consider this table:

  day     region_a_ms   region_b_ms
  ----- ------------- -------------
  Mon              20            24
  Tue              23            22
  Wed              21            25

1.  Explain why this is a wide representation for comparing regions over
    time.
2.  Rewrite it as tidy/long rows with columns `day`, `region`, and
    `duration_ms`.
3.  Give one reason a long representation is convenient for Seaborn's
    semantic mappings.

## Q10. Figure-level versus axes-level Seaborn (Conceptual/code design · Intermediate · 4 points)

You need a faceted distribution plot split by `region`, and you also
need to place a Seaborn scatter plot inside the right panel of a
Matplotlib figure that already contains two other panels.

Choose a suitable figure-level or axes-level function for each task and
explain why. Name one constraint when combining a figure-level Seaborn
function with a Matplotlib layout you already created.

## Q11. Interpret Seaborn's lineplot band (Conceptual · Intermediate · 4 points)

A dataset contains repeated duration measurements for each `day` and
`region`. The code is:

``` python
sns.lineplot(data=df, x="day", y="duration_ms", hue="region")
```

What does the shaded band generally represent by default in Seaborn
0.13.x, and what does it **not** automatically mean? Explain how
changing `errorbar`, for example to `errorbar=None` or `errorbar="sd"`,
changes the interpretation. Mention one reason to display sample size or
explain uncertainty in the caption.

## Q12. Static or interactive? (Trade-off · Intermediate · 4 points)

A daily scheduled report needs a consistent, publication-ready PNG of 14
days of pipeline latency. Separately, an internal investigator needs to
hover over points, zoom into a date range, and inspect individual run
IDs in a browser.

Recommend Seaborn/Matplotlib or Plotly for each deliverable. For a
small common example, assume `df` is already aggregated to exactly one
row per `day` and `pipeline`, with columns `day`, `p95_seconds`, and
`pipeline`; outline the equivalent field mappings and provide a minimal
plotting call for each library (static PNG for the report,
interactive HTML for the investigator). Discuss at least two trade-offs
in rendering, reproducibility, interactivity, or safe data exposure.
Avoid claiming that one library is universally better. Do not include
real run IDs or sensitive fields in the example.

## Q13. What is misleading here? --- error band described as a guarantee (Chart interpretation · Advanced · 4 points)

A Seaborn line plot uses the default shaded band. The report caption
says: "The true latency will fall inside this band for 95% of future
requests." The underlying dataset has repeated observations by day, but
the author has not checked the estimator or interval configuration.

What is wrong with the caption? Describe the checks and explicit
configuration needed before giving the band a more precise
interpretation. Your answer must distinguish uncertainty around an
estimate from the distribution of individual future observations.

## Q14. Static export and interactive HTML (Production judgement · Advanced · 4 points)

A Plotly figure works in a notebook but a PNG export fails on a clean CI
runner. The HTML version works locally. Give two plausible causes of the
PNG failure and a practical CI strategy for each. Also name two checks
to perform before sharing a standalone interactive HTML file.

------------------------------------------------------------------------

# Phase C --- Notebook workflows and reproducibility

## Q15. Find the hidden-state bug (Debugging · Intermediate · 4 points)

A notebook has these cells:

**Cell 1**

``` python
import pandas as pd
runs = pd.DataFrame({"day": ["Mon", "Tue"], "duration_ms": [20, 40]})
```

**Cell 2**

``` python
runs["duration_seconds"] = runs["duration_ms"] / 1000
```

**Cell 3**

``` python
# This cell displays a chart, but it was run yesterday before Cell 2 was edited.
ax.plot(runs["day"], runs["duration_seconds"])
```

The notebook appears to work when opened, but "Restart Kernel and Run
All" raises `NameError: name 'ax' is not defined`.

Identify the hidden-state and ordering problems. Provide a minimal
repair that makes the notebook execute from a fresh kernel. Explain why
saved output is not proof that the current cells run successfully.

## Q16. Refactor notebook logic and test it (Design/code · Intermediate · 4 points)

A notebook contains 70 lines that calculate daily success rate and draw
a chart. Describe a reasonable refactor into (a) a tested Python
function/module and (b) a thin notebook. Include one example of a unit
test assertion, **two ways to make notebook diffs reviewable**, and one
notebook/CI check that detects execution regressions.

## Q17. Design a Papermill parameters cell and command (Code writing · Advanced · 4 points)

You have `notebooks/daily_report.ipynb`. It should accept a report date
and an output directory. Supply a valid parameters cell suitable for
Papermill and a valid shell command to execute it for 2026-10-12 into
`build/2026-10-12.ipynb`. Assume the cell is tagged with the Papermill
`parameters` tag. Briefly state where Papermill's executed notebook goes
and why the tag matters. Then describe a CI loop that runs the notebook
for three dates, exports each executed notebook to HTML with code hidden,
and uploads the HTML files as access-controlled artifacts. State one
idempotency or non-overwrite safeguard.

## Q18. What could leak? --- saved notebook output (Security review · Intermediate · 4 points)

A notebook reads a private customer table and prints `df.head(10)`. The
author deletes the print cell but commits the `.ipynb` file. A reviewer
sees no corresponding source code in the current notebook.

Identify the possible disclosure path and give a safe remediation
workflow. Distinguish output stripping from deleting the original source
data or changing access permissions.

## Q19. What could leak? --- exception and diagnostic output (Security review · Intermediate · 4 points)

A notebook cell fails while constructing a database URL. The traceback
includes a full connection string with a username and password. The
author fixes the code and commits the notebook, assuming that the
visible cell now contains only `get_connection()`. What should be
reviewed and cleaned, and what must happen if a real credential was
exposed?

## Q20. What could leak? --- Papermill artifacts and CI logs (Security review · Advanced · 4 points)

A CI job runs a parameterized notebook against a staging dataset. It
stores the executed `.ipynb` as an artifact and logs all Papermill
parameters. One parameter is a bearer token; a later cell renders a
table containing customer email addresses.

List at least three separate leakage paths or risks and propose controls
for each. Your answer must cover parameters/logs, executed notebook
outputs, and artifact access or retention.

## Q21. What could leak? --- standalone Plotly HTML (Security review · Advanced · 4 points)

An analyst exports a Plotly scatter plot to standalone HTML. The plot
contains one point per support ticket; hover text includes `ticket_id`,
email address, and free-text summary. The HTML file is emailed to a
vendor and does not require a server to open.

Explain why "it is just a chart" is not a sufficient privacy review.
Give at least three concrete changes before export and sharing.

## Q22. What could leak? --- notebook metadata and embedded resources (Security review · Advanced · 4 points)

Before publishing a notebook-derived HTML report, a reviewer checks the
visible plots but does not inspect notebook metadata, hidden cell
outputs, embedded Plotly data, or linked resources. The report is
intended for public release.

Describe a pre-publication review that covers at least four of these
surfaces. Explain why `nbstripout` is useful but not a complete security
boundary, and distinguish a clean committed notebook from a safe
rendered report.

------------------------------------------------------------------------

# Phase D --- Communication, reports, and dashboards

## Q23. Make a figure self-contained (Design · Intermediate · 4 points)

A figure shows daily p95 latency, but it has the title "Latency," no
unit on the y-axis, no date range, no sample size, and no source/version
note. Propose a title, subtitle or caption, axis label, and
footnote/source line that would let a reader interpret the figure
without reading the notebook. You may invent a clearly labelled
synthetic source name and data version.

## Q24. Choose and justify an export format (Production judgement · Intermediate · 4 points)

For each target, recommend an export format and one relevant setting or
check:

1.  A figure for a two-column research paper.
2.  A figure embedded in a web page where broad viewer compatibility
    matters.
3.  A report appendix where readers need to zoom and print cleanly.

Explain the trade-off between vector and raster formats. Do not assume
that DPI alone controls the quality of vector output.

## Q25. Design a one-page pipeline-health dashboard (Design · Advanced · 4 points)

Design a lightweight one-page dashboard for synthetic pipeline runs.
Required metrics: success rate, p95 duration, data freshness, row-count
anomaly count, and failure breakdown. Explicitly design at least five
visuals/KPI elements and state the operational decision each supports.
Also state:

-   the order and purpose of the visual sections;
-   the default time window, units, last-updated information, and one
    useful filter;
-   how you would handle empty, stale, or failed data;
-   one way to avoid sending raw sensitive rows to the browser.

Aim for a clear hierarchy and no more than 6--8 visuals. Alternatives to
a particular dashboard framework are acceptable.

## Q26. Metric dictionary entries (Documentation · Advanced · 4 points)

Write dictionary entries for **success rate** and **p95 duration** for
the dashboard in Q25. Each entry must include: name, definition/formula,
unit, source, owner, refresh/freshness expectation, and at least one
caveat. Use this synthetic schema:

-   `run_id`: unique run identifier
-   `status`: one of `success`, `failed`, `cancelled`
-   `duration_seconds`: positive duration for completed runs
-   `finished_at`: UTC timestamp
-   `pipeline`: pipeline name

Define how cancelled runs are treated in the success-rate denominator.
For p95 duration, state which runs are included and how you handle
missing/invalid duration values.

## Q27. What is misleading here? --- denominator and freshness (Chart critique · Advanced · 4 points)

A dashboard says "Success rate: 99.5%" but shows no numerator,
denominator, date range, data freshness, or treatment of cancelled runs.
The backing query returns 199 successes and 200 denominator rows for the
last 90 days. The source has `success`, `failed`, and `cancelled` statuses,
but the query's treatment of cancelled runs is undocumented. The latest
data is 36 hours old, though the dashboard implies it is live.

Identify at least three interpretability or trust issues. Propose a
revised display, name one reconciliation check against the source-of-
truth table/query, and explain why the number alone is not enough to
support an operational decision.

## Q28. Accessibility repair plan (Design critique · Intermediate · 4 points)

An existing chart has red and green lines with no markers, a tiny
7-point legend, a title that only says "Results," faint grey text on a
white background, and no text summary or data table. Give at least five
specific accessibility or communication fixes. Include at least one fix
that does not depend on colour and one alternative for people who cannot
inspect the image.

## Q29. Validate a report build and visual regression (Production judgement · Advanced · 4 points)

A team generates figures manually from a notebook and pastes them into a
PDF. A release changes a helper function, but nobody notices that the
y-axis units changed from milliseconds to seconds. Propose a
reproducible build and test workflow that would help catch this. Include
data/version provenance, a figure or data assertion, an image-comparison
test, CI artifact handling, and one limitation of golden-image tests.

## Q30. Dashboard overload and false precision (Design critique · Advanced · 4 points)

A dashboard has 22 charts, inconsistent colours for the same status, p95
values printed to six decimal places, no caveats, no sample counts, and
ten filters that can be combined arbitrarily. Its landing view has no
stated takeaway or default date range.

Identify at least four problems and propose a prioritized redesign.
Explain how you would retain useful drill-down without turning the
landing page into an unstructured chart gallery.

------------------------------------------------------------------------

# Answer key and explanations

Answers below are model answers, not the only acceptable responses. For
design questions, award credit for equivalent choices when the reasoning
is explicit, the chart answers the stated question, and the proposed
design does not distort the data. Code examples assume the versions
stated near the top of this file.

## Phase A --- answers

### Q1

-   **Figure:** the top-level canvas/container for the whole
    composition; it can contain multiple Axes.
-   **Axes:** an individual plotting area with its data coordinate
    system and methods such as `plot`, `scatter`, `set_title`, and
    `set_xlabel`.
-   **Axis:** the x- or y-axis object responsible for scale, ticks, and
    tick labels. It is distinct from `Axes`.
-   **Artist:** a drawable object in the Figure/Axes hierarchy, such as
    a `Line2D`, `Text`, `Rectangle`, or patch.

The object-oriented form keeps a direct reference to the intended Axes,
makes subplot routing explicit, is easier to test, and avoids dependence
on whichever Axes is current in the `pyplot` state machine. Award full
credit when the answer captures the hierarchy and explains the
state-management benefit.

### Q2

The second series uses `plt.plot`, which targets the current Axes rather
than explicitly targeting `axes[1]`. The explicit `plt.sca(axes[0])`
makes the current Axes the left panel, so the throughput line is
deterministically drawn on the wrong panel. In production code, such
state can also be changed by earlier plotting calls or helper functions.

``` python
import matplotlib.pyplot as plt

latency_ms = [20, 24, 22]
throughput_rps = [100, 120, 115]
minute = [1, 2, 3]

fig, axes = plt.subplots(1, 2, figsize=(8, 3), constrained_layout=True)
axes[0].plot(minute, latency_ms, marker="o", label="latency")
axes[1].plot(minute, throughput_rps, marker="s", label="throughput")
axes[0].set(title="Latency", xlabel="minute", ylabel="ms")
axes[1].set(title="Throughput", xlabel="minute", ylabel="requests/s")
plt.close(fig)  # appropriate after saving/using the figure in a batch loop
```

`plt.close(fig)` is a suitable cleanup step after the figure has been
saved or otherwise consumed. In an interactive notebook, close only when
the figure is no longer needed. The main fix is explicit
`axes[1].plot(...)`; layout changes are optional.

### Q3

One valid implementation:

``` python
import matplotlib.pyplot as plt

def plot_duration(minutes, duration_ms, *, ax=None):
    if ax is None:
        _, ax = plt.subplots()
    ax.plot(minutes, duration_ms, marker="o")
    ax.set_xlabel("Elapsed time (minutes)")
    ax.set_ylabel("Duration (ms)")
    ax.set_title("Duration over time")
    return ax
```

It creates an Axes only when needed and returns the actual Axes used. A
caller can pass an existing Axes to compose a grid or test the line data
and labels. The function does not show or save the figure, leaving those
responsibilities to the caller. Creating a new figure only when
`ax is None` is the key behavior.

A complete synthetic caller example (equally spaced minutes) is:

```python
import numpy as np
import matplotlib.pyplot as plt

minutes = list(range(10))
duration_ms = [18, 20, 19, 24, 26, 40, 35, 28, 23, 21]
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(minutes, duration_ms, marker="o", label="run duration")
rolling_3 = np.convolve(duration_ms, np.ones(3) / 3, mode="valid")
ax.plot(minutes[2:], rolling_3, label="trailing 3-run mean")
ax.axvspan(4, 6, color="orange", alpha=0.2, label="incident window")
p95_ms = np.percentile(duration_ms, 95)
ax.axhline(p95_ms, color="crimson", linestyle="--", label="overall p95")
ax.set(xlabel="Elapsed time (minutes)", ylabel="Duration (ms)",
       title="Synthetic pipeline-run duration")
ax.legend()
fig.savefig("duration.svg", bbox_inches="tight")
fig.savefig("duration.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

The rolling mean is trailing and aligns to the last sample in each
three-run window. With irregular timestamps, sort first and choose a
time-based window (or resample explicitly); a fixed number of rows does
not represent a fixed elapsed duration. Label the p95 population/window;
this example draws one overall percentile, not a time-varying p95.

### Q4

The truncated y-axis exaggerates a 2-percentage-point difference; the
title overstates the evidence. A stronger design uses a bar axis
starting at zero, or a clearly labelled point/dot plot with a visible
scale and direct values. State the difference as **2 percentage
points**, not "2 percent" unless relative change is intended. A
truncated axis is not categorically forbidden: it can be acceptable for
some non-bar displays when the truncation is explicit, the scale is not
deceptive, and the visual encoding does not imply a false magnitude. For
bars, a zero baseline is normally important because length encodes
magnitude.

### Q5

Pie slices encode parts of a whole, but the five daily p95 values are
time-ordered measurements, not components of one total. Use a line chart
or dot plot with date on x and p95 duration in seconds on y; add a
vertical deployment marker at 12 October and, if meaningful, a
target/SLO line. Add the date range and sample counts/number of runs
contributing to each percentile, and explain any known data-quality
caveat. The key is to preserve temporal order and make the deployment
context visible without claiming causation from visual proximity alone.

### Q6

Possible choices:

1.  **Sorted horizontal bar chart** for eight failure counts; labels
    remain readable and rank is easy to compare.
2.  **Histogram** for the latency distribution/tail; a box plot can
    summarize spread but hides much of the tail shape.
3.  **Line chart** or time-series bar chart for daily volume, with an
    annotated/shaded incident window (`axvspan` or similar).
4.  **Scatter plot** for file size versus duration, with transparency if
    points overlap; a hexbin or binned aggregation can help if
    overplotting is severe.
5.  **Rate dot/bar chart with denominators** for incident rates by
    country; show the numerator and population/exposure denominator, and
    do not compare raw counts as if country sizes were equal. A map may
    add geographic context but can make precise ranking harder.
6.  **Line or point estimates with explicitly defined error bars/CI
    bands** for the daily estimated metric. State the interval meaning
    and sample size; do not present a confidence interval as the range of
    individual observations.

A valid alternative should match the analytical question and explain its
trade-off. Example: a table is precise for exact counts but makes the
ranking pattern slower to scan than a sorted bar chart.

### Q7

`sharey=True` gives both Axes a shared y-scale for counts, making bar
heights/count scales comparable. As written, the histogram bin edges are
chosen independently, so bins may not align; that makes direct shape
comparison harder. Supply the same explicit bin edges to both calls, for
example:

``` python
bins = [0, 5, 10, 15, 20, 25, 30]
axes[0].hist(region_a_ms, bins=bins)
axes[1].hist(region_b_ms, bins=bins)
```

If the lists are the same as the question, define
`region_a_ms = [10, 11, 12, 12, 13]` and
`region_b_ms = [10, 12, 14, 16, 25]`. Alternatively, state that bin
alignment is required for a meaningful comparison. `sharey=True` alone
does not guarantee equal bin edges.

### Q8

The rainbow palette imposes perceptually uneven colour changes on a
nominal category; use a small, distinct qualitative palette plus direct
labels or markers/linestyles. Independently rescaling two y-axes can
make lines overlap by construction, so apparent alignment is not
evidence of association and certainly not causation. Prefer aligned
small multiples with clearly labelled scales or plot normalized values
only if the normalization is explicitly defined and answers the intended
question. If association matters, inspect the paired data with a
suitable plot and analysis; do not infer it from a dual-axis overlay.

## Phase B --- answers

### Q9

The columns `region_a_ms` and `region_b_ms` each store a separate
variable/series, so this is wide data. One tidy representation is:

  day   region       duration_ms
  ----- ---------- -------------
  Mon   region_a              20
  Mon   region_b              24
  Tue   region_a              23
  Tue   region_b              22
  Wed   region_a              21
  Wed   region_b              25

Each row is one day-region observation, and `region` can map to `hue`
while `duration_ms` maps to `y`. Long/tidy data makes grouping and
semantic mappings explicit and scales more easily when new regions
appear. Wide data can still be convenient for some direct Matplotlib
calls; the representation should serve the operation.

### Q10

Use a figure-level function such as `sns.displot(..., col="region")` for
faceting because it creates/manages its own FacetGrid and multiple
panels. Use an axes-level function such as
`sns.scatterplot(..., ax=existing_ax)` to draw into an Axes already
placed in a Matplotlib layout. A figure-level function generally owns
the grid/layout it creates; it does not accept an arbitrary pre-existing
Axes in the same way, so combining it with an existing custom
multi-panel figure requires planning the composition rather than
treating it as a drop-in Axes method.

### Q11

For Seaborn 0.13.x, `sns.lineplot` by default estimates a mean and
displays an uncertainty interval around the estimate; the default
`errorbar` setting is a confidence interval (typically a 95% bootstrap
confidence interval for the estimator). It is not automatically a range
containing 95% of individual requests, a guarantee for future values, or
necessarily a standard-deviation band. `errorbar=None` removes the
interval; `errorbar="sd"` shows a standard-deviation interval rather
than a confidence interval. Explicitly configure the estimator/errorbar
to match the question, and report sample size or explain uncertainty
because a narrow band based on few observations may be easy to
overinterpret. Credit should reflect the distinction between uncertainty
in an estimate and the distribution of observations.

### Q12

For the scheduled, publication-ready PNG, Seaborn/Matplotlib is a strong
default: static output is easy to include in a reproducible report,
version, and visually review. For hover/zoom/run-level inspection,
Plotly is appropriate because browser interactivity is central to the
task. Trade-offs include: Plotly static export may need an additional
export engine/configuration such as Kaleido; interactive HTML can expose
embedded data and metadata; Matplotlib/Seaborn static output is less
interactive but easier to archive as a fixed artifact; rendering can
vary with fonts/browser or library versions. Neither choice is
universal---the audience and output contract decide.

For the same field mapping, one minimal pair is:

```python
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Assumes one pre-aggregated row per day/pipeline, already filtered.
fig, ax = plt.subplots(figsize=(7, 3.5))
sns.lineplot(data=df, x="day", y="p95_seconds", hue="pipeline", ax=ax, errorbar=None)
ax.set(xlabel="Day (UTC)", ylabel="p95 duration (seconds)")
fig.savefig("daily-p95.png", dpi=180, bbox_inches="tight")

interactive = px.line(
    df, x="day", y="p95_seconds", color="pipeline",
    labels={"day": "Day (UTC)", "p95_seconds": "p95 duration (seconds)"},
)
interactive.write_html("daily-p95.html", include_plotlyjs=True)
```

The example assumes the caller has already defined and privacy-reviewed
`df`; it deliberately excludes run IDs and customer fields. The two
outputs should use the same filtering, aggregation, units, and category
ordering before comparing them.

### Q13

The caption assigns a specific future-observation coverage
interpretation that the author has not established. The default lineplot
band concerns uncertainty around the plotted estimator, not a prediction
interval for individual future requests. Check the installed Seaborn
version, estimator, grouping, number of observations, and exact
`errorbar` configuration; set it explicitly (for example, a confidence
interval or standard deviation if that is the intended summary) and
label it accurately. If the goal is a range for individual observations
or future values, the default confidence band is not sufficient. Include
methodology and sample size/caveats rather than promising coverage.

### Q14

Plausible PNG-export causes include: (1) a static image export engine
such as Kaleido is missing or incompatible on the CI runner; install/pin
and smoke-test the required dependency in the locked environment. (2)
the CI environment differs in Plotly/browser or system dependencies, or
the figure/data is invalid; pin the environment, add a minimal export
smoke test, and inspect the actual error rather than assuming one cause.
(3) file permissions or output paths may be wrong; create the target
directory and test the path. For HTML, review embedded/hover data for
PII/secrets, validate that required resources are included or
intentionally linked, and test opening the artifact in a clean
environment. Static export should be treated as a separately tested
build target.

## Phase C --- answers

### Q15

The chart cell refers to `ax` without any cell creating it, and the
saved chart output may be stale. Cell 3 also needs to run after the data
preparation cell that creates `duration_seconds`. A minimal repair is:

``` python
import pandas as pd
import matplotlib.pyplot as plt

runs = pd.DataFrame({"day": ["Mon", "Tue"], "duration_ms": [20, 40]})
runs["duration_seconds"] = runs["duration_ms"] / 1000
fig, ax = plt.subplots()
ax.plot(runs["day"], runs["duration_seconds"], marker="o")
ax.set(xlabel="Day", ylabel="Duration (seconds)", title="Duration by day")
plt.show()
```

In a real notebook, split setup, data preparation, and plotting into
ordered cells, then use Restart Kernel and Run All. Saved outputs record
an earlier execution and can remain after code changes; they do not
prove that the current source cells run from a clean state.

### Q16

Move the calculation into a function such as `daily_success_rate(runs)`
in a module, with documented denominator rules and validation. Test the
calculation using a tiny deterministic DataFrame and known expected
output, for example
`assert daily_success_rate(sample) == expected_rate`. The notebook
should import the function, load or receive data, call it, and display
the result/figure without duplicating business logic. Add a CI check
that executes the notebook from a fresh kernel (for example, `nbmake` or
`nbconvert --execute`) and run unit tests separately. Keep plotting
smoke tests or artist-data assertions for key visual properties. Good
answers separate reusable logic from exploration and mention
deterministic inputs. Two diff-review practices include pairing the
`.ipynb` with a Jupytext `py:percent` file and synchronizing it in CI, and
stripping volatile outputs/execution counts with `nbstripout` while
reviewing the actual source diff. `nbstripout` is hygiene, not secret
scanning or a guarantee that source cells and metadata are safe.

### Q17

A valid parameter cell is:

``` python
report_date = "2026-10-12"
output_dir = "build"
```

Tag the cell with `parameters`. A valid command is:

``` bash
papermill notebooks/daily_report.ipynb build/2026-10-12.ipynb \
  -p report_date 2026-10-12 \
  -p output_dir build
```

Papermill injects supplied values after the tagged parameters cell
(using a parameter-injection cell) and executes the notebook; the second
positional argument is the executed notebook output path. The tag is how
Papermill identifies the cell whose defaults can be overridden. If
`build/` might not exist, create it in the CI step first (for example,
`mkdir -p build`).

For three dates, a POSIX-shell CI step can loop over a fixed allowlisted
date list and use a unique output path per date, for example:

```bash
set -eu
mkdir -p build/html
for day in 2026-10-10 2026-10-11 2026-10-12; do
  papermill notebooks/daily_report.ipynb "build/daily-${day}.ipynb" \
    -p report_date "$day" -p output_dir build
  jupyter nbconvert --to html --no-input \
    "build/daily-${day}.ipynb" --output "daily-${day}.html" \
    --output-dir build/html
done
```

Upload only reviewed HTML outputs as access-controlled CI artifacts with
an explicit retention policy; avoid uploading raw executed notebooks if
they may contain sensitive outputs. For repeatability, pin the environment,
use immutable/versioned input data, and fail rather than overwrite an
existing run artifact unless overwrite is explicitly intended.

### Q18

The `.ipynb` can retain output data even after the source cell is
deleted. Inspect notebook JSON and rendered outputs, clear sensitive
outputs, and review the diff before committing. Use `nbstripout` or a
controlled clear-output step as a commit hygiene measure, then re-run
from a clean kernel and confirm the committed notebook has no sensitive
outputs. If data was already committed or shared, follow the
repository's incident/remediation process and assess history/artifact
exposure; deleting a visible cell does not remove data from Git history
or copies. Output stripping does not delete the original source table
and does not change access permissions.

### Q19

Review cell outputs, tracebacks, execution metadata, notebook diffs,
generated HTML, CI logs, and any copied artifacts---not just current
source code. Clear the output and verify the serialized notebook and
rendered exports. If a real credential was exposed, treat it as
compromised: revoke/rotate it promptly, inspect access/use where
appropriate, and prevent recurrence by using a secret
manager/environment injection and redaction. Removing the displayed text
from the latest file alone does not invalidate a leaked credential or
erase all copies.

### Q20

At least three risks and matching controls:

1.  **Bearer token in Papermill parameters/logs:** do not pass secrets
    as logged notebook parameters; retrieve credentials from a secret
    store/environment at runtime, restrict log contents, and redact
    where possible.
2.  **Executed notebook output contains emails:** minimize or aggregate
    data, suppress or mask identifying fields, clear/review outputs
    before publication, and do not retain unsafe executed notebooks as
    general artifacts.
3.  **Artifact is accessible too broadly or retained indefinitely:**
    restrict CI artifact permissions, apply a retention limit, and
    separate trusted/internal artifacts from public release outputs.
4.  **HTML derived from the executed notebook may embed the same data:**
    inspect the rendered artifact and embedded data, not just the source
    notebook.
5.  **Staging access is over-privileged:** use least-privilege
    credentials and only the required data scope. Any three with clear
    path-to-control mapping earn full credit.

### Q21

Standalone HTML can include the plot's data and hover strings directly
in the file; it is not protected by server-side authorization after
being sent. Before sharing: remove or pseudonymize identifiers; exclude
email and free text unless specifically approved; aggregate or sample
safely and suppress small groups; inspect hover fields and serialized
HTML/embedded data; define recipient/access and retention; and verify no
secret appears in metadata or linked resources. A `ticket_id` may itself
be identifying in context. The fact that the file is static or "only a
chart" does not remove the privacy risk.

### Q22

A sound review includes: (1) inspect `.ipynb` JSON, metadata, all cell
outputs and tracebacks; (2) inspect the actual rendered HTML, including
embedded Plotly payloads, images and hidden hover fields; (3) scan
source and generated artifacts for tokens, credentials, emails, IDs and
other sensitive fields; (4) review linked/embedded resources and whether
the report fetches external data; (5) verify public-release permissions
and metadata; (6) render from a clean, reviewed notebook and check the
final artifact. `nbstripout` helps prevent accidental committed cell
outputs, but does not guarantee source code, metadata, generated HTML,
embedded interactive data, logs, Git history, or linked resources are
safe. A clean source notebook and a safe rendered report are different
review targets.

## Phase D --- answers

### Q23

One strong example:

-   **Title:** "Pipeline p95 duration rose after the 12 October
    deployment" (use only if the data actually supports this finding).
-   **Subtitle:** "Daily p95 duration, 8--15 Oct 2026; 48--63 completed
    runs/day; UTC."
-   **Y-axis:** "p95 duration (seconds)".
-   **Source/footnote:** "Source: synthetic `pipeline_runs` fixture,
    data version `demo-v1`; p95 calculated over completed runs per UTC
    day; cancelled runs excluded; generated by
    `reports/daily_latency.py`."

The title should state a supported takeaway, not overclaim causality. A
self-contained figure needs scope, units, source/version, and important
denominator or method notes; a date range and sample count help readers
judge representativeness. Other clear wording is acceptable.

### Q24

1.  **Two-column research paper:** PDF or SVG vector output when the
    downstream publisher supports it; set `figsize` to the final column
    width and check embedded fonts and line/text sizes.
2.  **Web page:** PNG is a broadly compatible raster choice; set
    adequate pixel dimensions/DPI and inspect legibility at the
    displayed size. SVG can also be suitable if the publishing
    environment supports it.
3.  **Appendix needing zoom and print:** PDF or SVG vector output,
    checking fonts, clipping, and print rendering.

Vector formats preserve scalable paths/text and are often preferable for
line art; raster formats are pixel-based and depend on pixel
dimensions/DPI. DPI chiefly affects rasterization and raster output; it
does not by itself determine vector path quality. The final export
should be inspected in its target environment.

### Q25

A strong layout has at least five purposeful elements: (1) success-rate
KPI for reliability, (2) p95-duration trend with an SLO line for latency,
(3) freshness/last-updated indicator for data currency, (4) row-count
anomaly count/trend for completeness, and (5) failure breakdown by stage
or reason for triage. Place top-line KPIs first, then trends, then the
failure breakdown and a compact details/drill-down section. Use a default such as the last 7 complete
UTC days, label seconds/percent/counts, show `last updated` and data
coverage, and provide a pipeline filter. Empty data should show "No data
for this window," stale data should show a visible stale warning, and
source failures should produce a clear error state rather than silently
displaying old values as current. Aggregate or sample server-side; do
not send raw rows or unnecessary identifiers to the browser. Keep the
landing view to roughly 4--6 visuals and make filters and caveats
visible. A clear Streamlit, Dash, Panel, or other lightweight
implementation can be valid.

### Q26

Example entries (the exact owner/source names can be synthetic but must
be stated):

  ------------------------------------------------------------------------------------------
  Field                   Success rate                     p95 duration
  ----------------------- -------------------------------- ---------------------------------
  Name                    `pipeline_success_rate`          `pipeline_duration_p95_seconds`

  Definition              `success / (success + failed)`   95th percentile of valid positive
                          among eligible completed runs in `duration_seconds` for runs with
                          the selected window; exclude     `status` in `success` or `failed`
                          `cancelled` from numerator and   and a valid `finished_at` in the
                          denominator                      selected window

  Unit                    Percent (%)                      Seconds (s)

  Source                  Versioned `pipeline_runs` table  Same source

  Owner                   Data Platform on-call / named    Data Platform on-call / named
                          team                             team

  Refresh                 Every 15 minutes; show latest    Every 15 minutes; show latest
                          successful refresh time          successful refresh time

  Caveat                  Cancelled runs are excluded;     Missing, non-finite, zero, or
                          show eligible denominator and    negative durations are excluded
                          window; late-arriving runs can   and counted as data-quality
                          restate the rate                 errors; small samples make p95
                                                           unstable
  ------------------------------------------------------------------------------------------

For a 0--1 rate, multiply by 100 for display and label percent. The
question explicitly requires cancelled runs to be handled; another
policy is possible only if it is explicitly defined and consistently
applied, but the answer must not silently mix definitions. A valid p95
implementation must state population and missing-value handling.

### Q27

Problems include: the denominator is hidden; the 90-day window is not
shown; the dashboard implies live freshness despite data being 36 hours
old; cancelled-run handling is undefined; and the aggregate may hide a
recent failure spike. Do not label the denominator "eligible" until its
status policy is verified. A temporary honest display is "99.5% (199/200
rows under the current query; denominator policy unverified), last 90
days, last refreshed 36 hours ago --- stale," or suppress the KPI until
reconciled. Reconcile the 199 successes and 200 denominator rows against
the authoritative query/table using the same UTC boundaries, status
filter, and late-arrival policy; record the query/data version used. Add
a trend and freshness/coverage indicator, and prevent the UI from implying
live data. One number without denominator, time window, definition, and
freshness is insufficient for an operational decision.

### Q28

Award credit for five distinct, concrete changes. Examples: use a
colourblind-safe palette; add different markers or line styles so colour
is not the only cue; enlarge the legend and use readable typography;
replace "Results" with a descriptive finding and scope; darken
low-contrast text and verify contrast; directly label series where
practical; add alt text or a concise text summary; provide a data table
or downloadable accessible table; use clear units and dates; ensure a
web view supports keyboard navigation. The answer must include a
non-colour cue and a text alternative/table. Accessibility is not solved
by changing colours alone.

### Q29

A good workflow versions the source data or records a stable data
version/run ID; stores metric definitions and the code revision;
generates figures and report from one command such as `make report`;
runs unit/data assertions (for example, assert the y-axis label is
`Duration (ms)` or test that the plotted values match expected
milliseconds); runs a `pytest-mpl`-style image comparison with reviewed
baseline and tolerances; and uploads generated report/figures as
access-controlled CI artifacts with appropriate retention. A
golden-image test can be brittle across fonts, OSs, backends, and
library versions, and can miss semantic errors if the baseline itself is
wrong. Pair visual comparison with data/label assertions and inspect
intentional baseline changes.

### Q30

Problems include: too many visuals without hierarchy; inconsistent
status colours; false precision; no sample size or caveats;
unconstrained combinations of filters that invite cherry-picking; no
takeaway/default time window; and no indication of freshness. Prioritize
a concise landing page with a stated purpose, 4--6 key visuals in a
hierarchy (KPIs, trends, breakdown), consistent colour semantics,
rounded values with units, sample counts/denominators, freshness, and a
caveats/methodology link. Set a meaningful default date range and make
filters explicit. Retain detail through drill-down, tabs, or a separate
details view with guardrails rather than placing every possible slice on
the landing page. A dashboard should support a defined decision, not
maximize chart count.

------------------------------------------------------------------------

# Scoring rubric

Each question is worth **4 points**; maximum score is **120 points**.
Score the reasoning and correctness, not exact wording.

  -----------------------------------------------------------------------
                        Score per question Criteria
  ---------------------------------------- ------------------------------
                          **4 --- Strong** Correct, complete response;
                                           explains why; code is valid or
                                           design choices are well
                                           justified; relevant
                                           risks/trade-offs are covered.

                       **3 --- Competent** Core answer is correct; one
                                           secondary detail,
                                           justification, or safeguard is
                                           missing.

                         **2 --- Partial** Some correct concepts, but a
                                           material omission or unclear
                                           reasoning remains; code/design
                                           would need meaningful
                                           revision.

                         **1 --- Limited** Recognizes part of the issue
                                           but the proposed fix is
                                           largely incomplete or
                                           unsupported.

                **0 --- Not demonstrated** Missing, materially incorrect,
                                           or unsafe answer.
  -----------------------------------------------------------------------

For code questions, reserve full credit for code that addresses the
stated task and uses explicit axes/parameters appropriately; minor
formatting differences are irrelevant. For privacy questions, full
credit requires identifying the disclosure path and a control that
addresses it. For chart critiques, full credit requires both identifying
the misleading mechanism and proposing a design that still answers the
question.

### Point allocation for multi-part questions

Use these allocations to keep grading consistent; accept equivalent
solutions that preserve the stated semantics.

- **Q3 (4):** helper contract and Axes return (1); rolling-window semantics
  (1); incident span and correctly defined p95 reference (1); SVG/PNG
  export and batch cleanup (1).
- **Q6 (4):** chart choice and fit for each of six scenarios (0.5 each);
  two plausible alternatives with a valid reason for rejecting them (1).
- **Q12 (4):** appropriate library choice and equivalent field mapping
  (1); runnable/credible static call (1); interactive call and export
  (1); trade-offs and privacy handling (1).
- **Q16 (4):** module/notebook separation (1); meaningful unit assertion
  (1); two reviewable-diff practices (1); fresh-kernel CI execution check
  (1).
- **Q17 (4):** parameter cell/tag and single-date command (1.5); three-date
  CI loop and HTML export (1.5); access/retention and non-overwrite or
  idempotency safeguard (1).
- **Q25 (4):** five purposeful visual/KPI elements and hierarchy (1.5);
  time window/units/freshness/filter and empty/stale/error states (1.5);
  server-side aggregation or other privacy control (1).
- **Q29 (4):** versioned data/build provenance (1); semantic/data assertion
  (1); image comparison with tolerance (1); controlled artifact handling
  and a limitation of golden images (1).

## Mastery thresholds

-   **108--120 (90--100%) --- Strong mastery:** ready to apply the
    module's patterns independently; still review any missed safety or
    reproducibility item.
-   **96--107 (80--89%) --- Operationally competent:** core skills are
    sound; revise the phase(s) where points were lost.
-   **78--95 (65--79%) --- Developing:** revisit lessons and repeat the
    relevant coding/design questions before using the workflow for
    shared reports.
-   **0--77 (below 65%) --- Rebuild foundations:** revisit the module in
    phase order and redo the questions with runnable examples.

**Safety/reproducibility guardrail:** Regardless of total score, review
Phase C if any of Q18--Q22 receives fewer than 3 points, and review
Phase A/B if you cannot explain the Matplotlib state bug or Seaborn band
semantics. A high aggregate score does not offset an unsafe export
workflow.

------------------------------------------------------------------------

# Final coverage checklist and traceability

Use this checklist to confirm that the roadmap outcomes have been
demonstrated. Mark an item complete only after answering the listed
questions and reviewing mistakes.

-   [ ] **Figure, Axes, Axis, Artist hierarchy and object-oriented
    plotting:** Q1--Q3, Q7.
-   [ ] **Correct Axes routing; figure lifecycle and reusable helpers:**
    Q2--Q3, Q29.
-   [ ] **Chart choice by analytical question and data shape:** Q5--Q7,
    Q9.
-   [ ] **Misleading design, scale integrity, colour, dual axes,
    denominator and false precision:** Q4--Q5, Q8, Q13, Q27, Q30.
-   [ ] **Tidy versus wide data; Seaborn semantics and
    figure-level/axes-level APIs:** Q9--Q10.
-   [ ] **Error-band interpretation and configuration:** Q11, Q13.
-   [ ] **Plotly versus static plotting and export strategy:** Q12, Q14,
    Q21--Q22, Q24.
-   [ ] **Notebook hidden state, ordered execution, modularization, and
    tests:** Q15--Q16, Q29.
-   [ ] **Papermill parameters and execution artifact:** Q17, Q20.
-   [ ] **`nbstripout`, saved outputs, secrets, PII, metadata,
    interactive HTML and CI artifacts:** Q18--Q22.
-   [ ] **Self-contained report figures, formats, reproducible
    generation and provenance:** Q23--Q24, Q29.
-   [ ] **Dashboard hierarchy, empty/stale/error states, and
    source-of-truth checks:** Q25--Q27, Q30.
-   [ ] **Metric dictionary, definitions, ownership, freshness and
    caveats:** Q26--Q27.
-   [ ] **Accessibility and alternatives to colour-only encoding:** Q28.
-   [ ] **CI execution, visual regression, and artifact handling:**
    Q16--Q17, Q20, Q29.
-   [ ] **Scope respected: no Stage 4 experimental-statistics exam,
    Stage 2 BI/serving implementation, or heavy Stage 5--6 ML
    plotting:** all questions remain within Module 1.21 outcomes.

## Required item audit map

-   **Five "What is misleading here?" items:** Q4, Q5, Q8, Q13, Q27.
-   **Five "What could leak?" items:** Q18, Q19, Q20, Q21, Q22.
    *(Exactly five are explicitly marked.)*
-   **Broken Matplotlib wrong-axes script:** Q2.
-   **Pipeline duration recipe (rolling mean, incident span, p95, SVG+PNG):** Q3.
-   **Chart choice and critique:** Q4--Q8; Q6 includes six selection scenarios and explicitly includes geography/rates and uncertainty.
-   **Tidy/wide and Seaborn API choice:** Q9--Q10.
-   **Seaborn error-band interpretation/configuration:** Q11, Q13.
-   **Plotly/Seaborn trade-offs:** Q12, Q14.
-   **Notebook hidden state and reproducibility repair:** Q15--Q16.
-   **Papermill parameters cell and valid command:** Q17.
-   **Output stripping, secrets, saved outputs and safe export:**
    Q18--Q22.
-   **One-page dashboard and metric dictionary:** Q25--Q27.
-   **Accessibility:** Q28.

**Roadmap alignment:** The assessment follows Section 3's four phases
and Section 4's requested question types. The lesson self-check work is
traceable as follows: Lesson 01 object model and pipeline-duration export
(Q1--Q3); Lesson 02 six chart-choice scenarios, misleading-chart repair,
and five dashboard visuals (Q4--Q8, Q25); Lesson 03 Seaborn function
choice, band semantics, and matched static/interactive versions (Q10--Q14);
Lesson 04 hidden state, reviewable diffs, modular tests, and CI execution
(Q15--Q16); Lesson 05 parameter injection, leakage controls, and a
three-date CI/HTML-artifact workflow (Q17--Q22); Lesson 06 self-contained
figures, source-of-truth reconciliation, and automated visual-regression
report build (Q23--Q29). Q30 reinforces the dashboard overload and false-
precision critique. The assessment remains within Module 1.21 scope.
