# Data Contracts and Producer Ownership

> **Stage 2 — Python for Data Engineering**  
> **Module 2.11 — Data Validation, Contracts, and Quality**  
> **Topic 05**
>
> A production dataset is not merely a table. It is an interface that other systems depend on. A data contract makes that interface explicit, measurable, owned, versioned, and enforceable.

---

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain what a data contract is from first principles.
- Explain why a schema alone is insufficient for a production data interface.
- Distinguish producer responsibilities from consumer responsibilities.
- Define the components of a production data contract.
- Document schema, semantics, quality, freshness, availability, ownership, version, and change policy.
- Identify breaking, non-breaking, and semantic changes.
- Explain why producer ownership is central to reliable data products.
- Understand consumer contracts and consumer dependencies.
- Explain ODCS conceptually without inventing specification details.
- Use JSON Schema, Avro, and Protobuf conceptually as schema/contract technologies.
- Understand contract enforcement in CI, ingestion, transformation, and publication.
- Build simple contract validation and schema-diff examples in Python.
- Design producer CI/CD workflows.
- Design ownership and escalation models.
- Handle deprecation and migration.
- Reason about backward and forward compatibility.
- Debug contract violations.
- Design a producer-owned orders data product.
- Explain pragmatic adoption and when a formal contract may not be worthwhile.
- Answer contract architecture and interview questions.

---

## Prerequisites

You should already understand:

- Python fundamentals.
- Basic SQL.
- DataFrames.
- Data-quality dimensions.
- Pydantic validation.
- Pandera validation.
- Declarative quality checks with Great Expectations/Soda.

This chapter builds on those topics rather than reproducing them.

The central progression is:

```text
A table has columns
        ↓
A schema describes those columns
        ↓
A contract describes what consumers can rely on
        ↓
A producer owns the published interface
        ↓
The contract is enforced
        ↓
Changes are classified and managed
        ↓
Consumers can safely build on the data product
```

---

# 1. The Problem Data Contracts Solve

Imagine two teams.

### Team A — Orders Service

Owns:

```text
orders
```

### Team B — Data Platform

Consumes:

```text
orders
```

The original schema says:

```text
order_id: integer
customer_id: integer
amount: decimal
```

Later, Team A changes:

```text
customer_id: integer
```

to:

```text
customer_id: string
```

The producer may think:

> "Strings can represent customer IDs too. This is harmless."

The consumer may experience:

```text
ETL failure
join failure
type-casting errors
broken dashboards
failed warehouse loads
```

Both perspectives can be reasonable.

The real problem is that **there was no explicit agreement describing what consumers could rely on**.

A data contract makes that agreement explicit.

---

# 2. Why the Producer May Think the Change Is Harmless

The producer sees the internal implementation.

Perhaps customer IDs originally came from a numeric database column.

Now the service has moved to a system where IDs are strings.

From the producer's perspective:

```text
"12345"
```

and:

```text
12345
```

may represent the same conceptual identifier.

But the consumer does not only depend on the concept.

The consumer may depend on:

```text
integer type
```

for:

- joins,
- database schema,
- serialization,
- analytics code,
- downstream APIs.

Therefore:

```text
Producer's implementation view
        ≠
Consumer's interface view
```

A contract creates the shared interface.

---

# 3. What Is a Data Contract?

## 3.1 Simple definition

A data contract is an explicit agreement describing **what a producer provides and what consumers can rely on**.

It is broader than a schema.

---

## 3.2 Technical definition

A useful model is:

```text
Data Contract
    =
    Schema
    +
    Semantics
    +
    Quality
    +
    Service Expectations
    +
    Ownership
    +
    Versioning
    +
    Change Policy
```

Depending on the organization, it may also include:

- lineage/context,
- documentation,
- enforcement points,
- escalation information,
- consumer expectations,
- examples,
- retention requirements.

---

## 3.3 What a contract can define

A production contract can define:

- dataset identity,
- field names,
- data types,
- nullability,
- constraints,
- field semantics,
- business meaning,
- units,
- timezone semantics,
- allowed values,
- data-quality rules,
- freshness,
- availability,
- delivery frequency,
- latency,
- SLAs/SLOs,
- ownership,
- contact information,
- escalation,
- contract version,
- compatibility policy,
- change policy,
- documentation,
- lineage/context,
- enforcement points.

The key idea is:

> **A schema describes structure. A contract describes the interface that consumers are allowed to rely on.**

---

# 4. Data Contract vs Schema

| Concept | Schema | Data Contract |
|---|---|---|
| Structure | Yes | Yes |
| Field names | Yes | Yes |
| Types | Yes | Yes |
| Nullability | Often | Yes |
| Semantics | Limited unless documented separately | Explicit |
| Business meaning | Usually external | Explicit |
| Quality rules | Usually separate | Can be included |
| Freshness | No | Yes |
| Availability | No | Yes |
| SLA/SLO | No | Yes |
| Ownership | No | Yes |
| Versioning | Sometimes | Explicit |
| Change policy | Usually external | Explicit |
| Enforcement | Schema validator | Multiple enforcement points |

---

## 4.1 Example: schema only

```yaml
orders:
  order_id: integer
  customer_id: integer
  amount: decimal
```

This tells a consumer very little about the actual data product.

What does `amount` mean?

Is it:

- gross amount?
- net amount?
- tax-inclusive?
- tax-exclusive?
- dollars?
- cents?
- local currency?
- USD?

What does `customer_id` mean?

Is it:

- an immutable customer identifier?
- a current CRM identifier?
- a temporary identifier?

When does the dataset arrive?

Who owns it?

What happens if the schema changes?

A schema alone does not answer these questions.

---

# 5. The Producer and Consumer Model

## 5.1 Producer

The producer is the team or system responsible for creating and publishing the dataset.

Examples:

```text
Application team → orders dataset
Payments service → payment events
CRM → customer data
Operational database → analytical tables
Event producer → streaming events
```

---

## 5.2 Consumer

A consumer depends on the published interface.

Examples:

```text
Data Platform
Finance
Analytics
ML pipelines
Reporting systems
Downstream applications
```

A consumer is not necessarily an external company.

It can be another team in the same organization.

---

## 5.3 Why ownership must be explicit

Without ownership:

```text
data breaks
    ↓
Who fixes it?
    ↓
Unknown
```

With ownership:

```text
data breaks
    ↓
identify producer
    ↓
identify rule violated
    ↓
escalate to owner
```

Ownership turns a data problem into an accountable engineering process.

---

# 6. Producer Ownership

Producer ownership is a core principle.

The producer should generally own:

- data correctness at the source boundary,
- contract definition,
- schema compatibility,
- semantic documentation,
- quality expectations,
- freshness commitments,
- change communication,
- versioning,
- incident response for producer defects,
- deprecation policy.

---

## 6.1 What producer ownership does not mean

Producer ownership does **not** mean:

> The producer is responsible for every downstream transformation.

The producer owns the published interface.

The consumer owns how it uses that interface.

For example:

```text
Producer:
    publishes orders correctly

Consumer:
    calculates monthly revenue correctly
```

If the consumer writes:

```python
revenue = orders["amount"] * 100
```

and that calculation is wrong, the producer is not automatically responsible.

---

# 7. Consumer Responsibilities

A contract works only when both sides respect it.

Consumers should:

- understand the contract,
- use documented semantics,
- avoid undocumented assumptions,
- monitor dependencies,
- respond to deprecation notices,
- migrate before deadlines,
- report violations,
- avoid modifying producer-owned data in place,
- test their usage against contract changes.

---

## 7.1 Producer vs consumer responsibilities

| Responsibility | Producer | Consumer |
|---|---|---|
| Published schema | Primary | Understand |
| Semantics | Primary | Use correctly |
| Source quality | Primary | Monitor impact |
| Freshness commitment | Primary | Consume within stated expectations |
| Downstream transformation | Not generally | Primary |
| Contract migration | Support | Primary |
| Contract violation report | Investigate | Report |
| Producer defect incident | Primary | Communicate impact |
| Consumer application bug | Support as needed | Primary |

This is a conceptual model, not a universal organizational RACI standard.

---

# 8. Components of a Production Data Contract

A useful contract can be organized into several areas.

## 8.1 Identity

Include:

- dataset name,
- domain,
- producer,
- known consumers.

Example:

```yaml
name: orders
domain: commerce
producer: orders-platform
```

---

## 8.2 Schema

Define:

- fields,
- types,
- nullability,
- constraints.

Example:

```text
order_id       integer   non-null
customer_id    string    non-null
amount         decimal   non-null
currency       string    non-null
order_time     timestamp non-null
status         enum      non-null
```

---

## 8.3 Semantics

Define:

- field meaning,
- units,
- timezone,
- business definitions,
- allowed values,
- grain.

Example:

```text
amount:
    gross order amount including tax
    denominated in currency
```

---

## 8.4 Quality

Define rules such as:

```text
order_id unique
customer_id non-null
amount >= 0
currency ∈ approved set
```

---

## 8.5 Service expectations

Examples:

```text
freshness
availability
delivery frequency
latency
retention
```

---

## 8.6 Ownership

Define:

```text
producer team
owner
contact
escalation path
```

---

## 8.7 Version

Example:

```text
contract version = 2.1.0
```

The exact versioning convention belongs to the organization.

---

## 8.8 Change policy

Define:

- additive changes,
- breaking changes,
- deprecation,
- migration windows,
- consumer communication.

---

## 8.9 Documentation

Include:

- field definitions,
- examples,
- known limitations,
- grain,
- business definitions.

---

# 9. Schema and Semantics

Semantics are often more important than syntax.

Consider:

```text
amount: decimal
```

The type is clear.

The meaning is not.

Possible meanings:

```text
gross amount
net amount
tax-inclusive amount
tax-exclusive amount
USD
local currency
cents
dollars
```

A technically valid schema can therefore support completely incorrect analytics.

---

## 9.1 Semantic metadata

Important semantic fields include:

```text
unit
currency
timezone
business definition
calculation method
grain
```

Example:

```yaml
amount:
  type: decimal
  description: "Gross order amount including tax."
  unit: "currency units"
  currency_field: "currency"
```

The exact contract representation is illustrative.

---

# 10. Quality Rules Inside Contracts

Quality expectations can become contract requirements.

Examples:

```text
order_id must be unique
customer_id must not be null
currency must belong to an approved set
event_timestamp must be timezone-aware
data must arrive within 15 minutes
```

Distinguish three concepts.

## 10.1 Schema constraint

Example:

```text
customer_id is string
```

## 10.2 Data-quality rule

Example:

```text
customer_id must not be null
```

## 10.3 Business semantic rule

Example:

```text
amount represents gross order value including tax
```

All three can be part of a useful contract.

---

# 11. SLA, SLO, and Freshness

## 11.1 SLA

A Service Level Agreement is a formal service commitment between parties.

In data systems, it can describe commitments such as:

```text
availability
delivery timing
freshness
```

The exact legal/organizational meaning varies.

---

## 11.2 SLO

A Service Level Objective is a measurable target.

Example:

```text
99% of daily orders deliveries
must be available by 06:00 UTC.
```

---

## 11.3 Freshness

Freshness describes how current the available data must be.

Weak:

```text
Orders arrive daily.
```

Stronger:

```text
Daily orders must be available by 06:00 UTC.
```

The second statement is operationally measurable.

---

## 11.4 Why service expectations belong in a contract

Suppose the dataset is structurally correct but arrives 12 hours late.

Schema validation passes.

The consumer still fails operationally.

Therefore:

```text
Correct schema
    ≠
Usable data product
```

---

# 12. Contract Versioning

Contracts need versions because interfaces change.

For example:

```text
orders-contract-v1
orders-contract-v2
```

Versioning allows consumers to understand:

```text
what changed
when it changed
whether migration is required
```

---

## 12.1 Semantic-versioning-style thinking

Some organizations use a model resembling:

```text
MAJOR.MINOR.PATCH
```

Illustratively:

### PATCH

Documentation correction.

### MINOR

Additive optional field.

### MAJOR

Removing or changing a required field.

This is a useful mental model, not a universal requirement.

The semantic impact of the change matters more than blindly assigning a number.

---

# 13. Breaking vs Non-Breaking Changes

| Change | Typical impact |
|---|---|
| Add optional field | Often non-breaking |
| Add required field | Potentially breaking |
| Remove field | Breaking |
| Rename field | Breaking |
| Widen numeric type | Context-dependent |
| Narrow numeric type | Breaking risk |
| Nullable → non-nullable | Breaking |
| Change field meaning | Potentially severe semantic break |
| Change units | Semantic breaking change |
| Add enum value | Consumer-dependent |

The word **typically** matters.

Compatibility depends on:

- serialization technology,
- consumers,
- query behavior,
- database behavior,
- contract rules,
- migration strategy.

---

# 14. Why Semantic Compatibility Matters

Consider:

### Version 1

```text
amount = gross amount including tax
```

### Version 2

```text
amount = net amount excluding tax
```

Schema:

```text
amount: decimal
```

unchanged.

Yet the contract has changed materially.

This is a **semantic breaking change**.

Other semantic changes include:

- timezone interpretation,
- currency interpretation,
- unit changes,
- status meaning,
- event grain,
- calculation methodology.

Schema compatibility is therefore necessary but not sufficient.

---

# 15. Contract Change Policy

A production change should follow a deliberate workflow:

```text
Proposed change
      ↓
Classify change
      ↓
Compatibility analysis
      ↓
Identify consumers
      ↓
Notify consumers
      ↓
Migration window
      ↓
Deploy producer change
      ↓
Validate consumers
      ↓
Deprecate old version
      ↓
Remove old version
```

This is much safer than:

```text
ALTER TABLE
    ↓
hope nothing breaks
```

---

# 16. Producer-Owned Change Management

Consider:

```text
customer_id:
    integer
        ↓
    string
```

A producer should:

1. identify the reason,
2. identify affected consumers,
3. classify compatibility,
4. create a migration strategy,
5. update the contract,
6. communicate the change,
7. provide a migration window where required,
8. deploy safely,
9. monitor,
10. deprecate the old interface when appropriate.

The producer is accountable for the change process because it owns the interface.

---

# 17. Consumer Contracts

A producer can publish 20 fields while a consumer relies on only 5.

For example:

```text
Producer:
    order_id
    customer_id
    amount
    currency
    status
    created_at
    ...
```

Consumer:

```text
order_id
customer_id
amount
currency
status
```

A consumer contract can describe what the consumer actually depends upon.

This can help answer:

```text
If the producer changes field X,
which consumers are affected?
```

Consumer dependency information is therefore valuable for change management.

---

# 18. ODCS — Open Data Contract Standard

The roadmap explicitly introduces ODCS.

The important concept is standardized representation of data contracts.

A standardized contract approach can provide common structures for concepts such as:

- metadata,
- schema,
- semantics,
- quality,
- service expectations,
- ownership,
- versioning.

The purpose is interoperability and consistent contract representation.

---

## 18.1 Specification accuracy

Do not invent an exact ODCS schema from memory.

If implementing an actual ODCS contract:

```text
identify specification/version
        ↓
read authoritative specification
        ↓
validate fields
        ↓
test contract
```

The examples in this chapter that use generic YAML structures are **illustrative contracts**, not claims that those fields constitute official ODCS requirements.

---

# 19. JSON Schema

## 19.1 What is JSON Schema?

JSON Schema describes the structure and constraints of JSON data.

It can express concepts such as:

- object properties,
- required properties,
- types,
- enums,
- numeric constraints,
- string constraints,
- nested structures,
- additional-property rules.

---

## 19.2 Illustrative order schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Order",
  "type": "object",
  "required": [
    "order_id",
    "customer_id",
    "amount",
    "currency"
  ],
  "properties": {
    "order_id": {
      "type": "integer"
    },
    "customer_id": {
      "type": "string"
    },
    "amount": {
      "type": "number",
      "minimum": 0
    },
    "currency": {
      "type": "string",
      "enum": ["USD", "EUR", "GBP", "INR"]
    }
  },
  "additionalProperties": false
}
```

This is a JSON Schema example.

It is not a complete organizational data contract.

---

## 19.3 What JSON Schema handles well

It is strong for:

```text
structure
types
required fields
basic constraints
enums
nested objects
```

---

## 19.4 What JSON Schema does not automatically solve

It does not by itself establish:

- data freshness,
- organizational ownership,
- operational SLA,
- consumer escalation,
- every business semantic,
- cross-system referential integrity,
- historical quality.

A contract is therefore broader than a JSON Schema.

---

# 20. Avro

Apache Avro is a schema-based serialization system commonly used in data and event systems.

Conceptually:

```text
Schema
    +
Record
    ↓
Serialization
    ↓
Data
```

An illustrative schema:

```json
{
  "type": "record",
  "name": "Order",
  "namespace": "com.example.orders",
  "fields": [
    {
      "name": "order_id",
      "type": "long"
    },
    {
      "name": "customer_id",
      "type": "string"
    },
    {
      "name": "amount",
      "type": "double"
    }
  ]
}
```

Schema evolution matters because producers and consumers may run at different times.

Compatibility depends on:

- how schemas are changed,
- reader/writer behavior,
- serialization configuration,
- ecosystem rules.

Do not assume that every schema change is automatically safe.

---

# 21. Protobuf

Protocol Buffers define structured messages.

An illustrative message:

```proto
message Order {
  int64 order_id = 1;
  string customer_id = 2;
  double amount = 3;
}
```

Important concepts include:

- message definitions,
- fields,
- field numbers,
- serialization,
- schema evolution,
- compatibility.

---

## 21.1 Why field numbers matter

In Protobuf:

```proto
string customer_id = 2;
```

contains a field number:

```text
2
```

That number is part of the serialized representation.

Therefore, schema evolution must respect the serialization model.

Do not casually reuse or change field numbers.

The exact compatibility rules depend on the ecosystem and evolution practices being used.

---

# 22. JSON Schema vs Avro vs Protobuf

| Dimension | JSON Schema | Avro | Protobuf |
|---|---|---|---|
| Representation | JSON schema | Avro schema | `.proto` schema |
| Common use | JSON validation/contracts | Data/event serialization | APIs/events/serialization |
| Human readability | High | Moderate | High |
| Serialization | Usually validates JSON | Yes | Yes |
| Schema evolution | Supported conceptually | Important design concern | Important design concern |
| Typical interface | JSON payloads | Data/event systems | Structured messages/RPC ecosystems |
| Strength | Flexible JSON structure | Schema + serialization for data systems | Compact typed messages |
| Limitation | Not a full operational contract | Requires schema/serialization discipline | Requires careful field evolution |
| Ownership | External concept | External concept | External concept |
| SLA/freshness | External | External | External |

Do not rank these technologies.

Selection depends on:

```text
transport
data format
ecosystem
compatibility requirements
serialization requirements
consumer technology
operational model
```

---

# 23. Contract Enforcement

A contract is useful only if it is enforceable.

Possible enforcement points include:

```text
Producer CI
    ↓
Contract validation
    ↓
Build/deploy gate
    ↓
Data production
    ↓
Ingestion validation
    ↓
Transformation validation
    ↓
Published-data validation
```

Different layers catch different failure modes.

---

# 24. Producer CI Enforcement

Suppose a producer changes:

```text
customer_id: integer
```

to:

```text
customer_id: string
```

A CI system can perform:

```text
Schema change
    ↓
Contract diff
    ↓
Compatibility classification
    ↓
CI pass/fail
    ↓
Deployment allowed/blocked
```

A conceptual Python diff:

```python
old_schema = {
    "customer_id": "integer",
    "amount": "decimal",
}

new_schema = {
    "customer_id": "string",
    "amount": "decimal",
}

changes = {
    field: (old_schema.get(field), new_schema.get(field))
    for field in set(old_schema) | set(new_schema)
    if old_schema.get(field) != new_schema.get(field)
}

print(changes)
```

Conceptual result:

```text
customer_id:
    integer → string
```

This is not a complete compatibility engine.

It demonstrates the idea:

```text
detect change
    ↓
classify change
    ↓
make deployment decision
```

---

# 25. Ingestion-Time Enforcement

A platform may validate incoming data:

```text
Incoming event
      ↓
Schema validation
      ↓
Contract validation
      ↓
Accepted
   OR
Rejected / quarantined
```

Why is this useful if producer CI already exists?

Because CI validates intended changes.

Runtime validation detects:

- bad deployment,
- malformed data,
- unexpected producer behavior,
- configuration errors,
- operational failures.

Therefore:

```text
CI enforcement
    ≠
runtime enforcement
```

Both can be useful.

---

# 26. Transformation-Time Enforcement

Data can become invalid after ingestion.

Examples:

- field renamed accidentally,
- join creates duplicates,
- aggregation changes grain,
- nullability changes,
- business invariant breaks.

Validation can therefore occur after transformations.

Relevant tools include:

```text
Pandera
Great Expectations
Soda
SQL
```

The appropriate tool depends on the transformation boundary.

---

# 27. Published-Data Enforcement

Final published data should also be validated.

Example:

```text
Raw source
    ↓
Transformations
    ↓
Gold table
    ↓
Contract validation
    ↓
Consumer access
```

Why?

Because source correctness does not guarantee transformed-data correctness.

A correct source can become incorrect through:

```text
bad join
wrong filter
aggregation error
type conversion
incorrect business logic
```

The published product is the interface consumers actually use.

---

# 28. Data Contract as a Data Product Interface

A dataset should not be treated as a random table.

A useful model is:

```text
Data Product
    =
    Data
    +
    Contract
    +
    Ownership
    +
    Quality
    +
    Documentation
    +
    Service Expectations
```

This changes organizational behavior.

Instead of:

```text
"Here is a table."
```

the producer provides:

```text
"Here is a data product with defined behavior."
```

---

# 29. Data Mesh Connection

Data contracts become particularly relevant in domain-oriented architectures.

Important concepts include:

- domain ownership,
- data as a product,
- federated governance,
- interoperability,
- explicit interfaces.

The key connection is:

```text
Domain team
    ↓
Owns data product
    ↓
Publishes contract
    ↓
Consumers use documented interface
```

This chapter does not attempt to teach the entire Data Mesh approach.

The important point is that decentralized ownership increases the value of explicit interfaces.

---

# 30. Contract Negotiation

A contract is an agreement, not merely a schema file.

Suppose a producer wants:

```text
rename customer_id
```

but a consumer depends on:

```text
customer_id
```

A useful process is:

```text
Identify impact
      ↓
Discuss alternatives
      ↓
Choose compatibility strategy
      ↓
Define migration window
      ↓
Notify consumers
      ↓
Deprecate old interface
```

The contract process is therefore partly technical and partly organizational.

---

# 31. Deprecation

A safe lifecycle can be:

```text
v1
 ↓
v2 introduced
 ↓
Consumers migrate
 ↓
v1 deprecated
 ↓
Monitoring period
 ↓
v1 removed
```

A good deprecation process defines:

- notice,
- migration deadline,
- communication,
- usage monitoring,
- removal criteria.

---

## 31.1 Why immediate removal is dangerous

If a producer immediately removes:

```text
customer_id
```

then downstream systems can fail without warning.

Deprecation creates a controlled transition.

---

# 32. Backward and Forward Compatibility Awareness

## 32.1 Backward compatibility

A newer producer/data representation can still work with older consumers.

Conceptually:

```text
new data
    ↓
old consumer
```

continues to function.

---

## 32.2 Forward compatibility

Older producer/data can still work with newer consumers.

Conceptually:

```text
old data
    ↓
new consumer
```

continues to function.

---

## 32.3 Full compatibility

Some ecosystems discuss compatibility in both directions.

The exact meaning depends on the technology.

For this topic, the important lesson is:

> **Compatibility is a property of an interface and its consumers, not merely a property of a field's data type.**

---

# 33. Complete Illustrative Orders Data Contract

The following is an **illustrative contract**, not an official ODCS schema.

```yaml
contract:
  name: orders
  domain: commerce
  producer: orders-platform
  version: 1.0.0

  consumers:
    - data-platform
    - analytics
    - finance

  grain:
    description: "One record represents one completed order."

  schema:
    order_id:
      type: integer
      nullable: false
      description: "Stable unique order identifier."

    customer_id:
      type: string
      nullable: false
      description: "Stable customer identifier."

    amount:
      type: decimal
      nullable: false
      description: "Gross order amount including tax."

    currency:
      type: string
      nullable: false
      allowed_values:
        - USD
        - EUR
        - GBP
        - INR

    order_timestamp:
      type: timestamp
      nullable: false
      timezone: UTC

    status:
      type: string
      nullable: false
      allowed_values:
        - pending
        - paid
        - cancelled
        - refunded

  quality:
    - rule_id: orders.order_id.unique
      requirement: "order_id must be unique"
      severity: critical

    - rule_id: orders.customer_id.complete
      requirement: "customer_id must not be null"
      severity: error

    - rule_id: orders.amount.non_negative
      requirement: "amount must be >= 0"
      severity: error

  service:
    freshness:
      target: "daily by 06:00 UTC"

    availability:
      target: "99% of scheduled deliveries"

  change_policy:
    breaking_change:
      requires:
        - compatibility_review
        - consumer_notification
        - migration_window

    deprecation:
      requires:
        - notice
        - migration_deadline
        - usage_monitoring

  ownership:
    team: orders-platform
    escalation: orders-oncall
```

The important learning point is not YAML syntax.

It is the information represented by the contract.

---

# 34. Contract Validation in Python

A simple contract representation can be loaded and inspected.

```python
import json

contract = {
    "name": "orders",
    "version": "1.0.0",
    "fields": {
        "order_id": {
            "type": "integer",
            "nullable": False,
        },
        "customer_id": {
            "type": "string",
            "nullable": False,
        },
        "amount": {
            "type": "number",
            "nullable": False,
        },
    },
}
```

A minimal structural validator:

```python
required_contract_keys = {
    "name",
    "version",
    "fields",
}

missing_keys = required_contract_keys - contract.keys()

if missing_keys:
    raise ValueError(
        f"Contract is missing keys: {sorted(missing_keys)}"
    )
```

This is intentionally simple.

The purpose is to demonstrate:

```text
contract definition
    ↓
contract validation
```

---

# 35. Validating Sample Records Against a Simple Contract

A minimal illustrative validator:

```python
def validate_record(record, contract):
    errors = []

    for field_name, rule in contract["fields"].items():
        if field_name not in record:
            errors.append(f"Missing field: {field_name}")
            continue

        value = record[field_name]

        if value is None and not rule["nullable"]:
            errors.append(f"Field is null: {field_name}")

    return errors
```

Usage:

```python
record = {
    "order_id": 1001,
    "customer_id": None,
    "amount": 25.0,
}

errors = validate_record(record, contract)

for error in errors:
    print(error)
```

Expected conceptual result:

```text
Field is null: customer_id
```

A production validator would also validate types, enums, ranges, semantics, and other contract rules.

---

# 36. Contract Diff

Consider version 1:

```python
v1 = {
    "customer_id": {
        "type": "integer",
        "nullable": False,
    },
    "amount": {
        "type": "decimal",
        "nullable": False,
    },
}
```

Version 2:

```python
v2 = {
    "customer_id": {
        "type": "string",
        "nullable": False,
    },
    "amount": {
        "type": "decimal",
        "nullable": False,
    },
}
```

A simple diff:

```python
def diff_fields(old, new):
    changes = {}

    all_fields = set(old) | set(new)

    for field in sorted(all_fields):
        if field not in old:
            changes[field] = {
                "change": "added",
                "new": new[field],
            }
        elif field not in new:
            changes[field] = {
                "change": "removed",
                "old": old[field],
            }
        elif old[field] != new[field]:
            changes[field] = {
                "change": "modified",
                "old": old[field],
                "new": new[field],
            }

    return changes
```

This detects structural differences.

It does **not** automatically know whether a semantic change is safe.

---

# 37. Schema Diff vs Compatibility Engine

A schema diff can say:

```text
customer_id:
    integer → string
```

A compatibility engine must answer:

```text
Is this safe?
For which consumers?
Under which serialization system?
Under which migration strategy?
```

Therefore:

```text
Schema diff
    ≠
Compatibility analysis
```

A diff is evidence used by compatibility analysis.

---

# 38. Semantic Changes

Consider:

### v1

```text
amount = gross amount including tax
```

### v2

```text
amount = net amount excluding tax
```

The schema diff might be:

```text
NO STRUCTURAL CHANGE
```

Yet the contract has changed.

This is why semantic metadata and human review are necessary.

---

# 39. Data Grain

Grain belongs in a contract because consumers depend on what one row represents.

Examples:

```text
one row = one order
```

versus:

```text
one row = one order line
```

versus:

```text
one row = one customer-day
```

A change from:

```text
one order
```

to:

```text
one order line
```

can break:

```text
COUNT(*)
SUM(amount)
joins
deduplication
analytics models
```

even if every column name and type remains unchanged.

Grain is therefore a semantic contract.

---

# 40. Business Definitions

Business terms must be explicit.

For example:

```text
revenue
```

could mean:

- gross revenue,
- net revenue,
- recognized revenue,
- booked revenue.

Similarly:

```text
active customer
```

could mean:

- logged in within 30 days,
- purchased within 90 days,
- has an active subscription.

A contract should define the meaning consumers are allowed to rely on.

---

# 41. Quality + Contract + Ownership

The production relationship is:

```text
Contract
    ↓
Quality rules
    ↓
Producer ownership
    ↓
Enforcement
    ↓
Consumer trust
```

A useful way to reason about the pieces is:

```text
Contract without ownership
    → documentation with no accountable owner

Contract without enforcement
    → suggestion rather than executable policy

Contract without quality
    → mostly structural description

Contract without change management
    → future compatibility incident
```

These are engineering consequences, not merely terminology.

---

# 42. Failure Scenarios

## Scenario 1 — Producer renames `customer_id`

### What changed

```text
customer_id → client_id
```

### Why it matters

Consumers may reference the original field.

### Contract impact

Breaking unless a compatibility mechanism exists.

### Producer responsibility

Notify, version, migrate, deprecate.

### Consumer responsibility

Migrate before removal.

### Prevention

Contract diff in CI.

---

## Scenario 2 — Producer adds a required field

Example:

```text
country_code
```

becomes mandatory.

### Impact

Consumers constructing records may fail.

### Classification

Potentially breaking.

### Action

Analyze consumers before deployment.

---

## Scenario 3 — Producer changes timezone semantics

Before:

```text
timestamp interpreted as UTC
```

After:

```text
timestamp interpreted as local time
```

Schema may remain:

```text
timestamp
```

but semantics changed.

This requires review.

---

## Scenario 4 — Currency changes

Before:

```text
amount is USD
```

After:

```text
amount is local currency
```

The type is unchanged.

The meaning is not.

This is a semantic breaking change unless consumers have explicitly been designed for the change.

---

## Scenario 5 — Event grain changes

Before:

```text
one row = one order
```

After:

```text
one row = one order line
```

Potential consequences:

```text
duplicate orders
inflated sums
broken joins
incorrect counts
```

---

## Scenario 6 — Freshness SLO is missed

The data is structurally valid but late.

This is a service-level contract violation.

---

## Scenario 7 — Enum values change

Before:

```text
paid
cancelled
```

After:

```text
paid
cancelled
refunded
```

Adding a value may be safe for some consumers and breaking for consumers that reject unknown values.

Therefore enum evolution is consumer-dependent.

---

## Scenario 8 — Consumer depends on undocumented behavior

Example:

```text
Consumer assumes rows are sorted by timestamp.
```

The contract never promised ordering.

The consumer has an undocumented dependency.

This is primarily a consumer design problem.

---

# 43. Debugging and Incident Exercises

## Incident A — Type mismatch at 09:00

Error:

```text
customer_id expected INTEGER
received STRING
```

Debugging sequence:

1. Identify producer.
2. Identify contract version.
3. Inspect schema diff.
4. Inspect producer deployment.
5. Identify affected consumers.
6. Classify compatibility.
7. Decide rollback vs migration.
8. Communicate.
9. Update the contract.
10. Add prevention.

---

## Incident B — Missing field

Error:

```text
amount column not found
```

Investigate:

```text
Was the field removed?
Was the dataset version changed?
Was a transformation renamed?
Did the producer violate the contract?
```

---

## Incident C — Semantically incorrect amount

No schema error occurs.

But finance reports:

```text
revenue doubled
```

Investigation finds:

```text
amount changed from net to gross
```

This demonstrates why schema-only validation is insufficient.

---

## Incident D — Freshness failure

The data arrived at:

```text
08:30 UTC
```

while the contract requires:

```text
06:00 UTC
```

Investigate:

```text
producer processing delay
source outage
scheduler failure
upstream dependency
```

The contract identifies the violation; observability and incident analysis identify the cause.

---

# 44. Hands-On Project — Producer-Owned Orders Data Contract

## Scenario

Four teams exist:

```text
Team A:
    Orders Service

Team B:
    Data Platform

Team C:
    Analytics

Team D:
    Finance
```

Team A owns the orders data product.

Teams B–D consume it.

---

## 44.1 Build `orders-contract-v1`

Include:

- schema,
- semantics,
- quality rules,
- freshness,
- ownership,
- version,
- compatibility policy,
- change policy,
- escalation.

---

## 44.2 Example v1

```yaml
name: orders
version: 1.0.0

producer:
  team: orders-service

grain:
  description: "One row represents one order."

fields:
  order_id:
    type: integer
    nullable: false
    unique: true

  customer_id:
    type: string
    nullable: false

  amount:
    type: decimal
    nullable: false
    semantic_type: gross_order_amount

  currency:
    type: string
    allowed_values: [USD, EUR, GBP, INR]

  order_timestamp:
    type: timestamp
    timezone: UTC

quality:
  freshness: "daily by 06:00 UTC"

change_policy:
  breaking_change:
    requires_consumer_notification: true
    requires_migration_window: true
```

This is illustrative.

---

# 45. Build `orders-contract-v2`

Introduce three changes.

### Change A — Add optional field

```text
sales_channel
```

Classify:

```text
Often non-breaking.
```

Why?

Existing consumers can ignore the field if the interface allows unknown/additional fields.

---

### Change B — Change `customer_id`

```text
string → integer
```

Classify:

```text
Potentially breaking / breaking depending on consumers.
```

---

### Change C — Change `amount` meaning

```text
gross including tax
        ↓
net excluding tax
```

Classify:

```text
Semantic breaking change.
```

The schema may not change at all.

---

# 46. Contract Test Example

A simple test can verify required fields:

```python
def assert_required_fields(record, contract):
    required = {
        name
        for name, rule in contract["fields"].items()
        if not rule.get("nullable", True)
    }

    missing = required - record.keys()

    assert not missing, (
        f"Missing required fields: {sorted(missing)}"
    )
```

A more mature contract test suite should include:

```text
schema
types
required fields
allowed values
semantic invariants
compatibility
freshness
producer CI
```

---

# 47. Testing Data Contracts

Several testing layers are useful.

## Unit tests

Test individual pieces of contract-validation code.

Example:

```text
schema parser
diff function
compatibility classifier
```

---

## Contract tests

Test whether a producer satisfies the published interface.

```text
producer output
    ↓
contract
    ↓
PASS / FAIL
```

---

## Data-quality checks

Test actual data quality:

```text
null rates
duplicates
validity
freshness
```

---

## Integration tests

Test the producer-consumer interaction.

```text
producer
    ↓
published interface
    ↓
consumer
```

These test different failure modes.

---

# 48. Producer CI/CD

A conceptual CI workflow:

```text
Developer changes schema
        ↓
Contract updated
        ↓
Contract tests
        ↓
Schema diff
        ↓
Compatibility check
        ↓
Consumer impact check
        ↓
Review
        ↓
Deploy
```

---

## 48.1 What should block deployment?

Potentially blocking conditions include:

```text
required field removed
incompatible type change
semantic breaking change without migration
contract tests fail
critical quality rule fails
```

Not every documentation change should block deployment.

Policy should distinguish:

```text
informational
warning
breaking
critical
```

---

# 49. Ownership Model

A realistic conceptual ownership matrix:

| Responsibility | Producer | Consumer | Platform |
|---|---|---|---|
| Schema | Primary | Consulted | Supported |
| Semantics | Primary | Consulted | Supported |
| Quality | Primary | Monitor | Tooling/enforcement |
| Usage | Informed | Primary | Supported |
| Migration | Support | Primary | Support |
| Producer incident | Primary | Impact communication | Facilitate |

Exact responsibilities depend on organizational structure.

The important principle is:

```text
Someone must own every important responsibility.
```

---

# 50. Pragmatic Adoption

Do not create heavyweight contracts for every dataset immediately.

A practical adoption strategy is:

1. identify critical datasets,
2. identify high-impact producers,
3. identify high-risk fields,
4. assign ownership,
5. define a small number of meaningful rules,
6. automate enforcement,
7. expand gradually.

---

## 50.1 Why not contract everything immediately?

Excessive governance can create:

- administrative burden,
- maintenance overhead,
- resistance,
- low-value documentation.

A better principle is:

> **Contract where reliability matters most.**

---

# 51. When a Formal Data Contract May Not Be Necessary

A formal contract may be unnecessary for:

- temporary exploratory datasets,
- internal scratch tables,
- one-off analysis,
- rapidly changing prototypes.

But the need can change when:

```text
consumers multiply
business impact increases
data becomes shared
reliability becomes important
```

Therefore:

```text
Contract maturity
    should follow
    interface criticality
```

This is a decision framework, not an absolute rule.

---

# 52. Maintainability

Contracts themselves can become technical debt.

Problems include:

- stale documentation,
- unused contracts,
- outdated owners,
- duplicated schemas,
- conflicting definitions,
- untracked versions,
- missing consumer inventory.

Solutions include:

- ownership metadata,
- automated validation,
- CI enforcement,
- lifecycle management,
- deprecation,
- usage monitoring,
- contract tests,
- regular review.

---

## 52.1 Contract lifecycle

A useful lifecycle is:

```text
Draft
  ↓
Reviewed
  ↓
Published
  ↓
Validated
  ↓
Versioned
  ↓
Deprecated
  ↓
Retired
```

---

# 53. Common Failure Modes

## 53.1 Contract is only documentation

### Symptom

A contract exists but no system checks it.

### Root cause

Documentation was treated as enforcement.

### Remediation

Add CI/runtime validation.

### Prevention

Make the contract executable at relevant boundaries.

---

## 53.2 No producer ownership

### Symptom

Nobody knows who should fix a defect.

### Root cause

Dataset ownership was never assigned.

### Remediation

Assign a producer owner and escalation path.

---

## 53.3 Consumers discover changes after deployment

### Symptom

Downstream systems fail unexpectedly.

### Root cause

No change-management process.

### Remediation

Introduce compatibility checks and consumer notification.

---

## 53.4 Schema exists but semantics are undefined

### Symptom

Two teams calculate different revenue values.

### Root cause

Field meaning was not documented.

### Remediation

Define business semantics.

---

## 53.5 Freshness expectations are vague

### Symptom

Producer says:

```text
data is daily
```

Consumer expects:

```text
06:00 UTC
```

### Remediation

Define a measurable SLO.

---

## 53.6 Quality rules are missing

### Symptom

Schema passes but data contains duplicates and invalid values.

### Remediation

Include measurable quality rules.

---

## 53.7 Breaking changes are not classified

### Symptom

A producer treats a required-field removal as a normal release.

### Remediation

Add compatibility classification.

---

## 53.8 No versioning

### Symptom

Consumers cannot tell which interface they target.

### Remediation

Introduce explicit contract versions.

---

## 53.9 No deprecation process

### Symptom

Old consumers break immediately.

### Remediation

Use migration windows and usage monitoring.

---

## 53.10 Contract is too strict

### Symptom

Legitimate producer improvements require unnecessary coordination.

### Remediation

Allow justified additive evolution.

---

## 53.11 Contract is too loose

### Symptom

Consumers make undocumented assumptions.

### Remediation

Document important semantics and service expectations.

---

## 53.12 Every dataset requires heavyweight governance

### Symptom

Teams avoid using contracts.

### Root cause

Governance cost exceeds value.

### Remediation

Prioritize critical data products.

---

## 53.13 Producer and consumer responsibilities are unclear

### Symptom

Every incident becomes a blame discussion.

### Remediation

Define responsibilities explicitly.

---

## 53.14 Semantic changes are ignored

### Symptom

No schema diff is detected, but analytics becomes wrong.

### Remediation

Review semantic changes explicitly.

---

## 53.15 Data grain is undocumented

### Symptom

Counts and joins become incorrect.

### Remediation

Document one-row meaning.

---

## 53.16 Units and timezones are undocumented

### Symptom

Numbers or timestamps are interpreted incorrectly.

### Remediation

Document units and timezone semantics.

---

## 53.17 Contracts are never tested

### Symptom

Contract looks correct but producer violates it.

### Remediation

Automate contract tests.

---

## 53.18 Contracts become stale

### Symptom

The documented contract differs from production.

### Remediation

Make contract updates part of change workflow and CI.

---

# 54. Interview Questions and Answers

## Basic

### 1. What is a data contract?

A data contract is an explicit agreement describing what a producer publishes and what consumers can rely on, including structure, meaning, quality, service expectations, ownership, and change policy.

---

### 2. Why is a schema not enough?

A schema primarily describes structure.

A production contract also describes:

```text
meaning
quality
freshness
availability
ownership
version
change policy
```

---

### 3. What is producer ownership?

Producer ownership means the producer is accountable for the correctness and compatibility of its published data interface and for managing changes to that interface.

---

### 4. What is a consumer?

A consumer is a system or team that relies on the producer's published data interface.

---

### 5. Why do data contracts matter?

They reduce ambiguity between producers and consumers and make assumptions explicit and enforceable.

---

## Intermediate

### 6. What belongs in a data contract?

At minimum:

```text
identity
schema
semantics
quality
service expectations
ownership
version
change policy
documentation
```

---

### 7. What is a breaking change?

A change that can invalidate assumptions made by existing consumers.

Examples:

```text
remove field
rename field
change required type
change nullability
change semantic meaning
change grain
```

---

### 8. What is a non-breaking change?

A change that can be introduced without invalidating existing consumer assumptions under the relevant contract rules.

An optional additive field is a common example, but actual compatibility depends on consumers and the interface technology.

---

### 9. Why is semantic compatibility important?

Because consumers rely on meaning, not just types.

Changing:

```text
gross revenue
```

to:

```text
net revenue
```

can break analytics while leaving the schema unchanged.

---

### 10. What is contract versioning?

Versioning identifies distinct contract states so producers and consumers can coordinate changes and migrations.

---

### 11. What is deprecation?

Deprecation is the controlled process of announcing that an interface/version will eventually be retired while giving consumers time to migrate.

---

## Advanced

### 12. How do you enforce contracts?

Use multiple layers:

```text
producer CI
runtime validation
ingestion validation
transformation validation
published-data validation
consumer contract tests
```

---

### 13. How do you design producer ownership?

Define:

```text
dataset
producer team
technical owner
business owner where appropriate
escalation
quality responsibility
change responsibility
incident responsibility
```

---

### 14. How do you manage multiple consumers?

Maintain:

```text
consumer inventory
contract versions
dependency information
migration deadlines
usage monitoring
```

---

### 15. What if a producer needs a breaking change?

Use:

```text
impact analysis
compatibility classification
consumer communication
versioning
migration window
dual support where practical
deprecation
removal
```

---

### 16. How do you detect contract violations?

Use:

- CI contract tests,
- schema validation,
- runtime validation,
- quality checks,
- freshness checks,
- published-data checks.

---

### 17. How do you prevent contract drift?

Combine:

```text
contract-as-code
+
CI
+
runtime validation
+
ownership
+
versioning
+
regular review
```

---

# 55. Architecture Questions

## 55.1 Design a producer-owned data product

A good answer should include:

```text
producer
contract
schema
semantics
quality
freshness
ownership
versioning
enforcement
monitoring
consumer discovery
change management
```

---

## 55.2 Design a contract for an orders dataset

Include:

```text
order_id
customer_id
amount
currency
order_timestamp
status
```

Then define:

```text
grain
types
nullability
meaning
quality
freshness
ownership
change policy
```

---

## 55.3 Design contract CI/CD

```text
Pull request
    ↓
Contract syntax validation
    ↓
Schema diff
    ↓
Compatibility classification
    ↓
Contract tests
    ↓
Consumer impact analysis
    ↓
Review
    ↓
Deploy
```

---

## 55.4 Design compatibility checks

The system should detect:

```text
field removal
required field addition
type change
nullability change
enum change
```

Then classify the change.

Semantic changes may require human review because they cannot always be inferred mechanically.

---

## 55.5 Design consumer migration

For a breaking change:

```text
v1 remains available
    ↓
v2 introduced
    ↓
consumers migrate
    ↓
usage monitored
    ↓
v1 deprecated
    ↓
v1 removed
```

---

## 55.6 Design contract governance at organizational scale

At scale, consider:

```text
contract registry
producer ownership
consumer inventory
contract validation
CI integration
compatibility checks
versioning
deprecation
monitoring
incident management
```

Avoid assuming every team needs identical governance.

---

# 56. Large-Scale Architecture Exercise

## Problem

You have:

```text
200 data-producing services
500 downstream consumers
```

Design a data-contract system.

---

## Requirements

Discuss:

- ownership,
- contract registry,
- schemas,
- semantics,
- validation,
- CI,
- compatibility,
- versioning,
- deprecation,
- consumer discovery,
- monitoring,
- incident response.

---

## Model architecture

```text
Producer repositories
        ↓
Contract-as-code
        ↓
CI validation
        ↓
Contract registry
        ↓
Consumer discovery
        ↓
Runtime enforcement
        ↓
Quality monitoring
        ↓
Incident management
```

---

## Key design principle

Central infrastructure can provide:

```text
standards
tooling
registry
validation
visibility
```

while domain teams retain:

```text
ownership
semantics
quality responsibility
change responsibility
```

This avoids making the central platform team the owner of every dataset.

---

# 57. Final Practical Challenge

## Scenario

A company operates:

```text
Orders
Payments
Customers
Inventory
Shipping
```

The Data Platform team consumes all five.

You must design contracts for:

```text
Orders
Payments
```

---

## Requirements

Each contract must define:

- schema,
- semantics,
- grain,
- quality,
- freshness,
- ownership,
- version,
- compatibility,
- change policy,
- enforcement,
- consumer responsibilities.

---

## Ten changes to classify

### Change 1

Add optional:

```text
sales_channel
```

Expected reasoning:

```text
Often non-breaking.
```

---

### Change 2

Remove:

```text
currency
```

Expected:

```text
Breaking.
```

---

### Change 3

Change:

```text
customer_id: integer → string
```

Expected:

```text
Potentially breaking / breaking depending on consumers.
```

---

### Change 4

Change:

```text
amount = gross
```

to:

```text
amount = net
```

Expected:

```text
Semantic breaking change.
```

---

### Change 5

Change:

```text
timestamp = UTC
```

to:

```text
timestamp = local timezone
```

Expected:

```text
Semantic change requiring review.
```

---

### Change 6

Add a new status:

```text
refunded
```

Expected:

```text
Consumer-dependent.
```

---

### Change 7

Make:

```text
customer_id nullable
```

Expected:

```text
Potentially breaking.
```

---

### Change 8

Change grain:

```text
one row = order
```

to:

```text
one row = order line
```

Expected:

```text
Breaking semantic change.
```

---

### Change 9

Improve documentation only.

Expected:

```text
Normally non-breaking.
```

---

### Change 10

Move delivery from:

```text
06:00 UTC
```

to:

```text
10:00 UTC
```

Expected:

```text
Service-level contract change.
```

It may be operationally breaking even though the schema is unchanged.

---

# 58. Expected Reasoning Pattern

For every contract change, ask:

```text
What changed?
      ↓
Does structure change?
      ↓
Does meaning change?
      ↓
Does quality change?
      ↓
Does service expectation change?
      ↓
Which consumers depend on it?
      ↓
Is it compatible?
      ↓
What migration is required?
      ↓
What communication is required?
      ↓
Who owns the change?
```

This is the core contract-engineering mindset.

---

# 59. Production Checklist

## Contract

- [ ] Dataset identity defined.
- [ ] Producer defined.
- [ ] Consumers identified where practical.
- [ ] Schema defined.
- [ ] Semantics documented.
- [ ] Data grain documented.
- [ ] Units documented.
- [ ] Timezone documented.
- [ ] Quality rules defined.
- [ ] Freshness defined.
- [ ] Availability defined.
- [ ] Version defined.

## Ownership

- [ ] Producer owner identified.
- [ ] Consumer responsibilities documented.
- [ ] Escalation path defined.
- [ ] Incident responsibility defined.

## Change Management

- [ ] Compatibility policy defined.
- [ ] Breaking-change classification defined.
- [ ] Versioning defined.
- [ ] Deprecation process defined.
- [ ] Migration window defined.
- [ ] Consumer communication defined.

## Enforcement

- [ ] Producer CI validation.
- [ ] Contract tests.
- [ ] Ingestion validation.
- [ ] Transformation validation.
- [ ] Published-data validation.

## Operations

- [ ] Monitoring.
- [ ] Quality results.
- [ ] Freshness monitoring.
- [ ] Incident response.
- [ ] Contract lifecycle review.
- [ ] Consumer usage monitoring where practical.

---

# 60. Final Mental Model

Remember:

```text
A table is data.
```

```text
A schema describes structure.
```

```text
A data contract describes what consumers can rely on.
```

```text
Producer ownership makes someone accountable for that promise.
```

```text
Enforcement makes the promise executable.
```

```text
Versioning makes change manageable.
```

```text
Quality rules make the promise measurable.
```

```text
Semantics make the data understandable.
```

```text
Change management keeps the interface stable.
```

Therefore:

```text
Data Contract
    =
    Structure
    +
    Meaning
    +
    Quality
    +
    Service Expectations
    +
    Ownership
    +
    Versioning
    +
    Enforcement
```

The production principle is:

> **A data contract is not merely a schema file. It is an explicit, owned, measurable interface between a producer and its consumers.**

---

# 61. Code Quality Requirements

All Python, YAML, JSON, and schema examples should:

- be beginner-readable,
- use meaningful names,
- include comments where useful,
- be syntactically valid when presented as executable code,
- identify dependencies,
- distinguish illustrative examples from production implementations,
- avoid fabricated output,
- avoid fabricated benchmark numbers,
- avoid invented standards,
- avoid presenting organization-specific conventions as universal.

For important examples:

1. Explain the example.
2. Show it.
3. Break it.
4. Explain the failure.
5. Show how producer and consumer responsibilities are affected.
6. Explain production implications.

---

# 62. Standards and Specification Accuracy

For ODCS, JSON Schema, Avro, and Protobuf:

- distinguish specification concepts from illustrative examples,
- do not invent mandatory fields,
- do not invent compatibility guarantees,
- do not present organization-specific conventions as universal standards,
- label illustrative examples clearly,
- use terminology accurately.

For version-sensitive technology:

```text
identify version
    ↓
consult the applicable specification/documentation
    ↓
validate example
    ↓
test
```

The purpose is to teach reliable engineering rather than memorization of possibly outdated examples.

---

# 63. Learning Loop

For every major contract concept:

```text
Concept
    ↓
Why it exists
    ↓
Failure mode without it
    ↓
Simple example
    ↓
Technical definition
    ↓
Implementation
    ↓
Breaking/change example
    ↓
Enforcement
    ↓
Production implications
    ↓
Trade-offs
    ↓
Exercise
    ↓
Interview/architecture question
```

This is deliberately different from syntax-first learning.

The goal is to develop the ability to answer:

```text
What does this contract promise?
Why does the promise matter?
Who owns it?
How is it enforced?
What happens when it changes?
```

---

# 64. Scope Boundaries

This chapter establishes the foundations for later topics without replacing them.

## Schema evolution

This chapter introduces:

- compatibility,
- breaking changes,
- versioning,
- deprecation.

Detailed schema-evolution implementation belongs to the dedicated schema-evolution topic.

## Quarantine / DLQ

This chapter explains that contract violations may require rejection or isolation.

Detailed quarantine/DLQ architecture belongs to its dedicated topic.

## Anomaly detection

This chapter introduces freshness and service expectations.

It does not teach the complete anomaly-detection system.

## Reconciliation

A contract does not replace source/target reconciliation.

Reconciliation remains a separate quality problem.

Similarly, this chapter uses:

- Pydantic,
- Pandera,
- Great Expectations,
- Soda,

as related validation layers without reproducing their complete lessons.

---

# 65. Completion Criteria

You are ready to progress when you can independently:

- define a data contract,
- explain why a schema is not enough,
- identify producer and consumer responsibilities,
- define a contract's schema and semantics,
- document grain, units, and timezone,
- define quality requirements,
- define freshness and availability expectations,
- assign ownership,
- version a contract,
- classify breaking and non-breaking changes,
- recognize semantic breaking changes,
- design a deprecation workflow,
- explain backward and forward compatibility,
- use JSON Schema conceptually,
- explain Avro and Protobuf conceptually,
- distinguish illustrative schemas from official standards,
- implement a basic contract validation example,
- implement a basic schema diff,
- design producer CI enforcement,
- design runtime enforcement,
- design consumer migration,
- debug contract violations,
- design a producer-owned data product,
- establish a pragmatic contract-adoption strategy,
- explain when formal contracts may not be necessary,
- design contract governance at organizational scale.

---

# Final Engineering Principle

A reliable data product is not created by publishing a table and hoping consumers understand it.

The production lifecycle is:

```text
Define the interface
        ↓
Define its meaning
        ↓
Define quality
        ↓
Assign ownership
        ↓
Define service expectations
        ↓
Version the interface
        ↓
Enforce it
        ↓
Communicate changes
        ↓
Migrate consumers safely
        ↓
Monitor the contract
        ↓
Retire obsolete versions deliberately
```

The central mindset is:

> **Do not ask only, "What columns does this dataset contain?"**

Ask:

> **"What exactly does this data product promise, who owns that promise, how is it enforced, and how can it change without surprising its consumers?"**
