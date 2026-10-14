# Project Roadmap — Real-Time Kafka Streaming Pipeline

This is the end-to-end roadmap for **Stage 2 Project 05: Real-Time Kafka
Streaming Pipeline**. It takes you from an empty repository to a
**production-grade** event-streaming system in which application events
flow through **Kafka**, are validated and enriched, aggregated in real time
with **Spark Structured Streaming**, turned into low-latency alerts with
**Apache Flink**, served to live dashboards and APIs, and archived to the
lakehouse — with no lost events, no double counting, and proof that the
real-time numbers match the batch truth.

It is written as a sequence of **milestones**. Each milestone has a goal,
tasks, deliverables, and **acceptance criteria** you must meet before moving
on. The acceptance criteria are what make this production grade rather than
"a consumer that printed messages".

---

## 1. Why this project matters

Real-time data promises fast decisions — live revenue, instant fraud
alerts, operational dashboards, fresh ML features. It also multiplies every
data engineering problem:

- events arrive late and out of order, so "revenue per minute" keeps
  changing;
- producers retry and consumers restart, so events are duplicated or lost;
- one malformed event blocks a partition for hours;
- state grows until a job runs out of memory;
- a burst of traffic creates lag that silently exceeds topic retention;
- a schema change from one team breaks every consumer;
- nobody can prove the dashboard matches the numbers finance computes the
  next morning.

This project makes you design and operate a streaming system that handles
all of these deliberately.

---

## 2. Project goal and scope

### Goal

Build `realtime_platform`, which continuously:

1. **Produces** typed application events (Protobuf with a schema registry)
   from simulated web and mobile clients into Kafka.
2. **Validates, deduplicates, and enriches** events into clean topics with
   exactly-once effects, sending bad events to dead-letter topics.
3. **Aggregates** events in real time with Spark Structured Streaming using
   event time, watermarks, and tumbling, sliding, and session windows.
4. **Detects** business conditions with low latency using Flink (stateful
   rules and interval joins) and publishes alerts.
5. **Serves** real-time metrics and alerts through a serving store, an API,
   and a live dashboard.
6. **Archives** every raw event to the lakehouse for replay and batch
   reconciliation.
7. Proves correctness with **replay** and **streaming-vs-batch
   reconciliation**, and stays healthy under bursts and failures (lag,
   backpressure, chaos drills).
8. Is deployed, monitored, and operable by someone else.

### In scope

- Event design and contracts, producers, Kafka topic design, Python
  consumers, Spark Structured Streaming, Flink/PyFlink, serving, lakehouse
  archive, delivery semantics, late data, state, replay, reconciliation,
  scaling, testing, deployment, observability, and operations.

### Out of scope (covered by other Stage 2 projects)

- API batch ingestion → **Project 01**.
- Database CDC with Debezium → **Project 02** (optional enrichment input
  here).
- Warehouse ELT with dbt → **Project 03**.
- Batch medallion processing at scale → **Project 04**.
- The full data-quality and observability platform → **Project 06**.

---

## 3. Prerequisites and when to do this project

**Recommended timing:** after completing **Modules 2.1–2.16**. The
production-hardening milestones (M11–M14) use Modules 2.17–2.22. If you
have not studied those yet, complete the **Core track** now and return for
the **Production track** later.

| Module | What this project uses from it |
| --- | --- |
| 2.1 Foundations | Batch vs streaming decisions, latency SLAs |
| 2.8 Data modelling | Event design, sessions, identity, clickstream modelling |
| 2.9 Ingestion patterns | At-least-once delivery, webhooks-style events, deduplication |
| 2.10 Concurrency | Async producers and consumers, bounded queues, graceful shutdown |
| 2.11 Validation and quality | Contracts, schema compatibility, dead-letter handling, reconciliation |
| 2.12 Pipeline design | Idempotency, late data, reprocessing windows, state |
| 2.14 PySpark | DataFrames, joins, Spark UI |
| 2.15 Lakehouse table formats | Streaming sinks into Iceberg or Delta, compaction |
| 2.16 Streaming | **Everything**: Kafka, producers, consumers, delivery semantics, Protobuf and registry, event time, watermarks, windows, state, Structured Streaming, Flink, lag, backpressure |
| 2.17 Cloud *(production track)* | Managed Kafka and compute options, IAM |
| 2.18 Delivery *(production track)* | Images, Kubernetes, CI/CD, secrets |
| 2.19 Testing | Integration tests with containers, property tests, streaming smoke tests |
| 2.20 Observability *(production track)* | Metrics, tracing through Kafka headers, alerts, runbooks, PII |
| 2.21 Performance and cost *(production track)* | Capacity planning, benchmarking, cost of always-on compute |
| 2.22 Serving *(production track)* | FastAPI, caching, freshness contracts |

### Tracks

| Track | Milestones | Result |
| --- | --- | --- |
| **Core track** | M0–M10 | A correct, tested streaming platform running locally with proven delivery semantics |
| **Production track** | M11–M14 | Deployed, secured, observable, and operable under failures and bursts |

**Estimated effort:** Core track 5 weeks; Production track 2–3 weeks (at
8–10 hours per week).

**Hardware note:** Kafka (3 brokers), a schema registry, Spark, Flink,
PostgreSQL, Redis, MinIO, and monitoring together need roughly 12–16 GB of
RAM. Use Compose profiles to run only what each milestone needs, or a small
cloud VM.

---

## 4. The scenario

You are a data engineer at **ShopLite**. The business wants to move from
"yesterday's numbers" to "right now".

### Event sources

| Producer | Events | Behaviour that makes it hard |
| --- | --- | --- |
| Web and mobile clients | `PageViewed`, `ProductViewed`, `AddedToCart`, `CheckoutStarted` | High volume; mobile clients go offline and send events minutes late; retries duplicate events; bots |
| Order service | `OrderPlaced`, `OrderCancelled` | Must never be lost or double counted |
| Payment service | `PaymentAuthorised`, `PaymentFailed`, `RefundIssued` | Arrives seconds to minutes after orders; must be joined with orders |
| Catalogue service | `ProductUpdated` (reference data) | Low volume; latest value per product needed for enrichment |

### Consumers and their needs

| Consumer | Needs |
| --- | --- |
| Operations dashboard | Revenue and orders per minute by country; active sessions; checkout conversion over the last 15 minutes |
| Risk team | Alerts within seconds: several failed payments per customer in 10 minutes; orders not paid within 15 minutes; unusually large orders |
| Marketing | Live funnel by channel |
| Data platform | Every raw event archived to the lakehouse for replay and daily batch truth |

### Service-level agreement (write it down in M0)

- **Latency:** dashboard metrics reflect events within **10 seconds at
  p95**; risk alerts are emitted within **5 seconds at p95** of the
  triggering event.
- **Completeness:** no event accepted by Kafka is ever lost; no event
  affects any metric or alert more than once.
- **Late data:** events up to **10 minutes** late update real-time windows;
  later events are corrected by daily reconciliation.
- **Correctness:** final real-time window values match the batch
  recomputation from the archive within an agreed tolerance (ideally
  exactly).
- **Archive:** raw events are queryable in the lakehouse within **5
  minutes**.
- **Resilience:** after a 2-hour outage of any processing component, the
  system catches up automatically without data loss, and lag never exceeds
  topic retention.

---

## 5. Target architecture

```text
 Producers (web/mobile simulator, order, payment, catalogue services)
   │ Protobuf + schema registry · idempotent producer · acks=all · trace context in headers
   ▼
 Kafka (KRaft, 3 brokers)
   raw.clicks · raw.orders · raw.payments · ref.products (compacted) · *.dlq
   │
   ├──► Python validator/enricher (consume–transform–produce, Kafka transactions)
   │        └──► clean.clicks · clean.orders · clean.payments        + *.dlq
   │
   ├──► Spark Structured Streaming (event time, watermarks, windows, state)
   │        ├──► metrics.* topics
   │        └──► serving store (PostgreSQL / Redis) via idempotent foreachBatch
   │
   ├──► Flink / PyFlink (low-latency keyed state, interval joins, CEP-style rules)
   │        └──► alerts.risk topic ──► alert consumer (notifications, alert store)
   │
   └──► Archive job (Structured Streaming → Iceberg/Delta bronze on MinIO)
            └──► daily batch recomputation & reconciliation vs real-time outputs

 Serving: FastAPI (metrics & alerts API) · Grafana live dashboard
 Operations: lag & latency metrics · tracing · alerts · runbook · chaos drills
```

### Technology choices (defaults)

| Concern | Default (local) | Production option |
| --- | --- | --- |
| Broker | Apache Kafka 4.x (KRaft), 3 brokers | Managed Kafka (Module 2.17) |
| Schemas | Protobuf + schema registry | Same |
| Python clients | `confluent-kafka` | Same |
| Validation/enrichment | Python consumer service with transactions | Same, or a Python stream-processing library |
| Aggregations | Spark Structured Streaming | Managed Spark |
| Low-latency alerts | Flink (Flink SQL or PyFlink DataStream) | Managed Flink |
| Serving store | PostgreSQL (history) + Redis (latest values) | Same, or a real-time OLAP database |
| API and dashboard | FastAPI + Grafana | Same |
| Archive | Iceberg (or Delta) on MinIO | Object storage + catalog |
| Monitoring | Prometheus, Grafana, Alertmanager, OpenTelemetry | Same or managed |
| Delivery | Docker Compose; optional kind/k3d with operators | Kubernetes, Terraform, GitHub Actions |

Record decisions as **ADRs** in `docs/adr/`: Protobuf vs Avro, topic and key
design, which engine does what (and why not only one), watermark delays,
serving store, and exactly-once strategy per hop.

---

## 6. Repository structure

```text
realtime-kafka-platform/
├── README.md
├── pyproject.toml / uv.lock
├── docker-compose.yml             # profiles: kafka, registry, spark, flink, serving, lake, monitoring
├── .env.example
├── docs/
│   ├── requirements.md
│   ├── architecture.md
│   ├── event-catalogue.md         # every event: purpose, owner, schema, key, topic, SLA
│   ├── topics.md                  # topic design: partitions, retention, compaction, ACLs
│   ├── delivery-semantics.md      # guarantee of every hop and how it is achieved
│   ├── adr/
│   └── runbook.md
├── schemas/                       # .proto files (versioned) + buf/registry config
├── topics/                        # topic definitions as code
├── producers/                     # event simulators and producer library
├── src/realtime/
│   ├── common/                    # serde, config, tracing, idempotent sink helpers
│   ├── validator/                 # consume–transform–produce service
│   ├── spark_jobs/                # aggregations, archive job
│   ├── flink_jobs/                # alert jobs (SQL and/or DataStream)
│   ├── serving/                   # FastAPI app, serving-store writers
│   ├── reconcile/                 # batch recomputation and comparison
│   └── ops/                       # lag monitor, latency probes, replay tools
├── tests/
│   ├── unit/  property/  integration/  e2e/  chaos/
│   └── fixtures/
└── .github/workflows/
```

---

## 7. Milestones overview

```text
Core track
  M0   Project framing and local platform
  M1   Event design, contracts, and topic design
  M2   Producers and the event simulator
  M3   Raw archive to the lakehouse
  M4   Validation, deduplication, and enrichment with exactly-once effects
  M5   Real-time aggregations with Spark Structured Streaming
  M6   Low-latency stateful alerts with Flink
  M7   Serving real-time results
  M8   Correctness: late data, replay, schema evolution, and reconciliation
  M9   Lag, backpressure, and scaling
  M10  Testing to production standard

Production track
  M11  Packaging, deployment, and security
  M12  CI/CD and safe upgrades of stateful jobs
  M13  Observability, end-to-end latency, and alerting
  M14  Operations: runbook, chaos drills, capacity, cost, and hand-over
  (M15 Optional stretch goals)
```

Commit and tag at the end of every milestone (`m0`, `m1`, …).

---

## 8. Core track

### M0 — Project framing and local platform

**Goal:** Clear requirements, measurable SLAs, and a reproducible local
streaming platform.

**Tasks**

1. Write `docs/requirements.md` with consumers, the SLA from Section 4, and
   non-goals; justify *why* each use case needs streaming rather than
   micro-batch or batch (Module 2.1).
2. Draw the architecture in `docs/architecture.md`, including every topic,
   job, store, and where state lives (Kafka offsets, Spark checkpoints,
   Flink checkpoints and savepoints, serving stores).
3. Build `docker-compose.yml` with profiles: Kafka (KRaft, 3 brokers), a
   schema registry, a Kafka UI, Spark, Flink (JobManager and TaskManagers),
   PostgreSQL, Redis, MinIO with a catalog, Prometheus, and Grafana — with
   health checks and idempotent set-up services (topics, buckets,
   namespaces).
4. Set up `uv`, Ruff, pytest, `pre-commit` with secret scanning, and a
   Protobuf toolchain (`protoc` or `buf`).
5. First ADRs: engines per workload, serving store, and table format for the
   archive.

**Acceptance criteria**

- [ ] The stack starts healthy profile by profile from a clean clone.
- [ ] The SLA has numeric latency, completeness, lateness, and resilience
      targets.
- [ ] Each streaming use case has a written justification.

---

### M1 — Event design, contracts, and topic design

**Goal:** Events are well-designed, typed, versioned contracts, and topics
are designed for ordering, parallelism, durability, and replay.

**Tasks**

1. Write `docs/event-catalogue.md`: for each event, its purpose, owner
   (producer team), consumers, key, and fields.
2. Define a common **event envelope** in Protobuf: `event_id` (UUID),
   `event_type`, `event_time` (when it happened), `producer`,
   `schema_version`, `user_id`/`anonymous_id`, `session_id`, and
   correlation/trace ids — and event-specific payloads.
3. Write `.proto` schemas following evolution rules (Module 2.16): stable
   field numbers, `reserved` for removed fields, well-known timestamp types.
4. Design topics (`docs/topics.md` and `topics/` as code): raw, clean,
   metrics, alerts, reference (compacted), and dead-letter topics; **keys**
   chosen for per-entity ordering (orders and payments keyed by `order_id`
   or `customer_id` — decide per join need and document); partition counts
   from throughput estimates; replication factor 3 with
   `min.insync.replicas=2`; **retention long enough to replay after a
   multi-hour outage and to rebuild state**.
5. Register schemas with **compatibility modes** per subject and add a CI
   breaking-change check (`buf breaking` or registry checks).
6. Classify **personal data** in events (user ids, IP addresses, emails in
   checkout) and decide how it is minimised or pseudonymised (Module 2.20).

**Acceptance criteria**

- [ ] Every event has an owner, key, schema, and topic.
- [ ] An incompatible schema change is rejected by the CI check and the
      registry.
- [ ] Topic retention and partitions are justified with numbers.
- [ ] Personal data fields are identified with a handling decision.

---

### M2 — Producers and the event simulator

**Goal:** Realistic, reproducible event traffic — including every
misbehaviour a real system produces — sent reliably to Kafka.

**Tasks**

1. Build a **producer library**: `confluent-kafka` producer with
   `acks=all`, idempotence enabled explicitly, compression, a
   deliberately chosen partitioner (so keys map consistently across
   languages — Module 2.16), delivery callbacks that log and count
   failures, schema-registry Protobuf serialisation, and a clean `flush()`
   on shutdown.
2. Build a **seeded simulator** of users, sessions, and services producing
   the events in Section 4, with configurable:
   - traffic rate and daily shape, plus bursts (10× for N minutes);
   - mobile **offline delays** (events arriving up to 30 minutes late) and
     out-of-order delivery;
   - **duplicates** from client retries (same `event_id`);
   - **skewed keys** (a viral product, a heavy customer) and bot sessions;
   - **malformed events** (wrong schema version, missing fields) sent to
     raw topics;
   - fraud-like patterns (bursts of failed payments) with known ground
     truth for evaluating alerts.
3. Make the simulator write a **ground-truth log** (every event it
   intended to send, with times) to files, for correctness checks later.
4. Expose producer metrics (sent, acknowledged, failed, latency).

**Acceptance criteria**

- [ ] A run is reproducible from its seed and produces a matching
      ground-truth log.
- [ ] Killing a broker during production loses no acknowledged events and
      creates no producer-caused duplicates.
- [ ] Every misbehaviour can be switched on and its rate configured.

---

### M3 — Raw archive to the lakehouse

**Goal:** Every event that reaches Kafka is archived durably, exactly once,
for replay and batch truth — before any processing can go wrong.

**Tasks**

1. Build a Structured Streaming **archive job** reading all raw topics and
   writing to `bronze.events_raw` (Iceberg or Delta) with the raw bytes or
   decoded payload, Kafka metadata (`topic`, `partition`, `offset`,
   timestamp), schema id, and ingestion time.
2. Guarantee **exactly-once archive**: checkpointing plus a guard on
   `(topic, partition, offset)` so restarts never duplicate or skip.
3. Choose a trigger interval that meets the 5-minute archive SLA without
   producing tiny files; schedule compaction (Module 2.15).
4. Build a **replay tool** that can republish archived events for a time
   range into a replay topic (for reprocessing after bugs, or for tests).

**Acceptance criteria**

- [ ] After 20 random restarts, the archive contains every Kafka record
      exactly once (compared with topic offsets and the ground-truth log).
- [ ] Archived events are queryable from DuckDB or Spark within the SLA.
- [ ] The replay tool republishes a chosen hour faithfully.

---

### M4 — Validation, deduplication, and enrichment with exactly-once effects

**Goal:** Downstream jobs read clean, unique, enriched events — and bad
events never block a partition or disappear.

**Tasks**

1. Build a Python **validator/enricher service** using a
   **consume–transform–produce** loop with **Kafka transactions**
   (`transactional.id`, sending consumer offsets within the transaction,
   `read_committed` downstream — Module 2.16).
2. **Validate** each event (schema, required fields, value ranges, event
   time not in the far future) and route failures to `*.dlq` topics with
   error headers (reason, source topic, offset) — never blocking the
   partition.
3. **Deduplicate** by `event_id` with bounded state (for example, a
   time-limited store keyed by `event_id` per partition, sized from the
   duplicate delay distribution) and document the dedupe window.
4. **Enrich** events with the latest product data from the compacted
   `ref.products` topic (a local table rebuilt from the compacted topic on
   start-up and updated continuously), and pseudonymise personal fields
   per M1.
5. Handle **rebalances** (flush state and commit before partitions are
   revoked) and **graceful shutdown** (Module 2.10).

**Acceptance criteria**

- [ ] Under repeated kill/restart, clean topics contain each valid event
      exactly once for `read_committed` consumers.
- [ ] Every malformed event appears in a DLQ with a reason; no partition is
      ever blocked.
- [ ] Enrichment uses the product version valid at processing time, and
      updates to products take effect without restarts.

---

### M5 — Real-time aggregations with Spark Structured Streaming

**Goal:** Correct, event-time-based live metrics that update as late data
arrives and are safe to restart.

**Tasks**

1. Read clean topics with Protobuf deserialisation; set `withWatermark` on
   `event_time` with a delay chosen from the **measured lateness
   distribution** (e.g. 10 minutes) and document the trade-off (Module
   2.16).
2. Compute:
   - **tumbling** 1-minute revenue and orders by country;
   - **sliding** 15-minute checkout conversion by channel (every minute);
   - **session windows** (30-minute gap) for active sessions and session
     length;
   - live funnel counts by channel.
3. Choose **output modes** per metric (update for dashboards, append for
   finalised windows) and write:
   - metrics topics for downstream consumers;
   - the **serving store** via `foreachBatch` with **idempotent upserts**
     keyed by `(metric, window_start, dimensions)` and a `batch_id` guard.
4. Keep state bounded (watermarks on every stateful operation) and monitor
   state size.
5. Mark each window's status (`open`, `final`) and its `as_of` time in the
   serving store.

**Acceptance criteria**

- [ ] Final window values equal a batch recomputation from the ground-truth
      log for the same events (see M8).
- [ ] Killing and restarting the job never double counts or loses window
      contributions.
- [ ] State size stays bounded over a multi-hour run.
- [ ] Dashboard metrics meet the 10-second p95 latency target.

---

### M6 — Low-latency stateful alerts with Flink

**Goal:** Risk alerts fire within seconds, exactly once, with bounded
state that survives failures and upgrades.

**Tasks**

1. Implement alert rules in **Flink SQL** where possible and the **PyFlink
   DataStream API** with keyed state where needed (Module 2.16):
   - **failed-payment burst:** 3 or more `PaymentFailed` events per
     customer within 10 minutes;
   - **unpaid order:** `OrderPlaced` with no `PaymentAuthorised` within 15
     minutes (interval join with a timeout, emitting on expiry);
   - **large order:** order total above a per-country threshold from
     reference data.
2. Use event-time processing with watermarks and **idle-source handling**;
   decide how late events affect alerts (ignore, emit corrections, or
   route to a side output) and document it.
3. Configure **RocksDB state**, **state TTL**, and **checkpoints** with
   exactly-once mode; write alerts to `alerts.risk` with a deterministic
   `alert_id` so duplicates can be recognised downstream.
4. Build an **alert consumer** that stores alerts idempotently and sends
   notifications (for example to a local webhook receiver), deduplicating
   by `alert_id`.
5. Evaluate alert quality against the simulator's **ground truth**:
   precision, recall, and latency percentiles.
6. Take a **savepoint**, change a rule threshold, and restore from the
   savepoint.

**Acceptance criteria**

- [ ] p95 alert latency meets the 5-second target.
- [ ] Every ground-truth fraud pattern produces exactly one alert
      notification, even across TaskManager failures.
- [ ] State stays bounded thanks to TTL; upgrades via savepoints preserve
      state.

---

### M7 — Serving real-time results

**Goal:** Consumers get fast, fresh, clearly labelled real-time data.

**Tasks**

1. Design the **serving store** (Module 2.22): PostgreSQL tables for window
   history and alert history; Redis for latest values (current minute,
   last 15 minutes) — with keys that include metric, dimensions, and
   window.
2. Build a **FastAPI** service: `/metrics/revenue?country=...&from=...`,
   `/metrics/conversion`, `/sessions/active`, `/alerts?since=...` — with
   authentication, pagination, and `as_of` and window status (`open` or
   `final`) in every response.
3. Build a **Grafana dashboard** with live panels (revenue per minute,
   conversion, active sessions, alert stream) and a freshness indicator.
4. Define and document what consumers should expect from open windows
   (values may still change) vs final windows.

**Acceptance criteria**

- [ ] The API p95 latency is within target under load (e.g. 100 requests
      per second).
- [ ] Every response states how fresh it is and whether the window is
      final.
- [ ] The dashboard updates live and shows a clear warning when data is
      stale.

---

### M8 — Correctness: late data, replay, schema evolution, and reconciliation

**Goal:** Prove — not assume — that real-time results are right, and that
the system can be corrected and evolved safely.

**Tasks**

1. Write `docs/delivery-semantics.md`: for every hop (producer → Kafka →
   validator → clean topics → Spark/Flink → serving store/alerts → archive)
   state the guarantee and the mechanism that achieves it (Module 2.16).
2. **Late data:** measure how many events arrive after the watermark; route
   them to a late-events topic; show that events within the allowed
   lateness update windows correctly.
3. **Reprocessing:** after a simulated logic bug in the aggregation job,
   reprocess a time range — either by resetting the job to Kafka offsets by
   timestamp or by replaying from the archive into a replay topic and a
   parallel job — and **atomically replace** affected serving-store rows.
4. **Schema evolution under load:** deploy a compatible schema change (new
   optional field) with old and new producers running together; then
   attempt an incompatible change and show it being blocked.
5. **Streaming vs batch reconciliation:** a daily batch job recomputes
   every metric from the archive (Spark or DuckDB) and compares it with the
   finalised real-time values; mismatches beyond tolerance raise an alert
   and a correction job updates the serving store.

**Acceptance criteria**

- [ ] The delivery-semantics document is complete and matches the tests
      in M10.
- [ ] Daily reconciliation passes for final windows (exactly, or within a
      justified tolerance for late events beyond the watermark).
- [ ] A reprocessing run fixes a simulated bug's effects without
      duplicates.
- [ ] Old and new producers and consumers interoperate during a schema
      change.

---

### M9 — Lag, backpressure, and scaling

**Goal:** The system absorbs bursts and outages without losing data or
violating SLAs for longer than necessary.

**Tasks**

1. Build a **lag monitor** (Module 2.16): per consumer group and partition,
   lag in records and in estimated seconds, growth rate, and time to catch
   up; alert on growth, not only on absolute lag.
2. Run **burst tests** (10× traffic for 30 minutes) and observe each
   component: producer buffers, broker throughput, validator, Spark batch
   durations, Flink backpressure, serving-store writes.
3. Apply **backpressure and scaling** measures and measure their effect:
   - Spark `maxOffsetsPerTrigger` for stable batches;
   - Flink parallelism and its backpressure view;
   - more validator instances (up to the partition count);
   - batching serving-store writes;
   - increasing partitions (and documenting the effect on key ordering and
     state).
4. **Hot keys:** reproduce a viral-product skew and fix it (better keys,
   pre-aggregation, or splitting hot keys) where it matters.
5. **Outage recovery:** stop each processing component for 2 hours under
   normal load, restart it, and measure catch-up time; verify lag never
   approached retention.
6. Write a **capacity plan**: throughput per partition and per instance,
   headroom, and the scaling procedure.

**Acceptance criteria**

- [ ] Bursts are absorbed with bounded latency degradation and full
      recovery.
- [ ] Every component catches up after a 2-hour outage without data loss.
- [ ] Lag alerts fire before retention could cause data loss.
- [ ] The capacity plan is backed by measured numbers.

---

### M10 — Testing to production standard

**Goal:** Automated tests prove the delivery guarantees and the business
logic, quickly and reliably.

**Tasks**

1. **Unit tests:** serialisation and envelope handling, validation rules,
   dedupe logic, enrichment, window assignment helpers, alert rule logic,
   serving-store upsert keys.
2. **Property tests** (Module 2.19): deduplication keeps exactly one event
   per id regardless of arrival order; idempotent sinks produce the same
   state when batches are replayed; windowed totals are independent of
   arrival order for events within the watermark.
3. **Integration tests** (Testcontainers or Compose): producer idempotence
   with a broker restart; transactional validator with `read_committed`
   consumers; DLQ routing; Spark streaming query restart from checkpoint;
   Flink job restart from checkpoint.
4. **End-to-end smoke test:** start the minimal stack, run the simulator for
   a few minutes with late events, duplicates, and malformed events, **poll**
   (never sleep) until outputs appear, and compare metrics and alerts with
   ground truth.
5. **Chaos tests:** kill random components during an end-to-end run and
   assert no loss and no double counting at the end.
6. Keep the pull-request suite within a time budget; run chaos tests
   nightly.

**Acceptance criteria**

- [ ] Re-introducing any of these bugs fails a test: auto-commit before
      processing, missing transactional offsets, no dedupe, missing
      watermark, non-idempotent `foreachBatch`, alert without deterministic
      id, DLQ that blocks.
- [ ] The end-to-end test matches ground truth.
- [ ] No flaky tests across 20 runs (chaos tests excluded from this count
      but deterministic in outcome).

**At the end of M10 you have completed the Core track.** Tag the repository
`core-complete` and write a retrospective.

---

## 9. Production track

### M11 — Packaging, deployment, and security

**Goal:** Every component is reproducible, securely connected, and
least-privileged.

**Tasks**

1. Build images for producers, the validator, the alert consumer, the API,
   and Spark and Flink jobs (Module 2.18); pin versions; scan images.
2. Manage **topics, ACLs, and schemas as code**, applied idempotently per
   environment.
3. Enable **TLS** and client authentication (e.g. SASL) for Kafka and the
   registry in non-local environments; configure **ACLs** so each service
   can only read and write its own topics (Module 2.20).
4. Deliver credentials through a secrets manager or Kubernetes secrets
   (Module 2.18).
5. Optionally deploy to Kubernetes: Kafka via an operator, Flink via its
   Kubernetes operator, Spark on Kubernetes, services as deployments with
   resource requests and limits, and autoscaling of consumers on lag
   (Module 2.18).

**Acceptance criteria**

- [ ] A service trying to read or write a topic outside its ACLs is
      denied.
- [ ] All connections are encrypted outside local development.
- [ ] No credential appears in Git, images, or logs.

---

### M12 — CI/CD and safe upgrades of stateful jobs

**Goal:** Changes ship frequently without losing state, events, or
correctness.

**Tasks**

1. **CI on pull requests:** lint, types, unit and property tests,
   integration tests, schema breaking-change checks, topic/ACL config
   validation, image build and scan.
2. **Deployment procedures** per component:
   - stateless services: rolling deployments with graceful shutdown;
   - Spark streaming jobs: stop gracefully, start the new version from the
     **same checkpoint** when compatible; for incompatible changes, start a
     new query with a new checkpoint from a chosen offset and reconcile;
   - Flink jobs: stop with a **savepoint**, deploy, restore from the
     savepoint; document state-compatibility rules.
3. **Shadow deployment** for risky logic changes: run the new job version in
   parallel on the same input into separate outputs, compare with the live
   version, then switch consumers.
4. Promote through `dev` → `staging` → `prod` with the end-to-end smoke test
   and reconciliation as gates; rehearse **rollback** for each component.

**Acceptance criteria**

- [ ] Upgrading each streaming job under load loses and duplicates nothing
      (verified by reconciliation).
- [ ] A shadow comparison is run before a logic change is switched on.
- [ ] Rollback of each component is documented and rehearsed.

---

### M13 — Observability, end-to-end latency, and alerting

**Goal:** You can see every event's journey, every component's health, and
every SLA — and are alerted before users notice.

**Tasks**

1. **Tracing:** propagate trace context in Kafka headers from producers
   through the validator to serving writes and alerts (Module 2.20); sample
   traces and keep all error traces.
2. **Metrics:** producer error rates and latency; broker health
   (under-replicated partitions); consumer lag per group; validator
   throughput, DLQ rate, dedupe hit rate; Spark input vs processing rate,
   batch duration, state size; Flink checkpoint duration and failures,
   backpressure, state size; serving write latency; API latency; end-to-end
   latency percentiles from latency probes.
3. **Dashboards:** an SLA overview (latency, completeness, lag, freshness)
   and a page per component.
4. **Alerts** with owners and runbooks:
   - p95 dashboard latency above SLA for 5 minutes → page;
   - risk-alert pipeline stalled or checkpoint failures repeating → page;
   - lag growing for 15 minutes or projected to reach retention → page;
   - DLQ rate above threshold → ticket;
   - reconciliation mismatch → ticket;
   - schema registry or broker health issues → page.
5. Make sure no personal data appears in logs, metrics labels, or traces.

**Acceptance criteria**

- [ ] Every chaos drill in M14 is detected by an alert.
- [ ] You can follow a single event from producer to dashboard in a trace.
- [ ] From the SLA dashboard alone, you can tell whether the platform is
      meeting its targets right now.

---

### M14 — Operations: runbook, chaos drills, capacity, cost, and hand-over

**Goal:** Someone else can run the platform, and it survives realistic
failures.

**Tasks**

1. Write `docs/runbook.md`: start/stop order, deployments and rollbacks,
   reprocessing a time range, resetting offsets safely, clearing a DLQ after
   a fix (replaying fixed events), scaling procedures, handling each alert,
   credential rotation, and escalation.
2. Run **chaos drills** and record detection and recovery times:
   - kill a broker; kill two brokers (observe write availability with
     `min.insync.replicas`);
   - kill the validator, the Spark driver, and a Flink TaskManager;
   - a poison-pill event storm;
   - a producer with a skewed clock sending events from the future;
   - an attempted incompatible schema change;
   - a 2-hour processing outage followed by catch-up;
   - a serving-store outage (Redis down).
   Every drill must end with reconciliation passing and no double-sent
   alerts.
3. **Capacity and performance:** benchmark maximum sustainable throughput
   per component; document headroom and scaling triggers (Module 2.21).
4. **Cost:** estimate always-on costs (brokers, Spark, Flink, serving) and
   compare with a micro-batch alternative for the dashboard metrics (e.g.
   `availableNow` every 5 minutes); write a recommendation per use case.
5. **Hand-over:** a walkthrough for a new engineer and a final
   retrospective.

**Acceptance criteria**

- [ ] All drills end with correct outputs and no duplicate notifications.
- [ ] Throughput limits and scaling triggers are documented with evidence.
- [ ] A cost comparison justifies (or challenges) streaming for each use
      case.
- [ ] Another person can reprocess an hour of data and handle a lag alert
      using only the runbook.

---

### M15 — Optional stretch goals

- **CDC enrichment:** join events with customer data streamed from Project
  02's Debezium topics (stream–table join on a compacted changelog).
- **Real-time ML features:** publish streaming features (orders in the last
  hour) to a feature store's online store (Module 2.22) and compare with
  batch features.
- **Python-native stream processing:** reimplement the validator or one
  aggregation with a Python stream-processing library and compare.
- **Streaming into the lakehouse from Flink:** write clean events to Iceberg
  from Flink with exactly-once sinks and compare with the Spark archive
  job.
- **Managed services:** run on managed Kafka and managed Flink or Spark and
  compare operations and cost (Module 2.17).
- **Queue-style consumption:** explore Kafka share groups (where available)
  for the notification sender and compare with consumer groups.

---

## 10. Definition of done

**Correctness**

- [ ] No acknowledged event is lost; no event affects metrics or alerts
      twice — proven by ground truth and chaos tests.
- [ ] Final real-time windows reconcile with batch recomputation; late data
      within the allowed lateness is included.
- [ ] Alerts meet precision/recall and latency targets against ground truth.

**Reliability and scaling**

- [ ] Bursts and outages are absorbed and recovered automatically.
- [ ] Lag stays far from retention, with alerts to prove it.
- [ ] Stateful jobs upgrade without losing state or events.

**Contracts and security**

- [ ] Protobuf schemas with enforced compatibility and CI checks.
- [ ] TLS, authentication, ACLs per service, and no secrets in code.
- [ ] Personal data minimised and absent from telemetry.

**Engineering and operations**

- [ ] Layered tests including property, integration, end-to-end, and chaos
      tests.
- [ ] Topics, schemas, ACLs, and jobs deployed as code through CI/CD.
- [ ] Tracing, SLA dashboards, actionable alerts, runbook, and drills.
- [ ] Requirements, event catalogue, topic design, delivery semantics,
      ADRs, capacity plan, cost analysis, and retrospective complete.

---

## 11. Evaluation rubric (self or peer review)

Score each area from 0 to 3. A production-grade project scores **at least 2
in every area** and **3 in Delivery semantics, Correctness, and
Resilience**.

| Area | What a "3" looks like |
| --- | --- |
| Delivery semantics | Every hop documented and proven; exactly-once effects under chaos |
| Correctness | Ground-truth and batch reconciliation pass; reprocessing works |
| Resilience | Bursts, outages, broker loss, and poison pills handled automatically |
| Event design and contracts | Clear envelope, keys, schemas, compatibility enforced in CI |
| Time and state | Measured watermarks, bounded state, documented late-data policy |
| Engine usage | Spark and Flink each used where they fit, with justified ADRs |
| Serving | Fresh, labelled, fast results via API and dashboard |
| Testing | Unit, property, integration, end-to-end, and chaos tests |
| Observability | End-to-end tracing, lag and latency SLOs, actionable alerts |
| Operations and cost | Runbook usable by others, capacity plan, cost-justified streaming |

---

## 12. Common pitfalls to avoid

- Processing-time windows for business metrics.
- Missing watermarks on stateful queries (unbounded state).
- Auto-committing offsets before processing, or committing outside the
  producer transaction in consume–transform–produce.
- Consumers reading transactional topics with `read_uncommitted`.
- Non-idempotent sinks (`INSERT` instead of keyed upserts) behind
  "exactly-once" engines.
- Alerts without deterministic ids, so retries send duplicate
  notifications.
- One malformed event blocking a partition.
- Deleting checkpoints or savepoints to "fix" a job.
- Increasing partitions without considering key ordering and state.
- Retention shorter than the longest plausible outage.
- Treating real-time dashboards as final truth without reconciliation.
- Choosing streaming for use cases a 15-minute micro-batch would serve at
  a fraction of the cost.

---

## 13. Suggested timeline

| Week | Milestones |
| --- | --- |
| 1 | M0 framing and platform · M1 events, contracts, topics |
| 2 | M2 producers and simulator · M3 raw archive |
| 3 | M4 validator and enrichment · M5 Spark aggregations |
| 4 | M6 Flink alerts · M7 serving |
| 5 | M8 correctness and reconciliation · M9 lag and scaling · M10 testing → **Core track complete** |
| 6 | M11 packaging and security · M12 CI/CD and safe upgrades |
| 7 | M13 observability · M14 operations and drills → **Production track complete** |
| 8 (optional) | M15 stretch goals |

---

## 14. What to show in a portfolio or interview

Be ready to explain:

1. Why each use case needs streaming — and which ones do not.
2. Your event envelope, keys, and topic design.
3. The delivery guarantee at every hop and how you proved it.
4. How watermarks were chosen and what happens to late events.
5. How state is bounded and how stateful jobs are upgraded.
6. Why Spark handles aggregations and Flink handles alerts (or why you
   would change that).
7. How real-time numbers are reconciled with batch truth.
8. What happened in your burst and outage drills, and how lag was kept away
   from retention.
9. The cost of always-on streaming versus micro-batch for each use case.

A README with the architecture diagram, the event catalogue, a short demo
(live dashboard, a fraud pattern producing one alert, a component killed and
recovered, reconciliation passing), and the runbook will show that you can
run real-time data in production — not just connect a consumer to a topic.
