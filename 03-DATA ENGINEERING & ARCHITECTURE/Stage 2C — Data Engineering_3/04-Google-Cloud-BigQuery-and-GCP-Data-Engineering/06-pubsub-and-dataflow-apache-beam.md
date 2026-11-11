# Pub/Sub and Dataflow (Apache Beam)

**Roadmap location:** `Stage 2C — Data Engineering_3/04-Google-Cloud-BigQuery-and-GCP-Data-Engineering/06-pubsub-and-dataflow-apache-beam.md`  
**Level:** Beginner → Intermediate → Advanced  
**Primary language:** Python with the Apache Beam SDK  
**Lab root:** `experiments/06_pubsub_dataflow/`

> **Execution status:** This lesson and its code examples have been statically reviewed. The DirectRunner tests and cloud deployment have **not** been executed in this environment. Cloud examples contain placeholders and require a configured Google Cloud project. Verify SDK versions, region support, IAM, quotas, and pricing before deployment.

---

## 1. Learning objectives and prerequisites

By the end of this lesson, you will be able to:

- Design Pub/Sub topics and subscriptions for pull, push, BigQuery export, and Cloud Storage export.
- Explain message acknowledgements, retention, replay, ordering keys, attributes, retry policies, and dead-letter topics.
- Distinguish Pub/Sub delivery from Beam processing semantics and sink commit guarantees.
- Build Beam pipelines with `PCollection`, `PTransform`, `ParDo`, `GroupByKey`, `CoGroupByKey`, `Combine`, and side inputs.
- Use the Beam Python SDK for batch and streaming pipelines.
- Read files from Cloud Storage and write structured data to BigQuery.
- Test transforms with `TestPipeline`, `assert_that`, and deterministic test data.
- Use event timestamps, fixed/sliding/session/global windows, triggers, watermarks, and allowed lateness correctly.
- Build Pub/Sub-to-BigQuery processing with validation, dead-letter handling, deduplication, and reconciliation.
- Deploy Dataflow jobs, including Flex Templates, and understand autoscaling, Streaming Engine, and shuffle.
- Explain stateful `DoFn`s, timers, state cost, and the boundaries of exactly-once claims.
- Diagnose watermark/system lag, throughput limits, hot keys, fusion, worker sizing, and sink bottlenecks.
- Choose among Beam/Dataflow, Spark Structured Streaming, Flink, and direct Pub/Sub export subscriptions.

### Prerequisites

You should already know:

- Python functions, iterators, type hints, exceptions, JSON parsing, packaging, and unit tests.
- SQL aggregates, partitioned tables, and BigQuery schemas.
- Cloud Storage, service accounts, IAM, `gcloud`, and Application Default Credentials.
- Basic streaming concepts: event time, processing time, late events, retries, and idempotency.
- Topic 04 ingestion patterns: explicit schemas, quarantine, replay, reconciliation, and the BigQuery Storage Write API.
- Topic 03 cost controls: partition filters, query dry runs, and avoiding unnecessary scans.

### Lab prerequisites

For the local-only section:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install "apache-beam[gcp]==2.77.0" pytest
```

Beam 2.77.0 is used as a reproducible example pin because the current Beam reference documentation lists that release. Confirm that the selected Python version and all transitive packages are supported by the chosen Beam release before production pinning.

For cloud exercises, also install and authenticate the Google Cloud CLI, enable the required APIs, select a region, and configure a budget alert. A local DirectRunner run does not need Pub/Sub, Dataflow, or BigQuery resources.

---

## 2. Event-driven architecture fundamentals

An event-driven architecture separates event production from event consumption. A producer publishes a fact or state change; one or more consumers process it independently.

```text
Application / device / CDC producer
               |
               v
          Pub/Sub topic
          /     |      \
         v      v       v
    Dataflow   BigQuery  Cloud Storage
    + Beam     export    export
       |
       v
 parse -> validate -> timestamp -> window -> aggregate
       |                                      |
       v                                      v
  dead-letter path                       BigQuery table
```

Use Pub/Sub when producers and consumers need asynchronous decoupling, buffering, fan-out, and managed message delivery. Use Dataflow when messages need nontrivial transformation, event-time windows, joins, state, enrichment, aggregation, or multiple outputs. If the requirement is simply to export compatible messages to a BigQuery table or Cloud Storage without complex processing, a Pub/Sub export subscription may be simpler and less costly than running a Dataflow job.

### Separate the reliability boundaries

A streaming pipeline crosses multiple independent systems:

1. **Publisher:** did the producer publish once, or retry and publish the same business event twice?
2. **Pub/Sub:** did the subscription deliver a message, and was it acknowledged?
3. **Beam/Dataflow:** did the runner process the record and commit internal results?
4. **Transform code:** is custom code deterministic and safe when retried?
5. **Sink:** did the BigQuery or other write commit, and can a retry duplicate the result?
6. **Business logic:** does the result represent one business event, or one delivery attempt?

These are different guarantees. Exactly-once processing in one layer does not automatically create end-to-end exactly-once business outcomes across all systems. Use stable event IDs, idempotent writes, sink-specific guarantees, and reconciliation.

### Pub/Sub versus Kafka

| Dimension | Pub/Sub | Kafka |
|---|---|---|
| Operational model | Fully managed Google Cloud messaging service | Usually managed Kafka service or self-managed cluster |
| Consumer model | Subscription with acknowledgement / redelivery | Consumer groups and offset commits |
| Parallelism | Service-managed scaling; ordering keys can constrain ordering | Partition count and partition assignment are central to parallelism |
| Replay | Retention and seek/replay controls on subscriptions/topics | Replay by offset while records remain retained |
| Ordering | Ordering keys and region constraints; not a universal global order | Ordering within a partition |
| Ecosystem | Tight integration with GCP services | Broad Kafka ecosystem and portable Kafka-native architecture |
| Best fit | GCP-native event delivery and managed integration | Existing Kafka estate, partition/retention controls, Kafka ecosystem, portability needs |

Neither is universally superior. Compare throughput, retention, replay, ordering, operational skills, networking, costs, ecosystem, and cross-cloud needs.

---

## 3. Pub/Sub architecture and message lifecycle

### Topics, subscriptions, and messages

- **Topic:** named stream of published messages.
- **Subscription:** named delivery state and configuration for one topic. Different subscriptions receive independent copies of messages; multiple consumers on the same subscription share work.
- **Message:** payload bytes plus optional attributes, publish timestamp, and a Pub/Sub message ID.
- **Acknowledgement:** confirms that a subscriber has completed processing a delivery attempt. If acknowledgement is missing or late, Pub/Sub may redeliver.
- **Retention:** controls how long messages remain available for a subscription or topic, subject to service configuration.
- **Replay/seek:** allows a subscription to seek to an earlier point when the required messages are still retained.
- **Ordering key:** requests ordering for messages sharing a key, subject to documented regional and subscriber constraints.
- **Retry policy:** redelivers after a negative acknowledgement or expired acknowledgement deadline; exponential backoff can reduce pressure during transient failures.
- **Dead-letter topic:** receives messages that exceed a configured delivery-attempt threshold, if dead-lettering is correctly configured and permissions are in place.

Default Pub/Sub delivery is at least once and messages may be redelivered. A subscriber should be idempotent. Do not assume a successful acknowledgement prevents every possible future duplicate.

### Subscription patterns

| Pattern | Delivery path | Use when | Main caveat |
|---|---|---|---|
| Pull | Subscriber requests messages | You control the consumer and flow control | Consumer must manage acknowledgement and concurrency |
| Push | Pub/Sub sends HTTPS requests to an endpoint | A reachable HTTP service is the consumer | Endpoint health, auth, response codes, and push backoff matter |
| BigQuery export subscription | Pub/Sub writes messages to an existing BigQuery table | Payloads already match a supported schema and require little transformation | At-least-once behavior; schema compatibility, IAM, and quotas matter |
| Cloud Storage export subscription | Pub/Sub exports messages to Cloud Storage | Durable file export is enough | Output format, file rotation, delivery latency, and downstream file processing matter |
| Dataflow subscriber | Beam reads Pub/Sub and transforms before writing | Need event-time aggregation, validation, joins, deduplication, or multiple sinks | Dataflow adds runtime cost and operational responsibility |

Topic 04 explains the BigQuery Storage Write API and ingestion semantics. A direct BigQuery subscription is not a substitute for a Dataflow pipeline when you need cross-message aggregation, event-time windows, or complex validation.

### Retention and replay

Retention is finite and configured. Subscription retention defaults and maximums can change; consult the current Pub/Sub documentation before choosing a replay window. If acknowledged messages are not retained, you cannot assume you can seek back to them later. Replay is not a substitute for a long-term immutable archive when audit or regulatory requirements need longer retention.

A safe replay plan defines:

- How far back messages must be retained.
- Whether the replay runs on the same subscription or a dedicated replay subscription.
- Whether output is overwritten, merged, or versioned.
- How duplicate effects are prevented.
- How replay completion is reconciled and audited.

### Dead-letter topic and retry policy

Configure dead-letter handling at the subscription when appropriate, but do not rely on it as the only error-handling path. Pub/Sub dead-lettering depends on the configured delivery-attempt threshold and service-agent permissions; the observed count is best effort. In Dataflow, some failures occur after the source message has already been acknowledged, so use an explicit in-pipeline dead-letter output for parse/validation and recoverable transform errors.

Use exponential backoff for transient subscriber failures. Do not use negative acknowledgements as a general-purpose scheduling mechanism. A poison message that fails permanently should be isolated and investigated, not retried forever.

### Message attributes

Attributes are string key/value metadata outside the payload. Common attributes include `event_id`, `schema_version`, `producer`, `tenant`, `event_type`, and a source trace ID. Keep large or sensitive values out of attributes. Attribute-based deduplication is only as good as the producer's stable identity contract.

### IAM checklist

Exact roles vary by operation. At minimum, identify separate identities for:

- Producer: permission to publish to the input topic.
- Pipeline launcher: permission to create Dataflow jobs and use the worker service account.
- Dataflow worker service account: permission to consume from the subscription/topic, write BigQuery tables, write dead-letter messages, and access staging/temp buckets.
- Dataflow service agent: required service-agent permissions, typically provisioned by Google when the service is enabled.
- Template builder: permission to push the container image to Artifact Registry and write the template spec to Cloud Storage.

Avoid granting Owner/Editor broadly. Verify the current IAM role requirements for Dataflow, Pub/Sub, BigQuery, Artifact Registry, and Cloud Storage.

---

## 4. Apache Beam programming model

Apache Beam describes a data-processing pipeline independently of a particular runner. Dataflow is Google's managed runner for Beam; the DirectRunner is useful for local development and tests but is not a performance or production-equivalence guarantee.

### Core abstractions

- **`PCollection`:** distributed collection of elements. It can be bounded (batch) or unbounded (streaming).
- **`PTransform`:** reusable operation that consumes and produces collections.
- **`ParDo`:** applies a `DoFn` to elements, supporting multiple outputs and per-element logic.
- **`GroupByKey`:** groups values by key. In streaming, it requires a meaningful windowing strategy and can cause a shuffle.
- **`CoGroupByKey`:** groups multiple keyed collections together, useful for joins and enrichment.
- **`Combine` / `CombinePerKey`:** combines values efficiently, often using partial aggregation before the shuffle.
- **Side input:** a smaller dataset made available to a transform, such as a reference mapping or configuration snapshot. A side input must fit its intended materialization/refresh model; it is not a free unlimited database lookup.
- **Runner:** executes the pipeline. DirectRunner and Dataflow differ in deployment, scaling, service integrations, and operational behavior.

Example:

```python
with beam.Pipeline() as pipeline:
    totals = (
        pipeline
        | "ReadNumbers" >> beam.Create([("web", 3), ("app", 5), ("web", 2)])
        | "SumByChannel" >> beam.CombinePerKey(sum)
    )
```

Expected result: `("web", 5)` and `("app", 5)` in no guaranteed output order.

### `GroupByKey` versus `Combine`

Use `GroupByKey` when you need all values for a key, such as a bounded set of records for a join. Use `CombinePerKey` when the goal is a reduction like sum, count, min, max, or a custom associative accumulator. A combine can reduce data movement because partial results can be computed before the shuffle. Neither transform automatically solves a hot key when one key dominates the workload.

### `CoGroupByKey`

```python
left = pipeline | "Left" >> beam.Create([("u1", "purchase"), ("u2", "view")])
right = pipeline | "Right" >> beam.Create([("u1", "gold"), ("u3", "silver")])

joined = ({
    "events": left,
    "customers": right,
} | "JoinByUser" >> beam.CoGroupByKey())
```

The grouped value for each key contains an iterable for each input label. Convert those iterables into a deliberate join shape and define behavior for missing matches. In production, large joins may require partitioning, a side input, or a different storage/processing strategy.

### Side inputs

Side inputs work well for a bounded reference table or small configuration snapshot. Consider refresh cadence, size, and consistency. A side input is not a transactional join with a live database. For large or rapidly changing reference data, consider a keyed join, external lookup service with caching and rate limits, or a storage system designed for that access pattern.

### Batch versus streaming

A bounded `PCollection` can complete after all input is processed. An unbounded collection needs windowing, triggers, and a policy for late data. A transform that is fine for batch may be incomplete or unbounded in streaming if it uses a global window without a trigger/termination strategy.

---

## 5. Batch processing and unit testing

### Local batch pipeline: Cloud Storage JSONL to BigQuery

Batch is the right starting point when files arrive periodically and the latency requirement allows it. Use explicit schemas, validate records, and avoid treating a successful load as proof of data correctness.

A simple bounded Beam pipeline can read newline-delimited JSON from GCS, parse valid records, and write to BigQuery. Use the same validation function as the streaming pipeline where practical. For a production batch pipeline, add a dead-letter file/table, deterministic run identifiers, source manifest, row-count reconciliation, and a retry-safe target strategy.

Illustrative batch pattern:

```python
import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.gcp.bigquery import WriteToBigQuery

SCHEMA = {
    "fields": [
        {"name": "event_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "event_ts", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "event_type", "type": "STRING", "mode": "REQUIRED"},
        {"name": "amount", "type": "FLOAT", "mode": "REQUIRED"},
    ]
}

def parse_json_line(line):
    obj = json.loads(line)
    return {
        "event_id": str(obj["event_id"]),
        "event_ts": obj["event_ts"],
        "event_type": str(obj["event_type"]),
        "amount": float(obj["amount"]),
    }

options = PipelineOptions()
with beam.Pipeline(options=options) as p:
    (
        p
        | "ReadJSONL" >> beam.io.ReadFromText("gs://YOUR_BUCKET/events/*.jsonl")
        | "ParseJSON" >> beam.Map(parse_json_line)
        | "WriteBigQuery" >> WriteToBigQuery(
            table="YOUR_PROJECT_ID:streaming_lab.batch_events",
            schema=SCHEMA,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            method=WriteToBigQuery.Method.FILE_LOADS,
            custom_gcs_temp_location="gs://YOUR_BUCKET/bq-temp/",
        )
    )
```

This is a minimal bounded example, not the full validated streaming lab. It appends rows and therefore is not automatically idempotent on retry. For a production batch, write to a run-scoped staging table or use a deterministic load/merge design before publishing the final result.

### Testing with `TestPipeline` and `assert_that`

Test transforms locally before connecting to cloud services. `assert_that` materializes the collection being tested and is intended for tests, not production processing.

```python
import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

def test_combine_per_key():
    with TestPipeline() as p:
        output = (
            p
            | beam.Create([("web", 2), ("app", 1), ("web", 3)])
            | beam.CombinePerKey(sum)
        )
        assert_that(output, equal_to([("web", 5), ("app", 1)]))
```

Write tests for:

- Valid JSON payloads.
- Missing required fields and invalid types.
- Invalid timestamps and future timestamps.
- Duplicate event IDs.
- Conflicting payloads with the same event ID.
- Boundary timestamps at a window edge.
- Late events within and beyond allowed lateness.
- Empty input, high-volume keys, and unexpected event types.
- Sink schema mismatches and write failures (integration tests in a disposable project).

Use `TestStream` to test watermark advances, event timestamps, triggers, and late elements. Test deterministic business logic with the DirectRunner; use a small cloud integration test to validate service identity, connector, region, and sink behavior.

---

## 6. Event time, windows, triggers, and watermarks

### Three clocks

- **Event time:** when the event happened according to the producer.
- **Processing time:** when a worker processes the element.
- **Ingestion/publish time:** when a service such as Pub/Sub receives the message.

These timestamps answer different questions. A click that happened at 10:00 but was uploaded at 10:07 belongs to the 10:00 event-time window if event time is trusted. Processing-time windows would classify it based on when the pipeline processed it.

Validate event timestamps: timezone, parseability, plausible skew, and source clock quality. An untrusted producer timestamp can make a watermark appear stuck or cause records to be considered late.

### Window types

| Window | Definition | Typical use | Trade-off |
|---|---|---|---|
| Fixed | Non-overlapping windows of a fixed duration | Events per minute or per hour | Simple and efficient; boundary semantics must be clear |
| Sliding | Fixed duration with a slide interval; windows overlap | Rolling metrics | One event can contribute to multiple windows, increasing work and output |
| Session | Windows group activity separated by an inactivity gap | User sessions | Windows are data-dependent and can merge when late events arrive |
| Global | One unbounded logical window | Global aggregates or explicitly triggered output | Requires explicit trigger/termination semantics for unbounded streams |

Example fixed window:

```python
events | beam.WindowInto(beam.window.FixedWindows(60))
```

This creates 60-second event-time windows, not processing-time windows.

Other Beam window constructors:

```python
# Sliding windows: 5-minute window, advanced every 1 minute.
sliding = events | beam.WindowInto(beam.window.SlidingWindows(300, 60))

# Session windows: merge activity separated by less than 30 minutes.
sessions = events | beam.WindowInto(beam.window.Sessions(30 * 60))

# Global window: one logical window; an unbounded stream needs an explicit
# trigger/accumulation policy or it may not emit useful results.
global_window = events | beam.WindowInto(
    beam.window.GlobalWindows(),
    trigger=beam.trigger.Repeatedly(
        beam.trigger.AfterProcessingTime(60)
    ),
    accumulation_mode=beam.trigger.AccumulationMode.DISCARDING,
)
```

The examples illustrate API shape, not a universal trigger policy. Sliding windows multiply the number of window memberships; session windows may merge; and global-window triggers must be designed around the desired emission and accumulation semantics.

### Watermarks

A watermark is the runner's estimate that it has processed events up to a point in event time. It is an estimate, not a proof that no older event will ever arrive. Source backlog, out-of-order delivery, retries, stuck workers, and old event timestamps can hold a watermark back.

### Triggers and allowed lateness

A trigger determines when a window emits results. A watermark-based trigger commonly emits when the watermark passes the window end. A late firing can emit updates when additional events arrive after that point, if the window's allowed lateness and trigger policy permit it. The accumulation mode determines whether panes contain accumulated results or only new results.

Allowed lateness is a retention/processing policy for late window data, not a guarantee that late data is always recoverable. Data arriving beyond allowed lateness may be dropped from that window. Some source connectors or sinks can have their own failure and delivery behavior.

Illustrative Beam pattern:

```python
windowed = (
    events
    | "WindowByMinute" >> beam.WindowInto(
        beam.window.FixedWindows(60),
        trigger=beam.trigger.AfterWatermark(
            late=beam.trigger.AfterProcessingTime(30)
        ),
        allowed_lateness=120,
        accumulation_mode=beam.trigger.AccumulationMode.ACCUMULATING,
    )
)
```

This requests a late firing after processing-time delay when late data arrives. Exact firing timing depends on runner behavior and watermark progression. A production pipeline must also define how downstream tables handle multiple panes: append every pane with a pane identifier, or use an upsert/merge strategy keyed by window and group. Blindly appending each update can overcount.

### Fixed-window aggregation output contract

For the lab, output is a **window result**, not a unique raw event. Each row has:

- `window_start`: event-time window start (UTC timestamp).
- `window_end`: event-time window end (UTC timestamp).
- `event_type`: grouping key.
- `event_count`: number of deduplicated accepted events.
- `amount_sum`: sum of accepted event amounts.
- `pane_index`: Beam pane index for updates.
- `is_late`: whether the pane is a late pane.
- `processed_at`: processing timestamp for observability.

Because triggers can emit more than one pane, a table of append-only pane outputs is an audit/diagnostic stream, not automatically a single current aggregate per window. To maintain a current snapshot, use a deterministic merge key such as `(window_start, event_type)` and an explicit pane/version ordering rule. Validate that rule with the sink and recovery strategy.

---

## 7. Reliable streaming pipeline design

### Recommended stages

```text
Pub/Sub
  |
  v
Read messages (payload + attributes)
  |
  v
Parse JSON + validate schema
  |                     \
  | valid                \ invalid
  v                       v
assign event timestamp   explicit DLQ output
  |
  v
deduplicate by stable event ID
  |
  v
fixed event-time windows
  |
  v
CombinePerKey / aggregate
  |
  v
BigQuery Storage Write API
  |
  v
reconciliation + alerts + replay runbook
```

Use a stable event contract. For this lab:

```json
{
  "event_id": "evt-000123",
  "event_ts": "2026-10-19T10:15:20Z",
  "event_type": "purchase",
  "amount": 42.5,
  "source": "demo"
}
```

Required fields:

| Field | Type | Rule |
|---|---|---|
| `event_id` | string | Stable business identity; same logical event must reuse it on retries |
| `event_ts` | RFC 3339 timestamp | UTC recommended; validate parsing and plausible range |
| `event_type` | string | Non-empty; use a controlled vocabulary where possible |
| `amount` | number | Finite numeric value; example assumes non-negative amounts |
| `source` | string | Producer identifier for debugging |

Malformed records go to a separate dead-letter topic/table with original payload, error code/message, source message ID, attributes, and observed timestamp. Do not silently drop malformed data.

### Duplicates: two identities

- **Transport duplicate:** same Pub/Sub message is redelivered. Dataflow's Pub/Sub connector and streaming mode can deduplicate by Pub/Sub message ID.
- **Business duplicate:** producer publishes the same `event_id` again as a new Pub/Sub message. The Pub/Sub message IDs differ. You need a stable event ID, an attribute-based deduplication feature with its documented scope, or application/sink-level deduplication.

The lab includes both duplicate payloads and a duplicate `event_id`. The demonstration pipeline deduplicates by event ID **within the same event-time window**. This is intentionally not a global deduplication guarantee. For production, choose a deduplication state store and retention policy that match the maximum retry/replay horizon, or deduplicate downstream using a durable unique key. Stateful deduplication has state storage and expiration costs.

### BigQuery sink semantics

For streaming writes, Beam's BigQuery sink supports different methods. The Storage Write API offers exactly-once or at-least-once modes depending on the selected method/configuration. At-least-once writes can produce duplicate rows. The legacy streaming inserts path is not the preferred new-project default in current Dataflow guidance.

A robust pattern:

- Use a partitioned table and explicit schema.
- Choose `STORAGE_WRITE_API` when exactly-once sink semantics are required and supported by the selected pipeline configuration.
- Use `STORAGE_API_AT_LEAST_ONCE` only when duplicates are acceptable or deduplicated downstream.
- Store stable business keys and use downstream `MERGE`/deduplication if the end-to-end contract requires it.
- Monitor failed rows, schema mismatches, quota errors, and sink latency.
- Reconcile source event IDs and aggregate counts over bounded time ranges.

Exactly-once processing inside Dataflow does not mean custom `DoFn` code executes only once, nor does it guarantee that every external side effect is idempotent. An external HTTP call or non-idempotent database write inside a retried `DoFn` can happen more than once.

---

## 8. Dead-letter handling, retries, replay, and deduplication

### Dead-letter completeness

Use two layers of failure handling:

1. **Application DLQ:** parse/schema/business validation failures routed through a Beam side output to a durable sink.
2. **Transport/subscription dead-lettering:** Pub/Sub dead-letter topic for messages that cannot be delivered/acknowledged according to the subscription policy.

A Pub/Sub dead-letter topic does not automatically capture every exception thrown in later Dataflow transforms. Dataflow may acknowledge source messages after the first fused stage has successfully processed and persisted its side effects. If a later transform or sink fails, the runner's retry/recovery behavior applies; the message may not appear in the Pub/Sub dead-letter topic. Therefore, implement an explicit application DLQ for expected bad data and use runner/job monitoring for infrastructure failures.

### Retry classes

| Failure | Strategy |
|---|---|
| Temporary API/quotas/network issue | Retry with backoff; use connector/runner retry semantics |
| Invalid JSON/schema violation | Route to DLQ; do not retry unchanged payload forever |
| BigQuery schema mismatch | Fix schema/contract; replay quarantined data after validation |
| Transient BigQuery sink failure | Let the runner/connector retry; validate sink idempotency |
| Poison record repeatedly crashing a worker | Isolate using explicit error outputs or safe per-element error handling; monitor failure counts |
| Historical reprocessing | Use a dedicated replay/backfill path and idempotent output strategy |

Do not catch every exception and return `None`. That hides failures and creates silent data loss. Catch expected data errors around parsing and validation; let infrastructure failures surface to the runner unless a carefully designed recovery path exists.

### Replay procedure

1. Identify the affected time range and source subscription/topic.
2. Verify retention includes the required messages.
3. Decide whether to seek a subscription, use a replay subscription, or replay an immutable archive.
4. Choose a new output version or idempotent upsert key.
5. Run a small canary range and verify duplicate handling.
6. Monitor lag, throughput, sink errors, and costs.
7. Reconcile counts and event IDs.
8. Record replay range, job ID, code version, and result.

Replay can create duplicate business effects if the sink uses append-only semantics. Never replay into a production aggregate without an explicit replacement/upsert plan.

---

## 9. Dataflow deployment and runtime architecture

### Dataflow runner

Dataflow executes Beam graphs on managed workers. It handles worker provisioning, parallel execution, shuffles, checkpointing/state, retries, and integration with Cloud Monitoring. It is not identical to DirectRunner: local success cannot prove cloud IAM, network, region, autoscaling, connector, or sink behavior.

### Autoscaling

Autoscaling adjusts worker capacity based on pipeline workload and runner signals. It does not fix every bottleneck. A hot key can limit parallelism even when more workers are added. A slow sink or external service can dominate latency. Minimum/maximum workers, worker machine type, regional quotas, startup time, and cost affect results.

### Streaming Engine

Streaming Engine moves portions of streaming execution state/shuffle work into the Dataflow service rather than requiring workers to perform all stateful streaming operations locally. Availability and billing depend on job configuration and current product settings. It can improve operational scalability but is not a substitute for correct windows, key distribution, or sink capacity.

### Shuffle service

Shuffle redistributes keyed data for operations such as `GroupByKey` and joins. Large shuffles can increase latency and cost. `CombinePerKey` can reduce shuffle volume when partial aggregation is possible. A shuffle stage may reveal key skew or high cardinality.

### Flex Templates

A Flex Template packages a pipeline in a container image plus a JSON template specification in Cloud Storage. It allows a job to be launched without a developer environment. Template creation requires a reproducible image, pinned dependencies, declared parameters, staging/temp locations, and IAM for the launcher and worker identities.

Example build/run outline (fill in project, region, repository, bucket, and template values):

```bash
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="us-central1"
export BUCKET="YOUR_UNIQUE_BUCKET"
export REPOSITORY="dataflow-templates"
export IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/pubsub-aggregate:1.0.0"
export TEMPLATE="gs://${BUCKET}/templates/pubsub-aggregate.json"

gcloud services enable \
  dataflow.googleapis.com \
  pubsub.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  artifactregistry.googleapis.com \
  --project="${PROJECT_ID}"

gcloud dataflow flex-template build "${TEMPLATE}" \
  --image-gcr-path="${IMAGE}" \
  --sdk-language="PYTHON" \
  --flex-template-base-image="PYTHON3" \
  --py-path="." \
  --env="FLEX_TEMPLATE_PYTHON_PY_FILE=main.py" \
  --env="FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=requirements.txt" \
  --metadata-file="metadata.json"

gcloud dataflow flex-template run "pubsub-aggregate-$(date +%Y%m%d-%H%M%S)" \
  --template-file-gcs-location="${TEMPLATE}" \
  --region="${REGION}" \
  --staging-location="gs://${BUCKET}/staging" \
  --temp-location="gs://${BUCKET}/temp" \
  --parameters="input_subscription=projects/${PROJECT_ID}/subscriptions/YOUR_SUBSCRIPTION,output_table=${PROJECT_ID}:streaming_lab.window_aggregates,dead_letter_topic=projects/${PROJECT_ID}/topics/YOUR_DLQ_TOPIC" \
  --service-account-email="YOUR_DATAFLOW_WORKER_SA"
```

This build command uses the documented Python Flex Template base-image workflow to build/push the launcher image and create the template specification. Ensure the Artifact Registry repository exists, the build identity can push images, and the source/requirements/metadata files are present. The Flex Template metadata must define the runtime parameters. See the official Flex Template documentation for current flags and Python image requirements. Do not launch until IAM, table schema, region, and parameters are verified.

### Dataflow SQL and provided templates

Google Cloud has provided Dataflow templates for common ingestion/transformation patterns, and Dataflow SQL capabilities have varied by product generation and release. Treat “Dataflow SQL” as a capability to investigate rather than assume it is the default way to build new pipelines. For new custom event-time logic, Beam Python/Java SDK pipelines are the direct programming model. Evaluate provided templates first when their schema, error handling, and sink semantics match the requirement.

---

## 10. State, timers, and delivery guarantees

### Stateful `DoFn`s

Beam stateful processing lets a `DoFn` retain per-key state across elements, typically within a window and with runner-managed state semantics. Timers let a transform schedule work based on event time or processing time. Common uses include:

- Deduplicating by stable event ID for a bounded retention interval.
- Maintaining a per-key running counter or small state machine.
- Emitting an incomplete session after an inactivity timeout.
- Buffering small groups before emitting output.

State is not free. It consumes storage and checkpointing resources, requires key/window design, and can create hot keys. State cleanup depends on window expiration, allowed lateness, and the timer/state API. Do not keep an unbounded set of every event ID forever. Define a TTL or bounded deduplication horizon, and decide what happens when a replay exceeds that horizon.

### Timers

- **Event-time timer:** fires relative to the event-time watermark; if the watermark is held back, the timer can be delayed.
- **Processing-time timer:** fires according to processing-time progression; useful for operational timeouts but less deterministic for event-time completeness.
- **Timer output:** still subject to runner execution, retries, and sink semantics. Do not use a timer as a guarantee that no later event will arrive.

A stateful transform must be keyed and compatible with Beam's state/timer model. Test the transform with the DirectRunner where supported and validate behavior on Dataflow, since runner support and operational behavior can differ.

### Delivery semantics in one table

| Layer | Possible guarantee / behavior | What you still need |
|---|---|---|
| Pub/Sub default | At-least-once; possible redelivery | Idempotent consumer and stable business IDs |
| Pub/Sub exactly-once subscription feature | Applies to supported subscription delivery semantics; has constraints | Does not make arbitrary downstream side effects exactly once |
| Dataflow streaming mode | Exactly-once by default, or at-least-once mode by configuration | Align sink mode, deduplication, and cost/latency goals |
| Beam user `DoFn` | Code may be retried; side effects can repeat | Keep transforms deterministic; avoid non-idempotent external side effects |
| BigQuery Storage Write API sink | Sink method controls write semantics | Select method deliberately; validate schema and duplicate handling |
| Business event processing | Depends on all stages and key semantics | Durable event identity, idempotent upsert, audit/reconciliation |

For aggregation workloads, exactly-once mode is often a safer starting point. At-least-once mode can reduce latency and cost when duplicates are acceptable or handled downstream, but must be paired with a matching BigQuery write method. Measure the real workload before changing modes.

---

## 11. Monitoring, performance tuning, and cost control

### What to monitor

- Job state and failure/restart counts.
- Input throughput and backlog.
- Element counts and estimated bytes per `PCollection`/stage.
- System lag (time spent processing or waiting within the pipeline).
- Data watermark lag and output watermark progression.
- Worker CPU/memory, worker count, autoscaling changes, and disk use.
- BigQuery sink latency, failed rows, schema errors, Storage Write API quota errors.
- DLQ rate and error categories.
- Duplicate rate, late-event rate, window pane count, and source-to-sink reconciliation.
- Cost per million events or per business unit of output.

### Interpret watermark and system lag

- **System lag high:** records are spending too much time in the pipeline or waiting for resources/sinks.
- **Data watermark lag high:** the pipeline's estimate of event-time completeness is behind the latest input event time. A slow stage, backlog, old timestamps, retries, or out-of-order input may contribute.
- **High throughput but watermark stuck:** out-of-order timestamps or a single slow partition/key may hold the watermark back.
- **Growing Pub/Sub backlog:** source ingestion is exceeding sustained consumer throughput or the pipeline is failing.
- **Healthy input, slow BigQuery output:** inspect sink quotas, schema failures, write mode, and BigQuery-side metrics.

Use the Dataflow job graph and step-level metrics to locate the slow transform; worker logs and structured error counters help distinguish bad data from infrastructure failures. Alert on lag and failed jobs using Cloud Monitoring. A dashboard without actionable thresholds and a response owner is incomplete.

### Fusion

Fusion combines adjacent transforms into a stage to reduce overhead and improve efficiency. But it can make a failure or bottleneck less obvious in the graph. Add meaningful transform labels and use stage-level metrics. Do not add `Reshuffle` just to make a graph look more parallel.

### Hot keys

A hot key is a key that receives disproportionate traffic, limiting parallelism after a grouping/shuffle step. Diagnose it by examining key distributions and stage wall time/throughput.

Mitigation options:

1. **Pre-aggregate with `CombinePerKey`** when the operation is associative and can reduce records before shuffle.
2. **Salt the key** by adding a bounded shard number, combine within shards, then remove the salt and combine again. This changes grouping shape and requires a correct second aggregation.
3. **Use a side input** for a small reference dataset rather than a large keyed join, if size/refresh semantics fit.
4. **Change the data model** or use a more suitable storage/processing pattern if one key must remain strictly serialized.

Key salting is not universal. It adds a second aggregation and can change semantics for non-associative operations. It does not help if the final unsalted key is inherently sequential or the sink is the bottleneck.

### `Reshuffle`

`Reshuffle` can introduce a redistribution/boundary in a pipeline and may help in specific cases such as breaking fusion or redistributing work. It also adds overhead and can alter execution characteristics. It is not a universal hot-key fix, and the runner may optimize pipeline stages differently than expected. Use only after profiling and verifying correctness.

### Batching writes and worker sizing

- Batch records where the sink supports efficient batching; too-small writes increase request overhead.
- Keep row schemas consistent and validate before sink writes.
- Choose machine type and worker bounds from measured throughput, memory, CPU, and latency—not guesswork.
- Avoid overprovisioning workers for a sink-limited pipeline.
- Account for idle streaming-job cost, Streaming Engine, shuffle, network egress, BigQuery ingestion, and storage.
- Use labels and billing export for attribution.
- Stop test jobs and delete temporary resources after exercises.

### Cost-control workflow

1. Start with a small bounded or short-duration stream.
2. Set budget alerts and quotas; alerts are not hard spending caps.
3. Use a dedicated test dataset and short retention.
4. Record throughput, latency, worker count, sink mode, and cost.
5. Scale one variable at a time.
6. Compare cost per million accepted events and end-to-end latency.
7. Stop streaming jobs when not in use; streaming jobs may incur ongoing cost while idle.
8. Do not benchmark production-sized workloads without an explicit cost approval.

---

## 12. Beam, Spark Structured Streaming, and Flink comparison

| Dimension | Beam + Dataflow | Spark Structured Streaming / Dataproc | Apache Flink |
|---|---|---|---|
| Programming model | Portable Beam model; runner implements execution | Spark DataFrame/Dataset and streaming query model | Stateful stream-processing runtime and APIs |
| Managed GCP path | Dataflow runner | Dataproc clusters or Dataproc Serverless for Spark | Usually self-managed or a selected managed distribution |
| Batch + stream | One model for bounded and unbounded data | Batch and streaming integrated in Spark | Strong stream-first model; batch support depends on API/runtime |
| Event-time windows/state | Beam windows, triggers, timers, state | Watermarks, windows, stateful operations | Rich event-time and state/timer model |
| Operational control | Managed worker lifecycle and runner optimizations | More Spark environment/configuration control | Fine-grained stream runtime control, more platform operations unless managed |
| Portability | Beam pipeline can run on supported runners, but connectors/features vary | Spark code is portable across compatible Spark environments | Flink code portable across compatible Flink environments |
| Best fit | GCP-native streaming/batch pipelines with Beam portability and managed Dataflow | Existing Spark skills/code, lakehouse transformations, large batch or micro-batch analytics | Low-latency stateful streaming, event-driven applications, strong Flink ecosystem |
| Trade-offs | Runner-specific semantics, cloud cost, connector differences | Cluster/runtime tuning and micro-batch/continuous-mode constraints | Operational complexity, state backend and checkpoint tuning, deployment model |

Beam portability means the pipeline model is reusable, not that every connector, runner feature, state/timer behavior, or performance characteristic is identical everywhere. Dataflow is a good fit when GCP integration and managed operations matter. Dataproc is a good fit for Spark/Hadoop workloads, especially existing PySpark code and lakehouse processing. Topic 07 covers Dataproc in detail.

---

## 13. Hands-on lab and troubleshooting

The complete lab is organized as:

```text
experiments/06_pubsub_dataflow/
├── requirements.txt
├── main.py
├── test_main.py
├── publisher.py
├── sample_events.jsonl
├── metadata.json
├── README.md
└── Dockerfile
```

### 13.1 Event schema and sample payloads

`sample_events.jsonl`:

```json
{"event_id":"evt-001","event_ts":"2026-10-19T10:00:10Z","event_type":"purchase","amount":12.5,"source":"demo"}
{"event_id":"evt-002","event_ts":"2026-10-19T10:00:25Z","event_type":"view","amount":0,"source":"demo"}
{"event_id":"evt-001","event_ts":"2026-10-19T10:00:10Z","event_type":"purchase","amount":12.5,"source":"demo"}
{"event_id":"evt-003","event_ts":"2026-10-19T09:59:50Z","event_type":"purchase","amount":7,"source":"demo"}
{"event_id":"evt-bad","event_ts":"not-a-timestamp","event_type":"purchase","amount":5,"source":"demo"}
{"event_id":"evt-004","event_ts":"2026-10-19T10:01:15Z","event_type":"purchase","amount":19.5,"source":"demo"}
```

The duplicate `evt-001` is a business duplicate with the same payload and timestamp. `evt-003` is intentionally late relative to the example event-time progression. `evt-bad` is malformed and should be routed to the DLQ. Actual lateness in a live stream depends on the Pub/Sub source watermark and when the message is published, not just the timestamp text.

### 13.2 Dependencies

`requirements.txt`:

```text
apache-beam[gcp]==2.77.0
google-cloud-pubsub>=2.25,<3
pytest>=8,<9
```

Pin and lock dependencies for production. Verify Beam's Python compatibility and dependency constraints in the target build environment.

### 13.3 Pipeline source: `main.py`

This pipeline supports either `--input_file` for a bounded local exercise or `--input_subscription` for cloud streaming. It parses and validates JSON, sends invalid records to a DLQ, assigns event time, deduplicates by event ID within a fixed window, aggregates, and writes window/pane results to a partitioned BigQuery table.

```python
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any

import apache_beam as beam
from apache_beam.io.gcp.bigquery import WriteToBigQuery
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.transforms.window import TimestampedValue


BIGQUERY_SCHEMA = {
    "fields": [
        {"name": "window_start", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "window_end", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "event_type", "type": "STRING", "mode": "REQUIRED"},
        {"name": "event_count", "type": "INTEGER", "mode": "REQUIRED"},
        {"name": "amount_sum", "type": "FLOAT", "mode": "REQUIRED"},
        {"name": "pane_index", "type": "INTEGER", "mode": "REQUIRED"},
        {"name": "is_late", "type": "BOOLEAN", "mode": "REQUIRED"},
        {"name": "processed_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
    ]
}


def parse_timestamp(value: str) -> datetime:
    """Parse an RFC3339 timestamp and normalize it to UTC."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("event_ts must include a timezone")
    return parsed.astimezone(timezone.utc)


class ParseAndValidate(beam.DoFn):
    BAD = "bad_records"

    def process(self, raw: bytes | str | tuple, attributes: dict[str, str] | None = None):
        try:
            # The pipeline normalizes both file lines and Pub/Sub messages to
            # (payload, attributes). File lines use an empty attributes dict.
            if isinstance(raw, tuple) and len(raw) == 2:
                raw, attributes = raw
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            event = json.loads(raw)

            event_id = event.get("event_id")
            event_type = event.get("event_type")
            source = event.get("source", "unknown")
            event_ts = parse_timestamp(str(event["event_ts"]))
            amount = float(event["amount"])

            if not isinstance(event_id, str) or not event_id.strip():
                raise ValueError("event_id must be a non-empty string")
            if not isinstance(event_type, str) or not event_type.strip():
                raise ValueError("event_type must be a non-empty string")
            if not math.isfinite(amount) or amount < 0:
                raise ValueError("amount must be finite and non-negative")

            yield TimestampedValue(
                {
                    "event_id": event_id,
                    "event_ts": event_ts,
                    "event_type": event_type,
                    "amount": amount,
                    "source": str(source),
                },
                event_ts.timestamp(),
            )
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            yield beam.pvalue.TaggedOutput(
                self.BAD,
                {
                    "raw_payload": raw.decode("utf-8", errors="replace")
                    if isinstance(raw, bytes) else str(raw),
                    "error_type": type(exc).__name__,
                    "error_message": str(exc)[:1000],
                    "attributes": attributes or {},
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                },
            )


def dedup_key(event: dict[str, Any]):
    # Keep the full event as the value; this example assumes repeated event_id
    # values represent the same immutable business event.
    return event["event_id"], event


def choose_one(events):
    # A deterministic tie-breaker is required if an event_id can carry
    # conflicting payloads. This demo's duplicates are identical.
    return min(
        events,
        key=lambda e: (
            e["event_ts"].isoformat(),
            e["event_type"],
            e["amount"],
            e["source"],
        ),
    )


class FormatWindowAggregate(beam.DoFn):
    def process(
        self,
        element,
        window=beam.DoFn.WindowParam,
        pane=beam.DoFn.PaneInfoParam,
    ):
        event_type, values = element
        count, amount_sum = values
        yield {
            "window_start": datetime.fromtimestamp(
                window.start.to_utc_datetime().timestamp(), timezone.utc
            ).isoformat(),
            "window_end": datetime.fromtimestamp(
                window.end.to_utc_datetime().timestamp(), timezone.utc
            ).isoformat(),
            "event_type": event_type,
            "event_count": int(count),
            "amount_sum": float(amount_sum),
            "pane_index": int(pane.index),
            "is_late": bool(pane.is_late),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }


def build_pipeline(
    pipeline: beam.Pipeline,
    *,
    input_file: str | None,
    input_subscription: str | None,
    output_table: str,
    dead_letter_topic: str | None,
    window_seconds: int = 60,
    allowed_lateness_seconds: int = 120,
):
    if bool(input_file) == bool(input_subscription):
        raise ValueError("Set exactly one of input_file or input_subscription")

    if input_file:
        raw = pipeline | "ReadJSONL" >> beam.io.ReadFromText(input_file)
    else:
        raw = (
            pipeline
            | "ReadPubSub"
            >> beam.io.gcp.pubsub.ReadFromPubSub(
                subscription=input_subscription,
                with_attributes=True,
            )
            | "ExtractPubSubPayload"
            >> beam.Map(lambda msg: (msg.data, dict(msg.attributes or {})))
        )

    def parse_pair(item):
        if isinstance(item, tuple):
            payload, attrs = item
            # Preserve attributes for DLQ metadata. ParseAndValidate emits
            # valid records as TimestampedValue and invalid records as DLQ.
            return payload, attrs
        return item, {}

    parsed = (
        raw
        | "NormalizeInput" >> beam.Map(parse_pair)
        | "ParseAndValidate"
        >> beam.ParDo(
            ParseAndValidate()
        ).with_outputs(ParseAndValidate.BAD, main="valid")
    )

    valid = parsed.valid
    invalid = parsed.bad_records

    if dead_letter_topic:
        (
            invalid
            | "SerializeDLQ" >> beam.Map(lambda r: json.dumps(r, default=str))
            | "WriteDLQ"
            >> beam.io.gcp.pubsub.WriteToPubSub(
                topic=dead_letter_topic,
                with_attributes=False,
            )
        )
    else:
        # Local tests can inspect this output; cloud deployments should supply
        # a durable DLQ destination instead of dropping invalid data.
        _ = invalid | "CountBadRecords" >> beam.Map(lambda _: 1)

    windowed = (
        valid
        | "FixedEventTimeWindows"
        >> beam.WindowInto(
            beam.window.FixedWindows(window_seconds),
            trigger=beam.trigger.AfterWatermark(
                late=beam.trigger.AfterProcessingTime(30)
            ),
            allowed_lateness=allowed_lateness_seconds,
            accumulation_mode=beam.trigger.AccumulationMode.ACCUMULATING,
        )
    )

    deduplicated = (
        windowed
        | "KeyByEventId" >> beam.Map(dedup_key)
        | "ChooseOnePerEventId" >> beam.CombinePerKey(choose_one)
        | "DropEventIdKey" >> beam.Values()
    )

    totals = (
        deduplicated
        | "KeyByEventType" >> beam.Map(
            lambda e: (e["event_type"], (1, e["amount"]))
        )
        | "SumCountAndAmount"
        >> beam.CombinePerKey(
            beam.combiners.TupleCombineFn(
                sum,
                sum,
            )
        )
    )

    rows = totals | "FormatWindowRows" >> beam.ParDo(FormatWindowAggregate())

    rows | "WriteBigQuery" >> WriteToBigQuery(
        table=output_table,
        schema=BIGQUERY_SCHEMA,
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
        method=WriteToBigQuery.Method.STORAGE_WRITE_API,
        additional_bq_parameters={
            "timePartitioning": {"type": "DAY", "field": "window_start"},
            "clustering": {"fields": ["event_type"]},
        },
    )

    return parsed, rows


def run(argv: list[str] | None = None):
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file")
    parser.add_argument("--input_subscription")
    parser.add_argument("--output_table", required=True)
    parser.add_argument("--dead_letter_topic")
    parser.add_argument("--window_seconds", type=int, default=60)
    parser.add_argument("--allowed_lateness_seconds", type=int, default=120)
    known_args, pipeline_args = parser.parse_known_args(argv)

    options = PipelineOptions(pipeline_args)
    options.view_as(StandardOptions).streaming = bool(known_args.input_subscription)

    with beam.Pipeline(options=options) as pipeline:
        build_pipeline(
            pipeline,
            input_file=known_args.input_file,
            input_subscription=known_args.input_subscription,
            output_table=known_args.output_table,
            dead_letter_topic=known_args.dead_letter_topic,
            window_seconds=known_args.window_seconds,
            allowed_lateness_seconds=known_args.allowed_lateness_seconds,
        )


if __name__ == "__main__":
    run()
```

**Implementation review note:** Beam Python APIs evolve. Before production, run the test suite with the pinned SDK and verify `ReadFromPubSub`, `PubsubMessage`, `WriteToBigQuery.Method.STORAGE_WRITE_API`, pane metadata, and `time_partitioning` behavior for that version. If the selected SDK's `CombinePerKey` combiner or BigQuery sink signature differs, adapt it to the official reference and rerun tests. The cloud pipeline should use an explicit durable DLQ; the local-only branch without a DLQ is for test inspection only.

### 13.4 Local unit tests: `test_main.py`

The tests below focus on parsing/validation and bounded aggregation behavior. They should be run before any cloud deployment. They have not been executed here.

```python
import json

import apache_beam as beam
import pytest
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

from main import ParseAndValidate


def test_valid_event_is_emitted():
    raw = json.dumps({
        "event_id": "evt-1",
        "event_ts": "2026-10-19T10:00:00Z",
        "event_type": "purchase",
        "amount": 12.5,
        "source": "test",
    })
    with TestPipeline() as p:
        result = (
            p
            | beam.Create([raw])
            | beam.ParDo(ParseAndValidate()).with_outputs(
                ParseAndValidate.BAD, main="valid"
            )
        )
        assert_that(
            result.valid
            | beam.Map(lambda event: event["event_id"]),
            equal_to(["evt-1"]),
        )
        assert_that(
            result.bad_records,
            equal_to([]),
            label="NoBadRecords",
        )


def test_malformed_timestamp_routes_to_dlq():
    raw = json.dumps({
        "event_id": "evt-2",
        "event_ts": "not-a-time",
        "event_type": "purchase",
        "amount": 2.0,
    })
    with TestPipeline() as p:
        result = (
            p
            | beam.Create([raw])
            | beam.ParDo(ParseAndValidate()).with_outputs(
                ParseAndValidate.BAD, main="valid"
            )
        )
        assert_that(result.valid, equal_to([]), label="NoValidRecords")
        assert_that(
            result.bad_records | beam.Map(lambda r: r["error_type"]),
            equal_to(["ValueError"]),
            label="BadTimestamp",
        )
```

Run locally:

```bash
pytest -q
python main.py \
  --input_file=sample_events.jsonl \
  --output_table=YOUR_PROJECT_ID:streaming_lab.window_aggregates
```

The second command is not a fully local command because it writes to BigQuery and needs credentials. For a truly local-only test, use `TestPipeline` tests or add a local output sink that writes JSONL. Do not run a continuous streaming job with the DirectRunner and expect it to behave exactly like Dataflow.

### 13.5 Publish synthetic events: `publisher.py`

```python
import json
import os
import time
from datetime import datetime, timedelta, timezone

from google.cloud import pubsub_v1

PROJECT_ID = os.environ["PROJECT_ID"]
TOPIC_ID = os.environ["TOPIC_ID"]

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

now = datetime.now(timezone.utc).replace(microsecond=0)
events = [
    {
        "event_id": "evt-100",
        "event_ts": now.isoformat().replace("+00:00", "Z"),
        "event_type": "purchase",
        "amount": 25.0,
        "source": "publisher-demo",
    },
    {
        # Same business ID and payload, published again as a new Pub/Sub message.
        "event_id": "evt-100",
        "event_ts": now.isoformat().replace("+00:00", "Z"),
        "event_type": "purchase",
        "amount": 25.0,
        "source": "publisher-demo",
    },
    {
        # Event time is older than publish time; this exercises late-data behavior.
        "event_id": "evt-101",
        "event_ts": (now - timedelta(minutes=3)).isoformat().replace("+00:00", "Z"),
        "event_type": "purchase",
        "amount": 7.5,
        "source": "publisher-demo",
    },
    {
        "event_id": "evt-invalid",
        "event_ts": "not-a-timestamp",
        "event_type": "purchase",
        "amount": 3.0,
        "source": "publisher-demo",
    },
]

for event in events:
    future = publisher.publish(
        topic_path,
        json.dumps(event).encode("utf-8"),
        event_id=event["event_id"],
        schema_version="1",
    )
    print("published", event["event_id"], "message_id", future.result())

publisher.transport.close()
```

Install the publisher dependency from `requirements.txt`, set `PROJECT_ID` and `TOPIC_ID`, and run `python publisher.py`. Repeated business event IDs receive different Pub/Sub message IDs unless publisher/service semantics say otherwise. The pipeline's event-ID logic handles the demo duplicate within the same window.

### 13.6 BigQuery table and GCP resources

Use a dataset and table in the same supported location as the Dataflow job where required. Example schema:

```sql
CREATE SCHEMA IF NOT EXISTS `YOUR_PROJECT_ID.streaming_lab`
OPTIONS(location = 'US');

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT_ID.streaming_lab.window_aggregates` (
  window_start TIMESTAMP NOT NULL,
  window_end TIMESTAMP NOT NULL,
  event_type STRING NOT NULL,
  event_count INT64 NOT NULL,
  amount_sum FLOAT64 NOT NULL,
  pane_index INT64 NOT NULL,
  is_late BOOL NOT NULL,
  processed_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(window_start)
CLUSTER BY event_type;
```

The pipeline's sink must be configured to match this table schema and partitioning. If you pre-create the table, use the appropriate `CREATE_NEVER` disposition to avoid accidental schema drift; if you use `CREATE_IF_NEEDED`, verify the sink creates the partitioning and schema exactly as expected for the pinned Beam version.

Example resources:

```bash
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="us-central1"
export INPUT_TOPIC="events"
export INPUT_SUBSCRIPTION="events-dataflow-sub"
export DLQ_TOPIC="events-dlq"
export BUCKET="YOUR_UNIQUE_BUCKET"
export DATASET="streaming_lab"
export WORKER_SA="YOUR_DATAFLOW_WORKER_SA"

gcloud pubsub topics create "${INPUT_TOPIC}" --project="${PROJECT_ID}"
gcloud pubsub topics create "${DLQ_TOPIC}" --project="${PROJECT_ID}"

gcloud pubsub subscriptions create "${INPUT_SUBSCRIPTION}" \
  --topic="${INPUT_TOPIC}" \
  --min-retry-delay=10s \
  --max-retry-delay=600s \
  --project="${PROJECT_ID}"

bq --project_id="${PROJECT_ID}" mk --dataset --location=US "${DATASET}"
```

Choose one dataset-creation method: run the SQL DDL above **or** use `bq mk`, not both. Create the bucket and Artifact Registry repository before building a Flex Template. Example resource setup:

```bash
gcloud storage buckets create "gs://${BUCKET}" --location="${REGION}" --project="${PROJECT_ID}"
gcloud artifacts repositories create "${REPOSITORY}" \
  --repository-format=docker --location="${REGION}" --project="${PROJECT_ID}"
# Alternative to the SQL CREATE SCHEMA above:
bq --project_id="${PROJECT_ID}" mk --dataset --location=US "${DATASET}"
```

Create the dead-letter topic before configuring a subscription dead-letter policy. If configuring Pub/Sub dead-lettering, grant the Pub/Sub service agent the required permissions on the dead-letter topic and subscription. A Beam in-pipeline DLQ uses the worker identity to publish; grant it publish permission on the DLQ topic.

### 13.7 Run on Dataflow

Example command for the Python pipeline:

```bash
python main.py \
  --runner=DataflowRunner \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --temp_location="gs://${BUCKET}/temp" \
  --staging_location="gs://${BUCKET}/staging" \
  --service_account_email="${WORKER_SA}" \
  --streaming \
  --input_subscription="projects/${PROJECT_ID}/subscriptions/${INPUT_SUBSCRIPTION}" \
  --dead_letter_topic="projects/${PROJECT_ID}/topics/${DLQ_TOPIC}" \
  --output_table="${PROJECT_ID}:${DATASET}.window_aggregates"
```

The exact `PipelineOptions` flag names are SDK-version-sensitive; verify them against the pinned Beam release. The `--streaming` flag is parsed by Beam's standard options, and the custom `input_subscription`, `dead_letter_topic`, and `output_table` arguments are consumed by this script. For a long-running production job, add labels, worker bounds, machine type, network/subnetwork, streaming mode, and update/rollback strategy as required by your environment.

### 13.8 Flex Template packaging

`metadata.json` (example metadata shape; validate against current Flex Template schema):

```json
{
  "name": "PubSub event aggregation to BigQuery",
  "description": "Validate Pub/Sub JSON events, route invalid records to a DLQ, and aggregate valid events into fixed event-time windows.",
  "parameters": [
    {
      "name": "input_subscription",
      "label": "Input Pub/Sub subscription",
      "helpText": "Full subscription resource path",
      "isOptional": false
    },
    {
      "name": "output_table",
      "label": "BigQuery output table",
      "helpText": "Project:dataset.table",
      "isOptional": false
    },
    {
      "name": "dead_letter_topic",
      "label": "Dead-letter topic",
      "helpText": "Full Pub/Sub topic resource path",
      "isOptional": false
    }
  ]
}
```

For Python Flex Templates, use the current documented base-image or custom-image build flow. A typical Google-provided base-image approach sets the pipeline file and requirements file through the supported environment variables and includes the source/metadata. Do not assume that a Flex Template can be built from `metadata.json` alone: the container image must contain the executable pipeline and dependencies.

After the image and template specification are built and uploaded, launch it with `gcloud dataflow flex-template run`. Use a unique job name, correct region, staging/temp bucket, worker service account, and required parameters. Verify the current official Flex Template documentation for the exact build flags of the selected Beam SDK and Python image.

### 13.9 Hot-key experiment

Create a bounded dataset with a highly skewed key distribution:

```python
hot_data = (
    [("hot", 1)] * 100_000
    + [(f"key-{i}", 1) for i in range(1_000)]
)
```

First run `CombinePerKey(sum)` and inspect the graph/step metrics. The local DirectRunner is useful to prove logic but is not a reliable benchmark for Dataflow hot-key behavior. For a cloud experiment, use a small approved dataset and compare stage throughput, wall time, shuffle volume, and worker utilization.

For an associative sum, salting can distribute partial work:

```python
def add_shard(item, shard_count=16):
    key, value, sequence = item
    return (key, sequence % shard_count), value

def remove_shard(item):
    (key, _shard), subtotal = item
    return key, subtotal

# Conceptual two-stage aggregation:
# 1. key by (original_key, shard), combine sums.
# 2. remove shard, combine the partial sums again.
```

This is a mitigation pattern, not a universal fix. It increases a second aggregation stage and only preserves results when the partial operation is associative/commutative. Diagnose key skew first; a sink bottleneck or inherently sequential business rule will not be solved by salting.

### 13.10 Expected outcomes

- Valid events are parsed into the event schema.
- Malformed JSON/timestamps and invalid values go to the application DLQ.
- Identical event IDs in the same window are counted once by the demo's deduplication stage.
- Accepted events are grouped by `event_type` and fixed event-time window.
- BigQuery contains window start/end, aggregate values, pane index, late-pane flag, and processing timestamp.
- Late events may cause additional panes while allowed lateness and trigger behavior permit; events beyond the allowed-lateness horizon may not update the aggregate.
- Repeated pane rows are possible with accumulating triggers. Downstream consumers must not sum every pane row as if it were a distinct final aggregate.

### 13.11 Troubleshooting guide

| Symptom | Likely cause | Response |
|---|---|---|
| Pub/Sub backlog grows | Source rate exceeds pipeline/sink capacity, job failure, or subscription misconfiguration | Check source backlog, Dataflow throughput, worker logs, and BigQuery write metrics |
| Watermark stalls | Old/out-of-order timestamps, retries, slow stage, or source backlog | Inspect data watermark per stage, event timestamp distribution, and worker errors |
| System lag rises | Slow transform, worker resource pressure, shuffle, or sink bottleneck | Use the job graph and step metrics to find the stage; change one variable at a time |
| Duplicate aggregate output | Multiple panes appended, business duplicate IDs, or at-least-once sink semantics | Define pane upsert semantics, dedup by stable ID, or reconcile downstream |
| Invalid events disappear | No durable DLQ configured or exception caught and discarded | Configure application DLQ and alert on error counts |
| BigQuery write errors | Schema mismatch, permissions, quota, region, or write-method incompatibility | Verify schema, sink mode, IAM, quotas, and region |
| Hot key slows one stage | One key dominates grouped work | Measure key skew; pre-combine, salt associative keys, or change data model |
| Autoscaling adds workers but latency stays high | Key bottleneck, sink limit, external call, or shuffle | Locate bottleneck before raising worker bounds |
| Flex Template launch fails | Image/spec mismatch, wrong region, missing permissions, or invalid parameter names | Validate template metadata/image and service account access |
| Local tests pass, cloud job fails | IAM, network, region, quotas, connector, or runner differences | Run a small cloud integration test and inspect worker logs |

### 13.12 Cleanup

Stop the Dataflow job first, then remove lab resources only after confirming they are not shared:

```bash
gcloud dataflow jobs list --region="${REGION}" --project="${PROJECT_ID}"
# Cancel the lab job using its actual JOB_ID:
gcloud dataflow jobs cancel YOUR_JOB_ID \
  --region="${REGION}" --project="${PROJECT_ID}"

gcloud pubsub subscriptions delete "${INPUT_SUBSCRIPTION}" --project="${PROJECT_ID}"
gcloud pubsub topics delete "${INPUT_TOPIC}" --project="${PROJECT_ID}"
gcloud pubsub topics delete "${DLQ_TOPIC}" --project="${PROJECT_ID}"

bq --project_id="${PROJECT_ID}" rm -r -f "${PROJECT_ID}:${DATASET}"
```

Also delete the lab bucket contents, Artifact Registry image/repository, Flex Template spec, and any service account created exclusively for the lab. Do not delete shared production resources. Check current resource names before cleanup.

### 13.13 Cost precautions

- Use DirectRunner and tests before cloud deployment.
- Publish only a small number of synthetic events.
- Use a dedicated test dataset, topic, bucket, and Artifact Registry repository.
- Use a short-lived streaming job; stop it immediately after the experiment.
- Set budget alerts and review Dataflow, Pub/Sub, BigQuery, Cloud Storage, Artifact Registry, network, and Logging costs.
- Avoid running a hot-key test with millions of records unless approved.
- Avoid long retention and replay of acknowledged messages unless required.
- Use current pricing pages for region-specific estimates.

---

## 14. Knowledge checks with detailed answers

### Questions

1. What is the difference between a topic and a subscription?
2. Why is Pub/Sub delivery at least once by default, and what does acknowledgement mean?
3. How do pull, push, BigQuery, and Cloud Storage subscriptions differ?
4. What is the difference between a Pub/Sub message ID and a business event ID?
5. Why does exactly-once processing in Dataflow not guarantee exactly-once business side effects?
6. When would you use `CombinePerKey` instead of `GroupByKey`?
7. Why do unbounded pipelines need windows and triggers?
8. What does a watermark mean, and why can it be held back?
9. What does allowed lateness guarantee—and what does it not guarantee?
10. Why are an application DLQ and a Pub/Sub dead-letter topic not interchangeable?
11. What is a hot key, and when can key salting help?
12. Why is `Reshuffle` not a universal performance fix?
13. What should you inspect when system lag is high but input throughput remains healthy?
14. What changes when using the BigQuery Storage Write API's at-least-once method?
15. When is a direct Pub/Sub BigQuery subscription preferable to Dataflow?
16. What is the difference between Beam portability and identical behavior across runners?
17. Why is DirectRunner testing insufficient to prove production readiness?
18. When would Spark Structured Streaming or Flink be a better fit?

### Answers

1. A topic is the named destination to which producers publish. A subscription is a consumer's delivery state/configuration for that topic. Multiple subscriptions fan out independently; consumers on one subscription share its messages.
2. Pub/Sub retries when an acknowledgement is not received or a message is otherwise redelivered. Acknowledgement tells Pub/Sub the delivery was handled, but redelivery can still occur. Consumers should be idempotent.
3. Pull clients request messages; push delivers to an HTTPS endpoint; BigQuery export writes compatible messages to a table; Cloud Storage export writes messages to a bucket. Export subscriptions reduce custom consumer code but provide less transformation flexibility.
4. Pub/Sub message ID identifies a published message. A business event ID identifies the logical event. Publishing the same event twice can create two message IDs with the same business ID.
5. Custom `DoFn` code can be retried, and external side effects may repeat. A sink may also have at-least-once semantics. End-to-end correctness requires idempotent side effects, stable keys, and reconciliation.
6. Use `CombinePerKey` for reductions such as sum/count when partial aggregation is valid; use `GroupByKey` when the logic needs all values grouped together. Combine often reduces shuffle volume.
7. Unbounded streams never naturally finish, so the pipeline needs a policy for grouping elements by time and deciding when results are emitted. Global windows require explicit triggers and are not a default answer for infinite streams.
8. A watermark estimates the event-time frontier the runner believes is complete. It can lag because of backlog, out-of-order events, old timestamps, slow stages, or retries; it is not a proof that no older event will arrive.
9. Allowed lateness retains window state for a configured horizon so late data can update results within that horizon. It does not guarantee replay beyond retention, recovery after the horizon, or identical behavior from every sink.
10. Pub/Sub dead-lettering covers subscription delivery/acknowledgement failures subject to configuration. Dataflow can acknowledge a source message before a later transform/sink fails, so application-level errors need an explicit pipeline DLQ and infrastructure errors need runner monitoring.
11. A hot key dominates grouped work and reduces parallelism. Salting can spread an associative aggregation across shards and combine partial results later; it adds work and cannot fix every sink or sequential bottleneck.
12. `Reshuffle` adds redistribution overhead and can change execution behavior. Use it only after graph/metric evidence shows a specific need.
13. Inspect the job graph, step-level wall time, data watermark lag, worker CPU/memory, shuffle, retries, source backlog, and sink latency/errors. Find the bottleneck before adding workers.
14. The at-least-once Storage Write API mode can reduce latency/cost but may duplicate writes. Match the sink method to Dataflow streaming mode and deduplicate downstream if needed.
15. When messages already fit the BigQuery schema and need little transformation, cross-message aggregation is unnecessary, and direct export's delivery/cost constraints are acceptable.
16. Beam defines a portable pipeline model, but connectors, runner optimizations, state/timer support, and execution characteristics can differ by runner. Test the exact runner and connectors used in production.
17. DirectRunner does not reproduce GCP IAM, networking, quotas, autoscaling, Dataflow service behavior, or sink integration. It validates logic, not the entire deployed system.
18. Spark fits existing Spark/lakehouse transformations and teams invested in the Spark ecosystem. Flink can fit demanding stateful event-time streaming when its runtime capabilities justify the platform operations. Choose from workload and operational constraints, not brand preference.

---

## 15. Syllabus checkpoint

Mark an item complete only when you can demonstrate it.

- [ ] Explain Pub/Sub topics, subscriptions, pull/push/export delivery, acknowledgements, retention, replay, ordering, attributes, retry policies, and dead-letter topics.
- [ ] Compare Pub/Sub and Kafka for a specific workload.
- [ ] Explain `PCollection`, `PTransform`, `ParDo`, `GroupByKey`, `CoGroupByKey`, `Combine`, and side inputs.
- [ ] Build a bounded GCS-to-BigQuery Beam pipeline with an explicit schema and retry-safe output strategy.
- [ ] Test parsing, validation, grouping, and window logic with `TestPipeline` and `assert_that`.
- [ ] Explain event time versus processing time and implement fixed windows.
- [ ] Describe sliding, session, and global windows and their trade-offs.
- [ ] Explain watermarks, triggers, accumulating/discarding panes, and allowed lateness.
- [ ] Build Pub/Sub-to-BigQuery processing with explicit invalid-record DLQ and stable event identity.
- [ ] Distinguish transport duplicates from business duplicates.
- [ ] Explain Dataflow exactly-once and at-least-once modes, including sink boundaries.
- [ ] Explain stateful `DoFn`s, timers, state cleanup, and state costs.
- [ ] Deploy a small Dataflow job and package a Flex Template in a lab environment.
- [ ] Read the job graph and interpret system lag, data watermark lag, throughput, and worker logs.
- [ ] Diagnose hot keys and justify whether `CombinePerKey`, key salting, `Reshuffle`, or worker changes are appropriate.
- [ ] Compare Beam/Dataflow, Spark Structured Streaming, and Flink.
- [ ] Estimate costs, stop jobs, and clean up resources safely.

**Pass condition:** produce test results, a small deployed job (if cloud access is available), screenshots or logs for the job graph/metrics, a DLQ sample, a reconciliation query, and a written reliability decision. Reading the lesson alone is not sufficient.

---

## 16. Summary and transition to Topic 07

Pub/Sub provides managed asynchronous message delivery; Apache Beam defines the pipeline model; Dataflow runs Beam pipelines with managed scaling, state, shuffle, and operational tooling. Reliable streaming requires explicit event-time semantics, validation, dead-letter handling, duplicate strategy, sink-aware delivery guarantees, monitoring, replay procedures, and cost controls.

The most important distinction is that Pub/Sub acknowledgement, Dataflow processing semantics, custom code execution, and sink commit behavior are separate layers. Design end-to-end idempotency and reconciliation instead of assuming a single “exactly-once” switch solves every duplicate or failure.

**Transition to Topic 07 — Dataproc and Dataproc Serverless:** Topic 07 covers managed Spark/Hadoop processing on GCP. Use Dataflow/Beam when the pipeline benefits from Beam's unified bounded/unbounded model and Dataflow's managed streaming integration; use Dataproc when Spark/Hadoop compatibility, existing PySpark jobs, lakehouse processing, or Spark-specific libraries are central. For warehouse-native SQL transformations, BigQuery SQL may be simpler than either distributed engine.

---

## 17. Official documentation references

1. [Pub/Sub overview](https://cloud.google.com/pubsub/docs/overview) — topics, messages, subscriptions, and event-driven design.
2. [Pub/Sub subscription overview](https://cloud.google.com/pubsub/docs/subscription-overview) — acknowledgement, redelivery, subscription types, and default behavior.
3. [Choose a subscription type](https://cloud.google.com/pubsub/docs/subscriber) — pull, push, BigQuery, and Cloud Storage export subscriptions.
4. [Subscription properties](https://cloud.google.com/pubsub/docs/subscription-properties) — ordering, retry, dead-letter configuration, and retention properties.
5. [Subscription retry policy](https://cloud.google.com/pubsub/docs/subscription-retry-policy) — immediate retry and exponential backoff.
6. [Message retention](https://cloud.google.com/pubsub/docs/subscription-message-retention) — retention and replay prerequisites.
7. [BigQuery subscriptions](https://cloud.google.com/pubsub/docs/bigquery) — direct Pub/Sub-to-BigQuery export, delivery semantics, and quotas.
8. [Cloud Storage subscriptions](https://cloud.google.com/pubsub/docs/cloudstorage) — direct export to Cloud Storage.
9. [Apache Beam programming guide](https://beam.apache.org/documentation/programming-guide/) — core model, transforms, windowing, triggers, state, and timers.
10. [Beam Python SDK reference](https://beam.apache.org/releases/pydoc/current/) — current Python APIs and connector signatures.
11. [Beam testing utilities](https://beam.apache.org/releases/pydoc/current/apache_beam.testing.util.html) — `assert_that` and test helpers.
12. [Read from Pub/Sub to Dataflow](https://cloud.google.com/dataflow/docs/concepts/streaming-with-cloud-pubsub) — source deduplication, timestamps, ordering, acknowledgements, and explicit DLQ design.
13. [Dataflow exactly-once processing](https://cloud.google.com/dataflow/docs/concepts/exactly-once) — processing guarantees and limitations.
14. [Dataflow streaming modes](https://cloud.google.com/dataflow/docs/guides/streaming-modes) — exactly-once and at-least-once modes.
15. [Write from Dataflow to BigQuery](https://cloud.google.com/dataflow/docs/guides/write-to-bigquery) — sink methods, Storage Write API, and streaming trade-offs.
16. [Flex Template configuration](https://cloud.google.com/dataflow/docs/guides/templates/configuring-flex-templates) — template image and specification packaging.
17. [Run Flex Templates](https://cloud.google.com/dataflow/docs/guides/templates/run-flex-templates) — launch commands, parameters, and IAM.
18. [Dataflow job metrics](https://cloud.google.com/dataflow/docs/guides/using-monitoring-intf) — system lag, data freshness, and stage metrics.
19. [Cloud Monitoring for Dataflow](https://cloud.google.com/dataflow/docs/guides/using-cloud-monitoring) — dashboards, metrics, and alerts.
20. [Dataflow pricing](https://cloud.google.com/dataflow/pricing) — current resource and streaming cost model.
21. [Pub/Sub pricing](https://cloud.google.com/pubsub/pricing) — current message and storage charges.
22. [BigQuery pricing](https://cloud.google.com/bigquery/pricing) — ingestion, storage, and query costs.
23. [Dataflow provided templates](https://cloud.google.com/dataflow/docs/guides/templates/provided-streaming) — existing templates and supported use cases.
24. [Dataproc overview](https://cloud.google.com/dataproc/docs/concepts/overview) — Spark/Hadoop processing distinction for Topic 07.

---

## Validation notes

- **Roadmap alignment:** covers the complete Topic 06 syllabus, checkpoint, exercise flow, and common mistakes; the target file path matches `Roadmap_ptree.md`.
- **Topic 04 integration:** includes BigQuery Storage Write API sink choices, explicit schema, quarantine/DLQ, replay, idempotency, and reconciliation.
- **Topic 07 boundary:** distinguishes Dataflow/Beam from Dataproc/Spark and explains when each fits.
- **Static review:** required sections, code fences, key APIs, event-time concepts, delivery semantics, deployment steps, IAM, cleanup, and official references were reviewed.
- **Actual tests/deployment:** **not run**. No DirectRunner test result, Dataflow job, Pub/Sub publishing, BigQuery write, benchmark, or Flex Template launch is claimed.
- **Unresolved environment-specific items:** exact Beam/Python compatibility, runner option names, connector behavior, BigQuery sink signature/partitioning, current template metadata/build flags, IAM/network settings, region compatibility, quotas, and pricing must be verified in the target GCP environment.
