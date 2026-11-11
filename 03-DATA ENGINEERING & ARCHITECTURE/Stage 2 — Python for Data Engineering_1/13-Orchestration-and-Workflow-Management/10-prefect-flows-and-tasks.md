# Prefect Flows and Tasks

> **Stage 2 — Python for Data Engineering**  
> **Module 2.13 — Orchestration and Workflow Management**  
> **Topic 10 — Prefect Flows and Tasks**
>
> **Learning level:** Beginner → Foundational → Intermediate → Advanced → Production-grade Data Engineering  
> **Primary principle:** An orchestrator coordinates work; it should not become the heavy data-processing engine.

---

## 1. Learning Objectives

By the end of this topic, you should be able to:

- Explain what workflow orchestration is and why Data Engineering systems need it.
- Explain the difference between a workflow, task, flow run, task run, state, deployment, worker, work pool, schedule, event, automation, and result.
- Explain where Prefect fits in a production Data Engineering architecture.
- Create Prefect 3 flows with `@flow`.
- Create meaningful tasks with `@task`.
- Pass typed and structured parameters into flows.
- Use Prefect logging without leaking secrets or sensitive data.
- Design retries around transient failures and idempotent operations.
- Apply timeouts to operations that can hang or exceed an acceptable execution window.
- Explain task caching and when caching is unsafe.
- Execute independent tasks concurrently with `.submit()`.
- Explain futures and dependency propagation.
- Use mapped work for dynamic collections of sources/items.
- Bound concurrency rather than treating concurrency as unlimited compute.
- Explain task runners and their relationship to execution.
- Explain task and flow states.
- Understand result persistence and why large datasets should not travel through the orchestrator.
- Use state hooks for operational side effects.
- Explain deployments, `serve()`, `deploy()`, work pools, and workers.
- Schedule flow runs and distinguish schedules from event-driven execution.
- Explain events and automations.
- Separate code, configuration, and secrets using appropriate configuration mechanisms.
- Design workflows that remain safe when a task is retried after a partial side effect.
- Build an end-to-end Data Engineering ingestion workflow.
- Inject failures and diagnose the resulting states and logs.
- Test Python business logic, tasks, flows, parameters, retries, and mapped work.
- Apply production design principles and identify orchestration anti-patterns.
- Compare Prefect, Airflow, and Dagster technically without assuming one tool is universally correct.
- Explain when a cron job may be sufficient and when orchestration adds meaningful operational value.
- Design a production-style `ingest_sources` system.

---

## 2. Prerequisites

This topic assumes that you understand:

- Python functions and decorators.
- Exceptions and exception handling.
- Basic type hints.
- Lists, dictionaries, loops, and comprehensions.
- HTTP/API concepts.
- Basic database concepts.
- Object storage concepts.
- Batch data pipelines.
- Idempotency at a conceptual level.
- Basic concurrency concepts from the preceding Data Engineering material.

You do **not** need previous Prefect experience.

### 2.1 What You Should Already Understand

A normal Python pipeline might look like:

```python
def extract():
    ...

def validate():
    ...

def transform():
    ...

def load():
    ...

extract()
validate()
transform()
load()
```

The code may work locally.

The production problem is not merely:

> "Can Python execute these functions?"

The production problem becomes:

- When should the workflow run?
- What happens if the API fails?
- Which step failed?
- Should the failed step retry?
- What happens if the retry repeats a database write?
- How long should a task be allowed to run?
- Can independent sources be processed concurrently?
- How do we prevent 500 concurrent requests?
- How do we observe historical runs?
- How do we deploy the workflow?
- What happens when the execution environment disappears?
- How do we trigger downstream processing?
- How do we safely rerun yesterday's partition?
- How do we test failure behavior?

Those are orchestration problems.

---

# 3. What Problem Prefect Solves

## 3.1 What Is Orchestration?

Workflow orchestration is the coordination of computational work according to dependencies, timing, state, failure behavior, and operational requirements.

A simplified workflow is:

```text
Extract
   ↓
Validate
   ↓
Transform
   ↓
Load
```

A real workflow may be:

```text
             ┌── Source A ──┐
             │              │
Start ───────┼── Source B ──┼── Validate ── Transform ── Load
             │              │
             └── Source C ──┘
```

The orchestrator coordinates the work.

It should not automatically become the place where all heavy computation happens.

---

## 3.2 Why Data Engineering Pipelines Need Orchestration

A production pipeline needs more than Python functions.

| Requirement | Orchestration concern |
|---|---|
| Timing | Schedule |
| Dependencies | Task/flow graph |
| Failure | State and failure handling |
| Transient errors | Retries |
| Hanging operations | Timeouts |
| Parallel sources | Concurrency |
| Historical execution | Run history |
| Configuration | Parameters/configuration |
| Operations | Logs and UI |
| Deployment | Execution infrastructure |
| External triggers | Events/automations |
| Reproducibility | Explicit inputs and deterministic processing |

Without orchestration, teams frequently end up implementing these concerns inconsistently inside scripts.

---

## 3.3 The Thin-Orchestration Principle

A useful production rule is:

> **Keep orchestration thin and keep business/data-processing logic reusable.**

Prefer:

```text
Prefect Flow
    ↓
Prefect Tasks
    ↓
Reusable Python / SQL / Spark / dbt / database / API logic
    ↓
External data systems
```

Avoid turning the flow into a giant application:

```python
@flow
def everything():
    # 2,000 lines of extraction,
    # transformation,
    # database logic,
    # validation,
    # retry logic,
    # notifications,
    # business rules...
    ...
```

A flow should coordinate meaningful units of work.

---

# 4. Prefect Mental Model

Prefect is an orchestration framework that allows ordinary Python code to be represented and operated as workflows.

The core mental model is:

```text
                         ┌──────────────────────┐
                         │      Prefect         │
                         │  orchestration layer │
                         └──────────┬───────────┘
                                    │
                                  Flow
                                    │
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
                  Task A          Task B          Task C
                    │               │               │
                    └─────── dependencies ─────────┘
                                    │
                                 Flow Run
                                    │
                              Task Runs
                                    │
                         States / Logs / Results
                                    │
                     Deployment / Worker / Work Pool
                                    │
                     Scheduled or event-driven execution
```

---

## 4.1 Prefect

Prefect is the orchestration framework.

It provides concepts for:

- defining flows;
- defining tasks;
- tracking runs;
- recording states;
- logging;
- retries;
- timeouts;
- caching;
- concurrency;
- deployment;
- scheduling;
- events and automations;
- operational visibility.

Prefect does **not** mean that every data transformation should execute inside the orchestration service.

---

## 4.2 Flow

A **flow** is the top-level workflow boundary.

Example:

```python
from prefect import flow

@flow
def daily_orders():
    print("Run the daily orders workflow")

if __name__ == "__main__":
    daily_orders()
```

A flow normally represents a meaningful unit of orchestration.

Examples:

- daily order ingestion;
- customer synchronization;
- warehouse refresh;
- source validation;
- partition backfill;
- feature-data preparation.

---

## 4.3 Task

A **task** is a meaningful unit of work managed by Prefect.

```python
from prefect import task

@task
def extract_orders():
    return ["order-1", "order-2"]
```

Tasks provide an operational boundary around work.

A task can have its own:

- state;
- logs;
- retries;
- timeout;
- cache behavior;
- execution;
- result.

---

## 4.4 Flow Run

A flow definition is code.

A **flow run** is an actual execution of that flow.

For example:

```text
Flow definition:
    daily_orders

Runs:
    daily_orders / 2026-10-01
    daily_orders / 2026-10-02
    daily_orders / 2026-10-03
```

The flow is the reusable definition.

The flow run is one occurrence.

---

## 4.5 Task Run

Similarly, a task definition can execute many times.

```text
Task:
    extract_source

Task runs:
    extract_source / source_a
    extract_source / source_b
    extract_source / source_c
```

When mapped work is used, this distinction becomes particularly important.

---

## 4.6 State

A state describes the orchestration status of work.

The practical states emphasized in this topic include:

- pending;
- running;
- completed;
- failed;
- cached;
- crashed.

Conceptually:

```text
Pending
   ↓
Running
   ↓
Completed
```

or:

```text
Pending
   ↓
Running
   ↓
Failed
   ↓
Retry
   ↓
Running
```

A state is orchestration metadata.

It is **not automatically the source of truth for the underlying business data**.

---

## 4.7 Parameters

Parameters are inputs to a flow.

```python
from prefect import flow

@flow
def ingest_orders(execution_date: str, source: str):
    print(execution_date, source)
```

Parameters make workflow behavior explicit.

---

## 4.8 Deployment

A deployment connects flow code with operational execution configuration.

A deployment can define or associate:

- how the flow is triggered;
- schedule;
- parameters;
- work pool;
- execution environment;
- operational metadata.

Think:

```text
Flow code
    +
Deployment configuration
    =
Operational workflow
```

---

## 4.9 Worker

A worker is an execution-side process that obtains work according to the configured Prefect deployment/work-pool model and starts flow execution.

A worker is not the workflow definition.

---

## 4.10 Work Pool

A work pool is an infrastructure abstraction used to associate deployments with an execution model.

Conceptually:

```text
Deployment
    ↓
Work Pool
    ↓
Worker / execution infrastructure
    ↓
Flow Run
```

The exact infrastructure underneath can vary.

---

## 4.11 Server/UI

Prefect's server/UI layer provides operational visibility.

Engineers use it to inspect:

- flow runs;
- task runs;
- states;
- logs;
- failures;
- retries;
- durations;
- deployment information;
- operational history.

---

## 4.12 Schedule

A schedule determines when runs should be created according to time-based rules.

Examples:

```text
Every 15 minutes
Every hour
Every day at 02:00
Cron expression
```

A schedule answers:

> "When should this run happen?"

It does not necessarily answer:

> "Is the data ready?"

---

## 4.13 Events and Automations

An event represents something that happened.

For example:

```text
Ingestion completed
       ↓
     event
       ↓
  automation
       ↓
Start downstream processing
```

An event-driven system can react to external or internal occurrences rather than only checking the clock.

---

## 4.14 Results and Persistence

Tasks can produce results.

But a production orchestrator should usually pass **small control-plane information**, not huge datasets.

Prefer:

```python
@task
def extract():
    path = "s3://bucket/orders/date=2026-10-01/"
    return path
```

over:

```python
@task
def extract():
    return huge_dataframe
```

The data belongs in a data system.

The orchestrator should normally carry:

- identifiers;
- paths;
- partition keys;
- row counts;
- status;
- metadata;
- references.

---

# 5. Ordinary Python vs Flow vs Task

## 5.1 Ordinary Function

```python
def extract():
    return ["a", "b"]
```

This is just Python.

It does not automatically gain orchestration behavior.

---

## 5.2 Task

```python
from prefect import task

@task
def extract():
    return ["a", "b"]
```

Prefect can now manage execution of this operation as a task run.

---

## 5.3 Flow

```python
from prefect import flow

@flow
def pipeline():
    print("coordinate workflow")
```

The function becomes a flow boundary.

---

## 5.4 Flow Calling Tasks

```python
from prefect import flow, task

@task
def extract():
    return ["a", "b"]

@task
def transform(rows):
    return [row.upper() for row in rows]

@flow
def pipeline():
    rows = extract()
    transformed = transform(rows)
    print(transformed)

if __name__ == "__main__":
    pipeline()
```

The important conceptual distinction is:

```text
Flow = workflow boundary
Task = meaningful managed work
```

---

# 6. Flows

## 6.1 First Flow

```python
from prefect import flow

@flow
def hello_prefect():
    print("Hello, Prefect!")

if __name__ == "__main__":
    hello_prefect()
```

This demonstrates the minimum flow concept.

---

## 6.2 Parameterized Flow

```python
from prefect import flow

@flow
def greet(name: str):
    print(f"Hello, {name}!")

if __name__ == "__main__":
    greet("Data Engineer")
```

The flow is reusable because the input is explicit.

---

## 6.3 Flow Calling Ordinary Functions

Prefect does not require every function to become a task.

```python
from prefect import flow

def normalize_name(name: str) -> str:
    return name.strip().lower()

@flow
def normalize_flow(name: str):
    normalized = normalize_name(name)
    print(normalized)

if __name__ == "__main__":
    normalize_flow(" Alice ")
```

This is useful when the function is simply local business logic and does not need a separate orchestration boundary.

---

## 6.4 Flow Calling Tasks

```python
from prefect import flow, task

@task
def extract():
    return ["alice", "bob"]

@task
def transform(rows: list[str]):
    return [row.upper() for row in rows]

@flow
def pipeline():
    rows = extract()
    transformed = transform(rows)
    print(transformed)

if __name__ == "__main__":
    pipeline()
```

Now Prefect has task-level operational boundaries.

---

## 6.5 Multiple Dependent Tasks

```python
from prefect import flow, task

@task
def extract() -> list[str]:
    return ["order-1", "order-2"]

@task
def validate(rows: list[str]) -> list[str]:
    if not rows:
        raise ValueError("No rows extracted")
    return rows

@task
def transform(rows: list[str]) -> list[str]:
    return [row.upper() for row in rows]

@task
def load(rows: list[str]) -> None:
    print(f"Loading {len(rows)} rows")

@flow
def orders_pipeline():
    rows = extract()
    valid = validate(rows)
    transformed = transform(valid)
    load(transformed)

if __name__ == "__main__":
    orders_pipeline()
```

Conceptually:

```text
extract
   ↓
validate
   ↓
transform
   ↓
load
```

---

# 7. Nested Flows / Subflows

A flow can call another flow when a separate workflow boundary is useful.

Conceptually:

```text
Parent flow
    ↓
Ingestion subflow
    ↓
Validation subflow
    ↓
Publication subflow
```

Use subflows when the nested workflow has a meaningful lifecycle of its own.

Do not create subflows merely to make a diagram look complicated.

A good question is:

> "Does this unit deserve independent operational visibility and lifecycle?"

If yes, a subflow may be useful.

If not, an ordinary function or task may be simpler.

---

# 8. Flow Parameters

## 8.1 Basic Parameters

```python
from prefect import flow

@flow
def ingest_orders(execution_date: str, source: str):
    print(execution_date, source)
```

Call:

```python
ingest_orders(
    execution_date="2026-10-01",
    source="orders_api",
)
```

---

## 8.2 Why Type Hints Matter

Compare:

```python
@flow
def ingest_orders(execution_date, source):
    ...
```

with:

```python
@flow
def ingest_orders(execution_date: str, source: str):
    ...
```

The typed version communicates the intended contract.

For production orchestration, explicit contracts make invalid execution easier to detect.

---

## 8.3 Default Values

```python
from prefect import flow

@flow
def ingest_orders(
    source: str,
    execution_date: str = "2026-10-01",
):
    print(source, execution_date)
```

Defaults can be useful for local development.

For production, avoid defaults that silently cause processing of the wrong partition.

---

## 8.4 Structured Parameters

For complex inputs, define an explicit model.

Depending on the Prefect version and supported parameter serialization behavior, Pydantic models can be used to define structured validation at the Python boundary.

Example:

```python
from pydantic import BaseModel
from prefect import flow

class IngestConfig(BaseModel):
    source: str
    execution_date: str
    batch_size: int = 1000

@flow
def ingest(config: IngestConfig):
    print(config.source)
    print(config.execution_date)
    print(config.batch_size)
```

The important engineering idea is not the framework syntax.

It is:

```text
Unclear input
    ↓
implicit assumptions
    ↓
hard-to-debug production behavior
```

versus:

```text
Explicit input contract
    ↓
validation
    ↓
predictable execution
```

---

## 8.5 Invalid Parameters

A production flow should reject invalid inputs early.

Examples:

```text
execution_date is empty
batch_size <= 0
source is unknown
environment is invalid
```

Failing early is usually safer than allowing an invalid value to travel through multiple tasks.

---

# 9. Logging

## 9.1 Why Logs Matter

A failed flow is only useful to an engineer if the engineer can understand what happened.

Useful logs answer:

- Which source?
- Which partition?
- Which run?
- Which operation?
- How many records?
- How long did it take?
- What external system failed?
- What error class occurred?

---

## 9.2 Prefect Logging

A typical task can use Prefect's logger:

```python
from prefect import task, get_run_logger

@task
def extract(source: str):
    logger = get_run_logger()

    logger.info("Starting extraction for source=%s", source)

    rows = ["a", "b", "c"]

    logger.info(
        "Completed extraction source=%s rows=%d",
        source,
        len(rows),
    )

    return rows
```

The exact logger behavior and UI presentation can depend on the Prefect execution environment, but the production principle remains:

> Log operationally useful facts at the correct level.

---

## 9.3 What to Log

Good examples:

```text
source=orders_api
partition=2026-10-01
rows_extracted=15234
duration_seconds=18.2
attempt=2
```

---

## 9.4 What Not to Log

Do not log:

- API keys;
- passwords;
- access tokens;
- private credentials;
- full sensitive customer records;
- large payloads;
- unnecessary personal information.

Bad:

```python
logger.info("API response=%s", response.text)
```

Better:

```python
logger.info(
    "API request completed source=%s status=%s rows=%d",
    source,
    response.status_code,
    row_count,
)
```

---

# 10. Retries

Retries are one of the most important orchestration features.

## 10.1 Transient vs Permanent Failure

### Transient

A transient failure may disappear if the operation is attempted again.

Examples:

- temporary network failure;
- HTTP 503;
- temporary database connection issue;
- object-store timeout;
- temporary rate-limit response.

### Permanent

A permanent failure will not be fixed by repeating the same request.

Examples:

- invalid credentials;
- malformed SQL;
- missing required column;
- invalid configuration;
- unsupported schema;
- deterministic application bug.

---

## 10.2 Basic Task Retry

Prefect tasks can be configured with retry behavior.

Example:

```python
from prefect import task

@task(
    retries=3,
    retry_delay_seconds=10,
)
def fetch_api():
    ...
```

The exact retry strategy should be selected according to the failure mode and current Prefect 3 API capabilities.

---

## 10.3 Retry Delay

Without delay:

```text
Failure
 ↓
Retry immediately
 ↓
Failure
 ↓
Retry immediately
```

This can make an outage worse.

A delay provides recovery time.

---

## 10.4 Exponential Backoff

Conceptually:

```text
Attempt 1 → wait 1 second
Attempt 2 → wait 2 seconds
Attempt 3 → wait 4 seconds
Attempt 4 → wait 8 seconds
```

The exact implementation should be based on the current Prefect API rather than copied from an outdated tutorial.

---

## 10.5 Retry + Idempotency

This is a critical production relationship:

> **RETRY + NON-IDEMPOTENT TASK = POTENTIAL DATA CORRUPTION**

Suppose:

```text
Task writes 1,000 rows
        ↓
Database commit succeeds
        ↓
Network response is lost
        ↓
Task appears to fail
        ↓
Prefect retries
        ↓
Same 1,000 rows are written again
```

If the write is not idempotent, duplicates can occur.

---

## 10.6 Retry-Safe Design

Use mechanisms such as:

- deterministic batch identifiers;
- unique constraints;
- merge/upsert;
- staging tables;
- transactional commit boundaries;
- object-store paths derived from partition identity;
- write-once partition conventions;
- deduplication keys.

Example:

```text
source = orders_api
partition = 2026-10-01
batch_id = orders_api:2026-10-01
```

A retry can safely target the same logical batch.

---

# 11. Timeouts

## 11.1 Why Timeouts Exist

Without a timeout, a task may remain active indefinitely.

Examples:

- API connection hangs;
- database query stalls;
- socket remains open;
- worker process is blocked;
- external dependency stops responding.

A timeout converts:

```text
Unknown duration
```

into:

```text
Maximum acceptable duration
```

---

## 11.2 Task Timeout

A task can be configured with a timeout according to the current Prefect 3 task API.

Conceptually:

```python
@task(timeout_seconds=300)
def extract():
    ...
```

The precise supported signature should be checked against the installed Prefect version.

---

## 11.3 Timeout vs Retry

They solve different problems.

```text
Timeout
    =
"This execution has taken too long."

Retry
    =
"Try the operation again."
```

They can work together:

```text
Task starts
   ↓
runs 300 seconds
   ↓
timeout
   ↓
failure
   ↓
retry
```

---

## 11.4 Timeout + Retry Timeline

Suppose:

- timeout = 5 minutes;
- retries = 2;
- delay = 30 seconds.

A worst-case execution can be approximately:

```text
Attempt 1
  5 min
  ↓
30 sec delay

Attempt 2
  5 min
  ↓
30 sec delay

Attempt 3
  5 min

≈ 16 minutes total
```

Therefore, retries and timeouts must be considered together when defining an operational deadline.

---

# 12. Caching

## 12.1 What Is Caching?

Caching means reusing an existing result instead of recomputing the same work when the cache conditions indicate that the result is still valid.

Conceptually:

```text
Input
  ↓
Cache key
  ↓
Existing valid result?
  ├── yes → reuse
  └── no  → execute task
```

---

## 12.2 Why Caching Exists

Caching can reduce:

- API calls;
- expensive computation;
- repeated database queries;
- unnecessary file processing;
- execution time.

---

## 12.3 Caching Is Not Retry

Retry:

```text
Failure
 ↓
Try again
```

Caching:

```text
Equivalent prior result exists
 ↓
Reuse it
```

---

## 12.4 Caching Is Not Persistence

Persistence means a result/state is retained.

Caching adds a semantic question:

> "Can this prior result be reused for this input now?"

A persisted result may exist without being valid for reuse.

---

## 12.5 Caching and Deterministic Inputs

Caching is safer when task output is a deterministic function of explicit inputs.

```text
output = f(source, partition)
```

is easier to cache safely than:

```text
output = f(current_time, external mutable state, hidden configuration)
```

---

## 12.6 Cache Invalidation

A classic problem:

```text
Cached result
     ↓
Source data changes
     ↓
Cache still says "valid"
     ↓
Stale result reused
```

Therefore ask:

- What defines freshness?
- What changes the cache key?
- How long is the result valid?
- Does external state affect correctness?

---

## 12.7 When Not to Cache

Avoid caching when:

- data changes frequently;
- correctness requires the newest state;
- cache invalidation is unreliable;
- side effects are involved;
- inputs are hidden;
- the task is cheap;
- stale data is dangerous.

---

# 13. Concurrency

## 13.1 Sequential Execution

Suppose:

```text
A = 10 seconds
B = 10 seconds
C = 10 seconds
```

Sequential:

```text
A ──────────
            B ──────────
                        C ──────────

≈ 30 seconds
```

If A, B, and C are independent, concurrency may reduce elapsed time.

---

## 13.2 Concurrent Execution

Conceptually:

```text
A ──────────
B ──────────
C ──────────

≈ 10 seconds
```

Actual performance depends on:

- task runner;
- CPU;
- network;
- external system;
- concurrency limits;
- scheduling overhead.

---

# 14. `.submit()` and Futures

A task call can execute synchronously from the flow's perspective:

```python
result = task_a()
```

With `.submit()`:

```python
future = task_a.submit()
```

the flow receives a future representing deferred task execution.

---

## 14.1 Independent Tasks

```python
from prefect import flow, task

@task
def extract_a():
    return "A"

@task
def extract_b():
    return "B"

@task
def transform(a: str, b: str):
    return f"{a}-{b}"

@flow
def pipeline():
    a = extract_a.submit()
    b = extract_b.submit()

    combined = transform.submit(a, b)

    return combined
```

Conceptually:

```text
extract_a ─┐
            ├── transform ── result
extract_b ─┘
```

A and B can run concurrently.

`transform` waits for the results it depends on.

---

## 14.2 Future Dependency Propagation

The important mental model is:

```text
future_a
future_b
   ↓
task C consumes both
   ↓
C cannot correctly execute until required inputs are available
```

This lets Prefect represent dependencies while allowing independent work to overlap.

---

# 15. Task Runners

A task runner controls how task execution is coordinated for a flow.

Conceptually:

```text
Flow
  ↓
Task runner
  ↓
Task execution
```

Task runners exist because:

- tasks may need concurrency;
- execution may need a particular model;
- resources need to be considered;
- execution behavior should be separated from workflow logic.

Prefect 3 provides task-runner implementations appropriate to different execution needs; the default and available runners can depend on the installed Prefect version and environment.

Do not treat the task runner as an unlimited compute engine.

---

## 15.1 Appropriate Use

For a small set of network-bound operations, concurrent task execution may be useful.

For heavy distributed computation, use the appropriate processing system instead:

```text
Prefect
  ↓
submit/coordinate
  ↓
Spark / warehouse / database / compute cluster
```

rather than:

```text
Prefect
  ↓
try to become Spark
```

---

# 16. Mapping / Mapped Work

Mapped work applies one task definition to many input items.

Suppose:

```text
source_1
source_2
source_3
...
source_N
```

Instead of manually creating separate functions:

```python
extract_source_1()
extract_source_2()
extract_source_3()
```

use one task definition.

The conceptual model is:

```text
                 ┌── source_1
                 ├── source_2
extract task ────┼── source_3
                 ├── ...
                 └── source_N
```

Prefect versions provide mapping facilities around task execution; use the current installed Prefect 3 API rather than assuming older examples are unchanged.

---

## 16.1 Why Mapping Exists

Mapping is useful for:

- multiple APIs;
- multiple files;
- partitions;
- tenants;
- tables;
- independent source systems.

---

## 16.2 Dynamic Workload Size

A key advantage is that the number of items can vary.

```text
Monday:
10 sources

Tuesday:
14 sources

Wednesday:
7 sources
```

The workflow definition does not need one hard-coded task per source.

---

## 16.3 Mapping + Concurrency

Mapping does **not** mean unlimited concurrency.

Bad:

```text
500 sources
   ↓
500 simultaneous API calls
```

Better:

```text
500 sources
   ↓
mapped tasks
   ↓
concurrency limit = 5
   ↓
5 active API calls
```

This protects the external system and the worker.

---

## 16.4 Partial Failure

Suppose 20 mapped tasks run:

```text
17 completed
2 retried and completed
1 failed permanently
```

The engineer must distinguish:

- successful work;
- retrying work;
- failed work.

A production rerun should not blindly duplicate the 17 successful operations.

This is why idempotency and explicit source/partition identity matter.

---

# 17. States

## 17.1 Core State Model

Conceptually:

```text
Pending
   ↓
Running
   ↓
Completed
```

Failure:

```text
Running
   ↓
Failed
   ↓
Retry
   ↓
Running
```

Caching can produce:

```text
Pending
   ↓
Cache evaluation
   ↓
Cached
```

A crash may produce a state indicating that execution ended unexpectedly.

---

## 17.2 Task State vs Flow State

A flow can contain many tasks.

For example:

```text
Task A → Completed
Task B → Completed
Task C → Failed
```

The flow may therefore be unsuccessful even though some tasks completed.

This distinction matters during debugging.

---

## 17.3 State Is Not Business Truth

Suppose:

```text
Load task = Completed
```

That does not automatically prove:

```text
Warehouse has correct data.
```

The data system and quality checks remain the source of truth for business correctness.

---

# 18. Results and Persistence

## 18.1 Small Results

Reasonable task results include:

```python
{
    "source": "orders_api",
    "partition": "2026-10-01",
    "path": "s3://bucket/orders/date=2026-10-01/",
    "rows": 15234,
}
```

---

## 18.2 Large Results

Avoid:

```python
return huge_dataframe
```

when the dataframe is very large.

Prefer:

```python
return "s3://bucket/orders/date=2026-10-01/"
```

or a table identifier.

---

## 18.3 Orchestration Boundary

The boundary should often look like:

```text
                 DATA PLANE
API ──→ Object Store ──→ Warehouse
                 ↑
                 │
          data references

                 CONTROL PLANE
              Prefect
                 │
       task states / logs
       dependencies / retries
       parameters / triggers
```

This separation improves scalability.

---

# 19. State Hooks

State hooks can be used for operational reactions to state changes.

Examples:

- failure notifications;
- success metrics;
- audit events;
- operational counters.

A conceptual example:

```python
def on_failure(flow, flow_run, state):
    print(
        f"Flow failed: {flow_run.id}; "
        f"state={state.type}"
    )
```

The exact hook signature depends on the Prefect 3 API version in use, so verify it against the installed version before production implementation.

---

## 19.1 Avoid Notification Storms

Bad design:

```text
500 mapped tasks
   ↓
500 failure notifications
```

Better:

```text
individual task failures
        ↓
aggregate operational signal
        ↓
one actionable notification
```

Use hooks for meaningful operational behavior, not noise.

---

# 20. Deployments

## 20.1 Code vs Deployment

A flow answers:

> What work should happen?

A deployment answers:

> How and when should that flow be operated?

Think:

```text
Flow code
    ↓
Deployment
    ├── schedule
    ├── parameters
    ├── work pool
    └── execution configuration
```

---

## 20.2 Local Development

A common development loop is:

```text
Write flow
   ↓
Run locally
   ↓
Inspect logs
   ↓
Inject failure
   ↓
Fix
   ↓
Test
```

Do not start with production deployment before understanding the flow locally.

---

# 21. `serve()` vs `deploy()`

Prefect 3 provides multiple deployment-oriented approaches.

The practical distinction is:

### `serve()`

A flow can be served in a relatively direct way from a running Python process.

Conceptually:

```text
Python process
   ↓
flow.serve(...)
   ↓
schedule / listen for work
   ↓
execute flow
```

This is useful for simpler operational setups where keeping a serving process alive is acceptable.

### `deploy()`

A deployment-oriented approach separates the flow definition from the infrastructure used to execute runs.

Conceptually:

```text
Flow code
   ↓
Deployment
   ↓
Work pool
   ↓
Worker / infrastructure
   ↓
Flow run
```

This becomes useful when infrastructure and application code need stronger separation.

> **Version note:** Prefect 3 APIs evolve. Treat exact method arguments and infrastructure configuration as version-specific. Verify the installed Prefect version before copying deployment commands into production.

---

# 22. Work Pools and Workers

## 22.1 Architecture

```text
Deployment
    ↓
Work Pool
    ↓
Worker
    ↓
Execution Environment
    ↓
Flow Run
    ↓
Tasks
```

---

## 22.2 Why This Separation Exists

It allows workflow code to be separated from the environment that executes it.

For example:

```text
Same flow
   ↓
Development work pool
   ↓
local execution
```

and:

```text
Same flow
   ↓
Production work pool
   ↓
container/cloud execution
```

The exact infrastructure depends on the configured work-pool type.

---

## 22.3 Worker Failure

Suppose:

```text
Deployment exists
        ↓
Worker crashes
        ↓
No execution capacity
```

The deployment definition has not necessarily disappeared.

The operational issue is execution capacity.

Debug:

1. Is the deployment active?
2. Is the work pool available?
3. Is the worker running?
4. Can the worker obtain work?
5. Does the worker have required credentials?
6. Is the execution environment healthy?
7. Is the task itself failing after execution begins?

---

# 23. Scheduling

Scheduling answers:

> When should a run be created?

Examples:

```text
Every hour
Every day at 02:00
Every 15 minutes
Cron-style schedule
```

---

## 23.1 Schedule-Driven Execution

```text
Clock
  ↓
Schedule matches
  ↓
Flow run created
  ↓
Worker executes
```

---

## 23.2 Event-Driven Execution

```text
External event
  ↓
Event received
  ↓
Automation condition
  ↓
Flow triggered
```

---

## 23.3 Schedule Is Not Data Readiness

This is a common production mistake:

```text
Every day at 02:00
```

does not mean:

```text
The source data will definitely be ready at 02:00.
```

A robust design may require:

- event trigger;
- readiness check;
- sensor/polling logic;
- upstream completion signal;
- bounded waiting;
- timeout and failure behavior.

---

# 24. Events and Automations

## 24.1 Event

An event is a representation of something that happened.

Examples:

```text
ingestion.completed
file.arrived
upstream.pipeline.completed
quality.check.failed
```

---

## 24.2 Automation

An automation evaluates an event or condition and performs a follow-up action.

Conceptually:

```text
Event
  ↓
Condition
  ↓
Automation
  ↓
Action
```

Example:

```text
ingestion.completed
        ↓
automation
        ↓
start transformation flow
```

---

## 24.3 Schedule vs Polling vs Event vs Automation

| Mechanism | Meaning |
|---|---|
| Schedule | Time says when to run |
| Polling | Repeatedly check whether a condition is true |
| Event | Something happened |
| Automation | React to an event/condition with an action |

Use the mechanism that matches the actual dependency.

---

# 25. Blocks and Variables

Production code should separate:

```text
CODE
≠
CONFIGURATION
≠
SECRET
```

---

## 25.1 Bad Design

```python
DATABASE_PASSWORD = "super-secret-password"
```

Never hard-code credentials into source code.

---

## 25.2 Configuration

Configuration may include:

```text
API endpoint
bucket name
environment
batch size
schema name
timeout
```

---

## 25.3 Secrets

Secrets include:

```text
password
API key
access token
private credential
```

Use the appropriate secret-management mechanism rather than treating secrets as ordinary source-code configuration.

---

## 25.4 Blocks

Blocks can represent reusable configuration/integration objects in Prefect.

The production principle is:

```text
environment-specific configuration
        ↓
external configuration mechanism
        ↓
flow code remains portable
```

---

## 25.5 Variables

Variables can hold configuration values that do not belong in source code.

Do not use Variables as an uncontrolled dumping ground for secrets.

---

# 26. Transaction Awareness

Orchestration does not make an external operation transactional.

Consider:

```text
Task
 ↓
INSERT 10,000 rows
 ↓
database commit
 ↓
network connection drops
 ↓
task reports failure
 ↓
Prefect retries
 ↓
same rows inserted again
```

The orchestrator did exactly what it was configured to do.

The underlying data operation was not retry-safe.

---

## 26.1 Commit Boundaries

Design clear commit boundaries:

```text
Extract
  ↓
validate
  ↓
stage
  ↓
transaction
  ↓
merge
  ↓
commit
```

---

## 26.2 Idempotent Database Pattern

Suppose:

```text
batch_id = orders_api:2026-10-01
```

The database can enforce uniqueness:

```text
batch_id unique
```

Then a retry can detect that the batch already exists.

Other approaches include:

- upsert;
- merge;
- staging + atomic promotion;
- partition replacement;
- deterministic object paths.

---

# 27. End-to-End Data Engineering Pipeline

Consider:

```text
                 ┌─────────────┐
                 │ Source APIs │
                 └──────┬──────┘
                        ↓
                   Ingestion
                        ↓
                  Raw storage
                        ↓
                    Validation
                        ↓
                   Transformation
                        ↓
                 Database/Warehouse
                        ↓
                  Quality checks
                        ↓
                     Publish
```

Prefect coordinates the workflow.

It does not replace:

- the APIs;
- object storage;
- database;
- warehouse;
- transformation engine;
- quality framework.

---

## 27.1 Progressive Implementation

Start:

```python
from prefect import flow

@flow
def ingest_sources():
    print("ingest sources")

if __name__ == "__main__":
    ingest_sources()
```

Then add tasks:

```python
from prefect import flow, task

@task
def ingest_source(source: str):
    print(f"Ingesting {source}")
    return source

@flow
def ingest_sources(sources: list[str]):
    for source in sources:
        ingest_source(source)

if __name__ == "__main__":
    ingest_sources(["orders", "customers"])
```

Then introduce concurrency only when there is a reason.

---

# 28. Roadmap Hands-On Lab — `ingest_sources`

The required practical system is:

> An `ingest_sources` flow that maps over multiple sources, uses retries, timeouts, caching, concurrency, deployment concepts, and automation chaining after ingestion.

Do not build the final system in one step.

---

## 28.1 Step 1 — Simplest Working Flow

```python
from prefect import flow

@flow
def ingest_sources(sources: list[str]):
    for source in sources:
        print(f"Ingesting {source}")

if __name__ == "__main__":
    ingest_sources(
        ["orders", "customers", "products"]
    )
```

Run it.

Confirm:

- the flow starts;
- parameters are visible;
- logs are readable.

---

## 28.2 Step 2 — Extract Task

```python
from prefect import flow, task

@task
def extract_source(source: str) -> dict:
    print(f"Extracting {source}")

    return {
        "source": source,
        "rows": 100,
        "path": f"s3://raw/{source}/",
    }

@flow
def ingest_sources(sources: list[str]):
    for source in sources:
        extract_source(source)

if __name__ == "__main__":
    ingest_sources(
        ["orders", "customers", "products"]
    )
```

---

## 28.3 Step 3 — Retry

```python
@task(
    retries=3,
    retry_delay_seconds=10,
)
def extract_source(source: str):
    ...
```

Now transient failures can be retried.

But retry safety must be evaluated before production use.

---

## 28.4 Step 4 — Timeout

Conceptually:

```python
@task(
    retries=3,
    retry_delay_seconds=10,
    timeout_seconds=300,
)
def extract_source(source: str):
    ...
```

Now a permanently hanging call does not consume execution forever.

---

## 28.5 Step 5 — Concurrent Submission

```python
from prefect import flow, task

@task
def extract_source(source: str):
    print(f"Extracting {source}")
    return source

@flow
def ingest_sources(sources: list[str]):
    futures = [
        extract_source.submit(source)
        for source in sources
    ]

    return futures
```

Independent source extractions can now overlap according to the configured task runner and resource constraints.

---

## 28.6 Step 6 — Mapped Work

Use the current Prefect 3 mapping facility supported by your installed version to apply one task definition across the source collection.

Conceptually:

```text
sources
   ↓
mapped extract task
   ├── orders
   ├── customers
   ├── products
   └── ...
```

Verify the exact mapping syntax against the installed Prefect version before production use.

---

## 28.7 Step 7 — Bounded Concurrency

Suppose:

```text
500 sources
```

but the API allows:

```text
5 requests at a time
```

The design should be:

```text
500 mapped inputs
       ↓
bounded execution
       ↓
5 concurrent requests
```

The exact concurrency-limit mechanism should be selected according to the Prefect 3 deployment and infrastructure model.

---

## 28.8 Step 8 — Caching

Identify a task where reuse is correct.

For example:

```text
Fetch static reference metadata
```

Do not automatically cache:

```text
real-time order ingestion
```

because stale data may violate correctness.

---

## 28.9 Step 9 — Deployment

Move from:

```text
python ingest.py
```

to an operational deployment model:

```text
Flow
 ↓
Deployment
 ↓
Work pool
 ↓
Worker
 ↓
Scheduled run
```

---

## 28.10 Step 10 — Automation Chaining

After successful ingestion:

```text
ingest_sources
      ↓
ingestion.completed
      ↓
automation
      ↓
transform_sources
```

This separates:

- ingestion;
- transformation;
- trigger logic.

---

# 29. Failure Injection

Production understanding requires breaking the workflow intentionally.

---

## 29.1 Failure 1 — Temporary API Failure

Inject:

```python
if first_attempt:
    raise RuntimeError("temporary API outage")
```

Expected reasoning:

```text
Task fails
 ↓
retry policy evaluates
 ↓
retry
 ↓
success
```

Questions:

- Was the error transient?
- Is the task idempotent?
- Did the retry occur?
- What does the run history show?

---

## 29.2 Failure 2 — Authentication Failure

Inject:

```text
HTTP 401 / invalid credentials
```

Do not blindly retry indefinitely.

Why?

Because:

```text
Invalid credential
 ≠
temporary network failure
```

Fix configuration or credentials.

---

## 29.3 Failure 3 — Database Timeout

Inject a database operation that exceeds the timeout.

Expected:

```text
Task running
 ↓
timeout
 ↓
failure
 ↓
retry if configured
```

But ensure the database operation itself is safe to retry.

---

## 29.4 Failure 4 — One Mapped Source Fails

Suppose:

```text
20 sources
19 succeed
1 fails
```

Inspect the individual task runs.

The goal is to avoid treating the entire batch as an undifferentiated blob.

---

## 29.5 Failure 5 — Timeout

Cause one task to sleep longer than its timeout.

Observe:

- task state;
- logs;
- retry behavior;
- elapsed time.

---

## 29.6 Failure 6 — Bad Cache

Change an upstream value while leaving the cache condition unchanged.

Ask:

> Why was stale data reused?

Then change the cache-key/freshness strategy.

---

## 29.7 Failure 7 — Worker Unavailable

Stop the worker or otherwise remove execution capacity.

Observe the difference between:

```text
workflow exists
```

and:

```text
workflow can currently execute
```

---

## 29.8 Failure 8 — Flow Crash

Cause an unhandled exception.

Inspect:

```text
Flow state
Task state
Logs
Input parameters
External system
```

---

## 29.9 Failure 9 — Retry Eventually Succeeds

Create:

```text
Attempt 1 → fail
Attempt 2 → fail
Attempt 3 → success
```

Verify that the underlying operation did not create duplicate side effects.

---

## 29.10 Failure 10 — Retry Eventually Fails

Create:

```text
Attempt 1 → fail
Attempt 2 → fail
Attempt 3 → fail
```

Now determine:

- final state;
- notification behavior;
- safe recovery strategy;
- whether a manual rerun is required.

---

# 30. Caching + Retry + Concurrency Interaction

These mechanisms are independent but interact.

Conceptually:

```text
Mapped tasks
    ↓
Concurrency limit
    ↓
Task execution
    ↓
Failure
    ↓
Retry
    ↓
Cache evaluation
    ↓
Completion
```

A common mistake is to reason about each feature in isolation.

---

## 30.1 Example

Suppose:

```text
100 mapped sources
concurrency = 5
retries = 3
cache enabled
```

Source 17 fails transiently.

Possible lifecycle:

```text
Source 17
   ↓
attempt 1
   ↓
failure
   ↓
retry
   ↓
attempt 2
   ↓
success
```

Meanwhile:

```text
sources 1–5
sources 6–10
...
```

continue within the concurrency boundary.

---

## 30.2 Operational Questions

Ask:

1. Can the task be safely retried?
2. Can the task be safely cached?
3. What is the cache key?
4. Does the external source have rate limits?
5. Can a retry exceed the source's quota?
6. Does a failed mapped task block downstream work?
7. How do we rerun only failed sources?
8. Where is the authoritative data state stored?

---

# 31. Observability

When a pipeline fails, use a disciplined workflow.

```text
Flow failed
    ↓
Inspect flow state
    ↓
Identify failed task
    ↓
Inspect task state
    ↓
Inspect logs
    ↓
Determine failure class
    ↓
Check retry history
    ↓
Inspect parameters/inputs
    ↓
Inspect external dependency
    ↓
Fix root cause
    ↓
Rerun safely
```

---

## 31.1 Flow Run History

Look for:

- start time;
- end time;
- duration;
- state;
- parameters;
- deployment;
- worker/execution context.

---

## 31.2 Task Run History

Look for:

- task state;
- attempt number;
- duration;
- logs;
- failure message;
- mapped item/source;
- dependency behavior.

---

## 31.3 What Engineers Should Not Do

Do not start by rerunning blindly.

Bad:

```text
Failure
 ↓
rerun everything
```

Better:

```text
Failure
 ↓
understand root cause
 ↓
identify safe retry boundary
 ↓
rerun only what is necessary
```

---

# 32. Testing Prefect Flows and Tasks

Testing should exist at multiple levels.

## 32.1 Test Ordinary Python Logic

If business logic is:

```python
def normalize_amount(value: str) -> float:
    return float(value.strip())
```

test it as normal Python.

```python
def test_normalize_amount():
    assert normalize_amount(" 12.5 ") == 12.5
```

Do not require the full orchestration environment for every unit test.

---

## 32.2 Test Task Logic

A task can still be called in a test context.

The important idea is to test:

- valid inputs;
- invalid inputs;
- expected outputs;
- expected exceptions.

---

## 32.3 Test Flow Parameters

```python
def test_valid_source():
    ...
```

Test invalid cases:

```text
empty source
unknown source
invalid date
negative batch size
```

---

## 32.4 Test Failure Behavior

A production test suite should prove that:

```text
temporary failure → retry
permanent failure → fail
timeout → timeout/failure
```

---

## 32.5 Test Mapped Work

Test:

```text
3 inputs
3 expected task executions
1 intentionally failing input
```

Verify that successful inputs are not accidentally reprocessed during recovery.

---

## 32.6 Test Deployment Configuration

Where practical, validate:

- deployment exists;
- schedule is correct;
- parameters are valid;
- work pool is correct;
- required configuration is available.

---

# 33. Production Design Principles

## 33.1 Thin Orchestration

Prefer:

```text
Flow
 ↓
Task
 ↓
Reusable logic
 ↓
Data system
```

---

## 33.2 Reusable Business Logic

Example:

```python
def parse_orders(payload: dict) -> list[dict]:
    ...
```

Then:

```python
@task
def parse_orders_task(payload: dict):
    return parse_orders(payload)
```

This keeps the core logic testable.

---

## 33.3 Idempotent Tasks

A retry should not corrupt data.

Use:

- deterministic keys;
- upsert;
- merge;
- transactional boundaries;
- partition replacement;
- deduplication.

---

## 33.4 Bounded Concurrency

Always ask:

```text
How many concurrent operations can the source safely handle?
How much memory does each task require?
How much database connection capacity exists?
```

---

## 33.5 Meaningful Task Boundaries

A good task represents meaningful work.

Examples:

```text
extract_source
validate_batch
transform_partition
load_partition
run_quality_checks
```

---

## 33.6 Avoid Micro-Tasks

Bad:

```text
@task
def add_one():
    return 1
```

repeated thousands of times merely to create a graph.

The orchestration overhead may exceed the work.

---

## 33.7 Explicit Parameters

Prefer:

```text
source
partition
environment
batch identifier
```

over hidden global variables.

---

## 33.8 Safe Retries

Only retry errors that can reasonably recover.

---

## 33.9 Controlled Timeouts

Every external call should have a sensible maximum duration.

---

## 33.10 Appropriate Caching

Cache only when correctness permits reuse.

---

## 33.11 Small Orchestration Results

Pass:

```text
paths
IDs
counts
metadata
```

rather than huge dataframes.

---

## 33.12 Secrets Outside Source Code

Never:

```python
PASSWORD = "..."
```

---

## 33.13 Structured Logs

Include:

```text
source
partition
batch_id
rows
duration
attempt
```

---

## 33.14 Deterministic Processing

For a given:

```text
source + partition + code/config version
```

the workflow should produce predictable outcomes.

---

## 33.15 Failure Isolation

A failure in one source should not unnecessarily destroy unrelated successful work.

---

# 34. Common Anti-Patterns

## 34.1 All Logic Inside `@flow`

**BAD DESIGN**

```python
@flow
def pipeline():
    # extraction
    # validation
    # transformation
    # database writes
    # notifications
    # hundreds of lines
```

**WHY IT IS BAD**

The orchestration boundary becomes difficult to test, observe, and maintain.

**BETTER DESIGN**

```text
flow
 ↓
meaningful tasks
 ↓
reusable business logic
```

---

## 34.2 Giant Tasks

**BAD**

```text
one task = entire company pipeline
```

**Failure mode**

A failure has a huge recovery boundary.

**Better**

Split by meaningful operational units.

---

## 34.3 Hundreds of Meaningless Micro-Tasks

**BAD**

```text
one task for every trivial Python statement
```

**Failure mode**

Excessive orchestration overhead and difficult debugging.

**Better**

Group coherent work.

---

## 34.4 Huge DataFrames as Task Results

**BAD**

```python
return huge_dataframe
```

**Failure mode**

Memory, serialization, transport, and persistence problems.

**Better**

```python
return "s3://bucket/path"
```

---

## 34.5 Unbounded Concurrency

**BAD**

```text
500 API sources
→ 500 simultaneous requests
```

**Failure mode**

Rate limits, connection exhaustion, worker overload.

**Better**

Bound concurrency.

---

## 34.6 Retrying Permanent Errors

**BAD**

```text
401 authentication failure
→ retry 10 times
```

**Failure mode**

Noise and wasted execution.

**Better**

Fix credentials/configuration.

---

## 34.7 Retrying Non-Idempotent Operations

**BAD**

```text
insert
→ uncertain result
→ retry insert
```

**Failure mode**

Duplicate data.

**Better**

Use idempotent writes.

---

## 34.8 Incorrect Caching

**BAD**

```text
rapidly changing data
→ long-lived cache
```

**Failure mode**

Stale data.

**Better**

Define freshness explicitly or do not cache.

---

## 34.9 Hard-Coded Credentials

**BAD**

```python
API_KEY = "secret"
```

**Failure mode**

Credential leakage.

**Better**

External secret/configuration mechanism.

---

## 34.10 Orchestration State as Data Truth

**BAD**

```text
Prefect says completed
→ therefore warehouse is correct
```

**Failure mode**

Operational state is confused with business correctness.

**Better**

Validate data using database/warehouse quality checks.

---

## 34.11 Hidden Failures

**BAD**

```python
try:
    ...
except Exception:
    pass
```

**Failure mode**

The workflow appears successful while work was lost.

**Better**

Fail explicitly and provide actionable logs.

---

## 34.12 Excessive Notifications

**BAD**

```text
one notification per mapped task failure
```

**Failure mode**

Alert fatigue.

**Better**

Aggregate actionable incidents.

---

## 34.13 No Timeout on External Calls

**BAD**

```text
HTTP request with no maximum duration
```

**Failure mode**

Hung workers.

**Better**

Set an appropriate timeout.

---

## 34.14 Deployment Without Resource Controls

**BAD**

```text
unbounded production execution
```

**Failure mode**

Infrastructure overload.

**Better**

Define concurrency, memory, CPU, connection, and external rate limits.

---

## 34.15 Confusing Schedule with Readiness

**BAD**

```text
Run at 02:00
therefore data must exist
```

**Failure mode**

Pipeline starts before upstream data is ready.

**Better**

Use readiness/event-driven design when necessary.

---

## 34.16 Treating Prefect as a Distributed Processing Engine

**BAD**

```text
Prefect
→ process terabytes directly inside orchestration tasks
```

**Failure mode**

Poor scalability and inappropriate architecture.

**Better**

```text
Prefect
→ coordinate
→ Spark / warehouse / database / compute platform
```

---

# 35. Prefect vs Airflow vs Dagster

This is a technical comparison, not a ranking.

| Dimension | Prefect | Airflow | Dagster |
|---|---|---|---|
| Primary model | Flows/tasks | DAGs/tasks/operators | Software-defined assets |
| Python style | Python-native workflow | Python-defined DAG | Python-native asset definitions |
| Task-centric work | Strong | Strong | Supported, but asset model is central |
| Asset-centric model | Can be represented | Possible through ecosystem/patterns | Central concept |
| Scheduling | Supported | Strong scheduling model | Supported |
| Dependencies | Python/task relationships | DAG dependencies | Asset/dependency relationships |
| Dynamic workflows | Strong Python flexibility | Dynamic task patterns | Asset and partition patterns |
| Deployment | Work pools/workers and related deployment models | Scheduler/executor/worker architecture | Code locations, daemon/webserver and deployment patterns |
| Observability | Flow/task run UI | DAG/task instance UI | Asset/run-oriented UI |
| Retries | Task-level patterns | Operator/task retry model | Op/asset execution retry patterns |
| Concurrency | Task execution and infrastructure controls | Executors/pools/concurrency controls | Executors/limits and infrastructure |
| Lineage | Workflow/task context | DAG/task-oriented | Asset lineage is central |
| Ecosystem | Python/cloud integrations | Very broad mature ecosystem | Strong data/asset ecosystem |
| Learning emphasis | Python workflows | DAG orchestration | Assets/data dependencies |
| Typical fit | Python-native workflow orchestration | Established DAG-centric platforms | Asset-centric data platforms |

The right selection depends on:

- existing platform;
- team expertise;
- workflow model;
- asset lineage requirements;
- infrastructure;
- ecosystem integrations;
- operational constraints;
- migration cost.

Do not select a tool because it is described as universally "best."

---

# 36. Prefect vs Cron

Cron is not inherently bad.

A simple job can be:

```text
cron
 ↓
python script
```

and be perfectly adequate.

---

## 36.1 Cron May Be Sufficient When

- one script;
- simple schedule;
- minimal dependencies;
- simple failure behavior;
- little operational history needed;
- one execution environment;
- manual recovery is acceptable.

Example:

```text
Every day at 03:00
run cleanup.py
```

---

## 36.2 Orchestration Becomes More Valuable When

You need:

- dependencies;
- retries;
- state tracking;
- rich observability;
- multiple tasks;
- concurrency;
- deployment management;
- operational history;
- event-driven triggers;
- automation;
- safe reruns;
- multiple execution environments.

The progression is:

```text
cron + script
       ↓
complexity increases
       ↓
dependencies
retries
state
concurrency
observability
deployments
events
       ↓
orchestration framework
```

Do not adopt an orchestrator merely because one exists.

---

# 37. Production Architecture

A conceptual Prefect architecture:

```text
                 ┌─────────────────────┐
                 │   Prefect Server/UI │
                 └──────────┬──────────┘
                            │
                       Deployment
                            │
                         Work Pool
                            │
                          Worker
                            │
                         Flow Run
                            │
               ┌────────────┴────────────┐
               │                         │
            Task A                    Task B
               │                         │
               └────────────┬────────────┘
                            │
                          Task C
                            │
               ┌────────────┼────────────┐
               │            │            │
             API/DB     Object Store   Warehouse
```

---

## 37.1 Boundary Explanation

### Prefect Server/UI

Operational control and visibility.

### Deployment

Defines how a flow becomes operationally executable.

### Work Pool

Associates deployment work with an execution model.

### Worker

Obtains/executes work.

### Flow Run

One actual workflow execution.

### Tasks

Meaningful units of managed work.

### External Systems

The actual data plane:

- APIs;
- databases;
- object stores;
- warehouses;
- processing engines.

---

# 38. Code Review Exercises

## Exercise 1 — Giant Flow

### Code

```python
@flow
def pipeline():
    data = requests.get(API).json()

    cleaned = []
    for row in data:
        if row["id"]:
            cleaned.append(row)

    connection = psycopg.connect(...)
    for row in cleaned:
        connection.execute(
            "INSERT INTO orders VALUES (...)"
        )

    print("done")
```

### Identify

- task boundary problems;
- retry problems;
- timeout problems;
- secret/configuration issues;
- database transaction issues;
- testability problems.

### Better Design

```text
flow
 ├── extract task
 ├── validate task
 └── load task
```

Business logic remains reusable outside orchestration.

---

## Exercise 2 — Unsafe Retry

```python
@task(retries=5)
def insert_rows(rows):
    for row in rows:
        database.insert(row)
```

### Problem

A failure after 500 successful inserts can cause a retry to insert those 500 rows again.

### Better Design

Use:

- deterministic IDs;
- unique constraints;
- staging;
- merge/upsert;
- transaction strategy.

---

## Exercise 3 — Unbounded Concurrency

```python
@flow
def ingest(sources):
    futures = [
        extract_source.submit(source)
        for source in sources
    ]
    return futures
```

### Problem

If `sources` contains 10,000 items, the system may overwhelm:

- API;
- worker;
- memory;
- network;
- database.

### Better Design

Bound concurrency according to system capacity.

---

## Exercise 4 — Incorrect Cache

```text
Task:
fetch current customer balances

Cache:
24 hours
```

### Problem

The result may become stale.

### Better Design

Do not cache unless the freshness contract permits it.

---

## Exercise 5 — Secret Leakage

```python
logger.info(
    "Calling API with key=%s",
    api_key,
)
```

### Problem

The secret may enter logs.

### Better Design

```python
logger.info("Calling source=%s", source)
```

---

# 39. Debugging Exercises

## Scenario 1 — 20 Sources

A mapped ingestion flow has 20 sources.

Result:

```text
17 succeeded
2 failed then succeeded after retry
1 continues failing
```

### Questions

1. What should you inspect?
2. How do mapped task states help?
3. Should the failed source retry?
4. Should the entire flow rerun?
5. How do you avoid reprocessing successful sources?
6. What makes the operation idempotent?

### Solution

Inspect:

```text
Flow run
 ↓
failed mapped task
 ↓
attempt history
 ↓
logs
 ↓
source parameters
 ↓
external dependency
```

The permanently failing source should not necessarily cause successful sources to be reprocessed.

A safe rerun depends on:

- deterministic source identity;
- idempotent writes;
- per-source state;
- downstream dependency behavior.

---

## Scenario 2 — Duplicate Rows After Retry

Observed:

```text
warehouse rows doubled
```

Task history:

```text
attempt 1 → timeout
attempt 2 → success
```

### Root Cause

The first attempt may have committed data before the task observed the timeout.

### Correct Engineering Response

Investigate the database transaction boundary and write semantics.

Do not assume:

```text
timeout = no side effect
```

---

## Scenario 3 — Worker Is Running but No Flow Executes

Check:

```text
Deployment
 ↓
Work Pool
 ↓
Worker
 ↓
credentials/configuration
 ↓
execution environment
```

Do not start by changing task code if the flow never reaches task execution.

---

# 40. Architecture Questions

## 1. How would you orchestrate 500 API sources?

Use one reusable extraction task with a source configuration collection and mapped/concurrent execution, with bounded concurrency, retries, timeouts, structured logging, and idempotent writes.

---

## 2. How would you limit API concurrency?

Set a bounded concurrency mechanism appropriate to the Prefect execution environment and external API capacity.

The limit should be based on:

```text
API rate limit
worker capacity
connection capacity
memory
business SLA
```

---

## 3. How would you handle rate limits?

Use:

- bounded concurrency;
- retry delays;
- exponential backoff where appropriate;
- rate-limit-aware error handling;
- request budgets.

Do not simply increase retries.

---

## 4. How would you make ingestion retry-safe?

Use:

- deterministic batch IDs;
- unique keys;
- upsert/merge;
- staging;
- transactional boundaries;
- idempotent object paths.

---

## 5. How would you prevent duplicate writes?

Enforce correctness in the data system:

```text
unique constraint
+
idempotent write
+
transaction
```

Do not rely only on the orchestrator.

---

## 6. How would you handle partial mapped-task failures?

Track each source independently.

Then:

```text
successful sources → leave successful
failed sources → investigate/retry
```

Only rerun the whole workflow if the downstream semantics require it and the writes are safe.

---

## 7. How would you schedule daily ingestion?

Define an appropriate deployment schedule with an explicit timezone and partition/input strategy.

Do not assume schedule time equals data readiness.

---

## 8. How would you trigger processing after ingestion?

Use an event/automation or another explicit dependency mechanism:

```text
ingestion complete
 ↓
event
 ↓
automation
 ↓
transformation flow
```

---

## 9. How would you separate code, configuration, and secrets?

```text
Code
  ↓
version-controlled

Configuration
  ↓
variables/configuration

Secrets
  ↓
secret management
```

---

## 10. How would you deploy Prefect in production?

Define:

- flow code packaging;
- deployment;
- work pool;
- execution environment;
- worker;
- configuration;
- secrets;
- concurrency limits;
- observability;
- operational ownership.

---

## 11. How would you handle worker failure?

Treat worker availability as an infrastructure concern.

Investigate:

- worker health;
- work-pool status;
- deployment;
- credentials;
- infrastructure;
- resource capacity.

---

## 12. How would you design observability?

Track:

- flow states;
- task states;
- retries;
- duration;
- source;
- partition;
- row counts;
- failures;
- deployment;
- worker/execution context.

---

## 13. When would you choose Prefect instead of cron?

When the workflow's operational complexity exceeds what a script and cron can manage economically:

```text
dependencies
+
retries
+
state
+
observability
+
concurrency
+
deployment
+
events
```

---

## 14. How would Prefect fit with an existing Airflow environment?

Avoid unnecessary duplication.

Possible approaches depend on organizational architecture:

- keep existing Airflow workflows;
- introduce Prefect for new workflow classes;
- migrate selectively;
- use clear ownership boundaries.

The decision should be based on operational requirements and migration cost.

---

## 15. How would you compare Prefect with Dagster?

Compare:

- flow/task-centric orchestration;
- asset-centric orchestration;
- dependency model;
- deployment;
- observability;
- lineage;
- team skills;
- existing platform.

Do not use a universal ranking.

---

# 41. Interview Preparation — Exactly 40 Questions

## Basic — 10 Questions

### 1. QUESTION
What is a Prefect flow?

**ANSWER:** A flow is the top-level workflow boundary used to define and execute an orchestrated workflow.

**EXPLANATION:** A flow groups meaningful workflow logic and gives Prefect a unit for run tracking, parameters, logging, scheduling, deployment, and operational visibility.

---

### 2. QUESTION
What is a Prefect task?

**ANSWER:** A task is a meaningful unit of managed work inside an orchestration workflow.

**EXPLANATION:** Tasks provide operational boundaries for work such as extraction, validation, transformation, or loading.

---

### 3. QUESTION
What does `@flow` do?

**ANSWER:** It declares a Python function as a Prefect flow.

**EXPLANATION:** Prefect can then manage executions of that workflow as flow runs.

---

### 4. QUESTION
What does `@task` do?

**ANSWER:** It declares a Python function as a Prefect task.

**EXPLANATION:** The operation can receive task-level orchestration features such as state tracking, retries, caching, logging, and concurrent execution.

---

### 5. QUESTION
What is a flow run?

**ANSWER:** One actual execution of a flow definition.

**EXPLANATION:** A flow definition can have many flow runs over time.

---

### 6. QUESTION
Why are parameters important?

**ANSWER:** They make workflow inputs explicit and reproducible.

**EXPLANATION:** Explicit parameters reduce hidden assumptions and make invalid input easier to detect.

---

### 7. QUESTION
What is a task state?

**ANSWER:** A representation of the task's orchestration status.

**EXPLANATION:** Examples include pending, running, completed, failed, cached, and crash-related states.

---

### 8. QUESTION
Why should large datasets not normally be returned from tasks?

**ANSWER:** Because orchestration systems are not the appropriate transport layer for large data.

**EXPLANATION:** Use object stores, databases, warehouses, or processing systems and return references such as paths or IDs.

---

### 9. QUESTION
What is `.submit()`?

**ANSWER:** A task invocation mechanism that submits task work for managed execution and returns a future-like object.

**EXPLANATION:** It enables independent task execution to overlap.

---

### 10. QUESTION
Why does orchestration need logs?

**ANSWER:** To make execution observable and failures diagnosable.

**EXPLANATION:** Operational logs should identify sources, partitions, row counts, durations, attempts, and meaningful errors without exposing secrets.

---

## Moderate — 10 Questions

### 11. QUESTION
What is the difference between a flow and a task?

**ANSWER:** A flow defines the workflow boundary; a task defines a meaningful unit of managed work within it.

**EXPLANATION:** A flow can coordinate many tasks, while each task can have its own state, retry, timeout, caching, and execution behavior.

---

### 12. QUESTION
When should a normal Python function remain a normal function instead of becoming a task?

**ANSWER:** When it is local reusable logic that does not require an independent orchestration boundary.

**EXPLANATION:** Turning every function into a task can create unnecessary orchestration overhead and complexity.

---

### 13. QUESTION
Why are retries dangerous for non-idempotent operations?

**ANSWER:** A retry may repeat an external side effect that already succeeded.

**EXPLANATION:** A network failure can occur after a database commit, causing the orchestrator to believe the operation failed even though the data changed.

---

### 14. QUESTION
What is the difference between a timeout and a retry?

**ANSWER:** A timeout limits execution duration; a retry starts another attempt after failure.

**EXPLANATION:** They solve different failure modes and must be designed together.

---

### 15. QUESTION
What is caching?

**ANSWER:** Reusing a prior task result when the cache conditions indicate that it is valid for the current inputs.

**EXPLANATION:** Caching reduces recomputation but introduces stale-result risks.

---

### 16. QUESTION
Why is bounded concurrency important?

**ANSWER:** Because external systems and workers have finite capacity.

**EXPLANATION:** Unlimited concurrency can exhaust connections, trigger API rate limits, consume memory, or overload databases.

---

### 17. QUESTION
What is a future?

**ANSWER:** A handle representing work that has been submitted but whose final result may not yet be available.

**EXPLANATION:** Downstream tasks can depend on futures while independent tasks execute concurrently.

---

### 18. QUESTION
What is mapped work?

**ANSWER:** Applying one task definition across a collection of inputs.

**EXPLANATION:** It is useful for dynamic workloads such as many files, APIs, partitions, or tenants.

---

### 19. QUESTION
What is a work pool?

**ANSWER:** An infrastructure abstraction connecting deployment work with an execution model.

**EXPLANATION:** It separates workflow definition from the environment used to execute flow runs.

---

### 20. QUESTION
Why should schedules not be confused with data readiness?

**ANSWER:** A clock time does not guarantee that upstream data is available.

**EXPLANATION:** Data readiness may require an event, readiness check, polling mechanism, or upstream completion signal.

---

## Hard — 10 Questions

### 21. QUESTION
A task writes to a database, commits, then times out before receiving the response. Prefect retries it. What can happen?

**ANSWER:** The retry can duplicate the database write.

**EXPLANATION:** A timeout indicates the orchestration layer did not observe successful completion; it does not prove that the external side effect did not occur. Idempotent writes are required.

---

### 22. QUESTION
How would you design 500 mapped API tasks against an API that permits only five concurrent requests?

**ANSWER:** Map the 500 sources but enforce a concurrency limit of five.

**EXPLANATION:** Mapping expresses the dynamic workload; bounded concurrency protects the external system and execution environment.

---

### 23. QUESTION
Why should business logic be testable without the orchestration environment?

**ANSWER:** Because unit tests should validate business correctness independently from orchestration infrastructure.

**EXPLANATION:** Thin task wrappers around reusable functions reduce test complexity and improve maintainability.

---

### 24. QUESTION
A mapped flow has 20 sources; 19 succeed and one fails permanently. Should you rerun the entire flow?

**ANSWER:** Not automatically.

**EXPLANATION:** First inspect per-source state, failure cause, and write idempotency. If successful sources are safely preserved, rerun only the failed unit where possible.

---

### 25. QUESTION
Why can a long-lived cache be dangerous for ingestion?

**ANSWER:** It can return stale data.

**EXPLANATION:** Ingestion usually exists to obtain current source state. Cache validity must be aligned with the data freshness contract.

---

### 26. QUESTION
How do task runners relate to orchestration?

**ANSWER:** They provide an execution model for task work within a flow.

**EXPLANATION:** They can enable concurrent execution, but they do not turn Prefect into a replacement for distributed data-processing engines.

---

### 27. QUESTION
What is the difference between a flow state and a task state?

**ANSWER:** A flow state represents the overall flow run; task state represents an individual task run.

**EXPLANATION:** A flow can contain both successful and failed tasks, so understanding both levels is necessary for diagnosis.

---

### 28. QUESTION
Why should orchestration results generally contain references instead of large datasets?

**ANSWER:** Because the data plane should store and process large data, while the orchestration layer should carry control-plane metadata.

**EXPLANATION:** References such as object paths, table IDs, and batch IDs are smaller and easier to serialize and persist.

---

### 29. QUESTION
How would you distinguish a transient API error from a permanent authentication error?

**ANSWER:** Use error classification based on HTTP status/error semantics and source behavior.

**EXPLANATION:** Temporary service errors may justify retry; invalid credentials generally require configuration correction rather than repeated attempts.

---

### 30. QUESTION
Why is `schedule-driven` execution different from `event-driven` execution?

**ANSWER:** Schedule-driven execution is triggered by time; event-driven execution is triggered by an occurrence or condition.

**EXPLANATION:** A daily clock is appropriate for periodic work, while an upstream completion event is appropriate when data readiness depends on another system.

---

## Advanced — 10 Questions

### 31. QUESTION
Design a production-safe `ingest_sources` flow for 500 sources with rate limits, retries, and partial failures.

**ANSWER:** Use parameterized source definitions, mapped task execution, bounded concurrency, timeout-aware extraction, classified retries, idempotent writes, structured logs, per-source state, and safe rerun semantics.

**EXPLANATION:** The design separates workload representation from concurrency control and makes each source independently recoverable.

---

### 32. QUESTION
How would you prove that retry behavior is safe?

**ANSWER:** Inject a failure after the external side effect and verify that a retry does not create duplicate business data.

**EXPLANATION:** Testing only the exception path is insufficient; the critical case is uncertainty about whether the side effect committed.

---

### 33. QUESTION
How would you debug a flow that shows successful task states but incorrect warehouse data?

**ANSWER:** Treat orchestration state and data correctness separately.

**EXPLANATION:** Inspect database transactions, source data, transformations, load logic, data-quality checks, and reconciliation metrics. A completed task only proves that the task execution reached its configured success condition.

---

### 34. QUESTION
How would you decide whether a task should be cached?

**ANSWER:** Evaluate determinism, freshness requirements, external side effects, cache-key completeness, invalidation strategy, and recomputation cost.

**EXPLANATION:** Caching is a correctness decision as well as a performance optimization.

---

### 35. QUESTION
How would you design observability for mapped ingestion?

**ANSWER:** Log source, partition, batch ID, attempt, row count, duration, and error classification, while tracking individual mapped task states and aggregate flow outcomes.

**EXPLANATION:** Operators need both per-source diagnosis and workflow-level visibility.

---

### 36. QUESTION
How would you separate orchestration from distributed computation?

**ANSWER:** Use Prefect to coordinate the workflow and invoke an appropriate processing engine for heavy computation.

**EXPLANATION:** The orchestrator controls sequencing, retries, triggers, and operational state; Spark, SQL warehouses, databases, or other compute systems perform the heavy data processing.

---

### 37. QUESTION
When might cron remain preferable to Prefect?

**ANSWER:** When the workload is simple enough that cron plus a script provides sufficient scheduling, failure handling, observability, and operational recovery.

**EXPLANATION:** Introducing an orchestrator has operational cost; the architecture should match the problem.

---

### 38. QUESTION
How would you choose between Prefect, Airflow, and Dagster?

**ANSWER:** Compare the workflow model, existing platform, team expertise, asset-lineage requirements, deployment architecture, ecosystem, and operational constraints.

**EXPLANATION:** Prefect emphasizes flows/tasks, Airflow emphasizes DAG/task orchestration, and Dagster emphasizes software-defined assets. Requirements determine suitability.

---

### 39. QUESTION
How would you design a production deployment for Prefect?

**ANSWER:** Separate flow code from deployment configuration, select an appropriate work pool, provide workers/execution infrastructure, externalize configuration and secrets, define schedules or event triggers, enforce resource limits, and implement observability and failure recovery.

**EXPLANATION:** Production deployment is an operational system, not merely a Python script executed on a server.

---

### 40. QUESTION
A source has a daily partition. The ingestion task succeeds but downstream validation fails. How would you rerun safely?

**ANSWER:** Preserve the partition identity, determine whether ingestion is already complete, rerun only the failed downstream boundary when possible, and ensure every write is idempotent.

**EXPLANATION:** The goal is deterministic recovery rather than blindly replaying every upstream side effect.

---

# 42. Practical Exercises

## Beginner

### Exercise 1 — First Flow

Create:

```python
@flow
def hello():
    ...
```

Requirements:

- run it locally;
- inspect its run;
- explain the flow boundary.

---

### Exercise 2 — First Task

Create:

```python
@task
def extract():
    ...
```

Call it from a flow.

---

### Exercise 3 — Parameters

Create:

```python
@flow
def process(source: str, execution_date: str):
    ...
```

Test valid and invalid values.

---

### Exercise 4 — Logging

Log:

- source;
- partition;
- row count;
- duration.

Do not log credentials.

---

## Intermediate

### Exercise 5 — Dependencies

Implement:

```text
extract
 ↓
validate
 ↓
transform
 ↓
load
```

---

### Exercise 6 — Retries

Inject a transient failure.

Prove:

```text
failure
 ↓
retry
 ↓
success
```

---

### Exercise 7 — Timeout

Make a task sleep beyond its timeout.

Record what happened.

---

### Exercise 8 — Caching

Create a deterministic task where caching is clearly safe.

Then change an external input and explain why stale caching can be dangerous.

---

### Exercise 9 — Concurrent Tasks

Create:

```text
extract_A
extract_B
extract_C
```

and execute them concurrently.

Explain why they are independent.

---

## Advanced

### Exercise 10 — Mapped Ingestion

Process:

```text
orders
customers
products
payments
```

with one reusable extraction task.

---

### Exercise 11 — Concurrency Limit

Pretend the API allows only three simultaneous requests.

Design the workflow so it never exceeds that boundary.

---

### Exercise 12 — Deployment

Create a deployment using a current Prefect 3 deployment workflow.

Document:

- deployment;
- work pool;
- worker;
- execution environment.

---

### Exercise 13 — Automation

Trigger a downstream transformation workflow after successful ingestion.

---

### Exercise 14 — Failure Recovery

Inject:

```text
1 temporary API failure
1 permanent authentication failure
1 timeout
1 mapped-source failure
```

Document the expected recovery behavior.

---

## Production Exercise

Build the complete:

```text
ingest_sources
```

system with:

- multiple sources;
- parameters;
- meaningful task boundaries;
- mapping;
- bounded concurrency;
- retries;
- timeouts;
- justified caching;
- structured logs;
- idempotent writes;
- deployment;
- work pool;
- worker;
- schedule;
- automation;
- tests;
- failure injection;
- operational documentation.

---

# 43. Final Capstone — Production-Style Prefect Ingestion Platform

## 43.1 Scenario

Build an ingestion platform for:

```text
orders_api
customers_api
products_api
payments_api
inventory_api
```

Each source has:

- endpoint;
- credentials;
- rate limit;
- timeout;
- retry policy;
- output partition.

---

## 43.2 Required Architecture

```text
                   Prefect
                      │
             ┌────────┴────────┐
             │                 │
          Schedule           Event
             │                 │
             └────────┬────────┘
                      ↓
                ingest_sources
                      │
              mapped source tasks
                      │
             bounded concurrency
                      │
             ┌────────┼────────┐
             ↓        ↓        ↓
           API A    API B    API N
             │        │        │
             └────────┼────────┘
                      ↓
                Raw Object Store
                      ↓
                  Validation
                      ↓
                 Transformation
                      ↓
                   Warehouse
                      ↓
                Quality Checks
                      ↓
                   Publish
```

---

## 43.3 Functional Requirements

The capstone must include:

- multiple sources;
- parameterized flow;
- task decomposition;
- mapped work;
- bounded concurrency;
- retries;
- timeouts;
- caching where justified;
- structured logging;
- state awareness;
- deployment;
- work pool;
- worker;
- schedule;
- automation;
- tests;
- idempotent writes;
- operational documentation.

---

## 43.4 Failure Requirements

Inject:

1. temporary API outage;
2. invalid credentials;
3. database timeout;
4. one mapped-source failure;
5. worker failure;
6. timeout;
7. retry success;
8. retry exhaustion;
9. stale-cache scenario;
10. partial downstream failure.

For each, document:

```text
Failure
 ↓
Observed state
 ↓
Logs
 ↓
Retry behavior
 ↓
External side effect
 ↓
Recovery
 ↓
Production improvement
```

---

## 43.5 Success Criteria

The capstone is complete only when you can demonstrate:

- safe retries;
- bounded concurrency;
- clear task boundaries;
- meaningful logs;
- deterministic partition identity;
- idempotent writes;
- safe recovery;
- observable deployments;
- tested failure behavior;
- documented operational procedures.

---

# 44. Connection to Previous Modules

## Module 2.9 — Data Ingestion and Extraction Patterns

Prefect coordinates ingestion.

```text
Prefect
   ↓
extract APIs/files/databases
   ↓
raw storage
```

Prefect does not replace ingestion logic.

---

## Module 2.10 — Concurrency and Parallelism

Prefect provides workflow-level concurrency mechanisms.

```text
Prefect
   ↓
bounded task concurrency
   ↓
ingestion operations
```

The deeper concurrency concepts remain important:

- threads;
- processes;
- async I/O;
- CPU vs I/O;
- resource limits.

---

## Module 2.11 — Data Validation, Contracts and Quality

Prefect can orchestrate validation:

```text
ingest
 ↓
validate
 ↓
quality gate
 ↓
continue / fail
```

The validation rules themselves belong to the data-quality layer.

---

## Module 2.12 — Transformation Patterns and Pipeline Design

Prefect coordinates transformation stages:

```text
extract
 ↓
stage
 ↓
transform
 ↓
merge
 ↓
publish
```

The transformation logic remains separate.

---

## Overall Relationship

```text
Prefect
  │
  ├── orchestrates ingestion
  │
  ├── triggers validation
  │
  ├── runs transformation
  │
  ├── executes quality gates
  │
  └── controls retries/reruns
```

Prefect coordinates these systems rather than replacing them.

---

# 45. Connection to the Rest of Module 2.13

## 01 — DAGs, Dependencies, and Scheduling Concepts

This topic applies the general concepts through Prefect's flow/task model.

---

## 02 — Limits of Cron

Prefect provides operational features when a simple scheduled script is no longer enough.

---

## 03 — Apache Airflow Architecture

Airflow and Prefect solve overlapping orchestration problems using different architectural models.

---

## 04 — Airflow DAGs, Operators, and TaskFlow

Airflow commonly expresses workflow dependencies through DAG/task abstractions.

Prefect emphasizes Python flow/task programming.

---

## 05 — Airflow Connections, Variables, Hooks, and XComs

Prefect has different configuration and data-passing mechanisms.

The underlying engineering concerns remain:

- credentials;
- configuration;
- external integrations;
- small control-plane outputs.

---

## 06 — Sensors, Deferrable Operators, and Data-Aware Scheduling

Prefect's event/polling/automation concepts address related operational dependencies using different abstractions.

---

## 07 — Retries, Deadlines, and Failure Callbacks

Prefect tasks also require:

- retry policy;
- timeout policy;
- failure handling;
- idempotency;
- operational notification.

---

## 08 — Backfills, Catch-up, and Partitioned Runs

Prefect workflows should also treat historical processing as controlled, deterministic work.

Partition identity should be explicit.

---

## 09 — Dagster Software-Defined Assets

Dagster emphasizes software-defined assets.

Prefect emphasizes flows/tasks.

The underlying question remains:

> "How should this data workflow be represented and operated?"

---

## 11 — Testing and Validating DAGs

The testing philosophy is shared:

```text
test logic
 ↓
test orchestration
 ↓
test failure behavior
 ↓
test deployment
```

---

# 46. Hands-On Learning Loop

For each major practical section:

```text
READ
  ↓
DRAW THE WORKFLOW
  ↓
DECIDE TRIGGERS & INTERVALS
  ↓
BUILD IT THIN
  ↓
RUN IT
  ↓
BREAK IT
  ↓
WATCH THE UI & LOGS
  ↓
RE-RUN THE PAST
  ↓
TEST IT
  ↓
WRITE IT DOWN
  ↓
EXPLAIN ALOUD
```

Do not skip the **BREAK IT** step.

Production orchestration is learned by understanding failure behavior, not only successful execution.

---

# 47. Code Quality Requirements

All executable examples should:

- use current Prefect 3 terminology;
- be syntactically valid;
- include imports;
- use clear names;
- use type hints where useful;
- avoid unexplained magic values;
- distinguish conceptual pseudocode from executable code;
- avoid deprecated Prefect APIs;
- avoid invented APIs;
- identify version-specific assumptions when necessary.

Because Prefect 3 is an actively evolving platform, verify exact deployment, mapping, task-runner, concurrency, hook, and configuration signatures against the installed Prefect version before production implementation.

---

# 48. Production Checklist

Before deploying a Prefect workflow, ask:

## Workflow Design

- [ ] Is the flow boundary meaningful?
- [ ] Are task boundaries meaningful?
- [ ] Is business logic reusable?
- [ ] Are dependencies explicit?

## Parameters

- [ ] Are inputs explicit?
- [ ] Are types defined?
- [ ] Are invalid values rejected?
- [ ] Is partition identity explicit?

## Reliability

- [ ] Are transient errors retried?
- [ ] Are permanent errors allowed to fail?
- [ ] Are retries idempotent?
- [ ] Are external side effects safe?

## Timeouts

- [ ] Does every external operation have a sensible timeout?
- [ ] Is timeout + retry duration understood?

## Caching

- [ ] Is caching actually necessary?
- [ ] Is the task deterministic enough?
- [ ] Is cache invalidation understood?
- [ ] Can stale data be harmful?

## Concurrency

- [ ] Is concurrency bounded?
- [ ] Are API rate limits respected?
- [ ] Are database connections bounded?
- [ ] Is worker memory sufficient?

## Results

- [ ] Are large datasets stored in the data plane?
- [ ] Are task results small references/metadata where possible?

## Security

- [ ] Are secrets outside source code?
- [ ] Are secrets excluded from logs?
- [ ] Is access least-privilege?

## Observability

- [ ] Are source and partition logged?
- [ ] Are row counts logged?
- [ ] Are errors actionable?
- [ ] Can mapped failures be identified?
- [ ] Can run history be inspected?

## Deployment

- [ ] Is deployment configuration version-controlled appropriately?
- [ ] Is the work pool correct?
- [ ] Is the worker healthy?
- [ ] Is the execution environment reproducible?

## Scheduling

- [ ] Is the timezone explicit?
- [ ] Are overlapping runs considered?
- [ ] Is schedule time confused with data readiness?

## Events

- [ ] Are event-driven dependencies modeled correctly?
- [ ] Are automations observable?
- [ ] Are duplicate events safe?

## Testing

- [ ] Is business logic unit-tested?
- [ ] Are tasks tested?
- [ ] Are flow parameters tested?
- [ ] Are retries tested?
- [ ] Are mapped failures tested?
- [ ] Is deployment configuration tested where practical?

---

# 49. Self-Assessment

You should be able to answer **YES** to each question:

- [ ] Can I explain what Prefect is?
- [ ] Can I explain a flow?
- [ ] Can I explain a task?
- [ ] Can I explain flow/task runs?
- [ ] Can I explain states?
- [ ] Can I use typed parameters?
- [ ] Can I implement retries?
- [ ] Can I implement timeouts?
- [ ] Can I explain caching?
- [ ] Can I use concurrent task execution?
- [ ] Can I use `.submit()`?
- [ ] Can I use mapped work?
- [ ] Can I control concurrency?
- [ ] Can I explain task runners?
- [ ] Can I explain persistence/results?
- [ ] Can I use state hooks appropriately?
- [ ] Can I create deployments?
- [ ] Can I explain `serve()` vs `deploy()`?
- [ ] Can I explain work pools?
- [ ] Can I explain workers?
- [ ] Can I schedule flows?
- [ ] Can I explain events?
- [ ] Can I explain automations?
- [ ] Can I use Blocks/Variables appropriately?
- [ ] Can I design retry-safe tasks?
- [ ] Can I design idempotent pipelines?
- [ ] Can I debug failed task runs?
- [ ] Can I handle partial mapped failures?
- [ ] Can I deploy a production-style flow?
- [ ] Can I test Prefect workflows?
- [ ] Can I explain Prefect vs Airflow?
- [ ] Can I explain Prefect vs Dagster?
- [ ] Can I explain when cron is sufficient?
- [ ] Can I build the roadmap's `ingest_sources` flow?

---

# 50. Final Review Questions for the Learner

Before moving to the next topic, explain these aloud without reading the answer:

1. Why does an orchestrator exist?
2. What makes a good task boundary?
3. Why is retry policy inseparable from idempotency?
4. Why can a timeout occur after a database side effect?
5. Why is caching a correctness decision?
6. Why is unlimited mapped concurrency unsafe?
7. What does a future represent?
8. Why should large datasets remain outside the orchestration control plane?
9. What is the difference between a flow run and a task run?
10. Why can a completed task still produce incorrect business data?
11. What is the purpose of a deployment?
12. What is the relationship between a deployment, work pool, and worker?
13. When would `serve()` be appropriate?
14. When would a worker-based deployment be appropriate?
15. What is the difference between a schedule and an event?
16. What is an automation?
17. How should configuration and secrets be separated from code?
18. How would you safely rerun one failed source out of 500?
19. When is cron enough?
20. How does Prefect differ conceptually from Airflow and Dagster?

If you can answer these clearly and demonstrate the capstone, you have moved beyond learning Prefect syntax into understanding orchestration as a production engineering discipline.

---

# 51. Key Takeaways

The most important ideas from this topic are:

1. **Prefect is an orchestration framework, not a replacement for the data plane.**
2. **A flow defines a workflow boundary.**
3. **A task represents meaningful managed work.**
4. **Use ordinary Python where orchestration adds no value.**
5. **Explicit parameters improve reproducibility.**
6. **Retries require idempotent side effects.**
7. **Timeouts prevent indefinite execution but do not prove that external side effects did not happen.**
8. **Caching improves efficiency only when reuse is semantically safe.**
9. **Concurrency must be bounded by real system capacity.**
10. **Futures represent deferred task results and enable dependency-aware concurrency.**
11. **Mapped work represents dynamic collections of similar work.**
12. **States describe orchestration behavior, not business-data truth.**
13. **Large datasets belong in databases, warehouses, object stores, or processing engines—not in orchestration results.**
14. **Deployments separate workflow code from operational execution configuration.**
15. **Work pools and workers provide an execution boundary.**
16. **Schedules answer "when"; events answer "what happened."**
17. **Automations connect events/conditions to operational actions.**
18. **Code, configuration, and secrets should remain separate.**
19. **Failure injection is necessary to prove production behavior.**
20. **Testing should cover business logic, orchestration, failure behavior, and deployment.**
21. **Cron remains useful for genuinely simple jobs.**
22. **Prefect, Airflow, and Dagster represent overlapping orchestration problems through different models.**
23. **Production orchestration is primarily about correctness, recoverability, observability, and controlled execution—not decorators.**

---

## Final Mental Model

Keep this model in mind:

```text
                    PRODUCTION DATA SYSTEM
                             │
                             ▼
                    ┌─────────────────┐
                    │     Prefect     │
                    │  ORCHESTRATION  │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
              Flow         Flow         Flow
                │            │            │
             Tasks        Tasks        Tasks
                │            │            │
        ┌───────┴──────┐     │     ┌──────┴──────┐
        ▼              ▼     ▼     ▼             ▼
      APIs          Files   DB   Warehouse    Compute
        │              │     │       │            │
        └──────────────┴─────┴───────┴────────────┘
                             │
                             ▼
                       Data Products
```

The engineer's responsibility is to make this system:

```text
CORRECT
+
IDEMPOTENT
+
OBSERVABLE
+
RETRY-SAFE
+
BOUNDED
+
TESTABLE
+
RECOVERABLE
+
OPERABLE
```

That is the real purpose of learning Prefect at production Data Engineering level.
