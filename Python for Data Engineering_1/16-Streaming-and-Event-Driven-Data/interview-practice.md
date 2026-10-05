# CLAUDE CODE PROMPT — CREATE `interview-practice.md` FOR MODULE 2.16

## ROLE

Act as a **Senior Data Engineer with 10+ years of industry experience** designing, building, debugging, scaling, and operating production-grade:

- Apache Kafka platforms
- Python streaming systems
- event-driven architectures
- CDC pipelines
- stateful stream-processing systems
- Spark Structured Streaming pipelines
- Apache Flink / PyFlink systems
- lakehouse ingestion pipelines
- high-throughput distributed data platforms
- real-time analytics systems
- streaming observability and reliability systems.

You are also an experienced **Data Engineering interviewer and hiring manager** who has conducted technical interviews for mid-level, senior, staff, and lead Data Engineers.

Your task is to create the complete interview-preparation module for:

```text
Python for Data Engineering/
└── 16-Streaming-and-Event-Driven-Data/
    └── interview-practice.md
```

The interview preparation must be based strictly on the concepts taught throughout:

```text
16-Streaming-and-Event-Driven-Data/
```

The Module 2.16 roadmap specifically identifies interview preparation around:

- queue vs log
- Kafka partitions and ordering
- consumer groups and rebalances
- acknowledgements and idempotent producers
- at-least-once vs exactly-once
- Kafka transactions
- event time vs processing time
- watermarks
- window types
- stateful processing and checkpoints
- Spark Structured Streaming vs Flink
- compacted topics
- Schema Registry compatibility
- consumer lag
- real-time revenue dashboards
- fraud alerts
- PostgreSQL → lakehouse CDC
- deduplication
- order/payment joins
- growing consumer lag
- reprocessing historical events.

Use the existing Module 2.16 files as the authoritative source for the exact concepts and terminology.

---

# 1. CRITICAL FILE-SCOPE RULE

**ONLY `interview-practice.md` may be modified.**

You may inspect all other files in:

```text
16-Streaming-and-Event-Driven-Data/
```

to understand the curriculum.

You MUST NOT:

- modify any other file
- create any other file
- delete any file
- rename any file
- reorganize the directory
- update `README.md`
- update any of the 13 topic files
- update `practice-questions.md`
- modify the roadmap
- create additional interview files.

The only file that may be created or updated is:

```text
16-Streaming-and-Event-Driven-Data/interview-practice.md
```

---

# 2. FIRST: INSPECT THE COMPLETE MODULE

Before generating interview questions, inspect and analyze the complete Module 2.16 curriculum.

Read:

```text
README.md
```

and:

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
practice-questions.md
```

only to understand the learning coverage and avoid blindly duplicating the same exercises.

The interview questions must test whether the learner can **explain, reason, diagnose, design, implement, and defend decisions** about these concepts.

---

# 3. SOURCE-OF-TRUTH RULE

The Module 2.16 topic files are the authoritative source.

Every interview question must be directly traceable to concepts actually taught in:

```text
16-Streaming-and-Event-Driven-Data/
```

Do not silently expand the curriculum into unrelated topics.

Do NOT turn this into a generic interview bank covering:

- Kubernetes internals
- cloud certifications
- generic SQL
- generic system design unrelated to streaming
- machine learning
- generic algorithms
- unrelated DevOps
- unrelated networking
- unrelated database internals.

External concepts may only appear when necessary to explain or solve a Module 2.16 streaming problem.

---

# 4. PRIMARY OBJECTIVE

Create exactly:

# 40 Interview Questions

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

Number them:

```text
1–10    Basic
11–20   Moderate
21–30   Hard
31–40   Advanced
```

Do not create 39 or 41.

Do not combine multiple interview questions under one number.

---

# 5. MOST IMPORTANT RULE — PROBLEM FIRST, SOLUTION SECOND

This rule applies to **ALL 40 interview questions**.

Every interview question must introduce a problem or interview scenario first.

Then provide the solution and explain:

> **How a strong candidate should solve and answer the problem.**

The structure must be:

```text
Interview Problem
        ↓
What the interviewer is testing
        ↓
How to approach the problem
        ↓
Strong answer
        ↓
Detailed technical reasoning
        ↓
Trade-offs
        ↓
Common weak answer
        ↓
What distinguishes a senior answer
```

Do not simply provide:

```text
Question:
What is Kafka?
Answer:
Kafka is...
```

That is insufficient.

The learner is preparing for technical interviews, not memorizing definitions.

---

# 6. REQUIRED STRUCTURE FOR EVERY QUESTION

Use this structure:

```markdown
## Question 1 — <Interview Question Title>

### Difficulty
Basic

### Interview Type
Conceptual / Debugging / Design / Coding / Architecture / Trade-off

### Topics Tested

- Kafka partitions
- Consumer groups
- Offsets

### Interview Problem

<realistic interview question or scenario>

### What the Interviewer Is Testing

<skills being evaluated>

### How to Approach the Problem

1. ...
2. ...
3. ...

### Strong Answer

<complete interview-quality answer>

### Detailed Reasoning

#### Step 1 — ...

#### Step 2 — ...

#### Step 3 — ...

### Example

<code / architecture / calculation / diagram where appropriate>

### Trade-offs

<important trade-offs>

### Common Weak Answer

<typical incomplete or incorrect answer>

### Why the Weak Answer Is Insufficient

...

### Senior-Level Insight

...

### Interview Takeaway

...
```

Use only sections that are relevant to the question, but preserve the overall structure.

---

# 7. INTERVIEW-ANSWER TEACHING STYLE

The goal is not only to provide the answer.

Teach the learner:

> **How to think and communicate during a real technical interview.**

For every solution, demonstrate:

```text
Clarify requirements
        ↓
Identify constraints
        ↓
Identify relevant streaming concepts
        ↓
Reason about correctness
        ↓
Reason about failure modes
        ↓
Choose architecture
        ↓
Explain trade-offs
        ↓
Discuss scaling
        ↓
Discuss observability
        ↓
State final recommendation
```

For architecture questions, explicitly demonstrate this reasoning process.

---

# 8. BASIC QUESTIONS — 1–10

Create exactly 10 Basic interview questions.

These should test foundational Module 2.16 understanding.

Cover concepts such as:

### Question areas

- Event stream vs message queue
- Event vs command
- Kafka topic
- Kafka partition
- Kafka offset
- Kafka key
- Ordering
- Consumer group
- Producer acknowledgements
- `acks=0`, `acks=1`, `acks=all`
- Idempotent producer
- Offset commit
- At-most-once
- At-least-once
- Event time
- Processing time
- Watermark
- Tumbling window
- Sliding window
- Session window
- Stateful vs stateless processing
- Consumer lag.

The question should still be scenario-oriented.

Example style:

> A team says Kafka guarantees ordering for all events in a topic. Is that statement correct? Explain exactly what ordering Kafka guarantees and how partition keys affect it.

Then provide the strong interview answer.

---

# 9. MODERATE QUESTIONS — 11–20

Create exactly 10 Moderate questions.

Moderate questions should combine multiple concepts.

Examples:

### Consumer groups

```text
6 Kafka partitions
8 consumers
```

Ask:

- How many consumers can actively process partitions?
- What happens to the remaining consumers?
- What happens when another consumer joins?
- What happens during rebalance?

---

### Producer reliability

A producer uses:

```text
acks=1
retries > 0
enable.idempotence=false
```

Ask:

- What failure modes exist?
- Can duplicates occur?
- How would you change the configuration?

---

### Delivery semantics

A consumer writes to PostgreSQL and commits its Kafka offset afterward.

It crashes after the database commit but before Kafka commit.

Ask:

- What happens after restart?
- What guarantee exists?
- How should the sink be designed?

---

### Event-time processing

Events arrive 7 minutes late.

Business requires correct 5-minute revenue windows.

Ask:

- How should the watermark be selected?
- What happens to late events?
- What are the trade-offs?

---

### Schema evolution

Producer v2 is deployed while consumer v1 remains active.

Ask:

- What compatibility rule is required?
- What schema changes are safe?
- How does Schema Registry help?

---

# 10. HARD QUESTIONS — 21–30

Create exactly 10 Hard interview questions.

Hard questions should simulate **real senior Data Engineer interviews**.

They should involve:

- debugging
- failure analysis
- architecture
- implementation
- trade-offs
- production incidents.

Include scenarios such as:

---

## Kafka hot partition

One partition has 90% of the traffic.

The consumer group has many consumers, but lag remains concentrated on one partition.

Ask the candidate to:

1. diagnose the problem;
2. explain why adding consumers may not help;
3. identify the key-distribution problem;
4. propose solutions;
5. explain ordering trade-offs.

---

## Consumer rebalance storm

A consumer repeatedly leaves the group.

Processing sometimes takes longer than:

```text
max.poll.interval.ms
```

Ask:

- Why does this happen?
- What symptoms appear?
- How would you fix it?
- What trade-offs exist?

---

## Kafka retention cliff

A consumer has fallen behind.

Given:

```text
current lag
producer throughput
consumer throughput
topic retention
```

ask the candidate to calculate whether the consumer can catch up before data expires.

Require explicit reasoning.

---

## Spark streaming lag

A Spark Structured Streaming pipeline has:

- increasing batch duration
- growing Kafka lag
- slow sink writes.

Ask the candidate to diagnose:

```text
source
→ processing
→ state
→ sink
```

and determine where backpressure is occurring.

---

## Flink backpressure

A Flink job shows downstream backpressure.

Ask:

- What does backpressure mean?
- How would you identify the bottleneck?
- What would you inspect?
- How would you remediate it?

---

## Debezium connector problem

A PostgreSQL Debezium connector is stopped for several hours while writes continue.

Ask:

- What happens to WAL?
- What happens to the replication slot?
- What happens when the connector restarts?
- What operational risks exist?

---

## CDC correctness

A CDC stream contains:

```text
INSERT
UPDATE
UPDATE
DELETE
```

Ask the candidate to explain how those events should be applied to a lakehouse table.

Include:

- ordering
- primary keys
- tombstones
- idempotency
- MERGE
- deletes.

---

## Stateful stream recovery

A stateful processor crashes during processing.

Ask:

- What must be persisted?
- How are offsets and state related?
- How do checkpoints help?
- How would replay work?
- How do you prevent duplicate business effects?

---

## Schema compatibility incident

A new producer deployment causes old consumers to fail deserializing events.

Ask:

- What likely went wrong?
- What compatibility policy should have prevented it?
- How would you recover?
- How would you prevent recurrence?

---

## Order-payment stream join

Orders and payments arrive independently.

Requirements:

```text
orders and payments may arrive out of order
maximum expected delay = 15 minutes
```

Ask the candidate to design:

- keying
- state
- event time
- watermark
- join bounds
- unmatched-order handling
- state cleanup.

---

# 11. ADVANCED QUESTIONS — 31–40

Create exactly 10 Advanced questions.

These must simulate **Senior / Staff-level streaming architecture interviews**.

The candidate must reason across multiple Module 2.16 concepts.

Advanced questions should require:

- requirements clarification
- architecture
- correctness
- failure recovery
- scaling
- state
- event-time reasoning
- delivery guarantees
- schema evolution
- observability
- cost/performance trade-offs.

---

# 12. ADVANCED QUESTION 31 — REAL-TIME ORDER ANALYTICS PLATFORM

Design:

```text
Applications
     ↓
Events / CDC
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

Requirements:

- revenue every 5 minutes
- active sessions
- fraud-style alerts within seconds
- PostgreSQL CDC
- late events
- duplicate events
- schema evolution
- failure recovery
- continuously updated lakehouse.

Require the candidate to explain:

- topic design
- partition keys
- replication
- schemas
- delivery guarantees
- watermark strategy
- windows
- state
- Spark vs Flink
- CDC
- lag monitoring
- backpressure
- recovery.

---

# 13. ADVANCED QUESTION 32 — EXACTLY-ONCE CLAIM

An engineer says:

> "Our pipeline is exactly-once because Kafka supports exactly-once."

Challenge the statement.

Analyze:

```text
Producer
 ↓
Kafka
 ↓
Consumer
 ↓
PostgreSQL
 ↓
External API
```

Ask:

- Where are transactions?
- Where can duplicates occur?
- Where can events be lost?
- Where can side effects repeat?
- How would you achieve exactly-once business effect?
- What cannot realistically be exactly-once?

The solution must distinguish:

```text
delivery guarantee
vs
processing guarantee
vs
business-effect guarantee
vs
end-to-end guarantee
```

---

# 14. ADVANCED QUESTION 33 — POSTGRESQL CDC TO LAKEHOUSE

Design:

```text
PostgreSQL
 ↓
Debezium
 ↓
Kafka
 ↓
Spark/Flink
 ↓
Delta/Iceberg
```

Requirements:

- inserts
- updates
- deletes
- snapshots
- schema changes
- duplicate delivery
- ordering
- replay
- recovery.

Require discussion of:

- WAL
- logical decoding
- replication slots
- snapshots
- Debezium envelopes
- LSN
- transaction metadata
- tombstones
- Schema Registry
- idempotent MERGE
- reconciliation.

---

# 15. ADVANCED QUESTION 34 — FIVE-MINUTE FRAUD ALERT

Business requirement:

> Generate a fraud alert within 5 seconds.

Events can arrive:

- out of order
- duplicated
- up to 2 minutes late.

Require the candidate to design:

```text
Kafka
→ processing engine
→ state
→ alert
```

Discuss:

- event time
- processing time
- watermark
- state
- deduplication
- latency
- correctness vs freshness
- late-event policy.

---

# 16. ADVANCED QUESTION 35 — MASSIVE CONSUMER LAG INCIDENT

Production incident:

```text
Consumer lag ↑
One partition extremely hot
Sink latency ↑
Rebalances ↑
CPU ↑
Retention deadline approaching
```

Ask the candidate to conduct an incident investigation.

Require:

1. immediate mitigation;
2. root-cause analysis;
3. partition analysis;
4. consumer analysis;
5. sink analysis;
6. backpressure strategy;
7. scaling strategy;
8. retention-risk calculation;
9. alerting improvements;
10. long-term architecture improvements.

---

# 17. ADVANCED QUESTION 36 — SPARK VS FLINK

A company needs:

- Kafka input
- event-time processing
- large state
- low latency
- stateful joins
- exactly-once effects
- operational simplicity.

Ask:

> Would you choose Spark Structured Streaming or Flink?

Do not accept:

> "Flink is faster."

or:

> "Spark is easier."

Require a structured comparison of:

- execution model
- latency
- state
- checkpoints
- savepoints
- ecosystem
- Python/JVM implications
- operational model
- workload characteristics
- team expertise
- failure recovery
- cost.

---

# 18. ADVANCED QUESTION 37 — SCHEMA EVOLUTION AT SCALE

Scenario:

```text
Producer v1
Consumer v1
Consumer v2
Producer v2
```

must coexist during a rolling deployment.

Ask the candidate to design safe schema evolution using:

```text
Protobuf
Schema Registry
compatibility rules
CI validation
```

Require discussion of:

- backward compatibility
- forward compatibility
- full compatibility
- transitive compatibility
- field numbers
- reserved fields
- deployment order
- rollback.

---

# 19. ADVANCED QUESTION 38 — CAPACITY PLANNING

Given:

```text
Peak producer throughput = 500,000 events/sec
Average event size = 2 KB
Consumer throughput = 70,000 events/sec/consumer
Partition throughput = 50,000 events/sec
```

Ask the candidate to reason about:

- partition count
- consumer count
- headroom
- peak vs average
- hot partitions
- catch-up capacity
- retention
- scaling.

Require calculations.

Do not simply provide the final number.

Show the reasoning step by step.

---

# 20. ADVANCED QUESTION 39 — REPROCESSING A WEEK OF EVENTS

A production bug corrupted the downstream analytical results.

Kafka retains seven days of events.

Ask:

> How would you safely reprocess the previous seven days without corrupting current production results?

Discuss:

- consumer groups
- offset management
- replay
- separate output topics
- idempotent sinks
- event-time windows
- state rebuilding
- checkpoint handling
- backfills
- validation
- batch reconciliation
- cutover strategy.

---

# 21. ADVANCED QUESTION 40 — COMPLETE SENIOR ARCHITECTURE INTERVIEW

Create a complete senior-level system-design interview.

Scenario:

> Design a production-grade real-time order analytics platform for a global e-commerce company.

Requirements:

```text
Millions of events/minute
Multiple event producers
PostgreSQL CDC
Real-time revenue
Customer sessions
Fraud alerts
Late events
Duplicate events
Schema evolution
Replay
Seven-day Kafka retention
Lakehouse sink
Strict correctness requirements
Low-latency alerts
```

Require the candidate to design:

```text
Event producers
      ↓
Transactional outbox / CDC
      ↓
Kafka
      ↓
Schema Registry
      ↓
Stream processing
      ↓
State
      ↓
Analytics
      ↓
Lakehouse
```

Then require them to explain:

### Kafka

- topics
- partitions
- keys
- replication
- retention
- compaction.

### Producers

- acknowledgements
- idempotence
- retries
- batching.

### Consumers

- groups
- commits
- rebalances
- replay.

### Reliability

- at-most-once
- at-least-once
- exactly-once effect.

### Schemas

- Protobuf
- Schema Registry
- compatibility.

### Time

- event time
- watermarks
- late data.

### Windows

- tumbling
- sliding
- session.

### State

- keyed state
- deduplication
- joins
- TTL
- checkpoints.

### Processing engines

- Spark
- Flink
- decision rationale.

### CDC

- Debezium
- WAL
- replication slots
- snapshots
- deletes
- tombstones.

### Operations

- lag
- backpressure
- hot partitions
- retention cliff
- capacity.

### Verification

- replay
- chaos testing
- batch reconciliation
- correctness checks.

This must be the most comprehensive interview problem in the file.

---

# 22. INTERVIEW QUESTION TYPES

Across the 40 questions, deliberately include different interview styles.

Use:

```text
Conceptual
Scenario-based
Debugging
Coding
Calculation
Architecture
System design
Failure analysis
Trade-off analysis
Incident response
```

Do not make all 40 questions architecture questions.

---

# 23. QUESTION DISTRIBUTION

Aim approximately for:

```text
Conceptual reasoning       ~20%
Debugging                  ~15%
Coding / implementation    ~15%
Calculations               ~10%
Architecture               ~20%
Failure analysis           ~10%
Trade-offs                 ~10%
```

The exact percentages do not have to be mathematically exact, but the interview bank must be diverse.

---

# 24. CODING INTERVIEW QUESTIONS

Include several coding-oriented questions using the Module 2.16 ecosystem:

```text
Python
confluent-kafka
PySpark
PyFlink
SQL
Kafka configuration
Debezium configuration
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

Flink:

```python
key_by(...)
```

SQL:

```sql
MERGE ...
```

Do not turn the entire file into a coding interview.

Use code where it helps test practical streaming knowledge.

---

# 25. CALCULATION INTERVIEW QUESTIONS

Include questions requiring actual calculations.

Examples:

### Consumer lag

```text
Latest offset = 1,000,000
Committed offset = 850,000
```

Determine lag.

---

### Catch-up time

```text
Lag = 500,000 records
Producer rate = 100,000/sec
Consumer rate = 130,000/sec
```

Calculate net recovery rate and approximate catch-up time.

---

### Partition sizing

Given:

```text
Required throughput
Per-partition throughput
Peak multiplier
```

determine partition requirements.

---

### Window assignment

Given event timestamps, determine:

- tumbling window
- sliding window
- session membership.

---

### Watermark

Given:

```text
maximum event time
allowed lateness
```

calculate the watermark.

---

# 26. SENIOR INTERVIEW ANSWER STYLE

For Hard and Advanced questions, answers should model how a senior candidate communicates.

Use language such as:

> "Before choosing the technology, I would clarify the latency SLA, throughput, ordering requirements, correctness requirements, replay requirements, and failure tolerance."

Then reason through the architecture.

Avoid jumping immediately to:

> "Use Kafka + Flink."

A strong senior answer must first identify requirements and constraints.

---

# 27. REQUIRE TRADE-OFFS

Every Hard and Advanced question must include trade-offs.

Examples:

```text
More partitions
vs
ordering / operational cost

More consumers
vs
partition limit

Longer watermark
vs
correctness / latency

Shorter watermark
vs
late-event loss

Exactly-once
vs
complexity

Higher retention
vs
storage cost

Spark
vs
Flink

Compaction
vs
historical event retention

Batching
vs
latency

Scaling
vs
cost
```

The candidate must explain why one choice is preferred for the scenario.

---

# 28. COMMON WEAK ANSWERS

Every question should include:

```markdown
### Common Weak Answer
```

Examples:

> "Just add more consumers."

> "Kafka guarantees exactly-once."

> "Use Flink because it is real-time."

> "Use a watermark of five minutes because events are five minutes late."

> "Increase partitions."

> "Use Schema Registry."

These are not complete answers.

Explain why they are insufficient.

---

# 29. WHAT A SENIOR CANDIDATE SHOULD SAY

For each Hard and Advanced question, include:

```markdown
### What Distinguishes a Senior Answer?
```

Discuss characteristics such as:

- clarifying requirements
- identifying failure modes
- distinguishing guarantees
- understanding partition-level behavior
- considering state growth
- considering replay
- considering operational consequences
- measuring before optimizing
- discussing trade-offs
- defining observability
- planning recovery.

---

# 30. INTERVIEWER FOLLOW-UP QUESTIONS

For Hard and Advanced questions, include several realistic interviewer follow-ups.

Example:

```text
Interviewer:
What happens if the consumer crashes after writing to PostgreSQL?

Candidate:
...

Interviewer:
What if the same event is replayed?

Candidate:
...

Interviewer:
What if the sink is unavailable for 30 minutes?

Candidate:
...

Interviewer:
What if Kafka retention expires before recovery?

Candidate:
...
```

This should train the learner to handle interview probing.

---

# 31. FOLLOW-UP QUESTIONS MUST INCREASE DIFFICULTY

Do not make follow-ups repetitive.

Use a progression:

```text
Initial design
      ↓
Failure
      ↓
Scale
      ↓
Correctness
      ↓
Operational issue
      ↓
Trade-off
```

Example:

```text
How would you design it?
        ↓
What happens when a consumer crashes?
        ↓
What if traffic increases 10×?
        ↓
What if events arrive 20 minutes late?
        ↓
What if one key becomes extremely hot?
        ↓
How would you prove correctness?
```

---

# 32. COVER ALL 13 MODULE FILES

Across the 40 interview questions, ensure meaningful coverage of:

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

No topic should be ignored.

Do not make the interview file overwhelmingly Kafka-only.

---

# 33. REQUIRED COVERAGE MATRIX

Before finalizing the file, internally create a matrix:

| Topic | Basic | Moderate | Hard | Advanced |
|---|---:|---:|---:|---:|
| Streams vs queues | ✓ | ✓ | ✓ | ✓ |
| Kafka architecture | ✓ | ✓ | ✓ | ✓ |
| Producers | ✓ | ✓ | ✓ | ✓ |
| Consumers | ✓ | ✓ | ✓ | ✓ |
| Delivery semantics | ✓ | ✓ | ✓ | ✓ |
| Protobuf / Schema Registry | ✓ | ✓ | ✓ | ✓ |
| Event time / watermarks | ✓ | ✓ | ✓ | ✓ |
| Windows | ✓ | ✓ | ✓ | ✓ |
| Stateful processing | ✓ | ✓ | ✓ | ✓ |
| Spark | ✓ | ✓ | ✓ | ✓ |
| Flink | ✓ | ✓ | ✓ | ✓ |
| Debezium / CDC | ✓ | ✓ | ✓ | ✓ |
| Lag / backpressure | ✓ | ✓ | ✓ | ✓ |

The exact distribution does not have to put every topic into every difficulty level, but the overall 40-question bank must cover every topic thoroughly.

---

# 34. DO NOT DUPLICATE PRACTICE QUESTIONS BLINDLY

`practice-questions.md` and `interview-practice.md` serve different purposes.

Practice questions:

> Can the learner solve a technical problem?

Interview questions:

> Can the learner explain, reason about, defend, and communicate a technical solution under interview conditions?

Therefore, even if a concept appears in both files, the interview question should emphasize:

- verbal explanation
- interviewer interaction
- follow-up questions
- trade-offs
- architecture reasoning
- concise communication
- production judgment.

---

# 35. INTERVIEW COMMUNICATION TRAINING

Include a short section near the beginning:

# How to Answer Streaming Interview Questions

Teach the learner to use:

```text
1. Clarify requirements
2. State assumptions
3. Identify latency / throughput
4. Identify ordering requirements
5. Identify delivery guarantee
6. Design Kafka topics
7. Design processing
8. Design state
9. Discuss failure recovery
10. Discuss scaling
11. Discuss observability
12. Explain trade-offs
13. Summarize the decision
```

For system-design questions, encourage diagrams.

For debugging questions, encourage:

```text
symptom
→ hypothesis
→ metric
→ experiment
→ root cause
→ mitigation
→ permanent fix
```

---

# 36. INTERVIEW DIAGRAM REQUIREMENT

For architecture questions, use ASCII diagrams where useful.

Example:

```text
PostgreSQL
    |
    v
Debezium
    |
    v
Kafka
    |
    +------> Consumer A
    |
    +------> Spark
    |
    +------> Flink
    |
    v
Lakehouse
```

Explain each component.

Do not include diagrams merely for decoration.

---

# 37. PRODUCTION INCIDENT QUESTIONS

Include realistic incident scenarios.

Examples:

### Incident A

```text
Kafka lag suddenly increases.
```

### Incident B

```text
One partition has 10× the lag of every other partition.
```

### Incident C

```text
Debezium WAL grows rapidly.
```

### Incident D

```text
Spark streaming batches become progressively slower.
```

### Incident E

```text
Flink shows sustained backpressure.
```

### Incident F

```text
Consumers begin rebalancing repeatedly.
```

### Incident G

```text
Schema deployment breaks consumers.
```

For each, require:

```text
Diagnosis
Immediate mitigation
Root cause
Permanent fix
Monitoring improvement
```

---

# 38. CORRECTNESS MUST BE CENTRAL

Streaming interview answers must explicitly reason about correctness.

For relevant questions ask:

```text
Can events be lost?
Can events be duplicated?
Can events arrive out of order?
Can state be lost?
Can results be recomputed?
Can the sink be safely replayed?
What happens after restart?
```

This is particularly important for:

- delivery semantics
- stateful processing
- CDC
- Spark
- Flink
- consumer groups
- replay.

---

# 39. OBSERVABILITY MUST BE DISCUSSED

For Hard and Advanced architecture questions, require candidates to discuss relevant metrics.

Examples:

```text
Consumer lag
Lag growth rate
Time to catch up
Input rate
Processing rate
Batch duration
State size
Checkpoint duration
Checkpoint failures
Backpressure
Partition skew
Broker health
Under-replicated partitions
Connector status
Replication slot lag
WAL growth
End-to-end latency
```

Do not require every metric for every question.

Use only relevant metrics.

---

# 40. FINAL DOCUMENT STRUCTURE

Organize `interview-practice.md` approximately as:

```markdown
# Module 2.16 — Streaming and Event-Driven Data
# Interview Practice

## Purpose

## How to Use This Interview Guide

## How to Answer Streaming Interview Questions

## Interview Difficulty Model

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

# Final Topic Coverage

# Senior Interview Readiness Checklist

# Final Module 2.16 Interview Assessment
```

---

# 41. FINAL TOPIC COVERAGE CHECKLIST

At the end of the file, include:

```text
[ ] Event streams vs message queues
[ ] Events vs commands
[ ] Replay
[ ] Fan-out
[ ] Event-driven patterns
[ ] Kafka topics
[ ] Partitions
[ ] Offsets
[ ] Keys
[ ] Ordering
[ ] Replication
[ ] ISR
[ ] min.insync.replicas
[ ] Retention
[ ] Log compaction
[ ] Hot partitions
[ ] Kafka producers
[ ] acks
[ ] Idempotent producers
[ ] Retries
[ ] Batching
[ ] Compression
[ ] Partitioners
[ ] Kafka consumers
[ ] Consumer groups
[ ] Offset commits
[ ] Rebalances
[ ] Replay
[ ] Pause/resume
[ ] DLQ
[ ] At-most-once
[ ] At-least-once
[ ] Exactly-once
[ ] Kafka transactions
[ ] Idempotent sinks
[ ] Protobuf
[ ] Schema Registry
[ ] Compatibility
[ ] Schema evolution
[ ] Event time
[ ] Processing time
[ ] Watermarks
[ ] Late events
[ ] Tumbling windows
[ ] Sliding windows
[ ] Session windows
[ ] Triggers
[ ] Output modes
[ ] Stateful processing
[ ] Keyed state
[ ] Deduplication
[ ] Stream-static joins
[ ] Stream-stream joins
[ ] State TTL
[ ] State stores
[ ] Checkpointing
[ ] State recovery
[ ] Spark Structured Streaming
[ ] Spark checkpoints
[ ] Spark Kafka integration
[ ] Spark watermarks
[ ] Spark stateful processing
[ ] foreachBatch
[ ] maxOffsetsPerTrigger
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
[ ] Snapshots
[ ] CDC envelopes
[ ] LSN
[ ] Deletes
[ ] Tombstones
[ ] SMTs
[ ] Transactional outbox
[ ] CDC to Kafka
[ ] CDC to lakehouse
[ ] Consumer lag
[ ] Backpressure
[ ] Scaling consumers
[ ] Hot partitions
[ ] Retention cliff
[ ] Catch-up time
[ ] End-to-end latency
[ ] Latency SLOs
[ ] Capacity planning
```

---

# 42. FINAL SENIOR-LEVEL ASSESSMENT

End the file with a self-assessment:

```text
NOT READY
READY
SENIOR-READY
```

Define each level.

## NOT READY

The learner:

- memorizes definitions
- struggles to explain Kafka internals
- cannot reason about failures
- cannot explain delivery semantics
- cannot design streaming systems independently.

## READY

The learner can:

- explain Kafka
- explain consumers and producers
- explain event time
- explain windows
- explain state
- explain CDC
- explain Spark/Flink
- diagnose basic lag and backpressure
- answer moderate design questions.

## SENIOR-READY

The learner can:

- clarify ambiguous requirements
- design complete streaming architectures
- reason about correctness
- explain failure windows
- design delivery guarantees
- reason about state recovery
- design CDC pipelines
- diagnose production incidents
- calculate capacity
- reason about lag and retention
- compare Spark and Flink based on workload
- explain trade-offs
- design observability
- defend architecture decisions under interviewer follow-up.

---

# 43. FINAL QUALITY AUDIT

Before saving `interview-practice.md`, perform a strict audit.

## Count

```text
Basic      = exactly 10
Moderate   = exactly 10
Hard       = exactly 10
Advanced   = exactly 10

TOTAL      = exactly 40
```

## Every question

Must contain:

```text
Problem
↓
What interviewer is testing
↓
How to approach
↓
Strong solution
↓
Reasoning
↓
Trade-offs
↓
Common weak answer
↓
Senior insight
```

where appropriate.

## Difficulty

Verify that:

```text
Basic
    ↓
Moderate
    ↓
Hard
    ↓
Advanced
```

represents a genuine increase in engineering complexity.

## Coverage

Verify all 13 Module 2.16 topic files are represented.

## Interview quality

Verify the questions test:

- conceptual knowledge
- practical knowledge
- debugging
- coding
- calculations
- architecture
- system design
- failure analysis
- trade-offs
- production judgment.

## No unrelated topics

Every question must remain inside:

```text
16-Streaming-and-Event-Driven-Data/
```

## Senior-level reasoning

Hard and Advanced solutions must demonstrate:

```text
Requirements
→ Constraints
→ Correctness
→ Architecture
→ Failure handling
→ Scaling
→ Observability
→ Trade-offs
→ Final recommendation
```

---

# 44. FINAL FILE-SAFETY CHECK

Before saving:

```text
ONLY:
16-Streaming-and-Event-Driven-Data/interview-practice.md
```

may be modified.

Do NOT modify:

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

practice-questions.md
```

Do not create any additional files.

---

# 45. FINAL INSTRUCTION

Create a **production-grade 40-question interview preparation system** for Module 2.16.

The interview progression must be:

```text
Basic Concepts
      ↓
Kafka Fundamentals
      ↓
Producer / Consumer Reliability
      ↓
Delivery Guarantees
      ↓
Schema Management
      ↓
Event-Time Processing
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
Consumer Lag
      ↓
Production Incidents
      ↓
Senior Architecture
```

The goal is NOT to teach the learner how to memorize answers.

The goal is to teach the learner how to respond like a **Senior Data Engineer**:

```text
Understand the requirement
        ↓
Ask clarifying questions
        ↓
Identify constraints
        ↓
Design the architecture
        ↓
Reason about correctness
        ↓
Analyze failure modes
        ↓
Explain scaling
        ↓
Define observability
        ↓
Explain trade-offs
        ↓
Defend the decision
```

Every interview question must introduce a **real problem or scenario first**, followed by a detailed explanation of **how to solve and answer it**.

The final `interview-practice.md` must be something the learner can use for repeated interview preparation, mock interviews, senior-level reasoning practice, and production streaming-system design preparation.