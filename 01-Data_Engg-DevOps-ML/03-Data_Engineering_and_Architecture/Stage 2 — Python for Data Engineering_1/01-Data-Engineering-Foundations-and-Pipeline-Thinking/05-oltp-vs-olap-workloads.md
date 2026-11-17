# OLTP vs OLAP Workloads

> **Module:** Python for Data Engineering → 01-Data-Engineering-Foundations-and-Pipeline-Thinking  
> **Topic:** 05 — OLTP vs OLAP Workloads  
> **Level:** Beginner → Intermediate → Advanced foundation  
> **Implementation rule for this lesson:** Python 3.12+ standard library only, with SQLite for local experiments.
>
> **Central engineering principle:**  
> **Design the data architecture around workload characteristics and business requirements—not around the database technology you happen to know.**

---

# 1. Why This Topic Matters

The previous topics established:

```text
Topic 01:
What do data engineers build?

Topic 02:
How does data move through a data lifecycle?

Topic 03:
How frequently should data be processed?

Topic 04:
Where should transformation happen?
```

This topic adds another fundamental question:

> **Why do operational systems and analytical systems usually have different workloads, storage patterns, data models, and performance requirements?**

A beginner may see:

```text
"database"
```

and assume one database should handle everything.

A production data engineer asks:

```text
What workload does this system have?
```

That question changes everything.

Compare:

```sql
SELECT *
FROM customers
WHERE customer_id = 42;
```

with:

```sql
SELECT
    country,
    SUM(amount) AS revenue
FROM orders
GROUP BY country;
```

Both are database queries.

But they ask the database to do very different work.

The first is a small, selective operational lookup.

The second may require scanning and aggregating a large amount of historical information.

This leads to the core mental model:

```text
Business operation
      ↓
Operational workload
      ↓
OLTP


Business analysis
      ↓
Analytical workload
      ↓
OLAP
```

The architectural consequences can include:

```text
OLTP
→ OLAP
→ row vs column storage
→ normalized vs denormalized models
→ workload isolation
→ read replicas
→ CDC-based replication
→ HTAP
→ measurable workload characteristics
```

This topic establishes the foundation for Topic 06, where you will study warehouse, lake, and lakehouse architectures in greater depth.

---

# 2. Learning Outcomes

By the end of this lesson, you should be able to:

1. Explain OLTP in simple language.
2. Explain OLAP in simple language.
3. Identify an OLTP workload and an OLAP workload.
4. Explain why their access patterns differ.
5. Explain point lookups and large analytical scans.
6. Explain row-oriented storage.
7. Explain column-oriented storage.
8. Explain why columnar storage is often effective for analytical queries.
9. Explain normalized relational models.
10. Explain denormalized and dimensional analytical models.
11. Explain why heavy analytics can interfere with production OLTP workloads.
12. Explain read replicas.
13. Explain replication lag.
14. Explain Change Data Capture (CDC) conceptually.
15. Explain HTAP, meaning Hybrid Transactional/Analytical Processing.
16. Explain queries per second (QPS), rows scanned, latency, and concurrency.
17. Run the required one-million-row SQLite benchmark.
18. Benchmark 10,000 primary-key lookups.
19. Benchmark a large aggregation.
20. Add a `country` index and measure its effect.
21. Build a toy column-oriented representation.
22. Compare bytes read for an amount-only aggregation.
23. Interpret benchmark results without treating a laptop experiment as a universal production benchmark.
24. Translate business workload requirements into architecture decisions.

---

# 3. The Most Important Mental Model

> **Database architecture follows workload characteristics.**

Do not start with:

```text
"We know PostgreSQL."
```

or:

```text
"We should use a warehouse."
```

Start with:

```text
What is the workload?
```

Then ask:

```text
How does it read?
How does it write?
How many operations happen?
How many rows does each query touch?
How quickly must it respond?
How many users are active?
How much consistency is required?
```

Then choose architecture.

A useful flow is:

```text
Business requirement
      ↓
Workload
      ↓
Access pattern
      ↓
Volume
      ↓
Latency
      ↓
Concurrency
      ↓
Consistency
      ↓
Architecture
      ↓
Technology
```

---

# 4. Start With Two Questions

## Operational question

```text
"Find customer 42."
```

This may need:

```text
one row
```

or a small number of rows.

The business process may be:

```text
customer opens profile
```

The system needs a quick response.

---

## Analytical question

```text
"Calculate monthly revenue by country for the last three years."
```

The system may need:

```text
millions or billions of rows
```

and perform:

```text
scan
→ filter
→ group
→ aggregate
```

The consumer may tolerate a longer query than a customer-facing transaction.

---

# 5. OLTP — Online Transaction Processing

**OLTP** means **Online Transaction Processing**.

A simple definition:

> **OLTP systems support many small, concurrent, operational reads and writes that keep a business application running.**

Examples:

- placing an order
- creating a customer
- updating an address
- processing a payment
- changing account balance
- reducing inventory
- updating a subscription

OLTP is about keeping the business operation working correctly and quickly.

---

# 6. OLTP in Plain English

Imagine an online shop.

A customer clicks:

```text
Buy Now
```

The application may need to:

1. create an order
2. record payment status
3. reduce inventory
4. save shipping information
5. return a confirmation

Those are operational actions.

The database may perform several short writes:

```text
INSERT order
UPDATE inventory
INSERT payment
```

The operations need to be:

- correct
- fast
- consistent
- safe under concurrency

That is an OLTP workload.

---

# 7. OLTP Workload Characteristics

Typical OLTP characteristics include:

- many small reads
- many small writes
- single-row lookups
- short transactions
- high concurrency
- strong consistency expectations
- predictable access patterns
- low response-time requirements

These are tendencies, not absolute rules.

Some systems contain mixed workloads.

The key idea is the **shape of the work**.

---

# 8. OLTP Example — Point Lookup

```sql
SELECT *
FROM customers
WHERE customer_id = 42;
```

This is a point lookup.

The database knows:

```text
I need the row associated with customer_id = 42.
```

If `customer_id` is indexed appropriately, the database may locate the row efficiently without scanning every customer.

This is fundamentally different from:

```sql
SELECT
    country,
    SUM(amount)
FROM orders
GROUP BY country;
```

which may touch a very large part of the dataset.

---

# 9. OLTP Example — Small Update

```sql
UPDATE inventory
SET quantity = quantity - 1
WHERE product_id = 1001;
```

This is operational.

The system is changing current state.

The application may need:

```text
very low latency
+
correctness
+
concurrency safety
```

A customer waiting for an order confirmation does not want the system to pause behind an unrelated analytical scan.

---

# 10. OLTP Example — Transaction

An OLTP transaction may conceptually perform:

```text
Debit account A by 100
      +
Credit account B by 100
```

The key problem is not just speed.

It is correctness.

You do not want:

```text
A = -100 applied
B = +100 failed
```

without a clear recovery mechanism.

This is why transactions matter.

---

# 11. Transaction Concept

A **transaction** is a unit of database work that should satisfy the application's consistency requirements as a unit.

At a foundational level, understand:

```text
transaction
→ operations
→ commit
```

or:

```text
transaction
→ error
→ rollback
```

A transaction therefore gives the application a controlled way to say:

```text
Treat these operations as one logical unit.
```

Detailed transaction isolation levels belong later in the database curriculum.

> You only need the transaction mental model here; detailed isolation and locking behavior are covered later.

---

# 12. Commit and Rollback

Conceptually:

```text
BEGIN
   ↓
update A
   ↓
update B
   ↓
COMMIT
```

If something goes wrong:

```text
BEGIN
   ↓
update A
   ↓
error
   ↓
ROLLBACK
```

The exact guarantees depend on the database engine and transaction configuration.

The architectural idea is:

> **Operational workloads often require small units of strongly controlled state change.**

---

# 13. OLTP Real-World Examples

## E-commerce

Typical OLTP actions:

- create order
- update order status
- reduce inventory
- record payment
- create shipment

## Banking

Typical OLTP actions:

- post transaction
- update account balance
- record payment
- authorize card transaction
- create account

## Healthcare

Typical OLTP actions:

- create appointment
- update patient registration
- record billing event

## SaaS

Typical OLTP actions:

- create organization
- create user
- update subscription
- change user settings

Real systems can contain multiple workload types.

---

# 14. OLTP Data Model

OLTP systems often use relational designs that reduce unnecessary duplication.

Suppose an order contains customer information directly in every row:

```text
orders
----------------------------------------------------------------
order_id | customer_name | customer_email | product | quantity
```

This can create repeated data.

A more normalized conceptual design can separate entities:

```text
customers
orders
order_items
products
payments
```

This is not the only valid design.

It is a common relational modeling approach.

---

# 15. Why Normalize OLTP Data?

Normalization can help:

- reduce duplication
- preserve consistency
- make updates easier
- reduce certain update anomalies

Suppose a customer's email changes.

With repeated customer email values:

```text
100 orders
→ potentially 100 repeated copies
```

A normalized customer table can store the current value once:

```text
customers
customer_id
email
```

and orders can reference it.

---

# 16. Update Anomaly

An **update anomaly** occurs when duplicated information must be changed in multiple places and some copies are not updated.

Example:

```text
Order 1 → old email
Order 2 → old email
Order 3 → new email
```

The database now contains inconsistent representations.

Normalization can reduce this problem.

---

# 17. Insert Anomaly

An **insert anomaly** occurs when a schema makes it difficult to add information without unrelated data.

For example, if customer information and product information are tightly combined in one table, creating a product before any order exists may become awkward.

Normalization can separate these entities.

---

# 18. Delete Anomaly

A **delete anomaly** occurs when removing one fact accidentally removes another fact that should still exist.

For example, if the only record of a product exists inside an order row, deleting the last order could accidentally remove the product information.

Again, normalized entity separation can help.

---

# 19. OLTP vs Normalization

The key mental model is:

```text
OLTP often values:
correct current state
+
consistent entities
+
controlled updates
```

Normalization can support those goals.

It does not mean:

```text
all OLTP systems must be fully normalized.
```

Production systems sometimes intentionally denormalize selected structures for performance or application convenience.

---

# 20. OLAP — Online Analytical Processing

**OLAP** means **Online Analytical Processing**.

A simple definition:

> **OLAP systems support analytical workloads that scan, combine, aggregate, and compare large amounts of data to answer business questions.**

Typical users include:

- analysts
- business intelligence systems
- data scientists
- ML pipelines
- finance teams
- executives
- operations analysts

---

# 21. OLAP in Plain English

Imagine the finance team asks:

> How much revenue did we generate by country for every month over the last three years?

The database may need to:

```text
read many rows
→ extract month
→ group by country/month
→ sum revenue
→ return aggregated results
```

That is an analytical workload.

---

# 22. OLAP Query Example

```sql
SELECT
    country,
    SUM(amount) AS revenue
FROM orders
GROUP BY country;
```

This query may scan a large portion of the `orders` table.

Unlike:

```sql
SELECT *
FROM orders
WHERE order_id = 12345;
```

it is not trying to find one specific row.

It is trying to summarize many rows.

---

# 23. OLAP Workload Characteristics

Typical analytical characteristics include:

- read-heavy workloads
- large scans
- aggregations
- joins across large datasets
- fewer writes in many analytical systems
- large intermediate results
- resource-intensive queries
- variable concurrency

Be careful:

> "OLAP has low concurrency" is too simplistic.

A modern analytical platform can support many users and queries.

The important distinction is:

> **Analytical queries often touch much more data per query and perform more expensive computation.**

---

# 24. OLAP Real-World Examples

## Finance

```text
Revenue by country by month
```

## Product analytics

```text
Daily active users by region
```

## Machine learning

```text
Build features from billions of historical events
```

## Executive analytics

```text
Year-over-year revenue analysis
```

## Fraud analytics

```text
Analyze years of transaction patterns
```

---

# 25. OLTP vs OLAP — First Comparison

| Dimension | OLTP | OLAP |
|---|---|---|
| Main purpose | Run business operations | Analyze data |
| Typical operation | Small reads/writes | Large scans/aggregations |
| Read pattern | Point lookup / small result | Large scans / aggregations |
| Write pattern | Frequent | Often less frequent |
| Query shape | Select/update specific entities | Group/join/aggregate |
| Concurrency | Often high | Variable, can also be high |
| Latency expectation | Usually very low | Depends on analytical need |
| Data model | Often normalized | Often denormalized/dimensional |
| Storage preference | Often row-oriented | Often column-oriented |
| Typical users | Applications | Analysts / BI / DS / ML |
| Example | Process payment | Analyze monthly revenue |

---

# 26. The Central Architectural Problem

The most important question is:

> **Why not simply run analytical queries on the production OLTP database?**

Because the analytical query can compete with business-critical operations for:

- CPU
- memory
- I/O
- cache
- locks
- connections
- temporary working space

Conceptually:

```text
Customer Requests
       ↓
Production OLTP Database
       ↓
Heavy Analytical Query
       ↓
CPU / memory / I/O competition
       ↓
Operational query slows
       ↓
Customer experience suffers
```

---

# 27. Why Direct OLTP Analytics Can Be Dangerous

A production database may support:

```text
5,000 small requests/sec
```

and then an analyst runs:

```text
scan billions of rows
```

The analytical query can consume resources needed by operational traffic.

Potential effects:

- customer-facing latency increases
- transaction throughput decreases
- connections become busy
- cache pressure increases
- disk I/O contention increases
- lock contention can appear in some query patterns
- operational workload becomes less predictable

This can contribute to operational **outages** when customer-facing workloads cannot get the resources or performance they require.

The exact behavior depends on the database engine and query.

The general problem is **resource competition**.

---

# 28. Resource Competition

Think of the database as a shared machine.

```text
CPU
├── customer request
├── payment transaction
├── inventory update
└── analytical aggregation
```

If the aggregation is extremely expensive:

```text
analytics
→ consumes resources
→ operational work gets less capacity
```

This is why workload isolation can become valuable.

---

# 29. Lock Contention

Locks are one mechanism databases may use to coordinate concurrent operations.

Analytical queries do not always create problematic locks, and modern engines use many techniques to reduce interference.

Still, the foundational concern is:

> **Concurrent workloads may interact through database resources and concurrency controls.**

For this topic, remember the risk rather than memorizing one universal lock behavior.

Detailed locking and isolation mechanics belong later.

---

# 30. Slow Customer-Facing Queries

Imagine an application endpoint:

```text
GET /customer/42
```

normally responds in:

```text
50 ms
```

An analyst starts a very heavy query.

Now application latency becomes:

```text
2 seconds
```

The exact numbers are illustrative.

The architectural point is:

```text
analytical work
→ changes operational performance
```

That is often unacceptable for a customer-facing system.

---

# 31. A Large Analytical Query Is Not "Bad"

Important nuance:

The problem is not:

```text
analytical query = bad
```

The problem is:

```text
analytical query on a resource
that must also protect operational work
```

A heavy analytical query can be perfectly reasonable on a system designed for it.

That is the purpose of workload separation.

---

# 32. Row-Oriented Storage

Now connect workload shape to storage layout.

Imagine data:

```text
id | name | country | revenue
---|------|---------|--------
1  | A    | India   | 100
2  | B    | India   | 200
3  | C    | Japan   | 150
```

A row-oriented representation conceptually stores:

```text
Row 1:
1, A, India, 100

Row 2:
2, B, India, 200

Row 3:
3, C, Japan, 150
```

The values associated with one entity are kept together conceptually.

---

# 33. Why Row Storage Fits OLTP

Suppose the application asks:

```sql
SELECT *
FROM customers
WHERE customer_id = 42;
```

The application may need:

```text
id
name
country
email
phone
status
...
```

A row-oriented layout is naturally aligned with:

> **retrieving most or all attributes of a small number of rows.**

That matches many operational access patterns.

Again, this is a conceptual storage model, not a claim about exactly how every database engine lays out every page in every situation.

---

# 34. Column-Oriented Storage

Now imagine the same dataset stored by columns.

Conceptually:

```text
id:
1, 2, 3

name:
A, B, C

country:
India, India, Japan

revenue:
100, 200, 150
```

Each column's values are grouped together.

This is called **column-oriented** or **columnar** storage.

---

# 35. Why Columnar Storage Can Help Analytics

Suppose the query is:

```sql
SELECT SUM(revenue)
FROM orders;
```

The query only requires:

```text
revenue
```

A column-oriented layout can be optimized to read the needed column rather than unrelated attributes.

That can reduce data movement.

Columnar systems can also exploit:

- compression
- encoding
- vectorized processing
- efficient scans

These concepts will be studied more deeply later.

---

# 36. Projection

**Projection** means selecting which columns are needed.

Example:

```sql
SELECT
    country,
    SUM(revenue)
FROM orders
GROUP BY country;
```

The query may only need:

```text
country
revenue
```

It does not need:

```text
customer_email
phone
shipping_address
payment_method
```

A columnar representation is naturally aligned with these projection-heavy workloads.

---

# 37. Compression

Column values often have similar types and sometimes repeated patterns.

For example:

```text
country:
India
India
India
India
US
US
US
```

A columnar system may exploit this regularity to compress the data effectively.

The exact compression method is implementation-specific.

The foundational principle is:

> **Column-oriented storage often creates strong opportunities for analytical compression and scan efficiency.**

---

# 38. Vectorized Processing

At a high level, vectorized processing means performing an operation over a group of values rather than treating every value as a completely separate operation.

For example:

```text
revenue:
[100, 200, 300, 400]

sum:
100 + 200 + 300 + 400
```

Analytical engines often optimize such column operations heavily.

You do not need to implement vectorized execution here.

---

# 39. Row vs Column Comparison

| Dimension | Row-oriented | Column-oriented |
|---|---|---|
| Physical organization | By rows | By columns |
| Point lookups | Often strong fit | Often less natural |
| Full-row reads | Strong fit | Less ideal |
| Analytical projection | Less optimized in many designs | Strong fit |
| Compression opportunities | Good | Often strong |
| Typical OLTP fit | High | Usually lower |
| Typical OLAP fit | Possible | Commonly strong |

These are workload-oriented tendencies.

Do not turn them into universal rules.

---

# 40. Why Columnar Storage Is Not Always Faster

Suppose the application needs:

```text
one customer
+
every column
```

Reading many separate column structures may not be the ideal physical representation.

Similarly, an analytical database can still perform poorly if:

- the query is badly written
- data is badly organized
- the engine has poor statistics
- the scan volume is huge
- the system is overloaded

Therefore:

```text
columnar
≠
automatically faster
```

It means the storage layout is often better aligned with analytical access patterns.

---

# 41. Normalized vs Denormalized Models

Now move from physical storage to logical data modeling.

## Normalized model

Information is split into related tables.

Example:

```text
customers
orders
order_items
products
```

The goal often includes:

- reduced redundancy
- consistent updates
- clear entity boundaries

## Denormalized model

Related data is combined into fewer or wider structures.

Example:

```text
sales_analysis
------------------------------------------------
date | customer | country | product | quantity | revenue
```

This can reduce joins for common analytical queries.

---

# 42. Why Denormalization Can Help Analytics

Consider:

```sql
SELECT
    c.country,
    SUM(oi.quantity * oi.unit_price)
FROM customers c
JOIN orders o
    ON o.customer_id = c.customer_id
JOIN order_items oi
    ON oi.order_id = o.order_id
GROUP BY c.country;
```

This can require several joins.

A pre-modeled analytical table may already contain:

```text
country
revenue
order_date
product_category
```

Then the query becomes simpler.

The trade-off is:

```text
more repeated / derived data
```

in exchange for:

```text
simpler analytical access
```

---

# 43. Dimensional Thinking

A common analytical modeling approach uses:

```text
fact table
+
dimension tables
```

## Fact table

Contains measurable business events.

Example:

```text
fact_sales
-----------------------------
date_id
customer_id
product_id
country_id
quantity
revenue
```

## Dimension tables

Describe entities or categories.

```text
dim_customer
dim_product
dim_date
dim_country
```

This is an analytical modeling concept.

Detailed dimensional modeling belongs later.

> You only need the workload-to-model relationship here; the full modelling curriculum is covered later in Module 2.8.

---

# 44. Why OLTP and OLAP Models Differ

A useful summary is:

## OLTP priorities

```text
correct current state
+
consistent entities
+
fast small operations
+
high concurrency
```

## OLAP priorities

```text
large scans
+
joins
+
aggregations
+
analytical convenience
```

Therefore:

```text
normalized model
```

often fits operational needs, while:

```text
denormalized / dimensional model
```

often fits analytical needs.

Neither is universally "better."

---

# 45. First Architecture Progression

A small system may start with:

```text
Application
    ↓
Single Database
    ↓
Light Analytics
```

This can be reasonable.

Do not learn:

> Every production system must have separate OLTP and OLAP databases.

That is too absolute.

The real question is:

> **When does workload isolation justify additional architecture?**

---

# 46. When One Database Can Be Fine

A small application may have:

- low traffic
- small datasets
- simple analytics
- controlled concurrency
- low operational risk

In such a case:

```text
one relational database
```

can be entirely reasonable.

Architecture should not be complicated merely to look professional.

---

# 47. When Workload Separation Becomes Valuable

Separate analytical resources may become useful when:

- analytical scans become large
- customer traffic increases
- analytical queries become unpredictable
- operational latency becomes sensitive
- analytics and applications compete for resources
- analytical storage patterns differ
- analytical scaling is different from transactional scaling

This is a workload decision.

---

# 48. Read Replicas

A **read replica** is a copy of an operational database that can serve selected read workloads without directly hitting the primary.

Conceptually:

```text
                     ┌───────────────┐
Writes ────────────► │   Primary DB  │
                     └───────┬───────┘
                             │
                         Replication
                             ↓
                     ┌───────────────┐
Reads ──────────────►│  Read Replica │
                     └───────────────┘
```

The primary handles writes.

The replica can serve some reads.

---

# 49. Why Read Replicas Exist

Potential benefits:

- reduce primary read load
- isolate some read traffic
- increase read capacity
- separate certain consumers from the primary

For example:

```text
Application writes
→ primary

Read-heavy application queries
→ replica
```

---

# 50. Read Replica Does Not Automatically Solve Analytics

A common mistake is:

```text
Primary overloaded by analytics
→ add read replica
→ put huge analytical queries on replica
→ problem solved
```

Not necessarily.

The heavy analytical workload can simply move to:

```text
replica
```

and consume its resources.

The key distinction is:

> **A replica isolates reads from the primary, but it does not automatically turn transactional infrastructure into an analytical platform.**

---

# 51. Replication Lag

A replica is not always perfectly synchronized at every instant.

Example:

```text
Primary:
order 1001 created

Replica:
does not have order 1001 yet
```

The time difference is replication lag.

Therefore:

```text
primary time
≠
replica visibility time
```

This can matter if consumers require very fresh or strongly consistent data.

---

# 52. Read Replica Trade-Offs

| Benefit | Cost / limitation |
|---|---|
| Reduces some primary read pressure | Replica also has finite resources |
| Easy conceptual model | Replication lag |
| Can support read scaling | Not automatically suitable for heavy analytics |
| Can isolate read traffic | Additional operational complexity |

---

# 53. CDC — Change Data Capture

**Change Data Capture (CDC)** is a way of capturing changes occurring in a source system so they can be propagated downstream.

A foundational model is:

```text
INSERT
UPDATE
DELETE
```

These are changes to source state.

Conceptually:

```text
OLTP Database
     ↓
Change Capture
     ↓
Change Stream / Log
     ↓
Analytical Platform
```

---

# 54. Why CDC Exists

Imagine an operational database containing:

```text
100 million rows
```

You want analytical systems to stay reasonably current.

A full copy every time may be wasteful.

CDC can conceptually propagate only changes:

```text
new row
changed row
deleted row
```

This can support:

- incremental downstream updates
- lower extraction volume
- near-real-time propagation
- workload isolation

The exact implementation varies by database.

---

# 55. CDC Example

Suppose:

```text
customer_id = 42
status = "TRIAL"
```

changes to:

```text
customer_id = 42
status = "ACTIVE"
```

CDC can conceptually represent:

```text
UPDATE
customer_id = 42
new_status = ACTIVE
```

Then the analytical platform can apply that change.

---

# 56. CDC Is Not the Same as a Read Replica

A read replica is primarily:

```text
another database copy
```

CDC is primarily:

```text
change propagation mechanism
```

The distinction is important.

| Dimension | Read replica | CDC |
|---|---|---|
| Main purpose | Offload/read scale | Propagate changes |
| Destination | Database copy | Downstream data system |
| Data movement | Replication | Change records |
| Analytical isolation | Limited by replica use | Can enable separate analytical system |
| Historical behavior | Depends on replica | Depends on retained change/history |

Implementation varies widely.

---

# 57. CDC-Based Analytical Architecture

A common conceptual architecture is:

```text
Application
    ↓
OLTP Database
    ↓
CDC
    ↓
Analytical Platform
    ↓
BI / ML / Analytics
```

This creates workload isolation.

The operational system continues handling operational work.

The analytical platform handles:

```text
large scans
aggregations
historical analysis
```

---

# 58. Why CDC Does Not Eliminate All Problems

CDC introduces its own engineering responsibilities:

- schema changes
- change ordering
- duplicate events
- missing changes
- recovery
- source impact
- downstream consistency

It solves one class of problem:

```text
how do changes get propagated?
```

It does not automatically solve:

```text
how should the analytical system model the data?
```

or:

```text
how should analytical queries perform?
```

---

# 59. HTAP

**HTAP** means:

> **Hybrid Transactional/Analytical Processing**

A simple definition:

> **HTAP systems attempt to support transactional and analytical workloads within a tightly integrated architecture.**

The motivation is:

```text
Can we reduce the need to move data
between completely separate transactional
and analytical systems?
```

---

# 60. Why HTAP Exists

Potential goals include:

- analytics closer to operational data
- reduced movement between systems
- mixed transactional and analytical access
- lower analytical freshness delay

However, combining workloads creates difficult design questions.

---

# 61. HTAP Challenges

Potential challenges include:

- resource contention
- consistency requirements
- indexing trade-offs
- query interference
- scaling differences
- system complexity
- performance isolation

HTAP does not mean:

```text
separate analytical systems are unnecessary everywhere.
```

It is one architectural option for specific workloads.

---

# 62. OLTP / OLAP / Read Replica / CDC / HTAP

A useful landscape is:

```text
                         ┌──────────────────┐
                         │      OLTP        │
                         │  Primary System  │
                         └────────┬─────────┘
                                  │
                  ┌───────────────┼────────────────┐
                  │               │                │
                  ↓               ↓                ↓
            Read Replica         CDC             HTAP
                  │               │
                  ↓               ↓
            Read-heavy       Analytical
             workloads        Platform
```

Interpretation:

- **Read replica:** copies operational data and can absorb selected reads.
- **CDC:** propagates source changes to another system.
- **HTAP:** tries to support transaction and analytical workloads in an integrated design.

---

# 63. Workload Characteristics as Measurable Numbers

Workload architecture becomes much clearer when you quantify it.

Four key measures in this lesson are:

```text
QPS
Rows scanned
Latency
Concurrency
```

---

# 64. QPS — Queries Per Second

**QPS** means **queries per second**.

Simple definition:

> How many database queries or requests are handled in one second.

Example:

```text
5,000 customer lookups / second
```

This can be common in high-traffic OLTP systems.

QPS alone is not enough.

The workload might be:

```text
5,000 tiny lookups
```

or:

```text
100 huge scans
```

Those are very different resource demands.

---

# 65. Rows Scanned

Rows scanned is a powerful workload signal.

Compare:

```text
Point lookup
→ 1 or a few rows
```

with:

```text
Revenue analysis
→ millions of rows
```

A query that touches more rows generally requires more work.

Not always proportionally more, because indexes, caching, pruning, storage layout, and engine optimizations matter.

Still:

> **Rows touched is one of the first quantities an engineer should think about.**

---

# 66. Latency

Latency asks:

> How quickly must the operation complete?

Examples:

```text
Payment authorization:
very low latency

Executive dashboard:
seconds may be acceptable

Monthly report:
minutes or hours may be acceptable
```

Latency is a business requirement, not just a database metric.

---

# 67. Concurrency

Concurrency asks:

> How many operations are active at approximately the same time?

Example:

```text
10 users
```

versus:

```text
10,000 simultaneous application requests
```

The same query can behave differently under heavy concurrency.

A database can be fast for one query and slow when thousands of users compete for resources.

---

# 68. Workload Profile

A useful way to profile a workload:

```text
Workload
   ↓
Read / write ratio
   ↓
Rows touched
   ↓
Query complexity
   ↓
Concurrency
   ↓
Latency requirement
   ↓
Consistency requirement
   ↓
Storage / processing architecture
```

This is one of the most important diagrams in this lesson.

---

# 69. Workload Profile Examples

| Workload | QPS | Rows scanned | Latency | Concurrency | Typical shape |
|---|---:|---:|---|---|---|
| Customer lookup | High | Few | Very low | High | OLTP |
| Payment write | High | Few | Very low | High | OLTP |
| Monthly revenue | Low/medium | Huge | Higher | Medium | OLAP |
| ML feature build | Low | Huge | Batch-tolerant | Batch-oriented | OLAP |
| Executive dashboard | Medium | Large | Seconds/minutes | Variable | OLAP |

The values are illustrative.

Do not treat them as industry benchmark thresholds.

---

# 70. Workload Shape Beats Product Name

A database product does not inherently define the workload.

The same database technology can sometimes be used for:

```text
OLTP
```

or:

```text
analytical workloads
```

depending on scale and workload shape.

Therefore:

```text
database product
≠
workload
```

Instead:

```text
workload
=
access pattern
+
data volume
+
query shape
+
concurrency
+
latency
+
consistency
```

---

# 71. Why Indexes Matter in OLTP

Suppose:

```sql
SELECT *
FROM orders
WHERE order_id = ?;
```

If `order_id` is indexed appropriately, the database may find the requested row efficiently.

Indexes can be very useful for selective lookups.

But indexes also have costs:

- storage
- write overhead
- maintenance
- memory/cache usage

Therefore:

> Indexes are workload-specific optimization structures.

---

# 72. Why Indexes Do Not Solve Every OLAP Problem

Suppose the query is:

```sql
SELECT
    country,
    SUM(amount)
FROM orders
GROUP BY country;
```

If the query needs most rows, an index may not avoid the fundamental need to process a large amount of data.

Adding:

```sql
CREATE INDEX idx_orders_country
ON orders(country);
```

may help particular access patterns.

It does not magically turn a large aggregation into a one-row lookup.

This is a major beginner lesson.

---

# 73. The Required SQLite Benchmark

The roadmap requires:

```text
oltp_vs_olap_bench.py
```

For this Markdown lesson, the complete learner-ready implementation is provided below.

Copy the code below into `oltp_vs_olap_bench.py` in your learning workspace, then run it to perform the benchmark.

The benchmark will:

1. create a SQLite table
2. generate 1,000,000 orders
3. run 10,000 primary-key lookups
4. run a full-table aggregation
5. add an index on `country`
6. rerun the benchmark
7. store equivalent data as a toy column-oriented layout
8. compare bytes read when summing one column

---

# 74. Resource Warning Before Running the Benchmark

The one-million-row benchmark is deliberately larger than the earlier exercises.

It can consume:

- disk space
- CPU
- memory
- time

The implementation should therefore:

- insert rows in batches
- use SQLite transactions
- avoid creating one million large Python objects at once
- generate deterministic values
- separate setup time from query-measurement time

The benchmark is still a local teaching experiment.

It is not a production capacity test.

---

# 75. Benchmark Data Model

Use:

```sql
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    country TEXT NOT NULL,
    amount REAL NOT NULL,
    created_at TEXT NOT NULL
);
```

The logical fields are:

```text
order_id
customer_id
country
amount
created_at
```

---

# 76. Deterministic Data Generation

Reproducibility matters.

Use:

```python
import random

random.seed(42)
```

Then the same generation logic can produce the same sequence of pseudo-random choices.

The exact data values are not important.

The repeatability is.

---

# 77. Memory-Conscious Bulk Insert

Do not create:

```python
orders = [ ... one million objects ... ]
```

unless you deliberately want to consume that memory.

Prefer batches:

```python
batch = []

for order_id in range(1, 1_000_001):
    batch.append(...)

    if len(batch) == 10_000:
        conn.executemany(...)
        batch.clear()
```

This keeps memory usage bounded.

---

# 78. Benchmark Implementation — Setup

```python
from __future__ import annotations

import csv
import random
import sqlite3
import statistics
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


DB_PATH = Path("oltp_vs_olap_bench.db")
COLUMNAR_DIR = Path("columnar")
ROW_FILE = Path("rows.csv")

ROW_COUNT = 1_000_000
LOOKUP_COUNT = 10_000
INSERT_BATCH_SIZE = 10_000


def create_table(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS orders")

    conn.execute(
        """
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            country TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.commit()
```

---

# 79. Benchmark Implementation — Data Generation

```python
def generate_orders(
    conn: sqlite3.Connection,
    row_count: int = ROW_COUNT,
) -> None:
    random.seed(42)

    countries = [
        "India",
        "US",
        "UK",
        "Germany",
        "Japan",
    ]

    base_time = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    batch = []

    for order_id in range(
        1,
        row_count + 1,
    ):
        created_at = (
            base_time
            + timedelta(
                minutes=order_id % 500_000
            )
        )

        customer_id = (
            1 + (order_id % 100_000)
        )

        country = countries[
            order_id % len(countries)
        ]

        amount = round(
            10
            + (order_id % 10_000) * 0.37,
            2,
        )

        batch.append(
            (
                order_id,
                customer_id,
                country,
                amount,
                created_at.isoformat(),
            )
        )

        if len(batch) >= INSERT_BATCH_SIZE:
            conn.executemany(
                """
                INSERT INTO orders (
                    order_id,
                    customer_id,
                    country,
                    amount,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                batch,
            )

            batch.clear()

    if batch:
        conn.executemany(
            """
            INSERT INTO orders (
                order_id,
                customer_id,
                country,
                amount,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            batch,
        )

    conn.commit()
```

---

# 80. Why the Generator Is Deterministic

The values are derived from:

```python
order_id
```

and a fixed random seed where random selection is used.

That means the experiment is easier to reproduce.

This does not make the benchmark statistically perfect.

It simply reduces unnecessary variability in the dataset.

---

# 81. Benchmark Implementation — Row Count

Before measuring queries:

```python
def count_rows(
    conn: sqlite3.Connection,
) -> int:
    row = conn.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()

    return int(row[0])
```

You should verify:

```text
1,000,000
```

before benchmarking.

---

# 82. Benchmark Implementation — 10,000 PK Lookups

Use:

```python
def benchmark_primary_key_lookups(
    conn: sqlite3.Connection,
    count: int = LOOKUP_COUNT,
) -> dict[str, float]:
    ids = [
        1 + (
            (i * 7919) % ROW_COUNT
        )
        for i in range(count)
    ]

    start = time.perf_counter()

    for order_id in ids:
        conn.execute(
            """
            SELECT
                order_id,
                customer_id,
                country,
                amount,
                created_at
            FROM orders
            WHERE order_id = ?
            """,
            (order_id,),
        ).fetchone()

    duration = (
        time.perf_counter() - start
    )

    return {
        "total_seconds": duration,
        "average_ms": (
            duration / count
        ) * 1000,
        "qps": count / duration,
    }
```

---

# 83. Why This Represents OLTP

The benchmark does:

```text
10,000
```

small selective lookups.

Each lookup asks for:

```text
one order
```

by primary key.

Conceptually:

```text
request
→ locate entity
→ return entity
```

That represents an OLTP-style access pattern.

---

# 84. Benchmark Implementation — OLAP Aggregation

Use SQLite-compatible SQL:

```python
def benchmark_aggregation(
    conn: sqlite3.Connection,
) -> dict[str, float]:
    start = time.perf_counter()

    rows = conn.execute(
        """
        SELECT
            country,
            substr(created_at, 1, 7) AS month,
            SUM(amount) AS revenue
        FROM orders
        GROUP BY
            country,
            month
        """
    ).fetchall()

    duration = (
        time.perf_counter() - start
    )

    return {
        "total_seconds": duration,
        "result_rows": float(len(rows)),
    }
```

---

# 85. Why This Represents OLAP

The query:

```text
GROUP BY country, month
```

requires information from a large portion of the dataset.

The system has to perform an analytical operation:

```text
scan
→ group
→ sum
→ return aggregate
```

This is fundamentally different from:

```text
WHERE order_id = ?
```

---

# 86. Warm-Up Before Measurement

For a simple local experiment, a warm-up can help reduce first-run effects.

For example:

```python
def warm_up(
    conn: sqlite3.Connection,
) -> None:
    conn.execute(
        """
        SELECT *
        FROM orders
        WHERE order_id = ?
        """,
        (1,),
    ).fetchone()

    conn.execute(
        """
        SELECT
            country,
            SUM(amount)
        FROM orders
        GROUP BY country
        """
    ).fetchall()
```

Do not treat a warm-up as a guarantee that the benchmark matches a production cache state.

---

# 87. Repeat the Benchmark

A stronger experiment can repeat each test several times.

```python
def repeat(
    fn,
    runs: int = 5,
) -> list[dict[str, float]]:
    results = []

    for _ in range(runs):
        results.append(fn())

    return results
```

Then inspect:

```text
median
average
minimum
maximum
```

For this lesson, median is often a useful summary because it reduces the impact of one unusually slow run.

---

# 88. Why Use `time.perf_counter()`?

Use:

```python
time.perf_counter()
```

for elapsed-time measurement.

It is designed for measuring durations.

Do not use wall-clock timestamps such as:

```python
datetime.now()
```

for benchmark duration measurements.

---

# 89. Benchmark Index Experiment

Add:

```sql
CREATE INDEX idx_orders_country
ON orders(country);
```

Python:

```python
def create_country_index(
    conn: sqlite3.Connection,
) -> None:
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_orders_country
        ON orders(country)
        """
    )

    conn.commit()
```

Then rerun the benchmark.

---

# 90. What to Measure After Adding the Index

Record:

```text
10,000 PK lookup time
aggregation time
```

Compare:

```text
before index
vs
after index
```

Then ask:

```text
Did PK lookup performance change?
Did the aggregation performance change?
Why?
```

The answer depends on how the query actually uses the indexed column.

---

# 91. Important Benchmark Nuance

The aggregation query groups by:

```text
country
month
```

The index is only:

```text
country
```

SQLite may or may not use it in the way you expect.

That is precisely why the experiment matters.

Do not begin with:

> "Index makes everything faster."

Begin with:

> "What access pattern can this index help?"

---

# 92. Benchmark Results Table

Record your actual results:

| Test | Before index | After index | Observation |
|---|---:|---:|---|
| 10,000 PK lookups | ___ | ___ | ___ |
| Country/month aggregation | ___ | ___ | ___ |
| Amount-only column read | ___ | ___ | ___ |

Do not copy benchmark numbers from this lesson.

Run the experiment on your machine.

---

# 93. Toy Row-Oriented File

The roadmap also requires equivalent data represented as one row file.

Create:

```text
rows.csv
```

For example:

```text
order_id,customer_id,country,amount,created_at
1,2,India,100.50,2026-01-01T00:00:00+00:00
2,3,US,50.25,2026-01-01T00:01:00+00:00
...
```

A query needing only:

```text
amount
```

still has to read through the row representation.

This is a teaching abstraction.

---

# 94. Toy Column-Oriented Layout

Create:

```text
columnar/
    order_id.csv
    customer_id.csv
    country.csv
    amount.csv
    created_at.csv
```

Now:

```text
amount.csv
```

contains only amount values.

This represents a crude column-oriented layout.

It is not a database storage engine.

---

# 95. Why Build a Toy Columnar Layout?

The purpose is to make one principle visible:

```text
Row layout:
all attributes travel together

Column layout:
individual attributes can be read independently
```

This helps explain why analytical systems often use columnar formats.

For physical storage formats, compression, and file-layout decisions, see **Module 2.5 — Data Formats, Compression, and File Layout**.

---

# 96. Writing the Toy Columnar Files

```python
def write_toy_columnar_files(
    conn: sqlite3.Connection,
) -> None:
    COLUMNAR_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    columns = {
        "order_id": "order_id.csv",
        "customer_id": "customer_id.csv",
        "country": "country.csv",
        "amount": "amount.csv",
        "created_at": "created_at.csv",
    }

    handles = {}
    writers = {}

    try:
        for column, filename in columns.items():
            path = COLUMNAR_DIR / filename

            handle = path.open(
                "w",
                newline="",
                encoding="utf-8",
            )

            handles[column] = handle
            writers[column] = csv.writer(handle)

        cursor = conn.execute(
            """
            SELECT
                order_id,
                customer_id,
                country,
                amount,
                created_at
            FROM orders
            ORDER BY order_id
            """
        )

        for row in cursor:
            writers["order_id"].writerow(
                [row[0]]
            )
            writers["customer_id"].writerow(
                [row[1]]
            )
            writers["country"].writerow(
                [row[2]]
            )
            writers["amount"].writerow(
                [row[3]]
            )
            writers["created_at"].writerow(
                [row[4]]
            )

    finally:
        for handle in handles.values():
            handle.close()
```

The row-oriented counterpart writes the same records into a single wide CSV file. This creates the row-oriented representation that the byte-comparison experiment reads alongside the columnar files.

```python
def write_toy_row_file(
    conn: sqlite3.Connection,
) -> None:
    with ROW_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "order_id",
                "customer_id",
                "country",
                "amount",
                "created_at",
            ]
        )

        cursor = conn.execute(
            """
            SELECT
                order_id,
                customer_id,
                country,
                amount,
                created_at
            FROM orders
            ORDER BY order_id
            """
        )

        for row in cursor:
            writer.writerow(row)
```

---

# 97. Measuring File Bytes

Use:

```python
def file_size(path: Path) -> int:
    return path.stat().st_size
```

Then compare:

```python
row_file_bytes = file_size(
    ROW_FILE
)

amount_file_bytes = file_size(
    COLUMNAR_DIR / "amount.csv"
)
```

---

# 98. The Amount-Only Question

Suppose the analytical query is conceptually:

```sql
SELECT SUM(amount)
FROM orders;
```

In the toy row layout:

```text
rows.csv
```

contains:

```text
order_id
customer_id
country
amount
created_at
```

You need to read through a file containing all those fields.

In the toy column layout:

```text
amount.csv
```

contains only:

```text
amount
```

Therefore:

```text
bytes required for amount-only access
```

can be significantly smaller.

That is the core lesson.

---

# 99. Measuring Bytes Read in a Toy Experiment

A simple file-size comparison is not identical to measuring actual operating-system bytes read.

It is a proxy.

Use:

```python
def compare_amount_bytes() -> dict[str, int]:
    row_bytes = ROW_FILE.stat().st_size

    amount_bytes = (
        COLUMNAR_DIR / "amount.csv"
    ).stat().st_size

    return {
        "row_layout_bytes": row_bytes,
        "amount_column_bytes": amount_bytes,
    }
```

Then explain:

> This compares stored file sizes, not exact physical I/O performed by a production query engine.

That distinction matters.

---

# 100. Toy Row vs Column Experiment

| Layout | Data needed for `SUM(amount)` | File representation | Teaching point |
|---|---|---|---|
| Row-oriented toy file | All row fields are present in each line | One wide CSV | Unrelated columns travel with amount |
| Column-oriented toy files | Only `amount.csv` | One file per column | Needed column can be read independently |

---

# 101. Benchmark Scientific Discipline

Treat the benchmark as an experiment.

Use:

- `time.perf_counter()`
- repeat runs
- warm-up where appropriate
- deterministic data
- separate setup from measurement
- identical query workloads
- consistent machine state where practical

Record:

```text
OS
Python version
SQLite version
CPU
RAM
storage device
```

The exact results depend on environment.

---

# 102. Why Laptop Benchmarks Are Limited

A local SQLite benchmark does not reproduce:

- distributed storage
- multiple workers
- network latency
- cloud object storage
- warehouse execution engines
- parallel execution
- production caching
- thousands of concurrent users
- failure recovery

Therefore:

> **Use the benchmark to understand workload behavior, not to predict production performance.**

---

# 103. Workload Interpretation

Suppose your results show:

```text
PK lookups:
very fast

aggregation:
much slower
```

The important conclusion is not:

```text
SQLite is bad at analytics.
```

That is too broad.

The correct conclusion is:

> A large aggregation touches a much larger amount of information and performs more work than a selective point lookup.

That is a workload observation.

---

# 104. Why QPS Alone Is Not Enough

Suppose:

```text
System A:
5,000 QPS
```

and:

```text
System B:
100 QPS
```

You might assume A is more demanding.

But what if:

```text
A:
5,000 one-row lookups
```

and:

```text
B:
100 queries that each scan 10 billion rows
```

System B may require substantially more total compute.

Therefore:

```text
QPS
+
rows touched
+
query complexity
+
latency
+
concurrency
```

give a more useful workload profile.

---

# 105. OLTP Workload as a Set of Numbers

Imagine:

```text
QPS            = 5,000
Rows/query     = 1–10
Latency target = <100 ms
Concurrency    = high
Write ratio    = high
```

This is an OLTP-shaped workload.

---

# 106. OLAP Workload as a Set of Numbers

Imagine:

```text
QPS            = 20
Rows/query     = 50 million
Latency target = seconds/minutes
Concurrency    = medium
Write ratio    = low
```

This is an OLAP-shaped workload.

These numbers are illustrative.

The point is to think quantitatively.

---

# 107. Data Volume vs Workload Volume

A small database can still contain an analytical workload.

A large database can still contain an operational workload.

Therefore:

```text
database size
≠
workload type
```

For example:

```text
10 GB database
```

could support:

```text
high-QPS OLTP
```

while:

```text
1 TB database
```

could have relatively light analytical usage.

The workload is defined by access behavior.

---

# 108. Read/Write Ratio

Another useful signal:

```text
How much does the system read?
How much does it write?
```

OLTP often has:

```text
many writes + many small reads
```

OLAP often has:

```text
many reads + relatively few writes
```

This is a tendency.

Analytical systems can absolutely ingest and mutate data.

The distinction is about dominant workload shape.

---

# 109. Consistency Requirements

An application processing money may care deeply about:

```text
correct current state
```

A monthly analytics query may care more about:

```text
historical completeness
+
analytical correctness
```

Both need correctness.

But the required consistency characteristics can differ.

This can influence architecture.

---

# 110. Freshness Requirements

A production application may need:

```text
latest customer balance
```

while an executive report may be acceptable with:

```text
data updated yesterday
```

This connects Topic 05 to the earlier processing-mode discussion.

The workload should be evaluated together with:

```text
freshness
latency
consumer expectations
```

---

# 111. Why OLTP and OLAP Often Separate

A common progression is:

```text
Stage 1
Application
    ↓
OLTP DB
    ↓
Light analytics
```

Then:

```text
Stage 2
Application
    ↓
Primary OLTP
    ↓
Read Replica
    ↓
Some read-heavy workloads
```

Then:

```text
Stage 3
Application
    ↓
OLTP
    ↓
CDC
    ↓
Analytical Platform
    ↓
BI / ML / Analytics
```

Alternative:

```text
Stage 4
HTAP or another integrated architecture
```

The architecture evolves when workload requirements justify it.

---

# 112. Architecture Progression Example

Suppose a small SaaS product begins with:

```text
10 requests/sec
```

and:

```text
100,000 rows
```

One database may be enough.

After growth:

```text
5,000 requests/sec
+
10 billion events
+
heavy analytics
```

the workload shapes are now very different.

The company may need:

```text
OLTP isolation
+
analytical infrastructure
```

The reason is not:

```text
the company became "more professional."
```

The reason is:

```text
the workload changed.
```

---

# 113. Real-World Case Study — Banking

Banking often contains very different workloads.

## OLTP workload

```text
Post transaction
Update balance
Authorize card
Record payment
```

Characteristics:

- many small operations
- low latency
- high concurrency
- strong correctness requirements

## OLAP workload

```text
Analyze five years of transactions
Calculate customer segmentation
Build fraud features
Produce regulatory reports
```

Characteristics:

- large scans
- historical data
- aggregations
- complex joins

Therefore it can be useful to separate the workload environments.

A real bank's architecture will vary substantially.

---

# 114. Banking Architecture Example

Conceptually:

```text
Core Banking / Payment Systems
        ↓
      OLTP
        ↓
      CDC
        ↓
Analytical Platform
        ↓
BI / Fraud Analytics / ML / Reporting
```

This is a conceptual model, not a universal bank architecture.

---

# 115. Real-World Case Study — E-commerce

## OLTP

```text
orders
inventory
payments
```

Operations:

```text
create order
update inventory
record payment
```

## OLAP

```text
sales trends
customer lifetime value
product performance
```

The same business creates both workloads.

---

# 116. E-commerce Query Comparison

### OLTP

```sql
SELECT *
FROM orders
WHERE order_id = 1001;
```

### OLAP

```sql
SELECT
    country,
    SUM(amount) AS revenue
FROM orders
GROUP BY country;
```

Both use the same logical business entity.

The access patterns are different.

---

# 117. Real-World Case Study — Healthcare

## OLTP

```text
patient registration
appointment creation
billing update
```

## OLAP

```text
patient utilization analysis
historical operational reports
resource trends
```

Operational systems may need low-latency transactional behavior.

Analytical systems may need large historical scans.

---

# 118. Real-World Case Study — Ride-Sharing

## OLTP

```text
trip state
driver status
rider request
payment
```

## OLAP

```text
city-level demand analysis
driver performance
route analysis
historical trip metrics
```

The operational system and analytical platform can therefore have different access patterns.

---

# 119. Real-World Case Study — SaaS

## OLTP

```text
subscription changes
user settings
organization records
```

## OLAP

```text
feature usage
customer health
retention analysis
product analytics
```

Again:

```text
same business
→ multiple workloads
```

---

# 120. Architecture Decision Exercise

For every scenario, identify:

```text
Workload
Why
Expected access pattern
Rows touched
Latency requirement
Concurrency
Possible architecture
```

---

## Scenario 1 — Banking API

> A banking API processes thousands of account transactions every second.

Think:

```text
small operations
high concurrency
low latency
writes
```

Likely workload category:

```text
OLTP
```

---

## Scenario 2 — Five Years of Revenue

> Finance calculates monthly revenue by country across five years.

Think:

```text
large historical scan
aggregation
analytical result
```

Likely workload category:

```text
OLAP
```

---

## Scenario 3 — ML Feature Build

> A machine-learning team scans billions of historical events to create features.

Think:

```text
large scan
large transformation
historical data
```

Likely workload category:

```text
OLAP
```

---

## Scenario 4 — Customer Lookup

> An application needs a customer profile under low latency.

Think:

```text
point lookup
small result
high concurrency
```

Likely workload category:

```text
OLTP
```

---

## Scenario 5 — Five-Minute Dashboard

> Operations needs a dashboard refreshed every few minutes.

Think:

```text
analytical workload
+
freshness requirement
```

Possible architecture:

```text
OLAP / analytical system
```

with a suitable update pattern.

---

# 121. Architecture Decision Record Exercise

## Scenario

> An e-commerce company currently runs customer-facing APIs and heavy analytics on one PostgreSQL database. The analytics team now runs long aggregation queries during business hours, and customer API latency is becoming unpredictable.

Write:

```text
Context
Current workload
Problem
Options
Decision
Consequences
```

Consider options such as:

```text
query optimization
indexes
read replica
analytical replica
CDC into analytical platform
HTAP-style architecture
other justified approach
```

Do not assume one predetermined answer.

The goal is to reason from workload requirements.

---

# 122. ADR — Reasoning Guidance

A strong analysis should include:

## Context

```text
customer-facing OLTP
+
heavy analytical queries
```

## Problem

```text
resource contention
→ unpredictable operational latency
```

## Options

```text
optimize
isolate reads
replicate changes
separate workloads
integrate workloads
```

## Decision

Choose based on:

```text
latency
scale
complexity
freshness
consistency
cost
```

## Consequences

Explain:

```text
what improves
what new complexity appears
what new failure modes appear
```

---

# 123. Trade-Off — Single Database

## Potential benefits

- simple deployment
- fewer components
- lower operational complexity
- easier local development

## Potential limitations

- workload contention
- shared resource pressure
- difficult independent scaling
- analytical queries can affect operational performance

Use one database when the workload is small enough and the trade-offs are acceptable.

---

# 124. Trade-Off — Read Replica

## Potential benefits

- offload reads
- protect some primary capacity
- relatively familiar architecture

## Costs

- replication lag
- extra infrastructure
- analytical workload can still overload replica
- scaling remains connected to the database design

A read replica is not a universal analytics solution.

---

# 125. Trade-Off — CDC to Analytical Platform

## Potential benefits

- workload isolation
- analytical scale can differ from OLTP scale
- near-real-time propagation can be possible
- analytical consumers do not compete directly with the primary database

## Costs

- additional infrastructure
- change-management complexity
- ordering/recovery concerns
- schema evolution concerns
- operational monitoring requirements

---

# 126. Trade-Off — HTAP

## Potential benefits

- tightly integrated operational and analytical access
- potentially lower data movement
- analytics closer to operational state

## Costs

- mixed-workload complexity
- resource contention
- specialized architecture
- scaling and isolation challenges

---

# 127. Architecture Decision Principle

Use:

```text
Context
→ Options
→ Decision
→ Consequences
```

not:

```text
technology
→ architecture
```

This pattern is reusable across Data Engineering.

---

# 128. Common Misconception — "OLTP Means Small Database"

False.

An OLTP database can be enormous.

The defining property is the workload:

```text
many operational transactions
+
small/targeted operations
+
high concurrency
+
low latency
```

---

# 129. Common Misconception — "OLAP Means Huge Database"

Not necessarily.

A small dataset can be queried analytically.

The defining property is:

```text
analytical access pattern
```

not raw database size.

---

# 130. Common Misconception — "OLTP Databases Cannot Run Analytics"

They can run analytical queries.

The concern is:

> Should heavy analytical queries compete with business-critical transactional work on the same resources?

For small systems, the answer may be yes.

For larger or latency-sensitive systems, isolation may be justified.

---

# 131. Common Misconception — "OLAP Databases Cannot Perform Writes"

Incorrect.

Analytical systems can ingest and modify data.

The distinction is not:

```text
reads vs writes
```

alone.

It is:

```text
workload shape
```

---

# 132. Common Misconception — "Every OLAP System Is a Warehouse"

Not necessarily.

Analytical workloads can run on various data systems.

This topic is about workload characteristics.

Topic 06 will cover:

```text
warehouse
lake
lakehouse
```

in greater depth.

---

# 133. Common Misconception — "Every OLTP System Is Relational"

Relational databases are common in OLTP.

But workload architecture can be implemented using other data-store patterns.

Do not memorize:

```text
OLTP = relational
```

as an absolute law.

The key is the access pattern.

---

# 134. Common Misconception — "Columnar Storage Is Always Faster"

No.

Columnar storage is often strong for:

```text
large scans
few columns
aggregations
analytical access
```

It is not automatically ideal for:

```text
single-entity full-row operations
```

---

# 135. Common Misconception — "Indexes Make Every Query Faster"

Indexes help specific access patterns.

They can also:

- consume storage
- increase write overhead
- require maintenance
- complicate optimization

A workload should determine index strategy.

---

# 136. Common Misconception — "Read Replicas Solve Analytics Completely"

A read replica can reduce primary read pressure.

It does not necessarily provide:

```text
columnar storage
analytical optimization
independent historical scaling
```

The replica itself has resources and workload limits.

---

# 137. Common Misconception — "CDC Is the Same as a Read Replica"

No.

```text
Read replica
→ copy/read scaling

CDC
→ propagate source changes
```

They can be used together.

---

# 138. Common Misconception — "HTAP Means You Never Need Separate Systems"

No.

HTAP is an architectural option.

It may make sense in some workloads and be inappropriate in others.

---

# 139. Common Misconception — "Normalized Is Always Better"

No.

Normalization is often useful for operational consistency.

Analytical workloads may benefit from denormalization or dimensional modeling.

Choose based on access patterns.

---

# 140. Common Misconception — "Denormalized Is Always Better"

Also false.

Denormalization can introduce:

- duplicated data
- update complexity
- storage overhead
- consistency challenges

It can be valuable for analytical access patterns.

---

# 141. Common Misconception — "QPS Alone Tells You the Architecture"

No.

You need at least:

```text
QPS
+
rows touched
+
query complexity
+
latency
+
concurrency
+
consistency
```

---

# 142. Failure Modes and Controls

| Problem | Why it happens | Potential impact | Conceptual mitigation |
|---|---|---|---|
| Heavy analytics on OLTP | Shared resources | Slow application queries | Workload isolation |
| Excessive concurrency | Many simultaneous requests | CPU/memory/connection pressure | Scale or isolate workload |
| Long aggregation | Large scan | Resource saturation | Analytical platform / optimization |
| Replica lag | Asynchronous replication | Stale reads | Consumer-aware read routing |
| Replica overload | Heavy analytical queries | Replica becomes bottleneck | Separate analytical platform |
| CDC interruption | Capture or delivery failure | Analytical copy becomes stale | Monitoring / recovery |
| Incorrect workload assumptions | Architecture based on guesses | Poor scaling | Measure workload |
| Bad index | Index not aligned with query | Unnecessary cost / little benefit | Workload-driven indexing |
| Storage mismatch | Layout not suited to access pattern | Excessive I/O | Match storage to workload |

---

# 143. Production Architecture: What Changes?

A toy system:

```text
Application
    ↓
SQLite
    ↓
Light analytics
```

may be enough for a small project.

A production system may evolve:

```text
Application
    ↓
OLTP Database
    ↓
CDC
    ↓
Analytical Platform
    ↓
BI / ML / Analytics
```

or:

```text
Application
    ↓
OLTP
    ↓
Read Replica
```

or:

```text
Integrated HTAP-style system
```

depending on requirements.

---

# 144. Production Concern — Workload Isolation

When two workloads have different priorities:

```text
customer transactions
```

and:

```text
historical analytics
```

isolation can prevent one from dominating the other.

Isolation can occur through:

- separate database instances
- read replicas
- separate analytical systems
- separate compute
- workload management policies

The specific implementation depends on platform architecture.

---

# 145. Production Concern — Query Governance

A production data platform may need controls around:

- expensive queries
- concurrency
- resource pools
- timeouts
- access
- priorities

This is an early introduction to workload management.

Detailed database governance is covered later.

---

# 146. Production Concern — Freshness

If CDC feeds an analytical platform:

```text
source changes
→ captured
→ delivered
→ applied
→ queryable
```

There is a delay.

Therefore the analytical system may be:

```text
near real-time
```

without being:

```text
instant
```

This connects to Topic 03 and Topic 08.

---

# 147. Production Concern — Consistency

Suppose:

```text
OLTP:
order status = PAID

Analytics:
order status = PENDING
```

The difference may simply be replication delay.

Consumers need to know whether:

```text
analytical data is eventually consistent
```

or:

```text
must match operational state immediately
```

This is a workload and consumer requirement.

---

# 148. Production Concern — Backfills

An analytical platform often needs:

```text
historical recomputation
```

This is easier when the analytical system is separated from the transactional workload.

You do not want a large historical rebuild to compete directly with customer-facing transactions.

---

# 149. Production Concern — Read Path vs Write Path

An OLTP system often has:

```text
write path
→ preserve operational state
```

An analytical platform often has:

```text
read/compute path
→ derive information
```

Keeping these workloads separate can reduce interference.

---

# 150. Advanced Mental Model — Workload Is a Vector

Instead of labeling a system simply:

```text
OLTP
```

think of the workload as a vector:

```text
QPS
Rows scanned
Read/write ratio
Latency
Concurrency
Consistency
Query complexity
Data volume
Freshness
```

Example:

```text
System A:
high QPS
low rows/query
low latency
high concurrency
many writes

System B:
low QPS
high rows/query
higher latency tolerance
large scans
many reads
```

The labels become shorthand for the workload profile.

---

# 151. Advanced Mental Model — Resource Competition

A database has finite resources:

```text
CPU
Memory
I/O
Network
Connections
Cache
Locks / concurrency structures
```

Different queries consume those resources differently.

An OLTP point lookup might use:

```text
small CPU
small I/O
short duration
```

A large OLAP aggregation might use:

```text
large scan
substantial CPU
memory for grouping
longer execution
```

When both workloads compete:

```text
resource contention
```

can become the architecture problem.

---

# 152. Advanced Mental Model — Query Shape

A query's SQL text is not enough.

You should ask:

```text
How selective is it?
How many rows can it touch?
How many columns does it need?
Does it sort?
Does it aggregate?
Does it join?
How much intermediate data can it create?
```

This is **query-shape thinking**.

---

# 153. Point Lookup vs Large Scan

## Point lookup

```sql
SELECT *
FROM orders
WHERE order_id = 12345;
```

Mental model:

```text
Find one entity.
```

## Large scan

```sql
SELECT
    country,
    SUM(amount)
FROM orders
GROUP BY country;
```

Mental model:

```text
Read lots of entities.
Summarize them.
```

This simple distinction should become automatic.

---

# 154. Why Analytical Systems Like Wide Historical Data

Analytics frequently asks:

```text
What happened across many entities
over a long period?
```

That encourages:

```text
large historical datasets
+
scan-heavy computation
```

OLTP asks more often:

```text
What is the state of this entity right now?
```

These are different questions.

---

# 155. Why OLTP Often Values Narrow Transactions

An operational transaction is often:

```text
read a few rows
update a few rows
commit
```

This helps keep latency predictable.

It is fundamentally different from:

```text
scan 1 billion rows
group by 12 dimensions
calculate multiple aggregates
```

---

# 156. Why OLAP Often Values Throughput

A dashboard query may not need:

```text
10 millisecond response
```

if:

```text
20 seconds
```

is acceptable.

Instead, the system may value:

```text
scan many rows efficiently
```

This is a throughput-oriented analytical problem.

Again, the exact target is workload-specific.

---

# 157. Three Different Meanings of "Fast"

A common source of confusion is the word:

```text
fast
```

Fast can mean:

### Low latency

```text
one request completes quickly
```

### High throughput

```text
many operations completed per second
```

### High scan efficiency

```text
large amounts of data processed efficiently
```

OLTP often emphasizes:

```text
low latency + high concurrency
```

OLAP often emphasizes:

```text
large-scan efficiency + analytical throughput
```

---

# 158. Architecture Does Not Mean One Database Per Query Type

Do not overreact.

A mature architecture does not necessarily mean:

```text
one database for point lookups
one database for every dashboard
one database for every ML job
```

Instead, group workloads according to meaningful isolation boundaries.

The question is:

> Which workloads create enough interference or different scaling needs to justify separation?

---

# 159. A Small System Can Mix Workloads

Example:

```text
Application
 ↓
SQLite
 ↓
simple daily report
```

This may be acceptable.

As workload grows:

```text
Application
 ↓
OLTP
 ↓
CDC
 ↓
Analytical
```

The architecture evolves when the workload justifies it.

---

# 160. Benchmark Cleanup

After experiments, clean up:

```text
oltp_vs_olap_bench.db
rows.csv
columnar/
```

For example, from Python:

```python
def cleanup() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    if ROW_FILE.exists():
        ROW_FILE.unlink()

    if COLUMNAR_DIR.exists():
        for path in COLUMNAR_DIR.iterdir():
            path.unlink()

        COLUMNAR_DIR.rmdir()
```

Use cleanup only after recording your results.

Do not accidentally delete unrelated files.

---

# 161. Benchmark Driver

A compact driver can look like:

```python
def run_benchmark() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(
        DB_PATH
    )

    try:
        create_table(conn)
        generate_orders(conn)

        assert (
            count_rows(conn)
            == ROW_COUNT
        )

        warm_up(conn)

        before_pk = benchmark_primary_key_lookups(
            conn
        )

        before_olap = benchmark_aggregation(
            conn
        )

        create_country_index(conn)

        after_pk = benchmark_primary_key_lookups(
            conn
        )

        after_olap = benchmark_aggregation(
            conn
        )

        print(
            "PK before:",
            before_pk,
        )

        print(
            "PK after:",
            after_pk,
        )

        print(
            "OLAP before:",
            before_olap,
        )

        print(
            "OLAP after:",
            after_olap,
        )

        write_toy_row_file(conn)
        write_toy_columnar_files(conn)

        amount_bytes = compare_amount_bytes()

        print(
            "Amount bytes comparison:",
            amount_bytes,
        )

    finally:
        conn.close()
```

The row-file and columnar-file comparison now runs inside this same driver, immediately after the primary-key and aggregation benchmarks complete.

---

# 162. Important Benchmark Limitation

SQLite is an embedded relational database.

It is useful for:

- learning SQL
- learning indexes
- learning transactions
- local experiments
- demonstrating workload differences

It does not reproduce:

- distributed query execution
- production warehouse internals
- cloud-scale concurrency
- columnar analytical engines

Therefore:

> **The benchmark teaches workload intuition, not production capacity planning.**

---

# 163. Performance Reasoning Questions

After the benchmark, answer:

1. Why did primary-key lookups behave differently from aggregation?
2. Why did the `country` index affect some workloads more than others?
3. Why doesn't an index automatically solve a large aggregation?
4. Why can columnar layout help projection-heavy analytics?
5. Why does concurrency change architecture?
6. Why might a read replica still be insufficient for analytics?
7. Why is CDC useful for workload isolation?

---

# 164. Answer Guidance — PK Lookup

A primary-key lookup is highly selective.

The workload asks:

```text
find one known entity
```

This generally touches far less data than a large aggregation.

---

# 165. Answer Guidance — Index Effect

An index is useful when it aligns with the access pattern.

An index on:

```text
country
```

can potentially help:

```text
WHERE country = ?
```

but a large aggregation may still need to process a large amount of data.

The engine decides whether the index is useful for the actual query plan.

---

# 166. Answer Guidance — Columnar Benefit

If a query needs:

```text
amount
```

only, a column-oriented representation can avoid carrying unrelated fields into the operation.

This can reduce:

```text
data read
```

and create opportunities for:

```text
compression
vectorized computation
```

---

# 167. Answer Guidance — Read Replica

A read replica moves read load away from the primary.

But:

```text
large analytical query
```

still consumes resources on the replica.

If analytics becomes large enough, a dedicated analytical platform can provide better isolation.

---

# 168. Answer Guidance — CDC

CDC allows:

```text
only changed data
```

to be propagated to a separate analytical environment.

That lets:

```text
OLTP workload
```

and:

```text
OLAP workload
```

scale more independently.

---

# 169. Advanced Architecture Scenario

Consider:

```text
Customer requests:
8,000/sec

Average lookup:
2 rows

Latency target:
<100 ms

Analytics:
50 queries/hour

Each analytics query:
500 million rows

Finance can wait:
30 minutes
```

What architecture would you investigate?

Do not answer only:

```text
OLTP
```

or:

```text
OLAP
```

Think:

```text
high-QPS operational workload
+
large analytical scans
+
very different latency requirements
```

That strongly suggests a workload-isolation discussion.

---

# 170. Another Advanced Scenario

Consider:

```text
Small internal application
100 users
50,000 rows
10 analytical queries/day
```

Would you immediately introduce:

```text
OLTP database
+
CDC
+
analytical platform
```

Not necessarily.

The architecture may be unnecessarily complex.

This reinforces:

> **Complexity should be justified by workload requirements.**

---

# 171. Advanced Scenario — Mixed Workload

Suppose:

```text
Operational writes:
1,000/sec

Analytics:
10 large queries/hour

Freshness requirement:
5 minutes
```

Possible options include:

```text
read replica
CDC → analytical platform
integrated architecture
```

The correct decision depends on:

```text
consistency
cost
team capability
query size
freshness
operational risk
```

---

# 172. Topic Boundary: Data Warehouse / Lake / Lakehouse

This topic tells you **why** analytical workloads often require different architecture.

The next topic explains **which analytical storage architectures** can support them.

Topic 06 will examine:

```text
warehouse
lake
lakehouse
```

in depth.

> **You need the workload mental model here; detailed platform architecture is covered next.**

---

# 173. Topic Boundary: Data Modelling

This topic introduces:

```text
normalized
denormalized
fact
dimension
```

Only as workload concepts.

Detailed modeling, keys, slowly changing dimensions, star schemas, and related techniques belong later in Module 2.8.

---

# 174. Topic Boundary: Database Connectivity

This lesson uses SQLite because it is available in the Python standard library.

It does not teach:

- connection pooling
- production PostgreSQL clients
- connection lifecycle
- database driver behavior
- production transaction isolation

Those topics belong later.

---

# 175. Topic Boundary: CDC

CDC is introduced conceptually.

You do not need to master:

- database log internals
- change-event formats
- Kafka
- Debezium
- exactly-once propagation
- distributed CDC recovery

Those are later topics.

---

# 176. Topic Boundary: Distributed Systems

This lesson does not teach:

- distributed query schedulers
- sharding algorithms
- distributed consensus
- distributed transactions
- cloud warehouse internals

The purpose is workload reasoning.

---

# 177. The Workload-First Checklist

Before choosing a database architecture, ask:

```text
[ ] What is the business workload?
[ ] Is it operational or analytical?
[ ] How many reads happen?
[ ] How many writes happen?
[ ] What is the read/write ratio?
[ ] What is the QPS?
[ ] How many rows does a typical query touch?
[ ] What is the latency target?
[ ] What is the concurrency?
[ ] What consistency is required?
[ ] How large is the data?
[ ] How quickly does it grow?
[ ] How fresh must analytical copies be?
[ ] Do workloads interfere with each other?
[ ] Can a simple architecture satisfy the requirement?
```

This checklist is more important than memorizing product names.

---

# 178. SQL Examples

## OLTP Point Lookup

```sql
SELECT *
FROM orders
WHERE order_id = ?;
```

### Why it is OLTP-shaped

```text
selective
small result
entity-oriented
```

---

## OLTP Update

```sql
UPDATE orders
SET status = ?
WHERE order_id = ?;
```

### Why it is OLTP-shaped

```text
small targeted write
current state
operational action
```

---

## OLAP Aggregation

```sql
SELECT
    country,
    SUM(amount) AS revenue
FROM orders
GROUP BY country;
```

### Why it is OLAP-shaped

```text
large scan
grouping
aggregation
analytical output
```

---

## OLAP Time Grouping in SQLite

```sql
SELECT
    substr(created_at, 1, 7) AS month,
    country,
    SUM(amount) AS revenue
FROM orders
GROUP BY
    month,
    country
ORDER BY
    month,
    country;
```

This is SQLite-compatible.

It demonstrates analytical grouping without relying on database-specific `DATE_TRUNC`.

---

# 179. Python Example — One Workload, Two Query Shapes

```python
def get_order(
    conn,
    order_id: int,
):
    return conn.execute(
        """
        SELECT
            order_id,
            customer_id,
            country,
            amount,
            created_at
        FROM orders
        WHERE order_id = ?
        """,
        (order_id,),
    ).fetchone()


def revenue_by_country(
    conn,
):
    return conn.execute(
        """
        SELECT
            country,
            SUM(amount) AS revenue
        FROM orders
        GROUP BY country
        """
    ).fetchall()
```

The Python code is simple.

The important lesson is the difference in workload shape.

---

# 180. Workload Profiling Exercise

Take any SQL query you write and record:

```text
Query:
____________________

Read or write:
____________________

Rows potentially touched:
____________________

Columns required:
____________________

Latency target:
____________________

Concurrency:
____________________

Consistency requirement:
____________________

Workload category:
____________________
```

This habit is useful far beyond this topic.

---

# 181. Performance Experiment — Query Shape

Create three queries:

### Query A

```sql
SELECT *
FROM orders
WHERE order_id = 42;
```

### Query B

```sql
SELECT
    country
FROM orders
WHERE order_id = 42;
```

### Query C

```sql
SELECT
    country,
    SUM(amount)
FROM orders
GROUP BY country;
```

Ask:

```text
Which touches the least data?
Which needs the largest scan?
Which is most selective?
```

---

# 182. Why "SELECT *" Matters

In analytical workloads,:

```sql
SELECT *
```

can request unnecessary columns.

If you only need:

```text
country
amount
```

prefer:

```sql
SELECT
    country,
    amount
FROM orders;
```

This is especially relevant to column-oriented systems because projection can reduce the amount of data that needs to be read.

The exact performance effect depends on the engine.

---

# 183. Production Query Thinking

A production engineer should ask:

```text
Do we need every column?
Can the filter reduce rows early?
How many rows are expected?
Is aggregation necessary?
Is the query repeated?
Can the result be precomputed?
```

These questions connect workload understanding to query optimization.

Detailed SQL optimization belongs later.

---

# 184. Workload Isolation Is Often About Predictability

Suppose two systems both have enough average capacity.

The problem may still be:

```text
unpredictable contention
```

Example:

```text
normal:
API latency = 50 ms

analytics starts:
API latency = 900 ms
```

Even if average CPU looks acceptable, the customer-facing workload has lost predictability.

This is one reason isolation can be valuable.

---

# 185. Average Performance vs Tail Latency

A production API is often sensitive to:

```text
p95
p99
```

latency.

You do not need to learn percentile monitoring deeply here.

The key idea is:

> An average can look healthy while a subset of requests becomes very slow.

Heavy analytical workloads can sometimes make tail latency worse.

---

# 186. Why Analytics on Production Databases Can Be Dangerous

The risk is not just:

```text
database becomes slow
```

It can affect:

```text
customer requests
payments
inventory
transactions
authentication
```

Therefore:

```text
analytical convenience
```

must be balanced against:

```text
operational reliability
```

---

# 187. A Simple Architecture Rule

> **Do not put a workload on a production operational system unless you are confident the workload cannot materially compromise the system's operational requirements.**

This is a risk-management principle.

It does not mean "never run analytics on OLTP."

It means measure and understand the consequences.

---

# 188. When Direct Analytics Can Still Be Fine

Examples:

- development environments
- small internal tools
- low-volume systems
- administrative reporting
- low-risk workloads
- controlled query schedules

Even production systems can sometimes use direct analytics when scale and risk are low.

Architecture should match the context.

---

# 189. The Difference Between "Can" and "Should"

A production database:

```text
can
```

run an analytical query.

That does not automatically mean it:

```text
should
```

run that query during peak business hours.

Architecture is about responsible workload placement.

---

# 190. OLTP vs OLAP and Data Engineering

A data engineer needs this distinction because pipelines often connect the two:

```text
OLTP
    ↓
Replication / CDC / extraction
    ↓
Analytical Platform
    ↓
OLAP
```

Data engineering creates the bridge between:

```text
operational truth
```

and:

```text
analytical use
```

---

# 191. Connection to Earlier Topics

## Topic 02 — Data Lifecycle

The movement may be:

```text
OLTP
→ ingestion
→ storage
→ transformation
→ OLAP
```

## Topic 03 — Batch / Streaming

CDC may be:

```text
near-real-time
```

or other ingestion modes can be:

```text
batch
micro-batch
streaming
```

## Topic 04 — ETL / ELT

Data can move:

```text
OLTP
→ ETL
→ analytical target
```

or:

```text
OLTP
→ ELT
→ analytical platform
```

This topic adds the reason why the destination workload may need different architecture.

---

# 192. Advanced Mental Model — Operational Truth vs Analytical Truth

The operational database represents current business state in a system optimized for transactions.

The analytical platform may contain:

```text
historical
transformed
aggregated
derived
```

representations.

They can be related without being identical.

For example:

```text
OLTP:
order status = PAID

OLAP:
daily revenue = 10,234,500
```

The analytical result is derived from many operational records.

---

# 193. Historical Data Changes the Workload

An application often asks:

```text
What is the state now?
```

An analytical system asks:

```text
What happened over time?
```

That difference drives:

```text
data volume
storage strategy
query shape
modeling
processing
```

---

# 194. Why OLAP Often Uses Historical Data

Business questions often involve:

```text
trends
comparisons
aggregations
segments
period-over-period analysis
```

These require history.

For example:

```text
revenue this month
vs
revenue last month
vs
revenue last year
```

The system needs multiple periods.

---

# 195. Why OLTP Often Focuses on Current State

An application might ask:

```text
What is the current inventory?
```

or:

```text
What is the current subscription status?
```

This is more current-state-oriented.

Historical data may exist, but the dominant operational access pattern is often current state.

---

# 196. The Same Data Can Support Both

A transaction:

```text
order_id = 1001
amount = 199.99
```

can support:

### OLTP

```text
Show order 1001.
```

### OLAP

```text
What was total revenue for September?
```

The underlying business data is related.

The workload differs.

---

# 197. Why Separate Storage Can Improve the System

Suppose:

```text
OLTP:
current operational state

OLAP:
historical analytical state
```

Separating them can provide:

```text
independent scaling
independent query optimization
workload isolation
different storage formats
different retention strategies
```

The cost is:

```text
more systems
more pipelines
more operational complexity
```

Again:

```text
Context
→ Options
→ Decision
→ Consequences
```

---

# 198. Production Trade-Off Summary

| Architecture | Simplicity | Workload Isolation | Analytical Scale | Freshness | Operational Complexity |
|---|---|---|---|---|---|
| Single DB | Higher | Lower | Lower/variable | Immediate | Lower |
| Read replica | Medium | Medium | Medium/variable | Near source, subject to lag | Medium |
| CDC + analytical platform | Lower | High | High | Can be near real-time | Higher |
| HTAP-style system | Medium/high | Varies | Varies | Potentially high | High |

These are broad tendencies.

Actual systems vary significantly.

---

# 199. Architecture Decision Questions

Ask:

```text
1. How important is operational latency?
2. How large are analytical scans?
3. How often do analytics run?
4. Can analytics wait?
5. How current must analytics be?
6. Can the workloads safely share resources?
7. How much complexity can the team support?
8. What does separate infrastructure cost?
9. What happens if the analytical workload spikes?
10. How will data move between systems?
```

---

# 200. Final Mental Model

Think:

```text
OLTP
→ operate the business

OLAP
→ analyze the business
```

Then:

```text
OLTP
→ many small operations
→ high concurrency
→ low latency
→ often normalized
→ often row-oriented

OLAP
→ large scans
→ aggregations
→ historical analysis
→ often denormalized
→ often column-oriented
```

Then:

```text
If workloads interfere:
→ isolate them
```

Possible mechanisms:

```text
read replica
CDC
separate analytical platform
HTAP
```

---

# 201. Official Roadmap Checkpoint

You must be able to satisfy the three required checkpoint tasks.

## Requirement 1 — Give **three differences** between OLTP and OLAP workloads

A valid answer can include:

### Difference 1 — Access pattern

```text
OLTP:
small selective reads/writes

OLAP:
large scans and aggregations
```

### Difference 2 — Primary objective

```text
OLTP:
run operational processes

OLAP:
answer analytical questions
```

### Difference 3 — Data/model/storage tendency

```text
OLTP:
often normalized and row-oriented

OLAP:
often denormalized/dimensional and column-oriented
```

These are workload tendencies rather than absolute rules.

---

# 202. Requirement 2 — Explain Why Columnar Storage Speeds Up Analytical Queries

A strong answer should say:

> Columnar storage organizes values by column, which can allow an analytical query to read only the columns it needs, reduce unnecessary data movement, benefit from compression, and support efficient column-oriented processing.

Do not say:

```text
columnar storage is always faster.
```

The benefit depends on the workload.

---

# 203. Requirement 3 — Explain Why Analysts Should Not Query the Production Database Directly

A strong answer should explain:

> Large analytical queries can compete with production transactions for CPU, memory, I/O, cache, connections, and other resources, potentially increasing customer-facing latency and operational risk.

Two safer alternatives include:

```text
1. Read replica
2. CDC → separate analytical platform
```

Other architectures may also be appropriate depending on requirements.

---

# 204. Additional Checkpoint Questions

Answer these without looking.

## Data modeling

1. Why is normalization useful in OLTP?
2. Why can denormalization help analytics?
3. What is a fact table?
4. What is a dimension table?

## Storage

5. What is row-oriented storage?
6. What is column-oriented storage?
7. What is projection?
8. Why can compression help analytical workloads?

## Architecture

9. What is a read replica?
10. What is replication lag?
11. What is CDC?
12. How is CDC different from a read replica?
13. What is HTAP?

## Workload metrics

14. What is QPS?
15. Why are rows scanned important?
16. What is latency?
17. What is concurrency?
18. Why is QPS alone insufficient?

## Architecture reasoning

19. Why can heavy analytics hurt OLTP?
20. When might one database still be enough?
21. When might workload isolation be justified?

---

# 205. Self-Explanation Test — Explain This to a New Teammate

Close the notes.

Explain:

1. What is OLTP?
2. What is OLAP?
3. Why are their workloads different?
4. Give three OLTP examples.
5. Give three OLAP examples.
6. Why can a large analytical query hurt a production OLTP system?
7. What is row-oriented storage?
8. What is column-oriented storage?
9. Why does columnar storage often help analytics?
10. What is normalization?
11. Why can denormalization help analytics?
12. What is a read replica?
13. What is CDC?
14. What is HTAP?
15. What do QPS and concurrency tell you?
16. Why does workload shape drive architecture?

Explain at least one example from banking or e-commerce.

A strong explanation should sound like:

```text
The production application needs many small,
fast, concurrent operations, so that is an OLTP workload.

The analytics team asks questions that scan and
aggregate large amounts of historical data, so that
is an OLAP workload.

Because the two workloads consume resources
differently, the company may isolate analytics
through a replica or a separate analytical platform.
```

Do not memorize that exact wording.

---

# 206. Interview Preparation — Beginner

## Question 1 — What is OLTP?

### Answer guidance

OLTP is online transaction processing. It supports operational business activity through many small, concurrent reads and writes, usually with strong correctness and low-latency requirements.

---

## Question 2 — What is OLAP?

### Answer guidance

OLAP is online analytical processing. It supports analytical queries that scan, join, aggregate, and compare larger amounts of data.

---

## Question 3 — What is the difference between OLTP and OLAP?

### Answer guidance

The most important distinction is workload shape:

```text
OLTP → small operational transactions
OLAP → analytical scans and aggregations
```

---

## Question 4 — Give examples.

### Answer guidance

OLTP:

```text
process payment
update inventory
create customer
```

OLAP:

```text
monthly revenue
customer segmentation
historical fraud analysis
```

---

# 207. Interview Preparation — Intermediate

## Question 5 — Why do OLTP systems often use normalized schemas?

### Answer guidance

Normalization can reduce duplication and update anomalies and can help maintain consistent operational state.

---

## Question 6 — Why do analytical systems often use denormalized models?

### Answer guidance

Denormalization can reduce joins and make common analytical access patterns simpler and more efficient.

---

## Question 7 — Why is columnar storage useful for analytics?

### Answer guidance

It groups values by column, which can reduce unrelated data reads for projection-heavy queries and can create strong compression and scan-efficiency opportunities.

---

## Question 8 — Why should heavy analytics not normally compete with production transactions?

### Answer guidance

Because both workloads consume shared resources, and heavy analytical scans can increase operational latency or reduce predictability.

---

# 208. Interview Preparation — Advanced

## Question 9 — What is a read replica?

### Answer guidance

A copy of an operational database that can serve selected read traffic, reducing pressure on the primary.

---

## Question 10 — What problem does CDC solve?

### Answer guidance

CDC captures changes in a source system so downstream systems can apply those changes without repeatedly performing full extracts.

---

## Question 11 — What is HTAP?

### Answer guidance

HTAP is an architecture intended to support transactional and analytical workloads in a tightly integrated system.

---

## Question 12 — Why might a read replica not be enough for analytics?

### Answer guidance

A replica still has finite compute, memory, I/O, and storage resources. Very large analytical queries can simply move the bottleneck from the primary to the replica.

---

## Question 13 — What metrics would you collect before choosing an architecture?

### Answer guidance

At minimum:

```text
QPS
rows scanned
latency
concurrency
read/write ratio
data volume
freshness
consistency
query complexity
```

---

# 209. Interview Preparation — Architecture

## Question 14 — When would you keep one database?

### Answer guidance

When workload volume and complexity are small enough, analytical use does not materially threaten operational requirements, and additional separation would not provide enough value to justify the complexity.

---

## Question 15 — When would you introduce a read replica?

### Answer guidance

When read traffic is contributing to primary pressure and a replicated read path can isolate appropriate reads without requiring a fully separate analytical platform.

---

## Question 16 — When would you use CDC?

### Answer guidance

When a separate downstream system needs reasonably current changes from an operational source, especially when repeated full extraction would be inefficient.

---

## Question 17 — When might HTAP make sense?

### Answer guidance

When the workload genuinely benefits from tightly integrated transactional and analytical access and the chosen platform can provide acceptable performance isolation and operational characteristics.

---

# 210. Benchmark Reflection

After running the SQLite experiment, write:

```text
My primary-key lookup result:
________________________________

My aggregation result:
________________________________

Index effect:
________________________________

Columnar byte comparison:
________________________________

Most important workload observation:
________________________________

One thing the benchmark cannot prove:
________________________________
```

The final line is important.

A strong engineer understands the limits of their evidence.

---

# 211. Benchmark Interpretation Exercise

Suppose your benchmark produces:

```text
PK lookup:
very fast

Aggregation:
much slower

Country index:
little change to aggregation
```

What should you conclude?

A good conclusion is:

```text
The point lookup is highly selective,
while the aggregation requires a larger scan.

The country index does not automatically
remove the need for broad analytical processing.

The workload shape, not the existence of an index,
determines the main cost.
```

---

# 212. Another Benchmark Interpretation

Suppose after adding the index:

```text
PK lookups:
no meaningful change
```

Why might that happen?

Because the primary key already had an index.

This demonstrates an important lesson:

> Adding another index on an unrelated column does not necessarily improve a workload that already uses a primary-key access path.

---

# 213. Another Benchmark Interpretation

Suppose:

```text
aggregation after index:
slightly faster
```

Do not conclude:

```text
indexes always improve analytics
```

Instead ask:

```text
Did the engine use the index?
Was the improvement due to the specific query shape?
How stable was the result across repeated runs?
```

Benchmark interpretation requires restraint.

---

# 214. Why Repeated Runs Matter

Suppose runs are:

```text
1.2 s
1.1 s
1.15 s
3.8 s
1.1 s
```

A single run of:

```text
3.8 s
```

might have been affected by:

- system activity
- cache state
- storage behavior
- background processes

This is why repeated measurements are useful.

---

# 215. Environment Recording

Before benchmarking, record:

```bash
python --version
```

and if available:

```bash
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```

Also note:

```text
OS
CPU
RAM
storage
```

This makes comparisons more meaningful.

---

# 216. Benchmark Safety

The benchmark creates:

```text
1,000,000 rows
```

Be careful with:

- disk space
- runtime
- temporary files

The exercise is explicitly large enough to demonstrate workload differences.

Do not silently reduce the benchmark to:

```text
10,000 rows
```

and call it equivalent.

If a learner's machine cannot comfortably complete it, the limitation should be documented rather than hidden.

---

# 217. Why the Benchmark Is Still Useful

Even though it is not production-grade, it can make visible:

```text
point lookup
vs
large scan
```

and:

```text
row layout
vs
column-oriented representation
```

These are foundational concepts.

The benchmark turns them from definitions into observations.

---

# 218. Advanced Mental Model — Architecture as Isolation

A useful way to think about architecture is:

```text
Which workloads deserve independent resources?
```

If:

```text
customer transactions
```

and:

```text
historical analytics
```

have different performance requirements, resource separation may be valuable.

This applies far beyond databases.

---

# 219. Advanced Mental Model — Scaling Dimensions

OLTP and OLAP can need to scale differently.

## OLTP

May scale around:

```text
QPS
connections
transactions/sec
low latency
```

## OLAP

May scale around:

```text
data scanned
parallel compute
memory
query throughput
historical data size
```

If one system must satisfy both, scaling can become awkward.

---

# 220. Advanced Mental Model — Data Movement Is a Cost

Separating systems solves contention, but it creates:

```text
data movement
```

Data movement can create:

- latency
- infrastructure cost
- replication complexity
- freshness delay
- schema-management work

Therefore:

```text
separate systems
```

is not free.

The architecture trade-off becomes:

```text
workload isolation
vs
data movement / complexity
```

---

# 221. Why CDC Can Be Valuable Despite Added Complexity

Suppose:

```text
OLTP
→ CDC
→ analytical system
```

The organization pays for:

```text
CDC infrastructure
```

but gains:

```text
workload isolation
+
independent analytical scaling
+
potentially fresher analytical data
```

The right question is:

> Is that value worth the added complexity?

---

# 222. Why HTAP Can Be Attractive

HTAP attempts to reduce some of that movement:

```text
shared / integrated data environment
```

Potentially:

```text
less replication
lower movement delay
```

But:

```text
mixed workloads
```

are difficult to optimize simultaneously.

Again:

```text
Context
→ Options
→ Decision
→ Consequences
```

---

# 223. Production Workload Review

When reviewing an architecture, ask:

```text
Who is the latency-sensitive consumer?
What queries are largest?
What is the peak QPS?
What is the peak concurrency?
What is the data growth rate?
What analytical freshness is required?
What is the cost of replication?
What happens if analytics spikes?
```

These questions reveal hidden architecture constraints.

---

# 224. Common Architecture Mistake

Avoid:

```text
We know PostgreSQL
→ use PostgreSQL for everything
```

Also avoid:

```text
We know warehouses
→ move every workload to a warehouse
```

Use:

```text
workload
→ requirements
→ architecture
→ technology
```

---

# 225. Another Common Mistake — Optimize Before Measuring

A weak approach is:

```text
query is slow
→ add index
```

A stronger approach is:

```text
measure
→ inspect workload
→ understand query shape
→ identify bottleneck
→ choose optimization
→ remeasure
```

This is production performance engineering.

---

# 226. Another Common Mistake — Benchmark the Wrong Thing

Do not measure:

```text
database startup
+
data generation
+
query
```

and call it:

```text
query performance
```

Separate:

```text
setup
```

from:

```text
measurement
```

This is why the benchmark keeps data generation outside query-timing functions.

---

# 227. Workload Review Template

Use this in future design discussions:

```text
SYSTEM:
____________________

PRIMARY WORKLOAD:
____________________

READ QPS:
____________________

WRITE QPS:
____________________

ROWS PER QUERY:
____________________

DATA VOLUME:
____________________

LATENCY TARGET:
____________________

CONCURRENCY:
____________________

FRESHNESS:
____________________

CONSISTENCY:
____________________

ANALYTICAL LOAD:
____________________

ARCHITECTURE:
____________________

WHY:
____________________
```

This is a practical engineering tool.

---

# 228. Final Decision Framework

When evaluating a database architecture:

```text
1. Identify workload.
2. Quantify workload.
3. Identify consumer requirements.
4. Identify interference risk.
5. List architecture options.
6. Estimate complexity.
7. Choose the simplest acceptable architecture.
8. Measure after implementation.
9. Revisit as workload changes.
```

This should become your default thinking pattern.

---

# 229. What You Should Carry Into Topic 06

The next topic deals with:

```text
warehouse
lake
lakehouse
```

Before entering it, you should already understand:

```text
Why analytical workloads
often need different architecture
from operational workloads.
```

The chain is:

```text
Business operations
      ↓
OLTP workload
      ↓
Operational system

Historical analysis
      ↓
OLAP workload
      ↓
Analytical system
```

Then:

```text
What should the analytical system look like?
```

That is the next architectural question.

---

# 230. Final Mental Model

Remember:

```text
OLTP
=
operate the business

OLAP
=
analyze the business
```

Then:

```text
OLTP
→ many small operations
→ high concurrency
→ low latency
→ current-state focus
→ often normalized
→ often row-oriented

OLAP
→ large scans
→ aggregations
→ historical analysis
→ analytical focus
→ often denormalized
→ often column-oriented
```

Then:

```text
If workloads interfere:
→ isolate them when justified.
```

Possible approaches include:

```text
read replica
CDC
separate analytical platform
HTAP
```

---

# 231. Official Final Checklist

## OLTP

- [ ] Definition
- [ ] Purpose
- [ ] Many small reads
- [ ] Many small writes
- [ ] Point lookups
- [ ] Transactions
- [ ] Consistency
- [ ] Concurrency
- [ ] Real-world examples
- [ ] Normalized models

## OLAP

- [ ] Definition
- [ ] Purpose
- [ ] Read-heavy workloads
- [ ] Large scans
- [ ] Aggregations
- [ ] Large joins
- [ ] Analytical examples
- [ ] Denormalized models
- [ ] Dimensional thinking

## Storage

- [ ] Row-oriented storage
- [ ] Column-oriented storage
- [ ] Why columnar helps analytics
- [ ] Projection
- [ ] Compression concept
- [ ] Vectorized processing concept
- [ ] Row vs column comparison

## Architecture

- [ ] Production DB contention
- [ ] Lock contention concept
- [ ] I/O contention
- [ ] CPU/memory competition
- [ ] Slow customer-facing queries
- [ ] Workload isolation
- [ ] Read replicas
- [ ] Replication lag
- [ ] CDC
- [ ] HTAP

## Workload Quantification

- [ ] QPS
- [ ] Rows scanned
- [ ] Latency
- [ ] Concurrency
- [ ] Read/write ratio
- [ ] Query complexity
- [ ] Workload profile

## Coding / Benchmark

- [ ] SQLite database
- [ ] 1,000,000 generated orders
- [ ] 10,000 primary-key lookups
- [ ] Large aggregation
- [ ] `time.perf_counter()`
- [ ] `country` index
- [ ] Rerun benchmark
- [ ] Compare measurements
- [ ] Toy columnar layout
- [ ] Amount-only read experiment
- [ ] Bytes-read comparison
- [ ] Resource-awareness guidance
- [ ] Cleanup guidance

## Engineering

- [ ] Workload-first architecture
- [ ] Trade-offs
- [ ] Failure modes
- [ ] Architecture progression
- [ ] ADR exercise
- [ ] Real-world case studies
- [ ] Common misconceptions
- [ ] Production vs toy distinction
- [ ] Interview preparation
- [ ] Self-explanation test
- [ ] Official checkpoint

---

# 232. Final Review

Before advancing, verify that you can answer:

1. What is OLTP?
2. What is OLAP?
3. What is the core difference in workload shape?
4. What is a point lookup?
5. What is a large scan?
6. Why do OLTP systems often use normalized schemas?
7. Why can OLAP systems benefit from denormalized models?
8. What is row-oriented storage?
9. What is column-oriented storage?
10. Why does columnar storage often help analytical queries?
11. What is projection?
12. Why can compression help columnar analytics?
13. Why can analytics interfere with production transactions?
14. What is resource contention?
15. What is a read replica?
16. What is replication lag?
17. What is CDC?
18. How is CDC different from a read replica?
19. What is HTAP?
20. What does QPS measure?
21. Why are rows scanned important?
22. What does latency measure?
23. What does concurrency mean?
24. Why is QPS alone insufficient?
25. Why doesn't an index solve every analytical problem?
26. When might one database still be sufficient?
27. When might workload isolation be justified?
28. Can you run the one-million-row benchmark?
29. Can you explain what the benchmark proves and does not prove?
30. Can you explain the architecture to another engineer?

If any answer is unclear, revisit the relevant section.

---

# 233. Final Engineering Principles

Keep these principles:

> **Workload shape matters more than database labels.**

> **Operational systems should protect business-critical transactions from unpredictable analytical resource consumption when the workload justifies isolation.**

> **Columnar storage is powerful because it aligns well with many analytical access patterns; it is not universally faster.**

> **Indexes are workload-specific tools, not universal performance solutions.**

> **Read replicas reduce some read pressure but do not automatically create an analytical platform.**

> **CDC is a change-propagation mechanism that can help isolate analytical workloads from operational systems.**

> **HTAP is an architectural option, not a universal replacement for separate systems.**

> **Measure workload characteristics before choosing architecture.**

---

# 234. Final Mental Model to Carry Forward

```text
Business requirement
        ↓
Workload
        ↓
Access pattern
        ↓
QPS / rows scanned / latency / concurrency
        ↓
Resource profile
        ↓
Architecture
        ↓
Storage + compute + replication strategy
```

And remember:

```text
OLTP
→ operate the business

OLAP
→ analyze the business
```

The architecture exists to serve those workload requirements.

That is the foundation for the next topic:

```text
Warehouse vs Lake vs Lakehouse
```

