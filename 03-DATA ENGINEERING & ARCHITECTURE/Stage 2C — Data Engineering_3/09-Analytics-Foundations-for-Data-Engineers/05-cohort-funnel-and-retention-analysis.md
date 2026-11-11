# Cohort, Funnel, and Retention Analysis

> **Audience:** Data engineers, analytics engineers, product analysts, and data-platform engineers moving from basic product metrics to production-grade behavioural analytics.  
> **SQL dialect for the hands-on lab:** DuckDB SQL. Most patterns translate to PostgreSQL, BigQuery, Snowflake, Spark SQL, or Trino, but date arithmetic and incremental-merge syntax differ.  
> **Roadmap placement:** Stage 2C — `09-Analytics-Foundations-for-Data-Engineers`, lesson 05, after descriptive statistics, approximate algorithms, hypothesis testing, and A/B-test data pipelines.

## 1. Title and learning objectives

By the end of this lesson, you should be able to:

- Define DAU, WAU, MAU, activation, conversion, churn, ARPU, LTV, stickiness, and retention with explicit grains, denominators, and windows.
- Build reliable event, user-day, cohort, funnel, and revenue-cohort models.
- Calculate D1/D7/D30 and weekly cohort retention, and distinguish bounded, unbounded, and rolling retention.
- Construct strict-order and loose-order funnels with a conversion window, including time-to-convert and per-session versus per-user analysis.
- Explain sessionisation, identity resolution, event deduplication, time-zone policy, cohort maturity, and small-segment risks.
- Decompose active-user movement into new, retained, resurrected, and churned users using explicit period definitions.
- Understand right-censoring, Kaplan–Meier retention curves, hazard rates, LTV, discounting, and payback.
- Design an incremental activity pipeline and validate it against a full rebuild, including late-arriving events.

**Core principle:** a metric is not fully defined by its formula. It also needs a population, unit of analysis, event/activity definition, time window, time zone, identity policy, and data-freshness contract.

## 2. Why product analytics depends on reliable event data

Product analytics asks questions such as:

- Do users return after signing up?
- Where do prospective customers abandon checkout?
- Does a new onboarding flow improve activation?
- Which acquisition cohorts produce durable revenue?
- Are more users active because acquisition improved, existing users returned, or previously inactive users came back?

Those questions are only as reliable as the event pipeline underneath them. A duplicate `purchase` can inflate conversion and revenue. A missing `signup` can shorten a funnel or put a user in the wrong cohort. A UTC/local-date mismatch can shift activity across days. A one-to-many join can multiply users or revenue. A dashboard that silently changes the meaning of “active” can create a false trend even when the underlying behaviour is unchanged.

### 2.1 Analytical layers

A practical architecture separates these responsibilities:

1. **Raw events:** immutable or append-only source records with ingestion metadata.
2. **Canonical events:** deduplicated, typed, timestamp-normalised events with resolved identities and quality flags.
3. **Dimensions:** users, devices, accounts, acquisition attribution, geography, plan history, and identity bridges.
4. **Atomic facts:** one row per canonical event; one row per user per active day; one row per session; one row per order/payment where relevant.
5. **Metric models:** cohort membership, retention cells, funnel step timestamps, revenue by user-period, and active-user movement.
6. **Semantic layer / serving:** governed metric definitions and dashboard-friendly aggregates.

Do not calculate every dashboard metric directly from raw events independently. Shared canonical models make definitions auditable and reduce the chance that different teams count different populations.

### 2.2 Grain comes before SQL

“Grain” is what one row represents. State it before writing a query.

| Model | Grain | Candidate key | Purpose |
|---|---|---|---|
| `raw_events` | One source-delivered event record | source + source event ID, when available | Preserve source payload and ingestion history |
| `canonical_events` | One deduplicated logical event | `event_id` | Standardised behavioural facts |
| `dim_users` | One canonical user | `user_id` | Signup time and stable user attributes |
| `user_identity_map` | One identity-to-canonical-user validity interval | identity type + identity value + valid interval | Cross-device/account identity resolution |
| `user_daily_activity` | One user per local activity date | `user_id`, `activity_date`, `activity_definition_version` | Efficient retention and active-user counts |
| `sessions` | One session | `session_id` | Session-level journeys and engagement |
| `user_cohorts` | One user per cohort definition/version | `user_id`, `cohort_type`, `cohort_version` | Stable cohort membership |
| `funnel_user_summary` | One eligible user per funnel run | `funnel_id`, `user_id`, `window_start` | User-level funnel analysis |
| `user_revenue_daily` | One user per revenue date and currency | `user_id`, `revenue_date`, `currency` | Revenue cohorts, ARPU, LTV |

A join between a user row and many event rows changes the grain. Aggregate events to the intended grain before joining if the desired output is one row per user.

## 3. Prerequisites and sample schema

### 3.1 Event contract

The lab assumes these fields:

```sql
-- DuckDB-compatible logical schema
CREATE TABLE raw_events (
    event_id         VARCHAR,       -- stable logical event ID for deduplication
    source_record_id VARCHAR,       -- unique source delivery/record ID
    user_id          VARCHAR,       -- canonical user ID when known
    anonymous_id     VARCHAR,       -- device/browser identity before login
    event_name       VARCHAR,
    event_ts_utc     TIMESTAMP,     -- event occurrence time, stored as UTC by contract
    ingested_at_utc  TIMESTAMP,     -- arrival time; can be later than event time
    session_id       VARCHAR,
    source           VARCHAR,
    is_bot            BOOLEAN DEFAULT FALSE,
    properties_json  VARCHAR
);

CREATE TABLE dim_users (
    user_id         VARCHAR PRIMARY KEY,
    signup_ts_utc   TIMESTAMP NOT NULL,
    acquisition_channel VARCHAR,
    signup_device   VARCHAR,
    country         VARCHAR,
    plan_at_signup  VARCHAR
);
```

The example uses `TIMESTAMP` and a UTC-by-contract convention because DuckDB timestamp semantics depend on the exact type. In a platform with explicit time-zone-aware types, use them consistently. Do not mix naive local timestamps with UTC timestamps.

### 3.2 Required assumptions

Before running the queries, make these policies explicit:

- **Canonical identity:** `user_id` is the analysis key. Anonymous events are attached only when a governed identity bridge supports the mapping. Do not infer identity from email or device heuristics ad hoc in a metric query.
- **Deduplication:** `event_id` identifies a logical event. If a source does not provide a stable ID, create a documented source-specific deduplication key. Do not deduplicate solely on `(user_id, event_name, timestamp)` if legitimate repeated events can share those values. In the canonical layer, make `is_bot` non-null: resolve known bots to `TRUE`, known non-bots to `FALSE`, and quarantine/flag unknown status rather than silently letting SQL's three-valued logic drop rows.
- **Event ordering:** order by `event_ts_utc`, then a deterministic tie-breaker such as `event_id`. Events with identical timestamps are not naturally ordered; define tie policy for funnels.
- **Time zone:** store occurrence timestamps in UTC, then derive `activity_date` in one declared reporting time zone (the lab uses UTC). A business operating in India might choose `Asia/Kolkata`; a global product may use user-local dates for some metrics, but must label that definition explicitly.
- **Activity:** the baseline definition is a non-bot `meaningful_activity` event. Signup alone does not count as activity unless the product definition says it does.
- **Revenue:** use net recognised revenue in a single currency or report currencies separately. Do not sum unlike currencies without conversion policy and FX-rate dates.
- **Cohort membership:** users stay in their original signup cohort even if channel, device, geography, or plan later changes. Segment by acquisition-time attributes or time-valid dimensions, not by the latest value unless that is explicitly the question.

### 3.3 Small reproducible dataset

This compact dataset is deliberately small enough to inspect by hand. The later lab scales the same pattern to larger tables.

```sql
CREATE OR REPLACE TABLE dim_users AS
SELECT * FROM (VALUES
  ('u1', TIMESTAMP '2025-01-01 10:00:00', 'paid',    'mobile', 'IN', 'free'),
  ('u2', TIMESTAMP '2025-01-01 12:00:00', 'organic', 'web',    'IN', 'free'),
  ('u3', TIMESTAMP '2025-01-02 09:00:00', 'paid',    'web',    'US', 'free'),
  ('u4', TIMESTAMP '2025-01-08 14:00:00', 'referral','mobile', 'IN', 'pro'),
  ('u5', TIMESTAMP '2025-01-09 08:00:00', 'organic', 'web',    'GB', 'free')
) AS t(user_id, signup_ts_utc, acquisition_channel, signup_device, country, plan_at_signup);

CREATE OR REPLACE TABLE canonical_events AS
SELECT * FROM (VALUES
  ('e01','u1','signup',          TIMESTAMP '2025-01-01 10:00:00', FALSE, 0.00),
  ('e02','u1','meaningful_activity',TIMESTAMP '2025-01-01 10:10:00', FALSE, 0.00),
  ('e03','u1','visit',           TIMESTAMP '2025-01-01 10:11:00', FALSE, 0.00),
  ('e04','u1','add_to_cart',     TIMESTAMP '2025-01-02 09:00:00', FALSE, 0.00),
  ('e05','u1','purchase',        TIMESTAMP '2025-01-03 10:00:00', FALSE, 40.00),
  ('e06','u2','signup',          TIMESTAMP '2025-01-01 12:00:00', FALSE, 0.00),
  ('e07','u2','visit',           TIMESTAMP '2025-01-01 12:05:00', FALSE, 0.00),
  ('e08','u2','purchase',        TIMESTAMP '2025-01-01 12:10:00', FALSE, 10.00),
  ('e09','u2','meaningful_activity',TIMESTAMP '2025-01-02 13:00:00', FALSE, 0.00),
  ('e10','u3','signup',          TIMESTAMP '2025-01-02 09:00:00', FALSE, 0.00),
  ('e11','u3','visit',           TIMESTAMP '2025-01-02 09:10:00', FALSE, 0.00),
  ('e12','u3','add_to_cart',     TIMESTAMP '2025-01-02 09:20:00', FALSE, 0.00),
  ('e13','u4','signup',          TIMESTAMP '2025-01-08 14:00:00', FALSE, 0.00),
  ('e14','u4','meaningful_activity',TIMESTAMP '2025-01-08 15:00:00', FALSE, 0.00),
  ('e15','u4','visit',           TIMESTAMP '2025-01-08 15:01:00', FALSE, 0.00),
  ('e16','u4','add_to_cart',     TIMESTAMP '2025-01-08 15:03:00', FALSE, 0.00),
  ('e17','u4','purchase',        TIMESTAMP '2025-01-08 15:05:00', FALSE, 25.00),
  ('e18','u5','signup',          TIMESTAMP '2025-01-09 08:00:00', FALSE, 0.00),
  ('e19','u5','visit',           TIMESTAMP '2025-01-09 08:01:00', FALSE, 0.00),
  ('e20','u5','add_to_cart',     TIMESTAMP '2025-01-09 08:02:00', FALSE, 0.00),
  ('e21','u5','meaningful_activity',TIMESTAMP '2025-01-10 08:00:00', FALSE, 0.00)
) AS t(event_id, user_id, event_name, event_ts_utc, is_bot, revenue);
```

The compact table omits raw-ingestion metadata to keep the example readable. Production canonical events should retain source IDs, ingestion timestamps, quality flags, and transformation version.

## 4. Product metrics and metric definitions

Each metric below has a default definition. A real product must confirm whether it fits the business question and publish it in the semantic layer with a stable metric name, owner, version, active-event definition, grain, population, numerator, denominator, window boundaries, time zone, identity/bot policy, freshness SLA, and historical-restatement policy.

### 4.1 DAU, WAU, and MAU

**Question:** How many distinct users were active during a given time window?

- **DAU:** distinct users with at least one qualifying activity on a reporting date.
- **WAU:** distinct users with at least one qualifying activity in the trailing seven calendar dates, or a defined calendar week. These are not interchangeable.
- **MAU:** distinct users with at least one qualifying activity in the trailing 30 calendar dates, or a defined calendar month. Again, choose one convention.

| Metric | Grain of source | Numerator / aggregation | Denominator | Window |
|---|---|---|---|---|
| DAU | user-day | distinct active users | none | one reporting date |
| WAU | user-day | distinct users | none | declared 7-day or calendar-week window |
| MAU | user-day | distinct users | none | declared trailing-30-day or calendar-month window |

```sql
-- DuckDB fixture example: a date spine ensures zero-activity dates are emitted.
-- In production, prefer the governed calendar/date dimension.
WITH calendar AS (
  SELECT CAST(d AS DATE) AS report_date
  FROM generate_series(DATE '2025-01-01', DATE '2025-01-10', INTERVAL 1 DAY) AS t(d)
), active_days AS (
  SELECT DISTINCT user_id, CAST(event_ts_utc AS DATE) AS activity_date
  FROM canonical_events
  WHERE event_name = 'meaningful_activity' AND is_bot = FALSE
)
SELECT c.report_date, COUNT(DISTINCT a.user_id) AS dau
FROM calendar c LEFT JOIN active_days a ON a.activity_date = c.report_date
GROUP BY c.report_date
ORDER BY c.report_date;

-- Trailing 30 calendar dates including report_date; the date spine includes zero-active days.
WITH calendar AS (
  SELECT CAST(d AS DATE) AS report_date
  FROM generate_series(DATE '2025-01-01', DATE '2025-01-10', INTERVAL 1 DAY) AS t(d)
), active_days AS (
  SELECT DISTINCT user_id, CAST(event_ts_utc AS DATE) AS activity_date
  FROM canonical_events
  WHERE event_name = 'meaningful_activity' AND is_bot = FALSE
)
SELECT d.report_date,
       COUNT(DISTINCT a.user_id) AS mau_trailing_30d
FROM calendar d LEFT JOIN active_days a
  ON a.activity_date BETWEEN d.report_date - INTERVAL 29 DAY AND d.report_date
GROUP BY d.report_date
ORDER BY d.report_date;
```

A trailing-seven-calendar-date **WAU** (including the report date) uses the same distinct-user-day source: 

```sql
WITH calendar AS (
  SELECT CAST(d AS DATE) AS report_date
  FROM generate_series(DATE '2025-01-01', DATE '2025-01-10', INTERVAL 1 DAY) AS t(d)
), active_days AS (
  SELECT DISTINCT user_id, CAST(event_ts_utc AS DATE) AS activity_date
  FROM canonical_events
  WHERE event_name = 'meaningful_activity' AND is_bot = FALSE
)
SELECT d.report_date, COUNT(DISTINCT a.user_id) AS wau_trailing_7d
FROM calendar d LEFT JOIN active_days a
  ON a.activity_date BETWEEN d.report_date - INTERVAL 6 DAY AND d.report_date
GROUP BY d.report_date
ORDER BY d.report_date;
```

This is a trailing seven-calendar-date metric, not a calendar-week metric. All examples assume `is_bot` has already been normalised to non-null in the canonical layer.

**Hand check:** if three users have qualifying events on one date and one user has five events, DAU is three, not seven. Distinct counting must occur at user grain.

**Misleading when:** event instrumentation changes, bots are included, identity stitching changes, or the active event is a low-value heartbeat.  
**Scale:** materialise distinct user-day rows; use partition pruning and incremental recomputation. Approximate distinct sketches can help with exploratory high-cardinality rollups, but do not replace exact user-level facts when auditability or exact deduplication is required.

### 4.2 Activation

**Question:** Did a new user reach the product's first meaningful value milestone?

A common definition is:


definition: `activated within 7 days = user completes activation event between signup timestamp and signup timestamp + 7 days`.

- **Grain:** one eligible signup user.
- **Numerator:** users who satisfy the activation event and window.
- **Denominator:** eligible new users in the signup cohort, excluding invalid/test accounts under a documented rule.
- **Window:** seven elapsed 24-hour days in this example, not “until the end of the seventh local date.”

```sql
WITH first_activation AS (
  SELECT user_id, MIN(event_ts_utc) AS activation_ts_utc
  FROM canonical_events
  WHERE event_name = 'activation_completed' AND is_bot = FALSE
  GROUP BY user_id
), eligible AS (
  SELECT u.user_id, u.signup_ts_utc, a.activation_ts_utc
  FROM dim_users u
  LEFT JOIN first_activation a USING (user_id)
)
SELECT
  COUNT(*) FILTER (
    WHERE activation_ts_utc >= signup_ts_utc
      AND activation_ts_utc < signup_ts_utc + INTERVAL 7 DAY
  ) AS activated_users,
  COUNT(*) AS eligible_users,
  COUNT(*) FILTER (
    WHERE activation_ts_utc >= signup_ts_utc
      AND activation_ts_utc < signup_ts_utc + INTERVAL 7 DAY
  )::DOUBLE / NULLIF(COUNT(*), 0) AS activation_rate
FROM eligible;
```

The lab's compact dataset does not include `activation_completed`, so this query is a template, not an expected-result query for that fixture. If activation is composed of multiple actions, model the sequence and window explicitly.

**Misleading when:** the event means something different across platforms, users have not had the full seven-day observation window, or the denominator includes invited users who never had an opportunity to sign up.

### 4.3 Conversion rate and funnel drop-off

**Question:** What fraction of a defined eligible population completes an action?

- **Grain:** usually one user or one session per funnel entry.
- **Numerator:** eligible units that complete the target step within the defined ordering/window.
- **Denominator:** units that entered the funnel, or units reaching the previous step for step-to-step conversion.
- **Window:** explicitly defined, e.g. seven days after the first qualifying visit.

`overall_conversion = users_at_purchase / users_at_visit`  
`step_conversion_i = users_at_step_i / users_at_step_(i-1)`  
`drop_off_i = 1 - step_conversion_i`.

Never divide purchase events by visit events and call it user conversion unless event-level conversion is explicitly intended. Repeated events can make event-level rates exceed 100%.

### 4.4 Churn

“Churn” has several valid definitions; publish one.

- **Period activity churn:** users active in period A but not active in immediately following period B, divided by users active in A.
- **Subscription churn:** subscriptions cancelled or expired in the period divided by the defined subscription base; use a subscription-grain model.
- **Survival churn:** time-to-event analysis of time until churn, accounting for users whose observation period ends before churn is observed.

For active-user churn, define period boundaries and active event first. A user absent from a short window is not necessarily permanently churned. Period churn is a discrete operational metric, not a substitute for survival analysis.

### 4.5 ARPU, LTV, revenue cohorts, and payback

- **ARPU for period P:** net recognised revenue in P / eligible users in the declared population for P. If the denominator is only users active in P, label it ARP(A)U rather than general ARPU.
- **Cumulative cohort revenue per acquired user:** total net revenue generated by cohort members through cohort age k / original eligible cohort size. State whether refunds, taxes, discounts, and currency conversion are included.
- **LTV:** expected discounted future contribution margin or revenue per acquired customer over a stated horizon. Revenue LTV and contribution-margin LTV are different.
- **Payback period:** earliest age at which cumulative contribution margin per acquired customer equals or exceeds acquisition cost, with cash-flow and discounting conventions stated.

A simple historical estimate is `cohort cumulative contribution margin / original acquired users`. Extrapolating lifetime value from early behaviour requires a model and assumptions; early cohorts may not represent mature cohorts, and retention/revenue curves can change. A discounted formulation is:

\[
LTV_H = \sum_{t=1}^{H} \frac{E[\text{contribution margin}_t]}{(1+r)^t}
\]

where `r` is the period-matched discount rate and `H` is the horizon. Use consistent time units and distinguish gross revenue from margin.

### 4.6 Stickiness

Common ratios include `DAU / MAU` and `DAU / WAU`. These approximate how frequently a monthly or weekly active population engages; they are not universal measures of product quality. Numerator and denominator should refer to compatible windows and definitions. Daily active users divided by a trailing-30-day active population on the same report date is a common DAU/MAU convention.

## 5. Cohort analysis fundamentals

A cohort groups entities by a shared starting point or attribute.

Examples:

- **Signup cohort:** week of first successful signup.
- **First-purchase cohort:** week of first completed purchase.
- **Acquisition cohort:** acquisition channel or campaign at acquisition time.
- **Feature cohort:** first use of a feature, if the analysis question is adoption after feature discovery.

Cohort definition and cohort age are separate dimensions. A signup-week cohort's age 1 is the first week after its cohort week in a weekly triangle; for daily cohorts, age 1 can mean the day after signup date. Never mix these definitions in one chart.

### 5.1 Weekly signup cohorts

```sql
WITH first_signup AS (
  SELECT user_id, MIN(signup_ts_utc) AS signup_ts_utc
  FROM canonical_events
  WHERE event_name = 'signup' AND is_bot = FALSE
  GROUP BY user_id
)
SELECT user_id,
       DATE_TRUNC('week', CAST(signup_ts_utc AS DATE))::DATE AS signup_cohort_week
FROM first_signup;
```

DuckDB's `DATE_TRUNC('week', ...)` returns the beginning of the ISO-style week for this date/time. Check your warehouse's week-start and week-number conventions. If `dim_users` is the trusted signup source, use it instead of re-deriving signup from events. The `first_signup` CTE illustrates the first-event pattern.

**Hand check:** with Monday as the week start, signup dates Wednesday 1 Jan and Thursday 2 Jan belong to the same week; Wednesday 8 Jan belongs to the next cohort week.

### 5.2 First event and cohort membership

Use `MIN(event_ts)` or `ROW_NUMBER()` to find the first qualifying event. Make sure the event is the correct business event, exclude invalid records consistently, and define what happens if events arrive late. Cohort membership should be stable once the source-of-truth event is accepted, but a late earlier event can require restating cohort membership under a documented correction policy.

For slowly changing attributes, segment by the value at cohort entry or use a time-valid dimension join. Joining a cohort to the user's latest plan can rewrite history and create survivorship or look-ahead bias.

## 6. Retention metrics and cohort tables

### 6.1 Define activity and the retention denominator

This lesson's baseline is **meaningful-event retention**: a user is active on a date if at least one non-bot `meaningful_activity` event occurs on that reporting date. Signup is not automatically active.

For a signup-date cohort:

- **Cohort size:** all eligible users whose signup date is the cohort date.
- **D1 retention:** cohort users active on signup date + 1 calendar day / cohort size, once the cohort has a complete D1 observation day.
- **D7 retention:** cohort users active on signup date + 7 calendar days / cohort size, once D7 is mature.
- **D30 retention:** same for signup date + 30 days.

For D1/D7/D30, the denominator is the original cohort, not just users active on the previous day. If the question is “of users active on day 6, how many are active on day 7?”, that is a different conditional transition metric.

Use a reporting `as_of_date` and mark a cohort-age cell as immature if the entire target date is not observed. For a UTC calendar-date policy, D7 is mature only when `signup_date + 7 days <= last_complete_activity_date`. If a business date is incomplete because ingestion is behind, use the last fully processed date, not wall-clock `CURRENT_DATE`.

### 6.2 Build one row per user per active day

```sql
CREATE OR REPLACE TABLE user_daily_activity AS
SELECT DISTINCT
       user_id,
       CAST(event_ts_utc AS DATE) AS activity_date,
       'meaningful_v1' AS activity_definition_version
FROM canonical_events
WHERE event_name = 'meaningful_activity'
  AND is_bot = FALSE
  AND user_id IS NOT NULL;
```

This is a compact full rebuild. A production implementation should partition by `activity_date`, carry data lineage/refresh timestamps, and rebuild dates affected by late events. The version column is intentional: if “active” changes, don't silently mix definitions in the same table.

### 6.3 Daily retention query

Assume `dim_users` contains the authoritative signup timestamp and the reporting date is UTC.

```sql
WITH cohort_users AS (
  SELECT user_id, CAST(signup_ts_utc AS DATE) AS cohort_date
  FROM dim_users
), cohort_sizes AS (
  SELECT cohort_date, COUNT(*) AS cohort_size
  FROM cohort_users
  GROUP BY cohort_date
), retention_counts AS (
  SELECT
    c.cohort_date,
    DATE_DIFF('day', c.cohort_date, a.activity_date) AS cohort_age_day,
    COUNT(DISTINCT c.user_id) AS retained_users
  FROM cohort_users c
  JOIN user_daily_activity a USING (user_id)
  WHERE a.activity_definition_version = 'meaningful_v1'
    AND a.activity_date >= c.cohort_date
    AND DATE_DIFF('day', c.cohort_date, a.activity_date) IN (0, 1, 7, 30)
  GROUP BY 1, 2
), complete AS (
  SELECT DATE '2025-01-10' AS last_complete_activity_date
)
SELECT
  s.cohort_date,
  s.cohort_size,
  r.cohort_age_day,
  r.retained_users,
  r.retained_users::DOUBLE / NULLIF(s.cohort_size, 0) AS retention_rate,
  (s.cohort_date + r.cohort_age_day * INTERVAL 1 DAY) <= x.last_complete_activity_date AS is_mature
FROM cohort_sizes s
JOIN retention_counts r USING (cohort_date)
CROSS JOIN complete x
ORDER BY s.cohort_date, r.cohort_age_day;
```

This query returns only cohort-age cells with at least one retained user, so a zero-retention cell would be absent. For a complete heatmap, generate all required ages with a calendar/age scaffold and left join counts, coalescing missing counts to zero **only when the cell is mature**. An immature cell is `NULL`/blank, not zero.

A robust heatmap-ready query:

```sql
WITH cohort_users AS (
  SELECT user_id, CAST(signup_ts_utc AS DATE) AS cohort_date FROM dim_users
), cohort_sizes AS (
  SELECT cohort_date, COUNT(*) AS cohort_size FROM cohort_users GROUP BY 1
), ages AS (
  SELECT * FROM (VALUES (0), (1), (7), (30)) AS v(cohort_age_day)
), last_complete AS (
  SELECT DATE '2025-01-10' AS last_complete_activity_date
), grid AS (
  SELECT s.cohort_date, s.cohort_size, a.cohort_age_day,
         s.cohort_date + a.cohort_age_day * INTERVAL 1 DAY AS target_date,
         l.last_complete_activity_date
  FROM cohort_sizes s CROSS JOIN ages a CROSS JOIN last_complete l
), counts AS (
  SELECT c.cohort_date,
         DATE_DIFF('day', c.cohort_date, a.activity_date) AS cohort_age_day,
         COUNT(DISTINCT c.user_id) AS retained_users
  FROM cohort_users c JOIN user_daily_activity a USING (user_id)
  WHERE a.activity_definition_version = 'meaningful_v1'
  GROUP BY 1, 2
)
SELECT g.cohort_date, g.cohort_age_day, g.cohort_size,
       CASE WHEN g.target_date <= g.last_complete_activity_date
            THEN COALESCE(c.retained_users, 0) ELSE NULL END AS retained_users,
       CASE WHEN g.target_date <= g.last_complete_activity_date
            THEN COALESCE(c.retained_users, 0)::DOUBLE / NULLIF(g.cohort_size, 0)
            ELSE NULL END AS retention_rate,
       g.target_date <= g.last_complete_activity_date AS is_mature
FROM grid g LEFT JOIN counts c
  ON c.cohort_date = g.cohort_date AND c.cohort_age_day = g.cohort_age_day
ORDER BY g.cohort_date, g.cohort_age_day;
```

`DATE_DIFF('day', start, end)` is DuckDB syntax. Confirm argument order in other engines. Here, cohort age is non-negative because activity before signup is excluded by data quality/cohort rules; the query should still explicitly filter pre-cohort activity when using a generic activity source.

### 6.3.1 Weekly signup cohorts with user-relative D1/D7/D30

When cohorts are grouped by **signup week**, users in the same cohort have different signup dates. Therefore, D1/D7/D30 activity must be compared with each user's own signup date, then aggregated to the signup-week cohort. Cohort maturity must use the latest signup date in that week so the entire denominator has the complete target window.

```sql
WITH cohort_users AS (
  SELECT user_id,
         CAST(signup_ts_utc AS DATE) AS signup_date,
         DATE_TRUNC('week', CAST(signup_ts_utc AS DATE))::DATE AS signup_cohort_week
  FROM dim_users
), cohort_sizes AS (
  SELECT signup_cohort_week,
         COUNT(*) AS cohort_size,
         MAX(signup_date) AS latest_signup_date
  FROM cohort_users
  GROUP BY 1
), ages AS (
  SELECT * FROM (VALUES (1), (7), (30)) AS a(cohort_age_day)
), counts AS (
  SELECT c.signup_cohort_week,
         DATE_DIFF('day', c.signup_date, a.activity_date) AS cohort_age_day,
         COUNT(DISTINCT c.user_id) AS retained_users
  FROM cohort_users c
  JOIN user_daily_activity a USING (user_id)
  WHERE a.activity_definition_version = 'meaningful_v1'
    AND a.activity_date IN (
      c.signup_date + INTERVAL 1 DAY,
      c.signup_date + INTERVAL 7 DAY,
      c.signup_date + INTERVAL 30 DAY
    )
  GROUP BY 1, 2
), last_complete AS (
  SELECT DATE '2025-01-10' AS last_complete_activity_date
)
SELECT s.signup_cohort_week, a.cohort_age_day, s.cohort_size,
       CASE WHEN s.latest_signup_date + a.cohort_age_day * INTERVAL 1 DAY
                       <= l.last_complete_activity_date
            THEN COALESCE(c.retained_users, 0) ELSE NULL END AS retained_users,
       CASE WHEN s.latest_signup_date + a.cohort_age_day * INTERVAL 1 DAY
                       <= l.last_complete_activity_date
            THEN COALESCE(c.retained_users, 0)::DOUBLE / NULLIF(s.cohort_size, 0)
            ELSE NULL END AS retention_rate,
       s.latest_signup_date + a.cohort_age_day * INTERVAL 1 DAY
         <= l.last_complete_activity_date AS is_mature
FROM cohort_sizes s
CROSS JOIN ages a
CROSS JOIN last_complete l
LEFT JOIN counts c
  ON c.signup_cohort_week = s.signup_cohort_week
 AND c.cohort_age_day = a.cohort_age_day
ORDER BY 1, 2;
```

This query has a fixed original signup-week denominator and reports a cell only after every user's target date is complete. A less conservative approach can use only users individually eligible for that age, but then the denominator changes with age and must be labelled as an eligible-user denominator; do not compare it silently with full-cohort retention.

For a **weekly cohort triangle** where age 0 is the signup calendar week and age 1 is the next calendar week, use `activity_week = DATE_TRUNC('week', activity_date)` and calculate `DATE_DIFF('week', signup_cohort_week, activity_week)`. Define whether a user is active in the signup week even if signup occurs late in that week. This weekly-calendar definition is distinct from user-relative D1/D7/D30.

### 6.4 Retention variants: bounded, unbounded, and rolling

These names are used inconsistently across vendors. Publish your exact semantics.

- **Bounded / exact-day retention:** active on exactly cohort age N. D7 means activity on day 7, not day 7 or later.
- **Unbounded / on-or-after retention:** active on day N or any later observed day within the declared observation horizon. A user active on day 14 counts for D7 unbounded retention.
- **Rolling retention:** in this lesson, a user is retained at age N if they have at least one qualifying active day in a rolling interval ending at age N (for example, days N−6 through N for a seven-day rolling window). The SQL example below uses days 1–7 for age 7. Some products call “return on or after N” rolling retention; avoid relying on the name alone.

Example SQL for exact-day versus on-or-after retention:

```sql
-- Exact-day retention for a given cohort age N.
WITH cohort_users AS (
  SELECT user_id, CAST(signup_ts_utc AS DATE) AS cohort_date FROM dim_users
)
SELECT c.cohort_date,
       COUNT(DISTINCT CASE WHEN a.activity_date = c.cohort_date + INTERVAL 7 DAY
                           THEN c.user_id END) AS exact_d7_users
FROM cohort_users c
LEFT JOIN user_daily_activity a
  ON a.user_id = c.user_id
 AND a.activity_definition_version = 'meaningful_v1'
GROUP BY c.cohort_date;

-- On-or-after D7 within the observed horizon.
WITH cohort_users AS (
  SELECT user_id, CAST(signup_ts_utc AS DATE) AS cohort_date FROM dim_users
)
SELECT c.cohort_date,
       COUNT(DISTINCT CASE WHEN a.activity_date >= c.cohort_date + INTERVAL 7 DAY
                           THEN c.user_id END) AS on_or_after_d7_users
FROM cohort_users c
LEFT JOIN user_daily_activity a
  ON a.user_id = c.user_id
 AND a.activity_date >= c.cohort_date + INTERVAL 7 DAY
 AND a.activity_date <= DATE '2025-01-10'
GROUP BY c.cohort_date;
```

Both queries should be paired with maturity checks and the original cohort denominator. For rolling 7-day retention at age N, join activity between `cohort_date + (N-6) days` and `cohort_date + N days` inclusive, then count distinct users. Decide whether age zero is signup day or the first full day after signup. A concrete rolling example for age 7 (activity on cohort ages 1 through 7) is:

```sql
WITH cohort_users AS (
  SELECT user_id, CAST(signup_ts_utc AS DATE) AS cohort_date FROM dim_users
)
SELECT c.cohort_date,
       COUNT(DISTINCT CASE WHEN a.activity_date BETWEEN c.cohort_date + INTERVAL 1 DAY
                                                   AND c.cohort_date + INTERVAL 7 DAY
                           THEN c.user_id END) AS rolling_7d_users
FROM cohort_users c
LEFT JOIN user_daily_activity a
  ON a.user_id = c.user_id
 AND a.activity_definition_version = 'meaningful_v1'
 AND a.activity_date BETWEEN c.cohort_date + INTERVAL 1 DAY
                          AND c.cohort_date + INTERVAL 7 DAY
GROUP BY c.cohort_date;
```

Divide by the original cohort size and publish the result only when the full target window is observed. This example's age-7 window is explicitly days 1–7; a different product may choose a window ending at day 7 with a different start, so name the exact window.

### 6.5 Cohort triangle interpretation

A retention triangle has cohorts in rows and cohort ages in columns. For example:

| Signup cohort | Age 0 | Age 1 | Age 7 | Age 30 |
|---|---:|---:|---:|---:|
| Jan 1 | 80% | 35% | 20% | 12% |
| Jan 8 | 82% | 38% | 22% | *immature* |
| Jan 15 | 78% | 34% | *immature* | *immature* |

These are illustrative values, not computed lab results. Blank/immature cells mean insufficient observation, not zero retention. A fair comparison uses the same cohort-age column or an appropriate survival method. Don't compare a new cohort's D7 with an old cohort's D30 and infer a trend.

### 6.6 Small hand-worked validation

Suppose a cohort contains four users: A, B, C, D. On D1, A and B are active. On D7, only B is active. On D30, none are active and the D30 period is complete.

- Cohort size = 4.
- D1 exact retention = 2 / 4 = 50%.
- D7 exact retention = 1 / 4 = 25%.
- D30 exact retention = 0 / 4 = 0%.

If D30 is not yet observed, report `NULL`/immature instead of 0%. If D7 is defined as on-or-after, users active on D7 or any later observed day count; the result cannot be lower than exact D7 for the same complete observation horizon.

## 7. Funnel analysis and conversion windows

### 7.1 Four-step funnel definition

The lab funnel is:

1. `visit`
2. `signup`
3. `add_to_cart`
4. `purchase`

The primary analysis unit is **user**. The entry is each user's first eligible `visit` inside the declared analysis-entry window; a user can contribute once to this user-level run. The conversion window is seven elapsed days after that visit: `[entry_ts, entry_ts + 7 days)`. The example fixture uses Jan 1–10, 2025 as its entry window; change both bounds together for another reporting run. Each step must occur after the prior step for the strict-order version. A separate session-level funnel starts from a session entry and counts sessions, not users.

This distinction matters because a user may visit several times, create several sessions, and purchase more than once. Never combine user-level denominators with session-level numerators.

### 7.2 Strict-order and loose-order semantics

For this lesson:

- **Strict-order funnel:** all four steps must occur in order with strictly increasing event timestamps; unrelated events may occur between funnel steps. The SQL below deliberately requires `next_step_ts > prior_step_ts`, so equal timestamps do not qualify even if `event_id` provides deterministic sorting. Use the event ID to make row ordering reproducible, not to imply temporal order where timestamps are tied. If ties should count, define and validate an explicit source sequence number as part of the event contract.
- **Loose-order funnel:** all four required events occur within the conversion window, but the event timestamps need not be in the prescribed order. This is useful as a diagnostic, not necessarily a meaningful causal journey.

Some analytics tools use “strict” to mean no intervening events. If your business requires **consecutive-step strictness**, add a rule that no disallowed event can occur between steps. Document the exact meaning in the metric name.

### 7.3 User-level strict funnel with first eligible event per step

```sql
WITH visits AS (
  SELECT user_id, MIN(event_ts_utc) AS entry_ts
  FROM canonical_events
  WHERE event_name = 'visit' AND is_bot = FALSE
    AND event_ts_utc >= TIMESTAMP '2025-01-01 00:00:00'
    AND event_ts_utc <  TIMESTAMP '2025-01-11 00:00:00'
  GROUP BY user_id
), step1 AS (
  SELECT v.user_id, v.entry_ts,
         MIN(e.event_ts_utc) AS signup_ts
  FROM visits v LEFT JOIN canonical_events e
    ON e.user_id = v.user_id AND e.event_name = 'signup' AND e.is_bot = FALSE
   AND e.event_ts_utc >= v.entry_ts
   AND e.event_ts_utc < v.entry_ts + INTERVAL 7 DAY
  GROUP BY v.user_id, v.entry_ts
), step2 AS (
  SELECT s1.*,
         MIN(e.event_ts_utc) AS cart_ts
  FROM step1 s1 LEFT JOIN canonical_events e
    ON e.user_id = s1.user_id AND e.event_name = 'add_to_cart' AND e.is_bot = FALSE
   AND s1.signup_ts IS NOT NULL
   AND e.event_ts_utc > s1.signup_ts
   AND e.event_ts_utc < s1.entry_ts + INTERVAL 7 DAY
  GROUP BY s1.user_id, s1.entry_ts, s1.signup_ts
), step3 AS (
  SELECT s2.*,
         MIN(e.event_ts_utc) AS purchase_ts
  FROM step2 s2 LEFT JOIN canonical_events e
    ON e.user_id = s2.user_id AND e.event_name = 'purchase' AND e.is_bot = FALSE
   AND s2.cart_ts IS NOT NULL
   AND e.event_ts_utc > s2.cart_ts
   AND e.event_ts_utc < s2.entry_ts + INTERVAL 7 DAY
  GROUP BY s2.user_id, s2.entry_ts, s2.signup_ts, s2.cart_ts
)
SELECT
  COUNT(*) AS visit_users,
  COUNT(signup_ts) AS signup_users,
  COUNT(cart_ts) AS cart_users,
  COUNT(purchase_ts) AS purchase_users,
  COUNT(signup_ts)::DOUBLE / NULLIF(COUNT(*), 0) AS visit_to_signup,
  COUNT(cart_ts)::DOUBLE / NULLIF(COUNT(signup_ts), 0) AS signup_to_cart,
  COUNT(purchase_ts)::DOUBLE / NULLIF(COUNT(cart_ts), 0) AS cart_to_purchase,
  COUNT(purchase_ts)::DOUBLE / NULLIF(COUNT(*), 0) AS visit_to_purchase
FROM step3;
```

**Important limitation:** this template uses `MIN(signup_ts)` in the seven-day window, then the earliest cart after it, then earliest purchase after that. It treats a prior signup before the entry visit as ineligible. If users can enter at a visit before signup, ensure `signup` truly represents the desired step and is not the signup event that created the user identity. For a marketing funnel that includes anonymous visits followed by signup, resolve anonymous identity to the new user before running the query.

### 7.4 Loose-order funnel

```sql
WITH visits AS (
  SELECT user_id, MIN(event_ts_utc) AS entry_ts
  FROM canonical_events
  WHERE event_name = 'visit' AND is_bot = FALSE
    AND event_ts_utc >= TIMESTAMP '2025-01-01 00:00:00'
    AND event_ts_utc <  TIMESTAMP '2025-01-11 00:00:00'
  GROUP BY user_id
), flags AS (
  SELECT v.user_id, v.entry_ts,
    MAX(CASE WHEN e.event_name = 'signup' THEN 1 ELSE 0 END) AS did_signup,
    MAX(CASE WHEN e.event_name = 'add_to_cart' THEN 1 ELSE 0 END) AS did_cart,
    MAX(CASE WHEN e.event_name = 'purchase' THEN 1 ELSE 0 END) AS did_purchase
  FROM visits v LEFT JOIN canonical_events e
    ON e.user_id = v.user_id AND e.is_bot = FALSE
   AND e.event_ts_utc >= v.entry_ts
   AND e.event_ts_utc < v.entry_ts + INTERVAL 7 DAY
   AND e.event_name IN ('signup','add_to_cart','purchase')
  GROUP BY v.user_id, v.entry_ts
)
SELECT COUNT(*) AS visit_users,
       SUM(did_signup) AS signup_users,
       SUM(did_cart) AS cart_users,
       SUM(did_purchase) AS purchase_users
FROM flags;
```

This loose query does **not** require events to occur in order. It is a diagnostic of “all these actions occurred within the window,” not a sequential conversion funnel. Because events may predate signup logically or occur in a nonsensical order, inspect differences against strict order before interpreting the result.

### 7.5 Step-to-step conversion and time to convert

Use the previous step's reached population as denominator for step-to-step conversion. For overall conversion, use funnel entrants. Time to convert can mean entry-to-purchase, visit-to-signup, or time between consecutive steps; name the interval explicitly.

```sql
-- Given a user-level funnel summary with entry_ts and purchase_ts:
SELECT
  MEDIAN(EPOCH(purchase_ts - entry_ts)) AS median_seconds_to_purchase,
  AVG(EPOCH(purchase_ts - entry_ts)) AS mean_seconds_to_purchase
FROM funnel_user_summary
WHERE purchase_ts IS NOT NULL;
```

The `funnel_user_summary` should contain one row per funnel entry/analysis unit. `EPOCH(interval)` expresses elapsed seconds in DuckDB; adapt the interval-to-seconds expression for other dialects. If a user can re-enter, use a stable `funnel_entry_id` and state whether the unit is user or entry. Do not accidentally deduplicate distinct session entries by user ID.

### 7.6 Per-session versus per-user funnels

- **Per-user:** one entry per user, typically first qualifying visit in the analysis period. Measures user journey conversion.
- **Per-session:** one entry per session, typically the first event in that session. Measures session journey conversion. A user can contribute multiple sessions.
- **Per-entry:** each qualifying entry event starts a funnel. This can over-weight highly active users unless intentional.

The output grain and denominator must match. Session funnels require a trustworthy `session_id` or a documented sessionisation rule. Here is a same-session sequential funnel; it counts each session's first eligible visit once. The `session_id` itself bounds the journey, so this query does not add a separate seven-day window.

```sql
WITH session_visits AS (
  SELECT session_id, user_id, MIN(event_ts_utc) AS entry_ts
  FROM canonical_events
  WHERE event_name = 'visit' AND is_bot = FALSE
    AND session_id IS NOT NULL
    AND event_ts_utc >= TIMESTAMP '2025-01-01 00:00:00'
    AND event_ts_utc <  TIMESTAMP '2025-01-11 00:00:00'
  GROUP BY session_id, user_id
), signup_step AS (
  SELECT v.session_id, v.user_id, v.entry_ts, MIN(e.event_ts_utc) AS signup_ts
  FROM session_visits v LEFT JOIN canonical_events e
    ON e.session_id = v.session_id AND e.user_id = v.user_id
   AND e.event_name = 'signup' AND e.is_bot = FALSE
   AND e.event_ts_utc > v.entry_ts
  GROUP BY v.session_id, v.user_id, v.entry_ts
), cart_step AS (
  SELECT s.*, MIN(e.event_ts_utc) AS cart_ts
  FROM signup_step s LEFT JOIN canonical_events e
    ON e.session_id = s.session_id AND e.user_id = s.user_id
   AND e.event_name = 'add_to_cart' AND e.is_bot = FALSE
   AND s.signup_ts IS NOT NULL AND e.event_ts_utc > s.signup_ts
  GROUP BY s.session_id, s.user_id, s.entry_ts, s.signup_ts
), purchase_step AS (
  SELECT c.*, MIN(e.event_ts_utc) AS purchase_ts
  FROM cart_step c LEFT JOIN canonical_events e
    ON e.session_id = c.session_id AND e.user_id = c.user_id
   AND e.event_name = 'purchase' AND e.is_bot = FALSE
   AND c.cart_ts IS NOT NULL AND e.event_ts_utc > c.cart_ts
  GROUP BY c.session_id, c.user_id, c.entry_ts, c.signup_ts, c.cart_ts
)
SELECT COUNT(*) AS visit_sessions,
       COUNT(signup_ts) AS signup_sessions,
       COUNT(cart_ts) AS cart_sessions,
       COUNT(purchase_ts) AS purchase_sessions
FROM purchase_step;
```

This query requires each step to share both the session ID and canonical user ID; the session ID defines the boundary. The compact fixture in Section 3 omits `session_id`, so extend that fixture or use a canonical event table with populated session IDs before running this query. Do not compare its session denominator to a user-level funnel denominator as if they were interchangeable.

## 8. SQL implementation patterns

### 8.1 First event with a window function

```sql
WITH ranked AS (
  SELECT user_id, event_ts_utc, event_id,
         ROW_NUMBER() OVER (
           PARTITION BY user_id
           ORDER BY event_ts_utc, event_id
         ) AS rn
  FROM canonical_events
  WHERE event_name = 'purchase' AND is_bot = FALSE
)
SELECT user_id, event_ts_utc AS first_purchase_ts
FROM ranked
WHERE rn = 1;
```

`MIN(timestamp)` is concise when only the timestamp is needed. `ROW_NUMBER()` is useful when you also need event properties and have a deterministic tie-breaker.

### 8.2 `LEAD` and `LAG` for sequence analysis

```sql
WITH ordered AS (
  SELECT user_id, event_ts_utc, event_name, event_id,
         LAG(event_name) OVER (
           PARTITION BY user_id ORDER BY event_ts_utc, event_id
         ) AS previous_event,
         LEAD(event_name) OVER (
           PARTITION BY user_id ORDER BY event_ts_utc, event_id
         ) AS next_event,
         LEAD(event_ts_utc) OVER (
           PARTITION BY user_id ORDER BY event_ts_utc, event_id
         ) AS next_event_ts
  FROM canonical_events
  WHERE is_bot = FALSE
)
SELECT * FROM ordered
WHERE event_name = 'visit';
```

This finds adjacent events in the ordered event stream. It is not a complete funnel query by itself: repeated events, unrelated intervening events, conversion windows, and entry semantics still need explicit logic.

### 8.3 `DATE_TRUNC` and cohort-age arithmetic

Use `DATE_TRUNC('week', date)` to create weekly cohorts. For daily retention, calculate `DATE_DIFF('day', cohort_date, activity_date)`; for weekly retention, calculate age in week boundaries using the same week-start convention. Avoid approximating a calendar month as 30 days if the question is calendar-month retention.

### 8.4 Avoiding one-to-many join multiplication

Bad pattern:

```sql
-- Dangerous: users with many events multiply in the joined rows.
SELECT COUNT(*) FROM dim_users u
JOIN canonical_events e USING (user_id);
```

Safer pattern when counting users with an event:

```sql
SELECT COUNT(DISTINCT u.user_id)
FROM dim_users u
WHERE EXISTS (
  SELECT 1 FROM canonical_events e
  WHERE e.user_id = u.user_id
    AND e.event_name = 'purchase'
    AND e.is_bot = FALSE
);
```

For revenue, aggregate event/order data to the correct user-period grain before joining it to users or cohorts. Do not sum the same revenue after joining it to daily activity rows.

## 9. Sessionisation and segmentation

### 9.1 Sessionisation

A common rule starts a new session when the gap since the prior event exceeds 30 minutes, but the threshold is a product decision. Some apps use inactivity, explicit session IDs, app background/foreground, or a hybrid rule. Bot events and system heartbeats should not silently keep a session alive.

```sql
WITH ordered AS (
  SELECT user_id, event_id, event_ts_utc, event_name,
         LAG(event_ts_utc) OVER (
           PARTITION BY user_id ORDER BY event_ts_utc, event_id
         ) AS previous_ts
  FROM canonical_events
  WHERE is_bot = FALSE AND user_id IS NOT NULL
), boundaries AS (
  SELECT *, CASE
    WHEN previous_ts IS NULL
      OR event_ts_utc > previous_ts + INTERVAL 30 MINUTE
    THEN 1 ELSE 0 END AS new_session
  FROM ordered
), numbered AS (
  SELECT *, SUM(new_session) OVER (
    PARTITION BY user_id ORDER BY event_ts_utc, event_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS session_number
  FROM boundaries
)
SELECT user_id, session_number,
       MIN(event_ts_utc) AS session_start_ts,
       MAX(event_ts_utc) AS session_end_ts,
       COUNT(*) AS event_count
FROM numbered
GROUP BY user_id, session_number;
```

This illustrative SQL assigns a session number per canonical user, not a globally unique session ID; unresolved anonymous events are excluded here and should be sessionised separately by `anonymous_id` if they are in scope. In production generate a stable key such as hash(user_id, session-start event ID, sessionisation version). If identity stitching changes, sessions can change too. Recompute sessions for affected users/dates and define how sessions crossing midnight are attributed.

### 9.2 Segmentation

Useful dimensions include acquisition channel, device, geography, plan, and new/existing status. Use the attribute value at the relevant time: signup device for acquisition analysis, current device for current activity, and time-valid plan for revenue/retention under plan membership.

- Establish a minimum segment-size rule or suppress unstable/sensitive small cells.
- Show denominators with rates.
- Avoid selecting segments after seeing the result and then presenting them as confirmatory findings.
- Consider multiple-comparison correction when scanning many segments.
- Ensure segment values are mutually exclusive when adding segment totals; users may have multiple devices/channels over time.

## 10. Advanced retention, survival, and LTV concepts

### 10.1 New, retained, resurrected, and churned users

Choose two non-overlapping activity periods, e.g. calendar months, and one active-user definition.

Let `A_prev` be users active in previous month and `A_curr` users active in current month. Let `A_ever_prev` be users with any qualifying activity before current month (including the previous month). Then:

- **New:** active this month, with no qualifying activity before this month.
- **Retained:** active in both previous and current months.
- **Resurrected:** active this month, inactive in the previous month, but active at least once before the previous month.
- **Churned:** active in previous month, inactive this month.

Under these definitions, current active users = new + retained + resurrected. Previous active users = retained + churned. Net active-user change = new + resurrected − churned. If “new” means new signup rather than first observed activity, use signup data and name the category accordingly.

```sql
-- `user_month_activity` has one row per user per calendar month with activity.
WITH months AS (
  SELECT DISTINCT activity_month FROM user_month_activity
), prev_curr AS (
  SELECT m.activity_month AS curr_month,
         m.activity_month - INTERVAL 1 MONTH AS prev_month
  FROM months m
), sets AS (
  SELECT pc.curr_month, pc.prev_month,
         curr.user_id AS curr_user_id,
         prev.user_id AS prev_user_id
  FROM prev_curr pc
  LEFT JOIN user_month_activity curr ON curr.activity_month = pc.curr_month
  LEFT JOIN user_month_activity prev ON prev.activity_month = pc.prev_month
), current_users AS (
  SELECT DISTINCT curr_month, user_id
  FROM user_month_activity
), previous_users AS (
  SELECT DISTINCT activity_month, user_id FROM user_month_activity
), first_active AS (
  SELECT user_id, MIN(activity_month) AS first_active_month
  FROM user_month_activity GROUP BY user_id
), labelled AS (
  SELECT c.activity_month,
         c.user_id,
         CASE
           WHEN f.first_active_month = c.activity_month THEN 'new'
           WHEN p.user_id IS NOT NULL THEN 'retained'
           WHEN f.first_active_month < c.activity_month - INTERVAL 1 MONTH THEN 'resurrected'
           ELSE 'other_or_incomplete_history'
         END AS movement_type
  FROM user_month_activity c
  JOIN first_active f USING (user_id)
  LEFT JOIN user_month_activity p
    ON p.user_id = c.user_id
   AND p.activity_month = c.activity_month - INTERVAL 1 MONTH
)
SELECT activity_month, movement_type, COUNT(*) AS users
FROM labelled
GROUP BY 1, 2 ORDER BY 1, 2;
```

This query labels users who first appeared in the immediately previous month and then are active again as retained, as intended. However, churned users are not in the current-user table; compute them separately as `previous_users EXCEPT current_users` or a left anti-join. A production model should also require complete month history; missing historical partitions must not be mistaken for user inactivity.

### 10.2 Survival analysis and right-censoring

Retention tables record whether users were active on selected days. Survival analysis asks how long until a defined event, such as churn, occurs.

- **Time-to-event:** time from cohort entry to churn under a documented churn definition.
- **Right-censoring:** observation ends before churn is seen, e.g. a user has not churned by the data cutoff. This is not the same as confirmed non-churn forever.
- **Kaplan–Meier estimate:** estimates the survival function while accounting for right-censored observations, under assumptions including non-informative censoring.
- **Hazard:** conditional event risk/rate at time t among entities still event-free immediately before t.

For discrete event times `t`, the Kaplan–Meier estimator is \(\hat S(t)=\prod_{t_j\le t}(1-d_j/n_j)\), where `d_j` is the number of events at `t_j` and `n_j` is the number at risk immediately before `t_j`. Right-censored users reduce later risk sets but are not counted as churn events at their censoring time. The conditional hazard estimate at an event time is `d_j / n_j`; it is not the same as `1 - S(t)` (cumulative event probability). Treat this as methodological awareness, not a claim that the SQL retention tables alone estimate survival without event/censoring records.

A simplistic “average observed lifetime among users who churned” is biased downward because it excludes censored users. Kaplan–Meier estimates can be more appropriate for time-to-churn, but censoring assumptions and delayed entry must be considered. “Inactive for 30 days” is a chosen operational churn rule, not a direct observation of permanent departure.

### 10.3 LTV and payback by cohort

A revenue cohort groups users by acquisition/signup period and accumulates revenue or contribution margin by age. Use the original cohort size as denominator when measuring revenue per acquired user; otherwise early cohort shrinkage can inflate apparent LTV.

A cohort revenue model should define:

- currency and FX conversion policy;
- gross revenue versus net revenue versus contribution margin;
- refund/chargeback treatment;
- order/payment grain and deduplication;
- cohort age and maturity;
- discount rate and time unit for discounted value;
- acquisition-cost allocation and payback definition.

Early-behaviour LTV prediction may use survival curves, parametric models, cohort curves, or machine-learning models, but should be back-tested on mature historical cohorts and calibrated across acquisition channels. Do not assume a short-term retention curve extrapolates indefinitely.

### 10.4 Seasonality, survivorship, and Simpson's paradox

- **Seasonality:** weekday, holiday, campaign, and billing-cycle patterns can change activity independently of product changes.
- **Survivorship bias:** analysing only users who remain observable or active excludes churned users and overstates retention or LTV.
- **Simpson's paradox:** aggregate retention can move opposite to every segment if the mix of channel/device/plan changes. Show both aggregate and stratified metrics, and explain population mix.
- **Cohort-size drift:** late identity merges, signup backfills, bot removal, or eligibility changes can alter historical cohort denominators. Version the cohort and record restatements.
- **Mixed time zones:** UTC event timestamps grouped by local date can shift daily activity. Pick and document the reporting clock.
- **Immature cohorts:** the newest cohorts have not had time to reach D7/D30; compare at equal age and show maturity.

## 11. Scalable data models and incremental processing

### 11.1 User-day activity model

The `user_daily_activity` model is often the central performance optimization. It reduces many events per user-day to one row. Use it for retention, DAU/WAU/MAU, and activity segmentation. It does not replace event-level facts when ordering or event properties matter.

### 11.2 Bitmaps and arrays

For high-volume workloads, activity dates can be encoded as bitmaps or arrays indexed by date. This can speed up intersection/union operations for retention and overlap analysis. Trade-offs:

- Bitmaps are efficient for set operations but require stable entity indexing and careful updates.
- Arrays can be convenient for a bounded horizon but can become large and awkward for sparse activity.
- Approximate distinct sketches can reduce memory for aggregate cardinality, but cannot answer arbitrary per-user questions and introduce estimation error.
- Exact user-day rows are easier to audit and often sufficient until profiling shows a bottleneck.

Choose based on workload, correctness tolerance, retention horizon, update pattern, and query engine—not because a technique is fashionable.

### 11.3 Incremental updates and late events

An event arriving late for Jan 3 can change the Jan 3 user-day, a session, cohort retention cells, and any aggregate built from them. Incremental processing must therefore identify the **affected dates and entities**, not only process today's partition.

A practical strategy:

1. Ingest raw events append-only with `ingested_at_utc`.
2. Deduplicate logical events by stable event key.
3. Maintain a lookback horizon for normal late arrivals, e.g. reprocess the last 7 days.
4. Route events later than the lookback to a correction queue or targeted restatement path.
5. Rebuild affected `(user_id, activity_date, definition_version)` keys deterministically.
6. Replace affected target partitions/keys transactionally; don't append blindly.
7. Recompute dependent cohort/funnel aggregates for affected users/cohort periods.
8. Record watermark, source snapshot/version, transformation version, and restatement time.

**Idempotency contract:** rerunning the same input snapshot and transformation version produces the same target rows and counts. Use stable keys and deterministic transformations. “Insert if missing” alone is insufficient if a late event changes an existing user's daily activity or session boundaries.

### 11.4 Example DuckDB incremental recomputation

The following illustrates the key-level replacement pattern. In a production orchestration system, derive `affected_dates` from newly ingested or corrected canonical events and ensure the transaction covers delete and insert.

```sql
BEGIN TRANSACTION;

-- `affected_dates` is populated by orchestration for this run.
CREATE TEMP TABLE affected_dates AS
SELECT DISTINCT CAST(event_ts_utc AS DATE) AS activity_date
FROM canonical_events
WHERE ingested_at_utc >= TIMESTAMP '2025-01-10 00:00:00'
  AND ingested_at_utc <  TIMESTAMP '2025-01-11 00:00:00';

DELETE FROM user_daily_activity
WHERE activity_date IN (SELECT activity_date FROM affected_dates)
  AND activity_definition_version = 'meaningful_v1';

INSERT INTO user_daily_activity
SELECT DISTINCT user_id,
       CAST(event_ts_utc AS DATE) AS activity_date,
       'meaningful_v1' AS activity_definition_version
FROM canonical_events
WHERE event_name = 'meaningful_activity'
  AND is_bot = FALSE
  AND user_id IS NOT NULL
  AND CAST(event_ts_utc AS DATE) IN (SELECT activity_date FROM affected_dates);

COMMIT;
```

The example assumes `ingested_at_utc` exists on `canonical_events`; it was omitted from the compact fixture for readability. If canonical events can be corrected or deleted, the affected-date set must include the old date as well as the new date. If a late event changes a session boundary, recompute all sessions for the affected user across the relevant time range, not just the event's date.

### 11.5 Full rebuild versus incremental equivalence

The core correctness test is equality of the incremental target and a full rebuild for the same canonical event snapshot and activity definition. Compare both directions using anti-joins/`EXCEPT`, not just row counts; equal counts can hide different users/dates.

```sql
CREATE OR REPLACE TEMP TABLE full_rebuild AS
SELECT DISTINCT user_id, CAST(event_ts_utc AS DATE) AS activity_date,
       'meaningful_v1' AS activity_definition_version
FROM canonical_events
WHERE event_name = 'meaningful_activity' AND is_bot = FALSE AND user_id IS NOT NULL;

-- Rows in full rebuild but not incremental target:
SELECT * FROM full_rebuild
EXCEPT
SELECT * FROM user_daily_activity WHERE activity_definition_version = 'meaningful_v1';

-- Rows in incremental target but not full rebuild:
SELECT * FROM user_daily_activity WHERE activity_definition_version = 'meaningful_v1'
EXCEPT
SELECT * FROM full_rebuild;
```

Both result sets should be empty. Run the test after injecting a late-arriving activity event and rerunning the incremental process.

## 12. Hands-on lab

This lab builds from the small fixture in Section 3. It demonstrates the model pattern; for a full production exercise, add ingestion metadata and expand the fixture to more users and dates.

### 12.1 Task A — build `user_daily_activity`

Run the full-rebuild query in Section 6.2. Validate uniqueness:

```sql
SELECT user_id, activity_date, activity_definition_version, COUNT(*) AS rows_per_key
FROM user_daily_activity
GROUP BY 1, 2, 3
HAVING COUNT(*) > 1;
```

Expected: zero rows. Validate the definition manually: `u1` is active on Jan 1, `u2` on Jan 2, `u4` on Jan 8, and `u5` on Jan 10. `u3` has no `meaningful_activity` event and is not active under this definition.

### 12.2 Task B — weekly cohorts and D1/D7/D30 retention

Use `dim_users` for cohort membership and `user_daily_activity` for activity. Use the weekly signup-cohort query in Section 6.3.1 for D1/D7/D30 and the mature-cell grid query in Section 6.3 for the daily cohort triangle. For this fixture, Jan 10 is the latest complete activity date. Most D7/D30 cells will be immature; that is expected.

Validate with a hand-worked user: `u1` signs up Jan 1 and has activity Jan 1 only, so `u1` counts for age 0 but not D1. `u2` signs up Jan 1 and is active Jan 2, so it counts for D1. A signup cohort's denominator includes all users with that signup date, even if they never generate the activity event. Hand-checking the fixture gives D1 exact retention of 1/2 for Jan 1 (only `u2` is active Jan 2), 0/1 for Jan 2, 0/1 for Jan 8, and 1/1 for Jan 9 (`u5` is active Jan 10). At the Jan 10 cutoff, D7 is mature for Jan 1 and Jan 2 cohorts (0/2 and 0/1 respectively), while Jan 8 and Jan 9 D7 cells are immature. These are hand-calculated fixture expectations, not execution results.

### 12.3 Task C — cohort triangle and heatmap-ready output

Use `cohort_date`, `cohort_age_day`, `cohort_size`, `retained_users`, `retention_rate`, and `is_mature` from the grid query. For a heatmap:

- rows = cohort date/week;
- columns = cohort age;
- cell value = retention rate;
- immature cells = null/blank;
- tooltip = numerator, denominator, cohort size, activity definition, and last complete date.

For weekly triangles, define weekly retention as active in week N relative to the cohort week, or active at least once in a seven-day interval. State which. Do not derive a weekly age using integer division of days if the reporting week starts differently from cohort week boundaries.

### 12.4 Task D — strict and loose four-step funnel

Run the queries in Section 7. The fixture has an important data-quality caveat: `u1` has a visit and later a purchase but has no `signup` event after that visit; `u2` purchases without an `add_to_cart`; `u3` visits and adds to cart without purchase; `u4` completes visit → cart → purchase but has no signup event after the visit. Thus a strict four-step funnel should not count these users as completing all four steps. This is intentional: it makes missing steps visible rather than silently treating signup attributes as signup events.

For a production marketing funnel, choose one of two coherent designs:

1. **Anonymous acquisition funnel:** resolve pre-signup anonymous events to the user identity and treat signup as an actual event in the sequence.
2. **Post-signup product funnel:** start from signup or first authenticated session and use a funnel that does not require a signup step after entry.

Don't combine these designs accidentally.

### 12.5 Task E — MAU movement decomposition

Create a monthly table with one row per user-month active under the chosen definition:

```sql
CREATE OR REPLACE TABLE user_month_activity AS
SELECT DISTINCT user_id,
       DATE_TRUNC('month', activity_date)::DATE AS activity_month
FROM user_daily_activity
WHERE activity_definition_version = 'meaningful_v1';
```

A more explicit movement query that includes churned users:

```sql
WITH months AS (
  SELECT DISTINCT activity_month FROM user_month_activity
), user_months AS (
  SELECT user_id, activity_month FROM user_month_activity
), first_active AS (
  SELECT user_id, MIN(activity_month) AS first_active_month
  FROM user_months GROUP BY user_id
), curr AS (
  SELECT activity_month, user_id FROM user_months
), curr_labels AS (
  SELECT c.activity_month, c.user_id,
    CASE
      WHEN f.first_active_month = c.activity_month THEN 'new'
      WHEN p.user_id IS NOT NULL THEN 'retained'
      WHEN f.first_active_month < c.activity_month - INTERVAL 1 MONTH THEN 'resurrected'
      ELSE 'new_or_history_incomplete'
    END AS movement_type
  FROM curr c JOIN first_active f USING (user_id)
  LEFT JOIN user_months p
    ON p.user_id = c.user_id
   AND p.activity_month = c.activity_month - INTERVAL 1 MONTH
), churned AS (
  SELECT p.activity_month + INTERVAL 1 MONTH AS activity_month,
         p.user_id, 'churned' AS movement_type
  FROM user_months p
  LEFT JOIN user_months c
    ON c.user_id = p.user_id
   AND c.activity_month = p.activity_month + INTERVAL 1 MONTH
  WHERE c.user_id IS NULL
)
SELECT activity_month, movement_type, COUNT(DISTINCT user_id) AS users
FROM (
  SELECT * FROM curr_labels
  UNION ALL
  SELECT * FROM churned
) all_movements
GROUP BY 1, 2 ORDER BY 1, 2;
```

The churn rows are attributed to the month immediately following the last active month in this query. For final-month churn, that next month may be incomplete; only publish churn for fully observed periods. The query also uses “first observed active month” as the new-user definition; if you need true newly acquired users, join signup cohorts instead. `new_or_history_incomplete` flags the case where a user was first observed in the prior month and is active now but not active in the prior month: under complete history this should be impossible, but with truncated history it must not be misclassified as resurrection.

**Important operational refinement:** the cleanest movement model builds each report month with a complete activity history, then compares sets for `curr_month` and `prev_month` and checks all prior months for first activity. Never interpret a missing prior partition as user inactivity.

### 12.6 Task F — changing the active definition changes retention

Compare at least two definitions:

- `meaningful_v1`: only `meaningful_activity` events.
- `any_non_signup_v1`: any non-bot event except `signup`.

```sql
WITH activity_definitions AS (
  SELECT user_id, CAST(event_ts_utc AS DATE) AS activity_date,
         'meaningful_v1' AS definition
  FROM canonical_events
  WHERE event_name = 'meaningful_activity' AND is_bot = FALSE
  UNION
  SELECT user_id, CAST(event_ts_utc AS DATE) AS activity_date,
         'any_non_signup_v1' AS definition
  FROM canonical_events
  WHERE event_name <> 'signup' AND is_bot = FALSE
), user_day AS (
  SELECT DISTINCT user_id, activity_date, definition FROM activity_definitions
)
SELECT definition, activity_date, COUNT(DISTINCT user_id) AS active_users
FROM user_day GROUP BY 1, 2 ORDER BY 2, 1;
```

The second definition is intentionally broad and likely overstates meaningful engagement. Compare the outputs and explain which question each answers. Never switch active definitions without a new semantic metric version and a historical restatement plan.

### 12.7 Task G — incremental update with a late event

1. Build `user_daily_activity` from the current canonical events.
2. Add a late event with an old occurrence date but a current ingestion date, e.g. a `meaningful_activity` for `u3` on Jan 3 ingested on Jan 10.
3. Recompute Jan 3 using the affected-date replacement pattern in Section 11.4.
4. Run the full-rebuild equivalence queries in Section 11.5.
5. Assert both anti-join/`EXCEPT` results are empty and no duplicate user-day keys exist.

The late event should add exactly one new `(u3, Jan 3, meaningful_v1)` row. A rerun should not add a second copy. In a real pipeline, do not use the event's occurrence date alone to decide whether it is newly ingested; use ingestion watermarks and stable event IDs.

### 12.8 Task H — incomplete follow-up periods

Set `last_complete_activity_date` to Jan 5 and inspect a cohort with signup Jan 1. D1 is mature, D7 and D30 are not. The correct output has D7/D30 as null, not zero. Restore the last-complete date to Jan 10 and confirm D7 remains mature only for cohorts whose target date is Jan 10 or earlier.

## 13. Tests and validation

A production metric pipeline should test semantics, not only whether SQL runs.

### 13.1 Data tests

- `event_id` is non-null and unique in canonical events, or source-specific deduplication is documented.
- `user_id` is non-null for user-level metrics; unresolved anonymous events are separately measured.
- `event_ts_utc` is valid and within plausible bounds.
- `user_daily_activity` unique key is `(user_id, activity_date, activity_definition_version)`.
- Cohort size is positive for published cohorts.
- `retained_users <= cohort_size` for exact-day retention.
- Retention rates are in `[0,1]`.
- Mature cells have numeric retention; immature cells are null.
- Retention definitions use the same time zone and activity definition across cohort and activity facts.
- Funnel step timestamps satisfy the declared order and conversion window.
- Step counts are non-increasing for a strictly sequential funnel.
- Revenue totals reconcile to a canonical order/payment fact after refund and currency policy.

### 13.2 Example assertions

```sql
-- Duplicate user-day keys: must return zero rows.
SELECT user_id, activity_date, activity_definition_version, COUNT(*) AS n
FROM user_daily_activity
GROUP BY 1, 2, 3 HAVING COUNT(*) > 1;

-- Invalid retention values: must return zero rows.
SELECT * FROM retention_cells
WHERE retention_rate < 0 OR retention_rate > 1
   OR retained_users > cohort_size;

-- Sequential funnel count invariant: must return zero rows.
SELECT * FROM funnel_results
WHERE signup_users > visit_users
   OR cart_users > signup_users
   OR purchase_users > cart_users;
```

These tests assume `retention_cells` and `funnel_results` are published models with the indicated columns. Adapt the table names to your project.

### 13.3 Hand-worked checks

Use explicit defect-injection cases so tests prove they detect realistic failures:

| Injected defect | Expected detector | Required result |
|---|---|---|
| Duplicate delivery of the same logical event | Canonical-event uniqueness/dedup test | Duplicate logical event rejected or deterministically collapsed |
| One user emits five activity events on one date | DAU versus event-count hand check | User contributes one DAU and one user-day |
| Activity occurs on D8 but not D7 | Exact-day versus on-or-after retention fixture | Exact D7 excludes the user; on-or-after D7 includes them if the horizon is complete |
| Funnel events occur out of order | Strict-funnel timestamp assertions | Later step is not counted as reached |
| Event occurs exactly at `entry_ts + 7 days` | Half-open conversion-window boundary test | Event is excluded under `[entry_ts, entry_ts + 7 days)` |
| A cohort's D7 target date is after the last complete date | Maturity test | Retention is `NULL`, not zero |
| Late event changes a prior user-day | Incremental/full-rebuild bidirectional `EXCEPT` | Both difference sets are empty after recomputation |
| Unknown/null bot flag enters canonical events | Canonicalization quality test | Row is resolved or quarantined, not silently omitted |

For any new metric:

1. Create 3–10 users with known events.
2. Compute expected numerator and denominator by hand.
3. Include a user with multiple qualifying events to catch event/user confusion.
4. Include a user with no activity to check cohort denominator retention.
5. Include a late event and a duplicate delivery.
6. Include a user with an event exactly at the conversion-window boundary to verify whether the interval is inclusive or exclusive.
7. Include an immature cohort to ensure it is null rather than zero.
8. Compare incremental and full rebuild outputs at row level.

### 13.4 Performance checks

- Partition canonical events by event date or ingestion date according to the dominant workload.
- Filter early and project only needed columns.
- Materialise user-day facts for repeated retention queries.
- Avoid cross joining every user to every date unless a bounded grid is required for output.
- Check query plans and shuffle/skew when using Spark or distributed warehouses.
- Cluster/sort on common filter and join keys where the platform supports it.
- Track freshness, row counts, unique-key violations, null rates, event volume, and late-arrival distribution.

## 14. Exercises with solutions

### Exercise 1 — DAU versus event count

A date has 100 `meaningful_activity` events from 20 distinct non-bot users. What is DAU?

**Solution:** DAU = 20. Event count is 100 and can be a separate engagement metric; it is not DAU.

### Exercise 2 — exact D7 retention

A signup cohort contains 200 users. On exactly day 7, 42 are active. Another 18 are active only on day 8. What is exact D7 retention? What is on-or-after D7 retention through day 30 if all 60 are active on day 7 or later and the window is complete?

**Solution:** exact D7 = 42/200 = 21%. On-or-after D7 = 60/200 = 30%. Use the original 200-user denominator for both.

### Exercise 3 — immature cohort

A cohort signed up four days ago. Can D7 retention be 0%?

**Solution:** not as an observed metric. It is immature because the D7 target day is not complete. Publish null/blank and a maturity flag.

### Exercise 4 — funnel grain

A user visits five times in separate sessions and purchases once. How many conversions count in a first-visit user-level funnel? How many sessions convert in a session-level funnel if the purchase occurs in one session?

**Solution:** user-level: one converting user if the purchase satisfies the chosen sequence/window from first entry. Session-level: one converting session. Do not count five converting users or five converting sessions.

### Exercise 5 — retention versus churn

A user is active in January, inactive in February, and active in March. Under month-over-month movement, classify the user in February and March.

**Solution:** churned in February under the activity-churn definition. Resurrected in March if there is qualifying activity before February and the history is complete. This is not proof the user permanently left in February.

### Exercise 6 — late-arriving event

A meaningful event occurred on March 3 but arrived March 10. Why is processing only the March 10 event partition insufficient?

**Solution:** the activity belongs to March 3's event-time partition and may affect user-day activity, sessions, retention, and cohort/funnel aggregates. The pipeline must use ingestion metadata to identify affected event-time dates and recompute the relevant keys/partitions.

### Exercise 7 — Simpson's paradox

Overall retention declines while retention improves in both paid and organic channels. Give one plausible explanation.

**Solution:** the mix of new users shifted toward the lower-retention channel, changing the aggregate weighted average. Report channel denominators and mix changes; don't assume the aggregate implies within-channel deterioration.

### Exercise 8 — choose an approximate method

When might a bitmap or approximate distinct sketch be appropriate?

**Solution:** bitmaps can be effective for repeated set intersections/unions over stable entity indexes; sketches can be useful for large aggregate distinct-count estimates when controlled error is acceptable. Neither is universally appropriate; exact user-day facts remain useful for auditing and arbitrary per-user analysis.

## 15. Common mistakes and production failure modes

1. **Undefined “active”:** changing the event set changes DAU and retention. Version the definition.
2. **Wrong denominator:** dividing retained users by users active the previous day answers a different question from cohort retention.
3. **Immature cells set to zero:** makes the newest cohorts appear to fail.
4. **Event-level funnel presented as user conversion:** repeated events distort rates.
5. **Out-of-order steps accepted:** later events can incorrectly satisfy earlier steps if sequence logic is absent.
6. **Pre-signup identity mismatch:** anonymous visits are not stitched to signup users, causing funnel leakage.
7. **One-to-many join multiplication:** user counts or revenue are inflated.
8. **Mixed time zones:** users move across dates and cohort ages.
9. **Late-arriving events ignored:** historical activity and session boundaries become wrong.
10. **Incremental append-only logic:** reruns duplicate rows or fail to correct changed keys.
11. **Latest attribute used for historical segmentation:** rewrites past channel/plan membership.
12. **Survivorship bias:** analysing only currently active users overstates retention/LTV.
13. **Tiny segments overinterpreted:** rates are noisy and can expose sensitive groups.
14. **Retention equated with survival:** “not seen” is not always “churned.”
15. **LTV extrapolation without validation:** early cohorts may not represent mature ones.
16. **Approximation used without error budget:** approximate cardinality may be unsuitable for financial reconciliation or contractual metrics.
17. **No restatement policy:** late identity resolution or bot filtering silently changes historical denominators.

## 16. Knowledge checkpoint

You should be able to answer these without looking up the lesson:

1. What are the grain, numerator, denominator, window, and active definition for DAU and D7 retention?
2. Why does exact D7 retention differ from on-or-after D7 retention?
3. How should an immature retention cell be represented?
4. What is the difference between a user-level and session-level funnel?
5. How do strict-order and loose-order funnels differ under this lesson's definitions?
6. How can `LEAD`/`LAG` help with event sequences, and what do they not solve by themselves?
7. Why can one-to-many joins inflate conversion or revenue?
8. How do new, retained, resurrected, and churned users relate to net active-user change?
9. What is right-censoring, and why is it relevant to churn/LTV?
10. How should an incremental pipeline process a late-arriving event?
11. Why must incremental output be compared to a full rebuild at row level?
12. When are bitmaps or approximate sketches helpful, and what are their limitations?

## 17. Final competency checklist

- [ ] Define each metric's population, grain, numerator, denominator, time window, and time zone.
- [ ] Build canonical events and a unique user-day activity table.
- [ ] Build signup cohorts using a stable first-event/source-of-truth rule.
- [ ] Calculate exact D1/D7/D30 retention with original cohort denominators.
- [ ] Distinguish exact-day, on-or-after, and rolling retention.
- [ ] Generate a complete cohort triangle with immature cells left null.
- [ ] Implement strict and loose funnels with a stated seven-day window.
- [ ] Explain per-user versus per-session conversion and time-to-convert.
- [ ] Use sessionisation and segmentation rules consistently.
- [ ] Decompose active-user movement and distinguish activity churn from survival.
- [ ] Explain revenue cohorts, LTV, discounting, and payback assumptions.
- [ ] Design incremental recomputation for late events and test against a full rebuild.
- [ ] Add uniqueness, range, maturity, funnel-order, and reconciliation tests.
- [ ] Document metric versions, lineage, refresh watermark, and historical restatement policy.

## 18. Authoritative references

Use official documentation for dialect-specific behaviour and primary methodology references for survival analysis. Verify the exact version used by your platform.

- DuckDB SQL documentation: <https://duckdb.org/docs/stable/sql/introduction>
- DuckDB date functions: <https://duckdb.org/docs/stable/sql/functions/date>
- PostgreSQL date/time functions (for dialect comparison): <https://www.postgresql.org/docs/current/functions-datetime.html>
- dbt documentation — models and incremental models: <https://docs.getdbt.com/docs/build/incremental-models>
- dbt documentation — data tests: <https://docs.getdbt.com/docs/build/data-tests>
- Google Analytics documentation — cohorts and retention concepts: <https://support.google.com/analytics/answer/9670133>
- Amplitude documentation — retention analysis concepts: <https://amplitude.com/docs/analytics/charts/retention-analysis/retention-analysis-interpret>
- Kaplan, E. L. and Meier, P. (1958), “Nonparametric Estimation from Incomplete Observations,” *Journal of the American Statistical Association*.
- Klein, J. P. and Moeschberger, M. L., *Survival Analysis: Techniques for Censored and Truncated Data*.

Vendor analytics products differ in definitions for rolling retention, strict funnels, and session attribution. Treat vendor terminology as a starting point, then publish your own metric contract and test it against examples.
