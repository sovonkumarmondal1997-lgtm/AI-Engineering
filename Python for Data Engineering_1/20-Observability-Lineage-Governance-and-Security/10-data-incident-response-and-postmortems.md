# Data Incident Response and Post-Mortems

> **Stage 2 → Python for Data Engineering**  
> **Module 2.20 → Observability, Lineage, Governance, and Security**  
> **Topic 10 → Data Incident Response and Post-Mortems**

## 1. Learning Objectives

By completing this module, you should be able to operate a production Data Engineering incident from first detection through recovery, postmortem, and long-term prevention.

You will learn to:

- identify wrong, late, missing, corrupted, and exposed data;
- distinguish data-quality, availability, freshness, security, privacy, and compliance incidents;
- classify severity based on consumer and business impact;
- detect incidents through metrics, logs, traces, data-quality checks, freshness monitors, Kafka lag, user reports, and security/privacy signals;
- operate an Incident Commander model;
- perform disciplined triage and containment;
- determine blast radius using inventory and lineage;
- identify the last known good state;
- investigate root cause and contributing factors;
- remediate and recover affected data;
- reconcile source and target state;
- verify recovery rather than trusting a green pipeline;
- communicate clearly with technical and business stakeholders;
- preserve evidence during security/privacy incidents;
- create runbooks;
- write blameless postmortems;
- use Five Whys;
- create measurable corrective and preventive actions;
- convert postmortem actions into tests, checks, alerts, dashboards, and runbooks;
- measure Time to Detect (TTD), Time to Mitigate (TTM), and Time to Resolve (TTR);
- run game days and incident simulations;
- measure improvement after incidents.

### Incident-response mindset

> **During an incident, the objective is not to immediately prove who caused the problem. The objective is to protect consumers, contain the impact, restore trustworthy data, understand the blast radius, communicate effectively, and learn how to prevent recurrence.**

---

## 2. The Incident Response Lifecycle

A practical lifecycle is:

```text
Detect
  ↓
Triage
  ↓
Contain
  ↓
Scope
  ↓
Remediate
  ↓
Recover
  ↓
Verify
  ↓
Communicate
  ↓
Learn
  ↓
Prevent
```

These stages are related but not necessarily strictly linear. A severe incident can move back into triage after a failed remediation attempt.

### Detect

A signal indicates that something may be wrong.

### Triage

Determine whether the signal represents meaningful consumer or operational impact.

### Contain

Stop the incident from getting worse.

### Scope

Determine what is affected.

### Remediate

Fix the underlying technical/data problem.

### Recover

Restore trustworthy service and data.

### Verify

Prove that recovery actually worked.

### Communicate

Keep the appropriate stakeholders informed.

### Learn

Analyze the incident and the response.

### Prevent

Turn lessons into durable engineering controls.

---

## 3. What Is a Data Incident?

A data incident is an event that causes material degradation to the correctness, availability, freshness, confidentiality, integrity, or trustworthy use of data.

### Wrong data

Examples:

- incorrect revenue;
- incorrect currency conversion;
- duplicate records;
- incorrect joins;
- corrupted values;
- incorrect aggregates.

Example:

```text
Expected revenue: $10.50
Actual revenue:   $1050.00
```

### Late data

Examples:

- delayed pipeline;
- stale warehouse;
- missing daily partition;
- delayed CDC.

### Missing data

Examples:

- failed ingestion;
- dropped events;
- incomplete CDC;
- missing partition.

### Exposed data

Examples:

- PII leak;
- unauthorized dataset access;
- sensitive information in logs;
- credentials or secrets exposed.

### Corrupted data

Examples:

- schema corruption;
- malformed records;
- incorrect transformation;
- unexpected encoding or type conversion.

### Incident categories

```text
Data Quality Incident
Data Availability Incident
Data Freshness Incident
Security Incident
Privacy Incident
Compliance Incident
```

One event can belong to multiple categories. For example, a PII exposure can simultaneously be a security and privacy incident.

---

## 4. Incident vs Data Quality Issue

Not every anomaly is an incident.

```text
Minor anomaly
      ↓
No meaningful consumer impact
      ↓
Normal data-quality workflow
```

Versus:

```text
Incorrect data
      ↓
Executive dashboard affected
      ↓
Financial reporting affected
      ↓
Production incident
```

### Key principle

> **Incident severity is driven by impact, not merely by the existence of a technical defect.**

A bad record in an unused development table is different from incorrect financial data consumed by executives.

Consider:

- who consumes the data;
- whether decisions depend on it;
- financial impact;
- customer impact;
- security/privacy impact;
- duration;
- geographic scope;
- data volume;
- regulatory/governance significance.

---

## 5. Incident Severity

A generic framework is:

```text
SEV-1
Critical consumer/business/security impact

SEV-2
Major production impact

SEV-3
Limited impact

SEV-4
Minor/non-urgent issue
```

Organizations may use different labels and thresholds.

### Severity dimensions

Severity should consider:

- consumer impact;
- business impact;
- data correctness;
- data availability;
- freshness;
- security;
- privacy;
- compliance;
- scope;
- duration.

### Example decision table

| Dimension | Lower severity | Higher severity |
|---|---|---|
| Consumers | Internal/limited | External/many consumers |
| Correctness | Cosmetic | Financial/critical decisions |
| Availability | Optional dataset | Critical production dataset |
| Freshness | Minor delay | Decisions depend on freshness |
| Privacy | No sensitive data | PII/sensitive exposure |
| Security | No unauthorized access | Confirmed unauthorized access |
| Scope | Small dataset | Enterprise-wide |
| Duration | Short | Long-running |
| Recovery | Simple rerun | Complex rebuild/backfill |

Do not let the label substitute for judgment. Severity should be tied to the actual impact model used by the organization.

---

## 6. Incident Detection Sources

Incidents can be detected through:

- Prometheus metrics;
- Grafana dashboards;
- Alertmanager;
- pipeline failures;
- data-quality checks;
- freshness monitors;
- anomaly detection;
- OpenTelemetry traces;
- logs;
- warehouse checks;
- Kafka lag;
- user reports;
- stakeholder reports;
- security alerts;
- privacy alerts;
- catalog/lineage signals.

### Observability vs incident response

> **Observability detects symptoms; incident response determines what to do about them.**

For example:

```text
Freshness alert
      ↓
Observation
      ↓
Triage
      ↓
"Is this a real consumer-impacting incident?"
```

A monitoring system may tell you that a pipeline is late. Incident response determines whether to declare, contain, scope, communicate, and recover.

---

## 7. Incident Declaration

A practical declaration flow:

```text
Signal
  ↓
Initial assessment
  ↓
Consumer impact?
  ↓
 YES
  ↓
Declare Incident
```

When an incident is declared, establish:

- incident ID;
- severity;
- start timestamp;
- affected systems;
- initial hypothesis;
- incident owner;
- incident channel/coordination mechanism.

Avoid spending excessive time debating whether the label is perfect. Declare early enough to create coordination when impact warrants it.

---

## 8. Incident Roles

Major incidents should separate coordination from technical execution.

### Incident Commander

Responsible for:

- overall coordination;
- prioritization;
- decisions;
- escalation;
- maintaining operational focus.

The Incident Commander should generally avoid becoming the primary person executing every command.

### Operations / Technical Responder

Responsible for:

- investigation;
- diagnosis;
- commands;
- remediation;
- recovery;
- validation.

### Communications Lead

Responsible for:

- stakeholder updates;
- status communication;
- business communication;
- coordinating customer-facing communication when appropriate.

### Scribe

Responsible for:

- timeline;
- decisions;
- actions;
- evidence;
- important observations.

### Why separate roles?

Without separation:

```text
One engineer
  ├── investigates
  ├── executes commands
  ├── talks to executives
  ├── records timeline
  └── makes decisions
```

Cognitive overload increases the chance of missed evidence, poor communication, and unsafe changes.

---

## 9. Incident Command Model

```text
                    Incident Commander
                           |
           +---------------+---------------+
           |               |               |
           v               v               v
       Technical       Communications     Scribe
       Responder          Lead
```

### Decision ownership

| Role | Primary responsibility |
|---|---|
| Incident Commander | Coordination and prioritization |
| Technical Responder | Diagnosis and technical action |
| Communications Lead | Stakeholder communication |
| Scribe | Timeline and evidence |

The exact staffing model depends on incident severity and organizational practice.

---

## 10. Triage

Triage determines what is happening before the team starts making risky changes.

Start with:

```text
What happened?
When did it start?
Who is affected?
What datasets are affected?
What consumers are affected?
Is the data wrong, missing, late, or exposed?
Is the issue still occurring?
What changed recently?
What is the last known good state?
```

### Evidence to collect

Useful evidence includes:

- pipeline run IDs;
- timestamps;
- alert details;
- recent deployments;
- Git SHA;
- image digest;
- configuration versions;
- schema versions;
- data-quality results;
- lineage;
- logs;
- traces;
- metrics.

### Avoid random production changes

Bad incident behavior:

```text
Alert
 ↓
Guess
 ↓
Change production
 ↓
New failure
 ↓
Less evidence
```

Better:

```text
Signal
 ↓
Evidence
 ↓
Hypothesis
 ↓
Safe test
 ↓
Decision
```

---

## 11. Containment

Containment means:

> **Stop the incident from getting worse.**

Possible actions:

- pause a pipeline;
- disable a bad deployment;
- stop downstream publication;
- quarantine bad data;
- block unsafe access;
- disable compromised credentials;
- stop a Kafka consumer;
- freeze an affected dataset.

### Containment vs remediation

```text
Containment
    ↓
Stop expansion
```

versus:

```text
Root-cause remediation
    ↓
Fix the underlying problem
```

For example:

```text
Bad transformation deployed
       ↓
Pause pipeline              ← containment
       ↓
Identify faulty code
       ↓
Deploy corrected code       ← remediation
```

Containment should be proportionate and reversible where possible.

---

## 12. Blast-Radius Analysis

Blast radius asks:

```text
Which datasets are affected?
Which partitions?
Which time window?
Which customers?
Which regions?
Which consumers?
Which dashboards?
Which ML features?
Which downstream pipelines?
```

### Why blast radius matters

A team cannot safely recover data without knowing what needs recovery.

Suppose a transformation bug ran for three hours.

The blast radius might be:

```text
3 hours
  ↓
12 partitions
  ↓
4 tables
  ↓
2 warehouse marts
  ↓
8 dashboards
  ↓
1 feature table
```

That is substantially more useful than:

> "The pipeline is broken."

---

## 13. Lineage-Based Scoping

Lineage is a core incident-response capability.

Example:

```text
Bad Source
   ↓
Dataset
   ↓
Downstream Tables
   ↓
Dashboards
   ↓
ML Features
   ↓
Consumers
```

Lineage helps answer:

- what is downstream?
- what depends on the affected dataset?
- which dashboards may be wrong?
- which features may be affected?
- which pipelines need reruns?
- which consumers need notification?

### OpenLineage

OpenLineage-style metadata can provide relationships between jobs, runs, and datasets.

A conceptual graph:

```text
Job A
  └── produces Dataset A
              ↓
          Job B
              ↓
        Dataset B
              ↓
          Job C
              ↓
        Dataset C
```

### Lineage gaps

Never assume lineage is complete.

Potential gaps:

- manually copied files;
- unmanaged SQL;
- local exports;
- external systems;
- dynamically generated queries;
- undocumented dependencies;
- missing instrumentation.

Therefore:

```text
Lineage
+
Inventory
+
Ownership
+
Runtime evidence
```

provides a stronger incident-scoping model than lineage alone.

---

## 14. Root-Cause Investigation

Root-cause analysis should be evidence-driven.

Investigate:

- recent changes;
- deployments;
- schema changes;
- configuration changes;
- upstream failures;
- infrastructure issues;
- dependency failures;
- data-contract violations;
- code defects;
- external-system failures.

### Avoid premature conclusions

Bad:

> "The developer made a typo."

Better:

> "A transformation accepted an incompatible unit without a validation assertion, and the deployment pipeline allowed it to reach production."

The second explanation exposes system conditions that can be improved.

---

## 15. Last Known Good State

The **last known good state** is the most recent state known to be correct and trustworthy.

Evidence may include:

- run metadata;
- data-quality results;
- checkpoints;
- pipeline version;
- Git SHA;
- container image digest;
- schema version;
- timestamps;
- reconciliation results.

Example:

```text
09:00 — Last validated good run
09:10 — Deployment
09:15 — First bad output
09:17 — Alert
```

The 09:00 state may become the recovery reference.

### Why it matters

Recovery strategies often depend on:

```text
Last known good state
        +
Known bad interval
        ↓
Targeted rebuild / backfill
```

---

## 16. Incident Timeline

A timeline turns scattered observations into a causal sequence.

Example:

```text
09:02 — Pipeline deployed
09:10 — First bad run
09:15 — Quality check fails
09:17 — Alert fires
09:20 — Incident declared
09:25 — Pipeline paused
09:40 — Blast radius identified
10:05 — Root cause found
10:20 — Fix deployed
10:35 — Data backfilled
10:50 — Validation complete
11:00 — Incident resolved
```

Record:

- exact timestamps;
- source of evidence;
- decisions;
- commands/actions;
- state transitions;
- communication events.

The scribe should record facts during the incident rather than reconstruct everything afterward.

---

## 17. Remediation

Possible remediation strategies include:

- rollback;
- hotfix;
- backfill;
- replay;
- recomputation;
- restore;
- data correction;
- schema fix;
- configuration fix;
- access revocation.

### Choosing a remediation

Evaluate:

```text
Safety
Correctness
Blast radius
Time to recover
Reversibility
Evidence impact
Downstream dependencies
```

Example:

```text
Bad transformation
   ↓
Rollback code
   ↓
Recompute affected interval
   ↓
Reconcile
   ↓
Republish
```

Do not choose the fastest action if it can make the data state harder to recover.

---

## 18. Recovery

Recovery is more than making infrastructure healthy.

A stronger definition is:

```text
System healthy
+
Data correct
+
Consumers restored
+
No hidden downstream corruption
+
Monitoring healthy
```

### Technical recovery vs data recovery

**Technical recovery:**

```text
Pipeline runs successfully
```

**Data recovery:**

```text
Correct code
+
Correct historical data
+
Correct downstream state
+
Verified consumers
```

A pipeline can be technically healthy while still publishing corrupted data.

---

## 19. Verification

Before declaring resolution, verify:

- row counts;
- checksums;
- data-quality checks;
- freshness;
- schema;
- reconciliation;
- downstream outputs;
- dashboards;
- consumer queries.

### Core principle

> **A green pipeline does not prove that the data is correct.**

Verification should be independent enough to catch the same defect that caused the incident.

---

## 20. Data Reconciliation

Reconciliation compares independent views of data.

### Row counts

```text
Source row count
      vs
Target row count
```

### Financial totals

```text
Source revenue
      vs
Target revenue
```

### Hash/checksum comparison

For suitable datasets, compare deterministic hashes or aggregate fingerprints.

### Business invariants

Examples:

```text
quantity >= 0
```

```text
total = subtotal + tax
```

```text
daily_revenue >= 0
```

### SQL example

```sql
SELECT
    DATE(event_time) AS event_date,
    COUNT(*) AS row_count
FROM events
GROUP BY DATE(event_time)
ORDER BY event_date DESC;
```

Compare the output with:

- expected historical ranges;
- source counts;
- ingestion metadata;
- downstream counts.

### Python example

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ReconciliationResult:
    source_count: int
    target_count: int

    @property
    def passed(self) -> bool:
        return self.source_count == self.target_count


result = ReconciliationResult(
    source_count=1_000_000,
    target_count=1_000_000,
)

assert result.passed
```

Production reconciliation should account for legitimate transformations such as filtering, deduplication, late-arriving data, and aggregation.

---

## 21. Communication During Incidents

A useful update answers:

```text
What happened?
Who is affected?
What is the current impact?
What are we doing?
What is the next update time?
```

### Example

```text
10:20 UTC — SEV-2 data incident.

A revenue transformation produced incorrect values for
the 09:10–10:00 processing window. Finance dashboards
are affected.

The pipeline is contained and publication is paused.
The team is rebuilding the affected interval.

Next update: 10:35 UTC.
```

### Communication principles

- state facts;
- distinguish facts from hypotheses;
- include timestamps;
- avoid speculation;
- state uncertainty explicitly;
- provide next-update expectations.

Different audiences may need different levels of detail.

---

## 22. Data Status Communication

Consumers need to know whether data can be trusted.

Useful states include:

```text
DATA FRESHNESS DEGRADED
```

```text
DATA QUALITY ISSUE UNDER INVESTIGATION
```

```text
DATA VERIFIED AND RESTORED
```

A data-status indicator can protect consumers from making decisions using untrusted data.

### Example status model

```text
HEALTHY
DEGRADED
UNTRUSTED
RECOVERING
VERIFIED
```

The status should have clear operational semantics rather than being a decorative dashboard label.

---

## 23. Security and Privacy Incidents

Special escalation is required when an incident involves:

- PII exposure;
- unauthorized access;
- credentials;
- encryption failure;
- data exfiltration;
- sensitive logs.

Conceptually:

```text
Technical Incident
       +
Security / Privacy Incident
       ↓
Additional Escalation
```

Possible participants include:

- security;
- privacy;
- governance;
- legal;
- incident management.

### Notification awareness

Do not invent notification deadlines.

Whether notification is required, to whom, and when depends on applicable law, contracts, organizational policy, and incident facts.

The engineering responsibility is to:

1. preserve evidence;
2. scope affected data;
3. identify affected systems/subjects where feasible;
4. provide accurate technical facts to the appropriate teams.

---

## 24. Evidence Preservation

Evidence can include:

- logs;
- traces;
- metrics;
- deployment records;
- Git commits;
- pipeline runs;
- access logs;
- lineage;
- snapshots;
- configuration;
- timestamps.

### Core principle

> **Preserve evidence before cleanup destroys the information needed to understand the incident.**

For a suspected security/privacy incident, do not casually delete logs or overwrite system state before the appropriate security/privacy process determines what evidence must be retained.

---

## 25. Incident Runbooks

A runbook should provide an operational path:

```text
Symptom
Trigger
Impact
Initial Checks
Containment
Diagnosis
Recovery
Verification
Escalation
Rollback
Communication
Postmortem
```

### Example: Data Pipeline Failure Runbook

**Trigger**

- pipeline failure alert;
- freshness SLO breach;
- data-quality alert.

**Initial checks**

```text
1. Identify pipeline/run.
2. Identify affected interval.
3. Check recent deployment.
4. Check upstream health.
5. Check data-quality signals.
6. Check downstream impact.
```

**Containment**

```text
Pause publication if bad data is still flowing.
```

**Diagnosis**

```text
Inspect logs → traces → run metadata → lineage → source/target data.
```

**Recovery**

```text
Rollback/fix → rebuild/backfill → reconcile.
```

**Verification**

```text
Quality checks → reconciliation → downstream checks.
```

**Escalation**

Escalate when:

- impact increases;
- security/privacy is suspected;
- recovery is blocked;
- business-critical consumers are affected.

---

## 26. Postmortems

A postmortem is:

> **A structured analysis performed after an incident to understand what happened, why it happened, how it was handled, and what must change.**

### Incident response vs postmortem

```text
Incident Response
    ↓
Restore trustworthy service
```

```text
Postmortem
    ↓
Learn and prevent recurrence
```

The postmortem is not a second incident response. It is the mechanism for organizational learning.

---

## 27. Blameless Postmortems

> **Blameless does not mean avoiding accountability. It means focusing on system conditions, decisions, controls, and process failures rather than personal blame.**

Useful questions:

- What conditions made the failure possible?
- What controls failed?
- What signals were missing?
- Why was the failure not detected earlier?
- Why did the system allow bad data to reach consumers?
- Why was recovery difficult?
- Which assumptions were wrong?
- Which safeguards were missing?

Avoid:

> "Who made the mistake?"

Prefer:

> "What system conditions allowed this failure to occur?"

The purpose is to increase the probability that people report weak signals and operational hazards before they become incidents.

---

## 28. Postmortem Structure

A complete postmortem should contain:

```text
Incident Summary
Incident ID
Severity
Start Time
End Time
Duration
Detection
Impact
Affected Systems
Affected Datasets
Affected Consumers
Timeline
Root Cause
Contributing Factors
Detection Gaps
Response Gaps
Recovery
Corrective Actions
Preventive Actions
Owners
Due Dates
Lessons Learned
```

### Section guidance

**Incident Summary:** one-paragraph description.

**Impact:** what consumers experienced.

**Timeline:** evidence-backed sequence.

**Root Cause:** primary causal condition.

**Contributing Factors:** additional conditions.

**Detection Gaps:** why detection was delayed or incomplete.

**Response Gaps:** what made response harder.

**Recovery:** how trustworthy service was restored.

**Corrective Actions:** immediate fixes.

**Preventive Actions:** durable controls.

**Owners/Due Dates:** accountability and completion tracking.

---

## 29. Five Whys

Five Whys is a structured questioning technique.

Example:

```text
Why was revenue incorrect?
        ↓
Incorrect currency conversion

Why?
        ↓
Exchange-rate table was stale

Why?
        ↓
Refresh pipeline failed

Why?
        ↓
Credential expired

Why?
        ↓
Credential rotation was not automated
```

The important lesson is not the number five. The technique should continue until the team reaches a useful system-level cause.

Avoid stopping at:

> "Engineer made a mistake."

Ask what system conditions made that mistake able to produce production impact.

---

## 30. Root Cause vs Contributing Factors

Example:

```text
Root Cause:
Incorrect transformation logic

Contributing Factors:
No data-quality assertion
No canary
No reconciliation
Weak deployment review
Insufficient alerting
```

A complex incident may have multiple causal pathways.

### Why the distinction matters

If the team fixes only the code:

```text
Code fixed
      ↓
Same missing safeguards
      ↓
Future defect can still escape
```

If the team also fixes the control environment:

```text
Code
+
Validation
+
Reconciliation
+
Alerting
+
Deployment safety
```

the recurrence probability can decrease substantially.

---

## 31. Corrective and Preventive Actions

### Corrective action

Fix the immediate problem.

Example:

```text
Correct the currency transformation.
```

### Preventive action

Reduce the chance of recurrence.

Examples:

```text
Add validation
Add alert
Add test
Add runbook
Improve deployment process
Improve access control
Improve lineage
Improve monitoring
```

The best postmortems produce actions that change system behavior, not just documentation.

---

## 32. Turning Postmortem Actions into Engineering Controls

> **Postmortem actions should become durable controls.**

Example:

```text
Incident:
Currency bug

Postmortem Action:
Add currency validation

        ↓

Automated Test
        +
Data Quality Check
        +
Alert
        +
Runbook
```

### Action-to-control mapping

| Postmortem finding | Durable control |
|---|---|
| Incorrect unit conversion | Unit validation test |
| Missing freshness detection | Freshness alert |
| Unknown downstream impact | Lineage instrumentation |
| Manual recovery was slow | Recovery runbook |
| Schema change caused corruption | Contract regression test |
| Sensitive field entered logs | PII log guard |
| No reconciliation | Automated reconciliation check |

This is how incident response improves engineering rather than simply producing a report.

---

## 33. Action Owners and Due Dates

Bad:

> Improve monitoring.

Better:

> Add a revenue reconciliation check to the daily sales pipeline, assign an owner, define acceptance criteria, and complete it by the approved due date.

Each action should include:

- owner;
- due date;
- priority;
- acceptance criteria;
- tracking state;
- verification method.

### Action lifecycle

```text
Identified
  ↓
Assigned
  ↓
In Progress
  ↓
Implemented
  ↓
Verified
  ↓
Closed
```

A closed action should have evidence that the promised control exists.

---

## 34. Incident Metrics

### Time to Detect (TTD)

How long until the incident is detected?

Conceptually:

```text
TTD = Detection Time - Incident Start Time
```

### Time to Mitigate (TTM)

How long until impact is reduced?

```text
TTM = Mitigation Time - Incident Start Time
```

### Time to Resolve (TTR)

How long until the incident is fully resolved?

```text
TTR = Resolution Time - Incident Start Time
```

Also track:

- repeat incident rate;
- false alert rate;
- incident frequency;
- consumer-impact duration;
- percentage detected automatically.

### Metrics are for improvement

Do not turn TTD/TTM/TTR into a simplistic ranking of individual engineers.

A high TTD may indicate:

- weak instrumentation;
- missing alerts;
- poor ownership;
- unclear thresholds.

A high TTM may indicate:

- weak runbooks;
- insufficient permissions;
- complex rollback;
- unclear incident command.

---

## 35. Game Days

> **A game day is a controlled simulation of a production failure used to test people, systems, runbooks, alerts, and recovery processes.**

Examples:

- Kafka outage;
- corrupted source;
- bad schema deployment;
- PII exposure;
- stale warehouse;
- failed backup;
- wrong transformation.

Lifecycle:

```text
Scenario
  ↓
Inject Failure
  ↓
Detect
  ↓
Respond
  ↓
Recover
  ↓
Measure
  ↓
Improve
```

Game days test the system before a real incident tests it for you.

---

## 36. Game-Day Design

A complete game-day plan contains:

- scenario;
- objective;
- participants;
- failure injection;
- expected signals;
- escalation;
- success criteria;
- recovery target;
- evidence;
- lessons;
- follow-up actions.

### Safe execution

For production environments, failure injection should be:

- explicitly authorized;
- bounded;
- observable;
- reversible;
- scoped;
- monitored;
- accompanied by a stop condition.

Prefer controlled environments for destructive scenarios.

### Example

```text
Scenario:
Kafka consumer stops processing

Objective:
Measure detection and recovery

Participants:
IC + technical responder + comms + scribe

Expected signal:
Consumer lag alert

Success:
Containment within target
Recovery within target
Verification completed
Postmortem controls identified
```

---

## 37. Incident Response Testing

Test:

- alerts;
- runbooks;
- escalation;
- dashboards;
- lineage;
- rollback;
- backfill;
- recovery;
- communication;
- postmortem workflow.

### Test pyramid

```text
Unit
  ↓
Integration
  ↓
End-to-End
  ↓
Game Day
```

Each layer tests a different failure mode.

---

## 38. Python Incident-Response Examples

### Detect a failed pipeline run

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PipelineRun:
    run_id: str
    status: str
    started_at: datetime
    finished_at: datetime | None


def is_failed(run: PipelineRun) -> bool:
    return run.status.upper() in {"FAILED", "ERROR"}
```

### Freshness check

```python
from datetime import datetime, timedelta, timezone


def is_fresh(last_event_at: datetime, max_age: timedelta) -> bool:
    now = datetime.now(timezone.utc)
    return now - last_event_at <= max_age
```

### Incident context

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class IncidentContext:
    incident_id: str
    severity: str
    affected_datasets: tuple[str, ...]
    affected_consumers: tuple[str, ...]
    hypothesis: str


context = IncidentContext(
    incident_id="INC-2026-001",
    severity="SEV-2",
    affected_datasets=("silver_sales", "gold_revenue"),
    affected_consumers=("finance_dashboard",),
    hypothesis="currency conversion regression",
)
```

### Incident state

```python
VALID_STATES = {
    "DETECTED",
    "DECLARED",
    "TRIAGING",
    "CONTAINED",
    "SCOPED",
    "REMEDIATING",
    "RECOVERING",
    "VERIFYING",
    "RESOLVED",
    "POSTMORTEM",
    "ACTIONS_TRACKED",
}


def validate_state(state: str) -> None:
    if state not in VALID_STATES:
        raise ValueError(f"Unknown incident state: {state}")
```

These examples are educational. A production incident system needs durable persistence, authorization, concurrency control, retries, auditability, and integrations.

---

## 39. SQL Incident Investigation

### Detect duplicates

```sql
SELECT
    customer_id,
    order_id,
    COUNT(*) AS duplicate_count
FROM orders
GROUP BY customer_id, order_id
HAVING COUNT(*) > 1;
```

### Detect missing partitions

```sql
SELECT
    DATE(event_time) AS event_date,
    COUNT(*) AS row_count
FROM events
GROUP BY DATE(event_time)
ORDER BY event_date DESC;
```

A missing expected date can be an ingestion/freshness signal.

### Detect null spikes

```sql
SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_ids
FROM orders;
```

### Compare source and target

```sql
SELECT
    COUNT(*) AS target_rows,
    SUM(amount) AS target_amount
FROM warehouse_orders
WHERE order_date = DATE '2026-01-10';
```

Compare with independently obtained source values.

### Identify recent loads

```sql
SELECT
    batch_id,
    started_at,
    completed_at,
    status
FROM pipeline_runs
ORDER BY started_at DESC
LIMIT 20;
```

Investigation should correlate these results with deployment and observability metadata.

---

## 40. Failure Injection Lab

Build a local incident simulation.

The required lifecycle for both mandatory drills is:

```text
Inject
→ Detect
→ Declare
→ Triage
→ Contain
→ Scope
→ Remediate
→ Recover
→ Verify
→ Communicate
→ Postmortem
→ Prevent
→ Re-test
```

The two mandatory scenarios are:

1. **Cents-vs-currency revenue incident**
2. **PII exposure incident**

---

## 41. Scenario A — Cents-vs-Currency Revenue Incident

### Incident

The pipeline incorrectly treats cents as dollars.

```text
Expected:
$10.50

Actual:
$1050.00
```

### Inject

Introduce a transformation defect:

```python
def convert_amount(raw_amount: int) -> float:
    # BUG: raw_amount is cents, but this treats it as dollars.
    return float(raw_amount)
```

Expected implementation:

```python
def convert_amount(raw_amount: int) -> float:
    return raw_amount / 100.0
```

### Detect

A reconciliation check compares expected source semantics with downstream totals.

```python
def assert_reasonable_currency(
    amount: float,
    expected_max: float,
) -> None:
    if amount > expected_max:
        raise ValueError(
            f"Currency value {amount} exceeds expected maximum"
        )
```

### Declare

Create an incident:

```text
Incident ID: INC-CURRENCY-001
Severity: SEV-2
Impact: Revenue dashboards and reports
```

### Triage

Determine:

- first bad run;
- affected interval;
- affected tables;
- affected dashboards;
- affected consumers.

### Contain

Pause publication of affected outputs.

### Scope

Use lineage:

```text
orders
  ↓
silver_orders
  ↓
gold_revenue
  ↓
warehouse_revenue
  ↓
finance_dashboard
```

### Remediate

Fix conversion logic.

### Recover

Reprocess the affected interval.

### Verify

Compare:

- source revenue;
- target revenue;
- row counts;
- aggregate totals;
- downstream dashboard values.

### Communicate

State:

```text
Revenue data for the affected interval was incorrect.
Publication was paused. The transformation has been fixed
and the affected interval is being rebuilt.

Next update: <approved time>.
```

### Postmortem

Root cause:

```text
Unit conversion defect.
```

Contributing factors:

```text
No unit assertion
No reconciliation
No canary
Insufficient alerting
```

### Prevent

Create:

- unit-validation tests;
- data-quality check;
- reconciliation;
- alert;
- runbook.

### Re-test

Re-run the incident simulation and confirm the new controls detect the defect earlier.

---

## 42. Scenario B — PII Exposure Incident

### Incident

An application or pipeline logs an email address:

```text
INFO customer_email=john@example.com
```

### Inject

Introduce an unsafe logging statement:

```python
def log_customer_failure(customer_email: str, logger) -> None:
    logger.info("customer_email=%s payment failed", customer_email)
```

### Detect

Possible signals:

- PII scanning alert;
- security monitoring;
- log-classification rule;
- human report.

### Declare

Classify as a technical incident with potential security/privacy impact.

### Triage

Determine:

- which logs contain the PII;
- time window;
- affected environments;
- log destinations;
- access paths;
- downstream copies.

### Contain

Potential actions include:

- stop further PII logging;
- disable affected code path;
- restrict access to affected logs;
- prevent additional propagation.

### Scope

Trace:

```text
Application
   ↓
Log collector
   ↓
Central logging
   ↓
Archive
   ↓
Security analytics
```

Also identify whether logs were exported to other systems.

### Evidence preservation

Preserve the information needed by the security/privacy process before applying cleanup or retention actions.

### Security/privacy escalation

Notify the appropriate security, privacy, governance, and legal teams according to organizational procedures.

Do not invent notification deadlines.

### Remediate

Use structured logging without direct PII:

```python
def log_customer_failure(request_id: str, logger) -> None:
    logger.info(
        "payment_failed",
        extra={"request_id": request_id},
    )
```

### Verify

Scan affected log paths and run regression tests.

### Postmortem

Root cause:

```text
Application logged a direct personal identifier.
```

Contributing factors:

```text
No PII log guard
No automated scanning
No structured logging policy enforcement
```

### Prevent

Implement:

- PII log scanning;
- redaction where appropriate;
- structured logging;
- sensitive-field deny lists;
- automated tests;
- code review checks;
- runbook updates.

### Re-test

Run the same drill again.

Success means:

```text
Unsafe log attempt
   ↓
Automated control detects/blocks
   ↓
No PII reaches governed logs
```

The second drill demonstrates improvement rather than merely repeating the first incident.

---

## 43. Incident State Machine

Use an explicit state model:

```text
DETECTED
   ↓
DECLARED
   ↓
TRIAGING
   ↓
CONTAINED
   ↓
SCOPED
   ↓
REMEDIATING
   ↓
RECOVERING
   ↓
VERIFYING
   ↓
RESOLVED
   ↓
POSTMORTEM
   ↓
ACTIONS_TRACKED
```

Possible failure/retry states include:

```text
CONTAINMENT_FAILED
RECOVERY_FAILED
VERIFICATION_FAILED
WAITING_ON_DEPENDENCY
ESCALATED
```

### Why explicit state matters

A state machine prevents the system from incorrectly representing:

```text
Recovery failed
      ↓
RESOLVED
```

Instead:

```text
Recovery failed
      ↓
RECOVERY_FAILED
      ↓
Retry / Escalate
```

---

## 44. Incident Evidence Pack

A production evidence package can contain:

```text
Incident ID
Timestamps
Affected datasets
Affected consumers
Alerts
Logs
Traces
Metrics
Pipeline runs
Git SHA
Image digest
Configuration
Lineage graph
Recovery actions
Validation results
Communication history
Postmortem
Action items
```

### Why this matters

It supports:

- auditability;
- debugging;
- organizational learning;
- security/privacy investigation;
- reproducibility;
- future prevention.

Evidence should have appropriate access controls and retention.

---

## 45. Testing

### Unit tests

Test:

- severity classification;
- incident state transitions;
- reconciliation logic;
- blast-radius calculation.

Example:

```python
def classify_severity(
    consumer_count: int,
    privacy_exposure: bool,
) -> str:
    if privacy_exposure:
        return "SEV-1"
    if consumer_count >= 100:
        return "SEV-2"
    return "SEV-3"


def test_privacy_exposure_escalates():
    assert classify_severity(1, True) == "SEV-1"
```

The exact severity thresholds are organization-specific; the example demonstrates the testing pattern.

### Integration tests

Test:

- monitoring signals;
- pipeline failure detection;
- lineage lookup;
- run metadata;
- incident creation.

### End-to-end tests

```text
Failure
  ↓
Alert
  ↓
Incident
  ↓
Containment
  ↓
Recovery
  ↓
Verification
```

### Regression tests

Every postmortem control should have a durable regression test where practical.

```text
Postmortem action
      ↓
Control implemented
      ↓
Regression test
      ↓
Future change
      ↓
Test remains green
```

---

## 46. Common Production Mistakes

| Mistake | Why it happens | Risk | Correct approach |
|---|---|---|---|
| No clear incident owner | Everyone assumes someone else leads | Slow decisions | Name an IC |
| Everyone debugs simultaneously | No coordination | Conflicting changes | Separate roles |
| No incident declaration | Team stays in ad-hoc mode | Poor communication | Declare explicitly |
| No severity | Impact is unclear | Wrong escalation | Use impact model |
| Poor communication | Technical focus dominates | Stakeholder confusion | Scheduled factual updates |
| Guessing | Pressure to act quickly | Wrong remediation | Gather evidence |
| Changing production before containment | Fear of delay | Expands blast radius | Contain first |
| Destroying evidence | Cleanup done too early | Lost investigation data | Preserve evidence |
| Ignoring lineage | Single-system thinking | Missed downstream impact | Use lineage + inventory |
| Green pipeline = correct | Operational success mistaken for data quality | Silent corruption | Verify data |
| Incomplete blast radius | Limited investigation | Consumers remain affected | Scope systematically |
| Incomplete recovery verification | Fix assumed correct | Recurrence | Independent checks |
| Weak runbooks | Knowledge is tribal | Slow response | Maintain tested runbooks |
| Blame-oriented postmortem | Fear | Weak learning | Blameless analysis |
| Vague actions | Easy to write | No durable change | Owner + due date + acceptance |
| No owners | Nobody accountable | Actions remain open | Assign ownership |
| No due dates | No urgency | Drift | Set approved deadline |
| No follow-up | Postmortem becomes archive | Recurrence | Track to closure |
| Repeat incidents | Root cause not addressed | Operational instability | Measure recurrence |
| No game days | Process untested | Surprises in real incident | Simulate |
| Actions not controls | Lessons remain prose | No prevention | Convert to tests/alerts/runbooks |

---

## 47. Production Incident Architecture

A complete architecture:

```text
                   Observability
                        |
          +-------------+-------------+
          |             |             |
       Metrics        Logs         Traces
          |             |             |
          +-------------+-------------+
                        |
                      Alerts
                        |
                 Incident System
                        |
                 Incident Commander
                        |
          +-------------+-------------+
          |             |             |
     Technical       Comms          Scribe
     Responder        Lead
          |
          v
 Triage → Contain → Scope → Remediate
                        |
                        v
                     Recover
                        |
                        v
                      Verify
                        |
                        v
                   Postmortem
                        |
                        v
               Corrective Actions
                        |
             +----------+----------+
             |          |          |
           Tests      Alerts    Runbooks
```

### Component responsibilities

**Observability:** produce signals.

**Alerting:** surface actionable symptoms.

**Incident system:** track incident state.

**Incident Commander:** coordinate response.

**Technical responder:** diagnose and remediate.

**Communications lead:** maintain stakeholder awareness.

**Scribe:** preserve timeline/evidence.

**Lineage/inventory:** scope impact.

**Verification:** prove recovery.

**Postmortem:** convert experience into improvements.

---

## 48. End-to-End Enterprise Incident Example

### Scenario

A production pipeline introduces incorrect revenue calculations that propagate through:

```text
API
 ↓
PostgreSQL
 ↓
Kafka
 ↓
Spark
 ↓
Lakehouse
 ↓
Warehouse
 ↓
BI
 ↓
ML Features
```

### 1. Detection

A revenue reconciliation check detects a large deviation.

```text
Expected: $10.5M
Actual:   $1050M
```

### 2. Incident declaration

Declare an incident and assign:

- IC;
- technical responder;
- communications lead;
- scribe.

### 3. Severity

Financial reporting impact makes this a major production incident under the organization's severity model.

### 4. Triage

Identify:

- first bad run;
- code version;
- affected interval;
- current pipeline state.

### 5. Containment

Pause downstream publication and stop the faulty pipeline.

### 6. Blast radius

Use lineage:

```text
Silver
  ↓
Gold
  ↓
Warehouse
  ↓
BI
  ↓
Feature Table
```

### 7. Root cause

The transformation converted cents directly into dollars.

### 8. Remediation

Fix the transformation and add a unit test.

### 9. Backfill

Reprocess only the affected interval.

### 10. Recovery

Republish corrected outputs.

### 11. Verification

Run:

- row-count reconciliation;
- revenue reconciliation;
- business invariants;
- downstream dashboard checks.

### 12. Communication

Communicate:

- impact;
- containment;
- current state;
- expected recovery;
- verification status.

### 13. Postmortem

Identify:

```text
Root cause:
Unit conversion defect.

Contributing factors:
No unit validation.
No reconciliation.
No canary.
Insufficient alerting.
```

### 14. Corrective actions

```text
Add unit tests
Add reconciliation
Add alert
Improve deployment validation
Add runbook
```

### 15. Game-day follow-up

Inject the same class of defect in a controlled environment and verify the new controls detect it earlier.

---

## 49. Checkpoint Questions

### Questions

1. What is a data incident?
2. When does a data-quality problem become an incident?
3. How should severity be determined?
4. What does an Incident Commander do?
5. What is triage?
6. What is containment?
7. What is blast radius?
8. How does lineage help incident response?
9. What is the last known good state?
10. Why is a green pipeline not proof of correct data?
11. What should be verified before closing an incident?
12. What is a blameless postmortem?
13. What are the Five Whys?
14. What is the difference between root cause and contributing factors?
15. How should action items become engineering controls?
16. What is Time to Detect?
17. What is Time to Mitigate?
18. What is Time to Resolve?
19. What is a game day?
20. How do game days improve operational readiness?

### Model answers

**1. What is a data incident?**  
A production event that materially affects data correctness, availability, freshness, integrity, confidentiality, or trustworthy use.

**2. When does a data-quality issue become an incident?**  
When it causes meaningful consumer, business, security, privacy, or operational impact requiring coordinated response.

**3. How should severity be determined?**  
Evaluate consumer/business impact, correctness, availability, freshness, security/privacy, compliance, scope, and duration.

**4. What does the IC do?**  
Coordinates decisions, prioritization, escalation, and overall incident response.

**5. What is triage?**  
Evidence-driven initial assessment of what happened, impact, current state, and likely scope.

**6. What is containment?**  
Actions that stop the incident from expanding.

**7. What is blast radius?**  
The set of datasets, records, time periods, systems, consumers, regions, and downstream assets affected.

**8. How does lineage help?**  
It exposes dependencies and downstream assets that may have inherited the bad data.

**9. What is the last known good state?**  
The most recent state independently known to be correct and trustworthy.

**10. Why is green not proof?**  
Pipeline execution success says little about semantic correctness of the produced data.

**11. What should be verified?**  
Counts, aggregates, checksums where suitable, data quality, freshness, schema, reconciliation, and downstream outputs.

**12. What is a blameless postmortem?**  
A structured analysis focused on system conditions and controls rather than personal blame.

**13. What are Five Whys?**  
A questioning method that repeatedly asks why until the team reaches a useful causal explanation.

**14. Root cause vs contributing factors?**  
Root cause identifies a primary causal condition; contributing factors identify additional conditions that allowed or amplified the incident.

**15. How do actions become controls?**  
Translate them into tests, checks, alerts, dashboards, runbooks, policy controls, or deployment safeguards.

**16. TTD?**  
Time from incident start to detection.

**17. TTM?**  
Time from incident start until impact is materially reduced.

**18. TTR?**  
Time from incident start until the incident is fully resolved and verified.

**19. Game day?**  
A controlled failure simulation used to test operational readiness.

**20. Why game days?**  
They expose gaps in alerts, roles, runbooks, recovery, communication, and tooling before real incidents do.

---

## 50. Interview Preparation

### Beginner

**Q: What is a data incident?**  
A: A production event that materially affects trustworthy data or its secure/available use.

**Q: What is incident severity?**  
A: A classification of incident impact used to determine response urgency and escalation.

**Q: What is triage?**  
A: Initial evidence-driven assessment of the event and its impact.

**Q: What is a postmortem?**  
A: Structured analysis of an incident to understand causes, response, and prevention.

### Intermediate

**Q: Incident Commander vs technical responder?**  
A: The IC coordinates; the technical responder investigates and executes technical work.

**Q: Containment vs remediation?**  
A: Containment stops further impact; remediation fixes the underlying problem.

**Q: What is blast radius?**  
A: The full set of affected data, systems, consumers, and downstream assets.

**Q: Why reconcile data?**  
A: To independently verify that recovered data matches expected source/business state.

**Q: What is a runbook?**  
A: An operational procedure for handling a known class of failure.

**Q: Why track incident metrics?**  
A: To identify systemic weaknesses in detection, mitigation, recovery, and repeat failures.

### Advanced

**Q: How do you use lineage during an incident?**  
A: Start at the bad source/output and traverse downstream dependencies to identify affected tables, dashboards, pipelines, and features.

**Q: How do you handle incorrect financial data?**  
A: Contain publication, identify the bad interval, scope downstream impact, fix/reprocess, reconcile financial totals, verify consumers, communicate status, and create preventive controls.

**Q: How do you scope a PII exposure?**  
A: Preserve evidence, identify the field and time window, trace log/data destinations and access, identify affected environments, and escalate to security/privacy processes.

**Q: How do you design recovery?**  
A: Use the last known good state, targeted rollback/replay/backfill, reconciliation, and independent verification.

### Senior / Production

**Q: Design a data incident-response process.**  
A: Combine observability, actionable alerts, severity classification, incident command, technical response, communications, scribe, lineage/inventory, containment, remediation, verification, postmortems, and action tracking.

**Q: How do you prevent recurring incidents?**  
A: Convert root causes and contributing factors into durable tests, checks, alerts, runbooks, deployment safeguards, and game-day scenarios.

**Q: How do you measure operational maturity?**  
A: Track TTD, TTM, TTR, repeat incident rate, automated detection, consumer impact duration, action closure, and game-day performance.

**Q: What makes a postmortem useful?**  
A: Evidence-backed causal analysis, clear impact, specific actions, accountable owners, due dates, acceptance criteria, and verified controls.

---

## 51. Final Assessment

This assessment is intentionally production-oriented.

### Scenario

A Data Platform processes financial, customer, and operational data through:

```text
API
 ↓
PostgreSQL
 ↓
Kafka
 ↓
Spark
 ↓
Lakehouse
 ↓
Warehouse
 ↓
BI
 ↓
ML Features
 ↓
Logs / Observability
```

A production transformation starts generating incorrect data.

### Tasks

1. Classify the incident.
2. Determine severity.
3. Define incident roles.
4. Perform triage.
5. Design containment.
6. Determine blast radius.
7. Use lineage to scope downstream impact.
8. Identify the last known good state.
9. Investigate root cause.
10. Separate root cause from contributing factors.
11. Design remediation.
12. Design backfill/replay.
13. Reconcile source and target.
14. Define verification.
15. Design stakeholder communication.
16. Determine whether security/privacy escalation is required.
17. Define evidence preservation.
18. Write a postmortem structure.
19. Apply Five Whys.
20. Define corrective actions.
21. Define preventive actions.
22. Assign owners and due dates.
23. Define TTD/TTM/TTR measurements.
24. Design a game day.
25. Convert postmortem actions into automated controls.

### Required implementation

Provide:

- Python;
- SQL;
- incident state machine;
- lineage-based scope;
- reconciliation;
- failure simulation;
- verification;
- postmortem;
- preventive controls.

Do not answer with definitions alone. Demonstrate operational reasoning.

---

## 52. Production Challenge

> **Design and operate a complete incident-response system for an enterprise Data Platform processing financial, customer, and operational data through APIs, Kafka, PostgreSQL, Spark, a lakehouse, a warehouse, BI systems, ML features, logs, and observability infrastructure.**

Your design must include:

- incident taxonomy;
- severity model;
- detection;
- alerting;
- Incident Commander model;
- technical responder;
- communications lead;
- scribe;
- triage;
- containment;
- blast-radius analysis;
- lineage-based scoping;
- root-cause analysis;
- recovery;
- reconciliation;
- stakeholder communication;
- privacy/security escalation;
- evidence preservation;
- postmortem;
- Five Whys;
- corrective actions;
- preventive controls;
- incident metrics;
- game days.

### Senior-level trade-off reasoning

For each major design choice, explain:

```text
Option A
  ↓
Benefits
  ↓
Risks
  ↓
Operational cost
  ↓
Failure modes
  ↓
Recovery implications
  ↓
Why selected
```

A strong solution should answer:

> How do you maintain calm, evidence-driven control when the data is wrong, consumers are waiting, and the root cause is not yet known?

---

## 53. Glossary

| Term | Meaning |
|---|---|
| Incident | Event requiring coordinated response because of meaningful impact |
| Data incident | Incident involving data correctness, availability, freshness, integrity, confidentiality, or trustworthy use |
| Severity | Classification of impact and response urgency |
| Incident Commander | Person coordinating the overall incident response |
| Technical responder | Person/team performing investigation and technical remediation |
| Communications lead | Person coordinating stakeholder communication |
| Scribe | Person recording timeline, decisions, actions, and evidence |
| Triage | Initial evidence-driven assessment |
| Containment | Actions that stop further impact |
| Blast radius | Full scope of affected data, systems, consumers, and dependencies |
| Root cause | Primary causal condition identified through investigation |
| Contributing factor | Additional condition that enabled or amplified the incident |
| Remediation | Work that fixes the underlying problem |
| Recovery | Restoration of trustworthy service/data |
| Verification | Evidence that recovery succeeded |
| Reconciliation | Independent comparison of expected and actual state |
| Last known good state | Most recent state known to be correct |
| Lineage | Relationships among datasets, jobs, runs, and downstream assets |
| Runbook | Documented operational response procedure |
| Postmortem | Structured analysis after an incident |
| Blameless postmortem | Postmortem focused on system conditions rather than personal blame |
| Five Whys | Iterative questioning technique for causal analysis |
| Corrective action | Action that fixes an immediate problem |
| Preventive action | Action intended to reduce recurrence |
| Time to Detect | Time from incident start to detection |
| Time to Mitigate | Time from incident start to meaningful impact reduction |
| Time to Resolve | Time from incident start to full verified resolution |
| Game day | Controlled failure simulation |
| Evidence preservation | Protecting incident artifacts needed for investigation/audit |
| Incident state | Current lifecycle status of an incident |
| Incident timeline | Timestamped record of incident events |
| Data trust | Degree to which consumers can rely on data correctness and freshness |

---

## 54. Incident Response Checklist

```text
[ ] I understand what constitutes a data incident.
[ ] I can classify data incidents.
[ ] I can determine severity.
[ ] I understand incident roles.
[ ] I understand Incident Commander responsibilities.
[ ] I can perform triage.
[ ] I can contain an incident.
[ ] I can determine blast radius.
[ ] I can use lineage for incident scoping.
[ ] I can identify the last known good state.
[ ] I can investigate root cause.
[ ] I can perform reconciliation.
[ ] I can plan remediation.
[ ] I can recover affected data.
[ ] I can verify recovery.
[ ] I can communicate incident status.
[ ] I understand privacy/security escalation.
[ ] I can preserve evidence.
[ ] I can create a runbook.
[ ] I can write a blameless postmortem.
[ ] I can use Five Whys.
[ ] I can identify root causes and contributing factors.
[ ] I can create actionable corrective actions.
[ ] I can assign owners and due dates.
[ ] I understand TTD.
[ ] I understand TTM.
[ ] I understand TTR.
[ ] I can design a game day.
[ ] I can measure incident improvement.
[ ] I can convert postmortem actions into tests.
[ ] I can convert postmortem actions into alerts.
[ ] I can convert postmortem actions into runbooks.
[ ] I can operate a production data incident.
```

---

## 55. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Section | Code/Example? |
|---|---|---|---|
| Data incident definition | Yes | 3 | Yes |
| Wrong data | Yes | 3, 41 | Yes |
| Late data | Yes | 3 | Yes |
| Missing data | Yes | 3 | Yes |
| Exposed data | Yes | 3, 42 | Yes |
| Corrupted data | Yes | 3 | Yes |
| Severity | Yes | 5 | Yes |
| Incident classification | Yes | 3, 5 | Yes |
| Detection sources | Yes | 6 | Yes |
| Alert-driven incident response | Yes | 6–7 | Yes |
| Human-reported incidents | Yes | 6 | Yes |
| Incident Commander | Yes | 8–9 | Yes |
| Technical responder | Yes | 8–9 | Yes |
| Communications lead | Yes | 8–9 | Yes |
| Scribe | Yes | 8–9 | Yes |
| Triage | Yes | 10 | Yes |
| Containment | Yes | 11 | Yes |
| Blast-radius analysis | Yes | 12 | Yes |
| Lineage-based scoping | Yes | 13 | Yes |
| Root cause | Yes | 14 | Yes |
| Remediation | Yes | 17 | Yes |
| Recovery | Yes | 18 | Yes |
| Verification | Yes | 19 | Yes |
| Stakeholder communication | Yes | 21 | Yes |
| Privacy/security escalation | Yes | 23 | Yes |
| Evidence preservation | Yes | 24 | Yes |
| Notification awareness | Yes | 23 | Yes |
| Blameless postmortem | Yes | 27 | Yes |
| Incident timelines | Yes | 16 | Yes |
| Impact analysis | Yes | 12–13 | Yes |
| Five Whys | Yes | 29 | Yes |
| Corrective actions | Yes | 31–32 | Yes |
| Preventive actions | Yes | 31–32 | Yes |
| Action owners | Yes | 33 | Yes |
| Due dates | Yes | 33 | Yes |
| Action items → tests | Yes | 32, 37 | Yes |
| Action items → alerts | Yes | 32, 37 | Yes |
| Action items → runbooks | Yes | 32, 37 | Yes |
| Incident metrics | Yes | 34 | Yes |
| Time to Detect | Yes | 34 | Yes |
| Time to Mitigate | Yes | 34 | Yes |
| Time to Resolve | Yes | 34 | Yes |
| Repeat incidents | Yes | 34 | Yes |
| Game days | Yes | 35–36 | Yes |
| Incident simulations | Yes | 40–42 | Yes |
| Measuring improvement | Yes | 35, 36 | Yes |
| Cents-vs-currency scenario | Yes | 41 | Yes |
| PII exposure scenario | Yes | 42 | Yes |
| Second-drill improvement | Yes | 42 | Yes |

---

## 56. Operational Accuracy Requirements

### Do not

- encourage uncontrolled production changes;
- encourage deleting evidence;
- blame individuals;
- assume the first hypothesis is correct;
- treat pipeline success as proof of data correctness;
- claim lineage is always complete;
- claim alerts automatically identify root cause;
- treat postmortems as punishment;
- create vague corrective actions;
- invent one incident-management process as a universal standard.

### Always

- prioritize consumer impact;
- contain before making risky changes;
- collect evidence;
- preserve timestamps;
- use lineage for blast-radius analysis;
- distinguish symptoms from causes;
- verify data recovery;
- communicate uncertainty clearly;
- preserve evidence for security/privacy incidents;
- create measurable corrective actions;
- assign owners and deadlines;
- test preventive controls;
- perform follow-up game days.

---

## 57. Production Reasoning Framework

For every incident, ask:

```text
What happened?
When did it start?
How was it detected?
Who is affected?
What data is affected?
What consumers are affected?
What is the severity?
Is the incident still expanding?
What can we safely contain?
What is the blast radius?
What does lineage show?
What is the last known good state?
What evidence do we have?
What changed?
What is the root cause?
What are the contributing factors?
How do we recover?
How do we verify recovery?
Who needs to be informed?
Is this a security/privacy incident?
What evidence must be preserved?
What permanent controls should change?
How will we know the fix works?
```

The goal is to develop **calm, evidence-driven, production incident-response thinking**.

---

## 58. Final Quality Bar

Before considering this module complete, verify that it is:

- beginner-friendly;
- technically accurate;
- operationally realistic;
- production-oriented;
- practical;
- code-driven;
- progressively structured;
- aligned with the roadmap;
- blameless;
- evidence-driven;
- complete;
- internally consistent.

The learner should be able to participate in or lead a production Data Engineering incident with:

- Data Engineers;
- Data Architects;
- Platform Engineers;
- SRE/DevOps Engineers;
- Security Engineers;
- Privacy/Governance teams;
- Product/Business stakeholders.

### Final capability

The goal is not to memorize incident-management vocabulary.

The goal is to reason through:

```text
Signal
  ↓
Impact
  ↓
Triage
  ↓
Containment
  ↓
Blast Radius
  ↓
Lineage
  ↓
Root Cause
  ↓
Remediation
  ↓
Recovery
  ↓
Verification
  ↓
Communication
  ↓
Postmortem
  ↓
Preventive Controls
  ↓
Game Day
  ↓
Improvement
```

A production Data Engineer should be able to answer:

> **What happened, what is affected, how do we safely contain it, what evidence supports our hypothesis, how do we restore trustworthy data, how do we prove recovery, and what permanent engineering controls prevent recurrence?**
