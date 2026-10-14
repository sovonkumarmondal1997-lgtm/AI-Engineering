# 08 — Indexes and Reading EXPLAIN Plans

> **Stage 2 — Python for Data Engineering**  
> **Module 2.6 — SQL for Data Engineers**  
> **Topic 08 — Indexes and Reading EXPLAIN Plans**
>
> **Primary engine:** PostgreSQL 16+  
> **Secondary comparison:** DuckDB  
> **Broader comparison:** analytical warehouses and Spark
>
> The goal of this chapter is not to memorize index commands. The goal is to learn how to move from a slow query to evidence, a hypothesis, one controlled change, and a measurable conclusion.

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain what an index is;
- explain an index as a physical access path;
- explain why an index can improve reads;
- explain why indexes also create write and storage costs;
- explain B-tree behavior conceptually;
- understand equality and range lookups;
- understand how indexes can sometimes support `ORDER BY`;
- explain unique-index behavior;
- use `EXPLAIN`;
- use `EXPLAIN ANALYZE` safely;
- use `BUFFERS` when I/O evidence matters;
- read execution plans as trees;
- read plans from inner nodes outward;
- distinguish estimated rows from actual rows;
- identify likely bottlenecks;
- understand `Seq Scan`, `Index Scan`, `Index Only Scan`, `Bitmap Index Scan`, and `Bitmap Heap Scan`;
- understand `Nested Loop`, `Hash Join`, and `Merge Join`;
- understand `Sort`, `HashAggregate`, and `GroupAggregate`;
- design composite indexes intentionally;
- reason about composite-index column order and the leftmost-prefix concept;
- understand covering indexes and `INCLUDE`;
- use partial indexes when the workload justifies them;
- use expression indexes when the query expression matches the index;
- reason about selectivity;
- explain why PostgreSQL may ignore an existing index;
- recognize non-sargable predicates and type-mismatch problems;
- understand planner statistics and `ANALYZE`;
- recognize bad row estimates;
- understand foundational `VACUUM` and bloat concepts;
- use `pg_stat_statements` and `auto_explain` at a practical-awareness level;
- understand query timeouts as an operational guardrail;
- understand GIN, GiST, and BRIN at the appropriate level;
- reason about indexes during bulk loads;
- understand `CREATE INDEX CONCURRENTLY`;
- understand how analytical engines can optimize without relying primarily on PostgreSQL-style B-tree indexes;
- reason about columnar storage, zone maps, partition pruning, and clustering;
- tune using:

```text
measure
→ read plan
→ form hypothesis
→ change one thing
→ measure again
```

Most importantly:

> **Explain why the query is slow, what the database is actually doing, what evidence supports the diagnosis, and how you will prove that one change helped.**

---

## 2. Why Query Performance Is a Data Engineering Problem

Query performance is not merely a DBA concern.

Slow SQL can directly affect:

```text
ETL/ELT latency
    ↓
batch completion time
    ↓
SLA compliance
    ↓
downstream freshness
    ↓
compute usage
    ↓
operational cost
```

It can also affect application behavior:

```text
slow query
    ↓
connection occupied longer
    ↓
more concurrent work waits
    ↓
queue grows
    ↓
latency increases
```

### A simple operational example

Suppose one transformation takes:

```text
20 seconds
```

and runs:

```text
100 times per day
```

That is:

```text
20 × 100 = 2,000 seconds
```

of execution time before considering retries, overlapping workloads, storage I/O, and downstream dependencies.

The exact improvement target depends on business requirements.

Do not optimize merely because:

```text
"the query looks ugly."
```

Optimize when:

```text
latency
cost
throughput
freshness
resource pressure
```

matter to the workload.

### Performance engineering is a trade-off

An index may improve a selective read while increasing:

```text
INSERT cost
UPDATE cost
DELETE cost
storage
maintenance
bulk-load time
```

Therefore:

> **Query tuning is workload tuning, not isolated-query optimization.**

---

## 3. Logical SQL vs Physical Execution

A SQL query describes the result you want.

The database still has to decide how to produce it.

Think:

```text
SQL query
    ↓
logical meaning
    ↓
optimizer
    ↓
physical plan
    ↓
execution
    ↓
result
```

### Logical question

```text
"What result should this SQL produce?"
```

### Physical question

```text
"How can the engine produce that result?"
```

These are different questions.

Example:

```sql
SELECT
    customer_id,
    SUM(amount)
FROM orders
GROUP BY customer_id;
```

Logically:

```text
group orders by customer
→ sum amount
→ produce one row per customer
```

Physically, PostgreSQL might choose something conceptually like:

```text
HashAggregate
    └── Seq Scan on orders
```

or:

```text
GroupAggregate
    └── Sort
         └── Seq Scan
```

The logical query is the same.

The physical strategy differs.

This topic is the bridge from:

```text
what SQL means
```

to:

```text
how the database executes it
```

---

## 4. The Core Mental Model of an Execution Plan

The central principle is:

> **An execution plan is the database's chosen physical strategy for producing the result.**

A plan is a tree.

The parent node consumes rows produced by child nodes.

Example:

```text
Nested Loop
├── Index Scan on customers
└── Index Scan on orders
```

The conceptual flow is:

```text
customer rows
    +
matching order rows
    ↓
Nested Loop
    ↓
final result
```

### Read the tree as data flow

For a more complex plan:

```text
HashAggregate
└── Hash Join
    ├── Seq Scan on customers
    └── Hash
        └── Seq Scan on orders
```

Think:

```text
orders scan
    ↓
hash build
    ↓
customers scan
    ↓
hash join
    ↓
aggregate
```

### Plan reading is a causal exercise

Do not ask only:

```text
"What is the top node?"
```

Ask:

```text
Which child produces rows first?
How many rows does it produce?
How many loops occur?
How many rows are consumed by the parent?
Where does work multiply?
Where does time accumulate?
```

---

## 5. What Is an Index?

An index is a separate data structure that gives the database another way to locate rows.

The simplest mental model:

```text
Without useful index
--------------------
table
 ↓
inspect many/all rows

With useful index
-----------------
index
 ↓
locate candidate rows
 ↓
fetch matching table rows when needed
```

A book analogy can help:

```text
book
→ scan every page

index
→ locate likely pages first
```

But the technical model is more important:

> **An index is an access path.**

### An index does not replace the table

The base table still exists.

The index provides additional physical organization.

For a B-tree on:

```text
customer_id
```

the database can navigate an ordered structure to find relevant key values.

It may then use those index entries to identify table rows.

### Important production lesson

Creating an index is not proof that the query will use it.

The optimizer compares possible plans and estimates their costs.

---

## 6. Why Indexes Help Reads

Suppose:

```text
orders = 100 million rows
```

and you ask:

```sql
SELECT *
FROM orders
WHERE order_id = 918273;
```

If `order_id` is highly selective, scanning all 100 million rows would be wasteful.

A useful B-tree access path can provide a far smaller candidate search.

Conceptually:

```text
100,000,000 rows
       ↓
B-tree lookup
       ↓
one/few candidate rows
```

### Equality lookups

```sql
WHERE customer_id = 12345
```

can be excellent candidates when:

```text
customer_id has high selectivity
```

### Range lookups

```sql
WHERE created_at >= ...
  AND created_at < ...
```

can also benefit because B-trees are ordered.

### Ordering

An index can sometimes supply rows in a useful order, reducing sorting work.

### But the optimizer decides

Even with an index:

```text
small table
or
many qualifying rows
or
high random-access cost
```

can make:

```text
Seq Scan
```

cheaper.

---

## 7. The Cost of Indexes

Indexes provide read access paths, but they are not free.

Think:

```text
Index
├── faster eligible reads
├── extra storage
├── write maintenance
└── operational complexity
```

### `INSERT`

A new row can require index entries to be maintained.

### `UPDATE`

If indexed values change, the relevant index structures also need maintenance.

### `DELETE`

Deleting a row affects index state and later cleanup.

### Storage

Ten large indexes can consume substantial storage.

### Maintenance

Indexes participate in:

```text
VACUUM
bloat management
backup/restore
replication
bulk loads
schema changes
```

### Production mistake

Do not:

```text
index every column
```

because “indexes make queries faster.”

Instead ask:

```text
What query?
What predicate?
What ordering?
What selectivity?
What write rate?
What storage cost?
```

---

## 8. B-Tree Indexes

PostgreSQL's B-tree is the general-purpose index type for many relational workloads.

Conceptually, it is:

```text
ordered key structure
        ↓
search by key
        ↓
navigate to relevant entries
```

### Useful workload patterns

B-tree indexes are broadly useful for:

```text
equality
range predicates
ordered retrieval
uniqueness
```

Examples:

```sql
WHERE customer_id = 123
```

```sql
WHERE created_at >= TIMESTAMPTZ '2026-01-01'
```

```sql
ORDER BY created_at DESC
```

### Logarithmic intuition

The important beginner intuition is:

```text
not "scan every key"
but
"navigate a structured ordered tree"
```

Do not turn this into a detailed discussion of internal page algorithms. At this stage, the key is to understand why ordering creates a useful access path.

---

## 9. Equality Lookups

Example:

```sql
SELECT *
FROM customers
WHERE customer_id = 12345;
```

Candidate index:

```sql
CREATE INDEX idx_customers_customer_id
ON customers(customer_id);
```

### Index-decision template

```text
Query pattern:
exact customer lookup

Predicate:
customer_id = constant

Ordering:
none

Expected selectivity:
very high if customer_id is unique

Table size:
large customer table

Read frequency:
high

Write frequency:
depends on customer lifecycle

Candidate index:
(customer_id)

Why:
supports equality search

Trade-offs:
storage + write maintenance

Validation plan:
EXPLAIN
→ EXPLAIN ANALYZE
→ compare execution evidence
```

### When Seq Scan can still win

If the table has:

```text
20 rows
```

an index can be unnecessary.

Scanning 20 rows may cost less than navigating an index and fetching heap pages.

So:

> **Index presence does not determine plan choice.**

---

## 10. Range Lookups

Example:

```sql
SELECT *
FROM orders
WHERE created_at >= TIMESTAMPTZ '2026-03-01 00:00:00+00'
  AND created_at <  TIMESTAMPTZ '2026-04-01 00:00:00+00';
```

Candidate:

```sql
CREATE INDEX idx_orders_created_at
ON orders(created_at);
```

### Why B-tree can help

The index stores keys in order.

The engine can:

```text
find lower bound
→ walk the ordered range
→ stop after upper bound
```

This connects to Topic 01's half-open range habit:

```text
[start, end)
```

which is especially useful for timestamp queries.

### Selectivity matters

A one-day filter on a multi-year event table may be selective.

A filter that matches 90% of the table is a different workload.

Do not use a universal percentage threshold. Let:

```text
table size
distribution
cache state
row width
random access
statistics
```

inform the decision.

---

## 11. Indexes and ORDER BY

Consider:

```sql
SELECT
    order_id,
    created_at
FROM orders
ORDER BY created_at DESC
LIMIT 100;
```

A suitable index may let PostgreSQL retrieve rows in a useful order, potentially avoiding or reducing a separate sort.

Example candidate:

```sql
CREATE INDEX idx_orders_created_at_desc
ON orders(created_at DESC);
```

### Important caveat

Do not say:

> “If an index matches `ORDER BY`, PostgreSQL always eliminates the sort.”

The optimizer still weighs:

```text
index traversal
heap fetches
selectivity
LIMIT
table size
```

against alternatives.

### Practical question

For a query with:

```text
ORDER BY
+
LIMIT
```

an ordered index can be particularly interesting because the engine may only need the first small set of rows.

Measure it.

---

## 12. Unique Indexes and Constraints

A unique constraint is a schema-level business rule:

```text
this value/composite combination must be unique
```

PostgreSQL enforces uniqueness through unique indexing machinery.

Example:

```sql
CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE
);
```

Or explicitly:

```sql
CREATE UNIQUE INDEX idx_customers_email
ON customers(email);
```

### Important distinction

A unique constraint expresses:

```text
schema/business rule
```

A unique index expresses:

```text
physical structure that can enforce uniqueness
```

The exact DDL relationship is engine-specific, and Topic 07 already covered constraint design in detail.

Here, remember:

> **Uniqueness can simultaneously be a data-quality rule and an access path.**

---

## 13. EXPLAIN

Use:

```sql
EXPLAIN
SELECT
    *
FROM orders
WHERE customer_id = 123;
```

`EXPLAIN` shows the optimizer's estimated plan without running the query in the normal case.

Typical information includes:

```text
Node
Estimated startup cost
Estimated total cost
Estimated rows
Estimated row width
Child nodes
```

### Simulated example

> **SIMULATED PLAN — NOT ACTUAL OUTPUT**

```text
Index Scan using idx_orders_customer_id on orders
  (cost=0.42..18.55 rows=12 width=64)
  Index Cond: (customer_id = 123)
```

Interpretation:

```text
Node:
Index Scan

Estimated total cost:
18.55

Estimated rows:
12

Estimated width:
64 bytes

Access path:
idx_orders_customer_id

Predicate handled by index:
customer_id = 123
```

Do not treat:

```text
cost = 18.55
```

as:

```text
18.55 milliseconds
```

It is an optimizer cost unit, not a direct time measurement.

---

## 14. EXPLAIN ANALYZE

Use:

```sql
EXPLAIN ANALYZE
SELECT
    *
FROM orders
WHERE customer_id = 123;
```

`EXPLAIN ANALYZE` actually executes the statement and reports actual execution information.

You can then compare:

```text
estimated rows
vs
actual rows
```

and:

```text
estimated strategy
vs
what really happened
```

### Typical information

```text
actual time
actual rows
loops
estimated rows
execution time
```

### Critical safety warning

For:

```text
INSERT
UPDATE
DELETE
```

`EXPLAIN ANALYZE` runs the statement.

Safe learning example:

```sql
BEGIN;

EXPLAIN ANALYZE
DELETE FROM orders
WHERE order_id = 918273;

ROLLBACK;
```

This still executes the delete before rolling it back.

For DDL and other side effects, understand the statement's transactional behavior and do not casually run analysis against production.

### Production principle

> **`EXPLAIN` asks what the optimizer plans. `EXPLAIN ANALYZE` shows what happened while executing.**

---

## 15. BUFFERS

Use:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    *
FROM orders
WHERE customer_id = 123;
```

`BUFFERS` adds block-I/O information.

At a high level, useful fields include:

```text
shared hit
shared read
temp blocks
```

### Conceptual interpretation

```text
shared hit
→ block found in PostgreSQL's shared buffers/cache

shared read
→ block had to be read from storage into the buffer

temp
→ temporary work used intermediate storage structures
```

Exact output and additional fields depend on the statement and PostgreSQL version.

### Why BUFFERS helps

Suppose two plans have similar CPU behavior but one reads a huge number of blocks.

`BUFFERS` gives evidence about:

```text
cache activity
storage reads
temporary I/O
```

It is especially useful when the question is:

> “Is this query spending time moving through a lot of data?”

Do not reduce performance analysis to buffer counts alone.

---

## 16. How to Read a Plan

Use a repeatable process.

### Step 1 — Find the root node

What operation produces the final result?

Examples:

```text
Aggregate
Sort
Nested Loop
Hash Join
```

### Step 2 — Inspect children

What data feeds the root?

### Step 3 — Find the leaf access

What actually reads the base table?

Examples:

```text
Seq Scan
Index Scan
Bitmap Heap Scan
```

### Step 4 — Compare estimated and actual rows

Look for meaningful mismatch.

### Step 5 — Inspect loops

A node with:

```text
actual rows = 10
loops = 100,000
```

may perform far more work than the single-row shape initially suggests.

### Step 6 — Identify time concentration

Which node consumed meaningful execution time?

### Step 7 — Inspect memory/I/O evidence

Use:

```text
BUFFERS
sort behavior
hash behavior
```

when relevant.

### Step 8 — Form one hypothesis

For example:

> “The nested loop became expensive because the outer side is much larger than estimated.”

### Step 9 — Make one meaningful change

Then re-measure.

---

## 17. Reading Plans from the Inside Out

The execution tree should be read as data flow.

Simulated example:

```text
HashAggregate
└── Hash Join
    ├── Seq Scan on customers
    └── Hash
        └── Seq Scan on orders
```

Read from the leaves:

```text
1. scan orders
2. build hash structure
3. scan customers
4. probe/join
5. aggregate
```

### Why this works

Parent nodes depend on child output.

If:

```text
Seq Scan on orders
```

produces ten million rows, everything above it must deal with those rows.

### Production habit

Do not stare only at:

```text
HashAggregate
```

and say:

```text
"Aggregate is slow."
```

The aggregate might be slow because:

```text
its child produced too many rows
```

This is why plan reading is causal.

---

## 18. Estimated Rows vs Actual Rows

This is one of the highest-value plan-reading skills.

Simulated:

```text
Index Scan
estimated rows = 100
actual rows    = 105
```

This is broadly consistent.

Another case:

```text
Index Scan
estimated rows = 100
actual rows    = 2,000,000
```

This is a major warning sign.

### Why?

The optimizer chooses plans using estimates.

Think:

```text
statistics
    ↓
cardinality estimate
    ↓
cost estimate
    ↓
plan choice
```

If the estimate is far from reality, the cost model can evaluate alternatives incorrectly.

### Example downstream consequence

The planner expects:

```text
100 rows
```

and chooses:

```text
Nested Loop
```

but reality is:

```text
2,000,000 rows
```

Now the repeated inner operation may execute far more times than expected.

### Important qualification

An estimate mismatch does not automatically mean the plan is bad.

The correct question is:

> **Did the estimate error materially contribute to an inefficient plan?**

---

## 19. Execution Time and Timing

PostgreSQL plan timing requires careful reading.

Key concepts:

```text
Planning Time
Execution Time
```

At the node level, `actual time` usually represents:

```text
startup → first row
total → completion
```

and is reported in milliseconds.

### Loops matter

A node with:

```text
actual time = 0.10..0.20
loops = 1
```

is very different from:

```text
actual time = 0.10..0.20
loops = 100,000
```

because the node executes repeatedly.

### Startup vs total

A node can have:

```text
high startup
low total
```

or:

```text
low startup
high total
```

depending on its work.

Use these fields as evidence, not as standalone explanations.

### Planning vs execution

Always distinguish:

```text
planning time
```

from:

```text
execution time
```

A query can have low execution time but non-trivial planning overhead, or the reverse.

---

## 20. Sequential Scan

Plan node:

```text
Seq Scan
```

means PostgreSQL reads table pages sequentially and evaluates the relevant condition.

### Important rule

> **Seq Scan does not mean the query is bad.**

It can be the correct choice when:

- the table is small;
- a large fraction of rows qualifies;
- the query needs many columns;
- sequential page access is cheaper than many random heap lookups.

### Example

```sql
SELECT *
FROM customers
WHERE country = 'IN';
```

If:

```text
80% of customers are in India
```

an index on `country` may not be attractive.

A sequential scan can be perfectly reasonable.

### Production mental model

Ask:

```text
How many rows qualify?
How large is the table?
How wide are the rows?
How expensive is random access?
```

not:

```text
"Why didn't PostgreSQL use my index?"
```

---

## 21. Index Scan

Plan node:

```text
Index Scan
```

conceptually means:

```text
navigate index
→ find candidate tuple locations
→ fetch table rows
```

Simulated:

```text
Index Scan using idx_orders_customer_id on orders
  Index Cond: (customer_id = 123)
```

### Why it can be useful

For a selective predicate:

```text
few matching rows
```

the index can avoid scanning the entire table.

### Heap access

The index may identify:

```text
where the row is
```

but the query may still need:

```text
columns not available from the index
```

so PostgreSQL fetches heap tuples.

### Production question

Ask:

```text
How many index entries?
How many heap fetches?
How many loops?
```

---

## 22. Index-Only Scan

Plan node:

```text
Index Only Scan
```

can allow PostgreSQL to satisfy the requested columns from the index without fetching the heap row for every tuple.

This requires more than simply having the columns somewhere in the index.

Conceptually:

```text
query columns
    ↓
contained in index
    ↓
can index answer the query?
    ↓
visibility information matters
```

### Visibility map

PostgreSQL tracks whether heap pages are known to contain only tuples visible to all relevant transactions.

This visibility information affects whether heap checks can be avoided.

Therefore:

> “Index-only” does not mean “the index always avoids touching the table.”

### Covering-index connection

A covering index can make index-only plans possible by placing needed columns in the index.

PostgreSQL's `INCLUDE` is one tool for this.

---

## 23. Bitmap Index Scan

Plan node:

```text
Bitmap Index Scan
```

conceptually means:

```text
use index
→ build bitmap of candidate table locations
```

This can be a useful middle ground between:

```text
highly selective Index Scan
```

and:

```text
full Seq Scan
```

### Why bitmap access exists

Suppose:

```text
thousands or hundreds of thousands of rows match
```

A direct row-by-row index lookup can involve many scattered heap fetches.

A bitmap can collect locations first, then process table pages more efficiently.

### Multiple indexes

PostgreSQL can also combine bitmap information from multiple indexes for certain boolean conditions.

Do not assume a bitmap plan is automatically faster. It is an optimizer choice based on the cost model.

---

## 24. Bitmap Heap Scan

Typical combination:

```text
Bitmap Index Scan
        ↓
Bitmap Heap Scan
```

Conceptually:

```text
Bitmap Index Scan
→ identify candidate pages/tuples

Bitmap Heap Scan
→ visit the table pages
→ recheck/filter where required
```

### Why this can be useful

It can make sense when:

```text
more matches than a highly selective Index Scan
but
fewer than a full-table workload
```

or when multiple index conditions can be combined.

### Plan-reading question

If you see:

```text
Bitmap Heap Scan
```

look below it.

Ask:

```text
Which index built the bitmap?
How many candidate rows?
How many heap blocks?
How many rows survived?
```

---

## 25. Nested Loop Join

A Nested Loop conceptually does:

```text
for each row from outer side
    execute/probe inner side
```

Simulated:

```text
Nested Loop
├── Seq Scan on customers
└── Index Scan on orders
```

Imagine:

```text
outer customers = 10 rows
inner lookup = fast index lookup
```

This can be excellent.

### Why it can become expensive

Now imagine:

```text
outer rows = 5,000,000
inner lookup = repeated many times
```

Even a small inner operation becomes expensive when repeated millions of times.

### Loop multiplication

This is why:

```text
actual rows
+
loops
```

must be read together.

Do not say:

> “Nested Loop is bad.”

Say:

> “Nested Loop can be efficient for a small outer relation with an efficient inner lookup; it can become expensive when the outer side is unexpectedly large.”

---

## 26. Hash Join

A Hash Join generally uses:

```text
build
+
probe
```

Conceptually:

```text
build a hash structure for one input
        ↓
scan/probe the other input
        ↓
match equal keys
```

Typical use:

```text
equality join
```

### Memory

The build side requires memory for the hash structure.

If the workload exceeds comfortable memory, the engine may need additional work such as batching or spilling.

### Plan-reading question

When you see:

```text
Hash Join
```

ask:

```text
Which side is being hashed?
How many rows were expected?
How many rows were actual?
Is memory likely to be an issue?
```

Do not teach a rigid rule that the smaller table is always the build side without examining the actual plan and optimizer choice.

---

## 27. Merge Join

A Merge Join conceptually merges two inputs that are ordered by the join keys.

```text
sorted input A
+
sorted input B
        ↓
merge matching keys
```

### Strengths

It can be attractive when:

```text
inputs are already appropriately ordered
```

or ordering can be obtained cheaply.

### Sorting cost

If the inputs are not ordered, the plan may include:

```text
Sort
```

nodes.

So when you see:

```text
Merge Join
├── Sort
└── Sort
```

the join itself is not the only relevant work.

Read the child nodes.

---

## 28. Sort

A `Sort` node orders rows according to a required ordering.

Sorting may be required for:

```text
ORDER BY
Merge Join
GroupAggregate
some DISTINCT/duplicate-elimination strategies
window operations
```

Topic 05 already covered window-specific ordering and frames, so here focus on execution.

### Memory

Sorting may consume significant memory.

If the sort cannot complete comfortably in memory, PostgreSQL can use temporary files.

This can be reflected in:

```text
BUFFERS
temp blocks
```

or in sort-specific plan information.

### Plan-reading habit

Do not ask only:

```text
"Is there a Sort?"
```

Ask:

```text
How many rows?
How wide?
What ordering is required?
How often does it run?
Did it spill?
Could a different access path produce useful ordering?
```

---

## 29. Hash Aggregate

A `HashAggregate` groups rows using a hash-based structure.

Example logical query:

```sql
SELECT
    customer_id,
    SUM(amount)
FROM orders
GROUP BY customer_id;
```

Possible simulated plan:

```text
HashAggregate
  Group Key: customer_id
  -> Seq Scan on orders
```

### Mental model

```text
input rows
    ↓
hash bucket by group key
    ↓
update aggregate state
    ↓
one output row per group
```

### Cost considerations

- number of input rows;
- number of groups;
- row width;
- memory;
- possible spill/batching.

Again:

> Do not decide that `HashAggregate` is good or bad in isolation.

---

## 30. Group Aggregate

A `GroupAggregate` can aggregate input already ordered/grouped on the grouping key.

Simulated:

```text
GroupAggregate
  Group Key: customer_id
  -> Sort
       Sort Key: customer_id
       -> Seq Scan on orders
```

Conceptual flow:

```text
input
→ order/group by key
→ process one group at a time
```

### HashAggregate vs GroupAggregate

| Dimension | `HashAggregate` | `GroupAggregate` |
|---|---|---|
| Main structure | hash table | ordered groups |
| Ordering requirement | not necessarily | grouped/ordered input |
| Memory shape | number of groups | depends on execution/order |
| Possible prerequisite | none | sort or already ordered input |

Neither is universally better.

The optimizer chooses based on its estimates and cost model.

---

## 31. Composite Indexes

A composite index contains multiple key columns.

Example:

```sql
CREATE INDEX idx_orders_customer_created
ON orders(customer_id, created_at);
```

This is not the same as having two unrelated single-column indexes.

Its key ordering is:

```text
customer_id
    then
created_at
```

### Query it can naturally support

```sql
SELECT *
FROM orders
WHERE customer_id = 123
  AND created_at >= TIMESTAMPTZ '2026-01-01';
```

It may also support:

```sql
WHERE customer_id = 123
```

because the leading key is present.

### Design template

```text
Query pattern:
customer history by time

Predicate:
customer_id = ?
created_at >= ?

Ordering:
created_at DESC

Expected selectivity:
high after customer_id filtering

Table size:
large

Read frequency:
high

Write frequency:
medium/high

Candidate index:
(customer_id, created_at DESC)

Why:
aligns with customer-scoped chronological access

Trade-offs:
storage + write maintenance

Validation plan:
compare EXPLAIN ANALYZE before/after
```

---

## 32. Column Order and Leftmost-Prefix Reasoning

For:

```text
(customer_id, created_at)
```

think of the index as primarily ordered by:

```text
customer_id
```

and within each customer:

```text
created_at
```

This is the intuitive **leftmost-prefix** concept.

### Naturally aligned

```sql
WHERE customer_id = 123
```

and:

```sql
WHERE customer_id = 123
  AND created_at >= ...
```

are naturally aligned with:

```text
(customer_id, created_at)
```

### Less naturally aligned

A query primarily filtering by:

```sql
WHERE created_at >= ...
```

does not have the same direct alignment with the first index key.

### Do not overstate the rule

Do not say:

> “The second column can never be used.”

The PostgreSQL optimizer has more nuanced options, and the exact plan depends on:

```text
statistics
predicate shape
data distribution
other indexes
table size
version
```

Use leftmost-prefix reasoning as:

> **A practical design intuition, not an absolute binary law.**

---

## 33. Covering Indexes and INCLUDE

PostgreSQL supports included, non-key columns:

```sql
CREATE INDEX idx_orders_customer_cover
ON orders(customer_id, created_at)
INCLUDE (amount, status);
```

The key columns are:

```text
customer_id
created_at
```

The included columns are:

```text
amount
status
```

### Why include columns?

Suppose:

```sql
SELECT
    created_at,
    amount,
    status
FROM orders
WHERE customer_id = 123
ORDER BY created_at DESC
LIMIT 100;
```

The index keys support:

```text
customer filter
+
ordering
```

and `INCLUDE` may provide extra selected columns for an index-only access path.

### Trade-offs

More included data means:

```text
larger index
+
more storage
+
more write maintenance
```

Do not include every column.

### Visibility-map dependency

Even when all needed values exist in the index, PostgreSQL may still need heap visibility checks depending on the state of the visibility map.

So:

> **Covering index ≠ guaranteed index-only scan.**

---

## 34. Partial Indexes

A partial index contains only rows satisfying a predicate.

Example:

```sql
CREATE INDEX idx_orders_pending
ON orders(customer_id)
WHERE status = 'pending';
```

Conceptually:

```text
orders
├── pending rows → included
└── other rows   → not indexed
```

### Good use cases

- pending jobs;
- active rows;
- hot subsets;
- sparse statuses.

### Candidate decision

```text
Query pattern:
find pending jobs for a customer

Predicate:
status = 'pending'

Expected selectivity:
small hot subset

Table size:
large

Read frequency:
high

Candidate index:
(customer_id) WHERE status = 'pending'

Why:
smaller structure focused on the hot subset

Trade-offs:
only useful for matching predicates; index maintenance still exists

Validation:
EXPLAIN ANALYZE against representative pending workload
```

### Important limitation

A partial index is only useful when the query predicate is compatible with its predicate.

Do not assume:

```text
partial index exists
→ every query benefits
```

---

## 35. Expression Indexes

An expression index indexes the result of an expression.

Example:

```sql
CREATE INDEX idx_users_lower_email
ON users (LOWER(email));
```

Then:

```sql
SELECT *
FROM users
WHERE LOWER(email) = 'alice@example.com';
```

can potentially use that expression index.

### Why this matters

Suppose the normal index is:

```sql
CREATE INDEX idx_users_email
ON users(email);
```

and the query is:

```sql
WHERE LOWER(email) = 'alice@example.com'
```

the indexed expression and the query expression do not match in the same way.

An expression index aligns the physical access path with the required transformation.

### Production caution

Do not create expression indexes for every transformation.

Ask:

```text
Is this expression part of a frequent workload?
Is it a stable business/query requirement?
Would a schema change be cleaner?
```

This connects directly to Topic 01's sargability discussion.

---

## 36. Selectivity

Selectivity describes how much of the table a condition matches.

Conceptually:

```text
high selectivity
→ few rows match

low selectivity
→ many rows match
```

### Example

```sql
WHERE customer_id = 12345
```

can be highly selective if the ID is unique.

Compare:

```sql
WHERE is_active = TRUE
```

If:

```text
95% of rows are active
```

then that condition is low-selectivity.

### Why selectivity matters

An index is not valuable merely because a predicate exists.

The optimizer compares:

```text
index-based access
vs
sequential scan
```

and estimates the work.

If most of the table qualifies, scanning sequentially can be cheaper.

Do not use a universal rule such as:

```text
"indexes only work below X%"
```

Real workload cost depends on more variables.

---

## 37. Why PostgreSQL May Ignore an Index

An existing index can be ignored for legitimate reasons.

Possible reasons include:

```text
table is small
large fraction of rows qualify
low selectivity
random-access cost is high
statistics are stale
predicate shape is not index-friendly
data types introduce casts
index order does not match the workload
another plan has lower estimated cost
```

### Troubleshooting template

```text
Query pattern:
...

Predicate:
...

Table size:
...

Expected selectivity:
...

Existing index:
...

Observed plan:
...

Why planner may prefer current plan:
...

Hypothesis:
...

Test:
...

Result:
...
```

### Example

```sql
SELECT *
FROM orders
WHERE status = 'completed';
```

If:

```text
92% of rows are completed
```

a sequential scan can be more attractive.

The optimizer is not “ignoring the index by mistake” merely because the index exists.

### Strong production lesson

> **“Index exists” is not evidence that “index should be used.”**

---

## 38. Non-Sargable Predicates

A predicate is often called **sargable** when its shape allows the optimizer to use an available access path efficiently.

Example that can be problematic for a simple index:

```sql
WHERE DATE(created_at) = DATE '2026-03-01'
```

because the column is wrapped in a function.

A more index-friendly shape is:

```sql
WHERE created_at >= TIMESTAMPTZ '2026-03-01 00:00:00+00'
  AND created_at <  TIMESTAMPTZ '2026-03-02 00:00:00+00'
```

### Another example

```sql
WHERE amount * 1.1 > 100
```

can be transformed algebraically, when safe, into a condition on the indexed column:

```sql
WHERE amount > 100 / 1.1
```

The exact rewrite depends on:

```text
numeric type
rounding
NULL behavior
business semantics
```

Do not rewrite expressions blindly.

### Alternative: expression index

If the transformed expression is itself the stable workload requirement:

```sql
CREATE INDEX ...
ON table ((DATE(created_at)));
```

may be appropriate in PostgreSQL.

Again:

```text
measure
→ inspect
→ choose
```

---

## 39. Type Mismatches

Data types influence both correctness and optimization.

Suppose:

```text
customer_id BIGINT
```

but the query compares it through an incompatible or unexpected cast.

The engine may need to cast values.

That can affect:

```text
index matching
selectivity estimation
operator selection
execution work
```

### Production principle

> **Store data in the correct type rather than correcting schema problems inside every query.**

### Diagnostic questions

```text
What is the column type?
What is the parameter/literal type?
Is an implicit cast occurring?
Which side is being cast?
Does the comparison match the index's operator semantics?
```

Do not invent a universal rule such as:

```text
"casts always prevent indexes."
```

The exact behavior depends on the expression and operator.

---

## 40. Planner Statistics

The PostgreSQL optimizer relies on statistics to estimate how many rows a predicate will match.

Statistics summarize aspects such as:

```text
row counts
value distributions
common values
distinctness
selectivity
```

The conceptual chain is:

```text
table data
   ↓
statistics
   ↓
cardinality estimate
   ↓
cost estimate
   ↓
plan choice
```

### Why statistics matter

Suppose:

```text
planner expects 100 rows
actual = 2,000,000
```

That is a very different workload from what the optimizer modeled.

### Distribution changes

A table can evolve:

```text
January
mostly completed orders

September
mostly pending orders
```

If statistics no longer reflect reality, the optimizer's estimates can degrade.

---

## 41. ANALYZE

Run:

```sql
ANALYZE orders;
```

`ANALYZE` updates planner statistics for the table.

It is useful after substantial data changes or distribution shifts.

Examples:

```text
large bulk load
large delete
large update
major distribution change
```

### Correct interpretation

Do not say:

> “Run ANALYZE whenever a query is slow.”

Instead:

> **When estimates appear stale or inaccurate, refreshing statistics with `ANALYZE` can improve the optimizer's information. It is one diagnostic/action among several.**

### Investigation sequence

```text
slow query
→ EXPLAIN ANALYZE
→ compare estimated/actual rows
→ if statistics appear stale
→ ANALYZE
→ re-measure
```

If the problem remains, investigate:

```text
query shape
index design
correlation
join strategy
data distribution
```

---

## 42. Bad Row Estimates

Simulated example:

> **SIMULATED PLAN**

```text
Nested Loop
  -> Seq Scan on customers
       estimated rows = 50
       actual rows    = 500000
  -> Index Scan on orders
       estimated rows = 1
       actual rows    = 4
       loops          = 500000
```

### Read it

The optimizer expected:

```text
50 outer rows
```

but reality was:

```text
500,000 outer rows
```

The inner index lookup then ran:

```text
500,000 times
```

The nested-loop plan became expensive.

### Possible explanation

The root cause could be:

```text
stale statistics
correlated predicates
data distribution change
underestimated relation size
```

Do not assume `ANALYZE` is always the solution.

### Production principle

A large row-estimate error is valuable diagnostic evidence.

The next question is:

> **Which plan decision did that error influence?**

---

## 43. VACUUM and Bloat

PostgreSQL uses MVCC, so updates and deletes can leave dead tuples until cleanup.

Conceptually:

```text
UPDATE / DELETE
    ↓
old row versions
    ↓
dead tuples
    ↓
VACUUM cleanup
```

### Bloat

At a foundational level, bloat means:

```text
physical storage contains more space than the current live data needs
```

It can involve:

```text
table bloat
index bloat
```

### Why bloat matters

Excess physical pages can increase:

```text
I/O
cache pressure
scan work
storage
maintenance
```

### VACUUM

`VACUUM` helps reclaim reusable space and maintain PostgreSQL visibility metadata.

It does not simply mean:

```text
shrink table to exact live size
```

and routine `VACUUM` is distinct from more disruptive table-rewrite operations.

### Long-running transactions

Long-running transactions can prevent old row versions from becoming removable.

You do not need the full MVCC course here. Topic 09 covers transaction/concurrency details.

---

## 44. pg_stat_statements

`pg_stat_statements` helps identify frequently executed and expensive statements at a workload level.

Typical installation:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

Availability and configuration depend on PostgreSQL deployment settings.

Useful concepts include:

```text
calls
total execution time
mean execution time
rows
I/O-related metrics where available/configured
```

### Why workload-level observability matters

Suppose:

```text
Query A = 2 seconds × 2 calls
Query B = 50 ms × 100,000 calls
```

Query B may be much more important to the workload despite looking faster per execution.

### Production lesson

Optimize the workload that matters, not merely the slowest-looking individual query.

Exact columns vary with PostgreSQL version and configuration. Verify your installed version's documentation.

---

## 45. auto_explain

> **POSTGRESQL-SPECIFIC**

`auto_explain` can automatically log execution plans for queries meeting configured criteria.

It is useful when:

```text
a query is slow in production
but
hard to reproduce manually
```

### Why it matters

Without automatic plan capture, an intermittent production problem can become:

```text
"it was slow, but now we cannot reproduce it."
```

`auto_explain` can provide evidence from the production environment itself.

### Operational caution

Logging full plans, especially with analysis/buffer details, has overhead.

Configure it deliberately.

This chapter only teaches awareness and practical purpose, not full PostgreSQL observability operations.

---

## 46. Query Timeouts

Production systems need guardrails.

Example:

```sql
SET statement_timeout = '5s';
```

This prevents a statement from running indefinitely within the session configuration.

A related operational setting is:

```sql
SET lock_timeout = '2s';
```

which limits time spent waiting for locks.

Topic 09 covers locking deeply. Here, focus on the principle:

```text
query
→ bounded resource usage
→ less risk of runaway work
```

### Why timeouts matter

Without a timeout:

```text
bad query
→ runs for a very long time
→ holds resources
→ competes with important workloads
→ operational incident
```

A timeout is not a query-tuning substitute.

It is a safety boundary.

---

## 47. GIN

> **POSTGRESQL-SPECIFIC**

GIN stands for a Generalized Inverted Index.

At this stage, think:

```text
one row value
contains
multiple searchable components
```

Typical use cases include:

```text
JSONB
arrays
full-text search
```

### Conceptual example

```sql
CREATE INDEX idx_orders_metadata_gin
ON orders
USING GIN (metadata);
```

The exact operator class affects supported operations.

### Core mental model

```text
B-tree
→ one ordered scalar key

GIN
→ searchable components inside a composite value
```

Do not reduce:

```text
GIN = JSONB only
```

It supports several multi-component/search-oriented workloads.

---

## 48. GiST

> **POSTGRESQL-SPECIFIC**

GiST is a flexible generalized search-tree framework.

Typical workloads include:

```text
ranges
geometric data
extensible search strategies
```

### Why multiple index types exist

A database needs different physical structures for different operator semantics.

For example:

```text
scalar equality/range
→ B-tree

multi-component containment/search
→ GIN

range/spatial/extensible strategies
→ GiST
```

These are broad mental models, not rigid one-to-one mappings.

Operator classes matter.

Do not turn GiST into a PostGIS-only topic.

---

## 49. BRIN

> **POSTGRESQL-SPECIFIC**

BRIN stands for Block Range Index.

A BRIN index stores compact summaries about ranges of table pages.

For time-ordered data:

```sql
CREATE INDEX idx_events_created_brin
ON events
USING BRIN (created_at);
```

### Conceptual model

Suppose physical blocks look roughly like:

```text
block 1 → 2026-01-01 ... 2026-01-02
block 2 → 2026-01-03 ... 2026-01-04
block 3 → 2026-01-05 ... 2026-01-06
```

A BRIN summary can help the engine reason:

```text
query asks for Jan 5+
→ block 1 cannot contain it
→ block 2 cannot contain it
→ block 3 may contain it
```

### BRIN is especially interesting when

- table is very large;
- values correlate with physical row order;
- query predicates use ranges;
- data is append-heavy or naturally ordered.

### BRIN vs B-tree

```text
B-tree
→ detailed key-level access path
→ often larger
→ useful for selective lookups

BRIN
→ compact page-range summaries
→ tiny compared with many detailed indexes
→ depends heavily on physical correlation
```

Do not claim BRIN is always faster.

Its strength is often:

```text
very large data
+
physical correlation
+
range filtering
+
small index footprint
```

---

## 50. Choosing an Index Type

Use this decision process:

```text
What query needs improvement?
        ↓
What predicate/order pattern exists?
        ↓
How selective is it?
        ↓
How large is the table?
        ↓
How often are reads performed?
        ↓
How often are writes performed?
        ↓
Is physical correlation important?
        ↓
Which index type fits?
        ↓
Measure before/after
```

### High-level comparison

| Type | Typical use | Strength | Trade-off |
|---|---|---|---|
| B-tree | equality/range/order | general-purpose | storage + write cost |
| GIN | JSONB/arrays/searchable multi-component values | containment/search | larger/complex structure |
| GiST | ranges/spatial/extensible search | flexible | operator/workload dependent |
| BRIN | huge physically correlated tables | very small summaries | depends on correlation |

### Decision rule

Do not start with:

```text
"Which index is best?"
```

Start with:

```text
"What does this workload need?"
```

---

## 51. Indexes During Bulk Loads

Suppose:

```text
1,000,000 rows
```

are inserted into a table with five secondary indexes.

Each inserted row may require maintenance of the relevant index structures.

Conceptually:

```text
one inserted row
→ table write
→ index A maintenance
→ index B maintenance
→ index C maintenance
...
```

### Why this matters

Bulk-load time can increase significantly when many indexes are maintained during ingestion.

### Strategies to evaluate

Depending on the workload:

```text
load into staging
→ validate
→ build/rebuild selected indexes
```

or:

```text
keep essential indexes
→ load
→ measure
```

### Do not prescribe “always drop indexes”

Dropping/rebuilding indexes also has:

```text
build cost
downtime/availability considerations
storage requirements
replication implications
```

The right strategy depends on:

```text
load size
load frequency
query traffic
index count
index build time
availability requirements
```

Benchmark the actual workload.

---

## 52. CREATE INDEX CONCURRENTLY

> **POSTGRESQL-SPECIFIC**

Example:

```sql
CREATE INDEX CONCURRENTLY idx_orders_customer_id
ON orders(customer_id);
```

The intent is to reduce interference with normal writes compared with a standard blocking index build.

### Important limitations

`CREATE INDEX CONCURRENTLY` is:

- more operationally complex;
- often slower;
- subject to special restrictions;
- not a magic “zero blocking” switch.

### Production questions

```text
How busy is the table?
Can the index build run for a long time?
What happens on failure?
Do we have monitoring?
What happens on replicas?
Can the application tolerate the build?
```

Never assume “concurrent” means:

```text
no operational risk
```

---

## 53. Analytical Engines Without Traditional B-Tree Indexes

PostgreSQL is not the architecture used by every analytical system.

For scan-heavy analytics, systems such as:

```text
DuckDB
Snowflake
BigQuery
Spark
```

can obtain strong performance through combinations of:

```text
columnar storage
vectorized execution
zone maps/data skipping
partition pruning
clustering
compression
predicate pushdown
```

Do not say:

> “DuckDB has no indexes.”

The useful distinction is:

> **These engines do not rely primarily on PostgreSQL-style B-tree indexing as their main scan-acceleration strategy for analytical workloads.**

### Why architecture matters

A row-store OLTP system often asks:

```text
Find a tiny set of rows quickly.
```

A columnar analytical engine often asks:

```text
Scan a large amount of one/few columns efficiently.
```

These workloads lead to different physical designs.

---

## 54. Zone Maps

A zone map or min/max metadata can summarize the range of values in a storage block.

Example:

```text
block 1 → id 1–100
block 2 → id 101–200
block 3 → id 201–300
```

Query:

```text
WHERE id > 250
```

Then:

```text
block 1 → skip
block 2 → skip
block 3 → inspect
```

### Core idea

```text
metadata
→ prove a block cannot contain matching values
→ skip the block
```

This is **data skipping**.

The exact mechanism differs by engine.

### Relationship to indexes

A zone map is not simply:

```text
B-tree for files
```

It is a different physical technique.

The engine can avoid work by using:

```text
storage layout
+
metadata
```

rather than a row-level ordered key structure.

---

## 55. Partition Pruning

Partition pruning is the process of avoiding partitions that cannot satisfy a query predicate.

Example:

```text
events
├── 2026-01
├── 2026-02
├── 2026-03
└── 2026-04
```

Query:

```sql
SELECT COUNT(*)
FROM events
WHERE event_time >= TIMESTAMPTZ '2026-03-01 00:00:00+00'
  AND event_time <  TIMESTAMPTZ '2026-04-01 00:00:00+00';
```

If the table is partitioned by `event_time`, unrelated partitions can be excluded.

### Mental model

```text
all partitions
    ↓
partition-key predicate
    ↓
eligible partitions
    ↓
scan only those partitions
```

This connects to Topic 07's table partitioning.

### Important caution

Partitioning only helps when:

```text
partition key
+
query predicates
+
data lifecycle
```

align.

A query without useful partition-key restriction may still touch many partitions.

---

## 56. Clustering

Clustering means physically organizing related values so that similar values tend to be stored closer together.

High-level benefit:

```text
related values close together
        ↓
better locality
        ↓
potentially better data skipping/scan efficiency
```

Exact clustering semantics vary by engine.

Examples in analytical platforms can include:

```text
cluster by customer_id
cluster by date
```

or systems that reorder/organize files or storage units around chosen columns.

### Important distinction

Clustering is a physical-layout strategy.

It is not interchangeable with:

```text
B-tree index
```

or:

```text
partitioning
```

Although all can influence physical access.

---

## 57. PostgreSQL vs DuckDB vs Warehouse Plan Thinking

| Engine/category | Common physical ideas |
|---|---|
| PostgreSQL | B-tree/other indexes, heap access, bitmap scans, join algorithms, statistics |
| DuckDB | columnar scans, vectorized execution, data skipping/zone-map-style concepts |
| Cloud warehouses | columnar storage, partition pruning, clustering, data skipping |
| Spark SQL | logical/physical plan, scans, shuffles, partitioning, joins |

### PostgreSQL

You commonly inspect:

```sql
EXPLAIN
EXPLAIN ANALYZE
EXPLAIN (ANALYZE, BUFFERS)
```

and reason about:

```text
Seq Scan
Index Scan
Hash Join
Nested Loop
Sort
Aggregate
```

### DuckDB

DuckDB provides:

```text
EXPLAIN
EXPLAIN ANALYZE
```

with analytical execution concepts such as:

```text
columnar operators
vectorized processing
filters
projection
joins
aggregations
```

Exact operator naming differs from PostgreSQL.

### Warehouses

Cloud warehouses often emphasize:

```text
columnar storage
partition pruning
clustering
data skipping
compression
distributed execution
```

### Spark

Spark exposes logical and physical plans through `EXPLAIN`.

For awareness, understand:

```text
logical plan
→ optimization
→ physical plan
→ scans/shuffles/joins
```

A shuffle is especially important in Spark because data may need to move across workers to satisfy operations such as:

```text
join
groupBy
window partitioning
```

You do not need to master Spark optimization in this chapter.

### Key principle

> **Read the plan in the vocabulary of the engine you are using.**

---

## 58. The Performance-Tuning Workflow

This is the chapter's most important operational procedure.

```text
MEASURE
   ↓
READ PLAN
   ↓
FORM HYPOTHESIS
   ↓
CHANGE ONE THING
   ↓
MEASURE AGAIN
   ↓
COMPARE
   ↓
KEEP OR REVERT
```

### Step 1 — Measure

Record:

```text
baseline runtime
row count
representative parameters
dataset scale
cache/context where possible
```

### Step 2 — Read plan

Capture:

```sql
EXPLAIN ...
```

and, when safe:

```sql
EXPLAIN (ANALYZE, BUFFERS) ...
```

### Step 3 — Form one hypothesis

Bad:

```text
"Let's add indexes until it gets faster."
```

Better:

> “The query scans the entire orders table because its predicate is selective and no matching access path exists.”

### Step 4 — Change one thing

For example:

```sql
CREATE INDEX ...
```

### Step 5 — Measure again

Capture:

```text
runtime
plan
rows
buffers
```

### Step 6 — Compare

Ask:

```text
Did the plan change?
Did the bottleneck move?
Did runtime improve?
Did resource usage improve?
Is the result still correct?
```

### Step 7 — Keep or revert

An optimization is not successful merely because:

```text
one test execution became faster
```

It should improve the relevant workload while preserving correctness and acceptable operational cost.

---

## 59. Production Performance Patterns

### Pattern 1 — Selective customer lookup

```text
Query:
WHERE customer_id = ?

Workload:
frequent exact lookup

Expected access pattern:
highly selective B-tree lookup

Potential index:
(customer_id)

Why:
few matching rows

Trade-offs:
write/storage cost

How to verify:
EXPLAIN ANALYZE

What could invalidate:
small table or low selectivity
```

---

### Pattern 2 — Date-range events query

```text
Query:
WHERE event_time >= start
  AND event_time < end

Workload:
time-bounded event analytics

Expected access pattern:
range access or partition pruning

Potential index:
B-tree(event_time)
or
BRIN(event_time) for huge physically correlated tables

Why:
range predicate

Trade-offs:
B-tree detail vs BRIN compactness

How to verify:
plan + buffers + timing

What could invalidate:
weak physical correlation or very broad ranges
```

---

### Pattern 3 — Top-N recent orders

```sql
SELECT
    order_id,
    customer_id,
    created_at,
    amount
FROM orders
WHERE customer_id = 123
ORDER BY created_at DESC
LIMIT 100;
```

Candidate:

```sql
CREATE INDEX idx_orders_customer_created
ON orders(customer_id, created_at DESC);
```

Reason:

```text
customer equality
+
recent ordering
+
LIMIT
```

Validate with actual data.

---

### Pattern 4 — Large event table with BRIN

Candidate:

```sql
CREATE INDEX idx_events_time_brin
ON events USING BRIN(event_time);
```

Workload assumptions:

```text
huge table
time-ordered ingestion
range queries
```

Invalidation:

```text
event_time poorly correlated with physical order
```

---

### Pattern 5 — Partial index for pending jobs

```sql
CREATE INDEX idx_jobs_pending
ON jobs(created_at)
WHERE status = 'pending';
```

Good when:

```text
pending rows are a small, hot subset
```

---

### Pattern 6 — Expression index for normalized email

```sql
CREATE INDEX idx_users_lower_email
ON users(LOWER(email));
```

Query:

```sql
WHERE LOWER(email) = 'alice@example.com'
```

---

### Pattern 7 — Composite index for customer + timestamp

```sql
CREATE INDEX idx_orders_customer_created
ON orders(customer_id, created_at DESC);
```

Good for:

```text
customer history
recent rows
customer-scoped time ranges
```

---

### Pattern 8 — Covering index

```sql
CREATE INDEX idx_orders_customer_cover
ON orders(customer_id, created_at DESC)
INCLUDE (amount, status);
```

Potential benefit:

```text
less heap access
possible index-only scan
```

Trade-off:

```text
larger index
more maintenance
```

---

### Pattern 9 — Bulk-load and rebuild strategy

Workload:

```text
large periodic batch
```

Question:

```text
Are many secondary indexes worth maintaining during the load?
```

Candidate strategy:

```text
staging load
→ transform/validate
→ build required indexes
→ publish
```

But benchmark against:

```text
keep indexes during load
```

because rebuilds also have a cost.

---

### Pattern 10 — Bad estimate caused by stale statistics

Symptom:

```text
estimated rows = 50
actual rows = 500,000
```

Hypothesis:

```text
statistics stale
```

Test:

```sql
ANALYZE relevant_table;
```

Then re-run:

```sql
EXPLAIN (ANALYZE, BUFFERS) ...
```

Conclusion must be based on before/after evidence.

---

## 60. Debugging Slow Queries

Use this sequence:

```text
1. Reproduce
2. Baseline
3. EXPLAIN
4. EXPLAIN ANALYZE safely
5. BUFFERS when useful
6. Read leaf → parent
7. Compare estimates/actuals
8. Inspect loops
9. Inspect scan choice
10. Inspect joins
11. Inspect sort/aggregate work
12. Inspect statistics
13. Inspect predicate shape
14. Inspect indexes
15. Change one thing
16. Re-measure
17. Re-check correctness
```

### Questions to ask

```text
Is too much data being scanned?

Is the filter selective?

Did the optimizer estimate the cardinality correctly?

Is a join multiplying work?

Is a nested loop repeating an operation too many times?

Is a sort expensive?

Is a hash operation memory-heavy?

Is the query forcing unnecessary casts/functions?

Is the index physically appropriate?

Is the index being maintained at a high write cost?
```

The goal is to identify the bottleneck, not to collect indexes.

---

## 61. Assertion and Validation Queries

Performance optimization must preserve correctness.

### Result-set equivalence

When changing a query, compare old and new results in a controlled way.

For exact row-set equivalence, you can compare:

```sql
(
    SELECT ...
    FROM ...

    EXCEPT

    SELECT ...
    FROM ...
)
UNION ALL
(
    SELECT ...
    FROM ...

    EXCEPT

    SELECT ...
    FROM ...
);
```

Expected:

```text
zero rows
```

For duplicate-preserving semantics, consider the required comparison semantics rather than blindly using `EXCEPT`.

### Row-count check

```sql
SELECT COUNT(*)
FROM (
    SELECT ...
) AS result;
```

Compare with the baseline.

### Duplicate check

```sql
SELECT
    customer_id,
    COUNT(*)
FROM result_table
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

### Aggregate reconciliation

```sql
SELECT
    SUM(amount)
FROM result_table;
```

Compare against the known baseline.

### Core principle

> **A faster query that changes the answer is not a successful optimization.**

---

## 62. Common Mistakes

### Mistake 1 — “Seq Scan is bad.”

**Example:**

```text
Seq Scan on 20-row table
```

**Why it fails:** The table is tiny.

**Correct approach:** Evaluate table size and selectivity.

**Lesson:** A plan node is not good or bad in isolation.

---

### Mistake 2 — “Every query should use an index.”

**Why risky:** Many queries legitimately benefit from sequential scans.

**Correct:** Let workload evidence and the optimizer guide the decision.

---

### Mistake 3 — Adding indexes without measuring

**Why:** Creates storage/write cost without proving benefit.

**Correct:** Establish a baseline and test one index at a time.

---

### Mistake 4 — Indexing every column

**Why:** Too many indexes increase:

```text
write overhead
storage
maintenance
bulk-load time
```

**Correct:** Index access paths that correspond to real workloads.

---

### Mistake 5 — Ignoring write cost

A read speedup may be paid for on every insert/update/delete.

---

### Mistake 6 — Wrong composite-column order

Index:

```text
(created_at, customer_id)
```

may behave very differently from:

```text
(customer_id, created_at)
```

for customer-scoped time queries.

---

### Mistake 7 — Misunderstanding covering indexes

`INCLUDE` can make an index more complete for a query, but it does not guarantee an index-only scan.

---

### Mistake 8 — Partial index predicate does not match workload

An index:

```sql
WHERE status = 'pending'
```

does not help an unrelated query on:

```text
status = 'completed'
```

just because the table is the same.

---

### Mistake 9 — Expression mismatch

An index on:

```sql
LOWER(email)
```

is relevant to queries using that expression.

Do not assume it automatically substitutes for every email predicate.

---

### Mistake 10 — Ignoring selectivity

A predicate matching most of a huge table may still favor a sequential scan.

---

### Mistake 11 — Ignoring stale statistics

A plan problem may be a statistics problem, not an index problem.

---

### Mistake 12 — Trusting estimated rows blindly

Always compare estimates with actuals when safe.

---

### Mistake 13 — Trusting one runtime measurement

Performance varies with:

```text
cache state
concurrency
data distribution
background activity
parameter values
```

Use representative repeated measurements.

---

### Mistake 14 — Running EXPLAIN ANALYZE on dangerous writes

`EXPLAIN ANALYZE` executes the statement.

Use controlled transactions for learning and be very cautious in production.

---

### Mistake 15 — Ignoring loops

A tiny node executed:

```text
500,000 times
```

can dominate the workload.

---

### Mistake 16 — Looking only at the root node

Read the full tree.

---

### Mistake 17 — Ignoring BUFFERS when I/O matters

Runtime alone may not explain why the query is spending time.

---

### Mistake 18 — Changing five things at once

You lose causal attribution.

---

### Mistake 19 — Assuming ANALYZE fixes every problem

Statistics are one piece of the optimizer's information.

---

### Mistake 20 — Ignoring bloat

Physical growth can create unnecessary I/O and storage pressure.

---

### Mistake 21 — Overusing covering indexes

`INCLUDE` increases index size.

---

### Mistake 22 — Overusing partial indexes

If the predicate distribution changes, the index may become less useful.

---

### Mistake 23 — Choosing BRIN without physical correlation

BRIN is strongest when values correlate with physical row order.

---

### Mistake 24 — Treating BRIN as a B-tree replacement

They solve different access-pattern problems.

---

### Mistake 25 — Assuming GIN/GiST/BRIN each have one rigid purpose

Operator class and workload matter.

---

### Mistake 26 — Assuming analytical engines need PostgreSQL-style indexes

Columnar/data-skipping architectures can be effective without primarily using B-tree indexes.

---

### Mistake 27 — Tuning without a hypothesis

“Try this index” is not an engineering explanation.

---

### Mistake 28 — Optimizing before checking correctness

A faster incorrect result is a failure.

---

### Mistake 29 — Overfitting to one dataset

A plan that improves one tiny fixture may not improve production-scale data.

---

## 63. Beginner Practice

### Exercise 1 — What is an index?

**Objective:** Understand access paths.

**Sample SQL:**

```sql
CREATE TABLE customers (
    customer_id BIGINT,
    email TEXT
);

INSERT INTO customers VALUES
    (1, 'a@example.com'),
    (2, 'b@example.com'),
    (3, 'c@example.com');
```

**Task:** Explain how a B-tree on `customer_id` changes the possible access path.

**Expected reasoning:** The index gives the optimizer a structured way to find matching IDs instead of scanning every table row.

---

### Exercise 2 — Index cost

Create:

```sql
CREATE INDEX idx_customers_email
ON customers(email);
```

List three benefits and three costs.

**Solution points:**

```text
benefits:
selective email lookup
possible ordering support
unique enforcement if unique

costs:
storage
write maintenance
maintenance/bulk-load work
```

---

### Exercise 3 — B-tree equality

**Sample query:**

```sql
SELECT *
FROM customers
WHERE customer_id = 2;
```

**Task:** Predict why a B-tree might help.

**Solution:** Equality on a suitable indexed key is a natural B-tree access pattern.

---

### Exercise 4 — Range lookup

Use:

```sql
SELECT *
FROM orders
WHERE created_at >= TIMESTAMPTZ '2026-01-01'
  AND created_at <  TIMESTAMPTZ '2026-02-01';
```

Explain why the half-open range is useful.

---

### Exercise 5 — `EXPLAIN`

Run:

```sql
EXPLAIN
SELECT *
FROM customers
WHERE customer_id = 2;
```

Record:

```text
node
estimated rows
cost
width
```

---

### Exercise 6 — `EXPLAIN ANALYZE`

Run:

```sql
EXPLAIN ANALYZE
SELECT *
FROM customers
WHERE customer_id = 2;
```

Compare:

```text
estimated rows
actual rows
execution time
```

---

### Exercise 7 — Estimated vs actual

Create a simulated plan:

```text
Seq Scan on customers
  estimated rows = 10
  actual rows    = 9
```

State whether the estimate appears broadly reasonable and why.

---

### Exercise 8 — Selectivity

Compare:

```sql
WHERE customer_id = 2
```

with:

```sql
WHERE country = 'IN'
```

Explain why the second may be less selective.

---

### Exercise 9 — Seq Scan is not bad

Create a five-row table and predict why PostgreSQL may prefer a sequential scan.

---

### Exercise 10 — Read a plan tree

> **SIMULATED PLAN**

```text
Aggregate
└── Seq Scan on orders
```

Task:

```text
What runs first?
What is the root?
What does the aggregate consume?
```

**Solution:**

```text
Seq Scan
→ Aggregate
→ final result
```

---

## 64. Intermediate Practice

### Exercise 1 — Composite index

For:

```sql
SELECT *
FROM orders
WHERE customer_id = 123
  AND created_at >= TIMESTAMPTZ '2026-01-01'
ORDER BY created_at DESC;
```

propose:

```sql
(customer_id, created_at DESC)
```

Then explain the decision.

---

### Exercise 2 — Reverse column order

Compare:

```text
(customer_id, created_at)
```

with:

```text
(created_at, customer_id)
```

Explain which query patterns naturally align with each.

---

### Exercise 3 — Covering index

Create:

```sql
CREATE INDEX idx_orders_customer_cover
ON orders(customer_id, created_at DESC)
INCLUDE (amount, status);
```

Task:

```text
What are key columns?
What are included columns?
Why might an index-only scan become possible?
```

---

### Exercise 4 — Partial index

Create:

```sql
CREATE INDEX idx_jobs_pending
ON jobs(created_at)
WHERE status = 'pending';
```

Then write:

```sql
SELECT *
FROM jobs
WHERE status = 'pending'
ORDER BY created_at
LIMIT 100;
```

Explain why the predicate aligns.

---

### Exercise 5 — Expression index

Create:

```sql
CREATE INDEX idx_users_lower_email
ON users(LOWER(email));
```

Use:

```sql
WHERE LOWER(email) = 'alice@example.com'
```

Explain why the expression matters.

---

### Exercise 6 — Bitmap scans

> **SIMULATED PLAN**

```text
Bitmap Heap Scan on orders
  Recheck Cond: (customer_id = 123)
  -> Bitmap Index Scan on idx_orders_customer_id
```

Identify:

```text
index phase
heap phase
```

---

### Exercise 7 — Join strategy

> **SIMULATED PLAN**

```text
Nested Loop
├── Seq Scan on customers
└── Index Scan on orders
```

Task: Give one workload where this is a good plan and one where it may be dangerous.

---

### Exercise 8 — `HashAggregate`

Explain why:

```text
HashAggregate
```

might need substantial memory for many distinct groups.

---

### Exercise 9 — `GroupAggregate`

Given:

```text
GroupAggregate
└── Sort
```

explain why the sort may be part of the aggregate's cost.

---

### Exercise 10 — BUFFERS

Record:

```text
shared hit
shared read
```

for a representative query and explain what each suggests.

---

## 65. Advanced Practice

### Exercise 1 — Bad estimate

> **SIMULATED PLAN**

```text
Nested Loop
  estimated outer rows = 100
  actual outer rows    = 2,000,000
```

Explain:

```text
why the mismatch matters
which cost assumption can become wrong
what evidence you would inspect next
```

---

### Exercise 2 — Statistics

Load a large amount of new data with a changed distribution.

Run:

```sql
EXPLAIN ANALYZE ...
```

Then:

```sql
ANALYZE relevant_table;
```

Re-run and compare.

---

### Exercise 3 — BRIN

Build a large time-ordered event table with `generate_series()`.

Create:

```text
BRIN(event_time)
B-tree(event_time)
```

Compare:

```text
index size
plan
runtime
buffer behavior
```

Do not declare a universal winner.

---

### Exercise 4 — GIN

Create a JSONB column and a GIN index.

Test a representative containment/search workload.

Explain why GIN is appropriate to a multi-component value.

---

### Exercise 5 — GiST

Design a range-oriented example.

Explain why a GiST-style index can be a more natural fit than assuming every workload should use B-tree.

---

### Exercise 6 — Bloat

Create a table, perform repeated updates, and investigate foundational signs of dead-tuple growth.

Explain what `VACUUM` is expected to accomplish.

---

### Exercise 7 — `pg_stat_statements`

Use it to identify high-total-time queries.

Compare:

```text
per-call latency
vs
total workload impact
```

---

### Exercise 8 — `auto_explain`

Design a configuration experiment that captures slow plans.

Document:

```text
threshold
expected logging
operational overhead
```

---

### Exercise 9 — Concurrent index creation

Design a safe plan for adding an index to a busy production table using:

```sql
CREATE INDEX CONCURRENTLY ...
```

State what risks remain.

---

### Exercise 10 — Analytical-engine comparison

Run the same scan-heavy analytical aggregation in PostgreSQL and DuckDB.

Compare:

```text
physical model
plan vocabulary
scan strategy
data skipping/columnar behavior
```

---

### Exercise 11 — Hypothesis-driven tuning

Write:

```text
baseline
hypothesis
single change
after evidence
decision
```

for a real or simulated slow query.

---

### Exercise 12 — Workload-level decision

Given:

```text
10 slow queries
100,000 fast queries
```

determine which one deserves investigation first based on total workload impact.

---

## 66. Plan-Reading Drills

The following plans are explicitly **simulated**. They are not claimed to be actual output from a PostgreSQL execution.

For each drill:

```text
1. identify the root operation;
2. identify the first-executed leaf nodes;
3. compare estimated and actual rows;
4. inspect loops;
5. identify the likely expensive area;
6. form one hypothesis;
7. state what you would test next.
```

### Drill 1 — Seq Scan

> **SIMULATED PLAN**

```text
Seq Scan on customers
  cost=0.00..2500.00 rows=50000 width=100
  actual time=0.020..21.500 rows=48000 loops=1
```

**Questions:**

```text
Root node?
Estimated rows?
Actual rows?
Is this necessarily bad?
```

**Solution:**

```text
root = Seq Scan
estimate = 50,000
actual = 48,000
estimate is reasonably close
not necessarily bad
```

Hypothesis:

```text
If most rows are needed, sequential access may be reasonable.
```

---

### Drill 2 — Index Scan

> **SIMULATED PLAN**

```text
Index Scan using idx_orders_customer_id on orders
  cost=0.42..20.10 rows=8 width=80
  actual time=0.020..0.080 rows=6 loops=1
  Index Cond: (customer_id = 123)
```

**Solution:**

```text
index access
high selectivity
estimate broadly close
small output
```

Potential conclusion:

```text
The index is providing a selective access path.
```

---

### Drill 3 — Index Only Scan

> **SIMULATED PLAN**

```text
Index Only Scan using idx_orders_customer_cover on orders
  cost=0.42..8.20 rows=100 width=32
  actual time=0.030..0.090 rows=98 loops=1
  Heap Fetches: 4
```

**Questions:**

```text
Why is it called index-only?
Why are there still heap fetches?
```

**Solution:**

```text
needed query values can be obtained from the index
but visibility checks still required some heap access
```

---

### Drill 4 — Bitmap

> **SIMULATED PLAN**

```text
Bitmap Heap Scan on orders
  cost=100.00..3000.00 rows=20000 width=80
  actual time=2.000..12.000 rows=18000 loops=1
  Recheck Cond: (customer_id = 123)

  -> Bitmap Index Scan on idx_orders_customer_id
       cost=0.00..95.00 rows=20000 width=0
       actual time=1.500..1.500 rows=18000 loops=1
```

**Solution:**

```text
bitmap index identifies candidates
bitmap heap scan visits table pages
actual rows close to estimate
```

---

### Drill 5 — Nested Loop estimate failure

> **SIMULATED PLAN**

```text
Nested Loop
  actual time=0.200..9000.000 rows=1500000 loops=1

  -> Seq Scan on customers
       estimated rows=100
       actual rows=500000

  -> Index Scan on orders
       estimated rows=5
       actual rows=3
       loops=500000
```

**Solution:**

The major issue is:

```text
outer estimate = 100
actual outer    = 500000
```

The inner lookup itself is not necessarily terrible.

The problem is repetition:

```text
500,000 loops
```

Hypothesis:

```text
bad cardinality estimate caused an unsuitable nested-loop choice
```

Next test:

```text
statistics
query predicates
alternative join strategies
```

---

### Drill 6 — Hash Join

> **SIMULATED PLAN**

```text
Hash Join
  Hash Cond: (orders.customer_id = customers.customer_id)

  -> Seq Scan on orders
       estimated rows=1000000
       actual rows=980000

  -> Hash
       -> Seq Scan on customers
            estimated rows=50000
            actual rows=50000
```

**Solution:**

Estimates are broadly aligned.

The hash join may be reasonable for the equality join.

Next question:

```text
memory/build-side cost
```

---

### Drill 7 — Merge Join

> **SIMULATED PLAN**

```text
Merge Join
  Merge Cond: (a.customer_id = b.customer_id)

  -> Sort
       Sort Key: a.customer_id
       actual time=100..300

  -> Sort
       Sort Key: b.customer_id
       actual time=80..220
```

**Solution:**

The join requires ordered input.

The child sorts may dominate execution work.

Hypothesis:

```text
sorting the inputs is the important cost
```

Potential experiment:

```text
access paths that already provide useful ordering
```

---

### Drill 8 — HashAggregate

> **SIMULATED PLAN**

```text
HashAggregate
  Group Key: customer_id
  actual rows=1000000
  Peak Memory Usage: 500000 kB
```

**Solution:**

There are many groups.

Potential concerns:

```text
memory
spilling
cardinality
```

Next test:

```text
Can the input be safely reduced?
Is the group cardinality expected?
```

---

### Drill 9 — GroupAggregate

> **SIMULATED PLAN**

```text
GroupAggregate
  Group Key: customer_id
  -> Sort
       Sort Key: customer_id
       actual time=500..3000
```

**Solution:**

The sort may be the dominant cost.

The aggregate depends on ordered input.

---

### Drill 10 — Bad statistics

> **SIMULATED PLAN**

```text
Index Scan
  estimated rows=20
  actual rows=900000
```

**Solution:**

The estimate is badly wrong.

Investigate:

```text
statistics freshness
distribution changes
data correlation
predicate selectivity
```

Potential action:

```sql
ANALYZE table_name;
```

Then re-measure.

---

## 67. Debugging Challenges

### Challenge 1 — Index exists but Seq Scan is chosen

**Symptoms:** A developer says, “The index isn't working.”

**Evidence:**

```text
table = 50 rows
Seq Scan chosen
```

**Diagnosis:** Table is tiny.

**Hypothesis:** Sequential access is cheaper.

**Correction:** No automatic correction is required.

**Re-measurement:** Verify with `EXPLAIN`.

**Production lesson:** Small tables can legitimately use Seq Scan.

---

### Challenge 2 — Low selectivity

**Symptoms:** An index on `status` exists, but:

```text
status='active'
```

still uses Seq Scan.

**Evidence:**

```text
90% of rows are active
```

**Diagnosis:** Low selectivity.

**Hypothesis:** Scanning the table is cheaper.

**Correction:** Do not add another identical low-selectivity index without evidence.

**Lesson:** Selectivity matters.

---

### Challenge 3 — Function blocks efficient access

**Broken:**

```sql
WHERE DATE(created_at) = DATE '2026-03-01'
```

**Evidence:** Existing B-tree on `created_at`.

**Diagnosis:** Query transforms the column.

**Hypothesis:** Half-open range can align better with the base index.

**Correction:**

```sql
WHERE created_at >= TIMESTAMPTZ '2026-03-01'
  AND created_at <  TIMESTAMPTZ '2026-03-02'
```

**Re-measure:** Compare plans.

**Lesson:** Query shape matters.

---

### Challenge 4 — Wrong composite order

**Workload:**

```text
WHERE customer_id = ?
ORDER BY created_at DESC
```

**Existing index:**

```text
(created_at, customer_id)
```

**Diagnosis:** The leading key does not align naturally with the customer-scoped access pattern.

**Hypothesis:** Reordering keys may produce a better access path.

**Correction candidate:**

```text
(customer_id, created_at DESC)
```

**Lesson:** Composite index order encodes a workload.

---

### Challenge 5 — Bad row estimate

**Evidence:**

```text
estimated 100
actual 2,000,000
```

**Diagnosis:** Cardinality estimate failure.

**Investigation:**

```text
statistics
distribution
correlated predicates
query shape
```

**Correction candidate:** `ANALYZE`, rewrite, or change index/query design depending evidence.

**Lesson:** Explain the mechanism; do not automatically prescribe `ANALYZE`.

---

### Challenge 6 — Expensive nested loop

**Evidence:**

```text
outer loops = 5,000,000
inner index scan loops = 5,000,000
```

**Diagnosis:** Repeated inner work.

**Hypothesis:** A different join strategy may be cheaper at actual cardinality.

**Correction:** Investigate estimates and compare a controlled alternative.

**Lesson:** Loops expose multiplicative work.

---

### Challenge 7 — Large sort

**Evidence:**

```text
Sort
large actual rows
significant runtime
```

**Diagnosis:** Sorting is expensive.

**Investigation:**

```text
Does another access path provide order?
Is there an ORDER BY + LIMIT pattern?
Can the query reduce rows before sorting?
```

**Lesson:** Do not just add an index; understand the required order.

---

### Challenge 8 — Heap fetches despite covering index

**Evidence:**

```text
Index Only Scan
Heap Fetches: 1,000,000
```

**Diagnosis:** Index-only access still requires visibility checks/heap access.

**Investigation:** Inspect table maintenance and query shape.

**Lesson:** Covering index is not a guarantee of zero heap access.

---

### Challenge 9 — BRIN performs poorly

**Evidence:**

```text
BRIN exists
range query remains expensive
```

**Diagnosis:** Physical correlation may be weak.

**Investigation:**

```text
How is event_time distributed physically?
Is ingestion interleaved?
Are old and new timestamps mixed?
```

**Correction:** Compare with a B-tree or improve physical layout if justified.

**Lesson:** BRIN depends on physical correlation.

---

### Challenge 10 — Stale statistics

**Symptoms:**

```text
query was fast
large load occurred
query plan changed badly
```

**Hypothesis:** Statistics no longer represent distribution.

**Correction candidate:**

```sql
ANALYZE table_name;
```

**Re-measure:** Compare plan and actual runtime.

---

## 68. Performance-Tuning Challenges

For every case, use:

```text
measure
→ inspect plan
→ state hypothesis
→ change one thing
→ measure again
→ explain result
```

### Case 1 — Slow customer lookup

Workload:

```text
customer_id equality lookup
large table
few rows expected
```

Candidate:

```text
B-tree(customer_id)
```

Validate:

```text
Seq Scan vs Index Scan
actual rows
buffers
runtime
```

---

### Case 2 — Slow date-range event query

Workload:

```text
huge events table
narrow time range
```

Candidates:

```text
B-tree(event_time)
BRIN(event_time)
partition pruning
```

Do not assume which one wins.

---

### Case 3 — Slow top-N recent orders

Query:

```sql
SELECT *
FROM orders
WHERE customer_id = 123
ORDER BY created_at DESC
LIMIT 50;
```

Candidate:

```text
(customer_id, created_at DESC)
```

Measure whether the access path reduces sorting/row scanning.

---

### Case 4 — Pending-job queue

Workload:

```text
status='pending'
ORDER BY created_at
LIMIT 100
```

Candidate:

```sql
CREATE INDEX idx_jobs_pending_created
ON jobs(created_at)
WHERE status = 'pending';
```

Measure representative pending workload.

---

### Case 5 — JSONB lookup

Workload:

```sql
WHERE metadata @> '{"campaign_id":"C123"}'
```

Candidate:

```text
GIN(metadata)
```

Confirm operator/index compatibility for the exact workload.

---

### Case 6 — Time-ordered event table

Workload:

```text
hundreds of millions of events
append-heavy
time ranges
```

Compare:

```text
BRIN
vs
B-tree
```

Measure:

```text
index size
plan
buffers
runtime
```

---

### Case 7 — Large join with bad estimates

Observed:

```text
Nested Loop
unexpectedly huge outer relation
```

Investigate:

```text
statistics
join predicates
data distribution
alternative join strategies
```

---

### Case 8 — Query slowed after adding indexes

Possible explanation:

```text
optimizer changed plan
or
write/maintenance contention increased
or
new index altered cost estimates
```

Do not assume:

```text
more indexes = faster reads
```

Investigate workload-wide impact.

---

### Case 9 — Bulk load became much slower

Compare:

```text
load without secondary indexes
vs
load with multiple indexes
```

Record:

```text
insert time
index build time
post-load query time
```

Then evaluate total pipeline cost.

---

### Case 10 — Fast in test, slow at production scale

Possible causes:

```text
larger data
different distribution
different cache state
different concurrency
different statistics
different parameter values
different storage
```

Reproduce the production shape as closely as practical.

---

## 69. Production Case Study

### Scenario

A subscription company has:

```text
customers
subscriptions
orders
payments
events
```

Production scale:

```text
tens of millions of orders
hundreds of millions of events
frequent customer lookups
time-range event queries
pending-payment queue
recent-order lookups
```

Problems:

```text
1. recent orders query is slow
2. event-range query scans too much data
3. pending-payment queue is slow
4. a join suddenly chooses an expensive Nested Loop
5. planner estimates are badly wrong
6. bulk load became much slower after indexes were added
```

### Step 1 — Identify workload patterns

Create a workload matrix:

| Workload | Predicate | Order | Data shape | Candidate |
|---|---|---|---|---|
| Recent orders | customer_id | created_at DESC | few rows | composite B-tree |
| Event range | event_time range | optional | huge | BRIN/B-tree/partitioning |
| Pending payments | status pending | created_at | small hot subset | partial index |
| Customer lookup | customer_id | none | selective | B-tree |
| Large join | customer_id | none | high cardinality | statistics + join plan review |

---

### Step 2 — Record baseline

For each query record:

```text
query text/parameter class
runtime
row count
EXPLAIN
EXPLAIN ANALYZE
BUFFERS
```

Do not optimize yet.

---

### Step 3 — Read the plans

#### Recent orders simulated baseline

> **SIMULATED**

```text
Limit
└── Sort
    └── Seq Scan on orders
         Filter: (customer_id = 123)
         estimated rows = 500000
         actual rows    = 42
```

### Interpretation

The query expects only:

```text
42 actual rows
```

but the plan scans a much larger relation.

Hypothesis:

```text
Selective customer lookup lacks a suitable access path.
```

Candidate:

```sql
CREATE INDEX idx_orders_customer_created
ON orders(customer_id, created_at DESC);
```

---

### Step 4 — Change one thing

Create only the candidate index.

Do not simultaneously:

```text
rewrite SQL
+
change statistics
+
change memory
+
change five indexes
```

That would destroy causal attribution.

---

### Step 5 — Re-measure

> **SIMULATED AFTER PLAN**

```text
Limit
└── Index Scan using idx_orders_customer_created on orders
     Index Cond: (customer_id = 123)
```

Then compare:

| Metric | Before | After |
|---|---:|---:|
| Execution time | 180 ms | 8 ms |
| Main scan | Seq Scan | Index Scan |
| Actual rows | 42 | 42 |
| Sort | present | reduced/removed |
| Correctness | same result | same result |

This example is simulated and must be validated with actual execution before making a production decision.

---

### Step 6 — Event range query

Suppose:

```sql
SELECT
    COUNT(*)
FROM events
WHERE event_time >= TIMESTAMPTZ '2026-03-01'
  AND event_time <  TIMESTAMPTZ '2026-04-01';
```

Baseline:

> **SIMULATED**

```text
Seq Scan on events
estimated rows = 5,000,000
actual rows    = 5,200,000
```

If this month is genuinely a narrow fraction of a huge table, investigate:

```text
B-tree(event_time)
BRIN(event_time)
partitioning by event_time
```

The right choice depends on:

```text
table scale
physical correlation
query frequency
write pattern
lifecycle
```

---

### Step 7 — Pending-payment queue

Query:

```sql
SELECT
    payment_id,
    order_id,
    created_at
FROM payments
WHERE status = 'pending'
ORDER BY created_at
LIMIT 100;
```

Candidate:

```sql
CREATE INDEX idx_payments_pending_created
ON payments(created_at)
WHERE status = 'pending';
```

Index decision:

```text
Query pattern:
hot pending subset

Predicate:
status = 'pending'

Ordering:
created_at

Expected selectivity:
small subset

Table size:
large

Read frequency:
high

Write frequency:
high

Candidate index:
partial(created_at) WHERE status='pending'

Trade-off:
write cost for pending rows + maintenance
```

Measure before/after.

---

### Step 8 — Join suddenly uses Nested Loop

Observed:

> **SIMULATED**

```text
Nested Loop
├── Seq Scan on customers
│   estimated rows = 1000
│   actual rows    = 1000000
└── Index Scan on orders
    loops          = 1000000
```

Diagnosis:

```text
outer relation is much larger than expected
```

Hypotheses:

```text
stale statistics
data-distribution change
predicate selectivity changed
```

First diagnostic action:

```sql
ANALYZE customers;
```

Then re-measure.

If the estimate improves but the plan remains problematic, continue the investigation.

Do not force a join type merely because the current plan is slow.

---

### Step 9 — Bulk load slowed after indexes were added

Compare:

```text
pipeline A:
load → query

pipeline B:
load with multiple secondary indexes → query
```

Measure:

```text
load duration
index build/rebuild time
post-load query performance
```

Possible conclusion:

```text
an index that improves interactive reads
may increase batch-load cost
```

The production choice should consider total workload value.

---

### Step 10 — Verify correctness

Before accepting any optimization:

```text
row counts
aggregates
duplicate checks
record samples
EXCEPT-based result comparison where semantics allow
```

### Final production design

A plausible final state could be:

```text
customer lookups
→ selective B-tree

recent orders
→ composite customer + timestamp index

pending payments
→ partial index

large time-ordered events
→ BRIN or partitioning depending measured workload

bad estimates
→ statistics maintenance / query redesign

bulk load
→ carefully managed index strategy

all changes
→ measured and validated
```

This is deliberately not a universal prescription.

The production engineer's job is to document:

```text
baseline
hypothesis
change
evidence
trade-off
final decision
```

---

## 70. Interview Questions

### 1. What is an index?

**Concise answer:** An index is a separate data structure that provides an alternative access path for locating data efficiently.

**Deeper explanation:** The optimizer can choose the index path when its estimated cost is lower than alternatives such as a sequential scan.

**SQL example:**

```sql
CREATE INDEX idx_orders_customer_id
ON orders(customer_id);
```

**Likely follow-up:** Why doesn't PostgreSQL always use it?

**Common mistake:** Saying an index replaces the table.

---

### 2. Why can an index improve reads?

**Concise answer:** It can locate a selective subset of rows without scanning the entire table.

**Deeper:** B-tree ordering supports efficient equality and range navigation.

**Example:**

```sql
WHERE customer_id = 123
```

**Follow-up:** What if 90% of rows match?

**Common mistake:** Ignoring selectivity.

---

### 3. What are index costs?

**Concise answer:** Storage, write maintenance, and operational/maintenance overhead.

**Deeper:** Inserts/updates/deletes may need index maintenance, and large indexes affect bulk loads and storage.

**Follow-up:** Would you index every column?

**Common mistake:** Treating indexes as free.

---

### 4. What is a B-tree?

**Concise answer:** PostgreSQL's general-purpose ordered index structure.

**Deeper:** It supports equality, ranges, ordering, and uniqueness workloads.

**Follow-up:** When might a sequential scan beat a B-tree?

**Common mistake:** Saying B-tree is optimal for every workload.

---

### 5. When is a sequential scan better?

**Concise answer:** When the table is small or a large fraction of rows must be read.

**Deeper:** Sequential page access can be cheaper than random heap fetches through an index.

**Follow-up:** What evidence would you inspect?

**Common mistake:** Calling every Seq Scan a problem.

---

### 6. What is EXPLAIN?

**Concise answer:** It shows the optimizer's estimated execution plan.

**Deeper:** It provides node types, costs, estimated rows, width, and plan relationships.

**Example:**

```sql
EXPLAIN
SELECT *
FROM orders
WHERE customer_id = 123;
```

**Common mistake:** Treating `cost` as milliseconds.

---

### 7. What is EXPLAIN ANALYZE?

**Concise answer:** It executes the query and reports actual execution information.

**Deeper:** It lets you compare estimates against actual rows, timing, and loops.

**Common mistake:** Forgetting that it executes modifications.

---

### 8. What is BUFFERS?

**Concise answer:** It adds buffer/I/O evidence to an execution analysis.

**Example:**

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...
```

**Follow-up:** What is the difference between hit and read?

**Common mistake:** Treating buffers as a direct time metric.

---

### 9. How do you read a plan?

**Concise answer:** Read it as a tree from leaf nodes toward the root, comparing rows, loops, time, and resource evidence.

**Deeper:** Parent nodes consume child output; many bottlenecks originate lower in the tree.

**Follow-up:** Why are loops important?

---

### 10. Why read from the inside out?

**Concise answer:** Child nodes produce the data consumed by parent nodes.

**Example:**

```text
Seq Scan
→ Hash
→ Hash Join
→ Aggregate
```

**Common mistake:** Looking only at the root node.

---

### 11. What does an estimated/actual row mismatch mean?

**Concise answer:** It indicates the optimizer's cardinality estimate differs from observed execution.

**Deeper:** Large errors can distort cost calculations and plan choices.

**Common mistake:** Claiming every mismatch means the optimizer is broken.

---

### 12. What is a Seq Scan?

**Answer:** A sequential table scan that evaluates rows as it reads them.

**Follow-up:** When is it appropriate?

---

### 13. What is an Index Scan?

**Answer:** An index is used to locate matching tuples, followed by heap access as needed.

**Follow-up:** How does this differ from index-only scan?

---

### 14. What is an Index Only Scan?

**Answer:** PostgreSQL can satisfy the required columns from the index while minimizing heap access, subject to visibility information.

**Common mistake:** Saying it never touches the heap.

---

### 15. What is a Bitmap Index Scan?

**Answer:** It uses an index to build a bitmap of candidate table locations.

**Follow-up:** What node often follows it?

---

### 16. What is a Bitmap Heap Scan?

**Answer:** It visits heap pages identified by the bitmap and retrieves/rechecks rows.

---

### 17. What is a Nested Loop?

**Answer:** For each outer row, PostgreSQL evaluates the inner side.

**Follow-up:** When is it good?

**Common mistake:** Saying Nested Loop is always bad.

---

### 18. What is a Hash Join?

**Answer:** It builds a hash structure for one input and probes it with the other, typically for equality joins.

**Follow-up:** What if memory is insufficient?

---

### 19. What is a Merge Join?

**Answer:** It matches two ordered inputs by advancing through their sorted keys.

**Follow-up:** Where can the cost come from?

**Answer:** Sorting the inputs when they are not already ordered.

---

### 20. HashAggregate vs GroupAggregate?

**Answer:** HashAggregate groups via a hash structure; GroupAggregate processes grouped/ordered input.

**Common mistake:** Declaring one universally faster.

---

### 21. What is selectivity?

**Answer:** How small the matching subset is relative to the relation.

**Example:**

```text
unique ID lookup
→ high selectivity
```

---

### 22. What is a composite index?

**Answer:** An index over multiple key columns.

**Example:**

```sql
(customer_id, created_at)
```

**Follow-up:** Why does column order matter?

---

### 23. Explain the leftmost-prefix concept.

**Concise answer:** A composite index is naturally aligned with query patterns beginning with its leading key columns.

**Deeper:** The first key structures the index; later keys refine ordering within that key.

**Common mistake:** Saying later columns can never be used.

---

### 24. What is a covering index?

**Answer:** An index that contains enough data to satisfy the query without needing all selected values from the heap.

**Follow-up:** What does PostgreSQL `INCLUDE` do?

---

### 25. What does INCLUDE do?

**Answer:** Adds non-key columns to an index so they can be available to the index without participating in key ordering.

**Common mistake:** Thinking `INCLUDE` changes the index's primary ordering.

---

### 26. What is a partial index?

**Answer:** An index containing only rows matching a predicate.

**Example:**

```sql
... WHERE status = 'pending'
```

**Common mistake:** Assuming it helps unrelated status queries.

---

### 27. What is an expression index?

**Answer:** An index on the result of an expression.

**Example:**

```sql
CREATE INDEX ...
ON users(LOWER(email));
```

---

### 28. Why might PostgreSQL ignore an index?

**Concise answer:** Because the optimizer estimates another plan is cheaper.

**Possible reasons:**

```text
small table
low selectivity
stale stats
non-sargable predicate
type mismatch
wrong index shape
random access cost
```

---

### 29. What are stale statistics?

**Answer:** Planner statistics that no longer represent the current data distribution well.

**Follow-up:** What can refresh them?

**Answer:** `ANALYZE`.

---

### 30. What does ANALYZE do?

**Answer:** Updates planner statistics used for cardinality and cost estimates.

**Common mistake:** Treating it as a universal performance fix.

---

### 31. What is table bloat?

**Answer:** Excess physical storage resulting from row-version and cleanup behavior, especially under update/delete-heavy workloads.

**Follow-up:** What tool helps routine cleanup?

**Answer:** `VACUUM`.

---

### 32. What does VACUUM do?

**Answer:** Cleans up dead tuples and maintains visibility metadata, helping PostgreSQL reuse storage and keep scans efficient.

---

### 33. What is pg_stat_statements?

**Answer:** A PostgreSQL extension that aggregates statement-level workload statistics to help identify expensive/high-volume queries.

---

### 34. What is auto_explain?

**Answer:** A PostgreSQL facility that can automatically log plans for queries meeting configured criteria.

---

### 35. Why use statement_timeout?

**Answer:** To limit how long a statement is allowed to run.

**Example:**

```sql
SET statement_timeout = '5s';
```

---

### 36. GIN vs GiST vs BRIN?

**Answer:** They support different workload patterns.

```text
GIN
→ multi-component/searchable values

GiST
→ ranges/spatial/extensible strategies

BRIN
→ compact summaries for physically correlated large tables
```

**Common mistake:** Turning these into rigid one-purpose rules.

---

### 37. When would BRIN be useful?

**Answer:** Very large tables where the indexed values correlate with physical order and queries use ranges.

---

### 38. Why can BRIN be much smaller?

**Answer:** It stores compact summaries for ranges of table pages rather than detailed entries for every indexed row.

---

### 39. What is CREATE INDEX CONCURRENTLY?

**Answer:** A PostgreSQL index-build method designed to reduce interference with normal table writes compared with a conventional build.

**Common mistake:** Calling it risk-free.

---

### 40. How do indexes affect bulk loads?

**Answer:** Existing indexes need maintenance as rows are loaded, which can increase ingestion cost.

**Follow-up:** Should indexes always be dropped?

**Answer:** No. Measure total workload and operational constraints.

---

### 41. Why do analytical engines often not need traditional B-tree indexes?

**Answer:** They can rely on columnar scans, vectorization, data skipping, partition pruning, clustering, and compression.

---

### 42. What are zone maps?

**Answer:** Storage metadata such as min/max summaries that allow engines to skip blocks that cannot satisfy predicates.

---

### 43. What is partition pruning?

**Answer:** Eliminating partitions that cannot satisfy a partition-key predicate.

---

### 44. What is clustering?

**Answer:** Physically organizing related values closer together to improve locality and potentially data skipping.

---

### 45. How would you tune a query that suddenly became slow?

**Answer:**

```text
baseline
→ EXPLAIN ANALYZE
→ BUFFERS
→ estimate/actual comparison
→ identify bottleneck
→ form one hypothesis
→ change one thing
→ re-measure
→ verify correctness
```

---

### 46. How do you prove an optimization helped?

**Answer:** Compare before/after execution evidence on a representative workload and verify that the result remains correct.

---

## 71. Production Checklist

Before tuning a production query:

- [ ] The query's correctness is already understood.
- [ ] The intended output grain is known.
- [ ] A representative baseline runtime is recorded.
- [ ] Representative parameter values are used.
- [ ] `EXPLAIN` has been inspected.
- [ ] `EXPLAIN ANALYZE` is used safely where appropriate.
- [ ] `BUFFERS` are inspected when I/O matters.
- [ ] The plan is read from inner nodes outward.
- [ ] Estimated and actual rows are compared.
- [ ] Loops are understood.
- [ ] The dominant cost is identified.
- [ ] Scan choice is understood.
- [ ] Join strategy is understood.
- [ ] Sort/hash operations are reviewed.
- [ ] Predicate sargability is checked.
- [ ] Selectivity is considered.
- [ ] Existing indexes are reviewed before adding new ones.
- [ ] Composite index order matches the workload.
- [ ] Covering/`INCLUDE` use is justified.
- [ ] Partial-index predicates match real workload patterns.
- [ ] Expression indexes are justified.
- [ ] Statistics freshness is considered.
- [ ] `ANALYZE` has been considered after substantial data changes.
- [ ] Bloat/maintenance is considered where relevant.
- [ ] Bulk-load impact is considered.
- [ ] `CREATE INDEX CONCURRENTLY` is considered for appropriate PostgreSQL production changes.
- [ ] One meaningful change is tested at a time.
- [ ] Before/after evidence is recorded.
- [ ] Query result correctness is re-verified.
- [ ] The final optimization has a written reason.
- [ ] Workload-wide effects have been considered.
- [ ] The change can be safely rolled back or reversed when appropriate.

---

## 72. Final Knowledge Check

Complete these practical tasks before moving on.

### Task 1 — Index fundamentals

Explain:

```text
What is an index?
Why is it an access path?
Why is it not free?
```

Then design one candidate index for:

```sql
SELECT *
FROM customers
WHERE customer_id = 123;
```

---

### Task 2 — Equality vs range

Design and justify indexes for:

```sql
WHERE customer_id = 123
```

and:

```sql
WHERE created_at >= ...
  AND created_at < ...
```

---

### Task 3 — ORDER BY

Given:

```sql
SELECT
    order_id,
    created_at
FROM orders
WHERE customer_id = 123
ORDER BY created_at DESC
LIMIT 50;
```

Propose a composite index and explain:

```text
predicate
ordering
column order
trade-offs
```

---

### Task 4 — EXPLAIN

Run:

```sql
EXPLAIN
SELECT *
FROM orders
WHERE customer_id = 123;
```

Identify:

```text
root
child
estimated rows
cost
```

---

### Task 5 — EXPLAIN ANALYZE + BUFFERS

Run:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE customer_id = 123;
```

Record:

```text
planning time
execution time
actual rows
loops
shared hits
shared reads
```

---

### Task 6 — Plan reading

Given:

> **SIMULATED**

```text
Nested Loop
├── Seq Scan on customers
│   estimated rows=100
│   actual rows=100000
└── Index Scan on orders
    loops=100000
```

Explain:

```text
why this may be expensive
what estimate is suspicious
what you would investigate next
```

---

### Task 7 — Estimated vs actual rows

Given:

```text
estimated = 50
actual = 750000
```

Explain:

```text
why this matters
which plan decisions it may influence
what evidence to collect
```

---

### Task 8 — Composite indexes

Explain the difference between:

```text
(customer_id, created_at)
```

and:

```text
(created_at, customer_id)
```

for customer-history queries.

---

### Task 9 — Leftmost-prefix reasoning

Explain what the leftmost-prefix concept does and does not mean.

---

### Task 10 — Covering index

Given:

```sql
SELECT created_at, amount, status
FROM orders
WHERE customer_id = 123
ORDER BY created_at DESC
LIMIT 100;
```

design a covering index using:

```text
INCLUDE
```

Then explain why index-only access is still subject to visibility information.

---

### Task 11 — Partial index

Design a partial index for:

```sql
status = 'pending'
```

and a query that matches its predicate.

---

### Task 12 — Expression index

Design an expression index for normalized email:

```sql
LOWER(email)
```

Then show the matching predicate.

---

### Task 13 — Why is PostgreSQL ignoring my index?

Create a scenario where:

```text
90% of rows match
```

and explain why a Seq Scan can be reasonable.

---

### Task 14 — Non-sargable predicate

Rewrite:

```sql
WHERE DATE(created_at) = DATE '2026-03-01'
```

as a half-open range.

Explain the access-path reasoning.

---

### Task 15 — Statistics

Create a changing data distribution, inspect estimate/actual rows, run:

```sql
ANALYZE
```

and compare.

---

### Task 16 — VACUUM and bloat

Explain:

```text
dead tuples
VACUUM
bloat
long-running transactions
```

at a foundational level.

---

### Task 17 — GIN/GiST/BRIN

For each workload choose a candidate index type:

```text
JSONB containment
range/spatial-style search
huge correlated time-ordered table
```

Defend each choice.

---

### Task 18 — Bulk load

Design a strategy for loading:

```text
100 million rows
```

into a table with multiple secondary indexes.

Compare:

```text
indexes maintained during load
vs
staging + build/rebuild
```

without assuming one always wins.

---

### Task 19 — Concurrent index creation

Write:

```sql
CREATE INDEX CONCURRENTLY ...
```

for a busy production table.

Then explain:

```text
why it helps
what it does not guarantee
what operational risks remain
```

---

### Task 20 — Analytical engines

Explain how a scan-heavy DuckDB or warehouse workload can be accelerated using:

```text
columnar storage
zone maps
partition pruning
clustering
vectorized execution
```

without relying primarily on PostgreSQL-style B-tree indexes.

---

### Task 21 — Tuning workflow

For a deliberately slow query, write:

```text
baseline
→ plan
→ hypothesis
→ one change
→ after measurement
→ correctness validation
```

---

### Task 22 — Final integrated exercise

Use this scenario:

```text
500 million event rows
50 million orders
high-frequency customer lookups
pending-payment queue
monthly event analytics
```

Produce:

```text
1. query workload inventory
2. index candidates
3. partition candidate
4. BRIN candidate
5. composite index candidate
6. partial index candidate
7. covering index candidate
8. statistic/ANALYZE plan
9. bulk-load strategy
10. measurement plan
```

For every decision document:

```text
Query pattern:
Predicate:
Ordering:
Expected selectivity:
Table size:
Read frequency:
Write frequency:
Candidate:
Why:
Trade-offs:
Validation:
What could invalidate the assumption:
```

---

## 73. Checkpoint — Ready for Topic 09?

You are ready to continue only when you can practically demonstrate all five capabilities.

### 1. Read an `EXPLAIN ANALYZE` plan and find the slowest node

You should be able to:

```text
read the tree
→ identify leaf execution
→ compare timing
→ consider loops
→ identify dominant work
```

Do not choose the slowest node by looking only at the largest-looking cost number.

---

### 2. Explain the leftmost-prefix rule for composite indexes

Given:

```text
(customer_id, created_at)
```

you should be able to explain why queries beginning with:

```text
customer_id
```

are naturally aligned with the index and why:

```text
created_at-only
```

queries do not have the same direct alignment.

You should also state that PostgreSQL's optimizer behavior is more nuanced than a rigid yes/no rule.

---

### 3. Choose between B-tree, partial, covering, GIN, and BRIN indexes

You should be able to map:

```text
general equality/range/order
→ B-tree

small hot subset
→ partial index

query needs extra non-key columns
→ covering/INCLUDE

multi-component searchable values
→ GIN

huge physically correlated range workload
→ BRIN
```

Then justify the choice using:

```text
workload
selectivity
data size
write rate
physical correlation
```

rather than memorization.

---

### 4. Explain why an index was not used

You should be able to investigate:

```text
small table
low selectivity
stale statistics
non-sargable predicate
type mismatch
wrong index shape
random access cost
alternative cheaper plan
```

and distinguish:

```text
"index exists"
```

from:

```text
"index is cheaper for this workload"
```

---

### 5. Explain how analytical engines speed up queries without B-tree indexes

You should be able to explain:

```text
columnar storage
+
vectorized execution
+
zone maps / data skipping
+
partition pruning
+
clustering
+
compression/predicate pushdown
```

and distinguish this architecture from PostgreSQL's traditional row-store/index access model.

### Practical demonstration requirement

Do not move to Topic 09 until you can solve the five tasks with:

```text
SQL
+
plan interpretation
+
measured evidence
+
clear engineering reasoning
```

---

# Final Roadmap Tuning Principle

Use this as the operational rule for future SQL performance work:

```text
MEASURE
   ↓
READ PLAN
   ↓
FORM HYPOTHESIS
   ↓
CHANGE ONE THING
   ↓
MEASURE AGAIN
```

The goal is not:

```text
"make the plan look clever."
```

The goal is:

```text
preserve correctness
+
improve meaningful workload performance
+
understand the trade-offs
```

An optimization is successful only when:

```text
the answer remains correct
AND
the measured workload improves meaningfully
AND
the operational cost remains acceptable
```

---

# Common Mistakes — Final Summary

Remember:

```text
Seq Scan
→ not automatically bad

index exists
→ not proof that it should be used

more indexes
→ not automatically better

composite index
→ column order matters

covering index
→ does not guarantee index-only scan

partial index
→ only useful for matching predicate patterns

expression index
→ query expression must align

selectivity
→ strongly affects access-path choice

statistics
→ influence cardinality and cost estimates

estimated rows
→ compare with actual rows

loops
→ expose repeated work

BUFFERS
→ useful evidence about I/O/cache activity

EXPLAIN ANALYZE
→ executes the statement

ANALYZE
→ refreshes statistics; does not fix every problem

VACUUM
→ cleanup/visibility maintenance; not a magic shrink command

BRIN
→ strongest when physical correlation supports it

GIN/GiST
→ operator/workload dependent

CREATE INDEX CONCURRENTLY
→ lower interference goal, not zero risk

bulk loads
→ indexes can increase ingestion cost

analytical engines
→ can use columnar/data-skipping physical techniques

optimization
→ should be hypothesis-driven
```

The durable senior-engineering habit is:

```text
Do not ask:
"Which index should I add?"

Ask:
"What is the workload?
What is the current plan?
Where is the bottleneck?
What hypothesis explains it?
What single change tests that hypothesis?
How will I prove the result?"
```

---

# Code Example Requirements

All important examples in this chapter are embedded directly in this Markdown file.

Primary environments:

```text
PostgreSQL 16+
DuckDB
```

When behavior is engine-specific, label it:

```text
STANDARD SQL
POSTGRESQL
DUCKDB
WAREHOUSE / SPARK CONCEPT
```

Examples use:

```text
customers
orders
order_lines
payments
events
subscriptions
jobs
```

### Important safety rule for plan examples

Actual plan output depends on:

```text
PostgreSQL version
statistics
data volume
configuration
hardware
cache state
concurrency
query parameters
```

Therefore:

- real examples show the SQL command to run;
- simulated plans are explicitly marked **SIMULATED**;
- no simulated plan is presented as actual output from a live engine.

---

# Safe EXPLAIN ANALYZE Requirement

Whenever you use:

```text
EXPLAIN ANALYZE
```

remember:

```text
SELECT
→ executes the query

INSERT/UPDATE/DELETE
→ executes the modification

DDL
→ requires special care depending on statement semantics
```

For destructive practice:

```sql
BEGIN;

EXPLAIN ANALYZE
DELETE FROM ...
WHERE ...;

ROLLBACK;
```

Use a controlled environment and never casually execute destructive `EXPLAIN ANALYZE` statements in production.

---

# Plan-Reading Accuracy Requirement

For each important plan node, ask:

```text
Node:
Estimated startup cost:
Estimated total cost:
Estimated rows:
Estimated width:
Actual time:
Actual rows:
Loops:
Buffers if present:
```

Then interpret:

```text
what the node does
what it consumed
what it produced
where work repeated
what evidence supports the diagnosis
```

Never infer a cause from a single number.

---

# Index-Decision Requirement

Before suggesting an index, document:

```text
Query pattern:
Predicate:
Ordering:
Expected selectivity:
Table size:
Read frequency:
Write frequency:
Candidate index:
Why:
Trade-offs:
Validation plan:
What could invalidate the assumption:
```

Make this a standard design-review habit.

---

# Before/After Requirement

Every serious tuning experiment should be documented as:

```text
BEFORE
- query
- plan
- runtime
- key evidence

HYPOTHESIS
- what is wrong
- why

CHANGE
- exactly one meaningful change

AFTER
- plan
- runtime
- key evidence

CONCLUSION
- whether the hypothesis was supported
- whether correctness was preserved
- whether the change should be kept
```

---

# No Hand-Waving Rule

Do not write:

> “The index makes the query faster.”

Prefer:

> “The index provides a more selective access path for this predicate, allowing PostgreSQL to identify a much smaller set of candidate rows than scanning the whole table. Whether that access path is actually cheaper depends on selectivity, table size, cached pages, row width, statistics, and the optimizer's cost model.”

Apply the same precision to:

```text
Seq Scan
Index Scan
Bitmap scans
join nodes
statistics
BRIN
partial indexes
covering indexes
analytical data skipping
```

---

# Performance Before Prescription

Never say:

> “Always create an index for this.”

Teach:

> “This workload suggests an index candidate. Validate the hypothesis with `EXPLAIN ANALYZE` and a before/after comparison.”

The point of this topic is not to memorize prescriptions.

The point is to develop a measurement-first performance engineering mindset.

---

# PostgreSQL-First Depth

This topic is primarily PostgreSQL because the roadmap explicitly emphasizes:

```text
indexes
EXPLAIN
EXPLAIN ANALYZE
BUFFERS
planner statistics
ANALYZE
VACUUM
pg_stat_statements
auto_explain
CREATE INDEX CONCURRENTLY
```

DuckDB and broader analytical engines are used to build architectural intuition.

Do not blur:

```text
PostgreSQL row-store/index architecture
```

with:

```text
analytical columnar/data-skipping architecture
```

---

# Analytical-Engine Accuracy

Do not reduce analytical systems to:

```text
"No indexes."
```

Instead reason:

```text
columnar storage
+
vectorized execution
+
zone maps/data skipping
+
partition pruning
+
clustering
+
compression
+
predicate pushdown
```

These can provide efficient scan-heavy analytics without relying primarily on PostgreSQL-style B-tree access paths.

---

# Statistics Accuracy

Do not say:

> “Run ANALYZE whenever a query is slow.”

Use:

> “When estimates appear stale or inaccurate—especially after substantial data changes or distribution shifts—refreshing statistics with `ANALYZE` can improve the optimizer's information. It is one diagnostic/action among several.”

---

# BRIN Accuracy

BRIN is especially useful when:

```text
table is very large
+
indexed values correlate with physical row order
+
predicates use ranges
```

For example:

```text
append-heavy event table
+
time-ordered rows
+
time-range queries
```

Do not claim BRIN is universally faster, smaller in every physical sense, or a replacement for B-tree.

---

# GIN/GiST Accuracy

Do not reduce them to:

```text
GIN = JSONB
GiST = spatial
```

Use:

```text
operator semantics
+
operator class
+
workload
```

to reason about suitability.

---

# No External Files

All chapter material is embedded here:

```text
sample schemas
sample data
SQL
simulated plans
before/after comparisons
exercises
solutions
debugging
performance challenges
case study
checklists
```

No separate:

```text
.sql
.csv
.py
.ipynb
benchmark
script
diagram
```

is required.

---

# Topic 08 Coverage Summary

This chapter covered:

- index definition;
- access paths;
- B-tree;
- equality lookups;
- range lookups;
- `ORDER BY`;
- uniqueness;
- index read/write/storage trade-offs;
- `EXPLAIN`;
- `EXPLAIN ANALYZE`;
- `BUFFERS`;
- plan trees;
- inside-out plan reading;
- estimated vs actual rows;
- execution timing;
- Seq Scan;
- Index Scan;
- Index Only Scan;
- Bitmap Index Scan;
- Bitmap Heap Scan;
- Nested Loop;
- Hash Join;
- Merge Join;
- Sort;
- HashAggregate;
- GroupAggregate;
- composite indexes;
- column order;
- leftmost-prefix reasoning;
- covering indexes;
- `INCLUDE`;
- partial indexes;
- expression indexes;
- selectivity;
- non-sargable predicates;
- type mismatches;
- reasons indexes may be ignored;
- planner statistics;
- `ANALYZE`;
- bad row estimates;
- `VACUUM`;
- bloat;
- `pg_stat_statements`;
- `auto_explain`;
- statement/lock timeouts;
- GIN;
- GiST;
- BRIN;
- index selection;
- bulk-load/index trade-offs;
- `CREATE INDEX CONCURRENTLY`;
- analytical engines without primary reliance on B-tree indexes;
- columnar storage;
- zone maps;
- partition pruning;
- clustering;
- PostgreSQL vs DuckDB vs warehouse/Spark plan thinking;
- measurement-first tuning;
- before/after comparison;
- production performance patterns;
- slow-query debugging;
- correctness validation;
- beginner practice;
- intermediate practice;
- advanced practice;
- simulated plan-reading drills;
- debugging challenges;
- performance-tuning challenges;
- production case study;
- interview questions;
- production checklist;
- final knowledge check;
- Topic 09 checkpoint.

---

# Final File-Safety Verification

This chapter is intended to exist only as:

```text
06-SQL-for-Data-Engineers/08-indexes-and-reading-explain-plans.md
```

No README, neighboring topic, practice file, interview file, helper file, benchmark file, dataset, script, notebook, folder, or other repository artifact is part of this chapter.
