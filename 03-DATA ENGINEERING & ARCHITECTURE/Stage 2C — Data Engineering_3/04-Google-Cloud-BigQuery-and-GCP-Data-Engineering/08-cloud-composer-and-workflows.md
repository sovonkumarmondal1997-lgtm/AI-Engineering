# Cloud Composer and Workflows

> **Stage 2C — Data Engineering_3 · 04-Google-Cloud-BigQuery-and-GCP-Data-Engineering · Topic 08**
>
> Target file: `08-cloud-composer-and-workflows.md`  
> Hands-on workspace: `experiments/08_composer/`

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Explain orchestration versus processing and model a pipeline as dependencies, state transitions, retries, and observable outcomes.
- Deploy and operate Cloud Composer, the managed Apache Airflow service, and understand its environment, DAGs bucket, scheduler, workers, triggerer, and UI.
- Use `BigQueryInsertJobOperator`, `GCSToBigQueryOperator`, `DataprocSubmitJobOperator`, and `DataflowTemplatedJobStartOperator` with the Google provider.
- Design idempotent, parameterized DAGs using Airflow templates such as `{{ ds }}`, sensible retries, timeouts, pools, concurrency limits, and controlled backfills.
- Use Workflows YAML to call Google Cloud APIs with the workflow's service account, handle errors, and chain API operations without maintaining an Airflow environment.
- Trigger Workflows with Cloud Scheduler or Eventarc when time-based or event-based initiation is sufficient.
- Test DAG imports and task structure locally, lint code, deploy with a controlled CI/CD process, and monitor failures and SLOs.
- Choose Composer, Workflows, Cloud Scheduler plus Cloud Run Jobs, or tools such as Dagster and Prefect based on actual requirements.

### Prerequisites

The roadmap assumes prior familiarity with:

- SQL, BigQuery jobs and tables, and cost controls (Topics 02–05).
- GCS ingestion, schemas, write dispositions, and data-quality handling (Topic 04).
- Pub/Sub and Dataflow jobs (Topic 06).
- Dataproc clusters and Serverless batches (Topic 07).
- Python, pytest, Git, Terraform, IAM, service accounts, and basic networking.
- Airflow DAG fundamentals from the earlier Airflow module.

### Lab cost warning

Cloud Composer environments are long-lived managed resources and can incur charges even when no DAG is running. Creating an environment may take tens of minutes. Workflows, Cloud Scheduler, BigQuery, logging, and storage may also incur charges according to current pricing and usage. Enable billing only if authorized, set a budget alert, use a dedicated lab project, and delete resources after testing. A budget alert is not a hard spending cap.

---

## 2. Orchestration fundamentals and dependency modelling

### 2.1 Orchestration is not processing

**Orchestration** decides *when* work runs, *which task depends on which*, *what to do on failure*, and *how to expose state*. **Processing** performs the heavy work: BigQuery executes SQL, Dataflow executes Beam pipelines, Dataproc runs Spark, and Cloud Run Jobs executes containerized code.

Do not load a large dataset into an Airflow worker and transform it there. Airflow workers should submit and monitor remote jobs, pass small metadata values, and enforce dependencies.

Example pipeline:

```text
GCS object for logical date
        |
        v
load raw file into BigQuery staging
        |
        v
run idempotent transform / MERGE
        |
        v
data-quality assertions
        |
        v
publish success metadata

Any failed task -> alert / incident workflow
```

### 2.2 Model dependencies explicitly

A task should have one clear responsibility and a bounded input/output contract. Define:

- **Trigger condition:** schedule, object arrival, event, or upstream task completion.
- **Logical date:** the data interval being processed, not necessarily the wall-clock date when the task starts.
- **Input contract:** expected object path, schema, partition, and completeness rule.
- **Output contract:** destination table/partition and how reruns behave.
- **Retry contract:** which failures are transient and safe to retry.
- **Timeout and concurrency:** maximum task duration, simultaneous DAG runs, and limits on expensive downstream work.
- **Completion contract:** data-quality checks and durable evidence of success.
- **Recovery contract:** rerun one task, rerun the date, backfill a range, or replay an event.

### 2.3 Airflow scheduling vocabulary

- **DAG:** a directed acyclic graph of tasks and dependencies.
- **Task instance:** a task for a particular DAG run/logical date.
- **Logical date / data interval:** the time period a run represents. Use Airflow's templating and data-interval semantics rather than `datetime.now()` for historical data selection.
- **Catchup:** whether Airflow creates runs for past intervals that have not been scheduled.
- **Backfill:** deliberately running a DAG for historical intervals.
- **Sensor:** waits for a condition such as a GCS object existing.
- **Trigger rule:** determines whether a task runs based on upstream task states.
- **Deferrable operator/sensor:** yields worker capacity while waiting, using a triggerer when supported and configured.
- **Pool:** limits concurrency for a named class of tasks.
- **XCom:** a mechanism for small task-to-task metadata. Do not pass datasets or large payloads through XCom.

### 2.4 A practical reliability principle

Retries provide *at-least-once attempts*, not automatic exactly-once business effects. If a BigQuery load succeeds but the worker loses its response, Airflow may retry. Use deterministic job IDs where the operator/API supports them, stable partition destinations, staging tables, `MERGE`, and validation. Make it safe to run the same logical date more than once.

---

## 3. Cloud Composer architecture and Airflow DAGs

### 3.1 What Composer manages

Cloud Composer is Google's managed Apache Airflow service. A Composer environment provides the managed Airflow runtime and integrates it with Google Cloud resources.

Core concepts:

- **Environment:** the managed Airflow deployment, its configuration, and supporting infrastructure.
- **DAGs bucket:** a Cloud Storage bucket used for DAG files and related environment artifacts. Uploading a DAG makes it available to the environment; it does not guarantee that the DAG imports successfully or is scheduled.
- **Airflow UI:** inspect DAGs, runs, task states, logs, rendered templates, and task dependencies.
- **Scheduler:** determines which task instances should run.
- **Workers:** execute task code and operators.
- **Triggerer:** runs asynchronous triggers for compatible deferrable tasks.
- **DAG processor / parsing:** loads DAG definitions and reports import errors.
- **Cloud Logging and Monitoring:** provide operational logs and metrics.

The exact infrastructure and configuration differ by Composer generation and image. Composer 2 and Composer 3 have different networking, resource configuration, scaling, and environment-management details. Do not apply a Composer 2 setting to Composer 3 without checking the current documentation for the chosen generation.

### 3.2 Environment and DAG lifecycle

1. Create the environment and its runtime service account.
2. Configure network, image, worker/scheduler resources, environment variables, and Python packages.
3. Upload DAG code and supporting modules to the environment's DAGs bucket.
4. Check import errors and confirm the DAG appears in the UI.
5. Trigger a controlled test run and inspect rendered templates and task logs.
6. Verify the output data and failure/retry behavior.
7. Deploy code through CI/CD and promote it between environments.
8. Upgrade Composer images and provider packages through a tested change process.
9. Delete the environment and separately decide what to do with its retained bucket and logs.

### 3.3 Version pinning and provider packages

The Google provider is distributed as `apache-airflow-providers-google`. Operator imports are versioned APIs. Composer images bundle specific Airflow and provider versions; not every parameter in the latest upstream docs necessarily exists in your image.

Before writing code, inspect the Composer image's Airflow and provider versions, and use the matching API documentation. Pin dependencies where appropriate, test in a non-production environment, and avoid upgrading Airflow/provider packages independently without checking the Composer compatibility constraints.

The runnable DAG and pytest examples below use Airflow 2-compatible imports. **Composer 3 is a Composer generation, not a promise that every Airflow 2 import works unchanged on Airflow 3.** For the exact sample, choose a currently supported Composer 3 image containing a compatible Airflow 2 release; if you choose Airflow 3, migrate core operator imports to the appropriate standard provider and rerun import/structure tests against that image before deployment.

The examples below use these standard imports:

```python
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.operators.bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.providers.google.cloud.operators.dataflow import DataflowTemplatedJobStartOperator
```

`DataprocSubmitJobOperator` remains the compatibility name specified in this roadmap; newer provider versions may document `ManagedSparkSubmitJobOperator` as the preferred alias. Verify the exact import and arguments supported by the target Composer image.

### 3.4 Composer 2 versus Composer 3

Do not memorize a single configuration as universal.

- **Scaling:** supported worker, scheduler, triggerer, and environment resource controls vary by generation and image. Composer 3 exposes workload configuration differently from Composer 2.
- **Networking:** private networking, IP ranges, egress, and Google API access must be designed for the generation and organizational topology.
- **Dependencies:** PyPI installation can require network access or a private package repository. Private environments may need Artifact Registry, a proxy, or another approved package source.
- **Upgrades:** use supported image versions and test DAG parsing, provider imports, task behavior, and Python dependencies before promotion.
- **Costs:** environment resources continue to exist outside task execution. Idle time is not free.

Use an explicit, currently supported image version in Terraform rather than a floating alias for production. The version string in the lab is a placeholder that must be replaced with a currently supported Composer 3 image.

---

## 4. Google Cloud operators and sensors

### 4.1 `GCSToBigQueryOperator`

Loads Cloud Storage objects into a BigQuery table. It is suitable for a GCS → BigQuery batch ingestion task and exposes parameters for source bucket/object(s), destination table, schema/autodetect, write disposition, create disposition, and related options.

Important design points:

- Use an explicit schema in production where possible.
- Set `source_objects` and destination table deterministically for the logical data interval.
- Choose `WRITE_APPEND`, `WRITE_TRUNCATE`, or `WRITE_EMPTY` deliberately.
- For retry safety, prefer a staging destination for a logical date, with a deterministic write disposition and a validation/promotion step.
- A wildcard object path can match multiple files; confirm the expected files are complete before loading.
- The operator's exact argument names and supported features depend on the installed Google provider version.

### 4.2 `BigQueryInsertJobOperator`

Submits BigQuery jobs, including Standard SQL queries and scripts. Use it for transformations, `MERGE`, and SQL assertions.

```python
transform = BigQueryInsertJobOperator(
    task_id="transform",
    configuration={
        "query": {
            "query": "SELECT 1",
            "useLegacySql": False,
        }
    },
    location="US",
)
```

This is a minimal shape example. For production, parameterize SQL and use a deterministic job identifier when appropriate. A repeated query is safe only if its data effects are safe: an `INSERT` can duplicate rows, whereas a carefully designed `MERGE` or partition replacement can be idempotent.

### 4.3 `DataprocSubmitJobOperator`

Submits a job to an existing Dataproc cluster; keep Spark execution on Dataproc, not inside the Airflow worker. The provider now documents `ManagedSparkSubmitJobOperator` as the preferred alias in newer versions, while `DataprocSubmitJobOperator` remains the roadmap's compatibility name. Confirm the installed provider's import and deferrable support.

```python
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator

submit_spark = DataprocSubmitJobOperator(
    task_id="submit_spark",
    project_id="YOUR_PROJECT_ID",
    region="us-central1",
    job={
        "placement": {"cluster_name": "YOUR_EXISTING_CLUSTER"},
        "pyspark_job": {
            "main_python_file_uri": "gs://YOUR_BUCKET/jobs/transform.py",
            "args": ["--run-date", "{{ ds }}"],
        },
    },
    gcp_conn_id="google_cloud_default",
    deferrable=True,  # Remove if unsupported by the target provider/image.
)
```

The cluster, job file, and service-account permissions must already exist. Prefer Dataproc Serverless for Spark if managing a persistent cluster is not justified; this operator example intentionally illustrates the cluster-backed API.

### 4.4 `DataflowTemplatedJobStartOperator`

Starts a Dataflow job from a **classic template**. Flex Templates use `DataflowStartFlexTemplateOperator` in provider versions that support it; do not pass a Flex Template spec to the classic-template operator.

```python
from airflow.providers.google.cloud.operators.dataflow import DataflowTemplatedJobStartOperator

start_dataflow = DataflowTemplatedJobStartOperator(
    task_id="start_classic_dataflow_template",
    project_id="YOUR_PROJECT_ID",
    location="us-central1",
    template="gs://dataflow-templates/latest/Word_Count",
    job_name="word-count-{{ ds_nodash }}",
    parameters={
        "inputFile": "gs://YOUR_BUCKET/input.txt",
        "output": "gs://YOUR_BUCKET/output/word-count",
    },
    gcp_conn_id="google_cloud_default",
    deferrable=True,  # Confirm provider support and remote-job wait semantics.
)
```

Use a real classic template and its documented parameters. The example's input/output paths are placeholders; a production pipeline must use a run-specific output path or an idempotent sink. For long-running jobs, use deferrable behavior where supported and monitor the remote job state.

### 4.5 Sensors and deferrable operators

A GCS object sensor can wait for a file. A synchronous sensor in poke mode can occupy a worker slot while waiting; reschedule or deferrable modes can reduce worker occupation where supported. Deferrable tasks require a working triggerer and compatible operator implementation.

Choose sensor mode based on the environment's provider and Airflow version. Set a finite timeout, polling interval, and a clear failure message. Do not use a sensor as the only proof that a multi-file batch is complete: use a manifest, expected file count, completion marker, or upstream contract when appropriate.

### 4.6 Authentication: connections and service accounts

On Google Cloud, use Application Default Credentials / the environment's attached service account or supported impersonation. Use the standard `google_cloud_default` connection where appropriate, and configure it to use keyless credentials rather than uploading a service-account JSON key. A connection is configuration; it does not grant IAM permissions by itself.

Grant the Composer environment's service account only the permissions needed for the workflow: read the source bucket, create BigQuery jobs, access staging/target datasets, submit/monitor Dataflow or Dataproc jobs, write logs, and access Secret Manager only where required. Use a separate service account for the workflow execution identity if the design calls for impersonation and the required IAM grants are in place.

---

## 5. Retries, idempotency, scheduling, and backfills

### 5.1 Retries and timeouts

Use retries for transient failures such as temporary service unavailability, rate limiting, and network timeouts. Do not blindly retry schema errors, invalid SQL, missing input, or permission denials. Use exponential backoff and a finite retry count.

Set:
- `retries`
- `retry_delay` and optionally exponential backoff
- `execution_timeout` for a maximum task duration
- sensor `timeout`
- DAG `max_active_runs`
- task-level `pool` / `pool_slots` where shared capacity needs protection
- environment-level worker concurrency consistent with the workload

A task timeout does not necessarily cancel every remote operation unless the operator's cancellation semantics support it. Check remote job state after a timeout and design a recovery path.

### 5.2 Use the logical date

Airflow templates use Jinja syntax. `{{ ds }}` renders the logical date as `YYYY-MM-DD`; `{{ data_interval_start }}` and `{{ data_interval_end }}` provide interval boundaries in supported Airflow versions.

For a daily pipeline, build input/output paths from the logical date rather than the current clock. This lets a retry or historical backfill process the same data interval.

### 5.3 Safe load-and-transform pattern

1. Wait for a known input object or manifest for the logical date.
2. Load the file into a date-scoped staging table with deterministic write behavior.
3. Transform into a curated partition using a `MERGE` or partition replacement strategy.
4. Validate uniqueness, row counts, required fields, and business constraints.
5. Notify downstream consumers only after validation passes.
6. Retain enough run metadata to reproduce and diagnose a failed interval.

Never assume Airflow's task state and the remote service's state are transactionally coupled. A remote job can finish while the Airflow worker loses connectivity. Design for reconciliation.

### 5.4 Backfill and catchup

Backfills can create many runs and stress BigQuery quotas, API quotas, external sources, and downstream jobs. Before enabling catchup or launching a backfill:

- Estimate the interval count and expected compute/cost.
- Use date-parameterized tasks and idempotent output writes.
- Limit concurrent DAG runs and use pools for expensive resources.
- Verify historical source availability and schema compatibility.
- Decide how to handle a missing interval and whether to fail, skip, or mark it incomplete.
- Alert on partial success and record which intervals were completed.
- Do not reuse a single staging table across concurrent logical dates.

### 5.5 Failure notifications

Use `on_failure_callback` for task-level alert integration or a dedicated notification task with a carefully selected trigger rule. A callback should send small incident metadata, not secrets or entire payloads. Avoid assuming a notification task will run after every possible DAG-level failure; test failure modes and configure notifications at the appropriate task/DAG layer.

For production, integrate with the team's approved incident system or a notification endpoint protected by IAM. The lab logs a clear failure record; it does not claim that a real email/SMS channel is configured.

---

## 6. Workflows architecture and syntax

### 6.1 What Workflows is

Google Cloud Workflows is a serverless workflow orchestrator. A workflow definition is YAML or JSON describing ordered steps, API calls, branches, loops, subworkflows, error handling, and retries. It is well suited to a relatively lightweight API chain.

Workflows can call Google Cloud APIs using OAuth2 as the workflow's service account, and can call Cloud Run services with OIDC when appropriate. Authentication must be explicitly configured for HTTP calls; HTTP requests do not automatically contain credentials.

Workflows is not an Airflow DAG engine. It does not provide the same scheduler ecosystem, task-instance model, broad provider-operator catalog, and data-engineering DAG UI as Composer.

### 6.2 Simple workflow chain

The following example calls BigQuery's REST API to run a SQL statement and then returns the job metadata. Replace the project, dataset, and table identifiers. It demonstrates a small chain, not a full substitute for the Composer DAG.

`workflow.yaml`:

```yaml
main:
  params: [input]
  steps:
    - initialize:
        assign:
          - project_id: ${input.project_id}
          - location: ${input.location}
          - query: ${input.query}
    - run_query:
        call: http.post
        args:
          url: ${"https://bigquery.googleapis.com/bigquery/v2/projects/" + project_id + "/jobs"}
          auth:
            type: OAuth2
            scopes: "https://www.googleapis.com/auth/cloud-platform"
          headers:
            Content-Type: application/json
          body:
            jobReference:
              projectId: ${project_id}
              location: ${location}
            configuration:
              query:
                query: ${query}
                useLegacySql: false
        result: query_job
    - return_result:
        return:
          project_id: ${project_id}
          location: ${location}
          job: ${query_job.body.jobReference}
```

The workflow above submits a BigQuery job; the API response may indicate that the job was accepted, not that the query has finished successfully. A production workflow must poll `jobs.get` until `DONE`, inspect `status.errorResult`, and only then mark the transformation successful. The next example includes a bounded poll loop.

### 6.3 Workflows chain with polling and failure checks

`workflow.yaml`:

```yaml
main:
  params: [input]
  steps:
    - initialize:
        assign:
          - project_id: ${input.project_id}
          - location: ${input.location}
          - query: ${input.query}
          # A unique execution ID keeps scheduled invocations from reusing
          # one BigQuery job ID. It is stable throughout this workflow execution.
          - execution_id: ${sys.get_env("GOOGLE_CLOUD_WORKFLOW_EXECUTION_ID")}
          - job_id: ${"orchestrated_" + execution_id}
          - poll_count: 0
    - submit_query:
        call: http.post
        args:
          url: ${"https://bigquery.googleapis.com/bigquery/v2/projects/" + project_id + "/jobs"}
          auth:
            type: OAuth2
            scopes: "https://www.googleapis.com/auth/cloud-platform"
          headers:
            Content-Type: application/json
          body:
            jobReference:
              projectId: ${project_id}
              jobId: ${job_id}
              location: ${location}
            configuration:
              query:
                query: ${query}
                useLegacySql: false
        result: submitted
    - wait_before_poll:
        call: sys.sleep
        args:
          seconds: 5
    - poll_job:
        call: http.get
        args:
          url: ${"https://bigquery.googleapis.com/bigquery/v2/projects/" + project_id + "/jobs/" + job_id}
          auth:
            type: OAuth2
            scopes: "https://www.googleapis.com/auth/cloud-platform"
          query:
            location: ${location}
        result: job_status
    - check_job:
        switch:
          - condition: ${job_status.body.status.state == "DONE" and "errorResult" in job_status.body.status}
            raise: ${json.encode_to_string(job_status.body.status.errorResult)}
          - condition: ${job_status.body.status.state == "DONE"}
            next: done
          - condition: ${poll_count >= 120}
            raise: "Timed out waiting for BigQuery job"
          - condition: true
            next: increment_poll
    - increment_poll:
        assign:
          - poll_count: ${poll_count + 1}
        next: wait_before_poll
    - done:
        return:
          job_id: ${job_id}
          status: ${job_status.body.status.state}
```

The workflow runtime and expression language are strict: validate the exact definition with `gcloud workflows deploy` in a lab project and test it with a harmless query. The workflow execution ID is used to construct a BigQuery job ID that is unique per execution and stable inside that execution; the generated ID must still meet BigQuery's job-ID character and length rules. If an execution is manually started again, it receives a new execution ID, so SQL side effects must remain idempotent. Do not accept arbitrary SQL from untrusted callers. The polling loop is bounded; choose a timeout consistent with the workload and Workflows execution limits.

### 6.4 Error handling and retry policy

Workflows supports `try`/`except` and retry policies. Retry only operations that are safe to repeat or whose API provides a reliable idempotency key. Do not wrap a non-idempotent `INSERT` or an external side effect in a generic retry policy without an idempotency strategy.

For HTTP calls, use the documented retry predicate and exponential backoff that fits the target API's transient error behavior. Log the execution ID and task/job IDs, not secret values.

### 6.5 Deploy and execute Workflows

```bash
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="us-central1"
export WORKFLOW="bq-transform-lab"
export WORKFLOW_SA="YOUR_WORKFLOW_RUNTIME_SERVICE_ACCOUNT"

gcloud config set project "${PROJECT_ID}"
gcloud services enable workflows.googleapis.com workflowexecutions.googleapis.com
gcloud workflows deploy "${WORKFLOW}" \
  --location="${REGION}" \
  --source="workflow.yaml" \
  --service-account="${WORKFLOW_SA}"

gcloud workflows execute "${WORKFLOW}" \
  --location="${REGION}" \
  --data='{"project_id":"YOUR_PROJECT_ID","location":"US","query":"SELECT 1 AS ok"}'

gcloud workflows executions list "${WORKFLOW}" --location="${REGION}"
```

The workflow service account needs permission to submit and read the BigQuery job. The principal deploying the workflow needs permission to deploy it and attach the selected service account. Do not grant project Owner/Editor just to complete the lab.

---

## 7. Triggering workflows with Cloud Scheduler and Eventarc

### 7.1 Cloud Scheduler

Use Cloud Scheduler when a workflow should start on a cron schedule, such as daily at 02:00 in a chosen time zone. Scheduler sends an authenticated request to the Workflows Executions API. The Scheduler service account needs `roles/workflows.invoker` on the workflow or appropriate project scope, and the deploying identity must be able to attach the service account.

Example:

```bash
export SCHEDULER_SA="YOUR_SCHEDULER_SERVICE_ACCOUNT"
export SCHEDULER_JOB="daily-bq-transform"
export SCHEDULE="0 2 * * *"
export TIME_ZONE="Asia/Kolkata"

gcloud services enable cloudscheduler.googleapis.com

gcloud scheduler jobs create http "${SCHEDULER_JOB}" \
  --location="${REGION}" \
  --schedule="${SCHEDULE}" \
  --time-zone="${TIME_ZONE}" \
  --uri="https://workflowexecutions.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/workflows/${WORKFLOW}/executions" \
  --http-method=POST \
  --update-headers="Content-Type=application/json" \
  --message-body="{\"argument\":\"{\\\"project_id\\\":\\\"${PROJECT_ID}\\\",\\\"location\\\":\\\"US\\\",\\\"query\\\":\\\"SELECT 1 AS ok\\\"}\"}" \
  --oauth-service-account="${SCHEDULER_SA}" \
  --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform"
```

The Workflows Executions API is a Google API; use the documented OAuth access-token option for Google API targets. The message body above is illustrative and runs a harmless query. The workflow constructs a unique BigQuery job ID from its own execution ID, so a recurring Scheduler job does not reuse a hard-coded job ID. Replace the query with a trusted, logical-date-aware, idempotent workload before scheduling. Verify shell quoting and the installed `gcloud scheduler jobs create http --help` flags, then test one manual trigger before enabling a recurring schedule. A cron schedule can trigger overlapping executions unless you design a lock/idempotency policy.

### 7.2 Eventarc

Use Eventarc when an event such as an object creation or an audit-log event should trigger a workflow. Eventarc delivers a CloudEvent to the workflow execution as a runtime argument. Validate the event filters and payload schema, and ensure the workflow is idempotent because event-triggered systems may retry delivery.

A GCS object-created event is not necessarily proof that every file in a batch has arrived. For multi-file batches, use a manifest/completion marker or a downstream completeness check.

Illustrative Cloud Storage finalize trigger (use a dedicated trigger identity with `roles/workflows.invoker` on the workflow, and choose an Eventarc location supported by the source and destination):

```bash
export EVENTARC_SA="YOUR_EVENTARC_TRIGGER_SERVICE_ACCOUNT"

gcloud services enable eventarc.googleapis.com pubsub.googleapis.com

gcloud eventarc triggers create gcs-finalize-to-workflow \
  --location="${REGION}" \
  --destination-workflow="${WORKFLOW}" \
  --destination-workflow-location="${REGION}" \
  --event-filters="type=google.cloud.storage.object.v1.finalized" \
  --event-filters="bucket=${BUCKET}" \
  --service-account="${EVENTARC_SA}"
```

Check the exact event type, bucket filter, location compatibility, required service-agent permissions, and trigger identity in the current Eventarc documentation before applying. The workflow must accept the CloudEvent JSON as its runtime argument (or explicitly extract the needed event fields); the BigQuery example above expects a different input shape, so adapt its `main` input handling before connecting this trigger. Do not connect a raw GCS event to a workflow that assumes `project_id`, `location`, and `query` fields without mapping and validating the event first.

### 7.3 Cloud Scheduler versus Eventarc

- **Scheduler:** time-based trigger.
- **Eventarc:** event-based trigger.
- **Composer schedule:** appropriate when the work is already a DAG and Airflow should manage its timetable, catchup, dependencies, retries, and run history.

Avoid scheduling the same logical pipeline from both Composer and Scheduler unless you intentionally handle duplicate/concurrent runs.

---

## 8. Composer versus Workflows versus alternative approaches

| Option | Best fit | Strengths | Trade-offs |
|---|---|---|---|
| **Cloud Composer / Airflow** | Multi-step data DAGs with dependencies, backfills, sensors, complex schedules, provider operators, and rich task-level history | Mature DAG model, broad integrations, retry/task state, ecosystem | Environment has ongoing cost and operational lifecycle; Python/provider compatibility needs management |
| **Workflows** | Lightweight API orchestration, service-to-service calls, branching, HTTP/API integration | Serverless execution, simple deployment, IAM-based API calls, no Airflow environment to operate | Less suitable for broad data DAGs with many sensors/backfills and Airflow-style task observability |
| **Cloud Scheduler + Cloud Run Jobs** | A scheduled container job or small independent task with no complex DAG | Simple cron + container execution; useful for one bounded job | Dependencies, backfills, and multi-step state must be implemented elsewhere |
| **Eventarc + Workflows/Cloud Run** | Event-driven API chain or reaction to cloud events | Event-based activation and decoupled components | Must design idempotency, event filtering, retry and dead-letter/incident handling |
| **Dagster / Prefect** | Teams preferring their asset/orchestration model or deployment ecosystem | Strong developer ergonomics and asset/task abstractions depending on product | Adds another platform and operating model; GCP integration, hosting, governance, and cost need evaluation |

Decision questions:

1. Are there many dependent tasks, sensors, backfills, and per-task operational history? Start with Composer.
2. Is the job mostly a small sequence of authenticated Google Cloud API calls? Consider Workflows.
3. Is there one containerized task on a cron schedule? Consider Scheduler + Cloud Run Jobs.
4. Is the trigger a cloud event? Consider Eventarc.
5. Does the organization already operate Dagster or Prefect effectively? Avoid adding a second orchestrator without a clear benefit.

No option eliminates the need for idempotency, data-quality checks, alerting, or ownership.

---

## 9. CI/CD, testing, monitoring, and incident response

### 9.1 Local testing first

A local environment can test Python syntax, DAG imports, dependency imports, task IDs, dependency edges, and business logic. It cannot prove that the DAG will run inside a particular Composer image or that cloud IAM/networking is correct.

Use a virtual environment and install compatible Airflow/provider packages for your chosen version. Do not casually install the newest Airflow and newest provider and assume they match Composer. The easiest safe approach is to run tests using the same constraints/provider versions as the target environment.

Recommended checks:

- `python -m compileall dags`
- `pytest`
- `ruff check dags tests`
- DAG import test
- DAG task graph assertions
- Workflows deployment validation in a non-production project
- integration test using a small, isolated dataset and one test object

### 9.2 CI/CD pipeline

A practical release path:

1. Format/lint and static-check DAG and workflow files.
2. Run unit tests and DAG import/structure tests.
3. Validate Terraform formatting and plan.
4. Deploy to a dev Composer environment and run a smoke test.
5. Verify output rows, uniqueness, logs, and alerts.
6. Promote the same versioned artifact to staging/production after approval.
7. Use a controlled rollback path and record the deployed commit/image/provider versions.

Do not let CI jobs upload arbitrary DAGs to production without review. Treat DAG code as production code: it can invoke APIs and use the environment's service-account permissions.

### 9.3 Monitoring and SLOs

Monitor at least:

- DAG run success rate and task failure rate.
- End-to-end pipeline duration and time since last successful run.
- Schedule delay and data freshness (for example, latest completed partition).
- Sensor wait duration and missing-input count.
- BigQuery job state, bytes processed, and data-quality failures.
- Dataproc/Dataflow remote job state and runtime.
- Composer scheduler/worker health, queued tasks, parse/import errors, and environment resource pressure.
- Alert delivery success and incident acknowledgment.

Define an SLO such as “the daily curated partition is validated by 07:00 local time on at least 99% of scheduled days over a rolling period.” The threshold is a business decision; do not copy an arbitrary percentage without an owner. A task success alone is not a freshness SLO if the task processed an empty or stale input. Distinguish a business SLA/SLO from Airflow's built-in SLA APIs: those APIs differ by Airflow major version and may not be available in every Composer image. Prefer a version-appropriate mechanism plus Cloud Monitoring alerts for freshness and duration, and confirm the selected image's support before adding an Airflow `sla` argument or callback.

### 9.4 Failure callbacks and alerts

Use failure callbacks or a notification task to send concise context: DAG ID, task ID, logical date, run ID, error summary, log link, and affected data interval. Redact credentials and sensitive row contents. Test the callback itself; notification failure must not silently mask the original task failure.

For incidents, preserve the run metadata and logs, stop uncontrolled retries if they amplify cost or duplicate writes, repair the cause, then rerun the affected logical interval. Record whether the repair was code, data, IAM, quota, or infrastructure-related.

---

## 10. Security, networking, secrets, and cost management

### 10.1 Service accounts and least privilege

Separate identities where practical:

- **Deployer/CI identity:** creates infrastructure and deploys DAG/workflow code.
- **Composer environment service account:** runs DAG tasks and calls required services.
- **Workflows runtime service account:** calls only the APIs required by its workflow.
- **Scheduler trigger identity:** invokes the Workflows execution API.
- **Eventarc trigger identity:** invokes the target according to the trigger configuration.

Grant `roles/composer.worker` to a custom Composer environment service account as required by the service, then add only the additional permissions its DAGs need. Workflows needs its runtime permissions separately from the identity that invokes it. Do not use downloaded service-account key files.

### 10.2 Connections and Secret Manager

Prefer attached service-account credentials and IAM. Store actual secrets in Secret Manager and grant access only to the identity that needs them. Airflow Connections can store non-secret connection settings and can use Composer's supported Secret Manager backend; avoid copying secret values into DAG source, ordinary environment variables, source control, task logs, or XCom.

For Composer 2/3, configure the backend through **Airflow configuration overrides** (not by setting reserved `AIRFLOW__...` environment variables):

| Airflow section/key | Example value |
| --- | --- |
| `secrets.backend` | `airflow.providers.google.cloud.secrets.secret_manager.CloudSecretManagerBackend` |
| `secrets.backend_kwargs` | `{"project_id":"YOUR_PROJECT_ID","connections_prefix":"airflow-connections","variables_prefix":"airflow-variables","sep":"-"}` |

Grant the environment service account `roles/secretmanager.secretAccessor` on only the required secrets (or a suitably scoped project if necessary). With the default prefixes, a connection named `orders_api` is stored as `airflow-connections-orders_api`; a variable named `orders_dataset` is stored as `airflow-variables-orders_dataset`. Store connection values in the documented URL-encoded URI format. Secrets fetched from Secret Manager may not be visible in the Airflow UI, so validate access through a controlled task without logging the secret value.

Environment variables are useful for non-secret runtime configuration. Example update (values are illustrative; quote and escape them appropriately):

```bash
gcloud composer environments update "${ENVIRONMENT_NAME}" \
  --location="${REGION}" \
  --update-env-variables="PIPELINE_MODE=lab,LOG_LEVEL=INFO"
```

Install only required, trusted, pinned PyPI dependencies compatible with the selected Composer image and provider set. Composer environment updates can take time and affect a shared environment; validate first in dev. Example using a reviewed requirements file:

```bash
gcloud composer environments update "${ENVIRONMENT_NAME}" \
  --location="${REGION}" \
  --update-pypi-packages-from-file="requirements-composer.txt"
```

For restricted networking/VPC Service Controls, use an approved private package repository or Artifact Registry path rather than assuming public PyPI is reachable. Do not use PyPI package installation as a substitute for version/compatibility testing.

### 10.3 Private IP and networking

A private Composer environment needs deliberate network and egress design. Verify the chosen Composer generation's networking requirements, IP ranges, Private Google Access/API routing, DNS, firewall rules, and package repository access. Private IP alone does not guarantee access to every Google API or package index.

For restricted environments, use an approved Artifact Registry/private PyPI source or controlled egress path. Test API access from the actual environment, not only from a developer laptop.

### 10.4 Package management and upgrades

Keep dependency sets small. Every additional package increases resolver conflicts, deployment time, and supply-chain exposure. Pin packages compatible with the Composer image, test provider upgrades, and avoid runtime installation of arbitrary packages from public internet in production. Keep a change record for image upgrades and Airflow/provider version changes.

### 10.5 Cost controls

- Composer environments run continuously and incur ongoing charges even when no DAG is active.
- Start with the smallest supported environment configuration that meets scheduler/worker needs, and scale based on queue depth, parsing latency, task runtime, and memory/CPU signals.
- Use deferrable operators/sensors when supported to free worker capacity while waiting.
- Avoid excessive DAG parsing, very high polling frequency, unbounded retries, and unnecessary backfills.
- Use pools and concurrency limits to protect BigQuery quotas and downstream services.
- Consider Workflows or Scheduler + Cloud Run Jobs for a small API chain or single task where a Composer environment would be disproportionate.
- Set budget alerts and inspect billing reports; alerts do not automatically stop spending.
- Deleting the Composer environment does **not** automatically delete its GCS environment bucket or Cloud Logging logs. Review and clean those separately only after preserving needed artifacts.

---

## 11. Hands-on exercises

### 11.1 Lab layout

Create this directory:

```text
experiments/08_composer/
├── README.md
├── dags/
│   └── gcs_to_bigquery_daily.py
├── tests/
│   └── test_dag.py
├── workflow.yaml
├── requirements-test.txt
├── terraform/
│   ├── versions.tf
│   ├── variables.tf
│   └── main.tf
└── observations.md
```

The lab DAG implements: GCS object detection → BigQuery load to staging → SQL transformation/MERGE → data-quality assertions → success metadata. A failure callback logs diagnostic context; connect it to an approved notification system for a real alert.

### 11.2 DAG source: `dags/gcs_to_bigquery_daily.py`

```python
"""Daily GCS -> BigQuery orchestration example.

Expected object:
  gs://<source_bucket>/incoming/orders/ds=YYYY-MM-DD/orders.jsonl

This example uses a date-scoped staging table and an idempotent MERGE.
The source is JSONL with event_id, customer_id, event_ts, amount_usd.
"""
from __future__ import annotations

import logging
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.trigger_rule import TriggerRule


PROJECT_ID = "{{ var.value.gcp_project_id }}"
BQ_LOCATION = "{{ var.value.bigquery_location }}"
SOURCE_BUCKET = "{{ var.value.orders_source_bucket }}"
DATASET = "{{ var.value.orders_dataset }}"
SOURCE_OBJECT = "incoming/orders/ds={{ ds }}/orders.jsonl"
STAGING_TABLE = "orders_stage_{{ ds_nodash }}"
TARGET_TABLE = "orders_curated"


def log_failure(context: dict) -> None:
    """Emit incident metadata; connect this to a real notifier if required."""
    ti = context.get("task_instance")
    logging.error(
        "COMPOSER_DAG_FAILURE dag_id=%s task_id=%s run_id=%s logical_date=%s",
        getattr(ti, "dag_id", None),
        getattr(ti, "task_id", None),
        context.get("run_id"),
        context.get("logical_date"),
    )


with DAG(
    dag_id="gcs_to_bigquery_daily",
    description="Detect GCS input, load staging, merge, validate",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule="0 3 * * *",
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "data-platform",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "execution_timeout": timedelta(minutes=45),
        "on_failure_callback": log_failure,
    },
    tags=["learning", "bigquery", "gcs"],
) as dag:
    start = EmptyOperator(task_id="start")

    wait_for_input = GCSObjectExistenceSensor(
        task_id="wait_for_input",
        bucket=SOURCE_BUCKET,
        object=SOURCE_OBJECT,
        google_cloud_conn_id="google_cloud_default",
        mode="reschedule",
        poke_interval=60,
        timeout=60 * 60,
        execution_timeout=timedelta(minutes=65),
        retries=0,  # The sensor already waits up to an hour; avoid 3 repeated hour-long waits.
    )

    load_to_staging = GCSToBigQueryOperator(
        task_id="load_to_staging",
        bucket=SOURCE_BUCKET,
        source_objects=[SOURCE_OBJECT],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET}.{STAGING_TABLE}",
        source_format="NEWLINE_DELIMITED_JSON",
        autodetect=False,
        schema_fields=[
            {"name": "event_id", "type": "STRING", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "STRING", "mode": "NULLABLE"},
            {"name": "event_ts", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "amount_usd", "type": "FLOAT", "mode": "NULLABLE"},
        ],
        create_disposition="CREATE_IF_NEEDED",
        write_disposition="WRITE_TRUNCATE",
        location=BQ_LOCATION,
        gcp_conn_id="google_cloud_default",
        # Keep the default unique job ID behavior for each execution attempt.
        # Retry safety comes from WRITE_TRUNCATE and date-scoped staging, not job-ID reuse.
        force_rerun=True,
    )

    merge_curated = BigQueryInsertJobOperator(
        task_id="merge_curated",
        location=BQ_LOCATION,
        gcp_conn_id="google_cloud_default",
        configuration={
            "query": {
                "useLegacySql": False,
                "query": f"""
                MERGE `{PROJECT_ID}.{DATASET}.{TARGET_TABLE}` AS T
                USING (
                  SELECT event_id, customer_id, event_ts, amount_usd
                  FROM `{PROJECT_ID}.{DATASET}.{STAGING_TABLE}`
                  QUALIFY ROW_NUMBER() OVER (
                    PARTITION BY event_id
                    ORDER BY event_ts DESC, customer_id DESC, amount_usd DESC
                  ) = 1
                ) AS S
                ON T.event_id = S.event_id
                WHEN MATCHED AND (
                  T.customer_id IS DISTINCT FROM S.customer_id OR
                  T.event_ts IS DISTINCT FROM S.event_ts OR
                  T.amount_usd IS DISTINCT FROM S.amount_usd
                ) THEN UPDATE SET
                  customer_id = S.customer_id,
                  event_ts = S.event_ts,
                  amount_usd = S.amount_usd,
                  updated_at = CURRENT_TIMESTAMP()
                WHEN NOT MATCHED THEN INSERT (
                  event_id, customer_id, event_ts, amount_usd, updated_at
                ) VALUES (
                  S.event_id, S.customer_id, S.event_ts, S.amount_usd,
                  CURRENT_TIMESTAMP()
                )
                """,
            }
        },
        # A fresh job ID is safe because the MERGE is designed to be idempotent.
        force_rerun=True,
        deferrable=True,
    )

    quality_check = BigQueryInsertJobOperator(
        task_id="quality_check",
        location=BQ_LOCATION,
        gcp_conn_id="google_cloud_default",
        configuration={
            "query": {
                "useLegacySql": False,
                "query": f"""
                ASSERT (
                  SELECT COUNT(*) = 0
                  FROM (
                    SELECT event_id
                    FROM `{PROJECT_ID}.{DATASET}.{TARGET_TABLE}`
                    GROUP BY event_id
                    HAVING COUNT(*) > 1
                  )
                ) AS 'duplicate event_id values in curated target';

                ASSERT (
                  SELECT COUNT(*) = 0
                  FROM `{PROJECT_ID}.{DATASET}.{TARGET_TABLE}`
                  WHERE event_id IS NULL OR amount_usd < 0
                ) AS 'invalid curated rows';
                """,
            }
        },
        # A fresh job ID is safe because the MERGE is designed to be idempotent.
        force_rerun=True,
        deferrable=True,
    )

    cleanup_staging = BigQueryInsertJobOperator(
        task_id="cleanup_staging",
        location=BQ_LOCATION,
        gcp_conn_id="google_cloud_default",
        configuration={
            "query": {
                "useLegacySql": False,
                "query": f"DROP TABLE IF EXISTS `{PROJECT_ID}.{DATASET}.{STAGING_TABLE}`",
            }
        },
        force_rerun=True,
        deferrable=True,
    )

    finish = EmptyOperator(task_id="finish")

    # A failed quality check preserves staging for diagnosis; successful runs clean it up.
    start >> wait_for_input >> load_to_staging >> merge_curated >> quality_check >> cleanup_staging >> finish
```

#### Important DAG notes

- Airflow Variables are used for non-secret environment configuration. Create `gcp_project_id`, `bigquery_location`, `orders_source_bucket`, and `orders_dataset` in the environment or supply them through your approved configuration mechanism.
- The DAG explicitly uses `force_rerun=True` for BigQuery operators and does not force reuse of a completed BigQuery job ID across manual reruns of the same logical date. This means a retry can submit a fresh remote job; safety therefore depends on the date-scoped staging table with `WRITE_TRUNCATE`, the deduplicated `MERGE`, and validation being idempotent. Confirm the `force_rerun` parameter exists in the selected provider version. Never assume a deterministic job ID makes every manual rerun succeed: provider reattachment semantics vary, and a completed job may be treated differently from a running job.
- BigQuery table identifiers are interpolated into SQL from Airflow Variables. Keep these values admin-controlled, validate them, and do not let untrusted DAG run inputs choose arbitrary identifiers.
- The target table must exist before the DAG runs. Create it with a schema compatible with the MERGE:

```sql
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT_ID.YOUR_DATASET.orders_curated` (
  event_id STRING NOT NULL,
  customer_id STRING,
  event_ts TIMESTAMP,
  amount_usd FLOAT64,
  updated_at TIMESTAMP
)
CLUSTER BY customer_id;
```

- The `ASSERT` statements run as a BigQuery script. Validate syntax and permissions in a small test dataset before production.
- `catchup=False` prevents automatic creation of historical scheduled runs for this example. A deliberate backfill procedure is still required for missed dates.
- The DAG waits for one deterministic object. If a date has multiple files, use a manifest/completion marker or a sensor/completeness check instead.
- The `log_failure` callback writes a stable `COMPOSER_DAG_FAILURE` marker to task logs; it is not, by itself, a real email or paging integration. For the lab's alert requirement, create a Cloud Logging log-based alert (or a log-based metric plus Cloud Monitoring alert policy) that matches this marker in the Composer environment's logs, route it to a test notification channel, and verify a deliberate failure reaches that channel. Check the actual log resource/labels in Logs Explorer before saving the filter.

### 11.3 Local DAG tests: `tests/test_dag.py`

```python
from __future__ import annotations

from pathlib import Path

from airflow.models import DagBag


DAG_FILE = (
    Path(__file__).resolve().parents[1]
    / "dags"
    / "gcs_to_bigquery_daily.py"
)


def test_dag_imports_without_errors():
    dag_bag = DagBag(dag_folder=str(DAG_FILE.parent), include_examples=False)
    assert dag_bag.import_errors == {}
    assert "gcs_to_bigquery_daily" in dag_bag.dags


def test_expected_tasks_and_dependencies():
    dag_bag = DagBag(dag_folder=str(DAG_FILE.parent), include_examples=False)
    dag = dag_bag.get_dag("gcs_to_bigquery_daily")
    assert dag is not None

    expected = {
        "start",
        "wait_for_input",
        "load_to_staging",
        "merge_curated",
        "quality_check",
        "cleanup_staging",
        "finish",
    }
    assert set(dag.task_ids) == expected

    assert dag.get_task("start").downstream_task_ids == {"wait_for_input"}
    assert dag.get_task("wait_for_input").downstream_task_ids == {"load_to_staging"}
    assert dag.get_task("load_to_staging").downstream_task_ids == {"merge_curated"}
    assert dag.get_task("merge_curated").downstream_task_ids == {"quality_check"}
    assert dag.get_task("quality_check").downstream_task_ids == {"cleanup_staging"}
    assert dag.get_task("cleanup_staging").downstream_task_ids == {"finish"}


def test_dag_has_no_catchup_and_limits_active_runs():
    dag_bag = DagBag(dag_folder=str(DAG_FILE.parent), include_examples=False)
    dag = dag_bag.get_dag("gcs_to_bigquery_daily")
    assert dag is not None
    assert dag.catchup is False
    assert dag.max_active_runs == 1
```

The test file intentionally imports only `Path` and `DagBag`; it does not contact Google Cloud.

`requirements-test.txt`:

```text
pytest
ruff
# Install Airflow and the Google provider using versions/constraints
# compatible with the selected Composer image, not arbitrary latest versions.
```

Example local commands, in a Python environment containing compatible Airflow/provider packages:

```bash
python -m compileall dags tests
ruff check dags tests
pytest -q
```

If the Airflow/provider packages are not installed locally, the DAG import tests will fail at import time; that is an environment limitation, not a successful test. Prefer a reproducible test environment with the target-compatible constraints. Do not use `pip install apache-airflow` without an appropriate constraints file.

### 11.4 Terraform deployment plan

The following Terraform provisions a Composer environment and grants the existing environment service account the required `roles/composer.worker` role. It does not create the service account, grant the DAG access to BigQuery/GCS, create datasets, or upload DAG code. Add narrowly scoped workflow-specific IAM bindings separately; do not give the environment service account broad project roles just to make the lab work.

`terraform/versions.tf`:

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 7.0, < 9.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
```

`terraform/variables.tf`:

```hcl
variable "project_id" {
  type        = string
  description = "Dedicated lab project ID"
}

variable "region" {
  type        = string
  description = "Supported Composer region"
  default     = "us-central1"
}

variable "environment_name" {
  type        = string
  description = "Globally unique within project/region"
  default     = "composer-orchestration-lab"
}

variable "composer_service_account" {
  type        = string
  description = "Existing environment service-account email"
}

variable "composer_image_version" {
  type        = string
  description = "Exact currently supported Composer 3 image version"
}
```

`terraform/main.tf`:

```hcl
resource "google_project_service" "composer_api" {
  project            = var.project_id
  service            = "composer.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_iam_member" "composer_worker" {
  project = var.project_id
  role    = "roles/composer.worker"
  member  = "serviceAccount:${var.composer_service_account}"
}

resource "google_composer_environment" "lab" {
  name   = var.environment_name
  region = var.region

  config {
    software_config {
      # Pin an exact version. Replace the variable value with a version
      # currently supported in this region and compatible with your DAG.
      image_version = var.composer_image_version
    }

    # Composer 3 workload controls: start small, then tune from queue depth,
    # scheduler latency, worker utilization, and task memory/CPU measurements.
    # This block is Composer 3-specific; use the Composer 2 schema if targeting Gen 2.
    environment_size = "ENVIRONMENT_SIZE_SMALL"
    workloads_config {
      scheduler {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
        count      = 1
      }
      triggerer {
        cpu        = 0.5
        memory_gb  = 1
        count      = 1
      }
      dag_processor {
        cpu        = 1
        memory_gb  = 2
        storage_gb = 1
        count      = 1
      }
      web_server {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
      }
      worker {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
        min_count  = 1
        max_count  = 3
      }
    }

    node_config {
      service_account = var.composer_service_account
    }
  }

  labels = {
    purpose = "learning"
    module  = "topic-08"
  }

  depends_on = [
    google_project_service.composer_api,
    google_project_iam_member.composer_worker,
  ]
}

output "composer_environment_name" {
  value = google_composer_environment.lab.name
}
```

The exact Terraform schema and available options depend on the Google provider and Composer generation. The workload block above is for Composer 3 and illustrates a small environment with worker autoscaling from one to three workers; remove/replace it when targeting Composer 2 and validate its different supported scaling/networking fields. Validate the chosen image and schema with the current Terraform Registry and Composer documentation before applying.

Deployment sequence:

```bash
cd experiments/08_composer/terraform
terraform init
terraform fmt -check
terraform validate
terraform plan \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="composer_service_account=YOUR_COMPOSER_SERVICE_ACCOUNT" \
  -var="composer_image_version=YOUR_EXACT_SUPPORTED_COMPOSER_3_IMAGE"
terraform apply \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="composer_service_account=YOUR_COMPOSER_SERVICE_ACCOUNT" \
  -var="composer_image_version=YOUR_EXACT_SUPPORTED_COMPOSER_3_IMAGE"
```

Creating an environment is slow and billable. Confirm the plan and budget before applying. If the environment is private, add the generation-specific network configuration, private IP range, API access, and package-source configuration based on your organization's network design.

### 11.5 Enable APIs and prepare data

```bash
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="us-central1"
export BUCKET="YOUR_UNIQUE_BUCKET"
export DATASET="orchestration_lab"

gcloud config set project "${PROJECT_ID}"
gcloud services enable \
  composer.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  workflows.googleapis.com \
  workflowexecutions.googleapis.com \
  cloudscheduler.googleapis.com \
  eventarc.googleapis.com \
  pubsub.googleapis.com \
  secretmanager.googleapis.com \
  dataproc.googleapis.com \
  dataflow.googleapis.com \
  logging.googleapis.com

gcloud storage buckets create "gs://${BUCKET}" \
  --location="${REGION}" \
  --uniform-bucket-level-access

bq --location=US mk --dataset "${PROJECT_ID}:${DATASET}"
```

Use a BigQuery dataset location consistent with the location configured in the DAG. The example uses a GCS source bucket and an Airflow Variable for its name. Upload a test object at the expected path and create the target table before running the DAG.

### 11.6 Upload DAG code

After the environment is created, get its details and DAGs bucket:

```bash
gcloud composer environments describe YOUR_ENVIRONMENT_NAME \
  --location="${REGION}" \
  --format="yaml(config.dagGcsPrefix,config.softwareConfig.imageVersion)"
```

Upload the DAG to the returned DAGs prefix:

```bash
gcloud storage cp dags/gcs_to_bigquery_daily.py \
  "gs://YOUR_COMPOSER_DAGS_BUCKET/dags/gcs_to_bigquery_daily.py"
```

Use the exact DAGs bucket/prefix reported by the environment. In some Composer setups the reported prefix already ends in `/dags`; inspect it before adding another `dags` segment. Wait for parsing, then check import errors in the UI/logs.

Create the Airflow Variables used by the DAG using the Airflow UI or the environment's supported mechanism:

- `gcp_project_id`
- `bigquery_location` (for example `US` when the dataset is in US multi-region)
- `orders_source_bucket`
- `orders_dataset`

Do not store secrets in these variables.

### 11.7 Failure and recovery exercises

Perform these only in the lab:

1. **Missing object:** leave the expected GCS object absent. Confirm the sensor times out, the load does not run, and the task failure is visible.
2. **Bad schema:** upload JSON with an incompatible field/type. Confirm the load fails and the curated target is not incorrectly promoted.
3. **Duplicate event IDs:** include duplicate source rows. Confirm the MERGE source deduplicates them and the quality assertion passes.
4. **Permission denial:** remove one lab-only permission in a controlled test or use a separate identity without access. Confirm the failure is diagnosable and restore the permission immediately.
5. **Retry:** force a transient failure and verify that rerunning the date does not create duplicate target keys.
6. **Backfill:** manually run one historical logical date with a matching input object and verify the partition/output. Do not enable broad catchup without estimating the run count.
7. **Alert path:** intentionally fail a task and verify the callback log. If you configure an external notification, verify delivery and protect the endpoint with IAM.
8. **Alert path:** trigger a controlled failure and confirm the Cloud Logging/Monitoring alert reaches a test notification channel; the callback log alone is not delivery verification.
9. **Workflow chain:** deploy `workflow.yaml`, execute a harmless `SELECT 1`, inspect execution logs, then run a bounded test query against the lab dataset.

### 11.8 Equivalent Workflows chain

Use the `workflow.yaml` source in Section 6. It demonstrates BigQuery job submission and bounded polling. For a true production equivalent, add:
- A GCS object metadata check or manifest check using the Cloud Storage API.
- A load job or API call that uses a deterministic job ID / destination.
- A transform `MERGE`.
- A quality query whose result is checked before returning success.
- Explicit exception handling, retry rules, and a failure notification or incident endpoint.

Do not claim the minimal Workflows chain is feature-equivalent to the Composer DAG: it lacks Airflow's task graph, sensor modes, built-in backfill model, and rich per-task history.

### 11.9 Compare implementation effort and cost

Record evidence in `observations.md`:

| Dimension | Composer DAG | Workflows chain |
|---|---|---|
| Setup / deployment effort | | |
| Lines of orchestration code | | |
| Dependencies and packages | | |
| Scheduling / backfill effort | | |
| Retry and failure visibility | | |
| IAM configuration effort | | |
| Operational maintenance | | |
| End-to-end duration | | |
| Actual billable services and cost | | |
| Best-fit workload | | |

Compare only equivalent behavior and include environment lifecycle costs. Do not compare a running Composer environment's monthly cost with one Workflows execution while omitting the workload, logging, storage, or Scheduler costs. Record actual billing data after it becomes available; if it cannot be isolated, say so.

### 11.10 Cleanup

Before deleting anything, inspect the Terraform plan/state, environment name, bucket, dataset, workflow, and Scheduler job. Export DAGs/logs if they are needed for learning or audit.

Delete the Composer environment through Terraform:

```bash
cd experiments/08_composer/terraform
terraform destroy \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="composer_service_account=YOUR_COMPOSER_SERVICE_ACCOUNT" \
  -var="composer_image_version=YOUR_EXACT_SUPPORTED_COMPOSER_3_IMAGE"
```

Composer does not automatically delete its environment bucket or Cloud Logging logs. Inspect the bucket name reported by the environment and delete it only if it is dedicated to this lab and its contents have been preserved or are no longer needed.

Delete the Scheduler job if created:

```bash
gcloud scheduler jobs delete daily-bq-transform --location="${REGION}"
```

Delete the Workflows resource if created:

```bash
gcloud workflows delete bq-transform-lab --location="${REGION}"
```

Delete lab staging tables and dataset only after verifying they contain no needed data. Do not delete a shared bucket, dataset, project, API, or service account as a generic cleanup step. Confirm that the Composer environment, Scheduler job, workflow, lab data, and billable resources have been removed or intentionally retained.

---

## 12. Troubleshooting and common mistakes

| Symptom | Likely cause | Investigation / response |
|---|---|---|
| DAG absent from UI | Wrong bucket/prefix, parsing delay, import error | Check `dagGcsPrefix`, DAG processor logs, and import errors |
| DAG import failure | Provider import mismatch, missing package, syntax error | Match Composer image/provider versions; run local import tests with compatible dependencies |
| `403` on GCS or BigQuery | Environment service account lacks permissions or perimeter blocks request | Inspect the exact API and resource; grant least privilege and check network perimeter |
| GCS sensor waits indefinitely | Wrong object key, wrong bucket, wrong logical date, object not complete | Inspect rendered template and input contract; set timeout and completion-marker policy |
| Load duplicates data | Append retry, reused target, non-idempotent write | Use date-scoped staging, deterministic write disposition, stable keys and `MERGE` |
| BigQuery job accepted but workflow reports success too early | Workflow did not poll the job to `DONE` | Poll `jobs.get`, inspect `status.errorResult`, and enforce a deadline |
| Remote job continues after Airflow task times out | Operator timeout/cancel behavior does not stop remote job | Inspect remote job state, cancel explicitly if safe, and reconcile outputs |
| Too many tasks queued | Worker/concurrency limits, pool saturation, scheduler pressure | Inspect queue, pools, DAG parsing, worker scaling, and downstream quotas |
| Composer package install fails | Incompatible dependency or no package-index access | Use pinned compatible packages and approved private repository/egress |
| Backfill causes cost spike | Too many historical runs or concurrent jobs | Pause/limit backfill, use pools/max active runs, estimate query and remote-job costs |
| Failure alert absent | Callback not configured, callback itself failed, wrong IAM/endpoint | Inspect callback logs and test alert path independently |
| Terraform environment create fails late | Unsupported image/config, IP range or service-account permissions | Validate Composer-generation-specific config and current supported image list |
| Environment deleted but bill persists | DAGs bucket, logs, dataset, or other resources remain | Inspect Composer environment bucket and billing resources; delete only confirmed lab-owned resources |

Common mistakes:

- Running heavy Spark, Dataflow, or data transformation code inside an Airflow worker instead of submitting a remote job.
- Hard-coding credentials or committing service-account key files.
- Treating retries as exactly-once execution.
- Using wall-clock `now()` for historical partition selection.
- Enabling catchup without planning for backfills and concurrency.
- Leaving Composer running idle after a lab.
- Installing unpinned packages that conflict with the managed Airflow image.
- Assuming Workflows and Composer are interchangeable.
- Assuming an API submission response means the remote job finished successfully.
- Deleting the environment but forgetting its bucket and logs.

---

## 13. Knowledge checks with detailed answers

### Questions

1. What is the difference between orchestration and processing?
2. Why is Composer more than a cron scheduler?
3. What is the role of the DAGs bucket?
4. What does `{{ ds }}` represent, and why is it useful?
5. Why can a task retry duplicate data even if Airflow retries only after a failure?
6. When should a deferrable sensor/operator be used?
7. What is the difference between `GCSToBigQueryOperator` and `BigQueryInsertJobOperator`?
8. When would you use `DataprocSubmitJobOperator` or `DataflowTemplatedJobStartOperator`?
9. Why should Workflows poll a BigQuery job after submitting it?
10. How should Cloud Scheduler authenticate when triggering Workflows?
11. What should be checked before installing a PyPI package in Composer?
12. What are the main risks of a historical backfill?
13. How does Composer differ from Workflows?
14. What does deleting a Composer environment not automatically remove?
15. What should an orchestration SLO measure?
16. Why are service-account key files discouraged?
17. When is Cloud Scheduler plus Cloud Run Jobs a reasonable alternative?
18. Why is a GCS object sensor not always sufficient for a multi-file batch?

### Answers

1. Orchestration manages sequence, scheduling, dependencies, retries, state, and alerts; processing executes the actual data transformation or computation.
2. Composer provides DAG dependencies, task instances, schedules, sensors, retries, backfills, pools, task history, and a provider ecosystem.
3. It stores DAG code and related environment artifacts. Uploading code does not guarantee successful parsing or execution.
4. It is the logical date rendered as `YYYY-MM-DD` in supported Airflow templates. It allows repeatable date-based paths and historical runs independent of wall-clock execution time.
5. The remote operation may have succeeded while the worker lost its response or the scheduler did not record success. A retry can execute the side effect again; idempotent writes and reconciliation are required.
6. For long waits or remote jobs when the operator and environment support deferrable execution. It can free worker capacity while a triggerer monitors completion.
7. `GCSToBigQueryOperator` loads GCS objects into a table. `BigQueryInsertJobOperator` submits general BigQuery jobs such as SQL queries, scripts, or other supported job configurations.
8. Use Dataproc submission for Spark/Hadoop jobs and Dataflow template operators for Dataflow template jobs. Keep compute in those services and monitor their remote lifecycle.
9. Job submission can return before execution finishes. Poll until `DONE`, check error status, and only then mark the orchestration step successful.
10. Use a dedicated Scheduler service account with the documented permission to invoke workflow executions; configure the supported OAuth/OIDC mechanism for the target API and verify with a test.
11. Check the Composer image, Airflow version, provider constraints, Python compatibility, network/package-index access, dependency resolution, and whether the package is actually needed.
12. High concurrency, quota exhaustion, duplicate effects, unavailable historical inputs, schema drift, long runtimes, and unexpected cost.
13. Composer is an Airflow environment for task DAGs, sensors, backfills, and detailed task history. Workflows is serverless API/workflow orchestration with a simpler step-oriented model.
14. The environment's Cloud Storage bucket and Cloud Logging logs may remain; inspect and remove them separately if safe.
15. Measure successful completion and data freshness against an agreed deadline, including data-quality gates—not only whether tasks ended in a success state.
16. Key files are long-lived credentials that can be copied or leaked. Attached service accounts and IAM provide controlled identity without distributing private keys.
17. For one bounded containerized job on a cron schedule where a full DAG scheduler is unnecessary.
18. A single object can arrive before other files in the batch. Use a manifest, completion marker, expected count, or upstream contract to establish completeness.

---

## 14. Syllabus checkpoint

Mark an item complete only after you can explain or demonstrate it.

- [ ] Explain Composer as managed Airflow, environment components, DAGs bucket, and UI.
- [ ] Use `BigQueryInsertJobOperator`, `GCSToBigQueryOperator`, `DataprocSubmitJobOperator`, and `DataflowTemplatedJobStartOperator` with compatible provider versions.
- [ ] Use service accounts and connections without downloaded key files.
- [ ] Explain Composer 2/3 differences, scaling, networking, and continuous environment costs.
- [ ] Use sensors and deferrable operators where supported.
- [ ] Build date-parameterized, idempotent tasks with safe retries and controlled backfills.
- [ ] Use Workflows YAML to call Google Cloud APIs and poll remote jobs.
- [ ] Trigger Workflows with Scheduler and explain Eventarc.
- [ ] Choose Composer, Workflows, Scheduler + Cloud Run Jobs, or another orchestrator with a reasoned trade-off.
- [ ] Test DAG imports and dependencies with pytest and linting.
- [ ] Deploy with Terraform and a controlled CI/CD process.
- [ ] Define monitoring, failure callbacks, and a data-freshness SLO.
- [ ] Explain IAM, secrets, private networking, package management, and cleanup.
- [ ] Record actual effort/cost observations and clearly label anything not measured.

**Exit criterion:** a local DAG import/structure test passes; a controlled cloud run performs GCS detection → BigQuery load → transform → quality validation; a Workflows chain is deployed and tested; and all lab resources are deleted or intentionally retained with their costs understood. If cloud execution is unavailable, mark it **not performed**, not passed.

---

## 15. Summary and transition to Topic 09

Cloud Composer is the stronger default for multi-step data pipelines that need DAG dependencies, sensors, backfills, task-level retries, and detailed operational history. Workflows is a good fit for lightweight API orchestration where a full Airflow environment would add unnecessary operational burden. Cloud Scheduler supplies time-based triggers; Eventarc supplies event-based triggers; Cloud Run Jobs is useful for bounded containerized processing.

Keep the responsibilities clear:

- Composer/Workflows: orchestration, control flow, retries, and visibility.
- BigQuery: warehouse SQL and data quality queries.
- Dataflow: Beam batch/stream processing.
- Dataproc: Spark/Hadoop processing.
- Cloud Run Jobs: containerized tasks when appropriate.

Topic 09 — Dataplex, IAM, and governance — adds governance and data-quality controls across the services orchestrated here. Continue to apply least privilege, data contracts, auditable deployment, and explicit cost ownership.

---

## 16. Official documentation references

Use current documentation for the selected Composer generation, image, Airflow version, provider package, and Terraform provider.

1. [Cloud Composer / Managed Airflow overview](https://cloud.google.com/composer/docs/composer-3/composer-overview)
2. [Create Managed Airflow environments](https://cloud.google.com/composer/docs/composer-3/create-environments)
3. [Create Composer environments with Terraform](https://cloud.google.com/composer/docs/composer-3/terraform-create-environments)
4. [Install Python dependencies in Composer 3](https://cloud.google.com/composer/docs/composer-3/install-python-dependencies)
5. [Delete Managed Airflow environments](https://cloud.google.com/composer/docs/composer-3/delete-environments)
6. [Monitor Composer environment health and performance](https://cloud.google.com/composer/docs/composer-3/monitor-key-metrics)
7. [Terraform `google_composer_environment` resource](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/composer_environment)
8. [Google Airflow provider: BigQuery operators](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/operators/cloud/bigquery.html)
9. [Google Airflow provider: Dataproc operators](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/operators/cloud/dataproc.html)
10. [Google Airflow provider: Dataflow operators](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/operators/cloud/dataflow.html)
11. [Workflows syntax overview](https://cloud.google.com/workflows/docs/reference/syntax)
12. [Create and deploy Workflows using gcloud](https://cloud.google.com/workflows/docs/create-workflow-gcloud)
13. [Authenticated requests from Workflows](https://cloud.google.com/workflows/docs/authenticate-from-workflow)
14. [Workflows retry syntax](https://cloud.google.com/workflows/docs/reference/syntax/retrying)
15. [Schedule Workflows with Cloud Scheduler](https://cloud.google.com/workflows/docs/schedule-workflow)
16. [Trigger Workflows with Eventarc](https://cloud.google.com/workflows/docs/trigger-workflow-eventarc)
17. [Cloud Scheduler HTTP authentication](https://cloud.google.com/scheduler/docs/http-target-auth)
18. [Cloud Composer pricing](https://cloud.google.com/composer/pricing)
19. [Workflows pricing](https://cloud.google.com/workflows/pricing)
20. [Cloud Scheduler pricing](https://cloud.google.com/scheduler/pricing)
21. [Cloud Composer Secret Manager backend](https://cloud.google.com/composer/docs/composer-3/configure-secret-manager)
22. [Cloud Composer environment variables](https://cloud.google.com/composer/docs/composer-3/set-environment-variables)
23. [Cloud Composer PyPI dependency installation](https://cloud.google.com/composer/docs/composer-3/install-python-dependencies)
24. [Eventarc trigger CLI reference](https://cloud.google.com/sdk/gcloud/reference/eventarc/triggers/create)
25. [Workflows built-in environment variables](https://cloud.google.com/workflows/docs/reference/environment-variables)
26. [Google provider BigQuery operator API reference](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/_api/airflow/providers/google/cloud/operators/bigquery/index.html)

---

## Verification and execution status

This lesson was aligned to Topic 08 in `roadmap-Google-Cloud-BigQuery-and-GCP-Data-Engineering.md` and the module position in `Roadmap_ptree.md`. The re-audit includes explicit examples for all four named Google provider operators, Composer 2/3 considerations, Terraform IAM/environment provisioning, DAG source and pytest structure tests, Workflows YAML with bounded BigQuery polling, Scheduler/Eventarc trigger patterns, Secret Manager/PyPI/environment configuration, failure alerting, cost, cleanup, and dependencies on Topics 04, 06, 07 and Topic 09. Code and provider behavior remain version-sensitive and must be checked against the selected Composer image.

**Execution status:** all code and commands are instructional examples. No Composer environment was provisioned, no DAG was imported or executed in GCP, no Workflows deployment was run, and no costs were measured while preparing this lesson. Verify the exact Composer image, provider parameters, IAM, network configuration, and Terraform schema for your target environment before deployment. The workflow polling and Scheduler authentication examples require validation in a test project before production use.
