# A/B Testing and Experiment Data Pipelines

> **Stage:** 2C — Data Engineering_3  
> **Module:** 09 — Analytics Foundations for Data Engineers  
> **Lesson:** 04 of 09  
> **Roadmap source:** `roadmap-Analytics-Foundations-for-Data-Engineers.md`  
> **Target:** `04-ab-testing-and-experiment-data-pipelines.md`

## 1. Learning objectives

After this lesson, you should be able to:

- Design a randomized controlled experiment with a hypothesis, primary metric, guardrails, MDE, duration, and decision rule.
- Select and document a randomization unit: user, session, device, account, or cluster.
- Implement deterministic assignment with stable hashing, traffic buckets, ramp-up, mutual-exclusion layers, and holdouts.
- Distinguish assignment, exposure, and outcome; explain intent-to-treat (ITT) and the risks of exposed-only analysis.
- Design experiment tables with explicit grains, keys, timestamps, and lineage.
- Define primary, secondary, guardrail, and diagnostic metrics consistently in a semantic layer.
- Detect and investigate sample ratio mismatch (SRM) and other data-quality failures.
- Build correct SQL for conversion rate and revenue per randomized user without join fan-out.
- Explain novelty, primacy, seasonality, interference, Simpson's paradox, bots, and instrumentation failures.
- Apply CUPED/CUPAC, stratification, sequential-testing awareness, and multiple-comparison safeguards.
- Build a reproducible synthetic experiment with 500,000 users, known treatment effect, exposure loss, bot traffic, guardrails, statistical analysis, and tests.
- Operate an idempotent experiment pipeline that handles retries, late events, identity resolution, and reproducible result publication.

## 2. Why experimentation is a Data Engineering problem

A/B testing is not merely a t-test at the end of a notebook. The causal interpretation depends on how users were assigned, how exposure was recorded, how outcomes were joined, and which units entered the analysis. A statistically correct test on a corrupted table still produces an untrustworthy conclusion.

A production experiment system must preserve:

1. **Design intent:** hypothesis, estimand, metrics, assignment unit, allocation, analysis window, exclusions, stopping rule, and decision rule.
2. **Assignment integrity:** stable and auditable treatment assignment that cannot silently change on retry or identity update.
3. **Exposure integrity:** evidence of when the assigned experience was actually delivered.
4. **Measurement integrity:** deduplicated events, consistent identity, well-defined denominators, late-data policy, and bot/internal-traffic handling.
5. **Statistical integrity:** analysis at the right unit, valid uncertainty estimates, SRM checks, multiplicity policy, and no unplanned peeking.
6. **Operational integrity:** reproducible inputs, idempotent recomputation, versioned results, and clear status when data are incomplete.

### Experiment lifecycle

```text
Hypothesis
  → Design (estimand, unit, primary metric, MDE, alpha, power, duration)
  → Pre-launch data and assignment validation
  → Launch / traffic ramp
  → Assignment and exposure logging
  → Outcome ingestion and data-quality monitoring
  → SRM + metric-pipeline validation
  → Freeze analysis snapshot / wait for late events
  → ITT analysis + uncertainty + guardrails
  → Decision, documentation, and result publication
  → Archive experiment configuration and code versions
```

### Example

Hypothesis: “A simplified checkout increases the probability that an eligible randomized user completes an order within seven days.”

- Unit: user, assigned once per experiment.
- Primary metric: `converted_7d`, a binary per-user outcome.
- Estimand: treatment-minus-control difference in the probability of conversion among all eligible randomized users (ITT).
- MDE: +1 percentage point absolute, from a specified baseline rate.
- Guardrails: checkout error rate and p95 checkout latency.
- Decision rule: consider shipping only if the predeclared analysis provides sufficient evidence of a practically meaningful primary-metric improvement and neither guardrail crosses its predeclared harm threshold. Exact thresholds must be chosen with stakeholders before launch.

Randomization supports causal interpretation of assignment when assignment is implemented correctly and the analysis respects the design. It does not repair broken instrumentation, post-treatment selection, interference, or differential missing outcomes.

## 3. Prerequisites and environment

This lesson builds on the previous lesson, **Hypothesis Testing and Confidence Intervals**. You should understand effect sizes, p-values, confidence intervals, power, and multiple comparisons.

The main lab uses Python, NumPy, SciPy, pandas, and DuckDB. Optional SQL modeling can be placed in dbt; Spark is discussed for distributed scale.

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install numpy pandas scipy duckdb statsmodels
```

For a dbt project, install the adapter appropriate to the warehouse, for example `dbt-duckdb`. Do not assume SQL syntax or incremental semantics are identical across adapters. Record Python and package versions for reproducibility.

## 4. Experiment design fundamentals

### 4.1 Randomized control and treatment

Eligible units are assigned to one of at least two arms:

- **Control:** current or baseline experience.
- **Treatment:** the proposed change.

Randomization aims to make assignment independent of pre-treatment characteristics in expectation. It balances both observed and unobserved covariates on average, but chance imbalances can occur, especially in small samples. Randomization does not mean every realized group is identical.

Define before launch:

- hypothesis and estimand;
- eligible population and exclusions;
- randomization unit;
- primary, secondary, diagnostic, and guardrail metrics;
- assignment ratio and allocation policy;
- baseline, MDE, alpha, target power, expected duration;
- analysis method, multiple-testing policy, and stopping rule;
- exposure definition, outcome window, and late-event grace period.

### 4.2 Randomization unit

| Unit | Appropriate when | Risks and design notes |
|---|---|---|
| User | Experience is persistent for a signed-in or resolved user | Cross-device identity changes can cause reassignment or contamination |
| Session | Treatment should vary by session and carryover is negligible | The same person can see both arms; outcomes must be session-level or modeled accordingly |
| Device | Experience is device-specific and device identity is stable | One person may span devices; account-level outcomes can be contaminated |
| Account / organization | Members share a product experience or decisions | Need enough independent accounts; cluster-level power may be lower |
| Cluster (store, region, school, network) | Spillovers or operational rollout require group assignment | Requires cluster-aware inference; few clusters create difficult uncertainty estimation |

Choose the unit based on the intervention, interference risk, and intended estimand—not merely the easiest key to join. Assignment unit, exposure logging, metric aggregation, and inference must be aligned.

### 4.3 Experiment lifecycle and duration

Duration is not only a sample-size calculation. It may need to cover weekly seasonality, billing cycles, novelty/primacy effects, delayed outcomes, and enough independent units. Set a fixed horizon or use a predeclared sequential design. Avoid stopping as soon as a conventional p-value crosses 0.05.

- **Novelty effect:** users react temporarily because a feature is new.
- **Primacy effect:** early experience or first exposure has a different effect than later use.
- **Seasonality:** weekday, holiday, campaign, or billing patterns alter outcomes.
- **Long-term holdout:** retain a small randomized control group to measure long-run effects, saturation, or cumulative costs after a launch.

## 5. Assignment and exposure architecture

### 5.1 Deterministic assignment

Randomization can be made deterministic using a stable hash of an experiment identifier and the canonical entity identifier. For example:

```python
import hashlib

def stable_bucket(experiment_id: str, entity_id: str, *, buckets: int = 10_000) -> int:
    if buckets <= 0:
        raise ValueError("buckets must be positive")
    payload = f"{experiment_id}|{entity_id}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big") % buckets

def assign_arm(experiment_id: str, entity_id: str, treatment_share: float = 0.5) -> str:
    if not 0.0 <= treatment_share <= 1.0:
        raise ValueError("treatment_share must be between 0 and 1")
    bucket = stable_bucket(experiment_id, entity_id)
    cutoff = int(treatment_share * 10_000)
    return "treatment" if bucket < cutoff else "control"

assert stable_bucket("checkout_v1", "user-123") == stable_bucket("checkout_v1", "user-123")
assert assign_arm("checkout_v1", "user-123") in {"control", "treatment"}
```

This is deterministic assignment, not a claim that each finite population is exactly balanced. Reproducibility requires the hash algorithm, string encoding, separator, canonical identifier, bucket count, seed/configuration, and selection rule to remain stable. Do not use a language's process-randomized built-in `hash()` for persistent assignment. Avoid ambiguous concatenation such as `"ab"+"c"` versus `"a"+"bc"`; delimiters or length-prefix encoding are important.

A high-quality hash spreads typical identifiers across buckets, but deterministic selection is not automatically representative. Check identifier coverage, eligibility, key reuse, and group balance. If IDs encode geography or acquisition channel and the hash or key construction is faulty, allocation may be systematically biased.

### 5.2 Buckets, traffic allocation, ramp-up, and holdouts

A common implementation maps a stable hash into \(B\) buckets, then assigns ranges to experiments or arms.

- **Traffic allocation:** only a chosen share of eligible traffic enters an experiment; the rest may receive the default experience.
- **Ramp-up:** gradually increase traffic after monitoring assignment, exposure, error, and guardrail signals. Ramp-up rules must be documented; changing allocation should not change a unit's arm unexpectedly.
- **Mutual-exclusion layer:** prevents experiments that might interact from simultaneously assigning the same unit to conflicting treatments. Layering needs an explicit, deterministic policy.
- **Holdout:** a randomized subset remains on control for longer-term measurement.
- **Reassignment policy:** usually a unit's assignment is sticky for the experiment. If configuration changes, preserve original assignment records and version the configuration.

Do not compare only users who “looked eligible after treatment” if treatment can influence that eligibility. Define eligibility before assignment whenever possible.

### 5.3 Assignment versus exposure versus outcome

- **Assigned:** a unit was allocated to an arm according to the experiment configuration.
- **Exposed:** the treatment or control experience was actually delivered according to an explicit exposure event or server-side confirmation.
- **Outcome:** the metric value measured over the specified window.

Exposure logs are essential diagnostics. However, analyzing only exposed users can break randomization: exposure may depend on user behaviour, client availability, treatment response, or other post-assignment variables. The primary causal analysis is often **intent-to-treat (ITT)**: analyze units according to their assigned arm, whether or not exposure was recorded. Exposed-only analysis can be useful for operational diagnostics, but is not automatically a valid causal estimate. Per-protocol or complier-effect estimands need additional assumptions and methods.

## 6. Experiment data model

Every table must document its grain. Most silent experiment errors are grain errors: duplicate assignment rows, event joins that multiply revenue, or outcome rows joined to several exposures.

### 6.1 Recommended tables

| Table | Grain | Primary key / important keys | Purpose |
|---|---|---|---|
| `experiment_config` | One row per experiment configuration version | `(experiment_id, config_version)` | Hypothesis, arms, unit, traffic share, metric version, dates, stopping rule |
| `experiment_assignments` | One row per experiment × randomized entity | `(experiment_id, entity_id)` for a sticky assignment; retain `config_version` and assignment timestamp | Arm assignment and eligibility snapshot |
| `experiment_exposures` | One row per exposure event | `exposure_id`; `(experiment_id, entity_id)` is a join key, not necessarily unique | When and how the assigned experience was delivered |
| `raw_events` | One row per source event | Stable `event_id` where available | Append-only ingested outcomes and diagnostics |
| `identity_map` | One row per identity link/version or validity interval | Source identity + validity/version | Cross-device/account resolution with time-aware rules |
| `user_daily_metrics` | One row per experiment × entity × date | `(experiment_id, entity_id, metric_date)` | Recomputable per-user outcomes/covariates, with a documented time zone |
| `experiment_results` | One row per experiment × analysis version × metric × arm/contrast | Composite versioned key | Estimates, intervals, p-values, guardrails, counts, data snapshot, code version |

Do not overwrite historical assignment records to make them match a new configuration. Preserve assignment timestamp, configuration version, and event time versus ingestion time. Where identity mappings change, use a documented “as-of” resolution policy so a later identity link does not silently rewrite historical assignment.

### 6.2 Key relationships

```text
experiment_config (1) ─── (many) experiment_assignments
experiment_assignments (1) ─── (many) experiment_exposures
experiment_assignments (1) ─── (many) user_daily_metrics
raw_events ── identity resolution ── per-entity outcome aggregation
user_daily_metrics ── analysis window ── one row per randomized entity
one analysis snapshot ── statistical analysis ── experiment_results
```

The assignments table is the denominator anchor for ITT. Build a one-row-per-assigned-entity analysis table first, then left join pre-aggregated outcome metrics. Never join raw event rows directly to assignments and calculate revenue without controlling the join grain.

### 6.3 Important timestamps

- `assigned_at`: assignment decision time.
- `exposed_at` / `event_ts`: time of actual delivery or event occurrence.
- `ingested_at`: time the event entered the platform.
- `metric_window_start`, `metric_window_end`: outcome eligibility interval.
- `analysis_cutoff_at`: event-time cutoff for a result snapshot.
- `computed_at`: pipeline execution time.

A late event may have `event_ts` inside the analysis window but `ingested_at` after the first result computation. Results should be marked provisional until the grace period closes or be versioned when recomputed.

## 7. Metric definitions and statistical design

### 7.1 Metric categories

- **Primary metric:** the single main outcome used for the principal decision. Specify numerator, denominator, unit, window, eligibility, deduplication, and null handling.
- **Secondary metrics:** additional outcomes that help explain the primary effect. Their multiplicity must be considered.
- **Guardrail metrics:** measures that must not degrade beyond an agreed threshold, such as checkout error rate or p95 latency.
- **Diagnostic metrics:** assignment balance, exposure rate, event volume, missingness, latency distributions, and segment checks used to investigate the mechanism or data integrity.

### 7.2 Example definitions

**Conversion per randomized user**

\[
\text{conversion rate} =
\frac{\text{distinct assigned entities with at least one qualifying conversion}}
{\text{eligible randomized entities}}
\]

**Revenue per randomized user (RPU)**

\[
\text{RPU} =
\frac{\text{qualifying net revenue attributed in the window}}
{\text{eligible randomized entities}}
\]

RPU is a ratio of total revenue to assigned users, not the average order value among purchasers. Conditioning on purchasers changes the population after treatment and can bias a causal comparison.

**Guardrails:** define checkout error rate denominator (for example, eligible checkout attempts) and p95 latency population (for example, all valid checkout requests). Keep the metric definition stable across arms and use a predeclared threshold.

### 7.3 Semantic-layer metric contracts

Store a versioned metric definition or reference it from the semantic layer (the roadmap links this to Module 2C.6). A metric contract should include:

- stable name and version;
- business definition and owner;
- SQL/expression or model reference;
- grain and unique key;
- numerator, denominator, null handling, and unit;
- event-time window and timezone;
- filters, bot policy, deduplication, and late-arrival policy;
- allowed dimensions and known limitations;
- tests and freshness requirements.

Do not duplicate slightly different definitions in experiment notebooks and dashboards. If the metric definition changes, publish a new version and rerun historical results only under an explicit backfill policy.

## 8. SRM and data-quality validation

### 8.1 Sample Ratio Mismatch

SRM occurs when observed assignment counts differ from the allocation expected by the design more than random variation would plausibly explain. It is an alarm requiring investigation, not proof by itself of a bug. It can reflect a real assignment bug, eligibility drift, logging loss, identity duplication, or an incorrect expected allocation.

For two arms with expected proportions \(p_i\) and observed counts \(O_i\), the Pearson statistic is:

\[
\chi^2 = \sum_i \frac{(O_i-E_i)^2}{E_i}, \quad E_i=Np_i.
\]

Compare it with a chi-square distribution with \(k-1\) degrees of freedom for \(k\) arms, when expected counts are adequate. Define the expected allocation from the experiment configuration and eligible population—not from the observed counts.

```python
import numpy as np
from scipy.stats import chisquare

def srm_test(observed_counts, expected_proportions):
    observed = np.asarray(observed_counts, dtype=float)
    proportions = np.asarray(expected_proportions, dtype=float)
    if observed.ndim != 1 or proportions.ndim != 1 or len(observed) != len(proportions):
        raise ValueError("Counts and proportions must be equal-length one-dimensional arrays")
    if np.any(observed < 0) or not np.all(np.isfinite(observed)):
        raise ValueError("Counts must be finite and non-negative")
    if np.any(proportions <= 0) or not np.isclose(proportions.sum(), 1.0):
        raise ValueError("Expected proportions must be positive and sum to one")
    expected = observed.sum() * proportions
    return chisquare(f_obs=observed, f_exp=expected)

result = srm_test([250_100, 249_900], [0.5, 0.5])
print({"chi2": result.statistic, "p_value": result.pvalue})
```

An SRM threshold should be defined operationally (often a small p-value plus minimum-count safeguards), with alert severity based on the experiment's context. Avoid repeatedly testing SRM without accounting for monitoring cadence if alerts themselves are used as formal inferential claims. For engineering alarms, the purpose is to flag unexpected imbalance for investigation.

### 8.2 Validation layers

1. **Assignment:** unique `(experiment_id, entity_id)`, valid arm, expected eligibility, correct configured allocation.
2. **Exposure:** exposure arm agrees with assignment, exposure rate by arm, timestamp after assignment, duplicate delivery IDs.
3. **Outcome:** one analysis row per randomized entity, metric windows applied correctly, valid denominators, no event join fan-out.
4. **Identity:** stable resolution policy, no entity in both arms, cross-device reassignment rate monitored.
5. **Data quality:** event freshness, duplicate rate, bot rate, nulls, missing outcomes, event volume, late-event backlog.
6. **Statistical:** SRM, plausible pre-treatment covariate balance, effect and interval, guardrail estimates, multiplicity policy.
7. **Publication:** snapshot ID, query/code version, metric version, cutoff time, row counts, status (`provisional`, `final`, `invalidated`).

A pre-treatment balance check can detect some problems but does not prove randomization is correct. Conversely, a single covariate imbalance can occur by chance. SRM is a high-priority diagnostic because many other analyses become hard to trust when assignment counts are wrong.

## 9. SQL and pipeline implementation

The following SQL is DuckDB-style SQL. Adapt types, percentile functions, date handling, incremental materializations, and test syntax for your database or dbt adapter.

### 9.1 Build one-row-per-entity metrics

Assume:
- `experiment_assignments(experiment_id, entity_id, arm, assigned_at, eligible)`;
- `raw_events(event_id, experiment_id, entity_id, event_name, event_ts, ingested_at, amount, is_bot)`;
- `experiment_config(experiment_id, window_start, window_end, analysis_cutoff_at)`.

Deduplicate by stable event ID before aggregating. If the source has no stable event ID, define an idempotent event key carefully; a timestamp-plus-payload hash can incorrectly collapse legitimate repeated events.

```sql
-- DuckDB-style example. The config row is one selected version per experiment.
WITH config AS (
    SELECT experiment_id, window_start, window_end, analysis_cutoff_at
    FROM experiment_config
    WHERE experiment_id = 'checkout_v1'
      AND config_version = 1
),
deduplicated_events AS (
    SELECT * EXCLUDE (rn)
    FROM (
        SELECT
            e.*,
            row_number() OVER (
                PARTITION BY e.event_id
                ORDER BY e.ingested_at DESC
            ) AS rn
        FROM raw_events e
        JOIN config c USING (experiment_id)
        WHERE e.ingested_at <= c.analysis_cutoff_at
    )
    WHERE rn = 1
),
entity_outcomes AS (
    SELECT
        e.experiment_id,
        e.entity_id,
        max(CASE WHEN e.event_name = 'purchase' THEN 1 ELSE 0 END) AS converted,
        sum(CASE WHEN e.event_name = 'purchase' THEN coalesce(e.amount, 0) ELSE 0 END) AS revenue,
        sum(CASE WHEN e.event_name = 'checkout_error' THEN 1 ELSE 0 END) AS checkout_errors,
        count(*) FILTER (WHERE e.event_name = 'checkout_attempt') AS checkout_attempts
    FROM deduplicated_events e
    JOIN config c USING (experiment_id)
    WHERE e.event_ts >= c.window_start
      AND e.event_ts < c.window_end
      AND coalesce(e.is_bot, false) = false
    GROUP BY e.experiment_id, e.entity_id
)
SELECT
    a.experiment_id,
    a.entity_id,
    a.arm,
    coalesce(o.converted, 0) AS converted,
    coalesce(o.revenue, 0.0) AS revenue,
    coalesce(o.checkout_errors, 0) AS checkout_errors,
    coalesce(o.checkout_attempts, 0) AS checkout_attempts
FROM experiment_assignments a
LEFT JOIN entity_outcomes o
  ON a.experiment_id = o.experiment_id
 AND a.entity_id = o.entity_id
WHERE a.experiment_id = 'checkout_v1'
  AND a.eligible = true;
```

Important caveats:

- The final table's grain is one row per eligible assignment, including users with no outcome events. This is essential for an ITT conversion denominator.
- Filling a missing conversion aggregate with zero is valid only when the event window is mature and the source is known complete for that unit/window. If an event partition is missing, ingestion is delayed, or instrumentation is unhealthy, treat the outcome as incomplete and keep the result provisional rather than silently converting missingness into a non-conversion.
- The SQL assumes purchase events are deduplicated and the event schema correctly identifies bot traffic. Production bot handling often needs a versioned policy and should not rely on a single unvalidated flag.
- Revenue semantics (refunds, currency conversion, tax, attribution, repeated purchases) must be specified by the metric contract.
- `max(converted)` means at least one purchase. If the business metric is number of orders or revenue, use the appropriate aggregate.
- For exposure-specific diagnostics, aggregate exposure events separately before joining. Joining assignments directly to many exposure rows and many raw events can multiply rows.

### 9.2 Conversion rate and revenue per randomized user

```sql
WITH per_user AS (
    -- Use the one-row-per-assignment table built above.
    SELECT experiment_id, entity_id, arm, converted, revenue,
           checkout_errors, checkout_attempts
    FROM experiment_user_outcomes
    WHERE experiment_id = 'checkout_v1'
),
arm_summary AS (
    SELECT
        arm,
        count(*) AS randomized_users,
        sum(converted) AS converted_users,
        avg(converted::DOUBLE) AS conversion_rate,
        sum(revenue) AS total_revenue,
        avg(revenue) AS revenue_per_randomized_user,
        sum(checkout_errors)::DOUBLE / nullif(sum(checkout_attempts), 0) AS checkout_error_rate
    FROM per_user
    GROUP BY arm
)
SELECT * FROM arm_summary;
```

Do not calculate revenue per user by joining each assignment to raw purchase rows and then counting users: users with multiple purchases would be duplicated in the denominator. Aggregate to the entity grain first.

### 9.3 dbt model and tests (illustrative)

A dbt model can materialize `experiment_user_outcomes` from versioned source models. Use `unique` and `not_null` tests for `(experiment_id, entity_id)` or a surrogate key, accepted-values tests for `arm`, and custom tests for assignment-to-exposure arm agreement and SRM. A uniqueness test catches duplicates but cannot by itself prove the metric's business definition is correct.

Example generic test configuration (adapt to your dbt version and project syntax):

```yaml
version: 2
models:
  - name: experiment_user_outcomes
    columns:
      - name: experiment_id
        data_tests: [not_null]
      - name: entity_id
        data_tests: [not_null]
      - name: arm
        data_tests:
          - not_null
          - accepted_values:
              arguments:
                values: ['control', 'treatment']
      - name: converted
        data_tests:
          - not_null
```

Add a model-level uniqueness test on the composite experiment/entity key using a custom generic test or a stable surrogate key. dbt's configuration syntax varies by version; validate the YAML with the version used in the repository.

## 10. Variance reduction and advanced designs

### 10.1 CUPED and CUPAC

CUPED uses pre-experiment outcome history or another pre-treatment covariate correlated with the outcome to reduce variance. CUPAC generalizes the idea using predictions from pre-treatment covariates. The adjustment must not use information caused by treatment.

For a pre-treatment covariate \(X\) and outcome \(Y\):

\[
Y_{\text{adj}} = Y - \theta(X-\bar X), \qquad
\theta = \frac{\operatorname{Cov}(Y,X)}{\operatorname{Var}(X)}.
\]

Estimate \(\theta\) according to a predeclared procedure and use the same policy across arms. A covariate measured after treatment starts can leak treatment effects into the adjustment. Validate that adjustment reduces variance in the intended setting and preserves the estimand.

### 10.2 Stratification

Stratified randomization can balance important pre-treatment dimensions (for example, country or platform). Analysis should account for the strata, and the allocation rules must be persisted. Do not create many tiny strata or select them after seeing outcomes.

### 10.3 Sequential testing and always-valid inference

Ordinary fixed-horizon p-values generally do not retain their advertised error rate when repeatedly inspected and used to stop early. Sequential methods define how evidence accumulates over time and which stopping rules are valid. Always-valid p-values or confidence sequences are designed for continuous monitoring under specified assumptions. They are not a license to change metrics, filter users, or repeatedly redefine the hypothesis.

### 10.4 Heterogeneous treatment effects and segments

Effects may differ by platform, geography, plan, or acquisition channel. Segment analysis can uncover real heterogeneity but creates multiplicity and low-power risks. Predeclare key segments, report denominators and intervals, apply an appropriate correction or hierarchical strategy, and distinguish confirmatory from exploratory results. Simpson's paradox can occur when group-level comparisons are aggregated across segments with different composition; inspect segment mix and the estimand before telling a causal story.

### 10.5 Interference and network effects

Standard individual-level A/B inference often assumes one unit's treatment does not affect another unit's outcome. This can fail in marketplaces, social networks, shared inventory, collaborative products, or pricing systems. Consider cluster randomization, graph-aware designs, saturation experiments, or switchbacks when spillovers are material.

### 10.6 Beyond conventional A/B tests (awareness)

- **Multi-armed bandits:** adaptively allocate traffic to improve reward during the experiment. Useful for optimization, but naive comparisons can be biased because allocation probabilities change; inference must account for the adaptive design.
- **Difference-in-differences:** compares before/after changes in treatment and comparison groups. Requires assumptions such as parallel trends and no relevant differential shocks.
- **Synthetic control:** constructs a weighted comparison from untreated units for an aggregate intervention. Validity depends on pre-intervention fit and donor-pool assumptions.
- **Switchback tests:** alternate treatments over time or operational blocks, useful when treatment affects a shared system (for example, marketplace supply). Must account for time trends, carryover, and block-level dependence.

These approaches do not replace randomization automatically; they require designs and assumptions matched to the intervention.

### 10.7 Build versus buy

The roadmap names Statsig, Optimizely, Eppo, GrowthBook, and LaunchDarkly experiments as examples of experimentation platforms. Compare products against current requirements and pricing rather than assuming feature parity.

| Decision factor | Build internally | Buy/adopt a platform |
|---|---|---|
| Assignment and SDK control | Maximum control over hashing, identity, layers, and custom rules; high responsibility | Faster integration if SDK and assignment semantics fit |
| Data model and warehouse integration | Can align tightly to internal event and metric models | Verify export fidelity, identifiers, raw assignment/exposure access, and backfill support |
| Statistical capabilities | Custom methods possible but require statistical expertise and validation | May provide analysis and monitoring, but verify assumptions and supported designs |
| Governance and audit | Must build permissions, versioning, logs, and audit trails | Assess access controls, audit export, retention, and reproducibility |
| Cost and operations | Engineering, on-call, reliability, and maintenance cost | Subscription/usage cost, vendor dependency, and migration constraints |
| Flexibility | High if well designed | Depends on product APIs, SDKs, and roadmap |

A platform does not eliminate the need for trustworthy event instrumentation, stable metric definitions, SRM monitoring, and independent validation.

## 11. Reproducible end-to-end lab

This lab specifies a synthetic experiment with **500,000 users** and a planted **+2% relative conversion effect**. The true effect is defined by the data-generating probabilities, while the observed estimate varies randomly. A simulation is not guaranteed to produce a statistically significant result in every run.

### 11.1 Lab design

- Randomization unit: synthetic user.
- Allocation: 50% control, 50% treatment using deterministic SHA-256 assignment.
- Baseline conversion probability: \(p_C=0.10\).
- Treatment conversion probability: \(p_T=0.102\), which is a 2% relative lift over 0.10 and an absolute lift of 0.002 (0.2 percentage points).
- Outcome: binary conversion within a fixed seven-day window.
- Exposure: some assigned users are not exposed; primary analysis remains ITT.
- Bots: a synthetic bot flag is logged; primary user-level metric excludes bots only if that exclusion was predeclared as eligibility before assignment. In this lab, bots are generated and explicitly marked ineligible before assignment so they are excluded from the target population, while their presence in raw events can test bot filtering.
- Guardrails: checkout error indicator and latency in milliseconds, with predeclared harm thresholds.
- Pre-treatment covariate: prior-period activity correlated with outcome; it is generated before treatment and used only for CUPED adjustment.
- Reproducibility: fixed random seed, stable hash algorithm, saved experiment config, and versioned analysis snapshot.

This lab's baseline and effect are illustrative. They are not a promise that a real experiment with the same row count will have the same variance or power.

### 11.2 Complete Python lab

Save as `ab_experiment_lab.py`. It creates assignment/exposure/outcome data, performs SRM, estimates ITT with a Welch test and bootstrap interval, compares CUPED-adjusted and unadjusted uncertainty, checks two guardrails, and validates idempotent recomputation. For a full 500,000-user run, bootstrap iterations are configurable; use 500–1,000 for a quick local smoke test and increase for a final analysis.

```python
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from scipy import stats

SEED = 20261019
N_USERS = 500_000
EXPERIMENT_ID = "checkout_simplification_v1"
BASELINE_RATE = 0.10
RELATIVE_LIFT = 0.02
TREATMENT_RATE = BASELINE_RATE * (1 + RELATIVE_LIFT)  # 0.102
TREATMENT_SHARE = 0.50
EXPOSURE_PROBABILITY = 0.97
BOOTSTRAP_REPETITIONS = 500  # Increase for more stable interval endpoints.

def stable_bucket(experiment_id: str, entity_id: str, buckets: int = 10_000) -> int:
    """Stable bucket. Encoding, separator, hash and bucket count are part of the contract."""
    if buckets <= 0:
        raise ValueError("buckets must be positive")
    payload = f"{experiment_id}|{entity_id}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big") % buckets

def assign_arm(entity_id: str, treatment_share: float = TREATMENT_SHARE) -> str:
    if not 0.0 <= treatment_share <= 1.0:
        raise ValueError("treatment_share must be between 0 and 1")
    cutoff = int(treatment_share * 10_000)
    return "treatment" if stable_bucket(EXPERIMENT_ID, entity_id) < cutoff else "control"

def build_synthetic_experiment(n_users: int = N_USERS, seed: int = SEED) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    users = pd.DataFrame({
        "entity_id": [f"user-{i:06d}" for i in range(n_users)],
        "is_bot": rng.random(n_users) < 0.01,
    })
    # Eligibility is determined before assignment. Bots exist in source traffic but are not eligible.
    users["eligible"] = ~users["is_bot"]
    eligible = users.loc[users["eligible"], ["entity_id"]].copy()
    eligible["arm"] = eligible["entity_id"].map(assign_arm)
    eligible["assigned_at"] = pd.Timestamp("2026-09-01T00:00:00Z")
    eligible["experiment_id"] = EXPERIMENT_ID
    eligible["config_version"] = 1

    # A pre-treatment covariate is independent of assignment and generated before outcomes.
    pre_activity = rng.normal(loc=0.0, scale=1.0, size=len(eligible))
    eligible["pre_activity"] = pre_activity

    arm_treatment = eligible["arm"].eq("treatment").to_numpy()
    # Use fixed probabilities for the primary metric so the planted effect is explicit.
    # Retain pre_activity for a correlated continuous secondary outcome used to illustrate CUPED.
    probabilities = np.where(arm_treatment, TREATMENT_RATE, BASELINE_RATE)
    converted = rng.binomial(1, probabilities, size=len(eligible))
    # Outcomes have a pre-treatment covariate signal for the CUPED illustration.
    # The data-generating probability remains 10%/10.2%; covariate is used as a correlated
    # pre-period proxy in a continuous secondary outcome rather than changing conversion rates.
    eligible["converted_7d"] = converted

    # Exposure is post-assignment. Some users are assigned but never exposed.
    exposed = rng.random(len(eligible)) < EXPOSURE_PROBABILITY
    exposures = eligible.loc[exposed, ["experiment_id", "entity_id", "arm"]].copy()
    exposures["exposure_id"] = [f"exp-{i:07d}" for i in range(len(exposures))]
    exposures["exposed_at"] = pd.Timestamp("2026-09-01T00:05:00Z")

    # Two guardrails. These are synthetic and designed to have no intended harmful shift.
    eligible["checkout_error"] = rng.binomial(
        1, np.where(arm_treatment, 0.020, 0.020), size=len(eligible)
    )
    eligible["checkout_latency_ms"] = rng.normal(
        loc=np.where(arm_treatment, 250.0, 250.0), scale=45.0, size=len(eligible)
    ).clip(min=20)

    # A continuous outcome with strong pre-period correlation for CUPED.
    # It is illustrative and not the primary conversion outcome.
    eligible["revenue_proxy"] = (
        10.0 + 2.0 * eligible["pre_activity"].to_numpy()
        + rng.normal(0, 5.0, size=len(eligible))
        + np.where(arm_treatment, 0.20, 0.0)
    )

    # Raw events intentionally include bot traffic and duplicates/retries to exercise pipeline rules.
    # Each entity can have one conversion event; event_id is stable and deduplicable.
    events = eligible[["experiment_id", "entity_id", "arm", "converted_7d",
                       "checkout_error", "checkout_latency_ms", "revenue_proxy"]].copy()
    events["event_id"] = [f"outcome-{i:07d}" for i in range(len(events))]
    events["event_name"] = np.where(events["converted_7d"].eq(1), "purchase", "no_purchase")
    events["event_ts"] = pd.Timestamp("2026-09-03T12:00:00Z")
    events["ingested_at"] = pd.Timestamp("2026-09-03T12:01:00Z")
    events["is_bot"] = False
    # A small retry sample repeats event IDs; downstream deduplication must keep one copy.
    retry_n = max(1, int(0.001 * len(events)))
    retries = events.iloc[:retry_n].copy()
    retries["ingested_at"] = pd.Timestamp("2026-09-03T12:03:00Z")
    raw_events = pd.concat([events, retries], ignore_index=True)

    # Include synthetic bot rows in raw event logs; they are not in the eligible assignment denominator.
    bot_users = users.loc[users["is_bot"], ["entity_id"]].copy()
    bot_events = pd.DataFrame({
        "experiment_id": EXPERIMENT_ID,
        "entity_id": bot_users["entity_id"].to_numpy(),
        "arm": "unassigned",
        "converted_7d": rng.binomial(1, 0.50, size=len(bot_users)),
        "checkout_error": rng.binomial(1, 0.05, size=len(bot_users)),
        "checkout_latency_ms": rng.normal(300, 80, size=len(bot_users)).clip(min=20),
        "revenue_proxy": np.nan,
        "event_id": [f"bot-{i:07d}" for i in range(len(bot_users))],
        "event_name": "purchase",
        "event_ts": pd.Timestamp("2026-09-03T12:00:00Z"),
        "ingested_at": pd.Timestamp("2026-09-03T12:01:00Z"),
        "is_bot": True,
    })
    raw_events = pd.concat([raw_events, bot_events], ignore_index=True)

    assignments = eligible[[
        "experiment_id", "config_version", "entity_id", "arm", "assigned_at",
        "pre_activity", "converted_7d", "checkout_error", "checkout_latency_ms", "revenue_proxy"
    ]].copy()
    return {
        "users": users,
        "assignments": assignments,
        "exposures": exposures,
        "raw_events": raw_events,
    }

def deduplicate_events(events: pd.DataFrame) -> pd.DataFrame:
    required = {"event_id", "ingested_at"}
    if not required.issubset(events.columns):
        raise ValueError(f"events missing columns: {required - set(events.columns)}")
    return (
        events.sort_values("ingested_at")
        .drop_duplicates(subset=["event_id"], keep="last")
        .reset_index(drop=True)
    )

def build_user_outcomes(assignments: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Return exactly one row per eligible randomized entity; no-outcome users remain."""
    deduped = deduplicate_events(events)
    eligible_events = deduped.loc[~deduped["is_bot"].fillna(False)].copy()
    # Aggregate events to entity grain before joining to assignments.
    aggregated = eligible_events.groupby(["experiment_id", "entity_id"], as_index=False).agg(
        event_converted=("converted_7d", "max"),
        event_error=("checkout_error", "max"),
        event_latency=("checkout_latency_ms", "mean"),
    )
    outcomes = assignments.merge(
        aggregated,
        on=["experiment_id", "entity_id"],
        how="left",
        validate="one_to_one",
    )
    outcomes["converted_7d"] = outcomes["event_converted"].fillna(0).astype(int)
    outcomes["checkout_error"] = outcomes["event_error"].fillna(0).astype(int)
    outcomes["checkout_latency_ms"] = outcomes["event_latency"].fillna(
        outcomes["checkout_latency_ms"]
    )
    return outcomes.drop(columns=["event_converted", "event_error", "event_latency"])

def srm_pvalue(assignments: pd.DataFrame, expected_treatment_share: float = 0.5) -> float:
    if not 0.0 < expected_treatment_share < 1.0:
        raise ValueError("expected_treatment_share must be strictly between 0 and 1")
    if assignments.empty:
        raise ValueError("SRM cannot be evaluated on an empty assignment set")
    counts = assignments["arm"].value_counts().reindex(["control", "treatment"], fill_value=0).to_numpy()
    result = stats.chisquare(
        f_obs=counts,
        f_exp=[counts.sum() * (1 - expected_treatment_share), counts.sum() * expected_treatment_share],
    )
    return float(result.pvalue)

def welch_effect(outcomes: pd.DataFrame, metric: str) -> dict[str, float]:
    c = outcomes.loc[outcomes["arm"].eq("control"), metric].astype(float).to_numpy()
    t = outcomes.loc[outcomes["arm"].eq("treatment"), metric].astype(float).to_numpy()
    test = stats.ttest_ind(t, c, equal_var=False)
    var_c, var_t = c.var(ddof=1), t.var(ddof=1)
    a, b = var_c / len(c), var_t / len(t)
    se = math.sqrt(a + b)
    df = (a + b) ** 2 / (a * a / (len(c) - 1) + b * b / (len(t) - 1))
    critical = stats.t.ppf(0.975, df)
    difference = float(t.mean() - c.mean())
    return {
        "control_mean": float(c.mean()),
        "treatment_mean": float(t.mean()),
        "difference": difference,
        "standard_error": float(se),
        "confidence_interval_95": (float(difference - critical * se), float(difference + critical * se)),
        "confidence_interval_width_95": float(2 * critical * se),
        "p_value": float(test.pvalue),
        "n_control": int(len(c)),
        "n_treatment": int(len(t)),
    }

def bootstrap_difference(outcomes: pd.DataFrame, metric: str, repetitions: int = BOOTSTRAP_REPETITIONS,
                        seed: int = SEED) -> tuple[float, float]:
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    rng = np.random.default_rng(seed)
    c = outcomes.loc[outcomes["arm"].eq("control"), metric].astype(float).to_numpy()
    t = outcomes.loc[outcomes["arm"].eq("treatment"), metric].astype(float).to_numpy()
    if len(c) == 0 or len(t) == 0:
        raise ValueError("both control and treatment must contain observations")
    estimates = np.empty(repetitions)
    for i in range(repetitions):
        estimates[i] = rng.choice(t, len(t), replace=True).mean() - rng.choice(c, len(c), replace=True).mean()
    low, high = np.quantile(estimates, [0.025, 0.975])
    return float(low), float(high)

def cuped_adjusted(outcomes: pd.DataFrame, metric: str, covariate: str = "pre_activity") -> pd.Series:
    """Use a pre-treatment covariate only; compute a common theta from pooled predeclared data."""
    y = outcomes[metric].astype(float)
    x = outcomes[covariate].astype(float)
    variance_x = x.var(ddof=1)
    if variance_x <= 0:
        return y.copy()
    theta = y.cov(x) / variance_x
    return y - theta * (x - x.mean())

def summarize(outcomes: pd.DataFrame, bootstrap_repetitions: int = BOOTSTRAP_REPETITIONS) -> dict:
    primary = welch_effect(outcomes, "converted_7d")
    bootstrap_ci = bootstrap_difference(
        outcomes, "converted_7d", repetitions=bootstrap_repetitions
    )
    primary["bootstrap_ci_95"] = bootstrap_ci
    primary["bootstrap_ci_width_95"] = float(bootstrap_ci[1] - bootstrap_ci[0])
    primary["bootstrap_to_welch_ci_width_ratio"] = float(
        primary["bootstrap_ci_width_95"] / primary["confidence_interval_width_95"]
    )
    outcomes = outcomes.copy()
    outcomes["revenue_proxy_cuped"] = cuped_adjusted(outcomes, "revenue_proxy")
    raw_rev = welch_effect(outcomes, "revenue_proxy")
    adjusted_rev = welch_effect(outcomes, "revenue_proxy_cuped")
    # Guardrails: compare error-rate difference and latency difference.
    error = welch_effect(outcomes, "checkout_error")
    latency = welch_effect(outcomes, "checkout_latency_ms")
    return {
        "primary_conversion": primary,
        "revenue_proxy_unadjusted": raw_rev,
        "revenue_proxy_cuped": adjusted_rev,
        "guardrail_error": error,
        "guardrail_latency_ms": latency,
    }

def recompute_daily(assignments: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Deterministic full recomputation for a frozen snapshot; idempotent by construction."""
    return build_user_outcomes(assignments, events).sort_values(
        ["experiment_id", "entity_id"]
    ).reset_index(drop=True)

def inject_assignment_bug(assignments: pd.DataFrame) -> pd.DataFrame:
    """Deliberately bias a subset of control assignments into treatment to test SRM alarm."""
    broken = assignments.copy()
    control_idx = broken.index[broken["arm"].eq("control")]
    n_flip = max(1, int(0.05 * len(control_idx)))
    broken.loc[control_idx[:n_flip], "arm"] = "treatment"
    return broken

def main() -> None:
    data = build_synthetic_experiment()
    assignments = data["assignments"]
    events = data["raw_events"]
    outcomes = recompute_daily(assignments, events)

    # Core grain, eligibility, deduplication, and determinism assertions.
    assert len(assignments) == assignments["entity_id"].nunique()
    assert not assignments["entity_id"].duplicated().any()
    assert set(assignments["arm"].unique()) == {"control", "treatment"}
    assert assignments["entity_id"].map(assign_arm).equals(assignments["arm"])
    assert len(outcomes) == len(assignments)
    assert not outcomes["entity_id"].duplicated().any()
    assert outcomes["converted_7d"].isin([0, 1]).all()
    assert len(deduplicate_events(events)) <= len(events)

    p_srm = srm_pvalue(assignments)
    bugged = inject_assignment_bug(assignments)
    p_srm_bug = srm_pvalue(bugged)
    assert p_srm > 0.001, "Unexpected SRM in nominal assignment; investigate hash/eligibility."
    # This threshold is deliberately robust to smaller smoke-test sizes too.
    # At the default 500,000-user scale, the same defect should be much more significant.
    assert p_srm_bug < 0.001, "Injected allocation bug was not detected by SRM check."

    report = summarize(outcomes)
    # The true DGP uses 10.0% control and 10.2% treatment probabilities.
    # Estimate need not equal truth, and significance is not guaranteed by one run.
    observed_relative_lift = (
        report["primary_conversion"]["treatment_mean"] /
        report["primary_conversion"]["control_mean"] - 1
    )
    report["primary_conversion"]["observed_relative_lift"] = observed_relative_lift
    report["srm_p_value"] = p_srm
    report["srm_p_value_after_injected_bug"] = p_srm_bug
    report["assigned_users_never_exposed"] = int(len(assignments) - len(data["exposures"]))
    report["eligible_assigned_users"] = int(len(assignments))
    exposure_counts = (
        data["exposures"].groupby("arm")["entity_id"].nunique()
        .reindex(["control", "treatment"], fill_value=0)
    )
    assignment_counts = assignments["arm"].value_counts().reindex(
        ["control", "treatment"], fill_value=0
    )
    report["exposure_rate_by_arm"] = {
        arm: float(exposure_counts[arm] / assignment_counts[arm])
        for arm in ["control", "treatment"]
    }
    report["raw_event_rows"] = int(len(events))
    report["deduplicated_event_rows"] = int(len(deduplicate_events(events)))
    print(report)

    # Exposure is a post-assignment diagnostic; it must retain the assigned arm.
    exposure_check = data["exposures"].merge(
        assignments[["experiment_id", "entity_id", "arm", "assigned_at"]],
        on=["experiment_id", "entity_id"], how="left", suffixes=("_exposure", "_assignment"),
        validate="many_to_one",
    )
    assert exposure_check["arm_exposure"].eq(exposure_check["arm_assignment"]).all()
    assert (exposure_check["exposed_at"] >= exposure_check["assigned_at"]).all()

    # Idempotency: same frozen inputs should yield the same row-level output.
    again = recompute_daily(assignments, events)
    pd.testing.assert_frame_equal(outcomes, again)

    # Guardrail decision thresholds are illustrative and must be agreed before a real experiment.
    # Do not claim a guardrail passed merely because its p-value is non-significant.
    error_harm = report["guardrail_error"]["difference"]
    latency_harm = report["guardrail_latency_ms"]["difference"]
    guardrail_error_threshold = 0.005  # max +0.5 percentage points absolute
    guardrail_latency_threshold_ms = 10.0
    guardrails_within_point_thresholds = (
        error_harm < guardrail_error_threshold and latency_harm < guardrail_latency_threshold_ms
    )
    print({
        "guardrail_error_difference": error_harm,
        "guardrail_latency_difference_ms": latency_harm,
        "guardrails_within_point_thresholds": guardrails_within_point_thresholds,
        "note": "Production decisions should use predeclared uncertainty-aware guardrail rules.",
    })

if __name__ == "__main__":
    main()
```

#### Important lab interpretation notes

1. The planted conversion probabilities are 10.0% and 10.2%, so the relative lift is \((0.102-0.100)/0.100=0.02=2\%\). The observed sample estimate fluctuates.
2. The example marks bots ineligible before assignment and keeps their events in raw data to test exclusion. Do not remove bots post-treatment if treatment can change the bot classification.
3. Exposure is deliberately not used to filter the primary ITT population. Compute exposure rates by arm as a diagnostic.
4. The `revenue_proxy` outcome is a continuous secondary outcome designed to demonstrate CUPED, not an order-revenue business metric. CUPED is compared on this outcome because its pre-treatment covariate is correlated with it.
5. The lab's point-threshold guardrail rule is illustrative. Production guardrail decisions should use predeclared uncertainty-aware rules (for example, a confidence bound against a non-inferiority margin), not merely a non-significant test.
6. The full lab can consume memory because it materializes several 500,000-row pandas tables. If memory is constrained, generate/ingest in chunks and use DuckDB for storage and aggregation. Do not silently reduce the user count and call it the 500,000-user run.

### 11.3 DuckDB SQL implementation

The Python lab is the canonical reproducible generator. Persist the returned DataFrames to DuckDB and build the same analysis grain with SQL:

```python
import duckdb

data = build_synthetic_experiment()
con = duckdb.connect("ab_experiment_lab.duckdb")
con.register("assignments_df", data["assignments"])
con.register("events_df", data["raw_events"])
con.register("exposures_df", data["exposures"])

# Persist only assignment-time fields in the assignment table. Outcomes remain in raw_events.
con.execute("""
CREATE OR REPLACE TABLE experiment_assignments AS
SELECT experiment_id, config_version, entity_id, arm, assigned_at, pre_activity
FROM assignments_df
""")
con.execute("CREATE OR REPLACE TABLE raw_events AS SELECT * FROM events_df")
con.execute("CREATE OR REPLACE TABLE experiment_exposures AS SELECT * FROM exposures_df")
con.execute("""
CREATE OR REPLACE TABLE experiment_config AS
SELECT 'checkout_simplification_v1' AS experiment_id,
       1 AS config_version,
       TIMESTAMPTZ '2026-09-01 00:00:00+00' AS window_start,
       TIMESTAMPTZ '2026-09-08 00:00:00+00' AS window_end,
       TIMESTAMPTZ '2026-09-04 00:00:00+00' AS analysis_cutoff_at
""")

# Apply both event-time eligibility and ingestion cutoff from the frozen config.
# The selected config row and cutoffs are part of the reproducible analysis snapshot.
con.execute("""
CREATE OR REPLACE TABLE user_daily_metrics AS
WITH dedup AS (
    SELECT * EXCLUDE (rn)
    FROM (
        SELECT e.*, row_number() OVER (
            PARTITION BY e.event_id ORDER BY e.ingested_at DESC
        ) AS rn
        FROM raw_events e
        JOIN experiment_config c USING (experiment_id)
        WHERE e.ingested_at <= c.analysis_cutoff_at
    )
    WHERE rn = 1
)
SELECT d.experiment_id, d.entity_id, CAST(d.event_ts AS DATE) AS metric_date,
       max(d.converted_7d) AS converted_7d,
       max(d.checkout_error) AS checkout_error,
       avg(d.checkout_latency_ms) AS checkout_latency_ms,
       avg(d.revenue_proxy) AS revenue_proxy
FROM dedup d
JOIN experiment_config c USING (experiment_id)
WHERE coalesce(d.is_bot, false) = false
  AND d.event_ts >= c.window_start
  AND d.event_ts < c.window_end
GROUP BY d.experiment_id, d.entity_id, CAST(d.event_ts AS DATE)
""")

con.execute("""
CREATE OR REPLACE TABLE experiment_user_outcomes AS
WITH dedup AS (
    SELECT * EXCLUDE (rn)
    FROM (
        SELECT e.*, row_number() OVER (
            PARTITION BY e.event_id ORDER BY e.ingested_at DESC
        ) AS rn
        FROM raw_events e
        JOIN experiment_config c USING (experiment_id)
        WHERE e.ingested_at <= c.analysis_cutoff_at
    )
    WHERE rn = 1
),
agg AS (
    SELECT d.experiment_id, d.entity_id,
           max(d.converted_7d) AS converted_7d,
           max(d.checkout_error) AS checkout_error,
           avg(d.checkout_latency_ms) AS checkout_latency_ms,
           avg(d.revenue_proxy) AS revenue_proxy
    FROM dedup d
    JOIN experiment_config c USING (experiment_id)
    WHERE coalesce(d.is_bot, false) = false
      AND d.event_ts >= c.window_start
      AND d.event_ts < c.window_end
    GROUP BY d.experiment_id, d.entity_id
)
SELECT a.experiment_id, a.config_version, a.entity_id, a.arm, a.assigned_at,
       a.pre_activity,
       coalesce(e.converted_7d, 0) AS converted_7d,
       coalesce(e.checkout_error, 0) AS checkout_error,
       e.checkout_latency_ms,
       coalesce(e.revenue_proxy, 0.0) AS revenue_proxy
FROM experiment_assignments a
LEFT JOIN agg e USING (experiment_id, entity_id)
JOIN experiment_config c
  ON a.experiment_id = c.experiment_id
 AND a.config_version = c.config_version
""")
# Validate grain before using the table.
assert con.execute("""
    SELECT count(*) = count(DISTINCT entity_id)
    FROM experiment_user_outcomes
""").fetchone()[0]

# Persist the analysis outputs as a versioned results table.
sql_outcomes = con.execute("SELECT * FROM experiment_user_outcomes").df()
result_summary = summarize(sql_outcomes, bootstrap_repetitions=100)
rows = []
for metric_name, metric_result in result_summary.items():
    ci = metric_result.get("confidence_interval_95", (None, None))
    bootstrap_ci = metric_result.get("bootstrap_ci_95", (None, None))
    rows.append({
        "experiment_id": EXPERIMENT_ID,
        "analysis_version": 1,
        "metric_name": metric_name,
        "control_mean": metric_result["control_mean"],
        "treatment_mean": metric_result["treatment_mean"],
        "difference": metric_result["difference"],
        "ci_low": ci[0],
        "ci_high": ci[1],
        "bootstrap_ci_low": bootstrap_ci[0],
        "bootstrap_ci_high": bootstrap_ci[1],
        "bootstrap_ci_width": metric_result.get("bootstrap_ci_width_95"),
        "bootstrap_to_welch_ci_width_ratio": metric_result.get("bootstrap_to_welch_ci_width_ratio"),
        "p_value": metric_result["p_value"],
        "source_cutoff": "2026-09-04T00:00:00Z",
    })
results_df = pd.DataFrame(rows)
con.register("results_df", results_df)
con.execute("CREATE OR REPLACE TABLE experiment_results AS SELECT * FROM results_df")
assert con.execute("SELECT count(*) FROM experiment_results").fetchone()[0] == len(rows)
```

The synthetic events use a single event date, so the daily table has one date per eligible entity in this simplified lab. The SQL applies the configured event-time window and ingestion cutoff even though all generated events fall within them. Real pipelines group multiple dates and then aggregate the eligible metric window into one analysis row per randomized entity. The Python generator carries outcomes in the assignment DataFrame as a convenience for the local lab; the DuckDB tables deliberately separate assignment-time fields from event-derived outcomes. In production, never store outcomes as assignment attributes. As above, do not interpret an absent outcome as zero until source completeness and window maturity have been validated. When replacing a table in a production dbt pipeline, use a versioned model and controlled snapshot/cutoff instead of destructive ad hoc updates.

### 11.4 SRM with an injected bug

The Python lab flips 5% of control assignments to treatment. That changes the observed ratio by design and should trigger the SRM assertion. In a production pipeline, investigate the root cause rather than automatically “fixing” the observed allocation. Potential causes include:

- assignment SDK or hash version mismatch;
- a changed identifier or inconsistent canonicalization;
- eligibility computed differently in assignment and reporting;
- assignment logging loss or duplicated entities;
- treatment-dependent exposure filters mistakenly used for assignment counts;
- sample inclusion rules applied after assignment.

An SRM check should be run on the correct assignment grain, using expected proportions from the saved experiment configuration and a clearly defined eligible population.

## 12. Idempotency, late events, and operational reliability

### 12.1 Idempotent recomputation

An idempotent pipeline produces the same result for the same frozen inputs and configuration, regardless of retries. Common patterns:

- deduplicate by stable source event ID;
- use deterministic transformations;
- partition by experiment and event/metric date;
- merge/upsert by stable primary key rather than blindly append;
- version the metric definition and experiment configuration;
- record analysis cutoff, source snapshot, code commit, and package versions;
- publish a result only after validation passes.

Idempotency does not mean outputs never change. A late event, identity correction, or source backfill can legitimately change the result when the input snapshot changes. That change should produce a new result version with lineage, not silently mutate an already published result.

### 12.2 Late-arriving events and grace periods

Use event time for the outcome window and ingestion time for freshness/backfill controls. Choose a late-arrival grace period based on the source's latency distribution. At cutoff:

1. mark results provisional while data are incomplete;
2. monitor lag and missing partitions;
3. freeze the event-time window and ingestion cutoff;
4. recompute after the grace period or a documented correction;
5. publish a new version if the result changes.

Do not extend the treatment outcome window differently for users who converted late. That would create unequal measurement opportunities.

### 12.3 Identity stitching

Cross-device identity resolution can change the apparent number of randomized units and can put one person in both arms. Decide whether assignment occurs on account, user, device, or another stable entity. Preserve the identity-map version and validity timestamps. Monitor:

- entities mapped to multiple assignments;
- cross-arm identity collisions;
- reassignment after login;
- merge/split events and their effect on historical cohorts.

Do not use future identity information without documenting its effect on the estimand and reproducibility.

### 12.4 Monitoring and alert severity

| Check | Example signal | Response |
|---|---|---|
| Assignment integrity | duplicate key, invalid arm, SRM | Pause interpretation; inspect config, SDK, and eligibility |
| Exposure integrity | arm mismatch, sudden exposure-rate change | Inspect client/server delivery and logging |
| Event freshness | delayed partitions or ingestion lag | Mark results provisional; delay finalization |
| Metric integrity | denominator collapse, revenue spike, missing outcomes | Reconcile sources and semantic definitions |
| Guardrails | error or latency threshold crossed | Follow predeclared safety stop policy |
| Result reproducibility | same snapshot produces different output | Investigate nondeterminism, mutable inputs, and code/config drift |

## 13. Testing and result verification

A robust test suite separates unit tests, data-quality tests, statistical checks, and integration tests. The following is a runnable `pytest` test module named `test_ab_experiment_lab.py`; save the main lab as `ab_experiment_lab.py` and run `pytest -q`. Fixtures deliberately use a smaller dataset so the test suite stays fast; the full 500,000-user run remains a separate integration exercise.

### 13.1 Unit and data-grain tests

```python
import pandas as pd
import pytest

from ab_experiment_lab import (
    SEED,
    assign_arm,
    build_synthetic_experiment,
    build_user_outcomes,
    deduplicate_events,
    recompute_daily,
    srm_pvalue,
    stable_bucket,
)

@pytest.fixture(scope="module")
def data():
    return build_synthetic_experiment(n_users=10_000, seed=SEED)

@pytest.fixture(scope="module")
def assignments(data):
    return data["assignments"]

@pytest.fixture(scope="module")
def events(data):
    return data["raw_events"]

def test_assignment_is_deterministic():
    assert assign_arm("user-1") == assign_arm("user-1")
    assert stable_bucket("exp", "user-1") == stable_bucket("exp", "user-1")

def test_srm_flags_injected_bug():
    sample = pd.DataFrame({
        "entity_id": [f"u{i}" for i in range(1000)],
        "arm": ["control"] * 500 + ["treatment"] * 500,
    })
    broken = sample.copy()
    broken.loc[:99, "arm"] = "treatment"
    assert srm_pvalue(sample) > 0.05
    assert srm_pvalue(broken) < 0.001

def test_recompute_is_idempotent(assignments, events):
    first = recompute_daily(assignments, events)
    second = recompute_daily(assignments, events)
    pd.testing.assert_frame_equal(first, second)

def test_retry_events_are_deduplicated(events):
    deduped = deduplicate_events(events)
    assert deduped["event_id"].is_unique
    assert len(deduped) < len(events)

def test_exposure_matches_assignment(data):
    exposures = data["exposures"]
    assignments = data["assignments"]
    checked = exposures.merge(
        assignments[["experiment_id", "entity_id", "arm", "assigned_at"]],
        on=["experiment_id", "entity_id"], how="left", suffixes=("_exposure", "_assignment"),
        validate="many_to_one",
    )
    assert checked["arm_exposure"].eq(checked["arm_assignment"]).all()
    assert (checked["exposed_at"] >= checked["assigned_at"]).all()
    # An intentionally corrupted exposure must be detectable.
    corrupted = exposures.copy()
    corrupted.loc[corrupted.index[0], "arm"] = (
        "control" if corrupted.loc[corrupted.index[0], "arm"] == "treatment" else "treatment"
    )
    bad = corrupted.merge(
        assignments[["experiment_id", "entity_id", "arm"]],
        on=["experiment_id", "entity_id"], how="left", suffixes=("_exposure", "_assignment"),
        validate="many_to_one",
    )
    assert (~bad["arm_exposure"].eq(bad["arm_assignment"])).any()

def test_analysis_has_one_row_per_assigned_user(assignments, events):
    outcomes = build_user_outcomes(assignments, events)
    assert len(outcomes) == len(assignments)
    assert not outcomes["entity_id"].duplicated().any()
```

These tests validate the helper functions and generated data contract; they do not prove production source completeness, statistical power, or causal validity. Add warehouse integration tests against actual event-time windows, ingestion cutoffs, and identity-map versions.

For the synthetic dataset, validate the realized conversion estimate against a tolerance chosen from sampling variability, not an exact expected percentage. For example, check that the observed difference is within a broad interval around 0.002 or use a simulation-based test. A single run can miss conventional significance even when the true effect is positive.

### 13.2 Effect recovery and power

The true effect is the difference between data-generating probabilities: 0.102 − 0.100 = 0.002. The realized estimate is random. A correct test should have calibrated Type I error under a null simulation and useful power under the stated alternative; it should not be forced to return significance.

A stronger validation plan repeats the experiment over many seeds and checks:
- mean estimated difference approaches 0.002;
- the nominal confidence interval has approximately its intended repeated-sampling coverage;
- null simulations reject at approximately the chosen alpha;
- SRM bug injection is detected;
- outcome aggregation matches an independently computed reference;
- same frozen inputs and code produce identical results.

### 13.3 SQL checks

Examples of checks to materialize as dbt tests or pipeline assertions:

```sql
-- Unique analysis grain: expected zero rows.
SELECT experiment_id, entity_id, count(*) AS n
FROM experiment_user_outcomes
GROUP BY 1, 2
HAVING count(*) <> 1;

-- Assignment/exposure arm mismatch: expected zero rows.
SELECT e.experiment_id, e.entity_id
FROM experiment_exposures e
JOIN experiment_assignments a
  ON e.experiment_id = a.experiment_id
 AND e.entity_id = a.entity_id
WHERE e.arm <> a.arm;

-- Invalid conversion values: expected zero rows.
SELECT *
FROM experiment_user_outcomes
WHERE converted_7d NOT IN (0, 1) OR converted_7d IS NULL;
```

Adapt column names to the model. The expected result of a test query should be explicit; a query returning rows is a failure requiring investigation.

## 14. Exercises with solutions

### Exercise 1 — Design a checkout experiment

Specify unit, eligibility, primary metric, MDE, alpha, power, duration, two guardrails, and a decision rule.

**Solution sketch:** choose user-level assignment for persistent checkout experience; define eligible users before assignment; use conversion within seven days as primary metric; state a baseline and absolute/relative MDE; plan sample size with the previous lesson's power methods; cover weekly cycles and the outcome window; define error-rate and p95-latency guardrails; require a practically meaningful primary result and guardrails within predeclared harm bounds.

### Exercise 2 — Assignment algorithm

Why is Python's built-in `hash()` not appropriate for persistent cross-process assignment? What must remain stable?

**Solution sketch:** Python string hashes are randomized across processes by default and are not a cross-language assignment contract. Use a specified stable hash, canonical entity key, encoding, separator/length-prefix format, bucket count, seed/configuration, and threshold. Version the assignment algorithm; changing it mid-experiment can reassign units.

### Exercise 3 — ITT versus exposed-only

A treatment increases page load time, causing some assigned users to abandon before the exposure event fires. Why might exposed-only analysis be biased?

**Solution sketch:** exposure is post-assignment and treatment affects the probability of exposure being logged. Conditioning on exposure selects different kinds of users in the two arms and breaks the original randomized comparison. ITT includes all eligible randomized units according to assignment; exposure rate remains an important diagnostic.

### Exercise 4 — SRM diagnosis

An experiment expects 50/50 assignment but observes 52/48. List at least five possible causes and describe the first checks.

**Solution sketch:** hash/SDK version mismatch, eligibility mismatch, assignment logging loss, duplicate entity IDs, inconsistent identity stitching, exposure filtering, bot rules applied differently, or a genuine random imbalance. Check assignment grain and configuration, compute SRM using expected allocation, inspect eligibility/identity, then compare assignment decisions with logged assignments.

### Exercise 5 — Avoid SQL fan-out

An assignment table has one row per user; the event table has multiple purchase rows per user. What happens if you join them and count assignment rows after the join?

**Solution sketch:** users with multiple purchase events appear multiple times, inflating denominators or revenue. Deduplicate source events and aggregate outcomes to one row per randomized entity before joining assignments; left join so zero-outcome users remain in the ITT denominator.

### Exercise 6 — CUPED leakage

A covariate is measured during the experiment and is affected by treatment. Why is it unsafe for ordinary CUPED adjustment?

**Solution sketch:** it is post-treatment and can carry part of the treatment effect; adjustment may remove causal signal or introduce bias. Use pre-treatment covariates and document the feature window.

### Exercise 7 — Late events

A purchase occurs before the analysis window ends but is ingested two days after the initial result. How should the pipeline handle it?

**Solution sketch:** use event time to decide whether it belongs in the outcome window and ingestion time to determine whether it was present at the snapshot cutoff. Mark the result provisional or recompute after the grace period, publish a versioned result, and preserve the earlier snapshot for audit.

## 15. Production pitfalls and common mistakes

1. Assigning by device but analyzing by account without resolving cross-arm identity.
2. Treating exposure as assignment or dropping assigned-but-unexposed units from ITT.
3. Defining eligibility after treatment when treatment can influence it.
4. Computing conversion from event rows instead of distinct randomized entities.
5. Joining assignments to raw events before aggregating and creating fan-out.
6. Summing per-user revenue incorrectly or changing refund/currency rules between arms.
7. Ignoring SRM or treating it as proof of one specific bug without investigation.
8. Filtering bots or internal traffic using a post-treatment rule.
9. Treating a non-significant guardrail test as proof of no harm.
10. Repeatedly checking ordinary p-values and stopping at significance.
11. Testing many segments and reporting only favourable ones.
12. Using post-treatment covariates in CUPED/CUPAC.
13. Letting late events rewrite published results without versioning.
14. Reassigning users after a traffic ramp or config change without preserving history.
15. Assuming a platform vendor guarantees metric correctness or causal validity.
16. Claiming the true effect must be statistically significant in every simulation.
17. Failing to document the source snapshot, metric version, query version, and analysis cutoff.
18. Using observational or quasi-experimental methods without stating their identifying assumptions.

## 16. Knowledge checkpoint

1. What is the difference between assignment, exposure, and outcome?
2. Why does randomization support causal interpretation, and what can still invalidate it?
3. How do you choose the randomization unit?
4. Why is ITT often the primary analysis?
5. What does SRM test, and why is it an alarm rather than a diagnosis?
6. What is the correct grain for conversion per randomized user?
7. How can a many-to-many join corrupt revenue per user?
8. Which covariates are safe for CUPED?
9. How do novelty, seasonality, interference, and Simpson's paradox affect interpretation?
10. How do you make a daily result recomputation idempotent and auditable?
11. What should happen when late events arrive after the result cutoff?
12. When might a bandit, difference-in-differences, synthetic control, or switchback design be more suitable than a conventional A/B test?

## 17. Final competency checklist

- [ ] I can write an experiment hypothesis and define a precise estimand.
- [ ] I can choose and justify the randomization unit.
- [ ] I can implement stable deterministic assignment and explain its versioning contract.
- [ ] I can distinguish assignment, exposure, and outcome, and explain ITT.
- [ ] I can design assignment, exposure, raw-event, identity, per-user metric, and results tables with explicit grains.
- [ ] I can define primary, secondary, guardrail, and diagnostic metrics consistently.
- [ ] I can implement SRM checks from configured allocation and investigate failures.
- [ ] I can write SQL that retains zero-outcome assigned users and avoids join fan-out.
- [ ] I can explain CUPED/CUPAC, stratification, sequential inference, segment multiplicity, and long-term holdouts.
- [ ] I can recognize novelty, primacy, seasonality, interference, network effects, Simpson's paradox, bots, and instrumentation bugs.
- [ ] I can design idempotent recomputation, late-event handling, identity stitching, and versioned publication.
- [ ] I can reproduce the synthetic lab and test the planted effect without promising significance.
- [ ] I can separate statistical evidence, data-quality evidence, and business decision criteria.

## 18. Authoritative references

Use documentation that matches the versions deployed in your environment.

- Analytics roadmap, Topic 04 — A/B testing and experiment data pipelines (the assigned module syllabus).
- SciPy statistical tests: <https://docs.scipy.org/doc/scipy/reference/stats.html>
- SciPy `ttest_ind`: <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html>
- statsmodels multiple testing: <https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html>
- DuckDB Python API: <https://duckdb.org/docs/stable/clients/python/overview>
- DuckDB SQL documentation: <https://duckdb.org/docs/stable/sql/introduction>
- dbt data tests: <https://docs.getdbt.com/docs/build/data-tests>
- NumPy random Generator: <https://numpy.org/doc/stable/reference/random/generator.html>
- Statsig experimentation documentation: <https://docs.statsig.com/>
- Optimizely experimentation documentation: <https://docs.developers.optimizely.com/>
- Eppo documentation: <https://docs.geteppo.com/>
- GrowthBook documentation: <https://docs.growthbook.io/>
- LaunchDarkly experimentation documentation: <https://docs.launchdarkly.com/home/experimentation>
- Deng, Xu, Kohavi, and Walker, “Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data”: <https://doi.org/10.1145/2433396.2433413>
- Kohavi, Tang, and Xu, *Trustworthy Online Controlled Experiments*: <https://experimentguide.com/>

---

**Completion criterion:** You are ready for the next roadmap lesson when you can design an experiment, implement and validate assignment/exposure/metric pipelines, investigate SRM, produce reproducible estimates and uncertainty, and explain what the evidence does—and does not—support.
