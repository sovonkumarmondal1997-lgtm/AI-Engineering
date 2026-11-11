# CLAUDE CODE PROMPT — CREATE `practice-questions.md` FOR MODULE 2.16

Act as a **Senior Data Engineer with 10+ years of industry experience** specializing in:

- Apache Kafka
- Python Data Engineering
- event-driven architectures
- streaming systems
- CDC
- Spark Structured Streaming
- Apache Flink / PyFlink
- stateful stream processing
- data reliability
- distributed systems
- streaming observability
- production data platforms.

You are also an expert technical educator and interview-preparation mentor.

Your task is to create the **complete practice-question and solution module** for:

```text
Python for Data Engineering/
└── 16-Streaming-and-Event-Driven-Data/
    └── practice-questions.md
```

The practice questions must be based strictly on the concepts taught throughout the complete:

```text
16-Streaming-and-Event-Driven-Data/
```

module.

---

# 1. CRITICAL FILE-SCOPE RULE

**ONLY `practice-questions.md` may be modified.**

You are allowed to:

- read the other files in the folder
- analyze their concepts
- synthesize their relationships
- use them to design integrated practice problems.

You MUST NOT:

- modify any other `.md` file
- create any other file
- delete any file
- rename any file
- reorganize the folder
- update the README
- update the roadmap
- update `interview-practice.md`
- modify any of the 13 topic files.

The final modification must be limited to:

```text
16-Streaming-and-Event-Driven-Data/practice-questions.md
```

---

# 2. FIRST: INSPECT THE ENTIRE MODULE

Before writing the practice questions, inspect and analyze **all relevant files** under:

```text
16-Streaming-and-Event-Driven-Data/
```

The canonical learning sequence is:

```text
01-event-streams-vs-message-queues.md
02-kafka-topics-partitions-offsets-and-replication.md
03-kafka-producers-in-python.md
04-kafka-consumers-and-consumer-groups.md
05-delivery-semantics-at-most-at-least-and-exactly-once.md
06-protobuf-and-schema-registry.md
07-event-time-processing-time-and-watermarks.md
08-tumbling-sliding-and-session-windows.md
09-stateful-stream-processing.md
10-spark-structured-streaming.md
11-apache-flink-and-pyflink-overview.md
12-debezium-cdc-streams-into-kafka.md
13-backpressure-and-consumer-lag.md
```

Also inspect:

```text
README.md
```

for module-level:

- learning objectives
- dependency chain
- mini-project
- learning methodology
- exit criteria
- cross-topic relationships.

You may inspect:

```text
interview-practice.md
```

only to avoid unnecessarily duplicating interview-specific questions.

---

# 3. SOURCE-OF-TRUTH RULE

The existing Module 2.16 learning files are the **authoritative source** for the practice questions.

Do not silently introduce concepts that were not taught in Module 2.16.

The questions may combine concepts from multiple Module 2.16 files, because the purpose of this file is to test integrated understanding.

However:

> Every question must be traceable to concepts actually taught in this module.

Do not turn this into a generic distributed-systems question bank.

Do not introduce unrelated:

- Kubernetes internals
- cloud architecture
- ML engineering
- generic database administration
- generic networking
- generic DevOps
- unrelated Python algorithms.

If an external concept is absolutely necessary to solve a problem, keep it at the minimum level required by the Module 2.16 curriculum.

---

# 4. PRIMARY OBJECTIVE

Create exactly:

# 40 Practice Questions

divided into:

```text
10 BASIC
10 MODERATE
10 HARD
10 ADVANCED
```

Total:

```text
10 + 10 + 10 + 10 = 40
```

Do not create 39.

Do not create 41.

Do not combine multiple questions and accidentally change the count.

Use explicit numbering:

```text
Basic:
1–10

Moderate:
11–20

Hard:
21–30

Advanced:
31–40
```

---

# 5. MOST IMPORTANT RULE — PROBLEM FIRST, SOLUTION SECOND

This rule applies to **ALL 40 questions**.

Every question must follow this structure:

```text
Problem
    ↓
How to solve the problem
    ↓
Detailed solution
    ↓
Why the solution works
```

Never provide only a question.

Never provide only an answer.

Never provide a one-line solution.

Every practice question must contain both:

1. **Problem**
2. **Solution**

---

# 6. REQUIRED STRUCTURE FOR EVERY QUESTION

Use the following structure consistently:

```markdown
## Question 1 — <Descriptive Title>

### Difficulty
Basic

### Topics Covered
- Topic X
- Topic Y

### Problem

<realistic problem statement>

### What You Need to Determine

1. ...
2. ...
3. ...

### Solution

#### Step 1 — Understand the problem

...

#### Step 2 — Identify the relevant streaming concepts

...

#### Step 3 — Design the solution

...

#### Step 4 — Implement / calculate / reason

...

#### Step 5 — Verify the result

...

### Final Answer

<clear final conclusion>

### Why This Solution Is Correct

...

### Common Mistake

...

### Key Takeaway

...
```

Not every problem requires all five "What You Need to Determine" items, but every problem must clearly explain the reasoning process.

---

# 7. TEACH THROUGH THE SOLUTIONS

The solutions must not merely reveal the answer.

They should teach the learner **how an experienced Data Engineer thinks**.

For every problem, explain:

```text
What is happening?
Why is it happening?
Which concept applies?
What are the alternatives?
Why is this solution preferred?
What could go wrong?
How would we verify it?
```

The learner should be able to solve a similar problem independently after reading the solution.

---

# 8. DIFFICULTY PROGRESSION

The difficulty must increase meaningfully.

Do NOT simply make Basic questions short and Advanced questions long.

The complexity must increase in terms of:

- number of concepts
- reasoning required
- failure modes
- architecture complexity
- calculations
- debugging
- trade-offs
- implementation
- distributed-system reasoning
- production constraints.

Use this progression:

```text
BASIC
    ↓
Understand individual concepts

MODERATE
    ↓
Combine 2–3 concepts

HARD
    ↓
Solve realistic engineering problems
with multiple interacting concepts

ADVANCED
    ↓
Production architecture,
failure analysis,
capacity planning,
correctness,
trade-offs,
and end-to-end reasoning
```

---

# 9. BASIC QUESTIONS — QUESTIONS 1–10

Create exactly **10 Basic questions**.

Basic questions should verify foundational understanding.

Cover concepts such as:

### Event streams vs queues

- event vs command vs message
- queue vs event stream
- replay
- fan-out
- when to use stream vs queue.

### Kafka fundamentals

- topic
- partition
- offset
- record key
- partition ordering.

### Kafka producers

- `produce()`
- `poll()`
- `flush()`
- asynchronous production
- `acks`.

### Kafka consumers

- consumer groups
- partition assignment
- offsets
- commits.

### Delivery semantics

- at-most-once
- at-least-once
- exactly-once effect.

### Schemas

- Protobuf
- Schema Registry
- schema evolution.

### Time

- event time
- processing time
- watermark.

### Windows

- tumbling
- sliding
- session.

### State

- stateless vs stateful
- keyed state
- deduplication.

### Engines

- basic Spark Structured Streaming concept
- basic Flink concept.

### CDC

- Debezium
- PostgreSQL WAL
- replication slot
- CDC event.

### Operations

- consumer lag
- backpressure.

Do not make all 10 questions cover only Kafka.

Distribute the questions across the complete module.

---

# 10. MODERATE QUESTIONS — QUESTIONS 11–20

Create exactly **10 Moderate questions**.

Each question should combine approximately 2–4 concepts.

Examples of appropriate combinations:

```text
Kafka partitions
+
consumer groups
+
offsets
```

or:

```text
event time
+
watermarks
+
tumbling windows
```

or:

```text
Debezium
+
Kafka
+
idempotent sink
```

or:

```text
Protobuf
+
Schema Registry
+
schema evolution
```

or:

```text
consumer lag
+
backpressure
+
consumer scaling
```

Possible problem styles:

- configuration analysis
- small calculations
- debugging
- Python implementation
- Kafka design
- event-time reasoning
- window assignment
- schema evolution
- CDC interpretation
- lag diagnosis.

The learner should have to reason rather than recall definitions.

---

# 11. HARD QUESTIONS — QUESTIONS 21–30

Create exactly **10 Hard questions**.

These should represent realistic Data Engineering problems.

Each should combine multiple concepts.

Examples:

### Problem type 1 — Kafka reliability

A producer experiences broker failures while publishing orders.

Ask the learner to reason about:

- `acks`
- retries
- idempotence
- duplicates
- ordering
- delivery guarantees.

---

### Problem type 2 — Consumer failure

A consumer processes a batch, crashes before committing, and restarts.

Ask:

- What happens?
- Can duplicates occur?
- How should the sink be designed?
- What delivery semantics result?

---

### Problem type 3 — Event-time analytics

Events arrive:

```text
out of order
late
from multiple partitions
```

Design:

- watermark
- allowed lateness
- window
- late-event handling.

---

### Problem type 4 — Stateful processing

Build:

```text
order
+
payment
```

stream correlation with a time bound.

Reason about:

- keyed state
- state TTL
- watermarks
- stream-stream joins
- recovery.

---

### Problem type 5 — Spark streaming

A Spark Structured Streaming job has:

- increasing micro-batch duration
- growing Kafka lag
- large input bursts.

Diagnose and design:

- checkpoint strategy
- `maxOffsetsPerTrigger`
- sink optimization
- recovery.

---

### Problem type 6 — Flink

A Flink job has:

```text
source → transform → slow sink
```

and the UI shows backpressure.

Identify:

- bottleneck
- propagation
- mitigation.

---

### Problem type 7 — Debezium

A PostgreSQL Debezium connector is stopped while writes continue.

Reason about:

- WAL
- replication slot
- connector recovery
- catch-up
- duplicate possibilities.

---

### Problem type 8 — Schema evolution

Producer changes a schema while old consumers remain deployed.

Reason about:

- compatibility
- Schema Registry
- backward/forward compatibility
- safe deployment.

---

### Problem type 9 — Hot partition

One Kafka partition has almost all the lag.

Reason about:

- key distribution
- partitioning
- consumer scaling
- ordering trade-offs.

---

### Problem type 10 — Retention

Consumer outage approaches Kafka retention.

Calculate:

- lag
- recovery rate
- time to catch up
- retention safety.

---

# 12. ADVANCED QUESTIONS — QUESTIONS 31–40

Create exactly **10 Advanced questions**.

These must resemble **senior Data Engineer / streaming-system design problems**.

They should require integrated reasoning across the module.

Advanced questions must include combinations of:

```text
Kafka
+
delivery semantics
+
schemas
+
event time
+
windows
+
state
+
Spark/Flink
+
CDC
+
lag
+
backpressure
+
failure recovery
```

Not every Advanced question needs every concept, but collectively all major areas must be exercised.

---

# 13. ADVANCED PROBLEM TYPES

Use realistic production scenarios.

Include problems such as:

### Advanced 31 — Real-time order analytics

Design:

```text
Producers
→ Kafka
→ Schema Registry
→ Stream processor
→ Stateful analytics
→ Lakehouse
```

Requirements:

- event-time correctness
- deduplication
- late data
- windows
- recovery
- idempotent sink.

Require a complete architecture and reasoning.

---

### Advanced 32 — Exactly-once business effect

A pipeline claims:

> "We use Kafka exactly-once."

Ask the learner to challenge that statement.

Analyze:

```text
Producer
→ Kafka
→ Consumer
→ PostgreSQL
→ External API
```

Determine:

- actual guarantee
- failure windows
- idempotency
- transactional boundaries
- external side effects.

---

### Advanced 33 — CDC to lakehouse

Design:

```text
PostgreSQL
→ Debezium
→ Kafka
→ Spark/Flink
→ Delta/Iceberg
```

Requirements:

- inserts
- updates
- deletes
- tombstones
- deduplication
- ordering
- schema evolution
- reconciliation.

---

### Advanced 34 — Kafka lag incident

Production system:

```text
lag increasing
one partition hot
sink slowing
consumer rebalances increasing
```

Require the learner to:

1. diagnose the root cause;
2. identify secondary symptoms;
3. choose mitigations;
4. protect retention;
5. define monitoring;
6. define recovery.

---

### Advanced 35 — Event-time correctness

A stream contains:

```text
event-time disorder
late events
idle partitions
clock skew
```

Design:

- watermark
- allowed lateness
- window
- late-data policy
- reconciliation.

---

### Advanced 36 — Stateful failure recovery

A stateful streaming job crashes after processing thousands of events.

Ask how to guarantee correct recovery.

Discuss:

- checkpoint
- offsets
- state
- replay
- deduplication
- idempotent sink.

---

### Advanced 37 — Schema evolution

Design a safe deployment where:

```text
Producer v2
Consumer v1
Consumer v2
```

coexist.

Require reasoning about:

- Protobuf
- Schema Registry
- compatibility
- rollout
- rollback.

---

### Advanced 38 — Capacity planning

Given:

```text
producer throughput
consumer throughput
partition count
peak traffic
retention
outage duration
```

calculate whether the architecture is safe.

Require:

- consumer count
- partition requirement
- headroom
- catch-up time
- retention risk.

---

### Advanced 39 — Spark vs Flink

Given a workload with:

- stateful processing
- low-latency requirements
- Kafka input
- event-time windows
- large state
- operational constraints.

Require the learner to choose:

```text
Spark Structured Streaming
or
Flink
```

and justify the decision.

Do not accept "Flink is faster" or "Spark is easier" as sufficient.

Require a structured trade-off analysis.

---

### Advanced 40 — Complete production streaming architecture

Design an end-to-end:

# Real-Time Order Analytics Platform

Architecture should potentially include:

```text
Application
   ↓
Transactional Outbox
   ↓
PostgreSQL
   ↓
Debezium
   ↓
Kafka
   ↓
Schema Registry
   ↓
Spark / Flink
   ↓
Stateful Processing
   ↓
Lakehouse
   ↓
Real-Time Analytics
```

Requirements should include:

- delivery semantics
- schema evolution
- event time
- watermarks
- windows
- state
- deduplication
- CDC
- backpressure
- lag monitoring
- retention
- failure recovery
- reconciliation
- SLOs.

The solution must explain the architecture component by component.

---

# 14. ENSURE ALL 13 TOPICS ARE COVERED

Across the 40 questions, ensure every one of these files is meaningfully represented:

```text
01-event-streams-vs-message-queues.md
02-kafka-topics-partitions-offsets-and-replication.md
03-kafka-producers-in-python.md
04-kafka-consumers-and-consumer-groups.md
05-delivery-semantics-at-most-at-least-and-exactly-once.md
06-protobuf-and-schema-registry.md
07-event-time-processing-time-and-watermarks.md
08-tumbling-sliding-and-session-windows.md
09-stateful-stream-processing.md
10-spark-structured-streaming.md
11-apache-flink-and-pyflink-overview.md
12-debezium-cdc-streams-into-kafka.md
13-backpressure-and-consumer-lag.md
```

Do not let the question bank become Kafka-heavy.

The practice set must represent the entire streaming curriculum.

---

# 15. REQUIRED TOPIC COVERAGE MATRIX

Before finalizing the document, internally create a coverage matrix.

Use this structure:

| Topic | Basic | Moderate | Hard | Advanced |
|---|---:|---:|---:|---:|
| Streams vs queues | ✓ | ✓ | ✓ | ✓ |
| Kafka architecture | ✓ | ✓ | ✓ | ✓ |
| Producers | ✓ | ✓ | ✓ | ✓ |
| Consumers | ✓ | ✓ | ✓ | ✓ |
| Delivery semantics | ✓ | ✓ | ✓ | ✓ |
| Protobuf/Schema Registry | ✓ | ✓ | ✓ | ✓ |
| Event time/watermarks | ✓ | ✓ | ✓ | ✓ |
| Windows | ✓ | ✓ | ✓ | ✓ |
| Stateful processing | ✓ | ✓ | ✓ | ✓ |
| Spark | ✓ | ✓ | ✓ | ✓ |
| Flink | ✓ | ✓ | ✓ | ✓ |
| Debezium/CDC | ✓ | ✓ | ✓ | ✓ |
| Lag/backpressure | ✓ | ✓ | ✓ | ✓ |

You do not need to literally expose this matrix in the final document unless useful.

But you MUST use it internally to verify balanced coverage.

---

# 16. QUESTION DISTRIBUTION

Do not make all questions theoretical.

Across the 40 questions, deliberately include:

### Conceptual reasoning

Questions that ask:

- explain
- compare
- choose
- justify.

### Calculation

Questions involving:

- offsets
- lag
- throughput
- catch-up time
- window boundaries
- partition capacity.

### Debugging

Questions involving:

- consumer failures
- rebalance
- lag
- hot partitions
- schema errors
- CDC failures
- checkpoint recovery.

### Coding

Include appropriate:

- Python
- Kafka
- Spark
- PyFlink
- SQL
- configuration.

### Architecture

Include:

- topic design
- partition strategy
- streaming architecture
- CDC architecture
- processing engine selection.

### Failure analysis

Include:

- crashes
- retries
- duplicates
- late events
- broker failures
- consumer outages
- state recovery
- WAL growth
- retention cliff.

---

# 17. CODING QUESTIONS

At least several questions must require actual implementation or pseudocode.

Use the module's intended ecosystem:

```text
Python 3.12+
confluent-kafka
protobuf
Schema Registry
PySpark
PyFlink
PostgreSQL
Kafka
```

Examples:

```python
producer.produce(...)
```

```python
consumer.poll(...)
```

Spark:

```python
spark.readStream
```

Flink/PyFlink:

```python
key_by(...)
```

PostgreSQL:

```sql
MERGE ...
```

Debezium/Kafka Connect:

```json
{
  "connector.class": "..."
}
```

Do not force code into questions where reasoning is more appropriate.

---

# 18. CALCULATION QUESTIONS

Include realistic calculations.

Examples:

### Lag

```text
latest offset = 250,000
committed offset = 230,000
```

Calculate lag.

### Catch-up

```text
lag = 500,000
consumer rate = 80,000/sec
producer rate = 60,000/sec
```

Calculate net recovery rate and approximate catch-up time.

### Partition capacity

```text
required throughput = 200 MB/sec
measured sustainable throughput = 25 MB/sec/partition
```

Reason about partition requirements.

### Window

Given events with timestamps, determine:

- tumbling window
- sliding window
- session membership.

### Watermark

Given:

```text
max event time
allowed lateness
```

determine watermark.

---

# 19. PROBLEM REALISM

Every question should feel like a real Data Engineering task.

Prefer scenarios such as:

```text
orders
payments
customers
clickstream
inventory
fraud events
CDC
IoT telemetry
user sessions
financial transactions
```

Avoid artificial textbook questions such as:

> "Define Kafka."

Instead prefer:

> "A team has 8 Kafka partitions and 12 consumers. Only 8 consumers are active. The team claims Kafka is failing to use all CPU cores. Explain what is happening and what you would change."

The solution should teach the concept.

---

# 20. SOLUTION QUALITY STANDARD

Every solution must include the reasoning process.

For example:

```text
Problem
↓
Identify constraints
↓
Identify relevant concepts
↓
Analyze failure mode
↓
Evaluate options
↓
Choose solution
↓
Implement
↓
Verify
```

For architecture problems:

```text
Requirements
↓
Architecture
↓
Data flow
↓
Correctness model
↓
Failure handling
↓
Scaling
↓
Observability
↓
Trade-offs
```

---

# 21. DO NOT GIVE SUPERFICIAL SOLUTIONS

Avoid solutions like:

> "Add more consumers."

Instead explain:

```text
First:
Check partition count.

Then:
Check per-partition lag.

Then:
Check whether a hot partition exists.

Then:
Check sink throughput.

Then:
Check CPU.

Then:
Check rebalance frequency.

Only then:
Decide whether consumer scaling is useful.
```

The solution should model senior-engineer reasoning.

---

# 22. INCLUDE COMMON MISTAKES

Every question should have at least one:

```text
### Common Mistake
```

Explain what a weaker engineer might do incorrectly.

Examples:

- assuming global Kafka ordering
- assuming more consumers always improve throughput
- confusing processing time with event time
- treating Kafka transactions as end-to-end exactly-once
- ignoring tombstones
- ignoring state TTL
- ignoring retention
- committing offsets before processing
- treating connector `RUNNING` as end-to-end health.

---

# 23. INCLUDE VERIFICATION

Whenever possible, explain how the learner can prove the solution.

Examples:

```text
Compare source and sink counts.
```

```text
Replay Kafka events.
```

```text
Kill and restart the consumer.
```

```text
Compare streaming output with batch recomputation.
```

```text
Inspect Kafka consumer lag.
```

```text
Inspect Spark progress metrics.
```

```text
Inspect Flink backpressure.
```

```text
Compare PostgreSQL source state with lakehouse state.
```

The goal is:

> **Do not just implement the pipeline. Prove that it is correct.**

---

# 24. INTEGRATED PROBLEM DESIGN

Some questions should intentionally connect earlier and later concepts.

For example:

```text
Kafka partitioning
        +
consumer groups
        +
delivery semantics
        +
idempotent sink
```

or:

```text
event time
        +
watermark
        +
window
        +
state
```

or:

```text
Debezium
        +
Kafka
        +
Schema Registry
        +
Spark
        +
MERGE
```

or:

```text
consumer lag
        +
backpressure
        +
partition skew
        +
retention
```

These integrated problems are especially important for Hard and Advanced levels.

---

# 25. MINI-PROJECT CONNECTION

Use the module's real-time order analytics platform as a recurring context where useful.

Conceptually:

```text
PostgreSQL / Application
        ↓
Debezium / Producers
        ↓
Kafka
        ↓
Schema Registry
        ↓
Spark / Flink
        ↓
Stateful Processing
        ↓
Lakehouse
        ↓
Analytics / Alerts
```

Questions should occasionally ask the learner to diagnose or extend this system.

Do not turn all 40 questions into the same project.

Use different scenarios while maintaining consistency with the module.

---

# 26. CROSS-TOPIC REASONING

Some questions should explicitly require the learner to identify which concepts interact.

Example:

> A Kafka consumer processes payment events using event time. Payments can arrive 8 minutes late. The business wants a 5-minute revenue window. Explain why simply using processing time would produce incorrect results.

Then require:

```text
event time
+
watermark
+
allowed lateness
+
window semantics
```

Another:

> A Debezium consumer is producing duplicate updates into a lakehouse.

Require:

```text
at-least-once delivery
+
CDC ordering
+
event metadata
+
idempotent MERGE
```

---

# 27. NO TOPIC SHOULD BE TESTED ONLY ONCE

Important concepts should appear multiple times at increasing difficulty.

For example:

```text
Kafka partitions
```

should appear in:

- Basic conceptual question
- Moderate calculation/design question
- Hard hot-partition problem
- Advanced capacity-planning problem.

Similarly:

```text
delivery semantics
event time
state
CDC
consumer lag
```

should reappear at higher levels.

This creates progressive reinforcement.

---

# 28. BASIC QUESTION CHARACTERISTICS

Basic questions should test:

- vocabulary
- mental models
- simple calculations
- straightforward decisions.

Do not make Basic questions trivial.

A Basic question should still require the learner to reason.

Example:

> A topic has four partitions and a consumer group has six consumers. How many consumers can actively own partitions at the same time, and why?

---

# 29. MODERATE QUESTION CHARACTERISTICS

Moderate questions should require:

- multiple concepts
- small implementation
- debugging
- configuration reasoning
- calculations.

Example:

> A consumer processes 20,000 records/sec while the producer generates 30,000 records/sec. The topic has six partitions. Explain why lag grows and identify two different mitigation strategies.

---

# 30. HARD QUESTION CHARACTERISTICS

Hard questions should require:

- failure analysis
- architecture
- implementation
- trade-offs.

Example:

> A consumer crashes after writing a batch to PostgreSQL but before committing Kafka offsets. The application restarts and processes the same records again. Design the sink so the business state remains correct.

---

# 31. ADVANCED QUESTION CHARACTERISTICS

Advanced questions should require:

- end-to-end architecture
- distributed-systems reasoning
- correctness guarantees
- scalability
- observability
- recovery
- trade-off analysis.

The learner should think like a senior Data Engineer.

---

# 32. REQUIRED MARKDOWN ORGANIZATION

The final `practice-questions.md` should use approximately this structure:

```markdown
# Module 2.16 — Streaming and Event-Driven Data
# Practice Questions and Solutions

## How to Use This Practice Set

## Coverage and Difficulty Model

---

# Part I — Basic

## Question 1 — ...
...
## Question 10 — ...

---

# Part II — Moderate

## Question 11 — ...
...
## Question 20 — ...

---

# Part III — Hard

## Question 21 — ...
...
## Question 30 — ...

---

# Part IV — Advanced

## Question 31 — ...
...
## Question 40 — ...

---

# Final Coverage Checklist

# Module 2.16 Mastery Guidance
```

---

# 33. FINAL COVERAGE CHECKLIST

At the end, include a concise learner-facing checklist showing that the 40 questions collectively cover:

```text
[ ] Event streams vs message queues
[ ] Kafka topics
[ ] Kafka partitions
[ ] Offsets
[ ] Keys
[ ] Replication
[ ] ISR
[ ] min.insync.replicas
[ ] Retention
[ ] Compaction
[ ] Kafka producers
[ ] Acknowledgements
[ ] Idempotence
[ ] Batching
[ ] Compression
[ ] Partitioners
[ ] Kafka consumers
[ ] Consumer groups
[ ] Offset commits
[ ] Rebalances
[ ] Replay
[ ] DLQ
[ ] Delivery semantics
[ ] Idempotent processing
[ ] Kafka transactions
[ ] Protobuf
[ ] Schema Registry
[ ] Schema compatibility
[ ] Schema evolution
[ ] Event time
[ ] Processing time
[ ] Watermarks
[ ] Late data
[ ] Tumbling windows
[ ] Sliding windows
[ ] Session windows
[ ] Triggers/output modes
[ ] Stateful processing
[ ] Keyed state
[ ] Deduplication
[ ] Stream-static joins
[ ] Stream-stream joins
[ ] State TTL
[ ] Checkpointing
[ ] State recovery
[ ] Spark Structured Streaming
[ ] Spark checkpoints
[ ] Spark Kafka integration
[ ] Spark stateful processing
[ ] Spark foreachBatch
[ ] Spark maxOffsetsPerTrigger
[ ] Flink
[ ] PyFlink
[ ] Flink state
[ ] Flink checkpoints
[ ] Flink savepoints
[ ] Flink backpressure
[ ] Debezium
[ ] PostgreSQL WAL
[ ] Logical decoding
[ ] Replication slots
[ ] CDC snapshots
[ ] Debezium envelopes
[ ] Deletes
[ ] Tombstones
[ ] SMTs
[ ] Outbox pattern
[ ] CDC → Kafka → lakehouse
[ ] Consumer lag
[ ] Record lag
[ ] Time lag
[ ] Backpressure
[ ] Hot partitions
[ ] Scaling consumers
[ ] Retention cliff
[ ] Catch-up time
[ ] End-to-end latency
[ ] Latency SLOs
[ ] Capacity planning
```

---

# 34. FINAL QUALITY AUDIT

Before finishing `practice-questions.md`, perform a strict audit.

Verify:

### Count

```text
Basic      = exactly 10
Moderate   = exactly 10
Hard       = exactly 10
Advanced   = exactly 10
TOTAL      = exactly 40
```

### Structure

Every question has:

```text
Problem
↓
Solution
↓
Reasoning
↓
Final Answer
↓
Common Mistake
↓
Key Takeaway
```

where appropriate.

### Coverage

All 13 Module 2.16 topic files are represented.

### Difficulty

Difficulty genuinely increases from Basic → Advanced.

### Solutions

Every problem has a detailed solution.

### Practicality

Questions include:

- conceptual reasoning
- calculations
- coding
- debugging
- architecture
- failure recovery
- trade-offs.

### Scope

Every question is directly related to:

```text
16-Streaming-and-Event-Driven-Data/
```

### No unrelated topics

Do not introduce unrelated curriculum material.

### Engineering quality

Solutions should model:

```text
requirements
→ constraints
→ diagnosis
→ design
→ implementation
→ verification
→ trade-offs
```

---

# 35. FINAL FILE-SAFETY CHECK

Before saving the result:

```text
ONLY practice-questions.md
```

may be modified.

Do not update:

```text
README.md
01-event-streams-vs-message-queues.md
02-kafka-topics-partitions-offsets-and-replication.md
03-kafka-producers-in-python.md
04-kafka-consumers-and-consumer-groups.md
05-delivery-semantics-at-most-at-least-and-exactly-once.md
06-protobuf-and-schema-registry.md
07-event-time-processing-time-and-watermarks.md
08-tumbling-sliding-and-session-windows.md
09-stateful-stream-processing.md
10-spark-structured-streaming.md
11-apache-flink-and-pyflink-overview.md
12-debezium-cdc-streams-into-kafka.md
13-backpressure-and-consumer-lag.md
interview-practice.md
```

Do not create any additional files.

---

# 36. FINAL INSTRUCTION

Create a **high-quality, production-oriented 40-question practice system** that takes the learner through:

```text
Fundamentals
     ↓
Kafka
     ↓
Producers / Consumers
     ↓
Reliability
     ↓
Schemas
     ↓
Event Time
     ↓
Windows
     ↓
State
     ↓
Spark
     ↓
Flink
     ↓
CDC
     ↓
Backpressure
     ↓
Lag
     ↓
Production Architecture
```

The questions should not merely ask:

> "What is X?"

They should increasingly ask:

> **"Here is a real streaming-system problem. What is happening, why is it happening, how would you solve it, what trade-offs exist, and how would you prove that your solution is correct?"**

The final practice file should therefore function as both:

1. a **learning reinforcement system**, and
2. a **production Data Engineering problem-solving exercise set**.

The ultimate goal is to prove that the learner can reason about a complete streaming system rather than memorize individual Kafka, Spark, Flink, or CDC concepts.