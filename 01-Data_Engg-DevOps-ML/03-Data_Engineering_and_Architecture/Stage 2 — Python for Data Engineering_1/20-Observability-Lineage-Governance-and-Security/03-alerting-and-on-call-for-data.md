# Module 2.20.03 — Alerting and On-Call for Data

> **Roadmap:** Stage 2 → Module 2.20 — Observability, Lineage, Governance, and Security  
> **Topic:** 03 — Alerting and On-Call for Data  
> **Level:** Beginner → Fundamentals → Practical → Advanced → Production  
> **Primary principle:** **Monitoring tells us what is happening; alerting tells us when someone needs to act.**

---

## Learning Objective

By the end of this module, you should be able to answer:

> **When should a data engineer be interrupted by an alert, what exactly should the alert mean, who should receive it, what should they do next, and how do we prevent alert fatigue?**

A production data platform is not healthy merely because jobs execute successfully. A pipeline can report `SUCCESS` while data is stale, incomplete, low-volume, invalid, expensive to produce, or delayed by streaming lag.

The operational chain this module teaches is:

```text
Signal
  ↓
Alert
  ↓
Routing
  ↓
On-call engineer
  ↓
Runbook
  ↓
Investigation
  ↓
Mitigation
  ↓
Validation
  ↓
Communication
  ↓
Alert improvement
```

---

# 1. Monitoring, Observability, Dashboards, Alerts, Reports, and Incidents

## 1.1 What is monitoring?

**Monitoring** is the systematic collection and presentation of signals that tell us whether a system is behaving as expected.

For a data platform, examples include:

- pipeline success/failure counts
- pipeline duration
- dataset freshness
- row volume
- null rate
- duplicate rate
- Kafka consumer lag
- retry counts
- warehouse query cost
- storage growth

Monitoring answers:

> **What is happening?**

Alerting answers a different question:

> **Does someone need to act now?**

## 1.2 What is observability?

Observability is the ability to understand the internal state of a system from its externally exposed telemetry and evidence.

In this module, alerting is one operational layer of the broader observability system.

A useful mental model is:

```text
Observability
├── Metrics
├── Logs
├── Traces
└── Operational context

Monitoring
└── Observe and visualize signals

Alerting
└── Decide when human action is required
```

## 1.3 Dashboard

A dashboard is an interactive view used to inspect current state, trends, and relationships.

Example:

```text
Daily orders pipeline
        ↓
Runs successfully
        ↓
Dashboard shows 10M rows
        ↓
No alert
```

The dashboard may be useful without requiring anyone to interrupt their work.

## 1.4 Alert

An alert is an operational signal that crosses a defined condition and requires a defined response.

```text
Daily orders pipeline
        ↓
Freshness exceeds SLO
        ↓
Alert
        ↓
Engineer investigates
```

An alert is therefore not simply a metric with a red color. It is an **action contract**.

## 1.5 Report

A report communicates status, trends, and analysis to stakeholders.

Example:

```text
Weekly pipeline reliability declined
from 99.2% to 98.4%.
```

This may require a management decision, but it normally does not require paging an on-call engineer immediately.

## 1.6 Incident

An incident is an operational event that materially affects reliability, consumers, data availability, data correctness, or another defined business/technical objective and requires coordinated response.

---

## Checkpoint

**Q1. Why is a dashboard not automatically an alert?**  
**Answer:** A dashboard supports observation and investigation; an alert represents a condition that requires a defined action.

**Q2. What is the core distinction between monitoring and alerting?**  
**Answer:** Monitoring tells us what is happening; alerting tells us when someone needs to act.

**Q3. Can a successful pipeline still produce an incident?**  
**Answer:** Yes. Technical execution success does not guarantee healthy, fresh, complete, or correct data.

---

# 2. Dashboards vs Alerts vs Reports

| Mechanism | Purpose | Audience | Action |
|---|---|---|---|
| Dashboard | Explore current state | Engineers/operators | Investigate |
| Alert | Demand attention | On-call | Act |
| Report | Communicate status/trends | Stakeholders | Understand/decide |

### Dashboard-only signal

```text
Pipeline duration
```

A duration trend can be valuable without paging anyone every time it changes.

### Alert-worthy signal

```text
Critical orders_gold freshness SLO breached.
```

This represents an operational condition with consumer impact.

### Report-worthy signal

```text
Weekly pipeline reliability declined from 99.2% to 98.4%.
```

The trend may drive engineering prioritization rather than immediate incident response.

### Why everything should not become an alert

If every metric produces a notification:

```text
1000 metrics
   ↓
1000 notifications
   ↓
engineers ignore notifications
   ↓
important page gets missed
```

A mature alerting system deliberately converts only high-value operational conditions into alerts.

---

# 3. What Makes a Good Alert?

A good production alert is:

- **Actionable**
- **Specific**
- **Timely**
- **Owned**
- **Prioritized**
- **Understandable**
- **Linked to evidence**
- **Linked to a runbook**
- **Connected to affected consumers**
- **Appropriate for its severity**

Bad:

```text
Pipeline unhealthy!!!
```

Better:

```text
CRITICAL: orders_gold freshness SLO breached for 18 minutes.

Affected consumer: Finance dashboard
Owner: Data Platform
Environment: production
Current freshness: 78 minutes
SLO: ≤ 60 minutes

Runbook: freshness investigation
Dashboard: pipeline health
```

The second alert tells the engineer what happened, why it matters, where to investigate, and what operational context is relevant.

### Alert design template

```text
Condition
  ↓
Meaning
  ↓
Impact
  ↓
Owner
  ↓
Severity
  ↓
Evidence
  ↓
Runbook
  ↓
Expected action
```

---

## Checkpoint

1. **Why should an alert have an owner?**  
   Without ownership, notification does not translate reliably into action.

2. **Why link a runbook?**  
   The engineer should not have to reconstruct the response procedure during an incident.

3. **Why include consumer impact?**  
   Impact determines urgency and prevents the alert from becoming an isolated infrastructure metric.

---

# 4. Symptom-Based vs Cause-Based Alerts

This is one of the most important alerting design decisions.

## 4.1 Cause-based alert

```text
Kafka broker CPU > 80%
```

This may be useful diagnostic information, but high CPU does not necessarily mean consumers are affected.

## 4.2 Symptom-based alert

```text
Critical consumer lag is causing
a downstream data freshness SLO breach.
```

This is closer to consumer impact.

### Why symptom-based paging is often stronger

Suppose:

```text
Kafka broker CPU = 85%
```

but:

```text
Consumer lag = normal
Freshness = normal
Consumers = unaffected
```

Paging may be unnecessary.

Now:

```text
Consumer lag ↑
       ↓
Processing delay ↑
       ↓
Freshness SLO breached
```

The downstream symptom represents an actual reliability problem.

### Important nuance

Cause-based alerts still matter for:

- diagnosis
- capacity management
- early warning
- infrastructure ownership
- known failure mechanisms

The principle is not:

> Never alert on causes.

It is:

> **Primary paging should generally represent meaningful impact where appropriate; supporting cause signals should help explain the incident.**

---

# 5. Alert Taxonomy for Data Pipelines

Every alert should define:

1. Signal
2. Threshold/condition
3. Severity
4. Owner
5. Expected action

## 5.1 Availability

Examples:

- pipeline failure
- DAG failure
- service unavailable

```text
Signal: pipeline_failures_total
Condition: failures increased
Severity: based on data tier and impact
Owner: pipeline owner
Action: investigate failure and recover
```

## 5.2 Freshness

Examples:

- dataset stale
- delivery deadline missed

```text
freshness_seconds > allowed_threshold
```

## 5.3 Volume

Examples:

- unexpectedly low volume
- unexpectedly high volume
- deviation from historical baseline

## 5.4 Data quality

Examples:

- null-rate threshold breached
- duplicate-rate threshold breached
- invalid records
- quarantine spike
- schema violations
- reconciliation failure
- business-rule failure

## 5.5 Streaming

Examples:

- consumer lag
- processing delay

## 5.6 Reliability

Examples:

- excessive retries
- repeated failures
- long-running pipeline

## 5.7 Cost

Examples:

- warehouse query-cost spike
- Spark compute spike
- unexpected cloud resource usage
- storage growth

## 5.8 Security/governance where relevant

Examples:

- access failure
- policy violation
- sensitive-data detection

Not every security or governance event belongs in the same paging channel; severity and ownership must be explicit.

---

# 6. Prometheus Alerting Fundamentals

Prometheus provides metrics collection/querying and alert-rule evaluation. Alertmanager handles downstream alert management such as routing, grouping, inhibition, and silencing.

Do not begin by memorizing YAML. First understand the conceptual flow:

```text
Metric
  ↓
PromQL expression
  ↓
Condition becomes true
  ↓
Alert rule
  ↓
Alert state
  ↓
Alertmanager
```

## 6.1 Core concepts

- **Metric:** numerical telemetry representing system state or activity.
- **PromQL:** Prometheus Query Language.
- **Alert rule:** a rule that turns a query condition into an alert.
- **Threshold:** a boundary used by a condition.
- **`for`:** requires a condition to remain true for a duration before firing.
- **Labels:** structured metadata used for classification and routing.
- **Annotations:** human-readable alert information.

## 6.2 Basic rule

```yaml
groups:
  - name: pipeline-alerts
    rules:
      - alert: PipelineFailure
        expr: increase(pipeline_failures_total[10m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pipeline failure detected"
          description: "A production pipeline has failed."
```

### Line-by-line interpretation

```yaml
groups:
```

Organizes alert rules.

```yaml
- name: pipeline-alerts
```

Names the rule group.

```yaml
alert: PipelineFailure
```

Defines the alert name.

```yaml
expr: increase(pipeline_failures_total[10m]) > 0
```

Evaluates whether the failure counter increased during the last ten minutes.

```yaml
for: 5m
```

Requires the condition to remain true for five minutes before firing.

```yaml
labels:
  severity: critical
```

Adds routing/metadata information.

```yaml
annotations:
  summary: ...
  description: ...
```

Provides operator-facing content.

> **Version note:** Prometheus configuration syntax and integrations can vary by version and deployment. Treat the conceptual model as stable and validate configuration against the version deployed by your organization.

---

# 7. PromQL for Data Engineering Alerts

The module only needs the PromQL concepts required to design meaningful pipeline alerts.

## 7.1 `increase()`

```promql
increase(pipeline_failures_total[10m]) > 0
```

Meaning:

> The counter increased during the last ten minutes.

This is useful for event counters such as pipeline failures.

## 7.2 `rate()`

```promql
rate(pipeline_failures_total[10m])
```

Meaning:

> Estimate the per-second rate of increase over the selected window.

This can help identify persistent failure rates or retry activity.

## 7.3 Comparisons

```promql
pipeline_freshness_seconds > 3600
```

A condition becomes true when freshness exceeds one hour.

## 7.4 Aggregation

```promql
sum(pipeline_failures_total)
```

```promql
avg(pipeline_duration_seconds)
```

```promql
max(pipeline_duration_seconds)
```

```promql
min(pipeline_rows)
```

Aggregation must be interpreted carefully: combining pipelines with different ownership, schedules, or data tiers can hide important distinctions.

## 7.5 Label filtering

```promql
pipeline_freshness_seconds{
  environment="production",
  data_tier="tier0"
}
```

This narrows the signal to production Tier 0 data.

## 7.6 Time windows

```promql
increase(pipeline_failures_total[10m])
```

The `[10m]` window changes what historical evidence is considered.

## 7.7 `for`

```yaml
for: 5m
```

A short transient condition can be prevented from immediately becoming a page.

### Trade-off

```text
Short `for`
→ faster detection
→ more sensitivity to transient conditions

Long `for`
→ fewer transient alerts
→ slower detection
```

---

## Checkpoint

1. **What does `increase()` help detect?**  
   Change in a counter over a time window.

2. **Why use `for`?**  
   To require persistence before firing and reduce transient noise.

3. **What are labels used for?**  
   Classification, filtering, routing, ownership, severity, and other structured metadata.

---

# 8. Freshness Alerts

Freshness is one of the most consumer-centric data reliability signals.

A useful conceptual definition is:

```text
freshness =
current_time - latest_successful_data_timestamp
```

Suppose:

```text
Current time: 07:30
Latest valid dataset timestamp: 06:15

Freshness = 75 minutes
```

If the SLO requires data within 60 minutes:

```text
75 minutes > 60-minute SLO
→ freshness alert
```

## 8.1 Pipeline success does not guarantee freshness

```text
Pipeline SUCCESS
      ↓
Job completed
      ↓
But upstream delivered stale data
      ↓
Dataset timestamp remains old
      ↓
Freshness SLO breached
```

This is why job success alone is insufficient.

## 8.2 Example metric

```promql
pipeline_freshness_seconds{
  environment="production",
  dataset="orders_gold"
} > 3600
```

A production implementation should account for schedule, expected delivery windows, dataset-specific SLOs, maintenance periods, and data-tier criticality.

## 8.3 Freshness design questions

Before paging, ask:

- What is the expected delivery time?
- What is the freshness SLO?
- Is the dataset critical?
- Is delayed data actually consumer-impacting?
- Is the delay expected during maintenance?
- Is the latest timestamp valid and trusted?
- Is upstream data itself late?
- Has the pipeline completed but published stale data?

---

# 9. Volume Alerts

Volume alerts detect unexpected changes in the amount of data.

Example:

```text
Today's rows = 2.1M
Expected = 10M ± 20%
```

Expected lower bound:

```text
10M × 0.80 = 8M
```

Therefore:

```text
rows < 8M
→ potential incident
```

## 9.1 Absolute thresholds

```text
rows < 1,000,000
```

Simple but often brittle.

## 9.2 Relative thresholds

```text
today / expected < 0.80
```

Useful when expected volume is known.

## 9.3 Historical baselines

For seasonal pipelines, Monday may legitimately differ from Sunday.

A better model might compare the current value against comparable historical periods.

```text
Current Monday
     ↓
Compare with historical Mondays
     ↓
Expected range
     ↓
Alert only on meaningful deviation
```

## 9.4 Why static thresholds can fail

```text
Static threshold = 8M
```

If normal traffic grows to 15M, the threshold becomes too permissive.

If a weekend normally contains 3M rows, the threshold becomes noisy.

---

# 10. Data Quality Alerts

Data quality alert candidates include:

- null rate
- duplicate rate
- invalid records
- quarantine volume
- schema violations
- reconciliation failures
- business-rule failures

Example:

```text
null_rate(customer_id) > 2%
```

But a failed quality check is not automatically a page.

## 10.1 Quality failure vs paging

```text
Quality check failed
        ↓
Classify impact
        ↓
Can consumers safely use the data?
        ↓
Severity decision
```

Possible outcomes:

```text
INFO/WARNING
→ record the issue and investigate during business hours

CRITICAL
→ page if consumers are materially affected or the data is unsafe
```

A quality threshold should be connected to:

- data tier
- consumer impact
- business rules
- recoverability
- data correctness risk
- downstream behavior

---

# 11. Lag Alerts

Streaming pipelines add another important dimension.

```text
Kafka
  ↓
Consumer
  ↓
Processing
  ↓
Data product
```

## 11.1 Consumer lag

Consumer lag measures the distance between available stream data and what a consumer has processed.

High lag can lead to:

```text
lag ↑
  ↓
processing delay ↑
  ↓
data freshness ↓
  ↓
consumer impact
```

Conceptual example:

```promql
kafka_consumer_lag_seconds > threshold
```

Actual metric names vary by Kafka exporter, platform, and deployment.

## 11.2 Lag is not always an incident

If:

```text
lag = 5 minutes
```

and the SLO allows:

```text
lag < 30 minutes
```

paging is likely unnecessary.

If:

```text
lag = 45 minutes
SLO = 30 minutes
Tier = 0
```

then the consumer-facing impact may justify a page.

---

# 12. Retry and Failure Alerts

Distinguish:

```text
one transient failure
```

from:

```text
pipeline failed 7 times in 20 minutes
```

The first may be recoverable noise.

The second may indicate:

- dependency outage
- authentication failure
- schema break
- code regression
- resource exhaustion
- retry storm

## 12.1 Retry storm

```text
Dependency failure
      ↓
Retry
      ↓
Retry
      ↓
Retry
      ↓
More load
      ↓
Dependency remains unhealthy
```

Alerting should distinguish transient recovery from repeated operational failure.

Useful signals:

- retries per run
- retry rate
- retry exhaustion
- consecutive failures
- duration spent retrying

---

# 13. Cost Alerts

Data platforms have meaningful cost failure modes.

Examples:

- warehouse query cost spike
- Spark compute spike
- unexpected cloud resource usage
- storage growth

A useful design is:

```text
Cost metric
+
Expected baseline
+
Business context
```

Example:

```text
Tier 2 exploratory workload
→ 2× normal warehouse spend
→ warning

Tier 0 production pipeline
→ 2× normal spend while preserving freshness
→ investigate cost without compromising recovery
```

Cost alerts should not blindly optimize for lower cost. Reliability, correctness, and business impact are part of the decision.

---

# 14. Severity

Severity represents:

> **Impact + urgency + required response**

Example policy:

| Severity | Meaning | Response |
|---|---|---|
| INFO | Awareness | No immediate action |
| WARNING | Investigation needed | Business hours |
| CRITICAL | Consumer impact | Page on-call |

Exact names and response policies are organization-specific.

## 14.1 Severity is contextual

The same technical condition can have different severity:

```text
Same failure
   ├── Tier 0 revenue dataset → CRITICAL
   ├── Tier 1 customer analytics → HIGH/CRITICAL
   ├── Tier 2 internal analytics → WARNING
   └── Tier 3 experiment → INFO
```

Severity should not be assigned solely from how large a metric looks.

---

# 15. Data Tiers and Alert Priority

A useful conceptual classification:

```text
Tier 0:
Revenue / financial reporting

Tier 1:
Customer-facing analytics

Tier 2:
Internal analytics

Tier 3:
Experimental datasets
```

Therefore:

```text
Same technical failure
≠
Same operational severity
```

Example:

```text
Freshness = 90 minutes late

Tier 0:
→ page

Tier 2:
→ warning

Tier 3:
→ dashboard/report
```

The actual policy must reflect organizational SLOs and ownership.

---

# 16. Alertmanager

The conceptual architecture is:

```text
Prometheus
    ↓
Alert rules
    ↓
Alertmanager
    ├── Grouping
    ├── Routing
    ├── Inhibition
    └── Silencing
         ↓
     Notification
```

Prometheus answers:

> Which alert condition is active?

Alertmanager answers:

> How should active alerts be organized and delivered?

## 16.1 Routing

Route based on:

- severity
- team
- pipeline
- data tier
- environment
- service ownership

Conceptual policy:

```text
critical + production + tier0
        ↓
primary on-call

warning + production
        ↓
team channel

development
        ↓
no paging
```

## 16.2 Grouping

Suppose one dependency fails:

```text
Kafka unavailable
   ↓
Consumer lag
   ↓
Pipeline freshness breach
   ↓
Warehouse freshness alert
```

Without grouping:

```text
4 alerts
```

With grouping:

```text
1 correlated incident
```

Grouping reduces notification volume and gives the responder a coherent incident view.

## 16.3 Inhibition

Inhibition suppresses secondary notifications while a known root condition is active.

Example:

```text
Database unavailable
        ↓
Inhibit:
  warehouse query failures
  pipeline failures
  consumer failures
```

Important:

> **Inhibition is not the same as ignoring failures.**

The purpose is to reduce duplicate symptoms while preserving useful information for investigation.

## 16.4 Silencing

A silence temporarily suppresses matching alerts.

Appropriate uses include:

- planned maintenance
- controlled incident investigation
- temporary known condition

A silence should have:

- reason
- owner
- scope
- start time
- expiration

Never treat:

```text
Silence
```

as:

```text
Fix
```

Permanent silences are dangerous because they can hide future incidents.

---

# 17. Actionable Alert Content

A production alert should answer:

1. What happened?
2. When?
3. How severe?
4. What is affected?
5. Who owns it?
6. What should I do?
7. Where is the evidence?
8. Where is the runbook?
9. What consumers are affected?

Example:

```text
ALERT: RevenueDatasetFreshnessBreach
Severity: CRITICAL
Pipeline: revenue_daily
Dataset: revenue_gold
Environment: production
Started: 06:45
Duration: 18m

Affected consumers:
Finance dashboard, revenue reporting

Current freshness: 78m
Expected/SLO: ≤ 60m

Owner: Data Platform
Runbook: Freshness investigation
Dashboard: Pipeline health
Run/trace information: attached via safe operational identifiers
```

Do not place secrets, credentials, tokens, or unnecessary sensitive data in alerts.

---

# 18. Runbooks

A runbook is an operational procedure that tells a responder how to interpret and safely respond to a known alert.

A strong runbook structure:

```text
1. Alert meaning
2. Impact
3. First checks
4. Dashboard
5. Logs
6. Trace/run metadata
7. Common causes
8. Safe recovery actions
9. Escalation
10. Validation
11. Communication
12. Post-incident actions
```

## 18.1 Sample runbook — Critical pipeline freshness breach

### Alert meaning

The dataset has exceeded its freshness SLO.

### Impact

Consumers may be viewing stale information.

### First checks

```text
1. Confirm alert is active.
2. Check dataset's latest valid timestamp.
3. Check pipeline run status.
4. Check upstream delivery.
5. Check warehouse processing time.
6. Check retries/failures.
7. Check known maintenance.
```

### Dashboard

Inspect:

- pipeline duration
- latest successful run
- freshness
- row volume
- retry count
- dependency health

### Logs

Look for:

- authentication errors
- schema errors
- warehouse timeouts
- upstream failures
- resource exhaustion

### Trace/run metadata

Use the relevant run/trace identifiers to correlate the alert with the affected execution.

### Common causes

- upstream data late
- warehouse load slow
- pipeline retry exhaustion
- dependency outage
- code regression

### Safe recovery actions

Only perform documented, reversible actions.

Examples:

- retry a failed stage
- restart a safe consumer
- trigger an approved backfill
- escalate when recovery is unsafe

### Escalation

Escalate when:

- no progress
- consumer impact increasing
- data-loss risk
- security implications
- compliance implications
- recovery blocked

### Validation

Do not declare recovery merely because a task turns green.

Verify:

```text
latest valid timestamp
+
quality checks
+
consumer-visible freshness
```

### Communication

Publish:

- impact
- current status
- next update
- credible ETA if known
- workaround if available

---

# 19. Alert → Runbook → Response

```text
Signal
 ↓
Alert
 ↓
Routing
 ↓
On-call engineer
 ↓
Runbook
 ↓
Investigation
 ↓
Mitigation
 ↓
Validation
 ↓
Communication
```

Every step has a purpose:

| Stage | Purpose |
|---|---|
| Signal | Observe a measurable condition |
| Alert | Identify actionable risk/impact |
| Routing | Deliver to the correct owner |
| On-call | Establish responsibility |
| Runbook | Reduce cognitive load |
| Investigation | Identify symptoms and causes |
| Mitigation | Restore reliability safely |
| Validation | Confirm consumer-visible recovery |
| Communication | Keep stakeholders aligned |

---

# 20. SLI and SLO for Alerting

## SLI

An SLI is what we measure.

Example:

```text
Dataset freshness
```

## SLO

An SLO defines the desired reliability level.

Example:

```text
99% of daily data available by 07:00
```

## Alert

An alert detects that the reliability objective is at risk or breached.

```text
SLI:
Dataset freshness

SLO:
99% of daily data available by 07:00

Alert:
Freshness SLO burn rate is dangerously high
```

Alerting should increasingly be tied to reliability objectives rather than arbitrary raw thresholds.

---

# 21. Error Budgets

An error budget is the amount of unreliability allowed by an SLO.

If:

```text
SLO = 99.9%
```

then:

```text
Error budget = 0.1%
```

For data engineering, the concept can be applied to:

- freshness
- successful delivery
- pipeline reliability
- consumer-visible availability

Example:

```text
SLO:
99% of scheduled deliveries meet freshness objective

Error budget:
1% of deliveries may miss the objective
```

The error budget influences:

- engineering priorities
- reliability work
- release decisions
- alerting strategy

If a team repeatedly consumes its budget, reliability work may need to take priority over additional feature work.

---

# 22. Burn Rate

Burn rate measures how quickly the system is consuming its allowed error budget.

Conceptually:

```text
SLO = 99%
Error budget = 1%

Recent failures are consuming
the budget much faster than sustainable.
```

A high burn rate means:

```text
Current reliability problem
        ↓
Budget being consumed rapidly
        ↓
Potential SLO failure
```

Burn-rate alerting can detect serious incidents before waiting for the entire SLO window to be exhausted.

---

# 23. Burn-Rate Alert Design

A robust design conceptually uses multiple windows:

```text
Short window
→ fast detection

Longer window
→ confirmation / sustained impact
```

This helps balance:

```text
fast detection
vs
false positives
```

For data platforms, adapt the concept to:

- freshness
- delivery reliability
- streaming delay

Do not blindly copy a generic web-service alert.

### Example reasoning

Suppose a Tier 0 dataset has a freshness SLO.

```text
Short-window burn rate very high
+
Longer-window burn rate also high
        ↓
Strong evidence of sustained consumer impact
        ↓
Page
```

A brief isolated spike may not justify the same response.

---

# 24. Alert Fatigue

Alert fatigue occurs when engineers receive so many alerts that important alerts are ignored.

Common causes:

- too many alerts
- poor thresholds
- duplicate alerts
- non-actionable alerts
- no ownership
- wrong severity
- cause and symptom alerts paging simultaneously
- development alerts paging production engineers

The goal is not:

> Zero alerts.

The goal is:

> **High-value alerts that reliably trigger useful action.**

---

# 25. Alert Precision

A useful operational measure is:

```text
precision =
useful/actionable alerts ÷ total alerts
```

For example:

```text
100 alerts
40 actionable
```

gives:

```text
precision = 40%
```

This is only one quality measure.

Also consider:

- false positives
- false negatives
- page volume
- duplicate incidents
- time-to-detect
- time-to-acknowledge
- time-to-recover
- consumer impact detected

There is a fundamental trade-off:

```text
More sensitivity
→ potentially faster detection
→ potentially more noise

Less sensitivity
→ fewer pages
→ potentially missed incidents
```

---

# 26. Alert Volume

Monitor alerting itself.

Useful dimensions include:

- total alerts
- pages
- notifications
- duplicate incidents
- alerts per pipeline
- alerts per service
- alerts per team
- alerts by severity
- alerts by environment

A team should know whether an alerting change actually reduced operational load.

---

# 27. Alert Deduplication

Multiple notifications can represent one incident.

Example:

```text
Database failure
   ├── warehouse query failure
   ├── pipeline failure
   ├── retry alert
   ├── freshness alert
   └── downstream consumer alert
```

Without correlation:

```text
5 alerts
```

Operationally:

```text
1 root incident
```

Deduplication and grouping use common identity/fingerprint dimensions to reduce repeated notifications.

---

# 28. Alert Quality Review

Periodically review every important alert.

Ask:

1. Did someone act on it?
2. Was it actionable?
3. Was severity correct?
4. Was the threshold correct?
5. Was the owner correct?
6. Was the runbook useful?
7. Was it duplicate noise?
8. Should it be removed?
9. Should it become dashboard-only?
10. Did it detect actual consumer impact?

An alert that repeatedly fires without action is a candidate for redesign.

---

# 29. On-Call Fundamentals

On-call means an engineer is explicitly responsible for responding to operational alerts during a defined coverage period.

Data teams need on-call because production data products have:

- schedules
- freshness expectations
- consumers
- downstream dependencies
- financial/business impact
- streaming workloads
- operational failure modes

Typical roles:

```text
Primary on-call
       ↓
First responder

Secondary on-call
       ↓
Backup / escalation

Incident commander
       ↓
Coordinates complex incidents where appropriate
```

Being available is not the same as being responsible.

```text
Available
≠
Responsible for restoring reliability
```

---

# 30. On-Call Rotations

Engineering rotation design should consider:

- primary/secondary coverage
- rotation schedules
- handover
- escalation
- time zones
- follow-the-sun models
- coverage gaps
- fatigue management

The goal is predictable operational responsibility.

Avoid designing rotations where:

```text
No explicit owner
+
unclear escalation
+
frequent interruptions
```

becomes the normal operating model.

---

# 31. On-Call Handover

A practical handover checklist:

```text
[ ] Open incidents
[ ] Degraded pipelines
[ ] Known noisy alerts
[ ] Pending investigations
[ ] Maintenance
[ ] Scheduled jobs
[ ] Expected unusual traffic
[ ] Known dependencies
[ ] Escalation contacts
```

A good handover transfers **operational state**, not merely a calendar slot.

Poor handover:

```text
"Nothing major. Good luck."
```

Good handover:

```text
Revenue pipeline is healthy now.
One upstream source has intermittent 429s.
Freshness warning is currently suppressed until 08:00 maintenance ends.
If 429s exceed the documented threshold, remove the temporary mitigation
and escalate to the source owner.
```

---

# 32. Escalation

A conceptual escalation path:

```text
L1:
Primary on-call

L2:
Senior data/platform engineer

L3:
Service owner / infrastructure specialist

L4:
Incident leadership / security / business stakeholders where required
```

Escalate when:

- there is no progress
- consumer impact is increasing
- security implications appear
- data-loss risk exists
- compliance implications exist
- recovery is blocked

Escalation is not failure. It is an explicit reliability mechanism.

---

# 33. Stakeholder Communication

Technical responders need to communicate impact without inventing certainty.

Example:

```text
Incident:
Revenue dataset delayed.

Impact:
Finance dashboard is 35 minutes stale.

Status:
Pipeline investigation in progress.

Next update:
15 minutes.

Current hypothesis:
Warehouse load saturation.
```

Stakeholders generally need:

- impact
- scope
- status
- credible ETA
- next update
- workaround if available

Avoid:

```text
"Definitely fixed in 10 minutes."
```

when evidence does not support that claim.

Prefer:

```text
"We have identified warehouse load saturation as the current hypothesis.
The team is testing mitigation. Next update in 15 minutes."
```

---

# 34. Data Status Communication

"Pipeline failed" may be technically correct but operationally incomplete.

Useful consumer-facing states include:

```text
Fresh
Delayed
Partial
Unavailable
Backfilled
Validated
```

Example:

```text
Pipeline failed
```

versus:

```text
Revenue dataset delayed.
Current data is 35 minutes stale.
Last validated dataset is available at 06:10.
Backfill is in progress.
```

The second communicates actual data-product state.

---

# 35. Production Alert Architecture

A complete conceptual architecture:

```text
Pipeline
   ↓
Metrics
   ↓
Prometheus
   ↓
Alert Rules
   ↓
Alertmanager
   ├── Group
   ├── Route
   ├── Inhibit
   └── Silence
        ↓
      On-call
        ↓
      Runbook
        ↓
   Investigation
        ↓
     Recovery
        ↓
    Verification
        ↓
   Communication
```

Each layer has a distinct responsibility:

| Layer | Responsibility |
|---|---|
| Pipeline | Generate operational signals |
| Metrics | Represent measurable state |
| Prometheus | Query/evaluate alert rules |
| Alertmanager | Manage alert delivery |
| Routing | Choose destination |
| Grouping | Combine related alerts |
| Inhibition | Suppress secondary symptoms |
| Silence | Temporarily suppress known conditions |
| On-call | Own response |
| Runbook | Guide investigation/recovery |
| Verification | Prove recovery |
| Communication | Report impact/status |

---

# 36. Hands-On Alerting Lab

This lab is intentionally self-contained in this Markdown document.

Suggested local stack:

- Python
- Prometheus
- Alertmanager
- Grafana where useful
- Docker Compose where appropriate

The pipeline should emit conceptual metrics:

```text
pipeline_success
pipeline_failure
pipeline_duration
pipeline_freshness
pipeline_rows
pipeline_lag
pipeline_quarantine
```

## 36.1 Minimal Python metrics example

Using the Prometheus Python client:

```python
from prometheus_client import Counter, Gauge, start_http_server
import time

pipeline_success = Counter(
    "pipeline_success_total",
    "Number of successful pipeline runs",
)

pipeline_failure = Counter(
    "pipeline_failure_total",
    "Number of failed pipeline runs",
)

pipeline_duration = Gauge(
    "pipeline_duration_seconds",
    "Latest pipeline duration in seconds",
)

pipeline_freshness = Gauge(
    "pipeline_freshness_seconds",
    "Age of the latest valid dataset",
)

pipeline_rows = Gauge(
    "pipeline_rows",
    "Rows produced by the latest run",
)

pipeline_lag = Gauge(
    "pipeline_lag_seconds",
    "Current processing lag",
)

pipeline_quarantine = Gauge(
    "pipeline_quarantine_ratio",
    "Fraction of records quarantined",
)

start_http_server(8000)

while True:
    try:
        started = time.time()

        # Replace this simulation with real pipeline work.
        time.sleep(2)

        duration = time.time() - started
        pipeline_duration.set(duration)
        pipeline_rows.set(10_000_000)
        pipeline_freshness.set(900)
        pipeline_lag.set(30)
        pipeline_quarantine.set(0.001)

        pipeline_success.inc()

    except Exception:
        pipeline_failure.inc()

    time.sleep(10)
```

The example is intentionally small. Production instrumentation should use stable metric names, appropriate labels, controlled cardinality, and explicit lifecycle semantics.

## 36.2 Prometheus scrape concept

A conceptual Prometheus configuration:

```yaml
scrape_configs:
  - job_name: data-pipeline
    static_configs:
      - targets:
          - "pipeline:8000"
```

## 36.3 Alert rules

```yaml
groups:
  - name: data-pipeline-alerts
    rules:

      - alert: PipelineFailure
        expr: increase(pipeline_failure_total[10m]) > 0
        for: 5m
        labels:
          severity: critical
          team: data-platform
        annotations:
          summary: "Production pipeline failure"
          description: "A production pipeline has recorded a failure."
          runbook: "freshness-and-pipeline-failure"

      - alert: PipelineFreshnessBreach
        expr: pipeline_freshness_seconds > 3600
        for: 10m
        labels:
          severity: critical
          team: data-platform
        annotations:
          summary: "Pipeline freshness SLO breached"
          description: "Dataset freshness exceeds the configured threshold."
          runbook: "freshness-and-pipeline-failure"

      - alert: PipelineLowVolume
        expr: pipeline_rows < 8000000
        for: 10m
        labels:
          severity: warning
          team: data-platform
        annotations:
          summary: "Pipeline volume is below expected range"
          description: "Latest row count is below the configured threshold."
          runbook: "volume-anomaly"

      - alert: HighQuarantineRatio
        expr: pipeline_quarantine_ratio > 0.05
        for: 10m
        labels:
          severity: warning
          team: data-platform
        annotations:
          summary: "High quarantine ratio"
          description: "The pipeline is quarantining an unusually large fraction of records."
          runbook: "data-quality"

      - alert: ConsumerLagHigh
        expr: pipeline_lag_seconds > 1800
        for: 10m
        labels:
          severity: critical
          team: streaming
        annotations:
          summary: "Consumer lag is high"
          description: "Streaming processing delay exceeds the configured threshold."
          runbook: "consumer-lag"

      - alert: ExcessiveRetries
        expr: rate(pipeline_failure_total[10m]) > 0.02
        for: 10m
        labels:
          severity: critical
          team: data-platform
        annotations:
          summary: "Pipeline failure rate is elevated"
          description: "Repeated failures indicate a possible retry storm or dependency problem."
          runbook: "pipeline-failure"
```

> **Important:** Metric names and thresholds here are lab examples. Production thresholds must be derived from actual SLOs, baselines, data tiers, schedules, and platform behavior.

## 36.4 Alertmanager routing concept

A conceptual configuration:

```yaml
route:
  receiver: team-channel

  routes:
    - matchers:
        - severity="critical"
        - environment="production"
        - data_tier="tier0"
      receiver: primary-oncall

    - matchers:
        - severity="warning"
      receiver: team-channel

    - matchers:
        - environment="development"
      receiver: development-channel
```

A production implementation should define explicit receivers and notification integrations appropriate to the organization.

---

# 37. Failure-Injection Lab

The purpose of failure injection is not merely to prove that an alert fires. It is to verify:

```text
Failure
→ Detection
→ Correct severity
→ Correct routing
→ Correct runbook
→ Correct response
→ Correct validation
```

## Incident 1 — Freshness breach

Cause:

```text
Warehouse load becomes slow.
```

Expected:

```text
Freshness alert
```

Learner tasks:

1. Confirm the freshness metric.
2. Check pipeline execution.
3. Check warehouse load.
4. Identify consumer impact.
5. Follow the runbook.
6. Communicate status.
7. Validate recovery.

## Incident 2 — Low volume

Cause:

```text
Upstream API returns incomplete data.
```

Expected:

```text
Volume alert
```

Investigate:

```text
Rows produced
vs
Historical expected range
```

Do not automatically backfill until the upstream correctness problem is understood.

## Incident 3 — Kafka lag

Cause:

```text
Consumer processing becomes slow.
```

Expected:

```text
Lag alert
```

Investigate:

```text
lag
→ processing rate
→ consumer health
→ downstream freshness
```

## Incident 4 — Retry storm

Cause:

```text
Downstream dependency repeatedly fails.
```

Expected:

```text
Retry/failure alert
```

Investigate whether retries are:

- recovering
- exhausting
- increasing dependency pressure

## Incident 5 — Alert storm

Cause:

```text
One database failure causes 15 downstream alerts.
```

Expected response:

```text
Grouping
+
Inhibition
+
Root-cause-focused paging
```

The learner should identify the dependency failure as the likely root condition rather than treating 15 notifications as 15 independent incidents.

---

# 38. Alert Fatigue Exercise

Imagine a production system with this configuration:

```text
Every pipeline duration change → alert
Every retry → page
Every null-rate change → page
Every Kafka CPU spike → page
Every freshness warning → page
Development failures → production pager
No runbooks
No owners
No severity model
No grouping
No inhibition
```

## Learner task

Redesign it.

Ask:

1. Which signals should remain metrics?
2. Which should become warnings?
3. Which should page?
4. Which alerts represent symptoms?
5. Which alerts represent causes?
6. Which should be grouped?
7. Which should be inhibited?
8. Which should have different data-tier severity?
9. What runbook does each page require?
10. How should development alerts be routed?

## Expert solution

A stronger model is:

```text
All useful telemetry
        ↓
Dashboards / metrics

Consumer-impact SLO breach
        ↓
Paging

Potential degradation
        ↓
Warning

Known root cause
        ↓
Diagnostic signal

Related symptoms
        ↓
Grouping/inhibition

Development
        ↓
Non-production channel
```

The goal is not zero telemetry. It is high-value operational interruption.

---

# 39. Simulated On-Call Week

## Monday — Freshness warning

Situation:

```text
Internal dataset is 12 minutes late.
SLO allows 30 minutes.
```

Expected response:

- verify the condition
- do not page if policy says warning
- investigate during business hours
- document if recurring

## Tuesday — Kafka lag critical

Situation:

```text
Tier 0 consumer lag exceeds SLO.
```

Tasks:

1. Triage
2. Identify severity
3. Determine owner
4. Use runbook
5. Investigate
6. Communicate
7. Escalate if required
8. Resolve
9. Validate
10. Review alert configuration

## Wednesday — Low-volume false positive

Situation:

```text
Alert fires because a weekend/holiday pattern
was incorrectly compared with a normal weekday.
```

Expected response:

- investigate baseline assumptions
- correct the alert model
- avoid blindly increasing thresholds
- decide whether dynamic/historical baselines are appropriate

## Thursday — Warehouse outage and alert storm

Situation:

```text
Warehouse unavailable
→ 15 downstream alerts
```

Expected response:

```text
Identify root dependency
→ group alerts
→ inhibit secondary symptoms
→ page appropriate owner
→ communicate consumer impact
```

## Friday — Customer-facing dataset unavailable

Situation:

```text
Critical customer-facing dataset unavailable.
```

Expected response:

1. Immediate triage
2. CRITICAL severity
3. Primary on-call ownership
4. Runbook
5. Consumer impact assessment
6. Escalation if recovery is blocked
7. Stakeholder update
8. Safe recovery
9. Validation
10. Post-incident alert review

---

# 40. Noisy Alert Removal Exercise

Suppose an alert fires 80 times each week and only once requires human action.

Ask:

> **Should this be removed, redesigned, downgraded, or converted to a dashboard metric?**

Use this reasoning process:

```text
Does it represent consumer impact?
        ↓
      No
        ↓
Is it useful for diagnosis?
        ↓
      Yes
        ↓
Keep as metric/dashboard signal

Does it indicate an actionable degradation?
        ↓
      Yes
        ↓
Can threshold or `for` be improved?
        ↓
      Yes
        ↓
Redesign

Does it remain non-actionable?
        ↓
Convert to non-paging telemetry
```

Do not optimize for zero alerts. Optimize for high-value alerts.

---

# 41. Testing Alerts

Alert configuration should be treated as code.

Test:

- PromQL validity
- threshold conditions
- `for` duration
- routing
- grouping
- inhibition
- silence behavior
- severity
- runbook references

## 41.1 Test the condition

A test should establish:

```text
Input metric state
→ expected alert state
```

Include boundary conditions:

```text
threshold - epsilon
threshold
threshold + epsilon
```

## 41.2 Test `for`

Verify:

```text
condition true for 2m
→ does not fire

condition true for 5m
→ fires
```

if the rule specifies `for: 5m`.

## 41.3 Test routing

Verify:

```text
critical + production + tier0
→ primary on-call
```

and:

```text
warning + production
→ team channel
```

## 41.4 Test inhibition

Simulate:

```text
database unavailable
+
downstream failures
```

Verify secondary notifications are suppressed according to policy.

## 41.5 Test silences

Verify:

- matching alerts are suppressed
- non-matching alerts remain active
- silence expires
- reason/owner metadata exists

## 41.6 Test runbook references

A firing alert should not point to:

```text
404 Not Found
```

or an obsolete procedure.

---

# 42. Alerts as Code

Alert configurations should be managed through engineering practices:

- version control
- code review
- environment-specific configuration
- CI validation
- deployment
- rollback
- testing

Example repository organization:

```text
observability/
├── alerts/
│   ├── pipeline-alerts.yml
│   ├── freshness-alerts.yml
│   └── streaming-alerts.yml
├── prometheus/
├── alertmanager/
└── runbooks/
```

This is an example organization only; this module does not require creating those files.

## Production lifecycle

```text
Change alert
   ↓
Pull request
   ↓
Static validation
   ↓
Rule tests
   ↓
Review
   ↓
Deploy
   ↓
Observe
   ↓
Rollback if necessary
```

Alerting logic deserves the same engineering discipline as production code.

---

# 43. Common Production Mistakes

| Mistake | Why it happens | Harm | Correct approach |
|---|---|---|---|
| Alerting on every metric | Fear of missing incidents | Alert fatigue | Page only on actionable conditions |
| No dashboard/page distinction | Treating telemetry as incidents | Too many interruptions | Define notification purpose |
| Cause-only alerts | Infrastructure-first thinking | Missed consumer impact | Combine impact and diagnostic signals |
| No consumer-impact alerts | Job-centric design | Data can be stale while jobs are green | Alert on SLOs and data health |
| Wrong thresholds | Arbitrary values | False positives/negatives | Use SLOs and baselines |
| No `for` | Immediate reaction to noise | Transient pages | Require persistence where appropriate |
| Alert storms | No correlation | Incident overload | Group/inhibit |
| Duplicate alerts | Multiple signals for one incident | Notification noise | Deduplicate/group |
| Incorrect severity | Metric magnitude used as severity | Wrong response | Use impact + urgency |
| No owner | Alert without responsibility | Delayed response | Explicit ownership |
| No runbook | Alert without procedure | Cognitive load | Link tested runbook |
| No escalation path | Stalled incidents | Longer recovery | Define escalation |
| Permanent silences | Noise treated as solved | Hidden incidents | Expiring, reasoned silences |
| Ignoring alert fatigue | No alert review | Pages get ignored | Measure and review |
| Development paging production | Environment ignored | Unnecessary interruption | Environment-aware routing |
| Alerting transient failures | No persistence criteria | False positives | Use `for` and recovery logic |
| No SLO alerts | Raw metrics dominate | Weak consumer focus | Alert on reliability objectives |
| No burn-rate alerting | Wait for full SLO failure | Slow detection | Use appropriate burn-rate strategy |
| No alert testing | Configuration assumed correct | Broken paging | Test as code |
| Never reviewing alerts | Set-and-forget | Stale/noisy alerts | Regular alert-quality review |

---

# 44. Production Trade-offs

There is no universal alerting configuration.

## Sensitivity vs noise

```text
More sensitive
→ faster detection
→ more false positives

Less sensitive
→ fewer alerts
→ potentially slower/missed detection
```

## Fast detection vs false positives

Use shorter windows when the impact of delay is high and the signal is trustworthy.

## Infrastructure vs consumer impact

Infrastructure alerts help diagnosis. Consumer-impact alerts help prioritize response.

## More alerts vs fewer high-value alerts

A mature system prefers fewer pages with higher actionability.

## Static thresholds vs dynamic baselines

Static thresholds are simple. Dynamic baselines better handle seasonality but introduce model complexity and potential instability.

## Immediate paging vs delayed confirmation

Paging immediately may be appropriate for critical, unambiguous conditions. Delayed confirmation can reduce noise for transient conditions.

## Simple routing vs sophisticated routing

Complex routing can reduce noise but increases configuration and operational complexity.

## Detection speed vs alert fatigue

The correct balance depends on:

- SLO
- impact
- failure frequency
- recovery time
- signal quality

## SLO-based vs raw-threshold alerting

Raw thresholds are useful diagnostics.

SLO-based alerting better represents consumer-facing reliability.

---

# 45. Checkpoint — Production Design

You should now be able to explain:

1. Why is a dashboard not an alert?
2. What makes an alert actionable?
3. What is the difference between symptom and cause alerts?
4. What does Alertmanager do?
5. Why do we group alerts?
6. What is inhibition?
7. What is a runbook?
8. What is an error budget?
9. Why can a successful pipeline still produce a bad data product?
10. Why should severity depend on data tier and consumer impact?

### Answers

1. Dashboards support exploration; alerts demand action.
2. It has a clear condition, owner, impact, severity, evidence, and next action.
3. Symptom alerts represent impact; cause alerts identify underlying mechanisms.
4. It routes, groups, inhibits, silences, and delivers active alerts.
5. Multiple symptoms may belong to one incident.
6. It suppresses secondary alerts while a known root condition is active.
7. A documented operational procedure for investigating and responding safely.
8. The allowed unreliability implied by an SLO.
9. Data can still be stale, incomplete, invalid, or delayed.
10. The same technical condition can have very different business impact.

---

# 46. Senior Data Engineer Interview Preparation

## Q1. What is the difference between monitoring and alerting?

**Answer:** Monitoring observes and exposes system state. Alerting applies an operational policy to determine when a human action is required.

## Q2. Why should not every dashboard metric page?

**Answer:** Most metrics are useful for observation and diagnosis, but only a subset represent actionable reliability conditions. Paging on everything causes alert fatigue.

## Q3. Symptom-based or cause-based alerts?

**Answer:** Consumer-impacting symptom alerts are often stronger paging signals because they directly represent reliability impact. Cause signals remain valuable for diagnosis and early warning.

## Q4. What does Prometheus do?

**Answer:** Prometheus stores/query metrics and evaluates alerting rules based on PromQL conditions.

## Q5. What does Alertmanager do?

**Answer:** It manages active alerts downstream of the rule evaluator through routing, grouping, inhibition, silencing, and notification handling.

## Q6. Why group alerts?

**Answer:** To represent correlated symptoms as a coherent incident and reduce notification overload.

## Q7. What is inhibition?

**Answer:** Suppression of secondary notifications when a known root condition is active.

## Q8. What is a silence?

**Answer:** A temporary suppression matching defined alerts, commonly used during maintenance or controlled incident work. It is not a fix.

## Q9. Why is freshness often more important than pipeline success?

**Answer:** A pipeline can execute successfully while the data it publishes remains stale because the upstream source was late or the resulting dataset timestamp did not advance.

## Q10. How would you design a freshness alert?

**Answer:** Define the freshness SLI, establish a dataset-specific SLO, account for schedule and data tier, measure the latest valid data timestamp, and page only when consumer impact or SLO risk warrants it.

## Q11. How would you alert on Kafka lag?

**Answer:** Measure lag or processing delay, compare it with the streaming SLO, and correlate lag with downstream freshness. Metric names depend on the exporter/platform.

## Q12. How do you reduce alert fatigue?

**Answer:** Remove non-actionable pages, tune thresholds and `for` durations, use grouping/inhibition, correct severity, route by environment and ownership, add runbooks, and continuously review alert quality.

## Q13. What is an error budget?

**Answer:** The amount of unreliability allowed by an SLO.

## Q14. What is burn rate?

**Answer:** The rate at which current unreliability consumes the allowed error budget.

## Q15. Why use multi-window burn-rate alerting?

**Answer:** A short window provides rapid detection while a longer window confirms sustained impact, balancing responsiveness and noise.

## Q16. What should an alert contain?

**Answer:** What happened, severity, affected asset/consumers, timing, owner, current and expected values, evidence links, runbook, and safe operational context.

## Q17. What is alert precision?

**Answer:** A useful approximation is actionable alerts divided by total alerts. It should be considered alongside false negatives, page volume, detection speed, and consumer impact.

## Q18. What is an alert fingerprint used for?

**Answer:** It provides a stable identity for equivalent alert instances so notifications can be grouped or deduplicated.

## Q19. What is an on-call handover?

**Answer:** Transfer of operational context including open incidents, degraded pipelines, noisy alerts, maintenance, scheduled jobs, known dependencies, and escalation contacts.

## Q20. When should an incident be escalated?

**Answer:** When progress is blocked, impact is increasing, data loss/security/compliance risk appears, or the current responder lacks the authority or expertise required to recover safely.

---

# 47. Final Assessment

## 47.1 Basic

1. Define monitoring.
2. Define observability.
3. Explain dashboard vs alert vs report.
4. Explain symptom vs cause.
5. Define freshness.
6. Define lag.
7. Define severity.
8. Explain a runbook.
9. Define SLI and SLO.
10. Define error budget.

### Expected standard

You should explain each concept without relying on memorized jargon.

## 47.2 Intermediate

1. Design a freshness alert for a Tier 1 dataset.
2. Design a low-volume alert with a historical baseline.
3. Decide whether a null-rate breach should page.
4. Design a Kafka lag warning.
5. Distinguish one transient failure from repeated failures.
6. Write a Prometheus rule using `increase()` and `for`.
7. Define alert labels and annotations.
8. Design routing for production vs development.
9. Write a runbook outline.
10. Decide whether a cost spike is actionable.

### Expected standard

You should justify thresholds and severity using consumer impact, SLOs, ownership, and operational response.

## 47.3 Advanced

1. Design an Alertmanager routing hierarchy.
2. Design grouping for a dependency outage.
3. Design inhibition for downstream symptoms.
4. Design expiring silences.
5. Design a burn-rate strategy for freshness.
6. Diagnose an alert storm.
7. Measure alert precision.
8. Design an alert-quality review process.
9. Design tests for alert rules.
10. Design alerts as code.

### Expected standard

You should reason about trade-offs rather than merely write configuration.

## 47.4 Production/Senior

1. Design a complete production alert architecture for a multi-tier data platform.
2. Define SLO-based paging for freshness, delivery, and streaming delay.
3. Design multi-window burn-rate detection.
4. Define primary/secondary on-call and escalation.
5. Design stakeholder communication.
6. Design data-status communication.
7. Build an alert-fatigue reduction program.
8. Define alert ownership and lifecycle.
9. Design failure-injection tests.
10. Define operational KPIs for the alerting system.

### Expected standard

A senior answer should demonstrate:

```text
Consumer impact
+
SLO reasoning
+
Alert precision
+
Routing
+
Incident response
+
Safe recovery
+
Continuous improvement
```

---

# 48. Final Production Incident Challenge

## Scenario

> At 06:30, the daily revenue dataset is expected to be available. At 06:45, consumers report that the dataset is stale. The pipeline dashboard shows several downstream failures, Kafka lag has increased, and multiple alerts have fired.

## Learner task

1. Identify the primary consumer impact.
2. Determine the correct severity.
3. Separate symptoms from likely causes.
4. Group related alerts.
5. Identify which alert should page.
6. Use the runbook.
7. Check freshness.
8. Check Kafka lag.
9. Check pipeline failures/retries.
10. Identify the likely root cause.
11. Communicate status.
12. Escalate if required.
13. Recover the pipeline.
14. Verify data freshness.
15. Determine whether alerts should be redesigned.

## Expert solution

### Step 1 — Consumer impact

Primary impact:

```text
Revenue dataset is stale at the expected delivery deadline.
```

Because revenue reporting is assumed to be Tier 0, the default operational posture should be critical, subject to the organization's actual SLO/policy.

### Step 2 — Severity

```text
Tier 0
+
SLO breach
+
consumer impact
→ CRITICAL
```

### Step 3 — Separate symptoms from causes

Potential symptoms:

```text
Freshness breach
Kafka lag
Downstream pipeline failures
```

Potential causes:

```text
Kafka processing degradation
Warehouse saturation
Upstream delay
Dependency failure
```

Do not declare a root cause merely because one metric looks abnormal.

### Step 4 — Group related alerts

Correlate alerts around:

```text
Revenue freshness incident
```

The multiple downstream alerts should not automatically be treated as independent incidents.

### Step 5 — Identify paging signal

The strongest primary page is the consumer-facing freshness/SLO breach.

Supporting alerts:

```text
Kafka lag
pipeline failures
retry rate
warehouse health
```

help diagnosis.

### Step 6 — Runbook

Follow the freshness runbook:

```text
Confirm freshness
→ inspect run
→ inspect upstream
→ inspect streaming lag
→ inspect warehouse
→ inspect retries
→ determine safe recovery
```

### Step 7 — Check freshness

Verify:

```text
latest valid data timestamp
current time
freshness SLO
```

### Step 8 — Check Kafka lag

Determine:

```text
lag magnitude
lag trend
consumer processing rate
whether lag explains downstream freshness
```

### Step 9 — Check failures/retries

Look for:

```text
consecutive failures
retry exhaustion
dependency failures
schema errors
resource errors
```

### Step 10 — Identify root cause

Suppose evidence shows:

```text
Warehouse saturation
   ↓
consumer processing slowed
   ↓
Kafka lag increased
   ↓
downstream pipeline missed freshness SLO
```

Then warehouse saturation is a plausible root cause, while Kafka lag and freshness breach are symptoms.

### Step 11 — Communicate

```text
Incident:
Revenue dataset delayed.

Impact:
Finance/revenue consumers are seeing stale data.

Status:
The team has confirmed a freshness SLO breach and is investigating
warehouse saturation associated with increased downstream processing delay.

Next update:
15 minutes.

Current hypothesis:
Warehouse load saturation.

No recovery ETA is being stated until mitigation is validated.
```

### Step 12 — Escalate

Escalate if:

- warehouse owner is required
- recovery is blocked
- impact is increasing
- data-loss risk exists
- the incident exceeds responder authority

### Step 13 — Recover

Use an approved, safe mitigation.

Do not improvise destructive operations merely to make the dashboard green.

### Step 14 — Verify

Recovery requires:

```text
Pipeline success
+
freshness restored
+
quality checks pass
+
consumer-visible data validated
```

### Step 15 — Improve

After recovery ask:

- Did the correct alert page?
- Were secondary alerts too noisy?
- Was routing correct?
- Was the runbook sufficient?
- Was the threshold appropriate?
- Should grouping/inhibition change?
- Did the alert detect impact quickly enough?

The mature operational loop is:

```text
Good alerting
    ↓
Fast detection
    ↓
Low-noise triage
    ↓
Correct escalation
    ↓
Safe recovery
    ↓
Consumer verification
    ↓
Alert improvement
```

---

# 49. Glossary

| Term | Meaning |
|---|---|
| Monitoring | Collection and observation of operational signals |
| Observability | Ability to understand system state from telemetry/evidence |
| Dashboard | Visual interface for exploring state and trends |
| Alert | Actionable signal requiring defined response |
| Report | Communication of status/trends to stakeholders |
| Symptom | Observable impact or resulting failure condition |
| Cause | Underlying mechanism producing a symptom |
| Prometheus | Metrics storage/query and alert-rule evaluation system |
| PromQL | Prometheus Query Language |
| Alert rule | Query-based condition that produces an alert |
| Alertmanager | Alert routing/grouping/inhibition/silencing component |
| Routing | Choosing where an alert is delivered |
| Grouping | Combining related alerts |
| Inhibition | Suppressing secondary alerts when a root condition is active |
| Silence | Temporary suppression of matching alerts |
| Severity | Impact + urgency + required response |
| Freshness | Age of the latest valid data |
| Lag | Processing distance/delay in a streaming system |
| Volume anomaly | Unexpected change in record volume |
| Data quality alert | Alert based on data correctness/completeness rules |
| Runbook | Operational procedure for an alert/incident |
| On-call | Explicit operational responsibility during a coverage period |
| Escalation | Transfer/increase of response to another owner or level |
| SLI | Service Level Indicator; what is measured |
| SLO | Service Level Objective; desired reliability |
| SLA | Service Level Agreement; externally/organizationally committed level |
| Error budget | Allowed unreliability implied by an SLO |
| Burn rate | Rate of error-budget consumption |
| Alert fatigue | Reduced attention caused by excessive/noisy alerts |
| Alert precision | Fraction of alerts that are useful/actionable |
| Deduplication | Reduction of repeated equivalent notifications |
| Incident | Operational event requiring coordinated response |

---

# 50. Final Learning Checklist

```text
[ ] Explain monitoring
[ ] Explain observability
[ ] Explain dashboard vs alert vs report
[ ] Explain actionable alerts
[ ] Explain symptom-based alerts
[ ] Explain cause-based alerts
[ ] Design freshness alerts
[ ] Design volume alerts
[ ] Design data-quality alerts
[ ] Design Kafka lag alerts
[ ] Design retry/failure alerts
[ ] Design cost alerts
[ ] Explain severity
[ ] Explain data-tier-based priority
[ ] Write Prometheus alert rules
[ ] Understand PromQL for alerts
[ ] Configure Alertmanager conceptually
[ ] Explain routing
[ ] Explain grouping
[ ] Explain inhibition
[ ] Explain silencing
[ ] Design actionable alert content
[ ] Write a production runbook
[ ] Explain SLI
[ ] Explain SLO
[ ] Explain error budget
[ ] Explain burn rate
[ ] Design SLO-based alerts
[ ] Identify alert fatigue
[ ] Measure alert quality
[ ] Deduplicate alerts
[ ] Design on-call rotations
[ ] Perform on-call handover
[ ] Define escalation
[ ] Communicate incidents
[ ] Communicate data status
[ ] Test alerts
[ ] Manage alerts as code
[ ] Perform failure injection
[ ] Run an on-call simulation
[ ] Remove noisy alerts
[ ] Design production alerting architecture
```

---

# 51. Roadmap Coverage Audit

This module explicitly covers the required roadmap areas.

## Alerting fundamentals

- [x] Dashboards
- [x] Alerts
- [x] Reports
- [x] Symptom alerts
- [x] Cause alerts

## Alert types

- [x] Freshness
- [x] Volume
- [x] Quality
- [x] Lag
- [x] Retry/failure
- [x] Cost

## Prometheus

- [x] Metrics
- [x] PromQL
- [x] Alert rules
- [x] `for`
- [x] Labels
- [x] Annotations

## Alertmanager

- [x] Routing
- [x] Grouping
- [x] Inhibition
- [x] Silencing

## Operational design

- [x] Severity
- [x] Data tiers
- [x] Ownership
- [x] Actionable content
- [x] Runbooks

## Reliability

- [x] SLI
- [x] SLO
- [x] Error budget
- [x] Burn rate

## Alert quality

- [x] Alert fatigue
- [x] Precision
- [x] Volume
- [x] Deduplication
- [x] Noise reduction

## On-call

- [x] Rotation
- [x] Handover
- [x] Escalation
- [x] Stakeholder communication
- [x] Data status

## Production

- [x] Failure simulation
- [x] On-call simulation
- [x] Noisy-alert removal
- [x] Testing
- [x] Alerts as code
- [x] Production trade-offs

---

# 52. Master Principle

The most important lesson in this module is:

> **A pipeline being technically successful does not necessarily mean that the data product is healthy.**

Examples:

```text
Pipeline SUCCESS
but
freshness SLO breached
```

```text
Pipeline SUCCESS
but
row volume is 80% below normal
```

```text
Pipeline SUCCESS
but
quality checks indicate unusable data
```

```text
Pipeline SUCCESS
but
Kafka lag causes consumers to receive stale data
```

Therefore:

> **Production alerting should be designed around consumer impact and operational action, not merely task execution status.**

A mature data platform does not try to alert on everything.

It builds a deliberate chain:

```text
Reliable signal
    ↓
Meaningful condition
    ↓
Correct severity
    ↓
Correct owner
    ↓
Low-noise routing
    ↓
Actionable alert
    ↓
Useful runbook
    ↓
Effective on-call response
    ↓
Safe recovery
    ↓
Consumer verification
    ↓
Continuous alert improvement
```

That is the foundation of production-grade alerting and on-call operations for data engineering.
