# Lookups, Enrichment and Reference Data

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain reference data, master data, transactional data, lookup, join, and enrichment;
- enrich transactional and event data safely with reference information;
- validate lookup-key uniqueness before joining;
- detect and prevent join fan-out;
- define explicit policies for missing matches;
- measure enrichment coverage and cardinality;
- distinguish current-state enrichment from historical point-in-time enrichment;
- perform SCD-style and effective-dated lookups;
- implement enrichment with Python, Polars, DuckDB, and SQL;
- choose dictionary, DataFrame, SQL, broadcast, or partitioned lookup strategies;
- design external enrichment with caching, TTL, batching, rate limits, and bounded concurrency;
- recognize when simple equality matching is insufficient and entity resolution is required;
- detect reference-data changes and perform targeted historical backfills;
- test deterministic enrichment pipelines;
- debug fan-out, missing-match, temporal, external-service, and cost failures;
- design production-grade enrichment architectures.

The central principle is:

> A production enrichment is not merely a join. It is a controlled dependency on another dataset or system.

---

## 2. Prerequisites

This chapter assumes you already understand:

- deterministic transformation pipelines;
- partition-scoped processing;
- deduplication;
- merge/upsert strategies;
- incremental processing and backfills;
- late-arriving data and reprocessing windows;
- deterministic hashing;
- Python data processing;
- basic SQL joins;
- DataFrame operations.

The dependency chain for this module is:

```text
01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09
```

The previous topics established how to make transformations repeatable and deterministic. This chapter adds another important dimension: **safe dependency management during transformation**.

---

## 3. What Is Enrichment?

Enrichment means adding trusted contextual information to a dataset by matching each record against reference, master, dimensional, or external data.

A simple example:

```text
order
  +
product reference
  ↓
enriched order
```

Another:

```text
event
  +
country mapping
  ↓
enriched event
```

Another:

```text
transaction
  +
historical FX rate
  ↓
currency-normalized transaction
```

The basic idea is easy.

The production problem is harder.

A lookup is correct only when:

1. the lookup key is appropriate;
2. the lookup key has the expected cardinality;
3. the matching rule is correct;
4. the correct version of the reference data is selected;
5. missing matches are handled deliberately;
6. the result remains deterministic;
7. the dependency is fresh enough;
8. external calls are bounded and controlled when applicable;
9. the enrichment can be reproduced and audited.

The production mental model is:

```text
Source Data
    ↓
Define Enrichment Contract
    ↓
Validate Lookup Data
    ↓
Choose Lookup Strategy
    ↓
Match Records
    ↓
Handle Missing Matches
    ↓
Validate Coverage
    ↓
Apply Temporal Rules if Needed
    ↓
Cache External Enrichment if Needed
    ↓
Measure Quality + Cost
    ↓
Produce Enriched Dataset
```

---

## 4. What Is Reference Data?

Reference data is data used to give standardized meaning, classification, or context to other datasets.

Examples include:

- country codes;
- currency codes;
- product categories;
- status mappings;
- tax codes;
- calendars;
- business classifications;
- geographic mappings;
- standardized code lists.

Reference data is often:

- smaller than fact data;
- relatively stable;
- shared by multiple pipelines;
- owned by another team or system;
- versioned;
- required for semantic consistency.

### Reference data vs transactional data

**Reference data** describes meanings or classifications.

```text
status_code | status_name
------------|------------
A           | Active
I           | Inactive
S           | Suspended
```

**Transactional data** represents business events.

```text
order_id | customer_id | amount | order_time
---------|-------------|--------|-----------
1001     | C001        | 50     | 2025-03-10
```

### Reference data vs master data

Master data represents core business entities:

- customers;
- products;
- suppliers;
- stores;
- organizations.

Master data can be larger, more dynamic, and more operationally important than a simple code list.

A product master may contain:

```text
product_id
sku
product_name
brand
category
supplier_id
status
```

It should therefore not automatically be treated as a Python dictionary.

---

## 5. Lookup vs Join vs Enrichment

These terms overlap, but they describe different levels of abstraction.

### Lookup

A lookup answers:

> Given this key, what information corresponds to it?

```text
P101 → Laptop
```

### Join

A join is the relational operation used to combine datasets.

```sql
SELECT
    o.order_id,
    p.category
FROM orders o
LEFT JOIN products p
    ON o.product_id = p.product_id;
```

### Enrichment

Enrichment is the business transformation:

> Add trusted product context to each order while preserving the required grain and historical correctness.

The distinction matters because a technically valid join can still be a semantically incorrect enrichment.

For example, this query may execute successfully:

```sql
SELECT *
FROM orders o
LEFT JOIN customer c
  ON o.customer_id = c.customer_id;
```

But if `customer` contains multiple rows per customer because it is historical data, the join may:

- duplicate orders;
- select the wrong customer version;
- inflate revenue;
- produce nondeterministic results.

---

## 6. Common Reference Data Patterns

Common reference datasets include:

| Pattern | Example |
|---|---|
| Static code list | status code → status name |
| Master data | product → category |
| SCD dimension | customer → country over time |
| Time-varying reference | currency → FX rate |
| Mapping table | postal code → region |
| Calendar | date → fiscal period |
| External reference | IP → country |
| Business classification | SKU → business category |

The correct enrichment technique depends on:

- size;
- uniqueness;
- update frequency;
- historical requirements;
- latency requirements;
- ownership;
- operational cost.

---

## 7. Static Code Lists

A static code list is a small mapping that changes infrequently.

Example:

```text
status_code | status_name
------------|------------
A           | Active
I           | Inactive
S           | Suspended
```

A Python dictionary is often sufficient:

```python
status_map = {
    "A": "Active",
    "I": "Inactive",
    "S": "Suspended",
}
```

The lookup is simple:

```python
status_map["A"]
# "Active"
```

### When a dictionary works well

Use a dictionary when:

- the mapping is small;
- it is stable;
- it fits comfortably in memory;
- the mapping is versioned with code/configuration;
- temporal behavior is not required.

### When a dictionary becomes inappropriate

A dictionary becomes a poor choice when:

- the reference contains millions of rows;
- it changes frequently;
- multiple teams own it;
- it requires effective dates;
- it requires database governance;
- you need audit history;
- the lookup is too large for worker memory.

A tiny static mapping and a customer master are both "lookups", but they have very different engineering requirements.

---

## 8. Master Data

Master data represents core business entities such as:

- customers;
- products;
- suppliers;
- stores;
- countries;
- organizations.

A master record may have:

```text
entity_id
name
status
attributes
effective_dates
source_system
updated_at
```

Production concerns include:

- stable identifiers;
- source ownership;
- updates;
- duplicate entities;
- versioning;
- quality contracts;
- source-system conflicts.

For example, a product may exist in an ERP system, commerce platform, and supplier system.

You need to know which identifier is authoritative.

A lookup that silently combines conflicting sources can create semantic corruption even when every SQL join is syntactically valid.

---

## 9. Slowly Changing Dimension Lookups

A dimension can change over time.

Suppose:

```text
customer_id | country
------------|--------
C123        | India
```

Later it becomes:

```text
customer_id | country
------------|---------
C123        | Singapore
```

If you enrich every historical order using only the current customer record, old orders can be assigned the new country.

For historical correctness, use a versioned representation such as SCD Type 2:

```text
customer_id | valid_from | valid_to   | country
------------|------------|------------|---------
C123        | 2025-01-01 | 2025-06-01 | India
C123        | 2025-06-01 | NULL       | Singapore
```

An order on:

```text
2025-03-10
```

belongs to the India version.

This is different from a current-state lookup.

### Current-state lookup

```text
customer_id → current attributes
```

### Historical lookup

```text
(customer_id, event_time) → attributes valid at event_time
```

The second form is required when historical correctness matters.

---

## 10. Time-Varying Reference Data

Some reference data changes according to effective time.

Examples:

- FX rates;
- tax rates;
- pricing;
- exchange rates;
- calendar definitions;
- geographic assignments.

The lookup key may therefore require:

```text
lookup_key + effective_time
```

Example:

```text
currency | effective_from | rate
---------|----------------|------
EUR      | 2025-03-01     | 1.08
EUR      | 2025-03-10     | 1.10
```

A transaction on March 5 should not automatically use the March 10 rate.

The correct record depends on the business time of the transaction.

---

## 11. Reference Data Sources and Ownership

Every important reference dataset should have an explicit ownership contract.

At minimum define:

| Attribute | Example |
|---|---|
| Owner | Finance Data Team |
| Source | ERP |
| Update frequency | Daily |
| Schema contract | Versioned |
| Freshness expectation | < 24 hours |
| Key | product_id |
| Uniqueness | Exactly one current row |
| Versioning | SCD2 |
| Quality rules | No null product IDs |

Ownership answers:

> Who is responsible when the enrichment breaks?

Without ownership, a pipeline can fail because of a dependency that nobody realizes they own.

---

## 12. Lookup-Key Uniqueness

This is one of the most important production concepts.

> A lookup key must be unique when the enrichment expects one output row per input row.

Suppose:

```text
orders
-------
order_id | product_id
1        | P101
```

and:

```text
product_reference
-----------------
product_id | category
P101       | Laptop
P101       | Electronics
```

One input row now matches two lookup rows.

The result becomes:

```text
order row
   ↓
two matches
   ↓
two output rows
```

This is join fan-out.

### Polars validation

```python
import polars as pl

duplicates = (
    products
    .group_by("product_id")
    .len()
    .filter(pl.col("len") > 1)
)

if duplicates.height > 0:
    raise ValueError("Lookup key is not unique")
```

### SQL validation

```sql
SELECT
    product_id,
    COUNT(*) AS row_count
FROM product_reference
GROUP BY product_id
HAVING COUNT(*) > 1;
```

The uniqueness rule should be treated as a **data contract**, not an informal assumption.

---

## 13. Preventing Join Fan-Out

Fan-out occurs when one source row matches multiple lookup rows.

For example:

```text
1 million orders
        +
duplicate product keys
        ↓
1.8 million enriched rows
```

The extra rows can silently corrupt:

- counts;
- revenue;
- averages;
- downstream joins;
- aggregates.

### Cardinality invariant

For a many-to-one enrichment:

```text
output_rows == input_rows
```

This is useful but not sufficient.

You should also validate:

- key uniqueness;
- null behavior;
- expected match rate;
- duplicate output keys;
- business invariants.

### Detect unexpected growth

```python
input_rows = orders.height
output_rows = enriched.height

if output_rows != input_rows:
    raise ValueError(
        f"Unexpected enrichment cardinality: "
        f"{input_rows=} {output_rows=}"
    )
```

A row-count check detects many fan-out failures, but it does not prove semantic correctness. A join can preserve row count while attaching the wrong version.

---

## 14. Missing-Match Policies

Suppose:

```text
order.product_id = P999
```

but P999 is absent from the reference table.

There is no universal answer for what should happen.

### Policy 1 — Unknown/default

```text
category = UNKNOWN
```

Useful when downstream systems can safely represent an unknown entity.

### Policy 2 — Flag

```text
lookup_missing = true
```

Useful when the record can continue but the data-quality issue must remain visible.

### Policy 3 — Quarantine

Move unmatched records to a separate dataset.

Useful when downstream consumers must receive only trusted enriched records.

### Policy 4 — Fail

Stop the pipeline.

Useful when a missing match represents a critical contract violation.

### Choosing the policy

Ask:

1. Is the reference mandatory?
2. Is an unknown value semantically valid?
3. Can downstream consumers operate safely?
4. Is missing data expected during normal operation?
5. Is the missing match recoverable?
6. Does continuing create misleading business output?

Do not universally default to `UNKNOWN`, and do not universally fail.

---

## 15. Enrichment Coverage Metrics

Define:

```text
coverage =
matched_records / total_records
```

For example:

```text
1,000,000 orders
990,000 matched

coverage = 99%
missing   = 1%
```

Track at least:

```text
lookup_match_rate
lookup_missing_rate
unknown_key_count
quarantined_record_count
```

A 99% match rate may be acceptable for one enrichment and unacceptable for another.

For a mandatory product master, 99% may represent a serious data-quality failure.

For an optional enrichment from a third-party service, 99% might be operationally acceptable.

The threshold is part of the enrichment contract.

---

## 15. Missing-Match Analysis

A missing match can have many causes:

- bad source ID;
- stale reference data;
- late reference data;
- deleted entity;
- schema mismatch;
- whitespace;
- casing differences;
- wrong source system;
- genuinely unknown entity.

For example:

```text
source: "P101 "
reference: "P101"
```

A direct equality comparison fails.

A useful investigation workflow is:

```text
Missing Match
    ↓
Check normalization
    ↓
Check source identifier
    ↓
Check reference freshness
    ↓
Check reference ownership
    ↓
Check late-arriving reference data
    ↓
Determine expected vs unexpected absence
```

Do not solve every missing-match problem by blindly normalizing strings. Normalization itself must be part of the documented matching contract.

---

## 16. Point-in-Time / As-Of Lookups

For a fact:

```text
event_time = 2025-03-05
```

find the reference record where:

```text
valid_from <= event_time
AND
event_time < valid_to
```

with an open-ended current record represented by `NULL`.

SQL example:

```sql
SELECT
    o.order_id,
    o.order_date,
    c.country
FROM orders o
JOIN customer_history c
  ON o.customer_id = c.customer_id
 AND o.order_date >= c.valid_from
 AND (
        o.order_date < c.valid_to
        OR c.valid_to IS NULL
     );
```

### What each condition does

```sql
o.customer_id = c.customer_id
```

finds the entity.

```sql
o.order_date >= c.valid_from
```

ensures the version has started.

```sql
o.order_date < c.valid_to
```

ensures the version has not ended.

```sql
c.valid_to IS NULL
```

allows the current version.

The boundaries should be designed deliberately. A common convention is a half-open interval:

```text
[valid_from, valid_to)
```

meaning:

```text
valid_from <= event_time < valid_to
```

This prevents adjacent versions from overlapping at their boundary.

---

## 17. Historical Correctness

Consider:

```text
C123
India:      Jan 1 → Jun 1
Singapore:  Jun 1 → current
```

and:

```text
order_date = Mar 15
customer_id = C123
```

The correct historical result is:

```text
country = India
```

even though the current customer country is Singapore.

The core rule is:

> Historical enrichment must use the reference value that was valid for the fact's business time.

This matters for:

- financial reporting;
- tax calculations;
- regulatory reporting;
- customer segmentation;
- historical analytics;
- revenue attribution.

---

## 18. Versioned Reference Data

Reference data can be versioned through:

- effective dates;
- version numbers;
- snapshots;
- SCD2 tables;
- Git-versioned files;
- database tables;
- object-storage snapshots.

Versioning improves:

### Reproducibility

You can determine which reference state produced an output.

### Auditability

You can explain why an enriched value existed.

### Rollback

You can restore a known-good reference version.

### Historical reconstruction

You can reproduce previous results when required.

A production pipeline should avoid relying on an undocumented mutable "current" lookup when historical reproducibility matters.

---

## 19. Python / Polars Enrichment

Start with the simple case.

```python
import polars as pl

orders = pl.DataFrame(
    {
        "order_id": [1, 2, 3],
        "product_id": ["P101", "P102", "P101"],
        "amount": [50, 80, 25],
    }
)

products = pl.DataFrame(
    {
        "product_id": ["P101", "P102"],
        "category": ["Laptop", "Phone"],
    }
)

enriched = orders.join(
    products,
    on="product_id",
    how="left",
)

print(enriched)
```

Expected result:

```text
order_id | product_id | amount | category
---------|------------|--------|---------
1        | P101       | 50     | Laptop
2        | P102       | 80     | Phone
3        | P101       | 25     | Laptop
```

The left join preserves the order rows.

### Validate first

```python
duplicate_keys = (
    products
    .group_by("product_id")
    .len()
    .filter(pl.col("len") > 1)
)

if duplicate_keys.height:
    raise ValueError("Product lookup is not unique")
```

Then perform the join.

### Validate cardinality

```python
if enriched.height != orders.height:
    raise ValueError("Unexpected fan-out")
```

### Validate missing matches

```python
enriched = enriched.with_columns(
    pl.col("category")
    .is_null()
    .alias("lookup_missing")
)
```

---


### Optional configuration validation with Pydantic

When enrichment definitions are configuration-driven, Pydantic can validate the configuration before execution.

```python
from pydantic import BaseModel


class LookupConfig(BaseModel):
    name: str
    key: str
    missing_policy: str
    temporal: bool = False
```

Pydantic validates the enrichment contract; it does not replace runtime reference-data quality checks.

## 20. DuckDB / SQL Enrichment

The equivalent SQL is:

```sql
SELECT
    o.*,
    p.category
FROM orders o
LEFT JOIN products p
    ON o.product_id = p.product_id;
```

Validate the lookup first:

```sql
SELECT
    product_id,
    COUNT(*) AS row_count
FROM products
GROUP BY product_id
HAVING COUNT(*) > 1;
```

Validate missing matches:

```sql
SELECT
    COUNT(*) AS missing_products
FROM orders o
LEFT JOIN products p
    ON o.product_id = p.product_id
WHERE p.product_id IS NULL;
```

Validate fan-out:

```sql
SELECT
    COUNT(*) AS input_rows
FROM orders;
```

and compare with the output relation:

```sql
SELECT
    COUNT(*) AS output_rows
FROM enriched_orders;
```

For relational transformation pipelines, SQL is often preferable when:

- the data already resides in a database or warehouse;
- the lookup is large;
- SQL query planning is valuable;
- the transformation belongs naturally in the analytical layer;
- you need database-native indexing, partitioning, or execution.

---

## 21. Dictionary-Based Lookups

A tiny mapping can be represented as:

```python
country_map = {
    "IN": "India",
    "SG": "Singapore",
    "US": "United States",
}
```

With Polars:

```python
df = df.with_columns(
    pl.col("country_code")
      .replace(country_map)
      .alias("country_name")
)
```

Dictionary lookup is appropriate for:

- tiny static mappings;
- simple transformations;
- low-complexity code lists;
- versioned configuration.

It becomes a poor choice for:

- millions of rows in the lookup;
- frequently changing reference data;
- temporal lookup;
- complex ownership;
- governed shared reference data.

---

## 22. Choosing the Lookup Implementation

| Situation | Suitable approach |
|---|---|
| Tiny static mapping | Python dictionary |
| Small reference table | DataFrame join |
| Large relational reference | SQL join |
| Historical dimension | Temporal/as-of join |
| External API | Cached enrichment |
| Huge distributed datasets | Broadcast or partitioned join depending on size/skew |
| Frequently changing master data | Managed reference dataset |

Consider:

- data size;
- update frequency;
- latency;
- correctness requirements;
- ownership;
- infrastructure;
- memory constraints;
- historical requirements.

The word "lookup" does not imply that the lookup table is small.

---

## 23. Large Lookup Tables

A large lookup changes the engineering problem.

Consider:

```text
500 GB reference table
+
1 TB fact table
```

A Python dictionary is obviously inappropriate.

Now consider:

- memory pressure;
- network movement;
- join strategy;
- partitioning;
- indexes;
- clustering;
- broadcast;
- shuffles;
- key skew.

The right question is not:

> Is this a lookup?

The right question is:

> What execution strategy minimizes cost while preserving the required correctness?

---

## 24. Broadcast vs Partitioned Joins

A broadcast join conceptually does this:

```text
Large fact
     +
Small lookup
     ↓
Broadcast lookup to workers
```

Instead of repeatedly moving the large fact dataset, the smaller relation is copied to workers.

### Benefits

- potentially less shuffle;
- lower network movement;
- potentially faster joins.

### Risks

- lookup too large for worker memory;
- key skew;
- stale cached lookup;
- cluster memory pressure.

Broadcast is not always better.

### Partitioned/distributed join

When the lookup is too large to broadcast, data can be partitioned by join key:

```text
hash(key) → partition
```

Conceptually:

```text
Fact partition 0   ←→ Lookup partition 0
Fact partition 1   ←→ Lookup partition 1
Fact partition 2   ←→ Lookup partition 2
```

This can avoid broadcasting the entire lookup but may introduce shuffle cost.

### Partitioned join concerns

- skewed keys;
- uneven partition sizes;
- network shuffle;
- partition count;
- co-location;
- storage layout.

The decision depends on actual data distribution, not a generic rule.

---

## 25. External Enrichment

External enrichment obtains information from another service.

Examples:

```text
IP address
    ↓
GeoIP service
    ↓
country
```

or:

```text
product_id
    ↓
external catalog API
    ↓
category
```

External enrichment is operationally more dangerous than a local join because it introduces:

- network latency;
- API failures;
- rate limits;
- cost;
- nondeterminism;
- service changes;
- availability dependencies;
- authentication requirements.

A local table can usually be retried cheaply.

An external API may charge for every request.

---

## 26. Never Hide Unbounded API Calls Inside a Row Transformation

Avoid this pattern:

```python
df.map_rows(lambda row: external_api(row["ip"]))
```

for millions of rows.

It can create:

- millions of network requests;
- uncontrolled concurrency;
- retry storms;
- rate-limit violations;
- cost explosions;
- slow pipelines;
- difficult recovery.

The production pattern is:

```text
Extract unique keys
        ↓
Deduplicate keys
        ↓
Batch/cache external calls
        ↓
Persist enrichment results
        ↓
Join locally
```

This separates external side effects from deterministic transformation logic.

---

## 27. Caching External Enrichment

A cache prevents the same key from repeatedly triggering external requests.

```text
IP address
    ↓
cache lookup
    ↓
hit ──→ reuse
miss
    ↓
API call
    ↓
persist result
```

Possible cache locations:

- local file;
- object storage;
- database table;
- Redis;
- durable enrichment table.

For repeatable Data Engineering pipelines, a durable enrichment table is often useful because it provides:

- persistence;
- auditability;
- reuse across runs;
- easier reconciliation;
- lower repeated external cost.

A cache should have an explicit freshness policy.

---

## 28. Cache TTL

TTL means **Time To Live**.

For example:

```text
IP → country
TTL = 7 days
```

Possible strategies:

### Short TTL

Useful when external data changes frequently.

Trade-off:

- fresher data;
- more external calls.

### Long TTL

Useful when values change rarely.

Trade-off:

- fewer calls;
- higher stale-data risk.

### Immutable reference

If the external result is effectively immutable, a permanent cache may be appropriate, subject to the source's actual semantics.

There is no universal TTL.

TTL should reflect:

- source volatility;
- business tolerance for staleness;
- cost;
- contractual freshness;
- historical reproducibility.

---

## 29. Rate Limits and Cost Controls

Suppose an API allows:

```text
100 requests/minute
```

while the pipeline can generate:

```text
10,000 requests/minute
```

The pipeline must enforce the external system's limits.

Production controls include:

- rate limiting;
- bounded concurrency;
- batching;
- retries with backoff;
- caching;
- request deduplication;
- checkpointing.

These connect directly to concurrency concepts learned earlier.

The goal is not maximum request concurrency.

The goal is:

> maximum safe throughput under the dependency's constraints.

### Cost model

Suppose an API charges:

```text
$0.001/request
```

and there are:

```text
10,000,000 unique keys
```

Then the illustrative cost is:

```text
10,000,000 × $0.001 = $10,000
```

If the raw dataset contains 100 million rows but only 10 million unique keys, deduplication can reduce the external request volume by 90%.

Caching can reduce it further across repeated pipeline runs.

---

## 30. Entity Resolution Awareness

Simple equality matching assumes:

```text
left.name == right.name
```

But these values may represent the same organization:

```text
"Acme Ltd"
"ACME LIMITED"
"Acme Limited."
```

Ordinary equality joins may fail.

Entity resolution may involve:

- canonicalization;
- deterministic matching;
- fuzzy matching awareness;
- master identifiers;
- confidence scores;
- manual review.

For example, canonicalization might normalize whitespace and punctuation before matching.

However, this chapter is not a full entity-resolution course.

The key engineering lesson is:

> Recognize when the problem is no longer a normal lookup.

Do not silently replace deterministic joins with fuzzy matching without defining the matching contract and handling false positives.

---

## 31. Reference Data Changes and Historical Backfills

Reference data changes.

Examples:

- product category renamed;
- tax rate corrected;
- country mapping updated;
- customer master corrected;
- FX rate corrected.

The pipeline must define what happens to historical facts.

Possible policies include:

1. historical outputs remain unchanged;
2. historical outputs are automatically restated;
3. affected history is reprocessed;
4. correction is applied only from an effective date;
5. a new version of the reference is used for future processing.

There is no universal answer.

The correct behavior depends on:

- business time;
- effective time;
- accounting rules;
- downstream expectations;
- audit requirements;
- backfill policy.

---

## 30A. Targeted Historical Backfills

Suppose a product category mapping changed on:

```text
2025-04-01
```

Do not automatically rebuild all history if only a small set of products was affected.

A targeted approach is:

```text
Changed reference data
        ↓
Identify affected keys
        ↓
Identify affected partitions
        ↓
Reprocess only affected history
        ↓
Validate
```

For example:

```python
affected_products = {"P101", "P204"}

affected_orders = orders.filter(
    pl.col("product_id").is_in(list(affected_products))
)
```

In a partitioned production system, the affected products can then be mapped to affected date partitions.

The objective is to minimize unnecessary computation while making the restatement auditable.

---

## 31A. Safe Reference-Data Enrichment Workflow

A production workflow is:

```text
Reference Source
      ↓
Validate Schema
      ↓
Validate Key Uniqueness
      ↓
Validate Freshness
      ↓
Version / Snapshot
      ↓
Enrich Fact Data
      ↓
Measure Coverage
      ↓
Validate Row Cardinality
      ↓
Validate Business Rules
      ↓
Publish
```

### Step 1 — Validate schema

Check:

- required columns;
- types;
- nullability;
- schema version.

### Step 2 — Validate uniqueness

Check the expected lookup grain.

### Step 3 — Validate freshness

Check whether the reference is recent enough for the pipeline.

### Step 4 — Version/snapshot

Preserve the reference state required for reproducibility.

### Step 5 — Enrich

Perform the deterministic lookup.

### Step 6 — Measure coverage

Calculate matched and missing records.

### Step 7 — Validate cardinality

Check for fan-out.

### Step 8 — Validate business rules

Examples:

```text
tax_rate >= 0
currency is recognized
country_code is valid
```

### Step 9 — Publish

Only publish after the enrichment contract passes.

---

# 32. Hands-On Implementation

We will build a complete conceptual enrichment pipeline using:

```text
orders
products
customer_history
fx_rates
```

and a simulated external:

```text
IP → country
```

## 35.1 Source Data

```python
import polars as pl

orders = pl.DataFrame(
    {
        "order_id": [1001, 1002, 1003, 1004],
        "product_id": ["P101", "P102", "P101", "P999"],
        "customer_id": ["C123", "C123", "C456", "C456"],
        "order_date": [
            "2025-03-05",
            "2025-03-10",
            "2025-07-10",
            "2025-07-11",
        ],
        "currency": ["EUR", "EUR", "USD", "EUR"],
        "amount": [100.0, 200.0, 50.0, 75.0],
        "ip": ["1.1.1.1", "2.2.2.2", "1.1.1.1", "9.9.9.9"],
    }
).with_columns(
    pl.col("order_date").str.to_date()
)

products = pl.DataFrame(
    {
        "product_id": ["P101", "P102"],
        "category": ["Laptop", "Phone"],
        "brand": ["BrandA", "BrandB"],
    }
)
```

Expected product reference:

```text
product_id | category | brand
------------|----------|-------
P101       | Laptop   | BrandA
P102       | Phone    | BrandB
```

---

## 35.2 Step 1 — Validate Product-Key Uniqueness

```python
duplicate_products = (
    products
    .group_by("product_id")
    .len()
    .filter(pl.col("len") > 1)
)

if duplicate_products.height:
    raise ValueError(
        "Product reference contains duplicate product_id values"
    )
```

Expected result:

```text
No duplicate keys
```

---

## 35.3 Step 2 — Product Enrichment

```python
enriched = orders.join(
    products,
    on="product_id",
    how="left",
)
```

Expected shape:

```text
4 input rows
4 output rows
```

P999 has no product reference, so its product attributes are null.

---

## 35.4 Step 3 — Detect Missing Products

```python
enriched = enriched.with_columns(
    pl.col("category")
      .is_null()
      .alias("product_lookup_missing")
)
```

Expected:

```text
P999 → missing
```

Now select the policy.

For this example we will keep the record but explicitly flag it:

```python
enriched = enriched.with_columns(
    pl.col("category")
      .fill_null("UNKNOWN")
      .alias("category")
)
```

The important point is not that `UNKNOWN` is always correct. The important point is that the policy is deliberate.

---

## 35.5 Step 4 — Calculate Coverage

```python
coverage = (
    enriched
    .select(
        (
            (~pl.col("product_lookup_missing")).mean()
        ).alias("lookup_match_rate")
    )
    .item()
)

print(coverage)
```

For the sample:

```text
3 matched / 4 total = 75%
```

A production pipeline should compare the result against a configured threshold.

---

## 35.6 Step 5 — Customer Historical Enrichment

Create SCD-style customer history:

```python
customer_history = pl.DataFrame(
    {
        "customer_id": ["C123", "C123", "C456"],
        "valid_from": [
            "2025-01-01",
            "2025-06-01",
            "2025-01-01",
        ],
        "valid_to": [
            "2025-06-01",
            None,
            None,
        ],
        "country": [
            "India",
            "Singapore",
            "United States",
        ],
    }
).with_columns(
    pl.col("valid_from").str.to_date(),
    pl.col("valid_to").str.to_date(),
)
```

A conceptual point-in-time join can be performed using a range-aware join strategy or by generating candidate matches and filtering the validity interval.

A simple SQL implementation is often clearer:

```sql
SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    c.country
FROM orders o
LEFT JOIN customer_history c
    ON o.customer_id = c.customer_id
   AND o.order_date >= c.valid_from
   AND (
       o.order_date < c.valid_to
       OR c.valid_to IS NULL
   );
```

The order from March 5 for C123 should receive:

```text
India
```

The order from July for C123 would receive:

```text
Singapore
```

---

## 35.7 Step 6 — FX As-Of Lookup

Create time-varying FX data:

```python
fx_rates = pl.DataFrame(
    {
        "currency": ["EUR", "EUR", "USD"],
        "effective_from": [
            "2025-03-01",
            "2025-03-10",
            "2025-01-01",
        ],
        "rate_to_usd": [1.08, 1.10, 1.00],
    }
).with_columns(
    pl.col("effective_from").str.to_date()
)
```

For:

```text
EUR
2025-03-05
```

the correct rate is:

```text
1.08
```

not:

```text
1.10
```

A SQL pattern is:

```sql
SELECT
    o.order_id,
    o.currency,
    o.order_date,
    r.rate_to_usd,
    o.amount * r.rate_to_usd AS amount_usd
FROM orders o
LEFT JOIN fx_rates r
    ON o.currency = r.currency
   AND r.effective_from <= o.order_date;
```

That query can produce multiple candidate rates when several historical records qualify, so it must be constrained to the latest effective rate.

One robust pattern is:

```sql
SELECT
    order_id,
    currency,
    order_date,
    rate_to_usd,
    amount,
    amount * rate_to_usd AS amount_usd
FROM (
    SELECT
        o.*,
        r.rate_to_usd,
        ROW_NUMBER() OVER (
            PARTITION BY o.order_id
            ORDER BY r.effective_from DESC
        ) AS rn
    FROM orders o
    LEFT JOIN fx_rates r
        ON o.currency = r.currency
       AND r.effective_from <= o.order_date
)
WHERE rn = 1;
```

The key semantic rule is:

```text
choose the latest reference version whose effective time
is not after the fact time
```

---

## 35.8 Step 7 — External IP Enrichment Simulation

Use a deterministic mock reference rather than making real network calls:

```python
ip_country_cache = {
    "1.1.1.1": "Australia",
    "2.2.2.2": "United States",
}
```

---

## 35.9 Step 8 — Deduplicate External Keys

The input contains:

```text
1.1.1.1
2.2.2.2
1.1.1.1
9.9.9.9
```

Only three unique keys exist.

```python
unique_ips = (
    orders
    .select("ip")
    .unique()
)
```

The production system should request each missing unique key at most once within the relevant cache policy.

---

## 35.10 Step 9 — Cache Enrichment Results

A durable conceptual cache is:

```text
ip | country | fetched_at | expires_at
---|---------|------------|-----------
1.1.1.1 | Australia | ... | ...
2.2.2.2 | United States | ... | ...
```

A simple in-memory demonstration:

```python
def enrich_ip(ip: str, cache: dict[str, str]) -> str | None:
    if ip in cache:
        return cache[ip]

    # Production code would call the external service here.
    # This example deliberately avoids network I/O.
    return None
```

The important architecture is:

```text
cache hit → reuse
cache miss → bounded external call → persist → reuse
```

---

## 35.11 Step 10 — Join Cached Results Back

```python
ip_reference = pl.DataFrame(
    {
        "ip": ["1.1.1.1", "2.2.2.2"],
        "country": ["Australia", "United States"],
    }
)

enriched = enriched.join(
    ip_reference,
    on="ip",
    how="left",
)
```

The main transformation remains local and deterministic.

---

## 35.12 Step 11 — Introduce Duplicate Lookup Keys

Now introduce:

```python
bad_products = pl.DataFrame(
    {
        "product_id": ["P101", "P101", "P102"],
        "category": ["Laptop", "Electronics", "Phone"],
    }
)
```

A join can now turn:

```text
P101
```

into two rows.

The validation should catch this before enrichment:

```python
duplicate_keys = (
    bad_products
    .group_by("product_id")
    .len()
    .filter(pl.col("len") > 1)
)

if duplicate_keys.height:
    raise ValueError("Unsafe product lookup: duplicate keys")
```

This is preferable to discovering the problem after revenue has already doubled.

---

## 35.13 Step 12 — Introduce Missing Lookup Keys

P999 is absent.

Possible policies:

```text
UNKNOWN
```

or:

```text
lookup_missing = true
```

or quarantine:

```text
orders_quarantine/
```

or pipeline failure.

The correct choice belongs in the enrichment contract.

---

## 35.14 Step 13 — Introduce a Reference Correction

Suppose:

```text
P101
old category = Laptop
new category = Computing
```

If historical outputs must reflect the correction, determine:

```text
affected key = P101
```

then:

```text
affected partitions
        ↓
reprocess
        ↓
validate
        ↓
publish
```

Do not rebuild unrelated products unless the business semantics require it.

---

# 33. Testing

Testing must validate invariants, not merely whether the join executes.

## Test 1 — Unique lookup key succeeds

```python
def assert_unique_lookup(df: pl.DataFrame, key: str) -> None:
    duplicates = (
        df.group_by(key)
        .len()
        .filter(pl.col("len") > 1)
    )
    assert duplicates.height == 0
```

Invariant:

```text
Each lookup key has at most one current record.
```

## Test 2 — Duplicate lookup key fails

```python
bad = pl.DataFrame(
    {
        "product_id": ["P101", "P101"],
        "category": ["Laptop", "Electronics"],
    }
)

duplicates = (
    bad.group_by("product_id")
    .len()
    .filter(pl.col("len") > 1)
)

assert duplicates.height > 0
```

Invariant:

```text
Invalid lookup data must be rejected before enrichment.
```

## Test 3 — Missing key follows policy

```python
assert enriched.filter(
    pl.col("product_id") == "P999"
).select("product_lookup_missing").item()
```

Invariant:

```text
Missing matches are explicit, not silently lost.
```

## Test 4 — Enrichment preserves expected cardinality

```python
assert enriched.height == orders.height
```

Invariant:

```text
Many-to-one enrichment does not create unexpected rows.
```

## Test 5 — Coverage is correct

```python
missing_count = enriched.filter(
    pl.col("product_lookup_missing")
).height

assert missing_count == 1
```

Invariant:

```text
Coverage metrics agree with actual match results.
```

## Test 6 — Point-in-time lookup returns the historical version

For C123 on March 5:

```text
expected country = India
```

For C123 after June 1:

```text
expected country = Singapore
```

Invariant:

```text
fact_time selects the valid reference version.
```

## Test 7 — FX uses the correct effective date

For EUR on March 5:

```text
expected rate = 1.08
```

Invariant:

```text
future reference rates cannot be selected.
```

## Test 8 — Cache prevents duplicate requests

Given:

```text
IP list = A, B, A, A
```

the external request set should be:

```text
A, B
```

not four requests.

Invariant:

```text
External calls operate on unique missing keys.
```

## Test 9 — Reference correction identifies affected partitions

Invariant:

```text
A reference correction produces a deterministic affected-key set
and therefore a deterministic affected-partition set.
```

## Test 10 — Reprocessing is deterministic

Run the same enrichment twice.

Expected:

```text
same inputs
+
same reference version
+
same transformation version
=
same outputs
```

## Test 11 — Broadcast and partitioned strategies agree

For the same logical input and reference snapshot:

```text
broadcast result == partitioned result
```

Only the execution strategy changes.

## Test 12 — Reference schema change is detected

For example, if:

```text
product_id
category
brand
```

becomes:

```text
product_id
category
```

and `brand` is contractually required, fail validation before publishing.

---

# 34. Debugging

## Scenario 1 — Enriched row count suddenly doubles

### Symptoms

```text
input = 1,000,000
output = 2,000,000
```

### Root cause

Duplicate lookup keys.

### Procedure

1. compare input/output cardinality;
2. inspect lookup key counts;
3. identify duplicated keys;
4. inspect source/reference change;
5. determine whether duplicate versions are legitimate;
6. select the correct version or reject the lookup.

### Incorrect approach

Drop arbitrary duplicates:

```python
lookup.unique("product_id")
```

without defining which record should win.

### Correct production solution

Define the lookup grain and version-selection rule.

### Prevention

- uniqueness validation;
- data contract;
- reference freshness monitoring;
- cardinality tests.

---

## Scenario 2 — Coverage drops from 99.9% to 94%

### Symptoms

A large increase in missing matches.

### Possible causes

- stale reference data;
- source identifier change;
- new product population;
- whitespace/casing;
- delayed master-data ingestion;
- deleted entities.

### Procedure

```text
Coverage drop
    ↓
Compare missing keys with prior run
    ↓
Sample missing keys
    ↓
Check normalization
    ↓
Check reference freshness
    ↓
Check source-system changes
    ↓
Classify expected vs unexpected
```

### Prevention

Monitor:

```text
lookup_match_rate
lookup_missing_rate
reference_freshness
unknown_key_count
```

---

## Scenario 3 — Historical reports suddenly change

### Likely cause

A current-state dimension was used for historical facts.

### Debugging

Inspect the enrichment query.

Look for:

```sql
JOIN current_customer
  ON customer_id
```

when the requirement actually needs:

```text
customer_id + order_date
```

### Correct solution

Use a point-in-time lookup against the correct historical reference version.

---

## Scenario 4 — External API cost explodes

### Symptoms

Request volume unexpectedly approaches input row count.

### Root causes

- no key deduplication;
- no cache;
- short/incorrect TTL;
- repeated full historical processing;
- retries counted as new calls.

### Correct pattern

```text
extract unique keys
        ↓
cache lookup
        ↓
request only misses
        ↓
persist results
        ↓
join locally
```

---

## Scenario 5 — External enrichment times out

### Root causes

- unbounded concurrency;
- oversized batches;
- service overload;
- missing backoff;
- no checkpointing.

### Correct approach

Use:

- bounded concurrency;
- timeout;
- exponential backoff;
- retry policy;
- circuit-breaking where appropriate;
- checkpointing;
- durable cache.

Do not respond by simply increasing concurrency.

---

## Scenario 6 — Python and SQL produce different results

Investigate:

- string normalization;
- null semantics;
- case sensitivity;
- timestamp/time-zone handling;
- duplicate reference keys;
- type coercion;
- temporal boundary rules.

A join is only deterministic when the matching contract is deterministic.

---

## Scenario 7 — FX conversion uses the wrong rate

Inspect:

```text
currency
effective_from
order_date
```

and verify:

```text
effective_from <= order_date
```

then select the maximum valid `effective_from`.

A common bug is accidentally selecting the latest rate globally rather than the latest rate valid for each transaction.

---

## Scenario 8 — Reference correction does not update historical outputs

Investigate:

1. whether the reference change was detected;
2. whether affected keys were identified;
3. whether affected partitions were identified;
4. whether the backfill ran;
5. whether the replacement was atomically published;
6. whether downstream state was invalidated.

A detected correction is not enough. It must propagate into the correct historical outputs.

---

# 35. Anti-Patterns

| Anti-pattern | Why it fails | Better approach |
|---|---|---|
| Blind left join | Duplicate keys can fan out | Validate uniqueness |
| Assume lookup is unique | Hidden data-quality problem | Enforce a key contract |
| Ignore missing matches | Silent corruption | Explicit missing-match policy |
| Use current dimension for history | Historical incorrectness | PIT/as-of lookup |
| API call per row | Slow and expensive | Deduplicate/cache/batch |
| No external cache | Repeated cost | Durable enrichment cache |
| Unlimited external concurrency | Rate-limit failures | Bounded concurrency |
| No coverage metric | Missing matches remain invisible | Measure coverage |
| Broadcast huge lookup | Memory failure | Partitioned/distributed strategy |
| No reference versioning | History cannot be reproduced | Snapshot/version |
| Automatically restate all history | Excessive compute/risk | Targeted backfill |
| Treat entity resolution as equality | Missed or incorrect matches | Canonicalization/resolution workflow |
| Arbitrarily drop duplicate lookup rows | Hides semantic ambiguity | Define version/grain rules |
| Normalize identifiers without a contract | Can create false matches | Document normalization |
| Use mutable current data for deterministic reruns | Results change over time | Pin reference version |
| Hide network I/O inside transformations | Hard to retry and test | Keep side effects at boundaries |
| Retry external requests forever | Cost and availability risk | Bounded retries/backoff |
| Treat cache as authoritative forever | Stale enrichment | Explicit TTL/version policy |
| Ignore key skew | Slow distributed joins | Measure and mitigate skew |

---

# 36. Observability

Production enrichment requires observability at three levels.

## Reference health

Track:

```text
reference_row_count
reference_freshness
reference_duplicate_key_count
reference_schema_version
```

These tell you whether the dependency itself is healthy.

## Enrichment quality

Track:

```text
enrichment_input_rows
enrichment_output_rows
lookup_match_rate
lookup_missing_rate
lookup_fanout_count
```

These tell you whether enrichment is behaving correctly.

## Temporal correctness

Track:

```text
asof_match_failures
late_reference_records
historical_reprocessing_partitions
```

These tell you whether time-aware logic is operating correctly.

## External enrichment

Track:

```text
external_requests_total
external_cache_hits
external_cache_misses
external_request_failures
external_rate_limit_events
external_enrichment_cost
```

Useful derived metrics include:

```text
cache_hit_rate =
cache_hits / (cache_hits + cache_misses)
```

and:

```text
external_failure_rate =
failed_requests / total_requests
```

Observability turns an enrichment dependency from a hidden assumption into an measurable system component.

---

# 37. Production Case Study

Consider an e-commerce company processing:

```text
500 million orders/events
```

Reference data includes:

```text
products
customers
currencies
tax rates
country mappings
```

Requirements:

- historical correctness;
- daily incremental processing;
- late reference data;
- changing product categories;
- changing customer attributes;
- external IP enrichment;
- strict cost controls.

## 40.1 Reference architecture

A suitable conceptual architecture is:

```text
             Reference Sources
                    |
        +-----------+-----------+
        |           |           |
     Product     Customer     FX/Tax
      Master      History     Reference
        |           |           |
        +-----------+-----------+
                    |
             Validation Layer
                    |
       Versioned Reference Snapshots
                    |
        +-----------+-----------+
        |                       |
   Local/SQL Enrichment    External Enrichment
        |                       |
        |                 Unique-key extraction
        |                       |
        |                 Cache lookup
        |                       |
        |                 Bounded API calls
        |                       |
        |                 Durable cache
        +-----------+-----------+
                    |
             Enriched Silver
                    |
             Validation Layer
                    |
               Gold Models
```

## 40.2 Ownership

Each reference dataset should have:

```text
owner
source system
schema contract
freshness SLA
quality rules
versioning policy
```

## 40.3 Lookup strategy

Use:

- SQL/DataFrame joins for local reference tables;
- SCD/PIT joins for historical customer data;
- effective-dated joins for FX/tax;
- dictionary mappings only for tiny static code lists;
- broadcast only when the reference is demonstrably small enough;
- partitioned strategies for large references.

## 40.4 External IP enrichment

Do not call the API for every event.

Instead:

```text
500M events
    ↓
extract unique IPs
    ↓
lookup durable cache
    ↓
request only missing keys
    ↓
bounded API calls
    ↓
persist results
    ↓
join locally
```

The number of external requests is therefore driven by unique missing keys, not raw event count.

## 40.5 Reference corrections

When product categories change:

```text
reference change
      ↓
identify affected products
      ↓
identify affected event/order partitions
      ↓
targeted reprocessing
      ↓
validation/reconciliation
      ↓
publish
```

This is safer and cheaper than blindly rebuilding 500 million events.

---

# 38. Senior Data Engineer Reasoning

Use this decision process for every enrichment:

```text
What information am I adding?
        ↓
Where does it come from?
        ↓
Who owns it?
        ↓
Is the lookup key unique?
        ↓
Can the lookup change over time?
        ↓
Do I need point-in-time correctness?
        ↓
What happens when there is no match?
        ↓
How large is the lookup?
        ↓
Can it be broadcast?
        ↓
Do I need partitioned processing?
        ↓
Is the enrichment external?
        ↓
Can I cache it?
        ↓
What are the rate/cost limits?
        ↓
Can reference changes require backfills?
        ↓
How will I prove the enrichment is correct?
```

The senior-level insight is:

> Enrichment is a dependency-management problem disguised as a join.

Before writing code, define:

```text
Input grain
Lookup grain
Join cardinality
Matching rule
Reference version
Missing-match policy
Temporal semantics
Freshness requirement
Performance strategy
Cost boundary
Observability
Backfill behavior
```

---

# 39. Interview Questions

Each question includes the expected answer, explanation, key concepts, and senior-level insight.

## Basic — 1

### Question

What is reference data?

### Expected answer

Reference data provides standardized meanings, classifications, or context used by other datasets. Examples include country codes, status codes, currency codes, and product categories.

### Explanation

It is usually not the business event itself. It gives the event context.

### Key concepts

- reference data;
- code lists;
- enrichment.

### Senior-level insight

Reference data is still a production dependency and should have ownership, freshness, quality, and versioning expectations.

---

## Basic — 2

### Question

What is enrichment?

### Expected answer

Enrichment adds contextual attributes to an existing dataset by matching each record against another trusted dataset or system.

### Explanation

An order can be enriched with product category or customer country.

### Key concepts

- lookup;
- join;
- context.

### Senior-level insight

Correctness includes cardinality and historical semantics, not just successful execution.

---

## Basic — 3

### Question

Why can a duplicate lookup key be dangerous?

### Expected answer

A source row can match multiple lookup rows, producing fan-out and increasing output cardinality.

### Explanation

One order matched to two product records can become two order rows.

### Key concepts

- uniqueness;
- fan-out;
- cardinality.

### Senior-level insight

Lookup-key uniqueness should be an explicit contract.

---

## Basic — 4

### Question

What is a missing-match policy?

### Expected answer

It defines what happens when a source record has no matching lookup record.

### Explanation

Possible actions include defaulting, flagging, quarantining, or failing.

### Key concepts

- unknown;
- quarantine;
- fail.

### Senior-level insight

The correct policy depends on business semantics.

---

## Basic — 5

### Question

What is enrichment coverage?

### Expected answer

Coverage is the proportion of source records that successfully match the lookup.

```text
matched / total
```

### Key concepts

- match rate;
- missing rate.

### Senior-level insight

Coverage thresholds should be part of the data-quality contract.

---

## Basic — 6

### Question

When is a Python dictionary a good lookup?

### Expected answer

For a small, static, simple mapping that fits comfortably in memory.

### Key concepts

- static mapping;
- memory;
- code/config versioning.

### Senior-level insight

A dictionary should not become an accidental substitute for a governed reference-data system.

---

## Basic — 7

### Question

What is a point-in-time lookup?

### Expected answer

It selects the reference version valid at the fact's business time.

### Key concepts

- effective date;
- historical correctness;
- SCD2.

### Senior-level insight

Current-state reference data can produce historically incorrect facts.

---

## Basic — 8

### Question

What is TTL in caching?

### Expected answer

Time To Live specifies how long a cached value is considered valid.

### Key concepts

- cache;
- freshness;
- staleness.

### Senior-level insight

TTL is a business/data-freshness decision, not merely a technical setting.

---

## Basic — 9

### Question

Why should external keys be deduplicated?

### Expected answer

To avoid repeated external requests for the same key.

### Key concepts

- request deduplication;
- cost;
- rate limits.

### Senior-level insight

External request volume should be based on unique missing keys whenever possible.

---

## Basic — 10

### Question

Why should reference data have an owner?

### Expected answer

Someone must be accountable for its quality, freshness, schema, and operational behavior.

### Senior-level insight

Unowned dependencies create fragile pipelines.

---

## Moderate — 11

### Question

How would you prevent join fan-out?

### Expected answer

Validate lookup-key uniqueness before the join and validate output cardinality after the join.

### Key concepts

- uniqueness;
- cardinality;
- contracts.

### Senior-level insight

Do not solve duplicate keys by arbitrarily selecting a row unless a deterministic business rule defines the winner.

---

## Moderate — 12

### Question

When should a pipeline fail on a missing lookup?

### Expected answer

When the reference is mandatory and continuing would create invalid or misleading business output.

### Senior-level insight

Fail-fast behavior should be contract-driven rather than universal.

---

## Moderate — 13

### Question

Why can row-count equality fail to prove enrichment correctness?

### Expected answer

A join can preserve row count while attaching the wrong reference version or wrong attributes.

### Key concepts

- temporal correctness;
- semantic correctness.

### Senior-level insight

Cardinality is necessary but not sufficient.

---

## Moderate — 14

### Question

How would you enrich historical orders with customer country?

### Expected answer

Use a customer history table and join on customer ID plus an effective-date interval.

### Senior-level insight

The fact's business time determines the reference version.

---

## Moderate — 15

### Question

How would you enrich transactions with historical FX rates?

### Expected answer

Find the latest FX record whose effective date is less than or equal to the transaction date.

### Senior-level insight

Never use the globally latest rate for historical transactions.

---

## Moderate — 16

### Question

When would you prefer SQL over a Python dictionary?

### Expected answer

When the lookup is relational, larger, governed, dynamic, temporal, or already stored in a database.

### Senior-level insight

Execution location and data ownership should influence implementation.

---

## Moderate — 17

### Question

Why is API-per-row enrichment dangerous?

### Expected answer

It can cause millions of network requests, high latency, rate-limit failures, retries, and uncontrolled cost.

### Senior-level insight

Separate external side effects from deterministic transformations.

---

## Moderate — 18

### Question

How does caching reduce external enrichment cost?

### Expected answer

Repeated keys can reuse previously retrieved values instead of generating new API requests.

### Senior-level insight

Durable caches also improve reproducibility and restart behavior.

---

## Moderate — 19

### Question

What determines whether a join should be broadcast?

### Expected answer

Primarily the lookup's size, worker memory, network cost, skew, and execution engine.

### Senior-level insight

Broadcast is an optimization, not a correctness rule.

---

## Moderate — 20

### Question

What should be monitored for enrichment?

### Expected answer

Reference freshness, duplicate keys, match rate, missing rate, fan-out, request volume, cache hit rate, failures, and cost.

### Senior-level insight

Observability must cover both the reference dependency and the enrichment output.

---

## Hard — 21

### Question

A 1-million-row order table becomes 1.8 million rows after enrichment. How do you debug it?

### Expected answer

Check lookup-key multiplicity, identify duplicate keys, inspect legitimate historical versions, verify the intended grain, and correct the matching rule.

### Senior-level insight

Do not simply deduplicate the output; find the semantic cause.

---

## Hard — 22

### Question

A customer changed country. How do you prevent historical reports from changing incorrectly?

### Expected answer

Store versioned customer history and use point-in-time enrichment.

### Senior-level insight

Historical analytics requires temporal semantics, not current-state joins.

---

## Hard — 23

### Question

A lookup table is 500 GB. How would you enrich a 1 TB fact table?

### Expected answer

Do not broadcast blindly. Evaluate partitioning, distribution, clustering, join-key statistics, execution engine, and possible precomputation.

### Senior-level insight

The physical execution strategy should be selected from measured data characteristics.

---

## Hard — 24

### Question

How would you design external enrichment for 100 million events?

### Expected answer

Extract unique keys, consult a durable cache, call the API only for missing keys, batch where supported, enforce rate limits and bounded concurrency, persist results, and join locally.

### Senior-level insight

The external system should not become the row-level transformation engine.

---

## Hard — 25

### Question

What is a safe way to select an effective-dated reference record?

### Expected answer

Filter to records whose effective time is not after the fact time and select the latest valid record.

### Senior-level insight

Boundary conventions must be explicit to avoid overlapping or missing intervals.

---

## Hard — 26

### Question

What happens if a reference correction affects only 2% of products?

### Expected answer

Identify affected product keys and affected output partitions, then run a targeted backfill.

### Senior-level insight

Targeted restatement minimizes compute and reduces operational risk.

---

## Hard — 27

### Question

Why can normalization create false matches?

### Expected answer

Aggressive normalization can collapse genuinely distinct identifiers into the same representation.

### Senior-level insight

Normalization is part of the matching contract and needs tests.

---

## Hard — 28

### Question

How would you prove deterministic enrichment?

### Expected answer

Pin input interval, reference version, normalization rules, transformation version, and matching semantics, then rerun and compare outputs.

### Senior-level insight

Determinism depends on controlling dependencies as well as transformation code.

---

## Hard — 29

### Question

Why is an external cache not automatically correct?

### Expected answer

The cached value may be stale, incorrectly keyed, or from an incompatible source version.

### Senior-level insight

A cache is part of the data contract and needs freshness and provenance.

---

## Hard — 30

### Question

How would you detect a silently stale reference table?

### Expected answer

Monitor reference freshness against expected update intervals and compare reference row/key populations with historical baselines.

### Senior-level insight

Freshness should be observable before enrichment produces misleading output.

---

## Advanced — 31

### Question

Design enrichment for one billion daily events using a small reference table.

### Expected answer

Use a versioned small reference snapshot, validate uniqueness/freshness, choose a broadcast/local strategy where memory permits, enrich deterministically, and validate cardinality and coverage.

### Senior-level insight

The small reference should be treated as a pinned dependency, not an unbounded mutable table.

---

## Advanced — 32

### Question

Design enrichment with a 500 GB reference dataset.

### Expected answer

Use a distributed join strategy based on key distribution, partitioning, clustering, shuffle characteristics, and skew. Avoid broadcasting.

### Senior-level insight

Physical data layout can matter as much as logical schema.

---

## Advanced — 33

### Question

Design point-in-time customer enrichment across multiple changing dimensions.

### Expected answer

Define each dimension's effective-time semantics, validate interval integrity, use fact-time joins, version reference snapshots, and test boundary conditions.

### Senior-level insight

Different dimensions may have different temporal semantics and should not be forced into one simplistic current-state model.

---

## Advanced — 34

### Question

Design historical FX enrichment.

### Expected answer

Version FX data by effective time, select the latest valid rate per transaction, handle missing rates explicitly, and retain reference provenance.

### Senior-level insight

Financial enrichment should be reproducible and auditable.

---

## Advanced — 35

### Question

Design external IP-to-country enrichment at scale.

### Expected answer

Deduplicate IPs, use a durable cache, batch calls if supported, apply bounded concurrency/rate limiting, persist results, define TTL, monitor cost, and locally join the results.

### Senior-level insight

External enrichment is a separate side-effecting subsystem.

---

## Advanced — 36

### Question

Design an enrichment cache.

### Expected answer

Define key, value, source version, fetched timestamp, expiry, status, error information, and storage strategy.

Example:

```text
key
value
source_version
fetched_at
expires_at
status
```

### Senior-level insight

Cache records should retain enough metadata to support reproducibility and debugging.

---

## Advanced — 37

### Question

How would you protect a pipeline from join fan-out?

### Expected answer

Define expected cardinality, validate lookup uniqueness, reject invalid reference versions, test output cardinality, and monitor fan-out.

### Senior-level insight

Protection belongs before and after the join.

---

## Advanced — 38

### Question

How would you design targeted backfills after reference-data changes?

### Expected answer

Detect reference changes, identify affected keys, map keys to affected partitions, reprocess only those partitions, validate outputs, and publish atomically.

### Senior-level insight

The affected-set calculation is a first-class transformation dependency.

---

## Advanced — 39

### Question

How would you build a shared reference-data platform?

### Expected answer

Provide governed datasets with owners, contracts, freshness expectations, versioning, quality checks, snapshots, lineage, and access patterns suitable for consuming pipelines.

### Senior-level insight

Centralization should reduce duplication without creating a single uncontrolled bottleneck.

---

## Advanced — 40

### Question

How would you guarantee deterministic reruns of an enrichment pipeline?

### Expected answer

Pin input data interval, reference snapshot/version, normalization rules, transformation version, matching semantics, and external enrichment results.

### Senior-level insight

For external systems, reproducibility may require persisting the enrichment response rather than relying on the service's current response.

---

# 40. Architecture Questions

## Architecture 1 — One Billion Events + Small Lookup

Design:

```text
1B events/day
+
small product reference
```

Reference solution:

```text
Versioned product snapshot
        ↓
Validate uniqueness/freshness
        ↓
Distribute efficiently
        ↓
Broadcast if safely bounded
        ↓
Enrich
        ↓
Validate cardinality/coverage
        ↓
Publish
```

Consider:

- worker memory;
- reference version;
- skew;
- output cardinality;
- reference freshness.

---

## Architecture 2 — 500 GB Reference

Design a 500 GB lookup.

Reference solution:

```text
Reference storage
      ↓
partition/cluster by join key
      ↓
distributed join
      ↓
monitor shuffle and skew
```

Do not assume broadcast.

---

## Architecture 3 — Point-in-Time Customer Enrichment

Requirements:

```text
orders
+
customer history
```

Reference design:

```text
customer_id
+
order_time
→
valid customer version
```

Add:

- interval validation;
- non-overlap checks;
- boundary tests;
- reference versioning;
- reconciliation.

---

## Architecture 4 — Historical FX

Use:

```text
currency
+
effective_from
```

For every fact:

```text
select max(effective_from)
where effective_from <= fact_time
```

Validate:

- missing currencies;
- future-rate selection;
- overlapping versions;
- deterministic boundaries.

---

## Architecture 5 — External IP-to-Country

Use:

```text
events
 ↓
unique IP extraction
 ↓
cache lookup
 ↓
missing IPs
 ↓
bounded external requests
 ↓
durable result table
 ↓
local join
```

Monitor:

```text
cache_hit_rate
request_count
failure_rate
rate_limit_events
cost
```

---

## Architecture 6 — Enrichment Cache

A useful schema is:

```text
cache_key
result
source_name
source_version
fetched_at
expires_at
status
error_code
```

The cache should be durable when reproducibility and cross-run reuse matter.

---

## Architecture 7 — Missing-Match Handling

Use classifications:

```text
expected unknown
temporary missing
data-quality error
reference-lag error
contract violation
```

Then map each classification to:

```text
default
flag
quarantine
retry
fail
```

---

## Architecture 8 — Fan-Out Protection

Before enrichment:

```text
validate lookup uniqueness
```

During/after enrichment:

```text
validate cardinality
validate duplicate output grain
monitor fanout_count
```

If the reference is historical:

```text
validate temporal uniqueness
```

not merely current-key uniqueness.

---

## Architecture 9 — Targeted Backfill

Use:

```text
reference version N
      ↓
diff against version N-1
      ↓
affected keys
      ↓
affected partitions
      ↓
reprocess
      ↓
reconcile
      ↓
atomic publish
```

This makes reference changes operationally manageable.

---

## Architecture 10 — Shared Reference Platform

A shared platform should provide:

```text
source ownership
schema contracts
freshness
quality validation
versioned snapshots
access patterns
lineage
change detection
consumer documentation
```

Consumer pipelines should be able to pin a known reference version when historical reproducibility matters.

---

# 41. Production Checklist

## Reference data

- [ ] Owner identified
- [ ] Source identified
- [ ] Schema contract defined
- [ ] Freshness requirement defined
- [ ] Versioning strategy defined
- [ ] Key uniqueness validated

## Enrichment

- [ ] Lookup key defined
- [ ] Join cardinality understood
- [ ] Fan-out protection exists
- [ ] Missing-match policy defined
- [ ] Coverage monitored
- [ ] Row-count/cardinality validation exists

## Temporal correctness

- [ ] Event time understood
- [ ] Reference effective time understood
- [ ] PIT/as-of logic implemented where required
- [ ] Historical behavior tested
- [ ] Interval boundaries defined
- [ ] Overlapping reference versions detected

## External enrichment

- [ ] Unique keys deduplicated
- [ ] Cache implemented where appropriate
- [ ] TTL defined
- [ ] Rate limits respected
- [ ] Concurrency bounded
- [ ] Cost monitored
- [ ] Failures/retries handled
- [ ] External results persisted when reproducibility requires them

## Backfills

- [ ] Reference changes detected
- [ ] Affected keys identified
- [ ] Affected partitions identified
- [ ] Targeted backfill supported
- [ ] Reconciliation exists
- [ ] Publication is atomic or safely recoverable

## Observability

- [ ] Reference freshness monitored
- [ ] Reference duplicate keys monitored
- [ ] Match rate monitored
- [ ] Missing rate monitored
- [ ] Fan-out monitored
- [ ] External cache hit rate monitored
- [ ] External failures monitored
- [ ] External cost monitored

---

# 42. Exercises

## Beginner

### Exercise 1 — Product Categories

Enrich orders with product categories.

Requirements:

- preserve order grain;
- validate product-key uniqueness;
- report missing products.

### Exercise 2 — Country-Code Lookup

Build a country-code mapping:

```text
IN → India
SG → Singapore
US → United States
```

Apply it to events.

### Exercise 3 — Reference vs Transactional Data

Explain the difference using an order system.

### Exercise 4 — Dictionary Lookup

Implement a status mapping with a Python dictionary.

### Exercise 5 — DataFrame Join

Implement product enrichment using Polars.

---

## Intermediate

### Exercise 6 — Validate Lookup-Key Uniqueness

Write a reusable validation function.

### Exercise 7 — Detect Fan-Out

Create duplicate product keys and detect output-cardinality growth.

### Exercise 8 — Missing-Match Policies

Implement:

- default;
- flag;
- quarantine;
- fail.

### Exercise 9 — Coverage

Calculate:

```text
match_rate
missing_rate
```

by day.

### Exercise 10 — SCD Lookup

Implement historical customer-country enrichment.

### Exercise 11 — FX As-Of Lookup

For each transaction, select the latest valid FX rate.

---

## Advanced

### Exercise 12 — Broadcast vs Partitioned Joins

Create datasets with different sizes and reason about:

- memory;
- shuffle;
- skew;
- execution cost.

### Exercise 13 — External Enrichment Cache

Build a mock API and a durable local cache.

### Exercise 14 — TTL

Add:

```text
fetched_at
expires_at
```

and implement cache validity.

### Exercise 15 — External Key Deduplication

Given millions of events, reduce requests to unique keys.

### Exercise 16 — Targeted Historical Backfill

Given changed product IDs, identify affected partitions and reprocess them.

### Exercise 17 — Reference Change Detection

Compare two reference snapshots and identify changed keys.

---

## Expert

### Exercise 18 — Billion-Record Enrichment

Design enrichment for billions of records using a small reference table.

Your design must cover:

- versioning;
- broadcast;
- skew;
- validation;
- observability.

### Exercise 19 — Multi-Dimension PIT Enrichment

Design point-in-time enrichment across:

```text
customer
product
tax
FX
```

### Exercise 20 — Global External Enrichment

Design an externally enriched global event pipeline with:

- regional caches;
- rate limits;
- failure recovery;
- deterministic reruns.

### Exercise 21 — Reference Governance

Design a governance model with:

- owners;
- contracts;
- freshness;
- versions;
- quality checks.

### Exercise 22 — Deterministic Reruns

Design a pipeline where rerunning the same input interval produces the same enriched output even when an external service has changed since the original run.

---

# 43. Final Mental Model

Use this sequence whenever you build enrichment:

```text
Reference Data
      ↓
Validate
      ↓
Version / Snapshot
      ↓
Choose Lookup Strategy
      ↓
Validate Key Uniqueness
      ↓
Enrich
      ↓
Handle Missing Matches
      ↓
Measure Coverage
      ↓
Validate Cardinality
      ↓
Apply Point-in-Time Rules
      ↓
Cache External Dependencies
      ↓
Monitor Cost + Quality
      ↓
Backfill When Reference Data Changes
```

The most dangerous enrichment bugs are often not join syntax errors.

They are semantic errors:

- wrong version;
- duplicate keys;
- missing matches;
- stale reference data;
- incorrect historical validity;
- uncontrolled external dependencies.

Treat reference data as a production dependency with:

```text
owner
contract
freshness expectation
versioning strategy
quality checks
observability
```

A strong Data Engineer asks not merely:

> Can I join these datasets?

but:

> Can I prove that this enrichment is correct, reproducible, historically valid, operationally safe, and affordable?

---

# 44. Exit Criteria

You are ready to move on when you can independently:

- explain enrichment;
- explain reference data;
- distinguish reference, master, and transactional data;
- implement static code-list lookups;
- implement DataFrame/SQL enrichment;
- validate lookup-key uniqueness;
- prevent join fan-out;
- define missing-match policies;
- calculate enrichment coverage;
- handle SCD lookups;
- perform point-in-time/as-of lookups;
- enrich with time-varying reference data;
- choose dictionary vs DataFrame vs SQL lookup;
- reason about large lookup tables;
- choose broadcast vs partitioned joins;
- design external enrichment;
- deduplicate external keys;
- implement caching;
- define cache TTL;
- respect API rate limits;
- control enrichment cost;
- understand entity-resolution limitations;
- detect reference-data changes;
- perform targeted historical backfills;
- build observability for enrichment;
- test temporal correctness;
- debug fan-out and missing-match failures;
- design production-grade enrichment architectures;
- explain these decisions in a senior Data Engineering interview.

The progression you should now be comfortable with is:

```text
Basic Lookup
      ↓
Reference Data
      ↓
Simple Enrichment
      ↓
Uniqueness
      ↓
Fan-Out Prevention
      ↓
Missing Matches
      ↓
Coverage
      ↓
SCD / Time-Varying Data
      ↓
Point-in-Time Enrichment
      ↓
Large Lookups
      ↓
Broadcast / Partitioned Joins
      ↓
External Enrichment
      ↓
Caching / TTL / Rate Limits
      ↓
Entity Resolution Awareness
      ↓
Reference Changes
      ↓
Targeted Backfills
      ↓
Testing
      ↓
Debugging
      ↓
Production Architecture
      ↓
Senior-Level Reasoning
```

The final principle is:

> Safe enrichment is controlled dependency management: validate the reference, define the matching semantics, preserve the required grain, select the correct temporal version, make missing matches explicit, bound external effects, observe the dependency, and make reference changes reproducible through targeted backfills.
