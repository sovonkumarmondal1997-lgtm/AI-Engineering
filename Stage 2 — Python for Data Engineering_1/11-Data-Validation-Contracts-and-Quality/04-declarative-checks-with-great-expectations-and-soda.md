# Declarative Checks with Great Expectations and Soda

> **Stage 2 — Python for Data Engineering**  
> **Module 2.11 — Data Validation, Contracts, and Quality**  
> **Topic 04**
>
> This chapter treats declarative data quality as an engineering discipline: define the rule, execute it, inspect the result, decide what happens, retain evidence, and operate the system over time.

---

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain why declarative data-quality checks exist.
- Distinguish declarative rule definition from imperative validation code.
- Explain the conceptual model of Great Expectations (GX).
- Explain the conceptual model of Soda and SodaCL.
- Define practical expectations/checks for schema, completeness, uniqueness, validity, volume, freshness, and business invariants.
- Use thresholds and severity deliberately.
- Turn validation results into pipeline quality gates.
- Validate data in DataFrames, Parquet, DuckDB, and PostgreSQL.
- Write custom SQL checks when generic checks are insufficient.
- Understand validation results as operational evidence rather than just pass/fail output.
- Store historical quality results and use them for trend analysis.
- Compare Pandera, Great Expectations, Soda, SQL, and database constraints without treating any as universally superior.
- Design maintainable quality rules with ownership, IDs, documentation, tests, and version controls.
- Recognize tool churn and avoid unnecessary framework proliferation.
- Debug failed or ineffective checks.
- Design a production-grade declarative quality gate.

---

## Prerequisites

You should already understand:

- Python fundamentals.
- Basic pandas/DataFrame concepts.
- Basic SQL.
- Basic relational database concepts.
- The quality dimensions from Topic 01.
- Pydantic record validation from Topic 02.
- Pandera DataFrame validation from Topic 03.

The goal here is not to repeat those topics. Instead, we move from **local validation** toward **declarative, repeatable, operational quality systems**.

---

# 1. Why Declarative Data Quality Exists

## 1.1 Start with the problem

Suppose an orders pipeline receives this data:

| order_id | customer_id | quantity | currency | total_amount |
|---|---|---:|---|---:|
| 1001 | C001 | 2 | USD | 40 |
| 1002 | C002 | 1 | EUR | 25 |
| 1003 | NULL | 3 | USD | 75 |
| 1003 | C004 | -1 | XYZ | -20 |

A Python program can certainly inspect this data:

```python
if orders["customer_id"].isna().any():
    raise ValueError("customer_id contains nulls")

if orders["order_id"].duplicated().any():
    raise ValueError("duplicate order_id")

if not orders["currency"].isin({"USD", "EUR", "GBP", "INR"}).all():
    raise ValueError("invalid currency")
```

This works.

The engineering problem begins when a platform has hundreds of datasets and thousands of quality rules.

Scattered validation code tends to produce:

- duplicated logic,
- inconsistent severity,
- inconsistent naming,
- difficult reporting,
- difficult historical analysis,
- difficult ownership,
- difficult operationalization,
- difficult cross-system checks,
- poor visibility into quality trends,
- SQL checks separated from Python validation,
- framework-specific behavior scattered throughout pipelines.

The deeper problem is that **the business rule becomes hidden inside implementation code**.

A production quality system should make the rule itself visible.

For example:

```text
order_id must be unique
currency must be one of USD/EUR/GBP/INR
quantity must be greater than zero
null customer_id rate must be <= 1%
latest order must be within the freshness SLA
```

The important question becomes:

> **What must be true about this dataset?**

rather than:

> **How do I manually write Python that happens to detect it?**

---

## 1.2 The progression

The learning progression is:

```text
Plain DataFrame
    ↓
Pandera schema validation
    ↓
Declarative quality checks
    ↓
Pipeline quality gates
    ↓
Historical quality monitoring
    ↓
Organization-wide data-quality system
```

Each layer solves a different problem.

### Plain DataFrame

Useful for exploration and transformation.

### Pandera

Useful for expressing DataFrame structure and constraints close to Python transformations.

### Declarative checks

Useful for representing quality rules in a standardized validation system.

### Quality gates

Turn validation results into pipeline decisions.

### Historical monitoring

Makes quality measurable over time.

### Organization-wide systems

Add ownership, reporting, governance, operational workflows, and shared conventions.

---

# 2. What Does "Declarative" Mean?

## 2.1 Imperative thinking

Imperative code tells the computer **how** to perform a procedure.

For example:

```python
invalid_rows = []

for row in rows:
    if row["quantity"] <= 0:
        invalid_rows.append(row)

if invalid_rows:
    raise ValueError("Invalid quantity")
```

The implementation describes the procedure.

## 2.2 Declarative thinking

Declarative validation describes **what must be true**.

```text
quantity must be greater than 0
```

The validation engine is responsible for evaluating that rule.

A declarative system separates:

```text
Rule definition
      ↓
Execution engine
      ↓
Result
      ↓
Severity
      ↓
Action
      ↓
Reporting
```

This separation is one of the major reasons declarative systems become useful at scale.

---

## 2.3 A simple analogy

Consider a building inspection.

You do not want every inspector inventing a completely different inspection process.

Instead, you define requirements:

```text
Fire exits must be accessible.
Emergency lighting must work.
Electrical panels must satisfy required conditions.
```

An inspection system then evaluates those requirements and records the findings.

Data-quality checks follow the same broad model.

---

# 3. What Is a Data Quality Check?

A quality check can be modeled as:

```text
Dataset
    +
Target
    +
Condition
    +
Threshold
    +
Observed result
    +
Severity
    +
Action
    +
Metadata
```

For example:

```text
Dataset:
    orders

Rule:
    order_id must be unique

Observed:
    99.97% unique

Expected:
    100% unique

Severity:
    CRITICAL

Action:
    block publication
```

Common rules include:

- a column must exist,
- a column must not be null,
- values must be unique,
- values must belong to an allowed set,
- values must satisfy a range,
- row count must remain above a minimum,
- a dataset must be fresh enough,
- a SQL condition must return zero violating rows.

Different tools use different terminology.

### Great Expectations

The central term is **expectation**.

### Soda

The central terms are **checks** and **SodaCL checks**.

These concepts overlap, but their APIs and configuration models are not identical.

---

# 4. Data Quality Dimensions Recap

Topic 01 introduced dimensions such as:

- completeness,
- validity,
- uniqueness,
- consistency,
- accuracy,
- timeliness/freshness,
- integrity.

Declarative checks turn those concepts into executable rules.

| Dimension | Example executable rule |
|---|---|
| Completeness | `customer_id IS NOT NULL` |
| Uniqueness | `order_id` has no duplicates |
| Validity | `currency IN ('USD', 'EUR', 'GBP', 'INR')` |
| Freshness | latest event is within the SLA |
| Integrity | every order references an existing customer |
| Consistency | `total_amount = quantity * unit_price` |

A check is therefore an **executable representation of a quality rule**.

The check does not magically prove that the data is correct. It proves that a particular rule was evaluated and produced a particular result.

---

# 5. Great Expectations — Conceptual Model

## 5.1 What is Great Expectations?

Great Expectations (GX) is a data-quality validation framework built around explicit expectations about data.

At a conceptual level:

```text
Data source
    ↓
Data asset
    ↓
Data selection / batch-like data unit
    ↓
Expectations
    ↓
Validation
    ↓
Validation results
    ↓
Documentation / reporting / action
```

The exact APIs and terminology can change between GX releases, so production work should always begin by checking the installed version and its current documentation.

The durable engineering concepts are more important than memorizing a historical API.

---

## 5.2 Major concepts

Depending on the GX version and workflow in use, you may encounter concepts such as:

- data sources,
- data assets,
- batches or batch-like data selections,
- expectations,
- expectation suites or current equivalents,
- validation,
- validation results,
- checkpoints or current execution workflow equivalents,
- documentation,
- metadata.

The important architecture is:

```text
WHAT SHOULD BE TRUE?
        ↓
EXPECTATIONS
        ↓
RUN VALIDATION
        ↓
WHAT ACTUALLY HAPPENED?
        ↓
VALIDATION RESULT
```

---

## 5.3 Why version awareness matters

Data-quality frameworks evolve.

A tutorial written for an older release can contain:

- removed APIs,
- renamed concepts,
- obsolete configuration,
- changed execution workflows.

Therefore:

```bash
python -c "import great_expectations as gx; print(gx.__version__)"
```

should be one of the first diagnostic commands when working in an existing environment.

Do not assume a code sample is current merely because it appears in a blog post or video.

---

# 6. Great Expectations Installation

Use the package-management convention already established by your project.

A generic installation command is:

```bash
python -m pip install great-expectations
```

Then inspect the installed version:

```bash
python -c "import great_expectations as gx; print(gx.__version__)"
```

For production environments, prefer a pinned dependency strategy.

For example, a project may pin dependencies through its package manager rather than relying on:

```text
latest
```

The exact version should be selected and tested by the project rather than fabricated in training material.

### Why pinning matters

Without controlled versions:

```text
pipeline today
    ↓
dependency upgrade
    ↓
API/behavior change
    ↓
validation failures
    ↓
pipeline outage
```

Version management is therefore part of quality-system reliability.

---

# 7. Your First Great Expectations Check

> **Version note:** The exact GX Python API varies by release. The following example illustrates the validation model and should be adapted to the installed release rather than copied blindly into production.

Consider:

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "order_id": [1001, 1002, 1003],
        "customer_id": ["C001", "C002", "C003"],
        "quantity": [2, 1, 3],
        "unit_price": [20.0, 25.0, 15.0],
        "currency": ["USD", "EUR", "INR"],
    }
)
```

The business rules are:

```text
order_id must exist
customer_id must not be null
order_id must be unique
currency must be allowed
quantity must be positive
```

Conceptually, an expectation suite might contain rules equivalent to:

```text
expect order_id column to exist
expect customer_id values to be non-null
expect order_id values to be unique
expect currency values to belong to USD/EUR/GBP/INR
expect quantity values to be greater than 0
```

A current GX workflow should be created using the APIs supported by the installed release.

The engineering pattern remains:

```text
Dataset
  ↓
Expectations
  ↓
Validation
  ↓
Result
```

---

## 7.1 Break the dataset

Inject defects:

```python
broken_orders = orders.copy()

broken_orders.loc[1, "customer_id"] = None
broken_orders.loc[2, "quantity"] = -3
broken_orders.loc[2, "currency"] = "XYZ"
broken_orders.loc[0, "order_id"] = 1002
```

Now several rules should fail.

Expected interpretation:

| Defect | Expected check result |
|---|---|
| Duplicate `order_id` | Fail |
| Null `customer_id` | Fail |
| Negative `quantity` | Fail |
| Invalid `currency` | Fail |

The important engineering behavior is not the exact formatting of GX output.

It is that the validation result tells you:

```text
Which rule failed?
What was observed?
What was expected?
What data was affected?
What action should follow?
```

---

# 8. Designing Useful Expectations

A check is useful only if it represents a meaningful rule.

For every expectation, ask:

1. What business rule does this represent?
2. Why does the rule matter?
3. What defect does it catch?
4. What does it not catch?
5. How expensive is it?
6. What should happen if it fails?

Example:

```text
Rule:
    order_id must be unique
```

### Why it matters

Duplicate identifiers can cause:

- double counting,
- incorrect joins,
- incorrect revenue totals,
- broken downstream assumptions.

### What it catches

Duplicate `order_id` values.

### What it does not catch

A completely wrong but unique order ID.

That distinction matters.

A technically correct check can still be insufficient.

---

## 8.1 Technically valid vs operationally useful

Suppose this check always passes:

```text
row_count >= 1
```

It is technically valid.

But if the normal dataset contains 20 million rows, a dataset with 1,000 rows might pass while the business is severely impacted.

A quality rule must therefore be designed around the failure mode.

```text
Technical validity
        ≠
Operational usefulness
```

---

# 9. Common Great Expectations Check Categories

## 9.1 Schema checks

Examples:

```text
column exists
expected columns exist
unexpected columns are rejected or reported
data types are compatible
```

Schema checks catch structural changes.

---

## 9.2 Completeness checks

Examples:

```text
customer_id is not null
email is not null
null percentage <= 1%
```

A threshold can be more realistic than requiring zero nulls.

---

## 9.3 Uniqueness checks

Examples:

```text
order_id is unique
```

or:

```text
duplicate percentage <= 0.1%
```

The correct rule depends on the business meaning of duplicates.

---

## 9.4 Validity checks

Examples:

```text
quantity > 0
currency ∈ {USD, EUR, GBP, INR}
status ∈ {pending, paid, cancelled, refunded}
```

Pattern validation can be useful for identifiers:

```text
customer_id matches the expected identifier format
```

---

## 9.5 Volume checks

Volume checks detect unusual population changes.

Examples:

```text
row count >= expected minimum
```

or:

```text
row count is within an expected range
```

A static minimum is simple.

A historical or business-derived expectation can be more informative.

---

## 9.6 Temporal checks

Examples:

```text
latest order timestamp is recent enough
```

Freshness is often an operational SLA rather than a pure schema property.

---

## 9.7 Distribution-oriented checks

Some quality systems support statistical or distribution-oriented expectations.

These can detect changes such as:

```text
quantity distribution changes substantially
```

Use them deliberately.

Do not turn every normal distribution fluctuation into an incident.

This chapter only introduces the integration point; advanced anomaly detection belongs elsewhere in the curriculum.

---

## 9.8 Custom logic

Generic expectations cannot express every business rule elegantly.

For complex relationships, SQL or framework-specific custom validation can be more readable.

Example:

```sql
SELECT COUNT(*) AS invalid_rows
FROM orders
WHERE total_amount <> quantity * unit_price;
```

Expected:

```text
invalid_rows = 0
```

---

# 10. Thresholds

Many quality rules are not simply:

```text
PASS / FAIL
```

Instead, the rule may allow a bounded amount of imperfection.

Examples:

```text
null percentage <= 1%
duplicate percentage <= 0.1%
row count >= expected minimum
failed rows <= allowed threshold
```

---

## 10.1 Hard constraint

A hard constraint means:

```text
Any violation is unacceptable.
```

Example:

```text
primary key must be unique
```

---

## 10.2 Threshold-based constraint

A threshold allows a defined range.

Example:

```text
description null rate <= 5%
```

The threshold must have an engineering or business reason.

Bad:

```text
We chose 5% because it sounded reasonable.
```

Better:

```text
Historical null rate is normally below 1%.
Operations has determined that >5% means the source is materially degraded.
```

---

## 10.3 Threshold design questions

Ask:

- What is the normal range?
- What is the business impact?
- Is the threshold absolute or relative?
- Is it based on history?
- What happens at the boundary?
- Is the threshold different by partition?
- Who owns the threshold?
- When should it be reviewed?

---

# 11. Severity

Severity is a policy layer above technical validation.

A check can fail without necessarily blocking the pipeline.

A practical classification is:

```text
INFO
WARNING
ERROR
CRITICAL
```

Example:

| Rule | Severity | Failure action |
|---|---|---|
| Optional description completeness | INFO | Log |
| Minor freshness warning | WARNING | Alert/report |
| Currency validity | ERROR | Stop affected publication |
| Primary-key uniqueness | CRITICAL | Block publication |

A failed informational check may only create an observation.

A failed critical check may block publication.

Therefore:

```text
Check result
    +
Severity policy
    ↓
Operational action
```

Severity should not be embedded casually inside individual assertions. It should be part of the quality policy.

---

# 12. Pipeline Quality Gates

A quality gate converts validation into a pipeline decision.

```text
Ingestion
    ↓
Transformation
    ↓
Quality checks
    ↓
+--------------------+
| PASS → Publish     |
| FAIL → Stop/Route  |
+--------------------+
```

Possible actions include:

- publish,
- block,
- quarantine,
- retry,
- alert,
- create an incident,
- continue with a warning,
- create an audit record.

A quality gate is therefore an **operational policy**, not merely a validation assertion.

---

## 12.1 Blocking and non-blocking checks

Example:

```text
CRITICAL:
    duplicate primary key
    → block

ERROR:
    invalid currency
    → block affected dataset

WARNING:
    description completeness below target
    → publish + alert

INFO:
    optional metadata missing
    → record only
```

The exact policy should depend on business impact.

---

# 13. Great Expectations Execution Workflow

The durable conceptual workflow is:

```text
data
  ↓
expectations
  ↓
execution
  ↓
validation results
  ↓
pass/fail decision
  ↓
reporting
  ↓
pipeline action
```

Older and newer GX versions may use different names for parts of this workflow.

Do not let terminology obscure the architecture.

The important distinction is:

```text
Expectation definition
        ≠
Validation execution
        ≠
Pipeline policy
```

A validation framework evaluates rules.

Your pipeline decides what those results mean operationally.

---

# 14. Validation Results

A useful validation result should make it possible to answer:

- Did the check succeed?
- Which expectation failed?
- What was observed?
- What was expected?
- Which column/data asset was affected?
- What metadata describes the execution?
- When did the validation run?
- Which run produced the result?

A representative conceptual result might look like:

```json
{
  "check_id": "orders.order_id.unique",
  "success": false,
  "observed_value": 0.997,
  "expected": 1.0,
  "dataset": "orders",
  "column": "order_id",
  "severity": "CRITICAL",
  "run_id": "orders-2026-10-01-1200"
}
```

This is a conceptual structure, not a claim about a specific GX release's exact JSON schema.

Validation results support:

- debugging,
- alerting,
- reporting,
- trend analysis,
- incident investigation.

---

# 15. Soda — Conceptual Model

## 15.1 What is Soda?

Soda is a data-quality system centered around checks, scans, data sources, metrics, thresholds, and results.

A simplified architecture is:

```text
Data source
    ↓
SodaCL checks
    ↓
Scan
    ↓
Metrics / observations
    ↓
Check outcome
    ↓
Reporting / action
```

---

## 15.2 What is SodaCL?

SodaCL is Soda's declarative configuration language for expressing data-quality checks.

The important idea is that quality logic can be represented as configuration rather than scattered Python control flow.

For example, conceptually:

```yaml
checks for orders:
  - row_count > 0
  - missing_count(customer_id) = 0
```

The exact syntax supported depends on the installed Soda version and package.

Always validate configuration against the installed version.

---

# 16. Your First Soda Check

Consider an `orders` dataset.

A simple SodaCL-style check might express:

```yaml
checks for orders:
  - row_count > 0
  - missing_count(customer_id) = 0
  - duplicate_count(order_id) = 0
```

The mental model is:

```text
orders
  ↓
check
  ↓
metric
  ↓
threshold
  ↓
outcome
```

For example:

```text
duplicate_count(order_id)
        ↓
observed = 4
        ↓
expected = 0
        ↓
FAIL
```

---

## 16.1 Inject a defect

Suppose the source originally contains:

```text
100,000 rows
0 duplicate order IDs
```

Then a duplicated batch introduces 500 duplicates.

The check changes from:

```text
duplicate_count(order_id) = 0
```

to:

```text
duplicate_count(order_id) = 500
```

The important result is not simply "Soda failed."

It is:

```text
Rule:
    order_id must be unique

Observed:
    500 duplicates

Expected:
    0

Decision:
    CRITICAL → block publication
```

---

# 17. SodaCL Fundamentals

A useful abstraction is:

```text
Dataset
    ↓
Check
    ↓
Metric
    ↓
Threshold
    ↓
Outcome
```

Examples include:

```text
row_count > 1000
missing_count(customer_id) = 0
duplicate_count(order_id) = 0
```

More complex checks can use SQL-backed logic where appropriate.

Keep SodaCL readable.

A quality configuration should be understandable by the engineer who owns the dataset six months later.

---

# 18. Soda Check Categories

Practical categories include:

### Row count

```text
row_count > expected minimum
```

### Missingness

```text
missing_count(customer_id) = 0
```

or a bounded missingness rule.

### Duplicate checks

```text
duplicate_count(order_id) = 0
```

### Value validity

Checks for:

```text
allowed categories
ranges
patterns
```

### Freshness

Check that the dataset or timestamp field is recent enough.

### Threshold-based checks

Example:

```text
null percentage <= 1%
```

### SQL-based checks

Use SQL when the rule is naturally expressed as a query.

### Anomaly awareness

Soda can participate in broader quality monitoring patterns, but this chapter only introduces the integration point. Advanced anomaly detection is outside this topic's main scope.

---

# 19. DuckDB Validation

DuckDB is particularly useful for local analytical validation.

It provides a practical bridge:

```text
Parquet
   ↓
DuckDB
   ↓
SQL quality check
   ↓
Result
```

This is valuable for learning because you can validate file-backed data without requiring a full warehouse.

---

## 19.1 Query Parquet with DuckDB

Example:

```python
import duckdb

connection = duckdb.connect()

row_count = connection.execute(
    """
    SELECT COUNT(*)
    FROM read_parquet('orders.parquet')
    """
).fetchone()[0]

print(row_count)
```

The SQL engine can evaluate quality rules close to the data.

---

## 19.2 A quality query

```python
invalid_count = connection.execute(
    """
    SELECT COUNT(*)
    FROM read_parquet('orders.parquet')
    WHERE quantity <= 0
    """
).fetchone()[0]

if invalid_count != 0:
    raise ValueError(
        f"Found {invalid_count} rows with invalid quantity"
    )
```

This is still imperative orchestration around a declarative SQL rule.

That distinction is useful:

```text
SQL expresses WHAT violates the rule.
Python decides WHAT TO DO with the result.
```

---

# 20. Parquet Validation

A Parquet file can be:

- readable,
- structurally valid,
- successfully parsed,

and still be logically wrong.

Examples:

```text
column exists but contains unexpected nulls
row count dropped unexpectedly
duplicate business keys appeared
currency contains invalid values
timestamps are stale
business invariant is violated
```

Useful validation layers include:

```text
Schema
Row count
Nullability
Uniqueness
Value ranges
Freshness
Business invariants
```

---

## 20.1 Example

```sql
SELECT
    COUNT(*) AS invalid_rows
FROM read_parquet('orders.parquet')
WHERE quantity <= 0;
```

Expected:

```text
invalid_rows = 0
```

The file's ability to open does not prove that the dataset is fit for consumption.

---

# 21. PostgreSQL Validation

Database-side checks can often be more efficient than pulling a large table into Python.

Useful checks include:

- row counts,
- null counts,
- duplicate keys,
- invalid statuses,
- referential consistency,
- freshness,
- business invariants.

---

## 21.1 Row count

```sql
SELECT COUNT(*) AS row_count
FROM orders;
```

---

## 21.2 Null count

```sql
SELECT COUNT(*) AS invalid_rows
FROM orders
WHERE customer_id IS NULL;
```

---

## 21.3 Duplicate keys

```sql
SELECT order_id, COUNT(*) AS occurrences
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

A quality check can convert the existence of any returned row into failure.

---

## 21.4 Invalid statuses

```sql
SELECT COUNT(*) AS invalid_rows
FROM orders
WHERE status NOT IN (
    'pending',
    'paid',
    'cancelled',
    'refunded'
);
```

---

## 21.5 Freshness

A representative PostgreSQL query is:

```sql
SELECT
    EXTRACT(
        EPOCH FROM (
            CURRENT_TIMESTAMP - MAX(order_timestamp)
        )
    ) AS age_seconds
FROM orders;
```

A pipeline can compare `age_seconds` with the freshness SLA.

The exact freshness threshold belongs to the business/operational contract.

---

# 22. DataFrame-Oriented Validation

Declarative frameworks complement, rather than automatically replace, DataFrame validation.

Compare:

```text
pandas / Polars
    +
Pandera
```

with:

```text
Great Expectations / Soda
```

and:

```text
SQL / database constraints
```

---

## 22.1 Small local transformation

Suppose a Python transformation produces a DataFrame.

Pandera may be a natural boundary:

```text
Python transformation
        ↓
Pandera schema
        ↓
validated DataFrame
```

---

## 22.2 Warehouse table

For a large warehouse table:

```text
Warehouse table
        ↓
SQL/GX/Soda checks
        ↓
quality result
```

Pulling the complete dataset into Python solely to validate it may be unnecessarily expensive.

---

## 22.3 Database integrity

For hard relational invariants, database constraints may be the first line:

```text
PRIMARY KEY
FOREIGN KEY
UNIQUE
CHECK
NOT NULL
```

Quality frameworks can complement these constraints rather than replace them.

---

# 23. Custom SQL Checks

SQL is essential because many business rules are relational.

## 23.1 Referential consistency

```sql
SELECT COUNT(*) AS invalid_rows
FROM orders AS o
LEFT JOIN customers AS c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

Expected:

```text
invalid_rows = 0
```

---

## 23.2 Business invariant

```sql
SELECT COUNT(*) AS invalid_rows
FROM orders
WHERE total_amount <> quantity * unit_price;
```

Expected:

```text
invalid_rows = 0
```

This rule may be more readable as SQL than as a generic expectation API.

---

## 23.3 Freshness

```sql
SELECT
    MAX(order_timestamp) AS latest_order_timestamp
FROM orders;
```

The pipeline can then compare the observed timestamp with the allowed freshness window.

---

## 23.4 Why SQL checks matter

SQL can express:

- joins,
- aggregations,
- relationships,
- business invariants,
- window logic,
- database-local calculations.

The advantages include:

- execution close to the data,
- expressive relational semantics,
- easy review by SQL-capable data engineers.

The trade-offs include:

- SQL dialect differences,
- performance risks,
- maintainability,
- portability,
- hidden complexity.

Use SQL because it improves clarity or capability, not simply because a framework allows custom SQL.

---

# 24. Framework Checks vs SQL Checks

| Approach | Main advantage | Main risk |
|---|---|---|
| Framework-native check | Standardized and reusable | May not express every business rule naturally |
| Custom SQL | Highly expressive | Dialect/performance/maintenance complexity |
| Database constraint | Enforced at data-store boundary | Not suitable for every analytical quality rule |

A practical principle:

```text
Use the simplest representation that expresses
the rule clearly and executes at acceptable cost.
```

---

# 25. Historical Quality Reporting

A single validation result is not enough.

Suppose today's null rate is:

```text
0.8%
```

and the threshold is:

```text
<= 1%
```

The check passes.

But historical results are:

```text
0.1%
0.2%
0.2%
0.3%
0.8%
```

That is a strong deterioration signal even though today's value is technically within the threshold.

Historical quality results should capture fields such as:

| Field | Example |
|---|---|
| Timestamp | 2026-10-01T12:00:00Z |
| Dataset | orders |
| Rule ID | orders.customer_id.null_rate |
| Metric | null_rate |
| Observed value | 0.008 |
| Threshold | 0.01 |
| Status | PASS |
| Run ID | orders-20261001-1200 |

The exact storage implementation is project-specific.

---

# 26. Quality Trend Analysis

Historical results enable:

- regression detection,
- trend analysis,
- incident investigation,
- quality scorecards,
- SLO monitoring.

Example:

```text
customer_id completeness

100% ┤████████████████████
 99% ┤███████████████████
 98% ┤█████████████████
 97% ┤███████████████
     └────────────────────
       day1 day2 day3 day4
```

The important engineering idea is:

```text
Current result
    +
Historical context
    ↓
Better operational decision
```

This is not the same as full anomaly detection.

A trend can be useful even before an anomaly-detection system is introduced.

---

# 27. Quality Reporting

A useful quality report should contain:

```text
Dataset
Run ID
Timestamp
Checks executed
Passed
Failed
Warnings
Critical failures
Observed metrics
Thresholds
Pipeline action
```

---

## 27.1 Raw output vs operational report

Raw output:

```text
check_17 = false
```

Operational report:

```text
Dataset: orders
Rule: orders.order_id.unique
Severity: CRITICAL
Observed duplicates: 421
Expected duplicates: 0
Run: orders-20261001-1200
Action: publication blocked
Owner: orders-data-product
```

The second form is much more useful during an incident.

---

# 28. Data Quality Scorecards

A scorecard can summarize multiple dimensions:

```text
Completeness: 98.5%
Validity:     99.9%
Uniqueness:   99.99%
Freshness:    PASS
```

But a single aggregate score can hide critical failures.

For example:

```text
Overall score = 99.5%
```

could coexist with:

```text
Primary-key uniqueness = FAIL
```

Therefore scorecards should preserve critical checks separately.

Possible components include:

- dimensions,
- weighted scoring where justified,
- critical checks,
- SLOs,
- trend indicators.

Do not invent arbitrary weights.

If weighting is used, document why.

---

# 29. Defect Injection Lab

The fastest way to learn a validator is to break the data deliberately.

Start with clean data.

Then inject:

1. missing column,
2. null customer IDs,
3. duplicate order IDs,
4. invalid currency,
5. negative quantity,
6. unexpected row-count drop,
7. stale timestamp,
8. referential-integrity failure,
9. invalid business invariant.

For every defect:

```text
Inject
  ↓
Run GX check
  ↓
Inspect result
  ↓
Run Soda check where appropriate
  ↓
Compare results
  ↓
Choose severity/action
```

---

## 29.1 Example defect

Clean:

```text
order_id = 1005
quantity = 2
unit_price = 25
total_amount = 50
```

Defective:

```text
order_id = 1005
quantity = 2
unit_price = 25
total_amount = 70
```

SQL rule:

```sql
SELECT COUNT(*) AS invalid_rows
FROM orders
WHERE total_amount <> quantity * unit_price;
```

Expected:

```text
0
```

Observed:

```text
1
```

The defect is detected even though every column may have a valid type and every value may look individually plausible.

That demonstrates why **business invariants** matter.

---

# 30. Great Expectations vs Soda

| Dimension | Pandera | Great Expectations | Soda | Plain SQL | Database constraints |
|---|---|---|---|---|---|
| Primary style | Python/DataFrame schema | Expectation-driven validation | Configuration/check-driven quality | SQL rules | Store-level enforcement |
| Typical target | DataFrames | Data assets/tables/DataFrames depending on workflow | Data sources/tables | Database/analytical engines | Relational tables |
| Configuration | Python | Framework APIs/configuration | SodaCL/configuration | SQL | DDL/schema |
| Strength | Local DataFrame contracts | Structured expectation workflow | Declarative checks and scans | Relational expressiveness | Strong integrity enforcement |
| Limitation | Less natural for warehouse-wide monitoring | Version/API complexity | Ecosystem/configuration complexity | Governance and portability must be designed | Not a complete analytical quality system |
| SQL support | Indirect/limited by context | Available depending on data source/workflow | Strong SQL-oriented usage | Native | Native SQL/constraints |
| DataFrame support | Strong | Available in relevant workflows | Depends on data-source workflow | Through an engine | Not the purpose |
| Reporting | Usually application/test output | Validation/reporting capabilities | Scan/check reporting | Must be built | Database/system telemetry |
| Pipeline integration | Python-native | Validation workflow integration | Scan/pipeline integration | Orchestrator/application | Write-time enforcement |
| Operational complexity | Low to moderate | Moderate to high depending on scope | Moderate to high depending on scope | Low framework overhead | Low framework overhead |
| Appropriate use | Python transformation boundary | Structured declarative validation | Data-quality scans/checks | Expressive relational rules | Hard database invariants |

This table is a **selection aid**, not a ranking.

The right choice depends on:

```text
data location
+
data volume
+
failure mode
+
ownership
+
required reporting
+
SQL needs
+
operational cost
```

---

# 31. Tool Selection Framework

Ask these questions:

1. Where is the data?
2. What is the data volume?
3. Is the data a DataFrame or database table?
4. Do checks need SQL?
5. Does the team need historical reporting?
6. Does the team need declarative configuration?
7. How much operational infrastructure is acceptable?
8. Who owns the checks?
9. How frequently do checks run?
10. What is the cost of failure?
11. What ecosystem already exists?
12. How stable is the chosen tool/API?

---

## 31.1 Decision examples

### Small Python transformation

```text
DataFrame
    ↓
Pandera may be sufficient
```

### Warehouse-centric quality program

```text
Warehouse
    ↓
GX / Soda / SQL may be appropriate
```

### Database integrity

```text
Database
    ↓
Constraints may be the first line
```

### Mixed architecture

```text
Source ingestion
    ↓
Pandera
    ↓
Transformation
    ↓
GX/Soda
    ↓
SQL/database constraints
```

Tools can coexist.

The objective is not to minimize the number of tools at any cost.

The objective is to minimize **unnecessary complexity while maintaining sufficient quality coverage**.

---

# 32. Maintainability

Quality systems degrade when checks are allowed to grow without governance.

Common problems:

- duplicated checks,
- unclear ownership,
- inconsistent naming,
- scattered SQL,
- undocumented thresholds,
- obsolete checks,
- rules that no longer reflect business requirements,
- unclear failure actions,
- framework-specific behavior hidden in pipelines.

---

## 32.1 Rule IDs

Use stable identifiers.

Example:

```text
orders.schema.required_columns
orders.order_id.unique
orders.customer_id.completeness
orders.currency.allowed_values
orders.total_amount.business_invariant
```

Stable IDs help with:

- history,
- ownership,
- reporting,
- incident investigation,
- migration.

---

## 32.2 Ownership metadata

A rule should have an owner.

Conceptually:

```yaml
rule_id: orders.order_id.unique
owner: orders-data-product
severity: CRITICAL
action: block_publish
```

The exact configuration mechanism is implementation-specific.

---

## 32.3 Threshold documentation

Bad:

```text
null_rate <= 0.03
```

Better:

```text
null_rate <= 0.03

Reason:
Historical baseline is <1%.
Operations accepts up to 3% during source maintenance.
Above 3%, downstream customer matching becomes materially degraded.
```

---

## 32.4 Lifecycle management

Every rule should have a lifecycle:

```text
Proposed
  ↓
Reviewed
  ↓
Active
  ↓
Maintained
  ↓
Retired
```

Do not let obsolete checks live forever.

---

# 33. Tool Churn

Tool churn occurs when organizations repeatedly add frameworks without removing or consolidating existing logic.

Example:

```text
Tool A adopted
    ↓
Tool B introduced
    ↓
checks duplicated
    ↓
multiple systems maintained
    ↓
engineers confused
    ↓
quality logic fragmented
```

Costs include:

- migration effort,
- retraining,
- duplicated logic,
- API instability,
- maintenance burden,
- lock-in,
- operational ownership.

A useful principle is:

> Adopt a new tool to solve a clear capability gap, not because every new framework is fashionable.

---

# 34. Versioning and API Stability

Production data-quality systems are software systems.

Treat them accordingly.

Practices include:

- dependency pinning,
- compatibility testing,
- upgrade planning,
- release-note review,
- automated test suites,
- avoiding undocumented APIs,
- isolating framework-specific code.

---

## 34.1 Adapter thinking

Instead of spreading framework-specific calls everywhere:

```text
pipeline code
    ↓
framework-specific API everywhere
```

prefer:

```text
pipeline
    ↓
quality interface/policy
    ↓
framework adapter
    ↓
GX/Soda
```

The exact architecture depends on project scale.

The principle is to make future change cheaper without building unnecessary abstraction.

---

# 35. Real-World Failure Modes

## 35.1 Check passes but data is still wrong

**Symptom**

All configured checks pass.

**Root cause**

The system checks the wrong failure modes.

**Debugging**

Review:

```text
business rules
quality dimensions
historical incidents
consumer expectations
```

**Remediation**

Add a rule that corresponds to the actual defect.

**Prevention**

Design checks from failure modes, not from whatever checks the framework makes easy.

---

## 35.2 Check is too strict

**Symptom**

Normal data causes failures.

**Root cause**

Constraint does not match real operating conditions.

**Debugging**

Inspect historical distributions and legitimate exceptions.

**Remediation**

Adjust the rule or define a justified threshold.

**Prevention**

Test boundaries before deployment.

---

## 35.3 Check is too weak

**Symptom**

The pipeline passes data that downstream users report as broken.

**Root cause**

Validation coverage is insufficient.

**Remediation**

Identify the missing invariant.

---

## 35.4 Threshold is arbitrary

**Symptom**

Teams debate the number instead of the business impact.

**Root cause**

No evidence supports the threshold.

**Remediation**

Use historical baselines, business impact, and operational requirements.

---

## 35.5 SQL query is slow

**Symptom**

Quality validation significantly increases runtime.

**Debugging**

Inspect:

- query plan,
- scanned rows,
- indexes/partitioning where relevant,
- joins,
- repeated scans,
- aggregation cost.

**Remediation**

Optimize SQL, reduce unnecessary scans, use incremental checks where appropriate, or move a suitable invariant closer to the database.

---

## 35.6 Quality checks increase pipeline runtime

Measure:

```text
baseline runtime
+
quality-check runtime
```

Do not assume that more checks are free.

---

## 35.7 Duplicate checks exist in multiple tools

Example:

```text
Pandera:
    customer_id non-null

GX:
    customer_id non-null

Soda:
    customer_id non-null
```

This may be intentional in layered architecture, but if all three exist for the same purpose without a clear boundary, maintenance cost increases.

Define ownership by validation layer.

---

## 35.8 Check ownership is unclear

A failure occurs and nobody knows who should fix it.

Remediation:

```text
rule → owner → escalation path
```

---

## 35.9 Historical results are not retained

Without history, teams cannot distinguish:

```text
one-time failure
```

from:

```text
gradual deterioration
```

Store results where operationally appropriate.

---

## 35.10 Failed checks do not trigger action

A red dashboard without pipeline policy is not a quality gate.

Connect:

```text
failure
    ↓
severity
    ↓
action
```

---

## 35.11 Warnings are ignored

Too many warnings produce alert fatigue.

A warning should have a reason to exist.

If nobody acts on it, reconsider:

```text
severity
threshold
owner
or rule value
```

---

## 35.12 Tool upgrade breaks checks

Treat framework upgrades as production changes.

Use:

```text
upgrade
  ↓
compatibility test
  ↓
validation suite
  ↓
controlled rollout
```

---

## 35.13 SQL dialect differences

A check written for one engine may fail elsewhere.

Consider:

```text
PostgreSQL
DuckDB
Spark SQL
Snowflake
BigQuery
```

when portability matters.

Do not assume SQL is universally identical.

---

## 35.14 False alarms

A technically correct check can still be operationally harmful if it generates repeated false alarms.

Investigate:

- baseline,
- threshold,
- partition behavior,
- legitimate exceptions,
- data latency,
- source timing.

---

# 36. Debugging Lab

## Scenario A — Row count suddenly fails

### Identify

```text
Rule:
row_count >= expected minimum
```

### Inspect

- observed count,
- historical counts,
- upstream extraction status,
- source partitions,
- processing window.

### Decide

Is this:

```text
real source degradation
```

or:

```text
expected volume variation
```

Then classify severity and action.

---

## Scenario B — Duplicate batch

Observed:

```text
duplicate_count(order_id) = 10,000
```

Debug:

```text
Did a partition get reprocessed?
Did ingestion lose idempotency?
Did an upstream producer resend data?
Did a join multiply rows?
```

Do not immediately blame the quality framework.

---

## Scenario C — Freshness failure

Observed:

```text
latest event = 90 minutes old
SLA = 30 minutes
```

Investigate:

```text
source delay
network issue
scheduler failure
consumer lag
late-arriving data
```

The validator detected the symptom.

The incident investigation finds the cause.

---

## Scenario D — Referential-integrity failure

SQL:

```sql
SELECT COUNT(*)
FROM orders o
LEFT JOIN customers c
  ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

If result is non-zero:

1. identify affected keys,
2. determine whether customers arrived late,
3. determine whether IDs are malformed,
4. inspect ingestion timing,
5. decide whether the rule should block publication.

---

## Scenario E — Threshold too sensitive

Suppose:

```text
normal null rate:
0.2%–0.8%

threshold:
0.5%
```

The threshold causes repeated warnings.

Compare:

```text
historical baseline
business impact
alert frequency
```

Then revise only with evidence.

---

## Scenario F — Tool upgrade changes behavior

Steps:

```text
1. Identify framework version before/after.
2. Reproduce the failing rule.
3. Compare documented behavior.
4. Inspect release notes.
5. Run validator tests.
6. Isolate changed API/semantics.
7. Pin/upgrade/adjust deliberately.
8. Record the change.
```

---

# 37. Hands-On Project: Declarative Data Quality Gate for an Orders Dataset

## 37.1 Architecture

```text
Orders source
    ↓
DuckDB / PostgreSQL / Parquet
    ↓
GX checks
    +
Soda checks
    ↓
Quality results
    ↓
Quality gate
    ↓
+-----------------------------+
| PASS → publish              |
| FAIL → block / alert / fix  |
+-----------------------------+
```

---

## 37.2 Project requirements

Implement at least 15 rules covering:

- schema,
- nulls,
- uniqueness,
- validity,
- row-count threshold,
- freshness,
- SQL business invariant,
- SQL referential integrity,
- severity,
- quality gate,
- historical result recording,
- defect injection,
- debugging,
- comparison of GX and Soda approaches.

All project code can live inside this chapter while you learn.

---

# 38. Project Dataset

Use a small synthetic dataset for learning rather than relying on an external dataset.

Recommended columns:

```text
order_id
customer_id
order_timestamp
quantity
unit_price
currency
status
total_amount
```

Example clean records:

```python
orders = [
    {
        "order_id": 1001,
        "customer_id": "C001",
        "order_timestamp": "2026-10-01T09:00:00",
        "quantity": 2,
        "unit_price": 20.0,
        "currency": "USD",
        "status": "paid",
        "total_amount": 40.0,
    },
    {
        "order_id": 1002,
        "customer_id": "C002",
        "order_timestamp": "2026-10-01T09:05:00",
        "quantity": 1,
        "unit_price": 25.0,
        "currency": "EUR",
        "status": "pending",
        "total_amount": 25.0,
    },
]
```

Defect categories to create:

```text
missing values
duplicate IDs
stale timestamps
invalid currency
negative quantity
invalid status
referential-integrity failure
business invariant violation
row-count drop
missing column
```

---

# 39. Example Rule Catalog

A useful 15-rule catalog is:

| ID | Rule | Severity |
|---|---|---|
| R001 | Required columns exist | CRITICAL |
| R002 | `order_id` not null | CRITICAL |
| R003 | `order_id` unique | CRITICAL |
| R004 | `customer_id` not null | ERROR |
| R005 | `quantity > 0` | ERROR |
| R006 | `unit_price >= 0` | ERROR |
| R007 | currency allowed | ERROR |
| R008 | status allowed | ERROR |
| R009 | row count above minimum | WARNING/ERROR |
| R010 | freshness within SLA | ERROR |
| R011 | `total_amount = quantity * unit_price` | CRITICAL |
| R012 | all customer IDs exist | CRITICAL |
| R013 | timestamp is not unexpectedly future-dated | WARNING/ERROR |
| R014 | null-rate threshold for optional attributes | WARNING |
| R015 | duplicate-rate threshold for a non-key field where appropriate | INFO/WARNING |

The exact severity should be decided from business impact.

---

# 40. Testing the Quality Checks

Testing the validator is different from testing the data.

## 40.1 Testing the data

Question:

> Does this dataset satisfy the rules?

Examples:

```text
valid data
invalid data
boundary data
```

## 40.2 Testing the validator

Question:

> Does the validator correctly detect the expected defect?

Tests should include:

- valid data passes,
- invalid data fails,
- threshold behavior,
- boundary conditions,
- SQL check behavior,
- historical result persistence,
- severity/action behavior,
- defect injection.

---

## 40.3 Example validator test

Conceptually:

```python
def test_negative_quantity_fails():
    data = [
        {"order_id": 1, "quantity": -1}
    ]

    result = validate_quantity(data)

    assert not result.success
```

The actual test implementation depends on the selected framework.

---

# 41. Performance Engineering

Quality checks have a cost.

Measure where practical:

- execution time,
- rows processed,
- checks executed,
- database query cost,
- repeated scans,
- expensive joins,
- expensive aggregations.

---

## 41.1 Simple vs expensive check

Simple:

```sql
SELECT COUNT(*)
FROM orders
WHERE customer_id IS NULL;
```

Potentially expensive:

```sql
SELECT COUNT(*)
FROM orders o
JOIN customers c
  ON o.customer_id = c.customer_id
WHERE ...
```

The second may require a large join.

That does not mean it should not exist.

It means its operational cost should be understood.

---

## 41.2 Cost-aware validation

A mature system aims for:

```text
sufficient quality coverage
+
acceptable operational cost
```

not:

```text
maximum number of checks
```

Never fabricate benchmark numbers.

Measure in the target environment.

A simple timing harness is:

```python
from time import perf_counter

start = perf_counter()

# run validation here

elapsed = perf_counter() - start
print(f"Validation time: {elapsed:.3f}s")
```

The observed number is environment-dependent.

---

# 42. Production Architecture

A layered production architecture can look like:

```text
Source
  ↓
Ingestion
  ↓
Pandera boundary checks
  ↓
Transformation
  ↓
GX/Soda declarative checks
  ↓
SQL/database checks
  ↓
Quality results
  ↓
Quality gate
  ↓
Publish
  ↓
Consumers
```

Different technologies exist at different boundaries because the data and failure modes differ.

---

## 42.1 Why multiple layers?

### Pandera

Useful at the Python/DataFrame boundary.

### GX/Soda

Useful for standardized declarative validation and operational quality checks.

### SQL

Useful for relational business rules.

### Database constraints

Useful for hard database-level integrity.

The key principle is:

> **No single tool is the entire data-quality architecture.**

---

# 43. Production Scenarios

## Scenario 1 — Order volume drops by 60%

### Detection

Row-count or volume check.

### Diagnosis

Compare:

- historical volume,
- source extraction,
- partitions,
- scheduler,
- upstream changes.

### Severity

Potentially ERROR/CRITICAL depending on business impact.

### Action

Block publication if downstream consumers would receive materially incomplete data.

### Prevention

Volume monitoring plus source-level observability.

---

## Scenario 2 — Duplicate order IDs increase suddenly

### Detection

Uniqueness check.

### Diagnosis

Investigate:

- repeated batch,
- retry behavior,
- missing idempotency,
- join multiplication.

### Action

Likely block if `order_id` is a true business key.

### Prevention

Idempotent ingestion and uniqueness enforcement.

---

## Scenario 3 — Customer IDs become nullable

### Detection

Completeness check.

### Diagnosis

Inspect source schema and upstream mapping.

### Action

Depending on downstream impact, block or warn.

---

## Scenario 4 — Freshness SLA is missed

### Detection

Timestamp/freshness check.

### Diagnosis

Inspect source delay and orchestration.

### Action

Alert or block according to SLA.

---

## Scenario 5 — Currency values change unexpectedly

Observed:

```text
USD
EUR
GBP
INR
JPY
```

but expected values were previously:

```text
USD
EUR
GBP
INR
```

Do not automatically assume the new value is invalid.

First determine whether:

```text
business requirements changed
```

or:

```text
source behavior changed unexpectedly
```

---

## Scenario 6 — SQL quality check becomes slow

Measure:

```text
query time
rows scanned
join cost
```

Then optimize or redesign the check.

---

## Scenario 7 — GX/Soda check fails after dependency upgrade

Treat it as a software compatibility incident:

```text
version
→ reproduce
→ identify behavior change
→ test
→ remediate
→ pin/upgrade deliberately
```

---

## Scenario 8 — Business rule changes but check does not

This is a governance failure.

Example:

```text
Old rule:
status ∈ {pending, paid, cancelled}

Business changes:
status may now include refunded
```

If the check is not updated, valid production data may be rejected.

Quality rules must have ownership and lifecycle management.

---

# 44. Interview Questions and Answers

## Basic

### 1. What is declarative data validation?

Declarative validation describes what must be true about data rather than embedding the entire validation procedure in imperative application code.

Example:

```text
order_id must be unique
```

The framework evaluates the rule and produces a result.

---

### 2. What is an expectation?

An expectation is an explicit statement of a data-quality condition that should hold for a dataset.

Examples:

```text
column exists
values are non-null
values are unique
values belong to an allowed set
```

---

### 3. What is SodaCL?

SodaCL is Soda's declarative configuration language for expressing data-quality checks.

It allows rules to be represented as configuration rather than scattered validation code.

---

### 4. Why are declarative checks useful?

They can standardize:

- rule definitions,
- execution,
- results,
- reporting,
- ownership,
- pipeline integration.

---

### 5. What is a quality gate?

A quality gate is an operational decision point that converts validation results into actions such as publish, block, alert, or investigate.

---

## Intermediate

### 6. Pandera vs Great Expectations?

Pandera is particularly natural for Python/DataFrame validation.

Great Expectations provides an expectation-driven validation model that can be used across data assets and execution workflows.

They can coexist.

---

### 7. Great Expectations vs Soda?

Both support declarative data-quality validation, but their configuration models, APIs, workflows, and operational patterns differ.

Selection should be based on:

```text
data source
team ecosystem
required reporting
SQL needs
ownership
operational cost
```

---

### 8. Why use SQL checks?

SQL is expressive for relational rules involving:

- joins,
- aggregates,
- business invariants,
- referential relationships.

It also allows validation to execute close to the database.

---

### 9. What are thresholds?

Thresholds define acceptable boundaries rather than requiring perfect values.

Example:

```text
null rate <= 1%
```

The threshold should be justified.

---

### 10. Why store historical validation results?

Because a single result lacks context.

History enables:

- trend analysis,
- regression detection,
- incident investigation,
- scorecards,
- SLO monitoring.

---

### 11. What is a blocking quality check?

A check whose failure prevents a downstream action such as publishing a dataset.

---

## Advanced

### 12. How would you design a quality system for a warehouse?

Use layers:

```text
database constraints
+
SQL checks
+
declarative framework checks
+
quality results
+
severity policy
+
quality gate
+
historical reporting
```

The exact framework should be selected based on the warehouse and organizational requirements.

---

### 13. How do you choose between Pandera, GX, Soda, and SQL?

Ask:

1. Where is the data?
2. What is the volume?
3. Is it a DataFrame or table?
4. Are relational SQL rules needed?
5. Is historical reporting required?
6. Who owns the checks?
7. What operational complexity is acceptable?

---

### 14. How do you prevent duplicate quality rules?

Create:

- rule IDs,
- ownership,
- a rule catalog,
- clear validation-layer boundaries,
- review processes.

For example:

```text
Pandera → Python transformation boundary
GX/Soda → dataset-level declarative quality
SQL → relational/business rules
DB constraints → hard integrity
```

---

### 15. How do you control validation cost?

Measure:

```text
runtime
rows scanned
query cost
repeated scans
join cost
```

Then prioritize high-value checks and optimize expensive rules.

---

### 16. How do you handle framework upgrades?

Use:

```text
version pinning
+
compatibility tests
+
release-note review
+
controlled upgrades
+
regression tests
```

---

### 17. How do you detect quality regressions?

Store historical metrics and compare current observations with:

```text
thresholds
+
historical baselines
+
known operating ranges
```

---

# 45. Architecture Questions

## 45.1 Design a production quality gate for orders

A reasonable architecture:

```text
orders source
    ↓
ingestion
    ↓
DataFrame/schema boundary
    ↓
transformation
    ↓
declarative checks
    ↓
SQL invariants
    ↓
results
    ↓
severity policy
    ↓
quality gate
    ↓
publish/block
```

Critical rules should be capable of blocking publication.

---

## 45.2 How would you validate Parquet data?

Use an analytical engine such as DuckDB to execute SQL checks over the file:

```text
Parquet
  ↓
DuckDB
  ↓
schema/volume/value/business checks
  ↓
result
```

A declarative framework can orchestrate or standardize the checks where appropriate.

---

## 45.3 How would you validate PostgreSQL tables?

Prefer database-side execution for large datasets:

```text
PostgreSQL
  ↓
SQL checks
  ↓
metrics/results
```

Avoid pulling entire tables into Python merely to count invalid rows.

---

## 45.4 How would you validate a 1-billion-row warehouse table?

Do not assume full-table Python scans are appropriate.

Consider:

- partition-aware validation,
- database-side SQL,
- incremental checks,
- metadata-based checks,
- sampling for suitable rules,
- historical baselines,
- targeted expensive checks,
- execution cost.

Critical integrity checks may require full evaluation, but the implementation should exploit the data platform's execution engine.

---

## 45.5 How would you design ownership?

Each rule should have:

```text
rule ID
dataset
owner
severity
action
threshold
documentation
```

Ownership should map to the team capable of fixing the underlying producer or transformation.

---

## 45.6 How would you manage tool churn?

Establish a rule:

> New validation tooling requires a concrete capability gap, migration plan, ownership model, and measurable benefit.

Avoid running multiple frameworks indefinitely for the same rule without a reason.

---

# 46. Final Practical Challenge

## Problem

You receive a production-style `orders` dataset containing several unknown defects.

Your task is to design a declarative quality system.

## Requirements

You must:

- define at least 15 rules,
- classify severity,
- choose thresholds,
- implement GX checks,
- implement SodaCL checks,
- implement at least two SQL checks,
- execute checks,
- inspect failures,
- inject defects,
- record results,
- define pipeline-gate behavior,
- explain why each rule exists,
- identify which checks should block publication.

---

## Hints

Start with:

```text
schema
↓
completeness
↓
uniqueness
↓
validity
↓
volume
↓
freshness
↓
business invariants
↓
referential integrity
↓
severity
↓
gate
```

Then ask:

```text
Which rules are local?
Which rules are relational?
Which rules are expensive?
Which rules are critical?
```

---

## Expected behavior

A mature solution should produce something similar to:

```text
Validation result
        ↓
Rule ID
        ↓
Observed metric
        ↓
Threshold
        ↓
Status
        ↓
Severity
        ↓
Action
```

---

## Complete solution design

A reasonable implementation would include:

```text
R001 required schema
R002 order_id not null
R003 order_id unique
R004 customer_id completeness
R005 quantity positive
R006 unit_price non-negative
R007 currency validity
R008 status validity
R009 row count
R010 freshness
R011 total amount invariant
R012 customer referential integrity
R013 timestamp validity
R014 optional-field completeness
R015 duplicate-rate policy
```

Then map:

```text
GX/Soda
    → generic dataset checks

SQL
    → relational/business invariants

Quality policy
    → severity/action

History
    → operational trend
```

---

# 47. Common Mistakes

## Treating checks as documentation only

A rule that never affects operations may have little practical value.

---

## No pipeline action

A failed check must have an intentional policy:

```text
log
warn
alert
block
quarantine
```

---

## Arbitrary thresholds

Thresholds should be evidence-based.

---

## Too many checks

More checks increase:

- runtime,
- maintenance,
- false alarms,
- cognitive load.

---

## Too few checks

Insufficient coverage lets defects escape.

---

## Duplicate rules

Avoid implementing the same invariant in multiple frameworks without a deliberate reason.

---

## Unclear ownership

Every important rule should have an owner.

---

## No historical results

Without history, quality deterioration can remain invisible.

---

## No version pinning

Framework upgrades can break validation behavior.

---

## Expensive SQL

A theoretically useful check can become operationally damaging if it scans enormous datasets repeatedly.

---

## Unreadable SodaCL

Declarative configuration should improve readability, not make rules cryptic.

---

## Framework-specific lock-in

Avoid scattering framework-specific behavior throughout unrelated business logic.

---

## Blindly copying outdated GX examples

Always inspect the installed GX version.

---

## Silently ignoring warnings

Warnings should be intentionally actionable or intentionally informational.

---

## One tool for every problem

Use the validation layer that fits the data and failure mode.

---

## Assuming a passing check means the dataset is fully correct

A passing check only means the tested rule passed.

```text
Passing checks
    ≠
Complete correctness
```

---

## No defect injection

If you never test failures, you do not know whether your quality system actually catches them.

---

## No validator tests

A validator itself can contain bugs.

---

## No maintenance process

Rules must evolve with the data product and business requirements.

---

# 48. Production Checklist

## Rule Design

- [ ] Business rule identified.
- [ ] Failure mode understood.
- [ ] Metric defined.
- [ ] Threshold justified.
- [ ] Severity defined.
- [ ] Action defined.

## Implementation

- [ ] Check implemented.
- [ ] SQL tested where applicable.
- [ ] Framework API verified against the installed version.
- [ ] Naming standardized.
- [ ] Rule ID assigned.

## Operations

- [ ] Quality gate defined.
- [ ] Alerts defined.
- [ ] Historical results retained.
- [ ] Ownership defined.
- [ ] Failure investigation process defined.

## Testing

- [ ] Valid dataset tested.
- [ ] Invalid dataset tested.
- [ ] Boundary conditions tested.
- [ ] Defect injection tested.
- [ ] SQL checks tested.
- [ ] Thresholds tested.

## Production

- [ ] Performance measured.
- [ ] Dependency versions pinned.
- [ ] Upgrade strategy defined.
- [ ] Duplicate checks removed or intentionally justified.
- [ ] Obsolete checks removed.
- [ ] Tool choice justified.

---

# 49. Final Mental Model

Declarative data quality means:

```text
Define the rule
      ↓
Execute the rule
      ↓
Observe the metric
      ↓
Compare with expectation
      ↓
Assign severity
      ↓
Take action
      ↓
Record the result
      ↓
Learn from history
```

Remember the role of each layer:

```text
Pandera
    → DataFrame-oriented validation

Great Expectations
    → Expectation-driven declarative validation

Soda / SodaCL
    → Configuration-oriented data-quality checks

SQL
    → Highly expressive data-source validation

Database constraints
    → Database-level integrity enforcement
```

The production question is not:

> **Which tool is the best?**

The better engineering question is:

> **Which validation layer and tool best fit this data, failure mode, ownership model, and operational cost?**

That question leads to maintainable quality architecture.

---

# 50. Code Quality Requirements

All examples in this chapter should be:

- readable by a beginner,
- compatible with modern Python,
- PEP 8 oriented,
- meaningful in naming,
- explicit about important lines,
- free of unnecessary abstraction,
- runnable or clearly labeled conceptual/pseudocode,
- explicit about dependencies,
- free of fabricated output,
- free of fabricated benchmark numbers.

For important framework APIs:

1. Explain the concept.
2. Show representative syntax.
3. Show a small example.
4. Show a realistic example.
5. Show failure behavior.
6. Explain production considerations.

Where an API is version-sensitive, the example is intentionally conceptual unless the installed environment has been verified.

---

# 51. Version Accuracy Requirements

Before using framework-specific examples in a real project:

```text
Inspect installed version
        ↓
Read current API/documentation
        ↓
Use supported syntax
        ↓
Run a minimal validation
        ↓
Add regression tests
        ↓
Pin the tested dependency
```

Especially for Great Expectations:

- do not blindly copy obsolete APIs,
- do not invent framework concepts,
- identify version-sensitive behavior,
- prefer currently supported APIs,
- explain terminology differences when they matter.

A code sample that merely looks correct is not production-quality teaching material.

---

# 52. Learning Loop

For every major quality rule, use this loop:

```text
Read the concept
      ↓
Understand why it exists
      ↓
Identify the failure mode
      ↓
Define the quality rule
      ↓
Implement the check
      ↓
Run the check
      ↓
Inject a defect
      ↓
Confirm the check catches it
      ↓
Decide severity/action
      ↓
Measure operational cost
      ↓
Explain the result
      ↓
Apply it to production architecture
```

This prevents syntax-first learning.

The goal is not to memorize framework commands.

The goal is to learn how to design and operate reliable data-quality systems.

---

# 53. Completion Criteria

You are ready to move beyond this topic when you can independently:

- explain declarative validation from first principles,
- distinguish expectations/checks from pipeline policy,
- explain GX's conceptual architecture,
- explain SodaCL's conceptual architecture,
- define useful checks for common quality dimensions,
- justify thresholds,
- assign severity based on operational impact,
- build a quality gate,
- validate Parquet through an analytical engine,
- validate PostgreSQL using database-side SQL,
- write relational business checks,
- retain and interpret historical results,
- debug failed checks,
- test validators with injected defects,
- reason about validation cost,
- compare Pandera, GX, Soda, SQL, and constraints,
- prevent duplicate rules,
- manage framework upgrades,
- design ownership,
- explain tool churn,
- design a production declarative quality architecture.

---

# Final Engineering Principle

A mature data-quality system is not a pile of assertions.

It is a controlled feedback loop:

```text
Business rule
      ↓
Executable quality check
      ↓
Observed evidence
      ↓
Severity and policy
      ↓
Pipeline action
      ↓
Historical record
      ↓
Trend / incident learning
      ↓
Rule maintenance
```

The framework is an implementation detail.

The engineering discipline is the real skill.
