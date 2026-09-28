# MERGE, Upsert, and SCD Implementation in SQL

> **Stage 2 — Python for Data Engineering**  
> **Module 2.6 — SQL for Data Engineers**  
> **Topic 10 — MERGE, upsert, and SCD implementation in SQL**  
> **Primary environment:** PostgreSQL 16+  
> **Secondary awareness:** DuckDB and warehouse/lakehouse SQL dialects
>
> This is the final topic in Module 2.6. The goal is not to memorize `MERGE` syntax. The goal is to reason correctly about how an incoming source state becomes a durable, repeatable, historically correct target state.

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain full refresh vs incremental loading;
- write PostgreSQL upserts with `INSERT ... ON CONFLICT`;
- use `DO NOTHING`;
- understand why the conflict target needs a real uniqueness definition;
- distinguish primary keys, surrogate keys, natural keys, business keys, and mutable keys;
- build a staging → validation → deduplication → compare → apply pipeline;
- write PostgreSQL `MERGE`;
- explain `MATCHED` and `NOT MATCHED`;
- use conditional updates and delete branches;
- explain why source rows must be deduplicated before a merge;
- use `IS DISTINCT FROM` for NULL-safe change detection;
- handle hard deletes, soft deletes, and tombstones;
- design idempotent incremental loads;
- implement SCD Type 1;
- implement SCD Type 2;
- maintain valid historical ranges;
- assert exactly one current SCD2 row per business key;
- detect overlapping validity ranges;
- detect unintended gaps;
- repair late-arriving and out-of-order historical changes;
- write point-in-time fact-to-dimension joins;
- reason about merge performance;
- compare SCD2 with snapshot tables;
- debug incorrect incremental loads;
- defend incremental-loading designs in interviews and architecture reviews.

---

## 2. Prerequisites

Do not re-learn the earlier SQL topics from scratch. This chapter assumes working familiarity with:

- joins;
- CTEs;
- window functions;
- deduplication;
- constraints and keys;
- indexes;
- transactions;
- NULL semantics;
- idempotent/repeatable jobs.

The important connections are:

```text
Topic 01: NULL semantics
      ↓
Topic 02/04: joins + CTEs
      ↓
Topic 05/06: windows + deduplication
      ↓
Topic 07/08: keys + constraints + indexes
      ↓
Topic 09: transactions + concurrency
      ↓
Topic 10: incremental reconciliation + historical state
```

A useful mental model is:

```text
incoming source
    ↓
What does one row mean?
    ↓
What entity does it identify?
    ↓
What changed?
    ↓
What should happen to the target?
    ↓
What should happen to history?
```

---

## 3. Why This Topic Matters in Data Engineering

Production data pipelines constantly answer this question:

> **How do I safely make the target reflect the latest valid source state without duplicating, losing, or corrupting information?**

Typical examples:

```text
source CRM customer data
        ↓
warehouse customer table

source product catalog
        ↓
warehouse product dimension

CDC events
        ↓
current operational state

customer attributes over time
        ↓
historical dimension
```

A toy pipeline says:

```text
INSERT rows
```

A production pipeline has to decide:

```text
insert?
update?
delete?
ignore?
history?
retry?
duplicate?
late arrival?
NULL change?
```

### The full problem

Suppose yesterday the target contains:

```text
customer_id | segment | status
------------+---------+--------
101         | Bronze  | active
102         | Silver  | active
```

Today's source contains:

```text
customer_id | segment | status
------------+---------+--------
101         | Silver  | active
102         | Silver  | active
103         | Bronze  | active
```

The target must become:

```text
101 → updated
102 → unchanged
103 → inserted
```

Now add deletes, duplicate source rows, late changes, and history. The problem becomes a state-reconciliation problem.

---

# Part I — Foundations

## 4. The Problem: Keeping Target State in Sync

The core mental model is:

```text
SOURCE STATE
     ↓
COMPARE WITH
     ↓
TARGET STATE
     ↓
INSERT / UPDATE / DELETE
```

Every incremental load should make its transformation rules explicit.

Ask:

```text
What is one source row?
What is one target row?
What identifies the same entity?
What counts as changed?
What counts as deleted?
What history must be preserved?
```

### Grain

State the grain before writing SQL.

Examples:

```text
products
→ one row per product

customers
→ one row per current customer

dim_customer
→ one row per customer version

fact_orders
→ one row per order
```

A large fraction of merge bugs are really **grain bugs**.

---

## 5. Full Refresh vs Incremental Loading

### Full refresh

A full refresh rebuilds the target from the source snapshot.

Conceptually:

```text
source snapshot
      ↓
replace target
```

Example:

```sql
TRUNCATE TABLE products;

INSERT INTO products (
    product_id,
    product_name,
    price
)
SELECT
    product_id,
    product_name,
    price
FROM source_products;
```

### Why it is conceptually simple

You do not need to determine:

```text
insert?
update?
```

You simply rebuild.

### Why it becomes expensive

If the source has 500 million rows and only 50,000 rows changed:

```text
full refresh
→ process 500,000,000 rows

incremental
→ ideally process a much smaller change set
```

Costs can include:

- reading large volumes;
- rewriting large targets;
- index maintenance;
- storage churn;
- downstream compute;
- longer publication windows.

### Incremental load

An incremental load works from:

```text
new/changed source data
+
existing target state
```

Conceptually:

```text
daily changes
      ↓
reconcile
      ↓
existing target
```

You must define:

```text
new row
changed row
deleted row
unchanged row
```

### Tiny example

**TARGET BEFORE**

```text
product_id | product_name | price
-----------+--------------+------
1          | Keyboard     | 50
2          | Mouse        | 25
```

**SOURCE**

```text
product_id | product_name | price
-----------+--------------+------
1          | Keyboard Pro | 60
2          | Mouse        | 25
3          | Monitor      | 200
```

**TARGET AFTER**

```text
product_id | product_name | price
-----------+--------------+------
1          | Keyboard Pro | 60
2          | Mouse        | 25
3          | Monitor      | 200
```

Interpretation:

```text
1 → changed
2 → unchanged
3 → inserted
```

---

## 6. Upsert Fundamentals

An **upsert** means:

> **Insert the row when the target row does not exist; update the row when the target row already exists.**

The concept is:

```text
incoming row
     ↓
does target identity exist?
     ├── no  → INSERT
     └── yes → UPDATE
```

Upsert is a natural fit for incremental loads where the incoming source contains the current state for each business key.

It is not automatically a full delete-aware reconciliation strategy.

---

## 7. Unique Constraints and Key Foundations

Before using an upsert, answer:

> **What makes two records the same entity?**

### Primary key

A primary key identifies a row in the target.

```sql
CREATE TABLE products (
    product_id BIGINT PRIMARY KEY,
    product_name TEXT NOT NULL,
    price NUMERIC(12, 2)
);
```

### Unique constraint

A unique constraint says that values or combinations of values must be unique.

```sql
CREATE TABLE customer_accounts (
    customer_id BIGINT PRIMARY KEY,
    external_customer_id TEXT UNIQUE
);
```

### Unique index

PostgreSQL can also represent uniqueness with a unique index.

```sql
CREATE UNIQUE INDEX ux_customer_external_id
ON customer_accounts (external_customer_id);
```

A unique constraint and unique index are related mechanisms, but they are not identical DDL objects. For upsert reasoning, the key point is:

> PostgreSQL needs a real uniqueness definition capable of identifying the conflicting target row.

### Business key

A business key comes from the business identity of an entity.

Examples:

```text
customer_id
product_id
external_customer_id
(source_system, source_customer_id)
```

### Natural key

A natural key is derived from business data.

Examples:

```text
country_code
email
tax_identifier
```

### Surrogate key

A surrogate key is an internally generated identifier.

Example:

```text
customer_sk = 84217
```

A surrogate key often identifies a **versioned dimension row**, while the business key identifies the underlying entity.

### Stable vs mutable keys

A stable key remains the same for the identity it represents.

A mutable field can change.

For example:

```text
customer_id = stable
email       = mutable
```

Using email as identity is only appropriate when the source system and business semantics guarantee that email really represents row identity.

### Wrong conflict target

Suppose:

```text
customer_id = 101
email = a@example.com
```

and later:

```text
customer_id = 101
email = new@example.com
```

If the conflict target is:

```text
email
```

then changing an email could create a second row instead of updating customer 101.

The correct key is a modeling decision, not a syntax decision.

---

## 8. PostgreSQL `ON CONFLICT`

PostgreSQL provides:

```sql
INSERT ... ON CONFLICT (...) DO UPDATE
```

and:

```sql
INSERT ... ON CONFLICT (...) DO NOTHING
```

### Simple upsert

```sql
INSERT INTO products (
    product_id,
    product_name,
    price,
    updated_at
)
VALUES (
    101,
    'Keyboard Pro',
    60.00,
    TIMESTAMP '2026-09-28 10:00:00'
)
ON CONFLICT (product_id)
DO UPDATE
SET
    product_name = EXCLUDED.product_name,
    price = EXCLUDED.price,
    updated_at = EXCLUDED.updated_at;
```

### What is `EXCLUDED`?

Inside the `DO UPDATE` branch:

```text
target table row
+
incoming conflicting row
```

The incoming row is referenced through:

```sql
EXCLUDED.column_name
```

So:

```sql
price = EXCLUDED.price
```

means:

> Set the target's price to the incoming row's price.

---

## 9. PostgreSQL `DO NOTHING`

Sometimes a conflict means:

```text
this incoming row is already safely represented
```

Use:

```sql
INSERT INTO event_types (
    event_type_id,
    event_name
)
VALUES (
    10,
    'payment_succeeded'
)
ON CONFLICT (event_type_id)
DO NOTHING;
```

### When this can make sense

- reference-data initialization;
- replayed immutable events;
- load where existing target state should win;
- idempotent inserts into a table where duplicates are expected on replay but should have no additional effect.

### Important question

`DO NOTHING` is not equivalent to:

```text
up-to-date
```

It means:

> The conflicting row is intentionally left unchanged.

Use it only when that business behavior is correct.

---

## 10. Example 1 — Simple PostgreSQL Upsert

**TARGET BEFORE**

```text
product_id | product_name | price
-----------+--------------+------
1          | Keyboard     | 50
2          | Mouse        | 25
```

**SOURCE**

```text
product_id | product_name | price
-----------+--------------+------
2          | Mouse Pro    | 30
3          | Monitor      | 200
```

SQL:

```sql
INSERT INTO products (
    product_id,
    product_name,
    price
)
VALUES
    (2, 'Mouse Pro', 30.00),
    (3, 'Monitor', 200.00)
ON CONFLICT (product_id)
DO UPDATE
SET
    product_name = EXCLUDED.product_name,
    price = EXCLUDED.price;
```

**TARGET AFTER**

```text
product_id | product_name | price
-----------+--------------+------
1          | Keyboard     | 50
2          | Mouse Pro    | 30
3          | Monitor      | 200
```

### What happened?

```text
2 → conflict on product_id → UPDATE
3 → no conflict → INSERT
1 → untouched
```

---

## 11. Example 2 — Upsert with `DO NOTHING`

```sql
INSERT INTO products (
    product_id,
    product_name,
    price
)
VALUES
    (2, 'Mouse Pro', 30.00),
    (3, 'Monitor', 200.00)
ON CONFLICT (product_id)
DO NOTHING;
```

Given:

```text
product_id = 2 already exists
```

PostgreSQL leaves row 2 unchanged and inserts row 3.

---

## 12. Updating Only Changed Rows

A naive upsert updates every conflicting row:

```sql
ON CONFLICT (product_id)
DO UPDATE
SET
    product_name = EXCLUDED.product_name,
    price = EXCLUDED.price,
    updated_at = CURRENT_TIMESTAMP;
```

That can create unnecessary work.

### Why unnecessary updates matter

They can create:

- more WAL/write activity;
- index maintenance;
- row churn;
- vacuum pressure;
- misleading audit timestamps;
- downstream change-detection events;
- unnecessary replication work.

The important principle is:

> **Do not rewrite a business row when its business values did not change.**

### Change-only pattern

```sql
INSERT INTO products (
    product_id,
    product_name,
    price,
    updated_at
)
VALUES
    (2, 'Mouse Pro', 30.00, TIMESTAMP '2026-09-28 10:00:00')
ON CONFLICT (product_id)
DO UPDATE
SET
    product_name = EXCLUDED.product_name,
    price = EXCLUDED.price,
    updated_at = EXCLUDED.updated_at
WHERE
    products.product_name IS DISTINCT FROM EXCLUDED.product_name
    OR products.price IS DISTINCT FROM EXCLUDED.price;
```

The `WHERE` condition makes the update conditional.

---

## 13. `IS DISTINCT FROM` and NULL-Safe Comparison

Normal SQL comparison uses three-valued logic.

Consider:

```sql
10 <> NULL
```

The result is not `TRUE`. It is `UNKNOWN`.

That means:

```sql
WHERE old_value <> new_value
```

does not reliably detect changes when NULL is possible.

### Use `IS DISTINCT FROM`

```sql
old_value IS DISTINCT FROM new_value
```

This gives a strict two-valued answer:

```text
different?
yes / no
```

### Comparison table

| Old | New | `old <> new` | `old IS DISTINCT FROM new` |
|---|---|---|---|
| 10 | 12 | TRUE | TRUE |
| 10 | 10 | FALSE | FALSE |
| NULL | 10 | UNKNOWN | TRUE |
| 10 | NULL | UNKNOWN | TRUE |
| NULL | NULL | UNKNOWN | FALSE |

### Why this matters

For incremental processing, your business question is usually:

> "Did the value actually change?"

`IS DISTINCT FROM` expresses that question directly.

### Example 3 — Change-only upsert

```sql
INSERT INTO products (
    product_id,
    product_name,
    price,
    updated_at
)
VALUES
    (1, 'Keyboard', 50.00, TIMESTAMP '2026-09-28 09:00:00'),
    (2, 'Mouse Pro', 30.00, TIMESTAMP '2026-09-28 09:00:00')
ON CONFLICT (product_id)
DO UPDATE
SET
    product_name = EXCLUDED.product_name,
    price = EXCLUDED.price,
    updated_at = EXCLUDED.updated_at
WHERE
    products.product_name IS DISTINCT FROM EXCLUDED.product_name
    OR products.price IS DISTINCT FROM EXCLUDED.price;
```

Here `updated_at` changes only if business columns change.

### Audit-column warning

If you write:

```sql
updated_at = CURRENT_TIMESTAMP
```

for every conflict, an unchanged source row becomes an apparent business change.

Separate:

```text
business change timestamp
```

from:

```text
pipeline observation timestamp
```

when those concepts differ.

---

# Part II — Production Staging and MERGE

## 14. The Staging Pattern

Production incremental loading commonly follows:

```text
SOURCE
   ↓
STAGING
   ↓
VALIDATE
   ↓
DEDUPLICATE
   ↓
COMPARE
   ↓
APPLY
   ↓
TARGET
```

Staging is not merely "another table."

It creates a controllable boundary between:

```text
ingestion
```

and:

```text
target mutation
```

### Staging responsibilities

Validate:

- schema;
- required columns;
- data types;
- business-key presence;
- duplicate keys;
- NULL key behavior;
- row counts;
- source freshness;
- data-quality rules;
- source-vs-target reconciliation.

### Temporary vs persistent staging

A temporary staging table can be useful for a single session/load:

```sql
CREATE TEMP TABLE staging_products (...);
```

Persistent staging can be useful when:

- multiple steps need the same data;
- operational visibility is required;
- failure recovery benefits from retained input;
- the pipeline architecture separates ingestion and publication.

The right choice depends on workload and operational requirements.

---

## 15. Example 4 — Staging → Validation → Deduplication → Upsert

### Target

```sql
CREATE TABLE products (
    product_id BIGINT PRIMARY KEY,
    product_name TEXT NOT NULL,
    price NUMERIC(12, 2),
    updated_at TIMESTAMP
);
```

### Staging

```sql
CREATE TEMP TABLE staging_products (
    product_id BIGINT,
    product_name TEXT,
    price NUMERIC(12, 2),
    updated_at TIMESTAMP,
    source_priority INT,
    ingestion_id BIGINT
);
```

### Source rows

```text
product_id | product_name | price | source_priority | ingestion_id
-----------+--------------+-------+-----------------+-------------
1          | Keyboard     | 50    | 1               | 1001
2          | Mouse Pro    | 30    | 1               | 1002
2          | Mouse        | 25    | 2               | 1003
3          | Monitor      | 200   | 1               | 1004
```

### Validation

```sql
SELECT *
FROM staging_products
WHERE product_id IS NULL
   OR product_name IS NULL;
```

Expected:

```text
0 rows
```

Duplicate-key assertion:

```sql
SELECT product_id
FROM staging_products
GROUP BY product_id
HAVING COUNT(*) > 1;
```

This returns:

```text
2
```

The merge source is unsafe until we choose a deterministic survivor.

### Deduplicate

```sql
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY
                updated_at DESC,
                source_priority DESC,
                ingestion_id DESC
        ) AS rn
    FROM staging_products AS s
)
SELECT
    product_id,
    product_name,
    price,
    updated_at
FROM ranked
WHERE rn = 1;
```

### Why these ordering rules?

The ranking rule is business logic.

It says:

```text
latest update wins
then higher source priority wins
then latest ingestion record wins
```

Without a deterministic tie-breaker, the surviving row can vary between runs.

### Apply

```sql
INSERT INTO products (
    product_id,
    product_name,
    price,
    updated_at
)
SELECT
    product_id,
    product_name,
    price,
    updated_at
FROM (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY
                updated_at DESC,
                source_priority DESC,
                ingestion_id DESC
        ) AS rn
    FROM staging_products AS s
) AS ranked
WHERE rn = 1
ON CONFLICT (product_id)
DO UPDATE
SET
    product_name = EXCLUDED.product_name,
    price = EXCLUDED.price,
    updated_at = EXCLUDED.updated_at
WHERE
    products.product_name IS DISTINCT FROM EXCLUDED.product_name
    OR products.price IS DISTINCT FROM EXCLUDED.price;
```

In production, the validation and apply boundary should be designed together with the transaction policy from Topic 09.

---

## 16. Why the Source Must Be Deduplicated Before MERGE

This is a critical production rule.

Suppose:

```text
SOURCE

product_id | price
-----------+------
10         | 25
10         | 27
```

and:

```text
TARGET

product_id | price
-----------+------
10         | 20
```

Now the merge condition is:

```text
source.product_id = target.product_id
```

One target row is matched by multiple source rows.

That creates an ambiguous mutation:

```text
Which incoming price wins?
25?
27?
```

### Broken assumption

A common mistake is:

> "The source normally has one row per key."

"Normally" is not enough for a production boundary.

Data can contain:

- duplicate CDC messages;
- replays;
- retry artifacts;
- source joins that multiplied rows;
- multiple updates in one batch;
- accidental duplicate extracts.

### Broken example

```sql
MERGE INTO products AS t
USING staging_products AS s
ON t.product_id = s.product_id
WHEN MATCHED THEN
    UPDATE SET
        price = s.price
WHEN NOT MATCHED THEN
    INSERT (
        product_id,
        product_name,
        price
    )
    VALUES (
        s.product_id,
        s.product_name,
        s.price
    );
```

The source must first be made compatible with the target merge grain.

### Correct principle

```text
raw source
   ↓
deduplicate
   ↓
one row per merge key
   ↓
MERGE / upsert
```

---

## 17. Deterministic Survivor Selection

Do not just write:

```sql
ROW_NUMBER() ...
```

without explaining the rule.

The ranking columns define **which source record represents the entity**.

Possible business rules:

```text
latest source update
highest source priority
highest completeness score
latest sequence number
latest ingestion timestamp
highest event version
```

### Example

```sql
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY
                updated_at DESC,
                source_priority DESC,
                source_event_id DESC
        ) AS rn
    FROM staging_products AS s
)
SELECT *
FROM ranked
WHERE rn = 1;
```

The last column is a deterministic tie-breaker.

### Equal timestamps

If two rows have:

```text
updated_at = 2026-09-28 10:00:00
```

and you order only by `updated_at DESC`, the survivor may not be deterministic.

Use a stable final tie-breaker.

---

## 18. MERGE Fundamentals

`MERGE` expresses source-target reconciliation in one statement.

Conceptually:

```text
For each source row:
    determine whether it matches target
        ↓
    matched?
      ├── yes → matched action
      └── no  → not-matched action
```

Important concepts:

- source table;
- target table;
- matching condition;
- matched rows;
- unmatched source rows;
- actions against the target.

### Standard conceptual pattern

```sql
MERGE INTO target AS t
USING source AS s
ON t.business_key = s.business_key

WHEN MATCHED THEN
    UPDATE SET ...

WHEN NOT MATCHED THEN
    INSERT (...)
    VALUES (...);
```

### SQL standard vs PostgreSQL vs DuckDB

Keep these distinct:

```text
standard SQL concept
        ↓
PostgreSQL syntax/behavior
        ↓
DuckDB version-specific syntax/behavior
        ↓
warehouse/lakehouse vendor behavior
```

Do not call a dialect-specific feature "universal SQL."

The roadmap assumes PostgreSQL 15+ for `MERGE`. Exact DuckDB support and syntax should be checked against the installed DuckDB version.

---

## 19. `WHEN MATCHED THEN UPDATE`

Basic form:

```sql
WHEN MATCHED THEN
    UPDATE SET
        product_name = s.product_name,
        price = s.price
```

A matched source row already has a target identity.

### Conditional matched action

```sql
WHEN MATCHED
     AND t.is_discontinued = false
THEN
    UPDATE SET
        price = s.price;
```

The condition is evaluated as part of the merge action logic.

Use explicit conditions when a business rule determines whether the update should occur.

---

## 20. `WHEN NOT MATCHED THEN INSERT`

Basic form:

```sql
WHEN NOT MATCHED THEN
    INSERT (
        product_id,
        product_name,
        price
    )
    VALUES (
        s.product_id,
        s.product_name,
        s.price
    );
```

The source row has no target match, so the target gets a new row.

---

## 21. Conditional Delete Branch

A merge can also remove a matched target row when the business rules say so.

Conceptually:

```sql
WHEN MATCHED
     AND s.is_discontinued = true
THEN DELETE
```

Use deletion only when the source meaning truly represents deletion.

Do not infer deletion from:

```text
row is missing from today's partial feed
```

unless the source contract explicitly says the feed is a complete authoritative snapshot.

---

## 22. PostgreSQL `MERGE`

### Example 5 — Simple PostgreSQL `MERGE`

```sql
MERGE INTO products AS t
USING staging_products AS s
ON t.product_id = s.product_id
WHEN MATCHED THEN
    UPDATE SET
        product_name = s.product_name,
        price = s.price,
        updated_at = s.updated_at
WHEN NOT MATCHED THEN
    INSERT (
        product_id,
        product_name,
        price,
        updated_at
    )
    VALUES (
        s.product_id,
        s.product_name,
        s.price,
        s.updated_at
    );
```

### Example 6 — Update + insert with change detection

```sql
MERGE INTO products AS t
USING (
    SELECT
        product_id,
        product_name,
        price,
        updated_at
    FROM (
        SELECT
            s.*,
            ROW_NUMBER() OVER (
                PARTITION BY product_id
                ORDER BY updated_at DESC, ingestion_id DESC
            ) AS rn
        FROM staging_products AS s
    ) AS ranked
    WHERE rn = 1
) AS s
ON t.product_id = s.product_id

WHEN MATCHED
     AND (
         t.product_name IS DISTINCT FROM s.product_name
         OR t.price IS DISTINCT FROM s.price
     )
THEN
    UPDATE SET
        product_name = s.product_name,
        price = s.price,
        updated_at = s.updated_at

WHEN NOT MATCHED THEN
    INSERT (
        product_id,
        product_name,
        price,
        updated_at
    )
    VALUES (
        s.product_id,
        s.product_name,
        s.price,
        s.updated_at
    );
```

The important flow is:

```text
source
→ deduplicate
→ compare
→ mutate
```

not:

```text
raw source
→ hope it is unique
→ mutate
```

---

## 23. Delete Semantics

There are three major ways deletion is represented.

### Hard delete

Physically remove the row:

```sql
DELETE FROM products
WHERE product_id = 10;
```

Appropriate when:

- the row is no longer needed;
- historical retention rules permit removal;
- downstream dependencies are understood.

### Soft delete

Keep the row but mark it:

```text
is_deleted
deleted_at
```

Example:

```sql
UPDATE customers
SET
    is_deleted = true,
    deleted_at = CURRENT_TIMESTAMP
WHERE customer_id = 101;
```

Queries then need a defined active-record predicate:

```sql
WHERE is_deleted = false
```

A common bug is forgetting the filter and accidentally reporting deleted entities.

### Tombstone / delete marker

A source may explicitly publish:

```text
customer_id = 101
operation = DELETE
```

A tombstone is a source-level statement that the entity was deleted.

### Missing is not automatically delete

Compare:

```text
SOURCE SNAPSHOT
```

with:

```text
CHANGE FEED
```

If today's source snapshot is complete and authoritative:

```text
row absent
```

might mean deleted.

If today's source contains only changes:

```text
row absent
```

means nothing.

Never turn absence into deletion without a source contract.

---

## 24. Example 7 — Merge with Conditional Delete

Suppose the staging contract has:

```text
product_id
product_name
price
is_discontinued
```

Then:

```sql
MERGE INTO products AS t
USING staging_products AS s
ON t.product_id = s.product_id

WHEN MATCHED
     AND s.is_discontinued = true
THEN
    DELETE

WHEN MATCHED
     AND s.is_discontinued = false
     AND (
         t.product_name IS DISTINCT FROM s.product_name
         OR t.price IS DISTINCT FROM s.price
     )
THEN
    UPDATE SET
        product_name = s.product_name,
        price = s.price

WHEN NOT MATCHED
     AND s.is_discontinued = false
THEN
    INSERT (
        product_id,
        product_name,
        price
    )
    VALUES (
        s.product_id,
        s.product_name,
        s.price
    );
```

The business rules are explicit:

```text
discontinued existing row → delete
active changed row       → update
new active row           → insert
```

---

## 25. DuckDB and Dialect Differences

**Engine context: DuckDB**

DuckDB participates in this module because it is useful for single-node analytical workloads.

For incremental loading, the learner should know that:

- DuckDB supports modern SQL mutation patterns;
- support for `MERGE` and related syntax has evolved by version;
- exact syntax and feature support should be checked against the installed DuckDB version;
- transaction/concurrency semantics differ from PostgreSQL;
- warehouse/lakehouse implementations can differ again.

### What not to do

Do not memorize:

```text
MERGE syntax
```

as if one exact spelling works everywhere.

Instead, verify:

```text
engine
version
feature support
syntax
transaction behavior
```

### Practical habit

When a pipeline is portable across PostgreSQL and DuckDB, keep:

```text
business transformation logic
```

conceptually separate from:

```text
dialect-specific SQL
```

---

# Part III — Idempotency

## 26. Idempotency

Idempotency means:

> **Running the same logical load repeatedly should converge to the same correct final business state.**

Think:

```text
apply(state)
apply(state)
apply(state)
```

should leave the same business state as one successful application.

### Idempotency test

```text
capture target
   ↓
run load
   ↓
capture target
   ↓
run identical load again
   ↓
capture target
   ↓
compare
```

### Common ways idempotency breaks

#### 1. Updating timestamps every run

```sql
updated_at = CURRENT_TIMESTAMP
```

even when business data did not change.

#### 2. Creating new surrogate keys every replay

A replay should not create another logical entity.

#### 3. Appending duplicates

```text
same source event
→ inserted twice
```

#### 4. Non-deterministic deduplication

Different source survivors on different runs produce different targets.

#### 5. Deleting and reinserting unnecessarily

This may change surrogate keys or history.

#### 6. Using current time in business transformation

If the transformation result depends on:

```sql
CURRENT_TIMESTAMP
```

two identical runs can produce different values.

### Separate business state from operational metadata

It can be valid for:

```text
pipeline_run_id
load_observed_at
```

to change on a replay while:

```text
business rows
```

remain exactly the same.

Define what "idempotent" means for the system.

---

## 27. Example 8 — Idempotent Incremental Load

Assume:

```text
target:
product 1 → price 50
product 2 → price 25

source:
product 1 → price 50
product 2 → price 30
product 3 → price 200
```

Use:

```sql
INSERT INTO products (
    product_id,
    product_name,
    price,
    updated_at
)
SELECT
    product_id,
    product_name,
    price,
    updated_at
FROM staging_products
ON CONFLICT (product_id)
DO UPDATE
SET
    product_name = EXCLUDED.product_name,
    price = EXCLUDED.price,
    updated_at = EXCLUDED.updated_at
WHERE
    products.product_name IS DISTINCT FROM EXCLUDED.product_name
    OR products.price IS DISTINCT FROM EXCLUDED.price;
```

Run the identical staging load again.

Expected business result:

```text
product 1 unchanged
product 2 remains 30
product 3 remains 200
```

No second business update should be generated for product 2 if its values are already the same.

---

# Part IV — Slowly Changing Dimensions

## 28. Slowly Changing Dimensions — Scope and Foundation

The full modelling theory of SCD types belongs to Module 2.8.

This chapter teaches only the SQL implementation knowledge needed here:

- current-state overwriting;
- historical versioning;
- validity ranges;
- surrogate keys;
- current-row flags;
- transaction-safe updates;
- deterministic history;
- idempotency;
- integrity assertions;
- late-arriving repairs;
- point-in-time joins.

### Why dimensions change

Customers can change:

```text
segment
region
status
account_manager
plan
```

Products can change:

```text
category
price class
brand
```

The analytical question may be:

> "What is true now?"

or:

> "What was true when the event happened?"

These are different questions.

---

## 29. SCD Type 1

Type 1 means:

> **Overwrite the old value with the new value.**

Example:

**BEFORE**

```text
customer_id | segment
------------+--------
101         | Bronze
```

**SOURCE**

```text
customer_id | segment
------------+--------
101         | Silver
```

**AFTER**

```text
customer_id | segment
------------+--------
101         | Silver
```

The previous value is replaced.

### When Type 1 fits

Use Type 1 when historical reconstruction of the old attribute is not required.

Typical reasons:

- current-state reporting only;
- correction of bad data;
- storage simplicity;
- no business need for historical versions.

Do not call Type 1 universally better or worse than Type 2. The correct design depends on the analytical requirement.

### Example 11 — SCD Type 1

```sql
CREATE TABLE dim_customer_current (
    customer_id BIGINT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment TEXT,
    status TEXT,
    updated_at TIMESTAMP NOT NULL
);
```

Load:

```sql
INSERT INTO dim_customer_current (
    customer_id,
    customer_name,
    segment,
    status,
    updated_at
)
SELECT
    customer_id,
    customer_name,
    segment,
    status,
    updated_at
FROM staging_customers
ON CONFLICT (customer_id)
DO UPDATE
SET
    customer_name = EXCLUDED.customer_name,
    segment = EXCLUDED.segment,
    status = EXCLUDED.status,
    updated_at = EXCLUDED.updated_at
WHERE
    dim_customer_current.customer_name IS DISTINCT FROM EXCLUDED.customer_name
    OR dim_customer_current.segment IS DISTINCT FROM EXCLUDED.segment
    OR dim_customer_current.status IS DISTINCT FROM EXCLUDED.status;
```

---

## 30. SCD Type 2

Type 2 preserves historical versions.

The implementation requires at least:

- `customer_sk` — surrogate row key;
- `customer_id` — business key;
- tracked attributes;
- `valid_from`;
- `valid_to`;
- `is_current`.

### Example structure

```sql
CREATE TABLE dim_customer (
    customer_sk BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    customer_name TEXT NOT NULL,
    segment TEXT,
    status TEXT,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP NOT NULL,
    is_current BOOLEAN NOT NULL
);
```

### Half-open interval convention

Use:

```text
[valid_from, valid_to)
```

Meaning:

```text
valid_from is included
valid_to is excluded
```

This avoids ambiguous boundaries.

### Timeline

```text
Customer 101

Bronze
2026-01-01 → 2026-01-10

Silver
2026-01-10 → 9999-12-31
```

The event at exactly:

```text
2026-01-10
```

belongs to the Silver version because:

```text
event_time >= '2026-01-10'
AND
event_time < valid_to
```

---

## 31. SCD Type 2 Mechanics

The fundamental state transition is:

```text
current version
      ↓
detect change
      ↓
expire old version
      ↓
insert new version
```

For one customer:

**BEFORE**

```text
customer_sk | customer_id | segment | valid_from  | valid_to    | is_current
------------+-------------+---------+-------------+-------------+-----------
1001        | 101         | Bronze  | 2026-01-01  | 9999-12-31  | true
```

**INCOMING**

```text
customer_id | segment | effective_date
------------+---------+---------------
101         | Silver  | 2026-01-10
```

**AFTER**

```text
customer_sk | customer_id | segment | valid_from  | valid_to    | is_current
------------+-------------+---------+-------------+-------------+-----------
1001        | 101         | Bronze  | 2026-01-01  | 2026-01-10  | false
1002        | 101         | Silver  | 2026-01-10  | 9999-12-31  | true
```

---

## 32. Two-Step SCD2 Approach

The simplest implementation is:

```text
UPDATE current version
        ↓
INSERT new version
```

Both operations belong to one database transaction.

### Why one transaction?

Bad:

```text
UPDATE old version
COMMIT

INSERT new version
-- failure
```

Now history can contain:

```text
no current row
```

Correct:

```sql
BEGIN;

UPDATE ...
;

INSERT ...
;

COMMIT;
```

If the insert fails:

```text
ROLLBACK
```

and the expired-row change is also rolled back.

### Example 12 — Basic SCD2 implementation

Assume `staging_customer_changes` has one deduplicated row per customer for this batch.

```sql
BEGIN;

-- Step 1: expire changed current rows.
UPDATE dim_customer AS d
SET
    valid_to = s.effective_date,
    is_current = false
FROM staging_customer_changes AS s
WHERE d.customer_id = s.customer_id
  AND d.is_current = true
  AND (
      d.customer_name IS DISTINCT FROM s.customer_name
      OR d.segment IS DISTINCT FROM s.segment
      OR d.status IS DISTINCT FROM s.status
  );

-- Step 2: insert new versions.
INSERT INTO dim_customer (
    customer_id,
    customer_name,
    segment,
    status,
    valid_from,
    valid_to,
    is_current
)
SELECT
    s.customer_id,
    s.customer_name,
    s.segment,
    s.status,
    s.effective_date,
    TIMESTAMP '9999-12-31 00:00:00',
    true
FROM staging_customer_changes AS s
WHERE NOT EXISTS (
    SELECT 1
    FROM dim_customer AS d
    WHERE d.customer_id = s.customer_id
      AND d.is_current = true
      AND d.customer_name IS NOT DISTINCT FROM s.customer_name
      AND d.segment IS NOT DISTINCT FROM s.segment
      AND d.status IS NOT DISTINCT FROM s.status
);

COMMIT;
```

### Important caveat

A production SCD2 load must define behavior for:

- new business keys;
- unchanged rows;
- changed rows;
- duplicate changes;
- multiple effective dates;
- late arrivals;
- out-of-order events.

The simple two-step form is the foundation, not the complete answer for every history workload.

---

## 33. Single-MERGE / UNION Technique

A more advanced idea is to shape a source set so that the mutation operation receives rows representing:

```text
the old version to expire
```

and:

```text
the new version to insert
```

Conceptually:

```text
business change
     ↓
two logical output rows

row A → update old version
row B → insert new version
```

A common technique is to use `UNION ALL` during source preparation.

### Conceptual source shaping

```sql
WITH changed AS (
    SELECT
        d.customer_id,
        d.customer_sk,
        d.segment AS old_segment,
        s.segment AS new_segment,
        s.effective_date
    FROM dim_customer AS d
    JOIN staging_customer_changes AS s
      ON d.customer_id = s.customer_id
    WHERE d.is_current = true
      AND d.segment IS DISTINCT FROM s.segment
),
merge_source AS (
    SELECT
        customer_sk,
        customer_id,
        'EXPIRE' AS action,
        old_segment AS segment,
        NULL::TIMESTAMP AS new_valid_from,
        effective_date AS new_valid_to
    FROM changed

    UNION ALL

    SELECT
        NULL AS customer_sk,
        customer_id,
        'INSERT' AS action,
        new_segment AS segment,
        effective_date AS new_valid_from,
        TIMESTAMP '9999-12-31 00:00:00' AS new_valid_to
    FROM changed
)
SELECT *
FROM merge_source;
```

The SQL design can then route:

```text
EXPIRE → update
INSERT → insert
```

### Why start with the two-step approach?

Because it is much easier to reason about:

```text
expire
→ insert
```

The advanced source-shaping technique should only be used when the engine capabilities and team can maintain it safely.

---

## 34. SCD Type 2 Integrity Assertions

A historical dimension is not correct merely because its SQL ran successfully.

You need post-conditions.

### Assertion 1 — Exactly one current row

```sql
SELECT
    customer_id
FROM dim_customer
GROUP BY customer_id
HAVING COUNT(*) FILTER (WHERE is_current) <> 1;
```

Expected:

```text
0 rows
```

### Assertion 2 — No overlapping ranges

For interval records ordered by `valid_from`, compare each row with the previous row.

```sql
WITH ordered AS (
    SELECT
        customer_id,
        customer_sk,
        valid_from,
        valid_to,
        LAG(valid_to) OVER (
            PARTITION BY customer_id
            ORDER BY valid_from, customer_sk
        ) AS previous_valid_to
    FROM dim_customer
)
SELECT
    customer_id,
    customer_sk,
    valid_from,
    valid_to,
    previous_valid_to
FROM ordered
WHERE previous_valid_to IS NOT NULL
  AND valid_from < previous_valid_to;
```

Expected:

```text
0 rows
```

If rows are returned, ranges overlap.

### Assertion 3 — No unintended gaps

```sql
WITH ordered AS (
    SELECT
        customer_id,
        customer_sk,
        valid_from,
        valid_to,
        LAG(valid_to) OVER (
            PARTITION BY customer_id
            ORDER BY valid_from, customer_sk
        ) AS previous_valid_to
    FROM dim_customer
)
SELECT
    customer_id,
    customer_sk,
    valid_from,
    previous_valid_to
FROM ordered
WHERE previous_valid_to IS NOT NULL
  AND valid_from <> previous_valid_to;
```

Expected:

```text
0 rows
```

### Important nuance

A gap can be valid if the business model explicitly allows periods where:

```text
no version existed
```

Therefore the assertion must match the business contract.

The checkpoint for this topic assumes the modeled history requires:

```text
one current row
no overlaps
no unintended gaps
```

---

## 35. Example 13 — SCD2 Multi-Change Timeline

Suppose customer 101 changes:

```text
2026-01-01 → Bronze
2026-01-10 → Silver
2026-01-20 → Gold
```

Represent source changes:

```text
customer_id | segment | effective_date
------------+---------+---------------
101         | Bronze  | 2026-01-01
101         | Silver  | 2026-01-10
101         | Gold    | 2026-01-20
```

Build intervals with `LEAD`:

```sql
WITH ordered_changes AS (
    SELECT
        customer_id,
        segment,
        effective_date,
        LEAD(effective_date) OVER (
            PARTITION BY customer_id
            ORDER BY effective_date
        ) AS next_effective_date
    FROM staging_customer_history
)
SELECT
    customer_id,
    segment,
    effective_date AS valid_from,
    COALESCE(
        next_effective_date,
        TIMESTAMP '9999-12-31 00:00:00'
    ) AS valid_to
FROM ordered_changes
ORDER BY customer_id, valid_from;
```

Result:

```text
customer_id | segment | valid_from  | valid_to
------------+---------+-------------+-------------
101         | Bronze  | 2026-01-01  | 2026-01-10
101         | Silver  | 2026-01-10  | 2026-01-20
101         | Gold    | 2026-01-20  | 9999-12-31
```

### Why `LEAD` matters

The next effective date defines:

```text
current version's valid_to
```

This is a clean example of how window functions from Topic 05 become an implementation tool in this topic.

---

## 36. Late-Arriving and Out-of-Order Changes

Normal history:

```text
Jan 1  → Bronze
Jan 10 → Silver
Jan 20 → Gold
```

Now a late event arrives on Jan 25:

```text
effective date = Jan 7
segment = Starter
```

The event is late because:

```text
arrival time = Jan 25
effective time = Jan 7
```

### Why simple append fails

Appending:

```text
Starter
Jan 7 → 9999-12-31
```

creates overlap with:

```text
Silver
Jan 10 → Jan 20
```

and:

```text
Gold
Jan 20 → 9999-12-31
```

### Correct reasoning

A late-arriving change can require:

```text
resequence affected history
→ recalculate boundaries
→ preserve one current row
→ preserve non-overlap
```

### Example 14 — Late-arriving repair

**BEFORE**

```text
customer_id | segment | valid_from  | valid_to    | is_current
------------+---------+-------------+-------------+-----------
101         | Bronze  | 2026-01-01  | 2026-01-10  | false
101         | Silver  | 2026-01-10  | 2026-01-20  | false
101         | Gold    | 2026-01-20  | 9999-12-31  | true
```

**LATE EVENT**

```text
101 | Starter | 2026-01-07
```

Correct historical sequence:

```text
Bronze
2026-01-01 → 2026-01-07

Starter
2026-01-07 → 2026-01-10

Silver
2026-01-10 → 2026-01-20

Gold
2026-01-20 → 9999-12-31
```

### Rebuild impacted customer history

For a bounded set of customers, a reliable pattern is to rebuild the affected history from the authoritative effective-dated source within one transaction.

Conceptually:

```sql
BEGIN;

DELETE FROM dim_customer
WHERE customer_id = 101;

INSERT INTO dim_customer (
    customer_id,
    customer_name,
    segment,
    status,
    valid_from,
    valid_to,
    is_current
)
WITH ordered AS (
    SELECT
        customer_id,
        customer_name,
        segment,
        status,
        effective_date,
        LEAD(effective_date) OVER (
            PARTITION BY customer_id
            ORDER BY effective_date, source_event_id
        ) AS next_effective_date,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY effective_date DESC, source_event_id DESC
        ) AS reverse_rank
    FROM authoritative_customer_history
    WHERE customer_id = 101
)
SELECT
    customer_id,
    customer_name,
    segment,
    status,
    effective_date AS valid_from,
    COALESCE(
        next_effective_date,
        TIMESTAMP '9999-12-31 00:00:00'
    ) AS valid_to,
    reverse_rank = 1 AS is_current
FROM ordered
ORDER BY effective_date;

COMMIT;
```

This example assumes the authoritative source can reconstruct the customer's complete effective-dated history.

### Production lesson

Late-arriving SCD2 logic is fundamentally a **history-resequencing problem**.

Do not "just insert another row."

---

## 37. Point-in-Time Joins

One of the most important uses of SCD2 is historical analysis.

Suppose an order occurred:

```text
2026-01-12
```

and customer 101 was:

```text
Silver
```

on that date.

Today the customer is:

```text
Gold
```

A current-state join answers:

```text
What is the customer now?
```

A point-in-time join answers:

```text
What was the customer's attribute when the fact occurred?
```

### Standard condition

```sql
event_time >= valid_from
AND event_time < valid_to
```

### Example 15 — Point-in-time join

```sql
SELECT
    f.order_id,
    f.customer_id,
    f.event_time,
    f.amount,
    d.segment
FROM fact_orders AS f
JOIN dim_customer AS d
    ON f.customer_id = d.customer_id
   AND f.event_time >= d.valid_from
   AND f.event_time < d.valid_to;
```

### Timeline reasoning

Dimension:

```text
Bronze
[2026-01-01, 2026-01-10)

Silver
[2026-01-10, 2026-01-20)

Gold
[2026-01-20, 9999-12-31)
```

Fact:

```text
2026-01-09
```

Matches:

```text
Bronze
```

Fact:

```text
2026-01-10
```

Matches:

```text
Silver
```

because:

```text
event_time >= valid_from
```

and the prior Bronze interval excludes its `valid_to`.

### Business comparison

Historical:

```text
revenue by customer segment as it was at event time
```

Current-state:

```text
revenue by customer segment as the customer is classified now
```

These can produce different business answers.

---

# Part V — Delete, Idempotency, and Edge Cases

## 38. Required Edge Cases

A production incremental load should explicitly define behavior for:

```text
duplicate source keys
duplicate target keys
NULL business columns
NULL comparisons
NULL keys
unchanged rows
changed rows
new rows
deletes
tombstones
missing snapshot rows
late arrivals
out-of-order changes
equal timestamps
ties
empty staging
empty target
source-only deletes
source-only updates
source-only inserts
repeated reruns
partial failure
rollback
valid_from = event_time
valid_to = event_time
overlaps
gaps
multiple current rows
```

### NULL keys

A business key that is NULL is often not a valid identity.

For example:

```text
customer_id = NULL
```

should usually fail validation before merge.

Assertion:

```sql
SELECT *
FROM staging_customers
WHERE customer_id IS NULL;
```

### Empty staging

Decide explicitly:

```text
empty staging means:
    no changes
```

or:

```text
empty staging means:
    source failure
```

Do not let an empty input accidentally trigger a full delete.

### Only deletes

If the source contains only tombstones:

```text
101 → DELETE
102 → DELETE
```

the pipeline should still behave correctly and leave unaffected entities alone.

### Equal timestamps

If:

```text
event_time = same timestamp
```

for two source rows, add:

```text
sequence_number
event_id
ingestion_id
```

or another deterministic ordering key.

---

## 39. Hard Delete vs Soft Delete vs Tombstone

### Hard delete

```sql
DELETE FROM customers
WHERE customer_id = 101;
```

### Soft delete

```sql
UPDATE customers
SET
    is_deleted = true,
    deleted_at = TIMESTAMP '2026-09-28 12:00:00'
WHERE customer_id = 101;
```

### Tombstone

Source:

```text
customer_id | operation
------------+----------
101         | DELETE
```

Target logic:

```sql
MERGE INTO customers AS t
USING staging_customer_events AS s
ON t.customer_id = s.customer_id

WHEN MATCHED
     AND s.operation = 'DELETE'
THEN
    UPDATE SET
        is_deleted = true,
        deleted_at = s.event_time

WHEN MATCHED
     AND s.operation <> 'DELETE'
THEN
    UPDATE SET
        is_deleted = false,
        segment = s.segment

WHEN NOT MATCHED
     AND s.operation <> 'DELETE'
THEN
    INSERT (
        customer_id,
        segment,
        is_deleted
    )
    VALUES (
        s.customer_id,
        s.segment,
        false
    );
```

The exact delete model depends on source semantics and retention requirements.

---

# Part VI — Performance Reasoning

## 40. Merge Performance

A production merge should be analyzed with the same discipline as any large data-engineering transformation.

Ask:

1. What is the merge key?
2. Is the source deduplicated?
3. How many source rows are processed?
4. How many target rows may be searched?
5. Is the target merge key indexed?
6. Can affected partitions be isolated?
7. Is the batch size appropriate?
8. How long is the transaction?
9. How much data actually changes?
10. Are unchanged rows being rewritten?

### Target merge key

If PostgreSQL must repeatedly locate:

```text
product_id
```

on a large target, a suitable index can be critical.

The exact plan should be measured with `EXPLAIN`, connecting directly to Topic 08.

### Batch size

Tiny batches can increase:

```text
transaction overhead
```

Large batches can increase:

```text
transaction duration
lock duration
rollback scope
```

The right batch size is a workload measurement question.

### Partition-scoped processing

If only:

```text
2026-09-28
```

is affected, avoid scanning unrelated historical data when the physical layout allows effective pruning.

Partitioning is not automatically better. It is useful when workload boundaries align with the physical design.

### Avoid unchanged writes

Compare:

```text
source value
vs
target value
```

before rewriting.

---

## 41. Indexes on Merge Keys

PostgreSQL example:

```sql
CREATE UNIQUE INDEX ux_products_product_id
ON products (product_id);
```

If the column is already a primary key:

```text
primary key
→ underlying uniqueness
→ useful lookup structure
```

### Trade-off

Indexes help locate target rows but also increase write maintenance.

For very large loads, consider:

```text
read/lookup cost
vs
write/index maintenance cost
```

Do not blindly add indexes to every merge target.

---

## 42. Batch Sizing

A useful mental model:

```text
smaller batch
→ shorter failure scope
→ shorter transaction
→ more transaction overhead

larger batch
→ better amortization
→ longer transaction
→ larger rollback scope
```

Measure:

```text
rows/sec
transaction duration
lock duration
WAL/write volume
memory
retry cost
```

Use the workload to choose the batch size.

---

## 43. Partition-Scoped Merges

If the target is partitioned by date and the source only affects a small date range, scope the merge to the relevant partition or predicate when possible.

Conceptually:

```text
10 billion historical rows
      ↓
only 2026-09-28 affected
      ↓
process the affected slice
```

Benefits can include:

- less scanned data;
- improved pruning;
- smaller working sets;
- shorter operations.

Do not claim that partitioning automatically speeds every merge. Poor partition keys can make workloads worse.

---

# Part VII — Snapshot Tables vs SCD2

## 44. Snapshot Tables

An alternative to SCD2 is to store periodic complete snapshots:

```text
dim_customer_snapshot_2026_01_01
dim_customer_snapshot_2026_01_02
dim_customer_snapshot_2026_01_03
...
```

Or a single snapshot table:

```text
snapshot_date
customer_id
segment
status
```

### Benefits

- conceptually simple;
- easy daily reconstruction;
- direct "state on date X" queries;
- straightforward debugging.

### Costs

- more storage;
- repeated processing of unchanged rows;
- potentially larger daily writes.

---

## 45. Example 16 — Snapshot Table

```sql
CREATE TABLE customer_daily_snapshot (
    snapshot_date DATE NOT NULL,
    customer_id BIGINT NOT NULL,
    segment TEXT,
    status TEXT,
    PRIMARY KEY (snapshot_date, customer_id)
);
```

Daily load:

```sql
INSERT INTO customer_daily_snapshot (
    snapshot_date,
    customer_id,
    segment,
    status
)
SELECT
    DATE '2026-09-28',
    customer_id,
    segment,
    status
FROM staging_customers
ON CONFLICT (snapshot_date, customer_id)
DO UPDATE
SET
    segment = EXCLUDED.segment,
    status = EXCLUDED.status;
```

### SCD2 vs snapshots

| Concern | SCD2 | Snapshot table |
|---|---|---|
| Current state | Direct | Filter latest snapshot |
| Historical state | Version ranges | Snapshot date |
| Storage | Change-oriented | Snapshot-oriented |
| Point-in-time query | Range join | Date/snapshot join |
| Late correction | Can require interval repair | Can require snapshot repair |
| Query model | More complex | Often simpler |
| Best fit | Change history is primary concern | Periodic state reconstruction is acceptable |

Do not choose based on a permanent "winner." Choose from:

```text
history requirements
storage
query patterns
source cadence
correction frequency
engine capabilities
operational simplicity
```

---

# Part VIII — Full Worked Production Examples

## 46. Example 17 — SCD2 Integrity Assertions

### Exactly one current version

```sql
SELECT
    customer_id
FROM dim_customer
GROUP BY customer_id
HAVING COUNT(*) FILTER (WHERE is_current) <> 1;
```

### Current row must have open-ended validity

```sql
SELECT *
FROM dim_customer
WHERE is_current = true
  AND valid_to <> TIMESTAMP '9999-12-31 00:00:00';
```

### Historical rows should not be current

```sql
SELECT *
FROM dim_customer
WHERE is_current = false
  AND valid_to = TIMESTAMP '9999-12-31 00:00:00';
```

### Overlap detection

```sql
WITH ordered AS (
    SELECT
        customer_id,
        customer_sk,
        valid_from,
        valid_to,
        LAG(valid_to) OVER (
            PARTITION BY customer_id
            ORDER BY valid_from, customer_sk
        ) AS previous_valid_to
    FROM dim_customer
)
SELECT *
FROM ordered
WHERE previous_valid_to IS NOT NULL
  AND valid_from < previous_valid_to;
```

### Gap detection

```sql
WITH ordered AS (
    SELECT
        customer_id,
        customer_sk,
        valid_from,
        valid_to,
        LAG(valid_to) OVER (
            PARTITION BY customer_id
            ORDER BY valid_from, customer_sk
        ) AS previous_valid_to
    FROM dim_customer
)
SELECT *
FROM ordered
WHERE previous_valid_to IS NOT NULL
  AND valid_from <> previous_valid_to;
```

### Key reconciliation

```sql
SELECT customer_id
FROM staging_customer_changes

EXCEPT

SELECT customer_id
FROM dim_customer
WHERE is_current = true;
```

Then reverse the comparison when the business rule requires it.

---

## 47. Example 18 — Reconciliation Counts

For a source batch:

```text
staged_count
insert_count
update_count
delete_count
unchanged_count
```

A simple expected relationship is:

```text
staged_count =
    inserts
  + changed rows
  + unchanged rows
  + deletes
```

but the exact accounting depends on source semantics.

### Changed-row classification

A useful query:

```sql
SELECT
    CASE
        WHEN t.product_id IS NULL THEN 'insert'
        WHEN t.product_name IS DISTINCT FROM s.product_name
          OR t.price IS DISTINCT FROM s.price
            THEN 'update'
        ELSE 'unchanged'
    END AS action,
    COUNT(*) AS row_count
FROM staging_products AS s
LEFT JOIN products AS t
    ON t.product_id = s.product_id
GROUP BY 1
ORDER BY 1;
```

This is often easier to reason about than blindly looking at affected-row counts.

---

# Part IX — Debugging

## 48. Debugging MERGE, Upsert, and SCD Problems

Use this workflow:

```text
1. Check source grain
2. Check target grain
3. Check key uniqueness
4. Check duplicate source rows
5. Check NULL keys
6. Inspect changed vs unchanged rows
7. Validate delete markers
8. Check transaction boundaries
9. Inspect SCD validity ranges
10. Re-run with a tiny dataset
11. Compare before/after target state
12. Verify idempotency
```

The first five steps often expose the real root cause.

---

## 49. Failure A — Multiple Source Rows Match One Target

**Symptom**

> The merge is unsafe or fails because several source rows correspond to one target entity.

**Broken scenario**

```text
product_id = 10
appears twice in staging
```

**Why**

The merge source does not have the required grain.

**Diagnosis**

```sql
SELECT product_id, COUNT(*)
FROM staging_products
GROUP BY product_id
HAVING COUNT(*) > 1;
```

**Corrected approach**

Deduplicate with deterministic ranking.

**Production lesson**

Source uniqueness is a pipeline invariant.

---

## 50. Failure B — Every Row Is Updated Every Run

**Symptom**

```text
second run
→ thousands of updates
```

**Why**

The merge updates on every conflict.

**Detection**

Compare business columns:

```sql
SELECT COUNT(*)
FROM staging_products AS s
JOIN products AS t
  ON t.product_id = s.product_id
WHERE t.product_name IS DISTINCT FROM s.product_name
   OR t.price IS DISTINCT FROM s.price;
```

If this count is much smaller than the affected rows, unnecessary updates are likely.

**Corrected approach**

Use a conditional update.

```sql
WHERE
    t.price IS DISTINCT FROM EXCLUDED.price
```

or the equivalent `MERGE` condition.

---

## 51. Failure C — Two Current SCD2 Rows

**Symptom**

```text
customer_id = 101
is_current = true
is_current = true
```

**Diagnosis**

```sql
SELECT customer_id
FROM dim_customer
GROUP BY customer_id
HAVING COUNT(*) FILTER (WHERE is_current) <> 1;
```

**Likely causes**

- non-atomic update/insert;
- duplicate source changes;
- late-arriving repair bug;
- concurrent writers;
- incorrect current-row condition.

**Corrected approach**

Repair affected business keys and add a hard database safeguard where the model permits one-current-row uniqueness.

A PostgreSQL example is a partial unique index:

```sql
CREATE UNIQUE INDEX ux_dim_customer_one_current
ON dim_customer (customer_id)
WHERE is_current = true;
```

This is a powerful database-level guarantee.

---

## 52. Failure D — Overlapping SCD2 Ranges

**Diagnosis**

```sql
WITH ordered AS (
    SELECT
        customer_id,
        customer_sk,
        valid_from,
        valid_to,
        LAG(valid_to) OVER (
            PARTITION BY customer_id
            ORDER BY valid_from, customer_sk
        ) AS previous_valid_to
    FROM dim_customer
)
SELECT *
FROM ordered
WHERE previous_valid_to IS NOT NULL
  AND valid_from < previous_valid_to;
```

**Why**

A new interval was inserted without resequencing affected history.

**Corrected approach**

Recompute affected boundaries.

---

## 53. Failure E — Historical Query Gives Wrong Segment

**Likely cause**

The query uses:

```sql
f.customer_id = d.customer_id
```

but omits validity.

Wrong:

```sql
JOIN dim_customer AS d
  ON f.customer_id = d.customer_id
```

Correct:

```sql
JOIN dim_customer AS d
  ON f.customer_id = d.customer_id
 AND f.event_time >= d.valid_from
 AND f.event_time < d.valid_to
```

**Production lesson**

An SCD2 table is not a current-state dimension until you explicitly choose the current row.

---

## 54. Failure F — Second Run Changes Data Again

**Symptom**

```text
Run 1 → updates 50 rows
Run 2 → updates 50 rows again
```

**Possible causes**

- current timestamp used in business-state comparison;
- unstable deduplication;
- source ordering changing;
- comparison columns include operational metadata;
- surrogate key regenerated;
- history rows recreated every run.

**Corrected approach**

Define business-state equality explicitly.

```text
same business values
+
same history
+
same current flags
=
same business state
```

---

# Part X — Hands-On Exercises

## 55. Exercise 1 — Product Price Upsert

### Objective

Upsert daily product-price data into `products`.

### Setup

```sql
CREATE TABLE products (
    product_id BIGINT PRIMARY KEY,
    product_name TEXT,
    price NUMERIC(12, 2)
);

INSERT INTO products VALUES
    (1, 'Keyboard', 50.00),
    (2, 'Mouse', 25.00);
```

### Task

Incoming data:

```text
1 → 50
2 → 30
3 → 200
```

Write:

```sql
INSERT ... ON CONFLICT
```

such that unchanged rows are not rewritten.

### Expected result

```text
1 → unchanged
2 → updated
3 → inserted
```

### Solution

```sql
INSERT INTO products (
    product_id,
    product_name,
    price
)
VALUES
    (1, 'Keyboard', 50.00),
    (2, 'Mouse', 30.00),
    (3, 'Monitor', 200.00)
ON CONFLICT (product_id)
DO UPDATE
SET
    product_name = EXCLUDED.product_name,
    price = EXCLUDED.price
WHERE
    products.product_name IS DISTINCT FROM EXCLUDED.product_name
    OR products.price IS DISTINCT FROM EXCLUDED.price;
```

### Explanation

The `WHERE` condition makes the update change-only.

---

## 56. Exercise 2 — Rewrite with MERGE

### Objective

Rewrite the product load with PostgreSQL `MERGE`.

### Task

Support:

- update;
- insert;
- delete when `is_discontinued = true`.

### Solution

```sql
MERGE INTO products AS t
USING staging_products AS s
ON t.product_id = s.product_id

WHEN MATCHED
     AND s.is_discontinued = true
THEN
    DELETE

WHEN MATCHED
     AND s.is_discontinued = false
     AND (
         t.product_name IS DISTINCT FROM s.product_name
         OR t.price IS DISTINCT FROM s.price
     )
THEN
    UPDATE SET
        product_name = s.product_name,
        price = s.price

WHEN NOT MATCHED
     AND s.is_discontinued = false
THEN
    INSERT (
        product_id,
        product_name,
        price
    )
    VALUES (
        s.product_id,
        s.product_name,
        s.price
    );
```

### Explanation

The action branches encode business state transitions explicitly.

---

## 57. Exercise 3 — Duplicate Source Failure

### Objective

Prove why source deduplication is necessary.

### Setup

```sql
INSERT INTO staging_products (
    product_id,
    product_name,
    price,
    updated_at,
    ingestion_id
)
VALUES
    (10, 'Monitor', 200.00, TIMESTAMP '2026-09-28 10:00:00', 100),
    (10, 'Monitor', 210.00, TIMESTAMP '2026-09-28 10:00:00', 101);
```

### Task

1. Find the duplicate.
2. Explain why merge is unsafe.
3. Choose the survivor.
4. Write the deduplication query.

### Solution

```sql
SELECT
    product_id,
    COUNT(*)
FROM staging_products
GROUP BY product_id
HAVING COUNT(*) > 1;
```

Deduplicate:

```sql
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY
                updated_at DESC,
                ingestion_id DESC
        ) AS rn
    FROM staging_products AS s
)
SELECT *
FROM ranked
WHERE rn = 1;
```

### Expected survivor

The row with:

```text
ingestion_id = 101
```

wins because it is the deterministic final tie-breaker.

---

## 58. Exercise 4 — 10-Day Customer SCD2

### Objective

Build `dim_customer` history from ten daily snapshots.

### Task

For one customer, provide changes such as:

```text
Day 1  Bronze
Day 2  Bronze
Day 3  Silver
Day 4  Silver
Day 5  Silver
Day 6  Gold
Day 7  Gold
Day 8  Platinum
Day 9  Platinum
Day 10 Platinum
```

### Required behavior

Only actual changes create new SCD2 versions.

Expected history:

```text
Bronze
→ Day 1 through Day 3 boundary

Silver
→ Day 3 through Day 6 boundary

Gold
→ Day 6 through Day 8 boundary

Platinum
→ Day 8 onward
```

### Required assertions

```text
one current row
no overlap
no unintended gaps
```

### Solution strategy

1. Deduplicate each daily source.
2. Compare against current state.
3. Expire changed version.
4. Insert new version.
5. Run integrity assertions after each day.
6. Re-run a day and verify idempotency.

---

## 59. Exercise 5 — Late-Arriving Change

### Objective

Repair historical SCD2 state.

### Setup

Existing history:

```text
Bronze  [2026-01-01, 2026-01-10)
Silver  [2026-01-10, 2026-01-20)
Gold    [2026-01-20, 9999-12-31)
```

Late event:

```text
Starter
effective_date = 2026-01-07
```

### Task

Recalculate the intervals.

### Expected result

```text
Bronze  [2026-01-01, 2026-01-07)
Starter [2026-01-07, 2026-01-10)
Silver  [2026-01-10, 2026-01-20)
Gold    [2026-01-20, 9999-12-31)
```

### Solution approach

Rebuild the affected customer's sequence from the authoritative history and use `LEAD` to recalculate `valid_to`.

### Required validation

```text
one current row
no overlaps
no gaps
```

---

## 60. Exercise 6 — Point-in-Time Revenue

### Objective

Compare historical segment attribution with current segment attribution.

### Task

Join:

```text
fact_orders
```

to:

```text
dim_customer
```

using the event timestamp.

### Solution

```sql
SELECT
    f.order_id,
    f.customer_id,
    f.amount,
    f.event_time,
    d.segment
FROM fact_orders AS f
JOIN dim_customer AS d
    ON f.customer_id = d.customer_id
   AND f.event_time >= d.valid_from
   AND f.event_time < d.valid_to;
```

Then compare with a current-state query:

```sql
SELECT
    f.customer_id,
    SUM(f.amount) AS revenue,
    d.segment AS current_segment
FROM fact_orders AS f
JOIN dim_customer AS d
    ON f.customer_id = d.customer_id
   AND d.is_current = true
GROUP BY
    f.customer_id,
    d.segment;
```

### Explanation

The first query answers:

```text
What segment did the customer have when the order happened?
```

The second answers:

```text
What segment does the customer have now?
```

---

## 61. Exercise 7 — Idempotency

### Objective

Prove the load can be replayed safely.

### Task

1. Record target business state.
2. Run the load.
3. Record state.
4. Run the exact same load again.
5. Compare.

### Suggested comparison

```sql
SELECT *
FROM products
ORDER BY product_id;
```

Run after each attempt and compare:

```text
business values
history
current flags
```

### Expected

The second identical run produces no additional business-state changes.

---

# Part XI — Paper-First Reasoning

## 62. Hand-Draw Before SQL

Before executing SQL, draw:

### Exercise A — Upsert

**TARGET BEFORE**

```text
product_id | price
-----------+------
1          | 50
2          | 25
```

**SOURCE**

```text
product_id | price
-----------+------
1          | 50
2          | 30
3          | 200
```

Predict:

```text
unchanged
updated
inserted
```

Only after predicting should you run SQL.

### Exercise B — SCD2

Draw:

```text
Customer 101
Bronze
Silver
Gold
```

Then write:

```text
valid_from
valid_to
is_current
```

### Exercise C — Late arrival

Insert:

```text
Starter @ Jan 7
```

into:

```text
Bronze @ Jan 1
Silver  @ Jan 10
Gold    @ Jan 20
```

Redraw all affected intervals.

### Why paper-first?

SQL syntax can hide logic.

Drawing the state first forces you to answer:

```text
what should the final table actually look like?
```

---

# Part XII — Mini-Challenges

## 63. Mini-Challenge 1 — Predict the Upsert

Target:

```text
1 → A
2 → B
```

Source:

```text
2 → B
3 → C
```

Question:

```text
Which rows change?
```

### Answer

```text
1 → unchanged
2 → unchanged
3 → insert
```

---

## 64. Mini-Challenge 2 — Find the Unsafe Source

Source:

```text
customer_id | segment
------------+--------
101         | Bronze
101         | Silver
```

Question:

> What makes this unsafe for a one-row-per-customer merge?

### Answer

The source does not match the target merge grain.

---

## 65. Mini-Challenge 3 — Choose the Survivor

Rows:

```text
customer_id | updated_at           | source_priority | event_id
------------+----------------------+-----------------+---------
101         | 2026-09-28 10:00:00  | 1               | 10
101         | 2026-09-28 10:00:00  | 2               | 11
101         | 2026-09-28 10:00:00  | 2               | 12
```

Rule:

```text
latest timestamp
→ highest source priority
→ highest event_id
```

### Answer

```text
event_id = 12
```

---

## 66. Mini-Challenge 4 — Identify the SCD2 Version

Dimension:

```text
Bronze  [Jan 1, Jan 10)
Silver  [Jan 10, Jan 20)
Gold    [Jan 20, ∞)
```

Event time:

```text
Jan 10
```

### Answer

```text
Silver
```

because `valid_from` is inclusive and `valid_to` is exclusive.

---

## 67. Mini-Challenge 5 — Find the Overlap

Rows:

```text
Bronze  [Jan 1, Jan 10)
Silver  [Jan 9, Jan 20)
```

### Answer

Overlap from:

```text
Jan 9 → Jan 10
```

The integrity assertion should return these rows.

---

## 68. Mini-Challenge 6 — Why Did Run 2 Change the Table?

Run 1:

```text
updated_at = 10:00
```

Run 2:

```text
updated_at = CURRENT_TIMESTAMP
```

Business values did not change.

### Answer

Operational metadata was treated as a business change.

Correct the change-detection predicate.

---

# Part XIII — Production Trade-Offs

## 69. Upsert vs MERGE

Do not create a permanent ranking.

Compare:

| Concern | `ON CONFLICT` | `MERGE` |
|---|---|---|
| PostgreSQL simplicity | Strong | Strong |
| Expressiveness | Focused on insert conflict | Multiple conditional branches |
| Dialect portability | PostgreSQL-specific | Standard concept, dialect syntax differs |
| Delete branch | Separate logic | Natural merge branch |
| Conditional actions | Supported | Rich branch model |
| Maintainability | Often simple | Can become complex |
| Best fit | Clear key-conflict upsert | Multi-action reconciliation |

The right choice depends on:

```text
engine
business rules
delete semantics
team familiarity
readability
portability
```

---

## 70. Type 1 vs Type 2

### Type 1

```text
current truth
```

Useful when historical values are not needed.

### Type 2

```text
historical truth
```

Useful when events must be interpreted using the attributes that were valid at that time.

The choice depends on:

```text
history requirement
query patterns
storage
business questions
```

---

## 71. Two-Step SCD2 vs MERGE-Based SCD2

### Two-step

```text
expire
→ insert
```

Strengths:

- explicit;
- easy to debug;
- easy to teach;
- straightforward transaction reasoning.

Costs:

- multiple statements;
- requires careful atomicity.

### MERGE-based

Strengths:

- compact statement-level reconciliation;
- can express branches in one command.

Costs:

- harder to reason about for complex history;
- more dialect/version sensitivity;
- source shaping may become complicated.

### Decision principle

Prefer the design the team can:

```text
prove correct
test
debug
operate
```

not the one with the fewest lines.

---

## 72. SCD2 vs Snapshot Tables

Use SCD2 when:

```text
change history is central
```

Use snapshots when:

```text
periodic full-state reconstruction is simpler
```

Consider:

```text
storage
query complexity
correction frequency
snapshot cadence
source capabilities
```

No permanent winner exists.

---

# Part XIV — Production Case Study

## 73. Production Case Study — Subscription Business

### Scenario

A subscription business receives daily customer, plan, and order data.

Target objects:

```text
customers
products
dim_customer
fact_orders
job_runs
```

Pipeline:

```text
daily source extract
        ↓
staging
        ↓
validation
        ↓
dedupe
        ↓
incremental upsert / MERGE
        ↓
SCD Type 1 / Type 2
        ↓
point-in-time facts
        ↓
reconciliation
        ↓
idempotency verification
```

### Initial load

Source:

```text
customer 101 → Bronze
customer 102 → Silver
```

Target starts empty.

Load result:

```text
101 → Bronze
102 → Silver
```

### Normal update

Next day:

```text
101 → Silver
```

Current-state target:

```text
101 → Silver
```

For SCD2:

```text
Bronze [day 1, day 2)
Silver [day 2, ∞)
```

### Insert

```text
103 → Bronze
```

Add customer 103.

### Delete

Source explicitly sends:

```text
102 → DELETE
```

Apply the configured delete model.

Do not infer the delete solely from missing rows unless the source is authoritative and complete.

### Duplicate source record

Input:

```text
101 → Silver
101 → Silver
```

Deduplicate before mutation.

### Unchanged record

Input:

```text
103 → Bronze
```

Target already contains:

```text
103 → Bronze
```

No business-state update should occur.

### Late historical correction

Input:

```text
customer 101
segment = Starter
effective date = 2026-09-10
arrival date = 2026-09-20
```

Repair impacted SCD2 intervals.

### Second identical run

Run the same source again.

Expected:

```text
same business state
same historical versions
same current flags
no duplicate versions
```

---

## 74. Case Study — Required Design Record

For each pipeline component, document:

```text
Problem:
Invariant:
Concurrent actors:
Transaction boundary:
Identity/key:
Source grain:
Target grain:
Insert behavior:
Update behavior:
Delete behavior:
History behavior:
Deduplication rule:
Isolation/transaction requirements:
Failure mode:
Retry strategy:
Validation:
Reconciliation:
Idempotency proof:
Performance strategy:
Observability:
```

### Complete solution

#### Customer current state

```text
Problem:
Keep current customer attributes synchronized.

Invariant:
At most one current customer row per customer_id.

Concurrent actors:
Daily pipeline + possible retry.

Transaction:
Validated apply.

Identity:
customer_id.

Change detection:
Tracked business columns using NULL-safe comparison.

Delete:
Explicit source delete marker / source contract.

Validation:
No NULL customer IDs.
No duplicate source customer IDs.
Exactly one target current row.
```

#### Customer SCD2

```text
Problem:
Preserve historical customer attribute values.

Invariant:
One current row.
No overlapping intervals.
No unintended gaps.

Transaction:
Expire + insert together.

Key:
customer_id = business key.
customer_sk = versioned surrogate key.

Late arrival:
Recompute impacted intervals.

Validation:
Zero-row integrity assertions.
```

#### Orders

```text
Problem:
Correct historical customer segmentation.

Strategy:
Point-in-time join using event_time.
```

#### Job execution

```text
Problem:
Prevent duplicate daily execution.

Strategy:
Transaction-safe job state + database uniqueness where possible.
```

### Why not simply MERGE everything?

Because the transformation has different semantic problems:

```text
current-state reconciliation
vs
historical versioning
vs
delete semantics
vs
event-time interpretation
```

One SQL keyword does not eliminate those modeling decisions.

---

# Part XV — Senior Data Engineer Decision Framework

## 75. Senior Data Engineer Thinking

Approach every incremental-load problem in this order:

```text
1. Define target grain.
2. Define row identity / business key.
3. Define source grain.
4. Define what counts as a change.
5. Define insert behavior.
6. Define update behavior.
7. Define delete behavior.
8. Define history requirements.
9. Define effective-time semantics.
10. Deduplicate source deterministically.
11. Define transaction boundaries.
12. Define idempotency.
13. Define assertions.
14. Define reconciliation.
15. Define performance strategy.
16. Define retry behavior.
17. Define observability.
18. Test pathological cases.
```

### 1. Target grain

```text
one row = what?
```

### 2. Identity

```text
which key identifies the entity?
```

### 3. Source grain

```text
one incoming row = what?
```

### 4. Change definition

```text
which columns matter?
```

### 5. Insert

```text
what happens if target identity does not exist?
```

### 6. Update

```text
what happens if business data changed?
```

### 7. Delete

```text
hard delete?
soft delete?
tombstone?
no deletion?
```

### 8. History

```text
Type 1?
Type 2?
snapshot?
```

### 9. Effective time

Distinguish:

```text
arrival time
event time
effective time
processing time
```

### 10. Deterministic deduplication

If two rows compete, the winner must be defined.

### 11. Transaction boundaries

The atomic unit should be:

```text
the state transition that must publish together
```

not necessarily the entire pipeline.

### 12. Idempotency

Prove:

```text
same input
→ same business state
```

### 13. Assertions

Make invalid state detectable.

### 14. Reconciliation

Track:

```text
expected
actual
inserted
updated
deleted
unchanged
```

### 15. Performance

Measure:

```text
source volume
target scan
index lookup
partition pruning
changed fraction
transaction time
```

### 16. Retry

Define which failures can be retried safely.

### 17. Observability

Log:

```text
run id
source batch
source row count
deduped row count
insert count
update count
delete count
duration
failure reason
retry count
```

### 18. Pathological cases

Always test:

```text
duplicates
NULLs
empty input
only deletes
only inserts
only updates
late arrivals
ties
replays
partial failures
```

---

# Part XVI — Architecture Review Questions

## 76. Scenario 1 — 100-Million-Row Daily Customer Snapshot

Ask:

```text
full refresh or incremental?
how will changes be identified?
what is the key?
how will duplicates be removed?
what counts as changed?
how will unchanged rows avoid rewrites?
what is the publication transaction?
```

### Reasoning path

```text
source snapshot
→ source contract
→ key
→ change detection
→ source reduction
→ affected-row processing
→ target publication
```

Do not assume incremental is always better. Compare the actual changed fraction and operational cost.

---

## 77. Scenario 2 — Historical Customer Segments Required

Question:

> Customers must be reported according to their segment at order time. What design is required?

### Reasoning

```text
historical accuracy required
→ preserve versions
→ SCD2
→ validity intervals
→ point-in-time join
```

---

## 78. Scenario 3 — Duplicate and Out-of-Order CDC

Question:

```text
duplicate events
+
out-of-order effective times
```

### Reasoning

```text
deduplicate
→ establish deterministic order
→ separate arrival time from effective time
→ repair/resequence history
→ assert intervals
```

---

## 79. Scenario 4 — Multi-Billion-Row Target

Ask:

```text
is merge key indexed?
can source be reduced?
can affected partitions be isolated?
how many rows actually change?
are unchanged rows being rewritten?
what is transaction size?
how much concurrency exists?
what does EXPLAIN say?
```

### Senior answer

Start from measurements.

Do not optimize `MERGE` by intuition alone.

---

# Part XVII — Interview and Architecture Questions

## 80. Basic Interview Questions

### Question 1 — What is an upsert?

**What the interviewer is testing:** State reconciliation fundamentals.

**Expected reasoning:** Explain insert vs update based on row identity.

**Strong answer:** An upsert inserts a row when its conflict identity is absent and updates the existing row when the identity already exists.

**Deeper answer:** In PostgreSQL, `ON CONFLICT` uses a unique constraint/index definition to identify the conflicting target row.

---

### Question 2 — Why is a unique constraint needed?

**Testing:** Key and identity reasoning.

**Strong answer:** The database needs a reliable uniqueness definition to determine when an incoming row conflicts with an existing target row.

**Deeper:** A business key should correspond to actual row identity; a mutable/non-unique attribute is unsafe.

---

### Question 3 — Full refresh vs incremental loading?

**Strong answer:** Full refresh rebuilds target state; incremental processing reconciles only new/changed/deleted data against existing state.

**Deeper:** Full refresh trades simplicity for potentially large compute/storage cost. Incremental requires key, change, delete, and idempotency semantics.

---

### Question 4 — What is `EXCLUDED`?

**Strong answer:** The incoming conflicting row in PostgreSQL `ON CONFLICT DO UPDATE`.

**Example:**

```sql
price = EXCLUDED.price
```

**Common mistake:** Thinking `EXCLUDED` refers to rows deleted from the table.

---

## 81. Intermediate Interview Questions

### Question 5 — Why deduplicate before MERGE?

**Testing:** Grain and correctness.

**Strong answer:** The source must match the target merge grain; multiple source rows for one target key make mutation ambiguous.

**Deeper:** Deduplication criteria are business logic and must be deterministic.

---

### Question 6 — What happens if two source rows match one target row?

**Strong answer:** The merge is unsafe and depending on the engine can fail or produce behavior you did not intend.

**Deeper:** The source must be shaped so each target identity has one authoritative source row for the merge operation.

---

### Question 7 — How do you avoid updating unchanged rows?

**Strong answer:** Add a change predicate using `IS DISTINCT FROM`.

**Example:**

```sql
WHERE t.price IS DISTINCT FROM EXCLUDED.price
```

**Common mistake:** Using `<>` when NULL is possible.

---

### Question 8 — What is a tombstone?

**Strong answer:** A source record explicitly indicating deletion.

**Deeper:** Absence from a change feed is not equivalent to a tombstone.

---

### Question 9 — Hard delete vs soft delete?

**Strong answer:** Hard delete removes the row; soft delete preserves the row and marks it deleted.

**Deeper:** The choice depends on retention, audit, historical, and downstream requirements.

---

## 82. Advanced Interview Questions

### Question 10 — Explain idempotent MERGE design.

**Strong answer:** The same source load can be replayed without changing the final business state beyond the first correct application.

**Deeper:** Idempotency requires deterministic source selection, stable identity, correct change detection, controlled delete semantics, and transaction-safe retries.

---

### Question 11 — How would you implement SCD2?

**Strong answer:** Match on the business key, detect attribute changes, expire the current row, and insert a new version in one transaction with `valid_from`, `valid_to`, `is_current`, and a surrogate key.

**Deeper:** The design also requires one-current-row, no-overlap, and no-unintended-gap assertions.

---

### Question 12 — Why must expiration + insertion be atomic?

**Strong answer:** Otherwise a failure between statements can leave the dimension with no current row or partially applied history.

**Deeper:** The two statements represent one logical historical state transition.

---

### Question 13 — How do you detect overlapping SCD2 ranges?

**Strong answer:** Order rows by `valid_from` and compare each `valid_from` with the previous `valid_to`.

**Example:**

```sql
LAG(valid_to) OVER (
    PARTITION BY customer_id
    ORDER BY valid_from
)
```

**Then:**

```sql
WHERE valid_from < previous_valid_to
```

---

### Question 14 — How do you repair late-arriving SCD2 changes?

**Strong answer:** Identify impacted entity history, insert the late event into the ordered effective-dated source, recalculate interval boundaries, then atomically replace or update affected versions.

**Deeper:** The key is historical resequencing, not appending.

---

### Question 15 — How does a point-in-time join work?

**Strong answer:** Join the fact to the dimension by business key plus the validity condition:

```sql
event_time >= valid_from
AND event_time < valid_to
```

---

### Question 16 — When would snapshot tables be preferable?

**Strong answer:** When periodic state capture is simpler and storage cost is acceptable.

**Deeper:** Snapshot tables can simplify historical state queries but may write far more unchanged data.

---

### Question 17 — How would you optimize a MERGE touching billions of rows?

**Strong answer:** First reduce the source, validate/deduplicate it, inspect the target access path, use appropriate indexing, restrict to affected partitions when possible, avoid unchanged writes, choose measured batch sizes, and inspect plans.

**Common mistake:** Adding indexes or partitions without measuring.

---

### Question 18 — How would you handle duplicate CDC events?

**Strong answer:** Deduplicate by business key plus event sequencing/version using deterministic rules before applying mutations.

---

### Question 19 — How would you design a retry-safe incremental pipeline?

**Strong answer:** Make source preparation replayable, define an idempotent target mutation, use transaction boundaries around publication, classify retryable failures, and verify final state with assertions.

---

### Question 20 — How do you choose between `ON CONFLICT` and `MERGE`?

**Strong answer:** Choose based on engine, business actions, delete requirements, readability, portability, and maintainability.

**Deeper:** A simpler expression of the actual business transition is usually easier to prove and operate.

---

# Part XVIII — Production Checklist

## 83. Correctness

- [ ] Target grain is defined.
- [ ] Source grain is defined.
- [ ] Business key is defined.
- [ ] The key is stable enough for the workflow.
- [ ] Target uniqueness is enforced.
- [ ] Source duplicates are checked.
- [ ] NULL key behavior is explicit.
- [ ] NULL comparison behavior is explicit.
- [ ] Insert semantics are explicit.
- [ ] Update semantics are explicit.
- [ ] Delete semantics are explicit.
- [ ] Tombstone behavior is explicit.
- [ ] Missing-source-row semantics are explicit.
- [ ] SCD2 intervals use a consistent boundary convention.
- [ ] Exactly one current SCD2 row is asserted.
- [ ] Overlap detection exists.
- [ ] Gap detection exists where gaps are invalid.

## 84. Idempotency

- [ ] The same input can be replayed.
- [ ] Source deduplication is deterministic.
- [ ] Unchanged rows remain unchanged.
- [ ] No duplicate SCD2 versions are created.
- [ ] Current flags remain correct.
- [ ] Operational timestamps are separated from business-state change detection.
- [ ] Retry behavior is safe.

## 85. Transaction Safety

- [ ] Related mutations are atomic.
- [ ] Failed runs do not leave partial history.
- [ ] SCD2 expiration and insertion occur in one transaction.
- [ ] The final publication boundary is explicit.
- [ ] External slow work is outside the critical transaction where possible.

## 86. Performance

- [ ] Merge key access is appropriate.
- [ ] Source volume is controlled.
- [ ] Unnecessary updates are avoided.
- [ ] Partition pruning is considered.
- [ ] Batch size is measured.
- [ ] Transaction duration is monitored.
- [ ] Query plans have been inspected.
- [ ] Write amplification is understood.

## 87. Testing

- [ ] Duplicate-source test.
- [ ] NULL-value test.
- [ ] NULL-key test.
- [ ] Insert test.
- [ ] Update test.
- [ ] Unchanged-row test.
- [ ] Delete test.
- [ ] Tombstone test.
- [ ] Empty staging test.
- [ ] Only-insert test.
- [ ] Only-update test.
- [ ] Only-delete test.
- [ ] Late-arriving-change test.
- [ ] Equal-timestamp tie test.
- [ ] SCD2 overlap test.
- [ ] Exactly-one-current-row test.
- [ ] Gap test.
- [ ] Point-in-time join test.
- [ ] Idempotency replay test.
- [ ] Transaction rollback test.

---

# Part XIX — Common Mistakes

## 88. Common Mistake Checklist

### Merging an undeduplicated source

**Broken:** Multiple source rows share one merge key.

**Fix:** Deduplicate first.

**Production lesson:** Source grain is a mutation precondition.

### Updating every row on every run

**Broken:** Unchanged rows receive new timestamps or versions.

**Fix:** Change-only predicates with `IS DISTINCT FROM`.

**Production lesson:** Business-state change should drive business-state mutation.

### SCD2 with overlapping ranges

**Broken:**

```text
Bronze [Jan 1, Jan 10)
Silver [Jan 9, Jan 20)
```

**Fix:** Resequence intervals.

### Expire old and insert new in separate transactions

**Broken:**

```text
expire → COMMIT
insert → failure
```

**Fix:** One transaction.

### Treating missing rows as deletes

**Broken:** A partial change feed causes accidental deletion.

**Fix:** Use source contract semantics.

### Non-deterministic deduplication

**Broken:** Equal timestamps with no tie-breaker.

**Fix:** Add a stable deterministic ordering column.

### Using a mutable field as identity

**Broken:** Email changes create a new entity.

**Fix:** Use the actual stable identity key.

### Mishandling NULL comparisons

**Broken:**

```sql
old_value <> new_value
```

**Fix:**

```sql
old_value IS DISTINCT FROM new_value
```

### Multiple current SCD2 rows

**Broken:** History has two rows with `is_current = true`.

**Fix:** repair and enforce the invariant.

### Incorrect validity boundaries

**Broken:** Both neighboring versions include the same timestamp.

**Fix:** Use:

```text
[valid_from, valid_to)
```

### Ignoring late-arriving events

**Broken:** Append the new row after the current version.

**Fix:** Recompute affected history.

### Creating duplicate SCD versions on replay

**Broken:** Same source event creates another historical row.

**Fix:** idempotent change detection and stable source identity.

### Partially committed history changes

**Broken:** Old row expires, new row fails.

**Fix:** atomic transaction.

---

# Part XX — Final Knowledge Check

## 89. Conceptual Questions

Answer in your own words.

1. What problem does an incremental load solve?
2. Why can a full refresh be easier but more expensive?
3. What does upsert mean?
4. Why does PostgreSQL need a uniqueness definition for `ON CONFLICT`?
5. How do business keys differ from surrogate keys?
6. What is a stable key?
7. Why can email be a dangerous identity key?
8. Why is staging a control boundary?
9. Why must the source be deduplicated before MERGE?
10. What does `EXCLUDED` mean?
11. Why use `DO NOTHING`?
12. Why is updating unchanged rows harmful?
13. Why use `IS DISTINCT FROM`?
14. What is a hard delete?
15. What is a soft delete?
16. What is a tombstone?
17. Why is a missing row not automatically a delete?
18. Define idempotency.
19. What breaks idempotency?
20. What does Type 1 preserve?
21. What does Type 2 preserve?
22. Why does SCD2 need a surrogate key?
23. What does `valid_from` mean?
24. What does `valid_to` mean?
25. Why use half-open intervals?
26. How do you detect overlap?
27. How do you detect unintended gaps?
28. What is a late-arriving change?
29. Why is a late-arriving SCD2 change a resequencing problem?
30. What is a point-in-time join?
31. Why is current-state attribution different from historical attribution?
32. Why can `LEAD()` help construct SCD2 ranges?
33. What should you measure before optimizing a large merge?
34. When might snapshots be simpler than SCD2?

---

## 90. SQL Tasks

### Task 1 — Write a PostgreSQL upsert

Given:

```text
products(product_id, product_name, price)
```

write an `ON CONFLICT` statement.

### Task 2 — Change-only update

Add NULL-safe change detection.

### Task 3 — Source dedupe

Write a `ROW_NUMBER()` CTE that keeps:

```text
latest updated_at
then highest source_priority
then highest event_id
```

### Task 4 — MERGE

Write:

```text
MATCHED → UPDATE
NOT MATCHED → INSERT
```

### Task 5 — Conditional delete

Add a delete branch driven by an explicit source delete flag.

### Task 6 — SCD2 expiration

Write the `UPDATE` that expires the current dimension version.

### Task 7 — SCD2 insertion

Write the `INSERT` that creates the new current version.

### Task 8 — Integrity assertion

Write a zero-row query that detects multiple current rows.

### Task 9 — Overlap assertion

Write a zero-row query for overlapping ranges.

### Task 10 — Point-in-time join

Write:

```sql
event_time >= valid_from
AND event_time < valid_to
```

into a fact-to-dimension join.

---

## 91. Debugging Tasks

### Task 1

A merge inserts duplicate products.

Find the source-grain problem.

### Task 2

A second run updates every row.

Find the change-detection problem.

### Task 3

SCD2 has two current rows.

Find the transaction or source-deduplication failure.

### Task 4

SCD2 has overlapping intervals.

Find the late-arrival or ordering issue.

### Task 5

Historical revenue uses today's customer segment.

Fix the join.

### Task 6

A replay creates another current history row.

Find the broken idempotency rule.

---

## 92. Architecture Tasks

For each scenario, define:

```text
target grain
source grain
business key
change rule
insert rule
update rule
delete rule
history rule
transaction boundary
idempotency
assertions
performance strategy
```

### Scenario A

Daily 10,000-row product feed.

### Scenario B

Daily 100-million-row customer snapshot.

### Scenario C

CDC with duplicate and out-of-order customer events.

### Scenario D

Customer segment must be historically accurate for all facts.

### Scenario E

Billion-row target with only 0.01% daily changes.

---

# Part XXI — Topic 10 Checkpoint

## 93. Checkpoint — Ready to Finish Module 2.6?

You should now be able to demonstrate every requirement below without relying on notes.

### 1. Write an upsert using `INSERT ... ON CONFLICT`

Demonstrate:

```sql
INSERT INTO products (...)
VALUES (...)
ON CONFLICT (product_id)
DO UPDATE
SET ...;
```

### 2. Write an upsert using `MERGE`

Demonstrate:

```sql
MERGE INTO products AS t
USING staging_products AS s
ON t.product_id = s.product_id
...
```

### 3. Explain why the source must be deduplicated before MERGE

You should be able to explain:

```text
one merge key
→ one authoritative source row
```

and prove duplicates with an assertion.

### 4. Implement SCD Type 1

Demonstrate:

```text
old value
→ overwritten current value
```

### 5. Implement SCD Type 2

Demonstrate:

```text
expire old
→ insert new
```

inside one transaction.

### 6. Write assertions for SCD2 integrity

You must have zero-row checks for:

```text
one current row
no overlaps
no unintended gaps
```

### 7. Verify one current row per business key

Use:

```sql
HAVING COUNT(*) FILTER (WHERE is_current) <> 1;
```

### 8. Detect overlapping validity ranges

Use ordered history and:

```text
valid_from < previous_valid_to
```

### 9. Detect unintended gaps

Use:

```text
valid_from <> previous_valid_to
```

when the business model requires contiguous history.

### 10. Perform a point-in-time fact-to-dimension join

Use:

```sql
event_time >= valid_from
AND event_time < valid_to
```

### 11. Explain late-arriving SCD2 corrections

You should be able to explain:

```text
late event
→ impacted history
→ resequence
→ recalculate intervals
→ validate
```

### 12. Demonstrate idempotency

Run the exact same load twice and prove:

```text
same business state
same history
same current flags
no duplicate versions
```

---

# Final Senior Data Engineer Mental Model

When you receive an incremental dataset, do not begin with:

```text
Should I use MERGE?
```

Begin with:

```text
What is one row?
        ↓
What identifies the entity?
        ↓
What does the source row mean?
        ↓
What changed?
        ↓
What is the delete contract?
        ↓
Do I need current state or history?
        ↓
How do I resolve duplicate source records?
        ↓
What transaction makes publication atomic?
        ↓
How do I make replay safe?
        ↓
How do I prove the final state is correct?
        ↓
How will this scale?
```

Then choose:

```text
ON CONFLICT
MERGE
two-step UPDATE + INSERT
SCD2
snapshot table
```

based on the actual requirements.

The professional standard is not:

> "I know how to write MERGE."

It is:

> **I can define source and target grain, establish stable row identity, deterministically reconcile inserts/updates/deletes, preserve history when required, make the load idempotent, validate the final state, and explain the operational trade-offs of the implementation.**

---

## Scope Boundary

This chapter completes Topic 10.

It intentionally does not fully re-teach:

- general joins;
- general CTEs;
- general window functions;
- general indexing;
- general transactions;
- the complete future SCD modelling theory in Module 2.8.

Those topics are prerequisites or downstream subjects. Here they are used specifically to implement and reason about incremental data loading.

### Final production principles

```text
Define grain.
Define identity.
Deduplicate deterministically.
Define insert/update/delete behavior.
Use NULL-safe comparisons.
Preserve history only when required.
Make state transitions atomic.
Make replays idempotent.
Validate with zero-row assertions.
Reconcile source and target.
Measure before optimizing.
Test pathological inputs.
```

**The goal is reliable state reconciliation, not clever SQL.**
