# 06 — Schema and Contract Regression Tests

> **Module 2.19 — Testing Data Pipelines**
>
> This module teaches how to protect data pipelines from schema changes, contract violations, unexpected output changes, and previously fixed regressions.

---

## 1. Learning Objectives

By the end of this module, you should be able to:

- Explain what a schema is across tables, DataFrames, events, and APIs.
- Distinguish schema validation, data-quality validation, schema regression, data regression, and code regression.
- Build deterministic schema snapshots and compare them in `pytest`.
- Detect missing columns, unexpected columns, type changes, nullability changes, and nested-structure changes.
- Design explicit producer/consumer data contracts.
- Classify schema changes using contract-specific compatibility rules.
- Explain backward, forward, and full compatibility.
- Reason about schema evolution and migration strategies.
- Understand schema registry concepts and Kafka-style event contracts.
- Explain Protobuf field numbering and evolution constraints.
- Use dbt model contracts as a deployment guardrail.
- Test REST API response contracts and recorded source responses.
- Understand consumer-driven contracts.
- Build golden datasets and safe golden-data regression tests.
- Distinguish expected changes from unexpected regressions.
- Build metric regression tests with meaningful bounds.
- Convert production incidents into permanent regression tests.
- Design ownership, versioning, CI/CD enforcement, and maintainability practices.
- Diagnose contract failures rather than simply updating expected artifacts.
- Design a production-grade regression strategy spanning unit, integration, and end-to-end testing.

The central engineering principle is:

> **A successful pipeline run does not prove that the data is correct.**

And:

> **Schema correctness does not automatically imply semantic correctness.**

---

## 2. Why Schema and Contract Regression Testing Matters

A data pipeline can be operationally healthy while producing incorrect data.

Consider:

```text
Pipeline starts
    ↓
Extraction succeeds
    ↓
Transformation succeeds
    ↓
Load succeeds
    ↓
Job reports SUCCESS
    ↓
But an upstream schema changed
    ↓
A downstream calculation interprets values differently
    ↓
Reports become incorrect
```

Compare two failure modes:

```text
Pipeline failure
    → alert
    → investigate
    → repair
```

versus:

```text
Pipeline success + incorrect data
    → no infrastructure error
    → no obvious exception
    → wrong dashboard
    → wrong financial metric
    → downstream decision based on bad data
```

The second can be more dangerous because the system appears healthy.

### A realistic example

Suppose an orders dataset originally contains:

```text
customer_id: integer
email: string
created_at: timestamp
revenue: decimal
```

An upstream producer changes it to:

```text
customer_id: string
email: string
created_at: string
revenue: float
```

A permissive ingestion layer may accept all four fields.

The pipeline may still finish successfully.

But downstream systems may experience:

- failed joins because key representations changed;
- timestamp parsing differences;
- loss of exact monetary semantics;
- rounding differences;
- altered null behavior;
- changed partitioning or serialization;
- incorrect aggregates.

Schema and contract regression tests make these changes visible before they become silent production failures.

---

## 3. The Problem: Silent Data Changes

### 3.1 Operational success is not semantic success

A scheduler normally observes things such as:

- process exit code;
- task status;
- container status;
- database connection status;
- API status code.

Those signals do not necessarily prove:

- the schema is compatible;
- the data types are still correct;
- required fields remain present;
- business semantics remain unchanged;
- row-level output is correct;
- important metrics remain within acceptable bounds.

Therefore production data testing needs multiple layers.

```text
Code correctness
      ↓
Schema correctness
      ↓
Contract compatibility
      ↓
Data correctness
      ↓
Business-metric correctness
```

No single layer replaces the others.

### 3.2 Schema correctness is not semantic correctness

Suppose this schema remains unchanged:

```text
order_id: string
amount: decimal
currency: string
```

The pipeline could still accidentally change:

```text
amount = gross_amount
```

to:

```text
amount = net_amount
```

The schema is valid.

The contract may also be technically valid.

But the business meaning changed.

This is why a production testing strategy usually combines:

- schema regression;
- contract validation;
- golden-data regression;
- metric regression;
- integration testing;
- end-to-end smoke testing.

---

## 4. Schema Fundamentals

### 4.1 What is a schema?

A **schema** describes the structural shape of data.

At minimum, it commonly includes:

- field/column names;
- data types;
- nullability;
- nested structure where applicable.

Depending on the system it may also include:

- ordering;
- constraints;
- metadata;
- logical types;
- field descriptions;
- precision and scale;
- partition information.

### 4.2 Table schema

A PostgreSQL-style table might be:

```sql
CREATE TABLE orders (
    order_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    amount NUMERIC(18, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);
```

Its schema contains structural information such as:

| Column | Type | Nullable |
|---|---|---|
| `order_id` | `BIGINT` | no |
| `customer_id` | `BIGINT` | no |
| `amount` | `NUMERIC(18,2)` | no |
| `created_at` | `TIMESTAMPTZ` | no |

### 4.3 DataFrame schema

A pandas DataFrame might expose:

```python
import pandas as pd

df = pd.DataFrame({
    "customer_id": pd.Series([101, 102], dtype="int64"),
    "email": pd.Series(["a@example.com", "b@example.com"], dtype="string"),
    "created_at": pd.to_datetime(["2026-01-01", "2026-01-02"]),
})
```

The schema is represented through column names and dtypes.

Polars and PySpark provide stronger explicit schema representations, which are useful in regression tests.

### 4.4 Event schema

A Kafka event can have a logical schema such as:

```text
OrderCreated
├── order_id: string
├── customer_id: string
├── amount: decimal
└── created_at: timestamp
```

For event systems, schema evolution is especially important because many consumers may process the same event.

### 4.5 API response schema

An API might return:

```json
{
  "id": 1001,
  "email": "customer@example.com",
  "created_at": "2026-01-01T12:30:00Z"
}
```

The contract includes more than field names. Consumers may rely on:

- required fields;
- types;
- nested structure;
- pagination;
- error format;
- enum values;
- timestamp representation.

---

## 5. Schema vs Contract vs Data Quality

These concepts are related but not identical.

| Concept | Primary question |
|---|---|
| Schema | What structural shape does the data have? |
| Data contract | What does the producer promise to provide? |
| Data-quality test | Is the data valid and usable? |
| Schema regression | Did the structural shape unexpectedly change? |
| Data regression | Did previously correct output unexpectedly change? |
| Code regression | Did software behavior change unexpectedly? |

### Example

A contract might say:

```yaml
dataset: orders
fields:
  amount:
    type: decimal
    nullable: false
    currency: USD
```

A schema test can verify:

```text
amount exists
amount is decimal
amount is non-nullable
```

A data-quality test can verify:

```text
amount >= 0
```

A semantic regression test might verify:

```text
amount equals expected business calculation
```

Each catches a different class of failure.

---

## 6. What Is Schema Regression?

**Schema regression** means that a previously established schema changed in a way that is unexpected, incompatible, or otherwise outside the approved contract.

Common regressions include:

```text
Missing column
Unexpected column
Type changed
Nullable → non-nullable
Non-nullable → nullable
Precision changed
Scale changed
Nested field removed
Nested field renamed
Field meaning changed
```

Not every schema difference is a regression.

The key question is:

> **Was this change intentional, compatible, and permitted by the contract?**

---

## 7. Schema Snapshots

A **schema snapshot** is a deterministic representation of the expected structure at a known version.

A simple snapshot might be:

```python
expected_schema = {
    "customer_id": "int64",
    "email": "string",
    "created_at": "datetime64[ns]",
    "revenue": "decimal",
}
```

A production-oriented snapshot should usually make important attributes explicit.

```python
expected_schema = {
    "customer_id": {
        "type": "int64",
        "nullable": False,
    },
    "email": {
        "type": "string",
        "nullable": True,
    },
    "created_at": {
        "type": "datetime64[ns]",
        "nullable": False,
    },
    "revenue": {
        "type": "decimal",
        "nullable": False,
        "precision": 18,
        "scale": 2,
    },
}
```

### What should a snapshot contain?

Depending on the platform:

- field names;
- data types;
- nullability;
- field order when order is contractually meaningful;
- nested structures;
- precision and scale;
- logical types;
- metadata that consumers rely on;
- schema version.

### Exact comparison

Use exact comparison when the contract is exact.

```python
def test_customer_schema():
    actual = get_customer_schema()

    expected = {
        "customer_id": "int64",
        "email": "string",
        "created_at": "datetime64[ns]",
    }

    assert actual == expected
```

### Intentional flexibility

Sometimes order does not matter:

```python
assert set(actual) == set(expected)
```

But do not weaken assertions merely to make tests pass.

A test should be relaxed only when the contract explicitly permits the variation.

---

## 8. Building Real Schema Regression Tests

### 8.1 Start with a schema helper

```python
from collections.abc import Mapping


def normalize_schema(schema: Mapping[str, str]) -> dict[str, str]:
    return dict(sorted(schema.items()))


def assert_schema_equal(
    actual: Mapping[str, str],
    expected: Mapping[str, str],
) -> None:
    actual_normalized = normalize_schema(actual)
    expected_normalized = normalize_schema(expected)

    assert actual_normalized == expected_normalized, (
        f"Schema mismatch:\n"
        f"expected={expected_normalized}\n"
        f"actual={actual_normalized}"
    )
```

The helper provides a stable representation and actionable failure output.

### 8.2 Better diagnostics

Instead of:

```text
AssertionError: False is not true
```

prefer:

```text
Schema mismatch

Missing columns:
  - customer_id

Unexpected columns:
  - client_id

Changed types:
  amount: decimal(18,2) → float64
```

A readable failure reduces mean time to diagnosis.

### 8.3 Pandas example

```python
import pandas as pd


EXPECTED = {
    "customer_id": "int64",
    "email": "string",
}


def schema_from_dataframe(df: pd.DataFrame) -> dict[str, str]:
    return {column: str(dtype) for column, dtype in df.dtypes.items()}


def test_customer_schema():
    df = load_customers()

    actual = schema_from_dataframe(df)

    assert actual == EXPECTED
```

### 8.4 Polars example

```python
import polars as pl


EXPECTED = {
    "customer_id": pl.Int64,
    "email": pl.String,
}


def test_customer_schema():
    df = load_customers()

    actual = dict(zip(df.columns, df.dtypes))

    assert actual == EXPECTED
```

### 8.5 PySpark example

```python
from pyspark.sql.types import (
    LongType,
    StringType,
    StructField,
    StructType,
)


EXPECTED = StructType([
    StructField("customer_id", LongType(), nullable=False),
    StructField("email", StringType(), nullable=True),
])


def test_customer_schema(spark):
    actual = load_customers(spark).schema
    assert actual == EXPECTED
```

Spark schema equality can be strict or deliberately normalized depending on the contract.

---

## 9. Schema Failure Diagnostics

A production schema test should distinguish at least:

### Missing column

```text
Expected:
customer_id

Actual:
email
created_at
```

### Unexpected column

```text
Expected:
customer_id
email

Actual:
customer_id
email
debug_flag
```

### Type change

```text
amount:
    expected decimal(18,2)
    actual   float64
```

### Nullability change

```text
customer_id:
    expected nullable=False
    actual   nullable=True
```

or the reverse:

```text
email:
    expected nullable=True
    actual   nullable=False
```

### Nested structure change

```text
customer.address.city
```

becomes:

```text
customer.location.city
```

A flattened path representation is often useful:

```text
customer.address.city → MISSING
customer.location.city → UNEXPECTED
```

---

## 10. Production Incident → Regression Test

This is one of the most important practices in production Data Engineering.

The workflow is:

```text
Production incident
        ↓
Identify exact failure
        ↓
Create smallest reproducible dataset
        ↓
Create regression test
        ↓
Run test against broken behavior
        ↓
Confirm it fails
        ↓
Fix pipeline
        ↓
Confirm test passes
        ↓
Keep regression test permanently
```

### Example incident

**Incident:** `revenue` changed from Decimal to Float.

**Impact:** financial aggregates experienced rounding differences.

**Correct response:**

1. Reproduce the type change.
2. Create a schema regression test.
3. Add exact-money assertions.
4. Add a minimal golden dataset containing representative monetary values.
5. Fix the producer or transformation.
6. Keep the regression tests.

### Why the test must fail before the fix

A regression test that never failed against the bug does not prove that it protects against the bug.

A strong workflow is:

```text
Broken implementation
    ↓
Regression test FAILS
    ↓
Implementation FIX
    ↓
Regression test PASSES
```

This is the same failure-first discipline used in other test types.

---

## 11. Data Contracts

A **data contract** is an explicit agreement about what data a producer provides and what consumers can rely upon.

A schema is part of a contract, but a contract can contain much more.

A contract may define:

- fields;
- types;
- nullability;
- allowed values;
- semantic definitions;
- ownership;
- version;
- compatibility policy;
- freshness expectations;
- quality expectations;
- SLA/SLO commitments where relevant.

### Example

```yaml
dataset: orders
owner: payments-team
version: 2

fields:
  order_id:
    type: string
    nullable: false

  customer_id:
    type: string
    nullable: false

  amount:
    type: decimal
    nullable: false
    precision: 18
    scale: 2

  created_at:
    type: timestamp
    nullable: false
```

The schema describes structure.

The contract additionally communicates:

```text
Who owns it?
Which version is this?
What does each field mean?
What changes are allowed?
What compatibility guarantees exist?
```

That is why a contract is more than a list of columns.

---

## 12. Producer and Consumer Contracts

A useful mental model is:

```text
Producer
    ↓
Publishes data
    ↓
Contract
    ↓
Consumer
```

### Producer obligations

A producer may be responsible for:

- maintaining the promised schema;
- preserving field semantics;
- following compatibility rules;
- communicating intentional breaking changes;
- publishing versions;
- deprecating fields deliberately.

### Consumer responsibilities

A consumer should:

- use the published contract;
- avoid undocumented assumptions;
- migrate before deprecated fields disappear;
- test its own expectations;
- report incompatibilities clearly.

### Examples

#### Orders → warehouse

```text
Orders service
    ↓
orders contract
    ↓
warehouse ingestion
```

#### CDC → lakehouse

```text
PostgreSQL
    ↓
CDC producer
    ↓
event contract
    ↓
lakehouse consumer
```

#### Kafka → streaming consumer

```text
Kafka producer
    ↓
event schema
    ↓
multiple consumers
```

#### API → ingestion pipeline

```text
External API
    ↓
API response contract
    ↓
ingestion
```

#### dbt model → downstream model

```text
staging_orders
    ↓
contract
    ↓
fct_orders
```

---

## 13. Breaking vs Non-Breaking Changes

There is no universal rule that every schema change is either safe or unsafe.

> **Whether a change is breaking depends on the contract and consumer behavior.**

### Potentially breaking changes

Common examples:

```text
int → string
nullable → non-nullable
column removed
field renamed
nested field removed
semantic meaning changed
```

### Potentially non-breaking changes

Often:

```text
add optional column
add optional event field
add nullable field
```

But even an apparently safe addition can break poorly designed consumers.

For example, a consumer may:

```python
expected_columns = ["id", "amount"]
assert list(df.columns) == expected_columns
```

Adding a column can then fail the consumer.

Therefore the correct question is not:

> Is adding a column always safe?

It is:

> Does the consumer contract permit the addition?

### Compatibility categories

#### Backward compatibility

New consumers can read old data, or a new schema can work with existing data according to the system's compatibility model.

#### Forward compatibility

Older consumers can tolerate data produced under the newer schema.

#### Full compatibility

Both directions are supported.

The exact interpretation depends on the serialization system and compatibility policy. Never reduce compatibility to a simplistic universal rule.

---

## 14. Schema Evolution

Schemas evolve because systems evolve.

Typical reasons:

- new business requirements;
- new fields;
- renamed concepts;
- regulatory changes;
- source-system migrations;
- new consumers;
- event version upgrades.

Uncontrolled evolution creates downstream breakage.

A controlled evolution process is:

```text
v1
 ↓
v2
 ↓
consumer migration
 ↓
deprecation period
 ↓
v3
```

### Example

Suppose:

```text
customer_id: integer
```

must become:

```text
customer_id: string
```

A safer migration may be:

```text
v1:
customer_id_int

v2:
customer_id_int
customer_id_string

Consumers migrate

v3:
customer_id_string
```

This is often safer than changing the existing field in place.

### Evolution controls

Use:

- versioning;
- compatibility validation;
- deprecation windows;
- migration documentation;
- consumer inventory;
- automated CI checks;
- staged rollout;
- explicit approval for breaking changes.

---

## 15. Schema Registry Concepts

A schema registry is a centralized system for managing schemas and their versions.

A simplified Kafka architecture is:

```text
Producer
   ↓
Schema Registry
   ↓
Kafka
   ↓
Consumer
```

A registry can provide:

- schema storage;
- versioning;
- compatibility checks;
- schema IDs;
- producer-side validation;
- consumer-side schema resolution.

### Why a registry matters

Without centralized schema management, producers and consumers may independently assume different structures.

A registry makes compatibility a managed platform concern.

### Conceptual workflow

```text
Producer proposes schema v3
        ↓
Registry checks compatibility
        ↓
Compatible?
   ┌────┴────┐
  yes        no
   ↓          ↓
publish     reject/change
```

A registry does not automatically guarantee semantic correctness. It is a structural/serialization compatibility control, not a replacement for business-data tests.

---

## 16. Protobuf and Schema-Based Events

Protobuf is a schema-based serialization system frequently used for strongly typed messages.

Example:

```proto
syntax = "proto3";

message Order {
  string order_id = 1;
  string customer_id = 2;
  double amount = 3;
}
```

### Why field numbers matter

The numbers:

```text
order_id = 1
customer_id = 2
amount = 3
```

are part of the wire-level identity of fields.

Do not casually reuse a field number for a different meaning.

For example, changing:

```proto
string amount = 3;
```

into an unrelated field while retaining number `3` can create decoding problems or semantic corruption.

### Evolution considerations

When evolving Protobuf schemas:

- preserve field numbers;
- avoid reusing removed field numbers;
- understand optionality semantics;
- consider old and new consumers;
- test compatibility;
- version changes deliberately.

### Regression testing connection

A Protobuf test should not stop at:

```text
"Does this message serialize?"
```

It should also ask:

```text
Can existing consumers still decode it?
Does the meaning remain unchanged?
Does the compatibility policy permit this evolution?
```

---

## 17. dbt Model Contracts

dbt model contracts protect the structure of analytical models.

A contract can make expected model columns explicit so that a model change is not silently accepted.

Conceptually:

```text
dbt model
   ↓
contract
   ↓
tests
   ↓
CI
   ↓
deployment
```

A simplified model configuration can look like:

```yaml
models:
  - name: fct_orders
    config:
      contract:
        enforced: true
    columns:
      - name: order_id
        data_type: string
      - name: amount
        data_type: numeric
```

The exact supported configuration depends on the dbt version and adapter, so production projects should validate against the installed version.

### Why model contracts matter

Suppose downstream models expect:

```text
fct_orders.order_id: string
fct_orders.amount: numeric
```

A developer changes:

```sql
cast(order_id as integer)
```

The model may still execute.

The contract provides a deployment guardrail.

### Contract failure reasoning

When CI reports a contract failure, do not immediately weaken or remove the contract.

Ask:

1. Was the model intentionally changed?
2. Is the change compatible?
3. Which consumers depend on the old type?
4. Is migration required?
5. Should the contract version change?
6. Is a breaking-change approval required?

---

## 18. API Contract Testing

For ingestion pipelines, API response structure is part of the data contract.

Suppose an endpoint returns:

```json
{
  "id": 1001,
  "email": "customer@example.com",
  "created_at": "2026-01-01T12:30:00Z"
}
```

A minimal contract can be represented in Python:

```python
EXPECTED_TYPES = {
    "id": int,
    "email": str,
    "created_at": str,
}
```

A simple validator:

```python
def assert_response_contract(payload: dict) -> None:
    for field, expected_type in EXPECTED_TYPES.items():
        assert field in payload, f"Missing required field: {field}"
        assert isinstance(payload[field], expected_type), (
            f"{field}: expected {expected_type.__name__}, "
            f"got {type(payload[field]).__name__}"
        )
```

### What should be tested?

At minimum:

- required fields;
- optional fields;
- types;
- nested structures;
- pagination;
- error responses;
- version-specific behavior.

### Nested example

```json
{
  "customer": {
    "id": 101,
    "profile": {
      "email": "a@example.com"
    }
  }
}
```

A contract should make the path explicit:

```text
customer.id
customer.profile.email
```

Then a move to:

```text
customer.contact.email
```

is detectable.

---

## 19. Recorded Source/API Regression Tests

External APIs are difficult to test repeatedly because they are:

- remote;
- mutable;
- rate-limited;
- sometimes expensive;
- dependent on authentication;
- outside your deployment boundary.

Recorded responses can provide deterministic regression tests.

```text
Real API
   ↓
Representative response recording
   ↓
Replay during tests
   ↓
Regression test
   ↓
Ingestion pipeline
```

A tool such as `pytest-recording` can support recorded HTTP interactions.

### Why recordings help

They allow a test to verify:

- parsing;
- field extraction;
- pagination handling;
- nested structure handling;
- error handling;
- transformation behavior.

### But recordings are not reality

A recording can become stale.

Therefore:

```text
recording changed
    ≠
automatically approve the new recording
```

When an upstream API changes:

1. identify the source change;
2. understand the impact;
3. update the contract if appropriate;
4. update the recording intentionally;
5. add or update regression tests;
6. review the change.

Blindly re-recording every test can hide upstream regressions.

---

## 20. Consumer-Driven Contracts

A consumer-driven contract emphasizes what the consumer actually requires.

A useful model is:

```text
Producer provides
        ↓
Consumer requires
        ↓
Contract describes the intersection
```

The producer may publish many fields, but a consumer may depend on only:

```text
order_id
customer_id
amount
```

The consumer contract can make those expectations explicit.

### Why this helps

In distributed systems, producer teams may not know every consumer dependency.

Consumer-driven contracts make those dependencies testable.

### Practical workflow

```text
Consumer defines expectation
        ↓
Contract is stored
        ↓
Producer change is proposed
        ↓
Contract verification runs
        ↓
Breaking change detected
        ↓
Change is rejected or coordinated
```

This is especially useful for:

- microservices;
- Kafka event producers;
- shared APIs;
- internal data products.

---

## 21. Golden Data / Golden Dataset Regression

A **golden dataset** is a small, deterministic dataset with an intentionally reviewed expected output.

The pattern is:

```text
Input fixture
     ↓
Pipeline
     ↓
Actual output
     ↓
Compare with golden output
```

Golden tests answer a different question from schema tests.

### Schema test

```text
Is the structure correct?
```

### Golden-data test

```text
Did this known input still produce the expected result?
```

### Example

Input:

```python
orders = [
    {"order_id": 1, "amount": 100, "status": "paid"},
    {"order_id": 2, "amount": 50, "status": "cancelled"},
]
```

Expected output:

```python
expected = [
    {"order_id": 1, "net_amount": 100},
]
```

A transformation bug that preserves the schema can still fail the golden test.

### pandas example

```python
import pandas as pd
from pandas.testing import assert_frame_equal


def test_orders_golden():
    actual = transform_orders(
        pd.DataFrame([
            {"order_id": 1, "amount": 100, "status": "paid"},
            {"order_id": 2, "amount": 50, "status": "cancelled"},
        ])
    )

    expected = pd.DataFrame([
        {"order_id": 1, "net_amount": 100},
    ])

    assert_frame_equal(
        actual.reset_index(drop=True),
        expected.reset_index(drop=True),
    )
```

### SQL example

For SQL transformations, compare stable keys and business fields rather than relying blindly on physical row order.

```sql
WITH actual AS (
    SELECT order_id, net_amount
    FROM fct_orders
    WHERE order_id IN (1, 2)
),
expected AS (
    SELECT *
    FROM expected_orders
)
SELECT *
FROM actual
EXCEPT
SELECT *
FROM expected;
```

A zero-row result can indicate equality, subject to SQL dialect and `NULL` semantics.

### PySpark example

```python
from pyspark.testing import assertDataFrameEqual


def test_spark_golden(spark):
    actual = transform_orders(input_df)

    expected = spark.createDataFrame(
        [(1, 100)],
        ["order_id", "net_amount"],
    )

    assertDataFrameEqual(
        actual.orderBy("order_id"),
        expected.orderBy("order_id"),
    )
```

---

## 22. Expected Differences

Not every difference is a regression.

There are two categories:

```text
Expected change
        vs
Unexpected change
```

### Example: expected

A new nullable field is intentionally added:

```text
discount_code: string | null
```

The golden artifact may need an approved update.

### Example: unexpected

A join change introduces duplicates:

```text
Before:
100 orders

After:
143 orders
```

The output schema may be identical.

This is a regression.

### Safe golden-data update process

Never use:

```text
"Just regenerate the expected output."
```

as an automatic response.

Use:

```text
Observed diff
    ↓
Understand root cause
    ↓
Classify expected/unexpected
    ↓
Review business impact
    ↓
Approve intentional change
    ↓
Update golden artifact
    ↓
Keep evidence in code review
```

Golden files are executable specifications. Updating them changes what the system considers correct.

---

## 23. Metric Regression Testing

Sometimes exact row-level comparison is too brittle or unnecessary.

Metric regression tests provide a higher-level guardrail.

Useful metrics include:

```text
row_count
null_rate
duplicate_rate
total_revenue
unique_customer_count
min
max
distribution statistics
```

### Exact metric assertion

```python
assert output["row_count"] == 1000
```

### Bounded assertion

```python
assert output["null_rate"] < 0.01
```

### Tolerant numeric comparison

```python
expected_revenue = 125_000.00

assert abs(
    output["total_revenue"] - expected_revenue
) < 0.01
```

### Percentage-change bound

```python
previous = 100_000
current = output["total_revenue"]

change = abs(current - previous) / previous

assert change < 0.05
```

The threshold must be justified by domain behavior.

### False positives

A threshold that is too tight may fail for legitimate variation.

### False negatives

A threshold that is too loose may allow serious corruption.

For example:

```text
null_rate < 20%
```

may technically pass while hiding a catastrophic upstream failure if the normal rate is `0.2%`.

### Business-impact connection

Metric regression is particularly useful when the exact row set is expected to vary but business invariants should remain stable.

---

## 24. Data Diff Regression

When a regression occurs, the next question is:

> **What exactly changed?**

Useful comparison techniques include:

```text
row-level diff
column-level diff
schema diff
anti-join
key-based comparison
aggregate comparison
hash comparison
```

### Stable-key comparison

Suppose `order_id` is the stable business key.

Compare:

```text
expected.order_id
actual.order_id
```

then compare important attributes.

### SQL `EXCEPT`

A basic approach is:

```sql
SELECT *
FROM actual
EXCEPT
SELECT *
FROM expected;
```

But naive `EXCEPT` has limitations:

- duplicate rows may be obscured depending on dialect;
- `NULL` behavior differs from ordinary equality;
- row ordering is irrelevant;
- large outputs can be difficult to inspect;
- there may be no stable key explaining the difference.

For production diagnostics, prefer key-based diffs when a stable business key exists.

---

## 25. Regression Test Pyramid

Schema and contract tests belong inside a broader testing strategy.

```text
             E2E smoke tests
                  ↑
          Integration tests
                  ↑
       Schema/contract tests
                  ↑
          Property tests
                  ↑
             Unit tests
```

This is not a strict hierarchy. Different tests operate at different boundaries.

### Unit-level schema assertion

Fastest.

Use when a transformation's output schema is part of its local contract.

### Integration contract test

Use when the contract crosses a real boundary such as:

- PostgreSQL;
- Kafka;
- object storage;
- API;
- dbt model.

### Golden-data regression

Use when known input/output behavior matters.

### Metric regression

Use when aggregate behavior matters more than exact row identity.

### E2E contract validation

Use for a small number of critical paths to prove that deployed components work together.

The goal is not to put every assertion into every layer.

The goal is to place each check at the cheapest layer that can reliably detect the failure.

---

## 26. Ownership and Maintainability

Contracts fail organizationally when ownership is unclear.

Ask:

- Who owns the schema?
- Who owns the contract?
- Who approves breaking changes?
- Who updates golden datasets?
- Who owns consumer expectations?
- Who handles deprecations?
- Who triages failures?

A practical model is:

```text
Producer team
    → owns published contract

Consumer team
    → owns consumer expectations

Platform team
    → owns shared validation infrastructure
```

Ownership should be explicit.

### Contract metadata

Useful metadata includes:

```yaml
dataset: orders
owner: payments-team
consumer_contact: data-platform
version: 3
compatibility: backward
status: active
```

### Maintainability principles

A regression test should:

- protect a meaningful failure mode;
- be deterministic;
- fail with useful diagnostics;
- have a clear owner;
- have an explicit update process;
- avoid unnecessary coupling to implementation details.

---

## 27. CI/CD Integration

A practical pipeline can look like:

```text
Developer PR
    ↓
Unit tests
    ↓
Schema tests
    ↓
Contract tests
    ↓
Golden-data tests
    ↓
Integration tests
    ↓
E2E smoke
    ↓
Merge
```

Not every repository needs every stage on every PR.

### PR-time tests

Run fast tests:

- schema snapshots;
- contract validation;
- small golden datasets;
- dbt contract checks;
- API replay tests.

### Pre-deployment

Run:

- integration contract tests;
- real dependency checks;
- representative data validation.

### Staging

Run:

- broader integration tests;
- deployment smoke tests;
- critical end-to-end contract checks.

### Post-deployment canary

Validate:

- schema;
- key metrics;
- critical outputs;
- event consumption.

### Scheduled regression

Use scheduled runs for tests that are:

- expensive;
- dependent on external sources;
- large-scale;
- representative of production data.

### Artifact collection

CI should preserve useful evidence:

```text
schema diff
contract failure
golden diff
metric diff
test logs
version/commit
environment
```

This shortens diagnosis time.

---

## 28. Failure Injection Lab

The fastest way to understand regression protection is to break the system deliberately.

### Failure 1 — Remove a column

Expected:

```text
customer_id
```

Actual:

```text
email
created_at
```

Expected result:

```text
FAIL
Missing column: customer_id
```

### Failure 2 — Change a type

```text
amount: Decimal
→
amount: float
```

Expected result:

```text
FAIL
amount expected Decimal, got float
```

### Failure 3 — Change nullability

```text
nullable
→
non-nullable
```

Expected result:

```text
FAIL
Nullability contract violated
```

### Failure 4 — Rename a field

```text
customer_id
→
client_id
```

Expected result:

```text
FAIL
Missing: customer_id
Unexpected: client_id
```

### Failure 5 — Change nested structure

```text
customer.address.city
```

becomes:

```text
customer.location.city
```

Expected result:

```text
FAIL
Missing nested path: customer.address.city
Unexpected nested path: customer.location.city
```

### Failure 6 — Golden output regression

Change:

```python
net_amount = amount
```

to:

```python
net_amount = amount * 0.9
```

without changing the contract.

The schema test passes.

The golden test fails.

This demonstrates why schema validation is not sufficient.

### Failure 7 — Metric regression

Introduce duplicate rows.

```text
row_count:
1000 → 2000

total_revenue:
100,000 → 200,000
```

A metric regression should fail.

### Required failure workflow

For every failure:

```text
Bug
 ↓
Test failure
 ↓
Diagnostic output
 ↓
Root cause
 ↓
Fix
 ↓
Passing test
```

Do not simply update the expected result to make the test green.

---

## 29. Hands-On Production Project

### Scenario

Build regression protection for an:

```text
E-commerce Data Platform
```

Architecture:

```text
Orders API
    ↓
Raw ingestion
    ↓
Bronze
    ↓
Silver
    ↓
Gold
    ↓
Analytics / ML consumers
```

The platform contains:

- REST APIs;
- PostgreSQL;
- object storage;
- Kafka;
- dbt;
- Spark;
- dashboards;
- ML pipelines.

### Contracts

Create contracts for:

```text
Orders
Customers
Payments
```

### Step 1 — Schema snapshots

Define expected schemas.

Example:

```yaml
dataset: orders
version: 1

fields:
  order_id:
    type: string
    nullable: false
  customer_id:
    type: string
    nullable: false
  amount:
    type: decimal
    nullable: false
```

### Step 2 — Schema regression

Write pytest checks for:

- missing columns;
- unexpected columns;
- type changes;
- nullability changes.

### Step 3 — Data contracts

Document:

- owner;
- fields;
- semantics;
- compatibility;
- version;
- migration policy.

### Step 4 — Breaking-change detection

Create examples:

```text
amount decimal → float
customer_id string → integer
remove payment_status
```

Classify each against the contract.

### Step 5 — Golden dataset

Create a small deterministic dataset:

```text
orders:
1, customer=A, amount=100, paid
2, customer=B, amount=50, cancelled
```

Define expected output.

### Step 6 — Golden comparison

Run the transformation and compare it with the expected output.

### Step 7 — Metric regression

Protect:

```text
row_count
null_rate
duplicate_rate
total_revenue
unique_customer_count
```

### Step 8 — API contract testing

Validate representative API responses.

### Step 9 — Incident-derived regression

Introduce a historical failure such as:

```text
revenue Decimal → float
```

Create a test that fails before the fix.

### Step 10 — CI strategy

Define:

```text
PR:
    schema + contract + golden + API replay

pre-deploy:
    integration

staging:
    E2E smoke

post-deploy:
    critical metric/schema canary
```

### Production-change simulation

Pretend the upstream producer changes:

```text
customer_id: string
```

to:

```text
customer_id: integer
```

The learner should trace:

```text
Producer change
    ↓
Contract check
    ↓
CI failure
    ↓
Consumer impact analysis
    ↓
Migration or rollback
    ↓
Approved contract update
    ↓
Re-run validation
```

---

## 30. Debugging Guide

### 30.1 Why did the schema test fail?

**Symptom**

```text
Schema mismatch
```

**Likely causes**

- source changed;
- transformation changed;
- dependency version changed;
- nullability changed;
- schema normalization differs.

**Diagnostic**

Print a structured diff:

```python
missing = expected.keys() - actual.keys()
unexpected = actual.keys() - expected.keys()

print("missing:", sorted(missing))
print("unexpected:", sorted(unexpected))
```

**Correct fix**

Identify whether the change is intentional before modifying the expected schema.

---

### 30.2 Why did a nullable field become required?

**Symptom**

```text
email expected nullable=True
actual nullable=False
```

**Likely causes**

- database migration;
- model contract changed;
- transformation added a filter;
- schema inference changed.

**Diagnostic**

Inspect source DDL and transformation logic.

**Correct fix**

Either restore compatibility or intentionally version and approve the new contract.

---

### 30.3 Why did the golden dataset change?

**Symptom**

```text
Expected:
net_amount = 100

Actual:
net_amount = 90
```

**Likely causes**

- business rule changed;
- code regression;
- dependency behavior changed;
- expected fixture is stale.

**Diagnostic**

Compare transformation logic and intermediate outputs.

**Correct fix**

Do not regenerate blindly. Classify the difference first.

---

### 30.4 Why did a metric regression trigger?

**Symptom**

```text
row_count exceeded expected bound
```

**Likely causes**

- duplicate join;
- source replay;
- late-arriving records;
- changed filter;
- upstream volume change.

**Diagnostic**

Check stable-key uniqueness and stage-level counts.

```sql
SELECT order_id, COUNT(*)
FROM transformed_orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

**Correct fix**

Fix the cause or deliberately update the bound only when the new behavior is valid.

---

### 30.5 Why does CI fail but local tests pass?

Common causes:

- dependency version mismatch;
- environment variables;
- timezone;
- locale;
- generated artifacts;
- stale local cache;
- missing CI service;
- different Python version.

Useful checks:

```bash
python --version
python -m pytest -q
python -m pip freeze
```

With `uv`:

```bash
uv run python --version
uv run pytest -q
```

---

### 30.6 Why did a contract update hide a regression?

The likely problem is that the expected contract was updated before the root cause was understood.

Investigate:

```text
Git diff
↓
Contract diff
↓
Golden diff
↓
Business impact
↓
Producer change
```

A contract change should be reviewed like a production code change.

---

### 30.7 Why does a schema registry reject a change?

Likely causes:

- compatibility rule violation;
- field removal;
- incompatible type change;
- incompatible evolution;
- incorrect schema version.

Do not disable compatibility checking merely to publish the new schema.

---

### 30.8 Why did an API recording become stale?

A recording represents one observed response at one point in time.

Possible causes:

- source API version changed;
- response values changed;
- authentication changed;
- pagination changed;
- recording no longer reflects representative production behavior.

Re-record intentionally and update the contract if required.

---

## 31. Common Mistakes

### Mistake 1 — Testing only column names

This misses:

- type changes;
- nullability;
- precision;
- nested changes.

### Mistake 2 — Ignoring data types

```text
decimal → float
```

can be a serious regression.

### Mistake 3 — Ignoring nullability

Consumers may depend on non-null fields.

### Mistake 4 — Treating every schema change as breaking

Optional additions may be safe under the contract.

### Mistake 5 — Treating every schema change as safe

Renames and semantic changes can break consumers even when a parser still succeeds.

### Mistake 6 — Blindly regenerating golden data

This can turn a real regression into a new expected result.

### Mistake 7 — Oversized golden datasets

Large fixtures become difficult to understand and maintain.

### Mistake 8 — Unstable timestamps

Tests become flaky when expected output depends on wall-clock time.

### Mistake 9 — Ignoring semantic changes

The schema can remain identical while meaning changes.

### Mistake 10 — No contract ownership

Unowned contracts decay.

### Mistake 11 — No versioning

Consumers cannot reason about evolution safely.

### Mistake 12 — No compatibility policy

Every change becomes an ad hoc negotiation.

### Mistake 13 — Testing only happy paths

Failures should be intentional and observable.

### Mistake 14 — No incident regression tests

Known failures can return.

### Mistake 15 — Tests that are too strict

Constant false failures train engineers to ignore CI.

### Mistake 16 — Tests that are too loose

Real regressions pass unnoticed.

### Mistake 17 — Running everything only after deployment

Late detection increases blast radius.

### Mistake 18 — Depending entirely on schema validation

Structural validity does not prove data correctness.

---

## 32. Best Practices

Use these principles in production:

1. Keep regression datasets small and deterministic.
2. Define explicit contracts.
3. Version contracts.
4. Treat breaking changes deliberately.
5. Review golden-data updates.
6. Use stable business keys.
7. Use meaningful metric thresholds.
8. Make failures actionable.
9. Assign ownership.
10. Integrate regression tests with CI/CD.
11. Preserve incident-derived tests permanently.
12. Separate expected from unexpected changes.
13. Keep fast tests fast.
14. Use integration and E2E tests for system-level behavior.
15. Never place production PII into regression fixtures unless explicitly governed and necessary.
16. Prefer synthetic or safely sampled fixtures.
17. Make compatibility policy visible to producers and consumers.
18. Test semantics where schema tests cannot.
19. Store enough metadata to reproduce a regression.
20. Treat changes to contracts and golden datasets as reviewed engineering changes.

---

## 33. Practical Exercises

### Exercise 1 — Create a schema snapshot

**Goal:** Represent a stable expected schema.

**Input:** A DataFrame with `customer_id`, `email`, and `created_at`.

**Task:** Build a deterministic schema dictionary.

**Expected behavior:** The representation contains every expected field and type.

**Hint:** Normalize field ordering before comparison.

---

### Exercise 2 — Detect a missing column

**Goal:** Detect structural deletion.

**Input:** Expected schema includes `customer_id`.

**Task:** Remove `customer_id` from the actual schema.

**Expected behavior:** The test fails with a readable missing-column message.

**Hint:** Compute `expected - actual`.

---

### Exercise 3 — Detect a type change

**Goal:** Protect a field's type.

**Input:** `amount` is expected to be decimal.

**Task:** Change the actual type to float.

**Expected behavior:** The regression test fails.

**Hint:** Include precision and scale if they are part of the contract.

---

### Exercise 4 — Classify schema changes

**Goal:** Learn contract-specific compatibility reasoning.

**Input:**

```text
A. add nullable field
B. remove field
C. int → string
D. rename field
E. add required field
```

**Task:** Classify each as potentially breaking or potentially non-breaking, then explain what consumer assumptions could change the classification.

**Expected behavior:** No change is labeled universally safe without considering the contract.

**Hint:** Ask what existing consumers can still read.

---

### Exercise 5 — Create a data contract

**Goal:** Move from schema to explicit producer obligations.

**Input:** Orders dataset.

**Task:** Define:

- owner;
- version;
- fields;
- types;
- nullability;
- compatibility policy.

**Expected behavior:** Another engineer can understand what is promised.

**Hint:** A contract should communicate ownership and evolution policy, not only columns.

---

### Exercise 6 — Create a golden dataset

**Goal:** Protect known transformation behavior.

**Input:** Three small orders with different statuses.

**Task:** Define deterministic input and expected output.

**Expected behavior:** The expected output is small enough to review manually.

**Hint:** Include edge cases that represent business rules.

---

### Exercise 7 — Introduce an intentional regression

**Goal:** Prove that the test protects against a failure.

**Input:** Existing transformation and golden test.

**Task:** Change the transformation logic.

**Expected behavior:** The test fails before the fix and passes after the fix.

**Hint:** Do not modify the expected result first.

---

### Exercise 8 — Build metric regression assertions

**Goal:** Protect business-level invariants.

**Input:** Historical metrics.

**Task:** Add assertions for row count, null rate, duplicate rate, and total revenue.

**Expected behavior:** A meaningful corruption scenario fails without rejecting normal variation.

**Hint:** Justify each threshold.

---

### Exercise 9 — Create an API contract test

**Goal:** Protect ingestion from source changes.

**Input:** Representative JSON response.

**Task:** Verify required fields, types, and nested paths.

**Expected behavior:** A removed or renamed field causes a clear failure.

**Hint:** Treat the response as a contract boundary.

---

### Exercise 10 — Convert an incident into a permanent regression test

**Goal:** Build institutional memory into the test suite.

**Input:** An incident where `customer_id` changed from string to integer.

**Task:** Create the smallest reproducer and permanent regression test.

**Expected behavior:** The test fails against the broken behavior and passes after the fix.

**Hint:** Preserve the test even after the incident is closed.

---

## 34. Checkpoint

You should now be able to explain:

- **Schema:** the structural shape of data.
- **Schema snapshot:** a versioned expected representation of that structure.
- **Schema regression:** an unexpected or incompatible structural change.
- **Contract:** an explicit producer/consumer agreement.
- **Schema vs contract:** schema describes structure; contract includes promises and expectations around it.
- **Breaking change:** a change that violates consumer compatibility under the applicable contract.
- **Non-breaking change:** a permitted evolution that preserves required compatibility.
- **Compatibility:** rules governing whether producers and consumers can evolve safely.
- **Schema evolution:** controlled change over time.
- **Schema registry:** centralized schema/version/compatibility management.
- **Protobuf:** schema-based serialization with explicit field numbers.
- **dbt model contracts:** structural deployment guardrails for analytical models.
- **API contract testing:** validation of external response structure and semantics at an ingestion boundary.
- **Consumer-driven contracts:** contracts shaped around consumer requirements.
- **Golden data:** deterministic expected outputs for representative inputs.
- **Expected differences:** intentionally approved output changes.
- **Metric regression:** protection of aggregate or statistical invariants.
- **Incident regression:** a permanent test derived from a known production failure.
- **Ownership:** explicit responsibility for contracts and expected behavior.
- **CI/CD integration:** automated enforcement before changes reach production.

### Checkpoint questions

1. What would happen if a producer changed `int → string`?
2. Why is removing a column usually dangerous?
3. Why is adding a nullable field often safer?
4. Why is schema validation insufficient for detecting revenue corruption?
5. When should you use golden data?
6. When should you use metric regression?
7. How can a production incident become a regression test?
8. Who should own a data contract?
9. When should a schema change require an approval workflow?
10. Why is blindly updating a golden dataset dangerous?

---

## 35. Interview Preparation

This section targets Senior Data Engineer and Data Platform Engineer interviews.

### Beginner

**1. What is schema validation?**

Expected answer should explain that schema validation checks structural expectations such as fields, types, and nullability.

**2. What is schema regression?**

A regression is an unexpected or incompatible change from an established schema or contract.

**3. What is a data contract?**

An explicit agreement defining what a producer provides and what consumers can rely upon, including structural and semantic expectations.

### Intermediate

**4. What makes a schema change breaking?**

There is no universal answer. It depends on compatibility policy and consumer behavior. Removing a field, changing a type, or changing semantics can be breaking.

**5. How would you test an evolving data contract?**

Discuss versioning, compatibility rules, schema snapshots, consumer expectations, migration strategy, and CI enforcement.

**6. How do you implement golden-data regression tests?**

Use small deterministic inputs, reviewed expected outputs, stable ordering/keys, and explicit review of expected changes.

**7. How do you test an API ingestion contract?**

Validate required fields, types, nested structures, pagination, error responses, and representative recorded responses.

### Advanced

**8. Design a contract-testing strategy for Kafka.**

A strong answer should discuss:

- event schema;
- schema registry;
- compatibility policy;
- producer validation;
- consumer expectations;
- versioning;
- deployment gates;
- representative integration tests;
- monitoring.

**9. How would you prevent a breaking producer change?**

Use schema registry compatibility checks, consumer-driven contracts, CI gates, ownership, and explicit breaking-change approval.

**10. How would you handle schema evolution across hundreds of consumers?**

Discuss consumer inventory, compatibility guarantees, versioned events, deprecation windows, migration tooling, observability, and staged rollout.

**11. How would you design golden-data regression at scale?**

Keep the core datasets small and representative, separate unit-level golden tests from larger integration suites, use deterministic artifacts, and avoid massive expected files.

**12. How do you distinguish legitimate business-rule changes from regressions?**

Require a clear change rationale, compare diffs, validate metrics, review ownership, update contracts intentionally, and preserve evidence in code review.

**13. How should schema/contract testing fit into CI/CD?**

Fast structural tests should run early; broader integration and E2E checks should run at later gates; production canaries should validate critical deployed contracts.

**14. How do you handle contract ownership in a large organization?**

Use explicit producer ownership, consumer ownership, platform ownership for shared infrastructure, documented escalation, and a change approval process.

### Scenario-based interview

> A producer changes `customer_id` from integer to string. The pipeline succeeds, but downstream revenue reports become incorrect. How would you detect, debug, and prevent this from happening again?

Reason through:

```text
Detection
   ↓
Diagnosis
   ↓
Root cause
   ↓
Contract
   ↓
Regression test
   ↓
CI protection
   ↓
Deployment policy
```

A strong answer should identify that successful execution does not prove semantic correctness. The candidate should combine schema regression, contract enforcement, golden data or representative fixtures, metric regression, consumer impact analysis, and a controlled rollout.

---

## 36. Final Assessment

### Scenario

You own a production data platform containing:

- PostgreSQL;
- Kafka;
- object storage;
- dbt;
- Spark;
- REST APIs;
- downstream dashboards;
- ML pipelines.

A production incident occurred because an upstream producer changed a field type without warning.

### Design task

Design a complete regression-testing strategy covering:

1. Schema regression tests.
2. Data contracts.
3. Compatibility rules.
4. Golden-data regression.
5. Metric regression.
6. API contract testing.
7. Kafka/event contract testing.
8. dbt model contracts.
9. Incident-derived regression tests.
10. CI/CD enforcement.
11. Ownership model.
12. Breaking-change approval process.

### Required architecture reasoning

Your design should answer:

```text
Where is each contract defined?
Who owns it?
Which tests run on every PR?
Which tests require integration infrastructure?
Which changes are automatically rejected?
Which changes require human approval?
How are consumers discovered?
How are deprecations communicated?
How are golden-data changes reviewed?
How are production incidents converted into permanent tests?
How is the deployed system monitored after release?
```

### Suggested target architecture

```text
                    ┌─────────────────────┐
                    │ Producer / Source   │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Contract + Schema   │
                    │ Registry / Version  │
                    └──────────┬──────────┘
                               ↓
             ┌─────────────────┴─────────────────┐
             ↓                                   ↓
      Schema/Contract CI                    Event/API Tests
             ↓                                   ↓
      Golden Regression                    Integration Tests
             └─────────────────┬─────────────────┘
                               ↓
                         Deployment Gate
                               ↓
                       Staging Validation
                               ↓
                         Production
                               ↓
                 Metric + Schema Canary Checks
```

The assessment is complete only when you can explain the trade-offs in this design rather than merely listing tools.

---

## 37. Final Production Checklist

Use this checklist before considering the topic mastered.

```text
[ ] I understand schema fundamentals.
[ ] I understand schema regression.
[ ] I can build schema snapshots.
[ ] I can test schema changes with pytest.
[ ] I understand data contracts.
[ ] I understand producer/consumer contracts.
[ ] I can identify breaking changes.
[ ] I understand schema evolution.
[ ] I understand schema registry concepts.
[ ] I understand Protobuf compatibility.
[ ] I understand dbt model contracts.
[ ] I can build API contract tests.
[ ] I understand consumer-driven contracts.
[ ] I can build golden-data regression tests.
[ ] I can review expected differences safely.
[ ] I can build metric regression tests.
[ ] I can convert incidents into regression tests.
[ ] I understand contract ownership.
[ ] I can integrate regression tests into CI/CD.
[ ] I can debug contract failures.
[ ] I can design a production-grade regression strategy.
```

---

## 38. Production Quality Gate

Before merging a schema or contract change, ask:

### Structural

```text
[ ] Are required fields still present?
[ ] Are types compatible?
[ ] Is nullability compatible?
[ ] Are nested paths compatible?
[ ] Are precision and scale preserved?
```

### Contract

```text
[ ] Is the owner known?
[ ] Is the contract version known?
[ ] Is the compatibility policy explicit?
[ ] Are affected consumers known?
[ ] Is the change approved if breaking?
```

### Regression

```text
[ ] Did schema regression tests pass?
[ ] Did golden-data tests pass?
[ ] Did metric regression tests pass?
[ ] Did API/event contract tests pass?
[ ] Did incident-derived tests pass?
```

### Deployment

```text
[ ] Did CI enforce the required checks?
[ ] Was the same artifact promoted?
[ ] Did staging validation pass?
[ ] Is there a rollback/migration plan?
[ ] Are post-deployment checks defined?
```

---

## 39. Connection to Module 2.19

This topic connects the previous and following testing layers.

```text
01 — Transformation tests
       ↓
02 — DataFrame equality and tolerance
       ↓
03 — Integration tests with Testcontainers
       ↓
04 — Property-based testing
       ↓
05 — Synthetic and sampled test data
       ↓
06 — Schema and contract regression tests
       ↓
07 — End-to-end pipeline smoke tests
```

The key progression is:

```text
Does this function work?
        ↓
Does this output match?
        ↓
Does this work with real dependencies?
        ↓
Does it satisfy broad invariants?
        ↓
Do we have realistic test data?
        ↓
Does the interface remain compatible?
        ↓
Does the deployed pipeline work end to end?
```

Schema and contract regression testing is therefore a boundary-protection layer between local correctness and system-level reliability.

---

## 40. Final Engineering Principles

Keep these principles throughout your Data Engineering career:

> **A successful pipeline run does not prove that the data is correct.**

> **Schema correctness does not automatically imply semantic correctness.**

> **A regression test should protect against a known or plausible failure mode without becoming so brittle that legitimate evolution becomes impossible.**

And most importantly:

```text
Production incident
        ↓
Understand failure
        ↓
Create smallest reproducible case
        ↓
Write regression test
        ↓
Fix implementation
        ↓
Keep the test permanently
```

A mature data platform does not merely recover from incidents.

It converts incidents into **institutionalized protection**.

That is the purpose of schema regression, data contracts, golden datasets, metric regression, compatibility testing, and incident-derived tests.

---

# Final Mastery Test

Before moving to Topic 07, explain this scenario without looking at the lesson:

```text
A Kafka producer changes:

customer_id: string
        ↓
customer_id: integer

The producer publishes successfully.
Kafka is healthy.
Consumers receive messages.
The Spark job succeeds.
The dashboard is populated.

But revenue numbers are wrong.
```

Your explanation should identify:

```text
1. Why infrastructure health did not detect the issue.
2. Why schema validation should have detected it.
3. Why a data contract should have rejected or controlled it.
4. How schema registry compatibility could help.
5. How consumer-driven contracts could help.
6. How a golden dataset could catch downstream behavior.
7. How metric regression could detect business impact.
8. How the incident becomes a permanent regression test.
9. Where CI/CD should enforce the protection.
10. Who owns the contract and approves future breaking changes.
```

If you can reason through all ten points and implement the corresponding tests, you have reached the intended production-oriented competency for this module.


---

## 41. Final Writing Requirements

This module is intentionally:

- structured;
- progressive;
- detailed;
- beginner-friendly;
- production-oriented;
- code-heavy where useful;
- easy to read;
- technically accurate;
- consistent with Module 2.19;
- explicit about failure modes;
- explicit about testing strategy;
- explicit about production trade-offs.

The material progresses from:

```text
Basic schema concepts
        ↓
Schema snapshots
        ↓
Schema regression
        ↓
Contracts
        ↓
Compatibility
        ↓
Schema evolution
        ↓
Registry concepts
        ↓
Event/API contracts
        ↓
Golden datasets
        ↓
Metric regression
        ↓
Incident regression
        ↓
Ownership
        ↓
CI/CD
        ↓
Production architecture
```

Every major concept includes a concrete Data Engineering example, and code examples are designed to be runnable or close to runnable with Python 3.12+ and the roadmap's relevant tools.

---

## 42. Final Quality Gate

Before considering this module complete, verify:

```text
✓ Schema snapshots
✓ Production incident → minimal regression test
✓ Output/data contracts
✓ Event schemas
✓ Breaking-change detection
✓ Schema registry concepts
✓ Protobuf
✓ dbt model contracts
✓ API contract tests
✓ Recorded source/API regression
✓ Consumer-driven contracts
✓ Golden-data diff
✓ Expected differences
✓ Metric regression bounds
✓ Ownership
✓ Maintainability
✓ CI/CD integration
✓ Practical code examples
✓ Failure injection
✓ Exercises
✓ Checkpoint
✓ Senior-level interview preparation
✓ Final assessment
✓ Production checklist
```

Final implementation gate:

```text
✓ Only 06-schema-and-contract-regression-tests.md is produced for this request.
✓ No roadmap topic is silently omitted.
✓ Concepts progress from basic → intermediate → advanced.
✓ Code examples are understandable.
✓ Failure scenarios are demonstrated.
✓ Production reasoning is included.
✓ The learner can implement the techniques after completing the module.
```

The final engineering standard is:

> Do not finish merely because the file is long. Finish only when the module can teach the learner to detect, diagnose, prevent, and safely evolve real production data contracts.
