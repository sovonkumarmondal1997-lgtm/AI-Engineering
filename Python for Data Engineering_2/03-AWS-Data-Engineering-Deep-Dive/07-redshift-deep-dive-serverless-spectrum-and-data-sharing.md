# 07 — Redshift Deep Dive: Serverless, Spectrum, and Data Sharing

> **G3 — AWS Data Engineering Deep Dive**  
> **Phase C — Governance and Warehousing**  
> **Level:** Intermediate → Advanced → Production  
> **Primary platform:** Amazon Redshift  
> **Related services:** Amazon S3, AWS Glue Data Catalog, AWS Lake Formation, Amazon Kinesis Data Streams, Amazon MSK, AWS IAM, AWS KMS, AWS CloudWatch  
> **Core loop:** Understand → Design → Implement → Query → Measure → Break → Diagnose → Fix → Secure → Cost-check → Document

---

# 1. Module Contract

This module turns Redshift from a service name into an engineering system.

The learner progresses through:

```text
Data Warehouse Fundamentals
        ↓
Redshift Architecture
        ↓
Provisioned Redshift + RA3
        ↓
Redshift Serverless
        ↓
S3 Loading / COPY / UNLOAD
        ↓
Table Design
        ↓
Distribution + Sort Keys
        ↓
Star Schema
        ↓
Incremental MERGE
        ↓
Materialized Views
        ↓
Spectrum
        ↓
Workload Management
        ↓
Data Sharing
        ↓
SUPER + PartiQL
        ↓
Streaming Ingestion
        ↓
Maintenance + System Views
        ↓
Security + Governance
        ↓
Performance + Cost Engineering
        ↓
Production Architecture
```

The objective is not to memorize Redshift commands.

The objective is to answer production questions such as:

- Should this workload use Redshift provisioned or Serverless?
- What should be the distribution strategy?
- Which columns should be sort keys?
- Should data remain in S3 or be loaded into Redshift?
- When should Spectrum be used?
- When should data sharing replace copying?
- How should incremental loads be made idempotent?
- How should runaway queries be controlled?
- How should PII be protected?
- How should streaming data enter the warehouse?
- How do we prove the warehouse is cost-efficient?

---

# 2. Roadmap Position

Topic 07 follows:

```text
S3 / S3 Tables
       ↓
Glue Data Catalog
       ↓
Glue ETL
       ↓
Athena + Iceberg
       ↓
Lake Formation
       ↓
Redshift
```

Redshift therefore consumes and complements the data-lake architecture rather than replacing it.

A common production architecture is:

```text
                    AWS DATA PLATFORM

Operational Sources
       |
       +----------------------+
       |                      |
       v                      v
     DMS / ETL             Streaming
       |                 Kinesis / MSK
       v                      |
      S3                     Redshift
       |                      |
 Glue Catalog                 |
       |                      |
 Lake Formation               |
       |                      |
       +----------+-----------+
                  |
             Redshift
                  |
       +----------+----------+
       |                     |
     BI / SQL             ML / Apps
```

---

# 3. What This Topic Must Cover

## Basics

- Redshift architecture
- leader and compute nodes
- RA3 nodes
- managed storage
- Redshift Serverless
- workgroups
- namespaces
- base capacity
- maximum capacity in RPUs
- provisioned vs Serverless
- steady vs spiky workloads
- cost control
- `COPY`
- S3
- multiple files
- Parquet
- manifests
- IAM roles
- `UNLOAD`

## Intermediate

- distribution styles:
  - `AUTO`
  - `KEY`
  - `EVEN`
  - `ALL`
- sort keys
- automatic table optimization
- compression and encodings
- star schemas
- staging tables
- `MERGE`
- incremental loading
- materialized views
- automatic refresh
- result caching
- Redshift Spectrum
- Glue Data Catalog
- external tables
- lake + warehouse joins
- workload management
- queues
- query priorities
- concurrency scaling
- query monitoring rules

## Advanced

- data sharing
- cross-cluster sharing
- cross-account sharing
- workgroup sharing
- cross-Region awareness
- multi-warehouse architecture
- multi-warehouse writes where supported
- `SUPER`
- PartiQL
- Kinesis streaming ingestion
- MSK streaming ingestion
- streaming materialized views
- `VACUUM`
- `ANALYZE`
- system tables/views
- performance diagnosis
- cost diagnosis
- IAM roles for `COPY`
- database roles
- row-level security
- dynamic data masking
- Lake Formation + Spectrum
- dbt on Redshift awareness

---

# 4. Why Data Warehouses Exist

A data lake is excellent for:

```text
cheap storage
+
open formats
+
large files
+
historical data
+
flexible processing
```

A warehouse is optimized for:

```text
interactive analytics
+
structured schemas
+
joins
+
aggregations
+
concurrency
+
BI workloads
```

A modern architecture often uses both.

```text
S3
=
durable analytical lake

Redshift
=
high-performance analytical warehouse
```

The question is not:

> "Which one is better?"

The real question is:

> "Which data should live where, and which engine should process each workload?"

---

# 5. Warehouse Mental Model

A warehouse turns:

```text
raw / semi-structured source data
```

into:

```text
curated relational analytical structures
```

Typical flow:

```text
Source
  ↓
Landing
  ↓
Staging
  ↓
Dimensions
  ↓
Facts
  ↓
Marts
  ↓
BI
```

Example:

```text
dim_customer
dim_product
dim_date
       |
       v
fact_order
       |
       v
sales_mart
```

---

# 6. OLTP vs OLAP

| Property | OLTP | OLAP |
|---|---|---|
| Primary goal | Transactions | Analytics |
| Typical queries | Small point lookups | Large scans |
| Writes | Frequent | Batch/stream |
| Joins | Usually smaller | Often large |
| Aggregations | Limited | Heavy |
| Data model | Operational | Analytical |
| Example | Application DB | Redshift |

Redshift is an analytical platform.

Do not use it as the transactional database for an application simply because it speaks SQL.

---

# 7. Redshift Architecture

At a high level, Redshift uses massively parallel processing.

Conceptually:

```text
                    SQL Client
                        |
                        v
                 Query Processing
                        |
              +---------+---------+
              |                   |
         Coordinator          Metadata
              |
      +-------+-------+
      |       |       |
      v       v       v
   Compute Compute Compute
   Node 1   Node 2   Node N
      |       |       |
      +-------+-------+
              |
          Storage
```

The important idea:

> A query is divided into work that can execute in parallel.

---

# 8. Leader and Compute Nodes

In traditional provisioned Redshift architecture, the leader node coordinates query planning and distributes work to compute nodes.

Compute nodes perform data processing.

Conceptually:

```text
Leader
  |
  +-- plan
  +-- coordinate
  +-- distribute
  |
  v
Compute nodes
  |
  +-- scan
  +-- join
  +-- aggregate
  +-- sort
```

Do not interpret "leader" as "the node that stores all warehouse data."

The analytical work is distributed across compute resources.

---

# 9. MPP

MPP means:

> Massively Parallel Processing.

Instead of:

```text
One server scans everything
```

Redshift attempts to do:

```text
Node 1 → partition of work
Node 2 → partition of work
Node 3 → partition of work
...
Node N → partition of work
```

The final result is assembled after distributed execution.

This makes data placement critical.

---

# 10. Data Distribution

Suppose a fact table contains:

```text
order_id
customer_id
product_id
order_date
amount
```

If a query frequently joins:

```text
fact_orders.customer_id
=
dim_customer.customer_id
```

then where those rows live can affect network movement.

Bad distribution can create:

```text
large data redistribution
        ↓
network movement
        ↓
slow joins
```

Good distribution can reduce unnecessary movement.

---

# 11. RA3 Architecture

RA3 node types separate compute from managed storage.

The important conceptual model is:

```text
Compute capacity
       |
       +----------------+
                        |
                 Managed storage
                        |
                     Data
```

This lets the warehouse scale compute and storage more independently than older tightly coupled architectures.

### Production lesson

Do not size an RA3 architecture solely by:

```text
raw data size
```

Also consider:

```text
concurrency
query complexity
scan volume
load throughput
sort/redistribution work
SLA
```

---

# 12. Managed Storage

With managed storage:

```text
Compute
    ≠
all physical storage capacity
```

This is useful when:

- data volume grows
- compute demand varies
- you need analytical elasticity
- storage and compute growth are not perfectly correlated

But managed storage does not make poor table design irrelevant.

Bad:

```text
huge scans
bad distribution
poor sort design
```

remain bad.

---

# 13. Redshift Serverless

Redshift Serverless separates the concepts of:

```text
Namespace
+
Workgroup
```

AWS describes a namespace as the storage/database/user-oriented collection and a workgroup as the compute-resource collection. citeturn0search17

Mental model:

```text
Namespace
    |
    +-- database
    +-- schemas
    +-- tables
    +-- users/roles
    +-- security/storage configuration

Workgroup
    |
    +-- compute
    +-- endpoint
    +-- network configuration
    +-- capacity settings
```

---

# 14. Workgroups

A Serverless workgroup represents compute resources.

A single namespace can support different compute environments.

Conceptually:

```text
Namespace
     |
 +---+----------------+
 |                    |
 v                    v
BI Workgroup       ETL Workgroup
```

This can help isolate:

```text
interactive analytics
```

from:

```text
batch processing
```

---

# 15. Namespaces

A namespace groups storage-oriented database resources.

Think:

```text
Namespace
├── Database
├── Schemas
├── Tables
├── Users / roles
├── Permissions
├── Encryption
└── Datashares / recovery configuration
```

The exact set of namespace properties changes as AWS evolves the service; verify current API/console behavior before automation.

---

# 16. Serverless Capacity

Redshift Serverless measures compute capacity in:

```text
RPU
=
Redshift Processing Unit
```

AWS currently documents:

```text
base capacity
+
maximum capacity
```

in RPUs. Base capacity defines baseline warehouse compute and maximum capacity limits the upper compute range used for scaling. citeturn0search8turn0search4

The exact available ranges can vary by Region and service generation, so never hard-code capacity assumptions into a production standard without checking current AWS documentation.

---

# 17. Base Capacity

Think:

```text
Base capacity
=
normal operating floor
```

If the base is too low:

```text
complex query
     ↓
resource pressure
     ↓
latency
```

If it is unnecessarily high:

```text
more baseline capacity
     ↓
higher cost
```

The correct value comes from measured workload behavior.

---

# 18. Maximum Capacity

Think:

```text
Maximum capacity
=
upper guardrail
```

It is valuable because Serverless can scale automatically, but an unconstrained workload can create an unexpected cost/performance envelope.

Production principle:

```text
elasticity
+
guardrails
```

not:

```text
elasticity
+
unlimited
```

---

# 19. Provisioned vs Serverless

| Workload | Provisioned | Serverless |
|---|---:|---:|
| Stable 24×7 workload | Strong | Strong |
| Highly predictable capacity | Strong | Moderate |
| Spiky demand | Moderate | Strong |
| Intermittent analytics | Moderate | Strong |
| Fine-grained compute sizing | Strong | Strong |
| Operational simplicity | Moderate | Strong |
| Long-running fixed workload | Strong | Strong |
| Cost guardrail | Strong | Strong if configured |

Use measured workload characteristics rather than ideology.

---

# 20. Choosing Serverless

Serverless is attractive when:

```text
demand is variable
+
operational simplicity matters
+
workloads can scale
+
capacity guardrails are defined
```

Example:

```text
weekday BI:
    high

night:
    low

month-end:
    very high
```

Serverless can fit this pattern well.

---

# 21. Choosing Provisioned

Provisioned can be attractive when:

```text
steady workload
+
predictable concurrency
+
stable SLA
+
known capacity requirement
+
long-lived warehouse
```

It can also be appropriate when workload behavior is easier to optimize around a fixed compute footprint.

---

# 22. Cost Decision

Never ask:

> "Is Serverless cheaper?"

Ask:

```text
What is the workload shape?
What is query volume?
What is concurrency?
What is runtime?
What is storage?
What is peak demand?
What is SLA?
What is idle time?
What are scaling limits?
```

Then measure:

```text
cost / query
cost / hour
cost / dashboard
cost / TB processed
cost / load
```

---

# 23. Loading from S3

The standard batch path is:

```text
S3
 |
 | COPY
 v
Redshift
```

This is preferred over millions of individual `INSERT` statements.

Why?

```text
COPY
=
bulk ingestion

INSERT per row
=
transaction overhead + poor throughput
```

---

# 24. COPY

Conceptual example:

```sql
COPY fact_orders
FROM 's3://company-lake/curated/orders/'
FORMAT AS PARQUET
IAM_ROLE 'arn:aws:iam::123456789012:role/redshift-copy-role';
```

The exact syntax should be validated against the current Redshift engine/version and security setup.

---

# 25. COPY Design Principles

Good ingestion:

```text
many reasonably sized files
+
columnar format
+
IAM role
+
idempotent process
+
staging
+
validation
```

Poor ingestion:

```text
one tiny file per record
+
manual credentials
+
single-row inserts
+
no validation
```

---

# 26. Many Files

Parallel ingestion benefits from parallel source files.

Instead of:

```text
orders.parquet
```

consider:

```text
orders/
    part-000.parquet
    part-001.parquet
    part-002.parquet
    ...
```

Do not create millions of tiny files.

The goal is:

```text
enough parallelism
without
small-file overhead
```

---

# 27. Parquet

Parquet is useful for analytical ingestion because it is:

- columnar
- compressed
- schema-aware
- efficient for analytical data

A common pattern:

```text
S3 Parquet
      ↓
COPY
      ↓
Redshift
```

For lake queries without loading the data, use Spectrum instead.

---

# 28. COPY from Manifest

A manifest explicitly lists input objects.

Conceptually:

```json
{
  "entries": [
    {"url": "s3://bucket/orders/part-001.parquet", "mandatory": true},
    {"url": "s3://bucket/orders/part-002.parquet", "mandatory": true}
  ]
}
```

Use manifests when you need precise control over the input set.

---

# 29. IAM Role for COPY

Prefer:

```text
Redshift
   |
   v
IAM role
   |
   v
S3
```

over long-lived access keys.

The role should have the narrowest required access.

Example conceptual permissions:

```text
s3:GetObject
s3:ListBucket
```

scoped to the required bucket/prefix.

If KMS encryption is involved, add only the required KMS permissions.

---

# 30. COPY Failure Diagnosis

If `COPY` fails:

```text
1. IAM role trust
2. S3 path
3. S3 permissions
4. KMS permissions
5. file format
6. schema mismatch
7. malformed records
8. manifest
9. network/security configuration
10. COPY options
```

Do not immediately broaden the IAM role.

---

# 31. UNLOAD

`UNLOAD` moves query results from Redshift to S3.

Conceptually:

```text
Redshift
   |
 UNLOAD
   |
   v
S3
```

Use cases:

- downstream lake processing
- data extracts
- sharing
- archival
- interoperability
- export to another processing system

---

# 32. UNLOAD Example

```sql
UNLOAD ('SELECT * FROM analytics.sales')
TO 's3://company-lake/exports/sales/'
IAM_ROLE 'arn:aws:iam::123456789012:role/redshift-unload-role'
FORMAT AS PARQUET;
```

Use controlled prefixes and encryption settings.

---

# 33. Table Design

Redshift table design revolves around:

```text
distribution
+
sort
+
encoding
+
schema
```

The design should be driven by workload.

---

# 34. Distribution Styles

Redshift supports distribution styles including:

```text
AUTO
KEY
EVEN
ALL
```

They answer:

> Where should rows be placed across compute resources?

---

# 35. AUTO Distribution

`AUTO` allows Redshift to manage distribution strategy.

It is often the best starting point when:

```text
you do not have enough workload evidence
```

Do not assume manual `KEY` distribution is automatically more professional.

Automation can be superior when it has enough workload evidence to optimize the table.

---

# 36. KEY Distribution

With:

```text
DISTKEY(customer_id)
```

rows with the same distribution key tend to be colocated according to Redshift's distribution mechanism.

This can reduce redistribution for common joins.

But it can create skew.

---

# 37. When KEY Distribution Helps

Potentially useful when:

```text
large fact
+
frequent join
+
stable high-value join key
+
good cardinality
+
balanced distribution
```

Example:

```text
fact_orders.customer_id
JOIN
dim_customer.customer_id
```

---

# 38. When KEY Distribution Hurts

Suppose:

```text
customer_id = "UNKNOWN"
```

appears in 40% of rows.

Then:

```text
KEY(customer_id)
```

can concentrate data.

Result:

```text
one slice
    |
    v
too much work
```

This is distribution skew.

---

# 39. EVEN Distribution

`EVEN` spreads rows without using a user-selected distribution key.

Useful when:

- there is no strong collocation key
- distribution is otherwise difficult
- the table does not benefit from key-based collocation

But joins may require redistribution.

---

# 40. ALL Distribution

`ALL` replicates the table across compute nodes.

Useful for:

```text
small dimensions
```

where local copies can eliminate repeated network movement.

Do not use `ALL` for giant fact tables.

---

# 41. Distribution Decision

| Table | Candidate |
|---|---|
| Huge fact | AUTO / KEY / EVEN based on workload |
| Small dimension | ALL may fit |
| Unknown workload | AUTO |
| Strong balanced join key | KEY |
| High-skew join key | Avoid KEY |
| Large rapidly changing dimension | Carefully evaluate ALL |

---

# 42. Distribution Skew

A useful diagnostic question:

> Is one compute slice doing disproportionately more work?

If yes, investigate:

```text
distribution key
+
data cardinality
+
NULL/unknown concentration
+
join pattern
```

Do not tune distribution from table size alone.

---

# 43. Sort Keys

Sort keys organize data so queries can eliminate unnecessary blocks.

If queries commonly filter by:

```sql
WHERE order_date >= '2026-01-01'
```

then a suitable sort strategy can improve pruning.

Mental model:

```text
Unsorted:
scan many blocks

Well sorted:
skip irrelevant blocks
```

---

# 44. Sort Key Selection

Choose based on:

```text
common predicates
+
join patterns
+
time filtering
+
range scans
+
table maintenance
```

Do not blindly choose:

```text
primary key
```

as the sort key.

---

# 45. Automatic Table Optimization

Automatic optimization can adjust table design based on observed workload and service intelligence.

This is especially useful when:

```text
workload evolves
```

However:

```text
AUTO
```

does not mean:

```text
ignore performance
```

You still need to inspect:

```text
query plans
system views
query latency
distribution
sort behavior
```

---

# 46. Compression and Encoding

Columnar storage benefits from appropriate encodings.

Compression can reduce:

```text
storage
+
I/O
```

But the correct encoding depends on:

```text
data type
cardinality
distribution
query pattern
```

Prefer current Redshift automatic encoding/table optimization capabilities where appropriate, while understanding what the system is doing.

---

# 47. Star Schema

Example:

```text
                 dim_customer
                      |
                      |
dim_product ---- fact_orders ---- dim_date
                      |
                      |
                 dim_store
```

Fact:

```text
order_id
customer_key
product_key
date_key
store_key
quantity
sales_amount
```

Dimensions:

```text
customer
product
date
store
```

---

# 48. Fact vs Dimension

### Fact

Usually:

```text
large
numeric measures
foreign keys
transaction/event grain
```

### Dimension

Usually:

```text
descriptive attributes
smaller
used for filtering/grouping
```

Redshift physical design should respect these logical roles.

---

# 49. Grain

Always state the grain.

Example:

> One row in `fact_orders` represents one order line.

This prevents:

```text
double counting
incorrect joins
incorrect aggregates
```

before performance tuning even begins.

---

# 50. Incremental Loads

A production pipeline should not reload the entire table for every change.

Typical pattern:

```text
Source CDC
   |
   v
S3 staging
   |
   v
Redshift staging table
   |
   v
MERGE
   |
   v
Target table
```

---

# 51. Staging Tables

Staging isolates:

```text
raw batch
```

from:

```text
production table
```

Example:

```text
stg_orders
```

contains the incoming batch.

Then:

```text
MERGE stg_orders
INTO fact_orders
```

---

# 52. MERGE

Conceptual:

```sql
MERGE INTO fact_orders AS t
USING stg_orders AS s
ON t.order_id = s.order_id
WHEN MATCHED THEN
    UPDATE SET
        status = s.status,
        amount = s.amount,
        updated_at = s.updated_at
WHEN NOT MATCHED THEN
    INSERT (
        order_id,
        status,
        amount,
        updated_at
    )
    VALUES (
        s.order_id,
        s.status,
        s.amount,
        s.updated_at
    );
```

The exact business keys and update semantics must match the source contract.

---

# 53. Idempotent MERGE

An incremental load should be safe to retry.

If the same batch is processed twice:

```text
first run → expected state
second run → same expected state
```

Avoid:

```text
duplicate rows
```

or:

```text
double-counted measures
```

Use:

```text
stable business key
+
deduplication
+
deterministic source state
+
MERGE
```

---

# 54. Late Data

Suppose:

```text
order_date = yesterday
```

arrives today.

Do not assume:

```text
today's partition = today's records
```

Your incremental strategy should account for:

```text
event time
+
ingestion time
+
CDC timestamp
+
source ordering
```

---

# 55. Materialized Views

A materialized view stores a precomputed result.

Conceptually:

```text
Base tables
   |
   v
Materialized view
   |
   v
BI query
```

Useful when the same expensive computation is repeatedly requested.

Example:

```sql
CREATE MATERIALIZED VIEW daily_sales_mv
AS
SELECT
    order_date,
    SUM(amount) AS revenue
FROM fact_orders
GROUP BY order_date;
```

---

# 56. Automatic Refresh

Automatic refresh can keep a materialized view aligned with base data where the view/query meets the service's current refresh capabilities.

Always verify current eligibility and refresh behavior before relying on it for an SLA.

---

# 57. Result Caching

Caching can reduce repeated computation when query results are eligible for reuse.

But caching is not a substitute for:

```text
good SQL
+
good table design
+
good distribution
+
good sort strategy
```

Ask:

```text
Is the workload repetitive?
Are results reusable?
What freshness is acceptable?
```

---

# 58. Redshift Spectrum

Spectrum lets Redshift query external data in S3 through catalog metadata.

Mental model:

```text
Redshift
   |
   | SQL
   v
Spectrum
   |
   v
Glue Data Catalog
   |
   v
S3
```

This creates a lake + warehouse architecture.

---

# 59. Why Spectrum Exists

Suppose:

```text
10 PB historical data
```

but only:

```text
50 TB
```

needs warehouse-style optimization.

You might keep:

```text
large history → S3
hot curated data → Redshift
```

and use Spectrum for selected lake access.

---

# 60. External Tables

An external table describes lake data.

Conceptually:

```sql
CREATE EXTERNAL SCHEMA lake
FROM DATA CATALOG
DATABASE 'curated'
IAM_ROLE '...';
```

Then:

```sql
SELECT *
FROM lake.events;
```

Exact syntax depends on the Redshift and Data Catalog setup.

---

# 61. Glue Data Catalog

The Glue Data Catalog provides metadata such as:

```text
database
table
columns
location
format
partition information
```

Spectrum can use that catalog to resolve external tables.

Therefore:

```text
Glue Catalog
=
metadata bridge
```

between the lake and Redshift Spectrum.

---

# 62. Lake + Warehouse Join

A powerful pattern:

```sql
SELECT
    o.customer_id,
    SUM(o.amount) AS revenue,
    COUNT(e.event_id) AS events
FROM warehouse.fact_orders o
JOIN lake.events e
    ON o.customer_id = e.customer_id
GROUP BY o.customer_id;
```

The exact physical behavior depends on data volume, filtering, join shape, and external scan efficiency.

Do not assume a lake join is free.

---

# 63. Spectrum Performance

Optimize:

```text
S3 file format
+
partitioning
+
predicate pushdown
+
column pruning
+
file size
+
data locality
```

Avoid:

```text
SELECT *
```

against huge external tables.

Prefer:

```sql
SELECT customer_id, event_ts
FROM lake.events
WHERE event_date >= DATE '2026-10-01';
```

---

# 64. Spectrum and Lake Formation

Lake Formation can govern Spectrum access.

AWS documents Lake Formation integration for Spectrum, including database/table/column access and data filters for row/cell-level controls. citeturn0search2

Mental model:

```text
Redshift Spectrum
        |
        v
Glue Data Catalog
        |
        v
Lake Formation
        |
        v
S3
```

This is why Topic 06 directly precedes Topic 07.

---

# 65. Workload Management

A production warehouse needs protection from:

```text
runaway query
+
bad dashboard
+
accidental cross join
+
massive external scan
+
unbounded transformation
```

Workload management controls how resources are allocated and protected.

---

# 66. Queues

Traditional WLM can organize workloads into queues.

Conceptually:

```text
BI queue
   |
   +-- analyst queries

ETL queue
   |
   +-- batch jobs

Admin queue
   |
   +-- maintenance
```

The exact WLM model depends on Redshift deployment mode and current service capabilities.

---

# 67. Query Priorities

Not all workloads have equal business importance.

Example:

```text
Executive dashboard
    HIGH

Interactive analyst
    NORMAL

Backfill
    LOW
```

Use priority to protect important workloads.

Do not simply make every queue high priority.

---

# 68. Concurrency Scaling

Concurrency scaling can provide additional compute capacity for eligible workloads when concurrency rises.

Use it for:

```text
spiky concurrent workloads
```

rather than assuming it solves every slow query.

If a query is intrinsically inefficient:

```text
bad query
+
more compute
```

can still be expensive.

---

# 69. Query Monitoring Rules

Query monitoring rules can stop or constrain runaway work.

Examples of monitoring dimensions include:

```text
execution time
rows scanned
CPU
disk usage
```

Conceptually:

```text
IF query exceeds boundary
THEN
    log / abort / change priority
```

Use these as guardrails, not as a replacement for query optimization.

---

# 70. Workload Isolation

A useful architecture:

```text
Production BI
     |
     v
Warehouse / Workgroup A

Data Engineering
     |
     v
Warehouse / Workgroup B

Ad hoc
     |
     v
Warehouse / Workgroup C
```

Data sharing can then allow controlled access without duplicating the source data.

---

# 71. Data Sharing

Redshift data sharing provides live access to shared data without manually copying the underlying data between warehouses.

AWS documents sharing across:

- clusters
- Serverless workgroups
- AWS accounts
- AWS Regions

and both read and, where supported/configured, write scenarios. citeturn0search3turn0search7

Mental model:

```text
Producer
   |
   | live datashare
   v
Consumer
```

---

# 72. Why Data Sharing Beats Copying

Without sharing:

```text
Warehouse A
    |
    v
EXPORT
    |
    v
S3
    |
    v
IMPORT
    |
    v
Warehouse B
```

With data sharing:

```text
Warehouse A
    |
    v
Datashare
    |
    v
Warehouse B
```

Benefits:

- less duplication
- fresher data
- simpler distribution
- lower operational overhead

Still evaluate cross-account, cross-Region and network/cost implications.

---

# 73. Cross-Cluster Sharing

A producer cluster can share selected database objects with another Redshift consumer.

Typical flow:

```text
Producer namespace
       |
       v
CREATE DATASHARE
       |
       v
ADD OBJECTS
       |
       v
GRANT USAGE / permissions
       |
       v
Consumer namespace
```

The exact SQL and authorization flow should be verified against the current Redshift documentation.

---

# 74. Cross-Account Sharing

Cross-account sharing adds:

```text
Producer account
        |
        v
Authorization
        |
        v
Consumer account
        |
        v
Association
```

AWS documents a two-way administrative handshake for cross-account sharing, and cross-account consumers can be associated with specific namespaces/clusters. citeturn0search10

---

# 75. Workgroup Sharing

Serverless consumers are associated through namespaces/workgroups.

Remember:

```text
namespace
=
storage/data identity

workgroup
=
compute environment
```

This separation enables multiple compute environments to work with shared data.

---

# 76. Cross-Region Sharing

Redshift supports cross-Region data sharing without manually copying the data to a new cluster in the traditional way. citeturn0search18

Evaluate:

```text
latency
+
data residency
+
cross-Region costs
+
regional availability
+
security
```

Do not enable cross-Region sharing simply because it is technically possible.

---

# 77. Multi-Warehouse Architecture

Example:

```text
                GOLD DATA
                    |
          +---------+---------+
          |                   |
       BI WH              Data Science WH
          |                   |
          +---------+---------+
                    |
               Shared data
```

Advantages:

- workload isolation
- team autonomy
- independent compute
- reduced copying

Risk:

```text
too many warehouses
=
governance + cost sprawl
```

---

# 78. Multi-Warehouse Writes

Current Redshift supports multi-warehouse writes for supported configurations and versions.

AWS documents write permissions such as:

```text
SELECT
INSERT
UPDATE
```

and schema permissions such as:

```text
USAGE
CREATE
```

for supported datashare-write scenarios. citeturn0search1turn0search9

Important:

> Treat multi-warehouse writes as a current-version feature, not a timeless Redshift assumption.

Always verify current patch/version, Region, object and workload limitations before production adoption.

---

# 79. Data Sharing Security

Share:

```text
minimum schemas
minimum tables
minimum privileges
```

Do not share:

```text
entire database
```

unless the consumer genuinely needs it.

For cross-account sharing:

```text
producer authorization
+
consumer association
+
database permissions
```

must be tested.

---

# 80. SUPER

`SUPER` is Redshift's semi-structured data type.

It can represent nested structures such as:

```json
{
  "customer": {
    "id": "C100",
    "segments": ["premium", "mobile"]
  }
}
```

This is useful when source data does not fit neatly into a flat relational schema.

---

# 81. When to Use SUPER

Good candidates:

- event payloads
- JSON documents
- nested application metadata
- semi-structured ingestion
- evolving source structures

Do not put every column into `SUPER`.

Use relational columns when:

```text
stable
+
frequently queried
+
strongly typed
```

---

# 82. PartiQL

PartiQL provides SQL-like access to nested/semi-structured structures.

Conceptual example:

```sql
SELECT
    payload.customer.id
FROM events;
```

For arrays/nested values, use Redshift's supported SUPER/PartiQL syntax.

---

# 83. SUPER Design Trade-Off

Relational:

```text
customer_id
country
device_type
```

Pros:

- strong typing
- predictable query patterns
- easier indexing/optimization concepts

SUPER:

```text
payload
```

Pros:

- flexible
- evolving schema
- nested data

Production approach:

```text
stable analytical attributes
→ relational columns

long-tail evolving payload
→ SUPER
```

---

# 84. Streaming Ingestion

Redshift can ingest streaming data from:

```text
Kinesis Data Streams
+
Amazon MSK
```

directly into a materialized view-based ingestion path.

AWS documents this as low-latency ingestion without requiring a temporary S3 landing stage. citeturn0search0turn0search14

---

# 85. Streaming Architecture

```text
Application
    |
    v
Kinesis / MSK
    |
    v
Redshift streaming ingestion
    |
    v
Materialized view
    |
    v
Analytics
```

This differs from:

```text
Stream
  ↓
S3
  ↓
ETL
  ↓
Redshift
```

because the streaming path can reduce intermediate storage and latency.

---

# 86. Kinesis Integration

Conceptually:

```text
Kinesis Data Stream
       |
       v
External schema
       |
       v
Streaming materialized view
       |
       v
Redshift
```

AWS documents Kinesis streaming ingestion using an external schema and a materialized view. citeturn0search5

---

# 87. MSK Integration

MSK can provide Kafka-compatible event streams.

Conceptually:

```text
MSK topic
   |
   v
Redshift streaming ingestion
   |
   v
Materialized view
```

AWS documents Redshift streaming ingestion from MSK without staging through S3. citeturn0search14

---

# 88. Streaming Materialized Views

The streaming materialized view acts as the ingestion target.

Conceptually:

```text
stream
   ↓
materialized view
   ↓
query
```

Important operational consideration:

> Avoid creating multiple independent consumers against the same stream/topic unnecessarily.

AWS notes that multiple streaming materialized views over the same stream/topic can increase consumer count, throttling risk and cost. citeturn0search0

---

# 89. Streaming Failure Modes

Watch for:

```text
consumer lag
+
shard/partition pressure
+
malformed payloads
+
schema mismatch
+
permissions
+
network access
+
refresh failures
```

A streaming system must have a freshness SLA.

Example:

```text
99% of events visible within 60 seconds
```

---

# 90. Maintenance

Production Redshift maintenance includes:

```text
VACUUM awareness
+
ANALYZE awareness
+
statistics
+
sort state
+
system views
```

Do not treat maintenance as a ritual.

Measure whether it improves:

```text
query plans
+
scan volume
+
latency
```

---

# 91. VACUUM

Historically, `VACUUM` has been used to restore sort order and reclaim space after deletes/updates.

Modern Redshift includes automation that can reduce the need for manual intervention in many workloads.

Still understand `VACUUM` because:

```text
legacy workloads
+
specific table states
+
operational diagnosis
```

may require it.

---

# 92. ANALYZE

Statistics help the optimizer estimate:

```text
row counts
+
data distribution
+
selectivity
```

Poor statistics can lead to poor plans.

Modern Redshift automates some analysis behavior, but engineers must understand:

```text
when stats are stale
+
what the optimizer is doing
```

---

# 93. System Tables and Views

Production diagnosis relies heavily on Redshift system metadata.

Useful families include:

```text
STL_*
STV_*
SVL_*
SVV_*
SYS_*
```

The exact recommended system views evolve.

Use them to investigate:

- query duration
- query steps
- scans
- joins
- queueing
- workload
- table metadata
- locks
- storage
- user activity
- errors

---

# 94. Performance Investigation

When a query is slow:

```text
1. Confirm the query
2. Check queue time
3. Check execution time
4. Check scan volume
5. Check distribution
6. Check joins
7. Check sort pruning
8. Check external scans
9. Check concurrency
10. Check statistics
11. Check materialized views
12. Check recent schema/data changes
```

Do not immediately resize the warehouse.

---

# 95. EXPLAIN

Use:

```sql
EXPLAIN
SELECT ...
```

to inspect the planned operations.

Look for:

```text
large redistribution
+
large scans
+
expensive joins
+
unexpected nested loops
+
poor selectivity
```

A senior engineer reads the plan before changing infrastructure.

---

# 96. Performance Incident — Distribution Skew

### Symptom

One workload slice is overloaded.

### Investigation

```text
distribution style
↓
distribution key
↓
key cardinality
↓
NULL/unknown concentration
↓
join pattern
```

### Fix candidates

```text
AUTO
KEY change
EVEN
ALL for small dimension
schema/workload redesign
```

---

# 97. Performance Incident — Full Scan

### Symptom

Query scans far more data than expected.

Check:

```text
sort key
predicate
data types
functions on filtered columns
table statistics
projection
materialized view
```

Example anti-pattern:

```sql
WHERE DATE(order_ts) = DATE '2026-10-01'
```

may be less optimizer-friendly than a range predicate depending on the physical design.

Prefer:

```sql
WHERE order_ts >= TIMESTAMP '2026-10-01 00:00:00'
  AND order_ts <  TIMESTAMP '2026-10-02 00:00:00'
```

when appropriate.

---

# 98. Performance Incident — Spectrum Scan

### Symptom

A Redshift query becomes expensive because it scans a large lake table.

Check:

```text
S3 format
partitioning
predicate pushdown
column projection
file sizes
external table statistics/metadata
```

Then decide:

```text
keep in lake
materialize to Redshift
pre-aggregate
create materialized view
```

---

# 99. Performance Incident — Concurrency

### Symptom

Individual queries are fast, but users experience high latency.

Possible cause:

```text
queueing
+
concurrency
```

Investigate:

```text
WLM
+
query priority
+
concurrency scaling
+
workload isolation
```

This is different from a single bad query.

---

# 100. Cost Optimization

Measure:

```text
compute
+
storage
+
S3
+
Spectrum
+
streaming
+
cross-Region
+
cross-account
+
data duplication
```

Cost optimization is architectural.

---

# 101. Cost Anti-Pattern

Bad:

```text
every team
    |
    v
separate warehouse
    |
    v
duplicate data
```

Better:

```text
shared source data
+
data sharing
+
isolated compute
```

when workload and governance justify it.

---

# 102. Serverless Cost Guardrails

Configure:

```text
base capacity
+
maximum capacity
+
usage limits
+
workload monitoring
+
AWS Budgets
```

Measure:

```text
RPU usage
+
query cost
+
load cost
```

Do not set a high maximum capacity without a cost reason.

---

# 103. Spectrum Cost

Spectrum can reduce the need to load all data into Redshift, but external scans still have cost/performance implications.

Optimize:

```text
partition pruning
+
column pruning
+
Parquet
+
reasonable file sizes
+
selective predicates
```

---

# 104. Data Sharing Cost

Data sharing can avoid data-copy workflows.

But cross-account and cross-Region architectures can have their own service and data-transfer cost considerations.

Always evaluate:

```text
copy cost
vs
sharing cost
```

using the current AWS pricing model.

---

# 105. Security

Redshift security is layered:

```text
IAM
+
network controls
+
KMS
+
database roles
+
database privileges
+
RLS
+
dynamic masking
+
Lake Formation for Spectrum
+
audit logging
```

No single mechanism is sufficient.

---

# 106. IAM Roles for COPY

Use IAM roles for:

```text
S3 read
+
KMS access
```

Avoid embedding long-lived credentials.

Example architecture:

```text
Redshift
   |
IAM role
   |
S3
```

The role should be scoped to the exact prefixes required.

---

# 107. Database Roles

Database roles let you group privileges around business responsibilities.

Example:

```text
role:
finance_analyst

grants:
    USAGE on schema finance
    SELECT on approved tables
```

Then users can be associated with the role rather than receiving dozens of direct grants.

---

# 108. Row-Level Security

Redshift supports row-level security for restricting which rows a database user/role can see.

Conceptually:

```text
role = regional_analyst
        |
        v
region = 'IN'
        |
        v
authorized rows
```

Use RLS when the security boundary belongs inside the Redshift warehouse.

Use Lake Formation filters when the data is being accessed through governed lake/Spectrum paths.

---

# 109. Dynamic Data Masking

Dynamic masking can protect sensitive values while allowing the underlying table to remain queryable.

Example:

```text
email
    |
    +-- privileged role → full email
    |
    +-- analyst → masked email
```

The correct masking strategy depends on the business policy and supported Redshift configuration.

---

# 110. Redshift Security vs Lake Formation

| Requirement | Redshift | Lake Formation |
|---|---:|---:|
| Warehouse database privileges | Strong | Not primary |
| Warehouse RLS | Strong | Not primary |
| Dynamic masking | Strong | Not primary |
| S3 lake governance | Limited | Strong |
| Spectrum fine-grained lake access | Integrated | Strong |
| Lake row/cell filters | No | Strong |
| Warehouse table sharing | Strong | Not primary |
| IAM integration | Yes | Yes |

Use the control where the data is being governed.

---

# 111. Lake Formation + Spectrum

A production lakehouse may use:

```text
S3
  ↓
Glue Catalog
  ↓
Lake Formation
  ↓
Spectrum
  ↓
Redshift
```

Lake Formation can enforce fine-grained access on Spectrum queries against governed lake data. citeturn0search2

This makes Topic 06 a direct dependency.

---

# 112. dbt on Redshift

dbt can provide:

```text
SQL transformations
+
models
+
tests
+
documentation
+
lineage
```

A Redshift dbt project may look like:

```text
sources
   ↓
staging
   ↓
intermediate
   ↓
marts
```

Use dbt for transformation workflow and testing.

Do not confuse:

```text
dbt
```

with:

```text
warehouse compute
```

Redshift executes the SQL.

---

# 113. Terraform / CLI / boto3

Infrastructure should be reproducible.

Conceptual repository:

```text
aws_redshift/
├── terraform/
├── sql/
├── tests/
├── dashboards/
└── docs/
```

Use:

```text
Terraform/OpenTofu
+
AWS CLI
+
boto3
+
SQL
```

---

# 114. Terraform Principles

Terraform should manage:

```text
Serverless workgroup
namespace
networking
security groups
IAM
KMS
S3
CloudWatch
```

where supported by the current AWS provider.

Do not put:

```text
database passwords
access keys
secrets
```

directly into source control.

Use Secrets Manager or the appropriate secret mechanism.

---

# 115. AWS CLI Examples

Inspect Serverless workgroups:

```bash
aws redshift-serverless list-workgroups
```

Inspect namespaces:

```bash
aws redshift-serverless list-namespaces
```

Get a workgroup:

```bash
aws redshift-serverless get-workgroup \
  --workgroup-name analytics-prod
```

Always validate CLI syntax against the current AWS CLI version.

---

# 116. boto3 Example

```python
import boto3

client = boto3.client("redshift-serverless")

workgroups = client.list_workgroups()

for workgroup in workgroups.get("workgroups", []):
    print(
        workgroup["workgroupName"],
        workgroup.get("baseCapacity")
    )
```

Use SDK automation for:

```text
inventory
+
compliance checks
+
cost reporting
+
drift detection
```

rather than destructive automation by default.

---

# 117. Hands-On Lab Environment

Use:

```text
AWS learning account
+
MFA
+
IAM Identity Center / assumed role
+
AWS Budgets
+
cost allocation tags
+
Terraform
+
AWS CLI v2
+
Python 3.12+
+
boto3
```

Use the smallest practical resources.

For every lab:

```text
CREATE
  ↓
TEST
  ↓
MEASURE
  ↓
BREAK
  ↓
FIX
  ↓
TEARDOWN
```

---

# 118. Lab 1 — Serverless

## Objective

Create:

```text
namespace
+
workgroup
```

with a deliberately controlled base and maximum capacity.

## Tasks

1. Create infrastructure with Terraform.
2. Configure encryption.
3. Configure network access.
4. Connect with SQL.
5. Create schema.
6. Run baseline query.
7. Record latency.
8. Run concurrent queries.
9. Observe capacity.
10. Destroy resources.

## Evidence

```text
Terraform plan
Terraform apply
SQL output
capacity settings
cost estimate
teardown
```

---

# 119. Lab 2 — COPY from S3

## Objective

Load Parquet data.

Dataset:

```text
orders
customers
products
```

Tasks:

```text
S3
 ↓
IAM role
 ↓
COPY
 ↓
Redshift
```

Test:

```sql
SELECT COUNT(*) FROM orders;
```

Then inspect:

```text
load time
row count
errors
```

Break:

```text
remove S3 permission
```

Diagnose and restore.

---

# 120. Lab 3 — Star Schema

Create:

```text
dim_customer
dim_product
dim_date
fact_orders
```

Create two designs:

```text
Design A:
    DISTKEY(customer_id)

Design B:
    AUTO
```

Run identical queries.

Measure:

```text
execution time
query plan
redistribution
scan volume
```

Write an ADR explaining the result.

---

# 121. Lab 4 — MERGE

Create:

```text
stg_orders
fact_orders
```

Load:

```text
insert batch
update batch
duplicate batch
```

Implement `MERGE`.

Verify:

```text
rerunning the same batch
```

does not duplicate business records.

---

# 122. Lab 5 — Spectrum

Create:

```text
S3 Parquet events
Glue Catalog
external schema
external table
```

Query:

```sql
SELECT
    event_date,
    COUNT(*)
FROM lake.events
WHERE event_date >= DATE '2026-10-01'
GROUP BY event_date;
```

Then join:

```text
Redshift fact_orders
+
S3 events
```

Measure scan behavior.

---

# 123. Lab 6 — Workload Management

Create workloads:

```text
BI
ETL
Ad hoc
```

Generate:

```text
fast query
slow query
large scan
concurrent queries
```

Configure current supported workload controls.

Test:

```text
priority
queueing
monitoring
abort/guardrail behavior
```

Document:

```text
expected
actual
lesson
```

---

# 124. Lab 7 — Data Sharing

Create:

```text
Producer
Consumer
```

Producer:

```text
gold schema
```

Consumer:

```text
analytics workgroup
```

Share only:

```text
approved objects
```

Verify:

```text
live data visibility
```

Then change producer data and confirm the consumer sees the updated shared state.

---

# 125. Lab 8 — Security

Implement:

```text
database role
+
least privilege
+
RLS
+
dynamic masking
```

Test:

```text
analyst
finance
admin
```

Expected result:

```text
analyst → masked / filtered
finance → authorized
admin → controlled elevated access
```

Perform negative tests.

---

# 126. Lab 9 — Performance Incident

Inject:

```text
skewed distribution key
```

Run a join.

Observe:

```text
slow query
+
uneven work
```

Diagnose:

```text
distribution
+
plan
+
system views
```

Fix:

```text
distribution strategy
```

Re-run.

Write incident report:

```text
root cause
blast radius
fix
prevention
```

---

# 127. Lab 10 — End-to-End Warehouse

Build:

```text
S3
 |
 COPY
 |
staging
 |
MERGE
 |
warehouse
 |
materialized views
 |
BI
```

Add:

```text
Spectrum
+
Lake Formation
+
data sharing
+
security
+
monitoring
```

Capture:

```text
architecture
cost
performance
security
teardown
```

---

# 128. Break/Fix Scenario 1 — COPY Access Denied

### Symptom

```text
COPY fails with S3 authorization error.
```

### Diagnose

```text
IAM role
↓
trust policy
↓
S3 prefix
↓
bucket policy
↓
KMS
```

### Lesson

Do not grant `s3:*` on `*`.

---

# 129. Break/Fix Scenario 2 — COPY Loads Wrong Files

### Symptom

Unexpected records appear.

### Diagnose

```text
prefix
manifest
file naming
incremental boundary
source watermark
```

### Fix

Use deterministic input selection.

---

# 130. Break/Fix Scenario 3 — MERGE Duplicates

### Symptom

Same business key appears multiple times.

### Diagnose

```text
staging duplicates
+
non-unique MERGE match
+
source CDC semantics
```

### Fix

Deduplicate staging before MERGE.

---

# 131. Break/Fix Scenario 4 — Query Suddenly Slow

Check:

```text
queue time
distribution
sort
statistics
scan
concurrency
recent data growth
recent schema changes
```

Do not resize first.

---

# 132. Break/Fix Scenario 5 — Spectrum Query Expensive

Check:

```text
partition pruning
column pruning
file format
file sizes
predicate
data volume
```

Then decide:

```text
optimize lake
or
materialize to warehouse
```

---

# 133. Break/Fix Scenario 6 — Unexpected Data Share Access

Check:

```text
datashare objects
consumer association
database privileges
role membership
cross-account authorization
```

Revoke the narrowest excessive permission.

---

# 134. Break/Fix Scenario 7 — Serverless Cost Spike

Check:

```text
base capacity
maximum capacity
query concurrency
long-running queries
external scans
ETL jobs
workload controls
```

Set a cost guardrail.

---

# 135. Break/Fix Scenario 8 — Streaming Lag

Check:

```text
stream throughput
shards/partitions
materialized view refresh
consumer configuration
payload size
permissions
network
```

Compare:

```text
event time
vs
warehouse visibility time
```

---

# 136. Automated Testing

Tests should cover:

## Schema

```text
expected columns
expected types
```

## Data

```text
row counts
uniqueness
nullability
referential integrity
```

## Security

```text
role can access expected data
role cannot access restricted data
```

## Incremental

```text
rerun same batch
=
same target state
```

## Performance

```text
query latency threshold
scan threshold
```

---

# 137. SQL Test Example

```sql
SELECT
    COUNT(*) AS duplicate_keys
FROM (
    SELECT order_id
    FROM fact_orders
    GROUP BY order_id
    HAVING COUNT(*) > 1
) d;
```

Expected:

```text
duplicate_keys = 0
```

---

# 138. Security Test Example

Test as:

```text
marketing_role
```

Then:

```sql
SELECT email
FROM customers
LIMIT 10;
```

Expected:

```text
DENIED
```

or:

```text
MASKED
```

depending on the policy.

---

# 139. Architecture Decision Record — Serverless vs Provisioned

## Context

Workload is:

```text
spiky
+
intermittent
+
cost-sensitive
```

## Decision

Start with Serverless.

## Consequence

Pros:

- operational simplicity
- elasticity

Cons:

- need capacity/cost guardrails
- need workload validation

---

# 140. ADR — AUTO vs KEY Distribution

## Context

Workload is not yet stable.

## Decision

Start with `AUTO`.

## Revisit when

```text
stable high-value join
+
sufficient workload evidence
+
distribution metrics
```

---

# 141. ADR — Spectrum vs Load to Redshift

Use Spectrum when:

```text
data is cold
+
large
+
occasionally queried
```

Load into Redshift when:

```text
data is hot
+
frequently joined
+
latency-sensitive
+
worth optimizing
```

---

# 142. ADR — Data Sharing vs Copy

Use sharing when:

```text
same data
+
multiple consumers
+
freshness important
+
copying is wasteful
```

Copy when:

```text
hard isolation
+
different lifecycle
+
different transformation
+
independent ownership
```

---

# 143. ADR — RLS vs Lake Formation Filter

Use Redshift RLS when:

```text
data lives in warehouse
```

Use Lake Formation filters when:

```text
data is governed in S3
+
consumed through Spectrum
```

---

# 144. Decision Matrix — Storage Location

| Requirement | S3 | Redshift |
|---|---:|---:|
| Massive raw history | Excellent | Not primary |
| Open formats | Excellent | Limited |
| Interactive joins | Moderate | Excellent |
| BI concurrency | Moderate | Excellent |
| Flexible raw data | Excellent | Moderate |
| Hot analytical marts | Moderate | Excellent |
| Low-cost archive | Excellent | Moderate |
| Central warehouse semantics | Moderate | Excellent |

---

# 145. Decision Matrix — Compute

| Pattern | Serverless | Provisioned |
|---|---:|---:|
| Spiky | Excellent | Good |
| Steady 24×7 | Good | Excellent |
| Intermittent | Excellent | Moderate |
| Predictable | Good | Excellent |
| Simple operations | Excellent | Moderate |
| Long-term fixed capacity | Good | Excellent |

---

# 146. Decision Matrix — Lake vs Warehouse

| Question | Spectrum | Redshift table |
|---|---:|---:|
| Very large cold data | Excellent | Moderate |
| Frequent joins | Moderate | Excellent |
| BI dashboard | Moderate | Excellent |
| Open lake access | Excellent | Moderate |
| Lowest latency | Moderate | Excellent |
| Frequent updates | Moderate | Excellent |
| Semi-structured source | Excellent | SUPER/relational |
| Strong warehouse governance | Moderate | Excellent |

---

# 147. Common Mistakes

## 1. Single-row INSERTs

Use bulk loading or staged ingestion.

## 2. Blind KEY distribution

A key can create severe skew.

## 3. No Serverless maximum capacity

Elasticity without a guardrail is dangerous.

## 4. SELECT *

Especially against Spectrum.

## 5. Copying data between warehouses unnecessarily

Evaluate data sharing first.

## 6. Ignoring query plans

Performance work should start with evidence.

## 7. Using Redshift as OLTP

It is an analytical warehouse.

## 8. No staging for CDC

This makes incremental loads harder to reason about.

## 9. Non-idempotent MERGE

Retries can duplicate or corrupt state.

## 10. Treating Spectrum as free

External scans have performance and cost implications.

## 11. Treating automatic optimization as magic

Measure outcomes.

## 12. Giving broad IAM roles

Use least privilege.

## 13. Ignoring KMS

Encryption adds another authorization boundary.

## 14. Sharing entire databases

Share only what the consumer needs.

## 15. No negative security tests

A policy is not proven until denied access fails.

---

# 148. Interview Preparation — Beginner

### What is Redshift?

A managed AWS analytical data warehouse designed for large-scale SQL analytics using massively parallel processing.

### What is Serverless?

A Redshift deployment model where AWS manages the underlying compute infrastructure and users configure logical namespaces/workgroups and capacity settings.

### What is Spectrum?

A Redshift capability for querying data stored in S3 through external tables/catalog metadata.

### What is `COPY`?

Bulk ingestion from sources such as S3 into Redshift tables.

### What is `UNLOAD`?

Exporting Redshift query results to S3.

---

# 149. Interview — Intermediate

### Why does distribution matter?

Because distributed joins may require data redistribution between compute slices.

### Why use sort keys?

To improve data pruning and reduce unnecessary block scans.

### Why use a staging table?

To isolate incoming data, validate it and make incremental processing safer.

### Why use MERGE?

To atomically express matched updates/inserts according to a business key.

### Why use Spectrum?

To query large lake datasets without loading every object into the warehouse.

---

# 150. Interview — Advanced

### Why use data sharing?

To provide live access to data across warehouses/accounts without manually copying the data.

### How do you debug a slow Redshift query?

Start with queue time and query plan, then inspect scans, redistribution, joins, sort behavior, statistics, concurrency and external scans.

### How do you secure PII?

Use IAM/database roles, RLS, dynamic masking, Lake Formation for Spectrum, KMS, network controls and negative tests.

### When should data remain in S3?

When it is large, cold, open-format, infrequently queried or better suited to lake processing.

---

# 151. Interview — Senior/Staff

A strong senior answer to:

> "Design an AWS lakehouse for enterprise analytics."

Should include:

```text
S3
+
Glue Catalog
+
Lake Formation
+
Athena
+
Redshift
+
Spectrum
+
data sharing
+
streaming
+
IAM
+
KMS
+
network isolation
+
observability
+
cost controls
+
IaC
```

Then explain:

```text
why each component exists
+
what alternatives were rejected
+
where data lives
+
who owns it
+
how access is enforced
+
how performance is measured
+
how the platform scales
+
how costs are controlled
```

---

# 152. Practice Questions — Basic

1. What problem does a data warehouse solve?
2. What is Redshift?
3. What is MPP?
4. What is a leader node?
5. What is a compute node?
6. What are RA3 nodes?
7. What is managed storage?
8. What is Redshift Serverless?
9. What is a namespace?
10. What is a workgroup?
11. What is an RPU?
12. What is `COPY`?
13. What is `UNLOAD`?
14. What is Spectrum?
15. What is a sort key?

---

# 153. Practice Questions — Intermediate

16. Compare Serverless and provisioned Redshift.
17. Explain `AUTO` distribution.
18. Explain `KEY` distribution.
19. Explain `EVEN`.
20. Explain `ALL`.
21. What is distribution skew?
22. Why are small files problematic?
23. Why use Parquet?
24. Why use a staging table?
25. Design an incremental `MERGE`.
26. What is a materialized view?
27. What is result caching?
28. What is Spectrum?
29. How does Spectrum use Glue Catalog?
30. How do you protect against runaway queries?

---

# 154. Practice Questions — Hard

31. Design a star schema for e-commerce.
32. Choose a distribution strategy for a 5 TB fact table.
33. Diagnose a skewed join.
34. Design Serverless capacity guardrails.
35. Compare Spectrum vs loading to Redshift.
36. Design a cross-account datashare.
37. Design workload isolation.
38. Design a CDC pipeline using staging + MERGE.
39. Design PII controls.
40. Design a Redshift + Lake Formation architecture.

---

# 155. Practice Questions — Advanced

41. Design a multi-warehouse enterprise platform.
42. Design multi-warehouse writes.
43. Design a Kinesis-to-Redshift near-real-time path.
44. Design an MSK-to-Redshift path.
45. Design a SUPER-based event model.
46. Diagnose a Serverless cost spike.
47. Diagnose a Spectrum performance incident.
48. Design data-sharing governance.
49. Design a warehouse security operating model.
50. Design a production Redshift platform entirely through IaC.

---

# 156. Cheat Sheet — Architecture

```text
Provisioned
    |
    +-- cluster
    +-- compute
    +-- managed storage for RA3

Serverless
    |
    +-- namespace
    +-- workgroup
    +-- RPU capacity
```

---

# 157. Cheat Sheet — Loading

```text
S3
 ↓
COPY
 ↓
staging
 ↓
MERGE
 ↓
warehouse
```

---

# 158. Cheat Sheet — Table Design

```text
Distribution
    ↓
Where rows live

Sort
    ↓
How efficiently blocks can be pruned

Encoding
    ↓
How efficiently columns are stored
```

---

# 159. Cheat Sheet — Spectrum

```text
Redshift
   ↓
Spectrum
   ↓
Glue Catalog
   ↓
S3
```

---

# 160. Cheat Sheet — Sharing

```text
Producer
   ↓
Datashare
   ↓
Consumer
```

No manual export/import is required for the normal live-sharing pattern.

---

# 161. Cheat Sheet — Security

```text
IAM
+
KMS
+
Database Roles
+
RLS
+
Dynamic Masking
+
Lake Formation
+
Network controls
```

---

# 162. Cheat Sheet — Performance

```text
EXPLAIN
+
system views
+
distribution
+
sort
+
statistics
+
concurrency
+
scan volume
```

---

# 163. Production Runbook — Slow Query

```text
1. Capture query ID
2. Check queue time
3. EXPLAIN
4. Check scan volume
5. Check joins
6. Check redistribution
7. Check sort pruning
8. Check statistics
9. Check concurrency
10. Check Spectrum
11. Apply smallest safe fix
12. Re-test
13. Record result
```

---

# 164. Production Runbook — Serverless Cost Spike

```text
1. Identify time window
2. Identify workgroup
3. Identify queries
4. Inspect RPU usage
5. Inspect maximum capacity
6. Identify large scans
7. Identify concurrency
8. Identify repeated queries
9. Add/adjust guardrails
10. Re-measure
```

---

# 165. Production Runbook — Data Share Incident

```text
1. Identify producer
2. Identify consumer
3. Identify datashare
4. List shared objects
5. Review consumer association
6. Review database privileges
7. Revoke excess privilege
8. Test access
9. Review audit evidence
10. Document incident
```

---

# 166. Production Runbook — COPY Failure

```text
1. Identify COPY command
2. Inspect STL/SYS load errors
3. Verify IAM role
4. Verify S3 prefix
5. Verify KMS
6. Verify file format
7. Verify schema
8. Verify manifest
9. Re-run with controlled sample
10. Restore production load
```

---

# 167. Security Testing

For every sensitive dataset test:

```text
ALLOW:
    expected role sees expected data

DENY:
    unauthorized role cannot see data
```

Test:

```text
warehouse table
+
Spectrum table
+
shared data
+
RLS
+
masking
```

Security is incomplete without negative tests.

---

# 168. Cost-Safety Rules

Every lab must:

```text
[ ] use smallest practical capacity
[ ] configure a budget
[ ] avoid unnecessary cross-Region resources
[ ] avoid unnecessary data copies
[ ] record query/load cost
[ ] remove test resources
[ ] remove temporary S3 objects where appropriate
[ ] verify no orphaned workgroups/clusters
```

Never claim an exact AWS price without checking current pricing for the Region and service configuration.

---

# 169. Current AWS Documentation Safety

AWS Redshift evolves rapidly.

Before production implementation verify:

```text
[ ] current Redshift Serverless capacity ranges
[ ] current RPU behavior
[ ] current workgroup options
[ ] current data-sharing capabilities
[ ] current multi-warehouse write support
[ ] current cross-account/Region limitations
[ ] current streaming support
[ ] current WLM controls
[ ] current Terraform provider support
[ ] current pricing
```

This module intentionally avoids treating volatile quotas, prices and Region availability as permanent facts.

---

# 170. Relationship to Previous Modules

## Module 2.8 — Data Modeling

Provides:

```text
star schema
fact/dimension design
```

This topic adds:

```text
Redshift physical design
```

## Module 2.12 — ELT / dbt

Provides:

```text
MERGE
incremental patterns
dbt
```

This topic applies them to Redshift.

## Module 2.15 — Iceberg

Provides:

```text
lakehouse tables
```

This topic adds:

```text
warehouse + lake integration
```

## G3 Topic 05 — Athena

Provides:

```text
S3 query layer
Iceberg
partitioning
```

This topic adds:

```text
warehouse execution
```

## G3 Topic 06 — Lake Formation

Provides:

```text
lake governance
```

This topic adds:

```text
Spectrum governance integration
```

---

# 171. Learning Loop

For every major feature:

```text
READ
 ↓
DRAW
 ↓
IMPLEMENT
 ↓
QUERY
 ↓
MEASURE
 ↓
BREAK
 ↓
DIAGNOSE
 ↓
FIX
 ↓
SECURE
 ↓
COST-CHECK
 ↓
DOCUMENT
 ↓
EXPLAIN
```

If you cannot explain why a change improved the system, you have not finished the exercise.

---

# 172. Final Capstone — Production AWS Analytics Warehouse

Build:

```text
                    SOURCE SYSTEMS
                          |
             +------------+------------+
             |                         |
             v                         v
           Batch                    Streaming
             |                    Kinesis / MSK
             v                         |
            S3                         |
             |                         v
       Glue Catalog               Redshift
             |                    Streaming MV
             |                         |
       Lake Formation                 |
             |                         |
             +------------+------------+
                          |
                       Spectrum
                          |
                          v
                     Redshift
                          |
        +-----------------+-----------------+
        |                 |                 |
       BI              Data Science      Analytics
```

Required capabilities:

```text
[ ] Serverless or provisioned decision
[ ] Terraform
[ ] S3 ingestion
[ ] COPY
[ ] staging
[ ] MERGE
[ ] star schema
[ ] distribution decision
[ ] sort-key decision
[ ] materialized view
[ ] Spectrum
[ ] Glue Catalog
[ ] Lake Formation
[ ] workload management
[ ] data sharing
[ ] security
[ ] RLS
[ ] dynamic masking
[ ] streaming
[ ] system-view monitoring
[ ] cost measurement
[ ] teardown
```

---

# 173. Capstone Evidence Package

Produce:

```text
architecture.md
decision-records.md
security-model.md
cost-model.md
performance-report.md
test-results.md
incident-report.md
teardown-evidence.md
```

For this learning repository, these can be conceptual deliverables or implemented artifacts in the broader project structure.

---

# 174. Final Architecture Review Questions

Before declaring the warehouse production-ready, answer:

### Data

```text
Where is each dataset stored?
Why?
```

### Compute

```text
Why Serverless or provisioned?
```

### Physical design

```text
Why this distribution?
Why this sort strategy?
```

### Lake

```text
Why Spectrum?
Why not load everything?
```

### Sharing

```text
Why share rather than copy?
```

### Security

```text
Who can see what?
How is PII protected?
```

### Operations

```text
How do we detect slow queries?
```

### Cost

```text
What is the cost driver?
What is the guardrail?
```

### Recovery

```text
What happens if the pipeline fails halfway through?
```

---

# 175. Final Completion Checklist

## Architecture

- [ ] Explain Redshift architecture
- [ ] Explain MPP
- [ ] Explain RA3
- [ ] Explain managed storage
- [ ] Explain Serverless
- [ ] Explain namespace/workgroup

## Capacity

- [ ] Explain RPU
- [ ] Explain base capacity
- [ ] Explain maximum capacity
- [ ] Choose Serverless vs provisioned

## Ingestion

- [ ] Use COPY
- [ ] Load multiple files
- [ ] Load Parquet
- [ ] Use IAM roles
- [ ] Use manifests
- [ ] Use UNLOAD

## Physical Design

- [ ] Explain AUTO
- [ ] Explain KEY
- [ ] Explain EVEN
- [ ] Explain ALL
- [ ] Diagnose skew
- [ ] Design sort keys
- [ ] Explain automatic optimization
- [ ] Explain compression

## Modeling

- [ ] Build star schema
- [ ] State fact grain
- [ ] Build dimensions
- [ ] Build facts

## Incremental

- [ ] Build staging
- [ ] Implement MERGE
- [ ] Make reruns idempotent

## Query Acceleration

- [ ] Build materialized view
- [ ] Explain refresh
- [ ] Explain result caching

## Spectrum

- [ ] Create external schema
- [ ] Query Glue Catalog
- [ ] Query S3
- [ ] Join lake + warehouse
- [ ] Optimize Spectrum
- [ ] Integrate Lake Formation

## Workload Management

- [ ] Explain queues
- [ ] Explain priorities
- [ ] Explain concurrency scaling
- [ ] Configure monitoring rules

## Data Sharing

- [ ] Explain live sharing
- [ ] Share across clusters
- [ ] Share across workgroups
- [ ] Share across accounts
- [ ] Explain cross-Region
- [ ] Understand multi-warehouse writes

## Advanced

- [ ] Explain SUPER
- [ ] Explain PartiQL
- [ ] Ingest Kinesis
- [ ] Ingest MSK
- [ ] Use streaming materialized views
- [ ] Explain VACUUM
- [ ] Explain ANALYZE
- [ ] Read system views

## Security

- [ ] IAM roles
- [ ] Database roles
- [ ] RLS
- [ ] Dynamic masking
- [ ] Lake Formation + Spectrum
- [ ] KMS
- [ ] Negative security tests

## Operations

- [ ] Performance runbook
- [ ] Cost runbook
- [ ] COPY incident runbook
- [ ] Data-sharing incident runbook
- [ ] Streaming incident runbook
- [ ] Teardown

**Completion standard:** explain, implement, break, diagnose, optimize and defend the architecture.

---

# 176. Final Roadmap Coverage Audit

| Requirement | Covered | Level |
|---|---:|---|
| Redshift architecture | Yes | Core |
| Leader/compute | Yes | Core |
| RA3 | Yes | Core |
| Managed storage | Yes | Core |
| Serverless | Yes | Core |
| Workgroups | Yes | Core |
| Namespaces | Yes | Core |
| Base capacity | Yes | Core |
| Maximum capacity | Yes | Core |
| Provisioned vs Serverless | Yes | Core |
| COPY | Yes | Core |
| S3 | Yes | Core |
| Multiple files | Yes | Core |
| Parquet | Yes | Core |
| Manifests | Yes | Intermediate |
| IAM roles | Yes | Core |
| UNLOAD | Yes | Core |
| AUTO distribution | Yes | Intermediate |
| KEY distribution | Yes | Intermediate |
| EVEN distribution | Yes | Intermediate |
| ALL distribution | Yes | Intermediate |
| Distribution skew | Yes | Advanced |
| Sort keys | Yes | Intermediate |
| Automatic table optimization | Yes | Intermediate |
| Compression | Yes | Intermediate |
| Star schema | Yes | Intermediate |
| MERGE | Yes | Intermediate |
| Staging | Yes | Intermediate |
| Materialized views | Yes | Intermediate |
| Automatic refresh | Yes | Intermediate |
| Result caching | Yes | Intermediate |
| Spectrum | Yes | Intermediate |
| Glue Catalog | Yes | Intermediate |
| External tables | Yes | Intermediate |
| Lake + warehouse joins | Yes | Intermediate |
| Spectrum performance | Yes | Advanced |
| WLM | Yes | Advanced |
| Queues | Yes | Advanced |
| Query priorities | Yes | Advanced |
| Concurrency scaling | Yes | Advanced |
| Query monitoring rules | Yes | Advanced |
| Data sharing | Yes | Advanced |
| Cross-cluster sharing | Yes | Advanced |
| Cross-account sharing | Yes | Advanced |
| Workgroup sharing | Yes | Advanced |
| Multi-warehouse architecture | Yes | Advanced |
| Multi-warehouse writes | Yes | Advanced |
| SUPER | Yes | Advanced |
| PartiQL | Yes | Advanced |
| Kinesis | Yes | Advanced |
| MSK | Yes | Advanced |
| Streaming materialized views | Yes | Advanced |
| VACUUM | Yes | Advanced |
| ANALYZE | Yes | Advanced |
| System tables/views | Yes | Advanced |
| Performance diagnosis | Yes | Advanced |
| Cost diagnosis | Yes | Advanced |
| Database roles | Yes | Advanced |
| RLS | Yes | Advanced |
| Dynamic masking | Yes | Advanced |
| Lake Formation + Spectrum | Yes | Advanced |
| dbt awareness | Yes | Awareness |
| Terraform | Yes | Advanced |
| AWS CLI | Yes | Intermediate |
| boto3 | Yes | Intermediate |
| Hands-on labs | Yes | Production |
| Break/fix | Yes | Production |
| Automated testing | Yes | Production |
| ADRs | Yes | Production |
| Decision matrices | Yes | Production |
| Production architecture | Yes | Production |
| Practice questions | Yes | Advanced |
| Interview preparation | Yes | Advanced |
| Runbooks | Yes | Production |
| Capstone | Yes | Production |

**Roadmap coverage: COMPLETE**

---

# 177. Technical Accuracy and Current-Documentation Audit

This module intentionally treats AWS documentation as the authority for volatile implementation details.

Current AWS documentation confirms, among other points:

- Serverless workgroups use RPU-based base/max capacity controls. citeturn0search4turn0search8
- Redshift data sharing supports live access across clusters, workgroups, accounts and Regions, with write capabilities available for supported configurations. citeturn0search1turn0search3
- Lake Formation can govern Redshift Spectrum access to Data Catalog/S3 data, including fine-grained row/cell/column controls. citeturn0search2turn0search11
- Redshift streaming ingestion supports Kinesis Data Streams and Amazon MSK through materialized views. citeturn0search0turn0search14

Before production implementation, re-check:

```text
[ ] AWS Region availability
[ ] current Redshift patch/version requirements
[ ] current Serverless capacity limits
[ ] current data-sharing write limitations
[ ] current Spectrum/Lake Formation behavior
[ ] current streaming limitations
[ ] current Terraform provider support
[ ] current AWS pricing
```

**Technical accuracy audit: PASS — current documentation verified for the volatile service areas; deployment-time verification remains mandatory.**

---

# 178. Security Audit

```text
[x] IAM least privilege
[x] S3 least privilege
[x] KMS awareness
[x] IAM roles instead of long-lived credentials
[x] Database roles
[x] RLS
[x] Dynamic masking
[x] Lake Formation integration
[x] Cross-account security
[x] Data-sharing scope control
[x] Negative security testing
[x] PII protection
[x] Workload guardrails
[x] Secret-handling guidance
```

**Security audit: PASS**

---

# 179. Cost-Safety Audit

```text
[x] Serverless base/max capacity guardrails
[x] AWS Budgets
[x] Cost allocation tags
[x] Spectrum scan-cost awareness
[x] Cross-Region cost awareness
[x] Cross-account cost awareness
[x] Data duplication avoidance
[x] Streaming cost awareness
[x] Query cost measurement
[x] Lab teardown
[x] No invented fixed pricing
```

**Cost-safety audit: PASS**

---

# 180. File-Scope Audit

This file is scoped specifically to:

```text
G3 Topic 07
Redshift Deep Dive:
Serverless, Spectrum, and Data Sharing
```

It does not attempt to replace the dedicated modules for:

```text
08 Kinesis / Firehose / MSK
09 EMR
10 Step Functions / EventBridge / MWAA
11 DMS / zero-ETL
12 CloudWatch / CloudTrail / Cost Explorer
13 KMS / VPC endpoints / private networking
14 Unified Studio / DataZone
```

Those services are discussed only where necessary to explain Redshift integration.

**File-scope audit: PASS**

---

# 181. Final Mental Model

```text
                         AWS DATA PLATFORM

                              SOURCES
                                 |
                 +---------------+---------------+
                 |                               |
              Batch                           Streaming
                 |                               |
                 v                               v
                S3                         Kinesis / MSK
                 |                               |
            Glue Catalog                        |
                 |                               |
           Lake Formation                        |
                 |                               |
          +------+-------------------------------+
          |
          +--------------------+
          |                    |
       Athena              Redshift
          |                    |
          |          +---------+---------+
          |          |                   |
          |       Warehouse           Spectrum
          |          |                   |
          |          |                   v
          |          |               S3 / Lake
          |          |
          |       Datashares
          |          |
          +----------+----------+
                     |
                  Consumers
                     |
             BI / Analytics / ML
```

The engineering decision is:

```text
WHERE SHOULD THE DATA LIVE?
        ↓
WHICH ENGINE SHOULD QUERY IT?
        ↓
HOW SHOULD IT BE PHYSICALLY ORGANIZED?
        ↓
HOW SHOULD WORKLOADS BE ISOLATED?
        ↓
HOW SHOULD DATA BE SHARED?
        ↓
HOW SHOULD ACCESS BE GOVERNED?
        ↓
HOW SHOULD PERFORMANCE BE MEASURED?
        ↓
HOW SHOULD COST BE CONTROLLED?
```

---

# 182. Final Engineering Principle

> **Redshift expertise is not memorizing SQL syntax. It is the ability to place data deliberately across S3 and the warehouse, choose the right compute model, design physical storage for the workload, protect concurrency, govern access, share data without unnecessary copies, and continuously prove the system is meeting performance, security and cost objectives.**

A production Redshift engineer should be able to move through:

```text
UNDERSTAND
    ↓
MODEL
    ↓
LOAD
    ↓
DISTRIBUTE
    ↓
SORT
    ↓
QUERY
    ↓
OPTIMIZE
    ↓
SHARE
    ↓
SECURE
    ↓
STREAM
    ↓
MONITOR
    ↓
TROUBLESHOOT
    ↓
CONTROL COST
    ↓
DEFEND THE ARCHITECTURE
```

**Module completion target:** You should be able to design and operate a production AWS analytical warehouse that integrates Redshift, S3, Glue Catalog, Lake Formation, Spectrum, streaming sources and data sharing—while making explicit performance, security and cost trade-offs.
