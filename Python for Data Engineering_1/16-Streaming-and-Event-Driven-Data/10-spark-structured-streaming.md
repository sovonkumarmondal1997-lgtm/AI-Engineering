# ROLE

Act as a **Senior Data Engineer with 10+ years of production experience** designing large-scale data platforms, Apache Spark systems, Kafka pipelines, lakehouse architectures, and production streaming workloads.

You are also an expert technical educator.

Your task is to create a complete, self-contained learning chapter for:

`16-Streaming-and-Event-Driven-Data/10-spark-structured-streaming.md`

inside my **Python for Data Engineering — Stage 2** curriculum.

The goal is to teach me **Spark Structured Streaming from absolute foundations through production-grade implementation**, using simple explanations first and progressively introducing advanced concepts, architecture, failure recovery, state management, performance, monitoring, and operational trade-offs.

---

# AUTHORITATIVE SOURCE

The authoritative source for this file is the existing **Module 2.16 — Streaming and Event-Driven Data roadmap**.

Use the roadmap as the source of truth for the scope and sequence of this topic.

The roadmap specifically defines Topic 10 — Spark Structured Streaming around:

- the unbounded-table model
- `readStream`
- `writeStream`
- micro-batch execution
- Kafka ingestion
- `subscribe`
- `startingOffsets`
- Protobuf/Avro/JSON parsing
- triggers
- output modes
- checkpoints
- event-time processing
- watermarks
- windows
- session windows
- stateful aggregations
- `dropDuplicatesWithinWatermark`
- stream-static joins
- stream-stream joins
- Kafka sinks
- file sinks
- Delta/Iceberg sinks
- `foreachBatch`
- idempotent `MERGE`
- exactly-once processing
- arbitrary stateful processing APIs
- monitoring
- `lastProgress`
- input rate
- processing rate
- batch duration
- state size
- Structured Streaming UI
- `maxOffsetsPerTrigger`
- backpressure
- restart compatibility
- small-file problems
- compaction
- recent lower-latency execution modes

The roadmap's required hands-on exercise is also authoritative:

1. Read `orders` and `payments` from Kafka using Protobuf deserialization.
2. Compute 5-minute tumbling revenue per country with a 10-minute watermark.
3. Write that result to Kafka in update mode.
4. Deduplicate orders within the watermark.
5. Join orders with payments within 15 minutes.
6. Upsert deduplicated orders into an Iceberg or Delta `silver.orders` table using `foreachBatch` + `MERGE`.
7. Make the merge idempotent.
8. Kill the job repeatedly.
9. Prove the lakehouse table equals a batch recomputation from Kafka.
10. Run the same workload using `availableNow`.
11. Compare cost and latency.

Do not omit any of these requirements.

---

# CRITICAL FILE-SCOPE RULE

You are ONLY creating/updating:

`16-Streaming-and-Event-Driven-Data/10-spark-structured-streaming.md`

### DO NOT MODIFY ANY OTHER FILE.

Do not modify:

- `README.md`
- `01-event-streams-vs-message-queues.md`
- `02-kafka-topics-partitions-offsets-and-replication.md`
- `03-kafka-producers-in-python.md`
- `04-kafka-consumers-and-consumer-groups.md`
- `05-delivery-semantics-at-most-at-least-and-exactly-once.md`
- `06-protobuf-and-schema-registry.md`
- `07-event-time-processing-time-and-watermarks.md`
- `08-tumbling-sliding-and-session-windows.md`
- `09-stateful-stream-processing.md`
- `11-apache-flink-and-pyflink-overview.md`
- `12-debezium-cdc-streams-into-kafka.md`
- `13-backpressure-and-consumer-lag.md`
- `practice-questions.md`
- `interview-practice.md`

Do not create unrelated helper files.

Do not rename files.

Do not refactor the folder.

Do not update the roadmap.

**Only the target Markdown file may be modified.**

---

# PRIMARY LEARNING OBJECTIVE

Build a complete understanding of:

> **How Apache Spark Structured Streaming turns an unbounded stream of events into continuously processed DataFrame computations with fault tolerance, event-time semantics, state management, and production sinks.**

I should finish this chapter able to move from:

```text
"I know Spark DataFrames."
```

to:

```text
"I can design, implement, test, operate, monitor,
debug, recover, and optimize production Spark
Structured Streaming pipelines."
```

---

# TEACHING PHILOSOPHY

Teach from **simple → intermediate → advanced → production**.

Do not begin with a giant Spark code listing.

Build the mental model first.

For every major concept use this teaching pattern:

1. Problem
2. Simple explanation
3. Analogy
4. Technical definition
5. Small event example
6. Spark implementation
7. Expected behavior
8. Failure scenario
9. Production consideration
10. Common mistake
11. Knowledge checkpoint

Use realistic Data Engineering examples such as:

- orders
- payments
- customers
- clickstream
- revenue
- CDC
- fraud alerts
- operational events

---

# SECTION 1 — PREREQUISITES AND CONNECTION TO EARLIER MODULES

Start by explaining what this topic assumes.

The roadmap says this module builds on:

- Spark DataFrames
- Spark plans
- partitions
- Spark UI
- Kafka
- event time
- watermarks
- windows
- stateful processing
- Delta/Iceberg
- `MERGE`

Do not re-teach entire earlier modules.

Instead, provide a concise bridge:

```text
Kafka
  ↓
Structured Streaming
  ↓
DataFrame transformations
  ↓
State / windows / joins
  ↓
Sink
```

Explain how the previous topics map into Spark Structured Streaming.

Clearly distinguish:

```text
concept learned previously
```

from:

```text
how Spark implements that concept
```

---

# SECTION 2 — WHAT IS SPARK STRUCTURED STREAMING?

Start from the absolute basics.

Explain:

- What Apache Spark is.
- What Structured Streaming is.
- Why Spark needs a streaming API.
- Difference between batch DataFrames and streaming DataFrames.
- What an unbounded stream means.
- Why an infinite stream cannot simply be loaded into memory.
- How Spark processes an unbounded input incrementally.

Introduce the core mental model:

> A streaming DataFrame represents an unbounded table whose rows continuously arrive over time.

Show:

```text
Batch table:

row 1
row 2
row 3
...
row N
```

versus:

```text
Streaming table:

row 1
row 2
row 3
...
row N
row N+1
row N+2
...
forever
```

Explain why this model is powerful.

---

# SECTION 3 — BATCH VS STREAMING DATAFRAMES

Create a detailed comparison.

Compare:

| Concept | Batch | Structured Streaming |
|---|---|---|
| Input | bounded | unbounded |
| Execution | finite job | continuously triggered |
| Result | final table | continuously updated result |
| Failure handling | task/job retry | checkpoint + restart |
| State | temporary | potentially persistent |
| Watermarks | normally unnecessary | critical for event-time state |
| Output | final | incremental |
| Latency | minutes/hours | seconds/minutes |

Explain which Spark APIs remain familiar.

Show examples:

```python
batch_df = spark.read...
```

and:

```python
stream_df = spark.readStream...
```

Explain what is similar and what is fundamentally different.

---

# SECTION 4 — `readStream` AND `writeStream`

Teach the core API.

Start with:

```python
stream_df = (
    spark.readStream
    .format(...)
    ...
)
```

Then:

```python
query = (
    stream_df.writeStream
    ...
    .start()
)
```

Explain:

- `readStream`
- streaming DataFrame
- transformations
- `writeStream`
- streaming query
- query lifecycle

Show the full conceptual flow:

```text
Source
 ↓
readStream
 ↓
Streaming DataFrame
 ↓
Transformations
 ↓
writeStream
 ↓
Sink
 ↓
Running Query
```

Explain:

- `start()`
- `awaitTermination()`
- `stop()`

Use a minimal runnable example before introducing Kafka.

---

# SECTION 5 — MICRO-BATCH EXECUTION MODEL

Teach the most important execution concept.

Explain that Structured Streaming traditionally executes many streaming workloads using **micro-batches**.

Example:

```text
Events continuously arrive
        ↓
Batch 1
        ↓
Batch 2
        ↓
Batch 3
        ↓
Batch 4
        ↓
...
```

Explain:

- what a micro-batch is
- how Spark identifies new data
- how a batch is processed
- when output is committed
- how checkpoints fit into the process
- latency vs throughput trade-off

Use a timeline.

Example:

```text
10:00:00 ─ events arrive
10:00:05 ─ micro-batch 1
10:00:10 ─ micro-batch 2
10:00:15 ─ micro-batch 3
```

Explain why:

> Structured Streaming is not simply "Kafka consumer code written in Spark."

---

# SECTION 6 — KAFKA AS A STREAMING SOURCE

Teach Kafka integration in depth.

Show:

```python
df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "orders")
    .load()
)
```

Explain every part.

Cover:

- Kafka bootstrap servers
- topic subscription
- Kafka `key`
- Kafka `value`
- partition
- offset
- timestamp
- headers
- binary data returned by Kafka connector

Explain the relationship:

```text
Kafka record
     ↓
Spark row
     ↓
key
value
topic
partition
offset
timestamp
```

---

# SECTION 7 — `startingOffsets`

Teach:

```text
startingOffsets
```

carefully.

Explain:

- earliest
- latest
- JSON partition-specific offsets
- starting point vs ongoing checkpoint behavior

Most importantly explain:

> `startingOffsets` is not a substitute for checkpoint management.

Explain what happens after a restart with an existing checkpoint.

Discuss common mistakes.

---

# SECTION 8 — PARSING KAFKA DATA

Kafka values commonly arrive as bytes.

Teach how to convert:

```text
binary Kafka value
        ↓
structured Spark columns
```

Cover:

### JSON

```python
from_json(...)
```

### Avro

Explain the conceptual parsing process and relevant Spark support.

### Protobuf

Explain the architecture:

```text
Kafka
 ↓
serialized Protobuf bytes
 ↓
Spark deserialization
 ↓
structured columns
```

Use the Module 2.16 schema concepts, but do not re-teach the complete Protobuf/schema-registry topic.

Explain why schema-aware streaming is preferable to arbitrary JSON for production systems.

---

# SECTION 9 — TRIGGERS

Teach all roadmap-required trigger concepts.

## Default trigger

Explain:

> Process available data as fast as Spark can.

## Fixed interval

Show conceptually:

```python
.trigger(processingTime="10 seconds")
```

Explain:

- latency
- workload cadence
- idle periods
- scheduling implications

## `availableNow`

Teach carefully.

Explain:

> Process all data currently available and then stop.

Show why it is useful for:

- scheduled incremental processing
- backfills
- catch-up workloads
- replacing some periodic batch jobs

Compare:

```text
continuous streaming
```

vs:

```text
availableNow
```

Provide a decision table.

---

# SECTION 10 — OUTPUT MODES

Teach:

- append
- update
- complete

Use concrete examples.

### Append

Only new final rows.

### Update

Rows whose values changed.

### Complete

Entire result table.

Explain why not every output mode is valid for every query.

Show examples using aggregations.

Explain the relationship between:

```text
query semantics
+
watermarks
+
state
+
output mode
```

---

# SECTION 11 — CHECKPOINTING

Teach checkpointing deeply.

Explain why streaming queries need durable progress.

Explain that checkpoints track information needed to recover:

- source progress
- offsets
- state
- query progress

Use:

```python
.option("checkpointLocation", "/path/to/checkpoint")
```

Explain:

- checkpoint directory
- restart behavior
- recovery
- checkpoint isolation
- one query per checkpoint location
- why checkpoints should not casually be deleted
- why checkpoints should not be casually shared
- what happens when a checkpoint is lost

Use a crash/restart timeline.

---

# SECTION 12 — STREAMING QUERY RECOVERY

Build a complete example.

Timeline:

```text
Kafka
 ↓
Spark
 ↓
Batch 1
 ↓
Checkpoint
 ↓
Batch 2
 ↓
Batch 3
 ↓
CRASH
```

Then:

```text
Restart
 ↓
Read checkpoint
 ↓
Recover offsets/state
 ↓
Continue
```

Explain why recovery is different from simply starting another Spark job.

Demonstrate:

1. Start query.
2. Process events.
3. Stop.
4. Restart.
5. Inspect checkpoint.
6. Confirm processing resumes correctly.

---

# SECTION 13 — EVENT-TIME PROCESSING IN SPARK

Connect Topics 07–09 to Spark.

Teach:

- event timestamp
- processing time
- event time
- out-of-order events
- late events
- watermark

Use:

```python
.withWatermark("event_time", "10 minutes")
```

Explain exactly what this means.

Do not merely define it.

Use a timestamp timeline.

Explain:

```text
event time
watermark
window completion
state cleanup
late event
```

---

# SECTION 14 — WATERMARKS

Explain Spark watermarks in detail.

Use examples.

Example:

```text
latest observed event time = 12:20
allowed lateness = 10 minutes

watermark ≈ 12:10
```

Explain:

- why watermarks exist
- what they allow Spark to assume
- how state can eventually be cleaned
- why late events become increasingly difficult to incorporate
- what happens to records older than the watermark
- relationship to stateful aggregations and joins

Explain partition/source behavior at a conceptual level.

Discuss:

- delayed sources
- idle partitions
- skew
- incorrect timestamps

---

# SECTION 15 — WINDOWED AGGREGATIONS

Teach Spark window functions.

Start with:

```python
from pyspark.sql.functions import window
```

Then:

```python
groupBy(
    window("event_time", "5 minutes"),
    "country"
)
```

Explain every part.

Use the roadmap requirement:

> 5-minute tumbling revenue per country with a 10-minute watermark.

Implement it fully.

Show:

```text
events
 ↓
parse timestamp
 ↓
withWatermark
 ↓
window
 ↓
groupBy country
 ↓
sum revenue
 ↓
writeStream
```

Explain why the watermark must be applied to the correct event-time column.

---

# SECTION 16 — SESSION WINDOWS

Teach:

```python
session_window(...)
```

Explain:

- session semantics
- inactivity gap
- event-time sessions
- state implications
- late events
- session merging

Use clickstream/customer activity as the example.

Keep the explanation focused on Structured Streaming rather than re-teaching the entire session-window theory from Topic 08.

---

# SECTION 17 — STATEFUL AGGREGATIONS

Connect Spark's aggregation model to Topic 09.

Explain:

```text
groupBy
+
window
+
aggregation
=
state
```

Teach:

- state maintained between micro-batches
- state growth
- watermark-driven cleanup
- checkpointed state

Show examples:

- count per customer
- revenue per country
- windowed count
- running business metrics

Explain why a stateful query without an appropriate state boundary can become expensive.

---

# SECTION 18 — STREAMING DEDUPLICATION

Teach:

```text
dropDuplicatesWithinWatermark
```

in detail.

Explain:

- why duplicate events occur
- why streaming deduplication requires state
- event ID
- watermark
- state cleanup
- late duplicate
- memory implications

Use a realistic order stream.

Show:

```python
orders = (
    orders
    .withWatermark("event_time", "10 minutes")
    .dropDuplicatesWithinWatermark(["order_id"])
)
```

Explain the semantics carefully.

Compare conceptually:

```text
batch dropDuplicates
```

with:

```text
streaming deduplication with watermark
```

Explain why a bounded state design matters.

---

# SECTION 19 — STREAM-STATIC / STREAM-TABLE JOINS

Teach enrichment.

Example:

```text
orders stream
+
customers table
```

Output:

```text
order_id
customer_id
country
segment
amount
```

Explain:

- streaming side
- static/reference side
- lookup/enrichment
- state implications
- update behavior
- practical use cases

Do not duplicate the full Topic 09 theory; focus on how Spark Structured Streaming expresses it.

---

# SECTION 20 — STREAM-STREAM JOINS

Teach stream-stream joins in depth.

Use:

```text
orders
+
payments
```

with:

```text
order_id
+
time condition
```

Use the roadmap's:

> orders and payments within 15 minutes.

Explain:

- why both sides are streaming
- why both sides need buffering/state
- why a time condition is important
- how watermarks bound state
- late events
- unmatched records
- duplicate events
- state growth

Provide a Spark example.

Explain why an unconstrained stream-stream join can become operationally dangerous.

---

# SECTION 21 — SINKS

Teach the major streaming sinks in the roadmap.

Cover:

### Kafka

Explain:

```text
Spark → Kafka
```

### Files

Explain:

```text
Spark → files
```

Discuss practical considerations.

### Delta

Explain:

```text
Spark → Delta table
```

### Iceberg

Explain:

```text
Spark → Iceberg table
```

### `foreachBatch`

Explain why it exists.

Use:

```python
def process_batch(batch_df, batch_id):
    ...
```

Then:

```python
.writeStream.foreachBatch(process_batch)
```

Explain:

- micro-batch boundary
- batch DataFrame
- batch ID
- custom sink logic
- idempotency

---

# SECTION 22 — `foreachBatch` + `MERGE`

This is a critical production topic.

Teach:

```text
Kafka
 ↓
Structured Streaming
 ↓
micro-batch
 ↓
foreachBatch
 ↓
MERGE
 ↓
Delta/Iceberg
```

Implement an idempotent upsert.

Use a deterministic key such as:

```text
order_id
```

Explain:

- insert
- update
- duplicate batch execution
- retry
- batch ID
- deterministic merge key
- idempotency

Show why this is unsafe:

```text
blind INSERT
```

and why this is safer:

```text
MERGE
```

Explain how this relates to the exactly-once effect rather than claiming that `foreachBatch` automatically provides exactly-once behavior.

---

# SECTION 23 — EXACTLY-ONCE IN STRUCTURED STREAMING

Teach this very carefully.

The roadmap states the practical model:

> replayable sources + checkpoints + idempotent or transactional sinks.

Explain the complete chain:

```text
Replayable source
       +
Checkpoint
       +
Deterministic processing
       +
Idempotent/transactional sink
       =
Exactly-once effect
```

Distinguish:

```text
engine processing guarantees
```

from:

```text
end-to-end business effect
```

Explain failure scenarios:

### Failure A

Spark crashes before sink commit.

### Failure B

Spark crashes after sink commit but before progress is recorded.

### Failure C

Micro-batch is retried.

Explain why the sink must tolerate repeated execution.

---

# SECTION 24 — `availableNow` AS INCREMENTAL BATCH

Build a complete example.

Compare:

```text
continuous streaming
```

with:

```text
availableNow
```

Show how the same transformation can be used in both modes.

Discuss:

- latency
- cost
- operational simplicity
- scheduling
- catch-up
- bounded workloads
- freshness requirements

Then implement the roadmap's required comparison:

> Run the same workload with `availableNow` as a scheduled incremental batch and compare cost and latency.

---

# SECTION 25 — ARBITRARY STATEFUL PROCESSING

Introduce recent Spark APIs for arbitrary stateful processing.

The roadmap specifically requires awareness of recent:

```text
transformWithState-style APIs
```

including pandas-based variants where applicable.

Explain:

- why ordinary aggregations are sometimes insufficient
- arbitrary per-key state
- custom state transitions
- event-driven state machines
- pattern detection

Keep this at the required awareness/use-case level.

Do not turn this into an unrelated Spark API catalog.

Clearly distinguish:

```text
traditional aggregations
```

from:

```text
arbitrary stateful processing
```

---

# SECTION 26 — MONITORING STREAMING QUERIES

Teach production observability.

Cover:

```text
lastProgress
```

Explain what it tells us.

Monitor:

- input rate
- processing rate
- batch duration
- state size
- trigger execution
- batch progress
- source offsets
- sink progress
- processing delays

Explain the key diagnostic comparison:

```text
input rate
vs
processing rate
```

Example:

```text
Input rate:       50,000 events/sec
Processing rate:  20,000 events/sec
```

Explain why this is a problem.

---

# SECTION 27 — STRUCTURED STREAMING UI

Explain the Structured Streaming UI tab.

Teach what to inspect:

- active queries
- batches
- duration
- input rates
- processing rates
- state operators
- state size
- progress
- bottlenecks

Create a debugging workflow:

```text
Is input arriving?
        ↓
Is Spark processing it?
        ↓
Is processing rate sufficient?
        ↓
Is state growing?
        ↓
Is the sink slow?
        ↓
Are batches getting longer?
```

---

# SECTION 28 — BACKPRESSURE AND `maxOffsetsPerTrigger`

Introduce the roadmap's required rate-limiting mechanism:

```text
maxOffsetsPerTrigger
```

Explain:

> How much Kafka data Spark should attempt to process in one trigger.

Show an example.

Explain why consuming as much data as possible is not always optimal.

Discuss:

- downstream capacity
- batch duration
- latency
- catch-up
- lag
- throughput
- stability

Connect this topic forward to Module Topic 13 without fully re-teaching consumer lag.

---

# SECTION 29 — STREAMING QUERY PERFORMANCE

Teach practical performance considerations.

Cover:

- batch size
- trigger interval
- input rate
- state size
- shuffle
- partitioning
- joins
- serialization
- sink throughput
- file output
- small files
- checkpoint overhead

Explain how to reason about a slow streaming job.

Use:

```text
input
→ parse
→ transform
→ state/shuffle
→ sink
```

and identify where latency can accumulate.

---

# SECTION 30 — SMALL FILE PROBLEM

Teach why streaming writes can produce many small files.

Explain:

```text
many micro-batches
+
many partitions
=
many output files
```

Discuss:

- file count
- metadata overhead
- query performance
- downstream performance
- compaction
- trigger frequency
- partitioning choices

Connect this to Delta/Iceberg table maintenance from Module 2.15.

Do not re-teach full lakehouse table-format concepts.

Focus on:

> Why streaming workloads create small files and how production systems mitigate the problem.

---

# SECTION 31 — QUERY CHANGES AND CHECKPOINT COMPATIBILITY

This is an advanced production topic.

Teach:

> Not every modification to a streaming query can safely reuse an existing checkpoint.

Discuss conceptually:

### Usually safer changes

Examples of changes that generally do not invalidate the logical state in the same way.

### Potentially dangerous changes

- changing stateful operations
- changing grouping keys
- changing join structure
- changing state schema
- changing output mode
- changing source identity
- changing sink identity
- changing query topology

Explain that exact compatibility depends on the query and Spark version.

Teach the operational rule:

> Never delete a checkpoint simply because a changed query fails to restart.

Explain safe migration thinking:

```text
Existing query
+
existing checkpoint
+
new code
=
compatibility question
```

---

# SECTION 32 — FAILURE AND RECOVERY LAB

Create a hands-on experiment.

Run:

```text
Kafka
 ↓
Spark Structured Streaming
 ↓
checkpoint
 ↓
sink
```

Then:

1. Start the query.
2. Produce events.
3. Confirm progress.
4. Kill the Spark process.
5. Restart the query.
6. Inspect the checkpoint.
7. Confirm recovery.
8. Produce more events.
9. Verify results.
10. Repeat several times.

Explain what should remain consistent.

---

# SECTION 33 — MAIN HANDS-ON PROJECT

Build the roadmap's complete:

`src/streaming_lab/spark_streaming.py`

exercise.

The implementation must contain:

## Part 1 — Kafka ingestion

Read:

```text
orders
payments
```

from Kafka.

Use Protobuf deserialization.

Explain the schema.

---

## Part 2 — Revenue aggregation

Compute:

```text
5-minute tumbling revenue
per country
```

with:

```text
10-minute watermark
```

Write the result to Kafka using:

```text
update mode
```

---

## Part 3 — Order deduplication

Deduplicate orders within the watermark.

Use an appropriate event identifier.

Explain the state semantics.

---

## Part 4 — Order-payment join

Join:

```text
orders
+
payments
```

within:

```text
15 minutes
```

Explain the event-time constraint.

---

## Part 5 — Lakehouse sink

Use:

```text
foreachBatch
+
MERGE
```

to upsert into:

```text
silver.orders
```

Use:

```text
Delta
```

or:

```text
Iceberg
```

depending on the local lab setup.

Make the operation idempotent.

---

## Part 6 — Failure testing

Kill the Spark query repeatedly.

Restart it.

Verify:

```text
streaming result
==
batch recomputation
```

from Kafka.

---

## Part 7 — `availableNow`

Run the same transformation with:

```text
availableNow
```

Compare:

- latency
- throughput
- resource usage
- cost
- operational complexity

---

# SECTION 34 — BATCH RECOMPUTATION FOR VERIFICATION

This is mandatory.

Explain why streaming results should be verified against an independent batch computation.

Build a batch recomputation from the same Kafka event history.

Compare:

```text
Streaming output
vs
Batch output
```

Check:

- row counts
- revenue
- order counts
- duplicate handling
- join results
- missing records

Explain differences caused by:

- watermark boundaries
- intentionally dropped late data
- sink semantics
- duplicate handling
- incomplete event history

Do not assume equality without explaining the conditions under which equality should hold.

---

# SECTION 35 — TESTING STRATEGY

Teach testing of Structured Streaming.

Include:

### Unit-level tests

Test:

- parsing
- transformations
- event-time logic
- deduplication
- aggregation logic

### Streaming query tests

Test:

- micro-batches
- checkpoint recovery
- restart
- duplicate input
- late events

### Integration tests

Test:

```text
Kafka
+
Spark
+
sink
```

### Failure tests

Test:

- process crash
- restart
- repeated batch execution
- sink retry

### Reconciliation tests

Compare streaming output to batch recomputation.

---

# SECTION 36 — PRODUCTION OBSERVABILITY

Create an observability checklist.

Monitor at minimum:

```text
input rows/sec
processing rows/sec
batch duration
trigger interval
state size
checkpoint duration
checkpoint failures
query status
source lag/progress
sink latency
sink failures
late events
watermark
```

Explain what abnormal values mean.

Provide troubleshooting examples.

---

# SECTION 37 — PRODUCTION ARCHITECTURE

Create a complete architecture:

```text
                   Kafka
                     |
             Spark Structured
                Streaming
                     |
       +-------------+-------------+
       |             |             |
     Parse        Dedup          Join
       |             |             |
       +-------------+-------------+
                     |
              Event-time State
                     |
                Checkpoint
                     |
          +----------+----------+
          |                     |
       Kafka Sink          Lakehouse
                            Delta/Iceberg
                                |
                              MERGE
```

Explain each component.

---

# SECTION 38 — REAL-WORLD DESIGN DECISIONS

Teach how a senior engineer decides:

### When should I use Structured Streaming?

### When should I use `availableNow` instead?

### When should I use Kafka as the sink?

### When should I use Delta/Iceberg?

### When should I use `foreachBatch`?

### When should I use append vs update vs complete?

### How much watermark delay should I choose?

### How much state should I expect?

### How frequently should the query trigger?

### How much Kafka data should one trigger process?

For every decision provide:

```text
Requirement
→ Options
→ Trade-offs
→ Recommendation
```

---

# SECTION 39 — COMMON MISTAKES

Create a dedicated section.

Cover at least:

1. Treating a streaming DataFrame as a normal batch DataFrame.
2. Forgetting `checkpointLocation`.
3. Reusing one checkpoint for unrelated queries.
4. Deleting checkpoints to solve configuration problems.
5. Using an inappropriate output mode.
6. Missing watermarks on stateful queries.
7. Creating unbounded state.
8. Using stream-stream joins without time constraints.
9. Assuming `foreachBatch` automatically guarantees exactly-once.
10. Using non-idempotent `foreachBatch` logic.
11. Ignoring state size.
12. Ignoring input rate vs processing rate.
13. Setting triggers without understanding workload behavior.
14. Producing excessive small files.
15. Changing a stateful query without checking checkpoint compatibility.
16. Assuming `startingOffsets` controls every restart.
17. Using `availableNow` when true continuous freshness is required.
18. Assuming more partitions always improve performance.
19. Ignoring slow sinks.
20. Not testing kill/restart behavior.

For every mistake explain:

```text
Why it happens
→ What breaks
→ How to fix it
→ Production lesson
```

---

# SECTION 40 — PERFORMANCE DEBUGGING PLAYBOOK

Create a practical debugging framework.

If the query is slow:

```text
Step 1 → Check input rate
Step 2 → Check processing rate
Step 3 → Check batch duration
Step 4 → Check state size
Step 5 → Check shuffle
Step 6 → Check Kafka partitioning
Step 7 → Check sink throughput
Step 8 → Check checkpoint duration
Step 9 → Check small-file behavior
Step 10 → Check trigger configuration
```

For each step explain:

- what to inspect
- what abnormal behavior means
- likely causes
- corrective action

---

# SECTION 41 — ADVANCED STATEFUL APIs

Provide awareness of recent Spark arbitrary-state APIs.

Discuss:

- `transformWithState`-style APIs
- arbitrary per-key state
- custom state transitions
- timers where applicable
- state lifecycle
- pandas-based variants where applicable

Do not pretend every Spark version exposes identical APIs.

Explicitly state that:

> API availability and behavior are version-dependent and should be verified against the Spark version being used.

Keep this section focused on conceptual understanding and use cases.

---

# SECTION 42 — LOWER-LATENCY EXECUTION MODES

The roadmap requires awareness of recent lower-latency execution modes.

Explain conceptually:

- why micro-batch exists
- why lower latency may require different execution characteristics
- what lower-latency modes are trying to solve
- trade-offs

Do not turn this into a separate framework comparison.

Clearly distinguish:

```text
traditional micro-batch
```

from:

```text
newer lower-latency execution approaches
```

and explicitly note that exact availability/behavior is version-dependent.

---

# SECTION 43 — VERSION AWARENESS

The Module 2.16 roadmap warns that Spark 4.x introduces streaming changes.

Therefore:

- do not blindly reproduce outdated Spark tutorials
- distinguish stable concepts from version-specific APIs
- state which examples assume Spark 4.x where appropriate
- verify API behavior against the version being used
- do not silently assume Spark 3.x behavior
- clearly label version-sensitive functionality

The conceptual foundations must remain independent of a specific minor release.

---

# SECTION 44 — KNOWLEDGE CHECKPOINTS

After each major section provide questions.

Examples:

- What is an unbounded table?
- Why does Spark use `readStream`?
- What does `writeStream` create?
- What is a micro-batch?
- What does `startingOffsets` control?
- Why are Kafka values often parsed from binary?
- What is the difference between append and update?
- Why are checkpoints required?
- What does a watermark accomplish?
- Why does deduplication require state?
- Why do stream-stream joins require time bounds?
- What does `foreachBatch` provide?
- Why isn't `foreachBatch` automatically exactly-once?
- What does `availableNow` solve?
- Why can state grow indefinitely?
- What does `maxOffsetsPerTrigger` control?
- Why do streaming jobs produce small files?
- Which query changes may invalidate checkpoint reuse?
- How would you debug a query whose input rate exceeds processing rate?

Require reasoning, not memorized definitions.

---

# SECTION 45 — PROGRESSIVE CODING EXERCISES

Create exercises in four levels.

## Level 1 — Beginner

Build:

1. A streaming word/count example.
2. A simple Kafka reader.
3. A simple console sink.
4. A fixed trigger.

## Level 2 — Intermediate

Build:

1. Event-time aggregation.
2. Watermarked tumbling revenue.
3. Streaming deduplication.
4. Stream-static enrichment.
5. Stream-stream order/payment join.

## Level 3 — Advanced

Build:

1. `foreachBatch` + `MERGE`.
2. Idempotent lakehouse sink.
3. Checkpoint/restart recovery.
4. `availableNow` incremental pipeline.
5. Query monitoring.

## Level 4 — Production

Build:

1. Failure-injection test.
2. Streaming-vs-batch reconciliation.
3. State-growth monitoring.
4. Input-vs-processing-rate monitoring.
5. Small-file analysis.
6. Backpressure/rate-limiting experiment.
7. Restart compatibility experiment.

Every exercise must include:

```text
Problem
Requirements
Input
Expected output
Implementation
Explanation
Tests
Failure cases
Production lesson
```

---

# SECTION 46 — DESIGN CHALLENGES

Create at least 7 architecture/design challenges.

Examples:

### Challenge 1
Real-time order revenue.

### Challenge 2
Real-time fraud detection.

### Challenge 3
CDC ingestion into a lakehouse.

### Challenge 4
Customer activity sessionization.

### Challenge 5
Streaming deduplication at high volume.

### Challenge 6
Kafka-to-Delta incremental ingestion.

### Challenge 7
A Spark streaming job that is falling behind.

For every challenge require decisions about:

```text
source
schema
trigger
watermark
window
state
checkpoint
output mode
sink
idempotency
monitoring
failure recovery
```

Then provide a senior-engineer solution and trade-off discussion.

---

# SECTION 47 — SENIOR DATA ENGINEER INTERVIEW QUESTIONS

Include interview questions covering:

- Structured Streaming architecture
- unbounded table model
- micro-batch execution
- Kafka integration
- offsets
- triggers
- output modes
- checkpoints
- watermarks
- state
- deduplication
- joins
- `foreachBatch`
- exactly-once
- Delta/Iceberg sinks
- monitoring
- backpressure
- `maxOffsetsPerTrigger`
- small files
- query evolution
- recovery

Do not make these simple definition questions.

For design questions use:

```text
Problem
→ Constraints
→ Proposed architecture
→ Implementation
→ Failure modes
→ Trade-offs
→ Recommendation
```

---

# SECTION 48 — PRODUCTION FAILURE SCENARIOS

Create realistic scenarios.

### Scenario 1

The streaming query repeatedly restarts from an unexpected point.

Diagnose checkpoint/offset behavior.

### Scenario 2

State size increases every day.

Determine why.

### Scenario 3

The input rate is 100,000 events/sec but processing rate is 50,000 events/sec.

Explain the consequences and solutions.

### Scenario 4

A `foreachBatch` sink contains duplicate rows after retries.

Explain why and fix the design.

### Scenario 5

A streaming query cannot restart after changing its grouping key.

Explain checkpoint/state compatibility.

### Scenario 6

The lakehouse contains millions of tiny files.

Diagnose the streaming configuration and sink behavior.

### Scenario 7

A 15-minute order-payment join consumes excessive state.

Identify possible causes.

### Scenario 8

A developer deletes the checkpoint to make a query start.

Explain why this can be dangerous.

---

# SECTION 49 — FINAL CAPSTONE

Build a complete:

## Real-Time Order Analytics Pipeline

Architecture:

```text
Kafka
 |
 +---- orders
 |
 +---- payments
 |
 v
Spark Structured Streaming
 |
 +---- Protobuf parsing
 |
 +---- event-time processing
 |
 +---- 10-minute watermark
 |
 +---- order deduplication
 |
 +---- 5-minute revenue window
 |
 +---- order/payment join
 |
 +---- state
 |
 +---- checkpoint
 |
 +---- foreachBatch
 |
 v
Delta / Iceberg
 |
 silver.orders
 |
 analytics.revenue
```

The capstone must demonstrate:

1. Kafka ingestion.
2. Protobuf parsing.
3. Event-time processing.
4. 10-minute watermark.
5. 5-minute tumbling revenue by country.
6. Update output mode.
7. Streaming deduplication.
8. 15-minute stream-stream join.
9. Idempotent `foreachBatch`.
10. Delta/Iceberg `MERGE`.
11. Checkpoint recovery.
12. Repeated kill/restart.
13. Batch reconciliation.
14. `availableNow`.
15. Monitoring.
16. Backpressure/rate limiting.
17. State-size analysis.
18. Small-file analysis.

---

# SECTION 50 — FINAL BATCH RECONCILIATION

The capstone is not complete until the streaming result is compared with an independent batch computation.

Build a validation workflow:

```text
Kafka event history
        |
        +----------------+
        |                |
        v                v
Streaming           Batch
Spark               recomputation
        |                |
        v                v
Streaming result    Batch result
        |                |
        +-------+--------+
                |
             Compare
```

Compare:

- counts
- revenue
- orders
- payments
- deduplication
- joins
- missing events
- duplicates

Explain any differences.

---

# SECTION 51 — FINAL ASSESSMENT

Create a serious assessment.

## Basic — 10 questions

Test:

- streaming DataFrames
- `readStream`
- `writeStream`
- micro-batches
- Kafka source
- triggers
- output modes

## Intermediate — 10 questions

Test:

- checkpoints
- watermarks
- windows
- deduplication
- joins
- sinks

## Advanced — 10 questions

Test:

- state
- exactly-once
- `foreachBatch`
- idempotency
- performance
- monitoring
- backpressure
- checkpoint compatibility

## Senior / Production — 10 scenarios

Require diagnosis/design of:

- state explosion
- slow processing
- checkpoint failures
- duplicate outputs
- late events
- join state growth
- small files
- recovery
- query changes
- production scaling

Include coding questions.

Include architecture questions.

Include failure-analysis questions.

Do not make the assessment answerable through memorization alone.

---

# SECTION 52 — MASTERY CHECKLIST

Before declaring this topic complete, verify that I can independently:

- [ ] Explain the unbounded-table model.
- [ ] Explain batch vs streaming DataFrames.
- [ ] Use `readStream`.
- [ ] Use `writeStream`.
- [ ] Explain micro-batch execution.
- [ ] Read Kafka using Spark.
- [ ] Explain `subscribe`.
- [ ] Explain `startingOffsets`.
- [ ] Parse JSON.
- [ ] Explain Avro parsing.
- [ ] Parse Protobuf.
- [ ] Explain default triggers.
- [ ] Use fixed processing-time triggers.
- [ ] Use `availableNow`.
- [ ] Explain append mode.
- [ ] Explain update mode.
- [ ] Explain complete mode.
- [ ] Configure checkpoints.
- [ ] Explain recovery.
- [ ] Use event-time timestamps.
- [ ] Configure watermarks.
- [ ] Build tumbling windows.
- [ ] Build session windows.
- [ ] Build stateful aggregations.
- [ ] Perform streaming deduplication.
- [ ] Perform stream-static joins.
- [ ] Perform stream-stream joins.
- [ ] Bound join state.
- [ ] Write to Kafka.
- [ ] Write to files.
- [ ] Write to Delta/Iceberg.
- [ ] Use `foreachBatch`.
- [ ] Implement idempotent `MERGE`.
- [ ] Explain exactly-once effects.
- [ ] Use `lastProgress`.
- [ ] Interpret input vs processing rate.
- [ ] Monitor state size.
- [ ] Use `maxOffsetsPerTrigger`.
- [ ] Explain backpressure.
- [ ] Diagnose small files.
- [ ] Reason about checkpoint compatibility.
- [ ] Test kill/restart recovery.
- [ ] Reconcile streaming output against batch output.
- [ ] Explain recent arbitrary-state APIs.
- [ ] Explain lower-latency execution awareness.
- [ ] Understand version-sensitive behavior.

---

# FINAL DOCUMENT STRUCTURE

Produce a polished Markdown learning chapter with a structure similar to:

```text
# Spark Structured Streaming

## 1. Learning Objectives
## 2. Prerequisites and Connection to Earlier Topics
## 3. What Is Spark Structured Streaming?
## 4. Batch vs Streaming DataFrames
## 5. readStream and writeStream
## 6. Micro-Batch Execution Model
## 7. Kafka as a Streaming Source
## 8. startingOffsets
## 9. Parsing Kafka Data
## 10. Triggers
## 11. Output Modes
## 12. Checkpointing
## 13. Query Recovery
## 14. Event-Time Processing
## 15. Watermarks
## 16. Windowed Aggregations
## 17. Session Windows
## 18. Stateful Aggregations
## 19. Streaming Deduplication
## 20. Stream-Static Joins
## 21. Stream-Stream Joins
## 22. Streaming Sinks
## 23. foreachBatch
## 24. foreachBatch + MERGE
## 25. Exactly-Once Processing
## 26. availableNow
## 27. Arbitrary Stateful Processing
## 28. Monitoring
## 29. Structured Streaming UI
## 30. Backpressure and maxOffsetsPerTrigger
## 31. Performance Optimization
## 32. Small Files and Compaction
## 33. Query Changes and Checkpoint Compatibility
## 34. Failure and Recovery Lab
## 35. Main Hands-On Project
## 36. Batch Reconciliation
## 37. Testing Strategy
## 38. Production Observability
## 39. Production Architecture
## 40. Design Decisions
## 41. Common Mistakes
## 42. Performance Debugging Playbook
## 43. Advanced Stateful APIs
## 44. Lower-Latency Execution Modes
## 45. Version Awareness
## 46. Progressive Exercises
## 47. Design Challenges
## 48. Senior Interview Questions
## 49. Production Failure Scenarios
## 50. Final Capstone
## 51. Final Assessment
## 52. Mastery Checklist
```

You may improve the exact section ordering if needed for pedagogical flow, but **do not omit any roadmap concept**.

---

# CODING REQUIREMENTS

All important concepts must have coding examples.

Prefer:

```python
PySpark
```

because this is a Python-focused curriculum.

Use realistic code rather than toy-only examples.

Examples should cover:

- `SparkSession`
- `readStream`
- `writeStream`
- Kafka source
- parsing
- watermark
- window
- aggregation
- deduplication
- joins
- sinks
- checkpoint
- `foreachBatch`
- `MERGE`
- monitoring
- `availableNow`

For every important code block explain:

```text
What it does
Why it works
What assumptions it makes
What can fail
How production code differs
```

---

# PRODUCTION ENGINEERING REQUIREMENTS

Throughout the chapter, teach the engineering questions a senior Data Engineer should ask:

### Correctness

- Can events be duplicated?
- Can events arrive late?
- Can events arrive out of order?
- Can the job restart?
- Can a batch be retried?

### State

- How much state exists?
- How is it bounded?
- How is it checkpointed?
- How is it recovered?

### Performance

- What is the input rate?
- What is the processing rate?
- How long does each micro-batch take?
- Is the sink the bottleneck?
- Is state becoming too large?

### Reliability

- What happens if Kafka is unavailable?
- What happens if Spark crashes?
- What happens if the sink fails?
- What happens if a batch is retried?

### Operations

- What metrics should be monitored?
- What alerts should exist?
- How do we diagnose lag?
- How do we detect state growth?

### Evolution

- Can the query be safely changed?
- Can the checkpoint be reused?
- Does the state schema remain compatible?

---

# TEACHING RULES

Follow these rules throughout the chapter:

1. **Do not skip concepts from the roadmap.**
2. Explain simple concepts before advanced ones.
3. Never introduce an API without explaining the underlying problem.
4. Use event timelines.
5. Use architecture diagrams.
6. Use state diagrams.
7. Use tables for comparisons.
8. Use runnable Python examples where practical.
9. Explain every important parameter.
10. Include failure scenarios.
11. Include debugging strategies.
12. Include production trade-offs.
13. Include knowledge checkpoints.
14. Include hands-on exercises.
15. Include senior-level design scenarios.
16. Include a final capstone.
17. Include a final assessment.
18. Clearly distinguish educational examples from production implementations.
19. Do not silently assume framework behavior that is version-specific.
20. Keep this file focused on **Spark Structured Streaming**.

---

# IMPORTANT BOUNDARIES

Do not duplicate entire dedicated topics that come later.

For example:

- Do not turn this into a full Flink tutorial.
- Do not turn this into a full Debezium tutorial.
- Do not turn this into a full Kafka tutorial.
- Do not turn this into a full Delta/Iceberg tutorial.
- Do not turn this into a full backpressure/consumer-lag chapter.

Instead, explain how those concepts interact with Spark Structured Streaming where required by this roadmap.

The goal is:

> **Deep mastery of Spark Structured Streaming, not shallow coverage of every streaming technology.**

---

# FINAL FILE-SCOPE VERIFICATION

Before finishing, verify all of the following:

- [ ] Only `09...` was previously handled; now only `10-spark-structured-streaming.md` is modified.
- [ ] No other file in `16-Streaming-and-Event-Driven-Data/` was modified.
- [ ] No unrelated files were created.
- [ ] Every Topic 10 roadmap concept is covered.
- [ ] All concepts progress from basic to advanced.
- [ ] Kafka ingestion is implemented.
- [ ] Protobuf parsing is demonstrated.
- [ ] Triggers are explained.
- [ ] Output modes are explained.
- [ ] Checkpoints are explained and demonstrated.
- [ ] Event-time processing is demonstrated.
- [ ] Watermarks are demonstrated.
- [ ] Tumbling windows are implemented.
- [ ] Session windows are explained/implemented.
- [ ] Stateful aggregation is covered.
- [ ] `dropDuplicatesWithinWatermark` is covered.
- [ ] Stream-static joins are covered.
- [ ] Stream-stream joins are covered.
- [ ] Kafka/file/Delta/Iceberg sinks are covered.
- [ ] `foreachBatch` is implemented.
- [ ] `MERGE` is implemented idempotently.
- [ ] Exactly-once effects are explained correctly.
- [ ] Arbitrary stateful APIs are covered at the required awareness level.
- [ ] `lastProgress` is covered.
- [ ] Structured Streaming UI is covered.
- [ ] Input vs processing rate is covered.
- [ ] State size is covered.
- [ ] `maxOffsetsPerTrigger` is covered.
- [ ] Backpressure is connected to rate limiting.
- [ ] Small-file problems are covered.
- [ ] Checkpoint/query compatibility is covered.
- [ ] Kill/restart testing is included.
- [ ] Batch reconciliation is included.
- [ ] `availableNow` is implemented and compared.
- [ ] Version awareness is included.
- [ ] Progressive coding exercises are included.
- [ ] Senior design questions are included.
- [ ] Production failure scenarios are included.
- [ ] Final capstone is included.
- [ ] Final assessment is included.
- [ ] Mastery checklist is included.

The finished file must be capable of taking a learner from:

```text
"I know PySpark DataFrames."
```

to:

```text
"I can design, implement, test, monitor,
debug, recover, and optimize production-grade
Spark Structured Streaming pipelines."
```

Do not consider the work complete merely because the Markdown file has been written.

The **learning outcome** must be complete.