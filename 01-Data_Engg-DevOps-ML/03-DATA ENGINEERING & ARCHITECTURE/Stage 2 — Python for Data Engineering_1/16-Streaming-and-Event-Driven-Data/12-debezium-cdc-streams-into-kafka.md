# CLAUDE CODE PROMPT — TEACH `12-debezium-cdc-streams-into-kafka.md`

Act as a **Senior Data Engineer with 10+ years of production experience** designing and operating large-scale data platforms, CDC pipelines, Kafka platforms, lakehouses, and event-driven systems.

Your task is to create/teach the complete learning content for:

`16-Streaming-and-Event-Driven-Data/12-debezium-cdc-streams-into-kafka.md`

This file belongs to the canonical Stage 2 module:

`Python for Data Engineering/16-Streaming-and-Event-Driven-Data/`

The authoritative topic is:

# Debezium CDC Streams into Kafka

---

## 1. STRICT FILE-SCOPE RULE

**IMPORTANT: DO NOT CHANGE, CREATE, DELETE, RENAME, OR UPDATE ANY OTHER FILE IN THE CURRENT FOLDER.**

You may work **ONLY** on:

`12-debezium-cdc-streams-into-kafka.md`

Do not modify:

- README.md
- `01-event-streams-vs-message-queues.md`
- `02-kafka-topics-partitions-offsets-and-replication.md`
- `03-kafka-producers-in-python.md`
- `04-kafka-consumers-and-consumer-groups.md`
- `05-delivery-semantics-at-most-at-least-and-exactly-once.md`
- `06-protobuf-and-schema-registry.md`
- `07-event-time-processing-time-and-watermarks.md`
- `08-tumbling-sliding-and-session-windows.md`
- `09-stateful-stream-processing.md`
- `10-spark-structured-streaming.md`
- `11-apache-flink-and-pyflink-overview.md`
- `13-backpressure-and-consumer-lag.md`
- `practice-questions.md`
- `interview-practice.md`
- any other file in the folder.

Do not reorganize the module.

Do not introduce unrelated topics from other modules.

---

# 2. PRIMARY LEARNING OBJECTIVE

Build the learner's understanding of **Change Data Capture (CDC) with Debezium and Kafka** from absolute fundamentals to advanced production architecture.

The learner must understand not merely how to run Debezium, but:

- what CDC is
- why CDC is needed
- why log-based CDC is powerful
- how PostgreSQL logical replication works
- how Debezium captures database changes
- how Kafka Connect fits into the architecture
- how Debezium converts database changes into Kafka events
- what the Debezium change-event envelope contains
- how snapshots work
- how streaming changes works after the snapshot
- how inserts, updates, deletes, and tombstones are represented
- how primary keys map to Kafka message keys
- how schemas work with Schema Registry
- how SMTs transform Debezium events
- how the Outbox Event Router works
- how CDC can feed a lakehouse
- how to handle duplicates, ordering, retries, and failures
- how replication slots work
- how WAL growth can become dangerous
- how heartbeats help maintain CDC health
- how schema changes affect CDC
- how to operate Debezium reliably in production.

Teach the subject in a **progressive learning sequence**:

**Database fundamentals → CDC fundamentals → log-based CDC → PostgreSQL logical replication → Debezium → Kafka Connect → Debezium architecture → snapshots → change events → Kafka topics → schemas → deletes/tombstones → SMTs → Outbox → lakehouse ingestion → failure recovery → operational monitoring → production architecture**

Do not jump directly into configuration.

---

# 3. TEACHING STYLE

Teach everything in **simple language first**, then progressively introduce professional terminology.

For every major concept use this structure whenever appropriate:

1. What is it?
2. Why does it exist?
3. What problem does it solve?
4. Simple real-world analogy
5. How it works internally
6. Minimal example
7. Python / SQL / configuration example where applicable
8. Production considerations
9. Common mistakes
10. Advanced considerations
11. Knowledge checkpoint

Avoid explaining concepts as isolated definitions.

Build a connected mental model.

For example, explain the complete chain:

```text
PostgreSQL
   ↓
WAL
   ↓
Logical Replication
   ↓
Replication Slot
   ↓
Debezium PostgreSQL Connector
   ↓
Kafka Connect
   ↓
Kafka Topic
   ↓
Consumer / Stream Processor
   ↓
Lakehouse / Search / Cache / Analytics / Services
```

The learner should understand exactly what happens at each stage.

---

# 4. START WITH THE PROBLEM CDC SOLVES

Begin by explaining why traditional database extraction approaches can become problematic.

Compare:

```text
Full extraction
Incremental extraction
Polling
Timestamp-based extraction
CDC
```

Explain problems such as:

- repeatedly scanning large tables
- detecting deletes
- detecting updates accurately
- missing changes
- source database load
- polling frequency
- latency
- race conditions
- late updates
- concurrent writes
- transactional consistency.

Use a simple example:

```text
orders
customers
payments
```

Show how an order changes:

```text
INSERT order
UPDATE order status
UPDATE order amount
DELETE order
```

Then explain why CDC can capture these changes as a stream of events.

---

# 5. CDC FUNDAMENTALS

Teach:

- Change Data Capture
- source database
- change event
- transaction
- insert
- update
- delete
- commit
- transaction log
- log-based CDC
- query-based CDC
- trigger-based CDC.

Compare the approaches.

Create a table comparing:

| Approach | How it works | Latency | Source load | Deletes | Reliability | Typical use |
|---|---|---|---|---|---|---|

Explain why **log-based CDC** is generally attractive for high-quality production pipelines.

Do not imply that CDC automatically solves every consistency problem.

---

# 6. LOG-BASED CDC

Explain database transaction logs.

Use a simple conceptual example:

```text
Application
    |
    v
PostgreSQL
    |
    +--> Tables
    |
    +--> WAL
```

Explain:

- Write-Ahead Log (WAL)
- why databases write changes to logs
- transaction ordering
- commit records
- log positions
- logical decoding
- physical vs logical replication
- why CDC systems consume logs instead of continuously querying tables.

Make clear that Debezium does not simply execute:

```sql
SELECT * FROM orders;
```

over and over.

Explain the distinction.

---

# 7. POSTGRESQL LOGICAL REPLICATION

This is an important foundation.

Teach:

- PostgreSQL WAL
- logical decoding
- replication slots
- publications
- `pgoutput`
- logical replication concepts
- source transaction ordering
- LSN (Log Sequence Number).

Explain the conceptual relationship:

```text
PostgreSQL transaction
        ↓
WAL
        ↓
Logical decoding
        ↓
Replication slot
        ↓
Debezium
```

Explain:

### Replication Slot

Teach:

- what a replication slot is
- why Debezium needs one
- how it tracks consumption progress
- why it protects WAL from being removed too early
- why an abandoned/unhealthy replication slot can cause WAL growth
- why WAL growth can eventually threaten database storage.

### Publication

Explain:

- what a PostgreSQL publication is
- which tables it exposes
- how Debezium uses it
- table selection.

### `pgoutput`

Explain that the PostgreSQL Debezium connector can use PostgreSQL's native logical replication output plugin:

`pgoutput`

Explain its role without unnecessarily diving into PostgreSQL internals outside the roadmap.

---

# 8. DEBEZIUM FUNDAMENTALS

Explain:

- what Debezium is
- why Debezium exists
- Debezium connectors
- Debezium PostgreSQL connector
- source connectors
- change events
- Kafka integration.

Build the architecture:

```text
PostgreSQL
    |
    | WAL / logical decoding
    v
Debezium PostgreSQL Connector
    |
    v
Kafka Connect
    |
    v
Kafka
```

Explain the responsibility of each component.

---

# 9. KAFKA CONNECT FUNDAMENTALS

Teach Kafka Connect before going deep into Debezium deployment.

Explain:

- Kafka Connect
- Connect worker
- connector
- task
- source connector
- sink connector
- converters
- REST API
- connector configuration
- distributed vs standalone mode at a conceptual level.

Explain:

```text
Kafka Connect Worker
        |
        +-- Debezium PostgreSQL Connector
        |
        +-- Task(s)
        |
        +-- Converter
        |
        +-- Kafka
```

Explain the distinction between:

```text
Kafka broker
Kafka Connect
Debezium
```

The learner must not confuse these components.

---

# 10. DEBEZIUM POSTGRESQL CONNECTOR ARCHITECTURE

Explain the full flow:

```text
PostgreSQL
    |
    | WAL
    v
Logical Decoding
    |
    | pgoutput
    v
Replication Slot
    |
    v
Debezium PostgreSQL Connector
    |
    v
Kafka Connect
    |
    v
Kafka Topics
```

Explain what happens:

1. PostgreSQL transaction occurs.
2. PostgreSQL writes to WAL.
3. WAL is logically decoded.
4. Debezium reads changes.
5. Debezium converts them into change events.
6. Kafka Connect serializes them.
7. Events are published to Kafka.
8. Consumers process the events.

Make this sequence extremely clear.

---

# 11. LOCAL DEVELOPMENT ENVIRONMENT

Create a realistic local lab using Docker Compose.

Use the roadmap's environment:

- PostgreSQL
- Kafka
- Kafka Connect
- Debezium PostgreSQL connector
- Schema Registry where appropriate
- Kafka UI where appropriate.

The environment should be realistic but understandable.

Show:

```text
docker-compose.yml
```

and explain important sections.

Use environment variables rather than hardcoding secrets.

Show how to verify:

```bash
docker compose ps
```

Show how to inspect PostgreSQL configuration.

Show how to verify Kafka Connect.

Show how to verify Debezium connector status.

---

# 12. POSTGRESQL CDC CONFIGURATION

Show the required conceptual configuration for PostgreSQL CDC.

Explain relevant settings such as:

- WAL level
- replication connections
- replication slots
- publication
- permissions
- replication user.

Use SQL examples where appropriate.

For example, show the conceptual setup for:

```sql
CREATE USER debezium ...
```

and:

```sql
CREATE PUBLICATION ...
```

Do not provide insecure production defaults without explanation.

Clearly distinguish:

```text
local development configuration
```

from:

```text
production configuration
```

---

# 13. REGISTERING THE DEBEZIUM CONNECTOR

Show a complete connector configuration example.

Use the Kafka Connect REST API.

Example structure:

```bash
curl -X POST ...
```

Explain important connector properties, including concepts such as:

- connector class
- database hostname
- database port
- database user
- database password
- database name
- plugin name
- slot name
- publication name
- topic prefix
- table inclusion
- snapshot mode
- converters
- schema history where applicable.

Explain every important configuration property.

Do not merely paste configuration.

---

# 14. SNAPSHOTS

This is a critical concept.

Explain why Debezium needs an initial snapshot.

Suppose the table already contains:

```text
1, Alice
2, Bob
3, Charlie
```

and CDC starts today.

How does the downstream system learn about Alice, Bob, and Charlie?

Explain the snapshot.

Teach:

- initial snapshot
- snapshot consistency
- snapshot + streaming handoff
- snapshot boundaries
- snapshot modes
- what happens after snapshot completion
- incremental snapshot awareness
- snapshot failure/restart considerations.

Explain the important transition:

```text
Existing database state
        ↓
Initial snapshot
        ↓
CDC streaming
        ↓
Future changes
```

Make the learner understand that CDC is not simply "start reading future changes."

---

# 15. DEBEZIUM CHANGE EVENT ENVELOPE

This is one of the most important parts of the file.

Teach the structure of a Debezium change event.

Use representative examples.

Explain fields/concepts such as:

```text
before
after
source
op
ts_ms
transaction
```

Where relevant.

Show examples for:

### INSERT

```json
{
  "before": null,
  "after": {...},
  "op": "c"
}
```

### UPDATE

```json
{
  "before": {...},
  "after": {...},
  "op": "u"
}
```

### DELETE

```json
{
  "before": {...},
  "after": null,
  "op": "d"
}
```

### READ / SNAPSHOT

Explain the `r` operation.

Do not oversimplify the meaning of each field.

Explain source metadata such as:

- database
- schema
- table
- LSN
- transaction information
- timestamps.

Explain why metadata matters for:

- ordering
- debugging
- replay
- lineage
- deduplication
- reconciliation.

---

# 16. CDC OPERATION TYPES

Teach clearly:

```text
c = create
u = update
d = delete
r = read/snapshot
```

Explain each with database examples.

Create a complete lifecycle:

```text
INSERT
  ↓
UPDATE
  ↓
UPDATE
  ↓
DELETE
```

Show the corresponding Debezium events.

Explain how consumers should interpret each operation.

---

# 17. KAFKA TOPICS GENERATED BY DEBEZIUM

Explain Debezium's topic model.

For example:

```text
<topic-prefix>.<schema>.<table>
```

Use a concrete conceptual example:

```text
dbserver.public.orders
```

Explain:

- topic naming
- table-to-topic mapping
- topic keys
- values
- partitions
- ordering implications
- consumer groups.

Explain why the primary key is generally important as the Kafka record key.

---

# 18. PRIMARY KEYS AND KAFKA MESSAGE KEYS

Teach:

```text
PostgreSQL Primary Key
        ↓
Kafka Record Key
```

Explain why this matters for:

- partitioning
- ordering per entity
- compaction
- downstream upserts
- deduplication.

Example:

```text
order_id = 1001
```

Explain how all events for order `1001` can be routed consistently.

Also discuss the limitations:

- hot keys
- skew
- missing primary keys
- composite keys.

---

# 19. SCHEMA REGISTRY AND DEBEZIUM

Connect this topic to the previous module topic on schemas.

Explain:

- Kafka message schemas
- Schema Registry
- Avro
- Protobuf
- converters
- schema IDs
- compatibility.

Explain the relationship:

```text
Database schema
       ↓
Debezium event schema
       ↓
Kafka serialization
       ↓
Schema Registry
       ↓
Consumers
```

Explain what happens when a database schema changes.

Discuss:

- adding columns
- removing columns
- changing data types
- compatibility
- downstream consumers.

Do not claim every database schema change is automatically safe.

---

# 20. DELETE EVENTS AND TOMBSTONES

Explain the difference between:

```text
DELETE event
```

and:

```text
TOMBSTONE
```

Explain why tombstones matter for Kafka log compaction.

Use a conceptual sequence:

```text
Key = 1001
Value = customer record

        ↓

DELETE event

        ↓

TOMBSTONE
Key = 1001
Value = null
```

Explain:

- delete semantics
- tombstone semantics
- compacted topics
- downstream state stores
- consumers that need to interpret deletes.

---

# 21. SINGLE MESSAGE TRANSFORMS (SMTs)

Teach Kafka Connect SMTs.

Explain:

- what SMTs are
- why they exist
- where they execute
- benefits
- limitations.

Discuss examples relevant to Debezium:

- unwrap Debezium envelope
- rename fields
- route topics
- filter fields/events
- add metadata
- transform keys.

Explain the trade-off:

```text
Raw Debezium envelope
        vs
Simplified downstream event
```

Teach the learner when **not** to overuse SMTs.

---

# 22. EVENT ENVELOPE UNWRAPPING

Explain the purpose of extracting:

```text
after
```

into a simpler event.

For example:

```text
Debezium envelope
       ↓
ExtractNewRecordState
       ↓
Simplified record
```

Explain the trade-offs:

### Raw envelope

Pros:

- full change information
- before/after
- operation
- metadata
- better auditability

Cons:

- more complex consumers

### Unwrapped event

Pros:

- simpler consumers
- easier analytics ingestion

Cons:

- may lose important CDC semantics unless metadata is preserved.

Explain when each model is appropriate.

---

# 23. OUTBOX PATTERN

This is a required advanced concept.

Teach the **Transactional Outbox Pattern**.

Explain the dual-write problem:

```text
Application
   |
   +--> Database
   |
   +--> Kafka
```

Why can this fail?

Example:

```text
DB transaction succeeds
Kafka publish fails
```

or:

```text
Kafka publish succeeds
DB transaction fails
```

Then introduce:

```text
Application
    |
    v
Database Transaction
    |
    +--> Business tables
    |
    +--> Outbox table
             |
             v
         Debezium
             |
             v
           Kafka
```

Explain why this provides a safer integration pattern.

---

# 24. DEBEZIUM OUTBOX EVENT ROUTER

Teach the Debezium Outbox Event Router concept.

Explain:

- outbox table
- event ID
- aggregate type
- aggregate ID
- event type
- payload
- routing
- topic selection.

Show an example outbox schema.

For example:

```sql
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY,
    aggregate_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);
```

Explain how an application writes the business transaction and outbox event in the same database transaction.

Then explain how Debezium publishes the event to Kafka.

---

# 25. CDC TO LAKEHOUSE

Teach the production architecture:

```text
PostgreSQL
      |
      v
Debezium
      |
      v
Kafka
      |
      v
Stream Processor
      |
      v
Delta / Iceberg
```

Explain how CDC events can be used to maintain a lakehouse table.

Teach the conceptual transformation:

```text
INSERT → insert row
UPDATE → update row
DELETE → delete row
```

Explain:

- event keys
- ordering
- deduplication
- transaction ordering
- LSN
- MERGE
- idempotent processing
- replay.

Show a conceptual SQL `MERGE`.

Do not pretend that simply writing CDC events into files automatically produces a correct current-state table.

---

# 26. CDC DEDUPLICATION AND ORDERING

Explain why duplicates can happen.

Connect this to the module's delivery-semantics topic.

Teach:

```text
At-least-once CDC delivery
        +
Retries
        +
Consumer restart
        =
Potential duplicate processing
```

Explain how downstream systems can use:

- primary key
- event ID
- LSN
- transaction metadata
- deterministic merge logic
- idempotent writes.

Discuss ordering carefully.

Explain the distinction between:

```text
Kafka partition ordering
```

and:

```text
global database ordering
```

Do not claim that Kafka automatically gives global ordering.

---

# 27. TRANSACTION ORDERING

Explain why transactions matter in CDC.

Use a simple example:

```text
Transaction T1:
UPDATE customers
UPDATE orders
COMMIT
```

Explain why downstream consumers may care about transaction boundaries and metadata.

Discuss:

- transaction IDs
- transaction metadata
- commit ordering
- LSN
- downstream consistency.

Stay within the roadmap's CDC scope.

---

# 28. HEARTBEATS

Teach Debezium heartbeats.

Explain:

- why heartbeats exist
- low-traffic databases
- replication slot health
- WAL retention
- monitoring progress.

Explain the problem:

```text
Database has almost no writes
        ↓
CDC appears quiet
        ↓
Monitoring cannot easily distinguish
healthy idle state from stalled CDC
```

Explain how heartbeats help.

---

# 29. REPLICATION SLOT HEALTH AND WAL GROWTH

This is a critical production topic.

Teach:

```text
PostgreSQL
    |
    v
WAL
    |
    v
Replication Slot
    |
    v
Debezium
```

Explain what happens when Debezium stops consuming.

Example:

```text
Debezium stopped
      ↓
Replication slot remains
      ↓
PostgreSQL retains WAL
      ↓
WAL grows
      ↓
Disk usage increases
      ↓
Database risk
```

Explain monitoring signals such as:

- replication slot lag
- WAL retention
- database disk usage
- connector health
- connector offsets
- heartbeat activity.

Explain why replication slots must be treated as production infrastructure.

---

# 30. CONNECTOR FAILURE AND RECOVERY

Teach failure scenarios.

At minimum cover:

### Scenario 1 — Debezium connector crashes

What happens?

### Scenario 2 — Kafka is temporarily unavailable

What happens?

### Scenario 3 — PostgreSQL restarts

What happens?

### Scenario 4 — Kafka Connect worker restarts

What happens?

### Scenario 5 — Network interruption

What happens?

### Scenario 6 — Connector is stopped for a long period

What happens to WAL?

### Scenario 7 — Replication slot becomes unhealthy

What happens?

For each scenario explain:

```text
Failure
→ Detection
→ Recovery
→ Data-loss risk
→ Duplicate risk
→ Verification
```

---

# 31. SNAPSHOT + STREAMING FAILURE SCENARIOS

Explain failure during:

- initial snapshot
- transition from snapshot to streaming
- connector restart
- Kafka outage
- PostgreSQL restart.

Teach how operators should reason about:

```text
What has already been captured?
What remains?
Where is progress stored?
Can the operation be replayed?
Can duplicates occur?
How do we verify correctness?
```

---

# 32. DATABASE SCHEMA EVOLUTION

Explain what happens when a source table changes.

Examples:

```sql
ALTER TABLE orders
ADD COLUMN discount DECIMAL;
```

Then discuss:

- Debezium schema updates
- Kafka schema changes
- Schema Registry compatibility
- downstream consumers
- lakehouse schemas
- breaking changes.

Discuss safe vs dangerous changes.

Examples:

```text
Adding nullable column
Changing data type
Renaming column
Dropping column
Changing primary key
```

Explain that schema evolution must be treated as a contract.

---

# 33. TABLE FILTERING

Explain how production systems avoid capturing every database table.

Teach concepts such as:

- included tables
- excluded tables
- schema filters
- topic prefix
- connector scope.

Explain why filtering is important for:

- performance
- security
- cost
- operational simplicity
- avoiding accidental exposure.

---

# 34. SECURITY

Teach production security at a practical level.

Cover:

- least-privilege database user
- Kafka authentication awareness
- TLS awareness
- secrets management
- database credentials
- Kafka ACLs
- network isolation
- sensitive columns
- PII considerations.

Do not expand this into a general security course.

Keep it specific to CDC pipelines.

---

# 35. OBSERVABILITY

Define the important CDC observability dimensions.

Monitor:

### Source

- PostgreSQL health
- WAL growth
- replication slot lag
- replication status

### Debezium

- connector status
- task status
- event throughput
- errors
- restart count
- snapshot progress

### Kafka

- topic throughput
- partition distribution
- producer failures
- consumer lag

### Downstream

- processing latency
- failed records
- DLQ volume
- reconciliation failures.

Teach the difference between:

```text
connector healthy
```

and:

```text
data pipeline healthy
```

A connector can be running while downstream processing is broken.

---

# 36. CDC DATA QUALITY

Explain how to prove CDC correctness.

Teach reconciliation techniques.

Examples:

```text
source row count
vs
lakehouse current-state row count
```

and:

```text
source checksum
vs
destination checksum
```

and:

```text
latest source update
vs
latest downstream update
```

Use LSN/event metadata where appropriate.

Explain that "Kafka has messages" does not prove that the downstream table is correct.

---

# 37. PRODUCTION CDC ARCHITECTURE

Design a complete architecture:

```text
                 ┌─────────────────┐
                 │   PostgreSQL    │
                 └────────┬────────┘
                          │
                         WAL
                          │
                          v
                 ┌─────────────────┐
                 │    Debezium     │
                 │ PostgreSQL Conn │
                 └────────┬────────┘
                          │
                    Kafka Connect
                          │
                          v
                 ┌─────────────────┐
                 │      Kafka      │
                 │ CDC Topics      │
                 └───────┬─────────┘
                         / \
                        /   \
                       v     v
                  Spark      Flink
                     |          |
                     v          v
                Lakehouse    Alerts
```

Explain every component.

Then extend the architecture with:

- Schema Registry
- Kafka Connect cluster
- monitoring
- DLQ where appropriate
- reconciliation
- object storage/lakehouse
- operational alerts.

---

# 38. HANDS-ON PROJECT

Build a complete local CDC lab.

Project structure:

```text
debezium_cdc_lab/
├── docker-compose.yml
├── postgres/
│   └── init.sql
├── connectors/
│   └── postgres-connector.json
├── producer/
│   └── seed_data.py
├── consumers/
│   └── cdc_consumer.py
├── lakehouse/
│   └── ...
├── tests/
│   └── ...
└── README.md
```

Only create these files if they are explicitly part of the learning lab environment and do not modify unrelated curriculum files.

The main learning file itself must remain:

`12-debezium-cdc-streams-into-kafka.md`

---

# 39. HANDS-ON LAB — PART 1: POSTGRESQL

Create:

```text
customers
orders
payments
```

Seed realistic data.

Show:

```sql
INSERT
UPDATE
DELETE
```

operations.

Explain what should appear in CDC.

---

# 40. HANDS-ON LAB — PART 2: DEBEZIUM

Configure:

```text
PostgreSQL
+
Debezium
+
Kafka Connect
+
Kafka
```

Register the connector.

Verify:

```bash
GET /connectors
```

and connector status.

---

# 41. HANDS-ON LAB — PART 3: INSPECT RAW EVENTS

Produce database changes.

Inspect the Kafka events.

For each event identify:

```text
key
before
after
op
source
timestamp
LSN
transaction metadata
```

The learner must manually trace:

```text
SQL statement
→ WAL
→ Debezium
→ Kafka record
```

---

# 42. HANDS-ON LAB — PART 4: UPDATE AND DELETE

Perform:

```sql
UPDATE orders ...
DELETE FROM orders ...
```

Observe:

```text
op = u
op = d
```

Then explain tombstone behavior.

---

# 43. HANDS-ON LAB — PART 5: OUTBOX

Create an outbox table.

Perform:

```text
business transaction
+
outbox insert
```

in the same PostgreSQL transaction.

Configure Debezium Outbox Event Router conceptually.

Verify that business events appear in Kafka.

Explain why this is safer than application-level dual writes.

---

# 44. HANDS-ON LAB — PART 6: CDC TO LAKEHOUSE

Consume CDC events.

Implement a downstream process that maintains a current-state table.

Demonstrate:

```text
INSERT
UPDATE
DELETE
```

using idempotent merge logic.

Include duplicate-event testing.

Verify the resulting state against PostgreSQL.

---

# 45. HANDS-ON LAB — PART 7: FAILURE TESTING

Perform controlled failures:

1. Stop Debezium.
2. Continue writing to PostgreSQL.
3. Observe WAL/replication slot behavior.
4. Restart Debezium.
5. Verify CDC catches up.
6. Introduce Kafka interruption.
7. Restart Kafka/Connect.
8. Verify downstream correctness.
9. Check for duplicates.
10. Reconcile source and destination.

Document the results.

---

# 46. HANDS-ON LAB — PART 8: SCHEMA EVOLUTION

Start with:

```text
orders(id, customer_id, amount, status)
```

Add:

```text
discount
```

Then test another potentially breaking change.

Observe:

```text
PostgreSQL schema
→ Debezium schema
→ Kafka schema
→ consumer behavior
```

Explain which changes are safe and which require coordination.

---

# 47. HANDS-ON LAB — PART 9: WAL GROWTH EXPERIMENT

Perform:

```text
Stop Debezium
↓
Generate database writes
↓
Observe WAL / replication slot state
↓
Restart Debezium
↓
Observe catch-up
```

Explain:

```text
why WAL grew
why it was retained
how Debezium caught up
what operational risk existed.
```

Do not intentionally fill the machine's disk.

Use a bounded experiment.

---

# 48. PYTHON CONSUMER EXAMPLE

Provide a simple Python Kafka consumer that reads Debezium events.

Use a production-relevant library consistent with the module environment.

The example should show:

```text
consume
→ deserialize
→ inspect op
→ process
→ handle errors
→ commit safely
```

Explain how the consumer differs when:

```text
raw Debezium envelope
```

versus:

```text
unwrapped event
```

is consumed.

---

# 49. ADVANCED PYTHON PROCESSING

Show a more production-oriented consumer pattern.

Include concepts such as:

- idempotency
- event ID
- primary key
- operation type
- retries
- DLQ
- structured logging
- graceful shutdown
- manual offset commit
- metrics.

Do not make the code unnecessarily complex.

Every advanced feature must have a reason.

---

# 50. CDC → KAFKA → SPARK/FLINK CONNECTION

Briefly connect this topic to the following module topics already covered.

Show:

```text
Debezium
   ↓
Kafka
   ↓
Spark Structured Streaming / Flink
   ↓
Lakehouse / Alerts
```

Explain why Debezium is generally the **source CDC layer**, while Spark/Flink are **processing layers**.

Do not duplicate the full Spark or Flink lessons.

Only establish the integration mental model.

---

# 51. COMMON CDC MISTAKES

Create a dedicated section.

At minimum cover:

1. Treating Debezium as a polling system.
2. Not understanding WAL.
3. Ignoring replication slots.
4. Ignoring WAL growth.
5. Treating snapshot as future-only CDC.
6. Ignoring deletes.
7. Ignoring tombstones.
8. Assuming Kafka provides global ordering.
9. Assuming CDC is automatically exactly-once end-to-end.
10. Ignoring duplicates.
11. Losing the Kafka record key.
12. Blindly unwrapping the Debezium envelope.
13. Ignoring schema evolution.
14. Running overly broad table capture.
15. Ignoring PII/security.
16. Not monitoring connector health.
17. Not reconciling source and destination.
18. Using the Outbox Pattern incorrectly.
19. Treating connector RUNNING status as proof of pipeline correctness.
20. Leaving abandoned replication slots.

For every mistake explain:

```text
Why it happens
Why it is dangerous
How to prevent it
```

---

# 52. DEBUGGING PLAYBOOK

Create a practical troubleshooting guide.

Examples:

### Problem

"No Kafka CDC messages."

Check:

```text
PostgreSQL configuration
→ publication
→ replication slot
→ connector status
→ task status
→ Kafka topic
```

### Problem

"CDC stopped."

Check:

```text
connector
→ task
→ database
→ replication slot
→ Kafka
→ network
```

### Problem

"WAL keeps growing."

Check:

```text
replication slot
→ Debezium consumption
→ connector health
→ slot restart_lsn / progress
```

### Problem

"Duplicate records downstream."

Check:

```text
consumer commits
→ retries
→ replay
→ idempotency
→ merge logic
```

### Problem

"Delete did not reach the destination."

Check:

```text
op=d
→ tombstone
→ serializer
→ consumer
→ sink logic
```

---

# 53. PRODUCTION DESIGN DECISIONS

Teach the learner how to reason about:

- snapshot strategy
- table selection
- topic naming
- partitioning
- key selection
- schema format
- raw vs unwrapped events
- SMT usage
- Outbox usage
- lakehouse ingestion
- retention
- security
- monitoring
- recovery
- reconciliation.

For every decision explain:

```text
Requirement
→ Options
→ Trade-offs
→ Recommended choice
→ Failure mode
```

---

# 54. ADVANCED DESIGN SCENARIOS

Include realistic senior-level scenarios.

### Scenario 1

A PostgreSQL database has 5,000 tables but only 50 need CDC.

Design the connector strategy.

### Scenario 2

A high-volume orders table has a hot partition.

How would you reason about Kafka keys and partitioning?

### Scenario 3

Debezium is down for two hours.

The database continues receiving writes.

What happens?

### Scenario 4

WAL is growing rapidly.

How do you investigate?

### Scenario 5

A downstream lakehouse table contains duplicates.

How do you diagnose and repair it?

### Scenario 6

A delete is visible in Kafka but not reflected in the lakehouse.

Trace the problem.

### Scenario 7

The database schema changes unexpectedly.

How should the CDC platform respond?

### Scenario 8

The application needs to publish business events and update PostgreSQL atomically.

Should it publish directly to Kafka?

Explain the Outbox decision.

### Scenario 9

A consumer team asks for only the latest row state instead of CDC history.

Should you unwrap the Debezium envelope?

Discuss trade-offs.

### Scenario 10

A CDC pipeline says:

```text
Connector = RUNNING
Kafka = healthy
```

but downstream data is stale.

Explain how you would investigate end-to-end.

---

# 55. MENTAL MODELS

End the conceptual teaching with strong mental models.

The learner should remember:

### Mental Model 1

```text
CDC = turning database changes into a stream of events.
```

### Mental Model 2

```text
PostgreSQL WAL
→ logical decoding
→ Debezium
→ Kafka
```

### Mental Model 3

```text
Snapshot = existing state
Streaming = future changes
```

### Mental Model 4

```text
Primary key
→ Kafka key
→ partitioning
→ ordering per entity
→ downstream upsert
```

### Mental Model 5

```text
Replication slot protects CDC progress
but can also retain WAL if CDC stops.
```

### Mental Model 6

```text
Debezium RUNNING
≠
End-to-end CDC correctness
```

### Mental Model 7

```text
Raw CDC event
→ process
→ idempotent sink
→ verified current state
```

---

# 56. KNOWLEDGE CHECKPOINTS

After every major section include short checkpoints.

Examples:

```text
Checkpoint:
Why does Debezium need PostgreSQL logical decoding?
```

```text
Checkpoint:
What is the difference between a replication slot and a Kafka offset?
```

```text
Checkpoint:
Why is the initial snapshot necessary?
```

```text
Checkpoint:
What does op='u' mean?
```

```text
Checkpoint:
Why are tombstones important?
```

```text
Checkpoint:
Why can a stopped Debezium connector cause WAL growth?
```

```text
Checkpoint:
Why is an idempotent downstream sink important?
```

Do not provide only memorization questions.

Require reasoning.

---

# 57. PROGRESSIVE EXERCISES

Provide exercises from beginner to advanced.

## Level 1 — Basic

- Define CDC.
- Explain WAL.
- Explain Debezium.
- Explain Kafka Connect.
- Explain snapshots.

## Level 2 — Intermediate

- Configure a PostgreSQL CDC connector.
- Inspect insert/update/delete events.
- Identify `before`, `after`, `op`.
- Identify Kafka keys.
- Explain tombstones.

## Level 3 — Advanced

- Build CDC → Kafka → sink.
- Implement idempotent processing.
- Implement reconciliation.
- Test connector restart.
- Test Kafka outage.

## Level 4 — Senior

- Design multi-table CDC.
- Design Outbox architecture.
- Design CDC → lakehouse.
- Diagnose WAL growth.
- Design schema evolution.
- Design observability and SLOs.

---

# 58. FINAL MINI-PROJECT

Create a realistic mini-project:

# PostgreSQL → Debezium → Kafka CDC Platform

Requirements:

```text
PostgreSQL
    ↓
Debezium
    ↓
Kafka
    ↓
Python consumer
    ↓
Current-state sink
```

Include:

### Source tables

```text
customers
orders
payments
```

### CDC

Capture:

```text
insert
update
delete
```

### Kafka

Use:

```text
database/schema/table
```

topic organization.

Use primary keys as record keys.

### Consumer

Implement:

- manual commit
- idempotency
- structured logging
- error handling
- DLQ awareness.

### Sink

Maintain current-state tables.

### Failure tests

Test:

- consumer crash
- Debezium restart
- Kafka interruption
- duplicate processing
- source writes while Debezium is unavailable.

### Verification

Compare:

```text
PostgreSQL current state
vs
downstream current state
```

The final system should demonstrate that the learner understands **correctness**, not merely deployment.

---

# 59. INTERVIEW PREPARATION

At the end include senior Data Engineer interview questions specifically about this topic.

Questions should progress:

```text
Basic
→ Intermediate
→ Advanced
→ Senior architecture
```

Examples:

- What is CDC?
- Why is log-based CDC useful?
- How does Debezium capture PostgreSQL changes?
- What is logical decoding?
- What is a replication slot?
- Why can replication slots cause WAL growth?
- What is the Debezium event envelope?
- What does `op='u'` mean?
- What is the difference between delete and tombstone?
- Why are Kafka record keys important?
- How does Debezium perform an initial snapshot?
- What happens when Debezium is down?
- How do you make downstream CDC processing idempotent?
- What is the Outbox Pattern?
- Why is the Outbox Pattern useful?
- How would you build CDC into a lakehouse?
- How would you diagnose WAL growth?
- How would you handle schema evolution?
- How would you design CDC for millions of changes per minute?
- How would you prove end-to-end CDC correctness?

For architecture questions, require the learner to explain:

```text
architecture
+
data flow
+
failure modes
+
recovery
+
trade-offs
+
observability
```

---

# 60. FINAL ASSESSMENT

Create a final assessment covering the entire file.

It should test whether the learner can:

1. Explain CDC from first principles.
2. Explain log-based CDC.
3. Explain PostgreSQL WAL.
4. Explain logical decoding.
5. Explain replication slots.
6. Explain publications.
7. Explain Debezium.
8. Explain Kafka Connect.
9. Configure a Debezium PostgreSQL connector.
10. Explain snapshots.
11. Interpret Debezium events.
12. Explain `c`, `u`, `d`, and `r`.
13. Explain Kafka keys.
14. Explain deletes and tombstones.
15. Explain Schema Registry integration.
16. Explain SMTs.
17. Explain the Outbox Pattern.
18. Explain CDC → Kafka → lakehouse.
19. Handle duplicates.
20. Reason about ordering.
21. Diagnose connector failures.
22. Diagnose WAL growth.
23. Handle schema evolution.
24. Design CDC observability.
25. Design a production-grade CDC architecture.

Include a mixture of:

- conceptual questions
- SQL exercises
- configuration exercises
- debugging scenarios
- architecture questions
- failure scenarios
- coding exercises.

---

# 61. PRODUCTION-READINESS CHECKLIST

Finish with a checklist.

The learner should be able to answer YES to:

### Fundamentals

- [ ] I understand CDC.
- [ ] I understand log-based CDC.
- [ ] I understand PostgreSQL WAL.
- [ ] I understand logical decoding.
- [ ] I understand replication slots.

### Debezium

- [ ] I understand Debezium architecture.
- [ ] I understand Kafka Connect.
- [ ] I can configure a PostgreSQL connector.
- [ ] I understand snapshots.
- [ ] I can interpret CDC events.

### Kafka

- [ ] I understand Debezium topic naming.
- [ ] I understand Kafka record keys.
- [ ] I understand partition ordering.
- [ ] I understand tombstones.

### Reliability

- [ ] I understand duplicates.
- [ ] I can design idempotent CDC processing.
- [ ] I understand connector recovery.
- [ ] I understand replication slot failure risks.
- [ ] I understand WAL growth.

### Integration

- [ ] I understand Schema Registry integration.
- [ ] I understand SMTs.
- [ ] I understand the Outbox Pattern.
- [ ] I can design CDC → Kafka → lakehouse.

### Operations

- [ ] I know what to monitor.
- [ ] I can diagnose stalled CDC.
- [ ] I can diagnose WAL growth.
- [ ] I can perform source-vs-destination reconciliation.
- [ ] I can design production failure recovery.

---

# 62. IMPORTANT VERSION-AWARENESS RULE

Use current, production-relevant concepts, but avoid blindly assuming that every version behaves identically.

The broader module uses:

- Kafka 4.x
- KRaft rather than ZooKeeper
- modern Kafka Connect
- PostgreSQL logical replication
- current Debezium concepts.

Where behavior is version-sensitive:

1. identify the version;
2. explain the version-sensitive behavior;
3. avoid obsolete configuration unless explicitly labeled as legacy;
4. prefer current official behavior.

Do not teach obsolete ZooKeeper-based Kafka architecture as the default.

---

# 63. DOCUMENT QUALITY REQUIREMENTS

The finished:

`12-debezium-cdc-streams-into-kafka.md`

must be:

- beginner-friendly
- technically rigorous
- production-oriented
- sequential
- self-contained
- practical
- code-heavy where useful
- simple before advanced
- explicit about failure modes
- explicit about trade-offs
- explicit about operational concerns.

Use:

- Markdown headings
- diagrams using Mermaid where useful
- tables
- SQL
- Python
- JSON
- YAML
- shell commands
- configuration examples
- architecture diagrams
- troubleshooting tables
- checklists.

Do not add irrelevant content from unrelated modules.

Do not repeat entire Spark, Flink, Kafka producer, Kafka consumer, or schema-registry courses. Reference their concepts only when necessary to explain Debezium's role in the larger pipeline.

---

# 64. REQUIRED END-TO-END LEARNING FLOW

The final lesson must follow this progression:

```text
1. Why CDC?
        ↓
2. CDC fundamentals
        ↓
3. Log-based CDC
        ↓
4. PostgreSQL WAL
        ↓
5. Logical decoding
        ↓
6. Replication slots
        ↓
7. Publications
        ↓
8. Debezium
        ↓
9. Kafka Connect
        ↓
10. PostgreSQL connector
        ↓
11. Snapshot
        ↓
12. Streaming changes
        ↓
13. Debezium event envelope
        ↓
14. Kafka topics and keys
        ↓
15. Schemas
        ↓
16. Deletes and tombstones
        ↓
17. SMTs
        ↓
18. Outbox Pattern
        ↓
19. CDC → lakehouse
        ↓
20. Idempotency and ordering
        ↓
21. Failures and recovery
        ↓
22. Schema evolution
        ↓
23. WAL/slot operations
        ↓
24. Observability
        ↓
25. Production architecture
        ↓
26. Hands-on project
        ↓
27. Interview preparation
        ↓
28. Final assessment
```

Do not skip stages.

---

# 65. FINAL INSTRUCTION TO CLAUDE CODE

Before finishing, verify that the file covers **every concept in the Debezium CDC topic from the canonical Module 2.16 roadmap**, especially:

- Kafka Connect workers/connectors/tasks/converters/REST
- Debezium PostgreSQL connector
- PostgreSQL logical decoding
- `pgoutput`
- replication slots
- publications
- topic-per-table behavior
- primary-key Kafka keys
- Debezium change envelope
- `before`
- `after`
- `op`
- source metadata
- LSN
- transaction metadata
- snapshot behavior
- initial/incremental snapshot awareness
- deletes
- tombstones
- Schema Registry converters
- SMTs
- envelope unwrapping
- Outbox Event Router
- heartbeats
- replication-slot health
- WAL growth
- CDC → Kafka → lakehouse
- deduplication
- ordering
- schema changes
- connector operations
- failure recovery.

Then perform a **coverage audit**.

Create an internal checklist:

```text
Roadmap concept
→ Explained?
→ Example provided?
→ Code/config provided where useful?
→ Production implication explained?
→ Failure mode explained?
→ Exercise provided?
```

If anything is missing, add it before finishing.

Finally verify:

```text
ONLY 12-debezium-cdc-streams-into-kafka.md
```

was modified.

Do not modify any other file in:

`16-Streaming-and-Event-Driven-Data/`