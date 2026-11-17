# Azure Event Hubs and Stream Analytics: Production Streaming Foundations

> **Scope:** Stage 2C — Data Engineering_3 → `05-Azure-Data-Engineering-and-Microsoft-Fabric/05-event-hubs-and-stream-analytics.md`  
> **Level:** Beginner → intermediate → advanced  
> **Source authority:** `Roadmap_ptree.md` and the module roadmap's Topic 05. This lesson stays within Event Hubs, Stream Analytics, and the engine-selection decisions required by that topic.

## 1. Purpose, prerequisites, and learning outcomes

Event Hubs is a managed event-ingestion log; Azure Stream Analytics (ASA) is a managed SQL-like stream-processing service. Together they support telemetry, clickstreams, operational events, and near-real-time aggregates without requiring you to operate a Kafka cluster or a streaming compute fleet. They are not interchangeable: Event Hubs retains and distributes events; Stream Analytics consumes streams, applies time-aware queries, and writes results to sinks.

### Prerequisites

Be comfortable with:

- Kafka concepts: topics, partitions, offsets, consumer groups, replay, at-least-once processing.
- Python, JSON, environment variables, virtual environments, and package installation.
- Basic SQL `SELECT`, `GROUP BY`, joins, and aggregates.
- Cloud identity, RBAC, storage containers, and the difference between data-plane and management-plane permissions.
- Event time versus processing/arrival time, and why retries can create duplicates.

The module roadmap also expects familiarity with ADLS Gen2 (Topic 02), orchestration (Topic 03), and Synapse (Topic 04). This lesson does not reteach those services.

### Learning outcomes

By the end, you should be able to:

1. Explain namespaces, event hubs, partitions, consumer groups, retention, throughput, and ordering.
2. Send and receive events with the Python SDK, persist checkpoints in Blob Storage, and explain restart behavior.
3. Configure Capture to archive events in Storage/ADLS and understand the Avro/Parquet configuration paths.
4. Write ASA queries using tumbling, hopping, sliding, and session windows; use event-time and temporal joins safely.
5. Design for late/out-of-order events, retries, duplicate delivery, replay, and idempotent sinks.
6. Diagnose lag, throttling, backlogs, and cost; choose Event Hubs/ASA or a more flexible engine.

## 2. Streaming mental model

```text
Devices / apps / services
          |
          v
  Event Hubs namespace
  +---------------------------+
  | event hub: telemetry      |
  | partition 0: ordered log  |
  | partition 1: ordered log  |
  | partition N: ordered log  |
  +---------------------------+
       |             |
       |             +--> Capture --> ADLS/Blob (Avro; Parquet via supported portal no-code path)
       |
       +--> consumer group A --> Stream Analytics --> ADLS / Synapse / Cosmos DB / Power BI / Event Hubs
       +--> consumer group B --> Python / Spark / Kafka-compatible client
```

A producer appends an event to a partition. Consumers read partition logs independently. Consumer groups isolate reader progress; one group's consumption does not advance another group's offsets. Capture archives the stream independently of application consumers. ASA is one consumer/processing path, not a replacement for the durable event log.

## 3. Event Hubs architecture and core concepts

### Namespace, event hub, partitions, and consumer groups

- **Namespace:** management, networking, authentication, and capacity boundary. Throughput units (Standard) are shared across event hubs in a namespace.
- **Event hub:** a named stream/log. Use separate event hubs for different retention, access, schema, or throughput needs; do not create one hub per device.
- **Partition:** an ordered append-only log segment. Ordering is guaranteed **within a partition**, not globally across all partitions. A partition key (for example `deviceId`) routes related events to the same partition, preserving per-key ordering if the producer consistently uses the key. Hot keys can create hot partitions.
- **Consumer group:** an independent view of the event stream, with its own reader progress. Use a separate group for logically independent applications, such as `asa-prod`, `fraud-monitor`, and `archive-validator`. Within a consumer group, partition ownership is divided among active readers; adding more readers than partitions does not increase parallelism beyond the partition count.
- **Offset / sequence number:** identifies position within a partition. A checkpoint records the position a consumer considers processed.
- **Retention:** a bounded replay horizon, not an indefinite archive. Use Capture or another durable sink for long-term retention. Replay is possible only while events remain retained or have been archived elsewhere.

### Throughput and capacity

The roadmap names throughput/processing units. The actual capacity model depends on tier:

- **Basic/Standard:** provisioned throughput units (TUs) at namespace level; Standard supports auto-inflate (scale up to a configured maximum, not automatic scale-down).
- **Premium:** processing units (PUs) with isolated resources and different performance/feature characteristics.
- **Dedicated:** capacity units (CUs) for dedicated clusters.

Capacity limits are tier- and region-dependent and can change. Do not hard-code a throughput estimate from a tutorial into a capacity plan. Measure bytes/sec, events/sec, average and p99 event size, consumer egress, burstiness, partition balance, and downstream sink rate. When ingress exceeds quota, producers may be throttled; egress pressure can appear as consumer lag/backlog even when producers remain healthy. Scale capacity, partition count (which generally must be selected at creation for a given tier/feature), batching, and consumer concurrency based on metrics. A larger partition count is not automatically better: it affects consumer parallelism and operational costs, and does not repair a skewed partition key.

### Kafka-compatible endpoint

Event Hubs exposes a Kafka protocol endpoint for supported Kafka clients. It is **Kafka protocol compatibility**, not a self-managed Kafka cluster: brokers, replication internals, administrative APIs, quotas, and feature support differ. Check the compatibility matrix for your exact client/version and required features. Common configuration uses the namespace's `*.servicebus.windows.net:9093` endpoint, SASL_SSL, and SASL mechanism `PLAIN`; the username is typically `$ConnectionString`, and the password is a namespace/event-hub connection string with the required SAS policy. Prefer Microsoft Entra ID where the chosen client/integration supports it. Never commit connection strings.

### IoT Hub versus Event Hubs

Choose **IoT Hub** when device identity, per-device authentication, device twins, cloud-to-device commands, device provisioning, or device lifecycle management is required. Choose **Event Hubs** for high-throughput event ingestion from applications/services and Kafka-compatible streaming. An IoT solution can use IoT Hub for device ingress and route telemetry onward to Event Hubs or storage. Do not select Event Hubs as a substitute for device management.

## 4. Python producer and consumer with checkpointing

### Environment and identity

Use Python 3.12+ per the module tooling baseline. From the lab folder:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install azure-eventhub azure-eventhub-checkpointstoreblob azure-identity
```

For production, prefer Microsoft Entra ID and managed identity. The sample files support a connection-string teaching path because it is easy to reproduce, but credentials are read from environment variables and never embedded in source. If using Entra ID, assign **Azure Event Hubs Data Sender** to the producer and **Azure Event Hubs Data Receiver** to the consumer at the narrowest appropriate scope; grant the consumer's identity the necessary Blob data permissions on the checkpoint container. Control-plane `Contributor` alone does not grant Event Hubs data-plane send/receive access.

Set variables in your shell or a local ignored `.env` file (never commit it):

```bash
# Connection string should be namespace-scoped or hub-scoped with Send/Listen rights only as needed.
export EVENTHUB_CONNECTION_STRING='Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=...'
export EVENTHUB_NAME='telemetry'
export EVENTHUB_CONSUMER_GROUP='checkpoint-lab'
export BLOB_STORAGE_CONNECTION_STRING='DefaultEndpointsProtocol=...'
export CHECKPOINT_CONTAINER='eh-checkpoints'
export EVENT_COUNT='100000'
```

PowerShell uses `$env:EVENTHUB_NAME = 'telemetry'` syntax. Do not use the RootManageSharedAccessKey in application workloads. Prefer Key Vault or managed identity for deployed apps. Rotate/revoke teaching keys after the lab.

### Producer: send 100,000 events in batches

See `experiments/05_eventhubs_asa/send_events.py`. It generates small JSON telemetry events with a device ID, event timestamp, sequence number, and temperature. Batching reduces protocol overhead. The producer uses a partition key based on `deviceId` so each device's events are routed consistently; do not use a single constant key for all devices, because that concentrates traffic in one partition. The event count is a target, not a claim that this workload has been run.

Operational notes:

- Keep payloads within the service's current event-size limit; batch size is constrained by the service and SDK.
- Use retry policies with bounded backoff for transient `ServiceBusy`/network failures; avoid retrying permanent authentication/schema errors indefinitely.
- A successful send confirms acceptance by Event Hubs, not successful downstream processing or archival.
- If a retry follows an ambiguous network timeout, the same logical event may be sent twice. Include a stable `eventId` for downstream deduplication.

### Consumer: Blob checkpoint store

See `experiments/05_eventhubs_asa/consume_checkpointed.py`. The checkpoint-store extension persists partition ownership and offsets in Blob Storage. The callback processes an event and periodically commits a checkpoint.

**Correctness rule:** checkpoint only after the event's required processing is durable. If you checkpoint before writing the result, a crash can lose the event from the application's perspective. If you write the result and crash before checkpointing, the event can be processed again. Therefore a checkpointed consumer normally provides at-least-once processing semantics, not universal exactly-once side effects.

Checkpoint each event for a simple lab, or checkpoint after a bounded batch/time interval for efficiency. If batching, ensure a checkpoint never advances beyond an event whose side effect failed. Use a separate Blob container per consumer group; keep it dedicated to checkpoint metadata, use a supported general-purpose storage configuration, and follow the SDK's current restrictions (for example, the official quickstart advises disabling hierarchical namespace, blob soft delete, and versioning for its checkpoint store setup).

### Restart experiment

1. Run the consumer and wait until it prints processed events and checkpoints.
2. Stop it with Ctrl+C.
3. Restart it with the same event hub, consumer group, and checkpoint container.
4. Observe that it resumes from persisted partition checkpoints rather than restarting from the beginning (unless no checkpoint exists or you changed the consumer group/starting position).
5. For a realistic failure test, deliberately stop the consumer between side-effect completion and checkpoint update. Confirm that a duplicate is possible and that a stable `eventId` makes the downstream operation idempotent.

Do not run two unrelated test consumers against the same consumer group and checkpoint container: they may compete for partition ownership and interfere with the experiment.

## 5. Capture and schema management

### Event Hubs Capture

Capture periodically writes the event stream to Azure Blob Storage or ADLS Gen2. It is useful for lake ingestion, replay, audits, and batch processing without requiring a custom reader to persist every event.

- **Default Capture format:** Apache Avro, which embeds schema information.
- **Parquet:** the roadmap calls out Avro/Parquet. Microsoft documents Parquet output through the Event Hubs **no-code editor in the Azure portal** for Capture to ADLS Gen2. This particular Parquet path has a material network limitation: the documented prerequisites require the ADLS Gen2 destination to be publicly accessible and not behind a storage firewall or secured in a virtual network. Do not use this path for a private-only storage design. If that conflicts with the lab's security requirements, use the supported Avro Capture path and convert downstream with Spark/ADF. Do not assume every Capture API/template/SDK configuration supports Parquet identically; verify the chosen creation path and region/feature availability.
- Configure destination account/container/filesystem, archive path format, time/size window, and authorization. Capture output is chunked files, not one file per event; each partition captures independently and writes a completed block blob when the configured size/time condition is met (first condition wins). Capture can also write empty files when no data is available, so validate file contents and event IDs rather than treating file presence/count as proof of delivery. Confirm storage account type/networking and same-subscription requirements for the selected authentication method before deployment.
- **Capture billing varies by tier:** Standard has a separate Capture charge; Premium and Dedicated include Capture in the tier price. The destination Storage/ADLS capacity and transactions are billed separately. Add lifecycle policies to expire or tier captured data only after validating retention requirements.
- Validate the archive by listing files and reading records. A non-empty Capture path does not alone prove every expected event arrived; compare producer event IDs/counts and partition sequence ranges where possible.

### Schema Registry

Event Hubs Schema Registry stores schema contracts in schema groups and supports schema-aware serialization. Avro is the established path; JSON Schema support is documented as preview in some current product experiences, so confirm its status and client support before choosing it. Compatibility-mode enforcement for schema evolution is documented for Avro; do not assume the same compatibility checks apply to every schema format. Registry metadata alone does not validate arbitrary raw JSON events: producers and consumers must use compatible serializers/deserializers and enforce the contract. Define required fields, types, units, timestamp semantics, compatibility policy, and evolution process. For Avro with backward compatibility, adding optional fields is a common compatible change; test schema changes with the actual serializer and consumers before rollout.

### Partition key and ordering design

Choose the key according to the ordering boundary you actually need: `deviceId` for per-device sequence, `accountId` for per-account events, or no key when distribution is more important than per-entity order. A partition key is not a global ordering mechanism. If related events must be processed in sequence, include an entity sequence/version and validate it in the consumer. Partition-count changes and routing behavior should be reviewed as a data-contract change.

## 6. Azure Stream Analytics architecture and query language

An ASA job has one or more **inputs** (for example, Event Hubs, IoT Hub, Blob/ADLS reference data), a SQL-like query, and one or more **outputs**. Configure authentication, serialization, event timestamp, and partitioning for each input/output. ASA is managed and convenient for SQL-style temporal aggregations, filtering, projections, and bounded temporal joins. It is less suitable for complex custom state, arbitrary libraries, advanced graph/stateful algorithms, or extensive feature engineering.

### Per-device one-minute tumbling aggregation

Assume Event Hubs input `telemetry` contains JSON records with `deviceId`, `eventTime` (ISO-8601 timestamp), `temperature`, and `eventId`. Configure the input to parse JSON and set `eventTime` as the event-time field in the query:

```sql
SELECT
    System.Timestamp() AS windowEnd,
    deviceId,
    COUNT(*) AS eventCount,
    AVG(temperature) AS avgTemperature,
    MIN(temperature) AS minTemperature,
    MAX(temperature) AS maxTemperature
FROM telemetry TIMESTAMP BY eventTime
GROUP BY deviceId, TumblingWindow(minute, 1)
```

A tumbling window is fixed-size, contiguous, non-overlapping. An event belongs to one window. The output timestamp from `System.Timestamp()` is the window end; it is not necessarily the original event timestamp.

### Four required window types

**Tumbling — non-overlapping, fixed duration:**

```sql
SELECT System.Timestamp() AS windowEnd, deviceId, COUNT(*) AS n
FROM telemetry TIMESTAMP BY eventTime
GROUP BY deviceId, TumblingWindow(minute, 1)
```

**Hopping — fixed duration with a hop interval; windows may overlap:**

```sql
SELECT System.Timestamp() AS windowEnd, deviceId, AVG(temperature) AS avgTemp
FROM telemetry TIMESTAMP BY eventTime
GROUP BY deviceId, HoppingWindow(minute, 10, 1)
```

This produces a 10-minute window every minute; an event can contribute to multiple results.

**Sliding — output when the content changes as events enter/leave the duration:**

```sql
SELECT System.Timestamp() AS windowEnd, deviceId, COUNT(*) AS n
FROM telemetry TIMESTAMP BY eventTime
GROUP BY deviceId, SlidingWindow(minute, 5)
HAVING COUNT(*) >= 3
```

Sliding-window semantics are event-driven; it is not simply a fixed schedule every minute.

**Session — group bursts separated by inactivity:**

```sql
SELECT System.Timestamp() AS sessionEnd, deviceId, COUNT(*) AS n
FROM telemetry TIMESTAMP BY eventTime
GROUP BY deviceId, SessionWindow(minute, 2, 30)
```

The arguments are time unit, inactivity timeout (2 minutes), and maximum duration (30 minutes). Verify the current ASA query-language syntax and supported constraints when changing parameters; the query is an illustrative pattern. Session windows are useful for user/device activity bursts rather than fixed reporting buckets.

### Temporal joins and reference data

ASA supports temporal joins for matching events within a bounded time interval. `DATEDIFF` defines the allowed time difference; the exact query shape depends on whether both inputs are streams or one is reference data.

For a **stream-to-reference-data** join, configure `deviceReference` as a reference-data input and use a normal key join:

```sql
SELECT e.deviceId, e.eventTime, r.siteName, e.temperature
FROM telemetry e TIMESTAMP BY eventTime
JOIN deviceReference r
    ON e.deviceId = r.deviceId
```

For a **stream-to-stream temporal join**, both sides are streams and the time bound is part of the join condition. A common query shape is:

```sql
SELECT a.deviceId, a.eventTime AS eventTimeA, b.eventTime AS eventTimeB,
       a.temperature AS temperatureA, b.temperature AS temperatureB
FROM telemetryA a TIMESTAMP BY eventTime
JOIN telemetryB b TIMESTAMP BY eventTime
    ON a.deviceId = b.deviceId
    AND DATEDIFF(minute, a, b) BETWEEN 0 AND 5
```

These are query patterns: validate the exact input aliases, timestamp types, supported join form, and temporal direction against the selected ASA query-language version before deployment. Reference data should be small enough and refreshed at a cadence that meets the job's needs. For two continuously changing streams, define which event-time differences count as a match and how unmatched events should be handled.

### Outputs

ASA supports outputs such as ADLS/Blob, Synapse, Cosmos DB, Power BI, and Event Hubs, subject to connector/configuration availability. Select the output for the consumer contract:

- **ADLS:** durable analytical archive; configure path, format, partitioning, and file rollovers.
- **Synapse:** serve downstream analytics, but account for sink throughput and write behavior.
- **Cosmos DB:** operational lookup/serving; use stable keys and idempotent upsert patterns where supported.
- **Power BI:** near-real-time visualization; avoid treating a dashboard sink as the system of record.
- **Event Hubs:** chain event-driven applications; protect against loops and duplicate propagation.

If a sink throttles, the ASA output backlog can grow and job latency rises. Make the sink capable of the expected throughput and monitor it as part of the pipeline, not just the ASA compute.

## 7. Event time, watermarks, late data, replay, and delivery guarantees

### Three times to distinguish

- **Event time:** when the source says the event happened (for example, `eventTime`).
- **Enqueue/arrival time:** when Event Hubs accepted it.
- **Processing time:** when a consumer or ASA processed it.

ASA's `TIMESTAMP BY` selects the event-time field for time-aware operations. The job's **late-arrival tolerance** and **out-of-order tolerance** govern how ASA handles events that arrive too late or out of order relative to the selected event time. Policies can drop events or adjust timestamps, depending on the configured action. Increasing tolerance can improve completeness but delays output and increases buffering/state. A watermark is a practical notion of event-time progress: it represents how far the engine believes it can finalize time windows given observed events and the configured tolerances. It is not a guarantee that no older event will ever arrive.

The processing order matters: ASA applies late-arrival handling and then out-of-order handling according to job configuration. Verify the actual Event Ordering settings in the portal/job definition; defaults and available policy choices may change. Record counts of adjusted/dropped events where available and alert when they exceed a business threshold.

### Replay and duplicate handling

- Event Hubs retains events for a configured period; consumer groups maintain independent progress, and a consumer can read from an earlier position while events are retained.
- Capture provides a longer-lived archive if retention and storage policy permit. Replaying from Capture is a separate ingestion process, not a transparent rewind of the original Event Hubs consumer.
- A checkpoint can be behind a completed side effect, causing replay/duplicate processing; a checkpoint advanced before a side effect can cause loss. This is the fundamental reason checkpoints alone do not guarantee exactly-once business outcomes.
- ASA can provide service-specific processing guarantees under configured conditions, but end-to-end exactly-once depends on source, job recovery, sink semantics, retries, and key design. Do not promise universal exactly-once delivery. Use stable event IDs, idempotent upserts, unique constraints, deduplication windows, or transactional sink writes where supported.
- If events can be replayed, make the downstream write idempotent and define whether a late event updates a prior aggregate, creates a correction record, or is rejected.

### Late-event lab strategy

The lab includes an event with an `eventTime` older than its enqueue time. Compare output under a low tolerance and a tolerance large enough to accept the delay. ASA's configured action may adjust or drop late events; it does not necessarily retroactively revise every already-emitted result. Choose tolerance from a measured lateness distribution and the business SLA, not convenience.

## 8. Monitoring, alerting, and operations

Monitor the whole chain, not one dashboard:

| Signal | Likely interpretation | Response |
|---|---|---|
| Producer throttling / `ServiceBusy` | Namespace ingress quota or burst limit reached | Inspect bytes/sec and events/sec; batch, retry with backoff, and scale TUs/PUs/CUs or tier |
| Consumer lag / growing backlog | Consumer throughput below ingress, slow handler, or downstream blockage | Inspect per-partition lag, CPU/IO, checkpoint frequency, and sink latency; add consumers only up to useful partition parallelism |
| Skewed partition traffic | Hot key or uneven event sizes | Inspect partition key distribution; change key only with ordering-contract review |
| Capture files delayed | Capture interval/size threshold, low traffic, or storage permissions/network issue | Check Capture status, configured interval/size, destination authorization, and storage metrics |
| ASA input backlog rising | Query compute constrained, source backlog, or event-time policy buffering | Inspect job diagram, input backlog per partition, SU utilization, query complexity, and input partitioning |
| ASA output backlog / latency | Sink throttling or write throughput too low | Inspect sink limits, output errors/retries, write partitioning, and target capacity |
| Late/out-of-order events adjusted/dropped | Source clocks, network delays, or tolerance too low | Compare event time and enqueue time; adjust producer clock/metadata and policy based on SLA |
| Auth failures | Expired key, missing data-plane role, firewall/private endpoint issue | Verify identity, least-privilege role scope, network path, and secret rotation |

Set Azure Monitor alerts for throttling, server errors, incoming/outgoing bytes/events, consumer lag/backlog, Capture failures, ASA SU utilization, input/output errors, and job state. Thresholds should be based on the workload's SLO and baseline. Use Action Groups to route incidents to the team's paging or ticketing system. Retain diagnostic logs long enough to investigate incidents; avoid logging secrets or full sensitive payloads.

### Scaling and operational trade-offs

- **Scale throughput:** increase TUs (Standard), PUs (Premium), or CUs (Dedicated) according to tier; auto-inflate only scales up within its configured cap and does not remove the need for capacity planning.
- **Scale consumers:** more consumers can improve throughput across partitions, but each partition can be owned by only one active consumer in a consumer group at a time. A consumer count greater than partition count is usually idle overhead.
- **Scale ASA:** increase Streaming Units (SUs) if compute-bound; inspect query parallelism, partitioning, serialization, and sink throughput before spending more. SUs do not solve an inherently throttled sink or an unbalanced key.
- **Retention vs Capture:** retention supports replay over a bounded period; Capture is a separate archive with separate storage and transaction costs.
- **Geo-disaster recovery:** namespace geo-disaster recovery typically replicates metadata/configuration through an alias; do not assume it replicates event data. Dedicated-tier geo-replication is a distinct capability with different semantics. Document RPO/RTO, failover procedure, DNS/alias behavior, consumer checkpoint strategy, and what happens to in-flight events. Test the selected tier's current DR model before making guarantees.

## 9. Workload decision matrix

| Option | Prefer when | Trade-offs / cautions |
|---|---|---|
| **Event Hubs + Stream Analytics** | Azure-native ingestion plus SQL-style filtering, temporal aggregation, simple joins, and managed operations | Limited general-purpose stateful logic; validate connector and sink semantics; Azure-centric |
| **Apache Kafka (self-managed or managed Kafka service)** | Kafka ecosystem, broad Kafka APIs/connectors, custom broker control, portability requirements | Cluster/service operations, tuning, upgrades, and cost depend on the chosen managed/self-managed offer; Event Hubs Kafka compatibility is not feature-identical Kafka |
| **Amazon Kinesis** | AWS-native streaming with AWS service integrations | AWS-specific IAM/capacity model; cross-cloud integration adds complexity |
| **Google Cloud Pub/Sub** | GCP-native event ingestion and event-driven integrations | Different subscription, retention, ordering-key, and delivery semantics; not a drop-in API replacement |
| **Spark Structured Streaming (Databricks/Fabric/Spark)** | Stateful transformations, joins, ML feature pipelines, lakehouse writes, larger code-based pipelines | More engineering and compute tuning; micro-batch/continuous semantics and sink guarantees vary by source/sink |
| **Flink on Azure / managed Flink offering** | Low-latency stateful stream processing, event-time timers, complex windows, keyed state | Availability and deployment model depend on the Azure offering/region; more operational and conceptual complexity than ASA |
| **Fabric Real-Time Intelligence (Eventstream, Eventhouse/KQL)** | Unified Fabric analytics, real-time event routing, KQL analytics, integration with OneLake/Power BI | Requires Fabric capacity and governance model; feature parity with Event Hubs/ASA or general-purpose Flink/Kafka is not one-to-one |

### Five scenario decisions

1. **10,000 devices, one-minute average temperature by device, Azure sink:** Event Hubs + ASA is a good first choice. Key by device, configure event time and late tolerance, monitor partition balance and sink latency.
2. **Complex fraud state across many entities with custom state, external lookups, and sub-second requirements:** evaluate Flink or Spark Structured Streaming; ASA may be too constrained for the state model.
3. **Existing Kafka estate depends on advanced Kafka APIs and custom broker administration:** use a Kafka service that supports the needed features. Event Hubs Kafka endpoint may work only after feature compatibility tests.
4. **AWS-native application already built around Kinesis and IAM:** stay with Kinesis unless a platform-level migration justifies the integration cost.
5. **Enterprise wants event ingestion, KQL exploration, dashboards, and OneLake integration in a Fabric-centric estate:** evaluate Fabric Real-Time Intelligence, but verify capacity, event routing, latency, governance, and feature requirements rather than assuming it replaces every Event Hubs/ASA use case.

## 10. Geo-DR and cross-cloud comparison

Event Hubs geo-disaster recovery and geo-replication are not synonyms. The commonly used geo-disaster-recovery pairing with an alias is focused on namespace metadata/configuration failover; producers and consumers must reconnect and applications must account for the destination namespace's data state. Dedicated-tier geo-replication can replicate event data, but its tier and setup requirements differ. Confirm the current product documentation and target SKU before selecting a recovery architecture.

When comparing Event Hubs with Kafka, Pub/Sub, or Kinesis, compare these dimensions explicitly: ordering scope, partition/shard key behavior, consumer-group/subscription model, retention/replay, delivery semantics, schema management, protocol/API compatibility, scaling unit, regional DR, private networking, monitoring, and total cost. Similar nouns do not imply identical guarantees.

## 11. Hands-on lab — `experiments/05_eventhubs_asa/`

The lab assets are in the sibling `experiments/05_eventhubs_asa/` directory. The workflow is designed for a small, disposable Azure subscription. **Intended outcomes are described; no Azure deployment, 100,000-event run, Capture read, ASA execution, or benchmark is claimed as performed.**

### Required resources and permissions

- Azure subscription and resource group; Azure CLI; Python 3.12+.
- Event Hubs namespace and event hub, Standard or another tier that supports the selected features; at least one event hub partition (choose enough partitions to allow the planned consumer parallelism; for this small lab, 2–4 is reasonable but not a performance recommendation).
- Storage account and Blob container for checkpoint metadata. For Capture, configure a separate ADLS Gen2/Blob destination as permitted by the chosen Capture path. Do not reuse the checkpoint container.
- Stream Analytics job with an Event Hubs input and ADLS output; optional Power BI or Synapse output depending on available access.
- Event Hubs data sender/receiver rights; storage data permissions for checkpoint and Capture; permissions to create/start/stop ASA jobs and configure outputs.
- Configure networking/firewalls/private endpoints so the local client and Azure services can reach required endpoints. Public network access may be blocked by organizational policy.

### Step A — Deploy and configure Event Hubs Capture

1. Create a resource group and namespace using the Azure portal or Azure CLI. Choose a region and tier; configure namespace capacity, minimum TLS/security, public/private access, and diagnostic settings according to your environment.
2. Create event hub `telemetry` with a modest partition count and retention long enough to finish the lab.
3. In the event hub's **Capture** settings, enable Capture, select the destination Storage/ADLS account and container/filesystem, choose the supported output format for that configuration (Avro is the default API-oriented path; use the portal no-code editor for the documented Parquet Capture path), and configure the archive path format and time/size window.
4. Verify that the destination is writable by the configured Capture mechanism and that storage networking permits it. Start with the shortest supported practical capture window for the lab; do not assume a file appears immediately after the first event.
5. Record the full Capture path and its format in `lab-notes.md`. Never paste keys into that file.

### Step B — Send 100,000 events

```bash
python send_events.py
```

The script reads `EVENT_COUNT` (default 100,000), sends batches, and emits progress. It may take time and consume capacity. If throttling occurs, use bounded retries, reduce producer concurrency or rate, and/or adjust capacity within the budget. Avoid launching many concurrent producers without measuring.

**Validation:** compare the script's accepted-send counter with its target, inspect Event Hubs incoming event/byte metrics, wait for Capture's configured time/size interval, list captured blobs, and read/inspect records using the appropriate Avro or Parquet reader. Do not compare only file count: Capture batches events into files. For stronger validation, count stable `eventId` values across all files and check for duplicates/missing IDs.

### Step C — Consume with checkpoints and restart

```bash
python consume_checkpointed.py
```

After several events/checkpoints, stop and restart the process. It should resume from the stored checkpoint for the same consumer group. The sample prints event IDs and checkpoints each event for clarity; production should batch checkpoints after durable processing. Introduce a controlled failure between the business write and checkpoint to demonstrate possible duplicate processing. Verify that downstream idempotency handles it.

### Step D — Build the one-minute ASA query

1. Create an ASA job and configure Event Hubs as the input. Choose the namespace, hub, consumer group, authentication method, serialization, and `eventTime` timestamp field.
2. Add the query from `asa/tumbling_per_device.sql`.
3. Configure an ADLS/Blob output with a supported format/path and credentials. Optionally add a Power BI or Synapse output if permissions and connector configuration are available.
4. Start the job with a defined output start time and send events. Verify output window-end timestamps and per-device aggregates. The first result appears only when the relevant window can close and the job's event-time policies permit progress.

### Step E — Late event and policy experiment

Use the sample event in `data/late_event.json` or send a record whose `eventTime` is several minutes earlier than its actual send time. In ASA job settings, locate the event-ordering policy. Record the late-arrival tolerance, action for late events, out-of-order tolerance, and action for out-of-order events. Run with a deliberately small tolerance, then with a tolerance that covers the event's lateness. Compare whether the event is dropped or adjusted and whether output latency changes. Do not assume already-emitted aggregates will be retroactively rewritten.

### Step F — Kafka client

Use the commands in `kafka/README.md` with a compatible Kafka CLI/client version. Configure the Event Hubs bootstrap endpoint on port 9093, `SASL_SSL`, `PLAIN`, username `$ConnectionString`, and a scoped connection string as the password. Use a send-only SAS policy for the producer and a listen-only policy for the consumer. Validate a small event count before the 100k run. If your selected Kafka client requires unsupported APIs, record the incompatibility rather than treating it as a client misconfiguration.

### Step G — Cost review and cleanup

- Review namespace tier/capacity hours, ingress/egress, Capture, storage capacity/transactions, ASA SU hours, and any Power BI/Synapse/Fabric capacity charges. Current regional prices and quotas must be checked in the Azure Pricing Calculator and service quotas; do not extrapolate from a single test.
- Stop/delete the ASA job when not needed; disable Capture if retaining the namespace; delete lab resources after preserving required evidence. Export only non-secret notes and screenshots.
- Delete the resource group only after verifying it contains no shared or production resources. Confirm no namespace, storage account, ASA job, or paid Fabric/Power BI capacity remains unintentionally active.

## 12. Troubleshooting checklist

- **`ServiceBusy` / throttling:** inspect namespace ingress, batching, event size, TU/PUs/CUs, auto-inflate cap, and retry backoff.
- **No events in consumer:** confirm namespace, event hub, consumer group, starting position, firewall/DNS, SAS rights or Entra role, and that events are still within retention.
- **Consumer starts from beginning:** confirm Blob checkpoint container, consumer group, namespace/hub names, storage data permissions, and that checkpoint writes succeeded.
- **Duplicates after restart:** expected under at-least-once side-effect/checkpoint boundaries; implement stable event IDs and idempotent writes.
- **Capture files missing:** inspect Capture enablement, destination path, identity/authorization, storage firewall, time/size window, and incoming event metrics.
- **ASA no output:** verify job is running, input deserialization, query field names, timestamp parsing, output auth, output schema and window close timing.
- **ASA backlog rising:** inspect source partition backlog, SU utilization, query complexity, event ordering tolerance, and sink throttling.
- **Late events disappear:** check `TIMESTAMP BY`, late-arrival action/tolerance, event clock quality, and query output timing.
- **Kafka auth error:** check endpoint/port, SASL_SSL, mechanism, username `$ConnectionString`, policy rights, and password format; don't paste credentials into tickets.

## 13. Practice questions and scenario exercises

1. Why does a consumer group not provide global ordering across partitions?
2. What happens if the consumer checkpoints before persisting a database write? What if it persists the write and crashes before checkpointing?
3. When is a partition key helpful, and when can it harm throughput?
4. Explain the difference between Capture and Event Hubs retention.
5. For a 10-minute window emitted every minute, choose the ASA window type and explain overlapping results.
6. A sensor event arrives six minutes after its event timestamp. What should be considered before changing ASA's late-arrival tolerance?
7. A job's input backlog grows while SU utilization is low. Name two downstream causes to investigate.
8. An application requires arbitrary keyed state, complex event-time timers, and custom code. Which engines should be evaluated beyond ASA?
9. What does Event Hubs geo-disaster recovery guarantee, and what must not be assumed about event data?
10. Why is Kafka compatibility not equivalent to full Kafka feature parity?

### Answer key

1. Each partition has its own ordered sequence; events in separate partitions have no total order unless the application imposes one.
2. Checkpoint-before-write risks loss; write-before-checkpoint risks duplicate replay. Checkpoint after durable processing and make writes idempotent.
3. It preserves per-key order and routes related events together; a hot key can overload one partition and limit parallelism.
4. Retention is a bounded replay window in Event Hubs; Capture archives events to Storage/ADLS as files with separate retention/cost policies.
5. Hopping window of size 10 minutes and hop 1 minute; a single event can contribute to multiple outputs.
6. Measure lateness distribution and business SLA, decide drop vs adjust behavior, quantify output delay and completeness, and test whether consumers can handle corrections.
7. Sink throttling/write latency and output errors/retries; also inspect target capacity and partitioning.
8. Evaluate Flink or Spark Structured Streaming on Databricks/Fabric; also consider Fabric Real-Time Intelligence if its capabilities fit.
9. Metadata/alias failover behavior differs from data replication; do not assume geo-DR automatically copies retained event data. Verify tier-specific replication semantics.
10. Event Hubs implements the Kafka protocol subset supported by its service; broker administration and feature APIs may differ.

## 14. Checkpoint

You are ready to move on when you can do these without notes:

- [ ] Explain partitions, consumer groups, Capture, retention, and the limits of global ordering.
- [ ] Send events from Python and consume with a Blob checkpoint store.
- [ ] Explain restart duplicates and implement idempotency using a stable event ID.
- [ ] Write ASA window queries and explain event-time, late arrival, and out-of-order policy.
- [ ] Diagnose throttling, backlog, Capture delay, and sink bottlenecks using metrics.
- [ ] Choose a processing engine based on state complexity, latency, operations, and platform fit.

**Roadmap common mistakes to avoid:** too few partitions for intended parallelism; no checkpointing; choosing Stream Analytics for complex stateful logic; ignoring throughput limits.

## 15. Official references

- [Event Hubs FAQ, protocols, tiers, and quotas](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-faq)
- [Event Hubs scalability guide](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-scalability)
- [Event Hubs Capture overview](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-capture-overview)
- [Capture Event Hubs data in Parquet format — prerequisites and network limitations](https://learn.microsoft.com/en-us/azure/stream-analytics/capture-event-hub-data-parquet)
- [Stream Analytics reference-data JOIN](https://learn.microsoft.com/en-us/stream-analytics-query/reference-data-join-azure-stream-analytics)
- [Stream Analytics temporal JOIN syntax](https://learn.microsoft.com/en-us/stream-analytics-query/join-azure-stream-analytics)
- [Python Event Hubs quickstart](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-python-get-started-send)
- [Python Blob checkpoint-store documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/eventhub-checkpointstoreblob-readme?view=azure-python)
- [Event Hubs Schema Registry concepts](https://learn.microsoft.com/en-us/azure/event-hubs/schema-registry-concepts)
- [ASA windowing functions](https://learn.microsoft.com/en-us/azure/stream-analytics/stream-analytics-window-functions)
- [ASA query-language windowing](https://learn.microsoft.com/en-us/stream-analytics-query/windowing-azure-stream-analytics)
- [ASA event ordering policies](https://learn.microsoft.com/en-us/azure/stream-analytics/event-ordering)
- [ASA time handling and watermark behavior](https://learn.microsoft.com/en-us/azure/stream-analytics/stream-analytics-time-handling)
- [ASA output troubleshooting](https://learn.microsoft.com/en-us/azure/stream-analytics/stream-analytics-troubleshoot-output)
- [Azure Well-Architected guidance for Event Hubs](https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-event-hubs)

> **Verification note:** This lesson and its lab files are learning materials. SQL-like queries and scripts are illustrative starter examples. Cloud resources, SDK calls against a live namespace, Capture output, ASA job execution, Kafka-client compatibility, cost, and performance were not executed or benchmarked in this environment. Confirm current region/SKU limits and portal configuration before using in production.
