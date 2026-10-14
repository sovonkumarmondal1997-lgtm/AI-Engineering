# Module 2.13 — Orchestration and Workflow Management
# Practice Questions

## How to Use These Questions

This practice set tests the complete `13-Orchestration-and-Workflow-Management/` module from foundational reasoning through senior Data Engineering architecture.

For each question:

1. Read the **Problem** without immediately reading the solution.
2. Draw the workflow when useful.
3. Identify triggers, data intervals, dependencies, state, and failure modes.
4. Attempt the implementation or architecture yourself.
5. Compare your answer with the **Solution**.
6. Explain aloud why the solution is safe in production.
7. Revisit the relevant Topic 01–11 material when you miss an important concept.

## Learning Rules

- Treat the orchestrator as a coordination system, not a heavy data-processing engine.
- Assume retries can happen and design side effects accordingly.
- Make data intervals explicit for scheduled and historical processing.
- Bound concurrency according to real resource limits.
- Treat failure behavior as part of the workflow contract.
- Use XCom/results for small metadata and references, not datasets.
- Protect current production workloads during backfills.
- Make quality gates actual dependencies of publication.
- Test orchestration code before deployment.
- Validate that expected workflows still exist after deployment.

---

# Part I — Basic

## Question 1 — Design a Simple Daily Orders DAG

**Difficulty:** Basic

**Topics Covered:**
- Topic 01 — DAGs, dependencies, and scheduling concepts

**Concepts Tested:**
- DAG, task, dependency, topological execution, schedule

### Problem

You need a daily `orders_daily` workflow with four steps: extract orders, transform them, run a quality check, and publish the result. The quality check must finish before publication. Describe the DAG and its dependency graph.

### Solution

Model each meaningful operation as a task and connect them according to the required ordering:

```text
extract
   ↓
transform
   ↓
quality_check
   ↓
publish
```

A conceptual Airflow TaskFlow implementation is:

```python
from airflow.decorators import dag, task
from pendulum import datetime

@dag(
    dag_id="orders_daily",
    start_date=datetime(2026, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
)
def orders_daily():

    @task
    def extract():
        return ["o1", "o2"]

    @task
    def transform(rows):
        return [row.upper() for row in rows]

    @task
    def quality_check(rows):
        assert rows
        return rows

    @task
    def publish(rows):
        print(f"Publishing {rows}")

    rows = extract()
    transformed = transform(rows)
    checked = quality_check(transformed)
    publish(checked)

dag = orders_daily()
```

The important point is that dependencies are represented by data/task relationships, not by the order in which functions happen to appear in the source file.

### Explanation

A DAG is a directed acyclic graph. Airflow determines runnable tasks from dependencies and task state; it does not simply execute the file from top to bottom. This graph permits topological execution while preventing `publish` from running before `quality_check`. In production, the extraction and transformation functions would normally be thin orchestration wrappers around independently testable business logic.

---

## Question 2 — Explain Fan-Out and Fan-In

**Difficulty:** Basic

**Topics Covered:**
- Topic 01 — DAGs, dependencies, and scheduling concepts

**Concepts Tested:**
- fan-out, fan-in, dependencies, parallel execution

### Problem

A workflow downloads customer, order, and payment data independently. After all three are available, one validation task must run. Draw the dependency pattern and explain why the three downloads can be concurrent.

### Solution

Use fan-out followed by fan-in:

```text
customer_extract ─┐
order_extract    ─┼──→ validate
payment_extract  ─┘
```

There is no dependency between the three extraction tasks, so the orchestrator can schedule them independently when execution capacity permits.

The validation task has all three tasks as upstream dependencies. Therefore it becomes runnable only after all required upstream tasks reach states that satisfy its trigger rule.

A conceptual TaskFlow structure is:

```python
customers = extract_customers()
orders = extract_orders()
payments = extract_payments()

validate(customers, orders, payments)
```

The important design decision is not to add artificial dependencies such as:

```text
customers → orders → payments
```

unless the business logic actually requires that order.

### Explanation

Fan-out means one workflow path splits into independent work. Fan-in means independent work converges into a downstream operation. This pattern is useful for independent ingestion sources and is a foundation for concurrency. It also illustrates why task boundaries should represent meaningful dependencies rather than arbitrary sequencing.

---

## Question 3 — Reason About Task States

**Difficulty:** Basic

**Topics Covered:**
- Topic 01 — DAGs, dependencies, and scheduling concepts; Topic 07 — Task retries, deadlines/SLAs, and failure callbacks

**Concepts Tested:**
- task states, upstream failure, retry, downstream scheduling

### Problem

`extract` fails on its first attempt but has a retry configured. `transform` depends on `extract`. What should happen before and after the retry succeeds?

### Solution

Initially:

```text
extract → failed attempt
```

Because `extract` is retryable, the task is not necessarily permanently failed. The orchestrator schedules another attempt according to its retry configuration.

While `extract` is retrying, `transform` should not execute because its required upstream dependency has not successfully completed.

If the retry succeeds:

```text
extract: success
        ↓
transform: runnable
```

If all allowed attempts fail:

```text
extract: terminal failure
        ↓
transform: blocked/not runnable according to dependency and trigger rules
```

The workflow should also emit appropriate operational information such as task logs and failure notifications where configured.

### Explanation

Task state is part of orchestration semantics. A retryable failure is different from a terminal failure. Downstream scheduling depends on upstream state and trigger rules. This is why simply saying 'the task failed' is insufficient when debugging a production workflow: the engineer must ask whether the task is retrying, terminally failed, skipped, deferred, or otherwise in a non-success state.

---

## Question 4 — Interpret a Daily Data Interval

**Difficulty:** Basic

**Topics Covered:**
- Topic 01 — DAGs, dependencies, and scheduling concepts; Topic 08 — Backfills, catch-up, and partitioned runs

**Concepts Tested:**
- data interval, partition, deterministic processing, historical run

### Problem

A daily run has `data_interval_start = 2026-10-01 00:00 UTC` and `data_interval_end = 2026-10-02 00:00 UTC`. Which logical period should the transformation process, and why should it avoid using the current wall-clock time?

### Solution

The intended logical interval is:

```text
[2026-10-01 00:00 UTC,
 2026-10-02 00:00 UTC)
```

That means the transformation should process data belonging to October 1, not whatever data happens to be available at the instant the task starts.

For example:

```sql
SELECT *
FROM orders
WHERE order_ts >= :interval_start
  AND order_ts < :interval_end;
```

Using the data interval makes the same logical run reproducible during:

- normal daily execution;
- reruns;
- historical backfills;
- debugging.

A query such as:

```sql
WHERE order_ts >= NOW() - INTERVAL '24 hours'
```

does not preserve that deterministic historical boundary.

### Explanation

A schedule identifies when a run is created; the data interval identifies the logical data period the run represents. Confusing the two creates subtle backfill and rerun bugs. Interval-based processing is therefore a correctness property, not merely a scheduling detail.

---

## Question 5 — Make a Task Idempotent

**Difficulty:** Basic

**Topics Covered:**
- Topic 01 — DAGs, dependencies, and scheduling concepts; Topic 07 — Task retries, deadlines/SLAs, and failure callbacks

**Concepts Tested:**
- idempotency, retry safety, duplicate writes

### Problem

A task writes the same daily order partition into a warehouse. It succeeds in the database, then crashes before reporting task success. The orchestrator retries it. Explain the defect if the task blindly performs `INSERT` again and propose a safer design.

### Solution

The defect is that the external side effect completed before the orchestrator learned about completion:

```text
write succeeds
   ↓
task crashes
   ↓
retry
   ↓
same write occurs again
```

A blind insert can create duplicates.

A safer design makes the write idempotent. Common approaches include:

1. Use a deterministic partition/key.
2. Write to a staging table and publish atomically.
3. Use an upsert/merge keyed by the business or batch key.
4. Replace the intended partition atomically when the pipeline owns the partition.
5. Use a transaction boundary that matches the intended state transition.

For example, a merge can conceptually enforce:

```text
same order_id + same logical partition
→ update existing row
instead of duplicate insertion
```

Then test:

```text
run once
run again
run after injected post-write failure
```

and verify the final business state is identical.

### Explanation

Retries provide recovery only when the retried operation is safe. The orchestrator cannot make an external database write transactional merely by retrying the task. This is why idempotency is a core orchestration engineering principle.

---

## Question 6 — Explain Why Cron Is Not a Full Orchestrator

**Difficulty:** Basic

**Topics Covered:**
- Topic 02 — Limits of cron and why orchestrators exist

**Concepts Tested:**
- cron, dependencies, retries, observability, historical runs

### Problem

A team currently uses cron entries to run `extract.sh` at 01:00 and `transform.sh` at 02:00. The extract sometimes takes three hours and occasionally fails. Explain two reasons why this design becomes unsafe as workflow complexity grows.

### Solution

First, fixed clock times do not naturally express completion dependencies. `transform.sh` at 02:00 does not mean "run after extract succeeds"; it means "start at 02:00." If extraction takes longer, transformation may overlap or consume incomplete data.

Second, cron by itself does not provide the workflow-level semantics expected from an orchestrator, such as:

- task state tracking;
- dependency-aware scheduling;
- retries with explicit policy;
- centralized operational visibility;
- historical run/backfill management;
- structured failure handling;
- richer concurrency controls.

A small independent script may still be perfectly appropriate for a simple recurring job. The problem arises when the workflow needs coordination and state.

### Explanation

Cron is a scheduler, not a complete workflow-management system. The correct engineering response is not 'cron is always bad'; it is to evaluate whether the workflow's coordination, recovery, visibility, and historical-processing requirements exceed what cron provides.

---

## Question 7 — Identify the Main Airflow Components

**Difficulty:** Basic

**Topics Covered:**
- Topic 03 — Apache Airflow architecture

**Concepts Tested:**
- scheduler, DAG processor, API server, triggerer, executor, workers, metadata database

### Problem

During a production incident, an engineer says: 'The scheduler, worker, API server, and metadata database are all the same thing.' Correct the statement and describe the responsibility of each major Airflow component at a high level.

### Solution

They are separate logical responsibilities.

- **DAG processor:** parses DAG definitions and makes workflow definitions available to the Airflow system.
- **Scheduler:** determines which task instances should be scheduled based on DAG structure, schedules, dependencies, and state.
- **API server:** provides the API/UI-facing application layer through which users and systems interact with Airflow.
- **Executor:** determines how scheduled task execution is handed off to the configured execution environment.
- **Workers:** execute task workloads when the chosen execution architecture uses workers.
- **Triggerer:** handles deferred/deferrable waiting work efficiently.
- **Metadata database:** stores Airflow's operational metadata and state needed by the platform.

The exact deployment topology varies, but these responsibilities should not be mentally collapsed into one process.

### Explanation

Understanding component boundaries is essential for debugging. A DAG can parse correctly while scheduling is unhealthy, or scheduling can work while workers cannot execute tasks. Component-level reasoning prevents engineers from treating every failure as 'the DAG is broken.'

---

## Question 8 — Write a Basic TaskFlow DAG

**Difficulty:** Basic

**Topics Covered:**
- Topic 04 — Airflow DAGs, operators, and TaskFlow API

**Concepts Tested:**
- TaskFlow API, @task, task dependency, Python task

### Problem

Write a small Airflow 3.x-oriented TaskFlow DAG with `extract_numbers`, `double_numbers`, and `publish`. The second task must receive the first task's result.

### Solution

A concise TaskFlow pattern is:

```python
from airflow.decorators import dag, task
from pendulum import datetime

@dag(
    dag_id="numbers_daily",
    start_date=datetime(2026, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
)
def numbers_daily():

    @task
    def extract_numbers() -> list[int]:
        return [1, 2, 3]

    @task
    def double_numbers(numbers: list[int]) -> list[int]:
        return [number * 2 for number in numbers]

    @task
    def publish(numbers: list[int]) -> None:
        print(numbers)

    numbers = extract_numbers()
    doubled = double_numbers(numbers)
    publish(doubled)

dag = numbers_daily()
```

The function invocation creates the dependency relationships rather than immediately performing the whole pipeline during DAG parsing.

### Explanation

TaskFlow provides a Python-native way to define tasks and dependencies. The key lesson is that orchestration code should remain thin and that returned values crossing task boundaries have operational implications. In production, large datasets should not be pushed through XCom merely because TaskFlow makes value passing syntactically convenient.

---

## Question 9 — Choose a Safe XCom Boundary

**Difficulty:** Basic

**Topics Covered:**
- Topic 05 — Connections, variables, hooks, and XComs

**Concepts Tested:**
- XCom, references, metadata, large datasets, secrets

### Problem

An engineer wants to place a 4 GB Pandas DataFrame into XCom so that the downstream task can read it. Explain why this is a poor design and give a better boundary.

### Solution

Do not use XCom as a transport mechanism for a multi-gigabyte dataset.

A better design is:

```text
extract task
   ↓
write dataset to object storage / database
   ↓
return small reference
   ↓
XCom carries:
  - object URI
  - partition
  - batch ID
  - row count
```

For example:

```python
return {
    "uri": "s3://bucket/orders/date=2026-10-01/",
    "row_count": 1250000,
}
```

The downstream task receives the reference and reads the actual dataset from the durable data system.

Never place secrets into XCom merely because it is convenient. Credentials should use the appropriate connection/secret mechanism.

### Explanation

XCom is intended for small task-to-task metadata and references, not bulk data transport. Keeping datasets in durable data systems separates orchestration metadata from data storage and avoids excessive metadata-database load.

---

## Question 10 — Build a Basic Sensor Decision

**Difficulty:** Basic

**Topics Covered:**
- Topic 06 — Sensors, deferrable operators, and data-aware scheduling

**Concepts Tested:**
- sensor, waiting, worker capacity, deferrable operator

### Problem

A DAG waits for a partner SFTP file that may arrive anywhere from 5 minutes to 4 hours after the workflow begins. Explain why a long-running traditional sensor can be inefficient and when a deferrable operator is useful.

### Solution

A traditional sensor that occupies worker execution capacity while repeatedly waiting can consume a worker slot for hours.

A deferrable operator can move the waiting state to the Triggerer when the operator supports deferral. Conceptually:

```text
task starts
   ↓
condition not ready
   ↓
defer
   ↓
Triggerer waits efficiently
   ↓
condition becomes true
   ↓
task resumes
```

This is particularly useful for long waits where the task is not performing useful compute.

The choice should also consider the trigger mechanism and service behavior. A short, cheap wait may not justify additional complexity.

### Explanation

The principle is to distinguish active work from waiting. Deferrable execution prevents long waits from unnecessarily consuming ordinary worker capacity. It is an orchestration/resource-management decision rather than merely a different syntax for a sensor.

---

# Part II — Moderate

## Question 11 — Choose Task Granularity for an Ingestion Pipeline

**Difficulty:** Moderate

**Topics Covered:**
- Topic 01 — DAGs, dependencies, and scheduling concepts; Topic 04 — Airflow DAGs, operators, and TaskFlow API

**Concepts Tested:**
- task granularity, observability, retries, failure isolation

### Problem

A developer creates one giant `run_everything()` task containing API ingestion, validation, transformation, warehouse loading, and publishing. Another developer creates 70 tiny tasks for every individual Python statement. Evaluate both designs and propose a reasonable middle ground.

### Solution

The giant task has poor orchestration visibility and failure isolation. If the warehouse load fails, the orchestrator sees one large task rather than distinct stages. Retrying the whole task can repeat successful work unnecessarily.

The 70-task design creates excessive orchestration overhead and makes the DAG difficult to understand and operate.

A reasonable boundary is around meaningful operational units:

```text
extract
   ↓
raw_write
   ↓
validate
   ↓
transform
   ↓
load
   ↓
quality_gate
   ↓
publish
```

Each task should have a meaningful responsibility, observable outcome, sensible retry behavior, and appropriate resource profile.

The exact number of tasks depends on workload and operational needs.

### Explanation

Task granularity is an engineering trade-off. Tasks should be large enough to represent useful work but small enough to provide meaningful failure isolation, retries, observability, and operational control. The orchestrator coordinates; heavy computation belongs in the execution layer.

---

## Question 12 — Cron or Orchestrator?

**Difficulty:** Moderate

**Topics Covered:**
- Topic 02 — Limits of cron and why orchestrators exist; Topic 01 — DAGs, dependencies, and scheduling concepts

**Concepts Tested:**
- cron limitations, dependency management, retries, observability, complexity

### Problem

A small script copies one local file to another directory every night and has no dependencies, no historical processing requirement, and no external service. Another workflow has eight dependent tasks, retries, quality gates, and historical backfills. Which coordination approach is appropriate for each and why?

### Solution

For the first workload, cron may be sufficient:

```text
one simple recurring action
+
minimal operational state
+
no dependency graph
```

Introducing a full orchestrator could add unnecessary operational complexity.

For the second workload, an orchestrator is appropriate because the workflow requires:

- dependency-aware execution;
- task state;
- retries;
- quality gates;
- historical processing;
- operational visibility.

The decision should therefore be based on workflow requirements, not a blanket rule that one tool is always better.

### Explanation

Cron remains useful for simple scheduling. An orchestrator becomes valuable when coordination, state, failure handling, backfills, and visibility become first-class requirements.

---

## Question 13 — Trace an Airflow Run Through the Architecture

**Difficulty:** Moderate

**Topics Covered:**
- Topic 03 — Apache Airflow architecture

**Concepts Tested:**
- DAG parsing, scheduler, API server, executor, worker, metadata database

### Problem

A new DAG file is committed and deployed. Explain the high-level path from the Python file becoming available to an actual task executing on a worker.

### Solution

A simplified path is:

```text
DAG source file
    ↓
DAG processor parses it
    ↓
DAG definition becomes available
    ↓
Scheduler evaluates schedule/dependencies/state
    ↓
Scheduler creates/schedules runnable task work
    ↓
Executor hands execution to the configured execution environment
    ↓
Worker executes the task where applicable
    ↓
Task state/log information is recorded
    ↓
Metadata database supports operational state
```

The API server provides the user/system interaction layer for inspecting and controlling the Airflow environment.

The Triggerer participates when deferred/deferrable work is used.

### Explanation

The purpose of this mental model is debugging. A failure to see a DAG is different from a scheduler problem, which is different from a worker problem. Each stage has a distinct responsibility.

---

## Question 14 — Design Dynamic Mapping for Partner Files

**Difficulty:** Moderate

**Topics Covered:**
- Topic 04 — Airflow DAGs, operators, and TaskFlow API

**Concepts Tested:**
- dynamic task mapping, fan-out, bounded concurrency, partial failure

### Problem

A daily run receives a list of 50 partner files. Each file can be processed independently. Explain how dynamic task mapping can represent this workload and identify two production concerns you must address.

### Solution

Dynamic task mapping can create one mapped task instance per input:

```text
file list
   ↓
process.expand(file=files)
   ↓
50 mapped task instances
```

A conceptual TaskFlow pattern is:

```python
from airflow.decorators import task

@task
def list_files() -> list[str]:
    return ["file-1", "file-2", "file-3"]

@task
def process_file(file_name: str) -> None:
    print(file_name)

files = list_files()
process_file.expand(file_name=files)
```

Two important production concerns are:

1. **Concurrency/resource control.** Fifty logical files should not automatically mean fifty simultaneous expensive external requests. Use appropriate pools or other controls.
2. **Partial failures/idempotency.** Some mapped items may fail while others succeed. Retrying a failed item must not duplicate successful external side effects.

### Explanation

Dynamic mapping expresses data-dependent fan-out without hard-coding every task. It is powerful, but mapping can amplify load dramatically. The orchestration design must therefore pair dynamic work with bounded concurrency and safe retry semantics.

---

## Question 15 — Use Task Groups Without Hiding the Contract

**Difficulty:** Moderate

**Topics Covered:**
- Topic 04 — Airflow DAGs, operators, and TaskFlow API

**Concepts Tested:**
- task groups, readability, dependencies, orchestration boundaries

### Problem

A DAG contains three logical stages: ingestion, validation, and publication. Each stage has several tasks. Explain when task groups help and what they must not be used to hide.

### Solution

Task groups can organize related tasks visually and conceptually:

```text
[ingestion]
   ├── source_a
   ├── source_b
   └── source_c

[validation]
   ├── schema
   └── quality

[publication]
   ├── warehouse
   └── notification
```

They improve readability when the grouping represents a meaningful domain or workflow boundary.

They should not hide critical dependencies or make the graph impossible to reason about. For example, the important contract:

```text
validation.quality → publication.warehouse
```

must remain understandable.

The group should also not become a substitute for sensible task design.

### Explanation

Task groups are an organization mechanism, not a correctness mechanism. They help humans understand large DAGs while the actual dependency graph remains explicit.

---

## Question 16 — Choose a Trigger Rule for a Branching Workflow

**Difficulty:** Moderate

**Topics Covered:**
- Topic 04 — Airflow DAGs, operators, and TaskFlow API

**Concepts Tested:**
- branching, trigger rules, skipped state

### Problem

A workflow branches into `process_orders` or `process_refunds`. After the branch, a final `audit` task should run whether either branch completes, but should not run if the entire workflow has failed unexpectedly. Explain why the default all-success dependency may not fit and what you would investigate.

### Solution

Branching intentionally causes some downstream tasks to be skipped. Therefore a downstream task that expects every upstream branch to be successful may not behave as intended.

The engineer should inspect the applicable Airflow trigger-rule semantics and choose a rule that matches the contract, for example one that permits the expected skipped branch while still requiring an acceptable successful path.

The design should explicitly document:

```text
branch
  ├── orders
  └── refunds
       ↓
      audit
```

The test suite should exercise both branch choices and verify that `audit` behaves correctly in each case.

### Explanation

Trigger rules are part of orchestration semantics. Branching introduces skipped states, so downstream behavior must be designed rather than assumed. The correct rule depends on the desired failure contract.

---

## Question 17 — Control Concurrent Warehouse Loads with Pools

**Difficulty:** Moderate

**Topics Covered:**
- Topic 04 — Airflow DAGs, operators, and TaskFlow API; Topic 06 — Sensors, deferrable operators, and data-aware scheduling

**Concepts Tested:**
- pools, bounded concurrency, external rate limits

### Problem

Twenty DAGs can simultaneously call a warehouse that safely supports only five concurrent heavy loads. Explain how a pool can help and why simply adding more workers is not a sufficient solution.

### Solution

Create a pool representing the constrained resource, with five available slots, and assign the heavy-load tasks to that pool.

Conceptually:

```text
20 tasks want warehouse access
            ↓
      warehouse_pool
       5 available slots
            ↓
5 execute concurrently
remaining tasks wait
```

This is different from increasing worker capacity. More workers can increase the number of simultaneous calls, potentially making the warehouse overload worse.

The pool encodes a resource constraint at the orchestration layer.

### Explanation

Concurrency should be bounded according to the constrained external resource, not simply according to how much compute the orchestration platform can provide. Pools make an external capacity limit explicit.

---

## Question 18 — Separate Connections, Variables, Hooks, and XCom

**Difficulty:** Moderate

**Topics Covered:**
- Topic 05 — Airflow connections, variables, hooks, and XComs

**Concepts Tested:**
- connections, variables, hooks, XCom, secrets

### Problem

For an API ingestion task, decide where you would put: API credentials, a non-secret environment setting, reusable API-client interaction logic, and a small returned batch ID.

### Solution

Use the abstractions according to their purpose:

- **API credentials:** Connections/secrets mechanism, not source code or ordinary variables.
- **Non-secret environment setting:** Variables or environment-specific configuration, depending on the platform convention.
- **Reusable API interaction logic:** A hook or ordinary Python client abstraction.
- **Small returned batch ID:** XCom is appropriate.

Conceptually:

```text
secret credential → Connection/secret management
configuration      → Variable/config
external access   → Hook/client
small metadata    → XCom
```

Never put passwords or tokens into XCom just because downstream tasks can access them.

### Explanation

These mechanisms solve different problems. Connections represent external-system credentials/configuration, hooks encapsulate external interactions, variables hold configuration, and XCom carries small task-to-task metadata. Separating them improves security and maintainability.

---

## Question 19 — Design a Data-Aware Waiting Workflow

**Difficulty:** Moderate

**Topics Covered:**
- Topic 06 — Sensors, deferrable operators, and data-aware scheduling

**Concepts Tested:**
- data-aware scheduling, assets, asset events, sensors, deferrable operators

### Problem

A downstream transformation should run when an upstream dataset becomes available rather than blindly running at a fixed clock time. Explain the difference between a fixed schedule and data-aware/event-driven coordination, and identify where sensors or deferrable waiting may still fit.

### Solution

A fixed schedule says:

```text
run at 06:00
```

A data-aware/event-driven design says conceptually:

```text
required data becomes available
        ↓
downstream workflow becomes eligible
```

This better represents readiness when the true trigger is data availability rather than time.

A sensor may still be appropriate when the system must actively wait for a condition that does not expose a direct event/data-aware mechanism. If the wait is long, a deferrable operator can move the waiting state to the Triggerer rather than consuming ordinary worker capacity.

### Explanation

Scheduling should express the actual business trigger. Data-aware orchestration reduces the mismatch between 'the clock says run' and 'the required data is ready.' Sensors remain useful for external readiness conditions, while deferrable execution improves resource efficiency during long waits.

---

## Question 20 — Configure Retry and Timeout Policy

**Difficulty:** Moderate

**Topics Covered:**
- Topic 07 — Task retries, deadlines/SLAs, and failure callbacks

**Concepts Tested:**
- retry count, retry delay, backoff, timeout, retryable vs permanent failure

### Problem

An API task normally fails temporarily with HTTP 503 but should not retry authentication failures. It also must not run longer than 15 minutes. Design the policy and explain how exponential backoff helps.

### Solution

The policy should distinguish transient and permanent failures.

For transient 503 failures:

```text
attempt
 ↓
retry after delay
 ↓
retry with increasing delay/backoff
```

For authentication failures such as a persistent 401:

```text
fail fast / classify as non-retryable
```

Also configure a 15-minute execution timeout.

A conceptual policy is:

```text
retries: bounded
retry delay: explicit
backoff: exponential where appropriate
timeout: 15 minutes
non-retryable authentication errors: no retry
```

The exact operator/API configuration should follow the Airflow 3.x implementation being used.

### Explanation

Retries should target transient failures, not every failure. Exponential backoff reduces pressure on a struggling dependency. A timeout prevents a hung operation from consuming resources indefinitely. Retry configuration must also be paired with idempotency when external side effects exist.

---

# Part III — Hard

## Question 21 — Plan a Controlled Historical Backfill

**Difficulty:** Hard

**Topics Covered:**
- Topic 08 — Backfills, catch-up, and partitioned runs

**Concepts Tested:**
- catch-up, backfill, partitions, load control, historical processing

### Problem

A daily orders DAG has been disabled for 30 days. The team now needs the missing historical partitions, but today's 07:00 workload must remain healthy. Design a safe backfill approach.

### Solution

Treat the historical work as controlled processing rather than simply launching all missing intervals at maximum concurrency.

Plan:

1. Identify the exact missing data intervals.
2. Verify the DAG is deterministic for each interval.
3. Verify writes are idempotent.
4. Limit backfill concurrency so today's workload retains capacity.
5. Process historical intervals in controlled batches.
6. Monitor source, warehouse, and worker load.
7. Retry failed historical intervals independently where possible.
8. Validate output partition-by-partition.
9. Reconcile completed versus failed intervals.
10. Stop or slow the backfill if it threatens current production work.

Use pools or other resource controls where appropriate.

### Explanation

Backfill load is a production capacity problem as well as a data-correctness problem. A successful historical run that overwhelms today's SLA is still an operational failure.

---

## Question 22 — Design a Dagster Partitioned Asset

**Difficulty:** Hard

**Topics Covered:**
- Topic 09 — Dagster software-defined assets

**Concepts Tested:**
- software-defined assets, partitions, resources, asset checks

### Problem

You need a daily `orders_clean` asset partitioned by date. It reads raw orders and must pass a quality check before being considered usable. Describe the asset design and the role of resources and asset checks.

### Solution

Model the data product as a partitioned software-defined asset:

```text
raw_orders
    ↓
orders_clean[date partition]
    ↓
asset check
```

The partition definition identifies the logical daily slices.

A resource can provide an external dependency such as:

- database access;
- object storage;
- API client.

The asset logic should use that resource rather than hard-coding infrastructure details.

An asset check can validate properties such as:

```text
row count > 0
required columns exist
duplicate rate acceptable
```

The check should have clear semantics about whether downstream consumption is allowed or whether the asset should be considered invalid.

### Explanation

Dagster's asset-centric model emphasizes data products and their dependencies. Partitions make historical slices explicit, resources separate infrastructure from asset logic, and asset checks make data correctness part of the asset workflow.

---

## Question 23 — Implement a Small Prefect Flow

**Difficulty:** Hard

**Topics Covered:**
- Topic 10 — Prefect flows and tasks

**Concepts Tested:**
- flow, task, parameters, retries, states

### Problem

Create a Prefect 3-style flow that accepts a `source_name`, calls a task to fetch records, then validates the records. The fetch task should have bounded retries.

### Solution

A conceptual Prefect 3 pattern is:

```python
from prefect import flow, task

@task(retries=3, retry_delay_seconds=30)
def fetch_records(source_name: str) -> list[dict]:
    # Call the source here.
    return [{"source": source_name, "id": 1}]

@task
def validate_records(records: list[dict]) -> list[dict]:
    if not records:
        raise ValueError("No records returned")
    return records

@flow
def ingest_source(source_name: str):
    records = fetch_records(source_name)
    validate_records(records)

if __name__ == "__main__":
    ingest_source("orders-api")
```

Exact configuration options should be verified against the installed Prefect 3 version.

### Explanation

The flow defines orchestration boundaries while tasks encapsulate retryable units of work. Parameters make the flow reusable. The retry belongs on the transient external operation rather than automatically surrounding every operation.

---

## Question 24 — Debug a DAG with an Incorrect Dependency

**Difficulty:** Hard

**Topics Covered:**
- Topic 04 — Airflow DAGs, operators, and TaskFlow API; Topic 11 — Testing and validating DAGs

**Concepts Tested:**
- structure testing, quality gates, dependencies, debugging

### Problem

The intended graph is `extract → transform → quality_gate → publish`, but a code review discovers that `publish` depends only on `transform`. The quality gate still runs. Identify the defect, provide the structural test that should catch it, and explain why executing the DAG once might not reveal the problem immediately.

### Solution

The defect is that `quality_gate` is not a prerequisite for `publish`.

A structure test should assert the critical dependency:

```python
def test_quality_gate_blocks_publish():
    dag = build_orders_dag()

    quality = dag.get_task("quality_gate")
    publish = dag.get_task("publish")

    assert quality.task_id in publish.upstream_task_ids
```

The correct graph is:

```text
extract
   ↓
transform
   ↓
quality_gate
   ↓
publish
```

A one-time execution may appear successful if the quality check happens to pass. The graph is still unsafe because a future quality failure could occur after `publish` has already been allowed to run.

A behavioral test should additionally inject a quality failure and verify that publication does not occur.

### Explanation

This is a classic example of why orchestration testing must validate structure, not merely successful execution. A quality gate is meaningful only if its state participates in the dependency contract that controls publication.

---

## Question 25 — Diagnose a DAG Parsing Failure

**Difficulty:** Hard

**Topics Covered:**
- Topic 03 — Apache Airflow architecture; Topic 11 — Testing and validating DAGs

**Concepts Tested:**
- DAG parsing, import tests, parse-time side effects, deployment

### Problem

After deployment, `orders_daily` disappears from the Airflow UI. The code contains a top-level API request that retrieves configuration before the DAG object is created. Explain the likely failure mode and the testing strategy that should prevent it.

### Solution

The top-level request executes during DAG parsing/import. If the API is unavailable, slow, or returns an unexpected response, importing the module can fail or exceed the acceptable parse-time budget.

Move the external request into runtime task code or another controlled execution boundary.

Testing should include:

1. **Static/code review:** detect network/database calls at module scope.
2. **Import test:** import every DAG in CI.
3. **Parse-time budget:** measure import duration where appropriate.
4. **Deployment validation:** verify that the expected DAG ID appears after deployment.
5. **DAG inventory check:** compare expected and loaded DAG IDs.

This creates multiple layers of protection.

### Explanation

A missing DAG can be a deployment-level failure even when the source commit looks valid. Import-time side effects are especially dangerous because they couple scheduler/DAG processing to external systems.

---

## Question 26 — Debug an XCom Data Explosion

**Difficulty:** Hard

**Topics Covered:**
- Topic 05 — Connections, variables, hooks, and XComs; Topic 11 — Testing and validating DAGs

**Concepts Tested:**
- XCom boundaries, metadata database, data references, testing

### Problem

A mapped ingestion workflow returns large Python lists from every mapped task through XCom. The metadata database is growing rapidly. Explain the architectural defect and redesign the boundary.

### Solution

The defect is treating XCom as a data transport system.

Redesign:

```text
mapped ingestion task
      ↓
write dataset to durable object/database storage
      ↓
return small metadata
```

For example:

```python
return {
    "uri": "s3://raw/orders/source=A/date=2026-10-01/",
    "partition": "2026-10-01",
    "row_count": 250000,
}
```

The downstream task reads the dataset from its durable store.

Testing should include a policy/structure check or code review rule that prevents oversized payloads from becoming normal orchestration state. Integration tests should validate that the reference points to accessible data.

### Explanation

XCom is operational metadata, not a replacement for a database or object store. Dynamic mapping multiplies the impact of a poor boundary, so a small per-task payload can become a large metadata problem at scale.

---

## Question 27 — Prevent a Retry Storm

**Difficulty:** Hard

**Topics Covered:**
- Topic 07 — Task retries, deadlines/SLAs, and failure callbacks; Topic 04 — Airflow DAGs, operators, and TaskFlow API

**Concepts Tested:**
- retry storm, exponential backoff, concurrency, failure classification

### Problem

An upstream API is down. Two hundred mapped tasks all fail simultaneously and immediately retry three times. The API becomes even more overloaded. Design a safer retry strategy.

### Solution

First classify the failure as transient but dependency-wide. Then avoid synchronized retries.

Use:

- bounded retry counts;
- retry delays;
- exponential backoff;
- appropriate jitter where supported/implemented;
- concurrency limits/pools;
- sensible timeouts;
- alerts after retry exhaustion.

Conceptually:

```text
200 failures
   ↓
bounded concurrency
   ↓
staggered retries
   ↓
dependency receives controlled load
```

Also consider whether every mapped item should independently retry while the upstream dependency is known to be unavailable. Observability should expose the failure pattern quickly.

The goal is not maximum retry count. The goal is controlled recovery without amplifying the incident.

### Explanation

Retries are a load-management problem as well as a reliability feature. Without backoff and bounded concurrency, an orchestrator can turn a transient dependency failure into a retry storm.

---

## Question 28 — Analyze a Mapped Partial Failure

**Difficulty:** Hard

**Topics Covered:**
- Topic 04 — Airflow DAGs, operators, and TaskFlow API; Topic 07 — Task retries, deadlines/SLAs, and failure callbacks; Topic 11 — Testing and validating DAGs

**Concepts Tested:**
- dynamic mapping, partial failure, retries, idempotency, observability

### Problem

A mapped task processes 100 partner files. Ninety-five succeed, five fail because of transient storage errors. Explain what the engineering team should preserve, what should be retried, and what must be tested.

### Solution

The successful mapped items should not be unnecessarily reprocessed merely because five items failed.

The design should:

1. Identify failed mapped instances individually.
2. Retry transient failures with bounded policy.
3. Preserve successful results.
4. Ensure each item is idempotent so a retry is safe.
5. Record enough metadata to identify failed inputs.
6. Alert if failures remain after retries.
7. Validate the final workflow contract before publication.

Tests should cover:

```text
100 inputs
→ 95 success
→ 5 transient failures
→ retries
→ 5 recover
→ no duplicate writes for 95
```

Also test the permanent-failure case where one or more items remain failed.

### Explanation

Dynamic work changes the failure model from one task result to many logical task instances. Production systems must reason about partial completion, targeted recovery, and the downstream consequences of incomplete work.

---

## Question 29 — Choose Between a Sensor and a Deferrable Operator

**Difficulty:** Hard

**Topics Covered:**
- Topic 06 — Sensors, deferrable operators, and data-aware scheduling

**Concepts Tested:**
- sensor modes, deferral, Triggerer, worker capacity

### Problem

A file arrival may take up to six hours. The current sensor occupies a worker while waiting. Explain the resource problem and redesign the waiting pattern.

### Solution

The current pattern consumes worker capacity while the task is mostly idle.

Use a deferrable operator/sensor where the applicable Airflow implementation supports the required condition:

```text
worker
  ↓
start waiting
  ↓
defer
  ↓
Triggerer monitors condition
  ↓
condition met
  ↓
worker resumes task
```

Also evaluate whether the source can provide an event/data-aware trigger. If it can, event/data-aware orchestration may be preferable to repeated polling.

The test strategy should verify:

- the condition is detected;
- the task resumes correctly;
- timeout behavior is defined;
- failure behavior is observable.

### Explanation

Deferral separates waiting from active worker execution. The Triggerer is designed to support this pattern. The correct solution depends on whether the source offers a suitable event mechanism and how much operational complexity is justified.

---

## Question 30 — Design a Logic-Change Backfill

**Difficulty:** Hard

**Topics Covered:**
- Topic 08 — Backfills, catch-up, and partitioned runs

**Concepts Tested:**
- logic-change backfill, shadow tables, atomic swap, downstream invalidation

### Problem

A transformation bug caused incorrect gold data for the last 90 days. The corrected logic must be applied without exposing partially rebuilt gold data. Design a safe reprocessing strategy.

### Solution

Do not overwrite production gold partitions blindly while rebuilding.

A safer pattern is:

```text
historical intervals
      ↓
run corrected transformation
      ↓
shadow/staging tables or equivalent isolated outputs
      ↓
validate counts/schema/business rules
      ↓
atomic publish/swap
      ↓
invalidate or refresh affected downstream data
```

Control the backfill's concurrency so it does not starve today's production processing.

Track each interval:

```text
pending
running
validated
published
failed
```

If a partition fails validation, do not publish that partition.

The final swap should make the corrected dataset visible atomically according to the warehouse/storage capabilities.

### Explanation

Logic-change backfills are riskier than ordinary reruns because the computation itself has changed. Shadow outputs separate computation from publication and provide a validation boundary before replacing trusted data.

---

# Part IV — Advanced

## Question 31 — Protect Today's SLA During a Large Backfill

**Difficulty:** Advanced

**Topics Covered:**
- Topic 08 — Backfills, catch-up, and partitioned runs; Topic 07 — Task retries, deadlines/SLAs, and failure callbacks; Topic 04 — Airflow DAGs, operators, and TaskFlow API

**Concepts Tested:**
- backfill load control, pools, deadlines, concurrency, priorities

### Problem

A six-month historical backfill requires thousands of partitions while the platform must still finish the daily customer pipeline before 07:00. Design the resource-control strategy.

### Solution

Separate historical capacity from critical daily capacity.

Use controls such as:

- bounded backfill concurrency;
- dedicated or shared pools with reserved capacity;
- priority/resource policies that protect critical daily work;
- controlled batches of historical intervals;
- monitoring of queue depth and runtime;
- explicit stopping criteria if today's workload is threatened.

Conceptually:

```text
Total capacity
├── protected daily capacity
└── controlled backfill capacity
```

Do not simply increase global worker count without considering downstream systems.

Measure:

```text
daily pipeline completion time
backfill throughput
warehouse/API load
queue depth
failure rate
```

Pause or reduce historical processing when it threatens the production deadline.

### Explanation

Backfill load control is part of reliability engineering. The objective is not to maximize historical throughput; it is to complete historical work while preserving the service level of current production workloads.

---

## Question 32 — Debug a Prefect Cache That Returns Stale Data

**Difficulty:** Advanced

**Topics Covered:**
- Topic 10 — Prefect flows and tasks; Topic 11 — Testing and validating DAGs

**Concepts Tested:**
- Prefect caching, deterministic inputs, invalidation, changing external data

### Problem

A Prefect task fetches today's API response. It is cached using only `source_name`, so yesterday's response is reused today. Diagnose the defect and redesign the cache key/usage.

### Solution

The cache key does not represent all inputs that determine the result.

If the result depends on:

```text
source_name
logical_date
API parameters
```

the caching identity must distinguish those inputs, or caching should be disabled when the external result is intentionally time-varying and freshness is required.

For example, conceptually:

```text
cache identity =
source_name + logical_date + request parameters
```

Test:

```text
run for 2026-10-01
run for 2026-10-02
```

and verify the second run does not incorrectly reuse the first result.

Also test invalidation behavior when upstream data changes.

### Explanation

Caching is a correctness decision, not merely a performance optimization. A cache is valid only when its identity and invalidation semantics match the computation's actual inputs and freshness requirements.

---

## Question 33 — Design Prefect Bounded Concurrency

**Difficulty:** Advanced

**Topics Covered:**
- Topic 10 — Prefect flows and tasks

**Concepts Tested:**
- task runners, futures, submit, mapping, bounded concurrency, external limits

### Problem

A Prefect flow must process 1,000 API requests, but the provider permits only 20 concurrent requests. Explain how you would model the workload and enforce bounded concurrency rather than creating an unbounded request storm.

### Solution

Use task-level parallelism with an explicit concurrency limit appropriate to the provider.

A conceptual pattern is:

```python
from prefect import flow, task

@task
def fetch(item):
    ...

@flow
def pipeline(items):
    futures = [fetch.submit(item) for item in items]
    return [future.result() for future in futures]
```

The exact concurrency mechanism should follow the Prefect 3 task-runner/concurrency facilities used by the deployment.

The design must enforce:

```text
1000 logical requests
        ↓
maximum 20 active requests
```

Also use retries and timeouts carefully. If the provider is already overloaded, retry storms can violate the same limit you are trying to protect.

### Explanation

`.submit()` creates deferred task work represented by futures. Parallelism is not the same as unlimited concurrency. Production orchestration must explicitly respect external rate limits and resource capacity.

---

## Question 34 — Design a Complete Testing Stack for One DAG

**Difficulty:** Advanced

**Topics Covered:**
- Topic 11 — Testing and validating DAGs

**Concepts Tested:**
- static analysis, import tests, unit tests, structure tests, policy tests, integration tests, deployment validation

### Problem

Design the test sequence for an `orders_daily` DAG before production. The DAG contains SQL, templates, quality gates, retries, and PostgreSQL integration.

### Solution

Use a layered pipeline:

```text
Ruff/static
   ↓
unit tests for business logic
   ↓
DAG import tests
   ↓
structure/dependency tests
   ↓
policy tests
   ↓
template/data-interval tests
   ↓
PostgreSQL integration tests
   ↓
deployment validation
```

Specific checks:

- Import every expected DAG.
- Assert required task IDs.
- Assert `quality_gate → publish`.
- Assert owner/tags/retry/timeout/catch-up policy.
- Render templates for fixed intervals.
- Unit-test transformations without Airflow.
- Integration-test SQL against isolated PostgreSQL.
- Inject failures to verify retry/idempotency.
- After deployment, compare expected versus loaded DAG IDs.

Do not make every test a full Airflow execution test.

For local Airflow validation, use the current Airflow 3.x mechanisms covered by the module, including `dag.test()` and the `airflow dags test` CLI. Use `pytest` for Python/unit/structure/policy tests. Integration tests may use isolated Docker services such as PostgreSQL or MinIO. For Prefect, test current mapping behavior and `.map()` only where it is supported by the installed/current Prefect 3 API; do not assume an older API signature.


### Explanation

The layers catch different failure classes. Fast deterministic checks should fail early; real-service and deployment checks should be targeted. The test strategy itself is part of production architecture.

---

## Question 35 — Design a Deadline-Protected Daily Pipeline

**Difficulty:** Advanced

**Topics Covered:**
- Topic 07 — Task retries, deadlines/SLAs, and failure callbacks; Topic 06 — Sensors, deferrable operators, and data-aware scheduling; Topic 01 — DAGs, dependencies, and scheduling concepts

**Concepts Tested:**
- deadline, freshness, timeout, retries, alerts, waiting, dependencies

### Problem

A customer dashboard must be fresh by 07:00. An upstream file can arrive late, transformations can fail transiently, and a warehouse load can hang. Design the orchestration controls needed to protect the deadline.

### Solution

Represent the workflow explicitly:

```text
file readiness
   ↓
ingest
   ↓
transform
   ↓
quality
   ↓
publish
```

Use an appropriate sensor/data-aware readiness mechanism for the file. If the wait is long, use deferrable waiting where supported.

Use:

- task-level timeouts for hung operations;
- bounded retries with backoff for transient failures;
- non-retryable handling for permanent errors;
- deadline/freshness monitoring;
- structured failure callbacks/alerts;
- dependency checks that prevent publication before quality passes.

Monitor:

```text
file arrival time
task durations
retry counts
queue delays
quality completion
publish completion
```

The deadline should produce actionable alerts before or when the freshness contract is breached.

### Explanation

A deadline is not achieved by setting a single timer. The system must control waiting, execution duration, retries, dependencies, and alerting so that the end-to-end freshness contract is observable and enforceable.

---

## Question 36 — Choose an Asset-Centric Boundary

**Difficulty:** Advanced

**Topics Covered:**
- Topic 09 — Dagster software-defined assets; Topic 06 — Sensors, deferrable operators, and data-aware scheduling; Topic 01 — DAGs, dependencies, and scheduling concepts

**Concepts Tested:**
- asset graph, partitions, asset checks, declarative automation, data-aware orchestration

### Problem

A platform has a stable raw-to-clean-to-gold data graph, and downstream consumers care about whether specific data products are fresh and valid. Explain where an asset-centric approach can be valuable and what should remain outside the asset definition.

### Solution

Model durable data products as assets:

```text
raw_orders
    ↓
clean_orders
    ↓
daily_orders_gold
```

Use partitions for logical slices where appropriate. Use resources for external infrastructure and asset checks for data-quality contracts.

Asset-driven/declarative automation can express downstream readiness based on upstream asset state rather than only clock schedules.

Keep heavy computation in the execution layer and keep infrastructure credentials/configuration in resources or appropriate configuration mechanisms.

Testing should validate:

- asset logic;
- dependencies;
- partitions;
- resource behavior;
- asset checks;
- downstream readiness conditions.

### Explanation

Asset-centric orchestration emphasizes the data products and their dependency graph. It can make data readiness and lineage semantics explicit. The choice should be based on the workflow's requirements rather than tool preference.

---

## Question 37 — Design Event-Driven and Scheduled Coordination Together

**Difficulty:** Advanced

**Topics Covered:**
- Topic 01 — DAGs, dependencies, and scheduling concepts; Topic 06 — Sensors, deferrable operators, and data-aware scheduling; Topic 10 — Prefect flows and tasks

**Concepts Tested:**
- schedule, event, automation, data readiness, triggers

### Problem

A pipeline has a normal daily schedule, but a high-priority partner file may arrive early and should trigger processing immediately. Another downstream workflow should run only when the upstream data product is available. Design the trigger strategy without creating duplicate processing.

### Solution

Separate the trigger concepts:

```text
daily schedule
     ↓
normal run

partner file event
     ↓
event-triggered run

upstream asset/data availability
     ↓
downstream eligibility
```

The key is to define a deterministic run identity/data interval and an idempotent processing contract so an event and scheduled trigger cannot create conflicting duplicate writes.

Use event/automation mechanisms where supported by the orchestration tool. For file readiness without an event source, a sensor may be appropriate.

Tests should include:

- scheduled trigger;
- early event trigger;
- duplicate event;
- event plus scheduled overlap;
- correct data interval;
- idempotent rerun.

### Explanation

Combining schedules and events requires explicit semantics. Events answer 'something happened'; schedules answer 'it is time.' The processing layer must remain safe if more than one trigger path requests the same logical work.

---

## Question 38 — Compare Airflow, Dagster, and Prefect for Three Workloads

**Difficulty:** Advanced

**Topics Covered:**
- Topic 03 — Apache Airflow architecture; Topic 09 — Dagster software-defined assets; Topic 10 — Prefect flows and tasks

**Concepts Tested:**
- task-centric orchestration, asset-centric orchestration, Python-native flows, deployment, concurrency, operational trade-offs

### Problem

Evaluate three workloads: (A) a large organization with many scheduled DAGs and established Airflow operations; (B) a data-product platform centered on partitioned assets and asset checks; (C) a Python-heavy workflow needing flexible flow/task orchestration and deployment/work-pool concepts. Explain which model fits each workload and the trade-offs without declaring a universal winner.

### Solution

A reasonable mapping is:

**A — Airflow:** Its scheduler/DAG/task model fits organizations that already operate scheduled workflows, operators, pools, sensors, and established Airflow infrastructure.

**B — Dagster:** Its software-defined asset model, partitions, resources, asset checks, and declarative automation align naturally with a platform organized around data products.

**C — Prefect:** Its Python-native flows/tasks, task submission/mapping, concurrency controls, deployments, work pools/workers, and automations can fit a Python-centric workflow model.

The decision should consider:

- existing platform expertise;
- operational model;
- workflow semantics;
- asset vs task orientation;
- deployment model;
- concurrency requirements;
- observability;
- testing;
- integration ecosystem;
- migration/operational cost.

Do not turn this into a claim that one tool is inherently best.

### Explanation

The tools overlap but emphasize different orchestration abstractions. The correct architectural decision is requirement-driven. A senior engineer should be able to explain why a chosen model fits the workload and what complexity it introduces.

---

## Question 39 — Design a Production Testing Pyramid for Mixed Orchestration

**Difficulty:** Advanced

**Topics Covered:**
- Topic 11 — Testing and validating DAGs; Topic 03 — Apache Airflow architecture; Topic 09 — Dagster software-defined assets; Topic 10 — Prefect flows and tasks

**Concepts Tested:**
- unit tests, import tests, structure tests, policy tests, integration tests, CI, deployment validation

### Problem

A platform contains 100 Airflow DAGs, 20 Dagster assets, and 15 Prefect flows. Design a CI testing strategy that catches broken imports, policy violations, business-logic defects, integration failures, and deployment regressions without executing every workflow end-to-end on every pull request.

### Solution

Use a layered test pyramid:

```text
Static analysis
      ↓
Pure Python unit tests
      ↓
Airflow import tests
Dagster definition/asset tests
Prefect flow/task tests
      ↓
Airflow structure/policy tests
      ↓
Template/data-interval tests
      ↓
Targeted integration tests
      ↓
Build/deployment validation
      ↓
Post-deployment inventory checks
```

Run broad fast checks on every PR. Select integration tests based on affected components and critical contracts. Run broader integration suites on merge/release as appropriate.

For Airflow, import every expected DAG and apply common policy tests. For Dagster, validate asset dependencies, partitions, and checks. For Prefect, test ordinary Python logic plus flow/task boundaries.

After deployment, compare expected workflow inventories with loaded production workflows.

### Explanation

The strategy maximizes early feedback while preserving realistic validation. Different orchestration tools require tool-specific tests, but the overall quality model remains consistent: loadability, structure, policy, logic, integration, and deployment.

---

## Question 40 — End-to-End Platform Orchestration Capstone

**Difficulty:** Advanced

**Topics Covered:**
- Topics 01–11 — complete Module 2.13

**Concepts Tested:**
- workflow boundaries, five-source ingestion, bronze/silver/gold, dbt, Airflow, Dagster, Prefect, retries, backoff, timeouts, non-retryable failures, alerts, 07:00 freshness, SFTP, mapping, pools, deferrable waiting, assets, XCom references, backfills, reprocessing, testing, CI, deployment validation

### Problem

You own `platform_orchestration/`, a production Data Engineering platform with five ingestion sources: three APIs, PostgreSQL, and an SFTP/file source. Data flows through bronze → silver transformations, dbt gold models, and a quality system. Airflow is the primary orchestration platform. A Dagster asset slice owns one asset-driven downstream product, and a Prefect flow handles a Python-heavy enrichment workflow.

Requirements:
- data must be fresh by 07:00;
- APIs have rate limits;
- SFTP arrival is variable;
- ingestion uses dynamic task mapping;
- waiting should not unnecessarily consume worker capacity;
- transient failures retry with backoff;
- permanent failures do not retry indefinitely;
- hung work has timeouts;
- alerts are structured;
- XCom carries references/metadata, not datasets;
- historical backfills must not destroy today's workload;
- reprocessing is parameterized and idempotent;
- quality gates block unsafe publication;
- CI must validate orchestration code;
- deployment must detect missing workflows.

Design the complete orchestration and validation architecture. Explain workflow boundaries, task boundaries, triggers, data intervals, dependencies, Airflow architecture, connections/secrets, XCom, sensors/deferrable waiting, retries, timeouts, deadlines, alerts, backfills, concurrency, quality gates, idempotency, Dagster and Prefect boundaries, testing, CI, deployment validation, and failure recovery.

### Solution

Start with the orchestration contract rather than code.

### 1. Workflow boundary

Use Airflow for the primary cross-system daily coordination:

```text
source readiness
   ↓
mapped ingestion
   ↓
bronze
   ↓
silver
   ↓
quality
   ↓
gold/dbt
   ↓
publish
```

Keep the Dagster slice focused on the data product/asset graph it owns. Keep the Prefect slice focused on the Python-heavy enrichment workload, with a clear boundary for how Airflow coordinates with it.

### 2. Source ingestion

Represent the five sources as independently observable units. Use dynamic mapping when the number of source/file inputs is data-dependent.

For APIs, enforce bounded concurrency with pools/rate limits.

For SFTP, use a readiness sensor or event/data-aware trigger. If waiting is long, use a deferrable implementation so workers are not unnecessarily occupied.

### 3. Data intervals

Define the daily logical interval explicitly:

```text
[day_start, next_day_start)
```

All partition-sensitive SQL and paths use that interval. Parameterized reprocessing accepts an explicit historical interval rather than silently using current time.

### 4. Credentials and XCom

Use Connections/secrets for credentials. Use hooks/client abstractions for external access. XCom contains only:

```text
URI
batch ID
partition
row count
status metadata
```

Large datasets remain in durable storage.

### 5. Reliability

Transient API/storage failures receive bounded retries with backoff. Authentication/configuration errors are classified as non-retryable. External calls have timeouts.

Idempotency is mandatory because a successful external write can be followed by a task crash and retry.

### 6. 07:00 freshness

The freshness contract spans the entire graph. Monitor:

```text
source arrival
ingestion completion
transformation duration
quality completion
gold completion
publish completion
```

Use deadlines/freshness monitoring and structured alerts rather than relying only on individual task failures.

### 7. Quality gates

The graph must enforce:

```text
silver
  ↓
quality_gate
  ↓
gold/publish
```

Tests must prove both dependency ordering and failure behavior.

### 8. Historical processing

For backfills:

```text
identify intervals
→ validate logic
→ controlled execution
→ partition validation
→ safe publication
```

Use bounded capacity so normal daily processing retains protected resources. For logic changes, prefer shadow outputs and an atomic publish/swap strategy where supported.

### 9. Dagster

Use the Dagster asset slice for the data product it owns:

```text
upstream asset
   ↓
partitioned asset
   ↓
asset check
```

Use resources for external dependencies and test asset logic, dependencies, partitions, and checks.

### 10. Prefect

Use a Prefect flow/task boundary for the Python-heavy enrichment:

```text
flow
 ├── task A
 ├── task B
 └── task C
```

Use parameters, bounded concurrency, retries/timeouts, and appropriate deployment/work-pool concepts. Do not duplicate orchestration responsibilities unnecessarily.

### 11. Testing

Build the testing pyramid:

```text
Ruff/static
↓
unit tests
↓
Airflow import tests
↓
DAG structure/policy
↓
templates/data intervals
↓
Dagster asset tests
↓
Prefect flow/task tests
↓
integration tests
↓
deployment validation
```

Inject failures for:

- API 503;
- authentication failure;
- database timeout;
- SFTP absence;
- mapped partial failure;
- quality failure;
- post-write crash;
- worker/execution failure.

### 12. CI

On PR:

```text
static
→ unit
→ imports
→ structure
→ policy
→ templates/intervals
```

Use targeted integration tests and broader suites at appropriate merge/release stages.

### 13. Deployment validation

Maintain expected inventories for Airflow DAGs and other critical workflows. After deployment:

```text
expected IDs
    vs
loaded IDs
```

A missing DAG is a deployment failure even if the deployment mechanism itself reports success.

### 14. Failure recovery

For each incident, determine:

```text
state
external side effect
logical interval
retryability
idempotency
downstream impact
alert status
recovery action
```

Never treat an orchestrator retry as proof that an external operation did not already succeed.

### 15. Production trade-offs

Keep orchestration thin, execution bounded, waiting efficient, side effects idempotent, data intervals deterministic, and quality gates enforceable. Choose Airflow, Dagster, and Prefect boundaries based on the semantics they are responsible for rather than forcing one tool to perform every role.

### Explanation

This capstone integrates the entire module. A production-grade design is not a giant DAG or a giant code listing. It is a set of explicit contracts for scheduling, dependencies, resource limits, failure handling, data correctness, testing, and deployment. The strongest answer explains not only what to build, but why each boundary exists and how it will be validated.

---

# Topic Coverage Matrix

| Topic | Questions |
|---|---|
| Topic 01 — DAGs, dependencies, and scheduling concepts | Q1, Q2, Q3, Q4, Q5, Q11, Q14, Q28, Q31, Q32, Q36, Q40 |
| Topic 02 — Limits of cron and why orchestrators exist | Q6, Q12 |
| Topic 03 — Apache Airflow architecture | Q7, Q13, Q22, Q31, Q35, Q36, Q37, Q40 |
| Topic 04 — Airflow DAGs, operators, and TaskFlow API | Q8, Q11, Q14, Q15, Q16, Q17, Q21, Q24, Q31, Q34, Q40 |
| Topic 05 — Airflow connections, variables, hooks, and XComs | Q9, Q18, Q23, Q31, Q40 |
| Topic 06 — Sensors, deferrable operators, and data-aware scheduling | Q10, Q19, Q25, Q30, Q32, Q36, Q40 |
| Topic 07 — Task retries, deadlines/SLAs, and failure callbacks | Q3, Q5, Q20, Q24, Q26, Q27, Q28, Q29, Q31, Q32, Q33, Q40 |
| Topic 08 — Backfills, catch-up, and partitioned runs | Q4, Q6, Q20, Q21, Q28, Q29, Q31, Q40 |
| Topic 09 — Dagster software-defined assets | Q20, Q22, Q35, Q37, Q40 |
| Topic 10 — Prefect flows and tasks | Q20, Q23, Q28, Q29, Q30, Q35, Q36, Q37, Q40 |
| Topic 11 — Testing and validating DAGs | Q21, Q23, Q24, Q25, Q26, Q28, Q30, Q35, Q37, Q40 |

## Difficulty Coverage

| Difficulty | Questions |
|---|---|
| Basic | Q1–Q10 |
| Moderate | Q11–Q20 |
| Hard | Q21–Q30 |
| Advanced | Q31–Q40 |

## Cross-Topic Coverage Validation

- **2+ topic combinations:** substantially more than 10 questions.
- **3+ topic combinations:** Q3, Q5, Q21, Q22, Q24, Q25, Q26, Q27, Q28, Q29, Q30, Q31–Q40.
- **4+ topic combinations:** Q21, Q24, Q28, Q31, Q32, Q34, Q35, Q36, Q37, Q40.
- **Airflow + testing:** Q21, Q22, Q23, Q24, Q25, Q26, Q28, Q34, Q35, Q40.
- **Dagster + testing:** Q35, Q37, Q40.
- **Prefect + testing:** Q28, Q35, Q37, Q40.
- **Airflow + Dagster + Prefect comparisons:** Q37, Q40.
- **Retries + idempotency:** Q5, Q24, Q26, Q27, Q28, Q31, Q32, Q40.
- **Backfills/data intervals:** Q4, Q20, Q21, Q28, Q31, Q40.
- **Failure/debugging:** Q3, Q21, Q22, Q24, Q25, Q26, Q27, Q28, Q29, Q31, Q32, Q40.
- **Architecture decisions:** Q12, Q13, Q17, Q19, Q30, Q31, Q32, Q34, Q35, Q36, Q37, Q38, Q39, Q40.

## Question-Type Coverage

The set deliberately mixes:

- conceptual reasoning;
- Python/Airflow/Prefect implementation;
- debugging;
- code-review-style reasoning;
- architecture;
- testing;
- production incidents;
- backfill/reprocessing;
- cross-tool comparison;
- configuration and policy decisions.

---

# Final Module Checklist

- [ ] I understand DAGs and dependencies.
- [ ] I understand schedules and data intervals.
- [ ] I understand cron's strengths and limitations.
- [ ] I understand Airflow architecture.
- [ ] I can write Airflow DAGs and reason about TaskFlow.
- [ ] I can reason about mapping, groups, branching, trigger rules, and pools.
- [ ] I can use connections, variables, hooks, and XComs safely.
- [ ] I understand sensors and deferrable operators.
- [ ] I understand data-aware scheduling.
- [ ] I can design retries, backoff, timeouts, deadlines, and failure handling.
- [ ] I can safely perform backfills and parameterized reprocessing.
- [ ] I understand partitioned processing and controlled historical load.
- [ ] I can build and reason about Dagster assets, partitions, resources, and checks.
- [ ] I can reason about Prefect flows, tasks, mapping, concurrency, caching, deployments, and work pools.
- [ ] I can compare Airflow, Dagster, and Prefect according to requirements.
- [ ] I can test orchestration code at multiple layers.
- [ ] I can design CI validation.
- [ ] I can validate deployments and detect disappeared workflows.
- [ ] I can design bounded concurrency and safe reruns.
- [ ] I can design production-grade orchestration.

---

# Practice Completion Rule

Do not judge mastery by the number of questions completed.

A stronger standard is:

```text
Can I explain the design?
        ↓
Can I implement it?
        ↓
Can I break it intentionally?
        ↓
Can I observe the failure?
        ↓
Can I recover safely?
        ↓
Can I test the regression?
        ↓
Can I explain the production trade-off?
```

If you can consistently complete that loop, you are moving from memorizing orchestration concepts toward production Data Engineering capability.
