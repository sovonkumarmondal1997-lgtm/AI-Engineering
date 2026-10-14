# Claude Code Prompt — Teach `05-delivery-semantics-at-most-at-least-and-exactly-once.md`

You are a **Senior Data Engineer with 10+ years of production experience** designing and operating distributed data platforms, Kafka-based streaming systems, CDC pipelines, lakehouses, and fault-tolerant data pipelines.

I am learning the **Stage 2 — Python for Data Engineering** curriculum.

We are currently working in:

```text
16-Streaming-and-Event-Driven-Data/
```

The **authoritative roadmap** for this module is the project's roadmap for:

```text
16-Streaming-and-Event-Driven-Data/
```

The current file is:

```text
05-delivery-semantics-at-most-at-least-and-exactly-once.md
```

Your task is to create a **complete, production-grade learning lesson** for this file.

---

# 1. STRICT SCOPE

You must teach **only the concepts relevant to delivery semantics** specified by the roadmap for this file.

Do **not** change, rewrite, create, delete, rename, or update any other file in:

```text
16-Streaming-and-Event-Driven-Data/
```

The only file you are allowed to create or modify is:

```text
16-Streaming-and-Event-Driven-Data/05-delivery-semantics-at-most-at-least-and-exactly-once.md
```

Do not modify:

- README.md
- 01-event-streams-vs-message-queues.md
- 02-kafka-topics-partitions-offsets-and-replication.md
- 03-kafka-producers-in-python.md
- 04-kafka-consumers-and-consumer-groups.md
- 06-protobuf-and-schema-registry.md
- 07-event-time-processing-and-watermarks.md
- 08-tumbling-sliding-and-session-windows.md
- 09-stateful-stream-processing.md
- 10-spark-structured-streaming.md
- 11-apache-flink-and-pyflink-overview.md
- 12-debezium-cdc-streams-into-kafka.md
- 13-backpressure-and-consumer-lag.md
- practice-questions.md
- interview-practice.md

Do not update the project tree or roadmap.

---

# 2. PRIMARY LEARNING OBJECTIVE

Build my understanding of:

> **At-most-once, at-least-once, and exactly-once delivery semantics**

from absolute fundamentals to advanced production-grade reasoning.

Do not assume that I already understand distributed systems.

Start with the simplest possible mental model and progressively introduce:

```text
message delivery
      ↓
processing
      ↓
acknowledgement
      ↓
offset management
      ↓
failure
      ↓
retry
      ↓
duplicate/lost records
      ↓
delivery semantics
      ↓
idempotent processing
      ↓
Kafka transactions
      ↓
exactly-once processing
      ↓
external systems
      ↓
end-to-end correctness
      ↓
failure testing
```

The lesson must make me capable of reasoning about **what happens to a record when a distributed streaming system fails at every possible point in the processing lifecycle**.

---

# 3. IMPORTANT TEACHING PRINCIPLE

Teach this topic using a simple recurring scenario.

Use an example such as:

```text
Kafka
  ↓
Consumer
  ↓
Transform
  ↓
Database
```

Suppose Kafka contains:

```text
order_id = 101
amount = 500
```

Walk through what happens when:

1. the consumer receives the event
2. processing succeeds
3. the database write succeeds
4. the consumer commits its offset
5. the consumer crashes
6. the database write succeeds but the consumer crashes before committing
7. the consumer commits before processing
8. the processing fails
9. the message is retried
10. the same message is processed again

Use this scenario repeatedly to make the semantics intuitive.

---

# 4. START WITH THE FUNDAMENTALS

Begin by explaining:

## 4.1 What does "delivery" mean?

Explain in simple language:

- What is a message?
- What does it mean to deliver a message?
- What does it mean to process a message?
- What is an acknowledgement?
- What is an offset?
- Why does a streaming system need to know what has been processed?
- Why can failures happen between processing and acknowledgement?

Clearly distinguish:

```text
message received
message processed
side effect completed
offset acknowledged/committed
```

Do not treat these as the same operation.

---

# 5. FAILURE WINDOWS

Teach the fundamental failure windows.

Show the lifecycle:

```text
READ
 ↓
PROCESS
 ↓
WRITE SIDE EFFECT
 ↓
COMMIT OFFSET
```

Then explain what happens if a crash occurs:

### Failure A

```text
READ
 ↓
CRASH
```

### Failure B

```text
READ
 ↓
PROCESS
 ↓
CRASH
```

### Failure C

```text
READ
 ↓
PROCESS
 ↓
WRITE DATABASE
 ↓
CRASH
 ↓
OFFSET NOT COMMITTED
```

### Failure D

```text
READ
 ↓
COMMIT OFFSET
 ↓
CRASH
 ↓
DATABASE WRITE NEVER HAPPENED
```

Explain exactly why these failures lead to:

- loss
- duplication
- retry
- reprocessing

This section should establish the foundation for all three delivery semantics.

---

# 6. AT-MOST-ONCE

Teach **at-most-once delivery** from first principles.

Explain:

> The system processes each message zero or one time, but a message can be lost.

Show the conceptual flow:

```text
READ
 ↓
COMMIT OFFSET
 ↓
PROCESS
```

Explain why this ordering creates the possibility of data loss.

Use a concrete example.

Example:

```text
Kafka:
order-101

Consumer:
commit offset 101

Consumer:
crashes before processing

Result:
order-101 is never processed
```

Explain:

- why the record is lost from the consumer's point of view
- why there are no duplicates caused by retry in this model
- when at-most-once might be acceptable
- when it is dangerous
- trade-off between correctness and latency/complexity

Include a Python/Kafka-style example showing the conceptual implementation.

Make the code clear and educational rather than unnecessarily large.

---

# 7. AT-LEAST-ONCE

Teach **at-least-once delivery** from first principles.

Explain:

> The system retries until the message is considered processed, so messages are not intentionally lost, but duplicates can occur.

Show:

```text
READ
 ↓
PROCESS
 ↓
COMMIT OFFSET
```

Then demonstrate:

```text
READ
 ↓
PROCESS
 ↓
DATABASE WRITE SUCCESS
 ↓
CRASH
 ↓
OFFSET NOT COMMITTED
 ↓
MESSAGE RETRIED
 ↓
DATABASE WRITE AGAIN
```

Explain why this produces duplicates.

Use a concrete order example:

```text
order_id = 101
```

First execution:

```text
INSERT order 101
```

Crash before offset commit.

Second execution:

```text
INSERT order 101
```

Explain why naive processing can create:

```text
order 101
order 101
```

and how an idempotent sink changes the result.

---

# 8. IDEMPOTENCY

This is a critical part of the lesson.

Explain **idempotency** very carefully.

Define:

> An operation is idempotent if performing it multiple times produces the same final effect as performing it once.

Use simple mathematical and data-engineering examples.

For example:

```text
SET balance = 100
```

versus:

```text
balance = balance + 100
```

Explain why these behave differently under retries.

Then show:

### Non-idempotent

```sql
INSERT INTO payments (...)
VALUES (...);
```

### Idempotent approaches

For example:

```sql
INSERT ... ON CONFLICT DO NOTHING
```

or:

```sql
INSERT ... ON CONFLICT (...) DO UPDATE
```

or a processed-event table:

```text
processed_events
----------------
event_id
processed_at
```

Explain how an event ID can be used as an idempotency key.

---

# 9. AT-LEAST-ONCE + IDEMPOTENT PROCESSING

Teach the key practical principle from the roadmap:

> **At-least-once delivery + idempotent processing = exactly-once effect**

Explain this carefully.

Do NOT incorrectly teach:

```text
at-least-once = exactly-once
```

Instead explain:

```text
Delivery semantics
        +
Processing semantics
        +
Sink semantics
        =
End-to-end behavior
```

Show a complete example:

```text
Kafka
 ↓
Consumer
 ↓
Process event
 ↓
UPSERT using event_id
 ↓
Commit offset
```

If the consumer crashes after the UPSERT but before the offset commit:

```text
event is replayed
       ↓
UPSERT executes again
       ↓
same final state
```

Explain why the duplicate delivery does not create a duplicate business effect.

---

# 10. EXACTLY-ONCE

Now introduce **exactly-once semantics**.

Explain the difference between:

### Exactly-once delivery

and

### Exactly-once processing

and

### Exactly-once effect

and

### End-to-end exactly-once semantics

These concepts must not be conflated.

Explain that exactly-once is not simply:

```text
"Kafka will never send the same message twice."
```

Instead, explain the complete system boundary.

Use:

```text
Source
 ↓
Consumer
 ↓
Processing
 ↓
Sink
```

and identify where exactly-once must hold.

---

# 11. KAFKA EXACTLY-ONCE

Teach Kafka's transactional mechanism.

Explain the role of:

```text
transactional.id
```

Explain:

- producer transactions
- atomic writes
- transaction boundaries
- transactional offsets
- consuming records
- transforming them
- producing results
- committing offsets as part of the transaction

Teach the conceptual flow:

```text
Consume
   ↓
Transform
   ↓
Begin transaction
   ↓
Produce output
   ↓
Commit consumed offsets transactionally
   ↓
Commit transaction
```

Explain why the transaction ties:

```text
output records
+
input offsets
```

together.

---

# 12. `read_committed`

Explain Kafka isolation levels.

Teach:

```text
read_uncommitted
read_committed
```

Explain:

- what uncommitted transactional records mean
- why downstream consumers may need `read_committed`
- how aborted transactions are handled
- why transactional producers alone are insufficient if consumers do not use the appropriate isolation level

Include a concise configuration example.

---

# 13. PYTHON KAFKA TRANSACTION EXAMPLE

Provide a practical Python example using the roadmap's Kafka Python ecosystem:

```text
confluent-kafka
```

Show a simplified consume-transform-produce transactional pattern.

The example should demonstrate the concepts rather than hide everything behind abstractions.

Include configuration concepts such as:

```python
transactional.id
enable.auto.commit = False
isolation.level = "read_committed"
```

Show the conceptual use of:

```python
init_transactions()
begin_transaction()
produce()
send_offsets_to_transaction()
commit_transaction()
abort_transaction()
```

Explain every important line.

Clearly explain what happens during:

```text
commit
```

and:

```text
abort
```

---

# 14. TRANSACTION FAILURE SCENARIOS

Do not only show the happy path.

Show what happens if the application crashes:

### Before transaction begins

### During processing

### After output is produced

### Before transaction commit

### During transaction commit

### After transaction commit

For every scenario explain:

```text
What exists?
What does not exist?
What will be retried?
What will the consumer see?
Can duplicate effects occur?
```

Use tables where useful.

---

# 15. IDEMPOTENT PRODUCER VS EXACTLY-ONCE

This distinction is mandatory.

Explain:

```text
idempotent producer
```

versus:

```text
transactional producer
```

versus:

```text
exactly-once processing
```

versus:

```text
exactly-once end-to-end effect
```

Explicitly explain:

> An idempotent Kafka producer does NOT automatically make an entire data pipeline exactly-once.

Show the boundaries.

For example:

```text
Python Producer
      ↓
Kafka
      ↓
Consumer
      ↓
PostgreSQL
```

Explain what Kafka can guarantee and what PostgreSQL must guarantee separately.

---

# 16. EXTERNAL SYSTEMS

Teach why exactly-once becomes harder when the sink is outside Kafka.

Examples:

```text
Kafka → PostgreSQL
Kafka → REST API
Kafka → Email
Kafka → Object Storage
Kafka → Lakehouse
```

Explain why Kafka transactions cannot automatically make an arbitrary external side effect exactly-once.

Use a REST API example:

```text
Kafka event
 ↓
POST /payment
 ↓
API succeeds
 ↓
consumer crashes
 ↓
offset not committed
 ↓
API called again
```

Explain why this can create a duplicate external effect.

Then show how idempotency keys can help:

```text
Idempotency-Key: payment-event-123
```

Explain the principle without moving into unrelated API design.

---

# 17. TRANSACTIONAL SINKS

Explain the roadmap concept of:

> transactional sinks

Show the idea of making:

```text
business result
+
consumer progress
```

part of the same atomic transaction when the technology permits it.

Use PostgreSQL as the educational example.

Demonstrate a conceptual pattern:

```text
BEGIN;

INSERT/UPSERT business result;

INSERT processed_event(event_id);

COMMIT;
```

Explain why this can provide a powerful exactly-once effect.

Then explain the boundary:

```text
Database transaction
        ≠
Kafka transaction
```

and when combining them requires careful architecture.

---

# 18. OFFSETS + RESULTS IN THE SAME DATABASE TRANSACTION

Teach the advanced pattern from the roadmap:

```text
offset
+
result
```

stored atomically in the same database transaction.

Use a simplified schema such as:

```sql
CREATE TABLE processed_events (
    event_id TEXT PRIMARY KEY,
    processed_at TIMESTAMP NOT NULL
);
```

and an example business table.

Explain:

1. begin DB transaction
2. process event
3. write result
4. record event ID / progress
5. commit DB transaction
6. only then consider the Kafka offset safely processed

Explain what happens if the DB transaction rolls back.

---

# 19. SPARK STRUCTURED STREAMING

Teach the roadmap's Spark perspective.

Explain how Spark Structured Streaming approaches reliability using:

- checkpoints
- replayable sources
- state
- idempotent sinks
- `foreachBatch`

Explain that exactly-once behavior depends on the complete source-processing-sink design.

Show a conceptual example involving:

```text
Kafka
 ↓
Spark Structured Streaming
 ↓
foreachBatch
 ↓
MERGE into Delta/Iceberg or another supported sink
```

Explain:

- checkpoint role
- replay
- batch IDs
- idempotent writes
- why a checkpoint is not the same thing as a business transaction
- why sink design still matters

Do not expand into the full Spark Structured Streaming module; only teach what is necessary to understand delivery semantics.

---

# 20. FLINK PERSPECTIVE

Briefly explain the roadmap's Flink perspective.

Cover:

- checkpoints
- state recovery
- exactly-once processing
- two-phase commit sinks

Explain conceptually how Flink can coordinate:

```text
checkpoint
+
state
+
sink commit
```

for stronger exactly-once guarantees.

Do not turn this into a full Flink lesson. Keep the explanation focused on delivery semantics.

---

# 21. SIDE EFFECTS THAT CANNOT BE NAIVELY EXACTLY-ONCE

Teach why side effects such as:

```text
send email
send SMS
call payment API
call external HTTP service
publish notification
```

cannot simply be declared exactly-once.

Show:

```text
process event
 ↓
send email
 ↓
email succeeds
 ↓
consumer crashes
 ↓
event replayed
 ↓
email sent again
```

Explain why retry safety requires:

- idempotency keys
- deduplication
- downstream idempotency
- durable operation identifiers

Keep this within the delivery-semantics scope.

---

# 22. PRACTICAL SEMANTICS COMPARISON

Create a clear comparison table:

| Semantic | Possible loss? | Possible duplicates? | Typical mechanism | Complexity |
|---|---|---|---|---|
| At-most-once | Yes | Generally no retry duplicates | Commit before processing | Low |
| At-least-once | No intentional loss | Yes | Process then commit | Medium |
| Exactly-once | Requires coordinated design | Hidden/controlled | Transactions/checkpoints/idempotency | High |

Then explain why this table is a simplification and why **end-to-end architecture determines actual correctness**.

---

# 23. END-TO-END DELIVERY GUARANTEE

Teach the following mental model:

```text
SOURCE
  ↓
TRANSPORT
  ↓
CONSUMER
  ↓
PROCESSING
  ↓
STATE
  ↓
SINK
  ↓
EXTERNAL SIDE EFFECT
```

For each layer ask:

```text
Can it lose data?
Can it duplicate data?
Can it replay data?
How is progress recorded?
How is failure recovered?
Is the operation idempotent?
Is there a transaction boundary?
```

Teach me to reason about the **weakest link** in an end-to-end guarantee.

---

# 24. FAILURE MATRIX

Create a detailed failure matrix.

At minimum include:

| Failure point | At-most-once | At-least-once | Exactly-once design |
|---|---|---|---|
| Crash before processing | possible loss | retry | recover/replay |
| Crash after processing | possible loss depending on commit | possible duplicate | coordinated transaction/recovery |
| Crash after sink write | potentially lost progress | duplicate delivery | transactional/idempotent sink |
| Crash before offset commit | loss possible | replay | transaction/recovery |
| External API succeeds then crash | external effect exists | duplicate possible | requires idempotent external operation |

Expand the table where useful.

---

# 25. CODING LABS

Create practical labs in increasing difficulty.

## Lab 1 — At-Most-Once

Build:

```text
Kafka → Python Consumer
```

Commit before processing.

Intentionally crash the consumer.

Observe lost records.

---

## Lab 2 — At-Least-Once

Build:

```text
Kafka → Python Consumer → PostgreSQL
```

Process first and commit afterward.

Crash after the DB write but before the Kafka offset commit.

Observe duplicate processing.

---

## Lab 3 — Idempotent Sink

Modify Lab 2 so that PostgreSQL uses:

```text
event_id
```

as the idempotency key.

Replay the same Kafka event multiple times.

Verify that the final business result is unchanged.

---

## Lab 4 — Processed Events Table

Create:

```sql
processed_events
```

and implement deduplication.

Test:

```text
same event 1 time
same event 2 times
same event 10 times
```

Verify one business effect.

---

## Lab 5 — Kafka Transactions

Build:

```text
Kafka input
    ↓
Python transactional consumer
    ↓
transform
    ↓
Kafka output
```

Use Kafka transactions.

Demonstrate:

```text
commit
abort
crash
retry
```

Use:

```text
read_committed
```

for the downstream consumer.

---

## Lab 6 — Transactional Failure Injection

Add deliberate failures at:

```text
before processing
after processing
after output produce
before transaction commit
after transaction commit
```

Record the observed behavior.

---

## Lab 7 — External API Idempotency

Simulate:

```text
Kafka → Python Consumer → HTTP service
```

Make the HTTP service support:

```text
Idempotency-Key
```

Crash the consumer after the API succeeds.

Replay the event.

Verify that the external service produces only one business effect.

---

## Lab 8 — Chaos Test

Create a small end-to-end pipeline and randomly kill/restart the consumer.

Measure:

```text
input events
processed events
duplicate deliveries
duplicate business effects
lost events
```

Compare the final result against a deterministic batch computation.

---

# 26. CHAOS TESTING

Make failure testing a first-class learning objective.

Introduce failures such as:

```text
consumer crash
network interruption
database failure
Kafka broker interruption
transaction abort
slow sink
process restart
```

For every test, record:

```text
event_id
attempt_number
processing_time
offset
transaction status
sink result
```

Teach me how to distinguish:

```text
duplicate delivery
```

from:

```text
duplicate business effect
```

This distinction is critical.

---

# 27. OBSERVABILITY FOR DELIVERY SEMANTICS

Teach what should be measured.

Include metrics/logs such as:

```text
records consumed
records processed
processing retries
duplicate events
deduplicated events
transaction commits
transaction aborts
consumer restarts
processing failures
sink failures
```

Explain how these metrics help identify whether a pipeline is actually behaving according to its intended delivery guarantee.

Do not turn this into the separate observability module.

---

# 28. COMMON MISCONCEPTIONS

Include a section called:

```text
Common Misconceptions
```

Correct at least these:

### Misconception 1

> Exactly-once means a message is physically delivered only once.

### Misconception 2

> Kafka automatically guarantees exactly-once for every sink.

### Misconception 3

> `enable.idempotence=true` means the whole pipeline is exactly-once.

### Misconception 4

> At-least-once is bad because duplicates happen.

### Misconception 5

> Exactly-once means retries never happen.

### Misconception 6

> Database UPSERT automatically solves every exactly-once problem.

### Misconception 7

> A Kafka transaction makes external HTTP calls exactly-once.

### Misconception 8

> Checkpoints alone guarantee business-level exactly-once correctness.

Explain each correction clearly.

---

# 29. PRODUCTION ARCHITECTURE EXAMPLES

Show several architectures.

## Architecture A

```text
Kafka
 ↓
Consumer
 ↓
Non-idempotent database
```

Explain why duplicates are dangerous.

## Architecture B

```text
Kafka
 ↓
Consumer
 ↓
Idempotent UPSERT
```

Explain the practical at-least-once + idempotent-effect model.

## Architecture C

```text
Kafka
 ↓
Transactional Consumer
 ↓
Kafka
```

Explain Kafka-to-Kafka exactly-once processing.

## Architecture D

```text
Kafka
 ↓
Spark Structured Streaming
 ↓
Checkpoint
 ↓
Idempotent MERGE sink
```

## Architecture E

```text
Kafka
 ↓
Flink
 ↓
Checkpoint
 ↓
Two-phase-commit sink
```

For each architecture explain:

- guarantee
- failure behavior
- complexity
- operational cost
- appropriate use case

---

# 30. DECISION FRAMEWORK

Create a practical decision framework.

Teach me how to decide between:

```text
At-most-once
At-least-once
At-least-once + idempotent sink
Kafka transactions
Spark checkpoint + idempotent sink
Flink checkpoint + transactional sink
```

Base the decision on:

- business correctness
- data loss tolerance
- duplicate tolerance
- latency requirements
- external side effects
- transaction support
- operational complexity
- cost
- replayability
- sink capabilities

---

# 31. ADVANCED DISTRIBUTED-SYSTEMS MENTAL MODEL

End the technical teaching with a strong mental model:

```text
Delivery guarantee
        ↓
Processing guarantee
        ↓
State guarantee
        ↓
Sink guarantee
        ↓
External side-effect guarantee
        ↓
End-to-end business guarantee
```

Explain why:

> The strongest guarantee of one component does not automatically become the strongest guarantee of the whole pipeline.

Teach me to ask:

1. Where can the system fail?
2. Where is progress recorded?
3. Can the event be replayed?
4. Can the operation be repeated safely?
5. What happens after a crash?
6. What transaction boundary exists?
7. What happens at the external sink?
8. What is the actual business-level guarantee?

---

# 32. CODE QUALITY REQUIREMENTS

All Python examples must:

- target Python 3.12+
- use clear type hints where helpful
- use meaningful variable names
- include error handling where appropriate
- include logging where useful
- demonstrate graceful shutdown where relevant
- avoid unnecessary abstractions
- explain configuration values
- be runnable or clearly state required infrastructure
- avoid pseudo-code when a realistic implementation can be shown

For Kafka examples use the module's intended ecosystem:

```text
confluent-kafka
```

For database examples PostgreSQL is preferred.

Use Docker Compose assumptions only where infrastructure is required.

---

# 33. TEACHING STYLE

Teach progressively:

```text
Level 1 — Beginner intuition
Level 2 — Core concepts
Level 3 — Kafka mechanics
Level 4 — Python implementation
Level 5 — Failure scenarios
Level 6 — Idempotency
Level 7 — Transactions
Level 8 — External systems
Level 9 — Spark/Flink
Level 10 — Production architecture
Level 11 — Chaos testing
Level 12 — Senior-level reasoning
```

For every major concept use:

```text
Simple explanation
        ↓
Real-world analogy
        ↓
Technical explanation
        ↓
Diagram
        ↓
Python/code example
        ↓
Failure scenario
        ↓
Production implication
        ↓
Knowledge-check question
```

Do not rush into advanced Kafka terminology before establishing the underlying idea.

---

# 34. KNOWLEDGE CHECKPOINTS

After each major section, include short questions.

Examples:

```text
Why can at-least-once create duplicates?

Why can at-most-once lose records?

Why is commit-before-processing dangerous?

Why is commit-after-processing safer for loss but vulnerable to duplicates?

What makes an operation idempotent?

Why is an idempotent producer not enough for end-to-end exactly-once?

Why do Kafka transactions combine output and offsets?

Why is an external REST API difficult to make exactly-once?

Why do Spark checkpoints not automatically guarantee business-level exactly-once?

Why are Flink checkpoints and transactional sinks related?
```

Answers should be provided after the questions or in a collapsible-style structure if Markdown supports it.

---

# 35. PRACTICAL EXERCISES

Add exercises at three levels.

## Beginner

- classify scenarios as at-most-once or at-least-once
- identify where duplicates occur
- identify where data loss occurs
- explain idempotency

## Intermediate

- implement an idempotent PostgreSQL sink
- add an event deduplication table
- build a retry-safe Kafka consumer
- implement a Kafka transactional producer/consumer flow

## Advanced

- design an end-to-end exactly-once architecture
- analyze external API failure behavior
- compare Kafka transactions with database transactions
- perform chaos testing
- prove final business correctness against a batch result

---

# 36. SENIOR DATA ENGINEER INTERVIEW PREPARATION

At the end, include interview questions strictly related to this file.

Cover:

- at-most-once
- at-least-once
- exactly-once
- idempotency
- Kafka transactions
- `read_committed`
- offsets
- failure windows
- transactional sinks
- external side effects
- Spark checkpoints
- Flink checkpoints
- two-phase commit
- end-to-end guarantees
- duplicate business effects
- failure testing

For difficult questions, require me to reason through a concrete failure scenario rather than simply define a term.

Include:

```text
Question
Expected reasoning
Strong answer
Common weak answer
```

Do not introduce unrelated interview topics.

---

# 37. FINAL CAPSTONE EXERCISE

Create one senior-level capstone.

Scenario:

```text
Kafka
 ↓
Order Events
 ↓
Python Consumer
 ↓
PostgreSQL
```

Requirements:

- at-least-once consumption
- event IDs
- idempotent business writes
- processed-event tracking
- controlled retries
- failure injection
- consumer restart
- duplicate detection
- final result verification

Then extend it to:

```text
Kafka
 ↓
Transactional Processor
 ↓
Kafka Output Topic
 ↓
read_committed Consumer
```

Finally analyze:

```text
Kafka → External API
```

and explain why a Kafka transaction alone does not provide exactly-once external business effects.

Require me to document:

```text
Source guarantee
Transport guarantee
Consumer guarantee
Processing guarantee
State guarantee
Sink guarantee
External-side-effect guarantee
Final end-to-end guarantee
```

---

# 38. FINAL ASSESSMENT

End the file with a comprehensive assessment.

The assessment should verify that I can:

- explain delivery semantics in simple terms
- identify loss scenarios
- identify duplicate scenarios
- explain commit ordering
- implement at-most-once
- implement at-least-once
- implement idempotent processing
- explain exactly-once effect
- explain Kafka transactions
- use `read_committed`
- explain transactional offsets
- distinguish producer idempotence from end-to-end exactly-once
- reason about PostgreSQL transactional sinks
- reason about external APIs
- explain Spark checkpoint-based recovery
- explain Flink checkpoint and transactional sink concepts
- design failure tests
- distinguish duplicate delivery from duplicate business effect
- reason about end-to-end guarantees

Include an explicit:

```text
NOT READY
READY
PRODUCTION-READY
```

mastery rubric.

---

# 39. FINAL MENTAL MODEL

End the lesson with a concise summary:

```text
At-most-once:
    Commit first → process later
    Lower complexity
    Possible loss

At-least-once:
    Process first → commit later
    No intentional loss
    Possible duplicates

Exactly-once effect:
    Replay is possible
    But repeated execution produces one business result

Exactly-once processing:
    Requires coordinated state, offsets, transactions/checkpoints,
    and compatible sinks

End-to-end exactly-once:
    Requires every relevant boundary to participate in the correctness model
```

Then reinforce:

> **Never ask only "Does Kafka provide exactly-once?"**
>
> Ask:
>
> **"What is the delivery and business-effect guarantee across the entire pipeline?"**

---

# 40. IMPORTANT ROADMAP BOUNDARY

This file is specifically about:

```text
05-delivery-semantics-at-most-at-least-and-exactly-once.md
```

Do not duplicate entire lessons from:

```text
03-kafka-producers-in-python.md
04-kafka-consumers-and-consumer-groups.md
06-protobuf-and-schema-registry.md
07-event-time-processing-and-watermarks.md
08-tumbling-sliding-and-session-windows.md
09-stateful-stream-processing.md
10-spark-structured-streaming.md
11-apache-flink-and-pyflink-overview.md
12-debezium-cdc-streams-into-kafka.md
13-backpressure-and-consumer-lag.md
```

However, when a concept from those files is necessary to explain delivery semantics, provide enough context to make the lesson self-contained.

Cross-reference the relevant file rather than duplicating an entire unrelated module.

---

# 41. FILE STRUCTURE

Organize the final Markdown document approximately as:

```text
# Delivery Semantics: At-Most-Once, At-Least-Once, and Exactly-Once

## Learning Objectives

## 1. Why Delivery Semantics Matter

## 2. The Message Processing Lifecycle

## 3. Failure Windows

## 4. At-Most-Once

## 5. At-Least-Once

## 6. Idempotency

## 7. At-Least-Once + Idempotent Processing

## 8. Exactly-Once Concepts

## 9. Kafka Transactions

## 10. read_committed

## 11. Python Kafka Transaction Example

## 12. Transaction Failure Scenarios

## 13. Idempotent Producer vs Exactly-Once

## 14. External Systems

## 15. Transactional Sinks

## 16. Offsets + Results in One Transaction

## 17. Spark Structured Streaming Perspective

## 18. Flink Perspective

## 19. External Side Effects

## 20. Delivery Semantics Comparison

## 21. End-to-End Guarantees

## 22. Failure Matrix

## 23. Practical Labs

## 24. Chaos Testing

## 25. Observability

## 26. Common Misconceptions

## 27. Production Architectures

## 28. Decision Framework

## 29. Advanced Distributed-Systems Mental Model

## 30. Knowledge Checkpoints

## 31. Practical Exercises

## 32. Senior Data Engineer Interview Questions

## 33. Capstone

## 34. Final Assessment

## 35. Final Mental Model
```

You may improve the exact section structure if doing so produces a clearer learning progression, but **do not omit any required concept**.

---

# 42. QUALITY BAR

Before finishing, verify the file against this checklist:

- [ ] Starts from absolute fundamentals
- [ ] Explains delivery semantics in simple language
- [ ] Explains failure windows
- [ ] Explains at-most-once
- [ ] Explains at-least-once
- [ ] Explains duplicates
- [ ] Explains idempotency
- [ ] Explains at-least-once + idempotent processing
- [ ] Explains exactly-once delivery vs processing vs effect
- [ ] Explains Kafka transactions
- [ ] Explains transactional offsets
- [ ] Explains `read_committed`
- [ ] Includes `confluent-kafka` Python examples
- [ ] Explains idempotent producer vs exactly-once
- [ ] Explains external system limitations
- [ ] Explains transactional sinks
- [ ] Explains offsets + results in the same DB transaction
- [ ] Covers Spark Structured Streaming from the semantics perspective
- [ ] Covers Flink from the semantics perspective
- [ ] Covers two-phase-commit sinks conceptually
- [ ] Covers external side-effect deduplication
- [ ] Includes failure matrices
- [ ] Includes practical labs
- [ ] Includes chaos testing
- [ ] Includes observability relevant to delivery semantics
- [ ] Includes common misconceptions
- [ ] Includes production architecture examples
- [ ] Includes a decision framework
- [ ] Includes knowledge checkpoints
- [ ] Includes practical exercises
- [ ] Includes senior-level interview preparation
- [ ] Includes a capstone
- [ ] Includes a final assessment
- [ ] Does not skip any roadmap concept
- [ ] Does not introduce unrelated curriculum topics
- [ ] Does not modify any other file

---

# 43. EXECUTION INSTRUCTION

Now inspect the existing project structure only as necessary to understand the current file and surrounding curriculum context.

Then create or update ONLY:

```text
16-Streaming-and-Event-Driven-Data/05-delivery-semantics-at-most-at-least-and-exactly-once.md
```

Make the lesson **deep, structured, beginner-friendly, technically accurate, production-oriented, and hands-on**.

The final file must teach the topic from:

```text
absolute beginner
        ↓
fundamentals
        ↓
Kafka semantics
        ↓
Python implementation
        ↓
failure reasoning
        ↓
idempotency
        ↓
transactions
        ↓
external systems
        ↓
Spark/Flink
        ↓
chaos testing
        ↓
production architecture
        ↓
senior data-engineering reasoning
```

**Do not modify any other file in the current folder under any circumstances.**