# CLAUDE CODE PROMPT

## ROLE

Act as a **Senior Data Engineer with 10+ years of industry experience** designing, building, and operating production-grade Apache Kafka platforms, Python streaming applications, distributed data pipelines, event-driven systems, CDC pipelines, and high-throughput data infrastructure.

You are teaching me the following canonical Stage 2 Data Engineering learning file:

```text
Python for Data Engineering/
└── 16-Streaming-and-Event-Driven-Data/
    └── 04-kafka-consumers-and-consumer-groups.md
```

The authoritative roadmap is:

```text
16-Streaming-and-Event-Driven-Data/
```

Your task is to create/update **ONLY**:

```text
16-Streaming-and-Event-Driven-Data/04-kafka-consumers-and-consumer-groups.md
```

### STRICT FILE-SAFETY REQUIREMENT

Do NOT:

- modify another file
- create another file
- delete another file
- rename another file
- reorganize the folder
- modify previous Module 2.16 files
- modify future Module 2.16 files

You may inspect other files for context if necessary, but **ONLY `04-kafka-consumers-and-consumer-groups.md` may be changed.**

---

# 1. PRIMARY OBJECTIVE

Build a **complete professional learning module** for:

> **Kafka Consumers and Consumer Groups**

The module must teach the subject from absolute beginner level through advanced production-level understanding.

The progression must be:

```text
Why consumers exist
        ↓
Kafka consumer architecture
        ↓
Python Kafka Consumer
        ↓
Consumer configuration
        ↓
poll()
        ↓
Records and metadata
        ↓
Consumer groups
        ↓
Partitions and parallelism
        ↓
Offset management
        ↓
auto.offset.reset
        ↓
Manual commits
        ↓
Synchronous vs asynchronous commits
        ↓
Commit-after-processing
        ↓
Rebalances
        ↓
Eager vs cooperative rebalancing
        ↓
Rebalance callbacks
        ↓
Timeouts
        ↓
session.timeout.ms
        ↓
max.poll.interval.ms
        ↓
Static membership
        ↓
Replay
        ↓
Seek
        ↓
Offset/timestamp-based replay
        ↓
Poison messages
        ↓
DLQ
        ↓
Pause/resume
        ↓
Idempotent sinks
        ↓
Failure recovery
        ↓
Operational consumer design
```

Do not jump directly into advanced Kafka terminology.

Build the mental model step by step.

---

# 2. AUTHORITATIVE ROADMAP SCOPE

The canonical Module 2.16 roadmap requires this file to cover all of the following:

- Kafka Python Consumer
- Consumer configuration
- `group.id`
- `subscribe()`
- `poll()`
- Consumer errors
- `close()`
- Consumer groups
- Partition assignment
- Consumer parallelism
- `auto.offset.reset`
- Offset commits
- Automatic offset commits
- Manual offset commits
- Commit after processing
- Synchronous commits
- Asynchronous commits
- Rebalances
- Eager rebalancing
- Cooperative/incremental rebalancing
- Rebalance callbacks
- Newer consumer rebalance protocol awareness
- `session.timeout.ms`
- `max.poll.interval.ms`
- Static membership
- Batch processing
- Commit per batch
- Seek
- Replay by offset
- Replay by timestamp
- Poison pills
- Dead-letter queues
- Pause/resume
- Flow control
- Idempotent sinks
- Upsert using event IDs
- Consumer failure/recovery
- One consumer with six partitions
- Eight consumers with six partitions
- Rebalance storm experiment
- Idempotent PostgreSQL sink
- Rebalance callback experiment
- DLQ experiment
- Timestamp replay experiment
- Consumer kill/restart
- Verification that events are not lost
- Verification that duplicates are absorbed

Do not skip any of these concepts.

The roadmap is the source of truth for the scope of this file.

---

# 3. IMPORTANT CURRICULUM BOUNDARY

This file is specifically about:

> **Kafka consumers and consumer groups.**

Do not turn it into the later delivery-semantics module.

The following file is separate:

```text
05-delivery-semantics-at-most-once-at-least-once-exactly-once.md
```

Therefore this file may explain the mechanics necessary to understand consumer reliability, but detailed delivery-semantics theory must remain in File 05.

Similarly, do not deeply teach:

```text
06-protobuf-and-schema-registry.md
07-event-time-processing-time-and-watermarks.md
08-tumbling-sliding-and-session-windows.md
09-stateful-stream-processing.md
10-spark-structured-streaming.md
11-apache-flink-and-pyflink-overview.md
12-debezium-cdc-streams-into-kafka.md
13-backpressure-and-consumer-lag.md
```

Those are separate curriculum modules.

You may reference them briefly when necessary.

---

# 4. START WITH THE FUNDAMENTAL QUESTION

Start with:

> What is a Kafka consumer?

Explain simply:

> A Kafka consumer is an application that reads records from Kafka topics and performs some processing on them.

Show:

```text
Kafka Topic
    |
    v
Partition
    |
    v
Consumer
    |
    v
Processing
    |
    v
Sink / Database / API / File
```

Then explain the responsibilities of:

```text
Producer
Broker
Consumer
```

Make this distinction very clear.

---

# 5. WHY CONSUMERS EXIST

Explain realistic consumer use cases:

- Data ingestion
- Analytics
- Fraud detection
- Notifications
- Database synchronization
- Search indexing
- Lakehouse ingestion
- ETL/ELT
- Materialized views
- Event-driven services

Example:

```text
Kafka
  |
  +----> Analytics Consumer
  |
  +----> Fraud Consumer
  |
  +----> Warehouse Consumer
  |
  +----> Notification Consumer
```

Explain that the same event stream can support multiple independent consumers.

---

# 6. PYTHON KAFKA CONSUMER

Use the curriculum's Python Kafka stack:

```python
from confluent_kafka import Consumer
```

Explain installation and basic configuration.

Start with:

```python
from confluent_kafka import Consumer

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "orders-consumer",
    "auto.offset.reset": "earliest",
})
```

Explain every configuration option.

Do not hide the configuration behind a custom framework at first.

---

# 7. `group.id`

Teach `group.id` extremely clearly.

Explain:

> A consumer group is a set of consumers cooperating to process partitions of a topic.

Explain:

```text
group.id = "orders-consumer"
```

means the consumer belongs to that logical consumer group.

Then show:

```text
Topic: orders

Consumer Group A
    Consumer A1
    Consumer A2
    Consumer A3

Consumer Group B
    Consumer B1
    Consumer B2
```

Explain:

- Same group → consumers share partitions
- Different groups → each group independently consumes the topic

This is one of the most important concepts in the module.

---

# 8. `subscribe()`

Teach:

```python
consumer.subscribe(["orders"])
```

Explain:

- Topic subscription
- Group membership
- Partition assignment
- Why consumers generally subscribe rather than manually assign partitions in common group-based applications

Also explain the distinction between:

```text
subscribe()
```

and:

```text
assign()
```

Only introduce manual assignment conceptually if needed; keep the main curriculum focused on consumer groups.

---

# 9. `poll()`

Teach:

```python
msg = consumer.poll(1.0)
```

from first principles.

Explain:

- Polling for records
- Timeout
- Returned message
- No message
- Error event
- Record event

Explain that a Kafka consumer is not simply:

```python
while True:
    read_message()
```

Instead, it interacts with Kafka through the consumer polling model.

---

# 10. BASIC CONSUMER LOOP

Build the simplest useful consumer:

```python
from confluent_kafka import Consumer, KafkaException

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "orders-consumer",
    "auto.offset.reset": "earliest",
})

consumer.subscribe(["orders"])

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            raise KafkaException(msg.error())

        print(
            msg.topic(),
            msg.partition(),
            msg.offset(),
            msg.key(),
            msg.value(),
        )

finally:
    consumer.close()
```

Explain every important line.

Then improve it incrementally.

---

# 11. CONSUMER RECORD METADATA

Teach the metadata available from a consumed record.

Explain:

- Topic
- Partition
- Offset
- Key
- Value
- Timestamp
- Headers

Show how to inspect them.

Explain why metadata matters for:

- Debugging
- Replay
- Ordering
- Observability
- Idempotency
- Auditing

---

# 12. CONSUMER ERRORS

Teach consumer error handling.

Explain:

- Kafka errors
- Temporary conditions
- Partition EOF
- Authentication/authorization failures at a conceptual level
- Broker connectivity problems
- Serialization/deserialization errors conceptually
- Application-level processing errors

Do not treat every `msg.error()` as the same kind of failure.

Explain the difference between:

```text
Kafka protocol/client event
```

and:

```text
Application processing failure
```

---

# 13. `close()`

Teach:

```python
consumer.close()
```

Explain why graceful shutdown matters.

Show:

```text
SIGTERM
   ↓
Stop consuming new work
   ↓
Finish current processing
   ↓
Commit appropriate offsets
   ↓
Leave group
   ↓
Close consumer
```

Explain why abruptly killing consumers can cause unnecessary rebalances or duplicate processing.

---

# 14. CONSUMER GROUPS

This is the central concept.

Explain:

> A consumer group allows multiple consumer instances to cooperatively process partitions of a topic.

Example:

```text
Topic: orders
Partitions: 6

Consumer Group:
    Consumer 1
    Consumer 2
    Consumer 3
```

Show possible assignment:

```text
Consumer 1 → P0, P1
Consumer 2 → P2, P3
Consumer 3 → P4, P5
```

Explain that exact assignment depends on the partition assignment strategy and group state.

---

# 15. PARTITIONS AND CONSUMER PARALLELISM

Teach the critical rule:

> Within a consumer group, a partition is assigned to at most one consumer at a time.

Then explain:

```text
6 partitions
3 consumers
```

can provide up to approximately:

```text
6 / 3 = 2 partitions per consumer
```

for a balanced assignment.

Then:

```text
6 partitions
8 consumers
```

means:

```text
6 active partition-processing assignments
2 consumers without assigned partitions
```

Explain why partition count bounds consumer parallelism.

Do not overstate this as the only performance bottleneck.

---

# 16. ONE CONSUMER VS MANY CONSUMERS

Create a progression:

### One consumer

```text
P0 P1 P2 P3 P4 P5
 \  \  \  \  \  \
      Consumer
```

### Three consumers

```text
P0 P1 → Consumer A
P2 P3 → Consumer B
P4 P5 → Consumer C
```

### Eight consumers

Explain why some consumers may remain idle when there are only six partitions.

This directly connects the consumer model to the previous partition module.

---

# 17. MULTIPLE CONSUMER GROUPS

Explain:

```text
orders topic
       |
       +---- Group A → Analytics
       |
       +---- Group B → Fraud
       |
       +---- Group C → Warehouse
```

Each group gets its own logical consumption position.

Explain:

- Independent progress
- Independent replay
- Different processing speeds
- Different business purposes

This is a foundational Kafka architecture concept.

---

# 18. `auto.offset.reset`

Teach:

```text
auto.offset.reset
```

from first principles.

Cover:

- `earliest`
- `latest`

Explain when the setting is used.

Important:

Explain that it applies when there is no valid committed offset for the relevant partition, rather than simply meaning "always start from earliest/latest."

Use examples.

---

# 19. OFFSET MANAGEMENT

Teach the consumer's relationship with offsets.

Explain:

```text
Kafka partition
       |
       +---- offset 100
       +---- offset 101
       +---- offset 102
       +---- offset 103
```

Consumer processes:

```text
100
101
102
```

Then needs to record where it has successfully progressed.

Introduce committed offsets.

Explain:

> A committed offset represents the consumer group's durable progress position.

Keep the exact off-by-one semantics clear when showing commits. Explain whether the committed position represents the next record to read.

---

# 20. AUTOMATIC OFFSET COMMITS

Explain automatic commits conceptually.

Discuss:

- Convenience
- Reduced application code
- Risk of committing before processing finishes
- Potential message loss depending on processing/commit timing

Use:

```text
Consume
 ↓
Commit
 ↓
Process
```

and explain the danger.

Do not simply say automatic commits are "bad." Explain when they may be acceptable and what guarantees they do and do not provide.

---

# 21. MANUAL OFFSET COMMITS

Teach manual commit.

Show:

```python
consumer.commit()
```

and, where appropriate, per-message/per-partition commit APIs supported by the installed client.

Explain why manual commits provide more control.

The central pattern should be:

```text
Consume
   ↓
Process
   ↓
Successful sink write
   ↓
Commit offset
```

This is critical.

---

# 22. COMMIT AFTER PROCESSING

Teach the fundamental rule:

> If the application uses manual offset management, commit only after the record or batch has been successfully processed according to the application's correctness requirements.

Show:

```text
Kafka
  ↓
Consumer
  ↓
Process
  ↓
Write to sink
  ↓
Commit offset
```

Compare with:

```text
Kafka
  ↓
Consumer
  ↓
Commit
  ↓
Process
```

Explain why the second pattern can cause records to be skipped after a crash.

Do not yet label the whole system "exactly-once."

---

# 23. SYNCHRONOUS COMMITS

Teach synchronous commit conceptually.

Explain:

```python
consumer.commit(asynchronous=False)
```

where supported.

Discuss:

- Waiting for broker acknowledgement
- Simpler failure reasoning
- Higher latency
- Commit overhead

Explain when synchronous commits can be useful.

---

# 24. ASYNCHRONOUS COMMITS

Teach asynchronous commits conceptually.

Explain:

```python
consumer.commit(asynchronous=True)
```

where supported.

Discuss:

- Lower blocking
- Higher throughput potential
- More complicated failure handling
- Commit ordering concerns
- Shutdown/final commit considerations

Do not oversimplify asynchronous commits as "better."

---

# 25. COMMIT PER MESSAGE VS COMMIT PER BATCH

Compare:

### Commit every message

```text
Consume
Process
Commit
Consume
Process
Commit
```

versus:

### Commit per batch

```text
Consume batch
Process batch
Commit
```

Explain:

- Commit overhead
- Failure recovery
- Duplicate window
- Throughput
- Processing latency

Use a worked example.

---

# 26. REBALANCES

Teach rebalancing from first principles.

Explain:

> A rebalance occurs when Kafka needs to redistribute partitions among members of a consumer group.

Triggers can include:

- Consumer joins
- Consumer leaves
- Consumer crashes
- Subscription changes
- Partition-count changes
- Membership changes

Show:

```text
Before:

Consumer A → P0 P1
Consumer B → P2 P3
Consumer C → P4 P5

Consumer B crashes.

After rebalance:

Consumer A → P0 P1 P2
Consumer C → P3 P4 P5
```

Explain that exact assignment depends on the assignment strategy.

---

# 27. WHY REBALANCES MATTER

Explain the production impact.

During a rebalance:

- Partition ownership changes
- Processing may pause
- In-flight work must be handled carefully
- Offset commits matter
- External resources may need coordination

Explain why frequent rebalances can reduce throughput and increase latency.

---

# 28. EAGER REBALANCING

Explain eager rebalancing conceptually.

Show:

```text
All consumers
    ↓
Give up assignments
    ↓
Rebalance
    ↓
New assignments
```

Explain:

- Simplicity
- Stop-the-world behavior
- Processing interruption

Do not overstate exact protocol details beyond what the installed Kafka/client version supports.

---

# 29. COOPERATIVE / INCREMENTAL REBALANCING

Teach cooperative rebalancing.

Explain:

> Cooperative rebalancing aims to minimize unnecessary partition movement and processing disruption.

Conceptual flow:

```text
Existing assignment
       ↓
Move only necessary partitions
       ↓
Keep unaffected assignments
```

Explain benefits:

- Less disruption
- Better stability
- Reduced stop-the-world behavior

Clearly distinguish:

```text
Eager
vs
Cooperative/incremental
```

---

# 30. REBALANCE CALLBACKS

Teach callbacks.

Explain why an application may need to know when:

- Partitions are assigned
- Partitions are revoked
- Partitions are lost

Use the `confluent-kafka` callback APIs appropriate to the installed version.

Build an example consumer that logs:

```text
Assigned:
P0, P1

Revoked:
P1

Lost:
P2
```

Explain what application work belongs in these callbacks.

---

# 31. NEWER CONSUMER REBALANCE PROTOCOL AWARENESS

The roadmap explicitly requires awareness of newer Kafka consumer rebalance behavior.

Teach this at a conceptual level.

Explain that newer Kafka versions introduce modern consumer-group/rebalance protocol capabilities and that behavior depends on:

- Kafka broker version
- Client version
- Configuration
- Enabled protocol

Do not present outdated Kafka tutorials as universal truth.

Tell the learner to verify current Kafka 4.x / `confluent-kafka` documentation for the installed versions.

The goal is awareness, not deep protocol implementation.

---

# 32. SESSION TIMEOUT

Teach:

```text
session.timeout.ms
```

Explain:

> This relates to how long the group coordinator waits to consider a consumer member failed when heartbeats are no longer being received.

Explain failure scenarios:

```text
Consumer healthy
      ↓
Heartbeats
      ↓
Broker knows member is alive
```

versus:

```text
Consumer crashes
      ↓
Heartbeats stop
      ↓
Session timeout
      ↓
Consumer considered dead
      ↓
Rebalance
```

Discuss trade-offs.

---

# 33. MAX POLL INTERVAL

Teach:

```text
max.poll.interval.ms
```

Explain:

> It limits how long the application can go between successful calls to `poll()` before Kafka considers the consumer unable to keep up with its assigned work.

This is critical.

Show:

```text
poll()
  ↓
Long processing
  ↓
Long processing
  ↓
Long processing
  ↓
max.poll.interval.ms exceeded
  ↓
Consumer may leave group / rebalance
```

Explain why a consumer that processes large batches slowly can trigger rebalances even if the process itself is alive.

---

# 34. SESSION TIMEOUT VS MAX POLL INTERVAL

Create a detailed comparison:

| Setting | Main concern | Failure condition |
|---|---|---|
| `session.timeout.ms` | Consumer liveness/heartbeats | Heartbeats stop |
| `max.poll.interval.ms` | Application processing time between polls | Application takes too long between polls |

Explain this distinction thoroughly.

---

# 35. STATIC MEMBERSHIP

Teach static membership conceptually.

Explain:

> Static membership allows a consumer instance to retain a stable identity across restarts, reducing unnecessary group churn in appropriate scenarios.

Introduce:

```text
group.instance.id
```

Explain use cases:

- Long-running services
- Controlled restarts
- Stateful consumers
- Avoiding unnecessary rebalances

Discuss trade-offs and operational considerations.

---

# 36. BATCH PROCESSING

Teach batch-oriented consumption.

Show:

```text
Poll
 ↓
Receive batch
 ↓
Process batch
 ↓
Commit
```

Explain:

- Throughput
- Sink efficiency
- Commit frequency
- Processing latency
- Failure window

Use a database sink example.

---

# 37. SEEK AND REPLAY

Teach:

> Kafka consumers can reposition their read position and replay historical records.

Explain:

```text
Current position:
offset 500

Seek back:
offset 400

Replay:
400 → 401 → ... → 500
```

Discuss why replay is useful for:

- Bug recovery
- Backfills
- Reprocessing
- Testing
- Rebuilding downstream data

---

# 38. REPLAY BY OFFSET

Teach replay by specific partition/offset.

Explain:

```text
Partition 2
offset 100
```

and:

```python
consumer.seek(...)
```

Use the correct `confluent-kafka` APIs for the installed version.

Explain how to:

1. Identify partition
2. Identify offset
3. Assign/seek appropriately
4. Process records
5. Verify output

---

# 39. REPLAY BY TIMESTAMP

Teach timestamp-based replay.

Explain the use case:

> "Replay everything from 10:00 AM onward."

Show the conceptual flow:

```text
Timestamp
   ↓
Find partition offsets
   ↓
Seek
   ↓
Replay
```

Use the appropriate Kafka/Python APIs for looking up offsets by timestamp.

Build a practical experiment.

---

# 40. POISON PILLS

Explain a poison message.

Example:

```text
Record 100 → valid
Record 101 → malformed
Record 102 → valid
```

If the consumer cannot process record 101, repeatedly retrying it may block progress.

Explain:

- Malformed payload
- Invalid business data
- Unexpected schema
- Application bug
- Permanent failure vs transient failure

---

# 41. DEAD-LETTER QUEUE

Teach the DLQ pattern.

Architecture:

```text
Kafka
  ↓
Consumer
  ↓
Processing failure
  ↓
DLQ
```

Show:

```text
orders
   |
   +----> Consumer
              |
              +---- success → Sink
              |
              +---- failure → orders.DLQ
```

Explain what a DLQ record should contain conceptually:

- Original topic
- Original partition
- Original offset
- Key
- Value
- Error reason
- Error timestamp
- Consumer/application information

Do not silently discard failed records.

---

# 42. DLQ TRADE-OFFS

Explain:

- DLQ avoids blocking the main stream
- DLQ does not magically fix bad data
- DLQ requires operational ownership
- DLQ needs replay/reprocessing strategy
- DLQ itself requires retention and monitoring

Explain when to use:

```text
retry
vs
DLQ
vs
drop
```

Do not introduce a simplistic universal policy.

---

# 43. PAUSE / RESUME

Teach consumer flow control.

Explain:

```text
consumer.pause(...)
consumer.resume(...)
```

where supported.

Use cases:

- Slow sink
- Temporary downstream outage
- Controlled processing
- Backpressure
- Rate limiting

Example:

```text
Kafka
 ↓
Consumer
 ↓
Database overloaded
 ↓
Pause partitions
 ↓
Database recovers
 ↓
Resume
```

Keep detailed consumer-lag/backpressure metrics for File 13.

---

# 44. IDEMPOTENT SINKS

This is an important production concept.

Explain:

> A consumer can process the same Kafka record more than once, so the downstream sink should often tolerate repeated application of the same event.

Use event IDs.

Example:

```text
event_id = evt-123
```

Database table:

```text
event_id PRIMARY KEY
```

Then:

```text
evt-123 → INSERT
evt-123 → duplicate
```

The second attempt does not change the final result.

Explain:

```text
Kafka
 ↓
Consumer
 ↓
Idempotent sink
 ↓
Commit offset
```

This concept is foundational for later delivery-semantics learning.

---

# 45. POSTGRESQL IDEMPOTENT SINK

Build a practical PostgreSQL example.

Use a table such as:

```sql
CREATE TABLE processed_events (
    event_id TEXT PRIMARY KEY,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    payload JSONB NOT NULL
);
```

Then demonstrate an idempotent insert/upsert pattern.

Explain:

```text
Consume event
    ↓
Database transaction
    ↓
Write event using event_id
    ↓
Commit DB transaction
    ↓
Commit Kafka offset
```

Explain what happens if the process crashes:

### Case 1

DB commit succeeds.

Kafka offset commit fails.

→ Event is processed again.

→ Sink detects same `event_id`.

→ Final state remains correct.

This is an essential reliability pattern.

---

# 46. CONSUMER CRASH SCENARIO

Simulate:

```text
Consume record
     ↓
Process
     ↓
Write sink
     ↓
Consumer crashes BEFORE offset commit
```

Explain:

```text
Record will likely be consumed again.
```

Then show how an idempotent sink absorbs the duplicate.

Do not label this as exactly-once without the complete delivery-semantics analysis.

---

# 47. CONSUMER FAILURE RECOVERY

Create a detailed recovery model.

Explain:

```text
Healthy
  ↓
Consumer crashes
  ↓
Group detects failure
  ↓
Rebalance
  ↓
Another consumer receives partition
  ↓
Resume from committed position
  ↓
Potential duplicate processing
```

This should become a core mental model.

---

# 48. REBALANCE STORM

The roadmap explicitly requires a rebalance-storm experiment.

Explain:

> A rebalance storm occurs when consumers repeatedly join/leave or repeatedly fail to maintain group membership, causing frequent partition redistribution.

Demonstrate:

```text
Consumer joins
  ↓
Rebalance
  ↓
Consumer leaves
  ↓
Rebalance
  ↓
Consumer rejoins
  ↓
Rebalance
```

Discuss causes:

- Crashes
- Too-short timeouts
- Processing exceeding `max.poll.interval.ms`
- Container instability
- Deployment churn
- Network problems

Measure:

- Rebalance frequency
- Processing interruption
- Throughput impact

---

# 49. CONSUMER WITH SIX PARTITIONS

Create the required experiment:

```text
Topic:
orders

Partitions:
6
```

Run:

```text
1 consumer
```

Then:

```text
3 consumers
```

Then:

```text
6 consumers
```

Then:

```text
8 consumers
```

Document:

- Partition assignment
- Active consumers
- Idle consumers
- Throughput
- Rebalance behavior

Do not fabricate results.

Require the learner to inspect actual assignment.

---

# 50. CONSUMER ASSIGNMENT EXPERIMENT

Build a Python consumer that prints:

```text
Consumer instance
Group ID
Assigned partitions
Revoked partitions
```

Use rebalance callbacks.

The output should allow the learner to see group membership changes directly.

---

# 51. REBALANCE CALLBACK LAB

Implement:

- `on_assign`
- `on_revoke`
- `on_lost` where supported by the installed client

Explain:

- What each callback means
- What operations are safe
- Why offset management matters
- How callbacks help observability

Do not use APIs that the installed client does not support; verify against the actual version.

---

# 52. TIMESTAMP REPLAY LAB

Build a practical replay experiment:

1. Produce events with timestamps.
2. Consume normally.
3. Identify a time range.
4. Resolve offsets corresponding to that timestamp.
5. Seek to those offsets.
6. Replay.
7. Write replayed records to a separate sink.
8. Compare original and replayed results.

Explain every step.

---

# 53. DLQ LAB

Create malformed events intentionally.

Example:

```text
valid
valid
malformed
valid
invalid business record
valid
```

Consumer behavior:

```text
Valid → Process
Malformed → DLQ
Valid → Process
Invalid → DLQ
```

Verify:

- Main consumer continues
- Failed records are preserved
- DLQ contains useful metadata
- Records can be inspected/reprocessed

---

# 54. CONSUMER KILL/RESTART LAB

Start:

```text
6 partitions
3 consumers
```

Then kill one consumer.

Observe:

```text
Partition reassignment
```

Restart it.

Observe:

```text
Another rebalance
```

Document:

- Before
- During
- After
- Offsets
- Duplicates
- Recovery time

---

# 55. END-TO-END IDempotency LAB

Use:

```text
Kafka
 ↓
Python Consumer
 ↓
PostgreSQL
```

Produce duplicate events:

```text
evt-001
evt-002
evt-001
evt-003
evt-002
```

The database should end with one logical application of each event.

Use:

```text
event_id
```

as the idempotency key.

Verify:

```text
Input records = N
Unique event IDs = M
Final logical effects = M
```

---

# 56. FAILURE-DRIVEN LEARNING

Do not only demonstrate successful consumption.

Break the consumer deliberately.

Experiments should include:

- Consumer crash
- Broker interruption
- Long processing
- Rebalance
- Poison message
- Duplicate event
- Slow database
- Consumer restart

For every experiment document:

```text
Expected behavior
Observed behavior
Root cause
Recovery
Potential data loss
Potential duplicate processing
Production lesson
```

---

# 57. PRODUCTION CONSUMER ARCHITECTURE

Build a realistic architecture:

```text
                    Kafka
                      |
                      v
              Consumer Group
             /      |       \
            /       |        \
      Consumer 1 Consumer 2 Consumer 3
          |          |           |
          +----------+-----------+
                     |
              Processing Layer
                     |
          +----------+-----------+
          |                      |
          v                      v
    Idempotent DB             DLQ
```

Explain:

- Group membership
- Partition assignment
- Processing
- Sink
- Offset commit
- Failure
- DLQ

---

# 58. CONSUMER CONFIGURATION DESIGN

Create a production-oriented configuration table.

Cover:

- `bootstrap.servers`
- `group.id`
- `auto.offset.reset`
- `enable.auto.commit`
- `session.timeout.ms`
- `max.poll.interval.ms`
- `max.poll.records`
- Relevant heartbeat/rebalance configuration where appropriate
- Client logging/configuration

For each explain:

```text
Purpose
Default/typical behavior
When to change
Risk of wrong setting
```

Do not blindly recommend values.

---

# 59. TIMEOUT TUNING SCENARIO

Give a scenario:

```text
Each batch takes 90 seconds to process.
```

Ask:

> What happens if `max.poll.interval.ms` is only 60 seconds?

Then explain the likely group-membership consequences.

Then design a better approach.

Also explain that simply increasing the timeout may hide a processing bottleneck rather than solve it.

---

# 60. BATCH SIZE DESIGN

Give scenarios:

### Scenario A

Fast lightweight processing.

### Scenario B

Slow database batch writes.

### Scenario C

Expensive CPU transformation.

Explain how batch size affects:

- Processing time
- Poll frequency
- Commit frequency
- Memory
- Throughput
- Failure recovery

---

# 61. COMMON CONSUMER MISTAKES

Create a dedicated section.

Cover at least:

### Mistake 1
Committing before processing.

### Mistake 2
Assuming `poll()` means processing succeeded.

### Mistake 3
Ignoring consumer errors.

### Mistake 4
Not calling `close()`.

### Mistake 5
Using too many consumers for too few partitions.

### Mistake 6
Ignoring rebalances.

### Mistake 7
Setting `max.poll.interval.ms` without considering processing time.

### Mistake 8
Using automatic commits without understanding timing.

### Mistake 9
Ignoring duplicate processing.

### Mistake 10
No idempotent sink.

### Mistake 11
No DLQ strategy for poison messages.

### Mistake 12
Infinite retries on permanently bad records.

### Mistake 13
Ignoring timestamp/offset replay requirements.

### Mistake 14
Creating rebalance storms.

For each explain:

```text
Problem
Why it happens
Failure mode
Better approach
Production impact
```

---

# 62. ADVANCED CONSUMER MENTAL MODEL

Build this central model:

```text
Kafka Topic
     |
     v
Partitions
     |
     v
Consumer Group
     |
     +---- Consumer 1
     +---- Consumer 2
     +---- Consumer 3
     |
     v
Partition Assignment
     |
     v
poll()
     |
     v
Processing
     |
     v
Sink
     |
     v
Commit Offset
```

Then add failure:

```text
Consumer crashes
      |
      v
Group detects failure
      |
      v
Rebalance
      |
      v
Partition reassigned
      |
      v
Resume from committed offset
      |
      v
Potential duplicate processing
      |
      v
Idempotent sink absorbs duplicate
```

This should be the learner's primary mental model.

---

# 63. OBSERVABILITY AWARENESS

Keep detailed lag analysis for File 13, but introduce the consumer-level signals that should be visible:

- Consumer assignment
- Partition ownership
- Poll frequency
- Processing duration
- Commit failures
- Rebalances
- Consumer errors
- Records processed
- Processing throughput
- Duplicate detection
- DLQ volume

Explain why these signals are important.

---

# 64. VERSION AWARENESS

The canonical module uses:

```text
Apache Kafka 4.x
Python 3.12+
confluent-kafka
KRaft
```

Ensure all examples are version-aware.

Do not provide ZooKeeper-based consumer instructions.

For features involving newer consumer rebalance behavior, explicitly state that exact behavior depends on broker/client versions and configuration.

Use the installed library's actual API.

---

# 65. CODE QUALITY REQUIREMENTS

All Python examples must:

- Target Python 3.12+.
- Use `confluent-kafka`.
- Be syntactically correct.
- Be runnable where practical.
- Use meaningful names.
- Include appropriate exception handling.
- Demonstrate graceful shutdown.
- Avoid unnecessary abstractions.
- Explain the important lines.

When demonstrating a production concept, distinguish:

```text
Educational example
```

from:

```text
Production-oriented pattern
```

Do not present toy code as a complete enterprise framework.

---

# 66. DIAGRAM REQUIREMENTS

Use Mermaid diagrams throughout the module.

At minimum include diagrams for:

- Basic consumer
- Consumer group
- One consumer / six partitions
- Multiple consumers
- Multiple consumer groups
- Offset progression
- Commit-after-processing
- Rebalance
- Eager rebalance
- Cooperative rebalance
- Static membership
- Replay
- DLQ
- Pause/resume
- Idempotent sink
- Consumer crash/recovery

Every diagram must be followed by a plain-language explanation.

---

# 67. SIMPLICITY → DEPTH TEACHING METHOD

For every major concept, follow:

```text
Simple explanation
        ↓
Real-world analogy
        ↓
Technical definition
        ↓
Diagram
        ↓
Python example
        ↓
Failure scenario
        ↓
Production implication
```

Example:

Do not begin with:

> "A consumer group coordinator manages membership and partition assignment."

First explain:

> "A consumer group is a team of workers sharing the partitions of a Kafka topic."

Then progressively introduce:

- group coordinator
- membership
- partition assignment
- rebalance
- offsets

---

# 68. DO NOT WRITE SHALLOW CONTENT

Do not produce a dictionary of Kafka consumer configuration settings.

For every important concept explain:

```text
What is it?
Why does it exist?
How does it work?
What problem does it solve?
What can go wrong?
How do I observe it?
How do I recover?
What is the production trade-off?
```

The objective is to build operational understanding.

---

# 69. REQUIRED LEARNING LOOP

For every important concept use:

```text
Read
 ↓
Draw
 ↓
Predict
 ↓
Implement
 ↓
Run
 ↓
Inspect
 ↓
Break
 ↓
Recover
 ↓
Measure
 ↓
Explain
```

For consumer failures specifically:

```text
Predict
 ↓
Kill consumer
 ↓
Observe rebalance
 ↓
Inspect assignment
 ↓
Restart consumer
 ↓
Observe second rebalance
 ↓
Inspect offsets
 ↓
Check duplicates
 ↓
Verify sink correctness
```

---

# 70. REQUIRED FILE STRUCTURE

Organize the Markdown file approximately as:

```text
# Kafka Consumers and Consumer Groups

## Learning Objectives

## Prerequisites

## 1. What Is a Kafka Consumer?

## 2. Why Kafka Consumers Exist

## 3. Python Kafka Consumer with confluent-kafka

## 4. Consumer Configuration

## 5. group.id

## 6. subscribe()

## 7. poll()

## 8. Basic Consumer Loop

## 9. Consumer Record Metadata

## 10. Consumer Errors

## 11. close() and Graceful Shutdown

## 12. Consumer Groups

## 13. Partitions and Consumer Parallelism

## 14. Multiple Consumers

## 15. Multiple Consumer Groups

## 16. auto.offset.reset

## 17. Kafka Offset Management

## 18. Automatic Offset Commits

## 19. Manual Offset Commits

## 20. Commit After Processing

## 21. Synchronous Commits

## 22. Asynchronous Commits

## 23. Commit Per Message vs Commit Per Batch

## 24. Rebalances

## 25. Why Rebalances Matter

## 26. Eager Rebalancing

## 27. Cooperative Rebalancing

## 28. Rebalance Callbacks

## 29. Modern Kafka Consumer Rebalance Protocol Awareness

## 30. session.timeout.ms

## 31. max.poll.interval.ms

## 32. session.timeout.ms vs max.poll.interval.ms

## 33. Static Membership

## 34. Batch Processing

## 35. Seek and Replay

## 36. Replay by Offset

## 37. Replay by Timestamp

## 38. Poison Messages

## 39. Dead-Letter Queues

## 40. Pause and Resume

## 41. Idempotent Sinks

## 42. PostgreSQL Idempotent Sink

## 43. Consumer Crash and Recovery

## 44. Rebalance Storm Experiment

## 45. Six-Partition Consumer Group Lab

## 46. Rebalance Callback Lab

## 47. Timestamp Replay Lab

## 48. DLQ Lab

## 49. Consumer Kill/Restart Lab

## 50. End-to-End Idempotency Lab

## 51. Production Consumer Architecture

## 52. Consumer Configuration Design

## 53. Timeout Tuning

## 54. Batch Size Design

## 55. Observability Awareness

## 56. Common Mistakes

## 57. Advanced Consumer Mental Model

## 58. Knowledge Checkpoints

## 59. Practical Exercises

## 60. Interview Questions

## 61. Final Assessment

## 62. Final Mental Model

## 63. Summary
```

You may adjust ordering slightly for pedagogy, but **do not remove any required roadmap concept**.

---

# 71. KNOWLEDGE CHECKPOINTS

After each major section include meaningful checkpoints.

Examples:

### Checkpoint 1

What is the difference between:

```text
Consumer
Consumer Group
Partition
Offset
```

### Checkpoint 2

Why can eight consumers be connected to a six-partition topic while only six can actively process partitions at one time within that group?

### Checkpoint 3

Why is:

```text
Process → Commit
```

usually safer than:

```text
Commit → Process
```

for manual offset management?

### Checkpoint 4

What causes a rebalance?

### Checkpoint 5

What is the difference between:

```text
session.timeout.ms
```

and:

```text
max.poll.interval.ms
```

### Checkpoint 6

Why can a poison message block progress?

### Checkpoint 7

Why does an idempotent sink matter?

Each checkpoint should provide expected reasoning.

---

# 72. PRACTICAL EXERCISES

Create progressive exercises.

## Beginner

Build a consumer that prints records.

## Beginner+

Print:

- Topic
- Partition
- Offset
- Key
- Value

## Intermediate

Create a three-consumer group for a six-partition topic.

Observe partition assignment.

## Intermediate+

Change:

```text
1 consumer
3 consumers
6 consumers
8 consumers
```

Compare assignments.

## Advanced

Implement manual offset commits after successful processing.

## Advanced

Implement a PostgreSQL idempotent sink.

## Advanced

Build a DLQ flow.

## Advanced

Replay records by timestamp.

## Expert

Diagnose a rebalance storm caused by slow processing.

## Expert Architecture Exercise

Design a consumer group for:

```text
6 partitions
3 consumer instances
PostgreSQL sink
5-second processing time per batch
```

Explain:

- Poll strategy
- Batch size
- Commit strategy
- Timeout configuration
- Idempotency
- Failure recovery

---

# 73. INTERVIEW QUESTIONS

Include detailed model answers for:

1. What is a Kafka consumer?
2. What is a consumer group?
3. Why do consumer groups exist?
4. How are partitions assigned to consumers?
5. What happens when there are more consumers than partitions?
6. Can multiple consumer groups consume the same topic?
7. What is `group.id`?
8. What does `poll()` do?
9. What does `auto.offset.reset` mean?
10. What is a committed offset?
11. Why commit after processing?
12. Automatic vs manual commits?
13. Synchronous vs asynchronous commits?
14. What is a rebalance?
15. What causes rebalances?
16. Eager vs cooperative rebalancing?
17. What are rebalance callbacks?
18. What is `session.timeout.ms`?
19. What is `max.poll.interval.ms`?
20. What is static membership?
21. How does Kafka replay work?
22. What is a poison message?
23. What is a DLQ?
24. Why use pause/resume?
25. Why are idempotent sinks important?
26. How would you handle duplicate events?
27. What happens when a consumer crashes?
28. How would you troubleshoot a rebalance storm?
29. How would you design a six-partition consumer group?
30. How would you design a reliable PostgreSQL Kafka consumer?

For system-design questions require:

```text
Requirements
→ Consumer-group design
→ Partition strategy
→ Processing model
→ Offset strategy
→ Failure strategy
→ Idempotency
→ Recovery
→ Trade-offs
```

---

# 74. FINAL ASSESSMENT

Create a comprehensive scenario-based assessment.

## Level 1 — Fundamentals

Test:

- Consumer
- Consumer group
- Partition
- Offset
- `poll()`

## Level 2 — Offset Management

Test:

- Automatic commits
- Manual commits
- Commit-after-processing
- Batch commits
- Replay

## Level 3 — Group Operations

Test:

- Assignment
- Rebalances
- Eager vs cooperative
- Static membership
- Timeouts

## Level 4 — Failure Handling

Test:

- Consumer crash
- Poison message
- DLQ
- Duplicate processing
- Idempotent sink
- Recovery

## Level 5 — Production Design

Design a complete:

```text
Kafka
 ↓
Consumer Group
 ↓
Python Consumers
 ↓
PostgreSQL
 ↓
DLQ
```

architecture.

Require the learner to justify:

```text
Group size
Batch size
Commit strategy
Timeouts
Idempotency
DLQ strategy
Replay strategy
Failure recovery
```

---

# 75. FINAL MENTAL MODEL

End the module with:

```text
Kafka Topic
     |
     +---- Partition 0
     +---- Partition 1
     +---- Partition 2
     +---- Partition 3
     +---- Partition 4
     +---- Partition 5
              |
              v
       Consumer Group
              |
       +------+------+
       |      |      |
       v      v      v
      C1     C2     C3
       |      |      |
       +------+------+
              |
              v
          Processing
              |
              v
        Idempotent Sink
              |
              v
        Commit Offset
```

Then show failure:

```text
Consumer crashes
      |
      v
Group detects failure
      |
      v
Rebalance
      |
      v
Partition reassigned
      |
      v
Resume from committed offset
      |
      v
Possible duplicate processing
      |
      v
Idempotent sink
      |
      v
Correct final state
```

The learner should understand:

```text
Consumer
= reads Kafka records

Consumer Group
= distributes partitions across cooperating consumers

Partition
= unit of ordered work assignment

Offset
= consumer's position

Commit
= durable progress marker

Rebalance
= redistribution of partitions

Replay
= move the consumer position backward

DLQ
= isolate records that cannot currently be processed

Pause/Resume
= control consumption

Idempotent Sink
= safely absorb repeated processing
```

---

# 76. FINAL QUALITY CHECK

Before completing the file, verify all of the following.

## Consumer Fundamentals

- [ ] Kafka consumer
- [ ] Producer vs consumer
- [ ] Consumer configuration
- [ ] `group.id`
- [ ] `subscribe()`
- [ ] `poll()`
- [ ] Consumer errors
- [ ] `close()`

## Consumer Groups

- [ ] Consumer groups
- [ ] Partition assignment
- [ ] Parallelism
- [ ] More consumers than partitions
- [ ] Multiple consumer groups

## Offsets

- [ ] `auto.offset.reset`
- [ ] Committed offsets
- [ ] Automatic commits
- [ ] Manual commits
- [ ] Commit after processing
- [ ] Sync commits
- [ ] Async commits
- [ ] Per-message commits
- [ ] Per-batch commits

## Rebalancing

- [ ] Rebalances
- [ ] Rebalance triggers
- [ ] Eager rebalancing
- [ ] Cooperative/incremental rebalancing
- [ ] Rebalance callbacks
- [ ] Modern protocol awareness
- [ ] `session.timeout.ms`
- [ ] `max.poll.interval.ms`
- [ ] Static membership

## Replay

- [ ] Seek
- [ ] Offset replay
- [ ] Timestamp replay

## Failure Handling

- [ ] Poison messages
- [ ] DLQ
- [ ] Pause/resume
- [ ] Consumer crash
- [ ] Recovery
- [ ] Duplicate processing
- [ ] Idempotent sink
- [ ] PostgreSQL example

## Labs

- [ ] 6-partition topic
- [ ] 1 consumer
- [ ] 3 consumers
- [ ] 6 consumers
- [ ] 8 consumers
- [ ] Rebalance storm
- [ ] Rebalance callbacks
- [ ] DLQ
- [ ] Timestamp replay
- [ ] Consumer kill/restart
- [ ] PostgreSQL idempotency
- [ ] Duplicate absorption
- [ ] No event loss verification

## Teaching Quality

- [ ] Basic → advanced
- [ ] Simple explanations
- [ ] Technical depth
- [ ] Python examples
- [ ] Kafka CLI where appropriate
- [ ] Mermaid diagrams
- [ ] Failure scenarios
- [ ] Production trade-offs
- [ ] Knowledge checkpoints
- [ ] Exercises
- [ ] Interview questions
- [ ] Final assessment
- [ ] Final mental model

## Scope

- [ ] Only `04-kafka-consumers-and-consumer-groups.md` modified
- [ ] No other file modified
- [ ] No unrelated concepts added
- [ ] Delivery semantics not unnecessarily duplicated
- [ ] Schema Registry not unnecessarily duplicated
- [ ] Stream processing engines not unnecessarily duplicated
- [ ] Consumer lag module not unnecessarily duplicated

---

# 77. FINAL INSTRUCTION TO CLAUDE CODE

Do not treat this as a short Kafka reference document.

Build a **complete professional learning module**.

By the end of the module, I should be able to:

1. Explain how Kafka consumers work.
2. Build a Python Kafka consumer using `confluent-kafka`.
3. Configure `group.id`.
4. Subscribe to topics.
5. Poll records safely.
6. Handle consumer errors.
7. Shut consumers down gracefully.
8. Explain consumer groups.
9. Explain partition assignment.
10. Reason about consumer parallelism.
11. Understand why six partitions cannot provide more than six active partition assignments within one consumer group at a time.
12. Explain multiple consumer groups.
13. Understand `auto.offset.reset`.
14. Understand committed offsets.
15. Use automatic and manual offset commits appropriately.
16. Commit after successful processing.
17. Understand synchronous and asynchronous commits.
18. Understand eager and cooperative rebalancing.
19. Implement rebalance callbacks.
20. Understand modern Kafka consumer rebalance protocol awareness.
21. Configure and reason about `session.timeout.ms`.
22. Configure and reason about `max.poll.interval.ms`.
23. Understand static membership.
24. Replay records by offset.
25. Replay records by timestamp.
26. Handle poison messages.
27. Build a DLQ strategy.
28. Use pause/resume for controlled consumption.
29. Build an idempotent PostgreSQL sink.
30. Handle consumer crashes.
31. Diagnose rebalances.
32. Diagnose rebalance storms.
33. Verify duplicate processing behavior.
34. Operate a six-partition consumer group.
35. Explain consumer behavior in a senior Data Engineering interview.
36. Design a production-grade Python Kafka consumer architecture.

The central engineering principle should be:

> **A Kafka consumer is not simply a loop that calls `poll()`. A production consumer must deliberately manage partition ownership, processing time, offsets, rebalances, failures, replay, poison records, downstream idempotency, and graceful shutdown.**

The central mental model should be:

```text
Kafka Partition
      ↓
Consumer Group
      ↓
Partition Assignment
      ↓
poll()
      ↓
Process
      ↓
Reliable Sink
      ↓
Commit Offset
      ↓
Continue
```

And when something fails:

```text
Failure
  ↓
Rebalance / Replay
  ↓
Resume from committed position
  ↓
Possible duplicate
  ↓
Idempotent processing
  ↓
Correct final state
```

Use the canonical Module 2.16 roadmap as the source of truth.

**Modify ONLY:**

```text
16-Streaming-and-Event-Driven-Data/04-kafka-consumers-and-consumer-groups.md
```

Do not modify any other file.