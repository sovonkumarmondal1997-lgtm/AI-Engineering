# Deploying dbt with Airflow and dbt Cloud

> **Roadmap location:** `Stage 2C — Data Engineering_3/06-dbt-and-Analytics-Engineering/08-deploying-dbt-with-airflow-and-dbt-cloud.md`  
> **Curriculum source:** Topic 08 in `roadmap-dbt-and-Analytics-Engineering.md`, checked against the complete `Roadmap_ptree.md`.  
> **Scope:** Environments, scheduled execution, dbt Cloud, Airflow/BashOperator, Cosmos, credentials, containers, CI/CD, monitoring, recovery, backfills, and operational ownership.  
> **Compatibility policy:** dbt, Airflow, provider, Cosmos, adapter, and cloud-service releases change independently. Examples use stable concepts and current documented command patterns, but pin versions for an actual deployment and validate provider-specific arguments against the installed versions. Placeholder account IDs, URLs, schemas, buckets, tokens, and secrets must be supplied by the operator.

> **Runtime-track distinction:** The local Docker demonstration uses the preceding lessons' DuckDB setup. The GitHub Actions slim-CI example is a separate Snowflake deployment pattern because safe deferral requires the CI adapter to read the production relations represented in the production manifest. Do not mix a Snowflake production manifest with a DuckDB-only CI target. For a DuckDB-only project, use a full isolated CI build; for another production warehouse, replace the Snowflake requirements/profile with that adapter's tested equivalent.

## Learning outcomes

By completing this lesson, you will be able to:

- Separate development, CI, staging, and production execution and data access.
- Configure dbt profiles/targets, schedule `dbt build`, interpret exit codes, and inspect `run_results.json`.
- Explain dbt Cloud projects, environments, IDE, deploy jobs, CI jobs, merge jobs, and scheduling.
- Orchestrate dbt with Airflow's `BashOperator`, a virtual environment/container, or Astronomer Cosmos.
- Design the sequence ingestion complete → source freshness → build/tests → documentation/artifact publication → downstream refresh.
- Use selectors and slim CI without confusing state artifacts, deferred relations, and output schemas.
- Inject credentials safely through environment variables, cloud secret managers, key-pair authentication, and OIDC where supported.
- Containerize a dbt project and understand Kubernetes, Cloud Run jobs, and ECS execution patterns.
- Implement CI/CD, alerts, artifact collection, duration reporting, safe retries, backfills, and recovery.
- Compare Airflow, dbt Cloud, Dagster, Prefect, Databricks Workflows, Azure Data Factory, and Snowflake tasks for the right operating context.
- Write a production runbook with clear ownership, escalation, and consumer communication.

---

## 1. Production execution: the operating model

dbt transforms data inside a warehouse or analytical platform. It does not, by itself, provide every capability required to operate a production pipeline: a schedule, external dependency checks, secret delivery, alert routing, retries, cross-system coordination, and incident ownership must be provided by dbt Cloud, Airflow, or another orchestration platform.

A typical production flow is:

```text
Upstream ingestion completes
        |
        v
Source freshness / ingestion SLA check
        |
        v
dbt build (models, seeds/snapshots as selected, and tests)
        |
        v
Persist artifacts + publish docs/catalog metadata
        |
        v
Refresh downstream consumers only after required tests pass
        |
        v
Notify success/failure and record run metrics
```

`dbt build` runs selected resources in dependency order and can include models, tests, seeds, and snapshots according to selection and project configuration. Tests associated with models are part of the build graph; a failing required test can fail the build and prevent downstream nodes from running. A separate `dbt test` task may be useful for a deliberate run → test → publish sequence, but running `dbt build` and then repeating all the same tests is usually redundant.

### 1.1 Responsibilities by component

| Component | Primary responsibility | Does not automatically guarantee |
|---|---|---|
| dbt project | SQL transformations, dependency graph, tests, documentation, artifacts | Scheduling, credentials management, paging, or cross-system recovery |
| Warehouse/adapter | Execute SQL, enforce database permissions, store relations | Correct metric meaning or safe orchestration |
| Scheduler/orchestrator | Trigger jobs, order tasks, retry, record task state, coordinate upstream/downstream systems | Correct dbt configuration or safe retry semantics for every operation |
| Secret manager / identity federation | Deliver credentials or short-lived identities | Least privilege unless policies are correctly scoped |
| CI/CD system | Validate changes and promote approved code | Production data correctness unless checks and access are designed properly |
| Observability stack | Capture logs, metrics, alerts, and run history | Incident resolution without ownership and runbooks |

### 1.2 Production versus demonstration

This lesson supplies templates and executable patterns. A real deployment still requires the operator to provide and verify:
- Warehouse type, account/project/host, database/catalog, warehouse/compute, and schemas.
- dbt adapter and compatible pinned package versions.
- Identity and permissions for development, CI, staging, and production.
- Artifact storage and retention policy.
- Scheduler runtime and network connectivity.
- Secret-manager paths, OIDC trust policies, and IAM/database grants.
- Alert destinations, on-call owner, SLA thresholds, and consumer contact list.
- A documented deployment/rollback policy for the chosen platform.

No cloud account, live scheduler, warehouse, dbt Cloud workspace, or alert destination is provisioned by the code in this lesson.

---

## 2. Environments, targets, profiles, and schema isolation

### 2.1 Environment strategy

| Environment | Purpose | Data and permissions | Typical execution |
|---|---|---|---|
| Development | Individual author iterates on models | Isolated schema; least privilege; safe/sanitized data where possible | `dbt build --select <changed-models+>` |
| CI / pull request | Prove a proposed change is valid | Per-PR schema; limited warehouse permissions; test data or safe production-state deferral | Parse/compile, slim build, tests, lint |
| Staging | Validate production-like code and connections | Separate schema/database/project; controlled access; representative data | Release candidate build and smoke tests |
| Production | Publish trusted data products | Production schemas, tightly scoped service identity, monitored cost and access | Scheduled/triggered deployment job |

Use distinct schemas and, where necessary, distinct database projects/accounts or warehouses. A different dbt target name is not sufficient isolation if two targets resolve to the same writable schema. Keep production credentials unavailable to untrusted pull-request code.

### 2.2 `profiles.yml` and targets

A local dbt Core project typically has a `dbt_project.yml` that names the profile:

```yaml
name: analytics
version: "1.0.0"
config-version: 2
profile: analytics

model-paths: ["models"]
seed-paths: ["seeds"]
test-paths: ["tests"]
macro-paths: ["macros"]
analysis-paths: ["analyses"]
target-path: "target"
clean-targets: ["target", "dbt_packages"]
```

The following profile is a **DuckDB demonstration** consistent with the preceding local lessons. It uses separate local files for targets. Do not use this local-file example as a production cloud-warehouse credential pattern.

`~/.dbt/profiles.yml`:

```yaml
analytics:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "{{ env_var('DBT_DUCKDB_DEV_PATH', 'dev.duckdb') }}"
      schema: dev
      threads: 4
    ci:
      type: duckdb
      path: "{{ env_var('DBT_DUCKDB_CI_PATH', 'ci.duckdb') }}"
      schema: ci
      threads: 2
    prod:
      type: duckdb
      path: "{{ env_var('DBT_DUCKDB_PROD_PATH', 'prod.duckdb') }}"
      schema: analytics
      threads: 4
```

For a real warehouse, use the profile schema documented by the selected adapter. Do not copy DuckDB keys into Snowflake, BigQuery, Redshift, Databricks, or Postgres profiles.

Example commands:

```bash
dbt debug --target dev
dbt build --target dev
dbt build --target ci
dbt build --target prod
```

The last command is shown to explain target selection, not as an instruction to let a developer run production manually. Production should run from the approved scheduler/deployment identity with audited code and controls.

### 2.3 Schema naming and isolation

A schema strategy should answer:
- Who owns the schema?
- Can a developer or PR job overwrite production relations?
- Is the schema ephemeral, retained for debugging, or shared?
- Who removes it, and how is cleanup restricted?
- Are identifiers sanitized before being inserted into schema names?
- Can untrusted PR code access production secrets or production state?

A warehouse target might map to schemas such as `dbt_dev_<user>`, `dbt_ci_pr_<number>`, `dbt_staging`, and `analytics`. The exact names are adapter- and organization-specific. Do not use untrusted branch names directly in SQL identifiers without validation.

### 2.4 Secrets and environment variables

Do not commit `profiles.yml` containing passwords, private keys, tokens, or service-account JSON. A profile can reference environment variables:

```yaml
# Example shape only; fields vary by adapter.
analytics:
  target: prod
  outputs:
    prod:
      type: snowflake
      account: "{{ env_var('DBT_SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('DBT_SNOWFLAKE_USER') }}"
      role: "{{ env_var('DBT_SNOWFLAKE_ROLE') }}"
      database: "{{ env_var('DBT_SNOWFLAKE_DATABASE') }}"
      warehouse: "{{ env_var('DBT_SNOWFLAKE_WAREHOUSE') }}"
      schema: "{{ env_var('DBT_SNOWFLAKE_SCHEMA') }}"
      authenticator: "{{ env_var('DBT_SNOWFLAKE_AUTHENTICATOR', 'SNOWFLAKE_JWT') }}"
      private_key_path: "{{ env_var('DBT_SNOWFLAKE_PRIVATE_KEY_PATH') }}"
      threads: 4
```

This is a profile **shape**, not a complete working key-pair configuration: the private key file must be securely mounted or created at runtime, the adapter's exact key parameters must match its pinned version, and the corresponding public key must be configured for the Snowflake user. Do not put the private key contents in YAML or Git. Some adapters use different names or support different authentication methods.

Use environment variables as a delivery interface, not as a secret store. Inject values from Airflow Connections/Secrets Backend, a cloud secret manager, a platform-managed connection, or short-lived workload identity. Never print the environment, run `set -x` around secret-bearing commands, or attach secret files to public artifacts.

---

## 3. Running dbt and interpreting results

### 3.1 Schedule `dbt build`

For a complete selected production graph:

```bash
dbt build --target prod
```

For a deliberately bounded selector:

```bash
dbt build --target prod --select tag:daily
```

For a changed model and downstream impact in a state-aware workflow:

```bash
dbt build \
  --target ci \
  --select "state:modified+" \
  --state /path/to/production-artifacts \
  --defer
```

Slim CI requires a trusted comparison state, typically the production `manifest.json`, and an isolated CI target/schema. `--defer` resolves unselected upstream references against state relations where appropriate; it is not a substitute for a CI schema or authorization boundary. Keep production state artifacts separate from CI output artifacts so a CI invocation cannot overwrite its own comparison baseline. State selection behavior depends on the selected dbt version and flags; confirm it against that version's docs.

### 3.2 Exit codes

A process exit code is the scheduler's first signal, not the full incident diagnosis.

| Exit code / state | Typical meaning | Response |
|---|---|---|
| `0` | Command completed successfully | Verify required artifacts and expected downstream state |
| Non-zero | Command failed, a required test failed, compilation/connection failed, or another error occurred | Stop dependent publication tasks, preserve logs/artifacts, classify the failure |
| Airflow `up_for_retry` | A task failed and is waiting for another attempt | Inspect whether retry is safe and whether the cause is transient |
| Airflow `failed` | No more retries or failure was configured as terminal | Alert owner, preserve context, follow runbook |

Do not assume every non-zero exit has the same cause. Parse dbt logs and `run_results.json` for the failed node, status, message, and timing. A missing artifact may mean the command failed before it wrote one; artifact collection must not mask the original command failure.

### 3.3 What `run_results.json` contains

dbt writes `target/run_results.json` for invocations such as `build`, `run`, `test`, `seed`, `snapshot`, and others. It contains results for executed nodes, including status and timing. It is not a complete project manifest, and it does not include nodes that were not executed. Source freshness has separate artifacts (`sources.json` and/or `freshness.json`, depending on dbt version and command track).

Example shape (illustrative, not a captured run):

```json
{
  "metadata": {
    "dbt_schema_version": "https://schemas.getdbt.com/dbt/run-results/v6.json",
    "dbt_version": "1.x"
  },
  "results": [
    {
      "unique_id": "model.analytics.fct_orders",
      "status": "success",
      "execution_time": 2.34,
      "message": null,
      "timing": [
        {"name": "compile", "started_at": "2026-01-01T00:00:00Z", "completed_at": "2026-01-01T00:00:00Z"},
        {"name": "execute", "started_at": "2026-01-01T00:00:00Z", "completed_at": "2026-01-01T00:00:02Z"}
      ]
    }
  ]
}
```

Artifact schema versions change; use the schema URL and `metadata.dbt_version` from the actual artifact. Do not hardcode the illustrative version into an artifact parser.

A useful parser:

```python
#!/usr/bin/env python3
"""Summarize dbt run_results.json and optionally export node records as CSV."""
import argparse
import csv
import json
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("artifact", nargs="?", default="target/run_results.json")
parser.add_argument("--csv", dest="csv_path", type=Path, help="Write node records to this CSV")
parser.add_argument("--run-id", default=os.getenv("DBT_RUN_ID", "unknown"))
parser.add_argument("--environment", default=os.getenv("DBT_ENVIRONMENT", "unknown"))
args = parser.parse_args()

path = Path(args.artifact)
if not path.exists():
    raise SystemExit(f"Missing artifact: {path}")

data = json.loads(path.read_text(encoding="utf-8"))
metadata = data.get("metadata", {})
results = data.get("results", [])
print(f"dbt_version={metadata.get('dbt_version', 'unknown')}")
print(f"schema={metadata.get('dbt_schema_version', 'unknown')}")
print(f"executed_nodes={len(results)}")

total_seconds = 0.0
failures = []
rows = []
for result in results:
    duration = float(result.get("execution_time") or 0)
    total_seconds += duration
    unique_id = result.get("unique_id", "unknown")
    status = result.get("status", "unknown")
    print(f"{status:12} {duration:8.2f}s {unique_id}")
    rows.append({
        "invocation_id": metadata.get("invocation_id", "unknown"),
        "run_id": args.run_id,
        "environment": args.environment,
        "dbt_version": metadata.get("dbt_version", "unknown"),
        "unique_id": unique_id,
        "resource_type": result.get("unique_id", "").split(".")[0] if result.get("unique_id") else "unknown",
        "status": status,
        "execution_time_seconds": duration,
        "message": result.get("message") or "",
    })
    if status not in {"success", "pass", "warn", "skipped", "no-op"}:
        failures.append((unique_id, status, result.get("message")))

print(f"sum_node_execution_seconds={total_seconds:.2f}")
for unique_id, status, message in failures:
    print(f"FAILURE {unique_id} status={status} message={message}")

if args.csv_path:
    args.csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "invocation_id", "run_id", "environment", "dbt_version", "unique_id",
        "resource_type", "status", "execution_time_seconds", "message",
    ]
    with args.csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"csv={args.csv_path}")

if failures:
    raise SystemExit(1)
```

The sum of node execution durations is not necessarily wall-clock job duration because dbt may run nodes in parallel and timing includes different phases. For overall duration, use invocation start/end metadata or scheduler/job start/end timestamps. Status values vary by node type and dbt version; keep the parser tolerant and preserve unknown statuses for investigation rather than assuming the list above is exhaustive.

### 3.4 Artifacts to retain

| Artifact | Purpose |
|---|---|
| `manifest.json` | Project graph, nodes, configs, dependencies, and metadata |
| `run_results.json` | Results and timing for nodes executed in one invocation |
| `sources.json` / `freshness.json` | Source freshness outcomes, depending on command/version |
| `catalog.json` | Introspected relation/column metadata from docs generation |
| dbt logs | Detailed command context and error diagnostics |

Store artifacts with an invocation-specific path, for example `s3://<bucket>/dbt/<environment>/<run-id>/`. Apply access controls and retention. Artifacts can contain SQL, relation names, and metadata that should not be public. Avoid uploading credentials or unredacted environment dumps.

---

## 4. dbt Cloud fundamentals

dbt Cloud (the dbt platform) can provide managed execution and deployment jobs, environments, CI jobs, a browser IDE/Studio experience, scheduling, logs, and artifact history. Exact UI labels, plan entitlements, and job features change; use the current platform documentation for the account.

### 4.1 Core objects

- **Project:** connection between a dbt code repository and the platform's project settings.
- **Development environment:** developer-specific environment, credentials, and execution context for editing/running project code.
- **Deployment environment:** version, code reference, warehouse connection, profile/connection profile, target settings, and other settings for scheduled/CI execution. Staging and production deployment environments should be separated.
- **IDE / Studio:** browser-based development and project workflows, depending on the current platform interface.
- **Deploy job:** builds and tests production or staging data assets on a schedule or trigger.
- **CI job:** validates a pull request, usually with a temporary/isolated schema and modified-node selection where configured.
- **Merge/deployment trigger:** runs approved code after a pull request merges, subject to the repository/platform configuration.
- **Artifacts and logs:** job outputs, status, timing, and metadata useful for debugging and monitoring.

### 4.2 Recommended dbt Cloud job design

1. **CI job:** run on pull request; use a CI/staging schema and configured state-aware selection where available; fail the required status check on test or build failure.
2. **Production deploy job:** use the designated production environment and a protected production identity; trigger on merge or an approved schedule.
3. **Freshness job/step:** check ingestion/freshness before rebuilding when source freshness is a release gate.
4. **Build/test:** use `dbt build` and a carefully reviewed selector.
5. **Docs/artifacts:** publish docs and retain artifacts after successful build/test. Use supported platform features rather than treating `dbt docs serve` as a hosted production web service.
6. **Alerts:** configure job failure notifications and route incidents to the owning team.
7. **Promotion:** promote reviewed code to production; do not promote by copying a developer's local target.

### 4.3 dbt Cloud versus self-managed Airflow

dbt Cloud reduces scheduler and execution-platform maintenance for dbt-centric workflows. Airflow is more flexible when the pipeline coordinates ingestion, dbt, APIs, file movement, ML, and many non-dbt systems. A team may use both, but avoid duplicating schedules and retries for the same production transformation without a clear ownership boundary.

---

## 5. Airflow orchestration patterns

### 5.1 Pattern A: BashOperator invoking a containerized dbt command

A DAG-level task can run a whole dbt command inside a pinned container. This is simple and robust when the dbt project is treated as one deployment unit. It offers less per-model Airflow visibility than Cosmos, but keeps orchestration complexity low.

The BashOperator must run in an environment where Docker is available and permitted. On managed Airflow, Docker socket access may not exist or may be prohibited. In that case use KubernetesPodOperator, ECS/Fargate, Cloud Run Jobs, or another supported execution operator rather than assuming `docker run` works on the scheduler/worker.

### 5.2 Pattern B: BashOperator with a preinstalled virtual environment

Use this only when the Airflow worker image contains a compatible Python/dbt adapter environment and project files. A dedicated venv or pinned worker image prevents dependency collisions with Airflow's own Python packages.

Example:

```python
BashOperator(
    task_id="dbt_build",
    bash_command=(
        "set -euo pipefail; "
        "/opt/dbt-venv/bin/dbt build "
        "--project-dir /opt/dbt/project "
        "--profiles-dir /opt/dbt/profiles "
        "--target prod"
    ),
)
```

The paths are deployment-specific. Do not install dbt adapters dynamically in every task run; dependency resolution can be slow, non-reproducible, and incompatible with Airflow's Python environment.

### 5.3 Full DAG: freshness → run → tests → docs → downstream refresh

This example uses Airflow 2.8+ style imports and a BashOperator running commands in a prebuilt worker image with dbt installed. Pin and test a compatible Airflow/provider/Python/dbt set in your own environment. The `DBT_PROJECT_DIR` and `DBT_PROFILES_DIR` directories must exist in the worker/container; environment variables and credentials must be supplied by the deployment.

`dags/dbt_production.py`:

```python
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook

def alert_failure(context):
    ti = context.get("task_instance")
    exception = str(context.get("exception", "unknown error"))[:800]
    message = (
        f"dbt DAG failed: dag={getattr(ti, 'dag_id', 'unknown')} "
        f"task={getattr(ti, 'task_id', 'unknown')} "
        f"run_id={context.get('run_id', 'unknown')} "
        f"exception={exception} log={getattr(ti, 'log_url', '')}"
    )
    # Store the webhook in an Airflow Connection; do not put it in source.
    SlackWebhookHook(slack_webhook_conn_id="slack_webhook_default").send(text=message)

DBT_PROJECT_DIR = "/opt/dbt/project"
DBT_PROFILES_DIR = "/opt/dbt/profiles"
DBT_TARGET = "prod"

default_args = {
    "owner": "analytics-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=2),
}

with DAG(
    dag_id="dbt_production_daily",
    description="Freshness-gated dbt production pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="0 5 * * *",
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    on_failure_callback=alert_failure,
    tags=["dbt", "analytics", "production"],
) as dag:
    source_freshness = BashOperator(
        task_id="source_freshness",
        bash_command=(
            "set -euo pipefail; "
            "/opt/dbt/project/experiments/08_deployment/scripts/run_dbt_and_archive.sh "
            "source freshness "
            f"--project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}"
        ),
        cwd=DBT_PROJECT_DIR,
        append_env=True,
        env={
            "DBT_TARGET": DBT_TARGET,
            "DBT_ENVIRONMENT": "production",
            "DBT_RUN_ID": "{{ run_id | replace('/', '_') }}_freshness",
        },
    )

    build_and_test = BashOperator(
        task_id="dbt_build_and_test",
        bash_command=(
            "set -euo pipefail; "
            "/opt/dbt/project/experiments/08_deployment/scripts/run_dbt_and_archive.sh "
            "build "
            f"--project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}"
        ),
        cwd=DBT_PROJECT_DIR,
        append_env=True,
        env={
            "DBT_ENVIRONMENT": "production",
            "DBT_RUN_ID": "{{ run_id | replace('/', '_') }}_build",
        },
    )

    generate_docs = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=(
            "set -euo pipefail; "
            "/opt/dbt/project/experiments/08_deployment/scripts/run_dbt_and_archive.sh "
            "docs generate "
            f"--project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}"
        ),
        cwd=DBT_PROJECT_DIR,
        append_env=True,
        env={
            "DBT_ENVIRONMENT": "production",
            "DBT_RUN_ID": "{{ run_id | replace('/', '_') }}_docs",
        },
    )

    publish_docs = BashOperator(
        task_id="publish_docs",
        bash_command=(
            "set -euo pipefail; "
            ': "${DBT_ARTIFACT_BUCKET:?Set DBT_ARTIFACT_BUCKET}"; '
            ': "${DBT_DOCS_BUCKET:?Set DBT_DOCS_BUCKET to a private approved bucket}"; '
            'aws s3 sync '
            '"s3://${DBT_ARTIFACT_BUCKET}/dbt/production/{{ run_id | replace("/", "_") }}_docs/docs/" '
            '"s3://${DBT_DOCS_BUCKET}/dbt-docs/production/"'
        ),
        append_env=True,
    )

    refresh_consumers = EmptyOperator(task_id="refresh_downstream_consumers")

    source_freshness >> build_and_test >> generate_docs >> publish_docs >> refresh_consumers
```

**Important operational qualifications:**
- Install a compatible `apache-airflow-providers-slack` release and create the `slack_webhook_default` Airflow Connection before enabling this callback. The callback is attached at DAG level; test its delivery and callback logs in your installed Airflow version.
- The DAG uses `dbt build`, which runs selected resources and applicable tests in dependency order. A failed required test returns a non-zero status and blocks docs generation, publication, and downstream refresh. Add a separate `dbt test` task only when you intentionally want a second validation invocation; otherwise it repeats work and may increase warehouse cost.
- The docs-generation wrapper archives the generated docs site under the run-specific private artifact prefix; the separate publisher task copies that prefix to `DBT_DOCS_BUCKET`, so the DAG does not depend on local files surviving across Airflow workers. The execution identity needs write access to the artifact prefix; the publisher identity needs read access to that run's docs prefix and write access to the private docs bucket. Adapt this for GCS, Azure Blob, or the platform's supported docs publishing flow. Keep the bucket private unless a reviewed public documentation policy exists.
- `EmptyOperator` is a placeholder for a real downstream refresh operator. Add it only after the data-quality gate.
- The example invokes `run_dbt_and_archive.sh` from the lab directory, so the image must contain that script, `dbt`, `aws`, the project, and the adapter. Supply `DBT_ARTIFACT_BUCKET`, `DBT_DOCS_BUCKET`, a unique run ID, and workload identity to each task. For real production, use a dedicated execution container/operator if the worker is not the dbt runtime. With ephemeral containers, upload per-invocation artifacts to shared durable storage; do not assume local `target/` persists across tasks.
- `source freshness` is the legacy command name still commonly supported by dbt Core. In newer command tracks, freshness artifact names and CLI behavior may differ. Pin the CLI and follow its version documentation.
- `append_env=True` preserves worker environment variables; it is not a secret-management solution. Avoid putting credentials in DAG source or logging them.

### 5.4 Use `dbt build` as a single graph task

A simpler alternative is:

```bash
dbt source freshness --target prod
dbt build --target prod
dbt docs generate --target prod
```

This is a good fit when you want dbt itself to own model/test dependency ordering and do not need every model to appear as an Airflow task. Preserve artifacts from each invocation separately because later commands may overwrite files in `target/`. Gate docs publication and downstream tasks on the build's successful exit code.

### 5.5 Retries and duplicate side effects

Retries are safe only when the operation is idempotent or has a clear deduplication/recovery design.

- Warehouse `CREATE OR REPLACE` or merge operations may be safe under certain model/adapter semantics, but do not assume all SQL is idempotent.
- Hooks, notifications, API calls, exports, and downstream refreshes can create duplicate side effects.
- Set retry count and delay based on expected transient failures, not as a substitute for fixing invalid SQL or permissions.
- Limit overlapping production runs when they could mutate the same relations.
- Make alerting idempotent or include a run ID so repeated notifications can be correlated.
- Use separate tasks and per-model retries when the orchestrator can identify a failed node reliably.

For model-level retries and dependency visibility, evaluate Cosmos. For a single dbt command, a task-level retry is simpler and avoids excessive orchestration overhead.

---

## 6. Astronomer Cosmos: dbt models as Airflow tasks

Cosmos can parse a dbt project and render model/test/source nodes into an Airflow DAG or task group. This provides more detailed Airflow visibility and can allow orchestration at dbt-node granularity. The exact operators, profiles mapping, execution modes, and import paths vary by Cosmos version.

### 6.1 When to choose Cosmos

Use Cosmos when:
- You want individual dbt model tasks and visible upstream/downstream dependencies.
- You need Airflow retries/alerts around selected model tasks.
- The team already operates Airflow and wants dbt graph visibility in the same UI.

Prefer a single command task when:
- The project is small or dbt's own graph execution is sufficient.
- Scheduler overhead from hundreds/thousands of tasks is undesirable.
- You do not need Airflow-level model-level controls.

Cosmos does not replace dbt's model/test semantics. It renders orchestration from the dbt project and still depends on compatible dbt, adapter, profile, execution mode, and project artifacts.

### 6.2 Cosmos example (illustrative API; pin a compatible Cosmos release)

The following shows the intended configuration shape. Cosmos releases may rename or change imports and constructor arguments, so verify it against the installed release's quickstart before use.

```python
from datetime import datetime

from airflow import DAG
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
from cosmos.constants import LoadMode, ExecutionMode

with DAG(
    dag_id="dbt_cosmos_production",
    start_date=datetime(2025, 1, 1),
    schedule="0 5 * * *",
    catchup=False,
    max_active_runs=1,
    tags=["dbt", "cosmos"],
) as dag:
    # Example only: use the profile mapping supported by your adapter,
    # and retrieve the connection from an Airflow Connection/Secrets Backend.
    dbt_tasks = DbtTaskGroup(
        group_id="dbt",
        project_config=ProjectConfig(
            dbt_project_path="/opt/airflow/dags/dbt/analytics",
            manifest_path="/opt/airflow/dags/dbt/analytics/target/manifest.json",
            load_method=LoadMode.DBT_MANIFEST,
        ),
        profile_config=ProfileConfig(
            profile_name="analytics",
            target_name="prod",
            profile_mapping=PostgresUserPasswordProfileMapping(
                conn_id="warehouse_prod",
                profile_args={"schema": "analytics"},
            ),
        ),
        execution_config=ExecutionConfig(
            execution_mode=ExecutionMode.LOCAL,
        ),
        operator_args={
            "install_deps": False,
            "retries": 1,
        },
    )
```

**Do not deploy this snippet without adapting it.** It illustrates a common Cosmos mapping-based setup for a Postgres connection; it is not a universal profile for Snowflake, BigQuery, Databricks, DuckDB, or another adapter. `manifest_path` must refer to a valid manifest produced by a compatible dbt project and available when the DAG is parsed. If using Cosmos's `DBT_MANIFEST` load mode, ensure the manifest is refreshed as part of your deployment process and is not stale relative to the code being executed. Check the pinned Cosmos version for `LoadMode`, `ExecutionMode`, mapping imports, and `operator_args`.

For production freshness gating, create a freshness task upstream of the rendered dbt task group and a docs/publication task downstream of the successful group. Verify the rendered dependency graph in the Airflow UI before enabling the schedule. If using a `DbtTaskGroup` that includes dbt tests, avoid running a duplicate whole-project `dbt test` without a reason.

### 6.3 Per-model failure diagnosis

With Cosmos, the failed task can often identify the model or test that failed. Include:
- DAG run ID, task ID, model/test unique ID, commit SHA, target/environment.
- dbt log excerpt and `run_results.json` location, if produced.
- Retry attempt and warehouse query ID where available.
- Link to the runbook and model owner.

Do not assume every parse/compile/connection error maps to one model task; some failures occur before task-level model execution.

---

## 7. Docker: reproducible dbt execution

### 7.1 Why containerize

A container pins Python, dbt Core, the adapter, OS dependencies, and project dependencies into a repeatable runtime. It reduces “works on my laptop” drift and gives Airflow/CI/Cloud Run/ECS/Kubernetes a consistent image.

Pin:
- A supported Python base image by immutable digest for production.
- Exact compatible `dbt-core` and adapter versions.
- Package versions in `requirements.txt`/lock file.
- The project Git commit or image tag.
- The adapter/warehouse CLI requirements.

### 7.2 Minimal Dockerfile

This example uses DuckDB as a local teaching adapter. It is a reproducible local demonstration, not a production warehouse image. Use the correct adapter and authentication libraries for the production warehouse.

`Dockerfile`:

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DBT_PROFILES_DIR=/opt/dbt/profiles \
    DBT_PROJECT_DIR=/opt/dbt/project

WORKDIR /opt/dbt

COPY experiments/08_deployment/requirements.txt /opt/dbt/requirements.txt
RUN pip install --no-cache-dir --requirement /opt/dbt/requirements.txt

COPY . /opt/dbt/project/

RUN dbt deps --project-dir /opt/dbt/project \
    && useradd --create-home --uid 10001 dbtuser \
    && mkdir -p /opt/dbt/profiles /opt/dbt/project/target /data \
    && chown -R dbtuser:dbtuser /opt/dbt /data

USER dbtuser
WORKDIR /opt/dbt/project

ENTRYPOINT ["dbt"]
CMD ["--help"]
```

The `.dockerignore` file is mandatory when copying the repository root; it prevents local secrets, Git history, caches, and build outputs from entering the image. The example runs `dbt deps` during image build after copying the project. Include `packages.yml` and the package lock file supported by your dbt version when the project uses packages. For production, build from a clean source checkout and use a dependency lock/pinned resolution policy; avoid resolving unpinned dependencies during each run.

Place `.dockerignore` at the **repository root**, because that is the Docker build context used above:

```text
.git
.venv
venv
__pycache__
.pytest_cache
.mypy_cache
.env
.env.*
.local-profiles/
profiles.yml
target/
logs/
dbt_packages/
prod_state/
artifacts/
*.duckdb
*.pem
*.p8
*.key
```

`experiments/08_deployment/requirements.txt` for the local DuckDB demonstration and SQLFluff lint example:

```text
dbt-core==1.11.16
dbt-duckdb==1.11.0
sqlfluff==4.4.0
sqlfluff-templater-dbt==4.4.0
```

These pins are a dated example, not a claim that this lesson's container was built or tested. The Snowflake CI example pins dbt Core and adapter to the same `1.12.3` release line; change both together only after checking the adapter's declared compatibility. Confirm Python/adapter/templater compatibility, resolve transitive dependencies, and use a lock file or pinned constraints for repeatable builds. For a different warehouse, use that adapter's compatible pinned release rather than assuming DuckDB and production adapters are interchangeable.

For the **Snowflake CI workflow** below, use a separate adapter-matched file `experiments/08_deployment/requirements-ci-snowflake.txt`. The example versions should match the dbt/adapter release line used to produce the production state manifest; verify them together before use.

```text
dbt-core==1.12.3
dbt-snowflake==1.12.3
sqlfluff==4.4.0
sqlfluff-templater-dbt==4.4.0
```

`experiments/08_deployment/profiles/profiles.yml.example` (Snowflake CI profile; contains no credentials):

```yaml
analytics:
  target: ci
  outputs:
    ci:
      type: snowflake
      account: "{{ env_var('DBT_SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('DBT_SNOWFLAKE_CI_USER') }}"
      role: "{{ env_var('DBT_SNOWFLAKE_CI_ROLE') }}"
      warehouse: "{{ env_var('DBT_SNOWFLAKE_CI_WAREHOUSE') }}"
      database: "{{ env_var('DBT_SNOWFLAKE_CI_DATABASE') }}"
      schema: "{{ env_var('DBT_SNOWFLAKE_CI_SCHEMA') }}"
      authenticator: SNOWFLAKE_JWT
      private_key_path: "{{ env_var('DBT_SNOWFLAKE_PRIVATE_KEY_PATH') }}"
      private_key_passphrase: "{{ env_var('DBT_SNOWFLAKE_PRIVATE_KEY_PASSPHRASE', '') }}"
      threads: 4
```

This profile assumes the dbt project's profile name is `analytics` and the Snowflake CI role can write only to its isolated CI schema while reading the upstream production relations required for deferral. Configure grants explicitly. For another adapter, replace this profile and the CI requirements together.

`experiments/08_deployment/.sqlfluff` (Snowflake example):

```ini
[sqlfluff]
dialect = snowflake
templater = dbt

[sqlfluff:templater:dbt]
project_dir = .
profiles_dir = ~/.dbt
profile = analytics
target = ci
```

Adjust the dialect, profile, and rules for the warehouse/style guide. SQLFluff templater support and dbt versions must be pinned as a compatible pair.

### 7.3 Build and run cleanly

Run from the **dbt repository root**, which must contain `dbt_project.yml`, `models/`, and the `experiments/08_deployment/` lab folder. The Dockerfile is stored under the lab directory, but the build context is the repository root so it can copy both the dbt project and the artifact wrapper.

```bash
docker build -f experiments/08_deployment/Dockerfile -t analytics-dbt:dev .

mkdir -p .local-profiles
# Create a local, non-production profiles.yml in .local-profiles/profiles.yml.
# Never commit credentials in that file.

docker run --rm \
  --env DBT_DUCKDB_DEV_PATH=/data/dev.duckdb \
  --env DBT_PROJECT_DIR=/opt/dbt/project \
  --mount type=bind,src="$PWD/.local-profiles",dst=/opt/dbt/profiles,readonly \
  --mount type=volume,src=dbt-lab-data,dst=/data \
  analytics-dbt:dev \
  build --target dev --profiles-dir /opt/dbt/profiles
```

This bind-mount example assumes Docker is running locally and the mounted project path is compatible with the image's Python/dbt environment. The profile and data path are local demonstration inputs. For production, use an image with the project baked in, read-only filesystem where possible, a non-root user, short-lived credentials, a controlled network path, and an ephemeral writable `target/` directory.

Do not mount the entire repository over a baked-in project directory in production unless the deployment intentionally requires it; bind mounts can hide files copied into the image.

### 7.4 Runtime environment and secret injection

- Set non-secret configuration (`DBT_TARGET`, project path, artifact prefix) via environment.
- Inject credentials from the platform's secret mechanism or workload identity.
- Mount private key files with least-privilege permissions and delete temporary copies after use.
- Do not pass secrets in Docker command-line arguments; command lines can be visible in process inspection or logs.
- Use a unique run ID and persist artifacts to durable storage before the container exits.
- Use a read-only image and non-root UID unless the runtime requires otherwise.

---

### 7.5 Running the image on Kubernetes, Cloud Run Jobs, or ECS

Use the same immutable image digest across these runtimes; inject target, secrets, and artifact configuration at execution time.

| Runtime | Typical pattern | Operational controls |
|---|---|---|
| Kubernetes | A `Job` or an Airflow KubernetesPodOperator launches the dbt image | Workload identity/service account, Secret/CSI integration, resource requests/limits, bounded `backoffLimit`, logs, and a unique run ID |
| Google Cloud Run Jobs | A job execution runs the image to completion | Configure service account, Secret Manager references, VPC access to the warehouse, task timeout/retries, and log/exit status collection |
| AWS ECS/Fargate | ECS task definition runs the image; EventBridge, Step Functions, or Airflow triggers it | Task role, Secrets Manager/SSM references, private networking, CloudWatch logs, CPU/memory, and explicit task exit-code handling |

Kubernetes Job template (replace image digest and secret names with operator-owned values):

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: dbt-production-run
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      serviceAccountName: dbt-production
      containers:
        - name: dbt
          image: registry.example.invalid/analytics-dbt@sha256:REPLACE_WITH_VERIFIED_DIGEST
          args: ["build", "--target", "prod", "--profiles-dir", "/opt/dbt/profiles"]
          env:
            - name: DBT_ENVIRONMENT
              value: production
            - name: DBT_RUN_ID
              valueFrom:
                fieldRef:
                  fieldPath: metadata.uid
            - name: DBT_WAREHOUSE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: dbt-warehouse-credentials
                  key: password
```

This is a template, not a ready-to-apply manifest. `registry.example.invalid` and the digest are deliberate placeholders; the secret and service account must be created securely. The shown generic password variable must match the adapter profile, and the pod needs network/identity permissions to reach the warehouse and artifact store. For an Airflow-owned retry policy, `backoffLimit: 0` prevents Kubernetes from independently re-running a failed pod; choose one retry owner deliberately.

For Cloud Run Jobs and ECS, create the job/task definition in the platform first, attach the appropriate execution identity and secret references, and then have Airflow or the deployment system invoke it. Do not pass secret values in CLI arguments or bake them into the image. Confirm the platform's task timeout, retry, cancellation, and exit-code semantics before using it as a production executor.

## 8. Secure identity and credentials

### 8.1 Secret-management patterns

| Runtime | Preferred pattern | Avoid |
|---|---|---|
| Local development | Personal profile outside Git; local credential manager | Committing `profiles.yml` secrets |
| Airflow | Airflow Connections and a configured Secrets Backend (cloud manager, Vault, etc.) | Passwords in DAG code or task arguments |
| Kubernetes | Workload identity or mounted secrets via the cluster's approved secret integration | Plain-text Kubernetes manifests in a public repository |
| AWS ECS/Cloud Run | Task/job execution identity and cloud secret manager | Static keys baked into image |
| GitHub Actions | OIDC federation to cloud role, tightly scoped by repository/environment/branch | Long-lived cloud keys in workflow YAML |
| dbt Cloud | Platform-managed connection profiles and environment credentials | Copying production secrets into developer variables |

### 8.2 Key-pair authentication

For warehouses such as Snowflake, key-pair authentication can avoid a long-lived password, but the private key is still a secret. Store it in a secret manager, configure the matching public key on the warehouse user, and ensure the adapter's expected key format, passphrase handling, and environment-variable/profile fields match the pinned adapter version. Rotate keys and audit the service user.

### 8.3 OIDC from GitHub Actions

OIDC allows GitHub Actions to exchange a workflow identity token for short-lived cloud credentials without storing a long-lived cloud access key in GitHub secrets. It requires:
- An OIDC identity provider in the cloud account.
- A role trust policy constrained to the intended repository and branch/environment.
- The minimum IAM permissions needed for the job.
- Workflow permission `id-token: write` only where needed.
- Protected GitHub environments/branch rules for production.

Example AWS action step (operator must create the role and trust policy first):

```yaml
permissions:
  contents: read
  id-token: write

steps:
  - uses: actions/checkout@v4
  - uses: aws-actions/configure-aws-credentials@v6
    with:
      role-to-assume: ${{ vars.AWS_DBT_DEPLOY_ROLE_ARN }}
      aws-region: ${{ vars.AWS_REGION }}
```

Pin actions to reviewed full commit SHAs in a high-assurance production repository. The version tags above are readable examples. OIDC only authenticates the workflow to AWS; you must still authorize the role to access the required secret manager, artifact bucket, or deployment service, and configure the warehouse to accept the resulting identity or credential flow. AWS OIDC does not automatically authenticate to every warehouse.

---

## 9. CI/CD: lint → compile → slim build → test → docs → deploy

### 9.1 Release flow

```text
Pull request
  ├─ lint SQL/Python/YAML
  ├─ dbt deps (pinned)
  ├─ dbt parse / compile
  ├─ slim CI build in isolated schema (state-aware when configured)
  ├─ required tests + known-answer checks
  └─ required review / merge protection
          |
          v
Protected merge to main
  ├─ build immutable image or run approved deployment job
  ├─ deploy to staging if required
  ├─ smoke tests / freshness / validation
  └─ production deployment job
          |
          v
Store artifacts -> publish docs -> alert/report -> downstream refresh
```

CI must not receive production write credentials for untrusted PRs. If state-based CI needs production artifacts, expose only the minimum read-only artifact and relation access, and ensure pull-request code cannot use that access to write to production. Never execute untrusted PR scripts with a production deployment token.

### 9.2 GitHub Actions workflow

The workflow below is a **template** for a dbt Core project using a configured adapter and warehouse. Replace placeholders, pin compatible package/action versions, configure protected environments, and implement the warehouse-specific credentials. It illustrates the release gates; it is not a complete universal cloud deployment.

`.github/workflows/dbt-ci-deploy.yml`:

```yaml
name: dbt CI and deploy

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: dbt-${{ github.ref }}
  cancel-in-progress: false

jobs:
  validate:
    if: github.event_name == 'pull_request' && github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    env:
      DBT_SNOWFLAKE_ACCOUNT: ${{ vars.DBT_SNOWFLAKE_ACCOUNT }}
      DBT_SNOWFLAKE_CI_USER: ${{ vars.DBT_SNOWFLAKE_CI_USER }}
      DBT_SNOWFLAKE_CI_ROLE: ${{ vars.DBT_SNOWFLAKE_CI_ROLE }}
      DBT_SNOWFLAKE_CI_WAREHOUSE: ${{ vars.DBT_SNOWFLAKE_CI_WAREHOUSE }}
      DBT_SNOWFLAKE_CI_DATABASE: ${{ vars.DBT_SNOWFLAKE_CI_DATABASE }}
      DBT_SNOWFLAKE_PRIVATE_KEY_PASSPHRASE: ${{ secrets.DBT_SNOWFLAKE_CI_PRIVATE_KEY_PASSPHRASE }}
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install pinned dbt and lint dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r experiments/08_deployment/requirements-ci-snowflake.txt
          dbt deps
      - name: Configure isolated Snowflake CI profile
        env:
          DBT_SNOWFLAKE_PRIVATE_KEY_PEM: ${{ secrets.DBT_SNOWFLAKE_CI_PRIVATE_KEY_PEM }}
        run: |
          set -euo pipefail
          test -n "$DBT_SNOWFLAKE_PRIVATE_KEY_PEM"
          mkdir -p "$HOME/.dbt"
          cp experiments/08_deployment/profiles/profiles.yml.example "$HOME/.dbt/profiles.yml"
          printf '%s' "$DBT_SNOWFLAKE_PRIVATE_KEY_PEM" > "$RUNNER_TEMP/snowflake_ci_key.p8"
          chmod 600 "$RUNNER_TEMP/snowflake_ci_key.p8"
          echo "DBT_SNOWFLAKE_PRIVATE_KEY_PATH=$RUNNER_TEMP/snowflake_ci_key.p8" >> "$GITHUB_ENV"
          echo "DBT_SNOWFLAKE_CI_SCHEMA=DBT_CI_PR_${{ github.event.number }}" >> "$GITHUB_ENV"
      - name: Lint SQL
        run: sqlfluff lint --config experiments/08_deployment/.sqlfluff models
      - name: Parse project
        run: dbt parse --target ci
      - name: Compile project
        run: dbt compile --target ci
      - name: Configure read-only state-artifact access for trusted same-repository PRs
        if: github.event.pull_request.head.repo.full_name == github.repository && vars.DBT_CI_STATE_READ_ROLE_ARN != '' && vars.DBT_PROD_MANIFEST_S3_URI != '' 
        uses: aws-actions/configure-aws-credentials@v6
        with:
          role-to-assume: ${{ vars.DBT_CI_STATE_READ_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - name: Download trusted production state manifest
        if: github.event.pull_request.head.repo.full_name == github.repository && vars.DBT_CI_STATE_READ_ROLE_ARN != '' && vars.DBT_PROD_MANIFEST_S3_URI != '' 
        env:
          STATE_MANIFEST_URI: ${{ vars.DBT_PROD_MANIFEST_S3_URI }}
        run: |
          set -euo pipefail
          test -n "$STATE_MANIFEST_URI"
          mkdir -p prod_state
          aws s3 cp "$STATE_MANIFEST_URI" prod_state/manifest.json
          test -s prod_state/manifest.json
      - name: Run slim CI when trusted state is available; otherwise run full isolated CI build
        env:
          DBT_TARGET: ci
        run: |
          set -euo pipefail
          if [ -s prod_state/manifest.json ]; then
            dbt build --target ci --select "state:modified+" --state ./prod_state --defer
          else
            dbt build --target ci
          fi
      - name: Preserve build artifacts before docs generation overwrites invocation results
        if: always()
        run: |
          mkdir -p artifacts
          [ ! -f target/run_results.json ] || cp target/run_results.json artifacts/run_results_build.json
          [ ! -f target/manifest.json ] || cp target/manifest.json artifacts/manifest_build.json
          [ ! -f target/sources.json ] || cp target/sources.json artifacts/sources.json
          [ ! -f target/freshness.json ] || cp target/freshness.json artifacts/freshness.json
      - name: Generate docs metadata after successful build/tests
        run: dbt docs generate --target ci
      - name: Preserve docs artifacts
        if: always()
        run: |
          mkdir -p artifacts
          [ ! -f target/run_results.json ] || cp target/run_results.json artifacts/run_results_docs.json
          [ ! -f target/manifest.json ] || cp target/manifest.json artifacts/manifest_docs.json
          [ ! -f target/catalog.json ] || cp target/catalog.json artifacts/catalog.json
      - name: Upload dbt artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: dbt-ci-artifacts-${{ github.run_id }}
          path: |
            artifacts/
            target/compiled/
          if-no-files-found: warn
          retention-days: 14

  deploy:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Validate deployment configuration
        env:
          DBT_CLOUD_API_TOKEN: ${{ secrets.DBT_CLOUD_API_TOKEN }}
          DBT_CLOUD_ACCOUNT_ID: ${{ vars.DBT_CLOUD_ACCOUNT_ID }}
          DBT_CLOUD_PROD_JOB_ID: ${{ vars.DBT_CLOUD_PROD_JOB_ID }}
          DBT_CLOUD_BASE_URL: ${{ vars.DBT_CLOUD_BASE_URL }}
        run: |
          set -euo pipefail
          test -n "$DBT_CLOUD_API_TOKEN"
          test -n "$DBT_CLOUD_ACCOUNT_ID"
          test -n "$DBT_CLOUD_PROD_JOB_ID"
          test -n "$DBT_CLOUD_BASE_URL"
      - name: Trigger and wait for the protected dbt Cloud production job
        env:
          DBT_CLOUD_API_TOKEN: ${{ secrets.DBT_CLOUD_API_TOKEN }}
          DBT_CLOUD_ACCOUNT_ID: ${{ vars.DBT_CLOUD_ACCOUNT_ID }}
          DBT_CLOUD_PROD_JOB_ID: ${{ vars.DBT_CLOUD_PROD_JOB_ID }}
          DBT_CLOUD_BASE_URL: ${{ vars.DBT_CLOUD_BASE_URL }}
        run: |
          set -euo pipefail
          base="${DBT_CLOUD_BASE_URL%/}"
          response="$(curl --fail --silent --show-error \
            --request POST \
            --header "Authorization: Token ${DBT_CLOUD_API_TOKEN}" \
            --header "Content-Type: application/json" \
            --data "{\"cause\":\"GitHub Actions merge ${GITHUB_SHA}\"}" \
            "${base}/api/v2/accounts/${DBT_CLOUD_ACCOUNT_ID}/jobs/${DBT_CLOUD_PROD_JOB_ID}/run/")"
          run_id="$(printf '%s' "$response" | jq -er '.data.id')"
          echo "Triggered dbt Cloud run id=${run_id}"
          deadline=$((SECONDS + 3600))
          while [ "$SECONDS" -lt "$deadline" ]; do
            status_response="$(curl --fail --silent --show-error \
              --header "Authorization: Token ${DBT_CLOUD_API_TOKEN}" \
              "${base}/api/v2/accounts/${DBT_CLOUD_ACCOUNT_ID}/runs/${run_id}/")"
            status="$(printf '%s' "$status_response" | jq -er '.data.status')"
            case "$status" in
              10)
                echo "dbt Cloud production run succeeded (run_id=${run_id})"
                exit 0
                ;;
              20|30|40)
                echo "dbt Cloud production run failed with terminal status=${status} (run_id=${run_id})" >&2
                exit 1
                ;;
              1|2|3)
                sleep 15
                ;;
              *)
                echo "Unknown dbt Cloud run status '${status}' for run_id=${run_id}; inspect the run in dbt Cloud." >&2
                exit 1
                ;;
            esac
          done
          echo "Timed out waiting for dbt Cloud run_id=${run_id}; inspect the job before retrying." >&2
          exit 1
```


**This is a deployable template only after the operator supplies the required settings and verifies the dbt Cloud API contract for the account.** Required configuration:
- `DBT_CI_STATE_READ_ROLE_ARN`: a role trusted only for the intended GitHub workflow identity, with read-only access to the one production manifest object; no production warehouse write grants.
- `DBT_PROD_MANIFEST_S3_URI`: a trusted manifest URI updated by the approved production job. The manifest must correspond to the production state you intend to compare against. If either state variable is absent, the workflow skips state download and runs a full isolated CI build.
- The sample warehouse workflow assumes a private repository and a Snowflake CI profile. It is gated to same-repository PRs because it uses protected credentials; allow only trusted contributors to modify workflow/model code that runs with these credentials. For public repositories, add a separate static-only fork-PR job or use a platform-managed CI path that does not expose secrets. The CI role can write only to an isolated `DBT_CI_PR_<number>` schema and has only the read access needed for deferral.
- The local DuckDB Docker requirements/profile are for the training demo only. Do not use them for the Snowflake state/defer workflow. If your actual project is DuckDB-only, use a full isolated CI build and remove the Snowflake-specific workflow steps.
- `DBT_CLOUD_API_TOKEN` as a protected GitHub environment secret; prefer a least-privileged service identity/token supported by the account and rotate it. `DBT_CLOUD_ACCOUNT_ID`, `DBT_CLOUD_PROD_JOB_ID`, and `DBT_CLOUD_BASE_URL` are environment variables. Configure the referenced dbt Cloud job with the production environment, approved branch, freshness/build/test/docs steps, and required notifications. Set the base URL for your account's region.
- The example uses dbt Cloud API v2 status codes (queued/starting/running: `1/2/3`; success: `10`; terminal non-success states: `20/30/40`, commonly error/cancelled/skipped). Verify the API version and response schema for your account; fail closed on unknown status. The workflow's own one-hour polling deadline is a client-side timeout, not a dbt Cloud status code; on timeout it fails without blindly re-triggering a second run.
- `dbt build --select "state:modified+" --state ./prod_state --defer` needs the right selector semantics and isolated CI schema. Validate selection with `dbt ls`; a project may need a selector that includes relevant parents/tests.
- For SQLFluff, pin `sqlfluff` and its dbt templater/adapter-compatible versions in `requirements.txt`; use the correct configuration for your project.
- Pin third-party actions to reviewed full SHAs for production security. Version tags are shown for readability.
- GitHub Actions and dbt Cloud deployment are two distinct runtimes. The workflow triggers and waits for a protected dbt Cloud production job; it does not install production warehouse credentials into GitHub Actions.

### 9.3 A concrete deployment choice

Choose one primary production executor:
- **dbt Cloud:** trigger a protected deploy job through the platform's supported job/API mechanism; credentials and environment live in the platform.
- **Airflow:** build/pull an immutable dbt image, execute it using a supported operator/runtime, collect artifacts, and gate downstream tasks.
- **Kubernetes / Cloud Run / ECS:** publish a versioned image, launch a job with workload identity and environment-specific configuration, and have the orchestrator capture exit status and artifacts.

Avoid running the same production selector from both GitHub Actions and Airflow on overlapping schedules. CI validates; the production orchestrator executes, unless the architecture deliberately makes GitHub Actions the production runner and has controls for it.

---

## 10. Artifact storage, alerts, and duration reporting

### 10.1 Persist artifacts safely

For each invocation, create an immutable prefix such as:

```text
dbt-artifacts/
  environment=production/
    date=2026-10-19/
      run_id=<orchestrator-run-id>/
        manifest.json
        run_results.json
        sources.json
        freshness.json
        catalog.json
        dbt.log
```

The exact artifact set depends on which commands ran and the dbt version. Copy artifacts immediately after each invocation before another command overwrites them. If a command fails before producing an artifact, store the available logs and record that the artifact is missing rather than treating the job as successful.

For object storage, configure private access, encryption, retention, lifecycle rules, and access logs. Avoid publishing full `manifest.json`, compiled SQL, or catalogs to a public static website without a security review.

### 10.2 Example: run a command and archive artifacts without masking failure

The following Bash wrapper is for a container that has `dbt`, `aws`, and a configured workload identity. It preserves the dbt command's exit code, uploads whatever artifacts exist, and then returns the original command status. The S3 prefix and role must be configured by the operator.

`scripts/run_dbt_and_archive.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

: "${DBT_ARTIFACT_BUCKET:?Set a private artifact bucket name}"
: "${DBT_ENVIRONMENT:?Set environment name}"
: "${DBT_RUN_ID:?Set a unique orchestrator run ID}"

if [ "$#" -lt 1 ]; then
  echo "Usage: run_dbt_and_archive.sh <dbt-subcommand> [args...]" >&2
  exit 64
fi

artifact_dir="${DBT_PROJECT_DIR:-.}/target"
prefix="s3://${DBT_ARTIFACT_BUCKET}/dbt/${DBT_ENVIRONMENT}/${DBT_RUN_ID}"
mkdir -p "$artifact_dir"
# Prevent an invocation that fails before writing artifacts from uploading stale
# results left by an earlier command under this invocation's run ID.
rm -f \
  "${artifact_dir}/run_results.json" \
  "${artifact_dir}/sources.json" \
  "${artifact_dir}/freshness.json" \
  "${artifact_dir}/catalog.json"
set +e
dbt "$@"
dbt_status=$?
set -e

# Upload only known artifacts/logs; do not archive the entire environment.
upload_status=0
if [ -f "${artifact_dir}/run_results.json" ]; then
  csv_path="/tmp/dbt-node-results-${DBT_RUN_ID}.csv"
  python "${DBT_PROJECT_DIR:-.}/experiments/08_deployment/scripts/summarize_run_results.py" \
    "${artifact_dir}/run_results.json" --csv "$csv_path" \
    --run-id "$DBT_RUN_ID" --environment "$DBT_ENVIRONMENT" || upload_status=$?
  if [ -f "$csv_path" ]; then
    aws s3 cp "$csv_path" "${prefix}/node_run_results.csv" || upload_status=$?
  fi
fi
for artifact in manifest.json run_results.json sources.json freshness.json catalog.json; do
  if [ -f "${artifact_dir}/${artifact}" ]; then
    aws s3 cp "${artifact_dir}/${artifact}" "${prefix}/${artifact}" || upload_status=$?
  fi
done
if [ -f "${DBT_PROJECT_DIR:-.}/logs/dbt.log" ]; then
  aws s3 cp "${DBT_PROJECT_DIR:-.}/logs/dbt.log" "${prefix}/dbt.log" || upload_status=$?
fi
if [ "${1:-}" = "docs" ] && [ "${2:-}" = "generate" ]; then
  # The docs publisher runs in a later Airflow task, possibly on another worker.
  aws s3 sync "$artifact_dir" "${prefix}/docs/" \
    --exclude '*' --include 'index.html' --include '*.json' \
    --include '*.css' --include '*.js' --include 'assets/*' || upload_status=$?
fi

if [ "$dbt_status" -ne 0 ]; then
  echo "dbt failed with exit=${dbt_status}; artifacts prefix=${prefix}" >&2
  exit "$dbt_status"
fi
if [ "$upload_status" -ne 0 ]; then
  echo "dbt succeeded but artifact upload failed; prefix=${prefix}" >&2
  exit "$upload_status"
fi
echo "dbt succeeded; artifacts archived at ${prefix}"
```

This wrapper archives artifacts only if they exist. It intentionally does not upload `profiles.yml`, private keys, `.env`, or arbitrary directories. If artifact upload fails after a successful build, it returns non-zero so the pipeline can alert; the runbook should distinguish “transformation succeeded, artifact archive failed” from “transformation failed.” For commands that overwrite `target/run_results.json`, archive after each invocation with a distinct `DBT_RUN_ID` or step suffix.

### 10.3 Summarize build duration

For a simple per-node duration table, use the parser in Section 3.3. To create a warehouse table, store one record per invocation/node with:
- `invocation_id`, environment, Git commit, target, job/DAG run ID.
- `unique_id`, resource type, status, `execution_time`.
- Start/end timestamps when available, adapter/warehouse, and error classification.
- Artifact schema version and collection timestamp.

Use orchestrator start/end time for wall-clock duration. Do not add node execution times and call the result total elapsed duration when dbt executes nodes concurrently.

A useful dashboard should show:
- Total wall-clock duration and trend.
- Slowest models/tests by execution time.
- Failure and retry rate.
- Source freshness misses and SLA breaches.
- Warehouse/query cost where the platform exposes it.
- Full-refresh/backfill runs separately from ordinary daily builds.
- Duration by environment, selector, and commit.

### 10.4 Store node timings in a table and chart them

The wrapper in Section 10.2 emits `node_run_results.csv` alongside `run_results.json`. In the DuckDB learning environment, load that CSV into an operational table (the file path is an example; adapt it to your mount and retention model):

```python
from pathlib import Path
import csv
import duckdb

# First create this CSV from the latest target/run_results.json:
# python experiments/08_deployment/scripts/summarize_run_results.py \
#   target/run_results.json --csv /tmp/dbt-node-results-latest.csv \
#   --run-id local-lab --environment dev
csv_path = Path("/tmp/dbt-node-results-latest.csv")
database_path = Path("dev.duckdb")  # Match DBT_DUCKDB_DEV_PATH in your local profile.

with csv_path.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

columns = [
    "invocation_id", "run_id", "environment", "dbt_version", "unique_id",
    "resource_type", "status", "execution_time_seconds", "message",
]
values = [
    tuple(
        float(row[column]) if column == "execution_time_seconds" else row[column]
        for column in columns
    )
    for row in rows
]

with duckdb.connect(str(database_path)) as connection:
    connection.execute("CREATE SCHEMA IF NOT EXISTS ops")
    connection.execute("""
        CREATE TABLE IF NOT EXISTS ops.dbt_node_run_results (
            invocation_id VARCHAR,
            run_id VARCHAR,
            environment VARCHAR,
            dbt_version VARCHAR,
            unique_id VARCHAR,
            resource_type VARCHAR,
            status VARCHAR,
            execution_time_seconds DOUBLE,
            message VARCHAR
        )
    """)
    connection.executemany(
        "INSERT INTO ops.dbt_node_run_results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        values,
    )
```

The example appends rows; add a unique key or deduplication rule for `(invocation_id, unique_id)` before using it in a recurring ingestion job. Run the parser immediately after the build invocation if you need model/test timings; a later `dbt docs generate` invocation writes its own `run_results.json`. A dbt invocation can include the same model across separate invocations, so `unique_id` alone is not a primary key.

Query the slowest models over recent runs:

```sql
select
    unique_id,
    count(*) as executions,
    round(avg(execution_time_seconds), 2) as avg_seconds,
    round(max(execution_time_seconds), 2) as max_seconds,
    sum(case when status not in ('success', 'pass', 'warn', 'skipped', 'no-op')
             then 1 else 0 end) as non_success_results
from ops.dbt_node_run_results
where environment = 'production'
group by unique_id
order by avg_seconds desc;
```

For a production warehouse, create the same logical table and load the CSV/JSON artifacts using the warehouse's supported external stage, bulk-load, or ingestion mechanism. Use the invocation ID and unique ID for deduplication, preserve raw artifacts for audit, and keep error messages access-controlled. Chart average/max execution time by model and run date; use scheduler timestamps—not the sum of parallel node times—for overall job duration.

### 10.5 Alerts that identify the failure

At minimum, alert with:
- DAG/job name and run ID.
- Failed task and, where available, dbt model/test unique ID.
- Environment, commit SHA, attempt number, and timestamp.
- Error summary and link to the scheduler log/runbook.
- Owner/on-call route and whether downstream publication was blocked.

Airflow's `on_failure_callback` receives task context; a callback can extract `dag_id`, `task_id`, `run_id`, and log URL. Model-level details require parsing dbt output/artifacts or using Cosmos task identity. Never put passwords, private keys, or raw secret environment values in alert messages.

A minimal Airflow callback shape:

```python
def alert_failure(context):
    ti = context.get("task_instance")
    dag_id = getattr(ti, "dag_id", "unknown")
    task_id = getattr(ti, "task_id", "unknown")
    run_id = context.get("run_id", "unknown")
    exception = context.get("exception")
    log_url = getattr(ti, "log_url", None)

    # Send through an Airflow Connection / notification service.
    # Sanitize exception text; never dump all context or environment variables.
    message = (
        f"dbt pipeline failed: dag={dag_id} task={task_id} "
        f"run_id={run_id} exception={str(exception)[:1000]} log={log_url}"
    )
    # notify_on_call(message)
```

The notification function is intentionally a placeholder. Configure a Slack provider, email backend, PagerDuty integration, or internal incident service and test delivery. An exception can contain SQL or sensitive literals; sanitize before sending it to a broad channel.

### 10.6 Freshness SLAs and Elementary

- **Source freshness SLA:** defines how late an upstream source may be before it is considered stale. Configure `loaded_at_field`, thresholds, and source-specific exceptions according to the source's semantics.
- **Model/test SLA:** defines how quickly critical models must finish and how quickly a failure must be detected.
- **Elementary:** a dbt-focused observability tool that can collect test/monitoring signals and support alerts/reports; exact features and deployment vary by release and product configuration. It complements rather than replaces an incident owner and tested runbook.
- **Cost dashboard:** correlate warehouse/query history with dbt model identifiers and job/run IDs where possible. Cost attribution is platform-specific and may be approximate.

Avoid alert fatigue: route actionable production failures to on-call, aggregate repeated failures, and make ownership explicit.

---

## 11. Failure handling, reruns, and recovery

### 11.1 Production runbook: a dbt test failed

**Trigger:** required production test fails and the build exits non-zero.

1. **Acknowledge and classify.** Capture environment, DAG/job run ID, commit SHA, failed model/test unique ID, status/message, warehouse query ID, and artifact path.
2. **Stop downstream publication.** Confirm downstream refreshes did not run after the failed gate. If they ran incorrectly, identify affected consumers and notify the owner.
3. **Determine scope.** Is the failure a genuine data-quality regression, a source freshness issue, a schema/permission problem, a transient warehouse error, or a test defect?
4. **Compare to baseline.** Inspect the failing test SQL, recent model/metric changes, source counts/freshness, and prior successful artifacts. Do not weaken a test just to restore green status.
5. **Contain safely.** If the new data is untrusted, pause the dependent refresh or route consumers to a previously validated relation only if a tested rollback/fallback exists. Do not overwrite production with a developer's local build.
6. **Fix or recover.** Correct the upstream data or model, or apply an approved narrow rerun. Rebuild impacted nodes and rerun the required tests.
7. **Validate.** Run reconciliation/known-answer checks and verify downstream consumers see the intended result.
8. **Communicate.** Notify the metric/model owner and affected consumers of impact, start/end time, workaround, and next update.
9. **Close the incident.** Record root cause, detection gap, corrective action, and follow-up owner.

### 11.2 Reruns and retries

- Rerun a failed task only after determining whether it is safe to repeat its side effects.
- If dbt completed some nodes before failure, inspect the artifact and dependency graph; rerunning the selected graph is usually preferable to assuming nothing changed.
- Use `dbt retry` only when supported by the installed dbt version and when the saved prior invocation state is available; otherwise use a reviewed selector/build command.
- A transient network/warehouse error may justify retry. A deterministic test failure usually needs investigation, not repeated retries.
- Keep retries bounded and alert after exhaustion.

### 11.3 Selective full refresh

`--full-refresh` can rebuild an incremental model from its full source history. It can be expensive and may change results if the model logic or historical source data has changed.

```bash
# Example only: run after review and during an approved maintenance window.
dbt build --target prod --select fct_orders --full-refresh
```

Before running:
1. Confirm the model is incremental and the adapter supports the intended behavior.
2. Estimate scan/compute cost and runtime.
3. Check locks, downstream consumers, and warehouse capacity.
4. Confirm the incremental strategy, unique key, late-arriving data handling, and schema-change policy.
5. Use the narrowest selector that is correct.
6. Capture artifacts and compare row counts/aggregates with the baseline.
7. Notify consumers if freshness or output semantics will change.

Do not run `--full-refresh` across the entire project as a generic response to a failure.

### 11.4 Microbatch backfills

For models configured with a supported microbatch strategy, use the version/adapter-specific backfill options documented for the installed dbt release. A safe backfill procedure:
- Identify the affected event-time interval and timezone.
- Confirm whether late data changes previously built buckets.
- Select only the affected model(s) and interval(s).
- Use a staging schema or a safe dry-run/estimate where available.
- Backfill bounded ranges, verify each batch, and monitor warehouse cost.
- Reconcile adjacent boundaries and downstream aggregates.
- Publish only after tests pass.

Do not invent a universal microbatch flag: supported syntax and adapter behavior vary. If the model does not use microbatch, use its documented incremental/full-refresh strategy instead.

### 11.5 Rollback and recovery

dbt is a transformation system, not a universal transactional rollback manager. Rolling back Git code does not automatically restore warehouse tables to their prior contents.

A controlled recovery:
1. Stop or pause the scheduled job if it is repeatedly damaging data.
2. Identify the last known-good commit and artifact set.
3. Determine whether the prior code can safely rebuild the affected relations.
4. If the warehouse supports time travel/snapshots/table clones, follow the platform's approved recovery procedure and permissions.
5. Otherwise rebuild affected models from validated sources using the last known-good code in a controlled target or approved production run.
6. Rerun tests and reconcile before unpausing downstream refreshes.
7. Record any interval of stale or inconsistent data and communicate it to consumers.

For breaking schema changes, coordinate code and consumer rollout. Do not assume that restoring an old model definition can reverse destructive DDL or restore deleted historical source data.

---

## 12. Backfills, ownership, and deprecation

### 12.1 Backfill decision matrix

| Situation | Preferred action | Guardrail |
|---|---|---|
| One transient task failure | Retry once after classifying error | Check idempotency and warehouse state |
| One model's logic changed | Build the model and downstream dependents with a reviewed selector | Test affected contracts/metrics and compare outputs |
| Late data for bounded dates | Use the model's supported incremental/microbatch strategy | Confirm update window and downstream recomputation |
| Historical logic correction | Selective full refresh or controlled backfill | Cost estimate, baseline comparison, approval |
| Widespread incorrect production output | Pause dependent refreshes; restore/rebuild from known-good state | Incident commander and consumer communication |
| Schema-breaking change | Version/migrate consumer contract | Do not silently replace a public model |

### 12.2 Ownership and on-call

Every production model/domain needs:
- **Business owner:** defines expected meaning and consumer impact.
- **Technical owner:** maintains SQL, tests, configuration, and deployment.
- **On-call route:** receives actionable alerts and knows how to escalate.
- **Runbook:** symptoms, diagnostic commands, rollback/backfill instructions, and communication templates.
- **SLA:** freshness and availability expectations with alert thresholds.
- **Deprecation policy:** notice period, consumer inventory, replacement path, and removal approval.

Do not assign every failure to “the data team” without a named accountable owner.

### 12.3 Communicating data changes

For a breaking or material change, communicate:
- What changed and why.
- Affected models/columns/metrics/dashboards.
- Effective time and historical backfill behavior.
- Whether prior results may change.
- Validation/reconciliation evidence.
- Consumer action and migration deadline.
- Owner and incident/update channel.

Use dbt docs, exposures, GitHub pull requests, catalogue metadata, and downstream usage information where available to identify consumers. Declared exposures are helpful but may not enumerate every external query or notebook.

---

## 13. Orchestration alternatives

| Platform | Good fit | Advantages | Trade-offs / operational questions |
|---|---|---|---|
| **dbt Cloud** | dbt-centric teams wanting managed jobs, environments, CI, logs, and platform integrations | Less scheduler infrastructure to operate; native dbt job history/artifacts | Product entitlements, supported connections, and cross-system orchestration boundaries must be checked |
| **Apache Airflow** | Complex pipelines with ingestion, dbt, APIs, file transfers, ML, and downstream dependencies | Flexible DAG/task control, broad ecosystem, retries, scheduling | Team owns scheduler/worker upgrades, plugins/providers, capacity, secrets, and operational reliability |
| **Dagster + `dagster-dbt`** | Asset-oriented orchestration and software-defined data products | dbt resources can be represented in asset/dependency workflows; useful asset observability | New platform and operating model; validate integration/version compatibility and team skill |
| **Prefect** | Python-centric workflows and orchestration with dynamic control flow | Flexible flow/task patterns and deployment choices | dbt is one task/integration among others; compare deployment/observability needs |
| **Databricks Workflows** | dbt jobs centered on Databricks compute/data platform | Platform-native scheduling and permissions for Databricks-centered workloads | Less natural as the only orchestrator for a heterogeneous enterprise stack |
| **Azure Data Factory (ADF)** | Azure-centric integration and scheduling across services | Integrates with Azure data movement/orchestration services | dbt execution may need an external runtime or command activity; manage credentials and logs across layers |
| **Snowflake tasks** | Simple Snowflake-native scheduled SQL/task chains | Native scheduling for supported Snowflake workloads | Not a general replacement for a cross-system orchestrator; external dbt runtime/commands need a deliberate integration |

### 13.1 Decision guide

- If the production workflow is primarily dbt and managed scheduling is sufficient, evaluate dbt Cloud first.
- If dbt is one part of a larger ingestion/API/ML workflow, Airflow or an asset/workflow orchestrator may be more appropriate.
- If the organization already standardizes on Dagster, Prefect, Databricks Workflows, ADF, or Snowflake tasks, prefer the established platform if it meets dependency, security, observability, and recovery requirements.
- Avoid selecting based on feature lists alone. Run the same failure/retry/backfill exercise and measure operator effort, incident visibility, security boundaries, and cost.

---

## 14. Hands-on lab — `experiments/08_deployment/`

### 14.1 Objective

Containerize the existing dbt project, execute it from a clean runtime, orchestrate freshness → build → tests → docs, alert on failures, add PR CI and a controlled production deployment path, compare dbt Cloud if access exists, and persist run artifacts for duration analysis.

### 14.2 Prerequisites

- Existing dbt project containing `stg_orders`, `stg_customers`, `stg_payments`, `int_orders_payments`, `fct_orders`, and `dim_customers`.
- The appropriate adapter and warehouse credentials.
- Python/dbt/adapter versions pinned and tested together.
- Docker or a supported cloud job runtime.
- For Airflow: a supported Airflow deployment and worker/execution image.
- For Cosmos: a compatible Cosmos release and adapter profile mapping.
- For GitHub Actions: repository branch protection, protected production environment, and CI-only credentials; OIDC trust policy if using cloud federation.
- Private artifact storage and an alert route.
- Optional: dbt Cloud account/project and an eligible deployment environment.

### 14.3 Lab structure

```text
experiments/
└── 08_deployment/
    ├── README.md
    ├── Dockerfile
    ├── requirements.txt
    ├── requirements-ci-snowflake.txt
    ├── .sqlfluff
    ├── profiles/
    │   └── profiles.yml.example
    ├── dags/
    │   ├── dbt_production.py
    │   └── dbt_cosmos_production.py
    ├── scripts/
    │   ├── run_dbt_and_archive.sh
    │   └── summarize_run_results.py
    ├── .github/
    │   └── workflows/
    │       └── dbt-ci-deploy.yml
    ├── runbooks/
    │   └── dbt-test-failure.md
    └── evidence/
        └── README.md
```

The lab files are an exercise layout. dbt will only discover project models/YAML under configured project paths; the Airflow DAG directory and deployment scripts do not automatically become part of the dbt project.

### 14.4 Step 1 — containerize

Copy the project's actual `dbt_project.yml`, models, macros, packages configuration, tests, seeds, snapshots, and any required project files into the image build context. Adapt the Dockerfile in Section 7.2 to the actual repository; remove any `COPY` instruction for a directory that does not exist.

Pin dbt Core, adapter, Python, and packages. Replace the placeholder versions in `requirements.txt` with a compatible tested set before building.

```bash
docker build -t analytics-dbt:lab .
docker run --rm analytics-dbt:lab --version
```

Expected result: image builds and the dbt CLI reports its version. This verifies the local image only; it does not prove warehouse connectivity or production readiness.

### 14.5 Step 2 — run from a clean container

Create a local profile outside Git and set the necessary non-secret environment variables. For the DuckDB demonstration profile:

```bash
mkdir -p .local-profiles
# Create .local-profiles/profiles.yml using the dev profile from Section 2.2.

docker build -f experiments/08_deployment/Dockerfile -t analytics-dbt:lab .
docker run --rm \
  --env DBT_DUCKDB_DEV_PATH=/data/dev.duckdb \
  --env DBT_PROJECT_DIR=/opt/dbt/project \
  --mount type=bind,src="$PWD/.local-profiles",dst=/opt/dbt/profiles,readonly \
  --mount type=volume,src=dbt-lab-data,dst=/data \
  analytics-dbt:lab \
  build --target dev --profiles-dir /opt/dbt/profiles
```

If the image does not bake in the project, mount or copy the project into the expected path. For a cloud warehouse, replace the local profile with the correct adapter profile and securely injected credentials. Expected outcome: command exits `0` and creates the expected relations/tests in the isolated dev target.

### 14.6 Step 3 — create the Airflow DAG

Use the DAG in Section 5.3 as the DAG-level execution approach, or adapt the Cosmos example in Section 6. Do not deploy both DAGs on the same production schedule. Set `DBT_PROJECT_DIR`, `DBT_PROFILES_DIR`, target, worker image, network, and secrets to match the actual Airflow deployment.

For a production worker with ephemeral task containers, add an artifact-upload step to each invocation or run the whole sequence in one container and upload artifacts in a `finally`/shell-trap path. Ensure artifact upload failure does not mask the original dbt exit status.

Expected outcome: Airflow renders the DAG and can execute it against a non-production target. Verify that freshness failure blocks `dbt build` and that a required test failure within `dbt build` blocks docs generation, publication, and downstream refresh.

### 14.7 Step 4 — add failure alerting

Implement the `alert_failure` callback from Section 10.3 using the approved Airflow Slack/email/PagerDuty integration. Store connection credentials in Airflow Connections or a Secrets Backend. Trigger a controlled failure in a non-production DAG and confirm the alert identifies the DAG, task, run ID, and log link.

Do not test by breaking production data. If the callback is attached at DAG/task default arguments, verify whether callback behavior covers retries and final failure as intended in the installed Airflow version.

### 14.8 Step 5 — implement PR CI and production deployment

Add the workflow from Section 9.2, then complete all operator-specific configuration:
- Populate trusted `prod_state/manifest.json` through a secure read-only artifact retrieval step, or replace slim CI with a full isolated CI build until state retrieval is configured.
- Configure a valid CI target/profile and isolated schema/database.
- Pin all dependencies and GitHub Actions to reviewed versions/SHAs.
- Configure SQLFluff to match the project's adapter/templater.
- Protect `main` and the `production` environment.
- Implement the deploy step by triggering dbt Cloud or publishing/running a pinned image through the chosen orchestrator.
- Make sure PR jobs cannot access production write credentials.

Expected outcome: a pull request produces a required validation status; a merge invokes only the selected production deployment mechanism. Confirm that no second scheduler launches a conflicting build.

### 14.9 Step 6 — optional dbt Cloud comparison

If the account and required features are available:
1. Connect the same repository to a dbt Cloud project.
2. Configure separate development and deployment environments.
3. Configure a CI job for pull requests and a production deploy job.
4. Configure source freshness, build/test commands, docs/artifact retention, and notifications.
5. Run the same commit and compare setup effort, logs, retry controls, artifact access, and integration limits with Airflow.
6. Record which features depend on the account plan or warehouse integration.

If the account or feature is unavailable, document the missing prerequisite and complete the local/Airflow lab. Do not mark the hosted comparison as executed.

### 14.10 Step 7 — store artifacts and summarize durations

After each dbt invocation, preserve:
- `run_results.json`
- `manifest.json`
- `sources.json` or `freshness.json` if generated
- `catalog.json` if docs generation completed
- relevant logs and command exit status

Use a unique run ID in the artifact path. Run the parser from Section 3.3 against each `run_results.json`. For a warehouse duration table, ingest the parsed node records and use scheduler timestamps for end-to-end wall-clock duration. Record an example only after running the job; do not fabricate timings.

`evidence/README.md` should contain:
- dbt/Python/adapter/Airflow/Cosmos versions.
- Environment and target (no secrets).
- Git commit SHA and run/DAG ID.
- Commands and exit codes.
- Artifact locations and schema versions.
- Summary of failed/passed nodes and actual durations.
- CI/deployment result and alert-delivery result.
- Any untested hosted integration or cloud prerequisite.

### 14.11 Troubleshooting

| Symptom | Likely cause | Response |
|---|---|---|
| `dbt: command not found` | dbt is not installed in the runtime or executable path is wrong | Inspect image/venv and pin dependencies |
| Adapter import/connection failure | Incompatible adapter version, missing network access, or wrong credentials/profile | Check `dbt --version`, `dbt debug`, adapter profile, network, and secret injection |
| `source freshness` fails | Stale source, incorrect `loaded_at_field`, timezone mismatch, or permission issue | Inspect freshness artifact/log and source SLA before proceeding |
| Build exits non-zero | Compilation, warehouse, model, or test failure | Identify failing node/status from logs and run artifacts |
| `run_results.json` absent | Command failed before artifact creation or output path differs | Preserve logs and report missing artifact; don't mask the command failure |
| Slim CI selects nothing or too much | Missing/stale production manifest or incorrect selector | Retrieve trusted state, inspect with `dbt ls`, and verify CI target isolation |
| Airflow task runs locally but not in deployment | Project/profile files, packages, network, or credentials differ between runtimes | Compare image digest, mounts, environment, identity, and logs |
| Cosmos DAG parse fails | Incompatible Cosmos API, missing/stale manifest, wrong profile mapping | Pin Cosmos and follow that version's quickstart; validate manifest availability |
| Duplicate notifications or repeated writes | Retry repeats side effects or overlapping runs | Add run IDs/idempotency, bound retries, limit concurrency, separate notifications |
| Docs task succeeds but consumers cannot see docs | Only `dbt docs generate` ran; no publishing/hosting step configured | Implement private artifact upload or approved hosting/publishing mechanism |
| Production deploy works from CI but not Airflow | Different identity, network, target, adapter, or secret source | Compare execution context; never copy production credentials into PR CI |
| Duration totals seem larger than job duration | Summed node times include parallel execution | Use orchestrator wall-clock timestamps for elapsed job duration |

### 14.12 Completion criteria

- [ ] Development, CI, staging, and production targets/schemas are isolated and documented.
- [ ] dbt and adapter versions are pinned and compatible.
- [ ] A clean container runs dbt using environment configuration and no committed secrets.
- [ ] Airflow executes freshness → build/run → tests → docs/publication with correct dependency gates.
- [ ] Cosmos alternative is understood and either tested in a compatible environment or explicitly left unverified.
- [ ] Failure alerts identify the DAG/task and model/test when available.
- [ ] PR CI uses an isolated schema and trusted state artifacts if slim CI is enabled.
- [ ] Production deploy runs only through the approved executor and protected identity.
- [ ] Artifacts are stored securely per invocation; `run_results.json` is summarized.
- [ ] Wall-clock duration is distinguished from the sum of parallel node durations.
- [ ] A test failure runbook has been exercised in a non-production environment.
- [ ] Reruns, selective full refreshes, and backfills have explicit safety checks.
- [ ] dbt Cloud has been compared if access is available; otherwise prerequisites are documented.
- [ ] Model/domain owners, on-call route, freshness SLA, and consumer communication process are defined.

---

## 15. Common mistakes

1. **Running production manually from a laptop.** Use the approved scheduler/deployment identity and auditable code.
2. **Committing credentials.** Keep secrets in managed connections/secret stores or use short-lived identity.
3. **One full build every hour by default.** Choose a schedule based on freshness SLA, dependency needs, and warehouse cost.
4. **Confusing `dbt run` and `dbt build`.** `build` runs applicable tests in dependency order; an additional full `test` may be redundant.
5. **Assuming retries are always safe.** Review idempotency, hooks, exports, and downstream side effects.
6. **Using slim CI without a trusted state manifest.** Keep production comparison state separate from CI output and isolate writes.
7. **Assuming docs generation publishes documentation.** `dbt docs generate` creates artifacts; hosting/upload is a separate configured step.
8. **Treating node-duration sums as total elapsed time.** dbt can execute nodes concurrently.
9. **Leaving a failed test without an owner.** Alerts need routing, runbooks, and a clear incident owner.
10. **Using `--full-refresh` broadly to fix any issue.** Scope the model and interval, estimate cost, and verify recovery.
11. **Rolling back Git and assuming warehouse data rolled back.** Code rollback and data restoration are separate operations.
12. **Running the same production schedule in two orchestrators.** Assign a single owner for production execution.
13. **Assuming a local demo proves a cloud deployment.** Validate the actual runtime, credentials, network, artifact storage, and alert route.

---

## 16. Roadmap checkpoint

Before considering Topic 08 complete, be able to:
- Draw the production flow from ingestion completion through freshness, dbt build/tests, docs/artifact publication, and downstream refresh.
- Explain environment targets and schema isolation.
- Interpret exit codes and `run_results.json`.
- Explain dbt Cloud projects, deployment environments, CI/deploy jobs, and scheduling.
- Compare BashOperator, container/virtualenv execution, and Cosmos.
- Configure secret injection and explain OIDC/key-pair trade-offs.
- Describe the CI/CD gates and the trusted state artifact required for slim CI.
- Explain artifact retention, alert payloads, freshness SLAs, and duration reporting.
- Execute a safe rerun/backfill and explain when selective full refresh is appropriate.
- Use the failed-test runbook and communicate impact to consumers.
- Compare dbt Cloud, Airflow, and Dagster for a defined use case.

---

## References

Use current official documentation for the exact versions and product plans used by your project:

- dbt deployment environments: https://docs.getdbt.com/docs/deploy/deploy-environments
- dbt deployment jobs: https://docs.getdbt.com/docs/deploy/deploy-jobs
- dbt CI: https://docs.getdbt.com/docs/deploy/continuous-integration
- dbt run results artifact: https://docs.getdbt.com/reference/artifacts/run-results-json
- Astronomer Cosmos: https://github.com/astronomer/astronomer-cosmos
- GitHub Actions OIDC in AWS: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws
- dbt documentation: https://docs.getdbt.com/

The lesson's examples are templates for review and adaptation. Verify all version-sensitive commands, operator imports, adapter settings, and integration entitlements before using them in production.
