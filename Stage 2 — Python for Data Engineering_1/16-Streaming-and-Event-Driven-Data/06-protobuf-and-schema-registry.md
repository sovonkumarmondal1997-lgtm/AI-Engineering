# Claude Code Prompt — Teach `06-protobuf-and-schema-registry.md`

You are a **Senior Data Engineer with 10+ years of production experience** building data platforms, event-driven architectures, Kafka ecosystems, schema governance systems, CDC pipelines, lakehouses, and production streaming systems.

I am following the **Stage 2 — Python for Data Engineering** curriculum.

We are currently working in:

```text
16-Streaming-and-Event-Driven-Data/
```

The current learning file is:

```text
06-protobuf-and-schema-registry.md
```

The authoritative roadmap for this module defines this file as the lesson on **Protobuf, schema registries, serialization/deserialization, compatibility, schema evolution, and production schema governance**.

Your task is to create a **complete, deeply structured, beginner-to-advanced learning lesson** for this file.

---

# 1. STRICT FILE-SCOPE RULE

You are allowed to create or modify **ONLY**:

```text
16-Streaming-and-Event-Driven-Data/06-protobuf-and-schema-registry.md
```

Do NOT modify, create, delete, rename, or rewrite any other file in the current folder.

In particular, do NOT modify:

```text
README.md
01-event-streams-vs-message-queues.md
02-kafka-topics-partitions-offsets-and-replication.md
03-kafka-producers-in-python.md
04-kafka-consumers-and-consumer-groups.md
05-delivery-semantics-at-most-at-least-and-exactly-once.md
07-event-time-processing-and-watermarks.md
08-tumbling-sliding-and-session-windows.md
09-stateful-stream-processing.md
10-spark-structured-streaming.md
11-apache-flink-and-pyflink-overview.md
12-debezium-cdc-streams-into-kafka.md
13-backpressure-and-consumer-lag.md
practice-questions.md
interview-practice.md
```

Do not update the roadmap or project tree.

If the file already exists, improve only that file.

---

# 2. PRIMARY OBJECTIVE

Teach me **Protobuf and Schema Registry** from absolute beginner level through production-grade data engineering.

The learning progression must be:

```text
Why schemas matter
        ↓
Structured events
        ↓
Serialization / deserialization
        ↓
JSON vs binary serialization
        ↓
Protobuf fundamentals
        ↓
.proto files
        ↓
Fields and field numbers
        ↓
Types
        ↓
Enums
        ↓
Nested messages
        ↓
Repeated fields
        ↓
Optional fields
        ↓
Python code generation
        ↓
Serialize / deserialize
        ↓
Kafka integration
        ↓
Schema Registry
        ↓
Subjects
        ↓
Schema versions
        ↓
Schema IDs
        ↓
Compatibility
        ↓
Schema evolution
        ↓
Production governance
        ↓
CI/CD compatibility checks
        ↓
Advanced schema design
```

The objective is not simply to memorize Protobuf syntax.

I should understand:

> **Why schema contracts are necessary in distributed streaming systems, how producers and consumers use them, how schemas evolve safely, and how Schema Registry protects production pipelines from incompatible changes.**

---

# 3. TEACHING STYLE

Assume I am technically capable but new to Protobuf and Schema Registry.

Do not assume prior knowledge of:

- serialization
- binary formats
- schema evolution
- schema compatibility
- Schema Registry
- Protobuf descriptors
- schema IDs
- wire formats

Start from first principles.

For every important concept use this progression:

```text
Simple explanation
        ↓
Real-world analogy
        ↓
Technical explanation
        ↓
Diagram
        ↓
Code example
        ↓
Failure example
        ↓
Production implication
        ↓
Knowledge checkpoint
```

Use simple language first, then introduce the correct technical terminology.

---

# 4. START WITH THE PROBLEM

Before teaching Protobuf, explain why schemas are needed.

Start with an event such as:

```json
{
  "order_id": 101,
  "customer_id": 42,
  "amount": 499.99,
  "currency": "USD"
}
```

Explain:

- what the producer knows
- what the consumer expects
- what happens if a field is missing
- what happens if a field changes type
- what happens if a field is renamed
- what happens if a new field is added
- what happens if old consumers still exist
- why multiple independent teams make schema management difficult

Build the idea:

```text
Producer
   ↓
Event
   ↓
Kafka
   ↓
Consumer A
Consumer B
Consumer C
```

Explain why a shared schema contract becomes important.

---

# 5. WHAT IS SERIALIZATION?

Teach serialization from absolute basics.

Explain:

> Serialization converts an in-memory object into a format that can be transmitted or stored.

And:

> Deserialization converts that representation back into an in-memory object.

Show:

```text
Python Object
     ↓
Serialization
     ↓
Bytes
     ↓
Kafka
     ↓
Deserialization
     ↓
Python Object
```

Explain why Kafka fundamentally deals with bytes.

Use simple Python examples.

Start with JSON.

Then compare:

```text
JSON
Protobuf
Avro
```

Do not turn this into a full Avro lesson; explain Avro only enough to establish the roadmap's required comparison.

---

# 6. JSON VS BINARY SCHEMAS

Create a clear comparison.

Explain:

### JSON

Advantages:

- human-readable
- easy debugging
- simple ecosystem

Disadvantages:

- larger payloads
- weaker type enforcement
- schema discipline is often external
- repeated field names increase payload size

### Protobuf

Advantages:

- compact binary representation
- strongly typed
- explicit schema
- generated code
- efficient serialization/deserialization
- controlled evolution

Disadvantages:

- not human-readable on the wire
- requires schema tooling
- schema evolution must be understood correctly

Explain why production streaming systems frequently use binary schemas.

---

# 7. INTRODUCE PROTOBUF

Explain:

> Protocol Buffers (Protobuf) is a language-neutral, platform-neutral serialization format and schema system.

Explain:

- `.proto` files
- messages
- fields
- field types
- field numbers
- generated classes
- serialization
- deserialization

Start with:

```proto
syntax = "proto3";

message OrderEvent {
  int64 order_id = 1;
  int64 customer_id = 2;
  double amount = 3;
  string currency = 4;
}
```

Explain every line.

Do not assume the learner understands `proto3`.

---

# 8. PROTOBUF FIELD NUMBERS

This is a critical concept.

Explain why:

```proto
string customer_id = 1;
```

has:

```text
field name = customer_id
field number = 1
```

Explain that the field number is part of the wire-level identity.

Teach:

> **Field numbers must be treated as permanent identifiers.**

Explain why changing:

```proto
customer_id = 1;
```

to:

```proto
customer_id = 7;
```

is dangerous.

Explain:

- binary wire representation
- backward compatibility implications
- old consumers
- new consumers
- field-number reuse

---

# 9. PROTOBUF SCALAR TYPES

Teach the major scalar types relevant to data engineering.

Include examples of:

```text
string
bytes
bool
int32
int64
uint32
uint64
sint32
sint64
fixed32
fixed64
sfixed32
sfixed64
float
double
```

Do not merely list them.

Explain:

- what each type represents
- typical use cases
- important differences
- signed vs unsigned
- integer encoding considerations
- why choosing the correct type matters

Keep the explanation practical.

---

# 10. ENUMS

Teach Protobuf enums.

Example:

```proto
enum OrderStatus {
  ORDER_STATUS_UNSPECIFIED = 0;
  ORDER_STATUS_PENDING = 1;
  ORDER_STATUS_PAID = 2;
  ORDER_STATUS_CANCELLED = 3;
}
```

Explain:

- why enum zero values matter
- explicit numeric values
- unknown enum values
- evolution considerations
- adding enum values
- compatibility considerations

Show Python usage.

---

# 11. NESTED MESSAGES

Teach nested messages.

Example:

```proto
message Money {
  string currency = 1;
  int64 units = 2;
}

message OrderEvent {
  int64 order_id = 1;
  Money amount = 2;
}
```

Explain:

- composition
- reusable structures
- nested serialization
- generated Python classes

Show realistic event modeling.

---

# 12. REPEATED FIELDS

Teach:

```proto
repeated string product_ids = 1;
```

Explain:

- lists
- repeated scalar values
- repeated messages
- serialization behavior
- common data engineering use cases

Show Python examples.

---

# 13. OPTIONAL FIELDS

Teach Protobuf `optional`.

Explain why presence matters.

Distinguish:

```text
field absent
```

from:

```text
field present with default value
```

Explain why this matters for data pipelines.

Use an example such as:

```proto
optional string customer_email = 5;
```

Show how presence can be checked in Python.

Explain the production implications.

---

# 14. `oneof`

Include `oneof` because it is important for robust Protobuf modeling.

Example:

```proto
message PaymentMethod {
  oneof method {
    Card card = 1;
    BankTransfer bank_transfer = 2;
    string wallet_id = 3;
  }
}
```

Explain:

- mutually exclusive fields
- use cases
- evolution considerations
- Python access

Keep this within the Protobuf foundation.

---

# 15. PROTOBUF FIELD EVOLUTION RULES

Teach the critical rule:

> **Never reuse field numbers.**

Show:

```proto
message Order {
  string order_id = 1;
  string customer_id = 2;
}
```

Then explain why this is dangerous:

```proto
message Order {
  string order_id = 1;
  int64 amount = 2;
}
```

when field `2` previously represented `customer_id`.

Explain:

```text
Old meaning:
field 2 → customer_id

New meaning:
field 2 → amount
```

This can cause catastrophic interpretation errors.

---

# 16. RESERVED FIELDS

Teach:

```proto
reserved 2;
reserved "customer_id";
```

Explain why deleted fields should often be reserved.

Show:

```text
Old field
   ↓
removed
   ↓
reserved
   ↓
prevents accidental reuse
```

Explain the production value of this practice.

---

# 17. ADDING FIELDS SAFELY

Teach why adding a new field can often be safe.

Example:

### Version 1

```proto
message OrderEvent {
  int64 order_id = 1;
  double amount = 2;
}
```

### Version 2

```proto
message OrderEvent {
  int64 order_id = 1;
  double amount = 2;
  string coupon_code = 3;
}
```

Explain what:

- old producer + new consumer
- new producer + old consumer

experience.

Explain defaults and unknown fields.

---

# 18. UNSAFE TYPE CHANGES

Teach why type changes are dangerous.

Discuss examples such as:

```text
int64 → string
string → bytes
double → string
```

Explain that compatibility depends on the exact schema and wire encoding, and that not every type change is safe.

Do not simplify this into "all type changes are always impossible."

Explain the principle:

> **A schema change must be evaluated for wire compatibility and consumer behavior, not merely whether the code compiles.**

---

# 19. PYTHON CODE GENERATION

Teach how `.proto` definitions become Python classes.

Cover:

```text
.proto
  ↓
protoc / buf
  ↓
generated Python code
  ↓
application
```

Use Python 3.12+.

Explain the role of:

```text
protoc
buf
protobuf Python runtime
```

Show installation/setup commands appropriate to the project's environment.

Explain generated files without requiring the learner to manually edit generated code.

---

# 20. PYTHON PROTOBUF EXAMPLE

Create a complete beginner-friendly example.

Use:

```proto
message OrderEvent {
  int64 order_id = 1;
  int64 customer_id = 2;
  double amount = 3;
  string currency = 4;
}
```

Then show Python:

```python
event = OrderEvent(
    order_id=101,
    customer_id=42,
    amount=499.99,
    currency="USD",
)
```

Show:

```python
payload = event.SerializeToString()
```

Then:

```python
decoded = OrderEvent()
decoded.ParseFromString(payload)
```

Explain every operation.

---

# 21. SERIALIZED BYTES

Teach what actually gets sent.

Show:

```text
Python object
      ↓
SerializeToString()
      ↓
bytes
      ↓
Kafka
```

Explain:

- why the wire representation is binary
- why you should not manually inspect it as text
- how schemas allow correct decoding
- how serialization errors should be handled

Show safe error handling.

---

# 22. PROTOBUF + KAFKA

Now connect Protobuf to Kafka.

Show:

```text
Producer
   ↓
Protobuf serialization
   ↓
bytes
   ↓
Kafka topic
   ↓
Protobuf deserialization
   ↓
Consumer
```

Explain:

- key vs value
- Protobuf event value
- Kafka headers
- serialization/deserialization boundaries

Use the module's intended Python ecosystem:

```text
confluent-kafka
```

Do not re-teach the complete Kafka producer/consumer modules.

Only teach the integration necessary for schema management.

---

# 23. SCHEMA REGISTRY

Now introduce Schema Registry.

Start from the problem:

```text
Producer A
Producer B
Producer C
Consumer A
Consumer B
Consumer C
```

all need to agree on schemas.

Explain:

> Schema Registry is a centralized system for storing, versioning, validating, and governing schemas used by data producers and consumers.

Explain:

- schema storage
- schema versions
- schema IDs
- compatibility rules
- subjects

Use a simple architecture:

```text
Producer
   |
   | register / retrieve schema
   ↓
Schema Registry
   |
   ↓
Kafka
   |
   ↓
Consumer
```

---

# 24. SCHEMA ID

Explain the idea of a schema ID.

Teach:

```text
Schema
  ↓
Registry
  ↓
Schema ID
```

Then:

```text
Kafka record
  ↓
serialized payload
  +
schema reference
```

Explain why the consumer needs to know which schema should decode the payload.

Do not incorrectly imply that the complete schema must be embedded in every Kafka message.

---

# 25. SUBJECTS

Teach Schema Registry subjects.

Explain:

```text
Subject
  ↓
Schema versions
  ↓
Schema evolution
```

Discuss subject naming strategies conceptually.

Include:

- topic-name strategy
- record-name strategy
- topic-record-name strategy

Explain the trade-offs.

Discuss when multiple event types may share a topic.

Do not assume one subject strategy is universally correct.

---

# 26. SCHEMA VERSIONS

Show:

```text
OrderEvent v1
OrderEvent v2
OrderEvent v3
```

Explain:

- registration
- versioning
- retrieving old schemas
- compatibility checks
- why old versions matter during rolling deployments

Use an example:

```text
Producer v2
Consumer v1
Consumer v2
```

Explain how compatibility allows gradual deployment.

---

# 27. COMPATIBILITY

This is one of the most important sections.

Teach:

```text
Backward compatibility
Forward compatibility
Full compatibility
```

Explain each in simple terms.

Use concrete producer/consumer examples.

### Backward

A new schema can read data written using the previous schema.

### Forward

An older schema can read data written using the newer schema.

### Full

Both directions work.

Do not merely provide definitions.

Show actual schema examples.

---

# 28. TRANSITIVE COMPATIBILITY

Teach:

```text
BACKWARD
BACKWARD_TRANSITIVE
FORWARD
FORWARD_TRANSITIVE
FULL
FULL_TRANSITIVE
```

Explain the difference between checking:

```text
current schema ↔ immediately previous schema
```

and:

```text
current schema ↔ all relevant historical schemas
```

Explain why transitive compatibility matters when a topic has a long history.

---

# 29. COMPATIBILITY EXAMPLES

Use a version progression:

```text
v1
order_id
amount
```

```text
v2
order_id
amount
currency
```

```text
v3
order_id
amount
currency
customer_id
```

Walk through compatibility.

Then introduce breaking changes such as:

```text
removing fields
changing field types
reusing field numbers
changing semantic meaning
```

Clearly distinguish:

```text
wire compatibility
```

from:

```text
business/semantic compatibility
```

A schema may technically remain compatible while changing the business meaning of a field.

This is an important senior-level concept.

---

# 30. PROTOBUF + SCHEMA REGISTRY

Explain the complete flow.

Use:

```text
                Schema Registry
                /      \
               /        \
        Producer          Consumer
           |                 |
       serialize          deserialize
           |                 |
           +------ Kafka ----+
```

Walk through:

1. producer obtains/registers schema
2. registry returns schema information
3. producer serializes the event
4. producer sends bytes to Kafka
5. consumer receives bytes
6. consumer uses schema information
7. consumer deserializes the event
8. compatibility protects the contract

---

# 31. CONFLUENT PROTOBUF SERIALIZER

Use the project's intended Python ecosystem.

Teach the conceptual role of:

```text
ProtobufSerializer
ProtobufDeserializer
```

Show a realistic Python Kafka producer example.

Explain:

- serializer configuration
- Schema Registry URL
- message type
- serialization
- producing to Kafka

Keep configuration explicit.

Do not hide critical concepts behind helper classes.

---

# 32. CONFLUENT PROTOBUF DESERIALIZER

Show the consumer side.

Teach:

```text
Kafka bytes
    ↓
ProtobufDeserializer
    ↓
Python Protobuf object
```

Explain:

- schema lookup
- schema ID
- deserialization failures
- incompatible schema behavior
- handling malformed records

Provide realistic Python code.

---

# 33. AVRO VS PROTOBUF VS JSON SCHEMA

Create a practical comparison.

| Feature | Protobuf | Avro | JSON Schema |
|---|---|---|---|
| Encoding | Binary | Binary | JSON/text |
| Schema | `.proto` | Avro schema | JSON Schema |
| Code generation | Strong | Available | Varies |
| Human readability | Low | Low | High |
| Evolution | Strong | Strong | Strong |
| Kafka ecosystem | Strong | Strong | Strong |
| Typical use | Service/event contracts | Data/streaming platforms | JSON APIs/events |

Explain that this is a practical comparison, not an absolute ranking.

Discuss:

- Protobuf strengths
- Avro strengths
- JSON Schema strengths

Do not turn this into a separate Avro course.

---

# 34. PROTOBUF EVOLUTION RULES

Create a dedicated production checklist.

Include:

### Safe practices

- never reuse field numbers
- reserve deleted field numbers
- reserve deleted field names where appropriate
- add fields carefully
- use appropriate defaults
- maintain compatibility
- use CI checks
- test old/new producer combinations
- test old/new consumer combinations

### Dangerous practices

- reusing field numbers
- changing semantic meaning
- unsafe type changes
- deleting fields without considering old consumers
- changing enum semantics carelessly
- assuming compilation means compatibility

---

# 35. SCHEMA EVOLUTION LAB

Build a hands-on lab.

Create:

```text
schemas/
    order_event_v1.proto
    order_event_v2.proto
    order_event_v3.proto
```

Start with:

```text
v1
order_id
amount
```

Then add:

```text
v2
currency
```

Then:

```text
v3
customer_id
```

Test:

```text
old producer → new consumer
new producer → old consumer
```

Record the behavior.

Then intentionally introduce:

```text
breaking_v4.proto
```

and explain exactly why it is unsafe.

---

# 36. SCHEMA REGISTRY LAB

Create a local Schema Registry environment using the module's Docker Compose infrastructure.

The environment should conceptually contain:

```text
Kafka
Schema Registry
Kafka UI
Python producer
Python consumer
```

Demonstrate:

1. register schema
2. inspect subject
3. inspect schema version
4. retrieve schema
5. observe schema ID
6. evolve schema
7. test compatibility
8. intentionally submit a breaking change
9. observe registry rejection

Use CLI/API examples where appropriate.

---

# 37. COMPATIBILITY MODE LAB

Configure a subject with an appropriate compatibility mode.

Test:

```text
v1 → v2
v2 → v3
```

Then test incompatible changes.

Demonstrate:

```text
accepted
```

versus:

```text
rejected
```

Explain why.

Do not simply show commands. Explain what the registry is protecting.

---

# 38. CI/CD BREAKING CHANGE CHECKS

Teach production schema governance.

Show the concept:

```text
Developer changes .proto
        ↓
Pull Request
        ↓
Schema compatibility check
        ↓
PASS / FAIL
        ↓
Merge
        ↓
Deploy
```

Use:

```text
buf breaking
```

as required by the roadmap.

Explain:

- why compatibility should be checked before deployment
- why runtime registry rejection is too late
- why schema changes belong in version control
- why automated checks are important

Show an example CI command/workflow.

Keep it simple but realistic.

---

# 39. SCHEMA REGISTRY COMPATIBILITY IN CI

Explain the relationship between:

```text
Buf
```

and:

```text
Schema Registry
```

Do not confuse their responsibilities.

Explain:

```text
Buf
→ checks Protobuf schema changes

Schema Registry
→ governs schemas used by deployed streaming applications
```

Explain how both can complement one another.

---

# 40. SUBJECT NAMING STRATEGIES

Teach in detail:

### TopicNameStrategy

### RecordNameStrategy

### TopicRecordNameStrategy

For each explain:

- how subjects are formed
- strengths
- weaknesses
- multi-event topics
- reuse across topics
- operational implications

Give concrete examples.

For example:

```text
orders-value
```

versus:

```text
com.company.events.OrderEvent
```

versus:

```text
orders-com.company.events.OrderEvent
```

Explain why naming decisions matter in multi-team environments.

---

# 41. MULTIPLE EVENT TYPES PER TOPIC

Discuss:

```text
Topic:
customer-events
```

containing:

```text
CustomerCreated
CustomerUpdated
CustomerDeleted
```

Explain:

- whether multiple event types should share a topic
- how subject naming affects this
- how consumers identify the event type
- trade-offs
- schema governance implications

Do not claim that one event type per topic is always required.

---

# 42. SCHEMA REFERENCES

Teach the roadmap's advanced concept:

> schema references

Explain why large schemas may be composed from reusable definitions.

For example:

```text
OrderEvent
    ↓
Money
    ↓
Address
```

Explain the conceptual value of reusable schema definitions.

Do not overcomplicate implementation details, but provide enough technical depth for a senior data engineer.

---

# 43. WELL-KNOWN TYPES

Teach Protobuf well-known types at a practical level.

Discuss examples such as:

```text
Timestamp
Duration
Struct
Value
Any
```

Focus especially on data engineering use cases.

Explain why timestamps should be represented consistently.

Connect this carefully to event schemas without turning it into the next module's event-time lesson.

---

# 44. `oneof` AND EVOLUTION

Return briefly to `oneof` and explain evolution risks.

Show why adding/removing alternatives must be considered carefully.

Explain how consumers behave when they encounter an alternative they do not know.

---

# 45. DEFAULT VALUES AND UNKNOWN FIELDS

Explain Protobuf behavior around:

- default values
- absent fields
- unknown fields
- newer producer → older consumer
- older producer → newer consumer

Use concrete examples.

This section should make compatibility behavior intuitive.

---

# 46. SERIALIZATION FAILURE HANDLING

Show realistic failure cases:

```text
invalid object
wrong field type
missing required application data
malformed bytes
unknown schema ID
schema lookup failure
incompatible schema
registry unavailable
```

Explain how production producers and consumers should respond.

Discuss:

- retries
- error logging
- DLQ where appropriate
- avoiding silent data corruption

Do not turn this into a generic error-handling lesson.

---

# 47. SCHEMA GOVERNANCE

Introduce production governance.

Teach:

```text
schema ownership
versioning
compatibility policy
review
CI checks
registry controls
documentation
deprecation
```

Explain why schema governance becomes increasingly important as organizations grow.

Use an organization example:

```text
Team A → produces OrderEvent
Team B → consumes OrderEvent
Team C → consumes OrderEvent
Team D → builds analytics
```

Explain why Team A cannot safely change the schema without considering downstream consumers.

---

# 48. SCHEMA CONTRACT AS AN API CONTRACT

Explain the analogy:

```text
REST API contract
        ≈
Event schema contract
```

But explain the differences.

Discuss:

- request/response APIs
- asynchronous event contracts
- independent deployment
- retained historical data
- replay

This should reinforce why schema evolution is especially important for event-driven data systems.

---

# 49. PRODUCTION ARCHITECTURE

Create a complete architecture:

```text
                  ┌─────────────────────┐
                  │   Schema Registry   │
                  └──────────┬──────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
        Python Producer               Python Consumer
              │                             │
      Protobuf Serializer          Protobuf Deserializer
              │                             │
              └────────── Kafka ────────────┘
```

Then extend it:

```text
Producer
   ↓
Schema Registry
   ↓
Kafka
   ↓
Consumer
   ↓
Data Warehouse / Lakehouse
```

Explain the responsibilities of each component.

---

# 50. ADVANCED PRODUCTION SCENARIOS

Create scenarios such as:

### Scenario 1

A producer adds a field.

What happens to old consumers?

### Scenario 2

A consumer is deployed before the producer.

What compatibility direction is required?

### Scenario 3

A field is deleted.

What should happen?

### Scenario 4

A field number is reused.

Why is this dangerous?

### Scenario 5

A producer changes the semantic meaning of an existing field without changing its type.

Why can compatibility checks fail to protect business correctness?

### Scenario 6

Two event types share one Kafka topic.

How should subjects be designed?

### Scenario 7

A schema registry becomes temporarily unavailable.

What should producers/consumers do?

### Scenario 8

A breaking `.proto` change reaches CI.

What should happen?

Require detailed reasoning for each.

---

# 51. HANDS-ON END-TO-END PROJECT

Create a practical project:

```text
protobuf_schema_lab/
```

Suggested structure:

```text
protobuf_schema_lab/
├── schemas/
│   ├── order_event_v1.proto
│   ├── order_event_v2.proto
│   └── order_event_v3.proto
├── generated/
├── producer/
├── consumer/
├── tests/
├── docker-compose.yml
└── README.md
```

The project should demonstrate:

1. Protobuf schema definition
2. Python code generation
3. serialization
4. deserialization
5. Kafka producer
6. Kafka consumer
7. Schema Registry
8. schema registration
9. schema versions
10. compatibility checking
11. schema evolution
12. breaking-change rejection
13. old/new producer compatibility testing
14. old/new consumer compatibility testing
15. CI compatibility validation

Do not modify files outside the target lesson while generating this lesson's instructional examples. The project structure is an **example for the learner**, not an instruction to create those files in the current curriculum folder.

---

# 52. FAILURE INJECTION

Include deliberate failure exercises.

Test:

```text
wrong schema
wrong field type
missing schema
unknown schema ID
incompatible schema
registry unavailable
malformed Protobuf payload
old consumer + new producer
new consumer + old producer
```

For each explain:

```text
What failed?
Why did it fail?
At what layer?
What should production systems do?
```

---

# 53. DEBUGGING WORKFLOW

Teach a practical debugging workflow.

When a Protobuf/Kafka message fails:

```text
1. Inspect topic
2. Identify producer schema
3. Identify schema ID
4. Inspect Schema Registry subject
5. Inspect schema version
6. Check compatibility
7. Inspect serializer/deserializer configuration
8. Check generated code version
9. Reproduce with known payload
10. Test old/new schema combinations
```

Explain each step.

---

# 54. COMMON MISTAKES

Create a detailed section:

## Common Mistakes

Include at least:

1. Reusing field numbers
2. Forgetting to reserve deleted fields
3. Assuming field names define wire compatibility
4. Treating schema registry as a simple file store
5. Ignoring compatibility modes
6. Deploying schema changes without CI checks
7. Changing semantic meaning without changing schema
8. Using unsafe type changes
9. Assuming generated code automatically guarantees compatibility
10. Assuming Protobuf alone provides schema governance
11. Ignoring old consumers
12. Ignoring replayed historical data
13. Using inconsistent timestamp representations
14. Treating Schema Registry availability as irrelevant
15. Putting unrelated event types into one subject
16. Choosing subject naming without understanding downstream impact

Explain why each mistake is dangerous.

---

# 55. PROTOBUF VS AVRO — SENIOR-LEVEL DECISION

Explain when an organization might choose:

```text
Protobuf
```

versus:

```text
Avro
```

Consider:

- service contracts
- streaming events
- data platforms
- code generation
- schema evolution
- ecosystem
- language support
- interoperability
- data warehouse/lakehouse integration

Do not declare a universal winner.

The objective is to teach architectural decision-making.

---

# 56. SCHEMA DESIGN CHECKLIST

Create a production checklist:

```text
Before approving a schema:
```

Check:

- Is the event name clear?
- Are fields semantically precise?
- Are field numbers stable?
- Are deleted fields reserved?
- Are timestamps modeled consistently?
- Are enums safe to evolve?
- Are optional fields used intentionally?
- Are nested messages reusable?
- Is `oneof` necessary?
- Is compatibility preserved?
- Is the subject correct?
- Is the compatibility mode correct?
- Has CI compatibility validation passed?
- Have old/new producer/consumer combinations been tested?
- Has semantic compatibility been reviewed?

---

# 57. KNOWLEDGE CHECKPOINTS

After each major section, include questions.

Examples:

```text
What is serialization?

Why does Kafka need bytes?

Why does Protobuf use field numbers?

Why must field numbers never be reused?

What happens when a new producer adds a field?

What is backward compatibility?

What is forward compatibility?

What is full compatibility?

Why is transitive compatibility useful?

What is a Schema Registry subject?

What is a schema ID?

What does ProtobufSerializer do?

Why does a consumer need the correct schema?

What is the difference between Buf and Schema Registry?

Why can a schema be wire-compatible but semantically incompatible?

Why are old consumers important?

Why are schema references useful?
```

Provide answers after the questions.

---

# 58. BEGINNER EXERCISES

Include exercises such as:

1. Write a basic `.proto`.
2. Define an `OrderEvent`.
3. Add an enum.
4. Add a nested `Money` message.
5. Add a repeated field.
6. Add an optional field.
7. Serialize a Python object.
8. Deserialize it.
9. Identify field numbers.
10. Explain why a field number cannot be reused.

---

# 59. INTERMEDIATE EXERCISES

Include:

1. Generate Python classes using `protoc`.
2. Generate using `buf`.
3. Produce Protobuf events to Kafka.
4. Consume Protobuf events from Kafka.
5. Register a schema.
6. Inspect schema versions.
7. Test backward compatibility.
8. Test forward compatibility.
9. Test full compatibility.
10. Create a deliberately breaking schema.

---

# 60. ADVANCED EXERCISES

Include:

1. Design a multi-team event contract.
2. Choose a subject naming strategy.
3. Design multiple event types in one topic.
4. Build schema compatibility CI.
5. Test old producer/new consumer.
6. Test new producer/old consumer.
7. Design schema references.
8. Analyze semantic compatibility.
9. Design a schema deprecation process.
10. Design a production schema governance policy.

---

# 61. SENIOR DATA ENGINEER INTERVIEW PREPARATION

Add interview questions strictly related to this file.

Cover:

- Protobuf
- serialization
- deserialization
- field numbers
- reserved fields
- optional fields
- enums
- nested messages
- repeated fields
- `oneof`
- schema evolution
- backward compatibility
- forward compatibility
- full compatibility
- transitive compatibility
- Schema Registry
- schema IDs
- subjects
- subject naming strategies
- Confluent serializers
- schema references
- CI compatibility checks
- semantic compatibility
- Protobuf vs Avro

For each advanced question provide:

```text
Question
What the interviewer is testing
Expected reasoning
Strong answer
Common weak answer
```

Include realistic system-design scenarios.

---

# 62. INTERVIEW SCENARIOS

Include senior-level scenarios such as:

### Scenario A

> Your company has 100 consumers of `OrderEvent`. Product wants to rename `customer_id` to `client_id`. How would you handle this?

### Scenario B

> A team reused a deleted Protobuf field number. Production consumers are now reading incorrect values. How do you respond?

### Scenario C

> A schema is backward compatible but the business meaning of a field changed. Should the change be approved?

### Scenario D

> You have three event types on one Kafka topic. How would you configure Schema Registry subjects?

### Scenario E

> A producer deployment is rolling out while some consumers are still running the previous version. What compatibility guarantee do you need?

### Scenario F

> CI detects an incompatible `.proto` change. The developer argues that all current consumers will be upgraded simultaneously. How would you evaluate this?

Require architecture-level reasoning.

---

# 63. FINAL CAPSTONE

Design a senior-level capstone:

## Real-Time Order Event Contract Platform

Architecture:

```text
Python Producer
      ↓
Protobuf
      ↓
Schema Registry
      ↓
Kafka
      ↓
Python Consumer
      ↓
PostgreSQL
```

Requirements:

- versioned `OrderEvent`
- Protobuf
- generated Python classes
- Schema Registry
- schema IDs
- subject naming
- compatibility configuration
- old/new producer testing
- old/new consumer testing
- CI breaking-change check
- malformed payload handling
- schema evolution
- reserved fields
- documentation
- schema governance

The learner must produce:

```text
schema design
compatibility policy
subject naming decision
CI strategy
producer implementation
consumer implementation
failure analysis
schema evolution plan
```

---

# 64. FINAL ASSESSMENT

Create a comprehensive assessment that tests whether I can:

- explain serialization
- explain Protobuf
- write `.proto` schemas
- use field numbers correctly
- use enums
- use nested messages
- use repeated fields
- use optional fields
- use `oneof`
- generate Python classes
- serialize and deserialize
- integrate Protobuf with Kafka
- explain Schema Registry
- explain schema IDs
- explain subjects
- explain schema versions
- explain backward compatibility
- explain forward compatibility
- explain full compatibility
- explain transitive compatibility
- safely evolve schemas
- use reserved fields
- use Confluent serializers/deserializers
- understand subject naming strategies
- understand schema references
- use Buf breaking checks
- distinguish wire compatibility from semantic compatibility
- debug schema failures
- design production schema governance

Create a mastery rubric:

```text
NOT READY
```

```text
FOUNDATIONAL
```

```text
PRODUCTION-READY
```

```text
SENIOR-LEVEL
```

Define concrete expectations for each level.

---

# 65. FINAL MENTAL MODEL

End with a concise but powerful mental model:

```text
Event
  ↓
Schema
  ↓
Serialization
  ↓
Bytes
  ↓
Kafka
  ↓
Schema ID / Registry
  ↓
Schema Resolution
  ↓
Deserialization
  ↓
Consumer
```

Then:

```text
Schema Design
      ↓
Schema Evolution
      ↓
Compatibility
      ↓
Registry Governance
      ↓
CI Validation
      ↓
Safe Deployment
```

Reinforce:

> **A schema is not merely a description of data. In an event-driven system, it is a long-lived contract between independently deployed producers and consumers.**

And:

> **Never evaluate a schema change only by asking whether the code compiles. Ask whether existing producers, existing consumers, historical events, wire compatibility, and business semantics remain safe.**

---

# 66. REQUIRED FILE STRUCTURE

Organize the final Markdown lesson approximately as:

```text
# Protobuf and Schema Registry

## Learning Objectives

## 1. Why Schemas Matter

## 2. Serialization and Deserialization

## 3. JSON vs Binary Serialization

## 4. Introduction to Protobuf

## 5. .proto Files

## 6. Protobuf Field Numbers

## 7. Scalar Types

## 8. Enums

## 9. Nested Messages

## 10. Repeated Fields

## 11. Optional Fields

## 12. oneof

## 13. Protobuf Evolution Rules

## 14. Reserved Fields

## 15. Adding Fields Safely

## 16. Unsafe Type Changes

## 17. Python Code Generation

## 18. Python Serialization and Deserialization

## 19. Protobuf and Kafka

## 20. Schema Registry

## 21. Schema IDs

## 22. Subjects

## 23. Schema Versions

## 24. Compatibility

## 25. Transitive Compatibility

## 26. Protobuf + Schema Registry

## 27. Confluent Protobuf Serializer

## 28. Confluent Protobuf Deserializer

## 29. Protobuf vs Avro vs JSON Schema

## 30. Schema Evolution

## 31. CI/CD Compatibility Checks

## 32. Subject Naming Strategies

## 33. Multiple Event Types per Topic

## 34. Schema References

## 35. Well-Known Types

## 36. Unknown Fields and Defaults

## 37. Serialization Failure Handling

## 38. Schema Governance

## 39. Schema Contracts as API Contracts

## 40. Production Architecture

## 41. Advanced Production Scenarios

## 42. Schema Evolution Lab

## 43. Schema Registry Lab

## 44. Compatibility Mode Lab

## 45. Failure Injection

## 46. Debugging Workflow

## 47. Common Mistakes

## 48. Protobuf vs Avro Decision Framework

## 49. Schema Design Checklist

## 50. Knowledge Checkpoints

## 51. Beginner Exercises

## 52. Intermediate Exercises

## 53. Advanced Exercises

## 54. Senior Data Engineer Interview Questions

## 55. Interview Scenarios

## 56. Final Capstone

## 57. Final Assessment

## 58. Final Mental Model
```

You may improve the exact structure if it creates a better learning progression, but **do not omit any required concept**.

---

# 67. CODE QUALITY REQUIREMENTS

All Python examples must:

- target Python 3.12+
- use clear variable names
- use type hints where useful
- include appropriate error handling
- use logging where useful
- avoid unnecessary abstractions
- explain important configuration
- be runnable where practical
- clearly identify required dependencies
- use the project's intended Kafka ecosystem
- use `confluent-kafka` where Kafka integration is demonstrated
- use the Python Protobuf runtime
- clearly separate generated code from handwritten application code

Do not provide fake APIs or invented configuration parameters.

Where exact tool/version behavior matters, explicitly state the expected version or verify it rather than silently assuming.

---

# 68. HANDS-ON LEARNING LOOP

Every major practical section should follow:

```text
1. Understand
2. Design
3. Implement
4. Run
5. Inspect
6. Break
7. Recover
8. Compare
9. Explain
```

For schema evolution specifically:

```text
Create v1
   ↓
Run producer/consumer
   ↓
Create v2
   ↓
Run compatibility checks
   ↓
Test old consumer
   ↓
Test new consumer
   ↓
Introduce breaking change
   ↓
Observe rejection
   ↓
Explain why
```

This is mandatory.

---

# 69. QUALITY-CONTROL CHECKLIST

Before considering the lesson complete, verify:

- [ ] Starts from absolute beginner level
- [ ] Explains why schemas matter
- [ ] Explains serialization/deserialization
- [ ] Explains JSON vs binary
- [ ] Explains Protobuf
- [ ] Explains `.proto`
- [ ] Explains scalar types
- [ ] Explains field numbers
- [ ] Explains enums
- [ ] Explains nested messages
- [ ] Explains repeated fields
- [ ] Explains optional fields
- [ ] Explains `oneof`
- [ ] Explains reserved fields
- [ ] Explains schema evolution
- [ ] Explains safe field addition
- [ ] Explains unsafe type changes
- [ ] Explains unknown fields/defaults
- [ ] Includes Python code generation
- [ ] Includes serialization/deserialization examples
- [ ] Integrates Protobuf with Kafka
- [ ] Explains Schema Registry
- [ ] Explains subjects
- [ ] Explains schema versions
- [ ] Explains schema IDs
- [ ] Explains backward compatibility
- [ ] Explains forward compatibility
- [ ] Explains full compatibility
- [ ] Explains transitive compatibility
- [ ] Covers Confluent Protobuf Serializer
- [ ] Covers Confluent Protobuf Deserializer
- [ ] Covers subject naming strategies
- [ ] Covers multiple event types per topic
- [ ] Covers schema references
- [ ] Covers Protobuf well-known types
- [ ] Covers Buf
- [ ] Covers `buf breaking`
- [ ] Covers CI/CD schema validation
- [ ] Distinguishes Buf from Schema Registry
- [ ] Distinguishes wire compatibility from semantic compatibility
- [ ] Includes production schema governance
- [ ] Includes realistic failure scenarios
- [ ] Includes debugging workflow
- [ ] Includes hands-on labs
- [ ] Includes schema evolution exercises
- [ ] Includes Schema Registry exercises
- [ ] Includes failure injection
- [ ] Includes common mistakes
- [ ] Includes production architecture
- [ ] Includes decision framework
- [ ] Includes senior interview preparation
- [ ] Includes capstone
- [ ] Includes final assessment
- [ ] Does not skip roadmap concepts
- [ ] Does not drift into unrelated modules
- [ ] Does not modify any other file

---

# 70. FINAL EXECUTION INSTRUCTION

Now inspect only the information necessary to understand the existing curriculum context and target file.

Then create or update:

```text
16-Streaming-and-Event-Driven-Data/06-protobuf-and-schema-registry.md
```

The resulting lesson must take me from:

```text
absolute beginner
      ↓
serialization fundamentals
      ↓
Protobuf fundamentals
      ↓
Python implementation
      ↓
Kafka integration
      ↓
Schema Registry
      ↓
compatibility
      ↓
schema evolution
      ↓
CI/CD validation
      ↓
schema governance
      ↓
production architecture
      ↓
senior-level reasoning
```

The lesson must be **deep, practical, technically accurate, simple to understand, and production-oriented**.

Do not skip any concept defined for this file in the roadmap.

**Under no circumstances modify any other file in `16-Streaming-and-Event-Driven-Data/`.**