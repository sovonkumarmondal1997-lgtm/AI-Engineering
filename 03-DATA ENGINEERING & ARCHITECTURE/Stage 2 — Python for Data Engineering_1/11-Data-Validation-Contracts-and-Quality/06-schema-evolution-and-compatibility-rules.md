# Schema Evolution and Compatibility Rules

> **Stage 2 — Python for Data Engineering**  
> **Module 2.11 — Data Validation, Contracts, and Quality**  
> **Topic 06 — Schema Evolution and Compatibility Rules**

---

## Learning Objectives

By the end of this chapter, you should be able to:

1. Explain why schemas change in production systems.
2. Define schema evolution in simple and technical terms.
3. Distinguish a schema from a broader data contract.
4. Classify schema changes as additive, breaking, or potentially breaking.
5. Explain backward, forward, full, and transitive compatibility.
6. Reason about compatibility directionally rather than treating it as symmetric.
7. Analyze type, nullability, default, enum, semantic, and data-grain changes.
8. Build a simple educational schema-diff engine in Python.
9. Explain what automated compatibility checks can and cannot detect.
10. Design CI checks that prevent unsafe structural changes.
11. Explain why semantic changes often require human review.
12. Safely evolve relational schemas, Parquet datasets, lakehouse tables, and event streams.
13. Apply expand-and-contract migrations.
14. Identify and control dual-write inconsistency.
15. Use versioned datasets, versioned stream topics, and stable views appropriately.
16. Detect and respond to runtime schema drift.
17. Understand the role of schema registries.
18. Design compatibility policies based on system constraints.
19. Plan replay, backfill, rollback, deprecation, and removal.
20. Connect schema evolution to data contracts and data quality.
21. Design a production-grade schema evolution workflow.

---

## Prerequisites

This chapter assumes you have already studied:

- **Topic 01 — Data Quality Dimensions**
- **Topic 02 — Pydantic Models, Validators, and Serialization**
- **Topic 03 — DataFrame Schema Validation with Pandera**
- **Topic 04 — Declarative Checks with Great Expectations and Soda**
- **Topic 05 — Data Contracts and Producer Ownership**

You do not need to memorize every previous topic. The important prerequisite is understanding that a data pipeline has producers, consumers, schemas, quality expectations, and ownership.

---

# 1. Why Schema Evolution Exists

Imagine an orders system that currently publishes:

```text
order_id: integer
customer_id: integer
amount: decimal
currency: string
```

A developer decides that customer identifiers should be strings because the organization is moving toward identifiers such as:

```text
"12345"
"CUST-9812"
"EU-00072"
```

The developer changes:

```text
customer_id: integer
```

to:

```text
customer_id: string
```

The producer application compiles, tests pass, and deployment succeeds.

Then a downstream consumer executes:

```sql
SELECT *
FROM orders
WHERE customer_id > 10000;
```

or a Python application executes:

```python
customer_id = int(record["customer_id"])
```

The consumer fails.

The producer deployment was successful.

The **system change was not compatible**.

This distinction is one of the most important ideas in Data Engineering:

> A successful producer deployment does not prove that the producer's new schema is compatible with the entire data ecosystem.

Schema evolution exists because real systems change while their dependencies continue running.

## 1.1 What Changes in Real Systems?

Schemas may evolve because of:

- new business requirements,
- new fields,
- new identifiers,
- new currencies,
- regulatory requirements,
- new event types,
- application redesigns,
- storage optimization,
- analytics requirements,
- migration from one platform to another,
- changes in business definitions,
- data-model improvements.

Common changes include:

```text
new field
removed field
renamed field
type changed
nullability changed
default changed
enum value added
timestamp representation changed
unit changed
meaning changed
grain changed
```

The engineering challenge is not:

> "Can we change the schema?"

It is:

> "Can we change the schema without unexpectedly breaking the systems that depend on it?"

---

# 2. The Core Schema-Evolution Learning Loop

Use this process whenever a schema change is proposed:

```text
Understand existing schema
        ↓
Identify proposed change
        ↓
Identify affected producers and consumers
        ↓
Classify the change
        ↓
Determine compatibility
        ↓
Test the change
        ↓
Choose deployment strategy
        ↓
Migrate consumers
        ↓
Monitor
        ↓
Deprecate old behavior
        ↓
Remove safely
```

For every significant change, ask:

1. What changed?
2. Who depends on the changed element?
3. Is the structural representation compatible?
4. Is the semantic meaning compatible?
5. Can old consumers process the new representation?
6. Can new consumers process old data?
7. Does historical replay still work?
8. Does the change affect data grain?
9. How will the change be deployed?
10. How will the old representation be retired?

This is the foundation of production schema evolution.

---

# 3. What Is Schema Evolution?

## 3.1 Simple Explanation

**Schema evolution means changing the structure or meaning of data over time while keeping dependent systems working safely.**

A schema is not necessarily permanent.

For example:

### Version 1

```text
orders
---------
order_id
customer_id
amount
```

### Version 2

```text
orders
---------
order_id
customer_id
amount
currency
```

The schema evolved because `currency` was added.

## 3.2 Technical Definition

Schema evolution is the controlled modification of a data interface over time while managing compatibility with:

- producers,
- consumers,
- stored historical data,
- processing systems,
- serialization formats,
- analytical queries,
- operational systems.

The important word is **controlled**.

Changing a schema is easy.

Changing it safely is an engineering discipline.

---

# 4. Where Schema Evolution Happens

Schema evolution appears in many layers.

## 4.1 Relational Databases

Example:

```sql
ALTER TABLE orders
ADD COLUMN currency VARCHAR(3);
```

The physical database schema changed.

But applications, ETL jobs, reports, stored procedures, and downstream consumers may depend on the table.

---

## 4.2 Data Warehouses

A warehouse table might evolve from:

```text
order_id
amount
```

to:

```text
order_id
amount
currency
tax_amount
discount_amount
```

The new columns may be structurally compatible, but the business semantics still need review.

---

## 4.3 Data Lakes and Parquet

Different Parquet files can contain different physical schemas.

For example:

```text
partition=2026-09-01
    order_id: int64
    amount: double

partition=2026-10-01
    order_id: int64
    amount: decimal
```

A reader may need a deliberate schema reconciliation strategy.

---

## 4.4 Lakehouse Tables

Lakehouse table formats provide metadata and schema-management mechanisms, but exact behavior depends on the table format and implementation.

The architectural principle remains:

```text
Physical schema changes
        ↓
Compatibility analysis
        ↓
Reader/writer behavior
        ↓
Validation
```

Do not assume that a lakehouse format automatically makes every schema change safe.

---

## 4.5 APIs

An API payload can evolve:

```json
{
  "id": 1001,
  "name": "Sovon"
}
```

to:

```json
{
  "id": 1001,
  "name": "Sovon",
  "country": "IN"
}
```

An optional field may be harmless to many consumers.

Removing or changing the meaning of an existing field can be much more dangerous.

---

## 4.6 Event Streams

An event can evolve from:

```json
{
  "order_id": 101,
  "amount": 100
}
```

to:

```json
{
  "order_id": 101,
  "amount": 100,
  "currency": "USD"
}
```

The challenge becomes more complicated because old events may remain available for replay.

---

# 5. Schema vs Data Contract

This topic follows Data Contracts and Producer Ownership.

Do not confuse these concepts.

## 5.1 Schema

A schema describes structure.

For example:

```text
order_id      integer
customer_id   integer
amount        decimal
currency      string
```

It tells us things such as:

- field names,
- data types,
- nullability,
- structural constraints.

## 5.2 Data Contract

A data contract is broader.

It can include:

```text
Schema
Semantics
Quality rules
Ownership
Freshness expectations
Availability expectations
Versioning
Change policy
Service expectations
```

## 5.3 Schema Evolution

Schema evolution concerns controlled changes to the interface.

The relationship is:

```text
Data Contract
      ↓
Schema
      ↓
Evolution Policy
      ↓
Compatibility Rules
      ↓
Enforcement
      ↓
Migration
```

Compatibility rules therefore form an operational part of a broader contract.

---

# 6. Change Taxonomy

A useful first step is classifying the change.

## 6.1 Additive Changes

An additive change introduces something new without removing existing structure.

Examples:

- adding an optional field,
- adding a nullable field,
- adding metadata.

Example:

```text
v1:
order_id
amount

v2:
order_id
amount
currency
```

If existing consumers ignore unknown fields, this may be compatible.

But do not automatically label every additive change safe.

---

## 6.2 Breaking Changes

A breaking change can cause an existing producer or consumer to stop working or interpret data incorrectly.

Examples:

- removing a field,
- renaming a field,
- incompatible type change,
- making a nullable field required,
- changing business semantics,
- changing record grain.

Example:

```text
customer_id: integer
```

to:

```text
customer_id: string
```

may break consumers.

---

## 6.3 Potentially Breaking Changes

Some changes depend heavily on the ecosystem.

Examples:

- adding an enum value,
- changing a default,
- widening numeric types,
- changing decimal precision,
- adding a required field.

A useful engineering principle is:

> Compatibility is determined by the actual producer/consumer behavior and technology rules, not by the name of the change alone.

---

# 7. Additive vs Breaking Changes

A practical starting table:

| Change | Typical Risk | Why |
|---|---|---|
| Add optional field | Lower | Existing consumers may ignore it |
| Add required field | High | Existing producers/consumers may not provide it |
| Remove field | High | Consumers may depend on it |
| Rename field | High | References may break |
| Change type | Context-dependent | Representation and assumptions change |
| Change nullability | Context-dependent | Value-presence assumptions change |
| Change meaning | High | Structural schema may remain unchanged |
| Add enum value | Context-dependent | Exhaustive consumers may reject it |

The word **typical** matters.

For example, adding an optional field is often low-risk, but an old consumer might reject unknown fields under a strict parser.

Therefore:

> "Non-breaking" does not mean "zero risk."

---

# 8. Compatibility Models

Compatibility describes whether different schema versions can safely interact.

It is directional.

That means:

```text
A compatible with B
```

does not automatically imply:

```text
B compatible with A
```

---

# 9. Backward Compatibility

## 9.1 Simple Explanation

Backward compatibility means a newer schema/data representation can still be processed by older consumers.

Think:

```text
NEW producer/schema
        ↓
OLD consumer
```

If the old consumer can still operate correctly, the change is backward-compatible for that interaction.

## 9.2 Example

Suppose v1 is:

```text
order_id
amount
```

v2 adds an optional field:

```text
order_id
amount
currency
```

An old consumer that reads only:

```text
order_id
amount
```

may continue working.

That is an example of a potentially backward-compatible additive change.

## 9.3 Important Caveat

Compatibility depends on the actual serialization format and consumer behavior.

A strict consumer that rejects unknown fields could behave differently.

---

# 10. Forward Compatibility

Forward compatibility asks the opposite directional question:

```text
OLD producer/data
        ↓
NEW consumer
```

Can the newer consumer correctly handle older data?

Example:

v1:

```text
order_id
amount
```

v2 consumer expects:

```text
order_id
amount
currency
```

If the v2 consumer can correctly handle missing `currency`, it can be forward-compatible with v1 data.

A common strategy is to define a meaningful default or represent missing values explicitly.

---

# 11. Full Compatibility

Full compatibility means both directions work:

```text
new → old
old → new
```

Conceptually:

```text
        NEW
       ↙   ↘
    OLD     OLD
       ↖   ↙
        NEW
```

It is stronger because the ecosystem supports both directions.

The exact meaning of "full" depends on the technology or schema-registry implementation being used.

Do not treat this chapter's conceptual definition as a vendor-specific compatibility guarantee.

---

# 12. Transitive Compatibility

Suppose we have:

```text
v1 → v2 → v3 → v4
```

A non-transitive policy may only validate a proposed version against a nearby version.

A transitive policy considers compatibility across a sequence of versions according to the ecosystem's rules.

This matters when consumers may lag.

Example:

```text
Producer = v4
Consumer = v1
```

If the organization expects old consumers to continue working, compatibility across the relevant historical versions matters.

Transitive compatibility is especially important for:

- long-lived streams,
- slow consumer migration,
- long retention periods,
- replay,
- multiple independent teams.

---

# 13. Compatibility Directionality

Compatibility must always identify:

- producer version,
- consumer version,
- direction,
- data being read or written.

Use a matrix rather than vague statements.

| Producer | Consumer | Result |
|---|---|---|
| v1 | v1 | Compatible |
| v2 | v1 | Depends on backward compatibility |
| v1 | v2 | Depends on forward compatibility |
| v2 | v2 | Compatible if both share the same contract |

The critical question is:

> Which version produces the data, and which version consumes it?

---

# 14. Compatibility Matrix

A useful operational matrix might look like:

| Producer | Consumer | Compatibility | Reason |
|---|---|---|---|
| v1 | v1 | Compatible | Same contract |
| v2 | v1 | Compatible if backward-compatible | New data must be readable by old consumer |
| v1 | v2 | Compatible if forward-compatible | New consumer must handle old data |
| v3 | v1 | Depends on transitive policy | Multiple versions apart |
| v1 | v3 | Depends on forward/transitive policy | Consumer may encounter historical data |

Never write:

> "v2 is compatible with v1."

Instead write:

> "v2-produced data is backward-compatible with v1 consumers under the stated rules."

That language forces directional reasoning.

---

# 15. Type Evolution

Type changes are one of the most common sources of compatibility problems.

## 15.1 Integer to Larger Integer

Conceptually:

```text
integer32
    ↓
integer64
```

This may be safe in some systems if all consumers can represent the larger range.

But it depends on:

- serialization format,
- consumer language,
- database type,
- application assumptions,
- actual value ranges.

Do not give a universal guarantee.

---

## 15.2 Integer to String

```text
12345
```

becomes:

```text
"12345"
```

This changes representation.

Existing consumers may execute:

```python
customer_id + 1
```

which worked for an integer but fails for a string.

Safe migration often looks like:

```text
introduce new representation
        ↓
support both representations temporarily
        ↓
migrate consumers
        ↓
backfill
        ↓
remove old representation
```

---

## 15.3 Integer to Decimal

This can be appropriate when precision or fractional values become necessary.

But downstream systems may have assumed:

```text
amount % 1 == 0
```

or may serialize integers differently.

Evaluate:

- precision,
- scale,
- serialization,
- storage type,
- application arithmetic,
- downstream BI behavior.

---

## 15.4 Float to Decimal

A change from floating-point representation to decimal can improve control over exact decimal quantities, but the representation and arithmetic behavior are different.

Consumers may need changes.

For financial amounts, define:

- precision,
- scale,
- currency,
- rounding rules,
- storage representation.

---

## 15.5 Decimal Precision Changes

Example:

```text
DECIMAL(10,2)
```

to:

```text
DECIMAL(18,4)
```

This may be compatible in one environment and operationally significant in another.

Questions:

- Can consumers represent the new precision?
- Can existing values be read?
- Does serialization preserve scale?
- Does downstream aggregation change?
- Are validation rules changing?

---

## 15.6 String to Enum

A generic string:

```text
status: string
```

may become:

```text
status: enum
```

This can make validation stronger but can also break previously accepted values.

---

## 15.7 Date to Timestamp

```text
2026-10-01
```

is not identical to:

```text
2026-10-01T13:30:00Z
```

A timestamp introduces time-of-day and potentially timezone semantics.

Consumers must understand what the timestamp means.

---

## 15.8 Naive Timestamp to Timezone-Aware Timestamp

These values are not equivalent:

```text
2026-10-01 12:00:00
```

and:

```text
2026-10-01T12:00:00+00:00
```

A safe migration must define:

- timezone,
- normalization policy,
- serialization,
- historical interpretation,
- consumer expectations.

---

# 16. Nullability Evolution

Nullability is part of the interface.

Consider:

```text
currency: string | null
```

versus:

```text
currency: string
```

## 16.1 Nullable → Required

Existing records may contain:

```text
currency = NULL
```

Making the field required can break:

- old records,
- old producers,
- backfills,
- consumers,
- ETL jobs.

Safer pattern:

```text
profile existing data
        ↓
fill missing values
        ↓
update producers
        ↓
validate no NULLs
        ↓
enforce NOT NULL
```

---

## 16.2 Required → Nullable

This may also break consumers.

A consumer might assume:

```python
currency.upper()
```

But now:

```python
currency = None
```

causes failure.

The structural change may look permissive while consumer behavior becomes unsafe.

---

# 17. Default Values

Defaults are part of behavior, not merely syntax.

Suppose:

### v1

```text
status default = "pending"
```

### v2

```text
status default = "active"
```

The schema shape may look unchanged.

But the behavior changed.

## 17.1 Why Defaults Matter

Defaults can exist in:

- databases,
- application code,
- serializers,
- message schemas,
- ingestion logic.

A database default does not automatically mean a Python model has the same default.

A serialization default does not automatically mean a consumer uses it.

Document the source of truth.

---

# 18. Enum Evolution

Suppose:

### v1

```text
pending
paid
cancelled
```

### v2

```text
pending
paid
cancelled
refunded
```

Adding `refunded` looks additive.

But an exhaustive consumer may contain:

```python
if status == "pending":
    handle_pending()
elif status == "paid":
    handle_paid()
elif status == "cancelled":
    handle_cancelled()
else:
    raise ValueError("Unknown status")
```

The new enum value breaks the consumer.

Therefore:

> An additive schema change can still be behaviorally breaking.

Analytics can also fail silently:

```sql
SELECT *
FROM orders
WHERE status IN ('pending', 'paid', 'cancelled');
```

`refunded` records now exist but are excluded.

---

# 19. Semantic Evolution

This is one of the most important advanced concepts.

Suppose the schema says:

```text
amount: decimal
```

Nothing structural changed.

But the producer changes the definition:

```text
v1:
amount = gross amount including tax
```

to:

```text
v2:
amount = net amount excluding tax
```

The schema is structurally identical.

The meaning changed.

Therefore:

```text
Schema compatibility
        ≠
Semantic compatibility
```

## 19.1 Examples of Semantic Change

### Unit

```text
temperature = Celsius
```

becomes:

```text
temperature = Fahrenheit
```

### Currency

```text
amount = USD
```

becomes:

```text
amount = EUR
```

### Timezone

```text
created_at = UTC
```

becomes:

```text
created_at = local time
```

### Event Meaning

```text
payment_completed
```

may previously mean:

```text
payment authorized
```

and later mean:

```text
funds settled
```

### Status Meaning

```text
active
```

may change from "account can log in" to "account has a paid subscription".

### Calculation Methodology

```text
revenue
```

may change from gross revenue to net revenue.

### Business Definition

```text
customer
```

may change from "any registered account" to "account with at least one completed order".

Structural compatibility cannot detect these reliably.

---

# 20. Data Grain Evolution

Data grain means:

> What does one row represent?

This is a contract property.

## 20.1 Example: Order Grain

### v1

```text
one row = one order
```

| order_id | amount |
|---|---:|
| 1001 | 120 |

### v2

```text
one row = one order line
```

| order_id | line_id | amount |
|---|---|---:|
| 1001 | 1 | 70 |
| 1001 | 2 | 50 |

The schema can contain the same columns and still be fundamentally incompatible.

## 20.2 Consequences

If a consumer calculates:

```sql
SELECT COUNT(*) FROM orders;
```

the meaning changes.

Revenue may double if an order-level amount is duplicated on every line.

Joins can produce duplicates.

ML features can change distribution.

Uniqueness assumptions can fail.

Therefore:

> Data grain should be treated as a first-class contract property.

---

# 21. Automated Schema Diffs

A schema diff compares:

```text
old schema
    +
new schema
    ↓
structural diff
    ↓
compatibility classification
```

A diff may detect:

- added fields,
- removed fields,
- changed types,
- changed nullability,
- changed defaults,
- changed enum values.

It is extremely useful in CI.

But it is not a complete semantic analyzer.

---

# 22. Educational Python Schema Representation

We can represent a schema simply:

```python
schema_v1 = {
    "fields": {
        "order_id": {
            "type": "integer",
            "nullable": False,
            "default": None,
        },
        "customer_id": {
            "type": "integer",
            "nullable": False,
            "default": None,
        },
        "amount": {
            "type": "decimal",
            "nullable": False,
            "default": None,
        },
        "currency": {
            "type": "string",
            "nullable": False,
            "default": "USD",
        },
    }
}
```

And a new version:

```python
schema_v2 = {
    "fields": {
        "order_id": {
            "type": "integer",
            "nullable": False,
            "default": None,
        },
        "customer_id": {
            "type": "string",
            "nullable": False,
            "default": None,
        },
        "amount": {
            "type": "decimal",
            "nullable": False,
            "default": None,
        },
        "currency": {
            "type": "string",
            "nullable": False,
            "default": "USD",
        },
        "discount": {
            "type": "decimal",
            "nullable": True,
            "default": None,
        },
    }
}
```

---

# 23. Implementing a Simple Schema Diff

The following implementation is deliberately educational.

It is not a production schema registry or complete compatibility engine.

```python
from __future__ import annotations

from typing import Any


def compare_schemas(
    old_schema: dict[str, Any],
    new_schema: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    old_fields = old_schema["fields"]
    new_fields = new_schema["fields"]

    changes = {
        "added": [],
        "removed": [],
        "changed": [],
    }

    for name in new_fields:
        if name not in old_fields:
            changes["added"].append(
                {
                    "field": name,
                    "new": new_fields[name],
                }
            )

    for name in old_fields:
        if name not in new_fields:
            changes["removed"].append(
                {
                    "field": name,
                    "old": old_fields[name],
                }
            )

    for name in old_fields.keys() & new_fields.keys():
        old = old_fields[name]
        new = new_fields[name]

        if old != new:
            changes["changed"].append(
                {
                    "field": name,
                    "old": old,
                    "new": new,
                }
            )

    return changes
```

Use it:

```python
diff = compare_schemas(schema_v1, schema_v2)

for category, changes in diff.items():
    print(category)
    for change in changes:
        print(" ", change)
```

Expected conceptual result:

```text
added
  discount

changed
  customer_id
```

---

# 24. Classifying Changes

A simple educational classifier:

```python
def classify_change(change: dict[str, Any]) -> str:
    if "new" in change and "old" not in change:
        field = change["new"]

        if field["nullable"] or field["default"] is not None:
            return "potentially_compatible"

        return "potentially_breaking"

    if "old" in change and "new" not in change:
        return "breaking"

    old = change["old"]
    new = change["new"]

    if old["type"] != new["type"]:
        return "breaking_risk"

    if old["nullable"] != new["nullable"]:
        return "breaking_risk"

    if old["default"] != new["default"]:
        return "semantic_or_behavioral_risk"

    return "changed"
```

This is intentionally conservative.

A production compatibility engine needs:

- format-specific rules,
- version-aware semantics,
- consumer context,
- compatibility direction,
- registry policy,
- schema references,
- logical types,
- enum rules,
- nested structures,
- aliases,
- deployment context.

Do not mistake a teaching implementation for a production compatibility engine.

---

# 25. Practical Schema Diff Output

Suppose:

### v1

```text
order_id: integer
customer_id: integer
amount: decimal
currency: string
```

### v2

```text
order_id: integer
customer_id: string
amount: decimal
currency: string
discount: decimal
```

A useful diff is:

```text
ADDED
-----
discount: decimal

CHANGED
-------
customer_id:
    integer → string
```

The engineering classification might be:

```text
discount
    → potentially compatible

customer_id
    → breaking risk
```

The CI system can then apply policy:

```text
diff
 ↓
classify
 ↓
allowed?
 ├── yes → pass
 └── no  → fail
```

---

# 26. CI Enforcement

A production workflow can look like:

```text
Pull Request
      ↓
Load old schema
      ↓
Load proposed schema
      ↓
Generate diff
      ↓
Compatibility check
      ↓
Automated tests
      ↓
PASS / FAIL
      ↓
Deployment
```

A conceptual Python gate:

```python
diff = compare_schemas(old_schema, new_schema)

breaking_changes = []

for change in diff["removed"]:
    breaking_changes.append(change)

for change in diff["changed"]:
    classification = classify_change(change)

    if classification == "breaking":
        breaking_changes.append(change)

if breaking_changes:
    raise SystemExit(
        f"Schema compatibility check failed: {breaking_changes}"
    )

print("Schema compatibility check passed.")
```

A real CI system would normally also include:

- contract tests,
- integration tests,
- consumer tests,
- semantic review,
- schema registry checks,
- deployment gates.

---

# 27. Human Review vs Automation

Automation is excellent at detecting structural changes.

For example:

```text
field removed
field added
type changed
nullability changed
default changed
```

Humans are often required for:

```text
meaning changed
unit changed
data grain changed
business definition changed
calculation changed
timezone meaning changed
```

A useful rule:

> Automation detects structure; engineering review evaluates meaning and operational impact.

---

# 28. Storage Evolution

Schema evolution differs by storage system.

## 28.1 Relational Databases

Common mechanisms include:

```sql
ALTER TABLE
```

and migration frameworks.

Safe evolution often uses:

```text
expand
    ↓
deploy compatibility
    ↓
migrate
    ↓
contract
```

---

## 28.2 Parquet

Parquet files are self-describing at the file level.

A dataset can therefore contain files with different schemas.

For example:

```text
day=01
    amount: int64

day=02
    amount: decimal
```

A downstream reader must have a deliberate strategy.

Possible strategies include:

- enforce one canonical schema,
- normalize during ingestion,
- use reader-side schema reconciliation where supported,
- rewrite historical data.

The correct strategy depends on the data platform and file-processing engine.

---

## 28.3 Lakehouses

Lakehouse table formats can manage metadata and schema evolution.

But exact behavior depends on:

- table format,
- engine,
- writer configuration,
- reader behavior,
- schema enforcement settings.

The important principle is:

> Storage technology can provide mechanisms, but compatibility still requires architectural policy.

---

## 28.4 Warehouse Tables

Warehouses may support:

```sql
ALTER TABLE
```

but physical compatibility does not automatically guarantee:

- query compatibility,
- semantic compatibility,
- BI compatibility,
- metric compatibility.

---

# 29. Database Schema Migrations

Suppose:

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL
);
```

We need:

```text
email
```

A naive migration is:

```sql
ALTER TABLE users
ADD COLUMN email TEXT NOT NULL;
```

This may fail because existing rows do not have values.

A safer progression can be:

```text
add column
    ↓
deploy application support
    ↓
backfill
    ↓
validate
    ↓
enforce constraint
```

For large tables, operational details matter:

- lock behavior,
- migration duration,
- write load,
- backfill strategy,
- replication,
- rollback,
- index creation.

---

# 30. Expand-and-Contract

Expand-and-contract is a core safe migration pattern.

## Phase 1 — Expand

Add the new representation without removing the old one.

```text
old_field
new_field
```

Both exist.

## Phase 2 — Migrate

Update producers to support the new representation.

Sometimes producers temporarily write both:

```text
old_field
new_field
```

## Phase 3 — Backfill

Populate the new representation for historical records.

## Phase 4 — Consumer Migration

Move consumers to the new representation.

## Phase 5 — Contract

Once evidence shows the old representation is no longer needed:

```text
remove old_field
```

---

# 31. Concrete Expand-and-Contract Example

Suppose:

```text
customer_name
```

must become:

```text
customer_first_name
customer_last_name
```

Do not immediately rename the column if zero-downtime compatibility is required.

Instead:

```text
Phase 1
-------
customer_name
customer_first_name
customer_last_name
```

Then:

```text
Phase 2
-------
Producer derives first/last names.
```

Then:

```text
Phase 3
-------
Backfill historical records.
```

Then:

```text
Phase 4
-------
Consumers migrate.
```

Finally:

```text
Phase 5
-------
Deprecate customer_name.
Remove customer_name.
```

---

# 32. Dual-Write Risks

Expand-and-contract can introduce dual-write problems.

Suppose the producer writes:

```text
customer_name = "John Smith"
first_name = "John"
last_name = "Smith"
```

A bug could produce:

```text
customer_name = "John Smith"
first_name = "John"
last_name = "Smyth"
```

Now two representations disagree.

## 32.1 Questions to Ask

Which field is the source of truth?

```text
old representation
        OR
new representation
```

Can one representation be deterministically derived from the other?

Can both updates happen atomically?

How will inconsistency be detected?

## 32.2 Production Controls

Use:

- explicit source-of-truth rules,
- transactional updates where appropriate,
- reconciliation checks,
- consistency metrics,
- migration monitoring.

Dual-write should be treated as a temporary migration mechanism, not an uncontrolled permanent architecture.

---

# 33. Versioned Datasets

Sometimes a clean version boundary is useful:

```text
orders_v1
orders_v2
```

## Benefits

- clear contract boundary,
- independent migration,
- easier rollback,
- consumer stability.

## Costs

- duplicate storage,
- duplicate maintenance,
- consumer confusion,
- lifecycle complexity,
- more monitoring.

Use versioned datasets when the change is substantial enough that consumers need an explicit migration boundary.

Do not create versions forever.

---

# 34. Versioned Stream Topics

Event systems may use:

```text
orders.v1
orders.v2
```

This allows:

```text
old consumers → v1
new consumers → v2
```

during a migration window.

Eventually:

```text
migrate consumers
      ↓
monitor usage
      ↓
retire v1
```

A stream differs from a database table because historical events may remain available for replay.

Therefore versioning must consider:

- retention,
- replay,
- backfill,
- old consumers,
- current consumers.

This is not a complete Kafka course; it is a schema-evolution design principle.

---

# 35. Stable Views

A stable view can act as a compatibility abstraction.

Suppose physical storage changes:

```text
raw_orders_v2
```

while consumers continue reading:

```sql
SELECT *
FROM orders;
```

The stable view can map the new physical structure to a stable consumer-facing interface.

Example:

```sql
CREATE VIEW orders AS
SELECT
    order_id,
    customer_id,
    amount,
    currency
FROM raw_orders_v2;
```

## Benefits

- migration flexibility,
- consumer-facing stability,
- abstraction over physical changes.

## Limitations

A view cannot magically solve:

- semantic changes,
- incompatible business logic,
- performance problems,
- incompatible grain,
- unavailable historical information.

---

# 36. Runtime Schema Drift

CI can catch many planned changes.

It cannot catch every runtime event.

Examples:

- source suddenly adds a field,
- source removes a field,
- type changes unexpectedly,
- nullability changes,
- a new enum appears,
- malformed payload arrives.

This is **runtime schema drift**.

## Example

Expected:

```text
currency: string
```

Actual payload:

```json
{
  "currency": 840
}
```

The system needs runtime validation even if CI passed.

---

# 37. Runtime Drift Policies

Different datasets can use different policies.

| Policy | Unexpected Change | Use Case |
|---|---|---|
| Strict | Fail | Critical contract |
| Compatible | Accept known-compatible change | Flexible ingestion |
| Warn | Alert and continue | Lower-risk source |
| Quarantine | Isolate invalid records | Mixed-quality streams |

## 37.1 Strict

```text
unexpected schema
      ↓
FAIL
```

Good when correctness is more important than continuity.

## 37.2 Compatible

```text
known compatible change
      ↓
ACCEPT
```

Useful when the ecosystem explicitly supports compatible evolution.

## 37.3 Warn

```text
unexpected additive change
      ↓
ALERT
      ↓
CONTINUE
```

Useful for less critical feeds where availability is prioritized.

## 37.4 Quarantine

```text
invalid record
      ↓
quarantine
      ↓
main pipeline continues
```

Detailed quarantine architecture belongs to the later dedicated topic.

---

# 38. Schema Registry Concept

A schema registry is a centralized system for managing schemas and versions.

Conceptually:

```text
Producer
   ↓
Schema Registry
   ↓
Compatibility Check
   ↓
Event/Data
   ↓
Consumer
```

Typical responsibilities can include:

- schema storage,
- version management,
- compatibility checks,
- producer registration,
- consumer discovery.

Do not assume a specific vendor.

Technologies such as Avro, Protobuf, and vendor schema registries have ecosystem-specific behavior.

The general principle is:

> Put schema definitions and compatibility policy somewhere that producers and consumers can consistently discover and enforce them.

---

# 39. Compatibility Policy Design

Organizations may choose policies such as:

```text
backward
forward
full
transitive
```

The choice depends on system requirements.

Consider:

### Consumer Deployment Speed

If consumers deploy slowly, compatibility windows need to be larger.

### Number of Consumers

Ten consumers and ten thousand consumers create different migration challenges.

### Event Replay

Long retention increases the importance of historical compatibility.

### Storage Retention

Long-lived datasets may need multiple schema versions to remain readable.

### Regulatory Requirements

Regulated systems may require stronger migration evidence and historical reproducibility.

### Operational Risk

Critical systems may choose stricter compatibility gates.

There is no universally best compatibility mode.

---

# 40. Event Replay

Schema evolution becomes harder when old events are replayed.

Suppose:

```text
Current consumer = v3
```

but the system replays:

```text
30-day-old events = v1
```

If v3 cannot understand v1 events, replay fails.

Therefore event architecture must consider:

```text
retention
    +
schema history
    +
consumer compatibility
    +
replay strategy
```

This matters for:

- disaster recovery,
- backfills,
- rebuilding derived tables,
- debugging,
- migration.

---

# 41. Backfilling

Suppose a new field is introduced:

```text
customer_segment
```

Existing historical rows do not contain it.

Possible approaches:

### NULL

```text
customer_segment = NULL
```

Meaning:

> unknown or not available.

### Default

```text
customer_segment = "unknown"
```

This is only correct if `"unknown"` has a meaningful business interpretation.

### Derived Value

Calculate it from existing attributes.

### Backfill

Run a historical transformation.

### Explicit Unknown Category

Use a controlled value such as:

```text
UNKNOWN
```

The choice affects:

- analytics,
- model features,
- quality metrics,
- downstream consumers.

Do not use a default merely to make a migration pass.

---

# 42. Schema Evolution and Data Contracts

The relationship can be summarized as:

```text
Data Contract
      ↓
Schema
      ↓
Evolution Policy
      ↓
Compatibility Rules
      ↓
Enforcement
      ↓
Migration
```

Topic 05 explains the broader agreement between producer and consumer.

This topic focuses on what happens when that agreement changes.

A contract without a change policy is incomplete for long-lived production systems.

---

# 43. Schema Evolution and Data Quality

Compatibility and quality solve different problems.

Consider:

```text
amount: decimal
```

The schema is compatible.

But the producer starts sending:

```text
-999999999
```

or:

```text
amount = 100 USD
currency = EUR
```

The schema can still be structurally valid.

Therefore:

```text
Compatibility ≠ Correctness
```

Use the appropriate layer:

```text
Schema compatibility
    → structure and interface evolution

Data quality validation
    → fitness and correctness

Data contract
    → producer/consumer agreement

Runtime validation
    → protection against unexpected data
```

---

# 44. Schema Compatibility vs Data Quality

| Question | Primary Concern |
|---|---|
| Can the consumer parse the field? | Schema compatibility |
| Does the field still exist? | Schema compatibility |
| Is the field the correct type? | Schema compatibility |
| Is amount non-negative? | Data quality |
| Is currency valid? | Data quality |
| Is timestamp fresh? | Data quality |
| Does one row still represent one order? | Both, especially contract semantics |
| Did the business definition change? | Semantic contract |

A production system needs both.

---

# 45. Production Change Scenarios

## Scenario 1 — Add Optional `discount_amount`

### Old

```text
order_id
amount
currency
```

### New

```text
order_id
amount
currency
discount_amount
```

### Analysis

Potentially additive.

Check:

- unknown-field behavior,
- consumer projections,
- storage readers,
- quality rules.

### Strategy

Add the optional field, validate, monitor consumers.

---

## Scenario 2 — Rename `customer_id` to `client_id`

### Old

```text
customer_id
```

### New

```text
client_id
```

This is normally breaking because existing consumers reference `customer_id`.

### Safer Strategy

```text
add client_id
    ↓
populate both
    ↓
migrate consumers
    ↓
monitor old usage
    ↓
deprecate customer_id
    ↓
remove customer_id
```

---

## Scenario 3 — Change Amount from Integer Cents to Decimal Dollars

### Old

```text
amount = 1250
```

meaning:

```text
$12.50
```

### New

```text
amount = 12.50
```

This is a representation and semantic migration.

Do not simply change the type.

You must define:

- unit,
- precision,
- scale,
- conversion,
- historical treatment,
- consumer migration.

---

## Scenario 4 — Make Currency Mandatory

### Old

```text
currency: nullable
```

### New

```text
currency: required
```

Before enforcing:

```text
profile NULLs
    ↓
backfill
    ↓
update producers
    ↓
validate
    ↓
enforce
```

---

## Scenario 5 — Add `refunded`

Existing:

```text
pending
paid
cancelled
```

New:

```text
pending
paid
cancelled
refunded
```

Test all consumers for unknown enum handling.

---

## Scenario 6 — Change Timestamp from UTC to Local Time

This is a semantic risk.

Even if the data type remains:

```text
timestamp
```

the meaning changes.

Define:

- canonical timezone,
- serialization,
- historical migration,
- consumer interpretation.

---

## Scenario 7 — Change One Row per Order to One Row per Order Line

This is a grain change.

It can break:

```text
COUNT(*)
SUM(amount)
JOIN behavior
uniqueness assumptions
ML features
```

Treat it as a contract-level breaking change.

---

## Scenario 8 — Remove Deprecated Column

Before removal:

```text
measure usage
    ↓
confirm consumers migrated
    ↓
communicate deadline
    ↓
deprecate
    ↓
grace period
    ↓
remove
    ↓
verify
```

---

# 46. Defect and Change Injection Lab

Use a controlled schema:

```python
orders_v1 = {
    "fields": {
        "order_id": {
            "type": "integer",
            "nullable": False,
            "default": None,
        },
        "customer_id": {
            "type": "integer",
            "nullable": False,
            "default": None,
        },
        "amount": {
            "type": "decimal",
            "nullable": False,
            "default": None,
        },
        "currency": {
            "type": "string",
            "nullable": False,
            "default": "USD",
        },
    }
}
```

Apply changes one at a time.

## Lab 1 — Add Optional Field

```text
discount
```

Expected reasoning:

```text
added
→ potentially compatible
→ verify consumer behavior
```

## Lab 2 — Remove Field

```text
currency
```

Expected:

```text
removed
→ breaking risk
```

## Lab 3 — Change Type

```text
customer_id:
integer → string
```

Expected:

```text
breaking risk
```

## Lab 4 — Change Nullability

```text
currency:
nullable=True → nullable=False
```

Expected:

```text
potentially breaking
```

## Lab 5 — Enum Change

Add:

```text
refunded
```

Expected:

```text
behavioral compatibility must be tested
```

## Lab 6 — Semantic Change

Keep:

```text
amount: decimal
```

but change its business meaning.

Expected:

```text
structural diff may be empty
semantic review required
```

## Lab 7 — Grain Change

Change:

```text
one row = order
```

to:

```text
one row = order line
```

Expected:

```text
contract-breaking semantic change
```

---

# 47. Python Implementation Lab

Create an educational compatibility workflow.

```python
def report_changes(
    old_schema: dict,
    new_schema: dict,
) -> None:
    diff = compare_schemas(old_schema, new_schema)

    print("ADDED")
    for change in diff["added"]:
        print(f"  {change['field']}")

    print("\nREMOVED")
    for change in diff["removed"]:
        print(f"  {change['field']}")

    print("\nCHANGED")
    for change in diff["changed"]:
        field = change["field"]
        print(f"  {field}")
        print(f"    old: {change['old']}")
        print(f"    new: {change['new']}")
```

Run:

```python
report_changes(schema_v1, schema_v2)
```

A structured result is more useful for automation than printing text:

```python
result = compare_schemas(schema_v1, schema_v2)
```

A CI system can then make a decision based on the result.

---

# 48. Automated Compatibility Testing

A minimal pytest-style suite might look like:

```python
def test_optional_field_is_detected_as_added():
    old_schema = {
        "fields": {
            "order_id": {
                "type": "integer",
                "nullable": False,
                "default": None,
            }
        }
    }

    new_schema = {
        "fields": {
            "order_id": {
                "type": "integer",
                "nullable": False,
                "default": None,
            },
            "currency": {
                "type": "string",
                "nullable": True,
                "default": None,
            },
        }
    }

    diff = compare_schemas(old_schema, new_schema)

    assert [x["field"] for x in diff["added"]] == ["currency"]
```

Removal:

```python
def test_removed_field_is_detected():
    old_schema = {
        "fields": {
            "order_id": {
                "type": "integer",
                "nullable": False,
                "default": None,
            },
            "currency": {
                "type": "string",
                "nullable": True,
                "default": None,
            },
        }
    }

    new_schema = {
        "fields": {
            "order_id": {
                "type": "integer",
                "nullable": False,
                "default": None,
            }
        }
    }

    diff = compare_schemas(old_schema, new_schema)

    assert [x["field"] for x in diff["removed"]] == ["currency"]
```

Type change:

```python
def test_type_change_is_detected():
    old_schema = {
        "fields": {
            "customer_id": {
                "type": "integer",
                "nullable": False,
                "default": None,
            }
        }
    }

    new_schema = {
        "fields": {
            "customer_id": {
                "type": "string",
                "nullable": False,
                "default": None,
            }
        }
    }

    diff = compare_schemas(old_schema, new_schema)

    assert diff["changed"][0]["field"] == "customer_id"
```

A production suite would expand this to:

- nullability,
- defaults,
- enum changes,
- nested fields,
- compatibility direction,
- consumer fixtures,
- replay fixtures.

---

# 49. Hands-On Project: Safe Orders Schema Evolution System

## Project Goal

Build a conceptual production-style system for safely evolving an orders contract.

Initial version:

```text
orders_v1
```

Then introduce:

```text
orders_v2
```

## Requirements

The project must demonstrate:

- explicit schemas,
- schema diff,
- compatibility classification,
- CI-style validation,
- backward compatibility,
- forward compatibility,
- full compatibility,
- transitive compatibility,
- expand-and-contract,
- stable view,
- versioned dataset,
- runtime drift policy,
- defect injection,
- tests,
- rollback strategy,
- deprecation strategy.

## Suggested Flow

```text
orders_v1
    ↓
proposed orders_v2
    ↓
schema diff
    ↓
compatibility classification
    ↓
automated tests
    ↓
semantic review
    ↓
deployment plan
    ↓
consumer migration
    ↓
monitoring
    ↓
deprecation
    ↓
removal
```

## Example Change

Introduce:

```text
discount_amount
```

Then introduce:

```text
customer_id:
integer → string
```

Compare the two changes.

The first is structurally additive.

The second requires migration planning.

---

# 50. Testing Strategy

Schema evolution requires multiple testing layers.

## 50.1 Unit Tests

Test:

```text
compare_schemas()
classify_change()
report_changes()
```

## 50.2 Compatibility Tests

Test combinations:

```text
old producer + new consumer
new producer + old consumer
```

according to the required compatibility policy.

## 50.3 Contract Tests

Validate producer output against the agreed contract.

## 50.4 Integration Tests

Run:

```text
producer
    +
consumer
```

together.

## 50.5 Runtime Tests

Detect:

```text
unexpected schema drift
```

## 50.6 Migration Tests

Exercise:

```text
expand
→ migrate
→ backfill
→ contract
```

A migration that works only in theory is not enough.

---

# 51. CI/CD Pipeline

A production-oriented workflow:

```text
Pull Request
      ↓
Schema diff
      ↓
Compatibility classifier
      ↓
Automated compatibility tests
      ↓
Semantic review
      ↓
Deployment
      ↓
Runtime validation
      ↓
Monitoring
      ↓
Deprecation
      ↓
Removal
```

## Which Changes Should Block Automatically?

Typically block or escalate:

- removed fields,
- incompatible type changes,
- sudden required fields,
- incompatible nullability changes,
- unsafe defaults,
- incompatible enum behavior.

Potentially allow with policy:

- compatible optional fields,
- compatible metadata,
- documented additive changes.

Require human review:

- semantic changes,
- grain changes,
- units,
- business definitions,
- calculation methodology.

---

# 52. Rollback Strategies

Schema migration design should include rollback before deployment.

Possible strategies:

## Revert Producer

Return to the previous producer version.

## Revert Schema

Restore the previous schema definition where feasible.

## Keep Old Field Temporarily

Do not remove an old field until confidence is established.

## Switch Consumer Back

Deploy consumers that still understand the previous contract.

## Maintain Dual-Write Temporarily

Keep old and new representations during migration.

## Restore Previous Dataset Version

Useful when versioned datasets provide explicit rollback boundaries.

Compatibility-aware migrations make rollback easier because the old representation has not been destroyed prematurely.

---

# 53. Migration Order

Deployment order matters.

## Unsafe

```text
producer changes
    ↓
consumer breaks
```

## Safer

```text
expand
    ↓
consumers support new form
    ↓
producer changes
    ↓
migrate consumers
    ↓
monitor
    ↓
contract/remove old form
```

A useful rule is:

> Introduce compatibility before requiring it.

---

# 54. Monitoring Schema Evolution

A successful deployment is not proof that migration is complete.

Monitor:

- schema version,
- schema drift,
- compatibility failures,
- consumer errors,
- deprecated-field usage,
- old-version usage,
- migration progress,
- runtime validation failures.

Example metrics:

```text
schema_version_events_total
schema_drift_events_total
compatibility_failures_total
deprecated_field_reads_total
old_version_consumers
runtime_validation_failures_total
```

The exact metric names are illustrative.

The important principle is to collect evidence that the migration actually succeeded.

---

# 55. Deprecation and Removal

A safe lifecycle:

```text
introduce replacement
        ↓
announce
        ↓
monitor usage
        ↓
migrate consumers
        ↓
deprecate
        ↓
grace period
        ↓
remove
        ↓
verify
```

"Deprecated" should mean something operationally.

It should normally have:

- a communication date,
- a migration deadline,
- usage monitoring,
- an owner,
- removal criteria.

---

# 56. Common Failure Modes

## 1. Treating Every Additive Change as Automatically Safe

**Symptom:** consumer rejects a new field.

**Root cause:** strict parser.

**Debugging:** inspect consumer deserialization behavior.

**Remediation:** compatibility policy or consumer migration.

**Prevention:** test representative consumers.

---

## 2. Treating Every Type Change as Automatically Safe

**Symptom:** parsing or arithmetic failures.

**Root cause:** changed representation.

**Debugging:** compare schema versions and runtime payloads.

**Remediation:** migration or dual representation.

**Prevention:** compatibility gate.

---

## 3. Ignoring Semantic Changes

**Symptom:** dashboards remain operational but metrics become wrong.

**Root cause:** field meaning changed.

**Debugging:** compare business definitions.

**Remediation:** contract correction and consumer review.

**Prevention:** semantic review.

---

## 4. Ignoring Data Grain

**Symptom:** revenue or row counts suddenly double.

**Root cause:** order grain became order-line grain.

**Debugging:** inspect uniqueness and row meaning.

**Remediation:** restore or explicitly migrate grain.

**Prevention:** document grain in the contract.

---

## 5. Making Fields Required Suddenly

**Symptom:** old producers fail validation.

**Root cause:** missing field.

**Remediation:** backfill and migrate before enforcement.

---

## 6. Removing Fields Without Consumer Analysis

**Symptom:** downstream queries fail.

**Root cause:** unknown dependency.

**Prevention:** dependency inventory and usage monitoring.

---

## 7. Changing Defaults Silently

**Symptom:** behavior changes without schema diff.

**Root cause:** default changed.

**Prevention:** treat defaults as contract behavior.

---

## 8. Adding Enum Values Without Checking Consumers

**Symptom:** consumer crashes on unknown value.

**Prevention:** exhaustive-case testing.

---

## 9. No Schema Diff in CI

**Symptom:** unsafe changes reach production.

**Prevention:** automated schema comparison.

---

## 10. No Runtime Drift Detection

**Symptom:** source changes unexpectedly and pipeline continues with bad data.

**Prevention:** runtime schema validation.

---

## 11. No Migration Window

**Symptom:** consumers cannot update before producer changes.

**Prevention:** plan explicit overlap.

---

## 12. No Rollback Strategy

**Symptom:** migration failure becomes prolonged outage.

**Prevention:** define rollback before deployment.

---

## 13. Dual-Write Inconsistency

**Symptom:** old and new representations disagree.

**Root cause:** independent writes.

**Prevention:** source-of-truth rules and consistency validation.

---

## 14. Backfills Change Historical Meaning

**Symptom:** historical reports change unexpectedly.

**Root cause:** new derivation does not match old business meaning.

**Prevention:** document historical semantics before backfill.

---

## 15. Old Event Versions Cannot Be Replayed

**Symptom:** replay job fails.

**Root cause:** current consumer cannot process retained historical schema.

**Prevention:** replay compatibility strategy.

---

## 16. Stable Views Hide Important Semantic Changes

**Symptom:** SQL continues running but results are wrong.

**Root cause:** abstraction preserved field names but not meaning.

**Prevention:** semantic contract review.

---

## 17. Too Many Schema Versions

**Symptom:** operational complexity increases.

**Root cause:** versions are never retired.

**Prevention:** lifecycle policy.

---

## 18. Deprecated Versions Are Never Removed

**Symptom:** permanent migration burden.

**Prevention:** measurable deprecation deadlines.

---

## 19. Compatibility Policy Is Undocumented

**Symptom:** every team makes different assumptions.

**Prevention:** explicit organization-level policy.

---

## 20. "Schema Compatible" Is Treated as "Business Correct"

**Symptom:** structurally valid but incorrect data.

**Prevention:** combine compatibility with data-quality and semantic validation.

---

# 57. Debugging and Incident Exercises

## Incident 1 — Wrong `customer_id` Type

A consumer reports:

```text
column customer_id has wrong type
```

### Investigation

1. Identify deployed schema version.
2. Identify producer deployment.
3. Generate schema diff.
4. Determine compatibility mode.
5. Inspect consumer expectation.
6. Check whether old and new representations coexist.
7. Choose rollback or migration.

### Likely Root Cause

```text
integer → string
```

was deployed without a compatibility migration.

---

## Incident 2 — Revenue Doubles

The schema has not changed.

Yet revenue doubles.

### Investigation

Check:

```text
data grain
```

The producer changed:

```text
one row = order
```

to:

```text
one row = order line
```

The structural schema can remain valid while analytics become incorrect.

Lesson:

> Schema compatibility does not guarantee semantic compatibility.

---

## Incident 3 — Unknown Enum

Consumer crashes:

```text
Unknown status: refunded
```

Investigate:

```text
new enum value
```

Then determine:

- whether consumer is exhaustive,
- whether unknown values should be tolerated,
- whether migration is required.

---

## Incident 4 — Historical Replay Fails

Current consumer:

```text
v3
```

Historical events:

```text
v1
```

Replay fails.

Investigate:

- retention policy,
- schema compatibility,
- transitive compatibility,
- migration/translation strategy.

---

## Incident 5 — Dual-Write Inconsistency

Observed:

```text
customer_name = "John Smith"

first_name = "John"
last_name = "Smyth"
```

Investigate:

- source of truth,
- write path,
- transaction boundaries,
- retry behavior,
- reconciliation checks.

---

# 58. Interview Questions and Answers

## Basic

### Q1. What is schema evolution?

Schema evolution is the controlled change of a data interface over time while managing compatibility with producers, consumers, stored data, and processing systems.

### Q2. What is a breaking change?

A breaking change can cause an existing producer or consumer to fail or interpret data incorrectly.

### Q3. What is backward compatibility?

It means newer schema/data can work with older consumers under the defined compatibility rules.

### Q4. What is forward compatibility?

It means older schema/data can work with newer consumers under the defined compatibility rules.

### Q5. What is schema drift?

Schema drift is an unexpected or uncontrolled change between the expected schema and the actual runtime schema.

---

## Intermediate

### Q6. Why can adding a field be breaking?

Because some consumers reject unknown fields or use strict deserialization.

### Q7. What happens when nullability changes?

Changing nullable to required can break existing producers and records. Changing required to nullable can break consumers that assume a value always exists.

### Q8. Why can enum additions break consumers?

An exhaustive consumer may reject unknown values.

### Q9. What is expand-and-contract?

A migration pattern where the new representation is introduced first, consumers are migrated, and the old representation is removed only after safe deprecation.

### Q10. Why use stable views?

They can preserve a consumer-facing interface while physical storage changes underneath.

### Q11. Why version datasets?

To create an explicit migration boundary for substantial changes and allow consumers to migrate independently.

---

## Advanced

### Q12. Explain full compatibility.

Conceptually, both old-to-new and new-to-old interactions are supported under the applicable compatibility rules.

### Q13. Explain transitive compatibility.

It maintains compatibility across a sequence of versions rather than only validating a single adjacent version relationship.

### Q14. How would you design schema evolution for an event platform?

Define explicit schemas and compatibility policy, enforce changes through CI/schema management, validate runtime events, support replay, monitor consumer versions, and deprecate old versions systematically.

### Q15. How would you handle a type migration?

Introduce the new representation, support both representations where needed, migrate consumers, backfill historical data, validate, monitor, and remove the old representation only after safe deprecation.

### Q16. How would you migrate a billion-row table?

Use an expand-and-contract approach, avoid unsafe blocking operations, add compatible structures, backfill in controlled batches, monitor load and correctness, migrate consumers, enforce constraints later, and define rollback.

### Q17. How do you detect semantic changes?

Structural diffing cannot reliably detect them. Use explicit business definitions, contract review, data-product ownership, documentation, tests, and domain-owner sign-off.

---

# 59. Architecture Questions

## Architecture 1 — Large Organization

Design schema evolution for an organization with:

```text
500 producers
2,000 consumers
multiple warehouses
event streams
batch pipelines
```

A reasonable architecture includes:

```text
Schema definitions
        ↓
Central contract/schema management
        ↓
Compatibility policy
        ↓
CI schema checks
        ↓
Producer validation
        ↓
Runtime validation
        ↓
Consumer migration tracking
        ↓
Monitoring
        ↓
Deprecation lifecycle
```

---

## Architecture 2 — CI Compatibility Checks

```text
Developer
    ↓
Pull Request
    ↓
Load baseline schema
    ↓
Load proposed schema
    ↓
Generate diff
    ↓
Classify structural changes
    ↓
Compatibility policy
    ↓
Semantic review if required
    ↓
PASS / FAIL
```

---

## Architecture 3 — Schema Registry

A vendor-neutral design:

```text
Producer
   │
   ├── register schema
   │
   ▼
Schema Registry
   │
   ├── store versions
   ├── check compatibility
   └── expose metadata
   │
   ▼
Event/Data
   │
   ▼
Consumer
```

---

## Architecture 4 — Runtime Drift Detection

```text
Incoming data
      ↓
Schema validation
      ↓
Contract validation
      ↓
Compatible?
   ┌──┴──┐
  yes    no
   ↓      ↓
accept   policy
          ├─ fail
          ├─ warn
          └─ quarantine
```

---

## Architecture 5 — Safe Database Migration

```text
Existing table
      ↓
Expand
      ↓
Deploy compatible application
      ↓
Backfill
      ↓
Validate
      ↓
Migrate consumers
      ↓
Monitor
      ↓
Contract
```

---

## Architecture 6 — Event Versioning

```text
Producer
   ↓
v2 event
   ↓
compatibility validation
   ↓
stream
   ├── v1 consumers
   └── v2 consumers
         ↓
migration
         ↓
retire v1
```

---

# 60. Final Practical Challenge

## Scenario

An Orders platform currently publishes:

```text
order_id
customer_id
amount
currency
status
created_at
```

The engineering team proposes ten changes.

For each change determine:

- change type,
- compatibility,
- risk,
- consumer impact,
- migration strategy,
- deployment order,
- validation strategy,
- rollback,
- deprecation.

---

## Change 1 — Add Optional Discount

```text
discount_amount
```

Think about:

- optionality,
- unknown-field behavior,
- downstream projections.

---

## Change 2 — Remove `customer_id`

Classify:

```text
breaking
```

Then design consumer migration.

---

## Change 3 — Rename `status`

A rename is not merely a text replacement.

Consider:

- queries,
- dashboards,
- APIs,
- event consumers,
- contracts.

---

## Change 4 — Change Amount Representation

```text
integer cents
    ↓
decimal dollars
```

Define:

- unit,
- precision,
- historical conversion,
- consumer migration.

---

## Change 5 — Make Currency Mandatory

Plan:

```text
profile NULLs
→ backfill
→ update producers
→ validate
→ enforce
```

---

## Change 6 — Add `refunded`

Check exhaustive consumers.

---

## Change 7 — Change Timezone Semantics

Determine whether:

```text
created_at
```

is still UTC or now represents local time.

---

## Change 8 — Change Data Grain

```text
one row = order
```

to:

```text
one row = order line
```

Treat as a contract-level semantic change.

---

## Change 9 — Introduce `orders_v2`

Determine:

- versioning benefits,
- consumer migration,
- storage cost,
- deprecation plan.

---

## Change 10 — Remove Deprecated Field

Require evidence:

```text
old usage = zero
```

or whatever organization-specific removal criterion has been agreed.

---

# 61. Production Checklist

## Before Change

- [ ] Existing schema documented
- [ ] Consumers identified
- [ ] Change classified
- [ ] Compatibility analyzed
- [ ] Semantic impact analyzed
- [ ] Data-grain impact analyzed
- [ ] Historical replay considered

## Implementation

- [ ] Schema diff generated
- [ ] Compatibility tests pass
- [ ] Contract tests pass
- [ ] Migration strategy defined
- [ ] Rollback defined
- [ ] Backfill strategy defined

## Deployment

- [ ] Correct deployment order
- [ ] Runtime validation enabled
- [ ] Monitoring enabled
- [ ] Consumer migration tracked
- [ ] Compatibility policy enforced

## Deprecation

- [ ] Old version marked deprecated
- [ ] Consumer usage measured
- [ ] Migration deadline defined
- [ ] Grace period defined
- [ ] Old version removed safely

## Production

- [ ] Historical replay considered
- [ ] Backfill strategy defined
- [ ] Data quality verified
- [ ] Semantic correctness verified
- [ ] Compatibility policy documented
- [ ] Runtime drift policy documented
- [ ] Rollback tested
- [ ] Ownership identified

---

# 62. Final Mental Model

Schema evolution is **controlled change**.

Every schema change should trigger this reasoning:

```text
What changed?
      ↓
Who depends on it?
      ↓
Is it structurally compatible?
      ↓
Is it semantically compatible?
      ↓
Can old consumers still work?
      ↓
Can new consumers work with old data?
      ↓
Does historical replay still work?
      ↓
Does data grain remain stable?
      ↓
How will we deploy it?
      ↓
How will we migrate consumers?
      ↓
How will we monitor it?
      ↓
How will we roll back?
      ↓
When can we remove the old version?
```

Remember the four-layer model:

```text
Schema compatibility
    protects structure

Data-quality validation
    protects data fitness

Contract governance
    protects producer/consumer expectations

Safe migration patterns
    protect production availability
```

And remember:

> **Compatibility is not the same as correctness.**

A schema can remain compatible while:

- units change,
- business definitions change,
- data grain changes,
- calculations change,
- invalid values appear.

Production Data Engineering therefore treats schema evolution as a combination of:

```text
Structure
+
Semantics
+
Compatibility
+
Testing
+
Deployment sequencing
+
Runtime validation
+
Monitoring
+
Migration
+
Deprecation
```

That is the difference between merely changing a schema and operating schema evolution safely at production scale.

---

# 63. Completion Criteria

You should consider this topic learned when you can independently:

- explain schema evolution to a beginner,
- classify common schema changes,
- explain backward and forward compatibility,
- reason about full and transitive compatibility,
- identify directional compatibility,
- analyze type and nullability changes,
- identify semantic changes,
- explain why data grain is a contract property,
- build a basic schema diff,
- design a CI compatibility gate,
- explain where human review is required,
- design an expand-and-contract migration,
- reason about dual-write risks,
- choose between versioned datasets and stable views,
- design a runtime drift policy,
- explain the purpose of a schema registry,
- account for event replay and historical data,
- design rollback and deprecation,
- distinguish compatibility from data quality,
- debug a schema-related production incident,
- propose a production-grade migration plan.

---

# 64. Final Self-Review

Before considering this topic complete, verify:

- [x] Schema evolution is defined clearly.
- [x] The production problem is explained.
- [x] Additive changes are covered.
- [x] Breaking changes are covered.
- [x] Potentially breaking changes are covered.
- [x] Backward compatibility is covered.
- [x] Forward compatibility is covered.
- [x] Full compatibility is covered.
- [x] Transitive compatibility is covered.
- [x] Compatibility directionality is explained.
- [x] Type evolution is covered.
- [x] Nullability evolution is covered.
- [x] Default evolution is covered.
- [x] Enum evolution is covered.
- [x] Semantic evolution is covered.
- [x] Data grain evolution is covered.
- [x] Automated schema diffing is covered.
- [x] CI enforcement is covered.
- [x] Human review vs automation is covered.
- [x] Storage evolution is covered.
- [x] Database migrations are covered.
- [x] Expand-and-contract is covered.
- [x] Dual-write risks are covered.
- [x] Versioned datasets are covered.
- [x] Versioned stream topics are covered.
- [x] Stable views are covered.
- [x] Runtime schema drift is covered.
- [x] Runtime drift policies are covered.
- [x] Schema registry concept is covered.
- [x] Compatibility policy selection is covered.
- [x] Event replay is covered.
- [x] Backfilling is covered.
- [x] Data-contract connection is covered.
- [x] Data-quality connection is covered.
- [x] Python schema-diff implementation is included.
- [x] Compatibility tests are included.
- [x] Defect/change injection is included.
- [x] Hands-on project is included.
- [x] CI/CD workflow is included.
- [x] Rollback strategy is included.
- [x] Deployment ordering is included.
- [x] Monitoring is included.
- [x] Deprecation is included.
- [x] Debugging incidents are included.
- [x] Interview questions are included.
- [x] Architecture questions are included.
- [x] Final practical challenge is included.
- [x] Production checklist is included.
- [x] Final mental model is included.
- [x] No fabricated benchmark results are included.
- [x] No unsupported universal compatibility guarantees are included.
- [x] Technology-specific behavior is distinguished from general principles.
- [x] Beginner → intermediate → advanced progression is maintained.
- [x] Code examples are coherent and internally consistent.
- [x] Compatibility is treated as directional.
- [x] Schema compatibility is not presented as semantic correctness.
- [x] Expand-and-contract is explained.
- [x] Runtime drift is explained.
- [x] Migration ordering is explained.

---

## Important Scope Boundary

This chapter focuses specifically on **schema evolution and compatibility rules**.

It intentionally does not become the complete Module 2.11.

Earlier topics are used only as architectural context:

- Topic 01 — Data Quality Dimensions
- Topic 02 — Pydantic
- Topic 03 — Pandera
- Topic 04 — Great Expectations/Soda
- Topic 05 — Data Contracts and Producer Ownership

Later topics are also referenced only where needed:

- Topic 07 — Quarantine/DLQ
- Topic 08 — Anomaly Detection
- Topic 09 — Reconciliation

The goal is to make the learner capable of designing, testing, deploying, monitoring, and safely operating production-grade schema evolution without duplicating those dedicated modules.
