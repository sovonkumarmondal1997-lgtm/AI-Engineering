# 10 — Databricks SQL, AI/BI Dashboards, and Genie

> **Module:** Gap Module G4 — Databricks Lakehouse Platform Deep Dive  
> **Topic:** 10 — Databricks SQL, AI/BI Dashboards, and Genie  
> **Level:** Beginner → Intermediate → Advanced → Production  
> **Primary discipline:** Analytics engineering, governed BI, semantic modeling, AI-assisted analytics  
> **Prerequisites:** G4 Topics 01–09 and Stage 2 foundations in SQL, Spark, Delta Lake, data modeling, governance, and performance engineering.

> **Current terminology note:** Databricks documentation currently uses **Genie Agents** for the capability historically referred to in this roadmap as **Genie Spaces**. This module retains "Genie space" when discussing the roadmap concept, but uses "Genie Agent" when describing current product terminology.

---

# 1. Module Purpose

Gold data is not the end of a lakehouse. It becomes valuable when people can consume it safely, consistently, and efficiently.

This module takes the learner through:

```text
SQL fundamentals
    ↓
Databricks SQL
    ↓
SQL warehouses
    ↓
Analytical query development
    ↓
Parameters and query operations
    ↓
Gold-layer analytics
    ↓
AI/BI dashboards
    ↓
Alerts
    ↓
Semantic metrics
    ↓
Genie / Genie Agents
    ↓
Governed AI-assisted analytics
    ↓
External BI
    ↓
Federation and caching
    ↓
Performance engineering
    ↓
Production analytics architecture
```

The objective is not to teach a dashboard UI.

The objective is to teach the engineering discipline required to turn governed lakehouse data into **correct, secure, performant, observable, and cost-effective analytical experiences**.

The core question is:

> **How do I take governed gold data in Databricks, expose it through SQL, define reliable business metrics, build performant dashboards and alerts, provide governed natural-language analytics through Genie, and ensure users receive correct answers at an acceptable operational cost?**

---

# 2. Why Topic 10 Follows Topic 09

The G4 progression is deliberate:

```text
Compute
  ↓
Workspace / development
  ↓
Governance
  ↓
Ingestion
  ↓
Declarative pipelines
  ↓
Orchestration
  ↓
Performance
  ↓
Analytics
  ↓
Sharing
```

Topic 09 taught how to reason about:

- Photon;
- query execution;
- table layout;
- liquid clustering;
- predictive optimization;
- performance measurement;
- cost/performance trade-offs.

Topic 10 turns those capabilities into a business-facing serving layer.

```text
Topic 07
Produce reliable data

Topic 08
Orchestrate reliable execution

Topic 09
Make execution efficient

Topic 10
Make the resulting data useful to people
```

---

# 3. Scope Boundary

This module assumes the learner already knows:

- SQL fundamentals;
- Spark/DataFrame fundamentals;
- Delta Lake fundamentals;
- medallion architecture;
- data modeling basics;
- Unity Catalog fundamentals;
- SQL warehouse concepts from G4 Topic 02;
- Lakeflow Declarative Pipelines from Topic 07;
- performance engineering from Topic 09.

This module therefore does **not** re-teach:

- complete SQL syntax from scratch;
- complete Spark internals;
- complete Delta internals;
- complete Unity Catalog;
- complete Lakeflow pipelines;
- complete compute administration.

Instead, it connects those foundations to production analytics.

---

# 4. Learning Objectives

By the end of this topic, you should be able to:

- write production-oriented analytical SQL;
- use the Databricks SQL editor effectively;
- use query history as an operational diagnostic tool;
- design reusable parameterized queries;
- reason about SQL warehouse sizing and concurrency;
- build governed AI/BI dashboards;
- design dashboard datasets around correct analytical grain;
- implement filters and parameters;
- schedule and securely share dashboards;
- build SQL alerts for freshness and business thresholds;
- understand materialized views;
- understand SQL-defined streaming tables;
- distinguish pipeline responsibilities from analytics-serving responsibilities;
- design a semantic layer;
- define governed business metrics;
- understand current Unity Catalog metric views;
- build and evaluate Genie Agents over curated data;
- provide precise instructions and trusted assets;
- evaluate generated SQL rather than trusting it blindly;
- apply row and column security to analytical experiences;
- integrate external BI tools;
- reason about query federation versus ingestion;
- understand caching and warm/cold benchmark effects;
- optimize dashboard performance;
- control analytics cost;
- design production analytics architecture;
- troubleshoot dashboard and Genie incidents;
- document analytics decisions with ADRs;
- build a complete finance analytics platform.

---

# 5. Analytics Architecture

Start with the complete lakehouse picture.

```text
Source Systems
      ↓
   Bronze
      ↓
   Silver
      ↓
    Gold
      ↓
Governed Analytical Tables / Views / Metrics
      ↓
 SQL Warehouse
      ↓
 ┌───────────────┬────────────────┬──────────────────┐
 │               │                │                  │
SQL Users    AI/BI Dashboards   Genie Agent     External BI
 │               │                │                  │
 └───────────────┴────────────────┴──────────────────┘
                       ↓
                Business Decisions
```

The architecture has a critical property:

> **Business-facing analytics should consume governed analytical assets, not arbitrary raw data.**

---

# 6. The Analytics Serving Mental Model

Think in layers.

```text
DATA PRODUCTION
Bronze → Silver → Gold

DATA GOVERNANCE
Unity Catalog
permissions
row filters
column masks
lineage
metric definitions

DATA SERVING
SQL warehouse

DATA CONSUMPTION
SQL
AI/BI
Genie
External BI

BUSINESS OUTCOME
Decision
```

Each layer has a responsibility.

| Layer | Primary responsibility |
|---|---|
| Bronze | Preserve/source-oriented data |
| Silver | Clean and conform |
| Gold | Business-oriented analytical model |
| Unity Catalog | Governance and discovery |
| SQL warehouse | Analytical compute |
| SQL | Deterministic analytical logic |
| Dashboard | Visual consumption |
| Semantic layer | Metric consistency |
| Genie | Governed natural-language exploration |
| External BI | Enterprise consumption outside native UI |
| Monitoring | Detect operational failure |

---

# 7. Analytical Data Model Foundation

Do not build analytics directly on an undefined grain.

## 7.1 Fact tables

A fact table records measurable business events.

Example:

```text
gold.orders
```

Possible columns:

```text
order_id
customer_id
product_id
order_date
quantity
gross_revenue
discount
net_revenue
region
```

## 7.2 Dimension tables

Dimensions provide descriptive context.

Examples:

```text
gold.customers
gold.products
gold.regions
```

## 7.3 Grain

Grain answers:

> **What does one row represent?**

For `gold.orders`:

```text
one row = one order
```

If you join it to a table containing multiple rows per order without controlling cardinality, revenue can be multiplied.

---

# 8. Metric Correctness Starts With Grain

Suppose:

```sql
SELECT
    customer_id,
    SUM(net_revenue) AS revenue
FROM gold.orders
GROUP BY customer_id;
```

This is meaningful if:

```text
gold.orders
grain = one row per order
net_revenue = order-level amount
```

Now imagine:

```text
orders
  1 row/order

order_items
  many rows/order
```

An unsafe join:

```sql
SELECT
    SUM(o.net_revenue)
FROM gold.orders o
JOIN gold.order_items i
  ON o.order_id = i.order_id;
```

can multiply `o.net_revenue`.

Correct analytics engineering requires:

```text
Understand grain
    ↓
Understand cardinality
    ↓
Join intentionally
    ↓
Validate totals
```

---

# 9. Gold Analytics Model

A useful finance model might contain:

```text
gold.orders
gold.customers
gold.products
gold.daily_revenue
gold.daily_product_sales
gold.customer_revenue
```

The gold layer should make common business questions easier to answer.

Examples:

```text
How much revenue did we generate yesterday?
Which products generated the most revenue?
What is AOV?
Which region is declining?
How many active customers do we have?
```

A good gold model reduces repeated complex logic in every dashboard.

---

# 10. Databricks SQL

Databricks SQL provides the SQL-oriented analytical interface to the lakehouse.

Current Databricks documentation describes core interfaces including:

- SQL editor;
- SQL warehouses;
- AI/BI;
- metric views;
- alerts;
- jobs;
- query history and query profiles.

The engineering mental model is:

```text
Lakehouse
    ↓
Unity Catalog
    ↓
SQL warehouse
    ↓
Databricks SQL
    ↓
Queries / dashboards / alerts / semantic analytics
```

Databricks SQL is not a separate data universe from Spark and Delta.

It is a managed analytical interface and execution environment over the lakehouse.

---

# 11. Databricks SQL vs Traditional Database SQL

Traditional database:

```text
Application
   ↓
Database
   ↓
SQL
```

Lakehouse analytics:

```text
Files / Delta / external sources
          ↓
Unity Catalog
          ↓
SQL warehouse / Spark-based compute
          ↓
SQL
```

The SQL language remains familiar, but the operating model changes.

The engineer must reason about:

- distributed execution;
- data volume;
- table layout;
- warehouse concurrency;
- caching;
- governance;
- cost;
- semantic consistency.

---

# 12. SQL Editor

The SQL editor is the analyst's primary interactive SQL environment.

Core workflow:

```text
Choose catalog/schema
        ↓
Write SQL
        ↓
Run
        ↓
Inspect results
        ↓
Profile
        ↓
Save/share
        ↓
Turn into dashboard/alert when appropriate
```

Example:

```sql
SELECT
    order_date,
    SUM(net_revenue) AS daily_revenue
FROM gold.orders
WHERE order_date >= current_date() - INTERVAL 30 DAYS
GROUP BY order_date
ORDER BY order_date;
```

### Read it carefully

```sql
SELECT
    order_date,
    SUM(net_revenue) AS daily_revenue
```

defines the result.

```sql
FROM gold.orders
```

identifies the analytical source.

```sql
WHERE order_date >= current_date() - INTERVAL 30 DAYS
```

limits the time window.

```sql
GROUP BY order_date
```

defines daily grain.

```sql
ORDER BY order_date
```

sorts the result.

---

# 13. Query History

Query history is not merely a record of old queries.

It is an operational diagnostic tool.

Use it to investigate:

```text
"The dashboard is slow."
```

by decomposing the problem:

```text
Which dashboard?
      ↓
Which dataset?
      ↓
Which query?
      ↓
Which warehouse?
      ↓
When did latency change?
      ↓
How much data was processed?
      ↓
Was concurrency high?
      ↓
What changed?
```

Useful investigation dimensions include:

- execution duration;
- failures;
- workload frequency;
- warehouse;
- user/service identity;
- query text;
- query profile;
- resource usage where exposed by the platform.

---

# 14. Query Reproducibility

A production analytical query should be reproducible.

Capture:

```text
Query text
Source objects
Parameters
Warehouse
Time window
Expected result
Metric definition
Owner
Purpose
```

Avoid dashboards containing undocumented business logic that cannot be reproduced elsewhere.

---

# 15. Parameterized Queries

Parameters allow one analytical query to serve multiple user selections.

Hard-coded:

```sql
SELECT
    SUM(net_revenue) AS revenue
FROM gold.orders
WHERE order_date >= '2026-01-01'
  AND region = 'North';
```

Reusable design:

```text
date parameter
+
region parameter
+
same analytical query
```

The exact parameter syntax varies by Databricks interface and should be verified against the current SQL editor/dashboard documentation before production implementation.

---

# 16. Why Parameterization Matters

Without parameters:

```text
Query 1 → North
Query 2 → South
Query 3 → East
Query 4 → West
```

With a reusable parameterized design:

```text
One query
    ↓
runtime selections
    ↓
different analytical slices
```

Benefits:

- reuse;
- maintainability;
- dashboard integration;
- consistent business logic;
- fewer duplicated queries.

Parameterization is not itself a substitute for access control or authorization.

---

# 17. Dashboard Parameters

Current AI/BI dashboard documentation supports parameters that can substitute values into dataset queries at runtime. Parameters can be connected to filter widgets and can influence the query before aggregation, which can improve analytical efficiency for appropriate workloads.

Conceptually:

```text
Viewer selects:
Region = North
Date = Last 30 Days
       ↓
Dashboard parameter
       ↓
Dataset query
       ↓
Filtered result
       ↓
Visualization
```

This differs from simply filtering an already-returned dataset in the browser.

Use the current Databricks dashboard documentation for exact UI and parameter syntax.

---

# 18. SQL Warehouse Fundamentals

A SQL warehouse is the serving compute layer for SQL analytics.

Think:

```text
Query
 ↓
SQL warehouse
 ↓
Compute
 ↓
Lakehouse data
```

Warehouse sizing is a capacity decision.

Do not memorize:

```text
"Finance = X warehouse size."
```

Instead reason:

```text
Data volume
+
Query complexity
+
Concurrency
+
Latency SLO
+
Peak traffic
+
Cost budget
=
Warehouse decision
```

---

# 19. SQL Warehouse Sizing

### Small workload

```text
few users
small data
low concurrency
```

May need relatively little capacity.

### High-concurrency workload

```text
many users
dashboard bursts
ad hoc analysts
scheduled refreshes
```

May require more capacity, workload isolation, or a different serving architecture.

### Core principle

> **Size for the workload and SLO, not the job title of the users.**

---

# 20. Concurrency

Consider:

```text
08:00
5 analysts
    ↓
10 queries

09:00
100 dashboard users
    ↓
20+ dashboard query executions
    ↓
ad hoc analyst traffic
    ↓
scheduled jobs
```

A warehouse that is fast for one query can still be overloaded under concurrency.

Investigate:

- queueing;
- concurrent queries;
- query duration;
- warehouse capacity;
- dashboard refresh schedules;
- workload isolation.

---

# 21. Auto-Stop and Idle Capacity

An always-running warehouse can create unnecessary cost.

An auto-stop policy can reduce idle consumption.

But aggressive stopping can introduce:

- startup latency;
- poor interactive experience;
- unpredictable user perception.

The correct balance depends on workload.

---

# 22. Serverless SQL Warehouses

Serverless SQL can abstract more infrastructure management and can be useful for variable analytical workloads.

Do not treat serverless as:

> "Always cheaper."

Cost depends on:

- workload;
- concurrency;
- runtime;
- usage pattern;
- current pricing;
- capacity behavior.

Verify current availability, limitations, and pricing in the target cloud/environment.

---

# 23. AI/BI Dashboards

Current Databricks documentation describes AI/BI dashboards as a business-intelligence experience with datasets, visualizations, filters, sharing, scheduling, and AI-assisted authoring.

The engineering model is:

```text
Dataset
   ↓
Visualization
   ↓
Page
   ↓
Dashboard
   ↓
Published analytical experience
```

A dashboard is therefore an **application-like analytical surface**, not just a collection of charts.

---

# 24. Dashboard Datasets

A dashboard dataset supplies data to one or more visualizations.

Current dashboard datasets can be based on:

- Unity Catalog tables;
- views;
- metric views;
- SQL queries;
- supported dashboard-local modeling constructs.

A good dataset should have:

- clear grain;
- explicit metric definitions;
- limited unnecessary columns;
- predictable joins;
- appropriate filters;
- reusable analytical logic.

---

# 25. Dashboard Dataset Design

Bad:

```text
dashboard
  ↓
raw bronze table
  ↓
complex joins
  ↓
business calculations
  ↓
chart
```

Better:

```text
bronze
  ↓
silver
  ↓
gold analytical model
  ↓
semantic metrics
  ↓
dashboard dataset
  ↓
visualization
```

This improves:

- correctness;
- reuse;
- governance;
- performance;
- maintainability.

---

# 26. AI/BI Visualizations

Visualization selection should follow the business question.

| Question | Suitable visual |
|---|---|
| Trend over time | Line chart |
| Compare categories | Bar chart |
| KPI | Single-value KPI |
| Distribution | Histogram |
| Geographic pattern | Map where appropriate |
| Contribution | Bar / stacked chart |
| Detail investigation | Table |
| Relationship | Scatter plot |

Do not use visual complexity as a substitute for analytical clarity.

---

# 27. Dashboard Filters

Current AI/BI dashboards support multiple filter types and scopes, including:

- multiple values;
- single value;
- date picker;
- date range;
- text entry;
- range slider.

Filters can operate at global, page, or widget/dataset-related scopes depending on configuration.

The performance question is:

> **Does the filter reduce work early enough to matter?**

---

# 28. Filter Correctness

A filter can be technically valid but semantically wrong.

Example:

```text
Dashboard:
Revenue by Region

Filter:
Region = "North"
```

If the filter applies only to one chart while users assume it applies to all charts, the dashboard becomes misleading.

Always test:

```text
Filter scope
+
Dataset mapping
+
Metric result
+
User expectation
```

---

# 29. Finance Dashboard

Build a finance dashboard around:

```text
Revenue
Net Revenue
Orders
Customers
AOV
Conversion Rate
Daily Revenue
MTD Revenue
YTD Revenue
Top Products
Top Regions
```

Example:

```sql
SELECT
    order_date,
    SUM(net_revenue) AS net_revenue,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT customer_id) AS customers,
    SUM(net_revenue)
      / NULLIF(COUNT(DISTINCT order_id), 0) AS aov
FROM gold.orders
GROUP BY order_date
ORDER BY order_date;
```

---

# 30. Metric Definition Review

Before putting this on a dashboard, define:

```text
Net Revenue
= SUM(order.net_revenue)

Orders
= COUNT(DISTINCT order_id)

Customers
= COUNT(DISTINCT customer_id)

AOV
= Net Revenue / Orders
```

Then define:

```text
What date?
What grain?
What exclusions?
What currency?
What null behavior?
What refunds?
What late-arriving data?
```

A metric is not complete merely because SQL can calculate it.

---

# 31. Dashboard Scheduling

Scheduling can:

- refresh dashboard datasets;
- keep published information current;
- populate/cache results for appropriate dashboard configurations;
- send subscriptions depending on current capabilities and configuration.

Current documentation supports scheduled dashboard updates and subscriptions to supported destinations.

Operational questions:

- How fresh must the dashboard be?
- When should refresh occur?
- Does refresh overlap with ingestion?
- Does refresh create a concurrency spike?
- Who owns failed schedules?

---

# 32. Dashboard Sharing

Publishing and sharing must be governed.

Consider:

```text
Audience
  ↓
Identity
  ↓
Entitlement
  ↓
Dashboard permissions
  ↓
Data permissions
  ↓
Row/column controls
```

A published dashboard should never become a mechanism for bypassing Unity Catalog governance.

Current Databricks documentation supports dashboard sharing with different permission/data-permission models and consumer access patterns.

---

# 33. SQL Alerts

Current Databricks SQL alerts run queries on a schedule and evaluate a condition against query results.

Use alerts for:

- KPI thresholds;
- freshness;
- operational checks;
- data quality signals;
- cost indicators;
- governed metric monitoring.

An alert is:

```text
Query
  ↓
Schedule
  ↓
Condition
  ↓
Evaluation
  ↓
Notification
```

---

# 34. Important Alert Limitation

Current Databricks documentation states that the standard SQL alert workflow does **not support queries with parameters**.

Therefore:

```text
Parameterized dashboard query
```

and

```text
Alert query
```

must not be assumed to be interchangeable.

Design alert SQL specifically for alert execution.

---

# 35. Freshness Alert

Business requirement:

> Alert if `gold.daily_revenue` is more than two hours behind the expected freshness target.

Conceptual query:

```sql
SELECT
    MAX(updated_at) AS latest_update
FROM gold.daily_revenue;
```

Then evaluate:

```text
current time - latest_update > allowed delay
```

But production design must account for:

- timezone;
- business hours;
- weekends;
- holidays;
- ingestion delays;
- late-arriving data;
- upstream outages.

---

# 36. Revenue Drop Alert

Requirement:

> Alert when daily revenue falls more than 30% day over day.

A robust conceptual query:

```sql
WITH daily AS (
    SELECT
        order_date,
        SUM(net_revenue) AS revenue
    FROM gold.orders
    GROUP BY order_date
),
comparison AS (
    SELECT
        order_date,
        revenue,
        LAG(revenue) OVER (ORDER BY order_date) AS previous_revenue
    FROM daily
)
SELECT
    order_date,
    revenue,
    previous_revenue,
    (revenue - previous_revenue)
      / NULLIF(previous_revenue, 0) AS pct_change
FROM comparison
WHERE order_date = current_date() - INTERVAL 1 DAY;
```

Then configure the alert around the returned result.

---

# 37. Alert False Positives

A 35% decline may be legitimate.

Possible reasons:

- public holiday;
- promotion ended;
- planned outage;
- seasonality;
- late-arriving data;
- source-system delay.

Therefore:

```text
Threshold
+
Business context
+
Freshness validation
+
Alert ownership
=
Useful alert
```

---

# 38. Materialized Views

A materialized view precomputes and stores query results.

Compare:

```text
View
=
query logic evaluated when queried
```

with:

```text
Materialized view
=
stored result maintained/refreshed by the platform
```

Benefits:

- repeated expensive queries can become faster;
- complex joins/aggregations can be reused;
- dashboard latency may improve.

Costs:

- storage;
- refresh compute;
- freshness considerations;
- maintenance;
- dependency management.

---

# 39. When to Use Materialization

Good candidate:

```text
same expensive aggregation
+
many readers
+
predictable refresh requirement
```

Poor candidate:

```text
rarely queried
+
cheap query
+
extremely high freshness requirement
+
materialization overhead not justified
```

Always benchmark.

---

# 40. Streaming Tables

Streaming tables represent a streaming-oriented managed table pattern in the Databricks declarative pipeline ecosystem.

Conceptually:

```text
Source
  ↓
Streaming semantics
  ↓
Streaming table
  ↓
Downstream analytical consumers
```

Current Lakeflow SQL supports constructs for materialized views and streaming tables.

Example from current documentation:

```sql
CREATE OR REFRESH STREAMING TABLE basic_st
AS
SELECT *
FROM STREAM samples.nyctaxi.trips;
```

Exact source suitability and change-handling behavior must be verified for the current pipeline/runtime.

---

# 41. Materialized View vs Streaming Table

| Dimension | Materialized View | Streaming Table |
|---|---|---|
| Primary semantics | Batch-oriented refresh | Streaming/incremental |
| Typical use | Derived analytical result | Incremental streaming data |
| Freshness | Refresh-driven | Continuous/incremental pattern |
| Best for | Reusable aggregations | Streaming ingestion/transformation |
| Operating model | Declarative | Declarative |

Do not choose based on terminology alone.

Choose based on:

```text
Source semantics
+
Freshness requirement
+
Transformation
+
Update behavior
+
Operational cost
```

---

# 42. SQL + Lakeflow Declarative Pipelines

The boundary:

```text
Lakeflow pipelines
=
WHAT data should be produced

Databricks SQL analytics
=
HOW users query and consume produced data
```

Pipeline:

```text
Source
 ↓
Transform
 ↓
Streaming table / materialized view / gold table
```

Analytics:

```text
Gold / semantic layer
 ↓
SQL
 ↓
Dashboard / alert / Genie
```

Some SQL-defined datasets can bridge these layers.

---

# 43. Standalone vs Pipeline-Managed Datasets

Current Databricks documentation describes both:

- standalone materialized views/streaming tables;
- Lakeflow pipeline-managed datasets.

A standalone object can have a managed pipeline behind it.

A full Lakeflow pipeline is an authored operational unit that can contain multiple datasets and dependency relationships.

The engineering question is:

> **Do I need one managed analytical dataset, or a complete governed dataflow with multiple dependent datasets and pipeline-level operations?**

---

# 44. Semantic Layer

A semantic layer gives business meaning to data.

Without it:

```text
Dashboard A:
Net Revenue = definition A

Dashboard B:
Net Revenue = definition B

Analyst C:
Net Revenue = definition C
```

With a governed semantic layer:

```text
Net Revenue
     ↓
one governed definition
     ↓
multiple consumers
```

This is a correctness mechanism, not merely documentation.

---

# 45. Metric Views

Current Databricks documentation describes **metric views** as a semantic layer for standardized business metrics.

Metric views can model:

- sources;
- joins;
- filters;
- fields/dimensions;
- measures;
- additional semantic metadata.

They are intended to make KPI calculations consistent across analytical consumers.

Exact feature availability and runtime/version requirements must be checked in the target environment.

---

# 46. Local vs Governed Metrics

Current AI/BI dashboard capabilities also support local metric views for logic that is useful within a specific dashboard but not yet ready for broad governance.

Mental model:

```text
Experiment
   ↓
Local metric logic
   ↓
Validate
   ↓
Harden
   ↓
Governed Unity Catalog metric view
   ↓
Reuse across consumers
```

This creates a useful promotion path.

---

# 47. Certified Metrics

Example:

```text
Metric:
Net Revenue

Definition:
SUM(net_revenue)
```

Another:

```text
Metric:
AOV

Definition:
Net Revenue / Distinct Orders
```

Certification should include:

- business owner;
- technical owner;
- definition;
- grain;
- exclusions;
- time semantics;
- currency;
- tests;
- governance;
- change process.

---

# 48. Metric Governance

A metric definition should answer:

```text
What does it mean?
Who owns it?
What tables feed it?
What grain is used?
What filters apply?
How is it calculated?
What security applies?
How is it tested?
Where is it consumed?
```

A metric that cannot answer these questions is not production-grade.

---

# 49. Genie — Current Terminology

The roadmap calls the feature **Genie spaces**.

Current Databricks documentation uses **Genie Agents**.

A Genie Agent is a domain-specific natural-language interface where users ask questions about governed data and can receive:

- generated SQL;
- result tables;
- visualizations;
- follow-up interactions.

The quality depends heavily on the analytical context curated by data/analytics experts.

---

# 50. Genie Mental Model

```text
Business Question
       ↓
Genie Agent
       ↓
Intent interpretation
       ↓
Relevant governed context
       ↓
Generated SQL
       ↓
SQL execution
       ↓
Result
       ↓
Business answer
```

The dangerous misconception is:

```text
User
 ↓
AI
 ↓
raw lakehouse
 ↓
trust
```

The production pattern is:

```text
Governed data
 ↓
Curated analytical model
 ↓
Certified metrics
 ↓
Genie context
 ↓
Evaluation
 ↓
Business user
```

---

# 51. Genie Agent Data Sources

Current Databricks documentation states that Genie Agents use Unity Catalog-governed data assets and can be configured with curated datasets, example SQL, instructions, and trusted assets.

The important design principle is:

> **Give Genie the smallest high-quality analytical surface that can answer the intended business questions.**

Avoid exposing irrelevant or ambiguous tables.

---

# 52. Genie Agent Curation

A high-quality Genie Agent should have:

```text
Curated tables
+
Clear column names
+
Descriptions
+
Business terminology
+
Example SQL
+
Metric definitions
+
Instructions
+
Security
+
Evaluation questions
```

This is analogous to prompt/context engineering for an AI system.

---

# 53. Genie Instructions

Bad:

```text
Answer finance questions.
```

Better:

```text
Use gold.finance_orders for finance revenue questions.

Net revenue means SUM(net_revenue).

Do not use gross_revenue when the user asks for net revenue.

Revenue is reported in USD.

Use order_date for daily revenue unless the user explicitly requests
another business date.

If the question cannot be answered from the curated assets,
state that the available data is insufficient rather than guessing.
```

Instructions reduce ambiguity.

They do not guarantee correctness.

---

# 54. Trusted Assets

Trusted assets provide examples and authoritative analytical context.

Examples:

```text
Example query:
"Show monthly net revenue."

Trusted metric:
Net Revenue.

Trusted table:
gold.finance_orders.

Trusted relationship:
orders.customer_id → customers.customer_id.
```

The objective is to guide the system toward known-good analytical patterns.

---

# 55. Genie Evaluation

Natural-language analytics must be evaluated like any production AI-assisted system.

Create 20 business questions.

Include:

1. simple lookup;
2. aggregation;
3. time comparison;
4. ranking;
5. filtering;
6. ambiguous terminology;
7. metric question;
8. security-sensitive question;
9. multi-table join;
10. unavailable-data question;
11. date-range question;
12. top-N question;
13. percentage-change question;
14. regional question;
15. product question;
16. customer question;
17. null-data question;
18. business-calendar question;
19. intentionally ambiguous question;
20. question with no valid answer.

---

# 56. Genie Evaluation Record

For every question record:

```text
Question
Expected answer
Expected SQL logic
Generated answer
Generated SQL
Correct?
Why?
Failure mode
Fix
Retest result
```

This creates an evaluation dataset.

Do not say:

> "Genie seems accurate."

Say:

> "Genie answered 18/20 test cases correctly; the two failures involved metric ambiguity and an unsupported date interpretation."

---

# 57. Genie Evaluation Metrics

Use a scorecard:

| Dimension | Score |
|---|---:|
| Intent understanding | /5 |
| SQL correctness | /5 |
| Metric correctness | /5 |
| Filter correctness | /5 |
| Join correctness | /5 |
| Security compliance | /5 |
| Answer clarity | /5 |
| Performance | /5 |

Track failures by category.

Example:

```text
Metric errors: 2
Join errors: 1
Date errors: 1
Security errors: 0
```

This is much more useful than one overall subjective score.

---

# 58. Generated SQL Review

Always inspect generated SQL for high-impact analytical use cases.

Check:

```text
FROM
JOIN
WHERE
GROUP BY
aggregation
date logic
metric definition
security
```

The fundamental equation is:

```text
Correct English
+
Incorrect SQL
=
Incorrect business decision
```

Natural-language fluency is not proof of analytical correctness.

---

# 59. Governed AI-Assisted Analytics

Production architecture:

```text
Raw Data
   ↓
Governance
   ↓
Curated Gold
   ↓
Certified Metrics
   ↓
Genie
   ↓
Business User
```

Controls include:

- Unity Catalog;
- row filters;
- column masks;
- least privilege;
- curated tables;
- metric definitions;
- trusted assets;
- generated SQL review;
- auditability.

---

# 60. Why Governance Comes Before AI

Bad architecture:

```text
Raw sensitive data
      ↓
AI assistant
      ↓
"Please answer anything"
```

Better:

```text
Sensitive data
      ↓
Unity Catalog governance
      ↓
Curated analytical model
      ↓
Approved metrics
      ↓
AI-assisted analytics
```

The AI layer should not become a governance bypass.

---

# 61. Row-Level Security

Example:

```text
Finance user
→ finance rows

Regional manager
→ assigned region

Executive
→ approved enterprise-level information
```

Row-level policies should be enforced by the governed data layer rather than relying only on dashboard filters.

A dashboard filter is a user-interface behavior.

A row-level security policy is an authorization control.

They are not equivalent.

---

# 62. Column-Level Security

Sensitive fields may require masking or restricted access.

Examples:

```text
email
phone
salary
bank_account
customer_pii
```

A production analytical design asks:

```text
Who can query the column?
Who can see the raw value?
Who can see masked value?
Does the same policy apply through dashboards?
Does the same policy apply through Genie?
```

---

# 63. Security Validation Across Interfaces

Required validation:

```text
SQL query
    ↓
correct row/column visibility?

Dashboard
    ↓
same security?

Genie
    ↓
same security?

External BI
    ↓
same security?
```

Never assume:

> "The dashboard is secure, therefore everything downstream is secure."

Test the actual data path.

---

# 64. External BI

External BI tools can consume Databricks SQL warehouses.

Architecture:

```text
External BI
      ↓
SQL warehouse
      ↓
Unity Catalog
      ↓
Gold / semantic layer
```

Typical concerns:

- authentication;
- authorization;
- concurrency;
- caching;
- query generation;
- workload isolation;
- data freshness;
- cost;
- governance.

Do not turn this module into vendor-specific training.

The important engineering problem is the serving contract.

---

# 65. External BI Serving Contract

Define:

```text
Data source
Metric definitions
Security model
Freshness SLA
Latency SLO
Concurrency expectation
Cost owner
Failure behavior
Change-management process
```

This prevents BI tools from becoming uncontrolled consumers.

---

# 66. Query Federation

Query federation allows Databricks to query supported external systems without first ingesting the data into Databricks storage.

Conceptually:

```text
Databricks SQL
     ↓
Unity Catalog foreign catalog
     ↓
External database
```

Current Databricks documentation describes query federation as using pushdown to supported external relational systems and governed access through Unity Catalog.

---

# 67. Federation vs Ingestion

| Scenario | Federation | Ingest |
|---|---|---|
| Small ad hoc analysis | Strong candidate | Usually unnecessary |
| Proof of concept | Strong candidate | Maybe |
| Repeated high-volume analytics | Often weaker | Strong candidate |
| Lowest source latency impact | Depends | Strong after ingestion |
| Source system protection | Can be a concern | Better after decoupling |
| Need historical analytical storage | Weak | Strong |
| Heavy transformations | Weak | Strong |
| Live source access | Strong | Requires ingestion freshness |
| Governance | Unity Catalog can govern foreign objects | Unity Catalog governs ingested data |

Current Databricks guidance favors managed ingestion for high-volume, lower-latency recurring workloads when supported, while federation is useful for ad hoc/reporting and migration scenarios.

---

# 68. Federation Decision Framework

Choose federation when:

```text
data volume manageable
+
query frequency manageable
+
source can tolerate workload
+
fresh/live access valuable
+
avoiding ingestion is useful
```

Choose ingestion when:

```text
high repeated volume
+
predictable analytical workloads
+
source-system protection
+
complex transformations
+
historical storage
+
low analytical latency
```

---

# 69. Caching

Caching can make repeated analytical workloads faster, but cache state changes benchmark results.

Mental model:

```text
First execution
    ↓
cold path

Repeated execution
    ↓
potentially warm/cached path
```

Therefore a fair benchmark should document:

```text
cold/warm state
query repetition
cache behavior
data changes
warehouse state
```

Never claim a fixed cache retention period without verifying the current platform documentation.

---

# 70. Dashboard Performance Engineering

A useful dashboard performance model:

```text
Good data model
+
Good SQL
+
Good physical layout
+
Efficient execution
+
Appropriate warehouse
+
Appropriate caching/materialization
+
Controlled concurrency
=
Good dashboard performance
```

No single feature guarantees performance.

---

# 71. Pre-Aggregated Gold Tables

Suppose a dashboard repeatedly calculates:

```sql
SELECT
    order_date,
    region,
    product_id,
    SUM(net_revenue)
FROM gold.orders
GROUP BY
    order_date,
    region,
    product_id;
```

If this is repeated at high frequency, consider an appropriate pre-aggregated gold table.

Benefits:

- lower query work;
- faster dashboards;
- predictable performance.

Trade-offs:

- storage;
- refresh cost;
- freshness;
- pipeline complexity;
- additional objects.

---

# 72. Materialization vs Pre-Aggregation

These are related but not identical.

```text
Materialized view
=
platform-maintained stored query result
```

```text
Pre-aggregated gold table
=
explicit analytical data product designed for reuse
```

Choose based on ownership and operational needs.

---

# 73. Dashboard Materialization

Current Databricks documentation describes dashboard dataset materialization as a Beta capability in which expensive dataset results can be precomputed and stored, reducing repeated execution of expensive joins/scans.

Treat Beta/preview features as environment-dependent.

Before production adoption verify:

- current availability;
- enablement;
- limitations;
- refresh semantics;
- cost;
- governance;
- operational behavior.

---

# 74. Dashboard Performance Failure Scenario

Scenario:

> The CFO dashboard takes 45 seconds to load.

Investigate in order:

```text
1. Query history
2. Underlying dataset queries
3. SQL warehouse
4. Concurrency
5. Data scanned
6. Joins
7. Aggregations
8. Physical layout
9. Materialization
10. Caching
11. Recent changes
```

Do not start by doubling the warehouse.

---

# 75. Business Metric Correctness

A fast dashboard can still be wrong.

Common causes:

- duplicate joins;
- wrong grain;
- missing records;
- late-arriving data;
- timezone errors;
- null handling;
- divide-by-zero;
- incorrect date windows;
- metric drift;
- inconsistent currency;
- refund treatment differences.

Correctness comes before performance.

---

# 76. Analytics Data Quality

Useful checks:

```text
Revenue reconciles to source
Orders count is plausible
Order IDs are unique where expected
No impossible dates
Expected null constraints hold
Metric totals reconcile
Currency is correct
Freshness is within SLA
```

A dashboard should not become the first place where data quality is discovered.

---

# 77. Production Analytics Architecture

Reference architecture:

```text
                 ┌──────────────────┐
                 │   Source Systems │
                 └────────┬─────────┘
                          ↓
                   Bronze / Silver
                          ↓
                     Gold Layer
                          ↓
              ┌──────────────────────┐
              │   Unity Catalog      │
              │ Governance + Metrics │
              └──────────┬───────────┘
                         ↓
                   SQL Warehouse
                         ↓
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
    SQL Users        AI/BI Dashboard     Genie
       ↓                 ↓                 ↓
       └─────────────────┼─────────────────┘
                         ↓
                  Business Decisions
```

Add:

```text
External BI
Federation
Alerts
Monitoring
Audit
Cost Management
```

---

# 78. Security Architecture

```text
Identity
   ↓
Unity Catalog
   ↓
Catalog / Schema / Object privileges
   ↓
Row filters / Column masks
   ↓
Semantic metrics
   ↓
SQL / Dashboard / Genie / External BI
```

Security should be enforced at the governed data layer wherever possible.

---

# 79. Cost Engineering

Analytics cost is driven by:

- warehouse size;
- runtime;
- concurrency;
- repeated queries;
- dashboard refresh;
- materialization;
- cache behavior;
- query inefficiency;
- idle capacity;
- workload isolation;
- serverless consumption.

Use:

```text
Cost per query
Cost per dashboard refresh
Cost per active user
Cost per business KPI
```

where practical.

Do not use fabricated prices.

Verify current Databricks and cloud pricing before making production decisions.

---

# 80. Cost Optimization Decision Tree

```text
Analytics expensive?
      ↓
Is query doing unnecessary work?
      ├─ Yes → optimize query/data model
      └─ No
          ↓
Is dashboard repeating expensive work?
      ├─ Yes → reuse/materialize/pre-aggregate where justified
      └─ No
          ↓
Is concurrency causing oversized compute?
      ├─ Yes → workload isolation/capacity analysis
      └─ No
          ↓
Is idle capacity high?
      ├─ Yes → auto-stop/lifecycle review
      └─ No
          ↓
Is latency SLO driving cost?
      ├─ Yes → evaluate business trade-off
      └─ No
          ↓
Continue workload-level investigation
```

---

# 81. Hands-On Labs

Every lab uses:

```text
Objective
Prerequisites
Setup
Dataset
SQL / configuration
Expected behavior
Measurements
Questions
Troubleshooting
Cleanup
Production lesson
```

---

## Lab 1 — First Databricks SQL Query

### Objective

Query a governed gold table.

### Query

```sql
SELECT
    order_date,
    SUM(net_revenue) AS daily_revenue
FROM gold.orders
GROUP BY order_date
ORDER BY order_date;
```

### Questions

1. What is the grain?
2. What does each output row represent?
3. Is `net_revenue` already at order grain?
4. What happens if it is not?

### Production lesson

Never assume metric correctness from SQL syntax.

---

## Lab 2 — Parameterized Analytical Queries

Build reusable queries for:

```text
date
region
product
```

Measure:

- reuse;
- correctness;
- filter behavior;
- query execution.

### Production lesson

Parameterization reduces duplication but does not replace authorization.

---

## Lab 3 — Query History Investigation

Run several queries.

Then investigate:

```text
Which query was slow?
Which warehouse ran it?
When did it run?
Did it fail?
What changed?
```

### Production lesson

Query history is part of the operational toolkit.

---

## Lab 4 — SQL Warehouse Workload

Create a workload that includes:

- one simple query;
- several concurrent queries;
- one expensive query.

Observe:

- runtime;
- concurrency;
- queueing where exposed;
- warehouse behavior.

### Production lesson

Performance must be evaluated under realistic workload conditions.

---

## Lab 5 — Finance Dashboard

Build:

- revenue;
- orders;
- customers;
- AOV;
- regional revenue;
- product revenue.

Use curated gold data.

### Production lesson

A dashboard is a data product.

---

## Lab 6 — Dashboard Filters

Add:

- date range;
- region;
- product.

Test:

```text
filter scope
filter correctness
query behavior
user experience
```

---

## Lab 7 — Scheduling and Sharing

Create a realistic executive/analyst sharing model.

Test:

- viewer access;
- editor access;
- published access;
- scheduled refresh;
- subscription where supported.

---

## Lab 8 — Freshness Alert

Create:

```text
latest update
```

and alert when it violates the freshness SLA.

Test:

- healthy state;
- stale state;
- notification;
- false-positive conditions.

---

## Lab 9 — Revenue Drop Alert

Implement the 30% day-over-day scenario.

Test:

```text
normal day
large drop
zero previous revenue
missing previous day
late data
```

---

## Lab 10 — Materialized View

Build a repeated expensive analytical result where supported.

Compare:

```text
normal view/query
vs
materialized result
```

Measure:

- runtime;
- refresh behavior;
- storage;
- cost.

---

## Lab 11 — SQL Streaming Table

Create/consume a SQL-defined streaming table in a supported environment.

Verify:

- incremental behavior;
- source semantics;
- refresh;
- downstream query behavior.

---

## Lab 12 — Metric Definitions

Create metrics:

```text
Net Revenue
AOV
Orders
Active Customers
```

Use the semantic-layer capability available in the current environment.

Validate the definitions against raw/gold reconciliation.

---

## Lab 13 — Genie Agent

Create a finance Genie Agent.

Add:

- curated tables;
- business terminology;
- instructions;
- example SQL;
- trusted assets.

---

## Lab 14 — Genie Evaluation

Ask 20 real business questions.

Record:

```text
Question
Expected answer
Expected SQL
Generated answer
Generated SQL
Correct?
Why?
Failure
Fix
Retest
```

---

## Lab 15 — Row/Column Security

Validate:

```text
SQL
Dashboard
Genie
```

against the same governed data.

Test:

- allowed user;
- restricted user;
- masked column;
- unauthorized access.

---

## Lab 16 — External BI

Connect an external BI tool if supported.

Validate:

- authentication;
- authorization;
- query execution;
- performance;
- concurrency;
- cost.

---

## Lab 17 — Query Federation

Demonstrate a supported external source.

Compare:

```text
federated query
vs
ingested table
```

Measure:

- latency;
- source-system load;
- cost;
- governance;
- repeatability.

---

## Lab 18 — Dashboard Performance Optimization

Start with an intentionally inefficient dashboard.

Optimize:

1. query;
2. data model;
3. layout;
4. materialization/pre-aggregation;
5. warehouse;
6. caching;
7. concurrency.

Document before/after evidence.

---

# 82. Required `sql/analytics/` Exercise

The roadmap-required exercise must be completed as one integrated workflow.

### Exercise 1 — Parameterized queries

Create:

```text
daily revenue
top products
conversion
```

and use them in an AI/BI dashboard.

### Exercise 2 — Alerts

Alert when:

```text
gold.daily_revenue is stale
```

or:

```text
revenue drops >30% day over day
```

### Exercise 3 — Certified metrics

Define:

```text
Net Revenue
AOV
```

using the semantic capability available in the environment.

### Exercise 4 — Genie

Create an Agent with:

- instructions;
- example SQL;
- trusted assets.

Evaluate with 20 business questions.

### Exercise 5 — Security

Verify:

```text
row filters
column masks
```

through:

```text
SQL
dashboard
Genie
```

---

# 83. Break/Fix Incidents

Each incident uses:

```text
Symptom
Business Impact
Initial Hypothesis
Evidence
Investigation
Root Cause
Fix
Verification
Prevention
Lesson
```

---

## Incident 1 — Dashboard Suddenly Becomes Slow

### Symptom

45-second dashboard load.

### Investigation

Check:

- query history;
- warehouse;
- concurrency;
- scan;
- query plan;
- recent changes.

### Root cause example

A gold query began scanning a much larger date range.

### Fix

Correct filtering and data model.

---

## Incident 2 — Dashboard Shows Incorrect Revenue

### Symptom

Dashboard is 18% higher than finance source.

### Investigation

Trace metric definition and joins.

### Root cause

One-to-many join multiplied order rows.

### Fix

Correct join grain.

---

## Incident 3 — Duplicate Rows After Join

### Root cause

Dimension was not unique on the join key.

### Fix

Enforce dimension grain or deduplicate intentionally.

---

## Incident 4 — SQL Warehouse Overwhelmed

### Symptom

Morning dashboard refresh creates latency spikes.

### Investigation

Analyze concurrency and refresh overlap.

### Fix

Adjust workload isolation/scheduling/capacity.

---

## Incident 5 — Dashboard Refresh Fails

Investigate:

```text
query
permissions
warehouse
source availability
schema changes
```

---

## Incident 6 — Alert Fires Incorrectly

### Root cause

Business holiday caused a legitimate revenue decline.

### Fix

Improve alert semantics and expected business-calendar behavior.

---

## Incident 7 — Freshness Alert Silent

### Root cause possibilities

- alert disabled;
- query wrong;
- threshold wrong;
- schedule not running;
- notification configuration;
- timezone mismatch.

---

## Incident 8 — Materialized Result Is Stale

Investigate:

- refresh;
- source changes;
- schedule;
- dependency;
- failure history.

---

## Incident 9 — Genie Generates Incorrect SQL

### Root cause

Ambiguous business terminology and insufficient examples.

### Fix

Improve:

- metric definitions;
- instructions;
- trusted assets;
- curated source set.

---

## Incident 10 — Genie Chooses Wrong Metric

### Root cause

Two metrics have similar names but different definitions.

### Fix

Centralize and clarify semantic definitions.

---

## Incident 11 — Genie Uses Inappropriate Table

### Root cause

Too many overlapping tables exposed.

### Fix

Curate the analytical surface.

---

## Incident 12 — Row Security Appears Incorrect

### Investigation

Compare:

```text
SQL
Dashboard
Genie
```

using the same user identity and data.

### Lesson

UI filtering is not equivalent to authorization.

---

## Incident 13 — External BI Becomes Slow

Investigate:

- query generation;
- concurrency;
- warehouse;
- cache;
- data scan;
- dashboard behavior.

---

## Incident 14 — Federation Creates High Latency

### Root cause

Repeated analytical workloads are being pushed to an operational database.

### Fix

Evaluate ingestion into the lakehouse.

---

## Incident 15 — Dashboard Cost Increases

Investigate:

- query frequency;
- refresh schedule;
- user growth;
- warehouse size;
- repeated scans;
- materialization;
- cache;
- new dashboard widgets.

---

## Incident 16 — Dashboard Fast but Wrong

### Lesson

Correctness is a production requirement, not an optional enhancement.

---

## Incident 17 — Metric Definitions Diverge

### Symptom

Two teams report different AOV.

### Root cause

Different denominator definitions.

### Fix

Certified semantic metric.

---

## Incident 18 — Genie Is Accurate in Testing but Fails in Production

Investigate:

- data permissions;
- changed tables;
- semantic metadata;
- production data distribution;
- evaluation coverage.

---

# 84. Production Runbook — Dashboard Incident

### Step 1 — Confirm impact

Record:

```text
dashboard
users
SLO
start time
```

### Step 2 — Identify underlying queries

Trace dashboard datasets.

### Step 3 — Inspect query history

Find slow/failed executions.

### Step 4 — Inspect warehouse

Check:

- capacity;
- concurrency;
- queueing;
- configuration.

### Step 5 — Inspect query profile

Find:

- expensive scan;
- join;
- aggregation;
- shuffle;
- bottleneck.

### Step 6 — Check data volume

Did the source grow?

### Step 7 — Check model

Did grain/cardinality change?

### Step 8 — Check layout

Did clustering or file behavior change?

### Step 9 — Check cache/materialization

Is the workload cold?

Did refresh fail?

### Step 10 — Check recent changes

```text
SQL
schema
dashboard
warehouse
pipeline
permissions
```

### Step 11 — Benchmark fix

Use controlled before/after comparison.

### Step 12 — Validate correctness

Performance improvements must not change business results incorrectly.

### Step 13 — Communicate

Report:

```text
Impact
Root cause
Fix
Expected behavior
Follow-up
```

---

# 85. Production Runbook — Genie Incorrect Answer

### Step 1

Capture the exact question.

### Step 2

Capture generated SQL.

### Step 3

Define expected business meaning.

### Step 4

Validate the expected SQL independently.

### Step 5

Inspect:

- source tables;
- metric definitions;
- instructions;
- examples;
- trusted assets;
- column descriptions;
- permissions.

### Step 6

Correct analytical context.

### Step 7

Retest the original question.

### Step 8

Add the question to regression evaluation.

### Step 9

Re-run the full evaluation set.

### Step 10

Document the failure mode.

---

# 86. Decision Matrix — Dashboard Source

| Source | Reuse | Governance | Performance Potential | Freshness | Best Use |
|---|---|---|---|---|---|
| Gold table | High | High | High | Pipeline-dependent | Core analytics |
| View | High | High | Variable | Near-live | Reusable logic |
| Materialized view | High | High | High for repeated workloads | Refresh-dependent | Expensive repeated analytics |
| Pre-aggregated table | High | High | High | Pipeline-dependent | High-volume BI |

---

# 87. Decision Matrix — Serving Interface

| Interface | Best For | Main Risk |
|---|---|---|
| Databricks SQL | Analysts / engineering | Uncontrolled ad hoc workload |
| AI/BI Dashboard | Repeated business reporting | Poor dataset design |
| Genie Agent | Natural-language exploration | Semantic/SQL errors |
| External BI | Enterprise BI ecosystem | Connector/concurrency complexity |

---

# 88. Decision Matrix — Federation vs Ingestion

| Dimension | Federation | Ingestion |
|---|---|---|
| Data movement | Minimal | Yes |
| Freshness | Potentially live | Ingestion-dependent |
| Source load | Can be significant | Lower after ingestion |
| Repeated large analytics | Often weaker | Strong |
| Historical storage | Weak | Strong |
| Transformation | Limited | Strong |
| POC/ad hoc | Strong | More effort |
| Governance | UC foreign catalog | UC native data |
| Operational independence | Lower | Higher |

---

# 89. Decision Matrix — Genie Readiness

| Requirement | Ready? |
|---|---|
| Curated gold tables | [ ] |
| Correct grain | [ ] |
| Certified metrics | [ ] |
| Clear column names | [ ] |
| Business descriptions | [ ] |
| Governance | [ ] |
| Trusted queries | [ ] |
| Evaluation set | [ ] |
| Security validation | [ ] |
| Performance validation | [ ] |
| Ownership | [ ] |
| Regression process | [ ] |

If several are unchecked, do not expose the dataset as a production natural-language analytics surface.

---

# 90. ADR-001 — Use Curated Gold Tables for Dashboards

## Context

Business dashboards require stable analytical semantics.

## Problem

Raw and silver tables create repeated transformation logic.

## Options

1. query raw data;
2. query silver data;
3. create governed gold model.

## Decision

Use curated gold analytical assets as the default dashboard serving layer.

## Why

- consistent grain;
- reusable metrics;
- governance;
- performance;
- maintainability.

## Trade-offs

Additional modeling work.

## Security

Govern through Unity Catalog.

## Cost

Potential additional storage/processing, offset by reduced repeated query work.

## Rollback

Revert dashboard dataset to the prior approved source if validation fails.

## Validation

Reconcile metrics with trusted source systems.

---

# 91. ADR-002 — Use SQL Warehouses for BI Workloads

## Context

BI workloads have different concurrency and latency requirements from batch processing.

## Decision

Use SQL warehouses as the analytical serving compute layer where appropriate.

## Trade-offs

Capacity and consumption costs.

## Validation

Benchmark representative BI concurrency.

---

# 92. ADR-003 — Centralize Business Metrics

## Context

Teams report different versions of the same KPI.

## Decision

Use governed metric definitions for shared enterprise KPIs.

## Why

Metric consistency is a correctness control.

## Consequences

Metric ownership and change management become explicit.

---

# 93. ADR-004 — Use Genie Only Over Governed Analytical Data

## Context

Natural-language analytics introduces semantic and security risk.

## Decision

Expose only curated, governed analytical assets.

## Why

Reduces ambiguity and protects sensitive data.

## Consequences

More upfront modeling and evaluation.

---

# 94. ADR-005 — Materialize Repeated Expensive Analytics

## Context

A dashboard repeatedly executes expensive aggregations.

## Decision

Evaluate materialized views or pre-aggregated gold tables.

## Why

Reduce repeated computation.

## Trade-offs

Refresh/storage cost.

---

# 95. ADR-006 — Use Federation for a Specific Ad Hoc Use Case

## Context

A small external operational dataset must be queried without building ingestion immediately.

## Decision

Use supported federation.

## Why

Fast access without creating a full ingestion pipeline.

## Exit condition

Move to ingestion if volume, frequency, latency, or source-system impact becomes unacceptable.

---

# 96. Analytics Quality Gate

Before publishing:

```text
Data correctness
      ↓
Metric correctness
      ↓
Security
      ↓
Performance
      ↓
Cost
      ↓
Usability
      ↓
Monitoring
      ↓
AI evaluation where applicable
      ↓
Production approval
```

A dashboard or Genie Agent is not production-ready until it passes the relevant gates.

---

# 97. Interview Preparation

## Beginner — 15

### B1. What is Databricks SQL?

**Answer:** The SQL-oriented analytical interface and execution environment for querying and serving lakehouse data.

### B2. What is a SQL warehouse?

**Answer:** Compute designed to execute SQL analytical workloads.

### B3. What is a dashboard dataset?

**Answer:** A query/table/model supplying data to dashboard visualizations.

### B4. Why use gold tables?

**Answer:** They provide curated, business-oriented, reusable analytical data.

### B5. What is an alert?

**Answer:** A scheduled evaluation of query results against a condition with notifications when the condition is met.

### B6. What is a materialized view?

**Answer:** A stored/precomputed query result maintained or refreshed by the platform.

### B7. What is a semantic layer?

**Answer:** A governed layer defining reusable business meaning and metrics.

### B8. What is a metric view?

**Answer:** A Databricks semantic-layer object for defining standardized business metrics.

### B9. What is Genie?

**Answer:** Databricks' natural-language analytics experience, currently documented as Genie Agents.

### B10. Why curate Genie data?

**Answer:** To reduce ambiguity, improve answer quality, and maintain governance.

### B11. What is query federation?

**Answer:** Querying supported external data sources without first ingesting the data into Databricks.

### B12. What is dashboard concurrency?

**Answer:** Multiple dashboard/query workloads executing at the same time.

### B13. Why can a dashboard be slow?

**Answer:** Query logic, data volume, layout, warehouse capacity, concurrency, caching, or materialization can all contribute.

### B14. Why is metric consistency important?

**Answer:** Different KPI definitions can produce contradictory business decisions.

### B15. Why review generated SQL?

**Answer:** Fluent natural-language output does not guarantee analytical correctness.

---

## Intermediate — 20

### I1. Why should dashboards generally use gold data?

Because gold provides curated grain, business semantics, governance, and reusable analytical logic.

### I2. Why can a one-to-many join inflate revenue?

Because one fact row may be repeated for every matching child row.

### I3. How do parameters improve dashboard reuse?

They allow one dataset/query to serve multiple runtime selections.

### I4. Why does concurrency affect warehouse sizing?

Multiple simultaneous workloads compete for execution capacity.

### I5. What is the difference between a view and materialized view?

A view stores logic; a materialized view stores a maintained/precomputed result.

### I6. Why are pre-aggregated tables useful?

They avoid repeatedly performing expensive aggregations.

### I7. What is a semantic metric?

A governed definition of a business measure.

### I8. Why are metric views useful?

They centralize metric logic for consistent reuse.

### I9. What is a Genie Agent?

A domain-specific natural-language interface configured over governed analytical assets.

### I10. Why are example queries useful to Genie?

They provide known-good analytical patterns.

### I11. Why are instructions useful?

They clarify terminology and analytical rules.

### I12. Why can Genie still be wrong after careful configuration?

AI-assisted query generation remains probabilistic and can misinterpret intent or data relationships.

### I13. What is query federation good for?

Ad hoc, exploratory, or migration-oriented access to supported external sources.

### I14. Why might ingestion be better for repeated analytics?

It decouples analytical workloads from the source and can provide better scale and latency.

### I15. Why does caching complicate benchmarking?

Warm executions can be materially different from cold executions.

### I16. What is a freshness alert?

An alert that detects whether data is newer than an expected freshness threshold.

### I17. Why can threshold alerts produce false positives?

Business seasonality or legitimate events can look like failures.

### I18. Why is dashboard sharing not the same as data authorization?

Dashboard access and underlying data privileges are separate controls.

### I19. Why should row security live at the data layer?

It protects data across multiple consumption interfaces.

### I20. Why should dashboard performance be measured under concurrency?

A query fast in isolation may be slow under production traffic.

---

## Advanced — 20

### A1. A 5 TB dashboard is slow with Photon. What do you inspect first?

Scan, plan, joins, aggregation, layout, concurrency, warehouse, and cache state before assuming compute is the issue.

### A2. Two dashboards report different revenue. How do you investigate?

Compare metric definitions, grain, joins, filters, date semantics, refunds, and source tables.

### A3. Genie generates valid SQL but the wrong business answer. Why?

The SQL can be syntactically correct while using the wrong metric, join, grain, or date semantics.

### A4. How do you evaluate a Genie Agent?

Use a representative question set and record generated SQL, expected SQL, correctness, failure modes, and regression results.

### A5. Why should raw tables not be the default Genie surface?

They create ambiguity, expose irrelevant data, and increase semantic/security risk.

### A6. When would you use a metric view instead of dashboard-local logic?

When the metric should be governed and reused across dashboards, Genie, and other consumers.

### A7. How do you decide between materialized view and pre-aggregated table?

Consider ownership, refresh behavior, reuse, transformation complexity, storage, and operational needs.

### A8. How do you investigate a dashboard cost spike?

Compare user traffic, query frequency, refresh schedules, warehouse size, query scans, and recent dashboard changes.

### A9. Why can federation become expensive?

Repeated queries may execute against remote systems and consume remote compute/network capacity.

### A10. What makes federation unsuitable for heavy analytics?

High data volume and repeated workloads can produce latency and source-system load.

### A11. How does a dashboard filter affect performance?

It can reduce query work when pushed into dataset SQL; it may be less useful if data is already materialized locally.

### A12. Why is query history important for incident response?

It provides execution evidence and allows comparison across time.

### A13. Why is semantic consistency a governance problem?

Different definitions can create contradictory organizational decisions.

### A14. How do row filters interact with Genie?

The analytical experience must respect the user's governed access to the underlying data; validate this in the actual environment.

### A15. What is the difference between dashboard filtering and row-level security?

Filtering changes what a user asks to display; row-level security controls what the user is authorized to access.

### A16. How do you benchmark dashboard improvements?

Control dataset, query, warehouse, concurrency, cache state, and user behavior.

### A17. Why can materialization increase cost?

It requires storage and refresh computation.

### A18. Why can pre-aggregation increase complexity?

It introduces additional data products and freshness/maintenance requirements.

### A19. What is a dashboard SLO?

A measurable objective for dashboard latency/freshness/availability.

### A20. Why should analytics architecture be evaluated end-to-end?

A slow or incorrect result may originate in data production, governance, compute, query, or serving—not the visualization itself.

---

## Senior / Production — 20

### S1. The CFO dashboard takes 40 seconds. Photon is enabled. What do you investigate?

Start with SLO, query history, query profile, scan, joins, layout, concurrency, warehouse capacity, and cache/materialization state.

### S2. Two teams define AOV differently. What architecture change do you make?

Centralize the definition in an appropriate governed semantic layer and assign ownership.

### S3. Genie answers 19/20 questions correctly. Is it production-ready?

Not automatically. Investigate the failed case, evaluate risk severity, add regression coverage, and define acceptable error boundaries.

### S4. Genie uses a sensitive table even though the answer could come from a gold table. What do you do?

Reduce the Agent's analytical surface and curate the governed gold/semantic assets.

### S5. How would you design a production Genie evaluation framework?

Create versioned test questions, expected semantics, generated SQL capture, correctness labels, security tests, regression thresholds, and ownership.

### S6. A dashboard is fast but costs 5× more. What do you do?

Compare SLO value against incremental cost and investigate whether query/model/cache/warehouse improvements can retain acceptable latency more cheaply.

### S7. How would you separate executive BI and analyst workloads?

Characterize concurrency and SLOs, then evaluate workload isolation and appropriate warehouse capacity.

### S8. When is federation preferable to ingestion?

For supported low/medium-volume ad hoc or exploratory access where live data matters and ingestion cost/latency is not justified.

### S9. When should federation be replaced by ingestion?

When volume, frequency, source load, latency, transformation, or historical analytics requirements make direct querying unsuitable.

### S10. How do you prevent metric drift?

Centralize governed definitions, test them, assign owners, document changes, and make dashboards/Genie consume the governed definitions.

### S11. How do you protect sensitive data in AI-assisted analytics?

Use governed identities, Unity Catalog permissions, row/column controls, curated assets, limited Genie scope, and evaluation.

### S12. How would you debug a dashboard regression after a pipeline change?

Compare data volume, grain, schema, query plans, scan, joins, metrics, refresh behavior, and warehouse workload before/after the change.

### S13. What is the biggest Genie governance risk?

Treating natural-language convenience as a substitute for data authorization and semantic correctness.

### S14. How do you design dashboard observability?

Track freshness, runtime, failures, query volume, warehouse utilization/concurrency, data quality, and cost.

### S15. How do you define a business metric contract?

Specify definition, grain, source, filters, time semantics, owner, security, tests, freshness, and consumers.

### S16. How do you prevent dashboard query explosion?

Reuse datasets/metrics, avoid duplicated logic, consolidate visualizations, schedule intelligently, and monitor query volume.

### S17. How do you evaluate materialization economically?

Compare repeated query compute and latency with refresh compute, storage, freshness, and operational complexity.

### S18. How do you make external BI production-grade?

Define authentication, authorization, serving contract, SLO, concurrency expectations, monitoring, cost ownership, and change management.

### S19. How do you handle a dashboard that violates both latency and cost objectives?

Reduce work first, then evaluate materialization/layout/query/compute/isolation changes against explicit SLO and cost constraints.

### S20. What is the senior-level analytics mental model?

```text
Correct data
→ Correct metric
→ Governed access
→ Efficient query
→ Appropriate compute
→ Reliable serving
→ Evaluated AI assistance
→ Observable cost
```

---

# 98. Practice Questions

## 98.1 SQL Practice — 20

1. Write a daily revenue query.
2. Calculate AOV.
3. Calculate month-to-date revenue.
4. Compare current revenue with prior day.
5. Find top 10 products.
6. Calculate regional revenue share.
7. Calculate customer conversion.
8. Identify missing dates.
9. Detect duplicate order IDs.
10. Reconcile gold revenue to a source total.
11. Calculate rolling seven-day revenue.
12. Safely divide revenue by orders.
13. Identify customers with declining revenue.
14. Compare current month to prior month.
15. Find stale partitions/data.
16. Create a freshness query.
17. Create a revenue-drop query.
18. Detect join multiplication.
19. Write a parameter-ready analytical query.
20. Explain the grain of each result.

---

## 98.2 Analytics Modeling — 15

1. Define the grain of `gold.orders`.
2. Design a customer dimension.
3. Explain a one-to-many join.
4. Design a daily revenue table.
5. Decide whether AOV belongs in a gold table or semantic layer.
6. Define net revenue.
7. Handle refunds.
8. Handle late-arriving orders.
9. Handle timezone.
10. Handle currency.
11. Define active customer.
12. Design a product-performance aggregate.
13. Identify a metric-definition conflict.
14. Design a semantic metric contract.
15. Design a gold layer for finance dashboards.

---

## 98.3 Dashboard Architecture — 15

1. Design an executive dashboard.
2. Design an analyst dashboard.
3. Decide which metrics belong on the first page.
4. Design filter scopes.
5. Design dashboard datasets.
6. Avoid duplicated SQL.
7. Design dashboard refresh.
8. Design sharing.
9. Design alert ownership.
10. Diagnose a slow dashboard.
11. Diagnose a wrong dashboard.
12. Design dashboard SLOs.
13. Design dashboard observability.
14. Design cost attribution.
15. Design dashboard release/change management.

---

## 98.4 Genie — 15

1. Design a finance Genie Agent.
2. Choose tables to expose.
3. Write domain instructions.
4. Create trusted SQL examples.
5. Define metric semantics.
6. Build 20 evaluation questions.
7. Classify failures.
8. Review generated SQL.
9. Test ambiguous questions.
10. Test unauthorized data requests.
11. Test wrong-metric behavior.
12. Test date logic.
13. Test joins.
14. Build a regression suite.
15. Define production-readiness criteria.

---

## 98.5 Performance Troubleshooting — 15

1. Dashboard takes 45 seconds.
2. Query scans 5 TB for a small result.
3. Warehouse is saturated at 9 AM.
4. One dashboard widget dominates runtime.
5. Materialized result is stale.
6. Cache changes benchmark results.
7. External BI is slower than SQL editor.
8. Federation is slow.
9. Query performance regresses after data growth.
10. Pre-aggregation improves latency but increases refresh cost.
11. More warehouse capacity barely helps.
12. Dashboard query count doubles.
13. Metric view is slower than expected.
14. Scheduled refresh creates a concurrency spike.
15. Genie-generated SQL is expensive.

---

## 98.6 Security/Governance — 10

1. Design regional row-level access.
2. Mask PII.
3. Secure executive dashboards.
4. Secure Genie.
5. Secure external BI.
6. Test row filters.
7. Test column masks.
8. Define metric ownership.
9. Prevent dashboard-based governance bypass.
10. Design an audit trail for analytics changes.

---

## 98.7 Cost Scenarios — 10

1. Dashboard cost doubles.
2. Warehouse is idle most of the day.
3. Refresh schedule runs too often.
4. Materialization saves runtime but adds refresh cost.
5. Federation is cheap initially but expensive at scale.
6. More compute improves latency 20% but costs 80% more.
7. Pre-aggregation reduces query cost but adds pipeline cost.
8. User growth creates concurrency pressure.
9. Cache reduces repeated compute.
10. A dashboard meets SLO but exceeds budget.

---

# 99. Senior Data Engineer Scenarios

## Scenario 1 — CFO Dashboard

> The CFO dashboard takes 40 seconds. The source table is 5 TB and Photon is enabled.

### Expected reasoning

```text
SLO
→ query history
→ profile
→ scan
→ joins
→ aggregation
→ layout
→ concurrency
→ cache/materialization
→ warehouse
```

Do not begin with "increase warehouse size."

---

## Scenario 2 — Conflicting Revenue

> Two dashboards report different revenue.

Investigate:

```text
Metric definition
→ grain
→ joins
→ filters
→ date
→ refunds
→ currency
→ source
```

---

## Scenario 3 — Genie Chooses Wrong Table

> Genie understands the question but selects the wrong table.

Fix:

```text
Reduce source surface
+
improve table descriptions
+
trusted examples
+
metric definitions
+
instructions
+
evaluation
```

---

## Scenario 4 — Correct SQL, Wrong Business Answer

Example:

```text
Question:
"What was net revenue last month?"

Generated SQL:
SUM(gross_revenue)
```

SQL is valid.

Business answer is wrong.

Lesson:

> **SQL validity is not semantic correctness.**

---

## Scenario 5 — Morning Dashboard Failure

The warehouse is healthy during the day but struggles at 9 AM.

Investigate:

- concurrent users;
- refresh schedules;
- query bursts;
- warehouse capacity;
- overlapping jobs.

---

## Scenario 6 — Cost Spike

Users did not increase.

Investigate:

```text
Query count
Query duration
Data scanned
Refresh schedule
Warehouse size
Materialization
Cache behavior
New widgets
```

---

## Scenario 7 — External BI Difference

External BI is slower than Databricks SQL.

Possible causes:

- different query generation;
- extra queries;
- concurrency;
- cache differences;
- result shape;
- connector behavior.

---

# 100. Common Misconceptions

## "Databricks SQL is just a SQL editor."

Incomplete.

It is part of a broader analytical serving platform including SQL warehouses, query execution, dashboards, alerts, metric views, and AI/BI experiences.

## "Dashboards should query raw tables."

Usually a poor production default.

Curated gold/semantic assets improve correctness, governance, and reuse.

## "A faster dashboard is automatically better."

No.

Correctness, security, freshness, reliability, and cost matter.

## "Genie can safely query any table."

No.

Curate and govern the analytical surface.

## "AI-generated SQL is automatically correct."

No.

Validate generated SQL and business semantics.

## "Metric definitions are just documentation."

No.

They can be executable semantic contracts.

## "Row-level security only needs to be implemented in the dashboard."

No.

Authorization belongs in the governed data layer.

## "More warehouse capacity always fixes performance."

No.

Data model, query, layout, concurrency, and source behavior can dominate.

## "Caching means the dashboard is permanently fast."

No.

Cache state, invalidation, freshness, and workload changes matter.

## "Materialized views are always better."

No.

They trade refresh/storage cost for query performance.

## "Federation is always better than ingestion."

No.

Federation is valuable for specific access patterns; ingestion is often better for repeated high-volume analytics.

## "If SQL succeeds, the result is correct."

No.

Syntactic correctness is different from business correctness.

---

# 101. Mental Models

### Mental Model 1

**Gold data → governed serving layer → business consumption.**

### Mental Model 2

**A dashboard is an application, not just a chart.**

### Mental Model 3

**Correct metric → correct data → correct SQL → correct answer.**

### Mental Model 4

**Genie quality depends heavily on the analytical context you provide.**

### Mental Model 5

**Govern AI-assisted analytics before automating it.**

### Mental Model 6

**Optimize the data path before simply adding compute.**

### Mental Model 7

**A metric is a contract, not just a formula.**

### Mental Model 8

**A filter is not authorization.**

### Mental Model 9

**A syntactically valid SQL query can still be semantically wrong.**

### Mental Model 10

**Benchmark dashboards like applications: workload, latency, concurrency, and cost all matter.**

---

# 102. Glossary

| Term | Definition |
|---|---|
| Databricks SQL | SQL-oriented analytical interface and execution environment for lakehouse workloads. |
| SQL warehouse | Managed compute used to execute SQL analytical workloads. |
| Query history | Record of SQL workload execution used for analysis and operations. |
| Query parameter | Runtime value used to make a query reusable. |
| AI/BI dashboard | Databricks business-intelligence experience for visual analytical consumption. |
| Dataset | Query/table/model supplying dashboard data. |
| Visualization | Graphical representation of analytical data. |
| SQL alert | Scheduled evaluation of a SQL query result against a condition. |
| Materialized view | Stored/precomputed query result maintained by the platform. |
| Streaming table | Managed table using streaming/incremental semantics in the declarative pipeline ecosystem. |
| Semantic layer | Governed layer defining business meaning and reusable metrics. |
| Metric definition | Formal definition of a business measure. |
| Metric view | Databricks semantic-layer object for standardized metrics. |
| Genie | Databricks natural-language analytics family; current product documentation uses Genie Agents for domain-specific data chat. |
| Genie Agent | Domain-specific natural-language analytics interface configured over governed data. |
| Genie space | Earlier roadmap/product terminology for Genie Agent. |
| Trusted asset | Curated analytical context such as trusted queries/semantic assets used to improve natural-language analytics. |
| Generated SQL | SQL produced by an AI-assisted analytics system. |
| Query federation | Querying supported external data systems without first ingesting the data. |
| Result cache | Reusable query results that can reduce repeated execution where supported. |
| Dashboard concurrency | Simultaneous analytical workload generated by dashboard users/refreshes. |
| Gold table | Curated business-oriented analytical data asset. |
| Grain | What one row in an analytical relation represents. |
| Measure | Quantitative business value such as revenue. |
| Dimension | Attribute used to segment/analyze measures. |
| Row filter | Governance rule controlling which rows a user can access. |
| Column mask | Governance rule controlling how sensitive column values are exposed. |
| Certified metric | Approved, governed business metric with an authoritative definition. |
| Query profile | Execution information used to understand query performance and bottlenecks. |
| Freshness | How current an analytical dataset is relative to its expected update time. |
| SLO | Service-level objective defining measurable expected behavior. |

---

# 103. Current-Documentation Safety

Databricks evolves rapidly.

Before production implementation, verify the current official documentation for:

- SQL warehouse capabilities;
- AI/BI dashboards;
- dashboard limits;
- filters and parameters;
- dashboard sharing and subscriptions;
- SQL alerts;
- materialized views;
- streaming tables;
- Genie Agents;
- metric views;
- semantic metadata;
- external BI connectivity;
- Lakehouse Federation;
- caching;
- serverless availability;
- preview/beta features;
- exact SQL syntax;
- current permissions;
- current pricing.

Do not fabricate:

- UI controls;
- API fields;
- feature flags;
- pricing;
- limits;
- availability;
- Genie behavior;
- semantic-layer syntax.

If a capability is preview, beta, experimental, region-dependent, runtime-dependent, or workspace-dependent, state that explicitly.

---

# 104. Connections to Other G4 Topics

## Topic 02 — Compute

SQL warehouses provide analytical serving compute.

## Topic 04 — Unity Catalog

Unity Catalog governs what users and analytical interfaces can access.

## Topic 07 — Lakeflow Declarative Pipelines

Pipelines produce the data consumed by analytics.

## Topic 08 — Lakeflow Jobs

Jobs can orchestrate refreshes and downstream analytical workflows.

## Topic 09 — Photon / Performance

Performance engineering directly affects SQL and dashboard latency.

## Topic 11 — Delta Sharing / Marketplace

Analytics assets may later be shared with external consumers.

## Topic 12 — Asset Bundles / CI/CD

Analytics assets should increasingly be managed and deployed reproducibly where supported.

## Topic 13 — Cost Management

SQL warehouses, dashboards, refreshes, and analytics queries contribute directly to platform cost.

## Topic 14 — MLflow / Feature Engineering

Analytics and ML often consume related governed lakehouse data products.

---

# 105. Production Capstone — Databricks Finance Analytics Platform

## Scenario

A company wants a governed finance analytics platform for executives and analysts.

Architecture:

```text
Gold finance tables
        ↓
Unity Catalog governance
        ↓
Certified metrics
        ↓
SQL warehouse
        ↓
┌───────────────────────────────┐
│ SQL queries                   │
│ AI/BI dashboard               │
│ SQL alerts                    │
│ Genie Agent                   │
│ External BI                   │
└───────────────────────────────┘
```

## Required implementation

1. daily revenue query;
2. top-products query;
3. conversion query;
4. parameterized filters;
5. finance dashboard;
6. dashboard schedule;
7. dashboard permissions;
8. freshness alert;
9. greater-than-30% revenue-drop alert;
10. certified metrics;
11. Genie Agent;
12. Genie instructions;
13. trusted assets;
14. 20-question Genie evaluation;
15. row/column security validation;
16. dashboard performance optimization;
17. cost analysis;
18. production runbook;
19. architecture ADR.

---

# 106. Capstone Deliverable

Produce:

```text
Architecture
Data Model
Metrics
Queries
Dashboard Design
Alerts
Genie Design
Security Model
Performance Model
Cost Model
Operational Runbooks
Evaluation Results
Production Recommendation
```

The recommendation must include:

```text
Current State
Problems
Evidence
Proposed Architecture
Security
Performance
Cost
Operational Model
Risks
Rollback
Validation
```

---

# 107. Genie Evaluation Scorecard

Use:

| Dimension | Score |
|---|---:|
| Intent understanding | /5 |
| SQL correctness | /5 |
| Metric correctness | /5 |
| Filter correctness | /5 |
| Join correctness | /5 |
| Security compliance | /5 |
| Answer clarity | /5 |
| Performance | /5 |

Add:

```text
Failure category
Severity
Root cause
Fix
Regression test
```

Do not treat "good enough in a demo" as production readiness.

---

# 108. Final Production Checklist

## Databricks SQL

- [ ] I can write analytical SQL.
- [ ] I can parameterize queries.
- [ ] I understand query history.
- [ ] I can investigate SQL failures.
- [ ] I can read query profiles.
- [ ] I understand warehouse/query relationships.

## SQL Warehouses

- [ ] I understand sizing.
- [ ] I understand concurrency.
- [ ] I understand auto-stop.
- [ ] I can reason about cost.
- [ ] I can distinguish latency from capacity problems.

## AI/BI Dashboards

- [ ] I can build datasets.
- [ ] I can build visualizations.
- [ ] I can create filters.
- [ ] I can use parameters.
- [ ] I can schedule dashboards.
- [ ] I can share dashboards securely.
- [ ] I can diagnose dashboard performance.
- [ ] I can validate metric correctness.

## Alerts

- [ ] I can create freshness alerts.
- [ ] I can create threshold alerts.
- [ ] I understand false positives.
- [ ] I can investigate alert failures.
- [ ] I understand alert-specific query limitations.

## Semantic Layer

- [ ] I understand metric definitions.
- [ ] I can define governed metrics.
- [ ] I understand metric views.
- [ ] I understand local vs governed semantic logic.
- [ ] I can create metric ownership/change controls.

## Genie

- [ ] I can create a Genie Agent.
- [ ] I can curate tables.
- [ ] I can write useful instructions.
- [ ] I can add trusted assets.
- [ ] I can evaluate generated SQL.
- [ ] I can evaluate answer correctness.
- [ ] I can test security.
- [ ] I can create a regression question set.
- [ ] I understand governed AI analytics.

## Production

- [ ] I understand external BI integration.
- [ ] I understand query federation.
- [ ] I understand caching.
- [ ] I can troubleshoot dashboard performance.
- [ ] I can analyze analytics cost.
- [ ] I can design secure analytics architecture.
- [ ] I can document analytics decisions.
- [ ] I can operate a production analytics incident.

---

# 109. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Section | Hands-on? | Production Depth? |
|---|---|---|---|---|
| SQL editor | Yes | 12 | Yes | Yes |
| Query history | Yes | 13 | Yes | Yes |
| Saved/reusable queries | Yes | 13–16 | Yes | Yes |
| Query parameters | Yes | 15–17 | Yes | Yes |
| AI/BI dashboards | Yes | 23–32 | Yes | Yes |
| Dashboard datasets | Yes | 24–25 | Yes | Yes |
| Visualizations | Yes | 26 | Yes | Yes |
| Dashboard filters | Yes | 27–28 | Yes | Yes |
| Dashboard scheduling | Yes | 31 | Yes | Yes |
| Dashboard sharing | Yes | 32 | Yes | Yes |
| Dashboard permissions | Yes | 32, 63 | Yes | Yes |
| SQL alerts | Yes | 33–37 | Yes | Yes |
| SQL warehouse serving | Yes | 18–22 | Yes | Yes |
| Warehouse sizing | Yes | 19 | Yes | Yes |
| Warehouse concurrency | Yes | 20 | Yes | Yes |
| Warehouse scaling | Yes | 19–22 | Yes | Yes |
| Auto-stop | Yes | 21 | Yes | Yes |
| Materialized views | Yes | 38–40 | Yes | Yes |
| Streaming tables | Yes | 40–43 | Yes | Yes |
| SQL + Lakeflow pipelines | Yes | 42–43 | Yes | Yes |
| Genie spaces / Agents | Yes | 49–58 | Yes | Yes |
| Natural-language questions | Yes | 50–56 | Yes | Yes |
| Curated tables | Yes | 51–54 | Yes | Yes |
| Genie instructions | Yes | 53 | Yes | Yes |
| Example queries | Yes | 54 | Yes | Yes |
| Trusted assets | Yes | 54 | Yes | Yes |
| Semantic layer | Yes | 44–48 | Yes | Yes |
| Metric definitions | Yes | 45–48 | Yes | Yes |
| Governed AI analytics | Yes | 59–63 | Yes | Yes |
| Certified metrics | Yes | 47–48 | Yes | Yes |
| Row-level security | Yes | 61–63 | Yes | Yes |
| Column-level security | Yes | 62–63 | Yes | Yes |
| Generated SQL review | Yes | 58 | Yes | Yes |
| External BI | Yes | 64–65 | Yes | Yes |
| Query federation | Yes | 66–68 | Yes | Yes |
| Caching | Yes | 69 | Yes | Yes |
| Dashboard performance | Yes | 70–75 | Yes | Yes |
| Pre-aggregated gold tables | Yes | 71–72 | Yes | Yes |
| Clustering relationship | Yes | 70 | Yes | Yes |
| Result/cache performance | Yes | 69–70 | Yes | Yes |
| Finance dashboard | Yes | 29, 81 | Yes | Yes |
| 20-question Genie evaluation | Yes | 55–57, 82 | Yes | Yes |
| Row/column security validation | Yes | 63, 81 | Yes | Yes |
| 18 progressive labs | Yes | 81 | Yes | Yes |
| 18 break/fix incidents | Yes | 83 | Yes | Yes |
| Dashboard incident runbook | Yes | 84 | Yes | Yes |
| Genie incident runbook | Yes | 85 | Yes | Yes |
| Decision matrices | Yes | 86–88 | Yes | Yes |
| ADRs | Yes | 90–95 | Yes | Yes |
| Interview preparation | Yes | 97 | Yes | Yes |
| SQL practice ≥20 | Yes | 98.1 | Yes | Yes |
| Analytics modeling ≥15 | Yes | 98.2 | Yes | Yes |
| Dashboard architecture ≥15 | Yes | 98.3 | Yes | Yes |
| Genie practice ≥15 | Yes | 98.4 | Yes | Yes |
| Performance scenarios ≥15 | Yes | 98.5 | Yes | Yes |
| Security scenarios ≥10 | Yes | 98.6 | Yes | Yes |
| Cost scenarios ≥10 | Yes | 98.7 | Yes | Yes |
| Senior Data Engineer scenarios | Yes | 99 | Yes | Yes |
| Common misconceptions | Yes | 100 | Yes | Yes |
| Mental models | Yes | 101 | Yes | Yes |
| Glossary | Yes | 102 | Yes | Yes |
| Current-documentation safety | Yes | 103 | Yes | Yes |
| Cross-topic dependencies | Yes | 104 | Yes | Yes |
| Production capstone | Yes | 105–106 | Yes | Yes |
| Genie scorecard | Yes | 107 | Yes | Yes |
| Final production checklist | Yes | 108 | Yes | Yes |

### Roadmap coverage result

**Complete against the supplied Topic 10 specification.**

---

# 110. Quality Verification

The module has been designed to satisfy the production-training standard:

- beginner-friendly progression;
- Databricks-specific context;
- SQL-heavy implementation;
- governed analytics;
- dashboard architecture;
- semantic consistency;
- AI-assisted analytics;
- Genie evaluation;
- performance engineering;
- cost engineering;
- security;
- troubleshooting;
- production runbooks;
- decision matrices;
- ADRs;
- interview preparation;
- practice questions;
- capstone;
- roadmap audit.

Current product terminology and capabilities should always be rechecked against official Databricks documentation before production implementation because Databricks evolves rapidly.

---

# 111. Final Operating Standard

Use this operating loop for production analytics:

```text
MODEL THE DATA
      ↓
DEFINE THE GRAIN
      ↓
DEFINE THE METRICS
      ↓
GOVERN THE DATA
      ↓
SERVE THROUGH APPROPRIATE COMPUTE
      ↓
WRITE CORRECT SQL
      ↓
BUILD REUSABLE ANALYTICAL DATASETS
      ↓
BUILD DASHBOARDS / ALERTS
      ↓
DEFINE SEMANTIC METRICS
      ↓
CURATE GENIE
      ↓
EVALUATE GENERATED SQL
      ↓
VALIDATE SECURITY
      ↓
BENCHMARK PERFORMANCE
      ↓
MEASURE COST
      ↓
MONITOR
      ↓
IMPROVE
```

The central principle is:

> **Correct data → correct metric → governed access → efficient query → reliable serving → evaluated AI assistance → observable cost.**

That is the production analytics engineering standard for Databricks SQL, AI/BI dashboards, and Genie.
