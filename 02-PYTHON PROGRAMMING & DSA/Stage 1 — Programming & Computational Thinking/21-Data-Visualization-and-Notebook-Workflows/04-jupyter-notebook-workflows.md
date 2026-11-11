# Jupyter Notebook Workflows: From Exploration to Reproducible Analysis

> **Stage 1 · Module 1.21 · Lesson 04**  
> **Target:** Python 3.12+, JupyterLab 4 or VS Code notebooks, and a project-managed environment. Examples use small synthetic data.  
> **Scope boundary:** This lesson covers notebook craft, environments, review, testing, and safe collaboration. Lesson 05 covers detailed Papermill parameterized execution and `nbstripout` mechanics.

## 1. Learning outcomes and the role of notebooks

By the end, you should be able to explain kernels and `.ipynb` structure; select the intended environment; structure a readable, top-to-bottom analysis; diagnose hidden state; move reusable logic into tested modules; review notebook diffs; manage dependencies, paths, outputs, memory, and secrets; test notebook execution in CI; profile slow cells; compare notebook alternatives; and apply basic security controls.

A notebook is an **executable explanation**: prose explains why each step exists, code makes the analysis inspectable, assertions expose assumptions, and a fresh-kernel run tests whether the result depends on forgotten state. Notebooks are effective for exploration, teaching, and evidence-rich reports. They are not automatically reliable pipelines: cells may run out of order, outputs can become stale, and saved outputs can contain sensitive data.

Use notebooks to explore and communicate. Move stable reusable transformations into tested Python modules. Move scheduled, long-running, retryable, or SLA-bound work into scripts/packages and orchestrated jobs. Render a report when readers need a stable artifact rather than a live kernel.

## 2. Environment and kernel mental model

### 2.1 Document versus process

A `.ipynb` file is JSON containing cells, source, metadata, execution counts, and outputs. A **kernel** is a separate process that executes code and retains Python objects in memory. Saving the document does not save a complete snapshot of the live kernel.

- **Code cells** execute in the kernel.
- **Markdown cells** render prose, headings, links, tables, and LaTeX such as `\\(O(n \\log n)\\)` or `\\[\\bar{x}=\\frac{1}{n}\\sum_{i=1}^{n}x_i\\]`.
- **Raw cells** are not interpreted as Markdown by the notebook renderer.
- **Execution counters** such as `In [7]` show execution order in the current session, not document order.
- **Outputs** are saved in the notebook and can remain after their source is edited or deleted.

Simplified `.ipynb` fragment (illustrative, not a complete notebook):

```json
{
  "cells": [
    {
      "cell_type": "code",
      "execution_count": 1,
      "metadata": {},
      "outputs": [],
      "source": ["value = 2 + 2\\n", "print(value)"]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": ["# A small calculation"]
    }
  ],
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 5
}
```

Real notebooks also contain cell IDs, language information, and output structures. Treat `.ipynb` as **source code and a possible data container**.

### 2.2 JupyterLab and VS Code environment selection

Open the repository root, create/activate its documented environment, install declared dependencies, select the matching kernel, and verify the interpreter before analysis.

**Terminal — create a new environment with `uv` (for a new project):**

```bash
uv init notebook-workflow-demo
cd notebook-workflow-demo
uv python pin 3.12
uv add pandas numpy matplotlib jupyterlab ipykernel
uv add --dev pytest ruff nbqa nbmake nbval jupytext nbstripout
uv sync
```

For an existing project, use its committed `pyproject.toml` and lock file rather than reinitializing it.

**Terminal — launch JupyterLab:**

```bash
uv run jupyter lab
```

**Terminal — register the active environment as a named kernel if it is missing from the UI:**

```bash
uv run python -m ipykernel install --user --name notebook-workflow-demo --display-name "Python (notebook-workflow-demo)"
```

This creates a project-local environment and records dependencies in the project metadata/lock file. Commit both files; recreate the environment from them on another machine rather than copying the virtual environment directory.

A one-off environment pattern is also available:

```bash
uv run --with ipykernel python -m ipykernel install --user --name myproj --display-name "Python (myproj)"
```

In VS Code, use the notebook kernel/interpreter picker. In JupyterLab, use the kernel selector. A matching display name is not proof that the correct interpreter is selected.

**Notebook code cell — check the actual environment:**

```python
import sys
from importlib import metadata

print("Python executable:", sys.executable)
print("Python version:", sys.version.split()[0])
for package in ("ipykernel", "numpy", "pandas", "matplotlib"):
    try:
        print(f"{package}: {metadata.version(package)}")
    except metadata.PackageNotFoundError:
        print(f"{package}: not installed in this kernel")
```

If the environment is moved or deleted, its registered kernelspec may point to a missing interpreter; recreate or remove the stale kernel as appropriate.

### 2.3 Useful features and correct command context

Notebook magics are **IPython/Jupyter features, not standard Python syntax**. Do not place them in importable `.py` modules.

| Feature | Context | Purpose |
|---|---|---|
| Markdown/LaTeX | Markdown cell | Explain assumptions, equations, units, conclusions |
| `%timeit expression` | Notebook code cell | Repeated timing for a short expression |
| `%%time` | First line of a code cell | Rough wall time for one cell execution |
| `%load_ext autoreload`, `%autoreload 2` | Notebook code cell | Reload changed modules during exploration |
| `%matplotlib inline` | Notebook code cell | Static inline figures; often default |
| `%matplotlib widget` | Notebook code cell | Interactive figures with compatible widget support |
| `object?`, `object??` | Notebook code cell | Help/signature and, when available, source |
| Tab completion | Notebook prompt | Discover names and attributes |
| `!command` | Notebook code cell | Run a shell command, with IPython-specific behavior |
| Variable inspector / outline | IDE UI | Inspect objects and navigate headings |
| Debugger | IDE UI or IPython | Step through code and inspect frames |

**Notebook code cell — examples:**

```python
values = list(range(10_000))
%timeit sum(values)
```

```python
%%time
total = sum(range(1_000_000))
print(total)
```

```python
%load_ext autoreload
%autoreload 2
sum?
```

**Notebook code cell — cautious shell use:**

```python
!python --version
```

Prefer a **terminal** for project commands such as `uv run pytest` and `uv run ruff check .`. Notebook shell commands may use an unexpected working directory/environment; interpolating untrusted text into shell commands can create command-injection risk. Never construct a shell command from raw user input.

### 2.4 Hidden state and the fresh-kernel repair

**Notebook code cell — deliberately broken example:**

```python
observed = [10, 12, 14, 16]
```

Run the cell, then run:

```python
average = sum(observed) / len(observed)
print(average)
```

Delete or edit the first cell so it no longer defines `observed`, but leave the kernel running. The second cell may still succeed because `observed` remains in memory. A fresh kernel fails. Similar problems arise from out-of-order cells, edited source with stale output, stale imported objects, random-number state, and changed working directories.

**Repair workflow:** save; restart the kernel; run all cells top-to-bottom; fix the first failure; repeat from a fresh kernel; check that outputs match current source and data; then inspect for secrets/PII. “Restart & Run All” is a minimum reproducibility test, not proof of analytical correctness or data safety.

## 3. A well-structured notebook walkthrough

Use this sequence, adapting as needed:

1. **Title and purpose:** question, audience, decision supported.
2. **Sources and limitations:** dataset identifier/version, scope, date range, known limitations.
3. **Parameters:** date window, thresholds, sample fraction, filters.
4. **Setup/imports:** project imports, seed, plotting defaults, provenance.
5. **Load:** documented source and portable path.
6. **Clean and validate:** schema, types, missingness, uniqueness, row counts.
7. **Analyse:** transformations, preferably delegated to tested package functions.
8. **Visualise:** labelled figures with units, sample sizes, and takeaways.
9. **Conclusions:** evidence, caveats, what cannot be inferred.
10. **Next steps:** follow-up checks or action.

Use descriptive names such as `01_explore_pipeline_runs.ipynb`. A `notebooks/README.md` should explain purpose, environment, run instructions, data sources, and output/commit policy.

### 3.1 Synthetic example: parameters, validation, analysis

**Notebook code cell — safe synthetic data:**

```python
import random
import numpy as np
import pandas as pd

SEED = 17
SAMPLE_FRAC = 1.0
DATA_VERSION = "synthetic-runs-v1"
random.seed(SEED)
rng = np.random.default_rng(SEED)

runs = pd.DataFrame({
    "run_id": range(1, 101),
    "duration_seconds": rng.gamma(shape=2.5, scale=4.0, size=100).round(3),
    "rows_read": rng.integers(900, 1_100, size=100),
    "status": rng.choice(["success", "failed"], size=100, p=[0.94, 0.06]),
})
if not 0 < SAMPLE_FRAC <= 1:
    raise ValueError("SAMPLE_FRAC must be in (0, 1]")
if SAMPLE_FRAC < 1:
    runs = runs.sample(frac=SAMPLE_FRAC, random_state=SEED)

print(f"Rows: {len(runs)} | data version: {DATA_VERSION} | seed: {SEED}")
runs.head()
```

**Markdown cell — source note:**

> These records are synthetic and generated with seed 17. They do not represent production reliability or latency.

**Notebook code cell — visible data-quality checks:**

```python
assert not runs.empty, "Expected at least one run"
assert runs["run_id"].is_unique, "run_id must be unique"
assert runs["duration_seconds"].notna().all(), "Duration contains missing values"
assert (runs["duration_seconds"] >= 0).all(), "Duration cannot be negative"
assert runs["status"].notna().all(), "Status contains missing values"

quality_summary = {
    "rows": int(len(runs)),
    "missing_duration": int(runs["duration_seconds"].isna().sum()),
    "duplicate_run_ids": int(runs["run_id"].duplicated().sum()),
    "failure_rate": float(runs["status"].eq("failed").mean()),
}
quality_summary
```

**Notebook code cell — summary and figure:**

```python
import matplotlib.pyplot as plt

summary = runs.groupby("status", observed=True)["duration_seconds"].agg(
    ["count", "median", "mean"]
)
display(summary)

fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)
ax.hist(runs["duration_seconds"], bins=15, edgecolor="white")
ax.set(
    title="Synthetic pipeline-run duration distribution",
    xlabel="Duration (seconds)",
    ylabel="Number of runs",
)
plt.show()
plt.close(fig)
```

**Markdown cell — conclusion template:**

> **Finding:** State the observed pattern and magnitude.  
> **Scope:** Include window, filters, sample size, and data version.  
> **Limitations:** Avoid causal claims not supported by the design.  
> **Next step:** Name the next check or decision.

`Path.cwd()` is only reliable if the notebook is launched from the project root. If launch locations vary, define and test a root-path convention rather than silently searching the machine.

## 4. Intermediate: package architecture, Git, dependencies, and data hygiene

### 4.1 One environment per project

Declare dependencies in `pyproject.toml` and commit the lock file. A lock file makes resolution reproducible within package-manager/platform constraints; it does not pin the operating system, external data, credentials, or remote services.

**Notebook code cell — record key library versions:**

```python
import sys
from importlib import metadata

print("Python:", sys.version.split()[0])
for package in ("numpy", "pandas", "matplotlib", "seaborn", "plotly"):
    try:
        print(f"{package}=={metadata.version(package)}")
    except metadata.PackageNotFoundError:
        pass
```

Avoid ad-hoc `!pip install` cells in shared notebooks. They can mutate the wrong environment, leave dependencies undeclared, and surprise collaborators. Add dependencies in a **terminal**, update the lock file, and restart the kernel. If a notebook-only install is unavoidable during local exploration, prefer `%pip` (IPython-aware) over `!pip`, then promote the dependency into project metadata before sharing.

### 4.2 Thin notebook over importable code

Suggested layout:

```text
notebook-workflow-demo/
├── pyproject.toml
├── src/runlens/
│   ├── __init__.py
│   └── analysis.py
├── tests/test_analysis.py
└── notebooks/01_explore_runs.ipynb
```

**File: `src/runlens/analysis.py`**

```python
from __future__ import annotations
import pandas as pd


def summarise_runs(runs: pd.DataFrame) -> pd.DataFrame:
    """Return run counts and median durations grouped by status."""
    required = {"status", "duration_seconds"}
    missing = required.difference(runs.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if runs.empty:
        return pd.DataFrame(columns=["status", "run_count", "median_seconds"])
    if runs["status"].isna().any() or runs["duration_seconds"].isna().any():
        raise ValueError("status and duration_seconds must not contain missing values")
    if (runs["duration_seconds"] < 0).any():
        raise ValueError("duration_seconds must be non-negative")
    return (
        runs.groupby("status", as_index=False, observed=True)
        .agg(
            run_count=("duration_seconds", "size"),
            median_seconds=("duration_seconds", "median"),
        )
        .sort_values("status", ignore_index=True)
    )
```

**File: `src/runlens/__init__.py`**

```python
"""Small helpers for pipeline-run analysis."""
from .analysis import summarise_runs

__all__ = ["summarise_runs"]
```

**File: `tests/test_analysis.py`**

```python
import pandas as pd
import pytest
from runlens import summarise_runs


def test_summarise_runs_groups_and_summarises():
    runs = pd.DataFrame({
        "status": ["success", "success", "failed"],
        "duration_seconds": [2.0, 4.0, 10.0],
    })
    result = summarise_runs(runs)
    assert result["status"].tolist() == ["failed", "success"]
    assert result["run_count"].tolist() == [1, 2]
    assert result["median_seconds"].tolist() == [10.0, 3.0]


def test_summarise_runs_rejects_negative_duration():
    runs = pd.DataFrame({"status": ["success"], "duration_seconds": [-1.0]})
    with pytest.raises(ValueError, match="non-negative"):
        summarise_runs(runs)
```

**Terminal — declare dependencies, editable install, tests:**

```bash
uv add pandas
uv add --dev pytest
uv pip install -e .
uv run pytest
```

This assumes a valid `pyproject.toml` with a build backend and `src/` package discovery. `uv pip install -e .` installs the project into the active environment; it does not declare missing dependencies.

**Notebook code cell — call the tested package:**

```python
%load_ext autoreload
%autoreload 2

import pandas as pd
from runlens import summarise_runs

runs = pd.DataFrame({
    "run_id": [1, 2, 3, 4],
    "status": ["success", "success", "failed", "success"],
    "duration_seconds": [2.0, 4.0, 10.0, 3.0],
})
display(summarise_runs(runs))
```

Editable installation makes local code importable without copying it. Autoreload is a development convenience, not a substitute for tests or a fresh-kernel run.

### 4.3 Paths, output size, memory, and caching

Use `pathlib` and a documented project-root convention rather than machine-specific absolute paths.

```python
from pathlib import Path

project_root = Path.cwd()  # valid only when launched from the project root
sample_path = project_root / "data" / "sample_runs.csv"
```

- Keep large/restricted datasets outside Git; include only approved synthetic fixtures.
- Display `head()`, samples, aggregates, and schema summaries—not entire large tables.
- Use chunked reads, database-side aggregation, or lazy scans when data exceed available memory.
- `del large_frame` releases a reference; `gc.collect()` can help with some objects but does not guarantee release of all native memory.
- Cache expensive deterministic steps only when cache keys include all relevant inputs, code/configuration, and data version. Invalidate when dependencies change. `joblib.Memory` can cache function results on disk, but its cache directory may contain sensitive derived data and must be protected/cleaned according to policy.
- Use documented Parquet checkpoints where appropriate; never assume a cached file is current merely because it exists.

### 4.4 Reviewable notebook diffs

`.ipynb` JSON contains source, outputs, execution counts, and metadata, so diffs can be noisy.

- **`nbstripout`:** strips outputs/selected metadata according to policy. It reduces noise but does not replace secret scanning.
- **Jupytext:** pair the notebook with text such as `py:percent` for readable source diffs. Keep the pair synchronized.
- **`nbdime`:** provides notebook-aware diffs/merges; it does not prove correctness or safety.
- **Rendered previews:** GitHub rendering or reviewed HTML/PDF helps assess narrative and figures, but does not replace source/metadata inspection.

**Terminal — add review tools and configure examples:**

```bash
uv add --dev nbstripout jupytext nbdime ruff nbqa
uv run nbstripout --install
uv run jupytext --set-formats ipynb,py:percent notebooks/01_explore_runs.ipynb
uv run nbdime config-git --enable
uv run ruff check --select E,F,I notebooks/01_explore_runs.ipynb
uv run nbqa ruff notebooks/
```

These commands assume the notebook already exists. Verify CLI help for the installed tool versions. `nbdime config-git --enable` configures the current user's Git integration. Detailed output-stripping hooks/policy are deferred to Lesson 05.

Ruff can lint supported notebook files; `nbqa` runs compatible tools against notebook code cells. Linting complements, but cannot replace, execution and human review.

### 4.5 Secrets and PII

Saved outputs can include tables, images, HTML, tracebacks, API responses, and accidental credentials. **Clearing outputs alone does not guarantee a secret-free notebook.** Review source and Markdown cells, outputs, attachments, metadata, paired scripts, rendered exports, and relevant Git history. If a real secret was committed, revoke/rotate it and follow the incident process; deleting it in a later commit does not remove it from history.

**Notebook code cell — read an environment variable without printing it:**

```python
import os

service_token = os.environ.get("SERVICE_TOKEN")
if not service_token:
    raise RuntimeError("SERVICE_TOKEN must be provided by the runtime")
print("Service token is configured; value intentionally not displayed.")
```

**Notebook code cell — interactive local prompt:**

```python
from getpass import getpass

service_token = getpass("Service token: ")
if not service_token:
    raise ValueError("A token is required")
```

For automation, use approved managed secret injection rather than prompting. Never hard-code, print, save, or interpolate secrets into shell commands. A `.env` file must not be committed and must follow the team's secret-management policy.

### 4.6 Collaboration and conventions

Use descriptive numbered names such as `01_explore_orders.ipynb`; keep a `notebooks/README.md` with purpose, environment, data source, run instructions, and output policy. Discuss shared-kernel and collaboration tooling (such as Jupyter collaboration or VS Code Live Share) with data access and isolation in mind.

Review checklist:

- [ ] Clear purpose and small enough scope.
- [ ] Fresh-kernel top-to-bottom run succeeds.
- [ ] Inputs, versions, time window, parameters, and limitations documented.
- [ ] Reusable logic lives in tested package code.
- [ ] Outputs are concise; no secrets/PII in source, outputs, metadata, attachments, paired scripts, or exports.
- [ ] Dependencies are declared/locked; no unexplained installs.
- [ ] Assertions, row counts, and data-quality checks are visible.
- [ ] Figures have units, labels, and evidence-aligned conclusions.
- [ ] Linting, tests, and CI execution pass.


## 5. Reproducibility beyond “Run All”

A successful fresh-kernel run is necessary but not sufficient. Reproducibility also depends on the interpreter and dependency resolution, input data, parameters, randomness, external services, locale/time zone, current time, and nondeterministic parallel operations.

### 5.1 Record provenance and parameters

Keep a visible **key findings / run metadata** cell near the top or end of the notebook. It should state what was run, against which data snapshot, with which parameters, and when. Do not put secrets or sensitive row-level data in this cell.

**Notebook code cell — reproducible metadata for the synthetic example:**

```python
from datetime import datetime, timezone
import platform

run_metadata = {
    "run_at_utc": datetime.now(timezone.utc).isoformat(),
    "python_version": platform.python_version(),
    "data_version": DATA_VERSION,
    "seed": SEED,
    "sample_fraction": SAMPLE_FRAC,
    "row_count": int(len(runs)),
}
run_metadata
```

The timestamp documents when the run occurred; it does not make time-dependent logic reproducible. For analyses depending on “today,” pass an explicit `as_of`/date parameter and record it. For external data, record a stable dataset version, immutable object version, commit/hash, query parameters, and extraction time where policy permits. A hash identifies bytes, not their meaning or licensing.

### 5.2 Seeds, lock files, and data snapshots

- Seed every random-number generator actually used (`random`, `numpy.random.Generator`, and any framework-specific generator); a single seed does not control all libraries or nondeterministic GPU/parallel operations.
- Prefer a committed lock file and a documented Python version. Pin direct dependencies when the project requires it; use a lock to capture resolved transitive versions. Rebuild on supported platforms and review lock changes.
- Version input data or provide a small, approved fixture. Do not use a mutable “latest” object as the only provenance record.
- Record parameters in notebook metadata/output or a report manifest. Keep source code and data version references together.
- Test pure transformation functions separately from notebook rendering and remote data access.

### 5.3 Notebook execution in CI

Run notebooks in a clean, bounded environment with explicit inputs and a time budget. A notebook that downloads live data or depends on credentials should be refactored to use a deterministic fixture or a separately managed integration test.

**Terminal — install testing tools in the project environment:**

```bash
uv add --dev nbmake nbval pytest
```

**Terminal — execute notebooks with pytest and nbmake:**

```bash
uv run pytest --nbmake notebooks/
```

`nbmake` integrates notebook execution with pytest; exact options and behavior depend on its installed version. `nbval` is an alternative for validating notebook execution and/or saved outputs, depending on the selected mode. Output comparisons can be brittle for timestamps, generated IDs, floating-point rendering, and plots; sanitize known volatile values and use justified tolerances rather than blindly accepting changed outputs. CI should fail on genuine execution errors, record the environment, enforce a time/resource budget, and preserve logs/artifacts according to data policy.

**Minimal CI shape (illustrative YAML; adapt to your CI provider):**

```yaml
name: notebook-checks
on: [push, pull_request]
jobs:
  notebooks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv sync --locked
      - run: uv run pytest
      - run: uv run pytest --nbmake notebooks/
```

Pin third-party CI actions to approved immutable references according to your organization's supply-chain policy. The snippet assumes the lock file, project configuration, tests, and `notebooks/` directory exist. It is a structural example, not a universal drop-in workflow.

## 6. Debugging, profiling, and scale

### 6.1 Diagnose the failing cell first

- Read the full traceback and identify the first frame belonging to your code; do not hide exceptions with broad `except Exception: pass`.
- `%debug` opens post-mortem debugging after an exception; `%pdb on` enables automatic post-mortem debugging. `breakpoint()` uses Python's debugger and can behave differently in remote/IDE kernels.
- Use the IDE debugger for stepping through package functions. Prefer tests for repeatable edge cases over debugging the same notebook state repeatedly.

**Notebook code cell — profiling examples (IPython magics):**

```python
%timeit sum(range(10_000))
%prun sum(i * i for i in range(100_000))
```

`%timeit` measures repeated execution of an expression and can be inappropriate for mutating code or expensive side effects. `%prun` profiles a statement. `%lprun` requires a compatible line-profiler extension; `%memit` requires an appropriate memory-profiler/IPython integration. `tracemalloc` tracks many Python allocation sites but not every native allocation; process RSS and library-specific memory can tell a different story.

### 6.2 Performance and remote execution

- Start by measuring wall time, memory, query volume, and transfer size. Do not assume a notebook UI is the bottleneck.
- Filter/project/aggregate near the data source; avoid transferring an entire warehouse table into a local kernel. Use chunking, database-side aggregation, or lazy query engines when appropriate.
- A remote kernel moves computation, not necessarily data-access risk. Review identity, network reachability, mounted storage, logs, and where outputs are saved.
- Apply CPU, memory, execution-time, and query-cost limits. Move scheduled, retryable, long-running or SLA-bound work to a job/orchestrator rather than leaving it attached to an interactive session.
- Caching (`joblib.Memory`, parquet checkpoints, or application caches) is safe only when inputs, code/configuration, dependency assumptions, and data versions are represented in invalidation logic. Avoid caching secrets or sensitive outputs in shared locations.

## 7. Alternatives and state/execution trade-offs

| System | Execution/state model | Useful for | Trade-off to understand |
|---|---|---|---|
| JupyterLab / VS Code notebooks | Persistent kernel; cells can execute out of order | Exploration, teaching, mixed narrative and code | Hidden state and saved outputs require discipline |
| marimo | Reactive Python notebook stored as `.py`; dependency-aware cell execution | Reproducible interactive Python analysis | Reactive execution differs from Jupyter's imperative kernel; extensions/integration differ |
| Quarto (`.qmd`) | Document-oriented rendering/execution across supported languages | Reports, publishing, reproducible documents | Render pipeline and execution environment must be managed |
| Observable | Reactive JavaScript notebooks | Browser-native interactive data work | JavaScript ecosystem and browser execution model |
| Pluto.jl | Reactive Julia notebooks | Julia workflows with dependency-aware execution | Julia language/ecosystem, not a Python drop-in |
| Colab / Kaggle / Databricks notebooks | Hosted/platform-specific kernels and storage | Managed compute, collaboration, platform data | Ephemeral storage, permissions, secrets, package setup and platform limits vary |

No system removes the need to version data, test logic, review outputs, or control access. Compare state semantics, language support, execution automation, deployment, collaboration, and governance before migrating.

## 8. Security model for notebook workflows

A notebook is executable code. Opening or executing an untrusted notebook can run arbitrary Python, shell commands, network requests, and filesystem operations available to the kernel. Do not treat a “Trust” action as a sandbox.

- Inspect source, Markdown, outputs, attachments, metadata, and paired text files before execution. Prefer a disposable environment/container with no production credentials, restricted network and filesystem access, and resource limits for unknown notebooks or LLM-generated code.
- Jupyter server access should use authentication, least privilege, protected transport (TLS via an approved deployment), and a controlled network boundary. Do not expose an unauthenticated server or arbitrary public port. A token is a bearer credential; do not paste it into logs or notebooks.
- Notebook extensions and IDE extensions are executable dependencies. Install only from approved sources, pin/review versions, and consider the permissions of the host process.
- Treat LLM-generated code as untrusted until reviewed and tested. Do not execute it in a kernel that has cloud credentials, mounted sensitive data, or broad network access. Use an isolated sandbox and explicit allow-listed inputs/outputs.
- Clearing notebook outputs reduces accidental disclosure but is not a security scan. Inspect cell source, Markdown, metadata, attachments, HTML/JSON exports, paired scripts, caches, and Git history; run approved secret scanners. If a credential leaks, revoke/rotate it and follow incident response.
- Apply data minimization: use synthetic or masked samples, avoid row-level PII in outputs, and check whether saved plots, HTML, logs, and CI artifacts reveal sensitive values.

## 9. Notebook vs other deliverables: decision framework

| Need | Prefer | Why / promotion trigger |
|---|---|---|
| Explore hypotheses, teach a workflow, show intermediate evidence | Notebook | Narrative and interactive inspection are useful; keep state controlled |
| Reuse a transformation or business rule | Package function + tests | Stable API, direct unit tests, reusable by notebooks and jobs |
| Repeatable batch run, retries, schedule, SLA | Script/package + orchestrator | Explicit inputs, logs, retries, observability and operational ownership |
| Interactive user-facing controls | App (e.g. Streamlit/Dash) | Separate user interaction from analyst kernel; add authentication and authorization |
| Stable publication or review artifact | Rendered report (e.g. Quarto / executed notebook export) | Readers consume a fixed output; preserve provenance and sanitize outputs |

“Promote when reused twice” is a useful heuristic, not a law. Promote sooner when logic is business-critical, security-sensitive, difficult to test in cells, or needed by production jobs.

## 10. Refactoring exercise: messy exploration to reviewable workflow

Use a provided messy notebook or create a synthetic one that has out-of-order cells, repeated transformations, unexplained constants, oversized outputs, machine-specific paths, and no visible data checks. Do not use production secrets or unapproved PII.

1. Write down its question, intended audience, decision, data source/version, parameters, and limitations.
2. Restart the kernel and run all cells. Record the first failure and remove hidden-state dependencies.
3. Create a parameters cell; make randomness and time dependencies explicit.
4. Extract stable transformations into `src/yourpkg/` and add unit tests for normal cases, edge cases, and invalid inputs.
5. Editable-install the package; leave the notebook to orchestrate steps and explain findings.
6. Add row-count/schema/assertion checks and a visible key-findings/data-version cell.
7. Strip outputs according to repository policy, pair with Jupytext if useful, and configure a pre-commit hook or equivalent review check.
8. Add CI execution (`pytest` and `pytest --nbmake notebooks/` or a documented alternative) with deterministic fixtures, a time budget, and safe artifacts.
9. Inspect diffs and rendered output. Scan source, outputs, metadata, attachments, paired files and history for secrets/PII.
10. Document before/after: reproducibility, test coverage, runtime/memory changes, reviewability, and remaining limitations. Do not claim a speedup without measurement.

## 11. Common mistakes checklist

- Trusting a notebook that has not passed a fresh-kernel top-to-bottom run.
- Confusing execution counters with document order or assuming saved outputs reflect current source.
- Mixing magics and shell commands into importable Python modules.
- Installing dependencies into an unverified interpreter or failing to commit dependency metadata/lock files.
- Depending on mutable data, current time, unrecorded parameters, or unseeded random state.
- Embedding huge tables, sensitive records, credentials, or stale plots in saved outputs.
- Treating output stripping, notebook trust, a successful CI run, or a lock file as complete proof of safety/reproducibility.
- Leaving reusable logic duplicated across cells instead of testing it in a package.
- Using caches without complete keys/invalidation or assuming `gc.collect()` always releases native memory.
- Treating a remote kernel, hosted notebook, extension, or LLM-generated snippet as inherently safe.

## 12. Self-check

1. **What is hidden state, and how do you eliminate it?** Explain how a variable can survive after its defining cell is edited/deleted, and describe a restart-and-run-all workflow plus its limits.
2. **Describe two ways to make notebook diffs reviewable.** Compare output stripping with `nbstripout`, a Jupytext text pairing, `nbdime`, and rendered previews; state what each does not guarantee.
3. **Convert an exploratory notebook into a package function with tests, a thin notebook, and a CI check.** Sketch a package layout, a meaningful unit test, and a notebook execution command such as `uv run pytest --nbmake notebooks/`; explain how to use a deterministic fixture and avoid secrets in artifacts.

A strong answer distinguishes notebook execution correctness from analytical validity and security. The notebook should explain the question, data version, parameters, checks, key findings, uncertainty/limitations, and next decision; tests should target reusable logic, while CI checks that the notebook remains executable.
