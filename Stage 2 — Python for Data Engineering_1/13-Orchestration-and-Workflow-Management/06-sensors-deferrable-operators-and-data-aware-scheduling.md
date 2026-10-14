# Sensors, Deferrable Operators, and Data-Aware Scheduling

> **Roadmap alignment:** This chapter follows the uploaded Topic 06 specification for `13-Orchestration-and-Workflow-Management/`, including its Airflow 3.x-first scope, required labs, failure scenarios, resource analysis, and interview structure.

> **Apache Airflow 3.x | Production Data Engineering**
>
> Learning progression: **why waiting exists → Sensors → poke mode → reschedule mode → timeouts → soft failure → deferrable operators → Triggerer → custom triggers → custom sensors → data-aware scheduling → Assets → asset events → cross-DAG dependencies → event-driven pipelines → failure handling → testing → resource optimization → architecture → interview preparation**

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- Explain why waiting for external conditions is an orchestration problem.
- Define a Sensor and explain its lifecycle.
- Explain polling, `poke_interval`, timeout, success, failure, and soft failure.
- Compare Sensor **poke mode** and **reschedule mode**.
- Explain why long waits can consume worker capacity.
- Explain **deferrable operators** and asynchronous waiting.
- Explain the role of the **Triggerer**.
- Trace a deferred task from worker → triggerer → worker.
- Distinguish a normal Sensor, rescheduling Sensor, deferrable operator, Asset dependency, external-task dependency, and event trigger.
- Explain custom Sensors and custom Triggers.
- Explain Airflow 3.x **Assets**, asset events, asset dependencies, and data-aware scheduling.
- Combine data availability with time/deadline expectations.
- Design cross-workflow dependencies without creating unnecessary coupling.
- Distinguish **data arrival** from **data readiness**.
- Design bounded, observable waiting behavior.
- Test Sensors, deferral, triggers, and Asset scheduling without production credentials.
- Reason about worker, Triggerer, scheduler, metadata-database, network, and event-load implications at scale.
- Design a production waiting architecture for heterogeneous external feeds.

### The core principle

> **Waiting is work too. Production orchestration makes waiting bounded, observable, resource-efficient, and semantically correct.**

---

## 2. Prerequisites

This chapter assumes you already understand:

- DAGs and dependencies.
- Basic Airflow scheduling.
- Operators and TaskFlow.
- Airflow architecture at a conceptual level.
- Connections, Variables, Hooks, and XComs.

Those topics are intentionally not re-taught in full. This chapter builds on them by answering a different question:

> **What should an orchestrator do when the work cannot start yet because an external condition is not ready?**

Airflow 3.x is the primary version throughout this chapter. Any Airflow 2.x terminology is explicitly treated as legacy/reference material rather than the primary implementation model.

---

## 3. The Problem: Waiting for Data

Data Engineering pipelines frequently depend on systems that operate outside the Airflow task itself.

Examples:

- an SFTP partner has not uploaded today's file;
- an object has not appeared in object storage;
- a database partition has not been committed;
- an external API job is still running;
- another workflow has not completed;
- an upstream data product has not been published;
- a partner feed is late;
- an upstream Asset has not been updated.

A simple model is:

```text
External system
      |
      | data not available yet
      v
   Airflow
      |
      | wait
      v
condition becomes true
      |
      v
downstream task
```

The difficulty is that **waiting itself consumes resources if implemented naively**.

Suppose a task starts at 05:00 and the partner file arrives at 06:00.

A naïve implementation may keep a worker process alive for the entire hour:

```text
Worker
  |
  +-- check
  +-- sleep
  +-- check
  +-- sleep
  +-- check
  +-- ...
  +-- file arrives
```

That is logically simple, but operationally expensive when the number of waiting tasks grows.

### The first design question

Do not start with:

> "Which Sensor class should I use?"

Start with:

> **"What condition am I waiting for, how long might I wait, how reliable is the signal, and what infrastructure should perform the waiting?"**

That question leads naturally to Sensors, rescheduling, deferral, and Asset-driven orchestration.

### Checkpoint

1. What external condition is the workflow waiting for?
2. Is the condition observable?
3. Could the wait last seconds, minutes, hours, or longer?
4. Does waiting consume a worker slot?
5. What happens if the condition never becomes true?

---

## 4. What Is a Sensor?

### 4.1 Simple definition

A **Sensor** is a task whose job is to wait until a condition becomes true.

Conceptually:

```python
while not condition_is_true():
    wait()
```

The real Airflow implementation adds task state, scheduling, timeout behavior, logging, retries, and resource-management semantics.

### 4.2 The vocabulary

| Term | Meaning |
|---|---|
| Condition | The fact that must become true before the task can succeed |
| Polling | Repeatedly checking that condition |
| `poke_interval` | How long the Sensor waits between checks in polling-style operation |
| Timeout | Maximum allowed waiting period |
| Success | Condition became true |
| Failure | The Sensor cannot successfully complete its wait |
| Soft failure | A deliberate non-success outcome that can result in a skipped task rather than a hard failure, depending on Sensor behavior and downstream rules |
| Sensor state | Airflow's task/run state representing the Sensor's current lifecycle |

### 4.3 Minimal conceptual example

```text
Wait for:
    s3://bucket/orders/date=2026-10-02/_SUCCESS

Check:
    Does the readiness marker exist?

If NO:
    wait and check again

If YES:
    succeed
```

### 4.4 Real Data Engineering examples

A Sensor can represent:

```text
File condition:
    /landing/orders.csv exists

Object condition:
    s3://bucket/orders/date=.../_SUCCESS exists

Database condition:
    expected partition exists

Workflow condition:
    upstream workflow reached the required state

External-system condition:
    API job status == READY

Data condition:
    expected dataset publication is available
```

A Sensor is therefore an **orchestration boundary**. It should answer whether a condition is satisfied, not perform the entire downstream business transformation.

### Checkpoint

- What is the condition?
- What is being polled?
- What is the polling interval?
- What is the maximum acceptable wait?
- What should happen if the condition never becomes true?

---

## 5. Sensor Lifecycle

A simplified Sensor lifecycle is:

```text
Sensor starts
    |
    v
Check condition
    |
    v
Condition true?
   / \
 No   Yes
 |     |
 v     v
wait  success
 |
 v
check again
 |
 +-------> timeout/failure if wait limit is exceeded
```

Operationally:

1. Airflow schedules the Sensor task.
2. The Sensor begins executing.
3. It evaluates the condition.
4. If the condition is satisfied, the task succeeds.
5. If not, the Sensor waits according to its mode.
6. Airflow checks again.
7. The cycle continues until success or a terminal condition such as timeout/failure.
8. Downstream tasks react according to their dependency and trigger semantics.

The important production distinction is **where the waiting happens**.

### Worker-based waiting

```text
Worker
  |
  +-- condition check
  +-- wait
  +-- condition check
  +-- wait
  +-- ...
```

### Deferred waiting

```text
Worker
  |
  +-- initial work
  |
  +-- defer
       |
       v
   Triggerer
       |
       +-- asynchronous wait
       |
       v
   trigger event
       |
       v
   Worker resumes task
```

The condition is the same. The resource model is different.

### Checkpoint

If a Sensor is waiting for two hours, ask:

> "Which component is occupied during those two hours?"

That question is central to production orchestration.

---

## 6. Poke Mode

### 6.1 What poke mode means

In **poke mode**, the Sensor remains executing while it waits between condition checks.

Conceptually:

```text
Worker
  |
  +-- Sensor running
       |
       +-- check
       +-- sleep
       +-- check
       +-- sleep
       +-- check
```

The worker remains associated with the task for the duration of the wait.

### 6.2 Why it is simple

Poke mode is easy to understand:

```text
run task
  ↓
check
  ↓
not ready
  ↓
wait
  ↓
check again
```

For short waits, that simplicity can be useful.

### 6.3 Resource implication

A long-running poke-mode Sensor can occupy worker capacity without doing meaningful compute.

For example:

```text
20 worker slots
10 long-running Sensors
-----------------------
Only 10 slots remain for other work
```

This is not a universal performance benchmark; it is a capacity model.

If a Sensor waits for 30 seconds, the cost may be insignificant.

If it waits for 12 hours and many such Sensors run concurrently, the resource implications become architectural.

### 6.4 Educational file-waiting example

The exact Sensor class/API can vary by provider and Airflow release, so provider-specific examples should be verified against the installed Airflow 3.x provider version.

The conceptual structure is:

```python
from datetime import timedelta

# Illustrative provider Sensor configuration.
wait_for_file = SomeFileSensor(
    task_id="wait_for_orders",
    filepath="/landing/orders.csv",
    poke_interval=60,
    timeout=30 * 60,
    mode="poke",
)
```

The important ideas are:

- check every minute;
- do not wait forever;
- identify the condition explicitly;
- keep the Sensor focused on waiting;
- choose the mode deliberately.

### 6.5 When poke mode is reasonable

Poke mode can be appropriate when:

- the expected wait is short;
- worker capacity is comfortably available;
- the Sensor implementation is simple;
- the operational model benefits from continuous execution;
- the wait does not create material contention.

It should not be selected simply because it is the default pattern you remember from an old tutorial.

### Checkpoint

If 500 tasks can each wait for an hour, would you design the system by assuming all 500 workers can remain occupied?

If the answer is no, continue to rescheduling and deferral.

---

## 7. Reschedule Mode

### 7.1 The basic idea

**Reschedule mode** changes where the waiting happens.

Instead of keeping the worker occupied:

```text
Sensor
  |
  +-- check
  |
  +-- not ready
       |
       v
 release worker
       |
       v
 scheduled for another check
       |
       v
 check again
```

The Sensor performs a check, and if the condition is not ready, the task yields its worker capacity and becomes eligible for another scheduled check.

### 7.2 Why reschedule exists

The goal is to avoid holding a worker slot during idle waiting.

The logical behavior is still:

```text
check → not ready → wait → check
```

But the infrastructure behavior is closer to:

```text
check → release worker → return later
```

### 7.3 Resource model

Compare:

```text
POKE

Worker =============================>
       check  sleep  check  sleep
```

with:

```text
RESCHEDULE

Worker ===check===>
                  free
Scheduler/metadata state
                  |
                  v
Worker ===check===>
                  free
```

Rescheduling is therefore useful for conditions that may take a meaningful amount of time but can be checked periodically.

### 7.4 Example

```python
# Illustrative configuration; verify the concrete provider Sensor
# and supported mode in your Airflow 3.x environment.

wait_for_marker = SomeFileSensor(
    task_id="wait_for_done_marker",
    filepath="/landing/orders.csv.done",
    poke_interval=5 * 60,
    timeout=2 * 60 * 60,
    mode="reschedule",
)
```

The exact class is intentionally provider-dependent. The design principles are not:

- bounded timeout;
- deliberate polling interval;
- worker release while waiting;
- clear readiness condition.

### 7.5 When reschedule is useful

Reschedule is particularly useful when:

- the condition is naturally polled;
- waits are longer than a short interactive delay;
- the Sensor supports rescheduling;
- event-driven or deferrable waiting is unavailable or unnecessary;
- worker capacity is valuable.

### Checkpoint

Ask:

> "Can I perform a quick check, release the worker, and come back later?"

If yes, rescheduling may fit the condition.

---

## 8. Sensor Timeouts and Soft Failure

### 8.1 Why every production Sensor needs a bound

A production Sensor should normally have a deliberate upper bound.

Without one:

```text
File missing
   |
   v
Sensor waits
   |
   v
waits
   |
   v
waits
   |
   v
possibly never ends
```

That creates operational ambiguity.

A bounded wait gives the organization a defined response:

```text
Expected arrival: 06:00
Sensor begins:    05:30
Deadline:         06:30

06:30
  |
  v
timeout
  |
  +--> failure/skip according to policy
  +--> alert/escalation
  +--> runbook
```

### 8.2 `poke_interval`

`poke_interval` is a polling cadence.

A smaller interval means:

- faster detection when the condition changes;
- more checks;
- more external calls;
- potentially more scheduler/worker/network activity.

A larger interval means:

- fewer checks;
- lower polling pressure;
- potentially higher detection latency.

Do not choose an interval arbitrarily. Choose it based on:

- expected arrival behavior;
- acceptable detection latency;
- external-system rate limits;
- infrastructure cost;
- failure/recovery characteristics.

### 8.3 Timeout

Timeout answers:

> "How long are we willing to wait before this wait is considered unsuccessful?"

It should be connected to a business or operational expectation rather than a random number.

### 8.4 Soft failure

`soft_fail` is useful when missing data is an expected, non-critical condition and the workflow should intentionally treat the Sensor as skipped rather than as a hard failure, subject to downstream trigger rules.

Example:

```text
Optional partner feed
        |
        v
Sensor
        |
        +-- feed arrives --> process it
        |
        +-- deadline missed --> skip optional branch
```

This can be appropriate for:

- optional enrichment;
- non-critical partner feeds;
- best-effort auxiliary data.

It can be dangerous for:

- regulatory data;
- financial settlement inputs;
- primary revenue datasets;
- required operational feeds.

A critical dataset should not silently disappear merely because `soft_fail=True`.

### 8.5 Downstream implications

A skipped Sensor does not mean:

> "The data exists."

It means the orchestration policy decided that this missing condition should not hard-fail that task.

Downstream tasks must be designed with the resulting state in mind.

### Checkpoint

For every Sensor ask:

1. What is the expected arrival time?
2. What is the maximum acceptable wait?
3. What happens after timeout?
4. Is missing data optional or critical?
5. Which downstream states are acceptable?

---

## 9. Sensor Types and Waiting Conditions

Sensors are about conditions, not about collecting an endless catalog of provider classes.

### File/object conditions

```text
file exists?
object exists?
marker exists?
```

Examples:

```text
/landing/orders.csv
s3://bucket/orders/date=2026-10-02/_SUCCESS
```

### Database conditions

```text
table ready?
partition present?
row exists?
load status == COMPLETE?
```

A database readiness check should have a clear semantic contract. Merely finding a table does not prove that its contents are complete.

### Workflow conditions

```text
upstream workflow completed?
upstream task reached required state?
```

### External-system conditions

```text
API job status == READY?
partner export status == COMPLETE?
```

### Data conditions

```text
expected dataset available?
required partition published?
data product marked READY?
```

### Checkpoint

Do not confuse:

```text
condition = "object exists"
```

with:

```text
condition = "object is complete, valid, and published"
```

The second is a much stronger contract.

---

## 10. Data Engineering Waiting Patterns

### 10.1 SFTP `.done` marker

A common partner pattern is:

```text
partner uploads:
    orders.csv

after upload completes:
    orders.csv.done
```

Airflow waits for:

```text
orders.csv.done
```

and only then begins ingestion.

The marker can be useful because it expresses a stronger condition than simply checking whether the main file name exists.

But the marker is not automatically trustworthy. The pipeline still needs to understand the partner contract.

### 10.2 Object-storage readiness marker

A common conceptual pattern is:

```text
s3://bucket/orders/date=2026-10-01/
    |
    +-- part-0001
    +-- part-0002
    +-- part-0003
    +-- _SUCCESS
```

The orchestration contract might use `_SUCCESS` as a readiness signal.

Again:

> **A marker is only as reliable as the system that produces it.**

### 10.3 Database readiness

A database condition might look conceptually like:

```sql
SELECT COUNT(*)
FROM orders
WHERE order_date = :expected_date;
```

But row count alone may be a poor readiness test. A better contract might use:

- load status;
- partition metadata;
- ingestion watermark;
- completion flag;
- quality status;
- transactionally published table/version.

### 10.4 Arrival vs completeness vs validity

This distinction is foundational:

```text
File exists
    ≠
File complete
    ≠
Data valid
    ≠
Data published
```

For example:

```text
orders.csv exists
       |
       v
file completeness check
       |
       v
schema/quality check
       |
       v
publish
```

A Sensor can establish that a condition is true. It does not magically prove every downstream quality property.

---

## 11. Deferrable Operators

### 11.1 Why they were introduced

Reschedule mode releases a worker between checks, but it still represents periodic scheduling of Sensor checks.

**Deferrable operators** address a broader class of waits by moving asynchronous waiting into the Triggerer.

Core idea:

> **A deferrable task can stop occupying a worker while it waits for an asynchronous external condition.**

Traditional waiting:

```text
Worker
  |
  +-- start task
  +-- wait
  +-- wait
  +-- wait
  +-- condition occurs
```

Deferrable waiting:

```text
Worker
  |
  +-- start task
  |
  +-- defer
       |
       v
   Triggerer
       |
       +-- asynchronous waiting
       |
       v
   condition occurs
       |
       v
   task resumes
       |
       v
     Worker
```

### 11.2 The important distinction

The worker is still needed to perform the actual task work.

The optimization concerns the **waiting period**.

```text
Worker time:
    initialization + actual task execution

Triggerer:
    asynchronous waiting
```

### 11.3 Why this scales

If many tasks spend most of their lifecycle waiting on external I/O, holding worker processes for all those waits is inefficient.

Deferral changes the resource allocation:

```text
Many waiting tasks
        |
        v
Triggerer handles asynchronous waits
        |
        v
Workers handle actual execution
```

This separates:

- compute/execution capacity;
- waiting capacity.

### 11.4 A critical caveat

Deferral is not free.

You now depend on:

- a healthy Triggerer;
- correct trigger implementation;
- asynchronous behavior;
- provider support;
- correct task resumption;
- appropriate capacity and observability.

A more scalable mechanism can also create a more complex failure surface.

### Checkpoint

The question is not:

> "Is deferrable always better?"

The correct question is:

> **"Does this workload spend enough time waiting that asynchronous deferral justifies the added operational model?"**

---

## 12. The Triggerer

### 12.1 What is the Triggerer?

The **Triggerer** is an Airflow component responsible for running asynchronous triggers for deferred tasks.

A useful mental model:

```text
                 Airflow
                    |
                 start task
                    |
                    v
                 Worker
                    |
                  defer
                    |
                    v
               Triggerer
                    |
             async waiting
                    |
              condition true
                    |
                    v
              resume task
                    |
                    v
                 Worker
```

### 12.2 What the Triggerer does

The Triggerer:

- runs asynchronous trigger logic;
- waits for external conditions;
- detects trigger completion;
- produces a trigger event;
- allows the associated task to resume.

### 12.3 What the Triggerer does not do

It should not become a place for:

- heavy CPU computation;
- long blocking synchronous work;
- large business transformations;
- database-heavy ETL;
- arbitrary application logic.

The Triggerer is fundamentally a waiting mechanism.

### 12.4 Triggerer failure

A production design must answer:

> "What happens if the Triggerer is unavailable?"

A deferred task cannot resume normally until its trigger can be evaluated and produce its event.

Therefore observe:

- Triggerer process health;
- trigger execution failures;
- deferred task age;
- trigger backlog/capacity;
- resumption latency.

### Checkpoint

For a deferred task that appears stuck:

```text
Task deferred?
    |
    +-- yes
         |
         +-- Triggerer running?
              |
              +-- yes
              |    |
              |    +-- trigger executing?
              |         |
              |         +-- event generated?
              |              |
              |              +-- task resumed?
              |
              +-- no --> investigate Triggerer availability
```

---

## 13. Deferrable Operator Lifecycle

The lifecycle is:

```text
Task starts
    |
    v
perform initial work
    |
    v
defer
    |
    v
Triggerer waits
    |
    v
trigger fires
    |
    v
task resumes
    |
    v
task completes
```

### Before defer

A worker may:

- validate configuration;
- establish initial state;
- create or start an external operation;
- construct trigger arguments.

### During deferral

The worker is released.

The Triggerer executes the asynchronous trigger.

### Trigger event

The trigger reports that the external condition has reached the expected state.

The task then resumes.

### After resume

The task may:

- process the trigger event;
- perform remaining work;
- finalize state;
- succeed or fail.

### Failure paths

Failures can occur:

- before deferral;
- inside the trigger;
- while communicating with the external system;
- when resuming;
- after resumption.

The architecture therefore needs observability across the entire lifecycle, not only in the worker log.

---

## 14. Sensors vs Reschedule vs Deferrable

| Approach | Worker slot while waiting | Mechanism | Best fit | Trade-offs |
|---|---:|---|---|---|
| Poke Sensor | Occupied | Repeated checks inside running task | Short/simple waits | Can waste worker capacity during long waits |
| Reschedule Sensor | Released between checks | Periodic task rescheduling | Polling conditions with longer waits | Still poll-based; cadence matters |
| Deferrable operator | Released | Triggerer-driven asynchronous waiting | Long I/O waits and high concurrency where supported | Requires Triggerer and correct async/provider support |

### Decision process

Consider:

1. **Wait duration**
   - seconds?
   - minutes?
   - hours?

2. **Concurrency**
   - one wait?
   - dozens?
   - hundreds or thousands?

3. **Provider support**
   - does a tested deferrable implementation exist?

4. **Condition type**
   - simple periodic poll?
   - asynchronous I/O?
   - event-driven condition?

5. **Infrastructure**
   - is Triggerer deployed and monitored?

6. **Operational requirements**
   - how quickly must the condition be detected?
   - how important is the wait?

7. **Failure model**
   - what happens when the external system or Triggerer fails?

Do not reduce the decision to "long wait = deferrable" without considering provider support and operational architecture.

---

## 15. Deferrable Operator Example

A concrete deferrable API is provider/version-sensitive. In Airflow 3.x, prefer an operator or Sensor documented by the installed provider as supporting deferral.

The configuration often has a shape similar to:

```python
wait_for_external_job = SomeProviderOperator(
    task_id="wait_for_external_job",
    external_job_id="{{ params.job_id }}",
    deferrable=True,
    timeout=60 * 60,
)
```

The important production behavior is:

```text
task starts on worker
        |
        v
provider initiates/inspects operation
        |
        v
task defers
        |
        v
Triggerer waits asynchronously
        |
        v
external condition completes
        |
        v
task resumes
        |
        v
final work executes on worker
```

### Version discipline

Do not copy a provider-specific class from an old Airflow tutorial without checking:

- installed Airflow version;
- installed provider version;
- whether the operator supports `deferrable`;
- whether the provider's trigger is supported;
- timeout semantics;
- connection requirements.

This chapter intentionally avoids inventing a concrete provider class where the roadmap does not mandate one.

---

## 13. Custom Triggers

### 16.1 Definition

A **Trigger** is asynchronous logic that waits for an external condition.

A custom Trigger exists when the desired waiting behavior is not provided by an existing tested Trigger.

### 16.2 Trigger lifecycle

Conceptually:

```text
Task
  |
  v
defer
  |
  v
Custom Trigger
  |
  v
async polling / event wait
  |
  v
condition satisfied
  |
  v
trigger event
  |
  v
task resumes
```

### 16.3 Why custom triggers exist

Examples:

- internal API exposes an async job-status endpoint;
- proprietary service has no existing provider Trigger;
- internal platform emits a specialized readiness event;
- a custom asynchronous protocol must be integrated.

### 16.4 Trigger design requirements

A production Trigger should have:

- explicit configuration;
- serializable state/configuration;
- asynchronous waiting;
- bounded external calls where appropriate;
- clear success event;
- clear error behavior;
- safe logging;
- tests.

### 16.5 Never block an asynchronous Trigger

Bad:

```python
def run_blocking_request_forever():
    while True:
        response = requests.get(...)
        time.sleep(60)
```

The problem is not merely style. Blocking synchronous code defeats the purpose of an asynchronous waiting component.

A conceptual asynchronous pattern is:

```python
async def wait_for_ready(client):
    while True:
        status = await client.get_status()

        if status == "READY":
            return {"status": "READY"}

        await asyncio.sleep(30)
```

The exact Trigger implementation should use the Airflow 3.x Trigger APIs supported by the installed Airflow version.

### 16.6 Trigger event

The Trigger should emit enough non-sensitive information for the resumed task to understand what happened.

Avoid placing:

- passwords;
- tokens;
- large payloads;
- sensitive records

inside event metadata.

### Checkpoint

Ask:

> "Can this Trigger spend most of its time awaiting I/O rather than blocking a thread/process?"

If not, the design should be reconsidered.

---

## 14. Custom Trigger Example

Educational scenario:

```text
Internal API:
    GET /jobs/{job_id}

Possible status:
    RUNNING
    READY
    FAILED
```

Desired behavior:

```text
Task
  |
  v
defer
  |
  v
Custom Trigger
  |
  +-- GET status asynchronously
  |
  +-- RUNNING --> wait
  |
  +-- READY --> trigger event
  |
  +-- FAILED --> trigger failure
```

Illustrative pseudocode:

```python
class WaitForInternalJobTrigger:
    def __init__(self, job_id, poll_seconds):
        self.job_id = job_id
        self.poll_seconds = poll_seconds

    async def run(self):
        while True:
            status = await get_job_status(self.job_id)

            if status == "READY":
                yield {"status": "READY"}
                return

            if status == "FAILED":
                raise RuntimeError("Internal job failed")

            await asyncio.sleep(self.poll_seconds)
```

This is intentionally an educational shape, not a claim that the class above is a drop-in Airflow 3.x Trigger. A production implementation must inherit from and use the current Airflow 3.x Trigger API and serialization/event conventions supported by the installed version.

### Line-by-line reasoning

- `job_id` identifies the external condition.
- `poll_seconds` controls polling cadence.
- `await get_job_status(...)` represents non-blocking I/O.
- `READY` produces the completion event.
- `FAILED` becomes an explicit failure rather than an endless wait.
- `asyncio.sleep(...)` yields control during the wait.

---

## 15. Custom Sensors

A custom Sensor is appropriate when you have a reusable condition that fits naturally into Sensor semantics but no suitable existing Sensor meets the requirement.

Examples:

- internal readiness table;
- proprietary file marker convention;
- internal service health/readiness endpoint;
- reusable business-specific readiness condition.

A custom Sensor should separate:

```text
condition logic
    +
Airflow task semantics
```

### Good custom Sensor design

```text
Custom Sensor
    |
    +-- obtain connection/configuration
    +-- evaluate condition
    +-- log safe diagnostic information
    +-- return condition result
    +-- respect timeout/mode semantics
```

Avoid:

```text
Custom Sensor
    |
    +-- wait
    +-- transform 500 GB
    +-- call five unrelated APIs
    +-- mutate production tables
    +-- publish datasets
```

Waiting components should wait.

### Custom Sensor vs Custom Trigger

| Requirement | Custom Sensor | Custom Trigger / deferrable design |
|---|---|---|
| Simple reusable condition | Good fit | Possible but may be unnecessary |
| Periodic synchronous check | Natural fit | Possible |
| Long asynchronous I/O wait | Less attractive | Better fit |
| Need worker release during async wait | Reschedule or deferral needed | Natural fit |
| Existing provider Sensor unavailable | Useful | Useful if async semantics matter |
| Very high concurrent waits | May require careful resource design | Often a better architectural fit |

The correct choice depends on condition semantics and infrastructure.

---

## 16. Data-Aware Scheduling

Traditional orchestration often starts with a clock:

```text
07:00
  |
  v
run workflow
```

But data pipelines frequently care about a different event:

```text
upstream dataset updated
        |
        v
run downstream workflow
```

**Data-aware scheduling** means downstream work can be triggered because required data/assets become available, rather than relying only on wall-clock time.

### Three models

#### Time-driven

```text
07:00
  |
  v
run
```

#### Data-driven

```text
upstream dataset updated
        |
        v
run downstream
```

#### Hybrid

```text
upstream dataset updated
        +
time/deadline expectation
        |
        v
run downstream
```

The hybrid model is particularly useful for operational data products.

### Why this matters

A clock-based schedule may start before the data exists:

```text
06:00
 |
 +--> workflow starts
       |
       +--> data not ready
```

A data-aware schedule can align downstream work with the data lifecycle:

```text
data published
      |
      v
asset event
      |
      v
downstream workflow
```

---

## 17. Airflow 3.x Assets

### 20.1 Asset definition

In Airflow 3.x terminology, an **Asset** represents a data or data-like object whose update can participate in orchestration.

Think:

```text
Bronze Orders
      |
      v
Silver Orders
      |
      v
Gold Revenue
```

The important shift is from thinking only about tasks to also thinking about **data products and their dependencies**.

### 20.2 Asset identity

An Asset needs an identifiable logical representation so Airflow can reason about:

- what data object is being referenced;
- which workflows depend on it;
- when it is updated;
- which downstream work may become eligible.

### 20.3 Asset dependencies

Conceptually:

```text
orders_raw
    |
    v
orders_bronze
    |
    v
orders_silver
    |
    v
revenue_gold
```

This expresses a data dependency graph.

### 20.4 Illustrative Airflow 3.x style

Airflow's exact Asset APIs are version-sensitive, so the installed Airflow 3.x documentation should be treated as the final API authority. An educational shape is:

```python
from airflow.sdk import Asset

bronze_orders = Asset("s3://example-bucket/orders/bronze")
silver_orders = Asset("s3://example-bucket/orders/silver")
gold_revenue = Asset("s3://example-bucket/revenue/gold")
```

A DAG can then declare relationships around these data products according to the current Airflow 3.x asset scheduling API.

### 20.5 Why Assets can be more meaningful than task dependencies

Task-centric thinking:

```text
task_a >> task_b >> task_c
```

Asset-centric thinking:

```text
bronze asset updated
        |
        v
silver data product
        |
        v
gold data product
```

The second model communicates what data is produced and consumed, not merely which task happened to run first.

### Checkpoint

Ask:

> "If the task implementation changes but the produced data product remains the same, which representation communicates the business/data dependency more clearly?"

---

## 18. Asset Events and Dependencies

### 21.1 Asset event

An **asset event** represents an update/publication event associated with an Asset.

Conceptually:

```text
orders_bronze updated
        |
        v
asset event
        |
        v
silver workflow becomes eligible
```

### 21.2 Why events matter

They connect:

```text
data state
    |
    v
orchestration state
```

This improves the ability to reason about:

- data availability;
- lineage;
- downstream eligibility;
- event timing;
- operational dependencies.

### 21.3 Event metadata

Event metadata can provide useful context, but should remain:

- small;
- relevant;
- non-sensitive;
- stable enough for operations.

Do not use event metadata as a substitute for moving large datasets.

### 21.4 Asset dependency graph

Example:

```text
orders_raw
    |
    v
orders_bronze
    |
    v
orders_silver
    |
    v
revenue_gold
```

This can support a data-aware scheduling model in which downstream workflows respond to upstream data updates.

---

## 19. Time + Asset Scheduling

Consider:

> Gold revenue should run when upstream data is available, but the business expects it by 07:00.

The architecture becomes:

```text
Upstream asset update
        +
deadline expectation
        |
        v
downstream processing
        |
        v
quality gate
        |
        v
gold publish
```

This is not the same as:

```text
07:00 --> run regardless of data state
```

Nor is it:

```text
wait forever for data
```

Instead:

```text
data-aware trigger
        |
        +--> process promptly when ready
        |
        +--> operational deadline monitors lateness
```

The waiting mechanism and deadline policy should remain explicit.

Do not hide missing-data behavior inside an ambiguous schedule.

---

## 20. Cross-DAG Dependencies

Cross-workflow dependencies can be represented in several ways.

| Mechanism | Dependency expressed as | Useful when | Main concern |
|---|---|---|---|
| Asset dependency | Data product update | Data itself is the interface | Requires reliable Asset update semantics |
| External-task dependency | Task/workflow state | Explicit task-level coordination is required | Couples workflows to task identities/states |
| Trigger another workflow | Control-plane action | One workflow intentionally launches another | Creates control coupling |
| Sensor | Poll an external condition | No clean event/data dependency exists | Polling/resource cost |
| Event-driven mechanism | External event | Upstream system can emit reliable events | Event infrastructure/reliability |

No mechanism is universally correct.

### Example

Suppose:

```text
Ingestion workflow
        |
        v
bronze asset
        |
        v
Transformation workflow
```

If the important interface is the data product, an Asset dependency may express the architecture more directly than:

```text
DAG A task X
        |
        v
DAG B task Y
```

### External task dependency

An external task relationship can be appropriate when the semantic requirement truly is:

> "Do not proceed until that particular upstream workflow/task reaches the required state."

Use it deliberately because it creates stronger operational coupling.

---

## 21. Avoiding Tight Coupling

A dependency chain can become:

```text
DAG A
  |
  v
DAG B
  |
  v
DAG C
  |
  v
DAG D
  |
  v
DAG E
```

The problem is not the number of DAGs by itself.

The problem is **unnecessary coupling**.

Potential consequences:

- harder debugging;
- larger blast radius;
- more complicated scheduling;
- stronger deployment coordination;
- difficult reruns;
- unclear ownership;
- brittle cross-workflow assumptions.

A data interface can reduce coupling:

```text
Producer
   |
   v
Published Asset
   |
   v
Consumer
```

The producer and consumer can then communicate through a defined data contract.

---

## 22. Event-Driven Data Pipelines

### Polling

```text
Airflow
  |
  +-- check
  +-- check
  +-- check
  +-- check
```

### Event-driven

```text
External system
      |
      v
event
      |
      v
orchestration
      |
      v
downstream work
```

### Trade-offs

| Dimension | Polling | Event-driven |
|---|---|---|
| Latency | Depends on interval | Potentially lower |
| Resource usage | Repeated checks | Less polling when events are reliable |
| Complexity | Often simpler initially | More infrastructure/contract complexity |
| Reliability | Depends on repeated successful checks | Depends on reliable event delivery |
| Observability | Check history can be direct | Event delivery and processing need visibility |
| Scalability | Polling can grow expensive | Event volume and infrastructure become concerns |

Event-driven is not automatically simpler.

If an external partner cannot reliably emit an event, a well-designed polling Sensor may be more practical.

---

## 23. Production Failure Handling

Production waiting logic must assume that conditions can fail.

### Failure 1 — File never arrives

**Symptom:** Sensor waits until timeout.

**Root causes:**
- partner outage;
- incorrect path;
- upstream job failure;
- holiday/business-calendar mismatch;
- network failure.

**Detection:**
- timeout;
- missing-data metric;
- expected-arrival monitoring.

**Response:**
- inspect upstream status;
- verify connection;
- contact partner if required;
- follow late-data runbook.

**Prevention:**
- explicit deadline;
- validated path/configuration;
- upstream contract monitoring.

---

### Failure 2 — File arrives late

**Symptom:** File arrives after the expected processing window.

**Root cause:** upstream lateness.

**Detection:** compare actual arrival with expected arrival.

**Response:** process according to late-data policy; alert/escalate if deadline is exceeded.

**Prevention:** SLA/operational deadline visibility and upstream monitoring.

---

### Failure 3 — Marker arrives but actual data is incomplete

**Symptom:** `.done` exists, but the file is incomplete or corrupt.

**Root cause:** unreliable marker contract or incorrect upload protocol.

**Detection:** file-size/checksum/schema/completeness validation.

**Response:** stop downstream processing; quarantine/reject incomplete data.

**Prevention:** stronger producer contract and quality gates.

---

### Failure 4 — Object storage temporarily unavailable

**Symptom:** Sensor checks fail with connection/service errors.

**Root cause:** transient service or network issue.

**Detection:** connection errors and external-service telemetry.

**Response:** retry according to policy; avoid interpreting infrastructure failure as "data does not exist."

**Prevention:** resilient connection handling and meaningful timeouts.

---

### Failure 5 — Database condition cannot be queried

**Symptom:** readiness query fails.

**Root causes:** database outage, credentials, network, query problem.

**Detection:** connection/query error.

**Response:** distinguish "cannot check" from "checked and not ready."

**Prevention:** tested connection, least privilege, bounded queries, operational monitoring.

---

### Failure 6 — Triggerer unavailable

**Symptom:** deferred tasks remain deferred longer than expected.

**Root cause:** Triggerer failure/capacity problem.

**Detection:** Triggerer health monitoring and deferred-task age.

**Response:** restore/scale Triggerer capacity and inspect affected triggers.

**Prevention:** production deployment with monitored Triggerer capacity and redundancy appropriate to the environment.

---

### Failure 7 — Custom Trigger crashes

**Symptom:** trigger fails rather than producing the expected event.

**Root cause:** unhandled exception, invalid configuration, external API behavior.

**Detection:** Triggerer logs and trigger failure state.

**Response:** inspect trigger configuration and external dependency.

**Prevention:** unit/integration tests and explicit error handling.

---

### Failure 8 — Sensor timeout

**Symptom:** expected condition never became true before timeout.

**Root cause:** missing/late data or incorrect timeout.

**Detection:** timeout state.

**Response:** alert/escalate and follow the late-data runbook.

**Prevention:** business-aligned deadlines.

---

### Failure 9 — Asset event is missing

**Symptom:** downstream work never becomes eligible even though data appears updated.

**Root causes:** producer did not emit/update the Asset correctly; event path failed; dependency definition is wrong.

**Detection:** compare data state with Asset/event state.

**Response:** inspect producer and scheduling metadata.

**Prevention:** integration tests and explicit Asset contracts.

---

### Failure 10 — Duplicate asset events

**Symptom:** downstream processing is triggered more than expected.

**Root cause:** duplicate event production or incorrect update semantics.

**Detection:** event metadata/run history and duplicate patterns.

**Response:** make downstream work idempotent and determine whether duplicate scheduling is expected.

**Prevention:** producer contracts and idempotent consumers.

---

### Failure 11 — Downstream starts before data is actually ready

**Symptom:** pipeline begins but reads incomplete data.

**Root cause:** weak readiness signal.

**Detection:** quality/completeness checks.

**Response:** stop publication and repair readiness contract.

**Prevention:** distinguish arrival from readiness.

---

### Failure 12 — Sensor waits forever

**Symptom:** task remains waiting indefinitely.

**Root cause:** missing timeout or broken scheduling/condition logic.

**Detection:** task age and wait-duration monitoring.

**Response:** terminate according to runbook and correct the configuration.

**Prevention:** bounded waiting is mandatory for production conditions.

---

## 27. Data Arrival vs Data Readiness

This distinction deserves its own rule:

```text
File exists
    ≠
File complete
    ≠
Data valid
    ≠
Data published
```

A robust pipeline can model:

```text
arrival
  |
  v
completeness
  |
  v
schema validation
  |
  v
quality validation
  |
  v
publication
```

The Sensor should represent the appropriate condition for orchestration.

For example:

```text
orders.csv exists
       |
       v
checksum/size/completeness
       |
       v
schema/quality
       |
       v
publish bronze
```

This is where waiting connects to the broader Data Engineering architecture.

---

## 28. Sensor Timeout and Deadline Design

A practical operational contract might be:

```text
Expected arrival: 05:30
Warning:          06:00
Hard deadline:    06:30
```

Interpretation:

- **Expected arrival:** normal upstream behavior.
- **Warning:** operational attention is required.
- **Hard deadline:** the wait is no longer acceptable.

The Sensor timeout is one implementation mechanism. It should not be confused with the business deadline itself.

A useful model is:

```text
expected arrival
      |
      v
normal waiting
      |
      +---- late warning
      |
      v
hard deadline
      |
      +---- fail/escalate according to policy
```

Topic 07 covers broader retry/failure-callback patterns. Here the focus is the waiting and scheduling side of deadline design.

---

## 29. Security Considerations

Waiting components interact with external systems and therefore require careful security.

### Use secure Connections/secrets management

Do not hard-code:

```python
password = "production-secret"
```

Prefer Airflow Connections and supported secrets backends.

### Do not log credentials

Bad:

```text
Connecting to API with token=abc123...
```

Good:

```text
Checking external job status for job_id=...
```

### Least privilege

A Sensor should have only the access needed to evaluate its condition.

Examples:

- read-only object-storage access for existence checks;
- read-only database permissions for readiness queries;
- minimum API scope for job-status checks.

### Protect event metadata

Do not put:

- access tokens;
- passwords;
- customer records;
- large sensitive payloads

into trigger or Asset event metadata.

### Custom trigger security

Custom triggers are infrastructure code. Treat them as production code:

- validate inputs;
- authenticate securely;
- avoid logging secrets;
- use timeouts;
- handle malformed responses;
- limit external access.

---

## 30. Testing Sensors

Testing should cover the condition and the orchestration behavior.

### 30.1 Unit tests

Test the condition logic independently.

Example scenarios:

```text
condition true  -> success
condition false -> continue waiting
external error  -> expected exception/failure path
```

### 30.2 Mock external systems

Mock:

- SFTP;
- object storage;
- APIs;
- databases.

The goal is to test orchestration logic without requiring production infrastructure.

### 30.3 Timeout tests

Simulate:

```text
condition never becomes true
```

Verify that:

- the wait is bounded;
- the expected terminal state occurs;
- downstream behavior is correct;
- the operational signal is observable.

### 30.4 Failure tests

Simulate:

- connection error;
- malformed response;
- missing file;
- authentication failure;
- temporary external-service failure.

The test should distinguish:

```text
"data is not ready"
```

from:

```text
"I cannot determine whether data is ready"
```

Those are operationally different.

### 30.5 Deferrable tests

Validate:

```text
task starts
    |
    v
task defers
    |
    v
trigger runs
    |
    v
trigger completes/fails
    |
    v
task resumes or fails
```

### 30.6 Asset tests

Validate:

- Asset definitions;
- dependencies;
- scheduling conditions;
- update/event behavior;
- downstream eligibility.

---

## 31. Testing Example

A condition function can be isolated:

```python
def is_ready(response: dict) -> bool:
    return response.get("status") == "READY"


def test_ready_response():
    assert is_ready({"status": "READY"}) is True


def test_running_response():
    assert is_ready({"status": "RUNNING"}) is False
```

Then external access can be mocked:

```python
def test_external_failure_is_not_treated_as_not_ready():
    # Pseudocode:
    # mock_client.get_status.side_effect = ConnectionError(...)
    #
    # Assert that the Sensor/Trigger follows the
    # configured infrastructure-failure path.
    ...
```

The important principle is:

> **Test the decision logic independently from the external system.**

---

## 32. Observability

A waiting task should not be a black box.

Operators should be able to answer:

- What is this task waiting for?
- How long has it been waiting?
- How often has it checked?
- When was the last successful check?
- When is the expected arrival?
- What is the timeout?
- Which external dependency is involved?
- Did the external system reject the request?
- Is the Triggerer healthy?
- Did a trigger fail?
- Was an Asset updated?
- Was an Asset event missing?
- Did downstream work start late?

### Useful operational signals

```text
sensor_state
wait_duration
check_count
last_check_time
timeout_events
trigger_failures
triggerer_health
asset_update_events
missing_expected_data
downstream_start_latency
```

### Long waits are signals

A long wait may be:

- normal;
- a late upstream;
- an infrastructure incident;
- a configuration error;
- a broken event contract.

Therefore wait duration itself can be operationally meaningful.

---

## 33. Resource Efficiency

Consider:

```text
100 sensors × 30 minutes
```

The multiplication is not a benchmark. It is a reminder that waiting scales with concurrency.

### Poke

```text
worker
  |
  +-- wait
  +-- wait
  +-- wait
```

### Reschedule

```text
worker
  |
  +-- check
  |
  +-- release
  |
  +-- check later
```

### Deferrable

```text
worker
  |
  +-- initial work
  |
  +-- defer

Triggerer
  |
  +-- asynchronous waiting
```

At scale, reason about:

- worker utilization;
- Triggerer utilization;
- scheduler load;
- metadata-database interactions;
- polling frequency;
- external network calls;
- event volume;
- operational complexity.

### Scaling thought experiment

#### 5 waiting conditions

A simple Sensor may be entirely reasonable.

#### 50 waiting conditions

Polling cadence and worker utilization deserve explicit analysis.

#### 500 waiting conditions

The team should consider:

- deferral support;
- event-driven interfaces;
- Triggerer capacity;
- external-system rate limits;
- observability.

#### 5,000 waiting conditions

The architecture must be evaluated as a distributed waiting system rather than a collection of unrelated Sensors.

Do not invent universal capacity numbers. Actual limits depend on:

- infrastructure;
- provider implementation;
- external systems;
- polling intervals;
- Triggerer configuration;
- scheduler/database capacity.

---

## 34. Production Design Patterns

### Pattern 1 — SFTP marker waiting

```text
SFTP
  |
  +-- orders.csv
  +-- orders.csv.done
             |
             v
       waiting mechanism
             |
             v
         ingestion
```

The readiness contract is the marker, but ingestion should still validate the data.

### Pattern 2 — Object-storage readiness

```text
object(s)
   |
   v
readiness check
   |
   v
processing
```

A marker object can provide a stronger readiness contract than checking one arbitrary object.

### Pattern 3 — Database readiness

```text
upstream table
      |
      v
readiness condition
      |
      v
downstream transformation
```

The condition might be a partition status, load-complete record, watermark, or publication state.

### Pattern 4 — Asset-driven pipeline

```text
Bronze Asset
     |
     v
Asset Event
     |
     v
Silver
     |
     v
Asset Event
     |
     v
Gold
```

### Pattern 5 — Deadline-aware waiting

```text
wait for data
     |
     v
deadline
     |
     +---- data arrives --> process
     |
     +---- deadline missed --> alert/escalate
```

---

## 35. End-to-End Lab

### Scenario

A partner sends an orders file through SFTP.

Expected flow:

```text
Partner SFTP
      |
      +-- orders.csv
      +-- orders.csv.done
      |
      v
Airflow waiting mechanism
      |
      v
Bronze ingestion
      |
      v
Bronze Asset
      |
      v
Silver transformation
      |
      v
Silver Asset
      |
      v
Gold transformation
      |
      v
Quality gate
      |
      v
Gold publication
```

### Lab requirements

The implementation should demonstrate:

- SFTP waiting;
- `.done` marker;
- bounded timeout;
- deferrable waiting where appropriate;
- Asset definitions;
- Asset dependencies;
- Asset events;
- downstream scheduling;
- deadline awareness;
- safe logging;
- testing.

### Suggested implementation phases

#### Phase 1 — Define the contract

Write down:

```text
Expected file:
    orders.csv

Readiness signal:
    orders.csv.done

Expected arrival:
    05:30

Hard deadline:
    06:30
```

Do this before writing Airflow code.

#### Phase 2 — Implement waiting

Choose among:

- poke;
- reschedule;
- deferrable provider-supported mechanism.

Document why.

#### Phase 3 — Ingest

After readiness is established:

```text
SFTP
  |
  v
bronze
```

The ingestion task should not be embedded inside the Sensor.

#### Phase 4 — Define data products

Model:

```text
bronze_orders
silver_orders
gold_revenue
```

as Assets according to the installed Airflow 3.x Asset API.

#### Phase 5 — Add downstream scheduling

Connect Asset updates to downstream eligibility.

#### Phase 6 — Add quality validation

```text
silver
  |
  v
quality gate
  |
  +-- pass --> gold
  |
  +-- fail --> stop publication
```

#### Phase 7 — Add deadline behavior

If the file is missing:

```text
deadline exceeded
       |
       v
alert/escalate
       |
       v
do not silently publish incomplete data
```

#### Phase 8 — Add tests

Test:

- file exists;
- file missing;
- marker missing;
- external failure;
- timeout;
- valid Asset dependency;
- downstream scheduling;
- invalid/incomplete data.

---

## 36. Required Sensor Comparison Experiment — 50 Sensors

The roadmap requires a comparison of:

> **50 Sensors waiting for files**

Compare:

1. poke mode;
2. reschedule mode;
3. deferrable approach.

### Experiment design

Create a controlled environment in which 50 independent conditions have varying arrival times.

Record:

- worker slot occupancy;
- number of checks;
- waiting duration;
- external calls;
- scheduler/task activity;
- Triggerer activity where applicable;
- operational complexity.

Do **not** claim fabricated benchmark results.

Instead, produce observations such as:

```text
Mode: Poke
Expected effect:
    waiting tasks remain associated with workers

Mode: Reschedule
Expected effect:
    workers are released between checks

Mode: Deferrable
Expected effect:
    asynchronous waits are handled by Triggerer-supported triggers
```

### Experimental controls

Keep consistent:

- condition distribution;
- polling interval where comparable;
- timeout;
- environment;
- worker capacity;
- external system behavior.

### Interpretation

The purpose is not to prove one mode universally wins.

The purpose is to learn:

> **How the waiting mechanism changes resource consumption and operational behavior.**

---

## 37. Required Asset Lab

Build:

```text
bronze → silver → gold
```

as an Asset-oriented pipeline.

### Demonstrate

- bronze Asset;
- silver Asset;
- gold Asset;
- dependencies;
- Asset updates;
- downstream scheduling;
- event-aware behavior.

### Compare task-level and Asset-level thinking

Task-centric:

```text
extract >> transform >> publish
```

Asset-centric:

```text
bronze updated
       |
       v
silver available
       |
       v
gold available
```

Task dependencies answer:

> "What must execute before what?"

Asset dependencies answer:

> "What data must be updated before downstream data can be produced?"

A production architecture can use both.

---

## 38. Required SFTP Deadline Lab

Create a scenario where:

```text
partner file expected
       |
       v
Airflow waits
       |
       +---- arrives before deadline --> process
       |
       +---- late --> alert/escalate
       |
       +---- never arrives --> bounded failure/skip policy
```

### Required behavior

The workflow must not silently process incomplete data.

### Full lifecycle

```text
05:30 expected
      |
      v
wait
      |
      +---- 05:40 file arrives
      |          |
      |          v
      |      validate
      |          |
      |          v
      |       ingest
      |
      +---- 06:30 no file
                 |
                 v
            deadline action
```

---

## 39. Custom Sensor vs Deferrable Design Exercise

For each scenario, choose the appropriate waiting mechanism and explain why.

| Scenario | Considerations |
|---|---|
| 10-second wait | Very short; worker cost may be negligible |
| 5-minute wait | Compare simplicity with worker utilization |
| 2-hour wait | Worker occupancy becomes more significant |
| 12-hour wait | Strong case for non-worker waiting if supported |
| Event-driven API | Prefer a reliable event/async mechanism when available |
| SFTP marker | Depends on provider support and wait characteristics |
| Database readiness | Consider query cost, polling, and data semantics |
| Very high concurrent waits | Resource architecture becomes central |

Do not decide using time alone.

Also consider:

- provider support;
- Triggerer availability;
- external rate limits;
- latency requirements;
- operational complexity;
- reliability of event signals.

---

## 40. Code Review Exercises

### Bad example 1 — Long poke-mode Sensor

```python
wait_for_partner = SomeFileSensor(
    task_id="wait",
    filepath="/landing/orders.csv",
    poke_interval=60,
    timeout=12 * 60 * 60,
    mode="poke",
)
```

**Problem:** potentially occupies a worker for a long period.

**Impact:** worker capacity can be consumed by waiting.

**Correction:** evaluate reschedule or a supported deferrable approach.

**Why:** the wait is separated from worker execution.

---

### Bad example 2 — Infinite timeout

```python
wait_for_file = SomeFileSensor(
    task_id="wait",
    filepath="/landing/orders.csv",
    timeout=None,
)
```

**Problem:** no bounded operational behavior.

**Impact:** missing data can become an indefinitely waiting task.

**Correction:** use a business-aligned timeout/deadline.

---

### Bad example 3 — Polling every second

```python
poke_interval=1
```

**Problem:** unnecessary external calls if data normally arrives on a much slower cadence.

**Impact:** increased load and possible rate limiting.

**Correction:** choose a polling interval based on detection requirements and upstream limits.

---

### Bad example 4 — Logging credentials

```text
Connecting to SFTP with username=... password=...
```

**Problem:** sensitive information in logs.

**Impact:** credential exposure.

**Correction:** use secure Connections/secrets and log only safe identifiers.

---

### Bad example 5 — Sensor where Asset dependency is clearer

```text
workflow B
    |
    +-- poll workflow A every minute
```

If workflow A reliably publishes an Asset, an Asset dependency may communicate the actual data contract more directly.

---

### Bad example 6 — Asset dependency without reliable update semantics

If the upstream system has no reliable mechanism for representing Asset updates, declaring an Asset dependency does not magically create the missing signal.

Use an appropriate ingestion/event/polling boundary.

---

### Bad example 7 — Blocking custom Trigger

```python
def run():
    while True:
        requests.get(...)
        time.sleep(60)
```

**Problem:** blocking synchronous work in an asynchronous waiting component.

**Correction:** use the current Airflow 3.x Trigger API with non-blocking asynchronous I/O.

---

## 41. Debugging Workflow

Use a repeatable sequence:

```text
Observe task state
      |
      v
Check Sensor logs
      |
      v
Check condition being evaluated
      |
      v
Check Connection
      |
      v
Check external system
      |
      v
Check timeout
      |
      v
Check worker / Triggerer state
      |
      v
Check Asset / event state
      |
      v
Reproduce locally
      |
      v
Fix
      |
      v
Add regression test
```

### For deferrable tasks

Explicitly ask:

```text
Task deferred?
    |
    v
Triggerer running?
    |
    v
Trigger executing?
    |
    v
Trigger event generated?
    |
    v
Task resumed?
```

### Diagnostic distinction

A critical debugging question is:

> **Did the condition evaluate to false, or did the system fail to evaluate the condition?**

These are different incidents.

```text
Data not ready
    !=
Cannot check whether data is ready
```

---

## 42. Common Anti-Patterns

1. Using poke mode for extremely long waits.
2. Polling too frequently.
3. No timeout.
4. Infinite waiting.
5. Treating file existence as proof of data readiness.
6. Using Sensors where Asset dependencies are clearer.
7. Using Assets without reliable upstream update semantics.
8. Blocking inside asynchronous Triggers.
9. Putting heavy business logic inside Sensors.
10. Putting heavy work inside Triggers.
11. Ignoring Triggerer capacity/availability.
12. Logging secrets.
13. Creating unnecessary custom Sensors.
14. Creating unnecessary custom Triggers.
15. Overusing cross-DAG dependencies.
16. Building tightly coupled DAG chains.
17. Ignoring late-arriving data.
18. Assuming data-aware scheduling automatically guarantees data quality.

The recurring principle is:

> **Orchestration expresses when work should happen; it does not replace data-quality contracts.**

---

## 43. Trade-offs

### Polling vs event-driven

**Polling**
- simpler to introduce;
- easy to reason about;
- creates repeated external calls;
- detection latency depends on polling cadence.

**Event-driven**
- can reduce polling;
- can reduce latency;
- requires reliable event infrastructure;
- introduces event-delivery failure modes.

### Poke vs reschedule

**Poke**
- simple;
- continuous task execution;
- consumes worker capacity during wait.

**Reschedule**
- releases worker between checks;
- still uses periodic polling;
- introduces scheduling/rescheduling behavior.

### Reschedule vs deferrable

**Reschedule**
- simple polling model;
- useful when a condition can be checked periodically;
- still creates repeated scheduling/check cycles.

**Deferrable**
- asynchronous waiting;
- releases worker during wait;
- requires Triggerer and supported trigger implementation.

### Sensor vs Asset dependency

**Sensor**
- useful when an external condition must be polled;
- flexible for systems without a reliable Asset update contract.

**Asset dependency**
- expresses data relationships directly;
- useful when the producer can reliably represent data updates;
- does not replace data-quality validation.

### Sensor vs external-task dependency

**Sensor**
- observes a condition.

**External-task dependency**
- coordinates around a specific upstream task/workflow state.

### Custom Sensor vs custom Trigger

**Custom Sensor**
- natural for reusable Sensor-style conditions.

**Custom Trigger**
- useful when asynchronous waiting is the important behavior.

### Time-based vs Asset-based scheduling

**Time-based**
- predictable;
- easy to understand;
- can start before data is ready.

**Asset-based**
- data-aware;
- aligns scheduling with data updates;
- depends on correct Asset semantics.

### Event-driven vs scheduled workflows

Event-driven systems can react quickly, but they require trustworthy event contracts.

Scheduled workflows are often simpler, but can introduce avoidable waiting or unnecessary runs when upstream data is not ready.

---

## 44. Architecture Questions

### 1. Design a pipeline waiting for an SFTP file

Expected architecture:

```text
SFTP
  |
  +-- data file
  +-- .done marker
          |
          v
bounded waiting
          |
          v
ingestion
          |
          v
quality validation
          |
          v
publish
```

Reasoning:

- wait on a reliable readiness signal;
- bound the wait;
- avoid logging credentials;
- validate data after arrival.

---

### 2. Design a pipeline waiting for a database partition

```text
upstream load
    |
    v
partition readiness condition
    |
    v
downstream task
```

Reasoning:

- prefer an explicit load/publish contract;
- avoid expensive unrestricted queries;
- distinguish unavailable database from absent partition.

---

### 3. Design a pipeline waiting for object storage

```text
object upload
     |
     v
readiness marker/event
     |
     v
processing
```

Use a marker or reliable event when possible.

---

### 4. Design high-volume waiting with hundreds of conditions

Reasoning:

- inventory waiting conditions;
- classify polling vs event-driven;
- prefer supported deferrable patterns for long async waits;
- size Triggerer capacity;
- protect external APIs from excessive polling;
- monitor wait age and trigger failures.

---

### 5. Design an Asset-driven bronze/silver/gold pipeline

```text
bronze Asset
    |
    v
silver Asset
    |
    v
gold Asset
```

Each publication should represent a meaningful data product update.

---

### 6. Design a deadline-aware pipeline

```text
data wait
   |
   +---- ready --> process
   |
   +---- late --> warning
   |
   +---- deadline --> escalation/failure policy
```

---

### 7. Design a cross-DAG dependency strategy

First determine whether the dependency is:

- data-oriented;
- task-state-oriented;
- control-flow-oriented;
- event-oriented.

Then select the mechanism that matches that contract.

---

### 8. Design a custom Trigger for an internal API

```text
task
 |
 +-- start/inspect external job
 |
 +-- defer
       |
       v
async custom Trigger
       |
       +-- RUNNING --> await
       +-- READY --> event
       +-- FAILED --> error
```

Keep the Trigger lightweight and asynchronous.

---

### 9. Design hybrid time + data scheduling

```text
Asset update
    +
business deadline
    |
    v
downstream processing
    |
    v
quality gate
```

The Asset controls data readiness; operational monitoring controls lateness.

---

### 10. Design failure handling when an upstream event never arrives

Required properties:

- bounded wait;
- observable state;
- alert/escalation;
- no silent publication;
- clear runbook;
- idempotent recovery path.

---

## 45. Interview Questions

### 10 Basic

#### 1. What is an Airflow Sensor?

**Answer:** A Sensor is a task whose purpose is to wait until an external or internal condition becomes true. It typically evaluates a condition repeatedly or uses another waiting mechanism and eventually succeeds, fails, or follows a configured non-success policy.

#### 2. What is poke mode?

**Answer:** Poke mode keeps the Sensor task executing while it waits between condition checks. Therefore the task remains associated with worker capacity during the wait.

#### 3. What is reschedule mode?

**Answer:** Reschedule mode allows a Sensor to perform a check and, when the condition is not ready, release the worker and become eligible for another check later.

#### 4. What is `poke_interval`?

**Answer:** It controls the interval between Sensor condition checks in polling-style operation. It should be selected based on detection latency, external-system limits, and infrastructure cost.

#### 5. Why should a Sensor have a timeout?

**Answer:** Without a timeout, missing or broken upstream conditions can produce indefinitely waiting tasks. A timeout creates a defined operational boundary.

#### 6. What is soft failure?

**Answer:** Soft failure allows an appropriate Sensor policy to treat a missing condition as a non-hard-failure outcome, commonly resulting in a skipped task state. It should be used only when the missing input is intentionally optional.

#### 7. What is a deferrable operator?

**Answer:** A deferrable operator can defer its task while waiting for an asynchronous external condition, allowing the worker to be released while the Triggerer handles the waiting.

#### 8. What is the Triggerer?

**Answer:** The Triggerer runs asynchronous Trigger logic for deferred tasks. When a Trigger detects the desired condition, it produces an event that allows the task to resume.

#### 9. What is an Airflow Asset?

**Answer:** In Airflow 3.x, an Asset represents a data or data-like object whose updates can participate in orchestration and downstream scheduling.

#### 10. What is data-aware scheduling?

**Answer:** It is scheduling driven by data or Asset availability/update events rather than relying only on a wall-clock schedule.

---

### 10 Moderate

#### 1. Why can poke-mode Sensors become expensive?

**Answer:** A long-running poke-mode Sensor remains associated with a worker while waiting. With many concurrent waits, worker capacity can be consumed by idle waiting instead of useful computation.

#### 2. When would you choose reschedule mode?

**Answer:** Use it when the condition can be checked periodically, the wait may be meaningful, and releasing the worker between checks is useful. It is particularly suitable when a simple polling model is sufficient.

#### 3. Why is a deferrable operator different from reschedule mode?

**Answer:** Reschedule performs periodic task scheduling/check cycles. Deferral moves asynchronous waiting into a Trigger executed by the Triggerer, allowing a richer non-blocking wait lifecycle.

#### 4. Why does a Trigger need to be asynchronous?

**Answer:** The Triggerer is intended to handle many waiting conditions efficiently. Blocking synchronous work would undermine that model and can reduce concurrency.

#### 5. Why is a `.done` marker useful?

**Answer:** It can provide a producer-defined readiness signal that is stronger than merely checking whether the main file name exists. Its reliability still depends on the producer contract.

#### 6. Why is file existence not the same as data readiness?

**Answer:** A file can exist while still being incomplete, malformed, invalid, or not formally published. Readiness should represent the condition the downstream workflow actually requires.

#### 7. When is an Asset dependency preferable to polling?

**Answer:** When the producer can reliably represent the update of the data product and the dependency is fundamentally data-oriented. The Asset then communicates the data contract directly.

#### 8. What happens if a Triggerer is unavailable?

**Answer:** Deferred tasks depending on triggers may remain deferred until trigger processing becomes available. Production systems therefore need Triggerer health monitoring and capacity planning.

#### 9. Why should event metadata be small and non-sensitive?

**Answer:** Event metadata is orchestration context, not a data-transfer mechanism. Large or sensitive payloads increase security, storage, and operational risk.

#### 10. Why should a Sensor avoid heavy business logic?

**Answer:** A Sensor's responsibility is to establish a condition. Embedding transformations or large data operations makes waiting logic harder to test, scale, and operate.

---

### 10 Hard

#### 1. How would you choose between poke, reschedule, and deferrable waiting?

**Answer:** Classify the condition by wait duration, concurrency, polling characteristics, provider support, Triggerer availability, latency requirement, external rate limits, and operational complexity. There is no universal winner.

#### 2. How would you debug a task stuck in deferred state?

**Answer:** Verify that the task actually deferred, confirm the Triggerer is healthy, inspect whether the Trigger is executing, inspect Trigger logs, verify that the external condition can be reached, determine whether a trigger event was generated, and confirm whether the task resumed.

#### 3. How can an Asset-based design reduce coupling?

**Answer:** It allows producers and consumers to communicate through a data product contract instead of directly depending on implementation-specific task identities. The producer can change internal task structure while preserving the published Asset contract.

#### 4. What is the difference between data arrival and data publication?

**Answer:** Arrival means data has appeared somewhere. Publication means the producer has declared it available according to the agreed contract. Between them may be completeness, validation, and quality checks.

#### 5. How can duplicate Asset events affect a pipeline?

**Answer:** They may cause downstream eligibility or runs to occur more often than intended, depending on scheduling semantics. Consumers should therefore be designed with idempotency and clear event semantics.

#### 6. Why should polling intervals be designed rather than guessed?

**Answer:** Polling affects detection latency, external API/database load, network traffic, scheduler activity, and operational cost. The interval is part of the system's resource and reliability design.

#### 7. How would you design a custom Trigger for an internal API?

**Answer:** Define serializable configuration, use the current Airflow 3.x Trigger interface, perform asynchronous I/O, handle RUNNING/READY/FAILED states, emit a small safe event, and test both success and failure paths.

#### 8. Why can event-driven orchestration still fail?

**Answer:** Events can be lost, duplicated, delayed, malformed, or produced incorrectly. Event-driven design changes the failure surface; it does not eliminate reliability engineering.

#### 9. How would you distinguish "data not ready" from "cannot check readiness"?

**Answer:** Model external-system failures separately from a false readiness condition. A successful query returning "not ready" is different from a connection timeout or authentication failure.

#### 10. What should be monitored for a high-volume waiting system?

**Answer:** Worker utilization, Triggerer health/capacity, deferred-task age, Sensor wait duration, check count, external-call errors, polling rate, Asset events, missed expected updates, and downstream start latency.

---

### 10 Advanced

#### 1. Design a waiting architecture for 5,000 possible external conditions.

**Answer:** Avoid treating each wait as an isolated worker task. Classify conditions into polling and event-driven categories, use supported deferrable mechanisms for asynchronous waits, minimize polling frequency, protect external systems, size and monitor Triggerer capacity, and define event/Asset contracts where possible.

#### 2. How would you combine an Asset dependency with a business deadline?

**Answer:** Let the Asset/update signal represent data availability while an independent operational deadline tracks expected completion. Process when data is ready; if the deadline is missed, trigger warning/escalation behavior rather than silently running with incomplete inputs.

#### 3. What makes a custom Trigger production-grade?

**Answer:** Correct Airflow 3.x API usage, serializable configuration, asynchronous I/O, bounded external interactions, explicit terminal states, safe logging, error handling, tests, observability, and compatibility with the deployed Triggerer architecture.

#### 4. When would a Sensor be preferable to an Asset dependency?

**Answer:** When the upstream condition is external and cannot reliably be represented as an Asset update, or when the required semantics are explicitly a readiness check rather than a data-product publication contract.

#### 5. How would you prevent a marker file from causing premature processing?

**Answer:** Establish a producer contract for the marker, validate completeness after the marker is observed, and use schema/quality checks before publication. The marker should be treated as a readiness signal, not proof of data quality.

#### 6. What is the architectural difference between task-centric and asset-centric orchestration?

**Answer:** Task-centric orchestration describes execution dependencies. Asset-centric orchestration describes relationships between produced and consumed data products. Production systems may need both layers.

#### 7. How would you handle an unreliable external event source?

**Answer:** Establish whether events can be replayed or reconciled. If not, supplement the event path with a bounded polling/reconciliation mechanism. Ensure downstream processing is idempotent so duplicate recovery signals are safe.

#### 8. How would you test a deferrable workflow without production infrastructure?

**Answer:** Unit-test condition logic, mock external clients, test trigger serialization/configuration, exercise success/failure/timeout paths, and use an isolated Airflow test environment where appropriate to verify defer/resume integration.

#### 9. How would you design observability for late data?

**Answer:** Track expected arrival, actual observation time, current wait duration, timeout/deadline status, upstream dependency identity, Asset/event state, and downstream start latency. Alerts should distinguish warning from hard-deadline conditions.

#### 10. What is the most important production principle for waiting logic?

**Answer:** Make waiting **bounded, resource-efficient, observable, and semantically correct**. The pipeline should know what it is waiting for, why it is waiting, how long it may wait, what happens if the condition never arrives, and how operators recover.

---

## 46. Practical Exercises

### Beginner

1. Create a simple file-waiting Sensor.
2. Change `poke_interval` and observe the effect.
3. Add a timeout.
4. Simulate a missing file.
5. Explain the Sensor lifecycle in your own words.

### Intermediate

1. Convert a polling Sensor from poke to reschedule mode.
2. Build an object-storage readiness check.
3. Implement a database readiness condition.
4. Add a business-aligned deadline.
5. Test external-system failure separately from "not ready."

### Advanced

1. Use a provider-supported deferrable operator.
2. Inspect Triggerer behavior.
3. Build a custom Trigger using the current Airflow 3.x API.
4. Build a custom Sensor.
5. Create Asset dependencies.
6. Implement data-aware scheduling.
7. Compare Sensor and Asset approaches.

### Expert / Production

Design a waiting architecture with:

- hundreds of possible waiting conditions;
- limited worker capacity;
- late data;
- missing data;
- Asset-driven downstream workflows;
- operational deadlines;
- alerts;
- tests;
- observability.

Document:

```text
condition model
waiting mechanism
resource model
failure model
deadline model
event model
data contract
test strategy
observability
```

---

## 47. Final Practical Challenge

A company receives five external data feeds.

### Feed behavior

- **Feed A:** SFTP file with `.done` marker.
- **Feed B:** object-storage object.
- **Feed C:** database partition.
- **Feed D:** REST API job.
- **Feed E:** upstream Airflow Asset.

### Requirements

- process data as soon as it is ready;
- avoid wasting worker slots while waiting;
- detect late data;
- enforce operational deadlines;
- avoid silently processing incomplete data;
- trigger downstream transformations;
- maintain bronze → silver → gold Asset lineage;
- support retries and reruns;
- maintain test coverage;
- provide operational visibility.

### Your design must specify

1. Waiting mechanism for each feed.
2. Sensor/reschedule/deferrable choice.
3. Trigger strategy.
4. Asset strategy.
5. Deadline strategy.
6. Failure handling.
7. Observability.
8. Testing strategy.
9. Resource/scalability model.
10. Recovery and rerun behavior.

### Expected architecture

```text
Feed A: SFTP
    |
    +-- .done marker
    |
    v
bounded/deferrable waiting
    |
    v
Bronze Asset

Feed B: Object storage
    |
    +-- reliable readiness signal
    |
    v
Bronze Asset

Feed C: Database
    |
    +-- partition/readiness contract
    |
    v
Bronze Asset

Feed D: REST API
    |
    +-- asynchronous job status
    |
    v
deferrable/custom Trigger where appropriate
    |
    v
Bronze Asset

Feed E: Airflow Asset
    |
    +-- Asset dependency
    |
    v
Bronze/consumer workflow

All feeds
    |
    v
Bronze
    |
    v
Silver
    |
    v
Gold
    |
    v
Quality gate
    |
    v
Publication
```

### Reasoning

The architecture should avoid using one waiting mechanism for every feed.

Instead:

- use reliable data contracts;
- use polling where polling is appropriate;
- use rescheduling when periodic checks are sufficient;
- use deferral for supported long asynchronous waits;
- use Assets when the dependency is fundamentally data-oriented;
- use explicit deadlines for missing data;
- make downstream work idempotent;
- keep waiting logic separate from transformations.

### Production checklist

- [ ] Every wait has a clear condition.
- [ ] Every production wait has a bounded operational policy.
- [ ] Worker capacity is not unnecessarily consumed by long waits.
- [ ] Triggerer capacity is monitored where deferral is used.
- [ ] External-system failures are distinguished from "not ready."
- [ ] Data arrival is not confused with data readiness.
- [ ] Asset updates represent meaningful data contracts.
- [ ] Duplicate events are safe.
- [ ] Late data has an operational response.
- [ ] Secrets are not logged.
- [ ] External dependencies are tested with mocks.
- [ ] Timeout behavior is tested.
- [ ] Deferred/resume behavior is tested.
- [ ] Asset scheduling behavior is tested.
- [ ] Operators can see what a task is waiting for.
- [ ] Recovery and rerun behavior is documented.

---

## 48. Relationship to Other Module 2.13 Topics

### Topic 04 — DAGs, Operators, and TaskFlow API

This chapter uses the task/operator foundation from Topic 04.

The connection is:

```text
Operator
   |
   v
Sensor / deferrable behavior
   |
   v
downstream task
```

Topic 04 teaches how tasks are built. This chapter focuses on **how tasks wait efficiently**.

### Topic 05 — Connections, Variables, Hooks, and XComs

Waiting components often use Connections and Hooks to access external systems.

For example:

```text
Sensor
  |
  v
Connection
  |
  v
external system
```

This chapter focuses on waiting semantics, not credential-management mechanics.

### Topic 07 — Retries, Deadlines, and Failure Callbacks

This chapter establishes:

- bounded waiting;
- missing-data deadlines;
- timeout behavior.

Topic 07 expands the broader retry/failure callback architecture.

### Topic 08 — Backfills, Catch-up, and Partitioned Runs

A waiting condition often relates to a particular data interval or partition.

Topic 08 focuses on how runs are replayed and partitioned. This chapter focuses on **waiting for the condition that makes a run eligible**.

---

## 49. Relationship to Earlier Data Engineering Modules

### Module 2.9 — Data Ingestion

A common relationship is:

```text
external source
      |
      v
waiting mechanism
      |
      v
ingestion
```

The waiting mechanism should not become the ingestion implementation.

### Module 2.11 — Data Validation and Quality

The Sensor may establish:

```text
data arrived
```

Validation establishes:

```text
data is acceptable
```

These are different contracts.

### Module 2.12 — Transformation Patterns and Pipeline Design

A typical architecture is:

```text
Ingestion
   |
   v
Sensor / Deferrable wait
   |
   v
Transformation
   |
   v
Quality gate
   |
   v
Publish
```

Or, for data-aware orchestration:

```text
Asset update
   |
   v
Transformation
   |
   v
Quality validation
   |
   v
Published dataset
```

This chapter connects these modules without re-teaching them.

---

## 50. Learning Checkpoints

After each major concept, verify that you can answer:

- What problem does this mechanism solve?
- Does it consume a worker slot while waiting?
- What happens if the condition never becomes true?
- What happens if the external system is unavailable?
- When should this be a Sensor?
- When should it be rescheduled?
- When should it be deferrable?
- When should it be Asset-driven?
- What is the difference between data arrival and data readiness?
- What happens if the Triggerer is unavailable?
- How would you test this without production infrastructure?

The goal is understanding, not memorization.

---

## 51. Code Quality Requirements

All examples should:

- target Airflow 3.x;
- be syntactically coherent;
- use realistic API patterns;
- avoid invented classes/methods;
- avoid hard-coded secrets;
- use placeholders where credentials are required;
- include useful comments;
- explain important lines;
- show failure handling;
- demonstrate production-safe patterns.

### Version-sensitive API rule

Airflow and provider APIs evolve.

Before using a provider-specific Sensor/operator/Trigger in a real project, verify:

```text
Airflow version
+
provider version
+
supported operator/Trigger API
```

Airflow 2.x examples found in older tutorials should not be copied into an Airflow 3.x production project without deliberate migration review.

---

## 52. Testing Quality Requirements

The test suite should cover:

- Sensor condition logic;
- timeout behavior;
- missing-file behavior;
- external-system failure;
- reschedule behavior;
- deferral behavior;
- Trigger logic;
- Trigger failure;
- Asset definitions;
- Asset dependencies;
- scheduling conditions;
- event handling.

External systems should be mocked where practical.

Production credentials should never be required merely to run unit tests.

---

## 53. Resource and Scalability Analysis

Use this conceptual progression:

```text
5 waiting conditions
       |
       v
50 waiting conditions
       |
       v
500 waiting conditions
       |
       v
5,000 waiting conditions
```

Do not assign universal capacity numbers.

Instead analyze:

- worker slots;
- Triggerer capacity;
- scheduler load;
- metadata-database load;
- polling frequency;
- network calls;
- external rate limits;
- event volume;
- operational complexity.

### Architectural shift

At small scale:

```text
simple Sensor
```

may be adequate.

At higher scale:

```text
Sensors
 + rescheduling
 + deferrable waits
 + events
 + Assets
 + monitoring
```

may become a more appropriate architecture.

The correct design depends on actual workload characteristics.

---

## 54. Observability Checklist

Production operators should be able to answer:

- [ ] What is this task waiting for?
- [ ] How long has it been waiting?
- [ ] What is the expected arrival time?
- [ ] What external dependency is involved?
- [ ] What is the timeout/deadline?
- [ ] Has the condition been checked recently?
- [ ] Did a check fail because the data was absent or because the system was unreachable?
- [ ] Is the Triggerer healthy?
- [ ] Did a Trigger fail?
- [ ] Did the expected Asset update occur?
- [ ] Is an Asset event missing?
- [ ] Are duplicate events occurring?
- [ ] Is the data actually ready?
- [ ] When did downstream processing start?

---

## 55. Final Knowledge Checklist

You should be able to answer **YES** to all of these:

- [ ] Can I explain what a Sensor is?
- [ ] Can I explain poke mode?
- [ ] Can I explain reschedule mode?
- [ ] Can I compare poke and reschedule?
- [ ] Can I configure Sensor timeouts?
- [ ] Can I explain soft failure?
- [ ] Can I explain deferrable operators?
- [ ] Can I explain the Triggerer?
- [ ] Can I explain how a deferred task resumes?
- [ ] Can I explain custom Triggers?
- [ ] Can I explain custom Sensors?
- [ ] Can I decide when to use each?
- [ ] Can I explain Airflow 3.x Assets?
- [ ] Can I explain Asset events?
- [ ] Can I explain data-aware scheduling?
- [ ] Can I compare time-based and Asset-based scheduling?
- [ ] Can I design cross-DAG dependencies?
- [ ] Can I design event-driven pipelines?
- [ ] Can I distinguish data arrival from data readiness?
- [ ] Can I design a deadline for missing data?
- [ ] Can I test Sensors?
- [ ] Can I test Triggers?
- [ ] Can I test Asset dependencies?
- [ ] Can I debug Triggerer problems?
- [ ] Can I design a production waiting architecture?

---

## 56. Final Self-Review

### Roadmap coverage

This chapter includes:

- Sensors;
- file/object waiting;
- SQL/database readiness;
- workflow dependencies;
- `poke_interval`;
- timeout;
- soft failure;
- poke mode;
- reschedule mode;
- deferrable operators;
- Triggerer;
- Trigger mechanics;
- custom Sensor;
- custom Trigger;
- Airflow 3.x Assets;
- Asset events;
- Asset/time conditions;
- cross-DAG dependencies;
- event-driven scheduling;
- SFTP `.done` marker;
- 50-Sensor comparison;
- bronze/silver/gold Asset pipeline;
- deadline-aware waiting.

### Technical correctness discipline

The chapter keeps:

- Airflow 3.x as primary;
- Airflow 2.x as legacy/reference material;
- provider-specific examples explicitly version-sensitive;
- no fabricated benchmark results;
- no arbitrary universal capacity claims;
- no insecure credential examples.

### Learning quality

The chapter progresses:

```text
basic
  ↓
intermediate
  ↓
advanced
  ↓
production
```

and uses:

```text
Concept
  ↓
Why
  ↓
Mental model
  ↓
Internal mechanics
  ↓
Example
  ↓
Failure
  ↓
Debugging
  ↓
Production pattern
  ↓
Trade-offs
  ↓
Testing
  ↓
Architecture
```

### Scope discipline

This chapter does not attempt to replace:

- Airflow architecture;
- DAG/operator fundamentals;
- Connections/Variables/Hooks/XComs;
- retries/failure callbacks;
- backfills;
- Dagster;
- Prefect.

It only explains relationships needed to understand waiting and data-aware scheduling.

---

## 57. Final Mental Model

When a production workflow cannot start yet, ask five questions:

### 1. What exactly am I waiting for?

```text
file?
object?
database state?
workflow?
API job?
Asset?
event?
```

### 2. Is the condition actually a data contract?

```text
arrival
  ≠
completeness
  ≠
validity
  ≠
publication
```

### 3. Where should the waiting happen?

```text
worker?
reschedule?
Triggerer?
event system?
```

### 4. What happens if it never becomes true?

```text
timeout
warning
failure
skip
escalation
recovery
```

### 5. Can the system scale?

```text
5 waits
50 waits
500 waits
5,000 waits
```

Consider:

```text
worker capacity
Triggerer capacity
scheduler
metadata DB
external APIs
network
events
observability
```

The mature design is not:

> "Use a Sensor."

It is:

> **"Model the readiness condition correctly, choose an efficient waiting mechanism, bound the wait, expose its state operationally, and connect the resulting data state to downstream orchestration."**

---

# Production Principle

> **A production-grade waiting mechanism should never be an invisible sleep loop. It should be an explicit orchestration contract with a clear condition, bounded waiting behavior, appropriate resource model, observable state, defined failure path, and testable semantics.**

That principle is the foundation for reliable Sensors, deferrable operators, Triggerer-based asynchronous waiting, and Airflow 3.x data-aware scheduling.
