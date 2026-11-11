# Quarantine, Dead-Letter, and Bad-Record Handling

> **Stage 2 — Python for Data Engineering**  
> **Module 2.11 — Data Validation, Contracts, and Quality**  
> **Topic 07 — Quarantine, Dead-Letter, and Bad-Record Handling**

---

## Learning Objectives

By the end of this lesson, you should be able to:

- explain why invalid data should not automatically be dropped;
- distinguish record-level failures from batch-level failures;
- choose between **fail, drop, flag, fix, and quarantine**;
- design a quarantine store with structured failure metadata;
- distinguish quarantine storage from a dead-letter queue (DLQ);
- classify validation failures with machine-readable error codes and severity;
- preserve enough evidence to investigate and replay a bad record;
- apply thresholds without inventing universal limits;
- design retry and DLQ behavior for transient versus deterministic failures;
- identify and handle poison messages;
- make replay idempotent;
- design a controlled quarantine lifecycle;
- connect Pydantic, Pandera, Great Expectations, and Soda results to operational actions;
- implement batch and streaming bad-record handling in Python;
- design write-audit-publish workflows;
- reason about atomicity, partial failure, and partial publishing;
- use circuit breakers when failure rates indicate a systemic problem;
- protect PII and sensitive data in quarantine systems;
- monitor quarantine depth, age, replay outcomes, and error classes;
- build a production recovery workflow from detection through prevention.

---

## Prerequisites

This topic builds on:

1. **Data Quality Dimensions** — what makes data valid, complete, accurate, timely, and consistent.
2. **Pydantic** — record-level validation and structured validation errors.
3. **Pandera** — DataFrame-level schema and data validation.
4. **Great Expectations / Soda** — declarative quality checks.
5. **Data Contracts** — producer ownership and explicit quality expectations.
6. **Schema Evolution** — compatibility and schema-drift reasoning.

These topics are used here as integration points rather than repeated in full.

---

# 1. The Production Problem

Consider a production pipeline:

```text
Source
  ↓
Ingestion
  ↓
Validation
  ↓
Transformation
  ↓
Publish
```

Suppose a batch contains:

```text
1,000,000 records
999,950 valid
50 invalid
```

The first question is not:

> "How do I remove the invalid records?"

The first question is:

> "What should happen to the invalid records, and can the valid records safely continue?"

Possible policies include:

```text
FAIL
DROP
FLAG
FIX
QUARANTINE
```

There is no universal answer.

The correct decision depends on:

- dataset criticality,
- defect type,
- blast radius,
- percentage of invalid data,
- whether the defect is deterministic,
- whether valid records are independently safe,
- downstream consequences,
- replay requirements,
- business tolerance,
- security requirements.

The central production principle is:

> **Preserve bad data for investigation and recovery rather than silently destroying it.**

Bad data is inevitable.

Silent data loss is not.

---

# 2. The Learning Loop for Bad Data

For every validation failure, reason through:

```text
Understand the failure
        ↓
Identify affected scope
        ↓
Classify the defect
        ↓
Decide action
        ↓
Preserve evidence
        ↓
Alert / record
        ↓
Repair or correct
        ↓
Replay safely
        ↓
Verify
        ↓
Prevent recurrence
```

This loop applies whether the failure comes from:

- a Python validator,
- a DataFrame schema,
- a database constraint,
- a contract check,
- a stream consumer,
- a source API,
- a batch file,
- a business rule.

---

# 3. What Is a Bad Record?

A **bad record** is a record that cannot safely continue through the intended data pipeline because it violates a structural, syntactic, semantic, contractual, referential, or business rule.

Examples include:

- missing required field;
- invalid datatype;
- malformed timestamp;
- invalid enum;
- negative quantity;
- invalid foreign key;
- schema mismatch;
- business-rule violation;
- duplicate record;
- malformed JSON;
- contract violation.

## 3.1 Syntactically Invalid

The data cannot be parsed.

Example:

```json
{"order_id": 101, "quantity":
```

The JSON itself is malformed.

---

## 3.2 Structurally Invalid

The payload parses, but does not match the expected structure.

Example:

```json
{
  "order_id": 101,
  "quantity": "five"
}
```

when the contract requires:

```text
quantity: integer
```

---

## 3.3 Semantically Invalid

The structure is valid, but the value's meaning is invalid.

Example:

```text
currency = "USD"
amount = -500
```

when the business definition requires a non-negative transaction amount.

---

## 3.4 Business-Rule Invalid

The individual fields may be valid, but their combination violates a business rule.

Example:

```text
order_status = "cancelled"
refund_amount = 0
refund_completed_at = present
```

If the domain rule says a completed refund must have a positive refund amount, the record is invalid even though every field has the correct datatype.

---

# 4. What Is Quarantine?

**Quarantine is a controlled holding area for data that cannot safely continue through the normal pipeline.**

Instead of:

```text
invalid
  ↓
discard
```

use:

```text
invalid
  ↓
quarantine
  ↓
diagnose
  ↓
repair
  ↓
replay
```

A quarantine system should preserve enough information to:

- investigate the defect;
- identify the source;
- identify the pipeline run;
- understand why validation failed;
- assign ownership;
- repair the record;
- replay it;
- audit what happened.

Quarantine is therefore not merely a folder called `errors/`.

It is an operational recovery mechanism.

---

# 5. Quarantine Architecture

A basic architecture:

```text
                  ┌─────────────────┐
                  │                 │
Input → Validate ─┤      Valid      ├→ Normal Pipeline
                  │                 │
                  └─────────────────┘
                           │
                           │ invalid
                           ▼
                    ┌──────────────┐
                    │  Quarantine  │
                    └──────────────┘
                           │
                           ▼
                       Diagnose
                           │
                           ▼
                         Repair
                           │
                           ▼
                         Replay
                           │
                           ▼
                       Revalidate
                           │
                           ▼
                         Publish
```

A streaming system may instead use:

```text
Producer
   ↓
Consumer
   ↓
Validation / Processing
   ├── success → downstream
   │
   └── failure → retry → DLQ
                         ↓
                      diagnose
                         ↓
                       repair
                         ↓
                       replay
```

The storage and messaging mechanisms can differ. The recovery principle remains the same.

---

# 6. Quarantine vs Dead-Letter Queue

These concepts overlap but are not identical.

## Quarantine

Quarantine is the broader concept.

It is often used in:

- batch pipelines;
- database pipelines;
- lake/object-storage workflows;
- warehouse ingestion;
- DataFrame processing.

Examples:

```text
quarantine table
quarantine files
error table
bad-record dataset
```

## Dead-Letter Queue

A **dead-letter queue (DLQ)** is commonly used in messaging and event-processing systems.

A message that cannot be successfully processed is routed to another destination:

```text
Event
  ↓
Consumer
  ↓
Failure
  ↓
DLQ
```

A DLQ can preserve the message and processing metadata for later inspection and replay.

## Comparison

| Mechanism | Typical Environment | Main Purpose |
|---|---|---|
| Quarantine table | Database / warehouse | Preserve invalid records |
| Quarantine files | Object storage / lake | Preserve bad batch records |
| Error table | Relational pipeline | Queryable failures |
| DLQ | Messaging / streaming | Isolate failed messages |
| Error topic | Streaming platform | Route failures separately |

The underlying principle is:

> **Isolate invalid data without silently losing it.**

---

# 7. Fail, Drop, Flag, Fix, Quarantine

These are different operational actions.

## 7.1 FAIL

Stop processing.

Use this when:

- corruption is widespread;
- the schema contract is broken;
- the critical dataset is unsafe;
- continuing would produce misleading output;
- a global invariant is violated.

Example:

```text
Expected:
customer_id: integer

Received:
customer_id: object
```

across most of the batch.

Failing may be safer than publishing questionable data.

---

## 7.2 DROP

Discard the record.

This is dangerous because the system loses evidence.

Drop is appropriate only when:

- loss is explicitly acceptable;
- the record is provably irrelevant;
- policy permits destruction;
- the action is observable and documented.

Never use:

```python
except Exception:
    pass
```

as a bad-record policy.

---

## 7.3 FLAG

Continue processing but mark the condition.

Useful for:

- soft quality issues;
- reviewable anomalies;
- non-critical conditions.

Example:

```text
email_missing = True
```

while allowing the record to enter a downstream table.

Flagging is appropriate only when downstream consumers understand the meaning of the flag.

---

## 7.4 FIX

Automatically correct the record.

Automatic repair should be used only when the correction is deterministic and auditable.

Example:

```text
raw quantity = "005"
normalized quantity = 5
```

A correction record should preserve:

```text
original_value
corrected_value
correction_reason
corrected_at
correction_rule
```

---

## 7.5 QUARANTINE

Remove the invalid record from the normal flow while preserving it for:

- investigation;
- correction;
- replay;
- audit.

---

# 8. Decision Framework

Ask:

1. Is the defect recoverable?
2. Is the record independently invalid?
3. Is the entire batch suspect?
4. Is the dataset critical?
5. Can valid records safely continue?
6. Is automatic repair deterministic?
7. Is data loss acceptable?
8. Is replay required?
9. Is the issue caused by producer/schema drift?
10. What is the downstream impact?

Then select:

```text
fail
drop
flag
fix
quarantine
```

The decision should be explicit rather than hidden in implementation code.

---

# 9. Record-Level vs Batch-Level Failure

This distinction is fundamental.

Suppose:

```text
1,000,000 records
1 invalid
```

If the invalid record is independent, record-level quarantine may be appropriate.

Now consider:

```text
1,000,000 records
500,000 invalid
```

The problem may be systemic.

Continuing with the remaining records could hide a producer outage or schema change.

A useful principle is:

> The scope of the response should match the scope of the defect.

## Examples

### One malformed order

```text
record-level quarantine
```

### Entire source schema changes

```text
batch-level failure
```

### Global referential integrity failure

Potentially:

```text
batch-level failure
```

### Temporary database outage

Usually:

```text
retry
```

rather than quarantine every record.

---

# 10. Thresholds

Suppose:

```text
invalid_records = 5
total_records = 1,000,000
```

Then:

```text
invalid_rate = 5 / 1,000,000
             = 0.0005%
```

A policy might allow valid records to continue while quarantining the five invalid records.

Now suppose:

```text
invalid_rate = 30%
```

A reasonable policy might instead:

```text
fail batch
alert owner
investigate producer
```

There is no universal threshold.

Thresholds should be based on:

- business impact;
- historical behavior;
- dataset criticality;
- known error rates;
- downstream tolerance.

A threshold should be a documented policy, not a random constant hidden in source code.

---

# 11. Quarantine Data Model

A production quarantine record should contain structured metadata.

A conceptual model:

| Field | Purpose |
|---|---|
| `quarantine_id` | Unique quarantine event |
| `run_id` | Identifies pipeline execution |
| `source` | Identifies producer/source system |
| `dataset` | Identifies affected dataset |
| `record_id` | Identifies source record |
| `received_at` | Source arrival time |
| `quarantined_at` | Quarantine time |
| `error_code` | Machine-readable defect |
| `error_message` | Human-readable detail |
| `validation_rule` | Rule that failed |
| `severity` | Operational priority |
| `original_payload` | Original evidence where safe |
| `schema_version` | Contract/schema version |
| `pipeline_stage` | Failure location |
| `retry_count` | Processing retry count |
| `status` | Lifecycle state |
| `owner` | Responsible team/domain |
| `replay_count` | Replay attempts |
| `last_replay_at` | Last replay timestamp |

This is metadata about the failure, not merely a copy of the bad payload.

---

# 12. Primary Keys and Idempotency

A quarantine system needs stable identifiers.

Possible identifiers:

```text
quarantine_id
```

for the quarantine event, and:

```text
record_id
```

for the source record.

A useful idempotency key could be:

```text
source + dataset + run_id + record_id
```

or a domain-specific event identifier.

The correct key depends on the source semantics.

Do not assume that a row number is a stable identity if the source can reorder rows.

---

# 13. Indexing and Partitioning

Quarantine data is operational data.

Useful query patterns include:

```text
find all failures for run X
find all failures for source Y
find all SCHEMA_MISMATCH errors
find all CRITICAL records
find oldest unresolved quarantine record
find records ready for replay
```

Potential partitioning dimensions:

```text
date
dataset
source
severity
schema_version
```

Do not partition solely because a field exists.

Partition based on actual access patterns and storage-engine behavior.

---

# 14. Retention

Quarantine data should have a retention policy.

For example:

```text
raw error payload
    → shorter retention

operational metadata
    → potentially longer retention
```

Retention depends on:

- operational recovery needs;
- compliance;
- cost;
- privacy;
- security;
- audit requirements.

A quarantine repository should not become an accidental permanent copy of every sensitive production payload.

---

# 15. Preserving the Original Record

Suppose:

```text
quantity = "-5"
```

An automated repair changes it to:

```text
quantity = "5"
```

If only the repaired record remains, forensic evidence has been lost.

A stronger model preserves:

```text
original_payload
normalized_payload
correction_reason
corrected_by
corrected_at
```

However, preserving the original payload must be balanced against privacy and security.

Do not store sensitive data merely because it is convenient for debugging.

---

# 16. Error Taxonomy

Use machine-readable error codes.

Examples:

```text
SCHEMA_MISMATCH
MISSING_REQUIRED_FIELD
INVALID_TYPE
INVALID_VALUE
NULLABILITY_VIOLATION
DUPLICATE_RECORD
REFERENTIAL_INTEGRITY_FAILURE
BUSINESS_RULE_VIOLATION
MALFORMED_PAYLOAD
CONTRACT_VIOLATION
```

Prefer:

```json
{
  "error_code": "MISSING_REQUIRED_FIELD",
  "error_message": "currency is required"
}
```

over relying only on:

```text
"something went wrong"
```

Machine-readable codes enable:

- aggregation;
- alert routing;
- dashboards;
- ownership;
- automated policies;
- trend analysis.

---

# 17. Error Severity

Not every validation failure should become a critical incident.

A simple severity model:

```text
INFO
WARNING
ERROR
CRITICAL
```

Example:

| Failure | Possible Severity |
|---|---|
| Optional descriptive field missing | WARNING |
| Invalid non-critical enrichment | ERROR |
| Contract violation affecting critical data | CRITICAL |
| One quarantined record in a low-risk feed | INFO/WARNING |

Severity must be contextual.

---

# 18. End-to-End Bad-Record Flow

A complete flow:

```text
Ingest
  ↓
Validate
  ↓
Valid?
 ┌───────┴────────┐
Yes               No
 ↓                 ↓
Normal          Classify
flow               ↓
                 Quarantine
                    ↓
              Alert / Record
                    ↓
                 Investigate
                    ↓
                  Repair
                    ↓
                  Replay
                    ↓
                Revalidate
                    ↓
                 Process
                    ↓
                  Audit
                    ↓
                 Publish
```

Every transition should have observable state.

---

# 19. Python Implementation: Basic Record Handling

Start with standard Python.

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ValidationFailure:
    error_code: str
    error_message: str
    field: str | None = None


@dataclass
class QuarantineRecord:
    quarantine_id: str
    run_id: str
    record_id: str
    source: str
    dataset: str
    original_payload: dict[str, Any]
    error_code: str
    error_message: str
    quarantined_at: datetime
    status: str = "NEW"
    replay_count: int = 0
```

A simple validator:

```python
def validate_record(record: dict[str, Any]) -> list[ValidationFailure]:
    failures: list[ValidationFailure] = []

    if "order_id" not in record:
        failures.append(
            ValidationFailure(
                error_code="MISSING_REQUIRED_FIELD",
                error_message="order_id is required",
                field="order_id",
            )
        )

    if "quantity" not in record:
        failures.append(
            ValidationFailure(
                error_code="MISSING_REQUIRED_FIELD",
                error_message="quantity is required",
                field="quantity",
            )
        )
    elif not isinstance(record["quantity"], int):
        failures.append(
            ValidationFailure(
                error_code="INVALID_TYPE",
                error_message="quantity must be an integer",
                field="quantity",
            )
        )

    if isinstance(record.get("quantity"), int):
        if record["quantity"] <= 0:
            failures.append(
                ValidationFailure(
                    error_code="INVALID_VALUE",
                    error_message="quantity must be positive",
                    field="quantity",
                )
            )

    return failures
```

The validator returns structured failures rather than printing errors.

---

# 20. Classifying a Record

```python
def classify_record(record: dict[str, Any]) -> list[ValidationFailure]:
    return validate_record(record)
```

For a production system, classification would usually consider:

- validation failures;
- severity;
- retryability;
- business impact;
- batch-level state.

The important separation is:

```text
validation
    ≠
operational decision
```

Validation tells us what is wrong.

Policy decides what to do.

---

# 21. Quarantine Function

```python
from uuid import uuid4


def quarantine_record(
    *,
    run_id: str,
    record_id: str,
    source: str,
    dataset: str,
    record: dict[str, Any],
    failure: ValidationFailure,
) -> QuarantineRecord:
    return QuarantineRecord(
        quarantine_id=str(uuid4()),
        run_id=run_id,
        record_id=record_id,
        source=source,
        dataset=dataset,
        original_payload=record,
        error_code=failure.error_code,
        error_message=failure.error_message,
        quarantined_at=datetime.now(timezone.utc),
    )
```

In a real system, the generated record would then be persisted to a secure quarantine destination.

---

# 22. Processing a Batch

```python
def process_batch(
    records: list[dict[str, Any]],
    run_id: str,
) -> tuple[list[dict[str, Any]], list[QuarantineRecord]]:
    valid_records: list[dict[str, Any]] = []
    quarantined: list[QuarantineRecord] = []

    for index, record in enumerate(records):
        failures = validate_record(record)

        if not failures:
            valid_records.append(record)
            continue

        for failure in failures:
            quarantined.append(
                quarantine_record(
                    run_id=run_id,
                    record_id=str(record.get("order_id", index)),
                    source="orders_api",
                    dataset="orders",
                    record=record,
                    failure=failure,
                )
            )

    return valid_records, quarantined
```

This is intentionally educational.

A production implementation should also define:

- duplicate handling;
- multi-error aggregation;
- stable source IDs;
- persistence semantics;
- thresholds;
- retryability;
- audit;
- metrics;
- security controls.

---

# 23. Bad Example: Silent Data Loss

This code is dangerous:

```python
valid = []

for record in records:
    try:
        validate_record(record)
        valid.append(record)
    except Exception:
        pass
```

Problems:

- invalid records disappear;
- error reason is lost;
- source identity is lost;
- replay is impossible;
- incident investigation is harder;
- reconciliation cannot prove where records went.

A safer pattern is:

```python
valid = []
quarantined = []

for record in records:
    failures = validate_record(record)

    if not failures:
        valid.append(record)
    else:
        quarantined.append(
            {
                "record": record,
                "failures": failures,
            }
        )
```

The key improvement is preservation.

---

# 24. Pydantic + Quarantine

Pydantic can validate an individual record.

Example:

```python
from pydantic import BaseModel, ValidationError


class Order(BaseModel):
    order_id: int
    quantity: int
    currency: str


def validate_with_pydantic(record: dict) -> Order | None:
    try:
        return Order.model_validate(record)
    except ValidationError:
        return None
```

For quarantine, do not throw away the validation details.

Instead:

```python
def validate_and_capture(record: dict):
    try:
        order = Order.model_validate(record)
        return {
            "valid": True,
            "record": order,
        }

    except ValidationError as exc:
        return {
            "valid": False,
            "record": record,
            "errors": exc.errors(),
        }
```

The error payload can be translated into structured quarantine metadata:

```text
record
validation errors
field path
timestamp
source
run_id
```

Do not reproduce the full Pydantic lesson here; use its validation errors as an integration point.

---

# 25. Pandera + Quarantine

For a DataFrame:

```text
DataFrame
   ↓
Pandera validation
   ↓
failure_cases
   ↓
identify affected records
   ↓
quarantine
```

A conceptual example:

```python
import pandas as pd
import pandera.pandas as pa


schema = pa.DataFrameSchema(
    {
        "order_id": pa.Column(int, nullable=False),
        "quantity": pa.Column(int, checks=pa.Check.gt(0), nullable=False),
    }
)

orders = pd.DataFrame(
    {
        "order_id": [1, 2, 3],
        "quantity": [2, -1, 4],
    }
)
```

When validation is configured to expose failure cases, those failures can feed the quarantine process.

A key difficulty is mapping DataFrame-level failures back to source records.

Therefore preserve a stable identifier:

```text
source_record_id
```

rather than relying only on the DataFrame index.

---

# 26. Great Expectations / Soda + Quarantine

Quality frameworks can produce results such as:

```text
check:
    order_quantity_positive

result:
    failed

observed:
    invalid_count = 50
```

The framework reports a quality result.

The pipeline policy decides what happens:

```text
Quality result
      ↓
Policy
      ├── FAIL
      ├── QUARANTINE
      ├── FLAG
      ├── ALERT
      └── CONTINUE
```

A failed check does not automatically mean every record should be quarantined.

For example, a dataset-level freshness check may require batch failure rather than record quarantine.

---

# 27. Batch Processing Design

A production-oriented batch pattern:

```text
Read batch
   ↓
Validate
   ↓
Split valid / invalid
   ↓
Persist quarantine
   ↓
Write valid output
   ↓
Audit
   ↓
Publish
```

Ordering matters.

You do not want:

```text
Publish
   ↓
discover validation failure
   ↓
try to reconstruct what happened
```

The system should establish evidence and state before making the dataset visible to consumers.

---

# 28. Write-Audit-Publish

This pattern is especially useful for reliable batch pipelines.

```text
WRITE
  ↓
AUDIT
  ↓
PUBLISH
```

## WRITE

Write validated output to a staging location.

Example:

```text
staging/orders/run_id=123
```

## AUDIT

Record:

```text
input count
valid count
quarantine count
error counts
schema version
run ID
quality results
```

## PUBLISH

Promote the validated result to the consumer-facing location.

Conceptually:

```text
staging
   ↓
validated + audited
   ↓
published
```

The exact atomicity mechanism depends on the storage system.

---

# 29. Atomicity and Partial Failure

Consider:

```text
valid data write succeeds
```

but:

```text
quarantine write fails
```

or:

```text
audit write fails
```

You may now have an inconsistent state.

For example:

```text
999,950 valid records published
50 invalid records
but no evidence exists for the 50
```

This violates the operational objective.

Possible mechanisms include:

- database transactions;
- staging tables;
- atomic promotion;
- atomic rename where the storage system supports it;
- idempotent writes;
- commit markers;
- publish flags.

Do not assume every database, object store, or table format provides identical transaction semantics.

Design around the guarantees of the actual storage system.

---

# 30. Partial Publishing

Suppose:

```text
99.99% valid
0.01% invalid
```

It may be reasonable to:

```text
publish valid records
quarantine invalid records
```

But consider:

```text
referential integrity globally broken
```

If every customer identifier suddenly fails, publishing partial orders could create an unusable downstream dataset.

The correct decision depends on whether the valid subset is independently meaningful.

The question is:

> Can the valid subset safely represent the business state without violating global invariants?

---

# 31. Circuit Breakers

A circuit breaker protects a pipeline from repeatedly processing data when evidence suggests a systemic failure.

Conceptually:

```text
Failure rate normal
      ↓
CLOSED
      ↓
process normally

Failure rate exceeds policy
      ↓
OPEN
      ↓
stop normal processing
      ↓
investigate / repair
      ↓
recovery
      ↓
HALF-OPEN
      ↓
test
      ↓
CLOSED
```

Circuit breakers are useful when:

- schema suddenly changes;
- invalid-record rate spikes;
- a producer malfunctions;
- an upstream dependency returns corrupted payloads.

The key distinction:

```text
individual bad record
    → quarantine

systemic failure
    → circuit breaker / batch failure
```

---

# 32. Dead-Letter Queues

A common streaming pattern:

```text
Event stream
    ↓
Consumer
    ↓
Validate / process
    ├── success → downstream
    │
    └── failure
          ↓
        retry
          ↓
        DLQ
          ↓
      investigation
          ↓
        repair
          ↓
        replay
```

A DLQ typically preserves:

- failed message;
- source metadata;
- failure reason;
- attempt count;
- timestamps;
- schema/version information where relevant.

Real brokers have different delivery, ordering, retention, transaction, and replay semantics. This lesson does not assume a universal broker guarantee.

---

# 33. Retry vs DLQ

Retries are appropriate for failures that may succeed later.

Examples:

- temporary network error;
- transient database outage;
- temporary dependency unavailability.

DLQ/quarantine is appropriate for persistent failures.

Examples:

- malformed payload;
- deterministic validation failure;
- poison message;
- persistent contract violation.

The decision:

```text
Is the failure likely to change without changing the input?
```

If yes:

```text
retry may help
```

If no:

```text
retrying indefinitely is wasteful
```

---

# 34. Poison Messages

A **poison message** is a message that repeatedly fails because its content or processing condition is persistently invalid.

Example:

```json
{
  "order_id": 1001
}
```

when `currency` is mandatory.

A naive system can do:

```text
retry
 ↓
failure
 ↓
retry
 ↓
failure
 ↓
retry
 ↓
failure
```

This creates:

- retry storms;
- latency;
- duplicate work;
- resource exhaustion.

A better policy:

```text
retry according to bounded policy
        ↓
persistent failure
        ↓
DLQ
```

---

# 35. Retry Policies

Common retry approaches include:

### Immediate Retry

Useful for very short transient failures.

### Fixed Delay

Wait a configured interval before trying again.

### Exponential Backoff

Increase delay after repeated failures.

Conceptually:

```text
attempt 1 → short delay
attempt 2 → longer delay
attempt 3 → longer again
```

### Jitter

Add controlled randomness to avoid synchronized retry bursts.

### Maximum Attempts

Bound the amount of retry work.

There is no universal retry count.

The policy should depend on:

- failure type;
- dependency behavior;
- latency requirements;
- cost;
- idempotency;
- downstream capacity.

---

# 36. Idempotency

Replay is dangerous if processing the same record twice creates duplicate effects.

Suppose:

```text
event_id = 123
```

is processed successfully, but the consumer crashes before acknowledging completion.

The message may be delivered again.

Without idempotency:

```text
charge customer
charge customer
```

could happen twice.

The goal is:

> Reprocessing the same logical input should not create unintended duplicate effects.

Possible identifiers include:

```text
event_id
order_id + event_type
source_file + row_number
source_batch_id + record_id
```

The correct key depends on domain semantics.

---

# 37. Idempotency for Different Destinations

## Database Writes

Use:

- unique constraints;
- upserts;
- idempotency keys;
- deterministic merge logic.

## API Calls

Use an API-supported idempotency key when the API provides that mechanism.

## File Publishing

Use deterministic paths or commit markers where appropriate.

## Event Processing

Track processed event IDs or use an equivalent domain-level mechanism.

## Quarantine Replay

The replay system must know whether a quarantine record has already been successfully applied.

---

# 38. Replay

Replay is the controlled attempt to process previously quarantined data again.

Flow:

```text
Quarantine
   ↓
Fix root cause
   ↓
Select records
   ↓
Replay
   ↓
Validate
   ↓
Process
   ↓
Audit
   ↓
Publish
```

Replay should be:

- controlled;
- observable;
- idempotent;
- traceable;
- associated with lineage.

Do not build a button called `replay_all()` without safeguards.

---

# 39. Replay Metadata

Useful metadata:

```text
replay_id
original_run_id
quarantine_id
replay_attempt
replayed_at
replay_reason
replay_operator/system
result
new_run_id
```

Example:

```json
{
  "replay_id": "rpl-001",
  "original_run_id": "run-2026-10-01",
  "quarantine_id": "q-991",
  "replay_attempt": 2,
  "replay_reason": "producer_fixed_currency_mapping",
  "result": "SUCCESS"
}
```

This provides an audit trail.

---

# 40. Quarantine Lifecycle

A useful state machine:

```text
NEW
 ↓
TRIAGED
 ↓
REPAIRING
 ↓
READY_FOR_REPLAY
 ↓
REPLAYED
 ↓
VERIFIED
 ↓
CLOSED
```

A permanent rejection path may be:

```text
NEW
 ↓
TRIAGED
 ↓
PERMANENTLY_REJECTED
```

Example meanings:

### NEW

Detected but not reviewed.

### TRIAGED

Failure classified and owner assigned.

### REPAIRING

Root cause or record is being corrected.

### READY_FOR_REPLAY

Correction is complete.

### REPLAYED

Replay has been executed.

### VERIFIED

Replay result passed verification.

### CLOSED

Operational lifecycle complete.

### PERMANENTLY_REJECTED

Policy explicitly says the record should not re-enter the pipeline.

---

# 41. Ownership and Alerting

Every quarantine system needs ownership.

Possible owners:

- producer team;
- data platform team;
- data engineering team;
- domain owner.

The correct owner depends on the contract and defect.

A useful alert contains:

```text
dataset
source
error rate
severity
sample errors
run ID
owner
remediation process
```

Compare:

```text
BAD:
"Pipeline failed."
```

with:

```text
BETTER:
orders ingestion
invalid rate: 4.2%
error: INVALID_TYPE
run: run-2026-10-01-001
owner: orders-data-product
affected records: 21,000
action: producer schema investigation
```

Operational context reduces time-to-diagnosis.

---

# 42. Alert Fatigue

Do not alert on every individual bad row.

If 50,000 records fail for the same reason, sending 50,000 alerts is operationally harmful.

Prefer:

- threshold-based alerts;
- aggregated alerts;
- severity-based routing;
- rate-of-change alerts;
- critical error-class alerts.

Example:

```text
50 individual INVALID_TYPE failures
```

should generally become:

```text
1 aggregated alert:
INVALID_TYPE = 50
```

The individual records remain available in quarantine.

---

# 43. PII and Security Hygiene

Quarantine can become one of the most sensitive data stores in the platform.

A bad payload may contain:

- personally identifiable information;
- payment data;
- credentials;
- tokens;
- sensitive business information.

Bad design:

```text
store entire payload forever
```

Better principles:

- data minimization;
- masking;
- redaction;
- encryption;
- access control;
- retention limits;
- audit logging;
- secure storage.

The debugging requirement to preserve evidence does not override security requirements.

---

# 44. Payment-Like Example

Suppose a malformed payload contains:

```json
{
  "order_id": 1001,
  "customer_email": "example@example.invalid",
  "card_number": "SYNTHETIC_ONLY",
  "cvv": "SYNTHETIC_ONLY"
}
```

Do not blindly store all fields in a quarantine table.

A sanitized representation could be:

```json
{
  "order_id": 1001,
  "customer_email": "[REDACTED]",
  "card_number": "[REDACTED]",
  "cvv": "[REDACTED]",
  "error_code": "CONTRACT_VIOLATION"
}
```

The example uses synthetic values only.

The production policy should define which fields may be retained and in what form.

---

# 45. Quarantine Storage Options

| Option | Strengths | Trade-offs |
|---|---|---|
| Relational table | Queryable, structured | Write volume and scaling considerations |
| Object storage | High scale, inexpensive bulk storage | More work for querying/replay |
| Event-stream DLQ | Natural for streaming | Broker-specific semantics |
| Key-value store | Fast targeted access | Less convenient for analytical investigation |
| Dedicated error store | Purpose-built operations | Additional infrastructure |

There is no universal winner.

Choose based on:

- scale;
- queryability;
- replay;
- retention;
- operational complexity;
- security.

---

# 46. Partitioning and Retention

Useful partition dimensions can include:

```text
date
dataset
source
severity
schema_version
```

For example:

```text
quarantine/
  dataset=orders/
    date=2026-10-01/
      severity=ERROR/
```

But partitioning should be based on actual workload patterns.

Retention may differ by data type:

```text
raw payload
    → limited retention

failure metadata
    → potentially longer retention
```

Always account for:

- operational recovery;
- compliance;
- cost;
- privacy;
- security.

---

# 47. Observability

Monitor the quarantine system itself.

Important measurements include:

```text
invalid_record_count
invalid_record_rate
quarantine_count
dlq_depth
oldest_quarantined_record_age
replay_success_rate
replay_failure_rate
top_error_codes
processing_latency
retry_count
circuit_breaker_state
```

These answer operational questions such as:

- Are bad records increasing?
- Is the DLQ accumulating?
- Are records getting stuck?
- Is replay working?
- Which producer is failing?
- Is the problem systemic?

A quarantine system without observability can become a silent data graveyard.

---

# 48. Reconciliation Connection

Suppose:

```text
input = 1,000,000
valid = 999,950
quarantined = 50
```

Then:

```text
1,000,000
    =
999,950 + 50
```

The counts should reconcile according to the pipeline's defined accounting rules.

This is important because otherwise records may disappear between stages.

Quarantine therefore contributes to reconciliation:

```text
input
  =
published
+
quarantined
+
explicitly rejected
```

The exact accounting categories depend on the pipeline.

---

# 49. Data-Loss Prevention

Dangerous pattern:

```python
valid_df = df[valid_mask]
```

If `invalid_df` is not persisted, invalid records have silently disappeared.

Safer:

```python
valid_df = df[valid_mask].copy()
invalid_df = df[~valid_mask].copy()

# Persist invalid_df to quarantine.
# Persist valid_df to the normal staging path.
```

The key is not the syntax.

The key is explicit accounting:

```text
valid
+
invalid
=
input
```

subject to the dataset's defined duplicate and filtering rules.

---

# 50. DataFrame Batch Implementation

A practical pattern:

```python
import pandas as pd


def split_orders(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    valid = (
        df["quantity"].notna()
        & (df["quantity"] > 0)
        & df["currency"].isin(["USD", "EUR", "GBP"])
    )

    valid_df = df.loc[valid].copy()
    invalid_df = df.loc[~valid].copy()

    return valid_df, invalid_df
```

Preserve a stable source identifier:

```text
source_record_id
```

rather than assuming:

```text
DataFrame index = permanent record identity
```

This becomes especially important after:

- sorting;
- concatenation;
- filtering;
- repartitioning;
- distributed processing.

---

# 51. Streaming / DLQ Simulation

A simple conceptual Python simulation:

```python
def process_message(message: dict) -> bool:
    failures = validate_record(message)

    if failures:
        return False

    return True


def consume(messages: list[dict]) -> tuple[list[dict], list[dict]]:
    processed = []
    dlq = []

    for message in messages:
        if process_message(message):
            processed.append(message)
        else:
            dlq.append(message)

    return processed, dlq
```

A production stream processor additionally needs to define:

- acknowledgment semantics;
- retry policy;
- ordering requirements;
- partitioning;
- deduplication;
- offset/checkpoint behavior;
- DLQ retention;
- replay mechanics.

Those are broker- and platform-specific.

---

# 52. Defect Injection Lab

Use a synthetic orders dataset.

Example:

```python
records = [
    {
        "order_id": 1,
        "quantity": 2,
        "currency": "USD",
    },
    {
        "order_id": 2,
        "quantity": -1,
        "currency": "USD",
    },
]
```

Inject these defects:

1. missing required field;
2. invalid type;
3. negative quantity;
4. invalid currency;
5. duplicate order;
6. invalid timestamp;
7. referential integrity failure;
8. business-rule failure;
9. malformed JSON;
10. schema drift.

For each defect:

```text
Inject
  ↓
Validate
  ↓
Classify
  ↓
Quarantine
  ↓
Inspect
  ↓
Repair
  ↓
Replay
  ↓
Verify
```

The objective is not merely to produce errors.

The objective is to exercise the full recovery lifecycle.

---

# 53. Complete Hands-On Python Workflow

The following educational implementation brings the concepts together.

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class QuarantineItem:
    quarantine_id: str
    run_id: str
    record_id: str
    error_code: str
    error_message: str
    original_record: dict
    status: str = "NEW"
    replay_count: int = 0
    created_at: datetime = datetime.now(timezone.utc)


def validate_order(record: dict) -> list[dict]:
    errors = []

    if "order_id" not in record:
        errors.append(
            {
                "error_code": "MISSING_REQUIRED_FIELD",
                "field": "order_id",
                "message": "order_id is required",
            }
        )

    if not isinstance(record.get("quantity"), int):
        errors.append(
            {
                "error_code": "INVALID_TYPE",
                "field": "quantity",
                "message": "quantity must be an integer",
            }
        )

    elif record["quantity"] <= 0:
        errors.append(
            {
                "error_code": "INVALID_VALUE",
                "field": "quantity",
                "message": "quantity must be positive",
            }
        )

    allowed_currencies = {"USD", "EUR", "GBP"}

    if record.get("currency") not in allowed_currencies:
        errors.append(
            {
                "error_code": "INVALID_VALUE",
                "field": "currency",
                "message": "currency is not supported",
            }
        )

    return errors


def quarantine_record(
    *,
    run_id: str,
    record: dict,
    error: dict,
) -> QuarantineItem:
    return QuarantineItem(
        quarantine_id=str(uuid4()),
        run_id=run_id,
        record_id=str(record.get("order_id", "unknown")),
        error_code=error["error_code"],
        error_message=error["message"],
        original_record=record.copy(),
        created_at=datetime.now(timezone.utc),
    )


def process_batch(
    records: list[dict],
    run_id: str,
) -> tuple[list[dict], list[QuarantineItem]]:
    valid = []
    quarantine = []

    for record in records:
        errors = validate_order(record)

        if not errors:
            valid.append(record)
            continue

        for error in errors:
            quarantine.append(
                quarantine_record(
                    run_id=run_id,
                    record=record,
                    error=error,
                )
            )

    return valid, quarantine
```

This code demonstrates:

- validation;
- structured errors;
- quarantine metadata;
- run identity;
- record identity;
- original-record preservation;
- separation of valid and invalid records.

A production system would persist these objects and add the operational controls discussed below.

---

# 54. Replay Function

A replay function should not blindly resend every quarantine item.

A conceptual implementation:

```python
def replay_quarantined(
    items: list[QuarantineItem],
) -> list[QuarantineItem]:
    results = []

    for item in items:
        if item.status not in {"READY_FOR_REPLAY", "NEW"}:
            continue

        item.replay_count += 1

        failures = validate_order(item.original_record)

        if failures:
            item.status = "NEW"
        else:
            item.status = "REPLAYED"

        results.append(item)

    return results
```

This is intentionally simplified.

A real replay process should also include:

- replay ID;
- replay reason;
- original run ID;
- new run ID;
- idempotency protection;
- audit;
- metrics;
- authorization;
- controlled selection;
- verification.

---

# 55. Reconciliation Function

A simple reconciliation function:

```python
def reconcile_counts(
    input_count: int,
    valid_count: int,
    quarantine_count: int,
) -> None:
    accounted_for = valid_count + quarantine_count

    if accounted_for != input_count:
        raise ValueError(
            "Record accounting does not reconcile: "
            f"input={input_count}, "
            f"valid={valid_count}, "
            f"quarantine={quarantine_count}"
        )
```

This turns an operational assumption into a testable invariant.

---

# 56. Circuit Breaker Simulation

A minimal educational model:

```python
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, threshold: float):
        self.threshold = threshold
        self.state = CircuitState.CLOSED

    def evaluate(self, invalid_rate: float) -> CircuitState:
        if invalid_rate >= self.threshold:
            self.state = CircuitState.OPEN

        return self.state

    def reset(self) -> None:
        self.state = CircuitState.CLOSED
```

Example:

```python
breaker = CircuitBreaker(threshold=0.20)

state = breaker.evaluate(invalid_rate=0.35)

print(state)
```

The exact threshold is deliberately a policy parameter.

It is not a universal recommendation.

A full production circuit breaker would also manage:

- recovery timing;
- half-open probes;
- metrics;
- state persistence where required;
- alerting;
- operator controls.

---

# 57. Write-Audit-Publish Project

## Project: Reliable Orders Pipeline with Quarantine and Replay

Build this logical pipeline:

```text
Source
  ↓
Ingest
  ↓
Contract Validation
  ↓
Record Validation
  ├── Valid ──────→ Transform → Staging
  │                              ↓
  │                            Audit
  │                              ↓
  │                           Publish
  │
  └── Invalid → Quarantine
                   ↓
                Diagnose
                   ↓
                 Repair
                   ↓
                 Replay
                   ↓
               Revalidate
                   ↓
                 Audit
                   ↓
                Publish
```

The project must demonstrate:

- valid records;
- invalid records;
- quarantine;
- structured errors;
- audit;
- publish;
- replay;
- idempotency;
- reconciliation;
- alerting;
- ownership;
- defect injection;
- tests.

Keep implementation inside this Markdown lesson if you are using it as the learning artifact; do not require external helper files to understand the design.

---

# 58. Testing Strategy

## Unit Tests

Test:

- validation;
- error classification;
- quarantine record creation;
- replay logic;
- reconciliation;
- threshold evaluation.

## Integration Tests

Test:

- quarantine persistence;
- replay;
- publish;
- audit;
- error-path persistence.

## Failure Tests

Inject:

- unavailable quarantine storage;
- duplicate replay;
- malformed payload;
- threshold exceeded;
- schema drift.

## Idempotency Test

Replay the same logical record twice.

Expected:

```text
no unintended duplicate effect
```

The exact implementation depends on the target system.

---

# 59. Performance Engineering

Bad-record handling can become a performance bottleneck.

Consider:

- per-record validation cost;
- batch validation;
- serialization overhead;
- quarantine writes;
- database inserts;
- object-storage writes;
- DLQ throughput;
- replay throughput.

Avoid:

```text
INSERT one quarantine row
INSERT one quarantine row
INSERT one quarantine row
...
```

when the storage system supports efficient batching.

Instead, consider:

```text
collect quarantine records
        ↓
batch write
```

But do not batch so aggressively that memory usage or recovery latency becomes unsafe.

Benchmark the actual implementation.

Do not invent benchmark numbers.

---

# 60. Failure Scenario 1 — One Malformed Record in a Million

Input:

```text
1,000,000
```

Invalid:

```text
1
```

Possible response:

```text
quarantine one record
continue valid records
emit aggregated alert if policy requires
reconcile counts
```

Investigate:

- source;
- error code;
- producer;
- whether this is normal historical behavior.

---

# 61. Failure Scenario 2 — Thirty Percent Invalid

Input:

```text
1,000,000
```

Invalid:

```text
300,000
```

Possible interpretation:

```text
systemic failure
```

Potential response:

```text
open circuit
stop publishing
quarantine affected evidence
alert owner
investigate producer/schema
```

The exact response depends on the business contract.

---

# 62. Failure Scenario 3 — Entire Schema Changes

Expected:

```text
customer_id: integer
```

Actual:

```text
customer_id: object
```

across the batch.

This may indicate schema drift.

Possible response:

```text
fail batch
preserve sample/failed records safely
alert producer
block publish
```

This is usually different from one malformed record.

---

# 63. Failure Scenario 4 — Temporary Database Outage

Suppose validation succeeds but the target database is unavailable.

This is not automatically a bad-record problem.

A transient infrastructure failure may require:

```text
retry with backoff
```

rather than:

```text
quarantine every valid record
```

This distinction prevents misuse of quarantine.

---

# 64. Failure Scenario 5 — Poison Message

A message always fails because:

```text
required field missing
```

Repeated retries produce:

```text
retry storm
```

Better:

```text
bounded retries
    ↓
DLQ
    ↓
repair producer or record
    ↓
replay
```

---

# 65. Failure Scenario 6 — Quarantine Storage Fails

Suppose:

```text
record validation fails
```

but:

```text
quarantine destination unavailable
```

The pipeline now has a difficult safety decision.

Do not simply:

```text
drop record
```

Possible policies include:

- fail the batch;
- buffer safely where the system guarantees durability;
- pause processing;
- use an alternate durable destination.

The policy must be explicit.

The key principle is:

> If preservation of failed records is a correctness requirement, failure of the quarantine mechanism can itself be a pipeline-critical failure.

---

# 66. Failure Scenario 7 — Replay Creates Duplicates

A quarantined record is replayed twice.

If processing is not idempotent:

```text
duplicate database row
```

or:

```text
duplicate downstream event
```

may result.

Investigation:

1. Identify replay ID.
2. Identify source record ID.
3. Check idempotency key.
4. Check target write semantics.
5. Determine whether the first replay committed.
6. Correct duplicate state.
7. Strengthen replay controls.

---

# 67. Failure Scenario 8 — Sensitive Data in Quarantine

A failed payload contains sensitive data.

Immediate priorities:

```text
restrict access
minimize exposure
redact where possible
apply retention
audit access
```

Do not create an unrestricted debugging table containing full production payloads.

---

# 68. Failure Scenario 9 — Slowly Increasing Invalid Rate

Suppose:

```text
Monday: 0.01%
Tuesday: 0.02%
Wednesday: 0.04%
Thursday: 0.10%
Friday: 0.30%
```

No single day may cross a catastrophic threshold.

But the trend is operationally important.

Monitor:

```text
invalid rate over time
error-code distribution
producer changes
schema versions
```

This can identify degradation before a large outage.

---

# 69. Failure Scenario 10 — Producer Does Not Respond

If the owning producer team does not respond:

- maintain the documented policy;
- keep affected records preserved;
- prevent unsafe publication if required;
- escalate through established ownership channels;
- avoid indefinite retries;
- track unresolved quarantine age.

The system should not depend on an individual engineer manually remembering what happened.

---

# 70. Streaming Replay Considerations

Streaming replay introduces additional concerns:

```text
ordering
offsets/checkpoints
partitioning
duplicates
retention
consumer state
```

A replay mechanism should define whether replay:

- re-inserts into the original stream;
- publishes to a dedicated replay stream;
- calls the consumer directly;
- creates a new processing run.

Do not assume replaying a message is equivalent to rewinding a broker.

Broker-specific semantics must be documented separately.

---

# 71. Batch Replay Considerations

Batch replay may be simpler:

```text
quarantine partition
    ↓
select records
    ↓
repair
    ↓
new run
    ↓
validate
    ↓
write staging
    ↓
audit
    ↓
publish
```

The replay should receive a new run ID while retaining the original run ID for lineage.

---

# 72. Ownership Model

A useful responsibility model:

| Responsibility | Typical Owner |
|---|---|
| Producer correctness | Producer/domain team |
| Validation framework | Data platform |
| Quarantine infrastructure | Data platform / Data Engineering |
| Business-rule definition | Domain owner |
| Replay approval | Data owner / authorized operator |
| Security policy | Security / governance |
| Consumer remediation | Consumer team |

The exact organization varies.

The important principle is:

> Every failure needs an accountable owner.

---

# 73. Quarantine as an Operational Data Product

A mature quarantine system can itself become an operational dataset.

It can answer:

```text
Which producers generate the most invalid records?
Which error codes are increasing?
Which datasets have the oldest unresolved failures?
How long does repair take?
What percentage of quarantined records successfully replay?
Which records are permanently rejected?
```

This enables continuous improvement.

The quarantine system should therefore be observable and governed like other production data systems.

---

# 74. Production Architecture

A production architecture can be represented as:

```text
                 Producer
                    ↓
                Ingestion
                    ↓
             Contract Validation
                    ↓
              Record Validation
               ┌────┴────┐
               ↓         ↓
             Valid     Invalid
               ↓         ↓
           Transform  Quarantine / DLQ
               ↓         ↓
            Quality    Diagnose
               ↓         ↓
             Audit      Repair
               ↓         ↓
            Publish    Replay
               ↓         ↓
            Consumer ←──┘
```

Supporting systems:

```text
                 ┌───────────────┐
                 │ Observability │
                 └───────┬───────┘
                         ↓
Validation → Audit → Quarantine → Replay
                         ↑
                      Ownership
```

Place:

- quarantine near the validation failure boundary;
- DLQ near stream-processing failure boundaries;
- audit around state transitions;
- replay behind controlled operational interfaces;
- alerting around actionable conditions.

---

# 75. Interview Questions and Answers

## Basic

### Q1. What is quarantine?

A controlled holding area for records that cannot safely continue through the normal pipeline, while preserving evidence for investigation and recovery.

### Q2. What is a DLQ?

A destination for messages that could not be successfully processed, commonly used in messaging and streaming systems.

### Q3. Why not drop invalid records?

Dropping destroys evidence and can cause silent data loss, making investigation, reconciliation, and replay difficult or impossible.

### Q4. What is a bad record?

A record that violates a structural, syntactic, semantic, contractual, referential, or business rule and therefore cannot safely proceed.

### Q5. What is replay?

A controlled attempt to process previously quarantined or dead-lettered data again after the underlying issue has been addressed.

---

## Intermediate

### Q6. Fail vs quarantine?

Fail when continuing would make the dataset unsafe or misleading. Quarantine when individual records can be isolated without compromising the valid subset.

### Q7. Retry vs DLQ?

Retry transient failures. Route deterministic or persistent processing failures to a DLQ/quarantine rather than retrying indefinitely.

### Q8. Record-level vs batch-level failure?

Record-level handling isolates independently invalid records. Batch-level failure is appropriate when the defect indicates a systemic or global problem.

### Q9. Why use thresholds?

Thresholds provide an explicit policy for deciding when an error rate changes from isolated defects to a systemic failure.

### Q10. What is idempotency?

The property that repeated processing of the same logical input does not create unintended duplicate effects.

### Q11. What is a poison message?

A message that repeatedly fails because its contents or processing condition are persistently invalid.

---

## Advanced

### Q12. How would you design a quarantine system?

Define structured metadata, stable record/run IDs, error taxonomy, retention, security, ownership, storage, replay, idempotency, monitoring, and lifecycle states.

### Q13. How do you prevent replay duplicates?

Use stable idempotency keys and idempotent target operations such as unique constraints, upserts, or equivalent domain-specific mechanisms.

### Q14. How do you handle millions of quarantined records?

Use scalable storage, partitioning, indexed metadata, batch operations, controlled replay windows, rate limiting, ownership, and observability.

### Q15. How do you secure quarantine storage?

Minimize retained sensitive data, redact where possible, encrypt, restrict access, audit access, and enforce retention.

### Q16. How do you handle partial publishing?

First determine whether the valid subset is independently meaningful. If global invariants are violated, fail or stop publication instead of publishing an unsafe partial result.

---

# 76. Architecture Interview Questions

## Design a Production Ingestion System with Quarantine

Requirements:

```text
10M records/day
record-level validation
batch-level safety
replay
audit
PII protection
```

A reasonable design:

```text
source
  ↓
ingestion
  ↓
validation
  ├── valid → staging → audit → publish
  │
  └── invalid → quarantine
                   ↓
                ownership
                   ↓
                 repair
                   ↓
                 replay
```

Add:

```text
metrics
alerts
retention
access control
idempotency
```

---

## Design a Streaming DLQ

```text
producer
   ↓
stream
   ↓
consumer
   ↓
validation
   ├── success → downstream
   └── failure → bounded retry → DLQ
                                  ↓
                               repair
                                  ↓
                                replay
```

The design must define:

- retry policy;
- poison-message behavior;
- idempotency;
- ordering implications;
- DLQ retention;
- replay path;
- monitoring.

---

## Design Write-Audit-Publish

```text
input
 ↓
validate
 ↓
write staging
 ↓
audit
 ↓
publish
```

The publish step should occur only after the required validation and audit evidence exists.

---

## Design Circuit-Breaker Behavior

```text
normal
 ↓
error rate rises
 ↓
threshold exceeded
 ↓
open circuit
 ↓
stop unsafe processing
 ↓
repair
 ↓
half-open test
 ↓
resume
```

---

## Design Replay at Scale

Requirements:

```text
millions of quarantined records
```

Consider:

- selection criteria;
- batching;
- rate limits;
- idempotency;
- replay IDs;
- lineage;
- retries;
- progress tracking;
- partial failure;
- verification.

Do not replay everything at once merely because it is technically possible.

---

# 77. Final Practical Challenge

## Scenario

A daily orders batch contains:

```text
5,000,000 records
4,990,000 valid
9,500 invalid
500 duplicates
```

Design:

1. validation;
2. classification;
3. quarantine;
4. duplicate handling;
5. thresholds;
6. write-audit-publish;
7. alerting;
8. replay;
9. idempotency;
10. reconciliation;
11. security controls.

### First Calculation

```text
5,000,000
=
4,990,000
+
9,500
+
500
```

The accounting reconciles.

The next question is whether the 9,500 invalid records are independent defects or evidence of a systemic problem.

---

## Additional Failure A — Quarantine Storage Unavailable

Decide:

- Can processing safely continue?
- Can invalid evidence be durably preserved elsewhere?
- Should the batch fail?
- How is the event recorded?

A key consideration is whether quarantine is a correctness requirement.

---

## Additional Failure B — Invalid Rate Suddenly Increases

Possible sequence:

```text
detect spike
 ↓
classify
 ↓
evaluate threshold
 ↓
open circuit if policy requires
 ↓
alert owner
 ↓
investigate producer
```

---

## Additional Failure C — Producer Changes Schema

Use:

```text
schema validation
+
compatibility policy
+
quarantine/fail decision
```

Do not treat all schema changes as record-level defects.

A global incompatible schema may require batch failure.

---

## Additional Failure D — Replay Produces Duplicates

Investigate:

```text
idempotency key
target write semantics
replay history
```

Then correct the duplicate effect and strengthen replay controls.

---

# 78. Expected Reasoning for the Final Challenge

A strong solution would reason approximately as follows:

```text
1. Validate records and classify failures.
2. Separate deterministic record defects from systemic failures.
3. Quarantine invalid records with structured metadata.
4. Deduplicate according to the dataset's identity rules.
5. Apply documented thresholds.
6. Keep valid records in staging rather than publishing immediately.
7. Persist audit evidence.
8. Publish only when required invariants hold.
9. Assign ownership for failures.
10. Repair deterministic defects.
11. Replay through the same validation path.
12. Make replay idempotent.
13. Reconcile every run.
14. Monitor quarantine age and error rates.
15. Protect sensitive fields.
16. Stop the pipeline when evidence indicates the valid subset is not independently trustworthy.
```

This is the difference between:

```text
"remove bad rows"
```

and:

```text
"operate a recoverable production data-quality system."
```

---

# 79. Common Mistakes

## 1. Silently Dropping Invalid Records

**Symptom:** input and output counts do not explain each other.

**Root cause:** invalid records were discarded.

**Correct design:** quarantine or explicit rejection accounting.

**Prevention:** reconciliation checks.

---

## 2. Retrying Permanent Errors Forever

**Symptom:** retry storm.

**Root cause:** deterministic invalid input treated as transient.

**Correct design:** bounded retries followed by DLQ/quarantine.

**Prevention:** classify retryability.

---

## 3. No Quarantine Metadata

**Symptom:** bad records exist but nobody knows why.

**Correct design:** structured error code, run ID, source, record ID, rule, timestamp.

---

## 4. No Record ID

**Symptom:** replay cannot target the original record.

**Correct design:** preserve a stable source identifier.

---

## 5. No Run ID

**Symptom:** cannot trace failure to a specific pipeline execution.

**Correct design:** every ingestion run receives a unique run ID.

---

## 6. No Error Code

**Symptom:** failures can only be searched by free text.

**Correct design:** machine-readable taxonomy.

---

## 7. No Ownership

**Symptom:** quarantined records accumulate indefinitely.

**Correct design:** assign responsible producer/domain/team.

---

## 8. No Replay Strategy

**Symptom:** quarantine becomes permanent storage.

**Correct design:** documented repair and replay lifecycle.

---

## 9. Replay Without Idempotency

**Symptom:** duplicate downstream effects.

**Correct design:** idempotency keys and safe writes.

---

## 10. Storing PII Indefinitely

**Symptom:** quarantine becomes a security liability.

**Correct design:** minimization, redaction, encryption, access control, retention.

---

## 11. Alerting on Every Bad Row

**Symptom:** alert fatigue.

**Correct design:** aggregate and threshold alerts.

---

## 12. No Threshold Policy

**Symptom:** engineers make inconsistent decisions during incidents.

**Correct design:** documented dataset-specific policy.

---

## 13. Treating All Failures as Batch Failures

**Symptom:** one malformed record blocks millions of good records.

**Correct design:** record-level isolation when safe.

---

## 14. Treating All Failures as Record Failures

**Symptom:** millions of corrupted records continue downstream.

**Correct design:** circuit breaker or batch failure for systemic defects.

---

## 15. Publishing Before Audit

**Symptom:** consumer sees data before pipeline state is understood.

**Correct design:** write → audit → publish.

---

## 16. No Reconciliation

**Symptom:** records disappear between stages.

**Correct design:** account for input, valid, quarantined, and explicitly rejected records.

---

## 17. No Retention Policy

**Symptom:** quarantine storage grows forever.

**Correct design:** documented operational and security retention.

---

## 18. No Quarantine Monitoring

**Symptom:** failures accumulate unnoticed.

**Correct design:** monitor depth, age, error classes, and replay outcomes.

---

## 19. No Circuit Breaker

**Symptom:** a broken producer continues generating massive amounts of bad data.

**Correct design:** systemic failure detection and controlled stop.

---

## 20. No Failure-Path Tests

**Symptom:** the normal path works, but incidents fail.

**Correct design:** explicitly test quarantine, replay, duplicate, threshold, and storage-failure paths.

---

# 80. Production Checklist

## Validation

- [ ] Validation rule exists.
- [ ] Error code exists.
- [ ] Severity is defined.
- [ ] Record/batch scope is defined.
- [ ] Retryability is defined.

## Quarantine

- [ ] Original record is preserved appropriately.
- [ ] Source is identified.
- [ ] Run ID is stored.
- [ ] Record ID is stored.
- [ ] Error metadata is stored.
- [ ] Owner is identified.
- [ ] Retention is defined.
- [ ] Security controls are defined.

## Recovery

- [ ] Repair process exists.
- [ ] Replay is supported.
- [ ] Replay is idempotent.
- [ ] Replay is observable.
- [ ] Reconciliation exists.
- [ ] Replay authorization is defined where appropriate.

## Pipeline

- [ ] Write-audit-publish is defined.
- [ ] Partial-publish policy exists.
- [ ] Circuit breaker exists where needed.
- [ ] Thresholds are documented.
- [ ] Rollback is defined.
- [ ] Quarantine-storage failure behavior is defined.

## Security

- [ ] PII minimization is implemented.
- [ ] Redaction is implemented where appropriate.
- [ ] Encryption is configured.
- [ ] Access control is configured.
- [ ] Retention is enforced.
- [ ] Access is auditable.

## Operations

- [ ] Alerts exist.
- [ ] Ownership exists.
- [ ] DLQ depth is monitored.
- [ ] Quarantine depth is monitored.
- [ ] Oldest-record age is monitored.
- [ ] Replay success is monitored.
- [ ] Replay failure is monitored.
- [ ] Top error codes are monitored.
- [ ] Invalid-rate trends are monitored.

---

# 81. Final Mental Model

Bad data is inevitable.

**Silent data loss is not.**

A production system should:

```text
Detect
  ↓
Classify
  ↓
Decide
  ↓
Preserve
  ↓
Alert
  ↓
Repair
  ↓
Replay
  ↓
Revalidate
  ↓
Reconcile
  ↓
Prevent recurrence
```

Remember:

```text
Retry transient failures.

Quarantine deterministic bad records.

Fail when the dataset is unsafe.

Never silently drop data without an explicit policy.

Make replay idempotent.

Preserve enough evidence to investigate.

Protect sensitive data.

Measure the quarantine system itself.
```

The deeper engineering model is:

```text
Validation
    tells you what is wrong.

Policy
    tells you what to do.

Quarantine / DLQ
    preserves recoverability.

Audit
    proves what happened.

Replay
    provides controlled recovery.

Idempotency
    makes recovery safe.

Reconciliation
    proves records were accounted for.

Observability
    makes the system operable.

Ownership
    makes remediation actionable.

Security
    prevents the recovery mechanism from becoming a data-exposure mechanism.
```

The goal is not to create a pipeline that never encounters bad data.

The goal is to create a pipeline where bad data is:

```text
detected
→ classified
→ isolated
→ explainable
→ recoverable
→ auditable
→ secure
```

That is production-grade bad-record handling.

---

# 82. Code Quality Requirements

All examples in this lesson should be:

- beginner-readable;
- modern Python;
- PEP 8-oriented;
- explicit about dependencies;
- clear about runnable code versus pseudocode;
- free of fabricated benchmark results;
- free of invented infrastructure guarantees;
- structured around meaningful names.

For important implementations, follow:

```text
Explain
  ↓
Show code
  ↓
Explain expected behavior
  ↓
Inject a failure
  ↓
Capture the failure
  ↓
Explain production implications
```

---

# 83. Security Requirements

Never use:

- real credentials;
- real API keys;
- real payment information;
- real personal data;
- real secrets.

Use synthetic values.

Remember that quarantine can become a sensitive data repository. The need for forensic evidence does not justify unrestricted retention of sensitive payloads.

---

# 84. Scope Boundary

This file is specifically about:

> **Quarantine, Dead-Letter, and Bad-Record Handling**

It does not replace the other Module 2.11 topics.

### Topic 01 — Data Quality Dimensions

Referenced to explain what failed.

### Topic 02 — Pydantic

Referenced to show how record validation errors feed quarantine.

### Topic 03 — Pandera

Referenced to show how DataFrame failure cases can identify bad rows.

### Topic 04 — Great Expectations / Soda

Referenced to show how quality results map to operational actions.

### Topic 05 — Data Contracts

Referenced to explain producer ownership and failure responsibility.

### Topic 06 — Schema Evolution

Referenced to explain schema drift and compatibility failures.

### Topic 08 — Anomaly Detection

Not reproduced here.

### Topic 09 — Reconciliation

Used only to demonstrate accounting for quarantined records.

The purpose of this topic is to connect validation failures to **safe operational handling and recovery**.

---

# 85. Completion Criteria

You should consider this topic learned when you can independently:

- explain bad-record handling from first principles;
- define quarantine;
- define a DLQ;
- distinguish quarantine from a DLQ;
- choose fail/drop/flag/fix/quarantine;
- distinguish record-level and batch-level failure;
- define threshold policies;
- design a quarantine data model;
- preserve original evidence safely;
- classify errors;
- assign severity;
- integrate Pydantic validation with quarantine;
- integrate Pandera failure cases with quarantine;
- map GX/Soda quality results to operational actions;
- design write-audit-publish;
- reason about atomicity and partial failure;
- decide when partial publishing is safe;
- design a circuit breaker;
- distinguish retryable failures from poison messages;
- design a DLQ workflow;
- implement idempotent replay;
- maintain replay lineage;
- operate a quarantine lifecycle;
- assign ownership;
- design actionable alerts;
- prevent alert fatigue;
- secure quarantine storage;
- choose storage options based on workload;
- define retention;
- monitor quarantine health;
- reconcile input and output accounting;
- implement record and batch failure paths in Python;
- design streaming/DLQ behavior without assuming universal broker semantics;
- test failure paths;
- reason about performance;
- design production architecture;
- answer interview and architecture questions;
- solve the final production scenario.

---

# 86. Final Self-Review

- [x] Bad-record handling is explained from first principles.
- [x] Quarantine is clearly defined.
- [x] DLQ is clearly defined.
- [x] Quarantine vs DLQ is explained.
- [x] Fail/drop/flag/fix/quarantine are covered.
- [x] Record-level vs batch-level decisions are covered.
- [x] Thresholds are covered.
- [x] Quarantine data model is covered.
- [x] Original-record preservation is covered.
- [x] Error taxonomy is covered.
- [x] Severity is covered.
- [x] Pydantic integration is covered.
- [x] Pandera integration is covered.
- [x] GX/Soda integration is covered.
- [x] Write-audit-publish is covered.
- [x] Atomicity/partial failure is covered.
- [x] Partial publishing is covered.
- [x] Circuit breakers are covered.
- [x] DLQ behavior is covered.
- [x] Retry vs DLQ is covered.
- [x] Poison messages are covered.
- [x] Retry policies are covered.
- [x] Idempotency is covered.
- [x] Replay is covered.
- [x] Replay metadata is covered.
- [x] Quarantine lifecycle is covered.
- [x] Ownership is covered.
- [x] Alerting is covered.
- [x] Alert fatigue is covered.
- [x] PII/security hygiene is covered.
- [x] Quarantine storage options are compared.
- [x] Retention is covered.
- [x] Observability is covered.
- [x] Reconciliation connection is covered.
- [x] Data-loss prevention is covered.
- [x] Defect injection is included.
- [x] Python implementation is included.
- [x] DataFrame implementation is included.
- [x] Streaming/DLQ concepts are included.
- [x] Hands-on project is included.
- [x] Testing strategy is included.
- [x] Performance is covered.
- [x] Circuit-breaker project is included.
- [x] Production architecture is included.
- [x] Interview questions are included.
- [x] Architecture questions are included.
- [x] Production scenarios are included.
- [x] Final practical challenge is included.
- [x] Common mistakes are included.
- [x] Production checklist is included.
- [x] Final mental model is included.
- [x] No real secrets or sensitive data are used.
- [x] No fabricated benchmark numbers are used.
- [x] Technology-specific behavior is not presented as universal.
- [x] The progression is basic → intermediate → advanced.
- [x] Invalid data is not treated as something that should automatically be dropped.
- [x] Retry vs quarantine is distinguished.
- [x] Replay + idempotency are connected.
- [x] Record-level vs batch-level failure is explained.
- [x] Write-audit-publish is explained.
- [x] Circuit breakers are explained.
- [x] Quarantine security and retention are explained.

---

## Final Takeaway

A reliable data platform does not merely ask:

> "Did validation pass?"

It also asks:

> "What happens when validation fails?"

A mature answer is:

```text
Detect
→ Classify
→ Preserve
→ Decide
→ Isolate
→ Alert
→ Repair
→ Replay
→ Revalidate
→ Reconcile
→ Prevent recurrence
```

That lifecycle turns bad data from an unrecoverable failure into a controlled operational workflow.
