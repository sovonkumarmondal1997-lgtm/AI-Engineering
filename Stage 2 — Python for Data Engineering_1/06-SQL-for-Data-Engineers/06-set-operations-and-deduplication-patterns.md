# 06 — Set Operations and Deduplication Patterns

> **Stage 2 — Python for Data Engineering**  
> **Module 2.6 — SQL for Data Engineers**  
> **Topic 06 — Set Operations and Deduplication Patterns**
>
> Primary environments: **PostgreSQL 16+** and **DuckDB**

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`;
- choose between set operations based on semantics rather than habit;
- explain why set-operation columns match **by position**, not by name;
- reason about compatible data types in set operations;
- predict how duplicate rows behave;
- define what “duplicate” means at a stated business grain;
- distinguish exact duplicates, business-key duplicates, and near-duplicates;
- detect duplicates with `GROUP BY ... HAVING COUNT(*) > 1`;
- use `DISTINCT` appropriately without treating it as a universal deduplication tool;
- deduplicate with `GROUP BY` when the survivor is derived through aggregation;
- use `ROW_NUMBER()` to select a deterministic survivor;
- use PostgreSQL `DISTINCT ON`;
- use `QUALIFY` where the target engine supports it;
- define survivor rules such as latest record, source priority, and most-complete record;
- remove physical duplicate rows safely and verify the result;
- reconcile source and target tables in both directions;
- distinguish missing, extra, and changed records;
- perform partition-level reconciliation with counts, distinct keys, and measures;
- explain how `NULL` behaves in set operations;
- combine differently ordered schemas safely;
- use `NULL` placeholders for missing columns;
- use DuckDB `UNION BY NAME` where appropriate;
- reason about the cost of `UNION`, `DISTINCT`, and large-scale deduplication;
- design a production-safe deduplication pipeline.

The central engineering habit is:

> **Define the grain, define the duplicate, define the survivor, then choose the SQL pattern.**

---

## 2. Why Set Operations Matter in Data Engineering

Set operations are often introduced as a reporting feature, but Data Engineers use them heavily for correctness, ingestion, migration, reconciliation, and quality control.

Typical situations include:

```text
CRM customers
ERP customers
Support customers
       ↓
combine
       ↓
canonical customer dataset
```

or:

```text
source table
    ↓
warehouse target
    ↓
compare
    ↓
missing / extra / changed records
```

Other common uses:

- appending daily files;
- combining source systems;
- comparing staging and target tables;
- verifying backfills;
- validating migrations;
- detecting records absent from downstream systems;
- identifying target-only records;
- checking that incremental loads contain the expected rows;
- finding duplicate business keys;
- creating a golden-record dataset.

Set operations answer questions about **row sets**.

Deduplication answers a different question:

> When multiple records may represent one business entity, which record should represent that entity at the target grain?

That distinction drives the rest of this chapter.

---

## 3. The Core Mental Model

Keep these two ideas separate:

```text
SET OPERATION
"What rows exist in A, B, both, or either?"

DEDUPLICATION
"Which row should represent the business entity at the target grain?"
```

Set operations work on result sets.

Deduplication is a data-modeling and business-rule decision expressed in SQL.

### Example

Suppose:

```text
customer_id | email           | updated_at
------------+-----------------+-------------------
1           | a@example.com   | 10:00
1           | a@example.com   | 11:00
```

These are not exact duplicates because `updated_at` differs.

But if the target grain is:

```text
one row per customer_id
```

then they are business-key duplicates.

The SQL problem is not:

```text
"How do I remove identical rows?"
```

It is:

```text
"Which record should survive for customer 1?"
```

That is why this principle is central:

> **Deduplication is a business-rule and grain problem, not merely a SQL syntax problem.**

---

## 4. Set Operations vs JOINs

A `JOIN` and a set operation both combine data, but they combine it differently.

### JOIN

A join combines **columns from related rows**.

```text
A + B
   ↓
more columns
```

Example:

```sql
SELECT
    c.customer_id,
    c.email,
    o.order_id
FROM customers AS c
JOIN orders AS o
    ON o.customer_id = c.customer_id;
```

### Set operation

A set operation combines or compares **rows from compatible result sets**.

```text
A + B
   ↓
more rows
```

Example:

```sql
SELECT customer_id, email
FROM crm_customers

UNION ALL

SELECT customer_id, email
FROM erp_customers;
```

### Comparison

| Concept | JOIN | Set operation |
|---|---|---|
| Main effect | combines columns | combines/compares rows |
| Relationship mechanism | join condition | row-set semantics |
| Typical output effect | wider result | taller result |
| Main questions | “Which rows relate?” | “Which rows are in A/B/both?” |
| Common DE use | enrich facts | append/reconcile datasets |

Do not oversimplify:

```text
JOIN = columns
UNION = rows
```

is a useful first mental model, but duplicate and cardinality semantics still matter.

---

## 5. What Is a Set Operation?

Start with ordinary set intuition.

```text
A = {1, 2, 3}
B = {3, 4, 5}
```

Then:

```text
A UNION B
    = {1, 2, 3, 4, 5}

A INTERSECT B
    = {3}

A EXCEPT B
    = {1, 2}

B EXCEPT A
    = {4, 5}
```

SQL extends this idea to rows.

If the row is:

```text
(customer_id, email)
```

then the row is treated as a combined value for set-operation purposes.

### Important qualification

Do not think of a database table as a mathematical set in every operational sense.

SQL can contain duplicate rows, so constructs such as:

```sql
UNION ALL
```

explicitly preserve duplicates.

The distinction is:

```text
SQL result with duplicate rows
        vs
set-operation semantics that remove duplicates
```

---

## 6. `UNION`

`UNION` combines two compatible result sets and removes duplicate result rows.

```sql
SELECT customer_id, email
FROM crm_customers

UNION

SELECT customer_id, email
FROM erp_customers;
```

If both sources contain:

```text
1 | a@example.com
```

the duplicate result row is removed.

### What must match?

For ordinary `UNION`:

- same number of output columns;
- corresponding columns must be type-compatible;
- columns align by **position**;
- duplicate result rows are removed.

### Tiny example

```sql
SELECT 1 AS id, 'A' AS source
UNION
SELECT 1 AS id, 'A' AS source;
```

Result:

```text
id | source
---+-------
1  | A
```

Because the complete selected rows are identical.

### Production question

Before using `UNION`, ask:

> “Do I actually want duplicate elimination?”

If not, `UNION ALL` is usually the semantic choice.

---

## 7. `UNION ALL`

`UNION ALL` appends the two result sets without removing duplicates.

```sql
SELECT customer_id, email
FROM crm_customers

UNION ALL

SELECT customer_id, email
FROM erp_customers;
```

If the same row exists in both sources, both copies remain.

### Example

```sql
SELECT 1 AS id, 'A' AS source
UNION ALL
SELECT 1 AS id, 'A' AS source;
```

Result:

```text
id | source
---+-------
1  | A
1  | A
```

### Why Data Engineers use it frequently

Suppose three source systems have already been independently standardized:

```text
CRM rows
ERP rows
SUPPORT rows
```

The combination step is often:

```text
standardize
→ UNION ALL
→ normalize
→ deduplicate according to business rules
```

This separates two concerns:

```text
append everything
```

from:

```text
decide what duplicate means and which row survives
```

That separation is much safer than silently deduplicating during ingestion.

---

## 8. `UNION` vs `UNION ALL`

| Feature | `UNION` | `UNION ALL` |
|---|---|---|
| Combines rows | Yes | Yes |
| Removes duplicate result rows | Yes | No |
| Preserves duplicate rows | No | Yes |
| Requires duplicate-elimination work | Yes | No duplicate elimination |
| Good for append-only ingestion | Sometimes | Often |
| Core semantic question | “Combine and dedupe?” | “Append all rows?” |

### Correct decision logic

Use:

```text
UNION
```

when duplicate result rows should disappear.

Use:

```text
UNION ALL
```

when every input row should be preserved.

Do not choose `UNION ALL` merely because someone says it is faster.

Do not choose `UNION` merely because duplicate rows “look ugly.”

Choose the operator whose semantics match the requirement.

---

## 9. `INTERSECT`

`INTERSECT` returns rows present in both result sets.

```sql
SELECT customer_id
FROM source_a

INTERSECT

SELECT customer_id
FROM source_b;
```

Example:

```text
A = {1, 2, 3}
B = {3, 4, 5}

A INTERSECT B
= {3}
```

### Data Engineering uses

- identify common records between two systems;
- validate overlap after a migration;
- compare source populations;
- identify records present in both snapshots.

### Duplicate behavior

Plain `INTERSECT` removes duplicate result rows.

Think:

```text
A
∩
B
```

The important question is membership in both result sets.

### Optional feature

Some engines support:

```sql
INTERSECT ALL
```

with multiset-style duplicate semantics.

This is not required for the core Topic 06 skill. When using it, verify the exact support and semantics in the target engine.

---

## 10. `EXCEPT`

`EXCEPT` returns rows present in the first result set but absent from the second.

```sql
SELECT customer_id
FROM source

EXCEPT

SELECT customer_id
FROM target;
```

Read it as:

```text
source
minus
target
```

Example:

```text
A = {1,2,3}
B = {3,4,5}

A EXCEPT B
= {1,2}
```

Reverse the order:

```sql
SELECT customer_id
FROM target

EXCEPT

SELECT customer_id
FROM source;
```

Now:

```text
= {4,5}
```

This directionality is extremely important for reconciliation.

### Production interpretation

```text
source EXCEPT target
→ missing from target

target EXCEPT source
→ unexpected in target
```

---

## 11. Combining Set Operations

Multiple set operations can be composed.

For example, the conceptual expression:

```text
(A UNION B)
EXCEPT C
```

should be made explicit:

```sql
(
    SELECT ...
    FROM a

    UNION

    SELECT ...
    FROM b
)
EXCEPT
SELECT ...
FROM c;
```

Use parentheses when combining operators if there is any possibility of ambiguity.

### Engineering principle

Prefer readable set logic over compact but difficult-to-review SQL.

Ask:

```text
What is the first set?
What is the second set?
What operation combines them?
What set is produced next?
```

This mirrors the grain-first reasoning used throughout SQL.

---

## 12. Column Matching by Position

This is one of the most dangerous set-operation mistakes.

Suppose:

```text
A:
customer_id | email

B:
email       | customer_id
```

If you write:

```sql
SELECT customer_id, email
FROM A

UNION ALL

SELECT email, customer_id
FROM B;
```

the database matches:

```text
A.customer_id
        ↕
B.email

A.email
        ↕
B.customer_id
```

because set-operation columns are matched by **position**, not by name.

This can be syntactically valid and semantically disastrous.

### Correct version

```sql
SELECT
    customer_id,
    email
FROM A

UNION ALL

SELECT
    customer_id,
    email
FROM B;
```

### Production rule

Before every set operation, explicitly verify:

```text
column 1 ↔ column 1
column 2 ↔ column 2
column 3 ↔ column 3
...
```

Do not assume names will protect you.

---

## 13. Compatible Data Types

Corresponding set-operation columns also need compatible data types.

For example:

```text
INTEGER
BIGINT
VARCHAR/TEXT
DATE
TIMESTAMP
```

Some pairs may be implicitly coerced.

Others may produce errors or unexpected types depending on the engine.

### Explicit casting

When the intended common type is important, use an explicit cast:

```sql
SELECT
    customer_id::BIGINT AS customer_id,
    email
FROM source_a

UNION ALL

SELECT
    CAST(customer_id AS BIGINT) AS customer_id,
    email
FROM source_b;
```

For portable SQL, prefer standard:

```sql
CAST(customer_id AS BIGINT)
```

when practical.

### Production rule

Do not rely on implicit conversion when:

- the source types are inconsistent;
- the output schema is part of a contract;
- multiple engines are involved;
- silent type widening could affect downstream logic.

Document the intended target type at the canonical schema boundary.

---

## 14. Duplicate Semantics

The word “duplicate” is overloaded.

Set operations have one specific interpretation:

```text
UNION
→ duplicate complete result rows are removed

UNION ALL
→ duplicate complete result rows remain
```

That does **not** mean:

```text
UNION
→ one row per customer
```

unless customer identity is exactly the full selected row.

### Example

Suppose:

```text
customer_id | email          | updated_at
------------+----------------+-----------
1           | a@example.com  | 10:00
1           | a@example.com  | 11:00
```

These are not duplicate selected rows if all three columns are selected.

Therefore:

```sql
SELECT customer_id, email, updated_at
FROM customer_records
```

with `DISTINCT` still returns both rows.

The business key may still be:

```text
customer_id
```

So these are business-key duplicates.

---

## 15. How to Define a Duplicate

Always define duplicate in terms of the intended grain.

### Exact duplicate

Every selected attribute is identical.

```text
same customer_id
same email
same timestamp
same country
same ...
```

### Business-key duplicate

Multiple rows represent one business entity according to the target key.

Examples:

```text
customer_id
order_id
email
account_number
```

The non-key columns may differ.

### Near-duplicate

Records are not identical, but normalization or domain rules say they may represent the same entity.

Examples:

```text
"ABC LTD"
"ABC Ltd."
"ABC Limited"
```

or:

```text
" abc@example.com "
"ABC@EXAMPLE.COM"
```

### Duplicate definition template

Before deduplication, write:

```text
Input grain:
one row per source customer record

Target grain:
one row per customer

Duplicate definition:
same customer_id

Business key:
customer_id

Survivor rule:
latest updated_at

Tie-breaker:
highest record_id

Expected output grain:
one row per customer
```

This is more important than the SQL syntax.

---

## 16. Exact Duplicates

Consider:

```text
id | name | country
---+------+--------
1  | A    | India
1  | A    | India
2  | B    | Nepal
```

The first two rows are exact duplicates across all displayed columns.

### Detection with grouping

```sql
SELECT
    id,
    name,
    country,
    COUNT(*) AS row_count
FROM customers
GROUP BY
    id,
    name,
    country
HAVING COUNT(*) > 1;
```

### Removal with `DISTINCT`

```sql
SELECT DISTINCT
    id,
    name,
    country
FROM customers;
```

This is valid when the intended operation is specifically:

> Keep one copy of every identical complete row.

It is not a general business-key solution.

---

## 17. Business-Key Duplicates

Suppose:

```text
customer_id | email          | updated_at
------------+----------------+----------------
1           | a@example.com  | 10:00
1           | a@example.com  | 11:00
2           | b@example.com  | 12:00
```

The two records for customer `1` are business-key duplicates.

The target grain is:

```text
one row per customer_id
```

### Why `DISTINCT` is insufficient

This:

```sql
SELECT DISTINCT
    customer_id,
    email,
    updated_at
FROM customer_records;
```

still returns both records for customer `1`.

The timestamp differs.

The question is not:

```text
Which rows are exactly identical?
```

It is:

```text
Which row should survive for customer 1?
```

That requires a survivor rule.

---

## 18. Near-Duplicates

Near-duplicates are records that become equivalent after a defined normalization or business rule.

Example emails:

```text
abc@example.com
 ABC@EXAMPLE.COM
abc@example.com
```

A common introductory normalization is:

```sql
LOWER(TRIM(email))
```

Example:

```sql
SELECT
    LOWER(TRIM(email)) AS normalized_email,
    COUNT(*) AS row_count
FROM customers
GROUP BY LOWER(TRIM(email))
HAVING COUNT(*) > 1;
```

### Important caution

Normalization can create legitimate collisions.

For example, a business might not treat every text transformation as proof of identity.

Therefore:

```text
normalization rule
+
business interpretation
```

must be explicit.

This chapter does not turn near-duplicate detection into a full fuzzy entity-resolution or ML matching system.

---

## 19. Duplicate Detection with `GROUP BY`

The fundamental duplicate detector is:

```sql
SELECT
    customer_id,
    COUNT(*) AS row_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

Interpretation:

```text
GROUP BY customer_id
→ one group per customer

COUNT(*)
→ how many rows belong to that customer

HAVING COUNT(*) > 1
→ return only duplicate groups
```

### No duplicates

If the query returns zero rows:

```text
there are no duplicate customer_ids
```

under that exact definition.

### Multiple-column business key

```sql
SELECT
    customer_id,
    country,
    COUNT(*) AS row_count
FROM customers
GROUP BY
    customer_id,
    country
HAVING COUNT(*) > 1;
```

The grouping columns define what “duplicate” means.

---

## 20. `SELECT DISTINCT`

`DISTINCT` removes duplicate combinations of the selected expressions.

```sql
SELECT DISTINCT
    customer_id,
    email
FROM customers;
```

The unit being deduplicated is:

```text
(customer_id, email)
```

not just:

```text
customer_id
```

### Example

Input:

```text
customer_id | email          | updated_at
------------+----------------+-----------
1           | a@example.com  | 10:00
1           | a@example.com  | 11:00
```

This:

```sql
SELECT DISTINCT
    customer_id,
    email
FROM customer_records;
```

returns one row.

But:

```sql
SELECT DISTINCT
    customer_id,
    email,
    updated_at
FROM customer_records;
```

returns two rows.

### Core definition

> `DISTINCT` answers “which complete selected rows are identical?”

It does not answer:

> “Which record should represent this business key?”

---

## 21. GROUP BY-Based Deduplication

`GROUP BY` can produce one row per key when the survivor values can be represented through aggregate logic.

Example:

```sql
SELECT
    customer_id,
    MAX(updated_at) AS latest_updated_at
FROM customer_records
GROUP BY customer_id;
```

This creates:

```text
one row per customer_id
```

But it does not automatically return all other columns from the winning record.

### Why this matters

Suppose:

```text
customer_id | email          | updated_at
------------+----------------+-----------
1           | old@example.com| 10:00
1           | new@example.com| 11:00
```

The grouped result can tell you:

```text
customer_id = 1
latest_updated_at = 11:00
```

but it does not automatically tell you:

```text
email = new@example.com
```

unless you add another safe strategy.

That is why `ROW_NUMBER()` is often the better expression of a row-survivor rule.

---

## 22. ROW_NUMBER-Based Deduplication

Canonical pattern:

```sql
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY updated_at DESC, record_id DESC
        ) AS rn
    FROM customer_records
)
SELECT *
FROM ranked
WHERE rn = 1;
```

Read it as:

```text
partition by business key
        ↓
put desired survivor first
        ↓
assign row numbers
        ↓
keep row 1
```

### Duplicate-definition template

```text
Input grain:
one row per customer record

Target grain:
one row per customer

Duplicate definition:
same customer_id

Business key:
customer_id

Survivor rule:
latest updated_at

Tie-breaker:
highest record_id

Expected output grain:
one row per customer
```

### Why this pattern is powerful

It returns the **entire surviving row**, not just one aggregated value.

---

## 23. PostgreSQL `DISTINCT ON`

PostgreSQL provides a concise row-selection pattern:

```sql
SELECT DISTINCT ON (customer_id)
    customer_id,
    email,
    updated_at,
    record_id
FROM customer_records
ORDER BY
    customer_id,
    updated_at DESC,
    record_id DESC;
```

> **POSTGRESQL-SPECIFIC**

### How to read it

```text
DISTINCT ON (customer_id)
→ keep one row per customer_id

ORDER BY
→ define which row wins
```

The ordering is therefore part of the correctness contract.

### Why it is concise

The query expresses:

```text
one row per key
+
winning order
```

without a separate CTE.

### Portability trade-off

`DISTINCT ON` is not standard SQL.

A portable alternative is:

```sql
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY updated_at DESC, record_id DESC
        ) AS rn
    FROM customer_records
)
SELECT *
FROM ranked
WHERE rn = 1;
```

Choose the pattern based on target-engine constraints and team conventions.

---

## 24. QUALIFY-Based Deduplication

Several analytical engines support `QUALIFY`.

Example:

```sql
SELECT *
FROM customer_records
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY updated_at DESC, record_id DESC
) = 1;
```

> **DIALECT-SPECIFIC**

`QUALIFY` filters after window calculations.

It is supported by engines including DuckDB, Snowflake, BigQuery, and Databricks SQL, but support should always be verified for the exact target engine/version.

### Standard SQL alternative

```sql
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY updated_at DESC, record_id DESC
        ) AS rn
    FROM customer_records
)
SELECT *
FROM ranked
WHERE rn = 1;
```

The important concept is:

```text
calculate survivor rank
→ then filter survivor rank
```

---

## 25. Choosing the Survivor

Deduplication is incomplete until the survivor rule is explicit.

Possible rules include:

```text
latest record
highest-priority source
most complete record
trusted source
highest quality score
lowest/oldest stable identifier
```

These are not interchangeable.

### Example requirement

Suppose three sources contain:

```text
CRM
ERP
SUPPORT
```

Business rule:

```text
CRM > ERP > SUPPORT
```

Then source priority is part of the survivor definition.

The SQL must encode it.

### Example

```sql
CASE
    WHEN source_system = 'CRM' THEN 1
    WHEN source_system = 'ERP' THEN 2
    WHEN source_system = 'SUPPORT' THEN 3
    ELSE 99
END
```

Use this rule before recency when source quality is more authoritative than timestamp.

---

## 26. Deterministic Survivor Selection

A deterministic survivor rule ensures repeated runs with the same input produce the same winner.

Bad:

```sql
ORDER BY updated_at DESC
```

when duplicate timestamps are possible.

Better:

```sql
ORDER BY
    updated_at DESC,
    record_id DESC
```

### Why this matters

Determinism improves:

- rerun consistency;
- testing;
- debugging;
- reproducibility;
- audits;
- data reconciliation.

### Production habit

Write the survivor rule as a priority sequence:

```text
primary business rule
→ secondary business rule
→ deterministic tie-breaker
```

For example:

```text
source priority
→ latest updated_at
→ lowest id
```

The final tie-breaker should leave no unresolved ambiguity when business requirements demand a single survivor.

---

## 27. Latest Record Wins

A common rule is:

> Latest record wins.

Use:

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY updated_at DESC, record_id DESC
)
```

Then:

```sql
WHERE rn = 1
```

### Why `MAX(updated_at)` is not enough

This:

```sql
SELECT
    customer_id,
    MAX(updated_at)
FROM customer_records
GROUP BY customer_id;
```

returns the latest timestamp.

It does not by itself retrieve:

```text
email
phone
country
status
source
...
```

from the same record.

### Join-back danger

Suppose two rows have the same latest timestamp:

```text
customer 1 | 11:00 | record 10
customer 1 | 11:00 | record 11
```

A join-back on:

```text
customer_id + updated_at
```

can return both rows.

A deterministic window ordering avoids that ambiguity.

---

## 28. Highest-Priority Source Wins

Suppose source hierarchy is:

```text
CRM      → priority 1
ERP      → priority 2
SUPPORT  → priority 3
```

We can encode:

```sql
CASE
    WHEN source_system = 'CRM' THEN 1
    WHEN source_system = 'ERP' THEN 2
    WHEN source_system = 'SUPPORT' THEN 3
    ELSE 99
END AS source_priority
```

Then:

```sql
ROW_NUMBER() OVER (
    PARTITION BY normalized_email
    ORDER BY
        source_priority,
        updated_at DESC,
        id ASC
)
```

### Survivor hierarchy

```text
priority
    ↓
recency
    ↓
deterministic tie-breaker
```

This is a much stronger production rule than:

```text
SELECT DISTINCT ...
```

because it explains why one record survives.

---

## 29. Most Complete Record Wins

Sometimes the desired survivor is the record containing the most useful information.

Create a completeness score:

```sql
CASE WHEN email IS NOT NULL THEN 1 ELSE 0 END
+
CASE WHEN phone IS NOT NULL THEN 1 ELSE 0 END
+
CASE WHEN country IS NOT NULL THEN 1 ELSE 0 END
+
CASE WHEN address IS NOT NULL THEN 1 ELSE 0 END
AS completeness_score
```

Then:

```sql
WITH scored AS (
    SELECT
        *,
        (
            CASE WHEN email IS NOT NULL THEN 1 ELSE 0 END
          + CASE WHEN phone IS NOT NULL THEN 1 ELSE 0 END
          + CASE WHEN country IS NOT NULL THEN 1 ELSE 0 END
          + CASE WHEN address IS NOT NULL THEN 1 ELSE 0 END
        ) AS completeness_score
    FROM customer_records
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY
                completeness_score DESC,
                updated_at DESC,
                record_id DESC
        ) AS rn
    FROM scored
)
SELECT *
FROM ranked
WHERE rn = 1;
```

### Important business caveat

“Most complete” is a business rule.

A more complete record is not automatically more authoritative.

For example:

```text
trusted CRM record
```

may be preferable to:

```text
untrusted source with more filled fields
```

Define the rule intentionally.

---

## 30. Tie-Breaker Rules

Tie-breakers should resolve the final ambiguity.

Typical choices:

```text
lowest stable id
highest stable id
source event sequence
ingestion sequence
trusted version number
```

Example:

```sql
ORDER BY
    updated_at DESC,
    record_id ASC
```

This means:

```text
latest timestamp wins
if tied → lowest record_id wins
```

### Avoid arbitrary ordering

Do not rely on:

```text
table storage order
physical row order
current execution plan
```

as a business rule.

A deterministic tie-breaker should be explicit in the SQL.

---

## 31. Exact vs Business-Key vs Near-Duplicate Deduplication

| Duplicate type | Definition | Typical strategy |
|---|---|---|
| Exact | every selected value is the same | `DISTINCT`, grouped exact-row detection |
| Business-key | same logical entity key | `ROW_NUMBER`, `DISTINCT ON`, `QUALIFY` |
| Near-duplicate | equivalent after normalization/rules | normalized key + explicit survivor rules |

### Key lesson

These are different problems.

```text
Exact
→ remove repeated identical rows

Business-key
→ select one representative record

Near-duplicate
→ first establish the identity rule
→ then select survivor
```

Do not use one technique as a universal replacement for the others.

---

## 32. Safe In-Place Duplicate Deletion

Physical duplicate deletion is much more dangerous than producing a deduplicated result.

The safe sequence is:

```text
1. define survivor
2. preview rows to delete
3. verify the preview
4. execute in a controlled transaction
5. validate uniqueness
6. commit only when satisfied
```

### PostgreSQL example using `ctid`

> **POSTGRESQL-SPECIFIC**

Suppose a table contains exact duplicate business records and has no usable stable key for the cleanup.

Preview:

```sql
WITH ranked AS (
    SELECT
        ctid,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id, email, country
            ORDER BY ctid
        ) AS rn
    FROM customers
)
SELECT *
FROM ranked
WHERE rn > 1;
```

`ctid` is a PostgreSQL physical tuple identifier.

It is useful for controlled cleanup of the current physical rows, but it is **not** a business identifier and should not be used as a permanent identity key.

### Delete inside a transaction

```sql
BEGIN;

WITH ranked AS (
    SELECT
        ctid,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id, email, country
            ORDER BY ctid
        ) AS rn
    FROM customers
)
DELETE FROM customers AS c
USING ranked AS r
WHERE c.ctid = r.ctid
  AND r.rn > 1;

-- Re-check before committing.
SELECT
    customer_id,
    email,
    country,
    COUNT(*) AS row_count
FROM customers
GROUP BY
    customer_id,
    email,
    country
HAVING COUNT(*) > 1;

ROLLBACK;
```

During practice, `ROLLBACK` lets you inspect the behavior without committing the deletion.

For a real production cleanup:

- prefer a stable primary key if one exists;
- preview the target rows;
- test on an isolated copy first;
- perform controlled cleanup during an appropriate operational window;
- validate downstream impact;
- commit only after verification.

### Upstream lesson

Physical deletion is not a substitute for fixing the source or pipeline that created the duplicates.

---

## 33. Reconciliation Fundamentals

Reconciliation asks:

> Does the target contain the records and values the source says it should contain?

Typical source/target questions:

```text
What is missing from target?

What is extra in target?

What changed?

Do counts match?

Do distinct business-key counts match?

Do amounts match?

Do partition-level counts match?
```

### Three record-level dimensions

```text
1. Missing
2. Extra
3. Changed
```

You need all three for a meaningful comparison.

### Important warning

Global totals are not sufficient proof of equality.

Two incorrect datasets can still have:

```text
same row count
same sum
```

while containing different records.

---

## 34. `EXCEPT` in Both Directions

Use source-minus-target:

```sql
SELECT customer_id
FROM source_customers

EXCEPT

SELECT customer_id
FROM target_customers;
```

Interpretation:

```text
source records absent from target
```

Now reverse it:

```sql
SELECT customer_id
FROM target_customers

EXCEPT

SELECT customer_id
FROM source_customers;
```

Interpretation:

```text
target records absent from source
```

### Why both directions matter

Checking only:

```text
source EXCEPT target
```

can miss unexpected target-only rows.

Checking only:

```text
target EXCEPT source
```

can miss missing source rows.

A complete reconciliation needs both.

---

## 35. Missing Rows

A source-minus-target comparison identifies rows expected by the source but not present in the target.

Example:

```sql
SELECT
    customer_id
FROM source_customers

EXCEPT

SELECT
    customer_id
FROM target_customers;
```

If the result is:

```text
101
104
108
```

then those keys exist in source and are absent from target.

### Assertion form

```sql
SELECT *
FROM (
    SELECT customer_id
    FROM source_customers

    EXCEPT

    SELECT customer_id
    FROM target_customers
) AS missing;
```

Expected result in a healthy fully replicated population:

```text
zero rows
```

---

## 36. Extra Rows

Now compare target minus source:

```sql
SELECT
    customer_id
FROM target_customers

EXCEPT

SELECT
    customer_id
FROM source_customers;
```

If this returns:

```text
900
901
```

those records exist in target but not source under the selected-row definition.

Possible explanations include:

- legitimate target enrichment;
- late source arrival;
- source deletion;
- stale target record;
- incorrect ingestion;
- different business populations.

Do not automatically classify every target-only row as an error. First confirm the reconciliation contract.

---

## 37. Changed Rows

A changed business-key record is not necessarily found by comparing only keys.

Suppose:

```text
Source:
customer_id | email          | status
------------+----------------+--------
1           | a@example.com  | active

Target:
customer_id | email          | status
------------+----------------+--------
1           | a@example.com  | inactive
```

Key comparison says:

```text
same customer exists
```

But the attributes differ.

### Full-row `EXCEPT`

If both tables have the same projected schema:

```sql
SELECT
    customer_id,
    email,
    status
FROM source_customers

EXCEPT

SELECT
    customer_id,
    email,
    status
FROM target_customers;
```

and the reverse:

```sql
SELECT
    customer_id,
    email,
    status
FROM target_customers

EXCEPT

SELECT
    customer_id,
    email,
    status
FROM source_customers;
```

can reveal that the row sets differ.

### Explaining the change

To explain which attribute changed, a key-based comparison is often more useful:

```sql
SELECT
    s.customer_id,
    s.email AS source_email,
    t.email AS target_email,
    s.status AS source_status,
    t.status AS target_status
FROM source_customers AS s
JOIN target_customers AS t
    ON t.customer_id = s.customer_id
WHERE s.email IS DISTINCT FROM t.email
   OR s.status IS DISTINCT FROM t.status;
```

PostgreSQL and DuckDB support `IS DISTINCT FROM`; verify exact portability when targeting another engine.

---

## 38. Partition-Level Reconciliation

Global comparison can tell you that something is wrong.

Partition-level comparison helps tell you **where**.

Example:

```sql
SELECT
    DATE_TRUNC('day', created_at) AS day,
    COUNT(*) AS row_count,
    COUNT(DISTINCT customer_id) AS distinct_customers,
    SUM(amount) AS total_amount
FROM source_orders
GROUP BY 1;
```

Run the equivalent against target.

### Useful partition-level metrics

```text
row count
distinct business-key count
sum of numeric measures
minimum timestamp
maximum timestamp
```

### Why it helps

Suppose global values are:

```text
source rows = 100,000
target rows = 100,000
```

but:

```text
2026-09-25:
source = 50,000
target = 49,000

2026-09-26:
source = 50,000
target = 51,000
```

Global equality hides a day-level redistribution problem.

Partition checks localize the discrepancy.

---

## 39. NULLs in Set Operations

This is a subtle but important distinction.

In ordinary SQL comparison:

```sql
NULL = NULL
```

does **not** evaluate to `TRUE`.

It evaluates to `UNKNOWN`.

However, set operations use row/set semantics for duplicate elimination and row matching in which `NULL` values can be treated as equal for these purposes.

### Example

Suppose:

```text
A:
1
NULL

B:
1
NULL
2
```

Then:

```sql
SELECT value
FROM a

INTERSECT

SELECT value
FROM b;
```

can produce:

```text
1
NULL
```

The `NULL` is considered part of the common row value under set-operation semantics.

### Important mental model

```text
ordinary comparison:
NULL = NULL
→ UNKNOWN

set operation:
NULL values can match for set semantics
→ NULL can participate in INTERSECT / EXCEPT / duplicate elimination
```

Do not say:

> “NULL equals NULL in SQL.”

That is incorrect for ordinary `=`.

---

## 40. Why NULL Behaves Differently from `=`

The apparent contradiction disappears once you distinguish the operation.

### Ordinary comparison

```sql
SELECT
    CASE
        WHEN NULL = NULL THEN 'equal'
        ELSE 'not true'
    END;
```

The predicate is not `TRUE`.

### Set operation

A set operation asks about row membership and duplicate semantics rather than performing the ordinary `=` predicate for each column.

That is why:

```sql
SELECT NULL AS value

INTERSECT

SELECT NULL AS value;
```

can return the `NULL` row.

### Production implication

When writing reconciliation logic, do not casually replace set operations with chains of ordinary equality predicates without thinking about `NULL` semantics.

If you must compare nullable attributes directly, a NULL-safe comparator such as:

```sql
source_value IS DISTINCT FROM target_value
```

can be useful in PostgreSQL and DuckDB.

---

## 41. Combining Different Schemas

A common ingestion problem is:

```text
CRM:
customer_id
email
country

ERP:
customer_id
country
email
```

Do not write:

```sql
SELECT *
FROM crm

UNION ALL

SELECT *
FROM erp;
```

The columns are in a different order.

### Correct approach

Explicitly project the intended canonical order:

```sql
SELECT
    customer_id,
    email,
    country
FROM crm

UNION ALL

SELECT
    customer_id,
    email,
    country
FROM erp;
```

### Production lesson

The canonical schema should be explicit at the boundary.

Do not depend on `SELECT *` in a multi-source set operation.

---

## 42. Explicit Column Lists and NULL Placeholders

Suppose source A has:

```text
customer_id
email
country
```

and source B has:

```text
customer_id
email
```

Use a `NULL` placeholder:

```sql
SELECT
    customer_id,
    email,
    country
FROM source_a

UNION ALL

SELECT
    customer_id,
    email,
    NULL AS country
FROM source_b;
```

### Why the placeholder matters

It preserves the canonical output schema:

```text
customer_id | email | country
```

even though source B cannot provide country.

### Semantic caution

`NULL` means:

```text
value unavailable / unknown / not supplied
```

unless your data contract defines a different meaning.

Do not silently replace a missing field with:

```text
''
0
'UNKNOWN'
```

unless those values have explicit semantic meaning.

---

## 43. DuckDB `UNION BY NAME`

DuckDB provides a convenient extension:

```text
UNION BY NAME
```

> **DUCKDB-SPECIFIC**

Instead of matching output columns solely by position, DuckDB can align them by column name.

Representative shape:

```sql
SELECT
    customer_id,
    email,
    country
FROM crm

UNION ALL BY NAME

SELECT
    country,
    customer_id,
    email
FROM erp;
```

Conceptually:

```text
match:
customer_id → customer_id
email       → email
country     → country
```

rather than:

```text
first column ↔ first column
second ↔ second
third ↔ third
```

### Why this is useful

It can reduce a class of column-order errors when combining evolving schemas.

### What it does not solve

It does not eliminate the need for:

- schema governance;
- correct column names;
- compatible types;
- intentional handling of missing columns;
- business-level validation.

A schema can be wrong by name too.

### Version note

DuckDB syntax and behavior can evolve. Verify the exact installed DuckDB version before making `UNION BY NAME` part of a production contract.

---

## 44. Performance of `UNION`

The key semantic difference is duplicate elimination.

```text
UNION ALL
→ append/concatenate semantics

UNION
→ combine
→ identify duplicate result rows
→ remove duplicates
```

Duplicate elimination may involve physical work such as:

```text
sorting
or
hashing
```

but the exact execution strategy is engine-dependent.

### Practical implication

If you know all rows should be preserved:

```sql
UNION ALL
```

avoids the need for duplicate elimination.

If you need deduplication:

```sql
UNION
```

may be correct, but you should understand that the deduplication work has a cost.

Do not make the simplistic claim:

> “UNION is slow.”

The correct statement is:

> `UNION` requires additional duplicate-elimination work that `UNION ALL` does not.

---

## 45. Performance of `DISTINCT`

`DISTINCT` also needs to identify duplicate rows.

Conceptually:

```text
input rows
    ↓
identify identical selected-row values
    ↓
retain unique rows
```

An engine may use:

```text
sorting
or
hash-based grouping
```

depending on the query and optimizer.

### Cost drivers

- row count;
- number of selected columns;
- row width;
- number of distinct values;
- available memory;
- intermediate result size;
- need to spill to disk.

A `DISTINCT` over:

```text
1 billion rows
+
50 wide columns
```

is a different operational problem from:

```text
10,000 narrow rows
+
2 columns
```

### Production lesson

Never use `DISTINCT` as a free cleanup step in a large pipeline.

First determine whether it is semantically required.

---

## 46. Deduplication Performance Intuition

A useful mental model is:

```text
more rows
+
wider rows
+
more candidate groups
+
more expensive survivor rules
=
more work
```

### Safe reduction

If filtering rows is logically safe, reduce the data before deduplication:

```text
raw data
→ filter to relevant records
→ project required columns
→ normalize
→ deduplicate
```

But be careful.

Filtering can change the duplicate population.

For example, if the business rule is:

> choose the latest record across all source events

then filtering out older records may be safe only if you have a proven equivalent condition.

### Large-scale question

Ask:

```text
Can I reduce rows safely before deduplication?

Can I reduce columns safely?

Can I deduplicate closer to the source?

Can I partition the workload?

Can I enforce uniqueness upstream so fewer duplicates reach this stage?
```

Do not optimize before defining correctness.

---

## 47. Production Deduplication Pipeline

A robust golden-record pipeline can look like:

```text
raw source
    ↓
standardize columns
    ↓
UNION ALL
    ↓
normalize business keys
    ↓
detect duplicate groups
    ↓
score/rank candidates
    ↓
choose deterministic survivor
    ↓
validate uniqueness
    ↓
publish golden dataset
```

For each stage, document:

```text
Input grain:
Transformation:
Output grain:
Business rule:
Validation:
```

### Example

#### Stage 1 — Standardize

```text
Input grain:
one row per raw source record

Transformation:
align column names/types/order

Output grain:
one row per raw source record

Validation:
compatible canonical schema
```

#### Stage 2 — Append

```sql
source_a
UNION ALL
source_b
UNION ALL
source_c
```

```text
Business rule:
preserve every source row before deduplication
```

#### Stage 3 — Normalize

```sql
LOWER(TRIM(email))
```

```text
Business rule:
email identity ignores surrounding whitespace/case
```

Only do this if the business contract supports it.

#### Stage 4 — Rank

```text
source priority
→ recency
→ deterministic id
```

#### Stage 5 — Publish

```text
rn = 1
```

#### Stage 6 — Validate

```sql
SELECT normalized_email
FROM golden_customers
GROUP BY normalized_email
HAVING COUNT(*) > 1;
```

Expected:

```text
zero rows
```

---

## 48. Debugging Deduplication

When duplicate counts are unexpectedly high:

### 1. Define the intended grain

Example:

```text
one row per normalized email
```

### 2. Define the business key

```text
normalized_email
```

### 3. Count duplicate groups

```sql
SELECT
    normalized_email,
    COUNT(*) AS row_count
FROM candidates
GROUP BY normalized_email
HAVING COUNT(*) > 1;
```

### 4. Inspect real duplicate examples

```sql
SELECT *
FROM candidates
WHERE normalized_email IN (
    SELECT normalized_email
    FROM candidates
    GROUP BY normalized_email
    HAVING COUNT(*) > 1
)
ORDER BY normalized_email, updated_at DESC;
```

### 5. Compare exact and business-key duplicates

A key-level duplicate does not necessarily mean a full-row duplicate.

### 6. Inspect source distribution

```text
CRM
ERP
SUPPORT
```

may have different quality or authority.

### 7. Inspect timestamps

Look for ties, future dates, null dates, or unexpected ingestion times.

### 8. Check normalization

A new normalization rule can collapse records that were previously distinct.

### 9. Verify survivor logic

Does the ordering really encode the business requirement?

### 10. Verify deterministic tie-breaking

No unresolved ties should remain when exactly one survivor is required.

### 11. Re-run the pipeline

Compare the output against the predicted grain.

### 12. Assert uniqueness

```sql
SELECT business_key
FROM golden_table
GROUP BY business_key
HAVING COUNT(*) > 1;
```

Expected:

```text
zero rows
```

---

## 49. Assertion Queries

Assertions should return zero rows when the invariant is satisfied.

### No duplicate business keys

```sql
SELECT
    customer_id
FROM golden_customers
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

Expected:

```text
zero rows
```

### Source minus target should be empty

```sql
SELECT *
FROM (
    SELECT
        customer_id,
        email,
        country
    FROM source_customers

    EXCEPT

    SELECT
        customer_id,
        email,
        country
    FROM target_customers
) AS missing;
```

Expected:

```text
zero rows
```

### Target minus source should be empty

```sql
SELECT *
FROM (
    SELECT
        customer_id,
        email,
        country
    FROM target_customers

    EXCEPT

    SELECT
        customer_id,
        email,
        country
    FROM source_customers
) AS extra;
```

Expected:

```text
zero rows
```

### Partition count assertion

Suppose you have a reconciled comparison table:

```sql
SELECT *
FROM reconciliation
WHERE source_row_count <> target_row_count;
```

Expected:

```text
zero rows
```

### Partition amount assertion

```sql
SELECT *
FROM reconciliation
WHERE source_total_amount IS DISTINCT FROM target_total_amount;
```

Expected:

```text
zero rows
```

Use tolerance rules where floating-point measures require them rather than blindly demanding binary equality.

---

## 50. Common Mistakes

### Mistake 1 — Using `UNION` when `UNION ALL` is required

**Broken:**

```sql
SELECT *
FROM daily_file_1

UNION

SELECT *
FROM daily_file_2;
```

**Why:** Legitimate repeated rows disappear.

**Correct:** Use `UNION ALL` when all rows are part of the intended population.

**Engineering lesson:** Do not deduplicate before you define whether duplicates are actually invalid.

---

### Mistake 2 — Using `UNION ALL` when duplicates must disappear

**Broken:**

```sql
source_a
UNION ALL
source_b
```

when the requirement is exact unique-row reconciliation.

**Why:** Duplicates remain.

**Correct:** Use `UNION` or an explicit deduplication strategy.

---

### Mistake 3 — Wrong column order

**Broken:**

```sql
SELECT customer_id, email FROM a
UNION ALL
SELECT email, customer_id FROM b;
```

**Why:** Position, not name, controls alignment.

**Correct:**

```sql
SELECT customer_id, email FROM a
UNION ALL
SELECT customer_id, email FROM b;
```

---

### Mistake 4 — Incompatible types

**Broken idea:**

```text
customer_id as INTEGER in A
customer_id as unrelated text format in B
```

**Why:** Implicit coercion may fail or produce an unintended common type.

**Correct:** Cast explicitly when the contract requires it.

---

### Mistake 5 — Treating `DISTINCT` as business-key deduplication

**Broken:**

```sql
SELECT DISTINCT *
FROM customer_records;
```

**Why:** Different versions remain.

**Correct:** Use a business-key survivor strategy.

---

### Mistake 6 — Using `DISTINCT` to hide a grain problem

**Broken pattern:**

```text
bad join
→ duplicate rows
→ DISTINCT
```

**Why:** It may hide the cause and remove legitimate records.

**Correct:** Investigate the intended grain and upstream cardinality first.

---

### Mistake 7 — Losing survivor attributes with `GROUP BY`

**Broken:**

```sql
SELECT
    customer_id,
    MAX(updated_at)
FROM customer_records
GROUP BY customer_id;
```

**Why:** Other columns from the winning row are not automatically returned.

**Correct:** Use a row-survivor pattern such as `ROW_NUMBER()` when you need the complete record.

---

### Mistake 8 — `MAX(timestamp)` without safe survivor selection

**Why:** Timestamps can tie.

**Correct:** Define a deterministic secondary key.

---

### Mistake 9 — Missing deterministic tie-breakers

**Broken:**

```sql
ORDER BY updated_at DESC
```

**Correct:**

```sql
ORDER BY updated_at DESC, record_id ASC
```

---

### Mistake 10 — Confusing exact and business-key duplicates

**Why:** Two records can differ in attributes and still represent the same entity.

**Correct:** State the target grain.

---

### Mistake 11 — Silent normalization

**Broken:**

```sql
LOWER(TRIM(email))
```

introduced without a data contract.

**Why:** It can create unintended identity collisions.

**Correct:** Treat normalization as a business rule.

---

### Mistake 12 — Deleting before defining a survivor

**Why:** You can remove the wrong record.

**Correct:**

```text
define survivor
→ preview delete set
→ validate
→ delete
```

---

### Mistake 13 — Using physical identifiers as business identifiers

**Why:** `ctid` is PostgreSQL physical metadata, not a durable business key.

**Correct:** Use a stable primary key for durable identity.

---

### Mistake 14 — Reconciliation in only one direction

**Why:** You can detect missing rows but miss extra rows, or vice versa.

**Correct:** Check both directions.

---

### Mistake 15 — Ignoring `NULL` set semantics

**Why:** `NULL` behaves differently in ordinary equality and set comparison semantics.

**Correct:** Demonstrate the exact operation being used.

---

### Mistake 16 — Global totals treated as proof of equality

**Why:** Different record sets can have identical totals.

**Correct:** Combine:

```text
record comparison
+
partition counts
+
distinct keys
+
measure reconciliation
```

---

### Mistake 17 — `UNION BY NAME` without schema governance

**Why:** Matching names cannot prove that the names themselves are correct.

**Correct:** Maintain an explicit canonical schema contract.

---

### Mistake 18 — Assuming `UNION` and `UNION ALL` have identical cost

**Why:** `UNION` must perform duplicate elimination.

**Correct:** Understand the semantic and physical differences.

---

### Mistake 19 — Assuming `DISTINCT` is cheap

**Why:** Large, wide datasets can make duplicate elimination expensive.

**Correct:** Estimate the data size and measure later with execution plans.

---

### Mistake 20 — Deduplicating after unnecessary expansion

**Why:** Joins or transformations may multiply rows first.

**Correct:** Control grain before large-scale deduplication where logically possible.

---

## 51. Beginner Practice

### Exercise 1 — Simple `UNION`

**Objective:** Understand duplicate removal.

**Sample data:**

```text
A = 1, 2, 3
B = 3, 4, 5
```

**Task:** Write `UNION` and predict the output.

**Expected reasoning:**

```text
1, 2, 3, 4, 5
```

**Solution:**

```sql
SELECT value
FROM (
    VALUES (1), (2), (3)
) AS a(value)

UNION

SELECT value
FROM (
    VALUES (3), (4), (5)
) AS b(value);
```

**Explanation:** The duplicate `3` is removed.

---

### Exercise 2 — `UNION ALL`

**Objective:** Preserve duplicates.

**Task:** Rewrite Exercise 1 with `UNION ALL`.

**Solution:**

```sql
SELECT value
FROM (
    VALUES (1), (2), (3)
) AS a(value)

UNION ALL

SELECT value
FROM (
    VALUES (3), (4), (5)
) AS b(value);
```

**Expected reasoning:** `3` appears twice.

---

### Exercise 3 — `INTERSECT`

**Task:** Find common values.

**Solution:**

```sql
SELECT value
FROM (
    VALUES (1), (2), (3)
) AS a(value)

INTERSECT

SELECT value
FROM (
    VALUES (3), (4), (5)
) AS b(value);
```

Expected:

```text
3
```

---

### Exercise 4 — `EXCEPT`

**Task:** Find values in A but not B.

**Solution:**

```sql
SELECT value
FROM (
    VALUES (1), (2), (3)
) AS a(value)

EXCEPT

SELECT value
FROM (
    VALUES (3), (4), (5)
) AS b(value);
```

Expected:

```text
1
2
```

---

### Exercise 5 — Position matching

**Sample schemas:**

```text
source_a:
customer_id | email

source_b:
email | customer_id
```

**Task:** Write a correct `UNION ALL`.

**Expected reasoning:** Explicitly select:

```text
customer_id, email
```

from both.

**Solution:**

```sql
SELECT customer_id, email
FROM source_a

UNION ALL

SELECT customer_id, email
FROM source_b;
```

---

### Exercise 6 — Compatible types

**Task:** Combine an integer customer ID with a bigint customer ID.

**Solution:**

```sql
SELECT CAST(customer_id AS BIGINT) AS customer_id
FROM source_a

UNION ALL

SELECT customer_id
FROM source_b;
```

Document the canonical output type.

---

### Exercise 7 — Exact duplicates

**Objective:** Detect identical rows.

**Solution:**

```sql
SELECT
    customer_id,
    email,
    country,
    COUNT(*) AS row_count
FROM customers
GROUP BY
    customer_id,
    email,
    country
HAVING COUNT(*) > 1;
```

---

### Exercise 8 — `DISTINCT`

**Task:** Remove exact duplicates from selected columns.

**Solution:**

```sql
SELECT DISTINCT
    customer_id,
    email,
    country
FROM customers;
```

Explain why this does not automatically produce one row per customer if other selected values differ.

---

### Exercise 9 — Business-key duplicate detection

**Task:** Find duplicate `customer_id` values.

**Solution:**

```sql
SELECT
    customer_id,
    COUNT(*) AS row_count
FROM customer_records
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

---

### Exercise 10 — Basic `GROUP BY` dedupe

**Task:** Return one row per customer with latest timestamp.

**Solution:**

```sql
SELECT
    customer_id,
    MAX(updated_at) AS latest_updated_at
FROM customer_records
GROUP BY customer_id;
```

**Explanation:** This gives a key-level summary, not necessarily the full winning record.

---

## 52. Intermediate Practice

### Exercise 1 — Business-key deduplication

**Objective:** One row per customer.

**Input grain:**

```text
one row per customer record
```

**Target grain:**

```text
one row per customer_id
```

**Duplicate definition:**

```text
same customer_id
```

**Survivor rule:**

```text
latest updated_at
```

**Tie-breaker:**

```text
highest record_id
```

**Solution:**

```sql
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY updated_at DESC, record_id DESC
        ) AS rn
    FROM customer_records
)
SELECT *
FROM ranked
WHERE rn = 1;
```

---

### Exercise 2 — Source priority

**Objective:** Prefer CRM over ERP.

**Ordering:**

```sql
CASE
    WHEN source_system = 'CRM' THEN 1
    WHEN source_system = 'ERP' THEN 2
    ELSE 99
END
```

Then add:

```text
updated_at DESC
record_id ASC
```

and explain why all three levels are necessary.

---

### Exercise 3 — Completeness score

Create a score from:

```text
email
phone
country
```

Then select the most complete record.

**Solution shape:**

```sql
WITH scored AS (
    SELECT
        *,
        (
            CASE WHEN email IS NOT NULL THEN 1 ELSE 0 END
          + CASE WHEN phone IS NOT NULL THEN 1 ELSE 0 END
          + CASE WHEN country IS NOT NULL THEN 1 ELSE 0 END
        ) AS completeness_score
    FROM customer_records
)
SELECT *
FROM scored
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY completeness_score DESC, updated_at DESC, record_id ASC
) = 1;
```

For PostgreSQL portability, replace `QUALIFY` with a CTE and outer filter.

---

### Exercise 4 — PostgreSQL `DISTINCT ON`

Solve the latest-record problem using:

```sql
DISTINCT ON (customer_id)
```

and compare the query with the `ROW_NUMBER()` version.

---

### Exercise 5 — DuckDB `QUALIFY`

Rewrite a deduplication query with:

```sql
QUALIFY ROW_NUMBER() OVER (...) = 1
```

Clearly label the syntax as dialect-specific.

---

### Exercise 6 — Normalized business key

Use:

```sql
LOWER(TRIM(email))
```

to identify collisions.

Then inspect the rows that collide after normalization.

---

### Exercise 7 — Tie case

Create two rows with identical:

```text
updated_at
```

for the same customer.

Prove that:

```sql
ORDER BY updated_at DESC
```

does not encode a complete survivor rule.

Add:

```sql
ORDER BY updated_at DESC, record_id ASC
```

and explain the deterministic result.

---

### Exercise 8 — Reconciliation missing rows

Calculate:

```text
source EXCEPT target
```

Interpret the result.

---

### Exercise 9 — Reconciliation extra rows

Calculate:

```text
target EXCEPT source
```

Interpret the result.

---

### Exercise 10 — Partition reconciliation

Compare:

```text
daily count
daily distinct key count
daily amount sum
```

between source and target.

Explain what each check can and cannot prove.

---

## 53. Advanced Practice

### Exercise 1 — Exact source/target equality

Project identical schemas and compare:

```text
source EXCEPT target
target EXCEPT source
```

Predict the expected result for equal datasets.

---

### Exercise 2 — False confidence

Construct two datasets with:

```text
same row count
same SUM(amount)
```

but different records.

Use `EXCEPT` to prove that aggregate equality does not imply record equality.

---

### Exercise 3 — Changed rows

Find business keys that exist in both source and target but have changed attributes.

Use:

```sql
IS DISTINCT FROM
```

for nullable attributes.

---

### Exercise 4 — Bidirectional reconciliation

Build one report containing:

```text
missing_count
extra_count
changed_count
source_count
target_count
```

Define each metric carefully.

---

### Exercise 5 — Partition-level reconciliation

Compare source and target by day and identify the first partition whose:

```text
row_count
distinct_key_count
total_amount
```

differs.

---

### Exercise 6 — NULL set semantics

Construct:

```text
A:
1
NULL

B:
1
NULL
2
```

Test all three:

```text
UNION
INTERSECT
EXCEPT
```

Explain the results.

---

### Exercise 7 — Schema evolution

Source A has:

```text
id
email
country
```

Source B has:

```text
id
email
```

Combine them with explicit `NULL AS country`.

Then state what a downstream consumer should interpret the NULL as.

---

### Exercise 8 — `UNION BY NAME`

In DuckDB, combine the same data with different column order.

Explain why the feature reduces one particular category of bug but does not replace schema governance.

---

### Exercise 9 — Physical duplicate cleanup

In PostgreSQL:

1. create duplicate rows in an inline `VALUES`-based practice table;
2. preview survivors and delete candidates;
3. use a transaction;
4. validate post-delete uniqueness;
5. roll back during practice.

State why `ctid` should not be treated as business identity.

---

### Exercise 10 — Large-scale dedup strategy

Given:

```text
500 million raw customer records
```

and a requirement:

```text
one row per normalized email
```

design the logical pipeline:

```text
standardize
→ filter
→ normalize
→ detect
→ rank
→ survivor
→ validate
```

For each step state:

```text
grain
business rule
validation
```

Then identify which operations may require substantial sort/hash work.

---

### Exercise 11 — Production reconciliation with nullable attributes

Compare source and target customer records where:

```text
phone can be NULL
country can be NULL
```

Use row-set comparison and attribute-level comparison without treating ordinary `=` as NULL-safe.

---

## 54. Debugging Challenges

### Challenge 1 — UNION accidentally swaps columns

**Symptom:** Emails appear in the customer-ID column.

**Broken SQL:**

```sql
SELECT customer_id, email
FROM crm

UNION ALL

SELECT email, customer_id
FROM erp;
```

**Investigation:**

1. inspect the select lists;
2. compare output positions;
3. ignore column names temporarily;
4. map position 1 to position 1.

**Root cause:** Set operations match by position.

**Corrected SQL:**

```sql
SELECT customer_id, email
FROM crm

UNION ALL

SELECT customer_id, email
FROM erp;
```

**Production lesson:** Never rely on `SELECT *` for evolving multi-source unions.

---

### Challenge 2 — UNION removes valid duplicate rows

**Symptom:** A record appears fewer times than expected after combining daily data.

**Broken SQL:**

```sql
SELECT *
FROM file_2026_09_27

UNION

SELECT *
FROM file_2026_09_28;
```

**Root cause:** `UNION` removes duplicate result rows.

**Corrected approach:**

```sql
SELECT *
FROM file_2026_09_27

UNION ALL

SELECT *
FROM file_2026_09_28;
```

if duplicates are legitimate across files.

**Production lesson:** Duplicate removal is a semantic choice.

---

### Challenge 3 — DISTINCT fails to create one row per customer

**Symptom:** Multiple records remain for the same customer.

**Broken SQL:**

```sql
SELECT DISTINCT
    customer_id,
    email,
    updated_at
FROM customer_records;
```

**Root cause:** `updated_at` differs.

**Corrected approach:** Use a business-key survivor rule.

---

### Challenge 4 — GROUP BY loses the winning email

**Symptom:** You know the latest timestamp but cannot safely return the corresponding email.

**Broken SQL:**

```sql
SELECT
    customer_id,
    MAX(updated_at) AS latest_updated_at
FROM customer_records
GROUP BY customer_id;
```

**Root cause:** Aggregation returns a summary, not the complete winning row.

**Corrected approach:**

```sql
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY updated_at DESC, record_id DESC
        ) AS rn
    FROM customer_records
)
SELECT *
FROM ranked
WHERE rn = 1;
```

**Production lesson:** Derive a row survivor when you need row attributes.

---

### Challenge 5 — Nondeterministic survivor

**Symptom:** Different records can survive across executions.

**Broken:**

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY updated_at DESC
)
```

**Root cause:** Timestamp ties.

**Corrected:**

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY updated_at DESC, record_id ASC
)
```

**Production lesson:** Tie-breakers are part of the business rule.

---

### Challenge 6 — Reversed source priority

**Symptom:** SUPPORT records win over CRM even though CRM should be authoritative.

**Broken:**

```sql
ORDER BY
    CASE
        WHEN source_system = 'SUPPORT' THEN 1
        WHEN source_system = 'CRM' THEN 2
        WHEN source_system = 'ERP' THEN 3
    END
```

**Root cause:** Priority mapping is reversed.

**Corrected approach:**

```sql
ORDER BY
    CASE
        WHEN source_system = 'CRM' THEN 1
        WHEN source_system = 'ERP' THEN 2
        WHEN source_system = 'SUPPORT' THEN 3
        ELSE 99
    END
```

**Production lesson:** Encode the business hierarchy visibly.

---

### Challenge 7 — Normalization collision

**Symptom:** Two customers collapse to one normalized email.

**Broken assumption:**

```sql
LOWER(TRIM(email))
```

is treated as proof of identity.

**Root cause:** Normalization changed the comparison space, but the business identity rule was not reviewed.

**Corrected approach:** Inspect collisions, define whether the normalized field is a valid business key, and apply additional survivor criteria where necessary.

---

### Challenge 8 — One-direction reconciliation

**Symptom:** “No missing source rows” is reported, but target still contains unexpected records.

**Broken approach:**

```text
source EXCEPT target
```

only.

**Corrected approach:**

```text
source EXCEPT target
target EXCEPT source
```

**Production lesson:** Reconciliation is bidirectional.

---

### Challenge 9 — Global totals match

**Symptom:** Row counts and total amounts match, but records are wrong.

**Root cause:** Aggregates can cancel out.

**Corrected approach:**

```text
row set comparison
+
partition checks
+
distinct key comparison
+
measure checks
```

**Production lesson:** Equal totals are evidence, not proof of equality.

---

### Challenge 10 — Physical deletion removes the wrong survivor

**Symptom:** A duplicate cleanup leaves the less-preferred record.

**Investigation:**

1. inspect survivor ordering;
2. preview `rn = 1` and `rn > 1`;
3. verify tie-breakers;
4. inspect deletion join condition;
5. run inside a transaction.

**Root cause:** Survivor rule was not defined or deletion targeted the wrong physical rows.

**Corrected approach:** Preview, rank deterministically, delete only the rows explicitly identified as non-survivors, and validate afterward.

---

## 55. Reconciliation Challenges

### Challenge 1 — Missing rows

Given:

```text
source keys:
1,2,3,4

target keys:
1,2,4
```

Write:

```sql
source EXCEPT target
```

Expected:

```text
3
```

---

### Challenge 2 — Extra rows

Given:

```text
source:
1,2,3

target:
1,2,3,5
```

Write:

```sql
target EXCEPT source
```

Expected:

```text
5
```

---

### Challenge 3 — Changed records

Source:

```text
1 | active
2 | active
```

Target:

```text
1 | inactive
2 | active
```

Find the changed key:

```sql
SELECT
    s.customer_id,
    s.status AS source_status,
    t.status AS target_status
FROM source_customers AS s
JOIN target_customers AS t
    ON t.customer_id = s.customer_id
WHERE s.status IS DISTINCT FROM t.status;
```

Expected:

```text
1
```

---

### Challenge 4 — Partition mismatch

Source:

```text
2026-09-27 | 1000 | 50000
2026-09-28 | 1200 | 60000
```

Target:

```text
2026-09-27 | 1000 | 50000
2026-09-28 | 1100 | 60000
```

Ask:

```text
Which checks fail?
Which checks pass?
What can row-count equality and amount equality hide?
```

---

### Challenge 5 — False confidence

Construct:

```text
Source:
A → 100
B → 200

Target:
A → 150
B → 150
```

Global sum:

```text
300
```

for both.

Explain why this does not prove equality.

Use a record-level comparison to expose the difference.

---

## 56. Production Case Study

### Scenario

Three systems provide customer records:

```text
CRM
ERP
SUPPORT
```

The warehouse target requires:

```text
one row per normalized email
```

Input records contain:

- duplicate emails;
- different capitalization;
- leading/trailing whitespace;
- NULL phone numbers;
- different update timestamps;
- different source systems.

### Business rules

1. normalize email using a deliberate rule;
2. prefer CRM over ERP over SUPPORT;
3. if source priority ties, prefer latest `updated_at`;
4. if timestamps tie, prefer lowest `id`;
5. publish exactly one survivor per normalized email;
6. validate the target grain;
7. reconcile source and target according to the business mapping.

### Step 1 — Standardize source schemas

```sql
WITH standardized AS (
    SELECT
        id,
        customer_id,
        email,
        phone,
        country,
        updated_at,
        source_system
    FROM source_customer_a

    UNION ALL

    SELECT
        id,
        customer_id,
        email,
        phone,
        country,
        updated_at,
        source_system
    FROM source_customer_b

    UNION ALL

    SELECT
        id,
        customer_id,
        email,
        phone,
        country,
        updated_at,
        source_system
    FROM source_customer_c
)
SELECT *
FROM standardized;
```

### Stage contract

```text
Input grain:
one row per raw source customer record

Transformation:
align schemas

Output grain:
one row per source record

Business rule:
preserve all source rows

Validation:
same canonical column order/types
```

---

### Step 2 — Normalize identity

```sql
WITH standardized AS (
    SELECT
        id,
        customer_id,
        email,
        phone,
        country,
        updated_at,
        source_system
    FROM source_customer_a

    UNION ALL

    SELECT
        id,
        customer_id,
        email,
        phone,
        country,
        updated_at,
        source_system
    FROM source_customer_b

    UNION ALL

    SELECT
        id,
        customer_id,
        email,
        phone,
        country,
        updated_at,
        source_system
    FROM source_customer_c
),
normalized AS (
    SELECT
        *,
        LOWER(TRIM(email)) AS normalized_email
    FROM standardized
)
SELECT *
FROM normalized;
```

### Stage contract

```text
Input grain:
one row per source customer record

Target business key:
normalized_email

Transformation:
LOWER(TRIM(email))

Output grain:
one row per source record

Validation:
inspect NULL emails and normalization collisions
```

---

### Step 3 — Rank candidates

The business rule is:

```text
CRM
→ ERP
→ SUPPORT
```

then:

```text
latest updated_at
```

then:

```text
lowest id
```

Query:

```sql
WITH standardized AS (
    SELECT id, customer_id, email, phone, country, updated_at, source_system
    FROM source_customer_a

    UNION ALL

    SELECT id, customer_id, email, phone, country, updated_at, source_system
    FROM source_customer_b

    UNION ALL

    SELECT id, customer_id, email, phone, country, updated_at, source_system
    FROM source_customer_c
),
normalized AS (
    SELECT
        *,
        LOWER(TRIM(email)) AS normalized_email
    FROM standardized
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY normalized_email
            ORDER BY
                CASE
                    WHEN source_system = 'CRM' THEN 1
                    WHEN source_system = 'ERP' THEN 2
                    WHEN source_system = 'SUPPORT' THEN 3
                    ELSE 99
                END,
                updated_at DESC,
                id ASC
        ) AS rn
    FROM normalized
    WHERE normalized_email IS NOT NULL
)
SELECT *
FROM ranked
WHERE rn = 1;
```

### Grain contract

```text
Input grain:
one row per source record

Duplicate definition:
same normalized_email

Business key:
normalized_email

Survivor rule:
CRM > ERP > SUPPORT

Secondary rule:
latest updated_at

Tie-breaker:
lowest id

Output grain:
one row per normalized email
```

---

### Step 4 — Validate uniqueness

```sql
WITH golden AS (
    -- survivor query from the previous stage
    SELECT ...
)
SELECT
    normalized_email
FROM golden
GROUP BY normalized_email
HAVING COUNT(*) > 1;
```

Expected:

```text
zero rows
```

---

### Step 5 — Reconcile source records

Reconciliation must account for the fact that the golden table intentionally collapses multiple source records into one survivor.

Therefore the correct comparison is not necessarily:

```text
raw source rows EXCEPT golden rows
```

as though they should be equal.

Instead, define the reconciliation mapping.

Useful checks include:

```text
raw source row counts by source
normalized-key counts
number of duplicate groups
number of survivors
survivor source distribution
```

Example:

```sql
SELECT
    source_system,
    COUNT(*) AS raw_rows,
    COUNT(DISTINCT LOWER(TRIM(email))) AS normalized_emails
FROM standardized
GROUP BY source_system;
```

And survivor distribution:

```sql
SELECT
    source_system,
    COUNT(*) AS survivor_rows
FROM golden_customers
GROUP BY source_system;
```

### Production reasoning

The golden table intentionally has:

```text
fewer rows than raw inputs
```

because its target grain is different.

Therefore reconciliation must compare:

```text
raw population
→ deduplication mapping
→ golden population
```

rather than blindly demanding source and target row-set equality.

---

### Stage-by-stage production model

```text
raw CRM
   \
raw ERP
    \
raw SUPPORT
        ↓
   UNION ALL
        ↓
 standardize
        ↓
 normalize key
        ↓
 detect duplicate groups
        ↓
 rank by:
 source priority
 → updated_at
 → id
        ↓
 select rn = 1
        ↓
 golden customers
        ↓
 uniqueness assertions
        ↓
 reconciliation metrics
```

This is the production-grade pattern:

> **Append first, define identity second, select the survivor third, validate fourth.**

---

## 57. Interview Questions

### 1. What is the difference between `UNION` and `UNION ALL`?

**Concise answer:** Both combine rows; `UNION` removes duplicate result rows, while `UNION ALL` preserves them.

**Deeper explanation:** `UNION` performs duplicate elimination, while `UNION ALL` represents pure append semantics.

**SQL example:**

```sql
SELECT 1
UNION
SELECT 1;
```

versus:

```sql
SELECT 1
UNION ALL
SELECT 1;
```

**Likely follow-up:** When should `UNION ALL` be preferred?

**Common mistake:** Saying `UNION ALL` is always better because it is faster.

---

### 2. When should `UNION ALL` be preferred?

**Concise answer:** When all input rows should be preserved.

**Deeper:** It avoids duplicate elimination when duplicate removal is not part of the business requirement.

**SQL:**

```sql
SELECT *
FROM january
UNION ALL
SELECT *
FROM february;
```

**Follow-up:** What if the sources overlap?

**Common mistake:** Removing duplicates without first deciding whether overlap is valid.

---

### 3. What does `INTERSECT` do?

**Concise answer:** Returns rows present in both result sets.

**SQL:**

```sql
SELECT customer_id FROM a
INTERSECT
SELECT customer_id FROM b;
```

**Follow-up:** What is the difference between `INTERSECT` and a join?

**Common mistake:** Treating it as a column-enrichment operation.

---

### 4. How does `EXCEPT` help reconciliation?

**Concise answer:** `source EXCEPT target` finds source rows missing from target; reverse it to find target-only rows.

**Follow-up:** Why use both directions?

**Common mistake:** Checking only one direction.

---

### 5. Do set operations match columns by name or position?

**Concise answer:** By position.

**SQL:**

```sql
SELECT customer_id, email FROM a
UNION ALL
SELECT customer_id, email FROM b;
```

**Follow-up:** How do you safely combine differently ordered schemas?

**Common mistake:** Assuming matching names protect against `SELECT *` mistakes.

---

### 6. What happens with incompatible data types?

**Concise answer:** The engine must find compatible types or the query fails; implicit coercion behavior is engine-dependent.

**Correct production habit:** Cast explicitly when the target schema matters.

---

### 7. What is an exact duplicate?

**Answer:** A row where all selected attributes are identical for the comparison being performed.

**SQL:**

```sql
SELECT
    a,
    b,
    COUNT(*)
FROM t
GROUP BY a, b
HAVING COUNT(*) > 1;
```

**Common mistake:** Calling business-key duplicates “exact duplicates.”

---

### 8. What is a business-key duplicate?

**Answer:** Multiple records representing one logical entity according to a business key.

**Example:**

```text
customer_id = 1
```

appearing on multiple rows with different timestamps.

---

### 9. What is a near-duplicate?

**Answer:** Records that are not identical but may represent the same entity after normalization or explicit business rules.

**Example:**

```text
ABC Ltd.
ABC LTD
```

**Common mistake:** Treating normalization as proof of identity.

---

### 10. How do you detect duplicates?

**Answer:** Group by the duplicate-defining key and test `COUNT(*) > 1`.

```sql
SELECT key, COUNT(*)
FROM t
GROUP BY key
HAVING COUNT(*) > 1;
```

---

### 11. `DISTINCT` vs `GROUP BY`?

**Answer:** `DISTINCT` removes duplicate combinations of selected expressions; `GROUP BY` creates groups that can also support aggregates.

**Common mistake:** Treating them as interchangeable in every semantic situation.

---

### 12. Why can `DISTINCT` be a bad deduplication strategy?

**Answer:** It does not define which row survives for a business key when other attributes differ.

**Follow-up:** What should you use?

**Answer:** A deterministic survivor strategy such as `ROW_NUMBER()`.

---

### 13. How does `ROW_NUMBER()` help deduplicate?

**Answer:** Partition by the business key, order candidate rows by survivor priority, then keep `rn = 1`.

---

### 14. Why are deterministic tie-breakers important?

**Answer:** They ensure the survivor does not depend on unresolved ordering ties.

**Example:**

```sql
ORDER BY updated_at DESC, record_id ASC
```

---

### 15. How do you implement latest-record deduplication?

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY updated_at DESC, record_id DESC
)
```

then:

```text
rn = 1
```

---

### 16. How do you implement source-priority deduplication?

Encode source priority explicitly:

```sql
CASE
    WHEN source_system = 'CRM' THEN 1
    WHEN source_system = 'ERP' THEN 2
    ELSE 99
END
```

then order by:

```text
priority
→ recency
→ tie-breaker
```

---

### 17. How do you implement completeness-based deduplication?

Create a score such as:

```sql
(CASE WHEN email IS NOT NULL THEN 1 ELSE 0 END)
+
(CASE WHEN phone IS NOT NULL THEN 1 ELSE 0 END)
```

then order by that score descending.

---

### 18. What is PostgreSQL `DISTINCT ON`?

**Answer:** A PostgreSQL-specific way to select one row per listed key according to the query's `ORDER BY`.

**Follow-up:** Is it standard SQL?

**Answer:** No.

---

### 19. What is `QUALIFY`?

**Answer:** A dialect-specific clause that filters after window functions are evaluated.

**Common mistake:** Assuming all SQL engines support it.

---

### 20. How do you safely delete physical duplicates?

**Answer:**

```text
define survivor
→ preview rows to delete
→ run controlled transaction
→ delete only explicit non-survivors
→ validate uniqueness
→ commit
```

**Follow-up:** What is `ctid`?

**Answer:** A PostgreSQL physical tuple identifier useful for controlled cleanup but not a durable business key.

---

### 21. What is reconciliation?

**Answer:** The systematic comparison of source and target populations and values to verify that the target matches the expected source state.

---

### 22. Why do you need `EXCEPT` in both directions?

**Answer:** One direction finds missing target rows; the other finds target-only rows.

---

### 23. How do you detect changed rows?

**Answer:** Compare records with the same business key and use NULL-safe comparisons such as `IS DISTINCT FROM` for nullable attributes; full-row `EXCEPT` can also reveal row-set differences.

---

### 24. Why do set operations treat NULL differently from ordinary equality?

**Answer:** Set operations use row/set semantics where NULLs can participate as matching values for duplicate elimination or set membership, whereas ordinary `NULL = NULL` evaluates to UNKNOWN.

---

### 25. How do you reconcile partition by partition?

**Answer:** Compare counts, distinct keys, and business measures grouped by a partition such as day or month.

---

### 26. Can matching totals prove two datasets are equal?

**Answer:** No. Equal counts and sums can hide different records.

---

### 27. How do you combine differently ordered schemas?

**Answer:** Explicitly project the columns into one canonical order, or use DuckDB's `UNION BY NAME` where appropriate.

---

### 28. What is DuckDB `UNION BY NAME`?

**Answer:** A DuckDB-specific extension that aligns union columns by name instead of only by ordinal position.

---

### 29. Why can `UNION` be more expensive than `UNION ALL`?

**Answer:** `UNION` must remove duplicate result rows, requiring additional work that `UNION ALL` avoids.

---

### 30. Why can `DISTINCT` be expensive?

**Answer:** The engine must identify duplicate selected-row values, potentially requiring sorting or hashing and substantial memory.

---

### 31. How would you design a production deduplication pipeline?

**Answer:**

```text
standardize
→ UNION ALL
→ normalize keys
→ detect duplicates
→ rank by explicit business rules
→ select survivor
→ assert uniqueness
→ reconcile outputs
```

**Common mistake:** Starting with `SELECT DISTINCT`.

---

## 58. Production Checklist

Before shipping a set-operation or deduplication query:

- [ ] I know the grain of each input.
- [ ] I know the intended output grain.
- [ ] I know what “duplicate” means for this dataset.
- [ ] I distinguished exact, business-key, and near-duplicates.
- [ ] I verified column order in every set operation.
- [ ] I verified compatible data types.
- [ ] I intentionally chose `UNION` vs `UNION ALL`.
- [ ] I understand duplicate behavior.
- [ ] I considered NULL semantics.
- [ ] `DISTINCT` is not being used as a band-aid.
- [ ] The survivor rule is explicit.
- [ ] Survivor ordering is deterministic.
- [ ] Tie-breakers are present.
- [ ] Business-key uniqueness is asserted after deduplication.
- [ ] Physical deletion is preceded by survivor validation.
- [ ] Deletion is performed in an appropriate controlled transaction.
- [ ] Reconciliation checks source minus target.
- [ ] Reconciliation checks target minus source.
- [ ] Changed records are investigated separately.
- [ ] Partition-level counts are checked.
- [ ] Partition-level distinct-key counts are checked.
- [ ] Partition-level totals are checked.
- [ ] Global totals are not treated as sufficient proof.
- [ ] Different source schemas are explicitly aligned.
- [ ] NULL placeholders are intentional.
- [ ] Dialect-specific syntax is clearly labeled.
- [ ] Performance cost of `UNION`/`DISTINCT` has been considered.
- [ ] Assertions exist for critical outputs.
- [ ] Upstream causes of duplicate creation are addressed where possible.

---

## 59. Final Knowledge Check

Complete these coding tasks without looking at the solutions first.

### Task 1 — `UNION`

Combine two sets and predict which duplicate rows disappear.

---

### Task 2 — `UNION ALL`

Combine two file batches where repeated rows are legitimate. Explain why `UNION ALL` is required.

---

### Task 3 — `INTERSECT`

Find customer IDs common to source and target.

---

### Task 4 — `EXCEPT`

Find source keys missing from target and then reverse the comparison.

---

### Task 5 — Positional matching

Given:

```text
A:
id, email, country

B:
country, id, email
```

write a safe union with an explicit canonical projection.

---

### Task 6 — Type compatibility

Combine a source `INTEGER` identifier with a target `BIGINT` identifier using an explicit cast.

---

### Task 7 — Exact duplicate detection

Find identical records using:

```sql
GROUP BY ...
HAVING COUNT(*) > 1
```

---

### Task 8 — DISTINCT

Show a case where `DISTINCT` removes exact duplicates but does not deduplicate a business key.

---

### Task 9 — Business-key dedupe

Deduplicate one row per `customer_id` using:

```text
latest timestamp
→ deterministic id
```

---

### Task 10 — PostgreSQL `DISTINCT ON`

Write the same deduplication using `DISTINCT ON`.

---

### Task 11 — `QUALIFY`

Write a DuckDB version using:

```sql
QUALIFY
```

---

### Task 12 — Source-priority survivor

Implement:

```text
CRM > ERP > SUPPORT
```

followed by latest timestamp and a tie-breaker.

---

### Task 13 — Completeness survivor

Choose the most complete record based on three nullable attributes, then break ties by recency and ID.

---

### Task 14 — Physical duplicate cleanup

Write a PostgreSQL transaction that:

```text
previews
→ deletes non-survivors
→ validates uniqueness
```

Then roll it back during practice.

---

### Task 15 — Reconciliation

Produce:

```text
source-only rows
target-only rows
```

using `EXCEPT` in both directions.

---

### Task 16 — Changed records

Find same business keys whose nullable attributes differ.

---

### Task 17 — Partition reconciliation

Compare source and target by day using:

```text
count
distinct key count
sum(amount)
```

---

### Task 18 — NULL semantics

Create:

```text
A = {1, NULL}
B = {1, NULL, 2}
```

and run:

```text
UNION
INTERSECT
EXCEPT
```

Explain the results.

---

### Task 19 — Different schemas

Combine one source with `country` and another without it using:

```sql
NULL AS country
```

---

### Task 20 — DuckDB `UNION BY NAME`

Combine two differently ordered schemas using DuckDB syntax and explain why it is still necessary to govern the schema.

---

### Task 21 — False-confidence reconciliation

Create two datasets with equal:

```text
row count
sum(amount)
```

but different record sets.

Prove the inequality with `EXCEPT`.

---

### Task 22 — End-to-end golden record

Build:

```text
raw
→ standardize
→ UNION ALL
→ normalize
→ rank
→ survivor
→ validate
→ reconcile
```

For each stage document:

```text
Input grain
Target grain
Duplicate definition
Business key
Survivor rule
Tie-breaker
Validation
```

---

## 60. Checkpoint — Ready for Topic 07?

You are ready to continue only when you can practically demonstrate all four capabilities.

### 1. Explain `UNION` vs `UNION ALL`

You should be able to explain:

```text
UNION
→ combines and removes duplicate result rows

UNION ALL
→ combines and preserves duplicate rows
```

You should also be able to explain why `UNION ALL` is often the right append operation when all source rows are valid.

### 2. Deduplicate by business key with deterministic survivor rules

You should be able to write:

```sql
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY
                updated_at DESC,
                record_id ASC
        ) AS rn
    FROM customer_records
)
SELECT *
FROM ranked
WHERE rn = 1;
```

and explain:

```text
grain
→ business key
→ survivor rule
→ tie-breaker
→ output grain
```

### 3. Reconcile two tables with `EXCEPT` and aggregate checks

You should be able to perform:

```text
source EXCEPT target
target EXCEPT source
```

and also compare:

```text
global counts
partition counts
distinct key counts
measure totals
```

You should understand:

```text
equal totals
≠
equal records
```

### 4. Explain how set operations treat NULLs

You should be able to explain:

```text
ordinary:
NULL = NULL
→ UNKNOWN

set semantics:
NULL can participate as a matching value for set duplicate/membership purposes
```

and demonstrate the difference with executable SQL.

### Practical final requirement

Do not continue until you can solve these four tasks without relying on `DISTINCT` as a generic answer to every duplicate problem.

---

# Final Mental Model

When you see a set-operation or deduplication problem, reason in this order:

```text
1. What is the input grain?

2. What is the target grain?

3. What exactly is a duplicate?

4. Is the task:
   combine,
   compare,
   or deduplicate?

5. If combining:
   UNION
   UNION ALL
   INTERSECT
   EXCEPT

6. If deduplicating:
   what is the business key?

7. Which record should survive?

8. Is survivor ordering deterministic?

9. What happens with NULLs?

10. How will I validate the result?

11. What could make the operation expensive?
```

A production Data Engineer should be able to state the semantic contract before writing the SQL:

```text
Input grain
    ↓
Target grain
    ↓
Duplicate definition
    ↓
Business key
    ↓
Survivor rule
    ↓
Tie-breaker
    ↓
SQL pattern
    ↓
Validation
```

That is the durable skill.

---

# Topic 06 Coverage Summary

This chapter covered:

- `UNION`;
- `UNION ALL`;
- `INTERSECT`;
- `EXCEPT`;
- positional column matching;
- compatible types;
- duplicate semantics;
- exact duplicates;
- business-key duplicates;
- near-duplicates;
- normalization;
- `GROUP BY` duplicate detection;
- `DISTINCT`;
- `GROUP BY` deduplication;
- `ROW_NUMBER` deduplication;
- PostgreSQL `DISTINCT ON`;
- `QUALIFY`;
- deterministic survivor selection;
- latest-record selection;
- source-priority selection;
- completeness scoring;
- deterministic tie-breakers;
- safe PostgreSQL physical duplicate deletion;
- source/target reconciliation;
- bidirectional `EXCEPT`;
- missing rows;
- extra rows;
- changed rows;
- partition-level reconciliation;
- NULL set semantics;
- explicit schema alignment;
- NULL placeholders;
- DuckDB `UNION BY NAME`;
- performance intuition for `UNION`;
- performance intuition for `DISTINCT`;
- production deduplication pipelines;
- debugging;
- assertions;
- beginner, intermediate, and advanced exercises;
- debugging challenges;
- reconciliation challenges;
- production case study;
- interview questions;
- production checklist;
- final knowledge check;
- Topic 07 checkpoint.

**Do not treat deduplication as “remove duplicates.” Treat it as “define the intended grain and deterministically construct the correct representative rows.”**
