# Snowflake Cost Monitoring and Resource Monitors

**Roadmap location:** `Stage 2C — Data Engineering_3/03-Snowflake-Deep-Dive/10-cost-monitoring-and-resource-monitors.md`  
**Level:** Beginner → Intermediate → Advanced  
**Hands-on lab:** `experiments/10_cost/`  
**Audience:** Data engineers, analytics engineers, platform engineers, warehouse administrators, and FinOps practitioners

> **Accuracy note:** Snowflake pricing, service names, feature availability, view columns, and account controls can change. The SQL below targets documented `SNOWFLAKE.ACCOUNT_USAGE` views and common warehouse configurations. Verify current columns and privileges in your account before operationalizing it. Cost history is delayed; do not treat it as a real-time kill switch. This lesson contains no measured results from a live Snowflake account.

---

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Explain compute, storage, data transfer, cloud-services adjustments, and serverless consumption without conflating credits with dollars.
2. Distinguish resource monitors, budgets, and historical usage views—and select the right control for a workload.
3. Use Snowsight and `ACCOUNT_USAGE` to identify spend by service, warehouse, query, role, and query tag where attribution is available.
4. Rank the top 20 queries by attributed compute credits for a clearly bounded current-week window.
5. Diagnose expensive SQL using query profiles, pruning, join cardinality, spilling, repeated scans, and cache behaviour.
6. Optimize warehouse uptime, size, query shape, storage retention, and serverless features using before-and-after evidence.
7. Build a cost dashboard, run a weekly FinOps review, and prepare a concise report with evidence, uncertainty, and owners.

## 2. Prerequisites and lab safety

You should already understand:

- Snowflake storage/compute separation and virtual warehouses (Topics 01–02).
- Micro-partitions, pruning, clustering, and query profiles (Topic 03).
- Loading patterns, streams, tasks, and dynamic tables (Topics 04–05).
- Snowpark and SQL execution (Topic 06).
- Time Travel, retention, and cloning (Topic 07).
- RBAC, grants, masking, and row access (Topic 08).
- Secure sharing and provider/consumer cost responsibilities (Topic 09).
- SQL, CTEs, window functions, and basic query tuning.

**Safety rules:** use a dedicated non-production database and small warehouse; apply a resource monitor before experiments; set auto-suspend; do not suspend shared production warehouses without an owner-approved plan; never run unbounded scans on production merely to learn; and drop only objects created for this lab. Resource monitors and usage views have different scopes and delays—neither replaces workload design, budgets, alerts, or a cost review.

---

## 3. The Snowflake cost model (beginner)

### 3.1 Cost components

```text
Snowflake account spend
├── Compute / credits
│   ├── User-managed virtual warehouses (queries, loading, web workloads)
│   ├── Serverless features (e.g. Snowpipe, automatic clustering,
│   │   Search Optimization, serverless tasks, dynamic-table refreshes)
│   └── Other feature-specific compute (availability depends on account/features)
├── Storage
│   ├── Active table data and retained historical versions
│   ├── Internal-stage files
│   └── Fail-safe / other storage categories where applicable
├── Data transfer / egress
│   └── Transfers across supported cloud/region boundaries and destinations
└── Cloud services
    └── Metadata, coordination, authentication, query compilation, etc.
        └── Billing adjustments may apply; raw usage is not always billed 1:1
```

| Component | What drives it | Where to investigate | Important distinction |
|---|---|---|---|
| Warehouse compute | Warehouse size, active time, concurrency, scaling, query work, idle time | `WAREHOUSE_METERING_HISTORY`, Snowsight | Warehouse credits are not the same as query-attributed credits; idle time exists. |
| Serverless compute | Feature-specific workload, such as Snowpipe or automatic clustering | `METERING_HISTORY`, feature-specific histories, Budgets | Warehouse resource monitors do not control serverless feature consumption. |
| Storage | Average billable bytes over time; table and stage data, retained versions | `STORAGE_USAGE`, preferably `STORAGE_DAILY_HISTORY` for bill reconciliation | Storage usage views use different measurement approaches; don't assume all bytes map directly to invoice bytes. |
| Data transfer | Egress and cross-region/cloud transfer | Cost-management views and transfer-related metering | Rates vary by source region, destination, and contract. Ingress and egress are not interchangeable. |
| Cloud services | Snowflake-managed service activity | `METERING_DAILY_HISTORY`, `METERING_HISTORY` | Billing adjustment rules can make billed credits lower than raw consumption. |

**Credit-to-dollar calculation:**

`estimated compute cost = consumed billable credits × applicable contract price per credit`

For example, if a hypothetical workload consumes **120 billable credits** and the applicable contract rate is **$2.40/credit**, the illustrative compute amount is `120 × $2.40 = $288`. This is a teaching example, not a quote or a statement about your Snowflake price. Actual rates depend on contract, cloud, region, edition, service, and commercial terms; storage and transfer may be billed separately.

### 3.2 Five measures that must not be conflated

- **Elapsed time:** wall-clock duration of a query. A fast query can run on a large warehouse; a slow query can spend time waiting or scanning inefficiently.
- **Query-attributed credits:** an allocation of compute usage to query execution. It excludes warehouse idle time and may omit some feature-specific costs.
- **Warehouse credits:** credits consumed while a warehouse runs, including time not cleanly attributable to individual queries.
- **Serverless consumption:** feature-specific compute outside user-managed warehouse runtime; inspect the relevant service history and budgets.
- **Total account spend:** all applicable compute, storage, data transfer, and cloud-services billing, with relevant adjustments. It is not the sum of a single query's elapsed time or credits.

### 3.3 Visibility, control, and optimization

```text
VISIBILITY                         CONTROL                         OPTIMIZATION
Snowsight cost pages               Resource monitors               Auto-suspend/right-size
ACCOUNT_USAGE history              Budgets + alerts                Pruning/join/query design
Query tags + warehouse ownership   Query timeouts/guardrails       Storage/retention cleanup
Dashboard + attribution             Operational runbooks             Before/after validation
```

Visibility tells you what happened; controls reduce or signal risk; optimization changes the underlying cost. Use all three.

---

## 4. Resource monitors, budgets, and alerts

### 4.1 Resource monitors

A **resource monitor** tracks credit usage associated with assigned user-managed warehouses or at account scope, and can notify or suspend/disable eligible warehouses when thresholds are reached. It is useful for controlling warehouse credit use, but it is **not** a universal spend cap.

Important limits:

- Resource monitors apply to warehouses; they do not control serverless features such as Snowpipe, automatic clustering, Search Optimization, or serverless tasks.
- A monitor's usage includes relevant warehouse and supporting cloud-services usage under Snowflake's monitor semantics; it is not a precise invoice calculator.
- Threshold actions can lag actual consumption. Running queries, cloud-services activity, and suspension timing can cause usage to exceed a threshold.
- Account-level and warehouse-level monitors have different scopes. A warehouse can be assigned to only one warehouse-level monitor; an account monitor is separate.
- Creating resource monitors requires `ACCOUNTADMIN` under the documented standard model. Delegate `MONITOR`/`MODIFY` privileges for ongoing administration where appropriate.
- Notifications must be configured/enabled; do not assume a trigger automatically reaches the right team.

**Safer threshold pattern:** alert at 70–80%, suspend at a lower-than-100% threshold for noncritical workloads, and reserve immediate suspension for workloads where cancellation is acceptable. For critical workloads, define an explicit exception/approval process rather than blindly attaching an immediate-suspend policy.

Example for a dedicated lab warehouse (execute with an authorized account administrator):

```sql
USE ROLE ACCOUNTADMIN;

-- Create the dedicated lab warehouse first; do not reuse a production warehouse.
CREATE WAREHOUSE WH_LAB_COST
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

-- Fail if the monitor name already exists; inspect it rather than replacing it.
CREATE RESOURCE MONITOR RM_LAB_COST
  WITH CREDIT_QUOTA = 25
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS
    ON 70 PERCENT DO NOTIFY
    ON 85 PERCENT DO SUSPEND
    ON 100 PERCENT DO SUSPEND_IMMEDIATE;

ALTER WAREHOUSE WH_LAB_COST SET RESOURCE_MONITOR = RM_LAB_COST;
```

This is intentionally a **small, illustrative lab quota**. `SUSPEND_IMMEDIATE` cancels running work and is inappropriate for many production workloads. Use only after reviewing the blast radius. Confirm trigger syntax and current feature support in the target account's Snowflake documentation before deployment.

Inspect configuration:

```sql
SHOW RESOURCE MONITORS;
SHOW WAREHOUSES;
```

For a production rollout, create a monitor per workload or cost center where isolation is important; a shared quota can let one team's activity consume another team's budget. Account-level monitors are a backstop, not a replacement for per-workload ownership. The sample deliberately uses `CREATE`, not `CREATE OR REPLACE`, to fail safely if the name already exists. `NOTIFY` sends notifications to account administrators who have enabled notifications; explicitly verify notification settings and recipient routing before relying on alerts. The sample warehouse is created as a dedicated lab object, so cleanup can safely remove it only after verifying ownership and dependencies.

### 4.2 Budgets and alerts

Snowflake **Budgets** provide spend monitoring for supported objects and serverless feature categories and can send notifications when projected monthly spending is expected to exceed a limit. Supported service/object combinations vary; consult the current support matrix. Budgets are visibility and alerting mechanisms, not equivalent to hard, instant termination of every service.

| Mechanism | Main purpose | Can suspend a warehouse? | Can monitor supported serverless spend? | Timing/limitations |
|---|---|---:|---:|---|
| Resource monitor | Warehouse credit threshold control | Yes, subject to configuration and action | No, not as a serverless spend control | Delayed/threshold-based; not exact spend enforcement |
| Account/custom budget | Spend visibility and projected-overrun alerts | No general hard suspension action | Yes, for supported services/objects | Measurement and notification delay; support matrix matters |
| Usage-history SQL | Retrospective investigation and reporting | No | Yes, when corresponding history exists | Views have different latency and retention |
| Query timeout/warehouse guardrails | Bound specific runaway query or workload behaviours | Can stop or constrain query work, depending on mechanism | Not a universal control for serverless services | Needs workload-specific testing |

A custom budget can be created as a Snowflake budget instance. The following is a concrete **illustrative** SQL pattern; use a dedicated database/schema, verified email address, and a role granted the documented privileges. Budget activation, notification integrations, and privileges must be configured for the account. The budget's credit limit is for alerting/forecasting, not an automatic warehouse-suspension threshold.

```sql
-- Run setup DDL with an authorized administrator. Use a verified recipient.
USE ROLE ACCOUNTADMIN;
CREATE DATABASE COST_GOVERNANCE_DB;
CREATE SCHEMA COST_GOVERNANCE_DB.BUDGETS;

CREATE NOTIFICATION INTEGRATION COST_BUDGET_EMAIL
  TYPE = EMAIL
  ENABLED = TRUE
  ALLOWED_RECIPIENTS = ('<VERIFIED_EMAIL_ADDRESS>');
GRANT USAGE ON INTEGRATION COST_BUDGET_EMAIL TO APPLICATION SNOWFLAKE;

CREATE ROLE COST_BUDGET_OWNER;
GRANT USAGE ON DATABASE COST_GOVERNANCE_DB TO ROLE COST_BUDGET_OWNER;
GRANT USAGE ON SCHEMA COST_GOVERNANCE_DB.BUDGETS TO ROLE COST_BUDGET_OWNER;
GRANT DATABASE ROLE SNOWFLAKE.BUDGET_CREATOR TO ROLE COST_BUDGET_OWNER;
GRANT DATABASE ROLE SNOWFLAKE.USAGE_VIEWER TO ROLE COST_BUDGET_OWNER;
GRANT CREATE SNOWFLAKE.CORE.BUDGET ON SCHEMA COST_GOVERNANCE_DB.BUDGETS
  TO ROLE COST_BUDGET_OWNER;

-- A budget owner needs APPLYBUDGET on any resource it adds.
-- Grant that privilege only to the intended lab resources, as approved.
GRANT APPLYBUDGET ON WAREHOUSE WH_LAB_COST TO ROLE COST_BUDGET_OWNER;

USE ROLE COST_BUDGET_OWNER;
USE SCHEMA COST_GOVERNANCE_DB.BUDGETS;
CREATE SNOWFLAKE.CORE.BUDGET LAB_WAREHOUSE_BUDGET();
CALL LAB_WAREHOUSE_BUDGET!SET_SPENDING_LIMIT(25);
CALL LAB_WAREHOUSE_BUDGET!SET_EMAIL_NOTIFICATIONS(
  'COST_BUDGET_EMAIL', '<VERIFIED_EMAIL_ADDRESS>');
CALL LAB_WAREHOUSE_BUDGET!ADD_RESOURCE(
  SELECT SYSTEM$REFERENCE('WAREHOUSE', 'WH_LAB_COST', 'SESSION', 'APPLYBUDGET'));
```

The sample uses a 25-credit monthly alert limit only as an example. A custom budget is distinct from the account budget: activating the account budget is a separate setup step and is not performed by this snippet. Budget setup is version- and privilege-sensitive; consult [Budgets](https://docs.snowflake.com/en/user-guide/budgets), [custom budgets](https://docs.snowflake.com/en/user-guide/budgets/custom-budget), and [budget troubleshooting](https://docs.snowflake.com/en/user-guide/budgets/troubleshoot). The account budget may need separate activation and configuration. A sensible budget should define scope, owner, monthly limit, notification destination, escalation route, and what action the owner takes.

After testing, clean up only the budget objects created for this exercise. Verify names and dependencies first; these commands are intentionally commented out so a copied script cannot drop an existing shared object accidentally:

```sql
-- DROP BUDGET COST_GOVERNANCE_DB.BUDGETS.LAB_WAREHOUSE_BUDGET;
-- DROP ROLE COST_BUDGET_OWNER;
-- DROP NOTIFICATION INTEGRATION COST_BUDGET_EMAIL;
-- DROP DATABASE COST_GOVERNANCE_DB;
```

### 4.3 Snowsight cost management

Use Snowsight's cost-management pages for an initial triage:

1. Start with account-level cost by service and time period.
2. Separate warehouse metering from serverless services, storage, and transfer.
3. Drill into warehouse usage and compare it with query-attributed usage.
4. Identify cost spikes by date, warehouse, feature, or object.
5. Export or reproduce important metrics using `ACCOUNT_USAGE` for repeatable reporting.

Menu labels can change. Current documentation describes **Admin → Cost management → Consumption** for account-level compute, storage, and data-transfer usage. Cost data can take up to 72 hours to appear in the Consumption page; this is not a real-time alerting surface. Cross-account organization views may require `ORGADMIN` as well as the appropriate account role. Use the current Snowsight documentation rather than relying on a fixed UI screenshot. For currency-denominated reporting, use the Snowsight Consumption view or the documented `ORGANIZATION_USAGE.USAGE_IN_CURRENCY_DAILY` view where your role/account access permits; do not convert credits to dollars without the applicable contract rate.

---

## 5. Usage history and attribution (intermediate)

### 5.1 Where each view fits

| View | Primary purpose | Typical caveat |
|---|---|---|
| `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY` | Hourly warehouse credits | Usually up to ~3 hours of latency for core columns; cloud-services columns can lag longer. It includes warehouse usage, not just query execution. |
| `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY` | Query text/metadata, role, warehouse, elapsed time, bytes scanned/spilled | Up to ~45 minutes of latency; up to 365 days retained in documented Account Usage view. Some fields are NULL or unavailable for some query types. |
| `SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE` | Daily account storage and internal-stage bytes | Up to ~2 hours latency; not the closest billing reconciliation source. Includes table bytes (including Time Travel), stage bytes, and Fail-safe bytes. |
| `SNOWFLAKE.ACCOUNT_USAGE.STORAGE_DAILY_HISTORY` | Storage measurements closer to billing | Prefer for bill reconciliation; still follow its documented latency and semantics. |
| `SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY` | Daily account credit usage and cloud-services adjustment | Up to ~3 hours latency; use `CREDITS_BILLED` for the billed-credit total represented by this view (not total spend including storage and transfer). |
| `SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY` | Hourly service-level usage, including many serverless services | Service-specific latency differs; cloud-services columns can lag up to ~6 hours and some streaming services longer. |
| `SNOWFLAKE.ACCOUNT_USAGE.SERVERLESS_TASK_HISTORY` | Serverless task usage by task and time window | Up to ~3 hours latency; `CREDITS_USED` may be represented as text, so cast safely for arithmetic. |
| `SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY` | Compute credits attributed to individual queries, query tag, user, warehouse, etc. | Up to ~8 hours latency; excludes idle warehouse time, short queries around 100 ms or less, and Adaptive Warehouse jobs. Use `QUERY_METERING_HISTORY` for per-query credit usage on Adaptive Warehouses. |

History views require appropriate privileges on the `SNOWFLAKE` database / imported database roles, or another authorized access path. Do not assume a worksheet role can read every view. Grant read access through a dedicated monitoring role according to least privilege. Current Snowflake documentation maps `QUERY_ATTRIBUTION_HISTORY` to `USAGE_VIEWER` and/or `GOVERNANCE_VIEWER`, and `QUERY_HISTORY` to `GOVERNANCE_VIEWER`; use the current Account Usage access table to confirm each view. For example, an account administrator can provision a narrowly scoped lab role as follows:

```sql
USE ROLE ACCOUNTADMIN;
CREATE ROLE IF NOT EXISTS COST_MONITOR_LAB;
GRANT DATABASE ROLE SNOWFLAKE.USAGE_VIEWER TO ROLE COST_MONITOR_LAB;
GRANT DATABASE ROLE SNOWFLAKE.GOVERNANCE_VIEWER TO ROLE COST_MONITOR_LAB;
-- Grant COST_MONITOR_LAB to the intended lab user/role through your approved RBAC process.
```

These grants provide broad visibility into the relevant usage/governance views, so do not grant them to general end users without review. Where the account's role model differs, grant only the required view access. Check `SHOW VIEWS IN SCHEMA SNOWFLAKE.ACCOUNT_USAGE` or query `DESC VIEW` to verify the exact schema exposed in your account.

### 5.2 Daily account metering and cloud-services adjustment

```sql
-- Use UTC consistently when reconciling Account Usage with organization usage or billing.
ALTER SESSION SET TIMEZONE = 'UTC';

-- Account-level daily billed credits, by service day.
SELECT
    USAGE_DATE,
    SUM(CREDITS_USED_COMPUTE) AS CREDITS_COMPUTE,
    SUM(CREDITS_USED_CLOUD_SERVICES) AS CREDITS_CLOUD_SERVICES_RAW,
    SUM(CREDITS_ADJUSTMENT_CLOUD_SERVICES) AS CLOUD_SERVICES_ADJUSTMENT,
    SUM(CREDITS_BILLED) AS CREDITS_BILLED
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY
WHERE USAGE_DATE >= DATEADD(day, -30, CURRENT_DATE())
  AND USAGE_DATE < CURRENT_DATE()
GROUP BY USAGE_DATE
ORDER BY USAGE_DATE;
```

Use this to see account-wide daily billed **credits** across supported metered compute services, not total account spend and not query/team attribution. `CREDITS_BILLED` includes compute credits and cloud-services adjustment semantics represented by this view; it does not include storage and data-transfer charges, which must be reviewed separately. Cloud-services billing adjustments mean raw usage and billed credits can differ. For finance reconciliation, compare the applicable usage views, currency-denominated cost data, and billing statements for the same time zone and period.

### 5.3 Daily warehouse credits

```sql
SELECT
    START_TIME::DATE AS USAGE_DATE,
    WAREHOUSE_NAME,
    SUM(CREDITS_USED_COMPUTE) AS COMPUTE_CREDITS,
    SUM(CREDITS_USED_CLOUD_SERVICES) AS CLOUD_SERVICES_CREDITS_RAW,
    SUM(CREDITS_USED) AS TOTAL_CREDITS_RAW
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP())
  AND START_TIME < CURRENT_TIMESTAMP()
GROUP BY 1, 2
ORDER BY USAGE_DATE DESC, TOTAL_CREDITS_RAW DESC;
```

`CREDITS_USED` in this view is raw warehouse usage and is not guaranteed to equal the credits billed after cloud-services adjustments. Use the daily metering view for billed account-level reconciliation. `START_TIME::DATE` follows the session time zone; set `TIMEZONE = UTC` before generating daily comparisons and use the same time-zone convention across all reports.

### 5.4 Current-week top 20 queries by attributed compute credits

This query ranks **queries** by `CREDITS_ATTRIBUTED_COMPUTE`, using a week that starts Monday at 00:00 in the session's current time zone and ends at the time the query runs. Set the session time zone consistently for reporting. `QUERY_ATTRIBUTION_HISTORY` has delayed ingestion, so the current week is incomplete.

```sql
ALTER SESSION SET TIMEZONE = 'UTC';

WITH week_bounds AS (
    SELECT
        DATEADD(day, 1 - DAYOFWEEKISO(CURRENT_DATE()), CURRENT_DATE())::TIMESTAMP_LTZ AS week_start,
        CURRENT_TIMESTAMP() AS week_end
), attributed AS (
    SELECT
        a.QUERY_ID,
        a.QUERY_TAG,
        a.USER_NAME,
        a.WAREHOUSE_NAME,
        a.START_TIME,
        a.END_TIME,
        a.CREDITS_ATTRIBUTED_COMPUTE,
        COALESCE(a.CREDITS_USED_QUERY_ACCELERATION, 0) AS QUERY_ACCELERATION_CREDITS
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY a
    CROSS JOIN week_bounds b
    WHERE a.START_TIME >= b.week_start
      AND a.START_TIME < b.week_end
), enriched AS (
    SELECT
        a.*,
        q.ROLE_NAME,
        q.EXECUTION_TIME,
        q.QUEUED_OVERLOAD_TIME,
        q.BYTES_SCANNED,
        q.BYTES_SPILLED_TO_LOCAL_STORAGE,
        q.BYTES_SPILLED_TO_REMOTE_STORAGE,
        q.ROWS_PRODUCED,
        q.QUERY_TEXT
    FROM attributed a
    LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q
      ON q.QUERY_ID = a.QUERY_ID
)
SELECT
    QUERY_ID,
    START_TIME,
    END_TIME,
    USER_NAME,
    ROLE_NAME,
    WAREHOUSE_NAME,
    COALESCE(NULLIF(QUERY_TAG, ''), 'UNTAGGED') AS QUERY_TAG,
    CREDITS_ATTRIBUTED_COMPUTE,
    QUERY_ACCELERATION_CREDITS,
    CREDITS_ATTRIBUTED_COMPUTE + QUERY_ACCELERATION_CREDITS AS ATTRIBUTED_CREDITS_INCLUDING_QAS,
    EXECUTION_TIME,
    QUEUED_OVERLOAD_TIME,
    BYTES_SCANNED,
    BYTES_SPILLED_TO_LOCAL_STORAGE,
    BYTES_SPILLED_TO_REMOTE_STORAGE,
    ROWS_PRODUCED,
    QUERY_TEXT
FROM enriched
ORDER BY ATTRIBUTED_CREDITS_INCLUDING_QAS DESC NULLS LAST
LIMIT 20;
```

**Interpretation and limitations:**

- The ranking includes query-attributed warehouse compute plus Query Acceleration Service credits where reported. It is a query-level attribution metric, not total billable account cost. Very short queries (roughly 100 ms or less) may not appear in per-query attribution, so this is not a complete census of every statement.
- Query acceleration credits may be `NULL` when not used; treating that as zero is appropriate for this ranking.
- Role and query details are joined from `QUERY_HISTORY`; rows can be absent due to history latency or field availability.
- Query-attribution history excludes warehouse idle time and does not capture all workload cost categories. It omits queries around 100 ms or less and does not include Adaptive Warehouse jobs; use `QUERY_METERING_HISTORY` for per-query credit usage on Adaptive Warehouses. It is not a substitute for warehouse metering or account-level billing.
- `QUERY_TEXT` can contain sensitive literals. Restrict dashboard access and consider redacting text from broad reports.
- If your account's `QUERY_ATTRIBUTION_HISTORY` schema differs, inspect `DESC VIEW SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY` and adjust to the currently documented columns. Do not silently substitute estimated query cost for metered credits.

### 5.5 Cost by query tag, role, and warehouse

Query tags must be set by clients or session configuration; a tag convention is not useful if applications fail to set it. Example:

```sql
ALTER SESSION SET QUERY_TAG = 'team=finance;workload=monthly_close;env=prod';
-- Run the intended workload in this session.
```

Example query-attributed compute by tag and user:

```sql
SELECT
    COALESCE(NULLIF(QUERY_TAG, ''), 'UNTAGGED') AS QUERY_TAG,
    USER_NAME,
    WAREHOUSE_NAME,
    SUM(CREDITS_ATTRIBUTED_COMPUTE) AS ATTRIBUTED_COMPUTE_CREDITS,
    SUM(COALESCE(CREDITS_USED_QUERY_ACCELERATION, 0)) AS QAS_CREDITS,
    COUNT(*) AS QUERY_COUNT
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY
WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
  AND START_TIME < CURRENT_TIMESTAMP()
GROUP BY 1, 2, 3
ORDER BY ATTRIBUTED_COMPUTE_CREDITS DESC;
```

Role-level attribution needs the query history join:

```sql
SELECT
    COALESCE(NULLIF(a.QUERY_TAG, ''), 'UNTAGGED') AS QUERY_TAG,
    q.ROLE_NAME,
    a.WAREHOUSE_NAME,
    SUM(a.CREDITS_ATTRIBUTED_COMPUTE) AS ATTRIBUTED_COMPUTE_CREDITS,
    COUNT(*) AS QUERY_COUNT
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY a
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q
  ON q.QUERY_ID = a.QUERY_ID
WHERE a.START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
  AND a.START_TIME < CURRENT_TIMESTAMP()
GROUP BY 1, 2, 3
ORDER BY ATTRIBUTED_COMPUTE_CREDITS DESC;
```

For a useful chargeback model, combine three layers rather than claiming one view answers everything:

1. **Direct query attribution:** query credits, tag, user, warehouse, role where available.
2. **Warehouse metering:** includes idle time and other warehouse consumption not attributed to query execution.
3. **Account/service reconciliation:** service-level metering, storage, transfer, and billed cloud-services adjustments.

A team-owned warehouse is often a more defensible way to allocate idle time than distributing idle cost by query duration. If multiple teams share a warehouse, document an allocation policy (query credits plus allocated idle share, or another agreed rule) and label it as an allocation, not a direct measurement.

### 5.6 Storage and stage files

```sql
ALTER SESSION SET TIMEZONE = 'UTC';

SELECT
    USAGE_DATE,
    STORAGE_BYTES / POWER(1024, 4) AS TABLE_TIB,
    STAGE_BYTES / POWER(1024, 4) AS INTERNAL_STAGE_TIB,
    FAILSAFE_BYTES / POWER(1024, 4) AS FAILSAFE_TIB
FROM SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE
WHERE USAGE_DATE >= DATEADD(day, -30, CURRENT_DATE())
ORDER BY USAGE_DATE;
```

This is a trend diagnostic, not a precise invoice reconstruction. The view's storage bytes include table data in Time Travel; stage bytes represent internal-stage files. Prefer `STORAGE_DAILY_HISTORY` when reconciling billable storage and validate current columns/semantics in docs. External cloud buckets have their own provider billing and may not be represented as internal-stage bytes.

### 5.7 Serverless task history and service metering

```sql
SELECT
    TASK_NAME,
    SUM(TRY_TO_DOUBLE(CREDITS_USED)) AS CREDITS_USED,
    MIN(START_TIME) AS FIRST_WINDOW,
    MAX(END_TIME) AS LAST_WINDOW
FROM SNOWFLAKE.ACCOUNT_USAGE.SERVERLESS_TASK_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP())
  AND START_TIME < CURRENT_TIMESTAMP()
GROUP BY TASK_NAME
ORDER BY CREDITS_USED DESC;
```

`SERVERLESS_TASK_HISTORY.CREDITS_USED` may be typed as `VARCHAR`; `TRY_TO_DOUBLE` prevents a malformed value from aborting the report. This view covers serverless task usage, not all task compute: tasks running on a user-managed warehouse consume that warehouse's credits.

```sql
-- High-level service spend over the last 30 days.
SELECT
    SERVICE_TYPE,
    ENTITY_TYPE,
    NAME,
    SUM(CREDITS_USED_COMPUTE) AS COMPUTE_CREDITS,
    SUM(CREDITS_USED_CLOUD_SERVICES) AS CLOUD_SERVICES_CREDITS_RAW,
    SUM(CREDITS_USED) AS RAW_CREDITS
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP())
  AND START_TIME < CURRENT_TIMESTAMP()
GROUP BY SERVICE_TYPE, ENTITY_TYPE, NAME
ORDER BY RAW_CREDITS DESC;
```

Use `SERVICE_TYPE` and the current service catalog to identify Snowpipe (`PIPE`), automatic clustering (`AUTO_CLUSTERING`), Search Optimization (`SEARCH_OPTIMIZATION`), dynamic-table-related service entries, serverless tasks, and other supported services. Exact service labels and availability may evolve. Do not assume every feature has an individual row in every view or that service names are static.


### 5.8 Data-transfer volume and currency reconciliation

`DATA_TRANSFER_HISTORY` reports transfer activity and bytes, not the final monetary charge. Use it to identify transfer patterns and destinations; use Snowsight Consumption or the appropriate currency-denominated usage view and billing statement to establish cost. Rates vary by region, cloud, transfer type, and contract.

```sql
ALTER SESSION SET TIMEZONE = 'UTC';

SELECT
    START_TIME::DATE AS USAGE_DATE_UTC,
    TRANSFER_TYPE,
    SOURCE_CLOUD,
    SOURCE_REGION,
    TARGET_CLOUD,
    TARGET_REGION,
    SUM(TRY_TO_NUMBER(BYTES_TRANSFERRED::VARCHAR)) AS BYTES_TRANSFERRED
FROM SNOWFLAKE.ACCOUNT_USAGE.DATA_TRANSFER_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP())
  AND START_TIME < CURRENT_TIMESTAMP()
GROUP BY 1, 2, 3, 4, 5, 6
ORDER BY BYTES_TRANSFERRED DESC;
```

This is a volume diagnostic, not a dollar calculation. The view can lag by about two hours. Do not infer a cost from bytes without the correct rate schedule and transfer category.

---

## 6. Cost attribution: query → warehouse → team → workload

```text
Client / scheduled job
  └─ sets QUERY_TAG and uses approved ROLE
       └─ runs query on TEAM/WORKLOAD warehouse
            ├─ QUERY_HISTORY: role, elapsed time, bytes scanned/spilled
            ├─ QUERY_ATTRIBUTION_HISTORY: attributed compute credits + tag
            └─ WAREHOUSE_METERING_HISTORY: full warehouse credits, including idle time
                 └─ finance allocation policy → team / product / cost center

Account-level reconciliation:
  METERING_DAILY_HISTORY + METERING_HISTORY + storage + transfer + invoice
```

### Recommended tagging convention

Use a small, stable schema rather than arbitrary free text:

`team=<team>;workload=<workload>;env=<env>;owner=<service-or-group>`

Rules:

- Set tags in connection/session initialization for applications and scheduled jobs.
- Do not put PII, secrets, access tokens, customer names, or query parameters in tags.
- Track the percentage of attributed credits with a valid tag as a governance KPI.
- Use a default value such as `UNTAGGED` in reports and assign an owner to fix gaps.
- Keep tags low-cardinality and standardize spelling; otherwise dashboards fragment one workload across many variants.

### Cost allocation options

| Model | How it works | Benefits | Trade-off |
|---|---|---|---|
| Warehouse ownership | Dedicated warehouse per team/product | Easy to attribute metering and idle time | More warehouses to govern; small workloads may fragment |
| Query-tag showback | Report query-attributed credits by tag | Good workload detail | Excludes idle time and some service costs; depends on tag hygiene |
| Hybrid allocation | Direct query attribution + explicitly allocated idle/shared costs | More complete chargeback | Allocation assumptions must be documented and agreed |
| Central platform allocation | Platform team owns shared warehouse and distributes a policy-based share | Simple central operations | Teams may not see marginal costs clearly; avoid opaque allocations |

---

## 7. Diagnose expensive queries (advanced)

Do not optimize only by elapsed time. Start with query profile, query history, warehouse load, and a stable representative workload. Query plans and bottlenecks are often more informative than a single timing.

### 7.1 Triage checklist

1. **Confirm the workload:** query ID, owner, business purpose, frequency, expected output, warehouse, role, tag, and whether the run is representative.
2. **Separate wait from work:** inspect execution time, queued overload time, compilation, and warehouse load. A queue issue may need concurrency/warehouse changes rather than SQL rewrite.
3. **Inspect bytes scanned and partitions:** if many bytes are scanned to return a small result, review filters, join keys, pruning, and projection.
4. **Inspect spills:** large local/remote spill can indicate memory pressure, poor join/sort shape, or oversized intermediates. Try a query rewrite first; compare a larger warehouse only as a controlled test.
5. **Inspect join cardinality:** validate join keys and grain. A many-to-many join or duplicate keys can multiply rows and consume huge resources.
6. **Check repeated full scans:** repeated batch jobs, non-incremental transformations, and unnecessary reprocessing often dominate cost.
7. **Evaluate cache:** result cache can make a repeated query cheap or very fast, but cache hits can hide the true cold-run cost. Record cache behaviour and compare both cold/warm cases deliberately.
8. **Compare cost, latency, and correctness:** a faster query that costs more may or may not be a win. Define a business objective and guardrail.

### 7.2 Common expensive patterns and remedies

| Symptom | Likely causes | First actions | Risks / evidence to collect |
|---|---|---|---|
| High bytes scanned / weak pruning | Filter not selective, expression prevents pruning, broad date range, wrong table layout | Filter on selective columns, avoid unnecessary casts on filter columns, project only required columns, inspect partitions scanned | Confirm row counts and result equality; don't cluster automatically without evidence. |
| Exploding joins / huge row explosion after join | Duplicate join keys, wrong grain, missing predicate, accidental cross join | Count key duplicates, check pre/post-join cardinality, aggregate/deduplicate at the correct grain | Never “fix” cost by dropping rows without validating business semantics. |
| Remote/local spilling | Large sort/hash aggregate/join, too much intermediate data, warehouse memory pressure | Reduce input rows/columns, improve join order/shape, pre-aggregate where correct; benchmark a larger warehouse if justified | A larger warehouse may reduce elapsed time but increase credits; measure total credits. |
| Repeated full scans | Full-refresh ELT, broad `MERGE`, recurring report re-computation | Incrementalize where correct, materialize reusable transformations, schedule only as often as needed | Incremental logic introduces correctness and late-arrival complexity. Test backfills. |
| Long idle runtime | Auto-suspend too long, clients leave warehouses running | Lower auto-suspend for intermittent workloads; enable auto-resume only where appropriate | Very short suspend may add resume latency and cache loss. Measure workload pattern. |
| Warehouse too large for light queries | Overprovisioned size, low concurrency | Test smaller size and compare credits/latency/concurrency | A smaller warehouse can increase queueing or run time; use workload-level SLOs. |
| Queueing | Too many concurrent queries, undersized warehouse, inefficient jobs | Inspect queued time/load, isolate workload, tune concurrency or size | Multi-cluster scaling may improve concurrency while increasing spend. |
| Expensive serverless feature | Feature enabled without measured value or on unstable data | Inspect feature history and benefit; disable only after impact assessment | Removing search optimization/clustering may worsen latency; compare SLA and credits. |
| Large stage bytes | Old files, repeated loads, unneeded staged artifacts | Identify stage owners, lifecycle/cleanup policy, remove only confirmed-unused files | Do not delete files needed for replay, recovery, or audit. |

### 7.3 `SELECT *`, result cache, and pruning

- Prefer explicit columns in production pipelines and consumer-facing queries. This reduces unnecessary data movement, improves readability, and avoids accidental downstream schema expansion. Snowflake may prune unused columns in some plans; therefore do not claim every `SELECT *` always scans every column—measure the plan and downstream usage.
- Result caching can reduce compute for repeated identical eligible queries. Do not force cache invalidation or treat a warm-cache result as a fair benchmark of query-plan improvements.
- Micro-partition pruning is a primary optimization lever. Use Query Profile to compare partitions scanned with total partitions and bytes scanned. Clustering has maintenance cost; only adopt it when query patterns and measured benefit justify that cost.
- Removing unused tables may reduce storage but can break consumers or recovery. Inventory ownership, dependencies, Time Travel, Fail-safe, retention, and legal holds before deletion.

### 7.4 Before-and-after measurement protocol

For every optimization, record:

| Field | Why it matters |
|---|---|
| Query ID / query tag / code version | Reproducibility and lineage |
| Input data range and row counts | Comparable workload |
| Warehouse size and configuration | Compute conditions |
| Cold/warm cache status | Avoids misleading comparisons |
| Elapsed time and queued time | Latency and contention |
| Bytes scanned and spilled | Query efficiency |
| Attributed compute + query acceleration credits | Query-level cost evidence |
| Warehouse metering over the test window | Includes idle time; isolate the test if possible |
| Correctness checks | Cost reduction is irrelevant if output changes incorrectly |
| Run count and variability | Prevents conclusions from one noisy run |

Use multiple runs if feasible, compare medians or distributions, and avoid overlapping unrelated workloads. State whether the evidence is measured, estimated, or sampled. Do not multiply a single-query credit reduction by monthly frequency unless frequency and representative cost are verified.

---

## 8. Serverless feature costs and storage optimization

### 8.1 Serverless features

| Feature | What to measure | Decision question |
|---|---|---|
| Snowpipe / Snowpipe Streaming | Pipe/service metering, load volume, freshness SLA | Does continuous ingestion provide enough latency/value over scheduled loads? |
| Automatic clustering | `AUTO_CLUSTERING` service usage and query performance trend | Does clustering reduce downstream query cost enough to offset maintenance? |
| Search Optimization Service | `SEARCH_OPTIMIZATION` service usage and point-lookup latency | Is the workload selective and frequent enough to justify the maintenance cost? |
| Dynamic tables | Refresh behavior, target lag, service metering and upstream changes | Is the target lag necessary? Is refresh work excessive due to upstream churn or broad dependencies? |
| Serverless tasks | `SERVERLESS_TASK_HISTORY` and `METERING_HISTORY` | Is serverless task convenience/management worth its feature cost compared with a warehouse-backed task? |
| Query Acceleration Service | Query-attribution QAS credits and eligible query latency | Does accelerated latency materially benefit the workload relative to the added credits? |

The view coverage and service labels vary by feature and account. Dynamic-table refresh history can help identify refresh timing and behavior, but pair it with warehouse metering or relevant serverless service metering to understand credits. Use both Snowsight and service-specific documentation; a missing row may reflect latency, retention, unsupported attribution, or no consumption, not necessarily a free feature.

### 8.2 Storage and retention

Storage optimization is a lifecycle decision, not just a deletion task.

- **Transient tables:** may avoid Fail-safe storage for eligible transient data, but they also change recovery guarantees. Use for reproducible staging/intermediate data that can be rebuilt—not as a blanket setting for critical curated data.
- **Retention tuning:** lower Time Travel retention only after considering recovery objectives, audit/legal obligations, and operational rollback needs. Storage savings depend on data churn and retained historical versions.
- **Stage-file cleanup:** remove only files confirmed unused after load validation and replay-window review. Use explicit owners and lifecycle rules.
- **Unused tables:** use ownership, query history, lineage, downstream dependencies, shares, tasks, and retention requirements to verify candidates before deletion.
- **Clones:** initially share underlying data, but modifications create divergent storage. Do not assume cloned dev/test environments are storage-free indefinitely.
- **Compression and physical bytes:** Snowflake's stored-byte metrics and invoice calculations are not necessarily identical to raw logical table size.

### 8.3 Repeated full reloads

Suppose a pipeline replaces a 2 TiB logical dataset every day. A simplistic estimate of “2 TiB × 30” is not a Snowflake storage invoice because billing depends on stored bytes over time, compression, retention, historical versions, Fail-safe, and account-specific pricing. Use this as a risk signal only. Measure daily storage trend and compare it with `STORAGE_DAILY_HISTORY`/billing for the same period. A safer design may use incremental `MERGE`, partitioned/date-scoped rebuilds, transient scratch data where appropriate, and cleanup of obsolete stage files.

---

## 9. Capacity contracts, on-demand, showback, and chargeback

Commercial terms differ by customer and region. A **capacity/commitment contract** can change effective unit economics and commitment risk; **on-demand** consumption generally exposes usage more directly to the applicable usage price. Do not compare raw credits alone and claim one commercial model is always cheaper. Model expected and peak usage, seasonality, contract commitments, overage terms, service mix, and unused commitment risk with finance/procurement.

- **Showback:** report each team's estimated or measured usage without transferring a bill. Useful for building trust and correcting tags before formal chargeback.
- **Chargeback:** allocate actual costs to budgets/cost centers. Requires a documented rule for shared warehouse idle time, serverless features, storage, transfer, and discounts/credits.
- **FinOps:** a recurring cross-functional loop among engineering, finance, and product owners: visibility → accountability → optimization → business-value validation.

A fair allocation policy should label each cost as **directly metered**, **attributed**, or **allocated by policy**. Never present allocated idle time as a measured query cost.

---

## 10. Cost dashboard design

A practical dashboard should answer “what changed, why, who owns it, and what action should happen?”

### 10.1 Suggested dashboard panels

1. **Account trend:** daily billed compute/service credits, month-to-date currency spend from a currency-denominated source, storage trend, and data transfer where available. Do not label credits as dollars or present compute credits alone as all-in account spend.
2. **Spend by service:** warehouse, serverless feature, cloud services adjustment, storage, transfer; show source and refresh time.
3. **Warehouse table:** credits, active/idle estimate, warehouse size, auto-suspend, owner/team, monitor, workload SLA.
4. **Top queries:** attributed compute credits, QAS credits, elapsed/queued time, bytes scanned, spill, query tag, role, owner, query ID.
5. **Serverless panel:** service type/object, credits, trend, freshness/latency, feature owner.
6. **Storage panel:** table/stage/retention trends, candidates for cleanup, owner, dependencies, approval status.
7. **Attribution quality:** percent tagged, untagged credits, missing owner, shared-warehouse allocation.
8. **Budget/monitor status:** thresholds, projected overrun, notification route, exceptions and next action.
9. **Optimization tracker:** hypothesis, baseline, change, validation, estimated monthly impact, confidence, rollback plan.

Every chart should state metric, unit, time zone, data source, last refreshed timestamp, and whether numbers are billed, raw, attributed, or estimated. Keep query text and sensitive metadata restricted.

### 10.2 Dashboard data model

Use separate fact tables/views rather than blindly joining hourly warehouse metering to query rows (which duplicates warehouse totals):

- `FACT_ACCOUNT_DAILY_METERING` — daily account/service billing measures.
- `FACT_WAREHOUSE_HOURLY_METERING` — warehouse/hour credits.
- `FACT_QUERY_ATTRIBUTION` — query-level attributed credits and tags.
- `FACT_QUERY_DIAGNOSTICS` — elapsed time, scans, spill, role, warehouse, query ID.
- `FACT_STORAGE_DAILY` — storage and stage trends.
- `DIM_WAREHOUSE_OWNER`, `DIM_QUERY_TAG`, `DIM_SERVICE`, `DIM_COST_CENTER` — governed ownership mappings.

Avoid joining query-level rows to warehouse-hour rows without an allocation grain: each query can match the same warehouse/hour and multiply metering totals. Reconcile measures at their native grain, then allocate explicitly if needed.

---

## 11. Weekly FinOps review routine

Run the same review weekly, with a monthly reconciliation against billing.

1. **Refresh and qualify data.** Record each source's refresh time and latency. Exclude incomplete latest intervals from month-over-month conclusions.
2. **Check account trend.** Compare last 7 complete days to prior 7 complete days and same weekday pattern where seasonality matters.
3. **Explain top movements.** Review service types, warehouse spikes, new serverless features, storage growth, and transfer changes.
4. **Review top queries.** Use attributed credits and query profile; assign a named owner and expected business outcome.
5. **Review idle/concurrency.** Find warehouses with high active runtime but low query attribution, excessive queueing, or poor auto-suspend configuration.
6. **Review attribution quality.** Track untagged query credits, unowned warehouses, shared-cost allocations, and missing service owners.
7. **Review monitors and budgets.** Check thresholds, alert routing, upcoming peak workloads, and suspension exceptions. Confirm no critical job is exposed to an unreviewed immediate suspend.
8. **Review storage and retention.** Inspect stage files, transient scratch data, Time Travel retention, clones, and unused-table candidates with owners.
9. **Select 1–3 prioritized changes.** Each has hypothesis, risk, baseline, owner, success metric, test plan, and rollback.
10. **Verify impact next week.** Report measured savings only after validating comparable workload and billing/metering data.

### Optimization prioritization matrix

Score each opportunity from 1 (low) to 5 (high). For **risk**, a higher score means more risk, so prioritize low-risk items with other factors equal.

| Opportunity | Expected savings | Effort | Risk | Evidence needed | Typical priority |
|---|---:|---:|---:|---|---|
| Auto-suspend a warehouse left idle | 3–5 | 1–2 | 1–2 | Metering, idle periods, workload schedule | High |
| Add query tags / warehouse owner | Indirect | 1–2 | 1 | Attribution coverage before/after | High enabling action |
| Remove unused `SELECT *` projections | 1–3 | 1–2 | 1–2 | Profile and result validation | High when scan/projection evidence exists |
| Fix many-to-many join explosion | 3–5 | 2–4 | 2–4 | Row counts, join keys, result tests | High when confirmed |
| Improve pruning / narrow scan | 2–5 | 2–4 | 2–3 | Partitions/bytes scanned and result equality | High when confirmed |
| Resize warehouse down | 1–4 | 1–2 | 2–4 | Credits, latency, queueing, concurrency | Medium; test first |
| Add clustering or Search Optimization | May increase cost; latency benefit varies | 3–5 | 2–3 | Baseline query pattern and feature credits | Only with clear evidence |
| Reduce retention / delete data | 1–4 storage savings | 2–4 | 4–5 | Legal, recovery, dependency and retention review | Low until approved |
| Disable serverless feature | 1–5 | 1–3 | 3–5 | Feature usage and SLA impact | Only after impact review |

A simple prioritization score may be used internally, but do not let an arbitrary formula override business risk or data correctness. Expected savings should be a range with confidence, not an unsupported single number.

### Ten optimizations to investigate first (evidence-dependent)

This is a **default investigation order**, not a promise that every item saves the most in every account:

1. Stop clearly unintended warehouse runtime and correct auto-suspend/auto-resume configuration.
2. Fix confirmed row explosion, accidental cross joins, and incorrect join grain.
3. Eliminate repeated full scans with correct incremental processing or reuse of validated intermediate results.
4. Improve pruning by narrowing time ranges and making filters selective; validate partitions and bytes scanned.
5. Reduce unnecessary projection and result volume; replace broad `SELECT *` in pipelines with required columns.
6. Right-size warehouses using a controlled test that measures credits, latency, and queueing.
7. Reduce wasteful scheduling/frequency for refreshes, tasks, or ingestion when business freshness permits.
8. Tune caching and workload reuse where eligible, while measuring cold and warm behaviour separately.
9. Review serverless features (clustering, Search Optimization, Snowpipe, dynamic tables, tasks) against their measured value and SLA.
10. Review unused tables, stage files, clones, and retention policies with owners, dependencies, recovery needs, and compliance obligations.

The first items often have lower implementation effort, but prioritize from your own evidence. A feature or storage change can increase total cost or risk if it degrades the workload or weakens recovery.

---

## 12. Hands-on lab — `experiments/10_cost/`

### 12.1 Lab goals and deliverables

By the end of the lab, create:

```text
experiments/10_cost/
├── 00-prerequisites-and-cost-safety.md
├── 01-resource-monitor.sql
├── 02-cost-views.sql
├── 03-top-queries.sql
├── 04-optimization-experiments.md
├── 05-serverless-review.sql
├── 06-finops-one-pager.md
└── README.md
```

These are **recommended lab artifacts**; create them in your roadmap repository. This lesson itself does not create those files or execute the SQL.

### 12.2 Setup and required access

1. Select a dedicated sandbox account or approved lab database and a small warehouse (for example `XSMALL` where available).
2. Confirm the warehouse's current resource monitor and auto-suspend settings. Do not reuse an existing production monitor or change shared resources without approval.
3. Use a monitoring role with the minimum required imported database roles/privileges to query relevant `SNOWFLAKE.ACCOUNT_USAGE` views. Depending on account configuration, this may require granting Snowflake-provided database roles or another approved access mechanism.
4. Use an account administrator only for operations that require it, such as creating resource monitors under the standard model. Switch back to the lab role for query tests.
5. Set a query tag such as `team=learning;workload=cost_lab;env=nonprod` in the lab session.
6. Record the account region, warehouse size, time zone, feature availability, and start/end timestamps.
7. Do not enable Search Optimization or automatic clustering solely to create a cost record; only use them if the account supports the feature and you have an approved test dataset and cost boundary.

### 12.3 Exercise 1 — Resource monitor

With authorized account-administrator access, inventory the lab warehouses and attach a dedicated monitor to each lab-owned warehouse that requires control. Run the Section 4.1 example for one dedicated lab warehouse; repeat with unique monitor/warehouse names for additional lab warehouses. Do not attach the example monitor blindly to every production warehouse. Confirm assignments using `SHOW RESOURCE MONITORS` and `SHOW WAREHOUSES`.

**Expected observation:** the monitor shows the configured quota, frequency, and triggers. Usage is not necessarily updated in real time. Notifications require notification configuration. Do not intentionally drive a critical warehouse to a suspension threshold to test it.

**Failure handling:** if you lack `ACCOUNTADMIN`, request an approved admin to create/assign the monitor or perform this exercise as a documented simulation. Do not elevate yourself or modify an existing monitor without authorization. If a monitor already exists, inspect it and avoid replacing it with `CREATE OR REPLACE`.

### 12.4 Exercise 2 — Create reporting views

Create a dedicated reporting schema using a role that owns only the lab objects. Example:

```sql
-- Fail safely if these dedicated lab names already exist; inspect before reusing.
CREATE DATABASE COST_LAB_DB;
CREATE SCHEMA COST_LAB_DB.REPORTING;

CREATE VIEW COST_LAB_DB.REPORTING.DAILY_WAREHOUSE_CREDITS AS
SELECT
    START_TIME::DATE AS USAGE_DATE,
    WAREHOUSE_NAME,
    SUM(CREDITS_USED_COMPUTE) AS COMPUTE_CREDITS,
    SUM(CREDITS_USED_CLOUD_SERVICES) AS CLOUD_SERVICES_CREDITS_RAW,
    SUM(CREDITS_USED) AS RAW_CREDITS
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(day, -90, CURRENT_TIMESTAMP())
GROUP BY 1, 2;

CREATE VIEW COST_LAB_DB.REPORTING.DAILY_ACCOUNT_COMPUTE_CREDITS_BILLED AS
SELECT
    USAGE_DATE,
    SUM(CREDITS_BILLED) AS CREDITS_BILLED
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY
WHERE USAGE_DATE >= DATEADD(day, -90, CURRENT_DATE())
GROUP BY 1;

CREATE VIEW COST_LAB_DB.REPORTING.QUERY_TAG_ATTRIBUTION AS
SELECT
    a.START_TIME::DATE AS USAGE_DATE,
    COALESCE(NULLIF(a.QUERY_TAG, ''), 'UNTAGGED') AS QUERY_TAG,
    a.USER_NAME,
    a.WAREHOUSE_NAME,
    SUM(a.CREDITS_ATTRIBUTED_COMPUTE) AS ATTRIBUTED_COMPUTE_CREDITS,
    SUM(COALESCE(a.CREDITS_USED_QUERY_ACCELERATION, 0)) AS QAS_CREDITS,
    COUNT(*) AS QUERY_COUNT
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY a
WHERE a.START_TIME >= DATEADD(day, -90, CURRENT_TIMESTAMP())
  AND a.START_TIME < CURRENT_TIMESTAMP()
GROUP BY 1, 2, 3, 4;

-- Daily attribution by query tag, active role, and warehouse where query history is available.
CREATE VIEW COST_LAB_DB.REPORTING.DAILY_ROLE_TAG_ATTRIBUTION AS
SELECT
    a.START_TIME::DATE AS USAGE_DATE,
    COALESCE(NULLIF(a.QUERY_TAG, ''), 'UNTAGGED') AS QUERY_TAG,
    q.ROLE_NAME,
    a.WAREHOUSE_NAME,
    SUM(a.CREDITS_ATTRIBUTED_COMPUTE) AS ATTRIBUTED_COMPUTE_CREDITS,
    SUM(COALESCE(a.CREDITS_USED_QUERY_ACCELERATION, 0)) AS QAS_CREDITS,
    COUNT(*) AS QUERY_COUNT
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY a
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q
  ON q.QUERY_ID = a.QUERY_ID
WHERE a.START_TIME >= DATEADD(day, -90, CURRENT_TIMESTAMP())
  AND a.START_TIME < CURRENT_TIMESTAMP()
GROUP BY 1, 2, 3, 4;
```

The `CREATE VIEW` statements require the role to have privileges on the destination database/schema and `SELECT` access to the source views. If view ownership and consumer access are separated, validate whether secure views or controlled grants are needed for your governance model. Set the session time zone to UTC before creating/running these views if the daily buckets must align with account/organization billing dates. Role attribution is obtained by joining query IDs to `QUERY_HISTORY`; because history feeds have different latencies, the role can be temporarily NULL. These views deliberately keep warehouse metering, billed compute credits, and query attribution separate so reports don't accidentally double-count them. Storage and data-transfer costs are not included in the daily billed-credit view; use the appropriate storage/transfer views and currency-denominated usage data for those components. The `CREATE VIEW` statements are only for the dedicated `COST_LAB_DB.REPORTING` lab objects; they fail rather than overwrite an existing view. Never point them at a production schema without change control.

**Expected observation:** rows appear only after usage has been recorded and the source views refresh. A newly created lab may have no data; that is not a failure. Query-tag attribution will show `UNTAGGED` for sessions that did not set a tag.

### 12.5 Exercise 3 — Find the three most expensive lab queries

Run the current-week query in Section 5.4 and filter to the lab warehouse or tag. For example, add this predicate to the `attributed` CTE if the tag convention is stable:

```sql
AND a.QUERY_TAG = 'team=learning;workload=cost_lab;env=nonprod'
```

Alternatively, filter by `WAREHOUSE_NAME` using the dedicated lab warehouse name. Review the top three rows with the Query Profile in Snowsight. If there are fewer than three query-attribution rows, do not invent results: run a few representative, bounded lab queries and wait for history to populate.

**Expected observation:** each returned query has a query ID and attribution fields; query history may be delayed or incomplete. If no records appear, verify role privileges, query tag, date/time zone, history latency, and that queries actually ran.

### 12.6 Exercise 4 — Optimize and compare

Choose three queries with different bottlenecks if available. For each query:

1. Save the query ID, SQL version, warehouse size, tag, input range, and output validation.
2. Inspect Query Profile for partitions/bytes scanned, join output rows, spills, and queueing.
3. Form one hypothesis: narrower projection, selective predicate, corrected join grain, incremental filter, or controlled warehouse-size test.
4. Change one variable at a time and preserve a rollback copy.
5. Run the same representative input and validate row counts, aggregates, and key-level results.
6. Compare at least several runs if feasible; record cache state and any concurrent workload.
7. Compare elapsed time, bytes scanned, spills, query-attributed credits, and warehouse metering over an isolated test window.
8. Report no savings unless the measurements support them. If no measured usage is available, report “insufficient data” and use the template below.

| Query | Baseline ID | Changed version | Baseline evidence | After evidence | Correctness | Conclusion |
|---|---|---|---|---|---|---|
| Query A | Fill in | Fill in | Measured only | Measured only | Pass/fail | Confirmed / inconclusive |
| Query B | Fill in | Fill in | Measured only | Measured only | Pass/fail | Confirmed / inconclusive |
| Query C | Fill in | Fill in | Measured only | Measured only | Pass/fail | Confirmed / inconclusive |

### 12.7 Exercise 5 — Serverless feature review

Use the service metering query in Section 5.7 and task history in Section 5.7. Group the output by service and object. Then document:

- Whether each feature is enabled and its owner.
- Credits or usage evidence over a completed time window.
- What business/latency benefit it provides.
- Whether the current workload justifies its cost.
- A safe next action: keep, tune, trial-disable, or investigate.
- What evidence would be required to decide if usage is absent or delayed.

Do not disable a production feature based only on one cost row. If the account does not use a feature or does not expose a matching view, record “not observed / not available” rather than “zero cost.”

### 12.8 Exercise 6 — One-page FinOps report

Use this structure in `06-finops-one-pager.md`:

```markdown
# Weekly Snowflake FinOps Report — <date range>

## Executive summary
- Account spend / billed credits (source and completeness):
- Largest observed movement:
- Most important risk:

## Evidence
- Warehouse usage:
- Serverless service usage:
- Storage / stage trend:
- Top three query findings:
- Attribution coverage / untagged spend:

## Actions
| Priority | Finding | Evidence | Estimated impact and confidence | Risk | Owner | Due date |
|---|---|---|---|---|---|---|

## Measurement limitations
- Source latency and missing data:
- Attributed vs billed vs allocated measures:
- Contract price assumption, if any:

## Next review
- Checks and decisions required:
```

If the account has no real history yet, use a **clearly labelled synthetic example** and do not present it as actual Snowflake usage. Do not invent credits saved, query IDs, prices, or billing outcomes.

### 12.9 Cleanup

- Drop only the dedicated lab views/schema/database and warehouse created for this exercise after exporting the report you want to keep.
- Detach or drop the lab resource monitor only after confirming it is assigned solely to the lab warehouse and no longer needed. Do not drop an account-level or shared monitor.
- Restore session query tag/time zone if needed; session parameters normally affect only the current session, but shared connection setup may persist them for later statements.
- Do not delete internal-stage files or production objects as part of this lab.
- Verify warehouses are suspended and no test workload continues to run.

Example cleanup for objects created exclusively for the lab:

```sql
-- First verify each object is lab-owned and not used by another workload.
-- Run these statements individually only after that verification; do not bulk-run
-- cleanup against names that existed before the lab.
-- ALTER WAREHOUSE WH_LAB_COST UNSET RESOURCE_MONITOR;
-- DROP RESOURCE MONITOR RM_LAB_COST;
-- DROP DATABASE COST_LAB_DB;
-- DROP WAREHOUSE WH_LAB_COST;
```

### 12.10 Lab troubleshooting

| Problem | Likely reason | Response |
|---|---|---|
| Permission denied on `ACCOUNT_USAGE` | Monitoring role lacks imported database role/privilege | Ask the account owner to grant approved read access; do not use admin role for every query. |
| Resource monitor command denied | Requires account-admin role under standard configuration | Request an authorized administrator; do not alter another team's monitor. |
| No recent history | Account Usage latency or no workload in period | Check actual query execution, wait for the documented latency, use Snowsight for immediate triage. |
| No query attribution rows | View delay, no query execution, unsupported workload type, or permissions | Check `QUERY_HISTORY`, query tag, warehouse type, and current view documentation. |
| Query tags inconsistent | Client doesn't set session parameter or overwrites it | Set tag in connection initialization and validate from query history. |
| Credits do not equal invoice | Different grain, raw vs billed credits, cloud-services adjustment, storage/transfer excluded | Reconcile account daily metering and billing; keep attributed query cost separate. |
| Query is fast but expensive | Large warehouse, high credits, cache, or short but compute-intensive scan | Compare credits, bytes, and warehouse size—not just elapsed time. |
| Resource monitor did not stop all spend | Serverless usage or cloud-services activity outside suspend control | Use budgets and feature-specific history; a monitor is not a universal account cap. |
| Before/after results vary | Cache, concurrency, data drift, warehouse change | Repeat runs, fix input and conditions, record cold/warm cache, isolate test. |

---

## 13. Production FinOps recommendations

1. **Set an owner on every warehouse, task, pipe, dynamic table, and cost-bearing feature.** Orphaned ownership is a recurring cause of waste.
2. **Use auto-suspend and auto-resume intentionally.** Intermittent workloads often benefit from short idle windows; interactive workflows may need a longer window for latency. Measure both runtime and resume penalty.
3. **Right-size based on workload evidence.** Test smaller/larger sizes with representative concurrency and SLOs; credits per second and total runtime jointly determine cost.
4. **Separate workloads by cost center and criticality.** Team-specific warehouses improve attribution and prevent one workload consuming another's quota; shared warehouses require an explicit idle-cost allocation policy.
5. **Tag all automated workloads.** Add a dashboard KPI for missing/untagged attribution and make tags part of deployment templates.
6. **Use budgets for supported serverless costs and resource monitors for warehouse controls.** Do not rely on either alone.
7. **Tune queries before buying features.** Clustering, Search Optimization, and Query Acceleration can be valuable, but each has costs and workload-specific applicability.
8. **Review storage and stage files with data owners.** Include Time Travel, Fail-safe, clones, transient-table recovery limits, legal holds, and replay needs in the decision.
9. **Use incremental pipelines where correctness allows.** Verify late-arriving data, deletes, backfills, and idempotency before removing full refreshes.
10. **Keep operational guardrails proportional.** Use timeouts, bounded input windows, workload isolation, monitors, and alert escalation without unexpectedly cancelling critical month-end/finance work.
11. **Reconcile periodically.** Account Usage is excellent for analysis but has delay and metric-specific semantics; compare monthly reports with billing and contract terms.
12. **Report savings honestly.** Label direct measurements, attributed credits, estimated dollar impact, and allocated costs distinctly. Document assumptions and confidence.

## 14. Common mistakes

- Monitoring warehouse credits only and ignoring serverless, storage, transfer, and cloud-services adjustments.
- Treating a resource monitor as a universal hard spend cap.
- Assuming budgets immediately terminate expensive work.
- Using query-attributed credits as if they include idle warehouse time.
- Ranking query costs with an unbounded or ambiguous time window.
- Joining hourly warehouse metering to every query in that hour and double-counting spend.
- Forgetting to tag application sessions or using uncontrolled, high-cardinality tag values.
- Assuming all `ACCOUNT_USAGE` views have identical latency, retention, permissions, or billing semantics.
- Assuming `STORAGE_USAGE` exactly equals the invoice.
- Optimizing only elapsed time while query credits or total warehouse consumption increase.
- Disabling Search Optimization, clustering, dynamic tables, or serverless tasks without measuring workload impact.
- Shortening retention or deleting tables/stage files before dependency, recovery, and legal review.
- Suspending critical warehouses immediately without a runbook, exception process, and owner approval.
- Claiming savings from one noisy run or fabricated sample data.
- Failing to recheck cost after a deployment or feature change.

---

## 15. Practice questions with answers

### Q1. Why can a query with 2 seconds of elapsed time still be expensive?

**Answer:** Elapsed time is not a direct cost metric. The query may use a large warehouse, scan/transform substantial data in a short period, invoke Query Acceleration, or run while the warehouse remains active. Check attributed credits, QAS credits, warehouse size, and metering context.

### Q2. What does a resource monitor control, and what does it not control?

**Answer:** It tracks warehouse-associated credit usage at assigned-warehouse or account scope and can notify/suspend eligible warehouses. It is not a control for all serverless features, storage, or data transfer, and thresholds are not an exact real-time cap.

### Q3. Why don't query-attributed credits add up exactly to warehouse credits?

**Answer:** Query attribution excludes idle warehouse time and may omit unsupported workloads or feature-specific consumption. Warehouse metering covers the warehouse over its active time, while account billing includes other services and adjustments.

### Q4. When should you use `METERING_DAILY_HISTORY` instead of `QUERY_ATTRIBUTION_HISTORY`?

**Answer:** Use daily metering for account-level billed-credit reconciliation by day. Use query attribution to understand relative query execution cost and tag/warehouse/user patterns. They answer different questions.

### Q5. How do budgets differ from resource monitors?

**Answer:** Resource monitors focus on warehouse credits and can suspend/disable eligible warehouses. Budgets monitor spending for supported objects/services, including supported serverless features, and send projected-overrun notifications; they are not general-purpose automatic suspension controls.

### Q6. What is the risk of ranking query costs by `EXECUTION_TIME` alone?

**Answer:** Elapsed time does not account for warehouse size, idle time, query acceleration, storage, transfer, or whether the query is repeated frequently. Rank by supported attributed credits for query-level prioritization, then reconcile at warehouse/account level.

### Q7. Why can a smaller warehouse increase total cost?

**Answer:** It may run much longer or queue more, so the reduction in credits per second may be offset by longer active time, concurrency effects, and SLO impact. Benchmark with representative workload and compare credits plus latency.

### Q8. Should you enable automatic clustering whenever a table is slow?

**Answer:** No. First inspect pruning, scan volume, filter patterns, and query profile. Clustering adds maintenance cost and helps only when its physical organization benefits the actual workload enough to justify that cost.

### Q9. How should shared warehouse idle time be allocated?

**Answer:** Use an agreed and documented policy—such as team-owned warehouse allocation or a proportional allocation based on query-attributed credits. Label the result as allocated cost, not direct query measurement.

### Q10. What is the safe way to evaluate a suspected expensive serverless feature?

**Answer:** Confirm the service usage and data freshness, identify the owning object and SLA, measure the benefit, then run an approved controlled change with rollback. A missing history row alone does not prove zero cost.

### Q11. Why can `STORAGE_USAGE` disagree with the bill?

**Answer:** It reports average daily storage bytes using its own measurement method, including table, stage, and Fail-safe categories. For closer billing reconciliation use the appropriate storage daily history view and align dates/time zones and billing semantics.

### Q12. What must a savings claim include?

**Answer:** A comparable baseline and after window, query IDs/code versions, input data, warehouse configuration, cache conditions, correctness validation, query-attributed and warehouse-level evidence, and explicit assumptions about frequency and contract pricing. Label estimates and confidence separately from measured savings.

---

## 16. Topic 10 checkpoint

You are ready to move on when you can do each item without relying on a memorized recipe:

- [ ] Explain every component of Snowflake cost: compute credits, storage, transfer, cloud services, and serverless features.
- [ ] Explain resource monitors versus budgets and alerts, including what each can and cannot control.
- [ ] Use Snowsight and `ACCOUNT_USAGE` to investigate spend while respecting data freshness and privileges.
- [ ] Write the SQL for the top 20 queries by attributed credits for a bounded current-week window.
- [ ] Attribute query cost using tags, warehouse, and role where supported, and explain why it differs from billed account spend.
- [ ] Find and diagnose an expensive query using scan/pruning, join cardinality, spilling, queueing, and repeated full scans.
- [ ] Evaluate serverless feature consumption without assuming missing data means zero cost.
- [ ] Explain storage trade-offs for transient tables, retention tuning, clones, and stage-file cleanup.
- [ ] Build a cost dashboard with explicit units, source, freshness, and measurement type.
- [ ] Produce a one-page FinOps report with evidence-backed recommendations, risks, owners, and no fabricated savings.

**Roadmap common mistakes to avoid:** monitoring only compute; failing to tag workloads; ignoring serverless features; and setting suspension thresholds that break critical jobs without a plan.

---

## 17. Official references

Use these as the source of truth for current syntax, view columns, latency, feature support, and pricing terms. Documentation can change after this lesson is authored.

- [Understanding overall cost](https://docs.snowflake.com/en/user-guide/cost-understanding-overall)
- [Managing cost in Snowflake](https://docs.snowflake.com/en/user-guide/cost-management-overview)
- [Exploring overall cost](https://docs.snowflake.com/en/user-guide/cost-exploring-overall)
- [Exploring compute cost](https://docs.snowflake.com/en/user-guide/cost-exploring-compute)
- [Exploring storage cost](https://docs.snowflake.com/en/user-guide/cost-exploring-data-storage)
- [DATA_TRANSFER_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/data_transfer_history)
- [USAGE_IN_CURRENCY_DAILY](https://docs.snowflake.com/en/sql-reference/organization-usage/usage_in_currency_daily)
- [Custom budgets](https://docs.snowflake.com/en/user-guide/budgets/custom-budget)
- [Working with resource monitors](https://docs.snowflake.com/en/user-guide/resource-monitors)
- [Budgets](https://docs.snowflake.com/en/user-guide/budgets)
- [Budget cost considerations](https://docs.snowflake.com/en/user-guide/budgets/cost)
- [Account Usage reference](https://docs.snowflake.com/en/sql-reference/account-usage)
- [WAREHOUSE_METERING_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history)
- [QUERY_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/query_history)
- [QUERY_ATTRIBUTION_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/query_attribution_history)
- [QUERY_METERING_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/query_metering_history)
- [DYNAMIC_TABLE_REFRESH_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/dynamic_table_refresh_history)
- [STORAGE_USAGE](https://docs.snowflake.com/en/sql-reference/account-usage/storage_usage)
- [STORAGE_DAILY_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/storage_daily_history)
- [METERING_DAILY_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/metering_daily_history)
- [METERING_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/metering_history)
- [SERVERLESS_TASK_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/serverless_task_history)
- [Attributing cost](https://docs.snowflake.com/en/user-guide/cost-attributing)
- [Snowflake pricing](https://www.snowflake.com/pricing/)

---

**End of lesson — Topic 10: Cost monitoring and resource monitors.**
