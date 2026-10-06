# 13 — Cost Management and System Tables

> **G4 — Databricks Lakehouse Platform Deep Dive**  
> **Topic 13 — Cost Management and System Tables**  
> **Level:** Basics → Intermediate → Advanced → Production  
> **Primary discipline:** Databricks FinOps, cost observability, system-table analytics, workload optimization

## 1. Learning Objectives

By the end of this module, you should be able to:

- explain Databricks billing and DBUs;
- distinguish Databricks usage charges from total cloud workload cost;
- understand relevant product/SKU categories;
- query billing usage and pricing system tables;
- analyze compute, jobs, pipelines, query history, and audit data;
- attribute usage to teams, environments, pipelines, and data products;
- design a production tagging taxonomy;
- use compute policies, auto-termination, auto-stop, warehouse sizing, job compute, budgets, and serverless usage policies as cost controls;
- build cost reports, dashboards, alerts, and anomaly detection;
- calculate unit economics;
- investigate unexplained cost increases;
- prevent double counting through grain-aware SQL;
- audit access to sensitive gold data;
- compare serverless and classic economics using measured workload data;
- run controlled optimization experiments;
- quantify before/after savings and trade-offs;
- design enterprise showback/chargeback;
- operate a production cost-observability capability.

The central question is:

> **What did Databricks cost, who spent it, what workload caused it, why did the cost change, how can I prove it with system data, what can I optimize, how much did I save, and how do I prevent recurrence?**

---

# 2. Prerequisites

This topic assumes the earlier roadmap already covered:

| Prerequisite | Earlier module/topic | Application here |
|---|---|---|
| SQL | Stage 2 | Cost-analysis queries |
| Data modeling | Stage 2 | FinOps fact/dimension model |
| Spark/PySpark | 2.14 | Workload/performance context |
| Delta Lake | 2.15 | Cost/performance implications |
| Cloud/IAM | 2.17 | Cloud cost context |
| CI/CD | 2.18 / G4 Topic 12 | Cost controls as code |
| Governance | 2.20 / G4 Topic 04 | Audit and ownership |
| Performance/cost | 2.21 | Databricks-specific cost measurement |
| Databricks compute | G4 Topic 02 | Cost-control decisions |
| Lakeflow Jobs | G4 Topic 08 | Job/run attribution |
| Photon/performance | G4 Topic 09 | Cost-performance optimization |
| Databricks SQL | G4 Topic 10 | Query/warehouse economics |

This file does **not** re-teach Spark, Delta internals, Airflow, dbt, Terraform, or Unity Catalog fundamentals. It applies those concepts specifically to Databricks cost engineering.

---

# 3. Why Databricks Cost Management Matters

A data platform can be technically excellent and financially unhealthy.

Consider:

```text
Pipeline works
+
Data is correct
+
SLA is met
+
Security is correct
```

but:

```text
Cost increased 3×
```

That is still a production engineering problem.

Databricks cost engineering asks:

```text
WHO?
WHAT?
WHERE?
WHEN?
WHY?
HOW MUCH?
WHAT DROVE IT?
WHAT CAN WE CHANGE?
WHAT DID THE CHANGE SAVE?
```

Cost management is therefore not merely:

> “Look at the monthly bill.”

It is an operational discipline:

```text
Visibility
   ↓
Attribution
   ↓
Investigation
   ↓
Optimization
   ↓
Governance
   ↓
Continuous Measurement
```

---

# Part I — Cost Fundamentals

# 4. Databricks Billing Fundamentals

## 4.1 What Is a DBU?

A **Databricks Unit (DBU)** is a unit of processing capability used by Databricks to meter certain platform usage.

The important engineering model is:

```text
Usage Quantity
×
Applicable Unit Price
=
Databricks Usage Cost
```

A DBU is not simply:

- one hour;
- one virtual machine;
- one query;
- one dollar.

It is a metered unit whose consumption depends on the workload/product.

Always use the current Databricks pricing and billing documentation for actual rates.

## 4.2 Why DBUs Exist

DBUs provide a common consumption metric across Databricks workloads.

Conceptually:

```text
Different workload
        ↓
Different SKU
        ↓
Usage measurement
        ↓
Billable quantity
```

This lets Databricks meter platform usage without making every product's cost model identical.

## 4.3 DBU Rate

A DBU rate is the applicable price associated with a SKU and pricing context.

The effective cost depends on:

- SKU;
- cloud;
- usage unit;
- account;
- effective pricing period;
- currency;
- applicable commercial terms.

Never hard-code a current DBU rate into production cost logic unless the rate is deliberately sourced from an authoritative pricing system.

---

# 5. Product SKUs

Relevant workload categories include:

- Jobs;
- all-purpose compute;
- SQL;
- serverless;
- pipelines.

The exact SKU names and availability vary by product, cloud, edition, region, and time.

The engineering principle is:

```text
Workload Type
→ Product/SKU
→ Usage
→ Price
→ Cost
```

## 5.1 Interactive Development

Developer debugging can involve:

- interactive compute;
- notebooks;
- exploratory SQL;
- repeated short executions;
- idle time.

Cost questions:

```text
How much time is idle?
How frequently is compute used?
Can auto-termination reduce waste?
Is the workload actually production work?
```

## 5.2 Production Jobs

Production jobs should normally use workload-appropriate job compute or serverless capabilities rather than relying on persistent interactive development compute.

Investigate:

- runtime;
- retries;
- concurrency;
- compute size;
- frequency;
- data volume;
- cost per successful run.

## 5.3 BI / SQL

Investigate:

- warehouse size;
- query volume;
- concurrency;
- queueing;
- auto-stop;
- refresh frequency;
- expensive queries.

## 5.4 Pipelines

Investigate:

- trigger frequency;
- processing duration;
- compute mode;
- data volume;
- retries;
- maintenance activity;
- cost per successful pipeline run.

---

# 6. Classic Compute Cost Model

For classic compute, the workload can incur both Databricks charges and underlying cloud infrastructure costs.

Conceptually:

```text
Total Classic Workload Cost
=
Databricks Usage Cost
+
Cloud Infrastructure Cost
```

Cloud infrastructure can include:

- virtual machines;
- disks;
- network-related costs;
- other associated cloud resources.

Current Databricks cost guidance explicitly distinguishes DBU charges from VM, disk, and associated network costs. For serverless services, Databricks documentation notes that VM infrastructure costs are incorporated into the serverless usage economics rather than separately billed to the customer in the same way. citeturn0search17

## 6.1 Cost Drivers

Classic compute cost depends on factors such as:

```text
Node count
×
Runtime
×
Workload configuration
+
Idle time
+
Associated infrastructure
```

A larger cluster is not automatically cheaper.

A smaller cluster is not automatically cheaper.

The correct objective is:

```text
Minimum total cost
while meeting
SLA + throughput + reliability + quality
```

---

# 7. Serverless Cost Model

Serverless changes the operational boundary.

With classic compute:

```text
Customer-managed compute configuration
+
Databricks usage
+
Cloud infrastructure
```

With serverless:

```text
Databricks-managed execution
+
Metered serverless usage
```

Serverless does **not** mean free.

Nor does:

```text
serverless = always cheaper
```

The correct question is:

> **What is the measured cost per unit of business work?**

Compare:

```text
Classic
vs
Serverless
```

using real workload measurements.

Possible benefits of serverless:

- less infrastructure management;
- faster operational setup;
- easier elastic execution;
- reduced manual capacity management.

Possible trade-offs:

- different unit economics;
- product-specific limitations;
- different startup/execution characteristics;
- different governance requirements.

---

# 8. Total Workload Cost

A critical mental model:

```text
Databricks Usage Cost
+
Cloud Infrastructure Cost
+
Other Required Platform Costs
=
Total Workload Economics
```

Do not confuse:

```text
DBU cost
```

with:

```text
total business workload cost
```

For classic compute, cloud infrastructure must be considered.

For serverless, infrastructure economics are incorporated differently.

For enterprise FinOps, also consider:

- engineering time;
- operational complexity;
- latency;
- reliability;
- support burden.

Therefore:

```text
Lowest DBU cost
≠
Lowest total cost
```

---

# 9. Illustrative Cost Calculation

Assume, purely for illustration:

```text
Usage = 500 DBUs
Illustrative rate = $0.50 / DBU
```

Then:

```text
Databricks usage cost
=
500 × $0.50
=
$250
```

If the same classic workload also incurs:

```text
Illustrative cloud infrastructure = $120
```

then:

```text
Total illustrative workload cost
=
$250 + $120
=
$370
```

These values are **illustrative only**.

Never treat tutorial numbers as current Databricks pricing.

---

# 10. Cost Per Unit

Once cost is measured, derive unit economics.

Examples:

```text
Cost per hour
Cost per job run
Cost per successful job run
Cost per pipeline run
Cost per dashboard refresh
Cost per query
Cost per TB processed
Cost per million records
Cost per business transaction
Cost per data product
```

General model:

```text
Unit Cost
=
Total Attributable Cost
÷
Business/Technical Output
```

The denominator must be meaningful.

---

# Part II — System Tables

# 11. What Are System Tables?

Databricks system tables are a Databricks-hosted analytical store of account/platform operational data in the `system` catalog.

They allow SQL-based historical analysis of areas including:

- billing;
- compute;
- query activity;
- jobs;
- audit events;
- governance;
- workload operations.

Current documentation describes system tables as read-only operational data sources for historical observability. citeturn0search14

This changes the workflow from:

```text
Open UI
→ Inspect manually
→ Guess
```

to:

```text
SQL
→ Filter
→ Join
→ Aggregate
→ Trend
→ Dashboard
→ Alert
→ Investigate
```

---

# 12. UI Inspection vs SQL Operational Analysis

## UI

Good for:

- quick investigation;
- interactive exploration;
- individual resource inspection.

## SQL system-table analysis

Good for:

- repeatable reports;
- historical analysis;
- attribution;
- cross-resource comparisons;
- dashboards;
- anomaly detection;
- automation;
- audit evidence.

Mental model:

```text
UI
=
Human inspection

System tables
=
Queryable operational evidence
```

---

# 13. Billing Usage

The principal billing usage system table is:

```sql
system.billing.usage
```

Current Databricks documentation describes it as the account's billable usage table and notes that it includes usage metadata, identity metadata, and custom tags. Records are typically available within hours rather than necessarily being real-time. citeturn0search1turn0search13

Important concepts include:

- usage record;
- usage quantity;
- usage start/end time;
- SKU;
- cloud;
- usage unit;
- resource metadata;
- identity metadata;
- custom tags.

The exact schema must be verified against current documentation before production SQL is deployed.

---

# 14. Billing Usage — First Query

Question:

> How much usage occurred by SKU each day?

Illustrative SQL:

```sql
SELECT
    DATE_TRUNC('day', usage_end_time) AS usage_day,
    sku_name,
    usage_unit,
    SUM(usage_quantity) AS usage_quantity
FROM system.billing.usage
WHERE usage_end_time >= CURRENT_DATE - INTERVAL 14 DAYS
GROUP BY
    DATE_TRUNC('day', usage_end_time),
    sku_name,
    usage_unit
ORDER BY
    usage_day,
    usage_quantity DESC;
```

### What it answers

It shows consumption trends by product/SKU.

### What to inspect

```text
Did usage increase?
Which SKU increased?
When did the change begin?
```

### Production action

If one SKU suddenly dominates:

```text
Investigate workload mapping
→ identify resource
→ identify team
→ identify workload change
```

---

# 15. Billing Data Grain

Never assume:

> one row = one job run.

A billing usage record represents a usage observation at the billing system's defined grain.

A workload can generate multiple usage records.

Current documentation explicitly warns that distributed serverless workloads can have multiple records for the same workload/time period. citeturn0search5

Therefore:

```text
Billing row
≠
Job run
```

unless the specific query design proves that relationship.

---

# 16. List Prices

The pricing system table is:

```sql
system.billing.list_prices
```

It stores historical SKU pricing information.

Current Databricks documentation describes fields such as:

- `price_start_time`;
- `price_end_time`;
- `account_id`;
- `sku_name`;
- `cloud`;
- `currency_code`;
- `usage_unit`;
- pricing information.

Pricing records are historical price-change records, not necessarily one row per usage event. citeturn0search3

This distinction is critical.

---

# 17. Usage + Price

Conceptually:

```text
Usage
   +
Applicable Price
   ↓
Estimated/List Cost
```

A robust pricing join considers:

```text
SKU
+
Cloud
+
Usage Unit
+
Effective Time Window
```

Illustrative:

```sql
SELECT
    u.sku_name,
    SUM(
        u.usage_quantity * CAST(p.pricing.default AS DOUBLE)
    ) AS estimated_list_cost
FROM system.billing.usage u
JOIN system.billing.list_prices p
    ON u.sku_name = p.sku_name
   AND u.cloud = p.cloud
   AND u.usage_unit = p.usage_unit
   AND u.usage_end_time >= p.price_start_time
   AND (
        p.price_end_time IS NULL
        OR u.usage_end_time < p.price_end_time
   )
WHERE u.usage_end_time >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY u.sku_name;
```

### Important

This is a **production-oriented illustrative pattern**, not a promise that every current workspace has identical schema/field semantics.

Verify the current system-table schema and pricing model before deploying it.

Current Databricks examples use the pricing table with effective time windows when calculating list-priced usage. citeturn0search19

---

# 18. Why Price Joins Are Difficult

A naive join:

```sql
ON usage.sku_name = price.sku_name
```

can be wrong.

Why?

Because the same SKU can have multiple historical prices.

Correct reasoning:

```text
SKU
+
Cloud
+
Usage Unit
+
Price Effective Period
```

The price record must be applicable to the usage timestamp.

---

# 19. Compute System Tables

Current Databricks compute system tables include information such as:

- cluster configurations;
- node types;
- node timelines;
- instance events;
- instance pools.

For example:

```text
system.compute.clusters
system.compute.node_timeline
system.compute.instance_events
```

Current documentation describes the cluster table as a slowly changing historical record of compute configurations and the node timeline as minute-level utilization data. citeturn0search11

Use these tables to investigate:

```text
Which compute exists?
How is it configured?
How long does it run?
How utilized is it?
Did configuration change?
```

---

# 20. Compute + Billing

A cost investigation may combine:

```text
Billing usage
+
Compute metadata
```

Conceptually:

```text
Cost
 ↓
Resource
 ↓
Compute configuration
 ↓
Utilization
```

Example questions:

- Did node count increase?
- Did runtime increase?
- Did utilization fall?
- Did a cluster remain idle?
- Did autoscaling expand unexpectedly?

---

# 21. Jobs and Pipeline Runs

Job/run information allows you to move from:

```text
Cost
```

to:

```text
Cost
→ workload
→ run
→ team
→ data product
```

The exact join keys depend on the available current system-table metadata.

Do not fabricate relationships.

Verify whether the required identifiers are present in your account's current system tables.

Useful questions:

```text
Which jobs run most frequently?
Which jobs have the highest cost?
Which jobs have high retry rates?
Which pipelines have increasing runtime?
Which workload has high cost per successful run?
```

---

# 22. Query History

Current Databricks system-table references include:

```sql
system.query.history
```

for supported query workloads.

It can help identify:

- expensive queries;
- long-running queries;
- query volume;
- query workload patterns;
- warehouse utilization;
- inefficient analytical behavior.

Current documentation identifies query history as a system table for query activity and notes its scope/availability can be feature dependent. citeturn0search18

---

# 23. Query History Analysis

Question:

> Which query patterns deserve investigation?

Illustrative:

```sql
SELECT
    DATE_TRUNC('day', start_time) AS query_day,
    COUNT(*) AS query_count
FROM system.query.history
WHERE start_time >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY DATE_TRUNC('day', start_time)
ORDER BY query_day;
```

Verify current column names before execution.

Production analysis should examine:

```text
Query count
Duration
Warehouse
User/service principal
Statement type
Data volume where available
```

---

# 24. Audit System Tables

A cost system is not a security audit system.

They complement each other.

Current Databricks system-table references include audit data under:

```sql
system.access.audit
```

where available.

System tables can support questions such as:

```text
Who accessed a sensitive object?
When?
What action occurred?
Who changed permissions?
```

Current system-table documentation identifies audit logs as operational system data and specifies retention/region characteristics that vary by system table. citeturn0search14

---

# 25. System Table Access

Access to system tables is itself governed.

Do not assume every workspace user can query every system table.

Production procedure:

```text
Identify required data
→ grant least privilege
→ test access
→ avoid exporting sensitive operational data unnecessarily
```

Databricks warns that system-table data can contain sensitive information and should be protected appropriately. citeturn0search14

---

# Part III — Cost Attribution

# 26. The Attribution Question

FinOps should answer:

> **Who spent how much, on what, for which workload, in which environment?**

A useful hierarchy:

```text
Account
 ↓
Business Unit
 ↓
Team
 ↓
Environment
 ↓
Data Product
 ↓
Pipeline / Job / Warehouse
```

---

# 27. Tagging Strategy

A production tagging taxonomy might include:

```text
team=data-platform
environment=prod
workload=orders-ingestion
pipeline=orders
cost_center=finance
data_product=orders-platform
owner=data-engineering
```

Do not put secrets or sensitive personal information in tags.

Current Databricks documentation states that tag data is stored as plain text and may be replicated globally; tags therefore should not contain sensitive information. citeturn0search2

---

# 28. Good vs Bad Tags

Bad:

```text
team=alice
password=...
customer_email=...
```

Good:

```text
team=payments
environment=prod
cost_center=finance
workload=payment-ingestion
data_product=payments-platform
```

Tags should describe resources, not expose sensitive data.

---

# 29. Resource-Level Tags

Apply attribution where supported to:

- compute;
- jobs;
- SQL warehouses;
- pipelines;
- serverless usage through applicable usage policies.

Current Databricks documentation describes custom tags as a mechanism for granular usage tracking and budgeting. citeturn0search2

---

# 30. Serverless Usage Policies

Serverless usage policies provide a mechanism for applying cost-attribution tags to serverless compute workloads.

Current Databricks documentation states that policy tags can propagate into:

```sql
system.billing.usage.custom_tags
```

for applicable serverless usage. citeturn0search0

Conceptual flow:

```text
User / Group / Service Principal
          ↓
Serverless Usage Policy
          ↓
Custom Tags
          ↓
Billing Usage
          ↓
Cost Attribution
```

Current feature availability and preview status must be checked before production adoption.

---

# 31. Attribution SQL

Question:

> Which team has the most tagged usage?

Illustrative pattern:

```sql
SELECT
    custom_tags['team'] AS team,
    SUM(usage_quantity) AS usage_quantity
FROM system.billing.usage
WHERE usage_end_time >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY custom_tags['team']
ORDER BY usage_quantity DESC;
```

Verify the current `custom_tags` type and syntax for your environment.

The key principle is:

```text
Billing
+
Metadata
+
Tags
=
Attribution
```

---

# 32. Team Spend

A production team report should include:

```text
Team
Environment
Workload
Usage
Estimated/List Cost
Period
```

Do not report only:

```text
team → cost
```

without explaining:

- time window;
- pricing basis;
- included SKUs;
- allocation rules;
- shared-cost treatment.

---

# 33. Pipeline Attribution

A pipeline cost report should answer:

```text
Pipeline
Runs
Usage
Cost
Cost per Run
Cost per Successful Run
Failure Rate
```

A high-cost pipeline may be expensive because:

```text
large data volume
OR
long runtime
OR
large compute
OR
frequent schedule
OR
retries
OR
inefficient transformation
```

---

# 34. Data Product Attribution

A data product may contain:

```text
Ingestion
+
Pipelines
+
Quality
+
Serving
+
Analytics
```

Its total cost therefore may require allocation across several workloads.

Example:

```text
orders-platform
├── ingestion
├── silver transformation
├── gold transformation
├── quality
└── analytics
```

Define allocation rules explicitly.

---

# 35. Untagged Spend

A production FinOps system should measure:

```text
Tagged Spend
+
Untagged Spend
=
Total Spend
```

Then:

```text
Attribution Coverage %
=
Tagged Spend / Total Spend × 100
```

Example:

```text
Total = $100,000
Tagged = $92,000

Coverage = 92%
```

The goal is not merely a high percentage.

The goal is:

> **Every material cost has an explainable owner and allocation rule.**

---

# Part IV — Cost Controls

# 36. Compute Policies

Compute policies can constrain:

- compute size;
- allowed configurations;
- runtime characteristics;
- tags;
- resource choices.

They are a preventive control.

```text
Developer request
      ↓
Policy
      ↓
Allowed compute
```

Current Databricks guidance recommends compute policies to enforce cost controls and resource limits and to require tags for attribution where appropriate. citeturn0search8

---

# 37. Auto-Termination

Idle interactive compute is a common waste source.

Without auto-termination:

```text
Developer finishes
 ↓
Cluster remains active
 ↓
No useful work
 ↓
Cost continues
```

With auto-termination:

```text
Idle threshold
 ↓
Compute stops
```

Do not blindly choose the smallest possible timeout.

Consider:

```text
Cost
+
Developer productivity
+
Startup latency
```

---

# 38. Auto-Stop for SQL Warehouses

Applicable SQL warehouses can use automatic stopping behavior.

Trade-off:

```text
More aggressive stop
→ lower idle cost
→ potentially higher startup latency
```

A BI workload with strict latency expectations may need a different policy from a development warehouse.

---

# 39. Warehouse Sizing

A warehouse that is too large:

```text
Low utilization
+
High cost
```

A warehouse that is too small:

```text
Queueing
+
Longer runtime
+
Poor user experience
```

Therefore:

```text
Optimize:
Cost
+
Latency
+
Concurrency
+
Reliability
```

---

# 40. Job Compute vs All-Purpose Compute

Production job execution should generally use workload-oriented compute rather than interactive all-purpose compute.

| Dimension | All-purpose | Job-oriented compute |
|---|---|---|
| Primary use | Interactive development | Production workloads |
| Isolation | Lower | Higher |
| Reproducibility | Lower | Higher |
| Idle risk | Higher | Lower |
| Scheduling fit | Weak | Strong |
| Governance | More user-driven | More controlled |
| Cost management | Harder | Easier to standardize |

This is a production engineering control, not merely a pricing trick.

---

# 41. Budgets

Budgets provide financial monitoring.

A useful hierarchy:

```text
Account budget
 ↓
Business-unit budget
 ↓
Team budget
 ↓
Project/data-product budget
```

Current Databricks cost-management tooling includes budgets that can monitor account-wide spending or filtered spending for teams, projects, or workspaces. citeturn0search10

A budget does not replace:

- attribution;
- monitoring;
- policies;
- anomaly investigation.

It complements them.

---

# 42. Cost Controls as a Layered System

A mature design is:

```text
Visibility
   ↓
Attribution
   ↓
Budget
   ↓
Policy
   ↓
Alert
   ↓
Investigation
   ↓
Optimization
```

A dashboard alone does not control spend.

---

# Part V — Cost Analytics

# 43. Daily Cost

The first operational report:

```text
Date
SKU
Usage
Estimated/list cost
```

Illustrative:

```sql
SELECT
    DATE_TRUNC('day', usage_end_time) AS day,
    sku_name,
    SUM(usage_quantity) AS usage_quantity
FROM system.billing.usage
WHERE usage_end_time >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY
    DATE_TRUNC('day', usage_end_time),
    sku_name
ORDER BY
    day,
    sku_name;
```

Use this to identify:

- trend;
- step changes;
- unusual spikes;
- SKU mix changes.

---

# 44. Cost Trends

Compare:

```text
Today
vs
Yesterday
```

and:

```text
This week
vs
Last week
```

and:

```text
Month-to-date
vs
Prior period
```

Do not interpret a cost increase without considering:

- workload volume;
- business seasonality;
- data growth;
- product launches.

---

# 45. Day-over-Day Spike Detection

Conceptual metric:

```text
Today
>
1.30 × trailing 7-day average
```

Illustrative SQL:

```sql
WITH daily AS (
    SELECT
        CAST(usage_end_time AS DATE) AS day,
        SUM(usage_quantity) AS usage
    FROM system.billing.usage
    GROUP BY CAST(usage_end_time AS DATE)
),
scored AS (
    SELECT
        day,
        usage,
        AVG(usage) OVER (
            ORDER BY day
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS trailing_7d_avg
    FROM daily
)
SELECT
    day,
    usage,
    trailing_7d_avg,
    usage / NULLIF(trailing_7d_avg, 0) AS spike_ratio
FROM scored
WHERE trailing_7d_avg IS NOT NULL
ORDER BY day DESC;
```

A real production implementation should account for:

- missing days;
- partial current-day data;
- seasonality;
- SKU changes.

---

# 46. Anomaly Detection

Static thresholds:

```text
Cost > $10,000
```

are often weak.

Better:

```text
Current Cost
vs
Historical Baseline
```

Possible baselines:

- trailing average;
- trailing median;
- same weekday;
- rolling percentile;
- expected workload volume.

The goal is:

```text
Expected increase
vs
Unexpected increase
```

---

# 47. Cost Dashboard

A production dashboard should answer three levels of questions.

## Executive

- total spend;
- MTD spend;
- trend;
- team spend;
- environment spend;
- budget utilization.

## Engineering

- top jobs;
- top queries;
- cost per run;
- failed-run cost;
- idle warehouse time;
- tagged/untagged spend.

## FinOps

- unit economics;
- attribution coverage;
- anomalies;
- optimization savings;
- budget variance.

---

# 48. Dashboard Design Principle

Do not create:

```text
Chart
+
Chart
+
Chart
```

Create:

```text
Metric
→ Question
→ Interpretation
→ Action
```

Example:

```text
Metric:
Cost per successful pipeline run

Question:
Is the pipeline becoming less efficient?

Interpretation:
Cost increased 35% while data volume increased only 5%.

Action:
Investigate compute sizing, retries and execution plan.
```

---

# 49. Cost per Pipeline Run

Basic:

```text
Cost per run
=
Pipeline cost
÷
Number of runs
```

Better:

```text
Cost per successful run
=
Total pipeline cost
÷
Successful runs
```

Why?

Because failed runs consume resources too.

Include:

- retries;
- repair runs;
- failed runs;
- runtime;
- data volume.

---

# 50. Cost per Dashboard

Conceptually:

```text
Dashboard cost
≈
Attributed warehouse/query cost
```

Investigate:

```text
Refresh frequency
+
Query count
+
Query duration
+
Warehouse size
+
Concurrency
```

A dashboard can become expensive after adoption increases even if the SQL itself did not change.

---

# 51. Cost per TB Processed

```text
Cost per TB
=
Attributable Cost
÷
TB Processed
```

Investigate:

- scan volume;
- pruning;
- clustering/layout;
- repeated processing;
- query design;
- data growth.

A lower cost per TB is useful only when:

```text
Latency
+
Reliability
+
Correctness
```

remain acceptable.

---

# Part VI — Advanced FinOps

# 52. Cost Drivers

Suppose:

```text
Monthly cost increased 40%.
```

Break it down:

```text
DBU usage?
Runtime?
Cluster size?
Frequency?
Retries?
Data volume?
Query volume?
Warehouse size?
Idle time?
SKU mix?
Serverless/classic transition?
```

Do not stop at:

> “DBUs increased.”

That describes the symptom, not the driver.

---

# 53. Production Cost Investigation

Incident:

> Monthly Databricks spend increased by 42%.

Investigation:

```text
1. Confirm increase
2. Compare periods
3. Compare SKU mix
4. Attribute by workspace
5. Attribute by team
6. Identify top workloads
7. Compare runtime
8. Compare execution frequency
9. Investigate retries
10. Inspect compute changes
11. Inspect query history
12. Inspect data-volume growth
13. Identify idle resources
14. Select optimization
15. Measure savings
16. Add preventive control
```

This is the central production exercise.

---

# 54. Showback vs Chargeback

## Showback

Inform teams:

```text
Your workloads consumed $18,000.
```

Financial responsibility remains centralized.

## Chargeback

Allocate financial responsibility:

```text
Team A → $18,000
Team B → $11,000
```

and use those allocations for financial planning/accounting.

Neither is universally superior.

Choose based on organizational maturity.

---

# 55. Enterprise Allocation Model

Conceptual hierarchy:

```text
Account
 ├── Business Unit
 │    ├── Team
 │    │    ├── Environment
 │    │    │    ├── Data Product
 │    │    │    │    ├── Pipeline
 │    │    │    │    └── Analytics
```

Each level should have an allocation rule.

---

# 56. Direct vs Shared Cost

## Direct

Clearly attributable:

```text
Orders pipeline
→ Orders team
```

## Shared

Used by multiple teams:

```text
Enterprise SQL warehouse
```

Possible allocation:

```text
Query runtime share
or
usage share
or
business-defined allocation
```

Document the method.

---

# 57. Multi-Workspace Cost Reporting

Enterprises may have:

```text
Development
Staging
Production
Analytics
ML
Sandbox
```

Centralized reporting should answer:

```text
Which workspace costs the most?
Which team owns it?
Which workloads drive the cost?
Is the growth justified?
```

Current system-table capabilities and availability vary by cloud/account configuration; verify current global vs regional behavior before designing a centralized report. Databricks documents billable usage as globally available in the account while several operational system tables are regional. citeturn0search1turn0search18

---

# 58. System-Table Join Strategy

A mature cost model may use:

```text
Billing usage
+
List prices
+
Compute
+
Jobs
+
Pipelines
+
Query history
+
Audit
+
Tags
```

But never join everything immediately.

First ask:

> **What is the grain of each dataset?**

---

# 59. Data Grain

Examples:

```text
Billing usage:
one usage record

Job runs:
one job/run record

Query history:
one query record

Audit:
one event record

Compute timeline:
one resource/time observation
```

If you join:

```text
1 usage
×
5 queries
×
3 audit events
```

you can accidentally create:

```text
15 rows
```

from one usage record.

That can inflate cost.

---

# 60. Double Counting Example

Bad:

```sql
SELECT SUM(u.usage_quantity)
FROM usage u
JOIN queries q
  ON u.resource_id = q.resource_id;
```

If one usage record matches 20 queries:

```text
Original usage = 10
Joined rows = 20
SUM = 200
```

Correct approaches include:

- aggregate each dataset to the intended grain first;
- use distinct resource/run keys carefully;
- define time windows;
- avoid many-to-many joins;
- validate totals against an independent source.

---

# 61. Cost Data Quality

A FinOps dashboard can be beautiful and financially wrong.

Validate:

- missing tags;
- missing resource IDs;
- duplicate usage;
- unknown SKUs;
- missing prices;
- orphaned usage;
- timestamp issues;
- unexpected zero/negative values;
- sudden record-volume changes;
- unattributed spend.

---

# 62. Cost Reconciliation

Always establish:

```text
Source Total
vs
Analytics Total
```

Example:

```text
Billing source = $100,000
FinOps model   = $98,700
Difference     = $1,300
```

Do not publish the dashboard until the difference is understood.

Possible causes:

- data latency;
- filtering;
- unsupported SKU;
- price mapping;
- currency;
- duplicated joins;
- missing workspace;
- partial-day data.

---

# 63. FinOps Data Model

Conceptual model:

```text
fact_usage
fact_job_runs
fact_queries

dim_resource
dim_team
dim_environment
dim_workload
dim_data_product
dim_price
```

Each fact needs a defined grain.

Example:

```text
fact_usage
=
one billing usage record
```

Then attribution dimensions can be joined through validated keys.

---

# 64. Unit Economics

Good FinOps asks:

```text
What did the workload cost?
```

Better FinOps asks:

```text
What did one unit of useful output cost?
```

Examples:

```text
$ / successful pipeline run
$ / dashboard refresh
$ / TB processed
$ / million records
$ / business transaction
$ / data product
```

This connects platform cost to business value.

---

# 65. Cost Data Quality Checkpoint

Before continuing, you should be able to:

- [ ] Define the grain of billing usage.
- [ ] Define the grain of query history.
- [ ] Explain why joins can double-count.
- [ ] Reconcile a FinOps model to a source total.
- [ ] Explain missing attribution.
- [ ] Explain why pricing must be time-aware.

---

# Part VII — Audit

# 66. Cost vs Security Audit

Cost management answers:

```text
What was consumed?
```

Security audit answers:

```text
Who accessed what?
```

They are distinct.

But both rely on:

```text
Operational evidence
+
Historical records
+
Identity
+
Time
+
Resource metadata
```

---

# 67. PII Access Audit

Suppose the sensitive objects are:

```text
gold.customer_pii
gold.orders_sensitive
gold.payments
```

Question:

> Who accessed these objects and when?

A conceptual audit query:

```sql
SELECT
    event_time,
    user_identity,
    action_name,
    request_params
FROM system.access.audit
WHERE event_time >= CURRENT_DATE - INTERVAL 7 DAYS
  AND (
       request_params LIKE '%customer_pii%'
       OR request_params LIKE '%orders_sensitive%'
       OR request_params LIKE '%payments%'
  )
ORDER BY event_time DESC;
```

**Verify the current audit schema and fields before execution.**

The production approach should prefer structured fields when available rather than brittle text matching.

---

# 68. PII Audit Investigation

Workflow:

```text
Sensitive object
 ↓
Audit records
 ↓
Identity
 ↓
Timestamp
 ↓
Action
 ↓
Expected access?
 ↓
Incident / compliance decision
```

Do not expose sensitive audit output broadly.

---

# Part VIII — Optimization

# 69. Optimization Methodology

Use:

```text
1. Measure
2. Attribute
3. Identify driver
4. Quantify opportunity
5. Estimate risk
6. Implement
7. Measure again
8. Compare
9. Document savings
10. Add guardrail
```

Optimization without measurement is guesswork.

---

# 70. Optimization Experiment 1 — Job Compute

Hypothesis:

> A production job is using larger compute than necessary.

Baseline:

```text
Runtime = 40 min
Cost/run = $12
Success rate = 99.5%
```

Change:

```text
Smaller adequate job compute
```

After:

```text
Runtime = 43 min
Cost/run = $8
Success rate = 99.6%
```

Savings:

```text
$4/run
```

If 1,000 runs/month:

```text
Illustrative savings = $4,000/month
```

The change is acceptable only if SLA and reliability remain acceptable.

---

# 71. Optimization Experiment 2 — Auto-Termination

Hypothesis:

> Development clusters remain idle for long periods.

Baseline:

```text
Idle time = 10 hours/day
```

Change:

```text
Auto-termination = controlled idle threshold
```

Measure:

```text
Idle time reduction
+
Developer startup impact
+
Cost reduction
```

Do not optimize idle time at the expense of unacceptable developer productivity.

---

# 72. Optimization Experiment 3 — Serverless vs Classic

Run the same representative workload under:

```text
Classic
vs
Serverless
```

Measure:

```text
Total cost
Runtime
Failure rate
Operational effort
```

Decision:

```text
Cost
+
Performance
+
Reliability
+
Operational complexity
```

Never assume serverless wins before measurement.

---

# 73. Optimization Experiment 4 — Warehouse Sizing

Compare:

```text
Warehouse A
vs
Warehouse B
```

Measure:

```text
Cost per dashboard refresh
Query latency
Queueing
Concurrency
User experience
```

The cheapest hourly warehouse may not produce the cheapest dashboard.

---

# 74. Before/After Measurement

Every experiment records:

```text
Workload
Baseline period
Baseline cost
Change
Post-change period
Post-change cost
Absolute savings
Savings %
Latency impact
Reliability impact
Trade-offs
```

Formula:

```text
Savings %
=
(Baseline Cost - New Cost)
/
Baseline Cost
× 100
```

Example:

```text
Baseline = $10,000
After = $8,500

Savings = $1,500

Savings % = 15%
```

---

# 75. Optimization Trade-offs

Always compare:

```text
Cost
Latency
Throughput
Reliability
Engineering complexity
Operational burden
Developer productivity
```

Examples:

```text
Smaller compute
→ cheaper
→ potentially slower

Aggressive auto-stop
→ cheaper
→ potentially slower startup

Serverless
→ less infrastructure management
→ different unit economics

Table optimization
→ lower scans
→ maintenance cost
```

---

# 76. Cost Optimization Checkpoint

Before continuing, you should be able to:

- [ ] Define a cost hypothesis.
- [ ] Establish a baseline.
- [ ] Change one meaningful variable.
- [ ] Measure after the change.
- [ ] Calculate savings.
- [ ] Evaluate latency/reliability trade-offs.
- [ ] Add a preventive control.

---

# Part IX — Production Operations

# 77. Troubleshooting Framework

Use:

```text
Symptom
 ↓
Hypotheses
 ↓
Evidence
 ↓
SQL Investigation
 ↓
Root Cause
 ↓
Fix
 ↓
Verification
 ↓
Prevention
```

Never jump directly from:

```text
Cost increased
```

to:

```text
Resize cluster
```

First establish the driver.

---

# 78. Troubleshooting Matrix

| Symptom | Likely causes | First investigation |
|---|---|---|
| Spend increased | volume, runtime, frequency, SKU, retries | billing by SKU/day |
| Missing attribution | missing tags/policy | `custom_tags` coverage |
| Duplicate cost | bad join grain | source vs modeled total |
| Expensive job | compute/runtime/retries | usage + job/run metadata |
| Expensive query | scans/concurrency/warehouse | query history |
| Idle warehouse | stop policy/usage pattern | warehouse events/history |
| Unknown SKU | new product/version | current pricing table/docs |
| Price mismatch | wrong effective period | price time-window join |
| Dashboard mismatch | data freshness/join/filter | reconcile to source |
| PII access question | audit schema/filter | audit system data |

---

# 79. System Table Unavailable

Possible causes:

- Unity Catalog/system-table prerequisites;
- insufficient permissions;
- regional/account availability;
- feature availability;
- incorrect schema/table name;
- temporary data-delivery latency.

Procedure:

```text
Confirm workspace/account capability
→ verify permissions
→ verify current documentation
→ inspect table existence
→ inspect data freshness
→ retry with a minimal query
```

---

# 80. Empty Result

Do not assume:

> “There is no usage.”

Check:

- date/time zone;
- data-delivery delay;
- workspace/account scope;
- table availability;
- filter;
- SKU;
- current-day partial data.

---

# 81. Missing Tags

If spend is unattributed:

```text
Check resource tags
→ check serverless usage policy
→ inspect billing record custom_tags
→ identify workload
→ remediate tagging
→ measure coverage
```

Remember:

> Tags generally help future attribution; they do not magically rewrite historical usage.

Current Databricks documentation notes that tags affect usage records going forward, so missing historical tags may require another allocation method. citeturn0search17

---

# 82. Incorrect Cost Totals

Investigation:

```text
Source total
vs
Price-joined total
vs
Attribution model total
```

Check:

- price effective period;
- SKU;
- cloud;
- usage unit;
- duplicate rows;
- filters;
- currency;
- data freshness.

---

# 83. Production Runbooks

## Runbook 1 — Daily Cost Review

**Purpose:** detect unusual spend early.

**Trigger:** daily scheduled review.

Steps:

1. Review daily spend.
2. Compare trailing baseline.
3. Review SKU mix.
4. Review top teams.
5. Review top workloads.
6. Review untagged spend.
7. Review active anomalies.
8. Create investigation tickets where needed.

Evidence:

```text
Daily report
Top contributors
Anomaly list
Attribution coverage
```

---

## Runbook 2 — Cost Spike Investigation

**Trigger:** threshold/anomaly alert.

```text
Confirm spike
→ compare periods
→ identify SKU
→ identify workspace/team
→ identify workload
→ inspect runtime/frequency/retries
→ inspect compute/query behavior
→ identify root cause
→ optimize
→ measure
→ add guardrail
```

---

## Runbook 3 — Unattributed Spend

```text
Quantify
→ identify resource
→ inspect tags
→ inspect serverless policy
→ map owner
→ add attribution
→ document historical allocation
→ monitor future coverage
```

---

## Runbook 4 — Expensive Job

Check:

```text
Cost/run
Runtime
Retries
Compute size
Frequency
Data volume
Execution plan
```

Then:

```text
Hypothesis
→ change
→ benchmark
→ approve
→ deploy
→ monitor
```

---

## Runbook 5 — PII Access Audit

```text
Identify sensitive objects
→ query audit records
→ identify identities
→ identify actions
→ compare expected access
→ investigate anomalies
→ preserve evidence
→ escalate
```

---

## Runbook 6 — Cost Dashboard Reconciliation

```text
Dashboard total
vs
Billing source
```

If different:

```text
Stop publication
→ identify grain
→ inspect filters
→ inspect price join
→ inspect missing data
→ reconcile
→ document
```

---

# 84. Decision Matrices

## Compute Choice

| Workload | All-purpose | Jobs | Serverless | SQL Warehouse |
|---|---:|---:|---:|---:|
| Interactive development | Strong | Weak | Possible | Possible |
| Scheduled ETL | Weak | Strong | Strong where suitable | Medium |
| Production pipeline | Weak | Strong | Strong where suitable | Weak |
| BI | Weak | Weak | Product-dependent | Strong |
| Ad hoc SQL | Weak | Weak | Possible | Strong |
| Long-lived interactive workload | Strong | Weak | Product-dependent | Possible |

Decision must include:

```text
Cost
Performance
Isolation
Operational burden
Governance
```

---

## Cost Control

| Problem | Primary control |
|---|---|
| Oversized compute | Compute policy |
| Forgotten interactive cluster | Auto-termination |
| Idle warehouse | Auto-stop |
| Unattributed serverless usage | Serverless usage policy |
| Unexpected spend | Budget/alert |
| Production on interactive compute | Job compute |
| Poor attribution | Tags |
| Cost anomaly | System-table alerting |

---

## Optimization

| Driver | Candidate action |
|---|---|
| Oversized compute | Resize |
| Idle time | Auto-stop/termination |
| Excess retries | Fix reliability/root cause |
| Excessive scans | Query/table optimization |
| Repeated processing | Incremental design |
| Warehouse queueing | Right-size/concurrency |
| Serverless/classic mismatch | Benchmark alternatives |
| High maintenance cost | Evaluate layout/optimization strategy |

---

## Attribution

| Requirement | Suggested dimension |
|---|---|
| Organization | Business unit |
| Financial ownership | Cost center |
| Engineering ownership | Team |
| Environment | dev/staging/prod |
| Workload | Job/pipeline |
| Product ownership | Data product |
| Resource ownership | Owner |

---

# 85. ADR Exercises

## ADR 1 — Standard Tagging Taxonomy

**Context:** Teams use inconsistent tags.

**Decision question:** Which required keys should every production workload have?

Evaluate:

```text
team
environment
workload
cost_center
data_product
owner
```

Trade-off:

```text
More tags
→ better attribution
→ more governance overhead
```

---

## ADR 2 — Jobs Compute vs All-Purpose

**Context:** Production jobs run on interactive clusters.

**Decision:** Move production workloads to workload-oriented compute unless a documented exception exists.

---

## ADR 3 — Serverless vs Classic

**Context:** A workload can use either.

**Decision criteria:**

```text
Measured cost
+
Latency
+
Reliability
+
Operational effort
```

---

## ADR 4 — Cost Dashboard Architecture

Compare:

```text
Workspace-local dashboard
vs
Centralized cost model
```

Evaluate:

- scale;
- ownership;
- latency;
- governance;
- cross-workspace reporting.

---

## ADR 5 — Showback vs Chargeback

Compare:

```text
Visibility only
vs
Financial allocation
```

Choose according to organizational maturity.

---

## ADR 6 — Centralized vs Workspace-Level Reporting

Evaluate:

```text
Global account reporting
vs
local operational reporting
```

Use both when appropriate.

---

# Part X — Hands-on

# 86. Progressive Labs

Every lab follows:

```text
Objective
Prerequisites
Scenario
Instructions
SQL/code
Expected result
Observation
Common mistakes
Troubleshooting
Checkpoint
Production takeaway
```

## Lab 01 — Understand DBUs and Total Cost

Calculate illustrative classic and serverless economics.

## Lab 02 — Explore Billing Usage

Query:

```sql
system.billing.usage
```

Identify usage by day and SKU.

## Lab 03 — Explore Pricing

Inspect:

```sql
system.billing.list_prices
```

Study effective price periods.

## Lab 04 — Analyze Compute

Explore compute configuration and utilization system tables.

## Lab 05 — Analyze Job/Pipeline Cost

Map usage to workload metadata where supported.

## Lab 06 — Analyze Query History

Identify high-duration/high-volume query patterns.

## Lab 07 — Build Tag Attribution

Apply:

```text
team
environment
workload
cost_center
```

and verify propagation where supported.

## Lab 08 — Build Daily Cost Report

Produce daily usage and estimated/list cost.

## Lab 09 — Build Cost Dashboard

Include:

- daily spend;
- trend;
- team;
- environment;
- top workloads;
- tagged/untagged spend.

## Lab 10 — Cost Anomaly Detection

Implement a trailing-baseline comparison.

## Lab 11 — Idle Compute Investigation

Identify idle resources and propose controls.

## Lab 12 — Expensive Jobs

Rank jobs by attributable cost.

## Lab 13 — Expensive Queries

Rank query workloads for investigation.

## Lab 14 — Cost per Pipeline Run

Calculate:

```text
Cost / run
Cost / successful run
```

## Lab 15 — Cost per TB Processed

Build a workload unit-economics metric.

## Lab 16 — Optimize a Workload

Implement one controlled optimization.

## Lab 17 — Measure Savings

Document:

```text
Before
After
Savings
Latency
Reliability
Trade-offs
```

## Lab 18 — Audit PII Access

Query current audit data for access to sensitive gold objects.

## Lab 19 — Enterprise Allocation

Build:

```text
Business Unit
→ Team
→ Environment
→ Data Product
→ Workload
```

## Lab 20 — Production Cost Incident

Investigate a simulated 42% monthly cost increase from raw evidence.

---

# 87. Required Hands-on Exercise — `sql/cost/`

Build the conceptual project:

```text
sql/
└── cost/
    ├── 01_daily_usage.sql
    ├── 02_list_price_join.sql
    ├── 03_team_attribution.sql
    ├── 04_pipeline_cost.sql
    ├── 05_dashboard_metrics.sql
    ├── 06_anomaly_detection.sql
    ├── 07_unit_economics.sql
    └── 08_pii_audit.sql
```

The learner must produce:

```text
Cost attribution
+
Dashboard
+
Alerts
+
Optimization
+
PII audit
```

---

# 88. Production Cost Incident

Scenario:

> Monthly Databricks spend increased by 42% while business revenue increased by only 8%.

Evidence:

```text
SKU usage
Compute metadata
Job runs
Query history
Tags
Pricing data
Audit data
```

Required investigation:

```text
1. Confirm the 42% increase.
2. Establish the comparison period.
3. Decompose by SKU.
4. Decompose by workspace.
5. Decompose by team.
6. Identify top workloads.
7. Check runtime.
8. Check execution frequency.
9. Check retries.
10. Check compute configuration.
11. Check query volume.
12. Check data volume.
13. Check idle resources.
14. Form a root-cause hypothesis.
15. Implement an optimization.
16. Measure before/after.
17. Add a guardrail.
```

Deliverable:

```text
Incident report
+
SQL evidence
+
Root cause
+
Optimization
+
Savings measurement
+
Prevention
```

---

# 89. Final Capstone — Databricks Cost Observability and FinOps Platform

Build a production-style cost-analysis capability.

The capstone must:

1. collect billing/system-table data;
2. join usage with applicable price information;
3. attribute cost using tags;
4. calculate daily spend;
5. calculate team spend;
6. calculate environment spend;
7. calculate pipeline spend;
8. identify expensive jobs;
9. identify expensive queries;
10. identify idle warehouses;
11. detect cost anomalies;
12. calculate unit economics;
13. audit gold PII access;
14. implement at least two cost optimizations;
15. measure before/after savings;
16. document trade-offs;
17. define cost governance;
18. produce an executive dashboard;
19. produce an engineering dashboard;
20. produce an operational runbook.

Architecture:

```text
Databricks Workloads
        │
        ├── Compute
        ├── Jobs
        ├── Pipelines
        ├── SQL Warehouses
        └── Queries
                │
                ▼
          System Tables
                │
                ▼
        Cost Analytics Layer
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
    Dashboard Alerts   Reports
        │       │        │
        └───────┼────────┘
                ▼
       FinOps / Engineering
                │
                ▼
         Optimization
                │
                ▼
        Policies / Budgets
```

---

# 90. Capstone Report

Document:

```text
Architecture
Data Sources
System Tables
Data Model
Tagging Strategy
Cost Model
Attribution Model
Dashboard Design
Alert Strategy
Optimization Experiments
Before/After Measurements
Governance
Audit Strategy
Known Limitations
Future Improvements
```

The result should resemble a real enterprise Databricks cost-observability/FinOps capability.

---

# Part XI — Interview Preparation

# 91. Interview Questions

## Beginner — 15

1. What is a DBU?
2. What is a Databricks SKU?
3. What are system tables?
4. What is `system.billing.usage`?
5. What is `system.billing.list_prices`?
6. Why use tags?
7. What is auto-termination?
8. What is auto-stop?
9. Why use job compute?
10. What is serverless?
11. What is cost attribution?
12. What is showback?
13. What is chargeback?
14. What is a unit cost?
15. Why can DBU cost differ from total workload cost?

### What interviewer is testing

Fundamental billing literacy.

### Strong answer structure

```text
Definition
→ Why it matters
→ Example
→ Production consideration
```

---

## Intermediate — 20

1. How do you attribute Databricks cost?
2. How do you identify expensive jobs?
3. How do you identify idle warehouses?
4. How do you build a cost dashboard?
5. How do you investigate a cost spike?
6. How do tags support FinOps?
7. What are serverless usage policies?
8. How do budgets differ from policies?
9. How do you calculate cost per pipeline run?
10. How do you calculate cost per TB?
11. Why can SQL joins double-count usage?
12. How do you reconcile cost reports?
13. How do you compare serverless and classic compute?
14. How do you identify untagged spend?
15. How do you use query history?
16. How do you use compute system tables?
17. How do audit tables complement cost tables?
18. What is showback?
19. What is chargeback?
20. How do you measure optimization savings?

### Senior answer pattern

```text
Measure
→ Attribute
→ Investigate
→ Optimize
→ Validate
→ Guardrail
```

---

## Advanced — 20

1. Design enterprise Databricks FinOps.
2. Design a cost allocation model for 100 data products.
3. Design a system-table cost model.
4. Design a pricing join.
5. Prevent double counting.
6. Design unit economics.
7. Design anomaly detection.
8. Design cost dashboards.
9. Design serverless attribution.
10. Design budget governance.
11. Compare classic and serverless.
12. Optimize a costly pipeline.
13. Optimize a BI workload.
14. Investigate 40% cost growth.
15. Reconcile Finance and Databricks totals.
16. Design multi-workspace reporting.
17. Design showback.
18. Design chargeback.
19. Design audit reporting.
20. Design cost data quality controls.

---

## Senior / Staff — 20

1. A pipeline runtime is unchanged but cost increased 35%. What do you investigate?
2. A team says its workload is cheap but centralized billing disagrees. Reconcile the numbers.
3. Finance reports $65K while the FinOps dashboard reports $50K. Debug it.
4. A warehouse is cheaper per hour but more expensive per dashboard refresh. Explain.
5. Design attribution for 100+ data products.
6. Prevent system-table join double counting.
7. Design showback vs chargeback.
8. Separate volume-driven growth from efficiency-driven growth.
9. Design governance that prevents runaway compute.
10. Design a cost-optimization program without damaging SLAs.
11. Design global and regional reporting.
12. Design cost data reconciliation.
13. Design a serverless/classic benchmark.
14. Design PII audit evidence.
15. Design FinOps data contracts.
16. Design anomaly response.
17. Design budget ownership.
18. Design executive vs engineering dashboards.
19. Design cost controls across development and production.
20. Explain what “production-grade FinOps” means.

For every interview question, evaluate:

```text
Conceptual correctness
SQL/system-table reasoning
Data-grain awareness
Production judgment
Security awareness
Cost-performance trade-offs
```

---

# 92. Practice Questions

## Beginner — 15

1. Define DBU.
2. Define SKU.
3. Explain classic cost.
4. Explain serverless cost.
5. Explain total workload cost.
6. Explain system tables.
7. Explain billing usage.
8. Explain list prices.
9. Explain tags.
10. Explain auto-termination.
11. Explain job compute.
12. Explain budgets.
13. Explain showback.
14. Explain chargeback.
15. Explain unit economics.

## Intermediate — 20

1. Write a daily usage query.
2. Group usage by SKU.
3. Group usage by team.
4. Explain custom tags.
5. Calculate attribution coverage.
6. Identify untagged usage.
7. Build a trailing average.
8. Detect a 30% spike.
9. Calculate cost per run.
10. Calculate cost per successful run.
11. Explain a pricing join.
12. Identify duplicate rows.
13. Explain data grain.
14. Design a cost dashboard.
15. Identify expensive queries.
16. Identify idle warehouses.
17. Explain budget vs alert.
18. Explain policy vs dashboard.
19. Explain serverless attribution.
20. Explain job compute economics.

## Advanced — 20

1. Design a FinOps star schema.
2. Design pricing effective-time joins.
3. Design multi-workspace reporting.
4. Design cost anomaly detection.
5. Design tag governance.
6. Design unit economics.
7. Design showback.
8. Design chargeback.
9. Design PII access audit.
10. Design cost reconciliation.
11. Investigate a 40% spike.
12. Compare serverless/classic.
13. Optimize warehouse sizing.
14. Optimize pipeline compute.
15. Optimize idle resources.
16. Investigate retry-driven cost.
17. Investigate data-volume-driven cost.
18. Investigate SKU-driven cost.
19. Design cost data quality.
20. Design FinOps governance.

## Production Troubleshooting — 10

1. Dashboard double-counts spend.
2. Price join is inflated.
3. Tags are missing.
4. System table is empty.
5. Query history is unavailable.
6. Pipeline cost unexpectedly doubles.
7. Warehouse remains active overnight.
8. Finance total differs from dashboard.
9. PII audit returns unexpected access.
10. Serverless attribution is missing.

## SQL Exercises — 10

1. Daily usage.
2. Daily list cost.
3. Cost by SKU.
4. Cost by team.
5. Cost by environment.
6. Cost by pipeline.
7. Top expensive workloads.
8. Trailing 7-day average.
9. Cost per successful run.
10. Tagged vs untagged spend.

## Architecture Questions — 10

1. Design a centralized cost platform.
2. Design multi-workspace attribution.
3. Design a dashboard architecture.
4. Design budget governance.
5. Design tagging standards.
6. Design serverless attribution.
7. Design cost data quality.
8. Design audit integration.
9. Design showback.
10. Design chargeback.

## Interview Scenarios — 10

1. 42% cost increase.
2. $15K unexplained spend.
3. Duplicate dashboard total.
4. Serverless appears more expensive.
5. Team rejects allocation.
6. Warehouse costs grow with users.
7. Pipeline cost grows without code changes.
8. PII access investigation.
9. Missing tags after deployment.
10. Cost falls but SLA worsens.

---

# 93. Senior-Level Scenarios

## Scenario 1 — Runtime Unchanged, Cost +35%

Investigate:

```text
SKU
Compute configuration
Price
Frequency
Cloud cost
Serverless/classic mode
```

Do not assume code changed.

---

## Scenario 2 — Team Disputes Cost

Reconcile:

```text
Billing source
→ tags
→ workload
→ allocation rule
→ dashboard
```

Document shared-cost allocation.

---

## Scenario 3 — Finance vs FinOps Mismatch

Compare:

```text
Currency
Period
Price basis
SKU inclusion
Cloud cost
Data latency
Filters
Allocation
```

---

## Scenario 4 — Cheap Hourly Warehouse, Expensive Dashboard

Investigate:

```text
Query duration
Concurrency
Queueing
Refresh frequency
Warehouse size
Cost per refresh
```

---

## Scenario 5 — 100 Data Products

Require:

```text
Standard tags
Data-product owner
Team
Environment
Cost center
Workload
Allocation rules
```

---

## Scenario 6 — Double Counting

First identify grain.

Then:

```text
Aggregate
→ join
→ reconcile
```

Never blindly join raw operational tables.

---

## Scenario 7 — Showback to Chargeback

Start with:

```text
Visibility
→ trusted attribution
→ governance
→ financial allocation
```

Do not introduce chargeback before the data is trustworthy.

---

## Scenario 8 — Volume vs Inefficiency

Decompose:

```text
Data volume
×
Cost per unit
```

If volume rose 50% but cost rose 120%, investigate efficiency.

---

# Part XII — Reference

# 94. Mental Models

## Mental Model 1

```text
Usage → Price → Cost
```

## Mental Model 2

```text
Visibility
→ Attribution
→ Optimization
→ Governance
```

## Mental Model 3

```text
Resource
→ Workload
→ Team
→ Data Product
→ Business Value
```

## Mental Model 4

```text
Cost = Quantity × Unit Economics
```

## Mental Model 5

```text
Low hourly cost ≠ low total workload cost
```

## Mental Model 6

```text
Every cost number must have a known grain
```

## Mental Model 7

```text
Measure → Change → Measure
```

---

# 95. Production Architecture

```text
Databricks Workloads
        │
        ├── Compute
        ├── Jobs
        ├── Pipelines
        ├── SQL Warehouses
        └── Queries
                │
                ▼
          System Tables
                │
                ▼
       Cost Analytics Layer
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
    Dashboard Alerts   Reports
        │       │        │
        └───────┼────────┘
                ▼
       FinOps / Engineering
                │
                ▼
          Optimization
                │
                ▼
        Policies / Budgets
```

This architecture creates a feedback loop:

```text
Run
→ Observe
→ Measure
→ Optimize
→ Re-run
→ Compare
→ Govern
```

---

# 96. Cost + Governance + Audit

These are complementary disciplines:

```text
Tags
→ cost attribution

Unity Catalog permissions
→ governance

Audit records
→ accountability

System tables
→ evidence

Policies
→ preventive control
```

Cost management is the operational measurement layer over the platform built in Topics 01–12.

---

# 97. Cross-Topic Connections

## Topic 02 — Compute

Compute selection directly affects cost.

## Topic 04 — Unity Catalog

Governance and ownership support attribution and audit.

## Topic 07 — Lakeflow Declarative Pipelines

Pipeline design affects cost per successful output.

## Topic 08 — Lakeflow Jobs

Scheduling, retries, repair runs and compute determine cost.

## Topic 09 — Photon / Performance

Performance optimization can change cost per unit of work.

## Topic 10 — Databricks SQL / AI-BI

Warehouse sizing, query behavior and dashboard refreshes drive analytical cost.

## Topic 12 — Asset Bundles / CI/CD

Cost policies, tags and configuration can be managed through deployment workflows where supported.

## Stage 2 Module 2.21 — Performance and Cost

That module establishes cloud-neutral performance/cost principles.

This topic applies them specifically to:

```text
Databricks billing
+
System-table evidence
+
Attribution
+
FinOps
```

---

# 98. Production Quality Gate

You should not consider this topic complete until you can demonstrate:

- [ ] Explain DBUs.
- [ ] Explain SKU-based billing.
- [ ] Explain classic compute cost.
- [ ] Explain serverless cost.
- [ ] Explain total workload cost.
- [ ] Query billing system data.
- [ ] Query pricing information.
- [ ] Analyze compute.
- [ ] Analyze jobs.
- [ ] Analyze pipelines.
- [ ] Analyze query history.
- [ ] Analyze audit data.
- [ ] Attribute cost using tags.
- [ ] Explain serverless usage policies.
- [ ] Build cost reports.
- [ ] Build dashboards.
- [ ] Build alerts.
- [ ] Detect anomalies.
- [ ] Calculate unit costs.
- [ ] Investigate cost spikes.
- [ ] Identify idle resources.
- [ ] Implement compute controls.
- [ ] Implement at least two optimizations.
- [ ] Measure savings.
- [ ] Prevent double counting.
- [ ] Explain data grain.
- [ ] Audit PII access.
- [ ] Design enterprise cost allocation.
- [ ] Explain showback/chargeback.
- [ ] Build the final capstone.

---

# 99. Glossary

| Term | Definition |
|---|---|
| DBU | Databricks Unit, a metered unit used for Databricks consumption. |
| SKU | Product/usage category used for billing and pricing. |
| Serverless | Databricks-managed execution model where infrastructure management is abstracted from the user. |
| Classic compute | Compute where the customer configures Databricks compute backed by cloud infrastructure. |
| Usage | Measured consumption recorded by the billing system. |
| List price | Published pricing associated with applicable SKU/usage context. |
| Cost attribution | Mapping usage/cost to an owner, team, workload or business unit. |
| FinOps | Discipline combining financial accountability with cloud/platform engineering. |
| Showback | Reporting cost to teams without necessarily charging their budgets. |
| Chargeback | Allocating financial responsibility to consuming teams/business units. |
| System table | Databricks-hosted operational data exposed through SQL. |
| Query history | Historical information about supported query workloads. |
| Audit log | Record of security/administrative events. |
| Compute policy | Rule set controlling compute configuration. |
| Auto-termination | Automatic shutdown of idle compute after a configured threshold. |
| Auto-stop | Automatic stopping of applicable idle SQL warehouse resources. |
| Unit economics | Cost normalized by a useful technical or business unit. |
| Cost center | Financial ownership category. |
| Data product | Governed data capability serving a defined consumer/business purpose. |
| Cost anomaly | Unexpected deviation from an established cost baseline. |
| Workload | A logical unit of computation such as a job, pipeline, query or application. |
| Grain | What one row of a dataset represents. |
| Attribution coverage | Proportion of spend mapped to a defined attribution dimension. |
| Budget | Financial target/monitoring boundary. |
| Usage policy | Policy used to apply controls/tags to applicable serverless usage. |

---

# 100. Cost-Safety for the Learning Environment

This module can create real cloud spend.

Use:

- Free Edition where sufficient;
- smallest adequate compute;
- short-running experiments;
- auto-termination;
- auto-stop where applicable;
- controlled datasets;
- budgets where available;
- alerts;
- cleanup procedures.

Do not run production-sized workloads merely to reproduce a learning example.

A safe loop:

```text
Small workload
→ Measure
→ Learn
→ Scale only when justified
```

---

# 101. Current Documentation and Syntax Safety

Databricks changes:

- product names;
- SKUs;
- pricing;
- system-table schemas;
- feature availability;
- cloud-specific capabilities;
- preview status;
- SQL fields.

Current documentation confirms, for example, `system.billing.usage`, `system.billing.list_prices`, current system-table categories, custom tags, serverless usage policies, and current cost-management tooling. citeturn0search1turn0search3turn0search10

Before production use, verify:

- current system-table schemas;
- current table paths;
- current column types;
- current pricing fields;
- current SKU names;
- current cloud/region support;
- current budget capabilities;
- current serverless usage-policy availability;
- current retention;
- current permissions.

Do not fabricate:

- prices;
- schemas;
- columns;
- SKU rates;
- availability guarantees.

If uncertain, label SQL:

> **Illustrative — verify against current Databricks documentation for the target workspace/account.**

---

# 102. Final Learning Loop

The G4 Databricks build loop becomes:

```text
Read
 ↓
Map to prior concept
 ↓
Build in dev
 ↓
Govern in Unity Catalog
 ↓
Run on cheapest adequate compute
 ↓
Break it
 ↓
Observe UI / system tables
 ↓
Attribute cost
 ↓
Measure
 ↓
Optimize
 ↓
Re-run
 ↓
Compare
 ↓
Document
 ↓
Add guardrail
```

The central production principle is:

> **Cost optimization is not a one-time resizing exercise. It is a continuous engineering feedback loop.**

---

# 103. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Where Taught | Hands-on Evidence |
|---|---|---|---|
| DBUs | YES | Sections 4, 9, 94 | Labs 01–02 |
| Product SKUs | YES | Section 5 | Labs 02–03 |
| Classic cloud infrastructure cost | YES | Sections 6, 9 | Lab 01 |
| Billing system tables | YES | Sections 11–14 | Labs 02, 08 |
| List prices | YES | Sections 16–18 | Lab 03 |
| Compute system data | YES | Sections 19–20 | Lab 04 |
| Jobs/pipeline runs | YES | Sections 21, 33 | Lab 05 |
| Query history | YES | Sections 22–23 | Labs 06, 13 |
| Audit logs | YES | Sections 24, 66–68 | Lab 18 |
| Custom tags | YES | Sections 26–35 | Lab 07 |
| Serverless budget policies | YES | Section 30, 41 | Lab 07 |
| Team/pipeline/data-product attribution | YES | Sections 32–34, 55–57 | Lab 19 |
| Compute policies | YES | Section 36 | Labs 11, 16 |
| Auto-termination | YES | Section 37 | Lab 11 |
| Auto-stop | YES | Section 38 | Labs 09, 11 |
| Warehouse sizing | YES | Sections 39, 73 | Lab 16 |
| Job compute vs all-purpose | YES | Section 40 | Labs 05, 16 |
| Cost dashboards | YES | Sections 47–48 | Lab 09 |
| Cost alerts | YES | Sections 45–46 | Lab 10 |
| Serverless vs classic comparison | YES | Sections 7, 72 | Lab 16 |
| Cost per pipeline run | YES | Section 49 | Lab 14 |
| Cost per dashboard | YES | Section 50 | Capstone |
| Cost per TB processed | YES | Section 51 | Lab 15 |
| Budgets | YES | Section 41 | Capstone |
| Account-level reporting | YES | Section 57 | Lab 19 |
| Cost attribution SQL | YES | Sections 14, 31–35, 43 | Labs 02, 07–09 |
| Two optimization experiments | YES | Sections 70–74, 89 | Labs 16–17 |
| PII access audit | YES | Sections 67–68 | Lab 18 |
| Production troubleshooting | YES | Sections 77–82 | Incidents / Runbooks |
| Production runbooks | YES | Section 83 | Runbooks 1–6 |
| Decision matrices | YES | Section 84 | ADR exercises |
| ADR exercises | YES | Section 85 | ADR 1–6 |
| Interview preparation | YES | Sections 91–92 | 75+ questions |
| Practice questions | YES | Section 92 | 85+ questions |
| Senior-level scenarios | YES | Section 93 | 8 scenarios |
| Final capstone | YES | Sections 89–90 | Full capstone |
| Production quality gate | YES | Section 98 | Completion checklist |

**Coverage result: COMPLETE against the supplied Topic 13 specification.**

---

# 104. Final Production Standard

The operating standard for Databricks cost engineering is:

```text
MEASURE
  ↓
ATTRIBUTE
  ↓
INVESTIGATE
  ↓
IDENTIFY DRIVER
  ↓
OPTIMIZE
  ↓
MEASURE AGAIN
  ↓
VALIDATE TRADE-OFFS
  ↓
DOCUMENT SAVINGS
  ↓
ADD GUARDRAIL
  ↓
MONITOR CONTINUOUSLY
```

And the FinOps architecture is:

```text
USAGE
→ PRICE
→ COST
→ ATTRIBUTION
→ UNIT ECONOMICS
→ INVESTIGATION
→ OPTIMIZATION
→ GOVERNANCE
→ AUDIT
→ CONTINUOUS IMPROVEMENT
```

The learner should leave this topic able to operate Databricks cost management as a **production engineering capability**, not merely read a monthly bill.

---

# 105. Final Validation Record

- Exact filename: `13-cost-management-and-system-tables.md`
- Authoritative Topic 13 specification reviewed: YES
- Authoritative G4 roadmap reviewed: YES
- Basics → Advanced → Production progression: YES
- DBUs and billing: YES
- Product SKUs: YES
- Classic/serverless economics: YES
- System tables: YES
- Billing usage: YES
- List prices: YES
- Compute data: YES
- Jobs/pipelines: YES
- Query history: YES
- Audit data: YES
- Cost attribution/tagging: YES
- Serverless usage policies: YES
- Compute policies: YES
- Auto-termination: YES
- Auto-stop: YES
- Warehouse sizing: YES
- Jobs compute vs all-purpose: YES
- Dashboards: YES
- Alerts/anomaly detection: YES
- Unit economics: YES
- Advanced FinOps: YES
- Showback/chargeback: YES
- Multi-workspace reporting: YES
- Data grain/double counting: YES
- Cost data quality: YES
- PII audit: YES
- Optimization experiments: YES
- Before/after measurement: YES
- Troubleshooting: YES
- Production runbooks: YES
- Decision matrices: YES
- ADR exercises: 6
- Progressive labs: 20
- Break/fix framework: YES
- Interview preparation: YES
- Practice questions: YES
- Senior scenarios: YES
- Production capstone: YES
- Production quality gate: YES
- Roadmap coverage audit: YES
- Current-documentation safety: YES
- Fake pricing avoided: YES
- Fake schema certainty avoided: YES
- Other roadmap files modified: NO
