# Module 2.20.04 — Data Lineage with OpenLineage

> **Roadmap:** Stage 2 → Module 2.20 — Observability, Lineage, Governance, and Security  
> **Topic:** 04 — Data Lineage with OpenLineage  
> **Level:** Beginner → Fundamentals → Practical → Advanced → Production

## Primary Learning Objective

By the end of this module, you should be able to answer:

> **Where did this dataset come from, which upstream systems produced it, which downstream datasets and consumers depend on it, what transformations occurred, and what will break if I change or remove it?**

The central principle is:

> **Lineage explains the flow and dependency relationships of data through a data platform.**

A mature lineage system supports:

```text
Discovery
   ↓
Impact Analysis
   ↓
Root-Cause Analysis
   ↓
Change Management
   ↓
Compliance
   ↓
Deprecation
   ↓
Operational Debugging
```

---

# 1. What Is Data Lineage?

Data lineage is the history and dependency graph showing:

- where data came from
- how it was transformed
- where it went
- which systems produced or consumed it
- which downstream assets depend on it

A simple example:

```text
API
 ↓
Raw Orders
 ↓
Clean Orders
 ↓
Orders Aggregate
 ↓
Revenue Dashboard
```

A data-platform representation could be:

```text
API
  ↓
raw.orders
  ↓
silver.orders
  ↓
gold.daily_revenue
  ↓
Finance Dashboard
```

Lineage is therefore a **relationship graph**, not merely a list of tables.

---

## 1.1 Why lineage matters

Without lineage, an engineer may see:

```text
gold.daily_revenue
```

and have to guess:

- who produced it
- which source tables feed it
- which jobs modify it
- which dashboards depend on it
- whether changing it will break another system

With lineage:

```text
raw.orders
   ↓
silver.orders
   ↓
gold.daily_revenue
   ↓
Finance Dashboard
```

the dependency structure becomes explicit.

---

## Checkpoint

**1. What is data lineage?**  
It is the history and dependency graph showing where data originated, how it was transformed, and where it flows.

**2. Why is lineage operationally useful?**  
It reduces uncertainty during discovery, impact analysis, debugging, change management, and deprecation.

---

# 2. Major Production Use Cases

## 2.1 Impact analysis

Question:

> If I change `raw.orders`, what downstream datasets might break?

```text
raw.orders
    ↓
silver.orders
    ↓
gold.revenue
    ↓
Finance Dashboard
```

Lineage reveals both direct and transitive dependencies.

## 2.2 Root-cause analysis

Question:

> Why is `gold.revenue` wrong?

Trace upstream:

```text
gold.revenue
    ↑
silver.orders
    ↑
raw.orders
    ↑
API
```

Then combine lineage with runtime metadata and data-quality signals to narrow the investigation.

## 2.3 Compliance

Lineage can help answer:

- Where does customer data flow?
- Which datasets are derived from a source?
- Which downstream systems may contain affected data?

Important:

> **Lineage alone does not satisfy compliance requirements.**

Compliance also requires appropriate controls, access management, retention, evidence, policies, and organizational processes.

## 2.4 Deprecation

Before removing a table:

```text
dataset_to_remove
       ↓
downstream tables
       ↓
dashboards
       ↓
ML features
       ↓
reports
```

Lineage helps identify consumers that must migrate before removal.

---

# 3. Table-Level Lineage

Table-level lineage represents relationships between datasets.

```text
source table
      ↓
transformation
      ↓
target table
```

Example:

```text
raw.orders
      ↓
silver.orders
      ↓
gold.daily_revenue
```

The key concepts are:

| Concept | Meaning |
|---|---|
| Source | Dataset being consumed |
| Target | Dataset being produced |
| Transformation | Logic connecting source to target |
| Dependency | Relationship between assets |
| Direction | Upstream → downstream flow |

Table-level lineage is the foundation. Column-level lineage adds much more detail.

---

# 4. Column-Level Lineage

Column lineage answers:

> Which source columns contributed to this target column?

Simple mapping:

```text
raw.orders.customer_id
        ↓
silver.orders.customer_id
        ↓
gold.revenue.customer_id
```

Transformation example:

```text
orders.amount
orders.tax
      ↓
SUM(amount + tax)
      ↓
daily_revenue.revenue
```

Column lineage is more precise but harder to produce correctly because transformations can involve:

- joins
- aliases
- nested queries
- UDFs
- dynamic SQL
- stored procedures
- runtime-generated data

---

# 5. Lineage Graph Terminology

A lineage graph contains nodes and edges.

```text
A ──→ B ──→ C ──→ D
```

| Term | Meaning |
|---|---|
| Node | Asset/entity represented in the graph |
| Edge | Relationship between nodes |
| Source | Upstream input |
| Target | Downstream output |
| Upstream | Where data comes from |
| Downstream | Where data goes |
| Parent | Immediate predecessor |
| Child | Immediate successor |
| Dependency | Relationship requiring another asset |
| Direct dependency | Immediate relationship |
| Transitive dependency | Dependency reached through other nodes |
| Transformation | Logic converting inputs to outputs |

For node `C`:

```text
Upstream:
A, B

Downstream:
D
```

The distinction between direct and transitive dependencies matters during impact analysis.

---

# 6. Upstream vs Downstream

Consider:

```text
A → B → C → D
```

For `C`:

```text
Direct upstream:
B

Transitive upstream:
A

Direct downstream:
D
```

For impact analysis, an engineer often needs the entire reachable downstream graph, not merely the immediate child.

---

## Checkpoint

You should now be able to explain:

1. What is table-level lineage?
2. What is column-level lineage?
3. What is upstream?
4. What is downstream?
5. What is a direct dependency?
6. What is a transitive dependency?

**Answers:** Table lineage connects datasets; column lineage connects source and target fields; upstream describes sources; downstream describes consumers; direct dependencies are immediate; transitive dependencies are reached through one or more intermediate assets.

---

# 7. Design-Time vs Runtime Lineage

This distinction is mandatory for production lineage.

## 7.1 Design-time lineage

Design-time lineage is inferred from definitions before or independently of a particular execution.

Sources include:

- SQL
- DAG definitions
- dbt models
- pipeline code
- schemas

Example:

```text
dbt SQL
   ↓
source.orders → model.orders
```

It tells us what a pipeline is designed to do.

## 7.2 Runtime lineage

Runtime lineage is captured from an actual execution.

Example:

```text
Job:
orders_pipeline

Run:
2026-10-05T06:00Z

Input:
raw.orders

Output:
silver.orders
```

Runtime lineage can provide evidence about what actually happened during a specific execution.

## 7.3 Why use both?

```text
Design-time lineage
+
Runtime lineage
=
stronger operational understanding
```

Design-time is useful for planning and static dependency discovery.

Runtime is useful for:

- actual execution evidence
- run-specific inputs/outputs
- failures
- execution metadata
- debugging

---

# 8. Limitations of Design-Time Lineage

Static analysis cannot always reconstruct runtime behavior.

Difficult cases include:

- dynamic SQL
- runtime-generated tables
- conditional branches
- dynamic paths
- external APIs
- Python code
- notebooks
- stored procedures
- UDFs
- runtime-selected datasets

Example:

```python
table = choose_table(environment)
```

A static parser may not know which table is actually selected.

Therefore:

> Design-time lineage is valuable, but it is not automatically a perfect representation of runtime behavior.

---

# 9. Limitations of Runtime Lineage

Runtime lineage can also have gaps.

Possible missing sources include:

- uninstrumented systems
- manual data movement
- external SaaS systems
- notebook execution
- ad-hoc SQL
- legacy tools
- unsupported connectors

Therefore:

> **Production lineage is usually a combination of automated and manually documented lineage.**

The objective is not to pretend that every relationship is automatically captured. The objective is to make coverage and gaps visible.

---

# 10. OpenLineage

OpenLineage is an open standard for collecting and exchanging lineage metadata/events.

It provides a common model around:

- jobs
- runs
- datasets
- events
- facets

It is useful because different systems can emit lineage using a common representation.

A simplified architecture is:

```text
Data System
    ↓
OpenLineage Integration
    ↓
OpenLineage Events
    ↓
Lineage Backend
    ↓
Catalog / Lineage UI
```

Typical producers include:

```text
Airflow
Spark
dbt
Python
   ↓
OpenLineage
   ↓
Lineage backend
```

Important distinction:

> **OpenLineage is primarily a standard for collecting and exchanging lineage metadata/events; it is not itself a complete data catalog.**

---

# 11. OpenLineage Architecture

A production-oriented conceptual architecture:

```text
┌───────────────┐
│ Airflow       │
└───────┬───────┘
        │
┌───────▼───────┐
│ Spark         │
└───────┬───────┘
        │
┌───────▼───────┐
│ dbt           │
└───────┬───────┘
        │
┌───────▼───────┐
│ Python Jobs   │
└───────┬───────┘
        │
        ▼
   OpenLineage
        │
        ▼
┌────────────────┐
│ Marquez /      │
│ compatible     │
│ lineage store  │
└───────┬────────┘
        │
        ▼
   Lineage UI
```

Each producer is responsible for generating appropriate lineage events. The backend stores/processes those events for exploration and analysis.

---

# 12. OpenLineage Data Model

This is one of the most important sections.

## 12.1 Job

A **Job** represents logical work.

Example:

```text
orders_daily_pipeline
```

The job identifies the operation independently of one particular execution.

## 12.2 Run

A **Run** represents one execution of a job.

```text
Job:
orders_daily_pipeline

Run:
2026-10-05T06:00:00Z
```

A job may have many runs:

```text
orders_daily_pipeline
 ├── run A
 ├── run B
 ├── run C
 └── run D
```

## 12.3 Dataset

A Dataset represents data consumed or produced.

Examples:

```text
postgres.orders
s3://lake/raw/orders
warehouse.gold.daily_revenue
```

## 12.4 Event

An Event describes what happened during execution.

The required lifecycle concepts are:

- START
- COMPLETE
- FAIL

---

# 13. OpenLineage Event Lifecycle

Normal execution:

```text
START
  ↓
execution
  ↓
COMPLETE
```

Failed execution:

```text
START
  ↓
execution
  ↓
FAIL
```

Conceptual START event:

```json
{
  "eventType": "START",
  "job": {
    "namespace": "data-platform",
    "name": "orders_daily"
  },
  "run": {
    "runId": "..."
  }
}
```

A COMPLETE event represents successful completion.

A FAIL event represents unsuccessful execution.

The lifecycle matters because runtime lineage without execution state is less useful operationally.

---

# 14. Namespace and Name Design

Consistent identity is foundational to useful lineage.

Poor naming:

```text
job1
table1
```

Better:

```text
namespace:
production.data-platform

job:
orders_daily

dataset:
warehouse.gold.daily_revenue
```

A practical naming strategy should make it possible to distinguish:

- environment
- platform/domain
- job identity
- dataset identity

Do not create arbitrary names for every integration.

Consistency matters because lineage quality degrades when the same logical asset appears under many unrelated identities.

---

# 15. Facets

Facets attach additional metadata to OpenLineage entities/events.

Required categories:

- schema facets
- data source facets
- SQL facets
- column lineage facets
- data quality facets
- custom facets

Think of the model as:

```text
Job / Run / Dataset / Event
            +
          Facets
            ↓
     richer lineage context
```

---

# 16. Schema Facets

Schema metadata can describe:

- column names
- data types
- schema information

Conceptual representation:

```json
{
  "schema": {
    "fields": [
      {"name": "customer_id", "type": "string"},
      {"name": "amount", "type": "decimal"}
    ]
  }
}
```

Schema information improves lineage usability because engineers can see not only that two datasets are related, but also what structures were involved.

---

# 17. Data Source Facets

Data source metadata can describe:

- source system
- dataset location
- connection context where appropriate

Examples:

```text
PostgreSQL
S3
Kafka
Warehouse
```

Never put:

```text
password
API token
secret key
private credential
```

into lineage metadata.

---

# 18. SQL Facets

SQL metadata can describe transformations.

Example:

```sql
SELECT
    customer_id,
    SUM(amount) AS revenue
FROM orders
GROUP BY customer_id;
```

SQL metadata can help lineage systems understand relationships between source and target fields.

However:

> SQL presence does not guarantee perfect column-level lineage.

Parsing can fail or become ambiguous for complex constructs.

---

# 19. Column Lineage Facets

Column lineage describes:

```text
source column
      ↓
transformation
      ↓
target column
```

Example:

```text
orders.amount
orders.tax
     ↓
amount + tax
     ↓
daily_revenue.total_revenue
```

Column-level metadata is highly valuable for:

- schema change analysis
- sensitive-data propagation analysis
- debugging
- compliance investigations
- deprecation planning

---

# 20. Data Quality Facets

Lineage becomes significantly more useful when quality information travels with it.

Examples:

```text
row_count
null_rate
duplicate_rate
quality_status
```

Consider:

```text
gold.revenue
   ↑
silver.orders
   ↑
raw.orders
```

with:

```text
raw.orders quality = FAIL
null_rate = 31%
```

Now lineage can help answer:

> Which downstream datasets may have been affected by this quality failure?

This is much stronger than viewing lineage and data quality as unrelated systems.

---

# 21. Custom Facets

Standard metadata may not capture organization-specific information.

Examples:

```text
business_owner
cost
classification
retention_policy
SLO
incident_id
```

Custom facets are useful when the metadata is genuinely part of the lineage context.

Avoid uncontrolled fields such as:

```text
field1
field2
random_note
temporary_value
```

Custom metadata should have:

- documented meaning
- stable naming
- ownership
- versioning expectations

---

## Checkpoint

1. **What is a facet?**  
   Additional metadata attached to OpenLineage entities/events.

2. **Why are facets important?**  
   They enrich the basic Job/Run/Dataset/Event model with operational and transformation context.

3. **What are the required facet categories?**  
   Schema, data source, SQL, column lineage, data quality, and custom facets.

---

# 22. OpenLineage Python Client

The Python client provides a way for custom Python applications to construct and emit OpenLineage events.

The conceptual workflow is:

```text
Create Job
   ↓
Create Run
   ↓
Describe input datasets
   ↓
Describe output datasets
   ↓
Attach facets
   ↓
Emit START
   ↓
Run work
   ↓
Emit COMPLETE or FAIL
```

Because exact client APIs can vary by package version, pin the OpenLineage Python client version used by your platform and validate code against that version rather than copying unverified examples.

A production implementation should treat event construction as application instrumentation, not as arbitrary logging.

---

# 23. Custom Python Lineage Emitter

Consider:

```text
Python ingestion job
        ↓
reads API
        ↓
writes object storage
```

The lineage should represent:

```text
START
  ↓
API source
  ↓
raw.orders
  ↓
COMPLETE
```

or:

```text
START
  ↓
API source
  ↓
FAIL
```

A robust emitter should capture:

```text
Job
Run
Input dataset
Output dataset
Execution lifecycle
Useful facets
```

### Instrumentation pattern

```python
def run_pipeline():
    run_id = create_run_id()

    emit_start(
        job="orders_ingestion",
        run_id=run_id,
        inputs=["external.orders_api"],
        outputs=["object_store.raw.orders"],
    )

    try:
        records = extract()
        transformed = transform(records)
        load(transformed)

        emit_complete(
            job="orders_ingestion",
            run_id=run_id,
        )
    except Exception as exc:
        emit_fail(
            job="orders_ingestion",
            run_id=run_id,
            error=str(exc),
        )
        raise
```

The function names above are intentionally conceptual. Replace them with the actual OpenLineage client methods for the pinned library version.

---

# 24. Python Pipeline Lineage

A custom pipeline may look like:

```text
extract()
   ↓
transform()
   ↓
load()
```

Lineage:

```text
source.api
     ↓
raw.orders
     ↓
silver.orders
     ↓
warehouse.orders
```

Automatic integrations are not universal. Custom Python instrumentation is therefore important for:

- internal frameworks
- specialized ingestion
- external APIs
- custom transformations
- legacy jobs
- unsupported systems

---

# 25. Airflow + OpenLineage

Airflow provides orchestration context:

```text
Airflow DAG
    ↓
Tasks
    ↓
OpenLineage integration
    ↓
Lineage events
```

Useful lineage context includes:

- DAG/job
- task/run
- inputs
- outputs
- execution lifecycle
- metadata/facets where supported

Airflow's orchestration metadata and OpenLineage's standardized event model complement each other.

Do not assume:

> Every Airflow task automatically produces perfect lineage.

Integration coverage depends on operators, versions, connectors, task behavior, and how datasets are accessed.

---

# 26. Spark + OpenLineage

Conceptually:

```text
Spark application
      ↓
OpenLineage integration
      ↓
Input datasets
      ↓
Transformations
      ↓
Output datasets
```

Relevant metadata may include:

- Spark application/job context
- dataset inputs
- dataset outputs
- SQL/query metadata
- schema metadata
- column lineage where supported
- runtime execution information

Spark UI and OpenLineage serve different purposes.

```text
Spark UI
→ execution performance/debugging

OpenLineage
→ data dependency/execution lineage
```

They complement one another.

---

# 27. dbt + OpenLineage

dbt naturally expresses design-time dependencies:

```text
dbt source
    ↓
dbt model
    ↓
dbt model
```

dbt metadata and runtime lineage are complementary:

```text
dbt metadata
+
OpenLineage runtime events
```

Relevant information can include:

- sources
- models
- runs
- SQL
- dependencies
- column lineage where supported

Again, exact integration behavior depends on the versions and deployment architecture in use.

---

# 28. Marquez

Marquez is a practical OpenLineage-compatible lineage backend and UI useful for learning and operational exploration.

Conceptually:

```text
Airflow / Spark / dbt / Python
          ↓
       OpenLineage
          ↓
        Marquez
          ↓
       Lineage UI
```

Important distinction:

```text
OpenLineage
= standard/event model

Marquez
= backend/UI implementation
```

Do not treat Marquez as synonymous with OpenLineage.

---

# 29. Local OpenLineage Lab

A practical local learning architecture:

```text
Python
  +
OpenLineage
  +
Marquez
```

Docker Compose is appropriate for a reproducible local environment.

## Lab objectives

You should be able to:

1. Start a local lineage backend.
2. Configure an OpenLineage endpoint.
3. Create a job identity.
4. Create a run identity.
5. Define input datasets.
6. Define output datasets.
7. Emit START.
8. Execute a small pipeline.
9. Emit COMPLETE.
10. Intentionally fail the pipeline.
11. Emit FAIL.
12. Attach useful facets.
13. Inspect the resulting lineage.

### Conceptual configuration

```text
Application
   ↓
OpenLineage client
   ↓
OpenLineage HTTP endpoint
   ↓
Marquez
   ↓
Lineage UI
```

The exact Docker images, ports, and client configuration should be pinned to the versions selected for your lab; validate them against the corresponding current documentation rather than treating illustrative values as universal.

---

# 30. End-to-End Lineage Example

Consider:

```text
API
 ↓
Python ingestion
 ↓
PostgreSQL / object storage
 ↓
Spark transformation
 ↓
Warehouse
 ↓
BI
```

Logical lineage:

```text
API
 ↓
raw.orders
 ↓
silver.orders
 ↓
gold.daily_revenue
 ↓
Finance Dashboard
```

Possible runtime jobs:

```text
orders_ingestion
spark_orders_cleaning
revenue_aggregation
```

Each execution can produce:

```text
START
COMPLETE / FAIL
```

with inputs and outputs represented as datasets.

---

# 31. Lineage + Run Metadata

Lineage becomes much more powerful when connected to execution metadata.

Example:

```text
run_id:
orders:2026-10-05:prod

trace_id:
4bf92f...

job:
orders_daily

inputs:
raw.orders

outputs:
gold.daily_revenue
```

The combined view lets an engineer move from:

```text
Dataset
```

to:

```text
Which job produced it?
Which run?
Which inputs?
What happened?
Which downstream assets were affected?
```

This complements the run metadata and observability work from earlier Module 2.20 topics.

---

# 32. Lineage + Data Quality

Consider:

```text
gold.daily_revenue
       ↑
silver.orders
       ↑
raw.orders
```

Suppose:

```text
raw.orders:
quality = FAIL
null_rate = 31%
```

Lineage lets us traverse from the failed source to potentially affected downstream assets.

The combined model is:

```text
Data Quality
     +
Lineage
     +
Run Metadata
     ↓
Operational Diagnosis
```

This is substantially more useful than any one of the three systems alone.

---

# 33. Root-Cause Analysis Using Lineage

Incident:

```text
gold.daily_revenue is 18% lower than expected.
```

Start at the affected output:

```text
gold.daily_revenue
       ↑
silver.orders
       ↑
raw.orders
       ↑
API
```

Then inspect evidence at each layer.

Example discovery:

```text
gold.daily_revenue
→ aggregation completed

silver.orders
→ row count unexpectedly low

raw.orders
→ input volume unexpectedly low

API
→ incomplete order response
```

Likely root cause:

```text
API returned incomplete order records
```

Lineage did not prove the root cause by itself. It reduced the search space so the engineer could investigate the correct upstream systems.

---

# 34. Impact Analysis

Scenario:

> The `customer_id` column in `raw.customers` is going to change type.

Question:

> What downstream systems could be affected?

Potential graph:

```text
raw.customers
   ↓
silver.customers
   ↓
gold.customer_metrics
   ↓
BI
   ↓
ML feature pipeline
```

A production impact analysis should consider:

- direct impact
- transitive impact
- consumer impact
- schema impact
- business impact
- column-level dependencies

Table-level lineage may show:

```text
raw.customers → gold.customer_metrics
```

Column-level lineage can reveal whether the specific `customer_id` column actually reaches downstream consumers.

---

# 35. Safe Dataset Deprecation Workflow

A safe workflow is:

```text
Candidate for deprecation
        ↓
Find downstream lineage
        ↓
Identify owners
        ↓
Identify consumers
        ↓
Notify consumers
        ↓
Migrate consumers
        ↓
Verify no active dependencies
        ↓
Deprecate
        ↓
Remove
```

Do not remove a dataset merely because its direct job dependency appears empty. Check:

- ad-hoc consumers
- dashboards
- ML features
- notebooks
- external systems
- undocumented processes

This is where lineage gaps become especially important.

---

# 36. Column-Level Lineage Deep Dive

## Example 1 — direct projection

```sql
SELECT customer_id
FROM orders;
```

Conceptual lineage:

```text
orders.customer_id
        ↓
target.customer_id
```

## Example 2 — expression

```sql
SELECT
    amount * 1.18 AS amount_with_tax
FROM orders;
```

```text
orders.amount
      ↓
amount * 1.18
      ↓
target.amount_with_tax
```

## Example 3 — aggregation

```sql
SELECT
    customer_id,
    SUM(amount + tax) AS revenue
FROM orders
GROUP BY customer_id;
```

Conceptual mapping:

```text
orders.customer_id
        ↓
target.customer_id

orders.amount ─┐
               ├→ amount + tax → SUM → target.revenue
orders.tax ────┘
```

## Example 4 — join

```sql
SELECT
    o.order_id,
    c.customer_segment
FROM orders o
JOIN customers c
  ON o.customer_id = c.customer_id;
```

Mappings include:

```text
orders.order_id
    ↓
target.order_id

customers.customer_segment
    ↓
target.customer_segment

orders.customer_id
        +
customers.customer_id
        ↓
join relationship
```

The join condition is itself important dependency information.

---

# 37. SQL Parsing and Column-Lineage Limitations

SQL parsing becomes difficult with:

- nested queries
- CTEs
- aliases
- wildcards
- functions
- UDFs
- dynamic SQL
- stored procedures
- temporary tables
- runtime-generated SQL

Example:

```sql
SELECT *
FROM dynamically_selected_table;
```

The parser may not know which physical dataset will be selected at runtime.

Therefore:

> **Column lineage derived from SQL parsing is valuable but not universally perfect.**

Do not promise 100% automated column lineage.

---

# 38. Lineage Gaps

Real platforms contain gaps:

- external SaaS
- manual uploads
- notebooks
- ad-hoc SQL
- unsupported databases
- custom scripts
- legacy pipelines
- stored procedures
- human workflows

A practical strategy combines:

```text
Automatic lineage
+
Custom emitters
+
Manual metadata
+
Documentation
```

The correct production behavior is to make gaps visible.

Bad:

```text
Lineage graph looks complete
but
many relationships are inferred incorrectly
```

Better:

```text
95% automated coverage
5% explicitly identified lineage gaps
```

Trust depends on knowing where the graph is incomplete.

---

# 39. Lineage Completeness

Lineage quality has multiple dimensions:

- coverage
- completeness
- correctness
- freshness
- missing edges
- unsupported systems

Example:

```text
95% of pipeline jobs emit lineage
5% do not
```

The missing 5% may matter disproportionately if those jobs feed critical financial or customer-facing data.

Therefore measure lineage coverage by **business importance**, not only by job count.

---

# 40. Lineage Quality

Ask:

1. Are job names consistent?
2. Are dataset names stable?
3. Are inputs captured?
4. Are outputs captured?
5. Are runs recorded?
6. Are failures recorded?
7. Are schemas current?
8. Is column lineage accurate?
9. Are external systems represented?
10. Are owners known?

A critical principle:

> **Bad lineage can be worse than incomplete lineage if users trust incorrect relationships.**

For example:

```text
Correct but incomplete
```

is safer than:

```text
Complete-looking but incorrect
```

---

# 41. Security and Privacy of Lineage

Lineage metadata can expose:

- dataset names
- customer-related fields
- internal systems
- SQL
- infrastructure
- business relationships

Protect lineage metadata using appropriate:

- access control
- sensitive metadata classification
- SQL sanitization
- secret avoidance
- retention policies

Never place:

```text
database passwords
API keys
access tokens
private credentials
```

inside lineage events.

This topic should complement, not replace, the dedicated security material elsewhere in the roadmap.

---

# 42. Production Lineage Architecture

A production architecture may look like:

```text
                         ┌───────────────┐
                         │ Airflow       │
                         └───────┬───────┘
                                 │
                         ┌───────▼───────┐
                         │ Spark         │
                         └───────┬───────┘
                                 │
                         ┌───────▼───────┐
                         │ dbt           │
                         └───────┬───────┘
                                 │
                         ┌───────▼───────┐
                         │ Python Jobs   │
                         └───────┬───────┘
                                 │
                            OpenLineage
                                 │
                         ┌───────▼───────┐
                         │ Marquez /     │
                         │ Lineage Store │
                         └───────┬───────┘
                                 │
                         ┌───────▼───────┐
                         │ Catalog / UI  │
                         └───────────────┘
```

Each producer should have a defined instrumentation strategy.

A mature platform also has:

```text
Lineage coverage monitoring
+
Naming standards
+
Ownership
+
Data quality integration
+
Run metadata integration
+
Security controls
+
Gap management
```

---

# 43. Failure-Injection Lab

## Failure 1 — Missing output

A job starts but produces no expected output.

Expected lineage investigation:

```text
Input exists
Output missing
```

Questions:

- Did START occur?
- Did FAIL occur?
- Which run failed?
- Which input was consumed?
- Was any partial output produced?

## Failure 2 — Wrong dataset

A pipeline accidentally writes to:

```text
gold.revenue_test
```

instead of:

```text
gold.daily_revenue
```

Lineage should reveal the unexpected output destination.

## Failure 3 — Upstream quality failure

Input quality degrades severely.

Use lineage to determine:

```text
bad source
   ↓
affected transformations
   ↓
affected outputs
   ↓
affected consumers
```

## Failure 4 — Broken lineage integration

One pipeline stops emitting OpenLineage events.

Expected response:

```text
Detect coverage gap
→ identify affected producer
→ restore instrumentation
→ validate new events
```

Do not silently assume that absence of lineage means absence of dependency.

## Failure 5 — Incorrect column mapping

A transformation changes the meaning of a column.

Use column lineage to investigate, while recognizing that automated lineage may not fully capture semantic changes.

---

# 44. Practical Lineage Questions

## Question 1

What are all upstream dependencies of `gold.daily_revenue`?

### Solution

Traverse the graph backward:

```text
gold.daily_revenue
        ↑
silver.orders
        ↑
raw.orders
        ↑
API
```

Include direct and transitive dependencies.

## Question 2

What downstream datasets depend on `raw.orders.customer_id`?

### Solution

Start with the column node and traverse downstream through column-level relationships, then identify affected tables and consumers.

## Question 3

Which pipelines wrote to `gold.customer_metrics` yesterday?

### Solution

Use runtime lineage:

```text
Dataset
  ↓
producer jobs
  ↓
runs
  ↓
time filter
```

This requires run-aware lineage, not only static design-time relationships.

## Question 4

Which dataset caused a downstream quality incident?

### Solution

Start at the failed output:

```text
quality failure
   ↓
lineage upstream
   ↓
inspect source quality
   ↓
compare run metadata
```

Lineage narrows the search; quality evidence establishes the failure.

## Question 5

Can we safely deprecate `silver.orders_v1`?

### Solution

Do not remove it until:

```text
all downstream dependencies identified
+
owners identified
+
consumers migrated
+
lineage gaps reviewed
+
replacement validated
```

---

# 45. Testing Lineage

Lineage instrumentation should be tested like production code.

Test that:

- START is emitted
- COMPLETE is emitted
- FAIL is emitted
- inputs are present
- outputs are present
- namespace is correct
- dataset names are stable
- facets are valid
- failure events are emitted
- custom Python jobs emit lineage
- external boundaries are documented

## Example test intent

```python
def test_pipeline_emits_complete_lineage():
    run_pipeline()

    assert start_event_exists()
    assert complete_event_exists()

    assert input_dataset_exists("raw.orders")
    assert output_dataset_exists("silver.orders")
```

The helper functions are conceptual; implement them against the lineage backend/test harness selected by the organization.

## CI/CD

A useful pipeline can validate:

```text
Code change
   ↓
Lineage instrumentation tests
   ↓
Schema/name checks
   ↓
Integration test
   ↓
Deployment
```

---

# 46. Common Production Mistakes

| Mistake | Why it happens | Danger | Production fix |
|---|---|---|---|
| Treating lineage as a catalog | Tool boundaries misunderstood | Wrong expectations | Separate event standard from catalog |
| Only table-level lineage | Easier to implement | Weak schema impact analysis | Add column lineage where reliable |
| Assuming column lineage is perfect | Automation over-trusted | Incorrect change analysis | Track limitations and gaps |
| Only design-time lineage | Static metadata is convenient | Misses actual runtime behavior | Add runtime lineage |
| Only runtime lineage | Execution focus dominates | Weak planning/dependency discovery | Combine both |
| Inconsistent dataset naming | Teams evolve independently | Broken graph identity | Define naming standards |
| Inconsistent namespaces | Local conventions | Duplicate identities | Standardize namespaces |
| Missing FAIL events | Success-only instrumentation | Failed runs disappear | Test lifecycle coverage |
| Missing external systems | Integrations stop at platform boundary | Hidden dependencies | Document/custom-emit |
| Ignoring notebooks | Hard to instrument | Unknown consumers | Register/document notebook lineage |
| Ignoring ad-hoc SQL | Difficult to govern | Hidden dependencies | Capture/document where possible |
| No custom emitters | Assuming integrations cover all systems | Large gaps | Build supported emitter patterns |
| Trusting stale lineage | No freshness checks | Bad impact analysis | Monitor lineage freshness |
| No lineage-quality monitoring | Graph assumed correct | Silent degradation | Measure coverage/correctness |
| Exposing sensitive SQL/metadata | Metadata treated as harmless | Security/privacy risk | Access-control and sanitize |
| Assuming automatic integrations capture everything | Vendor/tool optimism | Missing dependencies | Verify coverage |
| No run metadata integration | Dataset graph lacks execution context | Slow debugging | Correlate runs |
| No data-quality integration | Lineage isolated | Weak RCA | Join quality + lineage |
| No impact workflow | Graph exists but unused | Unsafe changes | Operationalize impact analysis |
| No deprecation workflow | Consumers not identified | Breaking removals | Require lineage review |

---

# 47. Production Trade-offs

## Automated vs manual lineage

```text
Automated
→ scalable
→ repeatable
→ may have blind spots

Manual
→ can cover unusual systems
→ expensive to maintain
```

Use both strategically.

## Table vs column lineage

```text
Table lineage
→ broad coverage
→ simpler

Column lineage
→ precise impact analysis
→ harder to derive and validate
```

## Design-time vs runtime

```text
Design-time
→ dependency intent

Runtime
→ execution evidence
```

Use both when practical.

## Completeness vs correctness

A graph that claims everything but is wrong is dangerous.

```text
Accurate incomplete lineage
>
Incorrect complete-looking lineage
```

## Detail vs storage/processing cost

Fine-grained lineage produces more metadata.

Decide where column-level and run-level detail creates real operational value.

## Centralized lineage vs distributed ownership

A central platform can provide standards and visibility, while data teams should own the correctness of their emitted lineage.

## SQL parsing vs runtime instrumentation

SQL parsing is powerful for static transformation understanding.

Runtime instrumentation is stronger for actual execution context.

Neither universally replaces the other.

## Open standard vs vendor-specific features

OpenLineage improves interoperability.

Vendor-specific systems may provide richer product features.

A production architecture should understand the boundary.

## Automatic integrations vs custom emitters

Use automatic integrations for supported systems and custom emitters where the platform has important unsupported boundaries.

---

# 48. Production Lineage Design Principles

A mature lineage platform should establish:

### 1. Stable identity

```text
namespace + name
```

must identify logical assets consistently.

### 2. Explicit execution identity

```text
job + run
```

should distinguish logical work from individual executions.

### 3. Accurate input/output relationships

Do not emit guessed dependencies merely to increase coverage.

### 4. Lifecycle completeness

Where supported:

```text
START
COMPLETE
FAIL
```

should be represented.

### 5. Visible gaps

Make unsupported systems explicit.

### 6. Quality integration

Connect lineage with:

```text
row counts
null rates
quality status
schema checks
```

### 7. Operational integration

Connect lineage with:

```text
run_id
trace_id
incident_id
```

where appropriate.

### 8. Security

Treat lineage metadata as potentially sensitive.

---

# 49. Checkpoint — Production Reasoning

You should now be able to explain:

1. What is data lineage?
2. What is upstream?
3. What is downstream?
4. What is table-level lineage?
5. What is column-level lineage?
6. What is design-time lineage?
7. What is runtime lineage?
8. Why is OpenLineage useful?
9. What is a Job?
10. What is a Run?
11. What is a Dataset?
12. What is an Event?
13. What are facets?

### Answers

1. A graph describing data origin, transformations, and destinations.
2. A source/dependency that feeds the current asset.
3. An asset or consumer that receives data from the current asset.
4. Dataset-to-dataset dependency information.
5. Source-column-to-target-column dependency information.
6. Lineage inferred from definitions such as SQL and DAGs.
7. Lineage captured from an actual execution.
8. It provides a common standard for exchanging lineage events across systems.
9. Logical work.
10. One execution of that work.
11. A consumed or produced data asset.
12. A record describing execution lifecycle/state and related lineage.
13. Additional metadata attached to lineage entities/events.

---

# 50. Final Production Incident Challenge

## Scenario

> The Finance team reports that `gold.daily_revenue` is approximately 18% lower than expected. The pipeline technically completed successfully.

The learner must:

1. Identify the downstream dataset.
2. Trace upstream dependencies.
3. Identify the relevant transformation.
4. Inspect runtime lineage.
5. Inspect data-quality information.
6. Identify the affected source.
7. Determine which other datasets may be affected.
8. Identify impacted business consumers.
9. Determine whether the issue is isolated or systemic.
10. Explain how lineage reduced the investigation scope.

## Expert solution

Start:

```text
gold.daily_revenue
       ↑
silver.orders
       ↑
raw.orders
       ↑
API
```

Then inspect runtime metadata for the successful run.

Suppose:

```text
gold.daily_revenue
→ run completed

silver.orders
→ 18% lower row count

raw.orders
→ input volume also 18% lower

API
→ incomplete response
```

Now inspect data quality:

```text
raw.orders
quality = FAIL
```

The lineage graph shows which downstream datasets may have inherited the bad input.

Next, perform impact analysis:

```text
raw.orders
   ↓
silver.orders
   ↓
gold.daily_revenue
   ├── Finance Dashboard
   ├── Revenue Report
   └── Revenue ML feature pipeline
```

The incident may therefore be systemic across multiple consumers.

The important lesson:

```text
Pipeline SUCCESS
≠
Data Product HEALTHY
```

Lineage reduced the investigation scope from the entire platform to a small upstream dependency chain.

---

# 51. Second Production Challenge — Safe Schema Change

## Scenario

> The platform team wants to change the type of `customer_id` in `raw.customers`.

Question:

> **Can we safely make this change?**

Use:

```text
Lineage discovery
      ↓
Downstream impact analysis
      ↓
Column-level dependency analysis
      ↓
Consumer identification
      ↓
Migration plan
      ↓
Validation
      ↓
Safe deployment
```

## Expert solution

First identify:

```text
raw.customers.customer_id
```

Then traverse downstream.

Example:

```text
raw.customers.customer_id
          ↓
silver.customers.customer_id
          ↓
gold.customer_metrics.customer_id
          ↓
BI
```

Also inspect:

```text
ML feature pipelines
ad-hoc consumers
notebooks
external exports
```

Then classify each dependency:

```text
Compatible
Needs migration
Unknown
```

Only after all important consumers are understood should the schema migration proceed.

Validation should include:

- schema compatibility
- transformed data correctness
- downstream tests
- consumer validation
- lineage verification

---

# 52. Senior Data Engineer Interview Preparation

## Q1. What is data lineage?

**Answer:** Data lineage describes where data originated, how it moved and transformed, and which downstream assets depend on it.

## Q2. Why does lineage matter?

**Answer:** It enables discovery, impact analysis, root-cause analysis, change management, compliance support, and safe deprecation.

## Q3. Table vs column lineage?

**Answer:** Table lineage identifies dataset-to-dataset relationships. Column lineage identifies source-field-to-target-field relationships and enables more precise schema impact analysis.

## Q4. Upstream vs downstream?

**Answer:** Upstream assets provide data to an asset; downstream assets consume or depend on it.

## Q5. Direct vs transitive dependency?

**Answer:** A direct dependency is immediate; a transitive dependency exists through one or more intermediate assets.

## Q6. Design-time vs runtime lineage?

**Answer:** Design-time lineage describes intended relationships inferred from code/configuration; runtime lineage records relationships observed during actual execution.

## Q7. What is OpenLineage?

**Answer:** An open standard for collecting and exchanging lineage metadata/events using concepts such as Jobs, Runs, Datasets, Events, and Facets.

## Q8. What are Job, Run, Dataset, and Event?

**Answer:** Job is logical work, Run is one execution, Dataset is consumed/produced data, and Event describes execution lifecycle and lineage state.

## Q9. Why are START, COMPLETE, and FAIL important?

**Answer:** They represent execution lifecycle and allow lineage consumers to distinguish active, successful, and failed executions.

## Q10. What are facets?

**Answer:** Additional metadata attached to lineage entities/events, such as schema, SQL, data source, column lineage, quality, and custom organizational metadata.

## Q11. Why can column lineage be difficult?

**Answer:** Complex SQL, dynamic SQL, UDFs, stored procedures, temporary objects, runtime-generated datasets, and semantic transformations can make static inference incomplete or ambiguous.

## Q12. What is Marquez?

**Answer:** A practical OpenLineage-compatible lineage backend/UI; it is an implementation, not the OpenLineage standard itself.

## Q13. Why use custom Python emitters?

**Answer:** To capture lineage for custom or unsupported pipelines, external systems, specialized frameworks, and legacy integrations.

## Q14. How would you use lineage for root-cause analysis?

**Answer:** Start at the affected output, traverse upstream dependencies, correlate the relevant runs and quality signals, and investigate the smallest plausible upstream set.

## Q15. How would you use lineage for impact analysis?

**Answer:** Traverse downstream from the changed asset or column, classify direct/transitive consumers, identify owners, and validate migration requirements.

## Q16. Is complete lineage always better?

**Answer:** No. Incorrect lineage can be more dangerous than incomplete lineage. Accuracy and explicit gap visibility are essential.

## Q17. How should lineage be secured?

**Answer:** Apply access control, avoid secrets, sanitize sensitive SQL/metadata, classify sensitive metadata, and apply appropriate retention.

## Q18. How do lineage and data quality work together?

**Answer:** Quality identifies unhealthy data; lineage identifies where that data came from and which downstream assets may be affected.

## Q19. How do lineage and run metadata work together?

**Answer:** Lineage explains relationships while run metadata identifies the specific execution and its operational context.

## Q20. What is a production lineage architecture?

**Answer:** A set of instrumented producers such as Airflow, Spark, dbt, and Python emitting standardized lineage events to a lineage backend, with consistent identity, quality controls, gap management, security, and operational integrations.

---

# 53. Final Assessment

## Basic

1. Define data lineage.
2. Explain upstream and downstream.
3. Define table lineage.
4. Define column lineage.
5. Explain direct vs transitive dependencies.
6. Define design-time lineage.
7. Define runtime lineage.
8. Define OpenLineage.
9. Define Job, Run, Dataset, Event.
10. Explain START/COMPLETE/FAIL.

## Intermediate

1. Build a lineage graph for a three-layer lakehouse.
2. Map a SQL projection to column lineage.
3. Identify direct and transitive downstream dependencies.
4. Explain why a dataset cannot safely be deprecated without impact analysis.
5. Explain the purpose of facets.
6. Design consistent namespaces and names.
7. Explain how runtime lineage differs from dbt design-time metadata.
8. Identify likely lineage gaps in a Python pipeline.
9. Explain how Marquez fits into the architecture.
10. Connect lineage with quality metadata.

## Advanced

1. Design custom Python lineage instrumentation.
2. Design Airflow integration boundaries.
3. Design Spark lineage capture.
4. Design dbt + OpenLineage integration.
5. Analyze column lineage for joins and aggregations.
6. Identify SQL parsing limitations.
7. Design lineage tests.
8. Design lineage coverage metrics.
9. Design gap-management strategy.
10. Design lineage metadata security controls.

## Senior / Production

1. Design lineage architecture across Airflow, Spark, dbt, and Python.
2. Design namespace standards.
3. Define lineage correctness and completeness metrics.
4. Design impact analysis for a breaking schema change.
5. Design a safe dataset deprecation process.
6. Design root-cause analysis using lineage + quality + run metadata.
7. Decide when manual lineage is justified.
8. Design external-system lineage.
9. Handle incomplete column lineage.
10. Explain the trade-off between complete-looking and trustworthy lineage.

---

# 54. Final Learning Checklist

```text
[ ] Explain data lineage
[ ] Explain why lineage matters
[ ] Explain upstream/downstream
[ ] Explain dependency graphs
[ ] Explain direct/transitive dependencies
[ ] Explain table-level lineage
[ ] Explain column-level lineage
[ ] Explain design-time lineage
[ ] Explain runtime lineage
[ ] Explain OpenLineage
[ ] Explain Jobs
[ ] Explain Runs
[ ] Explain Datasets
[ ] Explain Events
[ ] Explain START
[ ] Explain COMPLETE
[ ] Explain FAIL
[ ] Explain Facets
[ ] Explain Schema facets
[ ] Explain Data Source facets
[ ] Explain SQL facets
[ ] Explain Column Lineage facets
[ ] Explain Data Quality facets
[ ] Explain Custom facets
[ ] Use the OpenLineage Python client
[ ] Build a custom Python lineage emitter
[ ] Understand Airflow integration
[ ] Understand Spark integration
[ ] Understand dbt integration
[ ] Understand Marquez
[ ] Design namespaces and dataset names
[ ] Understand column-lineage limitations
[ ] Understand SQL parsing limitations
[ ] Identify lineage gaps
[ ] Handle external systems
[ ] Connect lineage with run metadata
[ ] Connect lineage with data quality
[ ] Perform root-cause analysis
[ ] Perform impact analysis
[ ] Design dataset deprecation workflow
[ ] Test lineage instrumentation
[ ] Secure lineage metadata
[ ] Perform failure injection
[ ] Design production lineage architecture
```

---

# 55. Roadmap Coverage Audit

## Lineage fundamentals

- [x] Why lineage matters
- [x] Table lineage
- [x] Column lineage
- [x] Impact analysis
- [x] Root-cause analysis
- [x] Compliance
- [x] Deprecation

## Lineage types

- [x] Design-time
- [x] Runtime

## OpenLineage

- [x] Jobs
- [x] Runs
- [x] Datasets
- [x] Events
- [x] START
- [x] COMPLETE
- [x] FAIL

## Facets

- [x] Schema
- [x] Data source
- [x] SQL
- [x] Column lineage
- [x] Data quality
- [x] Custom

## Integrations

- [x] Airflow
- [x] Spark
- [x] dbt
- [x] Python

## Backend

- [x] Marquez

## Production concepts

- [x] Namespace/name consistency
- [x] Column lineage
- [x] SQL parsing limitations
- [x] Lineage gaps
- [x] Manual lineage
- [x] Notebooks
- [x] External systems
- [x] Run metadata
- [x] Data quality
- [x] Impact analysis
- [x] Root-cause analysis
- [x] Failure handling
- [x] Lineage quality
- [x] Security

---

# 56. Important Lineage Principle

> **Lineage is only useful when engineers can trust the relationships it represents.**

Therefore distinguish:

```text
Complete lineage
```

from:

```text
Correct lineage
```

A lineage graph containing every dataset but incorrect dependencies is dangerous.

Likewise:

```text
Incomplete but accurate lineage
```

may be safer than:

```text
Complete-looking but incorrect lineage
```

Production systems should make lineage gaps visible.

A trustworthy lineage platform therefore communicates:

```text
What we know
+
What we inferred
+
What we cannot currently observe
```

---

# 57. Master Mental Model

When debugging or changing a data platform, think in this order:

```text
Dataset
   ↓
Who produced it?
   ↓
Which run produced it?
   ↓
Which inputs did that run consume?
   ↓
What transformation occurred?
   ↓
What quality state did the inputs have?
   ↓
Which downstream datasets depend on the result?
   ↓
Which consumers depend on those datasets?
   ↓
What happens if the dataset/schema changes?
```

The OpenLineage model helps standardize the evidence required to answer these questions across heterogeneous data systems.

The final production loop is:

```text
Data System
    ↓
Instrumentation
    ↓
OpenLineage Event
    ↓
Job / Run / Dataset / Facets
    ↓
Lineage Backend
    ↓
Trusted Lineage Graph
    ↓
Impact Analysis / RCA / Governance
    ↓
Safer Data Platform Changes
```

That is the foundation of production-grade data lineage with OpenLineage.
