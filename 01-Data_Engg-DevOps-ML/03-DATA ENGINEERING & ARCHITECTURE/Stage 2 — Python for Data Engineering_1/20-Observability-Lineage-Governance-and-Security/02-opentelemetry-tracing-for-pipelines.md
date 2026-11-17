# 02 — OpenTelemetry Tracing for Pipelines

> **Module 2.20 — Observability, Lineage, Governance, and Security**
>
> This chapter teaches distributed tracing for data pipelines from first principles through production-grade OpenTelemetry architecture, propagation, sampling, security, debugging, and operational design.

---

## 1. Module Overview

### The problem this module solves

A production data pipeline may cross many systems:

```text
API
 ↓
Kafka
 ↓
Python Consumer
 ↓
Spark
 ↓
Object Storage
 ↓
Warehouse
```

Suppose the pipeline normally completes in 12 minutes and suddenly takes 42 minutes.

Metrics from Topic 01 may tell you:

```text
pipeline_duration = 42 minutes
```

Structured logs may eventually tell you:

```text
warehouse timeout
```

But an engineer still needs to answer:

- Where did the 42 minutes go?
- Which service consumed most of the time?
- Was the API slow?
- Was Kafka delayed?
- Was Python processing slow?
- Was Spark slow?
- Was object storage slow?
- Was the warehouse slow?
- Did the execution travel through all expected systems?
- Where did the failure originate?
- Which downstream operation inherited the delay?

**Distributed tracing** answers these questions by following one execution across system boundaries.

### Metrics, logs, and traces

```text
Metrics
   ↓
What is happening?

Logs
   ↓
What happened?

Traces
   ↓
Where did this execution travel,
and where did it spend its time?
```

Tracing does **not** replace metrics or logs.

A production observability system uses all three:

| Signal | Primary question | Example |
|---|---|---|
| Metrics | What is happening? | Pipeline duration increased |
| Logs | What happened? | Warehouse connection timed out |
| Traces | Where did execution spend time? | Warehouse span took 28 minutes |

### Learning objectives

By the end of this module you should be able to:

- Explain distributed tracing from first principles.
- Explain traces, spans, parent/child relationships, trace IDs, and span IDs.
- Design useful span attributes and events.
- Record span status and exceptions correctly.
- Configure the OpenTelemetry Python SDK.
- Configure a tracer provider and resource attributes.
- Create manual spans.
- Export telemetry using OTLP.
- Use auto-instrumentation and manual instrumentation together.
- Instrument HTTP clients such as HTTPX.
- Understand database and cloud-client instrumentation.
- Explain context propagation.
- Explain W3C Trace Context.
- Propagate context over HTTP.
- Propagate context through Kafka message headers.
- Design traces for batch and streaming data pipelines.
- Correlate `run_id` with `trace_id`.
- Connect orchestrator, Spark, storage, and warehouse operations to pipeline traces.
- Correlate metrics, logs, and traces.
- Understand metric exemplars.
- Deploy an OpenTelemetry Collector.
- Explain receivers, processors, and exporters.
- Use redaction and filtering to protect telemetry.
- Design head and tail sampling.
- Avoid per-record spans in high-throughput streams.
- Test tracing instrumentation.
- Inject failures and debug distributed pipelines.
- Make production trade-offs around cost, overhead, security, and visibility.

---

# 2. Where This Topic Fits in Module 2.20

The Module 2.20 sequence is:

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

Topic 01 established:

- pipeline metrics,
- run metadata,
- `run_id`,
- structured logs,
- SLIs/SLOs,
- dashboards,
- operational debugging.

This topic adds a **distributed execution view**.

The key relationship is:

```text
Topic 01:
run_id → execution record → logs

Topic 02:
trace_id → distributed execution → spans
```

They are complementary identifiers.

### Checkpoint

**Question:** Why is tracing not simply "better logging"?

**Answer:** Logs describe events, while a trace models the hierarchy and timing of operations across service boundaries. Traces reveal where an execution spent time and how operations are causally related.

---

# 3. Why Distributed Tracing Exists

Consider:

```text
API
 ↓
Kafka
 ↓
Python Consumer
 ↓
Spark
 ↓
Object Storage
 ↓
Warehouse
```

A single pipeline execution may involve:

- multiple processes,
- multiple machines,
- multiple services,
- asynchronous messaging,
- network calls,
- database operations,
- distributed compute.

A timestamp in one service is not enough to reconstruct the whole execution.

## Without tracing

You might see:

```text
07:00 API request started
07:01 API request completed

07:02 Kafka consumer started
07:03 Spark started

07:25 warehouse load started
07:42 warehouse load completed
```

But you may not know whether these events belong to the same logical execution.

## With tracing

You can see:

```text
Trace: 4bf92f...
│
├── pipeline.run                 42m
│   ├── extract                  3m
│   ├── kafka.publish            1m
│   ├── consumer.process        30m
│   │   └── transform            5m
│   └── warehouse.load            8m
```

Now the investigation becomes:

> The pipeline was slow because consumer processing spent 30 minutes waiting or processing, rather than because the API was slow.

That is the central value of distributed tracing.

### Checkpoint

**Question:** What is the key question tracing answers that a simple duration metric cannot?

**Answer:** It shows where the execution spent its time and how that execution moved across components.

---

# 4. Distributed Tracing Fundamentals

## 4.1 Trace

A **trace** represents one distributed operation or logical execution.

For a data pipeline, an appropriate trace might represent:

```text
one pipeline run
```

when that execution is sufficiently bounded and useful as one distributed operation.

## 4.2 Span

A **span** represents one timed operation inside the trace.

Examples:

```text
pipeline.run
pipeline.extract
http.request
kafka.publish
pipeline.transform
spark.operation
warehouse.load
```

A span has:

- start time,
- end time,
- name,
- context,
- attributes,
- events,
- status,
- optional exception information.

## 4.3 Parent span

A parent span is the operation that logically contains another operation.

```text
pipeline.run
    ↓
pipeline.extract
```

## 4.4 Child span

The nested operation is a child span.

```text
pipeline.run
└── pipeline.extract
```

## 4.5 Root span

The top-level span has no parent inside the trace.

For a batch pipeline:

```text
pipeline.run
```

can be the root span.

## 4.6 Trace ID

A trace ID identifies the complete distributed operation.

Example:

```text
trace_id = 4bf92f3577b34da6
```

Real trace IDs are normally longer than this illustrative value; the example is intentionally abbreviated.

## 4.7 Span ID

A span ID identifies one span:

```text
span_id = 00f067aa0ba902b7
```

The trace ID remains stable across the distributed execution while span IDs distinguish individual operations.

## 4.8 Span hierarchy

```text
Trace
│
├── Pipeline Run
│   │
│   ├── Extract
│   │
│   ├── Kafka Publish
│   │
│   ├── Transform
│   │   ├── Spark Operation
│   │   └── Object Storage Write
│   │
│   └── Warehouse Load
```

This hierarchy lets an engineer reconstruct the execution.

### Checkpoint

1. What is a trace?
2. What is a span?
3. What is a root span?
4. What is a child span?
5. What identifies the complete trace?

**Answers**

1. A distributed logical operation represented as a collection of related spans.
2. A timed operation inside a trace.
3. The top-level span with no parent in that trace.
4. A span nested under another span.
5. The trace ID.

---

# 5. Trace vs Log vs Metric

A useful production mental model is:

```text
Metric
  ↓
Detect abnormal behavior

Trace
  ↓
Locate the slow/failing operation

Log
  ↓
Understand detailed context
```

### Example

Metric:

```text
pipeline_duration_seconds = 2,880
```

Trace:

```text
pipeline.run
└── warehouse.load = 2,100 seconds
```

Log:

```json
{
  "level": "ERROR",
  "run_id": "orders:2026-10-05:prod",
  "trace_id": "4bf92f...",
  "span_id": "00f067...",
  "stage": "warehouse_load",
  "error": "connection timeout"
}
```

The three signals form a chain:

```text
metric
  ↓
trace
  ↓
log
```

### Why all three matter

A metric is efficient for aggregation.

A trace is efficient for distributed timing and causality.

A log is efficient for detailed diagnostic information.

Removing one creates blind spots.

---

# 6. Span Attributes

A span's attributes describe the operation.

Examples:

```text
pipeline.name
pipeline.run_id
pipeline.environment
data.dataset
data.interval.start
data.interval.end
service.name
service.version
deployment.environment
```

A Python example:

```python
with tracer.start_as_current_span("pipeline.extract") as span:
    span.set_attribute("pipeline.name", "orders_daily")
    span.set_attribute("pipeline.run_id", "orders:2026-10-05:prod")
    span.set_attribute("pipeline.environment", "prod")
    span.set_attribute("data.dataset", "orders")
```

## What makes a good attribute?

A useful attribute is:

- relevant to the operation,
- stable enough to query,
- safe to expose,
- bounded where possible,
- consistently named.

### Good

```text
pipeline.name = orders_daily
pipeline.environment = prod
data.dataset = orders
```

### Risky

```text
customer.email = alice@example.com
request.body = <entire sensitive payload>
authorization = Bearer ...
```

Telemetry is itself data. It must be treated as a protected data asset.

### Resource attributes vs span attributes

**Resource attributes** describe the entity producing telemetry.

```text
service.name
service.version
deployment.environment
```

**Span attributes** describe one operation.

```text
pipeline.run_id
data.dataset
operation.type
```

---

# 7. Semantic Conventions

Semantic conventions provide standardized attribute names and meanings.

The goal is consistency:

```text
Team A
service.name

Team B
service.name

Team C
service.name
```

rather than:

```text
Team A → app_name
Team B → service
Team C → service_identifier
```

Use established OpenTelemetry semantic conventions where applicable.

For data-platform-specific concepts that do not have a suitable standardized convention, define a documented internal naming scheme.

### Production rule

> Consistency across teams is more valuable than inventing a new attribute name for every application.

---

# 8. Span Events

A span is a duration.

An **event** is a timestamped occurrence inside that span.

Example:

```text
Span:
pipeline.transform
│
├── event: schema_validation_started
├── event: schema_validation_failed
├── event: retry_attempt
└── event: checkpoint_created
```

## Python example

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("pipeline.transform") as span:
    span.add_event("schema_validation_started")

    try:
        validate_schema()
    except Exception as exc:
        span.add_event(
            "schema_validation_failed",
            attributes={
                "error.type": type(exc).__name__,
            },
        )
        raise
```

## Event vs span

Use a **new span** when an operation has meaningful duration and should be independently analyzed.

Use an **event** when something happened at a point in time inside an existing operation.

For example:

```text
Span:
warehouse.load
```

Events:

```text
merge_started
merge_commit
checkpoint_created
```

Do not create spans for every tiny internal event.

---

# 9. Span Status and Error Recording

OpenTelemetry spans have a status concept.

Conceptually:

```text
UNSET
OK
ERROR
```

A failed operation should record enough information to support diagnosis.

## Recording an exception

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("warehouse.load") as span:
    try:
        load_to_warehouse()
    except Exception as exc:
        span.record_exception(exc)
        span.set_status(
            trace.Status(
                trace.StatusCode.ERROR,
                description=str(exc),
            )
        )
        raise
```

### Exception recording vs status

These are related but distinct:

```text
record_exception()
```

records exception information, potentially including stack information.

```text
set_status(ERROR)
```

marks the span's operational status.

A production error-handling strategy should use both when appropriate.

### Avoid sensitive exception content

An exception message can contain:

- SQL parameters,
- customer information,
- access paths,
- secrets accidentally embedded by dependencies.

Review what gets exported.

---

# 10. OpenTelemetry Fundamentals

## What is OpenTelemetry?

OpenTelemetry is a vendor-neutral framework for generating, processing, and exporting telemetry.

It supports:

- traces,
- metrics,
- logs through the broader ecosystem.

For this module, the focus is distributed tracing.

The architecture is:

```text
Application
    ↓
OpenTelemetry API / SDK
    ↓
Exporter
    ↓
OTLP
    ↓
OpenTelemetry Collector
    ↓
Tracing Backend
```

## Why OpenTelemetry?

Without a common instrumentation model, teams can become tightly coupled to one observability vendor.

OpenTelemetry provides:

- common APIs,
- SDKs,
- instrumentation,
- propagation,
- exporters,
- collector architecture,
- semantic conventions.

### Checkpoint

**Question:** Is OpenTelemetry itself a tracing UI?

**Answer:** No. OpenTelemetry provides APIs, SDKs, instrumentation, propagation, and telemetry pipeline components. A backend such as Jaeger or Grafana Tempo can store and display traces.

---

# 11. OpenTelemetry API vs SDK

## API

The API is what application instrumentation code interacts with.

Conceptually:

```python
tracer = trace.get_tracer(__name__)
```

The application asks for a tracer without needing to know every export implementation detail.

## SDK

The SDK provides the implementation/configuration:

- tracer provider,
- span processors,
- exporters,
- resource information,
- sampling configuration.

This separation lets application instrumentation remain relatively independent from deployment-specific telemetry configuration.

---

# 12. Python OpenTelemetry Setup

For Python 3.12+:

```bash
uv add \
  opentelemetry-api \
  opentelemetry-sdk \
  opentelemetry-exporter-otlp
```

For HTTPX instrumentation:

```bash
uv add opentelemetry-instrumentation-httpx
```

Other integrations should be installed only when actually needed.

### Version discipline

OpenTelemetry integrations evolve. For production:

1. Pin compatible versions.
2. Read the integration's current documentation.
3. Test the instrumentation.
4. Avoid copying unverified examples from unrelated versions.

---

# 13. Tracer Provider

A tracer provider is the central SDK configuration for producing spans.

A minimal example:

```python
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

resource = Resource.create(
    {
        "service.name": "orders-pipeline",
        "service.version": "1.4.2",
        "deployment.environment": "prod",
    }
)

provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("orders-pipeline")
```

The important information is:

```text
service.name
service.version
deployment.environment
```

## Why resource information matters

Suppose a trace contains:

```text
service.name = orders-consumer
service.version = 1.4.2
deployment.environment = prod
```

An engineer can immediately distinguish it from:

```text
service.name = orders-consumer
service.version = 1.3.9
deployment.environment = staging
```

This is critical when debugging deployment-specific behavior.

---

# 14. Exporting with OTLP

OTLP stands for:

> **OpenTelemetry Protocol**

Operationally:

```text
Application
    ↓
OTLP
    ↓
Collector
    ↓
Tracing Backend
```

OTLP supports common transport patterns including HTTP and gRPC.

The exact endpoint and exporter configuration depend on deployment.

### Why a protocol matters

The application should not need to know every backend-specific storage detail.

Instead:

```text
Application → OTLP → Collector → Backend
```

provides a decoupling boundary.

---

# 15. Creating Manual Spans

The basic API is:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("extract"):
    rows = extract_data()
```

`start_as_current_span()`:

- creates a span,
- makes it current,
- establishes parent-child context,
- ends the span when the context manager exits.

## Pipeline example

```python
from opentelemetry import trace

tracer = trace.get_tracer("orders-pipeline")


def extract():
    with tracer.start_as_current_span("pipeline.extract"):
        return read_source()


def transform(rows):
    with tracer.start_as_current_span("pipeline.transform"):
        return clean_rows(rows)


def load(rows):
    with tracer.start_as_current_span("pipeline.load"):
        write_warehouse(rows)


def run_pipeline():
    with tracer.start_as_current_span("pipeline.run"):
        rows = extract()
        rows = transform(rows)
        load(rows)
```

Conceptually:

```text
pipeline.run
├── pipeline.extract
├── pipeline.transform
└── pipeline.load
```

---

# 16. Tracing a Pipeline Run

A production root span might represent one execution:

```text
pipeline.run
```

with child spans:

```text
pipeline.run
├── extract
├── transform
│   └── spark.operation
├── object_storage.write
└── warehouse.load
```

Useful root-span attributes:

```python
with tracer.start_as_current_span("pipeline.run") as span:
    span.set_attribute("pipeline.name", "orders_daily")
    span.set_attribute("pipeline.run_id", run_id)
    span.set_attribute("pipeline.environment", "prod")
    span.set_attribute("data.interval.start", interval_start)
    span.set_attribute("data.interval.end", interval_end)

    run_pipeline_steps()
```

### One trace per pipeline run?

Often yes for bounded batch executions, because it creates a natural debugging unit.

But the decision depends on:

- execution duration,
- trace size,
- orchestration model,
- asynchronous work,
- sampling,
- backend limits.

A trace should remain useful and operationally manageable.

---

# 17. Resource Attributes vs Span Attributes

### Resource

Describes the service/process/entity:

```text
service.name
service.version
deployment.environment
```

### Span

Describes an operation:

```text
pipeline.run_id
pipeline.name
data.dataset
operation.type
```

Example:

```text
Resource:
service.name = orders-consumer

Span:
name = kafka.process_batch
pipeline.run_id = orders:2026-10-05:prod
data.dataset = orders
```

Do not put execution-specific values into resource attributes.

---

# 18. Auto-Instrumentation

**Auto-instrumentation** means an integration automatically creates spans around supported library operations.

For example:

```text
Python application
      ↓
HTTPX instrumentation
      ↓
HTTP request spans
```

This reduces manual code.

## Manual vs automatic

### Manual instrumentation

You explicitly create:

```text
pipeline.extract
pipeline.transform
pipeline.load
```

This understands your business/pipeline semantics.

### Automatic instrumentation

The instrumentation library can create:

```text
HTTP request
database client operation
supported library call
```

This understands library-level operations.

### Production pattern

Use both:

```text
Automatic:
HTTP / DB / supported clients

Manual:
pipeline / business / task-level operations
```

Automatic instrumentation cannot infer that:

```text
"orders_daily"
```

is a business-critical pipeline stage unless you tell it.

---

# 19. HTTPX Instrumentation

A pipeline may call an external API:

```text
Pipeline
  ↓
HTTP API
  ↓
Response
```

Install:

```bash
uv add opentelemetry-instrumentation-httpx
```

A version-specific integration may use instrumentation helpers supplied by the package.

Conceptually:

```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

HTTPXClientInstrumentor().instrument()
```

Then:

```python
import httpx

response = httpx.get("https://example.internal/orders")
```

can produce an HTTP span.

### What the span can help answer

- How long was the request?
- What destination was called?
- What HTTP status was returned?
- Did the request fail?

### What should not be captured blindly

Never make telemetry collection a reason to expose:

```text
Authorization
API keys
passwords
sensitive request bodies
sensitive response bodies
```

Review instrumentation configuration and exported attributes.

---

# 20. Database and Cloud Instrumentation

Supported database and cloud libraries may have OpenTelemetry integrations.

A database span can provide evidence about:

```text
operation
duration
status
database/service
```

A cloud-client span may show:

```text
object storage operation
queue operation
managed service call
```

The exact package and API depend on the client library and OpenTelemetry integration version.

### Automatic instrumentation vs business spans

Automatic:

```text
warehouse query
object storage PUT
```

Manual:

```text
daily_revenue_publish
customer_snapshot_build
```

The two layers answer different questions.

### SQL safety

Do not automatically attach full SQL statements when they may contain:

- literal PII,
- sensitive parameters,
- secrets,
- proprietary business data.

Prefer safe operation identifiers and controlled metadata.

---

# 21. Context Propagation

Context propagation answers:

> How does Service B know that its operation belongs to the same distributed trace as Service A?

Architecture:

```text
Service A
   │
   │ trace context
   ▼
Service B
   │
   │ trace context
   ▼
Service C
```

Without propagation:

```text
Trace A

Trace B

Trace C
```

The backend cannot reliably reconstruct one distributed execution.

With propagation:

```text
Trace A
├── Service A
├── Service B
└── Service C
```

Context includes information needed to establish parent/child relationships.

---

# 22. W3C Trace Context

W3C Trace Context is a standardized way to carry trace context between systems.

Important concepts:

- `traceparent`
- `tracestate`
- trace ID
- parent span ID
- trace flags

A simplified representation is:

```text
traceparent:
version-trace_id-parent_span_id-flags
```

For example:

```text
00-4bf92f3577b34da6-00f067aa0ba902b7-01
```

The exact values are illustrative.

### Why standardization matters

If every team invented its own propagation header:

```text
X-Team-A-Trace
X-Team-B-Correlation
X-Team-C-Execution
```

distributed correlation would become fragile.

A shared standard creates interoperability.

---

# 23. HTTP Context Propagation

HTTP commonly carries trace context in headers.

Conceptually:

```text
Service A
   |
   | traceparent
   ▼
Service B
```

OpenTelemetry propagation APIs handle injection and extraction.

### Conceptual Python

```python
from opentelemetry.propagate import inject

headers = {}
inject(headers)

send_http_request(headers=headers)
```

On the receiving side:

```python
from opentelemetry.propagate import extract

context = extract(request.headers)
```

Instrumentation libraries normally handle this automatically for supported HTTP clients/frameworks.

### If propagation is missing

The receiver may start a new trace:

```text
Trace A
  └── HTTP request

Trace B
  └── receiver processing
```

instead of:

```text
Trace A
  └── HTTP request
      └── receiver processing
```

---

# 24. Kafka Context Propagation

HTTP headers are not enough for data platforms.

Consider:

```text
Producer
   ↓
Kafka topic
   ↓
Consumer
```

Kafka messages can carry headers.

Trace context can be injected into those headers.

Conceptual flow:

```text
Producer
  ↓
inject(context)
  ↓
Kafka headers
  ↓
Kafka topic
  ↓
extract(headers)
  ↓
Consumer
```

## Producer-side conceptual example

```python
from opentelemetry import trace
from opentelemetry.propagate import inject

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("kafka.publish") as span:
    headers = {}
    inject(headers)

    kafka_headers = [
        (key, value.encode("utf-8"))
        for key, value in headers.items()
    ]

    producer.send(
        "orders",
        value=payload,
        headers=kafka_headers,
    )
```

The exact producer API varies by Kafka client.

## Consumer-side conceptual example

```python
from opentelemetry import trace
from opentelemetry.propagate import extract

tracer = trace.get_tracer(__name__)

for message in consumer:
    carrier = {
        key: value.decode("utf-8")
        for key, value in message.headers
    }

    parent_context = extract(carrier)

    with tracer.start_as_current_span(
        "kafka.process",
        context=parent_context,
    ):
        process(message.value)
```

The exact header representation varies by Kafka client.

### Important messaging caveat

Kafka is asynchronous.

A producer span and consumer span may not represent a simple synchronous parent/child call in the same way as HTTP.

The trace relationship should reflect messaging semantics and the chosen instrumentation model. Do not assume every messaging trace is equivalent to an RPC tree.

---

# 25. End-to-End Kafka Trace

Consider:

```text
API
 ↓
Kafka Producer
 ↓
Kafka
 ↓
Kafka Consumer
 ↓
Processing
 ↓
Warehouse
```

A conceptual trace:

```text
API request
│
├── Kafka publish
│
└── Consumer processing
     │
     ├── transform
     └── warehouse write
```

The exact relationship between producer and consumer spans depends on messaging instrumentation and propagation semantics, but the trace context should let engineers correlate the execution.

### What this enables

An engineer can move from:

```text
consumer processing is slow
```

to:

```text
this execution originated from trace 4bf92f...
and spent most of its time in warehouse write
```

---

# 26. Pipeline Trace Design

For a batch pipeline:

```text
Airflow DAG
 ↓
Extract
 ↓
Transform
 ↓
Load
```

A useful design is:

```text
Root:
pipeline.run

Children:
pipeline.extract
pipeline.transform
pipeline.load
```

Additional spans may represent meaningful external operations:

```text
pipeline.extract
└── http.request

pipeline.transform
└── spark.operation

pipeline.load
└── warehouse.operation
```

Do not make every internal function a span.

### Span granularity rule

Create a span when an operation has enough:

- duration,
- operational meaning,
- diagnostic value

to justify independent telemetry.

---

# 27. `run_id` and `trace_id`

These identifiers are related but not identical.

## `run_id`

A business/operational execution identifier.

Example:

```text
orders:2026-10-05:prod
```

It belongs naturally in:

- run metadata,
- logs,
- pipeline records,
- operational dashboards.

## `trace_id`

A distributed tracing identifier.

Example:

```text
4bf92f3577b34da6...
```

It belongs naturally in:

- trace context,
- spans,
- correlated logs.

### Use both

```json
{
  "run_id": "orders:2026-10-05:prod",
  "trace_id": "4bf92f3577b34da6...",
  "span_id": "00f067aa..."
}
```

Why?

A pipeline execution can produce multiple traces or trace segments depending on asynchronous boundaries, retries, and architecture. The run ID remains the operational execution key while the trace ID represents one distributed trace.

---

# 28. Airflow / Orchestrator Context

A typical orchestrated pipeline looks like:

```text
DAG Run
  ↓
Task
  ↓
Task
  ↓
Task
```

A useful tracing architecture is:

```text
DAG run / pipeline execution
        ↓
root pipeline span
        ↓
task spans
        ↓
external operation spans
```

For example:

```text
pipeline.run
├── extract.task
│   └── http.request
├── transform.task
│   └── spark.operation
└── load.task
    └── warehouse.operation
```

### Orchestrator metadata

Keep operational identifiers such as:

```text
dag_id
task_id
run_id
execution interval
```

available for correlation where safe.

### Version caution

Airflow OpenTelemetry integration behavior can vary by Airflow version, providers, and deployment architecture. Do not assume one instrumentation API works across every version.

The stable architecture is:

```text
Airflow execution context
        ↓
trace context
        ↓
task instrumentation
        ↓
external operation spans
```

Use the exact integration supported by the version deployed in production.

---

# 29. Spark Tracing Boundaries

Spark already provides rich engine-level observability:

- applications,
- jobs,
- stages,
- tasks,
- shuffle,
- executor/resource metrics,
- Spark UI.

Tracing complements this rather than replacing it.

A useful architecture is:

```text
Pipeline trace
   ↓
Spark application
   ↓
Spark transformation
   ↓
Storage write
```

The trace can answer:

> When did the Spark operation occur, and how long did the pipeline-level operation take?

Spark's native UI can answer deeper engine questions:

> Which stage had the largest shuffle?

> Which tasks were skewed?

> Which executor failed?

### Important granularity rule

Do **not** claim that every Spark task automatically becomes an OpenTelemetry span.

At large scale, representing every internal task as a trace span can be expensive and may be the wrong abstraction.

Use:

```text
traces → pipeline/service boundaries

Spark UI/metrics → engine internals
```

---

# 30. Database and Warehouse Tracing

Consider:

```text
pipeline.load
    ↓
warehouse.merge
```

A useful warehouse span may contain:

```text
operation = MERGE
duration = ...
status = OK
database/service = warehouse
dataset/table = orders
```

Only include table or dataset information when it is safe and useful.

### Sensitive SQL

Avoid putting this into traces:

```sql
SELECT *
FROM customers
WHERE email = 'alice@example.com'
```

Prefer:

```text
operation = customer_lookup
table = customers
```

or safe database instrumentation fields.

The objective is diagnosis without turning traces into a copy of sensitive application traffic.

---

# 31. Correlating Logs, Traces, and Metrics

A production debugging path can look like:

```text
Metrics
   ↓
Detect abnormal behavior
   ↓
Trace
   ↓
Locate slow/failing operation
   ↓
Logs
   ↓
Understand detailed failure
```

A structured log can include:

```json
{
  "timestamp": "2026-10-05T07:14:32Z",
  "level": "ERROR",
  "run_id": "orders:2026-10-05:prod",
  "trace_id": "4bf92f...",
  "span_id": "00f067...",
  "stage": "warehouse_load",
  "error": "timeout"
}
```

This lets an operator search logs from a trace.

### Why this matters

Without correlation:

```text
dashboard
logs
traces
```

are separate islands.

With correlation:

```text
dashboard
  ↓
trace
  ↓
span
  ↓
logs
```

becomes a single investigation workflow.

---

# 32. Metric Exemplars

An exemplar is a mechanism for associating an aggregate metric observation with a specific trace.

Conceptually:

```text
pipeline_duration histogram
        ↓
specific trace
```

This can create:

```text
Grafana metric
    ↓
trace
    ↓
span
    ↓
logs
```

### Why exemplars are useful

Metrics are aggregated.

A metric might tell you:

```text
p95 pipeline duration = 38 minutes
```

An exemplar can provide a representative trace that lets the engineer inspect an actual execution.

This is especially useful for latency investigation.

Exemplars are a correlation bridge—not a replacement for metrics or tracing.

---

# 33. OpenTelemetry Collector

The Collector is a vendor-neutral telemetry pipeline.

Architecture:

```text
Pipeline
   ↓
OTLP
   ↓
OpenTelemetry Collector
   ├── Receivers
   ├── Processors
   └── Exporters
          ↓
     Trace Backend
```

## Why use a Collector?

It can centralize:

- batching,
- filtering,
- redaction,
- enrichment,
- sampling,
- routing,
- backend export.

Without a Collector:

```text
Application → Backend
```

With one:

```text
Application → Collector → Backend
```

The second architecture often gives platform teams more control.

---

# 34. Collector Receivers

A receiver accepts telemetry.

An OTLP receiver allows the Collector to receive OTLP telemetry.

Conceptually:

```text
Application
   ↓
OTLP
   ↓
OTLP receiver
```

The Collector can expose suitable endpoints for OTLP over HTTP and/or gRPC according to the deployment configuration.

---

# 35. Collector Processors

Processors transform or control telemetry after reception.

Common conceptual uses include:

- batching,
- attribute modification,
- filtering,
- redaction,
- sampling,
- resource enrichment.

For example:

```text
receive
  ↓
redact
  ↓
sample
  ↓
batch
  ↓
export
```

### Why processors matter

Centralized processing provides a defense-in-depth layer.

Even if an application accidentally adds a sensitive attribute:

```text
application
   ↓
collector filtering/redaction
   ↓
backend
```

the collector can prevent or reduce exposure.

This is not a substitute for fixing the application.

---

# 36. Collector Exporters

An exporter sends processed telemetry to a backend.

Conceptually:

```text
Collector
   ↓
Exporter
   ↓
Tracing backend
```

The application remains relatively independent from the final backend.

This supports architecture such as:

```text
many pipelines
      ↓
central collector tier
      ↓
one or more approved telemetry destinations
```

---

# 37. Collector Configuration Example

A conceptual local configuration:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:

processors:
  batch:

exporters:
  debug:

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [debug]
```

The exact production configuration depends on the deployed Collector distribution and backend.

A production environment may add:

```text
memory protection
redaction/filtering
tail sampling
TLS
authentication
backend exporters
resource enrichment
```

### Production rule

Treat Collector configuration as production code:

- review it,
- version it,
- test it,
- protect credentials,
- monitor it.

---

# 38. Collector Redaction

Telemetry should not expose:

```text
passwords
API keys
access tokens
credit card numbers
raw PII
sensitive request bodies
secrets
```

Defense in depth:

```text
Application filtering
        +
Collector filtering/redaction
        +
Backend access control
```

### Application-side rule

Do not create sensitive attributes in the first place.

Bad:

```python
span.set_attribute("customer.email", email)
```

Better:

```python
span.set_attribute("customer.segment", segment)
```

when the segment is genuinely useful and non-sensitive.

### Important warning about hashing

Hashing does not automatically make data anonymous.

A deterministic hash of a low-entropy value may be reversible through guessing or dictionary attacks.

---

# 39. Tracing Backends

Common tracing backends include:

- Jaeger
- Grafana Tempo
- other OpenTelemetry-compatible systems.

The architecture remains:

```text
Application
   ↓
Collector
   ↓
Tracing backend
   ↓
Trace UI
```

This module does not depend on one vendor.

For local learning, choose one backend and focus on:

- finding traces,
- expanding spans,
- inspecting attributes,
- inspecting events,
- finding errors,
- navigating from metric → trace → log.

---

# 40. Sampling

A production platform may generate too much tracing data to retain every trace.

Sampling controls telemetry volume.

The key question is:

> Which traces are worth keeping?

Important approaches:

```text
Head sampling
Tail sampling
```

---

# 41. Head Sampling

Head sampling makes the decision early.

For example:

```text
new trace
   ↓
sample decision
   ↓
keep or drop
```

### Advantages

- lower telemetry volume,
- lower application/export overhead,
- simpler implementation.

### Limitation

The system may discard a trace before knowing whether it will become interesting.

Example:

```text
trace starts normally
  ↓
warehouse timeout occurs 30 minutes later
```

If the trace was dropped at the beginning, the failure may be invisible.

---

# 42. Tail Sampling

Tail sampling makes the decision after more of the trace is available.

For example:

```text
trace
 ↓
observe outcome
 ↓
keep if:
   error
   very slow
   critical pipeline
```

### Advantages

It can retain:

- failed traces,
- very slow traces,
- traces matching important criteria.

### Costs

Tail sampling requires more infrastructure because trace information must be retained long enough to make the decision.

A Collector is often part of this architecture.

---

# 43. Production Sampling Strategy

A realistic policy might be:

```text
Development:
    100%

Production:
    errors             → keep
    very slow traces   → keep
    critical pipelines → high percentage
    normal success     → sampled
```

Do not treat arbitrary percentages as universal standards.

Sampling should depend on:

- telemetry volume,
- business criticality,
- incident history,
- storage cost,
- performance overhead,
- regulatory requirements.

### Production principle

> Prefer retaining unusual and operationally valuable traces over retaining enormous volumes of ordinary successful executions.

---

# 44. Telemetry Security

Telemetry itself is a data asset.

Protect it with:

- access control,
- retention policy,
- encryption in transit,
- encryption at rest,
- redaction,
- filtering,
- secure backend configuration,
- auditability.

Potentially sensitive telemetry includes:

```text
PII
credentials
tokens
request bodies
SQL parameters
customer identifiers
internal host information
```

### Security layers

```text
Instrumentation
    ↓
Collector
    ↓
Backend
    ↓
Users
```

Every layer should be considered.

---

# 45. PII in Traces

Bad:

```python
span.set_attribute("customer.email", email)
```

Bad:

```python
span.set_attribute("authorization", bearer_token)
```

Bad:

```python
span.set_attribute("request.body", raw_payload)
```

Safer examples:

```text
customer.segment
customer.region
request.operation
dataset.name
```

where these are genuinely useful and permitted.

### Data minimization

Ask:

> Do we need this attribute to diagnose the system?

If not, do not collect it.

---

# 46. Tracing Overhead

Tracing has costs:

- CPU,
- memory,
- network,
- storage,
- export processing,
- backend indexing,
- query cost,
- application latency.

The wrong design can make the system less reliable.

### Trade-off

```text
More visibility
      ↕
More overhead
```

The goal is not maximum telemetry.

The goal is:

> **Useful, actionable, secure telemetry at sustainable cost.**

---

# 47. Why You Must Not Create Per-Record Spans

Suppose a streaming system processes:

```text
10 million records/hour
```

A bad design is:

```text
10 million records
      ↓
10 million spans
```

This can create enormous:

- CPU overhead,
- memory pressure,
- network traffic,
- storage,
- backend indexing,
- query complexity.

### Better design

```text
Consumer poll
    ↓
Batch processing
    ↓
Sink write
```

Use metrics for record-level aggregation:

```text
records_processed_total
records_rejected_total
processing_latency
```

Use traces for operational boundaries.

### Principle

> Traces represent meaningful operations; metrics represent high-volume aggregates.

---

# 48. High-Throughput Streaming Design

Consider:

```text
Kafka
 ↓
Consumer
 ↓
10 million events/hour
```

A reasonable tracing design might be:

```text
consumer.poll
    ↓
batch.process
    ↓
sink.write
```

rather than:

```text
event 1 → span
event 2 → span
event 3 → span
...
event 10,000,000 → span
```

For a selected sampled message or debugging scenario, additional detail may be introduced, but it should not become the default architecture.

### Kafka lag remains a metric

Tracing can show:

```text
batch.process = 8 minutes
```

Metrics can show:

```text
consumer_lag = 1.8 million messages
```

Both are valuable.

---

# 49. Trace Design for a Slow Pipeline

Suppose:

```text
Pipeline duration:
10 min → 48 min
```

The trace shows:

```text
pipeline.run                  48m
├── extract                    3m
├── transform                  5m
├── kafka.wait                30m
└── warehouse.load            10m
```

The investigation immediately narrows.

Instead of asking:

> Why is the pipeline slow?

the engineer asks:

> Why did the Kafka-related stage consume 30 minutes?

Then combine trace data with:

```text
Kafka lag metric
consumer logs
run metadata
deployment changes
```

This is the intended metrics → traces → logs workflow.

---

# 50. Trace Design for a Failed Pipeline

Consider:

```text
pipeline.run
├── extract
├── transform
└── warehouse
       ↓
      ERROR
```

The warehouse span can contain:

```text
status = ERROR
exception = TimeoutError
trace_id = ...
span_id = ...
run_id = ...
```

Structured logs can contain:

```json
{
  "level": "ERROR",
  "run_id": "orders:2026-10-05:prod",
  "trace_id": "4bf92f...",
  "span_id": "00f067...",
  "stage": "warehouse_load",
  "error": "TimeoutError"
}
```

The engineer can navigate:

```text
metric
 ↓
trace
 ↓
error span
 ↓
log
 ↓
run metadata
```

---

# 51. Complete Production Architecture

A production-style architecture can be:

```text
                    ┌────────────────────┐
                    │   Data Pipeline    │
                    │ Python/Airflow/... │
                    └─────────┬──────────┘
                              │
                             OTLP
                              │
                              ▼
                    ┌────────────────────┐
                    │ OpenTelemetry      │
                    │ Collector          │
                    │                    │
                    │ Receivers          │
                    │ Processors         │
                    │ Sampling/Redaction │
                    │ Exporters          │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ Tracing Backend    │
                    │ Jaeger / Tempo     │
                    └─────────┬──────────┘
                              │
                              ▼
                          Trace UI
```

Alongside:

```text
Metrics → Prometheus → Grafana
Logs   → Log backend → Log UI
```

And correlation:

```text
Metrics
  ↓
Trace
  ↓
Logs
  ↓
Run metadata
```

---

# 52. Hands-On Local Lab

## Objective

Build:

```text
Python API
   ↓
HTTPX
   ↓
Kafka Producer
   ↓
Kafka
   ↓
Kafka Consumer
   ↓
Processing
   ↓
Warehouse/storage
```

Instrument the pipeline using OpenTelemetry.

## Required capabilities

The lab should demonstrate:

- Python SDK,
- tracer provider,
- OTLP,
- manual spans,
- HTTP instrumentation,
- HTTP propagation,
- Kafka propagation,
- producer spans,
- consumer spans,
- processing spans,
- sink spans,
- errors,
- structured correlation,
- local Collector,
- local tracing backend.

## Example dependency set

```bash
uv add \
  opentelemetry-api \
  opentelemetry-sdk \
  opentelemetry-exporter-otlp \
  opentelemetry-instrumentation-httpx
```

Add the Kafka client and other integrations according to the implementation chosen.

## Conceptual Compose architecture

```yaml
services:
  pipeline:
    build: .
    depends_on:
      - kafka
      - otel-collector

  kafka:
    image: kafka:example

  otel-collector:
    image: otel/opentelemetry-collector-contrib:example

  tracing-backend:
    image: jaegertracing/all-in-one:example
```

The exact Kafka and Collector image versions should be pinned to versions approved by the project rather than copied as floating tags.

## Minimal Collector configuration

```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:

processors:
  batch:

exporters:
  debug:

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [debug]
```

For a real backend, replace the debug exporter with the backend's supported exporter.

## Lab success criteria

You should be able to:

1. Start the pipeline.
2. Trigger an HTTP request.
3. Publish a Kafka message.
4. Consume the message.
5. Process it.
6. Write to the sink.
7. Find the resulting trace.
8. Expand the span hierarchy.
9. Inspect attributes.
10. Inspect events.
11. Trigger an error.
12. Find the error span.
13. Find the correlated log.
14. Correlate with `run_id`.

---

# 53. Failure-Injection Lab

Failure injection proves whether your tracing architecture actually works.

## Failure 1 — Slow HTTP API

Inject:

```python
import time

time.sleep(10)
```

Expected:

```text
HTTP span duration ↑
pipeline duration ↑
```

The trace should identify the HTTP operation as the delay.

## Failure 2 — Kafka consumer delay

Inject:

```python
time.sleep(30)
```

during batch processing.

Expected:

```text
consumer processing span becomes slow
Kafka lag increases
pipeline freshness degrades
```

The trace explains *where* time is spent while Kafka metrics explain *how far behind* the consumer is.

## Failure 3 — Warehouse timeout

Inject:

```python
raise TimeoutError("warehouse unavailable")
```

Expected:

```text
warehouse span = ERROR
exception recorded
pipeline trace contains failure
structured log contains trace_id/span_id
```

## Failure 4 — Broken Kafka propagation

Temporarily remove:

```python
inject(headers)
```

Expected:

```text
producer trace
    ↓
Kafka
    X
consumer trace
```

The consumer may begin a separate trace rather than continuing the producer's context.

Restore injection and extraction.

## Failure 5 — Sensitive telemetry leakage

Intentionally add:

```python
span.set_attribute("customer.email", email)
```

Then identify it during a telemetry review and remove it.

Also demonstrate why this is unsafe:

```python
span.set_attribute("authorization", token)
```

The correct production fix is not merely to redact the backend view; it is to stop creating the sensitive attribute.

---

# 54. Production Debugging Workflow

Use this workflow:

```text
1. Detect abnormal metric
2. Navigate to trace
3. Identify slow/failing span
4. Inspect span attributes
5. Inspect span events
6. Inspect exception
7. Find correlated logs
8. Identify affected pipeline/run
9. Use run_id
10. Determine impact
11. Fix/recover
12. Verify telemetry
```

## Example

Metric:

```text
pipeline duration = 75 minutes
```

Trace:

```text
pipeline.run
└── kafka.process_batch = 48 minutes
```

Kafka metrics:

```text
consumer lag = 1.9M messages
```

Logs:

```json
{
  "run_id": "orders:2026-10-05:prod",
  "trace_id": "4bf92f...",
  "stage": "kafka.process_batch",
  "message": "warehouse write retrying"
}
```

Run metadata:

```text
status = SUCCESS
duration = 75m
rows_read = 12M
rows_written = 12M
```

The pipeline technically succeeded, but downstream freshness was violated.

The investigation now focuses on:

```text
warehouse write saturation
```

rather than the API.

---

# 55. Common Mistakes

## 1. Instrumenting everything manually

**Why it happens:** Developers assume more spans mean more observability.

**Why dangerous:** Excessive spans increase overhead and noise.

**Correct approach:** Use automatic instrumentation for supported libraries and manual instrumentation for meaningful pipeline operations.

## 2. Instrumenting nothing

**Why it happens:** Teams assume auto-instrumentation understands business semantics.

**Why dangerous:** The system may expose HTTP calls but not `extract`, `transform`, or `load`.

**Correct approach:** Combine automatic and manual instrumentation.

## 3. No context propagation

**Why dangerous:** Services appear as disconnected traces.

**Fix:** Verify W3C context propagation across every distributed boundary.

## 4. Broken Kafka propagation

**Why dangerous:** Producer and consumer executions cannot be correlated.

**Fix:** Inject context into Kafka headers and extract it on the consumer side.

## 5. One span per record

**Why dangerous:** High-throughput systems can generate millions or billions of spans.

**Fix:** Trace batches and operational boundaries; use metrics for record aggregates.

## 6. High-cardinality attributes

Examples:

```text
customer_id
order_id
request_id
```

These may make trace search and backend storage expensive.

Use them only when justified and understand the backend's indexing behavior.

## 7. PII in span attributes

**Fix:** Apply data minimization and allowlists.

## 8. Secrets in HTTP headers

**Fix:** Never export authorization headers or tokens by default.

## 9. Full request bodies in traces

**Fix:** Record operation metadata, not sensitive payloads.

## 10. No sampling strategy

**Fix:** Define production retention and sampling policy before scale makes the problem urgent.

## 11. No Collector

A Collector is not mandatory for every small system, but central processing becomes valuable when you need:

- routing,
- redaction,
- sampling,
- batching,
- centralized policy.

## 12. Exporting directly to many backends

This couples application code to multiple destinations.

Prefer:

```text
application → Collector → approved backends
```

when the platform requires centralized control.

## 13. No resource attributes

Without service identity, traces become difficult to interpret.

Always establish useful resource information.

## 14. Inconsistent semantic conventions

Inconsistent names make cross-team dashboards and queries harder.

Use standard conventions where applicable.

## 15. Ignoring trace/log correlation

A trace without detailed logs can leave the final diagnosis difficult.

Correlate:

```text
trace_id
span_id
run_id
```

where appropriate.

## 16. Treating tracing as a replacement for metrics

Metrics remain superior for:

- aggregation,
- rates,
- SLOs,
- high-volume counts.

## 17. Excessive overhead

If tracing causes production instability, the design has failed.

Tune:

- sampling,
- span granularity,
- batching,
- exporter behavior,
- attribute volume.

## 18. Keeping all production traces forever

Tracing retention should match:

- operational need,
- cost,
- security,
- compliance,
- incident investigation requirements.

---

# 56. Testing OpenTelemetry Instrumentation

Observability itself must be tested.

## Test 1 — Span creation

Verify that the pipeline root span exists.

## Test 2 — Span attributes

Verify:

```text
pipeline.name
pipeline.run_id
```

are present where required.

## Test 3 — Error status

A failed operation should produce:

```text
status = ERROR
```

when appropriate.

## Test 4 — Exception recording

Verify the expected exception is recorded.

## Test 5 — Context propagation

Test:

```text
producer
  ↓
message headers
  ↓
consumer
```

and verify that the consumer receives the intended context.

## Test 6 — Sensitive attribute protection

Ensure prohibited fields are absent.

Example:

```python
assert "authorization" not in exported_attributes
assert "customer.email" not in exported_attributes
```

## Test 7 — Sampling behavior

Test that:

- normal traces can be sampled,
- errors are retained under the production policy,
- slow traces are retained where required.

---

# 57. Practical Instrumentation Test Pattern

A testing strategy can use an in-memory span exporter or another test exporter appropriate to the installed OpenTelemetry SDK version.

Conceptually:

```python
def test_pipeline_creates_root_span(exporter):
    run_pipeline()

    spans = exporter.get_finished_spans()

    names = {span.name for span in spans}

    assert "pipeline.run" in names
```

Test attributes:

```python
root = next(
    span for span in spans
    if span.name == "pipeline.run"
)

assert root.attributes["pipeline.name"] == "orders_daily"
```

Test failures:

```python
assert root.status.status_code.name == "ERROR"
```

The exact test-exporter setup should follow the OpenTelemetry SDK version pinned by the project.

---

# 58. Production Design Exercises

## Scenario A — API → Kafka → Python → Warehouse

Design:

```text
root span
producer span
consumer span
processing span
warehouse span
```

Explain:

- context propagation,
- asynchronous boundary,
- attributes,
- errors,
- logs,
- metrics.

### Expert direction

```text
API request
  ↓
kafka.publish
  ↓
consumer.process
  ↓
warehouse.write
```

Use Kafka headers for propagation and avoid per-message attribute explosion.

---

## Scenario B — Airflow → Spark → Object Storage → Warehouse

Answer:

- What should the root span be?
- Which operations should be child spans?
- What belongs in Spark UI/metrics instead?
- How do you correlate the run?

### Expert direction

```text
pipeline.run
├── airflow.task
├── spark.operation
└── warehouse.write
```

Use Spark-native telemetry for task/stage internals.

---

## Scenario C — High-volume Kafka stream

Question:

> Why should you not create one span per event?

### Expert answer

Because trace volume grows with event volume. At millions of events per hour, per-event spans can overwhelm the application, collector, network, backend, and storage.

Prefer:

```text
consumer batch
processing batch
sink operation
```

plus metrics for event-level aggregates.

---

## Scenario D — PII-heavy customer platform

Question:

> What telemetry should be blocked?

### Expert answer

At minimum review:

```text
customer email
phone
raw addresses
payment data
authentication tokens
request bodies
sensitive SQL parameters
```

Use data minimization, allowlists, redaction, access controls, retention, and encryption.

---

## Scenario E — Multi-service data platform

Question:

> Where should the Collector live?

### Expert answer

It can be deployed as:

- local/sidecar collector,
- node/agent collector,
- gateway collector,
- centralized collector tier,

depending on platform topology and requirements.

A common production pattern is:

```text
application
   ↓
local/agent collector
   ↓
gateway collector
   ↓
backend
```

The correct architecture depends on scale, network topology, security boundaries, and operational requirements.

---

# 59. Production Trade-offs

## Accuracy vs cost

Keeping every trace provides maximum visibility but can become prohibitively expensive.

## Visibility vs overhead

More spans increase diagnostic detail but also increase application and backend overhead.

## Sampling vs completeness

Sampling reduces cost but means some executions are not retained.

## Debuggability vs privacy

More attributes can make debugging easier while increasing the risk of sensitive-data exposure.

## Automatic vs manual instrumentation

Automatic instrumentation reduces coding effort; manual instrumentation captures domain semantics.

## Application exporter vs Collector

Direct export can be simple for small deployments. A Collector provides centralized control and policy.

## Fine-grained spans vs aggregate metrics

Spans are powerful for operations. Metrics are better for high-volume aggregates.

## More telemetry vs useful telemetry

The correct question is:

> What operational decision will this telemetry improve?

---

# 60. Checkpoints

## Checkpoint — Fundamentals

You should be able to explain:

1. What is a trace?
2. What is a span?
3. What is a trace ID?
4. What is a span ID?
5. What is a parent span?
6. What is a child span?

**Answers**

1. A distributed logical execution represented by related spans.
2. A timed operation within that execution.
3. An identifier for the complete trace.
4. An identifier for one span.
5. The containing operation.
6. The nested operation.

## Checkpoint — OpenTelemetry

1. What is OpenTelemetry?
2. API vs SDK?
3. What is OTLP?
4. What does a tracer provider do?

**Answers**

1. A vendor-neutral telemetry framework and ecosystem.
2. The API is the instrumentation-facing interface; the SDK provides implementation/configuration.
3. OpenTelemetry Protocol.
4. It configures how traces are produced, processed, sampled, and exported.

## Checkpoint — Propagation

1. Why is context propagation needed?
2. What is W3C Trace Context?
3. How does HTTP propagate context?
4. How does Kafka propagate context?

**Answers**

1. So downstream operations can remain correlated with the originating trace.
2. A standard for carrying distributed trace context.
3. Typically through HTTP headers such as `traceparent`.
4. Through Kafka message headers.

## Checkpoint — Production

1. Why not one span per record?
2. Why use sampling?
3. Why protect telemetry?
4. Why use a Collector?

**Answers**

1. High-throughput systems would generate excessive telemetry.
2. To control volume, cost, and overhead while retaining useful evidence.
3. Telemetry can contain sensitive operational or customer data.
4. To centralize processing such as batching, filtering, redaction, sampling, routing, and export.

---

# 61. Senior Data Engineering Interview Preparation

## 1. What is distributed tracing?

**Answer:** A telemetry technique that follows one logical operation across distributed components using related spans and propagation context.

## 2. Trace vs span?

**Answer:** A trace is the complete distributed operation; a span is one timed operation within it.

## 3. Trace ID vs span ID?

**Answer:** The trace ID identifies the complete execution; the span ID identifies one operation within it.

## 4. What is context propagation?

**Answer:** Carrying trace context across process or service boundaries so downstream operations can be associated with the originating trace.

## 5. What is W3C Trace Context?

**Answer:** A standardized propagation mechanism using fields such as `traceparent` and `tracestate`.

## 6. API vs SDK?

**Answer:** Application instrumentation uses the API; the SDK provides the implementation and configuration for generating/exporting telemetry.

## 7. What is OTLP?

**Answer:** OpenTelemetry Protocol, used to transmit telemetry between components.

## 8. Why use a Collector?

**Answer:** It centralizes telemetry processing, batching, filtering, redaction, sampling, routing, and export.

## 9. Auto vs manual instrumentation?

**Answer:** Auto-instrumentation captures supported library operations; manual instrumentation captures application and pipeline semantics.

## 10. How would you trace Kafka?

**Answer:** Create producer/consumer spans and propagate trace context through Kafka message headers, while respecting asynchronous messaging semantics.

## 11. How would you trace Airflow?

**Answer:** Correlate the DAG/pipeline execution with a root trace and task spans, then connect external HTTP, Spark, storage, and warehouse operations.

## 12. How would you trace Spark?

**Answer:** Use tracing for pipeline/application-level boundaries and Spark's native UI/metrics for detailed stage/task/executor analysis.

## 13. Head vs tail sampling?

**Answer:** Head sampling decides early; tail sampling decides after more trace information is available and can preferentially retain errors or slow traces.

## 14. Why not sample all errors with head sampling?

**Answer:** A head decision occurs before the system knows whether the future execution will fail, so a later error may already have been discarded.

## 15. Why not one span per Kafka event?

**Answer:** At high throughput, the telemetry volume becomes operationally and financially expensive. Trace batches and meaningful operations instead.

## 16. What should never be placed in traces?

**Answer:** Secrets, authentication tokens, passwords, payment information, raw PII, and sensitive payloads unless a specifically approved, protected design requires them.

## 17. How do metrics and traces work together?

**Answer:** Metrics detect aggregate abnormalities; traces identify the specific operation and timing behind those abnormalities.

## 18. How do logs and traces work together?

**Answer:** Trace IDs and span IDs let engineers move from a failing span to detailed structured log events.

## 19. What is an exemplar?

**Answer:** A link from an aggregate metric observation to representative trace context.

## 20. What is a production tracing architecture?

**Answer:** Application instrumentation → OTLP → Collector → sampling/redaction/processing → tracing backend, with correlation to metrics, logs, and run metadata.

---

# 62. Final Assessment

## Basic

1. Define distributed tracing.
2. Define a trace.
3. Define a span.
4. Explain parent and child spans.
5. Explain trace ID and span ID.
6. Explain span attributes.
7. Explain span events.
8. Explain span status.
9. Explain exception recording.
10. Explain OpenTelemetry.

## Intermediate

1. Configure a Python tracer provider.
2. Create a root pipeline span.
3. Create child task spans.
4. Add safe attributes.
5. Record an exception.
6. Configure OTLP export.
7. Instrument HTTPX.
8. Explain HTTP context propagation.
9. Explain Kafka header propagation.
10. Correlate `run_id` and `trace_id`.

## Advanced

1. Design a Collector pipeline.
2. Explain receivers, processors, and exporters.
3. Design head sampling.
4. Design tail sampling.
5. Design a Kafka tracing architecture.
6. Design Airflow/Spark tracing boundaries.
7. Design metrics/logs/traces correlation.
8. Design telemetry redaction.
9. Test propagation.
10. Test error instrumentation.

## Production / Senior

1. A pipeline succeeds but takes 75 minutes instead of 12. Design the investigation.
2. A Collector is overloaded. Diagnose likely causes.
3. A new instrumentation release creates millions of spans. Explain how you would recover.
4. A trace contains customer PII. Design the remediation.
5. Kafka producer and consumer traces are disconnected. Diagnose propagation.
6. A warehouse span is slow but the warehouse reports normal query time. Explain what additional evidence you need.
7. Design sampling for a billion-event/day streaming platform.
8. Design tracing for multi-region data pipelines.
9. Define what belongs in traces versus metrics.
10. Explain how you would prove that tracing improves incident response.

---

# 63. Final Production Incident Challenge

## Scenario

A critical production data pipeline normally completes in:

```text
12 minutes
```

It suddenly takes:

```text
75 minutes
```

The pipeline technically succeeds, but downstream consumers experience delayed data.

You have:

- pipeline metrics,
- run metadata,
- structured logs,
- OpenTelemetry traces,
- Kafka metrics,
- warehouse metrics.

## Investigation

### Step 1 — Metrics

Metrics show:

```text
pipeline_duration = 75 minutes
freshness SLO = violated
```

### Step 2 — Find trace

The run metadata provides:

```text
run_id = orders:2026-10-05:prod
trace_id = 4bf92f...
```

### Step 3 — Inspect span hierarchy

The trace shows:

```text
pipeline.run                     75m
├── extract                       4m
├── kafka.publish                 1m
├── kafka.process_batch          48m
│   └── transform                 6m
└── warehouse.load               22m
```

The largest delay is downstream processing.

### Step 4 — Inspect Kafka metrics

Kafka reports:

```text
consumer lag = 1.9M messages
```

This confirms that the consumer is falling behind.

### Step 5 — Inspect warehouse span

The warehouse span contains repeated operations:

```text
warehouse.write
warehouse.retry
warehouse.retry
warehouse.retry
```

### Step 6 — Inspect structured logs

Search:

```text
trace_id = 4bf92f...
span_id = ...
run_id = orders:2026-10-05:prod
```

The logs show:

```text
warehouse connection pool saturated
retrying write
```

### Step 7 — Determine root cause

The evidence points to:

```text
warehouse saturation
    ↓
write latency
    ↓
consumer processing slows
    ↓
Kafka lag grows
    ↓
pipeline freshness degrades
```

The trace narrowed the problem from:

```text
"Pipeline is slow."
```

to:

```text
"Warehouse writes are saturating the consumer's processing path."
```

### Step 8 — Recovery

Possible actions:

1. Stabilize warehouse capacity.
2. Reduce retry amplification.
3. Restore consumer throughput.
4. Allow Kafka lag to drain.
5. Verify warehouse correctness.
6. Verify data freshness.
7. Confirm SLO recovery.

### Step 9 — Prevent recurrence

Investigate:

- warehouse connection-pool sizing,
- concurrency,
- query performance,
- retry policy,
- backpressure,
- capacity planning,
- alert thresholds.

### Engineering lesson

Tracing did not replace:

```text
Kafka metrics
warehouse metrics
run metadata
logs
```

It connected them into an execution-level investigation.

---

# 64. Glossary

| Term | Meaning |
|---|---|
| Observability | Ability to understand system state from emitted evidence |
| Distributed tracing | Following one logical operation across distributed components |
| Trace | Collection of related spans representing an execution |
| Span | Timed operation within a trace |
| Root span | Top-level span in a trace |
| Child span | Nested span under a parent |
| Trace ID | Identifier for the complete trace |
| Span ID | Identifier for one span |
| Context | Information used to correlate execution |
| Context propagation | Carrying context across process/service boundaries |
| W3C Trace Context | Standardized trace-context propagation mechanism |
| `traceparent` | HTTP-style propagation field containing trace context |
| OpenTelemetry | Vendor-neutral telemetry framework/ecosystem |
| OpenTelemetry API | Instrumentation-facing API |
| OpenTelemetry SDK | Implementation/configuration layer |
| Tracer provider | SDK component responsible for tracer configuration |
| OTLP | OpenTelemetry Protocol |
| Instrumentation | Code/integration that produces telemetry |
| Auto-instrumentation | Instrumentation supplied automatically by integrations |
| Manual instrumentation | Application-defined spans and telemetry |
| Collector | Telemetry processing and routing service |
| Receiver | Collector component that accepts telemetry |
| Processor | Collector component that transforms/filters/samples telemetry |
| Exporter | Collector component that sends telemetry onward |
| Sampling | Selecting which traces to retain |
| Head sampling | Sampling decision made early |
| Tail sampling | Sampling decision made after observing more trace information |
| Semantic conventions | Standardized telemetry attribute names and meanings |
| Exemplar | Link between an aggregate metric observation and trace context |
| Span event | Timestamped event within a span |
| Span status | Operational status of a span |
| Context propagation | Mechanism for maintaining distributed trace relationships |

---

# 65. Final Learning Checklist

```text
[ ] Explain distributed tracing
[ ] Explain trace
[ ] Explain span
[ ] Explain trace ID
[ ] Explain span ID
[ ] Explain parent/child spans
[ ] Explain span attributes
[ ] Explain span events
[ ] Explain span status
[ ] Record exceptions
[ ] Explain OpenTelemetry
[ ] Explain API vs SDK
[ ] Configure Python OpenTelemetry
[ ] Configure tracer provider
[ ] Create manual spans
[ ] Configure OTLP
[ ] Explain auto-instrumentation
[ ] Instrument HTTPX
[ ] Understand database/cloud instrumentation
[ ] Explain context propagation
[ ] Explain W3C Trace Context
[ ] Propagate context over HTTP
[ ] Propagate context over Kafka
[ ] Trace producer → Kafka → consumer
[ ] Design pipeline traces
[ ] Correlate run_id and trace_id
[ ] Understand orchestrator tracing
[ ] Understand Spark tracing boundaries
[ ] Correlate warehouse operations
[ ] Correlate metrics/logs/traces
[ ] Explain exemplars
[ ] Explain OpenTelemetry Collector
[ ] Explain receivers
[ ] Explain processors
[ ] Explain exporters
[ ] Implement redaction
[ ] Protect PII and secrets
[ ] Explain head sampling
[ ] Explain tail sampling
[ ] Design a sampling strategy
[ ] Use semantic conventions
[ ] Control tracing overhead
[ ] Avoid per-record spans
[ ] Test instrumentation
[ ] Perform failure injection
[ ] Debug a slow pipeline
[ ] Design production tracing architecture
```

---

# 66. Roadmap Coverage Audit

This module explicitly covers the supplied Topic 02 roadmap requirements.

## Fundamentals

- Traces
- Spans
- Parent/child/root spans
- Trace ID
- Span ID
- Span attributes
- Span events
- Span status
- Error recording

## OpenTelemetry

- Python SDK
- Tracer provider
- Resources
- OTLP
- Auto-instrumentation
- Manual instrumentation

## Instrumentation

- HTTP/HTTPX
- Database/cloud clients
- Pipeline steps
- Airflow/orchestrator context
- Spark boundaries
- Kafka

## Propagation

- Context
- W3C Trace Context
- `traceparent`
- HTTP propagation
- Kafka header propagation

## Correlation

- Metrics
- Logs
- Traces
- Exemplars
- `run_id`
- `trace_id`

## Collector

- Receivers
- Processors
- Exporters
- Redaction
- Sampling
- Batching

## Sampling

- Head sampling
- Tail sampling
- Production strategy

## Security

- PII
- Secrets
- Tokens
- Request bodies
- SQL parameters
- Redaction
- Access control
- Retention
- Encryption

## Performance

- CPU
- Memory
- Network
- Storage
- Export overhead
- Sampling
- High-throughput design
- Avoiding per-record spans

## Production

- Failure injection
- Debugging
- Testing
- Operational trade-offs
- End-to-end architecture
- Production incident challenge

---

# 67. Writing and Engineering Principles

For every difficult concept, use this progression:

```text
Simple explanation
      ↓
Why it exists
      ↓
Real-world example
      ↓
Architecture
      ↓
Code
      ↓
How it works
      ↓
Failure mode
      ↓
Production trade-offs
      ↓
Best practice
```

The module deliberately avoids turning OpenTelemetry into a protocol-internals course.

The target is a Data Engineer who can **design, implement, debug, secure, and operate tracing in real data platforms**.

---

# 68. Accuracy Rules

OpenTelemetry integrations change over time.

For production implementation:

1. Pin compatible package versions.
2. Check the integration documentation for the deployed version.
3. Prefer stable APIs.
4. Test instrumentation in CI.
5. Separate conceptual architecture from version-specific syntax.
6. Do not assume every Airflow, Spark, Kafka, database, or cloud integration behaves identically.
7. Do not claim that an integration automatically creates spans for operations it does not actually instrument.
8. Do not present uncertain library syntax as guaranteed.

The most important architecture is stable:

```text
Application
   ↓
Instrumentation
   ↓
OpenTelemetry SDK
   ↓
OTLP
   ↓
Collector
   ↓
Processing / Sampling / Redaction
   ↓
Tracing Backend
```

---

# 69. Production Security Rule

Never intentionally place these directly into telemetry:

```text
Passwords
API keys
Bearer tokens
Secrets
Credit card numbers
Raw PII
Sensitive request bodies
Sensitive SQL parameters
```

Telemetry requires:

```text
Access control
Retention policy
Encryption
Redaction
Filtering
Monitoring
```

### Final security principle

> **Do not make telemetry the easiest place for an attacker or unauthorized employee to retrieve sensitive information.**

---

# 70. Final Engineering Principles

1. **Metrics tell you what is happening; traces show where an execution traveled and spent time; logs explain detailed events.**
2. **A trace should represent a meaningful distributed operation.**
3. **A span should represent a meaningful timed operation.**
4. **Use manual instrumentation for pipeline semantics.**
5. **Use automatic instrumentation for supported library boundaries.**
6. **Propagate context across every distributed boundary that should remain correlated.**
7. **Use W3C Trace Context where applicable.**
8. **Use Kafka headers for messaging context propagation.**
9. **Keep `run_id` and `trace_id` conceptually distinct and correlate both.**
10. **Use metrics for high-volume aggregates.**
11. **Never create one trace span per high-throughput record by default.**
12. **Use a Collector when centralized telemetry policy is valuable.**
13. **Sample normal traffic while preserving operationally important traces.**
14. **Protect telemetry as a sensitive data asset.**
15. **Minimize attributes instead of collecting everything.**
16. **Correlate metrics, traces, logs, and run metadata.**
17. **Test instrumentation itself.**
18. **Inject failures deliberately.**
19. **Design tracing around operational questions, not tool features.**
20. **The goal is useful, actionable, secure telemetry at sustainable cost.**

---

## Connection to the Next Topic

Topic 02 establishes distributed tracing.

The next topic, **03 — Alerting and On-Call for Data**, turns observability signals into operational action:

```text
Metrics
   +
Logs
   +
Traces
   ↓
Detection
   ↓
Alert
   ↓
On-call response
   ↓
Incident handling
```

Tracing answers:

> **Where did the execution go, and where did it spend its time?**

Alerting answers:

> **When should an engineer be interrupted, and what should they do next?**


## Roadmap Audit Note — Pipeline Tracing

**Pipeline tracing** is explicitly covered through root pipeline spans, task/step spans, external-service spans, and storage/warehouse spans.
