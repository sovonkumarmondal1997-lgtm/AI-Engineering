# Data Quality Dimensions

> **Stage:** Stage 2 — Python for Data Engineering  
> **Module:** 2.11 — Data Validation, Contracts, and Quality  
> **Topic:** 01 — Data Quality Dimensions  
> **Level:** Beginner → Advanced / Production Data Engineering  
> **Core principle:** Data quality is not one metric. It is a set of measurable properties that determine whether data is fit for its intended use.

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

1. Define data quality precisely.
2. Explain why data quality is a production engineering concern rather than merely a cleanup task.
3. Distinguish the major data-quality dimensions:
   - accuracy,
   - completeness,
   - validity,
   - consistency,
   - uniqueness,
   - timeliness,
   - integrity,
   - freshness,
   - conformity,
   - and availability.
4. Explain why different datasets require different quality dimensions.
5. Translate vague statements such as "the data looks wrong" into measurable quality rules.
6. Distinguish data quality from data validation, data profiling, data contracts, and data observability.
7. Design measurable quality metrics and thresholds.
8. Understand hard checks versus soft checks.
9. Separate record-level quality from dataset/table-level quality.
10. Understand how quality dimensions interact and sometimes conflict.
11. Identify appropriate dimensions for APIs, event streams, relational tables, analytical models, and ML datasets.
12. Build a Python-based quality assessment without hiding failures.
13. Design severity levels and failure policies.
14. Avoid common data-quality anti-patterns.
15. Prepare a production-ready quality dimension matrix.

---

# 2. What Is Data Quality?

A useful definition is:

> **Data quality is the degree to which data possesses the characteristics required for its intended use.**

The phrase **intended use** is critical.

Consider:

```text
customer_age = 37
```

Is it high-quality data?

You cannot answer from the value alone.

If the field is:

```text
age in completed years
```

then `37` may be valid.

If the field is:

```text
age at account creation
```

then you need additional context.

If the field is:

```text
customer_birth_year
```

then `37` is probably invalid.

Therefore:

```text
quality
    =
data
+
meaning
+
constraints
+
intended use
```

Data quality is not simply:

```text
"Does this value look reasonable?"
```

It is:

```text
"Does this value satisfy the requirements of the system that consumes it?"
```

---

# 3. Why Data Quality Matters in Data Engineering

A production data pipeline can successfully execute while producing unusable data.

For example:

```text
API request
   ↓
HTTP 200
   ↓
JSON parsed
   ↓
DataFrame created
   ↓
Parquet written
   ↓
Database loaded
```

Every technical operation succeeded.

But suppose:

```text
20% of customer IDs are null
15% of events are duplicated
8% of timestamps are in the future
12% of records are stale
```

The pipeline is technically successful but operationally incorrect.

This distinction is fundamental:

> **Pipeline success is not the same thing as data success.**

---

# 4. Data Quality as a Layered System

A production-quality pipeline should think in layers:

```text
Source
  ↓
Ingestion
  ↓
Schema
  ↓
Record validation
  ↓
Dataset validation
  ↓
Business-rule validation
  ↓
Quality metrics
  ↓
Quality decision
  ↓
Durable output
```

A later topic in this module will cover validation mechanisms in detail.

This chapter establishes the vocabulary needed to design those mechanisms correctly.

---

# 5. The Major Data Quality Dimensions

The most useful dimensions are:

| Dimension | Core Question |
|---|---|
| Accuracy | Does the data represent reality correctly? |
| Completeness | Is required information present? |
| Validity | Does the data conform to defined rules? |
| Consistency | Does the same information agree across records/systems? |
| Uniqueness | Are entities/events duplicated when they should not be? |
| Timeliness | Is the data available when it is needed? |
| Freshness | How recently has the data been updated? |
| Integrity | Are relationships and structural constraints preserved? |
| Conformity | Does the data follow required formats, standards, and conventions? |
| Availability | Is the expected data actually accessible to consumers? |

These dimensions overlap.

That is normal.

The goal is not to force every quality problem into exactly one category.

The goal is to make the quality requirement measurable.

---

# 6. Accuracy

## 6.1 Definition

**Accuracy** asks:

> Does the value correctly represent the real-world entity, event, or fact it is supposed to represent?

Example:

```text
customer_id = C123
customer_name = "Sovon"
```

If the actual customer associated with `C123` is someone else, the value is inaccurate even if:

- the type is correct,
- the string is non-empty,
- the schema is valid.

---

## 6.2 Accuracy Requires a Reference

Accuracy is often harder to test than validity.

For example:

```text
age = 35
```

You can test:

```text
age is integer
age >= 0
age <= 120
```

Those are validity checks.

But how do you prove:

```text
age == actual_customer_age
```

?

You need a trusted reference.

Possible reference sources include:

- source-of-record systems,
- authoritative master data,
- verified transactions,
- external reference datasets,
- manually verified records.

---

## 6.3 Validity vs Accuracy

Consider:

```text
email = "alice@example.com"
```

The value may be structurally valid.

But if Alice's real email is:

```text
alice@company.com
```

then the first value may be valid according to the syntax but inaccurate.

Therefore:

```text
valid
≠
accurate
```

---

## 6.4 Accuracy Metrics

Possible metrics:

```text
accurate_records / reference_checked_records
```

Example:

```text
98,500 / 100,000 = 98.5%
```

Accuracy can also be measured through:

- error rate,
- reconciliation difference,
- reference-match rate,
- manually verified sample accuracy.

---

## 6.5 Accuracy Is Often Expensive

You cannot always verify every record against an authoritative source.

Therefore production systems may use:

- sampling,
- reconciliation,
- reference joins,
- anomaly detection,
- source-system controls.

---

# 7. Completeness

## 7.1 Definition

**Completeness** asks:

> Is all required information present?

Examples:

```text
customer_id IS NOT NULL
order_id IS NOT NULL
event_time IS NOT NULL
```

---

## 7.2 Column Completeness

Suppose:

```text
customer_id
C001
C002
NULL
C004
```

There are 3 non-null values out of 4.

Completeness:

```text
3 / 4 = 75%
```

---

## 7.3 Dataset Completeness

Completeness can also mean whether the expected set of records arrived.

Suppose the source reports:

```text
expected records = 1,000,000
received records = 990,000
```

Then arrival completeness is:

```text
990,000 / 1,000,000
= 99%
```

This is different from null completeness.

---

## 7.4 Time-Window Completeness

Suppose an event pipeline should contain one record per minute.

Expected:

```text
09:00
09:01
09:02
...
09:59
```

If `09:31` is missing, the dataset may be incomplete even if every present row has all required columns populated.

---

## 7.5 Completeness Types

It is useful to distinguish:

```text
Field completeness
Record completeness
Partition completeness
Time-window completeness
Dataset completeness
Source completeness
```

---

# 8. Validity

## 8.1 Definition

**Validity** asks:

> Does a value conform to the allowed rules for its type, domain, format, range, or structure?

Examples:

```text
age >= 0
country_code ∈ allowed_country_codes
status ∈ {"pending", "active", "cancelled"}
email matches required format
event_time is a valid timestamp
```

---

## 8.2 Examples

Invalid:

```text
age = -5
```

Invalid:

```text
status = "banana"
```

Invalid:

```text
currency = "XYZ"
```

if `XYZ` is not an allowed currency code for the application.

---

## 8.3 Validity Is Not Accuracy

This distinction should become automatic:

```text
Validity:
Does the value follow the rules?

Accuracy:
Does the value represent reality?
```

Example:

```text
date_of_birth = 2000-01-01
```

It can be:

```text
valid = yes
accurate = unknown
```

---

# 9. Consistency

## 9.1 Definition

**Consistency** asks:

> Does the same concept agree across records, tables, systems, or time?

Example:

```text
customer table:
customer_id = 100
country = "IN"

order table:
customer_id = 100
country = "US"
```

The values conflict.

---

## 9.2 Internal Consistency

Within one record:

```text
start_time <= end_time
```

If:

```text
start_time = 10:00
end_time = 09:00
```

the record is internally inconsistent.

---

## 9.3 Cross-Table Consistency

Example:

```text
orders.customer_id
```

should agree with:

```text
customers.customer_id
```

---

## 9.4 Cross-System Consistency

Suppose:

```text
CRM:
customer_status = active

Billing:
customer_status = cancelled
```

The values may be inconsistent.

However, do not automatically label the situation as an error.

The systems may intentionally operate at different update times.

This is why **timeliness** and **consistency** must sometimes be analyzed together.

---

# 10. Uniqueness

## 10.1 Definition

**Uniqueness** asks:

> Are values that are supposed to identify one entity or event duplicated?

For a primary key:

```text
customer_id
```

you may require:

```text
count(customer_id) == count(distinct customer_id)
```

---

## 10.2 Duplicate Records

Consider:

```text
order_id | amount
---------|-------
1001     | 50
1002     | 80
1002     | 80
```

If each `order_id` should occur once, the third row is a duplicate.

---

## 10.3 Duplicate Events

Event data can intentionally contain repeated events.

For example, retries can cause:

```text
event_id = E100
event_id = E100
```

Therefore:

> Duplicate does not automatically mean incorrect.

You must know the data model.

---

## 10.4 Idempotency and Uniqueness

In ingestion systems, uniqueness often interacts with idempotency.

A pipeline may receive:

```text
same event
```

multiple times.

A quality-aware system may enforce:

```text
event_id unique
```

or use:

```text
event_id + source_partition + sequence
```

depending on the source semantics.

---

# 11. Timeliness

## 11.1 Definition

**Timeliness** asks:

> Is the data available at the time it is needed?

Suppose a dashboard is required by:

```text
08:00
```

but the data arrives at:

```text
11:00
```

The records may be accurate and complete.

They are still not timely for the dashboard's intended use.

---

## 11.2 Timeliness vs Freshness

These terms are related but not identical.

### Freshness

How recently the data was updated.

### Timeliness

Whether data arrived within the required time window for its use.

Example:

```text
Data updated 5 minutes ago.
```

Freshness:

```text
5 minutes old
```

But if the report had to be ready at 08:00 and it is now 09:30:

```text
timeliness = failed
```

---

# 12. Freshness

## 12.1 Definition

**Freshness** measures how old the latest available data is.

A common conceptual metric is:

```text
freshness = current_time - latest_data_timestamp
```

Example:

```text
current time = 10:00
latest record = 09:45
```

Freshness:

```text
15 minutes
```

---

## 12.2 Freshness Threshold

A pipeline might require:

```text
freshness <= 30 minutes
```

Then:

```text
15 minutes → pass
45 minutes → fail
```

---

## 12.3 Freshness Is Context-Dependent

A daily finance report might tolerate:

```text
24 hours
```

A fraud detection system might require:

```text
seconds
```

Therefore:

```text
freshness requirement
=
consumer requirement
```

---

# 13. Integrity

## 13.1 Definition

**Integrity** asks:

> Are the structural and relational relationships between data elements preserved?

Examples:

- foreign keys,
- parent-child relationships,
- referential integrity,
- valid entity relationships.

---

## 13.2 Referential Integrity

Suppose:

```text
orders.customer_id
```

references:

```text
customers.customer_id
```

An order with:

```text
customer_id = C999
```

is problematic if `C999` does not exist in the customer table.

This is a referential-integrity failure.

---

## 13.3 Orphan Records

An orphan is a child record without a valid parent.

Example:

```text
customers:
C001
C002

orders:
C001
C003
```

`C003` is an orphan customer reference.

---

## 13.4 Integrity Is More Than Foreign Keys

It can also include:

```text
parent-child relationships
event sequences
partition relationships
aggregation relationships
transaction boundaries
```

---

# 14. Conformity

## 14.1 Definition

**Conformity** asks:

> Does the data follow the required standards, conventions, and representations?

Examples:

```text
ISO country codes
ISO timestamps
standard currency codes
canonical units
approved naming conventions
expected casing
standardized categories
```

---

## 14.2 Example

Suppose a system requires:

```text
country_code = ISO 3166-1 alpha-2
```

Then:

```text
IN
US
GB
```

may conform.

But:

```text
India
United States
UK
```

may not conform to the required representation.

The information may still be semantically understandable.

Conformity concerns whether it follows the specified standard.

---

# 15. Availability

## 15.1 Definition

**Availability** asks:

> Is the expected data accessible to its consumers when required?

Examples:

- table exists,
- partition exists,
- object is readable,
- API response is available,
- dataset is not accidentally deleted,
- required partition has arrived.

Availability is closely related to pipeline reliability but can be treated as a data-quality dimension when the data product itself must be accessible.

---

# 16. Quality Dimensions Are Not Independent

A single incident can violate multiple dimensions.

Suppose an API stops sending one field.

```text
customer_email
```

The result may have:

```text
Completeness → failed
Validity → potentially unaffected
Accuracy → unknown
Conformity → potentially unaffected
```

Now suppose the API sends malformed email values:

```text
alice@@example
```

Then:

```text
Validity → failed
Completeness → passed
```

If the email belongs to another customer:

```text
Accuracy → failed
Validity → passed
```

This is why quality dimensions must be measured separately.

---

# 17. A Quality Dimension Does Not Automatically Define Failure

Consider:

```text
null_rate(customer_phone) = 20%
```

Is that a failure?

Not necessarily.

If phone number is optional:

```text
20% null
→ potentially acceptable
```

If phone number is mandatory:

```text
20% null
→ quality failure
```

The metric alone is not the policy.

You need:

```text
dimension
+
measurement
+
expected behavior
+
threshold
+
severity
+
action
```

---

# 18. From Dimension to Rule

A vague requirement:

> "Customer IDs should be complete."

Becomes:

```text
dimension = completeness
column = customer_id
metric = null_rate
threshold = 0%
severity = critical
action = reject batch
```

Another requirement:

> "Order timestamps should be recent."

Becomes:

```text
dimension = freshness
metric = current_time - max(order_timestamp)
threshold = <= 15 minutes
severity = high
action = alert + investigate
```

This transformation is one of the core skills of production data quality engineering.

---

# 19. Hard Checks vs Soft Checks

## 19.1 Hard Check

A hard check blocks the pipeline or quarantines data when the rule fails.

Example:

```text
primary key must not be null
```

Possible policy:

```text
failure → reject
```

---

## 19.2 Soft Check

A soft check records or alerts on a quality issue without necessarily blocking the pipeline.

Example:

```text
optional phone number null rate < 30%
```

Possible policy:

```text
failure → warn
```

---

## 19.3 Why Not Make Everything Hard?

If every anomaly blocks production:

```text
pipeline availability ↓
operational noise ↑
manual intervention ↑
```

Some dimensions should be monitored rather than treated as fatal.

---

# 20. Severity Levels

A practical classification can be:

```text
CRITICAL
HIGH
MEDIUM
LOW
INFO
```

Example:

### CRITICAL

```text
primary key missing
schema incompatible
required partition missing
```

### HIGH

```text
freshness exceeds SLA
large completeness drop
major referential-integrity failure
```

### MEDIUM

```text
moderate optional-field degradation
```

### LOW

```text
minor formatting drift
```

These labels are organizational policies, not universal standards.

---

# 21. Data Quality Dimensions vs Data Validation

These concepts should not be confused.

## Data Quality Dimensions

Describe **what property** you care about.

Examples:

```text
completeness
accuracy
validity
uniqueness
```

## Data Validation

Describes **how you test** the data.

Examples:

```python
assert customer_id.notna().all()
```

or a framework-based validation rule.

Therefore:

```text
Dimension = WHAT
Validation = HOW
```

---

# 22. Data Quality vs Data Profiling

## Profiling

Profiling asks:

> What does the data currently look like?

Examples:

```text
null percentage
distinct count
min
max
mean
distribution
duplicate rate
```

## Quality

Quality asks:

> Does the observed data meet the expected requirements?

Example:

```text
observed null rate = 4.2%

required null rate <= 1%

→ quality failure
```

Therefore:

```text
Profiling
    ↓
measurement

Quality assessment
    ↓
measurement + expectation
```

---

# 23. Data Quality vs Data Contracts

A data contract defines expectations between producers and consumers.

For example:

```text
producer:
orders-service

consumer:
analytics-platform

contract:
order_id → required
customer_id → required
order_total → decimal >= 0
currency → ISO code
event_time → UTC timestamp
```

Quality checks can enforce contract expectations.

Therefore:

```text
Data contract
    ↓
declared expectations

Data validation
    ↓
enforcement

Data quality metrics
    ↓
measurement

Data observability
    ↓
monitoring over time
```

---

# 24. Record-Level vs Dataset-Level Quality

This distinction is important.

## Record-Level

Checks one row:

```text
age >= 0
email valid
order_total >= 0
```

## Dataset-Level

Checks the collection:

```text
row count
duplicate rate
freshness
distribution
partition completeness
```

## Cross-Dataset

Checks relationships:

```text
orders.customer_id exists in customers.customer_id
```

Production systems usually need all three.

---

# 25. A Practical Quality Taxonomy

A useful taxonomy is:

```text
Level 1 — Field
    type
    nullability
    format
    range

Level 2 — Record
    cross-field relationships
    business rules

Level 3 — Dataset
    row count
    duplicates
    distributions
    freshness

Level 4 — Cross-dataset
    referential integrity
    reconciliation

Level 5 — Cross-system
    source-to-target consistency
    delivery completeness
```

This prevents a common mistake:

> Assuming that checking individual fields is sufficient to establish data quality.

---

# 26. Example: E-Commerce Orders

Suppose the `orders` table contains:

```text
order_id
customer_id
order_time
status
currency
amount
```

Define quality dimensions.

### Accuracy

```text
amount should match the authoritative order total
```

### Completeness

```text
order_id NOT NULL
customer_id NOT NULL
order_time NOT NULL
```

### Validity

```text
amount >= 0
status ∈ allowed statuses
currency ∈ supported currencies
```

### Uniqueness

```text
order_id unique
```

### Consistency

```text
order_time <= shipped_time
```

### Integrity

```text
customer_id exists in customer dimension
```

### Freshness

```text
latest order_time not older than expected
```

### Timeliness

```text
orders arrive within 10 minutes of source creation
```

### Conformity

```text
timestamps represented in UTC
currency follows ISO standard
```

---

# 27. Example: Clickstream Events

Suppose an event contains:

```text
event_id
user_id
event_name
event_time
page_url
device_type
```

Possible quality requirements:

```text
event_id not null
event_id unique
event_name in approved taxonomy
event_time valid
event_time not excessively future-dated
user_id valid when required
page_url conforms to expected URL rules
device_type in approved domain
events arrive within expected delay
```

Notice that event systems often care strongly about:

- uniqueness,
- timeliness,
- freshness,
- validity,
- ordering,
- and completeness.

---

# 28. Example: ML Training Data

ML datasets have additional concerns.

Possible dimensions:

```text
label completeness
label validity
feature completeness
feature distribution
duplicate rate
temporal consistency
target leakage
schema conformity
```

A dataset can pass traditional schema checks and still be unsuitable for training.

For example:

```text
label = valid integer
```

does not prove:

```text
label = correct
```

or:

```text
feature distribution = representative
```

---

# 29. Example: Financial Data

Financial data often requires strong:

- accuracy,
- completeness,
- integrity,
- consistency,
- timeliness,
- reconciliation.

For example:

```text
sum(transaction_amount)
```

may need to reconcile with:

```text
source_system_total
```

This introduces a powerful quality pattern:

> **Reconciliation is an accuracy/integrity technique for comparing independent representations of the same quantity.**

---

# 30. Quality Metrics

A quality dimension becomes operationally useful when it can be measured.

Common metrics:

```text
null_rate
invalid_rate
duplicate_rate
referential_integrity_failure_rate
freshness_age
delivery_lag
row_count
expected_row_count_ratio
reconciliation_difference
schema_violation_count
```

---

## 30.1 Null Rate

```text
null_rate =
null_values / total_values
```

---

## 30.2 Invalid Rate

```text
invalid_rate =
invalid_values / values_checked
```

---

## 30.3 Duplicate Rate

One definition:

```text
duplicate_rate =
duplicate_rows / total_rows
```

But always define exactly what constitutes a duplicate.

---

## 30.4 Completeness Ratio

```text
completeness =
non_null_required_values / required_values
```

---

## 30.5 Freshness

```text
freshness_age =
current_time - max(data_timestamp)
```

---

## 30.6 Reconciliation Difference

```text
difference =
source_total - target_total
```

For monetary values, define acceptable tolerance carefully.

---

# 31. Thresholds

Metrics become useful when paired with thresholds.

Example:

```text
customer_id completeness >= 99.99%
```

or:

```text
duplicate_rate <= 0.1%
```

or:

```text
freshness_age <= 15 minutes
```

But thresholds should be based on:

- business requirements,
- historical behavior,
- source capabilities,
- downstream tolerance,
- risk.

Do not choose thresholds merely because they are round numbers.

---

# 32. Absolute vs Relative Thresholds

## Absolute

```text
invalid_count <= 100
```

## Relative

```text
invalid_rate <= 0.1%
```

These behave differently as volume changes.

At:

```text
1,000 records
```

100 invalid records = 10%.

At:

```text
1,000,000 records
```

100 invalid records = 0.01%.

Therefore, the threshold must match the business meaning.

---

# 33. Static vs Dynamic Thresholds

## Static

```text
null_rate <= 1%
```

## Dynamic

Compare today's metric against historical behavior:

```text
today <= historical_mean + 3σ
```

Dynamic thresholds can detect unexpected changes.

However, they require:

- historical data,
- stable enough distributions,
- careful handling of seasonality,
- protection against alert fatigue.

---

# 34. Quality Dimensions and SLAs

A production data product may define:

```text
Completeness SLA:
>= 99.9%

Freshness SLA:
<= 15 minutes

Uniqueness:
100% for order_id

Validity:
>= 99.99%

Availability:
>= 99.9%
```

This turns quality into an operational contract.

---

# 35. Quality Is Consumer-Dependent

The same data may be acceptable for one consumer and unacceptable for another.

Example:

```text
Customer phone null rate = 10%
```

For:

```text
analytics segmentation
```

this may be acceptable.

For:

```text
SMS notification system
```

it may be unacceptable.

Therefore:

> **Data quality should be evaluated against the requirements of the data product and its consumers.**

---

# 36. Quality Dimension Interaction Example

Suppose today's order count is:

```text
1,000,000
```

Yesterday:

```text
1,050,000
```

Today is down by:

```text
50,000
```

Potential interpretations:

```text
completeness problem
source outage
business volume change
late-arriving data
duplicate reduction
partition failure
```

Row count alone cannot identify the root cause.

This is why quality dimensions should be evaluated together.

---

# 37. A Python Quality Assessment Example

The following example demonstrates basic metric computation.

```python
from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class QualityMetric:
    name: str
    value: float
    threshold: float
    passed: bool


def completeness_rate(series: pd.Series) -> float:
    if len(series) == 0:
        return 1.0

    return float(series.notna().mean())


def uniqueness_rate(series: pd.Series) -> float:
    if len(series) == 0:
        return 1.0

    return float(series.nunique(dropna=False) / len(series))


def quality_metrics(df: pd.DataFrame) -> list[QualityMetric]:
    customer_id_completeness = completeness_rate(df["customer_id"])

    order_id_uniqueness = uniqueness_rate(df["order_id"])

    return [
        QualityMetric(
            name="customer_id_completeness",
            value=customer_id_completeness,
            threshold=0.999,
            passed=customer_id_completeness >= 0.999,
        ),
        QualityMetric(
            name="order_id_uniqueness",
            value=order_id_uniqueness,
            threshold=1.0,
            passed=order_id_uniqueness >= 1.0,
        ),
    ]
```

This is intentionally simple.

A production implementation should also define:

- empty dataset behavior,
- metric semantics,
- null treatment,
- duplicate semantics,
- severity,
- error handling,
- logging,
- persistence,
- alerting.

---

# 38. Example Dataset

```python
import pandas as pd


orders = pd.DataFrame(
    {
        "order_id": [1, 2, 2, 4],
        "customer_id": ["C1", "C2", None, "C4"],
        "amount": [100.0, 200.0, -50.0, 400.0],
        "status": ["paid", "paid", "paid", "unknown"],
    }
)
```

Potential findings:

```text
order_id:
    duplicate

customer_id:
    missing value

amount:
    negative value

status:
    invalid category
```

One dataset therefore has multiple simultaneous quality failures.

---

# 39. Turning Findings Into a Quality Report

A useful report can look like:

```text
Dataset: orders
Rows: 4

Completeness
    customer_id: 75%
    FAIL

Uniqueness
    order_id: 75%
    FAIL

Validity
    amount >= 0: FAIL
    status domain: FAIL

Overall status:
    FAIL
```

The report should preserve the evidence.

Avoid reporting only:

```text
"Data quality failed."
```

That statement is not actionable.

---

# 40. Quality Status Should Be Explainable

A good quality result should answer:

```text
What failed?
Where?
How many records?
What percentage?
What threshold?
What severity?
What action?
```

Example:

```text
Rule:
customer_id completeness

Observed:
98.4%

Required:
>= 99.9%

Affected:
16,000 / 1,000,000 records

Severity:
HIGH

Action:
quarantine affected batch and alert owner
```

---

# 41. Common Anti-Patterns

## 41.1 "No Nulls Means Good Data"

False.

A dataset can contain:

- inaccurate values,
- duplicates,
- stale records,
- invalid categories,
- broken relationships.

---

## 41.2 "Schema Validation Is Data Quality"

False.

A value can satisfy the schema and still be wrong.

Example:

```text
amount: float
value: 999999999999
```

The type is valid.

The business meaning may not be.

---

## 41.3 "More Checks Always Means Better Quality"

Not necessarily.

Too many low-value checks can create:

- alert fatigue,
- operational noise,
- false positives,
- slower pipelines.

Checks should correspond to meaningful requirements.

---

## 41.4 "Every Quality Failure Should Block the Pipeline"

False.

Some failures should:

```text
reject
quarantine
warn
monitor
```

depending on severity and consumer impact.

---

## 41.5 "One Threshold Works Forever"

False.

Data volume and business behavior change.

Thresholds should be reviewed using historical evidence.

---

## 41.6 "Accuracy Can Always Be Tested Automatically"

False.

Accuracy often requires a trusted reference.

---

## 41.7 "Duplicate Always Means Bad Data"

False.

Duplicate events may be expected in at-least-once delivery systems.

The data model defines uniqueness requirements.

---

## 41.8 "Freshness and Timeliness Are the Same"

They are related but distinct.

Freshness describes age.

Timeliness describes suitability relative to a required delivery/use time.

---

## 41.9 "A Passing Pipeline Means Passing Data"

False.

Technical pipeline health and data quality are separate dimensions.

---

# 42. Production Quality Dimension Matrix

Use a matrix like this when designing a dataset.

| Dimension | Question | Metric | Example Threshold | Typical Action |
|---|---|---|---|---|
| Accuracy | Does data represent reality? | reference-match rate | >= 99.9% | investigate/reconcile |
| Completeness | Is required data present? | non-null rate | >= 99.9% | reject/quarantine |
| Validity | Does data satisfy rules? | valid-rate | >= 99.9% | reject/quarantine |
| Consistency | Do representations agree? | consistency rate | >= 99.9% | investigate |
| Uniqueness | Are identifiers/events duplicated? | duplicate rate | <= 0.1% | deduplicate/reject |
| Timeliness | Did data arrive when required? | delivery lag | <= SLA | alert |
| Freshness | How old is current data? | freshness age | <= SLA | alert |
| Integrity | Are relationships preserved? | orphan rate | 0% | reject/quarantine |
| Conformity | Does data follow standards? | conformity rate | >= 99.9% | normalize/reject |
| Availability | Is required data accessible? | availability | >= SLA | incident |

These values are examples only. Production thresholds must come from actual requirements.

---

# 43. Designing Dimensions for a Dataset

Use this workflow:

```text
1. Identify consumers.
2. Identify critical fields.
3. Identify business invariants.
4. Identify source guarantees.
5. Identify downstream requirements.
6. Select relevant quality dimensions.
7. Define metrics.
8. Define thresholds.
9. Define severity.
10. Define action.
11. Establish ownership.
12. Measure over time.
```

---

# 44. Quality Ownership

Every important quality rule should have an owner.

Possible ownership:

```text
producer team
data platform team
analytics engineering
data governance
consumer team
```

For example:

```text
customer_id validity
→ source application team

pipeline freshness
→ data platform team

business metric reconciliation
→ analytics/data product owner
```

Ownership prevents:

```text
quality failure
→ everyone sees it
→ nobody owns it
```

---

# 45. Quality as a Contract

A mature data product can express:

```text
Field:
customer_id

Required:
yes

Type:
string

Validity:
matches customer ID format

Uniqueness:
not required globally

Completeness:
>= 99.99%

Integrity:
must exist in customer dimension

Owner:
customer platform

Severity:
critical
```

This is much more actionable than:

```text
"customer_id should be good."
```

---

# 46. Quality Gates

A pipeline can establish quality gates:

```text
raw ingestion
    ↓
basic schema gate
    ↓
record validation
    ↓
dataset quality gate
    ↓
business-rule gate
    ↓
publish
```

Example:

```text
Schema incompatible
→ stop

Required key missing
→ quarantine

Optional field degradation
→ warn

Freshness slightly degraded
→ alert

Critical reconciliation failure
→ stop publication
```

---

# 47. Quality and Data Contracts

A producer-owned contract can specify:

```text
schema
required fields
allowed values
semantics
delivery SLA
quality guarantees
change policy
```

This changes the quality model from:

```text
consumer discovers problems later
```

to:

```text
producer declares expectations
        ↓
consumer knows expectations
        ↓
pipeline validates
        ↓
violations are visible
```

Later topics in this module will build on this model.

---

# 48. Quality and Observability

Data observability asks questions such as:

```text
Did row count change?
Did freshness change?
Did null rate change?
Did schema change?
Did distributions change?
```

A mature system tracks quality metrics over time.

For example:

```text
customer_id completeness

100% ────────────────┐
 99%                 │
 98%                 └──────
                     ↑
                  incident
```

The trend can be more informative than a single measurement.

---

# 49. Quality Incidents

A quality incident should be treated like an operational incident.

Useful information:

```text
start time
affected dataset
affected partitions
failed dimensions
observed metric
expected metric
consumer impact
root cause
mitigation
permanent fix
```

This encourages systematic improvement.

---

# 50. Exercises

## Exercise 1 — Classify the Problem

Classify each issue:

1. `customer_id IS NULL`
2. `status = "banana"`
3. duplicate `order_id`
4. API data is 3 hours old
5. `orders.customer_id` does not exist in customers
6. amount differs from the authoritative billing system
7. timestamp format violates the standard
8. dashboard dataset arrived after the reporting deadline

### Expected dimensions

Think in terms of:

```text
completeness
validity
uniqueness
freshness
integrity
accuracy
conformity
timeliness
```

---

## Exercise 2 — Design Rules

For this table:

```text
users(
    user_id,
    email,
    country,
    signup_time,
    status
)
```

Design at least:

- 2 completeness rules,
- 2 validity rules,
- 1 uniqueness rule,
- 1 conformity rule,
- 1 freshness/timeliness rule,
- 1 consistency rule.

---

## Exercise 3 — Threshold Design

A dataset has:

```text
10,000,000 rows
```

The business says:

> At most 0.01% of records may have invalid country codes.

Calculate the maximum allowed invalid records.

Do not simply state the percentage; convert the requirement into an operational count.

---

## Exercise 4 — Consumer-Specific Quality

Suppose:

```text
phone_number null rate = 15%
```

Determine whether that is necessarily a quality failure for:

1. analytics dashboard,
2. SMS notification system,
3. fraud investigation dataset.

Explain the reasoning.

---

## Exercise 5 — Freshness vs Timeliness

A dataset's latest record is:

```text
09:55
```

Current time:

```text
10:00
```

The report deadline is:

```text
09:30
```

Answer:

- Is the data fresh?
- Is the data timely?

Explain the distinction.

---

## Exercise 6 — Duplicate Semantics

A clickstream source retries delivery and can send the same event twice.

Should duplicate `event_id` values automatically cause a pipeline failure?

Explain the answer using:

- delivery semantics,
- idempotency,
- deduplication,
- business requirements.

---

## Exercise 7 — Accuracy vs Validity

A customer's date of birth is:

```text
2000-01-01
```

The value is syntactically valid.

The source-of-record says:

```text
2001-01-01
```

Which dimension failed?

Why is the original value still valid?

---

## Exercise 8 — Cross-Dataset Integrity

You have:

```text
customers = 1,000,000 rows
orders = 8,000,000 rows
```

There are 4,000 orders whose `customer_id` does not exist.

Calculate the orphan rate.

Then decide whether the result should automatically block publication or merely trigger an alert. Justify the policy.

---

# 51. Advanced Exercises

## Exercise 9 — Build a Quality Scorecard

For an orders dataset, define:

```text
10 quality rules
10 metrics
10 thresholds
10 severities
10 actions
```

Do not use arbitrary thresholds. State the business assumption behind each.

---

## Exercise 10 — Quality Dimension Interaction

A daily dataset has:

```text
row count: -20%
null rate: +5 percentage points
freshness: +45 minutes
duplicate rate: unchanged
```

Design an investigation sequence.

Do not assume the root cause.

---

## Exercise 11 — Design a Producer Contract

Create a contract for:

```text
orders
```

Include:

- schema,
- nullability,
- allowed values,
- uniqueness,
- freshness,
- timeliness,
- integrity,
- change expectations,
- quality thresholds.

---

## Exercise 12 — Quality Failure Policy

For each failure, choose:

```text
reject
quarantine
warn
monitor
```

and justify:

1. primary key missing,
2. optional phone field 5% null,
3. freshness 10 minutes beyond SLA,
4. 50 duplicate events in 10 million,
5. 30% invalid currency values.

---

# 52. Interview Questions

## Basic

1. What is data quality?
2. What are the major data-quality dimensions?
3. What is completeness?
4. What is validity?
5. What is accuracy?
6. What is uniqueness?
7. What is freshness?
8. What is timeliness?
9. What is referential integrity?
10. What is conformity?

---

## Moderate

1. What is the difference between accuracy and validity?
2. What is the difference between freshness and timeliness?
3. How do you measure completeness?
4. How do you measure duplicate rate?
5. Why can valid data still be inaccurate?
6. Why can duplicate records be legitimate?
7. What is the difference between profiling and validation?
8. What is a hard quality check?
9. What is a soft quality check?
10. Why should thresholds be tied to consumer requirements?

---

## Hard

1. How would you design quality checks for a clickstream pipeline?
2. How would you distinguish source failure from a genuine business-volume drop?
3. How would you measure accuracy when no authoritative reference exists?
4. How would you design a reconciliation check?
5. How would you choose between absolute and relative thresholds?
6. How do quality dimensions interact?
7. How would you prevent alert fatigue?
8. How would you decide which quality failures block publication?
9. How would you assign ownership for a quality rule?
10. How would you monitor quality trends over time?

---

## Advanced

1. Design a multi-layer data quality architecture for a production lakehouse.
2. Design quality SLAs for an event-driven data product.
3. How would you distinguish pipeline reliability from data quality?
4. How would you detect silent data degradation?
5. How would you design producer-owned data contracts?
6. How would you handle intentional duplicates in at-least-once event delivery?
7. How would you design cross-system reconciliation?
8. How would you evolve quality thresholds as volume changes?
9. How would you integrate quality metrics with incident management?
10. How would you design quality gates without making the pipeline unnecessarily brittle?

---

# 53. Production Design Exercise

Design quality controls for this pipeline:

```text
REST API
   ↓
Python ingestion
   ↓
raw JSON
   ↓
DataFrame
   ↓
transformation
   ↓
Parquet
   ↓
PostgreSQL
   ↓
analytics dashboard
```

Your design must identify:

### Source quality

```text
availability
completeness
validity
timeliness
```

### Ingestion quality

```text
schema
record counts
duplicates
checkpoint completeness
```

### Transformation quality

```text
business rules
cross-field consistency
type correctness
```

### Storage quality

```text
Parquet readability
partition completeness
row counts
```

### Database quality

```text
referential integrity
uniqueness
reconciliation
```

### Consumer quality

```text
freshness
timeliness
availability
```

---

# 54. Final Quality Dimension Checklist

Before saying:

> "This dataset is high quality."

verify that you can answer:

## Accuracy

- [ ] Does the data represent reality?
- [ ] What reference establishes accuracy?

## Completeness

- [ ] Are required fields populated?
- [ ] Did the expected records arrive?

## Validity

- [ ] Do values satisfy allowed rules?
- [ ] Are formats correct?

## Consistency

- [ ] Do related fields agree?
- [ ] Do related systems agree where they should?

## Uniqueness

- [ ] Are identifiers unique where required?
- [ ] Are duplicates intentional or accidental?

## Timeliness

- [ ] Did data arrive within the required time window?

## Freshness

- [ ] How old is the newest available data?

## Integrity

- [ ] Are relationships preserved?
- [ ] Are there orphan records?

## Conformity

- [ ] Are standards and canonical representations followed?

## Availability

- [ ] Can consumers access the expected data?

---

# 55. Final Mental Model

Remember the following transformation:

```text
"Data looks good"
        ↓
not measurable

"Customer IDs are complete"
        ↓
dimension:
completeness

metric:
non-null rate

expectation:
>= 99.99%

severity:
critical

action:
reject/quarantine

owner:
source producer
```

That is the transition from informal data checking to production data quality engineering.

---

# 56. Key Takeaways

1. Data quality is **fitness for intended use**.
2. Data quality is multidimensional.
3. Accuracy, completeness, validity, consistency, uniqueness, timeliness, freshness, integrity, conformity, and availability answer different questions.
4. Validity does not prove accuracy.
5. Non-null data is not necessarily high-quality data.
6. Duplicate data is not automatically incorrect.
7. Freshness and timeliness are related but distinct.
8. Data profiling measures what exists; quality assessment compares it with expectations.
9. Validation is the mechanism used to test quality requirements.
10. Data contracts make expectations explicit between producers and consumers.
11. Record-level checks are necessary but insufficient.
12. Dataset-level and cross-dataset checks are also required.
13. Every important quality rule should have a measurable metric.
14. Metrics need thresholds and actions.
15. Thresholds must reflect actual business and consumer requirements.
16. Not every quality failure should block a pipeline.
17. Quality ownership must be explicit.
18. Quality should be monitored over time.
19. Pipeline success does not imply data quality.
20. Production data quality is a deliberate engineering system, not an afterthought.

---

# 57. Final Production Principle

> **Do not ask only whether the pipeline ran successfully. Ask whether the resulting data is accurate, complete, valid, consistent, unique where required, timely, fresh, structurally intact, conformant, and available for its intended consumers—and define measurable evidence for each requirement.**
