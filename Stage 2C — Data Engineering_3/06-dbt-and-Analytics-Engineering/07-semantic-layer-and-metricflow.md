# dbt Semantic Layer and MetricFlow

> **Roadmap location:** `Stage 2C — Data Engineering_3/06-dbt-and-Analytics-Engineering/07-semantic-layer-and-metricflow.md`  
> **Curriculum source:** Topic 07 in `roadmap-dbt-and-Analytics-Engineering.md`, checked against the complete `Roadmap_ptree.md`.  
> **Scope:** Metric definitions, semantic models, MetricFlow query planning, metric correctness, serving, governance, alternatives, and governed AI access.  
> **Version baseline:** Examples use the **dbt v1.12+ metric specification and self-hosted MetricFlow CLI conventions** documented by dbt at the time this lesson was written. Hosted dbt Semantic Layer features, adapters, metric types, and integration availability depend on product track, account tier, warehouse, and installed version. Confirm the exact installed CLI with `mf --help`, `dbt --version`, and current product documentation before using production commands.

## Learning outcomes

By completing this lesson, you will be able to:

- Explain why metrics duplicated in dashboards drift and how a semantic layer establishes reusable definitions.
- Model entities, categorical/time dimensions, simple metrics, and higher-level metrics over the existing `fct_orders` and `dim_customers` marts.
- Define revenue, active customers, average order value (AOV), a conversion-rate metric, and cumulative revenue with explicit grains, filters, and owners.
- Explain how MetricFlow plans joins from entity relationships, and detect invalid join paths, fan-out, and non-additive calculations.
- Validate semantic configuration, query metrics by dimensions/time grain, inspect generated SQL, and compare results to independently written SQL.
- Distinguish local MetricFlow development from hosted dbt Semantic Layer serving and its APIs/integrations.
- Govern definitions through ownership, certification, testing, reconciliation, version control, and deprecation.
- Explain trade-offs among dbt Semantic Layer, Cube, LookML/Looker, AtScale, and warehouse-native semantic/metric views.
- Expose governed metrics to AI applications without allowing the model to invent formulas or bypass authorization.

---

## 1. Semantic layer fundamentals

### 1.1 The metric consistency problem

Imagine that three dashboards report “revenue”:

- Dashboard A sums all order payment amounts.
- Dashboard B excludes cancelled orders.
- Dashboard C sums order totals but includes refunds differently.

All three charts may be technically correct for their own SQL, yet they disagree because the word *revenue* has no single governed definition. Copying the SQL into more dashboards multiplies maintenance cost and creates reconciliation work.

A semantic layer centralizes metric meaning and describes how a consumer may group or filter the metric. A query engine such as MetricFlow turns the semantic request into SQL against the warehouse.

| Layer | Responsibility | Example |
|---|---|---|
| Raw/source data | Capture source facts | Raw orders and payments |
| dbt transformation models | Clean, join, and establish grains | `stg_orders`, `int_orders_payments` |
| Marts | Publish stable analytical tables | `fct_orders`, `dim_customers` |
| Semantic model | Declare entities, dimensions, and aggregatable fields for a mart | `orders` semantic model |
| Metric definition | Give an approved business measure a formula, filters, and aggregation semantics | `revenue` |
| Consumer | Request a metric by dimensions and filters | Revenue by month and customer segment |

A semantic layer is **not** a replacement for well-designed marts. It depends on correct grain, keys, business logic, and data quality. Stabilize and test the marts first.

### 1.2 What dbt Semantic Layer and MetricFlow do

- **dbt Semantic Layer** is dbt's governed metric-consumption capability. Hosted serving and supported downstream integrations are product capabilities; they are not automatically available in every dbt Core project.
- **MetricFlow** is the metric definition/query-planning engine used by the dbt Semantic Layer. It reads semantic metadata, plans a path between metric sources and requested dimensions, generates SQL for the warehouse, and returns the result.
- **Semantic model** describes how a dbt model should be interpreted: entities, dimensions, a default time dimension, and simple aggregations/metrics.
- **Metric** is a named business calculation that can be queried with compatible dimensions and filters.

In the v1.12+ specification used here, a simple metric is defined as a `type: simple` metric with an aggregation and expression. Older dbt semantic-layer tutorials often use a separate `measures:` block. Do not mix old and new specifications in one project: follow the version track selected for your project.

### 1.3 Measures versus metrics

The words are related but not interchangeable.

- A **measure** in dimensional modelling is an aggregatable business value stored at a fact grain, such as `total_payment_cents`.
- A **simple metric** in the current v1.12+ syntax defines how to aggregate an expression, such as `sum(total_payment_cents)`.
- A higher-level **metric** combines simple metrics, applies a ratio or expression, or accumulates a metric over time.

In older MetricFlow/dbt Semantic Layer YAML, `measures:` commonly held aggregation definitions and `metrics:` referred to metric objects built from those measures. In the v1.12+ configuration below, simple metrics use `metrics:` within the model's semantic definition and use `type: simple`, `agg`, and `expr`. The conceptual distinction still matters even though the YAML surface has evolved.

### 1.4 Entities: primary, foreign, and unique

Entities tell MetricFlow how rows in different semantic models relate. They are not merely labels; they define the keys from which joins can be planned.

| Entity type | Meaning | Example |
|---|---|---|
| `primary` | The semantic model's principal unique/natural key | `fct_orders.order_id` |
| `foreign` | A key pointing to an entity represented in another model | `fct_orders.customer_id` references the customer entity |
| `unique` | A unique key useful for connecting a model to other entities without declaring it the model's primary entity | A unique payment/customer mapping key in an appropriate model |

Only declare an entity unique if the corresponding column is actually unique at the model grain. A false uniqueness declaration can produce incorrect joins or invalid query plans. A primary entity should identify a row at the semantic model's grain.

For this lesson:
- `fct_orders` has one row per order; `order_id` is its primary entity.
- `fct_orders.customer_id` is a foreign entity named `customer`.
- `dim_customers` has one row per customer; `customer_id` is the primary entity named `customer`.

The shared entity name `customer` is the semantic join contract. Its key values must be compatible in type and meaning in both models.

### 1.5 Dimensions: categorical and time

- **Categorical dimensions** describe categories or attributes used to filter/group results, such as `order_status`, `customer_name`, or customer region.
- **Time dimensions** represent dates/timestamps, such as `order_date`. They enable time filters and grouping at day/week/month/quarter/year.
- A **dimension value** is an actual value in a dimension, such as `completed` or `cancelled`.
- The global time dimension often queried as `metric_time` is a semantic time concept, not a physical column you must add to every mart.

A dimension should describe a property at a well-defined grain. If customer attributes change historically, decide whether analysis should use current attributes or the historical attributes valid at the event time. The current `dim_customers` lesson model is a current-state dimension, not an SCD Type 2 model.

### 1.6 Aggregation behavior

Metric design begins with grain and aggregation behavior.

| Aggregation | Typical use | Important caution |
|---|---|---|
| `sum` | Additive monetary amounts or counts | Safe only when rows are not duplicated and units/filters match |
| `count` | Count non-null values/rows depending on expression semantics | Verify whether nulls and duplicate rows matter |
| `count_distinct` | Distinct customers/orders | Usually non-additive across groups: customer counts by region may not sum to a global distinct count |
| `average` | Average of values at the declared grain | An average of subgroup averages is generally not the overall average |
| `min` / `max` | Earliest/latest values, extrema | Not additive |
| Ratio | Numerator divided by denominator | Recompute from components at requested grain; do not average ratios blindly |
| Cumulative | Running or rolling aggregation over time | Requires correct time spine and window semantics |

Revenue is usually additive across orders and time if each order contributes exactly once and the business definition is consistent. Distinct active customers is not additive across days: one customer active on two days should be counted once in a two-day distinct count, not twice.

---

## 2. Metric dictionary: define the business contract first

A metric dictionary is the reviewable contract that exists before YAML is written. The example below is a **lab definition**, not a claim that it matches a company's accounting policy. Finance and business owners must approve the revenue definition before production use.

| Metric | Formula and meaning | Grain / time behavior | Filters and exclusions | Owner |
|---|---|---|---|---|
| `revenue` | `SUM(total_payment_cents) / 100`; amount paid/recorded for orders represented by `fct_orders`, converted from cents to currency units | One row per order in the fact; additive by order date when order rows are unique | This mart currently sums payment rows without a documented status/refund policy. For production, explicitly define successful/settled payments, refunds, cancellations, currency, tax, and recognition date. Do not label this finance-approved revenue until reconciled. | Finance metric owner + Analytics Engineering steward |
| `active_customers` | `COUNT(DISTINCT customer_id)` with at least one order in the selected period | Distinct customers over the requested period; daily counts are not additive across days | Excludes customers without an order in the selected period; order-status policy must be documented | Customer Analytics owner |
| `conversion_rate` | For this lab: `completed_orders / all_orders`; this is an **order completion rate**, not website visitor-to-purchase conversion | Ratio evaluated at the requested output grain (for example, month) | Numerator filters to the source's canonical completed status; denominator includes all eligible orders. Replace `'completed'` if the source's accepted status value differs. | Commerce/Product Analytics owner |
| `average_order_value` | `revenue / order_count` | Ratio at requested grain; order-count denominator must match revenue eligibility | Same order population and time field as revenue; do not average order-level or subgroup averages | Finance metric owner |
| `running_revenue` | Month-to-date accumulation of `revenue` in this example | One result per time bucket; restarts at month boundary for `grain_to_date: month` | Inherits revenue definition; requires a configured time spine | Finance metric owner |

### 2.1 Decide the time attribution rule

The mart's `order_date` is the event date used by the lab. A payments-based accounting metric might instead use payment settlement date; a recognized-revenue metric may use a finance ledger date. Do not silently substitute one for another.

For each metric, document:
1. Event date / time zone / calendar.
2. Currency and unit.
3. Included and excluded statuses.
4. Treatment of refunds, reversals, chargebacks, and late-arriving records.
5. Grain at which the source value is valid.
6. Owner, certification status, and reconciliation target.

If the existing `fct_orders` does not contain the fields required by the agreed policy, update the mart first. Do not force a semantic definition to compensate for missing or ambiguous source logic.

---

## 3. Version-qualified implementation

### 3.1 Compatibility and prerequisites

The YAML in this lesson follows the dbt v1.12+ metric specification, with self-hosted `mf` command examples. Current hosted dbt Semantic Layer access, production serving, and supported warehouses are separate from local CLI development.

Before starting:
```bash
dbt --version
mf --help
mf query --help
mf validate-configs --help
```

Use the help output from the installed version as the final authority for available flags. If `mf` is not installed or commands are unavailable, follow the installation instructions for the selected dbt/MetricFlow release rather than installing an unpinned latest package into a production environment.

**Warehouse note:** earlier lessons may use DuckDB for local mart development, but do **not** assume that MetricFlow supports DuckDB merely because dbt-duckdb works. Current dbt documentation lists supported MetricFlow warehouses by release (including Snowflake, BigQuery, Databricks, and specific dbt v1-only options); verify the exact support matrix before installing the adapter extra. If DuckDB is your only local adapter, use it to validate mart SQL and fixture arithmetic, but run MetricFlow-specific validation/query steps on a supported adapter. Hosted serving and BI/API integrations additionally require an eligible dbt plan and configured environment.

### 3.2 Existing mart contracts

The examples assume these existing models and grains:

| Model | Grain | Columns used in this lesson |
|---|---|---|
| `fct_orders` | One row per order | `order_id`, `customer_id`, `order_date`, `order_status`, `total_payment_cents`, `payment_count` |
| `dim_customers` | One row per current customer | `customer_id`, `first_name`, `last_name`, `full_name` |

The earlier mart's `total_payment_cents` is an aggregate of payment amounts. Its precise accounting interpretation depends on source data and payment-status logic. The semantic YAML uses that field as the lab's revenue basis solely to teach aggregation and query planning. For finance-grade revenue, first modify/test the mart to implement the approved policy.

### 3.3 Semantic model over `fct_orders`

Create or update `models/marts/fct_orders.yml` inside a configured `model-paths` directory. The semantic model is named `orders`.

```yaml
version: 2

models:
  - name: fct_orders
    description: >
      Order-grain fact model. One row per order. total_payment_cents is
      the sum of payment amounts recorded for the order; confirm payment
      status, refunds, and currency semantics before calling it revenue.
    semantic_model:
      enabled: true
      name: orders
    agg_time_dimension: order_date
    columns:
      - name: order_id
        description: Unique order identifier.
        entity:
          type: primary
          name: order
      - name: customer_id
        description: Customer identifier associated with the order.
        entity:
          type: foreign
          name: customer
      - name: order_date
        description: Date used for order-based metric time attribution.
        granularity: day
        dimension:
          type: time
      - name: order_status
        description: Canonicalized source order status.
        dimension:
          type: categorical
      - name: total_payment_cents
        description: Recorded payment amount summed at order grain, in cents.
      - name: payment_count
        description: Number of payment rows summed at order grain.
    metrics:
      - name: revenue
        description: Lab revenue basis, expressed in currency units.
        label: Revenue
        type: simple
        agg: sum
        expr: total_payment_cents / 100.0
      - name: order_count
        description: Number of order-grain rows.
        label: Order Count
        type: simple
        agg: sum
        expr: 1
      - name: active_customers
        description: Distinct customers with orders in the selected period.
        label: Active Customers
        type: simple
        agg: count_distinct
        expr: customer_id
      - name: completed_orders
        description: Orders with the canonical completed status.
        label: Completed Orders
        type: simple
        agg: sum
        expr: 1
        filter: "{{ Dimension('order__order_status') }} = 'completed'"
```

**Important checks before copying:**
- Keep the model names and column names identical to the actual dbt project.
- Confirm the status value is exactly `'completed'`; use the source's actual accepted value if different.
- `total_payment_cents / 100.0` assumes a currency with 100 minor units per major unit. This is not valid for every currency and is not a substitute for currency conversion.
- The YAML defines `active_customers` as distinct customers who placed an order in the queried period. It does not imply product activity or website activity.
- Do not create a `measure:` block from older examples alongside these v1.12+ `type: simple` metric definitions.

### 3.4 Semantic model over `dim_customers`

Create or update `models/marts/dim_customers.yml`:

```yaml
version: 2

models:
  - name: dim_customers
    description: >
      Current-state customer dimension with one row per customer.
      Historical attributes are not preserved by this model.
    semantic_model:
      enabled: true
      name: customers
    columns:
      - name: customer_id
        description: Stable customer identifier.
        entity:
          type: primary
          name: customer
      - name: first_name
        description: Customer first name; apply privacy policy before exposure.
        dimension:
          type: categorical
      - name: last_name
        description: Customer last name; apply privacy policy before exposure.
        dimension:
          type: categorical
      - name: full_name
        description: Display name for internal analysis where permitted.
        dimension:
          type: categorical
```

The relationship is expressed by the entity name `customer`: `orders.customer_id` is foreign, and `customers.customer_id` is primary. MetricFlow can use this path to add customer dimensions to order metrics. The join is only valid if the dimension contains at most one row per `customer_id` and the foreign-key values refer to the same customer identifier domain.

Do not expose names, emails, or other personal data to broad consumers simply because they are valid dimensions. Metric definitions and authorization policies must be designed together.

### 3.5 Ratio and derived metrics

For the v1.12+ specification, add ratio and derived metrics to the model's `metrics:` list after the component metrics above:

```yaml
      - name: average_order_value
        description: Revenue divided by the number of eligible orders.
        label: Average Order Value
        type: ratio
        numerator: revenue
        denominator: order_count
      - name: conversion_rate
        description: "Order completion rate: completed orders divided by all orders."
        label: Order Completion Rate
        type: ratio
        numerator: completed_orders
        denominator: order_count
      - name: revenue_per_active_customer
        description: Revenue divided by distinct active customers in the requested period.
        label: Revenue per Active Customer
        type: derived
        expr: revenue / active_customers
        input_metrics:
          - name: revenue
          - name: active_customers
```

Append these entries at the same indentation level as the other entries under `metrics:`. Do not paste a second `metrics:` key into the same YAML object.

Why use a ratio for AOV? Because MetricFlow evaluates numerator and denominator at the requested output grain. If a month has $300 of revenue and 10 orders, monthly AOV is $30. The correct quarterly AOV is total quarter revenue divided by total quarter orders—not the arithmetic mean of three monthly AOVs unless the months have equal order counts.

**Conversion terminology:** this example measures order completion, not visitor-to-purchase conversion. A real funnel conversion rate needs a well-defined eligible population (for example, sessions or signups), a conversion event, an entity connecting those events, an attribution window, and deduplication rules. Do not infer website conversion from an orders-only mart.

### 3.6 Cumulative metric: month-to-date revenue

Append this metric under the same `metrics:` list:

```yaml
      - name: running_revenue_mtd
        description: Revenue accumulated from the start of each month through each time bucket.
        label: Running Revenue MTD
        type: cumulative
        input_metric: revenue
        grain_to_date: month
```

This means month-to-date accumulation, not a lifetime running total. If you need a trailing 30-day metric instead, use the installed version's documented `window` syntax and validate the output around missing dates and boundaries. Do not combine `grain_to_date` and a rolling `window` unless the selected specification explicitly supports that combination.

### 3.7 Conversion metrics: distinguish metric type from ratio definition

The roadmap includes conversion metrics as a concept. A dedicated conversion metric links a base event to a later conversion event for the same entity within a defined time window. This differs from the `conversion_rate` ratio above, which only calculates completed orders divided by all orders.

A version-qualified **illustrative funnel configuration** using the dbt v1.12+ syntax is shown below. It adds `fct_visits` and `fct_buys` event models, each with a stable event key, a shared `user` entity, and an event-time dimension. It is **not runnable against only `fct_orders` and `dim_customers`**, because those models do not contain visit events.

```yaml
version: 2

models:
  - name: fct_visits
    semantic_model:
      enabled: true
      name: visits
    agg_time_dimension: visit_date
    columns:
      - name: visit_id
        entity:
          type: primary
          name: visit
      - name: user_id
        entity:
          type: foreign
          name: user
      - name: visit_date
        granularity: day
        dimension:
          type: time
      - name: referrer_id
        dimension:
          type: categorical
    metrics:
      - name: visits
        type: simple
        label: Visits
        agg: count
        expr: visit_id

  - name: fct_buys
    semantic_model:
      enabled: true
      name: buys
    agg_time_dimension: buy_date
    columns:
      - name: buy_id
        entity:
          type: primary
          name: buy
      - name: user_id
        entity:
          type: foreign
          name: user
      - name: buy_date
        granularity: day
        dimension:
          type: time
    metrics:
      - name: buys
        type: simple
        label: Buys
        agg: count
        expr: buy_id

# Advanced metric references simple metrics in two different semantic models.
metrics:
  - name: visit_to_buy_conversion_rate_7d
    description: "Conversion rate from a visit to a buy within seven days."
    label: "Visit to buy conversion rate (7-day window)"
    type: conversion
    entity: user
    calculation: conversion_rate
    base_metric: visits
    conversion_metric: buys
    window: 7 days
```

The conversion metric is defined at the top level because it references simple metrics from two different semantic models. Confirm that event IDs are unique, `user_id` values share the same identity domain, and timestamps support the chosen window. For filtered attribution, the current spec supports a `base_metric` or `conversion_metric` object with a `name` and filter. For example, use this object form in the top-level metric:

```yaml
base_metric:
  name: visits
  filter: "{{ Dimension('visit__referrer_id') }} = 'facebook'"
```

Before adopting a conversion metric, check the current version's official specification and test:
1. Model eligible base events and conversion events with stable entity keys.
2. Define the event timestamp and attribution window explicitly.
3. Deduplicate multiple conversion events according to the business rule.
4. Verify which base event receives credit when several eligible base events precede one conversion.
5. Test conversions before the base event, outside the window, duplicate events, missing IDs, and zero/null conversions.

The lab's `conversion_rate` ratio remains a valid, deliberately narrower order-completion metric and is reproducible from `fct_orders`.

---

## 4. Time spine and time granularities

### 4.1 What a time spine solves

A **time spine** is a continuous set of time buckets at a defined granularity. It enables time-based joins and cumulative/rolling calculations, including periods with no underlying fact rows. Without a complete spine, a date with no orders may disappear instead of appearing with zero or a null metric, and window boundaries can behave incorrectly.

Time spine design decisions:
- Choose the base grain (daily for this lab).
- Cover the required historical and future range.
- Decide whether weekly/monthly boundaries follow calendar, ISO, or fiscal rules.
- Use a consistent time zone before truncating timestamps to dates.
- Confirm whether no-activity periods should appear as zero, null, or be omitted.
- Extend the date range before it expires; monitor the spine's future coverage.

### 4.2 Daily time spine SQL

Create `models/marts/time_spine_daily.sql`. The example uses the project's dbt-utils date-spine macro, so the package must be installed and pinned as described in the project:

```sql
{{ config(materialized='table') }}

with base_dates as (

    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2020-01-01' as date)",
        end_date="cast('2035-01-01' as date)"
    ) }}

)

select cast(date_day as date) as date_day
from base_dates
```

This is a dbt-utils macro example, not a built-in SQL function. Verify the exact macro arguments and SQL emitted by the pinned dbt-utils version and warehouse adapter. In a new project, use the currently documented dbt time-spine recipe for your adapter rather than assuming date syntax is portable.

Configure it in `models/marts/time_spine.yml`:

```yaml
version: 2

models:
  - name: time_spine_daily
    description: One row per calendar day for time-based metric joins.
    time_spine:
      standard_granularity_column: date_day
    columns:
      - name: date_day
        description: Calendar date used as the daily time-spine key.
        granularity: day
```

Build it before validating cumulative metrics:

```bash
dbt deps
dbt run --select time_spine_daily
dbt parse
mf validate-configs
```

If you already have a tested `dim_date` table, configure it as the time spine instead of creating a duplicate. Add custom fiscal granularities only when their calendar definitions are unambiguous and tested.

### 4.3 Querying time grains

With the self-hosted CLI convention in this lesson:

```bash
# Daily revenue
mf query --metrics revenue --group-by metric_time

# Monthly revenue and AOV
mf query --metrics revenue,average_order_value --group-by metric_time__month

# Monthly order-completion rate
mf query --metrics conversion_rate --group-by metric_time__month

# Month-to-date running revenue
mf query --metrics running_revenue_mtd --group-by metric_time
```

Available granularities and the exact command flags vary by MetricFlow/dbt version. Current documentation commonly uses `metric_time__day`, `metric_time__week`, `metric_time__month`, `metric_time__quarter`, and `metric_time__year`. Run `mf query --help` if the local version expects a different flag or dimension name.

**Calendar caution:** grouping a timestamp by day without defining the source time zone can shift events across dates. Convert timestamps to the business time zone in the mart before treating the date as a canonical business day.

---

## 5. MetricFlow query planning and SQL generation

### 5.1 Query planning mental model

A metric query asks for something like: “Give me monthly revenue by customer name for the last quarter.”

MetricFlow conceptually:
1. Resolves the metric and its source semantic model.
2. Resolves requested dimensions and time grain.
3. Finds a valid join path using entity relationships.
4. Applies metric-level filters and query-level filters.
5. Plans aggregations at the correct grain and places them before/after joins as needed.
6. Generates warehouse SQL and executes it (or exposes/compiles the SQL, depending on CLI and integration).
7. Returns one value per requested output group.

This is more than string substitution. It is a constrained query-planning problem. If no valid relationship exists, the dimension is unreachable, or the path is ambiguous, the correct response is to fix the semantic graph rather than manually forcing an unsafe join.

### 5.2 Query across the customer entity

```bash
mf query \
  --metrics revenue,average_order_value \
  --group-by customer__full_name,metric_time__month
```

The exact dimension naming shown in command output depends on the semantic model and version. Inspect available names with `mf list dimensions` or the equivalent documented command. Do not assume a field's SQL column name is always its public semantic dimension name.

Expected shape (illustrative only; values depend on the actual warehouse data):

| customer | metric month | revenue | average order value |
|---|---|---:|---:|
| Customer A | 2026-01 | 250.00 | 125.00 |
| Customer B | 2026-01 | 90.00 | 90.00 |

These numbers are placeholders to illustrate the output shape, not measured results from your project.

### 5.3 Inspect generated SQL

For self-hosted MetricFlow, the current command documentation uses `--explain` to display the SQL/plan; hosted dbt platform CLI uses `--compile` in documented examples. Check `mf query --help` for the installed version.

```bash
# Self-hosted MetricFlow CLI (v1/v2 conventions documented by dbt)
mf query \
  --metrics revenue \
  --group-by customer__full_name,metric_time__month \
  --explain
```

The generated SQL will be adapter-specific. A simplified conceptual form might look like this:

```sql
select
    date_trunc('month', orders.order_date) as metric_month,
    customers.full_name as customer_name,
    sum(orders.total_payment_cents) / 100.0 as revenue
from analytics.fct_orders as orders
left join analytics.dim_customers as customers
    on orders.customer_id = customers.customer_id
group by 1, 2
order by 1, 2;
```

This SQL is an explanatory equivalent, not a transcript of MetricFlow's generated SQL. Actual output may use nested subqueries, quoted identifiers, time-spine joins, filters, or adapter-specific date functions.

### 5.4 Compare with hand-written SQL

Use the same metric definition, time attribution, filters, and output grain in both queries. The independent SQL should not copy generated SQL mechanically; it should express the agreed business rule clearly.

```sql
select
    date_trunc('month', cast(o.order_date as timestamp)) as metric_month,
    c.full_name as customer_name,
    sum(o.total_payment_cents) / 100.0 as revenue
from analytics.fct_orders as o
left join analytics.dim_customers as c
    on o.customer_id = c.customer_id
group by 1, 2
order by 1, 2;
```

For adapters that don't support the shown `date_trunc` signature, use the adapter's equivalent. Compare:
- Same row keys (customer, month).
- Same row count and missing groups.
- Same values within an explicit decimal tolerance.
- Same status/date/currency filters.
- Same treatment of customers without a dimension row.
- Same behavior when a month has no facts.

Do not compare only grand totals: two incorrect queries can have the same total but different group-level results.

### 5.5 Join correctness and fan-out

A **fan-out** occurs when a join multiplies fact rows. Suppose `fct_orders` has two orders:

| order_id | customer_id | total_payment_cents |
|---|---|---:|
| 101 | 7 | 10000 |
| 102 | 7 | 20000 |

Correct revenue is 300.00. If `dim_customers` accidentally contains three rows for customer 7, joining orders to that dimension produces six joined rows and revenue of 900.00. The issue is a violated dimension grain, not a metric aggregation bug.

Incorrect query pattern:

```sql
select sum(o.total_payment_cents) / 100.0 as revenue
from analytics.fct_orders o
join analytics.dim_customers c
  on o.customer_id = c.customer_id;
```

This query inflates revenue if `dim_customers.customer_id` is duplicated. A `distinct` applied after the sum will not repair it.

Correct controls:
1. Test `dim_customers.customer_id` as unique and not null.
2. Test the order key in `fct_orders` as unique and not null.
3. Test the customer relationship and monitor unmatched keys.
4. Verify join cardinality before defining a semantic entity.
5. If a source is many-to-many, model a bridge and an explicit allocation rule rather than declaring a false one-to-one relationship.
6. Pre-aggregate the many-side to the intended grain before joining when that preserves the business meaning.

Example dbt tests (place in the appropriate YAML for the project version):

```yaml
models:
  - name: dim_customers
    columns:
      - name: customer_id
        data_tests:
          - unique
          - not_null

  - name: fct_orders
    columns:
      - name: order_id
        data_tests:
          - unique
          - not_null
      - name: customer_id
        data_tests:
          - relationships:
              arguments:
                to: ref('dim_customers')
                field: customer_id
```

The nested `arguments` syntax is version-dependent; if your installed dbt release uses the earlier generic-test argument syntax, adapt to that release's documented format. Tests validate the model grain; semantic metadata does not replace them.

### 5.6 Why averaging averages is wrong

Suppose:
- January: revenue $100 across 2 orders → AOV $50.
- February: revenue $900 across 30 orders → AOV $30.

A simple mean of the two monthly averages is \((50 + 30) / 2 = 40\). But the true combined AOV is \((100 + 900) / (2 + 30) = 31.25\).

The right approach is to keep the additive components—revenue and order count—and calculate the ratio at the requested grain:

\[
\text{AOV} = \frac{\sum \text{eligible order revenue}}{\sum \text{eligible orders}}
\]

A ratio metric expresses this behavior directly. If a consumer needs a mean of monthly AOVs for a particular business reason, name and define that statistic explicitly; it is not overall AOV.

---

## 6. Metric testing and reconciliation

### 6.1 Test a known-answer fixture

Use a tiny, controlled dataset to prove arithmetic before testing a full warehouse. The following fixture is illustrative and can be implemented as seeds or temporary tables.

`orders_fixture.csv`:

```csv
order_id,customer_id,order_date,order_status,total_payment_cents
1,10,2026-01-03,completed,10000
2,10,2026-01-04,completed,20000
3,20,2026-01-05,cancelled,5000
4,20,2026-02-02,completed,90000
```

Expected answers under the **lab's simplified definitions**:
- Revenue for January: \(100 + 200 + 50 = 350\) currency units.
- Order count for January: 3.
- AOV for January: \(350 / 3 = 116.6667\).
- Completed-order rate for January: \(2 / 3 \approx 0.6667\).
- Distinct active customers in January: 2.
- Revenue for February: 900.
- Running MTD revenue on February 2: 900, because the MTD window restarts at February 1.

This fixture intentionally includes a cancelled order with an amount to reveal the importance of the revenue filter policy. If the approved definition excludes cancelled orders, revenue for January would be 300 rather than 350; change the metric definition and expected answer together. Never leave the policy ambiguous.

The fixture's `total_payment_cents` is already at order grain; do not join raw payment rows to this table without aggregating payments to one row per order first.

### 6.2 Build metric tests

For each important metric, test:
- **Known-answer values:** fixture rows with hand-calculated expected answers.
- **Aggregation behavior:** month/quarter/global results match recomputation from components.
- **Dimensional consistency:** the metric groups correctly by each supported dimension.
- **Time boundaries:** month/year rollover, no-fact dates, time zone boundaries, late data, and partial periods.
- **Filter semantics:** metric-level filters and query-level filters combine as intended.
- **Join cardinality:** dimension keys are unique and relationships are valid.
- **Null/zero behavior:** denominator zero, missing dimension, null amount, and empty time buckets.
- **Access control:** restricted dimensions/metrics are unavailable to unauthorized consumers.

A basic SQL reconciliation for monthly revenue and order count:

```sql
select
    date_trunc('month', cast(order_date as timestamp)) as metric_month,
    sum(total_payment_cents) / 100.0 as expected_revenue,
    count(*) as expected_order_count
from analytics.fct_orders
group by 1
order by 1;
```

A singular dbt test can verify the known-answer fixture before you compare MetricFlow to the mart. Create `tests/assert_metric_known_answers.sql` after adding `orders_fixture.csv` as a seed. It returns rows only when the calculated values differ from the expected answers:

```sql
with actual as (

    select
        cast(date_trunc('month', cast(order_date as timestamp)) as date) as metric_month,
        sum(total_payment_cents) / 100.0 as revenue,
        count(*) as order_count,
        sum(case when order_status = 'completed' then 1 else 0 end) as completed_orders
    from {{ ref('orders_fixture') }}
    group by 1

),

expected as (

    select
        cast('2026-01-01' as date) as metric_month,
        350.0 as revenue,
        3 as order_count,
        2 as completed_orders

    union all

    select
        cast('2026-02-01' as date) as metric_month,
        900.0 as revenue,
        1 as order_count,
        1 as completed_orders

)

select
    coalesce(a.metric_month, e.metric_month) as metric_month,
    a.revenue as actual_revenue,
    e.revenue as expected_revenue,
    a.order_count as actual_order_count,
    e.order_count as expected_order_count,
    a.completed_orders as actual_completed_orders,
    e.completed_orders as expected_completed_orders
from actual a
full outer join expected e
    on a.metric_month = e.metric_month
where a.metric_month is null
   or e.metric_month is null
   or abs(a.revenue - e.revenue) > 0.0001
   or a.order_count <> e.order_count
   or a.completed_orders <> e.completed_orders
```

The fixture test proves the independent arithmetic for the sample rows. It does not by itself prove MetricFlow generated the same result: run the equivalent `mf query`, compare the grouped result to this independent baseline, and retain the outputs as lab evidence. For AOV, compare `expected_revenue / nullif(expected_order_count, 0)` rather than `avg(order_value)` over a derived monthly result.

### 6.3 Reconcile with Finance

The metric owner should produce a reconciliation pack that records:
1. Business definition and accounting source of truth.
2. Reconciliation date range, currency, time zone, and close status.
3. Expected finance total and source/report identifier.
4. Semantic metric result and exact query/commit/environment.
5. Absolute and relative variance.
6. Explained adjustments: refunds, reversals, tax, discounts, timing, currency conversion, cancellations, and late-arriving entries.
7. Tolerance, approver, and sign-off date.

Do not invent reconciliation numbers. Use real finance-approved figures and preserve the source evidence. A discrepancy should be investigated, not “fixed” by adding an undocumented filter until the totals happen to match.

### 6.4 CI strategy

A sensible metric CI gate:
- Parse/validate the semantic configuration.
- Build the changed mart models.
- Run key and relationship tests.
- Run a small known-answer fixture or unit/integration test.
- Compare key metric outputs against independently written SQL.
- Require owner approval for changes to certified metric definitions.
- Publish the semantic metadata only from the intended environment and approved commit.

Heavy full-history reconciliations can run nightly or during financial close, but a fast subset of high-value checks should run for pull requests. Define the subset and exclusions explicitly.

---

## 7. Commands, saved queries, exports, and caching

### 7.1 Validate configuration and query metrics

For self-hosted MetricFlow (the CLI convention for this lesson):

```bash
# Parse dbt project metadata first
dbt parse

# Validate semantic-model and metric configuration
mf validate-configs

# Discover metric names and their available dimensions
mf list metrics
mf list dimensions
mf list entities

# Query one metric by month
mf query --metrics revenue --group-by metric_time__month

# Query multiple metrics at a common grain
mf query --metrics revenue,order_count,average_order_value \
  --group-by metric_time__month

# Inspect generated SQL/plan (flag depends on CLI version)
mf query --metrics revenue --group-by metric_time__month --explain
```

In the hosted dbt platform CLI, equivalent commands are generally exposed through `dbt sl`, for example `dbt sl query` and `dbt sl validate`; the exact command surface differs by dbt version/track. Do not assume that `mf validate-configs` is the hosted CLI command. Use the CLI help and current dbt command reference for the selected installation.

A successful config validation proves structural/configuration checks passed; it does **not** prove the metric matches the finance definition or that every warehouse query is correct.

### 7.2 Saved queries

Saved queries package a known set of metrics, dimensions, and filters for repeatable consumption. The following is a **version-qualified example** of the documented saved-query shape; merge it as a root-level `saved_queries:` key into a project YAML file and validate it with the installed release. Do not duplicate an existing root key.

```yaml
saved_queries:
  - name: monthly_commerce_metrics
    description: "Monthly revenue, order count, and average order value."
    label: Monthly Commerce Metrics
    config:
      cache:
        enabled: true
      meta:
        owner: "analytics-engineering"
        domain: "commerce"
      tags:
        - certified-candidate
    query_params:
      metrics:
        - revenue
        - order_count
        - average_order_value
      group_by:
        - "TimeDimension('metric_time', 'month')"
    exports:
      - name: monthly_commerce_metrics_export
        config:
          export_as: table
          alias: monthly_commerce_metrics
          schema: analytics_exports
```

This example illustrates a saved query with cache enabled and a table export definition; it is not evidence that the cache was populated or the export ran. Cache availability/refresh behavior and saved-query validation/building/export execution vary by dbt version and product track. Current docs describe `dbt build --resource-type saved_query` for building saved-query nodes and hosted job-scheduler execution for exports. Exporting into a warehouse schema requires permission, naming/ownership, refresh/freshness policy, and a supported environment. Remove the `exports` block for a local-only exercise if the selected installation does not support it.

A saved query should specify:
- Stable query name and owner.
- Approved metric list and dimensions.
- Required filters / default date window where relevant.
- Expected consumer and data classification.
- Tests/reconciliation link.
- Version-control review path.

Use the command supported by the installed CLI to list and query saved queries, such as `mf list saved-queries` and `mf query --saved-query <name>` in supported self-hosted releases. Check `--help` before relying on parameters; dimensions and metric lists may be fixed by the saved query rather than overridable at query time.

### 7.3 Exports and caching

Exports and caching are not identical:
- **Export/materialization** writes a result into a warehouse relation or export target on a schedule or explicit run. It can make a common query easy to consume, but it introduces freshness, ownership, and rebuild questions.
- **Result caching** reuses a previous query result where the serving product and configuration support it.
- **Declarative caching / pre-aggregation** defines reusable precomputed data structures or policies, where supported by the specific product.
- **Warehouse caching** is the database's own behavior and is not the same as dbt Semantic Layer caching.

dbt's hosted Semantic Layer documents exports and caching features, but availability, setup, invalidation behavior, and supported cache types depend on the account/product version. Local self-hosted MetricFlow commands should not be assumed to provide the hosted cache service. Use current product documentation and verify freshness/invalidation with a controlled test before claiming cache behavior.

---

## 8. Serving metrics to BI tools, APIs, and notebooks

### 8.1 Local definitions versus hosted serving

There are two distinct workflows:

1. **Local development:** define models/metrics in YAML, parse and validate them, run MetricFlow queries against a configured warehouse, inspect generated SQL, and test the results.
2. **Hosted serving:** configure a dbt Semantic Layer environment and credentials, deploy the semantic definitions, then connect supported consumers through dbt's APIs/connectors.

Having a locally valid semantic model does not automatically provision an API endpoint, service token, JDBC connection, GraphQL schema, or BI connector.

### 8.2 JDBC and GraphQL

dbt Semantic Layer exposes APIs/connectivity options for querying governed metrics, including JDBC-based connectivity for supported clients and GraphQL API capabilities in documented product workflows. These are hosted/product integration capabilities and should be verified against the current dbt Semantic Layer API documentation, product plan, workspace setup, and permissions.

Operational controls:
- Use a dedicated service identity with least privilege.
- Store service tokens in a secret manager, not in a repository or notebook.
- Rotate credentials and monitor usage.
- Enforce the same model/metric authorization policy for API and BI access.
- Avoid exposing unrestricted raw SQL as a bypass around metric-level policy.
- Log query identity, metric names, filters, environment, and execution outcome while protecting sensitive values.

### 8.3 Integrations: Tableau, Power BI, Hex, Mode, notebooks

| Consumer | Integration approach | Availability caveat |
|---|---|---|
| Tableau | dbt Semantic Layer connector/JDBC-based connection where supported | Requires supported Tableau version, dbt host/environment credentials, and an eligible dbt plan; verify current connector prerequisites |
| Power BI | Use the current supported connector or supported JDBC/partner route, where available | Do not assume a universal native connector for every version; confirm current dbt integration catalog and licensing |
| Hex | Supported dbt Semantic Layer integration where available | Workspace permissions, connection setup, and plan may be required |
| Mode | Supported dbt Semantic Layer integration where available | Confirm current connector support and the intended dbt product track |
| Notebooks | Use an officially supported client/API/connector or query the warehouse directly for independent tests | A notebook that directly queries marts is not automatically governed by the Semantic Layer |
| Other BI tools | JDBC/API or partner integration when documented and supported | Test dimensions, filters, types, and auth behavior in the exact version |

Do not equate “can connect to the warehouse” with “queries through the semantic layer.” If a BI tool points directly at `fct_orders`, its own SQL can still bypass the governed metric definition.

### 8.4 Example consumption workflow

1. Publish and deploy the semantic definitions from the approved commit.
2. Configure the dbt Semantic Layer environment and grant a service account the minimum required access.
3. Configure a supported BI/notebook connection using the current official instructions.
4. Query `revenue` by `metric_time__month` and a customer dimension.
5. Compare the output to the known-answer fixture and independent SQL.
6. Test unauthorized access and confirm that sensitive dimensions are not exposed.
7. Record connector version, dbt environment, metric-definition commit, and test outcome.

This is an implementation workflow, not a claim that an external connection has been provisioned or executed in this lab.

---

## 9. Governance: ownership, certification, deprecation, and version control

### 9.1 Ownership and certification

A metric needs both a business owner and a technical steward.

- **Business owner:** approves meaning, inclusions/exclusions, time attribution, and reconciliation policy.
- **Analytics Engineering steward:** maintains the semantic YAML, model dependencies, tests, and releases.
- **Data platform owner:** operates credentials, warehouse access, query performance, and serving infrastructure.

An example governance register (metadata convention, not an automatic dbt feature):

| Metric | Business owner | Technical steward | Status | Required evidence |
|---|---|---|---|---|
| `revenue` | Finance | Analytics Engineering | Draft until finance reconciliation passes | Approved definition, source tie-out, regression tests |
| `active_customers` | Customer Analytics | Analytics Engineering | Candidate | Activity definition, distinct-count tests |
| `conversion_rate` | Product Analytics | Analytics Engineering | Candidate | Eligible denominator, event/status definition, attribution policy |
| `average_order_value` | Finance | Analytics Engineering | Candidate | Ratio component tests and currency policy |
| `running_revenue_mtd` | Finance | Analytics Engineering | Candidate | Time-spine and month-boundary tests |

Use project metadata such as `meta.owner`, `meta.domain`, and `meta.certification_status` only as a documented project convention. These fields do not automatically certify a metric, grant access, or create an approval workflow unless you build governance automation around them.

### 9.2 Certification policy

A metric may be marked certified only when:
- Its business definition and owner are approved.
- Grain, filters, time semantics, currency, null handling, and exclusions are documented.
- Semantic YAML validates.
- Key models and join keys have passing tests.
- Known-answer and dimension-level reconciliations pass.
- Finance or the accountable business owner has signed off when required.
- A rollback and deprecation path exists.

Certification is a governance state, not a magic YAML label. A tag or `meta` key is a useful signal but does not prove the metric is correct.

### 9.3 Version control and changes

Store semantic YAML with the SQL models in Git. Review changes to:
- Formula or aggregation.
- Metric filters and dimension availability.
- Entity names or join relationships.
- Default time dimension and date semantics.
- Currency conversion or unit.
- Output type/precision.
- Certification and ownership metadata.

For a breaking definition change, prefer an explicit migration: create a new metric name or versioned contract, communicate the difference, update consumers, measure adoption, and deprecate the old definition only after an agreed window. Do not silently change a certified metric because the new total looks more plausible.

### 9.4 Deprecation process

A practical deprecation sequence:
1. Identify all BI/API/notebook consumers using the metric.
2. Publish the replacement name and semantic difference.
3. Mark the old metric deprecated through the project's documented metadata/process.
4. Warn consumers and set a retirement date.
5. Track usage and migration completion.
6. Remove the old definition only after owner approval and validation that no required consumer depends on it.

A metadata flag alone does not notify every consumer or prevent old queries from running; build automation or use product features that explicitly support the required workflow.

---

## 10. Alternatives and architectural trade-offs

The options overlap but are not interchangeable. Evaluate where definitions live, who serves queries, how caching/pre-aggregation works, which consumers are first-class, and what operating burden your team accepts.

| Option | Core model | Strengths | Trade-offs / best fit |
|---|---|---|---|
| **dbt Semantic Layer / MetricFlow** | Metrics defined alongside dbt models; MetricFlow plans SQL; hosted serving via dbt platform | Reuses dbt models, tests, Git workflow, and SQL warehouse; semantic definitions can serve multiple supported consumers | Hosted serving/integrations require eligible product capabilities; query execution is warehouse-backed; verify current integration matrix |
| **Cube** | Semantic modeling and serving layer with APIs/SQL interfaces and caching/pre-aggregations depending on deployment | Strong embedded/multi-interface use cases; dedicated serving layer and cache/pre-aggregation options | Adds another service and operational surface; model compatibility, security, and sync need design |
| **LookML** | Semantic modeling inside Looker | Tight integration with Looker workflows, governed explores, and BI behavior | Strongly associated with Looker; potential duplication if dbt owns the same logic; consumer portability is narrower |
| **Looker semantic capabilities** | Looker uses LookML and associated modeling/query features | Mature BI-centered governance and analysis for organizations standardized on Looker | Not the same thing as a general cross-tool metric API; licensing and platform coupling matter |
| **AtScale** | Enterprise semantic/OLAP layer, often with aggregate awareness and BI/MDX/DAX/SQL interfaces | Useful where enterprise BI interoperability, governed aggregates, and large multidimensional workloads are central | Commercial platform and additional modeling/operations; evaluate cost and platform fit |
| **Snowflake Semantic Views** | Semantic definitions stored as Snowflake objects | Native to Snowflake; useful with Snowflake SQL and supported Snowflake AI/analytics capabilities | Tied to Snowflake's platform and capabilities; cross-warehouse portability requires another contract |
| **Databricks metric views** | Metric definitions represented in Databricks/Unity Catalog capabilities | Native integration with Databricks governance and analytics/AI ecosystem | Databricks-centric; verify current feature maturity, supported query paths, and workspace/runtime requirements |

### 10.1 How to choose

Choose dbt Semantic Layer when the team already owns metrics in dbt and wants supported downstream consumers to reuse those definitions without maintaining separate BI formulas.

Choose Cube when you need a dedicated serving layer, embedded analytics, multiple API protocols, or cache/pre-aggregation controls and are prepared to operate another layer.

Choose LookML/Looker when Looker is the main analytical interface and the organization values its native modeling and governance workflow.

Evaluate AtScale when enterprise semantic/OLAP requirements, large aggregate-aware workloads, and existing BI contracts justify a specialist platform.

Choose warehouse-native semantic/metric views when one warehouse is the strategic center and native governance/query capabilities outweigh cross-platform portability.

These products evolve quickly. The table is an architectural comparison, not a definitive claim about every plan, release, connector, or feature flag. Verify current vendor documentation and run a pilot using the same five metrics and test cases before selecting a platform.

---

## 11. Semantic layers for AI applications

### 11.1 Why AI needs governed metric context

A natural-language-to-SQL or agentic analytics application can hallucinate a formula, join the wrong grain, or interpret “active customer” differently from the organization. Giving an LLM direct unrestricted access to raw tables does not solve semantic consistency.

A governed architecture makes the semantic layer the metric authority:

```text
User question
    |
    v
LLM interprets intent and proposes metric/dimension/filter names
    |
    v
Allowlist + authorization + schema/metric validation
    |
    v
dbt Semantic Layer API / approved query interface
    |
    v
MetricFlow query plan -> warehouse SQL -> warehouse
    |
    v
Result + metric definition/version + filters + time range
    |
    v
LLM explains the result without changing its calculation
```

The LLM may translate “monthly revenue by customer” into a request for `revenue` grouped by `metric_time__month` and an approved customer dimension. It should not be allowed to redefine revenue by writing arbitrary SQL if the policy requires governed metrics.

### 11.2 Safe request contract

An application-side tool contract can look like this (illustrative pseudocode, not a dbt-provided API schema):

```json
{
  "metric_names": ["revenue"],
  "group_by": ["metric_time__month"],
  "filters": [
    {
      "dimension": "order_status",
      "operator": "equals",
      "value": "completed"
    }
  ],
  "time_range": {
    "start": "2026-01-01",
    "end": "2026-03-31"
  }
}
```

Before executing:
- Validate metric and dimension names against the approved semantic manifest/API.
- Check the caller's authorization for the environment, metric, dimension, and data classification.
- Enforce date-range and result-size limits.
- Reject unsupported operators, unknown fields, and raw SQL.
- Apply row/column-level policies at the serving/warehouse layer, not only in the prompt.
- Record the exact metric definitions, filters, and time range used.

After executing:
- Return values with metric name, units, time range, filters, and freshness context.
- Preserve query provenance and definition version.
- Tell the user when the metric is unavailable or ambiguous rather than substituting a guessed calculation.
- Never ask the LLM to silently “fix” a result by changing the query until it matches expectations.

### 11.3 MCP and API availability

Current dbt materials describe connecting AI tools to governed metrics through dbt's MCP server and Semantic Layer workflows. Treat this as a product/integration capability whose setup, tool coverage, authentication, and access control depend on current documentation and account configuration. Do not assume a generic MCP server automatically inherits every BI permission or that it supports every operation.

A secure implementation should:
1. Authenticate each user or trusted service identity.
2. Authorize every requested metric/dimension/filter.
3. Query only through approved metric definitions.
4. Keep secrets out of prompts and model context.
5. Log requests and result provenance with privacy controls.
6. Test prompt-injection attempts that ask the agent to ignore governance, reveal restricted dimensions, or execute arbitrary SQL.
7. Provide an explicit “definition not found” response instead of inventing a metric.

---

## 12. Hands-on lab — `experiments/07_semantic_layer/`

### 12.1 Lab objective

Add governed semantic definitions to the existing `fct_orders` and `dim_customers` models, define simple/ratio/cumulative metrics, validate them, query by dimensions and time grain, compare MetricFlow with independent SQL, and—if eligible access is available—connect a BI tool or notebook to the hosted Semantic Layer.

### 12.2 Prerequisites

- The dbt project from previous lessons builds `fct_orders` and `dim_customers`.
- You know the grain and column names and have tested `order_id`, `customer_id`, and dimension uniqueness.
- A configured dbt adapter and warehouse.
- A pinned dbt/MetricFlow release with the v1.12+ metric syntax used here.
- The time-spine model and required package installed, if the project needs it.
- A MetricFlow-supported adapter for actual `mf` validation/query execution; DuckDB alone may not satisfy this prerequisite for the selected release.
- For hosted API/BI work: eligible dbt plan, supported warehouse, configured Semantic Layer environment, credentials/service token, and a supported connector.
- A known-answer fixture or test dataset. Never treat example values in this lesson as actual project results.

### 12.3 Lab file layout

```text
experiments/
└── 07_semantic_layer/
    ├── README.md
    ├── metric_dictionary.md
    ├── models/
    │   └── marts/
    │       ├── fct_orders.yml
    │       ├── dim_customers.yml
    │       ├── time_spine_daily.sql
    │       └── time_spine.yml
    ├── seeds/
    │   └── orders_fixture.csv
    ├── tests/
    │   └── assert_metric_known_answers.sql
    ├── analyses/
    │   └── monthly_revenue_handwritten.sql
    └── evidence/
        └── README.md
```

The files under `experiments/07_semantic_layer/models/` are an exercise layout. dbt only discovers models/YAML inside configured `model-paths`; either copy/merge the files into the actual project `models/` directory or add the lab directory to `model-paths` deliberately. Do not assume nested exercise files are automatically parsed.

### 12.4 Step 1 — record the metric dictionary

Create `metric_dictionary.md` using Section 2. For each metric, write the exact formula, grain, filters, owner, status, and known-answer test. Confirm whether `total_payment_cents` includes failed payments, refunds, or cancelled orders. If unknown, keep `revenue` explicitly in draft status.

### 12.5 Step 2 — configure the semantic models

Copy/adapt the YAML from Sections 3.3–3.6 into the configured model path:
- `fct_orders.yml`: order/customer entities, `order_date`, categorical status, revenue/order count/active customers/completed orders, AOV, completion rate, and MTD revenue.
- `dim_customers.yml`: primary customer entity and approved categorical dimensions.
- `time_spine.yml`: daily time spine declaration.

Check for duplicate YAML keys and merge metric entries into the existing `metrics:` list. Ensure `order_status = 'completed'` matches the real source. If the metric YAML is version-incompatible, use the installed version's documented spec; do not mix v1.12+ syntax with legacy `measures:` examples.

### 12.6 Step 3 — build, parse, and validate

From the dbt project root, ensure the fixture seed is actually loaded before running its singular test. If the lab directory is outside configured `seed-paths` / `model-paths`, first move or merge the files into the project paths or configure those paths deliberately.

```bash
dbt deps
dbt seed --select orders_fixture
dbt build --select fct_orders dim_customers time_spine_daily
dbt parse
mf validate-configs
dbt test --select assert_metric_known_answers
```

Expected result: the configured models build, MetricFlow validates the semantic configuration, and the singular test returns zero failure rows. This is an expected outcome, not a claim that the commands have been executed here. Exact command selection and CLI names may differ by installed version; check `dbt --help` and `mf --help`. Record actual output, versions, adapter, and commit in `evidence/README.md`. MetricFlow steps require a supported adapter; the prior lessons' DuckDB setup alone does not establish that prerequisite.

If validation fails, first check model/YAML discovery, model name/column spelling, duplicate keys, entity uniqueness, metric names, and version-specific syntax.

### 12.7 Step 4 — query by dimension and time grain

```bash
mf query --metrics revenue --group-by metric_time__month
mf query --metrics revenue,average_order_value --group-by metric_time__month
mf query --metrics active_customers --group-by metric_time__month
mf query --metrics conversion_rate --group-by metric_time__month
mf query --metrics running_revenue_mtd --group-by metric_time
mf query --metrics revenue --group-by customer__full_name,metric_time__month
```

Use `mf list metrics`, `mf list dimensions`, and `mf list entities` to confirm names accepted by your installed release. If a customer name dimension is restricted, use a safe non-PII dimension instead. Record query commands, environment, commit SHA, output shape, and any deviations.

### 12.8 Step 5 — compare generated SQL with handwritten SQL

Run a query with the documented compile/explain flag for your CLI version. Save the generated SQL in a private/evidence location if it does not contain sensitive literals. Run the equivalent hand-written SQL from `analyses/monthly_revenue_handwritten.sql`.

Compare:
- Monthly group keys and missing months.
- Revenue, order count, and AOV values.
- Filters and event-date semantics.
- Customer dimension join cardinality.
- Numeric precision and null/zero behavior.

The hand-written SQL must calculate from the same mart and definition, not from an unrelated raw source. If the results disagree, investigate the generated plan, join keys, filters, and aggregation grain before editing the metric.

### 12.9 Step 6 — known-answer and fan-out tests

Load the fixture from Section 6.1 into a test relation or adapt it to the project's seed convention. Calculate expected values independently. Test the dimension uniqueness assumption by intentionally duplicating one customer key in a disposable test relation and demonstrate how a naïve join inflates revenue.

Do not contaminate the production mart to perform this exercise. Use an isolated schema/seed fixture. Add assertions for the expected January/February values, AOV, distinct active customers, completion rate, and MTD boundary.

### 12.10 Step 7 — optional hosted BI/API connection

If you have the required dbt plan, supported warehouse, configured environment, and integration access:
1. Deploy the semantic definitions from an approved commit/environment.
2. Create or obtain a least-privilege service identity/token.
3. Follow the current official instructions for a supported Tableau, Power BI, Hex, Mode, JDBC, GraphQL, or notebook integration.
4. Query monthly revenue and AOV through the semantic layer.
5. Verify that unauthorized users cannot access restricted metrics/dimensions.
6. Compare the connector's results to the known-answer fixture and local query.
7. Record connector version, dbt environment, permission scope, and test result.

If access is not available, complete the local MetricFlow lab and document the missing prerequisite. Do not mark the API/integration step complete just because the local YAML validates.

### 12.11 Troubleshooting

| Symptom | Likely cause | Corrective action |
|---|---|---|
| `semantic_manifest.json` is empty or metrics are missing | YAML is outside configured `model-paths`, parse not rerun, or semantic model disabled | Check model paths, `semantic_model.enabled`, and rerun `dbt parse` |
| Unknown metric or dimension | Name mismatch or wrong version-specific dimension naming | Run the CLI's list commands and use the reported name |
| Entity join fails or is unavailable | Entity name/key mismatch, missing relationship, or ambiguous join path | Verify the same semantic entity name, key types, uniqueness, and model grain |
| Revenue is inflated after adding customer dimension | Duplicate customer keys or another many-side join caused fan-out | Test dimension uniqueness, inspect join path, and fix model grain |
| AOV differs from average of monthly AOVs | Averaging averages instead of recomputing from components | Calculate total revenue / total eligible orders at the target grain |
| Cumulative metric errors or has missing dates | Time spine not configured, not built, too short, or grain metadata incorrect | Verify `time_spine`, base column granularity, range, and date types |
| `mf` command not found | MetricFlow CLI is absent or installed version uses another command surface | Check installed packages/version and follow the official installation guide |
| `--explain` / `--compile` rejected | Flag differs by self-hosted/hosted CLI or release | Use `mf query --help` or the hosted `dbt sl` command help |
| BI connection cannot authenticate | Missing entitlement, wrong environment ID/host/token, or insufficient permission | Verify plan, token scope, environment, supported connector version, and logs |
| Finance total differs | Revenue semantics or source timing/filters differ | Reconcile policy, payment status, refunds, tax, date, currency, and late data with Finance |

### 12.12 Completion criteria

- [ ] The `fct_orders` and `dim_customers` semantic models parse and describe their real columns and grains.
- [ ] Primary/foreign entity relationships are correct and backed by uniqueness/relationship tests.
- [ ] Revenue, active customers, AOV, completion-rate ratio, and MTD cumulative revenue have documented formulas, filters, grains, and owners.
- [ ] The metric dictionary is reviewed; the revenue definition is not certified until finance semantics are approved.
- [ ] Time spine is configured, built, and checked for coverage and calendar boundaries.
- [ ] `mf validate-configs` passes in the actual installed environment using a MetricFlow-supported adapter.
- [ ] MetricFlow queries run by dimension and time grain, with outputs saved as evidence.
- [ ] Generated SQL is compared with independently written SQL at the same grain.
- [ ] A fan-out test demonstrates the risk of duplicate dimension keys.
- [ ] Ratio calculations use additive numerator/denominator components at the requested grain.
- [ ] Known-answer values and time-boundary tests pass for the fixture.
- [ ] An API/BI/notebook connection is tested if required access exists; otherwise the missing prerequisites are documented.
- [ ] Ownership, certification, versioning, and deprecation are defined for production metrics.

---

## 13. Common mistakes and design rules

1. **Building the semantic layer before marts are stable.** Fix grain, keys, business logic, and tests first.
2. **Calling every monetary sum revenue.** Distinguish captured payments, gross sales, net sales, recognized revenue, tax, and refunds.
3. **Treating entity metadata as a data-quality constraint.** Entities do not make duplicate keys unique; test the physical data.
4. **Assuming joins are always safe.** Check cardinality and fan-out for every path.
5. **Averaging averages or ratios.** Preserve additive numerator/denominator components and calculate at the output grain.
6. **Counting active customers additively across time.** Distinct counts are non-additive; recompute for the requested period.
7. **Ignoring time-spine coverage.** A cumulative metric can be wrong around gaps and window boundaries.
8. **Mixing YAML generations.** Do not combine v1.12+ simple-metric syntax with legacy `measures:` examples without a deliberate migration.
9. **Assuming local validation means hosted serving is configured.** APIs, tokens, integrations, plans, and warehouse support are separate prerequisites.
10. **Treating a `meta` field as certification or access control.** Implement the policy in the actual serving and authorization layer.
11. **Comparing only grand totals.** Compare grouped keys, filters, null behavior, and boundary cases.
12. **Allowing an LLM to invent metric logic.** Validate requested names and execute only approved definitions through the governed interface.

---

## 14. Roadmap checkpoint

Before moving to Topic 08 — Deploying dbt with Airflow and dbt Cloud, explain aloud:

- Why the same metric can disagree across dashboards and how the semantic layer addresses the consistency problem.
- How the `orders` and `customers` semantic models connect through the `customer` entity.
- How MetricFlow plans a join and why a false uniqueness assumption can inflate revenue.
- The difference between a simple metric, ratio metric, derived metric, cumulative metric, and a funnel conversion metric.
- Why AOV must be recomputed from total revenue and order count instead of averaging subgroup averages.
- What a time spine provides and why MTD metrics need correct time coverage.
- How to validate the configuration, query a metric, inspect generated SQL, and compare it with independent SQL.
- What must be in place before a metric is certified and reconciled with Finance.
- The trade-offs among dbt Semantic Layer, Cube, LookML/Looker, AtScale, and warehouse-native metric views.
- How an AI application can request governed metrics without bypassing definitions or authorization.

---

## References for version-sensitive implementation

Use these official or primary-source references to confirm syntax and current availability before implementing:

- dbt Semantic Layer overview: https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl
- MetricFlow overview: https://docs.getdbt.com/docs/build/about-metricflow
- MetricFlow commands and local/hosted command differences: https://docs.getdbt.com/docs/build/metricflow-commands
- dbt Semantic Layer quickstart (v1.12+ syntax): https://docs.getdbt.com/guides/sl-qs
- MetricFlow time spine guide: https://docs.getdbt.com/guides/mf-time-spine
- Cumulative metrics: https://docs.getdbt.com/docs/build/cumulative
- Conversion metrics: https://docs.getdbt.com/docs/build/conversion
- Tableau integration prerequisites: https://docs.getdbt.com/docs/platform-integrations/semantic-layer/tableau
- MetricFlow source repository: https://github.com/dbt-labs/metricflow
- Snowflake Semantic Views overview: https://docs.snowflake.com/en/user-guide/views-semantic/overview
- Databricks metric-view documentation: https://docs.databricks.com/en/metric-views/index.html

Product plans, APIs, warehouse support, command names, and YAML specifications evolve. Pin versions in the project and re-check the documentation for that version before deploying.
