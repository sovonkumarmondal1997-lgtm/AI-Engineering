# Task Retries, Deadlines, and Failure Callbacks in Apache Airflow 3.x

> **Production-oriented learning chapter for Data Engineers**
>
> Primary version: **Apache Airflow 3.x**
>
> Core lifecycle:
>
> **failure → classify → retry or fail fast → timeout/deadline evaluation → callback → actionable alert → runbook → recovery**

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- classify transient and permanent failures;
- explain what a retry is and how Airflow counts attempts;
- configure bounded retries;
- choose retry delays based on failure characteristics;
- explain exponential backoff and maximum retry delay;
- design idempotent tasks that are safe to retry;
- distinguish Airflow-level retries from retries inside application code;
- avoid nested retry explosions;
- decide when to fail fast;
- configure task execution timeouts;
- distinguish task execution timeout from a workflow/data deadline;
- explain the historical Airflow 2.x SLA concept and why it is not the current Airflow 3.x approach;
- describe Airflow 3.x Deadline Alerts and deadline-oriented monitoring;
- implement failure, retry, and success callbacks;
- design structured, actionable alerts;
- reason about alert severity and alert fatigue;
- handle partial failure in dynamically mapped tasks;
- distinguish task success from data freshness success;
- write operational runbooks;
- test failure behavior without requiring a real notification system;
- inject failures deliberately;
- observe retry and failure metrics;
- design production failure-management architecture;
- answer advanced interview and architecture questions.

### The central principle

A production retry policy is **not**:

```text
failure → try again
```

It is:

```text
Task fails
    ↓
Classify the failure
    ↓
Is it transient?
 ┌───────────────┴───────────────┐
Yes                             No
 ↓                               ↓
Is retry safe?                 Fail fast
 ↓                               ↓
Yes ──→ bounded retry          Alert/investigate
 ↓
backoff + timeout
 ↓
success?
 ┌──────┴──────┐
Yes            No
 ↓              ↓
continue      final failure
                 ↓
              callback
                 ↓
              alert
                 ↓
              runbook
                 ↓
              recovery
```

---

## 2. Prerequisites

This chapter assumes you already understand:

- DAGs and dependencies;
- Airflow tasks and operators;
- TaskFlow;
- Connections, Variables, Hooks, and XComs;
- sensors and deferrable operators;
- basic Python;
- basic SQL;
- production data-pipeline concepts such as idempotency and partitioned processing.

Those subjects are not re-taught here. They are referenced only when they affect failure management.

---

# 3. Why Production Tasks Fail

A task can fail because of the task itself, its input, a dependency, infrastructure, or an external service.

Common examples include:

| Failure | Likely transient? | Retry? | Reason |
|---|---:|---:|---|
| Temporary database connection failure | Often | Usually | Dependency may recover |
| Network timeout | Often | Usually | Network condition may disappear |
| API rate limit | Often | Usually | Backoff gives provider time |
| Temporary SFTP outage | Often | Usually | Remote service may recover |
| Object-storage transient error | Often | Usually | Infrastructure condition may clear |
| DNS failure | Sometimes | Often bounded | Resolver/service may recover |
| Connection-pool exhaustion | Sometimes | Depends | Retry without fixing saturation may worsen load |
| Temporary upstream outage | Often | Usually | External dependency may recover |
| Database lock timeout | Often | Usually bounded | Later attempt may acquire lock |
| Malformed input | Usually no | Usually no | Same input remains malformed |
| Schema/contract violation | Usually no | No blind retry | Requires investigation or producer fix |
| Invalid credentials | No | No | Repeating the same credential cannot repair it |
| Missing configuration | No | No | Configuration must be corrected |
| Programming bug | No | Usually no | Retry repeats defective code |
| Resource exhaustion | Depends | Depends | Retry can amplify pressure |

The important production skill is not memorizing which exception is always retryable.

The skill is **classifying the failure from evidence**.

---

# 4. Failure Taxonomy

## 4.1 Transient failure

A transient failure is a condition that may disappear without changing the task's logic or input.

Examples:

- temporary network outage;
- database unavailable for a short period;
- API rate limit;
- temporary DNS failure;
- object-storage service interruption;
- short-lived lock contention.

A retry can be useful because the environment may be different on the next attempt.

## 4.2 Permanent failure

A permanent failure is a condition where another identical attempt is unlikely to succeed.

Examples:

- invalid credentials;
- missing required secret;
- malformed input;
- invalid SQL;
- incompatible schema;
- programming defect;
- invalid configuration.

Blind retries consume resources and delay diagnosis.

## 4.3 Conditional failures

Some failures require context.

For example:

```text
HTTP 429 → usually retryable
HTTP 401 → usually not retryable until credentials change
HTTP 500 → often retryable
HTTP 400 → often a request/input problem
```

These are **heuristics**, not universal laws. Provider-specific behavior and API contracts matter.

---

# 5. What Is a Retry?

A retry means Airflow gives a task another execution attempt after a failure.

Conceptually:

```text
Attempt 1
   ↓
failure
   ↓
wait
   ↓
Attempt 2
   ↓
failure
   ↓
wait
   ↓
Attempt 3
   ↓
success
```

Important vocabulary:

- **initial attempt** — the first execution;
- **retry** — an additional execution after failure;
- **retry count** — configured number of additional attempts;
- **try number** — attempt identity visible in task context/UI;
- **final failure** — failure after the retry policy is exhausted;
- **task state** — Airflow's state for the task instance.

The key arithmetic is:

```text
total possible executions = 1 + retries
```

Therefore:

```text
retries=0 → 1 possible execution
retries=3 → up to 4 possible executions
```

This matters for capacity, API load, task duration, and deadlines.

---

# 6. Retry Configuration

A representative Airflow 3.x TaskFlow task can be configured with:

```python
from datetime import timedelta

from airflow.sdk import dag, task


@dag(
    dag_id="retry_example",
    schedule="@daily",
    catchup=False,
)
def retry_example():

    @task(
        retries=3,
        retry_delay=timedelta(minutes=5),
        retry_exponential_backoff=True,
        max_retry_delay=timedelta(minutes=30),
    )
    def extract_orders():
        # Perform one bounded unit of work.
        ...

    extract_orders()


retry_example()
```

The exact behavior should be checked against the Airflow version installed by your environment.

### Main controls

| Control | Meaning |
|---|---|
| `retries` | Maximum number of additional task attempts |
| `retry_delay` | Base delay between retry attempts |
| `retry_exponential_backoff` | Makes retry delay grow rather than remain constant |
| `max_retry_delay` | Upper bound for calculated retry delay |
| `execution_timeout` | Maximum runtime of an individual task execution |

Airflow's current documentation exposes these task retry controls, and current Airflow 3.x documentation also supports a retry policy abstraction for more detailed exception-aware behavior. citeturn1search9turn1search10

---

# 7. Retry Count

Consider:

```python
@task(retries=3)
def load():
    ...
```

The task may execute:

```text
initial attempt
      ↓
retry 1
      ↓
retry 2
      ↓
retry 3
```

Maximum executions:

```text
1 + 3 = 4
```

It is a common beginner mistake to read `retries=3` as "the task runs three times total."

It means **three additional retry opportunities** after the initial attempt.

### Operational consequence

Suppose:

- 100 mapped task instances exist;
- each has `retries=3`.

The scheduler may need to manage up to:

```text
100 × 4 = 400 task executions
```

if every instance fails every attempt.

That does not mean 400 executions will necessarily run simultaneously. Concurrency limits, pools, scheduling, and worker capacity still apply.

But it demonstrates why retry configuration is a capacity decision.

---

# 8. Retry Delay

Immediate retries can amplify an outage.

Bad pattern:

```text
failure
 ↓
immediate retry
 ↓
failure
 ↓
immediate retry
 ↓
failure
```

If an API is already overloaded, every failed task immediately sending another request can increase pressure.

A bounded delay creates recovery space:

```text
failure
 ↓
wait
 ↓
retry
```

### Delay should match the failure

Examples:

- short network interruption → relatively short delay may be sufficient;
- API rate limit → delay should respect provider guidance where available;
- database failover → allow time for recovery;
- planned external availability window → retry policy may need a longer horizon;
- permanent validation error → no delay is useful because no retry is appropriate.

There is no universal "correct" retry delay.

---

# 9. Exponential Backoff

With fixed delay:

```text
5 min
5 min
5 min
5 min
```

With exponential backoff:

```text
5 min
10 min
20 min
40 min
...
```

The exact sequence depends on the configured base delay, multiplier, implementation, and cap.

Exponential backoff is useful because repeated callers gradually reduce pressure on a struggling dependency.

Current Airflow 3.3 documentation supports numeric `retry_exponential_backoff` multipliers; for example, `2.0` represents a doubling multiplier, while boolean compatibility is retained in Python DAGs. citeturn1search10

### Why backoff helps

It can reduce:

- retry storms;
- synchronized request bursts;
- pressure on rate-limited APIs;
- repeated database connection attempts;
- load during partial outages.

### Jitter

If many tasks fail simultaneously, identical backoff schedules can still synchronize:

```text
100 tasks
   ↓
all fail
   ↓
all wait 5 minutes
   ↓
all retry together
```

Jitter introduces variation in retry timing.

Conceptually:

```text
base delay + random variation
```

The important principle is:

> Backoff reduces pressure; jitter reduces synchronization.

Do not claim that jitter is a universal requirement. Use it when the dependency and workload make synchronized retries a concern.

---

# 10. Maximum Retry Delay

Backoff without a ceiling can produce increasingly long waits.

Example:

```text
1 min
2 min
4 min
8 min
16 min
32 min
...
```

A production policy may impose a ceiling:

```text
1 min
2 min
4 min
8 min
15 min
15 min
...
```

The exact cap is workload-specific.

### Why a cap matters

Without a cap:

- recovery can become too slow;
- deadline calculations become difficult;
- incidents remain unresolved for long periods;
- operators may not understand when the next attempt will happen.

Airflow exposes `max_retry_delay` as the maximum interval between retries. citeturn1search2

---

# 11. Retry Design by Failure Type

| Failure | Retry strategy | Main concern |
|---|---|---|
| API 429 | Bounded backoff; respect provider guidance | Rate limits |
| Temporary DB connection failure | Bounded retry + backoff | Dependency recovery |
| Temporary SFTP outage | Retry + backoff | Remote availability |
| Invalid credentials | Fail fast | Repeating bad credentials |
| Schema violation | Fail fast | Input/contract repair |
| Malformed file | Fail fast or quarantine | Same file remains invalid |
| Programming bug | Usually fail fast | Repeating defective code |
| Lock timeout | Bounded retry | Contention |
| Object storage temporary error | Retry + backoff | Service recovery |
| Resource exhaustion | Diagnose before retrying | Retry may increase pressure |

The correct question is:

> "What condition caused this failure, and can a later attempt plausibly encounter a different condition?"

---

# 12. Idempotency and Safe Retries

Retries become dangerous when repeating a task creates duplicate or inconsistent effects.

Suppose:

```sql
INSERT INTO orders(order_id, amount)
VALUES (1001, 50.00);
```

The task writes the row successfully, but the worker loses communication before Airflow records success.

Airflow may retry.

The second attempt may insert the same logical order again.

The problem is not Airflow's retry mechanism.

The problem is that the operation was not safely repeatable.

## Safer patterns

### 12.1 Unique constraints

```sql
CREATE UNIQUE INDEX orders_order_id_uq
ON orders(order_id);
```

### 12.2 Upsert / merge semantics

```sql
INSERT INTO orders(order_id, amount)
VALUES (%s, %s)
ON CONFLICT (order_id)
DO UPDATE SET amount = EXCLUDED.amount;
```

### 12.3 Partition overwrite

For a deterministic partition:

```text
write partition 2026-10-01
```

rather than repeatedly appending the same logical partition.

### 12.4 Deterministic output paths

```text
s3://bucket/gold/orders/date=2026-10-01/
```

A retry writes the same logical location rather than generating an uncontrolled second output.

### 12.5 Write-audit-publish

A robust pattern is:

```text
write
  ↓
audit/validate
  ↓
publish
```

This reduces the chance that partially written output is mistaken for final output.

This connects directly to Module 2.12's production transformation patterns.

---

# 13. Retry Safety Checklist

Before adding retries, ask:

1. Is the task idempotent?
2. Can partial output exist?
3. Can duplicate rows be created?
4. Can an external API receive duplicate requests?
5. Is the operation transactional?
6. Is there a unique business key?
7. Is the output deterministic?
8. Can the task safely restart?
9. Can the downstream system tolerate repeated requests?
10. What happens if the process succeeds but the worker loses communication before recording success?

That last question is particularly important.

Distributed systems can fail between:

```text
side effect completed
```

and:

```text
orchestrator recorded success
```

Retries must be designed around that reality.

---

# 14. Orchestrator Retries vs In-Task Retries

There are two different retry layers.

## 14.1 Airflow/orchestrator-level retry

```text
Task starts
   ↓
task fails
   ↓
Airflow marks attempt failed
   ↓
retry delay
   ↓
Airflow starts the task again
```

## 14.2 In-task retry

```text
Airflow starts task
   ↓
Python client makes request
   ↓
request fails
   ↓
client waits
   ↓
client retries
   ↓
task eventually succeeds/fails
```

### Comparison

| Dimension | Airflow retry | In-task retry |
|---|---|---|
| Visibility | Clear task attempts | Often inside one task log |
| Granularity | Whole task execution | Individual operation |
| Configuration | DAG/task policy | Application/client code |
| Operational UI | Strong | Depends on logging |
| Backoff | Airflow policy | Library/application policy |
| Best use | Task-level recovery | Fine-grained dependency calls |
| Risk | Re-running whole task | Hidden repeated work |
| Complexity | Centralized | Distributed through code |

Both can be useful.

The danger is uncontrolled nesting.

---

# 15. The Nested Retry Problem

Suppose:

```text
Airflow:
3 retries
```

and:

```text
Python client:
5 internal attempts
```

A rough upper bound can become:

```text
4 Airflow task executions × 5 internal attempts
= 20 dependency attempts
```

That is before considering additional retries inside lower-level libraries.

This can create:

- unexpected dependency load;
- long task duration;
- confusing logs;
- difficult incident diagnosis;
- deadline misses.

### Design rule

Define retry ownership explicitly.

For example:

```text
HTTP client:
small bounded retry for connection-level transient failures

Airflow:
task-level retry for task recovery
```

or:

```text
HTTP client:
no hidden retries

Airflow:
centralized retry policy
```

The best design depends on the dependency and required granularity.

---

# 16. Fail Fast vs Retry

Fail fast when another identical attempt is unlikely to help.

Examples:

- invalid credentials;
- missing required secret;
- invalid configuration;
- schema contract violation;
- malformed required input;
- invalid SQL;
- programming exception.

Conceptually:

```text
Permanent failure
      ↓
do not retry blindly
      ↓
fail
      ↓
alert
      ↓
investigate
```

Failing fast is not "less reliable."

It can be **more operationally reliable** because it makes the real problem visible sooner.

---

# 17. Execution Timeouts

An execution timeout answers:

> **How long may one task execution run?**

Airflow uses `execution_timeout` for this purpose.

Example:

```python
from datetime import timedelta

@task(
    execution_timeout=timedelta(minutes=20),
)
def transform_orders():
    ...
```

Current Airflow documentation states that `execution_timeout` applies to tasks and controls the maximum time allowed for each execution; exceeding it raises `AirflowTaskTimeout`. citeturn0search4

### Timeout is not retry delay

These are different:

```text
retry_delay
    = how long to wait before another attempt
```

```text
execution_timeout
    = how long one execution may run
```

```text
deadline
    = when the business/service outcome must be achieved
```

---

# 18. Timeout Design

Without a timeout:

```text
Task
 ↓
hangs
 ↓
worker occupied
 ↓
pipeline delayed
 ↓
deadline risk
```

With a timeout:

```text
Task
 ↓
runs
 ↓
timeout
 ↓
failure
 ↓
retry / callback / alert
```

Timeout design affects:

- worker utilization;
- failure detection;
- retry timing;
- downstream freshness;
- deadline risk.

## Timeout too short

```text
legitimate slow task
       ↓
timeout
       ↓
unnecessary retry
```

## Timeout too long

```text
real hang
   ↓
worker remains occupied
   ↓
failure detected late
```

The timeout should be based on observed workload behavior and business requirements, not a universal number.

---

# 19. Deadlines and SLA Concepts

A timeout and a deadline answer different questions.

### Task execution timeout

> How long may this individual task execution run?

### Workflow/data deadline

> When must the required outcome be ready?

### SLA concept

> Did the service meet an expected operational target?

Example:

```text
05:00
 ↓
ingestion
 ↓
transformation
 ↓
quality
 ↓
publish
 ↓
07:00 business deadline
```

A task can individually remain within its execution timeout while the overall pipeline still misses the 07:00 requirement.

---

# 20. Airflow 2 SLA vs Airflow 3.x Deadlines

This distinction is mandatory for anyone reading older Airflow material.

## Airflow 2.x legacy material

Older tutorials may show:

```python
@task(
    sla=timedelta(minutes=30)
)
def task():
    ...
```

Treat this as **legacy/reference material**, not as current Airflow 3.x production guidance.

Airflow's Airflow 3 migration documentation states that SLAs were deprecated and removed and replaced with Deadline Alerts. citeturn0search3

## Airflow 3.x direction

Airflow 3.1 introduced Deadline Alerts. Current documentation describes deadlines as time thresholds for DAG runs that trigger a callback when the threshold is exceeded. citeturn1search0turn1search6

A representative current pattern is:

```python
from datetime import timedelta

from airflow.sdk import DAG
from airflow.sdk.definitions.deadline import DeadlineAlert, DeadlineReference
from airflow.providers.smtp.notifications.smtp import SmtpNotifier

with DAG(
    dag_id="deadline_example",
    schedule="@daily",
    deadline=DeadlineAlert(
        reference=DeadlineReference.DAGRUN_QUEUED_AT,
        interval=timedelta(minutes=30),
        callback=SmtpNotifier(
            to="data-platform@example.com",
            subject="DAG deadline missed",
            html_content="The DAG exceeded its configured deadline.",
        ),
    ),
):
    ...
```

The exact reference and callback should be selected according to the Airflow release and provider versions used by your deployment. The official Airflow 3.3 documentation shows `DeadlineAlert`, `DeadlineReference`, and notifier-based callbacks. citeturn1search0

### Important distinction

Do not teach:

```text
SLA = retry mechanism
```

It is not.

A deadline is an **operational expectation**.

Retries are a **failure-recovery mechanism**.

Freshness checks are **data-state validation**.

Quality checks are **correctness validation**.

These controls complement each other.

---

# 21. Deadline-Oriented Data Engineering

Consider:

> Gold revenue data must be ready by 07:00.

The pipeline:

```text
05:00
 ↓
ingestion
 ↓
transformation
 ↓
quality
 ↓
publish
 ↓
07:00
```

Suppose an upstream source is late:

```text
late source
   ↓
ingestion delayed
   ↓
transformation delayed
   ↓
deadline risk
   ↓
operational escalation
```

Retrying a failed task does not automatically guarantee the business deadline.

A production system therefore considers:

```text
retry horizon
+
task timeout
+
pipeline duration
+
upstream readiness
+
deadline
```

---

# 22. Freshness vs Task Success

This is one of the most important production distinctions.

A task can succeed:

```text
task succeeds at 08:00
```

while the business requirement is:

```text
revenue data ready by 07:00
```

Therefore:

> **task success ≠ freshness success**

Similarly:

```text
load task = SUCCESS
```

does not prove:

```text
dataset is current
```

Freshness monitoring can evaluate:

- latest available partition;
- latest event timestamp;
- expected arrival time;
- expected row/window coverage;
- publication time;
- business deadline.

A mature platform monitors both:

```text
orchestration state
```

and:

```text
data state
```

---

# 23. Failure Callbacks

A callback allows additional operational logic to run when a task or DAG reaches a relevant state.

Important callback types for this chapter:

- `on_failure_callback`;
- `on_retry_callback`;
- `on_success_callback`.

Current Airflow documentation also defines `on_execute_callback` and `on_skipped_callback`; they are outside the core focus here. citeturn0search0

Callbacks can be configured at DAG or task scope, including through `default_args`. Airflow supports lists of callbacks as well. citeturn0search0

### What callbacks should do

Good callback responsibilities:

- construct an alert;
- record an operational event;
- emit a metric;
- attach context;
- route a notification;
- point to a runbook.

Poor callback responsibilities:

- perform a large transformation;
- repair the underlying dataset;
- execute a long recovery workflow;
- become a hidden critical dependency.

Keep callbacks **small, observable, and defensive**.

---

# 24. Failure Callbacks in Detail

A simple structured callback:

```python
def notify_failure(context):
    ti = context["task_instance"]
    exception = context.get("exception")

    message = {
        "dag_id": ti.dag_id,
        "task_id": ti.task_id,
        "run_id": ti.run_id,
        "try_number": ti.try_number,
        "error": str(exception) if exception else "unknown",
    }

    print(message)
```

The callback receives runtime context.

Current Airflow documentation describes callback context as a mapping containing runtime information about the task instance. citeturn0search0

### Context fields commonly useful for operations

Depending on the callback and run type:

- DAG ID;
- task ID;
- run ID;
- data interval;
- logical date where applicable;
- try number;
- exception;
- task instance;
- relevant log information.

Do not dump every available field into an alert.

Select information that helps an operator diagnose the incident.

---

# 25. Callback Context and Airflow 3.x

A robust callback should assume that runtime context depends on the type of event.

For example, Airflow documents that DAG callback context can select a task instance associated with the relevant DAG state, and that relying on one task instance as a complete representation of the whole DAG state is not recommended. citeturn0search0

Therefore:

```text
DAG failed
```

does not necessarily mean:

```text
the callback's selected task instance explains every reason for the DAG failure
```

For actionable operational design:

- use task callbacks for task-specific failure;
- use DAG callbacks for DAG-level outcomes;
- query or link to the broader run state when necessary;
- do not assume one callback context contains the complete incident narrative.

---

# 26. Retry Callbacks

`on_retry_callback` is useful when a task is going to retry.

Good uses:

- metrics;
- structured retry logging;
- operational state;
- recording retry reasons;
- low-noise diagnostic events.

Poor use:

```text
every retry → page an engineer
```

For most systems:

```text
retry event
    ↓
metric/log
```

and:

```text
final actionable failure
    ↓
alert/page
```

is less noisy.

Current Airflow documentation defines `on_retry_callback` as the callback invoked when a task is up for retry. citeturn0search0

---

# 27. Success Callbacks

`on_success_callback` can be useful for:

- audit logging;
- operational metrics;
- lightweight notifications;
- recording successful publication;
- emitting an internal event.

Example:

```python
def record_success(context):
    ti = context["task_instance"]

    print(
        {
            "event": "task_success",
            "dag_id": ti.dag_id,
            "task_id": ti.task_id,
            "run_id": ti.run_id,
        }
    )
```

Do not turn a success callback into:

```text
task succeeds
   ↓
callback performs 30-minute data transformation
```

That hides important work outside the DAG's visible task structure.

---

# 28. Structured Failure Notification

A production alert should answer:

> What failed, when did it fail, what data was affected, why did it fail, who owns it, where can I investigate, and what should I do next?

Useful fields:

```text
DAG:
Task:
Run:
Data interval:
Try:
Failure:
Owner:
Severity:
Log:
Runbook:
Next action:
```

Bad:

```text
Task failed.
```

Better:

```text
DAG: orders_daily
Task: extract_api
Run: scheduled__2026-10-01
Data interval: 2026-10-01
Try: 4
Failure: API timeout after bounded retries
Owner: Data Ingestion
Severity: High
Log: <task log>
Runbook: API-INGESTION-001
Next action: Check provider health and request-rate status.
```

The second alert reduces operator search time.

---

# 29. Actionable Alerts

A useful alert contains:

- pipeline;
- task;
- data interval;
- failure category;
- attempt;
- error summary;
- severity;
- owner;
- log location;
- runbook;
- recommended next action.

Avoid:

- vague alerts;
- duplicate alerts;
- alerts without ownership;
- alerts without context;
- alerts that require the operator to reconstruct the incident manually.

### Alert design principle

```text
failure
 ↓
context
 ↓
classification
 ↓
severity
 ↓
owner
 ↓
next action
```

---

# 30. Alert Severity and Routing

Severity is an organizational policy, not a universal Airflow standard.

One possible conceptual model:

### Critical

Business-critical data unavailable or an important deadline is at immediate risk.

### High

Important production pipeline failed and requires intervention.

### Medium

Recoverable issue or non-critical source problem.

### Low

Informational retry or diagnostic event.

Teams should define their own:

- severity definitions;
- routing rules;
- paging policy;
- business impact criteria;
- escalation path.

Do not assume "High" always means page someone.

---

# 31. Alert Fatigue

Too many alerts reduce the value of alerts.

Bad:

```text
Retry 1 → alert
Retry 2 → alert
Retry 3 → alert
Final failure → alert
```

A lower-noise model:

```text
Retry events
    ↓
metrics + logs

Final actionable failure
    ↓
alert
```

There are exceptions.

For example, a critical system may alert when:

```text
deadline risk detected
```

even before final failure.

The key is that every alert should have a clear operator action.

---

# 32. Non-Retryable Errors

Common non-retryable categories:

- authentication error;
- schema contract violation;
- invalid configuration;
- malformed required input;
- invalid SQL;
- programming defect;
- missing secret.

Example:

```text
HTTP 401
 ↓
same credentials
 ↓
retry
 ↓
HTTP 401
```

No amount of retrying changes the credentials.

The production response is:

```text
fail fast
 ↓
structured callback
 ↓
owner notification
 ↓
runbook
 ↓
credential/configuration repair
 ↓
safe rerun
```

Where available, Airflow's retry-policy mechanisms can be used to make exception-aware decisions. Current Airflow 3.3 task documentation describes reusable retry policies and notes that `AirflowFailException` takes precedence over the policy. citeturn1search9

---

# 33. Mapped Task Partial Failures

Dynamic task mapping creates multiple task instances from one mapped task definition.

Conceptually:

```python
extract.expand(
    source=[
        "postgres",
        "sftp",
        "api",
        "warehouse",
    ]
)
```

Possible result:

```text
postgres  → success
sftp      → success
api       → failed
warehouse → success
```

This is a **partial mapped-task failure**.

It is not equivalent to:

```text
everything failed
```

### Operational questions

You must determine:

- which mapped instance failed;
- whether that instance is retryable;
- how many retries remain;
- whether downstream tasks require all mapped instances;
- whether partial results can be published safely;
- how the alert identifies the failed source.

---

# 34. Mapped Failure Alerting

A useful notification:

```text
DAG: ingestion
Task: extract
Run: scheduled__2026-10-01

Mapped instances:
  postgres  → success
  sftp      → success
  api       → failed
  warehouse → success

Failed source:
api

Failure:
timeout

Next action:
inspect API availability and rate-limit status.

Runbook:
API-INGESTION-001
```

This is much more actionable than:

```text
extract failed
```

### Downstream behavior

The downstream design determines whether one failed mapped instance blocks publication.

For example:

```text
4 sources
  ↓
3 succeed
1 fails
  ↓
quality/publish policy
```

Possible business policies include:

- all sources required → block publication;
- source optional → continue with explicit degraded-state handling;
- failed source quarantined → publish only if business rules permit.

Do not hide partial failure merely to make the DAG green.

---

# 35. Runbooks

A mature failure-management chain is:

```text
Failure
   ↓
Alert
   ↓
Runbook
   ↓
Recovery
```

A runbook should contain:

- symptom;
- likely causes;
- diagnostic commands;
- relevant logs;
- dashboards;
- safe rerun procedure;
- escalation;
- owner;
- rollback/recovery;
- prevention.

## Example: API ingestion repeatedly fails

### Symptom

`extract_api` exhausts its configured retries.

### First checks

1. Open the task log.
2. Identify HTTP status or network exception.
3. Check provider health.
4. Check rate-limit state.
5. Check credential validity.
6. Check whether the source endpoint changed.
7. Inspect the most recent successful run.

### If rate limited

- respect provider limits;
- avoid immediate manual rerun loops;
- check whether backoff policy is appropriate;
- determine whether a deadline is at risk.

### If authentication failed

- do not blindly retry;
- verify the configured credential;
- follow the credential-rotation procedure;
- rerun only after repair.

### If the payload schema changed

- stop blind retries;
- inspect the contract;
- quarantine affected input if required;
- update transformation/contract handling;
- test before rerun.

### Recovery

Use a safe rerun procedure that preserves idempotency.

### Prevention

- monitor failure categories;
- monitor freshness;
- track repeated failures;
- maintain provider contract tests.

---

# 36. Failure Management Decision Tree

```text
Task failed
    |
    v
Is the failure transient?
    |
   / \
 Yes  No
  |    |
  |   Fail fast
  |      |
  |    Alert
  |
Is retry safe?
  |
 / \
Yes No
 |   |
Retry Redesign
 |
Did retry succeed?
 |
/ \
Yes No
 |   |
Continue
     |
  Final failure
     |
   Callback
     |
    Alert
     |
  Runbook
```

Every branch has a reason.

The most important branch is not:

```text
retry?
```

It is:

```text
is retry both useful and safe?
```

---

# 37. Production Failure Scenarios

## Scenario 1 — Temporary PostgreSQL outage

**Classification:** transient.

**Retry:** yes, bounded.

**Timeout:** yes, based on expected query/connection behavior.

**Callback:** retry metrics; final failure notification.

**Severity:** depends on business impact.

**Runbook:** inspect database health, connection availability, locks, and recent deployment changes.

---

## Scenario 2 — API rate limiting

**Classification:** usually transient.

**Retry:** yes, with backoff and provider guidance.

**Timeout:** yes.

**Callback:** retry telemetry; alert if retries are exhausted or deadline risk becomes material.

**Severity:** depends on affected business data.

**Runbook:** inspect rate limits, request volume, provider status, and credential/client configuration.

---

## Scenario 3 — Invalid API credentials

**Classification:** permanent until configuration changes.

**Retry:** no blind retry.

**Timeout:** not the primary control.

**Callback:** failure callback.

**Severity:** based on business impact.

**Runbook:** credential verification/rotation and safe rerun.

---

## Scenario 4 — Malformed source file

**Classification:** usually permanent for that input.

**Retry:** no blind retry.

**Callback:** failure alert.

**Severity:** based on business impact.

**Runbook:** inspect input, quarantine if appropriate, contact producer, correct/reprocess.

---

## Scenario 5 — Schema contract violation

**Classification:** usually permanent.

**Retry:** no blind retry.

**Callback:** alert owner.

**Severity:** potentially high if publication is blocked.

**Runbook:** compare contract versions and recent producer changes.

---

## Scenario 6 — Database lock timeout

**Classification:** often transient.

**Retry:** bounded.

**Backoff:** useful.

**Timeout:** important.

**Runbook:** inspect lock holders and transaction duration if repeated.

---

## Scenario 7 — Task hangs

**Classification:** unknown until diagnosed.

**Timeout:** essential.

**Retry:** only if restarting is safe.

**Callback:** final failure alert.

**Runbook:** inspect worker logs, external calls, CPU/memory, and dependency state.

---

## Scenario 8 — Object-storage outage

**Classification:** often transient.

**Retry:** bounded with backoff.

**Alert:** after meaningful failure or deadline risk.

**Runbook:** provider health, credentials, bucket policy, network path.

---

## Scenario 9 — Partial mapped-task failure

**Classification:** per mapped instance.

**Retry:** failed instance if safe.

**Alert:** identify the specific source.

**Downstream:** follow explicit business completeness policy.

---

## Scenario 10 — All retries exhausted

**Classification:** unresolved.

**Callback:** final failure callback.

**Alert:** actionable.

**Runbook:** classify root cause before rerun.

---

## Scenario 11 — Task succeeds but dataset is stale

**Task state:** success.

**Data state:** freshness failure.

**Response:** freshness/deadline alert.

**Lesson:** orchestration state does not replace data observability.

---

## Scenario 12 — Failure shortly before 07:00 deadline

The system should consider:

```text
current time
+
remaining retries
+
retry delays
+
task timeout
+
downstream duration
```

If the expected recovery horizon threatens the deadline, escalate operationally rather than simply waiting for every retry opportunity.

---

# 38. End-to-End `orders_daily` Failure Management Lab

Build:

```text
Orders ingestion
       ↓
Transformation
       ↓
Quality gate
       ↓
Gold publication
```

Introduce:

- PostgreSQL transient outage;
- API timeout;
- invalid credential;
- quality failure;
- slow transformation;
- mapped source failure.

Configure:

- bounded retries;
- retry delay;
- exponential backoff;
- maximum retry delay;
- execution timeout;
- failure callback;
- retry callback;
- success callback where useful;
- structured alerts;
- freshness/deadline monitoring.

### Suggested skeleton

```python
from datetime import timedelta

from airflow.sdk import dag, task


def failure_callback(context):
    ti = context["task_instance"]
    exception = context.get("exception")

    print(
        {
            "event": "task_failure",
            "dag_id": ti.dag_id,
            "task_id": ti.task_id,
            "run_id": ti.run_id,
            "try_number": ti.try_number,
            "exception": str(exception) if exception else None,
        }
    )


def retry_callback(context):
    ti = context["task_instance"]

    print(
        {
            "event": "task_retry",
            "dag_id": ti.dag_id,
            "task_id": ti.task_id,
            "run_id": ti.run_id,
            "try_number": ti.try_number,
        }
    )


@dag(
    dag_id="orders_daily_failure_management",
    schedule="@daily",
    catchup=False,
)
def orders_daily_failure_management():

    @task(
        retries=3,
        retry_delay=timedelta(minutes=2),
        retry_exponential_backoff=2.0,
        max_retry_delay=timedelta(minutes=20),
        execution_timeout=timedelta(minutes=30),
        on_failure_callback=failure_callback,
        on_retry_callback=retry_callback,
    )
    def ingest():
        ...

    @task(
        execution_timeout=timedelta(minutes=45),
        on_failure_callback=failure_callback,
    )
    def transform():
        ...

    @task(
        retries=0,
        on_failure_callback=failure_callback,
    )
    def quality_gate():
        ...

    @task(
        retries=2,
        retry_delay=timedelta(minutes=3),
        retry_exponential_backoff=2.0,
        max_retry_delay=timedelta(minutes=15),
        execution_timeout=timedelta(minutes=20),
        on_failure_callback=failure_callback,
    )
    def publish():
        ...

    ingest_result = ingest()
    transformed = transform()
    quality = quality_gate()
    published = publish()

    ingest_result >> transformed >> quality >> published


orders_daily_failure_management()
```

This is a teaching skeleton, not a complete production ingestion implementation.

The important learning point is that each task has a deliberately chosen failure policy rather than one universal policy.

---

# 39. Failure Injection Lab

The learner should intentionally inject failures.

## Failure 1 — Temporary network failure

Simulate a failure for the first attempt and success afterward.

Expected:

```text
attempt 1 → fail
wait
attempt 2 → success
```

Observe:

- task attempts;
- retry delay;
- callback behavior;
- logs.

---

## Failure 2 — Permanent authentication error

Raise a representative authentication exception.

Expected:

```text
authentication failure
 ↓
fail fast
 ↓
alert
```

Do not create unnecessary retries.

---

## Failure 3 — Execution timeout

Create a task that sleeps longer than its `execution_timeout`.

Expected:

```text
task runs
 ↓
timeout
 ↓
failure
 ↓
retry if configured
```

Airflow documents `AirflowTaskTimeout` for exceeded task execution timeouts. citeturn0search4

---

## Failure 4 — Mapped partial failure

Map four sources and deliberately fail one.

Expected:

```text
source A → success
source B → success
source C → failure
source D → success
```

Investigate:

- map index;
- failed source;
- retry behavior;
- downstream state;
- alert clarity.

---

## Failure 5 — Final retry fails

Make every attempt fail.

Expected:

```text
attempt 1 → fail
attempt 2 → fail
attempt 3 → fail
final failure
   ↓
failure callback
   ↓
actionable alert
   ↓
runbook
```

---

## Failure 6 — Freshness deadline missed

Allow the DAG to complete but make the dataset arrive after the business target.

Expected:

```text
DAG task = success
data freshness = failure
deadline = missed
```

The system should not silently treat this as complete business success.

---

# 40. Testing Failure Behavior

Test:

- retry configuration;
- retry policy;
- callback invocation;
- callback context;
- timeout behavior;
- permanent failure handling;
- mapped task failures;
- alert formatting;
- deadline logic.

### Unit-test callback logic

A callback can be tested with a synthetic context.

```python
def test_failure_callback(capsys):
    context = {
        "task_instance": FakeTaskInstance(
            dag_id="orders_daily",
            task_id="extract_api",
            run_id="test_run",
            try_number=4,
        ),
        "exception": TimeoutError("API timed out"),
    }

    failure_callback(context)

    captured = capsys.readouterr()

    assert "extract_api" in captured.out
    assert "API timed out" in captured.out
```

The exact fake object depends on your testing framework.

The important principle is:

> Test the callback's behavior without requiring a real Slack, email, or PagerDuty-style service.

---

# 41. Callback Testing

A callback test should verify useful context:

- DAG ID;
- task ID;
- run ID;
- try number;
- exception;
- data interval where applicable;
- relevant metadata/links where available.

### Mock notification clients

Prefer:

```text
callback
   ↓
mock notifier
```

over:

```text
callback
   ↓
real production paging system
```

during unit tests.

This makes tests:

- deterministic;
- fast;
- safe;
- repeatable.

Integration tests can verify the notifier integration separately.

---

# 42. Observability

Track operational signals such as:

- retry count;
- retry rate;
- retries per task;
- task duration;
- timeout count;
- final failure count;
- failure category;
- callback execution;
- callback failure;
- alert count;
- alert severity;
- deadline misses;
- freshness misses;
- mapped-task failure distribution;
- repeated failures by task/source.

### Why retry rate matters

Suppose final failure rate remains low but:

```text
retry rate ↑
```

for several days.

That can indicate:

- a dependency becoming unstable;
- capacity pressure;
- an API approaching rate limits;
- a deteriorating network path;
- an application nearing timeout thresholds.

Retries can therefore act as an **early warning signal**.

---

# 43. Retry Storms

A retry storm can look like:

```text
100 tasks fail
      ↓
each retries immediately
      ↓
external service receives another 100 requests
      ↓
service remains overloaded
      ↓
more failures
      ↓
more retries
```

Mitigations include:

- exponential backoff;
- jitter where appropriate;
- bounded retries;
- concurrency controls;
- pools/rate limits;
- fail-fast permanent errors;
- circuit-breaker-like operational strategies where appropriate.

Do not solve every retry-storm problem with retries alone.

Sometimes the correct response is to reduce load.

---

# 44. Callback Failure

A callback is itself executable code.

Therefore:

```text
task fails
   ↓
callback runs
   ↓
callback fails
```

The original task failure still exists.

Do not assume callback failure repairs the task.

Current Airflow documentation notes that callback errors appear in DAG processor logs rather than task logs, which makes defensive callback design important. citeturn0search0

### Defensive callback design

- keep callbacks lightweight;
- validate required context;
- catch expected notification errors;
- log callback failures clearly;
- avoid secrets in messages;
- avoid making callbacks large workflows;
- monitor callback failures.

The callback should help operations, not become another hidden outage source.

---

# 45. Retry + Timeout + Deadline Relationship

Consider:

```text
05:00
  |
  | attempt 1
  |------ timeout
  |
  | retry delay
  |
  | attempt 2
  |------ failure
  |
  | backoff
  |
  | attempt 3
  |
07:00 business deadline
```

These controls answer different questions:

```text
execution_timeout
    ↓
How long may this attempt run?
```

```text
retry policy
    ↓
How should the task recover from failure?
```

```text
deadline
    ↓
When must the business/service outcome be ready?
```

A production design must evaluate all three together.

---

# 46. Production Design Patterns

## Pattern 1 — Transient API failure

```text
API
 ↓
timeout
 ↓
bounded retry
 ↓
backoff
 ↓
success
```

Use when the failure is plausibly temporary.

---

## Pattern 2 — Permanent configuration error

```text
invalid credentials
 ↓
fail fast
 ↓
failure callback
 ↓
alert owner
 ↓
repair configuration
 ↓
safe rerun
```

---

## Pattern 3 — Quality failure

```text
quality violation
 ↓
no blind retry
 ↓
quarantine/investigation
 ↓
producer or transformation repair
```

---

## Pattern 4 — Deadline-aware pipeline

```text
task retries
 ↓
deadline approaching
 ↓
operational escalation
```

Do not wait blindly for retries if the remaining retry horizon is incompatible with the business deadline.

---

## Pattern 5 — Mapped ingestion

```text
source A → success
source B → success
source C → retry/fail
source D → success
```

Alert specifically about source C.

---

# 47. Trade-offs

## More retries

**Pros**

- better resilience to transient failures.

**Cons**

- slower recovery;
- more dependency load;
- delayed incident visibility.

## Longer retry delays

**Pros**

- gives dependencies more recovery time.

**Cons**

- increases completion latency.

## Exponential backoff

**Pros**

- reduces retry pressure.

**Cons**

- can increase recovery time.

## Aggressive timeouts

**Pros**

- detects hangs quickly.

**Cons**

- can terminate legitimate slow work.

## Loose timeouts

**Pros**

- allows long-running operations.

**Cons**

- slow failure detection.

## More alerts

**Pros**

- more visibility.

**Cons**

- more alert fatigue.

The correct choice depends on:

- dependency behavior;
- business deadlines;
- task duration;
- idempotency;
- cost;
- operational capacity.

---

# 48. Architecture Exercises

## 1. Flaky REST API

Design:

- retry classification;
- backoff;
- maximum attempts;
- timeout;
- rate-limit behavior;
- alert policy.

### Expected reasoning

Retry transient network/rate-limit failures, but avoid retrying permanent request/authentication failures. Bound both client and Airflow retries.

---

## 2. PostgreSQL ingestion

Design failure handling for:

- connection failure;
- lock timeout;
- malformed SQL;
- duplicate key.

### Expected reasoning

Treat dependency failures differently from correctness failures. Protect writes with transactions and idempotent keys.

---

## 3. 07:00 freshness guarantee

Design:

```text
ingestion → transform → quality → publish
```

for a 07:00 target.

### Expected reasoning

Model task durations, retry horizon, upstream readiness, and deadline monitoring together.

---

## 4. Idempotent transformation

Design retry behavior for a partitioned transformation.

### Expected reasoning

Make output deterministic and safely replaceable before enabling aggressive recovery.

---

## 5. Non-idempotent external API

Design failure handling when a POST may create an external resource.

### Expected reasoning

Blind retries can duplicate external side effects. Use provider-supported idempotency keys or another durable deduplication strategy when available.

---

## 6. Mapped task failure

Design alerts for:

```text
20 mapped sources
19 success
1 failed
```

### Expected reasoning

Identify the failed source/map index and make downstream completeness policy explicit.

---

## 7. Retry storm prevention

100 tasks fail against one external API.

### Expected reasoning

Bound concurrency, use backoff, consider jitter, respect rate limits, and avoid immediate synchronized retries.

---

## 8. Callback architecture

Design:

```text
task failure
 ↓
callback
 ↓
notification
 ↓
runbook
```

### Expected reasoning

Keep callback logic lightweight and notification-specific. Do not perform recovery work directly inside the callback.

---

## 9. Failure runbook

Create a runbook for repeated API failure.

### Expected reasoning

Include symptoms, evidence, diagnostics, owner, safe rerun, escalation, and prevention.

---

## 10. Complete production failure-management strategy

Combine:

- classification;
- idempotency;
- retries;
- backoff;
- timeout;
- deadline;
- callback;
- alert;
- runbook;
- recovery.

### Expected reasoning

Every control should have a distinct responsibility. Avoid solving the same problem with multiple uncontrolled retry layers.

---

# 49. Code Review Exercises

## Bad example 1 — Zero-delay retries

```python
@task(
    retries=3,
    retry_delay=timedelta(seconds=0),
)
def call_api():
    ...
```

### Problem

A failing dependency may receive immediate repeated requests.

### Better

Use a bounded delay and, when appropriate, exponential backoff.

---

## Bad example 2 — Infinite retries

```python
while True:
    try:
        call_service()
        break
    except Exception:
        continue
```

### Problem

The task can hang indefinitely and hide an outage.

### Better

Bound attempts and time.

---

## Bad example 3 — Retrying invalid credentials

```text
401
 ↓
retry
 ↓
401
 ↓
retry
```

### Problem

The underlying credential does not change.

### Better

Fail fast and route to the credential owner.

---

## Bad example 4 — Non-idempotent write

```text
POST create-order
 ↓
network timeout
 ↓
retry POST
```

### Problem

The first request may have succeeded even though the client timed out.

### Better

Use an idempotency key or another deduplication mechanism supported by the external system.

---

## Bad example 5 — Nested retry explosion

```text
Airflow retries = 5
HTTP client retries = 10
```

### Problem

Potentially many dependency calls per logical task attempt.

### Better

Define clear retry ownership and bound total work.

---

## Bad example 6 — Vague failure callback

```python
def failure_callback(context):
    send_alert("Task failed")
```

### Problem

No task, run, failure, owner, or next action.

### Better

Send structured context.

---

## Bad example 7 — Alert every retry

```text
retry 1 → page
retry 2 → page
retry 3 → page
final failure → page
```

### Problem

Alert fatigue.

### Better

Use metrics/logs for routine retries and alert on meaningful failure or deadline risk.

---

## Bad example 8 — No execution timeout

```python
@task(retries=3)
def unknown_duration_operation():
    ...
```

### Problem

A hung execution can consume capacity indefinitely.

### Better

Set a workload-appropriate execution timeout.

---

## Bad example 9 — Task success equals freshness

```text
load task = SUCCESS
therefore dashboard data = current
```

### Problem

The task may have loaded stale or incomplete data.

### Better

Monitor freshness and completeness independently.

---

# 50. Interview Questions

## 10 Basic

### 1. What is a retry in Airflow?

**Answer:** A retry is an additional execution attempt after a task fails, according to its configured retry policy. If `retries=3`, the task has one initial attempt plus up to three additional attempts.

### 2. What is the difference between `retries=0` and `retries=3`?

**Answer:** `retries=0` permits only the initial execution. `retries=3` permits up to four total executions.

### 3. What does `retry_delay` control?

**Answer:** It controls the base waiting period before a retry attempt. It does not control how long the task itself is allowed to run.

### 4. What is exponential backoff?

**Answer:** Exponential backoff increases the delay between retry attempts, reducing pressure on a dependency during an outage or rate-limit condition.

### 5. What is a transient failure?

**Answer:** A failure caused by a temporary condition that may disappear, such as a temporary network outage or service unavailability.

### 6. What is a permanent failure?

**Answer:** A failure that is unlikely to succeed without changing the underlying condition, such as invalid credentials, malformed input, or a code defect.

### 7. Why is idempotency important for retries?

**Answer:** Because a retry repeats work. If the work creates duplicate or inconsistent side effects, the retry can corrupt results.

### 8. What is an execution timeout?

**Answer:** A maximum runtime for an individual task execution. In Airflow, `execution_timeout` limits the time allowed for the execution.

### 9. What is a failure callback?

**Answer:** A callback invoked when a task or DAG reaches a failure state, allowing operational logic such as structured logging or notification.

### 10. Why should alerts be actionable?

**Answer:** Operators need enough context to identify the failure, assess impact, locate evidence, and take the next recovery action without reconstructing the incident from scratch.

---

## 10 Moderate

### 11. Why should permanent failures generally not be retried?

**Answer:** Repeating the same input and configuration does not repair the cause. Retries consume capacity, delay diagnosis, and can generate alert noise.

### 12. How can retry storms happen?

**Answer:** Many tasks can fail simultaneously and retry at the same time, creating another large burst of requests against an already unhealthy dependency.

### 13. How does exponential backoff help?

**Answer:** It increases the time between attempts, reducing repeated pressure and giving the dependency more opportunity to recover.

### 14. What is `max_retry_delay` for?

**Answer:** It caps the delay produced by the backoff calculation so retry intervals do not grow beyond an operationally acceptable ceiling.

### 15. What is the difference between Airflow retries and client retries?

**Answer:** Airflow retries repeat the task execution. Client retries repeat a particular operation inside a task. Client retries can provide finer granularity but can become hidden or excessive if not bounded.

### 16. What is a nested retry problem?

**Answer:** It occurs when both the orchestrator and application/library retry independently, potentially multiplying the number of actual dependency attempts and increasing latency and load.

### 17. Why can a task timeout even when retries are configured?

**Answer:** `execution_timeout` limits one execution. If it expires, that attempt fails; the retry policy may then determine whether another attempt is scheduled.

### 18. What is the difference between a timeout and a deadline?

**Answer:** A timeout limits one execution's runtime. A deadline defines when a larger workflow or business outcome is expected to be complete.

### 19. Why is a task success state not enough to guarantee freshness?

**Answer:** A task can successfully process stale, incomplete, or late input. Freshness is a property of the resulting data, not merely the task's execution state.

### 20. What belongs in a failure alert?

**Answer:** At minimum: pipeline, task, run, interval, failure category, attempt, error summary, severity, owner, log location, runbook, and next action.

---

## 10 Hard

### 21. A task has `retries=3`, and each attempt takes 10 minutes before failing. The retry delay is 5 minutes. What is the minimum elapsed time before final failure, ignoring scheduler/queue overhead?

**Answer:** Four executions can each consume 10 minutes, with three 5-minute waits between them:

```text
10 + 5 + 10 + 5 + 10 + 5 + 10
= 55 minutes
```

This demonstrates why retry policy affects deadline planning.

### 22. Why can retrying a database write be unsafe even when the database is healthy?

**Answer:** The first write may have committed while the client lost communication before observing the success. A retry can then create a duplicate unless the operation is idempotent or protected by a uniqueness/deduplication mechanism.

### 23. How would you design retries for HTTP 429 versus HTTP 401?

**Answer:** HTTP 429 commonly indicates rate limiting and may be retryable with backoff and provider guidance. HTTP 401 commonly indicates an authentication problem and should not be blindly retried with unchanged credentials.

### 24. Why can a long execution timeout be harmful?

**Answer:** It delays detection of hangs and can keep worker capacity occupied, increasing queueing and downstream deadline risk.

### 25. Why can a short execution timeout be harmful?

**Answer:** It can terminate legitimate slow operations, causing unnecessary retries, additional load, and potentially duplicate side effects.

### 26. How should mapped task failures affect alerting?

**Answer:** Alerts should identify the failed mapped instance or source rather than merely saying the parent mapped task failed. Operators need to know which partitions/sources require attention.

### 27. Why should callbacks remain lightweight?

**Answer:** They run as operational reactions to task/DAG state. Turning them into large processing jobs hides work, complicates observability, and creates another dependency that can fail.

### 28. What is alert fatigue?

**Answer:** It is the loss of alert value caused by excessive, repetitive, or low-actionability notifications. Operators may begin ignoring alerts.

### 29. How should you test a failure callback?

**Answer:** Supply a controlled context, invoke the callback, assert the structured output or mocked notifier call, and test important context fields. Do not require a real production notification system for unit tests.

### 30. How does a deadline complement retries?

**Answer:** Retries attempt recovery; the deadline measures whether the overall outcome remains on time. A pipeline can continue retrying while simultaneously becoming operationally late, so deadline monitoring provides a separate signal.

---

## 10 Advanced

### 31. Design a retry policy for a 20-source mapped ingestion pipeline where one source is rate-limited and another has invalid credentials.

**Answer:** Classify each source independently. The rate-limited source receives bounded backoff and possibly provider-guided delays. The invalid-credential source should fail fast. Alerts should identify individual sources. Downstream publication must follow an explicit completeness policy rather than treating every mapped instance identically.

### 32. How would you prevent nested retry explosions?

**Answer:** Define ownership at each layer. Decide which failures are handled by the client and which by Airflow. Bound both layers, avoid overlapping broad exception handling, and estimate the maximum dependency attempts per logical task execution.

### 33. A DAG must publish by 07:00. Each task has retries configured. How do you determine whether the retry policy is compatible with the deadline?

**Answer:** Estimate the worst-case duration of each attempt, execution timeouts, retry delays, backoff growth, concurrency/queue delays, and downstream processing time. Compare the resulting recovery horizon with the remaining time before 07:00. If the policy can exceed the business window, use deadline-aware escalation rather than assuming retries guarantee success.

### 34. What is the relationship between task failure and data freshness?

**Answer:** They are separate dimensions. A failed task may obviously threaten freshness, but a successful task can also produce stale data. Production observability therefore monitors both execution state and data-state freshness.

### 35. Why should an authentication failure usually fail fast?

**Answer:** The same authentication request with unchanged credentials is unlikely to succeed. Repeating it wastes capacity and can delay the operator's response. The correct workflow is usually repair configuration/credentials, then rerun safely.

### 36. How would you design callback failure handling?

**Answer:** Keep callback code defensive, log callback failures clearly, isolate notification failures from the original task failure, and avoid making the callback a critical data-processing dependency. Monitor callback failures separately.

### 37. Explain the Airflow 2 SLA to Airflow 3.x transition.

**Answer:** Older Airflow 2.x material may use task-level SLA configuration. Airflow 3 removed the legacy SLA mechanism and introduced Deadline Alerts as the deadline-oriented mechanism. Current designs should use Airflow 3.x deadline capabilities plus freshness and quality monitoring rather than presenting `sla=` as current production syntax. citeturn0search3turn1search0

### 38. How would you design an actionable alert for a mapped task with 99 successes and one failure?

**Answer:** Identify the DAG, task, run, failed map index/source, error category, attempt, owner, severity, log location, runbook, and next action. Do not force the operator to inspect all 100 instances manually.

### 39. When might retrying a quality failure be harmful?

**Answer:** If the input or transformation logic is deterministically wrong, retrying simply repeats the same violation. It wastes resources and delays investigation. Quality failures should generally be classified and handled explicitly rather than blindly retried.

### 40. Design the complete failure-management lifecycle for a production revenue pipeline.

**Answer:** Start with failure classification and idempotent task design. Apply bounded retries only to plausible transient failures, use backoff and maximum delay, enforce execution timeouts, monitor business deadlines and freshness, use lightweight callbacks for operational events, generate structured alerts, route them by severity and ownership, maintain runbooks, test failure paths, inject failures in non-production environments, and measure retry/failure/freshness/deadline signals. The system should make recovery safe rather than merely making failures less visible.

---

# 51. Practical Exercises

## Beginner

1. Configure three retries.
2. Configure a five-minute retry delay.
3. Classify ten example failures.
4. Add an execution timeout.
5. Write a basic failure callback.
6. Log the task ID and run ID from callback context.

## Intermediate

1. Implement exponential backoff.
2. Add a maximum retry delay.
3. Distinguish retryable and non-retryable failures.
4. Build a structured failure notification.
5. Mock a notification client.
6. Simulate an execution timeout.
7. Test a retry callback.
8. Create a freshness check separate from task success.

## Advanced

1. Design nested retry boundaries.
2. Handle mapped-task partial failure.
3. Build deadline monitoring.
4. Create an operational runbook.
5. Inject transient and permanent failures.
6. Measure retry rate.
7. Create severity-based alert routing.
8. Design an idempotent external API operation.

## Production

Design a pipeline containing:

- transient API failures;
- permanent configuration failures;
- idempotent writes;
- bounded retries;
- exponential backoff;
- execution timeouts;
- deadline monitoring;
- structured alerts;
- callback testing;
- mapped tasks;
- operational runbook.

---

# 52. Final Practical Challenge

A daily revenue pipeline must be complete by **07:00**.

Architecture:

```text
5 ingestion sources
        ↓
     bronze
        ↓
     silver
        ↓
quality validation
        ↓
   gold revenue
```

Potential failures:

- transient database errors;
- API rate limits;
- invalid credentials;
- malformed files;
- schema violations;
- slow transformations;
- partial source failures.

Requirements:

- retry transient failures;
- fail fast on permanent failures;
- prevent retry storms;
- enforce execution timeouts;
- monitor the 07:00 deadline;
- generate actionable alerts;
- handle mapped-task partial failures;
- preserve idempotency;
- provide runbooks;
- test failure behavior.

## Your design task

Produce:

1. retry policy;
2. failure classification;
3. timeout policy;
4. deadline policy;
5. callback strategy;
6. alert strategy;
7. mapped-task behavior;
8. testing strategy;
9. runbook.

## Expected architecture

```text
                         ┌─────────────────────┐
                         │ Failure classification│
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
               transient                       permanent
                    │                               │
            safe to retry?                    fail fast
                    │                               │
              bounded retry                    callback
                    │                               │
              backoff/timeout                    alert
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                             business deadline
                                    │
                             freshness check
                                    │
                               publication
```

## Expected reasoning

- Not every source receives the same retry policy.
- Authentication and contract failures should normally fail fast.
- Transient API/database failures may use bounded retries.
- All retried writes must be safe to repeat.
- Timeouts prevent individual executions from consuming capacity indefinitely.
- Deadline monitoring answers whether the business outcome is still on time.
- Freshness checks verify the state of the data.
- Callbacks should produce operational context, not perform large recovery jobs.
- Mapped alerts should identify failed sources.
- Runbooks turn alerts into repeatable recovery procedures.

---

# 53. Relationship to Other Module 2.13 Topics

## Topic 05 — Connections, Variables, Hooks, and XComs

Connection configuration can directly affect failure classification.

Example:

```text
invalid connection credential
        ↓
authentication failure
        ↓
fail fast
```

Do not re-teach Connections or Hooks here.

---

## Topic 06 — Sensors and Deferrable Operators

Sensor timeout and task execution timeout are different controls.

For example, a sensor may have:

```text
sensor waiting timeout
```

while each execution can also have:

```text
execution_timeout
```

Airflow documents that sensor `timeout` has semantics specific to reschedule-mode sensors, while `execution_timeout` limits an individual execution. citeturn0search4

Do not re-teach sensors here.

---

## Topic 08 — Backfills, Catch-up, and Partitioned Runs

Retries can interact with historical processing.

Example:

```text
historical partition
 ↓
task fails
 ↓
retry
 ↓
safe deterministic rerun
```

The same idempotency principles apply.

Do not re-teach backfills here.

---

# 54. Relationship to Module 2.12

Topic 07 depends heavily on the production principles from:

**Transformation Patterns and Pipeline Design**

Especially:

- idempotency;
- deterministic processing;
- partitioned execution;
- safe reruns;
- write-audit-publish.

The relationship is:

```text
correct transformation design
          ↓
safe task retry
          ↓
safe recovery
```

If the transformation is not idempotent, simply adding more retries can make the system less safe.

---

# 55. Learning Checkpoints

After each major concept, ask:

- Is this failure transient or permanent?
- Is retrying safe?
- How many total attempts are possible?
- What happens between attempts?
- Is exponential backoff appropriate?
- Is a maximum delay needed?
- Does the task need an execution timeout?
- Is this a task timeout or a business deadline?
- Should a retry callback run?
- Should the final failure alert an operator?
- Is the alert actionable?
- Is the dataset fresh even if the task succeeded?
- What happens if one mapped task fails?
- What does the runbook say?

These questions test engineering judgment rather than parameter memorization.

---

# 56. Production Observability Checklist

A production implementation should consider:

- [ ] retry count;
- [ ] retry rate;
- [ ] task duration;
- [ ] timeout count;
- [ ] final failure count;
- [ ] failure category;
- [ ] callback execution;
- [ ] callback failures;
- [ ] alert count;
- [ ] alert severity;
- [ ] deadline misses;
- [ ] freshness misses;
- [ ] mapped-task failure distribution;
- [ ] repeated failures by task/source;
- [ ] owner and runbook coverage.

Use these signals to identify systemic problems.

For example:

```text
final failures stable
retry rate increasing
```

may indicate an emerging dependency problem before it becomes a large outage.

---

# 57. Common Mistakes Checklist

Avoid:

- retrying everything;
- never retrying transient failures;
- infinite retries;
- no backoff;
- no maximum retry delay;
- retry storms;
- retrying non-idempotent operations;
- nested retry explosions;
- no execution timeout;
- confusing timeout with deadline;
- using legacy Airflow 2 SLA syntax as current Airflow 3.x guidance;
- vague alerts;
- alerting on every retry;
- no runbook;
- ignoring mapped partial failures;
- assuming task success means data freshness;
- making callbacks too complex;
- allowing callback failure to obscure the original failure.

---

# 58. Production Failure-Management Checklist

Before deploying a critical DAG, ask:

## Failure classification

- [ ] Are transient and permanent failures distinguished?
- [ ] Are retryable exceptions identified from evidence?
- [ ] Are permanent errors prevented from entering long retry loops?

## Retry design

- [ ] Is retry count bounded?
- [ ] Is retry delay intentional?
- [ ] Is exponential backoff appropriate?
- [ ] Is maximum retry delay configured when needed?
- [ ] Are nested retries bounded?

## Retry safety

- [ ] Is the task idempotent?
- [ ] Can duplicate rows be created?
- [ ] Can duplicate external requests be created?
- [ ] Are transactions and unique keys appropriate?
- [ ] Are outputs deterministic?

## Timeout

- [ ] Does the task have a workload-appropriate execution timeout?
- [ ] Is the timeout based on observed behavior?
- [ ] Could the timeout terminate legitimate slow work?

## Deadline

- [ ] Is there a documented business deadline?
- [ ] Is deadline monitoring separate from retries?
- [ ] Is freshness monitored?
- [ ] Is quality monitored?

## Callbacks

- [ ] Is failure callback logic lightweight?
- [ ] Is retry callback logic low-noise?
- [ ] Is success callback logic appropriate?
- [ ] Are callback failures observable?

## Alerts

- [ ] Does every actionable alert identify the owner?
- [ ] Does it identify the run and task?
- [ ] Does it contain failure context?
- [ ] Does it link to logs?
- [ ] Does it link to a runbook?
- [ ] Does it contain a next action?
- [ ] Is severity defined by organizational policy?

## Mapped tasks

- [ ] Can operators identify failed map indexes/sources?
- [ ] Is partial failure behavior explicit?
- [ ] Is downstream completeness policy documented?

## Recovery

- [ ] Is there a safe rerun procedure?
- [ ] Is there an escalation path?
- [ ] Is the runbook current?
- [ ] Has failure injection been tested?

---

# 59. Final Knowledge Checklist

You should be able to answer **YES** to all of these:

- [ ] Can I classify transient vs permanent failures?
- [ ] Can I configure task retries?
- [ ] Can I configure retry delay?
- [ ] Can I explain exponential backoff?
- [ ] Can I explain maximum retry delay?
- [ ] Can I design safe retry behavior?
- [ ] Can I explain idempotency?
- [ ] Can I compare orchestrator retries with in-task retries?
- [ ] Can I prevent nested retry explosions?
- [ ] Can I configure execution timeouts?
- [ ] Can I distinguish task timeout from workflow/data deadline?
- [ ] Can I explain the Airflow 2 SLA legacy concept?
- [ ] Can I explain the Airflow 3.x deadline-oriented approach?
- [ ] Can I implement failure callbacks?
- [ ] Can I implement retry callbacks?
- [ ] Can I use success callbacks appropriately?
- [ ] Can I design actionable alerts?
- [ ] Can I prevent alert fatigue?
- [ ] Can I handle mapped-task partial failures?
- [ ] Can I design freshness monitoring?
- [ ] Can I create an operational runbook?
- [ ] Can I test failure behavior?
- [ ] Can I design retry policies for production?
- [ ] Can I explain the complete failure-management lifecycle?

---

# 60. Final Mental Model

The most important lesson is:

```text
                    TASK FAILURE
                         |
                         v
                CLASSIFY THE FAILURE
                         |
             ┌───────────┴───────────┐
             |                       |
         TRANSIENT                PERMANENT
             |                       |
       Is retry safe?              FAIL FAST
             |                       |
        ┌────┴────┐                  |
        |         |                  |
       YES        NO                 |
        |         |                  |
      RETRY     REDESIGN              |
        |                            |
    BACKOFF                          |
        |                            |
    TIMEOUT                          |
        |                            |
   SUCCESS?                          |
    /    \                           |
  YES    NO                          |
   |      |                          |
CONTINUE  FINAL FAILURE              |
            |                        |
            └──────────┬─────────────┘
                       |
                   CALLBACK
                       |
                ACTIONABLE ALERT
                       |
                    RUNBOOK
                       |
                    RECOVERY
                       |
             SAFE RERUN / PREVENTION
```

And around this lifecycle sit three independent operational controls:

```text
                 ┌──────────────────────┐
                 │      RETRIES         │
                 │ recovery mechanism   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     TIMEOUTS         │
                 │ execution boundary  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     DEADLINES        │
                 │ business expectation│
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    FRESHNESS         │
                 │ data-state outcome  │
                 └──────────────────────┘
```

A production-grade orchestrator does not merely "retry failed tasks."

It makes failure **bounded, classifiable, observable, actionable, and recoverable**.

That is the core operational skill this topic is designed to build.

---

## Version and Scope Notes

- Apache Airflow 3.x is the primary version for this chapter.
- Airflow 2.x SLA configuration is discussed only as legacy/reference material.
- Airflow 3.x Deadline Alerts are the current deadline-oriented concept described here. citeturn0search3turn1search0
- Version-sensitive APIs should be checked against the exact Airflow and provider versions used by the deployment.
- Numeric retry backoff multipliers are supported in current Airflow 3.3 documentation; explicit `2.0` is used in examples for clarity. citeturn1search10
- No universal retry counts, timeout values, alert thresholds, SLA targets, or recovery percentages are prescribed.
- Examples use illustrative values only.
- This chapter intentionally does not re-teach DAG fundamentals, Connections/Variables/Hooks/XComs, sensors/deferrable operators, backfills, Dagster, or Prefect.


---

## Source Alignment and Verification Note

This chapter was produced from the supplied Topic 07 specification, which explicitly requires the target file to cover retries, deadlines/SLAs, callbacks, failure classification, idempotency, mapped partial failures, runbooks, testing, failure injection, observability, production architecture, and exactly 40 interview questions. fileciteturn24file0L21-L27

The supplied specification also requires Airflow 3.x as primary and Airflow 2 SLA material to be clearly treated as legacy/reference material. fileciteturn24file0L95-L121

Official Apache Airflow documentation was checked for version-sensitive details concerning retries, callbacks, execution timeouts, Deadline Alerts, and the Airflow 2-to-3 SLA transition. citeturn0search0turn0search3turn0search4turn1search0
