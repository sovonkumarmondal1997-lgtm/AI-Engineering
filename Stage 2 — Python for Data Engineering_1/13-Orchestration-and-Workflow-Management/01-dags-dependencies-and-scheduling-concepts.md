# DAGs, Dependencies, and Scheduling Concepts

> **Stage 2 — Python for Data Engineering**  
> **Module 2.13 — Orchestration and Workflow Management**  
> **Topic 01**  
> **Level:** Beginner → Advanced / Production Engineering

## Learning Objective

By the end of this topic, you should be able to explain:

> **What an orchestrator actually does, how a workflow is represented as a DAG, how dependencies determine execution order, how scheduling determines when a run should happen, what a run represents, what data interval it covers, how tasks behave under failure and retry, how task granularity affects reliability and scheduler overhead, how concurrency is controlled, and why orchestration must remain separate from heavy computation.**

The objective is deliberately tool-independent. Airflow, Dagster, and Prefect implementation details come later.

---

# 1. From Python Scripts to Orchestrated Workflows

Consider a normal Data Engineering pipeline:

```text
Extract Orders
      ↓
Validate Orders
      ↓
Transform Orders
      ↓
Load Warehouse
      ↓
Run Quality Checks
      ↓
Publish Dataset
```

At small scale, a Python script can execute these steps sequentially.

At production scale, the questions become more difficult:

- What if extraction fails?
- What if validation is still running?
- Which tasks can run concurrently?
- Which tasks must wait?
- What date of data is this run processing?
- What happens when a task fails halfway through?
- Can the failed task be retried safely?
- How many concurrent tasks can the API or database tolerate?
- How can yesterday's failed run be reproduced?
- How can an operator see exactly what failed?

This is where **orchestration** becomes necessary.

The central distinction is:

```text
WHAT must happen?
        ↓
Workflow + Tasks + Dependencies

WHEN should it happen?
        ↓
Schedule / Trigger

WHAT HAPPENED DURING THIS EXECUTION?
        ↓
Run + Task Instances + States
```

An orchestrator coordinates the work. It should generally not become the system performing the heavy computation itself.

---

# 2. Core Vocabulary

| Concept | Meaning |
|---|---|
| Workflow | A defined collection of related work and dependencies |
| Task | A meaningful unit of work |
| Dependency | A relationship that determines execution eligibility/order |
| Run | One execution instance of a workflow |
| Task instance | One task as part of one particular run |
| Orchestration | Coordination of workflow execution |
| Schedule | A time-based rule describing when runs should occur |
| Trigger | An event/action that makes work eligible |
| DAG | Directed Acyclic Graph representing tasks and dependencies |

Do not confuse:

```text
workflow
task
dependency
run
task instance
```

A useful mental model is:

```text
Workflow definition
        ↓
      Run
        ↓
 Task instances
        ↓
Task states
```

---

# 3. What Is a Workflow?

A **workflow** is a defined process describing work, relationships, ordering, and execution behavior.

Example:

```text
Extract
   ↓
Transform
   ↓
Validate
   ↓
Publish
```

A workflow tells the orchestration system:

1. what work exists;
2. which work depends on other work;
3. what can execute independently;
4. what must wait;
5. what constitutes successful progression.

### Workflow vs pipeline

A **pipeline** often emphasizes data movement and transformation.

A **workflow** emphasizes the complete coordination of work.

A Data Engineering pipeline can therefore be represented as a workflow.

---

# 4. What Is a Task?

A **task** is a meaningful unit of work.

Examples:

- execute Python code;
- execute SQL;
- invoke an ingestion CLI;
- run dbt;
- validate a dataset;
- move a file;
- call an external service.

Task boundaries are important because they determine what the orchestration system can observe, retry, schedule, and recover independently.

## One giant task

```text
run_entire_pipeline()
```

Internally:

```text
extract
transform
validate
load
publish
```

If publishing fails after several hours, the entire task may need to be rerun.

## Multiple meaningful tasks

```text
extract
   ↓
transform
   ↓
validate
   ↓
load
   ↓
publish
```

Now the system can isolate failure.

Task boundaries affect:

- retries;
- observability;
- failure isolation;
- parallelism;
- scheduling;
- debugging;
- recovery.

Do not conclude that more tasks are always better. Thousands of tiny tasks can create scheduler and metadata overhead.

---

# 5. What Is a Dependency?

A dependency defines an execution relationship.

Given:

```text
extract_orders
      ↓
transform_orders
```

the arrow means:

> `transform_orders` should not execute until `extract_orders` has successfully completed.

The arrow is not visual decoration. It is an execution rule.

A simple dependency representation is:

```python
dependencies = {
    "extract_orders": [],
    "transform_orders": ["extract_orders"],
    "validate_orders": ["transform_orders"],
    "publish_orders": ["validate_orders"],
}
```

This represents:

```text
extract_orders
      ↓
transform_orders
      ↓
validate_orders
      ↓
publish_orders
```

The graph can exist independently of Airflow, Dagster, or Prefect.

---

# 6. What Is a DAG?

**DAG** means:

> **Directed Acyclic Graph**

Break the term down.

## Directed

Edges have a direction:

```text
A → B
```

is different from:

```text
B → A
```

For orchestration:

```text
Extract → Transform
```

means transformation depends on extraction.

## Acyclic

A DAG cannot contain a cycle.

Valid:

```text
A → B → C
```

Invalid:

```text
A → B → C → A
```

## Graph

A graph consists of nodes and edges.

For orchestration:

```text
nodes = tasks
edges = dependencies
```

Example:

```text
        ┌── Validate Orders ────┐
Extract ┼── Validate Customers ┼── Publish
        └── Validate Products ──┘
```

---

# 7. Why Cycles Are Not Allowed

Consider:

```text
A → B
B → C
C → A
```

Ask:

> Which task can start first?

- `A` waits for `C`.
- `C` waits for `B`.
- `B` waits for `A`.

There is no valid starting point.

Therefore a scheduler cannot derive a valid dependency-respecting execution order.

## Educational cycle detector

```python
def detect_cycle(graph: dict[str, list[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True

        if node in visited:
            return False

        visiting.add(node)

        for dependency in graph.get(node, []):
            if visit(dependency):
                return True

        visiting.remove(node)
        visited.add(node)
        return False

    for node in graph:
        if visit(node):
            return True

    return False
```

The important concept is the distinction between:

```text
currently exploring
```

and:

```text
already completely explored
```

Encountering a node already being explored indicates a cycle.

---

# 8. Topological Ordering

A **topological order** is an ordering in which every dependency occurs before the task that depends on it.

Given:

```text
extract
   ↓
clean
   ↓
transform
   ↓
publish
```

a valid order is:

```text
extract
clean
transform
publish
```

A DAG can have more than one valid order.

Example:

```text
          ┌── validate_orders ──┐
extract ──┤                     ├── publish
          └── validate_customers┘
```

After `extract` succeeds, the two validation tasks are independent.

They may execute in either order or concurrently.

## Educational topological sort

```python
from collections import defaultdict, deque


def topological_sort(
    dependencies: dict[str, list[str]],
) -> list[str]:
    nodes = set(dependencies)

    for deps in dependencies.values():
        nodes.update(deps)

    indegree = {node: 0 for node in nodes}
    dependents: dict[str, list[str]] = defaultdict(list)

    for task, deps in dependencies.items():
        for dependency in deps:
            indegree[task] += 1
            dependents[dependency].append(task)

    ready = deque(
        node
        for node, degree in indegree.items()
        if degree == 0
    )

    order: list[str] = []

    while ready:
        node = ready.popleft()
        order.append(node)

        for dependent in dependents[node]:
            indegree[dependent] -= 1

            if indegree[dependent] == 0:
                ready.append(dependent)

    if len(order) != len(nodes):
        raise ValueError("Dependency graph contains a cycle")

    return order
```

### How it works

1. Calculate the number of prerequisites for every node.
2. Find nodes with zero prerequisites.
3. Put them into the ready queue.
4. Remove a ready node.
5. Conceptually mark it complete.
6. Reduce the prerequisite count of downstream nodes.
7. When a downstream node reaches zero, it becomes ready.
8. If not every node can be processed, a cycle exists.

This is the conceptual foundation of dependency-aware scheduling.

---

# 9. Fan-Out

**Fan-out** occurs when one task enables multiple downstream tasks.

```text
                 ┌── Validate Orders
Extract ─────────┼── Validate Customers
                 └── Update Metrics
```

Data Engineering example:

```text
extract_orders
      ├── validate_orders
      ├── validate_customers
      └── update_metrics
```

Once `extract_orders` succeeds, independent branches may execute concurrently.

Fan-out is therefore a common source of orchestration parallelism.

---

# 10. Fan-In

**Fan-in** occurs when multiple upstream tasks converge into one downstream task.

```text
Extract Orders ────────┐
Extract Customers ─────┼── Build Customer 360
Extract Products ──────┘
```

The downstream task waits for all required dependencies.

This is useful when a final dataset requires multiple independently produced inputs.

---

# 11. Fan-Out + Fan-In

A complete pattern:

```text
                    ┌── Validate Orders ────┐
                    │                       │
Extract ────────────┼── Validate Customers ─┼── Publish
                    │                       │
                    └── Validate Products ──┘
```

Execution:

1. `Extract` executes.
2. After success, the three validations become eligible.
3. The validations can execute independently.
4. `Publish` waits for the required validations.
5. After the fan-in condition is satisfied, `Publish` executes.

---

# 12. Workflow vs Schedule vs Trigger

A workflow answers:

```text
WHAT must happen?
```

A schedule/trigger answers:

```text
WHEN or BECAUSE OF WHAT should it become eligible?
```

Important trigger categories:

1. time-based;
2. event-based;
3. data-aware;
4. manual.

The workflow graph can remain the same while its triggering mechanism changes.

---

# 13. Time-Based Scheduling

Time-based schedules include:

```text
Every hour
Every day at 02:00
Every Monday
Every 15 minutes
```

Two useful conceptual categories are:

### Fixed interval

```text
Every 60 minutes
```

The schedule is based on elapsed intervals.

### Calendar schedule

```text
Every day at 02:00
```

The schedule is tied to calendar time.

These are not identical concepts.

---

# 14. Cron Concepts

The conventional five-field cron structure is:

```text
minute hour day-of-month month day-of-week
```

Example:

```text
0 2 * * *
```

means a daily execution at 02:00 under the standard five-field interpretation.

Another example:

```text
*/15 * * * *
```

means every 15 minutes.

Cron is introduced here only as a foundational scheduling concept.

> **Scope boundary:** Detailed limitations of cron and the decision of when to use cron versus an orchestrator belong to Topic 02.

---

# 15. Event-Based Triggers

Event-based triggers respond to external events.

Examples:

```text
File arrives
Message is published
API event occurs
Upstream workflow finishes
External job completes
```

Compare:

```text
Time-driven:

Run every hour
    ↓
Check whether file exists
```

with:

```text
Event-driven:

File arrives
    ↓
Workflow becomes eligible
```

For example:

```text
partner/orders/2026-10-02.csv
```

may arrive from a partner.

The event can be the actual readiness signal rather than an hourly polling assumption.

---

# 16. Data-Aware Triggers

A data-aware trigger is based on an upstream dataset becoming available or updated.

Example:

```text
Raw Orders
    ↓
Silver Orders
    ↓
Gold Revenue
```

Conceptually:

```text
Silver Orders updated
        ↓
Gold Revenue becomes eligible
```

Compare:

```text
Time-based:
"run at 06:00"
```

with:

```text
Data-aware:
"run when the required upstream dataset is updated"
```

This concept connects to later Airflow asset-aware scheduling and Dagster software-defined assets.

Detailed implementation syntax belongs later.

---

# 17. Manual Runs

Production systems still need manual execution.

Examples:

- emergency rerun;
- historical run;
- debugging;
- recovery;
- backfill;
- testing;
- operational intervention.

A manual run should still respect:

- data interval;
- idempotency;
- dependencies;
- concurrency controls;
- auditability.

Manual execution should not mean uncontrolled execution.

---

# 18. Workflow Runs

A workflow definition is not a workflow run.

Example definition:

```text
orders_daily
```

A particular run may represent:

```text
orders_daily
2026-10-01
```

The definition describes:

```text
what should happen
```

The run represents:

```text
this particular execution
```

Conceptually:

```text
Workflow definition
      ↓
Run A → interval A
Run B → interval B
Run C → interval C
```

---

# 19. Task Instances

A task definition:

```text
extract_orders
```

is not an execution.

A task instance is:

```text
extract_orders
for the 2026-10-01 workflow run
```

Task instances provide a place to reason about:

- state;
- logs;
- start time;
- end time;
- duration;
- retry count;
- failure information.

Example:

```text
Task:
extract_orders

Workflow run:
orders_daily / 2026-10-01

Task instance:
extract_orders / orders_daily / 2026-10-01
```

---

# 20. Task States

The foundational states are:

```text
queued
running
success
failed
up for retry
skipped
upstream failed
```

A simplified lifecycle:

```text
queued
  ↓
running
  ├── success
  ├── failed
  │     ↓
  │  up for retry
  │     ↓
  │  running
  └── skipped
```

An upstream failure can prevent downstream execution:

```text
extract       SUCCESS
transform     FAILED
validate      UPSTREAM_FAILED
publish       UPSTREAM_FAILED
```

The exact state machine varies by orchestrator, but the concepts are common.

---

# 21. Logical Date

A critical concept is:

> **The run date is not necessarily the data date.**

Suppose a daily workflow processes:

```text
2026-10-01
```

data.

The workflow may execute on:

```text
2026-10-02
```

after the data interval closes.

Therefore:

```text
execution time
```

is not automatically:

```text
data being processed
```

The orchestration system needs a logical representation of what the run is responsible for.

---

# 22. Data Interval

A data interval represents the period of data covered by a run.

Example:

```text
data interval

2026-10-01 00:00
        ↓
2026-10-02 00:00
```

Conceptually:

```python
from datetime import datetime

start = datetime(2026, 10, 1, 0, 0)
end = datetime(2026, 10, 2, 0, 0)

print(start)
print(end)
```

Tasks should use explicit interval information rather than silently using:

```python
datetime.now()
```

Using the current clock for historical pipeline logic is dangerous because a historical run can behave differently depending on when it is rerun.

Interval-aware processing supports:

- deterministic processing;
- reproducibility;
- retries;
- partitioning;
- debugging;
- historical execution.

---

# 23. Execution Time vs Logical Date vs Data Interval

| Concept | Meaning |
|---|---|
| Execution time | When the task actually runs |
| Logical date | Which scheduled/run identity the execution represents |
| Data interval | Which period of data the run is responsible for |

Example:

```text
Data interval:
2026-10-01 00:00 → 2026-10-02 00:00

Actual execution:
2026-10-02 02:15
```

These are intentionally different.

This distinction must be understood before framework-specific orchestration.

---

# 24. Task Granularity

Task granularity determines how much work is placed inside one task.

## Too coarse

```text
run_entire_pipeline()
```

Internally:

```text
extract
transform
validate
load
publish
```

Problems:

- poor failure isolation;
- coarse retries;
- difficult debugging;
- poor observability;
- limited parallelism.

## Too fine

```text
thousands of tiny tasks
```

Problems:

- scheduler overhead;
- metadata explosion;
- dependency complexity;
- operational complexity;
- increased orchestration cost.

A useful principle is:

> **A task should represent a meaningful unit of independently observable and recoverable work.**

This is a guideline, not an absolute rule.

---

# 25. Task Granularity Trade-Off

Compare:

### Design A

```text
daily_pipeline
```

### Design B

```text
extract_orders
extract_customers
transform_orders
transform_customers
quality_check
publish
```

Design B can improve:

- failure isolation;
- retries;
- observability;
- parallelism;
- debugging.

But excessive decomposition can produce:

```text
task_1
task_2
...
task_10000
```

which increases orchestration overhead.

The correct task boundary depends on:

- recoverability;
- observability;
- dependency structure;
- runtime;
- operational ownership;
- scheduler overhead.

---

# 26. Idempotent Tasks

An idempotent task can be safely repeated without producing an incorrect logical result.

Example:

```text
load_partition(date="2026-10-01")
```

A safe implementation can rerun that logical partition without creating an incorrect duplicate state.

Contrast with:

```python
append_rows_to_table()
```

If a retry blindly appends the same rows, duplicates can occur.

Idempotency matters for:

- retries;
- backfills;
- manual reruns;
- recovery;
- overlapping executions.

A conceptual test is:

```text
Run once
   ↓
Correct result

Run again with the same logical input
   ↓
Still correct
```

Idempotency is a property of the operation and its surrounding data semantics, not merely a scheduler setting.

---

# 27. Deterministic Tasks

A deterministic task should produce the same logical result given:

```text
same inputs
+
same parameters
+
same code/version
```

Useful practices:

- explicit data intervals;
- explicit inputs;
- controlled parameters;
- avoiding hidden current-time dependencies;
- avoiding uncontrolled randomness.

### Deterministic vs idempotent

They are related but different.

**Deterministic** asks:

> Given the same conditions, is the result predictable?

**Idempotent** asks:

> Can the same logical operation be repeated without making the result incorrect?

A useful mental model is:

```text
deterministic
+
idempotent
=
safer orchestration
```

They are not identical concepts.

---

# 28. Concurrency in Orchestration

Example:

```text
                  ┌── extract_orders
extract_sources ──┼── extract_customers
                  └── extract_products
```

After `extract_sources` succeeds, independent branches can become eligible.

Conceptually:

- **concurrency** concerns overlapping progress;
- **parallelism** concerns simultaneous execution on separate resources.

The orchestration concern is:

> Which work is eligible concurrently, and how much concurrency is safe?

Detailed Python concurrency mechanics belong to the dedicated concurrency module.

---

# 29. Concurrency Controls

Important controls include:

- maximum active runs;
- maximum parallel tasks;
- resource pools.

Unrestricted concurrency can overload:

- APIs;
- databases;
- SFTP servers;
- warehouses;
- CPU;
- memory;
- network;
- downstream systems.

Example:

```text
API limit = 10 requests/second
```

but the workflow launches:

```text
100 concurrent extraction tasks
```

The workflow may overload the API.

Therefore orchestration must control concurrency.

---

# 30. Maximum Active Runs

Suppose:

```text
orders_daily
```

allows only one active run.

If yesterday's run is still executing:

```text
Yesterday = active
Today     = waiting
```

This can prevent unsafe overlap.

However, overlap is not inherently bad. Whether it is safe depends on:

- idempotency;
- partitioning;
- output design;
- downstream capacity;
- resource constraints.

---

# 31. Maximum Parallel Tasks

Suppose:

```text
maximum parallel tasks = 10
```

and 30 tasks are eligible.

Conceptually:

```text
10 execute
20 wait
```

This creates a controlled execution envelope.

---

# 32. Resource Pools

A resource pool represents shared constrained capacity.

Example:

```text
SFTP_POOL = 3 slots
```

If 20 tasks require SFTP:

```text
3 execute
17 wait
```

The tasks are not necessarily dependent on each other.

They simply compete for a constrained resource.

Examples:

```text
sftp_pool
api_pool
warehouse_pool
gpu_pool
```

Resource pools are therefore an orchestration-level representation of operational capacity.

---

# 33. Orchestration vs Execution

One of the most important principles in production orchestration is:

> **The orchestrator coordinates work; it should not perform the heavy work itself.**

### Preferred

```text
Orchestrator
     ↓
Submit SQL / Spark / container / CLI
     ↓
Execution system
     ↓
Heavy computation
```

### Problematic

```text
Orchestrator process
     ↓
Load 500 GB dataset into memory
     ↓
Transform it
```

Heavy computation inside the orchestration process can cause:

- scheduler instability;
- memory pressure;
- poor scalability;
- difficult recovery;
- resource contention;
- operational coupling.

---

# 34. Real-World Execution Systems

An orchestrator can coordinate:

```text
PostgreSQL
Spark
dbt
Python CLI
Docker container
Kubernetes job
Object storage
API
```

without becoming the compute engine.

Examples:

```text
Airflow
   ↓
dbt build
   ↓
Warehouse executes transformation
```

or:

```text
Airflow
   ↓
Submit Spark job
   ↓
Spark cluster performs computation
```

Framework-specific implementation belongs to later topics.

---

# 35. Task-Centric vs Asset-Centric Orchestration

## Task-centric

```text
Run task A
   ↓
Run task B
   ↓
Run task C
```

The primary mental object is the task and its execution.

## Asset-centric

```text
Keep dataset A up to date
        ↓
enables dataset B
        ↓
enables dataset C
```

The primary object is the data asset.

Airflow and Prefect commonly support task-oriented workflow thinking, while Airflow also has asset-aware scheduling. Dagster strongly emphasizes software-defined assets.

This topic introduces the distinction; detailed implementation belongs later.

---

# 36. Cross-Workflow Dependencies

A production platform may contain:

```text
Ingestion Workflow
        ↓
Transformation Workflow
        ↓
Quality Workflow
        ↓
Publishing Workflow
```

Possible coordination mechanisms include:

- time-based coordination;
- event-based coordination;
- data-aware dependency;
- explicit workflow dependency.

Avoid fragile assumptions such as:

```text
"the upstream usually finishes by 05:30"
```

followed by:

```text
start downstream at 06:00
```

Execution duration varies.

A real dependency should represent actual readiness or completion.

---

# 37. Why One Giant DAG Is Usually Problematic

A giant DAG can create:

- ownership problems;
- large blast radius;
- difficult deployment;
- difficult debugging;
- dependency complexity;
- difficult backfills;
- scheduling complexity;
- poor operational independence.

Several logical workflows can instead be used:

```text
Ingestion
   ↓
Transformation
   ↓
Quality
   ↓
Publishing
```

But excessive fragmentation also causes:

- hidden dependencies;
- dependency-management problems;
- operational fragmentation.

Engineering principle:

> **Split workflows according to meaningful ownership, lifecycle, dependency, and operational boundaries—not arbitrary task counts.**

---

# 38. Orchestrator as Operational Metadata System

A production orchestrator records operational metadata such as:

```text
run id
task id
state
start time
end time
duration
retry count
failure information
logs
dependencies
```

This allows questions such as:

> Which task failed?

> How long did it run?

> How many times did it retry?

> Which interval failed?

> Which downstream work was affected?

Lineage awareness extends this idea to relationships between workflows/tasks and the data they produce or consume.

---

# 39. Tool-Independent DAG Runner

The goal of this project is **not** to build a production orchestrator.

The goal is to understand the internal concepts.

Requirements:

1. tasks are Python functions;
2. dependencies are represented using a dictionary;
3. execute tasks in topological order;
4. detect cycles;
5. recognize independent tasks;
6. record task states;
7. refuse cycles;
8. add retries per task;
9. propagate upstream failure;
10. pass a data interval to every task;
11. run the workflow for three historical days.

---

## 39.1 Define Tasks

```python
from datetime import datetime


def extract(
    interval_start: datetime,
    interval_end: datetime,
) -> None:
    print(f"Extract: {interval_start} → {interval_end}")


def transform(
    interval_start: datetime,
    interval_end: datetime,
) -> None:
    print(f"Transform: {interval_start} → {interval_end}")


def validate(
    interval_start: datetime,
    interval_end: datetime,
) -> None:
    print(f"Validate: {interval_start} → {interval_end}")


def publish(
    interval_start: datetime,
    interval_end: datetime,
) -> None:
    print(f"Publish: {interval_start} → {interval_end}")


tasks = {
    "extract": extract,
    "transform": transform,
    "validate": validate,
    "publish": publish,
}
```

---

## 39.2 Define Dependencies

```python
dependencies = {
    "extract": [],
    "transform": ["extract"],
    "validate": ["transform"],
    "publish": ["validate"],
}
```

This is:

```text
extract
   ↓
transform
   ↓
validate
   ↓
publish
```

---

## 39.3 Topological Sort

Use the previously defined:

```python
topological_sort(dependencies)
```

to determine a valid execution order.

The important learning is:

```text
Graph
  ↓
Topological order
  ↓
Eligible tasks
```

---

## 39.4 Add Task States

```python
from enum import Enum


class TaskState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    UP_FOR_RETRY = "up_for_retry"
    SKIPPED = "skipped"
    UPSTREAM_FAILED = "upstream_failed"
```

Example lifecycle:

```text
QUEUED
  ↓
RUNNING
  ↓
SUCCESS
```

or:

```text
QUEUED
  ↓
RUNNING
  ↓
FAILED
  ↓
UP_FOR_RETRY
  ↓
RUNNING
```

---

## 39.5 Add Retries

```python
import time


def execute_with_retries(
    task,
    interval_start: datetime,
    interval_end: datetime,
    max_retries: int,
) -> bool:
    attempts = 0

    while True:
        try:
            task(interval_start, interval_end)
            return True

        except Exception as exc:
            attempts += 1

            if attempts > max_retries:
                print(f"Permanent failure: {exc}")
                return False

            print(
                f"Retrying after failure "
                f"({attempts}/{max_retries}): {exc}"
            )
            time.sleep(0.1)
```

The conceptual transition is:

```text
RUNNING
   ↓
FAILED
   ↓
UP_FOR_RETRY
   ↓
RUNNING
```

Retrying safely requires rerunnable task behavior.

---

## 39.6 Pass a Data Interval

```python
def run_workflow(
    start: datetime,
    end: datetime,
) -> None:
    print(
        f"Workflow interval: "
        f"{start.isoformat()} → {end.isoformat()}"
    )
```

Every task should receive:

```text
interval_start
interval_end
```

rather than deriving the business date from the machine clock.

---

## 39.7 Run Three Historical Days

```python
from datetime import datetime, timedelta

days = [
    datetime(2026, 9, 28),
    datetime(2026, 9, 29),
    datetime(2026, 9, 30),
]

for day in days:
    next_day = day + timedelta(days=1)
    run_workflow(day, next_day)
```

This produces three explicit historical intervals.

That is the conceptual foundation for reproducible historical execution.

---

## 39.8 Failure Propagation

Suppose:

```text
extract       SUCCESS
transform     FAILED
validate      UPSTREAM_FAILED
publish       UPSTREAM_FAILED
```

A downstream task should not blindly execute against incomplete upstream output.

For fan-out:

```text
             ┌── task_b SUCCESS ──┐
task_a ──────┼── task_c FAILED ───┼── task_e
             └── task_d SUCCESS ──┘
```

If every branch is required, `task_e` cannot safely execute.

The key idea:

> **Failure propagation is a dependency decision, not merely an exception-handling decision.**

---

## 39.9 Parallel Eligibility

Given:

```text
           ┌── task_b
task_a ────┼── task_c
           └── task_d
```

after `task_a` succeeds:

```text
task_b = eligible
task_c = eligible
task_d = eligible
```

Eligibility does not necessarily mean immediate execution.

The orchestrator must still apply:

```text
workflow limits
task limits
resource limits
system limits
```

---

# 40. Break the Runner Deliberately

Use:

```text
Build it
   ↓
Run it
   ↓
Break it
   ↓
Observe
   ↓
Fix it
```

## Failure

Make `transform` raise an exception.

Expected:

```text
transform = FAILED
downstream = UPSTREAM_FAILED
```

## Hang

Make a task sleep longer than expected.

Discuss:

- timeout concepts;
- monitoring;
- stuck-run detection.

Detailed timeout configuration belongs to later topics.

## Cycle

Add:

```text
publish → extract
```

Now:

```text
extract → transform → validate → publish
   ↑                              ↓
   └──────────────────────────────┘
```

Cycle detection must reject the graph.

## Non-idempotent behavior

Make a task append duplicate output on every execution.

Run it twice.

Observe the incorrect result.

## Overlap

Run two workflow instances against the same output.

Analyze why:

- idempotency;
- partitioning;
- concurrency controls

matter.

---

# 41. Required Diagram Set

## Simple DAG

```text
A → B → C
```

## Directed graph

```text
A → B
A → C
```

## Cyclic graph

```text
A → B → C
↑       ↓
└───────┘
```

## Topological order

```text
A
↓
B
↓
C
```

## Fan-out

```text
       ┌── B
A ─────┼── C
       └── D
```

## Fan-in

```text
A ──┐
B ──┼── D
C ──┘
```

## Fan-out + fan-in

```text
       ┌── B ──┐
A ─────┼── C ──┼── E
       └── D ──┘
```

## Time-based scheduling

```text
Clock
  ↓
Schedule reached
  ↓
Workflow run
```

## Event-based scheduling

```text
External event
      ↓
Workflow becomes eligible
```

## Data-aware scheduling

```text
Dataset updated
      ↓
Downstream workflow eligible
```

## Run vs task instance

```text
Workflow definition
        ↓
    Workflow run
        ↓
  ┌─────┼─────┐
  ↓     ↓     ↓
Task  Task  Task
instance instances instances
```

## Task state transitions

```text
queued
  ↓
running
 ├── success
 ├── failed → up_for_retry → running
 └── skipped
```

## Data interval

```text
start                         end
 |-----------------------------|
2026-10-01 00:00          2026-10-02 00:00
```

## Task granularity

```text
Too coarse:
[ entire pipeline ]

Meaningful:
[extract] [transform] [validate] [publish]

Too fine:
[tiny] [tiny] [tiny] ... [tiny]
```

## Orchestration vs execution

```text
Orchestrator
     ↓
Submit work
     ↓
Execution system
     ↓
Heavy computation
```

## Task-centric vs asset-centric

```text
Task-centric:
A → B → C

Asset-centric:
Dataset A → Dataset B → Dataset C
```

## Cross-workflow dependencies

```text
Ingestion
   ↓
Transformation
   ↓
Quality
   ↓
Publishing
```

## Multi-workflow architecture

```text
Sources
   ↓
Ingestion
   ↓
Transformation
   ↓
Quality
   ↓
Publishing
```

Every diagram exists to support an execution concept, not merely as decoration.

---

# 42. Real-World Data Engineering Examples

Use orchestration reasoning with:

- orders;
- customers;
- payments;
- transactions;
- APIs;
- SFTP files;
- PostgreSQL;
- object storage;
- dbt;
- data quality;
- warehouse publishing.

Example:

```text
SFTP Partner
     ↓
Extract
     ↓
Bronze
     ↓
Silver
     ↓
Quality Gate
     ↓
Gold
     ↓
Publish
```

This becomes an orchestration graph when each meaningful stage is represented as a task and real relationships are represented as dependencies.

---

# 43. Common Orchestration Mistakes

## 1. Confusing execution date with data date

**Consequence:** wrong partitions are processed.

**Better:** use explicit run context/data interval.

## 2. Using current time for historical logic

**Consequence:** historical reruns can produce different results.

**Better:** pass interval boundaries.

## 3. One giant task

**Consequence:** coarse recovery and poor observability.

**Better:** meaningful task boundaries.

## 4. Thousands of tiny tasks

**Consequence:** scheduler and metadata overhead.

**Better:** group work meaningfully.

## 5. Heavy computation inside the orchestrator

**Consequence:** scheduler instability and resource contention.

**Better:** delegate heavy work to execution systems.

## 6. Cyclic dependencies

**Consequence:** no valid execution order.

**Better:** validate the graph.

## 7. No concurrency limits

**Consequence:** downstream systems are overloaded.

**Better:** use active-run limits, task limits, and resource pools.

## 8. Non-idempotent tasks

**Consequence:** retries can create duplicates or inconsistent state.

**Better:** design safe reruns.

## 9. Timing-based dependencies

**Consequence:** downstream can start before upstream is ready.

**Better:** use actual completion/data readiness.

## 10. One giant DAG for the entire company

**Consequence:** ownership and operational recovery become difficult.

**Better:** establish logical workflow boundaries.

## 11. Ignoring task states

**Consequence:** operators cannot understand what happened.

**Better:** model lifecycle state explicitly.

## 12. Ignoring retries

**Consequence:** transient failures become unnecessary workflow failures.

**Better:** define appropriate retry behavior.

## 13. Passing large datasets through orchestration metadata

**Consequence:** the metadata system becomes a data transport layer.

**Better:** store data in the appropriate data system and pass references.

## 14. Treating scheduling as execution

**Consequence:** responsibilities become mixed.

**Better:** separate coordination from computation.

## 15. Artificial dependencies

**Consequence:** unnecessary serialization and reduced parallelism.

**Better:** dependencies should represent real business, data, or resource relationships.

---

# 44. Debugging Scenarios

For every incident, use:

```text
Problem
Symptoms
Evidence
Root cause
Investigation
Solution
Production lesson
```

## Scenario 1 — Downstream starts before data is ready

**Problem:** A transformation begins while extraction is incomplete.

**Symptoms:** partial data and intermittent failures.

**Evidence:** downstream starts at a fixed clock time.

**Root cause:** timing assumption replaced a real dependency.

**Investigation:** compare actual upstream completion with downstream start.

**Solution:** coordinate on actual completion/data availability.

**Production lesson:** schedules are not substitutes for readiness dependencies.

---

## Scenario 2 — Daily job processes the wrong date

**Problem:** A run on October 2 processes October 2 instead of October 1.

**Symptoms:** wrong partitions or duplicates.

**Evidence:** task calls `datetime.now()`.

**Root cause:** execution time confused with data interval.

**Investigation:** inspect interval context and task timestamp logic.

**Solution:** pass explicit interval boundaries.

**Production lesson:** business scope should be explicit.

---

## Scenario 3 — Two runs overlap and corrupt output

**Problem:** two runs write the same logical output concurrently.

**Symptoms:** duplicate/inconsistent data.

**Evidence:** multiple active runs.

**Root cause:** overlap was not made safe.

**Investigation:** inspect run history and destination writes.

**Solution:** use idempotent partition-aware writes and appropriate active-run controls.

**Production lesson:** overlap is an architectural decision.

---

## Scenario 4 — A cycle prevents execution

**Problem:** no valid task becomes ready.

**Symptoms:** dependency scheduling cannot progress.

**Evidence:**

```text
A → B → C → A
```

**Root cause:** cyclic dependency.

**Investigation:** run cycle detection.

**Solution:** remove the incorrect relationship.

**Production lesson:** DAGs must remain acyclic.

---

## Scenario 5 — Massive task causes slow recovery

**Problem:** a six-hour task fails after five hours.

**Symptoms:** retry restarts everything.

**Root cause:** task boundary is too coarse.

**Investigation:** identify independently recoverable stages.

**Solution:** split into meaningful tasks.

**Production lesson:** task boundaries determine recovery granularity.

---

## Scenario 6 — 500 tasks overwhelm an API

**Problem:** hundreds of tasks execute concurrently.

**Symptoms:** rate-limit errors and connection failures.

**Root cause:** insufficient concurrency control.

**Investigation:** measure task concurrency against API capacity.

**Solution:** apply bounded concurrency/resource controls.

**Production lesson:** maximum task throughput is constrained by downstream capacity.

---

## Scenario 7 — Downstream relies on estimated completion

**Problem:** downstream starts at 06:00 because upstream "usually finishes by 05:30."

**Symptoms:** intermittent incomplete data.

**Root cause:** timing assumption.

**Solution:** explicit completion/data dependency.

**Production lesson:** coordinate on actual readiness.

---

# 45. Practical Exercises

## Exercise 1 — Draw a DAG

Convert:

```text
Extract orders
Extract customers
Transform orders
Transform customers
Quality check
Publish
```

into a DAG.

Identify:

- dependencies;
- independent branches;
- fan-out;
- fan-in.

## Exercise 2 — Identify Dependencies

Given:

```text
extract_orders
extract_customers
transform_orders
transform_customers
customer_360
publish
```

Assume:

- `transform_orders` depends on `extract_orders`;
- `transform_customers` depends on `extract_customers`;
- `customer_360` depends on both transformations;
- `publish` depends on `customer_360`.

Write the dependency dictionary.

## Exercise 3 — Topological Sort

Given:

```python
dependencies = {
    "extract": [],
    "transform": ["extract"],
    "validate": ["transform"],
    "publish": ["validate"],
}
```

Determine a valid order.

## Exercise 4 — Detect a Cycle

Given:

```python
dependencies = {
    "A": ["C"],
    "B": ["A"],
    "C": ["B"],
}
```

Determine whether a cycle exists and explain it.

## Exercise 5 — Fan-Out/Fan-In

Design:

```text
Ingestion
   ├── Validate Orders
   ├── Validate Customers
   └── Validate Products
              ↓
            Publish
```

Explain which tasks can execute independently.

## Exercise 6 — Scheduling

Choose the conceptual trigger for:

1. daily 06:00 reporting;
2. processing when a partner file arrives;
3. processing when an upstream dataset updates;
4. emergency manual rerun.

Explain the decision.

## Exercise 7 — Task Granularity

Compare:

```text
run_entire_pipeline()
```

with:

```text
extract
transform
validate
publish
```

Explain the trade-offs.

## Exercise 8 — Idempotency

Evaluate:

```text
replace partition for 2026-10-01
append rows without deduplication
upsert by business key
create file with incrementing timestamp
```

Which are naturally safer to rerun, and why?

## Exercise 9 — Concurrency

An API supports ten concurrent requests and there are 50 independent extraction tasks.

Design an orchestration-level concurrency strategy.

## Exercise 10 — Workflow Boundaries

Split:

```text
Extract every source
Transform every source
Run every quality check
Publish every dataset
Send every notification
```

into logical workflows and justify the boundaries.

---

# 46. Mini Project — Production Data Workflow

## Scenario

Every day a company receives:

1. orders from SFTP;
2. customers from an API;
3. products from PostgreSQL.

The platform must:

```text
Extract
   ↓
Validate
   ↓
Transform
   ↓
Quality Check
   ↓
Publish
```

Requirements:

- independent sources can execute concurrently;
- transformations wait for required extraction;
- quality checks complete before publishing;
- each run processes a defined data interval;
- tasks are idempotent;
- concurrency respects source limits;
- heavy computation runs outside the orchestrator;
- workflow boundaries are justified.

### Learner tasks

1. draw the DAG;
2. define tasks;
3. define dependencies;
4. identify fan-out/fan-in;
5. define triggers;
6. define task states;
7. define concurrency limits;
8. identify task granularity;
9. explain idempotency;
10. identify where heavy computation runs;
11. decide one workflow vs several;
12. explain historical reruns.

## Complete Solution

A reasonable graph is:

```text
Extract Orders ───────┐
Extract Customers ────┼── Transform ── Quality ── Publish
Extract Products ─────┘
```

Independent extraction tasks can become eligible concurrently.

Transform waits for its required inputs.

Quality waits for transformation.

Publish waits for the required quality gates.

A daily schedule can create the run, while event/data-aware triggers may be appropriate when source arrival is the true readiness condition.

Each run should carry:

```text
data_interval_start
data_interval_end
```

Writes should be idempotent for safe reruns.

Concurrency should respect:

```text
API pool
SFTP pool
Database pool
```

Heavy processing should be submitted to the appropriate execution system.

Workflow boundaries should follow ownership, lifecycle, dependency, and operational recovery requirements.

---

# 47. Interview Questions

## Basic — 10

1. **What is a DAG?**  
   A Directed Acyclic Graph; in orchestration, tasks are nodes and dependencies are directed edges.

2. **What is a task?**  
   A meaningful unit of work that can be observed and recovered independently.

3. **What is a dependency?**  
   A relationship controlling when downstream work becomes eligible.

4. **Why can DAGs not contain cycles?**  
   Circular prerequisites prevent a valid starting point and topological order.

5. **What is fan-out?**  
   One task enabling multiple downstream branches.

6. **What is fan-in?**  
   Multiple upstream tasks converging on a downstream task.

7. **What is a workflow run?**  
   One execution instance of a workflow definition.

8. **What is a task instance?**  
   One task as part of a particular workflow run.

9. **What is a data interval?**  
   The period of data represented by a run.

10. **What is a trigger?**  
    An event/action that makes a workflow eligible to run.

## Intermediate — 10

1. **Why is logical date different from execution time?**  
   A run can execute after the interval it represents has closed.

2. **How do task states work?**  
   Tasks move through lifecycle states such as queued, running, success, failed, retry, skipped, and upstream failed.

3. **Why does task granularity matter?**  
   It affects retries, observability, failure isolation, parallelism, and scheduler overhead.

4. **Why must tasks be idempotent?**  
   Retries and reruns repeat logical operations.

5. **What is deterministic vs idempotent?**  
   Determinism concerns predictable output for the same inputs; idempotency concerns safe repeated execution.

6. **How do concurrency limits protect systems?**  
   They prevent excessive simultaneous load on shared resources.

7. **What is a resource pool?**  
   A shared capacity constraint for tasks competing for a limited resource.

8. **What is data-aware scheduling?**  
   Scheduling based on required data becoming available or updated.

9. **Why are cross-workflow dependencies difficult?**  
   They coordinate independently executing workflows and can become fragile.

10. **Why are timing-based dependencies fragile?**  
    Upstream duration varies, so estimated completion times are not guaranteed.

## Advanced — 10

1. **Why should an orchestrator remain thin?**  
   It coordinates; execution systems perform heavy computation.

2. **When should you split a DAG?**  
   When meaningful ownership, lifecycle, dependency, or operational boundaries exist.

3. **When is a giant DAG justified?**  
   When work genuinely forms one tightly coupled operational lifecycle.

4. **How should workflow boundaries be designed?**  
   Around real business/data dependencies, ownership, lifecycle, and recovery.

5. **How would you control API rate limits?**  
   Use bounded concurrency and shared resource controls.

6. **How would you design safe reruns?**  
   Use interval-scoped inputs, deterministic logic, idempotent writes, and controlled concurrency.

7. **How do you distinguish orchestration from execution?**  
   Orchestration coordinates eligibility and submission; execution systems perform computation.

8. **Task-centric vs asset-centric: when is each useful?**  
   Task-centric emphasizes execution units; asset-centric emphasizes keeping datasets/assets current.

9. **What operational metadata should an orchestrator maintain?**  
   Run/task identity, state, timing, duration, retries, failures, logs, and dependencies.

10. **How would you diagnose repeated workflow overlap?**  
    Inspect run history, active-run controls, task durations, interval ownership, and output-writing behavior.

---

# 48. Architecture Questions

## Architecture 1 — Five Independent Sources

### Problem

Design ingestion for five independent sources.

### Reasoning

Do not serialize independent work unnecessarily.

### Architecture

```text
              ┌── Source A
              ├── Source B
Orchestrator ─┼── Source C
              ├── Source D
              └── Source E
```

### Trade-offs

More concurrency can improve throughput but increases resource pressure.

### Production considerations

Use source-specific concurrency/resource limits and idempotent writes.

---

## Architecture 2 — Bronze → Silver → Gold

```text
Bronze
  ↓
Silver
  ↓
Quality
  ↓
Gold
  ↓
Publish
```

Each stage can be independently observable and recoverable.

Trade-off: more stages improve visibility but add orchestration metadata and dependencies.

---

## Architecture 3 — Cross-Workflow Dependencies

Avoid:

```text
Upstream usually finishes at 05:30
          ↓
Downstream starts at 06:00
```

Prefer:

```text
Upstream complete
       ↓
Downstream eligible
```

or data availability:

```text
Dataset updated
       ↓
Downstream eligible
```

---

## Architecture 4 — Rate-Limited API

```text
Many eligible tasks
       ↓
API resource limit
       ↓
Bounded execution
       ↓
API
```

The system should favor safe bounded throughput over uncontrolled concurrency.

---

## Architecture 5 — Multi-Workflow Platform

```text
┌─────────────┐
│  Ingestion  │
└──────┬──────┘
       ↓
┌──────────────┐
│Transformation│
└──────┬───────┘
       ↓
┌─────────────┐
│   Quality   │
└──────┬──────┘
       ↓
┌─────────────┐
│ Publishing  │
└─────────────┘
```

The workflows can have separate ownership and lifecycle while retaining explicit dependencies.

---

# 49. Knowledge Check

Before continuing, verify that you can answer:

- [ ] Can I explain DAGs without mentioning Airflow?
- [ ] Can I identify dependencies?
- [ ] Can I detect cycles?
- [ ] Can I explain topological order?
- [ ] Can I explain fan-out and fan-in?
- [ ] Can I distinguish schedule from trigger?
- [ ] Can I explain a workflow run?
- [ ] Can I explain a task instance?
- [ ] Can I explain task states?
- [ ] Can I explain logical date?
- [ ] Can I explain data interval?
- [ ] Can I explain task granularity?
- [ ] Can I explain idempotency?
- [ ] Can I explain determinism?
- [ ] Can I explain concurrency limits?
- [ ] Can I explain resource pools?
- [ ] Can I explain orchestration vs execution?
- [ ] Can I explain task-centric vs asset-centric orchestration?
- [ ] Can I explain cross-workflow dependencies?
- [ ] Can I explain why giant DAGs can become problematic?

---

# 50. Final Mental Model

```text
WORKFLOW
   ↓
TASKS
   ↓
DEPENDENCIES
   ↓
DAG
   ↓
TRIGGER / SCHEDULE
   ↓
RUN
   ↓
TASK INSTANCES
   ↓
TASK STATES
   ↓
EXECUTION
   ↓
RETRY / FAILURE / RECOVERY
   ↓
OBSERVABILITY
```

Reinforce:

```text
Orchestrator coordinates.
Execution systems compute.

Tasks should be meaningful.
Dependencies should represent real relationships.

Runs should be interval-aware.
Tasks should be deterministic and idempotent.

Concurrency should be bounded.
Failures should be observable.

Historical runs should be reproducible.
```

---

# 51. Final Learning Checkpoint

```text
[ ] Workflow
[ ] Task
[ ] Dependency
[ ] DAG
[ ] Directed graph
[ ] Acyclic graph
[ ] Cycle detection
[ ] Topological ordering
[ ] Fan-out
[ ] Fan-in
[ ] Time-based scheduling
[ ] Fixed intervals
[ ] Cron basics
[ ] Event-based triggers
[ ] Data-aware triggers
[ ] Manual triggers
[ ] Workflow runs
[ ] Task instances
[ ] Task states
[ ] Logical date
[ ] Data interval
[ ] Task granularity
[ ] Idempotency
[ ] Determinism
[ ] Concurrency
[ ] Maximum active runs
[ ] Maximum parallel tasks
[ ] Resource pools
[ ] Orchestration vs execution
[ ] Task-centric orchestration
[ ] Asset-centric orchestration
[ ] Cross-workflow dependencies
[ ] Workflow boundaries
[ ] Operational metadata
```

Do not move to advanced Airflow implementation concepts until these fundamentals are clearly established.

---

# 52. Scope Boundaries for Topic 01

The following belong primarily to later topics:

```text
Topic 02 — Limits of cron and why orchestrators exist
Topic 03 — Apache Airflow architecture
Topic 04 — Airflow DAGs, operators, and TaskFlow API
Topic 05 — Connections, variables, hooks, XComs
Topic 06 — Sensors, deferrable operators, data-aware scheduling implementation
Topic 07 — Retries, deadlines, failure callbacks
Topic 08 — Backfills, catch-up, partitioned runs
Topic 09 — Dagster software-defined assets
Topic 10 — Prefect flows and tasks
Topic 11 — Testing and validating DAGs
```

This chapter introduces concepts needed to understand orchestration, but does not turn them into framework-specific tutorials.

Examples:

- Explain data-aware scheduling conceptually; do not teach full Airflow asset syntax.
- Explain task states conceptually; do not teach complete Airflow retry configuration.
- Explain interval-scoped historical execution; do not teach the complete framework-specific backfill workflow.

---

# 53. Production Engineering Standard

For every major concept, ask:

```text
What is it?
Why does it exist?
How does it work?
When should I use it?
What can go wrong?
What are the trade-offs?
How is it implemented?
How do I debug it?
How does it behave in production?
```

Use:

```text
Concept
→ Why it exists
→ Internal mechanics
→ Real-world example
→ Small example
→ Code
→ Failure mode
→ Debugging
→ Production consideration
→ Exercise
→ Review
→ Interview question
→ Architecture question
```

---

# 54. Topic Completion Standard

You should be able to look at a Data Engineering pipeline and independently identify:

```text
What are the tasks?
What are the dependencies?
What is the DAG?
Where is the fan-out?
Where is the fan-in?
What triggers the workflow?
What data interval does each run represent?
What are the task instances?
What states can tasks enter?
What tasks can run concurrently?
What concurrency must be limited?
Are tasks idempotent?
Are tasks deterministic?
Where does the heavy computation execute?
Should this be one workflow or multiple workflows?
What operational metadata should be recorded?
```

The conceptual progression is:

```text
Python scripts
    ↓
Workflow
    ↓
Tasks
    ↓
Dependencies
    ↓
DAG
    ↓
Scheduling / Triggers
    ↓
Runs
    ↓
Task Instances
    ↓
States
    ↓
Intervals
    ↓
Retries / Failure / Recovery
    ↓
Concurrency Controls
    ↓
Operational Metadata
    ↓
Production Workflow Design
```

This topic is the conceptual foundation for the remaining orchestration topics in Module 2.13.
