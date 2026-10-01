# Reconciliation and Row-Count Audits

> **Module:** Python for Data Engineering — Data Validation, Contracts, and Quality  
> **Topic:** 09 — Reconciliation and Row-Count Audits  
> **Level:** Beginner → Intermediate → Advanced → Production  
> **Core question:** **Did the data that entered one stage of the system actually arrive correctly at the next stage?**

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- Explain reconciliation in plain language.
- Distinguish validation from reconciliation and auditing.
- Build basic row-count audits.
- Explain why equal row counts do **not** prove equal data.
- Identify records with stable keys.
- Perform set-based reconciliation with Python, pandas, and SQL.
- Reconcile important aggregates such as counts, sums, distinct counts, and financial totals.
- Build deterministic row and batch hashes.
- Reconcile data by partition, batch, and pipeline run.
- Design an audit table that preserves evidence of what happened.
- Choose exact, absolute, relative, and business tolerances.
- Handle late-arriving data without confusing temporary incompleteness with permanent loss.
- Detect duplicate and replay loads and connect reconciliation to idempotency.
- Perform incremental reconciliation using watermarks, high-water marks, and CDC.
- Reconcile transformations such as filtering, joins, deduplication, aggregation, and row explosion.
- Reconcile APIs, files, databases, warehouses, lakehouses, and streams.
- Classify reconciliation failures and select safe recovery actions.
- Build tests and defect-injection experiments.
- Debug mismatches systematically.
- Design a production-grade reconciliation architecture.
- Explain reconciliation decisions in technical interviews and system-design discussions.

### The learning progression

```text
beginner intuition
      ↓
what reconciliation means
      ↓
why it exists
      ↓
row-count audits
      ↓
source vs target comparison
      ↓
keys and record identity
      ↓
aggregate reconciliation
      ↓
checksum/hash reconciliation
      ↓
partition reconciliation
      ↓
batch/run reconciliation
      ↓
incremental reconciliation
      ↓
tolerance-based reconciliation
      ↓
late-arriving data
      ↓
duplicate detection
      ↓
streaming reconciliation
      ↓
audit trails
      ↓
production architecture
      ↓
testing
      ↓
debugging
      ↓
mini-project
      ↓
advanced production scenarios
      ↓
interview/architecture questions
```

---

## 2. Why Reconciliation Exists

Imagine that a warehouse sends **100 boxes** to another warehouse.

The receiving warehouse records **97 boxes**.

The first question is not:

> "Are the 97 boxes valid?"

The first question is:

> **"Where did the other 3 boxes go?"**

That is the intuition behind reconciliation.

A data pipeline has similar boundaries:

```text
source system
    ↓
data extraction
    ↓
raw dataset
    ↓
transformation
    ↓
target dataset
```

At every important boundary, we want evidence that the expected data crossed the boundary correctly.

### 2.1 What reconciliation detects

Reconciliation can detect:

- missing records
- duplicated records
- unexpected additions
- dropped records
- partial loads
- incomplete extraction
- transformation loss
- filtering mistakes
- partition loss
- source/target mismatches
- failed writes
- replay duplication
- late-arriving data
- incorrect joins
- aggregation mismatches
- pipeline bugs
- operational failures

### 2.2 Reconciliation is a control, not just a query

A production reconciliation process usually has:

```text
measurement
    ↓
comparison
    ↓
expected result
    ↓
classification
    ↓
evidence
    ↓
action
```

For example:

```text
source_count = 1,000,000
target_count = 999,998
difference = 2

        ↓

Is a difference of 2 allowed?

        ↓

No

        ↓

Investigate / block / replay
```

A production system should be able to answer not only **what differed**, but also:

- when was the check performed?
- which run produced the data?
- which source snapshot was used?
- which target snapshot was used?
- what rule was applied?
- what tolerance was configured?
- who or what owns the failure?
- what recovery action occurred?
- did the later reconciliation pass?

---

## 3. Validation vs Reconciliation

These concepts are related but answer different questions.

| Concept | Main question |
|---|---|
| Schema validation | Is the structure correct? |
| Record validation | Is each record valid? |
| DataFrame validation | Does the dataset satisfy its schema/rules? |
| Volume monitoring | Did approximately the expected amount arrive? |
| Reconciliation | Did the expected data move correctly between boundaries? |
| Audit | Can we prove what happened? |

### Example

Suppose a source contains:

```text
order_id | amount
---------+-------
A        | 100
B        | 200
C        | 300
```

The target contains:

```text
order_id | amount
---------+-------
A        | 100
B        | 200
C        | 999
```

Every row may satisfy a basic schema:

- `order_id` exists
- `amount` is numeric
- no required field is null

But reconciliation can still discover that the important business value changed.

### The distinction

```text
Validation:
"Is this data valid?"

Reconciliation:
"Did the expected data move correctly between two systems,
 stages, datasets, or pipeline boundaries?"

Audit:
"Can we prove what happened?"
```

These controls complement one another.

---

## 4. What Is a Row-Count Audit?

A row-count audit compares the number of records observed at one boundary with the number expected at another boundary.

The simplest case is:

```python
source_count = 1_000
target_count = 1_000

assert source_count == target_count
```

If:

```python
source_count = 1_000
target_count = 973

difference = source_count - target_count
print(difference)
# 27
```

we have evidence that 27 more records existed at the source than at the target.

### Important warning

A row-count audit tells you about **quantity**, not necessarily **identity or correctness**.

This is a central principle:

```text
row count equality != data equality
```

---

## 4.1 Source Count

A source count is a measurement of how many records the source boundary contains.

Example SQL:

```sql
SELECT COUNT(*) AS source_count
FROM source.orders;
```

In Python:

```python
source_count = 1000
```

In production, capture the count as part of the run's audit metadata rather than calculating it and immediately discarding it.

---

## 4.2 Target Count

Example:

```sql
SELECT COUNT(*) AS target_count
FROM target.orders;
```

Python:

```python
target_count = 973
```

---

## 4.3 Expected Count

Sometimes the target should equal the source.

But sometimes the target is intentionally different.

Examples:

```text
one-to-one copy:
expected_target = source_count

filter:
expected_target <= source_count

aggregation:
expected_target is determined by grouping cardinality

explode:
expected_target may be greater than source_count
```

The expected count must therefore come from **transformation semantics**, not from a universal rule.

---

## 4.4 Comparing Counts

A useful basic result contains:

```python
source_count = 1_000
target_count = 973

difference = source_count - target_count

if source_count == 0:
    difference_pct = 0.0 if target_count == 0 else float("inf")
else:
    difference_pct = abs(difference) / source_count * 100

print(difference)
print(difference_pct)
```

For a source of 1,000 and target of 973:

```text
difference = 27
difference_pct = 2.7%
```

### The zero baseline

Never blindly calculate:

```python
abs(source_count - target_count) / source_count
```

when:

```text
source_count == 0
```

Instead define an explicit policy.

For example:

```python
def percentage_difference(source_count: int, target_count: int) -> float:
    if source_count < 0 or target_count < 0:
        raise ValueError("Counts cannot be negative")

    if source_count == 0:
        return 0.0 if target_count == 0 else float("inf")

    return abs(source_count - target_count) / source_count * 100
```

**Production consideration:** the mathematical result for a zero baseline is less important than having a documented business policy for `0 → 0`, `0 → positive`, and `positive → 0`.

---

## 5. The Simplest Reconciliation

The first useful mental model is:

```text
source
  |
  | measure
  v
source_count
  |
  | compare
  v
target_count
  |
  | classify
  v
PASS / FAIL
```

A simple implementation:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CountReconciliation:
    source_count: int
    target_count: int
    difference: int
    difference_pct: float
    passed: bool


def reconcile_counts(
    source_count: int,
    target_count: int,
    tolerance_pct: float = 0.0,
) -> CountReconciliation:
    if source_count < 0 or target_count < 0:
        raise ValueError("Counts must be non-negative")

    if tolerance_pct < 0:
        raise ValueError("Tolerance cannot be negative")

    difference = target_count - source_count

    if source_count == 0:
        difference_pct = 0.0 if target_count == 0 else float("inf")
    else:
        difference_pct = abs(difference) / source_count * 100

    passed = difference_pct <= tolerance_pct

    return CountReconciliation(
        source_count=source_count,
        target_count=target_count,
        difference=difference,
        difference_pct=difference_pct,
        passed=passed,
    )


result = reconcile_counts(1_000, 998, tolerance_pct=0.5)
print(result)
```

### What this code does not prove

It does not prove:

- the same records arrived
- no duplicates exist
- no substitutions occurred
- the values are unchanged
- partitions are correct
- business totals are correct

Those require stronger controls.

---

## 6. Why Row Counts Alone Are Not Enough

Consider:

```text
Source:
A
B
C
D

Target:
A
B
C
X
```

Both contain:

```text
4 rows
```

But `D` is missing and `X` is unexpected.

Therefore:

```text
source_count == target_count
```

does **not** imply:

```text
source_data == target_data
```

### Equal counts can hide

- missing records
- unexpected records
- duplicates
- substitutions
- wrong partitions
- incorrect transformations

A stronger reconciliation hierarchy is:

```text
Count
  ↓
Key set
  ↓
Aggregates
  ↓
Field-level comparison
  ↓
Canonical hashes
```

You do not always need every layer. The right controls depend on the data boundary and its business risk.

---

## 7. Reconciliation Across Pipeline Boundaries

A mature pipeline may look like:

```text
Source
  ↓
Raw
  ↓
Staging
  ↓
Curated
  ↓
Analytics
  ↓
Published dataset
```

Different boundaries may require different controls.

## 7.1 Source to Raw

Typical checks:

- extraction count
- API/file manifest
- source batch ID
- raw record count
- raw partition count
- extraction timestamps

## 7.2 Raw to Staging

Typical checks:

- input count
- rejected/quarantined count
- accepted count
- expected filtering
- duplicate rate
- partition counts

A useful accounting relationship might be:

```text
input_count
    =
accepted_count
+ quarantined_count
+ intentionally_rejected_count
```

provided the pipeline contract defines those categories as mutually exclusive and exhaustive.

## 7.3 Staging to Curated

Typical checks:

- key reconciliation
- deduplication accounting
- business-rule filters
- aggregate preservation
- partition reconciliation

## 7.4 Curated to Analytics

The target may be aggregated, so exact row equality may be meaningless.

Instead compare:

- metric totals
- group-level counts
- distinct entities
- date coverage
- expected dimensional grain

## 7.5 Source to Warehouse

For large systems, use multiple levels:

```text
run count
partition count
key sample/full key reconciliation
aggregate reconciliation
```

## 7.6 Warehouse to Published Dataset

Focus on:

- published row counts
- business metrics
- freshness
- expected filters
- semantic transformations
- publication version

---

## 8. Record Identity and Keys

Reconciliation needs a definition of **which record is which**.

## 8.1 Natural Keys

A natural key is an identifier that already exists in the business data.

Example:

```text
order_id
```

If `order_id` is globally unique and stable, it is useful for reconciliation.

## 8.2 Surrogate Keys

A surrogate key is generated by the data system.

Example:

```text
customer_sk
```

Surrogate keys can be useful inside a warehouse but may not match across independently generated systems.

## 8.3 Business Keys

A business key identifies an entity according to business meaning.

Examples:

```text
customer_id
account_number
order_id
```

## 8.4 Composite Keys

Sometimes identity requires multiple fields:

```text
customer_id + order_date
```

or:

```text
source_system + transaction_id
```

In Python:

```python
key = (customer_id, order_date)
```

In SQL:

```sql
ON s.customer_id = t.customer_id
AND s.order_date = t.order_date
```

## 8.5 Why Keys Matter for Reconciliation

Without a stable identity, you may know:

```text
source = 1,000
target = 1,000
```

but not whether the same 1,000 records arrived.

### When there is no natural key

Possible approaches include:

1. use a trustworthy composite business key;
2. create a deterministic canonical record fingerprint;
3. reconcile using multiple business attributes;
4. use source sequence numbers or offsets;
5. improve the upstream contract to provide stable identifiers.

Do not casually invent a random surrogate key after ingestion and assume it solves cross-system reconciliation.

---

## 9. Count-Based Reconciliation

## 9.1 Exact Count Match

For a one-to-one boundary:

```python
passed = source_count == target_count
```

## 9.2 Count Difference

Define:

```text
difference = target - source
```

The sign matters.

For:

```text
source = 1000
target = 973
```

```text
difference = -27
```

This indicates fewer target records.

For:

```text
source = 1000
target = 1025
```

```text
difference = +25
```

This indicates more target records.

## 9.3 Percentage Difference

Formula:

\[
difference\_pct =
\frac{|target-source|}{source}\times100
\]

Variables:

- `source` = reference record count
- `target` = observed target count
- absolute value makes the percentage non-negative

Example:

```text
source = 1,000
target = 950

absolute difference = 50

50 / 1,000 × 100
= 5%
```

Python:

```python
def difference_pct(source: int, target: int) -> float:
    if source == 0:
        return 0.0 if target == 0 else float("inf")
    return abs(target - source) / source * 100
```

## 9.4 Tolerance

A rule could be:

```text
PASS if difference_pct <= 0.5%
```

But the tolerance must have a business or system justification.

## 9.5 Zero-Row Loads

Examples:

```text
0 → 0
```

may be a valid empty batch.

But:

```text
0 → 10,000
```

could indicate unexpected data creation.

And:

```text
10,000 → 0
```

may indicate a catastrophic load failure.

The interpretation depends on the boundary contract.

## 9.6 Duplicate Loads

A duplicate load may produce:

```text
source = 1,000
target = 2,000
```

But more subtle replay bugs can preserve the count while changing record identity.

That is why count checks must be combined with key and duplicate checks.

---

## 10. Set-Based Reconciliation

Set reconciliation asks:

```text
Which source records are missing from the target?

Which target records were not present in the source?
```

## 10.1 Records in Source but Not Target

Using Python sets:

```python
source_ids = {"A", "B", "C", "D"}
target_ids = {"A", "B", "C", "E"}

missing = source_ids - target_ids

print(missing)
# {'D'}
```

## 10.2 Records in Target but Not Source

```python
unexpected = target_ids - source_ids

print(unexpected)
# {'E'}
```

## 10.3 Missing Records

```text
Source - Target
```

means:

> records expected from the source but absent in the target.

## 10.4 Unexpected Records

```text
Target - Source
```

means:

> records present in the target that were not present in the source comparison population.

## 10.5 Full Outer Join

With pandas:

```python
import pandas as pd

source = pd.DataFrame({"order_id": ["A", "B", "C", "D"]})
target = pd.DataFrame({"order_id": ["A", "B", "C", "E"]})

reconciled = source.merge(
    target,
    on="order_id",
    how="outer",
    indicator=True,
)

print(reconciled)
```

The `_merge` column indicates:

```text
left_only   → source only
right_only  → target only
both        → found in both
```

## 10.6 Anti-Join Concepts

A left anti-join returns records from the left side that have no match on the right.

Conceptually:

```text
source LEFT ANTI JOIN target
```

returns missing target records.

A right anti-join does the opposite.

### Production warning: duplicate multiplication

If the join key is not unique, a normal join can multiply rows.

For example:

```text
source:
A
A

target:
A
```

A join may produce two matches.

Before interpreting join results, understand the grain and uniqueness of each side.

---

## 11. SQL Reconciliation

## 11.1 Count Reconciliation

```sql
SELECT COUNT(*) AS source_count
FROM source.orders;
```

```sql
SELECT COUNT(*) AS target_count
FROM target.orders;
```

A combined comparison can be clearer:

```sql
SELECT
    (SELECT COUNT(*) FROM source.orders) AS source_count,
    (SELECT COUNT(*) FROM target.orders) AS target_count;
```

## 11.2 Missing Keys

```sql
SELECT s.order_id
FROM source.orders AS s
LEFT JOIN target.orders AS t
    ON s.order_id = t.order_id
WHERE t.order_id IS NULL;
```

This is a common anti-join pattern.

## 11.3 Unexpected Keys

```sql
SELECT t.order_id
FROM target.orders AS t
LEFT JOIN source.orders AS s
    ON t.order_id = s.order_id
WHERE s.order_id IS NULL;
```

## 11.4 Full Outer Reconciliation

PostgreSQL supports `FULL OUTER JOIN`:

```sql
SELECT
    COALESCE(s.order_id, t.order_id) AS order_id,
    CASE
        WHEN s.order_id IS NULL THEN 'target_only'
        WHEN t.order_id IS NULL THEN 'source_only'
        ELSE 'both'
    END AS reconciliation_status
FROM source.orders AS s
FULL OUTER JOIN target.orders AS t
    ON s.order_id = t.order_id;
```

Dialect support differs across database engines, so use an equivalent anti-join/union strategy when `FULL OUTER JOIN` is unavailable.

## 11.5 NULL Behavior

This:

```sql
a = b
```

does not evaluate to `TRUE` when both values are SQL `NULL`.

For null-safe comparison, use dialect-appropriate operators. PostgreSQL provides:

```sql
a IS NOT DISTINCT FROM b
```

This treats two nulls as equal.

---

## 12. Aggregate Reconciliation

Counts are not enough when business values can change.

Consider:

```text
Source:
orders  = 100
revenue = $50,000

Target:
orders  = 100
revenue = $47,000
```

Row counts reconcile, but the business result does not.

## 12.1 Sum Checks

```sql
SELECT
    COUNT(*) AS row_count,
    SUM(amount) AS total_amount
FROM source.orders;
```

Compare with the target.

## 12.2 Count Checks

Count can refer to:

- total rows
- successful rows
- failed rows
- rows per status
- rows per partition

## 12.3 Min/Max Checks

Useful for detecting coverage problems:

```sql
SELECT
    MIN(order_timestamp) AS min_ts,
    MAX(order_timestamp) AS max_ts
FROM source.orders;
```

A target that suddenly begins two days later may have a missing time range.

## 12.4 Distinct Count Checks

```sql
SELECT COUNT(DISTINCT customer_id)
FROM source.orders;
```

Compare with target.

Distinct counts can expose problems that total row counts miss.

## 12.5 Business Metric Reconciliation

Examples:

- total revenue
- total quantity
- total tax
- number of active customers
- number of completed orders
- number of refunds

The selected metrics should reflect the business meaning of the dataset.

## 12.6 Financial Reconciliation

Suppose:

```text
Source payment amount = 1,250,000
Target payment amount = 1,245,000
Difference            = 5,000
```

A small percentage difference can still represent a serious operational issue.

For monetary values, use `Decimal` rather than binary floating-point arithmetic:

```python
from decimal import Decimal

source_amount = Decimal("1250000.00")
target_amount = Decimal("1245000.00")

difference = source_amount - target_amount

print(difference)
# 5000.00
```

### Financial controls

Consider:

- absolute difference
- relative difference
- currency
- rounding rules
- decimal precision
- missing transactions
- duplicate transactions
- reversals/refunds
- exchange-rate timing

A financial reconciliation tolerance should be explicitly approved by the relevant business/data owner.

---

## 13. Hash and Checksum Reconciliation

A hash is a deterministic fingerprint of input bytes.

A simple example:

```python
import hashlib


def row_hash(values: list[str]) -> str:
    payload = "|".join(values)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

For:

```python
row_hash(["A", "100", "paid"])
```

the same input produces the same digest.

## 13.1 Why Hashes Help

A hash can compactly represent many fields.

Instead of comparing every field individually in some workflows, you can compare deterministic fingerprints.

But:

> A hash is evidence of matching representations, not a magical proof of semantic equivalence.

## 13.2 Row Hashes

A robust row hash needs a defined serialization.

For example:

```python
import hashlib


def canonical_row(
    order_id: str,
    amount: Decimal,
    status: str | None,
) -> str:
    normalized_status = "" if status is None else status.strip().lower()

    return "|".join(
        [
            order_id.strip(),
            format(amount, ".2f"),
            normalized_status,
        ]
    )


def row_hash(
    order_id: str,
    amount: Decimal,
    status: str | None,
) -> str:
    canonical = canonical_row(order_id, amount, status)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

## 13.3 Batch Hashes

A batch-level fingerprint can summarize a deterministic collection of records.

A naive approach:

```python
hash(concatenated_rows)
```

is dangerous if row order is not guaranteed.

A more controlled approach is to sort deterministic record hashes before creating a batch digest:

```python
import hashlib


def batch_hash(row_hashes: list[str]) -> str:
    ordered = sorted(row_hashes)
    payload = "\n".join(ordered).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
```

This makes the batch fingerprint insensitive to input row order.

## 13.4 Deterministic Hashing

For deterministic reconciliation, define:

- column order
- string normalization
- null representation
- timestamp format
- timezone
- decimal formatting
- encoding
- row ordering policy

Without those rules, logically equivalent data can produce different hashes.

## 13.5 Canonicalization

Canonicalization means converting logically equivalent values into one agreed representation.

Example:

```text
" PAID "
"paid"
"Paid"
```

may or may not be equivalent. The business contract must decide.

Similarly:

```text
2026-09-30T12:00:00Z
2026-09-30 08:00:00-04:00
```

represent the same instant but have different textual representations.

## 13.6 Hash Collisions

Cryptographic hash functions can theoretically collide.

For ordinary engineering reconciliation, SHA-256 provides a very large digest space and is generally used as a strong fingerprint, but never claim mathematical impossibility of collision.

## 13.7 Limitations

Hashes do not automatically tell you:

- which record changed
- which field changed
- whether formatting differences are intentional
- whether a transformation changed business meaning

Use them as one layer of evidence.

---

## 14. Partition-Level Reconciliation

Partition reconciliation answers:

> **Where exactly is the mismatch?**

A total count can hide localized failures.

Example:

```text
Source

2026-09-28 → 100,000
2026-09-29 → 100,000
2026-09-30 → 100,000
```

Target:

```text
2026-09-28 → 100,000
2026-09-29 → 200,000
2026-09-30 → 100,000
```

The target has 100,000 extra records on one date.

### Partition dimensions

Reconcile by:

- date
- hour
- region
- source
- customer segment
- event type

## 14.1 SQL

```sql
SELECT
    order_date,
    COUNT(*) AS source_count
FROM source.orders
GROUP BY order_date
ORDER BY order_date;
```

```sql
SELECT
    order_date,
    COUNT(*) AS target_count
FROM target.orders
GROUP BY order_date
ORDER BY order_date;
```

Then compare the grouped results.

## 14.2 pandas

```python
source_daily = (
    source.groupby("order_date")
    .size()
    .rename("source_count")
)

target_daily = (
    target.groupby("order_date")
    .size()
    .rename("target_count")
)

daily = source_daily.to_frame().join(
    target_daily,
    how="outer",
).fillna(0)

daily["difference"] = (
    daily["target_count"] - daily["source_count"]
)

print(daily)
```

### Production value

Partition reconciliation sharply reduces investigation time:

```text
whole dataset mismatch
        ↓
date mismatch
        ↓
region mismatch
        ↓
specific run
        ↓
specific records
```

---

## 15. Batch and Run-Level Reconciliation

Every important pipeline execution should have an identity.

Useful identifiers include:

```text
run_id
batch_id
extract_id
load_id
partition_id
```

## 15.1 Run IDs

A `run_id` identifies a particular pipeline execution.

Example:

```text
run-2026-09-30-001
```

## 15.2 Batch IDs

A `batch_id` identifies a logical input batch.

A single run may process several batches, or a batch may be replayed by several runs.

## 15.3 Source Extract IDs

External systems may provide:

```text
extract_id = export-83921
```

This is valuable evidence because it connects your pipeline to the producer's own artifact.

## 15.4 Target Load IDs

Similarly:

```text
load_id = warehouse-load-1832
```

can identify what was written.

## 15.5 Audit Metadata

A useful audit record contains:

```text
run_id
dataset
source_count
target_count
difference
source_min_timestamp
source_max_timestamp
target_min_timestamp
target_max_timestamp
status
started_at
completed_at
```

## 15.6 End-to-End Run Tracking

A useful lineage chain is:

```text
source_extract_id
       ↓
pipeline_run_id
       ↓
target_load_id
       ↓
reconciliation_id
```

This allows an incident responder to trace one execution across the system.

---

## 16. Audit Tables

## 16.1 Why Audit Tables Exist

A log message can tell you:

```text
reconciliation failed
```

An audit table can preserve:

- what was checked
- what values were observed
- which rule was used
- when it was checked
- what status resulted

This creates durable evidence.

## 16.2 Audit Table Schema

PostgreSQL-compatible example:

```sql
CREATE TABLE reconciliation_audit (
    run_id TEXT NOT NULL,
    dataset_name TEXT NOT NULL,
    source_count BIGINT,
    target_count BIGINT,
    count_difference BIGINT,
    difference_pct NUMERIC,
    source_checksum TEXT,
    target_checksum TEXT,
    status TEXT NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL
);
```

### Field explanations

| Field | Purpose |
|---|---|
| `run_id` | Identifies the pipeline execution |
| `dataset_name` | Identifies the reconciled dataset |
| `source_count` | Captures source-side measurement |
| `target_count` | Captures target-side measurement |
| `count_difference` | Stores the numerical difference |
| `difference_pct` | Stores relative difference |
| `source_checksum` | Optional source fingerprint |
| `target_checksum` | Optional target fingerprint |
| `status` | PASS/WARNING/FAIL/etc. |
| `checked_at` | Evidence timestamp |

## 16.3 Production Extensions

Useful additional fields:

- pipeline version
- code version
- environment
- source system
- target system
- partition
- severity
- failure reason
- operator
- remediation status
- source snapshot identifier
- target snapshot identifier
- rule version
- reconciliation duration

## 16.4 Audit History

Do not overwrite history blindly.

A historical audit trail lets you answer:

```text
Did this dataset fail yesterday?
Did it recover?
How often does this pipeline mismatch?
Which rule fails most often?
How long do incidents remain unresolved?
```

---

## 17. Tolerance-Based Reconciliation

Exact equality is not always appropriate.

Example:

```text
Source = 1,000,000
Target = 999,998
```

A difference of two records might be expected in an eventually consistent system.

## 17.1 Exact Equality

```python
passed = source_count == target_count
```

Use when the system contract requires exact movement.

## 17.2 Absolute Tolerance

Formula:

\[
|source-target| \le tolerance
\]

Example:

```text
source = 1,000,000
target = 999,998
tolerance = 5

difference = 2

2 <= 5 → PASS
```

Python:

```python
def within_absolute_tolerance(
    source: int,
    target: int,
    tolerance: int,
) -> bool:
    if tolerance < 0:
        raise ValueError("Tolerance cannot be negative")
    return abs(source - target) <= tolerance
```

## 17.3 Relative Tolerance

Formula:

\[
\frac{|source-target|}{source}\le tolerance
\]

where `tolerance` is expressed as a fraction.

Example:

```text
source = 1,000,000
target = 999,000
difference = 1,000

relative difference = 0.001 = 0.1%
```

Python:

```python
def within_relative_tolerance(
    source: int,
    target: int,
    tolerance_fraction: float,
) -> bool:
    if tolerance_fraction < 0:
        raise ValueError("Tolerance cannot be negative")

    if source == 0:
        return target == 0

    return abs(source - target) / source <= tolerance_fraction
```

## 17.4 Business Tolerance

Tolerance can represent:

- expected late events
- source-system eventual consistency
- known rounding
- API timing
- operational delay

It should not simply be:

```text
"We set 5% because the check kept failing."
```

## 17.5 Why Tolerance Can Be Dangerous

A tolerance that is too high can turn:

```text
real data loss
```

into:

```text
PASS
```

Therefore:

> **Tolerance is a business/data-system decision, not an arbitrary convenience.**

---

## 18. Reconciliation with Late-Arriving Data

A mismatch does not always mean data loss.

Suppose the source is still receiving events.

At:

```text
T+0 → target has 950,000
```

Later:

```text
T+2h → source and target both have 1,000,000
```

The initial mismatch was caused by timing.

## 18.1 Event Time

When the business event occurred.

## 18.2 Ingestion Time

When the system received the event.

## 18.3 Processing Time

When the pipeline processed the event.

These can differ significantly.

## 18.4 Late Data

Late data arrives after the normal expected processing window.

## 18.5 Reconciliation Windows

A system might define:

```text
T+0   → provisional
T+30m → provisional
T+2h  → final
```

The exact window depends on the dataset contract and SLA.

## 18.6 Watermarks

A watermark represents a system's progress toward believing that data up to some event-time boundary is sufficiently complete.

Watermarks help distinguish:

```text
still waiting
```

from:

```text
expected window is closed
```

## 18.7 Final vs Provisional Reconciliation

A production result can have states such as:

```text
PROVISIONAL
PASS
WARNING
FAIL
```

A provisional mismatch should not necessarily page an on-call engineer if the data is still inside the documented grace period.

---

## 19. Reconciliation and Duplicate Detection

Equal counts can hide duplicates.

Example:

```text
Source IDs:
A B C D

Target IDs:
A B C C
```

Both contain four rows.

But the target is wrong.

## 19.1 Duplicate Records

SQL:

```sql
SELECT
    order_id,
    COUNT(*) AS occurrence_count
FROM target.orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

## 19.2 Duplicate Loads

A whole batch may be loaded twice.

Example:

```text
batch-001
batch-001
```

The data may be identical but duplicated.

## 19.3 Replay Duplication

A retry can accidentally insert records a second time.

## 19.4 Idempotency

A useful property is:

> Repeating the same logical operation produces the same final state rather than creating duplicate effects.

For a load operation:

```text
load(batch_001)
load(batch_001)
```

should not necessarily create two copies.

## 19.5 Exactly-Once vs Effectively-Once

Exactly-once semantics are a system-level property with strong implementation requirements.

"Effectively once" often means that the system may retry operations internally, but the final externally visible result behaves as though each logical record was processed once.

Do not use the terms interchangeably without defining the system guarantees.

---

## 20. Incremental Reconciliation

## 20.1 Full Reconciliation

A full reconciliation compares the complete relevant dataset.

Advantages:

- strong coverage
- simple conceptual model

Costs:

- expensive scans
- large joins
- high network movement
- potentially long runtime

## 20.2 Incremental Reconciliation

Only the changed scope is reconciled.

Examples:

```text
today's partition
new CDC records
records after a high-water mark
changed rows since last successful run
```

## 20.3 High-Water Marks

A high-water mark records the greatest successfully processed value.

Example:

```text
last_processed_id = 8,500,000
```

The next extraction may request:

```text
id > 8,500,000
```

## 20.4 Watermarks

Time-based pipelines may use:

```text
updated_at > last_watermark
```

But timestamp watermarks require careful handling of:

- clock differences
- equal timestamps
- late updates
- timezone normalization
- precision

## 20.5 Changed Records

A reliable `updated_at` or version column can support incremental reconciliation.

## 20.6 Change Data Capture

CDC systems emit changes such as:

```text
INSERT
UPDATE
DELETE
```

Reconciliation can compare:

```text
expected changes
```

with:

```text
applied changes
```

This is often more efficient than repeatedly scanning a full table.

---

## 21. Reconciliation for Transformations

This is one of the most important production concepts.

Source and target row counts may legitimately differ.

### Filtering

```text
1,000 source rows
→ 700 target rows
```

If the contract says cancelled orders are removed, this may be correct.

### Deduplication

```text
1,000 source rows
→ 950 target rows
```

This may be expected if 50 duplicate source records were collapsed.

### Aggregation

```text
1,000 detail rows
→ 100 aggregate rows
```

Expected.

### Exploding arrays

```text
100 source rows
→ 450 target rows
```

Potentially expected.

Therefore:

> **Reconciliation must compare against expected transformation semantics, not blindly require equal counts.**

---

## 22. Expected Reconciliation Rules

A transformation should define what relationship is expected.

Examples:

```text
one-to-one copy:
target == source

filter:
target <= source

deduplication:
target <= source

aggregation:
target <= source

explode:
target >= source
```

These are conceptual examples, not universal laws.

For example, an aggregation could generate more rows than an unusual source grain, and a transformation can duplicate rows intentionally.

The production rule must be explicit.

### A useful pattern

Define:

```text
source metric
+
transformation contract
+
expected relationship
+
target metric
=
reconciliation decision
```

---

## 23. Reconciliation for Aggregated Data

## 23.1 Detail-to-Aggregate Reconciliation

Suppose the source contains order details and the target contains daily revenue.

Do not compare:

```text
source row count == target row count
```

Instead compare:

```text
SUM(source.amount) == SUM(target.daily_revenue)
```

for the same business population and time window.

## 23.2 Sum Preservation

```sql
SELECT SUM(amount)
FROM source.order_lines;
```

versus:

```sql
SELECT SUM(revenue)
FROM target.daily_revenue;
```

The grouping changes, but the relevant business measure may be preserved.

## 23.3 Count Preservation

Counts may need semantic conversion.

For example:

```text
COUNT(order_lines)
```

is not necessarily equal to:

```text
COUNT(orders)
```

because one order can contain many lines.

## 23.4 Group-Level Reconciliation

Compare by:

```text
date
region
product_category
```

rather than only comparing a global total.

## 23.5 Roll-Up Reconciliation

If a warehouse has:

```text
hour → day → month
```

you can reconcile:

```text
sum(hourly) == daily
sum(daily) == monthly
```

subject to the defined population and treatment of late corrections.

---

## 24. Reconciliation for APIs and External Systems

APIs introduce unique failure modes:

- pagination
- missing pages
- duplicate pages
- retry duplication
- partial responses
- rate limiting
- changing source data during extraction

## 24.1 API Extraction Counts

Suppose:

```text
API reports: 10,000 records
pipeline loads: 7,500 records
```

This is immediately suspicious.

## 24.2 Pagination

Track:

```text
pages_requested
pages_received
records_received
API_total
```

Example:

```python
from dataclasses import dataclass


@dataclass
class APIAudit:
    pages_requested: int
    pages_received: int
    records_received: int
    api_total: int


audit = APIAudit(
    pages_requested=100,
    pages_received=75,
    records_received=7500,
    api_total=10000,
)

if audit.records_received != audit.api_total:
    print("Potential incomplete extraction")
```

## 24.3 Missing Pages

A pipeline may receive pages:

```text
1, 2, 3, 5, 6
```

and silently skip page 4.

Track page/token continuity where the API supports it.

## 24.4 Retry Duplication

A retry should not append the same logical page twice without detection.

Useful controls:

- page token tracking
- source record keys
- batch IDs
- idempotent writes

## 24.5 External System Audit Metadata

Capture:

- request/run ID
- API endpoint
- extraction start/end
- reported total
- pages requested
- pages received
- retry count
- HTTP failures
- rate-limit events

---

## 25. Reconciliation for Files

Files provide several reconciliation layers.

## 25.1 File-Level Counts

Expected:

```text
3 files
```

Observed:

```text
2 files
```

## 25.2 Record Counts

Each file can have a manifest count.

## 25.3 File Size

Unexpectedly tiny files can be a useful signal, but file size alone does not prove record completeness.

## 25.4 Manifest Files

Example:

```text
manifest:

file_001.parquet
file_002.parquet
file_003.parquet
```

A richer manifest can contain:

```text
file name
file size
record count
checksum
partition
schema version
```

A manifest can therefore act as an explicit reconciliation contract.

## 25.5 Checksums

File checksums can establish whether a file's bytes changed.

They do not explain semantic differences after a file is transformed.

## 25.6 Multi-File Batches

Reconcile:

```text
expected files
actual files
expected total rows
actual total rows
expected partitions
actual partitions
```

---

## 26. Reconciliation for Databases

Suppose:

```text
source database
       ↓
ETL
       ↓
target database
```

Use:

- source SQL
- target SQL
- count comparison
- key comparison
- aggregate comparison
- partition comparison

## 26.1 Snapshot Consistency

This is critical:

> **Comparing source and target at different points in time can produce false mismatches.**

Suppose the source receives 500 new orders while your target query is running.

Then:

```text
source count = 1,000,500
target count = 1,000,000
```

The difference may simply reflect observation times.

Possible controls include:

- source snapshot IDs
- transaction-consistent reads
- extraction cutoffs
- run-specific timestamps
- CDC positions
- immutable source extracts

## 26.2 PostgreSQL Example

```sql
SELECT
    COUNT(*) AS row_count,
    MIN(order_id) AS min_order_id,
    MAX(order_id) AS max_order_id
FROM source.orders
WHERE updated_at < TIMESTAMPTZ '2026-10-01 00:00:00+00';
```

Use the same logical cutoff on the target when appropriate.

---

## 27. Reconciliation for Data Lakes and Warehouses

A common architecture is:

```text
Source
  ↓
Raw
  ↓
Staging
  ↓
Curated
  ↓
Warehouse
  ↓
Published data product
```

At each boundary, define the appropriate evidence.

| Boundary | Useful controls |
|---|---|
| Source → Raw | extract count, manifest, source batch ID |
| Raw → Staging | accepted/rejected accounting, partitions, keys |
| Staging → Curated | deduplication, business filters, aggregates |
| Curated → Warehouse | grain, business metrics, partitions |
| Warehouse → Published | published count, metrics, freshness, contract |

Do not assume every boundary should use the same rule.

---

## 28. Streaming Reconciliation

Streaming is harder because the system is continuously changing.

A batch system can often ask:

```text
"How many records were in yesterday's batch?"
```

A stream asks:

```text
"How many events have been produced, received, processed,
committed, and acknowledged up to a defined point in time?"
```

## 28.1 Event Counts

Compare producer and consumer counts over a defined window.

## 28.2 Windowed Counts

Example:

```text
10:00–10:05
producer = 10,000
consumer = 9,850
```

## 28.3 Consumer Lag

The missing 150 events may simply be waiting.

## 28.4 Producer vs Consumer

Example:

```text
Producer:
10,000 events

Consumer:
9,850 processed

Outstanding:
150
```

This is not automatically permanent loss.

## 28.5 Offsets

For offset-based systems, track:

```text
producer partition
consumer partition
latest produced offset
latest committed offset
```

## 28.6 Watermarks

Use event-time progress to determine when a window can be considered sufficiently complete.

## 28.7 Late Events

A final reconciliation may need to wait for a watermark or grace period.

## 28.8 Duplicate Events

Track stable event IDs where possible.

---

## 29. Reconciliation Failures

| Failure | Meaning | Detection |
|---|---|---|
| Missing | Source record absent from target | anti-join |
| Extra | Target record absent from source | anti-join |
| Duplicate | Same record appears multiple times | duplicate-key check |
| Partial load | Only subset arrived | count/partition |
| Wrong transformation | Record changed incorrectly | field/aggregate |
| Wrong partition | Data landed in wrong partition | partition audit |
| Timing mismatch | Source and target observed at different times | snapshot/run metadata |
| Replay duplication | Retry created duplicates | run/batch identity |
| API page loss | One or more pages were skipped | page/token audit |
| Aggregate corruption | Important totals changed | aggregate reconciliation |
| Schema-induced mismatch | Representation changed | schema/contract checks |

---

## 30. Reconciliation Decision Model

A production decision process can be:

```text
Reconciliation result
        ↓
Is mismatch within documented tolerance?
        ↓
YES → PASS

NO
 ↓
Is data still within grace period?
 ↓
YES → PROVISIONAL / WAIT

NO
 ↓
Can partial publication be safe?
 ↓
YES → PARTIAL / FLAG

NO
 ↓
BLOCK / INVESTIGATE
```

Possible states:

### PASS

Evidence satisfies the rule.

### WARNING

A deviation exists but policy permits continued operation with visibility.

### FAIL

The reconciliation rule was violated.

### BLOCK

Publishing or downstream processing must stop because data cannot safely continue.

### INVESTIGATE

The system needs human or automated diagnosis.

### REPLAY

A controlled rerun is required.

### PARTIAL PUBLISH

Only safe data is published, with explicit semantics and downstream awareness.

---

## 31. Production Reconciliation Architecture

A production architecture can look like:

```text
                 +------------------+
                 |   Source System  |
                 +---------+--------+
                           |
                           v
                 +------------------+
                 |    Extraction    |
                 +---------+--------+
                           |
                           v
                 +------------------+
                 |   Source Audit   |
                 +---------+--------+
                           |
                           v
                 +------------------+
                 |  Transformation  |
                 +---------+--------+
                           |
                           v
                 +------------------+
                 |    Target Load   |
                 +---------+--------+
                           |
                           v
                 +------------------+
                 |   Target Audit   |
                 +---------+--------+
                           |
                           v
                 +----------------------+
                 | Reconciliation Engine|
                 +----------+-----------+
                            |
             +--------------+--------------+
             |                             |
             v                             v
      +-------------+               +-------------+
      |  Audit Store|               |   Metrics   |
      +------+------+               +------+------+
             |                             |
             |                             v
             |                       +-----------+
             |                       | Alerting  |
             |                       +-----+-----+
             |                             |
             v                             v
      +-------------+               +-----------+
      | Investigation|<-------------| Dashboard |
      +------+------+
             |
             v
      +-------------+
      | Recovery    |
      +-------------+
```

## Components

### Source Audit

Captures what the source says was available.

### Target Audit

Captures what the target says was written.

### Reconciliation Engine

Applies rules such as:

- count
- key
- aggregate
- partition
- checksum
- tolerance
- timing

### Audit Store

Persists evidence.

### Metrics

Turns reconciliation into observable operational signals.

### Alerting

Notifies responsible operators according to severity.

### Dashboard

Shows historical patterns and active failures.

#### Recovery

Supports:

- retry
- replay
- backfill
- partition reload
- full reload
- deduplication

---

## 32. Observability and Alerting

Useful metrics include:

```text
reconciliation_pass_rate
reconciliation_failure_count
missing_record_count
unexpected_record_count
duplicate_count
count_difference
difference_pct
aggregate_difference
partition_mismatch_count
time_to_reconcile
```

## Dashboard questions

A reconciliation dashboard should help answer:

- How many checks passed today?
- Which datasets fail most often?
- Which partitions are problematic?
- What is the average mismatch size?
- How long do failures remain open?
- Are failures increasing?
- Which pipeline version introduced a new failure pattern?

## Alerts

Not every mismatch deserves the same alert.

For example:

```text
financial mismatch
    → high severity

minor expected late data
    → no page / provisional state

repeated partition mismatch
    → operational alert
```

Alert policy should be driven by documented criticality.

---

## 33. Performance and Cost

Reconciliation can be expensive.

Potential costs include:

- full-table scans
- large joins
- sorting
- hashing
- network movement
- cross-system queries
- repeated scans

## Optimization techniques

### Partition pruning

Instead of scanning:

```text
10 TB
```

scan only:

```text
today's partition
```

when the reconciliation scope is partition-specific.

### Incremental reconciliation

Compare only changed records.

### Precomputed metrics

Persist counts and aggregates at write time.

### Metadata comparison

Use:

- manifests
- batch metadata
- source totals
- target load metadata

before expensive record-level checks.

### Sampling

Sampling can be useful for low-risk exploratory detection but does not prove complete reconciliation.

### Aggregate reconciliation

A cheap aggregate check may detect many failures before an expensive key comparison.

### Key-range reconciliation

Break large datasets into deterministic ranges:

```text
1–10M
10M–20M
20M–30M
```

### Checksums

Compact fingerprints can reduce data movement when deterministic canonicalization is available.

### Approximate methods

Approximate cardinality or statistical techniques may reduce cost where exactness is not required.

### Accuracy/cost principle

```text
higher assurance
    ↑
    |  full key + field comparison
    |  key reconciliation
    |  partition reconciliation
    |  aggregate reconciliation
    |  count reconciliation
    ↓
lower cost
```

The correct design depends on business risk.

---

## 34. Testing Reconciliation

A reconciliation engine should be tested like production software.

At minimum test:

- exact match
- missing records
- unexpected records
- duplicates
- equal counts but different records
- zero source rows
- zero target rows
- zero baseline
- absolute tolerance
- percentage tolerance
- late-arriving data
- expected filtering
- expected aggregation
- expected deduplication
- partition mismatch
- checksum mismatch
- API pagination mismatch

## Example pytest tests

```python
import pytest


def reconcile_counts(
    source: int,
    target: int,
    tolerance_fraction: float = 0.0,
) -> bool:
    if source < 0 or target < 0:
        raise ValueError("Counts cannot be negative")
    if tolerance_fraction < 0:
        raise ValueError("Tolerance cannot be negative")

    if source == 0:
        return target == 0

    return abs(target - source) / source <= tolerance_fraction


def test_exact_match():
    assert reconcile_counts(100, 100)


def test_missing_records_fail():
    assert not reconcile_counts(100, 90)


def test_relative_tolerance():
    assert reconcile_counts(1000, 998, tolerance_fraction=0.005)


def test_zero_to_zero_passes():
    assert reconcile_counts(0, 0)


def test_zero_to_positive_fails():
    assert not reconcile_counts(0, 10)


def test_negative_count_rejected():
    with pytest.raises(ValueError):
        reconcile_counts(-1, 0)
```

## Equal-count substitution test

This is important:

```python
def test_equal_counts_do_not_prove_identity():
    source_ids = {"A", "B", "C", "D"}
    target_ids = {"A", "B", "C", "X"}

    assert len(source_ids) == len(target_ids)
    assert source_ids != target_ids
```

---

## 35. Defect Injection

Defect injection turns reconciliation from a theoretical topic into an engineering skill.

Create a synthetic source dataset and intentionally introduce failures.

## Defect 1 — Delete 10% of target records

Expected detection:

```text
count mismatch
key mismatch
```

## Defect 2 — Add unexpected records

Expected detection:

```text
target-only keys
count mismatch
```

## Defect 3 — Duplicate an entire batch

Expected detection:

```text
count mismatch
duplicate batch ID
duplicate keys
```

## Defect 4 — Replace records while preserving row count

Expected detection:

```text
count check → MISS
key reconciliation → CATCH
```

This demonstrates why row counts are insufficient.

## Defect 5 — Move records to the wrong partition

Expected detection:

```text
global count → possibly PASS
partition reconciliation → CATCH
```

## Defect 6 — Corrupt one financial aggregate

Expected detection:

```text
count → PASS
key set → PASS
aggregate reconciliation → CATCH
```

## Defect 7 — Skip one API page

Expected detection:

```text
page audit
API total
count reconciliation
```

## Defect 8 — Replay a batch

Expected detection:

```text
batch identity
duplicate keys
count increase
```

## Defect 9 — Legitimate transformation count difference

Example:

```text
1,000 source
→ 700 target
```

with an explicit cancellation filter.

Expected result:

```text
PASS under transformation-aware rule
```

## Defect 10 — Late-arriving data

Initial:

```text
source = 1,000
target = 950
```

Later:

```text
source = 1,000
target = 1,000
```

Expected classification:

```text
PROVISIONAL → PASS
```

---

## 36. Debugging Reconciliation Failures

Use a systematic workflow.

```text
1. Detect mismatch
2. Verify audit calculation
3. Verify source snapshot/time
4. Verify target snapshot/time
5. Compare row counts
6. Compare partitions
7. Compare keys
8. Identify missing records
9. Identify unexpected records
10. Check duplicates
11. Compare aggregates
12. Inspect transformation logic
13. Inspect retries/replays
14. Inspect upstream failures
15. Determine root cause
16. Decide recovery
17. Reconcile again
18. Close the incident
```

## Step 1 — Verify the check itself

A broken reconciliation calculation can create a false incident.

Verify:

- query
- filters
- timezone
- parameters
- dataset names
- join condition
- snapshot

## Step 2 — Verify time

Ask:

```text
Were source and target measured for the same logical window?
```

## Step 3 — Narrow by partition

Find:

```text
which date?
which hour?
which region?
which source?
```

## Step 4 — Compare keys

Determine:

```text
missing IDs
unexpected IDs
duplicates
```

## Step 5 — Compare aggregates

Look for:

```text
amount
quantity
tax
status
```

differences.

## Step 6 — Inspect transformation

Check:

- filters
- joins
- deduplication
- aggregation
- null handling
- partition assignment

## Step 7 — Inspect operational history

Check:

- retries
- failed writes
- timeouts
- API errors
- partial file arrival
- orchestration failures

## Step 8 — Decide recovery

Possible actions:

```text
retry
replay
backfill
partition reload
full reload
deduplication
correction
manual intervention
```

## Step 9 — Reconcile again

Recovery is incomplete until the resulting data passes the required reconciliation.

---

## 37. Recovery

## Retry

Use when the operation failed transiently and is idempotent or otherwise safe to repeat.

## Replay

Reprocess a known source batch.

Requires careful duplicate prevention.

## Backfill

Reprocess a historical window.

Useful for late data or corrected source records.

## Partial Reload

Reload only affected records.

Useful when affected keys are known.

## Partition Reload

Reload one broken date/hour/region partition.

Often much cheaper than a full reload.

## Full Reload

Appropriate when:

- corruption is widespread
- incremental recovery cannot be trusted
- source is authoritative and reload is safe

## Deduplication

Remove duplicate effects while preserving correct records.

## Correction

Apply a controlled data fix where business policy permits.

## Manual Intervention

Use only when automation cannot safely resolve the situation.

Recovery must preserve:

- audit history
- run IDs
- reproducibility
- idempotency

---

## 38. Mini Project — Production Data Reconciliation System

Build a complete reconciliation system around synthetic orders.

## Dataset

Create:

```text
source_orders
target_orders
```

Fields:

```text
order_id
customer_id
order_timestamp
status
quantity
amount
region
```

## Layer 1 — Count reconciliation

Calculate:

- source count
- target count
- difference
- percentage difference

## Layer 2 — Key reconciliation

Calculate:

- missing IDs
- unexpected IDs
- duplicate IDs

## Layer 3 — Aggregate reconciliation

Calculate:

- total quantity
- total amount
- distinct customers

## Layer 4 — Partition reconciliation

Compare:

- daily count
- regional count

## Layer 5 — Hash reconciliation

Create a deterministic record hash and compare mismatches.

## Layer 6 — Audit record

Produce a structured result:

```json
{
  "run_id": "run-001",
  "dataset": "orders",
  "source_count": 10000,
  "target_count": 9980,
  "missing_records": 20,
  "unexpected_records": 0,
  "duplicate_records": 0,
  "status": "FAIL"
}
```

## Layer 7 — Decision

Classify:

```text
PASS
WARNING
FAIL
BLOCK
```

### Suggested implementation skeleton

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ReconciliationResult:
    run_id: str
    dataset: str
    source_count: int
    target_count: int
    missing_records: int
    unexpected_records: int
    duplicate_records: int
    quantity_difference: int
    amount_difference: Decimal
    status: str


def reconcile_orders(
    *,
    run_id: str,
    source_count: int,
    target_count: int,
    missing_records: int,
    unexpected_records: int,
    duplicate_records: int,
    source_quantity: int,
    target_quantity: int,
    source_amount: Decimal,
    target_amount: Decimal,
) -> ReconciliationResult:
    quantity_difference = target_quantity - source_quantity
    amount_difference = target_amount - source_amount

    if (
        source_count == target_count
        and missing_records == 0
        and unexpected_records == 0
        and duplicate_records == 0
        and quantity_difference == 0
        and amount_difference == Decimal("0.00")
    ):
        status = "PASS"
    else:
        status = "FAIL"

    return ReconciliationResult(
        run_id=run_id,
        dataset="orders",
        source_count=source_count,
        target_count=target_count,
        missing_records=missing_records,
        unexpected_records=unexpected_records,
        duplicate_records=duplicate_records,
        quantity_difference=quantity_difference,
        amount_difference=amount_difference,
        status=status,
    )
```

This is an educational core. A production implementation would add configuration, persistence, logging, metrics, security, retries, and operational controls.

---

## 39. Advanced Production Project

Extend the mini-project into a production-style reconciliation service.

Add:

- partition-aware reconciliation
- incremental reconciliation
- audit table
- tolerance configuration
- late-arriving data
- run IDs
- historical reconciliation results
- alerting
- retry/replay handling
- idempotency
- automated defect injection
- pytest suite
- performance measurement

## Scaling from 1 million to 1 billion+ rows

At 1 million rows, a full key comparison may be inexpensive.

At 1 billion rows, the same design may become operationally expensive.

### At larger scale

Prefer:

```text
partition pruning
      +
incremental scope
      +
precomputed metrics
      +
distributed aggregation
      +
key-range reconciliation
      +
targeted deep comparison
```

### Example architecture

```text
1B-row dataset
      |
      v
partition metadata
      |
      v
cheap count/aggregate checks
      |
      +---- PASS → record evidence
      |
      +---- mismatch
               |
               v
         narrow partition
               |
               v
         key comparison
               |
               v
         affected ranges
               |
               v
        record-level checks
```

The expensive checks should be targeted rather than performed unnecessarily over the entire population.

---

## 40. Production Scenarios

## Scenario 1 — Equal Counts, Wrong Records

```text
Source = 1,000,000
Target = 1,000,000
```

But 10,000 records were replaced.

### How do you detect it?

A count check cannot.

Use:

- key-level comparison
- deterministic hashes
- business aggregates
- field-level comparison where necessary

The correct lesson is:

```text
equal counts ≠ equal data
```

---

## Scenario 2 — Missing Partition

All partitions reconcile except:

```text
2026-09-30
```

### Investigation

1. Compare the partition count.
2. Identify the source batch/run for that date.
3. Inspect file/API/database extraction metadata.
4. Inspect target write status.
5. Check orchestration logs.
6. Check whether the partition is late rather than missing.
7. Reload only the affected partition if safe.
8. Reconcile again.

---

## Scenario 3 — Duplicate Replay

A failed pipeline retries and loads the same batch twice.

### Detection

Look for:

- duplicate batch ID
- duplicate keys
- unexpected count increase
- repeated source extract ID

### Root cause

A retry was not idempotent.

#### Recovery

- stop further duplicate effects
- identify duplicate load
- remove or compensate for duplicate records
- replay safely
- reconcile

### Prevention

- idempotency key
- load ledger
- unique constraint where appropriate
- run/batch tracking

---

## Scenario 4 — Late Data

Source eventually contains:

```text
1,000,000
```

but at initial reconciliation target has:

```text
950,000
```

### Correct interpretation

Do not immediately classify this as permanent data loss.

Ask:

```text
Is the reconciliation window still open?
```

If yes:

```text
PROVISIONAL
```

If the grace period expires:

```text
FAIL / INVESTIGATE
```

---

## Scenario 5 — Legitimate Filter

Source:

```text
1,000,000
```

Target:

```text
700,000
```

because the contract explicitly filters cancelled records.

Naive rule:

```text
target == source
```

would fail incorrectly.

Correct rule:

```text
target = expected eligible source population
```

The reconciliation must use the transformation contract.

---

## Scenario 6 — Financial Mismatch

Counts match, but total amount differs.

Investigation:

1. Compare total amount.
2. Compare by partition/date.
3. Compare by transaction ID.
4. Look for missing records.
5. Look for duplicate records.
6. Compare refunds/reversals.
7. Verify currency.
8. Verify decimal precision.
9. Check transformation logic.
10. Determine whether the mismatch is expected or an incident.

---

## 41. Interview Questions

## Basic — 10 Questions

### 1. What is data reconciliation?

**Answer:** It is the controlled comparison of expected and observed data across system or pipeline boundaries to establish whether data moved correctly.

### 2. What is a row-count audit?

**Answer:** A check comparing record counts at two boundaries or against an expected count.

### 3. Why is row-count equality insufficient?

**Answer:** Different records can produce the same count. Equal counts can hide missing records, unexpected records, duplicates, or substitutions.

### 4. What is a missing record?

**Answer:** A record present in the source comparison population but absent from the target.

### 5. What is an unexpected record?

**Answer:** A record present in the target comparison population but absent from the source comparison population.

### 6. How do validation and reconciliation differ?

**Answer:** Validation asks whether data satisfies structural or business rules; reconciliation asks whether expected data moved correctly across a boundary.

### 7. Why do keys matter?

**Answer:** Keys provide record identity, allowing reconciliation to determine whether the same records exist on both sides.

### 8. What is an anti-join?

**Answer:** A query pattern that returns rows from one side with no matching key on the other side.

### 9. What is duplicate detection?

**Answer:** Identifying repeated records or repeated identifiers where uniqueness is expected.

### 10. What is an audit trail?

**Answer:** Durable evidence describing what was checked, when, against which data, using which rule, and with what result.

---

## Moderate — 10 Questions

### 11. How would you reconcile source and target counts?

**Answer:** Capture both counts for the same logical scope, calculate the difference, apply the documented expectation/tolerance, and persist the result.

### 12. How do you find missing records in SQL?

**Answer:** Use a left anti-join pattern:

```sql
SELECT s.order_id
FROM source.orders s
LEFT JOIN target.orders t
  ON s.order_id = t.order_id
WHERE t.order_id IS NULL;
```

### 13. Why reconcile aggregates?

**Answer:** Row counts can match while important business values differ.

### 14. When would partition reconciliation help?

**Answer:** When a global check shows a mismatch and you need to identify where the mismatch occurred, or when correctness is inherently partition-specific.

### 15. What is a reconciliation tolerance?

**Answer:** A documented range of acceptable difference based on system or business semantics.

### 16. Why can tolerances be dangerous?

**Answer:** An excessive tolerance can hide real data loss or corruption.

### 17. What should an audit table contain?

**Answer:** At minimum, run identity, dataset, source/target measurements, differences, status, and timestamp; production systems often add versions, partitions, snapshots, severity, and remediation metadata.

### 18. How do you reconcile an API?

**Answer:** Compare API-reported totals with received records while tracking pagination, pages/tokens, retries, failures, and extraction metadata.

### 19. How do you reconcile files?

**Answer:** Compare manifests, expected file count, actual file count, record counts, partitions, file sizes where useful, and checksums.

### 20. Why should financial reconciliation use Decimal?

**Answer:** Decimal arithmetic avoids many binary floating-point representation problems and provides explicit monetary precision.

---

## Hard — 10 Questions

### 21. How would you reconcile a billion-row table?

**Answer:** Use partition-aware and incremental reconciliation, precomputed aggregates, distributed processing, metadata checks, and targeted deep comparison rather than repeatedly performing an unrestricted full-table join.

### 22. What is deterministic hashing?

**Answer:** It means logically equivalent records are converted into the same canonical representation before hashing so that the resulting fingerprint is reproducible.

### 23. Why is canonicalization necessary?

**Answer:** Different representations of equivalent values can produce different hashes.

### 24. How do late-arriving records affect reconciliation?

**Answer:** Immediate comparison may report a temporary mismatch. The system needs event-time semantics, grace periods, watermarks, or provisional/final reconciliation states.

### 25. What is snapshot consistency?

**Answer:** The source and target measurements represent compatible logical points in time. Without this, legitimate concurrent changes can appear as mismatches.

### 26. How should filtering affect reconciliation?

**Answer:** The expected target population should be derived from the documented filter semantics rather than requiring source and target counts to match.

### 27. How can an incorrect join cause reconciliation failures?

**Answer:** A wrong join can drop records, duplicate rows, or associate the wrong attributes. Key-level and aggregate checks can expose these effects.

### 28. When is a full reconciliation preferable?

**Answer:** When the dataset is manageable, risk is high, the source is authoritative, or periodic full verification is needed to validate incremental controls.

### 29. What is incremental reconciliation?

**Answer:** Reconciliation limited to the changed or newly processed scope using partitions, high-water marks, CDC, or similar mechanisms.

### 30. Why can a checksum mismatch be difficult to debug?

**Answer:** A checksum tells you that canonical representations differ but not which records or fields caused the difference.

---

## Advanced — 10 Questions

### 31. How would you reconcile a distributed pipeline where source and target cannot be queried simultaneously?

**Answer:** Establish explicit extraction or snapshot boundaries, persist source-side measurements, attach immutable run/extract identifiers, and compare target results against that recorded source state.

### 32. How do you reconcile streaming data?

**Answer:** Define windows and event-time semantics, track producer/consumer offsets, lag, watermarks, late events, duplicate IDs, and finalization rules rather than comparing constantly changing global totals.

### 33. How would you control reconciliation cost at billion-row scale?

**Answer:** Push checks toward metadata and partition level first, reconcile incrementally, compute aggregates during ingestion where practical, use targeted key comparisons, and reserve full record comparison for high-risk or affected scopes.

### 34. What is effectively-once processing?

**Answer:** A design where retries may occur internally, but the externally visible outcome behaves as though each logical event were applied once.

### 35. How do you reconcile a replay-safe pipeline?

**Answer:** Track logical batch identity, make writes idempotent, detect repeated batch IDs, compare key uniqueness, and retain audit history linking attempts to outcomes.

### 36. How would you design reconciliation SLOs?

**Answer:** Define measurable expectations such as reconciliation completion time, pass rate, unresolved failure duration, and critical mismatch detection latency, then assign them according to dataset criticality.

### 37. How would you reconcile a transformation that intentionally changes row count?

**Answer:** Define the transformation contract, identify the expected population relationship, and reconcile semantic metrics rather than using raw row equality.

### 38. How do you distinguish a late-data mismatch from data loss?

**Answer:** Compare against the documented event-time/reconciliation window, inspect watermarks and ingestion progress, and perform final reconciliation after the grace period.

### 39. How do you debug equal-count substitutions?

**Answer:** Move from counts to key sets, then deterministic hashes or field-level comparisons, and inspect the transformation path for replacement or join errors.

### 40. What makes a reconciliation system production-grade?

**Answer:** Explicit rules, stable identity, consistent snapshots, audit persistence, observability, tolerances grounded in contracts, scalable execution, testing, recovery, idempotency, and historical evidence.

---

## 42. System Design / Architecture Questions

## 1. Design reconciliation for a 5 TB daily ingestion pipeline.

### Requirements

- detect missing data
- minimize scan cost
- identify broken partitions
- retain audit history

### Assumptions

- data is partitioned by event date
- source provides batch IDs
- target supports partition pruning

### Architecture

```text
source manifest
      ↓
source audit
      ↓
partitioned ingestion
      ↓
target audit
      ↓
partition reconciliation
      ↓
aggregate checks
      ↓
targeted key reconciliation
```

### Metrics

- source/target count
- partition difference
- missing key count
- aggregate difference
- reconciliation duration

### Failure modes

- missing partition
- duplicate partition
- partial file arrival
- late data

#### Recovery

- partition reload
- replay
- backfill

---

## 2. Design source-to-warehouse reconciliation for 1 billion records.

Use:

- incremental scope
- partition pruning
- source snapshots
- batch IDs
- precomputed aggregates
- distributed key reconciliation
- targeted deep comparison

Avoid an unrestricted full-table join for every run.

---

## 3. Design reconciliation for an API with paginated responses.

Track:

```text
request ID
page/token
pages requested
pages received
API total
records received
retry count
HTTP errors
```

Detect:

- skipped page
- repeated page
- partial response
- changing source population

---

## 4. Design reconciliation for a multi-file S3/Parquet batch.

Use a manifest containing:

```text
file
partition
record_count
size
checksum
schema_version
```

Compare the manifest with observed files and loaded records.

---

## 5. Design streaming producer-consumer reconciliation.

Track:

```text
topic/stream
partition
producer offset
consumer committed offset
event ID
watermark
lag
duplicate count
```

Reconcile over event-time windows rather than relying only on global counts.

---

## 6. Design a reconciliation audit store.

Store:

```text
run_id
dataset
source_system
target_system
source_snapshot
target_snapshot
partition
rule
source_metrics
target_metrics
difference
status
severity
checked_at
remediation_status
```

Partition/cluster the audit store according to its access patterns.

---

## 7. Design incremental reconciliation for CDC.

Use:

```text
source commit position
target applied position
change count
operation type
key
run ID
```

Reconcile both:

```text
change volume
```

and:

```text
applied business state
```

where required.

---

## 8. Design reconciliation when source and target cannot be queried simultaneously.

Use a persisted source extract or source snapshot metadata.

```text
source snapshot
      ↓
source audit artifact
      ↓
pipeline
      ↓
target
      ↓
target audit
      ↓
reconcile recorded source evidence
```

---

## 9. Design reconciliation with late-arriving data.

Use:

```text
provisional result
      ↓
grace period
      ↓
watermark/finalization
      ↓
final reconciliation
```

Do not page on every provisional mismatch.

---

## 10. Design reconciliation for financial transactions.

Use:

- immutable transaction IDs
- Decimal arithmetic
- count reconciliation
- amount reconciliation
- duplicate detection
- currency-aware logic
- reversal/refund handling
- partition reconciliation
- audit history
- strict recovery controls

Financial reconciliation should favor explicit evidence and conservative failure handling.

---

## 43. Final Practical Challenge

Design and solve a synthetic reconciliation exercise containing:

- exact matches
- missing records
- unexpected records
- duplicate records
- equal-count substitutions
- partition mismatches
- aggregate mismatches
- late-arriving data
- legitimate filtering
- aggregation
- API pagination failure
- replay duplication

## Dataset A — source observations

```text
batch-001
orders: 10,000
amount: 1,000,000
partitions:
  2026-09-28: 3,000
  2026-09-29: 3,500
  2026-09-30: 3,500
```

## Dataset B — target observations

```text
batch-001
orders: 9,990
amount: 998,000
partitions:
  2026-09-28: 3,000
  2026-09-29: 3,500
  2026-09-30: 3,490
```

Additional facts:

```text
5 source IDs are missing
5 unexpected IDs exist
10 target records contain duplicate business keys
```

### Your tasks

1. Identify which reconciliation method applies.
2. Calculate the count difference.
3. Calculate the percentage difference.
4. Determine whether the count check passes under a 0.1% tolerance.
5. Identify the partition mismatch.
6. Explain why aggregate reconciliation fails.
7. Determine whether duplicate detection changes the diagnosis.
8. Decide whether the mismatch is expected or a defect.
9. Identify likely root causes.
10. Choose a recovery strategy.
11. Design a production control to prevent recurrence.
12. Explain which evidence should remain in the audit store.

### Extension

Add a late-arriving partition and a legitimate cancellation filter. Recalculate the expected target population instead of assuming source and target counts must match.

---

## 44. Common Mistakes

## Mistake 1 — Assuming equal row counts prove equality

They do not.

## Mistake 2 — Ignoring keys

Without identity, you cannot reliably detect substitutions.

## Mistake 3 — Ignoring duplicates

A duplicate can preserve total row count while changing the population.

## Mistake 4 — Reconciling different snapshots

Concurrent source changes can create false mismatches.

## Mistake 5 — Comparing before late data settles

A temporary mismatch can become a false incident.

## Mistake 6 — Using arbitrary tolerances

Tolerance must have documented semantics.

## Mistake 7 — Using floating-point values for financial reconciliation

Use explicit decimal arithmetic.

## Mistake 8 — Ignoring partitions

Global metrics can hide localized failures.

## Mistake 9 — Comparing full tables unnecessarily

Use a layered strategy.

## Mistake 10 — Failing to record audit metadata

Without evidence, incident investigation becomes guesswork.

## Mistake 11 — Not tracking run IDs

You need to know which execution produced which result.

## Mistake 12 — Ignoring transformation semantics

A filter or aggregation can legitimately change row counts.

## Mistake 13 — Treating every count difference as an error

The expected relationship depends on the transformation contract.

## Mistake 14 — Failing to detect equal-count substitutions

Always use stronger controls when business risk requires them.

## Mistake 15 — No recovery mechanism

Detection without recovery leaves operations incomplete.

## Mistake 16 — No idempotency

Retries can create duplicate effects.

## Mistake 17 — No historical audit trail

You lose the ability to investigate recurring failures.

## Mistake 18 — No automated tests

Reconciliation logic itself can contain bugs.

---

## 45. Practical Production Checklist

## Identity

- [ ] Stable business key identified
- [ ] Duplicate policy defined
- [ ] Composite key understood
- [ ] Key uniqueness assumptions documented

## Counts

- [ ] Source count captured
- [ ] Target count captured
- [ ] Expected count defined
- [ ] Difference calculated
- [ ] Tolerance documented

## Records

- [ ] Missing keys detected
- [ ] Unexpected keys detected
- [ ] Duplicates detected
- [ ] Equal-count substitutions detectable where required

## Aggregates

- [ ] Important sums checked
- [ ] Counts checked
- [ ] Distinct counts checked
- [ ] Financial metrics reconciled where relevant

## Partitions

- [ ] Partition counts captured
- [ ] Partition completeness checked
- [ ] Broken partitions identifiable

## Timing

- [ ] Snapshot semantics defined
- [ ] Late-data policy defined
- [ ] Reconciliation window defined
- [ ] Watermark/finalization policy defined where applicable

## Audit

- [ ] Run ID recorded
- [ ] Source metrics recorded
- [ ] Target metrics recorded
- [ ] Reconciliation status recorded
- [ ] Failure reason recorded
- [ ] Historical audit retained

### Recovery

- [ ] Retry strategy defined
- [ ] Replay strategy defined
- [ ] Backfill strategy defined
- [ ] Partition reload strategy defined
- [ ] Idempotency guaranteed

## Operations

- [ ] Metrics emitted
- [ ] Alerts configured
- [ ] Dashboard available
- [ ] Ownership defined
- [ ] Incident workflow defined

---

## 46. Code Quality Requirements

All Python examples in this chapter should follow these principles:

- Python 3.x
- syntactically valid code
- runnable with minimal modification
- clear names
- type hints where useful
- explicit edge-case handling
- no hidden assumptions
- timezone-aware datetimes in production examples
- `Decimal` for monetary calculations where appropriate
- explanation of important lines
- clear distinction between educational code and production architecture

A small example can be simple:

```python
source_count == target_count
```

A production implementation may additionally need:

```text
configuration
logging
metrics
persistence
retries
idempotency
auditability
alerting
security
scalability
testing
```

---

## 47. SQL Quality Requirements

Good reconciliation SQL should be:

- readable
- properly formatted
- explicit about joins
- explicit about NULL behavior
- mindful of duplicate multiplication
- mindful of snapshot consistency
- appropriate for large datasets where possible

Use PostgreSQL-compatible SQL when a concrete dialect is required.

### Duplicate multiplication example

Suppose:

```text
source:
A
A

target:
A
```

A join on `A` can produce multiple output rows.

Therefore, always understand the expected grain before interpreting a join-based reconciliation result.

---

## 48. Beginner-Friendly Mathematics

The important formulas are simple once the intuition is clear.

## Difference

\[
difference = target - source
\]

Example:

```text
source = 100
target = 97

difference = 97 - 100
           = -3
```

Interpretation:

```text
3 fewer target rows
```

## Absolute difference

\[
|target-source|
\]

Example:

```text
|-3| = 3
```

## Percentage difference

\[
\frac{|target-source|}{source}\times100
\]

Example:

```text
source = 1,000
target = 950

difference = 50

50 / 1,000 × 100
= 5%
```

## Absolute tolerance

\[
|target-source| \le tolerance
\]

## Relative tolerance

\[
\frac{|target-source|}{source}\le tolerance
\]

The important production question is not only:

```text
"What is the formula?"
```

but:

```text
"What does the result mean for this data contract?"
```

---

## 49. Production vs Educational Code

## Educational Example

```python
source_count = 1000
target_count = 998

assert source_count == target_count
```

This teaches the concept.

## Production Considerations

A production reconciliation system may need:

```text
configuration
logging
metrics
persistent audit records
snapshot identifiers
run IDs
retry controls
idempotency
alerts
access controls
data masking
partition-aware execution
historical retention
testing
recovery
```

The difference is not that the simple example is "wrong."

It is that production systems must account for operational reality.

---

## 50. Production Reconciliation Design Pattern

A useful layered design is:

```text
Layer 1
Cheap volume/count check
        ↓
Layer 2
Partition/coverage check
        ↓
Layer 3
Key-set check
        ↓
Layer 4
Aggregate/business-metric check
        ↓
Layer 5
Hash/field comparison
        ↓
Layer 6
Audit evidence
        ↓
Layer 7
Decision + recovery
```

Not every dataset needs every layer.

The design should be proportional to:

```text
business criticality
+
failure cost
+
data volume
+
system characteristics
+
reconciliation cost
```

---

## 51. Final Mental Model

Remember the progression:

```text
Row-count audit asks:
"Did approximately the expected number of records arrive?"

Key reconciliation asks:
"Did the expected records arrive?"

Aggregate reconciliation asks:
"Did the important business totals remain consistent?"

Partition reconciliation asks:
"Where exactly is the mismatch?"

Hash reconciliation asks:
"Does the deterministic representation of the data match?"

Audit logging asks:
"Can we prove what happened?"

Production reconciliation asks:
"Is this mismatch expected, temporary, tolerable, or a real incident—and what should we do next?"
```

The central principle is:

> **Reconciliation is not simply comparing two row counts. It is a controlled process for proving that data moved correctly across system boundaries, detecting missing/extra/duplicate/incorrect data, understanding expected transformation differences, preserving audit evidence, and supporting safe recovery.**

---

## 52. Completion Criteria

You should consider this topic complete when you can explain and implement all of the following without relying on a single `COUNT(*)` check:

- [ ] validation vs reconciliation
- [ ] row-count audits
- [ ] equal counts vs equal data
- [ ] stable record identity
- [ ] set-based reconciliation
- [ ] pandas reconciliation
- [ ] SQL reconciliation
- [ ] aggregate reconciliation
- [ ] financial reconciliation
- [ ] deterministic hashing
- [ ] canonicalization
- [ ] partition reconciliation
- [ ] run/batch reconciliation
- [ ] audit tables
- [ ] tolerance-based reconciliation
- [ ] late-arriving data
- [ ] duplicate/replay detection
- [ ] idempotency
- [ ] incremental reconciliation
- [ ] transformation-aware reconciliation
- [ ] API reconciliation
- [ ] file reconciliation
- [ ] database reconciliation
- [ ] lake/warehouse/lakehouse reconciliation
- [ ] streaming reconciliation
- [ ] failure classification
- [ ] decision policies
- [ ] production architecture
- [ ] observability
- [ ] performance/cost trade-offs
- [ ] testing
- [ ] defect injection
- [ ] debugging
- [ ] recovery
- [ ] mini-project
- [ ] advanced production design
- [ ] interview reasoning
- [ ] architecture reasoning

Most importantly, understand both:

```text
WHY reconciliation exists
```

and:

```text
HOW to build production-grade reconciliation systems
```

The learner should finish this chapter capable of designing, implementing, testing, debugging, and explaining reconciliation and row-count auditing systems in real production Data Engineering environments.
