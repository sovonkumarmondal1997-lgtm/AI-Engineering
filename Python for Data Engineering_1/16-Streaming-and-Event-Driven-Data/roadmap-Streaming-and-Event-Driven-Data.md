# Roadmap — Module 2.16: Streaming and Event-Driven Data

This is the learning roadmap for the sixteenth module of Stage 2, **Python
for Data Engineering**. It tells you **what** to learn about streaming and
event-driven data, **in what order**, **how** to learn each topic, and
**how to prove to yourself** that you have learned it before you move on.

Until now, almost everything you built ran in **batches**: a run for
yesterday, a backfill for last March. Many businesses need data sooner —
fraud decisions in seconds, live operational dashboards, inventory that
updates as orders arrive, CDC replication with minutes of delay, and
features for ML models computed as events happen. That requires treating
data as an **unbounded, continuous stream of events**.

Streaming is not "batch, but faster". It brings new problems: events arrive
late and out of order, processes restart in the middle of a computation,
state must survive failures, duplicates are the default, and a slow
consumer can silently fall days behind. This module teaches the concepts
that are the same across every streaming system (delivery semantics, event
time, watermarks, windows, state), the de-facto standard platform (Apache
Kafka), and the main processing engines you will meet (Spark Structured
Streaming and Apache Flink) — all from Python.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain event streams vs message queues and choose between them;
  describe common event-driven architecture patterns.
- Explain Kafka's model — topics, partitions, offsets, replication, and
  retention — and design topics for a workload.
- Write reliable Kafka **producers** and **consumers** in Python, including
  keys, batching, acknowledgements, consumer groups, rebalances, and
  offset commits.
- Explain and implement **at-most-once, at-least-once, and exactly-once**
  processing, and know which one you actually have.
- Define event schemas with **Protobuf** (and Avro), manage them in a
  **schema registry**, and evolve them safely.
- Reason about **event time vs processing time**, **watermarks**, and
  late data.
- Use **tumbling, sliding, and session windows** correctly.
- Build **stateful** stream processing (aggregations, deduplication, joins)
  with fault-tolerant state.
- Build pipelines with **Spark Structured Streaming** and understand
  **Apache Flink / PyFlink** and when to choose it.
- Stream database changes with **Debezium** into Kafka and apply them to
  lakehouse tables.
- Monitor **consumer lag**, handle **backpressure**, and scale consumers.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.15. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Processes, networking, Docker Compose | Stage 0 | Running brokers, registries, and connectors locally |
| Generators, context managers, retries, logging | Stage 1 — Modules 1.9–1.10 | Consumer loops, graceful shutdown, and safe logging |
| Batch vs micro-batch vs streaming, freshness SLAs | Stage 2 — Module 2.1 | Deciding when streaming is worth its cost |
| Avro files and schema resolution | Stage 2 — Module 2.5 | Avro mechanics are **not** re-taught; this module adds registries and Protobuf |
| SQL `MERGE`, transactions | Stage 2 — Module 2.6 | Idempotent streaming sinks |
| Event modelling, sessions, identity | Stage 2 — Module 2.8 | What the events mean and how they are modelled |
| Webhooks, at-least-once delivery, **CDC concepts** and logical decoding | Stage 2 — Module 2.9 | Debezium builds on these; concepts **not** re-taught |
| Queues, back pressure, graceful shutdown, asyncio | Stage 2 — Module 2.10 | In-process versions of the ideas used here at scale |
| Schema compatibility modes, dead-letter handling, anomaly checks | Stage 2 — Module 2.11 | Applied to topics and streams |
| Deduplication, merge loads, late data in batch, state and checkpoints | Stage 2 — Module 2.12 | The batch counterparts of this module's patterns |
| Orchestration and continuous jobs | Stage 2 — Module 2.13 | Where streaming jobs sit alongside batch DAGs |
| Spark DataFrames, plans, partitions, the Spark UI | Stage 2 — Module 2.14 | Structured Streaming uses the same API |
| Delta and Iceberg tables, `MERGE`, compaction | Stage 2 — Module 2.15 | Streaming sinks into the lakehouse |

**Tools needed:**

- Docker Compose with: **Apache Kafka 4.x** (KRaft mode — no ZooKeeper), a
  **schema registry**, **Kafka Connect with Debezium**, a Kafka web UI,
  PostgreSQL (with logical replication), and MinIO.
- Python 3.12+ in a `uv` project: `uv add "confluent-kafka[protobuf,avro,schemaregistry]"
  protobuf pyspark apache-flink pytest` (check PyFlink's supported Python
  versions), plus the Spark Kafka connector package and the Protobuf
  compiler or `buf`.
- A Kafka-compatible alternative such as Redpanda is fine for lighter local
  development.

**A note on versions:** Kafka 4 removed ZooKeeper, and recent releases add
features such as a new consumer rebalance protocol and queue-style "share
groups". Flink 2.x and Spark 4.x also introduced streaming changes. Many
tutorials are older — check behaviour against the versions you run.

---

## 3. How the module is organised

The thirteen topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — Streaming Foundations                     (Basics)
  01 Event streams vs message queues
  02 Kafka: topics, partitions, offsets, and replication

Phase B — Kafka Clients and Guarantees              (Intermediate → Advanced)
  03 Kafka producers in Python
  04 Kafka consumers and consumer groups
  05 Delivery semantics: at-most-once, at-least-once, exactly-once
  06 Protobuf and schema registry

Phase C — Stream Processing Concepts                (Intermediate → Advanced)
  07 Event time, processing time, and watermarks
  08 Tumbling, sliding, and session windows
  09 Stateful stream processing

Phase D — Stream Processing Engines                 (Advanced)
  10 Spark Structured Streaming
  11 Apache Flink and PyFlink overview

Phase E — Integration and Operations                (Advanced)
  12 Debezium CDC streams into Kafka
  13 Backpressure and consumer lag

Consolidate
  practice-questions.md
  interview-practice.md
  Module mini-project: a real-time order analytics platform
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09 ► 10 ► 11 ► 12 ► 13
why  the  write read  guar- con-  time  win-  state Spark Flink CDC  keep up
logs log            antees tracts       dows              in    with the
                                                          stream stream
```

Why this order:

- The log model (01–02) explains every Kafka behaviour that follows.
- You produce (03) before you consume (04); delivery semantics (05) only
  make sense once you know both sides; schemas (06) protect both.
- Time (07), windows (08), and state (09) are engine-independent concepts
  that must be understood before engines (10–11) implement them.
- Debezium (12) combines Kafka, schemas, and CDC concepts from Module 2.9.
- Lag and backpressure (13) are the operational view of everything above.

---

## 4. Suggested schedule

About **6 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — streams vs queues · Topic 02 — Kafka fundamentals (run a cluster) |
| 2 | Topic 03 — producers · Topic 04 — consumers and groups |
| 3 | Topic 05 — delivery semantics · Topic 06 — Protobuf and schema registry |
| 4 | Topic 07 — event time and watermarks · Topic 08 — windows · Topic 09 — state |
| 5 | Topic 10 — Spark Structured Streaming · Topic 11 — Flink and PyFlink |
| 6 | Topic 12 — Debezium · Topic 13 — backpressure and lag · practice · interview practice · mini-project |

---

## 5. How to study every topic (the streaming loop)

```text
Read → Draw the flow with time → Predict ordering, duplicates, lateness
→ Build it → Replay it → Kill it (consumer, broker, job) → Restart it
→ Verify results against a batch recomputation → Measure lag & latency
→ Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Draw the flow with time**: producers, topics and partitions,
   consumers, state, sinks — and a timeline of events with their event
   times and arrival times.
3. **Predict** ordering, duplicates, and lateness before running anything.
4. **Build it** with a deterministic **event generator** you control
   (configurable rate, keys, out-of-order delay, duplicates, bad records).
5. **Replay it**: reset offsets and reprocess; results must be the same.
6. **Kill it**: stop consumers, brokers, or jobs at random points.
7. **Restart it** from committed offsets or checkpoints.
8. **Verify** streaming results against a **batch recomputation** of the
   same events (with DuckDB or Spark batch) — the streaming answer should
   converge to the batch answer.
9. **Measure** end-to-end latency, throughput, and consumer lag.
10. **Write down** what you learned in `module-2.16-notes.md`.
11. **Explain aloud** what happens to each event during a failure and
    restart.

Keep one `streaming_lab/` project:

```text
streaming_lab/
├── docker-compose.yml   # Kafka (KRaft), schema registry, Connect + Debezium, UI, PostgreSQL, MinIO
├── schemas/             # .proto and .avsc files (versioned)
├── generator/           # event generator with lateness, duplicates, and bad-record switches
├── src/streaming_lab/   # producers, consumers, Spark and Flink jobs
├── checkpoints/         # local checkpoint directories (git-ignored)
└── tests/
```

---

## 6. Phase A — Streaming Foundations (Basics)

### Topic 01 — [Event streams vs message queues](01-event-streams-vs-message-queues.md)

**Why it comes first:** "Kafka", "RabbitMQ", "SQS", and "Pub/Sub" are often
used interchangeably, but they make very different promises. Choosing
wrongly shapes an entire architecture.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Events (facts that happened) vs commands (requests to do something) vs messages |
| Basics | **Message queues** (e.g. RabbitMQ, SQS): messages delivered to one consumer, acknowledged, and removed |
| Basics | **Event streams / logs** (e.g. Kafka, Kinesis, Pulsar, Redpanda, Event Hubs): an append-only, ordered, retained log that many consumers read independently at their own positions |
| Intermediate | Differences that matter: retention and **replay**, ordering guarantees, fan-out to many consumers, per-message acknowledgement vs offset tracking, throughput |
| Intermediate | Choosing: task distribution and work queues → queues; data pipelines, replayable history, and many independent consumers → streams |
| Intermediate | Where streaming is worth it vs micro-batch or batch (latency needs vs cost and complexity, from Module 2.1) |
| Advanced | **Event-driven architecture patterns**: event notification, event-carried state transfer, event sourcing, CQRS, and the transactional outbox |
| Advanced | Designing good events: immutable, self-describing, with ids, timestamps, and versions (links to event modelling in Module 2.8) |
| Advanced | Hybrids and convergence: queue-like consumption on logs (e.g. Kafka share groups) and log-like features in queue services — awareness |
| Advanced | The streaming landscape: brokers, stream processors (Spark, Flink, Kafka Streams), and streaming databases — awareness |

**How to learn it**

1. Read the topic file.
2. For ten use cases (send welcome email, fraud scoring, CDC replication,
   clickstream analytics, image-resizing jobs, inventory updates, audit
   log, ML feature updates, nightly report trigger, IoT telemetry), choose
   queue, stream, or batch, and justify.
3. Draw one system using event notification and the same system using
   event-carried state transfer; list the trade-offs.

**Hands-on exercise — `experiments/01_queue_vs_log/`**

1. Using an in-process queue (Module 2.10) and a Kafka topic, send the same
   1,000 events to two consumers; show that the queue splits them while
   the log gives each consumer every event.
2. Replay the Kafka topic from the beginning for a new consumer; show that
   a queue cannot do this.
3. Write a one-page "queue or stream?" decision guide.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain the difference between queues and logs.
- [ ] Explain why replay matters for data pipelines.
- [ ] Describe four event-driven architecture patterns.
- [ ] Decide when streaming is worth its cost.

**Common mistakes:** using a queue where several teams need the same
events; treating commands as events; adopting streaming where hourly batch
would meet the SLA.

---

### Topic 02 — [Kafka: topics, partitions, offsets, and replication](02-kafka-topics-partitions-offsets-and-replication.md)

**Why here:** Kafka is the most common event streaming platform in data
engineering. Its core abstractions — partitioned, replicated logs — decide
ordering, parallelism, durability, and cost.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Brokers**, **topics**, **partitions**, **offsets**; records with key, value, headers, and timestamp |
| Basics | Ordering: guaranteed **within a partition**, not across partitions; the record **key** decides the partition |
| Basics | Running Kafka locally in **KRaft** mode; the CLI tools and a web UI |
| Intermediate | **Replication**: leaders, followers, replication factor, **in-sync replicas (ISR)**, `min.insync.replicas`, and what happens when a broker fails |
| Intermediate | **Retention**: time- and size-based deletion vs **log compaction** (keep the latest value per key — useful for changelogs and CDC state) |
| Intermediate | Choosing partition counts: target throughput, consumer parallelism, key distribution, and the cost of too many partitions |
| Intermediate | Topic design: naming conventions, one event type per topic vs several, key choice for ordering and even distribution |
| Advanced | Hot partitions from skewed keys (the streaming form of Module 2.14's skew) |
| Advanced | Segments and storage; tiered storage for long retention (awareness) |
| Advanced | KRaft controllers vs the old ZooKeeper-based architecture (recognising it in older setups) |
| Advanced | Managed Kafka and Kafka-compatible services (Module 2.17) — awareness |

**How to learn it**

1. Read the topic file.
2. Run a three-broker KRaft cluster in Docker; create topics with
   different partition counts and replication factors; inspect them.
3. Stop a broker and observe leadership changes and under-replicated
   partitions.

**Hands-on exercise — `experiments/02_kafka_basics/`**

1. Produce keyed events with the console tools and confirm that each key
   always lands in the same partition.
2. Create an `orders` topic (6 partitions, replication factor 3,
   `min.insync.replicas=2`) and a compacted `customer_state` topic;
   explain every setting.
3. Kill one broker, then two, and document when writes with the strongest
   acknowledgement settings (Topic 03) start failing.
4. Produce events with a heavily skewed key distribution and show the hot
   partition.
5. Write a topic design document for your mini-project's events.

**Checkpoint:**

- [ ] Explain topics, partitions, offsets, and keys.
- [ ] Explain Kafka's ordering guarantee.
- [ ] Explain replication, ISR, and `min.insync.replicas`.
- [ ] Explain deletion vs compaction retention.
- [ ] Choose partition counts and keys for a workload.

**Common mistakes:** expecting global ordering across partitions; a
replication factor of 1 in production; far too many partitions "for
future scale"; keys that concentrate traffic on one partition.

---

## 7. Phase B — Kafka Clients and Guarantees (Intermediate → Advanced)

### Topic 03 — [Kafka producers in Python](03-kafka-producers-in-python.md)

**Why here:** Producers decide whether events are durable, ordered, and
duplicated — before any consumer sees them.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The `confluent-kafka` `Producer`: configuration, `produce()`, delivery callbacks, `poll()`, and `flush()` |
| Basics | Keys, values, headers, and serialisation (bytes, JSON, and schema-based formats in Topic 06) |
| Basics | Asynchronous sending: why `produce()` returns immediately and delivery is confirmed later |
| Intermediate | **Acknowledgements**: `acks=0`, `acks=1`, `acks=all` — durability vs latency |
| Intermediate | **Idempotent producer** (`enable.idempotence`): no duplicates from producer retries, ordering preserved — set it explicitly |
| Intermediate | Retries and timeouts (`delivery.timeout.ms`, `retries`), and what happens to events that finally fail |
| Intermediate | Throughput tuning: `linger.ms`, batch size, compression (`zstd`, `lz4`, `snappy`) |
| Intermediate | **Partitioners**: the default partitioner in the Python client differs from the Java client's; set it explicitly when keys must map to the same partitions across languages |
| Advanced | Producing from services safely: flushing on shutdown, handling a full local buffer, and never losing events silently |
| Advanced | Message size limits and patterns for large payloads (store in object storage, send a reference) |
| Advanced | The **transactional outbox**: writing events to a database table in the same transaction as business data and publishing them via CDC (Topic 12) instead of dual writes |
| Advanced | Async producers (e.g. with asyncio clients) — awareness |

**How to learn it**

1. Read the topic file.
2. Produce 1 million events with different `acks`, `linger.ms`, and
   compression settings; measure throughput and latency.
3. Kill a broker mid-send with and without idempotence; count duplicates.

**Hands-on exercise — `src/streaming_lab/producers.py`**

1. Build an `OrderEventProducer` with `acks=all`, idempotence, compression,
   delivery callbacks that log failures, and a clean `flush()` on
   shutdown (`SIGTERM` handling from Module 2.10).
2. Build the **event generator**: order, payment, and click events with
   configurable rate, key skew, out-of-order delays, duplicates, and bad
   records.
3. Benchmark three configurations (low latency, balanced, high throughput).
4. Prove that the same key maps to the same partition as a Java/CLI
   producer when the partitioner is set explicitly.
5. Implement an outbox table in PostgreSQL (published later via Debezium in
   Topic 12).

**Checkpoint:**

- [ ] Configure a durable, idempotent Python producer.
- [ ] Explain `acks` and idempotence trade-offs.
- [ ] Tune batching and compression for throughput.
- [ ] Explain why dual writes are dangerous and how the outbox helps.

**Common mistakes:** never calling `poll()`/`flush()` (events lost on exit);
`acks=1` for critical data; ignoring delivery errors; mismatched
partitioners between languages; writing to a database and Kafka in two
separate steps.

---

### Topic 04 — [Kafka consumers and consumer groups](04-kafka-consumers-and-consumer-groups.md)

**Why here:** Consumers turn the log into processing. Their offset commits
decide whether events are lost, duplicated, or processed exactly as
intended.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The `Consumer`: `group.id`, `subscribe()`, the `poll()` loop, handling errors, and `close()` |
| Basics | **Consumer groups**: partitions divided among group members; parallelism limited by partition count |
| Basics | `auto.offset.reset` (`earliest` / `latest`) for new groups |
| Intermediate | **Offset commits**: automatic vs manual; committing **after** processing; synchronous vs asynchronous commits |
| Intermediate | **Rebalances**: when members join or leave; eager vs cooperative-incremental assignment; rebalance callbacks to commit or flush before losing partitions; the newer consumer group protocol (awareness) |
| Intermediate | Timeouts: `session.timeout.ms`, `max.poll.interval.ms` — and why slow processing gets a consumer kicked out of the group |
| Intermediate | Batching: processing records in batches and committing per batch |
| Advanced | Static group membership to reduce rebalances during restarts |
| Advanced | Seeking and replay: resetting offsets for reprocessing (by offset or timestamp) |
| Advanced | Poison-pill records: deserialisation failures and bad data sent to a **dead-letter topic** instead of blocking the partition (Module 2.11) |
| Advanced | Pausing and resuming partitions for flow control (Topic 13) |
| Advanced | Idempotent sinks: writing results so that reprocessing produces the same state (upserts by event id — Module 2.12) |

**How to learn it**

1. Read the topic file.
2. Run a consumer group, scale it from 1 to 8 members on a 6-partition
   topic, and observe assignments and idle consumers.
3. Make processing slower than `max.poll.interval.ms` and observe the
   rebalance storm.

**Hands-on exercise — `src/streaming_lab/consumers.py`**

1. Build an `OrderConsumer` that processes batches, writes to PostgreSQL
   with an idempotent upsert keyed by event id, and commits offsets only
   after the database commit.
2. Add rebalance callbacks that flush in-progress batches before
   partitions are revoked.
3. Route undeserialisable and invalid records to `orders.dlq` with error
   headers, and keep processing.
4. Reset the group's offsets to a timestamp and reprocess; prove the
   database ends in the same state.
5. Kill consumers randomly during processing and verify no events are lost
   (duplicates are absorbed by the idempotent sink).

**Checkpoint:**

- [ ] Write a consumer that commits after processing.
- [ ] Explain consumer groups, partition assignment, and rebalances.
- [ ] Handle slow processing without rebalance storms.
- [ ] Route poison pills to a dead-letter topic.
- [ ] Replay a topic safely.

**Common mistakes:** auto-commit with slow or failing processing (lost
events); more consumers than partitions expecting more speed; one bad
record blocking a partition forever; non-idempotent sinks.

---

### Topic 05 — [Delivery semantics: at-most-once, at-least-once, and exactly-once](05-delivery-semantics-at-most-at-least-and-exactly-once.md)

**Why here:** "Exactly-once" is the most misunderstood phrase in
streaming. With producers and consumers understood, you can reason
precisely about what guarantees your pipeline really has — end to end.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **At-most-once**: commit before processing — failures lose events |
| Basics | **At-least-once**: commit after processing — failures cause duplicates |
| Basics | **Exactly-once**: every event affects the result exactly once — requires cooperation from every part of the pipeline |
| Intermediate | The practical formula (from Module 2.12): **at-least-once delivery + idempotent processing = exactly-once effect** |
| Intermediate | Idempotent producers (no duplicates from retries) vs end-to-end exactly-once |
| Intermediate | **Kafka transactions**: `transactional.id`, atomic writes to several topics, and `isolation.level=read_committed` for consumers |
| Intermediate | **Consume–transform–produce** with transactions: committing consumer offsets inside the producer's transaction |
| Advanced | Exactly-once into external systems: transactional sinks, idempotent upserts, deterministic output keys, or storing offsets together with results in the same database transaction |
| Advanced | How engines provide it: Spark Structured Streaming (replayable sources + checkpoints + idempotent sinks), Flink (checkpoints + two-phase-commit sinks) |
| Advanced | Side effects that cannot be exactly-once (emails, external API calls) and how to deduplicate them |
| Advanced | Proving your semantics: chaos tests that kill components and compare results with a batch recomputation |

**How to learn it**

1. Read the topic file.
2. Implement the same counter pipeline three ways (commit before, commit
   after, transactional) and kill it 50 times each; count lost and
   duplicated events.
3. Write down the guarantee of every hop in your mini-project design.

**Hands-on exercise — `src/streaming_lab/semantics.py`**

1. Build a consume–transform–produce job (`orders` → `order_totals`) with
   Kafka transactions; verify with a `read_committed` consumer that no
   partial or duplicate outputs are visible after crashes.
2. Build a consumer that stores results **and** offsets in PostgreSQL in
   one transaction, and resumes from the stored offsets on restart.
3. Run chaos tests on all variants and produce a table of lost and
   duplicated events per approach.
4. Document where a downstream side effect (e.g. a notification) could
   still happen twice, and add a deduplication key.

**Checkpoint:**

- [ ] Explain the three delivery semantics and their failure modes.
- [ ] Explain the difference between an idempotent producer and
      end-to-end exactly-once.
- [ ] Implement transactional consume–transform–produce.
- [ ] Achieve exactly-once effects in an external sink.

**Common mistakes:** believing "Kafka has exactly-once" means your whole
pipeline does; transactional producers read by `read_uncommitted`
consumers; non-idempotent sinks behind "exactly-once" engines.

---

### Topic 06 — [Protobuf and schema registry](06-protobuf-and-schema-registry.md)

**Why here:** Events are contracts between teams (Module 2.11). A schema
registry makes those contracts machine-enforced: producers cannot publish
events that consumers cannot read.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why schemas for events: compact binary encoding, types, validation, and documentation — vs untyped JSON |
| Basics | **Protobuf**: `.proto` files, messages, scalar types, `enum`, nested messages, `repeated`, `optional`, and **field numbers** |
| Basics | Generating Python classes (with `protoc` or `buf`) and serialising/deserialising messages |
| Intermediate | **Schema registry**: subjects, versions, schema ids, and compatibility modes (backward, forward, full, transitive — concepts from Module 2.11) |
| Intermediate | The wire format: each message carries a schema id so consumers can look up the schema |
| Intermediate | `confluent-kafka` serializers and deserializers for Protobuf, Avro, and JSON Schema with the registry |
| Intermediate | **Protobuf evolution rules**: never reuse or change field numbers; `reserved` for removed fields; adding fields is safe; changing types is usually not |
| Intermediate | Choosing Protobuf vs Avro vs JSON Schema (Avro file mechanics from Module 2.5) |
| Advanced | Subject naming strategies (per topic vs per record type) and multiple event types in one topic |
| Advanced | Breaking-change detection in CI (e.g. `buf breaking`, registry compatibility checks) as part of producer CI (Module 2.11) |
| Advanced | Well-known types (timestamps, wrappers), `oneof`, and defaults — pitfalls when converting to tables |
| Advanced | Registry operations: alternatives to the Confluent registry, access control, and schema references — awareness |

**How to learn it**

1. Read the topic file.
2. Write `.proto` schemas for your order, payment, and click events and
   register them.
3. Try ten schema changes and record which ones the registry accepts under
   `BACKWARD` and `FULL` compatibility.

**Hands-on exercise — `schemas/` and `src/streaming_lab/schemas.py`**

1. Define `OrderPlaced`, `PaymentCaptured`, and `PageViewed` in Protobuf
   with timestamps, enums, and nested messages; generate Python classes.
2. Switch the producer and consumers from JSON to Protobuf with the schema
   registry; compare message sizes and throughput.
3. Evolve `OrderPlaced` compatibly (add a field) and incompatibly (reuse a
   field number); show the registry rejecting the latter.
4. Add a CI script that runs a breaking-change check on every `.proto`
   change.
5. Show old consumers reading new events and new consumers reading old
   events.

**Checkpoint:**

- [ ] Write and evolve Protobuf schemas safely.
- [ ] Produce and consume with a schema registry.
- [ ] Explain registry compatibility modes and the wire format.
- [ ] Block breaking schema changes in CI.

**Common mistakes:** reusing field numbers; untyped JSON for critical
events; auto-registering schemas from any producer without review; one
topic with unrelated event types and no naming strategy.

---

## 8. Phase C — Stream Processing Concepts (Intermediate → Advanced)

### Topic 07 — [Event time, processing time, and watermarks](07-event-time-processing-time-and-watermarks.md)

**Why here:** Streaming results depend on *when* things happened, but
events arrive late and out of order. Watermarks are how every modern
engine decides when a result is "complete enough".

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Event time** (when it happened), **ingestion time** (when Kafka received it), **processing time** (when your code saw it) |
| Basics | Out-of-order and late events: mobile clients offline, network delays, retries, partition interleaving |
| Basics | Why processing-time results are non-deterministic and change on replay |
| Intermediate | **Watermarks**: the engine's estimate that "no more events older than T are expected"; how watermarks advance from observed event times |
| Intermediate | **Bounded out-of-orderness**: watermark = max event time seen − allowed delay |
| Intermediate | **Allowed lateness** and **late data handling**: drop, update earlier results, or route to a side output / late-data topic |
| Intermediate | The core trade-off: **latency vs completeness** (a longer delay waits for more late data but emits results later) |
| Advanced | Watermarks across partitions and sources: the minimum wins; idle partitions stalling watermarks and idleness handling |
| Advanced | Clock skew and bad timestamps (events from the future), and validating event times |
| Advanced | Choosing the delay from measured lateness distributions (the same method as Module 2.12's reprocessing windows) |
| Advanced | Correcting results after the stream: combining streaming outputs with periodic batch reconciliation (Module 2.11) |

**How to learn it**

1. Read the topic file.
2. Generate events with a known lateness distribution; plot event time vs
   arrival time.
3. By hand, compute the watermark after each arriving event for a small
   sequence, and mark which events are late.

**Hands-on exercise — `src/streaming_lab/watermarks.py`**

1. Implement a tiny watermark tracker in plain Python over a Kafka
   consumer: bounded out-of-orderness, per-partition tracking, idle
   partition handling, and a late-event side output topic.
2. Count events per minute by processing time and by event time; replay
   the topic and show that only the event-time result is stable.
3. Measure lateness percentiles and choose a delay; show how many events
   are late at 5 s, 30 s, and 5 min delays and what latency each costs.
4. Inject events with timestamps in the future and handle them.

**Checkpoint:**

- [ ] Explain event, ingestion, and processing time.
- [ ] Explain watermarks and bounded out-of-orderness.
- [ ] Choose a lateness delay from data and explain the trade-off.
- [ ] Handle late and invalid-timestamp events explicitly.

**Common mistakes:** processing-time windows for business metrics; no
handling for late events (silently dropped); watermarks stalled by idle
partitions; trusting client timestamps blindly.

---

### Topic 08 — [Tumbling, sliding, and session windows](08-tumbling-sliding-and-session-windows.md)

**Why here:** Aggregating an infinite stream requires cutting it into
finite pieces. Windows define those pieces; watermarks decide when each
piece is finished.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Tumbling windows**: fixed-size, non-overlapping (e.g. revenue per 5 minutes) |
| Basics | **Sliding (hopping) windows**: fixed-size, overlapping, with a slide interval (e.g. 10-minute window every minute) |
| Basics | **Session windows**: dynamic windows closed by a gap of inactivity (e.g. user sessions with a 30-minute gap — Module 2.8's sessions, now in a stream) |
| Intermediate | Window assignment by event time; window start/end alignment and time zones (UTC) |
| Intermediate | When results are emitted: at watermark (final), early (speculative), and late (updates) — **triggers** |
| Intermediate | Output modes: append only final results vs update results as they change |
| Intermediate | Keyed windows (per customer, per country) and global windows |
| Advanced | Cost of sliding windows (each event in many windows) and alternatives (pre-aggregate into small tumbling windows and combine) |
| Advanced | Session windows that merge when a late event bridges two sessions |
| Advanced | Count-based windows and why they are rarely right for business metrics |
| Advanced | Verifying windowed results against batch SQL (window functions and date truncation from Module 2.6) |

**How to learn it**

1. Read the topic file.
2. For a small sequence of timestamped events, draw by hand which
   tumbling, sliding, and session windows each event belongs to.
3. Decide window types for ten metrics and justify each.

**Hands-on exercise — `src/streaming_lab/windows.py`**

1. Implement tumbling, sliding, and session windows in plain Python (with
   your Topic 07 watermark tracker) to understand the mechanics.
2. Compute revenue per 5-minute tumbling window, a 1-hour sliding average
   every 5 minutes, and user sessions with a 30-minute gap.
3. Emit early results every 30 seconds and final results at watermark;
   show late updates.
4. Recompute the same metrics in batch with DuckDB and prove the final
   streaming results match.

**Checkpoint:**

- [ ] Explain tumbling, sliding, and session windows.
- [ ] Explain triggers, early and late results, and output modes.
- [ ] Choose window types for business metrics.
- [ ] Verify windowed stream results against batch.

**Common mistakes:** local-time windows; sliding windows with tiny slides
(huge cost); session windows without a maximum length; emitting "final"
results before the watermark passes.

---

### Topic 09 — [Stateful stream processing](09-stateful-stream-processing.md)

**Why here:** Windows, deduplication, joins, and running totals all need
the processor to **remember** things between events. That memory — state —
must be correct, bounded, and survive failures.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Stateless (filter, map, parse) vs **stateful** (aggregate, deduplicate, join, detect patterns) operations |
| Basics | **Keyed state**: state partitioned by key and co-located with the partition that processes the key |
| Intermediate | **Streaming deduplication** by event id within a time bound (state that expires) |
| Intermediate | **Stream–table (stream–static) joins**: enriching events with reference data (Module 2.12 enrichment, now continuous) and keeping that data up to date |
| Intermediate | **Stream–stream joins**: matching orders with payments within a time bound; why both sides must be buffered in state and bounded by watermarks |
| Intermediate | **State stores and backends**: in-memory vs RocksDB-backed state; state size and memory |
| Intermediate | **Checkpointing**: periodically saving offsets and state so a restart resumes exactly |
| Advanced | **State TTL and cleanup**: why unbounded state eventually kills every streaming job |
| Advanced | Arbitrary stateful logic (per-key state machines, pattern detection such as "three failed payments in 10 minutes") |
| Advanced | Changing a running stateful job: code changes, state schema changes, and when checkpoints/savepoints can or cannot be reused |
| Advanced | Rebuilding state by replaying from Kafka (retention and compacted changelog topics make this possible) |
| Advanced | Python-native stream processing libraries (awareness; check project maintenance) vs JVM engines |

**How to learn it**

1. Read the topic file.
2. For five stateful operations, write what state is kept per key, how it
   grows, and when it can be deleted.
3. Kill a stateful consumer and discuss what is lost without a
   checkpoint.

**Hands-on exercise — `src/streaming_lab/state.py`**

1. Extend your plain-Python processor with keyed state stored in a local
   embedded store (e.g. SQLite or RocksDB bindings), checkpointed together
   with offsets.
2. Implement deduplication by event id with a 1-hour expiry.
3. Join orders with payments within 15 minutes; emit unmatched orders to an
   alert topic after the time bound.
4. Implement a per-customer state machine that flags three failed payments
   within 10 minutes.
5. Kill and restart the processor; prove results match an uninterrupted
   run; show state size staying bounded thanks to expiry.

**Checkpoint:**

- [ ] Explain keyed state and why it follows partitioning.
- [ ] Implement streaming deduplication and joins with bounded state.
- [ ] Explain checkpointing and recovery.
- [ ] Explain state TTL and the risks of changing stateful jobs.

**Common mistakes:** unbounded state (deduplication or joins without a
time bound); state not checkpointed with offsets; changing keys or state
layout in a running job without a migration plan.

---

## 9. Phase D — Stream Processing Engines (Advanced)

### Topic 10 — [Spark Structured Streaming](10-spark-structured-streaming.md)

**Why here:** You already know Spark (Module 2.14). Structured Streaming
lets you write streaming jobs with the same DataFrame API, and it is one of
the most common ways to stream into lakehouse tables.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The model: a stream as an unbounded table; `readStream` / `writeStream`; the **micro-batch** execution model |
| Basics | Reading from Kafka (the Spark Kafka connector): `subscribe`, `startingOffsets`, and parsing values (Protobuf/Avro/JSON functions) |
| Basics | **Triggers**: default (as fast as possible), fixed interval, and `availableNow` (process everything available, then stop — incremental batch, Module 2.12) |
| Basics | **Output modes**: append, update, complete |
| Intermediate | **Checkpoint locations**: offsets and state for recovery; never sharing or deleting them casually |
| Intermediate | Event-time processing: `withWatermark`, `window()`, `session_window()` |
| Intermediate | Stateful operations: aggregations, `dropDuplicatesWithinWatermark`, stream–static and stream–stream joins |
| Intermediate | **Sinks**: Kafka, files, Delta/Iceberg tables (Module 2.15), and **`foreachBatch`** for custom logic such as `MERGE` into lakehouse tables |
| Intermediate | **Exactly-once** in Structured Streaming: replayable sources + checkpoints + idempotent or transactional sinks |
| Advanced | Arbitrary stateful processing APIs in recent Spark versions (e.g. `transformWithState`-style APIs, including pandas-based variants) — awareness and use cases |
| Advanced | Monitoring: `lastProgress`, input rate vs processing rate, batch duration, state size, the Structured Streaming UI tab |
| Advanced | Rate limiting (`maxOffsetsPerTrigger`) for backpressure (Topic 13) |
| Advanced | Which query changes are allowed between restarts with the same checkpoint |
| Advanced | Small files from streaming writes and compaction (Modules 2.5 and 2.15) |
| Advanced | Lower-latency execution modes in recent Spark versions — awareness |

**How to learn it**

1. Read the topic file.
2. Port your plain-Python window and join logic from Topics 07–09 to
   Structured Streaming and compare the amount of code.
3. Stop and restart a query many times; inspect the checkpoint directory.

**Hands-on exercise — `src/streaming_lab/spark_streaming.py`**

1. Read `orders` and `payments` from Kafka with Protobuf deserialisation.
2. Compute 5-minute tumbling revenue per country with a 10-minute
   watermark, writing to a Kafka topic in update mode.
3. Deduplicate orders within the watermark and join orders with payments
   within 15 minutes.
4. Upsert deduplicated orders into an Iceberg or Delta `silver.orders`
   table with `foreachBatch` + `MERGE`, idempotently.
5. Kill the job repeatedly; prove the lakehouse table equals a batch
   recomputation from the topic.
6. Run the same job with `availableNow` as a scheduled incremental batch
   and compare cost and latency.

**Checkpoint:**

- [ ] Build Structured Streaming jobs from Kafka with watermarks and
      windows.
- [ ] Choose triggers and output modes.
- [ ] Use `foreachBatch` to merge into lakehouse tables idempotently.
- [ ] Explain checkpoints and exactly-once in Structured Streaming.
- [ ] Monitor a streaming query.

**Common mistakes:** missing watermarks on stateful queries (unbounded
state); deleting checkpoints to "fix" a job (reprocessing or data loss);
non-idempotent `foreachBatch` logic; thousands of tiny files in sinks.

---

### Topic 11 — [Apache Flink and PyFlink overview](11-apache-flink-and-pyflink-overview.md)

**Why here:** Flink is the leading engine for low-latency, heavily stateful
streaming. Even if you mainly use Spark, you must understand what Flink
offers and when it is the better choice.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Flink's model: true record-at-a-time streaming (batch as a special case) vs Spark's micro-batches |
| Basics | Architecture: JobManager, TaskManagers, task slots, parallelism, and operators |
| Basics | APIs: **DataStream API**, **Table API**, and **Flink SQL**; PyFlink as the Python interface to them |
| Intermediate | Event time and watermark strategies, windows, and keyed state as first-class concepts (Topics 07–09 in Flink) |
| Intermediate | **State backends** (heap vs RocksDB), **checkpoints** (automatic, for recovery) and **savepoints** (manual, for upgrades and migrations) |
| Intermediate | Exactly-once with checkpoints and two-phase-commit sinks (e.g. Kafka) |
| Intermediate | Flink SQL for streaming joins, windows, and CDC sources (Flink CDC) — often the most productive way to use Flink from Python |
| Advanced | How Python runs in PyFlink (Python workers alongside the JVM) and its performance implications; preferring SQL/Table API where possible |
| Advanced | Deployment: session vs application clusters, Kubernetes operators, and managed Flink services — awareness |
| Advanced | Recent Flink versions' architectural changes (e.g. disaggregated state) — awareness |
| Advanced | Choosing Flink vs Spark Structured Streaming vs Kafka Streams-style libraries: latency, state size, team skills, ecosystem, and operations |

**How to learn it**

1. Read the topic file.
2. Run a local Flink cluster (Docker) and submit a PyFlink job; explore the
   Flink web UI (job graph, checkpoints, backpressure view).
3. Rewrite one Spark streaming job from Topic 10 in Flink SQL and compare.

**Hands-on exercise — `src/streaming_lab/flink/`**

1. Build a PyFlink Table API / Flink SQL job reading `orders` and
   `payments` from Kafka, computing 1-minute tumbling revenue and an
   order–payment interval join, writing results to Kafka.
2. Build a PyFlink DataStream job with keyed state implementing the "three
   failed payments in 10 minutes" alert.
3. Enable checkpoints with RocksDB state; kill a TaskManager and observe
   recovery.
4. Take a savepoint, change the job, and restore from the savepoint.
5. Write a decision note: Flink or Spark for your mini-project's
   low-latency alerts, with reasons.

**Checkpoint:**

- [ ] Explain Flink's architecture and APIs.
- [ ] Build PyFlink SQL and DataStream jobs.
- [ ] Explain checkpoints vs savepoints and state backends.
- [ ] Choose between Flink and Spark for a workload.

**Common mistakes:** heavy per-record Python UDFs where SQL would do;
treating checkpoints as upgrade snapshots (use savepoints); choosing Flink
for workloads that hourly micro-batches would serve.

---

## 10. Phase E — Integration and Operations (Advanced)

### Topic 12 — [Debezium CDC streams into Kafka](12-debezium-cdc-streams-into-kafka.md)

**Why here:** In Module 2.9 you read PostgreSQL's change log yourself.
Debezium does this in production: it streams every database change into
Kafka topics, ready for stream processors and lakehouse tables.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Kafka Connect**: workers, connectors, tasks, converters, and the REST API to manage them |
| Basics | The **Debezium PostgreSQL connector**: logical decoding with `pgoutput`, replication slots, and publications (concepts from Module 2.9) |
| Basics | Topics per table, message keys = primary keys |
| Intermediate | The **change event envelope**: `before`, `after`, `op` (create, update, delete, read/snapshot), `source` metadata (LSN, transaction, table), and timestamps |
| Intermediate | **Snapshots**: initial snapshot modes, incremental snapshots, and the snapshot-to-streaming handoff |
| Intermediate | Deletes and **tombstones** (for compacted topics), and handling them in consumers and sinks |
| Intermediate | Converters with the schema registry (Avro, Protobuf, or JSON Schema) and schema changes flowing through |
| Intermediate | **Single message transforms (SMTs)**, e.g. unwrapping the envelope to the new row state, routing, and filtering |
| Advanced | The **outbox event router**: publishing domain events from an outbox table (Topic 03) |
| Advanced | Heartbeats and replication-slot health: preventing WAL growth on quiet databases; monitoring slot lag (the risk from Module 2.9) |
| Advanced | Applying CDC to the lakehouse: stream → deduplicate/order by LSN → `MERGE` into Iceberg/Delta (Topic 10, Module 2.15) |
| Advanced | Operating connectors: restarts, offsets, failures, re-snapshots, and schema changes in the source database |
| Advanced | Debezium without Kafka (Debezium Server / embedded engine) — awareness |

**How to learn it**

1. Read the topic file.
2. Deploy the Debezium PostgreSQL connector via Kafka Connect's REST API;
   make inserts, updates, and deletes; read the raw change events.
3. Map every field of the envelope to what you built by hand in Module 2.9.

**Hands-on exercise — `connect/` and `src/streaming_lab/cdc.py`**

1. Stream `customers`, `orders`, and the outbox table from PostgreSQL into
   Kafka with Protobuf or Avro converters and the schema registry.
2. Add an unwrap SMT for one topic and keep the full envelope for another;
   compare consumer code.
3. Apply `orders` changes to an Iceberg or Delta table with Spark
   Structured Streaming and `foreachBatch` `MERGE`, including deletes;
   prove the table equals the source database.
4. Publish order events through the outbox event router.
5. Add a column in PostgreSQL and follow the schema change through the
   registry and the lakehouse table.
6. Stop the connector, generate writes, and monitor replication slot lag
   and WAL size; configure heartbeats.

**Checkpoint:**

- [ ] Deploy and manage Kafka Connect and Debezium connectors.
- [ ] Explain the change event envelope and snapshots.
- [ ] Handle deletes, tombstones, and schema changes.
- [ ] Apply CDC streams to lakehouse tables correctly.
- [ ] Monitor replication slots and connector health.

**Common mistakes:** unmonitored replication slots filling the source
disk; ignoring deletes and tombstones; applying changes without ordering
by log position; re-snapshotting large tables in production without a plan.

---

### Topic 13 — [Backpressure and consumer lag](13-backpressure-and-consumer-lag.md)

**Why last:** A streaming system is only healthy if every consumer keeps
up. Lag is the single most important streaming metric, and backpressure is
how systems survive bursts without falling over.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Consumer lag**: the difference between the latest offset and the committed offset per partition; lag in records vs lag in time |
| Basics | Measuring lag with Kafka CLI tools, web UIs, and client metrics |
| Basics | **Backpressure**: slowing intake when downstream cannot keep up, instead of crashing or buffering without limit |
| Intermediate | Causes of lag: slow sinks, CPU-heavy processing, hot partitions, rebalance storms, GC pauses, and traffic bursts |
| Intermediate | Scaling consumers: adding group members (up to the partition count), increasing partitions (and its effect on key ordering), batching sink writes |
| Intermediate | Backpressure mechanisms: Kafka's pull model, pausing partitions, `maxOffsetsPerTrigger` in Spark, Flink's built-in backpressure and its UI |
| Intermediate | **The retention cliff**: if lag exceeds topic retention, unread data is deleted — permanent data loss |
| Advanced | Alerting on lag: absolute thresholds vs growth rate vs estimated time to catch up; per-partition lag to detect skew |
| Advanced | Autoscaling consumers on lag (e.g. event-driven autoscalers on Kubernetes — awareness, Module 2.18) |
| Advanced | Catch-up strategies after outages: temporary scale-out, prioritising recent data, or replaying from the lakehouse instead of the topic |
| Advanced | End-to-end latency measurement (event time → sink commit time) and latency SLOs (Module 2.1) |
| Advanced | Capacity planning: throughput per partition and per consumer, headroom for bursts |

**How to learn it**

1. Read the topic file.
2. Run a producer at 5× the consumer's capacity for 10 minutes; plot lag
   per partition over time.
3. Apply each mitigation one at a time and measure recovery time.

**Hands-on exercise — `src/streaming_lab/lag.py`**

1. Build a lag monitor that reports per-partition lag (records and
   estimated seconds), lag growth rate, and time to catch up, and exits
   non-zero when an SLO is breached.
2. Create a burst and recover by: scaling consumers, batching sink writes,
   and increasing partitions (and document the ordering impact).
3. Create a hot partition with skewed keys and show that adding consumers
   does not help; fix it with a better key.
4. Configure `maxOffsetsPerTrigger` on the Spark job and observe stable
   batch durations under bursts; observe backpressure in the Flink UI.
5. Set a short retention on a test topic and demonstrate data loss when lag
   exceeds it; write the alert that would have prevented it.

**Checkpoint:**

- [ ] Measure consumer lag in records and time.
- [ ] Explain and apply backpressure mechanisms.
- [ ] Diagnose lag causes and choose the right fix.
- [ ] Explain the retention cliff and alert before it.

**Common mistakes:** alerting only on absolute lag; adding consumers beyond
the partition count; increasing partitions without considering key
ordering; retention shorter than the worst plausible outage.

---

## 11. Consolidate — practice questions and interview practice

### [`practice-questions.md`](practice-questions.md)

For every question:

1. Decide whether streaming is needed at all, and what latency is
   required.
2. Design topics: keys, partitions, retention, schemas, and compatibility.
3. State the delivery guarantee of every hop and how exactly-once effects
   are achieved.
4. Define event time, watermark delay, windows, and state bounds.
5. Choose an engine and sink; implement it with the event generator.
6. Kill components, restart, and compare with a batch recomputation.
7. Measure latency and lag, and define alerts.

### [`interview-practice.md`](interview-practice.md)

Streaming appears in many senior data engineering interviews. Practise out
loud with diagrams and a **30-minute timer** for design questions.

Typical concept questions: queue vs log; partitions and ordering; consumer
groups and rebalances; `acks` and idempotent producers; at-least-once vs
exactly-once; Kafka transactions; event time vs processing time;
watermarks; window types; stateful processing and checkpoints; Spark
Structured Streaming vs Flink; compacted topics; schema registry
compatibility; consumer lag.

Typical design questions: "real-time revenue dashboard with late mobile
events", "fraud alerts within 5 seconds", "replicate a PostgreSQL database
into a lakehouse continuously", "deduplicate an at-least-once event
stream", "join orders and payments that arrive minutes apart", "our
consumer lag keeps growing — what do you do?", and "how would you
reprocess a week of events after a bug fix?".

---

## 12. Module mini-project — a real-time order analytics platform

This is the proof that you have finished the module.

**Scenario:** The business wants live operational metrics (revenue per
5 minutes, active sessions), fraud-style alerts within seconds, and a
continuously updated lakehouse — while keeping the nightly batch platform
as the source of reconciled truth.

Build `realtime_platform/` with:

1. **Infrastructure** — Docker Compose with a three-broker Kafka (KRaft)
   cluster, schema registry, Kafka Connect with Debezium, PostgreSQL, MinIO,
   a Kafka UI, and a Flink cluster.
2. **Sources** — Debezium CDC from PostgreSQL (`customers`, `orders`,
   outbox events) and a Python clickstream/payment producer using Protobuf
   with the schema registry, idempotence, and `acks=all`.
3. **Contracts** — `.proto` schemas under version control with a CI
   breaking-change check and registry compatibility set per subject.
4. **Python consumers** — an at-least-once consumer with an idempotent
   PostgreSQL sink and a dead-letter topic; a transactional
   consume–transform–produce job.
5. **Spark Structured Streaming** — watermarked tumbling revenue windows,
   session windows, deduplication, an order–payment stream–stream join, and
   `foreachBatch` `MERGE` of CDC changes into Iceberg or Delta tables.
6. **Flink** — a PyFlink job (SQL or DataStream) for low-latency stateful
   alerts with RocksDB state, checkpoints, and a savepoint-based upgrade.
7. **Operations** — a lag monitor with SLO alerts, backpressure settings,
   a burst test, a broker-failure test, and replication-slot monitoring.
8. **Verification** — chaos tests (kill consumers, jobs, and a broker) and
   a nightly batch reconciliation comparing streaming outputs with a batch
   recomputation of the same events.
9. **Design record** — topic design, delivery guarantees per hop, watermark
   choices from measured lateness, and the Spark-vs-Flink decision.

**Grading yourself:** no event is lost and no duplicate affects any result
after repeated chaos tests; final windowed results match the batch
recomputation; the lakehouse tables equal the source database; schema
changes that would break consumers are blocked before deployment; and lag
alerts fire long before retention could cause data loss.

---

## 13. Module self-assessment — exit criteria

Only move to Module 2.17 when you can tick every box without looking at your
notes:

- [ ] I can choose between queues, streams, and batch, and describe
      event-driven patterns.
- [ ] I can design Kafka topics with keys, partitions, replication, and
      retention.
- [ ] I can write reliable Python producers and consumers.
- [ ] I can explain and implement at-most-once, at-least-once, and
      exactly-once effects.
- [ ] I can manage event schemas with Protobuf and a schema registry.
- [ ] I can reason about event time, watermarks, and late data.
- [ ] I can use tumbling, sliding, and session windows correctly.
- [ ] I can build bounded, fault-tolerant stateful processing.
- [ ] I can build Spark Structured Streaming jobs into the lakehouse.
- [ ] I can explain Flink and build a PyFlink job.
- [ ] I can run Debezium CDC into Kafka and apply it to tables.
- [ ] I can monitor lag and handle backpressure.
- [ ] I have finished the practice questions, interview practice, and the
      mini-project.

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Apache Kafka documentation (4.x) — design, producer/consumer configuration, transactions, KRaft | 02–05, 13 |
| `confluent-kafka` Python client documentation and examples (including schema registry serializers) | 03–06 |
| Protocol Buffers documentation (language guide, proto3, evolution rules) and `buf` documentation | 06 |
| *Kafka: The Definitive Guide*, 2nd edition — Gwen Shapira, Todd Palino, Rajini Sivaram, Krit Petty (O'Reilly) | 01–05, 13 |
| *Streaming Systems* — Tyler Akidau, Slava Chernyak, Reuven Lax (O'Reilly) | 07, 08, 09 |
| Tyler Akidau — "Streaming 101" and "Streaming 102" articles | 07, 08 |
| Spark Structured Streaming Programming Guide (4.x) | 10 |
| Apache Flink documentation — concepts, PyFlink, Flink SQL, state and fault tolerance | 09, 11 |
| Debezium documentation — PostgreSQL connector, event format, outbox event router | 12 |
| *Designing Data-Intensive Applications* — Martin Kleppmann, chapter on stream processing | 01, 05, 07, 09 |

---

## 15. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Managed Kafka, Kinesis, Pub/Sub, Event Hubs, and managed Flink | 2.17 Cloud Storage and Cloud Data Platforms |
| Running brokers, connectors, and streaming jobs on Kubernetes; autoscaling on lag | 2.18 Containers, Infrastructure, and CI/CD for Data |
| Testing streaming jobs and chaos tests | 2.19 Testing Data Pipelines |
| Lag alerting, tracing events end to end, PII in event streams | 2.20 Observability, Lineage, Governance, and Security |
| Throughput tuning and the cost of always-on streaming | 2.21 Performance, Scaling, and Cost Optimization |
| Real-time features for ML and streaming data for AI applications | 2.22 Serving Data for Analytics, ML, and AI |

Streaming systems never stop, so their mistakes never stop either. The
habits you build here — reason in event time, state every delivery
guarantee, bound every piece of state, make every sink idempotent, verify
streams against batch, and watch lag like an SLO — are what let a real-time
pipeline run for years without losing or double-counting a single event.
