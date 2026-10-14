# Lakeflow Jobs Orchestration

> **Topic 08 — Lakeflow Jobs orchestration**  
> **Phase C — Ingestion and Pipelines**  
> **Learning level:** Beginner → Intermediate → Advanced → Production → System Design  
> **Dependency:** `01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14`

> **Documentation safety:** Databricks changes product terminology, task capabilities, dynamic-value syntax, triggers, compute support, limits, APIs, and pricing. Stable orchestration concepts are taught directly; exact version-sensitive implementation syntax is marked as illustrative and should be verified against the current Databricks documentation before production use.

---

## 1. Learning Objectives

By completing this module, you should be able to:

- Explain why Data Engineering systems need orchestration.
- Distinguish a Job, Run, Task, Dependency, Trigger, Parameter, and Repair Run.
- Model workflows as DAGs.
- Select appropriate task types: Notebook, Python script, Python wheel, SQL, Pipeline, dbt, and Run Job.
- Choose between jobs compute, shared compute, and serverless where supported.
- Design schedules, retries, timeouts, and notifications.
- Use scheduled, file-arrival, table-update, and continuous triggers where supported.
- Parameterize jobs for dates, environments, sources, and backfills.
- Use dynamic value references and task values.
- Implement if/else, for-each, and run-if control flow.
- Recover failed workflows with repair runs.
- Monitor run history, task logs, duration, retries, queueing, and failures.
- Design safe historical backfills and reruns.
- Control concurrency and prevent overlapping runs.
- Build idempotent tasks so retries and repairs are safe.
- Run production workflows with service principals and least privilege.
- Compare Lakeflow Jobs with Apache Airflow.
- Integrate Airflow with Databricks when a platform-wide orchestrator is required.
- Engineer reliability, security, observability, and cost.
- Design production orchestration architectures.
- Troubleshoot incidents using evidence rather than blind reruns.

### The production question

> **Can I design, build, operate, troubleshoot, recover, optimize, and explain production Lakeflow Jobs workflows?**

The target answer is **yes**.

---

## 2. Roadmap Position and Prerequisites

Topic 08 follows:

```text
Topic 05 — Auto Loader
        ↓
Topic 06 — Lakeflow Connect
        ↓
Topic 07 — Lakeflow Declarative Pipelines
        ↓
Topic 08 — Lakeflow Jobs
        ↓
Topic 09 — Performance
```

The core operating model is:

```text
INGEST
   ↓
TRANSFORM
   ↓
VALIDATE
   ↓
ORCHESTRATE
   ↓
MONITOR
   ↓
RECOVER
```

Earlier topics already covered:

- Databricks architecture
- compute
- notebooks and project structure
- Unity Catalog
- Auto Loader
- Lakeflow Connect
- declarative pipelines
- Spark/PySpark
- Delta
- Structured Streaming
- dbt foundations
- Airflow foundations

This module therefore focuses on **orchestration**, not re-teaching those technologies.

### Dependency principle

A pipeline answers:

> **What data should be produced?**

A Job answers:

> **When should work run, in what order, under what conditions, and what happens when it fails?**

---

## 3. Why Data Engineering Needs Orchestration

Consider a simple workflow:

```text
Files arrive
    ↓
Ingest
    ↓
Transform
    ↓
Quality checks
    ↓
Publish gold
    ↓
Notify consumers
```

One task is easy.

Production systems usually look like:

```text
customers
orders
products
payments
events
    ↓
multiple ingestion paths
    ↓
multiple transformations
    ↓
quality gates
    ↓
gold datasets
    ↓
BI / ML / AI consumers
```

Dependencies matter:

```text
customers ───────┐
products ────────┤
                 ↓
orders ─────────→ silver_orders
                       ↓
                  gold_revenue
                       ↓
                    dashboard
```

Without orchestration, engineers end up maintaining:

- cron scripts
- shell wrappers
- ad-hoc notebooks
- manually ordered jobs
- fragile retries
- manual failure recovery
- undocumented dependencies
- inconsistent schedules
- manual backfills

### What orchestration provides

| Requirement | Orchestration responsibility |
|---|---|
| Ordering | Dependencies |
| Timing | Schedules/triggers |
| Parallelism | DAG design |
| Failure handling | Retries/repair |
| Conditional execution | If/else/run-if |
| Fan-out | For-each |
| Historical processing | Parameters/backfills |
| Monitoring | Run history/logs |
| Alerting | Notifications |
| Identity | Run-as/service principal |
| Concurrency | Limits/queueing |
| Recovery | Repair/backfill/rerun |

---

## 4. Orchestration From Zero

Orchestration is the system that decides:

> **what should run, when it should run, in what order, under what conditions, and what should happen when something fails.**

Mental model:

```text
WHAT?
  ↓
Task

WHEN?
  ↓
Trigger / Schedule

IN WHAT ORDER?
  ↓
Dependency

IF SOMETHING FAILS?
  ↓
Retry / Repair / Alert

IF DATA CHANGES?
  ↓
Conditional execution

HOW MANY?
  ↓
Concurrency / Queueing

WHO RUNS IT?
  ↓
Service principal / identity
```

### The orchestration lifecycle

```text
Define
  ↓
Trigger
  ↓
Schedule
  ↓
Execute
  ↓
Observe
  ↓
Retry / Branch / Repair
  ↓
Validate
  ↓
Publish
```

---

## 5. What Is Lakeflow Jobs?

Lakeflow Jobs is Databricks' workflow orchestration capability for running tasks with dependencies, compute, triggers, parameters, monitoring, and recovery controls.

Conceptually:

```text
Job
 ├── Task A
 ├── Task B
 ├── Task C
 └── Task D
```

### Job

The orchestration definition.

### Run

One execution of the Job.

```text
Daily Orders Job
      ↓
Run: 2026-10-06
```

### Task

One unit of executable work.

```text
ingest_orders
transform_orders
quality_check
publish_gold
```

### Dependency

A relationship defining when a downstream task can execute.

```text
ingest
  ↓
transform
```

### Trigger

The event or schedule that starts a Job.

### Parameter

Information supplied to the Job/task.

### Repair Run

A controlled rerun of a failed/canceled portion of a workflow where supported.

---

## 6. Jobs, Runs, Tasks, and Dependencies

| Concept | Meaning | Example |
|---|---|---|
| Job | Workflow definition | Daily Orders Job |
| Run | One execution | Run for 2026-10-06 |
| Task | Executable unit | `transform_orders` |
| Dependency | Ordering relationship | Transform waits for ingest |
| Trigger | Starts execution | Daily schedule |
| Parameter | Runtime input | `run_date=2026-10-06` |
| Repair run | Recovery execution | Rerun failed path |

Example:

```text
Daily Orders Job
       ↓
Run: 2026-10-06
       ↓
ingest_orders
       ↓
transform_orders
       ↓
quality_check
       ↓
publish_gold
```

### Why the distinction matters

A common beginner mistake is to say:

> "The Job failed."

Production engineers ask:

> "Which Run failed, which Task failed, what dependency was blocked, what evidence exists, and what recovery operation is safest?"

That difference is operational maturity.

---

## 7. DAG Fundamentals

A workflow is a **Directed Acyclic Graph**.

```text
A
↓
B
↓
C
```

Or:

```text
A ─┐
   ├──→ C
B ─┘
```

### Core DAG concepts

**Node:** task.

**Edge:** dependency.

**Root:** task with no upstream dependency.

**Leaf:** downstream endpoint.

**Fan-out:** one task feeds many tasks.

```text
       ┌→ B
A ─────┼→ C
       └→ D
```

**Fan-in:** many tasks feed one task.

```text
A ─┐
B ─┼→ D
C ─┘
```

**Critical path:** longest dependency path that determines minimum workflow duration.

### Critical path example

```text
A = 10 min
B = 20 min
C = 30 min
```

Sequential:

```text
10 + 20 + 30 = 60 min
```

Parallel:

```text
max(10, 20, 30) = 30 min
```

Real systems add:

- compute startup
- queue time
- retries
- dependencies
- data availability
- network latency

### DAG rule

> Parallelism should be intentional, not accidental.

---

## 8. Task Types

Current Databricks documentation lists task types including Notebook, Python script, Python wheel, SQL, Pipeline, dbt and other specialized task types. This module focuses on the roadmap-required core task types. citeturn0search6

| Task type | Best fit | Main risk |
|---|---|---|
| Notebook | Interactive/data-science-oriented logic | Monolithic code |
| Python script | Lightweight executable Python | Configuration/testing drift |
| Python wheel | Reusable production package | Packaging complexity |
| SQL | SQL transformation/checks | SQL-only limitation |
| Pipeline | Declarative pipeline execution | Mixing orchestration with transformation semantics |
| dbt | dbt Core transformations | Cross-system complexity |
| Run Job | Reusable workflow composition | Hidden dependency chains |

### Decision principle

Choose the task type based on:

```text
Workload
  ↓
Code maturity
  ↓
Reusability
  ↓
Testing needs
  ↓
Deployment model
  ↓
Operational ownership
```

---

## 9. Notebook Tasks

A Notebook task executes notebook-based logic.

Good use cases:

- exploratory-to-operational workflows
- SQL/Python mixed workflows
- teams already using notebooks
- small orchestration glue
- analyst-owned production jobs with adequate controls

Example:

```text
Job
 ↓
Notebook: ingest_orders
 ↓
Notebook: validate_orders
```

### Notebook strengths

- fast development
- readable
- easy visualization
- convenient debugging
- familiar to data teams

### Notebook weaknesses

- hidden state
- monolithic code
- difficult unit testing
- excessive `%run` chains
- hardcoded configuration
- weak reuse
- merge conflicts
- code-review friction

### Production rule

A notebook is not inherently bad.

The problem is using a notebook as an entire software architecture.

---

## 10. Python Script Tasks

A Python script task runs a Python file. Databricks recommends supported workspace/Git-based source locations rather than relying on DBFS root or mounts for code. citeturn0search4

Conceptual flow:

```text
Python source
    ↓
Job task
    ↓
Compute
    ↓
Exit status
```

Example:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--run-date", required=True)
args = parser.parse_args()

print(f"Processing {args.run_date}")
```

The Job supplies:

```text
--run-date 2026-10-06
```

### Production considerations

- explicit arguments
- structured logging
- deterministic exit codes
- testable functions
- dependency pinning
- source control
- configuration separation
- no secrets in code

---

## 11. Python Wheel Tasks

A wheel packages Python application logic for repeatable execution.

Conceptual structure:

```text
src/
  pipeline/
    ingestion.py
    transforms.py
    quality.py
```

Then:

```text
Python package
      ↓
Wheel
      ↓
Job task
      ↓
Entry point
```

Databricks documents Python wheel tasks as a supported Lakeflow Jobs task type, with package name and entry point configuration. citeturn0search0

### Why wheels are production-friendly

- reusable code
- versioning
- dependency management
- automated tests
- CI/CD
- clear entry points
- reproducibility

### When to prefer a wheel

Prefer it when:

- logic is reused
- unit testing matters
- multiple jobs share code
- CI/CD is established
- the workload is production-critical

### Trade-off

Packaging adds engineering discipline.

That is usually a benefit for mature production systems.

---

## 12. SQL Tasks

SQL tasks are useful for:

- transformations
- quality checks
- reconciliation
- publishing
- analytical operations

Illustrative pattern:

```sql
SELECT COUNT(*)
FROM silver.orders
WHERE order_date = :run_date;
```

> **Illustrative pattern:** exact parameter syntax depends on the task type and current Databricks interface. Verify current documentation before production use.

### Good SQL task

```text
One clear responsibility
+
Explicit parameters
+
Observable result
+
Idempotent behavior
```

### Poor SQL task

A 1,500-line script that:

- mixes unrelated transformations
- hardcodes production objects
- has hidden side effects
- cannot be safely rerun

---

## 13. Pipeline Tasks

Topic 07 defines the data pipeline.

Topic 08 orchestrates it.

```text
Lakeflow Job
      ↓
Pipeline Task
      ↓
Lakeflow Declarative Pipeline
      ↓
Bronze → Silver → Gold
```

Mental model:

```text
Lakeflow Declarative Pipelines
=
WHAT data should be produced

Lakeflow Jobs
=
WHEN / IN WHAT ORDER / UNDER WHAT CONDITIONS
```

### Example

```text
File arrival
   ↓
Lakeflow Job
   ↓
Pipeline task
   ↓
Bronze
   ↓
Silver
   ↓
Gold
   ↓
Publish
```

The Job should not duplicate transformation logic that belongs in the pipeline.

---

## 14. dbt Tasks

A dbt task lets a Job orchestrate dbt transformations alongside other tasks. Current Databricks documentation distinguishes dbt Core tasks from dbt platform tasks; the roadmap's focus is orchestration of dbt work, not re-teaching dbt. citeturn0search1turn0search2

Example:

```text
Auto Loader
   ↓
dbt task
   ↓
SQL quality
   ↓
Notebook reporting
```

### Why use a dbt task

- centralized workflow
- scheduling
- dependency management
- monitoring
- notifications
- integration with other task types

### Production considerations

- pin dbt dependencies
- use source control
- use service identity
- validate catalog/schema privileges
- monitor dbt artifacts/logs
- avoid duplicating transformations elsewhere

Databricks recommends using a dbt task in a Databricks Job for production dbt transformations and supports parameter references in dbt commands. citeturn0search2turn0search5

---

## 15. Run Another Job

A Run Job task composes one workflow from another:

```text
Job A
  ↓
Run Job
  ↓
Job B
```

Useful for:

- reusable domain workflows
- platform workflows
- shared ingestion jobs
- modular orchestration

### Risks

- hidden dependencies
- difficult debugging
- failure propagation
- excessive nesting
- ownership ambiguity
- circular dependencies

Current Databricks documentation explicitly disallows circular Run Job dependencies and limits nesting depth. Verify current limits before designing deeply nested workflows. citeturn0search3

### Production rule

Prefer a small number of clearly owned workflow boundaries over deeply nested orchestration.

---

## 16. Dependencies and Execution Graphs

Sequential:

```text
ingest
  ↓
transform
  ↓
publish
```

Parallel:

```text
          ┌→ customers
ingestion ┼→ orders
          └→ products
```

Fan-in:

```text
customers ─┐
orders ────┼→ silver_customer_360
products ──┘
```

### Example

```text
ingest_customers ──┐
                    ├──→ build_customer_360
ingest_orders ──────┘
```

`build_customer_360` should not execute until all required upstream inputs have completed successfully according to the configured dependency semantics.

### Hidden dependency anti-pattern

```text
Task B
```

reads a table produced by Task A but has no explicit dependency on A.

This is dangerous because the scheduler does not necessarily know the relationship.

### Rule

> If a dependency matters to correctness, make it explicit.

---

## 17. Compute Choices

The major choices include:

- jobs compute
- shared job compute
- serverless compute

Current Databricks guidance recommends jobs compute for many job tasks and documents serverless support/limitations by task type. citeturn0search8turn0search11

### Jobs compute

Good for:

- isolated task execution
- predictable dependencies
- production workloads
- reproducible environments

### Shared job compute

Can reduce startup overhead where multiple tasks can safely share resources.

Risks:

- resource contention
- failure coupling
- harder performance attribution

### Serverless

Benefits:

- less infrastructure management
- managed compute
- elasticity
- simpler operations

Risks:

- feature limitations
- workload compatibility
- pricing characteristics
- less low-level infrastructure control

### Compute decision matrix

| Workload | Jobs compute | Shared compute | Serverless |
|---|---:|---:|---:|
| Small Python task | Strong | Possible | Strong if supported |
| SQL task | Use SQL warehouse | N/A | Strong if supported |
| Heavy Spark task | Strong | Possible | Depends on support |
| Multiple independent tasks | Strong | Possible | Strong if supported |
| Specialized runtime | Strong | Strong | Verify support |
| Low operations overhead | Moderate | Moderate | Strong |
| Strict infrastructure control | Strong | Strong | Lower |

> **Cheapest adequate compute** is the goal, not simply the smallest compute.

---

## 18. Schedules

A schedule answers:

> When should the Job start?

Examples:

```text
Daily at 02:00
```

```text
Every hour
```

```text
Weekdays
```

### Scheduling considerations

- business timezone
- data availability
- daylight-saving changes where relevant
- expected runtime
- overlap risk
- downstream SLA
- maintenance windows

### Example

```text
Source available by 01:30
      ↓
Job starts 02:00
      ↓
Gold ready by 06:00
```

A schedule should be derived from source readiness and consumer SLA, not chosen arbitrarily.

---

## 19. Retries

Retries handle transient failures.

```text
Task
 ↓
Transient failure
 ↓
Retry
 ↓
Success
```

Typical transient failures:

- temporary network issue
- short-lived service error
- capacity issue
- temporary dependency outage

Permanent failures:

- invalid SQL
- missing object
- bad credentials
- broken code
- invalid parameter

### Retry design

Consider:

- retry count
- delay/backoff
- task idempotency
- downstream side effects
- source pressure
- alerting

### Retry rule

> Never add retries without thinking about idempotency.

A retry of a non-idempotent task can duplicate:

- records
- payments
- files
- API calls
- notifications

---

## 20. Timeouts

A timeout protects the workflow from unexpected long-running work.

Example:

```text
Expected runtime = 20 min
Timeout = 60 min
```

A timeout that is too short:

```text
Expected = 20 min
Timeout = 5 min
```

creates false failures.

A timeout that is too long:

```text
Expected = 20 min
Timeout = 12 hours
```

can hide runaway work.

### Timeout design

Use:

```text
Baseline runtime
+
Normal variance
+
Recovery allowance
```

Then alert on unusually long duration before a hard timeout when possible.

---

## 21. Notifications

Useful alerts include:

- task failure
- job failure
- long duration
- repeated retry
- missed freshness target
- critical quality failure

### Alert severity

```text
Critical failure
    ↓
Immediate alert

Expected warning
    ↓
Monitoring

Informational event
    ↓
Log
```

### Alert fatigue

If every minor warning sends an immediate page:

```text
Too many alerts
      ↓
Engineers ignore alerts
      ↓
Critical incident missed
```

Alerting is an engineering design problem.

---

## 22. Triggers

Current Databricks documentation supports automatic Job triggers including:

- time-based schedules
- table updates
- file arrival in Unity Catalog storage locations
- continuous execution
- and other newer trigger types depending on workspace capabilities. citeturn0search9

This roadmap focuses on:

1. scheduled
2. file arrival
3. table update
4. continuous

### Trigger decision

| Trigger | Best fit |
|---|---|
| Scheduled | Predictable batch |
| File arrival | Landing-file workflows |
| Table update | Downstream table-driven workflows |
| Continuous | Low-latency/continuous workloads where supported |

---

## 23. File-Arrival Triggers

Conceptual flow:

```text
Partner file
   ↓
Unity Catalog storage location
   ↓
File arrival
   ↓
Lakeflow Job
   ↓
Ingestion
```

### Risks

**Duplicate event**

The same logical input can produce repeated execution.

**Partial arrival**

A workflow can begin before the expected input set is complete.

**Burst arrival**

100 files can produce a much larger execution load than expected.

**Missing arrival**

The expected file never appears.

### Mitigation

- idempotent ingestion
- source completeness checks
- batching where appropriate
- freshness monitoring
- explicit source contracts

---

## 24. Table-Update Triggers

Conceptual:

```text
Bronze updated
      ↓
Quality job
      ↓
Silver
```

Useful when a downstream workflow should react to upstream table changes.

Questions to ask:

- Which table is the source of truth?
- How frequently does it update?
- Can updates arrive in bursts?
- Can downstream processing overlap?
- Is every update worth triggering a run?
- Is the downstream operation idempotent?

Use table triggers when they reduce unnecessary polling and align execution with actual data availability.

---

## 25. Continuous Execution

Conceptual difference:

```text
Scheduled
=
Start at time T
```

```text
Event-driven
=
Start when event E occurs
```

```text
Continuous
=
Keep processing continuously according to supported execution semantics
```

### Trade-offs

| Dimension | Scheduled | Event-driven | Continuous |
|---|---|---|---|
| Latency | Higher | Lower | Lowest/near-continuous |
| Cost predictability | Strong | Strong | Lower |
| Operational complexity | Lower | Moderate | Higher |
| Freshness | Schedule-dependent | Event-dependent | Continuous |
| Best fit | Batch | Event-triggered | Streaming |

Current compute support and trigger limitations must be checked before production design. For example, current Databricks documentation describes specific continuous scheduling limitations for serverless jobs. citeturn0search11

---

## 26. Parameters

Parameters make workflows reusable.

Core parameter categories:

- Job parameters
- Task parameters
- Dynamic value references
- Run-date values
- Task values

Conceptual flow:

```text
Job
 ↓
Parameters
 ↓
Tasks
 ↓
Outputs
```

Current Databricks documentation describes job-level key/value parameters, task parameters, dynamic value references, and task values as core parameterization mechanisms. citeturn0search12

---

## 27. Job Parameters

Example:

```text
run_date    = 2026-10-06
environment = prod
source      = orders
```

Use cases:

- reusable workflows
- environment selection
- partition processing
- backfills
- source selection
- business-date processing

Conceptually:

```text
Job
 ├── run_date
 ├── environment
 └── source
       ↓
Tasks
```

### Production rule

Do not hardcode:

```text
prod_catalog
```

inside transformation logic when the same workflow must run in multiple environments.

---

## 28. Task Parameters

Task-level parameters specialize individual tasks.

Example:

```text
Job:
run_date = 2026-10-06

Task A:
source = orders

Task B:
catalog = prod_catalog
```

Current Databricks documentation supports task parameters and describes how job parameters can be pushed down to compatible task types. citeturn0search7

### Design rule

Use Job parameters for workflow-wide context.

Use Task parameters for task-specific configuration.

---

## 29. Dynamic Value References

Dynamic values let a workflow reference runtime metadata and other dynamic information.

Conceptual examples:

```text
run date
job ID
run ID
start time
task context
job parameters
upstream task values
```

Illustrative syntax:

```text
{{job.parameters.run_date}}
```

> **Version-sensitive syntax:** verify the current Dynamic Value References documentation for the exact supported reference names and contexts.

### Why dynamic values matter

Without them, teams create:

```text
Job for Jan 1
Job for Jan 2
Job for Jan 3
...
```

With parameters:

```text
One reusable Job
+
run_date
```

---

## 30. Task Values

Task values allow one task to expose runtime information to downstream tasks.

Conceptual flow:

```text
Task A
  ↓
records_processed = 125000
  ↓
Task B
```

Task B can use that value for:

- branching
- validation
- alerting
- dynamic configuration
- operational decisions

Illustrative reference:

```text
{{tasks.ingest.values.records_processed}}
```

> **Version-sensitive syntax:** verify current task-value syntax and task support before implementation.

### Example

```text
Task A:
records_processed = 125000

Task B:
threshold = 100000

125000 > 100000
      ↓
continue
```

---

## 31. If/Else

Quality gate:

```text
Quality Check
      |
      +---- PASS → Publish
      |
      +---- FAIL → Alert
```

Example:

```text
quality_score >= 99%
        |
      YES ──→ publish
        |
       NO ──→ quarantine / alert
```

Use if/else for:

- quality gates
- business conditions
- feature flags
- conditional publication
- environment-specific branches

Do not use it to hide fundamental dependency errors.

---

## 32. For-Each

For-each provides controlled fan-out.

Example:

```text
sources =
[
  customers,
  orders,
  products,
  payments
]
```

Conceptual graph:

```text
             ┌── customers
             ├── orders
FOR EACH ────┼── products
             └── payments
```

Current Databricks task-parameter documentation describes For each as iterating over a JSON-formatted array to run conditionalized task logic. citeturn0search7

### Benefits

- reusable logic
- less duplicated configuration
- consistent processing
- parameterized source handling

### Risks

- excessive parallelism
- source throttling
- resource contention
- harder debugging
- one bad source affecting the fan-out
- huge task counts

### Rule

> Fan-out should match downstream capacity.

---

## 33. Run-If Dependencies

Run-if logic controls whether a task executes based on upstream task states/conditions.

Common conceptual policies include:

```text
Run if all succeeded
Run if any succeeded
Run if upstream failed
Run if condition is met
```

Useful for:

- cleanup
- notifications
- quarantine
- failure handling
- optional publishing

Do not assume a specific run-if option exists without checking the current Databricks documentation.

---

## 34. Repair Runs

Suppose:

```text
A ✓
↓
B ✓
↓
C ✗
↓
D blocked
```

A repair should conceptually allow:

```text
C → D
```

instead of:

```text
A → B → C → D
```

### Why repair matters

- lower runtime
- lower cost
- less duplicate processing
- faster recovery
- preserves successful work

### Repair safety

Repairing a workflow is only safe when the failed task and downstream tasks are designed to tolerate re-execution.

That brings us back to:

> **Idempotency.**

Current Databricks documentation supports repairing/rerunning failed or canceled jobs through the UI/API. citeturn0search8

---

## 35. Monitoring

A production monitoring model:

```text
Did it start?
     ↓
Did it run?
     ↓
Did it succeed?
     ↓
How long did it take?
     ↓
Did retries occur?
     ↓
Did downstream tasks run?
     ↓
Was the output correct?
```

Monitor:

### Availability

- Job success/failure
- task success/failure

### Reliability

- retry rate
- repair frequency

### Performance

- runtime
- critical-path duration
- queue time

### Freshness

- data availability time
- SLA attainment

### Cost

- compute duration
- task frequency
- retry cost

### Operational health

- stuck runs
- queued runs
- overlapping runs

---

## 36. Failure Triage

When a Job fails:

```text
Job failed
   ↓
Which Run?
   ↓
Which Task?
   ↓
What error?
   ↓
Transient or permanent?
   ↓
Retry?
   ↓
Repair?
   ↓
Backfill?
```

### Do not begin with

> "Run the entire Job again."

Begin with evidence.

### Example

```text
Task: transform_orders
Error: missing column customer_id
```

This is likely a code/schema problem, not a transient network problem.

A retry may simply reproduce the same failure.

---

## 37. Backfills

Suppose:

```text
Expected:
Jan 1 → Jan 10

Present:
Jan 1 → Jan 3
Jan 7 → Jan 10

Missing:
Jan 4 → Jan 6
```

A backfill intentionally processes historical intervals.

### Safe backfill sequence

```text
Define interval
      ↓
Verify source of truth
      ↓
Confirm idempotency
      ↓
Check downstream dependencies
      ↓
Run historical processing
      ↓
Reconcile
      ↓
Validate downstream products
      ↓
Document
```

### Backfill risks

- duplicate records
- overwriting correct history
- downstream double counting
- resource contention
- long runtime
- cost spikes
- overlapping production runs

---

## 38. Historical Reruns

A parameterized Job can process:

```text
run_date = 2026-09-01
run_date = 2026-09-02
run_date = 2026-09-03
```

This is preferable to creating separate Jobs for every date.

### Historical rerun checklist

```text
[ ] Source data exists
[ ] Transformation version is correct
[ ] Idempotency is proven
[ ] Downstream impact is understood
[ ] Concurrency is controlled
[ ] Historical date is explicit
[ ] Validation exists
[ ] Cost is acceptable
```

---

## 39. Concurrency and Queueing

Concurrency controls how many Job runs may execute simultaneously.

Example:

```text
Run A
Run B
Run C
```

With concurrency = 1:

```text
Run A
  ↓
Run B
  ↓
Run C
```

### Why limit concurrency?

- prevent overlapping writes
- protect source systems
- avoid race conditions
- reduce cost
- prevent resource contention
- preserve deterministic results

### Queueing

Conceptually:

```text
Run requested
     ↓
Already running?
     ↓
YES → Queue
NO  → Execute
```

Queueing trades:

```text
lower concurrency
```

for:

```text
higher waiting time
```

The correct balance depends on SLA and source/compute capacity.

---

## 40. Preventing Overlapping Runs

Example:

```text
Expected runtime = 45 min
Schedule = every 30 min
```

Potential result:

```text
Run 1 ────────────────┐
Run 2       ──────────┼── overlap
Run 3               ──┘
```

Possible consequences:

- duplicate processing
- competing writes
- inconsistent state
- source pressure
- increased cost

### Design rule

A schedule must be compatible with:

```text
Expected runtime
+
normal variance
+
retry behavior
+
queue time
```

---

## 41. Idempotency

Idempotency means:

> Repeating the same logical operation does not produce an incorrect additional effect.

Example:

```text
Run 1
write orders for 2026-10-06

Run 2
same logical input
```

A correct idempotent design should still produce the correct state.

### Techniques

- `MERGE`
- deterministic keys
- partition replacement
- deduplication
- transaction semantics
- run-date isolation
- external side-effect protection

### Dangerous non-idempotent task

```text
INSERT INTO target
SELECT ...
```

If retried blindly, it may duplicate rows.

### Safer conceptual pattern

```text
Identify logical key
      ↓
Match existing state
      ↓
Insert/update deterministically
```

### External side effects

Be especially careful with:

- payments
- emails
- API POST requests
- file uploads
- notifications

A Databricks retry cannot automatically make an external API call idempotent.

---

## 42. Service Principals

Production workflows should not depend on an individual employee's identity.

Better:

```text
Developer
   ↓
Deploys workflow

Service Principal
   ↓
Executes workflow

Unity Catalog
   ↓
Authorizes data access
```

### Why?

Employees:

- change roles
- leave organizations
- lose access
- change permissions

Production workloads should have stable machine identity.

### Run identity

Distinguish:

```text
Job owner
```

from:

```text
Run-as / execution identity
```

The exact UI terminology and supported configuration should be checked against the current Databricks workspace documentation.

---

## 43. Security and Governance

Use:

- service principals
- Unity Catalog
- least privilege
- environment isolation
- secret management
- auditability
- controlled production access

Mental model:

```text
Identity
   ↓
Authorization
   ↓
Task
   ↓
Data
```

### Least privilege

A Job that only reads:

```text
prod_catalog.sales.orders
```

should not have broad write access to:

```text
prod_catalog
```

### Environment separation

```text
DEV
 ↓
TEST
 ↓
PROD
```

Each should have:

- distinct configuration
- appropriate permissions
- controlled deployment
- clear ownership

---

## 44. Cost Engineering

Conceptual model:

```text
Cost
=
Frequency
×
Runtime
×
Compute
×
Retries
×
Concurrency
```

This is a **conceptual engineering model**, not an exact Databricks billing formula.

### Cost drivers

- unnecessary schedules
- long tasks
- repeated retries
- excessive backfills
- overlapping runs
- excessive fan-out
- inefficient compute
- idle resources
- duplicate orchestration

### Optimization loop

```text
Measure
  ↓
Identify expensive task
  ↓
Optimize DAG
  ↓
Optimize compute
  ↓
Reduce unnecessary runs
  ↓
Measure again
```

Cost should be treated as an architectural concern.

---

## 45. Reliability Engineering

A reliable Job has:

```text
Correct dependency graph
+
Idempotent tasks
+
Retries
+
Timeouts
+
Monitoring
+
Repair
+
Backfill strategy
+
Stable identity
```

### Reliability questions

Before production:

1. What can fail?
2. What is transient?
3. What is permanent?
4. Can the task be safely retried?
5. Can it be repaired?
6. Can historical data be reprocessed?
7. Can runs overlap?
8. How will engineers know?
9. Who owns the incident?
10. What evidence proves recovery?

---

## 46. Lakeflow Jobs vs Airflow

| Dimension | Lakeflow Jobs | Apache Airflow |
|---|---|---|
| Primary scope | Databricks-centric orchestration | Platform-wide orchestration |
| Databricks integration | Native | Via providers/operators |
| Non-Databricks systems | More limited | Strong |
| Ecosystem | Databricks platform | Broad provider ecosystem |
| Multi-cloud heterogeneous workflows | Less natural | Strong |
| Operational overhead | Lower inside Databricks | Higher |
| Portability | Lower | Higher |
| Team ownership | Databricks team | Platform/orchestration team |
| Compute integration | Native Databricks | External systems/providers |
| Governance integration | Strong with Databricks | Depends on integrations |
| Best fit | Databricks-centric platform | Heterogeneous enterprise platform |

### Do not ask

> Which tool is universally better?

Ask:

> Which orchestrator best matches the organization's workload boundaries, ecosystem, skills, and operating model?

---

## 47. When Lakeflow Jobs Is Enough

Lakeflow Jobs may be sufficient when:

```text
Most workloads
      ↓
Databricks
      ↓
Databricks-native governance
      ↓
Databricks-native compute
      ↓
Databricks-native pipelines
```

Benefits:

- fewer systems
- simpler operations
- native task types
- native compute integration
- native monitoring
- simpler identity model

### But evaluate

- external APIs
- Kubernetes workloads
- cloud services
- SaaS workflows
- multi-cloud dependencies
- organization-wide orchestration standards

---

## 48. When Airflow Makes More Sense

Airflow can be stronger when workflows span:

```text
Databricks
+
Kubernetes
+
AWS services
+
GCP services
+
APIs
+
SaaS
+
non-Databricks databases
```

Example:

```text
Airflow
 ├── AWS API
 ├── PostgreSQL
 ├── Kubernetes
 ├── Databricks
 └── External SaaS
```

The trade-off is greater platform ownership and operational complexity.

---

## 49. Airflow → Databricks

Architecture:

```text
Airflow
   ↓
Databricks task/job
   ↓
Lakeflow Declarative Pipeline
   ↓
Gold
```

### Separation of concerns

Airflow:

```text
Cross-platform orchestration
```

Databricks:

```text
Data processing / Lakehouse execution
```

### Why this architecture can be strong

It avoids forcing one orchestrator to solve every platform problem.

### Why it can be expensive

You now operate:

- Airflow
- Databricks
- two identity models
- two monitoring surfaces
- cross-platform dependencies

Avoid duplicate orchestration:

```text
Airflow triggers Job
AND
Job also triggers itself
```

That creates confusing ownership.

---

## 50. Production Architecture Patterns

### Architecture A — Daily Batch

```text
Schedule
   ↓
Ingestion
   ↓
Transformation
   ↓
Quality
   ↓
Gold
   ↓
Notification
```

### Architecture B — Event-Driven

```text
File arrival
   ↓
Lakeflow Job
   ↓
Auto Loader
   ↓
Pipeline
   ↓
Quality
   ↓
Publish
```

### Architecture C — Multi-Source

```text
Customers ──┐
Orders ─────┤
Products ───┤
Payments ───┤
Events ─────┘
      ↓
Lakeflow Jobs
      ↓
Lakehouse
```

### Architecture D — Airflow + Databricks

```text
Airflow
   ↓
Databricks Job
   ↓
Lakeflow Pipeline
   ↓
Gold
```

---

## 51. SLA / SLO Thinking

Example business SLA:

```text
Gold revenue table available by 07:00.
```

Break down:

```text
Ingestion
   ↓
Transformation
   ↓
Quality
   ↓
Publishing
```

If:

```text
Ingestion = 45 min
Transform = 90 min
Quality = 20 min
Publish = 10 min
```

Sequential critical path:

```text
165 min
```

Parallelizing independent work may reduce the path.

### SLO examples

```text
99% of daily Jobs complete before 06:30
99.5% of runs do not require manual repair
Critical task failure alerts delivered within 5 minutes
```

Targets must be business-specific.

---

## 52. Hands-on Labs

All labs are self-contained in this module.

## Lab 1 — First Job

Build conceptually:

```text
Job
 ├── ingest
 ├── transform
 └── publish
```

Tasks:

1. define task responsibilities
2. add dependencies
3. choose compute
4. add a schedule
5. add failure notification

Checkpoint:

> Explain why each dependency exists.

---

## Lab 2 — Multiple Task Types

Build a workflow containing:

- Python task
- SQL task
- Pipeline task
- dbt task

Document why each task type exists.

---

## Lab 3 — DAG Design

Build:

```text
customers ──┐
            ├──→ silver ──→ gold
orders ─────┘
```

Measure the critical path.

Then redesign for maximum safe parallelism.

---

## Lab 4 — Scheduled Job

Create a daily workflow.

Document:

- timezone
- source readiness
- run date
- expected runtime
- timeout
- alerting
- downstream SLA

---

## Lab 5 — File Arrival

Simulate:

```text
File arrives
   ↓
Job triggers
   ↓
Ingestion
```

Test:

- duplicate file
- late file
- burst of files
- missing expected file

---

## Lab 6 — Table Update Trigger

Design a downstream workflow that reacts to an upstream table update.

Document:

- source table
- trigger behavior
- expected frequency
- overlap controls
- idempotency

> Verify current workspace support before implementing exact trigger configuration.

---

## Lab 7 — Parameters

Use:

```text
environment
run_date
source
```

Pass them through multiple tasks.

Test:

```text
DEV
2026-10-06
orders
```

and:

```text
PROD
2026-10-06
orders
```

---

## Lab 8 — Task Values

Task A produces:

```text
records_processed = 125000
```

Task B uses that value:

```text
if records_processed > threshold:
    continue
else:
    alert
```

Verify that the branch is deterministic.

---

## Lab 9 — If/Else

Build:

```text
quality_check
      |
      +── PASS → publish
      |
      +── FAIL → alert
```

Test both branches.

---

## Lab 10 — For-Each

Process:

```text
customers
orders
products
payments
```

using one parameterized processing pattern.

Measure:

- parallelism
- duration
- resource usage
- failure isolation

---

## Lab 11 — Repair Run

Force:

```text
Task C = failure
```

Graph:

```text
A ✓
↓
B ✓
↓
C ✗
↓
D blocked
```

Repair the failed path.

Verify that successful work is not unnecessarily repeated.

---

## Lab 12 — Backfill

Process:

```text
2026-09-01
2026-09-02
2026-09-03
```

using a reusable `run_date` parameter.

Verify:

- no duplicates
- correct partitions
- correct totals
- correct downstream results

---

## Lab 13 — Concurrency

Create overlapping run requests.

Observe:

- active runs
- queued runs
- waiting time
- resource contention

Then change concurrency settings and compare behavior.

---

## Lab 14 — Service Principal

Design a production Job executed by a service principal.

Document:

- identity
- catalog grants
- schema grants
- secret access
- audit trail
- developer vs runtime permissions

---

## Lab 15 — Airflow Comparison

Design:

```text
Option A
Lakeflow Jobs

Option B
Airflow → Databricks
```

Compare:

- orchestration scope
- operations
- identity
- monitoring
- cost
- ownership
- portability

---

## 53. Break/Fix Incidents

For each incident use:

```text
Incident
Symptoms
Initial hypothesis
Evidence
Diagnosis
Root cause
Fix
Verification
Prevention
Runbook entry
```

## Incident 1 — Transient Network Failure

**Symptoms:** Task fails once with a temporary network error.

**Diagnosis:** Evidence shows a transient dependency outage.

**Fix:** Retry using controlled backoff.

**Prevention:** Appropriate retry policy and monitoring.

---

## Incident 2 — Permanent Failure Retried Repeatedly

**Symptoms:** Task fails five times with the same schema error.

**Root cause:** Retries were configured for a deterministic code/schema failure.

**Fix:** Stop retry storm; correct code/schema.

**Prevention:** Classify failures before adding retries.

---

## Incident 3 — Overlapping Runs

**Symptoms:** Two runs write the same date.

**Root cause:** Schedule interval is shorter than runtime and concurrency was not constrained.

**Fix:** Control concurrency and redesign schedule.

**Prevention:** Runtime/SLA analysis.

---

## Incident 4 — Task Exceeds Duration

**Symptoms:** Normal runtime is 20 minutes; current run is 3 hours.

**Evidence:** Input volume unchanged; task is waiting on a downstream dependency.

**Fix:** Diagnose dependency/queue issue.

**Prevention:** Duration alerts.

---

## Incident 5 — File Trigger Fires Unexpectedly

**Symptoms:** Job runs many times during one file delivery.

**Root cause:** File-arrival behavior does not match assumed batching semantics.

**Fix:** Make processing idempotent and adjust trigger strategy.

**Prevention:** Test burst arrivals.

---

## Incident 6 — Wrong Parameter

**Symptoms:** Production Job processes development catalog.

**Root cause:** Hardcoded/default parameter override.

**Fix:** Correct environment parameterization and permissions.

**Prevention:** Deployment validation.

---

## Incident 7 — Quality Failure Does Not Block Publish

**Symptoms:** Bad data reaches Gold.

**Root cause:** Conditional branch was wired incorrectly.

**Fix:** Correct dependency/control-flow semantics.

**Prevention:** Test both success and failure branches.

---

## Incident 8 — Excessive For-Each Parallelism

**Symptoms:** 200 partner tasks overwhelm source system.

**Root cause:** Fan-out ignored source/API capacity.

**Fix:** Bound concurrency.

**Prevention:** Capacity-aware fan-out design.

---

## Incident 9 — Repair Run Creates Duplicates

**Symptoms:** Records double after repair.

**Root cause:** Failed task was non-idempotent.

**Fix:** Deduplicate/reconcile and redesign write semantics.

**Prevention:** Idempotency testing.

---

## Incident 10 — Backfill Corrupts Downstream Results

**Symptoms:** Historical metrics change twice.

**Root cause:** Backfill was not isolated from downstream incremental processing.

**Fix:** Reconcile affected interval and downstream products.

**Prevention:** Backfill runbook and dependency analysis.

---

## Incident 11 — Service Principal Permission Failure

**Symptoms:** Job works manually but fails in production.

**Root cause:** Developer had access that runtime identity lacked.

**Fix:** Grant only required Unity Catalog privileges.

**Prevention:** Test using the actual production identity.

---

## Incident 12 — Manual Success, Production Failure

**Symptoms:** Run Now succeeds; scheduled run fails.

**Root causes:** Different identity, parameters, compute, environment, or source availability.

**Fix:** Compare runtime context.

**Prevention:** Production-like testing.

---

## Incident 13 — Cost Spike

**Symptoms:** Daily orchestration spend doubles.

**Evidence:** Retry count and fan-out increased.

**Fix:** Remove unnecessary retries/fan-out.

**Prevention:** Cost monitoring.

---

## Incident 14 — Airflow/Lakeflow Duplicate Trigger

**Symptoms:** Same workflow executes twice.

**Root cause:** Airflow and Lakeflow both own scheduling.

**Fix:** Establish one source of orchestration truth.

**Prevention:** Architecture ownership rule.

---

## Incident 15 — Long-Running Task Blocks Schedule

**Symptoms:** Queue grows continuously.

**Root cause:** Task duration exceeds trigger interval.

**Fix:** Reduce work, increase capacity, or change schedule/concurrency policy.

**Prevention:** SLA and critical-path monitoring.

---

## 54. Production Runbooks

## Runbook 1 — Job Failed

```text
SYMPTOM
↓
Identify failed run
↓
Identify failed task
↓
Inspect logs
↓
Classify transient/permanent
↓
Retry or repair
↓
Verify
↓
Prevent recurrence
```

---

## Runbook 2 — Task Failed

Check:

- task logs
- parameters
- identity
- source
- compute
- dependencies
- code version

Do not rerun until the failure class is understood.

---

## Runbook 3 — Task Repeatedly Retries

1. Stop treating retries as the solution.
2. Inspect the repeated error.
3. Determine transient vs permanent.
4. Stop retry storm if necessary.
5. Fix root cause.
6. Re-run safely.

---

## Runbook 4 — Job Is Stuck

Check:

- active task
- dependency state
- queue
- compute
- external dependency
- streaming state
- timeout

---

## Runbook 5 — Job Running Too Long

Compare:

```text
Current duration
vs
Historical baseline
```

Then inspect:

- input volume
- compute
- dependency waits
- retries
- skew
- external systems

---

## Runbook 6 — Runs Are Overlapping

Check:

- schedule
- concurrency
- runtime
- retries
- queueing
- idempotency

Then choose:

```text
reduce frequency
or
increase capacity
or
constrain concurrency
```

---

## Runbook 7 — Runs Are Queued

Check:

- active run count
- concurrency limit
- compute availability
- source capacity
- SLA impact

---

## Runbook 8 — File Trigger Misbehaving

Check:

- monitored location
- arrival pattern
- duplicate events
- batching
- file completeness
- idempotency

---

## Runbook 9 — Wrong Parameter

Trace:

```text
Job parameter
↓
Task parameter
↓
Dynamic value
↓
Code
```

Compare expected vs actual runtime values.

---

## Runbook 10 — Task-Value Failure

Check:

- upstream task success
- value existence
- value type/format
- reference syntax
- downstream task support

---

## Runbook 11 — Repair-Run Issue

Check:

- failed task
- downstream dependencies
- idempotency
- state already written
- duplicate effects

---

## Runbook 12 — Backfill Issue

Check:

- historical interval
- source completeness
- duplicate writes
- downstream impact
- concurrency
- validation

---

## Runbook 13 — Service Principal Permission Failure

Check:

```text
Identity
↓
Catalog
↓
Schema
↓
Object
↓
Required privilege
```

Do not solve by granting broad admin permissions.

---

## Runbook 14 — Cost Spike

Check:

- run count
- retry count
- runtime
- compute
- fan-out
- backfills
- overlap
- continuous execution

---

## Runbook 15 — Airflow/Lakeflow Duplicate Orchestration

Determine:

```text
Who owns the schedule?
Who owns dependencies?
Who owns retry?
Who owns alerts?
```

Then remove duplicate orchestration.

---

## 55. Observability Framework

### Availability

- Job success/failure
- task success/failure

### Reliability

- retry rate
- repair frequency
- failed-run rate

### Performance

- task duration
- critical-path duration
- queue time

### Freshness

- source arrival time
- Job start time
- output availability

### Cost

- runtime
- compute usage
- retries
- backfills

### Operational health

- queued runs
- stuck runs
- overlapping runs
- disabled jobs
- alert delivery

### Dashboard concept

```text
JOB HEALTH
├── Success rate
├── Failure rate
├── Retry rate
├── Repair rate
├── P95 duration
├── Queue time
├── SLA attainment
└── Cost/run
```

---

## 56. Decision Matrices

## Notebook vs Python Script vs Python Wheel

| Dimension | Notebook | Python Script | Python Wheel |
|---|---|---|---|
| Rapid development | Strong | Strong | Moderate |
| Reuse | Moderate | Strong | Strongest |
| Unit testing | Moderate | Strong | Strongest |
| CI/CD | Moderate | Strong | Strongest |
| Visualization | Strong | Weak | Weak |
| Production maturity | Moderate | Strong | Strongest |
| Packaging | Low | Moderate | Strong |
| Recommended for core shared logic | Sometimes | Yes | Yes |

---

## Jobs Compute vs Shared vs Serverless

| Dimension | Jobs Compute | Shared | Serverless |
|---|---|---|---|
| Isolation | Strong | Lower | Managed |
| Startup | Moderate | Potentially lower | Managed |
| Infrastructure control | Strong | Strong | Lower |
| Operations | Moderate | Moderate | Lowest |
| Feature compatibility | Strong | Strong | Verify |
| Cost model | Usage-based | Usage-based | Usage-based |
| Best fit | Production tasks | Related tasks | Supported managed workloads |

---

## Trigger Decision

| Requirement | Scheduled | File Arrival | Table Update | Continuous |
|---|---:|---:|---:|---:|
| Daily batch | Strong | Weak | Weak | Weak |
| Landing files | Weak | Strong | Weak | Weak |
| Downstream table reaction | Weak | Weak | Strong | Weak |
| Low latency | Weak | Strong | Strong | Strong |
| Predictability | Strong | Moderate | Moderate | Lower |
| Operational simplicity | Strong | Strong | Moderate | Lower |

---

## Retry vs Repair vs Full Rerun

| Situation | Retry | Repair | Full rerun |
|---|---:|---:|---:|
| Transient failure | Strong | Possible | Weak |
| Failed one task | Weak | Strong | Weak |
| Downstream tasks blocked | Weak | Strong | Possible |
| Corrupted state | Weak | Depends | Strong candidate |
| Non-idempotent task | Dangerous | Dangerous | Dangerous |
| Historical correction | Weak | Possible | Backfill preferred |

---

## Lakeflow Jobs vs Airflow

| Question | Lakeflow Jobs | Airflow |
|---|---|---|
| Mostly Databricks? | Strong | Possible |
| Many external systems? | Moderate | Strong |
| Kubernetes workflows? | Moderate | Strong |
| Databricks-native governance? | Strong | Requires integration |
| Organization-wide orchestrator? | Depends | Strong |
| Low platform overhead? | Strong | Lower |
| Portability? | Lower | Strong |

---

## One Job vs Multiple Jobs

| Dimension | One Job | Multiple Jobs |
|---|---|---|
| Simplicity | Strong | Lower |
| Domain isolation | Lower | Strong |
| Reuse | Moderate | Strong |
| Failure isolation | Lower | Strong |
| Monitoring | Simpler | More distributed |
| Ownership | Central | Domain-specific |
| Best fit | Cohesive workflow | Independent domains |

---

## Sequential vs Parallel

| Dimension | Sequential | Parallel |
|---|---|---|
| Simplicity | Strong | Moderate |
| Runtime | Longer | Shorter if independent |
| Resource use | Lower | Higher |
| Dependency safety | Easier | Requires analysis |
| SLA optimization | Weak | Strong |
| Risk of contention | Lower | Higher |

---

## 57. Architecture Decision Records

## ADR 1 — Lakeflow Jobs vs Airflow

**Context:** Platform contains mostly Databricks workloads but also some external services.

**Options:**
1. Lakeflow Jobs only
2. Airflow only
3. Airflow for cross-platform + Databricks Jobs for local workflows

**Decision:** Evaluate based on workflow boundaries and organizational ownership; avoid forcing one orchestrator onto all workloads.

**Trade-offs:** Multiple systems increase operational complexity.

**Security:** Two identity models may be required.

**Cost:** Platform operations must be included.

**Reconsideration trigger:** External workload share grows materially.

---

## ADR 2 — Notebook vs Python Wheel

**Context:** A transformation is now reused by six workflows.

**Decision:** Move shared business logic into a tested package/wheel.

**Reason:** Reuse, testing, versioning, CI/CD.

**Trade-off:** Packaging pipeline becomes required.

---

## ADR 3 — Serverless vs Jobs Compute

**Context:** Standard supported workload has variable demand.

**Decision:** Prefer serverless where supported and economically appropriate; use jobs compute for workloads requiring capabilities/control not available in serverless.

**Reconsideration:** Cost or feature requirements change.

---

## ADR 4 — Single Monolithic Job vs Domain Jobs

**Decision:** Keep strongly coupled tasks together; split independently owned workflows.

**Risk:** Too many Jobs can create orchestration fragmentation.

---

## ADR 5 — Sequential vs Parallel

**Decision:** Parallelize only independent tasks whose source and compute capacity can tolerate concurrent execution.

**Trade-off:** Lower critical-path duration versus higher resource demand.

---

## ADR 6 — Retry vs Repair

**Decision:** Retry transient failures; use repair for failed workflow paths; use backfill/full reconstruction for historical correctness issues.

**Reason:** Different failure classes require different recovery operations.

---

## ADR 7 — Service Principal Runtime Identity

**Decision:** Production Jobs execute under a stable machine identity with least privilege.

**Reason:** Human identities are not reliable production runtime identities.

---

## 58. Common Mistakes

## 1. Jobs owned by and running as individual users

**Why:** Easy during development.

**Danger:** Employee access changes.

**Detection:** Job fails after employee role change.

**Prevention:** Service principal runtime identity.

---

## 2. One monolithic notebook task

**Why:** Fast initial implementation.

**Danger:** Poor testing and reuse.

**Detection:** Hundreds/thousands of lines and unrelated responsibilities.

**Prevention:** Modular tasks/packages.

---

## 3. All-purpose clusters for production jobs

**Why:** Convenient.

**Danger:** Cost and isolation issues.

**Detection:** Job shares interactive compute.

**Prevention:** Use appropriate jobs/serverless compute.

---

## 4. No failure alerts

**Why:** Engineers assume monitoring UI is enough.

**Danger:** Consumers discover failures first.

**Prevention:** Critical failure alerts.

---

## 5. No long-duration alerts

**Why:** Only success/failure is monitored.

**Danger:** A Job can remain technically healthy while missing SLA.

**Prevention:** Duration SLOs.

---

## 6. Excessive task fragmentation

**Why:** "More tasks means better orchestration."

**Danger:** More scheduling overhead and complexity.

**Prevention:** One task per meaningful unit of work.

---

## 7. Hidden dependencies

**Why:** Code reads upstream table implicitly.

**Danger:** Scheduler cannot enforce the relationship.

**Prevention:** Explicit DAG dependency.

---

## 8. Non-idempotent tasks

**Why:** Initial run works.

**Danger:** Retry/repair duplicates data.

**Prevention:** Deterministic writes.

---

## 9. Unlimited retries

**Why:** "Retry fixes transient errors."

**Danger:** Permanent failure becomes retry storm.

**Prevention:** Classify failure types.

---

## 10. No timeout

**Why:** Engineer does not know normal runtime.

**Danger:** Runaway resource usage.

**Prevention:** Baseline runtime and set meaningful timeout.

---

## 11. Uncontrolled concurrency

**Why:** Independent runs seem harmless.

**Danger:** Duplicate writes and resource contention.

**Prevention:** Concurrency policy.

---

## 12. Hardcoded production paths

**Why:** Fast configuration.

**Danger:** Environment contamination.

**Prevention:** Parameters and deployment controls.

---

## 13. No backfill strategy

**Why:** Team only designs the happy path.

**Danger:** Historical corrections become emergencies.

**Prevention:** Design backfills before production.

---

## 14. No repair strategy

**Why:** Teams always rerun everything.

**Danger:** Waste and duplicate effects.

**Prevention:** Idempotency + repair procedures.

---

## 15. Duplicate Airflow/Lakeflow scheduling

**Why:** Migration or unclear ownership.

**Danger:** Double execution.

**Prevention:** One scheduling source of truth.

---

## 16. Excessive fan-out

**Why:** For-each makes parallelism easy.

**Danger:** Source/compute overload.

**Prevention:** Capacity-aware fan-out.

---

## 17. No cost monitoring

**Why:** Workflow correctness dominates attention.

**Danger:** Spend grows unnoticed.

**Prevention:** Cost/run and duration metrics.

---

## 59. Mental Models

## Mental Model 1

```text
Lakeflow Declarative Pipeline
=
WHAT should be produced

Lakeflow Jobs
=
WHEN / HOW / IN WHAT ORDER
```

---

## Mental Model 2

```text
JOB
=
Container for workflow execution
```

---

## Mental Model 3

```text
TASK
=
One unit of work
```

---

## Mental Model 4

```text
DEPENDENCY
=
What must happen before this can run
```

---

## Mental Model 5

```text
TRIGGER
=
What causes a Job to start
```

---

## Mental Model 6

```text
PARAMETER
=
Information supplied to a run
```

---

## Mental Model 7

```text
RETRY
=
Try the same task again

REPAIR
=
Continue from the failed portion

BACKFILL
=
Run historical data intentionally
```

---

## Mental Model 8

```text
Reliable orchestration
=
DAG
+
Idempotency
+
Retries
+
Timeouts
+
Monitoring
+
Recovery
```

---

## 60. Production Engineering Principles

### Principle 1

> Orchestration is not business logic.

### Principle 2

> Tasks should be independently testable.

### Principle 3

> Retries require idempotency.

### Principle 4

> Every production workflow needs observability.

### Principle 5

> Every production workflow needs a recovery strategy.

### Principle 6

> Personal user identities should not be the production execution identity.

### Principle 7

> Parallelism should be intentional.

### Principle 8

> More tasks do not automatically mean better orchestration.

### Principle 9

> Backfills must be designed before they are needed.

### Principle 10

> Cost is an architectural concern, not merely a billing concern.

---

## 61. Interview Preparation

## Basic — 15

### B1 — What is orchestration?

**Expected thinking:** Coordination rather than transformation.

**Strong answer:** Orchestration determines what runs, when, in what order, under what conditions, and how failures are handled.

**Why:** It separates workflow control from data-processing logic.

**Follow-up:** What does a scheduler alone not solve?

---

### B2 — What is a Job?

**Strong answer:** A workflow definition containing one or more executable tasks and their operational configuration.

**Follow-up:** How is a Run different?

---

### B3 — What is a Task?

**Strong answer:** One executable unit of work inside a Job.

**Follow-up:** Give three task types.

---

### B4 — What is a DAG?

**Strong answer:** A directed acyclic graph representing tasks and their dependencies.

**Follow-up:** What is a critical path?

---

### B5 — Why use dependencies?

**Strong answer:** To guarantee required ordering and make workflow relationships explicit.

**Follow-up:** What is a hidden dependency?

---

### B6 — What is a retry?

**Strong answer:** Re-executing a failed task, typically for transient failures.

**Follow-up:** Why does idempotency matter?

---

### B7 — What is a timeout?

**Strong answer:** A maximum permitted execution duration used to detect runaway or unexpectedly slow work.

**Follow-up:** What happens if it is too short?

---

### B8 — What is a trigger?

**Strong answer:** A condition or schedule that starts a Job.

**Follow-up:** Name four roadmap trigger types.

---

### B9 — What is a parameter?

**Strong answer:** Runtime configuration supplied to a Job or Task.

**Follow-up:** Why are dates useful parameters?

---

### B10 — What is a repair run?

**Strong answer:** A recovery operation that reruns the failed/canceled portion of a workflow where supported.

**Follow-up:** What can make repair unsafe?

---

### B11 — What is a backfill?

**Strong answer:** Intentional historical processing for a missing or corrected interval.

**Follow-up:** How do you prevent duplicates?

---

### B12 — Why use a service principal?

**Strong answer:** To provide a stable production execution identity independent of individual employees.

**Follow-up:** What principle should govern its permissions?

---

### B13 — What is concurrency?

**Strong answer:** The number of workflow runs allowed to execute simultaneously.

**Follow-up:** Why limit it?

---

### B14 — Why monitor duration?

**Strong answer:** A successful run can still violate an SLA.

**Follow-up:** What metric would you use?

---

### B15 — When might Airflow be preferred?

**Strong answer:** When orchestration spans many heterogeneous external systems and a platform-wide orchestrator is justified.

**Follow-up:** Can Airflow still run Databricks work?

---

## Intermediate — 15

### I1 — Notebook vs Python wheel?

**Strong answer:** Use notebooks for rapid/interactive workflows; prefer packages/wheels for reusable, tested production logic.

**Follow-up:** What migration signal indicates a notebook should become a package?

---

### I2 — Why is a hidden dependency dangerous?

**Strong answer:** The scheduler cannot enforce it, so downstream work may run before required upstream state exists.

**Follow-up:** How do you detect one?

---

### I3 — Why can retries create duplicates?

**Strong answer:** A non-idempotent write repeats its side effect.

**Follow-up:** Give a safe write pattern.

---

### I4 — Why limit concurrency?

**Strong answer:** To prevent overlapping writes, race conditions, source overload, and uncontrolled cost.

**Follow-up:** What if the SLA requires more throughput?

---

### I5 — When should you use repair instead of full rerun?

**Strong answer:** When a localized failure can be safely rerun without reconstructing successful work.

**Follow-up:** What if state is corrupted?

---

### I6 — Why are backfills different from retries?

**Strong answer:** A retry repeats a failed execution; a backfill intentionally processes historical business data.

**Follow-up:** What additional validation does a backfill need?

---

### I7 — Why parameterize environment?

**Strong answer:** To reuse the workflow across dev/test/prod without hardcoded destinations.

**Follow-up:** What permission boundary should exist?

---

### I8 — What is task-value passing useful for?

**Strong answer:** Passing runtime metadata from one task to downstream control flow.

**Follow-up:** Give a quality-gate example.

---

### I9 — Why use for-each?

**Strong answer:** To apply the same processing pattern to multiple parameterized inputs.

**Follow-up:** What can go wrong with excessive fan-out?

---

### I10 — What is a run-if dependency?

**Strong answer:** A dependency that controls execution based on upstream task state/conditions.

**Follow-up:** Give a cleanup example.

---

### I11 — What makes a Job production-ready?

**Strong answer:** Explicit dependencies, idempotent tasks, appropriate compute, parameters, retries, timeouts, observability, recovery, identity, security, and cost controls.

**Follow-up:** What is usually forgotten?

---

### I12 — How would you diagnose a stuck Job?

**Strong answer:** Identify active task, dependency state, queue, compute, external dependency, and timeout evidence.

**Follow-up:** Why not immediately cancel it?

---

### I13 — Why can a green Job still violate SLA?

**Strong answer:** Success status says execution completed, not that it completed within the business freshness requirement.

**Follow-up:** What should monitor SLA?

---

### I14 — Why can serverless be cheaper operationally but not necessarily cheaper per unit?

**Strong answer:** It reduces infrastructure management but billing still depends on workload consumption and execution characteristics.

**Follow-up:** What should you measure?

---

### I15 — Can Lakeflow Jobs and Airflow coexist?

**Strong answer:** Yes, but ownership boundaries must be explicit to prevent duplicate orchestration.

**Follow-up:** Give an architecture.

---

## Advanced — 15

### A1 — A Job runs every 30 minutes but normally takes 45 minutes. What do you do?

**Strong answer:** Quantify overlap, determine whether processing is idempotent, inspect SLA, constrain concurrency or redesign runtime/schedule, and validate source capacity.

**Why:** Scheduling and runtime are inconsistent.

**Follow-up:** What if business SLA requires 30-minute freshness?

---

### A2 — Task C fails after A and B succeed. What is the safest recovery?

**Strong answer:** Classify C failure, fix root cause, then repair the failed path if the task is idempotent.

**Follow-up:** What if C partially wrote data?

---

### A3 — Four partners need identical processing. Four tasks or for-each?

**Strong answer:** Use for-each when logic is genuinely identical and parameterizable; separate tasks when partner behavior or failure isolation differs materially.

**Follow-up:** How do you cap parallelism?

---

### A4 — A repair run duplicates records. What does that tell you?

**Strong answer:** The failed path is not safely idempotent or its state assumptions are wrong.

**Follow-up:** How do you repair the already-corrupted output?

---

### A5 — How would you design a backfill for three months?

**Strong answer:** Parameterize date interval, validate source, control concurrency, ensure idempotency, isolate downstream effects, reconcile results, and monitor cost.

**Follow-up:** Why not run all dates simultaneously?

---

### A6 — How do you distinguish transient from permanent failures?

**Strong answer:** Use error classification, historical behavior, dependency status, and whether repeating without changing state/code can plausibly succeed.

**Follow-up:** What happens when classification is uncertain?

---

### A7 — How would you prevent development from writing to production?

**Strong answer:** Environment parameters, isolated targets, least-privilege identities, deployment validation, and permission boundaries.

**Follow-up:** What is the defense-in-depth strategy?

---

### A8 — When is a notebook task still appropriate?

**Strong answer:** When the logic is understandable, reasonably testable, not highly reused, and the notebook improves developer productivity without becoming a monolith.

**Follow-up:** What signals migration to a wheel?

---

### A9 — Why is a service principal not enough for security?

**Strong answer:** Identity establishes who runs; least-privilege authorization determines what it can do.

**Follow-up:** How do you govern data access?

---

### A10 — How does DAG design affect cost?

**Strong answer:** Excessive parallelism can increase concurrent compute, while unnecessary serialization can increase runtime and cost.

**Follow-up:** How do you find the balance?

---

### A11 — How do you avoid duplicate orchestration with Airflow?

**Strong answer:** Assign one system ownership of schedule/dependency execution for each workflow boundary.

**Follow-up:** What if Airflow must trigger Databricks?

---

### A12 — What makes a Job observable?

**Strong answer:** Run/task status, duration, retries, queue time, freshness, logs, alerts, and cost metrics.

**Follow-up:** Which are SLOs?

---

### A13 — Why is queueing sometimes better than concurrency?

**Strong answer:** Queueing protects shared resources and correctness when overlapping runs are unsafe.

**Follow-up:** What is the cost?

---

### A14 — How do task values change orchestration design?

**Strong answer:** They allow runtime outputs to influence downstream control flow without hardcoding decisions.

**Follow-up:** Give a data-quality example.

---

### A15 — What is the strongest argument for declarative pipeline + Jobs separation?

**Strong answer:** It cleanly separates data-product semantics from workflow-control semantics, improving maintainability and ownership.

**Follow-up:** When should logic remain inside the pipeline?

---

## Production/System Design — 10

### P1 — Design a production workflow for S3, PostgreSQL, CRM CDC, and Kafka.

**Strong answer:** Use source-appropriate ingestion, declarative pipelines for data products, Lakeflow Jobs for orchestration, explicit dependencies, quality gates, service identity, controlled concurrency, monitoring, repair, and backfill strategies.

**Follow-up:** How do you handle late data?

---

### P2 — Design a 07:00 revenue SLA.

**Strong answer:** Build the critical path, parallelize independent ingestion, budget retries, set timeouts, establish quality gates, monitor freshness, and reserve recovery capacity.

**Follow-up:** What happens if one upstream source is late?

---

### P3 — When should the platform use Airflow?

**Strong answer:** When cross-platform heterogeneous orchestration is substantial enough to justify centralized orchestration and operational ownership.

**Follow-up:** What remains inside Databricks?

---

### P4 — How would you make repair runs safe?

**Strong answer:** Idempotent writes, deterministic keys, clear dependency graph, state inspection, and post-repair reconciliation.

**Follow-up:** What if an external API was called?

---

### P5 — Design a multi-environment Job platform.

**Strong answer:** Parameterized configuration, isolated targets, CI/CD, service principals, environment-specific permissions, and deployment validation.

**Follow-up:** How do you prevent accidental prod execution?

---

### P6 — A Job costs 4× more this month. Diagnose it.

**Strong answer:** Compare run count, runtime, compute, retries, fan-out, backfills, overlap, and continuous execution against baseline.

**Follow-up:** What evidence proves the fix?

---

### P7 — Design a reliable partner-ingestion workflow.

**Strong answer:** For-each with bounded concurrency, source-specific parameters, idempotent ingestion, quality gate, per-source failure isolation, retries for transient failures, and operational alerts.

**Follow-up:** How do you handle one bad partner?

---

### P8 — How would you recover a corrupted historical interval?

**Strong answer:** Stop unsafe downstream publication if necessary, identify authoritative source, define interval, choose backfill/reconstruction, control concurrency, reconcile, and validate consumers.

**Follow-up:** What is the rollback strategy?

---

### P9 — Design Airflow → Databricks orchestration.

**Strong answer:** Airflow owns cross-platform scheduling; Databricks executes data processing; identity, retries, monitoring, and ownership boundaries are explicit.

**Follow-up:** How do you avoid double triggers?

---

### P10 — What does production-grade orchestration mean?

**Strong answer:**

```text
Explicit DAG
+
Correct task abstraction
+
Idempotency
+
Controlled retries
+
Timeouts
+
Parameterization
+
Observability
+
Recovery
+
Stable identity
+
Least privilege
+
Concurrency control
+
Cost management
```

**Follow-up:** Which of these would you refuse to omit?

---

## 62. Practice Questions

## Basic — 10

### Q1
What is orchestration?

**Answer:** Coordinating tasks, timing, dependencies, conditions, failures, and recovery.

### Q2
What is a Job?

**Answer:** A workflow definition.

### Q3
What is a Run?

**Answer:** One execution of a Job.

### Q4
What is a Task?

**Answer:** One unit of work.

### Q5
What is a dependency?

**Answer:** A relationship that controls task ordering.

### Q6
Why use parameters?

**Answer:** To make workflows reusable and configurable.

### Q7
Why use retries?

**Answer:** To recover from transient failures.

### Q8
Why use timeouts?

**Answer:** To detect runaway/abnormally slow work.

### Q9
What is a repair run?

**Answer:** Rerunning the failed portion of a workflow where supported.

### Q10
What is a backfill?

**Answer:** Intentional historical processing.

---

## Intermediate — 10

### Q11
A Job runs every hour but takes two hours. What problem exists?

**Answer:** Potential overlapping runs, queue growth, contention, or missed SLA.

### Q12
Why can a retry duplicate data?

**Answer:** The task is non-idempotent.

### Q13
When is for-each useful?

**Answer:** Repeated parameterized processing with common logic.

### Q14
What should a service principal have?

**Answer:** Only the permissions required by its workflow.

### Q15
Why use task values?

**Answer:** To pass runtime outputs to downstream tasks.

### Q16
Why use repair instead of full rerun?

**Answer:** To avoid repeating successful work.

### Q17
What is a critical path?

**Answer:** The longest dependency path controlling minimum workflow duration.

### Q18
When might Airflow be preferable?

**Answer:** Broad heterogeneous platform orchestration.

### Q19
Why monitor duration?

**Answer:** SLA violations can occur even when a Job succeeds.

### Q20
What is queueing?

**Answer:** Holding runs until execution capacity/concurrency permits them.

---

## Advanced — 10

### Q21
A repair duplicates rows. What should you inspect?

**Answer:** Idempotency, write semantics, partial side effects, and existing state.

### Q22
How would you backfill a month safely?

**Answer:** Parameterize dates, verify source, control concurrency, validate each interval, and reconcile downstream outputs.

### Q23
Why can excessive for-each fan-out be dangerous?

**Answer:** It can overwhelm sources and compute.

### Q24
Why can Airflow + Lakeflow become problematic?

**Answer:** Duplicate scheduling/ownership and multiple monitoring/identity layers.

### Q25
How do you choose task type?

**Answer:** Based on workload, reuse, testing, packaging, and operational maturity.

### Q26
What makes a retry safe?

**Answer:** The task is idempotent or otherwise compensates for repeated execution.

### Q27
What makes a timeout useful?

**Answer:** It is based on historical runtime and SLA expectations.

### Q28
Why should production Jobs use service principals?

**Answer:** Stable identity and controlled permissions.

### Q29
What is the difference between a Job and a Pipeline?

**Answer:** A Pipeline defines/maintains data products; a Job orchestrates execution.

### Q30
How does DAG parallelism affect cost?

**Answer:** It can reduce elapsed time but increase concurrent compute.

---

## Expert / Production — 10

### Q31
Design a safe daily revenue workflow.

**Answer:** Explicit ingestion dependencies, parallel independent sources, quality gate, idempotent gold publishing, SLA monitoring, alerts, repair/backfill strategy, and stable identity.

### Q32
A source arrives late every Monday. What do you do?

**Answer:** Model the source availability pattern, adjust trigger/SLA expectations, monitor lateness, and avoid false incident alerts.

### Q33
A Job succeeds but misses the business SLA. Is it healthy?

**Answer:** No. Operational success and SLA compliance are separate dimensions.

### Q34
Why is full rerun not always the best recovery?

**Answer:** It wastes successful work and can create duplicates or additional cost.

### Q35
How do you decide concurrency?

**Answer:** Based on workload isolation, source capacity, compute capacity, idempotency, and SLA.

### Q36
How do you design service-principal permissions?

**Answer:** Grant only required catalog/schema/object access and secret access.

### Q37
What should an orchestration runbook contain?

**Answer:** Symptom, evidence, diagnosis, root cause, fix, verification, and prevention.

### Q38
What should be measured for orchestration cost?

**Answer:** Runs, runtime, compute, retries, fan-out, backfills, and overlap.

### Q39
How do you choose Lakeflow Jobs vs Airflow?

**Answer:** Evaluate workload heterogeneity, platform boundaries, ecosystem integration, ownership, cost, and operational complexity.

### Q40
What is the central production principle?

**Answer:**

> **Orchestration must make execution predictable, observable, recoverable, and safe to repeat.**

---

## 63. Production Capstone

## Scenario

A company has:

```text
S3 clickstream
PostgreSQL orders
CRM customer CDC
Kafka events
```

Lakehouse:

```text
Bronze
Silver
Gold
```

Requirements:

- file ingestion
- database CDC
- streaming
- quality checks
- SCD2
- gold aggregations
- alerts
- daily schedules
- file-arrival trigger
- conditional branching
- for-each processing
- backfills
- repair runs
- concurrency control
- service principal
- monitoring
- cost control

### Target architecture

```text
                 ┌──→ Orders Ingestion ──────┐
                 │                            │
File Arrival ────┼──→ Clickstream Ingestion ──┤
                 │                            ↓
                 └──→ Customer CDC ───────→ Quality
                                              ↓
                                         If / Else
                                        ↙          ↘
                                  PASS               FAIL
                                   ↓                   ↓
                                Gold              Alert
                                   ↓
                              Publish / BI
```

Add:

```text
For Each
```

for multiple partner sources.

Add:

```text
Repair
Backfill
Concurrency
Service Principal
```

### Required documentation

1. Job architecture
2. Task graph
3. Dependencies
4. Compute choice
5. Trigger strategy
6. Parameters
7. Task values
8. Control flow
9. Retry strategy
10. Timeout strategy
11. Alert strategy
12. Repair strategy
13. Backfill strategy
14. Concurrency strategy
15. Security
16. Cost
17. Airflow comparison
18. ADRs
19. Failure scenarios
20. Runbooks

### Acceptance criteria

```text
[ ] All dependencies are explicit
[ ] Task types are justified
[ ] Compute is justified
[ ] Trigger strategy is documented
[ ] Parameters are reusable
[ ] Task values are used where appropriate
[ ] Conditional logic is tested
[ ] For-each concurrency is controlled
[ ] Tasks are idempotent
[ ] Retries are intentional
[ ] Timeouts are justified
[ ] Repair strategy exists
[ ] Backfill strategy exists
[ ] Service principal is used
[ ] Least privilege is documented
[ ] Monitoring exists
[ ] Cost is measured
[ ] Airflow boundary is explicit
[ ] Runbooks exist
[ ] ADRs exist
```

---

## 64. Final Knowledge Checkpoint

```text
[ ] I understand why orchestration exists.
[ ] I can explain Lakeflow Jobs.
[ ] I understand Jobs vs Runs vs Tasks.
[ ] I understand dependencies.
[ ] I understand DAGs.
[ ] I understand notebook tasks.
[ ] I understand Python script tasks.
[ ] I understand Python wheel tasks.
[ ] I understand SQL tasks.
[ ] I understand pipeline tasks.
[ ] I understand dbt tasks.
[ ] I understand Run Job tasks.
[ ] I understand jobs compute.
[ ] I understand shared compute.
[ ] I understand serverless.
[ ] I can choose appropriate compute.
[ ] I understand schedules.
[ ] I understand retries.
[ ] I understand timeouts.
[ ] I understand notifications.
[ ] I understand scheduled triggers.
[ ] I understand file-arrival triggers.
[ ] I understand table-update triggers.
[ ] I understand continuous execution.
[ ] I understand Job parameters.
[ ] I understand Task parameters.
[ ] I understand dynamic values.
[ ] I understand Task values.
[ ] I understand if/else.
[ ] I understand for-each.
[ ] I understand run-if dependencies.
[ ] I understand repair runs.
[ ] I understand monitoring.
[ ] I understand backfills.
[ ] I understand historical reruns.
[ ] I understand concurrency.
[ ] I understand queueing.
[ ] I understand overlapping-run risks.
[ ] I understand idempotency.
[ ] I understand service principals.
[ ] I understand production security.
[ ] I understand cost optimization.
[ ] I can compare Lakeflow Jobs with Airflow.
[ ] I can design Airflow → Databricks architecture.
[ ] I can design a production orchestration architecture.
[ ] I can troubleshoot failed Jobs.
[ ] I can write production runbooks.
```

---

## 65. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Section | Code Example? | Hands-on? | Production Depth? |
|---|---|---|---|---|---|
| Jobs | COMPLETE | 5–6 | Yes | Yes | Yes |
| Tasks | COMPLETE | 6–8 | Yes | Yes | Yes |
| Dependencies | COMPLETE | 7, 16 | Yes | Yes | Yes |
| Notebook task | COMPLETE | 9 | Yes | Yes | Yes |
| Python script task | COMPLETE | 10 | Yes | Yes | Yes |
| Python wheel task | COMPLETE | 11 | Yes | Yes | Yes |
| SQL task | COMPLETE | 12 | Yes | Yes | Yes |
| Pipeline task | COMPLETE | 13 | Yes | Yes | Yes |
| dbt task | COMPLETE | 14 | Yes | Yes | Yes |
| Run another job | COMPLETE | 15 | Yes | Yes | Yes |
| Jobs compute | COMPLETE | 17 | Yes | Yes | Yes |
| Shared job clusters | COMPLETE | 17 | Conceptual | Yes | Yes |
| Serverless | COMPLETE | 17 | Conceptual | Yes | Yes |
| Schedules | COMPLETE | 18 | Examples | Yes | Yes |
| Retries | COMPLETE | 19 | Yes | Yes | Yes |
| Timeouts | COMPLETE | 20 | Yes | Yes | Yes |
| Notifications | COMPLETE | 21 | Yes | Yes | Yes |
| Scheduled triggers | COMPLETE | 22 | Yes | Yes | Yes |
| File-arrival triggers | COMPLETE | 23 | Yes | Yes | Yes |
| Table-update triggers | COMPLETE | 24 | Conceptual | Yes | Yes |
| Continuous triggers | COMPLETE | 25 | Conceptual | Yes | Yes |
| Job parameters | COMPLETE | 27 | Yes | Yes | Yes |
| Task parameters | COMPLETE | 28 | Yes | Yes | Yes |
| Dynamic value references | COMPLETE | 29 | Illustrative | Yes | Yes |
| Run-date parameters | COMPLETE | 27, 29, 38 | Yes | Yes | Yes |
| Task values | COMPLETE | 30 | Illustrative | Yes | Yes |
| If/else | COMPLETE | 31 | Yes | Yes | Yes |
| For-each | COMPLETE | 32 | Yes | Yes | Yes |
| Run-if dependencies | COMPLETE | 33 | Conceptual | Yes | Yes |
| Repair runs | COMPLETE | 34 | Yes | Yes | Yes |
| Run history | COMPLETE | 35 | Yes | Yes | Yes |
| Task logs | COMPLETE | 35 | Yes | Yes | Yes |
| Failure alerts | COMPLETE | 21, 35 | Yes | Yes | Yes |
| Duration alerts | COMPLETE | 21, 35 | Yes | Yes | Yes |
| Backfills | COMPLETE | 37 | Yes | Yes | Yes |
| Historical reruns | COMPLETE | 38 | Yes | Yes | Yes |
| Concurrency limits | COMPLETE | 39 | Yes | Yes | Yes |
| Queueing | COMPLETE | 39 | Yes | Yes | Yes |
| Avoid overlapping runs | COMPLETE | 40 | Yes | Yes | Yes |
| Lakeflow Jobs vs Airflow | COMPLETE | 46–48 | Yes | Yes | Yes |
| Airflow → Databricks | COMPLETE | 49 | Yes | Yes | Yes |
| Service principals | COMPLETE | 42 | Yes | Yes | Yes |
| Idempotency | COMPLETE | 41 | Yes | Yes | Yes |
| Security | COMPLETE | 43 | Yes | Yes | Yes |
| Reliability | COMPLETE | 45 | Yes | Yes | Yes |
| Cost optimization | COMPLETE | 44 | Yes | Yes | Yes |
| Production architectures | COMPLETE | 50, 63 | Yes | Yes | Yes |
| Hands-on labs | COMPLETE | 52 | Yes | 15 labs | Yes |
| Break/fix incidents | COMPLETE | 53 | No | 15 incidents | Yes |
| Production runbooks | COMPLETE | 54 | No | 15 runbooks | Yes |
| Decision matrices | COMPLETE | 56 | No | Yes | Yes |
| ADRs | COMPLETE | 57 | No | Yes | Yes |
| Interview questions | COMPLETE | 61 | No | Yes | Yes |
| Practice questions | COMPLETE | 62 | No | Yes | Yes |
| Production capstone | COMPLETE | 63 | Yes | Yes | Yes |
| Final knowledge checklist | COMPLETE | 64 | No | Yes | Yes |
| Roadmap coverage audit | COMPLETE | 65 | No | Yes | Yes |

### Audit result

**COMPLETE**

Every required Topic 08 roadmap item is explicitly marked **COMPLETE**.

---

## 66. Completion Checklist

```text
[ ] Orchestration fundamentals are covered.
[ ] Lakeflow Jobs is explained.
[ ] Jobs/Runs/Tasks are differentiated.
[ ] DAGs are explained.
[ ] All roadmap task types are covered.
[ ] Compute choices are covered.
[ ] Schedules are covered.
[ ] Retries are covered.
[ ] Timeouts are covered.
[ ] Notifications are covered.
[ ] All roadmap trigger types are covered.
[ ] Job parameters are covered.
[ ] Task parameters are covered.
[ ] Dynamic values are covered.
[ ] Run-date processing is covered.
[ ] Task values are covered.
[ ] If/else is covered.
[ ] For-each is covered.
[ ] Run-if is covered.
[ ] Repair runs are covered.
[ ] Monitoring is covered.
[ ] Backfills are covered.
[ ] Historical reruns are covered.
[ ] Concurrency is covered.
[ ] Queueing is covered.
[ ] Overlap prevention is covered.
[ ] Idempotency is covered.
[ ] Service principals are covered.
[ ] Security is covered.
[ ] Cost engineering is covered.
[ ] Reliability engineering is covered.
[ ] Lakeflow Jobs vs Airflow is covered.
[ ] Airflow → Databricks is covered.
[ ] Production architectures are covered.
[ ] 15 hands-on labs are included.
[ ] 15 break/fix incidents are included.
[ ] 15 production runbooks are included.
[ ] Decision matrices are included.
[ ] ADRs are included.
[ ] 55 interview questions are included.
[ ] 40 practice questions are included.
[ ] Production capstone is included.
[ ] Final knowledge checkpoint is included.
[ ] Roadmap coverage audit is included.
[ ] Current-documentation safety is explicit.
[ ] No unsupported API/limit/pricing claim is presented as permanent fact.
```

---

## 67. Final Operating Standard

For production Lakeflow Jobs, think:

```text
DEFINE
  ↓
TASK
  ↓
DEPEND
  ↓
TRIGGER
  ↓
PARAMETERIZE
  ↓
EXECUTE
  ↓
OBSERVE
  ↓
RETRY / BRANCH / REPAIR
  ↓
RECONCILE
  ↓
BACKFILL WHEN REQUIRED
  ↓
OPTIMIZE
  ↓
DOCUMENT
```

The central principle is:

> **Orchestration must make execution predictable, observable, recoverable, and safe to repeat.**

And the most important separation in this module is:

```text
Lakeflow Declarative Pipelines
=
WHAT data should be produced

Lakeflow Jobs
=
WHEN / HOW / IN WHAT ORDER
```
