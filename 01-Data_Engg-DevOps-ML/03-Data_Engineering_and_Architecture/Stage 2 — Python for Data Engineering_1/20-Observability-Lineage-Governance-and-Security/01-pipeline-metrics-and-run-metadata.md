# 01 — Pipeline Metrics and Run Metadata

> **Module 2.20 — Observability, Lineage, Governance, and Security**
>
> This chapter teaches production data engineers how to measure, record, correlate, visualize, debug, and operate data pipelines using **metrics, unified run metadata, and structured logs**.

---

## 1. Module Overview

### What this module teaches

A production data pipeline does more than move rows from one system to another. Engineers must be able to answer:

- Is the pipeline healthy right now?
- Is it getting slower?
- Is it producing the expected amount of data?
- Is the data fresh enough for consumers?
- What exactly happened during one execution?
- Which code and container version produced that run?
- Where did a failed run stop?
- Can an engineer move from a dashboard symptom to a specific `run_id` and then to the relevant structured logs?

This topic establishes the observability foundation for Module 2.20. OpenTelemetry tracing is deliberately treated as the **next topic**; here the deep focus is on metrics, run metadata, and structured logs.

### Why it matters

A pipeline can report `SUCCESS` while the data product is still wrong.

For example:

```text
API → Kafka → Spark → Object Storage → Warehouse → BI
```

Suppose the warehouse table contains 18% less revenue than expected. A green pipeline status alone cannot tell you whether:

- the API returned fewer records,
- Kafka stopped receiving events,
- Spark processed zero or fewer rows,
- object storage received incomplete files,
- the warehouse load dropped records,
- the pipeline ran with an unexpected code version,
- or the source itself changed.

Observability gives you the evidence needed to distinguish these cases.

### Metrics vs run metadata

A useful mental model is:

> **Metrics tell you what is happening across executions. Run metadata tells you what happened during one execution. Logs explain the detailed events around that execution.**

Analogy:

> Metrics are the dashboard of a factory; run metadata is the detailed production record for one batch.

### Learning objectives

By the end of this module, you should be able to:

- Explain observability, monitoring, debugging, telemetry, and operational visibility.
- Distinguish metrics, logs, and traces.
- Choose counters, gauges, histograms, and summaries appropriately.
- Instrument Python pipelines with `prometheus-client`.
- Understand Prometheus scraping, time series, labels, targets, exporters, and basic PromQL.
- Design operational metrics for batch and streaming pipelines.
- Design a unified `run_metadata` model.
- Design useful `run_id` values without pretending there is one universal format.
- Emit structured JSON logs correlated by `run_id`.
- Use Python `contextvars` to avoid manually passing correlation state through every function.
- Derive useful SLIs and define SLOs.
- Apply RED and USE appropriately.
- Avoid dangerous metric cardinality.
- Build operational Grafana dashboards.
- Treat dashboards as code.
- Connect application-level observability with Airflow, Spark, Kafka, and warehouse metrics.
- Test instrumentation itself.
- Simulate failures and debug them systematically.
- Make production observability decisions with scale, security, cost, and maintainability in mind.

### Prerequisites

This module assumes familiarity with:

- Python and application logging.
- Processes, networking, and permissions.
- `contextvars`, async/concurrency concepts.
- Pipeline run tables and pipeline state.
- Data freshness and quality concepts.
- Airflow or another orchestrator.
- Spark fundamentals.
- Kafka fundamentals.
- Cloud storage and warehouse concepts.
- CI/CD and testing.

---

# 2. Observability Fundamentals

## 2.1 What is observability?

**Observability** is the ability to understand the internal state and behavior of a system from the information it emits.

For a data platform, that means being able to reason about:

```text
source
  ↓
ingestion
  ↓
processing
  ↓
storage
  ↓
warehouse
  ↓
consumer
```

and answer questions about health, latency, volume, freshness, failures, and impact.

### Monitoring vs observability

| Concept | Practical meaning |
|---|---|
| Monitoring | Watching known signals and checking whether they cross known conditions |
| Observability | Having enough structured evidence to investigate unknown failure modes |
| Debugging | Using evidence to identify the cause of a problem |
| Telemetry | Data emitted by systems for operational understanding |
| Operational visibility | The ability of engineers to see and reason about system behavior |

Monitoring might tell you:

```text
orders_daily_failed_runs = 1
```

Observability lets you continue:

```text
Which run?
Which version?
Which stage?
How many rows?
Which input interval?
Which error?
Which downstream data was affected?
```

## 2.2 Why logs alone are insufficient

A log stream containing:

```text
Pipeline failed
Pipeline failed
Pipeline failed
...
```

is difficult to aggregate and compare.

Metrics answer questions such as:

```text
How many failures occurred?
How frequently?
Is failure rate increasing?
Is duration degrading?
```

Run metadata answers:

```text
What happened in run orders_daily:2026-10-05:production?
```

Structured logs answer:

```text
What was happening inside that run immediately before the failure?
```

## 2.3 Why pipeline observability differs from application observability

Traditional applications often emphasize:

- request rate,
- error rate,
- request latency,
- resource utilization.

Data systems additionally need:

- freshness,
- rows and bytes,
- completeness,
- quarantine volume,
- consumer lag,
- data intervals,
- processing windows,
- source-to-output relationships,
- data quality signals,
- cost per run.

A successful process is not necessarily a successful data product.

### Checkpoint

Before continuing, answer:

1. What is the difference between monitoring and observability?
2. Why are logs alone insufficient?
3. Why does a data pipeline need freshness and volume signals?

**Answers**

1. Monitoring checks known signals; observability provides evidence for investigating system state, including unknown failure modes.
2. Logs are detailed but difficult to aggregate into operational trends and objectives.
3. Consumers care whether data is available, complete, and fresh—not merely whether a process exited successfully.

---

# 3. The Three Core Observability Signals

| Signal | Primary question | Example |
|---|---|---|
| Metrics | What is happening? | `10,000` rows processed |
| Logs | What happened? | `MERGE completed` |
| Traces | Where did time go? | API call took `4s` |

This module focuses deeply on **metrics and logs**. Topic 02 covers OpenTelemetry tracing.

### When to use each

Use **metrics** for:

- trends,
- rates,
- counts,
- latency distributions,
- dashboards,
- SLO calculations,
- alerts.

Use **structured logs** for:

- detailed events,
- failures,
- diagnostic context,
- individual execution evidence,
- correlation through `run_id`.

Use **traces** for:

- distributed request/path timing,
- cross-service causality,
- identifying where time is spent.

---

# 4. Metric Types

## 4.1 Counter

A **counter** represents a value that monotonically increases, except that the underlying process may restart and the time series may reset.

Good examples:

```text
pipeline_runs_total
pipeline_failures_total
rows_processed_total
rows_quarantined_total
```

Do not use a counter for a value that naturally goes up and down, such as current queue depth.

### Python

```python
from prometheus_client import Counter

pipeline_runs = Counter(
    "pipeline_runs_total",
    "Total number of pipeline executions",
    ["pipeline", "environment"],
)

pipeline_failures = Counter(
    "pipeline_failures_total",
    "Total number of failed pipeline executions",
    ["pipeline", "environment"],
)

pipeline_runs.labels(
    pipeline="orders_daily",
    environment="prod",
).inc()
```

### How to reason about a counter

Ask:

> Is this measuring an event that happened?

If yes, a counter is often appropriate.

Examples:

```text
run completed
record rejected
file processed
message consumed
load failed
```

## 4.2 Gauge

A **gauge** represents a current value that can move up and down.

Examples:

```text
pipeline_lag_seconds
records_in_flight
queue_depth
active_pipeline_runs
```

```python
from prometheus_client import Gauge

queue_depth = Gauge(
    "pipeline_queue_depth",
    "Current number of records waiting for processing",
    ["pipeline", "environment"],
)

queue_depth.labels(
    pipeline="orders_stream",
    environment="prod",
).set(1250)
```

Use gauges for state:

```text
current lag
current queue
current active workers
current temperature
current freshness
```

## 4.3 Histogram

A histogram records observations into configurable buckets and is especially useful for distributions such as latency.

```python
from prometheus_client import Histogram

run_duration = Histogram(
    "pipeline_run_duration_seconds",
    "Pipeline execution duration in seconds",
    ["pipeline", "environment"],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800),
)

with run_duration.labels(
    pipeline="orders_daily",
    environment="prod",
).time():
    run_pipeline()
```

### Why not only use averages?

Suppose ten runs have durations:

```text
8, 8, 8, 8, 8, 8, 8, 8, 8, 108 minutes
```

The average is about `18` minutes, but the distribution contains a severe outlier.

Latency distributions help answer:

- What is typical?
- How often are runs very slow?
- Is the tail degrading?
- Are SLOs being met?

## 4.4 Summary

A **summary** records observations and may expose quantile estimates depending on the client implementation.

Conceptually:

```text
Histogram:
  observations → buckets → aggregatable distribution

Summary:
  observations → client-side quantile calculations
```

Histograms are often preferable for infrastructure-style monitoring because bucketed distributions can be aggregated across dimensions.

Do not choose a summary simply because "p95" sounds useful. Consider whether the measurement needs aggregation across instances or workers.

### Checkpoint

1. Which metric type represents completed events?
2. Which represents current queue depth?
3. Which is commonly useful for run-duration distributions?
4. Why can a histogram be more useful than a single average?

**Answers:** counter, gauge, histogram, and because distributions reveal tails and outliers that averages hide.

---

# 5. Prometheus Fundamentals

Prometheus is a metrics collection and time-series monitoring system.

A simplified architecture is:

```text
Python Pipeline
      ↓
prometheus-client
      ↓
 /metrics endpoint
      ↓
Prometheus
      ↓
   PromQL
      ↓
 Grafana
```

## 5.1 Pull/scrape model

A typical Prometheus setup periodically **scrapes** an HTTP endpoint exposed by a target.

Example:

```text
GET /metrics
```

The target exposes current metric samples, and Prometheus stores them as time series.

## 5.2 Time series

A time series is identified by a metric name plus its label set.

Conceptually:

```text
pipeline_runs_total{
    pipeline="orders_daily",
    environment="prod"
}
```

is different from:

```text
pipeline_runs_total{
    pipeline="customers_daily",
    environment="prod"
}
```

The label values define separate series.

## 5.3 Targets and exporters

A **target** is something Prometheus scrapes.

An **exporter** exposes metrics from a system that does not natively expose Prometheus metrics in the desired format.

Examples include exporters or integrations for infrastructure and platform components.

## 5.4 Minimal Prometheus configuration

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "data-pipeline"
    static_configs:
      - targets:
          - "pipeline:8000"
```

The pipeline must expose:

```text
http://pipeline:8000/metrics
```

## 5.5 PromQL basics

A raw metric:

```promql
pipeline_runs_total
```

A rate:

```promql
rate(pipeline_failures_total[5m])
```

A sum across pipelines:

```promql
sum(rate(pipeline_runs_total[5m]))
```

A filtered series:

```promql
pipeline_runs_total{
  pipeline="orders_daily",
  environment="prod"
}
```

### Checkpoint

Explain:

- What is a target?
- What is scraping?
- What is a time series?
- Why do labels matter?

---

# 6. Prometheus Client in Python

Install the client:

```bash
uv add prometheus-client
```

A practical pipeline has stages:

```text
extract()
   ↓
transform()
   ↓
load()
```

We can instrument execution without turning every function into a metrics framework.

```python
from __future__ import annotations

import time
from prometheus_client import Counter, Gauge, Histogram, start_http_server

PIPELINE = "orders_daily"
ENVIRONMENT = "prod"

runs_total = Counter(
    "pipeline_runs_total",
    "Total pipeline runs",
    ["pipeline", "environment"],
)

success_total = Counter(
    "pipeline_success_total",
    "Successful pipeline runs",
    ["pipeline", "environment"],
)

failure_total = Counter(
    "pipeline_failure_total",
    "Failed pipeline runs",
    ["pipeline", "environment"],
)

rows_processed_total = Counter(
    "pipeline_rows_processed_total",
    "Rows processed",
    ["pipeline", "environment"],
)

rows_quarantined_total = Counter(
    "pipeline_rows_quarantined_total",
    "Rows quarantined",
    ["pipeline", "environment"],
)

run_duration_seconds = Histogram(
    "pipeline_run_duration_seconds",
    "Pipeline execution duration",
    ["pipeline", "environment"],
)

freshness_seconds = Gauge(
    "pipeline_freshness_seconds",
    "Current data freshness in seconds",
    ["pipeline", "environment"],
)


def extract() -> list[dict]:
    return [
        {"order_id": 1, "amount": 100},
        {"order_id": 2, "amount": 200},
    ]


def transform(rows: list[dict]) -> tuple[list[dict], int]:
    valid = [row for row in rows if row["amount"] >= 0]
    quarantined = len(rows) - len(valid)
    return valid, quarantined


def load(rows: list[dict]) -> None:
    # Replace with the real warehouse/object-storage load.
    print(f"loading {len(rows)} rows")


def run_pipeline() -> None:
    runs_total.labels(PIPELINE, ENVIRONMENT).inc()
    started = time.perf_counter()

    try:
        rows = extract()
        transformed, quarantined = transform(rows)

        rows_processed_total.labels(PIPELINE, ENVIRONMENT).inc(len(transformed))
        rows_quarantined_total.labels(PIPELINE, ENVIRONMENT).inc(quarantined)

        load(transformed)

        success_total.labels(PIPELINE, ENVIRONMENT).inc()

    except Exception:
        failure_total.labels(PIPELINE, ENVIRONMENT).inc()
        raise

    finally:
        run_duration_seconds.labels(
            PIPELINE,
            ENVIRONMENT,
        ).observe(time.perf_counter() - started)


if __name__ == "__main__":
    start_http_server(8000)
    run_pipeline()
```

### Production reasoning

The example is deliberately small, but the important production pattern is:

```text
event counters
+
state gauges
+
duration distributions
+
bounded labels
```

Do not create one metric per customer, order, or run.

---

# 7. Metrics for Data Pipelines

Pipeline metrics should answer operational questions rather than merely provide technical telemetry.

## 7.1 Run metrics

| Metric | What it measures | Why it matters | Abnormal behavior | Engineer action |
|---|---|---|---|---|
| Run duration | Execution time | Detect regressions | Duration rising | Compare recent runs and versions |
| Success count | Completed runs | Reliability | Drop in successes | Inspect failures |
| Failure count | Failed runs | Reliability | Spike | Investigate failure pattern |
| Retry count | Recovery attempts | Stability | Retries increasing | Find underlying transient/permanent issue |
| Run frequency | Execution cadence | Scheduling health | Missing runs | Check orchestrator/scheduler |

## 7.2 Data-volume metrics

Track:

```text
rows_read
rows_written
bytes_read
bytes_written
```

These can expose:

- missing source data,
- accidental filtering,
- unexpected joins,
- duplicate expansion,
- schema/source changes.

A pipeline that normally reads 12 million rows and suddenly reads 2,000 deserves investigation even if it returns `SUCCESS`.

## 7.3 Data-quality and exception metrics

Track where appropriate:

```text
rows_quarantined
rejected_records
invalid_records
duplicate_records
```

These connect observability with the quality systems built earlier in the roadmap.

## 7.4 Freshness

A useful definition is:

```text
freshness = current_time - latest_data_timestamp
```

For example:

```text
latest_data_timestamp = 06:42
current_time           = 07:05

freshness = 23 minutes
```

Consumers may care more about this than whether a job process completed.

## 7.5 Streaming metrics

For streaming systems, include:

- consumer lag,
- queue depth,
- throughput,
- processing delay,
- partition activity.

A healthy consumer process can still be badly behind.

## 7.6 Infrastructure and cost signals

Where available, observe:

- queue time,
- resource utilization,
- warehouse queue time,
- bytes processed,
- compute consumption,
- cost per run.

Cost should be treated as an operational signal, not merely a finance report.

### Practical metric-design rule

For every metric ask:

1. What does it measure?
2. Why does it matter?
3. How will it be instrumented?
4. What does abnormal behavior look like?
5. What action should an engineer take?

---

# 8. Batch Metrics vs Run Metadata

This is one of the most important distinctions in the module.

## Metrics

Metrics aggregate behavior across time and executions.

```text
pipeline_runs_total = 15,342
```

This is useful for:

- trend analysis,
- rates,
- dashboards,
- SLOs,
- alerts.

## Run metadata

Run metadata records one execution.

```json
{
  "run_id": "orders_daily:2026-10-05:production",
  "pipeline": "orders_daily",
  "status": "SUCCESS",
  "rows_read": 1250000,
  "rows_written": 1248200,
  "duration_seconds": 384,
  "git_sha": "abc123",
  "image_digest": "sha256:..."
}
```

It is useful for:

- execution history,
- debugging,
- reproducibility,
- auditability,
- incident investigation,
- comparing individual runs.

### Why both are required

Metrics can tell you:

```text
orders_daily became slower this week.
```

Run metadata can tell you:

```text
The slowdown began after git SHA abc123
and only affected the 2026-10-05 run,
which read 3x the normal volume.
```

---

# 9. Unified Run Metadata

A production `run_metadata` model consolidates the information needed to understand one execution.

## 9.1 Recommended fields

```text
run_id
pipeline
environment
status
start_time
end_time
duration
git_sha
image_digest
data_interval_start
data_interval_end
rows_read
rows_written
bytes_read
bytes_written
rows_quarantined
retry_count
error_type
cost
```

### Example PostgreSQL schema

```sql
CREATE TABLE run_metadata (
    run_id TEXT PRIMARY KEY,
    pipeline TEXT NOT NULL,
    environment TEXT NOT NULL,
    status TEXT NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    duration_seconds DOUBLE PRECISION,
    git_sha TEXT,
    image_digest TEXT,
    data_interval_start TIMESTAMPTZ,
    data_interval_end TIMESTAMPTZ,
    rows_read BIGINT,
    rows_written BIGINT,
    bytes_read BIGINT,
    bytes_written BIGINT,
    rows_quarantined BIGINT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    error_type TEXT,
    cost NUMERIC(18, 6)
);
```

## 9.2 Mandatory vs optional fields

A reasonable baseline is:

**Mandatory**

- `run_id`
- `pipeline`
- `environment`
- `status`
- `start_time`

**Strongly recommended**

- `end_time`
- `duration_seconds`
- `git_sha`
- `image_digest`
- data interval
- rows and bytes
- retry count

**Optional depending on platform**

- `error_type`
- cost
- engine-specific identifiers
- warehouse job IDs
- Spark application ID
- Airflow DAG/task identifiers

### Why code version matters

Without the code version, a historical run can become difficult to reproduce or explain.

### Why image digest matters

A Git SHA identifies source code, but the deployed artifact may also depend on:

- base image,
- Python dependencies,
- OS packages,
- configuration.

An immutable image digest provides stronger deployment evidence.

### Why the data interval matters

A daily pipeline may run at 07:00 while processing data for the previous day. Execution time and data interval are different concepts.

---

# 10. Designing `run_id`

A `run_id` identifies a specific pipeline execution.

Good properties include:

- uniqueness,
- correlation usefulness,
- stable representation,
- compatibility with the orchestrator,
- suitability for logs and run metadata.

Bad:

```text
run_1
run_2
run_3
```

These IDs may be unique but carry little operational context.

A more useful example is:

```text
orders_daily:2026-10-05:production
```

However, there is no universal format. An orchestrator may already generate an execution ID. Your application may need a separate execution identifier if one execution can contain multiple internal attempts or stages.

### Idempotency is different

Do not confuse:

```text
run_id
```

with:

```text
idempotency_key
```

A run ID identifies an execution. An idempotency key represents a logical operation for which repeated execution should not create duplicate effects.

---

# 11. Structured JSON Logging

Plain text:

```text
Pipeline failed
```

Structured logging:

```json
{
  "timestamp": "2026-10-05T07:14:32Z",
  "level": "ERROR",
  "pipeline": "orders_daily",
  "run_id": "orders_daily:2026-10-05:production",
  "stage": "load",
  "error_type": "DatabaseTimeout",
  "message": "Warehouse connection timed out"
}
```

The structured record can be:

- searched,
- filtered,
- aggregated,
- parsed by machines,
- correlated with dashboards and run metadata.

## 11.1 A practical Python logger

```python
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "pipeline"):
            payload["pipeline"] = record.pipeline

        if hasattr(record, "run_id"):
            payload["run_id"] = record.run_id

        if hasattr(record, "stage"):
            payload["stage"] = record.stage

        return json.dumps(payload)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())

logger = logging.getLogger("data_pipeline")
logger.setLevel(logging.INFO)
logger.handlers = [handler]
logger.propagate = False
```

The exact logging architecture can vary, but the principle is stable:

> Put operational context in structured fields rather than hiding it in prose.

### Security

Never place secrets, passwords, tokens, raw PII, or sensitive payloads into logs simply because the logger can serialize them.

---

# 12. `contextvars` and Run Correlation

Passing `run_id` through every function can become noisy:

```python
extract(run_id)
transform(rows, run_id)
load(rows, run_id)
validate(rows, run_id)
```

Python's `contextvars` can carry context-local state.

```python
from contextvars import ContextVar

run_id_var: ContextVar[str | None] = ContextVar(
    "run_id",
    default=None,
)
```

Set it at the pipeline boundary:

```python
token = run_id_var.set("orders_daily:2026-10-05:production")

try:
    extract()
    transform()
    load()
finally:
    run_id_var.reset(token)
```

A helper can retrieve it:

```python
def current_run_id() -> str | None:
    return run_id_var.get()
```

Then logging code can automatically include it.

### Practical model

```text
pipeline
   ↓
extract
   ↓
transform
   ↓
load
```

All functions can access the current execution context without explicitly threading the identifier through every function signature.

### Async and concurrency

`contextvars` are designed for context-local values and work well with modern Python asynchronous execution when context is propagated correctly. Threads, tasks, executors, and process boundaries still require careful design.

Do not assume context automatically crosses every distributed boundary.

This topic focuses on local application correlation. Distributed context propagation is handled more deeply in OpenTelemetry tracing.

---

# 13. Correlating Metrics, Run Metadata, and Logs

The operational model should look like:

```text
Metric
  ↓
Dashboard
  ↓
Abnormal behavior
  ↓
pipeline / dataset
  ↓
run_id
  ↓
run_metadata
  ↓
structured logs
  ↓
failure location
```

## Example incident

Grafana shows:

```text
orders_daily duration:
8 minutes → 31 minutes
```

Find the affected run:

```text
run_id =
orders_daily:2026-10-05:production
```

Run metadata:

```text
rows_read       = 12,000,000
rows_written    = 11,800,000
status          = FAILED
retry_count     = 2
git_sha         = abc123
```

Structured logs:

```json
{
  "run_id": "orders_daily:2026-10-05:production",
  "stage": "warehouse_load",
  "error_type": "DatabaseTimeout"
}
```

Now the engineer has moved from:

> "The pipeline is slow."

to:

> "This execution processed unusually high volume and ultimately timed out during warehouse loading."

That is observability enabling debugging rather than merely displaying charts.

---

# 14. SLIs

An **SLI**, or Service Level Indicator, is a measurement representing a user-relevant aspect of service behavior.

Useful data-engineering SLIs include:

- pipeline success rate,
- freshness,
- availability,
- delivery latency,
- data completeness,
- consumer-visible delay.

## Measurement vs user experience

There may be hundreds of measurements:

```text
CPU
memory
rows
bytes
tasks
partitions
queries
```

But the important question is:

> Which measurement represents what the consumer experiences?

For example:

```text
raw metric:
pipeline duration

consumer-facing SLI:
data available by 07:00
```

A pipeline can become slower without violating a consumer SLO if the data is still available on time.

---

# 15. SLOs

An **SLO**, or Service Level Objective, defines a target for an SLI.

Example:

```text
99% of daily pipelines complete before 07:00.
```

Another:

```text
95% of events become available to consumers within 5 minutes.
```

## SLI vs SLO vs SLA

| Term | Meaning |
|---|---|
| SLI | What you measure |
| SLO | Internal reliability target |
| SLA | Formal service commitment, often contractual |

An SLO is not merely an alert threshold.

It should influence:

- engineering priorities,
- reliability work,
- error budgets,
- operational decisions.

## Error budget

If the SLO is:

```text
99% successful on-time delivery
```

then the remaining 1% represents the allowed unreliability under the chosen measurement period.

The error budget helps answer:

> How much unreliability can we tolerate before reliability work must take priority?

---

# 16. RED Method

RED stands for:

- **Rate**
- **Errors**
- **Duration**

For pipelines:

```text
Rate:
pipeline runs / events processed

Errors:
failed runs / failed records

Duration:
pipeline execution latency
```

RED is useful for service-like behavior, but data systems need additional dimensions.

For example, RED alone will not tell you that:

```text
pipeline succeeded
but rows_read fell from 12M to 2K
```

Therefore combine RED with data-specific signals such as:

- freshness,
- volume,
- completeness,
- quarantine,
- lag.

---

# 17. USE Method

USE stands for:

- **Utilization**
- **Saturation**
- **Errors**

Apply it to resources such as:

- compute,
- workers,
- Kafka consumers,
- databases,
- storage,
- Spark executors.

Examples:

```text
Spark executor utilization
Kafka consumer saturation
Database connection pool saturation
Warehouse queue time
```

### RED vs USE

```text
RED → service/pipeline behavior

USE → resource behavior
```

They complement one another.

A pipeline may have high duration because:

```text
service behavior:
duration ↑

resource behavior:
database saturation ↑
```

This is more useful than observing duration alone.

---

# 18. Metric Labels and Cardinality

Labels are powerful:

```text
pipeline="orders"
dataset="orders"
environment="prod"
```

But every distinct label combination creates a separate time series.

This is **cardinality**.

### Good

```python
labels(
    pipeline="orders",
    environment="prod",
)
```

### Dangerous

```text
run_id="..."
user_id="..."
customer_id="..."
order_id="..."
request_id="..."
```

These identifiers can have enormous or effectively unbounded value sets.

### Why high cardinality is dangerous

It can increase:

- memory usage,
- storage,
- query cost,
- scrape load,
- dashboard complexity,
- operational instability.

### Rule

> **Never put unbounded identifiers into metric labels.**

Put detailed identifiers in:

- structured logs,
- run metadata,
- traces where appropriate,
- event records.

Use bounded dimensions for metrics.

---

# 19. Production Metric Design

A useful baseline:

| Metric | Type | Labels | Purpose |
|---|---|---|---|
| `pipeline_runs_total` | Counter | pipeline, env | Run volume |
| `pipeline_failures_total` | Counter | pipeline, env | Failures |
| `pipeline_duration_seconds` | Histogram | pipeline, env | Runtime distribution |
| `pipeline_rows_processed_total` | Counter | pipeline, env | Throughput |
| `pipeline_freshness_seconds` | Gauge | dataset, env | Freshness |
| `pipeline_lag_seconds` | Gauge | pipeline, env | Delay |

### Design reasoning

Notice what is absent:

```text
run_id
customer_id
order_id
user_id
```

Those belong in detailed execution evidence rather than high-volume metric dimensions.

---

# 20. Dashboard Design

A dashboard should answer operational questions.

It is not a collection of every metric available.

## 20.1 Overview

Include:

- pipeline health,
- success rate,
- failure rate,
- freshness,
- current incidents.

## 20.2 Performance

Include:

- run duration,
- throughput,
- lag.

## 20.3 Data volume

Include:

- rows read,
- rows written,
- quarantined records.

## 20.4 Reliability

Include:

- SLO compliance,
- error budget,
- failed runs.

### Operational question

A good dashboard should let an engineer answer:

> Which pipeline is unhealthy, what changed, and where should I investigate next?

---

# 21. Dashboards as Code

Manually configured dashboards are fragile.

Problems include:

- configuration drift,
- undocumented changes,
- inconsistent environments,
- difficult review,
- difficult rollback.

A repository can contain:

```text
observability/
├── dashboards/
│   └── pipeline-overview.json
├── prometheus/
│   └── prometheus.yml
└── grafana/
    └── provisioning/
```

Benefits:

- version control,
- reproducibility,
- reviewability,
- environment promotion,
- CI validation.

Treat dashboards as deployable configuration rather than one-off UI state.

---

# 22. Airflow Metrics

Airflow can provide or expose operational signals such as:

- DAG runs,
- task failures,
- task duration,
- retries,
- scheduling delay.

But orchestrator telemetry should not replace application-level instrumentation.

### Airflow can tell you

```text
DAG task failed
```

Your application/run metadata should help answer:

```text
How many rows were read?
How many were written?
What data interval was processed?
Which code version ran?
Which stage failed?
```

The two layers complement one another.

---

# 23. Spark Metrics

Spark has engine-level telemetry including:

- application execution,
- job/stage/task timing,
- input/output records,
- shuffle behavior,
- executor/resource metrics,
- application IDs,
- Spark UI information.

Distinguish:

```text
Pipeline-level metrics
```

from:

```text
Spark-engine-level metrics
```

Pipeline-level:

```text
orders_daily duration
rows read
rows written
freshness
SLO
```

Spark-level:

```text
stage duration
shuffle bytes
executor utilization
task failures
```

Run metadata can correlate them using identifiers such as:

```text
run_id
spark_application_id
```

---

# 24. Kafka Metrics

Important streaming signals include:

- consumer lag,
- throughput,
- partition activity,
- consumer health,
- processing delay.

Architecture:

```text
Kafka
  ↓
Consumer
  ↓
Processing
  ↓
Sink
```

A healthy consumer process does not necessarily mean a healthy pipeline.

For example:

```text
consumer is alive
consumer lag = 2,000,000 messages
```

The service is running, but consumers may be far behind.

Kafka operational metrics should therefore complement pipeline-level metrics and data freshness.

---

# 25. Warehouse Metrics

Useful warehouse signals include:

- query duration,
- load duration,
- rows loaded,
- rows rejected,
- bytes processed,
- load failures,
- queue time,
- cost-related measurements where available.

Connect these to pipeline run metadata.

For example:

```text
run_id
   ↓
warehouse_job_id
   ↓
load duration
bytes processed
rows loaded
query failure
```

This makes warehouse behavior part of the pipeline's execution story.

---

# 26. Complete Production Example

Consider:

```text
API
 ↓
Python ingestion
 ↓
Object Storage
 ↓
Spark transformation
 ↓
Warehouse
 ↓
BI
```

The platform emits:

```text
Prometheus metrics
+
run metadata
+
structured JSON logs
+
run_id
+
contextvars
+
Grafana dashboards
```

The correlation model is:

```text
Grafana
  ↓
orders_daily duration anomaly
  ↓
run_id
  ↓
run_metadata
  ↓
git_sha / image_digest / row counts
  ↓
structured logs
  ↓
failing stage
```

This is the foundation that Topic 02 will extend with distributed tracing.

---

# 27. Failure-Injection Lab

Failure injection is mandatory because observability that has never been exercised is only an assumption.

## Failure 1 — API becomes slow

Inject:

```python
import time

time.sleep(30)
```

Expected evidence:

- duration increases,
- extraction-stage logs show delay,
- run metadata records longer runtime,
- duration histogram changes.

## Failure 2 — Warehouse load fails

Raise:

```python
raise TimeoutError("warehouse connection timed out")
```

Expected:

- failure counter increases,
- run metadata becomes `FAILED`,
- structured error log contains `run_id`,
- the relevant stage is identifiable.

## Failure 3 — Input volume drops

Change source behavior so that:

```text
normal rows = 12,000,000
actual rows = 2,000
```

Expected:

- rows-read metric drops,
- dashboard shows anomaly,
- run metadata exposes unusual volume.

## Failure 4 — Pipeline becomes stale

Stop or delay ingestion.

Expected:

```text
freshness_seconds ↑
consumer-facing SLI ↓
```

## Failure 5 — Metric cardinality explodes

Temporarily introduce:

```python
bad_metric.labels(run_id=run_id).inc()
```

where every run creates a new label value.

Explain why this is dangerous, remove the unbounded label, and move the execution identifier into run metadata/logs.

### Failure-injection principle

A good exercise does not merely prove that an error is logged. It proves that:

```text
failure
  ↓
signal
  ↓
detection
  ↓
correlation
  ↓
diagnosis
  ↓
recovery
```

actually works.

---

# 28. Production Debugging Workflow

Use this repeatable workflow:

```text
1. Observe symptom
2. Check dashboard
3. Identify affected pipeline/dataset
4. Check SLI/SLO
5. Find relevant run
6. Obtain run_id
7. Inspect run metadata
8. Search structured logs
9. Identify failing stage
10. Determine impact
11. Recover
12. Verify
13. Record incident
```

## Step 1 — Observe the symptom

Example:

```text
Gold revenue dashboard is lower than normal.
```

## Step 2 — Check the dashboard

Look at:

- freshness,
- volume,
- duration,
- failure rate,
- SLO status.

## Step 3 — Identify scope

Determine:

```text
Which dataset?
Which pipeline?
Which environment?
Which time interval?
```

## Step 4 — Check SLI/SLO

Was the consumer-facing reliability objective violated?

## Step 5 — Find the run

Use run metadata to identify the execution.

## Step 6 — Obtain `run_id`

Use the ID as the correlation key.

## Step 7 — Inspect run metadata

Check:

```text
status
rows_read
rows_written
duration
git_sha
image_digest
retry_count
error_type
```

## Step 8 — Search structured logs

Filter by:

```text
run_id
```

and identify the failing stage.

## Step 9 — Determine impact

Do not stop at "the pipeline failed."

Determine:

- affected data interval,
- affected datasets,
- downstream consumers,
- volume of bad/missing data.

## Step 10 — Recover

Possible actions include:

- retry,
- backfill,
- restore,
- rerun,
- quarantine,
- block publication.

## Step 11 — Verify

Use:

- row counts,
- freshness,
- quality checks,
- reconciliation,
- consumer-facing SLIs.

## Step 12 — Record

Capture the incident and future preventive action.

---

# 29. Common Production Mistakes

| Mistake | Why it happens | Why dangerous | Detection | Fix |
|---|---|---|---|---|
| Logging everything, measuring nothing | Logging feels easy | No trend/SLO visibility | No useful dashboards | Add purposeful metrics |
| Hundreds of useless metrics | Instrumentation without design | Noise and cost | Low dashboard usefulness | Define operational questions first |
| High-cardinality labels | IDs seem convenient | Monitoring instability | Series count grows | Bound labels |
| `run_id` as metric label | Correlation shortcut | Unbounded series | Cardinality review | Put ID in logs/run metadata |
| Missing code version | Run schema too small | Cannot explain regression | Run comparison | Store Git SHA |
| Missing image version | Source-only thinking | Artifact differs | Deployment audit | Store image digest |
| Missing data interval | Confusing execution and data time | Bad incident scope | Run review | Store interval |
| Status without row counts | Process-centric thinking | Silent data loss | Volume comparison | Store row/byte metrics |
| Monitoring infrastructure only | Platform-centric design | Consumer impact missed | Freshness incidents | Add data SLIs |
| Dashboards nobody uses | Dashboard-first design | Operational waste | Usage review | Start from questions |
| Alerting on every metric | Threshold obsession | Alert fatigue | Alert-volume analysis | Alert only on actionable conditions |
| No log/run correlation | Systems designed separately | Slow debugging | Incident drill | Standardize `run_id` |
| No standard metadata schema | Team-by-team design | Inconsistent operations | Schema audit | Unified model |
| Treating success as correctness | Process completion bias | Silent data failures | Data-quality checks | Combine status with data signals |
| Manual dashboards | UI-only operations | Configuration drift | Environment comparison | Dashboards as code |

---

# 30. Testing Observability

Instrumentation itself should be tested.

A pipeline can produce correct data while silently losing observability.

## 30.1 What to test

Verify:

- successful runs increment the success metric,
- failures increment the failure metric,
- `run_id` is present in structured logs,
- run metadata is written on failure,
- labels are bounded,
- duration is recorded,
- retries are represented correctly.

## 30.2 Example

A simplified test can validate run metadata behavior:

```python
def test_failed_run_is_recorded(run_store):
    run_store.start(
        run_id="orders_daily:test-001",
        pipeline="orders_daily",
    )

    try:
        raise TimeoutError("warehouse unavailable")
    except TimeoutError as exc:
        run_store.fail(
            run_id="orders_daily:test-001",
            error_type=type(exc).__name__,
        )

    record = run_store.get("orders_daily:test-001")

    assert record.status == "FAILED"
    assert record.error_type == "TimeoutError"
```

## 30.3 Cardinality testing

Treat metric labels as an interface.

A review should ask:

```text
Are all label dimensions bounded?
Can a new data value create an unbounded number of series?
```

This is a design test, not just a unit test.

---

# 31. Production Design Exercises

## Scenario A — Daily financial pipeline

Design:

- metrics,
- metric types,
- bounded labels,
- run metadata,
- logs,
- SLIs,
- SLOs,
- dashboard panels.

### Expected direction

Measure:

```text
runs
failures
duration
rows
bytes
freshness
quarantine
cost
```

A likely SLO:

```text
99% of daily revenue data is available before 07:00.
```

## Scenario B — Real-time fraud-event pipeline

Emphasize:

- event throughput,
- consumer lag,
- processing delay,
- rejected events,
- freshness,
- sink failures.

## Scenario C — Customer analytics platform

Emphasize:

- freshness,
- completeness,
- dataset-level health,
- consumer-visible availability,
- bounded dataset labels.

## Scenario D — Large Spark batch pipeline

Add:

- Spark application ID,
- stage/task timing,
- shuffle signals,
- executor/resource signals,
- input/output volume,
- pipeline-to-Spark correlation.

## Scenario E — Kafka event-processing platform

Add:

- consumer lag,
- partition activity,
- processing throughput,
- consumer health,
- processing delay,
- sink throughput.

For every scenario, explain not just *what* you measure, but *why*.

---

# 32. Hands-On Project

## Project: Production-Style Pipeline Observability

Build:

```text
Source
  ↓
Extract
  ↓
Transform
  ↓
Load
```

### Requirements

Use:

- Python
- Prometheus
- Grafana
- structured JSON logging
- `run_id`
- `contextvars`
- run metadata
- failure handling
- a basic SLI/SLO
- dashboard
- Docker Compose where appropriate

## 32.1 Suggested architecture

```text
                   ┌───────────────┐
                   │ Python Pipeline│
                   └───────┬───────┘
                           │
            ┌──────────────┼───────────────┐
            │              │               │
         Metrics          Logs         Run Metadata
            │              │               │
            ▼              ▼               ▼
       Prometheus      Log System       PostgreSQL
            │                             
            ▼
         Grafana
```

## 32.2 Directory structure

```text
pipeline-observability/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── metrics.py
│   ├── logging_config.py
│   ├── run_context.py
│   └── run_metadata.py
├── observability/
│   ├── prometheus.yml
│   └── dashboards/
│       └── pipeline-overview.json
├── tests/
│   ├── test_metrics.py
│   └── test_run_metadata.py
├── compose.yaml
└── pyproject.toml
```

## 32.3 Configuration

A minimal Compose setup:

```yaml
services:
  pipeline:
    build: .
    ports:
      - "8000:8000"

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./observability/prometheus.yml:/etc/prometheus/prometheus.yml:ro

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

## 32.4 Prometheus configuration

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "pipeline"
    static_configs:
      - targets: ["pipeline:8000"]
```

## 32.5 Run metadata implementation

Create a repository/service abstraction:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RunMetadata:
    run_id: str
    pipeline: str
    environment: str
    status: str
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float | None = None
    git_sha: str | None = None
    image_digest: str | None = None
    rows_read: int | None = None
    rows_written: int | None = None
    rows_quarantined: int | None = None
    retry_count: int = 0
    error_type: str | None = None
    cost: float | None = None
```

Persist these records in PostgreSQL or another durable store.

## 32.6 Project tasks

1. Implement the pipeline.
2. Start the Prometheus metrics endpoint.
3. Instrument run counters.
4. Instrument duration with a histogram.
5. Instrument row and byte counts.
6. Track freshness.
7. Generate a `run_id`.
8. Store unified run metadata.
9. Emit structured JSON logs.
10. Use `contextvars`.
11. Build a Grafana dashboard.
12. Define one SLI.
13. Define one SLO.
14. Inject at least three failures.
15. Debug each failure using the observability workflow.
16. Test the instrumentation.
17. Version the dashboard configuration.

## 32.7 Expected operational outcome

You should be able to answer:

> Which pipeline is unhealthy?

Then:

> Which execution caused it?

Then:

> What happened during that execution?

Then:

> Which version ran and what data did it process?

Then:

> What should we do to recover and verify?

---

# 33. Production-Level Reasoning

For every observability design decision, ask:

### Why?

Why do we need this signal?

### When?

When is this signal useful?

### Why not?

When would this mechanism be inappropriate?

### Trade-off?

What are the:

- storage costs,
- query costs,
- engineering costs,
- operational costs,
- maintenance costs?

### Failure?

What happens if the observability system itself fails?

### Scale?

How does the design behave at:

```text
1 million
100 million
1 billion
```

records/events?

### Security?

Could the telemetry expose:

- PII,
- secrets,
- credentials,
- sensitive business values?

### Maintainability?

Will another engineer understand the metric and metadata schema six months later?

> Do not learn observability as isolated tool commands. Learn the engineering decisions behind the telemetry.

---

# 34. Beginner → Advanced Progression

## Level 1 — Beginner

Understand:

- observability,
- metrics,
- logs,
- counters,
- gauges,
- histograms,
- run metadata.

## Level 2 — Intermediate

Understand:

- Prometheus,
- labels,
- structured logging,
- `run_id`,
- `contextvars`,
- Grafana,
- SLIs,
- SLOs.

## Level 3 — Advanced

Understand:

- RED/USE,
- cardinality,
- dashboard design,
- cross-system correlation,
- Airflow/Spark/Kafka/warehouse metrics,
- failure diagnosis.

## Level 4 — Production

Understand:

- observability architecture,
- operational trade-offs,
- SLO-driven monitoring,
- failure injection,
- testing instrumentation,
- dashboards as code,
- production debugging,
- cost/security considerations.

---

# 35. SQL for Run Metadata

Run metadata becomes significantly more useful when it is queryable.

## Failed runs

```sql
SELECT
    run_id,
    pipeline,
    start_time,
    duration_seconds,
    error_type
FROM run_metadata
WHERE status = 'FAILED'
ORDER BY start_time DESC;
```

## Runs by status in the last seven days

```sql
SELECT
    pipeline,
    status,
    COUNT(*) AS runs
FROM run_metadata
WHERE start_time >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY pipeline, status
ORDER BY pipeline, status;
```

## Slowest runs

```sql
SELECT
    pipeline,
    run_id,
    duration_seconds,
    rows_read,
    rows_written
FROM run_metadata
WHERE start_time >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY duration_seconds DESC
LIMIT 20;
```

## Retry-heavy pipelines

```sql
SELECT
    pipeline,
    AVG(retry_count) AS avg_retries,
    MAX(retry_count) AS max_retries
FROM run_metadata
WHERE start_time >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY pipeline
ORDER BY avg_retries DESC;
```

## Volume anomaly investigation

```sql
SELECT
    pipeline,
    run_id,
    rows_read,
    rows_written,
    start_time
FROM run_metadata
WHERE pipeline = 'orders_daily'
ORDER BY start_time DESC
LIMIT 30;
```

The actual anomaly detection strategy can be more sophisticated; the important point is that run metadata creates durable execution evidence.

---

# 36. Checkpoints

## Checkpoint — Fundamentals

You should be able to explain:

1. What is observability?
2. What is a counter?
3. What is a gauge?
4. What is a histogram?
5. Why is a metric different from run metadata?

**Answers**

1. The ability to understand system state and behavior from emitted evidence.
2. A monotonically increasing event measurement.
3. A current-state value that can move up or down.
4. A distribution-oriented metric type useful for latency and duration.
5. Metrics aggregate behavior; run metadata describes an individual execution.

## Checkpoint — Correlation

You should be able to explain:

1. Why use `run_id`?
2. Why use structured logs?
3. Why use `contextvars`?
4. Why should `run_id` normally not be a metric label?

**Answers**

1. It provides an execution-level correlation key.
2. They make operational events machine-searchable and structured.
3. They carry execution-local context without manually passing it through every function.
4. Run IDs are typically high-cardinality/unbounded and can create excessive time series.

## Checkpoint — Reliability

You should be able to explain:

1. What is an SLI?
2. What is an SLO?
3. How does RED apply to pipelines?
4. How does USE apply to infrastructure?
5. Why are data-specific signals still needed?

**Answers**

1. A user-relevant measurement.
2. A target for an SLI.
3. Rate, errors, and duration describe service/pipeline behavior.
4. Utilization, saturation, and errors describe resource behavior.
5. RED/USE alone do not capture freshness, completeness, or volume correctness.

---

# 37. Senior Interview Preparation

## 1. Metrics vs logs vs traces

**Answer:** Metrics provide aggregated operational signals, logs provide detailed events, and traces connect timed operations across services. This topic focuses on metrics and structured logs; tracing is developed in Topic 02.

## 2. Counter vs gauge vs histogram

**Answer:** Counters measure cumulative events, gauges represent current state, and histograms capture distributions such as latency.

## 3. Why not use `run_id` as a Prometheus label?

**Answer:** Run IDs are usually high-cardinality and effectively unbounded. Each unique value can create another time series, increasing resource and query costs. Put run IDs in logs and run metadata.

## 4. How would you design pipeline metrics?

**Answer:** Start from operational questions. Measure run success/failure, duration, retries, rows/bytes, freshness, quarantine, lag, throughput, queue time, and cost where relevant. Use bounded labels and align metrics with consumer-facing SLIs.

## 5. What belongs in run metadata?

**Answer:** Execution identity, pipeline/environment, status, timing, code version, image digest, data interval, row/byte counts, quarantine, retries, error type, and relevant cost or engine identifiers.

## 6. Why store both Git SHA and image digest?

**Answer:** Git SHA identifies source revision; image digest identifies the immutable deployed artifact. They answer related but different reproducibility questions.

## 7. What is an SLI?

**Answer:** A measurement that represents a user-relevant aspect of service behavior.

## 8. What is an SLO?

**Answer:** A reliability objective defined against an SLI over a stated measurement window.

## 9. RED vs USE?

**Answer:** RED describes service behavior through Rate, Errors, and Duration. USE describes resource behavior through Utilization, Saturation, and Errors.

## 10. How would you debug a slow pipeline?

**Answer:** Start with dashboard symptoms, identify the affected pipeline and SLI, locate the run, obtain `run_id`, inspect run metadata, compare duration/volume/version, search structured logs, identify the failing stage, determine impact, recover, and verify.

## 11. What makes a data pipeline dashboard useful?

**Answer:** It answers operational questions and presents health, freshness, failures, performance, volume, and SLO state without overwhelming operators with every available metric.

## 12. How should Airflow and application instrumentation coexist?

**Answer:** Airflow provides orchestration-level signals such as DAG/task status and scheduling behavior. Application instrumentation provides data-specific signals such as rows, bytes, freshness, and execution details.

## 13. How would Spark observability integrate with pipeline observability?

**Answer:** Correlate pipeline `run_id` with Spark application identifiers and combine pipeline-level metrics with Spark job/stage/task and resource metrics.

## 14. How would Kafka observability integrate?

**Answer:** Combine consumer lag, throughput, partition activity, and processing delay with pipeline-level freshness and run metadata.

## 15. What is the biggest observability anti-pattern?

**Answer:** Collecting telemetry without designing around operational questions. More telemetry does not automatically create more observability.

---

# 38. Final Assessment

## Basic

1. Define observability.
2. Explain monitoring vs observability.
3. Explain counters, gauges, histograms, and summaries.
4. Explain metrics vs logs.
5. Explain run metadata.
6. Define `run_id`.
7. Explain freshness.
8. Explain cardinality.

## Intermediate

1. Instrument a Python pipeline using `prometheus-client`.
2. Expose `/metrics`.
3. Configure Prometheus scraping.
4. Design a unified `run_metadata` table.
5. Emit structured JSON logs.
6. Add `run_id` correlation using `contextvars`.
7. Build a Grafana dashboard.
8. Define an SLI and SLO.

## Advanced

1. Design RED and USE metrics for a Spark pipeline.
2. Explain bounded metric labels.
3. Integrate Airflow metrics with application metrics.
4. Correlate Kafka lag with consumer-facing freshness.
5. Correlate warehouse jobs with pipeline executions.
6. Design dashboards as code.
7. Test observability instrumentation.
8. Design failure-injection experiments.

## Senior-level

1. A pipeline succeeds but row volume falls by 80%. Design the investigation.
2. Prometheus memory usage grows rapidly after a new metric deployment. Diagnose the likely cause.
3. A pipeline becomes slower only in production. Explain how run metadata helps isolate the cause.
4. A daily revenue SLO is violated. Design the investigation and recovery workflow.
5. Design observability for a platform processing one billion events per day.
6. Explain what telemetry should never contain and why.
7. Design a standardized observability contract for multiple pipeline teams.
8. Explain how you would measure whether the observability system itself is useful.

---

# 39. Final Production Challenge

> **Scenario:** A critical daily revenue pipeline reports `SUCCESS`, but downstream dashboards show revenue approximately **18% lower than expected**.

Investigate using:

- metrics,
- run metadata,
- structured logs,
- `run_id`,
- freshness,
- row counts,
- bytes,
- pipeline duration,
- SLI/SLO,
- dashboard,
- debugging workflow.

## Expert investigation

### Step 1 — Start from the consumer symptom

The first fact is:

```text
Revenue is 18% lower.
```

Do not assume that a successful pipeline means the data is correct.

### Step 2 — Check dashboard signals

Inspect:

```text
freshness
rows read
rows written
duration
failures
quarantine
SLO status
```

Suppose:

```text
rows_read:
12.0M → 9.6M
```

That is a 20% reduction and is directionally consistent with the revenue discrepancy.

### Step 3 — Find the run

Locate the affected execution:

```text
run_id =
orders_daily:2026-10-05:production
```

### Step 4 — Inspect run metadata

Suppose:

```text
status = SUCCESS
rows_read = 9,600,000
rows_written = 9,580,000
git_sha = abc123
image_digest = sha256:...
```

The successful status is not enough.

### Step 5 — Inspect structured logs

Search:

```text
run_id="orders_daily:2026-10-05:production"
```

Look for:

```text
source response size
pagination counts
filter counts
transform counts
load counts
warnings
```

Suppose the extraction logs reveal:

```text
page 1: 5,000,000 records
page 2: 4,600,000 records
API reported next page but extractor stopped
```

### Step 6 — Determine impact

Compare:

```text
expected source volume
actual source volume
transformed volume
loaded volume
```

Then determine affected:

- data interval,
- downstream tables,
- dashboards,
- consumers.

### Step 7 — Recover

Possible recovery:

- correct extractor behavior,
- rerun/backfill the affected interval,
- verify idempotency,
- reconcile output.

### Step 8 — Verify

Do not stop after a green rerun.

Verify:

- expected row counts,
- expected bytes,
- freshness,
- quality checks,
- revenue reconciliation,
- SLO state.

### Core lesson

> **A successful pipeline execution is not necessarily a successful data product.**

---

# 40. Glossary

| Term | Meaning |
|---|---|
| Observability | Ability to understand system state from emitted evidence |
| Telemetry | Operational information emitted by a system |
| Metric | Quantitative measurement over time |
| Counter | Cumulative event measurement |
| Gauge | Current-state measurement |
| Histogram | Distribution-oriented metric |
| Summary | Metric type exposing summary/quantile information |
| Prometheus | Time-series metrics and monitoring system |
| PromQL | Prometheus query language |
| Label | Key/value dimension attached to a metric |
| Cardinality | Number of unique time-series combinations |
| Structured logging | Logs represented as structured fields |
| Run metadata | Durable record describing one execution |
| `run_id` | Identifier used to correlate an execution |
| SLI | Service Level Indicator |
| SLO | Service Level Objective |
| SLA | Service Level Agreement |
| Error budget | Allowed unreliability implied by an SLO |
| RED | Rate, Errors, Duration |
| USE | Utilization, Saturation, Errors |
| Freshness | Age of the newest available data |
| Lag | Processing delay behind the expected position/time |
| Throughput | Amount of work/data processed per unit time |
| Dashboard | Visual operational view of system signals |

---

# 41. Final Learning Checklist

```text
[ ] Explain observability
[ ] Explain metrics vs logs vs traces
[ ] Explain Counter
[ ] Explain Gauge
[ ] Explain Histogram
[ ] Explain Summary
[ ] Instrument Python with prometheus-client
[ ] Explain Prometheus scraping
[ ] Design pipeline metrics
[ ] Design run metadata
[ ] Design run_id
[ ] Implement structured JSON logs
[ ] Use contextvars for correlation
[ ] Correlate metrics → run metadata → logs
[ ] Explain SLIs
[ ] Define SLOs
[ ] Apply RED
[ ] Apply USE
[ ] Control metric cardinality
[ ] Build Grafana dashboards
[ ] Understand dashboards as code
[ ] Instrument Airflow pipelines
[ ] Understand Spark metrics
[ ] Understand Kafka metrics
[ ] Understand warehouse metrics
[ ] Test observability instrumentation
[ ] Debug a failed/slow pipeline
[ ] Perform failure injection
[ ] Design production observability
```

---

# 42. Final Self-Audit

Before considering this topic complete, verify that you can explicitly explain:

- Observability signals.
- Counters.
- Gauges.
- Histograms.
- Summaries.
- Prometheus client.
- Prometheus scraping.
- Grafana.
- Run duration.
- Success/failure.
- Retries.
- Rows.
- Bytes.
- Quarantine.
- Freshness.
- Lag.
- Queue time.
- Cost.
- Batch metrics vs run metadata.
- Unified run metadata.
- `run_id`.
- Structured JSON logging.
- `contextvars`.
- SLIs.
- SLOs.
- RED.
- USE.
- Label/cardinality rules.
- Dashboards as code.
- Airflow.
- Spark.
- Kafka.
- Warehouses.
- Production instrumentation.
- Failure simulation.
- Testing instrumentation.
- Debugging workflow.
- Production design trade-offs.

If any item is unclear, return to that section and implement it in the hands-on project before moving to Topic 02.

---

# 43. Final Engineering Principles

1. **Measure what consumers experience, not only what machines do.**
2. **Use metrics for aggregated operational behavior.**
3. **Use run metadata for execution-level evidence.**
4. **Use structured logs for detailed diagnostic events.**
5. **Correlate everything with a useful execution identity.**
6. **Keep metric labels bounded.**
7. **Do not put unbounded identifiers into Prometheus labels.**
8. **Track data volume and freshness, not only process status.**
9. **Store the code and artifact versions that produced the run.**
10. **Define SLIs from consumer experience and SLOs from reliability objectives.**
11. **Use RED and USE as complementary frameworks, not rigid rules.**
12. **Treat dashboards as operational products and version them as code.**
13. **Connect Airflow, Spark, Kafka, and warehouse telemetry to pipeline execution context.**
14. **Test observability itself.**
15. **Inject failures deliberately.**
16. **A green pipeline status does not prove correct data.**
17. **Telemetry must not become a source of PII or secret leakage.**
18. **Design for scale, cost, security, and maintainability from the beginning.**
19. **Observability is successful only when it helps an engineer detect, diagnose, recover, and verify.**
20. **The objective is not more telemetry; the objective is better operational decisions.**

---

## Connection to Module 2.20

This topic establishes the measurement layer for the remainder of Module 2.20:

```text
01 Metrics + Run Metadata
        ↓
02 OpenTelemetry Tracing
        ↓
03 Alerting + On-Call
        ↓
04 Lineage
        ↓
05 Catalog
        ↓
06 PII Protection
        ↓
07 Encryption
        ↓
08 Access Control
        ↓
09 Retention + Erasure
        ↓
10 Incident Response
```

The next topic adds distributed tracing so that the platform can answer not only:

> **What is happening?**

but also:

> **Where did the work happen, how did context move across systems, and where did the time go?**
