# Change Streams and NoSQL-to-Lakehouse Ingestion

> **Stage 2C — Data Engineering_3 · Module 01: NoSQL and Distributed Databases · Topic 09**  
> **Level:** Beginner → Intermediate → Advanced  
> **Purpose:** Move operational NoSQL data into a lakehouse incrementally, correctly, observably, and without unnecessary source load.

---

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Explain why operational stores should usually serve application traffic while analytical workloads use a lakehouse or warehouse.
- Choose among a full snapshot, timestamp polling, and log-/stream-based change data capture (CDC), and state what each can and cannot guarantee.
- Design extraction plans for MongoDB, DynamoDB, Cassandra, Elasticsearch/OpenSearch, and Neo4j without pretending their change semantics are interchangeable.
- Persist source positions safely, restart consumers, replay events, and recover when a source retention window has expired.
- Design an initial-snapshot-to-stream handoff that has an explicit consistency boundary and reconciliation plan.
- Preserve stable business keys while landing raw events in Bronze and normalizing nested data into Silver tables.
- Apply inserts, updates, and deletes through idempotent `MERGE` logic, with per-key ordering and tombstones.
- Detect schema drift, quarantine invalid data, reconcile source and destination, and monitor lag, failures, and source-read costs.
- Evaluate managed ingestion versus a custom Kafka/CDC pipeline.

### Prerequisites and connection to earlier topics

This lesson builds on the earlier module rather than re-teaching it:

| Prior topic or stage skill | How it is used here |
|---|---|
| Topic 01 — NoSQL families | Match the extraction plan to document, wide-column, key-value, search, or graph storage. |
| Topic 02 — consistency models | Understand that a snapshot, a replica read, and a change log may expose different consistency boundaries. |
| Topic 03 — MongoDB modelling | Preserve `_id`, nested structures, update semantics, and change-stream events. |
| Topic 04 — Cassandra partitioning/tombstones | Understand token ranges, CDC commit-log segments, TTLs, and deletion markers. |
| Topic 05 — DynamoDB single-table design and Streams | Handle partition/sort keys, stream view types, sequence numbers, and deletes. |
| Topic 06 — Redis | Recognize that cache state is not automatically a canonical analytical source; prefer the system of record or an explicit event log. |
| Topic 07 — Elasticsearch/OpenSearch | Treat a search index as a derived projection unless it is explicitly the system of record. |
| Topic 08 — Neo4j/Cypher | Export nodes/relationships with stable IDs and preserve relationship identity. |
| Stage 2 Module 2.5 — nested data | Flatten documents and convert arrays into child tables without losing keys. |
| Stage 2 Module 2.9 — CDC and watermarks | Apply incremental extraction foundations and understand timestamp-polling blind spots. |
| Stage 2 Module 2.12 — idempotent merge/dedup | Make replay safe and avoid duplicate target rows. |
| Stage 2 Module 2.16 — Kafka/Debezium | Understand source connectors, durable event transport, and sinks. |
| Stage 2B — object storage/lakehouse | Land immutable raw records and publish Delta/Iceberg/Parquet data with appropriate permissions. |

**Roadmap placement:** this is the final topic because it combines the operational database concepts from Topics 01–08 into the module mini-project: a polyglot operational platform feeding a lakehouse. The resulting governed tables become reusable inputs for later Stage 2C analytics/platform modules (including cloud data platforms and lakehouse tooling) and downstream ML feature/data pipelines; keep the ingestion contract independent of any one warehouse or cloud.

## 2. The e-commerce example used throughout

Assume an e-commerce application uses multiple operational stores:

- **MongoDB `orders`**: canonical order documents, including customer, line items, shipping address, and payment summary.
- **DynamoDB**: checkout/session or order-status records keyed by `PK`/`SK`.
- **Cassandra**: high-volume device/fulfilment events, queried by tenant and time bucket.
- **Elasticsearch/OpenSearch**: product/search index, derived from product/catalogue data.
- **Neo4j**: customer-account-device relationships for fraud investigation.

The lakehouse needs trustworthy analytical tables such as `silver.orders`, `silver.order_items`, `silver.order_status_events`, `silver.device_events`, `silver.search_documents`, and `silver.fraud_relationships`. It must not assume that each store contains a complete or equally authoritative copy of business state. Record lineage and source-of-truth ownership for every entity.

Example MongoDB order document:

```json
{
  "_id": "ord-1042",
  "customer_id": "cust-81",
  "created_at": "2026-10-18T10:00:00Z",
  "updated_at": "2026-10-18T10:04:12.120Z",
  "status": "paid",
  "currency": "INR",
  "total": 1499.00,
  "shipping": {"city": "Pune", "postal_code": "411001"},
  "items": [
    {"line_id": "1", "sku": "SKU-A", "qty": 1, "unit_price": 999.00},
    {"line_id": "2", "sku": "SKU-B", "qty": 2, "unit_price": 250.00}
  ],
  "payment": {"provider": "gateway-x", "state": "captured"}
}
```

Use `_id` as the source document identity, `customer_id` as a stable business key, and `(order_id, line_id)` as the child-table key. Do not replace stable identifiers with row numbers or array positions: item arrays can be reordered or edited.

## 3. Why separate OLTP from analytics?

Operational stores are tuned for application access patterns: point reads, small writes, indexed lookups, predictable latency, and availability. Analytical workloads often scan large ranges, join many entities, aggregate historical data, and repeatedly reread the same history. Running them on the operational store can consume CPU, memory, I/O, cache capacity, connections, and replica bandwidth needed by the application. Large scans may also interfere with compaction, replication, or index maintenance.

A lakehouse separates the workloads and provides cheap historical retention, columnar scans, governed tables, and reproducible transformations. Separation is not free: ingestion introduces latency, schema handling, replay logic, storage, and reconciliation. The design target is not “zero cost” but a deliberate freshness/correctness/cost trade-off.

Recommended path:

```text
Operational stores
  ├── MongoDB ── change stream / supported connector ─┐
  ├── DynamoDB ── Streams, Kinesis, or export ────────┤
  ├── Cassandra ── CDC logs / supported connector ───┤
  ├── Elasticsearch/OpenSearch ── scan / app events ─┤
  └── Neo4j ── query/export / app events ────────────┘
                                                       ↓
                                      durable transport / object storage
                                                       ↓
                         Bronze: immutable raw events + source metadata
                                                       ↓
                      validation → dedup → type policy → quarantine
                                                       ↓
                   Silver: current-state tables + event/child tables
                                                       ↓
                      Gold: business metrics, features, reporting
```

Do not route analytical reads back to the source just because the lakehouse is behind. Publish a freshness SLA and alert on violations.

## 4. Snapshot, timestamp polling, CDC, and change streams

These terms are related but not interchangeable.

| Method | How it detects data | Position/checkpoint | Deletes | Main limitations |
|---|---|---|---|---|
| Full snapshot | Reads all visible records at a point or over a scan window | Snapshot ID, partition/range progress, and source consistency boundary if available | A later snapshot comparison can infer missing rows, but not always the exact delete time/reason | Expensive; concurrent writes can create an inconsistent multi-page copy unless a consistent snapshot mechanism exists. |
| Timestamp polling | Re-queries rows with `updated_at > last_watermark` (usually with overlap) | Timestamp plus tie-breaker and run metadata | Usually invisible unless a tombstone or soft-delete field is retained | Missing/incorrect timestamps, precision collisions, clock skew, hard deletes, backdated updates, late writes, and non-atomic checkpointing. |
| CDC from a database log | Reads database mutation/log records | Log offset, LSN, token, sequence, or connector offset | Often explicit delete/tombstone events, subject to source and connector semantics | Log retention, configuration, privileges, schema/event semantics, and possible gaps if the offset expires. |
| Change stream/API | Reads a database-provided event feed | Resume token or stream sequence/position | Often explicit delete event; full deleted document may not be included unless pre-images or keys suffice | Retention windows and service-specific guarantees; some stores expose only partial event information or no native change stream. |

A full snapshot answers “what records did the scan observe?” A change feed answers “what mutations were emitted after a source-defined position?” Timestamp polling approximates change detection from mutable row metadata. CDC is the broader practice of capturing database changes, often from logs; a change stream is one API for exposing such changes.

### 4.1 Timestamp watermark pattern

A common query is:

```sql
SELECT *
FROM source_table
WHERE updated_at > :previous_watermark
  AND updated_at <= :upper_bound;
```

Do not use only a timestamp when multiple rows can share the same timestamp. Prefer a compound cursor such as `(updated_at, primary_key)` with lexicographic comparison if the source supports it, or deliberately re-read a time overlap and deduplicate. Persist the **upper bound actually used**, not the maximum timestamp seen after arbitrary filtering.

A safer polling pattern is:

1. Read the previous committed watermark.
2. Choose a bounded upper time `T` from a trusted clock.
3. Query `updated_at >= previous_watermark - overlap` and `updated_at <= T`.
4. Land all records with source metadata in Bronze.
5. Validate and apply idempotently to Silver.
6. Commit the new watermark only after all records through `T` are durably landed and target application has reached the required commit boundary.
7. Re-read overlap on the next run; deduplicate by stable key and version/order rule.

Even this does not discover hard deletes unless the source exposes soft deletes, an audit table, a delete log, or a periodic full reconciliation. Timestamp polling is not a substitute for CDC where delete completeness and low latency are requirements.

### 4.2 Snapshot scan cost and partitioning

A full scan can be split into non-overlapping key ranges, token ranges, or time buckets. Parallelism reduces elapsed time but can increase source load. Use bounded concurrency, source read limits, and checkpoint each completed range. A range checkpoint means only that the range was scanned; it does **not** prove the entire source was observed at one consistent instant.

- **MongoDB:** paginate on a stable indexed key; use a supported snapshot/read concern strategy where the deployment and scan duration permit it. `_id` pagination is practical but a long-running multi-page scan is not automatically a single point-in-time snapshot.
- **DynamoDB:** use `Scan` cautiously; it is paginated and can consume read capacity. Parallel scan segments are not a global point-in-time snapshot. For large tables, evaluate export-to-S3 rather than repeatedly scanning.
- **Cassandra:** token-range scans can distribute work, but consistency level, replica state, tombstones, TTLs, and concurrent writes affect observed state. Avoid ad hoc full-cluster scans against latency-sensitive workloads.
- **Elasticsearch/OpenSearch:** use a stable sort and point-in-time/search-after pattern when supported by the deployed version; avoid deep `from`/`size` pagination. A search index is a projection and may lag its upstream source.
- **Neo4j:** use bounded key ranges or stable IDs and pagination. A long-running sequence of queries is not automatically a transactionally consistent graph snapshot; keep the export boundary explicit.

## 5. Source-store extraction strategies

### 5.1 Capability matrix

| Store | Full copy | Incremental/change capture | Delete detection | Important constraints |
|---|---|---|---|---|
| MongoDB | Indexed/paginated collection scan; supported consistent read strategy where practical; Atlas or connector export options may apply | Change streams on supported replica-set/sharded deployments; MongoDB source connector; polling as fallback | `operationType: "delete"` includes document key; pre-image is optional and must have been enabled/retained for it to exist | Resume token is tied to stream context; oplog/retention and image retention can limit recovery. `updateLookup` is current-state lookup, not necessarily exact event-time post-image. |
| DynamoDB | `Scan` or point-in-time export to S3 | DynamoDB Streams, Kinesis Data Streams for DynamoDB, or supported zero-ETL/managed integration | Stream `REMOVE` record; export snapshots represent state, not a complete mutation history | DynamoDB Streams retains records for 24 hours. Kinesis retention is configurable according to stream settings. Export-to-S3 has service prerequisites and is not a continuous per-event feed. |
| Cassandra | Token-range scan/query plan, Spark/connector, or managed export | CDC-enabled commit-log segments or a supported connector; Debezium Cassandra connector availability/status must be checked against the exact release | CDC event/connector representation depends on source path; Cassandra tombstones are storage-level delete markers and are not a universal event contract | CDC requires configuration and disk/space planning; TTL expiration and tombstone compaction mean current-state scans cannot reconstruct every historical delete. |
| Elasticsearch/OpenSearch | Scroll/PIT + `search_after` or snapshot/backup/export facility, depending on goal | Usually app-level event stream, upstream source CDC, or version-specific change-data mechanism/connector; do not assume a universal native CDC log | Delete API events are not necessarily recoverable from a later index scan; track upstream delete events or an audit/outbox | Often a derived search projection; refresh delay and reindexing change what a scan observes. Elasticsearch and OpenSearch APIs/connectors may differ. |
| Neo4j | Batched node/relationship export by stable IDs; supported connector or graph export | Application outbox/domain events, query-based timestamp/version polling, or a specific licensed/plugin/connector feature where available | Explicit domain event or tombstone is safest; graph queries alone cannot infer when a deleted node/relationship was removed | Do not assume every Neo4j edition/version exposes a general-purpose CDC feed. Node and relationship identity and deletion semantics must be designed. |

**Key distinction:** a store's native stream, a connector's event envelope, and an application event are different contracts. Document the contract for the actual deployed product/version, including which events are emitted, whether deletes have before-images, and how offsets are committed.

### 5.2 MongoDB change streams

Change streams require a deployment topology that supports them (typically a replica set or sharded cluster). A change event's `_id` field is the resume token; do not modify or remove it in a change-stream pipeline. Resume with `resume_after`/`resumeAfter` using the token for the same compatible stream context. For invalidate events such as collection drop/rename events, `start_after`/`startAfter` may be required instead of `resume_after`. `startAtOperationTime` is an alternative start position, not something to combine with the resume-token options.

Python example using PyMongo. This is an instructional consumer skeleton: `save_checkpoint_atomically` and `write_bronze_durably` are application functions that must be implemented against your durable store.

```python
from pymongo import MongoClient
from pymongo.errors import PyMongoError

client = MongoClient("mongodb://localhost:27017/?replicaSet=rs0")
orders = client.shop.orders
checkpoint_store = client.ingestion.checkpoints

# A real implementation should scope the checkpoint by source, database,
# collection, pipeline fingerprint, and consumer version.
checkpoint = checkpoint_store.find_one({"_id": "shop.orders.v1"}) or {}
resume_token = checkpoint.get("resume_token")

watch_options = {"full_document": "updateLookup"}
if resume_token is not None:
    watch_options["resume_after"] = resume_token

try:
    with orders.watch(**watch_options) as stream:
        for event in stream:
            # 1. Write the raw event durably before advancing the checkpoint.
            write_bronze_durably(event)
            # 2. Commit the token only after the event is durably landed.
            save_checkpoint_atomically(
                source="shop.orders.v1",
                resume_token=event["_id"],
            )
except PyMongoError:
    # Log error type and last durable token; do not silently reset to now.
    raise
```

Important details:

- `full_document="updateLookup"` retrieves the most current majority-committed document at lookup time. If subsequent writes occur before lookup, it may not be the exact document state at the instant of the triggering update. The update delta in the event describes that update; use pre/post-images where supported and configured if exact images are required.
- Pre/post-images require supported MongoDB versions and collection configuration (MongoDB 6.0+ introduced change-stream pre/post-images). Image availability depends on enablement and retention; `whenAvailable` can return null, while `required` can fail if the image is unavailable.
- Delete events normally provide `documentKey`, not a full deleted document. A delete can be applied using the stable document key; if downstream logic needs prior fields, preserve pre-images or an independent audit event.
- Resume tokens are not indefinite backups. If the required history has fallen outside the oplog/change-stream history available to the deployment, resume can fail. Do not silently open a new stream “from now”; reconcile or rebuild first.
- Persist tokens with the event that they acknowledge. If Bronze write succeeds but checkpoint fails, replay creates a duplicate that must be deduplicated. If checkpoint succeeds before the event is durable, a crash can lose that event. Prefer at-least-once delivery plus idempotent landing.

### 5.3 DynamoDB Streams, Kinesis, and incremental S3 exports

**DynamoDB Streams** emits item-level records for table modifications. The stream view type controls whether records include keys only, old images, new images, or both. `NEW_AND_OLD_IMAGES` is useful for audits/diffs but increases event size and may expose sensitive data. `REMOVE` indicates removal of an item; the event's key is sufficient to tombstone a target row if the lakehouse key mapping is stable. Stream records are retained for **24 hours**, so consumers need lag alarms and a recovery plan.

**Kinesis Data Streams for DynamoDB** is an alternative streaming path for higher-scale/longer configurable retention and Kinesis ecosystem integration. It has its own shard/sequence-number checkpointing, retention configuration, scaling, and cost model. AWS currently documents retention up to one year for Kinesis Data Streams, subject to the configured service plan/settings; verify the current limit and cost for the actual stream. Do not apply DynamoDB Streams’ 24-hour retention assumption to Kinesis.

**Incremental export to S3** is snapshot-oriented and useful for analytical transfer without scanning the table with repeated `Scan` calls. It is not the same thing as an event-by-event change stream. Confirm table point-in-time recovery/export prerequisites, export format, export time range, and service support for the chosen incremental export workflow. A full export or incremental export can support reconciliation/backfills; a stream or Kinesis path is needed for lower-latency mutations.

Boto3 sketch for consuming a DynamoDB Streams shard (simplified; production code must enumerate shards, handle iterators, retry throttling, and persist shard iterator progress/sequence numbers safely):

```python
import boto3

streams = boto3.client("dynamodbstreams", region_name="us-east-1",
                       endpoint_url="http://localhost:8000")
tables = boto3.client("dynamodb", region_name="us-east-1",
                      endpoint_url="http://localhost:8000")

# DynamoDB Local behavior and stream support depend on the local version.
# Create the table with StreamSpecification enabled before writing items.
desc = tables.describe_table(TableName="Orders")
stream_arn = desc["Table"].get("LatestStreamArn")
if not stream_arn:
    raise RuntimeError("Enable a stream on Orders before consuming it")

stream_desc = streams.describe_stream(StreamArn=stream_arn)["StreamDescription"]
shard_id = stream_desc["Shards"][0]["ShardId"]
iterator = streams.get_shard_iterator(
    StreamArn=stream_arn, ShardId=shard_id,
    ShardIteratorType="TRIM_HORIZON")["ShardIterator"]

while iterator:
    response = streams.get_records(ShardIterator=iterator, Limit=100)
    for record in response["Records"]:
        # Normalize INSERT/MODIFY/REMOVE to a common event envelope,
        # then write raw JSON/Parquet and checkpoint the sequence number.
        handle_dynamodb_record(record)
    iterator = response.get("NextShardIterator")
```

`TRIM_HORIZON` means earliest record still available to that iterator, not “all history since table creation.” A restarted consumer must persist and resume from a suitable sequence/position using a robust shard checkpoint strategy. The sketch uses one shard only and is not a production shard-discovery loop. DynamoDB Local is a bounded functional simulation; it does not reproduce all managed-service scale, IAM, retention, export, or zero-ETL behavior.

### 5.4 Cassandra CDC logs

Cassandra's CDC writes eligible commit-log segments to a CDC raw directory when CDC is enabled and configured. Operators must plan CDC space, segment lifecycle, disk pressure, and downstream consumption. CDC is not automatically a globally ordered, forever-retained business-event log. Partitioning, replica behavior, TTLs, tombstones, compaction, and the chosen CDC consumer determine what is observable and how it is decoded.

Production approach:

1. Verify Cassandra version, CDC configuration, directory and disk quotas, permissions, and supported consumer/connector matrix.
2. Use a compatible CDC consumer or connector that understands the deployed version's commit-log format; do not parse binary logs with a home-grown script.
3. Persist segment/offset progress and event identity in the consumer's durable checkpoint store.
4. Land raw CDC events first. Normalize mutations with primary-key columns and mutation metadata.
5. Preserve delete/tombstone information when emitted. A query of current table state cannot tell you the exact history of a hard delete or TTL expiry.
6. Alert on CDC backlog and disk usage. If required segments are gone, rebuild a snapshot and reconcile rather than assuming the missing history can be recovered.

**Version-specific connector caution:** the current Debezium 3.6 Cassandra connector documentation describes a per-node JVM process (not a Kafka Connect-framework connector) that reads each node's local CDC commit logs and publishes table topics to Kafka. CDC must be enabled both node-wide and on each table. Because each node sees only its local writes, replicated mutations can produce duplicates, and local commit-log arrival is not a globally ordered business-event sequence. The current documentation also lists unsupported changes that are ignored, including TTL on collection-type columns, range deletes, static columns, triggers, materialized views, secondary indices, and lightweight transactions. Verify the exact Debezium/Cassandra compatibility matrix and all limitations for the release you will deploy; do not treat “connector exists” as proof that every mutation is captured. See the linked versioned connector documentation in Section 20.

### 5.5 Elasticsearch and OpenSearch

A search index is commonly a denormalized projection of a source database, not the authoritative history. Best option: capture changes from the system of record and use that same event to update both the search index and lakehouse. If the index itself is the only available source, export documents with PIT/search-after or another version-supported stable pagination strategy, and pair it with an application outbox/event log or explicit audit stream for updates and deletes.

Do not infer a delete solely from absence in a paginated scan unless the scan represents a known complete consistent boundary. Otherwise a document may be missing because of refresh lag, routing/filter mismatch, permissions, partial scan failure, or concurrent mutation. If the source API exposes only current documents, it cannot reconstruct all historical changes. Validate Elasticsearch and OpenSearch connector/API differences for the exact engine and version.

### 5.6 Neo4j graph synchronization

Export nodes and relationships separately, retaining stable application IDs. A node's internal database ID should not be treated as a permanent cross-environment business key unless the product explicitly guarantees that property for the intended use. Model relationship identity explicitly where parallel relationships can exist, for example `relationship_id`, `source_id`, `target_id`, and domain attributes.

Preferred incremental approach: publish domain events/outbox records when the application changes nodes/relationships, or use a specifically supported CDC/plugin/connector capability after checking version, edition, and licensing. A query such as `WHERE updated_at > $watermark` can be a fallback only if all relevant node and relationship mutations update a reliable timestamp and deletes are recorded separately. Neo4j query polling alone cannot reliably discover hard deletes that leave no marker.

For graph exports, land node and relationship records as separate Bronze entities, then build `silver.graph_nodes` and `silver.graph_relationships`. Preserve endpoint keys and enforce referential checks before building analytics. Graph algorithms can be run in Neo4j or downstream; exported analytics must record algorithm/configuration version and graph snapshot boundary.

## 6. Common event envelope and source positions

Different systems use different native positions. Normalize them into a common envelope without discarding the original payload or source cursor.

```json
{
  "source_system": "mongodb-shop",
  "source_entity": "shop.orders",
  "source_key": {"_id": "ord-1042"},
  "operation": "update",
  "source_position": {"kind": "mongodb_resume_token", "value": {"_data": "..."}},
  "source_version": null,
  "source_event_time": null,
  "source_document_updated_at": "2026-10-18T10:04:12.120Z",
  "capture_time": "2026-10-18T10:04:12.311Z",
  "schema_fingerprint": "sha256:...",
  "before": null,
  "after": {"_id": "ord-1042", "status": "paid"},
  "raw_payload": {"...": "original source event"}
}
```

The envelope fields are a target convention, not a claim that every source provides all fields. Use `null` where unavailable and document the semantics. Do not fabricate source event time from capture time or copy a document's `updated_at` into `source_event_time` unless the source contract defines it as the mutation time. For example, MongoDB change events expose a logical `clusterTime`; an application field such as `updated_at` can be missing, low precision, or written incorrectly. A source position may be opaque and only meaningful to the originating connector. Preserve the native token/offset exactly, protected against accidental mutation.

Minimum durable metadata:

- source system/entity and stable key;
- native source position or connector offset;
- source operation (`insert`, `update`, `delete`, `snapshot`, etc.);
- source event timestamp if actually provided, capture timestamp, ingestion run ID;
- schema/version fingerprint and raw payload;
- transformation version/build ID used for each Silver commit or replay;
- target application status or batch ID;
- checkpoint version and consumer/connector configuration fingerprint.

**Keep the checkpoint boundaries separate.** A source-capture checkpoint may mean “the event is durably present in Bronze”; it must not be reported as “Silver has applied the event.” Track (1) source position durably landed in Bronze and (2) Bronze offset/batch durably applied to Silver. If Bronze and the source checkpoint cannot share a transaction, write Bronze first and then advance the source checkpoint: a crash can create a duplicate, which event-identity deduplication handles, but advancing first can lose an event. Likewise, if Silver commits and its consumer crashes before recording the applied offset, replay the same Bronze batch and rely on an idempotent, version-guarded merge.

## 7. Kafka and connector architecture

A common architecture is:

```text
source database → source connector → Kafka topic(s) → object-storage sink
                                              └────→ stream processor → Delta/Iceberg
```

Kafka adds durable buffering and decouples source capture from downstream processing. It does not automatically make a pipeline end-to-end exactly-once: source offsets, Kafka producer/consumer transactions, object writes, and table commits must be coordinated or made idempotent.

- **MongoDB connector:** Debezium's MongoDB connector captures changes from replica sets/sharded clusters into Kafka topics. Verify the compatible MongoDB and Debezium release versions and connector configuration.
- **Cassandra connector:** Debezium's Cassandra connector has had incubating status in release lines. Validate tested versions and limitations; do not assume the same maturity as the MongoDB connector.
- **Kafka Connect sinks:** object-storage sinks commonly write files to S3-compatible storage, but file naming, partitioning, delivery semantics, schema registry behavior, and delete handling depend on the chosen connector and configuration.
- **Other options:** managed ingestion may avoid operating Kafka and connectors but may constrain supported entities, freshness, schema handling, or destination formats.

Connector configuration review checklist:

1. Exact source, connector, runtime, and destination versions.
2. Required source topology, privileges, logs, and retention.
3. Topic naming, key strategy, partition count, and ordering assumptions.
4. Snapshot mode and initial snapshot-to-stream behavior.
5. Offset storage durability and recovery procedure.
6. Delete/tombstone configuration and downstream interpretation.
7. Schema registry/evolution and incompatible type policy.
8. Error tolerance, dead-letter/quarantine topic, retries, and alerting.
9. Object sink commit/rotation strategy and file size/partition strategy.
10. Tested restart, rebalance, retention-expiry, and replay drills.

## 8. Initial snapshot → change stream without gaps

This is the hardest correctness boundary. A naïve sequence “scan collection, then open stream” has a gap: writes made after the scan passed a key but before the stream starts may not be in either result. Opening the stream first and then scanning can create duplicates and can overwrite newer state with an older snapshot row unless the merge is version-aware.

### 8.1 Safe patterns

**Pattern A — source/connector-supported consistent snapshot plus log position (preferred when available).** The source or connector establishes a snapshot boundary and a corresponding log position. It emits snapshot rows associated with that boundary and then changes after the boundary. Follow the connector's documented algorithm and recovery rules; do not manually recreate a connector's snapshot protocol by guessing an offset.

**Pattern B — start stream first, buffer changes, snapshot, then reconcile/apply.** This can work only if the source permits a defensible stream start boundary and the buffered events cover the entire snapshot interval. Buffer all events durably, take the snapshot, then merge snapshot rows and buffered events using source ordering/version metadata. Events before the snapshot boundary may be duplicates; events after the boundary must win over older snapshot values. If no common ordering/version exists, do not claim a provably gap-free handoff.

**Pattern C — watermark overlap plus reconciliation (best-effort polling).** Use an overlap window and idempotent merge, then compare a fresh full snapshot/counts/checksums. This reduces gaps but is not equivalent to transactional snapshot-plus-log capture when timestamps are unreliable.

### 8.2 Handoff diagram and risk points

```text
Time ────────────────────────────────────────────────────────────────────►
       establish boundary/position P0
                  │
                  ├── begin durable stream capture at P0 ───────────┐
                  │                                                  │
                  ├── scan snapshot (may overlap concurrent writes)  │
                  │       snapshot rows → Bronze                     │
                  │                                                  │
                  └── record snapshot completion and range coverage  │
                                                                     ▼
                                                     buffered changes after P0
                                                                     │
                    merge snapshot + changes using stable key/version │
                                                                     ▼
                                             reconcile → publish checkpoint
```

Risk points:

- **Gap:** stream begins after snapshot scan and a write falls between them.
- **Duplicate:** stream begins before snapshot ends and the same mutation appears in both paths.
- **Stale overwrite:** an older snapshot row is applied after a newer change event.
- **Missing delete:** snapshot omits a deleted row but the pipeline cannot distinguish a delete from a range not yet scanned.
- **Unprovable order:** snapshot rows and events have no common source boundary or version. A timestamp alone may not be sufficient.

### 8.3 Handoff checklist

- Use a source-supported snapshot/log handoff whenever available.
- Record `snapshot_id`, start/end time, source boundary, completed ranges, and source/connector version.
- Start and durably buffer the change feed at the documented boundary.
- Keep snapshot rows and stream events distinguishable in Bronze.
- Merge by stable key and a source-defined order/version, not arrival time alone.
- Do not advance the published checkpoint until both snapshot coverage and buffered events through the boundary are committed.
- Reconcile counts, keys, sampled values, and deletes after handoff.
- If the source cannot expose a consistent boundary, explicitly label the result best-effort and schedule repeated reconciliation/full refreshes.

## 9. Bronze → Silver transformation

### 9.1 Bronze: immutable evidence

Bronze should retain the original event or snapshot record and capture metadata. Prefer append-only files/table partitions by source and ingestion date; partitioning should not create a tiny-file explosion. Do not flatten away the raw payload before it is safely stored. Keep sensitive fields protected by access controls and retention policy.

Example Bronze columns:

```text
source_system, source_entity, source_key_json, operation,
source_position_json, source_version, source_event_time,
captured_at, ingestion_run_id, schema_fingerprint,
raw_payload_json, payload_hash
```

Raw event JSON is not always identical to the source document. A MongoDB change event wraps the changed document and metadata; DynamoDB uses typed attribute values; CDC connectors may add envelope fields. Preserve both the envelope and original payload.

### 9.2 Silver: typed and queryable entities

For the order example, create:

- `silver.orders`: one row per `order_id`, with `customer_id`, status, totals, shipping fields, and last source version.
- `silver.order_items`: one row per `(order_id, line_id)`, with SKU, quantity, and unit price.
- `silver.order_payments` if payment details need independent history/governance.
- `silver.order_events`: optional append-only event history with operation, source position, and event metadata.

Stable keys must survive flattening. Avoid using array index as `line_id` unless the source contract guarantees stable array ordering and meaning. If the source does not provide a child ID, define a deterministic business key (for example `(order_id, sku, fulfillment_group)` only if it is truly unique); otherwise retain a generated identity with a clearly documented reconciliation strategy.

### 9.3 Flattening nested orders

The following PySpark example transforms **complete source-document images** from Bronze. The normalizer must first map source-specific operations to canonical values (`snapshot`, `insert`, `update`, `delete`) and extract keys from the source envelope. Do not feed a raw CDC envelope or a delete event into `from_json` as though it were an order document. For MongoDB partial updates, obtain/reconstruct a complete document image only if the downstream model requires it; `updateLookup` may reflect a later state.

```python
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DecimalType, ArrayType
)

# These are complete document images only; deletes are handled separately.
complete_docs = bronze.where(
    F.col("operation").isin("snapshot", "insert", "update")
    & F.col("raw_payload_json").isNotNull()
)
deletes = bronze.where(F.col("operation") == "delete").select(
    "source_key_json", "source_position_json", "source_version",
    "captured_at", F.lit(True).alias("is_deleted")
)

order_schema = StructType([
    StructField("_id", StringType()),
    StructField("customer_id", StringType()),
    StructField("created_at", StringType()),
    StructField("updated_at", StringType()),
    StructField("status", StringType()),
    StructField("currency", StringType()),
    StructField("total", DecimalType(18, 2)),
    StructField("shipping", StructType([
        StructField("city", StringType()),
        StructField("postal_code", StringType()),
    ])),
    StructField("items", ArrayType(StructType([
        StructField("line_id", StringType()),
        StructField("sku", StringType()),
        StructField("qty", IntegerType()),
        StructField("unit_price", DecimalType(18, 2)),
    ]))),
])

parsed = complete_docs.select(
    "source_position_json", "source_version", "operation", "captured_at",
    "raw_payload_json",
    F.from_json("raw_payload_json", order_schema).alias("doc")
)

# Route doc-is-null and missing-key rows to quarantine in production; do not drop them.
invalid = parsed.where(
    F.col("doc").isNull() | F.col("doc._id").isNull()
)
valid = parsed.where(
    F.col("doc").isNotNull() & F.col("doc._id").isNotNull()
)

orders_silver = valid.select(
    F.col("doc._id").alias("order_id"),
    F.col("doc.customer_id").alias("customer_id"),
    F.to_timestamp("doc.created_at").alias("created_at"),
    F.to_timestamp("doc.updated_at").alias("updated_at"),
    F.col("doc.status").alias("status"),
    F.col("doc.currency").alias("currency"),
    F.col("doc.total").alias("total"),
    F.col("doc.shipping.city").alias("shipping_city"),
    F.col("doc.shipping.postal_code").alias("shipping_postal_code"),
    "source_position_json", "source_version", "operation", "captured_at"
)

# explode (not explode_outer) yields no child rows for an empty/null items array.
items_silver = valid.select(
    F.col("doc._id").alias("order_id"),
    F.explode("doc.items").alias("item"),
    "source_position_json", "source_version", "operation", "captured_at"
).where(F.col("item.line_id").isNotNull()).select(
    "order_id", F.col("item.line_id").alias("line_id"),
    F.col("item.sku").alias("sku"), F.col("item.qty").alias("qty"),
    F.col("item.unit_price").alias("unit_price"),
    "source_position_json", "source_version", "operation", "captured_at"
)
```

`invalid` and `deletes` are intentionally separate outputs: write invalid records to quarantine with the raw payload and parse errors; map delete keys into tombstones; and apply child-row removals when a complete parent image shows an item no longer exists. The snippet demonstrates parsing and flattening, not a complete streaming transaction. Production code must persist the source position only after the Bronze write, and must make parent and child updates replay-safe. Confirm that `raw_payload_json` is actually serialized as the document JSON (not a BSON wrapper or DynamoDB typed-attribute map) before using this schema.

## 10. Deduplication, per-key ordering, idempotency, and deletes

### 10.1 Delivery and processing semantics

At-least-once capture plus idempotent processing is a practical baseline. A crash after landing an event but before checkpointing causes replay; this is expected. The target should converge to the correct state even when an event is applied twice.

Do not call a pipeline “exactly once” merely because Kafka, Delta, or Iceberg has transactional features. End-to-end exactly-once requires coordination across source position, event sink, transformation state, and target commit; most practical systems instead use durable checkpoints, deduplication, and idempotent writes.

### 10.2 Event identity and ordering

Use a deterministic event identity where available:

- MongoDB: source entity + resume token (opaque token retained as raw bytes/string/JSON).
- DynamoDB Streams: stream ARN/table + shard + sequence number (and event identity as provided by the API); handle shard lineage.
- Kinesis: stream + shard + sequence number.
- Kafka: topic + partition + offset, with key and source metadata retained.
- Cassandra: connector-defined source position/event ID; do not invent a global sequence if the source does not provide one.
- Polling: stable key + source version/update timestamp + payload hash, with the limitations of polling recorded.

Ordering is usually only reliable within a defined scope: per source partition, shard, or key. If events for a single key can arrive from multiple partitions, define a source version or deterministic conflict policy. `captured_at` is not a safe order field. If no comparable version exists, route conflicts to reconciliation rather than choosing the latest arrival blindly.

### 10.3 Tombstones and delete processing

A tombstone is a durable representation that a key has been deleted. It may be a delete event in Bronze and a soft-delete/current-state marker in Silver. Do not physically erase all evidence before downstream consumers have processed the delete.

Recommended current-state fields:

```text
business_key, ..., is_deleted, deleted_at,
source_position, source_version, last_applied_at
```

For sources that emit explicit deletes, map the source key into the target key even if `after` is null. For sources without reliable delete capture, use soft-delete/audit events or periodic full reconciliation. Do not infer deletes from missing rows in a partial scan.

### 10.4 Delta Lake merge example

The following SQL illustrates a **current-state** merge. `silver.orders_changes` is assumed to be a staged, deduplicated set containing at most one winning event per `order_id` for the merge batch, with a comparable `source_version` (for example, a source sequence or a carefully defined connector order). `source_version` is illustrative; it must be mapped to a real source-defined comparable version for the source in use.

```sql
MERGE INTO silver.orders AS t
USING silver.orders_changes AS s
ON t.order_id = s.order_id
WHEN MATCHED
  AND s.source_version > t.source_version
  AND s.operation = 'delete'
THEN UPDATE SET
  t.is_deleted = true,
  t.deleted_at = s.event_time,
  t.source_version = s.source_version,
  t.last_applied_at = current_timestamp()
WHEN MATCHED
  AND s.source_version > t.source_version
  AND s.operation <> 'delete'
THEN UPDATE SET
  t.customer_id = s.customer_id,
  t.status = s.status,
  t.total = s.total,
  t.updated_at = s.updated_at,
  t.is_deleted = false,
  t.source_version = s.source_version,
  t.last_applied_at = current_timestamp()
WHEN NOT MATCHED AND s.operation <> 'delete'
THEN INSERT (
  order_id, customer_id, status, total, updated_at,
  is_deleted, source_version, last_applied_at
) VALUES (
  s.order_id, s.customer_id, s.status, s.total, s.updated_at,
  false, s.source_version, current_timestamp()
);
```

A delete for a key not yet in the target does not insert a row in this example. If you need protection against a later-arriving stale insert resurrecting the key, store a tombstone even when the target row is absent, or maintain a separate per-key latest-version/deletion ledger. For an Iceberg target, use the engine/catalog-supported `MERGE INTO` semantics for your version; syntax and feature availability vary by engine and Iceberg version. Do not copy Delta SQL unchanged into every Iceberg runtime.

Before merging, deduplicate staged events. Example SQL when a real comparable version is available:

```sql
WITH ranked AS (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY source_version DESC, event_time DESC
  ) AS rn
  FROM bronze.order_events_validated
)
SELECT * FROM ranked WHERE rn = 1;
```

The tie-breaker must be deterministic. If `source_version` ties and the source offers no further ordering field, comparing `event_time` may still be insufficient; detect tied conflicting payloads and quarantine/reconcile them.

### 10.5 Arrays and child deletes

When an order update changes its `items` array, do not only upsert the new children: removed items must be deleted/tombstoned in `silver.order_items`. Two common approaches:

1. Treat each parent document as a complete current-state image: stage all child rows for the changed parent, then transactionally replace that parent's child set (where the table engine supports a safe transaction pattern), or compute child-key differences and tombstone missing child keys.
2. Model each line item as its own source entity with independent insert/update/delete events, if the source design supports it.

The first approach depends on receiving a complete document image. `updateLookup` may reflect a later document state; use a reliable full-image or snapshot strategy if exact per-event child history is required. Keep append-only `order_events` if historical mutations matter.

### 10.6 Failure-mode acceptance matrix

Use this matrix in code review and failure-injection drills. “Effectively once” means repeated delivery converges to one correct target state; it is not a claim that the source, transport, and lakehouse share one distributed transaction.

| Failure or race | Required guardrail | Evidence required before sign-off |
|---|---|---|
| Insert/update/delete occurs during snapshot | Source-supported snapshot/log boundary; otherwise durable stream buffer plus a defensible merge order and reconciliation | Inject each operation during the scan; show no missing key/state/delete after handoff |
| Crash after event received but before Bronze write | Do not advance source checkpoint; resume/re-deliver from last durable position | Restart test shows event eventually lands |
| Bronze write succeeds, checkpoint fails | Accept replay; deduplicate by stable source event identity | Raw duplicates are detectable and Silver has one current state |
| Silver commit succeeds, applied-offset write fails | Replay Bronze batch; use event identity and version-guarded idempotent merge | Replaying same batch leaves values, tombstones, and counts unchanged |
| Duplicate delivery | Unique event identity in Bronze/control state and idempotent merge | Duplicate replay produces no duplicate current-state rows |
| Same-key events arrive out of order | Use a source-defined comparable per-key version/order; otherwise quarantine conflicts and reconcile | Old update after new update/delete cannot overwrite/resurrect state |
| Equal/low-precision timestamps | Compound cursor or source position, overlap, dedup; timestamp alone is not a total order | Test equal timestamps with distinct updates |
| Timestamp polling misses late update or hard delete | Overlap and periodic source reconciliation; CDC/outbox for stronger completeness | Compare key sets and sampled values; demonstrate delete detection path |
| Source position/oplog/stream retention expires | Stop unsafe checkpoint advancement; snapshot/rebuild and reconcile, or replay from retained raw archive | Recovery record quantifies any irrecoverable interval |
| New field/incompatible type appears | Versioned schema contract, raw preservation, quarantine/approved evolution | Fixture demonstrates additive acceptance and incompatible-type quarantine |
| Nested array changes/removes child | Complete image or explicit child events; diff child keys and tombstone removals | Removed child no longer appears active after replay |
| Backfill overlaps live ingestion | Separate backfill ID/staging, source boundary, version guard, controlled publish | Re-running overlapping range converges without stale overwrite |
| Transformation changes before replay | Keep raw Bronze immutable; record `transform_version`; replay to staging and compare before publish | Same raw input under each version is reproducible and differences reviewed |

A test that only checks process exit status is insufficient. Assertions must cover key coverage, per-key winning version, delete/tombstone state, duplicate replay, schema quarantine, and reconciliation results.

## 11. Schema drift, evolution, and quarantine

Schemaless does not mean schema-free. Consumers still depend on field names, types, nullability, units, and nested shapes. Common drift includes a new optional field, renamed field, `integer` becoming `string`, array becoming scalar, missing nested object, timestamp format change, and numeric precision changes.

### 11.1 Detection strategy

For every raw event:

1. Preserve the raw payload.
2. Infer or parse against a versioned expected schema.
3. Calculate a canonical schema fingerprint (field paths and logical types, excluding unstable ordering where appropriate).
4. Compare with the approved schema registry/table contract.
5. Classify drift as additive-compatible, incompatible type change, missing required field, or malformed record.
6. Apply the declared policy; do not silently coerce all values to strings.

### 11.2 Example policy

| Drift | Default policy | Why |
|---|---|---|
| New nullable field | Record and approve additive evolution; add to Silver deliberately | Avoid surprise schema changes in production tables. |
| `total` decimal → string | Quarantine or parse only if format is explicitly validated | Silent cast can corrupt financial values. |
| Required key missing | Quarantine; alert | Cannot safely merge without stable identity. |
| `items` array → object | Quarantine or route to a version-specific parser | Flattening semantics have changed. |
| Unknown extra field | Preserve in Bronze; log schema drift | Raw evidence remains available for later backfill. |
| Invalid timestamp | Quarantine with raw value and parser error | Do not substitute capture time as source event time. |

Example quarantine table:

```text
source_system, source_entity, source_position, raw_payload,
schema_fingerprint, validation_errors, first_seen_at, replay_status
```

Reprocessing quarantined records should use the same idempotent event identity and should not bypass the source checkpoint policy. Schema evolution is a reviewed contract, not an automatic “merge schema everywhere” switch.

## 12. Replay, backfills, and retention expiry

### 12.1 Safe replay

- Keep raw Bronze immutable for a declared retention period, subject to privacy and deletion requirements.
- Store source positions and target commit IDs in a durable checkpoint/control table.
- Replay into a staging table or a new table version, deduplicate by event identity, and merge by source ordering.
- Avoid applying old events over newer target state. Use source versions, snapshots, or a controlled full rebuild.
- For schema fixes, reprocess Bronze with a versioned transformation rather than mutating historical raw evidence.
- Make backfill ranges explicit and record `backfill_id`, range, source boundary, transformation version, and reconciliation results.

### 12.2 When a position expires

**MongoDB resume token/oplog window expired:** stop the consumer and preserve logs/checkpoints. Do not reset to “now” and claim no loss. Determine the last durable source position, start a new supported snapshot/change-stream handoff, reconcile, and backfill from an authoritative history source if one exists. If no source history exists, document the irrecoverable interval and quantify the uncertainty.

**DynamoDB Streams record expired:** the Streams retention window is 24 hours. If required records are no longer available, recover from an export/snapshot and reconcile; use Kinesis with suitable retention for future needs if its trade-offs fit. Do not assume incremental export reconstructs every expired stream event in order; it reconstructs state over its supported export semantics.

**Kinesis retention exceeded:** data older than configured retention is unavailable from the stream. Restore from archive/source history or take a new snapshot and reconcile.

**Cassandra CDC segments removed:** if CDC segments needed for the checkpoint have been purged or overwritten, perform a consistent-enough re-snapshot and reconciliation, and inspect why CDC consumption lagged or disk constraints removed required history.

**Kafka offsets expired or topic data deleted:** restore from retained raw object storage or source history; otherwise rebuild snapshot plus a new capture boundary. Check whether connector offsets and source history are still compatible.

### 12.3 Resume-token-expired runbook

1. **Declare impact:** page the pipeline owner; record source, collection, last durable token, first failed time, target freshness, and downstream consumers.
2. **Freeze unsafe advancement:** do not replace the checkpoint with a new token and do not publish a “caught up” status.
3. **Preserve evidence:** save consumer logs, connector offsets, pipeline version/configuration, current target counts, and latest successful reconciliation.
4. **Diagnose retention:** confirm whether the token is invalid because of retention/oplog history, stream definition changes, collection invalidation, permissions, or a transient issue. Do not classify every resume failure as expiry.
5. **Choose recovery:** if history is still available, retry with the correct supported resume option and unchanged stream context. If history is expired, run a source-supported snapshot-plus-stream handoff or restore from an authoritative archive.
6. **Rebuild into staging:** take a snapshot with range coverage and boundary metadata; buffer new events if the chosen handoff protocol requires it.
7. **Reconcile:** compare counts and key sets by partition/range, sample records, inspect deletes, and compare business aggregates.
8. **Publish:** atomically switch/reconcile target state only when acceptance checks pass. Record any interval that cannot be reconstructed.
9. **Prevent recurrence:** alert on lag well before retention expiry, increase retention only where supported and cost-justified, tune consumer throughput, and run restart/expiry drills.
10. **Close incident:** document root cause, lost/uncertain interval, repair actions, and updated RPO/freshness expectations.

## 13. Reconciliation and data quality

CDC correctness must be measured, not assumed. Reconcile after initial load, handoff, connector upgrades, recovery, schema changes, and periodically in steady state.

### 13.1 Reconciliation layers

1. **Counts:** source and target counts for a stable snapshot boundary, with known filters and entity definitions. Counts alone can match while values differ.
2. **Key sets:** compare distinct stable keys by range/partition. A count match is not proof that the same keys exist.
3. **Checksums/hashes:** canonicalize field ordering, timestamp/timezone representation, decimals, nulls, and arrays before hashing. Hashes can reveal mismatches but are not a substitute for defining canonicalization.
4. **Sampled comparisons:** compare selected source and target rows/documents including nested fields and child arrays.
5. **Business invariants:** order totals, item counts, status distributions, orphan relationship counts, and delete/tombstone counts.
6. **Change accounting:** source events observed = successfully applied + quarantined + explicitly ignored by documented policy + currently pending, after accounting for replay/dedup. Track these categories separately.

Example validation queries:

```sql
-- Current-state row counts excluding tombstones
SELECT COUNT(*) FROM silver.orders WHERE is_deleted = false;

-- Child rows without a parent (should be zero or explained)
SELECT COUNT(*)
FROM silver.order_items i
LEFT ANTI JOIN silver.orders o ON i.order_id = o.order_id
WHERE i.is_deleted = false;

-- Check for duplicate stable keys
SELECT order_id, COUNT(*)
FROM silver.orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

For a source-side count, run against the same snapshot boundary when the database supports it. Comparing a live count at 10:00 with a lakehouse count from 09:50 is a useful lag signal but not a strict correctness proof.

## 14. Observability, alerting, and source-read cost

Build per-source/entity dashboards. A single overall pipeline status hides which source is falling behind.

| Metric | Meaning | Alerting approach |
|---|---|---|
| `source_lag_seconds` | Current time minus latest source event time, only if source event time is meaningful | Alert on freshness SLA; separately track capture delay. |
| `capture_lag_seconds` | Capture time minus source event time | Detect connector or source backlog; beware clock skew. |
| `checkpoint_age_seconds` | Time since durable position advanced | Alert if stalled beyond expected idle/traffic behavior. |
| `consumer_lag_records/bytes` | Unconsumed records in stream/log transport | Alert before retention window is threatened. |
| `resume_failures_total` | Failed resume attempts categorized by cause | Page on invalid/expired positions; distinguish transient failures. |
| `quarantine_rate` | Invalid events divided by observed events | Alert on sudden schema or data-quality change. |
| `duplicate_event_rate` | Events rejected by event-identity dedup | Sudden spikes may indicate replay loops or unstable identity. |
| `reconciliation_mismatch_count` | Count/key/hash/aggregate differences | Block publication for critical mismatches. |
| `source_read_bytes/ops/capacity` | Cost and load imposed on source | Set budgets; limit scan concurrency and poll frequency. |
| `CDC_disk_usage` | Cassandra CDC segment disk pressure | Alert before source-side retention/backpressure risk. |
| `target_commit_duration` | Silver merge/commit time | Helps distinguish source lag from target bottlenecks. |

Logs should include `source`, `entity`, `run_id`, `snapshot_id`, `event_identity`, checkpoint before/after, target commit, and error category. Do not log secrets, payment details, or full sensitive payloads in ordinary application logs.

## 15. Managed ingestion vs custom pipeline

Options in the roadmap include Atlas Data Federation, DynamoDB zero-ETL integrations, AWS Glue/Databricks connectors, Airbyte, Fivetran, `dlt`, Kafka, and Debezium. They are not equivalent products: some query/export data, some replicate changes, some orchestrate batch syncs, and some capture logs into a stream. Confirm source/destination support and semantics in current documentation before selecting one.

| Option | Often a fit when | Questions to answer first |
|---|---|---|
| Native managed integration (for example, a DynamoDB zero-ETL path where supported) | Low operational burden and an approved managed path are priorities | Which regions/engines/destinations are supported? What is the freshness, delete, schema, replay, and cost contract? |
| Atlas Data Federation / Atlas export/query options | Atlas-hosted data needs federated access or export | Is the goal querying, snapshot export, or continuous CDC? Does it meet the latency and replay requirements? |
| AWS Glue or Databricks connectors | Batch/ETL integration fits the platform and source connector is supported | Is it a snapshot reader or true change capture? Which connector version and feature limitations apply? |
| Airbyte / Fivetran | Standard connectors, managed operations, and faster delivery justify the service | Verify exact connector's incremental/deletes behavior, sync modes, schema changes, log retention, and pricing. |
| `dlt` | Python-oriented ingestion and destination loading suit the use case | It is a framework, not a universal database CDC source; check extractor support and whether source semantics are polling or CDC. |
| Kafka + Debezium + sink | Low-latency, durable streaming and control over routing are required | Can the team operate Kafka Connect, schema governance, offsets, rebalances, DLQs, upgrades, and retention? |
| Custom Python consumer | Narrow source scope and bespoke logic justify ownership | Team must implement retries, checkpoints, schema policy, replay, observability, and disaster recovery correctly. |

**Build vs buy:** compare total cost of ownership, not license price alone. Include infrastructure, engineering/on-call time, source load, connector limits, support, schema evolution, security, recovery, and exit/migration costs. Pilot the hardest requirement (usually delete fidelity, initial snapshot handoff, and retention-expiry recovery) before committing.

## 16. Required hands-on exercises

Create the directory exactly as specified by the roadmap:

```text
experiments/09_nosql_to_lakehouse/
├── README.md
├── compose.yaml                 # local services; pin versions
├── data/generate_orders.py      # deterministic synthetic data
├── src/mongodb_consumer.py
├── src/dynamodb_stream_consumer.py
├── src/normalize_orders.py
├── src/merge_current_state.sql
├── src/schema_contract.py
├── runbooks/mongodb_resume_token_expired.md
├── tests/test_dedup_and_deletes.py
└── outputs/                     # local experiment outputs; do not commit secrets
```

Create the scaffold before starting (from the repository root):

```bash
mkdir -p experiments/09_nosql_to_lakehouse/{data,src,runbooks,tests,outputs}
touch experiments/09_nosql_to_lakehouse/README.md
```

Use pinned image/package versions and a disposable local dataset. `uv` project dependencies can include `pymongo`, `boto3`, `pytest`, `pyarrow`, `pyspark` (if using Spark), and the appropriate Delta/Iceberg runtime. Use only services needed for each exercise. Do not assume DynamoDB Local reproduces managed AWS exports/zero-ETL, and do not claim a local stream has the same retention or scaling behavior as the cloud service.

### Exercise 1 — Five-store extraction matrix

**Goal:** For MongoDB, DynamoDB, Cassandra, Elasticsearch/OpenSearch, and Neo4j, document full copy, incremental changes, and deletes.

**Setup:** Read the store-specific sections above; select exact local or managed versions; create `experiments/09_nosql_to_lakehouse/README.md`.

**Steps:** For each store, write a one-page table with source of truth, full-copy method, native or connector change path, source position, ordering scope, delete representation, retention, snapshot consistency boundary, schema behavior, permissions, and estimated source-read cost. Mark each feature `native`, `connector-dependent`, `application-event`, `polling`, or `not available in this setup`.

**Expected outcome:** A capability matrix grounded in the exact chosen versions, with no generic “CDC supported” claim.

**Validation:** A reviewer can identify how a delete is captured and how the pipeline recovers after the source position expires for all five stores.

**Failure scenarios / troubleshooting:** If docs disagree, record the product and connector version and inspect the exact connector reference. If the store is only a derived index, identify its upstream owner. If no reliable delete path exists, add an outbox/audit design or mark the solution insufficient.

### Exercise 2 — Draw and critique snapshot-to-stream handoff

**Goal:** Identify gaps, duplicates, and stale overwrites.

**Setup:** Use the handoff diagram in Section 8 and choose one source with a documented snapshot/change boundary.

**Steps:** Draw three timelines: (a) scan then stream, (b) stream then scan, (c) source-supported coordinated snapshot+log. Add concurrent insert, update, and delete events at the worst possible moments. Label snapshot boundary, durable stream start, checkpoint commit, and publication point.

**Expected outcome:** The diagram demonstrates why naïve sequencing is unsafe and why ordering/reconciliation is needed.

**Validation:** For each timeline, state whether the event is lost, duplicated, or can overwrite newer state; describe the mechanism that prevents or detects it.

**Failure scenarios / troubleshooting:** If the source exposes no common boundary/version, do not claim provable gap-free capture. Choose best-effort overlap plus full reconciliation or a supported connector protocol.

### Exercise 3 — MongoDB resume-token restart

**Goal:** Persist tokens and restart without losing recoverable events.

**Setup:** Run MongoDB as a replica set, enable the replica set, install compatible PyMongo, and create `shop.orders`. Implement durable Bronze storage and a checkpoint collection or file/database checkpoint with atomic replacement.

**Steps:** Start consumer; insert/update/delete several orders; verify each raw event is durable; kill the consumer after Bronze write but before checkpoint and restart; then kill it after checkpoint commit and verify the event had already been durably written. Resume using the last committed token. Track duplicates by token/event identity.

**Expected outcome:** Recoverable events are present at least once in Bronze; replay duplicates are detected; no event is acknowledged by a checkpoint before durable landing.

**Validation:** Assert every expected operation is represented in Bronze or documented quarantine, the checkpoint never moves ahead of durable data, and replay does not duplicate current-state rows.

**Failure scenarios / troubleshooting:** A standalone MongoDB deployment cannot test change streams; use a replica set. If token is rejected, check stream definition, token serialization, invalidate events, and oplog history. Do not reset token to latest without reconciliation.

### Exercise 4 — Initial snapshot and gap-free transition

**Goal:** Snapshot a collection and transition to change capture without gaps.

**Setup:** Use a connector/source with a documented consistent snapshot+log-position protocol. If the local exercise uses a manually orchestrated PyMongo stream and scan, explicitly mark it as a bounded simulation unless a shared source boundary can be proven.

**Steps:** Generate concurrent order inserts, updates, and deletes while the snapshot runs. Land snapshot rows with `snapshot_id` and stream events with native token. Apply the documented handoff protocol. Merge into a staging table using source ordering/version; reconcile key set, counts, sampled values, and deletes.

**Expected outcome:** A repeatable process with explicit boundary and reconciliation evidence. If the selected local method cannot guarantee a consistent boundary, the expected outcome is a documented limitation and detected mismatches—not a false claim of zero gaps.

**Validation:** Repeat the run; assert no unexplained missing keys, no stale overwrite, and no unexplained duplicate current-state keys. Save reconciliation output with the run ID.

**Failure scenarios / troubleshooting:** Stale snapshot overwrites indicate missing ordering/version logic. Missing keys indicate incomplete scan/range checkpointing. Unmatched deletes require an explicit tombstone or authoritative source reconciliation.

### Exercise 5 — DynamoDB Local stream to Parquet/Delta

**Goal:** Consume stream records and apply them idempotently, including deletes.

**Setup:** Run DynamoDB Local (or LocalStack), create an `Orders` table with a key schema and stream view type such as `NEW_AND_OLD_IMAGES`, and install Boto3. For Parquet, install `pyarrow`; for Delta, use a compatible Spark/Delta environment. Document local-service limitations.

**Steps:** Insert, modify, and delete items. Discover stream ARN and shards; consume records with a checkpoint per shard/sequence. Write normalized raw events to JSON or Parquet. Stage one winning event per key and apply a target `MERGE`/equivalent with tombstones. Restart the consumer and replay a batch.

**Expected outcome:** Parquet files or Delta table rows contain the captured changes; deletes result in a tombstone/current-state deletion according to policy; replay is idempotent.

**Validation:** Assert source operation counts match landed+quarantined+pending accounting; run duplicate-key and delete assertions; compare final target state with a source scan after writes stop.

**Failure scenarios / troubleshooting:** Empty stream: verify stream enabled before writes and stream ARN refreshed. Missing records: inspect shard enumeration, iterator expiration, checkpoint scope, and local emulator version. Parquet alone is append-only; use a table engine or downstream merge process for current-state semantics.

### Exercise 6 — Nested orders: Bronze to Silver and child tables

**Goal:** Preserve keys while flattening nested documents and arrays.

**Setup:** Generate deterministic nested order documents with stable `line_id`, optional nested shipping/payment objects, and several items per order. Land source documents and event envelopes separately.

**Steps:** Write immutable Bronze JSON; parse using a versioned schema; create `silver.orders` and `silver.order_items`; apply a parent update that changes an item and removes another; ensure the removed child is tombstoned or deleted using a complete-parent-image policy. Add validation for orphan items and duplicate keys.

**Expected outcome:** One current row per order and one current row per child key; nested fields are typed; raw payload remains available.

**Validation:** Verify `(order_id, line_id)` uniqueness, parent-child referential integrity, decimal/timestamp parsing, and removed-child handling.

**Failure scenarios / troubleshooting:** Array index used as a key causes item identity shifts. `explode_outer` can produce null child rows; filter them appropriately. Partial update events need reconstruction or full-image handling before child replacement.

### Exercise 7 — Schema drift and quarantine

**Goal:** Detect additive and incompatible changes.

**Setup:** Use the nested orders generator and a versioned schema contract.

**Steps:** Add optional field `gift_message`; then change `total` from numeric to a string with both valid and invalid formats; then omit a required `_id`. Capture each event. Fingerprint schemas, classify changes, approve the additive field, quarantine incompatible values and missing keys, and replay corrected quarantined records after policy update.

**Expected outcome:** New field is visible in drift metrics; approved additive change can be evolved deliberately; invalid types and missing keys are quarantined with raw evidence.

**Validation:** Check schema fingerprints, error categories, quarantine counts, replay idempotency, and no silent conversion of invalid monetary values.

**Failure scenarios / troubleshooting:** Inference may vary with sample size; compare against a versioned contract. If a field changes types across records, define an explicit coercion rule or retain raw plus a normalized nullable field.

### Exercise 8 — Idempotent MERGE including deletes

**Goal:** Prove duplicate delivery and stale replay do not corrupt current state.

**Setup:** Create a staging dataset containing insert/update/delete events, duplicates, and out-of-order events for the same key. Include a real comparable version in the test data.

**Steps:** Deduplicate by event identity; select the winning event per key using source version; merge into current state; replay the same batch; then replay an older update after a delete. Store tombstones or a version ledger so the stale event cannot resurrect the row.

**Expected outcome:** Replaying the same batch changes no final values; older events do not overwrite newer state; deletes remain effective.

**Validation:** Compare table snapshot before/after duplicate replay; assert one row per key, source version monotonicity, and deleted-key behavior.

**Failure scenarios / troubleshooting:** If the source provides no comparable cross-event version, do not invent one from arrival time. Restrict ordering scope, use connector-specific offsets where valid, or route conflicts to reconciliation.

### Exercise 9 — MongoDB resume-token-expired runbook

**Goal:** Write an actionable recovery playbook.

**Setup:** Use `runbooks/mongodb_resume_token_expired.md` and the checklist in Section 12.3.

**Steps:** Document alert signals, impact assessment, evidence to preserve, how to distinguish expiry from invalid stream context/transient errors, supported snapshot+stream recovery, target staging, reconciliation gates, publication, customer impact, and recurrence prevention. If the local setup cannot safely force real oplog expiry, simulate an invalid/unknown token and label it a control-flow simulation, not a retention-expiry test.

**Expected outcome:** An on-call engineer can recover without blindly resetting to “now” or claiming completeness.

**Validation:** Have a second person walk the runbook against a failure-injection checklist; every step has an owner, command/source of evidence, and exit criterion.

**Failure scenarios / troubleshooting:** If source history and raw archive are both unavailable, quantify the irrecoverable interval, rebuild current state from a snapshot, document uncertainty, and obtain business sign-off before claiming recovery complete.

## 17. Common mistakes

- Running repeated large analytical scans against the production operational store without read budgets.
- Treating timestamp polling as complete CDC and overlooking hard deletes or missing timestamps.
- Opening a stream only after a snapshot and assuming no gap exists.
- Assuming MongoDB `updateLookup` is the exact post-image at the triggering event time.
- Assuming resume tokens, stream records, or CDC logs are retained forever.
- Committing a checkpoint before raw event durability.
- Assuming Kafka guarantees exactly-once effects across every external sink.
- Using arrival time as a universal ordering key.
- Dropping delete events because they lack a full document.
- Inferring deletes from absence in an incomplete or non-consistent scan.
- Flattening arrays with array positions as durable business keys.
- Replacing child tables on a partial update without reconstructing the complete parent state.
- Automatically coercing schema drift or silently enabling schema evolution.
- Treating Elasticsearch/OpenSearch as a canonical source without verifying ownership and index semantics.
- Assuming Neo4j has a universal CDC feed across editions/versions.
- Assuming Debezium connector maturity/version support is identical for MongoDB and Cassandra.
- Treating DynamoDB Local as a complete simulation of managed exports, zero-ETL, IAM, retention, or scaling.
- Publishing a new snapshot without recording its boundary, range coverage, and reconciliation results.

## 18. Practice questions

1. A collection scan finishes at 10:00 and a change stream starts at 10:02. What class of writes may be missing, and why does overlap alone not prove correctness?
2. Why is `updated_at > watermark` vulnerable when timestamps have millisecond precision and multiple updates share the same value?
3. What is the difference between a MongoDB resume token and a source event timestamp?
4. When is `fullDocument: "updateLookup"` insufficient for exact event-time history?
5. How do DynamoDB Streams and Kinesis differ in retention configuration and checkpoint model?
6. Why can Cassandra TTL expiration and tombstone compaction complicate delete history?
7. If an Elasticsearch document disappears from a scan, what alternative explanations exist besides a business delete?
8. Why should Neo4j relationship IDs be preserved separately from node IDs?
9. How do you prevent an old replayed update from resurrecting a deleted order?
10. What should happen if two conflicting events for one key have no comparable source version?
11. Why is raw Bronze useful when a schema change is discovered after the initial load?
12. What can counts, key-set comparisons, hashes, and sampled row comparisons each reveal—and miss?
13. Which connector features must be checked before relying on Debezium Cassandra in production?
14. What evidence is required before declaring an expired-token recovery complete?
15. Which source-read and lag metrics should page the team before a retention window is exceeded?

## 19. Checkpoints and self-assessment

Mark each item only when you can demonstrate it in the lab or explain the limitation precisely.

- [ ] Explain snapshots, timestamp polling, CDC, and change streams without treating them as synonyms.
- [ ] For all five stores, document full-copy, change-capture, delete, retention, and ordering semantics for the actual version.
- [ ] Explain why a timestamp watermark can miss deletes and updates.
- [ ] Persist and resume a MongoDB change-stream token after a restart, with durable raw landing before checkpoint advancement.
- [ ] Explain DynamoDB Streams retention and the differences among Streams, Kinesis, and S3 exports.
- [ ] Describe Cassandra CDC configuration/backlog risks and verify connector maturity/version support.
- [ ] Design a defensible snapshot-to-stream handoff and name cases where a local simulation cannot prove gap-free capture.
- [ ] Build Bronze raw-event storage and typed Silver order/child tables with stable keys.
- [ ] Apply duplicate, out-of-order, update, and delete events idempotently without stale resurrection.
- [ ] Detect additive and incompatible schema drift and quarantine invalid records.
- [ ] Execute count/key/hash/sample reconciliation after snapshot, handoff, and recovery.
- [ ] Write and rehearse the expired-resume-token runbook.
- [ ] Monitor lag, checkpoint age, failed positions, quarantine, reconciliation mismatches, and source-read cost.
- [ ] Make a reasoned build-versus-buy recommendation with version-specific feature evidence.

**Ready to move on when:** you can explain not only how events reach the lakehouse, but what proves that the data is complete enough for its stated SLA—and what you do when that proof fails.

## 20. References and version discipline

Treat the following vendor/project documentation as the authority for the exact versions you deploy. Product features and connector support change; record the version checked in your lab README and re-check before production rollout.

- MongoDB Change Streams (resume tokens and full-document lookup): https://www.mongodb.com/docs/manual/changestreams/
- MongoDB change-stream update event and pre/post-images: https://www.mongodb.com/docs/manual/reference/change-events/update/
- Debezium release overview and tested versions: https://debezium.io/releases/
- Debezium MongoDB connector: https://debezium.io/documentation/reference/stable/connectors/mongodb.html
- Debezium supported source connectors (incubating status is version-dependent): https://debezium.io/documentation/reference/stable/connectors/
- AWS Glue MongoDB connections: https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-connect-mongodb-home.html
- DynamoDB Streams developer guide: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html
- Kinesis Data Streams for DynamoDB: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/kds.html
- AWS comparison of DynamoDB Streams and Kinesis Data Streams for DynamoDB: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/streamsmain.html
- DynamoDB export to S3: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/S3DataExport.HowItWorks.html
- Apache Cassandra CDC documentation: https://cassandra.apache.org/doc/latest/cassandra/managing/operating/cdc.html
- Debezium 3.6 Cassandra connector documentation (connector architecture and ignored feature classes): https://debezium.io/documentation/reference/3.6/connectors/cassandra.html
- Elasticsearch Point in Time API: https://www.elastic.co/guide/en/elasticsearch/reference/current/point-in-time-api.html
- OpenSearch point-in-time/search pagination documentation: https://docs.opensearch.org/latest/search-plugins/searching-data/point-in-time/
- Neo4j documentation: https://neo4j.com/docs/
- Delta Lake `MERGE` documentation: https://docs.delta.io/delta-update.html
- Apache Iceberg documentation: https://iceberg.apache.org/docs/latest/
- Airbyte documentation: https://docs.airbyte.com/
- Fivetran documentation: https://fivetran.com/docs
- `dlt` documentation: https://dlthub.com/docs

### Technical boundary note

This lesson describes architecture and illustrative code; it does not claim that any lab was executed or that any benchmark or recovery result was measured. Confirm current product docs for managed integrations (including Atlas Data Federation, DynamoDB zero-ETL, Glue/Databricks connectors, Airbyte, Fivetran, and `dlt`) before relying on a specific source, destination, region, retention, delete, or schema-evolution capability. Where a source does not expose a reliable change feed, design an application event/outbox or label the polling/reconciliation approach as best-effort.
