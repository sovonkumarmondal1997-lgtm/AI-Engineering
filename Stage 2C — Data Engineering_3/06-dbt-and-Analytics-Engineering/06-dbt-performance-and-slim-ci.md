# dbt Performance and Slim CI

> **Roadmap location:** `Stage 2C — Data Engineering_3/06-dbt-and-Analytics-Engineering/06-dbt-performance-and-slim-ci.md`  
> **Scope:** Build performance, warehouse cost, execution artifacts, state selection, deferral, slim CI, warehouse-specific tuning, data diffs, and large-project execution design.  
> **Prerequisites:** A working dbt project, `ref()`/`source()`, staging/intermediate/mart layers, materializations, incremental models, tests, and Git-based development.  
> **Project continuity:** Examples reuse `stg_orders`, `stg_order_items`, `stg_customers`, `int_orders_payments`, `fct_orders`, and `dim_customers`.

## Topic 06 — Learning outcomes

By completing this lesson, you should be able to:

- Explain why a dbt project is slow or expensive and separate model runtime from end-to-end build duration.
- Use `run_results.json` and the DAG to find bottlenecks and estimate the critical path.
- Benchmark thread counts and materializations reproducibly rather than guessing.
- Use `state:modified+`, `--state`, and `--defer` correctly.
- Design slim CI with a production-state manifest, a separate PR schema, and reliable cleanup.
- Choose incremental, partitioning, clustering, and warehouse settings for the relevant platform.
- Use `dbt clone` only where supported and appropriate.
- Control expensive tests, failures, query attribution, and per-domain workloads.
- Compare changed model outputs with data-diff tools without treating row-count equality as proof of correctness.
- Understand the limits of large-project decomposition, dbt Mesh, faster parsing, and dbt Fusion.

---

## 1. Performance is a measurement problem first

The goal is not to make every command run faster at any cost. The goal is to reduce end-to-end feedback time and warehouse spend while preserving correctness, consumer contracts, and production safety.

Measure at least four dimensions separately:

1. **Elapsed time:** wall-clock time from command start to finish.
2. **Critical-path time:** longest dependency-constrained path through the selected DAG, accounting for execution and scheduling.
3. **Resource consumption/cost:** warehouse credits, bytes scanned, slot-ms, DBUs, CPU, memory, or query charges, depending on the platform.
4. **Correctness and confidence:** required tests, data comparisons, and deployment gates that still run.

A change that cuts a single model from 10 minutes to 5 minutes may not reduce total build time if that model is not on the critical path. Increasing threads may shorten elapsed time while increasing contention or cost. Replacing a table with a view can reduce build work but make every downstream query slower or more expensive.

### 1.1 Why dbt builds become slow

| Cause | Mechanism | First investigation |
|---|---|---|
| Too many selected models | Every selected resource adds work and scheduling overhead | Selection, project graph, command scope |
| Wrong materialization | Views push work to consumers; tables rebuild large results; ephemeral models duplicate compiled SQL | Materialization, query plans, downstream use |
| Wide full-table rebuild | Recomputes historical data that has not changed | Rows/bytes processed, incremental feasibility |
| Serial dependencies | A long chain prevents downstream work from starting early | DAG critical path, parent/child relationships |
| Expensive joins/windows | Large scans, skew, poor join order, spilling | Warehouse query profile and query history |
| Too many threads | Resource contention, queueing, warehouse saturation | Runtime and cost across a controlled thread sweep |
| Too few threads | Independent models wait unnecessarily | Runnable DAG width and warehouse capacity |
| Slow parsing/large project | Compilation and parsing overhead dominates small runs | Command timing, project size, parser/engine versions |
| Expensive tests | Large scans or repeated validation queries | Test query history and scheduling policy |
| Data layout mismatch | Full scans despite filters or poor pruning | Partition/clustering design, bytes scanned |
| Warehouse queueing | Queries wait for resources or concurrency slots | Queue time vs execution time |
| Unbounded downstream work | A model change fans out to many descendants | `state:modified+`, DAG fan-out, domain selectors |

Do not assume a model is slow because its SQL file is long. A short query can scan a huge table; a complex query can be fast if the engine prunes data and uses an effective plan.

### 1.2 Materialization trade-offs

- **View:** usually cheap to create/update, but its query logic runs when consumers query it. Deep view chains can produce expensive downstream queries.
- **Table:** pays compute cost during build and stores the result. Useful for expensive transformations reused by many consumers, but full refreshes can be costly.
- **Incremental:** processes a subset of data according to a unique key, watermark, partition strategy, or adapter-specific merge behavior. It needs correct handling of late-arriving updates, deletes, deduplication, and backfills.
- **Ephemeral:** compiles into downstream SQL rather than creating a warehouse relation. Useful for small reusable logic, but can duplicate logic and increase downstream query complexity.
- **Materialized view:** maintained by warehouse-specific behavior and constraints. Refresh semantics, supported SQL, freshness, and cost differ by platform.

Choose based on the frequency of change, volume, reuse, consumer query patterns, freshness requirement, and warehouse behavior. Do not convert a model to incremental just because it is large; first define its change-detection and correction strategy.

### 1.3 Threads and DAG parallelism

`threads` is configured in the dbt profile for a target. dbt can run independent ready nodes concurrently, but a node cannot start until its dependencies are ready. A project with 50 independent staging models can exploit more concurrency than a chain of 50 dependent models.

More threads can help when:
- many selected models are independent;
- the warehouse can execute them concurrently;
- the bottleneck is runnable dbt work, not warehouse saturation.

More threads can hurt when:
- queries compete for memory, slots, or warehouse resources;
- the platform queues work or auto-scales expensively;
- concurrent builds contend with production;
- a small number of long serial nodes dominate the DAG.

Example profile (illustrative; adapt the adapter and credentials):

```yaml
analytics:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: analytics.duckdb
      threads: 4
```

For other adapters, retain the adapter-specific required fields. Do not copy a DuckDB profile into a Snowflake/BigQuery/Databricks project. Threads are a client-side concurrency setting; they are not equivalent to warehouse size, BigQuery slots, or Databricks cluster capacity.

---

## 2. Measure model runtimes and find the critical path

### 2.1 Read `run_results.json`

A successful dbt command commonly writes `target/run_results.json`. It contains the results of resources included in that invocation, including fields such as `unique_id`, `status`, and `execution_time`; available fields depend on dbt version and resource type. It does not contain the complete project graph. Use `manifest.json` for dependency edges.

Example `run_results.json` shape (simplified illustrative data, not a real benchmark):

```json
{
  "metadata": {
    "dbt_version": "1.x",
    "invocation_id": "example-invocation"
  },
  "results": [
    {
      "unique_id": "model.analytics.stg_orders",
      "status": "success",
      "execution_time": 12.4
    },
    {
      "unique_id": "model.analytics.int_orders_payments",
      "status": "success",
      "execution_time": 48.1
    },
    {
      "unique_id": "model.analytics.fct_orders",
      "status": "success",
      "execution_time": 20.7
    }
  ]
}
```

Times above are seconds, for illustration only. Do not treat this tiny example as representative. Actual result objects may also include timing phases, adapter response, message, failures, and other fields.

A simple script can rank the 10 slowest executed resources:

```python
#!/usr/bin/env python3
"""Print the 10 slowest results from one dbt invocation."""

import json
from pathlib import Path

payload = json.loads(Path("target/run_results.json").read_text(encoding="utf-8"))
results = payload.get("results", [])

def duration(result):
    try:
        return float(result.get("execution_time", 0.0))
    except (TypeError, ValueError):
        return 0.0

for item in sorted(results, key=duration, reverse=True)[:10]:
    print(
        f"{duration(item):8.2f}s  "
        f"{item.get('status', 'unknown'):12} "
        f"{item.get('unique_id', '<unknown>')}"
    )
```

This ranking is useful for triage but is **not** a critical-path analysis. It also ranks tests and other resources if they are present in `results`; filter by `unique_id` prefix or join against `manifest.json` if you only want models. `execution_time` is not necessarily pure warehouse execution time and may include adapter/client overhead.

### 2.2 Critical path versus slowest node

The critical path is the longest dependency-constrained route through the selected DAG. For each node, a simplified earliest-finish calculation is:

\[
EF(v) = duration(v) + \max_{p \in parents(v)} EF(p)
\]

For a node with no selected parent, \(EF(v)=duration(v)\). The maximum \(EF\) across terminal nodes estimates the critical path under a simple serial-per-node model. Real dbt runs add scheduling delays, concurrent resource contention, and non-model tasks; use this as a diagnostic estimate, not a perfect reconstruction of scheduler behavior.

For example, imagine:
- chain A: 30s → 40s → 50s = 120s;
- independent chain B: 70s → 20s = 90s;
- a separate model takes 100s.

The 100-second model is the slowest single model, but chain A's 120 seconds is the longer dependency path. If the 100-second model is independent, it may overlap with chain A and not determine the total elapsed time.

### 2.3 Python critical-path estimator

Save as `scripts/critical_path.py`. It reads `manifest.json` for edges and `run_results.json` for observed durations. It estimates critical paths only for resources with duration results; missing nodes are reported rather than assigned invented durations.

```python
#!/usr/bin/env python3
"""Estimate dbt model critical paths from manifest edges and run results."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def load(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(manifest_path: str, results_path: str) -> int:
    manifest = load(manifest_path)
    run_results = load(results_path)

    nodes: dict[str, Any] = manifest.get("nodes", {})
    parents: dict[str, list[str]] = manifest.get("parent_map") or {}
    durations: dict[str, float] = {}

    for result in run_results.get("results", []):
        uid = result.get("unique_id")
        value = result.get("execution_time")
        if not uid or value is None:
            continue
        try:
            durations[uid] = max(0.0, float(value))
        except (TypeError, ValueError):
            continue

    # Restrict the estimate to model nodes that have durations in this invocation.
    selected = {
        uid for uid, node in nodes.items()
        if node.get("resource_type") == "model" and uid in durations
    }
    if not selected:
        print("No model nodes with execution_time found in run_results.json.")
        return 1

    # Dependencies among the selected, measured models only.
    deps = {uid: [p for p in parents.get(uid, []) if p in selected] for uid in selected}
    children: dict[str, list[str]] = {uid: [] for uid in selected}
    indegree = {uid: len(deps[uid]) for uid in selected}
    for uid, upstream in deps.items():
        for parent in upstream:
            children[parent].append(uid)

    queue = sorted(uid for uid, degree in indegree.items() if degree == 0)
    finish: dict[str, float] = {}
    predecessor: dict[str, str | None] = {uid: None for uid in selected}

    while queue:
        uid = queue.pop(0)
        upstream = deps[uid]
        if upstream:
            best_parent = max(upstream, key=lambda parent: finish.get(parent, 0.0))
            predecessor[uid] = best_parent
            start_time = finish.get(best_parent, 0.0)
        else:
            start_time = 0.0
        finish[uid] = start_time + durations[uid]

        for child in children[uid]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
                queue.sort()

    if len(finish) != len(selected):
        print("Could not process all selected models; the graph may contain a cycle or invalid nodes.")
        return 2

    terminal = max(finish, key=finish.get)
    path: list[str] = []
    cursor: str | None = terminal
    while cursor is not None:
        path.append(cursor)
        cursor = predecessor[cursor]
    path.reverse()

    print(f"Estimated model-only critical path: {finish[terminal]:.2f}s")
    for uid in path:
        node = nodes.get(uid, {})
        print(f"  {durations[uid]:8.2f}s  {node.get('name', uid)} [{uid}]")

    missing = sorted(uid for uid in selected if uid not in finish)
    if missing:
        print(f"Unprocessed measured models: {len(missing)}")
    print(
        "Caveat: dependencies whose parent has no duration result are excluded "
        "from this estimate; scheduling and warehouse contention are not modeled."
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/critical_path.py target/manifest.json target/run_results.json")
        raise SystemExit(2)
    try:
        raise SystemExit(main(sys.argv[1], sys.argv[2]))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Unable to read dbt artifacts: {exc}", file=sys.stderr)
        raise SystemExit(2)
```

Run after a representative build:

```bash
dbt build
python scripts/critical_path.py target/manifest.json target/run_results.json
```

**Interpretation:** this is a static model-only approximation. If a dependency is a source, seed, test, snapshot, or other resource not included as a measured model, the estimator treats that missing-duration dependency as outside the selected subgraph. For high-confidence analysis, include compatible durations for all relevant nodes, inspect `run_results.json` timing details, and compare with the actual scheduler logs and warehouse query history.

### 2.4 Correlate with warehouse query history

Use the adapter's query history/profiling interface to distinguish:
- queue/wait time;
- execution time;
- bytes scanned or partitions scanned;
- rows read/written;
- spills, shuffle, skew, and memory pressure;
- warehouse/slot/cluster size;
- query cost or resource consumption.

A model runtime is not a cost metric. A quick query may scan a large amount of data; a slow query may be waiting for a warehouse or concurrency slot. Query-history fields and retention differ by platform and permission. Correlate using a stable query comment, invocation ID, model identifier, query tag, or timestamp window rather than relying only on SQL text matching.

---

## 3. Reproducible performance benchmarking

A valid benchmark compares equivalent work under controlled conditions. Never report an improvement from unrelated runs without noting the confounders.

### 3.1 Benchmark protocol

1. Pin dbt, adapter, package, and warehouse versions/configuration.
2. Choose a fixed commit and fixed data snapshot or dataset.
3. Separate cold-start and warm-cache runs; record which one is being compared.
4. Capture baseline full-build wall time, per-model durations, critical path, warehouse cost/resource usage, and test outcomes.
5. Change one variable at a time: thread count first, then materialization, then physical layout.
6. Repeat each scenario several times; report median and range, not the best run.
7. Keep target schema, warehouse size, query cache behavior, and concurrency conditions comparable.
8. Confirm data correctness with tests and representative data comparisons.
9. Record exact commands, timestamps, commit SHA, and artifacts.
10. Roll back a change that only shifts cost to consumers or reduces confidence without a justified trade-off.

### 3.2 Thread sweep

Example matrix; **numbers are planned test settings, not measured results**:

| Run | Threads | Warehouse/cluster | Cache condition | Measured outputs |
|---|---:|---|---|---|
| A | 1 | Fixed | Cold or documented | Wall time, critical path, cost, failures |
| B | 2 | Same | Same policy | Same outputs |
| C | 4 | Same | Same policy | Same outputs |
| D | 8 | Same | Same policy | Same outputs |

Use a different target profile or environment variable per run; do not modify production settings while benchmarking. Stop increasing threads when elapsed time stops improving, queue time grows, resource consumption increases disproportionately, or production contention appears.

### 3.3 Materialization experiment

Choose one expensive model with known semantics and representative downstream consumers. Compare:
- current materialization;
- a table materialization if currently a view and repeated query cost is material;
- an incremental design if the model has a correct change-detection/backfill strategy.

Measure both build and downstream query cost. A view-to-table change may make builds slower but consumers faster. An incremental conversion may reduce routine work while making backfills and late-arriving corrections more complex. A full refresh must remain possible and tested.

A results template:

```text
Commit:
Dataset/snapshot:
dbt + adapter versions:
Warehouse/cluster:
Cache policy:
Scenario:
Command:
Median wall time:
Critical-path estimate:
Total query/resource cost:
Top model runtimes:
Rows/bytes processed:
Tests/data-diff result:
Known confounders:
Decision and rollback trigger:
```

Do not fill the table with invented values. Use actual observations from your environment.

---

## 4. Intermediate: state selection, `--state`, and `--defer`

### 4.1 What `state:modified+` means

dbt state selection compares the current parsed project to a prior state manifest supplied through `--state`. The selector `state:modified` selects resources dbt considers modified under the selected comparison semantics; the trailing `+` selects their descendants as well.

```bash
dbt ls --select state:modified+ --state prod_artifacts
dbt build --select state:modified+ --state prod_artifacts
```

The second command is a state-based build but does **not** enable deferral. Whether a changed node is selected depends on the manifest comparison, including changes to code/config/metadata and how dbt's state selector defines modifications in your version. Confirm behavior in the installed version's docs and inspect `dbt ls` output before using it as a release gate.

Selection semantics to remember:

- `state:modified` — modified resources identified by comparison with the state manifest.
- `state:modified+` — those resources plus downstream descendants.
- `+state:modified` is not a universal equivalent in all selector combinations; use the documented selector grammar and verify with `dbt ls`.
- `--state prod_artifacts` — tells dbt where the comparison manifest lives.
- `--defer` — allows references to eligible unselected resources to resolve to relations represented in the state manifest, instead of requiring every upstream relation to be rebuilt in the current target. It does not itself select resources.
- `--defer` without a usable state manifest does not provide the intended production fallback.

### 4.2 Production state artifacts

Keep the state manifest from the **successful production deployment** separate from the CI build's target directory. Commonly, the state directory contains a production `manifest.json`; a complete artifact bundle may also contain `run_results.json` and `catalog.json` for other analyses. State selection primarily needs the manifest.

Recommended artifact practice:
- generate artifacts from the production code/target after a successful deploy;
- store them immutably or version them by commit/deployment;
- record the commit SHA, dbt version, environment, and generated time;
- retrieve a known successful production artifact into `prod_artifacts/`;
- avoid overwriting the state manifest while the CI command is using it;
- ensure credentials allow access to production artifact storage but do not expose secrets in logs.

### 4.3 What `--defer` does and does not do

Example branch command:

```bash
dbt build \
  --select state:modified+ \
  --defer \
  --state prod_artifacts \
  --target ci \
  --target-path target-ci
```

The target `ci` should write to an isolated PR schema. For selected nodes, dbt builds into the CI target. For references to unselected nodes, deferral can resolve the reference to the corresponding relation in the state manifest (typically the production relation), subject to resource type, manifest contents, and dbt version behavior.

Deferral is not a data copy and not a full environment clone. It can make CI faster by reusing existing production relations, but:
- a production relation must exist and be accessible;
- the CI role needs appropriate read permissions;
- deferred upstream data may differ from what a branch would produce if the upstream model were rebuilt;
- unselected changes are not automatically built;
- deferred resources can point at a different environment than the PR target;
- tests must be designed with that environment mix in mind.

Use `dbt ls --select state:modified+ --state prod_artifacts` first to review selection. Consider `--favor-state` only if you understand the version-specific semantics and intentionally want state relations to take precedence in cases where a current-target relation also exists. Do not add flags from old examples without checking the installed CLI.

### 4.4 Common state-selection workflow

```bash
# 1. Retrieve the manifest produced by the latest successful production deployment.
#    Exact download mechanism depends on your artifact store.

# 2. Verify the artifact and inspect the selected nodes.
test -s prod_artifacts/manifest.json
dbt ls --select state:modified+ --state prod_artifacts

# 3. Build the changed resources and descendants in an isolated target.
dbt build \
  --select state:modified+ \
  --defer \
  --state prod_artifacts \
  --target ci \
  --target-path target-ci
```

If the selector produces no nodes, do not silently assume success means the intended PR was tested. Check whether the state artifact is stale, whether the changed files affect dbt resources, and whether the selection comparison is appropriate for the project.

### 4.5 Slim CI is a selection strategy, not a correctness shortcut

Slim CI aims to run the necessary subset of a project for a pull request. It commonly combines:
- comparison against a production manifest;
- selection of changed resources and descendants;
- deferral to production for eligible unselected upstreams;
- an isolated schema/database/catalog for the PR;
- tests and required policy checks;
- cleanup after the PR closes.

It should still run repository-wide checks that are cheap and important, such as parsing, linting, selector validation, and documentation/governance checks. Some changes—global macros, packages, project config, dispatch logic, or shared model contracts—can have broad impact. A safe pipeline may widen selection or run a full build for those changes.

---

## 5. Per-PR schemas and cleanup

### 5.1 Isolation model

A PR schema prevents one branch's relations from overwriting another branch or production. The schema name must be unique, deterministic, sanitized, and limited to a controlled character set. Use a distinct dbt target and separate `target-path` for CI output; do not put the production state manifest inside a directory dbt overwrites during the run.

Example profile fragment:

```yaml
analytics:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: analytics.duckdb
      schema: analytics_dev
      threads: 4
    ci:
      type: duckdb
      path: analytics_ci.duckdb
      schema: "{{ env_var('DBT_SCHEMA', 'analytics_ci') }}"
      threads: 4
```

This is an illustrative DuckDB profile fragment; other adapters require different connection fields and may represent schema/database isolation differently. In CI, set `DBT_SCHEMA=ci_pr_123` (a sanitized PR identifier). For shared warehouses, ensure model configuration does not override the PR schema unexpectedly and that the CI role cannot write to production schemas.

### 5.2 Cleanup

Cleanup must run when the PR closes and after failures when possible. Use a least-privilege cleanup role that can drop only the expected CI schemas. Validate schema names before constructing SQL; never interpolate arbitrary untrusted branch text into a DDL statement.

A dbt macro can provide adapter-aware schema deletion:

```jinja
-- macros/drop_ci_schema.sql
{% macro drop_ci_schema(schema_name) %}
  {% if not modules.re.match('^ci_pr_[0-9]+$', schema_name) %}
    {{ exceptions.raise_compiler_error(
      "Refusing to drop schema outside the ci_pr_<digits> naming convention"
    ) }}
  {% endif %}

  {% set relation = api.Relation.create(
      database=target.database,
      schema=schema_name,
      identifier=none
  ) %}
  {% do adapter.drop_schema(relation) %}
{% endmacro %}
```

The `target.database` and adapter relation behavior vary by adapter; verify the macro on the chosen adapter and adapt relation construction where required. Run only with a controlled value:

```bash
dbt run-operation drop_ci_schema --args '{"schema_name": "ci_pr_123"}' --target ci
```

The macro's allowlist is an important safety guard, not a substitute for warehouse permissions. Validate that the selected `ci` target's database is the expected non-production database before enabling automated cleanup. If your adapter does not support this pattern, use a reviewed adapter-specific cleanup script.

Also run scheduled cleanup for abandoned schemas, since PR close events can be missed, cancelled, or lack credentials. Apply an age threshold and allowlist so the job cannot drop unrelated schemas.

---

## 6. GitHub Actions slim-CI example

This is an adapter-configurable workflow pattern using AWS S3 for the production state manifest. The production-state retrieval job does not check out or execute pull-request code; the separate build job receives only the manifest artifact. The build job still executes PR-controlled SQL, Jinja, macros, packages, and hooks, so its warehouse identity must be restricted to disposable CI schemas and read-only access to deferred production relations.

Assumptions:
- A successful production deployment publishes `manifest.json` to `s3://YOUR_BUCKET/dbt/prod/manifest.json`.
- The AWS OIDC trust policy is restricted to the intended repository and protected `dbt-state-read` environment; the role has read-only access to this one artifact path.
- The repository has a `ci` dbt target and a reviewed profile that honors `DBT_SCHEMA`.
- Warehouse credentials are injected through a protected GitHub Environment and are least-privilege. Do not expose production write credentials to PR builds.
- Protect workflow files with required review/CODEOWNERS. For stronger isolation, put the credentialed artifact-retrieval workflow in a centrally managed reusable workflow on a protected branch.
- This example intentionally skips fork PRs for credentialed slim CI. Run uncredentialed lint/parse checks separately for fork PRs.

Create `.github/workflows/dbt-slim-ci.yml`:

```yaml
name: dbt slim CI

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

permissions:
  contents: read

concurrency:
  group: dbt-pr-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  fetch-prod-state:
    if: github.event.pull_request.draft == false && github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    environment: dbt-state-read
    permissions:
      contents: read
      id-token: write
    steps:
      - name: Configure AWS credentials with OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.DBT_STATE_READ_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}

      - name: Retrieve production state manifest
        run: |
          mkdir -p prod_artifacts
          aws s3 cp s3://YOUR_BUCKET/dbt/prod/manifest.json prod_artifacts/manifest.json
          test -s prod_artifacts/manifest.json

      - name: Upload state manifest for the build job
        uses: actions/upload-artifact@v4
        with:
          name: prod-state-manifest
          path: prod_artifacts/manifest.json
          if-no-files-found: error
          retention-days: 1

  slim-ci:
    needs: fetch-prod-state
    if: github.event.pull_request.draft == false && github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    environment: dbt-ci
    permissions:
      contents: read
    env:
      DBT_SCHEMA: ci_pr_${{ github.event.pull_request.number }}
      DBT_PROFILES_DIR: ${{ github.workspace }}/.ci/profiles
      DBT_TARGET: ci
    steps:
      - name: Checkout PR
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Download production state manifest
        uses: actions/download-artifact@v4
        with:
          name: prod-state-manifest
          path: prod_artifacts

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install pinned dbt dependencies
        run: |
          python -m pip install --upgrade pip
          # requirements-dbt.txt must pin dbt, the adapter, and package versions.
          pip install -r requirements-dbt.txt

      - name: Parse and inspect selection
        run: |
          dbt deps
          dbt parse --target ci --target-path target-ci
          dbt ls --select state:modified+ --state prod_artifacts --target ci --target-path target-ci

      - name: Build changed resources and descendants
        run: |
          dbt build \
            --select state:modified+ \
            --defer \
            --state prod_artifacts \
            --target ci \
            --target-path target-ci

      - name: Run project-specific documentation and governance checks
        run: python scripts/audit_dbt_docs.py target-ci/manifest.json

      - name: Upload diagnostic artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: dbt-ci-pr-${{ github.event.pull_request.number }}
          path: |
            target-ci/manifest.json
            target-ci/run_results.json
          if-no-files-found: ignore
          retention-days: 7
```

**Important adjustments before use:**
- Pin action versions to reviewed commit SHAs according to your organization's supply-chain policy. The major-version tags above are illustrative, not a claim that the workflow was executed.
- Add the selected adapter's profile and credential variables to the protected `dbt-ci` environment. The profile must route writes to `ci_pr_<number>` and must not permit writes to production schemas.
- Keep `prod_artifacts/manifest.json` outside the `target-ci` output directory. Publish production artifacts only after a successful deployment and keep each manifest immutable during a CI run.
- `dbt parse` and `dbt ls` flags vary by installed dbt version; verify with `--help` and inspect the selected set before treating it as a gate.
- A PR changing macros, package dependencies, project config, or shared infrastructure may need broader validation than `state:modified+`.
- Cancellation can leave a schema behind. Keep cleanup independent of the build job's success path and run an abandoned-schema janitor.
- The manifest artifact is metadata, not a copy of production data. The CI role still needs appropriate read access to any deferred relations, but should not have production write access.

### 6.1 PR-close cleanup workflow

Use a separate cleanup workflow and check out the trusted default branch—not the PR head—so a PR cannot replace the cleanup macro that runs with the cleanup identity. The profile and macro must be reviewed, adapter-specific, and limited to the CI schema naming convention. Configure the protected `dbt-ci-cleanup` environment with the least-privilege credentials referenced by that profile.

```yaml
name: dbt PR schema cleanup

on:
  pull_request:
    types: [closed]

permissions:
  contents: read

jobs:
  cleanup:
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    environment: dbt-ci-cleanup
    permissions:
      contents: read
    env:
      DBT_SCHEMA: ci_pr_${{ github.event.pull_request.number }}
      DBT_PROFILES_DIR: ${{ github.workspace }}/.ci/profiles
    steps:
      - name: Checkout trusted default branch
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.repository.default_branch }}

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install pinned dbt dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dbt.txt

      - name: Validate schema name
        shell: bash
        run: |
          [[ "$DBT_SCHEMA" =~ ^ci_pr_[0-9]+$ ]]

      - name: Drop the PR schema using the reviewed macro
        run: |
          dbt deps
          dbt run-operation drop_ci_schema \
            --args "{\"schema_name\": \"${DBT_SCHEMA}\"}" \
            --target ci
```

This cleanup template is only executable after the adapter-specific `profiles.yml`, protected credential variables, and reviewed `drop_ci_schema` macro are present on the default branch. The macro must verify the expected non-production database as well as the allowlisted schema name. Restrict cleanup credentials to the CI namespace; if cleanup fails, alert the platform owner and let a scheduled, age-based janitor reconcile abandoned schemas. Do not use an unconditional shell `DROP SCHEMA` with unvalidated input.

---

## 7. Incremental conversion, partitioning, and clustering

### 7.1 Incremental model design

Incremental models are appropriate when the transformation can correctly identify new or changed records and when routine processing is substantially cheaper than full rebuilds.

Example pattern for an order staging/intermediate model (adapt the unique key, timestamp, and SQL dialect to the real source):

```sql
{{
  config(
    materialized='incremental',
    unique_key='order_id'
  )
}}

select
    order_id,
    customer_id,
    order_date,
    status,
    updated_at
from {{ ref('stg_orders') }}

{% if is_incremental() %}
where updated_at >= (
    select coalesce(max(updated_at), cast('1900-01-01' as timestamp))
    from {{ this }}
)
{% endif %}
```

This is illustrative, not universally safe. A strict `>` watermark can miss records with equal timestamps; `>=` can reprocess boundary records. A late update to a record with an older `updated_at`, source deletes, timestamp precision, and timezone differences require explicit handling. Validate the strategy with a backfill, late-arriving update, duplicate, and delete scenario. The `unique_key` strategy and merge semantics vary by adapter.

### 7.2 Partitioning and clustering

- **Partitioning** divides a table by a supported partition key such as date. Queries must filter the partition key in a way the optimizer can prune.
- **Clustering** organizes data to improve access for common predicates or joins. Benefit depends on data distribution and workload; clustering is not a substitute for correct filters.
- **Incremental processing** controls which rows are transformed. Partitioning/clustering controls physical data layout. They solve related but different problems.

Do not add partitions or clustering keys based only on column popularity. Inspect actual query history, filter selectivity, table size, maintenance overhead, and workload patterns.

### 7.3 Warehouse-specific tuning comparison

| Platform | Candidate levers | What to measure | Important caveat |
|---|---|---|---|
| Snowflake | Warehouse size, auto-suspend/auto-resume, concurrency/multi-cluster settings, query profile, model/query tags, adapter-specific `snowflake_warehouse` config when supported | Credits, queue time, spill, scan volume, elapsed time | Bigger warehouse can finish sooner but cost more; adapter config names/options are version-dependent |
| BigQuery | Partition filters, clustering, bytes processed, slot-ms, reservation/edition capacity, query plan | Bytes scanned, slot consumption, shuffle, elapsed time, cost model | `require_partition_filter` and partition pruning are table/query design concerns; slots and on-demand billing behave differently |
| Databricks | Delta table layout, liquid clustering where supported, file sizes, query profile, cluster/SQL warehouse sizing | DBUs, scan/shuffle, file pruning, spill, wall time | Liquid clustering support depends on table format/runtime/warehouse and is not a generic dbt setting |
| DuckDB | `threads`, memory limit, temp directory, file format/layout, query plan | CPU, memory, spill/temp usage, elapsed time | Local CPU/disk and concurrency limits differ from a managed cloud warehouse |

#### Snowflake

Tune warehouse size using measured query profile and workload. A larger warehouse may reduce elapsed time but increase credit burn; auto-suspend can reduce idle spend but too-aggressive suspension can increase startup latency. Snowflake adapter configurations may allow model-level warehouse routing (often expressed through `snowflake_warehouse` in supported adapter versions); verify the adapter docs and ensure warehouses exist and roles have access.

#### BigQuery

Partition large tables by a field aligned with common filters, and make queries filter that partition column. Use clustering for common selective filters/joins where it improves pruning. Inspect bytes processed, slot-ms, shuffle, and execution stages. Avoid assuming more slots always fix a poor join or a query that scans every partition. Partition filters and slot reservations are configured at table/project/job level and are not identical to dbt thread count.

#### Databricks

Liquid clustering can improve data skipping and layout for supported Delta tables/runtime configurations, but it is a platform feature rather than a universal dbt option. Confirm table format, runtime, catalog/compute, and adapter support. Compare scan volume, file pruning, shuffle, and DBU consumption before and after. Do not run layout maintenance on every build without measuring the cost.

#### DuckDB

Start with a controlled `threads` sweep, observe CPU/memory and temporary disk use, and keep input files and cache policy consistent. More threads may not improve a storage-bound or single-query workload. Avoid comparing a warm-cache local run with a cold-cache CI run and calling it a materialization improvement.

---

## 8. Advanced: clone, data diffs, tests, and release gates

### 8.1 `dbt clone`

`dbt clone` can create target relations that reference or clone existing state relations on platforms/adapters that support the relevant clone semantics. Its value is to provision a test environment without rebuilding every unchanged upstream model. Availability, behavior, and cost depend on dbt version, adapter, and warehouse features; it is not a universal cross-platform zero-copy guarantee.

Before using it:
- verify `dbt clone --help` and the adapter's supported behavior;
- identify the state manifest and target environment;
- check whether the warehouse supports zero-copy cloning or equivalent;
- understand which relation types can be cloned and whether permissions are preserved;
- test cleanup and avoid assuming cloned data is independent in every respect.

Use `--defer` and `dbt clone` for different jobs: deferral resolves references to state relations for unselected resources; clone attempts to materialize/clone selected state relations into the target where supported. Neither makes untested changes safe by itself.

### 8.2 Data diffs with `audit_helper` or comparable tools

A successful build says that the selected resources completed; it does not prove that changed data is equivalent or that the change is semantically correct. Data-diff methods can compare a branch result with a baseline.

Possible approaches:
- `audit_helper` package macros for comparing relations and reporting row/column differences;
- Datafold-style platform integrations or other data-diff tools;
- custom SQL for counts, aggregates, key-level comparisons, or checksums.

Packages and SaaS tools have different installation, permissions, feature, and licensing requirements. Pin and verify the selected tool for your dbt version.

**Minimum meaningful comparison for a changed fact model:**
1. Compare row counts, partition/date counts, and key uniqueness.
2. Compare key sets in both directions to find missing/extra orders.
3. Compare important measures such as `order_total` by day/status and investigate deltas.
4. Compare a sample or full set of business-critical columns where feasible.
5. Use deterministic tolerances for floating-point/rounding differences.
6. Explain expected differences when the PR intentionally changes business logic.

A row-count comparison alone can miss changes where one row disappears and another appears, or a value changes without affecting row count.

Example SQL comparison (adapt dialect and relation names):

```sql
-- Run against a branch/PR relation and a baseline relation.
select 'baseline' as version_name, count(*) as row_count
from analytics_prod.fct_orders
union all
select 'pr' as version_name, count(*) as row_count
from ci_pr_123.fct_orders;
```

This is a smoke check, not a complete data diff. For key-level comparison, adapt to your SQL dialect:

```sql
-- Keys present in baseline but absent in the PR result.
select order_id
from analytics_prod.fct_orders
except
select order_id
from ci_pr_123.fct_orders;
```

Run the reverse comparison too. `EXCEPT` semantics and quoting differ by SQL dialect; some warehouses use `MINUS` or require fully qualified names. For a production-quality check, compare only after both relations are materialized, ensure the baseline is a stable snapshot, and report counts of both missing and extra keys.

### 8.3 Test-cost control

Do not remove important tests simply because they cost money. Design a tiered policy:

- **Every PR:** parse/compile, lint, cheap unit tests, key uniqueness/not-null tests on changed public models, required contract and documentation checks, selected integration tests.
- **Production deployment:** required tests against deployment target, freshness checks, contract checks, and any risk-based reconciliation.
- **Scheduled/nightly:** broad expensive uniqueness/relationship checks, full historical reconciliations, sampled or full distribution checks, high-volume row comparisons.
- **Periodic:** backfill tests, performance baselines, full-refresh validation, and expensive data-diff audits.

Schedule based on risk and change frequency. For high-risk models, expensive checks may still need to block deployment. Sampling reduces cost but can miss rare defects; document the miss risk and retain full checks where required.

### 8.4 `--fail-fast` and `--warn-error`

- `--fail-fast` stops further work after a failure is detected, reducing wasted execution in some cases. It does not undo completed writes or guarantee immediate cancellation of every in-flight warehouse query.
- `--warn-error` promotes dbt warnings to errors; `--warn-error-options` can provide more selective behavior in supported versions. Turning all warnings into errors can expose noisy or environment-specific warnings, so test the policy before enforcing it broadly.

Use strict failure behavior for required CI gates, but retain diagnostic artifacts on failure. Separate non-blocking exploratory checks from release-blocking tests, and make the policy visible to developers.

### 8.5 Cost attribution with `query_comment` and tags

Query comments/tags can help link warehouse query history to a dbt model, invocation, environment, or team. Exact configuration and fields depend on dbt and adapter versions. A common dbt project pattern is to configure query comments using a supported macro/configuration, and use model tags to group resources for selection/reporting.

Illustrative project metadata:

```yaml
models:
  analytics:
    marts:
      +tags: ["domain:commerce", "cost_center:analytics"]
```

Tags are dbt metadata and may not automatically become warehouse query tags. A basic invocation-level comment can be configured in `dbt_project.yml` where supported:

```yaml
query-comment:
  comment: "dbt invocation={{ invocation_id }}"
  append: true
```

This example adds an invocation identifier; it does not by itself guarantee model-level attribution on every adapter. To attribute individual model queries, use the adapter/dbt-version-supported query-comment macro or query-tag mechanism and include only safe identifiers such as the model unique ID, invocation ID, and environment. Confirm those fields actually appear in warehouse query history. Avoid putting secrets, personal data, or unbounded/high-cardinality values in query comments.

### 8.6 Profiling expensive models

For each top candidate:
1. Find its query in the warehouse history using model/invocation identifiers or timestamps.
2. Read the execution plan/profile: scan, join, shuffle, spill, sort, window, and aggregation stages.
3. Confirm row counts and data skew at join keys.
4. Inspect partition pruning and clustering effectiveness.
5. Check whether CTEs are inlined/recomputed or materialized as intended by the warehouse.
6. Simplify filters and projections early where the optimizer benefits.
7. Avoid repeated scans of the same large relation where a reusable intermediate model is justified.
8. Compare the change with the same benchmark protocol and run correctness checks.

Do not blindly rewrite SQL based on style alone. CTE readability is useful, but the warehouse optimizer decides much of the execution plan.

### 8.7 Large projects, selectors, dbt Mesh, and per-domain jobs

As projects grow, separate responsibilities and schedule work by domain when this reduces contention and improves ownership. Use `selectors.yml` for named, reviewable selection rules rather than repeating fragile CLI expressions in every workflow.

Example selector file:

```yaml
selectors:
  - name: commerce_marts
    description: Commerce mart models and their required upstream dependencies.
    definition:
      method: path
      value: models/marts/commerce
```

This selector selects resources in the path; it does not automatically add upstream dependencies. A job that needs upstream nodes may use a documented selector combination or `+` graph operator. Verify selector grammar with `dbt ls --selector commerce_marts` and the installed version.

Example commands:

```bash
# Inspect the selector
dbt ls --selector commerce_marts

# Include ancestors of selected nodes
dbt build --select +path:models/marts/commerce

# Inspect changed resources and descendants against production state
dbt ls --select state:modified+ --state prod_artifacts
```

For large projects, consider:
- per-domain CI jobs and ownership boundaries;
- explicit cross-domain contracts;
- shared packages and stable public models;
- dbt Mesh for cross-project dependencies where the deployment/product capabilities support it;
- versioning and deprecation policies for public interfaces;
- avoiding duplicate jobs that build the same heavy ancestors concurrently.

dbt Mesh is an architectural approach and set of product capabilities, not simply a folder layout. Cross-project references, access controls, metadata exchange, and deployment behavior depend on the dbt product/version and configuration. Verify current support before designing around a feature.

### 8.8 Faster parsing and dbt Fusion awareness

Large projects may spend meaningful time parsing project files before model execution. Keep packages, macros, YAML, and model paths organized; avoid unnecessary project duplication; measure parsing separately from execution. Partial parsing behavior depends on the project and dbt version.

dbt Fusion is a newer engine/authoring experience whose capabilities, availability, adapter support, licensing, and compatibility can change. Treat it as an option to evaluate, not a universal drop-in speed guarantee. Check the current dbt product documentation for supported adapters, features, migration requirements, and operational constraints. Benchmark the same project and workflow before/after adoption.

---

## 9. Hands-on lab — `experiments/06_performance_ci/`

### Lab objectives

Generate a reproducible 100-model project, benchmark a baseline, tune threads and materializations, exercise production-state selection and deferral, implement PR-schema isolation, and compare changed outputs. This lab generates synthetic SQL and does not claim any benchmark result in advance.

### 9.1 Lab layout

```text
experiments/
└── 06_performance_ci/
    ├── README.md
    ├── generate_project.py
    ├── benchmark.sh
    ├── scripts/
    │   ├── critical_path.py
    │   ├── compare_counts.py
    │   └── compare_duckdb_counts.py
    ├── .github/
    │   └── workflows/
    │       ├── dbt-slim-ci.yml
    │       └── dbt-pr-cleanup.yml
    └── benchmark-results/
        └── README.md
```

The generated project is a synthetic performance harness. It is not a substitute for measuring the real commerce models. The primary local lab uses DuckDB because the row-count comparison script queries the generated DuckDB database directly; other adapters need an adapter-specific count-query implementation.

### 9.2 Generate a reproducible 100-model DAG

Save as `generate_project.py`:

```python
#!/usr/bin/env python3
"""Generate a small deterministic dbt project with 100 dependent models.

The generated project is a benchmark harness, not a warehouse-independent
performance guarantee. It uses generic SQL and a DuckDB profile.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path("generated_100_models")
MODEL_COUNT = 100
ROOT.mkdir(parents=True, exist_ok=True)

for folder in ("models/staging", "models/intermediate", "models/marts", "macros"):
    (ROOT / folder).mkdir(parents=True, exist_ok=True)

project_yml = """name: generated_100_models
version: "1.0.0"
config-version: 2
profile: generated_100_models
model-paths: ["models"]
macro-paths: ["macros"]
clean-targets: ["target", "dbt_packages"]
models:
  generated_100_models:
    staging:
      +materialized: view
    intermediate:
      +materialized: view
    marts:
      +materialized: table
"""
(ROOT / "dbt_project.yml").write_text(project_yml, encoding="utf-8")

# A minimal local DuckDB profile. Keep credentials out of source control in
# real projects; this profile is local-only and uses a generated DB file.
profiles_dir = ROOT / ".ci"
profiles_dir.mkdir(exist_ok=True)
(profiles_dir / "profiles.yml").write_text(
    """generated_100_models:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: generated.duckdb
      schema: main
      threads: 4
    ci:
      type: duckdb
      path: generated.duckdb
      schema: "{{ env_var('DBT_SCHEMA', 'ci_lab') }}"
      threads: 4
""",
    encoding="utf-8",
)

for i in range(MODEL_COUNT):
    name = f"model_{i:03d}"
    folder = "models/staging" if i < 10 else (
        "models/intermediate" if i < 80 else "models/marts"
    )
    if i == 0:
        sql = "select 1 as id, 10 as amount\n"
    else:
        parent = f"model_{i - 1:03d}"
        sql = (
            f"select id, amount + {i} as amount\n"
            f"from {{{{ ref('{parent}') }}}}\n"
        )
    (ROOT / folder / f"{name}.sql").write_text(sql, encoding="utf-8")

# Explicit seed/source-free DAG: each model depends on the previous one.
# This is intentionally chain-heavy so critical-path behavior is visible.
print(f"Generated {MODEL_COUNT} models under {ROOT}")
print("Profile: .ci/profiles.yml; set DBT_PROFILES_DIR=.ci before running dbt.")
```

The generated DAG is a chain, which illustrates a dependency-limited workload. For a parallelism experiment, create a second generated topology with multiple independent branches and a final join. Do not interpret results from a chain as evidence that more threads never help in a wider DAG.

Run:

```bash
cd experiments/06_performance_ci
python generate_project.py
cd generated_100_models
export DBT_PROFILES_DIR="$PWD/.ci"
dbt deps
dbt parse
```

**Expected outcome:** 100 model SQL files are created and dbt parses them if the pinned dbt-duckdb version accepts the generated profile and SQL. No benchmark timing is claimed here. The generated model names are `model_000` through `model_099`; they intentionally do not replace the real project model names.

### 9.3 Baseline full build and artifacts

The lab layout includes `benchmark.sh`; save the following file at `experiments/06_performance_ci/benchmark.sh` and make it executable. It uses the platform's `time` utility to record real elapsed time and propagates the dbt command's exit status.

```bash
#!/usr/bin/env bash
set -euo pipefail
if ! command -v dbt >/dev/null 2>&1; then
  echo "dbt is not installed or is not on PATH" >&2
  exit 127
fi
exec /usr/bin/time -p dbt build "$@"
```

Run from the generated project root after the setup in Section 9.2:

```bash
dbt clean
../benchmark.sh --target dev --target-path target-baseline
python ../scripts/critical_path.py target-baseline/manifest.json target-baseline/run_results.json
```

If using the lab tree exactly as written, copy the critical-path script into `generated_100_models/scripts/` or adjust the path to the location where you saved it. Run the command from the generated project root.

Record:
- dbt/adapter/Python versions;
- OS, CPU/memory, disk type;
- `threads`;
- cold/warm cache condition;
- wall-clock duration;
- top 10 models;
- critical-path estimate;
- result statuses and any errors.

The sample chain has only one ready model at a time, so increasing threads should not be expected to create meaningful DAG parallelism. This is a structural expectation, not a measured result.

### 9.4 Tune threads and materializations

Run the same project and dataset at controlled thread settings, changing one variable at a time. Because the example chain is serial, a better thread benchmark needs a branching topology; generate or construct that topology before concluding that thread count is irrelevant.

For each setting, preserve separate output directories and record actual timings. Run sequentially against the same local database, not concurrently:

```bash
../benchmark.sh --threads 1 --target dev --target-path target-t1
../benchmark.sh --threads 2 --target dev --target-path target-t2
../benchmark.sh --threads 4 --target dev --target-path target-t4
```

`--threads` is available in supported dbt CLI versions; verify `dbt build --help` for your installed version. If your version/adapter does not support this override, edit the profile and record the change. Do not run concurrent benchmarks against the same schema or database file.

To compare materializations, change only a subset of models or project-level config and record the exact diff. Rebuild with a clean target schema/database for a full-rebuild baseline. For incremental experiments, run at least two builds with a controlled new/updated input and verify late-arriving changes and duplicate handling. Do not compare a cold full table build with a warm incremental run as if they were equivalent.

Use `benchmark-results/README.md` to record real measurements. Suggested template:

```text
Run ID:
Commit:
dbt/adapter:
Topology (chain/branches):
Threads:
Materialization:
Cache state:
Command:
Wall time:
Critical path:
Top 10 runtimes:
Warehouse/resource cost:
Correctness checks:
Notes:
```

### 9.5 Save production artifacts and exercise state selection

In the real project, after a successful production deployment, archive `target/manifest.json` (and optionally `run_results.json` and `catalog.json`) under a versioned artifact location. For this local lab, copy a baseline manifest into a separate state directory:

```bash
mkdir -p prod_artifacts
cp target-baseline/manifest.json prod_artifacts/manifest.json

# Modify one model's SQL or configuration, then isolate branch outputs in a separate schema.
export DBT_SCHEMA=ci_state_test
dbt parse --target ci --target-path target-branch

# Inspect the selected set before building.
dbt ls --resource-type model --select state:modified+ --state prod_artifacts --target ci --target-path target-branch --output name

# Build changed resources and descendants into ci_state_test, deferring eligible unselected refs to baseline relations.
dbt build \
  --select state:modified+ \
  --defer \
  --state prod_artifacts \
  --target ci \
  --target-path target-branch
```

For a real CI environment, use a unique schema per PR. The local DuckDB profile writes selected branch models to `ci_state_test` while the baseline relations remain in `main`; this is essential because writing selected models back into `main` would overwrite the baseline used by deferral and comparison. The local example has a serial chain, so changing an upstream model can select many descendants. That is expected: `+` selects descendants.

Do not overwrite the manifest in `prod_artifacts/` with a branch manifest. Keep state inputs immutable for the duration of the command. Deferral only works for relations represented by the state manifest that exist and are accessible in the same configured database; it does not create missing baseline relations.

### 9.6 Data-diff script for row counts

Save as `scripts/compare_counts.py`:

```python
#!/usr/bin/env python3
"""Compare counts for baseline and PR relations using a configured dbt adapter.

This example invokes no warehouse by itself; it expects counts to be supplied
from SQL queries or a separately configured comparison connection. The
function below is a deterministic comparison core for CI integration.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def compare(baseline: int, candidate: int, allowed_delta: int = 0) -> dict[str, object]:
    delta = candidate - baseline
    return {
        "baseline_rows": baseline,
        "candidate_rows": candidate,
        "delta_rows": delta,
        "allowed_delta": allowed_delta,
        "within_tolerance": abs(delta) <= allowed_delta,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=int, required=True)
    parser.add_argument("--candidate", type=int, required=True)
    parser.add_argument("--allowed-delta", type=int, default=0)
    parser.add_argument("--output", default="row-count-diff.json")
    args = parser.parse_args()

    result = compare(args.baseline, args.candidate, args.allowed_delta)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["within_tolerance"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

This script checks the comparison logic, not the warehouse query. A CI integration must obtain counts from the actual baseline and PR relations using the selected adapter or data-diff tool, then pass those measured values to the script. Do not hard-code counts and treat that as a real data diff.

Example logic test with deliberately illustrative inputs:

```bash
python scripts/compare_counts.py --baseline 1000 --candidate 1000
python scripts/compare_counts.py --baseline 1000 --candidate 1012 --allowed-delta 0
```

The first returns success; the second returns a non-zero exit code. These are example numbers for validating the comparison behavior, not observed model counts. For production-quality comparison, add key-set and metric comparisons as described in Section 8.2.

### 9.7 Compare actual baseline and candidate relation counts (DuckDB lab)

The `compare_counts.py` example above tests only the comparison function when counts are supplied by the caller. For this local DuckDB lab, use the adapter-specific script below to query the actual baseline and candidate schemas. It intentionally supports only the generated `model_000`–`model_099` names; do not use this DuckDB-specific script for Snowflake, BigQuery, or Databricks.

Save as `scripts/compare_duckdb_counts.py`:

```python
#!/usr/bin/env python3
"""Compare row counts for generated models in two DuckDB schemas."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import duckdb

IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MODEL_NAME = re.compile(r"^model_[0-9]{3}$")


def safe_identifier(value: str, label: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise ValueError(f"Invalid {label}: {value!r}")
    return '"' + value.replace('"', '""') + '"'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default="generated.duckdb")
    parser.add_argument("--baseline-schema", default="main")
    parser.add_argument("--candidate-schema", required=True)
    parser.add_argument("--models-file", required=True)
    parser.add_argument("--output", default="row-count-diff.json")
    args = parser.parse_args()

    try:
        baseline_schema = safe_identifier(args.baseline_schema, "baseline schema")
        candidate_schema = safe_identifier(args.candidate_schema, "candidate schema")
        models = [line.strip() for line in Path(args.models_file).read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, ValueError) as exc:
        print(f"Invalid comparison input: {exc}", file=sys.stderr)
        return 2
    if not models:
        print("No selected model names were supplied; refusing an empty comparison.", file=sys.stderr)
        return 2
    if any(not MODEL_NAME.fullmatch(name) for name in models):
        print("Model list contains a name outside model_000..model_099.", file=sys.stderr)
        return 2

    report: list[dict[str, object]] = []
    try:
        with duckdb.connect(args.database, read_only=True) as con:
            existing = {
                (row[0], row[1])
                for row in con.execute(
                    "select table_schema, table_name from information_schema.tables"
                ).fetchall()
            }
            for model in models:
                if (args.baseline_schema, model) not in existing:
                    raise ValueError(f"Baseline relation missing: {args.baseline_schema}.{model}")
                if (args.candidate_schema, model) not in existing:
                    raise ValueError(f"Candidate relation missing: {args.candidate_schema}.{model}")
                quoted_model = safe_identifier(model, "model name")
                baseline = con.execute(
                    f"select count(*) from {baseline_schema}.{quoted_model}"
                ).fetchone()[0]
                candidate = con.execute(
                    f"select count(*) from {candidate_schema}.{quoted_model}"
                ).fetchone()[0]
                report.append({
                    "model": model,
                    "baseline_rows": baseline,
                    "candidate_rows": candidate,
                    "delta_rows": candidate - baseline,
                    "counts_match": baseline == candidate,
                })
    except (OSError, duckdb.Error, ValueError) as exc:
        print(f"Comparison failed: {exc}", file=sys.stderr)
        return 2

    payload = {
        "database": args.database,
        "baseline_schema": args.baseline_schema,
        "candidate_schema": args.candidate_schema,
        "compared_models": len(report),
        "all_counts_match": all(item["counts_match"] for item in report),
        "results": report,
    }
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["all_counts_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

After the state-based build, capture the selected model names and compare their baseline (`main`) and candidate (`ci_state_test`) counts:

```bash
dbt ls --resource-type model --select state:modified+ --state prod_artifacts --target ci --target-path target-branch --output name > changed_models.txt
python ../scripts/compare_duckdb_counts.py \
  --database generated.duckdb \
  --baseline-schema main \
  --candidate-schema ci_state_test \
  --models-file changed_models.txt \
  --output row-count-diff.json
```

A zero exit code means all compared row counts match, not that row values or business semantics match. A nonzero exit code means a count differs or the comparison could not be completed. Inspect missing/extra keys and important measures before treating a PR as equivalent. If the modified model intentionally changes results, document expected deltas and use explicit assertions rather than weakening the comparison silently.

### 9.8 Expected outcomes and diagnosis

| Result | Interpretation / next step |
|---|---|
| Parse fails | Check generated paths, project/profile names, installed adapter, and SQL syntax |
| Full build succeeds but takes similar time at every thread count | Chain-heavy DAG limits parallelism; inspect runnable width before changing warehouse size |
| State selection includes many nodes | A changed upstream model has many descendants; inspect `dbt ls` and confirm that this is intended |
| State selection is empty | State manifest may be wrong/stale, change may not affect parsed resources, or command path/target may be incorrect |
| Deferred reference fails | State relation missing/inaccessible, wrong database/schema mapping, or target permissions incomplete |
| CI writes into shared schema | Target/profile/schema generation is not PR-specific; stop the job and fix isolation before continuing |
| Cleanup fails | Auth/permissions, adapter-specific relation construction, or naming guard issue; alert and use approved janitor process |
| Row counts match but outputs differ | Counts alone cannot detect value changes or key substitutions; add key/column-level comparisons |
| Threads increase cost without reducing elapsed time | Warehouse saturation, query queueing, serial DAG, or non-query overhead; revert and inspect profiles |

### 9.9 Completion criteria

- [ ] Generate a deterministic 100-model project and verify its parsed model count.
- [ ] Capture a baseline full build and preserve `manifest.json`/`run_results.json`.
- [ ] Identify the 10 slowest resources and distinguish that list from the estimated critical path.
- [ ] Benchmark multiple thread settings with a recorded environment and comparable cache conditions.
- [ ] Compare at least one materialization change and verify downstream correctness/cost trade-offs.
- [ ] Save a separate production/baseline manifest and inspect `state:modified+` selection before building.
- [ ] Run a deferred build in an isolated target and understand which upstreams are reused.
- [ ] Configure PR schema naming, cleanup-on-close, and abandoned-schema cleanup.
- [ ] Add a meaningful data-diff check and document why row-count-only checks are limited.
- [ ] Record real results without inventing timings or savings.

---

## 10. Roadmap checkpoint

You should be able to explain:

1. Why a slowest-model list is not the same as the critical path.
2. When increasing threads improves throughput and when it only increases contention.
3. How `state:modified+`, `--state`, and `--defer` differ.
4. Why a production manifest and a PR output directory must be kept separate.
5. How per-PR schemas prevent branches from overwriting each other and how cleanup is made safe.
6. Which levers are specific to Snowflake, BigQuery, Databricks, and DuckDB.
7. Why a row-count match is a weak data-diff result.
8. Which expensive tests should run on every PR versus nightly, based on risk.
9. How query comments/tags support cost attribution only when the adapter/warehouse actually records them.
10. What dbt Mesh, `dbt clone`, and dbt Fusion can offer, and why availability/version checks matter.

### Common mistakes

- Running a full build for every PR without considering state selection.
- Optimizing the slowest individual model while ignoring the dependency critical path.
- Increasing threads beyond the warehouse's useful concurrency.
- Converting a model to incremental without a late-data, delete, and backfill plan.
- Using `--defer` without a valid state manifest or without access to referenced production relations.
- Putting the production manifest in a target directory that the CI invocation overwrites.
- Allowing multiple PRs to write to the same schema.
- Forgetting schema cleanup or using unvalidated user input in cleanup DDL.
- Assuming warehouse-specific settings are portable across adapters.
- Treating successful completion or equal row counts as proof of semantic correctness.
- Moving all expensive tests out of PR/production gates without a risk-based policy.
- Claiming a benchmark, cost saving, clone capability, or Fusion benefit without measuring and verifying it.

---

## 11. Verification and execution boundary

This lesson defines repeatable measurement methods and example code. Illustrative JSON values and command examples are not benchmark results. A script's presence does not mean it has been executed against your warehouse. Before production use, pin dbt and adapter versions, validate CLI options, run the scripts against generated and real artifacts, test cleanup in a non-production environment, and verify platform-specific capabilities with current vendor documentation.
