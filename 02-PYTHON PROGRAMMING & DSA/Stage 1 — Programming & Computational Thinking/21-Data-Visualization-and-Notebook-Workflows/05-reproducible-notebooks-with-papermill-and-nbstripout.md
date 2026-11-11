# Reproducible Notebooks with Papermill and nbstripout

> **Stage 1 — Programming & Computational Thinking · Module 1.21 · Lesson 05**  
> Target file: `05-reproducible-notebooks-with-papermill-and-nbstripout.md`  
> Baseline: Python 3.12+, JupyterLab 4, and tools pinned in the project's lock file. Check version-sensitive flags against the installed versions before upgrading.

## 1. Learning outcomes and the reproducibility model

By the end of this lesson, you should be able to:

- Parameterize a notebook with a cell tagged `parameters`, execute it unattended with Papermill, and explain the injected-parameters cell.
- Keep source notebooks distinct from executed notebooks, logs, rendered reports, and machine-readable artifacts.
- Execute/export with `nbconvert`; apply a deliberate `nbstripout` policy without treating it as a security boundary.
- Validate parameters, use deterministic seeds where possible, identify data snapshots, and record run provenance.
- Capture notebook outputs with Scrapbook or explicit files; diagnose failures, timeouts, working-directory issues, and kernel mismatches.
- Make notebook changes reviewable with Jupytext, pre-commit, Ruff/nbqa, and notebook-aware tests.
- Design CI execution with sample data, time budgets, artifacts, warning policies, and retention/access controls.
- Use `nbformat`, `nbclient`, and `nbconvert` programmatically, and decide when stable logic should move into a package or scheduled job.

### Mental model

```text
versioned source notebook + locked environment + validated parameters
           + versioned input data + code revision + run identifier
                                |
                                v
                       controlled execution
               +----------------+----------------+
               |                |                |
               v                v                v
         executed .ipynb      run logs       explicit metrics/data
               |
               v
        rendered HTML/PDF/Markdown after privacy review
```

Reproducibility does not guarantee byte-for-byte identical output in every environment. It means inputs, environment, code revision, parameters, and known nondeterminism are recorded well enough to explain and, within stated limits, recreate a run.

- **Source notebook:** reviewed, version-controlled input; usually committed without execution outputs.
- **Executed notebook:** a run artifact containing executed cells, outputs, execution counts, and possibly failure context. It may contain sensitive data.
- **Logs:** operational records for run IDs, progress, warnings, and diagnosis. Do not log secrets or unnecessary row-level data.
- **Rendered report:** audience-facing HTML, Markdown, or PDF. Review it separately from the source notebook.
- **Explicit artifacts:** `metrics.json`, plots, or curated tables intended for downstream consumers.
- **Provenance:** code revision, runtime/library versions, effective parameters, data snapshot identity, and run ID.

Lesson 04 focuses on interactive notebook practice and hidden state. This lesson focuses on unattended execution, parameter contracts, run artifacts, governance, and automation.

## 2. Setup and project layout

The examples use `uv`; equivalent environment managers are acceptable if they produce a controlled and recorded environment. Run setup commands from the repository root, not from a notebook cell.

### Runtime dependencies — terminal

```bash
uv add papermill pandas numpy ipykernel
```

Install only libraries actually required by the notebook. Papermill executes notebooks; `ipykernel` supplies a Python kernel; pandas/NumPy support the sample data workflow.

### Development and governance tools — terminal

```bash
uv add --dev nbstripout nbconvert jupytext nbqa ruff pre-commit nbval nbformat nbclient scrapbook
```

`nbmake` is an alternative pytest plugin for executing notebooks:

```bash
uv add --dev nbmake
```

Pin dependencies through `pyproject.toml` and commit `uv.lock`. These are project choices, not a universal list. Confirm installed command options using `uv run papermill --help`, `uv run jupyter nbconvert --help`, and `uv run nbstripout --help`.

### Suggested layout

```text
project/
├── src/reporting/                 # importable, tested business logic
├── tests/
├── notebooks/daily_report.ipynb   # reviewed source notebook
├── data/sample_orders.csv         # small synthetic fixture only
├── out/runs/                      # executed notebooks (normally ignored)
├── out/reports/                   # rendered reports
├── out/metrics/                   # machine-readable metrics
├── logs/                          # access-controlled operational logs
├── pyproject.toml
├── uv.lock
├── .gitignore
└── .pre-commit-config.yaml
```

Example `.gitignore`:

```gitignore
out/
logs/
.ipynb_checkpoints/
```

Do not ignore all output directories if a small, sanitized golden artifact is intentionally versioned. Document exceptions and keep production outputs out of source control by default.

## 3. A parameterized notebook with a clear contract

Create `notebooks/daily_report.ipynb`. The following are **cell contents**, not a complete `.ipynb` JSON document. In JupyterLab/VS Code, add the exact cell tag `parameters` to Cell 1. A comment mentioning the tag is not enough. Papermill runs the parameters cell and injects a separate cell with command-line overrides after it; the executed notebook becomes a record of effective values.

### Cell 1 — parameters

```python
run_date = "2026-10-18"
data_path = "data/sample_orders.csv"
data_version = "sample-v1"
sample_frac = 1.0
random_seed = 17
output_dir = "out"
run_id = "local-2026-10-18-a"
```

Defaults should be safe for interactive work and tests. The values passed at runtime must use these exact parameter names.

### Cell 2 — validate, resolve paths, and load data

```python
from pathlib import Path
import random
import numpy as np
import pandas as pd

from datetime import date
try:
    parsed_date = date.fromisoformat(run_date)
except (TypeError, ValueError) as exc:
    raise ValueError("run_date must be a valid YYYY-MM-DD date") from exc
if not isinstance(data_path, str) or not data_path.strip():
    raise ValueError("data_path must be a non-empty path")
if not isinstance(data_version, str) or not data_version.strip():
    raise ValueError("data_version must identify the input snapshot")
if not isinstance(sample_frac, (int, float)) or isinstance(sample_frac, bool):
    raise TypeError("sample_frac must be numeric")
if not 0 < float(sample_frac) <= 1:
    raise ValueError("sample_frac must be in (0, 1]")
if not isinstance(random_seed, int) or isinstance(random_seed, bool):
    raise TypeError("random_seed must be an integer")
if (
    not isinstance(run_id, str)
    or not run_id.strip()
    or run_id in {".", ".."}
    or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for char in run_id)
):
    raise ValueError("run_id must contain only letters, digits, dot, underscore, or hyphen")

random.seed(random_seed)
np.random.seed(random_seed)

# Papermill is launched with --cwd . from the project root.
root = Path.cwd().resolve()
input_path = (root / data_path).resolve()
# Example policy: inputs must remain inside the repository's data directory.
approved_data_root = (root / "data").resolve()
if input_path != approved_data_root and approved_data_root not in input_path.parents:
    raise ValueError("data_path must resolve under the approved data/ directory")
if not input_path.is_file():
    raise FileNotFoundError(f"Input data not found: {input_path}")

output_root = (root / output_dir).resolve()
if output_root != root and root not in output_root.parents:
    raise ValueError("output_dir must resolve inside the project root")
run_output_dir = output_root / "runs"
report_dir = output_root / "reports"
metrics_dir = output_root / "metrics"
for directory in (run_output_dir, report_dir, metrics_dir):
    directory.mkdir(parents=True, exist_ok=True)

orders = pd.read_csv(input_path)
if sample_frac < 1:
    orders = orders.sample(frac=float(sample_frac), random_state=random_seed)
if "order_id" not in orders.columns:
    raise ValueError("Expected column 'order_id' is missing")
if not orders["order_id"].is_unique:
    raise ValueError("order_id must be unique for this report's input")
```

This is a teaching example, not a complete filesystem security boundary. A production job should use configured allow-listed roots, avoid accepting arbitrary paths from untrusted callers, and record a content hash or immutable data-platform version—not just a human label. Date parsing here validates calendar format, but timezone and business-calendar semantics must be defined separately if relevant.

### Cell 3 — write a metrics artifact atomically

```python
import json
import os
import tempfile

row_count = int(len(orders))
metrics = {
    "run_id": run_id,
    "run_date": parsed_date.isoformat(),
    "data_version": data_version,
    "rows": row_count,
    "sample_frac": float(sample_frac),
    "random_seed": random_seed,
}
metrics_path = metrics_dir / f"daily_metrics_{parsed_date.isoformat()}_{run_id}.json"
if metrics_path.exists():
    raise FileExistsError(f"Refusing to overwrite existing run artifact: {metrics_path}")
fd, temporary_name = tempfile.mkstemp(
    prefix=f".{metrics_path.name}.", suffix=".tmp", dir=metrics_path.parent
)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(metrics, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    # Atomic replacement within the same filesystem. The prior existence
    # check is not a concurrency lock; use exclusive creation/locking when
    # concurrent writers are possible.
    if metrics_path.exists():
        raise FileExistsError(f"Run artifact appeared concurrently: {metrics_path}")
    os.link(temporary_name, metrics_path)
finally:
    try:
        os.unlink(temporary_name)
    except FileNotFoundError:
        pass

metrics
```

The output name includes a run ID to reduce collisions and the code refuses ordinary overwrites. The existence check alone is not a complete concurrency guarantee; for concurrent workers, use an atomic exclusive-create/locking strategy or a unique run directory. Atomicity of one file does not make multiple files a transaction.

### Execute from the repository root — terminal

```bash
mkdir -p out/runs out/reports out/metrics
uv run papermill \
  notebooks/daily_report.ipynb \
  out/runs/daily_report_2026-10-18_local-2026-10-18-a.ipynb \
  -r run_date 2026-10-18 \
  -r data_path data/sample_orders.csv \
  -r data_version sample-v1 \
  -p sample_frac 1.0 \
  -p random_seed 17 \
  -r output_dir out \
  -r run_id local-2026-10-18-a \
  --kernel python3 \
  --cwd . \
  --execution-timeout 600 \
  --log-output
```

- First path: source notebook. Second path: executed notebook. They must not be the same path.
- `-p NAME VALUE` parses a value as YAML; use it for numeric/boolean values when the intended type is clear. `-r NAME VALUE` preserves a raw string, so it is used for dates, paths, snapshot IDs, output directories, and run IDs in this example. Keep names aligned exactly with Cell 1.
- `--kernel python3` selects a kernelspec available to the runner; verify with `uv run jupyter kernelspec list`. The kernelspec's interpreter must match the locked project environment.
- `--cwd .` makes relative paths resolve from the repository root for supported Papermill versions. Confirm option support against the pinned version.
- `--execution-timeout 600` is a per-cell timeout, not necessarily a hard total job deadline.
- `--log-output` streams cell output to logs; output may contain sensitive values. `--progress-bar` is another presentation option in supported Papermill versions; check the pinned CLI help before using it.
- Papermill exits non-zero on execution failure and may preserve a notebook containing traceback context when possible. A process kill or disk failure can prevent a complete artifact. Check exit status and validate the output before publishing.

**Retry only when work is idempotent** or duplicate side effects are prevented by transactions, idempotency keys, deduplication, or run-state tracking. A notebook that sends email or writes to a warehouse can repeat those effects after a timeout. Record whether a run is `started`, `succeeded`, or `failed`, and do not treat a partial output notebook as a successful report.

## 4. nbconvert, nbstripout, and source-control policy

### Execute and export with nbconvert — terminal

To execute and render a source notebook in one command, use an explicit output location and check options for the pinned nbconvert version:

```bash
uv run jupyter nbconvert \
  --to html \
  --execute notebooks/daily_report.ipynb \
  --output daily_report_preview.html \
  --output-dir out/reports \
  --ExecutePreprocessor.timeout=600
```

This example is an interactive preview using source defaults; it is **not** a replacement for the Papermill parameterized run. For an already executed notebook, export without re-execution:

```bash
uv run jupyter nbconvert \
  --to html \
  --no-input \
  --output daily_report_2026-10-18.html \
  --output-dir out/reports \
  out/runs/daily_report_2026-10-18_local-2026-10-18-a.ipynb
```

`--no-input` hides code in the rendered view; it does not remove output data, embedded images, HTML, or secrets. Review the rendered artifact. PDF export may require a TeX installation or another exporter-specific dependency; do not assume every format works in every environment.

### What nbstripout does—and does not do

`nbstripout` is a source-control hygiene tool, not a secret-removal guarantee. Depending on the installed version and configuration, it removes cell outputs and execution counts and may remove selected notebook metadata. Inspect the installed tool's help and a before/after diff to establish the exact policy.

Typical repository setup — terminal:

```bash
uv run nbstripout --install --attributes
```

This configures a Git filter in the local repository and can write `.gitattributes`; verify the generated configuration and test a commit in a disposable branch. Teammates and CI clones may need the filter installed too, so document setup and use a consistent pre-commit/CI check. A Git clean filter affects the staged/committed representation; it does not necessarily erase outputs from the working copy.

**Do not infer that stripping removes secrets.** It may leave source-cell literals, Markdown, attachments, metadata fields not covered by the configured policy, and secrets printed into any retained or exported artifact. It cannot remove a secret from Git history or other copies. Use secret scanning (`gitleaks` or `detect-secrets`), source review, targeted redaction, and history remediation when needed. Never put credentials in a notebook; use a secret manager, environment variables, or `getpass` for interactive prompts. Environment variables can still leak if printed or copied into outputs.

## 5. Provenance, determinism, and data lineage

Record at least: run ID, UTC start time, Python version, OS/platform, key library versions, Git commit (if available), effective parameters, input data version/hash, and whether the working tree was dirty. Do not record secrets, full connection strings, or raw sensitive data. Provenance fields can be unavailable; represent them as `null`/`unknown` with a reason rather than crashing or fabricating a value.

### Robust provenance cell — Python

```python
import importlib.metadata as metadata
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone


def git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args], capture_output=True, text=True,
            check=True, timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = result.stdout.strip()
    return value or None


def package_version(distribution: str) -> str | None:
    try:
        return metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return None

provenance = {
    "run_id": run_id,
    "started_at_utc": datetime.now(timezone.utc).isoformat(),
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    "git_commit": git_value("rev-parse", "HEAD"),
    "git_worktree_status": git_value("status", "--porcelain"),
    "libraries": {
        name: package_version(name)
        for name in ("pandas", "numpy", "papermill", "nbconvert")
    },
    "parameters": {
        "run_date": run_date,
        "data_path": data_path,
        "data_version": data_version,
        "sample_frac": float(sample_frac),
        "random_seed": random_seed,
        "output_dir": output_dir,
    },
    "data_fingerprint": os.environ.get("DATA_SNAPSHOT_ID", data_version),
}
print(json.dumps(provenance, indent=2, sort_keys=True))
```

This records the Git commit and status when Git is available, and returns `None` when commands or package metadata are unavailable. It does not compute a content hash of the input; use a trusted immutable snapshot ID or calculate a hash for manageable local files. A `data_path` is not a data version by itself. Consider recording the lock-file hash and runner/container image digest as well.

For deterministic sampling, seed the relevant random generators and pass `random_state` explicitly where supported. Seeds do not guarantee identical results across library versions, parallel execution, hardware, or nondeterministic upstream systems. Document tolerances and known nondeterminism instead of claiming universal determinism.

## 6. Capturing results and handling failures

Prefer explicit, schema-validated artifacts such as `metrics.json` for downstream systems. Scrapbook can attach named values to an executed notebook and read them later.

### Scrapbook — Python cell

```python
import scrapbook as sb

sb.glue("row_count", int(len(orders)))
sb.glue("data_version", data_version)
```

Read a completed notebook in a separate Python process:

```python
import scrapbook as sb

record = sb.read_notebook(
    "out/runs/daily_report_2026-10-18_local-2026-10-18-a.ipynb"
)
print(record.scraps["row_count"].data)
```

These snippets require `scrapbook` in the kernel environment. If unavailable, write a JSON artifact instead. Avoid gluing raw records, PII, secrets, or large dataframes into notebook metadata/outputs.

### Failure-handling checklist

- Preserve the Papermill output notebook and traceback for diagnosis, but restrict access and retention.
- Record command exit status, run ID, input snapshot, and elapsed time in logs.
- Set a per-cell timeout and a separate CI/job-level wall-clock limit.
- Specify the kernel and working directory explicitly; verify the kernel's interpreter and dependency set.
- Do not automatically retry a failed job with non-idempotent side effects.
- Distinguish a failed execution artifact from a successful report; validate required outputs before publication.
- Keep logs concise and redact sensitive values. `--log-output` may copy cell outputs into CI logs.

## 7. Jupytext, pre-commit, Ruff, and reviewable diffs

Jupytext can pair a notebook with a text representation such as `py:percent`. This makes code/narrative changes easier to review, but the paired files must be synchronized and the notebook format must preserve the metadata your workflow depends on.

### Pair and synchronize — terminal

```bash
uv run jupytext --set-formats ipynb,py:percent notebooks/daily_report.ipynb
uv run jupytext --sync notebooks/daily_report.ipynb
```

Review both files after synchronization. Avoid editing both representations independently and assuming the tool will infer which side is authoritative. Test that cell tags and metadata needed for Papermill survive round-tripping in the pinned Jupytext version.

### Lint Python cells

```bash
uv run nbqa ruff notebooks/
uv run ruff check src tests
uv run pre-commit run --all-files
```

A minimal `.pre-commit-config.yaml` should pin hook revisions and include the project's chosen notebook stripping, Ruff, and secret-scanning hooks. Hook IDs and configuration vary by provider/version; copy them from each tool's official documentation and test them locally rather than assuming an arbitrary YAML snippet is portable. Ensure notebook-aware linting does not rewrite or remove the `parameters` tag.

For review, prefer focused notebooks, meaningful names, a README with environment/run instructions, a rendered preview for narrative-heavy notebooks, and `nbdime` when cell-aware diffs are useful. GitHub's rendered preview can help reviewers but is not a substitute for execution or privacy review.

## 8. Quarto, cell tags, and report export

Quarto and nbconvert templates can hide code, arrange figures/tables, and create audience-specific reports. Treat rendering as a separate build step and validate the resulting artifact.

Common Jupyter/Quarto-related tags include `remove-input`, `remove-cell`, and `remove-output`, but support and exact behavior depend on the renderer/template. Test tags against the pinned toolchain. Hiding code or output from a rendered view is not the same as deleting it from the source notebook or securing the underlying data.

Example export of an executed notebook with nbconvert:

```bash
uv run jupyter nbconvert --to markdown \
  --output daily_report_2026-10-18.md \
  --output-dir out/reports \
  out/runs/daily_report_2026-10-18_local-2026-10-18-a.ipynb
```

Quarto's `render --execute-params` is an alternative when the project is authored as a Quarto document; it is not a Papermill flag. Keep the parameter contract and output paths documented per renderer.

## 9. CI execution and test strategy

CI should prove that a clean environment can execute the notebook with small, versioned synthetic/sample data. It should not depend on a developer's current kernel state or production credentials.

A provider-neutral job should:

1. Check out the repository and install from the lock file.
2. Run package unit tests and linting.
3. Validate notebook JSON and source-control hygiene.
4. Execute selected notebooks with sample parameters and a hard job timeout.
5. Fail on uncaught exceptions and configured warning classes; do not globally suppress warnings to make the build green.
6. Upload executed notebooks, logs, HTML previews, and metrics as artifacts with appropriate access controls and retention.
7. Run secret scanning on source notebooks, paired text, generated outputs, and artifacts before sharing.

### Illustrative terminal checks

```bash
uv sync --locked
uv run pytest
uv run nbqa ruff notebooks/
uv run pytest --nbmake notebooks/daily_report.ipynb
```

The `nbmake` command requires `nbmake` installed as a development dependency. A CI provider's matrix, cache, and artifact-upload YAML is provider-specific—keep those details separate from the general principles above.

### `nbval` and output regression

`nbval` can execute notebooks and optionally compare outputs against saved expected outputs. Output comparisons may be brittle for timestamps, random values, platform-dependent formatting, or floating-point calculations. Use sanitization and tolerances where supported, and compare stable semantic results rather than volatile representations. Do not keep secrets in a golden notebook simply to make a test pass.

### CI controls to decide explicitly

- **Matrix:** Python/library versions only where the project promises compatibility; otherwise test the locked production environment first.
- **Caching:** cache package downloads/environments keyed by lock file and Python version; never let a stale cache override the lock.
- **Time budget:** per-cell timeout plus job-level deadline and cancellation policy.
- **Warnings:** define actionable warning classes and a documented allow-list; do not convert every warning into an error blindly if upstream dependencies are noisy.
- **Artifacts:** retain only as long as operationally required; restrict access to executed notebooks and logs; scrub before public release.
- **Sample data:** synthetic or licensed, small, stable, and versioned. Production data access belongs in a separately governed execution environment.

## 10. Programmatic notebook validation and execution

Use `nbformat` to parse/validate notebook structure, `nbclient` for controlled execution, and `nbconvert` preprocessors/exporters for organization-specific policy. These APIs are versioned; test them against the project's pinned dependency set.

### Validate notebook structure — Python script

```python
from pathlib import Path
import nbformat

notebook_path = Path("notebooks/daily_report.ipynb")
notebook = nbformat.read(notebook_path, as_version=4)
nbformat.validate(notebook)

parameter_cells = [
    cell for cell in notebook.cells
    if cell.cell_type == "code" and "parameters" in cell.get("metadata", {}).get("tags", [])
]
if len(parameter_cells) != 1:
    raise ValueError(f"Expected exactly one parameters cell; found {len(parameter_cells)}")
```

### Edit, tag, clear outputs, and validate with nbformat — Python script

```python
from pathlib import Path
import nbformat
from nbformat.v4 import new_markdown_cell

source = Path("notebooks/daily_report.ipynb")
target = Path("out/runs/daily_report_prepared.ipynb")
target.parent.mkdir(parents=True, exist_ok=True)
notebook = nbformat.read(source, as_version=4)
nbformat.validate(notebook)

# Add a review note without modifying the source file.
notebook.cells.insert(0, new_markdown_cell("Run prepared by the controlled build workflow."))
for cell in notebook.cells:
    if cell.cell_type == "code":
        cell.outputs = []
        cell.execution_count = None
# Keep the Papermill parameters tag intact and validate after edits.
nbformat.validate(notebook)
nbformat.write(notebook, target)
```

This writes a separate prepared artifact. Clearing outputs is appropriate for a clean execution input but is **not** a reliable secret scrubber; source, Markdown, attachments, metadata, and other copies still need review. Programmatic edits should preserve required tags and be covered by tests.

### Execute with nbclient — Python script

```python
from pathlib import Path
import nbformat
from nbclient import NotebookClient

source = Path("notebooks/daily_report.ipynb")
target = Path("out/runs/nbclient_smoke.ipynb")
target.parent.mkdir(parents=True, exist_ok=True)
notebook = nbformat.read(source, as_version=4)
client = NotebookClient(
    notebook,
    timeout=600,
    kernel_name="python3",
    resources={"metadata": {"path": str(Path.cwd())}},
    allow_errors=False,
)
executed = client.execute()
nbformat.write(executed, target)
```

This smoke test uses source defaults, not Papermill overrides. The selected kernel must exist, and the notebook's data paths must be valid from the configured working directory. For parameterized runs, use Papermill or explicitly inject values before execution.

### Policy checks with a preprocessor/exporter

A custom `nbconvert` preprocessor can reject notebooks whose outputs exceed a size budget, whose outputs contain disallowed patterns, or whose cell tags violate policy. Keep checks narrow and explain their limits: regex scanning can miss encoded/obfuscated secrets, while broad patterns can produce false positives. Run secret scanning as an additional control, not as a guarantee.

For example, this simple policy check detects oversized serialized outputs but does not identify secrets:

```python
import nbformat
from pathlib import Path

path = Path("out/runs/daily_report_2026-10-18_local-2026-10-18-a.ipynb")
notebook = nbformat.read(path, as_version=4)
limit_bytes = 2_000_000
oversized = []
for index, cell in enumerate(notebook.cells):
    if cell.cell_type != "code":
        continue
    size = len(str(cell.get("outputs", [])).encode("utf-8"))
    if size > limit_bytes:
        oversized.append((index, size))
if oversized:
    raise ValueError(f"Notebook outputs exceed policy limit: {oversized}")
```

### Export with an nbconvert exporter — Python script

```python
from pathlib import Path
import nbformat
from nbconvert import HTMLExporter

source = Path("out/runs/daily_report_2026-10-18_local-2026-10-18-a.ipynb")
target = Path("out/reports/daily_report_2026-10-18.html")
target.parent.mkdir(parents=True, exist_ok=True)
notebook = nbformat.read(source, as_version=4)
nbformat.validate(notebook)
exporter = HTMLExporter()
exporter.exclude_input = True  # presentation choice, not a privacy control
html, resources = exporter.from_notebook_node(notebook)
target.write_text(html, encoding="utf-8")
```

This is a direct exporter API example; it assumes the executed notebook exists and has already passed the report's success and privacy gates. A custom `nbconvert.preprocessors.Preprocessor` can enforce policy before export, but its checks should be tested and combined with secret scanning rather than treated as complete detection.

## 11. Privacy, governance, and retention

Treat `.ipynb` files as both code and data. A notebook can leak information through source cells, Markdown, outputs, display HTML, embedded images, widget state, attachments, metadata, exception tracebacks, logs, and rendered reports.

- Use least-privilege data access and separate identities for local development and scheduled production runs.
- Use environment variables or a secret manager for noninteractive credentials; use `getpass` only for interactive entry. Never print environment values or include credentials in Papermill parameters.
- Scan source and generated artifacts with secret scanners. Review findings; automated scanners can miss secrets and produce false positives.
- Redact PII and sensitive row-level values before saving or exporting. Removing outputs is useful hygiene, but it is not proof of absence.
- Restrict artifact/log access, set retention and deletion policies, and preserve an audit trail of who ran or published a report.
- Keep provenance useful but minimal; do not record full file paths if they reveal sensitive infrastructure or user names.
- Treat untrusted notebooks as executable code. Inspect source before execution; use an isolated, least-privilege runner with restricted network/filesystem access. Jupyter server tokens and authentication, extensions, kernel packages, and notebook dependencies are security-sensitive. Review extension supply chains and do not execute LLM-generated code against production credentials or unrestricted hosts.

## 12. Scheduling and scale; when to promote logic into a package

Scheduling options include cron/systemd timers, CI schedules, and orchestrators such as Airflow's Papermill integration, Dagster, or managed notebook jobs. These are awareness-level alternatives, not a full orchestration implementation. A scheduled job should define ownership, alerting, timeout, retries, idempotency, resource limits, and retention.

For parallel parameter sweeps, use bounded worker pools/array jobs, unique run IDs/output directories, explicit resource limits, and backpressure. Avoid launching unbounded kernels. Remote/cloud notebook runners and container images must pin dependencies, control data access, and clean up kernels and temporary data. Keep large reusable transformations out of the notebook.

Promote logic when inputs/outputs stabilize, tests are valuable, a schedule/SLA exists, multiple notebooks reuse the same operation, or side effects need robust retry/transaction handling. Refactor in small steps:

1. Extract pure transformations into functions.
2. Add unit tests and input/output contracts.
3. Move reusable code into an importable module/package.
4. Expose a CLI or task interface if needed.
5. Keep the notebook as a thin parameter, narrative, visualization, and report layer.

## 13. Alternative notebook/report systems

- **Jupyter + Papermill:** execute a notebook with parameters and preserve an executed notebook artifact.
- **nbconvert / `jupyter execute`:** execute or export notebooks with a simpler command-line workflow; parameter handling is not equivalent to Papermill by default.
- **Jupytext:** pair notebooks with text formats for review and synchronization; it is not itself a scheduler.
- **Quarto:** render documents/notebooks with report-oriented layout and parameter support; execution and metadata behavior depend on project configuration.
- **marimo:** reactive notebook model that can reduce hidden-state problems, with different authoring and execution semantics from `.ipynb`.
- **Ploomber:** pipeline-oriented organization of notebook/script tasks.
- **Managed notebook jobs:** convenient integration with platform identity/data services, but introduce platform-specific permissions, costs, and portability trade-offs.

Choose based on execution model, parameter support, review workflow, deployment target, governance, and team skills—not novelty alone.

## 14. Daily data-quality report exercise

Build `notebooks/daily_report.ipynb` to accept `run_date`, a versioned input snapshot, a seed, and a unique `run_id`. Use only synthetic/sample data in CI.

Required deliverables:

1. Validate parameters and the expected schema; fail loudly when required columns, uniqueness, freshness, or quality thresholds are violated.
2. Produce a compact HTML report and `metrics.json` with row counts, missing-value rates, duplicate counts, threshold results, data version, and provenance. Do not include raw records or PII.
3. Execute for three dates with Papermill in CI or a documented cron-style run. Each run must use a distinct output path and ID.
4. Preserve failed-run diagnostics privately; publish only successful, reviewed artifacts.
5. Configure nbstripout and a pre-commit/CI secret scan; demonstrate that stripping is not being treated as a secret-removal control.
6. Add package-function unit tests, a notebook smoke test, and an execution time budget.
7. Document schedule, required permissions, data retention, retry/idempotency policy, owner, alerting, and manual rerun procedure in a short runbook.

### Execute three dates — terminal illustration

Run from the repository root after installing the locked environment and ensuring each date has an available, versioned input snapshot. Use a distinct run ID and output notebook path for each run:

```bash
for day in 2026-10-16 2026-10-17 2026-10-18; do
  run_id="ci-${day}"
  uv run papermill \
    notebooks/daily_report.ipynb \
    "out/runs/daily_report_${day}_${run_id}.ipynb" \
    -r run_date "$day" \
    -r data_path "data/sample_orders_${day}.csv" \
    -r data_version "sample-${day}" \
    -p sample_frac 1.0 \
    -p random_seed 17 \
    -r output_dir out \
    -r run_id "$run_id" \
    --kernel python3 --cwd . --execution-timeout 600 --log-output || exit 1
done
```

This shell loop is illustrative: create the three fixture files or adapt the data-version resolver before running it. A production scheduler should not fabricate snapshot IDs; resolve them from the actual data platform. Export HTML only after a run succeeds and passes artifact/privacy checks.

### Example quality assertions — Python cell

```python
required_columns = {"order_id", "order_total", "created_at"}
missing_columns = required_columns - set(orders.columns)
if missing_columns:
    raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

if orders["order_id"].duplicated().any():
    raise ValueError("Duplicate order_id values detected")
if orders["order_total"].isna().mean() > 0.02:
    raise ValueError("order_total missingness exceeded 2% threshold")
if (orders["order_total"].dropna() < 0).any():
    raise ValueError("Negative order_total values require investigation")
```

Thresholds are illustrative and must be justified by the dataset's contract. A quality failure should fail the run with an actionable error, not silently drop records.

## 15. Common mistakes

- The parameters cell is missing the exact `parameters` tag, or CLI names do not match notebook variables.
- Source and executed notebook paths are identical, overwriting the reviewed source.
- A relative path works locally but fails because the runner's working directory differs.
- A run records `data_path` but not an immutable data version or fingerprint.
- Missing Git/package metadata crashes provenance collection or is replaced with a fabricated value.
- A retry repeats an email, write, or other side effect.
- `nbstripout` is assumed to remove secrets from source cells, attachments, metadata, or Git history.
- `--no-input` or a `remove-output` tag is treated as a security boundary.
- CI suppresses warnings, depends on production credentials, or uploads raw outputs without access/retention review.
- Jupytext pairing drifts or strips metadata needed for Papermill.
- A timeout is mistaken for proof that no side effect occurred.
- An executed notebook or log is published even though the process failed.

## 16. Self-check

1. **How does Papermill inject parameters and where do results go?** Explain the `parameters` cell tag, injected-parameters cell, source/output separation, and the executed notebook's role as a run record.
2. **Which controls prevent secrets and PII from leaking through `.ipynb` files?** Explain least privilege, secret scanning, targeted redaction, review of source/outputs/attachments/metadata/logs, artifact access control, retention, and why nbstripout alone is insufficient.
3. **Build a parameterized report notebook, execute it for three dates in CI, and attach HTML artifacts.** Define the parameter contract, unique output/run IDs, sample data, quality thresholds, provenance, timeout/retry policy, tests, secret scan, and artifact retention.

## Further practice

- Compare Papermill with nbconvert execution and Quarto rendering; state which one owns parameter injection and which artifact is produced.
- Demonstrate missing Git metadata and missing package metadata in provenance without failing the report.
- Force a quality-threshold failure and verify the job exits non-zero while preserving restricted diagnostics.
- Inspect the committed notebook after nbstripout and prove that source-cell literals and other non-output content still require separate scanning.
