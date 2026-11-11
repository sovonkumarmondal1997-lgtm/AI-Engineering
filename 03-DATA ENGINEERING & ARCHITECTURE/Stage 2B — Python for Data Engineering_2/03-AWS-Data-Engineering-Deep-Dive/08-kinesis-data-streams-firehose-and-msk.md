# Kinesis Data Streams, Firehose, and MSK

> **G3 — AWS Data Engineering Deep Dive | Phase D | Topic 08**
>
> Production-oriented AWS streaming engineering module.
>
> **Scope:** AWS-specific implementation after the roadmap's Kafka/streaming foundations in Module 2.16. This module refreshes streaming concepts briefly, then focuses on Kinesis Data Streams, Amazon Data Firehose, Amazon MSK, MSK Connect, Managed Service for Apache Flink, Glue Schema Registry, reliability, security, performance, cost, observability, and production architecture.

---

## 0. Module Position, Objective, and Scope Boundary

This topic sits after the AWS service landscape, S3/S3 Tables, Glue Data Catalog, Glue ETL/Data Quality, Athena, Lake Formation, and Redshift. The goal is not to repeat an entire Kafka curriculum. Instead:

```text
Module 2.16
    ↓
Kafka / streaming foundations
    ↓
G3 Topic 08
    ↓
AWS-specific production implementation
```

The learner should finish able to:

- design a production streaming architecture on AWS
- produce and consume Kinesis records reliably
- reason about shards, partition keys, sequence numbers, retention, capacity, replay, and lag
- implement partial-failure-safe producers
- choose shared consumers, enhanced fan-out, KCL, or Lambda
- diagnose hot shards and consumer lag
- use Firehose for managed delivery and lake/warehouse ingestion
- configure dynamic S3 partitioning, Parquet conversion, Lambda transformation, and Iceberg delivery where supported
- run Kafka workloads on MSK with IAM authentication
- understand MSK Provisioned, MSK Serverless, MSK Connect, Debezium, S3 sinks, and Managed Service for Apache Flink
- govern event schemas with Glue Schema Registry
- choose Kinesis vs MSK vs Firehose from requirements rather than familiarity
- operate streaming systems with measurable reliability, security, performance, and cost controls.

### Prerequisite refresh

Know these terms from Module 2.16:

- event
- producer
- consumer
- topic/stream
- partition/shard
- ordering
- offset/sequence
- consumer group
- retention
- event time vs processing time
- at-least-once delivery
- idempotency.

Do not spend weeks relearning Kafka internals here.

---

# 1. AWS Streaming Architecture

A useful mental model is:

```text
                     Streaming Sources
                            |
                 -----------------------
                 |                     |
              Kinesis                  MSK
                 |                     |
                 |                   Kafka
                 |                     |
                 ------- Processing ----
                          |
               -----------------------
               |          |          |
            Lambda      Flink     Consumers
               |
            Firehose
               |
        -----------------
        |       |       |
       S3    Redshift  OpenSearch
       |
   Parquet / Iceberg
       |
 Athena / Lakehouse
```

### Component roles

| Component | Primary role |
|---|---|
| Kinesis Data Streams | AWS-native programmable event stream |
| Firehose | Managed delivery/ingestion service |
| MSK | Managed Apache Kafka platform |
| Lambda | Event-driven lightweight processing |
| KCL | Consumer coordination/checkpointing framework |
| Managed Service for Apache Flink | Stateful stream processing |
| MSK Connect | Managed Kafka Connect workers/connectors |
| Glue Schema Registry | Central schema contract/versioning |
| S3 | Durable lake landing |
| Iceberg | Transactional lakehouse table format |
| Redshift | Analytical warehouse |
| Athena | Serverless SQL over the lake |
| OpenSearch | Search/operational analytics destination |

### Engineering principle

Do not start with:

> "Which AWS service do I know?"

Start with:

```text
Requirements
↓
Latency
↓
Replay
↓
Processing complexity
↓
Ecosystem requirements
↓
Operational ownership
↓
Security
↓
Cost
↓
Service choice
```

---

# 2. Streaming Data Engineering Foundations

## 2.1 Event

An event records something that happened:

```json
{
  "event_id": "evt-1001",
  "event_type": "click",
  "user_id": "u-42",
  "event_ts": "2026-10-06T10:30:00Z"
}
```

## 2.2 Producer

The producer creates and publishes events.

## 2.3 Consumer

The consumer reads events and performs work.

## 2.4 Partitioning

Events are distributed across partitions/shards so multiple consumers can process data in parallel.

## 2.5 Ordering

Streaming systems usually guarantee ordering within a defined partition/shard boundary, not globally across the entire stream.

## 2.6 Retention and replay

Retention creates a recovery window:

```text
Event
 ↓
Retained
 ↓
Consumer failure
 ↓
Restart
 ↓
Replay available data
```

Replay is one reason a stream should not be treated as merely a transport pipe.

## 2.7 At-least-once delivery

A robust design assumes an event may be processed more than once.

Therefore:

```text
Reliable consumer
=
Retry
+
Idempotency
+
Checkpointing
+
Replay
+
Observability
```

Do not claim exactly-once semantics unless the specific service path and sink actually support the required guarantee.

---

# 3. Kinesis Data Streams Architecture

```text
Producer
   |
   v
Kinesis Data Stream
   |
   +---- Shard 1
   +---- Shard 2
   +---- Shard 3
   |
   v
Consumers
```

Core objects:

- stream
- record
- partition key
- shard
- sequence number
- retention
- consumer.

When a producer writes a record, Kinesis uses the partition key to determine the shard placement, stores the record in the stream, and returns metadata including a sequence number for successful writes.

---

# 4. Streams

A Kinesis Data Stream is the durable logical stream through which producers publish records and consumers read them.

Think of it as:

```text
logical stream
    =
ordered shard collections
    +
retention
    +
consumer access
```

A stream is not the same thing as a database table:

- records are immutable
- consumers track their own progress
- replay is possible while data remains retained
- downstream processing determines the business state.

### Operational questions

Before creating a stream, ask:

1. What is the expected event rate?
2. What is the peak rate?
3. How much replay is required?
4. How many independent consumers exist?
5. What ordering is required?
6. Is traffic stable or highly variable?
7. What is the cost ceiling?
8. Which downstream systems will consume it?

---

# 5. Shards

A shard is a unit of parallelism and capacity inside a Kinesis Data Stream.

Conceptually:

```text
Stream
 |
 +-- Shard A
 |     +-- ordered records
 |
 +-- Shard B
 |     +-- ordered records
 |
 +-- Shard C
       +-- ordered records
```

A shard affects:

- write capacity
- read capacity
- parallelism
- ordering scope
- scaling decisions
- hot-shard risk.

### Important

Do not memorize old shard limits from blog posts. AWS changes service capabilities and quotas. Verify current limits in the official Kinesis documentation before sizing or presenting an operational number.

---

# 6. Provisioned vs On-Demand Capacity

| Characteristic | Provisioned | On-Demand |
|---|---|---|
| Capacity model | Explicit stream capacity | AWS-managed capacity scaling |
| Capacity planning | Higher | Lower |
| Predictability | Strong for known workloads | Strong for variable workloads |
| Operational effort | Higher | Lower |
| Spiky traffic | Requires planning | Often a better fit |
| Stable traffic | Often attractive | Can still be appropriate |
| Cost decision | Capacity-driven | Usage/scaling-driven |
| Best starting point | Known steady workload | New/variable workload |

### Decision rule

Use provisioned capacity when you understand the workload and need explicit capacity management.

Use on-demand when traffic is variable, bursty, or still being characterized and reduced capacity-management overhead is valuable.

Always verify current quotas and pricing before deployment.

---

# 7. Partition Keys

The partition key is one of the most important design decisions.

Conceptually:

```text
Partition Key
      ↓
   Hashing
      ↓
Shard Selection
```

Common candidates:

- `user_id`
- `customer_id`
- `device_id`
- `tenant_id`
- order/account identifiers.

### Good key characteristics

A good partition key usually has:

- sufficient cardinality
- reasonably balanced frequency
- stable semantics
- an ordering requirement that matches the key.

### Example

Suppose:

```text
80% of traffic:
country = "IN"
```

Using:

```text
partition_key = country
```

can concentrate traffic.

Using:

```text
partition_key = user_id
```

usually distributes better when users are numerous and traffic is reasonably balanced.

### Trade-off

Changing the key can improve distribution but change ordering semantics.

You must answer:

> What must be ordered, and what can be processed independently?

---

# 8. Sequence Numbers

A successful Kinesis write returns a sequence number.

Compare:

```text
Partition Key
=
routing / ordering-domain input
```

with:

```text
Sequence Number
=
service-assigned record position identifier
```

Sequence numbers matter for:

- consumer progress
- checkpoints
- replay
- debugging
- identifying successful writes.

Do not treat a sequence number as a globally meaningful business event ID.

Use an application-level `event_id` for business idempotency.

---

# 9. Retention

Retention determines how long records remain available for consumers.

Retention supports:

- replay
- delayed consumers
- incident recovery
- backfills
- debugging
- recovery after downstream outages.

### Recovery reasoning

```text
Consumer failure
↓
How long until recovery?
↓
How far behind are we?
↓
Is retained data still available?
↓
Can the consumer catch up?
```

Longer retention can increase recovery options and may increase cost. Verify current retention ranges and pricing before production sizing.

---

# 10. Kinesis Producer Architecture

A production producer should look like:

```text
Application
   |
Validate event
   |
Assign event_id / timestamp
   |
Choose partition key
   |
Serialize
   |
Batch
   |
PutRecords
   |
Inspect per-record results
   |
Retry only failures
   |
Metrics + logs
```

The producer should not treat a successful HTTP/API response as proof that every record succeeded.

---

# 11. boto3 `PutRecords`

Basic example:

```python
import boto3

kinesis = boto3.client("kinesis")

response = kinesis.put_records(
    StreamName="click-events",
    Records=[
        {
            "Data": b'{"user_id":"u1","event":"click"}',
            "PartitionKey": "u1",
        },
        {
            "Data": b'{"user_id":"u2","event":"view"}',
            "PartitionKey": "u2",
        },
    ],
)

print(response)
```

`PutRecords` sends multiple records in one request. The response contains a result entry corresponding to each submitted record, including success metadata or an error for a failed record. AWS documents a current maximum of 500 records per request and a total request payload limit; verify current API limits before production tuning. citeturn1search3

### Important ordering caveat

`PutRecords` processes records independently. A failed record does not stop subsequent records, so the API does not guarantee that records in the request are written in the same ordering you submitted them. If strict ordering is required, design around the relevant ordering boundary rather than assuming batch submission provides global ordering. citeturn1search3

---

# 12. Partial `PutRecords` Failures

This is a mandatory production concept.

Example:

```text
Batch:
A → success
B → failure
C → success
D → failure
```

The API call can return HTTP success while individual records fail.

Inspect:

- `FailedRecordCount`
- response entry position
- `ErrorCode`
- `ErrorMessage`
- successful `ShardId`
- successful `SequenceNumber`.

### Correct retry algorithm

```text
Send batch
   ↓
Inspect response
   ↓
Failed records?
   ├── No → done
   └── Yes
         ↓
     Extract only failures
         ↓
     Backoff + jitter
         ↓
     Retry failures
         ↓
     Repeat with bounded attempts
```

### Do not do this

```python
# Bad pattern:
while failed:
    kinesis.put_records(Records=original_batch)
```

That can duplicate records that already succeeded.

### Better pattern

```python
import json
import random
import time
import boto3

kinesis = boto3.client("kinesis")


def put_records_with_retry(stream_name, events, max_attempts=5):
    pending = [
        {
            "Data": json.dumps(event).encode("utf-8"),
            "PartitionKey": event["user_id"],
        }
        for event in events
    ]

    for attempt in range(max_attempts):
        if not pending:
            return

        response = kinesis.put_records(
            StreamName=stream_name,
            Records=pending,
        )

        failed = []
        for record, result in zip(pending, response["Records"]):
            if "ErrorCode" in result:
                failed.append(record)

        if not failed:
            return

        pending = failed

        sleep_seconds = min(30, 2 ** attempt) + random.random()
        time.sleep(sleep_seconds)

    raise RuntimeError(
        f"{len(pending)} records still failed after {max_attempts} attempts"
    )
```

Production improvements should add:

- structured logging
- metrics
- bounded retry duration
- alerting
- poison/error handling
- request correlation
- application event IDs.

AWS's API documentation explicitly describes partial success and recommends handling unsuccessful records rather than assuming the whole request failed. citeturn1search3

---

# 13. Reliable Producer Design

A production producer should include:

- validation
- deterministic partition-key logic
- event IDs
- timestamps
- batching
- bounded retries
- exponential backoff
- jitter
- throttling awareness
- structured logs
- metrics
- failure accounting
- idempotency strategy at downstream consumers.

### Producer metrics

Track:

```text
records_sent
records_failed
records_retried
retry_exhausted
bytes_sent
throttles
latency
```

### Failure policy

Do not retry forever.

After a bounded retry budget:

```text
Retry exhausted
↓
Failure queue/store/log
↓
Alert
↓
Investigate
↓
Replay after remediation
```

---

# 14. Kinesis Consumers

Conceptual flow:

```text
Stream
 ↓
Shard
 ↓
Consumer
 ↓
Records
 ↓
Processing
 ↓
Checkpoint
```

Consumer concepts:

- shard iterator
- polling
- records
- checkpoint
- replay
- worker ownership.

A consumer must make an explicit choice about where its progress state lives and how it recovers.

---

# 15. Shared Consumers

With shared consumption, consumers share the read path associated with the stream.

This can be sufficient when:

- consumer count is modest
- throughput requirements are moderate
- latency requirements are not extremely strict
- cost simplicity matters.

Multiple consumers can compete for shared read throughput. If several independent applications require isolated, low-latency reads, evaluate enhanced fan-out.

---

# 16. Enhanced Fan-Out

Conceptually:

```text
Kinesis Stream
     |
 -------------------------
 |          |            |
Consumer A Consumer B Consumer C
```

Enhanced fan-out gives registered consumers a dedicated read-throughput path rather than forcing all consumers to share the same read throughput.

Evaluate it when:

- several independent consumers exist
- consumer latency matters
- read contention is a problem
- isolation is valuable.

Trade-offs include additional service configuration and cost.

---

# 17. Kinesis Client Library (KCL)

KCL is a consumer coordination library.

It helps with:

- shard discovery
- worker coordination
- load balancing
- checkpointing
- failover
- lease management.

Mental model:

```text
              KCL workers
              /        \
             /          \
         Shard A      Shard B
             \          /
              \        /
          checkpoint/lease state
                 |
              DynamoDB
```

KCL turns low-level shard coordination into a managed application pattern.

---

# 18. Checkpoints and DynamoDB Leases

A checkpoint records consumer progress.

A lease records worker ownership/coordination state.

Failure example:

```text
Worker A
   ↓
Shard 1
   ↓
Checkpoint
   ↓
Worker A crashes
   ↓
Worker B acquires work
   ↓
Worker B resumes from checkpoint
```

Checkpointing is not the same as exactly-once processing.

If a consumer crashes after processing an event but before checkpointing, the event may be processed again.

Therefore:

```text
checkpointing
+
idempotent processing
=
robust recovery
```

---

# 19. Lambda Consumers

Typical architecture:

```text
Kinesis
   ↓
Lambda Event Source Mapping
   ↓
Lambda Function
   ↓
Business Logic
```

Lambda abstracts much of the polling machinery.

Key controls include:

- batch size
- batching window
- concurrency
- retry behavior
- partial batch failure behavior
- bisecting on error
- failure destinations
- monitoring.

---

# 20. Lambda Batching

Batching creates a latency/throughput trade-off.

```text
Small batch
→ lower waiting latency
→ more invocations
→ potentially higher overhead

Large batch
→ higher efficiency
→ fewer invocations
→ larger failure blast radius
```

Tune from measurements rather than intuition.

Test:

1. event rate
2. processing duration
3. batch size
4. batching window
5. concurrency
6. iterator age
7. downstream capacity.

---

# 21. Error Handling and Bisecting

A poison record can repeatedly fail a batch.

Conceptually:

```text
Batch of 16 fails
       ↓
Split
       ↓
8 + 8
       ↓
Failing half
       ↓
4 + 4
       ↓
...
       ↓
Poison record isolated
```

Bisecting can reduce the search space for a bad record.

But it is not a substitute for:

- validation
- dead-letter/failure handling
- observability
- replay strategy.

---

# 22. Failure Destinations

A robust failure path:

```text
Kinesis
   ↓
Lambda
   ↓
Processing failure
   ↓
Retry
   ↓
Bisect if configured
   ↓
Failure destination
   ↓
Investigation
   ↓
Fix
   ↓
Replay
```

Failure records should preserve enough context to identify:

- source stream
- shard/sequence context where available
- event ID
- failure reason
- timestamp
- application version.

---

# 23. Hot Shards

A hot shard occurs when the partition-key distribution concentrates too much traffic onto a shard.

```text
Bad partition key
      ↓
Traffic concentration
      ↓
Hot shard
      ↓
Throttling
      ↓
Producer retries
      ↓
Latency increases
      ↓
Consumer lag can increase
```

### Example

Bad:

```text
partition_key = country
```

if:

```text
IN = 80%
US = 10%
GB = 5%
Other = 5%
```

Better candidate:

```text
partition_key = user_id
```

when the business ordering requirement permits it.

### Key-design test

Ask:

1. How many unique keys exist?
2. How frequently does each key occur?
3. Does one tenant dominate?
4. What ordering must be preserved?
5. Can a key be salted?
6. Can traffic be split by a higher-cardinality identifier?

---

# 24. Partition-Key Design

A partition key should satisfy two competing requirements:

```text
Business ordering
        +
Load distribution
```

### Example

You require per-customer ordering.

Possible:

```text
partition_key = customer_id
```

If one customer is extremely large, consider whether:

- that customer can be isolated
- ordering can be scoped differently
- a controlled suffix can be introduced
- downstream reconstruction is acceptable.

Do not blindly add random salting when strict per-key ordering is required.

---

# 25. Resharding and Capacity

When workload growth causes capacity pressure, possible actions include:

- redesigning partition keys
- increasing capacity
- resharding where applicable
- reducing producer bursts
- optimizing consumers
- reducing downstream bottlenecks.

Use evidence:

```text
Metric
↓
Affected shard
↓
Traffic distribution
↓
Producer behavior
↓
Consumer behavior
↓
Capacity change
↓
Re-measure
```

Capacity scaling is not a substitute for a bad partition key.

---

# 26. Firehose Fundamentals

Amazon Data Firehose is a managed delivery service.

Mental model:

```text
Streaming Source
      ↓
   Firehose
      ↓
    Buffer
      ↓
 Destination
```

Use Firehose when the dominant problem is:

> "Reliably deliver streaming data to a supported destination with little custom infrastructure."

Do not treat Firehose as a general-purpose stream-processing engine.

---

# 27. Firehose Destinations

This roadmap focuses on:

- Amazon S3
- Amazon Redshift
- Amazon OpenSearch Service
- Apache Iceberg destinations where supported.

The exact destination feature set evolves, so verify current documentation before designing around a specific integration.

---

# 28. Firehose Buffering

Firehose buffers records before delivery.

Conceptual trade-off:

```text
Smaller buffer
→ lower latency
→ smaller output objects
→ potentially more object overhead

Larger buffer
→ higher delivery latency
→ larger output objects
→ often better lake efficiency
```

Buffering is therefore a data-lake design decision, not merely a transport setting.

Consider:

- target latency
- object size
- downstream query efficiency
- partition cardinality
- destination limits
- cost.

Do not hard-code old buffer limits without checking current documentation.

---

# 29. Firehose to S3

Common architecture:

```text
Kinesis Data Streams
        ↓
     Firehose
        ↓
       S3
        ↓
     Athena
```

Production configuration should consider:

- S3 prefix design
- error prefix
- compression
- buffering
- encryption
- IAM role
- object naming
- schema
- downstream partition pruning.

Firehose supports S3 delivery and S3-side encryption options including SSE-KMS. citeturn1search12

---

# 30. Firehose Dynamic Partitioning

Dynamic partitioning groups records by keys from the data and delivers them to corresponding S3 prefixes.

Example:

```text
Incoming events
      ↓
Dynamic partitioning
      ↓
date=2026-10-06/
event_type=click/
```

A useful target layout might be:

```text
s3://lake/events/
  event_date=2026-10-06/
    event_type=click/
```

Dynamic partitioning can reduce data scanned by Athena and other S3 analytics engines by organizing records into query-relevant prefixes. citeturn0search2

### Important operational constraints

Dynamic partitioning:

- is configured when creating the Firehose stream
- currently supports S3 destinations
- cannot simply be switched off after enabling it on that stream
- must be designed carefully to avoid partition explosion and tiny files. citeturn0search3turn0search11

### Partition explosion

Bad:

```text
partition = user_id
```

for millions of users with sparse traffic.

This can create many small datasets and poor lake efficiency.

Better:

```text
date + bounded business dimension
```

when the query workload supports it.

---

# 31. Firehose Format Conversion

Firehose can convert JSON input to:

- Apache Parquet
- Apache ORC

before writing to S3.

Why Parquet?

- columnar
- compressed
- efficient predicate/column projection
- suitable for Athena and lake analytics.

AWS requires a deserializer, a schema, and a serializer for format conversion. The schema is sourced from AWS Glue Data Catalog. citeturn1search0turn1search5

---

# 32. Glue Schema for Parquet Conversion

Architecture:

```text
JSON events
    ↓
Firehose
    ↓
Glue Data Catalog schema
    ↓
Parquet serializer
    ↓
S3
```

The Glue schema must match the input structure closely enough for the conversion to succeed.

Common failure:

```text
Producer schema
      ≠
Glue schema
      ↓
Conversion failure / missing attributes
```

AWS specifically notes that schema mismatch can cause attributes not represented in the Glue schema to be absent from converted output. citeturn1search0

### Scope connection

Topic 03 already teaches Glue Data Catalog. Here focus on:

- using the schema
- conversion behavior
- compatibility
- failure diagnosis.

Do not duplicate the complete Glue Catalog curriculum.

---

# 33. Lambda Record Transformation

Architecture:

```text
Kinesis
   ↓
Firehose
   ↓
Lambda transformation
   ↓
Firehose
   ↓
S3
```

Good uses:

- normalization
- field renaming
- lightweight filtering
- adding derived fields
- converting non-JSON input to JSON before format conversion.

Firehose supports Lambda transformation before delivery. citeturn1search2

### When Lambda becomes the wrong tool

Prefer a more capable stream processor when you need:

- complex state
- large joins
- event-time windows
- long-running state
- sophisticated enrichment
- large-scale aggregations.

That is where Managed Service for Apache Flink becomes relevant.

---

# 34. Firehose to Iceberg

Firehose can deliver streaming data to Apache Iceberg tables in Amazon S3 and can route records from one stream to different Iceberg tables. AWS documentation also describes support for insert, update, and delete operations and Lake Formation fine-grained controls for supported Iceberg configurations. citeturn0search10

Architecture:

```text
Streaming Source
      ↓
    Firehose
      ↓
Iceberg Table(s)
      ↓
Athena / Spark / Flink / Redshift integrations
```

Important considerations:

- catalog configuration
- table routing
- schema
- partition strategy
- operation semantics
- Lake Formation governance
- table maintenance
- replay/recovery
- current feature limitations.

For self-managed Iceberg tables, you remain responsible for table maintenance such as compaction and snapshot expiration. S3 Tables provide a more managed storage experience. citeturn0search10

### Exact configuration safety

Verify current Firehose Iceberg destination configuration before applying Terraform or API examples; this integration is more volatile than basic S3 delivery.

---

# 35. Firehose to Redshift

Conceptual flow:

```text
Kinesis
   ↓
Firehose
   ↓
Redshift
   ↓
Analytics
```

Use Firehose when:

- delivery is straightforward
- buffering is acceptable
- you want a managed ingestion path
- the destination fits Firehose's supported model.

Compare with direct streaming ingestion when:

- latency requirements are tighter
- warehouse-native streaming capabilities are preferable
- custom processing is required.

Topic 07 covers the Redshift architecture and performance side.

---

# 36. Firehose to OpenSearch

OpenSearch is useful for:

- operational search
- logs
- near-real-time exploration
- text-oriented analytics
- observability-style workloads.

Do not use OpenSearch as a replacement for:

- the durable lake
- the analytical warehouse
- a general-purpose event stream.

---

# 37. Iterator Age and Consumer Lag

For Kinesis consumers, iterator age is a critical operational signal.

Mental model:

```text
Producer rate
     ↓
Consumer processing rate
     ↓
Lag
     ↓
Iterator Age
```

### Healthy trend

```text
Low and stable
```

### Dangerous trend

```text
Increasing continuously
```

### Incident example

> Iterator age increases continuously for one shard.

Investigate:

1. Is the producer traffic skewed?
2. Is one shard hot?
3. Is the consumer slower than normal?
4. Did downstream latency increase?
5. Did Lambda concurrency change?
6. Is the consumer throttled?
7. Did record size increase?
8. Is one event causing repeated failures?

Never treat iterator age as merely a dashboard number. It is evidence of a growing recovery problem.

---

# 38. MSK Fundamentals

Refresh Kafka:

```text
Producer
   ↓
Kafka Topic
   ↓
Partitions
   ↓
Consumer Group
```

Amazon MSK is a managed Apache Kafka service.

AWS manages substantial infrastructure, but your team still owns important decisions around:

- topics
- partitioning
- replication strategy
- clients
- consumer groups
- schema
- application behavior
- networking
- IAM/authorization
- capacity and cost.

---

# 39. MSK Provisioned

Provisioned MSK gives you a managed Kafka cluster model with brokers and explicit infrastructure choices.

Think about:

- broker type
- broker count
- storage
- partitions
- replication
- networking
- scaling
- configuration
- monitoring.

AWS provides different broker options and configuration capabilities; verify current supported broker configurations before sizing a new cluster. citeturn1search8

### Operational responsibility

Managed Kafka is still Kafka.

You must monitor:

- broker health
- storage
- CPU
- network
- partition distribution
- replication
- consumer lag
- application behavior.

---

# 40. MSK Serverless

MSK Serverless provides a serverless Kafka operating model.

Use it when:

- you want less infrastructure management
- traffic is variable
- Kafka compatibility is important
- the workload fits service constraints.

Compare:

| Dimension | MSK Provisioned | MSK Serverless |
|---|---|---|
| Infrastructure management | More | Less |
| Capacity model | Explicit | Service-managed |
| Kafka ecosystem | Yes | Yes, subject to supported capabilities |
| Control | Higher | Lower |
| Operational burden | Higher | Lower |
| Cost model | Infrastructure/usage dependent | Usage-oriented |
| Best fit | Predictable/control-heavy workloads | Variable/simpler workloads |

Do not assume "serverless" means unlimited. Verify current quotas, supported features, and pricing before production use.

---

# 41. MSK Networking

MSK is a networked platform, so connectivity is part of application correctness.

Consider:

- VPC
- subnets
- security groups
- routing
- DNS
- private connectivity
- client placement
- cross-account/network architecture where required.

Troubleshooting order:

```text
DNS
↓
Route
↓
Security Group
↓
TLS
↓
Authentication
↓
Authorization
↓
Kafka protocol
```

Do not jump to IAM if the client cannot establish network connectivity.

---

# 42. IAM Authentication for MSK

Conceptually:

```text
Kafka Client
    ↓
IAM Authentication
    ↓
MSK
    ↓
IAM authorization
```

IAM authentication can provide identity and fine-grained authorization using AWS IAM policies. AWS recommends IAM role-based authentication for applications already running in AWS. citeturn1search9

A current client configuration example documented by AWS uses:

```properties
security.protocol=SASL_SSL
sasl.mechanism=AWS_MSK_IAM
sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;
sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler
```

The exact client library/JAR version must be selected from current AWS MSK IAM authentication documentation. citeturn1search14

### Security principle

Prefer:

```text
IAM role
+
least-privilege Kafka permissions
+
TLS
```

over embedding long-lived credentials in applications.

---

# 43. Kafka Clients on MSK

The practical goal is:

> Take the Kafka producer/consumer skills from Module 2.16 and run them against managed MSK.

You need:

- bootstrap broker information
- network connectivity
- authentication
- authorization
- topic
- producer configuration
- consumer group
- offsets.

The application remains Kafka-aware. MSK changes the infrastructure and operating model, not the fundamental Kafka application abstraction.

---

# 44. MSK Connect

Kafka Connect uses:

```text
Connector
   ↓
Worker
   ↓
Tasks
```

Two broad types:

```text
Source Connector
External System → Kafka

Sink Connector
Kafka → External System
```

MSK Connect is AWS's managed Kafka Connect capability.

Use it when a connector is a better fit than custom application code.

Monitor:

- connector state
- task state
- throughput
- errors
- offsets
- worker capacity
- destination health.

MSK Connect uses an execution role and additional IAM permissions; current AWS documentation should be used to construct least-privilege policies. citeturn0search4

---

# 45. Debezium on MSK Connect

Architecture:

```text
PostgreSQL
    ↓
Debezium
    ↓
MSK Connect
    ↓
MSK
    ↓
Consumers
```

Use this for CDC pipelines where database changes become Kafka events.

Important concepts:

- source connector
- offsets
- source metadata
- schemas
- snapshot behavior
- ongoing change events
- connector health
- restart/recovery.

Do not re-teach Debezium internals from Module 2.16. Focus on AWS deployment and operations.

---

# 46. S3 Sink Connectors

Architecture:

```text
MSK
 ↓
S3 Sink Connector
 ↓
S3
 ↓
Lakehouse
```

Compare with:

```text
Kinesis
 ↓
Firehose
 ↓
S3
```

| Dimension | Firehose | Kafka Connect S3 Sink |
|---|---|---|
| Main abstraction | Managed delivery | Kafka ecosystem connector |
| Kafka dependency | Optional | Required |
| Control | Lower | Higher |
| Portability | AWS-centric | Kafka ecosystem |
| Connector ecosystem | Smaller | Broad Kafka Connect ecosystem |
| Operations | Simpler | More connector/worker management |
| Best fit | Managed AWS delivery | Kafka-centered platform |

Choose based on architecture, not brand preference.

---

# 47. Managed Service for Apache Flink

Architecture:

```text
Kinesis / MSK
      ↓
Managed Service for Apache Flink
      ↓
Stateful Processing
      ↓
S3 / Redshift / Other Sink
```

Managed Service for Apache Flink is designed for processing streaming data with Java, Python, SQL, or Scala and supports stateful streaming workloads. citeturn0search12turn0search13

Use it for:

- event-time processing
- windows
- joins
- aggregations
- state
- checkpointing
- recovery
- complex streaming logic.

Module 2.16 already teaches Flink fundamentals. This module focuses on the AWS managed operating model.

---

# 48. Stateful Stream Processing

Stateless:

```text
event
 ↓
transform
 ↓
output
```

Stateful:

```text
event
 ↓
state
 ↓
previous events
 ↓
window / join / aggregate
 ↓
output
```

Examples:

- rolling counts
- sessionization
- fraud detection
- real-time aggregation
- streaming joins.

The moment a business rule depends on history, state management becomes central.

---

# 49. Glue Schema Registry

Schemas are contracts between producers and consumers.

Architecture:

```text
Producer
   ↓
Schema Registry
   ↓
Consumer
```

AWS Glue Schema Registry supports integrations with:

- Apache Kafka
- Amazon MSK
- Kinesis Data Streams
- Managed Service for Apache Flink
- Lambda.

AWS documents support for Avro, JSON Schema, and Protobuf formats. citeturn0search0

### Why use it?

Without schema governance:

```text
Producer changes
↓
Consumer breaks
```

With governance:

```text
Producer proposes schema
↓
Compatibility check
↓
Version registered
↓
Consumers evolve safely
```

---

# 50. Schema Evolution

Example:

### Version 1

```json
{
  "user_id": "u1",
  "event_type": "click"
}
```

### Version 2

```json
{
  "user_id": "u1",
  "event_type": "click",
  "device_type": "mobile"
}
```

Adding an optional field can often be compatible.

Dangerous changes include:

- removing required fields
- changing incompatible types
- changing semantics without versioning
- making an optional field mandatory.

Glue Schema Registry checks compatibility rules when registering new schema versions. citeturn0search7

### Compatibility concepts

- backward compatibility
- forward compatibility
- breaking changes
- versioning
- consumer contract.

AWS documents integrations for MSK/Kafka, Kinesis, Flink, and Lambda, with specific library/version requirements for some Kinesis integrations. citeturn0search1

---

# 51. Kinesis vs MSK

This is the key architecture decision.

| Dimension | Kinesis Data Streams | MSK |
|---|---|---|
| Ecosystem | AWS-native | Apache Kafka |
| AWS integration | Excellent | Excellent |
| Kafka compatibility | No | Yes |
| Operational model | Simpler | Kafka operational model |
| Partitioning | Shards / partition keys | Kafka partitions |
| Consumer model | AWS-native consumers/KCL/Lambda | Kafka consumer groups |
| Connector ecosystem | AWS integrations | Kafka Connect ecosystem |
| Portability | Lower | Higher |
| Team skill | AWS streaming | Kafka |
| CDC | AWS patterns available | Strong Kafka/Connect ecosystem |
| Stateful processing | Flink/Lambda/etc. | Flink/Kafka ecosystem |
| Cost model | AWS service usage | Cluster/serverless + networking/storage/usage |
| Best reason to choose | AWS-native simplicity | Kafka compatibility/ecosystem |

## Choose Kinesis when

- AWS-native implementation is preferred
- operational simplicity matters
- tight Lambda/Firehose integration matters
- Kafka portability is not a requirement
- the team wants AWS-managed streaming primitives.

## Choose MSK when

- Kafka compatibility is important
- existing Kafka clients should be reused
- Kafka Connect ecosystem matters
- portability is strategically important
- existing Kafka expertise is strong.

## Do not choose either blindly

If the requirement is simply:

> "Get events reliably into S3."

You may need Firehose rather than a programmable streaming platform.

---

# 52. Kinesis vs Firehose

| Requirement | Kinesis Data Streams | Firehose |
|---|---|---|
| Programmable event stream | Strong fit | Not primary purpose |
| Custom consumers | Yes | Limited |
| Replay-oriented stream | Yes | Delivery-oriented |
| Stateful processing | Via consumers/Flink | Not primary purpose |
| Simple S3 landing | Possible | Excellent fit |
| Redshift delivery | Possible via integrations | Excellent fit |
| OpenSearch delivery | Possible via consumers | Managed delivery path |
| Low-code ingestion | Moderate | Strong |
| Consumer control | High | Lower |
| Main abstraction | Stream | Delivery service |

Mental model:

```text
Kinesis Data Streams
=
Streaming platform

Firehose
=
Managed delivery service
```

---

# 53. Kinesis vs MSK vs Firehose

Use a requirement-first model:

```text
Need a programmable event stream?
→ Kinesis Data Streams or MSK

Need Kafka ecosystem/portability?
→ MSK

Need AWS-native simplicity?
→ Kinesis

Need managed delivery into storage/warehouse/search?
→ Firehose
```

Exceptions exist. For example, a Kafka-centered organization may use MSK plus a sink connector, while an AWS-native organization may use Kinesis plus Firehose.

---

# 54. Reliability and Delivery Semantics

Production streaming should explicitly model:

- retries
- duplicates
- checkpointing
- replay
- failure destinations
- idempotency
- recovery windows.

### At-most-once

An event may be lost but is not intentionally retried.

### At-least-once

An event is retried, so duplicates are possible.

### Effectively-once

Business results are made idempotent so duplicate delivery does not produce duplicate business effects.

This is often the practical production goal.

---

# 55. Idempotent Consumers

Example:

```text
event_id = 123
```

Consumer receives:

```text
123
123
```

This can happen because:

```text
process
↓
crash before checkpoint
↓
restart
↓
replay
```

Use an idempotency strategy:

```text
event_id
 ↓
deduplication / idempotent sink
 ↓
business effect
```

Examples:

- database unique constraint
- conditional write
- idempotency table
- deterministic upsert
- transactionally coupled checkpoint/sink design where supported.

Do not create a global deduplication database without considering throughput, retention, and cost.

---

# 56. Stream Replay and Recovery

Recovery model:

```text
Failure
 ↓
Consumer recovery
 ↓
Checkpoint
 ↓
Replay retained events
 ↓
Idempotent processing
 ↓
Catch up
```

Ask:

1. How far behind can a consumer become?
2. How long is retention?
3. What is the maximum recovery duration?
4. Can downstream sinks accept replay traffic?
5. Are outputs idempotent?
6. How will replay be monitored?

---

# 57. Security

Production streaming security is:

```text
Identity
+
Authorization
+
TLS
+
Encryption
+
Network isolation
+
Audit
```

Controls:

- IAM roles
- least privilege
- KMS encryption where appropriate
- TLS
- VPC/private connectivity
- security groups
- Secrets Manager where credentials are required
- CloudTrail awareness
- schema governance.

### Avoid

- long-lived access keys in code
- broad `*` permissions
- public streaming endpoints
- unencrypted sensitive data
- unrestricted connector roles.

---

# 58. Observability

## Kinesis

Monitor:

- incoming records
- incoming bytes
- write throttling
- read throttling
- iterator age
- consumer health.

## Firehose

Monitor:

- delivery success/failure
- delivery latency
- transformation errors
- destination errors
- throttling
- data freshness.

## MSK

Monitor:

- broker health
- storage
- CPU
- network
- partition health
- replication
- consumer lag.

### Diagnostic pattern

```text
Metric
→ Symptom
→ Likely cause
→ Investigation
→ Fix
→ Verification
```

---

# 59. Troubleshooting Framework

Use:

```text
Symptom
 ↓
Identify affected stream/topic
 ↓
Check producer
 ↓
Check partition/shard distribution
 ↓
Check consumer
 ↓
Check lag
 ↓
Check downstream sink
 ↓
Check errors
 ↓
Check capacity
 ↓
Root cause
 ↓
Fix
 ↓
Verify
```

Do not restart everything first. Preserve evidence.

---

# 60. Production Failure Scenarios

## Incident 1 — Partial `PutRecords` failures

**Symptom:** request returns HTTP success but `FailedRecordCount > 0`.

**Evidence:** per-record `ErrorCode` values.

**Hypothesis:** throttling or transient internal failures.

**Fix:** retry only failed records with bounded backoff.

**Verification:** failed count returns to zero and producer metrics stabilize.

**Prevention:** batching, partition-key review, capacity monitoring, retry metrics.

---

## Incident 2 — Hot shard

**Symptom:** one shard experiences disproportionately high write pressure.

**Evidence:** shard-level metrics and partition-key distribution.

**Root cause:** low-cardinality/skewed partition key.

**Fix:** redesign the partition key or capacity strategy.

**Verification:** distribution becomes materially more balanced.

---

## Incident 3 — Consumer lag increases

**Symptom:** iterator age rises continuously.

**Evidence:** consumer processing latency, throttling, downstream latency.

**Root cause:** consumer throughput below producer throughput.

**Fix:** increase consumer parallelism, optimize processing, or correct hot-shard/capacity issues.

**Prevention:** alert on trend, not only absolute threshold.

---

## Incident 4 — Lambda poison record

**Symptom:** a batch repeatedly fails.

**Evidence:** repeated invocation failures.

**Root cause:** malformed or semantically invalid record.

**Fix:** use partial-failure handling/bisecting and a failure destination as appropriate.

**Verification:** healthy records resume and the poison record is isolated.

---

## Incident 5 — Firehose delivery failure

**Symptom:** delivery errors increase.

**Evidence:** Firehose delivery metrics and destination logs.

**Hypotheses:** destination throttling, permissions, networking, malformed data.

**Fix:** identify the destination-side failure and correct the relevant dependency.

---

## Incident 6 — Firehose creates too many tiny files

**Symptom:** S3 contains many small objects.

**Evidence:** object-size distribution.

**Root cause:** buffering/partition design produces many low-volume partitions.

**Fix:** reduce partition cardinality and tune buffering within current supported limits.

---

## Incident 7 — Dynamic partitioning creates excessive partitions

**Symptom:** huge number of S3 prefixes.

**Root cause:** high-cardinality partition key such as raw `user_id`.

**Fix:** use bounded business dimensions and time-based partitioning where appropriate.

---

## Incident 8 — Parquet conversion schema mismatch

**Symptom:** conversion fails or fields disappear.

**Evidence:** Glue schema versus producer payload.

**Root cause:** schema mismatch or unsupported data type.

**Fix:** correct the Glue schema or transform input into a compatible shape.

AWS documents schema mismatch and certain data-type conversion failures as common causes of Firehose Parquet conversion problems. citeturn1search0turn1search4

---

## Incident 9 — MSK producer cannot authenticate

**Symptom:** Kafka client reaches the cluster but authentication fails.

**Evidence:** client authentication errors.

**Hypotheses:** wrong IAM mechanism, incorrect client configuration, missing permissions.

**Fix:** verify IAM auth configuration, identity, policy, and TLS.

---

## Incident 10 — MSK consumer lag increases

**Symptom:** Kafka consumer lag rises.

**Evidence:** consumer metrics, broker health, partition assignment.

**Root cause candidates:** slow consumer, hot partition, downstream bottleneck, insufficient application parallelism.

**Fix:** identify the bottleneck before scaling.

---

## Incident 11 — Debezium connector stops

**Symptom:** CDC events stop arriving.

**Evidence:** connector/task state and source database health.

**Root cause candidates:** connector configuration, credentials, offsets, source database state, schema changes.

**Fix:** inspect connector/task logs before restarting.

---

## Incident 12 — Schema evolution breaks consumers

**Symptom:** consumer deserialization failures after producer deployment.

**Evidence:** schema version and compatibility error.

**Root cause:** breaking schema change.

**Fix:** roll back or publish a compatible version; then update consumers deliberately.

---

# 61. Hands-On Lab Environment

Use this conceptual project layout:

```text
jobs/streaming/
├── producers/
├── consumers/
├── lambda/
├── firehose/
├── msk/
├── schemas/
└── tests/
```

This is a learning layout only; the module does not require these files to be created.

---

# 62. Hands-On Lab 1 — Kinesis Producer

### Objective

Build a reliable producer.

### Tasks

1. Create an on-demand Kinesis stream.
2. Generate click events.
3. Add `event_id`, `user_id`, `event_type`, and timestamp.
4. Partition by user.
5. Use `PutRecords`.
6. Detect partial failures.
7. Retry only failed records.
8. Add exponential backoff and jitter.
9. Log event IDs.
10. Verify successful delivery.

### Evidence

Record:

- throughput
- failures
- retries
- final success count
- partition-key rationale.

---

# 63. Hands-On Lab 2 — Kinesis Consumers

Build two conceptual consumers:

### Consumer A

Shared consumer.

### Consumer B

Enhanced fan-out consumer.

Compare:

- latency
- throughput
- isolation
- operational complexity
- cost.

### Report

Write a short conclusion:

> Enhanced fan-out is justified when __________ because __________.

---

# 64. Hands-On Lab 3 — Lambda Consumer

Architecture:

```text
Kinesis
 ↓
Lambda
 ↓
Processing
```

Configure and test:

- batch size
- batching window
- retry
- bisecting
- failure destination.

Inject a poison record.

Measure:

- recovery time
- successful records
- failed records
- iterator age
- replay behavior.

---

# 65. Hands-On Lab 4 — Firehose to S3

Architecture:

```text
Kinesis
 ↓
Firehose
 ↓
S3
 ↓
Athena
```

Configure conceptually:

- dynamic partitioning
- event date
- event type
- Parquet conversion
- Glue schema
- error prefix.

Query the resulting data with Athena.

### Important constraint

Firehose record-format conversion to Parquet/ORC is an S3-oriented conversion path; AWS documents that enabling format conversion restricts the destination to S3. citeturn1search1

---

# 66. Hands-On Lab 5 — Hot Shard

Generate intentionally skewed traffic:

```text
80% events
→ same partition key
```

Measure:

- shard utilization
- throttling
- producer latency
- iterator age.

Then redesign the partition key.

Document:

```text
Before
→ distribution
→ symptom

After
→ distribution
→ outcome
```

---

# 67. Hands-On Lab 6 — MSK Serverless

Take the Kafka producer/consumer from Module 2.16 and run the application against MSK Serverless.

Tasks:

1. establish network connectivity
2. obtain bootstrap information
3. configure IAM authentication
4. create/use a topic
5. produce records
6. consume with a consumer group
7. verify offsets
8. inspect failures.

AWS's current MSK Serverless client documentation demonstrates the IAM SASL configuration pattern shown earlier in this module. citeturn1search14

---

# 68. Hands-On Lab 7 — MSK Connect

Conceptual pipeline:

```text
PostgreSQL
 ↓
Debezium
 ↓
MSK Connect
 ↓
MSK
 ↓
Consumer
```

Then compare:

```text
MSK
 ↓
S3 Sink Connector
 ↓
S3
```

Evaluate:

- connector management
- task behavior
- offsets
- monitoring
- IAM
- failure recovery.

---

# 69. Hands-On Lab 8 — Schema Governance

Create:

```text
Event Schema v1
```

Then evolve to:

```text
Event Schema v2
```

Test:

- backward-compatible change
- forward-compatible change
- breaking change
- consumer behavior.

Use Glue Schema Registry.

Record the compatibility policy you chose and why.

---

# 70. Hands-On Lab 9 — Kinesis vs MSK

Implement the same conceptual clickstream workload with:

```text
Kinesis
```

and:

```text
MSK
```

Compare:

- developer experience
- throughput
- operations
- scaling
- cost
- ecosystem
- portability
- observability.

Produce an ADR.

---

# 71. Hands-On Lab 10 — End-to-End Streaming Platform

Design:

```text
Clickstream
      |
      +----------------+
      |                |
   Kinesis            MSK
      |                |
      +-------+--------+
              |
          Processing
         /     |      \
     Lambda   Flink   Consumers
         \     |      /
              |
           Firehose
              |
       ----------------
       |              |
      S3          Redshift
       |
   Parquet/Iceberg
       |
     Athena
```

Then answer:

> Which components would you remove for a simpler workload?

A senior engineer should be able to explain not only how to build this architecture, but when **not** to build it.

---

# 72. Terraform, AWS CLI, and boto3

Use Infrastructure as Code for repeatability.

Potential resources include:

- Kinesis stream
- Firehose delivery stream
- IAM roles/policies
- Lambda event source mapping
- MSK infrastructure
- security groups/networking
- Glue Schema Registry resources
- supporting S3/KMS resources.

### CLI categories

Use the AWS CLI for:

- stream inspection
- stream metadata
- Firehose inspection
- MSK inspection
- operational automation.

### boto3 categories

Use boto3 for:

- stream creation
- `PutRecords`
- metadata
- test automation
- operational tooling.

### Syntax safety

AWS APIs, Terraform provider resources, and service capabilities evolve. Verify current official documentation before copying production IaC/API arguments.

---

# 73. Performance Engineering

Use:

```text
Measure
↓
Identify bottleneck
↓
Change one variable
↓
Measure again
```

Tune:

- partition-key distribution
- producer batching
- shard utilization
- consumer batching
- enhanced fan-out
- Lambda concurrency
- Firehose buffering
- S3 file size
- dynamic partitioning
- Parquet conversion
- consumer lag
- MSK partition count
- broker utilization.

### Example

If iterator age rises:

```text
Do not immediately add capacity.
```

First determine:

```text
Producer rate?
Consumer processing time?
Hot shard?
Downstream bottleneck?
Repeated failures?
```

---

# 74. Cost Engineering

## Kinesis

Cost drivers can include:

- capacity model
- throughput
- retention
- consumer features.

## Firehose

Cost drivers can include:

- data volume
- transformations
- format conversion
- destination delivery.

## MSK

Cost drivers can include:

- broker resources
- storage
- data transfer
- Serverless usage
- networking.

## Lambda

Cost drivers can include:

- invocations
- duration
- memory
- concurrency.

### Cost discipline

```text
Plan
↓
Estimate
↓
Tag
↓
Deploy
↓
Measure
↓
Experiment
↓
Destroy
```

Use:

- AWS Budgets
- alerts
- cost allocation tags
- Terraform teardown
- explicit cleanup.

Never memorize a price from this document. Check current AWS pricing before deployment.

---

# 75. Decision Matrix — Shared vs Enhanced Fan-Out

| Requirement | Shared | Enhanced fan-out |
|---|---:|---:|
| Few consumers | Strong | Often unnecessary |
| Many independent consumers | Possible but contention risk | Stronger fit |
| Lowest-latency reads | Weaker | Stronger |
| Simplicity | Strong | Moderate |
| Consumer isolation | Lower | Higher |
| Cost sensitivity | Stronger | Evaluate |
| Read contention | Risk | Better isolation |

---

# 76. Decision Matrix — Lambda vs KCL

| Requirement | Lambda | KCL |
|---|---|---|
| Minimal infrastructure | Strong | Moderate |
| Event-driven application | Strong | Strong |
| Custom long-running consumer | Limited | Strong |
| Fine-grained worker control | Lower | Higher |
| Server management | Low | Higher |
| Checkpoint coordination | Managed through integration | Explicit KCL model |
| Operational customization | Moderate | High |

Choose Lambda when the event-driven function model fits.

Choose KCL when you need a more explicit long-running consumer architecture.

---

# 77. Decision Matrix — Firehose vs Custom Consumer → S3

| Dimension | Firehose | Custom consumer |
|---|---|---|
| Implementation effort | Low | High |
| Delivery control | Moderate | High |
| Buffering | Managed | You own it |
| Transformations | Limited/lightweight | Arbitrary |
| Operations | Lower | Higher |
| S3 delivery | Strong | Strong |
| Cost optimization | Service-dependent | Engineering-dependent |
| Best fit | Standard ingestion | Specialized processing |

---

# 78. Decision Matrix — MSK Provisioned vs Serverless

| Dimension | Provisioned | Serverless |
|---|---|---|
| Infrastructure control | Higher | Lower |
| Operational effort | Higher | Lower |
| Capacity planning | More explicit | More managed |
| Stable predictable workload | Strong candidate | Candidate |
| Variable workload | Candidate | Strong candidate |
| Feature flexibility | Higher | Verify current feature set |
| Cost model | Infrastructure-oriented | Usage-oriented |
| Best fit | Control-heavy Kafka platform | Simpler/variable Kafka workloads |

---

# 79. Decision Matrix — Lambda Transformation vs Flink

| Requirement | Lambda | Managed Flink |
|---|---|---|
| Field normalization | Strong | Overkill |
| Lightweight enrichment | Strong | Strong |
| Stateful aggregation | Weak | Strong |
| Event-time windows | Weak | Strong |
| Complex joins | Weak | Strong |
| Simple per-record transformation | Strong | Overkill |
| Long-lived state | Weak | Strong |
| Operational complexity | Lower | Higher |

---

# 80. Decision Matrix — Firehose vs Kafka Connect S3 Sink

| Dimension | Firehose | Kafka Connect S3 Sink |
|---|---|---|
| AWS-native delivery | Strong | Moderate |
| Kafka dependency | No | Yes |
| Connector ecosystem | Lower | Strong |
| Portability | Lower | Higher |
| Operational complexity | Lower | Higher |
| Custom Kafka semantics | Lower | Higher |
| S3 delivery | Strong | Strong |
| Best fit | AWS-managed ingestion | Kafka-centered platform |

---

# 81. Architecture Decision Records

## ADR-01 — Kinesis vs MSK

**Context:** The platform needs durable real-time ingestion.

**Decision:** Select based on AWS-native simplicity vs Kafka ecosystem requirements.

**Alternatives:** Kinesis, MSK.

**Why:** Avoid choosing a platform solely because the engineering team knows it.

**Trade-offs:** portability, operations, cost, ecosystem.

**Consequence:** The decision must be recorded with workload assumptions.

---

## ADR-02 — Firehose vs Custom Consumer

**Context:** Events must land in S3.

**Decision:** Use Firehose when standard managed delivery satisfies requirements.

**Alternative:** Custom consumer.

**Why:** Reduce operational burden unless custom processing is necessary.

**Consequence:** Less control in exchange for lower operational complexity.

---

## ADR-03 — Shared vs Enhanced Fan-Out

**Context:** Multiple consumers need independent access.

**Decision:** Use enhanced fan-out when latency/isolation justify it.

**Consequence:** Additional cost and service configuration.

---

## ADR-04 — Lambda vs KCL

**Context:** A Kinesis consumer is required.

**Decision:** Use Lambda for function-oriented event processing; use KCL for explicit worker/consumer control.

---

## ADR-05 — Firehose vs Kafka Connect for S3

**Context:** Streaming data must reach the lake.

**Decision:** Firehose for AWS-native delivery; Kafka Connect when Kafka ecosystem portability and connector semantics dominate.

---

## ADR-06 — MSK Serverless vs Provisioned

**Context:** Kafka workload capacity varies.

**Decision:** Evaluate serverless for operational simplicity and variable demand; provisioned for explicit infrastructure control and supported workload requirements.

---

## ADR-07 — Flink vs Lambda Transformation

**Context:** Stream transformation is becoming more complex.

**Decision:** Lambda for lightweight record-level work; Flink for stateful/event-time/windowed processing.

---

# 82. Common Mistakes

| Mistake | Why dangerous | Prevention |
|---|---|---|
| Ignoring partial `PutRecords` failures | Silent data loss | Inspect every response entry |
| Retrying entire batch | Duplicate records | Retry failed records only |
| Low-cardinality partition key | Hot shards | Model key distribution |
| Ignoring iterator age | Hidden recovery backlog | Alert on trends |
| No poison-record strategy | Consumer stuck | Failure path + replay |
| Tiny Firehose buffers | Tiny objects | Tune buffering |
| Excessive dynamic partitions | Fragmented lake | Bound cardinality |
| Schema drift | Consumer failures | Registry + compatibility |
| No compatibility policy | Breaking deployments | Contract tests |
| Leaving provisioned MSK running | Unnecessary cost | Teardown discipline |
| Broad IAM | Security exposure | Least privilege |
| Public streaming infrastructure | Attack surface | Private networking |
| Treating Firehose as stream processor | Architectural mismatch | Use Kinesis/MSK/Flink |
| Choosing MSK only because Kafka is familiar | Over-engineering | Requirements-first decision |
| Choosing Kinesis without ecosystem analysis | Migration/connector friction | Evaluate Kafka needs |
| No replay plan | Poor incident recovery | Retention + checkpoint + idempotency |
| No cost model | Surprise bills | Budget and tags |

---

# 83. Security Design

Production model:

```text
Identity
   ↓
IAM
   ↓
Service Authorization
   ↓
TLS
   ↓
KMS
   ↓
VPC
   ↓
Security Groups
   ↓
Private Connectivity
   ↓
Audit
```

### Checklist

- [ ] IAM roles instead of long-lived keys
- [ ] least privilege
- [ ] KMS where required
- [ ] TLS
- [ ] private networking
- [ ] security groups
- [ ] Secrets Manager where credentials are needed
- [ ] CloudTrail awareness
- [ ] schema governance
- [ ] PII classification
- [ ] cost/resource tags.

---

# 84. Testing Strategy

Testing layers:

```text
Unit Tests
↓
Producer Tests
↓
Consumer Tests
↓
Schema Tests
↓
Integration Tests
↓
Failure Tests
↓
Load Tests
```

## Producer tests

- serialization
- partition-key selection
- retry behavior
- partial failures.

## Consumer tests

- duplicate event
- poison event
- checkpoint recovery
- downstream failure.

## Schema tests

- compatible change
- incompatible change
- required field behavior.

## Firehose tests

- transformation failure
- delivery failure
- schema mismatch
- partition routing.

## Load tests

Measure:

- throughput
- latency
- throttling
- consumer lag
- CPU
- memory
- output object sizes.

---

# 85. Idempotency Deep Dive

Example:

```text
event_id = 123
```

Consumer receives:

```text
123
123
```

Possible reason:

```text
Process
 ↓
Crash
 ↓
Checkpoint not committed
 ↓
Restart
 ↓
Replay
```

Possible implementation:

```text
event_id
 ↓
deduplication key
 ↓
conditional write / unique constraint
 ↓
business effect
```

Trade-offs:

- storage cost
- deduplication window
- concurrency
- cleanup
- consistency model
- throughput.

Do not build a permanent deduplication store unless the business requirement justifies it.

---

# 86. Production Reference Architectures

## Architecture 1 — Simple AWS-Native Streaming

```text
Application
   ↓
Kinesis
   ↓
Firehose
   ↓
S3
   ↓
Athena
```

Best for straightforward ingestion.

---

## Architecture 2 — Real-Time Processing

```text
Application
   ↓
Kinesis
   ↓
Lambda / Flink
   ↓
Redshift
```

Best when real-time processing is the main requirement.

---

## Architecture 3 — Kafka Enterprise Platform

```text
Applications
   ↓
MSK
   ↓
MSK Connect / Flink
   ↓
S3 / Redshift
```

Best when Kafka ecosystem requirements dominate.

---

## Architecture 4 — Hybrid

```text
Applications
      |
   ---------
   |       |
Kinesis   MSK
   |       |
   --- Processing ---
          |
       Firehose
          |
       S3/Iceberg
          |
      Athena/Redshift
```

Use only when the distinct requirements justify operating multiple streaming platforms.

---

# 87. Troubleshooting Runbooks

## Runbook — Producer Failure

**Symptom:** producer errors.

**First checks:**

1. authentication
2. stream existence
3. region
4. network
5. response failure count
6. throttling
7. payload size.

**Verification:** successful records and stable retry rate.

---

## Runbook — Partial Batch Failure

**Symptom:** HTTP 200 but failures exist.

**First checks:**

- `FailedRecordCount`
- per-record error
- shard distribution.

**Fix:** retry failed records only.

---

## Runbook — Hot Shard

**Symptom:** one shard is overloaded.

**Metrics:**

- incoming records
- incoming bytes
- throttling
- partition-key frequency.

**Fix:** correct key design and/or capacity.

---

## Runbook — Consumer Lag

**Symptom:** iterator age rises.

**First checks:**

- producer rate
- consumer processing time
- failures
- downstream latency
- shard distribution.

**Fix:** address the bottleneck; do not automatically scale everything.

---

## Runbook — Lambda Poison Record

**Symptom:** repeated batch failures.

**First checks:**

- failing event
- logs
- retry behavior
- bisect configuration
- failure destination.

**Fix:** isolate and quarantine the bad event, then replay after correction.

---

## Runbook — Firehose Delivery Failure

**Symptom:** destination failures.

**First checks:**

- destination health
- IAM
- network
- Firehose metrics
- error logs.

**Fix:** correct the dependency and verify backlog recovery.

---

## Runbook — Firehose Transformation Failure

**Symptom:** transformation errors.

**First checks:**

- Lambda logs
- input payload
- function version
- timeout
- output contract.

**Fix:** make the transformation deterministic and schema-compatible.

---

## Runbook — MSK Authentication Failure

**Symptom:** authentication rejected.

**First checks:**

- SASL mechanism
- IAM identity
- IAM policy
- TLS
- bootstrap endpoint
- client library configuration.

**Fix:** correct identity/configuration before changing cluster infrastructure.

---

## Runbook — MSK Connectivity Failure

**Symptom:** client cannot reach brokers.

**First checks:**

```text
DNS
↓
Routing
↓
Security Group
↓
TLS
↓
Authentication
```

---

## Runbook — Kafka Consumer Lag

**Symptom:** consumer group lag increases.

**First checks:**

- partition distribution
- consumer processing latency
- consumer instances
- downstream dependencies
- broker health.

---

## Runbook — Schema Compatibility Failure

**Symptom:** deserialization breaks after producer deployment.

**First checks:**

- schema version
- compatibility policy
- producer deployment
- consumer version.

**Fix:** restore compatibility before replaying traffic.

---

# 88. Interview Preparation

## Beginner

### What is Kinesis?

A managed AWS streaming service for durable event ingestion and consumption.

### What is a shard?

A unit of Kinesis capacity and parallelism within a stream.

### What is a partition key?

An input used to determine shard placement and therefore the ordering boundary.

### What is Firehose?

A managed delivery service for moving streaming data to supported destinations.

### What is MSK?

Amazon's managed service for Apache Kafka.

---

## Intermediate

### Explain partial `PutRecords` failures.

A request can succeed at the API level while individual records fail. Inspect the per-record response and retry only failures.

### Explain hot shards.

A skewed partition-key distribution concentrates traffic onto a shard, causing throttling or latency.

### Explain enhanced fan-out.

It provides registered consumers with dedicated read throughput and isolation from other consumers.

### Explain KCL.

A consumer library that handles shard coordination, leases, load balancing, and checkpointing.

### Explain Firehose dynamic partitioning.

It groups streaming records by keys and delivers them to corresponding S3 prefixes.

### Explain MSK Serverless.

A managed serverless Kafka operating model that reduces infrastructure management while retaining Kafka concepts, subject to service capabilities and quotas.

---

## Advanced

### Design a 1-million-events-per-second pipeline.

Expected discussion:

- requirements and peak rate
- partition-key distribution
- capacity model
- consumer architecture
- hot-shard avoidance
- backpressure
- replay
- schema governance
- sink capacity
- observability
- cost
- disaster recovery.

### Diagnose consumer lag.

Start with:

```text
Producer rate
→ shard distribution
→ consumer throughput
→ errors
→ downstream latency
```

### Choose Firehose vs Kafka Connect.

Choose Firehose for managed AWS delivery; choose Kafka Connect when Kafka ecosystem and connector portability/control matter.

---

## Senior/Staff

Discuss:

- Kinesis vs MSK platform strategy
- multi-region streaming
- schema governance
- replay/recovery
- security boundaries
- cost controls
- CDC + lakehouse architecture
- migration from Kafka to AWS-native streaming
- hybrid Kinesis/MSK architecture
- organizational operating model.

---

# 89. Practice Questions

## Conceptual — 20

1. What problem does streaming solve?
2. Why is retention important?
3. What is an ordering boundary?
4. Why can duplicate events occur?
5. What is idempotency?
6. What is a Kinesis stream?
7. What is a shard?
8. What is a partition key?
9. What is a sequence number?
10. What is iterator age?
11. What is Firehose?
12. What is dynamic partitioning?
13. Why is Parquet useful?
14. What is MSK?
15. What is MSK Connect?
16. What is Flink?
17. What is schema evolution?
18. What is a hot shard?
19. What is replay?
20. Why is observability part of reliability?

### Answers

1. Continuous ingestion/processing of events.
2. It defines the recovery/replay window.
3. The scope within which ordering is maintained.
4. Retries and crash-before-checkpoint scenarios.
5. Making repeated processing produce one logical business effect.
6. A managed AWS event-streaming resource.
7. A unit of Kinesis capacity and parallelism.
8. A value used to determine shard placement.
9. A service-assigned identifier for a record.
10. A lag indicator for Kinesis consumption.
11. Managed streaming delivery.
12. Routing records into S3 prefixes using record keys.
13. Columnar storage improves analytical efficiency.
14. Managed Apache Kafka.
15. Managed Kafka Connect workers/connectors.
16. A stateful stream-processing engine available as a managed AWS service.
17. Controlled changes to event contracts.
18. Traffic concentration on one shard.
19. Reprocessing retained events.
20. Without evidence, incidents become guesswork.

---

## Kinesis — 15

21. Why can `PutRecords` partially fail?
22. Why retry only failed records?
23. How does a partition key influence capacity?
24. Why can country be a poor partition key?
25. When might on-demand be preferred?
26. What does a sequence number identify?
27. Why is application `event_id` still needed?
28. What does KCL provide?
29. Why does KCL use lease/checkpoint state?
30. What does enhanced fan-out solve?
31. What is a poison record?
32. Why is iterator age important?
33. What is replay?
34. How does a hot shard form?
35. How would you fix a hot shard?

### Answers

21. Individual records are processed independently.
22. To avoid duplicating already successful records.
23. It determines shard placement.
24. It may be low-cardinality/skewed.
25. When traffic is variable or capacity is uncertain.
26. The service-assigned record position identifier.
27. Business idempotency needs a stable application identifier.
28. Consumer coordination and checkpointing.
29. To coordinate workers and recover progress.
30. Read-throughput contention/isolation.
31. A record that repeatedly causes processing failure.
32. It exposes growing consumer lag/recovery risk.
33. Reading retained events again.
34. Skewed key distribution.
35. Redesign the key and/or adjust capacity.

---

## Firehose — 15

36. What is Firehose's primary abstraction?
37. Why buffer data?
38. What is dynamic partitioning?
39. Why can dynamic partitioning cause small files?
40. Why is user ID often a poor S3 partition?
41. Why use Parquet?
42. What role does Glue play in format conversion?
43. Can Lambda transform records before delivery?
44. When should Lambda not be used?
45. What is an error prefix?
46. Why monitor delivery latency?
47. What is Iceberg delivery?
48. When is Firehose preferable to a custom consumer?
49. Why can buffering be a cost optimization?
50. Why must current Firehose capabilities be verified?

### Answers

36. Managed delivery.
37. To batch records and improve delivery efficiency.
38. Routing records into S3 prefixes by data keys.
39. High-cardinality partitions fragment data.
40. Millions of sparse user partitions create tiny datasets.
41. Columnar, compressed, analytics-friendly.
42. It provides schema information for conversion.
43. Yes, for supported Firehose transformation flows.
44. When processing requires complex state or windows.
45. A destination path for delivery/error handling patterns.
46. It exposes delivery freshness problems.
47. Managed streaming delivery into Iceberg tables where supported.
48. When requirements are standard and operational simplicity matters.
49. Larger objects can improve storage/query efficiency.
50. AWS features and limits evolve.

---

## MSK — 15

51. What is MSK?
52. What does MSK manage?
53. What does your team still manage?
54. What is MSK Serverless?
55. Why use IAM authentication?
56. What does IAM authenticate?
57. What does IAM authorize?
58. What is MSK Connect?
59. What is a source connector?
60. What is a sink connector?
61. What is Debezium used for?
62. Why use an S3 sink?
63. Why might Kafka portability matter?
64. What is consumer lag?
65. Why can a Kafka consumer lag grow?

### Answers

51. Managed Apache Kafka.
52. AWS manages core infrastructure and service operations.
53. Topics, clients, schemas, applications, security decisions, and workload operations.
54. A serverless Kafka model.
55. AWS-integrated identity and authorization.
56. The client identity.
57. Whether that identity may perform actions.
58. Managed Kafka Connect.
59. External system to Kafka.
60. Kafka to external system.
61. CDC/event capture from databases.
62. To land Kafka data in the data lake.
63. It reduces ecosystem lock-in.
64. Difference between produced and consumed progress.
65. Consumer throughput is below production or partitions are otherwise blocked.

---

## Troubleshooting — 10

66. HTTP 200 but `FailedRecordCount > 0`. What do you do?
67. One Kinesis shard is hot. What do you inspect?
68. Iterator age rises continuously. What do you investigate?
69. Lambda repeatedly fails. What next?
70. Firehose creates millions of small files. Why?
71. Parquet conversion fails. What do you compare?
72. MSK authentication fails. What do you check first?
73. MSK connectivity fails. What comes before IAM debugging?
74. Debezium stops producing events. What evidence matters?
75. Consumer deserialization breaks after a deployment. What likely happened?

### Answers

66. Retry only failed records.
67. Partition-key distribution and traffic concentration.
68. Producer rate, consumer rate, failures, shard pressure, downstream latency.
69. Identify the poison record and use the configured failure strategy.
70. Partition cardinality and buffering are poor.
71. Producer payload versus Glue schema/type compatibility.
72. Client mechanism, IAM identity, policy, TLS, bootstrap config.
73. DNS/routing/security-group/network reachability.
74. Connector/task logs, source DB health, offsets, schema changes.
75. A breaking schema evolution.

---

## Architecture — 10

76. When should you choose Kinesis over MSK?
77. When should you choose MSK over Kinesis?
78. When should you choose Firehose instead of either?
79. When should enhanced fan-out be justified?
80. When is Lambda preferable to Flink?
81. When is Flink preferable to Lambda?
82. When is Firehose preferable to Kafka Connect S3 sink?
83. When is MSK Serverless preferable to provisioned?
84. Why might hybrid Kinesis + MSK be a bad idea?
85. What evidence belongs in a streaming ADR?

### Answers

76. AWS-native simplicity and integration dominate.
77. Kafka ecosystem/compatibility/portability dominate.
78. Managed delivery is the primary requirement.
79. Multiple consumers need isolated low-latency reads.
80. Lightweight per-record logic.
81. Stateful/event-time/windowed processing.
82. AWS-native delivery and lower operational burden dominate.
83. Variable workloads and reduced infrastructure management.
84. It increases platform complexity and duplicated operational capability.
85. Requirements, alternatives, assumptions, cost, latency, reliability, security, and consequences.

---

## Security — 10

86. Why prefer IAM roles?
87. Why use TLS?
88. Why use KMS?
89. Why use private networking?
90. Why are broad IAM policies dangerous?
91. What should MSK IAM authentication protect?
92. Why protect schemas?
93. Why audit connector roles?
94. Why classify PII in streams?
95. What is the security baseline for streaming?

### Answers

86. Avoid long-lived credentials.
87. Protect data in transit.
88. Protect data at rest with controlled keys where required.
89. Reduce exposure.
90. They expand blast radius.
91. Client identity and authorization.
92. A schema is an operational/data contract.
93. Connectors can access large data surfaces.
94. Streaming systems often carry sensitive user data.
95. Least privilege + encryption + private networking + authorization + audit.

---

## Performance — 10

96. What creates a hot shard?
97. How can batching improve producers?
98. How can consumer batching improve efficiency?
99. What does enhanced fan-out change?
100. Why does partition cardinality affect S3 performance?
101. Why does Parquet help Athena?
102. What does rising iterator age indicate?
103. Why can excessive MSK partitions hurt operations?
104. Why can larger Firehose buffers help?
105. What is the correct performance-engineering loop?

### Answers

96. Skewed partition-key traffic.
97. Fewer API calls and better throughput.
98. Better per-invocation efficiency.
99. Read-throughput isolation.
100. It affects prefix count and object fragmentation.
101. Columnar pruning and compression.
102. Consumer backlog/recovery risk.
103. More metadata, management, and operational overhead.
104. Larger output objects and potentially better delivery efficiency.
105. Measure → isolate bottleneck → change one variable → measure again.

---

## Cost — 10

106. What drives Kinesis cost?
107. What drives Firehose cost?
108. What drives MSK cost?
109. What drives Lambda cost?
110. Why tag streaming resources?
111. Why use AWS Budgets?
112. Why tear down development MSK clusters?
113. Why can excessive dynamic partitioning increase cost?
114. Why can custom consumers cost more operationally even if service cost is lower?
115. What is the correct cost workflow?

### Answers

106. Capacity/usage, throughput, retention and consumer features.
107. Data volume and enabled processing/delivery features.
108. Broker/storage/network/serverless usage.
109. Invocation and execution characteristics.
110. Attribution.
111. Early cost warning.
112. Persistent billable resources can accumulate unnecessary cost.
113. It can create fragmented storage and more objects.
114. Engineering time is an operational cost.
115. Plan → estimate → tag → deploy → measure → optimize → destroy.

---

## Kinesis-vs-MSK Decisions — 10

116. Which is more Kafka-native?
117. Which is generally simpler for AWS-native streaming?
118. Which has the broader Kafka Connect ecosystem?
119. Which should you evaluate for an existing Kafka estate?
120. Which should you evaluate for simple Kinesis → S3 delivery?
121. Which service is a managed delivery service rather than the primary event-stream abstraction?
122. What should decide Kinesis vs MSK?
123. Why is team expertise relevant?
124. Why is portability relevant?
125. What is the worst decision heuristic?

### Answers

116. MSK.
117. Kinesis.
118. MSK/Kafka.
119. MSK.
120. Firehose.
121. Firehose.
122. Requirements and trade-offs.
123. Operational expertise affects reliability.
124. Migration/lock-in strategy matters.
125. "Choose what the team already knows."

---

# 90. Cheat Sheets

## Kinesis Architecture

```text
Producer
↓
Stream
↓
Shard
↓
Consumer
↓
Checkpoint
↓
Sink
```

## Shards

```text
Shard
=
capacity
+
parallelism
+
ordering boundary
```

## Partition Keys

```text
Key
↓
Hash
↓
Shard
```

Optimize for:

```text
ordering requirement
+
distribution
```

## `PutRecords`

```text
Batch
↓
Response
↓
Inspect every record
↓
Retry only failures
```

## Enhanced Fan-Out

```text
Shared
=
consumers share read path

EFO
=
registered consumers get dedicated read throughput
```

## KCL

```text
KCL
↓
leases/checkpoints
↓
DynamoDB
↓
worker coordination
```

## Lambda

```text
Kinesis
↓
event source mapping
↓
Lambda
↓
batch/retry/failure handling
```

## Firehose

```text
Source
↓
Firehose
↓
Buffer
↓
Destination
```

## Dynamic Partitioning

```text
record key
↓
S3 prefix
```

Avoid high-cardinality prefixes.

## Parquet Conversion

```text
JSON
↓
Glue schema
↓
Parquet
↓
S3
```

## Iceberg Delivery

```text
stream
↓
Firehose
↓
Iceberg
↓
lake analytics
```

Verify current supported configuration.

## Iterator Age

```text
increasing
=
investigate consumer backlog
```

## MSK

```text
Kafka clients
↓
MSK
↓
topics
↓
partitions
↓
consumer groups
```

## MSK IAM

```text
IAM identity
↓
SASL/IAM
↓
TLS
↓
MSK authorization
```

## MSK Connect

```text
connector
↓
worker
↓
tasks
```

## Flink

```text
stream
↓
state
↓
window/join/aggregate
↓
output
```

## Schema Registry

```text
schema
↓
version
↓
compatibility
↓
consumer contract
```

## Kinesis vs MSK

```text
AWS-native simplicity
→ Kinesis

Kafka ecosystem
→ MSK

Managed delivery
→ Firehose
```

## Troubleshooting

```text
Symptom
↓
Metric
↓
Evidence
↓
Hypothesis
↓
Test
↓
Fix
↓
Verify
```

---

# 91. Final Capstone — AWS Real-Time Data Platform

## Scenario

A company receives:

- clickstream
- application events
- transactions
- customer events.

Requirements:

- real-time ingestion
- replay
- low latency
- S3 lake
- Parquet
- Iceberg
- Athena
- Redshift
- schema governance
- PII protection
- observability
- cost controls.

## Architecture exercise

```text
Applications
     |
     +-------------------+
     |                   |
  Kinesis               MSK
     |                   |
     +--------+----------+
              |
        Stream Processing
         /       |       \
     Lambda     Flink    Consumers
         \       |       /
              |
           Firehose
              |
        ----------------
        |              |
       S3           Redshift
       |
   Parquet/Iceberg
       |
     Athena
```

## Required deliverables

1. architecture diagram
2. service decision record
3. partition-key design
4. schema design
5. failure strategy
6. replay strategy
7. security model
8. cost model
9. observability model
10. disaster-recovery considerations
11. teardown plan.

### Senior-level requirement

Explain which components are **not necessary** for the minimum viable architecture.

---

# 92. Cost-Safety Lab Rules

Because this module can create billable AWS infrastructure:

```text
Plan
↓
Estimate
↓
Tag
↓
Deploy
↓
Measure
↓
Experiment
↓
Destroy
```

Before labs:

- enable MFA
- use IAM Identity Center/assumed roles where appropriate
- establish AWS Budgets
- add cost allocation tags
- define teardown steps
- set a maximum experiment duration
- avoid unnecessary provisioned MSK resources.

After labs:

- delete temporary streams
- delete Firehose delivery streams
- remove Lambda resources
- remove test MSK resources
- remove test networking if dedicated
- remove test S3 data
- inspect billing/cost explorer.

Always verify current AWS pricing and free-tier terms before deployment.

---

# 93. Current AWS Documentation Safety

AWS streaming services evolve.

Before presenting exact production configuration, verify current official documentation for:

- Kinesis throughput limits
- shard/capacity quotas
- retention
- Firehose destinations
- dynamic partitioning
- Parquet conversion
- Iceberg delivery
- MSK Serverless capabilities
- IAM authentication
- MSK Connect
- Managed Service for Apache Flink
- Glue Schema Registry
- Terraform provider resources
- pricing.

Never fabricate:

- API parameters
- CLI flags
- Terraform arguments
- limits
- pricing
- service integrations
- supported destinations
- authentication mechanisms.

If a service capability is volatile, explicitly label the configuration as requiring current-doc verification.

---

# 94. Relationships to Other Modules

This topic connects to:

- Module 2.9 — Data Ingestion
- Module 2.11 — Data Quality
- Module 2.13 — Orchestration
- Module 2.14 — PySpark
- Module 2.15 — Iceberg
- Module 2.16 — Kafka and Streaming
- Module 2.17 — Cloud Data Platforms
- Module 2.18 — Terraform / CI/CD
- Module 2.20 — Observability / Governance / PII
- Module 2.21 — Performance / Cost
- G3 Topic 03 — Glue Data Catalog
- G3 Topic 05 — Athena
- G3 Topic 07 — Redshift.

### Boundary rule

Do not re-teach these modules in full. Use them as dependencies and integration points.

---

# 95. Production Operating Standard

A production streaming engineer should be able to answer:

### Understand

- What is the event contract?
- What is the ordering requirement?
- What is the replay window?

### Produce

- How are records partitioned?
- How are partial failures retried?
- What is the retry budget?

### Consume

- How is progress checkpointed?
- What happens after a crash?
- How are duplicates handled?

### Deliver

- Why Kinesis?
- Why Firehose?
- Why MSK?
- Why this sink?

### Monitor

- What metric indicates lag?
- What metric indicates throttling?
- What indicates destination failure?

### Troubleshoot

- What evidence will you collect first?
- Which dependency is likely failing?

### Optimize

- Is the bottleneck compute, network, partitioning, consumer throughput, or sink capacity?
- What is the cost per unit of useful output?

### Secure

- Which role can produce?
- Which role can consume?
- Where is encryption enabled?
- Is traffic private?

### Design

- What happens during a consumer outage?
- What happens during a producer burst?
- What happens when the schema changes?
- How do you replay safely?

---

# 96. Completion Checklist

## Kinesis

- [ ] Streams
- [ ] Shards
- [ ] Provisioned capacity
- [ ] On-demand capacity
- [ ] Partition keys
- [ ] Sequence numbers
- [ ] Retention
- [ ] `PutRecords`
- [ ] Partial batch failures
- [ ] Reliable producer
- [ ] Shared consumers
- [ ] Enhanced fan-out
- [ ] KCL
- [ ] Checkpoints
- [ ] DynamoDB leases
- [ ] Lambda consumers
- [ ] Batching
- [ ] Bisecting
- [ ] Failure destinations
- [ ] Hot shards
- [ ] Resharding
- [ ] Iterator age
- [ ] Replay
- [ ] Idempotency
- [ ] Recovery

## Firehose

- [ ] S3
- [ ] Redshift
- [ ] OpenSearch
- [ ] Buffering
- [ ] Dynamic partitioning
- [ ] Parquet conversion
- [ ] Glue schema
- [ ] Lambda transformation
- [ ] Iceberg
- [ ] Error handling
- [ ] Small-file mitigation

## MSK

- [ ] Provisioned
- [ ] Serverless
- [ ] Networking
- [ ] IAM authentication
- [ ] Kafka clients
- [ ] Consumer groups
- [ ] MSK Connect
- [ ] Debezium
- [ ] S3 sink
- [ ] Consumer lag

## Processing

- [ ] Managed Flink
- [ ] Stateful processing
- [ ] Windows
- [ ] State
- [ ] Checkpointing
- [ ] Recovery

## Governance

- [ ] Glue Schema Registry
- [ ] Schema versioning
- [ ] Compatibility
- [ ] Schema evolution

## Architecture

- [ ] Kinesis vs MSK
- [ ] Kinesis vs Firehose
- [ ] Firehose vs Kafka Connect
- [ ] Lambda vs KCL
- [ ] Lambda vs Flink
- [ ] Provisioned vs Serverless
- [ ] Reliability
- [ ] Security
- [ ] Performance
- [ ] Cost
- [ ] Observability
- [ ] Troubleshooting
- [ ] Runbooks
- [ ] ADRs
- [ ] Testing
- [ ] Capstone

---

# 97. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Section | Code/Example | Hands-On | Tested? |
|---|---|---|---|---|---|
| Kinesis Data Streams | Yes | 3–9 | Architecture | Lab 1/2 | Practice |
| Streams | Yes | 4 | Architecture | Lab 1 | Practice |
| Shards | Yes | 5 | Shard diagrams | Lab 5 | Practice |
| Provisioned capacity | Yes | 6 | Decision matrix | Lab 5 | Practice |
| On-demand capacity | Yes | 6 | Decision matrix | Lab 1 | Practice |
| Partition keys | Yes | 7, 24 | Examples | Labs 1/5 | Practice |
| Sequence numbers | Yes | 8 | Explanation | Lab 1 | Practice |
| Retention | Yes | 9 | Recovery model | Capstone | Practice |
| boto3 `PutRecords` | Yes | 11–12 | Python | Lab 1 | Practice |
| Partial failures | Yes | 12 | Retry code | Lab 1 | Practice |
| Firehose | Yes | 26–35 | Architecture | Lab 4 | Practice |
| S3 | Yes | 29–34 | Delivery | Lab 4 | Practice |
| Redshift | Yes | 35 | Delivery architecture | Capstone | Practice |
| OpenSearch | Yes | 36 | Destination use case | Capstone | Practice |
| Buffering | Yes | 28 | Trade-off | Lab 4 | Practice |
| Shared consumers | Yes | 15 | Comparison | Lab 2 | Practice |
| Enhanced fan-out | Yes | 16 | Comparison | Lab 2 | Practice |
| KCL | Yes | 17 | Coordination model | Lab 2 | Practice |
| Checkpoints | Yes | 18 | Recovery flow | Labs 2/3 | Practice |
| DynamoDB leases | Yes | 18 | KCL model | Lab 2 | Practice |
| Lambda consumers | Yes | 19–22 | Architecture | Lab 3 | Practice |
| Batching | Yes | 20 | Trade-off | Lab 3 | Practice |
| Bisecting | Yes | 21 | Failure tree | Lab 3 | Practice |
| Failure destinations | Yes | 22 | Failure flow | Lab 3 | Practice |
| Hot shards | Yes | 23 | Incident | Lab 5 | Practice |
| Partition-key skew | Yes | 23–24 | Examples | Lab 5 | Practice |
| Resharding/capacity | Yes | 25 | Recovery model | Lab 5 | Practice |
| Dynamic partitioning | Yes | 30 | S3 prefix model | Lab 4 | Practice |
| Parquet conversion | Yes | 31–32 | Pipeline | Lab 4 | Practice |
| Glue schema | Yes | 32 | Catalog model | Lab 4/8 | Practice |
| Lambda transformation | Yes | 33 | Pipeline | Lab 4 | Practice |
| Iceberg delivery | Yes | 34 | Architecture | Capstone | Practice |
| Iterator age | Yes | 37 | Incident | Labs 3/5 | Practice |
| MSK | Yes | 38–43 | Kafka model | Lab 6 | Practice |
| MSK Provisioned | Yes | 39 | Comparison | Lab 9 | Practice |
| MSK Serverless | Yes | 40 | Comparison | Lab 6 | Practice |
| IAM authentication | Yes | 42 | Client config | Lab 6 | Practice |
| Kafka clients | Yes | 43 | Client model | Lab 6 | Practice |
| MSK Connect | Yes | 44 | Connector model | Lab 7 | Practice |
| Debezium | Yes | 45 | CDC architecture | Lab 7 | Practice |
| S3 sink | Yes | 46 | Comparison | Lab 7 | Practice |
| Managed Flink | Yes | 47 | Architecture | Lab 10 | Practice |
| Stateful processing | Yes | 48 | State model | Lab 10 | Practice |
| Glue Schema Registry | Yes | 49 | Schema model | Lab 8 | Practice |
| Schema evolution | Yes | 50 | Version example | Lab 8 | Practice |
| Kinesis vs MSK | Yes | 51 | Decision matrix | Lab 9 | Practice |
| Ecosystem | Yes | 51 | Matrix | Lab 9 | Practice |
| Throughput/capacity | Yes | 5, 6, 51 | Trade-offs | Labs 5/9 | Practice |
| Retention | Yes | 9, 51 | Recovery | Capstone | Practice |
| Operational effort | Yes | 51, 78 | Matrix | Lab 9 | Practice |
| Cost model | Yes | 74, 75 | Cost section | Lab 9 | Practice |
| Portability | Yes | 51, 80 | Matrix | Lab 9 | Practice |
| Reliability | Yes | 54–56 | Failure model | Labs 1–10 | Practice |
| Security | Yes | 57, 83 | Security model | Capstone | Practice |
| Performance | Yes | 73 | Optimization | Labs 5/9 | Practice |
| Observability | Yes | 58 | Metrics | Labs 3/5 | Practice |
| Troubleshooting | Yes | 59, 87 | Runbooks | Incidents | Practice |
| Testing | Yes | 84 | Testing strategy | Labs | Practice |
| ADRs | Yes | 81 | 7 ADRs | Labs 9/10 | Review |
| Interview preparation | Yes | 88 | Model answers | — | Yes |
| Practice questions | Yes | 89 | 125 questions | — | Yes |
| Cheat sheets | Yes | 90 | Reference cards | — | Yes |
| Capstone | Yes | 91 | AWS Real-Time Data Platform | Yes | Yes |
| Cost safety | Yes | 92 | Lab controls | Labs | Yes |

### Audit result

**PASS — all explicit roadmap requirements represented in this module.**

The module intentionally keeps Kafka/Flink fundamentals as a refresh and concentrates depth on AWS-specific production implementation, as required by the source roadmap.

---

# 98. Technical Accuracy and Safety Audit

Before using this document in a real AWS account:

- [ ] Verify current Kinesis quotas and limits.
- [ ] Verify current Firehose destination capabilities.
- [ ] Verify current Firehose Iceberg configuration.
- [ ] Verify current MSK Serverless capabilities and quotas.
- [ ] Verify current MSK IAM client configuration.
- [ ] Verify current MSK Connect connector support.
- [ ] Verify current Managed Service for Apache Flink capabilities.
- [ ] Verify current Glue Schema Registry integrations.
- [ ] Verify Terraform provider syntax.
- [ ] Verify AWS CLI syntax.
- [ ] Verify current AWS pricing.
- [ ] Configure AWS Budgets.
- [ ] Use least-privilege IAM.
- [ ] Use private networking where appropriate.
- [ ] Tear down billable lab resources.

### Sources checked for volatile AWS details

The module's current-service statements were cross-checked against official AWS documentation for:

- `PutRecords` and partial failures. citeturn1search3
- Firehose dynamic partitioning. citeturn0search2turn0search3
- Firehose Parquet/ORC conversion and Glue schema requirements. citeturn1search0turn1search1
- Firehose Lambda transformation. citeturn1search2
- Firehose Iceberg delivery. citeturn0search10turn0search15
- MSK IAM authentication/client configuration. citeturn1search9turn1search14
- MSK Connect IAM requirements. citeturn0search4turn0search18
- Managed Service for Apache Flink. citeturn0search12turn0search13
- Glue Schema Registry and integrations. citeturn0search0turn0search1turn0search7

---

# 99. Final Mental Model

```text
UNDERSTAND
    ↓
PRODUCE
    ↓
CONSUME
    ↓
PROCESS
    ↓
DELIVER
    ↓
MONITOR
    ↓
REPLAY
    ↓
TROUBLESHOOT
    ↓
OPTIMIZE
    ↓
SECURE
    ↓
DESIGN
```

The senior-engineer mental model is:

```text
Kinesis
=
programmable AWS-native stream

MSK
=
managed Kafka platform

Firehose
=
managed delivery

Lambda
=
lightweight event processing

Flink
=
stateful stream processing

Schema Registry
=
event contract governance

S3/Iceberg
=
durable analytical lake

Redshift
=
warehouse analytics

Athena
=
serverless lake SQL
```

And the architectural decision rule is:

```text
Requirements
    ↓
Ordering
    ↓
Replay
    ↓
Latency
    ↓
Processing complexity
    ↓
Ecosystem
    ↓
Operational burden
    ↓
Security
    ↓
Cost
    ↓
Service choice
```

A production data engineer does not merely know how to create a stream.

They know **why the stream exists, how it fails, how it recovers, how it scales, how it is secured, how it is observed, how it is paid for, and when a different architecture is better.**
