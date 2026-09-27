# Roadmap — Module 2.6: SQL for Data Engineers

This is the learning roadmap for the sixth module of Stage 2, **Python for
Data Engineering**. It tells you **what** to learn about SQL, **in what
order**, **how** to learn each topic, and **how to prove to yourself** that
you have learned it before you move on.

SQL is the most important language in data engineering after Python — and
in many teams it is used more. Transformations in warehouses and
lakehouses (ELT, dbt, Spark SQL), data-quality checks, reconciliation,
incremental loads, and most interview rounds are written in SQL. You have
already used simple SQL in SQLite (Module 2.1) and DuckDB (Module 2.4).
This module turns that into **production-grade SQL**: correct under NULLs
and duplicates, safe under concurrency, fast because you can read the
plan, and able to load data incrementally with `MERGE` and slowly changing
dimensions.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain SQL's logical order of execution and predict what every clause
  sees.
- Write filters, sorts, and expressions that are correct under
  **three-valued logic** (`NULL`).
- Write every kind of join — including semi-joins, anti-joins, non-equi
  joins, and `LATERAL` — and predict and prevent **join explosion**.
- Aggregate with `GROUP BY`, `HAVING`, conditional aggregation, `FILTER`,
  and `GROUPING SETS` / `ROLLUP` / `CUBE`.
- Structure complex logic with subqueries and CTEs, including recursive
  CTEs.
- Use **window functions** for ranking, running totals, moving averages,
  period-over-period change, gaps-and-islands, and sessionisation.
- Use set operations and choose the right deduplication pattern.
- Design tables with correct data types and constraints.
- Choose indexes and read `EXPLAIN` / `EXPLAIN ANALYZE` plans to fix slow
  queries.
- Explain transactions, isolation levels, MVCC, and locking, and write
  loads that are safe under concurrency.
- Implement upserts with `INSERT ... ON CONFLICT` and `MERGE`, and build
  **SCD Type 1 and Type 2** dimensions in SQL.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.5. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Processes, memory, storage | Stage 0 — How Computers Work / OS Fundamentals | Plans, buffers, and I/O costs in `EXPLAIN` |
| Command line, Docker basics | Stage 0 — Command Line / Developer Environment | Running PostgreSQL in a container and `psql` |
| State, preconditions, edge cases | Stage 1 — Module 1.1 | Writing queries that handle empty inputs, NULLs, and duplicates |
| Idempotency and repeatable jobs | Stage 1 — Module 1.10 | Every load in Topics 09–10 must be re-runnable |
| OLTP vs OLAP, ETL vs ELT, medallion | Stage 2 — Module 2.1 | Why the same SQL behaves differently in PostgreSQL and DuckDB |
| pandas `groupby`, `merge`, window-style ops | Stage 2 — Module 2.3 | You will map each pandas pattern to its SQL equivalent |
| DuckDB basics and analytics SQL extensions | Stage 2 — Module 2.4 | DuckDB is the second engine in every exercise |
| Parquet files, partitions | Stage 2 — Module 2.5 | Loading test data and comparing OLTP vs OLAP engines |

**Tools needed:**

- **PostgreSQL 16 or newer** in Docker (the main engine for this module,
  representing OLTP databases and classic SQL semantics).
- **DuckDB** CLI or Python package (representing analytical engines and
  warehouse-style SQL).
- `psql` and, optionally, a GUI such as DBeaver.
- Python only to **generate** test data (Modules 2.2–2.4); connecting to
  databases from Python is taught in Module 2.7, so in this module you run
  SQL from `.sql` files with `psql -f` and the DuckDB CLI.
- A realistic dataset of a few million rows (orders, customers, products,
  events) generated once and loaded into both engines.

**A note on dialects:** SQL is a standard, but every engine adds its own
extensions. This roadmap teaches standard SQL first, then marks
engine-specific features (PostgreSQL, DuckDB, and — for awareness —
Snowflake, BigQuery, and Spark SQL). Always check your engine's
documentation when a topic says a feature is dialect-specific.

---

## 3. How the module is organised

The ten topics are grouped into four phases. Work through them **in
order**.

```text
Phase A — Querying Correctly                   (Basics)
  01 SELECT, filter, sort, and NULL semantics
  02 Joins and join explosion
  03 Aggregation, GROUP BY, and HAVING

Phase B — Expressive Analytical SQL            (Intermediate → Advanced)
  04 Subqueries and CTEs
  05 Window functions: ranking, running totals, LAG / LEAD
  06 Set operations and deduplication patterns

Phase C — Tables and Performance               (Intermediate → Advanced)
  07 DDL, constraints, and column data types
  08 Indexes and reading EXPLAIN plans

Phase D — Safe Data Changes                    (Advanced)
  09 Transactions, isolation levels, and locking
  10 MERGE, upsert, and SCD implementation in SQL

Consolidate
  practice-questions.md
  interview-practice.md
  Module mini-project: an incremental SQL warehouse
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09 ► 10
read  combine summarise structure  window  dedupe  design  tune  change   load
rows  tables  groups   queries    over    & compare tables queries safely incrementally
                                  rows
```

Why this order:

- NULL semantics (01) come first because they change the result of joins
  (02), aggregates (03), `NOT IN` subqueries (04), window frames (05), and
  set operations (06).
- Joins come before aggregation because the most common aggregation bug is
  aggregating after a join that multiplied rows.
- Window functions (05) need CTEs (04) to filter their results in standard
  SQL; deduplication (06) mostly uses window functions.
- You design tables (07) before indexing them (08).
- `MERGE` and SCD (10) need everything: joins, windows, dedupe,
  constraints, indexes, and transactions (09).

---

## 4. Suggested schedule

About **5 weeks at 8–10 hours per week**. SQL fluency comes from volume —
aim to write at least **200 queries** during this module.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — SELECT and NULLs · Topic 02 — joins |
| 2 | Topic 03 — aggregation · Topic 04 — subqueries and CTEs |
| 3 | Topic 05 — window functions · Topic 06 — set operations and dedupe |
| 4 | Topic 07 — DDL and types · Topic 08 — indexes and EXPLAIN · Topic 09 — transactions |
| 5 | Topic 10 — MERGE and SCD · practice questions · interview practice · mini-project |

---

## 5. How to study every topic (the SQL engineering loop)

```text
Read → State the grain → Predict the row count → Write the query
→ Check against a hand-computed tiny table → Run on both engines
→ Break it (NULLs, duplicates, empty) → Read the plan → Write it down
→ Explain aloud
```

1. **Read** the topic file once, fully.
2. **State the grain** of every input table and of the output ("one row
   per customer per day"). This is the most important SQL habit a data
   engineer has.
3. **Predict the row count** of the result before running the query.
4. **Write the query**, formatted consistently (one clause per line,
   explicit column lists, meaningful aliases).
5. **Check it on a tiny table** (5–10 rows you inserted by hand with
   `INSERT ... VALUES`) where you computed the answer on paper.
6. **Run on both engines** (PostgreSQL and DuckDB) and note any dialect
   differences.
7. **Break it**: add NULLs, duplicate keys, empty tables, ties in ordering.
8. **Read the plan** with `EXPLAIN` for anything that runs on more than a
   few thousand rows (from Topic 08 onwards, always).
9. **Write down** the rule you learned in `module-2.6-notes.md`.
10. **Explain aloud** what each clause does, in execution order.

**Test your SQL like code.** Write every check as an **assertion query
that returns zero rows when correct** — for example, "rows where the
primary key is duplicated" or "orders whose total differs from the sum of
their lines". This is how data-quality tests work in dbt and similar tools
(Modules 2.11 and 2.12).

Keep a single `sql_lab/` project:

```text
sql_lab/
├── docker-compose.yml     # PostgreSQL
├── data/                  # generated CSV/Parquet (git-ignored)
├── schema/                # DDL files, numbered in run order
├── queries/<topic>/       # one .sql file per exercise
├── tests/                 # assertion queries (must return zero rows)
└── run_tests.sh           # runs every tests/*.sql and fails on any row
```

---

## 6. Phase A — Querying Correctly (Basics)

### Topic 01 — [SELECT, filter, sort, and NULL semantics](01-select-filter-sort-and-null-semantics.md)

**Why it comes first:** Every later query is built from these clauses, and
NULL handling is the single biggest source of silently wrong SQL results.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `SELECT`, column aliases, expressions, `FROM`, `WHERE`, `ORDER BY`, `LIMIT` / `OFFSET` (and `FETCH FIRST n ROWS ONLY`) |
| Basics | **Logical order of execution**: `FROM` → `WHERE` → `GROUP BY` → `HAVING` → window functions → `SELECT` → `DISTINCT` → `ORDER BY` → `LIMIT` — and why you cannot use a `SELECT` alias in `WHERE` |
| Basics | Comparison and logical operators, `IN`, `BETWEEN`, `LIKE` / `ILIKE` (PostgreSQL), `CASE WHEN` |
| Basics | Common functions: string (`LOWER`, `TRIM`, `SUBSTRING`, `CONCAT` / `\|\|`), numeric (`ROUND`, `ABS`), date/time (`CURRENT_DATE`, `DATE_TRUNC`, `EXTRACT`, intervals) |
| Intermediate | **NULL and three-valued logic**: `NULL = NULL` is unknown; `IS NULL` / `IS NOT NULL`; `WHERE` keeps only rows where the condition is TRUE |
| Intermediate | `COALESCE`, `NULLIF`, and `IS DISTINCT FROM` (NULL-safe comparison) |
| Intermediate | NULL traps: `NOT IN` with a NULL in the list returns no rows; `col <> 'x'` drops NULL rows; string concatenation with NULL; arithmetic with NULL |
| Intermediate | Sorting NULLs: `NULLS FIRST` / `NULLS LAST` and engine defaults; deterministic ordering with tie-breaker columns |
| Intermediate | Type casting: `CAST(x AS type)` and `x::type` (PostgreSQL); integer division (`5 / 2` = `2` in PostgreSQL) |
| Advanced | Time filters: half-open ranges (`ts >= '2025-03-01' AND ts < '2025-04-01'`) instead of `BETWEEN` on timestamps; `timestamp` vs `timestamptz` in filters |
| Advanced | **Sargable predicates**: why `WHERE DATE(created_at) = '2025-03-01'` or `WHERE amount * 1.1 > 100` can prevent index use and partition pruning (connects to Topic 08 and Module 2.5) |
| Advanced | Keyset (seek) pagination vs `OFFSET` pagination for large result sets and extraction jobs |

**How to learn it**

1. Read the topic file.
2. For ten queries, write the logical execution order next to each clause.
3. Build a truth table for `AND`, `OR`, and `NOT` with `TRUE`, `FALSE`, and
   `NULL`, then verify every cell in PostgreSQL.

**Hands-on exercise — `queries/01/`**

1. Load a customers table where 10% of `country`, `email`, and
   `referrer_id` values are NULL.
2. Write "customers not from India" three ways (`<>`, `NOT IN`,
   `IS DISTINCT FROM`) and explain the three different row counts.
3. Show the `NOT IN (subquery containing NULL)` trap and fix it with
   `NOT EXISTS`.
4. Filter March orders with `BETWEEN` on a timestamp and with a half-open
   range; find the orders `BETWEEN` loses or double-counts at the month
   boundary.
5. Write keyset pagination over orders by `(created_at, order_id)`.
6. Write assertion queries in `tests/` for every rule you discovered.

**Checkpoint — you are ready to move on when you can:**

- [ ] List the logical order of SQL clauses from memory.
- [ ] Explain three-valued logic and why `NOT IN` with NULL returns nothing.
- [ ] Use `COALESCE`, `NULLIF`, and `IS DISTINCT FROM` correctly.
- [ ] Filter timestamps with half-open ranges.
- [ ] Explain what makes a predicate sargable.

**Common mistakes:** `= NULL` instead of `IS NULL`; relying on result order
without `ORDER BY`; `BETWEEN` on timestamps; wrapping filtered columns in
functions.

---

### Topic 02 — [Joins and join explosion](02-joins-and-join-explosion.md)

**Why here:** Nearly every useful query combines tables. Joins are also the
most common cause of inflated revenue and lost customers in reports.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `INNER`, `LEFT`, `RIGHT`, `FULL OUTER`, and `CROSS` joins; self-joins; join conditions with `ON` and `USING` |
| Basics | Venn diagrams are misleading: think of joins as "for each row on the left, find all matching rows on the right" |
| Intermediate | **Join cardinality** (1:1, 1:N, N:1, N:M) and predicting output row counts from key uniqueness (same idea as `validate=` in Module 2.3, now in SQL) |
| Intermediate | **Join explosion**: duplicate keys on the "one" side, many-to-many joins, and the *fan trap* (joining two child tables to the same parent multiplies both) |
| Intermediate | Fixes: pre-aggregate each child table to the parent grain **before** joining; deduplicate dimensions; assert key uniqueness |
| Intermediate | `LEFT JOIN` pitfalls: a condition on the right table in `WHERE` turns it into an inner join — put it in `ON` instead |
| Intermediate | **Semi-joins** (`EXISTS`, `IN`) and **anti-joins** (`NOT EXISTS`, `LEFT JOIN ... WHERE right.key IS NULL`) |
| Intermediate | NULL keys never match in SQL joins (contrast with pandas in Module 2.3) |
| Advanced | Non-equi and range joins (events to a price valid between two dates); `ASOF JOIN` (DuckDB, Snowflake) and its equivalent with `LATERAL` in PostgreSQL |
| Advanced | `LATERAL` joins: "for each row, run this subquery" — e.g. latest 3 orders per customer |
| Advanced | `NATURAL JOIN` and `USING` dangers when schemas change |
| Advanced | Join algorithms at a conceptual level: nested loop, hash join, merge join — and which one suits which data (details in Topic 08) |
| Advanced | Join reconciliation: checking that row counts and totals before and after the join match expectations |

**How to learn it**

1. Read the topic file.
2. For ten join queries, write the expected cardinality and output row
   count before running them.
3. Build a fan trap on purpose (orders → payments and orders → shipments)
   and measure the inflated totals.

**Hands-on exercise — `queries/02/`**

1. Report revenue per customer by joining `orders` to `order_lines` and to
   `payments`; show the fan-trap inflation, then fix it by pre-aggregating
   in two CTEs.
2. Insert a duplicate row into `products` and show the effect on revenue;
   write an assertion that catches duplicate keys in dimension tables.
3. Show the `LEFT JOIN` + `WHERE right.col = ...` bug and fix it.
4. Find customers with no orders (anti-join) three ways and compare plans
   later in Topic 08.
5. Price each order line with the product price valid at order time (range
   join), and with `ASOF JOIN` in DuckDB.
6. Latest three orders per customer with `LATERAL`.

**Checkpoint:**

- [ ] Predict a join's output row count from key cardinalities.
- [ ] Explain and fix a fan trap.
- [ ] Write semi-joins and anti-joins.
- [ ] Explain why a `WHERE` filter can turn a left join into an inner join.
- [ ] Write a range join and a `LATERAL` join.

**Common mistakes:** joining facts to facts; not checking row counts after
joins; `SELECT DISTINCT` to "fix" a join explosion instead of fixing the
grain.

---

### Topic 03 — [Aggregation, GROUP BY, and HAVING](03-aggregation-group-by-and-having.md)

**Why here:** Once tables are joined correctly, you summarise them. Most
gold-layer tables are aggregations.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Aggregate functions: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`; `COUNT(*)` vs `COUNT(col)` vs `COUNT(DISTINCT col)` |
| Basics | `GROUP BY`: every selected column is either grouped or aggregated; the output grain is the group-by columns |
| Basics | `HAVING` (filter groups) vs `WHERE` (filter rows) |
| Intermediate | Aggregates ignore NULLs; `AVG` over NULLs vs zeros; `SUM` of no rows is NULL (use `COALESCE`) |
| Intermediate | **Conditional aggregation**: `SUM(CASE WHEN ... THEN amount END)` and the standard `FILTER (WHERE ...)` clause |
| Intermediate | Pivot-style reports with conditional aggregation; `PIVOT` in DuckDB and other engines |
| Intermediate | Collecting values: `STRING_AGG`, `ARRAY_AGG` (and ordering inside them) |
| Intermediate | Statistical aggregates: `PERCENTILE_CONT` / `PERCENTILE_DISC ... WITHIN GROUP`, `MODE`, `STDDEV` |
| Advanced | `GROUPING SETS`, `ROLLUP`, `CUBE`, and `GROUPING()` for subtotals and grand totals in one query |
| Advanced | Approximate aggregation for big data (e.g. `approx_count_distinct`, HyperLogLog) and when approximate is acceptable |
| Advanced | Averages of averages and ratio metrics: computing ratios from summed numerators and denominators |
| Advanced | Integer overflow and precision in large sums; `NUMERIC` vs `DOUBLE PRECISION` for money |
| Advanced | Dialect conveniences: `GROUP BY ALL` (DuckDB, Snowflake, Databricks), grouping by position (`GROUP BY 1, 2`) and its risks |

**How to learn it**

1. Read the topic file.
2. Rewrite ten pandas `groupby` exercises from Module 2.3 in SQL.
3. For each, state the output grain and row count first.

**Hands-on exercise — `queries/03/`**

1. Daily revenue, order count, distinct customers, and average order value
   per country.
2. A single query with revenue split by payment method using `FILTER`.
3. Countries with more than 1,000 orders and an average order value above a
   threshold (`HAVING`).
4. A report with subtotals per country, per month, and a grand total using
   `ROLLUP`, labelled with `GROUPING()`.
5. p50 and p95 order value per country.
6. Show the "average of averages" error and compute the correct weighted
   average.
7. Assertion: the sum of daily revenue equals the sum of order revenue.

**Checkpoint:**

- [ ] Explain `COUNT(*)` vs `COUNT(col)` vs `COUNT(DISTINCT col)`.
- [ ] Explain `WHERE` vs `HAVING`.
- [ ] Write conditional aggregation with `FILTER`.
- [ ] Produce subtotals with `ROLLUP` or `GROUPING SETS`.
- [ ] Compute a correct ratio metric across groups.

**Common mistakes:** aggregating after an exploding join; averaging
averages; filtering aggregates in `WHERE`; `SUM` returning NULL for empty
groups.

---

## 7. Phase B — Expressive Analytical SQL (Intermediate → Advanced)

### Topic 04 — [Subqueries and CTEs](04-subqueries-and-ctes.md)

**Why here:** Real transformations have many steps. Subqueries and CTEs let
you build them as readable, testable stages — the SQL version of `pipe`
chains in Module 2.3.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Scalar subqueries, subqueries in `FROM` (derived tables), and subqueries in `WHERE` (`IN`, `EXISTS`) |
| Basics | Common Table Expressions: `WITH step_1 AS (...), step_2 AS (...) SELECT ...` |
| Intermediate | **Correlated subqueries**: a subquery that runs per outer row; how engines often rewrite them as joins, and when they stay slow |
| Intermediate | CTEs as pipeline stages: one CTE per transformation step (import, clean, join, aggregate, final) — the style used in dbt models |
| Intermediate | `EXISTS` vs `IN` vs `JOIN`: semantics with duplicates and NULLs |
| Advanced | **Recursive CTEs**: hierarchies (employee → manager, category trees), graph walks, and cycle protection |
| Advanced | Generating series and date spines (`generate_series` in PostgreSQL and DuckDB, recursive CTEs elsewhere) to fill missing days in reports |
| Advanced | CTE materialisation: PostgreSQL inlines simple CTEs by default and supports `MATERIALIZED` / `NOT MATERIALIZED`; other engines differ |
| Advanced | Readability rules: naming CTEs by what they contain, limiting CTE length, and when to use a temporary table or view instead |

**How to learn it**

1. Read the topic file.
2. Take one long, nested query and rewrite it as a chain of CTEs; then
   rewrite one correlated subquery as a join and compare the plans.
3. Draw a small org chart and query it with a recursive CTE.

**Hands-on exercise — `queries/04/`**

1. Customers whose total spend is above the average customer spend — with
   a scalar subquery, a CTE, and a window function (preview of Topic 05).
2. A "daily revenue report with zero-revenue days included" using a date
   spine and a `LEFT JOIN`.
3. Full category paths (`Electronics > Phones > Android`) from a
   parent/child category table with a recursive CTE, with a guard against
   cycles.
4. A five-step CTE pipeline from raw orders to a gold summary, with an
   assertion query for each step's grain.

**Checkpoint:**

- [ ] Explain correlated vs uncorrelated subqueries.
- [ ] Structure a transformation as a CTE chain.
- [ ] Write a recursive CTE for a hierarchy.
- [ ] Build a date spine to fill missing periods.

**Common mistakes:** deeply nested subqueries nobody can read; recursive
CTEs without a stop condition; assuming CTEs are always computed once.

---

### Topic 05 — [Window functions: ranking, running totals, LAG / LEAD](05-window-functions-ranking-running-totals-and-lag-lead.md)

**Why here:** Window functions are the most powerful analytical feature in
SQL and appear in almost every data engineering interview. They compute
across related rows **without collapsing them**.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `function() OVER (PARTITION BY ... ORDER BY ...)`; window functions vs `GROUP BY` |
| Basics | Ranking: `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `PERCENT_RANK`, `CUME_DIST` — and how each treats ties |
| Basics | Offsets: `LAG`, `LEAD` (with default values), `FIRST_VALUE`, `LAST_VALUE`, `NTH_VALUE` |
| Intermediate | Aggregate windows: running totals (`SUM(...) OVER (ORDER BY ...)`), share of total (`amount / SUM(amount) OVER (PARTITION BY ...)`) |
| Intermediate | **Frames**: `ROWS` vs `RANGE` vs `GROUPS`; `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` for moving averages; time-based `RANGE` frames with intervals |
| Intermediate | The **default frame trap**: with `ORDER BY`, the default frame ends at the current row (and includes ties under `RANGE`), which is why `LAST_VALUE` often looks wrong |
| Intermediate | Filtering on window results: wrap in a CTE (standard SQL) or use `QUALIFY` (DuckDB, Snowflake, BigQuery, Databricks) |
| Intermediate | Top-N per group and latest-record-per-key with `ROW_NUMBER` |
| Advanced | **Gaps and islands**: consecutive streaks (login days, uptime periods) using the difference of row numbers |
| Advanced | **Sessionisation**: new session when the gap to the previous event exceeds a threshold (`LAG` + running `SUM` of a new-session flag) |
| Advanced | Period-over-period change (month-over-month, year-over-year) and cohort retention |
| Advanced | Deterministic ordering: adding tie-breakers so results do not change between runs |
| Advanced | Named windows (`WINDOW w AS (...)`) and the cost of many different window specifications (sorts) |

**How to learn it**

1. Read the topic file.
2. On a 10-row table, compute `ROW_NUMBER`, `RANK`, and `DENSE_RANK` by hand
   with ties, then verify.
3. For five frames, draw which rows are included for the current row.

**Hands-on exercise — `queries/05/`**

1. Top 3 products by revenue per country (handle ties explicitly).
2. Running total and 7-day moving average of daily revenue; compare
   `ROWS` and `RANGE` frames when some days are missing.
3. Each customer's days since previous order and month-over-month revenue
   change with `LAG`.
4. Longest streak of consecutive active days per user (gaps and islands).
5. Sessionise click events with a 30-minute inactivity gap; count sessions
   and session length per user.
6. Monthly cohort retention table: share of each signup cohort active in
   later months.
7. Rewrite exercise 1 with `QUALIFY` in DuckDB.

**Checkpoint:**

- [ ] Explain `ROW_NUMBER` vs `RANK` vs `DENSE_RANK` on ties.
- [ ] Explain `ROWS` vs `RANGE` frames and the default frame.
- [ ] Solve gaps-and-islands and sessionisation problems.
- [ ] Filter on a window result in standard SQL and with `QUALIFY`.

**Common mistakes:** non-deterministic `ROW_NUMBER` ordering; the
`LAST_VALUE` default-frame surprise; using `RANK` where `ROW_NUMBER` was
needed for deduplication.

---

### Topic 06 — [Set operations and deduplication patterns](06-set-operations-and-deduplication-patterns.md)

**Why here:** Combining, comparing, and deduplicating datasets are daily
data engineering tasks: merging sources, reconciling tables, and keeping
the right version of each record.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `UNION` vs `UNION ALL` (and why `UNION ALL` is usually what you want); `INTERSECT`; `EXCEPT` |
| Basics | Columns are matched **by position**, not by name; matching types and column counts |
| Basics | Finding duplicates: `GROUP BY key HAVING COUNT(*) > 1` |
| Intermediate | Deduplication patterns: `SELECT DISTINCT`, `GROUP BY`, `ROW_NUMBER()` = 1, `DISTINCT ON` (PostgreSQL), `QUALIFY` |
| Intermediate | Choosing the survivor: latest by timestamp, highest priority source, most complete record — with deterministic tie-breakers |
| Intermediate | Exact duplicates vs business-key duplicates vs near-duplicates (normalised keys) |
| Intermediate | Deleting duplicates in place safely (keep one physical row per key) |
| Advanced | **Table comparison and reconciliation**: `EXCEPT` in both directions to find rows missing or different between source and target; count and sum checks by partition |
| Advanced | NULLs in set operations: set operations treat NULLs as equal (unlike `=`) |
| Advanced | Combining sources with different schemas: `UNION ALL` with explicit column lists and NULL placeholders; `UNION BY NAME` (DuckDB) |
| Advanced | Performance: `UNION` and `DISTINCT` cost a sort or hash of the full result |

**How to learn it**

1. Read the topic file.
2. Implement "latest record per customer" five ways and compare the
   results and plans.
3. Build two versions of a table with known differences and find every
   difference with `EXCEPT`.

**Hands-on exercise — `queries/06/`**

1. Combine customers from three source systems (different column orders)
   with `UNION ALL` and a `source_system` column.
2. Deduplicate to one golden record per email with rules: prefer the CRM
   source, then the latest `updated_at`, then the lowest id.
3. Delete exact duplicate rows from a table in place in PostgreSQL,
   keeping one.
4. Reconcile a source table and a loaded target table: missing rows, extra
   rows, and changed rows, plus per-day counts and sums.
5. Assertion queries: no duplicate business keys; source and target
   reconcile.

**Checkpoint:**

- [ ] Explain `UNION` vs `UNION ALL`.
- [ ] Deduplicate by business key with deterministic survivor rules.
- [ ] Reconcile two tables with `EXCEPT` and aggregate checks.
- [ ] Explain how set operations treat NULLs.

**Common mistakes:** `UNION` silently removing legitimate duplicate rows;
columns in the wrong order in a `UNION`; `DISTINCT` hiding a grain problem.

---

## 8. Phase C — Tables and Performance (Intermediate → Advanced)

### Topic 07 — [DDL, constraints, and column data types](07-ddl-constraints-and-column-data-types.md)

**Why here:** Until now you queried tables. Now you design them so that
bad data is rejected at write time and queries stay correct.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `CREATE TABLE`, `DROP TABLE`, `ALTER TABLE` (add, drop, rename columns), `CREATE TABLE AS SELECT` (CTAS), schemas as namespaces |
| Basics | Core types: `SMALLINT` / `INTEGER` / `BIGINT`, `NUMERIC(p, s)`, `REAL` / `DOUBLE PRECISION`, `TEXT` / `VARCHAR(n)`, `BOOLEAN`, `DATE`, `TIMESTAMP`, `TIMESTAMPTZ`, `INTERVAL`, `UUID` |
| Basics | Constraints: `PRIMARY KEY`, `NOT NULL`, `UNIQUE`, `CHECK`, `FOREIGN KEY`, `DEFAULT` |
| Intermediate | Choosing types: `NUMERIC` for money, `BIGINT` for ids that grow, `TIMESTAMPTZ` for events (PostgreSQL stores an absolute instant and displays in the session time zone) |
| Intermediate | Semi-structured types: `JSONB` and arrays in PostgreSQL; `STRUCT`, `LIST`, `MAP`, and `JSON` in DuckDB (connects to Module 2.5 nested data) |
| Intermediate | Keys: natural vs surrogate keys; identity columns (`GENERATED ... AS IDENTITY`) vs `SERIAL`; UUIDs (design depth in Module 2.8) |
| Intermediate | Foreign keys: `ON DELETE` behaviour and their cost during bulk loads |
| Intermediate | Views vs materialised views; temporary tables; generated columns |
| Advanced | NULLs and `UNIQUE`: multiple NULLs are allowed by default in PostgreSQL; `NULLS NOT DISTINCT` (PostgreSQL 15+) |
| Advanced | Safe schema changes on large tables: which `ALTER TABLE` operations rewrite the table or take heavy locks (details in Topic 09); expand-and-contract migrations (tooling in Module 2.7) |
| Advanced | Declarative table partitioning in PostgreSQL (range by date) and partition pruning; comparison with file partitioning from Module 2.5 |
| Advanced | Constraints in analytical warehouses: often **not enforced** (informational only) — so data engineers must test uniqueness and referential integrity themselves (Module 2.11) |
| Advanced | Naming conventions and documentation: `COMMENT ON`, consistent snake_case, `_at` for timestamps, `_id` for keys, `is_` / `has_` for booleans |

**How to learn it**

1. Read the topic file.
2. Design DDL for an e-commerce schema (customers, addresses, products,
   orders, order_lines, payments) with every type and constraint justified
   in a comment.
3. Try to insert ten kinds of bad data and confirm each is rejected by a
   constraint.

**Hands-on exercise — `schema/`**

1. Write numbered DDL files that create the e-commerce schema in
   PostgreSQL with primary keys, foreign keys, `CHECK` constraints
   (non-negative amounts, valid statuses), and `TIMESTAMPTZ` columns.
2. Create the same schema in DuckDB and list which constraints behave
   differently.
3. Create a range-partitioned `events` table by month in PostgreSQL and show
   partition pruning with `EXPLAIN`.
4. Add a column with a default to a 10-million-row table and time it; then
   change a column type and compare the time (table rewrite).
5. Store order metadata as `JSONB`, query a nested key, and discuss when to
   promote a JSON key to a real column.

**Checkpoint:**

- [ ] Choose correct types for money, ids, timestamps, and flags.
- [ ] Use all six constraint types.
- [ ] Explain `TIMESTAMP` vs `TIMESTAMPTZ`.
- [ ] Explain why warehouse constraints are often not enforced and what
      you do about it.
- [ ] Create a partitioned table and show pruning.

**Common mistakes:** `FLOAT` for money; `VARCHAR(255)` everywhere by habit;
naive timestamps for events; no primary key; running table-rewriting
`ALTER`s on large production tables at peak time.

---

### Topic 08 — [Indexes and reading EXPLAIN plans](08-indexes-and-reading-explain-plans.md)

**Why here:** With tables designed, you learn why queries are slow and how
to make them fast — by reading the plan instead of guessing.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What an index is (a sorted structure pointing to rows) and its cost: faster reads, slower writes, more storage |
| Basics | B-tree indexes: equality and range lookups, sorting, and uniqueness |
| Basics | `EXPLAIN` (estimated plan) vs `EXPLAIN ANALYZE` (runs the query and shows actual rows and time); `BUFFERS` for I/O |
| Intermediate | Plan nodes: sequential scan, index scan, index-only scan, bitmap index/heap scan; nested loop, hash join, merge join; sort, hash aggregate, group aggregate |
| Intermediate | Reading a plan: from the innermost node outwards; estimated vs actual rows; where time is spent |
| Intermediate | **Composite indexes** and column order (leftmost-prefix rule); covering indexes (`INCLUDE`); partial indexes (`WHERE status = 'pending'`); expression indexes (`LOWER(email)`) |
| Intermediate | Other index types in PostgreSQL: `GIN` (JSONB, arrays, full-text), `GiST`, and **`BRIN`** (tiny indexes for huge, time-ordered tables — very useful for event data) |
| Intermediate | When an index is **not** used: low selectivity, non-sargable predicates, type mismatches, stale statistics |
| Advanced | Planner statistics: `ANALYZE`, row estimates, and bad plans caused by wrong estimates; `VACUUM` and table bloat (basics) |
| Advanced | Finding slow queries: `pg_stat_statements`, `auto_explain` (awareness), and query timeouts |
| Advanced | Indexes and bulk loads: dropping and rebuilding indexes around large loads; `CREATE INDEX CONCURRENTLY` |
| Advanced | Analytical engines are different: DuckDB, Snowflake, BigQuery, and Spark rely on columnar storage, min/max zone maps, partition pruning, and clustering instead of B-tree indexes — reading their plans with `EXPLAIN ANALYZE` (Module 2.4) and `EXPLAIN` in Spark (Module 2.14) |
| Advanced | A tuning method: measure → read plan → form a hypothesis → change one thing → measure again |

**How to learn it**

1. Read the topic file.
2. Run ten queries from Topics 01–06 on a 10-million-row table with
   `EXPLAIN (ANALYZE, BUFFERS)` and annotate each plan.
3. For each index you add, write down which query it helps and which
   writes it slows.

**Hands-on exercise — `queries/08/`**

1. Load 20 million orders into PostgreSQL. Time five typical queries with
   no indexes and save their plans.
2. Add the right B-tree, composite, partial, and covering indexes; rerun
   and compare plans and timings.
3. Add a `BRIN` index on `created_at` of a time-ordered events table and
   compare its size and speed with a B-tree.
4. Make one query non-sargable (function on the column) and fix it with an
   expression index or a rewritten predicate.
5. Measure bulk-insert time of 1 million rows with and without indexes.
6. Run the same queries in DuckDB, compare plans, and explain why DuckDB
   is fast without indexes for scans and aggregates.

**Checkpoint:**

- [ ] Read an `EXPLAIN ANALYZE` plan and find the slowest node.
- [ ] Explain the leftmost-prefix rule for composite indexes.
- [ ] Choose between B-tree, partial, covering, GIN, and BRIN indexes.
- [ ] Explain why an index was not used.
- [ ] Explain how analytical engines speed up queries without B-tree
      indexes.

**Common mistakes:** indexing every column; ignoring write costs; tuning
without reading the plan; trusting `EXPLAIN` estimates without `ANALYZE`.

---

## 9. Phase D — Safe Data Changes (Advanced)

### Topic 09 — [Transactions, isolation levels, and locking](09-transactions-isolation-levels-and-locking.md)

**Why here:** Pipelines write data while applications and other pipelines
read and write the same tables. Without understanding transactions, loads
leave half-written data, lose updates, or block production.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **ACID**: atomicity, consistency, isolation, durability |
| Basics | `BEGIN`, `COMMIT`, `ROLLBACK`; autocommit; `SAVEPOINT` and partial rollback |
| Basics | Loading a batch atomically: all rows or none |
| Intermediate | **Isolation levels**: Read Uncommitted, Read Committed (PostgreSQL default), Repeatable Read, Serializable |
| Intermediate | Anomalies: dirty read, non-repeatable read, phantom read, **lost update**, **write skew** — and which level prevents which in PostgreSQL |
| Intermediate | **MVCC** (multi-version concurrency control): readers do not block writers and writers do not block readers; snapshots |
| Intermediate | Row locks: `SELECT ... FOR UPDATE`, `FOR SHARE`, `NOWAIT`, and `SKIP LOCKED` (for work queues and job claiming) |
| Advanced | Serialization failures under Repeatable Read / Serializable, and the need to **retry** transactions |
| Advanced | Table-level locks taken by DDL and maintenance; how an `ALTER TABLE` waiting for a lock can block all other queries; `lock_timeout` and `statement_timeout` |
| Advanced | **Deadlocks**: how they happen, how PostgreSQL detects them, and how to prevent them (consistent lock order, small transactions) |
| Advanced | Long-running transactions: blocking cleanup (`VACUUM`), holding locks, and replication lag |
| Advanced | Pipeline patterns: load into a staging table, then swap or merge inside one short transaction; advisory locks to prevent two runs of the same job at once |
| Advanced | Transactions in analytical engines: DuckDB (single-writer ACID), warehouses, and lakehouse table formats (optimistic concurrency — Module 2.15) |

**How to learn it**

1. Read the topic file.
2. Open two `psql` sessions side by side and reproduce each anomaly step by
   step at different isolation levels. Write down the timeline.
3. Create a deadlock on purpose and read PostgreSQL's error message.

**Hands-on exercise — `queries/09/`**

1. Load a daily batch into a table inside a transaction; kill the process
   halfway and show the table is unchanged.
2. Reproduce a lost update with two sessions under Read Committed and fix
   it with `SELECT ... FOR UPDATE` and with an atomic `UPDATE ... SET x = x
   + 1`.
3. Reproduce write skew (e.g. two doctors going off call) and show that
   Serializable catches it.
4. Build a job queue table where several workers claim jobs with
   `FOR UPDATE SKIP LOCKED` without double-processing.
5. Show an `ALTER TABLE` blocked behind a long transaction blocking new
   `SELECT`s, then protect it with `lock_timeout`.
6. Implement the staging-then-swap pattern for a full table refresh.

**Checkpoint:**

- [ ] Explain ACID and each isolation level.
- [ ] Reproduce and prevent a lost update.
- [ ] Explain MVCC in two sentences.
- [ ] Use `SKIP LOCKED` for a work queue.
- [ ] Explain why long transactions and unguarded DDL are dangerous.

**Common mistakes:** loading row by row in autocommit mode; long
transactions around slow Python code; ignoring serialization-failure
retries; running DDL in production without a lock timeout.

---

### Topic 10 — [MERGE, upsert, and SCD implementation in SQL](10-merge-upsert-and-scd-implementation-in-sql.md)

**Why last:** This is where everything comes together. Incremental loads
compare new data to existing data (joins, dedupe), change it safely
(transactions), rely on keys (constraints, indexes), and keep history
(windows).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Full refresh vs incremental loads: why incremental loads need upserts |
| Basics | **Upsert** in PostgreSQL: `INSERT ... ON CONFLICT (key) DO UPDATE SET ... = EXCLUDED....` and `DO NOTHING`; the unique constraint it requires |
| Basics | The staging pattern: load new data into a staging table, validate it, then apply it to the target |
| Intermediate | **`MERGE`** (SQL standard; PostgreSQL 15+, and most warehouses and lakehouse engines): `WHEN MATCHED THEN UPDATE`, `WHEN NOT MATCHED THEN INSERT`, `WHEN MATCHED AND ... THEN DELETE`; engine support and syntax differences (including DuckDB's upsert and merge support — check your version) |
| Intermediate | **Deduplicate the source first**: `MERGE` fails (or behaves unpredictably) when several source rows match one target row |
| Intermediate | Updating only when something changed: comparing columns with `IS DISTINCT FROM` to avoid useless writes |
| Intermediate | Handling deletes: hard deletes, soft deletes (`is_deleted`, `deleted_at`), and delete markers (tombstones) from sources |
| Intermediate | Idempotency: running the same merge twice must produce the same table |
| Advanced | **Slowly changing dimensions** in SQL (the full modelling theory of SCD types is in Module 2.8): **Type 1** (overwrite) and **Type 2** (keep history with `valid_from`, `valid_to`, `is_current`, and a surrogate key) |
| Advanced | SCD Type 2 mechanics: expire the current row and insert the new version in one transaction; the two-step approach vs a single `MERGE` with a union trick |
| Advanced | Out-of-order and late changes in SCD Type 2 (a change arriving with an effective date before the current version) and why they require re-sequencing history |
| Advanced | Point-in-time joins: facts joined to the dimension version valid at the event time (`event_time >= valid_from AND event_time < valid_to`) |
| Advanced | Performance of merges: indexes on merge keys, batch sizes, and partition-scoped merges in large tables |
| Advanced | Snapshot tables as an alternative to SCD Type 2 (daily full copies) and their trade-offs |

**How to learn it**

1. Read the topic file.
2. Draw the target table before and after each merge for a small example
   with inserts, updates, unchanged rows, and deletes.
3. Walk through SCD Type 2 changes for one customer on paper, including one
   late-arriving change.

**Hands-on exercise — `queries/10/`**

1. Upsert daily product-price files into a `products` table with
   `ON CONFLICT`, updating only rows whose values changed; log inserted and
   updated counts.
2. Rewrite it with `MERGE`, including a delete branch for products marked
   as discontinued.
3. Make the source contain duplicates and show the `MERGE` failure; fix it
   with a `ROW_NUMBER` deduplication CTE.
4. Build `dim_customer` as **SCD Type 2** from daily customer snapshots;
   process 10 days of snapshots; assert exactly one current row per
   customer and no overlapping validity ranges.
5. Process a late-arriving change and repair the history.
6. Join `fact_orders` to `dim_customer` point-in-time and compare revenue
   by customer segment "as it was" vs "as it is now".
7. Re-run every load twice and assert the tables are unchanged
   (idempotency).

**Checkpoint:**

- [ ] Write an upsert with `ON CONFLICT` and with `MERGE`.
- [ ] Explain why the source must be deduplicated before a merge.
- [ ] Implement SCD Type 1 and Type 2 in SQL.
- [ ] Write assertions for SCD Type 2 integrity (one current row, no
      overlaps, no gaps).
- [ ] Join facts to dimensions point-in-time.

**Common mistakes:** merging an undeduplicated source; updating every row
on every run; SCD Type 2 with overlapping validity ranges; closing the old
version and inserting the new one in separate transactions.

---

## 10. Consolidate — practice questions and interview practice

### [`practice-questions.md`](practice-questions.md)

For every question:

1. Write the grain of each input and of the expected output.
2. Predict the output row count.
3. Build a tiny test table with `INSERT ... VALUES`, including NULLs,
   duplicates, and ties.
4. Write the query as a CTE chain.
5. Write assertion queries that prove it correct.
6. Run it on the large dataset and read the plan.

### [`interview-practice.md`](interview-practice.md)

SQL rounds are part of nearly every data engineering interview. Practise
with a **20-minute timer**, speaking out loud:

1. Clarify the grain, keys, NULL handling, ties, and time zones.
2. Describe the approach in plain English.
3. Write the query step by step with CTEs.
4. Walk through it on a tiny example.
5. Discuss performance: indexes, partitioning, and how it would run in a
   warehouse at 1,000× the data.

Typical themes: Nth highest value (with ties), top-N per group, duplicates
and deduplication, running totals, month-over-month growth, retention
cohorts, consecutive days (gaps and islands), sessionisation, median and
percentiles, hierarchies with recursive CTEs, pivoting, anti-joins
("customers who never ..."), fan-trap debugging, and "this query is slow —
walk me through the plan".

---

## 11. Module mini-project — an incremental SQL warehouse

This is the proof that you have finished the module.

**Scenario:** A subscription business runs its application on PostgreSQL.
The analytics team wants a small warehouse with history, built in SQL only.

Build `sql_warehouse/`:

1. **Source (OLTP)** — a PostgreSQL schema with customers, plans,
   subscriptions, invoices, and payments, fully constrained. A Python
   generator (from earlier modules) produces 30 days of daily changes:
   inserts, updates, deletes, duplicates, and one late-arriving change.
2. **Staging** — daily extracts loaded into staging tables inside
   transactions; deduplicated and validated with assertion queries.
3. **Dimensions** — `dim_customer` (SCD Type 2) and `dim_plan` (SCD Type 1)
   with `MERGE`.
4. **Facts** — `fact_invoice` and `fact_payment` loaded incrementally with
   upserts, idempotent on re-run.
5. **Marts** — monthly recurring revenue (MRR) with month-over-month
   change, churn and retention cohorts, top plans per region, and customer
   lifetime value — using window functions, `ROLLUP`, and point-in-time
   joins.
6. **Performance** — indexes chosen from `EXPLAIN ANALYZE` evidence, with a
   before/after table; the same marts computed in DuckDB from Parquet
   exports for comparison.
7. **Concurrency** — prove that a report query running during a load sees
   either the old or the new data, never half of it; guard the load job
   with an advisory lock.
8. **Tests** — a `tests/` folder of assertion queries (keys unique,
   SCD integrity, reconciliation of source vs warehouse totals per day)
   run by `run_tests.sh`, which fails if any assertion returns rows.

**Grading yourself:** running all 30 days in order — and then re-running
any day — produces identical marts; every assertion passes; every index
has a written reason; and you can explain every query clause by clause.

---

## 12. Module self-assessment — exit criteria

Only move to Module 2.7 when you can tick every box without looking at your
notes:

- [ ] I can explain SQL's logical execution order and NULL semantics.
- [ ] I can predict join row counts and prevent join explosion.
- [ ] I can aggregate correctly, including conditional aggregation and
      subtotals.
- [ ] I can structure complex queries with CTEs and recursive CTEs.
- [ ] I can solve ranking, running-total, gaps-and-islands, and
      sessionisation problems with window functions.
- [ ] I can deduplicate and reconcile tables with set operations and
      window functions.
- [ ] I can design tables with correct types and constraints.
- [ ] I can choose indexes and read `EXPLAIN ANALYZE` plans.
- [ ] I can explain isolation levels, MVCC, and locking, and write
      concurrency-safe loads.
- [ ] I can implement upserts, `MERGE`, and SCD Type 1 and 2 idempotently.
- [ ] I have finished the practice questions, interview practice, and the
      mini-project.

---

## 13. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| PostgreSQL official documentation — "The SQL Language", "Performance Tips" (`EXPLAIN`), "Concurrency Control", `MERGE` and `INSERT ... ON CONFLICT` | All topics |
| DuckDB documentation — SQL reference and "Friendly SQL" | 01–06, 10 |
| *SQL Performance Explained* — Markus Winand (and the free site *Use The Index, Luke*) | 01, 07, 08 |
| *Learning SQL*, 3rd edition — Alan Beaulieu (O'Reilly) | 01–06 |
| *SQL Antipatterns* — Bill Karwin | 02, 06, 07 |
| *The Art of PostgreSQL* — Dimitri Fontaine | 04, 05, 07, 08 |
| *Designing Data-Intensive Applications* — Martin Kleppmann, chapter on transactions | 09 |
| Modern SQL (modern-sql.com) — Markus Winand, on window functions, `FILTER`, `LATERAL`, and dialect support | 03, 04, 05 |

---

## 14. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Running SQL from Python, parameters, transactions from code | 2.7 Python Database Connectivity |
| Migrations for schema changes | 2.7 — Alembic |
| Bulk loading with `COPY` | 2.7 — bulk loading and server-side cursors |
| Keys, grain, SCD types, dimensional models | 2.8 Data Modelling for Analytics |
| Incremental extraction with watermarks and CDC | 2.9 Data Ingestion and Extraction Patterns |
| Assertion queries as data tests | 2.11 Data Validation, 2.12 dbt tests |
| CTE-style models and incremental merges | 2.12 Transformation Patterns — dbt |
| Spark SQL, joins, and plans at scale | 2.14 PySpark |
| `MERGE` on lakehouse tables | 2.15 Lakehouse Table Formats |
| Warehouse SQL dialects | 2.17 Cloud Data Platforms |
| Row- and column-level security | 2.20 Observability, Lineage, Governance, and Security |

SQL outlives every tool trend in data engineering. The habits you build
here — stating the grain, predicting row counts, writing assertion
queries, reading the plan, and loading idempotently — apply unchanged to
PostgreSQL, DuckDB, Spark SQL, Snowflake, BigQuery, and every engine that
comes next.
