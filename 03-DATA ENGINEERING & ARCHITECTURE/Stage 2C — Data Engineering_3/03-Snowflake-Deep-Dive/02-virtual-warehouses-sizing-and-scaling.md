# Virtual Warehouses: Sizing and Scaling

**Roadmap location:** `Stage 2C — Data Engineering_3/03-Snowflake-Deep-Dive/02-virtual-warehouses-sizing-and-scaling.md`  
**Module:** Snowflake Deep Dive · Topic 02  
**Level:** Beginner → Advanced

> This lesson follows Topic 01, *Snowflake architecture: storage, compute, and services*. A virtual warehouse is the user-managed compute layer; it is not the database storage layer and it is not the whole Snowflake service.

## 1. Scope, prerequisites, and learning objectives

### Prerequisites

You should be able to connect to Snowflake, select a database/schema/warehouse, run basic SQL, read a query result, and explain the separation of storage and compute. You should also understand that a query may be served by result reuse and that pruning/data layout can affect how much work the warehouse performs.

### Learning objectives

By the end, you can:

- Explain a virtual warehouse and the XS–6XL size/credit relationship.
- Create, suspend, resume, resize, and safely configure a warehouse.
- Calculate illustrative credit consumption with the 60-second minimum and per-second billing in mind.
- Distinguish **scale-up** (more resources per cluster) from **scale-out** (more clusters for concurrent queries).
- Explain multi-cluster min/max settings, Standard and Economy policies, queuing, and workload isolation.
- Use Query Profile evidence to diagnose queueing, execution bottlenecks, and local/remote spilling.
- Set statement timeouts and query tags for operational safety and cost attribution.
- Benchmark cost per completed workload, rather than selecting a warehouse based on runtime alone.
- Explain when Query Acceleration Service (QAS), Search Optimization Service (SOS), specialized warehouse types, or serverless task compute may help.
- Produce a sensible warehouse layout for ETL, BI, data science/ML, and ad hoc work.

## 2. Beginner: warehouse fundamentals

### 2.1 What a virtual warehouse is

A **virtual warehouse** is a configurable pool of compute resources that executes queries and data-manipulation work, including many loads and DML operations. A warehouse can be started, suspended, resized, and (for eligible multi-cluster configurations) scaled across clusters independently of the stored table data.

This separation matters operationally: data remains in Snowflake-managed storage while a warehouse provides compute when work is submitted. You can use different warehouses against the same data to isolate workloads and tune latency/cost independently. A warehouse is not a dedicated database server you must leave running continuously.

**Use it for:** SQL queries, transformations, ELT, BI dashboards, and other operations requiring warehouse compute.  
**Trade-off:** a running warehouse consumes credits even when lightly utilized; a larger warehouse costs more per unit time and does not guarantee a proportional speedup for every query.

### 2.2 Size and the credit-per-hour doubling rule

Warehouse size describes the resources available **per cluster**. For **Gen1 standard warehouses**, the familiar reference schedule is:

| Size | Gen1 standard credits per full hour per cluster | Relative hourly rate (XS = 1) |
|---|---:|---:|
| X-Small (XS) | 1 | 1× |
| Small (S) | 2 | 2× |
| Medium (M) | 4 | 4× |
| Large (L) | 8 | 8× |
| X-Large (XL) | 16 | 16× |
| 2X-Large | 32 | 32× |
| 3X-Large | 64 | 64× |
| 4X-Large | 128 | 128× |
| 5X-Large | 256 | 256× |
| 6X-Large | 512 | 512× |

Each size step generally doubles the compute capacity and hourly credit rate for Gen1 standard warehouses. **Do not blindly apply this table to every warehouse type or generation.** Gen2 standard warehouses and Snowpark-optimized warehouses have their own service-consumption details; consult the current service consumption table for your region, generation, type, and configuration. Gen2 availability and supported sizes vary.

The table is a unit for reasoning, not a monetary price. Snowflake credits are not a universal fixed currency amount: your contract, cloud/region, edition, and pricing model determine the effective monetary cost.

### 2.3 Per-second billing and the 60-second minimum

Warehouse compute is billed per second **after a 60-second minimum when compute resources are provisioned**. Suspending after 20 seconds does not avoid the first minute. After that first minute, a continuously running warehouse accrues usage by the second. If the warehouse is suspended and later resumed, a new minimum period applies. Additional clusters started by a multi-cluster warehouse also consume credits while running; include their actual run intervals and any applicable provisioning minimums when estimating usage. Resizing provisions additional resources and increases billed usage while those resources run; resizing from 5XL/6XL down to 4XL or smaller can briefly overlap old and new resources while the old resources quiesce.

For multi-cluster warehouses, calculate credits from the size and actual running time of each cluster; a maximum cluster count is a cap, not proof that every cluster ran for the entire interval. For resizing, account for additional compute provisioned at the resize time, and note the documented brief overlap when resizing from 5XL/6XL to 4XL or smaller.

For a simple Gen1 XS example:

- Hourly rate: 1 credit/hour.
- Run continuously for 30 seconds after resume: approximately `1 × 60 / 3600 = 0.0167` credits, billed as one minute.
- Run for 10 minutes: approximately `1 × 10 / 60 = 0.1667` credits.

Actual billing records can be rounded for display, and warehouse type/generation can change the rate. These examples use the Gen1 reference table only.

**Production implication:** very short bursts that repeatedly resume a warehouse can pay multiple minimum periods. Auto-suspend is useful, but its threshold should be aligned with workload gaps rather than set blindly to the smallest possible value.

### 2.4 Warehouse lifecycle

```text
                 query arrives
                      |
                      v
            +--------------------+
            | SUSPENDED warehouse|
            +--------------------+
               | AUTO_RESUME=TRUE
               | (or manual RESUME)
               v
            +--------------------+       idle for AUTO_SUSPEND
            | RESUMING / STARTING |------------------------------+
            +--------------------+                              |
                      | ready                                   v
                      v                                +--------------------+
            +--------------------+                     | SUSPENDED warehouse|
            | RUNNING: executes  |<--------------------+--------------------+
            | queries and DML    |
            +--------------------+
               |        ^
               |        | ALTER WAREHOUSE ... RESUME
               |        | (if suspended)
               +--------+
```

A warehouse can be manually suspended/resumed. With `AUTO_RESUME = TRUE`, a query needing the warehouse can cause it to resume. With `AUTO_SUSPEND`, Snowflake suspends it after the configured idle interval. A newly created warehouse can be set to start suspended with `INITIALLY_SUSPENDED = TRUE`.

### 2.5 Create and operate a safe warehouse

Run this in a role that has the required warehouse-creation and usage privileges. Names are examples; check your organisation's naming and governance rules first.

```sql
-- If DE_LAB_XS already exists, stop and choose a unique lab name; do not reuse it.
CREATE WAREHOUSE DE_LAB_XS
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Learning lab: small, auto-suspending warehouse';

-- Select the warehouse for this session.
USE WAREHOUSE DE_LAB_XS;

-- Inspect configured properties and current state.
SHOW WAREHOUSES LIKE 'DE_LAB_XS';

-- Suspend when finished; this stops warehouse compute billing while suspended.
ALTER WAREHOUSE DE_LAB_XS SUSPEND;

-- Resume explicitly when required.
ALTER WAREHOUSE DE_LAB_XS RESUME;

-- Resize for a controlled test, then restore the small size.
ALTER WAREHOUSE DE_LAB_XS SET WAREHOUSE_SIZE = 'SMALL';
ALTER WAREHOUSE DE_LAB_XS SET WAREHOUSE_SIZE = 'XSMALL';
```

If you created `DE_LAB_XS` only for this example and have finished with it, verify it is not shared, suspend it if it is running, then remove it:

```sql
-- Execute only if this example created the warehouse and it is not shared.
-- If it is already suspended, skip the ALTER line and run only DROP.
ALTER WAREHOUSE DE_LAB_XS SUSPEND;
DROP WAREHOUSE DE_LAB_XS;
```

`AUTO_SUSPEND = 60` means 60 seconds of inactivity, not 60 minutes. `AUTO_RESUME` is a convenience, not a replacement for privilege controls and monitoring. Do not use `CREATE OR REPLACE WAREHOUSE` casually against a shared production object: replacement can reset properties and disrupt users. For disposable labs, fail fast if the chosen name already exists rather than silently reusing it; use reviewed `ALTER` statements only when you intentionally mean to modify an existing warehouse.

## 3. Intermediate: scaling and concurrency

### 3.1 Scale-up versus scale-out

| Dimension | Scale-up | Scale-out |
|---|---|---|
| Change | Increase warehouse size, e.g. XS → S → M | Add clusters to a multi-cluster warehouse, e.g. 1 → 2 → 3 |
| Primary goal | Give an individual query or workload more compute resources | Increase concurrent query capacity and reduce contention/queueing |
| Typical signal | Long execution time, CPU/resource pressure, spilling, large/complex operations | Many queries arrive together; queueing rises while individual queries are not necessarily resource-starved |
| Cost effect | Higher credit rate per active cluster | Credits increase as additional clusters run |
| Limitation | A query may not speed up proportionally; poor SQL/pruning may dominate | Does not automatically make one query faster; it distributes concurrency across clusters |

**Rule of thumb:** tune the query and data access first; scale up when a workload needs more resources; scale out when concurrency is the problem. These approaches can coexist, but they solve different problems.

### 3.2 Multi-cluster warehouses

A multi-cluster warehouse is one logical warehouse that can run multiple clusters of the same configured size. Multi-cluster warehouses are an Enterprise Edition (or higher) feature. `MIN_CLUSTER_COUNT` specifies the minimum number of clusters kept running in auto-scale mode; `MAX_CLUSTER_COUNT` caps the number that can run. A min/max range of 1–1 behaves as a single-cluster warehouse.

```sql
CREATE WAREHOUSE BI_CONCURRENCY_LAB
  WAREHOUSE_SIZE = 'XSMALL'
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 3
  SCALING_POLICY = 'STANDARD'
  ENABLE_QUERY_ACCELERATION = FALSE
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Lab only: evaluate concurrency scaling';

-- Change settings only after checking edition and workload requirements.
ALTER WAREHOUSE BI_CONCURRENCY_LAB SET
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 2
  SCALING_POLICY = 'ECONOMY';
```

This example creates a separate object. If you run it only for practice, remove it after use once you have verified it is not shared: suspend it if running, then execute `DROP WAREHOUSE BI_CONCURRENCY_LAB;`.

In auto-scale mode, Snowflake decides when to start/stop clusters within the configured range. More clusters mean more concurrent compute capacity and potentially more credits. Setting a minimum above one can preserve ready capacity but charges for those clusters while they run; a maximum that is too low can leave queries queued during spikes. `AUTO_SUSPEND` applies to the warehouse as a whole, not independently to every cluster: Snowflake scales down toward the configured minimum first, and suspends the whole warehouse only when the minimum cluster count is running and the warehouse has been idle for the configured interval. Confirm the account edition and the allowed maximum cluster count for the selected warehouse size before deployment.

#### Standard versus Economy scaling policies

- **Standard** prioritizes responsiveness and minimizing queueing by favoring additional clusters when queries queue or Snowflake estimates the running clusters lack capacity. It can consume more credits during bursts.
- **Economy** conserves credits by starting a new cluster only when Snowflake estimates enough load exists to keep it busy for about six minutes, and by marking lightly loaded clusters for shutdown when estimated remaining work is below that threshold. It can be appropriate for less latency-sensitive workloads, but may increase queue time.

These are policies for **auto-scale multi-cluster warehouses**. In maximized mode, all configured clusters run, so the auto-scale policy does not decide whether to start or stop clusters. Confirm exact behaviour in the current Snowflake documentation because policy implementation can evolve.

### 3.3 Understand concurrency and queueing

A warehouse can execute multiple queries concurrently, but capacity is finite. The number that can run at once depends on query size, complexity, memory/resource demand, and current load—not simply a fixed number of users. If a query cannot obtain sufficient resources, it can wait in a queue. Queueing may be a concurrency symptom, but it can also result from provisioning, transaction locks, or other operational factors; inspect the query's timing and profile before choosing a fix.

Possible responses:

1. Reduce unnecessary work: avoid `SELECT *`, filter early where possible, improve joins, and verify partition pruning.
2. Separate workloads so a long ETL query does not compete with interactive dashboards.
3. Scale up if individual queries are resource-bound.
4. Use multi-cluster scaling for predictable bursts of concurrent queries when edition and cost allow.
5. Review BI result reuse and caching before provisioning extra capacity.

### 3.4 Query Profile: execution, queueing, and spilling

Open a query in Snowsight and select **Query Profile**. Exact labels can change, but investigate these categories:

- **Queued time:** time waiting before execution. If elevated, investigate concurrency, warehouse state/provisioning, and contention. It is not fixed by a bigger warehouse in every case.
- **Execution time:** time spent processing the query. Inspect expensive operators, scans, joins, aggregations, and data movement.
- **Local spilling:** intermediate data exceeds available memory and spills to local storage. It can slow processing. A larger warehouse may provide more resources, but first check join shape, cardinality, aggregation size, and unnecessary columns.
- **Remote spilling:** intermediate data spills beyond local storage to remote storage; this is often more expensive in latency and is a strong signal to investigate memory pressure and query design. It is not, by itself, proof that the warehouse must be resized.
- **Scan/pruning evidence:** inspect partitions scanned versus total where available, bytes scanned, and scan operators. Poor pruning can make even a large warehouse do excessive work.

**Do not diagnose by total elapsed time alone.** Query Profile timings can include multiple concurrent operators and should not always be added together as if they were sequential wall-clock durations. Compare the same query, data state, cache state, and workload conditions.

#### Profile exercise

For a query that runs slowly, record:

1. Total elapsed time and queued time.
2. Execution time and the most expensive operators.
3. Local/remote spill evidence.
4. Bytes scanned and partitions scanned/total, if applicable.
5. Warehouse size, cluster count, and whether the result was reused from cache.

Then classify the primary issue: **query efficiency**, **per-query compute/memory**, **concurrency/queueing**, or **measurement/cache confounder**. State what evidence supports your classification before changing the warehouse.

### 3.5 Timeouts, statement limits, and query tags

Timeouts are guardrails. Use them to stop runaway queries, not to hide poor performance. Session/object parameters and account-level policy vary by role and environment; confirm privileges and precedence before changing shared settings.

```sql
-- Session-level attribution for queries run in this session.
ALTER SESSION SET QUERY_TAG = 'lab:warehouse-sizing:xs-baseline';

-- Session-level safety limits (seconds). Example values only.
ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 1800;
ALTER SESSION SET STATEMENT_QUEUED_TIMEOUT_IN_SECONDS = 120;

-- Check current session parameters.
SHOW PARAMETERS LIKE 'STATEMENT%TIMEOUT%' IN SESSION;
SHOW PARAMETERS LIKE 'QUERY_TAG' IN SESSION;

-- Remove the lab tag when finished if you continue using the session.
ALTER SESSION UNSET QUERY_TAG;
```

`STATEMENT_TIMEOUT_IN_SECONDS` caps statement runtime; `STATEMENT_QUEUED_TIMEOUT_IN_SECONDS` limits how long a statement waits in a queue. Use values that match the workload's service-level objectives. For example, an interactive BI request may need a short queue timeout, while a long batch transformation may need a longer execution timeout. A timeout does not guarantee that every downstream side effect can be rolled back in the way an application expects; design retry and transaction behaviour deliberately.

Query tags provide a useful attribution label for query history and reporting. Use stable, non-sensitive values such as team, workload, pipeline, and experiment identifier. Do not put secrets or personal data in tags.

## 4. Advanced: measure cost and choose the right configuration

### 4.1 Benchmarking methodology

Compare the **same representative workload** on XS, S, M, and L where feasible. Keep the SQL, data snapshot, session settings, role, query tag, and concurrency conditions consistent. For each run record:

- elapsed time and queue time;
- warehouse size and cluster count;
- Query Profile spill and scan/pruning evidence;
- cache status (especially result reuse);
- warehouse credits or a defensible estimate from metering data;
- success/failure and rows/records processed.

Avoid a benchmark where the first run is cold and later runs are served from result cache without accounting for that difference. For a fair compute benchmark, disable persisted query-result reuse in each benchmark session with `ALTER SESSION SET USE_CACHED_RESULT = FALSE;`, and verify each query actually executed in Query History. This does **not** disable the warehouse's local data cache; record warehouse cache conditions too. Restore the session parameter when done (`ALTER SESSION UNSET USE_CACHED_RESULT;` if the session inherited no explicit override, or set it back to the intended prior value). Do not disable caching in production merely to improve a benchmark; isolate the experiment.

Use query history and warehouse metering history after the account's data becomes available. History latency and granularity mean they may not give a perfect per-query allocation for very short runs. If multiple queries share a warehouse concurrently, warehouse-level metering cannot be naively assigned to one query without an attribution method. Use query attribution where available, or label results as estimates.

### 4.2 Cost per completed workload, not runtime alone

For a Gen1 standard warehouse, a simplified uninterrupted-run estimate is:

`credits ≈ (credits_per_hour_per_cluster × active_cluster_seconds) / 3600`

Apply the 60-second minimum for each cluster start/resume and account for additional clusters, resizing, and the actual warehouse generation/type. This is a learning approximation, not a replacement for account metering.

**Illustrative example with explicit assumptions:** assume a single Gen1 standard warehouse, no resizing, one cluster, a continuously active interval of at least 60 seconds, no additional serverless charges, and the reference rates above. Ignore storage, cloud services, contract pricing, and any non-warehouse services.

| Size | Assumed runtime | Gen1 rate | Estimated warehouse credits |
|---|---:|---:|---:|
| XS | 20 minutes | 1 credit/hour | 0.333 credits |
| S | 12 minutes | 2 credits/hour | 0.400 credits |
| M | 7 minutes | 4 credits/hour | 0.467 credits |
| L | 4 minutes | 8 credits/hour | 0.533 credits |

These times are **hypothetical**, not benchmark results. The larger warehouse finishes sooner, but XS has the lowest estimated credit consumption in this example. If the L runtime were sufficiently lower, its cost per completed job could become lower; measure instead of assuming runtime halves at every size.

A simple comparison metric is:

`credits per successful job = measured credits attributable to the workload / successful completed jobs`

Also track latency percentiles, failure/retry rate, concurrency, and cost per unit of output (for example, per million rows transformed). A warehouse that is cheapest for one batch job may be wrong for a dashboard with a strict p95 latency target.

### 4.3 Auto-suspend and bursty workloads

Auto-suspend stops warehouse compute after an idle interval. Shorter thresholds reduce idle burn, but if the workload has frequent gaps, repeated resumes can trigger multiple 60-second minimums and add startup latency. Longer thresholds reduce start/stop churn but spend more credits during idle periods. Choose a threshold using observed inter-arrival gaps and availability requirements.

**Illustrative saving calculation:** assume Gen1 XS (1 credit/hour), queries occupy the warehouse for a total of 30 minutes across one hour, and the alternative configuration leaves it running for the full hour. If a 60-second auto-suspend policy actually reduces active time to 35 minutes (including startup/idle gaps and minimum billing effects), the simple estimate is 0.583 credits versus 1.0 credit, a reduction of about 0.417 credits (41.7%). This is only an example: real savings depend on request timings, resume frequency, warehouse startup, and actual metering. Measure a representative day rather than extrapolating from this assumption.

### 4.4 Query Acceleration Service versus Search Optimization Service

These are distinct services, not substitutes for basic query tuning or warehouse sizing.

| Feature | Main purpose | Consider when | Cost / caution |
|---|---|---|---|
| **Query Acceleration Service (QAS)** | Offloads eligible portions of certain query workloads to additional Snowflake-managed compute, potentially reducing elapsed time for supported query patterns | Large scans/filters with eligible work and variable query performance; test against the actual query profile | Has separate serverless-style credit consumption and eligibility/scale settings. It may add cost without helping ineligible or already-efficient queries. |
| **Search Optimization Service (SOS)** | Maintains search access paths to accelerate selective lookups and supported predicates, including certain equality/substring/semi-structured cases | Selective point-lookups against large tables where pruning alone is insufficient | Adds maintenance and storage/compute cost; best evaluated for selective access patterns, not broad scans or every query. |

QAS is about accelerating eligible work during query execution; SOS maintains search optimization structures to make qualifying selective access faster. First inspect the profile and query shape. Use a controlled before/after experiment and compare latency plus the full incremental service cost. Current Snowflake documentation states that QAS is enabled by default for newly created Gen2 standard and multi-cluster warehouses; inspect `ENABLE_QUERY_ACCELERATION` and the scale-factor setting instead of assuming it is off. Actual QAS credits depend on eligible queries using the service, and are billed separately from warehouse compute. Exact eligibility and billing rules are version-sensitive; see official references.

### 4.5 Warehouse types and serverless compute: awareness

- **Gen2 standard warehouses:** a newer standard-warehouse generation with hardware/software improvements. Many workloads may finish faster, but results vary; benchmark cost per workload. Availability and supported sizes can differ by region and configuration. Do not compare Gen1 and Gen2 solely by assuming identical credit rates and runtime. Snowflake currently enables Query Acceleration Service (QAS) by default for Gen2 standard warehouses; include any QAS consumption in total workload cost and verify the current default/scale-factor behavior for your account.
- **Snowpark-optimized warehouses:** specialized for memory-intensive Snowpark workloads such as Python processing or ML-style tasks with higher memory needs. They are not automatically better for ordinary SQL analytics and can have different credit rates and startup/performance characteristics. Choose only after confirming a memory-bound workload and testing.
- **Serverless task compute:** for supported serverless tasks, Snowflake manages the compute rather than requiring a user-managed warehouse. This is a separate billing model; compare the serverless task charge and operational characteristics against a warehouse-backed task. Not all task configurations use serverless compute.
- **Other serverless features:** QAS and SOS can incur charges outside the warehouse's normal running credits. Snowflake currently enables QAS by default for newly created multi-cluster warehouses as well as Gen2 standard warehouses; creating or converting a warehouse does not mean QAS charges are always present, but the setting and actual eligible-query usage must be checked. Warehouse metering alone therefore does not describe the whole workload cost. Include QAS and SOS consumption in the full cost comparison when applicable.

Keep the distinction clear: a warehouse is user-managed compute; serverless features use Snowflake-managed compute and have feature-specific billing. Avoid assuming that auto-suspend on a warehouse controls serverless charges.

## 5. Workload isolation and concurrency architecture

### 5.1 Example team layout

A team has scheduled ELT, interactive BI, data science/ML exploration, and occasional ad hoc analysis. Use separate warehouses to reduce resource contention, assign ownership, and attribute usage. The following is a starting design, not a universal sizing prescription.

| Warehouse | Workload | Starting configuration | Scaling approach | Rationale / guardrail |
|---|---|---|---|---|
| `WH_ETL_BATCH` | Scheduled transformations and batch DML | S or M, initially suspended, auto-resume; auto-suspend after observed job gaps | Scale up for a large transformation; use a bounded cluster range only if jobs genuinely overlap | Predictable windows; tag each pipeline; set timeouts and alert on failures. |
| `WH_BI_INTERACTIVE` | Dashboards and analyst queries | S or M; auto-resume; idle threshold tuned to dashboard cadence | Multi-cluster auto-scale for bursts of concurrent users if Enterprise+ is available; Standard for latency-oriented bursts, Economy if queueing is acceptable | Protect interactive latency from batch work; measure p95 and queue time. |
| `WH_DS_ML` | Feature exploration, model preparation, Snowpark jobs | S initially; test standard vs Snowpark-optimized for memory-heavy tasks | Scale up for a proven compute/memory bottleneck; do not assume more clusters speed one training job | Use tags, bounded runtime, separate permissions, and scheduled shutdown when work is complete. |
| `WH_ADHOC` | Exploratory SQL and one-off analysis | XS or S; aggressive auto-suspend | Usually one cluster; cap usage through governance and monitoring | Isolate experimentation and prevent unbounded ad hoc jobs from affecting BI. |

### 5.2 Design principles

1. **Separate by service objective and workload behaviour**, not by every individual user. A separate warehouse is useful when it isolates contention, ownership, permissions, or budget; too many tiny warehouses can add operational complexity.
2. **Use least privilege.** Grant usage to roles that need each warehouse; do not grant broad administrative privileges merely to let analysts run queries.
3. **Tag work.** Apply a session query tag or an orchestration-level tag consistently. Make it easy to answer “which team or pipeline caused this spend?”
4. **Set budgets and monitor usage.** Warehouse auto-suspend is a guardrail, not a complete cost-control strategy. Monitor warehouse credits and serverless feature usage separately; configure resource monitors/budgets according to your account's governance model.
5. **Treat BI concurrency separately from per-query performance.** A multi-cluster warehouse can add parallel capacity; a larger cluster is more directly aimed at individual-query resources.
6. **Use result reuse and data pruning.** If the result cache can serve repeated identical queries, extra warehouse compute may not be the relevant lever. For cache misses, optimize scans and joins before paying for more compute.
7. **Avoid noisy-neighbour effects.** A large, long-running ETL query can compete with interactive BI on the same warehouse. Separate warehouses when service objectives conflict.

## 6. Hands-on lab — `experiments/02_warehouses/`

The roadmap names `experiments/02_warehouses/` as the lab location. No separate `experiments/02_warehouses/` directory or lab files were present in the supplied workspace for this audit, so the complete exercise specification is included below. If your repository keeps lab scripts and measurement notes separately, place them in that directory; do not treat this audit as verification of files that were not supplied.

### 6.1 Lab safety and prerequisites

You need a Snowflake account, permission to create/use warehouses and query history, and Snowsight access to Query Profile. Multi-cluster testing requires a suitable edition (Enterprise or higher). If you do not have the required edition, document the limitation and complete the single-cluster portions; do not claim a multi-cluster comparison was run.

Use a dedicated lab warehouse, a small dataset/query, and a short time window. A large query or 30 concurrent sessions can create real usage. Obtain approval before running a load test in a shared account. Do not create 30 concurrent queries against production. Warehouse and feature prices vary; this lab records credits and elapsed time, not a guaranteed monetary amount.

### 6.2 Setup

```sql
-- If this name already exists, stop and choose a unique lab name.
CREATE WAREHOUSE WH_LAB_SIZE
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Topic 02 sizing experiment';

USE WAREHOUSE WH_LAB_SIZE;
ALTER SESSION SET QUERY_TAG = 'lab:topic02:warehouse-sizing';
ALTER SESSION SET USE_CACHED_RESULT = FALSE;

-- A deterministic starter workload. Replace/extend only if it is too short
-- to provide useful profile/size differences; do not fabricate benchmark data.
SELECT
  MOD(SEQ4(), 1000) AS bucket,
  COUNT(*) AS row_count
FROM TABLE(GENERATOR(ROWCOUNT => 1000000))
GROUP BY 1
ORDER BY 1;
```

This query generates one million synthetic rows and aggregates them; it avoids creating a persistent large table. It is only a representative starter workload and may be too simple to reveal a meaningful scaling difference. To test production-like performance, use a permitted non-sensitive dataset with realistic joins, filters, and volume. Keep query text and data consistent across size tests. `USE_CACHED_RESULT = FALSE` prevents persisted query-result reuse in this session but does not disable the warehouse's local data cache; record both result-reuse evidence and warehouse-cache conditions.

### 6.3 Experiment A — XS through L

Run the exact same query at each size. Set a unique query tag per run so history is easier to filter. Allow the warehouse to reach the requested size before running the measured query. Keep `USE_CACHED_RESULT = FALSE` for every run, verify that each query actually executes, and record warehouse local-cache state. If a session was opened with a prior explicit value for `USE_CACHED_RESULT`, restore that prior value after the test rather than blindly unsetting it.

```sql
ALTER WAREHOUSE WH_LAB_SIZE SET WAREHOUSE_SIZE = 'XSMALL';
ALTER SESSION SET QUERY_TAG = 'lab:topic02:size:xs';
-- Run the representative SELECT above; save its query ID and open Query Profile.

ALTER WAREHOUSE WH_LAB_SIZE SET WAREHOUSE_SIZE = 'SMALL';
ALTER SESSION SET QUERY_TAG = 'lab:topic02:size:s';
-- Run the same SELECT; save query ID and profile.

ALTER WAREHOUSE WH_LAB_SIZE SET WAREHOUSE_SIZE = 'MEDIUM';
ALTER SESSION SET QUERY_TAG = 'lab:topic02:size:m';
-- Run the same SELECT; save query ID and profile.

ALTER WAREHOUSE WH_LAB_SIZE SET WAREHOUSE_SIZE = 'LARGE';
ALTER SESSION SET QUERY_TAG = 'lab:topic02:size:l';
-- Run the same SELECT; save query ID and profile.
```

Use a table in your notes with `size`, `query_id`, `elapsed seconds`, `queued seconds`, `local spill`, `remote spill`, `bytes scanned`, `cache evidence`, and `credits (measured or estimate)`. Do not invent values: record what your account actually shows. If the query is too short to produce useful differences, choose a slightly more demanding permitted query rather than increasing warehouse size indefinitely.

**Fairness controls:** use comparable cache conditions; ensure each run really executes; avoid concurrent unrelated work on the lab warehouse; record generation/type; allow resizing to complete; repeat runs if results vary. Do not compare a cache-served result against a full execution and call it a warehouse speedup.

**Expected observations:** larger warehouses may reduce runtime for compute-bound work, but speedup is workload-dependent and may be small for simple, scan-limited, cache-served, or otherwise non-compute-bound queries. Credits per job can rise even as elapsed time falls. Spilling may decrease if more memory is available, but that is not guaranteed. These are hypotheses to test, not promised results.

### 6.4 Experiment B — single cluster versus multi-cluster concurrency

This experiment is optional if your account edition does not support multi-cluster warehouses. Use a test account and low-cost query, not a production service. The roadmap suggests 30 concurrent small queries; treat that as an upper lab target, and start with 5–10 clients to verify safety before increasing to 30.

```sql
-- If either name already exists, stop and choose unique lab names.
CREATE WAREHOUSE WH_LAB_SINGLE
  WAREHOUSE_SIZE = 'XSMALL'
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 1
  ENABLE_QUERY_ACCELERATION = FALSE
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

CREATE WAREHOUSE WH_LAB_MULTI
  WAREHOUSE_SIZE = 'XSMALL'
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 3
  SCALING_POLICY = 'STANDARD'
  ENABLE_QUERY_ACCELERATION = FALSE
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;
```

Run the same set of concurrent client queries first on `WH_LAB_SINGLE`, then on `WH_LAB_MULTI`. For a valid comparison, use the same query, input, client count, session behavior, and test duration. Set `USE_CACHED_RESULT = FALSE` in every worker session and assign a query tag that identifies the test/worker; otherwise result reuse can invalidate the comparison. Record total completion time, per-query latency distribution, queue time, clusters observed, warehouse credits, and QAS credits if QAS is enabled/used. Check Snowsight/warehouse history for scaling evidence; scaling can take time and may not occur if queries are too short or the concurrency does not exceed available capacity. A multi-cluster warehouse may have QAS enabled by default, so compare like-for-like QAS settings where possible or explicitly include QAS usage in total cost.

A Python connector harness can run parallel queries, but connection parameters should come from environment variables or a secrets manager—not hard-coded credentials. If implementing a harness, open one connection per worker, set the warehouse and query tag, execute the same statement, record query IDs and monotonic elapsed times, then close every connection in `finally` blocks. Respect account concurrency limits and stop if spend or queueing exceeds your test budget.

**Expected observations:** the multi-cluster configuration may reduce queueing during a burst, but can consume more credits when extra clusters run. If the queries are tiny, cached, or not sufficiently concurrent, Snowflake may not start another cluster and the measured difference may be negligible. Do not interpret “no scaling occurred” as proof the feature is broken; inspect workload intensity and cluster history.

### 6.5 Experiment C — auto-suspend for bursty usage

1. Choose a lab workload that runs in short bursts with realistic idle gaps. Use a dedicated warehouse and a bounded test window.
2. Set a baseline threshold such as `AUTO_SUSPEND = 600`, then record the exact burst schedule, query IDs, number of resumes, startup latency, and credits. Make the idle gaps longer than 60 seconds but shorter than the baseline threshold so the two policies can be compared:

   ```sql
   ALTER WAREHOUSE WH_LAB_SIZE SET AUTO_SUSPEND = 600 AUTO_RESUME = TRUE;
   ```
3. Set `AUTO_SUSPEND = 60` and `AUTO_RESUME = TRUE`:

   ```sql
   ALTER WAREHOUSE WH_LAB_SIZE SET AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;
   ```

4. Repeat the same schedule over a comparable period. Record number of resumes, active duration, minimum billing periods, query startup latency, and credits.
5. Repeat the same burst schedule and compare measured credits, number of resumes, and latency. If possible, repeat the baseline/test sequence to reduce time-of-day confounding; do not extrapolate from a single short burst to a whole day without stating the assumptions.

The warehouse suspends only after its idle period, and each resume can invoke the 60-second minimum. If the workload has gaps shorter than the threshold, it may remain running; if gaps are long, suspension may reduce idle burn but add startup latency. Choose a policy that satisfies the workload's latency objective.

### 6.6 Experiment D — warehouse design document

Write a one-page proposal using the table in Section 5. Include workload owner, expected schedule/concurrency, starting size, min/max clusters, scaling policy, auto-suspend, query tag convention, timeout policy, budget/alert, and the evidence that would trigger resizing. State which recommendations are measured and which are hypotheses.

### 6.7 Troubleshooting

| Symptom | Checks | Safe response |
|---|---|---|
| Warehouse does not resume | Current role privileges, warehouse state, `AUTO_RESUME`, session's selected warehouse | Verify `USE WAREHOUSE`; ask an administrator for only the needed grants. |
| Query is slow at every size | Query Profile, scan/pruning, joins, filters, cache status, remote spill | Fix query/data access or test a representative workload before further scaling. |
| Query is queued | Queue time, active workload, cluster count, warehouse state | Separate workloads or evaluate multi-cluster scaling if concurrency is the cause. |
| Multi-cluster does not scale out | Edition, min/max settings, scaling policy, workload duration/intensity, cluster history | Increase test concurrency carefully; verify supported configuration before drawing conclusions. |
| Credit numbers do not match hand estimates | Warehouse type/generation, multiple clusters, start/resume minimums, resize overlap, history latency/rounding, concurrent workloads | Label estimates, inspect metering history, and account for all active clusters and feature charges. |
| Auto-suspend saves less than expected | Frequent resumes, 60-second minimums, gaps shorter than threshold, other active clusters | Measure event timing and tune threshold; do not assume a lower value always saves money. |

### 6.8 Cleanup

Run cleanup only if the corresponding `CREATE WAREHOUSE` statement succeeded in this lab run and the name was not an existing/shared resource. First ensure no other person or job depends on the lab warehouses. Suspend, then drop only the resources created by this run:

```sql
ALTER WAREHOUSE WH_LAB_SIZE SUSPEND;
DROP WAREHOUSE WH_LAB_SIZE;

-- Run these pairs only if the optional concurrency experiment created them.
ALTER WAREHOUSE WH_LAB_SINGLE SUSPEND;
DROP WAREHOUSE WH_LAB_SINGLE;
ALTER WAREHOUSE WH_LAB_MULTI SUSPEND;
DROP WAREHOUSE WH_LAB_MULTI;
```

Do not run cleanup for a name whose creation failed or that you did not create. Check each warehouse state first; if it is already suspended, skip its `ALTER ... SUSPEND` statement and proceed to `DROP` only when the object was created by this run and is not shared. Do not run these `DROP` statements against shared or production warehouses. Remove session overrides/tags when the session will be reused: set `QUERY_TAG` to the intended value and restore `USE_CACHED_RESULT` to its prior setting. Keep your notes and query IDs as the experiment record.

### 6.9 Lab acceptance criteria

- [ ] The same query was tested on XS, S, M, and L, or any unavailable run was documented honestly.
- [ ] Each run includes query ID, elapsed/queued time, spill evidence, cache condition, and measured or explicitly estimated credits.
- [ ] The report distinguishes runtime improvement from cost-per-job improvement.
- [ ] Single-cluster and multi-cluster behavior were compared if the account supports it; otherwise, the limitation is recorded.
- [ ] Auto-suspend behavior was evaluated using observed burst/idle intervals and minimum billing periods.
- [ ] A workload layout exists for ETL, BI, data science/ML, and ad hoc workloads.
- [ ] All lab warehouses were suspended/dropped safely, and no code execution or measurement is claimed without evidence.

## 7. Production recommendations and operating checklist

1. **Start small, measure, and change one variable at a time.** Use XS/S as an initial test size when appropriate, but never treat a fixed size as universally optimal.
2. **Keep compute lifecycle explicit.** Set auto-suspend based on idle-gap patterns, enable auto-resume only where appropriate, and audit warehouses that remain running without work.
3. **Separate query latency from queue latency.** Scale up for resource-heavy execution; scale out for concurrent demand; optimize SQL before either when profile evidence points to unnecessary work.
4. **Benchmark cost per successful unit of work.** Include retries, data volume, latency objectives, cluster count, cache conditions, and serverless feature costs.
5. **Set workload guardrails.** Use timeouts, query tags, ownership, least-privilege access, budgets/resource monitors, and regular spend reviews.
6. **Keep workload isolation purposeful.** Distinct ETL, BI, ML, and ad hoc warehouses often improve governance and reduce noisy-neighbour effects; avoid warehouse proliferation without an operational reason.
7. **Evaluate specialized features separately.** QAS, SOS, Gen2, Snowpark-optimized warehouses, and serverless tasks should be enabled or selected based on measured workload fit and complete incremental cost.
8. **Re-test after change.** SQL changes, data growth, concurrency shifts, warehouse generation, and account configuration can change the best setting.

## 8. Common mistakes and misconceptions

- **“A bigger warehouse always makes queries faster.”** Small, cache-served, poorly pruned, or I/O-bound workloads may not benefit proportionally.
- **“More clusters make one query faster.”** Multi-cluster warehouses primarily address concurrency; scale-up is the more direct per-query capacity lever.
- **“A suspended warehouse has no cost anywhere.”** Warehouse compute stops, but other Snowflake costs—storage, data transfer, cloud services, and serverless features—may still apply.
- **“Per-second billing means a 5-second run costs only 5 seconds.”** Each resume/start has a 60-second minimum.
- **“Auto-suspend should always be one second.”** Frequent resumes can incur repeated minimum periods and latency.
- **“Queueing proves the warehouse is too small.”** It may indicate concurrency, warehouse startup, or other contention; use the profile/history evidence.
- **“More clusters are free until busy.”** Active additional clusters consume credits; minimum cluster settings can keep extra capacity running.
- **“The XS/S/M/L cost table applies to every configuration.”** The reference table is Gen1 standard; generation and warehouse type matter.
- **“Fastest runtime means best configuration.”** Compare cost per successful workload and service-level objectives.
- **“Query Profile spilling means resize immediately.”** Inspect joins, cardinality, pruning, selected columns, and resource pressure first.
- **“Warehouse metering equals total workload cost.”** Serverless features and other billable services can be separate line items.
- **“Thirty concurrent test queries are harmless.”** Load tests consume real resources and should start small in a dedicated test account.

## 9. Practice questions with answers

### Q1. What is the difference between XS and S in the Gen1 standard reference schedule?

**Answer:** XS is 1 credit/hour per cluster and S is 2 credits/hour per cluster. S has approximately twice the compute resources, but it does not guarantee half the runtime. Measure the workload.

### Q2. A warehouse resumes for 25 seconds and is suspended. How should its compute usage be estimated?

**Answer:** Apply the 60-second minimum for that resume. For Gen1 XS, the estimate is `1 × 60 / 3600 ≈ 0.0167` credits, not `25 / 3600`. A later resume incurs another minimum period.

### Q3. A dashboard has many concurrent users and rising queued time, but individual queries are reasonably fast. Should you scale up or out first?

**Answer:** Investigate concurrency and consider multi-cluster scale-out if the account edition and cost target support it. Scale-up is aimed more directly at giving each cluster more resources and may not solve burst concurrency as efficiently.

### Q4. One complex query spills to remote storage and takes a long time. What should you inspect before resizing?

**Answer:** Query Profile operators, join cardinality, aggregation size, scan volume/pruning, unnecessary columns, and local/remote spill evidence. If the query is resource/memory-bound after query improvements, test a larger warehouse and compare cost per completed job.

### Q5. Why can a larger warehouse finish a job faster but consume more credits?

**Answer:** The hourly credit rate rises with size. A shorter runtime only offsets that increase if the runtime reduction is large enough. Calculate measured credits per job rather than relying on elapsed time alone.

### Q6. When is Economy scaling policy potentially appropriate?

**Answer:** For bursty concurrency where reducing spend is more important than minimizing queue time. It can delay adding clusters relative to Standard, so it is unsuitable where queue latency must be kept low.

### Q7. What is the main difference between QAS and SOS?

**Answer:** QAS can accelerate eligible work during query execution using additional managed compute; SOS maintains search optimization structures for supported selective lookups/predicates. Their eligibility and cost models differ, and both require workload-specific testing.

### Q8. Why must a benchmark account for result cache?

**Answer:** A repeated query may return a cached result without executing the warehouse work being compared. That can make a later run appear dramatically faster and cheaper for reasons unrelated to warehouse size.

### Q9. When might a Snowpark-optimized warehouse be useful?

**Answer:** For measured memory-intensive Snowpark/Python workloads that benefit from higher memory capacity. It is not automatically a better choice for ordinary SQL and should be compared using the relevant type's credit schedule.

### Q10. Name four elements of a production warehouse design beyond size.

**Answer:** Examples include auto-suspend/resume, cluster min/max and scaling policy, query tags, statement timeouts, least-privilege grants, workload ownership/isolation, budgets/resource monitors, and latency/cost SLOs.

## 10. Roadmap-aligned final checkpoint

Use this checklist before moving to Topic 03, *Micro-partitions, clustering, and pruning*:

- [ ] **Credits and doubling rule:** explain the XS–6XL Gen1 standard reference rates and note type/generation differences.
- [ ] **Billing lifecycle:** explain per-second billing, the 60-second minimum on each start/resume, and the impact of repeated resumes.
- [ ] **Scale-up vs scale-out:** choose the right approach for per-query resource pressure versus concurrency/queueing.
- [ ] **Multi-cluster:** explain min/max cluster counts, Standard versus Economy, and how scaling affects credits.
- [ ] **Query Profile:** identify queue time, execution bottlenecks, local/remote spilling, and scan/pruning evidence.
- [ ] **Workload isolation:** design warehouses for ETL, BI, data science/ML, and ad hoc usage with ownership and guardrails.
- [ ] **Sizing methodology:** compare XS/S/M/L with consistent query/cache conditions and evaluate cost per successful workload.
- [ ] **Services and types:** distinguish QAS from SOS and explain Gen2, Snowpark-optimized warehouses, and serverless task compute at awareness level.
- [ ] **Operational safety:** configure auto-suspend/resume, timeouts, tags, budgets/monitoring, and safe cleanup.

If any item cannot be explained with evidence from the lab or a concrete example, revisit the relevant section before proceeding.

## 11. Authoritative references

Documentation is version-sensitive. Confirm current syntax, regional/edition availability, credit tables, and feature eligibility before using these settings in production.

1. [Snowflake — Overview of warehouses](https://docs.snowflake.com/en/user-guide/warehouses-overview) — sizes, warehouse properties, billing, query processing, and concurrency.
2. [Snowflake — Warehouse considerations](https://docs.snowflake.com/en/user-guide/warehouses-considerations) — sizing methodology, auto-suspend, billing for resizing, cache trade-offs, and scale-up vs scale-out.
3. [Snowflake — Multi-cluster warehouses](https://docs.snowflake.com/en/user-guide/warehouses-multicluster) — min/max clusters, auto-scale vs maximized mode, scaling policies, and cluster-count limits.
4. [Snowflake — Understanding compute cost](https://docs.snowflake.com/en/user-guide/cost-understanding-compute) — warehouse, serverless, and cloud services compute billing concepts.
5. [Snowflake — Query Profile](https://docs.snowflake.com/en/user-guide/ui-query-profile) — operator-level query diagnosis.
6. [Snowflake — Query Acceleration Service](https://docs.snowflake.com/en/user-guide/query-acceleration-service) — eligible workloads and configuration.
7. [Snowflake — Search Optimization Service](https://docs.snowflake.com/en/user-guide/search-optimization-service) — supported access patterns and maintenance considerations.
8. [Snowflake — Generation 2 standard warehouses](https://docs.snowflake.com/en/user-guide/warehouses-gen2) — Gen2 behaviour, configuration, and availability caveats.
9. [Snowflake — Snowpark-optimized warehouses](https://docs.snowflake.com/en/user-guide/warehouses-snowpark-optimized) — workload fit, memory/resource constraints, startup considerations, and billing.
10. [Snowflake — Introduction to tasks](https://docs.snowflake.com/en/user-guide/tasks-intro) — serverless versus user-managed task compute and cost considerations.

---

**Source alignment:** This lesson follows Topic 02 of `roadmap-Snowflake-Deep-Dive.md` and the target path recorded in `Roadmap_ptree.md`. It does not claim that the example SQL, lab runs, or benchmark outcomes have been executed in a Snowflake account.
